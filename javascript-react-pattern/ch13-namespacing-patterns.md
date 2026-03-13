# Chapter 13: Namespacing Patterns (네임스페이스 패턴)

## 핵심 질문

> 자바스크립트에서 네임스페이스는 어떤 문제를 해결했으며, ES Modules 시대에도 네임스페이스 개념은 여전히 필요한가?

---

## 1. 네임스페이스의 필요성과 역사

### 전역 스코프 오염 문제

네임스페이스(*Namespace — 코드 단위를 고유한 식별자로 그룹화한 것*)는 자바스크립트에서 가장 오래된 구조적 문제 중 하나인 **전역 스코프 오염**을 해결하기 위해 등장했다. 자바스크립트는 C++, Java, Python과 달리 언어 차원의 네임스페이스 기능을 기본 제공하지 않았다. 모든 `<script>` 태그는 동일한 전역 스코프를 공유하기 때문에, 서로 다른 스크립트가 같은 이름의 변수나 함수를 정의하면 **충돌**이 발생했다.

```html
<!-- 2010년대 전형적인 웹 페이지 -->
<script src="jquery.min.js"></script>
<script src="analytics.js"></script>      <!-- window.track 정의 -->
<script src="ad-tracker.js"></script>     <!-- window.track 덮어씀! -->
<script src="app.js"></script>
```

이 문제는 단순히 변수명을 신중하게 짓는 것으로 해결되지 않았다. 서드파티 라이브러리가 늘어나고 애플리케이션이 복잡해질수록 이름 충돌 가능성은 기하급수적으로 높아졌다.

### `<script>` 태그 시대의 한계

ES Modules 이전의 자바스크립트에는 파일 단위의 스코프 격리가 없었다. 개발자들은 이 한계를 극복하기 위해 **객체와 클로저를 활용한 네임스페이스 패턴**을 고안했다. jQuery, YUI, Dojo, Google Closure 같은 라이브러리들은 각각 고유한 네임스페이스 전략을 사용했다.

> **핵심 통찰**: 이 장에서 다루는 전통적 네임스페이스 패턴들은 대부분 **ES Modules가 해결한 문제를 수동으로 우회하던 기법**이다. 역사적 맥락을 이해하면 현재 모듈 시스템의 설계 의도를 더 깊이 파악할 수 있다.

---

## 2. 전통적 네임스페이스 패턴

아래 패턴들은 ES Modules 이전 시대의 해결책이다. 각 패턴의 코드, 장단점, 그리고 **2026년 현재의 관점**을 함께 정리한다.

### 2.1 단일 전역 변수 (Single Global Variable)

하나의 전역 변수를 주요 참조 객체로 사용하는 방식이다. IIFE(*Immediately Invoked Function Expression — 정의 직후 즉시 실행되는 함수 표현식*)가 함수와 속성을 가진 객체를 반환하고, 이를 단일 변수에 할당한다.

```typescript
const myApp = (() => {
  const privateKey = "secret";

  function doSomething(): string {
    return `Processing with ${privateKey}`;
  }

  return {
    doSomething,
  };
})();

// 사용
myApp.doSomething();
```

| 장점 | 단점 |
|------|------|
| 전역 변수를 하나로 제한 | 다른 개발자가 같은 이름을 사용할 가능성 |
| IIFE로 private 멤버 구현 가능 | 대규모 앱에서 하나의 객체에 모든 것이 집중됨 |

**현대적 평가**: ES Modules의 `export`/`import`가 이 패턴을 완전히 대체한다. 파일 자체가 스코프이므로 IIFE로 감쌀 필요가 없다.

### 2.2 접두사 네임스페이스 (Prefix Namespace)

피터 미쇼(*Peter Michaux*)가 제안한 패턴으로, 고유한 접두사를 모든 식별자 앞에 붙이는 방식이다.

```typescript
const myApp_users: string[] = [];
const myApp_maxRetries: number = 3;

function myApp_fetchData(url: string): Promise<Response> {
  return fetch(url);
}

function myApp_formatDate(date: Date): string {
  return date.toISOString();
}
```

