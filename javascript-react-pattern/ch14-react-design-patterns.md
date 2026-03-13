# Chapter 14: React Design Patterns (리액트 디자인 패턴)

## 핵심 질문

> 리액트에서 컴포넌트의 재사용성과 관심사 분리를 달성하기 위한 디자인 패턴은 무엇이며, React 19 시대에 어떤 패턴이 권장되는가?

---

## 1. 리액트 소개와 핵심 개념

리액트(*React*)는 2013년 메타(구 페이스북)에서 개발한 UI 라이브러리로, 인터페이스를 **컴포넌트**, **Props**, **상태**라는 세 가지 핵심 개념으로 나누어 관리한다. 리액트는 구성(*composition*)에 초점을 맞추고 있어 디자인 시스템의 요소들과 자연스럽게 연결되며, 페이지 단위가 아닌 **컴포넌트 단위**로 사고하는 모듈화된 접근 방식을 요구한다.

### JSX

JSX(*JavaScript XML*)는 XML과 유사한 구문을 사용하여 HTML을 자바스크립트에서 사용할 수 있게 해주는 확장 문법이다. JSX는 리액트와 함께 인기를 얻었지만 다른 라이브러리에서도 널리 사용된다.

```tsx
// JSX는 자바스크립트로 변환된다
const element = <h1 className="greeting">Hello, world!</h1>;

// 위 코드는 아래와 동일하다
const element = React.createElement("h1", { className: "greeting" }, "Hello, world!");
```

### 컴포넌트

컴포넌트(*Component*)는 리액트의 기본 구성 요소다. 입력값(Props)을 받아 화면에 표시할 내용을 나타내는 리액트 요소를 반환하는 함수이며, UI를 독립적이고 재사용 가능한 조각으로 나눌 수 있게 해준다.

```tsx
interface GreetingProps {
  name: string;
}

function Greeting({ name }: GreetingProps) {
  return <h1>Hello, {name}!</h1>;
}
```

### Props와 상태

**Props**(*Properties*)는 상위 컴포넌트에서 하위 컴포넌트로 전달되는 읽기 전용 데이터다. 한 번 전달되면 컴포넌트 내부에서 변경할 수 없다.

**상태**(*State*)는 컴포넌트의 라이프사이클 동안 값이 변할 수 있는 정보를 담고 있는 객체다. 시간이 지남에 따라 변하는 데이터를 관리하는 기술을 **상태 관리**(*State Management*)라고 한다.

### CSR과 SSR

| 렌더링 방식 | 설명 | 특징 |
|------------|------|------|
| **CSR** (*Client-Side Rendering*) | 서버가 기본 HTML 컨테이너만 전송하고, 로직·라우팅·렌더링은 클라이언트 자바스크립트가 처리 | SPA에 적합, 높은 상호작용성 |
| **SSR** (*Server-Side Rendering*) | 서버가 완전한 HTML을 생성하여 전송 | 빠른 초기 로딩, SEO 유리 |
| **하이드레이션** (*Hydration*) | 서버에서 렌더링된 HTML에 자바스크립트를 연결하여 상호작용 가능하게 만드는 과정 | SSR 후 클라이언트에서 수행 |

> **Osmani의 조언**: CRA(Create React App)는 제한적인 개발 환경을 제공하여 최신 웹 애플리케이션 개발에 적합하지 않다. 대신 Next.js, Remix와 같은 실제 서비스에 적합한 리액트 기반 프레임워크를 사용하여 새로운 웹 애플리케이션을 구축할 것을 권장한다.

---

## 2. 고차 컴포넌트 (Higher-Order Components)

고차 컴포넌트(*Higher-Order Component, HOC*)는 **컴포넌트를 인자로 받아 새로운 컴포넌트를 반환하는 함수**다. 고차 컴포넌트는 특정 기능(스타일 적용, 인증, 전역 상태 추가 등)을 포함하고 있어 매개변수로 전달받은 컴포넌트에 해당 기능을 적용한 새로운 컴포넌트를 만들어 반환한다.

### 기본 예제: withStyles

```tsx
function withStyles<P extends object>(Component: React.ComponentType<P & { style: React.CSSProperties }>) {
  return (props: P) => {
    const style: React.CSSProperties = { padding: "0.2rem", margin: "1rem" };
    return <Component style={style} {...props} />;
  };
}

const Button = ({ style }: { style?: React.CSSProperties }) => (
  <button style={style}>Click me!</button>
);

const Text = ({ style }: { style?: React.CSSProperties }) => (
  <p style={style}>Hello World!</p>
);

const StyledButton = withStyles(Button);
const StyledText = withStyles(Text);
```

### 실전 예제: withLoader

API에서 데이터를 가져오는 동안 로딩 화면을 보여주는 HOC다. 컴포넌트와 URL을 인자로 받아 데이터 페칭 로직을 재사용할 수 있게 한다.

```tsx
import { useEffect, useState, ComponentType } from "react";

interface WithLoaderProps {
  data: unknown;
}

export default function withLoader<P extends WithLoaderProps>(
  Element: ComponentType<P>,
  url: string
) {
  return (props: Omit<P, "data">) => {
    const [data, setData] = useState<unknown>(null);

    useEffect(() => {
      async function getData() {
        const res = await fetch(url);
        const json = await res.json();
        setData(json);
      }
      getData();
    }, []);

    if (!data) {
      return <div>Loading...</div>;
    }

    return <Element {...(props as P)} data={data} />;
  };
}
```

```tsx
// 사용 측
import withLoader from "./withLoader";

interface DogImagesProps {
  data: { message: string[] };
}

function DogImages({ data }: DogImagesProps) {
  return data.message.map((dog, index) => (
    <img src={dog} alt="Dog" key={index} />
  ));
}

export default withLoader(
  DogImages,
  "https://dog.ceo/api/breed/labrador/images/random/6"
);
```

### 실전 예제: withAuth

인증 여부를 확인하여 접근을 제어하는 HOC다.

```tsx
import { ComponentType } from "react";
import { Navigate } from "react-router-dom";

interface WithAuthOptions {
  redirectTo?: string;
}

function withAuth<P extends object>(
  WrappedComponent: ComponentType<P>,
  options: WithAuthOptions = {}
) {
  const { redirectTo = "/login" } = options;

  return (props: P) => {
    const isAuthenticated = useAuth(); // 커스텀 Hook 가정

    if (!isAuthenticated) {
      return <Navigate to={redirectTo} replace />;
    }

    return <WrappedComponent {...props} />;
  };
}

// 사용
const ProtectedDashboard = withAuth(Dashboard);
const ProtectedAdmin = withAuth(AdminPanel, { redirectTo: "/unauthorized" });
```

