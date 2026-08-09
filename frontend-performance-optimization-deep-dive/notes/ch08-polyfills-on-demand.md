# Chapter 8: 폴리필은 '필요한 경우'에만 로드하라

## 핵심 질문

번들 분석 도구를 열면 가장 먼저 눈에 띄는 것이 `core-js`, `regenerator-runtime` 같은 수백 KB의 폴리필이다. 최신 브라우저 사용자가 IE11용 폴리필을 다운로드하고 실행하는 낭비를 어떻게 없앨 것인가? 그리고 여전히 구형 브라우저를 쓰는 사용자에게는 어떻게 서비스를 제공할 것인가?

## 1. 가능한 타깃 브라우저를 최소한으로 좁혀라

폴리필은 번들 크기만 늘리는 게 아니다. **폴리필 코드도 파싱되고, 컴파일되고, 실행돼야 한다.** 모바일 저사양 기기에서는 이 과정에 수백 밀리초가 추가된다. 크롬·사파리·파이어폭스 최신 버전은 `Object.groupBy()`(크롬 117+), `Promise.withResolvers()`(크롬 119+), `Array.fromAsync()`(크롬 121+) 같은 최신 기능까지 네이티브로 지원하는데도, 빌드 타깃을 낮게 잡으면 모든 사용자에게 모든 폴리필이 배달된다.

해결의 출발점은 **browserslist**다. Babel·PostCSS·Autoprefixer 등 모든 빌드 도구가 공통으로 참조하는 타깃 브라우저 정의 표준으로, 이 구성 하나만 조정해도 번들이 크게 줄어든다.

### 1.1 browserslist 설정

```json
// package.json
{
  "browserslist": ["> 0.5%", "last 2 versions", "not dead"]
}
```

```
# .browserslistrc
> 0.5%
last 2 versions
not dead
```

이 조건들은 AND가 아니라 **OR로 결합**된다. "전 세계 점유율 0.5% 이상" **또는** "각 브라우저의 최신 2버전" **또는** "업데이트가 유지되는 브라우저" 중 하나라도 만족하면 타깃에 포함된다. `not dead`는 공식 지원이 종료된 브라우저(IE11 등)를 제외한다. 기본값인 `defaults` 쿼리는 `> 0.5%, last 2 versions, Firefox ESR, not dead`와 동일하다.

`npx browserslist` 명령으로 현재 설정이 어떤 브라우저를 타기팅하는지 확인할 수 있다.

> **핵심 통찰**: 폴리필 양을 결정하는 것은 목록의 **길이**가 아니라 **가장 낮은 버전**이다. 목록이 길어도 전부 최신 브라우저면 폴리필은 적고, 목록이 짧아도 IE11 하나가 끼어 있으면 폴리필이 폭증한다. 실제 서비스 데이터를 보면 사용자의 90% 이상이 최신 브라우저인 경우가 많다. 구글 애널리틱스나 서버 로그의 User-Agent를 분석해 **점유율 1% 미만의 레거시 브라우저는 과감히 제외를 검토**한다.

더 공격적으로 모던 브라우저만 타기팅할 수도 있다.

```json
{
  "browserslist": ["chrome >= 120", "edge >= 120", "firefox >= 120", "safari >= 17"]
}
```

크롬/엣지 120 이상(2023년 12월 출시)은 ES2023까지 대부분의 기능(`Array.prototype.toSorted()`, `Array.prototype.findLast()`, `Object.hasOwn()`)을 네이티브로 지원한다. 다만 `Array.fromAsync()`(크롬 121+), `Set.prototype.union()`(크롬/엣지 122+, 파이어폭스 127+, 사파리 17+), `Object.groupBy()`(크롬 117+, 사파리 17.4+) 등 일부 최신 기능은 더 높은 버전이 필요하다.

> **참고 - 에버그린 브라우저(evergreen browser)**<br><br>사용자의 별도 조작 없이 자동으로 최신 버전으로 업데이트되는 브라우저다. 크롬·엣지·파이어폭스·사파리가 대표적이다. IE 시절에는 사용자가 직접 설치 파일을 받아 버전을 올려야 했기에 구버전 사용자가 많았지만, 에버그린 브라우저는 항상 최신 상태를 유지하므로 개발자가 최신 웹 표준을 더 빠르고 과감하게 도입할 수 있다.

