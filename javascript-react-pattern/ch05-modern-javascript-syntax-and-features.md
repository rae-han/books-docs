# Chapter 05: Modern JavaScript Syntax and Features (최신 자바스크립트 문법과 기능)

## 핵심 질문

> ES2015+ 모듈 시스템과 클래스 문법은 자바스크립트 디자인 패턴 구현에 어떤 기반을 제공하며, 이를 효과적으로 활용하려면 무엇을 알아야 하는가?

---

## 1. 애플리케이션 분리의 중요성

확장 가능하고 유지보수하기 쉬운 애플리케이션을 만들려면 **관심사의 분리**(*Separation of Concerns*)가 필수다. 모듈(*Module — 독립적인 코드 단위로, 특정 기능을 캡슐화하여 다른 코드와의 의존성을 최소화한 것*)은 이 분리를 실현하는 핵심 도구다.

### 모듈의 역할

모듈을 사용하면 코드를 **느슨한 결합**(*Loose Coupling — 모듈 간 의존성이 최소화되어 한 모듈의 변경이 다른 모듈에 영향을 주지 않는 상태*)으로 구성할 수 있다. 각 모듈은 자신의 책임만 담당하고, 필요한 의존성만 명시적으로 가져온다.

### 모듈 시스템의 역사

자바스크립트에는 오랫동안 네이티브 모듈 시스템이 없었다. 이 공백을 메우기 위해 커뮤니티 주도의 여러 모듈 포맷이 등장했다.

| 모듈 포맷 | 시대 | 환경 | 특징 |
|-----------|------|------|------|
| **IIFE** | 2000년대 | 브라우저 | 즉시 실행 함수로 스코프 격리. 의존성 관리 불가 |
| **AMD** (*Asynchronous Module Definition*) | 2010~2015 | 브라우저 (RequireJS) | 비동기 로딩 지원. `define()`과 `require()` 사용 |
| **CommonJS** | 2009~ | Node.js | 동기 로딩. `require()`/`module.exports`. 서버 환경에 적합 |
| **UMD** (*Universal Module Definition*) | 2012~ | 양쪽 | AMD + CommonJS 호환 래퍼. 라이브러리 배포용 |
| **ES Modules** | 2015~ | 양쪽 | 언어 표준. `import`/`export`. 정적 분석 가능. **현재 표준** |

```typescript
// CommonJS (레거시 Node.js)
const lodash = require("lodash");
module.exports = { myFunction };

// ES Modules (현대 표준)
import lodash from "lodash";
export { myFunction };
```

AMD와 CommonJS는 역사적으로 중요한 역할을 했지만, 2015년 ES6에서 **ES Modules**(*ESM*)가 표준으로 도입되면서 점차 대체되었다. 오늘날 새로운 프로젝트는 거의 예외 없이 ESM을 사용한다.

> **핵심 통찰**: 모듈 시스템의 진화 과정은 자바스크립트 생태계가 "글로벌 스크립트 언어"에서 "대규모 애플리케이션 언어"로 성장한 역사 자체다. ES Modules의 표준화로 이 긴 여정은 사실상 마무리되었다.

---

## 2. 모듈 가져오기와 내보내기

ES Modules의 핵심은 `import`와 `export` 키워드다.

### 내보내기 (export)

내보내기에는 **이름 있는 내보내기**(*Named Export*)와 **기본 내보내기**(*Default Export*) 두 가지가 있다.

```typescript
// bakery.ts — 이름 있는 내보내기
export interface Cake {
  name: string;
  flavor: string;
  price: number;
}

export const defaultFlavor: string = "vanilla";

export function createCake(name: string, flavor: string = defaultFlavor): Cake {
  return { name, flavor, price: calculatePrice(flavor) };
}

// 내부 함수 — export하지 않으므로 외부에서 접근 불가
function calculatePrice(flavor: string): number {
  const prices: Record<string, number> = {
    vanilla: 3000,
    chocolate: 3500,
    strawberry: 4000,
  };
  return prices[flavor] ?? 3000;
}
```

```typescript
// cakeFactory.ts — 기본 내보내기
import type { Cake } from "./bakery";

export default class CakeFactory {
  private recipes: Map<string, string> = new Map();

  register(name: string, flavor: string): void {
    this.recipes.set(name, flavor);
  }

  create(name: string): Cake {
    const flavor = this.recipes.get(name) ?? "vanilla";
    return { name, flavor, price: this.getPrice(flavor) };
  }

  private getPrice(flavor: string): number {
    return flavor === "chocolate" ? 3500 : 3000;
  }
}
```

### 가져오기 (import)

```typescript
// 이름 있는 가져오기
import { createCake, defaultFlavor } from "./bakery";
import type { Cake } from "./bakery";

// 기본 가져오기 — 이름을 자유롭게 지정
import Factory from "./cakeFactory";

// 이름 변경 (별칭)
import { createCake as bakeCake } from "./bakery";

// 혼합 가져오기 — 기본 + 이름 있는 내보내기를 동시에
import Factory, { createCake } from "./combined-module";
```

