# Chapter 5: 프리로드 스캐너를 방해하지 말고 활용하라

## 핵심 질문

아무리 `fetchpriority="high"`를 걸어도 브라우저가 그 리소스의 존재를 모른다면 소용이 없다. 브라우저는 어떻게 아직 파싱하지 않은 HTML 속 리소스를 미리 찾아내는가? 그리고 우리가 매일 쓰는 어떤 코드 패턴이 그 무료 최적화를 무력화하고 있는가?

## 1. 프리로드 스캐너의 작동 원리

### 1.1 메인 파서가 멈추는 이유

브라우저의 메인 HTML 파서는 HTML을 위에서 아래로 순차적으로 읽으며 DOM을 구축한다. 하지만 두 경우에 이 과정이 멈춘다.

- **`<link rel="stylesheet">`를 만났을 때**: CSS는 렌더 블로킹 리소스다. CSS 없이 화면을 먼저 그리면 스타일이 깨진 콘텐츠가 잠깐 보였다가 다시 그려지는 FOUC(*Flash of Unstyled Content*)가 발생한다. 이를 막기 위해 브라우저는 CSS 다운로드가 끝날 때까지 렌더링을 멈춘다. 메인 파서 자체가 멈추는 것은 아니지만 CSS를 기다리는 동안 자바스크립트를 실행할 수 없어 실질적으로 파싱이 지연된다.
- **`<script>` 태그를 만났을 때**: `async`나 `defer`가 없는 스크립트는 파서 블로킹 리소스다. 자바스크립트가 DOM을 조작하거나 `document.write()`를 쓸 수 있으므로, 브라우저는 스크립트 실행 결과를 반영한 후에야 다음 HTML을 안전하게 파싱할 수 있다.

문제는 **메인 파서가 멈춰 있는 동안 HTML 나머지 부분에 어떤 리소스가 필요한지 브라우저가 모른다**는 것이다.

```
[프리로드 스캐너가 없다면]

브라우저 메인 파서                          네트워크
HTML 파싱 시작 ────────────────────▶ styles.css 요청
CSS 다운로드 대기 중 (렌더링 블로킹)
                    ◀──────────── styles.css 완료
<script src="app.js"> 발견 ────────▶ app.js 요청
스크립트 다운로드 & 실행 대기 (파싱 블로킹)
                    ◀──────────── app.js 완료
스크립트 실행 중 (파싱 중단)
body 파싱 재개
  → 이 시점에야 hero.jpg 발견 ─────▶ hero.jpg 요청
                                      ⚠ 늦은 발견으로 LCP 지연
```

### 1.2 프리로드 스캐너의 등장

2008년 초 인터넷 익스플로러 팀이 `lookahead downloader`를 구현했고, 거의 동시에 웹킷에도 "Speculative Preload Scanner"라는 유사 메커니즘이 도입됐다. 파이어폭스도 몇 달 후 "speculative parser"라는 이름으로 같은 기능을 추가했다.

프리로드 스캐너는 **메인 파서와 독립적으로 동작하는 가벼운 HTML 스캐너**다. 메인 파서가 멈춰 있는 동안 HTML의 나머지 부분을 먼저 훑어 필요한 리소스를 발견하고 다운로드를 시작한다. 효과는 실측으로 검증됐다.

- **모질라**: CNN.com 홈페이지(110KB HTML, 스타일시트 3개, 외부 자바스크립트 15개)를 무선 네트워크(54/160kbit, 700ms RTT)에서 테스트한 결과 **78.5초 → 63.3초, 19% 개선**
- **구글 크롬**: Alexa top 2000 사이트 테스트에서 Speed Index 기준 **약 20% 개선**

> **핵심 통찰**: 프리로드 스캐너는 **절대로 자바스크립트를 실행하지 않는다.** DOM을 구축하지도, CSS를 파싱하지도 않는다. 순수하게 HTML 마크업만 스캔한다. `<img src="…">`나 `<link href="…">`처럼 **HTML에 명시적으로 선언된 리소스만** 발견할 수 있다.

### 1.3 동작 시나리오

