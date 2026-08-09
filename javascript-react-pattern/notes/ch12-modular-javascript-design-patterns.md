# Chapter 12: Modular JavaScript Design Patterns (모듈형 자바스크립트 디자인 패턴)

## 핵심 질문

> 자바스크립트의 모듈 시스템은 어떻게 진화했으며, 현대 애플리케이션에서 모듈을 효과적으로 구성하는 방법은 무엇인가?

---

## 1. 모듈의 중요성

확장 가능한 자바스크립트 환경에서 **모듈형**(*Modular*)이란 서로 의존성이 낮은 기능들이 모듈로 저장된 형태를 뜻한다. 모듈은 세 가지 핵심 가치를 제공한다.

### 느슨한 결합

모듈은 코드를 **느슨한 결합**(*Loose Coupling*)으로 구성하여, 한 부분의 변경이 다른 부분에 미치는 영향을 최소화한다. 각 모듈은 명확한 인터페이스를 통해서만 외부와 소통하므로, 내부 구현을 자유롭게 변경할 수 있다.

### 의존성 관리

모듈 시스템은 의존성을 **명시적으로 선언**하게 한다. `import` 문을 보면 해당 모듈이 무엇에 의존하는지 즉시 파악할 수 있으며, 이는 코드의 이해도와 유지보수성을 크게 높인다.

```typescript
// 의존성이 명시적으로 드러나는 모듈
import { validateEmail, validatePhone } from "./validators";
import { UserRepository } from "./repositories/user";
import { sendWelcomeEmail } from "./services/email";

export async function registerUser(data: RegistrationData): Promise<User> {
  validateEmail(data.email);
  validatePhone(data.phone);
  const user = await UserRepository.create(data);
  await sendWelcomeEmail(user);
  return user;
}
```

### 캡슐화

모듈은 **정보 은닉**(*Information Hiding*)을 실현한다. `export`하지 않은 함수, 변수, 타입은 모듈 외부에서 접근할 수 없다. 이는 모듈의 공개 API를 작게 유지하여 변경의 영향 범위를 제한한다.

> **핵심 통찰**: 모듈의 진정한 가치는 코드를 "파일별로 나누는 것"이 아니라, **변경의 영향 범위를 통제하는 것**에 있다. 좋은 모듈 설계는 "무엇을 숨길 것인가"를 결정하는 것에서 시작한다.

---

## 2. 모듈 시스템의 역사

ES2015 이전, 자바스크립트에는 네이티브 모듈 시스템이 없었다. 이 공백을 메우기 위해 커뮤니티 주도의 여러 모듈 포맷이 등장했다. 현재는 모두 ES Modules로 수렴했지만, 레거시 코드를 이해하고 마이그레이션하기 위해 역사적 맥락을 아는 것이 중요하다.

### AMD (Asynchronous Module Definition)

AMD(*Asynchronous Module Definition*)는 모듈과 의존성 모두를 **비동기적으로 로드**할 수 있도록 설계된 모듈 정의 방식이다. CommonJS의 모듈 형식에 대한 사양 초안으로 시작했지만, 전체적인 합의를 이루지 못해 별도의 amdjs 그룹으로 독립했다. RequireJS와 curl.js 같은 스크립트 로더를 통해 구현되었으며, **브라우저 우선 접근 방식**을 채택하여 빌드 과정 없이도 브라우저에서 모듈을 로딩할 수 있었다.

AMD의 핵심은 `define` 메서드(모듈 정의)와 `require` 메서드(의존성 로딩)다.

```typescript
// AMD 모듈 정의 — define(id?, dependencies?, factory)
define("userModule", ["jquery", "lodash"], function ($, _) {
  // 의존성(jquery, lodash)이 함수 파라미터로 주입된다
  var users = [];

  return {
    addUser: function (name) {
      users.push({ name: name, id: _.uniqueId() });
    },
    render: function () {
      $(".user-list").html(users.map(function (u) { return u.name; }).join(", "));
    },
  };
});
```

AMD는 Dojo, MooTools, jQuery 등의 프로젝트에서 채택되었고, 비동기 로딩과 유연한 모듈 정의라는 장점을 제공했다. 그러나 `define()` 보일러플레이트가 번거롭고, 콜백 기반 API가 코드를 복잡하게 만든다는 단점이 있었다.

### CommonJS

CommonJS는 **서버 사이드**에서 모듈을 선언하는 간단한 API를 제공하는 모듈 형식이다. 2009년 케빈 당구르(*Kevin Dangoor*)가 시작한 ServerJS 프로젝트에서 탄생했으며, Node.js의 기본 모듈 시스템으로 채택되면서 사실상 서버 자바스크립트의 표준이 되었다.

CommonJS의 핵심은 `require` 함수(모듈 가져오기)와 `exports` 객체(모듈 내보내기)다. AMD와 달리 모듈을 함수로 감싸는 작업이 필요하지 않다.

