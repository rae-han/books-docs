# Chapter 12: The Interface Segregation Principle (ISP / 인터페이스 분리 원칙)

## 핵심 질문

한 클래스의 인터페이스가 서로 다른 클라이언트 집합을 동시에 만족시키려 할 때 무엇이 잘못되는가? "비대한(fat) 인터페이스"는 어떻게 자신과 무관한 클라이언트까지 변경에 끌어들이는가? 클라이언트가 분리되어 있다면 인터페이스 역시 어떻게 분리되어야 하는가?

> 인터페이스 분리 원칙은 '비대한' 인터페이스의 단점을 해결한다. 비대한 인터페이스를 가지는 클래스는 응집력 없는 인터페이스를 가지는 클래스다.<br>— Robert C. Martin

---

## 1. ISP의 정의

> **인터페이스 분리 원칙 (Interface Segregation Principle)**<br>**클라이언트는 자신이 사용하지 않는 메소드에 의존하도록 강제되어서는 안 된다.**

비대한(*fat - 응집력이 없고 다양한 책임이 한데 묶인*) 인터페이스를 가지는 클래스는 응집력 없는 인터페이스를 가지는 클래스다. 그 인터페이스의 메소드들은 여러 그룹으로 분해될 수 있고, 각 그룹은 **서로 다른 클라이언트 집합**을 지원한다. 즉, 어떤 클라이언트는 메소드 그룹 A를 사용하고, 다른 클라이언트는 메소드 그룹 B를 사용한다.

ISP는 이런 객체가 존재할 수 있음은 인정한다. 그러나 **클라이언트가 이 객체를 단일한 클래스로 보게 해서는 안 된다**고 주장한다. 클라이언트는 응집력 있는 **추상 기반 클래스**(여러 개로 분리된 인터페이스)를 통해 객체를 바라보아야 한다.

> **핵심 통찰**: 클라이언트가 자신이 사용하지 않는 메소드에 의존하도록 강제될 때, 그 클라이언트는 그 메소드의 변경에 취약해진다. 이것은 모든 클라이언트 사이에 **의도하지 않은 결합**을 만들어 낸다. 어떤 클라이언트가 자신은 사용하지 않지만 다른 클라이언트가 사용하는 메소드를 포함하는 클래스에 의존할 때, 그 클라이언트는 다른 클라이언트 때문에 가해진 변경에 영향을 받는다.

---

## 2. 인터페이스 오염 — Door / TimedDoor 예제

### 2.1 시작점: 단순한 Door 추상화

보안 시스템을 생각해 보자. 시스템에는 잠기거나 열릴 수 있는 `Door` 객체들이 있고, 자신이 열렸는지 잠겼는지 안다.

<details>
<summary>원문 C++ 코드 (목록 12-1)</summary>

```cpp
// 목록 12-1: 보안 출입문
class Door {
public:
    virtual void Lock() = 0;
    virtual void Unlock() = 0;
    virtual bool IsDoorOpen() = 0;
};
```

</details>

```typescript
// TypeScript - Door 추상화
interface Door {
    lock(): void;
    unlock(): void;
    isDoorOpen(): boolean;
}
```

`Door`는 추상이므로 클라이언트는 특정 구현에 의존하지 않고도 `Door` 인터페이스를 따르는 객체를 사용할 수 있다.

### 2.2 새 요구사항: TimedDoor

이제 `TimedDoor` 구현을 추가하자. 문이 열린 채로 너무 오래 있으면 알람을 울려야 한다. 이를 위해 `TimedDoor`는 `Timer` 객체와 통신한다.

<details>
<summary>원문 C++ 코드 (목록 12-2)</summary>

```cpp
// 목록 12-2
class Timer {
public:
    void Register(int timeout, TimerClient* client);
};

class TimerClient {
public:
    virtual void Timeout() = 0;
};
```

</details>

```typescript
// TypeScript - Timer / TimerClient
interface TimerClient {
    timeout(): void;
}

class Timer {
    register(timeout: number, client: TimerClient): void {
        // 일정 시간 뒤 client.timeout() 호출
    }
}
```

제한시간 초과 정보를 받고 싶은 객체는 `Timer.register`를 호출한다. 인자로는 제한시간과, 시간 초과 시 호출될 `timeout` 메소드를 가진 `TimerClient`가 들어간다.

