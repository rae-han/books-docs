# Chapter 09: Behavioral Patterns (행위 패턴)

## 핵심 질문

> 객체 간의 커뮤니케이션과 책임 분배를 어떻게 설계하면 느슨한 결합을 유지하면서도 복잡한 워크플로를 구현할 수 있는가? TypeScript/현대 자바스크립트에서 각 행위 패턴은 어떻게 구현되는가?

---

## 행위 패턴 개요

행위 패턴(*Behavioral Pattern*)은 **객체 간의 의사소통을 돕는** 패턴이다. 객체가 서로 어떻게 상호작용하고, 책임을 어떻게 분배하는지에 초점을 맞춘다.

이 장에서 다루는 행위 패턴:

| 패턴 | 의도 |
|------|------|
| **관찰자** (*Observer*) | 주체의 상태 변화를 관찰자에게 자동 통지 |
| **중재자** (*Mediator*) | 객체 간 직접 참조를 중앙 허브로 대체 |
| **커맨드** (*Command*) | 메서드 호출을 객체로 캡슐화 |
| **이터레이터** (*Iterator*) | 컬렉션의 내부 구조를 노출하지 않고 순차 접근 |
| **전략** (*Strategy*) | 알고리즘 가족을 캡슐화하여 교체 가능하게 |
| **상태** (*State*) | 내부 상태에 따라 객체의 행동을 변경 |
| **템플릿 메서드** (*Template Method*) | 알고리즘 골격을 정의하고 일부 단계를 하위 클래스에 위임 |
| **책임 연쇄** (*Chain of Responsibility*) | 요청을 처리자 체인을 따라 전달 |
| **방문자** (*Visitor*) | 클래스 변경 없이 새로운 연산을 추가 |

> **Osmani의 조언**: 행위 패턴은 시스템의 여러 부분이 "어떻게 대화하는가"를 설계하는 것이다. 잘못된 커뮤니케이션 패턴은 강한 결합과 유지보수의 악몽을 초래한다. 패턴의 의도를 정확히 이해하고, 상황에 맞는 패턴을 선택하라.

---

## 1. 관찰자 패턴 (Observer Pattern)

관찰자(*Observer*) 패턴은 한 객체(주체)가 변경될 때 다른 객체들(관찰자)에 변경되었음을 알릴 수 있게 해주는 패턴이다. 주체의 상태가 변하면 관찰자들에게 자동으로 알림을 보낸다. 최신 프레임워크에서는 상태의 변화를 컴포넌트에 알리기 위해 관찰자 패턴을 사용하곤 한다.

### 패턴 카드: Observer

| 항목 | 설명 |
|------|------|
| **의도** | 한 객체의 상태 변화를 의존하는 모든 객체에게 자동으로 알린다 |
| **사용 시점** | 하나의 객체 변경이 다른 여러 객체에 연쇄적으로 반영되어야 할 때 |
| **미사용 시점** | 알림 대상이 항상 하나뿐이거나, 동기적 직접 호출이 더 명확한 경우 |
| **장점** | 느슨한 결합, 동적 구독/해제, 일대다 의존성 관리 |
| **단점** | 구독자 추적 어려움, 메모리 누수(구독 해제 누락), 알림 순서 보장 어려움 |

### 1.1 구성 요소

관찰자 패턴의 핵심 구성 요소는 네 가지다:

- **주체**(*Subject*): 관찰자 리스트를 관리하고, 추가와 삭제를 가능하게 한다.
- **관찰자**(*Observer*): 주체의 상태 변화 알림을 감지하는 `update` 인터페이스를 제공한다.
- **구체적 주체**(*ConcreteSubject*): 상태 변화에 대한 알림을 모든 관찰자에게 전달하고, 자신의 상태를 저장한다.
- **구체적 관찰자**(*ConcreteObserver*): 주체의 참조를 저장하고, 관찰자의 `update` 인터페이스를 구현하여 주체의 상태 변화에 반응한다.

### 1.2 TypeScript 구현

```typescript
// 관찰자 인터페이스
interface Observer<T> {
  update(data: T): void;
}

// 주체 인터페이스
interface Subject<T> {
  subscribe(observer: Observer<T>): void;
  unsubscribe(observer: Observer<T>): void;
  notify(data: T): void;
}

// 구체적 주체 — 주식 가격을 관찰하는 예제
class StockTicker implements Subject<StockUpdate> {
  #observers = new Set<Observer<StockUpdate>>();
  #prices = new Map<string, number>();

  subscribe(observer: Observer<StockUpdate>): void {
    this.#observers.add(observer);
  }

  unsubscribe(observer: Observer<StockUpdate>): void {
    this.#observers.delete(observer);
  }

  notify(data: StockUpdate): void {
    for (const observer of this.#observers) {
      observer.update(data);
    }
  }

  updatePrice(symbol: string, price: number): void {
    const prev = this.#prices.get(symbol);
    this.#prices.set(symbol, price);
    this.notify({ symbol, price, previousPrice: prev });
  }
}

interface StockUpdate {
  symbol: string;
  price: number;
  previousPrice?: number;
}

// 구체적 관찰자 — 가격 표시
class PriceDisplay implements Observer<StockUpdate> {
  update(data: StockUpdate): void {
    console.log(`[Display] ${data.symbol}: $${data.price}`);
  }
}

// 구체적 관찰자 — 큰 변동 경고
class PriceAlert implements Observer<StockUpdate> {
  constructor(private threshold: number) {}

  update(data: StockUpdate): void {
    if (data.previousPrice === undefined) return;
    const change = Math.abs(data.price - data.previousPrice) / data.previousPrice;
    if (change > this.threshold) {
      console.log(
        `[ALERT] ${data.symbol} changed by ${(change * 100).toFixed(1)}%!`
      );
    }
  }
}

// 사용
const ticker = new StockTicker();
const display = new PriceDisplay();
const alert5 = new PriceAlert(0.05);

ticker.subscribe(display);
ticker.subscribe(alert5);

ticker.updatePrice("AAPL", 150);
// [Display] AAPL: $150

ticker.updatePrice("AAPL", 165);
// [Display] AAPL: $165
// [ALERT] AAPL changed by 10.0%!

ticker.unsubscribe(alert5); // 구독 해제
```

### JavaScript vs TypeScript

```javascript
// JavaScript — 인터페이스가 없으므로 observer.update 존재 여부를 런타임에 확인해야 함
class StockTicker {
  #observers = new Set();

  subscribe(observer) {
    if (typeof observer.update !== "function") {
      throw new Error("Observer must implement update()");
    }
    this.#observers.add(observer);
  }

  notify(data) {
    for (const observer of this.#observers) {
      observer.update(data);
    }
  }
}
```

```typescript
// TypeScript — Observer<T> 인터페이스를 implements하지 않으면 컴파일 에러
// observer.update()의 매개변수 타입도 제네릭으로 안전하게 강제
class PriceAlert implements Observer<StockUpdate> {
  update(data: StockUpdate): void { /* ... */ }
  //     ^? data: StockUpdate — 타입이 보장됨
}
```

### 1.3 발행/구독 패턴 (Publish/Subscribe)

관찰자 패턴의 변형인 발행/구독(*Pub/Sub*) 패턴은 실제 자바스크립트 환경에서 더 널리 사용된다. 핵심 차이는 **토픽/이벤트 채널**을 중간에 두어 발행자와 구독자를 완전히 분리한다는 것이다.

| 비교 항목 | 관찰자 패턴 | 발행/구독 패턴 |
|-----------|------------|--------------|
| **결합도** | 주체가 관찰자 목록을 직접 관리 | 발행자와 구독자가 서로 모름 |
| **통신 방식** | 직접 호출 (`observer.update()`) | 토픽/채널 기반 간접 통신 |
| **필터링** | 없음 (모든 변경 수신) | 토픽별 선택적 구독 |
| **사용 사례** | 같은 모듈 내 상태 동기화 | 모듈 간 이벤트 전달 |