```typescript
// CommonJS 모듈 — require()와 module.exports
const path = require("path");
const fs = require("fs");

function readConfig(configPath) {
  const fullPath = path.resolve(configPath);
  const raw = fs.readFileSync(fullPath, "utf-8");
  return JSON.parse(raw);
}

// 외부로 내보내기
module.exports = { readConfig };
```

CommonJS는 **동기적 로딩** 방식을 사용하기 때문에 파일 시스템 접근이 빠른 서버 환경에 적합했지만, 브라우저 환경에서는 네트워크 지연 문제로 인해 비효율적이었다. 또한 정적 분석이 어려워 트리 쉐이킹(*Tree Shaking*)이 불가능하다는 치명적 한계가 있었다.

### UMD (Universal Module Definition)

UMD(*Universal Module Definition*)는 AMD와 CommonJS의 호환성 문제를 해결하기 위해 등장한 **실험적 모듈 포맷**이다. 런타임에 환경을 감지하여 AMD, CommonJS, 또는 브라우저 전역 객체 중 적절한 방식으로 모듈을 등록한다. 주로 **라이브러리 배포**에 사용되었으나, ES Modules와 번들러의 발전으로 현재는 거의 사용되지 않는다.

### 모듈 포맷 비교

| 특성 | AMD | CommonJS | UMD | ES Modules |
|------|-----|----------|-----|------------|
| **로딩 방식** | 비동기 | 동기 | 환경에 따라 다름 | 비동기 (정적 분석) |
| **주요 환경** | 브라우저 | Node.js | 양쪽 | 양쪽 (표준) |
| **문법** | `define`/`require` | `require`/`exports` | 래퍼 함수 | `import`/`export` |
| **정적 분석** | 불가 | 불가 | 불가 | **가능** |
| **트리 쉐이킹** | 불가 | 불가 | 불가 | **가능** |
| **순환 의존성** | 부분 지원 | 부분 지원 | 해당 없음 | 지원 (주의 필요) |
| **현재 상태** | 레거시 | Node.js에서 여전히 사용 | 레거시 | **현재 표준** |

> **Osmani의 조언**: AMD와 CommonJS는 자바스크립트 모듈화의 초석이 되었다. 이들이 없었다면 ES Modules 표준도 만들어지지 않았을 것이다. 레거시 코드베이스를 다루는 개발자라면 이 역사를 이해하는 것이 마이그레이션의 첫걸음이다.

---

## 3. ES Modules 심화

Ch05에서 `import`/`export`의 기본 문법을 다루었다. 이 장에서는 대규모 애플리케이션에서 ES Modules를 효과적으로 활용하기 위한 **심화 패턴**에 집중한다.

### Named Exports vs Default Exports 전략

두 내보내기 방식은 각각 명확한 용도가 있다.

```typescript
// ✅ Named Exports — 여러 기능을 내보내는 유틸리티 모듈에 적합
// validators.ts
export function validateEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

export function validatePhone(phone: string): boolean {
  return /^\d{10,11}$/.test(phone);
}

export function validateAge(age: number): boolean {
  return age >= 0 && age <= 150;
}
```

```typescript
// ✅ Default Export — 모듈의 주요 기능이 하나일 때 적합
// UserService.ts
export default class UserService {
  async findById(id: string): Promise<User> { /* ... */ }
  async create(data: CreateUserDto): Promise<User> { /* ... */ }
  async delete(id: string): Promise<void> { /* ... */ }
}
```

| 기준 | Named Export | Default Export |
|------|-------------|---------------|
| **IDE 자동 완성** | 우수 (이름이 고정) | 미흡 (임의 이름 가능) |
| **리팩터링** | 안전 (이름 변경 시 모든 import 갱신) | 위험 (import 이름이 제각각) |
| **트리 쉐이킹** | 최적 (사용한 것만 포함) | 모듈 전체 포함 가능성 |
| **사용 시점** | 유틸리티, 상수, 타입 | 클래스, 컴포넌트, 설정 |

> **핵심 통찰**: 현대 TypeScript 프로젝트에서는 **Named Exports를 기본으로 사용**하는 것이 권장된다. Default Export는 React 컴포넌트처럼 "파일 = 하나의 주요 기능"인 경우에 한해 사용한다. Google, Airbnb 등의 스타일 가이드도 Named Exports를 선호한다.

### Re-exporting (Barrel Files)

배럴 파일(*Barrel File*)은 여러 모듈의 export를 하나의 진입점에서 재내보내기(*Re-export*)하는 `index.ts` 파일이다.

```typescript
// models/User.ts
export interface User {
  id: string;
  name: string;
  email: string;
}

// models/Product.ts
export interface Product {
  id: string;
  name: string;
  price: number;
}

// models/Order.ts
export interface Order {
  id: string;
  userId: string;
  products: Product[];
  total: number;
}
```

```typescript
// models/index.ts — 배럴 파일
export { User } from "./User";
export { Product } from "./Product";
export { Order } from "./Order";
```

```typescript
// 사용처 — 깔끔한 import 경로
import { User, Product, Order } from "./models";
```

**배럴 파일의 장단점**:

| 장점 | 단점 |
|------|------|
| import 경로가 깔끔해진다 | **번들 크기 증가** 위험 — 하나만 필요해도 전체가 로드될 수 있다 |
| 모듈의 공개 API를 중앙 관리 | 순환 의존성 발생 가능성 증가 |
| 내부 구조 변경 시 외부 영향 최소화 | **개발 서버 성능 저하** — Vite 등에서 HMR이 느려질 수 있다 |

```typescript
// ⚠️ 안티패턴: 깊은 중첩 배럴
// src/index.ts → features/index.ts → features/auth/index.ts → features/auth/utils/index.ts
// 이렇게 하면 하나의 import가 수십 개의 모듈을 연쇄적으로 로드한다

// ✅ 권장: 기능 경계에서만 배럴 사용
import { LoginForm, useAuth } from "@/features/auth";
```

### Dynamic Import (`import()`)

동적 가져오기(*Dynamic Import*)는 `import()` 함수를 사용하여 모듈을 **런타임에 비동기적으로** 로드하는 기능이다. Promise를 반환하며, 코드 분할(*Code Splitting*)과 조건부 로딩의 핵심 메커니즘이다.

```typescript
// 라우트 기반 코드 분할
async function loadPage(route: string): Promise<void> {
  switch (route) {
    case "/dashboard": {
      const { DashboardPage } = await import("./pages/Dashboard");
      renderPage(DashboardPage);
      break;
    }
    case "/settings": {
      const { SettingsPage } = await import("./pages/Settings");
      renderPage(SettingsPage);
      break;
    }
    default: {
      const { NotFoundPage } = await import("./pages/NotFound");
      renderPage(NotFoundPage);
    }
  }
}
```

```typescript
// 조건부 로딩 — 기능 플래그 기반
async function initAnalytics(config: AppConfig): Promise<void> {
  if (config.features.analytics) {
    const { AnalyticsService } = await import("./services/analytics");
    const analytics = new AnalyticsService(config.analyticsKey);
    analytics.init();
  }
}
```

```typescript
// React에서의 동적 가져오기 — React.lazy
import { lazy, Suspense } from "react";

const AdminPanel = lazy(() => import("./components/AdminPanel"));

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      {isAdmin && <AdminPanel />}
    </Suspense>
  );
}
```

### Import Attributes

Import Attributes(*이전 이름: Import Assertions*)는 모듈을 가져올 때 추가 메타데이터를 제공하는 문법이다. TC39 Stage 3 제안으로 시작되어, JSON 모듈 가져오기가 대표적인 사용 사례다.

```typescript
// JSON 모듈 가져오기 — Import Attributes
import config from "./config.json" with { type: "json" };
// config는 JSON 파일의 default export로 사용 가능

// CSS 모듈 가져오기 (브라우저 네이티브)
import styles from "./styles.css" with { type: "css" };
document.adoptedStyleSheets = [...document.adoptedStyleSheets, styles];
```

> 주의: `assert` 키워드는 폐기되었고, `with` 키워드가 표준이다. 기존 `import ... assert { type: "json" }` 코드는 `import ... with { type: "json" }`으로 마이그레이션해야 한다.

### Top-level Await

Top-level Await(*최상위 await*)는 ES2022에서 표준화된 기능으로, 모듈의 최상위 스코프에서 `async` 함수 없이도 `await`를 사용할 수 있다.

```typescript
// database.ts — Top-level Await로 모듈 초기화
const connection = await createDatabaseConnection({
  host: process.env.DB_HOST,
  port: Number(process.env.DB_PORT),
});

export const db = connection.getDatabase("myapp");

// 이 모듈을 import하는 측은 connection이 완료된 후에야 모듈을 사용할 수 있다
```

```typescript
// config.ts — 환경별 설정 동적 로딩
const env = process.env.NODE_ENV ?? "development";
const { default: config } = await import(`./configs/${env}.json`, {
  with: { type: "json" },
});

export default config;
```

**주의사항**: Top-level Await는 해당 모듈을 import하는 **모든 모듈의 실행을 블로킹**한다. 따라서 앱의 진입점이나 설정 초기화 같은 곳에서만 제한적으로 사용해야 한다.

### 순환 의존성 (Circular Dependencies)

순환 의존성(*Circular Dependency*)은 모듈 A가 모듈 B를 import하고, 모듈 B가 다시 모듈 A를 import하는 상황이다. ES Modules는 순환 의존성을 문법적으로 허용하지만, **런타임에 예상치 못한 `undefined` 값**을 만들 수 있다.

```typescript
// ❌ 순환 의존성 문제
// user.ts
import { createOrder } from "./order";

export interface User {
  id: string;
  name: string;
}

export function createUser(name: string): User {
  return { id: crypto.randomUUID(), name };
}

// order.ts
import { User } from "./user"; // user.ts ↔ order.ts 순환!

export interface Order {
  id: string;
  user: User;
}

export function createOrder(user: User): Order {
  return { id: crypto.randomUUID(), user };
}
```

**해결 방법 1: 공통 모듈 추출**