browserslist는 한 번 설정하고 끝이 아니다. **분기마다 사용자 데이터를 재검토**하고 `npx update-browserslist-db`로 브라우저 데이터베이스를 최신으로 유지한다. 1년 전 점유율 5%였던 브라우저가 지금은 1% 미만일 수 있다.

### 1.2 코드에서 사용하는 기능도 폴리필 크기를 결정한다

browserslist를 아무리 좁혀도 **코드에서 타깃 브라우저가 지원하지 않는 최신 기능을 쓰면 폴리필이 추가된다.**

```ts
// 크롬 110 미만 타깃이면 폴리필 필요
const sorted = [3, 1, 2].toSorted(); // toSorted는 크롬 110+

// 크롬 117 미만 타깃이면 폴리필 필요 (ES2024 표준)
const grouped = Object.groupBy(items, (item) => item.category);
```

Can I use에서 각 기능의 지원 현황을 확인하는 습관과 함께, **`eslint-plugin-compat`**을 쓰면 타깃 브라우저에서 지원하지 않는 API 사용을 개발 중에 바로 경고받을 수 있다.

```js
// eslint.config.js (Flat Config)
import compat from 'eslint-plugin-compat';

export default [
  {
    plugins: { compat },
    rules: {
      ...compat.configs.recommended.rules,
    },
    // browserslist 설정을 자동으로 참조
  },
];
```

## 2. 조건부 폴리필 로딩

browserslist는 **빌드 타임** 최적화다. 모든 사용자에게 동일한 번들을 주되 그 안의 폴리필 양을 줄인다. 하지만 타깃에 크롬 120이 포함돼 있어도 실제 사용자는 크롬 120부터 140까지 다양하다. 크롬 140 사용자도 크롬 120용 폴리필을 받게 된다.

**조건부 폴리필 로딩**은 런타임에 브라우저가 기능을 지원하는지 확인하고 필요한 경우에만 폴리필을 로드한다. 초기 번들에는 폴리필을 아예 넣지 않는다.

- **장점**: 최신 브라우저 사용자는 폴리필을 전혀 다운로드하지 않는다. 에버그린 브라우저 특성상 대다수가 최신 버전이므로 매우 효과적이다.
- **단점**: 로딩 로직을 직접 작성해야 하고, 레거시 브라우저에서는 **추가 네트워크 요청**이 발생하며 폴리필 로드 완료 전까지 앱 실행을 대기해야 한다. 전체 평균 로딩 시간은 줄지만 **구형 브라우저 사용자는 오히려 느려질 수 있다.**

### 2.1 기능 감지 (feature detection)

```ts
// app.js
async function loadPolyfillsIfNeeded(): Promise<void> {
  const polyfills: Promise<unknown>[] = [];

  // Object.groupBy 미지원 시 폴리필 (크롬 117+, 사파리 17.4+)
  if (!Object.groupBy) {
    polyfills.push(import('./polyfills/object-groupby.js'));
  }

  // Array.fromAsync 미지원 시 폴리필 (크롬 121+)
  if (!Array.fromAsync) {
    polyfills.push(import('./polyfills/array-fromasync.js'));
  }

  // IntersectionObserver 미지원 시 폴리필
  if (!('IntersectionObserver' in window)) {
    polyfills.push(import('./polyfills/intersection-observer.js'));
  }

  // 모든 폴리필 로드 완료 대기
  await Promise.all(polyfills);
}

// 폴리필 로드 후 애플리케이션 시작
loadPolyfillsIfNeeded().then(() => {
  import('./main.js');
});
```

최신 브라우저에서는 `polyfills` 배열이 비어 있으므로 `Promise.all([])`이 즉시 완료되고 메인 앱이 바로 실행된다.

더 정교한 감지가 필요한 경우도 있다. `Set`은 존재하지만 `union`·`intersection` 같은 최신 메서드는 없는 브라우저가 있으므로 `'Set' in window`만으로는 부족하다.

```ts
function needsSetMethodsPolyfill(): boolean {
  // Set 메서드: 크롬/엣지 122+, 파이어폭스 127+, 사파리 17+ (2024년 표준화)
  return !('Set' in window) || !('union' in Set.prototype) || !('intersection' in Set.prototype);
}
```

이렇게 세밀하게 감지하면 **부분적으로만 최신 기능을 지원하는 브라우저**(예: `Object.groupBy`가 없는 사파리 17.0~17.3)에도 최소한의 폴리필만 줄 수 있다.