### HOC 조합하기

여러 HOC를 중첩하여 사용할 수 있다.

```tsx
export default withHover(
  withLoader(DogImages, "https://dog.ceo/api/breed/labrador/images/random/6")
);
```

### 장점

- 재사용하고자 하는 로직을 **한 곳에 모아 관리**할 수 있다
- 코드를 DRY하게 유지하고 효과적으로 **관심사를 분리**할 수 있다
- 애플리케이션 전체에 걸쳐 여러 컴포넌트에 동일한 동작을 적용할 때 효과적이다

### 단점

| 문제 | 설명 |
|------|------|
| **이름 충돌** (*Naming Collision*) | HOC가 전달하는 prop 이름이 기존 prop과 충돌할 수 있다 |
| **디버깅 어려움** | 여러 HOC를 조합하면 어떤 HOC가 어떤 prop을 제공하는지 파악하기 어렵다 |
| **래퍼 헬** (*Wrapper Hell*) | 깊게 중첩된 컴포넌트 트리가 만들어지기 쉽다 |
| **refs 전달** | HOC가 ref를 자동으로 전달하지 않아 `React.forwardRef`를 사용해야 한다 |

```tsx
// 이름 충돌 문제 예시
function withStyles<P extends object>(Component: ComponentType<P>) {
  return (props: P) => {
    const style = { padding: "0.2rem", margin: "1rem" };
    // Button이 이미 style prop을 가지고 있으면 덮어씌워진다!
    return <Component style={style} {...props} />;
  };
}

// 해결: prop 병합
function withStyles<P extends { style?: React.CSSProperties }>(
  Component: ComponentType<P>
) {
  return (props: P) => {
    const style: React.CSSProperties = {
      padding: "0.2rem",
      margin: "1rem",
      ...props.style, // 기존 스타일 병합
    };
    return <Component {...props} style={style} />;
  };
}
```

### 현대적 관점

> **핵심 통찰**: HOC는 리액트 초기부터 사용된 강력한 패턴이지만, Hooks의 등장 이후 대부분의 HOC 사용 사례는 커스텀 Hook으로 대체할 수 있다. 그러나 **컴포넌트를 감싸서 렌더링 로직 자체를 변경**해야 하는 경우(인증 가드, 레이아웃 래퍼, 에러 바운더리 등)에는 여전히 HOC가 유효하다.

---

## 3. 렌더 프롭스 (Render Props)

렌더 프롭스(*Render Props*)는 **JSX 요소를 반환하는 함수를 prop으로 전달**하여 컴포넌트의 렌더링을 위임하는 패턴이다. 컴포넌트 자체는 렌더 prop 외에는 아무것도 렌더링하지 않으며, 자신의 렌더링 로직을 구현하는 대신 렌더 prop을 호출한다.

### 기본 개념

```tsx
// render prop을 활용한 Title 컴포넌트
interface TitleProps {
  render: () => React.ReactNode;
}

const Title = ({ render }: TitleProps) => render();

// 사용
<Title render={() => <h1>I am a render prop!</h1>} />
```

render라는 이름이 반드시 필요한 것은 아니다. JSX를 반환하는 모든 prop이 렌더 prop으로 간주된다.

```tsx
interface MultiRenderProps {
  renderFirst: () => React.ReactNode;
  renderSecond: () => React.ReactNode;
  renderThird: () => React.ReactNode;
}

const Title = ({ renderFirst, renderSecond, renderThird }: MultiRenderProps) => (
  <>
    {renderFirst()}
    {renderSecond()}
    {renderThird()}
  </>
);
```

### 데이터 전달과 상태 끌어올리기

렌더 prop을 받는 컴포넌트는 보통 내부 데이터를 렌더 prop 함수의 인자로 전달한다. 이를 통해 **상태 끌어올리기**(*Lifting State Up*)를 구현할 수 있다.

상태 끌어올리기란 형제 컴포넌트 간 상태를 공유해야 할 때, 상태를 가장 가까운 공통 조상 컴포넌트로 끌어올리는 것을 말한다.

```tsx
// 온도 변환기 예제 — 상태 끌어올리기
interface InputProps {
  render: (value: string) => React.ReactNode;
}

function Input({ render }: InputProps) {
  const [value, setValue] = useState("");

  return (
    <>
      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Temp in °C"
      />
      {render(value)}
    </>
  );
}

function Kelvin({ value }: { value: string }) {
  return <div className="temp">{parseFloat(value || "0") + 273.15}K</div>;
}

function Fahrenheit({ value }: { value: string }) {
  return <div className="temp">{(parseFloat(value || "0") * 9) / 5 + 32}°F</div>;
}

export default function App() {
  return (
    <div className="App">
      <h1>Temperature Converter</h1>
      <Input
        render={(value) => (
          <>
            <Kelvin value={value} />
            <Fahrenheit value={value} />
          </>
        )}
      />
    </div>
  );
}
```

### children을 통한 함수 전달

렌더 prop의 변형으로, 컴포넌트의 자식으로 함수를 전달할 수 있다. 이 함수는 `children` prop을 통해 접근하며, 엄밀히 말하면 이것도 렌더 프롭스 패턴이다.

```tsx
interface InputWithChildrenProps {
  children: (value: string) => React.ReactNode;
}

function Input({ children }: InputWithChildrenProps) {
  const [value, setValue] = useState("");

  return (
    <>
      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Temp in °C"
      />
      {children(value)}
    </>
  );
}

// 사용: render prop 이름에 구애받지 않음
<Input>
  {(value) => (
    <>
      <Kelvin value={value} />
      <Fahrenheit value={value} />
    </>
  )}
</Input>
```

### 장점

- **이름 충돌 해결**: props를 자동으로 병합하지 않고 명시적으로 전달하므로 HOC의 이름 충돌 문제가 없다
- **props 출처 명확**: 어떤 props가 어디에서 오는지 렌더 prop 인자 목록에서 정확하게 파악할 수 있다
- **관심사 분리**: 상태를 가진 컴포넌트와 렌더링 컴포넌트를 분리할 수 있다

### 단점

- Hooks가 렌더 프롭스로 해결할 수 있는 문제 대부분을 이미 해결했다
- 라이프사이클 관련 메서드를 추가할 수 없으므로, 받은 데이터를 변경할 필요가 없는 렌더링 전용 컴포넌트에만 사용할 수 있다
- 중첩이 깊어지면 **콜백 헬**(*Callback Hell*)과 유사한 구조가 만들어진다

### 현대적 관점

