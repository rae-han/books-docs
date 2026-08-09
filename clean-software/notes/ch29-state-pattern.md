# Chapter 29: The State Pattern (스테이트 패턴)

## 핵심 질문

복잡한 시스템의 행위를 어떻게 간결하고 명쾌하게 표현할 수 있는가? 유한 상태 기계(*FSM - Finite State Machine, 유한한 상태들과 그 사이의 전이로 시스템을 정의하는 추상 모델*)는 어떤 방식으로 구현할 수 있으며, 각 구현 기법은 어떤 비용과 장점을 가지는가? 스테이트 패턴은 다른 구현 방식들과 어떻게 다른가?

> 변화의 수단이 없는 국가는 자기 보전의 수단이 없는 국가다.<br>— 에드먼드 버크(Edmund Burke), 1729~1797

---

## 1. 유한 상태 기계의 개괄

유한 상태 오토마타(*finite state automata - 유한한 상태와 전이로 정의되는 계산 모델*)는 소프트웨어 무기 창고에서 꺼내 쓸 수 있는 가장 유용한 추상 개념 중 하나다. 복잡한 시스템의 행위를 조사하거나 정의할 수 있는 간결하면서도 명쾌한 방법을 제공하며, 이해하기도 쉽고 고치기도 쉬운 강력한 구현 전략도 제공한다.

> **핵심 통찰**: 유한 상태 기계는 상위 수준의 GUI부터 가장 하위 수준의 통신 프로토콜에 이르기까지 시스템의 **모든 수준에서** 사용할 수 있다. 거의 어디에나 적용할 수 있는 보편적 도구다.

### 1.1 지하철 개찰구 예제

지하철 개찰구(*subway turnstile - 사람들이 지하철에 타기 위해 통과하는 문을 제어하는 장치*)는 간단한 FSM의 한 예다. 두 가지 상태와 두 가지 이벤트를 가진다.

**초기 STD(*State Transition Diagram - 상태 전이 다이어그램*):**

```
       ┌──────────┐  coin/unlock   ┌────────────┐
   ──▶ │  Locked  │ ─────────────▶ │  Unlocked  │
       │          │ ◀───────────── │            │
       └──────────┘   pass/lock    └────────────┘
```

STD는 적어도 네 부분으로 구성된다.

| 구성 요소 | 표현 | 의미 |
|-----------|------|------|
| **상태(state)** | 모서리가 둥근 상자 | 시스템이 머무를 수 있는 안정 위치 |
| **전이(transition)** | 상태를 연결하는 화살표 | 한 상태에서 다른 상태로 이동 |
| **이벤트(event)** | 화살표의 이름표 앞부분 | 전이를 일으키는 입력 |
| **행동(action)** | 화살표의 이름표 뒷부분 | 전이가 일어날 때 수행할 작업 |

위 다이어그램은 다음 두 문장으로 완전히 설명된다:

- Locked 상태에서 `coin` 이벤트를 받으면, Unlocked 상태로 전이하고 `unlock` 행동을 호출한다.
- Unlocked 상태에서 `pass` 이벤트를 받으면, Locked 상태로 전이하고 `lock` 행동을 호출한다.

### 1.2 상태 전이 테이블 (STT)

전이를 기술한 문장들은 **상태 전이 테이블**(*STT - State Transition Table*)이라는 단순한 표로 요약할 수 있다.

| 현재 상태 | 이벤트 | 다음 상태 | 행동 |
|-----------|--------|-----------|------|
| Locked | coin | Unlocked | unlock |
| Unlocked | pass | Locked | lock |

각 행은 시작 상태, 전이를 일으키는 이벤트, 종료 상태, 수행할 행동이라는 **네 가지 요소**로 전이 화살표 하나를 설명한다.

### 1.3 STD/STT의 설계 도구로서의 가치

STD와 STT는 단순히 행위를 기술하는 표기법이 아니다. 매우 강력한 **설계 도구**이기도 하다.

> **핵심 통찰**: STD/STT는 설계자가 **누락된 전이**를 찾아내기 쉽게 만든다. 프로그래머는 대개 정상적인 이벤트 흐름을 더 철저히 궁리하는 반면 비정상적인 가능성은 놓치기 쉽다. STD/STT는 모든 상태에서 모든 이벤트를 다 다루는지 쉽게 점검할 수 있는 방법을 제공한다.

위 초기 모델을 검토해 보면 누락이 보인다:

