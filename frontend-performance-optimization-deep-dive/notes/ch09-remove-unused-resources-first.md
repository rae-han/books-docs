# Chapter 9: 트리 셰이킹보다 불필요한 리소스 자체를 없애는 것이 우선이다

## 핵심 질문

번들러가 사용하지 않는 코드를 자동으로 제거해줄 것이라는 기대는 왜 배신당하는가? Coverage로 확인하면 초기 로드의 70~78%가 미사용 코드인 현실에서, 무엇을 먼저 고쳐야 하는가? 트리 셰이킹 설정이 아니라 **코드 작성 단계의 선택**이 번들 크기를 결정한다.

## 1. 번들 분석으로 문제를 가시화하라

번들 크기를 줄이기 전에 가장 먼저 할 일은 현재 상태를 정확히 파악하는 것이다. 어떤 라이브러리가 번들의 대부분을 차지하는지, 실제 사용되는 코드가 얼마인지 모른 채 최적화하면 잘못된 곳에 시간을 낭비한다. 번들 분석은 "보이지 않는 문제"를 "측정 가능한 수치"로 바꾸는 작업이다.

### 1.1 크롬 Coverage로 미사용 코드 비율 측정

1. 크롬 개발자 도구에서 `Cmd+Shift+P`(macOS) / `Ctrl+Shift+P`(윈도우)로 Command Menu 열기
2. "Coverage" 입력 후 **Show Coverage** 선택
3. 패널 하단의 새로고침 버튼 클릭 → 페이지가 리로드되며 코드 사용량 기록
4. 각 파일 옆 빨간색 바 = 사용되지 않는 코드 비율

실제 사례: 한 Next.js 프로젝트의 2MB가 넘는 `_app.js` 파일은 **초기 페이지 로드 시 78%가 사용되지 않았다.** 초기 로딩에 불필요한 컴포넌트·라우트·라이브러리가 모두 메인 번들에 포함돼 있었다는 뜻이다.

> **핵심 통찰**: Coverage 해석 시 주의점 - 초기 로드에는 안 쓰이지만 **특정 기능 사용 시 필요한 코드도 '미사용'으로 표시된다.** 따라서 "이 코드를 삭제하라"가 아니라 **"이 코드를 동적 임포트로 분리할 수 있는가", "이 페이지 렌더링에 정말 필요한가"**를 판단하는 데 써야 한다. Coverage를 켜둔 채 페이지를 탐색하면 기능별 코드 사용 패턴을 파악해 코드 스플리팅 전략을 세울 수 있다.

### 1.2 웹팩 번들 분석기로 번들 구성 파악

Coverage가 코드의 **사용 여부**를 보여준다면, 웹팩 번들 분석기는 번들의 **구성**을 트리맵으로 시각화한다.

```js
// webpack.config.js
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;

module.exports = {
  plugins: [
    new BundleAnalyzerPlugin({
      analyzerMode: 'static',
      reportFilename: 'bundle-report.html',
      openAnalyzer: false,
    }),
  ],
};
```

번들 분석기로 발견할 수 있는 세 가지 대표 문제는 다음과 같다.

1. **예상보다 큰 라이브러리**: moment.js는 약 300KB에 달하며 기본적으로 **모든 로캘 파일**을 포함한다. 실제로는 한국어·영어만 쓰는데도 말이다.
2. **중복된 패키지**: 의존성 이슈로 `lodash@4.17.21`과 `lodash@3.10.1`이 동시에 번들에 들어가는 경우. 서로 다른 라이브러리가 각각 다른 버전을 의존하기 때문이다.
3. **사용하지 않는 라이브러리의 전체 코드 포함**: `import { debounce } from 'lodash'`처럼 쓰면 트리 셰이킹이 작동하지 않아 전체 라이브러리가 포함될 수 있다.

실제 사례로 한 Next.js 앱의 `/login` 라우트는 334KB였는데, recharts의 배럴 엑스포트 문제를 해결하자 **103KB로 231KB 감소**했다. 번들 분석기로 "recharts가 예상보다 크다"는 것을 발견했기에 가능한 최적화였다.

### 1.3 난독화된 번들에서 라이브러리 식별하기

자기 프로젝트가 아니라 경쟁사 벤치마킹, 소스맵 없는 레거시, 외부 사이트 조사에서는 난독화된 코드에서 라이브러리를 알아내야 한다.

**방법 1 - AI에게 물어보기**: 현시점에서 가장 빠르고 정확하다. 난독화·압축된 코드라도 LLM은 패턴을 인식한다. 변수명은 `a`, `b`, `c`로 축약돼도 **API 이름들은 외부 인터페이스라서 원형 그대로 유지**되기 때문이다(예: `AbstractRecoilValue`, `getRecoilValueAsLoadable` 같은 이름으로 Recoil을 식별). AI가 식별했다면 깃허브 저장소 검색이나 `package.json`으로 크로스 체크한다. 단, 사내 라이브러리·마이너 패키지는 식별하지 못할 수 있고 보안상 외부 AI에 코드를 못 보내는 환경도 있다.