렌더 프롭스 패턴은 Hooks로 대부분 대체할 수 있다. 다만, **Headless UI 컴포넌트**(*렌더링은 소비자에게 위임하고 로직만 제공하는 컴포넌트*)에서는 여전히 렌더 프롭스 또는 children as function 패턴이 유용하다. Radix UI, Downshift 등의 라이브러리가 이 패턴을 활용한다.

---

## 4. Hooks 패턴

리액트 16.8부터 도입된 Hooks(*훅*)는 클래스 컴포넌트 없이도 **상태와 라이프사이클 메서드를 함수형 컴포넌트에서 사용**할 수 있게 해주는 기능이다. Hooks 자체는 디자인 패턴이라고 할 수 없지만, 많은 전통적인 디자인 패턴(HOC, 렌더 프롭스)을 대체할 수 있어 애플리케이션 설계에서 핵심적인 역할을 한다.

### 4.1 기본 Hooks

#### useState

함수형 컴포넌트 내에서 상태를 관리한다. 현재 상태 값과 상태를 업데이트하는 함수를 반환한다.

```tsx
function Input() {
  const [input, setInput] = useState("");

  return (
    <input
      onChange={(e) => setInput(e.target.value)}
      value={input}
      placeholder="Type something..."
    />
  );
}
```

#### useEffect

컴포넌트의 라이프사이클에 접근하여 부수 효과(*Side Effect — 데이터 페칭, 구독, 타이머, DOM 조작 등 렌더링 외의 작업*)를 처리한다. `componentDidMount`, `componentDidUpdate`, `componentWillUnmount`를 하나로 합쳐 사용할 수 있다.

```tsx
// componentDidMount — 마운트 시 한 번 실행
useEffect(() => { /* ... */ }, []);

// componentWillUnmount — 클린업 함수
useEffect(() => {
  return () => { /* 정리 로직 */ };
}, []);

// componentDidUpdate — 의존성 변경 시 실행
useEffect(() => { /* ... */ }, [dependency]);
```

```tsx
function Input() {
  const [input, setInput] = useState("");

  useEffect(() => {
    console.log(`The user typed ${input}`);
  }, [input]);

  return (
    <input
      onChange={(e) => setInput(e.target.value)}
      value={input}
      placeholder="Type something..."
    />
  );
}
```

#### useContext

`React.createContext`로 만든 Context 객체를 인자로 받아 해당 Context의 현재 값에 접근할 수 있게 한다. Context API와 연동하여 props를 여러 단계에 걸쳐 전달하지 않고도 애플리케이션 전역에서 상태를 공유할 수 있다.

```tsx
const ThemeContext = createContext<"light" | "dark">("light");

function ThemedButton() {
  const theme = useContext(ThemeContext);
  return <button className={`btn-${theme}`}>Themed Button</button>;
}
```

#### useRef

DOM 요소에 대한 참조를 유지하거나, 렌더링 사이에 값을 유지하되 변경 시 리렌더링을 트리거하지 않아야 할 때 사용한다.

```tsx
function TextInputWithFocusButton() {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleClick = () => {
    inputRef.current?.focus();
  };

  return (
    <>
      <input ref={inputRef} type="text" />
      <button onClick={handleClick}>Focus the input</button>
    </>
  );
}
```

#### useMemo와 useCallback

**useMemo**는 계산 비용이 큰 값을 메모이제이션하여 의존성이 변경되지 않는 한 이전 결과를 재사용한다. **useCallback**은 함수를 메모이제이션하여 불필요한 리렌더링을 방지한다.

```tsx
function ExpensiveList({ items, filter }: { items: Item[]; filter: string }) {
  // 값 메모이제이션
  const filteredItems = useMemo(
    () => items.filter((item) => item.name.includes(filter)),
    [items, filter]
  );

  // 함수 메모이제이션
  const handleClick = useCallback(
    (id: string) => {
      console.log(`Clicked item ${id}`);
    },
    [] // 의존성 없음
  );

  return (
    <ul>
      {filteredItems.map((item) => (
        <ListItem key={item.id} item={item} onClick={handleClick} />
      ))}
    </ul>
  );
}
```

#### useReducer

`useState`의 대안으로, 여러 하위 값을 포함하는 복잡한 상태 로직이나 이전 상태에 의존하는 상태 변경에 특히 유용하다.

```tsx
interface State {
  count: number;
  step: number;
}

type Action =
  | { type: "increment" }
  | { type: "decrement" }
  | { type: "setStep"; payload: number };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "increment":
      return { ...state, count: state.count + state.step };
    case "decrement":
      return { ...state, count: state.count - state.step };
    case "setStep":
      return { ...state, step: action.payload };
  }
}

function Counter() {
  const [state, dispatch] = useReducer(reducer, { count: 0, step: 1 });

  return (
    <div>
      <p>Count: {state.count}</p>
      <button onClick={() => dispatch({ type: "increment" })}>+</button>
      <button onClick={() => dispatch({ type: "decrement" })}>-</button>
    </div>
  );
}
```

### 4.2 커스텀 Hooks

리액트에서 기본 제공하는 Hooks 외에도 직접 커스텀 Hook을 만들어 사용할 수 있다. 모든 Hook은 `use`로 시작해야 하며, 이를 통해 리액트가 내부적으로 Hook 규칙 준수 여부를 판단한다.

#### useKeyPress — 키 입력 감지

```tsx
function useKeyPress(targetKey: string): boolean {
  const [keyPressed, setKeyPressed] = useState(false);

  useEffect(() => {
    const handleDown = ({ key }: KeyboardEvent) => {
      if (key === targetKey) setKeyPressed(true);
    };

    const handleUp = ({ key }: KeyboardEvent) => {
      if (key === targetKey) setKeyPressed(false);
    };

    window.addEventListener("keydown", handleDown);
    window.addEventListener("keyup", handleUp);

    return () => {
      window.removeEventListener("keydown", handleDown);
      window.removeEventListener("keyup", handleUp);
    };
  }, [targetKey]);

  return keyPressed;
}
```

#### useToggle — 불리언 토글

```tsx
function useToggle(initialValue = false): [boolean, () => void] {
  const [value, setValue] = useState(initialValue);
  const toggle = useCallback(() => setValue((v) => !v), []);
  return [value, toggle];
}

// 사용
function Modal() {
  const [isOpen, toggleOpen] = useToggle();
  return (
    <>
      <button onClick={toggleOpen}>{isOpen ? "Close" : "Open"}</button>
      {isOpen && <div className="modal">Modal Content</div>}
    </>
  );
}
```

#### useLocalStorage — 로컬 스토리지 동기화