- Unlocked 상태에서 `coin` 이벤트를 다루는 전이가 없다.
- Locked 상태에서 `pass` 이벤트를 다루는 전이가 없다.

이를 보완한 완성형 STD는 다음과 같다.

```
         pass/alarm
         ┌───┐
         │   ▼
       ┌─────────┐  coin/unlock   ┌───────────┐
   ──▶ │ Locked  │ ─────────────▶ │ Unlocked  │
       │         │ ◀───────────── │           │
       └─────────┘   pass/lock    └───────────┘
                                       │  ▲
                                       └──┘
                                  coin/thankyou
```

**완전한 STT:**

| 현재 상태 | 이벤트 | 다음 상태 | 행동 |
|-----------|--------|-----------|------|
| Locked | coin | Unlocked | unlock |
| Locked | pass | Locked | alarm |
| Unlocked | coin | Unlocked | thankyou |
| Unlocked | pass | Locked | lock |

승객이 동전을 두 번 넣으면 "고맙습니다" 표시가 켜지고, 잠긴 문을 무리하게 통과하면 경고음이 울린다.

---

## 2. 구현 기법 1 — 중첩 switch/case

FSM을 구현하는 가장 직접적인 전략은 **중첩 switch/case**(*nested switch/case - 두 단계 이상으로 중첩된 switch 문*)를 사용하는 것이다.

<details>
<summary>원문 Java 코드 — Turnstile.java (중첩 switch/case)</summary>

```java
public class Turnstile {
    // 상태
    public static final int LOCKED = 0;
    public static final int UNLOCKED = 1;

    // 이벤트
    public static final int COIN = 0;
    public static final int PASS = 1;

    /* 전용 */ int state = LOCKED;
    private TurnstileController turnstileController;

    public Turnstile(TurnstileController action) {
        turnstileController = action;
    }

    public void event(int event) {
        switch (state) {
            case LOCKED:
                switch (event) {
                    case COIN:
                        state = UNLOCKED;
                        turnstileController.unlock();
                        break;
                    case PASS:
                        turnstileController.alarm();
                        break;
                }
                break;
            case UNLOCKED:
                switch (event) {
                    case COIN:
                        turnstileController.thankyou();
                        break;
                    case PASS:
                        state = LOCKED;
                        turnstileController.lock();
                        break;
                }
                break;
        }
    }
}
```

</details>

```typescript
// TypeScript
enum State { LOCKED, UNLOCKED }
enum Event { COIN, PASS }

interface TurnstileController {
    lock(): void;
    unlock(): void;
    thankyou(): void;
    alarm(): void;
}

class Turnstile {
    state: State = State.LOCKED;

    constructor(private controller: TurnstileController) {}

    event(event: Event): void {
        switch (this.state) {
            case State.LOCKED:
                switch (event) {
                    case Event.COIN:
                        this.state = State.UNLOCKED;
                        this.controller.unlock();
                        break;
                    case Event.PASS:
                        this.controller.alarm();
                        break;
                }
                break;
            case State.UNLOCKED:
                switch (event) {
                    case Event.COIN:
                        this.controller.thankyou();
                        break;
                    case Event.PASS:
                        this.state = State.LOCKED;
                        this.controller.lock();
                        break;
                }
                break;
        }
    }
}
```

중첩 switch/case는 코드를 상호 배타적인 네 영역으로 나누며, 각 영역은 STD의 전이 하나에 대응한다.

### 2.1 행동을 컨트롤러 인터페이스로 분리하기

위 코드에서 `TurnstileController` 인터페이스는 단순히 코드를 깔끔하게 정리하기 위한 장치가 아니다. **테스트가 설계에 미치는 영향**을 보여주는 사례다.

<details>
<summary>원문 Java 코드 — TurnstileController.java</summary>

```java
public interface TurnstileController {
    public void lock();
    public void unlock();
    public void thankyou();
    public void alarm();
}
```

</details>

테스트 코드에서는 이 인터페이스를 **스푸프(*spoof - 테스트용 가짜 구현*)** 로 구현하여 어떤 행동이 호출되었는지 검증한다.

