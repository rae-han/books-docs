# Chapter 7: 렌더링 블로킹 리소스를 줄이는 것이 진짜 '빠름'의 시작이다

## 핵심 질문

HTML은 이미 도착했는데 화면은 왜 여전히 비어 있는가? 10KB짜리 CSS 하나가 1MB짜리 HTML 전체의 표시를 막는 이유는 무엇이며, 그 블로킹을 어디까지 줄일 수 있는가?

## 1. CSS와 자바스크립트의 렌더 블로킹

### 1.1 CSS는 왜 렌더링을 블로킹하는가

CSS는 태생적으로 렌더 블로킹 리소스다. 브라우저는 완전한 CSSOM을 구성하기 전까지 화면에 아무것도 그리지 않는다. 이유는 간단하다. CSS가 모두 로드되기 전에 화면을 그리면 사용자는 스타일이 적용되지 않은 날것의 HTML을 보게 된다. 검은 글씨에 파란 링크만 있는 투박한 화면이 잠깐 뜨고 이후 디자인이 갑자기 바뀌는 현상 — **FOUC(*Flash of Unstyled Content*)**다. 브라우저는 이를 방지하려고 CSSOM 구성이 완료될 때까지 렌더링을 **의도적으로** 지연시킨다.

```html
<head>
  <link rel="stylesheet" href="/styles.css" />
  <!-- ⚠ 이 CSS가 다운로드되고 파싱될 때까지 렌더링 블로킹 -->
</head>
<body>
  <h1>환영합니다</h1>
  <p>본문 내용...</p>
</body>
```

`styles.css`가 600KB이고 Slow 4G(1.44Mbps)에서 로드된다면 약 3.3초가 걸린다. **HTML 파싱이 1초 만에 끝났어도 사용자는 3.3초 동안 빈 화면만 본다.** HTML이 1KB든 1MB든 상관없다.

> **핵심 통찰**: `<head>`의 모든 `<link rel="stylesheet">`는 **위치와 상관없이** 기본적으로 렌더 블로킹이다. `media` 속성이나 다른 조건을 명시하지 않는 한 예외가 없다. 100KB 메인 스타일과 50KB 프린트 전용 스타일을 함께 넣으면 **화면에 전혀 필요 없는 프린트 CSS까지 포함해 150KB가 모두 로드될 때까지** 브라우저는 기다린다.

### 1.2 CSS와 자바스크립트의 연쇄 블로킹

`async`·`defer` 없는 동기 스크립트는 HTML 파싱을 중단시킨다(Ch6 참조). 여기서 중요한 것은 **CSS와 자바스크립트가 서로 영향을 미친다**는 점이다.

자바스크립트는 `getComputedStyle()` 같은 API로 스타일 정보를 읽을 수 있으므로 브라우저는 **CSSOM이 완성될 때까지 스크립트 실행을 지연시킨다.**

```html
<head>
  <link rel="stylesheet" href="/styles.css" />  <!-- 2초 소요 -->
  <script src="/app.js"></script>               <!-- 1초 소요 -->
</head>
```

CSS와 스크립트가 병렬로 다운로드되지만 **스크립트는 CSS 파싱이 끝날 때까지 실행되지 않는다.** 결과적으로 CSS 2초 + 스크립트 실행 시간만큼 렌더링이 지연된다. 이것이 렌더 블로킹 리소스가 누적되면 FCP가 급격히 늦어지는 이유다.

### 1.3 크리티컬 렌더링 패스

```
HTML 수신
  ↓
HTML 파싱 시작
  ├─ 동기 JS 발견? ──YES──▶ JS 다운로드 → CSSOM 완료? ──NO──▶ CSSOM 대기
  │                                        └──YES──▶ JS 실행 → HTML 파싱 재개
  │
  └─ CSS 발견? ──YES──▶ CSS 다운로드 & 파싱 → CSSOM 생성
  ↓
DOM 생성 + CSSOM 생성
  ↓
렌더 트리 생성 → 레이아웃 계산 → 페인트 → 화면에 표시
```

1. **HTML 파싱 → DOM 트리 구성**
2. **CSS 파싱 → CSSOM 트리 구성**
3. **DOM + CSSOM → 렌더 트리 생성**(실제로 화면에 보이는 요소만)
4. **레이아웃 계산**(각 요소의 정확한 위치와 크기)
5. **페인트**(픽셀을 화면에 그림)