### 2.3 미숙한 해결책: Door가 TimerClient를 상속

`TimedDoor`가 `TimerClient` 메시지를 받게 하려면 어떻게 할까? **한 가지 미숙한 방법**은 `Door`가 `TimerClient`를 상속받도록 만드는 것이다.

```
                «interface»
                TimerClient
                ──────────
                 timeout()
                     △
                     │
                     │
                   Door
                ──────────
                  lock()
                  unlock()
                  isDoorOpen()
                  timeout()      ◀── Door 모두가 끌려옴
                     △
                     │
                TimedDoor
```

이 해결책에서 `Door`(따라서 모든 파생 `Door`)는 `TimerClient`를 상속받는다. 이렇게 하면 `TimerClient`가 `Timer`에 자신을 등록하고 `timeout` 메시지를 받을 수 있다는 점은 보장된다.

### 2.4 무엇이 잘못되었는가 — 인터페이스 오염

| 문제 | 설명 |
|------|------|
| **불필요한 결합** | `Door`가 `TimerClient`에 의존하게 된다 |
| **퇴화한 구현 강요** | 타이머가 필요 없는 `Door` 파생 클래스도 `timeout` 메소드를 (아무 일도 하지 않게) 구현해야 한다 — 잠재적 LSP 위반 |
| **불필요한 임포트** | 타이머를 안 쓰는 `Door` 변형을 사용하는 애플리케이션도 `TimerClient`를 임포트해야 한다 |
| **인터페이스 비대화** | 파생 클래스가 새 메소드를 필요로 할 때마다 기반 클래스가 더 비대해진다 |

이것이 **인터페이스 오염(*interface pollution - 무관한 메소드들이 기반 인터페이스에 떠밀려 들어가는 현상*)**의 전형적 사례다. 정적 타입 언어(C++, Java)에서 흔히 발생하는 증후군이다.

---

## 3. 클라이언트가 인터페이스에 미치는 반대 작용

보통 우리는 "인터페이스 변경 → 사용자에 영향"이라는 한 방향만 생각한다. 그러나 **반대 방향으로 작용하는 힘**도 있다: **사용자가 인터페이스 변경을 불러일으킨다.**

### 3.1 시나리오: Timer 사용자가 여러 번 등록한다

`TimedDoor`를 보자. 문이 열렸음을 감지하면 `Timer.register`를 호출한다. 그런데 제한시간 초과 전에 문이 닫히고, 한참 뒤 다시 열린다. 이로 인해 **이전 요청이 끝나기 전에 새로운 요청**이 등록된다. 결국 첫 번째 등록의 `timeout`이 호출되어 잘못된 알람이 울린다.

이 문제를 해결하려면 각 등록에 고유의 `timeOutId`를 주고 `timeout` 호출에서 그 코드를 같이 받게 하면 된다.

<details>
<summary>원문 C++ 코드 (목록 12-3)</summary>

```cpp
// 목록 12-3: ID를 사용한 Timer
class Timer {
public:
    void Register(int timeout, int timeOutId, TimerClient* client);
};

class TimerClient {
public:
    virtual void TimeOut(int timeOutId) = 0;
};
```

</details>

```typescript
// TypeScript - timeOutId 지원
interface TimerClient {
    timeout(timeOutId: number): void;
}

class Timer {
    register(timeout: number, timeOutId: number, client: TimerClient): void {
        /* ... */
    }
}
```

### 3.2 변경이 일으키는 파급

이 변경은 명백히 `TimerClient`의 모든 사용자에 영향을 미친다 — 그건 어쩔 수 없다. 그러나 **2.3의 설계**(Door가 TimerClient를 상속)에서는 `Door`와 `Door`의 모든 클라이언트까지 영향을 받는다.

> **핵심 통찰**: 왜 `TimerClient`의 변경이 **타이머를 사용하지 않는** `Door` 파생 클래스의 클라이언트에까지 영향을 주어야 하는가? 프로그램 한 부분의 변경이 전혀 관계없는 부분에까지 영향을 줄 때, 이 변경에 드는 비용과 그 영향은 예상할 수 없을 정도가 되고 부작용의 위험성은 급격히 증가한다. 이것이 **경직성**과 **점착성**의 악취다.

이런 결합을 막기 위해 인터페이스를 분리한다.

---

## 4. 분리 기법 1 — 위임을 통한 분리 (Adapter)