**방법 2 - 소스맵 확인**: 소스맵이 있으면 이보다 쉬운 방법이 없다.

```ts
// 크롬 개발자 도구 Console에서
fetch('/static/js/main.abc123.js.map')
  .then((r) => r.json())
  .then((map) => {
    console.log('Sources:', map.sources);
    // ["node_modules/react/index.js", "node_modules/lodash/debounce.js", "src/App.jsx", ...]
  });
```

`map.sources` 배열에 번들에 포함된 모든 파일의 원본 경로가 명시돼 있다. Network 탭에서 JS 파일 응답의 마지막 줄에 `sourceMappingURL` 주석이 있는지 확인하거나 URL에 `.map`을 붙여 직접 접근해본다.

> **실무 팁**: 소스맵은 양날의 검이다. 자기 프로젝트 분석에는 최고지만 **프로덕션에 배포되면 비즈니스 로직·API 엔드포인트·내부 구조가 모두 노출되는 보안 문제**가 된다. 대부분의 프로젝트는 프로덕션 빌드에서 소스맵을 제거한다. 남의 서비스를 분석할 때는 먼저 소스맵부터 확인해보는 것이 순서다.

**방법 3 - 전역 객체 확인**: `Object.keys(window)`에서 `__`로 시작하거나 프레임워크 이름을 포함하는 객체를 찾는다. `window.next.version`(Next.js), `window.__mobxGlobals.version`(MobX), `window['__core-js_shared__']`(core-js), `window.$`(jQuery). 단, lodash·axios 같은 유틸리티 라이브러리는 전역 객체를 만들지 않으므로 프레임워크 식별에만 유용하다.

## 2. 트리 셰이킹이 제대로 작동하지 않는 이유

Next.js·비트는 프로덕션 빌드에서 트리 셰이킹이 기본 활성화돼 있다. 그런데도 Coverage에서 70% 이상이 미사용으로 나온다. 문제는 **트리 셰이킹이 항상 동작하는 '마법'이 아니라는 점**이다. 트리 셰이킹은 정적 분석 기반이라, 분석이 불가능한 패턴을 만나면 안전하게 **"모든 코드를 유지하는" 쪽을 선택**한다.

### 2.1 CommonJS는 트리 셰이킹할 수 없다

ESModule은 정적 구조를 가져서 번들러가 빌드 타임에 어떤 export가 사용되는지 분석할 수 있다. 반면 CommonJS는 런타임에 동작한다.

```js
// ❌ CommonJS - module.exports 객체가 런타임에 생성됨
module.exports = {
  add: (a, b) => a + b,
  subtract: (a, b) => a - b,
  multiply: (a, b) => a * b,
  divide: (a, b) => a / b,
};

const utils = require('./utils');
console.log(utils.add(1, 2));
// utils[someVariable] 같은 동적 접근이 가능하므로
// 번들러는 어떤 프로퍼티가 쓰일지 미리 알 수 없다 → 전부 유지
```

```ts
// ✅ ESModule - import { add }가 빌드 타임에 "add만 사용"을 선언
export const add = (a: number, b: number) => a + b;
export const subtract = (a: number, b: number) => a - b;

import { add } from './utils';
console.log(add(1, 2));
// subtract, multiply, divide는 번들에서 제거됨
```

대표적인 실전 사례가 lodash다.

```ts
// ❌ 트리 셰이킹 불가능 - CommonJS 패키지, 전체 약 67KB 포함
import _ from 'lodash';
const debounced = _.debounce(fn, 300);

// ✅ 트리 셰이킹 가능 - ESModule 패키지, debounce만 약 2KB
import debounce from 'lodash-es/debounce';
const debounced = debounce(fn, 300);
```

**패키지의 모듈 시스템 확인법**

- 파일 확장자: `.mjs`는 항상 ESModule, `.cjs`는 항상 CommonJS. `.js`는 `package.json`의 `"type"` 필드에 따라 달라진다.
- `package.json` 필드:

```json
{
  "type": "module",                  // .js 파일을 ESModule로 취급 (기본값은 commonjs)
  "main": "dist/index.js",           // CommonJS 진입점
  "module": "dist/index.esm.js",     // ESModule 진입점 (번들러가 main보다 우선 확인)
  "exports": {
    ".": {
      "import": "./dist/index.mjs",  // import 시
      "require": "./dist/index.js"   // require 시
    }
  }
}
```

- 파일 내용 직접 확인: `export`/`import`/`import.meta`면 ESModule, `module.exports`/`require()`면 CommonJS. **`package.json` 필드가 잘못 설정된 패키지도 많으므로** 번들 분석 도구로 실제 트리 셰이킹 작동을 확인하는 것이 가장 확실하다.

번들러가 ESModule을 우선하도록 설정할 수도 있다.