**CSS는 2·3번 단계를, 동기 자바스크립트는 1번 단계를 블로킹한다.** 따라서 렌더링 블로킹 리소스를 줄이는 것이 CRP를 최적화하는 가장 직접적인 방법이다.

> **핵심 통찰**: 이 장 전체의 메시지는 하나다. **초기 화면을 그리는 데 꼭 필요한 리소스만 동기적으로 로드하고, 나머지는 비동기로 처리하거나 지연시킨다.**

## 2. 크리티컬 CSS 추출과 인라인화

### 2.1 크리티컬 CSS란

크리티컬 CSS는 **첫 화면에 보이는 콘텐츠(Above-the-fold)를 렌더링하는 데 필요한 최소한의 CSS**다. 사용자가 페이지를 열었을 때 브라우저는 스크롤 없이 보이는 영역만 우선 렌더링하면 되고, 나머지는 나중에 그려도 사용자는 인지하지 못한다.

```html
<!-- ❌ 모든 CSS를 동기 로드 -->
<head>
  <link rel="stylesheet" href="/styles.css" />  <!-- 200KB, 모두 렌더 블로킹 -->
</head>

<!-- ✅ 크리티컬 CSS 인라인 + 나머지 비동기 -->
<head>
  <style>
    /* 크리티컬 CSS: 14KB 이하 */
    body { margin: 0; font-family: system-ui; }
    .header { background: #fff; padding: 1rem; }
    .hero { min-height: 500px; }
  </style>

  <link rel="preload" href="/styles.css" as="style"
        onload="this.onload=null;this.rel='stylesheet'" />
  <noscript><link rel="stylesheet" href="/styles.css" /></noscript>
</head>
```

인라인 `<style>`은 HTML과 함께 파싱되므로 **추가 네트워크 요청이 없다.** 나머지 CSS는 `preload` + `onload` 핸들러로 비동기 로드되고, `<noscript>`는 자바스크립트 비활성화 환경의 폴백이다.

**핵심 이점은 네트워크 왕복 시간(RTT) 제거다.**

```
[일반 CSS 로딩]
1. HTML 다운로드 (1 RTT)
2. HTML 파싱 중 <link rel="stylesheet"> 발견
3. CSS 다운로드 요청 (1 RTT)
4. CSS 다운로드 완료 후 CSSOM 구성
5. 렌더링 시작
→ 총 2 RTT. Slow 4G에서 RTT 400ms면 CSS만으로 800ms

[크리티컬 CSS 인라인]
HTML과 함께 도착 → 추가 RTT 없음 → FCP가 최소 400ms 빨라짐
```

### 2.2 TCP 초기 혼잡 윈도우와 14,600바이트

크리티컬 CSS 최적화에서 항상 등장하는 숫자가 **14,600바이트(약 14KB)**다. 임의로 정한 값이 아니라 TCP 프로토콜의 동작에서 비롯된다.

TCP는 연결 직후 네트워크 상황(대역폭·지연·혼잡도)을 전혀 모른다. 처음부터 대량으로 전송하면 중간 라우터 버퍼가 넘쳐 패킷 손실이 발생한다. 이를 막기 위해 **초기 혼잡 윈도우(*Initial Congestion Window*, IW)**가 ACK를 받기 전까지 전송할 수 있는 최대 데이터 양을 제한한다.

과거 IW는 2~4 패킷이었지만 2011년 구글 제안으로 2013년 RFC 6928로 표준화되며 **10 패킷**으로 증가했다. 대부분의 현대 OS·서버(Linux 3.0+, Windows Server 2008+)가 IW 10을 기본값으로 쓴다.

```
TCP/IP 표준 MTU: 1500바이트
  − IP 헤더 20바이트
  − TCP 헤더 20바이트
  = 실제 데이터 공간 1460바이트

10 패킷 × 1460바이트 = 14,600바이트 (약 14KB)
```

```
[14,600바이트 이하]
클라이언트 → 서버: GET /index.html
서버 → 클라이언트: HTML + 크리티컬 CSS (IW 10 패킷으로 한 번에 전송)
클라이언트: 즉시 렌더링 시작 (ACK 전에도 가능) ✅

[14,600바이트 초과]
서버 → 클라이언트: 첫 10 패킷(14,600바이트)
[대기] 서버는 ACK를 받을 때까지 대기
클라이언트 → 서버: ACK
서버 → 클라이언트: 나머지 데이터
→ 추가 RTT 발생 ⚠
```

