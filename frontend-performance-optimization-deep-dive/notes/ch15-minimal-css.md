# Chapter 15: CSS는 최소한만 남겨야 빠르다

## 핵심 질문

이미지가 늦으면 빈 공간이 보이고 폰트가 늦으면 텍스트만 안 보이지만, **CSS가 늦으면 화면 전체가 멈춘다.** 90th percentile 기준 최대 225KB의 CSS가 실제로 사용되지 않는 현실에서 - 어떤 CSS를 언제 로드할 것이며, 미사용 코드와 런타임 CSS-in-JS의 비용은 어떻게 제거하는가?

## 1. 크리티컬 CSS 추출과 인라인화

Ch7에서 크리티컬 CSS의 개념과 렌더 블로킹 원리(FOUC 방지, 14KB TCP 제한)를 다뤘다. 이 장은 **실무 관점의 식별·측정·도구·전략 선택**에 집중한다.

### 1.1 첫 화면에 보이는 콘텐츠 측정

첫 화면 영역은 뷰포트 크기에 따라 달라진다(데스크톱 1920×1080, 노트북 1366×768, 모바일 375×667 등). 가장 일반적인 해상도 기준으로 추출하는 것이 현실적이다.

- **Coverage 패널**: CSS 파일별 사용률을 바이트 단위로 보여준다. 단, **전체 페이지 기준**이라 스크롤 후 콘텐츠의 스타일도 "사용됨"으로 표시된다는 한계가 있다.
- **프로그래밍 방식 식별**: `getBoundingClientRect()`로 뷰포트 내에 실제로 보이는 요소를 걸러낸다.

```ts
function getAboveFoldElements() {
  const elements: Element[] = [];
  const viewportHeight = window.innerHeight;
  const viewportWidth = window.innerWidth;

  document.querySelectorAll('*').forEach((element) => {
    const rect = element.getBoundingClientRect();
    if (
      rect.top < viewportHeight && rect.bottom > 0 &&
      rect.left < viewportWidth && rect.right > 0 &&
      window.getComputedStyle(element).display !== 'none'
    ) {
      elements.push(element);
    }
  });
  return elements;
}
```

일반적으로 첫 화면 요소는 전체 DOM의 10~20%지만, 적용되는 CSS 규칙은 30~50%에 달한다 - 전역 스타일(reset·타이포그래피)과 공통 컴포넌트(헤더·내비게이션)가 포함되기 때문이다.

### 1.2 크리티컬 CSS의 범위와 크기

기준은 **압축 후 14KB 이하**(TCP slow start 첫 10패킷, Ch7 참조)다. 실무에서 크리티컬 CSS는 전체 CSS의 5~15% 수준(중앙값 76KB 기준 약 8~12KB)이다.

- **포함**: 레이아웃 속성(display·position·크기), 타이포그래피, 색상·배경, 첫 화면에서 쓰이는 미디어 쿼리
- **제외**: 스크롤해야 보이는 콘텐츠(푸터·댓글), 인터랙션 요소(드롭다운·모달·툴팁·호버), 프린트 스타일, 불필요한 반응형 스타일

효과는 실측으로 검증됐다 - web.dev 사례 기준 크리티컬 CSS 인라인 + 비크리티컬 지연 로드로 **FCP 1초 → 0.8초(20% 개선)**. 느린 네트워크일수록 개선 폭이 크다.

### 1.3 실무 트레이드오프 - 인라인이 항상 답은 아니다

> **핵심 통찰**: 인라인의 장점(별도 요청 없이 즉시 렌더링)은 분명하지만, **세 가지 실질 비용**을 냉정하게 평가해야 한다.