### JavaScript vs TypeScript

TypeScript에서는 내보내기에 **타입**과 **인터페이스**도 포함할 수 있다. `export type`이나 `export interface`를 사용하면 런타임 코드 없이 타입 정보만 내보낸다.

```typescript
// types.ts — 타입 전용 내보내기
export type ID = string | number;
export interface User {
  id: ID;
  name: string;
  email: string;
}

// 타입 전용 가져오기 (TypeScript 3.8+)
import type { User, ID } from "./types";

// 혼합 — 인라인 타입 표시 (TypeScript 4.5+)
import { CakeFactory, type Cake } from "./cakeFactory";
```

`import type`은 컴파일 후 완전히 제거되므로 번들 크기에 영향을 주지 않는다. JavaScript에서는 이 기능이 없으며, JSDoc 주석으로 타입을 명시하는 방법이 대안이다.

### .mjs 확장자와 모듈 설정

브라우저에서 ESM을 사용할 때는 `<script type="module">`을 지정해야 한다. Node.js에서는 `.mjs` 확장자를 사용하거나, `package.json`에 `"type": "module"`을 설정하여 `.js` 파일을 ESM으로 인식시킬 수 있다.

```html
<!-- 브라우저에서 ES Module 사용 -->
<script type="module" src="./main.js"></script>

<!-- 인라인 모듈도 가능 -->
<script type="module">
  import { createCake } from "./bakery.js";
  console.log(createCake("Test"));
</script>
```

> **Osmani의 조언**: Named Export를 기본으로 사용하라. Default Export는 편리해 보이지만, IDE의 자동 완성과 리팩터링 도구가 Named Export를 더 잘 지원한다. TypeScript 생태계에서는 Named Export가 사실상 표준이다.

---

## 3. 모듈 객체

모듈에서 내보내는 항목이 많을 때, **네임스페이스 가져오기**(*Namespace Import*)를 사용하면 하나의 객체로 묶어서 접근할 수 있다.

```typescript
// math.ts
export const PI: number = 3.14159;
export const E: number = 2.71828;

export function add(a: number, b: number): number {
  return a + b;
}

export function multiply(a: number, b: number): number {
  return a * b;
}
```

```typescript
// 네임스페이스 가져오기
import * as MathUtils from "./math";

console.log(MathUtils.PI);             // 3.14159
console.log(MathUtils.add(2, 3));      // 5
console.log(MathUtils.multiply(4, 5)); // 20
```

`import * as`는 모듈의 모든 이름 있는 내보내기를 하나의 객체 아래에 모은다. 이 방식은 모듈의 출처를 명확하게 만들어 코드 가독성을 높이지만, **트리 셰이킹**(*Tree Shaking — 사용하지 않는 코드를 번들에서 제거하는 최적화 기법*)에 불리할 수 있으므로 주의가 필요하다. 다만 최신 번들러(Webpack 5, Rollup, esbuild)는 `import *`에 대해서도 상당 수준의 트리 셰이킹을 지원한다.

```typescript
// 트리 셰이킹에 유리한 방식 (권장)
import { createCake } from "./bakery";

// 트리 셰이킹에 불리할 수 있는 방식
import * as Bakery from "./bakery";
Bakery.createCake("Test");
```

> **핵심 통찰**: 네임스페이스 가져오기는 유틸리티 모듈처럼 관련 함수가 많은 경우에 유용하다. 그러나 번들 최적화가 중요한 프로덕션 코드에서는 필요한 항목만 골라서 가져오는 것이 더 나은 선택이다.

---

## 4. 외부 소스로부터 가져오는 모듈

브라우저 환경에서는 원격 URL에서 모듈을 직접 가져올 수 있다.

```html
<script type="module">
  import confetti from "https://cdn.skypack.dev/canvas-confetti";
  confetti();
</script>
```

CDN(*Content Delivery Network*)에서 직접 모듈을 가져오는 방식은 빌드 도구 없이 프로토타이핑하거나 간단한 프로젝트를 구성할 때 유용하다. 그러나 프로덕션 환경에서는 **네트워크 지연**, **가용성 의존**, **버전 관리의 어려움** 등의 이유로 번들러를 통한 로컬 의존성 관리가 권장된다.

Deno와 같은 런타임은 URL 기반 모듈 가져오기를 1급 시민(*first-class citizen*)으로 지원하며, 이는 Node.js의 `node_modules` 방식과 대조적인 접근이다.

```typescript
// Deno — URL 기반 임포트
import { serve } from "https://deno.land/std@0.200.0/http/server.ts";
```

---

## 5. 정적으로 모듈 가져오기

지금까지 살펴본 `import` 문은 모두 **정적 가져오기**(*Static Import*)다. 정적 가져오기는 다음과 같은 특징을 가진다.