```typescript
// ✅ types.ts — 공유 타입을 별도 모듈로 추출
export interface User {
  id: string;
  name: string;
}

export interface Order {
  id: string;
  user: User;
}

// user.ts — types만 import
import type { User } from "./types";
export function createUser(name: string): User { /* ... */ }

// order.ts — types만 import
import type { User, Order } from "./types";
export function createOrder(user: User): Order { /* ... */ }
```

**해결 방법 2: 의존성 역전**

```typescript
// ✅ 의존성 역전 — 인터페이스에 의존하게 만들기
// interfaces/OrderCreator.ts
export interface OrderCreator {
  create(userId: string): Promise<Order>;
}

// user.ts — 구체적인 order 모듈 대신 인터페이스에 의존
import type { OrderCreator } from "./interfaces/OrderCreator";

export class UserService {
  constructor(private orderCreator: OrderCreator) {}
  async placeOrder(userId: string) {
    return this.orderCreator.create(userId);
  }
}
```

> **핵심 통찰**: 순환 의존성은 대부분 **모듈의 책임이 명확하지 않다는 설계 신호**다. 타입만 순환하는 경우 `import type`으로 해결할 수 있지만, 런타임 값이 순환하면 반드시 모듈 구조를 재설계해야 한다.

---

## 4. 모듈 디자인 패턴

실제 프로젝트에서 모듈을 효과적으로 구성하기 위한 디자인 패턴들을 살펴본다.

### Barrel Pattern (배럴 패턴)

앞서 다룬 배럴 파일의 체계적인 적용이다. `index.ts`에서 모듈의 **공개 API만 선택적으로 재내보내기**하여, 모듈 경계를 명확히 한다.

```typescript
// features/auth/services/AuthService.ts
export class AuthService {
  async login(email: string, password: string): Promise<AuthToken> { /* ... */ }
  async logout(): Promise<void> { /* ... */ }
  async refreshToken(token: string): Promise<AuthToken> { /* ... */ }

  // 내부용 메서드 — 배럴에서 export하지 않음
  private async validateCredentials(email: string, password: string): Promise<boolean> { /* ... */ }
}

// features/auth/hooks/useAuth.ts
export function useAuth() { /* ... */ }

// features/auth/components/LoginForm.tsx
export function LoginForm() { /* ... */ }

// features/auth/index.ts — 배럴: 공개 API만 노출
export { AuthService } from "./services/AuthService";
export { useAuth } from "./hooks/useAuth";
export { LoginForm } from "./components/LoginForm";
export type { AuthToken, AuthUser } from "./types";
// 내부 유틸리티, 헬퍼 함수 등은 의도적으로 내보내지 않는다
```

### Facade Module Pattern (퍼사드 모듈 패턴)

복잡한 하위 시스템의 여러 모듈을 하나의 **단순화된 인터페이스** 뒤에 감추는 패턴이다.

```typescript
// services/storage/localStorage.ts
export function getItem<T>(key: string): T | null { /* ... */ }
export function setItem<T>(key: string, value: T): void { /* ... */ }

// services/storage/indexedDB.ts
export async function getRecord<T>(store: string, key: string): Promise<T | null> { /* ... */ }
export async function putRecord<T>(store: string, key: string, value: T): Promise<void> { /* ... */ }

// services/storage/cookie.ts
export function getCookie(name: string): string | null { /* ... */ }
export function setCookie(name: string, value: string, days: number): void { /* ... */ }

// services/storage/index.ts — 퍼사드: 저장소 복잡성을 숨김
import * as local from "./localStorage";
import * as idb from "./indexedDB";
import * as cookie from "./cookie";

export type StorageType = "local" | "indexed" | "cookie";

interface StorageOptions {
  type?: StorageType;
  expiry?: number;
}

export async function save<T>(
  key: string,
  value: T,
  options: StorageOptions = { type: "local" }
): Promise<void> {
  switch (options.type) {
    case "indexed":
      return idb.putRecord("app", key, value);
    case "cookie":
      return cookie.setCookie(key, JSON.stringify(value), options.expiry ?? 7);
    case "local":
    default:
      return local.setItem(key, value);
  }
}

export async function load<T>(
  key: string,
  options: StorageOptions = { type: "local" }
): Promise<T | null> {
  switch (options.type) {
    case "indexed":
      return idb.getRecord("app", key);
    case "cookie": {
      const raw = cookie.getCookie(key);
      return raw ? JSON.parse(raw) : null;
    }
    case "local":
    default:
      return local.getItem(key);
  }
}
```

### Plugin/Extension Module Pattern (플러그인/확장 모듈 패턴)

핵심 모듈에 기능을 **동적으로 추가**할 수 있는 확장 가능한 아키텍처를 구성하는 패턴이다.