```typescript
// TypeScript - 테스트 코드
describe("Turnstile", () => {
    let t: Turnstile;
    let lockCalled = false;
    let unlockCalled = false;
    let thankyouCalled = false;
    let alarmCalled = false;

    beforeEach(() => {
        lockCalled = unlockCalled = thankyouCalled = alarmCalled = false;
        const controllerSpoof: TurnstileController = {
            lock: () => { lockCalled = true; },
            unlock: () => { unlockCalled = true; },
            thankyou: () => { thankyouCalled = true; },
            alarm: () => { alarmCalled = true; },
        };
        t = new Turnstile(controllerSpoof);
    });

    it("Locked 상태에서 coin을 받으면 Unlocked로 가고 unlock을 호출한다", () => {
        t.state = State.LOCKED;
        t.event(Event.COIN);
        expect(t.state).toBe(State.UNLOCKED);
        expect(unlockCalled).toBe(true);
    });

    it("Unlocked 상태에서 pass를 받으면 Locked로 가고 lock을 호출한다", () => {
        t.state = State.UNLOCKED;
        t.event(Event.PASS);
        expect(t.state).toBe(State.LOCKED);
        expect(lockCalled).toBe(true);
    });
});
```

> **Uncle Bob의 경험**: 테스트가 `state` 변수에 직접 접근하려면 이 변수가 전용(private)이면 안 된다. 그래서 변수를 패키지 스코프로 만들고 "원래는 전용으로 만들고 싶다"고 주석을 달았다. 자바에는 C++의 friend 같은 개념이 없어 테스트 가시성을 따로 표현하기 어렵다. 테스트할 생각을 하지 않았다면 아마 `TurnstileController` 인터페이스를 만들지도 않았을 것이다. 하지만 그랬다면 유감스러웠을 것이다 — 이 인터페이스는 **FSM의 논리와 행동 사이의 결합을 깔끔히 끊어준다**.

> **핵심 통찰**: 각 단위를 독립적으로 검증하는 테스트 코드를 만들어야 한다는 필요성 때문에, 우리는 테스트할 필요가 없었더라면 사용하지 않았을 방법들로 코드 사이의 결합을 끊게 된다. **테스트 용이성은 결합이 적은 설계를 이끄는 힘**으로 작용한다.

### 2.2 중첩 switch/case의 비용과 장점

| 구분 | 내용 |
|------|------|
| **장점** | 간단한 상태 기계라면 명쾌하고 효율적이다. 모든 상태와 코드를 한두 페이지 안에 볼 수 있다 |
| **비용 1** | 상태와 이벤트가 수십 개로 많아지면 case 문이 여러 페이지에 걸쳐 이어지면서 알아보기 힘들어진다 |
| **비용 2** | FSM의 **논리와 행동의 구별이 명확하지 않다**. 행동이 case 문 사이에 깊이 파묻히기 쉽다 |
| **비용 3** | 길이가 긴 중첩 switch/case의 유지보수는 매우 어렵고 실수에 취약하다 |

---

## 3. 구현 기법 2 — 전이 테이블 해석

전이를 설명하는 **데이터 테이블**을 만드는 것도 FSM을 구현하는 매우 흔한 방법이다. 이벤트를 처리하는 일종의 엔진이 이 테이블을 해석하는데, 엔진은 발생한 이벤트와 들어맞는 전이를 찾아서 적절한 동작을 호출하고 상태를 변경한다.

### 3.1 전이 테이블 구축과 엔진

<details>
<summary>원문 Java 코드 — Turnstile.java (전이 테이블 방식)</summary>

```java
public class Turnstile {
    public static final int LOCKED = 0;
    public static final int UNLOCKED = 1;
    public static final int COIN = 0;
    public static final int PASS = 1;

    int state = LOCKED;
    private TurnstileController turnstileController;
    private Vector transitions = new Vector();

    private interface Action {
        void execute();
    }

    private class Transition {
        int currentState;
        int event;
        int newState;
        Action action;

        public Transition(int currentState, int event,
                          int newState, Action action) {
            this.currentState = currentState;
            this.event = event;
            this.newState = newState;
            this.action = action;
        }
    }

    public Turnstile(TurnstileController action) {
        turnstileController = action;
        addTransition(LOCKED,   COIN, UNLOCKED, unlock());
        addTransition(LOCKED,   PASS, LOCKED,   alarm());
        addTransition(UNLOCKED, COIN, UNLOCKED, thankyou());
        addTransition(UNLOCKED, PASS, LOCKED,   lock());
    }

    public void event(int event) {
        for (int i = 0; i < transitions.size(); i++) {
            Transition transition = (Transition) transitions.elementAt(i);
            if (state == transition.currentState
                && event == transition.event) {
                state = transition.newState;
                transition.action.execute();
            }
        }
    }

    private Action lock()     { return () -> turnstileController.lock(); }
    private Action unlock()   { return () -> turnstileController.unlock(); }
    private Action alarm()    { return () -> turnstileController.alarm(); }
    private Action thankyou() { return () -> turnstileController.thankyou(); }
}
```