`TimedDoor`는 2개의 분리된 클라이언트(`Timer`와 `Door`의 사용자)가 사용하는 2개의 분리된 인터페이스를 가져야 한다. 그런데 두 인터페이스의 구현은 같은 데이터를 조작하므로 같은 객체에서 구현되어야 한다. 어떻게 분리할까?

**객체의 클라이언트는 그 객체의 인터페이스를 통해 객체에 접근할 필요가 없다.** **위임**이나 **그 객체의 기반 클래스**를 통해 접근할 수 있다.

### 4.1 DoorTimerAdapter — Adapter 패턴 적용

`TimerClient`에서 파생된 객체를 생성하고 그 일을 `TimedDoor`에 위임한다.

```
   «interface»                 «interface»
   TimerClient                 Door
   ───────────                 ──────────
    timeout()                  lock()
       △                       unlock()
       │                       isDoorOpen()
       │                          △
   DoorTimerAdapter               │
   ─────────────────              │
    timeout()  ──────┐            │
                     │            │
                     └────▶ TimedDoor
                            ─────────────
                             doorTimeOut(id)
                «creates»
```

`TimedDoor`가 `Timer`에 등록할 때 `DoorTimerAdapter`를 생성해 등록한다. `Timer`가 `timeout`을 호출하면 `DoorTimerAdapter`가 그 호출을 `TimedDoor.doorTimeOut`으로 변환해 위임한다.

<details>
<summary>원문 C++ 코드 (목록 12-4)</summary>

```cpp
// 목록 12-4: TimedDoor.cpp
class TimedDoor : public Door {
public:
    virtual void DoorTimeOut(int timeOutId);
};

class DoorTimerAdapter : public TimerClient {
public:
    DoorTimerAdapter(TimedDoor& theDoor)
        : itsTimedDoor(theDoor) {}

    virtual void TimeOut(int timeOutId) {
        itsTimedDoor.DoorTimeOut(timeOutId);
    }
private:
    TimedDoor& itsTimedDoor;
};
```

</details>

```typescript
// TypeScript - 위임을 통한 분리
class TimedDoor implements Door {
    lock(): void { /* ... */ }
    unlock(): void { /* ... */ }
    isDoorOpen(): boolean { return false; }

    doorTimeOut(timeOutId: number): void {
        // TimedDoor 고유 로직 — 알람 울림
    }
}

class DoorTimerAdapter implements TimerClient {
    constructor(private readonly door: TimedDoor) {}

    timeout(timeOutId: number): void {
        this.door.doorTimeOut(timeOutId);
    }
}
```

### 4.2 위임의 장점과 비용

| 측면 | 평가 |
|------|------|
| ISP 준수 | `Door` 클라이언트가 `Timer`에 결합되지 않음 |
| `TimerClient` 변경의 격리 | 목록 12-3 같은 변경이 `Door` 사용자에 전혀 영향 없음 |
| 인터페이스 변환 가능 | `TimerClient` 인터페이스와 `TimedDoor` 인터페이스가 달라도 됨 |
| 비용 1 — 객체 생성 | 등록할 때마다 새 어댑터 객체 생성 |
| 비용 2 — 실행/메모리 | 위임 호출의 실행시간 + 메모리 소모 (영(zero)이 아님) |

> **Uncle Bob의 경험**: 이 해결책도 다소 세련되지는 못하다. 타이머 등록 때마다 새 객체를 생성하고, 위임 과정은 아주 작긴 하지만 영이 아닌(*nonzero - 0보다 큰*) 실행시간과 메모리를 요구한다. 임베디드 실시간 제어 시스템처럼 이런 자원이 부족한 영역에서는 분명히 문제가 될 수 있다.

---

## 5. 분리 기법 2 — 다중 상속을 통한 분리

`TimedDoor`가 `Door`와 `TimerClient`를 **모두 상속**받도록 한다. 두 기반 클래스의 클라이언트는 `TimedDoor`를 사용할 수 있지만 어느 쪽도 `TimedDoor` 자체에는 의존하지 않는다.

```
   «interface»                  «interface»
   TimerClient                  Door
   ───────────                  ──────────
    timeout()                   lock()
       △                        unlock()
       │                        isDoorOpen()
       │                           △
       │                           │
       └──────────┬────────────────┘
                  │
              TimedDoor
              ─────────────
               timeout(id)      ◀── TimerClient 구현
               lock()           ◀── Door 구현
               ...
```