| 장점 | 단점 |
|------|------|
| 구현이 매우 단순 | 접두사가 같은 전역 변수가 대량 생성됨 |
| 이름 충돌 가능성 감소 | 코드 가독성이 크게 저하됨 |
| | 접두사 자체가 충돌할 가능성 존재 |

**현대적 평가**: 완전히 **폐기된 패턴**이다. 현대 코드베이스에서 이 패턴을 사용하는 경우는 없으며, CSS에서의 BEM 네이밍이나 환경 변수(`REACT_APP_`, `VITE_`)의 접두사 관례 정도만 유사한 형태로 남아 있다.

### 2.3 객체 리터럴 표기법 (Object Literal Notation)

키-값 쌍으로 이루어진 객체를 사용하여 관련 기능을 그룹화하는 방식이다. 각 키가 새로운 네임스페이스가 될 수 있다.

```typescript
const myApp = {
  config: {
    language: "ko",
    enableGeolocation: true,
    maxPhotos: 20,
  },

  utils: {
    formatDate(date: Date): string {
      return date.toLocaleDateString("ko-KR");
    },
    generateId(): string {
      return crypto.randomUUID();
    },
  },

  models: {},
  views: {},
};

// 동적으로 속성 추가
myApp.utils.parseJSON = (str: string) => JSON.parse(str);
```

네임스페이스 존재 여부를 확인하는 관용적 패턴도 있었다:

```typescript
// 옵션 1: OR 연산자 (가장 흔함)
const myApp = myApp || {};

// 옵션 2: 조건문
if (!myApp) { myApp = {}; }

// 옵션 3: window 객체 명시
window.myApp || (window.myApp = {});
```

| 장점 | 단점 |
|------|------|
| 가독성이 좋고 직관적 | private 멤버를 직접 지원하지 않음 |
| 깊은 중첩 구조 지원 | 여전히 전역에 하나의 변수가 존재 |
| 충돌 검사 패턴과 결합 가능 | |

**현대적 평가**: 객체 리터럴로 설정값을 구조화하는 것은 여전히 유효하다. 다만 **네임스페이스 목적**으로 사용하는 것은 ES Modules로 대체되었다.

### 2.4 중첩 네임스페이스 (Nested Namespace)

객체 리터럴 패턴을 확장하여 계층적 구조를 만드는 방식이다. 과거 야후의 YUI 라이브러리가 대표적으로 사용했다.

```typescript
const myApp = myApp || {};
myApp.routers = myApp.routers || {};
myApp.models = myApp.models || {};
myApp.models.user = myApp.models.user || {};

// YUI 스타일의 깊은 중첩
// YAHOO.util.Dom.getElementsByClassName("test");
// myApp.utilities.charting.html5.plotGraph(data);
// myApp.services.social.facebook.realtimeStream.getLatest();
```

| 장점 | 단점 |
|------|------|
| 충돌 위험이 매우 낮음 | 접근 경로가 길어져 코드가 장황해짐 |
| 논리적 계층 구조를 명확히 표현 | 매번 존재 여부를 확인해야 하는 반복 코드 |
| | 깊은 중첩은 객체 탐색 비용을 증가시킴 |

> **Osmani의 조언**: 단일 객체 네임스페이스와 중첩 네임스페이스의 성능 차이는 크지 않다. 성능보다는 코드 구조의 명확성과 유지보수성을 기준으로 선택하라.

**현대적 평가**: 디렉터리 구조 + ES Modules가 이 패턴을 자연스럽게 대체한다. `myApp.services.social.facebook`은 `@myApp/services/social/facebook` 패키지 경로로 대응된다.

### 2.5 즉시 실행 함수 표현식 (IIFE)

정의 직후 바로 실행되는 익명 함수로, 내부 변수와 함수를 외부로부터 완전히 캡슐화한다. 벤 알만(*Ben Alman*)이 이 용어를 정립했다.

```typescript
const namespace = namespace || {};

// 네임스페이스에 기능을 주입
((ns: Record<string, unknown>, undefined?: undefined) => {
  // private 멤버
  const apiKey = "sk-secret-key";

  // public 멤버
  ns.version = "1.0.0";
  ns.sayHello = (): void => {
    speak("hello world");
  };

  // private 함수
  function speak(msg: string): void {
    console.log(`You said: ${msg}`);
  }
})((window as any).namespace = (window as any).namespace || {});

// 확장: 다른 파일에서 같은 네임스페이스에 기능 추가
((ns: Record<string, unknown>) => {
  ns.sayGoodbye = (): void => {
    console.log("goodbye");
  };
})((window as any).namespace = (window as any).namespace || {});
```