| 특징 | 설명 |
|------|------|
| **파일 최상위** | 모듈의 최상위 레벨에서만 사용 가능 (함수나 조건문 안에서 사용 불가) |
| **컴파일 타임 분석** | 번들러가 빌드 시점에 의존성 그래프를 분석할 수 있다 |
| **트리 셰이킹 가능** | 사용하지 않는 코드를 제거하여 번들 크기를 최적화할 수 있다 |
| **순환 참조 처리** | 정적 분석 덕분에 순환 참조를 감지하고 처리할 수 있다 |

```typescript
// 정적 가져오기 — 항상 파일 최상위에 위치
import { useState, useEffect } from "react";
import type { FC, ReactNode } from "react";

// 조건부 가져오기는 불가능
// if (condition) {
//   import { something } from "./module"; // SyntaxError!
// }
```

### 정적 가져오기의 성능 문제

정적 import는 **초기 로드 시** 모든 의존성을 한꺼번에 로드한다. 대규모 애플리케이션에서는 이것이 성능 문제를 일으킬 수 있다.

```
main.ts
├── import dashboard.ts (100KB)
│   ├── import chart.ts (200KB)
│   └── import table.ts (150KB)
├── import settings.ts (80KB)
└── import admin.ts (300KB)  ← 관리자만 사용하는데 항상 로드됨
```

사용자가 대시보드만 보더라도 admin 모듈까지 로드되어 **불필요한 네트워크 비용과 파싱 시간**이 발생한다. 이 문제를 해결하는 것이 동적 가져오기다.

> **핵심 통찰**: 정적 import의 "모든 것을 미리 로드"하는 특성은 자바스크립트 엔진이 의존성 그래프를 사전에 분석하고 최적화할 수 있게 해주는 장점이 있다. 하지만 애플리케이션이 커지면 이 장점이 오히려 성능 병목으로 작용한다. 정적과 동적 import를 적절히 조합하는 것이 핵심이다.

---

## 6. 동적으로 모듈 가져오기

**동적 가져오기**(*Dynamic Import*)는 `import()`를 함수처럼 호출하여 런타임에 모듈을 로드하는 기법이다. 이 함수는 **Promise**를 반환하므로 `async/await`와 자연스럽게 결합된다.

```typescript
// 기본적인 동적 가져오기
async function loadModule(): Promise<void> {
  const module = await import("./bakery");
  const cake = module.createCake("Lazy Cake");
  console.log(cake);
}
```

동적 가져오기는 **코드 분할**(*Code Splitting — 전체 번들을 여러 작은 청크로 나누어 필요한 시점에만 로드하는 기법*)의 기반이 된다. Webpack, Vite, Rollup 등 주요 번들러는 `import()` 호출을 만나면 자동으로 별도의 청크(*chunk*)로 분리한다.

### 6.1 사용자 상호작용에 따라 가져오기

사용자가 특정 기능을 실제로 사용할 때만 해당 모듈을 로드하면 초기 번들 크기를 크게 줄일 수 있다.

```typescript
// 채팅 위젯 — 버튼 클릭 시에만 모듈 로드
const chatButton = document.getElementById("open-chat") as HTMLButtonElement;

chatButton.addEventListener("click", async (): Promise<void> => {
  const { ChatWidget } = await import("./chat-widget");
  const widget = new ChatWidget();
  widget.open();
});
```

리액트에서는 `React.lazy()`를 사용하여 컴포넌트 레벨에서 동적 가져오기를 구현한다.

```tsx
import { lazy, Suspense, useState } from "react";
import type { FC } from "react";

// 컴포넌트가 실제로 렌더링될 때까지 로드를 지연
const AdminPanel = lazy(() => import("./AdminPanel"));

const App: FC = () => {
  const [showAdmin, setShowAdmin] = useState<boolean>(false);

  return (
    <>
      <button onClick={() => setShowAdmin(true)}>관리자 패널</button>
      {showAdmin && (
        <Suspense fallback={<div>로딩 중...</div>}>
          <AdminPanel />
        </Suspense>
      )}
    </>
  );
};
```

### 6.2 화면에 보이면 가져오기 (IntersectionObserver)

사용자가 **스크롤하여 특정 요소가 화면에 보이는 순간** 모듈을 로드하는 고급 패턴이다. **IntersectionObserver API**를 활용한다.

```typescript
// IntersectionObserver를 활용한 지연 로딩
function lazyLoadOnVisible(
  elementId: string,
  moduleLoader: () => Promise<{ render: (el: HTMLElement) => void }>,
): void {
  const element = document.getElementById(elementId);
  if (!element) return;

  const observer = new IntersectionObserver(
    async (entries: IntersectionObserverEntry[]) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          const module = await moduleLoader();
          module.render(entry.target as HTMLElement);
          observer.unobserve(entry.target); // 한 번만 로드
        }
      }
    },
    { rootMargin: "200px" }, // 200px 전에 미리 로드 시작
  );

  observer.observe(element);
}

// 사용 예시 — 차트가 화면에 보일 때 차트 라이브러리 로드
lazyLoadOnVisible("chart-container", () => import("./heavy-chart-lib"));
```