```typescript
// core/plugin.ts — 플러그인 인터페이스 정의
export interface Plugin<TContext = unknown> {
  name: string;
  version: string;
  install(context: TContext): void | Promise<void>;
  uninstall?(context: TContext): void | Promise<void>;
}

// core/app.ts — 플러그인을 받아들이는 코어
export class App {
  private plugins = new Map<string, Plugin<App>>();
  private config: Record<string, unknown> = {};

  async use(plugin: Plugin<App>): Promise<this> {
    if (this.plugins.has(plugin.name)) {
      throw new Error(`Plugin "${plugin.name}" is already installed.`);
    }
    await plugin.install(this);
    this.plugins.set(plugin.name, plugin);
    return this;
  }

  setConfig(key: string, value: unknown): void {
    this.config[key] = value;
  }

  getConfig<T>(key: string): T | undefined {
    return this.config[key] as T;
  }
}

// plugins/logger.ts — 플러그인 구현
import type { Plugin } from "../core/plugin";
import type { App } from "../core/app";

export const LoggerPlugin: Plugin<App> = {
  name: "logger",
  version: "1.0.0",
  install(app) {
    app.setConfig("logger.level", "info");
    console.log("[Logger] Plugin installed");
  },
};

// main.ts — 사용
const app = new App();
await app.use(LoggerPlugin);
```

### Feature Module Pattern (기능별 모듈 그룹화 패턴)

**기능 단위**(*Feature*)로 관련된 모든 코드(컴포넌트, 훅, 서비스, 타입, 테스트)를 하나의 디렉터리에 모으는 패턴이다. 기술적 역할(components, hooks, services)이 아닌 **비즈니스 도메인**으로 코드를 구성한다.

```
src/
├── features/
│   ├── auth/
│   │   ├── components/
│   │   │   ├── LoginForm.tsx
│   │   │   └── RegisterForm.tsx
│   │   ├── hooks/
│   │   │   └── useAuth.ts
│   │   ├── services/
│   │   │   └── AuthService.ts
│   │   ├── types.ts
│   │   ├── __tests__/
│   │   │   └── AuthService.test.ts
│   │   └── index.ts          ← 배럴 (공개 API)
│   ├── products/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── types.ts
│   │   └── index.ts
│   └── orders/
│       ├── ...
│       └── index.ts
├── shared/                     ← 공통 유틸리티, UI 컴포넌트
│   ├── components/
│   ├── hooks/
│   └── utils/
└── app/                        ← 앱 설정, 라우팅, 레이아웃
    ├── routes.tsx
    └── layout.tsx
```

```typescript
// features/auth/index.ts — 기능 모듈의 공개 API
export { LoginForm } from "./components/LoginForm";
export { RegisterForm } from "./components/RegisterForm";
export { useAuth } from "./hooks/useAuth";
export { AuthService } from "./services/AuthService";
export type { AuthToken, AuthUser, LoginCredentials } from "./types";

// features/orders/services/OrderService.ts — 다른 기능 모듈 사용
import { AuthService } from "@/features/auth"; // 배럴을 통해 import
```

핵심 규칙은 **기능 모듈 간의 import는 반드시 배럴(index.ts)을 통해서만** 이루어져야 한다는 것이다. 이를 통해 각 기능의 내부 구현이 캡슐화된다.

### Side-effect Module Pattern (부수 효과 모듈 패턴)

특정 값을 내보내지 않고, **import되는 것 자체가 목적**인 모듈이다. 폴리필, 전역 설정, CSS 파일 등이 해당된다.

```typescript
// polyfills.ts — 부수 효과 모듈
import "core-js/stable";
import "regenerator-runtime/runtime";

// 전역 에러 핸들러 설정
window.addEventListener("unhandledrejection", (event) => {
  console.error("Unhandled promise rejection:", event.reason);
  reportError(event.reason);
});

// global.css — CSS 부수 효과 모듈
import "./styles/global.css";

// main.ts — 부수 효과 모듈은 값 없이 import만 한다
import "./polyfills";
import "./styles/global.css";

// 이후 앱 코드 시작
import { App } from "./App";
```

`package.json`의 `sideEffects` 필드에서 이 패턴과 트리 쉐이킹의 관계를 관리한다 (5절에서 상세히 다룸).

---

## 5. 현대 빌드 도구와 모듈

모듈 시스템이 표준화되면서, 빌드 도구의 역할은 **모듈을 브라우저에 효율적으로 전달하는 것**으로 변화했다.

### Tree Shaking (트리 쉐이킹)

트리 쉐이킹(*Tree Shaking — 사용하지 않는 코드를 최종 번들에서 제거하는 기법*)은 ES Modules의 **정적 구조**를 활용한다. `import`/`export`가 정적이므로 빌드 타임에 어떤 export가 실제로 사용되는지 분석할 수 있다.

```typescript
// math.ts
export function add(a: number, b: number): number {
  return a + b;
}

export function subtract(a: number, b: number): number {
  return a - b;
}

export function multiply(a: number, b: number): number {
  return a * b;
}

// app.ts — add만 import
import { add } from "./math";
console.log(add(1, 2));
// → subtract, multiply는 최종 번들에서 제거된다
```

**`sideEffects` 플래그**: 번들러에게 "이 패키지의 모듈은 import만으로는 부수 효과가 없다"고 알려주는 `package.json` 설정이다.

```json
{
  "name": "my-library",
  "sideEffects": false
}
```