| 장점 | 단점 |
|------|------|
| private/public 멤버를 명확히 분리 | 문법이 복잡하고 중첩 괄호가 많음 |
| 여러 파일에서 같은 네임스페이스를 확장 가능 | 디버깅 시 스택 트레이스가 불명확 |
| 전역 스코프 오염 최소화 | |

**현대적 평가**: IIFE는 ES Modules가 등장하기 전의 **가장 실용적인 모듈 패턴**이었다. 현재는 모듈 번들러가 자동으로 스코프를 격리해주므로 직접 IIFE를 작성할 필요가 거의 없다. 다만, 라이브러리의 UMD 빌드나 인라인 스크립트에서 여전히 간헐적으로 사용된다.

### 2.6 네임스페이스 주입 (Namespace Injection)

`Function.prototype.apply`를 활용하여 `this`를 네임스페이스의 프록시로 사용하는 패턴이다. 여러 네임스페이스에 동일한 기능을 쉽게 주입할 수 있다.

```typescript
const myApp: Record<string, any> = {};
myApp.utils = {};

(function (this: Record<string, any>) {
  let val = 5;
  this.getValue = (): number => val;
  this.setValue = (newVal: number): void => {
    val = newVal;
  };
  this.tools = {};
}).apply(myApp.utils);

// tools 하위 네임스페이스에 기능 추가
(function (this: Record<string, any>) {
  this.diagnose = (): string => "diagnosis";
}).apply(myApp.utils.tools);

// 모듈/네임스페이스 생성자 패턴 (call 사용)
const creator = function (this: Record<string, any>, val: number = 0) {
  let counter = val;
  this.next = (): number => counter++;
  this.reset = (): void => {
    counter = 0;
  };
};

const ns1: Record<string, any> = {};
const ns2: Record<string, any> = {};

creator.call(ns1);        // counter 초기값 0
creator.call(ns2, 5000);  // counter 초기값 5000
```

| 장점 | 단점 |
|------|------|
| 여러 네임스페이스에 동일한 기능을 쉽게 적용 | `this` 바인딩 의존으로 화살표 함수와 호환 불가 |
| getter/setter 같은 기본 메서드 확장에 유용 | 더 간단한 대안(객체 병합)이 존재 |
| | 코드 흐름을 추적하기 어려움 |

**현대적 평가**: 완전히 **폐기된 패턴**이다. 클래스 상속, 믹스인, 또는 단순한 함수 합성으로 대체할 수 있다. `this` 바인딩에 의존하는 패턴은 현대 자바스크립트의 방향성과 맞지 않는다.

---

## 3. 고급 네임스페이스 패턴

### 3.1 중첩 네임스페이스 자동화

스토얀 스테파노프(*Stoyan Stefanov*)가 제안한 패턴으로, 문자열을 파싱하여 자동으로 중첩 네임스페이스를 생성하는 유틸리티 함수다.

```typescript
function extend(ns: Record<string, any>, nsString: string): Record<string, any> {
  const parts = nsString.split(".");
  let parent = ns;

  for (let i = 0; i < parts.length; i++) {
    if (typeof parent[parts[i]] === "undefined") {
      parent[parts[i]] = {};
    }
    parent = parent[parts[i]];
  }

  return parent;
}

// 사용
const myApp: Record<string, any> = {};

const mod = extend(myApp, "modules.module2");
console.log(mod === myApp.modules.module2); // true

extend(myApp, "moduleA.moduleB.moduleC.moduleD");
extend(myApp, "longer.version.looks.like.this");
```

이 함수는 이미 존재하는 중간 네임스페이스를 덮어쓰지 않으면서 필요한 계층만 생성하므로, 여러 파일에서 안전하게 호출할 수 있었다.

**현대적 평가**: 디렉터리 구조가 이 역할을 대신한다. `extend(myApp, "modules.module2")`는 `import { module2 } from "./modules/module2"`로 자연스럽게 대응된다.