```tsx
// React에서 — 커스텀 Hook으로 구현
import { useRef, useState, useEffect, lazy, Suspense } from "react";

function useOnScreen(ref: React.RefObject<HTMLElement | null>): boolean {
  const [isVisible, setIsVisible] = useState<boolean>(false);

  useEffect(() => {
    if (!ref.current) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.1 },
    );

    observer.observe(ref.current);
    return () => observer.disconnect();
  }, [ref]);

  return isVisible;
}

// 사용
const HeavyComponent = lazy(() => import("./HeavyComponent"));

function Page() {
  const ref = useRef<HTMLDivElement>(null);
  const isVisible = useOnScreen(ref);

  return (
    <div ref={ref}>
      {isVisible && (
        <Suspense fallback={<div>로딩 중...</div>}>
          <HeavyComponent />
        </Suspense>
      )}
    </div>
  );
}
```

> **Osmani의 조언**: 동적 import를 과도하게 사용하면 네트워크 워터폴(*waterfall*)이 발생할 수 있다. 핵심 모듈은 정적으로 로드하고, 무거운 서드파티 라이브러리나 사용 빈도가 낮은 기능에만 동적 import를 적용하라. 크롬 DevTools의 Coverage 탭을 사용하여 실제로 초기 로드 시 사용되지 않는 코드를 식별하는 것이 좋다.

---

## 7. 서버에서 모듈 사용하기

Node.js는 전통적으로 CommonJS를 사용했지만, v12부터 ES Modules를 실험적으로 지원하기 시작하여 v16 이후 정식 지원한다.

### Node.js에서 ESM 활성화

**방법 1: `package.json`에 `type` 필드 설정**

```json
{
  "name": "my-app",
  "version": "1.0.0",
  "type": "module"
}
```

이 설정을 추가하면 프로젝트 내 모든 `.js` 파일이 ES Module로 취급된다.

**방법 2: `.mjs` 확장자 사용**

```
project/
├── package.json          (type: "commonjs" 또는 미설정)
├── legacy-code.js        ← CommonJS로 동작
└── modern-code.mjs       ← ES Module로 동작
```

**방법 3: TypeScript 프로젝트**

```json
// tsconfig.json
{
  "compilerOptions": {
    "module": "ESNext",
    "moduleResolution": "bundler",
    "target": "ES2022"
  }
}
```

### CommonJS와 ES Modules 상호 운용

```typescript
// ESM에서 CommonJS 모듈 가져오기 — 대부분 동작
import express from "express"; // CommonJS 모듈이지만 default import 가능

// CommonJS에서 ESM 모듈 가져오기 — 동적 import만 가능
// const { something } = require("./es-module.mjs"); // 불가!
const esModule = await import("./es-module.mjs"); // OK
```

| 비교 항목 | CommonJS | ES Modules |
|-----------|----------|------------|
| 구문 | `require()` / `module.exports` | `import` / `export` |
| 로딩 | 동기 | 비동기 |
| 분석 | 런타임 | 컴파일 타임 (정적 분석 가능) |
| 트리 셰이킹 | 불가능 | 가능 |
| Top-level await | 불가능 | 가능 (ES2022) |
| 브라우저 지원 | 번들러 필요 | 네이티브 지원 |

> **핵심 통찰**: ESM으로의 전환은 Node.js 생태계에서 아직 진행 중이다. 많은 npm 패키지가 CJS와 ESM을 동시에 지원하는 듀얼 패키지 형태로 배포되고 있다. 새 프로젝트에서는 ESM을 기본으로 선택하되, 레거시 의존성과의 호환성을 항상 확인해야 한다.

---

## 8. 모듈을 사용하면 생기는 이점

ES Modules를 사용하면 다음과 같은 이점을 얻는다.

### 8.1 한 번만 실행

모듈 코드는 **최초 가져오기 시 단 한 번만 실행**된다. 동일한 모듈을 여러 곳에서 가져와도 코드는 다시 실행되지 않으며, 이미 평가된 결과가 공유된다. 이 특성은 싱글턴(*Singleton*) 패턴을 자연스럽게 구현할 수 있게 한다.

```typescript
// config.ts — 모듈 스코프의 싱글턴
interface AppConfig {
  apiUrl: string;
  debug: boolean;
  version: string;
}

const config: AppConfig = {
  apiUrl: "https://api.example.com",
  debug: process.env.NODE_ENV !== "production",
  version: "1.0.0",
};

export default config;

// 어디서 가져와도 동일한 config 객체를 참조한다
```

### 8.2 자동 지연 실행 (auto defer)

`<script type="module">`로 로드된 스크립트는 자동으로 **지연 실행**(*deferred*)된다. 일반 `<script>` 태그와 달리 DOM 파싱을 차단하지 않으므로 별도의 `defer` 속성이 필요 없다.

