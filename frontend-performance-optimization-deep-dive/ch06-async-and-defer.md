# Chapter 6: async와 defer는 로딩 병목을 풀기 위한 가장 기본적인 도구다

## 핵심 질문

일반 `<script>` 태그는 HTML 파싱을 완전히 멈춘다. `async`와 `defer`는 각각 언제 스크립트를 실행하며 순서는 어떻게 보장되는가? 그리고 "라이브러리 문서가 시키는 대로 붙여넣은" 스크립트 태그에 무엇을 붙여야 하는지 어떻게 판단하는가?

## 1. 스크립트가 렌더링을 막는 방식

브라우저는 HTML을 위에서 아래로 읽으며 DOM 트리를 구축한다. `<div>`, `<p>`, `<img>` 같은 태그는 빠르게 처리하지만 `<script>` 태그를 만나면 즉시 파싱을 멈춘다. 이를 **파서 블로킹(*parser blocking*)**이라고 한다.

스크립트 처리는 세 단계로 진행되며, **세 단계가 모두 끝날 때까지 HTML 파서는 멈춰 있다.**

1. **다운로드**: 외부 스크립트라면 파일을 받는다(인라인은 이 단계 생략)
2. **파싱과 컴파일**: 자바스크립트를 파싱하고 실행 가능한 바이트코드로 컴파일한다
3. **실행**: `console.log()`, DOM 조작, 변수 선언 등 모든 코드가 실행된다

다운로드 500ms + 파싱·컴파일 100ms + 실행 200ms라면 HTML 파싱은 총 **800ms** 중단된다.

```html
<head>
  <title>Example</title>
  <script src="/vendor.js"></script>
  <!-- ⚠ 파서 멈춤: 다운로드 500ms + 파싱 100ms + 실행 200ms = 800ms -->
  <script src="/app.js"></script>
  <!-- ⚠ 파서 또 멈춤: 파싱 50ms + 실행 150ms = 200ms -->
</head>
<body>
  <!-- 여기까지 도달하는 데 1000ms가 추가로 걸림 -->
  <img src="/hero.jpg" alt="Hero" />
</body>
```

프리로드 스캐너가 `app.js`를 미리 다운로드했더라도 마찬가지다. **`vendor.js`가 실행되는 동안 파서가 멈춰 있고, 그 후 `app.js` 실행 시간 동안 또 멈추기 때문이다.**

### 1.1 왜 브라우저는 이렇게 동작하는가

근본 원인은 **자바스크립트가 동기적으로 실행되며 현재까지 파싱된 DOM에 즉시 접근·조작할 수 있다**는 점이다. 네 가지 이유를 보자.

1. **스크립트가 이미 파싱된 DOM을 읽거나 조작할 수 있다.** 파싱을 계속하면서 스크립트를 병렬 실행하면 "아직 파싱 중인" DOM을 읽어 예상치 못한 결과가 나온다.
2. **스크립트 간 실행 순서가 보장되어야 한다.** 앞 스크립트가 전역 변수를 선언하면 뒤 스크립트가 그것을 쓸 수 있어야 한다(jQuery → 플러그인).
3. **스크립트가 전역 상태를 변경할 수 있다.** `window` 객체에 변수를 추가하거나 프로토타입을 수정하면 이후 코드에 영향을 준다.
4. **`document.write()`가 파서 위치에 직접 HTML을 삽입할 수 있다.** 현대 웹에서 거의 쓰지 않지만 하위 호환성을 위해 여전히 지원된다.

### 1.2 파서 블로킹 vs 렌더링 블로킹

- **파서 블로킹**: HTML 파싱을 멈추는 것
- **렌더링 블로킹**: 화면 그리기를 멈추는 것

CSS는 **렌더 블로킹이지만 파서 블로킹은 아니다.** 브라우저는 CSS를 기다리는 동안에도 HTML 파싱을 계속할 수 있다(프리로드 스캐너 작동). 다만 CSS가 완료될 때까지 화면을 그리지 않는다.

반면 스크립트는 **파서 블로킹이면서 동시에 렌더 블로킹**이다. 더 정확히는 **스크립트가 CSSOM이 준비될 때까지 실행을 지연시킨다.** 스크립트가 `getComputedStyle()` 같은 API로 스타일 정보를 읽을 수 있기 때문이다.

```html
<head>
  <link rel="stylesheet" href="/styles.css" />  <!-- 500ms 다운로드 -->
  <script src="/app.js"></script>
  <!-- app.js는 다운로드가 끝나도 styles.css 완료 전까지 실행되지 않음 -->
</head>
```

### 1.3 실제 규모의 영향

HTTP Archive의 2024년 데이터 기준 데스크톱 페이지 중간값은 **23개**, 모바일은 **22개**의 자바스크립트 파일을 로드한다. 모두 일반 `<script>`로 로드하고 스크립트당 평균 100ms 실행 시간이면 **2.2초의 블로킹**이 발생한다. FCP와 LCP를 직접 악화시키는 수치다.

```
[일반 스크립트의 파서 블로킹 타임라인]

HTML 파싱      ▓▓ (0~100ms)
vendor.js      ░░░░░░ 다운로드(100~700ms) ▓▓ 파싱·컴파일 ▓▓▓ 실행(~900ms)
app.js         (프리로드 스캐너가 미리 받음)  ▓ 파싱 ▓▓ 실행(900~1100ms)
HTML 파싱 재개                                          ▓▓ (1100~1200ms)
hero.jpg                                                  ░░░ 발견·다운로드(1200~1700ms)
                                                                    ↑ LCP 완료 1700ms
```