### 3.2 의존성 선언 패턴 (Dependency Declaration)

깊게 중첩된 네임스페이스에 반복 접근하는 비용을 줄이기 위해, 함수 상단에서 로컬 변수에 캐싱하는 패턴이다.

```typescript
// Before: 매번 전체 경로로 접근
myApp.utilities.math.fibonacci(25);
myApp.utilities.math.sin(56);
myApp.utilities.drawing.plot(98, 50, 60);

// After: 로컬 참조로 캐싱
const maths = myApp.utilities.math;
const drawing = myApp.utilities.drawing;

maths.fibonacci(25);
maths.sin(56);
drawing.plot(98, 50, 60);
```

**현대적 평가**: ES Modules의 `import`문이 이 패턴의 정확한 현대적 등가물이다.

```typescript
// 의존성 선언 패턴의 현대 버전 — 그냥 import다
import { fibonacci, sin } from "./utilities/math";
import { plot } from "./utilities/drawing";

fibonacci(25);
sin(56);
plot(98, 50, 60);
```

---

## 4. ES Modules 시대의 네임스페이스

ES Modules(*ESM — ECMAScript 표준 모듈 시스템*)는 네임스페이스 충돌 문제를 **언어 차원에서 근본적으로 해결**했다. 각 파일이 독립적인 모듈 스코프를 가지므로, `export`하지 않은 것은 외부에서 접근할 수 없다.

### 4.1 ES Modules가 네임스페이스 문제를 해결하는 방법

```typescript
// math.ts — 파일 자체가 네임스페이스
const SECRET_CONSTANT = 42; // 외부에서 접근 불가 (private)

export function fibonacci(n: number): number {
  if (n <= 1) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);
}

export function factorial(n: number): number {
  if (n <= 1) return 1;
  return n * factorial(n - 1);
}
```

| 전통 네임스페이스가 해결하던 문제 | ES Modules의 해결 방식 |
|------|------|
| 전역 스코프 오염 방지 | 모듈 스코프 자동 격리 |
| private 멤버 구현 | `export` 하지 않으면 private |
| 이름 충돌 방지 | `import { x as y }` 별칭 가능 |
| 계층 구조 | 디렉터리 구조 + barrel files |
| 지연 로딩 | `import()` 동적 임포트 |

### 4.2 `import * as namespace` — 명시적 네임스페이스 임포트

개별 함수를 하나씩 가져오는 대신, 모듈 전체를 네임스페이스 객체로 가져올 수 있다.

```typescript
// utils/math.ts
export function add(a: number, b: number): number { return a + b; }
export function subtract(a: number, b: number): number { return a - b; }
export const PI = 3.14159;

// app.ts
import * as MathUtils from "./utils/math";

MathUtils.add(1, 2);
MathUtils.subtract(5, 3);
console.log(MathUtils.PI);
```

이 패턴은 다음과 같은 상황에서 유용하다:

- 동일한 이름의 export가 여러 모듈에 존재할 때 (`import * as UserAPI`, `import * as ProductAPI`)
- 모듈의 출처를 코드에서 명시적으로 드러내고 싶을 때
- 서드파티 라이브러리의 유틸리티를 그룹화할 때

### 4.3 Barrel Files — 모듈 그룹의 네임스페이스화

배럴 파일(*Barrel File — 여러 모듈의 export를 하나의 진입점으로 모아 재수출하는 index 파일*)은 디렉터리 단위의 네임스페이스를 구현하는 현대적 방법이다.

```typescript
// utils/math.ts
export function fibonacci(n: number): number { /* ... */ }
export function factorial(n: number): number { /* ... */ }

// utils/string.ts
export function capitalize(s: string): string { /* ... */ }
export function truncate(s: string, len: number): string { /* ... */ }

// utils/index.ts (barrel file)
export * as math from "./math";
export * as string from "./string";

// app.ts — 깔끔한 네임스페이스 접근
import { math, string } from "./utils";

math.fibonacci(10);
string.capitalize("hello");
```

