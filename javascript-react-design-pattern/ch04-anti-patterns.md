# Chapter 04: Anti-Patterns (안티패턴)

## 핵심 질문

> 안티패턴이란 무엇이며, 올바른 패턴과 어떻게 구분하는가? 자바스크립트와 타입스크립트에서 흔히 발생하는 안티패턴은 무엇이고, 어떻게 탈출할 수 있는가?

---

## 1. 안티패턴의 정의와 기원

**안티패턴**(*Anti-Pattern — 문제를 해결하는 것처럼 보이지만 실제로는 더 큰 문제를 야기하는 잘못된 설계*)이라는 용어는 1995년 앤드루 쾨니히(*Andrew Koenig*)가 GoF의 디자인 패턴에서 영감을 받아 처음 만들었다. 디자인 패턴이 "반복되는 문제에 대한 검증된 해결책"이라면, 안티패턴은 "반복되는 문제에 대한 **검증된 나쁜 해결책**"이다.

안티패턴에는 두 가지 핵심 개념이 담겨 있다:

| 개념 | 설명 |
|------|------|
| **잘못된 해결책** | 특정 문제에 대해 겉보기에는 해결하는 것 같지만, 실제로는 상황을 악화시키는 접근 방식 |
| **올바른 해결책에 이르는 방법** | 잘못된 상황에서 벗어나 올바른 설계로 전환하는 구체적인 경로 |

두 번째 개념이 특히 중요하다. 안티패턴을 아는 것의 가치는 "이렇게 하지 마라"는 경고에만 있는 것이 아니라, **잘못된 설계에서 올바른 설계로 리팩터링하는 구체적인 경로를 제시**하는 데 있다.

### 안티패턴을 배워야 하는 이유

크리스토퍼 알렉산더는 좋은 설계(good design)와 좋은 컨텍스트(good context) 사이의 균형을 강조했다. 이 균형이 무너지면 안티패턴이 발생한다.

| 상황 | 결과 |
|------|------|
| 좋은 설계 + 좋은 컨텍스트 | **패턴** — 올바른 해결책 |
| 나쁜 설계 + 좋은 컨텍스트 | **안티패턴** — 상황은 맞지만 접근이 잘못됨 |
| 좋은 설계 + 나쁜 컨텍스트 | **오용** — 올바른 패턴을 잘못된 상황에 적용 |
| 나쁜 설계 + 나쁜 컨텍스트 | **혼란** — 전면 재설계 필요 |

> **핵심 통찰**: 안티패턴을 이해하는 것은 디자인 패턴을 아는 것만큼이나 중요하다. 패턴을 배우면 "무엇을 해야 하는지" 알 수 있지만, 안티패턴을 배우면 "무엇을 하지 말아야 하는지"와 "잘못된 길에서 어떻게 빠져나오는지"를 알 수 있다.

---

## 2. 자바스크립트의 전통적 안티패턴

Osmani는 자바스크립트에서 흔히 볼 수 있는 안티패턴 목록을 제시한다. 이 안티패턴들은 자바스크립트의 유연한 특성에서 비롯된 것이 많다.

### 2.1 전역 네임스페이스 오염

전역 네임스페이스 오염(*Global Namespace Pollution*)은 자바스크립트에서 가장 오래되고 가장 흔한 안티패턴이다. 전역 스코프에 변수와 함수를 무분별하게 선언하면 이름 충돌, 예측 불가능한 버그, 메모리 누수 등이 발생한다.

```typescript
// 안티패턴: 전역 네임스페이스 오염
var config = { apiUrl: "https://api.example.com" };
var currentUser = null;
var isAuthenticated = false;

function login(username: string, password: string): void {
  currentUser = username;
  isAuthenticated = true;
}

// 다른 스크립트가 같은 이름의 전역 변수를 사용하면 충돌
// 어디서 전역 변수가 수정되었는지 추적 불가
```