### 2.2 스크립트 로딩 순서와 성능 영향

폴리필 로더는 메인 애플리케이션보다 **먼저** 실행돼야 하고, 폴리필 로드가 끝나기 전에 앱이 시작되면 안 된다.

```html
<head>
  <!-- 폴리필 로더를 먼저 로드 (블로킹) -->
  <script src="/polyfill-loader.js"></script>
</head>
<body>
  <div id="app"></div>
  <!-- 메인 앱은 폴리필 로드 후 실행 -->
  <script type="module" src="/main.js"></script>
</body>
```

```ts
// index.js (진입점) - 번들러 사용 시
import { loadPolyfillsIfNeeded } from './polyfill-loader.js';

// 1. 폴리필 먼저 로드 (await로 완료 대기)
await loadPolyfillsIfNeeded();

// 2. 폴리필 준비 완료 후 메인 앱 로드
import('./main.js');
```

> **실무 팁**: 폴리필 로딩 실패에 대비한 **에러 핸들링이 필수다.** 네트워크 오류나 CDN 장애로 로드가 실패하면 앱이 아예 시작되지 않을 수 있다. `try-catch`로 실패를 감지하고 폴백을 구성하거나 사용자에게 오류를 알린다. 또한 레거시 브라우저의 추가 RTT를 완화하려면 **자바스크립트로 조건부 프리로드**를 구현한다. HTML에 `<link rel="preload">`를 직접 쓰면 모든 브라우저가 폴리필을 받아 조건부 로딩의 이점이 사라진다.

```html
<script>
  if (!Object.groupBy) {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.as = 'script';
    link.href = '/polyfills/object-groupby.js';
    document.head.appendChild(link);
  }
</script>
```

### 2.3 자체 호스팅 폴리필 번들

> **핵심 통찰**: 과거 인기를 끌었던 Polyfill.io 같은 외부 CDN 서비스는 **더 이상 사용하면 안 된다.** 2024년 2월 Funnull이라는 회사가 polyfill.io 도메인을 인수한 뒤 악성 코드를 삽입하는 공급망 공격이 발생했고, 같은 해 6월 알려지면서 10만 개 이상의 웹사이트가 영향을 받았다. 구글과 클라우드플레어가 즉시 경고를 발행했다. **폴리필은 자체 호스팅한다.**

`core-js`를 직접 임포트해 필요한 기능만 담은 폴리필 파일을 만든다.

```ts
// polyfills/modern.js - 모던 브라우저용 최소 폴리필 (ES2023~2024)
import 'core-js/actual/object/group-by';      // 크롬 117+, 사파리 17.4+
import 'core-js/actual/array/from-async';     // 크롬 121+, 사파리 16.4+
import 'core-js/actual/array/to-sorted';      // 크롬 110+, 사파리 16+
import 'core-js/actual/set/union';            // 크롬/엣지 122+, 파이어폭스 127+, 사파리 17+
import 'core-js/actual/set/intersection';

// polyfills/legacy.js - 레거시 브라우저용 전체 폴리필
import 'core-js/stable';
import 'regenerator-runtime/runtime';
```

```ts
// vite.config.ts - 폴리필을 별도 청크로 분리
export default {
  build: {
    rollupOptions: {
      input: {
        main: './src/main.js',
        'polyfills-modern': './src/polyfills/modern.js',
        'polyfills-legacy': './src/polyfills/legacy.js',
      },
    },
  },
};
```

기능 감지 결과에 따라 **3단계**로 로드한다.

```ts
async function loadPolyfills(): Promise<void> {
  // 매우 오래된 브라우저 (IE11, 크롬 < 100 등) → 전체 폴리필
  if (!Array.prototype.at || !Object.hasOwn) {
    await import('/dist/polyfills-legacy.js');
    return;
  }

  // 비교적 최신이지만 ES2023~2024 기능 누락 (크롬 110~120, 사파리 16~17.3) → 최소 폴리필
  if (!Array.prototype.toSorted || !Object.groupBy) {
    await import('/dist/polyfills-modern.js');
    return;
  }

  // 최신 브라우저 (크롬 121+, 사파리 17.4+) → 폴리필 불필요, 0바이트
}
```

대부분의 사용자는 세 번째 그룹에 속하므로 추가 다운로드가 없고, 소수의 레거시 사용자만 폴리필을 받는다.