</details>

```typescript
// TypeScript
type Action = () => void;

interface Transition {
    currentState: State;
    event: Event;
    newState: State;
    action: Action;
}

class Turnstile {
    private state: State = State.LOCKED;
    private transitions: Transition[] = [];

    constructor(private controller: TurnstileController) {
        this.addTransition(State.LOCKED,   Event.COIN, State.UNLOCKED, () => this.controller.unlock());
        this.addTransition(State.LOCKED,   Event.PASS, State.LOCKED,   () => this.controller.alarm());
        this.addTransition(State.UNLOCKED, Event.COIN, State.UNLOCKED, () => this.controller.thankyou());
        this.addTransition(State.UNLOCKED, Event.PASS, State.LOCKED,   () => this.controller.lock());
    }

    private addTransition(
        currentState: State,
        event: Event,
        newState: State,
        action: Action,
    ): void {
        this.transitions.push({ currentState, event, newState, action });
    }

    event(event: Event): void {
        for (const t of this.transitions) {
            if (this.state === t.currentState && event === t.event) {
                this.state = t.newState;
                t.action();
            }
        }
    }
}
```

### 3.2 전이 테이블 해석의 비용과 장점

> **핵심 통찰**: 전이 테이블을 구축하는 코드를 **정규적인 상태 전이 테이블처럼 읽을 수 있다**. `addTransition` 네 라인을 이해하기는 굉장히 쉽다. 상태 기계의 논리도 한 장소에 모여 있으며, 동작의 구현과 섞여 오염되지도 않는다.

| 구분 | 내용 |
|------|------|
| **장점 1** | 테이블이 STT처럼 읽힌다. 새 전이 추가는 `addTransition` 한 줄 추가로 끝 |
| **장점 2** | **실행시간에 테이블 교체 가능**. 상태 기계 로직을 동적으로 패치하거나 시작 조건에 따라 다른 FSM을 선택할 수 있다 |
| **비용 1** | **속도**. 전이 테이블을 선형 검색하므로 큰 상태 기계에서는 무시 못 할 정도로 오래 걸릴 수 있다 |
| **비용 2** | 테이블을 지원하는 보조 코드(액션 래퍼, addTransition 함수 등)가 상당히 많이 필요하다 |

---

## 4. 구현 기법 3 — 스테이트 패턴 (State Pattern)

**스테이트 패턴**(*State Pattern - GoF가 정의한 23개 디자인 패턴 중 하나*)은 중첩 switch/case의 효율성과 상태 테이블 해석의 유연성을 **결합**한 패턴이다.

### 4.1 구조

```
            ┌─────────────────┐         «interface»
            │    Turnstile    │ ───▶  ┌──────────────────┐
            ├─────────────────┤       │  TurnstileState  │
            │ + coin()        │       ├──────────────────┤
            │ + pass()        │       │ + coin(t)        │
            │ # lock()        │       │ + pass(t)        │
            │ # unlock()      │       └──────────────────┘
            │ # thankyou()    │              △       △
            │ # alarm()       │              │       │
            └─────────────────┘   ┌──────────┘       └──────────┐
                                  │                             │
                       ┌──────────────────────┐    ┌─────────────────────────┐
                       │ LockedTurnstileState │    │ UnlockedTurnstileState  │
                       ├──────────────────────┤    ├─────────────────────────┤
                       │ + coin(t)            │    │ + coin(t)               │
                       │ + pass(t)            │    │ + pass(t)               │
                       └──────────────────────┘    └─────────────────────────┘
```

`Turnstile`은 이벤트들을 공용 메소드로 갖고 행동들은 보호(protected) 메소드로 갖는다. 그리고 `TurnstileState`라는 인터페이스에 대한 참조를 하나 갖는다. `TurnstileState`의 파생형 2개가 각각 FSM의 상태 2개를 나타낸다.

이벤트 메소드 중 하나가 호출되면 `Turnstile`은 이를 `TurnstileState` 객체에게 **위임**한다. 상태 변경은 참조가 다른 파생형 인스턴스를 가리키게 함으로써 이루어진다.

### 4.2 구현

<details>
<summary>원문 Java 코드 — TurnstileState.java</summary>