```typescript
// 탈출 경로: 모듈 시스템 사용
// auth.ts
interface AuthState {
  currentUser: string | null;
  isAuthenticated: boolean;
}

const state: AuthState = {
  currentUser: null,
  isAuthenticated: false,
};

export function login(username: string, password: string): void {
  state.currentUser = username;
  state.isAuthenticated = true;
}

export function getCurrentUser(): string | null {
  return state.currentUser;
}
// 모듈 스코프 안에 캡슐화되어 전역 오염 없음
```

### 2.2 setTimeout/setInterval에 문자열 전달

`setTimeout`이나 `setInterval`에 함수 대신 문자열을 전달하면 내부적으로 `eval()`이 호출된다. 이는 보안 취약점과 성능 저하를 야기한다.

```typescript
// 안티패턴: 문자열 전달 — 내부적으로 eval() 호출
setTimeout("console.log('hello')", 1000);
setInterval("updateCounter()", 500);

// 문제점:
// 1. eval()과 동일한 보안 위험 (코드 인젝션 가능)
// 2. 스코프 체인 접근 불가
// 3. JS 엔진의 최적화 불가
// 4. TypeScript에서 타입 검사 불가
```

```typescript
// 탈출 경로: 함수 참조를 전달
setTimeout(() => console.log("hello"), 1000);
setInterval(updateCounter, 500);
```

### 2.3 Object.prototype 수정

자바스크립트의 기본 객체 프로토타입을 수정하면 모든 객체에 영향을 미쳐 예측 불가능한 동작이 발생한다.

```typescript
// 안티패턴: 네이티브 프로토타입 수정
Object.prototype.hasProperty = function (key: string): boolean {
  return this.hasOwnProperty(key);
};

Array.prototype.unique = function <T>(): T[] {
  return [...new Set(this)];
};

// 문제점:
// 1. for...in 루프에서 예상치 못한 속성이 열거됨
// 2. 서드파티 라이브러리와 충돌 가능
// 3. 향후 ECMAScript 표준에 같은 이름의 메서드가 추가되면 충돌
```

```typescript
// 탈출 경로: 유틸리티 함수로 분리
function hasProperty(obj: Record<string, unknown>, key: string): boolean {
  return Object.prototype.hasOwnProperty.call(obj, key);
}

function unique<T>(arr: T[]): T[] {
  return [...new Set(arr)];
}
```

### 2.4 인라인 자바스크립트

HTML 내에 자바스크립트를 직접 작성하면 관심사의 분리 원칙을 위반하고 유지보수가 어려워진다.

```html
<!-- 안티패턴: 인라인 자바스크립트 -->
<button onclick="handleClick()">클릭</button>
<div onmouseover="this.style.color='red'">호버</div>
```

```typescript
// 탈출 경로: 이벤트 리스너 분리
const button = document.querySelector<HTMLButtonElement>("#myButton");
button?.addEventListener("click", handleClick);

// React/현대 프레임워크에서는 JSX를 사용하되 로직을 분리
function ClickButton(): JSX.Element {
  const handleClick = (): void => {
    console.log("clicked");
  };
  return <button onClick={handleClick}>클릭</button>;
}
```

### 2.5 document.write 사용

`document.write()`는 페이지 로딩이 완료된 후 호출하면 전체 DOM을 덮어쓴다. 현대 웹 개발에서는 사용을 피해야 한다.

```typescript
// 안티패턴
document.write("<h1>Hello World</h1>");

// 문제점:
// 1. 페이지 로딩 후 호출하면 기존 DOM 전체가 삭제됨
// 2. 비동기 스크립트에서 호출 시 예측 불가능한 결과
// 3. 성능 문제 (파서 차단)
// 4. CSP(Content Security Policy) 위반 가능
```

```typescript
// 탈출 경로: DOM API 사용
const heading = document.createElement("h1");
heading.textContent = "Hello World";
document.body.appendChild(heading);
```