```tsx
function useLocalStorage<T>(key: string, initialValue: T): [T, (value: T | ((val: T) => T)) => void] {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? (JSON.parse(item) as T) : initialValue;
    } catch {
      return initialValue;
    }
  });

  const setValue = (value: T | ((val: T) => T)) => {
    const valueToStore = value instanceof Function ? value(storedValue) : value;
    setStoredValue(valueToStore);
    window.localStorage.setItem(key, JSON.stringify(valueToStore));
  };

  return [storedValue, setValue];
}

// 사용
function Settings() {
  const [theme, setTheme] = useLocalStorage<"light" | "dark">("theme", "light");
  return <button onClick={() => setTheme(theme === "light" ? "dark" : "light")}>{theme}</button>;
}
```

#### useDebounce — 디바운스된 값

```tsx
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(handler);
  }, [value, delay]);

  return debouncedValue;
}

// 사용: 검색 입력 최적화
function SearchInput() {
  const [query, setQuery] = useState("");
  const debouncedQuery = useDebounce(query, 300);

  useEffect(() => {
    if (debouncedQuery) {
      fetchSearchResults(debouncedQuery);
    }
  }, [debouncedQuery]);

  return <input value={query} onChange={(e) => setQuery(e.target.value)} />;
}
```

#### useFetch — 데이터 페칭

```tsx
interface UseFetchResult<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
}

function useFetch<T>(url: string): UseFetchResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    async function fetchData() {
      try {
        setLoading(true);
        const res = await fetch(url, { signal: controller.signal });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json = (await res.json()) as T;
        setData(json);
      } catch (err) {
        if (err instanceof Error && err.name !== "AbortError") {
          setError(err);
        }
      } finally {
        setLoading(false);
      }
    }

    fetchData();
    return () => controller.abort();
  }, [url]);

  return { data, loading, error };
}
```

### 커스텀 Hook 작성 원칙

1. **단일 책임**: 하나의 Hook은 하나의 관심사만 다룬다
2. **`use` 접두사**: 리액트가 Hook 규칙 준수를 확인하려면 반드시 `use`로 시작해야 한다
3. **순수 함수**: Hook 내부에서 다른 Hook을 호출할 수 있지만, 조건문이나 반복문 안에서 Hook을 호출해서는 안 된다
4. **반환값 설계**: 단일 값은 그대로, 두 값은 튜플 `[value, setter]`, 여러 값은 객체 `{ data, loading, error }`로 반환한다

### 4.3 Hooks의 규칙 (Rules of Hooks)

| 규칙 | 설명 |
|------|------|
| **최상위에서만 호출** | 반복문, 조건문, 중첩 함수 내부에서 Hook을 호출하면 안 된다 |
| **리액트 함수에서만 호출** | 함수형 컴포넌트 또는 커스텀 Hook 안에서만 호출할 수 있다 |
| **`use` 접두사** | 커스텀 Hook의 이름은 반드시 `use`로 시작해야 한다 |

```tsx
// 잘못된 사용
function Component({ shouldFetch }: { shouldFetch: boolean }) {
  if (shouldFetch) {
    const data = useFetch("/api/data"); // 조건문 안에서 Hook 호출 — 규칙 위반!
  }
}

// 올바른 사용
function Component({ shouldFetch }: { shouldFetch: boolean }) {
  const data = useFetch(shouldFetch ? "/api/data" : ""); // Hook은 항상 호출되되, 인자로 제어
}
```

### 4.4 Hooks의 장단점

**장점**:
- **더 적은 코드**: 클래스 문법, 생성자, bind 등이 불필요하여 코드가 간결해진다
- **복잡한 컴포넌트 단순화**: 관심사별로 로직을 그룹화할 수 있다
- **상태 관련 로직 재사용**: 커스텀 Hook으로 UI와 무관한 로직을 추출하고 공유할 수 있다
- **일관성**: 함수 바인딩과 호출 컨텍스트에 대한 혼란이 없다

**단점**:
- Hook 사용 규칙을 준수해야 한다 (Linter 플러그인 권장)
- `useEffect`를 올바르게 사용하려면 상당한 연습이 필요하다
- `useCallback`, `useMemo`의 잘못된 사용(불필요한 곳에 과도하게 적용)에 주의해야 한다

### 4.5 Hooks vs HOC vs Render Props 비교

| 기준 | HOC | Render Props | Hooks |
|------|-----|-------------|-------|
| **코드 위치** | 컴포넌트 외부에서 감싼다 | JSX 내부에 인라인 | 컴포넌트 함수 내부 |
| **이름 충돌** | prop 이름 충돌 위험 | 없음 (명시적 전달) | 없음 (로컬 변수) |
| **중첩 문제** | 래퍼 헬 | 콜백 헬 | 없음 (평탄한 구조) |
| **타입 추론** | 어려움 | 보통 | 우수 |
| **재사용성** | 컴포넌트 단위 | 컴포넌트 단위 | **로직 단위** |
| **디버깅** | DevTools에서 래퍼 추적 어려움 | 보통 | DevTools 지원 우수 |
| **권장 시기** | 렌더링 로직 변경 (가드, 레이아웃) | Headless UI 패턴 | **대부분의 경우** |

> **핵심 통찰**: Hooks는 HOC와 렌더 프롭스 패턴이 해결하려 했던 "로직 재사용" 문제를 근본적으로 해결했다. 컴포넌트 트리 구조를 변경하지 않고도 상태 관련 로직을 추출하고 공유할 수 있기 때문이다. 새 코드에서는 Hooks를 기본으로 사용하되, HOC는 인증 가드나 레이아웃 래퍼처럼 "컴포넌트 자체를 감싸야 하는" 경우에만 사용하는 것이 좋다.

---

## 5. 컴포넌트 합성 패턴 (Composition Patterns)

### 5.1 Container/Presentational 패턴

**Container 컴포넌트**(*컨테이너 컴포넌트*)는 데이터를 가져오고 상태를 관리하는 로직을 담당하며, **Presentational 컴포넌트**(*프레젠테이셔널 컴포넌트*)는 받은 데이터를 순수하게 렌더링하는 역할만 한다.

```tsx
// Container: 로직 담당
function UserListContainer() {
  const { data: users, loading, error } = useFetch<User[]>("/api/users");

  if (loading) return <Spinner />;
  if (error) return <ErrorMessage error={error} />;

  return <UserList users={users ?? []} />;
}

// Presentational: 렌더링만 담당
interface UserListProps {
  users: User[];
}

function UserList({ users }: UserListProps) {
  return (
    <ul>
      {users.map((user) => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```

Hooks의 등장으로 이 패턴의 필요성이 줄었지만, **데이터 로직과 UI를 분리**하는 원칙 자체는 여전히 유효하다. 커스텀 Hook이 Container의 역할을 대신하고, 컴포넌트는 Presentational에만 집중하는 형태가 현대적인 접근 방식이다.

