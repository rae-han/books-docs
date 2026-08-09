# Chapter 4: 리소스 우선순위를 재정의하면 로딩이 빨라진다

## 핵심 질문

빠른 네트워크와 올바른 로딩 순서는 별개의 문제다. 500KB 서드파티 스크립트가 먼저 내려오고 정작 LCP를 차지하는 히어로 이미지가 나중에 오는 상황을 어떻게 뒤집을 것인가? 브라우저는 어떤 기준으로 우선순위를 매기며, 개발자는 어디까지 개입해야 하는가?

## 1. 브라우저의 리소스 우선순위 메커니즘

> **참고 - 히어로 이미지란**<br><br>웹 페이지 상단에 가장 먼저 표시되는 대형 이미지로 사용자의 첫인상을 결정하는 핵심 시각 요소다. 뉴스 사이트의 메인 기사 이미지, 이커머스의 제품 배너, 랜딩 페이지의 상단 비주얼이 대표적이다. 보통 LCP 요소가 되므로 성능 최적화에서 중요하게 다룬다.

브라우저는 HTML을 파싱하면서 수십~수백 개의 리소스를 발견한다. 대역폭은 제한돼 있고 HTTP/2 멀티플렉싱도 적절한 우선순위 없이는 혼잡만 가중시킨다. 그래서 브라우저는 각 리소스에 자동으로 우선순위를 매긴다. 크롬의 네트워크 스택은 **Highest / High / Medium / Low / Lowest** 5단계로 분류한다.

이 기본 규칙은 대부분 합리적이지만 항상 최적은 아니다. **브라우저는 각 사이트의 맥락을 모르기 때문**이다. 실제로 Network 탭의 Priority 칼럼을 보면 LCP를 차지하는 히어로 이미지가 Medium으로 로드되는 반면, 폴드 아래에 있어 보이지도 않는 이미지가 먼저 내려오는 상황이 흔하다.

### 1.1 중요 렌더링 경로와 블로킹 관계

중요 렌더링 경로(*critical rendering path*)란 브라우저가 HTML을 받아 화면에 픽셀을 그리기까지 거쳐야 하는 필수 단계다.

```
HTML 다운로드
  → HTML 파싱 시작
     ├─ <link rel="stylesheet"> 발견
     │    → CSS 다운로드 (Highest)  ⚠ 렌더링 블로킹
     │      파싱은 계속되지만 렌더링은 대기
     │    → CSS 파싱 완료 → CSSOM 생성
     │
     ├─ <script> 발견
     │    → 자바스크립트 다운로드 (High)  ⚠ 파싱 블로킹
     │      HTML 파싱도 멈춤
     │    → 자바스크립트 실행 → HTML 파싱 재개
     │
     └─ <img> 발견
          → 이미지 다운로드 (Low, 백그라운드)  블로킹 없음

  → DOM + CSSOM → 렌더 트리 생성 → 레이아웃 계산 → 페인트 → FCP
```

- **CSS는 렌더 블로킹**: CSSOM이 없으면 스타일을 적용할 수 없으므로 CSS가 도착할 때까지 렌더링을 멈춘다.
- **동기 자바스크립트는 파싱 블로킹**: 자바스크립트가 DOM을 조작할 수 있으므로 브라우저는 스크립트를 먼저 실행하고 HTML 파싱을 계속한다.
- **이미지는 블로킹하지 않는다**: 이미지가 없어도 텍스트와 레이아웃을 먼저 그릴 수 있다. **이것이 이미지가 낮은 우선순위를 받는 이유다.** 하지만 LCP 요소가 이미지라면 이야기가 달라진다.

프리로드 스캐너(*preload scanner*)는 이 과정을 최적화하는 브라우저 내부 메커니즘이다. HTML 파서가 `<script>` 때문에 멈춰 있을 때도 계속 HTML을 훑어보며 뒤에 있는 `<img>`를 미리 발견해 다운로드를 시작한다. 다만 **HTML만 분석하므로 CSS에서 참조하는 배경 이미지나 자바스크립트로 동적 삽입되는 리소스는 발견하지 못한다**(자세한 내용은 Ch5).

### 1.2 리소스 타입별 기본 우선순위

**CSS 파일: Highest**

```html
<!-- Highest 우선순위 -->
<link rel="stylesheet" href="main.css" />

<!-- Low 우선순위(print용은 화면 렌더링에 불필요) -->
<link rel="stylesheet" href="print.css" media="print" />
```

**자바스크립트: High ~ Low** (위치와 속성에 따라 크게 달라진다)

- `<head>` 안의 동기 스크립트: **High** (HTML 파싱을 막으므로)
- `<body>` 초반의 동기 스크립트: **High** (아직 파싱 초기 단계)
- `<body>` 중후반의 동기 스크립트: **Medium** (상당 부분 파싱 완료)
- `async` 스크립트: **Low** (언제 실행돼도 상관없음)
- `defer` 스크립트: **Low** (`DOMContentLoaded` 전까지 대기)
- 동적으로 삽입된 스크립트: **Low** (기본적으로 `async` 동작)

**이미지: Medium ~ Low**