스크립트가 블로킹하지 않았다면 히어로 이미지는 100ms에 발견됐을 것이다. **1100ms의 지연**이다.

**Performance 탭 확인법**: 페이지를 녹화하고 Main 트랙을 보면 `Parse HTML`과 `Evaluate Script`가 번갈아 나타난다. `Parse HTML`이 중단되고 `Evaluate Script`가 실행되는 지점이 파서 블로킹이다.

### 1.4 `<body>` 끝에 두는 오래된 해법의 한계

가장 오래된 해결책은 스크립트를 `</body>` 직전에 두는 것이다. 파서 블로킹이 FCP·LCP에 영향을 주지 않지만 **스크립트 다운로드 자체가 늦게 시작된다.** HTML 전체를 파싱한 후에야 다운로드가 시작되므로 TTI가 지연되고, 사용자가 버튼을 클릭해도 아무 반응이 없다.

더 나은 해법이 `async`와 `defer`다. `<head>`에 선언하면 **프리로드 스캐너가 즉시 발견해 다운로드를 시작하면서도 HTML 파싱은 계속 진행된다.**

## 2. defer: 순서를 보장하며 파싱 후 실행

### 2.1 정확한 실행 시점

`defer` 스크립트는 세 단계로 처리된다.

1. **발견 및 다운로드 시작**: `<script defer>` 태그를 만나면 즉시 다운로드하되 파싱을 멈추지 않는다
2. **HTML 파싱 계속**: 스크립트는 백그라운드에서 다운로드된다
3. **파싱 완료 후 실행**: `</html>`에 도달하면 다운로드된 `defer` 스크립트를 **HTML 순서대로** 실행한다

3번의 정확한 타이밍이 중요하다.

- **HTML 파싱 완료 후**: `</html>` 태그를 읽고 DOM 트리 구축이 끝난 시점
- **`DOMContentLoaded` 이벤트 발생 전**: 모든 `defer` 스크립트 실행이 완료돼야 `DOMContentLoaded`가 발생한다

```
전체 순서:
1. HTML 파싱 시작
2. <script defer> 발견 → 다운로드 시작 (파싱 계속)
3. HTML 파싱 완료 (</html> 도달)
4. 모든 defer 스크립트 실행 (HTML 순서대로)
5. DOMContentLoaded 이벤트 발생
6. window.onload 이벤트 발생 (이미지 등 모든 리소스 로드 완료 후)
```

**다운로드가 파싱보다 느리면 어떻게 되는가?** HTML 파싱은 완료되지만 브라우저는 다운로드가 끝날 때까지 기다린다. 파싱이 500ms에 끝나도 다운로드가 800ms에 완료되면 300ms를 기다린 뒤 실행하고, `DOMContentLoaded`는 1000ms에 발생한다. **이것이 "파싱 완료 후 실행"의 정확한 의미다.**

> **실무 팁**: `defer`는 HTML 파싱을 블로킹하지 않지만 **`DOMContentLoaded`는 지연시킨다.** Performance 탭에서 `Parse HTML` 완료와 `DOMContentLoaded` 사이에 긴 `Evaluate Script` 구간이 보인다면 무거운 `defer` 스크립트가 원인이다. 가벼운 스크립트(~10ms)는 간격이 거의 안 보이지만, 무거운 스크립트는 1초에 달하는 구간이 명확히 드러난다. **`defer`를 써도 스크립트 실행 시간 자체는 최적화해야 한다.**

### 2.2 여러 개의 defer 스크립트

`defer`의 가장 중요한 특징은 **실행 순서 보장**이다. 다운로드는 병렬로 진행되지만 실행은 반드시 선언 순서대로 이뤄진다.

```html
<head>
  <script defer src="/jquery.js"></script>  <!-- 500ms 다운로드 -->
  <script defer src="/plugin.js"></script>  <!-- 200ms 다운로드 -->
  <script defer src="/app.js"></script>     <!-- 300ms 다운로드 -->
</head>
```

```
다운로드 완료 순서: plugin(200ms) → app(300ms) → jquery(500ms)
실행 순서:          jquery → plugin → app  (HTML 선언 순서)

1. HTML 파싱 완료 후 대기
2. jquery.js 다운로드 완료 대기 (500ms)
3. jquery.js 실행
4. plugin.js 실행 (jQuery에 의존하므로 안전)
5. app.js 실행
6. DOMContentLoaded 발생
```

이 순서 보장이 의존성 체인을 안전하게 처리한다. `async`였다면 `plugin.js`가 `jquery.js`보다 먼저 실행되어 `$ is not defined` 에러가 났을 것이다.

> **핵심 통찰**: 순서 보장에는 대가가 있다. **하나의 스크립트 다운로드가 매우 느리면 뒤의 모든 스크립트 실행이 지연된다.** `jquery.js`가 5초 걸리면 `plugin.js`(200ms)와 `app.js`(300ms)는 다운로드가 끝나도 5초까지 기다린다. 이 경우 느린 스크립트를 분리하거나, 코드 스플리팅으로 청크를 줄이거나, `preload`·103 Early Hints로 다운로드를 최적화한다.

### 2.3 defer를 써야 하는 경우

**첫째, DOM 요소를 참조하는 스크립트.** DOM이 완전히 파싱된 후 실행되므로 `document.querySelector()`를 안전하게 쓸 수 있다.

```html
<head>
  <script defer src="/app.js"></script>
</head>
<body>
  <div id="root"></div>
</body>
```

```ts
// app.js — DOM이 준비돼 있음
const root = document.getElementById('root'); // ✅ 안전
root.innerHTML = '<h1>Hello</h1>';
```