1. **캐싱 효율 저하**: 인라인 CSS는 매 페이지 방문마다 재전송된다. 10KB 크리티컬 CSS × 10페이지 = 100KB 전송 vs 외부 파일이면 첫 방문 10KB 후 캐시 재사용. **첫 방문자에게는 1 RTT(~50ms)를 벌지만 재방문자에게는 매번 10~14KB를 추가 전송**하는 구조다. 재방문 많은 사이트(뉴스·블로그·SaaS 대시보드)일수록 외부 파일이 유리하다.
2. **유지보수 복잡도**: CSS 수정 = 모든 페이지 HTML 재생성 + CDN 전체 퍼지. SSR 환경에서는 CSS 변경이 곧 서버 재배포다.
3. **빌드 복잡도**: Puppeteer 기반 도구는 페이지당 수 초 - 100페이지면 빌드가 수 분 늘어난다.

**인라인을 피해야 하는 상황**: ① 페이지 50개 이상의 콘텐츠 사이트, ② CSS 변경이 잦은 프로젝트(주 1회 이상), ③ 이미 FCP가 1.8초 이하로 충분히 빠른 경우, ④ CDN 캐시 히트율이 높은 사이트(SaaS 대시보드 등).

실무 해법은 **하이브리드**다. 트래픽 많은 주요 페이지(홈·목록·상세)만 개별 크리티컬 CSS를 추출하고 나머지는 공통 크리티컬 CSS를 쓴다. SPA는 첫 진입 페이지만 인라인하고 이후 라우트는 청크별 동적 로드한다.

> **실무 팁 - 프레임워크 지원 현황(2025)**: Next.js `experimental.inlineCss`는 앱 라우터 전용 실험 기능으로 프로덕션 비권장(SSR·RSC 페이로드 중복, 페이지별 제어 불가). 넉스트는 `@nuxtjs/critters`(Beasties 기반)가 비교적 안정적. SvelteKit `inlineStyleThreshold`는 첫 화면 기준이 아닌 **단순 파일 크기 기준**이며 상대 경로 문제가 있다. **프로덕션 수준이 필요하면 Critters/Beasties 같은 별도 도구를 빌드 파이프라인에 통합하는 것이 가장 안정적이다.**

### 1.4 추출 도구 3종

| 도구 | 방식 | 장점 | 단점 |
|---|---|---|---|
| **Critical** | Puppeteer 실제 렌더링(내부적으로 Penthouse 사용) | 사용 간단, HTML에서 CSS 자동 감지, 걸프/웹팩 통합 쉬움 | 느림 - 페이지 100개면 100번 브라우저 렌더링 |
| **Beasties**(구 Critters) | 헤드리스 브라우저 없이 HTML 파싱 | 매우 빠름, 웹팩·비트 플러그인, 빌드 자동 통합 | **JS 동적 스타일 감지 불가** - SPA·동적 콘텐츠에 부정확 |
| **Penthouse** | Puppeteer + 병렬 처리 특화 | 대규모 사이트, `renderWaitTime`으로 동적 렌더링 대기, `forceInclude/Exclude` 수동 제어 | HTML·CSS 경로 수동 지정으로 설정 복잡 |

```ts
// Critical 기본 사용
import { generate } from 'critical';

await generate({
  inline: true,
  base: 'dist/',
  src: 'index.html',
  target: { html: 'index.html', css: 'critical.css' },
  dimensions: [
    { width: 375, height: 667 },    // 모바일
    { width: 1920, height: 1080 },  // 데스크톱
  ],
  extract: true, // 인라인 후 원본 CSS에서 제거
  ignore: { atrule: ['@font-face'] }, // 폰트는 별도 로드
});
```

핵심은 **CI/CD 통합 자동화**다. 배포마다 재추출하고 디자인 변경 시 자동 업데이트되게 한다.

### 1.5 인라인 vs 프리로드 전략

**인라인 방식** - `<style>` 태그로 직접 삽입. 네트워크 요청 없이 가장 빠른 초기 렌더링. 단 HTML 크기 증가, 캐싱 불가, 캐시 관리 복잡.