### 2.4 런타임 조건부 로딩 vs 빌드타임 자동화

두 방식은 철학이 다르다. 런타임 방식은 **"브라우저가 실행될 때 판단한다"**, 빌드타임 방식은 **"배포 전에 미리 결정한다"**다.

| 관점 | 런타임 조건부 로딩 | 빌드타임 자동화(`@babel/preset-env`) |
|---|---|---|
| 최신 브라우저 | 폴리필 0바이트, 완벽한 최적화 | IE 타깃 포함 시 불필요한 폴리필까지 다운로드 |
| 레거시 브라우저 | 추가 네트워크 요청으로 지연(파일당 RTT 추가) | 번들에 포함돼 있어 추가 요청 없음 |
| 세밀한 제어 | 사파리 17.3과 17.4를 구분해 제공 가능 | 모든 브라우저에 동일 번들 |
| 업데이트 | 재빌드 없이 폴리필 파일만 교체 가능 | 코드 수정 → 빌드 → 배포 필요 |
| 오버헤드 | 모든 사용자가 기능 감지 로직(수 KB)을 실행 | 없음 |
| 안정성 | 로드 실패 시 앱이 시작 안 될 수 있음(에러 핸들링 필수) | 빌드 시점에 번들 내용이 확정, 예측 가능 |
| 관리 | 폴리필 목록을 개발자가 직접 유지 | 바벨이 코드를 스캔해 자동 결정 |

**런타임 방식을 선택하는 경우**

1. **최신 브라우저 사용자가 대다수(90% 이상)**: 대부분이 0바이트 폴리필 혜택을 본다
2. **초기 번들 크기가 핵심 지표**: SPA·모바일 웹에서 LCP·TTI가 우선일 때
3. **레거시 사용자의 약간의 지연을 비즈니스적으로 감수 가능**
4. **동적 폴리필 관리가 필요**: 국가·디바이스별 분기, A/B 테스트

**빌드타임 방식을 선택하는 경우**

1. **레거시 브라우저 비중이 높음(20% 이상)**: 기업 내부 시스템, 공공기관 사이트
2. **네트워크가 불안정한 환경**: 추가 네트워크 요청 자체가 위험일 때
3. **안정성과 예측 가능성 우선**: 금융·의료·전자상거래처럼 에러가 허용되지 않는 서비스
4. **팀의 빌드 도구 숙련도가 높음**: 설정 한 번으로 전체 파이프라인 자동화

**하이브리드 전략**

실무에서는 두 방식의 조합이 효과적일 때가 많다. **안정화된 기능(ES2015~2022)은 빌드타임에 포함하고, 전환기의 최신 기능(ES2023~2024)만 런타임에 조건부 로드**한다.

```ts
// 빌드타임: @babel/preset-env로 ES2015~2022 폴리필 자동 포함
// browserslist: ["chrome >= 90", "safari >= 14"]

// 런타임: ES2023~2024 최신 기능만 조건부 로딩
async function loadLatestPolyfills(): Promise<void> {
  const polyfills: Promise<unknown>[] = [];

  if (!Object.groupBy) {
    polyfills.push(import('./polyfills/object-groupby.js'));
  }
  if (!Array.fromAsync) {
    polyfills.push(import('./polyfills/array-fromasync.js'));
  }

  await Promise.all(polyfills);
}
```

- 크롬 90~116 사용자: 빌드타임 폴리필만 받아 안정적으로 동작(추가 요청 없음)
- 크롬 117~120 사용자: `Object.groupBy`는 네이티브, `Array.fromAsync`만 동적으로 받음
- 크롬 121+ 사용자: 모든 기능 네이티브, 추가 폴리필 0바이트

> **핵심 통찰**: 어떤 방식을 고르든 근거는 **실제 사용자 데이터**다. 구글 애널리틱스 Browser & OS 리포트, CrUX, RUM에서 브라우저 버전별 사용자 비율·번들 다운로드 시간·LCP/FCP·에러율을 확인한다. "추측하지 말고 측정하라." 그리고 분기마다 재검토한다 - 1년 전에는 런타임 방식이 맞았어도 지금은 빌드타임이 더 적합할 수 있고, 그 반대도 마찬가지다.

## 3. core-js와 폴리필 최적화