**둘째, 의존성이 있는 여러 스크립트.**

```html
<script defer src="/react.js"></script>
<script defer src="/react-dom.js"></script>
<script defer src="/app.js"></script>
<!-- React → ReactDOM → App 순서 보장 -->
```

**셋째, 애플리케이션 메인 번들.** DOM 준비 후 앱을 초기화해야 하고 여러 청크의 순서를 보장해야 하기 때문이다.

**넷째, `DOMContentLoaded`를 기다리던 스크립트.** `defer`로 바꾸면 이벤트 리스너 자체가 불필요해진다.

```ts
// Before: 일반 스크립트
document.addEventListener('DOMContentLoaded', () => {
  const root = document.getElementById('root');
  root.innerHTML = '<h1>Hello</h1>';
});

// After: defer 스크립트 — 이벤트 리스너 불필요
const root = document.getElementById('root'); // 이미 DOM 준비됨
root.innerHTML = '<h1>Hello</h1>';
```

**defer를 쓰지 말아야 하는 경우**는 ① 다른 스크립트에 의존하지 않는 독립적 스크립트(`async`가 적합), ② **인라인 스크립트**(`defer`는 외부 스크립트에만 작동한다).

## 3. async: 최대한 빨리 비순차 실행

`defer`가 "순서를 지키며 나중에 실행"이라면, `async`는 "순서 상관없이 최대한 빨리 실행"이다.

### 3.1 실행 시점

1. **발견 및 다운로드 시작**: 파싱을 멈추지 않는다
2. **HTML 파싱 계속**
3. **다운로드 완료 즉시 실행**: 현재 진행 중인 HTML 파싱을 일시 중단하고 스크립트를 실행한 뒤 파싱을 재개한다

```html
<head>
  <script async src="/analytics.js"></script>  <!-- 100ms 다운로드 -->
</head>
<body>
  <!-- 여기를 파싱 중일 때 analytics.js 다운로드 완료 -->
  <div>Content</div>
  <!-- ⚠ 파싱 멈춤, analytics.js 실행 → 끝나면 파싱 재개 -->
  <div>More content</div>
</body>
```

다운로드가 파싱보다 오래 걸리면 파싱이 먼저 완료되고, **`DOMContentLoaded`는 `async` 스크립트를 기다리지 않고 바로 발생한다.** 스크립트는 나중에 다운로드가 끝나면 그때 실행된다.

> **핵심 통찰**: 두 속성의 결정적 차이는 이것이다.<br>**`defer`**: HTML 파싱 완료 후, `DOMContentLoaded` **발생 전** 실행<br>**`async`**: 다운로드 완료 즉시 실행, `DOMContentLoaded`와 **무관**

이 차이 때문에 `async` 스크립트는 DOM 조작 코드에 적합하지 않다. 파싱 중간에 실행될 수 있어 필요한 DOM 요소가 아직 없을 수 있다.

### 3.2 여러 개의 async 스크립트

**실행 순서가 전혀 보장되지 않는다.** HTML 선언 순서는 무시되고 다운로드 완료 순서대로 실행된다.

```html
<script async src="/script-a.js"></script>  <!-- 500ms -->
<script async src="/script-b.js"></script>  <!-- 200ms -->
<script async src="/script-c.js"></script>  <!-- 100ms -->
<!-- 실행 순서: C(100ms) → B(200ms) → A(500ms) -->
```

네트워크 상황·파일 크기·서버 응답 속도에 따라 **매번 순서가 달라진다.** 의존성이 있으면 런타임 에러가 난다.

```ts
// script-a.js (500ms)
window.myLibrary = { init: function () { /* ... */ } };

// script-b.js (200ms, 먼저 실행됨)
window.myLibrary.init();
// ❌ TypeError: Cannot read property 'init' of undefined
```

### 3.3 async를 써야 하는 경우

**오직 독립적인 스크립트에만** 쓴다. 다른 코드에 의존하지 않고, 다른 코드가 의존하지도 않는 경우다.

1. **분석·추적 스크립트**: 구글 애널리틱스, 믹스패널. 최대한 빨리 로드되어 데이터 수집을 시작하는 것이 목표다.
2. **독립적인 위젯**: 채팅 위젯(Intercom, Zendesk), 소셜 버튼, 댓글 시스템(Disqus)
3. **광고 스크립트**: 구글 애드센스 등. 메인 콘텐츠 로딩을 블로킹하면 안 된다.
4. **에러 추적 스크립트**: Sentry, Bugsnag. 빨리 로드되어 에러를 캡처해야 한다.

```html
<!-- ✅ 각 스크립트가 독립적이므로 순서 무관 -->
<script async src="/google-analytics.js"></script>
<script async src="/hotjar.js"></script>
<script async src="/sentry.js"></script>
```

> **실무 팁**: 분석 도구의 인라인 초기화 스니펫(`gtag('js', new Date())` 같은 코드)은 어차피 즉시 실행되므로 `async`나 `defer`를 붙여도 동작이 달라지지 않는다. **외부 로더만 `async`로 선언하고 인라인 코드는 일반 `<script>`로 둔다.**

## 4. async와 defer의 선택 기준

```
DOM 요소를 참조하는가?
  ├ 예 ──▶ defer 사용
  └ 아니오
     │
     다른 스크립트에 의존하는가?
       ├ 예 ──▶ defer 사용 (순서 보장 필수)
       └ 아니오
          │
          실행 순서가 중요한가?
            ├ 예 ──▶ defer 사용
            └ 아니오
               │
               렌더링 성능이 최우선인가?
                 ├ 예 ──▶ defer 고려 (파싱 완료 후 실행)
                 └ 아니오 ──▶ async 사용 (최대한 빨리 실행)
```