```json
{
  "name": "my-library",
  "sideEffects": [
    "**/*.css",
    "./src/polyfills.ts"
  ]
}
```

`sideEffects: false`로 설정하면, 번들러는 사용하지 않는 모듈을 과감하게 제거한다. CSS 파일이나 폴리필처럼 부수 효과가 있는 모듈은 배열에 명시해야 한다.

### Code Splitting (코드 분할)

코드 분할(*Code Splitting*)은 애플리케이션을 여러 청크(*Chunk*)로 나누어, 필요한 시점에 필요한 코드만 로드하는 기법이다.

**라우트 기반 분할** — 가장 일반적이고 효과적인 방식이다.

```typescript
// React Router + lazy를 활용한 라우트 기반 코드 분할
import { lazy, Suspense } from "react";
import { createBrowserRouter, RouterProvider } from "react-router-dom";

const Dashboard = lazy(() => import("./pages/Dashboard"));
const Settings = lazy(() => import("./pages/Settings"));
const Analytics = lazy(() => import("./pages/Analytics"));

const router = createBrowserRouter([
  { path: "/dashboard", element: <Dashboard /> },
  { path: "/settings", element: <Settings /> },
  { path: "/analytics", element: <Analytics /> },
]);

function App() {
  return (
    <Suspense fallback={<GlobalSpinner />}>
      <RouterProvider router={router} />
    </Suspense>
  );
}
```

**컴포넌트 기반 분할** — 무거운 컴포넌트를 별도 청크로 분리한다.

```typescript
// 무거운 차트 라이브러리를 필요할 때만 로드
const HeavyChart = lazy(() => import("./components/HeavyChart"));

function AnalyticsPage() {
  const [showChart, setShowChart] = useState(false);

  return (
    <div>
      <button onClick={() => setShowChart(true)}>차트 보기</button>
      {showChart && (
        <Suspense fallback={<ChartSkeleton />}>
          <HeavyChart data={analyticsData} />
        </Suspense>
      )}
    </div>
  );
}
```

### Bundle vs Bundleless

현대 빌드 도구는 **개발 환경과 프로덕션 환경에서 서로 다른 전략**을 사용한다.

| | 개발 환경 (Bundleless) | 프로덕션 환경 (Bundle) |
|---|---|---|
| **전략** | 브라우저 네이티브 ESM 활용 | Rollup 등으로 번들링 |
| **장점** | HMR이 극도로 빠름, 서버 시작 즉시 | HTTP 요청 최소화, 최적화 |
| **단점** | 파일 수만큼 HTTP 요청 | 빌드 시간 소요 |
| **대표 도구** | Vite dev server | Vite build (Rollup), webpack |

Vite(*비트 — 프랑스어로 "빠르다"*)는 이 이중 전략의 대표적 도구다. 개발 시에는 ESM을 네이티브로 제공하고, 프로덕션 빌드에서만 Rollup으로 번들링한다.

### Import Maps (브라우저 네이티브)

Import Maps(*임포트 맵*)는 브라우저에서 **모듈 식별자를 URL로 매핑**하는 기능이다. 번들러 없이도 `import lodash from "lodash"`처럼 베어 스펙파이어(*Bare Specifier — 경로 없이 패키지 이름만 사용하는 import*)를 사용할 수 있다.

```html
<!-- index.html -->
<script type="importmap">
{
  "imports": {
    "react": "https://esm.sh/react@19",
    "react-dom/client": "https://esm.sh/react-dom@19/client",
    "lodash-es": "https://esm.sh/lodash-es@4",
    "@/": "./src/"
  }
}
</script>

<script type="module">
  // Import Map 덕분에 번들러 없이 베어 스펙파이어 사용 가능
  import React from "react";
  import { debounce } from "lodash-es";
</script>
```

Import Maps는 **프로토타이핑, 소규모 프로젝트, CDN 기반 배포**에 유용하다. 대규모 프로젝트에서는 여전히 빌드 도구가 더 나은 최적화를 제공한다.

### 빌드 도구 비교

| 도구 | 개발 서버 | 프로덕션 번들러 | 언어 | 특징 |
|------|-----------|----------------|------|------|
| **Vite** | ESM (네이티브) | Rollup / Rolldown | JS/Go(esbuild) | HMR 극도로 빠름, 프레임워크 통합 우수 |
| **Webpack** | 번들 기반 | 자체 | JS | 풍부한 플러그인 생태계, 레거시 지원 |
| **Turbopack** | 번들 기반 (증분) | 자체 | Rust | Next.js 통합, Webpack 호환 목표 |
| **Rspack** | 번들 기반 | 자체 | Rust | Webpack API 호환, 빠른 빌드 속도 |
| **esbuild** | 자체 | 자체 | Go | 극도로 빠른 트랜스파일링, 단순한 API |

> **Osmani의 조언**: 빌드 도구 선택에서 가장 중요한 것은 속도가 아니라 **프로젝트와 팀의 맥락**이다. 새 프로젝트라면 Vite가 거의 항상 좋은 선택이다. 기존 Webpack 프로젝트의 마이그레이션은 Rspack을 통해 점진적으로 진행할 수 있다.