Slow 4G(RTT 400ms)에서 15,000바이트를 쓰면 14,600바이트 대비 **400ms가 더 걸린다. 400바이트 늘었을 뿐인데 FCP가 400ms 느려지는 것이다.**

**네 가지 실무 의미**

1. **정확히는 14,600바이트(약 14.26KB)다.** 다만 실제 한계는 MSS·전송 계층·TLS/HTTP 오버헤드·서버 설정에 따라 달라진다. **14KB 전후를 넘기면 추가 왕복이 발생할 수 있다고 보고 HTML 전체 크기를 작게 유지한다.**
2. **크리티컬 CSS만이 아니라 HTML 문서 전체가 기준이다.** 이것이 가장 중요하다.

   ```
   HTML 마크업
   + <style> 인라인 크리티컬 CSS
   + <script> 인라인 자바스크립트
   + 메타 태그, DOCTYPE 등
   = HTML 문서 전체 크기
   ```

   HTML 마크업 5,000바이트 + 인라인 JS 2,000바이트라면 크리티컬 CSS는 **7,600바이트까지만** 쓸 수 있다.
3. **압축 후 크기가 기준이다.** Gzip/브로틀리 압축 후 크기가 14,600바이트 이하여야 한다.
4. **모바일 우선으로 측정한다.** 데스크톱보다 모바일의 첫 화면 영역이 좁으므로 모바일 기준으로 추출하면 크기를 줄일 수 있다.

```ts
function measureCriticalCSSSize(): { sizeInBytes: number; sizeInKB: string } | undefined {
  const criticalStyles = document.querySelector('style[data-critical]');
  if (!criticalStyles) {
    console.log('Critical CSS not found');
    return;
  }

  const cssContent = criticalStyles.textContent ?? '';
  const sizeInBytes = new Blob([cssContent]).size;
  const sizeInKB = (sizeInBytes / 1024).toFixed(2);

  console.log(`Critical CSS size: ${sizeInKB} KB (${sizeInBytes} bytes)`);

  const IW10_THRESHOLD = 14600; // TCP Initial Window 10 packets (10 × 1460 bytes)
  if (sizeInBytes > IW10_THRESHOLD) {
    console.warn('⚠ Critical CSS exceeds 14,600 bytes threshold');
    console.log(`Recommended: reduce by ${sizeInBytes - IW10_THRESHOLD} bytes`);
  } else {
    console.log('✅ Critical CSS size is optimal');
  }

  return { sizeInBytes, sizeInKB };
}
```

### 2.3 크리티컬 CSS 식별하기

**크롬 개발자 도구 Coverage**

1. 개발자 도구 열기(`Cmd+Shift+P` 또는 `Ctrl+Shift+P`)
2. "Show Coverage" 입력 후 실행
3. 새로고침 버튼을 클릭해 페이지 로드
4. CSS 파일 클릭 → 초록색이 사용된 CSS, 빨간색이 미사용 CSS

Coverage는 **전체 페이지 기준**이라 스크롤 후 콘텐츠도 포함된다. 첫 화면만 정확히 추출하려면 자바스크립트로 뷰포트 내 요소를 식별하거나 자동화 도구를 쓴다.

```ts
// 첫 화면에 보이는 요소 확인
document.querySelectorAll('*').forEach((el) => {
  const rect = el.getBoundingClientRect();
  if (rect.top < window.innerHeight && rect.bottom > 0) {
    console.log(el.tagName, el.className);
  }
});
```

**자동화 도구**

CSS 규칙 수집·의존성 해결·미디어 쿼리 처리를 수동으로 하는 것은 현실적이지 않다.

- **`critical`**: 애디 오스마니가 만든 도구. Puppeteer로 실제 브라우저에서 첫 화면 CSS를 추출한다. 유연하고 설정 옵션이 다양해 정적 사이트나 복잡한 레이아웃에 적합하다.
- **`penthouse`**: Puppeteer 기반으로 정확도가 높지만 설정이 다소 복잡하다. 대규모 CSS가 있는 사이트에 적합하다.
- **`beasties`**: 웹팩/Next.js 통합이 쉬워 리액트·뷰 프로젝트에서 많이 쓴다. 고급 커스터마이징은 제한적이다.