```js
// webpack.config.js
module.exports = {
  resolve: {
    mainFields: ['module', 'main'],
  },
};
```

### 2.2 사이드 이펙트가 있으면 제거할 수 없다

트리 셰이킹이 작동하려면 "이 코드를 제거해도 동작이 변하지 않는다"는 확신이 필요하다. **사이드 이펙트**(함수 외부 상태를 변경하는 모든 동작)가 이 확신을 깨뜨린다.

```ts
// 사이드 이펙트 예시
console.log('Module loaded');                        // 콘솔 출력
window.myGlobal = 'value';                           // 전역 변수 수정
Array.prototype.myMethod = function () {};           // 프로토타입 수정
import './styles.css';                               // CSS 파일 로드
```

모듈 레벨에서 실행되는 코드는 함수가 호출되지 않아도 실행돼야 하므로 번들러가 제거할 수 없다. 객체 게터처럼 감지하기 어려운 사이드 이펙트도 있다.

**해결 방법**

```ts
// ❌ Before: 모듈 레벨에서 실행 - 임포트하는 순간 무조건 실행
import { initAnalytics } from './analytics';
initAnalytics();

export function myFunction() { /* ... */ }

// ✅ After: 명시적 호출 - 호출되지 않으면 모듈 전체 제거 가능
export function myFunction() { /* ... */ }
export function init() {
  initAnalytics();
}
```

CSS 임포트도 마찬가지다. 라이브러리 진입점에서 CSS를 임포트하면 함수 하나만 써도 모든 CSS가 포함된다. **실제로 스타일이 필요한 컴포넌트 레벨로 옮긴다.**

라이브러리를 개발한다면 `package.json`에 `sideEffects` 필드를 명시한다.

```json
{ "sideEffects": false }
```

```json
{ "sideEffects": ["**/*.css", "./src/polyfills.js"] }
```

`false`는 "이 패키지의 모든 파일에 사이드 이펙트가 없다"는 선언으로, 번들러가 이를 신뢰하고 더 적극적으로 트리 셰이킹한다.

### 2.3 동적 참조는 정적 분석이 불가능하다

자바스크립트는 동적 언어라서 런타임에 결정되는 패턴이 많고, 번들러는 이런 패턴을 만나면 안전하게 모든 코드를 유지한다.

```ts
// ❌ 동적 프로퍼티 접근 - functionName이 무엇일지 빌드 타임에 알 수 없음
const functionName = getUserInput();
const result = utils[functionName]('hello');
// utils 객체의 모든 메서드가 번들에 포함됨
```

클래스도 마찬가지다. `validator[`validate${fieldType}`]` 같은 동적 메서드 호출이 가능하므로 클래스 메서드를 공격적으로 트리 셰이킹할 수 없다. `validateEmail`만 써도 `validatePhone`, `validateUrl`이 함께 들어간다.

```ts
// ❌ 변수를 통한 간접 참조 - 어떤 모듈이 로드될지 알 수 없음
const moduleName = isProduction ? './prod' : './dev';
const config = require(moduleName);

// ✅ 조건문은 동적이지만 각 분기의 경로는 정적 → 분석 가능
const config = isProduction ? require('./prod') : require('./dev');
```

동적 플러그인 로딩(`` require(`./plugins/${name}`) ``)을 만나면 웹팩은 **`plugins/` 디렉터리의 모든 파일**을 번들에 포함시킨다.

**해결책은 동적 참조를 정적 맵으로 변환하는 것이다.**

```ts
// ✅ 정적 맵 - 사용되지 않는 플러그인은 트리 셰이킹으로 제거됨
import { formatPlugin } from './plugins/format';
import { validatePlugin } from './plugins/validate';
import { transformPlugin } from './plugins/transform';

const plugins = {
  format: formatPlugin,
  validate: validatePlugin,
  transform: transformPlugin,
};

class PluginSystem {
  loadPlugin(name: keyof typeof plugins) {
    return plugins[name];
  }
}
```

동적 임포트를 완전히 없앨 수 없다면 **명시적 분기**로 범위를 제한한다.

```ts
// ❌ 범위가 너무 넓음 - locales 디렉터리의 모든 파일 포함
import(`./locales/${lang}.json`);

// ✅ 명시적 분기 - 정확히 세 파일만 포함되도록 보장
let localeData;
switch (lang) {
  case 'en': localeData = await import('./locales/en.json'); break;
  case 'ko': localeData = await import('./locales/ko.json'); break;
  case 'ja': localeData = await import('./locales/ja.json'); break;
}
```

허용 목록 **검증**만으로는 부족하다. 검증을 통과해도 여전히 모든 파일이 번들에 포함되기 때문이다. 라이브러리 선택 시점에도 이를 고려한다 - i18next는 동적 로딩을 많이 써서 트리 셰이킹이 어렵고, react-intl은 정적 임포트를 권장해 더 잘 작동한다.