배럴 파일 사용 시 주의할 점이 있다. 트리 셰이킹(*Tree Shaking — 사용하지 않는 코드를 빌드에서 제거하는 최적화*)이 제대로 작동하지 않을 수 있으므로, 대규모 라이브러리에서는 개별 경로 임포트를 권장하는 경우가 많다.

```typescript
// 트리 셰이킹 문제가 될 수 있음
import { Button } from "@ui/components"; // barrel file을 통한 임포트

// 더 나은 대안 (필요한 모듈만 직접 임포트)
import { Button } from "@ui/components/Button";
```

### 4.4 TypeScript의 `namespace` 키워드

TypeScript에는 `namespace`(*구 `module`*) 키워드가 존재한다. 이는 ES Modules가 표준화되기 이전에 도입된 기능이다.

```typescript
// TypeScript namespace (사용 비권장)
namespace MyApp {
  export interface User {
    name: string;
    email: string;
  }

  export function createUser(name: string, email: string): User {
    return { name, email };
  }
}

const user = MyApp.createUser("Kim", "kim@example.com");
```

**TypeScript 팀의 공식 입장**: ES Modules를 사용하라. `namespace`는 레거시 코드와의 호환성을 위해 유지되지만, 새 코드에서는 사용하지 않는 것이 권장된다. 유일한 예외는 **전역 타입 선언 파일**(`.d.ts`)에서 앰비언트 네임스페이스로 사용하는 경우다.

```typescript
// global.d.ts — 이 경우에만 namespace가 정당화됨
declare namespace NodeJS {
  interface ProcessEnv {
    NODE_ENV: "development" | "production";
    API_URL: string;
  }
}
```

### 4.5 모노레포에서의 패키지 네임스페이싱

대규모 조직에서는 npm 스코프(*Scope — `@org/` 접두사를 사용한 패키지 네임스페이스*)를 활용하여 패키지 수준의 네임스페이스를 구현한다.

```
@mycompany/ui-components
@mycompany/api-client
@mycompany/shared-utils
@mycompany/auth
```

```typescript
// 스코프 패키지를 통한 네임스페이스
import { Button, Modal } from "@mycompany/ui-components";
import { fetchUser } from "@mycompany/api-client";
import { formatDate } from "@mycompany/shared-utils";
```

이는 전통적인 `myApp.ui.Button`, `myApp.api.fetchUser`와 동일한 역할을 하면서도, 각 패키지가 독립적으로 버전 관리되고, 트리 셰이킹이 가능하며, 타입 안전성까지 보장된다.

---

## 5. 전통 vs 현대 비교 테이블

| 전통 패턴 | 현대적 대안 | 상태 |
|------|------|------|
| 단일 전역 변수 (IIFE 반환) | ES Module `export`/`import` | 폐기됨 |
| 접두사 네임스페이스 (`myApp_fn`) | 모듈 스코프 격리 | 폐기됨 |
| 객체 리터럴 표기법 | `import * as ns` 또는 barrel files | 설정 객체 용도로만 유효 |
| 중첩 네임스페이스 | 디렉터리 구조 + barrel files | 폐기됨 |
| IIFE 캡슐화 | 모듈 스코프 (자동 격리) | UMD 빌드에서만 잔존 |
| 네임스페이스 주입 (`apply`) | 클래스 상속, 믹스인, 합성 | 폐기됨 |
| 중첩 네임스페이스 자동화 (`extend`) | 디렉터리 구조 | 폐기됨 |
| 의존성 선언 (로컬 캐싱) | `import` 문 | `import`로 자연스럽게 대체 |
| TypeScript `namespace` | ES Modules | `.d.ts` 앰비언트 선언에서만 유효 |
| — | `@org/package` 스코프 패키지 | 모노레포 표준 |
| — | Import Maps | 브라우저 네이티브 모듈 해석 |

---

## 최신 업데이트 (2026)