**프리로드 외부 파일 방식** - 캐싱 가능(재방문 성능), 대신 최소 1 RTT 추가.

```html
<!-- CSS 비동기 로드 표준 패턴 -->
<link rel="preload" href="/css/main.css" as="style"
      onload="this.onload=null;this.rel='stylesheet'" />
<noscript><link rel="stylesheet" href="/css/main.css" /></noscript>
```

> **참고 - `onload` 핸들러의 두 가지 일**<br><br>① `this.onload=null` - 일부 브라우저에서 `rel` 변경 시 onload가 재실행되어 무한 루프에 빠지는 것을 방지. ② `this.rel='stylesheet'` - 프리로드된 리소스를 실제 스타일시트로 적용(이미 다운로드됐으므로 즉시 파싱). `<noscript>`는 자바스크립트 비활성 환경 폴백이다. HTTP/2 Server Push는 크롬 106부터 기본 비활성화이므로 실무 권장안에서 제외하고, 추가 RTT는 103 Early Hints로 줄일 수 있다.

**선택 기준**

- 크리티컬 CSS **5KB 미만** → 인라인(요청 오버헤드 > HTML 증가 비용)
- **5~14KB** → 페이지 수·재방문율 고려(페이지 적고 재방문 많으면 외부 파일, 페이지 많으면 인라인)
- **14KB 초과** → 외부 파일 필수(TCP slow start 임곗값 초과로 인라인 이점 소멸)
- 페이지별 차이가 크면 **혼합**: 공통 부분 외부 파일 + 페이지 고유 부분만 인라인

## 2. 미사용 CSS 제거

### 2.1 미사용 CSS의 세 가지 비용

1. **네트워크 + 렌더 블로킹**: 600KB CSS 중 절반이 미사용이면 Slow 4G에서 약 1.7초 낭비 - 그리고 CSS는 렌더 블로킹이므로 **미사용 코드가 FCP·LCP를 직접 지연**시킨다. LCP 이미지·중요 JS와 대역폭 경쟁도 일으킨다.
2. **파싱·메모리 오버헤드**: 미사용 규칙도 파싱되어 CSSOM에 포함된다. 복잡한 선택자(`.parent .child > .grandchild:nth-child(2n)`)가 수천 개면 파싱에 수십 ms가 추가되고 메인 스레드를 블로킹해 INP에도 영향을 준다.
3. **스타일 계산 비용**: 브라우저는 DOM 요소마다 모든 CSSOM 규칙과의 매칭을 검사한다. SPA의 빈번한 인터랙션(모달·탭 전환)마다 미사용 규칙까지 재검사된다. Performance 패널의 `Recalculate Style`이 길면 이 신호다.

### 2.2 PurgeCSS와 자동화

PurgeCSS는 소스코드(HTML·JSX·Vue 템플릿)를 스캔해 실제 사용되는 선택자만 남긴다. 동작: 콘텐츠 파일 스캔 → 정규식 기반 선택자 후보 추출 → CSS 선택자와 비교 → 미매칭 규칙 제거.

```js
// webpack.config.js
const { PurgeCSSPlugin } = require('purgecss-webpack-plugin');
const glob = require('glob');

module.exports = {
  plugins: [
    new PurgeCSSPlugin({
      paths: glob.sync(`${path.join(__dirname, 'src')}/**/*`, { nodir: true }),
      safelist: {
        standard: [/^btn/, /^alert/],
        deep: [/^modal/],
        greedy: [/^tooltip/],
      },
    }),
  ],
};
```

> **핵심 통찰 - PurgeCSS 최대 함정은 동적 클래스**: PurgeCSS는 정규식 기반이라 `` `text-${color}-500` `` 같은 **문자열 연결로 만든 클래스를 인식하지 못하고 제거해버린다.** 해결은 두 가지 - ① `safelist`에 명시(`standard` 정확 매칭 / `deep` 정규식 / `greedy` 부분 매칭 시 전체 보존), ② 애초에 **전체 문자열로 작성**한다: `color === 'red' ? 'text-red-500' : 'text-blue-500'`.