크롬 117(2023년 9월)부터 뷰포트 내 이미지의 중요성을 인식해 우선순위를 상향한다. **처음 5개의 큰 이미지(10,000px² 이상)는 Low에서 Medium으로 자동 상향**된다.

- 뷰포트 안 큰 이미지(처음 5개): **Medium**
- 뷰포트 안 작은 이미지: **Low**
- 뷰포트 밖(below-the-fold) 이미지: **Low**
- `loading="lazy"` 이미지: 뷰포트 진입 전까지 다운로드 지연, 진입 시 **Low**로 시작

**폰트: High**

`@font-face`로 선언된 웹폰트는 CSS가 파싱되고 해당 폰트를 쓰는 텍스트가 발견될 때 다운로드가 시작된다. 텍스트 렌더링에 필수이므로 High를 받지만 **발견 시점 자체가 늦다.** 이것이 FOIT/FOUT 문제의 원인이다.

**리소스 힌트**

- `<link rel="preload">`: `as` 속성에 따라 결정된다. `as="style"` → Highest, `as="script"`/`as="font"` → High, `as="image"` → Medium
- `<link rel="prefetch">`: **Lowest**. 사실상 프리페치 전용 우선순위로, 현재 페이지 렌더링에 영향을 주지 않고 유휴 대역폭이 있을 때만 다운로드된다.

**전체 요약표**

| 우선순위 | 리소스 타입 | 비고 |
|---|---|---|
| **Highest** | HTML 문서 / 일반 CSS 파일 / `<link rel="preload" as="style">` | 렌더 블로킹 리소스 |
| **High** | `<head>`·`<body>` 초반 동기 스크립트 / `preload as="script"` / `preload as="font"` / `<link rel="modulepreload">` / 웹폰트(`@font-face`) / `fetchpriority="high"` 이미지 | 파싱 블로킹 또는 중요 리소스 |
| **Medium** | `<body>` 중후반 동기 스크립트 / 뷰포트 내 이미지 / `preload as="image"` | 어느 정도 파싱이 진행된 상태 |
| **Low** | `async`·`defer` 스크립트 / 뷰포트 밖 이미지 / `loading="lazy"` 이미지(진입 시) / `fetchpriority="low"` 스크립트 / 조건부 CSS(`media="print"`) | 비차단 리소스 |
| **Lowest** | `<link rel="prefetch">` | 다음 내비게이션 준비, 유휴 대역폭만 사용 |

이 규칙은 크롬 기준이며 파이어폭스·사파리는 약간 다를 수 있다. 하지만 **렌더링이나 파싱을 막는 리소스는 높게, 그렇지 않으면 낮게**라는 핵심 원칙은 동일하다.

### 1.3 잘못된 우선순위가 만드는 문제

**LCP 이미지의 낮은 우선순위**

가장 흔한 문제다. 뷰포트 내 이미지라도 기본적으로 Medium이므로 CSS(Highest)와 자바스크립트(High)가 먼저 다운로드된다. CSS 300KB + JS 500KB라면 이미지 다운로드가 시작되기까지 수백 ms에서 수 초가 걸린다. 라이트하우스는 이를 "Preload Largest Contentful Paint image" 경고로 알려준다.

```html
<!-- ❌ 문제: LCP 이미지가 Medium 우선순위 -->
<img src="hero.jpg" alt="Hero" />

<!-- ✅ 해결 1: preload -->
<link rel="preload" href="hero.jpg" as="image" />
<img src="hero.jpg" alt="Hero" />

<!-- ✅ 해결 2: fetchpriority (더 간단) -->
<img src="hero.jpg" alt="Hero" fetchpriority="high" />
```

**높은 우선순위 리소스의 남발**

> **핵심 통찰**: **모든 것이 높은 우선순위면 우선순위가 없는 것과 같다.** 대역폭은 제한돼 있으므로 high 리소스가 4개면 각각 전체 대역폭의 1/4만 할당받는다. 실무 기준으로 `fetchpriority="high"`를 3개 이상에 쓰면 LCP가 오히려 느려지는 경우가 많다.

**웹폰트의 늦은 발견**

`CSS 다운로드 → CSS 파싱 → @font-face 발견 → 폰트 다운로드` 순서라 폰트가 늦게 도착한다. 그 사이 브라우저는 텍스트를 렌더링하지 못하거나(FOIT) 시스템 폰트로 먼저 보여줬다가 다시 그린다(FOUT). FOUT는 CLS까지 유발한다. `<link rel="preload" as="font">`로 CSS와 병렬 다운로드하면 완화된다.

**동적 삽입 리소스의 지연**

리액트나 뷰로 이미지를 렌더링하면 HTML에는 `<div id="root"></div>`만 있다. `자바스크립트 다운로드 → 실행 → 이미지 발견 → 이미지 다운로드` 순서가 되어 로딩이 극도로 늦어진다.

```ts
const img = document.createElement('img');
img.src = 'hero.jpg';  // 이 시점에야 다운로드 시작 (매우 늦음)
document.body.appendChild(img);
```