| 영역 | 변화 |
|------|------|
| **ES Modules 지원** | 모든 주요 브라우저와 Node.js에서 ESM이 기본 모듈 시스템으로 정착. `require()`는 레거시로 분류됨 |
| **Import Maps** | `<script type="importmap">`이 모든 주요 브라우저에서 지원됨. 번들러 없이도 bare specifier(`import { x } from "lodash"`)를 브라우저에서 직접 해석 가능 |
| **TypeScript namespace** | TypeScript 팀이 공식적으로 `namespace` 대신 ES Modules 사용을 강력 권장. ESLint의 `@typescript-eslint/no-namespace` 규칙이 널리 채택됨 |
| **Node.js** | `"type": "module"`이 새 프로젝트의 기본값으로 자리잡음. `--experimental-require-module` 플래그로 CJS에서 ESM을 `require()` 가능 |
| **번들러** | Vite, Rspack, Turbopack 등 ESM 네이티브 번들러가 주류. Webpack의 점유율은 지속 하락 |

> **핵심 통찰**: 2026년 현재, 새로운 프로젝트에서 전통적 네임스페이스 패턴을 사용할 이유는 거의 없다. 다만, 레거시 코드를 유지보수하거나 CDN을 통한 스크립트 로딩이 필요한 경우에는 IIFE + 단일 전역 변수 패턴이 여전히 유효하다.

---

## 실무 적용 가이드

### 새 프로젝트를 시작할 때

1. **ES Modules를 기본으로 사용한다** — 파일 하나가 모듈 하나다
2. **디렉터리 구조로 네임스페이스를 표현한다** — `src/utils/`, `src/models/`, `src/services/`
3. **barrel files는 신중하게 사용한다** — 트리 셰이킹 영향을 고려
4. **모노레포에서는 `@org/` 스코프를 활용한다**

### 레거시 코드를 다룰 때

1. **전역 변수 패턴을 인식하고 이해한다** — 리팩터링의 첫걸음
2. **IIFE 패턴은 ES Module로 점진적으로 전환한다**
3. **TypeScript `namespace`는 `export`/`import`로 대체한다**

### 라이브러리를 배포할 때

1. **ESM을 기본 빌드 포맷으로 제공한다**
2. **CDN 사용자를 위해 UMD/IIFE 빌드도 병행한다** — 이때 단일 전역 변수 패턴이 필요
3. **Import Maps 호환을 고려한다**

```typescript
// 라이브러리의 UMD 빌드 — 전통 패턴이 여전히 필요한 유일한 케이스
(function (root, factory) {
  if (typeof define === "function" && define.amd) {
    define([], factory);
  } else if (typeof module === "object" && module.exports) {
    module.exports = factory();
  } else {
    (root as any).MyLibrary = factory();
  }
})(typeof self !== "undefined" ? self : this, function () {
  return {
    version: "1.0.0",
    greet: (name: string) => `Hello, ${name}!`,
  };
});
```

---

## 요약

- 네임스페이스 패턴은 ES Modules 이전 시대에 **전역 스코프 오염과 이름 충돌**을 해결하기 위해 고안되었다
- 전통적 패턴(단일 전역 변수, 접두사, 객체 리터럴, 중첩 네임스페이스, IIFE, 네임스페이스 주입)은 대부분 **역사적 의미**만 남아 있다
- ES Modules는 파일 단위 스코프 격리, `export`/`import`, 동적 임포트로 네임스페이스 문제를 **근본적으로 해결**했다
- 현대적 네임스페이스 전략: `import * as ns`, barrel files, `@org/` 스코프 패키지, 디렉터리 구조
- TypeScript의 `namespace` 키워드는 `.d.ts` 앰비언트 선언을 제외하면 **사용하지 않는 것이 권장**된다
- 라이브러리 배포 시 CDN 사용자를 위한 UMD 빌드에서만 전통 패턴이 여전히 필요하다

---

## 다른 챕터와의 관계

- **Ch07 (자바스크립트 디자인 패턴)**: 모듈 패턴, 노출 모듈 패턴은 네임스페이스 패턴과 결합하여 사용되었으며, 이 장의 IIFE 기반 패턴의 발전형이다
- **Ch10 (모듈 패턴)**: AMD, CommonJS, ESM 등 모듈 시스템의 진화를 다루며, 네임스페이스 패턴이 왜 불필요해졌는지의 배경을 설명한다
- **Ch12 (리액트 디자인 패턴)**: 리액트 컴포넌트는 모듈 단위로 구성되어 네임스페이스 충돌 문제가 발생하지 않는 구조를 보여준다