모두 헤드리스 브라우저로 페이지를 렌더링하고 뷰포트에 보이는 요소의 CSS 규칙만 추출한다. **빌드 파이프라인에 통합하면 HTML이 변경될 때마다 최신 크리티컬 CSS가 자동 생성된다.**

### 2.4 인라인 구현과 비동기 로딩

```html
<!doctype html>
<html>
  <head>
    <!-- 1. 크리티컬 CSS 인라인 (14KB 이하) -->
    <style>
      body { margin: 0; font-family: system-ui; }
      .header { background: #fff; padding: 1rem; }
    </style>

    <!-- 2. 나머지 CSS는 프리로드로 비동기 로드 -->
    <link rel="preload" href="/styles.css" as="style"
          onload="this.onload=null;this.rel='stylesheet'" />
    <noscript><link rel="stylesheet" href="/styles.css" /></noscript>
  </head>
  <body>
    <!-- 콘텐츠 -->
  </body>
</html>
```

`onload` 이벤트에서 `rel="stylesheet"`로 바꾸면 다운로드 완료 후 CSS가 적용된다.

> **실무 팁**: 주의할 점 세 가지. ① 크리티컬 CSS는 반드시 14KB 이하로 유지한다. 첫 TCP 왕복에 들어가지 못하면 FCP 개선 효과가 줄어든다. ② **FOUC를 방지하려면 크리티컬 CSS에 레이아웃과 폰트 스타일이 포함돼야 한다.** ③ 비동기 CSS 로딩 중 스타일이 바뀌면 CLS가 발생할 수 있다.

## 3. 미디어 쿼리를 활용한 조건부 로딩

프린트용 CSS, 다크 모드 CSS, 특정 화면 방향 전용 CSS처럼 **현재 사용자 환경에 불필요한 CSS**가 포함된 경우가 많다. `<link>` 태그의 `media` 속성이 이를 해결한다.

```html
<link rel="stylesheet" href="/styles.css" media="screen" />
<link rel="stylesheet" href="/print.css" media="print" />
<link rel="stylesheet" href="/dark.css" media="(prefers-color-scheme: dark)" />
```

브라우저는 페이지 로드 시 모든 `<link>`의 `media` 속성을 평가한다. **일치하지 않는 미디어 쿼리의 CSS는 CSSOM 구성에서 제외되어 렌더 트리 생성을 블로킹하지 않는다.** 다만 파일 자체는 낮은 우선순위로 다운로드되어 캐시에 저장되므로, 나중에 조건이 바뀌면(프린트 모드 진입, 다크 모드 전환) 추가 네트워크 요청 없이 즉시 적용된다.

### 3.1 성능 최적화에 쓸 수 있는 미디어 쿼리

**프린트 CSS 분리**

과거와 달리 실제로 프린트하는 사용자는 극소수인데, 프린트 스타일은 보통 20~50KB를 차지한다. 헤더·푸터·사이드바를 숨기고 페이지 나누기를 제어하는 스타일을 화면 사용자 전원에게 렌더 블로킹하는 것은 명백한 낭비다.

```html
<link rel="stylesheet" href="/print.css" media="print" />
```

**다크 모드 CSS 조건부 로딩**

다크 모드 스타일은 모든 컴포넌트의 색상·배경·그림자를 재정의해야 하므로 보통 30~80KB다. iOS·안드로이드·macOS·윈도우 모두 `prefers-color-scheme`을 지원하므로 즉시 적용 가능하다.

```html
<link rel="stylesheet" href="/light.css" media="(prefers-color-scheme: light)" />
<link rel="stylesheet" href="/dark.css" media="(prefers-color-scheme: dark)" />
<link rel="stylesheet" href="/default.css" />  <!-- 시스템 설정 없을 때 폴백 -->
```

**애니메이션 민감성 (`prefers-reduced-motion`)**

시스템에서 "애니메이션 줄이기"를 켠 사용자는 전정 장애·멀미·주의력 문제로 과도한 애니메이션을 불편해한다. 포트폴리오나 마케팅 랜딩 페이지의 애니메이션 CSS는 20~50KB에 달하기도 한다. **접근성과 성능을 동시에 개선하는 사례다.**