> **Osmani의 조언**: 위의 전통적 안티패턴들은 경험 많은 개발자에게는 당연한 것처럼 보일 수 있다. 하지만 이러한 안티패턴들이 여전히 레거시 코드베이스에 존재하며, 안티패턴을 인식하는 것이 리팩터링의 첫걸음이다.

---

## 3. 패턴과 안티패턴의 경계

**완벽한 설계도 잘못된 상황에서 사용되면 안티패턴이 된다.** 이 원칙은 매우 중요하다. 패턴과 안티패턴의 경계는 고정되어 있지 않으며, 적용 상황(컨텍스트)에 따라 달라진다.

### 패턴이 안티패턴이 되는 조건

| 패턴 | 올바른 사용 (패턴) | 잘못된 사용 (안티패턴) |
|------|---------------------|------------------------|
| **싱글턴** | DB 연결 풀, 로거 | 모든 서비스 클래스를 싱글턴으로 만듦 |
| **옵저버** | UI 이벤트 시스템 | 수백 개의 구독자가 얽힌 이벤트 스파게티 |
| **팩토리** | 복잡한 객체 생성 | 단순 객체까지 팩토리로 생성 (과잉 설계) |
| **데코레이터** | 기능의 동적 추가 | 10겹 이상의 데코레이터 래핑 (디버깅 불가) |
| **공급자 패턴** | 테마, 인증 등 전역 상태 | 모든 상태를 하나의 Context에 넣음 (불필요한 리렌더링) |

```typescript
// 예: 싱글턴 패턴의 양면

// 올바른 사용: DB 연결 풀 — 실제로 하나만 있어야 하는 리소스
class DatabasePool {
  private static instance: DatabasePool | null = null;
  private constructor(private pool: Connection[]) {}

  static getInstance(): DatabasePool {
    if (!DatabasePool.instance) {
      DatabasePool.instance = new DatabasePool(createPool());
    }
    return DatabasePool.instance;
  }
}

// 안티패턴: 모든 서비스를 싱글턴으로 — 테스트와 의존성 주입 불가능
class UserService {
  private static instance: UserService | null = null;
  private constructor() {}

  static getInstance(): UserService {
    if (!UserService.instance) {
      UserService.instance = new UserService();
    }
    return UserService.instance;
  }
  // 테스트에서 이 서비스를 모킹하기 어렵다
  // 다른 구현으로 교체하기 어렵다
}
```

```tsx
// 예: Context(공급자 패턴)의 양면

// 안티패턴: 모든 상태를 하나의 Context에 넣음
interface AppState {
  user: User | null;
  theme: Theme;
  cart: CartItem[];
  notifications: Notification[];
  searchResults: SearchResult[];
}

const AppContext = createContext<AppState>(defaultState);
// 문제: searchResults만 변경되어도 user, theme를 사용하는 모든 컴포넌트가 리렌더링

// 올바른 사용: 관심사별로 Context 분리
const UserContext = createContext<User | null>(null);
const ThemeContext = createContext<Theme>(defaultTheme);
const CartContext = createContext<CartState>(defaultCart);
// 각 Context는 독립적으로 변경되며 불필요한 리렌더링이 없다
```

> **핵심 통찰**: 패턴과 안티패턴의 경계는 고정되어 있지 않다. 동일한 설계라도 **컨텍스트**(적용 상황)에 따라 패턴이 될 수도, 안티패턴이 될 수도 있다. 패턴을 적용할 때는 항상 "이 상황에서 이 패턴이 적합한가?"라는 질문을 먼저 해야 한다.

---

## 4. 현대 TypeScript/JavaScript 안티패턴 (2026)

원서에서 다룬 전통적 안티패턴 외에, 현대 TypeScript와 React 생태계에서 새롭게 등장한 안티패턴들이 있다. 이 안티패턴들은 도구와 프레임워크의 발전에도 불구하고 여전히 많은 프로젝트에서 발견된다.

### 4.1 `any` 타입 남용