해결책은 중요한 이미지를 `<link rel="preload">`로 미리 선언하거나, **SSR로 HTML에 이미지를 포함시키는 것**이다.

## 2. 리소스 힌트로 우선순위 제어하기

### 2.1 preload: 필수 리소스를 미리 로드

`<link rel="preload">`는 현재 페이지에 반드시 필요한 리소스를 브라우저가 자연스럽게 발견하기 **전에** 미리 로드하도록 지시한다.

가장 중요한 특징은 **`as` 속성이 필수**라는 점이다. `as`는 리소스 타입을 명시해 브라우저가 올바른 우선순위와 `Content-Type`을 설정하도록 한다. 없으면 콘솔에 `<link rel=preload> must have a valid 'as' value` 경고가 뜨고, 잘못 지정하면 브라우저가 리소스를 매칭하지 못해 **이중 다운로드**가 발생한다.

```html
<!-- ✅ 올바른 예 -->
<link rel="preload" href="/fonts/custom.woff2" as="font" type="font/woff2" crossorigin />
<link rel="preload" href="/critical.css" as="style" />
<link rel="preload" href="/app.js" as="script" />

<!-- ❌ as 속성 없음 -->
<link rel="preload" href="/app.js" />
```

**시나리오 1: 웹폰트 최적화**

```html
<head>
  <!-- 웹폰트를 CSS보다 먼저 프리로드 -->
  <link rel="preload" href="/fonts/roboto-regular.woff2" as="font" type="font/woff2" crossorigin />
  <link rel="stylesheet" href="/styles.css" />
</head>
```

> **실무 팁**: 폰트 프리로드에 **`crossorigin`을 빠뜨리면 이중 다운로드가 발생한다.** 웹폰트는 CORS 요청으로 로드되는데, `crossorigin` 없이 프리로드하면 브라우저가 나중에 `@font-face`에서 CORS로 다시 요청한다. 크롬은 콘솔에 "the request credentials mode does not match. Consider taking a look at crossorigin attribute" 경고를 표시하고, Network 탭에서 같은 폰트가 두 번 내려오는 것을 볼 수 있다.

**시나리오 2: LCP 이미지 최적화**

```html
<!-- 방법 1: preload (as="image"라 Medium 우선순위) -->
<link rel="preload" href="/hero.jpg" as="image" />
<img src="/hero.jpg" alt="Hero" />

<!-- 방법 2: fetchpriority (더 간단, High 우선순위) -->
<img src="/hero.jpg" alt="Hero" fetchpriority="high" />
```

**시나리오 3: 동적 삽입 스크립트 최적화**

SPA에서 프리로드 스캐너가 발견하지 못하는 청크를 미리 선언한다.

```html
<link rel="preload" href="/vendors~main.js" as="script" />
<link rel="preload" href="/main.js" as="script" />
<div id="root"></div>
```

**주의사항**

- **3개 이하만 프리로드한다.** 여러 리소스가 대역폭을 나눠 쓰면 각각 느려진다.
- **프리로드한 리소스는 반드시 곧 사용돼야 한다.** 크롬은 `load` 이벤트로부터 수 초 이내에 사용되지 않으면 "The resource was preloaded using link preload but not used within a few seconds from the window's load event" 경고를 표시한다(실측 기준 3~5초는 경고 없음, 10초 이상이거나 미사용이면 경고).

### 2.2 prefetch: 다음 페이지를 위한 사전 로딩

`prefetch`는 `preload`와 정반대 개념이다. **다음 내비게이션**에서 쓸 리소스를 Lowest 우선순위로 받아둔다. 브라우저는 현재 페이지의 중요 리소스를 모두 다운로드하고 남은 유휴 대역폭이 있을 때만 프리페치한다.

| 특성 | preload | prefetch |
|---|---|---|
| 목적 | 현재 페이지 필수 리소스 | 다음 페이지 준비 |
| 우선순위 | High ~ Highest | Lowest |
| 사용 시점 | 즉시(수 초 이내) | 다음 내비게이션 |
| 미사용 시 경고 | 있음(콘솔 경고) | 없음 |
| 대역폭 영향 | 현재 페이지와 경쟁 | 유휴 시에만 사용 |

Next.js·Nuxt·리액트 라우터는 뷰포트에 보이는 링크의 청크를 자동으로 프리페치한다.

```tsx
import Link from 'next/link';

function ProductList() {
  return (
    <div>
      {/* 이 링크가 뷰포트에 보이면 /product/123 청크를 자동 prefetch */}
      <Link href="/product/123">상품 보기</Link>
    </div>
  );
}
```

`prefetch={false}`로 비활성화하거나, 반대로 중요한 페이지를 명시적으로 프리페치할 수도 있다.

```tsx
import { useRouter } from 'next/router';
import { useEffect } from 'react';

function HomePage() {
  const router = useRouter();

  useEffect(() => {
    // 사용자가 70% 이상 방문하는 페이지를 미리 prefetch
    router.prefetch('/product/best-seller');
  }, [router]);

  return <div>홈페이지</div>;
}
```

**프리페치를 쓸 만한 경우는 세 가지뿐이다.**