```html
<!DOCTYPE html>
<html>
  <head>
    <link rel="stylesheet" href="styles.css" />
    <script src="app.js"></script>
  </head>
  <body>
    <img src="hero.jpg" alt="Hero" />
    <script src="analytics.js"></script>
  </body>
</html>
```

메인 파서는 `app.js`를 다운로드하고 실행할 때까지 멈춘다. `app.js`가 5MB 번들이고 다운로드에 2초, 파싱·실행에 1초가 걸린다면 `hero.jpg` 다운로드는 3초 뒤에야 시작된다.

프리로드 스캐너가 있으면 상황이 달라진다.

```
브라우저 메인 파서        프리로드 스캐너              네트워크
HTML 파싱 시작 ─────────────────────────────────▶ styles.css 요청
CSS 다운로드 대기 중
                      프리로드 스캐너 활성화
                      HTML 나머지 부분 스캔 ──────▶ hero.jpg 요청 (미리 발견)
                                            ──────▶ analytics.js 요청 (미리 발견)
                      ◀───────────────────────── styles.css 완료
app.js 요청 ────────────────────────────────────▶
스크립트 실행 대기 중     [병렬 다운로드 진행 중]
                                              hero.jpg 다운로드 진행
                                              analytics.js 다운로드 진행
                      ◀───────────────────────── app.js 완료
스크립트 실행 → body 파싱 재개
  → hero.jpg는 이미 다운로드 완료!  ✅ LCP 시간 단축
```

구체적인 수치로 보자. `<head>`에 1.5초 걸리는 블로킹 스크립트가 있고 `<body>`에 LCP 이미지(다운로드 1초)가 있다면,

- **프리로드 스캐너 없음**: 1.5초 대기 후 이미지 다운로드 시작 → LCP 최소 **2.5초**
- **프리로드 스캐너 있음**: 이미지가 스크립트와 병렬 다운로드 → LCP **1.5초** (1초 개선)

> **실무 팁**: Network 탭에서 **중요한 이미지나 폰트가 Low 우선순위로 표시되거나 다운로드 시작 시점(Queueing)이 유난히 늦다면, 그 리소스는 프리로드 스캐너가 발견하지 못했을 가능성이 높다.** HTML에 선언된 리소스는 즉시 시작되지만 자바스크립트로 동적 생성된 이미지는 수 초 뒤에야 시작된다.

## 2. 프리로드 스캐너를 방해하는 안티패턴

프리로드 스캐너는 HTML만 스캔한다. **자바스크립트나 CSS를 통해 리소스를 삽입하는 모든 패턴은 발견할 수 없다.**

### 2.1 자바스크립트로 리소스 동적 삽입

가장 흔한 안티패턴이다. 특히 서드파티 스크립트를 비동기로 로드하기 위해 많이 쓴다.

```ts
// ❌ 프리로드 스캐너가 발견하지 못함
const script = document.createElement('script');
script.src = 'https://example.com/analytics.js';
script.async = true;
document.head.appendChild(script);
```

이 코드가 `<head>`의 블로킹 스크립트 안에 있다면 그 스크립트가 다운로드·파싱·실행될 때까지 `analytics.js` 다운로드가 시작되지 않는다. 수백 ms에서 수 초까지 지연된다.

```ts
// ❌ 이미지도 마찬가지 — LCP 이미지라면 치명적
function loadHeroImage(): void {
  const img = document.createElement('img');
  img.src = '/hero.jpg';
  img.alt = 'Hero';
  document.querySelector('.hero')?.appendChild(img);
}
loadHeroImage();
```

`innerHTML`, `insertAdjacentHTML()`, `outerHTML`로 삽입하는 것도 동일하게 발견되지 않는다.

### 2.2 인라인 스크립트에서 src 설정

HTML 마크업은 존재하되 리소스 URL이 자바스크립트로 결정되는 패턴이다.

```html
<!-- ❌ 프리로드 스캐너가 src를 알 수 없음 -->
<img id="hero" alt="Hero" />
<script>
  const isMobile = window.innerWidth < 768;
  document.getElementById('hero').src = isMobile ? '/hero-mobile.jpg' : '/hero-desktop.jpg';
</script>
```