```java
interface TurnstileState {
    void coin(Turnstile t);
    void pass(Turnstile t);
}

class LockedTurnstileState implements TurnstileState {
    public void coin(Turnstile t) {
        t.setUnlocked();
        t.unlock();
    }
    public void pass(Turnstile t) {
        t.alarm();
    }
}

class UnlockedTurnstileState implements TurnstileState {
    public void coin(Turnstile t) {
        t.thankyou();
    }
    public void pass(Turnstile t) {
        t.setLocked();
        t.lock();
    }
}

public class Turnstile {
    private static TurnstileState lockedState = new LockedTurnstileState();
    private static TurnstileState unlockedState = new UnlockedTurnstileState();
    private TurnstileController turnstileController;
    private TurnstileState state = lockedState;

    public Turnstile(TurnstileController action) {
        turnstileController = action;
    }
    public void coin() { state.coin(this); }
    public void pass() { state.pass(this); }

    public void setLocked()   { state = lockedState; }
    public void setUnlocked() { state = unlockedState; }
    public boolean isLocked()   { return state == lockedState; }
    public boolean isUnlocked() { return state == unlockedState; }

    void thankyou() { turnstileController.thankyou(); }
    void alarm()    { turnstileController.alarm(); }
    void lock()     { turnstileController.lock(); }
    void unlock()   { turnstileController.unlock(); }
}
```

</details>

```typescript
// TypeScript
interface TurnstileState {
    coin(t: Turnstile): void;
    pass(t: Turnstile): void;
}

class LockedTurnstileState implements TurnstileState {
    coin(t: Turnstile): void {
        t.setUnlocked();
        t.unlock();
    }
    pass(t: Turnstile): void {
        t.alarm();
    }
}

class UnlockedTurnstileState implements TurnstileState {
    coin(t: Turnstile): void {
        t.thankyou();
    }
    pass(t: Turnstile): void {
        t.setLocked();
        t.lock();
    }
}

class Turnstile {
    // 상태 객체는 변수가 없으므로 정적 싱글톤으로 공유한다
    private static lockedState: TurnstileState = new LockedTurnstileState();
    private static unlockedState: TurnstileState = new UnlockedTurnstileState();
    private state: TurnstileState = Turnstile.lockedState;

    constructor(private controller: TurnstileController) {}

    coin(): void { this.state.coin(this); }
    pass(): void { this.state.pass(this); }

    setLocked():   void { this.state = Turnstile.lockedState; }
    setUnlocked(): void { this.state = Turnstile.unlockedState; }

    thankyou(): void { this.controller.thankyou(); }
    alarm():    void { this.controller.alarm(); }
    lock():     void { this.controller.lock(); }
    unlock():   void { this.controller.unlock(); }
}
```

> **핵심 통찰**: 상태 객체는 변수가 없으므로 **정적(static) 싱글톤**으로 공유한다. 상태가 바뀔 때마다 새 인스턴스를 만들지 않아도 되며, `Turnstile` 인스턴스가 여러 개여도 상태 객체는 재사용된다.

### 4.3 스테이트 vs 스트래터지

스테이트 패턴의 클래스 다이어그램은 **스트래터지 패턴(*Strategy Pattern - 14장에서 다룬, 알고리즘을 객체로 캡슐화하는 패턴*)** 과 매우 닮았다. 두 패턴 모두 컨텍스트(*context - 다형적 행동을 위임받는 주체 클래스*) 클래스가 있고, 두 패턴 모두 파생형이 여러 개인 다형적 기반 클래스에 위임한다.

| 구분 | 스테이트 | 스트래터지 |
|------|----------|-------------|
| 컨텍스트 참조 | 파생형이 컨텍스트 참조를 가짐 | 컨텍스트 참조 불필요 |
| 컨텍스트 메소드 호출 | 파생형의 중심 기능 | 호출할 필요 없음 |
| 의도 | 상태에 따라 행동을 바꾸는 것 | 알고리즘을 교체하는 것 |

> **핵심 통찰**: 스테이트 패턴의 모든 적용 사례는 스트래터지 패턴이라고 볼 수도 있지만, **스트래터지 패턴의 모든 적용이 스테이트 패턴은 아니다**. 스테이트는 스트래터지의 특수한 형태다.

### 4.4 스테이트 패턴의 비용과 장점