```html
<!-- 일반 스크립트 — HTML 파싱 차단 -->
<script src="blocking.js"></script>

<!-- 모듈 스크립트 — 자동 defer -->
<script type="module" src="non-blocking.js"></script>

<!-- 위 두 줄은 사실상 동일한 효과 -->
<script defer src="non-blocking.js"></script>
<script type="module" src="non-blocking.js"></script>
```

### 8.3 재사용성

모듈은 독립적인 코드 단위이므로 여러 프로젝트에서 재사용할 수 있다. npm 패키지 생태계가 이 재사용성의 대표적인 예다.

### 8.4 네임스페이스 분리

각 모듈은 자체적인 스코프를 가진다. 모듈 내부에서 선언한 변수는 명시적으로 내보내지 않는 한 외부에서 접근할 수 없다. 이는 전역 네임스페이스 오염(*global scope pollution*)을 근본적으로 방지한다.

### 8.5 트리 셰이킹

정적 분석이 가능한 ESM 구조 덕분에 번들러가 **사용되지 않는 내보내기를 제거**할 수 있다. 이를 트리 셰이킹이라 하며, 프로덕션 번들 크기를 크게 줄여준다.

```typescript
// math.ts
export function add(a: number, b: number): number { return a + b; }
export function subtract(a: number, b: number): number { return a - b; }
export function multiply(a: number, b: number): number { return a * b; }
export function divide(a: number, b: number): number { return a / b; }

// app.ts — add만 사용
import { add } from "./math";
console.log(add(1, 2));
// 번들러는 subtract, multiply, divide를 최종 번들에서 제거한다
```

> **Osmani의 조언**: 트리 셰이킹의 효과를 극대화하려면 사이드 이펙트(*side effect*)가 없는 순수한 모듈을 작성하고, `package.json`에 `"sideEffects": false`를 설정하여 번들러에게 안전한 제거가 가능함을 알려야 한다.

---

## 9. 생성자, 게터, 세터를 가진 클래스

ES2015에서 도입된 `class` 문법은 자바스크립트의 프로토타입 기반 상속을 더 직관적으로 표현하는 **문법적 설탕**(*Syntactic Sugar*)이다. 디자인 패턴의 구현에 있어 클래스는 핵심적인 구성 요소가 된다.

### 기본 클래스 구조

```typescript
class Cake {
  private name: string;
  private flavor: string;
  private toppings: string[];

  constructor(name: string, flavor: string, toppings: string[] = []) {
    this.name = name;
    this.flavor = flavor;
    this.toppings = toppings;
  }

  // 게터 (getter) — 프로퍼티처럼 접근
  get description(): string {
    return `${this.name}은(는) ${this.flavor} 맛이다.`;
  }

  // 세터 (setter) — 유효성 검사 포함 가능
  set mainFlavor(flavor: string) {
    if (!flavor.trim()) {
      throw new Error("빈 문자열은 허용되지 않는다");
    }
    this.flavor = flavor;
  }

  addTopping(topping: string): void {
    this.toppings.push(topping);
  }

  listToppings(): string[] {
    return [...this.toppings];
  }
}

const myCake = new Cake("생일 케이크", "초콜릿", ["딸기"]);
console.log(myCake.description); // "생일 케이크은(는) 초콜릿 맛이다."
myCake.mainFlavor = "바닐라";    // 세터 호출
myCake.addTopping("블루베리");
```

### JavaScript vs TypeScript

TypeScript의 클래스는 JavaScript 클래스에 **접근 제한자**(*Access Modifier*)와 **타입 주석**, 그리고 **매개변수 프로퍼티**를 추가한다.

```typescript
// TypeScript — 매개변수 프로퍼티로 간결하게 작성
class Cake {
  constructor(
    private name: string,
    private flavor: string,
    private toppings: string[] = [],
  ) {}
  // 생성자 매개변수에 접근 제한자를 붙이면 자동으로 프로퍼티 선언+할당

  get description(): string {
    return `${this.name}은(는) ${this.flavor} 맛이다.`;
  }
}
```

```javascript
// JavaScript (동등한 코드) — 접근 제한자 없음
class Cake {
  #name;    // # 프리픽스로 private 필드 (ES2022)
  #flavor;
  #toppings;

  constructor(name, flavor, toppings = []) {
    this.#name = name;
    this.#flavor = flavor;
    this.#toppings = toppings;
  }

  get description() {
    return `${this.#name}은(는) ${this.#flavor} 맛이다.`;
  }
}
```

| 기능 | JavaScript | TypeScript |
|------|-----------|------------|
| **public** | 기본값 (키워드 없음) | `public` 키워드 (생략 가능) |
| **private** | `#` prefix (런타임 강제) | `private` 키워드 (컴파일 타임) + `#` prefix도 지원 |
| **protected** | 지원 안 함 | `protected` 키워드 |
| **readonly** | 지원 안 함 | `readonly` 키워드 |
| **매개변수 프로퍼티** | 지원 안 함 | 접근 제한자를 매개변수에 직접 사용 |