1. **명확한 플로우**: 랜딩 → 회원가입, 상품 목록 → 상품 상세, 장바구니 → 결제
2. **분석 데이터로 검증된 높은 이동률**: 애널리틱스로 70% 이상의 이동이 확인된 경우
3. **사용자 인터랙션 예측**: 버튼 hover나 터치 순간에 프리페치 시작

```tsx
function ProductCard({ productId }: { productId: string }) {
  const handleMouseEnter = () => {
    const link = document.createElement('link');
    link.rel = 'prefetch';
    link.href = `/product/${productId}.js`;
    document.head.appendChild(link);
  };

  return (
    <div onMouseEnter={handleMouseEnter}>
      <a href={`/product/${productId}`}>상품 보기</a>
    </div>
  );
}
```

> **실무 팁**: 크롬은 `<link rel="prerender">`를 셀룰러 네트워크에서 자동 비활성화하며, Speculation Rules API의 prerender도 Save-Data 모드나 Energy Saver 모드에서 자동 비활성화된다. 일반 `<link rel="prefetch">`는 브라우저가 자동 제한하지 않지만 quicklink나 Next.js 같은 라이브러리는 느린 네트워크·Save-Data 모드에서 프리페치를 끈다.

### 2.3 preconnect와 dns-prefetch: 연결 준비하기

리소스를 받기 전에 브라우저는 **DNS 조회 → TCP 핸드셰이크 → TLS 협상** 세 단계를 거쳐야 하고, 각 단계마다 RTT가 소요된다. 외부 도메인일수록 이 오버헤드가 크다.

- **`preconnect`**: DNS 조회 + TCP 연결 + TLS 협상을 모두 미리 수행한다. 이 과정은 일반적으로 300~500ms 소요되며 느린 모바일에서는 더 오래 걸린다.
- **`dns-prefetch`**: DNS 조회만 미리 수행한다. DNS 조회는 보통 20~120ms 걸리므로 이것만 해둬도 효과가 있다. 오버헤드가 작고 지원 범위가 넓다.

```html
<!-- 구글 폰트: preconnect 두 개가 필요 -->
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />

<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Roboto&display=swap" />
```

`fonts.googleapis.com`은 CSS를, `fonts.gstatic.com`은 실제 폰트 파일을 제공한다. 폰트 파일은 CORS 요청이므로 `crossorigin`이 필요하다.

> **실무 팁**: **`preconnect`는 1~2개 도메인에만 쓴다.** 실제로 연결을 맺으므로 메모리와 CPU를 소비하고, 사용하지 않는 연결은 10초 후 자동으로 닫힌다. 나머지 외부 도메인은 `dns-prefetch`로 충분하다.

```html
<!-- ✅ 좋은 예 -->
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link rel="dns-prefetch" href="https://cdn.jsdelivr.net" />
<link rel="dns-prefetch" href="https://www.google-analytics.com" />
<link rel="dns-prefetch" href="https://www.googletagmanager.com" />
```

**preconnect가 효과적인 세 가지 시나리오**

1. **웹폰트**: 폰트는 CSS 파싱 후에야 요청되므로 연결 오버헤드가 크다. 프리커넥트는 사실상 필수다.
2. **CDN 리소스**: LCP 이미지가 CDN에 있다면 프리커넥트가 LCP를 크게 개선한다.
3. **API 서버**: SPA에서 첫 렌더링 직후 API를 호출하는 경우, 특히 서버가 다른 지역에 있을 때 효과가 크다.

라이트하우스는 외부 도메인 리소스가 많으면 "Preconnect to required origins" 제안을 준다. Network 탭에서 외부 리소스의 **Queueing·Stalled 시간이 길다면** 프리커넥트로 개선할 수 있다.

### 2.4 modulepreload: ESModule 사전 로딩

ESModule은 의존성이 깊어질수록 워터폴이 길어진다. `app.js`가 `utils.js`를, `utils.js`가 `helpers.js`를 임포트하면 브라우저는 각 모듈을 파싱해야 다음 의존성을 발견하므로 순차적으로 다운로드한다.

```html
<!-- 기본 ESModule 로딩 (워터폴 발생) -->
<script type="module" src="/app.js"></script>
<!-- app.js 다운로드 → 파싱 → utils.js 발견 → 다운로드 → 파싱 → helpers.js 발견... -->

<!-- modulepreload로 병렬 로딩 -->
<link rel="modulepreload" href="/app.js" />
<link rel="modulepreload" href="/utils.js" />
<link rel="modulepreload" href="/helpers.js" />
<script type="module" src="/app.js"></script>
<!-- 세 파일을 동시에 다운로드 -->
```

`modulepreload`는 High 우선순위를 받으며, 모듈을 다운로드한 뒤 **즉시 파싱해 모듈 맵(module map)에 저장**한다. 나중에 `import`를 만나면 파싱 단계를 건너뛰고 바로 실행된다.