```html
<link rel="stylesheet" href="/animations.css" media="(prefers-reduced-motion: no-preference)" />
<link rel="stylesheet" href="/reduced-motion.css" media="(prefers-reduced-motion: reduce)" />
```

**입력 방식 감지 (`hover`, `pointer`)**

터치 디바이스에서 마우스 hover 효과는 의미가 없다. 모바일 트래픽이 60~70%인 사이트에서 hover CSS를 분리하면 **대다수 사용자의 렌더 블로킹 크기를 10~30KB 줄일 수 있다.**

```html
<link rel="stylesheet" href="/hover-effects.css" media="(hover: hover)" />
<link rel="stylesheet" href="/precise-ui.css" media="(pointer: fine)" />
<link rel="stylesheet" href="/touch-ui.css" media="(pointer: coarse)" />
```

`pointer: fine`은 마우스·트랙패드 같은 정밀 입력, `pointer: coarse`는 터치 입력을 의미한다.

**고해상도 디스플레이**

레티나 전용 `@2x`·`@3x` 이미지 스타일은 일반 디스플레이에서 불필요하다. 다만 요즘은 SVG로 해상도 문제가 해결되므로 **비트맵을 많이 쓰는 경우에만** 고려한다.

```html
<link rel="stylesheet" href="/retina.css"
      media="(-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi)" />
```

**화면 방향·뷰포트 크기별 CSS (주의 필요)**

`orientation`이나 뷰포트 크기로 CSS 파일을 완전히 분리할 수도 있지만 **대부분의 경우 권장하지 않는다.** 반응형 디자인은 하나의 CSS 파일 안에서 미디어 쿼리로 처리하는 편이 코드 중복을 줄이고 유지보수에 유리하다. **각 디바이스에서만 쓰이는 대량의 특화 스타일이 있을 때만** 고려한다(예: 모바일에서 전혀 쓰지 않는 데스크톱 전용 대시보드 UI가 100KB 이상).

### 3.2 실제 개선 효과

```html
<!-- 최적화 전 -->
<head>
  <link rel="stylesheet" href="/main.css" />   <!-- 300KB -->
  <link rel="stylesheet" href="/print.css" />  <!-- 150KB -->
  <link rel="stylesheet" href="/dark.css" />   <!-- 90KB -->
</head>
```

- 총 CSS: 540KB / **렌더 블로킹: 540KB(전부)**
- CSS 다운로드: `540KB × 8bit ÷ 1.44Mbps` ≈ **3,000ms**
- Slow 4G FCP: HTML 200ms + CSS 3,000ms ≈ **3,200ms**

```html
<!-- 최적화 후 -->
<head>
  <link rel="stylesheet" href="/main.css" />                                    <!-- 300KB -->
  <link rel="stylesheet" href="/print.css" media="print" />                     <!-- 150KB, 비블로킹 -->
  <link rel="stylesheet" href="/dark.css" media="(prefers-color-scheme: dark)" /><!-- 90KB, 비블로킹 -->
</head>
```

- 총 CSS: 540KB(동일) / **렌더 블로킹: 300KB(`main.css`만)**
- CSS 다운로드: `300KB × 8 ÷ 1.44` ≈ **1,667ms**
- Slow 4G FCP: HTML 200ms + 1,667ms ≈ **1,867ms**
- **FCP 개선: 1,333ms 단축, 42% 개선**

같은 CSS 파일을 쓰면서 `media` 속성만 추가했을 뿐인데 FCP가 1.3초 이상 빨라졌다.

### 3.3 실무 적용 팁과 주의사항

**1. `media` 속성은 다운로드를 막지 않는다**

렌더 블로킹만 제어할 뿐 다운로드 자체는 진행된다. **완전히 사용하지 않는 CSS는 HTML에서 제거해야 한다.**

```html
<!-- ❌ 사용하지 않는 CSS를 media로 숨김 — 다운로드는 됨 -->
<link rel="stylesheet" href="/unused.css" media="not all" />

<!-- ✅ 아예 제거 -->
```

**2. 조건이 변경되면 즉시 적용된다**