| 질문 | 답변 | 선택 |
|---|---|---|
| DOM 요소를 참조하는가? | 예 | `defer` |
| 다른 스크립트에 의존하는가? | 예 | `defer` |
| 실행 순서가 중요한가? | 예 | `defer` |
| 독립적이고 빨리 실행돼야 하는가? | 예 | `async` (단, 성능 영향 측정) |
| 렌더링 성능이 최우선인가? | 예 | `defer` |

> **핵심 통찰**: **의심스러우면 `defer`를 선택한다.** 잘못된 `async` 사용은 런타임 에러를 일으키지만, `defer`를 잘못 쓰면 최악의 경우라도 실행이 약간 늦어지는 정도에 그친다.

### 4.1 분석·텔레메트리 스크립트의 선택 기준

이 경우는 단순한 "빠른 데이터 수집 vs 성능 최적화" 트레이드오프가 아니다.

**① 기본 전략: `async` 우선, 성능 이슈 발견 시 `defer` 전환**

대부분의 분석 도구는 공식 문서에서 `async`를 권장한다. 빨리 실행될수록 초기 페이지뷰·인터랙션·이탈률을 정확히 추적할 수 있기 때문이다. `defer`는 사용자가 빠르게 이탈하면 데이터를 놓칠 수 있다.

하지만 `async`는 파싱 중간에 실행되어 FCP/LCP를 지연시킨다. 구글 애널리틱스 `gtag.js`(약 30KB gzip)는 실행에 평균 20~30ms가 걸리고, 히어로 이미지가 아직 파싱되지 않았다면 이 지연이 LCP에 직접 영향을 준다.

**② 핵심 웹 지표 점수에 따른 결정**

- **LCP 2.3~2.5초**: Good(2.5초) 기준에 아슬아슬하다. `defer` 전환으로 50~100ms 절약 가능
- **FCP 1.6~1.8초**: Good(1.8초) 기준에 근접. 파싱 블로킹 제거로 개선 가능
- **LCP < 2.0초, FCP < 1.5초**: 여유가 있으므로 `async`를 유지해 데이터 수집 품질을 우선

**③ A/B 테스트로 실제 영향 측정**

```ts
// Step 1: 현재 상태 측정
window.addEventListener('load', () => {
  const perfData = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
  const paintEntries = performance.getEntriesByName('first-contentful-paint');
  const fcp = paintEntries.length > 0 ? paintEntries[0].startTime : null;

  sendMetric({
    variant: 'async',
    fcp,
    domContentLoaded: perfData.domContentLoadedEventEnd,
    timestamp: Date.now(),
  });
});
```

```html
<!-- Step 2: 사용자의 50%에게 defer 버전 제공 -->
<script>
  const useDefer = Math.random() < 0.5;
  const script = document.createElement('script');
  script.src = 'https://www.google-analytics.com/analytics.js';
  if (useDefer) {
    script.defer = true;
    window.analyticsVariant = 'defer';
  } else {
    script.async = true;
    window.analyticsVariant = 'async';
  }
  document.head.appendChild(script);
</script>
```

**Step 3: 결과 판단 기준**

- FCP 차이 **50ms 이상** → `defer` 전환 고려
- FCP 차이 **20~50ms** → 데이터 수집 품질 영향을 평가 후 결정
- FCP 차이 **20ms 이하** → `async` 유지

> 실제 사례로 한 이커머스 사이트는 구글 애널리틱스를 `defer`로 전환한 후 FCP가 평균 68ms, LCP가 45ms 개선됐다. 다만 이탈률 추적 정확도가 2% 감소했다(빠르게 이탈한 사용자의 데이터 누락). 이 사이트는 핵심 웹 지표 점수를 더 중요하다고 판단해 `defer`를 채택했다.

**④ 스크립트 크기에 따른 기준**

| 크기(gzip) | 예상 실행 시간 | 권장 전략 | 예시 |
|---|---|---|---|
| < 20KB | 10~20ms | `async`(영향 미미) | 구글 애널리틱스 gtag.js(17KB), Hotjar(15KB) |
| 20~50KB | 20~40ms | `async` 기본, 성능 이슈 시 `defer` | 믹스패널(32KB), 세그먼트(28KB) |
| 50~100KB | 40~80ms | `defer` 우선 고려 | 복합 텔레메트리 번들(75KB) |
| > 100KB | 80ms+ | `defer` 필수 또는 지연 로딩 | 무거운 APM 도구(120KB+) |

매우 무거운 APM(200KB+)은 유휴 시간에 로드한다.

```ts
if ('requestIdleCallback' in window) {
  requestIdleCallback(() => {
    const script = document.createElement('script');
    script.src = '/apm-bundle.js';
    document.head.appendChild(script);
  });
} else {
  window.addEventListener('load', () => {
    setTimeout(() => {
      const script = document.createElement('script');
      script.src = '/apm-bundle.js';
      document.head.appendChild(script);
    }, 1000);
  });
}
```

**⑤ 복합적 고려사항**

- **페이지 복잡도**: 간단한 랜딩 페이지(HTML < 30KB)는 파싱이 금방 끝나므로 `async`의 블로킹 영향이 상대적으로 크다 → `defer` 권장. 복잡한 SPA(HTML > 100KB)는 파싱 시간이 길어 상대적 영향이 작다 → `async` 무방.
- **비즈니스 우선순위**: 전환율 추적이 중요한 이커머스는 `async`. 광고 수익이 핵심인 미디어·콘텐츠 사이트는 핵심 웹 지표가 광고 단가에 영향을 주므로 `defer`.