| 특성 | `preload as="script"` | `modulepreload` |
|---|---|---|
| 대상 | 일반 스크립트 | ESModule |
| 파싱 | 실행 시점에 파싱 | 즉시 파싱 |
| 의존성 처리 | 명시된 파일만 다운로드 | 명시된 파일만 다운로드(브라우저에 따라 정적 의존성도 가져올 수 있음) |
| 캐시 위치 | HTTP 캐시 | 모듈 맵(이미 파싱된 상태로 저장) |
| 브라우저 지원 | 모든 모던 브라우저 | 크롬 66+, 사파리 17.0+, 파이어폭스 115+ |

**실무에서 수동으로 추가하는 경우는 드물다.** 비트가 빌드 시 의존성 그래프를 분석해 필요한 `modulepreload`를 HTML에 자동 삽입하기 때문이다.

```html
<!-- 비트 빌드 결과 예시 -->
<head>
  <link rel="modulepreload" href="/assets/index.js" />
  <link rel="modulepreload" href="/assets/vendor.js" />
  <link rel="modulepreload" href="/assets/utils.js" />
</head>
```

다만 SPA에서 동적으로 로드되는 라우트 청크는 빌드 툴이 자동 처리하지 않으므로 필요하면 수동으로 추가한다.

```tsx
import { useEffect } from 'react';

function HomePage() {
  useEffect(() => {
    // 방문 확률이 높은 라우트 청크를 미리 로드
    const link = document.createElement('link');
    link.rel = 'modulepreload';
    link.href = '/assets/ProductPage.js';
    document.head.appendChild(link);
  }, []);

  return <div>홈페이지</div>;
}
```

## 3. fetchpriority 속성으로 세밀하게 제어하기

리소스 힌트는 `<head>`에 별도로 추가해야 하고 URL을 두 번 명시해야 한다. 동적으로 생성되거나 조건부로 로드되는 리소스에는 쓰기 어렵다. `fetchpriority`는 **리소스를 선언하는 바로 그 자리에서** 우선순위를 지정한다.

### 3.1 작동 원리

`fetchpriority`는 `high`, `low`, `auto` 세 값만 받으며 **절대적 우선순위가 아니라 상대적 힌트**다. `high`는 "Highest로 설정해줘"가 아니라 "기본보다 높게 해줘"라는 의미이며, 브라우저가 내부적으로 적절한 레벨을 결정한다.

```html
<!-- 기본: Medium -->
<img src="/hero.jpg" alt="Hero" />

<!-- high: High로 상승 -->
<img src="/hero.jpg" alt="Hero" fetchpriority="high" />

<!-- low: Low로 하락 -->
<img src="/footer.jpg" alt="Footer" fetchpriority="low" />
```

`<img>`, `<script>`, `<link>`, `<iframe>`에 쓸 수 있고 `fetch()` API와 `<link rel="preload">`에도 적용된다.

```html
<script src="/analytics.js" fetchpriority="low"></script>
<link rel="stylesheet" href="/critical.css" fetchpriority="high" />
<link rel="preload" href="/hero.jpg" as="image" fetchpriority="high" />
```

```ts
fetch('/api/user', { priority: 'high' }).then((res) => res.json());
```

지원하지 않는 브라우저는 속성을 무시하므로 점진적 개선으로 안전하게 쓸 수 있다.

> **핵심 통찰**: `preload`와 `fetchpriority`는 역할이 다르다. **`preload`는 발견 시점을 앞당기고, `fetchpriority`는 발견 시점은 그대로 두고 우선순위만 조정한다.** CSS 안의 배경 이미지나 폰트처럼 HTML에 직접 명시되지 않은 리소스에는 `fetchpriority`를 쓸 수 없으므로 여전히 `preload`가 필요하다. 반대로 조건부 렌더링되는 리소스에는 미사용 경고가 나지 않는 `fetchpriority`가 안전하다.

### 3.2 이미지 우선순위 최적화

`fetchpriority`가 가장 효과적인 곳은 이미지다. 라이트하우스의 "Preload Largest Contentful Paint image" 제안을 해결하는 가장 간단한 방법이기도 하다.

```html
<!-- LCP 이미지: 높은 우선순위 -->
<img src="/hero.jpg" alt="Hero" fetchpriority="high" />

<!-- 두 번째 이미지: 기본 우선순위 (auto는 생략 가능) -->
<img src="/feature1.jpg" alt="Feature 1" />

<!-- 폴드 아래 이미지: 지연 로딩 (fetchpriority 불필요) -->
<img src="/footer.jpg" alt="Footer" loading="lazy" />

<!-- 중요하지 않은 이미지: 낮은 우선순위 -->
<img src="/decoration.jpg" alt="Decoration" fetchpriority="low" />
```

`loading="lazy"`를 이미 쓰고 있다면 `fetchpriority="low"`는 불필요하다. `lazy`는 뷰포트 밖 이미지의 다운로드 자체를 지연시키므로 이미 충분히 낮다.

`srcset`과 함께 써도 정상 작동한다. 브라우저가 적절한 이미지를 선택한 후 `fetchpriority`를 적용한다.

```html
<img
  srcset="/hero-small.jpg 480w, /hero-medium.jpg 768w, /hero-large.jpg 1200w"
  sizes="100vw"
  src="/hero-large.jpg"
  alt="Hero"
  fetchpriority="high"
/>
```