```typescript
// 타입 안전한 Pub/Sub 구현
type EventMap = Record<string, unknown>;
type EventHandler<T> = (data: T) => void;

class EventBus<E extends EventMap> {
  #handlers = new Map<keyof E, Set<EventHandler<any>>>();

  on<K extends keyof E>(event: K, handler: EventHandler<E[K]>): () => void {
    if (!this.#handlers.has(event)) {
      this.#handlers.set(event, new Set());
    }
    this.#handlers.get(event)!.add(handler);

    // 구독 해제 함수 반환 — 메모리 누수 방지
    return () => {
      this.#handlers.get(event)?.delete(handler);
    };
  }

  emit<K extends keyof E>(event: K, data: E[K]): void {
    this.#handlers.get(event)?.forEach((handler) => handler(data));
  }
}

// 이벤트 맵 정의 — 토픽별 데이터 타입을 강제
interface AppEvents {
  "user:login": { userId: string; timestamp: number };
  "cart:add": { productId: string; quantity: number };
  "order:complete": { orderId: string; total: number };
}

const bus = new EventBus<AppEvents>();

const unsubscribe = bus.on("user:login", (data) => {
  console.log(`User ${data.userId} logged in`);
  //                  ^? data: { userId: string; timestamp: number }
});

bus.emit("user:login", { userId: "u123", timestamp: Date.now() });

// bus.emit("user:login", { wrong: "data" });
// ^^^^^^^ Error: '{ wrong: string }'은 할당할 수 없습니다

unsubscribe(); // 구독 해제
```

> **핵심 통찰**: 관찰자 패턴에서 가장 흔한 버그는 **구독 해제 누락**이다. TypeScript의 Pub/Sub에서 `on()` 메서드가 `unsubscribe` 함수를 반환하도록 설계하면, 구독 해제를 잊는 실수를 줄일 수 있다. React의 `useEffect` 클린업이 이 패턴을 따른다.

### 1.4 장점과 단점

**장점**:
- 애플리케이션을 더 작고 느슨하게 연결된 부분으로 나눌 수 있다
- 클래스를 강하게 결합시키지 않으면서 관련 객체 간의 일관성을 유지할 수 있다
- 동적인 관계가 형성되어 뛰어난 유연성을 제공한다

**단점**:
- 발행자와 구독자의 연결이 분리되어, 애플리케이션의 특정 부분이 기대하는 대로 동작하는지 보장하기 어려워질 수 있다
- 구독자들이 서로의 존재를 모르고, 발행자를 변경하는 데 드는 비용을 파악할 수 없다
- 구독자와 발행자 사이의 관계가 동적으로 결정되므로 추적이 어려울 수 있다

---

## 2. 중재자 패턴 (Mediator Pattern)

중재자(*Mediator*) 패턴은 하나의 객체가 이벤트 발생 시 다른 여러 객체들에게 알림을 보낼 수 있는 디자인 패턴이다. 시스템의 구성 요소들 사이에 직접적인 관계가 너무 많을 때, 중앙 통제 포인트를 두어 모든 구성 요소들이 이를 통해 간접적으로 소통하게 한다.

현실 세계의 비유로는 항공 교통 관제 시스템이 있다. 관제탑(중재자)은 모든 항공기의 통신이 관제탑을 거쳐 이루어지게 하고, 항공기끼리 직접 통신하지 않게 한다.

### 패턴 카드: Mediator

| 항목 | 설명 |
|------|------|
| **의도** | 객체 간 직접 참조를 제거하고 중앙 허브를 통해 간접 소통하게 한다 |
| **사용 시점** | 여러 객체 간 복잡한 상호작용이 있고, 워크플로 로직을 한 곳에 집중하고 싶을 때 |
| **미사용 시점** | 객체 간 관계가 단순하여 중재자가 오히려 복잡성을 추가할 때 |
| **장점** | 느슨한 결합, 워크플로 한눈에 파악, 구성 요소 재사용성 향상 |
| **단점** | 중재자가 "갓 객체"로 비대해질 위험, 중재자 자체가 단일 실패 지점 |

### 2.1 관찰자 패턴 vs 중재자 패턴

이 두 패턴은 유사해 보이지만 근본적인 차이가 있다:

| 비교 항목 | 관찰자 / Pub/Sub (이벤트 집합) | 중재자 |
|-----------|-------------------------------|--------|
| **로직 위치** | 이벤트 소스와 핸들러에 분산 | 중재자 내부에 집중 |
| **의도** | 이벤트 전파 — "발행 후 망각" | 워크플로 조율 — 의사결정 |
| **방향성** | 다방향 (누구나 발행/구독) | 중앙 집중 (중재자가 조율) |
| **사용 사례** | 독립적 이벤트 처리 | 비즈니스 로직에 따른 상호작용 조정 |

> **Osmani의 조언**: 설령 두 패턴의 구현이 유사한 핵심 구조를 사용한다 하더라도, 그 안에는 근본적인 차이가 존재한다. 이벤트 집합 패턴은 "발행 후 망각" 방식이지만, 중재자 패턴은 미리 설정해 둔 특정 입력에 주목하여 역할이 분명한 참여자 사이의 행동을 조율하고 촉진한다.

### 2.2 채팅방 예제

```typescript
// 동료(Colleague) 인터페이스
interface ChatUser {
  name: string;
  receive(from: string, message: string): void;
}

// 중재자
class ChatRoom {
  #users = new Map<string, ChatUser>();

  join(user: ChatUser): void {
    this.#users.set(user.name, user);
    this.broadcast("System", `${user.name} joined the room`);
  }

  leave(userName: string): void {
    this.#users.delete(userName);
    this.broadcast("System", `${userName} left the room`);
  }

  // 특정 사용자에게 메시지 전달 — 중재자가 라우팅 결정
  send(from: string, to: string, message: string): void {
    const recipient = this.#users.get(to);
    if (recipient) {
      recipient.receive(from, message);
    } else {
      this.#users.get(from)?.receive("System", `${to} is not in the room`);
    }
  }

  // 전체 브로드캐스트 — 발신자를 제외하고 전파
  broadcast(from: string, message: string): void {
    for (const [name, user] of this.#users) {
      if (name !== from) {
        user.receive(from, message);
      }
    }
  }
}

// 구체적 동료
class User implements ChatUser {
  constructor(
    public readonly name: string,
    private room: ChatRoom,
  ) {}

  receive(from: string, message: string): void {
    console.log(`[${this.name}] ${from}: ${message}`);
  }

  send(to: string, message: string): void {
    this.room.send(this.name, to, message);
  }

  broadcast(message: string): void {
    this.room.broadcast(this.name, message);
  }
}

// 사용
const room = new ChatRoom();

const alice = new User("Alice", room);
const bob = new User("Bob", room);
const charlie = new User("Charlie", room);

room.join(alice);   // [Bob] System: Alice joined the room
room.join(bob);     // [Alice] System: Bob joined the room
room.join(charlie);

alice.send("Bob", "Hi Bob!");
// [Bob] Alice: Hi Bob!

alice.broadcast("Hello everyone!");
// [Bob] Alice: Hello everyone!
// [Charlie] Alice: Hello everyone!
```

핵심은 `User`끼리 직접 참조하지 않는다는 것이다. 모든 메시지는 `ChatRoom`(중재자)을 통해 라우팅되며, 중재자가 수신자 존재 여부 확인, 브로드캐스트 범위 결정 등 **워크플로 로직**을 담당한다.

### 2.3 중재자 vs 퍼사드

두 패턴 모두 기존 모듈의 기능을 추상화하지만 미묘한 차이가 있다:

| 비교 | 중재자 | 퍼사드 |
|------|--------|--------|
| **방향** | 다방향 (모듈 ↔ 중재자 ↔ 모듈) | 단방향 (클라이언트 → 퍼사드 → 서브시스템) |
| **인지** | 모듈이 중재자를 명시적으로 참조 | 서브시스템이 퍼사드를 모름 |
| **목적** | 워크플로 조율 | 복잡한 인터페이스 단순화 |

---

## 3. 커맨드 패턴 (Command Pattern)

커맨드(*Command*) 패턴은 메서드 호출, 요청 또는 작업을 **단일 객체로 캡슐화**하여 추후에 실행할 수 있도록 해준다. 명령을 내리는 객체와 명령을 실행하는 객체의 책임을 분리하며, `execute()`와 `undo()`를 통해 실행/취소를 지원한다.

### 패턴 카드: Command

| 항목 | 설명 |
|------|------|
| **의도** | 요청을 객체로 캡슐화하여 매개변수화, 큐잉, 로깅, 취소를 지원한다 |
| **사용 시점** | 실행 취소/재실행이 필요하거나, 요청을 큐에 넣어 나중에 실행해야 할 때 |
| **미사용 시점** | 단순한 직접 메서드 호출이 더 명확한 경우 |
| **장점** | 실행/취소 지원, 매크로 명령 조합, 호출자와 수신자 분리 |
| **단점** | 클래스 수 증가, 간단한 작업에 과도한 설계 |