`core-js`는 ECMAScript 표준 기능을 폴리필로 제공하는 사실상의 표준 라이브러리다. 문제는 잘못 쓰면 번들에 불필요한 폴리필이 수백 KB씩 들어간다는 점이다. `import 'core-js'`처럼 전체를 임포트하면 코드에서 `Array.fromAsync()`만 써도 `Map`·`Set`·`Symbol` 등 쓰지 않는 폴리필까지 몽땅 번들링된다.

### 3.1 @babel/preset-env의 useBuiltIns 옵션

`useBuiltIns`는 폴리필 포함 방식을 제어하며 세 가지 값을 가진다.

**`false`(기본값)** - 폴리필을 자동으로 추가하지 않는다. 개발자가 직접 임포트해야 하며 관리 책임이 전적으로 개발자에게 있다.

**`entry`** - 진입점의 `import 'core-js/stable'`을 browserslist 설정에 따라 필요한 폴리필로 대체한다.

```json
// .babelrc
{
  "presets": [
    ["@babel/preset-env", {
      "useBuiltIns": "entry",
      "corejs": 3
    }]
  ]
}
```

```ts
// src/index.js (진입점)
import 'core-js/stable';
import 'regenerator-runtime/runtime';
```

바벨이 이 임포트를 타깃 브라우저에 필요한 개별 폴리필 수백 개로 변환한다. **코드에서 실제로 쓰는지와 무관하게** 타깃 브라우저가 지원하지 않는 모든 기능의 폴리필이 포함되므로 비효율적이다.

**`usage`(권장)** - 코드에서 **실제로 사용하는 기능만** 자동으로 폴리필을 추가한다. `core-js`를 명시적으로 임포트할 필요도 없다.

```json
// .babelrc
{
  "presets": [
    ["@babel/preset-env", {
      "useBuiltIns": "usage",
      "corejs": 3
    }]
  ]
}
```

```ts
// src/index.js - core-js 임포트 불필요
const grouped = Object.groupBy(items, (item) => item.category);
const asyncData = await Array.fromAsync(asyncIterator);

// 바벨이 자동으로 다음을 추가:
// import "core-js/modules/es.object.group-by"
// import "core-js/modules/es.array.from-async"
```

크롬 100을 타기팅하더라도 코드에서 두 기능만 쓴다면 **그 두 개의 폴리필만** 번들에 들어간다.

### 3.2 core-js 버전 명시의 중요성

`corejs` 옵션을 생략하면 바벨은 **2018년부터 유지보수가 중단된 core-js 2**를 사용한다. 반드시 3 이상을 명시한다.

```json
{
  "presets": [
    ["@babel/preset-env", {
      "useBuiltIns": "usage",
      "corejs": {
        "version": "3.49",
        "proposals": false
      }
    }]
  ]
}
```

> **실무 팁**: **`corejs: 3`처럼 메이저 버전만 쓰면 3.0.0으로 해석된다.** 그러면 3.0 이후 추가된 폴리필(`Promise.allSettled`, `String.prototype.replaceAll` 등)을 쓸 수 없다. `{version: "3.49"}`처럼 **마이너 버전까지 명시**해야 해당 버전까지의 모든 폴리필이 활성화된다. `package.json`에도 `"core-js": "^3.49.0"`으로 정확한 버전을 맞춘다.

`proposals` 옵션은 아직 표준화되지 않은 제안 단계 기능의 폴리필 포함 여부다. Stage 3 제안도 최종 표준에서 바뀔 수 있으므로 특별한 이유가 없다면 `false`로 유지한다.

### 3.3 폴리필로 구현 불가능한 기능들

일부 저수준 기능은 자바스크립트만으로 네이티브와 동일하게 재현할 수 없다.

- **`Proxy`**: 객체 동작(`get`·`set`·`has`)을 가로채는 메타프로그래밍 기능. 엔진 레벨에서 구현돼야 하므로 폴리필이 불가능하다. **뷰 3가 IE11을 지원하지 않는 이유가 바로 이것이다**(뷰 2는 `Object.defineProperty`, 뷰 3는 `Proxy` 기반).
- **`WeakMap` / `WeakSet`**: 가비지 컬렉션을 방해하지 않는 약한 참조는 자바스크립트로 구현할 수 없다. 폴리필 라이브러리는 일반 `Map`으로 흉내만 내는데 이는 **메모리 누수를 일으킬 수 있다.**
- **`Symbol`**: 문자열이나 객체로 흉내 낼 수는 있지만 진짜 원시 타입이 아니므로 `typeof`가 `'object'`로 나오는 등 알려진 심벌(well-known symbol)이 제대로 작동하지 않는다.
- **Private class fields(`#field`)**: 바벨이 `WeakMap`으로 변환할 수 있지만 `WeakMap` 자체가 폴리필 불가능하므로 구형 브라우저에서는 결국 제한적이다.