---

## 6. Node.js의 모듈 이중 체제

Node.js는 CommonJS를 기본 모듈 시스템으로 시작했지만, v13.2.0부터 ES Modules를 안정적으로 지원한다. 현재 Node.js는 **CJS와 ESM의 이중 체제**로 운영되며, 이는 패키지 작성자에게 고유한 과제를 안겨준다.

### CJS vs ESM in Node.js

| 특성 | CommonJS (CJS) | ES Modules (ESM) |
|------|---------------|-------------------|
| **로딩** | 동기 (`require()`) | 비동기 (`import`) |
| **파싱** | 런타임 | 파싱 타임 (정적 분석) |
| **this** | `module.exports` | `undefined` |
| **__filename, __dirname** | 사용 가능 | 사용 불가 (`import.meta.url` 사용) |
| **JSON import** | `require("./data.json")` | `import data from "./data.json" with { type: "json" }` |
| **상호 운용** | ESM을 `import()`로 로드 가능 | CJS를 `import`로 로드 가능 (default export) |

### package.json "type" 필드

`package.json`의 `"type"` 필드는 `.js` 파일의 해석 방식을 결정한다.

```json
{
  "name": "my-esm-package",
  "type": "module"
}
```

| `"type"` 값 | `.js` 파일 해석 | `.mjs` 해석 | `.cjs` 해석 |
|-------------|----------------|-------------|-------------|
| `"module"` | ESM | ESM | CJS |
| `"commonjs"` (기본) | CJS | ESM | CJS |
| 생략 | CJS | ESM | CJS |

### .mjs / .cjs 확장자

`"type"` 설정과 관계없이 모듈 시스템을 **파일 단위**로 명시할 수 있다.

- `.mjs` — 항상 ES Modules로 해석
- `.cjs` — 항상 CommonJS로 해석

```typescript
// utils.mjs — package.json의 "type"과 무관하게 항상 ESM
export function greet(name) {
  return `Hello, ${name}!`;
}

// legacy.cjs — 항상 CJS
const path = require("path");
module.exports = { resolve: path.resolve };
```

### "exports" 필드 (조건부 내보내기)

`package.json`의 `"exports"` 필드는 패키지의 **진입점을 조건에 따라 다르게 지정**하는 기능이다. CJS와 ESM 소비자 모두에게 올바른 파일을 제공하는 핵심 메커니즘이다.

```json
{
  "name": "my-library",
  "type": "module",
  "exports": {
    ".": {
      "import": {
        "types": "./dist/index.d.ts",
        "default": "./dist/index.mjs"
      },
      "require": {
        "types": "./dist/index.d.cts",
        "default": "./dist/index.cjs"
      }
    },
    "./utils": {
      "import": "./dist/utils.mjs",
      "require": "./dist/utils.cjs"
    }
  }
}
```

| 조건 | 의미 |
|------|------|
| `"import"` | `import` 문으로 패키지를 로드할 때 사용 |
| `"require"` | `require()`로 패키지를 로드할 때 사용 |
| `"types"` | TypeScript 타입 정의 파일 경로 |
| `"default"` | 다른 조건에 해당하지 않을 때 기본값 |
| `"browser"` | 브라우저 환경에서의 진입점 |
| `"node"` | Node.js 환경에서의 진입점 |

### Dual Package Hazard (이중 패키지 위험)

이중 패키지 위험(*Dual Package Hazard*)은 하나의 패키지가 CJS와 ESM 두 버전을 제공할 때, **같은 패키지가 두 번 로드**되어 서로 다른 인스턴스가 생기는 문제다.

```typescript
// ⚠️ 이중 패키지 위험 시나리오
// consumer-a.mjs — ESM 버전 로드
import { singleton } from "my-lib"; // → dist/index.mjs의 singleton

// consumer-b.cjs — CJS 버전 로드
const { singleton } = require("my-lib"); // → dist/index.cjs의 다른 singleton!

// 두 singleton은 서로 다른 인스턴스!
```

**해결 방법**: 상태를 갖는 모듈은 **하나의 구현**(보통 CJS)을 두고, ESM 래퍼가 이를 재내보내기하는 방식을 사용한다.

```javascript
// dist/index.cjs — 실제 구현
const state = { count: 0 };
module.exports = {
  increment() { return ++state.count; },
  getCount() { return state.count; },
};

// dist/index.mjs — ESM 래퍼 (CJS 구현을 재내보내기)
import cjs from "./index.cjs";
export const increment = cjs.increment;
export const getCount = cjs.getCount;
```

---

## 최신 업데이트 (2026)

원서 출판(2023) 이후 모듈 생태계에 중요한 변화가 있었다.