### 3.1 기본 구현 — 텍스트 에디터

```typescript
// 커맨드 인터페이스
interface Command {
  execute(): void;
  undo(): void;
}

// 수신자 (Receiver)
class TextEditor {
  #content = "";

  get content(): string {
    return this.#content;
  }

  insertAt(position: number, text: string): void {
    this.#content =
      this.#content.slice(0, position) + text + this.#content.slice(position);
  }

  deleteRange(start: number, length: number): string {
    const deleted = this.#content.slice(start, start + length);
    this.#content =
      this.#content.slice(0, start) + this.#content.slice(start + length);
    return deleted;
  }
}

// 구체적 커맨드 — 텍스트 삽입
class InsertTextCommand implements Command {
  constructor(
    private editor: TextEditor,
    private position: number,
    private text: string,
  ) {}

  execute(): void {
    this.editor.insertAt(this.position, this.text);
  }

  undo(): void {
    this.editor.deleteRange(this.position, this.text.length);
  }
}

// 구체적 커맨드 — 텍스트 삭제
class DeleteTextCommand implements Command {
  #deletedText = "";

  constructor(
    private editor: TextEditor,
    private position: number,
    private length: number,
  ) {}

  execute(): void {
    this.#deletedText = this.editor.deleteRange(this.position, this.length);
  }

  undo(): void {
    this.editor.insertAt(this.position, this.#deletedText);
  }
}

// 호출자 (Invoker) — 커맨드 히스토리 관리
class CommandHistory {
  #history: Command[] = [];
  #undone: Command[] = [];

  execute(command: Command): void {
    command.execute();
    this.#history.push(command);
    this.#undone = []; // 새 명령 실행 시 redo 스택 초기화
  }

  undo(): void {
    const command = this.#history.pop();
    if (command) {
      command.undo();
      this.#undone.push(command);
    }
  }

  redo(): void {
    const command = this.#undone.pop();
    if (command) {
      command.execute();
      this.#history.push(command);
    }
  }
}

// 사용
const editor = new TextEditor();
const history = new CommandHistory();

history.execute(new InsertTextCommand(editor, 0, "Hello"));
console.log(editor.content); // "Hello"

history.execute(new InsertTextCommand(editor, 5, " World"));
console.log(editor.content); // "Hello World"

history.undo();
console.log(editor.content); // "Hello"

history.redo();
console.log(editor.content); // "Hello World"

history.execute(new DeleteTextCommand(editor, 5, 6));
console.log(editor.content); // "Hello"

history.undo();
console.log(editor.content); // "Hello World"
```

### 3.2 CarManager 예제 (원서)

원서에서는 `execute()`를 통해 메서드 이름과 인자를 전달하는 방식으로 커맨드 패턴을 소개한다:

```typescript
// 수신자
class CarManager {
  requestInfo(model: string, id: string): string {
    return `The information for ${model} with ID ${id} is foobar`;
  }

  buyVehicle(model: string, id: string): string {
    return `You have successfully purchased Item ${id}, a ${model}`;
  }

  arrangeViewing(model: string, id: string): string {
    return `You have booked a viewing of ${model} (${id})`;
  }
}

// 타입 안전한 커맨드 실행기
type CarManagerMethod = keyof CarManager;

function executeCarCommand(
  manager: CarManager,
  method: CarManagerMethod,
  ...args: [string, string]
): string {
  return manager[method](...args);
}

const manager = new CarManager();

console.log(executeCarCommand(manager, "buyVehicle", "Ford Escort", "453543"));
// "You have successfully purchased Item 453543, a Ford Escort"

console.log(executeCarCommand(manager, "requestInfo", "Ford Mondeo", "54323"));
// "The information for Ford Mondeo with ID 54323 is foobar"
```

> **핵심 통찰**: 커맨드 패턴의 진정한 가치는 단순한 메서드 간접 호출이 아니라, **실행 취소**, **매크로 명령**, **명령 큐잉** 같은 고급 기능을 가능하게 한다는 것이다. Redux의 액션 객체, React의 `useReducer` 디스패치가 모두 커맨드 패턴의 현대적 구현이다.

---

## 4. 이터레이터 패턴 (Iterator Pattern)

이터레이터(*Iterator*) 패턴은 컬렉션의 내부 구조를 노출하지 않고 요소에 **순차적으로 접근**할 수 있는 방법을 제공한다. 현대 JavaScript에서는 `Symbol.iterator`와 제네레이터 함수를 통해 언어 레벨에서 지원된다.

### 패턴 카드: Iterator

| 항목 | 설명 |
|------|------|
| **의도** | 집합 객체의 내부 표현을 노출하지 않고 순차 접근을 제공한다 |
| **사용 시점** | 다양한 컬렉션 구조를 동일한 방식으로 순회해야 할 때 |
| **미사용 시점** | 단순 배열을 `for...of`로 순회하는 것으로 충분할 때 |
| **장점** | 순회 로직과 컬렉션 분리, 다양한 순회 전략 지원 |
| **단점** | 간단한 컬렉션에는 과도한 설계, 커서 상태 관리 필요 |

### 4.1 내부 이터레이터 vs 외부 이터레이터

| 구분 | 내부 이터레이터 | 외부 이터레이터 |
|------|----------------|----------------|
| **제어 주체** | 이터레이터 자체가 순회 제어 | 소비자가 `next()` 호출로 제어 |
| **예시** | `Array.prototype.forEach()` | `Symbol.iterator` / 제네레이터 |
| **장점** | 사용 간편 | 유연한 제어 (일시 정지, 건너뛰기) |

### 4.2 Symbol.iterator와 제네레이터

```typescript
// 커스텀 이터러블 — 이진 트리 중위 순회
class TreeNode<T> {
  constructor(
    public value: T,
    public left: TreeNode<T> | null = null,
    public right: TreeNode<T> | null = null,
  ) {}
}

class BinaryTree<T> implements Iterable<T> {
  constructor(private root: TreeNode<T> | null = null) {}

  // Symbol.iterator를 구현하면 for...of에서 사용 가능
  *[Symbol.iterator](): Iterator<T> {
    yield* this.#inOrder(this.root);
  }

  // 제네레이터 함수 — 중위 순회
  *#inOrder(node: TreeNode<T> | null): Generator<T> {
    if (node === null) return;
    yield* this.#inOrder(node.left);
    yield node.value;
    yield* this.#inOrder(node.right);
  }

  // 다른 순회 전략도 제공 가능
  *preOrder(): Generator<T> {
    yield* this.#preOrder(this.root);
  }

  *#preOrder(node: TreeNode<T> | null): Generator<T> {
    if (node === null) return;
    yield node.value;
    yield* this.#preOrder(node.left);
    yield* this.#preOrder(node.right);
  }
}

// 사용
const tree = new BinaryTree(
  new TreeNode(4,
    new TreeNode(2, new TreeNode(1), new TreeNode(3)),
    new TreeNode(6, new TreeNode(5), new TreeNode(7)),
  ),
);

// for...of — 기본은 중위 순회
for (const value of tree) {
  process.stdout.write(`${value} `);
}
// 1 2 3 4 5 6 7

// 전위 순회
console.log([...tree.preOrder()]); // [4, 2, 1, 3, 6, 5, 7]

// 구조 분해 할당
const [first, second, third] = tree;
console.log(first, second, third); // 1 2 3
```

### 4.3 비동기 이터레이터 (AsyncIterator)

```typescript
// 페이지네이션된 API를 비동기 이터레이터로 추상화
async function* fetchPages<T>(
  url: string,
  pageSize: number,
): AsyncGenerator<T[]> {
  let page = 1;
  let hasMore = true;

  while (hasMore) {
    const response = await fetch(`${url}?page=${page}&size=${pageSize}`);
    const data: { items: T[]; totalPages: number } = await response.json();

    yield data.items;

    hasMore = page < data.totalPages;
    page++;
  }
}

// for-await-of로 소비
async function processAllUsers(): Promise<void> {
  for await (const users of fetchPages<User>("/api/users", 50)) {
    for (const user of users) {
      console.log(user.name);
    }
  }
}
```

### JavaScript vs TypeScript