### 5.2 Compound Components 패턴

합성 컴포넌트(*Compound Components*)는 여러 컴포넌트가 함께 동작하여 하나의 완전한 UI를 구성하는 패턴이다. HTML의 `<select>`와 `<option>`처럼, 부모 컴포넌트가 내부 상태를 관리하고 자식 컴포넌트들이 이를 암시적으로 공유한다.

```tsx
// Tabs 합성 컴포넌트
interface TabsContextType {
  activeTab: string;
  setActiveTab: (id: string) => void;
}

const TabsContext = createContext<TabsContextType | null>(null);

function useTabs() {
  const context = useContext(TabsContext);
  if (!context) throw new Error("Tabs 컴포넌트 내부에서만 사용할 수 있습니다");
  return context;
}

function Tabs({ defaultTab, children }: { defaultTab: string; children: React.ReactNode }) {
  const [activeTab, setActiveTab] = useState(defaultTab);

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div className="tabs">{children}</div>
    </TabsContext.Provider>
  );
}

function TabList({ children }: { children: React.ReactNode }) {
  return <div className="tab-list" role="tablist">{children}</div>;
}

function Tab({ id, children }: { id: string; children: React.ReactNode }) {
  const { activeTab, setActiveTab } = useTabs();

  return (
    <button
      role="tab"
      aria-selected={activeTab === id}
      className={activeTab === id ? "tab active" : "tab"}
      onClick={() => setActiveTab(id)}
    >
      {children}
    </button>
  );
}

function TabPanel({ id, children }: { id: string; children: React.ReactNode }) {
  const { activeTab } = useTabs();
  if (activeTab !== id) return null;

  return <div role="tabpanel">{children}</div>;
}

// Tabs에 하위 컴포넌트를 정적 속성으로 연결
Tabs.List = TabList;
Tabs.Tab = Tab;
Tabs.Panel = TabPanel;

// 사용
function App() {
  return (
    <Tabs defaultTab="overview">
      <Tabs.List>
        <Tabs.Tab id="overview">Overview</Tabs.Tab>
        <Tabs.Tab id="settings">Settings</Tabs.Tab>
        <Tabs.Tab id="billing">Billing</Tabs.Tab>
      </Tabs.List>
      <Tabs.Panel id="overview">Overview content</Tabs.Panel>
      <Tabs.Panel id="settings">Settings content</Tabs.Panel>
      <Tabs.Panel id="billing">Billing content</Tabs.Panel>
    </Tabs>
  );
}
```

합성 컴포넌트 패턴의 장점은 사용자가 **내부 구현을 알 필요 없이 선언적으로** 컴포넌트를 조합할 수 있다는 것이다.

### 5.3 Slot 패턴

Slot 패턴은 `children`이나 이름 있는 props를 통해 컴포넌트의 특정 영역에 콘텐츠를 삽입하는 패턴이다.

```tsx
interface CardProps {
  header?: React.ReactNode;
  footer?: React.ReactNode;
  children: React.ReactNode;
}

function Card({ header, footer, children }: CardProps) {
  return (
    <div className="card">
      {header && <div className="card-header">{header}</div>}
      <div className="card-body">{children}</div>
      {footer && <div className="card-footer">{footer}</div>}
    </div>
  );
}

// 사용
<Card
  header={<h2>Title</h2>}
  footer={<button>Submit</button>}
>
  <p>Card content goes here</p>
</Card>
```

### 5.4 Controlled vs Uncontrolled Components

| 특성 | Controlled | Uncontrolled |
|------|-----------|-------------|
| **데이터 소유** | 부모 컴포넌트가 상태를 소유하고 prop으로 전달 | 컴포넌트 자체가 내부 상태를 관리 |
| **값 접근** | 항상 최신 값에 접근 가능 | `ref`를 통해 필요할 때만 접근 |
| **사용 시기** | 실시간 검증, 조건부 UI, 다른 컴포넌트와 상태 공유 | 단순 폼, 성능 최적화 |

```tsx
// Controlled
function ControlledInput() {
  const [value, setValue] = useState("");
  return <input value={value} onChange={(e) => setValue(e.target.value)} />;
}

// Uncontrolled
function UncontrolledInput() {
  const inputRef = useRef<HTMLInputElement>(null);
  const handleSubmit = () => console.log(inputRef.current?.value);
  return <input ref={inputRef} defaultValue="" />;
}
```

---

## 6. 상태 관리 패턴

### 6.1 로컬 상태 (useState)

컴포넌트 내부에서만 사용되는 상태는 `useState`로 충분하다. 상태가 하나의 컴포넌트에만 관련된다면 전역 상태로 끌어올릴 필요가 없다.

### 6.2 공급자 패턴 (Context API + Provider)

프롭 드릴링(*Prop Drilling — 부모 컴포넌트로부터 자식 컴포넌트에 이르기까지 여러 계층을 통해 prop을 전달하는 과정*)을 해결하기 위해 Context API를 사용한다.

```tsx
interface AuthContextType {
  user: User | null;
  login: (credentials: Credentials) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) throw new Error("AuthProvider 내부에서만 사용할 수 있습니다");
  return context;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  const login = async (credentials: Credentials) => {
    const user = await authApi.login(credentials);
    setUser(user);
  };

  const logout = () => {
    authApi.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// 사용
function App() {
  return (
    <AuthProvider>
      <Dashboard />
    </AuthProvider>
  );
}

function Profile() {
  const { user, logout } = useAuth();
  return (
    <div>
      <span>{user?.name}</span>
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

> **Osmani의 조언**: Context API는 "자주 변경되지 않는" 전역 데이터(테마, 인증, 언어 설정)에 적합하다. 자주 변경되는 상태를 Context에 넣으면 해당 Context를 구독하는 모든 컴포넌트가 리렌더링되므로 성능 문제가 발생할 수 있다.

### 6.3 외부 상태 관리 라이브러리

| 라이브러리 | 특징 | 적합한 상황 |
|-----------|------|-----------|
| **Zustand** | 최소한의 API, 보일러플레이트 거의 없음, 선택적 구독 | 중소규모 앱, 빠른 프로토타이핑 |
| **Jotai** | 원자(*atom*) 기반, 세밀한 리렌더링 제어, Bottom-up 접근 | 독립적인 상태 조각이 많은 앱 |
| **Redux Toolkit** | 예측 가능한 상태 변화, DevTools, 미들웨어 생태계 | 대규모 팀, 복잡한 비즈니스 로직 |

```tsx
// Zustand 예시
import { create } from "zustand";

interface CounterStore {
  count: number;
  increment: () => void;
  decrement: () => void;
}