### 2.4 배럴 엑스포트가 너무 깊으면 번들러가 분석을 포기한다

배럴 엑스포트(barrel export)는 여러 모듈을 하나의 진입점(`index.js`)으로 모아 다시 엑스포트하는 패턴이다. 얕은 단계에서는 ESModule + `sideEffects: false`면 트리 셰이킹이 작동하지만, **중첩이 깊어지면 번들러가 정적 분석을 포기하고 모든 코드를 포함시킨다.**

```ts
// components/forms/index.js
export { Input } from './Input';
export { Textarea } from './Textarea';

// components/index.js
export * from './forms';
export * from './buttons';
export * from './modals';

// 사용하는 곳 - Input 하나를 위해 번들러가 전체 의존성 트리를 분석해야 함
import { Input } from './components';
```

Next.js 팀 테스트에 따르면 일부 라이브러리의 진입점 배럴 파일에는 **최대 10,000개의 re-export**가 있고, 100,000개 이상의 파일을 가진 모듈에서는 컴파일에 약 30초가 걸렸다. 이 깊이에서는 번들러가 완벽한 정적 분석을 못 하고 안전을 위해 더 많은 코드를 포함시킨다. 실제로 한 프로젝트에서는 **recharts를 어디에서도 사용하지 않았는데도** 중첩 배럴 엑스포트 때문에 번들에 포함됐다.

**배럴 엑스포트 제거 전후 라우트별 번들 크기** (실측)

| 라우트 | Before | After | 감소량 |
|---|---|---|---|
| /login | 334KB | 103KB | -231KB |
| /memos | 470KB | 339KB | -131KB |
| /setting | 422KB | 266KB | -156KB |

**해결 방법**

```ts
// ❌ 배럴 엑스포트 사용
import { Button, Input } from './components';

// ✅ 직접 임포트 - 번들러가 정확히 어떤 파일이 필요한지 즉시 알 수 있음
import { Button } from './components/Button';
import { Input } from './components/Input';
```

기존 코드 수정이 부담스럽다면 Next.js 13.5+의 `optimizePackageImports`가 배럴 임포트를 자동으로 직접 임포트로 변환한다.

```js
// next.config.js
module.exports = {
  experimental: {
    optimizePackageImports: ['@mui/material', '@mui/icons-material'],
  },
};
```

라이브러리 개발자라면 `package.json`의 `exports` 필드로 명시적 진입점을 제공한다(`"./Button": "./dist/Button.js"`).

> **실무 팁 - 모노레포**: 내부 패키지의 `main`이 `src/index.ts` 같은 **소스코드를 직접 가리키면** 배럴 엑스포트 문제가 그대로 전달되고 트리 셰이킹이 작동하지 않는다. 내부 패키지도 빌드를 거쳐 `dist/index.js`(+ `module`·`exports` 필드)를 제공해야 한다.

## 3. 네이티브 API로 대체하거나 가벼운 대안을 선택하라

브라우저는 이미 강력한 API를 제공한다. 문제는 라이브러리가 제공하는 기능의 10%도 안 쓰면서 수십 KB를 번들에 넣는 경우다. **네이티브 API는 번들 크기가 0이고, 트리 셰이킹·모듈 시스템 걱정도 없다.**

| 라이브러리 | 번들 크기 | 네이티브 대안 | 비고 |
|---|---|---|---|
| axios | 14.5KB(gzip) | `fetch()` | 기본 HTTP 요청은 fetch로 충분. 인터셉터가 필요하면 래퍼 함수 작성 |
| moment.js | 약 300KB(gzip 약 70KB) | `Intl.DateTimeFormat`, `Intl.RelativeTimeFormat` | **moment 팀도 사용 중단 권장.** 날짜 계산이 필요하면 dayjs(3KB) 등 |
| lodash | 70KB | 네이티브 배열/객체 메서드 | `map`·`filter`·`find`·스프레드로 대부분 대체 가능 |
| qs, query-string | 6~8KB | `URLSearchParams` | 기본 쿼리스트링 파싱은 네이티브로 충분 |
| uuid | 3KB | `crypto.randomUUID()` | UUID v4만 필요하면 네이티브(크롬 92+, Node 14.17+) |
| classnames | 1KB | 템플릿 리터럴 | `` `${condition ? 'class1' : ''} ${class2}` `` |
| date-fns | 18KB(gzip) | `Intl` API | 포매팅만 필요하면 Intl로 충분. 계산 로직이 많으면 유지 |

```ts
// moment.js 사용 (약 300KB)
import moment from 'moment';
const formatted = moment().format('YYYY년 M월 D일');
const relative = moment().fromNow();

// Intl API 사용 (0KB)
const formatter = new Intl.DateTimeFormat('ko-KR', {
  year: 'numeric',
  month: 'long',
  day: 'numeric',
});
const formatted = formatter.format(new Date()); // "2025년 1월 15일"

const rtf = new Intl.RelativeTimeFormat('ko-KR', { numeric: 'auto' });
const relative = rtf.format(-3, 'hour'); // "3시간 전"
```