TypeScript의 `private`은 **컴파일 타임 전용**이고, JavaScript의 `#` 프리픽스는 **런타임에서도 접근을 차단**한다. TypeScript 4.3+에서는 `#` 프리픽스도 사용할 수 있으므로, 런타임 보호가 필요하면 `#`을 선택한다.

### 상속 (extends, super)

```typescript
class PremiumCake extends Cake {
  private candles: number;

  constructor(name: string, flavor: string, candles: number) {
    super(name, flavor, ["생크림"]); // 부모 생성자 호출 — 반드시 this 접근 전에
    this.candles = candles;
  }

  // 메서드 오버라이드
  override get description(): string {
    return `[프리미엄] ${super.description} (촛불 ${this.candles}개)`;
  }
}

const premium = new PremiumCake("유진의 케이크", "바닐라", 25);
console.log(premium.description);
// "[프리미엄] 유진의 케이크은(는) 바닐라 맛이다. (촛불 25개)"
```

TypeScript의 `override` 키워드는 의도적으로 부모 메서드를 재정의하고 있음을 명시한다. `tsconfig.json`에서 `"noImplicitOverride": true`를 설정하면 `override` 없이 부모 메서드를 재정의하려 할 때 에러가 발생한다.

### 비공개 필드와 정적 멤버

```typescript
class Counter {
  // 정적 비공개 필드
  static #totalInstances: number = 0;

  // 인스턴스 비공개 필드
  #count: number = 0;

  constructor() {
    Counter.#totalInstances++;
  }

  increment(): void {
    this.#count++;
  }

  get value(): number {
    return this.#count;
  }

  // 정적 메서드
  static getTotalInstances(): number {
    return Counter.#totalInstances;
  }

  // 정적 블록 (ES2022) — 복잡한 정적 초기화
  static {
    console.log("Counter 클래스 로드됨");
  }
}

const c1 = new Counter();
const c2 = new Counter();
console.log(Counter.getTotalInstances()); // 2
// c1.#count; // SyntaxError — 외부에서 비공개 필드 접근 불가
```

### JavaScript vs TypeScript

TypeScript에서는 `abstract` 키워드로 **추상 클래스**(*Abstract Class — 직접 인스턴스화할 수 없고, 하위 클래스가 특정 메서드를 반드시 구현하도록 강제하는 클래스*)를 정의할 수 있다. 이는 디자인 패턴의 **템플릿 메서드 패턴**이나 **팩토리 패턴** 구현에 유용하다.

```typescript
// TypeScript 전용 — 추상 클래스
abstract class Shape {
  abstract area(): number;
  abstract perimeter(): number;

  // 구체 메서드 — 하위 클래스가 공통으로 사용
  describe(): string {
    return `넓이: ${this.area().toFixed(2)}, 둘레: ${this.perimeter().toFixed(2)}`;
  }
}

class Circle extends Shape {
  constructor(private radius: number) {
    super();
  }

  area(): number {
    return Math.PI * this.radius ** 2;
  }

  perimeter(): number {
    return 2 * Math.PI * this.radius;
  }
}

// const shape = new Shape(); // Error — 추상 클래스는 인스턴스화 불가
const circle = new Circle(5);
console.log(circle.describe()); // "넓이: 78.54, 둘레: 31.42"
```

JavaScript에는 `abstract` 키워드가 없다. 동일한 효과를 내려면 기본 클래스의 메서드에서 수동으로 에러를 던져야 한다.

> **핵심 통찰**: ES 클래스는 프로토타입 기반 상속의 문법적 설탕이지만, `#private` 필드, `static` 블록 등 프로토타입만으로는 구현하기 어려운 기능도 추가되었다. 디자인 패턴 구현 시 클래스 문법은 패턴의 의도를 더 명확하게 드러내는 도구가 된다.

---

## 10. 자바스크립트 프레임워크와 클래스

### 리액트: 클래스에서 함수로

리액트는 한때 클래스 컴포넌트가 주류였지만, **Hooks**의 도입(React 16.8, 2019) 이후 **함수 컴포넌트**가 표준이 되었다.

```typescript
// 클래스 컴포넌트 (레거시)
import { Component } from "react";

interface CounterProps {
  initialCount: number;
}

interface CounterState {
  count: number;
}

class CounterClass extends Component<CounterProps, CounterState> {
  state: CounterState = { count: this.props.initialCount };

  increment = (): void => {
    this.setState((prev) => ({ count: prev.count + 1 }));
  };

  render() {
    return (
      <button onClick={this.increment}>
        Count: {this.state.count}
      </button>
    );
  }
}
```

```tsx
// 함수 컴포넌트 + Hooks (현대적)
import { useState } from "react";
import type { FC } from "react";

interface CounterProps {
  initialCount: number;
}

const Counter: FC<CounterProps> = ({ initialCount }) => {
  const [count, setCount] = useState<number>(initialCount);

  return (
    <button onClick={() => setCount((prev) => prev + 1)}>
      Count: {count}
    </button>
  );
};
```