프리로드 스캐너는 `<img id="hero">`를 발견하지만 `src` 속성이 없으므로 다운로드할 이미지가 없다.

`data-src`에 URL을 담아두고 자바스크립트로 옮기는 지연 로딩 라이브러리 패턴도 같은 문제다.

```html
<!-- ❌ LCP 이미지에 적용하면 성능이 악화됨 -->
<img data-src="/image.jpg" class="lazyload" alt="Image" />
```

이미지 다운로드는 지연 로딩 라이브러리가 로드되고, 초기화되고, 스크롤 이벤트를 감지한 후에야 시작된다.

### 2.3 CSS의 @import

CSS 파일 안에서 다른 CSS를 불러오는 `@import`는 프리로드 스캐너가 발견할 수 없다.

```css
/* styles.css */
@import url('typography.css');
@import url('layout.css');
```

```
HTML 파싱 → styles.css 발견 → 다운로드(200ms) → 파싱(50ms)
                                                    ↓ 이때야 @import 발견
                                    typography.css, layout.css 다운로드 시작
                                                    ↓
                                          모든 CSS 완료 후에야 렌더링
```

두 파일은 **250ms 늦게** 시작된다. 중첩 `@import`는 더 심각하다.

```css
/* styles.css */  @import url('base.css');
/* base.css */    @import url('reset.css'); @import url('variables.css');
```

`reset.css`와 `variables.css`는 `styles.css → base.css` 순서로 다운로드·파싱된 후에야 발견되는 **3단계 지연**이다.

```html
<!-- ✅ 모든 CSS를 HTML에 직접 선언 → 병렬 다운로드 -->
<link rel="stylesheet" href="reset.css" />
<link rel="stylesheet" href="variables.css" />
<link rel="stylesheet" href="typography.css" />
<link rel="stylesheet" href="layout.css" />
```

조건부 CSS도 `@import` 대신 `media` 속성을 쓰면 프리로드 스캐너가 발견할 수 있다.

```html
<link rel="stylesheet" href="print.css" media="print" />
<link rel="stylesheet" href="mobile.css" media="(max-width: 768px)" />
```

### 2.4 SPA 프레임워크의 동적 렌더링

리액트·뷰·스벨트는 자바스크립트로 DOM을 렌더링한다. 컴포넌트 안의 이미지·스크립트·스타일시트는 프리로드 스캐너가 발견하지 못한다.

```tsx
function Hero() {
  return (
    <div className="hero">
      {/* ❌ JSX는 자바스크립트가 실행돼야 DOM이 됨 */}
      <img src="/hero.jpg" alt="Hero" />
    </div>
  );
}
```

CSR 방식에서 이미지가 발견되기까지의 과정은 다음과 같다.

```
bundle.js 다운로드 요청 → 다운로드 완료
  → 리액트 라이브러리 파싱
  → 애플리케이션 번들 파싱
  → 리액트 초기화
  → Hero 컴포넌트 렌더링
  → <img src="/hero.jpg"> DOM 삽입
     ↑ 이 시점에야 브라우저가 이미지를 발견
  → /hero.jpg 다운로드 요청  ⚠ 수 초 지연
```

CSR 앱의 초기 HTML은 보통 이렇게 생겼다.

```html
<head>
  <title>My App</title>
  <script src="/bundle.js"></script>
</head>
<body>
  <div id="root"></div>
</body>
```

프리로드 스캐너가 발견할 수 있는 것은 `bundle.js` 하나뿐이다.

### 2.5 document.write()

오래된 패턴이지만 여전히 일부 서드파티 스크립트가 사용한다. `document.write()`는 HTML 파서가 문서를 읽는 도중 문서 내용을 수정할 수 있어 **프리로드 스캐너가 미리 스캔한 내용을 무효화**할 수 있다.

```js
// ❌ 파서를 블로킹하고 프리로드 스캐너도 우회
document.write('<script src="https://ads.example.com/banner.js"></script>');
```

크롬은 특정 조건에서 `document.write()`로 삽입된 스크립트를 아예 차단하기도 한다.

## 3. 프리로드 스캐너 친화적인 코드 작성하기