```ts
// lodash 체이닝
const result = _.chain(users).filter((u) => u.age > 20).map((u) => u.name).uniq().value();

// 네이티브 메서드 (0KB)
const result = [...new Set(users.filter((u) => u.age > 20).map((u) => u.name))];
```

네이티브로 완전 대체가 어렵거나 마이그레이션이 부담스럽다면 **ESModule 기본 + 트리 셰이킹이 잘 작동하는 경량 대안**을 쓴다.

- **lodash → es-toolkit**: lodash 호환 API를 제공하면서 번들 크기가 96% 작다. `sample` 함수가 lodash는 2,000바이트, es-toolkit은 88바이트. 성능도 최대 11.8배 빠른 경우가 있다. 기존 lodash를 유지해야 한다면 최소한 개별 임포트(`lodash/debounce`)로 전체 포함을 막는다.
- **moment.js → dayjs 또는 date-fns**: dayjs는 moment와 거의 동일한 API에 단 3KB. date-fns는 함수 하나하나가 독립 모듈이라 트리 셰이킹이 매우 잘 작동한다.
- **axios → ky**: fetch 기반 경량 HTTP 클라이언트(5KB). 자동 재시도·타임아웃 같은 편의 기능을 제공하며, 완전한 네이티브 fetch로 가기 전 중간 단계로 적합하다.

> **핵심 통찰**: 새 라이브러리를 설치하기 전에 세 가지를 확인한다. ① **브라우저 네이티브 API로 대체 가능한가**(MDN 검색), ② **ESModule을 지원하는가**(`"type": "module"` 또는 `"module"` 필드), ③ **트리 셰이킹이 작동하는가**(`"sideEffects": false` + 실제 번들 크기). **라이브러리를 설치하는 것은 쉽지만 나중에 제거하는 것은 어렵다.**

## 4. 같은 라이브러리가 두 번 설치돼 있다

번들 분석기에서 같은 라이브러리가 여러 버전으로 보이는 것은 npm의 의존성 해소 알고리즘에서 비롯된다. `package-a`가 `lodash@^4.0.0`, `package-b`가 `lodash@^3.0.0`을 요구하면 npm은 두 버전을 모두 설치한다. 호환성을 위한 안전한 선택이지만 번들 관점에서는 낭비다. 더 교묘하게는 **semver 범위 내에서도** 설치 순서나 락파일 상태에 따라 4.17.21과 4.16.6이 동시에 설치될 수 있다.

### 4.1 npm ls로 중복 찾아내기

```bash
npm ls lodash
```

```
my-app@1.0.0
├── lodash@4.17.21
├─┬ package-a@1.0.0
│ └── lodash@3.10.1          ← ⚠ 중복 발생!
└─┬ package-b@2.0.0
  └── lodash@4.17.21 deduped ← 최상위 lodash 재사용
```

핵심은 `deduped` 키워드다. package-b는 최상위와 같은 버전을 요구하므로 npm이 자동으로 중복을 제거했고, package-a는 메이저 버전이 달라 별도로 설치됐다. `--all`로 전체 중첩 의존성을, `--depth=2`로 깊이를 제한해 볼 수 있다. pnpm은 `pnpm list lodash`, yarn은 `yarn why lodash`(어떤 패키지 때문에 설치됐는지 이유를 표시)를 쓴다.

> **실무 팁**: pnpm은 하드 링크로 디스크 공간을 절약하지만 **번들러는 심볼릭 링크를 따라가 실제 파일을 읽으므로 서로 다른 버전은 여전히 번들에 중복 포함된다.** 디스크 절약 ≠ 번들 절약이다.

중복 발생의 세 가지 패턴: ① **레거시 의존성**(오래된 라이브러리가 구버전을 요구), ② **좁은 semver 범위**(정확한 버전 고정과 범위 지정이 섞임), ③ **전이적 의존성의 중복**(간접 의존성에서 발생 - 가장 흔함).

### 4.2 dedupe로 중복 제거

```bash
npm dedupe
```

두 패키지가 공통으로 만족할 수 있는 버전이 있으면 최상위로 끌어올려(hoisting) 중복을 제거한다. 단, **semver 범위 내에서만** 작동한다.

- **서로 다른 메이저 버전은 제거할 수 없다**: `lodash@3.x`와 `lodash@4.x`는 호환되지 않으므로 dedupe가 통합하지 못한다.
- **정확한 버전(4.17.15)이 명시된 경우도 교체하지 않는다**: 의도적 고정으로 간주한다.

### 4.3 resolutions/overrides로 버전 강제

dedupe로 해결되지 않으면 버전을 강제로 통일한다. yarn은 `resolutions`, npm은 `overrides`, pnpm은 `pnpm.overrides` 필드를 쓴다.

```json
{
  "overrides": {
    "lodash": "4.17.21"
  }
}
```