| 구분 | 내용 |
|------|------|
| **장점 1** | 상태 기계의 **논리와 행동을 매우 분명히 분리**한다. 행동은 Context에, 논리는 State 파생형들에 분산된다 |
| **장점 2** | **재사용성**. 다른 상태 논리에 같은 Context를 재사용하거나, 같은 상태 논리에 다른 Context를 적용할 수 있다 |
| **장점 3** | **효율성**. 가상 함수 호출 한 번으로 분기가 끝나므로 중첩 switch/case만큼 빠르다 |
| **비용 1** | State 파생형을 일일이 작성하는 작업이 **지루하다**. 상태가 20개라면 정신이 멍해진다 |
| **비용 2** | **논리가 분산**된다. 상태 기계의 논리를 한눈에 볼 수 있는 장소가 없어 유지보수가 힘들어진다 |

---

## 5. 구현 기법 4 — SMC (State Machine Compiler)

State 파생형 작성의 지루함과 상태 기계 논리를 한 장소에 표현할 필요성 때문에, Uncle Bob은 **텍스트로 작성된 상태 전이 테이블을 스테이트 패턴 구현 클래스들로 변환하는 도구**인 SMC(*State Machine Compiler - 상태 기계 컴파일러, Uncle Bob이 작성한 무료 오픈소스 도구*)를 만들었다.

### 5.1 SMC 입력 문법

```
FSMName Turnstile
Context TurnstileActions
Initial Locked
Exception FSMError
{
  Locked {
    coin  Unlocked  unlock
    pass  Locked    alarm
  }
  Unlocked {
    coin  Unlocked  thankyou
    pass  Locked    lock
  }
}
```

맨 위 네 줄은 각각:

| 항목 | 의미 |
|------|------|
| `FSMName` | 생성될 상태 기계 클래스 이름 |
| `Context` | 행동 함수를 선언하는 클래스 이름 |
| `Initial` | 시작 상태 |
| `Exception` | 잘못된 이벤트를 받았을 때 던질 예외 이름 |

본문은 `currentState { event newState action }` 형태로 상태별 전이를 나열한다.

### 5.2 SMC가 만들어내는 3차원 FSM

컴파일러는 Context 클래스에서 파생된 클래스를 생성한다. 사용자는 다시 그 클래스에서 파생받는 클래스를 만들어 행동 함수를 구현한다. 이렇게 **3계층 구조**가 만들어지며, 이를 **3차원 유한 상태 기계**(*Three-Level FSM*)라고 부른다.

```
       «interface»
   ┌──────────────────┐
   │ TurnstileActions │   ← (1) 행동 함수 선언
   ├──────────────────┤
   │ + lock()         │
   │ + unlock()       │
   │ + thankyou()     │
   │ + alarm()        │
   └──────────────────┘
            △
            │
   «generated»
   ┌─────────────────┐    ┌──────────────────┐
   │    Turnstile    │ ──▶│   State (priv)   │   ← (2) SMC 생성: FSM 논리
   ├─────────────────┤    ├──────────────────┤
   │ + coin()        │    │ + coin(Turnstile)│
   │ + pass()        │    │ + pass(Turnstile)│
   └─────────────────┘    └──────────────────┘
            △                  △        △
            │                  │        │
            │            ┌─────┘        └─────┐
            │       ┌─────────┐         ┌──────────┐
            │       │ Locked  │         │ Unlocked │
            │       └─────────┘         └──────────┘
            │
   ┌─────────────────┐
   │  TurnstileFSM   │   ← (3) 사용자 작성: 실제 행동 위임
   ├─────────────────┤
   │ + lock()        │ ─▶ TurnstileController.lock()
   │ + unlock()      │
   │ + thankyou()    │
   │ + alarm()       │
   └─────────────────┘
```

사용자가 작성해야 할 코드는 `TurnstileActions` 추상 클래스와 `TurnstileFSM` 구상 클래스뿐이다.

<details>
<summary>원문 Java 코드 — 사용자 작성분 (TurnstileActions, TurnstileFSM)</summary>

```java
public abstract class TurnstileActions {
    public void lock() {}
    public void unlock() {}
    public void thankyou() {}
    public void alarm() {}
}

public class TurnstileFSM extends Turnstile {
    private TurnstileController controller;
    public TurnstileFSM(TurnstileController controller) {
        this.controller = controller;
    }
    public void lock()     { controller.lock(); }
    public void unlock()   { controller.unlock(); }
    public void thankyou() { controller.thankyou(); }
    public void alarm()    { controller.alarm(); }
}
```

</details>