### 4.2 전체 비교

| 특징 | `async` | `defer` |
|---|---|---|
| 실행 시점 | 다운로드 완료 즉시 | HTML 파싱 완료 후 |
| 실행 순서 | 보장 안 됨(다운로드 순) | 보장됨(HTML 순서대로) |
| HTML 파싱 중단 | 가능(실행 시 파싱 중단) | 없음 |
| `DOMContentLoaded` | 대기 안 함 | 실행 완료 후 발생 |
| DOM 조작 | 위험(DOM 미준비 가능) | 안전(DOM 준비됨) |
| 의존성 있는 코드 | 부적합 | 적합 |
| 주요 사용 사례 | 분석, 광고, 위젯 | 앱 코드, 라이브러리 |
| 인라인 스크립트 | 동작 안 함 | 동작 안 함 |
| 모듈 스크립트 기본 | `async` 추가 필요 | 기본 동작(`type="module"`) |
| 브라우저 지원 | IE10+(모든 모던 브라우저) | IE10+(모든 모던 브라우저) |

실무에서 가장 흔한 패턴은 다음과 같다.

```html
<head>
  <!-- 메인 애플리케이션: defer (순서 보장) -->
  <script defer src="/vendor.js"></script>
  <script defer src="/app.js"></script>

  <!-- 분석 및 추적: async (최대한 빨리) -->
  <script async src="/analytics.js"></script>
  <script async src="/sentry.js"></script>

  <!-- 광고: async (독립적) -->
  <script async src="/ads.js"></script>
</head>
```

## 5. 모듈 스크립트와 type="module"

### 5.1 모듈 스크립트의 다섯 가지 차이

**① 기본적으로 `defer` 동작**

명시적으로 `defer`를 붙이지 않아도 자동으로 `defer`처럼 동작한다.

```html
<!-- 실행 타이밍이 동일 -->
<script type="module" src="/app.js"></script>
<script defer src="/app.js"></script>
```

**② 자동 엄격 모드**: `"use strict"` 선언이 필요 없다.

**③ 스코프 격리**: 모듈 최상위 변수는 전역 스코프에 추가되지 않는다. 각 모듈이 자신만의 스코프를 가지므로 전역 네임스페이스 오염을 방지한다.

**④ `import` 구문 지원**: 브라우저가 `import`를 만나면 자동으로 의존성 모듈을 다운로드·파싱하고, 모든 의존성이 해결된 후에야 모듈을 실행한다.

**⑤ 중복 실행 방지**: 같은 URL의 모듈은 여러 번 선언돼도 한 번만 실행된다(일반 스크립트는 각각 실행).

```html
<script type="module" src="/utils.js"></script>
<script type="module" src="/utils.js"></script>
<!-- utils.js는 한 번만 실행됨 -->
```

### 5.2 async 모듈 스크립트

`type="module"`에 `async`를 추가하면 일반 `async`처럼 다운로드 완료 즉시 실행되고 `DOMContentLoaded`를 대기하지 않는다.

| 특징 | `<script async>` | `<script type="module" async>` |
|---|---|---|
| 실행 시점 | 다운로드 완료 즉시 | 다운로드 완료 즉시 |
| `import` 지원 | ✗ | ✓ |
| 엄격 모드 | 명시 필요 | 자동 적용 |
| 스코프 | 전역 | 모듈 스코프 |
| 의존성 자동 로드 | ✗ | ✓ |
| 중복 실행 방지 | ✗ (매번 실행) | ✓ (한 번만 실행) |

`async` 모듈도 일반 `async`와 같은 문제를 갖는다. DOM이 준비되지 않았을 수 있고 순서가 보장되지 않는다. **DOM을 조작하는 모듈에서는 `async`를 제거해 기본 `defer` 동작을 쓴다.**

### 5.3 모듈과 일반 스크립트 혼용

네 가지 스크립트 타입이 서로 다른 규칙으로 실행된다.

1. **일반 `<script>`**: HTML 순서대로 즉시 실행(파싱 블로킹)
2. **`<script defer>`**: HTML 파싱 완료 후, HTML 순서대로 실행
3. **`<script type="module">`**: HTML 파싱 완료 후, HTML 순서대로 실행 — **`defer`와 같은 큐에서 실행**
4. **`<script type="module" async>`**: 다운로드 완료 즉시 실행

> **핵심 통찰**: `<script defer>`와 `<script type="module">`은 **같은 defer 스크립트 큐**에 추가되어 HTML 선언 순서대로 실행된다. 두 타입을 섞어 써도 선언 순서가 곧 실행 순서다.

```html
<script>console.log('1. Inline 즉시 실행');</script>
<script src="/regular.js"></script>              <!-- 2. 파싱 블로킹 -->
<script defer src="/defer-a.js"></script>        <!-- defer 큐 순서 1 -->
<script type="module" src="/module-b.js"></script><!-- defer 큐 순서 2 -->
<script defer src="/defer-c.js"></script>        <!-- defer 큐 순서 3 -->
<script type="module" async src="/module-async.js"></script>  <!-- 다운로드 완료 즉시 -->
```

```
실행 순서:
1. 인라인 스크립트
2. regular.js (파싱 블로킹)
3. (HTML 파싱 완료)
4. module-async.js (다운로드 완료 시점에 따라 3번과 5~7번 사이 어디든)
5. defer-a.js
6. module-b.js
7. defer-c.js
8. DOMContentLoaded
```