핵심 원칙은 간단하다. **리소스를 아무 조작 없이 HTML에 직접 선언한다.**

### 3.1 HTML에 직접 선언하기

```html
<head>
  <link rel="stylesheet" href="styles.css" />
  <script src="app.js" defer></script>
  <link rel="preload" as="font" href="fonts/roboto.woff2" crossorigin />
</head>
<body>
  <img src="/hero.jpg" alt="Hero" fetchpriority="high" />
  <script src="analytics.js" async></script>
</body>
```

`defer`와 `async`를 쓰면 **파서를 블로킹하지 않으면서도 프리로드 스캐너가 발견할 수 있다.** 서드파티 스크립트도 동적 삽입 대신 HTML에 선언하되 `async`를 붙이는 것이 낫다.

```html
<!-- ✅ 구글 애널리틱스도 HTML에 선언 -->
<script src="https://www.googletagmanager.com/gtag/js?id=GA_ID" async></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag() {
    dataLayer.push(arguments);
  }
  gtag('js', new Date());
  gtag('config', 'GA_ID');
</script>
```

### 3.2 조건부 콘텐츠는 CSS로 숨긴다

`display: none`이나 `visibility: hidden`으로 숨긴 요소도 프리로드 스캐너가 발견한다. **CSS에서 숨기는 것일 뿐 HTML에는 그대로 남아 있기 때문이다.**

```html
<!-- ✅ display:none이어도 프리로드 스캐너가 발견 -->
<div class="modal" style="display: none">
  <img src="/modal-image.jpg" alt="Modal" />
</div>
```

사용자가 모달을 열 때쯤이면 이미 이미지 다운로드가 완료돼 있다.

하지만 **프레임워크의 조건부 렌더링은 다르다.** 뷰의 `v-if`나 리액트의 조건부 렌더링은 자바스크립트가 실행되기 전까지 DOM에 존재하지 않는다.

```vue
<!-- ❌ v-if는 자바스크립트 실행 후 DOM 생성 -->
<template>
  <div v-if="isModalOpen">
    <img src="/modal-image.jpg" alt="Modal" />
  </div>
</template>

<!-- ⚠ v-show는 display:none으로 숨김 (SSR일 때 효과) -->
<template>
  <div v-show="isModalOpen">
    <img src="/modal-image.jpg" alt="Modal" />
  </div>
</template>
```

```tsx
// ⚠ 항상 렌더링하고 CSS로 숨김 (SSR일 때 효과)
function Modal({ isOpen }: { isOpen: boolean }) {
  return (
    <div style={{ display: isOpen ? 'block' : 'none' }}>
      <img src="/modal-image.jpg" alt="Modal" />
    </div>
  );
}
```

> **핵심 통찰**: **CSR에서는 `v-show`나 `display:none` 패턴도 소용없다.** 초기 HTML에 없으면 프리로드 스캐너가 발견할 수 없기 때문이다. **SSR/SSG로 HTML에 포함되거나 정적 HTML에 직접 선언된 경우에만** 미리 발견할 수 있다. 또한 이 패턴은 불필요한 리소스를 미리 다운로드하고 DOM 노드가 늘어나는 트레이드오프가 있으므로 **LCP·FCP에 영향을 주는 중요한 리소스에만** 쓴다.

### 3.3 SSR/SSG의 이점

서버에서 HTML을 생성하면 모든 리소스가 HTML에 명시적으로 선언된다.

```html
<!-- SSR: 완전한 HTML -->
<head>
  <link rel="stylesheet" href="/styles.css" />
  <script src="/bundle.js" defer></script>
</head>
<body>
  <div id="root">
    <img src="/hero.jpg" alt="Hero" />
    <link rel="stylesheet" href="/component.css" />
  </div>
</body>
```

프리로드 스캐너가 모든 이미지와 CSS를 즉시 발견한다. **이것이 Next.js·Nuxt·SvelteKit 같은 메타 프레임워크가 SSR/SSG를 기본으로 제공하는 주요 이유 중 하나다.**