```javascript
// JavaScript — 이터레이터 프로토콜은 동일하지만 타입 안전성 없음
class BinaryTree {
  *[Symbol.iterator]() {
    yield* this.#inOrder(this.root);
  }
  // yield되는 값의 타입을 알 수 없음
}
```

```typescript
// TypeScript — Iterable<T>, Iterator<T>, AsyncGenerator<T>로 타입 안전한 순회
class BinaryTree<T> implements Iterable<T> {
  *[Symbol.iterator](): Iterator<T> { /* ... */ }
  //                     ^? 소비자가 T 타입의 값을 받음을 보장
}
```

> **핵심 통찰**: 현대 JavaScript에서 이터레이터 패턴은 언어 내장 기능이다. `Symbol.iterator`를 구현하면 `for...of`, 스프레드 연산자, 구조 분해 할당 등 모든 반복 문법에서 사용할 수 있다. 제네레이터는 게으른 평가(*Lazy Evaluation*)를 가능하게 하여 무한 시퀀스도 표현할 수 있다.

---

## 5. 전략 패턴 (Strategy Pattern)

전략(*Strategy*) 패턴은 **알고리즘 가족을 정의**하고, 각각을 캡슐화하여 **교체 가능**하게 만든다. 클라이언트 코드의 변경 없이 런타임에 알고리즘을 바꿀 수 있다.

### 패턴 카드: Strategy

| 항목 | 설명 |
|------|------|
| **의도** | 알고리즘을 캡슐화하여 교체 가능하게 만들고, 클라이언트로부터 독립시킨다 |
| **사용 시점** | 동일한 문제에 대해 여러 해결 방법이 있고, 런타임에 선택해야 할 때 |
| **미사용 시점** | 알고리즘이 하나뿐이거나 변경될 가능성이 없을 때 |
| **장점** | 개방-폐쇄 원칙(OCP) 준수, 조건문 제거, 알고리즘 교체 용이 |
| **단점** | 클라이언트가 전략 간 차이를 알아야 함, 전략 객체 수 증가 |

### 5.1 유효성 검사 전략

```typescript
// 전략 인터페이스
interface ValidationStrategy {
  validate(value: string): ValidationResult;
}

interface ValidationResult {
  isValid: boolean;
  error?: string;
}

// 구체적 전략들
class RequiredStrategy implements ValidationStrategy {
  validate(value: string): ValidationResult {
    return value.trim().length > 0
      ? { isValid: true }
      : { isValid: false, error: "필수 입력 항목입니다" };
  }
}

class EmailStrategy implements ValidationStrategy {
  validate(value: string): ValidationResult {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(value)
      ? { isValid: true }
      : { isValid: false, error: "올바른 이메일 형식이 아닙니다" };
  }
}

class MinLengthStrategy implements ValidationStrategy {
  constructor(private minLength: number) {}

  validate(value: string): ValidationResult {
    return value.length >= this.minLength
      ? { isValid: true }
      : { isValid: false, error: `최소 ${this.minLength}자 이상이어야 합니다` };
  }
}

class PasswordStrengthStrategy implements ValidationStrategy {
  validate(value: string): ValidationResult {
    const hasUpperCase = /[A-Z]/.test(value);
    const hasLowerCase = /[a-z]/.test(value);
    const hasNumbers = /\d/.test(value);
    const hasSpecial = /[!@#$%^&*]/.test(value);

    const strength = [hasUpperCase, hasLowerCase, hasNumbers, hasSpecial]
      .filter(Boolean).length;

    if (strength < 3) {
      return {
        isValid: false,
        error: "대소문자, 숫자, 특수문자 중 3가지 이상 포함해야 합니다",
      };
    }
    return { isValid: true };
  }
}

// 컨텍스트 — 전략을 조합하여 사용
class FormValidator {
  #rules = new Map<string, ValidationStrategy[]>();

  addRule(field: string, ...strategies: ValidationStrategy[]): this {
    const existing = this.#rules.get(field) ?? [];
    this.#rules.set(field, [...existing, ...strategies]);
    return this;
  }

  validate(data: Record<string, string>): Map<string, string[]> {
    const errors = new Map<string, string[]>();

    for (const [field, strategies] of this.#rules) {
      const value = data[field] ?? "";
      const fieldErrors: string[] = [];

      for (const strategy of strategies) {
        const result = strategy.validate(value);
        if (!result.isValid && result.error) {
          fieldErrors.push(result.error);
        }
      }

      if (fieldErrors.length > 0) {
        errors.set(field, fieldErrors);
      }
    }

    return errors;
  }
}

// 사용
const validator = new FormValidator()
  .addRule("email", new RequiredStrategy(), new EmailStrategy())
  .addRule(
    "password",
    new RequiredStrategy(),
    new MinLengthStrategy(8),
    new PasswordStrengthStrategy(),
  );

const errors = validator.validate({
  email: "invalid-email",
  password: "weak",
});

console.log(errors.get("email"));
// ["올바른 이메일 형식이 아닙니다"]

console.log(errors.get("password"));
// ["최소 8자 이상이어야 합니다", "대소문자, 숫자, 특수문자 중 3가지 이상 포함해야 합니다"]
```

### 5.2 함수형 전략 — TypeScript에서의 간결한 대안

TypeScript에서는 인터페이스 + 클래스 대신 **함수 타입**으로 전략을 더 간결하게 표현할 수 있다:

```typescript
// 전략을 함수 타입으로 정의
type SortStrategy<T> = (a: T, b: T) => number;

// 전략들
const byName: SortStrategy<User> = (a, b) => a.name.localeCompare(b.name);
const byAge: SortStrategy<User> = (a, b) => a.age - b.age;
const byRegistration: SortStrategy<User> = (a, b) =>
  a.registeredAt.getTime() - b.registeredAt.getTime();

interface User {
  name: string;
  age: number;
  registeredAt: Date;
}

// 컨텍스트
class UserList {
  #users: User[] = [];
  #sortStrategy: SortStrategy<User> = byName; // 기본 전략

  add(user: User): void {
    this.#users.push(user);
  }

  setSortStrategy(strategy: SortStrategy<User>): void {
    this.#sortStrategy = strategy;
  }

  getSorted(): User[] {
    return [...this.#users].sort(this.#sortStrategy);
  }
}

const list = new UserList();
list.add({ name: "Charlie", age: 30, registeredAt: new Date("2024-01-15") });
list.add({ name: "Alice", age: 25, registeredAt: new Date("2025-06-01") });
list.add({ name: "Bob", age: 35, registeredAt: new Date("2023-11-20") });

list.setSortStrategy(byAge);
console.log(list.getSorted().map((u) => u.name));
// ["Alice", "Charlie", "Bob"]

list.setSortStrategy(byRegistration);
console.log(list.getSorted().map((u) => u.name));
// ["Bob", "Charlie", "Alice"]
```

> **핵심 통찰**: JavaScript/TypeScript에서 전략 패턴은 "함수를 일급 객체로 전달하는 것"과 본질적으로 동일하다. 클래스 기반 전략은 상태를 가진 복잡한 알고리즘에, 함수 기반 전략은 상태가 없는 단순 로직에 적합하다. React에서 Hook을 교체하여 동작을 바꾸는 것도 전략 패턴의 변형이다.

---

## 6. 상태 패턴 (State Pattern)

상태(*State*) 패턴은 **내부 상태에 따라 객체의 행동을 변경**한다. 외부에서 보면 마치 클래스 자체가 바뀐 것처럼 보인다. 복잡한 `if-else`/`switch` 조건문을 상태 객체로 대체하여 코드를 깔끔하게 만든다.

### 패턴 카드: State

| 항목 | 설명 |
|------|------|
| **의도** | 객체의 내부 상태에 따라 행동을 변경하며, 상태별 로직을 개별 객체로 캡슐화한다 |
| **사용 시점** | 객체가 여러 상태를 가지고, 상태마다 다른 행동을 해야 할 때 |
| **미사용 시점** | 상태가 2~3개뿐이고 전환 로직이 단순한 경우 |
| **장점** | 조건문 제거, 상태별 로직 격리, 새 상태 추가 용이 (OCP 준수) |
| **단점** | 상태 클래스 수 증가, 상태 전환 로직이 분산될 수 있음 |

### 6.1 주문 상태 머신