이런 기능을 쓸 때 선택지는 둘이다. ① 해당 기능을 네이티브로 지원하는 브라우저만 타기팅하거나, ② 해당 기능을 쓰지 않도록 코드를 작성한다(뷰 2처럼 `Object.defineProperty` 사용 등).

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|---|---|---|
| browserslist를 "혹시 모르니까" 넓게 설정 | 대다수 사용자가 불필요한 폴리필을 다운로드·파싱·실행 | 실사용자 데이터 기반으로 좁히고 분기마다 재검토 |
| `useBuiltIns: 'entry'` 사용 | 코드에서 안 쓰는 기능의 폴리필까지 전부 포함 | `usage`로 전환해 실사용 기능만 포함 |
| `corejs` 옵션 생략 | 유지보수 중단된 core-js 2가 사용됨 | `corejs: {version: "3.49"}` 명시 |
| `corejs: 3`으로 메이저만 명시 | 3.0.0으로 해석되어 이후 추가된 폴리필 사용 불가 | 마이너 버전까지 명시 |
| Polyfill.io 등 외부 폴리필 CDN 사용 | 2024년 공급망 공격 사례처럼 악성 코드 삽입 위험 + 장애 시 서비스 전체 중단 | 자체 호스팅 폴리필 번들 구성 |
| HTML에 폴리필 `<link rel="preload">` 직접 작성 | 모든 브라우저가 다운로드해 조건부 로딩 이점이 사라짐 | 자바스크립트로 조건부 프리로드 |
| `'Set' in window`만으로 기능 감지 | `Set`은 있어도 `union` 등 최신 메서드가 없는 브라우저를 놓침 | 프로토타입 메서드까지 세밀하게 감지 |
| 폴리필 로드 실패 처리 없음 | 네트워크 오류 시 앱이 아예 시작되지 않음 | `try-catch` + 폴백 전략 |
| `Proxy`·`WeakMap` 폴리필을 신뢰 | 엔진 레벨 기능이라 완전 재현 불가, `Map` 흉내는 메모리 누수 유발 | 지원 브라우저만 타기팅하거나 코드에서 회피 |
| 한 번 설정 후 방치 | 브라우저 점유율은 계속 변한다 | `npx update-browserslist-db` 월 1회 + 분기별 타깃 재평가 |

## 측정과 검증

- **`npx browserslist`**: 현재 설정이 타기팅하는 브라우저 목록을 확인한다. browserslist 플레이그라운드에서 쿼리별 점유율도 시각적으로 볼 수 있다.
- **번들 분석 도구**: `webpack-bundle-analyzer`, `source-map-explorer`로 번들에서 `core-js`가 차지하는 크기를 측정한다. 타깃 조정 전후를 비교한다.
- **실사용자 브라우저 분포**: 구글 애널리틱스 Browser & OS 리포트, CrUX, RUM에서 브라우저 버전별 비율을 확인한다. 런타임 vs 빌드타임 의사결정의 근거다.
- **`eslint-plugin-compat`**: 타깃 브라우저에서 지원하지 않는 API 사용을 개발 단계에서 잡아낸다.
- **CI/CD 모니터링**: 폴리필 크기 변화를 파이프라인에서 추적해 의도치 않은 증가를 감지한다.

## 체크리스트

**browserslist 설정 확인**

- [ ] `package.json` 또는 `.browserslistrc`에 타깃 브라우저가 정의돼 있는지 확인
- [ ] `npx browserslist`로 현재 타깃 브라우저 목록 확인
- [ ] 지원 중단할 레거시 브라우저(IE11 등) 제거 검토
- [ ] 실제 사용자 데이터 기반으로 타깃 재평가(구글 애널리틱스, 서버 로그)
- [ ] `> 0.5%, last 2 versions, not dead` 같은 쿼리로 현대적 브라우저 타기팅

**바벨 설정 최적화**