```tsx
// Next.js App Router (SSR)
export default function Page() {
  return (
    <div>
      {/* 서버에서 HTML 생성 → 프리로드 스캐너가 즉시 발견 */}
      <Image src="/hero.jpg" alt="Hero" preload />
    </div>
  );
}
```

> **실무 팁**: Next.js 16부터 `priority` 속성은 폐기됐다. LCP 이미지에는 `preload` 속성을 쓰거나 상황에 따라 `fetchpriority="high"`·`loading="eager"`를 직접 지정한다. 다만 **속성보다 중요한 것은 이미지가 애초에 HTML에 포함돼 있다는 사실이다.**

### 3.4 반응형 이미지는 네이티브 API로

자바스크립트로 `window.innerWidth`를 확인해 이미지를 선택하는 대신 `<picture>`와 `srcset`을 쓴다. 이 API들은 HTML에 선언되므로 프리로드 스캐너가 즉시 인식하고, **미디어 쿼리까지 평가해서** 적절한 이미지를 다운로드한다.

```html
<!-- ✅ 반응형 이미지도 프리로드 스캐너가 발견 -->
<picture>
  <source media="(min-width: 768px)" srcset="/hero-desktop.jpg" />
  <source media="(max-width: 767px)" srcset="/hero-mobile.jpg" />
  <img src="/hero-desktop.jpg" alt="Hero" fetchpriority="high" />
</picture>

<!-- ✅ srcset + sizes로도 가능 -->
<img
  srcset="/hero-mobile.jpg 767w, /hero-desktop.jpg 768w"
  sizes="100vw"
  src="/hero-desktop.jpg"
  alt="Hero"
  fetchpriority="high"
/>
```

### 3.5 다섯 가지 핵심 원칙

1. **모든 리소스를 HTML에 직접 선언한다.** 자바스크립트로 동적 삽입하는 대신 `<img>`, `<script>`, `<link>` 태그를 HTML에 작성한다.
2. **조건부 콘텐츠는 CSS로 숨긴다.** DOM 조작 대신 `display: none`을 쓰되, 중요한 리소스에만 적용한다.
3. **`async`와 `defer`를 적극 활용한다.** 파서를 블로킹하지 않으면서 프리로드 스캐너가 발견할 수 있다.
4. **SSR/SSG를 고려한다.** CSR만 쓰면 프리로드 스캐너가 무용지물이 된다.
5. **네이티브 브라우저 API를 사용한다.** 반응형 이미지는 자바스크립트 분기 대신 `<picture>`·`srcset`·`sizes`로 구현한다.

## 4. 불가피한 동적 리소스 최적화

모달 이미지, A/B 테스트 스크립트, 코드 스플리팅 청크처럼 HTML에 선언할 수 없는 리소스도 있다. 이 경우 **Ch4의 리소스 힌트가 프리로드 스캐너의 사각지대를 메운다.**

```html
<head>
  <!-- 동적 삽입될 스크립트를 미리 프리로드로 알림 -->
  <link rel="preload" as="script" href="https://www.googletagmanager.com/gtag/js?id=GA_ID" />
</head>
<body>
  <script>
    // 나중에 동적 삽입하더라도 이미 다운로드 완료
    const script = document.createElement('script');
    script.src = 'https://www.googletagmanager.com/gtag/js?id=GA_ID';
    script.async = true;
    document.head.appendChild(script);
  </script>
</body>
```

### 4.1 동적 import()와 웹팩 매직 코멘트

코드 스플리팅으로 분리된 청크는 필연적으로 동적 리소스지만, 웹팩 매직 코멘트로 로딩 전략을 제어할 수 있다.

```ts
// 여유 시간에 미리 로드 → HTML에 <link rel="prefetch">를 자동 추가
import(/* webpackPrefetch: true */ './components/Modal.js');

// 메인 번들과 병렬로 즉시 다운로드 → 중요한 컴포넌트에만
import(/* webpackPreload: true */ './components/CriticalModal.js');

// 청크 이름 지정으로 디버깅 용이
import(/* webpackChunkName: "product-detail" */ './pages/ProductDetail.js');
```

`React.lazy`와 조합하면 컴포넌트 레벨에서 제어할 수 있다.