```typescript
// TypeScript - 사용자 작성분
abstract class TurnstileActions {
    lock(): void {}
    unlock(): void {}
    thankyou(): void {}
    alarm(): void {}
}

// Turnstile은 SMC가 생성한 클래스. 여기서는 행동을 controller에 위임만 한다.
class TurnstileFSM extends Turnstile {
    constructor(private controller: TurnstileController) {
        super();
    }
    override lock():     void { this.controller.lock(); }
    override unlock():   void { this.controller.unlock(); }
    override thankyou(): void { this.controller.thankyou(); }
    override alarm():    void { this.controller.alarm(); }
}
```

> **핵심 통찰**: 자동 생성된 코드와 사용자가 작성하는 코드가 **완전히 분리**되어 있다. 자동 생성된 코드를 직접 수정해야 할 일은 절대로 없어야 한다. 심지어 그 코드를 보는 일도 없어야 한다. 이진 코드(binary)를 대하는 것처럼 다루어도 될 정도다.

### 5.3 SMC 접근 방법의 비용과 장점

| 구분 | 내용 |
|------|------|
| **장점 1** | FSM 설명이 한 장소에 모두 모여 있어 유지보수가 매우 쉽다 |
| **장점 2** | 논리와 행동 구현이 철저히 분리된다 |
| **장점 3** | 효율적이고, 우아하며, 작성해야 할 코드가 매우 적다 |
| **장점 4** | 잘못된 이벤트가 일어나면 자동으로 예외(`FSMError`)를 던지는 코드까지 생성된다 |
| **비용** | **별도 도구 의존**. 도구 설치와 사용법을 익혀야 한다 (하지만 SMC는 매우 간단하고 무료) |

---

## 6. 네 가지 구현 기법 비교

| 기법 | 효율성 | 유연성 | 논리 가시성 | 작성 비용 | 추천 시점 |
|------|--------|--------|-------------|-----------|-----------|
| 중첩 switch/case | ◎ | △ | ○ (소규모) | ○ | 상태/이벤트가 적은 단순 FSM |
| 전이 테이블 해석 | △ (선형 검색) | ◎ (런타임 교체) | ◎ | △ (지원 코드 多) | 런타임에 로직 교체가 필요할 때 |
| 스테이트 패턴 | ◎ | ○ | △ (분산됨) | △ (파생형 多) | 패턴 학습용/도구 없이 클린한 구현 원할 때 |
| SMC | ◎ | ◎ | ◎ | ◎ (입력 짧음) | 중간~대규모 FSM, 도구 도입 가능할 때 |

---

## 7. 어떤 경우에 상태 기계를 사용해야 하는가?

Uncle Bob은 상태 기계(와 SMC)를 다양한 종류의 애플리케이션에서 사용한다.

### 7.1 GUI에 대한 상위 수준 애플리케이션 정책

> **Uncle Bob의 경험**: "무상태(stateless)" GUI를 구현하는 코드 자체는 아이러니하게도 **상태와 밀접하다**. 어떤 메뉴 항목과 버튼을 비활성화할지, 어떤 하위 창을 보여줄지, 어떤 탭을 활성화할지, 초점을 어디에 맞출지 — 이 모든 결정은 인터페이스의 상태와 관련 있다. 이런 요소들을 단일 제어 구조에 조직해놓지 않으면 제어가 악몽이 된다는 사실을 오래전에 배웠다. 그 이후로 내가 작성하는 거의 모든 GUI에서는 SMC가 생성하는 FSM을 사용한다.

**로그인 화면 FSM 예시** (`login.sm`):

```
Initial init
{
  init {
    start             logginIn               displayLoginScreen
  }
  logginIn {
    enter             checkingPassword       checkPassword
    cancel            init                   clearScreen
  }
  checkingPassword {
    passwordGood      loggedIn               startUserProcess
    passwordBad       notifyingPasswordBad   displayBadPasswordScreen
    thirdBadPassword  screenLocked           displayLockScreen
  }
  notifyingPasswordBad {
    OK                checkingPassword       displayLoginScreen
    cancel            init                   clearScreen
  }
  screenLocked {
    enter             checkingAdminPassword  checkAdminPassword
  }
  checkingAdminPassword {
    passwordGood      init                   clearScreen
    passwordBad       screenLocked           displayLockScreen
  }
}
```

비밀번호 3회 오류 시 관리자 비밀번호 입력 전까지 화면이 잠긴다. 애플리케이션의 **상위 수준 정책이 한 장소에 머무르며**, 나머지 시스템 코드는 정책 코드와 섞이지 않아 단순해진다.

### 7.2 GUI 상호작용 컨트롤러

상자 그리기 같은 마우스 상호작용도 FSM으로 자연스럽게 표현된다.