const useCounterStore = create<CounterStore>((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
  decrement: () => set((state) => ({ count: state.count - 1 })),
}));

function Counter() {
  const { count, increment, decrement } = useCounterStore();
  return (
    <div>
      <span>{count}</span>
      <button onClick={increment}>+</button>
      <button onClick={decrement}>-</button>
    </div>
  );
}
```

### 6.4 상태 위치 결정 전략

상태를 어디에 둘지 결정하는 것은 리액트 애플리케이션 설계에서 가장 중요한 판단 중 하나다.

```
이 상태가 하나의 컴포넌트에서만 사용되는가?
  └─ Yes → useState (로컬 상태)
  └─ No → 부모-자식 간 2~3단계 이내인가?
      └─ Yes → 상태 끌어올리기 (Lifting State Up)
      └─ No → 자주 변경되는 상태인가?
          └─ No → Context API
          └─ Yes → 외부 상태 관리 라이브러리 (Zustand, Jotai 등)
```

---

## 7. 코드 분할과 지연 로딩

### 7.1 정적 가져오기 vs 동적 가져오기

**정적 가져오기**(*Static Import*)는 `import` 키워드를 사용하여 모듈을 가져오며, 모든 정적 모듈은 초기 번들에 포함된다. 애플리케이션의 모든 모듈이 한 번에 로드되므로 번들 크기가 커질 수 있다.

**동적 가져오기**(*Dynamic Import*)는 실제로 필요한 시점에 모듈을 로드한다. 초기 번들에 포함되지 않으므로 초기 로딩 속도를 개선할 수 있다.

### 7.2 React.lazy + Suspense

리액트의 `React.lazy`와 `Suspense`를 사용하면 컴포넌트를 동적으로 가져올 수 있다.

```tsx
import { lazy, Suspense } from "react";

// 동적 가져오기: EmojiPicker는 초기 번들에 포함되지 않음
const EmojiPicker = lazy(() => import("./EmojiPicker"));

function ChatInput() {
  const [pickerOpen, togglePicker] = useReducer((state: boolean) => !state, false);

  return (
    <Suspense fallback={<p>Loading...</p>}>
      <div className="chat-input-container">
        <input type="text" placeholder="Type a message..." />
        <button onClick={togglePicker}>Emoji</button>
        {pickerOpen && <EmojiPicker />}
      </div>
    </Suspense>
  );
}
```

동적 가져오기의 종류:

| 유형 | 설명 | 예시 |
|------|------|------|
| **상호작용 시 가져오기** (*Import on Interaction*) | 사용자 상호작용(클릭, 호버 등)에 의해 모듈 로드 | 이모지 선택 창 클릭 시 로드 |
| **화면에 보이는 순간 가져오기** (*Import on Visibility*) | 뷰포트에 진입할 때 모듈 로드 | 스크롤하면 나타나는 컴포넌트 |

### 7.3 경로 기반 분할 (Route-based Splitting)

특정 페이지에서만 필요한 리소스를 해당 경로 진입 시에만 로드한다.

```tsx
import { lazy, Suspense } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";

const Home = lazy(() => import("./pages/Home"));
const Overview = lazy(() => import("./pages/Overview"));
const Settings = lazy(() => import("./pages/Settings"));

function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<div>Loading...</div>}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/overview" element={<Overview />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
```

페이지 이동 시 로딩 시간이 다소 걸릴 수 있다는 점은 이미 많은 사용자에게 익숙하기 때문에, 경로 기반 분할은 자연스럽고 효과적인 최적화 전략이다.

### 7.4 PRPL 패턴

PRPL(*Push, Render, Pre-cache, Lazy-load*)은 어려운 네트워크 환경에서도 애플리케이션이 최대한 효율적으로 로드될 수 있도록 하는 패턴이다.

| 단계 | 설명 |
|------|------|
| **Push** (푸시) | 중요한 리소스를 효율적으로 푸시하여 서버 왕복 횟수를 최소화하고 로딩 시간을 단축 |
| **Render** (렌더링) | 초기 경로를 최대한 빠르게 렌더링하여 사용자 경험 개선 |
| **Pre-cache** (사전 캐싱) | 서비스 워커를 사용하여 자주 방문하는 경로의 에셋을 백그라운드에서 미리 캐싱 |
| **Lazy-load** (지연 로딩) | 자주 요청되지 않는 경로나 에셋은 나중에 로드 |

PRPL 패턴은 주로 **애플리케이션 셸**(*App Shell — 애플리케이션 로직의 대부분을 포함하며 여러 경로에서 공유되는 최소한의 파일*)을 주요 진입점으로 사용한다. 초기 접근 경로의 화면이 완전히 렌더링되기 전에 다른 리소스가 요청되지 않도록 보장하며, 초기 경로 로드 후 서비스 워커가 설치되어 다른 경로의 리소스를 백그라운드에서 가져온다.

### 7.5 번들 분할과 성능 지표

번들 크기를 결정할 때 고려해야 할 핵심 지표:

| 지표 | 설명 |
|------|------|
| **FCP** (*First Contentful Paint*) | 첫 번째 콘텐츠가 사용자 화면에 표시되는 시간 |
| **LCP** (*Largest Contentful Paint*) | 가장 큰 콘텐츠가 화면에 렌더링되는 시간 |
| **TTI** (*Time to Interactive*) | 모든 콘텐츠가 화면에 표시되고 상호작용 가능해지는 시간 |

번들 분할을 통해 초기 번들 크기를 줄이면 FCP와 LCP를 단축할 수 있고, 필요한 코드만 로드하면 TTI도 개선된다. 특히 저사양 기기나 느린 네트워크 환경에서는 그 차이가 더욱 크게 나타난다.

### 7.6 로딩 우선순위

`preload`는 브라우저가 늦게 요청할 수도 있는 중요한 리소스를 더 일찍 요청하게 하는 최적화 기능이다. `prefetch`는 곧 필요할 가능성이 있는 리소스를 미리 캐시하는 방법이다.

```html
<!-- preload: 현재 페이지에서 즉시 필요한 리소스 -->
<link rel="preload" href="critical-font.woff2" as="font" crossorigin />