Tailwind CSS는 자체적으로 소스 파일을 스캔해 사용하는 유틸리티만 생성하므로 **별도 PurgeCSS 통합보다 content/소스 스캔 대상이 빠짐없이 설정됐는지 확인**하는 것이 중요하다(개발 3MB → 프로덕션 10KB 이하 사례).

### 2.3 Coverage 도구로 미사용 CSS 찾기

Coverage 패널(Cmd+Shift+P → "Show Coverage" → 리로드)은 리소스별 Total Bytes / Unused Bytes / 시각화 바를 보여준다. 100KB 중 Unused 75KB면 최적화 1순위다. 파일 클릭 시 Sources 패널에서 라인별 사용/미사용(빨간색)을 확인한다.

**빨간색 코드를 그냥 삭제하면 안 되는 세 가지 이유**

1. **동적 콘텐츠**: 모달·드롭다운·툴팁은 초기 로드 기준 미사용으로 표시되지만 실제로 필요하다. **Coverage를 켠 상태로 모든 인터랙션(모달 열기·탭 전환·드롭다운)을 수행한 뒤** 측정을 끝내야 진짜 미사용을 구분할 수 있다.
2. **반응형 스타일**: 데스크톱에서 측정하면 모바일 미디어 쿼리가 미사용으로 뜬다. 양쪽 모두 측정한다.
3. **서드파티 프레임워크**: Bootstrap·Material UI는 대부분 미사용이 많다 - 필요한 컴포넌트만 임포트하거나 PurgeCSS로 제거한다.

## 3. CSS-in-JS 성능 고려사항

### 3.1 Runtime CSS-in-JS의 문제점

styled-components(~15KB gzip), Emotion(~7KB) 같은 런타임 라이브러리는 세 층위의 비용을 만든다.

**① 번들 크기와 파싱**: 런타임 엔진 + 스타일 정의 코드가 자바스크립트 번들에 포함된다. CSS 파일은 JS 파싱을 막지 않지만, **CSS-in-JS는 자바스크립트 번들의 일부이므로 JS 파싱을 블로킹**한다.

**② 스타일 직렬화와 DOM 주입**: 렌더링마다 스타일 객체 → CSS 문자열 변환(직렬화)이 일어나고, `<style>` 태그가 `<head>`에 주입된다. 실측: **Emotion 평균 렌더링 54.3ms → Sass Modules 전환 후 27.7ms(48% 감소)**. 리액트 코어 팀의 세바스천 마크보게는 이 방식이 "리액트 렌더링 중 프레임마다 모든 DOM 노드에 대해 모든 CSS 규칙을 재계산하게 만든다 - 매우 느리다"고 지적했다. 리스트·테이블처럼 수백 요소 렌더링에서 특히 두드러지고 INP를 저하시킨다.

**③ SSR 하이드레이션의 복잡성**: 정적 CSS는 `<link>` 하나로 끝나지만 런타임 CSS-in-JS는 -

- 서버에서 `ServerStyleSheet`로 렌더링 중 스타일을 수집·직렬화해야 하며, **요청마다 실행되어 서버 CPU와 TTFB가 증가**한다. `sheet.seal()`을 `finally`에서 호출하지 않으면 메모리 누수까지 발생한다.
- 클라이언트 하이드레이션 시 컴포넌트가 재실행되며 스타일을 **다시 생성**한다 - `<head>`에 동일 스타일이 두 번 존재하게 된다.
- 타이밍 문제로 **FOUC·CLS**가 발생한다: 서버 스타일로 정상 렌더링 → 하이드레이션이 서버 스타일 제거 → 짧은 무스타일 순간 → 클라이언트 스타일 재주입.

