# Chapter 06: Categories of Design Patterns (디자인 패턴의 유형)

## 핵심 질문

> GoF의 23가지 디자인 패턴은 어떤 기준으로 분류되며, 각 유형은 어떤 설계 문제를 해결하는가?

---

## 1. 배경 — GoF와 디자인 패턴의 분류 체계

GoF(*Gang of Four*)로 불리는 에리히 감마(*Erich Gamma*), 리차드 헬름(*Richard Helm*), 랄프 존슨(*Ralph Johnson*), 존 블리시드(*John Vlissides*)는 1995년에 **23가지 핵심 객체 지향 디자인 패턴**을 정의했다. 이 패턴들은 모두 **특정 객체 지향 설계의 문제나 이슈에 초점**을 맞추고 있다.

GoF는 이 23가지 패턴을 **문제 해결 방법의 공통점**을 기준으로 세 가지 유형으로 분류했다:

| 유형 | 영문 | 초점 |
|------|------|------|
| **생성 패턴** | Creational | 객체를 **어떻게** 만들 것인가 |
| **구조 패턴** | Structural | 객체를 **어떻게 조합**할 것인가 |
| **행위 패턴** | Behavioral | 객체 간 **어떻게 소통**할 것인가 |

이 분류 체계는 30년이 지난 지금까지도 디자인 패턴을 이해하고 학습하는 가장 기본적인 프레임워크로 사용된다. 어떤 패턴이 어떤 유형에 속하는지를 알면, 해당 패턴이 **어떤 종류의 문제를 해결하는지** 직관적으로 파악할 수 있다.

> **핵심 통찰**: 패턴을 개별적으로 외우기보다 **유형별 "관심사"를 먼저 이해**하면 23가지 패턴의 전체 지도가 머릿속에 그려진다. "이 문제는 객체 생성의 문제인가, 구조의 문제인가, 소통의 문제인가?"라고 자문하는 것이 패턴 선택의 출발점이다.

---

## 2. 생성 패턴 (Creational Patterns)

생성 패턴(*Creational Pattern*)은 **주어진 상황에 적합한 방식으로 객체를 생성하는 방법**에 중점을 둔다. 객체의 기본 생성 방식(`new` 키워드로 직접 인스턴스화)은 프로젝트의 복잡성이 증가함에 따라 설계상의 문제를 야기할 수 있다. 생성 패턴은 이러한 **객체 생성 과정을 제어**하여 상황에 맞는 방식으로 객체가 만들어지도록 한다.

### 생성 패턴이 해결하는 문제

- 어떤 구체 클래스의 인스턴스를 만들어야 하는지를 시스템이 직접 알아야 하는 **강한 결합**
- 객체 생성 로직이 여러 곳에 흩어져 있어 변경 시 **다수의 파일을 수정**해야 하는 상황
- 복잡한 초기화 절차를 가진 객체를 생성할 때 **일관성을 보장**하기 어려운 문제

### 포함 패턴

| 패턴 | 핵심 의도 |
|------|-----------|
| **Constructor** | 새 객체를 초기화하는 특별한 메서드 |
| **Factory** | 생성할 객체의 구체 클래스를 서브클래스가 결정하게 한다 |
| **Abstract Factory** | 관련된 객체 군을 구체 클래스 지정 없이 생성한다 |
| **Prototype** | 기존 객체를 복제하여 새 객체를 만든다 |
| **Singleton** | 클래스의 인스턴스가 오직 하나만 존재하도록 보장한다 |
| **Builder** | 복잡한 객체의 생성과 표현을 분리하여 단계적으로 구성한다 |

### TypeScript에서의 생성 패턴 활용

```typescript
// Factory 패턴 — 구체 클래스를 숨기고 인터페이스로 반환
interface Notification {
  send(message: string): void;
}

class EmailNotification implements Notification {
  send(message: string): void {
    console.log(`Email: ${message}`);
  }
}

class PushNotification implements Notification {
  send(message: string): void {
    console.log(`Push: ${message}`);
  }
}

function createNotification(type: "email" | "push"): Notification {
  switch (type) {
    case "email":
      return new EmailNotification();
    case "push":
      return new PushNotification();
  }
}

// 호출부는 구체 클래스를 알 필요 없다
const notification = createNotification("email");
notification.send("Hello!");
```