<!-- prefetch: 다음 페이지에서 필요할 수 있는 리소스 -->
<link rel="prefetch" href="next-page-bundle.js" as="script" />
```

| 기법 | 시점 | 우선순위 | 용도 |
|------|------|---------|------|
| **preload** | 즉시 | 높음 | 현재 경로에 필수적인 리소스 (폰트, 히어로 이미지) |
| **prefetch** | 유휴 시간 | 낮음 | 다음 경로에서 필요할 리소스 |
| **preload + async** | 즉시 다운로드, 비동기 실행 | 높음 (다운로드) | 파싱 차단 없이 높은 우선순위 다운로드 |

> **핵심 통찰**: 코드 분할과 지연 로딩의 핵심은 "사용자가 필요로 하는 코드만, 필요한 시점에 제공한다"는 원칙이다. 모든 것을 지연 로딩하는 것이 아니라, 초기 렌더링에 필수적인 코드와 나중에 로드해도 되는 코드를 **전략적으로 구분**하는 것이 중요하다.

---

## 8. React 19의 새로운 패턴

React 19는 기존 패턴을 대체하거나 보완하는 새로운 API를 도입했다. 이러한 변화는 서버 중심 아키텍처와 더 나은 사용자 경험을 향한 리액트의 방향성을 반영한다.

### 8.1 `use()` Hook — Promise/Context 소비

`use()`는 Promise나 Context를 컴포넌트 내부에서 직접 소비할 수 있게 해주는 새로운 Hook이다. 기존 Hook과 달리 **조건문 안에서도 호출**할 수 있다는 특별한 규칙을 가진다.

```tsx
import { use, Suspense } from "react";

// Promise 소비
async function fetchUser(id: string): Promise<User> {
  const res = await fetch(`/api/users/${id}`);
  return res.json();
}

function UserProfile({ userPromise }: { userPromise: Promise<User> }) {
  const user = use(userPromise); // Suspense와 함께 동작

  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.email}</p>
    </div>
  );
}

function App() {
  const userPromise = fetchUser("1"); // 렌더링 외부에서 Promise 생성

  return (
    <Suspense fallback={<div>Loading user...</div>}>
      <UserProfile userPromise={userPromise} />
    </Suspense>
  );
}
```

```tsx
// Context 소비 — 조건부 사용 가능
function StatusDisplay({ showTheme }: { showTheme: boolean }) {
  if (showTheme) {
    const theme = use(ThemeContext); // 조건문 안에서 호출 가능!
    return <div className={theme}>Themed content</div>;
  }
  return <div>Default content</div>;
}
```

### 8.2 Server Actions — 폼 처리

Server Actions는 클라이언트에서 서버 함수를 직접 호출할 수 있게 하는 기능이다. `"use server"` 지시어로 표시하며, `<form>`의 `action` prop에 직접 전달할 수 있다.

```tsx
// actions.ts — 서버에서 실행
"use server";

export async function createTodo(formData: FormData) {
  const title = formData.get("title") as string;
  await db.todos.create({ title });
  revalidatePath("/todos");
}
```

```tsx
// TodoForm.tsx — 클라이언트 컴포넌트
import { createTodo } from "./actions";

function TodoForm() {
  return (
    <form action={createTodo}>
      <input name="title" placeholder="New todo..." required />
      <button type="submit">Add</button>
    </form>
  );
}
```

Server Actions는 기존의 API 라우트 + `fetch` + 로딩 상태 관리 패턴을 크게 단순화한다.

### 8.3 `useOptimistic` — 낙관적 업데이트

`useOptimistic`은 서버 응답을 기다리지 않고 UI를 즉시 업데이트하는 낙관적 업데이트(*Optimistic Update*)를 간편하게 구현할 수 있게 한다.

```tsx
import { useOptimistic } from "react";

interface Todo {
  id: string;
  title: string;
  completed: boolean;
}