**전역 변수 의존성 문제**도 주의한다. `window`에 설정된 전역 변수는 모듈에서 접근할 수 있지만, **모듈 내에서 선언한 변수는 전역에 노출되지 않는다.** 일반 스크립트에 값을 제공하려면 `window`에 명시적으로 할당해야 하는데, 이는 모듈의 스코프 격리 장점을 포기하는 것이므로 권장하지 않는다.

**혼용 시 원칙**

1. **일관성 유지**: 가능하면 전부 모듈로 작성하거나 전부 일반 스크립트로 작성한다
2. **레거시 지원**: `<script nomodule>`로 모듈 미지원 브라우저 폴백을 제공한다
3. **전역 의존성 최소화**
4. **번들러 사용**: 비트·웹팩이 이 문제를 자동 처리한다

```html
<!-- 모던 브라우저: 모듈 사용 -->
<script type="module" src="/app-modern.js"></script>
<!-- 레거시 브라우저: 번들된 일반 스크립트 -->
<script nomodule src="/app-legacy.js"></script>
```

## 6. 동적 스크립트 로딩

### 6.1 기본 동작은 async

자바스크립트로 생성해 DOM에 추가한 스크립트는 **기본적으로 `async`처럼 동작**한다. 다운로드 완료 즉시 실행되고 순서가 보장되지 않는다.

```ts
// ⚠ async처럼 동작 — 다운로드 완료 즉시 실행
const script = document.createElement('script');
script.src = '/analytics.js';
document.head.appendChild(script);
```

```ts
// ❌ 순서가 보장되지 않음
const lib = document.createElement('script');
lib.src = '/library.js';  // 100KB
document.head.appendChild(lib);

const app = document.createElement('script');
app.src = '/app.js';      // 10KB
document.head.appendChild(app);
// app.js가 먼저 다운로드 완료되면 먼저 실행 → library.js에 의존하면 에러
```

동적 삽입의 기본 동작은 **독립적인 스크립트를 조건부로 로드할 때** 적합하다. '독립적'이란 ① 다른 스크립트의 전역 변수·함수에 의존하지 않고 자체 완결적이며, ② 다른 스크립트가 그 실행 결과를 기다리지 않고, ③ 언제 실행되든 앱 로직에 영향이 없는 경우다. 구글 애널리틱스, Sentry, 광고 스크립트가 대표적이다.

### 6.2 순서 보장이 필요하면 async = false

```ts
function loadScriptsInOrder(): void {
  const lib = document.createElement('script');
  lib.src = '/library.js';
  lib.async = false;  // 순서 보장
  document.head.appendChild(lib);

  const plugin = document.createElement('script');
  plugin.src = '/plugin.js';
  plugin.async = false;
  document.head.appendChild(plugin);

  const app = document.createElement('script');
  app.src = '/app.js';
  app.async = false;
  document.head.appendChild(app);
  // library.js → plugin.js → app.js 순서 보장
}
```

> **핵심 통찰**: `async = false`는 "실행 순서를 보장한다"는 점에서 `<script defer>`를 순서대로 작성한 것과 비슷하다. **다만 `defer`는 DOM 파싱이 끝난 뒤에만 실행되는 반면, 동적 스크립트는 다운로드가 끝나는 즉시 실행되어 파서를 다시 중단시킬 수 있다.** DOM 준비 후에 실행돼야 한다면 `DOMContentLoaded` 이후에 삽입하거나 아예 정적 `<script defer>`/`type="module"`로 제공한다.

또한 `async = false`는 **동적으로 생성한 스크립트에만 효과가 있다.** HTML에 선언된 `<script src="/app.js" async="false">`는 의미가 없다. `async`는 boolean 속성이라 존재하기만 하면 `true`다.

### 6.3 재사용 가능한 헬퍼

결제 버튼 클릭 시 PG 라이브러리 로드, A/B 테스트 그룹별 기능 추가, 관리자 모드 디버깅 도구 로드처럼 동적 로딩이 필요한 곳이 많다면 헬퍼로 묶는 것이 좋다.

```ts
function loadScriptsSequentially(urls: string[]): Promise<void> {
  return new Promise((resolve, reject) => {
    let loadedCount = 0;

    urls.forEach((url) => {
      const script = document.createElement('script');
      script.src = url;
      script.async = false; // 순서 보장
      script.onload = () => {
        loadedCount++;
        if (loadedCount === urls.length) {
          resolve();
        }
      };
      script.onerror = () => reject(new Error(`Failed to load ${url}`));
      document.head.appendChild(script);
    });
  });
}

loadScriptsSequentially(['/vendor/react.js', '/vendor/react-dom.js', '/app.js'])
  .then(() => {
    console.log('모든 스크립트 로드 완료');
  })
  .catch((err) => console.error(err));
```

## 7. 흔한 실수와 안티패턴

### 7.1 body 끝에 스크립트 두기

2000년대 중반부터 널리 퍼진 레거시 패턴이다. 여전히 동작하지만 성능 관점에서 세 가지 문제가 있다.

1. **다운로드 시작이 늦다**: 프리로드 스캐너가 `<head>`를 스캔할 때 발견하지 못하므로 `<body>` 끝까지 파싱한 후에야 다운로드가 시작된다
2. **병렬 처리 기회 손실**: HTML 파싱과 스크립트 다운로드를 병렬로 처리할 수 없다
3. **FCP 지연 가능**: 스크립트가 필요한 컴포넌트를 렌더링한다면 다운로드가 늦어 FCP가 지연된다