> **Osmani의 조언**: 생성 패턴의 핵심은 **"무엇을 만들 것인가"와 "어떻게 만들 것인가"를 분리**하는 데 있다. 이 분리가 이루어지면 새로운 종류의 객체를 추가할 때 기존 코드를 수정하지 않아도 된다.

---

## 3. 구조 패턴 (Structural Patterns)

구조 패턴(*Structural Pattern*)은 **객체의 구성(*composition*)과 각 객체 간의 관계를 인식하는 간단한 방법을 찾는 것**에 중점을 둔다. 이 패턴들은 시스템의 한 부분을 변경해도 **다른 부분에 영향을 주지 않도록** 돕는다. 또한 시스템에서 원래 설계 목적에 맞지 않는 부분을 원래 목적에 맞게 개조하는 데에도 유용하다.

### 구조 패턴이 해결하는 문제

- 서로 호환되지 않는 인터페이스를 가진 클래스들을 **함께 작동**시켜야 하는 상황
- 기존 객체에 **새로운 기능을 동적으로 추가**해야 하지만 상속은 부적절한 경우
- 복잡한 하위 시스템을 **단순한 인터페이스로 감싸** 사용 편의성을 높여야 할 때
- 수많은 유사 객체의 **메모리 사용을 최적화**해야 하는 경우

### 포함 패턴

| 패턴 | 핵심 의도 |
|------|-----------|
| **Decorator** | 객체에 동적으로 새 책임을 추가한다 |
| **Facade** | 하위 시스템의 복잡한 인터페이스를 단순화한다 |
| **Flyweight** | 다수의 유사 객체에서 공유 가능한 상태를 분리하여 메모리를 절약한다 |
| **Adapter** | 호환되지 않는 인터페이스를 변환하여 함께 작동하게 한다 |
| **Proxy** | 다른 객체에 대한 접근을 제어하는 대리자를 제공한다 |
| **Composite** | 객체를 트리 구조로 구성하여 개별 객체와 복합 객체를 동일하게 다룬다 |
| **Bridge** | 추상화와 구현을 분리하여 독립적으로 변경할 수 있게 한다 |

### TypeScript에서의 구조 패턴 활용

```typescript
// Decorator 패턴 — TC39 Stage 3 Decorators (TypeScript 5.0+)
function logged<T extends (...args: any[]) => any>(
  originalMethod: T,
  context: ClassMethodDecoratorContext,
) {
  return function (this: any, ...args: Parameters<T>): ReturnType<T> {
    console.log(`Calling ${String(context.name)} with`, args);
    const result = originalMethod.apply(this, args);
    console.log(`Result:`, result);
    return result;
  };
}

class Calculator {
  @logged
  add(a: number, b: number): number {
    return a + b;
  }
}

const calc = new Calculator();
calc.add(2, 3);
// "Calling add with [2, 3]"
// "Result: 5"
```

```typescript
// Proxy 패턴 — ES6 Proxy로 접근 제어
interface User {
  name: string;
  email: string;
  _password: string;
}

function createSafeUser(user: User): User {
  return new Proxy(user, {
    get(target, prop: string) {
      if (prop.startsWith("_")) {
        throw new Error(`Access denied: ${prop} is private`);
      }
      return Reflect.get(target, prop);
    },
  });
}

const user = createSafeUser({ name: "Alice", email: "a@b.com", _password: "secret" });
console.log(user.name);      // "Alice"
// console.log(user._password); // Error: Access denied
```

> **핵심 통찰**: 구조 패턴은 **"레고 블록"**에 비유할 수 있다. 각 블록(객체)의 내부를 변경하지 않으면서도, 조합 방식을 바꾸거나 어댑터를 끼워 넣어 전체 구조의 유연성을 확보한다.

---

## 4. 행위 패턴 (Behavioral Patterns)

행위 패턴(*Behavioral Pattern*)은 시스템 내 **객체 간의 커뮤니케이션을 개선하거나 간소화**하는 것에 중점을 둔다. 이 패턴들은 서로 다른 객체 간의 **공통 커뮤니케이션 패턴을 감지**하고, 각 객체에 **책임을 효과적으로 분배**하는 방법을 제시한다.

### 행위 패턴이 해결하는 문제