- [ ] `@babel/preset-env` 설치 및 적용 확인
- [ ] `useBuiltIns: 'usage'` 설정으로 사용된 기능만 폴리필 포함
- [ ] core-js 버전 명시(마이너 버전까지)
- [ ] `targets` 설정이 browserslist와 일치하는지 확인
- [ ] 번들 분석 도구로 폴리필 크기 측정

**조건부 폴리필 로딩**

- [ ] 런타임 기능 감지 구현(`Object.groupBy`, `Array.fromAsync` 등)
- [ ] 동적 `import()`로 폴리필 지연 로딩 구현
- [ ] 자체 호스팅 폴리필 번들 준비(외부 CDN 의존성 제거)
- [ ] 폴리필 로딩 실패 시 폴백 전략 수립
- [ ] 개발 환경에서 폴리필 로딩 시뮬레이션 테스트

**지속적 관리**

- [ ] 월 1회 browserslist 데이터베이스 업데이트(`npx update-browserslist-db`)
- [ ] 분기별 타깃 브라우저 재평가 및 조정
- [ ] `core-js`, `@babel/preset-env` 최신 버전 유지
- [ ] 새로운 표준 기능의 브라우저 지원율 추적(caniuse.com)
- [ ] 폴리필 크기 변화를 CI/CD 파이프라인에서 모니터링

## 요약

- 폴리필은 번들 크기뿐 아니라 **파싱·컴파일·실행 시간**까지 잡아먹는다. 저사양 모바일에서는 수백 ms의 낭비다.
- 가장 쉬운 최적화는 **browserslist로 타깃을 좁히는 것**이다. 조건은 OR로 결합되며, 폴리필 양은 목록 길이가 아니라 **가장 낮은 버전**이 결정한다.
- 타깃만큼 **코드에서 쓰는 기능**도 중요하다. `eslint-plugin-compat`으로 타깃 밖 API 사용을 개발 중에 잡는다.
- 조건부 폴리필 로딩은 런타임 기능 감지로 필요한 브라우저에만 폴리필을 보낸다. 최신 브라우저는 0바이트, 레거시는 추가 RTT라는 트레이드오프다.
- **Polyfill.io는 2024년 공급망 공격 이후 금지 대상이다.** 폴리필은 `core-js` 기반으로 자체 호스팅한다.
- 3단계 전략(최신 = 0바이트 / 중간 = 최소 폴리필 / 레거시 = 전체 폴리필)이 실전 기본형이다.
- 런타임 vs 빌드타임 선택 기준: **최신 브라우저 90% 이상이면 런타임**, **레거시 20% 이상·불안정 네트워크·안정성 최우선이면 빌드타임**. 실무에서는 ES2015~2022는 빌드타임, ES2023~2024만 런타임으로 처리하는 **하이브리드**가 효과적이다.
- `@babel/preset-env`는 `useBuiltIns: 'usage'` + `corejs: {version: "3.49"}`(마이너 버전까지)가 정답에 가깝다. `entry`는 안 쓰는 폴리필까지 포함하고, 버전 생략은 죽은 core-js 2를 부른다.
- **`Proxy`·`WeakMap`·`Symbol`·private 필드는 폴리필로 완전 구현이 불가능하다.** 지원 브라우저만 타기팅하거나 코드에서 회피한다(뷰 3가 IE11을 버린 이유).
- 폴리필 최적화는 단발성 작업이 아니다. 분기마다 브라우저 점유율을 재검토하고 "추측하지 말고 측정하라"는 원칙을 지킨다.

## 다른 챕터와의 관계

- **Ch6(async와 defer)**: `<script nomodule>` 패턴으로 모던/레거시 번들을 분기하는 기법이 이 장의 조건부 로딩과 결합된다.
- **Ch9(번들 분석과 불필요한 리소스 제거)**: 폴리필 다이어트가 끝난 뒤의 다음 단계다. 번들 분석기에서 `core-js` 덩어리를 발견하는 것이 보통 이 장으로 돌아오는 계기가 된다.
- **Ch10(코드 스플리팅)**: 폴리필을 별도 청크로 분리하는 빌드 설정이 코드 스플리팅 전략의 일부다.
- **Ch23(서드파티 코드 통제)**: Polyfill.io 공급망 공격 사례는 서드파티 스크립트를 통제해야 하는 이유의 대표적 실례다.
- **Ch25(차세대 웹 표준)**: 새 표준 도입 시 "폴리필 vs 점진적 향상" 판단 기준이 이 장의 기능 감지 전략과 이어진다.