200KB `app.js`를 4G(평균 10Mbps)에서 로드하는 데 200ms, HTML 파싱에 150ms가 걸린다고 하면,

- **body 끝 패턴**: HTML 파싱 150ms + 다운로드 대기 + 다운로드 200ms = **최소 350ms**
- **head + defer 패턴**: `max(파싱 150ms, 다운로드 200ms)` = **200ms**

**150ms 차이**가 FCP와 TTI에 직접 영향을 준다.

```html
<!-- ✅ 모던 패턴 -->
<head>
  <title>My App</title>
  <link rel="stylesheet" href="/styles.css" />
  <script defer src="/vendor.js"></script>
  <script defer src="/app.js"></script>
</head>
<body>
  <div id="app"></div>
</body>
```

`defer`는 body 끝 배치와 **동일한 안전성**(DOM 준비 후 실행)을 보장하면서 **실행 순서까지 보장**하고 **다운로드는 병렬로** 처리한다.

### 7.2 인라인 스크립트에 defer/async 사용

```html
<!-- ❌ 동작하지 않음 -->
<script defer>
  console.log('이 코드는 defer가 적용되지 않음');
  document.querySelector('#app').textContent = 'Hello'; // null 에러
</script>
```

HTML 명세는 **"Both attributes have no effect for inline scripts"**라고 명확히 정의한다. `defer`와 `async`의 핵심은 "다운로드와 파싱을 분리하는 것"인데, 인라인 스크립트는 별도 다운로드 과정이 없으므로 의미가 없다.

```html
<head>
  <script defer>
    console.log('1. inline script');
    console.log(document.body); // null — body가 아직 없음
  </script>
  <script defer src="/external.js"></script>
</head>
<body>
  <div id="app">Hello</div>
</body>
```

```
실행 결과:
1. inline script
null
2. external script
<body>...</body>
```

**해결 방법 세 가지**

1. **외부 파일로 분리하고 `defer` 사용** (가장 권장)
2. **`DOMContentLoaded` 이벤트 사용**: 단, 스크립트 자체는 즉시 실행되어 파싱을 블로킹한다
3. **`type="module"` 사용**: 인라인 모듈 스크립트는 `defer`처럼 동작한다