function TodoList({ todos }: { todos: Todo[] }) {
  const [optimisticTodos, addOptimisticTodo] = useOptimistic(
    todos,
    (currentTodos: Todo[], newTodo: Todo) => [...currentTodos, newTodo]
  );

  async function handleAdd(formData: FormData) {
    const title = formData.get("title") as string;
    const tempTodo: Todo = { id: `temp-${Date.now()}`, title, completed: false };

    addOptimisticTodo(tempTodo); // 즉시 UI 반영
    await createTodoAction(formData); // 서버에 요청 (실패 시 자동 롤백)
  }

  return (
    <div>
      <form action={handleAdd}>
        <input name="title" />
        <button type="submit">Add</button>
      </form>
      <ul>
        {optimisticTodos.map((todo) => (
          <li key={todo.id} style={{ opacity: todo.id.startsWith("temp") ? 0.5 : 1 }}>
            {todo.title}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

### 8.4 `useFormStatus` — 폼 상태

`useFormStatus`는 부모 `<form>`의 제출 상태에 접근할 수 있게 하는 Hook이다. 폼 내부의 자식 컴포넌트에서 사용한다.

```tsx
import { useFormStatus } from "react-dom";

function SubmitButton() {
  const { pending, data, method } = useFormStatus();

  return (
    <button type="submit" disabled={pending}>
      {pending ? "Submitting..." : "Submit"}
    </button>
  );
}

function ContactForm() {
  return (
    <form action={submitContactForm}>
      <input name="email" type="email" required />
      <textarea name="message" required />
      <SubmitButton /> {/* 폼 상태를 자동으로 인지 */}
    </form>
  );
}
```

### 8.5 `useActionState` — 액션 상태 관리

`useActionState`는 Server Action의 결과를 상태로 관리하는 Hook이다. 폼 제출 후 성공/오류 메시지 표시 등에 활용한다.

```tsx
import { useActionState } from "react";

interface FormState {
  message: string;
  errors?: Record<string, string>;
}

async function loginAction(prevState: FormState, formData: FormData): Promise<FormState> {
  const email = formData.get("email") as string;
  const password = formData.get("password") as string;

  try {
    await authenticate(email, password);
    return { message: "Login successful!" };
  } catch {
    return { message: "", errors: { form: "Invalid credentials" } };
  }
}

function LoginForm() {
  const [state, formAction, isPending] = useActionState(loginAction, { message: "" });

  return (
    <form action={formAction}>
      <input name="email" type="email" />
      <input name="password" type="password" />
      <button disabled={isPending}>{isPending ? "Logging in..." : "Login"}</button>
      {state.errors?.form && <p className="error">{state.errors.form}</p>}
      {state.message && <p className="success">{state.message}</p>}
    </form>
  );
}
```

### 8.6 React Compiler — 자동 메모이제이션

React Compiler(*이전 이름: React Forget*)는 빌드 타임에 코드를 분석하여 **자동으로 메모이제이션을 적용**하는 컴파일러다. `useMemo`, `useCallback`, `React.memo`를 수동으로 작성하지 않아도 컴파일러가 최적의 메모이제이션을 삽입한다.

```tsx
// React Compiler 이전: 수동 메모이제이션
function TodoList({ todos, filter }: Props) {
  const filteredTodos = useMemo(
    () => todos.filter((t) => t.status === filter),
    [todos, filter]
  );

  const handleClick = useCallback((id: string) => {
    markAsComplete(id);
  }, []);

  return filteredTodos.map((todo) => (
    <TodoItem key={todo.id} todo={todo} onClick={handleClick} />
  ));
}

// React Compiler 이후: 수동 메모이제이션 불필요
function TodoList({ todos, filter }: Props) {
  const filteredTodos = todos.filter((t) => t.status === filter);

  const handleClick = (id: string) => {
    markAsComplete(id);
  };

  return filteredTodos.map((todo) => (
    <TodoItem key={todo.id} todo={todo} onClick={handleClick} />
  ));
}
// 컴파일러가 자동으로 필요한 메모이제이션을 적용
```

React Compiler가 올바르게 작동하려면 컴포넌트가 **리액트의 규칙**(순수 렌더링, 불변 props/state)을 따라야 한다. 규칙을 위반하는 컴포넌트는 컴파일러가 자동으로 건너뛴다.

---

## 최신 업데이트 (2026)

| 영역 | 변화 | 영향 |
|------|------|------|
| **React 19 정식 출시** | `use()`, Server Actions, `useOptimistic`, `useFormStatus`, `useActionState` | 서버-클라이언트 통합 패턴의 주류화 |
| **React Compiler** | 자동 메모이제이션, `useMemo`/`useCallback` 수동 사용 불필요 | 성능 최적화의 자동화 |
| **Server Components** | 서버에서만 실행되는 컴포넌트가 기본값 (Next.js App Router) | 번들 크기 자연 감소, 데이터 페칭 패턴 변화 |
| **Next.js 15** | Partial Prerendering, Turbopack 안정화 | SSR + CSR 하이브리드의 새로운 기준 |
| **상태 관리** | Zustand, Jotai 등 경량 라이브러리가 Redux를 대체하는 추세 가속 | 보일러플레이트 감소, 학습 곡선 완화 |
| **리스트 가상화** | `react-window`, `@tanstack/react-virtual` 등 가상화 라이브러리가 보편화 | 대규모 리스트 렌더링 성능 표준화 |

> **핵심 통찰**: React 19의 가장 큰 변화는 **서버와 클라이언트의 경계가 흐려진 것**이다. Server Actions를 통해 별도의 API 엔드포인트 없이 서버 함수를 호출하고, Server Components를 통해 서버에서만 실행되는 로직을 자연스럽게 분리할 수 있다. 이러한 변화는 "어디서 실행되는가"를 기준으로 한 새로운 아키텍처 패턴을 요구한다.

---

## 실무 적용 가이드

### 패턴 선택 체크리스트

| 상황 | 권장 패턴 |
|------|----------|
| 여러 컴포넌트에서 상태 로직 공유 | **커스텀 Hook** |
| 컴포넌트를 감싸서 렌더링 조건을 변경 (인증, 레이아웃) | **HOC** |
| UI 없이 로직만 제공하는 라이브러리 컴포넌트 | **Render Props / Headless UI** |
| Select, Tabs 같은 복합 UI 구성 | **Compound Components** |
| 전역 테마/인증/언어 설정 공유 | **Context API (Provider)** |
| 자주 변경되는 전역 상태 | **외부 상태 관리 (Zustand, Jotai)** |
| 초기 로딩 성능 최적화 | **코드 분할 + React.lazy + Suspense** |
| 폼 처리와 서버 연동 | **Server Actions + useActionState** |
| 즉각적인 사용자 피드백 | **useOptimistic** |
| 성능 최적화 (메모이제이션) | **React Compiler** (수동 최적화 최소화) |

### 리액트 디자인 패턴의 진화

```
클래스 컴포넌트 시대 (2013~2018)
├── Mixins → 폐기
├── HOC → 로직 재사용
└── Render Props → 유연한 렌더링 위임

Hooks 시대 (2019~2023)
├── 커스텀 Hooks → HOC/Render Props 대체
├── Context API → 전역 상태 공유
└── React.lazy + Suspense → 코드 분할

Server Components 시대 (2024~)
├── Server Components → 서버 전용 렌더링
├── Server Actions → 서버 함수 직접 호출
├── React Compiler → 자동 메모이제이션
└── use() Hook → 비동기 데이터 소비
```

---

## 요약

- **고차 컴포넌트(HOC)**: 컴포넌트를 받아 새 컴포넌트를 반환하는 함수로, 로직 재사용에 유용하지만 이름 충돌과 래퍼 헬 문제가 있다
- **렌더 프롭스**: JSX를 반환하는 함수를 prop으로 전달하여 렌더링을 위임하는 패턴으로, 명시적 데이터 흐름이 장점이다
- **Hooks**: HOC와 렌더 프롭스를 대부분 대체하며, **커스텀 Hook**을 통해 컴포넌트 구조 변경 없이 로직을 재사용할 수 있다
- **합성 패턴**: Container/Presentational, Compound Components, Slot 패턴을 통해 컴포넌트를 선언적으로 조합한다
- **상태 관리**: 로컬 상태 → 상태 끌어올리기 → Context API → 외부 라이브러리 순서로 복잡도에 따라 선택한다
- **코드 분할**: `React.lazy` + `Suspense`로 동적 가져오기를 구현하고, PRPL 패턴으로 초기 로딩을 최적화한다
- **React 19**: `use()`, Server Actions, `useOptimistic`, `useFormStatus`, `useActionState`, React Compiler 등 서버-클라이언트 통합과 자동 최적화를 향한 새로운 패턴이 도입되었다

---

## 다른 챕터와의 관계

- **← Ch01 (디자인 패턴 소개)**: 공급자 패턴 예시로 리액트 Context API를 소개했으며, 이 장에서 그 패턴을 본격적으로 다룬다
- **← Ch07 (생성 패턴)**: 팩토리 패턴은 리액트에서 동적으로 컴포넌트를 생성하는 패턴과 연결된다
- **← Ch08 (구조 패턴)**: 데코레이터 패턴은 HOC의 이론적 기반이 되며, 프록시 패턴은 리액트의 `forwardRef`와 관련된다
- **← Ch09 (행위 패턴)**: 옵저버 패턴은 리액트의 상태 관리와 리렌더링 메커니즘의 기반이다
- **← Ch11 (비동기 프로그래밍 패턴)**: Promise, async/await는 리액트의 데이터 페칭과 Server Actions의 기초가 된다
- **← Ch12 (모듈 패턴)**: ES 모듈의 정적/동적 import는 리액트의 코드 분할 전략과 직접 연결된다
- **→ Ch15 (렌더링 패턴)**: 이 장에서 다룬 CSR, SSR 개념이 다음 장에서 SSG, ISR, RSC 등으로 확장된다