TypeScript를 사용하면서 `any`를 남발하면 타입 시스템의 이점을 모두 잃게 된다. "TypeScript를 사용하고 있다"는 착각만 남는다.

```typescript
// 안티패턴: any 남용 — "TypeScript를 사용하는 척하는 JavaScript"
function processData(data: any): any {
  return data.items.map((item: any) => ({
    id: item.id,
    name: item.name,
    // 런타임에 item.name이 존재하지 않으면 undefined가 조용히 전파됨
  }));
}

async function fetchUser(id: any): Promise<any> {
  const response = await fetch(`/api/users/${id}`);
  return response.json(); // 반환 타입도 any
}
```

```typescript
// 탈출 경로: 명시적 타입 정의와 unknown 사용
interface ApiResponse<T> {
  items: T[];
  total: number;
}

interface UserItem {
  id: string;
  name: string;
}

function processData(data: ApiResponse<UserItem>): UserItem[] {
  return data.items.map((item) => ({
    id: item.id,
    name: item.name,
  }));
}

// 외부 데이터는 unknown으로 받고 검증 후 사용
async function fetchUser(id: string): Promise<User> {
  const response = await fetch(`/api/users/${id}`);
  const data: unknown = await response.json();

  // Zod 등의 런타임 검증 라이브러리 활용
  return userSchema.parse(data);
}
```

| `any` 사용이 합리적인 경우 | 대안 |
|----------------------------|------|
| 서드파티 라이브러리에 타입이 없을 때 | `@types/*` 패키지 검색 또는 직접 타입 선언 |
| 마이그레이션 중간 단계 | `// @ts-expect-error`와 TODO 코멘트 병행 |
| 정말로 모든 타입을 허용해야 할 때 | `unknown` + 타입 가드 |

### 4.2 배럴 파일의 무분별한 사용

배럴 파일(*Barrel File — `index.ts`에서 여러 모듈을 re-export하는 파일*)은 import를 깔끔하게 만들어 주지만, 과도하게 사용하면 번들 크기 증가와 순환 의존성 문제를 야기한다.

```typescript
// 안티패턴: 깊은 배럴 파일 체인
// components/index.ts
export * from "./Button";
export * from "./Modal";
export * from "./Table";
export * from "./Chart";    // 무거운 차트 라이브러리 포함
export * from "./DatePicker"; // 무거운 날짜 라이브러리 포함

// pages/Dashboard.tsx
import { Button } from "@/components"; // Button만 필요하지만
// → 트리 셰이킹이 완벽하지 않으면 Chart, DatePicker 등도 번들에 포함됨
```

```typescript
// 탈출 경로: 직접 import 또는 선별적 배럴 파일

// 방법 1: 직접 import
import { Button } from "@/components/Button";

// 방법 2: 가벼운 컴포넌트만 배럴 파일에 포함
// components/index.ts
export * from "./Button";
export * from "./Input";
export * from "./Label";
// 무거운 컴포넌트는 직접 import하도록 배럴에서 제외

// 방법 3: package.json의 exports 필드 활용
// package.json
{
  "exports": {
    "./button": "./dist/components/Button.js",
    "./chart": "./dist/components/Chart.js"
  }
}
```

### 4.3 불필요한 추상화 (Over-Engineering)

"나중에 필요할지도 모른다"는 이유로 불필요한 추상 계층을 만드는 것은 코드의 복잡성만 증가시킨다.

```typescript
// 안티패턴: 과도한 추상화 — 단순한 API 호출에 3개의 추상 계층

// Layer 1: 추상 HTTP 클라이언트
abstract class BaseHttpClient {
  abstract get<T>(url: string): Promise<T>;
  abstract post<T>(url: string, data: unknown): Promise<T>;
}

// Layer 2: 추상 리포지토리
abstract class BaseRepository<T> {
  constructor(protected client: BaseHttpClient) {}
  abstract findAll(): Promise<T[]>;
  abstract findById(id: string): Promise<T>;
}

// Layer 3: 구체 리포지토리
class UserRepository extends BaseRepository<User> {
  findAll(): Promise<User[]> {
    return this.client.get("/api/users");
  }
  findById(id: string): Promise<User> {
    return this.client.get(`/api/users/${id}`);
  }
}

// 실제로는 이 모든 것이 fetch() 한 줄이면 충분한 경우가 대부분이다
```