화면 회전이나 다크 모드 전환 시 이미 다운로드된 CSS가 추가 요청 없이 즉시 적용되어 부드럽게 전환된다.

**3. 크리티컬 CSS와 함께 사용한다**

```html
<head>
  <!-- 1. 크리티컬 CSS 인라인 (모든 환경에 필수) -->
  <style data-critical>
    /* 14KB 이하의 첫 화면 CSS */
  </style>

  <!-- 2. 메인 CSS 비동기 로드 -->
  <link rel="preload" href="/main.css" as="style"
        onload="this.onload=null;this.rel='stylesheet'" />

  <!-- 3. 조건부 CSS (렌더 블로킹 안 함) -->
  <link rel="stylesheet" href="/print.css" media="print" />
  <link rel="stylesheet" href="/dark.css" media="(prefers-color-scheme: dark)" />
</head>
```

**4. 복잡한 미디어 쿼리는 피한다**

조건이 복잡할수록 브라우저 평가 비용이 증가한다. 간단하고 명확한 조건으로 나눈다.

**5. 폴백을 고려한다**

오래된 브라우저는 일부 미디어 쿼리를 지원하지 않을 수 있다. 기본 CSS를 먼저 로드하고 향상된 기능을 미디어 쿼리로 추가한다.

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|---|---|---|
| 프린트·다크 모드 CSS에 `media` 미지정 | 화면에 전혀 안 쓰이는 CSS가 렌더 블로킹에 포함됨 | `media="print"`, `media="(prefers-color-scheme: dark)"` |
| 크리티컬 CSS가 14,600바이트 초과 | 첫 TCP 왕복에 못 들어가 추가 RTT 발생(Slow 4G에서 400ms) | 모바일 뷰포트 기준으로 추출해 크기 축소 |
| 크리티컬 CSS만 14KB로 계산 | **HTML 마크업 + 인라인 JS까지 합산**해야 하는데 누락 | HTML 문서 전체 크기를 압축 후 기준으로 측정 |
| 압축 전 크기로 14KB 판단 | 실제 전송 크기는 Gzip/브로틀리 압축 후 크기다 | 압축 후 크기로 측정 |
| 사용하지 않는 CSS를 `media="not all"`로 숨김 | 렌더 블로킹만 피할 뿐 다운로드는 그대로 진행됨 | HTML에서 아예 제거 |
| 크리티컬 CSS에 레이아웃·폰트 스타일 누락 | 비동기 CSS 도착 시 FOUC와 CLS 발생 | 레이아웃·폰트를 크리티컬에 포함 |
| `<noscript>` 폴백 누락 | 자바스크립트 비활성 환경에서 CSS가 아예 적용되지 않음 | `preload` + `onload` 패턴에 `<noscript>` 추가 |
| 반응형 레이아웃을 뷰포트별 파일로 분리 | 코드 중복이 늘고 유지보수가 어려워짐 | 하나의 CSS 안에서 `@media`로 처리 |
| 지나치게 복잡한 `media` 조건 | 브라우저 평가 비용이 증가 | 간단·명확한 조건으로 분리 |
| 디자인 변경 후 크리티컬 CSS 미갱신 | 첫 화면 스타일이 누락되어 FOUC 발생 | CI/CD에 크리티컬 CSS 생성 자동화 |

## 측정과 검증

**라이트하우스**

"Eliminate render-blocking resources"(또는 "Render blocking requests") 항목에서 어떤 리소스가 블로킹하는지와 절약 가능한 시간(Est savings)을 확인한다.

**Performance 탭**

페이지를 녹화하면 HTML 파싱이 어느 시점에 멈추고 CSS·자바스크립트 처리 후 언제 재개되는지 정확히 볼 수 있다. 라이트하우스는 정적 분석을, Performance 탭은 시각적 타임라인을 제공한다.

**콘솔로 렌더 블로킹 리소스 감지**

```ts
const renderBlockingResources: unknown[] = [];

// CSS 확인
document.querySelectorAll<HTMLLinkElement>('link[rel="stylesheet"]').forEach((link) => {
  if (!link.media || link.media === 'all' || link.media === 'screen') {
    renderBlockingResources.push({ type: 'CSS', url: link.href });
  }
});

// 동기 스크립트 확인 (async/defer 없는 모든 위치)
document.querySelectorAll<HTMLScriptElement>('script[src]').forEach((script) => {
  if (!script.async && !script.defer) {
    renderBlockingResources.push({
      type: 'JavaScript',
      url: script.src,
      location: script.closest('head') ? 'head' : 'body',
    });
  }
});

console.table(renderBlockingResources);
```