| 영역 | 변화 |
|------|------|
| **Import Maps** | 모든 주요 브라우저에서 지원 (Chrome, Firefox, Safari, Edge). Deno에서도 네이티브 지원 |
| **Deno / Bun** | ESM-first 런타임으로 CJS 호환 레이어가 아닌 ESM을 기본으로 사용. Bun은 CJS와 ESM을 동일 파일에서 혼용 가능 |
| **TypeScript moduleResolution** | `"bundler"` 모드 도입 — 번들러의 실제 모듈 해석 방식에 맞춤. `"node16"`/`"nodenext"` 대비 더 유연 |
| **Node.js** | `require(esm)` 실험적 지원 (v22+). CJS에서 ESM 모듈을 동기적으로 require 가능 |
| **Vite 6 / Rolldown** | Rolldown(Rust 기반 번들러)이 Vite의 Rollup을 대체 예정. 개발/프로덕션 빌드 통합 |
| **Import Attributes** | `with` 문법 표준화 진행. JSON, CSS 모듈 가져오기 안정화 |
| **package.json "exports"** | TypeScript의 `"types"` 조건이 사실상 표준으로 정착. `"exports"` 미지원 도구는 거의 사라짐 |

---

## 실무 적용 가이드

### 새 프로젝트 시작 체크리스트

1. **`package.json`에 `"type": "module"` 설정** — ESM을 기본으로 사용
2. **TypeScript `moduleResolution: "bundler"` 설정** — 번들러 환경에 최적화
3. **`sideEffects` 필드 설정** — 트리 쉐이킹 최적화
4. **기능 단위 디렉터리 구조 채택** — Feature Module Pattern 적용
5. **배럴 파일은 기능 경계에서만 사용** — 과도한 중첩 방지

### tsconfig.json 모듈 관련 권장 설정

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "verbatimModuleSyntax": true,
    "isolatedModules": true,
    "esModuleInterop": true
  }
}
```

| 옵션 | 의미 |
|------|------|
| `verbatimModuleSyntax` | `import type`을 강제하여 타입-전용 import를 명확히 함 |
| `isolatedModules` | 파일 단위 트랜스파일링 호환 보장 (Vite, esbuild 등) |
| `moduleResolution: "bundler"` | 번들러의 실제 해석 방식에 맞춘 모듈 해석 |

### 라이브러리 배포 시 package.json 템플릿

```json
{
  "name": "my-library",
  "version": "1.0.0",
  "type": "module",
  "main": "./dist/index.cjs",
  "module": "./dist/index.mjs",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "import": {
        "types": "./dist/index.d.ts",
        "default": "./dist/index.mjs"
      },
      "require": {
        "types": "./dist/index.d.cts",
        "default": "./dist/index.cjs"
      }
    }
  },
  "sideEffects": false,
  "files": ["dist"]
}
```

---

## 요약

- **모듈의 핵심 가치**는 느슨한 결합, 명시적 의존성 관리, 캡슐화를 통해 **변경의 영향 범위를 통제**하는 것이다
- **AMD, CommonJS, UMD**는 ES Modules 이전 시대의 커뮤니티 솔루션이며, 현재는 역사적 맥락으로만 의미가 있다. 다만 Node.js에서는 CommonJS가 여전히 광범위하게 사용된다
- **ES Modules 심화 기법** — Dynamic Import(코드 분할), Import Attributes(JSON/CSS 가져오기), Top-level Await(모듈 초기화), 순환 의존성 해결 — 을 숙지해야 대규모 애플리케이션을 효과적으로 구성할 수 있다
- **모듈 디자인 패턴** — Barrel, Facade, Plugin, Feature Module, Side-effect — 을 통해 프로젝트의 모듈 구조를 체계화할 수 있다
- **트리 쉐이킹과 코드 분할**은 ESM의 정적 구조를 기반으로 작동하며, `sideEffects` 플래그와 `import()` 함수가 핵심 도구다
- **Node.js의 이중 체제**(CJS/ESM)를 이해하고, `"exports"` 필드를 활용하여 다양한 환경의 소비자에게 올바른 모듈을 제공해야 한다
- 새 프로젝트는 **`"type": "module"` + ESM + TypeScript `moduleResolution: "bundler"`** 조합으로 시작하는 것이 권장된다

---

## 다른 챕터와의 관계

- **Ch05 (최신 자바스크립트 문법과 기능)**: `import`/`export`의 기본 문법과 Named/Default Export를 다룬다. 이 장은 그 심화 편이다
- **Ch07 (자바스크립트 디자인 패턴)**: 모듈 패턴(*Module Pattern*), 노출 모듈 패턴(*Revealing Module Pattern*)은 ES Modules 이전에 클로저로 캡슐화를 구현한 방식이다. ESM은 이 패턴들을 언어 수준에서 대체한다
- **Ch09 (비동기 프로그래밍 패턴)**: Dynamic Import와 Top-level Await는 비동기 프로그래밍과 밀접하게 연관된다
- **Ch11 (네임스페이스 패턴)**: 네임스페이스는 전역 스코프 오염을 방지하는 ES Modules 이전의 방식이다. ESM의 모듈 스코프가 이를 근본적으로 해결한다
- **Ch14 (리액트 애플리케이션 구조)**: Feature Module Pattern과 코드 분할(React.lazy)은 리액트 애플리케이션 아키텍처의 핵심이다