> **핵심 통찰**: **`fetchpriority="high"`는 단 하나의 LCP 이미지에만 쓴다.** 여러 이미지를 동시에 높은 우선순위로 내려받으면 대역폭을 나눠 쓰게 되어 각각 느려진다.

### 3.3 스크립트와 스타일시트

이미지만큼 흔하지는 않지만 서드파티 스크립트의 우선순위를 낮추는 데 유용하다.

```html
<!-- 중요한 앱 스크립트: 기본 우선순위(High) -->
<script src="/app.js"></script>

<!-- 서드파티 분석·광고: 낮은 우선순위 -->
<script src="/analytics.js" async fetchpriority="low"></script>
<script src="/ads.js" defer fetchpriority="low"></script>

<!-- A/B 테스트 스크립트: 깜빡임(flicker) 방지를 위해 높은 우선순위 -->
<script src="/experiment.js" fetchpriority="high"></script>
```

이미 `async`나 `defer`를 쓰고 있다면 우선순위가 이미 낮으므로 `fetchpriority="low"`의 추가 효과는 크지 않다.

CSS는 기본이 Highest이므로 `fetchpriority="high"`가 거의 불필요하다. 다만 `media` 속성으로 조건부 로드하는 경우에는 유용하다.

```html
<link rel="stylesheet" href="/dark-mode.css" media="(prefers-color-scheme: dark)" fetchpriority="high" />
<link rel="stylesheet" href="/print.css" media="print" fetchpriority="low" />
```

## 4. 프레임워크별 적용 방법

### 4.1 Next.js

프로덕션 빌드 시 여러 리소스 힌트를 자동 생성한다. `<Link>` 컴포넌트는 뷰포트에 보이는 링크의 청크를 자동 프리페치한다.

> **실무 팁**: **Next.js 16부터 `<Image>`의 `priority` 프롭은 폐기됐다.** LCP 이미지에는 `preload` 프롭을 쓰거나, 상황에 따라 `fetchpriority="high"` 또는 `loading="eager"`를 직접 지정한다.

```tsx
import Image from 'next/image';

function Hero() {
  return <Image src="/hero.jpg" alt="Hero" width={1200} height={600} preload />;
}
```

폰트는 `next/font` 모듈이 리소스 힌트를 자동 처리한다. 빌드 타임에 폰트를 다운로드해 자체 호스팅하고, `preload` 링크를 자동 추가하며, 폰트 폴백으로 CLS를 방지한다.

```tsx
import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin'], display: 'swap' });

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko" className={inter.className}>
      <body>{children}</body>
    </html>
  );
}
// 빌드 시 자동 생성:
// <link rel="preload" href="/_next/static/media/inter.woff2" as="font" type="font/woff2" crossorigin />
```

로컬 폰트도 `next/font/local`로 동일한 최적화를 받는다.

```tsx
import localFont from 'next/font/local';

const customFont = localFont({
  src: [
    { path: './fonts/CustomFont-Regular.woff2', weight: '400' },
    { path: './fonts/CustomFont-Bold.woff2', weight: '700' },
  ],
  display: 'swap',
});
```

### 4.2 Nuxt

`@nuxt/fonts` 모듈이 폰트 최적화를 자동 처리한다. 빌드 타임에 폰트를 자체 호스팅하고 `preload` 링크를 추가하며, fontaine으로 폰트 메트릭을 맞춰 CLS를 방지한다.

```bash
npx nuxt module add fonts
```

```ts
// nuxt.config.ts
export default defineNuxtConfig({
  modules: ['@nuxt/fonts'],
});
```

CSS에서 폰트 패밀리를 쓰기만 하면 자동으로 최적화된다. 로컬 폰트도 `fonts.families` 설정으로 처리한다.

Nuxt 3에서는 `useHead()` 컴포저블로 컴포넌트 단위 리소스 힌트를 추가할 수 있다.

```vue
<script setup lang="ts">
useHead({
  link: [{ rel: 'preload', href: '/hero.jpg', as: 'image' }],
});
</script>

<template>
  <img src="/hero.jpg" alt="Hero" fetchpriority="high" />
</template>
```

### 4.3 비트

프로덕션 빌드 시 진입점 모듈과 주요 의존성에 대해 `<link rel="modulepreload">`를 자동 삽입한다. 커스텀 힌트는 `index.html`을 직접 수정하거나 플러그인으로 추가한다.