```tsx
const AdminPanel = React.lazy(() => import(/* webpackPrefetch: true */ './AdminPanel'));

function App() {
  return <Suspense fallback={<Loading />}>{isAdmin && <AdminPanel />}</Suspense>;
}
```

### 4.2 인터섹션 옵저버로 지연 로딩

스크롤 이벤트로 지연 로딩을 구현하면 성능 문제가 생긴다. 인터섹션 옵저버(*Intersection Observer*)가 더 효율적이다.

```ts
const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const img = entry.target as HTMLImageElement;
        img.src = img.dataset.src ?? '';   // data-src를 src로 이동
        observer.unobserve(img);           // 더 이상 관찰하지 않음
      }
    });
  },
  {
    rootMargin: '50px', // 뷰포트 50px 전에 미리 로드
  },
);

document.querySelectorAll('img[data-src]').forEach((img) => {
  observer.observe(img);
});
```

`rootMargin`을 쓰면 요소가 뷰포트에 나타나기 전에 미리 로드해 사용자가 스크롤했을 때 이미 준비돼 있게 만든다.

브라우저 네이티브 지연 로딩을 쓰면 직접 구현할 필요도 없다.

```html
<img src="/below-fold.jpg" loading="lazy" alt="Below fold" />
```

> **핵심 통찰**: **LCP 이미지에는 어떤 형태의 지연 로딩도 쓰면 안 된다.** 라이브러리든 `loading="lazy"`든 마찬가지다. LCP 이미지는 뷰포트에 즉시 보이므로 지연 로딩이 오히려 발견을 늦춘다. LCP 이미지는 `<img src="/hero.jpg" fetchpriority="high">`로 즉시 로드한다.

### 4.3 예측과 측정

동적 리소스 최적화는 트레이드오프의 연속이다. 프리로드를 많이 쓰면 대역폭을 낭비하고, 프리페치를 많이 쓰면 모바일 데이터를 소비하며, 지연 로딩을 과도하게 쓰면 사용자 경험이 나빠진다.

```ts
// ✅ 실제 사용 패턴을 기반으로 최적화
// 분석 결과 사용자의 60%가 제품 상세 페이지로 이동
if (userBehaviorAnalysis.productDetailClickRate > 0.5) {
  const link = document.createElement('link');
  link.rel = 'prefetch';
  link.href = '/product-detail-chunk.js';
  document.head.appendChild(link);
}
```

> **핵심 통찰**: 동적 리소스 최적화의 핵심은 **'예측'**이다. 사용자가 어떤 리소스를 언제 필요로 할지 예측하고 그에 맞춰 미리 로드하거나 지연시킨다. 하지만 예측은 항상 불확실하므로 **A/B 테스트와 `web-vitals` 측정으로 검증하고 조정해야 한다.** 라이트하우스의 "Preload key requests" 권장사항도 맹목적으로 따르면 안 된다.

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|---|---|---|
| `document.createElement('script')`로 서드파티 삽입 | 삽입 코드가 실행될 때까지 다운로드가 시작되지 않음 | `<script async>`로 HTML에 선언 |
| 인라인 스크립트로 `img.src` 설정 | `src` 없는 `<img>`는 프리로드 스캐너가 다운로드할 것이 없음 | `srcset`/`<picture>`로 대체 |
| CSS `@import` 사용 | CSS 다운로드 + 파싱 후에야 발견되어 250ms 이상 지연, 중첩 시 배가 | 모든 CSS를 `<link>`로 HTML에 선언 |
| LCP 이미지에 지연 로딩 라이브러리(`data-src`) | 라이브러리 로드·초기화·스크롤 감지 후에야 다운로드 시작 | `<img src fetchpriority="high">` |
| LCP 이미지에 `loading="lazy"` | 뷰포트 진입 전까지 다운로드가 지연되어 LCP 악화 | 기본값 `eager` 유지 |
| CSR로 LCP 이미지 렌더링 | 번들 다운로드 → 파싱 → 초기화 → 렌더링을 모두 기다려야 함 | SSR/SSG 도입 또는 `<link rel="preload">` |
| `document.write()`로 스크립트 삽입 | 파서 블로킹 + 프리로드 스캐너 우회, 크롬이 차단하기도 함 | 제거하고 `async` 스크립트로 대체 |
| `innerHTML`로 이미지 삽입 | 자바스크립트 실행 전까지 리소스가 존재하지 않음 | HTML에 직접 선언 |
| CSR에서 `v-show`/`display:none`을 믿음 | 초기 HTML에 없으면 CSS로 숨겨도 발견 못 함 | SSR과 함께 써야 효과가 있음 |
| 모든 조건부 리소스를 `display:none`으로 노출 | 쓰지 않을 리소스까지 다운로드하고 DOM 노드가 늘어남 | LCP·FCP에 영향 주는 리소스에만 적용 |