<details>
<summary>원문 C++ 코드 (목록 12-5)</summary>

```cpp
// 목록 12-5: TimedDoor.cpp
class TimedDoor : public Door, public TimerClient {
public:
    virtual void TimeOut(int timeOutId);
};
```

</details>

```typescript
// TypeScript - 다중 인터페이스 구현
class TimedDoor implements Door, TimerClient {
    lock(): void { /* ... */ }
    unlock(): void { /* ... */ }
    isDoorOpen(): boolean { return false; }

    timeout(timeOutId: number): void {
        // TimerClient로서 받은 알림 처리 — 알람 울림
    }
}
```

### 5.1 위임 vs 다중 상속

> **Uncle Bob의 경험**: 나는 일반적인 상황에서 다중 상속 해결책(그림 12-3)을 선호한다. 위임(그림 12-2)을 선택하는 경우는 `DoorTimerAdapter` 객체가 행하는 **변환이 필수적이거나, 다양한 시간에 다양한 변환이 필요한 경우**뿐이다.

| 기준 | 위임 (Adapter) | 다중 상속 |
|------|----------------|------------|
| 자원 비용 | 객체 생성 + 위임 호출 | 거의 없음 |
| 인터페이스 변환 | 자유로움 | 동일 시그너처 강제 |
| 런타임 동적 교체 | 어댑터 교체로 가능 | 불가 |
| 권장 상황 | 변환이 필수적일 때 | 그 외 일반적 상황 |

TypeScript에서는 `implements`로 여러 인터페이스를 합성하는 것이 자연스러워, 자바·C++의 다중 상속 부담 없이 같은 효과를 얻을 수 있다.

---

## 6. ATM 사용자 인터페이스 예제

좀 더 의미 있는 예제로 가자. 전통적인 ATM(*automated teller machine - 현금 자동 지급기*) 문제다. ATM의 UI는 매우 유연해야 한다 — 다양한 언어로 번역되어야 하며, 스크린·점자판·음성 합성기로 출력될 수 있어야 한다.

### 6.1 트랜잭션 계층구조

ATM이 수행할 수 있는 각 트랜잭션을 `Transaction` 파생 클래스로 캡슐화한다: `DepositTransaction`, `WithdrawalTransaction`, `TransferTransaction`. 각 트랜잭션은 UI의 메소드를 호출한다.

### 6.2 나쁜 설계: 비대한 UI 인터페이스

```
            Transaction {abstract}
            ─────────────────────
                  execute()
                     △
       ┌─────────────┼─────────────┐
       │             │             │
   Deposit      Withdrawal     Transfer
   Transaction  Transaction    Transaction
       │             │             │
       └─────────────┼─────────────┘
                     ▼
              «interface»
                  UI
            ───────────────────────────
            requestDepositAmount()
            requestWithdrawalAmount()
            requestTransferAmount()
            informInsufficientFunds()
```

<details>
<summary>원문 C++ 스타일 코드</summary>

```cpp
class UI {
public:
    virtual void RequestDepositAmount() = 0;
    virtual void RequestWithdrawalAmount() = 0;
    virtual void RequestTransferAmount() = 0;
    virtual void InformInsufficientFunds() = 0;
};
```

</details>

```typescript
// TypeScript - 비대한 UI (ISP 위반)
interface UI {
    requestDepositAmount(): void;
    requestWithdrawalAmount(): void;
    requestTransferAmount(): void;
    informInsufficientFunds(): void;
}
```

### 6.3 위반의 폐해

이것이 바로 ISP가 피하라고 하는 상황이다. 각 트랜잭션은 다른 트랜잭션이 사용하지 않는 UI 메소드를 사용한다.

- `Transaction`의 어느 한 파생 클래스를 변경하면 → 대응하는 UI 메소드 변경 가능성 발생
- → `Transaction`의 **모든 파생 클래스**와 `UI`에 의존하는 모든 코드가 영향받음
- 예: `PayGasBillTransaction`을 추가하면 UI에 새 메소드를 추가 → `DepositTransaction`, `WithdrawalTransaction`, `TransferTransaction` 전부 재컴파일
- DLL/공유 라이브러리로 배포되었다면 **재배포까지** 강제됨 (내부 로직은 바뀐 게 없는데도)