### 3.2 Zero-runtime CSS-in-JS

해법은 **빌드 타임에 정적 CSS를 추출**하는 것이다. 개발 시에는 자바스크립트로 스타일을 작성하지만 빌드 후에는 일반 CSS 파일 + 클래스명만 남는다.

**Vanilla Extract** - 타입 안전성 + 완전한 Zero-runtime. "Sass처럼 작동하지만 타입스크립트의 강력함".

```ts
// button.css.ts
import { style } from '@vanilla-extract/css';

export const button = style({
  padding: '0.5rem 1rem',
  borderRadius: '0.25rem',
  border: 'none',
  cursor: 'pointer',
});

export const primary = style({ background: '#007bff', color: 'white' });
```

```ts
// theme.css.ts - 테마 계약에도 타입 안전성
import { createTheme } from '@vanilla-extract/css';

export const [themeClass, vars] = createTheme({
  color: { primary: '#007bff', text: '#212529' },
  space: { small: '0.5rem', medium: '1rem' },
});

export const card = style({
  padding: vars.space.medium, // 자동완성 + 타입 체크
  color: vars.color.text,
});
```

**Linaria** - 태그드 템플릿 리터럴로 기존 CSS 문법 그대로(미디어 쿼리·의사 선택자·중첩 지원). 동적 스타일은 CSS 변수로 변환된다. 타입 안전성은 없다.

**CSS Modules 하이브리드** - Zero-runtime 전환이 어렵다면 CSS Modules(+ 유틸리티 클래스) 조합도 효과적이다. 로컬 스코핑·코로케이션을 유지하며 런타임 오버헤드를 제거한다.

### 3.3 Zero-runtime의 현실적 제약

1. **동적 스타일링 제한**: 프롭의 임의 값을 직접 스타일에 쓸 수 없다(빌드 타임에 CSS가 확정되므로). CSS 변수 우회가 가능하지만 코드가 복잡해지고 타입 안전성이 약해진다. **사용자 커스터마이징 위젯·테마 에디터**처럼 프롭 기반 완전 동적 스타일이 핵심이면 런타임 방식이 더 적합할 수 있다.

```tsx
// CSS 변수 우회 패턴
export const box = style({
  width: 'var(--box-width)',
  background: 'var(--box-color)',
});

function Box({ width, color, children }) {
  return (
    <div className={box} style={{ '--box-width': `${width}px`, '--box-color': color }}>
      {children}
    </div>
  );
}
```

2. **빌드 시간 증가**: 빌드 중 자바스크립트 평가 + CSS 추출이 필요해 대규모 프로젝트에서 HMR이 느려지고 초기 빌드가 수 분까지 늘어난 사례가 있다.
3. **마이그레이션 비용**: 라이브러리 교체 수준이 아니다 - Spot 팀은 Emotion → Vanilla Extract 전환에 200개 이상 컴포넌트를 수작업으로, 수개월에 걸쳐 옮겼다.
4. **디버깅 복잡도**: 스타일 정의와 실제 CSS가 다른 파일에 있고, 타입 에러인지 CSS 추출 에러인지 구분이 어려울 때가 있다.

### 3.4 솔루션 선택 기준

| 솔루션 | 성능 | 개발 경험 | 빌드 복잡도 | 적합한 경우 |
|---|---|---|---|---|
| CSS Modules | 최고(런타임 0) | 중간(동적 스타일 제한) | 낮음 | 정적 스타일 위주 프로젝트 |
| Runtime CSS-in-JS | 낮음(런타임 + SSR 복잡도) | 높음(프롭 기반 동적) | 낮음 | 내부 도구, 프로토타입, 소규모 |
| Zero-runtime CSS-in-JS | 최고(빌드 타임 추출) | 높음(타입 안전 + 코로케이션) | 중간 | **대규모 프로덕션, SSR 사이트** |