**미디어 쿼리 블로킹 상태 분석**

```ts
function analyzeMediaQueries(): void {
  const stylesheets = document.querySelectorAll<HTMLLinkElement>('link[rel="stylesheet"]');
  const blocking: unknown[] = [];
  const nonBlocking: unknown[] = [];

  stylesheets.forEach((link) => {
    const media = link.media || 'all';
    const matches = window.matchMedia(media).matches;
    const info = { href: link.href, media, matches };

    if (media === 'all' || media === 'screen' || matches) {
      blocking.push(info);
    } else {
      nonBlocking.push(info);
    }
  });

  console.log('Render Blocking CSS:', blocking);
  console.log('Non-Blocking CSS:', nonBlocking);
}
```

이 함수는 ① 모든 스타일시트를 수집하고, ② `window.matchMedia()`로 현재 환경과 비교하며, ③ `all`·`screen`이거나 일치하면 블로킹으로 분류해 ④ 두 그룹으로 출력한다. **라이트하우스의 정적 분석과 이 함수의 동적 분석을 함께 쓰면 더 정확하다.**

## 체크리스트

**렌더 블로킹 리소스 진단**

- [ ] 라이트하우스에서 "Eliminate render-blocking resources" 항목 확인
- [ ] Performance 탭에서 HTML 파싱이 멈추는 구간 확인
- [ ] 모든 `<link rel="stylesheet">`에 적절한 `media` 속성이 있는지 확인
- [ ] `<head>` 내부에 `async`/`defer` 없는 동기 스크립트가 있는지 확인
- [ ] 현재 렌더 블로킹 CSS의 총 크기 측정(100KB 이하 권장)

**크리티컬 CSS 구현**

- [ ] 첫 화면에 보이는 콘텐츠 요소를 정확히 식별
- [ ] 크리티컬 CSS가 14,600바이트 이하인지 확인
- [ ] **HTML 문서 전체 크기**(HTML + 인라인 CSS + 인라인 JS)가 14,600바이트 이하인지 확인
- [ ] 크리티컬 CSS를 `<style>` 태그로 `<head>` 최상단에 인라인
- [ ] 나머지 CSS를 `preload` + `onload`로 비동기 로드
- [ ] 자바스크립트 비활성화 환경을 위한 `<noscript>` 폴백 추가
- [ ] 모바일과 데스크톱 뷰포트 모두에서 첫 화면 테스트
- [ ] FOUC 발생 여부 확인

**미디어 쿼리 최적화**

- [ ] 프린트 CSS를 `media="print"`로 분리
- [ ] 다크 모드 CSS를 `media="(prefers-color-scheme: dark)"`로 분리
- [ ] 애니메이션 CSS를 `media="(prefers-reduced-motion: no-preference)"`로 분리
- [ ] hover 효과 CSS를 `media="(hover: hover)"`로 분리(선택)
- [ ] 디바이스별 전용 CSS가 있다면 적절한 미디어 쿼리로 분리
- [ ] 콘솔에서 미디어 쿼리 분석 함수로 블로킹 상태 확인
- [ ] 완전히 사용하지 않는 CSS는 HTML에서 제거(`media`로 숨기지 않기)

**자동화 도구 활용**

- [ ] 크리티컬 CSS 추출 도구 선택(`critical`, `beasties`, `penthouse`)
- [ ] 빌드 프로세스에 크리티컬 CSS 생성 자동화
- [ ] 페이지 타입별로 다른 크리티컬 CSS 생성(홈·목록·상세 등)
- [ ] CI/CD 파이프라인에 크리티컬 CSS 생성 단계 추가
- [ ] 디자인 변경 시 자동으로 재생성되는지 확인

**성능 측정 및 검증**

- [ ] FCP가 얼마나 개선됐는지 측정(최소 200~500ms 목표)
- [ ] LCP 개선 여부 확인
- [ ] Slow 4G / Regular 4G 조건에서 테스트
- [ ] 라이트 모드와 다크 모드 양쪽에서 테스트
- [ ] 프린트 미리보기에서 프린트 CSS 적용 확인
- [ ] 실제 사용자 환경(RUM)에서 FCP/LCP 데이터 수집
- [ ] `PerformanceObserver`로 paint 이벤트 모니터링