| 비교 항목 | 클래스 컴포넌트 | 함수 컴포넌트 |
|-----------|----------------|--------------|
| **코드량** | 많음 (`this`, 생명주기 메서드) | 적음 (Hook 사용) |
| **로직 재사용** | HOC, Render Props (복잡) | 커스텀 Hook (단순) |
| **`this` 바인딩** | 필요 (버그 유발 가능) | 불필요 |
| **최적화** | `shouldComponentUpdate` 수동 구현 | `React.memo`, `useMemo` |
| **동시성 모드** | 제한적 지원 | 완전 지원 |

### 웹 컴포넌트: 클래스가 여전히 필수

반면 **웹 컴포넌트**(*Web Components — 프레임워크에 의존하지 않는 브라우저 네이티브 컴포넌트 기술*)에서는 클래스가 필수다. 커스텀 엘리먼트(*Custom Element*)를 정의하려면 `HTMLElement`를 상속해야 한다.

```typescript
class MyCounter extends HTMLElement {
  private count: number = 0;
  private shadow: ShadowRoot;

  constructor() {
    super();
    this.shadow = this.attachShadow({ mode: "open" });
  }

  connectedCallback(): void {
    this.render();
    this.shadow.querySelector("button")?.addEventListener("click", () => {
      this.count++;
      this.render();
    });
  }

  private render(): void {
    this.shadow.innerHTML = `
      <style>
        button { padding: 8px 16px; font-size: 16px; cursor: pointer; }
      </style>
      <button>Count: ${this.count}</button>
    `;
  }
}

customElements.define("my-counter", MyCounter);
// HTML에서 <my-counter></my-counter>로 사용
```

### 클래스가 여전히 유용한 영역

| 영역 | 이유 |
|------|------|
| **Web Components** | `HTMLElement`를 상속해야 하므로 클래스 필수 |
| **에러 바운더리** | React에서 `componentDidCatch`를 사용하려면 클래스 컴포넌트 필요 |
| **디자인 패턴** | Strategy, Observer, State 등 GoF 패턴은 클래스로 표현하면 직관적 |
| **데코레이터 기반 프레임워크** | TypeORM, NestJS 등 |

> **Osmani의 조언**: 리액트에서 새 컴포넌트를 작성할 때는 함수 컴포넌트를 사용하라. 클래스 컴포넌트는 레거시 코드 유지보수 시에만 만나게 될 것이다. 그러나 웹 컴포넌트나 특정 디자인 패턴(예: 전략 패턴의 컨텍스트 클래스) 구현에서는 클래스가 여전히 최선의 선택이다.

---

## 최신 업데이트 (2026)

원서 출판(2023) 이후 자바스크립트 언어와 생태계에 중요한 변화가 있었다.

| 영역 | 변화 |
|------|------|
| **ES2022** | Top-level `await`, `#private` 필드/메서드, `static` 클래스 기능, `at()`, `Object.hasOwn()` |
| **ES2023** | `Array.prototype.findLast()`/`findLastIndex()`, Hashbang grammar, Change Array by Copy (`toSorted()`, `toReversed()`, `with()`) |
| **ES2024** | `Promise.withResolvers()`, `Object.groupBy()`, Temporal API (Stage 3), Decorators (Stage 3 → 표준화 진행), Explicit Resource Management (`using` 키워드) |
| **Import Maps** | `<script type="importmap">`으로 번들러 없이 베어 스페시파이어(*bare specifier*) 해석 가능 |
| **빌드 도구** | Vite 6, Turbopack 안정화, Rspack 등장 — Webpack에서 이동하는 추세 |
| **TypeScript** | TS 5.x — `const` 타입 매개변수, `satisfies` 연산자, 데코레이터 지원 |

### Change Array by Copy (ES2023)

`toSorted()`, `toReversed()`, `with()` 메서드는 **원본 배열을 변경하지 않고 새 배열을 반환**한다. 리액트의 불변 상태 관리와 특히 잘 맞는다.

```typescript
const numbers: number[] = [3, 1, 4, 1, 5];

// 기존 — 원본을 변경
// numbers.sort(); // numbers가 변경됨!

// ES2023 — 원본 보존
const sorted: number[] = numbers.toSorted((a, b) => a - b);
const reversed: number[] = numbers.toReversed();
const replaced: number[] = numbers.with(2, 99); // index 2를 99로 교체

console.log(numbers);  // [3, 1, 4, 1, 5] — 변경 없음
console.log(sorted);   // [1, 1, 3, 4, 5]
console.log(reversed); // [5, 1, 4, 1, 3]
console.log(replaced); // [3, 1, 99, 1, 5]
```

### Promise.withResolvers() (ES2024)

Promise 생성 시 `resolve`와 `reject` 함수를 외부로 추출할 수 있는 정적 메서드다.