```html
<!DOCTYPE html>
<html lang="ko">
  <head>
    <meta charset="UTF-8" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link rel="preload" href="/fonts/custom.woff2" as="font" type="font/woff2" crossorigin />
    <title>Vite App</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|---|---|---|
| 6개 이상 프리로드 | 대역폭 경쟁으로 각 리소스가 느려지고 LCP가 오히려 악화 | 핵심 2~3개만 |
| 여러 이미지에 `fetchpriority="high"` | 모든 것이 높으면 우선순위가 없는 것과 같다 | LCP 이미지 하나에만 |
| 폰트 프리로드에 `crossorigin` 누락 | CORS 불일치로 같은 폰트가 두 번 다운로드됨 | `crossorigin` 필수 추가 |
| `preload`에 `as` 누락 또는 오지정 | 우선순위 오설정 + 리소스 매칭 실패로 이중 다운로드 | 정확한 `as` 값 지정 |
| 현재 페이지 리소스를 `prefetch` | Lowest 우선순위로 로드되어 LCP가 지연됨 | `preload` 또는 `fetchpriority="high"` |
| 조건부 렌더링 리소스를 `preload` | 사용되지 않으면 대역폭 낭비 + 콘솔 경고 | hover 시점에 `prefetch`로 전환 |
| 5개 이상 `preconnect` | 실제 TCP/TLS 연결을 유지하며 메모리·CPU 낭비 | 중요 1~2개만, 나머지는 `dns-prefetch` |
| LCP 이미지에 `loading="lazy"` | 뷰포트 진입 후에야 다운로드가 시작되어 LCP 악화 | 기본값 `eager` 유지 |
| LCP 이미지를 자바스크립트로 동적 삽입 | 프리로드 스캐너가 발견하지 못해 극도로 늦어짐 | SSR로 HTML에 포함하거나 `preload` 선언 |
| 프레임워크 자동 최적화와 중복 적용 | 같은 리소스에 힌트가 두 번 걸려 혼란 유발 | 프레임워크가 처리하는 부분은 그대로 둔다 |

## 측정과 검증

**크롬 개발자 도구 Network 탭**

칼럼 헤더를 우클릭해 Priority 항목을 체크하면 각 리소스의 우선순위를 볼 수 있다. LCP 이미지에 `fetchpriority="high"`를 추가했다면 Priority가 `High`로 표시돼야 한다. 워터폴 차트로 실제 다운로드 순서를 함께 확인한다.

**라이트하우스**

- "LCP request discovery" - LCP 리소스 발견이 늦은지 진단
- "Preload Largest Contentful Paint image" - LCP 이미지 우선순위 문제
- "Preconnect to required origins" - 외부 도메인 연결 준비 제안

**Performance 패널**

리소스 로딩 타임라인으로 병목 지점을 찾고, Performance Insights로 LCP 요소가 무엇인지 식별한다.

**콘솔 경고**

- `<link rel=preload> must have a valid 'as' value` - `as` 누락
- `The resource was preloaded using link preload but not used within a few seconds` - 미사용 프리로드
- `the request credentials mode does not match` - `crossorigin` 누락으로 인한 이중 다운로드

**개선 전후 비교**

적용 후 반드시 라이트하우스를 다시 실행하고 실제 핵심 웹 지표(LCP·INP·CLS)를 측정한다. **개선이 없다면 힌트를 제거하는 것도 최적화다.**

## 체크리스트

**초기 분석**

- [ ] 라이트하우스로 "LCP request discovery", "Preconnect candidates" 진단 확인
- [ ] Network 탭에서 Priority 칼럼을 활성화해 현재 우선순위 확인
- [ ] Performance 패널에서 리소스 로딩 타임라인 분석해 병목 파악
- [ ] LCP 요소 식별(Performance Insights 활용)

**LCP 최적화**

- [ ] LCP 이미지가 HTML에 직접 포함돼 있는지 확인(자바스크립트 동적 삽입 피하기)
- [ ] LCP 이미지에 `<link rel="preload" as="image">` 또는 `fetchpriority="high"` 적용
- [ ] LCP 이미지에 `loading="lazy"`를 쓰지 않기(기본값 `eager` 유지)
- [ ] 프레임워크 사용 시 LCP 이미지 우선 로드(Next.js `<Image preload>`, Nuxt `preload` 등)

**외부 도메인 최적화**

- [ ] 외부 폰트 서버(구글 폰트, 어도비 폰트)에 `preconnect` 추가
- [ ] 초기 렌더링에 필요한 외부 API 서버에 `preconnect` 추가
- [ ] 외부 CDN에 `preconnect` 추가(이미지·스크립트 등)
- [ ] 프리커넥트는 최대 3~4개로 제한
- [ ] 우선순위가 낮은 외부 도메인은 `dns-prefetch`만 사용

**폰트 최적화**

- [ ] 크리티컬 폰트에 `<link rel="preload" as="font" type="font/woff2" crossorigin>` 추가
- [ ] 폰트 프리로드 시 `crossorigin` 속성 반드시 추가(이중 다운로드 방지)
- [ ] 폰트 프리로드는 실제로 필요한 1~2개만 적용
- [ ] `font-display: swap` 또는 `optional`과 함께 사용

**이미지 최적화**

- [ ] 폴드 아래 이미지에 `loading="lazy"` 적용
- [ ] 크리티컬하지 않은 이미지에 `fetchpriority="low"` 추가
- [ ] 히어로 이미지 등 중요 이미지에 `fetchpriority="high"` 적용
- [ ] 반응형 이미지(`srcset`, `sizes`)와 함께 사용해 최적 이미지 선택

**자바스크립트 최적화**

- [ ] 크리티컬하지 않은 서드파티 스크립트에 `async` 또는 `defer` 추가
- [ ] 분석 스크립트에 `fetchpriority="low"` 추가
- [ ] `<script type="module">`은 자동으로 `defer`가 적용되므로 추가 설정 불필요
- [ ] 번들러가 자동 생성하는 `modulepreload`는 그대로 유지

**내비게이션 최적화**

- [ ] SPA에서 다음 라우트 청크에 `<link rel="prefetch">` 적용
- [ ] 프레임워크의 자동 프리페치 기능 활용(Next.js `<Link>`, Nuxt `<NuxtLink>`)
- [ ] 방문 가능성이 높은 페이지만 선택적으로 프리페치

**검증 및 모니터링**

- [ ] Network 탭에서 Priority가 의도대로 설정됐는지 확인
- [ ] 라이트하우스를 다시 실행해 경고가 사라졌는지 확인
- [ ] Performance 패널에서 개선 전후 타임라인 비교
- [ ] 실제 핵심 웹 지표(LCP·INP·CLS) 측정으로 효과 검증
- [ ] 콘솔에 "preloaded but not used" 경고가 없는지 확인

## 요약

- 브라우저는 리소스에 자동으로 5단계 우선순위(Highest/High/Medium/Low/Lowest)를 매긴다. **렌더링이나 파싱을 막는 리소스는 높게, 그렇지 않으면 낮게**가 원칙이다.
- CSS는 렌더 블로킹이라 Highest, 동기 자바스크립트는 파싱 블로킹이라 High, 이미지는 블로킹하지 않아 Medium~Low를 받는다. **LCP 이미지가 Medium이라 CSS·JS보다 늦게 오는 것이 가장 흔한 문제다.**
- 크롬 117부터 뷰포트 내 큰 이미지 처음 5개는 Low에서 Medium으로 자동 상향된다.
- 네 가지 리소스 힌트는 목적이 명확히 다르다. **`preconnect`**(외부 도메인 연결 준비) / **`dns-prefetch`**(DNS만, 더 가벼움) / **`preload`**(현재 페이지 필수 리소스를 미리 발견) / **`prefetch`**(다음 페이지를 유휴 대역폭으로 준비).
- `preload`는 `as` 속성이 필수이고, 폰트에는 `crossorigin`이 필수다. 빠뜨리면 이중 다운로드가 발생한다.
- `modulepreload`는 ESModule의 의존성 워터폴을 평탄화한다. 다운로드 후 즉시 파싱해 모듈 맵에 저장하므로 `preload as="script"`보다 ESM 프로젝트에 적합하다. 비트가 자동 삽입한다.
- `fetchpriority`는 상대적 힌트다. **발견 시점을 앞당기는 것이 아니라 우선순위만 조정한다.** 발견 시점이 문제면 `preload`, 순위만 문제면 `fetchpriority`.
- 최적화의 역설: **`preload` 남발, `fetchpriority="high"` 남발, `preconnect` 남발은 모두 역효과다.** 프리로드는 3개 이하, high는 1~2개, 프리커넥트는 1~2개가 기준선이다.
- 프레임워크는 이미 많은 것을 자동화한다. Next.js `next/font`·`<Link>` 자동 프리페치, Nuxt `@nuxt/fonts`, 비트 `modulepreload`. **프레임워크가 못 하는 것만 직접 추가한다.**
- 순서는 언제나 같다. **문제를 측정으로 먼저 발견 → 최소한의 힌트만 추가 → 적용 후 다시 측정.** 개선이 없으면 제거하는 것도 최적화다.

## 다른 챕터와의 관계

- **Ch1(네트워크 최적화)**: HTTP/2 스트림 우선순위가 구현 불일치로 폐기됐다는 점을 다뤘다. 이 장의 리소스 힌트와 `fetchpriority`는 브라우저 레벨에서 그 공백을 메우는 수단이다.
- **Ch5(프리로드 스캐너)**: "브라우저가 리소스를 발견할 수 있어야 우선순위 조정이 의미가 있다"는 이 장의 결론을 이어받는다. 프리로드 스캐너를 방해하는 안티패턴을 다룬다.
- **Ch6(async와 defer)**: 스크립트 우선순위가 위치·속성에 따라 어떻게 달라지는지 이 장에서 요약했고, 그 실행 타이밍과 선택 기준을 본격적으로 다룬다.
- **Ch7(렌더링 블로킹 리소스)**: 중요 렌더링 경로에서 CSS·JS의 블로킹을 실제로 줄이는 기법(크리티컬 CSS 인라인화, 미디어 쿼리 조건부 로딩)을 다룬다.
- **Ch12(이미지 최적화)**: `srcset`·`sizes`·`loading`·`decoding` 등 이미지 전용 속성과 이 장의 `fetchpriority`가 함께 쓰인다.
- **Ch14(폰트 최적화)**: 이 장에서 언급한 FOIT/FOUT, `font-display`, 폰트 프리로드를 폰트 관점에서 전면적으로 다룬다.
- **Ch25(차세대 웹 표준)**: Speculation Rules API는 `prefetch`/`prerender`를 선언적으로 확장한 차세대 표준이다.