- 객체 간 **강한 결합**으로 인해 하나의 변경이 연쇄적인 수정을 초래하는 문제
- **알고리즘의 교체**가 필요한데 기존 코드를 수정해야 하는 상황
- 객체의 **상태 변화를 다른 객체들에게 통지**해야 하지만, 통지 대상이 유동적인 경우
- 복잡한 **요청 처리 체인**을 유연하게 구성해야 하는 상황

### 포함 패턴

| 패턴 | 핵심 의도 |
|------|-----------|
| **Iterator** | 컬렉션의 내부 구조를 노출하지 않고 요소에 순차 접근한다 |
| **Mediator** | 객체들 간의 직접 소통을 금지하고 중재자를 통해서만 소통하게 한다 |
| **Observer** | 한 객체의 상태 변화를 관찰하는 다수의 객체에게 자동 통지한다 |
| **Visitor** | 객체 구조를 변경하지 않고 새로운 연산을 추가한다 |
| **Strategy** | 알고리즘 군을 정의하고 교체 가능하게 캡슐화한다 |
| **State** | 객체의 내부 상태에 따라 행동을 변경한다 |
| **Command** | 요청을 객체로 캡슐화하여 매개변수화, 큐잉, 로깅, 취소를 가능하게 한다 |
| **Template Method** | 알고리즘의 뼈대를 정의하고 세부 단계를 서브클래스에 위임한다 |
| **Chain of Responsibility** | 요청을 처리할 수 있는 객체들의 체인을 구성하여 순서대로 전달한다 |
| **Memento** | 객체의 이전 상태를 저장하고 복원할 수 있게 한다 |
| **Interpreter** | 언어의 문법을 정의하고 해당 문법으로 문장을 해석한다 |

### TypeScript에서의 행위 패턴 활용

```typescript
// Observer 패턴 — 제네릭을 활용한 타입 안전한 이벤트 시스템
type Listener<T> = (data: T) => void;

class EventEmitter<EventMap extends Record<string, unknown>> {
  private listeners = new Map<keyof EventMap, Set<Listener<any>>>();

  on<K extends keyof EventMap>(event: K, listener: Listener<EventMap[K]>): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(listener);
  }

  off<K extends keyof EventMap>(event: K, listener: Listener<EventMap[K]>): void {
    this.listeners.get(event)?.delete(listener);
  }

  emit<K extends keyof EventMap>(event: K, data: EventMap[K]): void {
    this.listeners.get(event)?.forEach((listener) => listener(data));
  }
}

// 사용 예시 — 이벤트명과 데이터 타입이 컴파일 타임에 검증된다
interface AppEvents {
  userLogin: { userId: string; timestamp: number };
  itemAdded: { itemId: string; quantity: number };
}

const emitter = new EventEmitter<AppEvents>();
emitter.on("userLogin", (data) => {
  console.log(`User ${data.userId} logged in`); // data 타입 자동 추론
});
```

```typescript
// Strategy 패턴 — 함수형 스타일
type SortStrategy<T> = (items: T[]) => T[];

const bubbleSort: SortStrategy<number> = (items) => {
  const arr = [...items];
  for (let i = 0; i < arr.length; i++) {
    for (let j = 0; j < arr.length - i - 1; j++) {
      if (arr[j] > arr[j + 1]) [arr[j], arr[j + 1]] = [arr[j + 1], arr[j]];
    }
  }
  return arr;
};

const quickSort: SortStrategy<number> = (items) => {
  if (items.length <= 1) return items;
  const pivot = items[0];
  const left = items.slice(1).filter((x) => x <= pivot);
  const right = items.slice(1).filter((x) => x > pivot);
  return [...quickSort(left), pivot, ...quickSort(right)];
};

class Sorter<T> {
  constructor(private strategy: SortStrategy<T>) {}

  setStrategy(strategy: SortStrategy<T>): void {
    this.strategy = strategy;
  }

  sort(items: T[]): T[] {
    return this.strategy(items);
  }
}

const sorter = new Sorter(bubbleSort);
sorter.sort([3, 1, 4, 1, 5]); // bubbleSort 사용
sorter.setStrategy(quickSort);
sorter.sort([3, 1, 4, 1, 5]); // quickSort로 교체
```