```typescript
// 기존 방식 — 콜백 내부에서만 resolve/reject 접근 가능
let resolve!: (value: string) => void;
let reject!: (reason: Error) => void;
const promise = new Promise<string>((res, rej) => {
  resolve = res;
  reject = rej;
});

// ES2024 — 깔끔한 분해
const { promise: p, resolve: res, reject: rej } = Promise.withResolvers<string>();
setTimeout(() => res("완료!"), 1000);
```

### Explicit Resource Management (using 키워드)

TypeScript 5.2+에서 지원하며 TC39에서 표준화가 진행 중이다. 스코프를 벗어날 때 자동으로 리소스를 정리한다.

```typescript
class DatabaseConnection implements Disposable {
  constructor(private url: string) {
    console.log(`연결: ${url}`);
  }

  query(sql: string): unknown[] {
    return []; // 쿼리 실행
  }

  [Symbol.dispose](): void {
    console.log(`연결 해제: ${this.url}`);
  }
}

function executeQuery(): void {
  using db = new DatabaseConnection("postgres://localhost/mydb");
  const results = db.query("SELECT * FROM users");
  // 함수가 끝나면 db[Symbol.dispose]()가 자동 호출된다
}
```

### Import Maps (브라우저 네이티브)

빌드 도구 없이 브라우저에서 베어 스페시파이어(패키지 이름)로 모듈을 가져올 수 있게 한다.

```html
<script type="importmap">
{
  "imports": {
    "react": "https://esm.sh/react@19",
    "react-dom/client": "https://esm.sh/react-dom@19/client",
    "lodash/": "https://esm.sh/lodash-es/"
  }
}
</script>
<script type="module">
  import { useState } from "react";
  import { debounce } from "lodash/debounce";
</script>
```

### TypeScript satisfies 연산자 (TS 4.9+)

**값의 타입 호환성을 검증하면서도 추론된 타입을 유지**하는 연산자다.

```typescript
type ColorMap = Record<string, string | number[]>;

// as를 사용하면 타입 정보가 넓어짐
const colors1 = {
  red: "#ff0000",
  green: [0, 255, 0],
} as ColorMap;
// colors1.red.toUpperCase(); // 에러! string | number[]라서 string 메서드 사용 불가

// satisfies를 사용하면 타입 호환성 검증 + 추론 유지
const colors2 = {
  red: "#ff0000",
  green: [0, 255, 0],
} satisfies ColorMap;
colors2.red.toUpperCase();       // OK! red가 string으로 추론됨
colors2.green.map((v) => v * 2); // OK! green이 number[]로 추론됨
```

---

## 요약

- **모듈 시스템**은 IIFE → AMD/CommonJS → ES Modules로 진화했으며, ES Modules가 브라우저와 Node.js 모두의 표준이다
- **Named Export**를 기본으로 사용하고, Default Export는 모듈의 주요 값이 하나일 때만 사용한다
- `import * as`를 통한 **네임스페이스 가져오기**는 모듈 출처를 명확히 하지만, 트리 셰이킹에 불리할 수 있다
- **정적 import**는 사전 분석과 트리 셰이킹에 유리하고, **동적 import**(`import()`)는 코드 분할과 지연 로딩에 유용하다
- **IntersectionObserver**와 동적 import를 결합하면 "화면에 보일 때 로드"하는 고급 최적화가 가능하다
- 모듈은 **한 번만 실행**, **자동 defer**, **스코프 격리**, **트리 셰이킹** 등의 이점을 제공한다
- **클래스**는 React에서는 역할이 줄었지만, Web Components, 디자인 패턴, 데코레이터 기반 프레임워크에서 여전히 핵심이다
- TypeScript의 **매개변수 프로퍼티**, **접근 제한자**, **추상 클래스**, **import type**, **satisfies** 등은 JavaScript를 더 강력하게 만든다
- ES2022~2024의 새로운 기능(top-level await, Change Array by Copy, `using` 키워드 등)은 더 안전하고 표현력 있는 코드를 가능하게 한다

---

## 다른 챕터와의 관계

- **← Ch01 (디자인 패턴 소개)**: 이 챕터에서 다루는 모듈과 클래스 문법이 왜 필요한지, 패턴의 맥락에서 이해할 수 있다
- **→ Ch06 (패턴 카테고리)**: 여기서 배운 `class`, `extends`, `import`/`export`가 생성/구조/행위 패턴 분류의 기반이 된다
- **→ Ch07 (자바스크립트 디자인 패턴)**: 이 챕터의 클래스 문법과 모듈 시스템이 싱글턴, 팩토리, 옵저버 등 패턴의 실제 구현에 직접 사용된다
- **→ Ch08 (자바스크립트 MV* 패턴)**: 모듈을 통한 관심사 분리가 MVC/MVP/MVVM 아키텍처 패턴의 전제 조건이 된다
- **→ Ch12 (리액트 디자인 패턴)**: 동적 가져오기와 `React.lazy()`, IntersectionObserver 기반 지연 로딩이 리액트 성능 최적화 패턴에서 핵심 역할을 한다