- **초기 렌더링이 중요한 공개 사이트·이커머스**: CSS Modules 또는 Zero-runtime. Runtime은 FCP·LCP 저하.
- **인터랙션 많은 대시보드·SaaS**: Zero-runtime(Runtime은 INP 저하).
- **SSR/SSG**: Zero-runtime 또는 CSS Modules 필수(하이드레이션 복잡도·FOUC 회피).
- **레거시 마이그레이션**: 신규 컴포넌트부터 Zero-runtime으로, 점진 전환.
- **팀 스킬셋**: TS 경험 팀 → Vanilla Extract, CSS 친숙 팀 → Linaria/CSS Modules.

> **핵심 통찰**: Zero-runtime으로 전환하면 **CSS 코드 스플리팅이 공짜로 따라온다.** 웹팩·비트는 `React.lazy()` 등 동적 임포트로 컴포넌트를 분할할 때 해당 컴포넌트의 CSS도 자동으로 별도 청크로 추출한다 - 사용자가 그 컴포넌트를 로드할 때만 CSS가 함께 온다. 미디어 쿼리 기반 조건부 로딩은 Ch7의 `<link media>` 속성을 쓴다.

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|---|---|---|
| 모든 페이지에 큰 크리티컬 CSS 인라인 | 재방문자에게 매번 10~14KB 재전송, 캐싱 이점 상실 | 5KB 미만만 인라인, 이상이면 외부 파일 + 프리로드 |
| 14KB 초과 크리티컬 CSS | TCP slow start 임곗값 초과로 인라인 이점 소멸 | 범위 축소 또는 외부 파일 전환 |
| Coverage 빨간색 코드를 즉시 삭제 | 모달·반응형 등 동적/조건부 스타일도 미사용으로 표시됨 | 모든 인터랙션 수행 + 양쪽 뷰포트 측정 후 판단 |
| 동적 클래스(`` `text-${color}-500` ``) + PurgeCSS | 정규식이 인식 못 해 필요한 스타일이 제거됨 | 전체 문자열 작성 또는 `safelist` 등록 |
| Tailwind content 설정 누락 | 스캔 안 된 파일의 클래스가 프로덕션에서 사라짐 | 모든 템플릿·컴포넌트 경로 포함 확인 |
| SSR 프로덕션에 Runtime CSS-in-JS | 하이드레이션 이중 스타일 생성 + FOUC + TTFB 증가 | Zero-runtime(Vanilla Extract·Linaria) 또는 CSS Modules |
| `ServerStyleSheet`에 `seal()` 누락 | 요청마다 메모리 누수 | `try-finally`에서 `sheet.seal()` 호출 |
| 리스트 항목마다 css prop 동적 스타일 | 렌더링마다 직렬화 + 스타일 재계산으로 INP 저하 | 정적 클래스 + CSS 변수로 분리 |
| SPA 전 라우트에 크리티컬 CSS 인라인 | 첫 로드 이후엔 자바스크립트 라우팅이라 무의미 | 첫 진입 페이지만 인라인, 이후 청크 동적 로드 |
| Beasties를 동적 콘텐츠 SPA에 사용 | HTML 파싱만 하므로 JS 주입 스타일을 놓침 | Puppeteer 기반(Critical/Penthouse) 사용 |
| 비동기 CSS 패턴에서 `onload=null` 누락 | 일부 브라우저에서 무한 루프 | 표준 패턴 그대로 사용 + `<noscript>` 폴백 |

## 측정과 검증