> **Osmani의 조언**: 행위 패턴은 흔히 "가장 많이 사용되는" 유형이다. 대부분의 애플리케이션에서 가장 복잡한 부분은 객체 생성이나 구조가 아니라 **객체 간 상호작용**이기 때문이다.

---

## 5. 디자인 패턴의 분류 — 클래스 vs 객체

GoF는 세 가지 유형 외에 **클래스 기반**과 **객체 기반**이라는 또 다른 축을 추가하여 패턴을 더 세밀하게 분류했다. 엘리스 닐슨(*Elis Nielsen*)의 2004년 분류표는 이 매트릭스를 정리한 것으로, 패턴이 주로 **클래스 간의 관계**(상속)를 다루는지 **객체 간의 관계**(합성)를 다루는지를 구분한다.

### 클래스 패턴 vs 객체 패턴

| 구분 | 클래스 패턴 | 객체 패턴 |
|------|-------------|-----------|
| **관계 형성 시점** | 컴파일 타임 (상속) | 런타임 (합성/위임) |
| **메커니즘** | 클래스 상속 (`extends`) | 객체 합성, 위임, 참조 |
| **유연성** | 정적 — 실행 중 변경 불가 | 동적 — 실행 중 변경 가능 |
| **GoF 원칙** | — | "상속보다 합성을 선호하라" |

### GoF 23가지 패턴 분류표

엘리스 닐슨(*Elyse Nielsen*)이 2004년에 정리한 분류표를 바탕으로, GoF의 23가지 패턴 전체를 유형/범위/패턴/설명으로 정리하면 다음과 같다.

| 유형 | 범위 | 패턴 | 설명 |
|------|------|------|------|
| **생성** | 클래스 | Factory Method | 인터페이스를 기반으로 여러 파생 클래스를 생성 |
| **생성** | 객체 | Abstract Factory | 구체적인 내부 구현 없이 여러 클래스가 상속받아 사용하는 인스턴스를 생성 |
| **생성** | 객체 | Builder | 객체를 생성하는 부분과 내부 구현을 분리하여 항상 같은 유형의 객체를 생성 |
| **생성** | 객체 | Prototype | 복사 또는 복제에 사용되는 초기화된 인스턴스 |
| **생성** | 객체 | Singleton | 전역에서 접근 가능한 하나만의 인스턴스를 가진 클래스 |
| **구조** | 클래스 | Adapter | 호환되지 않는 인터페이스가 상호작용하도록 클래스를 매치 |
| **구조** | 객체 | Bridge | 객체의 인터페이스와 구현을 분리하여 독립적으로 구성 |
| **구조** | 객체 | Composite | 단순히 합친 상태 이상의 효율을 내는 간단하면서 복합적인 구조 |
| **구조** | 객체 | Decorator | 객체에 새로운 프로세스를 동적으로 추가 |
| **구조** | 객체 | Facade | 전체 시스템의 복잡한 부분을 숨기는 단일 클래스 |
| **구조** | 객체 | Flyweight | 여러 객체에 공통 상태를 공유하는 세분화된 인스턴스 |
| **구조** | 객체 | Proxy | 실제 객체를 대신하는 대체 객체 |
| **행위** | 클래스 | Interpreter | 언어의 목적과 문법에 일치하는 언어 요소를 포함시키는 방법 |
| **행위** | 클래스 | Template Method | 상위 클래스에서 기본 구조를 생성한 다음 하위 클래스에서 구체적으로 정의 |
| **행위** | 객체 | Chain of Responsibility | 요청을 처리할 수 있는 객체를 찾기 위해 체인 간에 요청을 전달 |
| **행위** | 객체 | Command | 호출 부분과 실행 부분을 나누는 방법 |
| **행위** | 객체 | Iterator | 내부 구조를 모른 채 요소에 순차적으로 접근 |
| **행위** | 객체 | Mediator | 클래스가 서로를 직접적으로 참조하지 않도록 중간에 간소화된 커뮤니케이션을 정의 |
| **행위** | 객체 | Memento | 나중에 복구할 수 있도록 객체의 내부 상태를 저장 |
| **행위** | 객체 | Observer | 클래스 간의 일관성을 보장하기 위해 여러 클래스에 변경 사항을 알리는 방법 |
| **행위** | 객체 | State | 상태가 변경되면 객체의 행위도 변경 |
| **행위** | 객체 | Strategy | 클래스 내부에 알고리즘 구현을 캡슐화하여 상황에 따른 선택과 구현을 분리 |
| **행위** | 객체 | Visitor | 클래스를 변경하지 않고도 새로운 작업을 추가 |