이것이 **점착성(viscosity)의 악취**다.

### 6.4 좋은 설계: 클라이언트별 인터페이스 + 다중 상속

UI 인터페이스를 `DepositUI`, `WithdrawalUI`, `TransferUI` 같은 개별 인터페이스로 분리하고, 최종 `UI` 클래스가 이들을 다중 상속(또는 `implements`)한다.

```
   «interface»            «interface»             «interface»
   DepositUI              WithdrawalUI            TransferUI
   ─────────────────      ──────────────────      ──────────────────
   requestDeposit         requestWithdrawal       requestTransfer
   Amount()               Amount()                Amount()
                          informInsufficient
                          Funds()
        △                     △                       △
        │                     │                       │
   Deposit               Withdrawal               Transfer
   Transaction           Transaction              Transaction
        │                     │                       │
        └─────────────────────┼───────────────────────┘
                              ▼
                     ┌─────────────────┐
                     │       UI        │  implements
                     │ DepositUI,      │  WithdrawalUI,
                     │ TransferUI      │
                     └─────────────────┘
```

<details>
<summary>원문 C++ 코드 (목록 12-6)</summary>

```cpp
// 목록 12-6: 분리된 ATM UI 인터페이스
class DepositUI {
public:
    virtual void RequestDepositAmount() = 0;
};

class DepositTransaction : public Transaction {
public:
    DepositTransaction(DepositUI& ui) : itsDepositUI(ui) {}
    virtual void Execute() {
        itsDepositUI.RequestDepositAmount();
    }
private:
    DepositUI& itsDepositUI;
};

class WithdrawalUI {
public:
    virtual void RequestWithdrawalAmount() = 0;
    virtual void InformInsufficientFunds() = 0;
};

class WithdrawalTransaction : public Transaction {
public:
    WithdrawalTransaction(WithdrawalUI& ui) : itsWithdrawalUI(ui) {}
    virtual void Execute() {
        itsWithdrawalUI.RequestWithdrawalAmount();
    }
private:
    WithdrawalUI& itsWithdrawalUI;
};

class TransferUI {
public:
    virtual void RequestTransferAmount() = 0;
};

class TransferTransaction : public Transaction {
public:
    TransferTransaction(TransferUI& ui) : itsTransferUI(ui) {}
    virtual void Execute() {
        itsTransferUI.RequestTransferAmount();
    }
private:
    TransferUI& itsTransferUI;
};

class UI : public DepositUI, public WithdrawalUI, public TransferUI {
public:
    virtual void RequestDepositAmount();
    virtual void RequestWithdrawalAmount();
    virtual void RequestTransferAmount();
    virtual void InformInsufficientFunds();
};
```

</details>

```typescript
// TypeScript - 클라이언트별 인터페이스
interface DepositUI {
    requestDepositAmount(): void;
}

interface WithdrawalUI {
    requestWithdrawalAmount(): void;
    informInsufficientFunds(): void;
}

interface TransferUI {
    requestTransferAmount(): void;
}

abstract class Transaction {
    abstract execute(): void;
}

class DepositTransaction extends Transaction {
    constructor(private readonly ui: DepositUI) {
        super();
    }
    execute(): void {
        this.ui.requestDepositAmount();
    }
}

class WithdrawalTransaction extends Transaction {
    constructor(private readonly ui: WithdrawalUI) {
        super();
    }
    execute(): void {
        this.ui.requestWithdrawalAmount();
    }
}

class TransferTransaction extends Transaction {
    constructor(private readonly ui: TransferUI) {
        super();
    }
    execute(): void {
        this.ui.requestTransferAmount();
    }
}

// 통합 UI — 분리된 인터페이스들을 모두 구현
class ATMUI implements DepositUI, WithdrawalUI, TransferUI {
    requestDepositAmount(): void { /* ... */ }
    requestWithdrawalAmount(): void { /* ... */ }
    requestTransferAmount(): void { /* ... */ }
    informInsufficientFunds(): void { /* ... */ }
}
```

`Transaction`의 새 파생 클래스가 만들어질 때마다 대응하는 UI 인터페이스의 기반 클래스가 필요하다. 그러나 이런 클래스는 널리 사용되지 않는다 — 보통 `main`이나 시스템 시작 시점에서 구체 인스턴스를 만들 때만 쓰인다. **따라서 새 UI 기반 클래스를 추가하는 충격은 최소화된다.**