```html
<!-- ✅ 인라인 모듈은 defer 동작 -->
<script type="module">
  document.querySelector('#app').textContent = 'Hello';
</script>
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|---|---|---|
| `<head>`의 외부 스크립트에 속성 없음 | 다운로드+파싱+실행 동안 HTML 파싱이 완전히 멈춤 | `defer` 또는 `async` 추가 |
| `</body>` 직전에 스크립트 배치 | 프리로드 스캐너가 늦게 발견해 다운로드 시작이 지연됨 | `<head>` + `defer`로 이동 |
| 인라인 스크립트에 `defer`/`async` | HTML 명세상 아무 효과 없음. 즉시 실행되어 `document.body`가 `null` | 외부 파일 분리 또는 `type="module"` |
| 의존성 있는 스크립트에 `async` | 다운로드 순서대로 실행되어 `$ is not defined` 같은 런타임 에러 | `defer`로 순서 보장 |
| DOM 조작 스크립트에 `async` | 파싱 중간에 실행되어 `getElementById`가 `null` 반환 | `defer` 사용 |
| 무거운 분석 스크립트(>100KB)에 `async` | 파싱 중간 실행으로 LCP가 크게 저하됨 | `defer` 필수 또는 `requestIdleCallback` 지연 로딩 |
| 동적 삽입 스크립트의 순서를 기대 | 기본이 `async` 동작이라 순서가 보장되지 않음 | `script.async = false` 설정 |
| HTML에 `async="false"` 작성 | `async`는 boolean 속성이라 존재하면 `true` | `defer`를 쓰거나 `async`를 아예 생략 |
| `async` 모듈로 DOM 조작 | 모듈이어도 `async`면 DOM 미준비 상태에서 실행 | `async` 제거(기본 `defer` 동작) |
| 무거운 `defer` 스크립트 방치 | 파싱은 안 막지만 `DOMContentLoaded`가 크게 지연됨 | 코드 스플리팅·동적 `import()`로 실행 시간 단축 |
| 모듈 내부 변수를 일반 스크립트에서 접근 | 모듈은 스코프가 격리되어 전역에 노출되지 않음 | 전체를 모듈로 통일(`window` 할당은 비권장) |

## 측정과 검증

**Performance 탭**

- Main 트랙에서 `Parse HTML`과 `Evaluate Script`가 번갈아 나타나는 지점이 파서 블로킹이다
- `DOMContentLoaded` 마커 직전에 긴 `Evaluate Script` 구간이 있다면 무거운 `defer` 스크립트가 원인이다
- 여러 `defer` 스크립트가 HTML 선언 순서대로 실행되는지 확인할 수 있다

**Network 탭**

`defer` 스크립트가 병렬로 다운로드되는지 확인한다. Performance 탭에서는 순차 실행되지만 Network 탭에서는 동시에 내려와야 정상이다.

**라이트하우스**

- "Reduce JavaScript execution time" — 스크립트 실행 시간 최적화 효과 측정
- "Eliminate render-blocking resources" — 파서·렌더 블로킹 리소스 진단

**A/B 테스트 + `web-vitals`**

분석 스크립트의 `async`/`defer` 선택은 실사용자 환경에서 FCP·LCP를 비교해 결정하는 것이 가장 정확하다.

## 체크리스트

**스크립트 기본 원칙**

- [ ] `<head>`의 모든 외부 스크립트에 `defer` 또는 `async`를 추가했는가
- [ ] `<body>` 끝에 있는 스크립트를 `<head>`로 이동하고 `defer`를 추가했는가
- [ ] 인라인 스크립트는 필요한 경우에만 사용하고 최소화했는가

**defer 사용**

- [ ] DOM을 조작하는 스크립트에 `defer`를 사용했는가
- [ ] 의존성이 있는 라이브러리들을 `defer`로 순서 보장했는가
- [ ] 애플리케이션 메인 번들에 `defer`를 사용했는가

**async 사용**

- [ ] 분석 스크립트(구글 애널리틱스, 믹스패널 등)에 `async`를 사용했는가
- [ ] 독립적인 서드파티 위젯에 `async`를 사용했는가
- [ ] 다른 코드에 의존하지 않는 유틸리티 스크립트에 `async`를 사용했는가
- [ ] 무거운 분석 스크립트(>50KB)는 `defer` 전환을 검토했는가

**모듈 스크립트**

- [ ] ESModule에는 `type="module"`을 명시했는가
- [ ] 모듈 스크립트가 기본적으로 `defer` 동작을 한다는 것을 인지했는가
- [ ] 모듈과 일반 스크립트를 혼용할 때 실행 순서를 고려했는가

**서드파티 스크립트**

- [ ] 서드파티 스크립트를 동적 삽입 대신 HTML에 선언했는가
- [ ] 광고나 채팅 위젯 같은 무거운 스크립트를 지연 로딩했는가
- [ ] 사용자 인터랙션 후 로드할 수 있는 스크립트를 식별했는가

## 요약

- 일반 `<script>`는 **다운로드 → 파싱·컴파일 → 실행** 세 단계가 끝날 때까지 HTML 파싱을 완전히 멈춘다. 자바스크립트가 동기적이고 DOM을 조작할 수 있기 때문이다.
- 스크립트는 파서 블로킹이면서 렌더 블로킹이다. 게다가 **CSSOM이 준비될 때까지 실행이 지연된다**(스타일을 읽을 수 있으므로).
- HTTP Archive 2024 기준 페이지당 22~23개 자바스크립트 파일이 로드된다. 모두 블로킹이면 2.2초의 지연이 발생한다.
- **`defer`**: 다운로드는 즉시 시작, 실행은 HTML 파싱 완료 후 **선언 순서대로**, `DOMContentLoaded` **직전**에. 순서 보장 대가로 **가장 느린 스크립트가 뒤의 모든 실행을 지연**시킨다.
- **`async`**: 다운로드 완료 즉시 실행. 파싱 중간에도 실행되어 파싱을 중단시킬 수 있고, **순서가 전혀 보장되지 않으며**, `DOMContentLoaded`를 기다리지 않는다.
- 선택 기준은 명확하다. **DOM 참조 / 다른 스크립트 의존 / 순서 중요 → `defer`.** 독립적이고 빨리 실행돼야 함 → `async`. **의심스러우면 `defer`**(잘못된 `async`는 런타임 에러, 잘못된 `defer`는 약간의 지연일 뿐).
- 분석 스크립트는 기본 `async`, 핵심 웹 지표가 기준선에 근접하면 `defer` 전환을 검토한다. 크기 기준으로 20KB 미만은 `async`, 100KB 초과는 `defer` 필수다.
- `type="module"`은 **기본적으로 `defer`처럼 동작**하며 엄격 모드·스코프 격리·의존성 자동 로드·중복 실행 방지가 추가된다. `<script defer>`와 **같은 큐**에서 선언 순서대로 실행된다.
- 동적 삽입 스크립트는 **기본이 `async` 동작**이다. 순서가 필요하면 `script.async = false`를 설정하되, `defer`와 달리 다운로드 완료 즉시 실행되어 파서를 중단시킬 수 있다는 차이를 안다.
- **인라인 스크립트에는 `defer`·`async`가 전혀 동작하지 않는다.** HTML 명세에 명시돼 있다. 외부 파일 분리 또는 `type="module"`로 해결한다.
- `<body>` 끝 배치는 레거시 패턴이다. **`<head>` + `defer`가 동일한 안전성에 병렬 다운로드까지 얻는다.**

## 다른 챕터와의 관계

- **Ch4(리소스 우선순위)**: 스크립트 위치·속성에 따라 우선순위가 High~Low로 달라진다는 규칙을 다뤘다. 이 장은 그 속성들의 실행 타이밍을 정면으로 다룬다.
- **Ch5(프리로드 스캐너)**: "HTML에 선언하되 파서를 블로킹하지 않게 하라"는 결론의 구체적 수단이 `async`·`defer`다. `<body>` 끝 배치가 나쁜 이유도 프리로드 스캐너 관점에서 설명된다.
- **Ch7(렌더링 블로킹 리소스)**: 스크립트뿐 아니라 CSS의 렌더 블로킹을 줄이는 방법을 다룬다. 크리티컬 CSS 인라인화와 미디어 쿼리 조건부 로딩이 핵심이다.
- **Ch10(코드 스플리팅)**: 무거운 `defer` 스크립트가 `DOMContentLoaded`를 지연시키는 문제의 근본 해법이다. 동적 `import()`로 초기 실행 시간을 줄인다.
- **Ch18(자바스크립트 실행 최적화)**: `requestIdleCallback`으로 무거운 스크립트를 유휴 시간에 미루는 기법을 본격적으로 다룬다.
- **Ch23(서드파티 코드 통제)**: 분석·광고·위젯 스크립트의 로딩 전략을 파사드 패턴·샌드박싱까지 확장한다.