이 표에서 주목할 점은 **객체 패턴이 클래스 패턴보다 압도적으로 많다**는 것이다. 클래스 범위의 패턴은 Factory Method, Adapter, Interpreter, Template Method 단 4개뿐이며, 나머지 19개는 모두 객체 범위다. 이는 GoF가 제안한 "상속보다 합성을 선호하라"(*Favor composition over inheritance*)는 원칙과 정확히 일치한다. 현대 TypeScript 개발에서도 이 원칙은 더욱 강조되고 있다.

> **핵심 통찰**: 매트릭스를 통째로 외울 필요는 없다. 중요한 것은 **대부분의 유용한 패턴이 객체 합성 기반**이라는 점이다. 클래스 상속은 간단한 경우에만 사용하고, 복잡한 관계에서는 합성을 통해 유연성을 확보하는 것이 현대적 설계의 방향이다.

---

## 6. 현대 자바스크립트/타입스크립트에서의 패턴 분류

GoF의 23가지 패턴은 1995년에 C++과 Smalltalk를 기반으로 정의되었다. 30년이 지난 현대 자바스크립트/타입스크립트 환경에서는 **언어 자체의 발전**으로 인해 일부 패턴의 위상이 크게 달라졌다. 어떤 패턴은 여전히 핵심적이고, 어떤 패턴은 언어 기능에 흡수되었으며, 어떤 패턴은 완전히 다른 형태로 변형되었다.

### 여전히 핵심적인 패턴

다음 패턴들은 현대 JS/TS에서도 **명시적으로 구현해야 하는 상황이 빈번**하다:

- **Observer** — 상태 관리, 이벤트 시스템, 리액티브 프로그래밍의 근간
- **Strategy** — 알고리즘 교체, 렌더링 전략 선택, 정렬/필터 로직 분리
- **Factory** — 컴포넌트 동적 생성, API 응답 기반 객체 생성
- **Decorator** — TC39 데코레이터 표준화(TypeScript 5.0+)로 언어 수준에서 지원
- **Facade** — 복잡한 API를 커스텀 Hook이나 래퍼 함수로 단순화
- **Composite** — React/JSX의 컴포넌트 트리 자체가 Composite 구조
- **Command** — `useReducer`의 action dispatch, undo/redo 구현
- **Mediator** — 상태 관리 스토어(Redux, Zustand)가 Mediator 역할

### 언어 기능에 흡수된 패턴

다음 패턴들은 **언어 또는 런타임이 이미 제공**하므로, 별도로 구현할 필요가 거의 없다:

- **Iterator** — `for...of`, 제너레이터(`function*`), `Symbol.iterator`가 내장
- **Singleton** — ES 모듈이 본질적으로 싱글톤 (모듈 스코프는 한 번만 평가됨)
- **Prototype** — `Object.create()`, 프로토타입 체인이 언어의 핵심 메커니즘
- **Proxy** — ES6 `Proxy` 객체가 네이티브로 제공

### 다른 형태로 변형된 패턴

다음 패턴들은 GoF의 원래 형태와 달리, **현대적 도구나 패러다임으로 대체**되었다:

- **Observer** → `EventEmitter`(Node.js), RxJS Observable, Signals(Angular/Solid/Preact)
- **Template Method** → 고차 함수(*Higher-Order Function*)와 콜백으로 대체
- **State** → 유한 상태 머신 라이브러리(XState), `useReducer`
- **Chain of Responsibility** → Express/Koa 미들웨어 체인, Next.js 미들웨어

### 전통 GoF vs 현대 JS/TS 대응 비교