---

## 7. 인터페이스 초기화와 전역 변수

### 7.1 각 트랜잭션이 특정 UI 참조를 보유

목록 12-6에서는 각 트랜잭션이 자신의 특정 UI에 대한 참조를 받아 생성된다.

```typescript
const gui = new ATMUI();
const dt = new DepositTransaction(gui);
```

쓰기 편하지만 각 트랜잭션 내부에 UI 참조 멤버를 보유해야 한다.

### 7.2 전역 참조 묶음 — 또 다른 해법

전역 상수 묶음을 만들 수도 있다. 전역 변수가 항상 어설픈 설계의 징후는 아니다 — 이 경우 쉬운 접근이라는 분명한 이점을 제공하고, 참조는 변경 불가능하므로 다른 사용자를 놀라게 할 수도 없다.

<details>
<summary>원문 C++ 코드 (목록 12-8)</summary>

```cpp
// 분리된 전역 포인터
static UI Lui;  // 비전역 객체
DepositUI&    GdepositUI    = Lui;
WithdrawalUI& GwithdrawalUI = Lui;
TransferUI&   GtransferUI   = Lui;

class WithdrawalTransaction : public Transaction {
public:
    virtual void Execute() {
        GwithdrawalUI.RequestWithdrawalAmount();
    }
};
```

</details>

```typescript
// TypeScript - 분리된 전역 참조
const _ui = new ATMUI();
export const depositUI:    DepositUI    = _ui;
export const withdrawalUI: WithdrawalUI = _ui;
export const transferUI:   TransferUI   = _ui;
```

### 7.3 절대 하지 말아야 할 것 — 전역들을 한 클래스에 묶기

전역 네임스페이스 오염을 막으려고 모든 전역을 `UIGlobals` 같은 한 클래스에 넣고 싶은 유혹이 든다. **그러나 이것은 비참한 결과를 낳는다.**

<details>
<summary>원문 C++ 코드 (목록 12-9)</summary>

```cpp
// ui_globals.h
#include "depositUI.h"
#include "withdrawalUI.h"
#include "transferUI.h"

class UIGlobals {
public:
    static WithdrawalUI& withdrawal;
    static DepositUI&    deposit;
    static TransferUI&   transfer;
};
```

</details>

`UIGlobals`를 쓰려면 `ui_globals.h`를 포함해야 하고, 이 헤더는 `depositUI.h`, `withdrawalUI.h`, `transferUI.h`를 모두 포함한다. 즉 **UI 인터페이스 중 어느 하나라도 쓰려는 모듈은 이행적으로 모든 인터페이스에 의존하게 된다.** 어느 UI 인터페이스라도 변경되면 `UIGlobals`를 포함한 모든 모듈이 재컴파일되어야 한다.

> **핵심 통찰**: `UIGlobals` 클래스는 **분리하려고 그렇게 애썼던 인터페이스를 다시 결합시켜 버린다.** ISP 위반은 종종 "편의를 위한 한곳 모음" 형태로 슬그머니 되돌아온다.

---

## 8. 복합체와 단일체 — 함수 시그너처 선택

어떤 함수 `g`가 `DepositUI`와 `TransferUI` 둘 다 접근해야 한다고 하자. 다음 중 어느 시그너처가 좋은가?

```typescript
// (A) 복합형 — 인터페이스별 매개변수
function g(d: DepositUI, t: TransferUI): void { /* ... */ }

// (B) 단일형 — 통합 UI 하나
function g(ui: ATMUI): void { /* ... */ }
```

(A)는 같은 객체를 두 번 넘기게 되어 `g(ui, ui)` 같은 호출이 이상해 보인다. 그러나 **대개 (A) 복합형이 (B) 단일형보다 바람직하다.**

| 시그너처 | 의존성 | 결과 |
|---------|--------|------|
| (B) 단일 `UI` | UI 안의 모든 인터페이스에 의존 | `WithdrawalUI`가 바뀌면 `g`와 `g`의 모든 클라이언트가 영향받음 |
| (A) 복합 매개변수 | 정확히 필요한 두 인터페이스에만 의존 | `WithdrawalUI` 변경이 `g`에 영향 안 줌 |