## 측정과 검증

**크롬 개발자 도구 Network 탭**

1. **리소스 발견 시점**: Queueing 시간이 긴 리소스는 발견이 늦은 것이다. 워터폴에서 다운로드 시작 시점을 비교하면 HTML 선언 리소스와 자바스크립트 생성 리소스의 차이가 명확히 보인다.
2. **우선순위**: Priority 칼럼에서 중요한 리소스가 Low로 표시되는지 확인한다.
3. **미사용 프리로드**: 콘솔에서 "The resource was preloaded using link preload but not used within a few seconds" 경고를 확인한다.

**라이트하우스**

"Preload key requests" 권장사항이 표시된다면 프리로드 스캐너가 놓친 리소스가 있다는 신호다. 다만 각 리소스가 정말 조기 로드가 필요한지, 프리로드가 실제로 LCP를 개선하는지 측정해서 판단한다.

**web-vitals 라이브러리 + A/B 테스트**

`web-vitals`로 LCP·FCP·INP를 수집하고 사용자 그룹 간 차이를 비교하는 것이 프리로드·프리페치 전략의 실제 효과를 가장 정확하게 검증하는 방법이다.

## 체크리스트

**HTML 작성 시**

- [ ] 모든 중요한 리소스(이미지·스크립트·스타일시트)를 HTML에 직접 선언했는가
- [ ] LCP 이미지를 `<img>` 태그로 선언하고 `fetchpriority="high"`를 추가했는가
- [ ] 서드파티 스크립트를 동적 삽입 대신 `<script async>` 또는 `<script defer>`로 선언했는가
- [ ] CSS를 `@import` 대신 `<link rel="stylesheet">`로 선언했는가
- [ ] 폰트를 `<link rel="preload" as="font">`로 선언해 조기 발견되도록 했는가

**자바스크립트 코드**

- [ ] `document.createElement()`로 이미지를 삽입하고 있다면 HTML 선언이나 `srcset`/`<picture>`로 대체 가능한가
- [ ] 인라인 스크립트에서 `src`를 설정하는 패턴을 `srcset`/`<picture>`로 대체 가능한가
- [ ] `document.write()`를 제거했는가
- [ ] LCP 이미지에 지연 로딩 라이브러리나 `loading="lazy"`를 적용하고 있다면 제거했는가

**SPA 프레임워크**

- [ ] CSR 대신 SSR이나 SSG로 완전한 HTML을 제공할 수 있는가
- [ ] 뷰의 `v-if` 대신 `v-show`로 대체 가능한 조건부 렌더링이 있는가(SSR 전제)
- [ ] 리액트 조건부 렌더링을 `display:none`으로 대체해 HTML에 리소스가 포함되도록 할 수 있는가

**불가피한 동적 리소스**

- [ ] 웹팩 매직 코멘트(`webpackPrefetch`, `webpackPreload`)로 청크 로딩 전략을 제어하는가
- [ ] 인터섹션 옵저버로 뷰포트 진입 이미지를 지연 로딩하는가(LCP 이미지 제외)
- [ ] 네이티브 `loading="lazy"`를 뷰포트 밖 이미지에 적용하는가(LCP 이미지 제외)
- [ ] 동적 `import()`로 로드되는 ESModule이 `<link rel="modulepreload">`로 사전 로드되도록 빌드 도구가 설정돼 있는가
- [ ] 동적으로 로드되는 중요 리소스에 `<link rel="preload">` 또는 `prefetch`를 적절히 활용하는가