- **Coverage**: CSS 사용률 측정(목표 70% 이상). 인터랙션 수행 후 측정으로 동적 스타일 오판 방지.
- **라이트하우스**: "Eliminate render-blocking resources", "Reduce unused CSS" 경고 확인.
- **Performance 패널**: `Recalculate Style` 길이로 과도한 규칙 수 진단, FCP 마커로 인라인 전후 비교.
- **Network 탭**: 총 CSS 전송 크기(전체 페이지 100KB 이하 목표), 라우트별 CSS 청크 분리 로드 확인.
- **목표 지표**: FCP 1.8초 이하, LCP 2.5초 이하, Runtime CSS-in-JS 사용 시 INP 200ms 이하.
- **CI/CD**: 라이트하우스 CI로 빌드마다 CSS 크기·미사용 비율 측정, Performance budget으로 임곗값 초과 시 빌드 실패, PR마다 CSS 크기 변화 리포트.

## 체크리스트

**크리티컬 CSS 인라인화**

- [ ] 크리티컬 CSS를 14KB 이내로 유지(gzip 압축 후 기준)
- [ ] 첫 화면 렌더링에 필요한 최소한만 인라인
- [ ] 프레임워크 자동 도구 우선 검토(Next.js inlineCss, Nuxt Beasties, SvelteKit inlineStyleThreshold - 제약 확인)
- [ ] 자동 도구로 부족하면 Critical/Beasties/Penthouse 사용
- [ ] `<link rel="preload" as="style">` + onload 패턴으로 나머지 CSS 비동기 로드
- [ ] 크리티컬 CSS와 전체 CSS의 중복 없는지 빌드 설정 확인

**미사용 CSS 제거**

- [ ] Coverage 탭에서 미사용 CSS 비율 확인
- [ ] 미사용 50% 이상이면 PurgeCSS 도입
- [ ] 동적 클래스명을 safelist에 추가
- [ ] Tailwind 사용 시 content/소스 스캔 대상 완전성 확인
- [ ] 빌드 후 CSS 크기 감소율 확인(70% 이상 목표)
- [ ] 프로덕션 빌드에서 실제 페이지 테스트로 스타일 누락 검증

**CSS-in-JS 선택과 마이그레이션**

- [ ] Runtime CSS-in-JS(Emotion, styled-components)를 프로덕션에서 회피
- [ ] 초기 렌더링 중요 시 Zero-runtime(Vanilla Extract·Linaria·CSS Modules) 선택
- [ ] SSR 환경은 반드시 Zero-runtime
- [ ] 마이그레이션은 신규 컴포넌트부터 점진 전환
- [ ] 타입 안전성 필요 시 Vanilla Extract
- [ ] 전환 전후 FCP·LCP·INP 측정으로 효과 검증

**CSS 코드 스플리팅**

- [ ] 빌드 도구의 CSS 스플리팅 자동 지원 확인(mini-css-extract-plugin, 비트 cssCodeSplit)
- [ ] 동적 임포트 시 CSS 자동 분리 검증
- [ ] 라우트별 CSS 청크 생성을 빌드 결과물로 확인
- [ ] Network 탭에서 필요한 CSS만 로드되는지 확인
- [ ] 미디어 쿼리 조건부 로딩은 `<link media>` 활용(Ch7)

**성능 측정과 모니터링**

- [ ] 라이트하우스 "Reduce unused CSS" 경고 확인
- [ ] Coverage 사용률 70% 이상 목표
- [ ] 총 CSS 전송 크기 100KB 이하 목표
- [ ] FCP 1.8초 / LCP 2.5초 이하 확인
- [ ] Runtime CSS-in-JS 사용 시 INP 200ms 이하 확인

**빌드 자동화와 CI/CD**

- [ ] PurgeCSS를 빌드 스크립트에 통합
- [ ] 크리티컬 CSS 생성을 프로덕션 빌드에 포함
- [ ] CSS 번들 크기 임곗값 초과 시 빌드 실패 설정
- [ ] 라이트하우스 CI로 CSS 지표 모니터링
- [ ] Performance budget에 CSS 크기 제한 추가
- [ ] PR마다 CSS 크기 변화 자동 리포트

## 요약