또한 (B)는 두 인자가 항상 같은 객체임을 단정하게 만들지만, 나중에 객체가 분리될 수도 있다. **모든 인터페이스가 하나의 객체에 결합되어 있다는 사실은 `g`가 알 필요가 없는 정보**다.

---

## 9. 클라이언트 그룹 만들기

클라이언트는 종종 자신이 호출하는 서비스 메소드에 의해 그룹으로 묶일 수 있다. 이런 그룹에 대해 분리된 인터페이스를 만들면, 각 서비스가 구현해야 하는 인터페이스 수가 줄어들 뿐 아니라 그 서비스가 각 클라이언트 형(type)에 의존하게 되는 일도 막을 수 있다.

> **핵심 통찰**: 인터페이스는 **개별 클라이언트가 아니라 클라이언트 그룹** 단위로 분리하라. 그룹 간 메소드가 겹쳐도 겹치는 부분이 작으면 인터페이스를 분리된 상태로 두고, 공통 함수는 각 인터페이스에 한 번씩 선언한다. 서버 클래스는 이들 모두를 상속받지만 구현은 한 번만 한다.

---

## 10. 인터페이스 변경 — 기존 인터페이스를 깨지 말고 새 인터페이스를 추가하라

객체지향 애플리케이션을 유지보수할 때 기존 클래스·컴포넌트의 인터페이스가 종종 변경된다. 이런 변경이 큰 영향을 미쳐, 시스템 큰 부분의 재컴파일·재배포가 필요해질 때가 있다.

이 충격을 완화하려면 **기존 인터페이스를 변경하는 것이 아니라 기존 객체에 새로운 인터페이스를 추가**하면 된다. 새 메소드에 접근하려는 클라이언트는 객체에 그 인터페이스에 대해 질의(query)할 수 있다.

<details>
<summary>원문 C++ 코드 (목록 12-10)</summary>

```cpp
void Client(Service* s) {
    if (NewService* ns = dynamic_cast<NewService*>(s)) {
        // 새로운 서비스 인터페이스 사용
    }
}
```

</details>

```typescript
// TypeScript - 새 인터페이스 추가 후 type guard로 질의
interface Service {
    doOriginal(): void;
}

interface NewService extends Service {
    doNew(): void;
}

function isNewService(s: Service): s is NewService {
    return typeof (s as NewService).doNew === "function";
}

function client(s: Service): void {
    if (isNewService(s)) {
        s.doNew();
    } else {
        s.doOriginal();
    }
}
```

> **Uncle Bob의 경험**: 모든 원칙은 지나치지 않도록 세심한 주의가 필요하다. 몇몇은 클라이언트에 의해 분리되고 나머지는 버전에 의해 분리되는 **수백 개의 인터페이스를 갖는 클래스**에 대한 공포는 정말 무시무시할 것이다.

---

## 11. 자주 하는 실수

| 안티패턴 | 문제 | 해결 |
|----------|------|------|
| **비대한 단일 인터페이스** — 모든 메소드를 하나의 기반 클래스/인터페이스에 몰아넣음 | 무관한 클라이언트끼리 결합, 모두가 서로의 변경에 흔들림 | 클라이언트 그룹별 인터페이스로 분리 후 다중 상속(`implements`) |
| **퇴화 구현(빈 메소드)** — 필요 없는 메소드를 빈 구현으로 채움 | LSP 위반 위험, 클라이언트가 호출했을 때 침묵의 실패 | 메소드를 다른 인터페이스로 분리해 애초에 상속받지 않게 함 |
| **이행적 의존을 만드는 전역 묶음** — `UIGlobals` 식으로 분리된 인터페이스를 한 헤더/모듈에 다시 합침 | 분리해 둔 인터페이스가 재결합 — ISP 효과 무력화 | 인터페이스마다 별도 import/export, 묶음 헤더 금지 |
| **단일형 인자(`g(UI&)`)** — 편의상 통합 인터페이스 하나로 함수를 받음 | `g`가 모든 하위 인터페이스에 의존 — 무관한 변경에 영향받음 | 필요한 인터페이스만 매개변수로 받는 복합형 시그너처 |
| **이른 분리** — 변경 증상이 없는데 수십 개로 쪼개기 | 인터페이스 수 폭증, 매핑·등록 부담, 가독성 저하 | 클라이언트 그룹의 변경 축이 실제로 드러날 때 분리 |
| **상속만으로 끌어오기** — 필요한 메소드 한 개 때문에 무관한 기반 클래스를 상속 | 인터페이스 오염 시작점 | 위임(Adapter) 또는 별도 인터페이스로 다중 상속 |