## 요약

- 렌더링 블로킹 리소스가 있으면 네트워크를 아무리 최적화해도 사용자는 빈 화면을 본다. **10KB CSS 하나가 1MB HTML 전체의 표시를 막는다.**
- CSS는 FOUC를 방지하기 위해 **CSSOM 구성이 완료될 때까지 렌더링을 의도적으로 지연**시킨다. `<head>`의 모든 `<link rel="stylesheet">`는 조건을 명시하지 않는 한 렌더 블로킹이다.
- CSS와 자바스크립트는 **연쇄 블로킹**한다. 스크립트가 `getComputedStyle()`을 쓸 수 있으므로 CSSOM이 완성될 때까지 실행이 지연된다.
- 크리티컬 렌더링 패스의 5단계(HTML 파싱 → CSS 파싱 → 렌더 트리 → 레이아웃 → 페인트) 중 CSS는 2·3번, 동기 JS는 1번을 막는다.
- 크리티컬 CSS 인라인화의 핵심 가치는 **RTT 제거**다. 일반 CSS 로딩은 2 RTT가 필요하지만 인라인은 HTML과 함께 도착한다.
- **14,600바이트**는 TCP 초기 혼잡 윈도우 10 패킷 × MSS 1460바이트에서 나온 값이다. 이를 넘기면 추가 RTT가 발생해 Slow 4G에서 400ms가 더 걸린다.
- **14,600바이트는 크리티컬 CSS만이 아니라 HTML 문서 전체(마크업 + 인라인 CSS + 인라인 JS) 기준이며, 압축 후 크기다.**
- `media` 속성은 렌더 블로킹만 제어하고 **다운로드는 막지 않는다.** 안 쓰는 CSS는 아예 제거해야 한다.
- 성능에 쓸 수 있는 미디어 쿼리는 `print`(20~50KB), `prefers-color-scheme`(30~80KB), `prefers-reduced-motion`(20~50KB), `hover`/`pointer`(10~30KB), 고DPI다.
- 실측 예시로 540KB CSS 중 240KB를 `media`로 분리하면 **Slow 4G FCP가 3,200ms → 1,867ms(42% 개선)**된다.
- 크리티컬 CSS와 미디어 쿼리는 **함께 쓸 때 가장 효과적이다.** 인라인 크리티컬 + 메인 비동기 + 조건부 CSS의 3단 구성이 표준 패턴이다.
- 완벽한 최적화보다 **측정 가능한 개선**이 중요하다. 자동화 도구를 CI/CD에 통합해 디자인이 바뀌어도 최적화 상태를 유지한다.

## 다른 챕터와의 관계

- **Ch4(리소스 우선순위)**: `media="print"` CSS가 Low 우선순위를 받는다는 규칙을 소개했다. 이 장은 그 규칙을 렌더 블로킹 제거 전략으로 확장한다.
- **Ch5(프리로드 스캐너)**: 메인 파서를 멈추게 하는 CSS·스크립트를 발견 관점에서 다뤘다면, 이 장은 그 리소스 자체를 줄인다. CSS `@import`를 피해야 하는 이유가 양쪽에서 만난다.
- **Ch6(async와 defer)**: 자바스크립트의 파서·렌더 블로킹 메커니즘을 상세히 다뤘다. 이 장은 CSS 쪽 블로킹에 집중한다.
- **Ch14(폰트 최적화)**: 크리티컬 CSS에 폰트 스타일을 포함해야 FOUC를 막는다는 점이 폰트 로딩 전략(`font-display`)과 직결된다.
- **Ch15(CSS 최적화)**: 이 장에서 개요만 다룬 크리티컬 CSS 추출 도구의 상세 사용법, 빌드 파이프라인 통합, 뷰포트별 최적화, 인라인 vs 프리로드 선택 기준, 미사용 CSS 제거, CSS-in-JS 성능을 전면적으로 다룬다.
- **Ch20(CLS)**: 비동기 CSS 로딩 중 스타일이 바뀌면 CLS가 발생한다는 문제를 레이아웃 안정성 관점에서 다룬다.