**반응형 이미지**

- [ ] 반응형 이미지를 자바스크립트 대신 `srcset`·`sizes`로 HTML에 구현했는가
- [ ] 미디어 쿼리가 필요한 경우 `<picture>`와 `<source>`를 사용해 HTML에 선언했는가
- [ ] WebP·AVIF 같은 최신 포맷을 `<source type="…">`로 제공했는가

## 요약

- 프리로드 스캐너는 **메인 파서가 CSS·스크립트로 블로킹된 동안 별도로 동작하는 가벼운 HTML 스캐너**다. HTML 나머지를 미리 훑어 리소스를 발견하고 다운로드를 시작한다.
- 2008년 IE·웹킷·파이어폭스에 거의 동시에 도입됐고, 실측 기준 **19~20%의 로딩 시간 개선** 효과가 있다. 개발자가 설정할 필요 없는 브라우저의 무료 최적화다.
- **결정적 제약: 프리로드 스캐너는 자바스크립트를 실행하지 않고 CSS를 파싱하지도 않는다.** HTML에 명시적으로 선언된 리소스만 발견한다.
- 주요 안티패턴: 자바스크립트 동적 삽입(`createElement`·`innerHTML`), 인라인 스크립트로 `src` 설정, CSS `@import`, `data-src` 지연 로딩 라이브러리, CSR 렌더링, `document.write()`.
- `@import`는 CSS 다운로드+파싱 후에야 발견되므로 250ms 이상 지연되고, 중첩하면 지연이 배가된다. 모든 CSS는 `<link>`로 HTML에 선언한다.
- CSR에서는 `bundle.js` 하나만 발견 가능하다. LCP 이미지는 번들 다운로드 → 파싱 → 리액트 초기화 → 렌더링을 모두 기다려야 하므로 수 초까지 지연된다.
- 다섯 가지 원칙: **HTML 직접 선언 / 조건부는 CSS로 숨김 / `async`·`defer` 활용 / SSR·SSG / 네이티브 API(`<picture>`·`srcset`)**.
- `display:none`으로 숨긴 요소도 프리로드 스캐너가 발견하지만, **CSR에서는 초기 HTML에 없으므로 소용없다.** SSR이 전제다.
- 불가피한 동적 리소스는 `<link rel="preload">`, 웹팩 매직 코멘트(`webpackPrefetch`/`webpackPreload`), 인터섹션 옵저버로 보완한다.
- **LCP 이미지에는 어떤 지연 로딩도 적용하지 않는다.**
- 순서가 중요하다. **리소스 힌트를 추가하기 전에, 먼저 브라우저가 리소스를 발견할 수 있게 만드는 것이 우선이다.** 발견하지 못한 리소스는 우선순위가 아무리 높아도 늦게 로드된다.

## 다른 챕터와의 관계

- **Ch4(리소스 우선순위)**: "브라우저가 리소스를 발견할 수 있어야 우선순위 조정이 의미가 있다"는 결론을 이 장이 이어받는다. 불가피한 동적 리소스에는 Ch4의 `preload`·`prefetch`·`modulepreload`가 사각지대를 메우는 도구로 쓰인다.
- **Ch6(async와 defer)**: 이 장이 권장한 "HTML에 선언하되 파서를 블로킹하지 않게 하라"의 구체적 수단이다. 두 속성의 실행 타이밍과 선택 기준을 다룬다.
- **Ch7(렌더링 블로킹 리소스)**: 메인 파서를 멈추게 하는 CSS·스크립트 자체를 줄이는 방법을 다룬다.
- **Ch10(코드 스플리팅)**: 웹팩 매직 코멘트와 동적 `import()`를 전략 관점에서 본격적으로 다룬다.
- **Ch11(서버로 로직 이동)·Ch16(하이드레이션)**: 이 장이 SSR/SSG를 권장한 이유(프리로드 스캐너 친화성)가 서버·클라이언트 역할 분담과 하이드레이션 논의로 확장된다.
- **Ch12(이미지 최적화)**: `<picture>`·`srcset`·`sizes`·`loading` 속성을 이미지 전용 관점에서 상세히 다룬다.