---

## 12. 설계 원칙

| 원칙 | 설명 |
|------|------|
| **클라이언트가 분리되면 인터페이스도 분리하라** | 서로 다른 클라이언트 그룹은 자신만의 인터페이스를 가져야 함 |
| **객체 인터페이스 ≠ 클래스 인터페이스** | 같은 객체라도 클라이언트는 위임/기반 클래스를 통해 분리된 인터페이스로 접근 가능 |
| **위임은 변환·동적 교체용, 다중 상속이 기본** | 자원·인터페이스 변환이 필수일 때만 위임, 그 외에는 다중 상속(`implements`) |
| **클라이언트 그룹 단위로 분리** | 모든 클라이언트마다가 아닌, 메소드 사용 패턴이 비슷한 그룹별로 인터페이스 작성 |
| **묶음 헤더/네임스페이스 금지** | 분리된 인터페이스를 한곳에 모으면 이행적 의존이 부활 — ISP가 무효화됨 |
| **함수 시그너처도 ISP를 따른다** | 함수가 필요로 하는 정확한 인터페이스만 매개변수로 받음 (복합형 선호) |
| **변경은 추가로, 수정 아니라** | 기존 인터페이스를 깨지 말고 새 인터페이스를 추가한 뒤 type guard로 질의 |

---

## 13. 결론

비대한 클래스는 클라이언트들 간에 **기이하고 해로운 결합**을 유발한다. 한 클라이언트가 비대한 클래스에 변경을 가하면 모든 나머지 클라이언트가 영향받는다. 그러므로 클라이언트는 자신이 실제로 호출하는 메소드에만 의존해야 한다.

그러려면 비대한 클래스의 인터페이스를 **클라이언트 고유의(client-specific) 인터페이스 여러 개**로 분해해야 한다. 각 인터페이스는 자신의 특정한 클라이언트나 클라이언트 그룹이 호출하는 함수만 선언한다. 그 다음 비대한 클래스가 모든 클라이언트 고유 인터페이스를 상속(또는 `implements`)하고 구현한다.

이렇게 하면:
- 호출하지 않는 메소드에 대한 클라이언트의 의존성을 끊고
- 클라이언트가 서로에 대해 독립적이 된다

> **핵심 통찰**: ISP는 SRP의 **인터페이스 차원 표현**이다. SRP가 "한 클래스에 한 책임"을 말한다면, ISP는 "**한 인터페이스에 한 클라이언트 그룹**"을 말한다. 결합은 종종 인터페이스를 통해 전파되므로, 인터페이스를 책임/클라이언트 단위로 자르는 것이 시스템의 변경 비용을 결정한다.

---

## 요약

- **ISP의 정의**: 클라이언트는 자신이 사용하지 않는 메소드에 의존하도록 강제되어서는 안 된다
- **비대한 인터페이스의 폐해**:
  - 무관한 클라이언트끼리 의도하지 않은 결합
  - 한 클라이언트 때문에 인터페이스가 바뀌면 모든 클라이언트가 재컴파일·재배포
  - 퇴화 구현 강요로 LSP 잠재 위반
- **분리 기법 두 가지**:
  1. **위임(Adapter)** — 변환이 필수적이거나 동적 교체가 필요할 때
  2. **다중 상속/`implements`** — 일반 상황의 기본 선택 (Uncle Bob 선호)
- **클라이언트 단위가 아닌 클라이언트 그룹 단위로 분리하라** — 너무 잘게 쪼개면 인터페이스 폭증
- **분리된 인터페이스를 다시 묶지 마라** — `UIGlobals` 식 묶음 클래스/헤더는 ISP 효과를 무력화
- **함수 시그너처에도 적용** — 단일형 `g(UI)`보다 복합형 `g(DepositUI, TransferUI)`가 의존성을 최소화
- **변경은 추가로** — 기존 인터페이스를 수정하지 말고 새 인터페이스를 추가한 뒤 type guard로 질의
- ISP는 SRP의 인터페이스 차원 표현 — 결합은 인터페이스를 따라 전파되며, 인터페이스 분리가 시스템 변경 비용을 결정한다