특정 패키지의 의존성만 강제하는 세밀한 제어도 가능하다.

```json
{
  "overrides": {
    "package-a": {
      "lodash": "4.17.21"
    }
  }
}
```

**세 가지 주의사항**

1. **하위 호환성을 깨는 강제는 금물.** 메이저 버전이 바뀌면 API가 달라진다(lodash 3.x의 `_.pluck`은 4.x에서 `_.map`으로 변경 → 강제하면 프로덕션에서 `TypeError: _.pluck is not a function`). **패치·마이너 버전 통일에만** 안전하다.
2. **타입 정의 충돌 주의.** `@types/react@17.x`를 리액트 18과 강제 조합하면 새 타입이 없어 에러가 나고, 반대 조합은 존재하지 않는 타입을 참조한다. 타입 패키지는 실제 라이브러리 버전과 반드시 일치시킨다.
3. **근본 해결은 라이브러리 업데이트다.** overrides는 임시 우회책이다. 의존 패키지가 구버전을 요구하는 것이 진짜 문제이므로, 저장소에 이슈를 제기하거나 유지보수가 끊긴 라이브러리는 대안으로 마이그레이션한다.

overrides 적용 후에는 **반드시 전체 테스트 스위트를 실행**한다. 런타임 API 변경은 타입 체크로 잡히지 않는다.

### 4.4 peerDependencies 충돌 해결

`peerDependencies`는 "이 패키지를 쓰려면 특정 패키지가 프로젝트에 설치돼 있어야 한다"는 선언이다. 리액트 컴포넌트 라이브러리가 리액트를 `dependencies`에 넣지 않는 이유는 **프로젝트와 라이브러리가 서로 다른 리액트를 번들에 포함하는 것을 막기 위해서**다.

리액트 19 프로젝트에 리액트 16.8.5~18만 지원하는 react-beautiful-dnd를 설치하려 하면 npm v7+가 `ERESOLVE` 에러로 설치를 거부한다. 이때 많은 개발자가 `--legacy-peer-deps`로 강제 설치하는데, **이는 명백히 잘못된 접근이다.**

강제 설치가 일으키는 문제:

- **번들 크기 증가**: 호환되지 않는 조합이 설치되어 리액트(약 130KB gzip)가 번들에 두 번 들어갈 위험
- **런타임 에러**: `Error: Invalid hook call.` - 리액트는 전역 상태를 유지하는데 두 개의 리액트가 있으면 훅이 올바른 인스턴스를 찾지 못한다. **타입 체크로 잡히지 않고**, 로컬에서는 잘 되다가 프로덕션의 특정 사용자 플로에서만 터져 디버깅이 매우 어렵다.
- **API 호환 불일치**: 라이브러리가 리액트 18의 `useSyncExternalStore`를 내부에서 쓰는데 프로젝트가 17이면 해당 API가 없어 런타임 에러

**올바른 해결**

1. **프로젝트 버전을 라이브러리에 맞춘다**: 라이브러리가 호환성을 추가할 때까지 리액트 18 유지가 가장 안전
2. **대안 라이브러리로 마이그레이션**: react-beautiful-dnd는 공식 폐기 상태 → `@dnd-kit`(리액트 19 지원)으로 교체

**예방책**: ① 설치 전 `npm view <package> peerDependencies`로 호환성 확인, ② `npm outdated`로 정기 점검 + 폐기 패키지 즉시 교체, ③ 메이저 프레임워크 업그레이드는 생태계가 따라올 때까지 기다린 후 진행.

## 5. 번들 최적화 우선순위 전략

모든 문제를 한 번에 해결할 수 없으므로 우선순위를 정해 단계적으로 접근한다.

1. **크기 대비 사용률이 낮은 라이브러리** (최우선): Coverage 사용률 30% 미만 + 번들 분석기에서 100KB 이상 → 투입 대비 효과 최대. moment.js → dayjs/Intl, lodash 전체 → 개별 임포트/직접 구현, 관리자용 chart.js → 동적 임포트 분리.
2. **중복 패키지 제거**: `npm ls` → `npm dedupe` → 필요 시 overrides(마이너/패치만) → peerDependencies 정렬. 한 번 해결하면 지속 효과가 있어 우선순위가 높다.
3. **트리 셰이킹 최적화**: CommonJS·배럴 엑스포트·`sideEffects` 설정을 점검한다. 즉각 효과는 크지 않아도 이후 추가되는 코드에서 자동으로 불필요한 부분이 제거되므로 장기 효과가 크다.
4. **코드 스플리팅과 지연 로딩**: 초기 로드에 안 쓰이는 코드(관리자 패널·대시보드)를 동적 임포트로 분리. 단, 과도하면 HTTP 요청 증가·캐싱 효율 저하가 있으므로 청크 크기와 사용 빈도를 고려한다(Ch10).