- CSS 최적화의 원칙은 **"필요한 것만, 필요한 때에"**다. CSS는 렌더 블로킹이라 미사용 코드가 네트워크·파싱·스타일 계산의 3중 비용을 만든다.
- 크리티컬 CSS는 전체의 5~15%(약 8~12KB)이며 **압축 후 14KB 이하**가 기준이다. 첫 화면 요소는 DOM의 10~20%지만 규칙은 30~50%를 차지한다(전역 스타일·공통 컴포넌트 때문).
- **인라인은 만능이 아니다.** 첫 방문 1 RTT 절약 vs 재방문 매번 재전송의 트레이드오프 - 페이지 50개 이상·CSS 변경 잦음·FCP 이미 양호·재방문 많음이면 외부 파일 + 프리로드가 낫다. 5KB 미만 인라인 / 14KB 초과 외부 파일 / 사이는 재방문율로 판단.
- 추출 도구: **Critical**(간단, Puppeteer라 느림) / **Beasties**(빠름, 동적 스타일 못 봄) / **Penthouse**(병렬·대규모, 설정 복잡). CI/CD 자동화가 핵심이다.
- 비동기 CSS 표준 패턴: `preload as="style"` + `onload="this.onload=null;this.rel='stylesheet'"` + `<noscript>` 폴백.
- 미사용 CSS 제거는 PurgeCSS로 자동화하되 **동적 클래스가 최대 함정**이다(전체 문자열 작성 또는 safelist). Coverage는 모든 인터랙션 수행 + 양쪽 뷰포트 측정 후 판단한다.
- Runtime CSS-in-JS의 3중 비용: JS 번들 포함(파싱 블로킹), 렌더링마다 직렬화 + DOM 주입(실측 48% 렌더링 차이, INP 저하), SSR 하이드레이션 이중 작업(FOUC·CLS·TTFB 증가).
- 해법은 **Zero-runtime**(Vanilla Extract = 타입 안전, Linaria = CSS 친숙) 또는 CSS Modules 하이브리드다. 단 동적 스타일 제한(CSS 변수 우회), 빌드 시간 증가, 마이그레이션 비용(수개월 사례), 디버깅 복잡도의 제약을 점검하고 선택한다.
- 선택 매트릭스: 공개 사이트·이커머스·SSR → Zero-runtime/CSS Modules, 내부 도구·프로토타입 → Runtime도 무방, 마이그레이션 → 신규 컴포넌트부터 점진적으로.
- Zero-runtime 전환 시 CSS 코드 스플리팅은 번들러가 자동 처리한다. 그리고 CSS 최적화는 일회성이 아니다 - **라이트하우스 CI + Performance budget으로 회귀를 방지**한다.

## 다른 챕터와의 관계

- **Ch7(렌더링 블로킹 리소스)**: 크리티컬 CSS의 개념·14KB 원리·미디어 쿼리 조건부 로딩을 개관했고, 이 장은 도구·전략 선택·트레이드오프를 실무 수준으로 완결한다.
- **Ch9(불필요한 리소스 제거)**: Coverage로 미사용 코드를 찾는 방법론이 자바스크립트(Ch9)와 CSS(이 장)에서 같은 문법으로 반복된다.
- **Ch10(코드 스플리팅)**: 동적 임포트 시 CSS 청크 자동 분리가 이 장의 Zero-runtime 논의와 만난다.
- **Ch11(서버로 로직 이동)·Ch16(하이드레이션)**: Runtime CSS-in-JS의 SSR 하이드레이션 비용이 하이드레이션 장의 문제의식과 직결된다.
- **Ch14(폰트 최적화)**: 크리티컬 CSS의 `@font-face` 처리(ignore 설정)와 폰트 로딩 전략이 함께 설계돼야 한다.
- **Ch18(자바스크립트 실행)·Ch22(컴포넌트 최적화)**: 스타일 재계산이 메인 스레드를 블로킹해 INP를 저하시키는 메커니즘이 런타임 최적화 장들로 이어진다.