```typescript
// 상태 인터페이스
interface OrderState {
  readonly name: string;
  confirm(order: Order): void;
  ship(order: Order): void;
  deliver(order: Order): void;
  cancel(order: Order): void;
}

// 구체적 상태 — 대기
class PendingState implements OrderState {
  readonly name = "Pending";

  confirm(order: Order): void {
    console.log("주문이 확인되었습니다.");
    order.setState(new ConfirmedState());
  }

  ship(_order: Order): void {
    console.log("오류: 확인되지 않은 주문은 배송할 수 없습니다.");
  }

  deliver(_order: Order): void {
    console.log("오류: 확인되지 않은 주문은 배달할 수 없습니다.");
  }

  cancel(order: Order): void {
    console.log("주문이 취소되었습니다.");
    order.setState(new CancelledState());
  }
}

// 구체적 상태 — 확인됨
class ConfirmedState implements OrderState {
  readonly name = "Confirmed";

  confirm(_order: Order): void {
    console.log("이미 확인된 주문입니다.");
  }

  ship(order: Order): void {
    console.log("주문이 배송 처리되었습니다.");
    order.setState(new ShippedState());
  }

  deliver(_order: Order): void {
    console.log("오류: 배송 전에 배달할 수 없습니다.");
  }

  cancel(order: Order): void {
    console.log("확인된 주문이 취소되었습니다.");
    order.setState(new CancelledState());
  }
}

// 구체적 상태 — 배송됨
class ShippedState implements OrderState {
  readonly name = "Shipped";

  confirm(_order: Order): void {
    console.log("이미 배송된 주문입니다.");
  }

  ship(_order: Order): void {
    console.log("이미 배송 중입니다.");
  }

  deliver(order: Order): void {
    console.log("주문이 배달 완료되었습니다.");
    order.setState(new DeliveredState());
  }

  cancel(_order: Order): void {
    console.log("오류: 배송 중인 주문은 취소할 수 없습니다.");
  }
}

// 구체적 상태 — 배달 완료
class DeliveredState implements OrderState {
  readonly name = "Delivered";

  confirm(_order: Order): void {
    console.log("이미 배달 완료된 주문입니다.");
  }

  ship(_order: Order): void {
    console.log("이미 배달 완료된 주문입니다.");
  }

  deliver(_order: Order): void {
    console.log("이미 배달 완료된 주문입니다.");
  }

  cancel(_order: Order): void {
    console.log("오류: 배달 완료된 주문은 취소할 수 없습니다.");
  }
}

// 구체적 상태 — 취소됨
class CancelledState implements OrderState {
  readonly name = "Cancelled";

  confirm(_order: Order): void {
    console.log("오류: 취소된 주문은 확인할 수 없습니다.");
  }

  ship(_order: Order): void {
    console.log("오류: 취소된 주문은 배송할 수 없습니다.");
  }

  deliver(_order: Order): void {
    console.log("오류: 취소된 주문은 배달할 수 없습니다.");
  }

  cancel(_order: Order): void {
    console.log("이미 취소된 주문입니다.");
  }
}

// 컨텍스트
class Order {
  #state: OrderState;

  constructor(public readonly orderId: string) {
    this.#state = new PendingState();
  }

  setState(state: OrderState): void {
    console.log(`  [${this.orderId}] ${this.#state.name} → ${state.name}`);
    this.#state = state;
  }

  get stateName(): string {
    return this.#state.name;
  }

  confirm(): void { this.#state.confirm(this); }
  ship(): void { this.#state.ship(this); }
  deliver(): void { this.#state.deliver(this); }
  cancel(): void { this.#state.cancel(this); }
}

// 사용
const order = new Order("ORD-001");

order.confirm();
// 주문이 확인되었습니다.
//   [ORD-001] Pending → Confirmed

order.ship();
// 주문이 배송 처리되었습니다.
//   [ORD-001] Confirmed → Shipped

order.cancel();
// 오류: 배송 중인 주문은 취소할 수 없습니다.

order.deliver();
// 주문이 배달 완료되었습니다.
//   [ORD-001] Shipped → Delivered
```

### 6.2 신호등 예제 — 상태 전환의 순환

```typescript
interface TrafficLightState {
  readonly color: string;
  readonly duration: number; // milliseconds
  next(): TrafficLightState;
}

class GreenState implements TrafficLightState {
  readonly color = "Green";
  readonly duration = 30_000;
  next(): TrafficLightState { return new YellowState(); }
}

class YellowState implements TrafficLightState {
  readonly color = "Yellow";
  readonly duration = 5_000;
  next(): TrafficLightState { return new RedState(); }
}

class RedState implements TrafficLightState {
  readonly color = "Red";
  readonly duration = 20_000;
  next(): TrafficLightState { return new GreenState(); }
}

class TrafficLight {
  #state: TrafficLightState = new RedState();

  get color(): string { return this.#state.color; }

  async run(cycles: number): Promise<void> {
    for (let i = 0; i < cycles * 3; i++) {
      console.log(`🚦 ${this.#state.color} (${this.#state.duration / 1000}s)`);
      await new Promise((r) => setTimeout(r, this.#state.duration));
      this.#state = this.#state.next();
    }
  }
}
```

> **핵심 통찰**: 상태 패턴은 `switch (state)` 문을 다형성으로 대체한다. 새로운 상태를 추가할 때 기존 코드를 수정하지 않고 새 클래스만 만들면 된다. 상태 전환이 복잡해지면 XState 같은 상태 머신 라이브러리를 사용하는 것이 더 효율적이다.

---

## 7. 템플릿 메서드 패턴 (Template Method Pattern)

템플릿 메서드(*Template Method*) 패턴은 **알고리즘의 골격을 기본 클래스에 정의**하고, 일부 단계의 구현을 하위 클래스에 위임한다. 알고리즘의 전체 구조는 변경하지 않으면서 특정 단계만 재정의할 수 있다.

### 패턴 카드: Template Method

| 항목 | 설명 |
|------|------|
| **의도** | 알고리즘의 뼈대를 정의하고, 일부 단계를 하위 클래스가 재정의하게 한다 |
| **사용 시점** | 알고리즘의 전체 구조는 동일하되 세부 단계만 다를 때 |
| **미사용 시점** | 알고리즘의 구조 자체가 매번 다른 경우 (→ 전략 패턴 고려) |
| **장점** | 코드 중복 제거, 알고리즘 구조 보장, 확장 포인트 명확 |
| **단점** | 상속 의존, 상위 클래스 변경 시 하위 클래스에 영향 |

### 7.1 데이터 처리 파이프라인

```typescript
// 기본 클래스 — 알고리즘 골격 정의
abstract class DataProcessor<TRaw, TParsed, TResult> {
  // 템플릿 메서드 — 전체 흐름을 정의 (final 역할)
  process(source: string): TResult {
    console.log(`Processing: ${source}`);
    const raw = this.fetch(source);
    const parsed = this.parse(raw);
    const validated = this.validate(parsed);
    const result = this.transform(validated);
    this.save(result);
    return result;
  }

  // 추상 메서드 — 하위 클래스가 반드시 구현
  protected abstract fetch(source: string): TRaw;
  protected abstract parse(raw: TRaw): TParsed;
  protected abstract transform(data: TParsed): TResult;

  // 훅 메서드 — 기본 구현이 있지만 재정의 가능
  protected validate(data: TParsed): TParsed {
    return data; // 기본: 검증 없이 통과
  }

  protected save(_result: TResult): void {
    // 기본: 저장하지 않음. 필요 시 재정의
  }
}

// 구체적 구현 — CSV 처리
interface CsvRow {
  [key: string]: string;
}

class CsvProcessor extends DataProcessor<string, CsvRow[], CsvRow[]> {
  protected fetch(source: string): string {
    // 실제로는 파일 읽기
    return "name,age,email\nAlice,25,alice@example.com\nBob,30,bob@example.com";
  }

  protected parse(raw: string): CsvRow[] {
    const [headerLine, ...lines] = raw.split("\n");
    const headers = headerLine.split(",");
    return lines.map((line) => {
      const values = line.split(",");
      return Object.fromEntries(headers.map((h, i) => [h, values[i]]));
    });
  }

  protected validate(data: CsvRow[]): CsvRow[] {
    return data.filter((row) => row.email?.includes("@"));
  }

  protected transform(data: CsvRow[]): CsvRow[] {
    return data.map((row) => ({
      ...row,
      name: row.name.toUpperCase(),
    }));
  }

  protected save(result: CsvRow[]): void {
    console.log(`Saved ${result.length} rows to database`);
  }
}

// 구체적 구현 — JSON API 처리
interface ApiResponse {
  data: UserData[];
  total: number;
}

interface UserData {
  id: number;
  name: string;
  active: boolean;
}

class ApiProcessor extends DataProcessor<string, UserData[], UserData[]> {
  protected fetch(source: string): string {
    // 실제로는 API 호출
    return JSON.stringify({
      data: [
        { id: 1, name: "Alice", active: true },
        { id: 2, name: "Bob", active: false },
      ],
      total: 2,
    });
  }

  protected parse(raw: string): UserData[] {
    const response: ApiResponse = JSON.parse(raw);
    return response.data;
  }

  protected transform(data: UserData[]): UserData[] {
    return data.filter((user) => user.active);
  }
}

// 사용
const csvProcessor = new CsvProcessor();
const result = csvProcessor.process("data.csv");
// Processing: data.csv
// Saved 2 rows to database

const apiProcessor = new ApiProcessor();
const activeUsers = apiProcessor.process("/api/users");
// Processing: /api/users
```

### 7.2 템플릿 메서드 vs 전략

| 비교 | 템플릿 메서드 | 전략 |
|------|-------------|------|
| **메커니즘** | 상속 (is-a) | 조합 (has-a) |
| **변경 시점** | 컴파일 타임 | 런타임 |
| **변경 범위** | 알고리즘 일부 단계 | 전체 알고리즘 |
| **TypeScript 적합성** | 추상 클래스로 구현 | 함수 타입 / 인터페이스로 구현 |

> **핵심 통찰**: 템플릿 메서드 패턴은 "알고리즘의 구조를 고정하고 세부만 변경"할 때 유용하다. 하지만 TypeScript/JavaScript에서는 상속보다 조합(*Composition*)이 선호되므로, 전략 패턴이나 함수 파이프라인이 더 자주 사용된다. 템플릿 메서드는 프레임워크 설계에서 여전히 강력한 도구다.

---

## 8. 책임 연쇄 패턴 (Chain of Responsibility Pattern)

책임 연쇄(*Chain of Responsibility*) 패턴은 요청을 **처리자 체인을 따라 전달**하는 패턴이다. 각 처리자는 요청을 처리하거나, 처리할 수 없으면 다음 처리자에게 넘긴다. Express.js/Koa의 미들웨어가 이 패턴의 대표적인 현실 사례다.

### 패턴 카드: Chain of Responsibility

| 항목 | 설명 |
|------|------|
| **의도** | 요청의 발신자와 수신자를 분리하고, 여러 처리자에게 기회를 준다 |
| **사용 시점** | 요청을 처리할 객체를 미리 알 수 없거나, 여러 단계의 처리가 필요할 때 |
| **미사용 시점** | 요청 처리자가 항상 하나로 확정될 때 |
| **장점** | 처리자 추가/제거가 용이, 호출자와 처리자 분리, 단일 책임 원칙 |
| **단점** | 요청이 처리되지 않을 수 있음, 체인이 길면 성능 문제, 디버깅 어려움 |

### 8.1 미들웨어 체인 구현

```typescript
// 미들웨어 타입 — Express.js 스타일
interface Context {
  path: string;
  method: string;
  headers: Record<string, string>;
  body?: unknown;
  user?: { id: string; role: string };
  response?: { status: number; body: unknown };
}

type Middleware = (ctx: Context, next: () => Promise<void>) => Promise<void>;

// 미들웨어 체인 실행기
class MiddlewareChain {
  #middlewares: Middleware[] = [];

  use(middleware: Middleware): this {
    this.#middlewares.push(middleware);
    return this;
  }

  async execute(ctx: Context): Promise<Context> {
    let index = 0;

    const next = async (): Promise<void> => {
      if (index < this.#middlewares.length) {
        const middleware = this.#middlewares[index++];
        await middleware(ctx, next);
      }
    };

    await next();
    return ctx;
  }
}

// 구체적 미들웨어들
const logger: Middleware = async (ctx, next) => {
  const start = Date.now();
  console.log(`→ ${ctx.method} ${ctx.path}`);
  await next();
  console.log(`← ${ctx.method} ${ctx.path} (${Date.now() - start}ms)`);
};

const auth: Middleware = async (ctx, next) => {
  const token = ctx.headers["authorization"];
  if (!token) {
    ctx.response = { status: 401, body: { error: "Unauthorized" } };
    return; // next()를 호출하지 않아 체인 중단
  }
  ctx.user = { id: "u123", role: "admin" }; // 토큰 검증 후 사용자 설정
  await next();
};

const roleGuard = (requiredRole: string): Middleware => {
  return async (ctx, next) => {
    if (ctx.user?.role !== requiredRole) {
      ctx.response = { status: 403, body: { error: "Forbidden" } };
      return;
    }
    await next();
  };
};

const handler: Middleware = async (ctx, _next) => {
  ctx.response = { status: 200, body: { message: "Success", user: ctx.user } };
};

// 사용 — 체인 구성
const app = new MiddlewareChain()
  .use(logger)
  .use(auth)
  .use(roleGuard("admin"))
  .use(handler);

// 인증 없는 요청 — 체인이 auth에서 중단
await app.execute({
  path: "/admin",
  method: "GET",
  headers: {},
});
// → GET /admin
// ← GET /admin (1ms)
// response: { status: 401, body: { error: "Unauthorized" } }

// 인증된 요청 — 체인이 끝까지 실행
await app.execute({
  path: "/admin",
  method: "GET",
  headers: { authorization: "Bearer token123" },
});
// → GET /admin
// ← GET /admin (2ms)
// response: { status: 200, body: { message: "Success", user: { id: "u123", role: "admin" } } }
```

### 8.2 클래스 기반 책임 연쇄

```typescript
// 추상 핸들러
abstract class SupportHandler {
  #next: SupportHandler | null = null;

  setNext(handler: SupportHandler): SupportHandler {
    this.#next = handler;
    return handler; // 체이닝 지원
  }

  handle(ticket: SupportTicket): string {
    if (this.canHandle(ticket)) {
      return this.process(ticket);
    }
    if (this.#next) {
      return this.#next.handle(ticket);
    }
    return `티켓 #${ticket.id}를 처리할 수 있는 핸들러가 없습니다.`;
  }

  protected abstract canHandle(ticket: SupportTicket): boolean;
  protected abstract process(ticket: SupportTicket): string;
}

interface SupportTicket {
  id: number;
  severity: "low" | "medium" | "high" | "critical";
  message: string;
}

class BotHandler extends SupportHandler {
  protected canHandle(ticket: SupportTicket): boolean {
    return ticket.severity === "low";
  }
  protected process(ticket: SupportTicket): string {
    return `[Bot] 티켓 #${ticket.id} 자동 응답 처리 완료`;
  }
}

class JuniorHandler extends SupportHandler {
  protected canHandle(ticket: SupportTicket): boolean {
    return ticket.severity === "medium";
  }
  protected process(ticket: SupportTicket): string {
    return `[Junior] 티켓 #${ticket.id} 담당자 배정`;
  }
}

class SeniorHandler extends SupportHandler {
  protected canHandle(ticket: SupportTicket): boolean {
    return ticket.severity === "high" || ticket.severity === "critical";
  }
  protected process(ticket: SupportTicket): string {
    return `[Senior] 티켓 #${ticket.id} 긴급 처리`;
  }
}

// 체인 구성
const bot = new BotHandler();
const junior = new JuniorHandler();
const senior = new SeniorHandler();

bot.setNext(junior).setNext(senior);

console.log(bot.handle({ id: 1, severity: "low", message: "FAQ 질문" }));
// [Bot] 티켓 #1 자동 응답 처리 완료

console.log(bot.handle({ id: 2, severity: "critical", message: "시스템 장애" }));
// [Senior] 티켓 #2 긴급 처리
```

> **핵심 통찰**: Express.js/Koa의 미들웨어 시스템, Next.js의 미들웨어, Nest.js의 가드/인터셉터 모두 책임 연쇄 패턴의 구현이다. `next()` 호출 여부로 체인의 진행/중단을 제어한다는 점이 핵심이다.

---

## 9. 방문자 패턴 (Visitor Pattern)

방문자(*Visitor*) 패턴은 **클래스의 변경 없이 새로운 연산을 추가**할 수 있게 한다. 객체 구조와 연산을 분리하여, 새로운 연산이 필요할 때 기존 클래스를 수정하지 않고 방문자 클래스만 추가하면 된다.

### 패턴 카드: Visitor

| 항목 | 설명 |
|------|------|
| **의도** | 객체 구조의 요소에 수행할 연산을 분리하여, 요소 변경 없이 새 연산을 추가한다 |
| **사용 시점** | 다양한 타입의 요소에 대해 여러 독립적인 연산을 수행해야 할 때 |
| **미사용 시점** | 요소 클래스 구조가 자주 변경되는 경우 (→ 모든 방문자를 수정해야 함) |
| **장점** | 새 연산 추가 용이, 관련 동작을 하나의 방문자에 모음, 단일 책임 원칙 |
| **단점** | 새 요소 타입 추가 시 모든 방문자 수정 필요, 캡슐화 위반 가능성 |

### 9.1 AST 방문자 — 컴파일러/린터 패턴

```typescript
// 요소 인터페이스 — accept 메서드 정의
interface ASTNode {
  accept<T>(visitor: ASTVisitor<T>): T;
}

// 구체적 요소들
class NumberLiteral implements ASTNode {
  constructor(public readonly value: number) {}
  accept<T>(visitor: ASTVisitor<T>): T {
    return visitor.visitNumber(this);
  }
}

class BinaryExpression implements ASTNode {
  constructor(
    public readonly left: ASTNode,
    public readonly operator: "+" | "-" | "*" | "/",
    public readonly right: ASTNode,
  ) {}
  accept<T>(visitor: ASTVisitor<T>): T {
    return visitor.visitBinary(this);
  }
}

class UnaryExpression implements ASTNode {
  constructor(
    public readonly operator: "-" | "!",
    public readonly operand: ASTNode,
  ) {}
  accept<T>(visitor: ASTVisitor<T>): T {
    return visitor.visitUnary(this);
  }
}

// 방문자 인터페이스
interface ASTVisitor<T> {
  visitNumber(node: NumberLiteral): T;
  visitBinary(node: BinaryExpression): T;
  visitUnary(node: UnaryExpression): T;
}

// 구체적 방문자 — 수식 평가
class Evaluator implements ASTVisitor<number> {
  visitNumber(node: NumberLiteral): number {
    return node.value;
  }

  visitBinary(node: BinaryExpression): number {
    const left = node.left.accept(this);
    const right = node.right.accept(this);
    switch (node.operator) {
      case "+": return left + right;
      case "-": return left - right;
      case "*": return left * right;
      case "/": return left / right;
    }
  }

  visitUnary(node: UnaryExpression): number {
    const operand = node.operand.accept(this);
    switch (node.operator) {
      case "-": return -operand;
      case "!": return operand === 0 ? 1 : 0;
    }
  }
}

// 구체적 방문자 — 수식을 문자열로 변환
class Printer implements ASTVisitor<string> {
  visitNumber(node: NumberLiteral): string {
    return String(node.value);
  }

  visitBinary(node: BinaryExpression): string {
    const left = node.left.accept(this);
    const right = node.right.accept(this);
    return `(${left} ${node.operator} ${right})`;
  }

  visitUnary(node: UnaryExpression): string {
    const operand = node.operand.accept(this);
    return `(${node.operator}${operand})`;
  }
}

// 구체적 방문자 — 노드 수 카운팅
class NodeCounter implements ASTVisitor<number> {
  visitNumber(_node: NumberLiteral): number {
    return 1;
  }

  visitBinary(node: BinaryExpression): number {
    return 1 + node.left.accept(this) + node.right.accept(this);
  }

  visitUnary(node: UnaryExpression): number {
    return 1 + node.operand.accept(this);
  }
}

// 사용 — (3 + 4) * (-2) 를 표현
const ast: ASTNode = new BinaryExpression(
  new BinaryExpression(
    new NumberLiteral(3),
    "+",
    new NumberLiteral(4),
  ),
  "*",
  new UnaryExpression("-", new NumberLiteral(2)),
);

const evaluator = new Evaluator();
const printer = new Printer();
const counter = new NodeCounter();

console.log(ast.accept(printer));    // "((3 + 4) * (-2))"
console.log(ast.accept(evaluator));  // -14
console.log(ast.accept(counter));    // 5
```

새로운 연산(예: 최적화, 코드 생성)을 추가할 때 기존 노드 클래스는 전혀 수정할 필요가 없다. `ASTVisitor<T>`를 구현하는 새 클래스만 만들면 된다.

### 9.2 파일 시스템 예제 — 더 실용적인 시나리오

```typescript
interface FileSystemEntry {
  name: string;
  accept<T>(visitor: FileSystemVisitor<T>): T;
}

class File implements FileSystemEntry {
  constructor(
    public readonly name: string,
    public readonly size: number,
    public readonly extension: string,
  ) {}

  accept<T>(visitor: FileSystemVisitor<T>): T {
    return visitor.visitFile(this);
  }
}

class Directory implements FileSystemEntry {
  public readonly children: FileSystemEntry[] = [];

  constructor(public readonly name: string) {}

  add(entry: FileSystemEntry): this {
    this.children.push(entry);
    return this;
  }

  accept<T>(visitor: FileSystemVisitor<T>): T {
    return visitor.visitDirectory(this);
  }
}

interface FileSystemVisitor<T> {
  visitFile(file: File): T;
  visitDirectory(dir: Directory): T;
}

// 총 크기 계산 방문자
class SizeCalculator implements FileSystemVisitor<number> {
  visitFile(file: File): number {
    return file.size;
  }
  visitDirectory(dir: Directory): number {
    return dir.children.reduce((sum, child) => sum + child.accept(this), 0);
  }
}

// 특정 확장자 검색 방문자
class ExtensionFinder implements FileSystemVisitor<File[]> {
  constructor(private ext: string) {}

  visitFile(file: File): File[] {
    return file.extension === this.ext ? [file] : [];
  }
  visitDirectory(dir: Directory): File[] {
    return dir.children.flatMap((child) => child.accept(this));
  }
}

// 사용
const root = new Directory("src")
  .add(new File("index.ts", 1024, "ts"))
  .add(new File("style.css", 512, "css"))
  .add(
    new Directory("utils")
      .add(new File("helpers.ts", 2048, "ts"))
      .add(new File("constants.ts", 256, "ts")),
  );

console.log(root.accept(new SizeCalculator()));     // 3840
console.log(root.accept(new ExtensionFinder("ts"))); // [index.ts, helpers.ts, constants.ts]
```

> **핵심 통찰**: 방문자 패턴은 "요소 구조는 안정적이지만 연산은 자주 추가되는" 상황에서 위력을 발휘한다. TypeScript의 ESLint, Babel 플러그인, Prettier 등 AST 기반 도구들이 모두 방문자 패턴을 기반으로 한다.

---

## 최신 업데이트 (2026)

### Observer → Signals 제안 (TC39)

TC39 Signals 제안(*Stage 1*)은 관찰자 패턴을 언어 레벨에서 지원하려는 움직임이다. React의 `useState`, Solid의 `createSignal`, Angular의 `signal()`이 모두 이 방향을 가리킨다:

```typescript
// TC39 Signals 제안 (미확정 — 2026년 기준 Stage 1)
// 아래는 개념적 사용 예시
import { Signal, Computed, Effect } from "std:signals";

const count = new Signal(0);
const doubled = new Computed(() => count.get() * 2);

const dispose = new Effect(() => {
  console.log(`Count: ${count.get()}, Doubled: ${doubled.get()}`);
});

count.set(5);
// Count: 5, Doubled: 10
```

현재 사용 가능한 실무 대안:

| 라이브러리 | 관찰자 패턴 구현 방식 |
|-----------|---------------------|
| **RxJS** | Observable/Observer + 연산자 파이프라인 |
| **Zustand** | `subscribe()` 메서드 — 선택적 상태 구독 |
| **Jotai** | 원자(*Atom*) 단위 구독 — 세밀한 리렌더링 |
| **SolidJS Signals** | 자동 의존성 추적 — 가장 Signals 제안에 가까움 |

### Iterator → 내장 프로토콜과 비동기 확장

```typescript
// Iterator helpers 제안 (Stage 3 → 2026년 대부분의 엔진에서 지원)
const result = Iterator.from([1, 2, 3, 4, 5])
  .filter((n) => n % 2 === 0)
  .map((n) => n * 10)
  .toArray();
// [20, 40]

// for-await-of — 비동기 이터레이터
for await (const chunk of readableStream) {
  process(chunk);
}
```

### Mediator → 이벤트 버스 vs React Context vs Zustand

| 중재자 역할 | 구현 방식 | 장점 | 단점 |
|------------|----------|------|------|
| **EventBus** | 커스텀 Pub/Sub 클래스 | 프레임워크 무관 | 타입 안전성 부족 가능 |
| **React Context** | `createContext` + `Provider` | React 내장 | 전역 리렌더링 문제 |
| **Zustand** | 중앙 스토어 + 선택적 구독 | 세밀한 리렌더링 | React 의존 |

### Command → Redux 액션과 useReducer

```typescript
// Redux Toolkit — 커맨드 패턴의 현대적 구현
import { createSlice, PayloadAction } from "@reduxjs/toolkit";

// 액션 = 커맨드 객체
const counterSlice = createSlice({
  name: "counter",
  initialState: { value: 0 },
  reducers: {
    increment(state) { state.value += 1; },
    decrement(state) { state.value -= 1; },
    incrementByAmount(state, action: PayloadAction<number>) {
      state.value += action.payload;
    },
  },
});

// useReducer — 로컬 상태에서의 커맨드 패턴
type Action =
  | { type: "increment" }
  | { type: "decrement" }
  | { type: "reset"; payload: number };

function reducer(state: number, action: Action): number {
  switch (action.type) {
    case "increment": return state + 1;
    case "decrement": return state - 1;
    case "reset": return action.payload;
  }
}
```

### Strategy → React Hook 조합

```typescript
// React Hook으로 전략 패턴 구현
function useSearchStrategy(strategy: "local" | "api") {
  const localSearch = useLocalSearch();
  const apiSearch = useApiSearch();

  return strategy === "local" ? localSearch : apiSearch;
}

// 사용 — 전략 교체가 Hook 교체로 자연스럽게 이루어짐
function SearchComponent({ mode }: { mode: "local" | "api" }) {
  const { search, results } = useSearchStrategy(mode);
  // ...
}
```

### State → XState와 useReducer 상태 머신

```typescript
// XState v5 — 선언적 상태 머신
import { createMachine, createActor } from "xstate";

const orderMachine = createMachine({
  id: "order",
  initial: "pending",
  states: {
    pending: {
      on: {
        CONFIRM: "confirmed",
        CANCEL: "cancelled",
      },
    },
    confirmed: {
      on: {
        SHIP: "shipped",
        CANCEL: "cancelled",
      },
    },
    shipped: {
      on: { DELIVER: "delivered" },
    },
    delivered: { type: "final" },
    cancelled: { type: "final" },
  },
});

const actor = createActor(orderMachine).start();
actor.send({ type: "CONFIRM" });
actor.send({ type: "SHIP" });
console.log(actor.getSnapshot().value); // "shipped"
```

### Chain of Responsibility → Next.js 미들웨어

```typescript
// next.js middleware.ts — 책임 연쇄 패턴의 실제 적용
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  // 1단계: 인증 체크
  const token = request.cookies.get("session");
  if (!token && request.nextUrl.pathname.startsWith("/dashboard")) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  // 2단계: 리다이렉트 규칙
  if (request.nextUrl.pathname === "/old-page") {
    return NextResponse.redirect(new URL("/new-page", request.url));
  }

  // 3단계: 헤더 추가 후 다음으로 전달
  const response = NextResponse.next();
  response.headers.set("x-custom-header", "hello");
  return response;
}

export const config = {
  matcher: ["/((?!api|_next/static|favicon.ico).*)"],
};
```

---

## 실무 적용 가이드

### 패턴 선택 체크리스트

| 상황 | 권장 패턴 |
|------|-----------|
| 상태 변경을 여러 컴포넌트에 알려야 함 | **관찰자** (Zustand `subscribe`, RxJS, EventBus) |
| 여러 객체 간 복잡한 워크플로 조율 | **중재자** (React Context, 중앙 스토어) |
| 실행 취소/재실행이 필요 | **커맨드** (Command + History 스택) |
| 다양한 컬렉션을 동일하게 순회 | **이터레이터** (`Symbol.iterator`, 제네레이터) |
| 동일 문제의 알고리즘을 교체 | **전략** (함수 인자, Hook 조합) |
| 객체 행동이 상태에 따라 완전히 달라짐 | **상태** (XState, useReducer 상태 머신) |
| 알고리즘 골격은 같고 세부만 다름 | **템플릿 메서드** (추상 클래스) |
| 요청을 단계별 처리자에게 전달 | **책임 연쇄** (미들웨어 체인) |
| 클래스 변경 없이 새 연산 추가 | **방문자** (AST 처리, 파일 시스템 분석) |

### 행위 패턴 조합 사례

| 조합 | 사례 |
|------|------|
| Observer + Command | Redux — 상태 변경 알림 + 액션 캡슐화 |
| Strategy + State | 상태별로 다른 전략을 선택하는 게임 AI |
| Chain of Responsibility + Command | 미들웨어 체인에서 각 단계가 커맨드를 실행 |
| Mediator + Observer | 중재자가 Pub/Sub 이벤트를 수신하여 워크플로 조율 |
| Template Method + Strategy | 골격은 고정, 특정 단계를 전략으로 주입 |

### TypeScript가 행위 패턴에 미치는 영향

| JavaScript 방식 | TypeScript 대안 |
|-----------------|-----------------|
| `observer.update` 존재 여부 런타임 확인 | `Observer<T>` 인터페이스 컴파일 타임 보장 |
| 이벤트 데이터 타입 불명 | 제네릭 `EventBus<E>`로 토픽별 데이터 타입 강제 |
| `execute(methodName, ...args)` 문자열 | 판별 유니언으로 커맨드 타입 안전성 보장 |
| 상태 전환 조건문 | 상태별 클래스 + 인터페이스로 허용되는 전환만 구현 |
| 미들웨어 `ctx` 타입 불명 | `Context` 인터페이스로 타입 안전한 체인 |

---

## 요약

- **관찰자 패턴**: 주체의 상태 변화를 구독자에게 자동 통지. Pub/Sub 변형으로 토픽 기반 느슨한 결합 구현. Signals 제안이 언어 레벨 지원을 향해 진행 중
- **중재자 패턴**: 객체 간 직접 참조를 중앙 허브로 대체하여 워크플로를 한 곳에서 관리. 관찰자 패턴과의 핵심 차이는 "로직이 중재자에 집중"되는 점
- **커맨드 패턴**: 요청을 객체로 캡슐화하여 실행/취소/큐잉 지원. Redux 액션, `useReducer`가 현대적 구현
- **이터레이터 패턴**: `Symbol.iterator`와 제네레이터로 언어 레벨에서 지원. `for-await-of`로 비동기 순회까지 확장
- **전략 패턴**: 알고리즘을 캡슐화하여 교체 가능. TypeScript에서는 함수 타입으로 간결하게 표현 가능
- **상태 패턴**: 조건문을 다형성으로 대체. XState로 선언적 상태 머신 구현 가능
- **템플릿 메서드 패턴**: 알고리즘 골격을 고정하고 세부만 하위 클래스에 위임. 프레임워크 설계에 유용
- **책임 연쇄 패턴**: Express/Koa/Next.js 미들웨어의 기반 패턴. `next()` 호출로 체인 진행/중단 제어
- **방문자 패턴**: 클래스 변경 없이 새 연산 추가. ESLint, Babel, TypeScript 컴파일러 등 AST 도구의 핵심

---

## 다른 챕터와의 관계

- **← Ch06 (패턴 카테고리)**: 생성/구조/행위 분류 체계와 GoF 패턴 분류표를 제공한다
- **← Ch07 (생성 패턴)**: 행위 패턴이 다루는 객체들은 생성 패턴(팩토리, 빌더 등)으로 만들어진다
- **← Ch08 (구조 패턴)**: 데코레이터로 감싼 객체에 관찰자를 붙이거나, 퍼사드를 중재자로 확장하는 등 구조 패턴과 조합된다
- **→ Ch10 (MV* 패턴)**: 행위 패턴(특히 Observer, Mediator)이 MVC/MVP/MVVM 아키텍처의 기반 메커니즘이 된다
- **→ Ch14 (리액트 디자인 패턴)**: Observer → Zustand/Jotai, Command → useReducer, State → XState 등 React 생태계에서의 구현으로 이어진다