> **핵심 통찰**: 번들 분석은 일회성이 아니라 **지속적인 작업**이다. CI/CD에 번들 분석기를 통합해 PR마다 크기 변화를 자동 확인하고, 10% 이상 증가 시 경고를 띄운다. "번들이 크다"는 막연한 느낌이 아니라 **"`_app.js`의 78%가 미사용", "moment.js가 300KB", "lodash가 두 버전"**처럼 구체적 사실을 파악하고, "번들 50% 감축" 같은 막연한 목표 대신 **"moment.js 제거로 298KB 절감"**처럼 측정 가능한 목표를 세운다. 실제 프로젝트들에서 번들 최적화는 LCP 0.5~1초, TTI 1~2초 개선으로 이어졌다 - 숫자를 위한 최적화가 아니라 사용자 경험을 위한 최적화다.

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|---|---|---|
| 번들러가 알아서 최적화해줄 것이라 신뢰 | 트리 셰이킹은 CommonJS·사이드 이펙트·동적 참조 앞에서 무력화됨 | 코드 작성 단계에서 트리 셰이킹 친화적 패턴 선택 |
| `import _ from 'lodash'` 전체 임포트 | CommonJS 패키지라 전체 67KB가 번들에 포함 | `lodash-es` 개별 임포트 또는 es-toolkit |
| 라이브러리 진입점에서 CSS 임포트 | 함수 하나만 써도 모든 CSS가 번들에 포함 | 사용하는 컴포넌트 레벨로 CSS 임포트 이동 |
| `` import(`./locales/${lang}.json`) `` | 디렉터리의 모든 파일이 번들에 포함 | 명시적 `switch` 분기로 범위 제한 |
| 중첩 배럴 엑스포트(`export * from`) 남용 | 번들러가 분석을 포기하고 미사용 라이브러리까지 포함 | 직접 임포트 또는 `optimizePackageImports` |
| 모노레포 내부 패키지의 `main`이 `src/index.ts` | 소스 직접 참조로 배럴 문제가 그대로 전달됨 | 빌드 결과물(`dist/`) + `module`·`exports` 필드 제공 |
| Coverage의 미사용 코드를 무조건 삭제 | 특정 기능에서 쓰이는 코드도 초기 로드 기준 '미사용'으로 표시됨 | 삭제가 아니라 동적 임포트 분리 후보로 판단 |
| 메이저 버전을 overrides로 강제 통일 | API 변경으로 프로덕션 런타임 에러(`_.pluck` 사례) | 패치·마이너 통일만, 메이저는 라이브러리 업데이트로 |
| `--legacy-peer-deps`로 강제 설치 | 리액트 중복 포함 + `Invalid hook call` 런타임 에러(타입 체크로 못 잡음) | 버전을 맞추거나 대안 라이브러리로 마이그레이션 |
| 프로덕션에 소스맵 배포 | 비즈니스 로직·API 엔드포인트·내부 구조 전부 노출 | 프로덕션 빌드에서 소스맵 제거 |
| 설치 전 크기 확인 없이 `npm install` | 나중에 제거하기 훨씬 어려움 | bundlephobia.com + `npm view` peerDependencies 확인 습관 |

## 측정과 검증

- **크롬 Coverage**: 초기 로드 시 미사용 코드 비율 측정. 페이지 탐색을 이어가며 기능별 코드 사용 패턴도 파악한다.
- **웹팩 번들 분석기**: 트리맵으로 번들 구성 시각화. 예상보다 큰 라이브러리, 중복 패키지, 의도치 않은 의존성을 찾는다.
- **`npm ls <패키지>` / `yarn why` / `pnpm list`**: 중복 설치와 그 원인(어떤 패키지가 요구하는지) 추적.
- **`npm view <패키지> peerDependencies`**: 설치 전 호환성 확인.
- **bundlephobia.com**: 설치 전 패키지 크기·트리 셰이킹 지원 여부 확인.
- **CI/CD 통합**: PR마다 번들 크기 변화 리포트 자동 생성, 임곗값 초과 시 경고. "어느 순간 번들이 커졌는데 원인을 모르겠다"를 방지한다.

## 체크리스트

**번들 분석**

- [ ] 크롬 Coverage로 초기 로드 시 미사용 코드 비율 측정
- [ ] 웹팩 번들 분석기로 번들 구성 시각화, 가장 큰 패키지 파악
- [ ] 사용률 30% 미만 + 100KB 이상 패키지 파악
- [ ] 예상치 못한 의존성이나 중복 패키지 확인

**트리 셰이킹 최적화**

- [ ] 전체 임포트 대신 개별 함수 임포트(`lodash/debounce`)
- [ ] 배럴 엑스포트 사용 패턴 확인 및 개선
- [ ] `package.json`의 `sideEffects` 필드 설정 확인
- [ ] CommonJS 모듈 사용 여부 확인, ESModule 전환 검토

**네이티브 API 활용**