```
                         mouseUp/stopAnimation,drawRectangle
            ┌──────────────────────────────────────────┐
            │                                          │
            ▼                                          │
   ┌──────────────────┐                       ┌────────────────┐
   │  Waiting for     │ ─ mouseDown/          │   Dragging     │ ◀─┐
   │     click        │   recordFirstPoint,   │                │   │ mouseMove/
   │                  │   beginAnimation  ──▶ │                │ ──┘ animateRectangle
   └──────────────────┘                       └────────────────┘
                                                  │       ▲
                                       mouseLeave │       │ mouseEnter
                                       pauseAnim  │       │ resumeAnim
                                                  ▼       │
                                            ┌────────────────────┐
                                            │   OutOfCanvas      │
                                            └────────────────────┘
```

GUI 상호작용은 유한 상태 기계로 가득 차 있다. 사용자에게서 오는 이벤트가 상호작용의 상태를 변경한다.

### 7.3 분산 처리

분산 처리도 들어오는 이벤트에 기반해 상태가 변경되는 또 다른 상황이다. 큰 정보 단위를 여러 패킷으로 쪼개 보내는 시나리오는 다음과 같은 FSM이 된다.

```
   ┌─────────┐  sendTransmissionRequest    ┌────────────────────┐
   │ Initial │ ─────────────────────────▶ │ EstablishingSession│
   └─────────┘                             └────────────────────┘
                                            │   ▲           │
                          requestDenied/    │   │           │ sessionAccepted/
                          sendTransmis...  ─┘   │           │ sendFirstPacket
                                                │           ▼
                                                │   ┌──────────────────┐
                                                │   │ SendingPackets   │ ◀─┐ packetAcknowledged/
                                                │   └──────────────────┘ ──┘ sendNextPacket
                                                │           │
                                                │           │ lastPacketAcknowledged/
                                                │           │ sendSessionTermination
                                                │           ▼
                                                │   ┌──────────────────────┐
                                                └── │ TerminatingSession   │
                                  sessionAborted   └──────────────────────┘
                                                            │ sessionTerminated
                                                            ▼
                                                          (End)
```

---

## 8. 결론

> **핵심 통찰**: 유한 상태 기계는 많이 활용되지 않고 있다. 그러나 더 분명하고, 더 단순하고, 더 유연하고, 더 정확한 코드를 작성하는 데 도움이 되는 시나리오는 매우 많다. **스테이트 패턴과 상태 전이 테이블로부터 코드를 생성하는 단순한 도구들**을 활용하면 큰 도움이 될 것이다.

상태와 이벤트를 명시적으로 다루는 사고방식은 코드를 단순하게 만든다. 모든 분기와 부수 효과를 if문 더미 속에 묻어두기보다, **언제 어떤 일이 일어나는지**를 STD/STT라는 명시적 형태로 끌어내는 것이 핵심이다.

---

## 요약

- **유한 상태 기계(FSM)**는 시스템 행위를 간결하게 표현하는 강력한 추상이다. STD(다이어그램)와 STT(테이블)로 시각화된다
- FSM의 4요소: **상태(state) / 전이(transition) / 이벤트(event) / 행동(action)**
- STD/STT는 **누락된 전이**(어느 상태에서 어떤 이벤트를 처리하지 않는가)를 쉽게 발견하게 해주는 설계 도구다
- **네 가지 구현 기법**:
  1. **중첩 switch/case** — 단순·효율적이지만 대규모에 취약
  2. **전이 테이블 해석** — 데이터로 표현해 런타임 교체 가능, 그러나 선형 검색 비용
  3. **스테이트 패턴** — 다형성으로 분기를 대체. 효율적이고 명확하지만 파생형 작성이 지루하고 논리 분산
  4. **SMC** — 텍스트 STT를 스테이트 패턴 코드로 자동 생성. 모든 장점을 결합하지만 도구 의존
- **스테이트 vs 스트래터지**: 둘 다 위임 기반이지만, 스테이트 파생형은 **컨텍스트 참조를 갖고 컨텍스트 메소드를 호출**한다는 점이 핵심 차이
- **테스트 용이성은 좋은 설계를 이끄는 힘** — `TurnstileController` 인터페이스는 테스트 때문에 도입되었지만, 결과적으로 FSM 논리와 행동을 결합 해제했다
- FSM이 자연스럽게 들어맞는 영역: **GUI 상위 정책 / GUI 상호작용 / 분산 통신 프로토콜** — 이벤트에 의해 상태가 변하는 모든 곳