| 패턴 | 전통 (GoF) | 현대 JS/TS 대응 |
|------|-----------|----------------|
| **Iterator** | Iterator 인터페이스 구현 | `for...of`, generators, `Symbol.iterator` |
| **Observer** | Subject/Observer 클래스 | `EventEmitter`, RxJS, Signals, `useState`/`useEffect` |
| **Singleton** | static instance + private constructor | ES Module 스코프 (모듈 자체가 싱글톤) |
| **Factory** | Factory 클래스 계층 | 팩토리 함수, 판별 유니온(*Discriminated Union*) |
| **Proxy** | Proxy 클래스 수동 구현 | ES6 `Proxy` 객체, `Reflect` API |
| **Prototype** | clone() 메서드 구현 | `Object.create()`, 스프레드 연산자(`...`), `structuredClone()` |
| **Decorator** | 래퍼 클래스 중첩 | TC39 Decorators(`@decorator`), 고차 함수 |
| **Template Method** | 추상 클래스 + 메서드 오버라이드 | 콜백 함수, 고차 함수, Hook 패턴 |
| **State** | State 인터페이스 + 구체 State 클래스 | XState, `useReducer`, 유한 상태 머신 |
| **Chain of Responsibility** | Handler 체인 클래스 | Express/Koa 미들웨어, Next.js 미들웨어 |
| **Mediator** | Mediator 인터페이스 | Redux, Zustand, 이벤트 버스 |
| **Command** | Command 인터페이스 + 구체 Command | `useReducer` action, Redux action/reducer |
| **Memento** | Memento 객체로 상태 스냅샷 | `structuredClone()`, Immer의 불변 상태 |

```typescript
// Iterator — 언어에 내장된 패턴
class Range {
  constructor(private start: number, private end: number) {}

  // Symbol.iterator를 구현하면 for...of에서 자동으로 사용된다
  *[Symbol.iterator](): Iterator<number> {
    for (let i = this.start; i <= this.end; i++) {
      yield i;
    }
  }
}

for (const num of new Range(1, 5)) {
  console.log(num); // 1, 2, 3, 4, 5
}

// Singleton — ES Module이 자체적으로 싱글톤을 보장
// config.ts
const config = {
  apiUrl: process.env.API_URL ?? "https://api.example.com",
  timeout: 5000,
} as const;

export default config;
// 어디서 import해도 동일한 객체 참조 — 별도 Singleton 클래스 불필요

// Proxy — ES6 Proxy로 접근 제어
function createReactive<T extends object>(
  target: T,
  onChange: (prop: string, value: unknown) => void,
): T {
  return new Proxy(target, {
    set(obj, prop, value) {
      const result = Reflect.set(obj, prop, value);
      onChange(String(prop), value);
      return result;
    },
  });
}

const state = createReactive({ count: 0 }, (prop, value) => {
  console.log(`${prop} changed to ${value}`);
});
state.count = 1; // "count changed to 1"
```

> **Osmani의 조언**: 패턴을 GoF 원서 그대로 구현하려는 강박을 버려야 한다. 현대 자바스크립트는 1995년의 C++과는 완전히 다른 언어다. 패턴의 **의도**(*intent*)를 이해하고, 그 의도를 현대적 도구로 실현하는 것이 올바른 접근이다.

---

## 7. 세 유형 한눈에 비교

| 비교 항목 | 생성 패턴 | 구조 패턴 | 행위 패턴 |
|-----------|-----------|-----------|-----------|
| **핵심 질문** | "무엇을 만들까?" | "어떻게 조합할까?" | "어떻게 소통할까?" |
| **관심사** | 객체 인스턴스화 | 클래스/객체 구성 | 객체 간 책임 분배 |
| **문제 해결 방향** | 생성 로직 캡슐화 | 인터페이스 적응/단순화 | 통신 패턴 정형화 |
| **GoF 패턴 수** | 5개 | 7개 | 11개 |
| **대표 패턴** | Factory, Singleton | Decorator, Facade | Observer, Strategy |
| **TypeScript 핵심 기능** | 제네릭, 인터페이스 | 데코레이터, Proxy | 이벤트, 콜백, 제네릭 |

---

## 실무 적용 가이드

### 패턴 유형별 선택 플로우차트

문제를 마주했을 때 어떤 유형의 패턴을 고려해야 하는지 판단하는 기준:

```
문제 분석 시작
│
├─ "객체를 만드는 방식이 복잡하거나 변경이 잦은가?"
│   └─ YES → 생성 패턴 고려
│       ├─ 객체 종류가 런타임에 결정 → Factory / Abstract Factory
│       ├─ 생성 절차가 복잡하고 단계적 → Builder
│       ├─ 인스턴스가 하나여야 함 → Singleton
│       └─ 기존 객체와 유사한 객체 필요 → Prototype
│
├─ "기존 객체/클래스의 인터페이스나 구조를 변경해야 하는가?"
│   └─ YES → 구조 패턴 고려
│       ├─ 호환되지 않는 인터페이스 연결 → Adapter
│       ├─ 기능을 동적으로 추가 → Decorator
│       ├─ 복잡한 시스템을 단순화 → Facade
│       ├─ 접근 제어 필요 → Proxy
│       └─ 메모리 최적화 필요 → Flyweight
│
└─ "객체 간 상호작용이나 책임 분배가 문제인가?"
    └─ YES → 행위 패턴 고려
        ├─ 상태 변화 통지 → Observer
        ├─ 알고리즘 교체 → Strategy
        ├─ 요청을 객체로 캡슐화 → Command
        ├─ 객체 간 직접 의존 줄이기 → Mediator
        └─ 상태 기반 행동 변경 → State
```

### 유형별 실수하기 쉬운 함정

| 유형 | 흔한 실수 | 올바른 접근 |
|------|-----------|-------------|
| **생성** | 모든 객체 생성에 Factory 적용 | 생성 로직이 **실제로 복잡하거나 변경 가능성이 있을 때**만 적용 |
| **생성** | Singleton 남용 | 전역 상태가 **정말 필요한지** 먼저 검토 — 대부분 의존성 주입으로 대체 가능 |
| **구조** | Decorator 중첩으로 디버깅 곤란 | 데코레이터 체인이 3단계를 넘으면 설계를 재검토 |
| **구조** | Facade가 God Object로 변질 | Facade는 **위임만** 해야 하며, 자체 로직을 가져서는 안 된다 |
| **행위** | Observer에서 메모리 누수 | 구독 해제(`unsubscribe`)를 반드시 구현 — React의 `useEffect` cleanup |
| **행위** | Strategy 패턴을 if-else로 대체 | 전략이 2개 이하이고 변경 가능성이 낮으면 단순 조건문이 더 적합 |

---

## 요약

- GoF의 23가지 디자인 패턴은 **생성, 구조, 행위** 세 가지 유형으로 분류된다
- **생성 패턴**은 객체를 "어떻게 만들 것인가"에 초점을 두며, Factory, Singleton, Builder 등이 포함된다
- **구조 패턴**은 객체를 "어떻게 조합할 것인가"에 초점을 두며, Decorator, Facade, Adapter 등이 포함된다
- **행위 패턴**은 객체 간 "어떻게 소통할 것인가"에 초점을 두며, Observer, Strategy, Command 등이 포함된다
- 클래스 기반 vs 객체 기반의 추가 분류축이 있으며, **객체 합성 기반 패턴이 압도적으로 많다** — 이는 "상속보다 합성" 원칙과 일치한다
- 현대 JS/TS에서는 일부 패턴(Iterator, Singleton, Proxy 등)이 **언어 기능에 흡수**되었고, 일부(Observer, State, Chain of Responsibility 등)는 **현대적 도구로 변형**되었다
- 패턴 선택의 출발점은 **"이 문제가 생성의 문제인가, 구조의 문제인가, 소통의 문제인가?"**를 자문하는 것이다

---

## 다른 챕터와의 관계

- **← Ch01 (디자인 패턴 소개)**: GoF의 23가지 패턴이 존재한다는 사실을 처음 언급했으며, 이 챕터에서 세 유형으로 분류한다
- **← Ch05 (모던 자바스크립트 문법)**: ES2015+ 클래스, 모듈, Proxy 등 이 챕터의 코드 예시에서 활용하는 문법의 기초를 다룬다
- **→ Ch07 (생성 패턴)**: 이 챕터에서 개요로 소개한 생성 패턴 각각을 TypeScript로 상세 구현한다
- **→ Ch08 (구조 패턴)**: Decorator, Facade, Flyweight, Adapter, Proxy 등 구조 패턴의 상세 구현을 다룬다
- **→ Ch09 (행위 패턴)**: Observer, Strategy, Mediator, Command, State 등 행위 패턴의 상세 구현을 다룬다