```typescript
// 탈출 경로: YAGNI 원칙 — 필요할 때 추상화하라

// 시작: 단순한 함수로 충분
async function getUsers(): Promise<User[]> {
  const response = await fetch("/api/users");
  return response.json();
}

async function getUserById(id: string): Promise<User> {
  const response = await fetch(`/api/users/${id}`);
  return response.json();
}

// 반복이 3회 이상 발생하면 그때 추상화를 고려 (Ch02의 Rule of Three)
// 필요시 점진적으로 추상화 계층 추가
```

> **핵심 통찰**: YAGNI(*You Aren't Gonna Need It — 지금 필요하지 않은 것을 미리 만들지 마라*)는 안티패턴을 방지하는 핵심 원칙이다. Ch02에서 배운 "세 가지 법칙"처럼, 추상화도 최소 세 번의 반복이 확인된 후에 도입하는 것이 안전하다.

### 4.4 Prop Drilling 대신 컴포지션 미활용

React에서 깊은 컴포넌트 트리를 통해 props를 전달하는 것은 대표적인 안티패턴이다. Ch01에서 공급자 패턴으로 해결하는 방법을 살펴보았지만, 여기서는 Context API 외의 대안도 함께 살펴본다.

```tsx
// 안티패턴: 4단계 이상의 prop drilling
function App() {
  const [theme, setTheme] = useState<Theme>("light");
  return <Layout theme={theme} setTheme={setTheme} />;
}

function Layout({ theme, setTheme }: LayoutProps) {
  return <Sidebar theme={theme} setTheme={setTheme} />;
}

function Sidebar({ theme, setTheme }: SidebarProps) {
  return <ThemeToggle theme={theme} setTheme={setTheme} />;
}

function ThemeToggle({ theme, setTheme }: ThemeToggleProps) {
  return (
    <button onClick={() => setTheme(theme === "light" ? "dark" : "light")}>
      {theme}
    </button>
  );
}
```

```tsx
// 탈출 경로 1: 컴포지션 패턴 (children 활용)
function App() {
  const [theme, setTheme] = useState<Theme>("light");
  return (
    <Layout>
      <Sidebar>
        <ThemeToggle theme={theme} setTheme={setTheme} />
      </Sidebar>
    </Layout>
  );
}

// Layout과 Sidebar는 theme에 대해 알 필요가 없다
function Layout({ children }: { children: React.ReactNode }) {
  return <div className="layout">{children}</div>;
}

function Sidebar({ children }: { children: React.ReactNode }) {
  return <aside>{children}</aside>;
}
```

```tsx
// 탈출 경로 2: 상태 관리 라이브러리 (Zustand 예시)
import { create } from "zustand";

interface ThemeStore {
  theme: Theme;
  toggle: () => void;
}

const useThemeStore = create<ThemeStore>((set) => ({
  theme: "light",
  toggle: () =>
    set((state) => ({
      theme: state.theme === "light" ? "dark" : "light",
    })),
}));

// 어떤 깊이의 컴포넌트에서든 직접 접근 가능
function ThemeToggle() {
  const { theme, toggle } = useThemeStore();
  return <button onClick={toggle}>{theme}</button>;
}
```

### 4.5 useEffect 만능주의

React의 `useEffect`를 모든 로직의 만능 도구로 사용하는 것은 흔한 안티패턴이다. 불필요한 `useEffect`는 성능 저하, 무한 루프, 예측 불가능한 동작을 야기한다.

```tsx
// 안티패턴 1: 파생 상태를 useEffect로 계산
function FilteredList({ items, query }: FilteredListProps) {
  const [filteredItems, setFilteredItems] = useState<Item[]>([]);

  // 불필요한 useEffect — 렌더링 중에 계산하면 충분하다
  useEffect(() => {
    setFilteredItems(items.filter((item) => item.name.includes(query)));
  }, [items, query]);

  return <ul>{filteredItems.map(/* ... */)}</ul>;
}

// 안티패턴 2: 이벤트 핸들러 로직을 useEffect에 넣기
function Form() {
  const [submitted, setSubmitted] = useState(false);

  // 불필요한 useEffect — 이벤트 핸들러에서 직접 처리하면 된다
  useEffect(() => {
    if (submitted) {
      sendAnalytics("form_submitted");
      setSubmitted(false);
    }
  }, [submitted]);

  return <button onClick={() => setSubmitted(true)}>제출</button>;
}
```

```tsx
// 탈출 경로 1: 파생 상태는 useMemo 또는 렌더링 중 직접 계산
function FilteredList({ items, query }: FilteredListProps) {
  const filteredItems = useMemo(
    () => items.filter((item) => item.name.includes(query)),
    [items, query]
  );

  return <ul>{filteredItems.map(/* ... */)}</ul>;
}

// 탈출 경로 2: 이벤트 핸들러에서 직접 처리
function Form() {
  const handleSubmit = (): void => {
    sendAnalytics("form_submitted");
    // 추가 로직...
  };

  return <button onClick={handleSubmit}>제출</button>;
}
```

### useEffect가 적절한 경우 vs 아닌 경우

| useEffect가 적절한 경우 | useEffect가 불필요한 경우 |
|--------------------------|----------------------------|
| 외부 시스템과의 동기화 (WebSocket, DOM API) | 파생 상태 계산 |
| 컴포넌트 마운트 시 데이터 페칭 | 이벤트 핸들러 로직 |
| 브라우저 API 구독/해제 | props/state에서 바로 계산 가능한 값 |
| 타이머 설정/해제 | 다른 state를 동기화하기 위한 상태 업데이트 |

### 4.6 조기 최적화 (Premature Optimization)

성능 문제가 실제로 발생하기 전에 복잡한 최적화를 적용하는 것은 코드 복잡성만 증가시킨다.

```tsx
// 안티패턴: 모든 컴포넌트에 React.memo, useMemo, useCallback 적용
const UserCard = React.memo(({ user }: { user: User }) => {
  const formattedName = useMemo(
    () => `${user.firstName} ${user.lastName}`, // 문자열 결합에 useMemo?
    [user.firstName, user.lastName]
  );

  const handleClick = useCallback(() => {
    console.log(user.id); // 단순 로깅에 useCallback?
  }, [user.id]);

  return <div onClick={handleClick}>{formattedName}</div>;
});
```

```tsx
// 탈출 경로: 먼저 측정하고, 필요할 때만 최적화
function UserCard({ user }: { user: User }) {
  // 단순한 연산은 그냥 실행
  const formattedName = `${user.firstName} ${user.lastName}`;

  const handleClick = (): void => {
    console.log(user.id);
  };

  return <div onClick={handleClick}>{formattedName}</div>;
}

// React DevTools Profiler로 실제 병목을 확인한 후에만 메모이제이션 적용
// React 19의 React Compiler는 많은 경우 자동 메모이제이션을 수행한다
```

> **Osmani의 조언**: "최적화는 측정에서 시작한다." React DevTools의 Profiler, Chrome DevTools의 Performance 탭 등으로 **실제 병목 지점**을 먼저 확인하라. 추측에 기반한 최적화는 대부분 시간 낭비다.

### 4.7 신 컴포넌트 (God Component)

하나의 컴포넌트에 너무 많은 책임을 부여하면 테스트, 재사용, 유지보수가 모두 어려워진다.

```tsx
// 안티패턴: 하나의 컴포넌트에 모든 것을 담는 "신 컴포넌트"
function DashboardPage() {
  const [user, setUser] = useState<User | null>(null);
  const [posts, setPosts] = useState<Post[]>([]);
  const [comments, setComments] = useState<Comment[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("posts");
  const [searchQuery, setSearchQuery] = useState("");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedPost, setSelectedPost] = useState<Post | null>(null);
  // ... 20개 이상의 useState

  useEffect(() => { /* 사용자 페칭 */ }, []);
  useEffect(() => { /* 게시물 페칭 */ }, [user]);
  useEffect(() => { /* 댓글 페칭 */ }, [selectedPost]);
  useEffect(() => { /* 알림 구독 */ }, []);
  // ... 10개 이상의 useEffect

  // 300줄 이상의 JSX...
  return (
    <div>
      {/* 헤더, 탭, 검색, 목록, 모달, 푸터 등 모두 한 컴포넌트 안에 */}
    </div>
  );
}
```

```tsx
// 탈출 경로: 관심사별 분리 + 커스텀 훅 추출

// 1. 데이터 로직을 커스텀 훅으로 추출
function useDashboardData(userId: string) {
  const { data: user } = useQuery({
    queryKey: ["user", userId],
    queryFn: fetchUser,
  });
  const { data: posts } = useQuery({
    queryKey: ["posts", userId],
    queryFn: fetchPosts,
  });
  return { user, posts };
}

// 2. UI 상태를 커스텀 훅으로 추출
function useDashboardUI() {
  const [activeTab, setActiveTab] = useState("posts");
  const [searchQuery, setSearchQuery] = useState("");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  return {
    activeTab, setActiveTab,
    searchQuery, setSearchQuery,
    sortOrder, setSortOrder,
  };
}

// 3. 컴포넌트를 관심사별로 분리
function DashboardPage() {
  const { user, posts } = useDashboardData("user-1");
  const { activeTab, setActiveTab } = useDashboardUI();

  return (
    <div>
      <DashboardHeader user={user} />
      <TabNavigation active={activeTab} onChange={setActiveTab} />
      <PostList posts={posts} />
      <NotificationPanel />
    </div>
  );
}
```

### 신 컴포넌트의 징후 체크리스트

- [ ] `useState`가 5개 이상
- [ ] `useEffect`가 3개 이상
- [ ] JSX가 200줄 이상
- [ ] 한 파일이 300줄 이상
- [ ] 컴포넌트 이름에 "Page", "Container", "Main" 등 포괄적 이름 사용

위 항목 중 3개 이상 해당하면 분리를 고려해야 한다.

---

## 5. 안티패턴 인식과 탈출 프로세스

안티패턴을 인식하고 올바른 패턴으로 전환하는 일반적인 프로세스를 정리한다.

### 4단계 탈출 프로세스

```
[1. 인식] → [2. 영향 분석] → [3. 대안 탐색] → [4. 점진적 전환]
```

| 단계 | 활동 | 산출물 |
|------|------|--------|
| **1. 인식** | 코드 리뷰, 린터 경고, 성능 프로파일링으로 안티패턴 발견 | 안티패턴 목록 |
| **2. 영향 분석** | 이 안티패턴이 미치는 구체적 영향 측정 (번들 크기, 렌더링 횟수 등) | 영향도 보고서 |
| **3. 대안 탐색** | 올바른 패턴 후보를 비교 검토 | 대안 패턴 비교표 |
| **4. 점진적 전환** | 한 번에 전면 교체가 아닌 점진적 리팩터링 | 리팩터링된 코드 |

### ESLint로 자동 감지 가능한 안티패턴

```typescript
// .eslintrc.json 설정으로 안티패턴 자동 감지
const eslintConfig = {
  rules: {
    // any 타입 사용 금지
    "@typescript-eslint/no-explicit-any": "error",

    // 타입 단언 제한
    "@typescript-eslint/consistent-type-assertions": [
      "error",
      { assertionStyle: "never" },
    ],

    // eval 및 문자열 기반 setTimeout 금지
    "no-eval": "error",
    "no-implied-eval": "error",

    // prototype 수정 금지
    "no-extend-native": "error",

    // var 사용 금지 (전역 오염 방지)
    "no-var": "error",

    // React Hook 의존성 배열 검사
    "react-hooks/exhaustive-deps": "warn",
  },
};
```

> **핵심 통찰**: 안티패턴의 가장 위험한 특성은 **단기적으로는 작동한다**는 점이다. 문제가 드러나는 것은 코드베이스가 성장하고, 팀원이 늘어나고, 요구 사항이 변경될 때다. 따라서 안티패턴은 코드 리뷰와 자동화 도구를 통해 **조기에 발견하는 것**이 가장 중요하다.

### 전통 vs 현대 안티패턴 비교

| 전통적 안티패턴 | 현대적 안티패턴 (2026) |
|-----------------|------------------------|
| 전역 변수 오염 | 전역 상태 관리 라이브러리 남용 |
| `document.write` | `dangerouslySetInnerHTML` 남용 |
| 콜백 지옥 | `useEffect` 체이닝 지옥 |
| `eval()` 사용 | `any` 타입으로 타입 시스템 무력화 |
| `Object.prototype` 수정 | 모듈 사이드 이펙트 (import 시 전역 상태 변경) |
| 인라인 JS | 인라인 스타일 객체 매 렌더링 재생성 |

---

## 요약

- **안티패턴**은 앤드루 쾨니히가 1995년 GoF에서 영감을 받아 만든 용어로, **잘못된 해결책**과 **올바른 해결책으로의 탈출 경로**를 함께 기술한다
- 안티패턴을 배우는 것은 패턴을 배우는 것만큼 중요하다 — "하지 말아야 할 것"을 아는 것이 좋은 설계의 절반이다
- 자바스크립트의 전통적 안티패턴: **전역 네임스페이스 오염**, **setTimeout 문자열 전달**, **Object.prototype 수정**, **인라인 JS**, **document.write**
- **완벽한 설계도 잘못된 상황에서 사용되면 안티패턴이 된다** — 패턴 적용 시 항상 컨텍스트를 고려해야 한다
- 현대 TypeScript/React 안티패턴: **`any` 남용**, **배럴 파일 과용**, **불필요한 추상화**, **prop drilling**, **useEffect 만능주의**, **조기 최적화**, **신 컴포넌트**
- 안티패턴 탈출은 **인식 → 영향 분석 → 대안 탐색 → 점진적 전환**의 4단계 프로세스를 따른다
- ESLint와 TypeScript strict 모드를 활용하면 많은 안티패턴을 자동으로 감지할 수 있다

---

## 다른 챕터와의 관계

- **← Ch01 (디자인 패턴 소개)**: Ch01에서 "좋은 패턴"을 배웠다면, 이 챕터는 그 **정반대**인 안티패턴을 다룬다
- **← Ch02 (프로토 패턴)**: 패턴성 검증을 통과하지 못한 해결책이 널리 퍼지면 안티패턴이 될 수 있다. 프로토 패턴과 안티패턴의 경계를 이해하는 것이 중요하다
- **← Ch03 (패턴 구조화)**: 안티패턴도 패턴과 동일한 구조(컨텍스트, 문제, 잘못된 해결책, 올바른 해결책)로 문서화할 수 있다
- **→ Ch05 (최신 자바스크립트 문법)**: 모듈 시스템, 클래스, 화살표 함수 등 현대 문법이 전통적 안티패턴 다수를 언어 차원에서 해결했음을 확인할 수 있다
- **→ Ch07 (디자인 패턴)**: 각 안티패턴의 "탈출 경로"가 Ch07에서 다루는 정식 패턴(옵저버, 전략, 모듈 등)과 연결된다
- **→ Ch12~14 (리액트 패턴)**: useEffect 남용, prop drilling, 신 컴포넌트 등 React 특화 안티패턴의 해결책이 리액트 패턴 챕터에서 상세히 다루어진다