- [ ] axios → fetch API 교체 가능 여부 검토
- [ ] moment.js → dayjs 또는 Intl API 교체 검토
- [ ] lodash 사용 패턴 분석 후 네이티브 메서드/직접 구현 대체 확인
- [ ] 브라우저 지원 범위 확인 후 폴리필 제거 가능 여부 검토

**중복 패키지 제거**

- [ ] `npm ls`로 중복 설치 패키지 확인
- [ ] `npm dedupe`로 자동 해결 가능한 중복 제거
- [ ] resolutions/overrides로 마이너/패치 버전 통일(메이저는 강제하지 않기)
- [ ] peerDependencies 충돌 확인 및 버전 정렬
- [ ] 폐기된 패키지 확인 후 대안으로 마이그레이션

**우선순위 및 지속 관리**

- [ ] 크기 대비 사용률 낮은 패키지부터 최적화
- [ ] 구체적이고 측정 가능한 목표 설정(예: "moment.js 제거로 298KB 절감")
- [ ] CI/CD에 번들 크기 변화 모니터링 추가
- [ ] PR마다 번들 크기 변화 리포트 자동 생성
- [ ] 새 라이브러리 추가 시 `npm view` + bundlephobia.com으로 크기 확인
- [ ] 정기 번들 분석 일정 수립(월 1회 또는 분기 1회)

## 요약

- 번들 최적화의 진짜 문제는 번들러 설정이 아니라 **코드 작성 단계의 선택**이다. 트리 셰이킹은 마법이 아니며 분석 불가능한 패턴을 만나면 "전부 유지"를 선택한다.
- 최적화의 시작은 **측정**이다. Coverage(사용 여부) + 번들 분석기(구성)로 "78%가 미사용", "moment가 300KB" 같은 구체적 사실을 만든다.
- 난독화된 번들의 라이브러리 식별은 **AI 패턴 인식 → 소스맵 확인 → 전역 객체 확인** 순서로 접근한다. 식별 결과는 깃허브 크로스 체크로 검증한다.
- 트리 셰이킹을 방해하는 4대 원인: **① CommonJS**(런타임 구조라 정적 분석 불가 - `lodash` vs `lodash-es`), **② 사이드 이펙트**(모듈 레벨 실행 코드·CSS 임포트 - 함수로 감싸고 `sideEffects` 필드 명시), **③ 동적 참조**(`utils[name]`·`` require(`./x/${n}`) `` - 정적 맵과 명시적 분기로 변환), **④ 깊은 배럴 엑스포트**(직접 임포트 또는 `optimizePackageImports`).
- **네이티브 API는 번들 0KB다.** fetch·Intl·URLSearchParams·crypto.randomUUID가 axios·moment·qs·uuid를 대체한다. 어렵다면 es-toolkit·dayjs·ky 같은 ESModule 경량 대안을 쓴다.
- 새 라이브러리 설치 전 3문: 네이티브로 가능한가 / ESModule인가 / 트리 셰이킹이 되는가. **설치는 쉽지만 제거는 어렵다.**
- 중복 패키지는 `npm ls`로 찾고(핵심 키워드 `deduped`), `dedupe`(semver 범위 내) → overrides(패치·마이너만) 순으로 해결한다. pnpm의 디스크 절약은 번들 절약이 아니다.
- **peerDependencies 충돌을 `--legacy-peer-deps`로 우회하지 않는다.** 리액트 중복 포함과 `Invalid hook call` 런타임 에러라는 시한폭탄이다. 버전을 맞추거나 대안으로 마이그레이션한다.
- 우선순위: **저사용·대용량 라이브러리 → 중복 제거 → 트리 셰이킹 → 코드 스플리팅.** CI/CD 모니터링으로 지속 관리하며, 결과는 LCP 0.5~1초·TTI 1~2초 개선으로 나타난다.

## 다른 챕터와의 관계

- **Ch8(폴리필)**: 번들 다이어트의 1단계가 폴리필이었다면 이 장은 2단계(라이브러리·코드)다. 번들 분석기에서 core-js 덩어리가 보이면 Ch8로, 라이브러리 덩어리가 보이면 이 장으로 온다.
- **Ch10(코드 스플리팅)**: 이 장의 4순위 전략(초기 로드에 불필요한 코드의 동적 임포트 분리)을 전면적으로 다룬다. Coverage가 스플리팅 지점을 찾는 도구가 된다.
- **Ch11(서버로 로직 이동)**: "이 코드가 클라이언트에 있어야 하는가"라는 더 근본적인 질문으로 확장된다. 무거운 라이브러리를 서버로 옮기면 번들에서 아예 사라진다.
- **Ch18(자바스크립트 실행 최적화)**: 번들 크기는 다운로드뿐 아니라 파싱·컴파일·실행 시간의 문제이기도 하다. 줄인 번들이 메인 스레드 부담 감소로 이어진다.
- **Ch23(서드파티 코드 통제)**: 자사 번들이 아닌 서드파티 스크립트의 크기·영향 통제를 다룬다.
