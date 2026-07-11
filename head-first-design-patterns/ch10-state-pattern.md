# Chapter 10: The State Pattern (상태 패턴)

## 핵심 질문

- 상태에 따라 동작이 완전히 달라지는 객체를, **거대한 `if/switch` 조건문 없이** 어떻게 만들까?
- 새 상태를 추가할 때 **기존 코드를 최소한만** 건드리려면(OCP)?
- 클래스 다이어그램이 똑같은 **전략 패턴과 상태 패턴**은 무엇이 다른가?

---

## 1. 뽑기 기계 — 상태 다이어그램

주식회사 왕뽑기의 뽑기 기계는 4개 상태와 전환을 가진다.

```
        동전 투입          손잡이 돌림
 [동전 없음] ──────▶ [동전 있음] ──────▶ [알맹이 판매]
     ▲   ◀──────         │  알맹이 내보냄  │
     │    동전 반환        │       ┌─────────┘
     └───────────────────┘       ▼ 알맹이>0 → 동전 없음 / 알맹이=0 → 매진
                              [매진]
```

---

## 2. 첫 시도 (나쁜 예) — 정수 상태 + 조건문

```typescript
class GumballMachine {
  static readonly SOLD_OUT = 0;
  static readonly NO_QUARTER = 1;
  static readonly HAS_QUARTER = 2;
  static readonly SOLD = 3;

  private state = GumballMachine.SOLD_OUT;

  insertQuarter(): void {
    if (this.state === GumballMachine.HAS_QUARTER) {
      console.log("동전은 한 개만 넣어주세요.");
    } else if (this.state === GumballMachine.NO_QUARTER) {
      this.state = GumballMachine.HAS_QUARTER;
      console.log("동전이 투입되었습니다.");
    } else if (this.state === GumballMachine.SOLD_OUT) {
      console.log("매진되었습니다.");
    } else if (this.state === GumballMachine.SOLD) {
      console.log("알맹이를 내보내고 있습니다.");
    }
  }
  // ejectQuarter(), turnCrank(), dispense()에도 똑같은 4갈래 조건문 반복...
}
```

동작은 하지만, **"당첨(WINNER) 상태"를 추가**해 달라는 요청이 오면 재앙이 된다.

> **핵심 통찰**: 새 상태를 추가하려면 **모든 메서드의 조건문을 다 고쳐야** 한다 → OCP 위반, 상태 전환이 조건문 속에 숨어 불분명, 새 버그 유발. 바뀌는 부분(상태별 행동)이 캡슐화되지 않았다.

---

## 3. 상태 패턴 — 상태를 객체로

각 상태를 **클래스**로 만들고, 뽑기 기계는 **현재 상태 객체에 행동을 위임**한다.

```typescript
/** 모든 상태가 구현하는 인터페이스 — 뽑기 기계의 모든 행동에 대응. */
interface State {
  insertQuarter(): void;
  ejectQuarter(): void;
  turnCrank(): void;
  dispense(): void;
}
```

```typescript
class NoQuarterState implements State {
  constructor(private machine: GumballMachine) {}

  insertQuarter(): void {
    console.log("동전을 넣으셨습니다.");
    this.machine.setState(this.machine.getHasQuarterState()); // 상태 전환
  }
  ejectQuarter(): void { console.log("동전을 넣어 주세요."); }
  turnCrank(): void { console.log("동전을 넣어 주세요."); }
  dispense(): void { console.log("동전을 넣어 주세요."); }
}

class HasQuarterState implements State {
  constructor(private machine: GumballMachine) {}

  insertQuarter(): void { console.log("동전은 한 개만 넣어 주세요."); }
  ejectQuarter(): void {
    console.log("동전이 반환됩니다.");
    this.machine.setState(this.machine.getNoQuarterState());
  }
  turnCrank(): void {
    console.log("손잡이를 돌리셨습니다.");
    this.machine.setState(this.machine.getSoldState());
  }
  dispense(): void { console.log("알맹이를 내보낼 수 없습니다."); }
}

class SoldState implements State {
  constructor(private machine: GumballMachine) {}

  insertQuarter(): void { console.log("알맹이를 내보내고 있습니다."); }
  ejectQuarter(): void { console.log("이미 알맹이를 뽑으셨습니다."); }
  turnCrank(): void { console.log("손잡이는 한 번만 돌려 주세요."); }
  dispense(): void {
    this.machine.releaseBall();
    if (this.machine.getCount() > 0) {
      this.machine.setState(this.machine.getNoQuarterState());
    } else {
      console.log("Oops, 알맹이가 없습니다!");
      this.machine.setState(this.machine.getSoldOutState());
    }
  }
}
```

뽑기 기계(Context)는 상태 객체들을 보유하고, 요청을 현재 상태에 위임한다.

```typescript
class GumballMachine {
  private soldOutState: State;
  private noQuarterState: State;
  private hasQuarterState: State;
  private soldState: State;

  private state: State;
  private count: number;

  constructor(numberGumballs: number) {
    this.soldOutState = new SoldOutState(this);
    this.noQuarterState = new NoQuarterState(this);
    this.hasQuarterState = new HasQuarterState(this);
    this.soldState = new SoldState(this);
    this.count = numberGumballs;
    this.state = numberGumballs > 0 ? this.noQuarterState : this.soldOutState;
  }

  // 조건문이 사라지고, 현재 상태에 위임만 한다
  insertQuarter(): void { this.state.insertQuarter(); }
  ejectQuarter(): void { this.state.ejectQuarter(); }
  turnCrank(): void {
    this.state.turnCrank();
    this.state.dispense();
  }

  setState(state: State): void { this.state = state; }
  releaseBall(): void {
    console.log("알맹이를 내보내고 있습니다.");
    if (this.count > 0) { this.count--; }
  }
  getCount(): number { return this.count; }
  getNoQuarterState(): State { return this.noQuarterState; }
  getHasQuarterState(): State { return this.hasQuarterState; }
  getSoldState(): State { return this.soldState; }
  getSoldOutState(): State { return this.soldOutState; }
}
```

<details>
<summary>Java 원본 (HasQuarterState)</summary>

```java
public class HasQuarterState implements State {
    GumballMachine gumballMachine;
    public HasQuarterState(GumballMachine gumballMachine) {
        this.gumballMachine = gumballMachine;
    }
    public void insertQuarter() {
        System.out.println("동전은 한 개만 넣어 주세요.");
    }
    public void ejectQuarter() {
        System.out.println("동전이 반환됩니다.");
        gumballMachine.setState(gumballMachine.getNoQuarterState());
    }
    public void turnCrank() {
        System.out.println("손잡이를 돌리셨습니다.");
        gumballMachine.setState(gumballMachine.getSoldState());
    }
    public void dispense() {
        System.out.println("알맹이를 내보낼 수 없습니다.");
    }
}
```
</details>

> **패턴 정의 — 상태 패턴 (State Pattern)**<br>객체의 내부 상태가 바뀜에 따라서 객체의 행동을 바꿀 수 있다. 마치 객체의 클래스가 바뀌는 것과 같은 결과를 얻는다.

```
     Context ──state──▶ «interface» State
     request()          handle()
     (state.handle())        △
                    ┌────────┼────────┐
              ConcreteStateA  ...  ConcreteStateB
```

이 리팩터링으로 얻은 것:
- 각 상태의 행동을 **별개 클래스로 국지화**
- 관리 힘든 `if` 조건문 제거
- 각 상태는 **변경에 닫혀 있고**, 기계는 새 상태 추가라는 **확장에 열려 있다**(OCP)
- 원래 상태 다이어그램에 훨씬 가까운 코드

---

## 4. 새 상태 추가 — WinnerState

"10번에 1번 알맹이 2개" 기능을 추가한다. **새 클래스 하나 + 전환 코드만** 추가하면 된다(기존 상태들은 거의 안 건드림).

```typescript
class WinnerState implements State {
  constructor(private machine: GumballMachine) {}
  // insert/eject/turnCrank는 SoldState와 동일 (부적절 메시지)
  dispense(): void {
    this.machine.releaseBall();
    if (this.machine.getCount() === 0) {
      this.machine.setState(this.machine.getSoldOutState());
    } else {
      this.machine.releaseBall(); // 알맹이 하나 더!
      console.log("축하드립니다! 알맹이를 하나 더 받으실 수 있습니다.");
      this.machine.setState(
        this.machine.getCount() > 0
          ? this.machine.getNoQuarterState()
          : this.machine.getSoldOutState(),
      );
    }
  }
}

// HasQuarterState의 turnCrank에서 10% 확률로 WinnerState로 전환
turnCrank(): void {
  const winner = Math.floor(Math.random() * 10); // 0~9
  if (winner === 0 && this.machine.getCount() > 1) {
    this.machine.setState(this.machine.getWinnerState());
  } else {
    this.machine.setState(this.machine.getSoldState());
  }
}
```

> **핵심 통찰**: 첫 설계(조건문)였다면 4개 메서드를 다 고쳐야 했지만, 상태 패턴에서는 **클래스 하나 추가 + 전환점 한 곳 수정**으로 끝난다. 이것이 상태를 객체로 캡슐화한 보상이다.

---

## 5. 전략 패턴 vs 상태 패턴

> 방구석 토크 — 두 쌍둥이의 대화<br><br>**전략**: 우리 둘, 클래스 다이어그램이 똑같잖아. 하는 일도 같은 거 아냐?<br>**상태**: 구조는 같아도 **목적**이 완전히 달라. 너(전략)는 **클라이언트가 어떤 전략을 쓸지 지정**하지. 나(상태)는 **Context가 내부 규칙에 따라 스스로 상태를 바꿔** — 클라이언트는 상태를 몰라도 돼.

| 구분 | 전략 패턴(1장) | 상태 패턴(이 장) |
|------|--------------|-----------------|
| 클래스 다이어그램 | **동일** | **동일** |
| 누가 행동을 정하나 | **클라이언트**가 전략을 지정 | **Context**가 내부 상태에 따라 전환 |
| 전환 | 보통 외부에서 교체 | 상태들이 **스스로 다음 상태 결정** |
| 목적 | 서브클래싱 대신 **알고리즘 교체** | **조건문 지옥**을 상태 객체로 대체 |
| 상태/전략 개수 | 보통 하나를 골라 씀 | 정해진 여러 상태를 오가며 씀 |

> **핵심 통찰**: **"수많은 조건문 대신 상태 패턴"**, **"서브클래싱 대신 전략 패턴"**으로 기억하면 된다. 구조는 같아도 의도가 다르다.

---

## 6. TS/JS 관점 — 상태 머신은 프런트의 일상

> **핵심 통찰**: UI는 본질적으로 상태 머신이다(로딩/성공/에러, 폼의 입력중/제출중/완료 등). 프런트엔드에서는 상태 패턴의 정신이 **판별 유니언(discriminated union)** 이나 **XState** 같은 상태 머신 라이브러리로 구현되는 경우가 많다.

```typescript
// 판별 유니언으로 "불가능한 상태를 불가능하게" 만드는 방식
type FetchState<T> =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: T }
  | { status: "error"; error: Error };

function render(state: FetchState<User>): string {
  // status에 따라 컴파일러가 접근 가능한 필드를 좁혀준다
  switch (state.status) {
    case "idle": return "대기 중";
    case "loading": return "불러오는 중...";
    case "success": return state.data.name; // data 접근 가능
    case "error": return state.error.message; // error 접근 가능
  }
}
```

> 클래스 기반 상태 패턴은 "상태별 행동이 많고 전환 규칙이 복잡할 때" 유리하고, 판별 유니언은 "상태에 따라 데이터 형태가 다를 때" 타입 안전성 면에서 유리하다. 규모가 커지면 **XState**로 상태·전환·부수효과를 선언적으로 관리한다.

---

## 연습 문제 (해답 예시)

**1. 첫 설계(조건문)의 문제점** — OCP 위반(A), 상태 전환이 조건문에 숨음(D), 바뀌는 부분 미캡슐화(E), 새 버그 위험(F). (포트란식 절차적 코드 B도 해당.)

**2. `SoldOutState` 구현** — 알맹이가 없으므로 모든 행동이 "매진/불가" 메시지. `refill()` 시에만 `NoQuarterState`로 전환.

**3. `dispense()`가 항상 호출되는 문제** — `turnCrank()`가 `dispense()`를 무조건 부른다(동전 없이 돌려도). `turnCrank()`가 boolean을 반환하거나 예외를 쓰도록 개선할 수 있다.

**4. `WinnerState`를 따로 둘까, `SoldState`에 합칠까?** — 합치면 코드 중복은 줄지만 `SoldState`가 두 역할(당첨/일반)을 갖게 되어 **단일 책임 원칙(9장) 위반**. 행사 종료·확률 변경 등을 고려하면 분리가 낫다 — 상황에 맞는 트레이드오프.

**5. `refill()` 추가** — `State`에 `refill()`을 넣고, `SoldOutState`만 `NoQuarterState`로 전환(나머지는 무동작). `GumballMachine.refill(n)`은 개수를 늘리고 현재 상태의 `refill()` 호출.

---

## 디자인 원칙 정리 (누적)

이 장에서는 **새 원칙이 추가되지 않는다**. 상태 패턴은 기존 원칙(캡슐화·구성·OCP·단일 책임)의 종합 응용이다.

1~9번 원칙은 그대로: 캡슐화 / 인터페이스 / 구성 / 느슨한 결합 / OCP / DIP / 최소 지식 / 할리우드 / 단일 책임.

---

## 요약

- **상태 패턴**은 상태별 행동을 **각각의 상태 클래스**로 캡슐화하고, Context가 **현재 상태 객체에 행동을 위임**한다. 내부 상태가 바뀌면 행동도 바뀐다.
- 거대한 **조건문(`if/switch`) 지옥**을 없애고, 새 상태 추가를 **클래스 추가 + 전환점 수정**으로 국지화한다(OCP).
- 상태 전환은 **상태 클래스**가 결정할 수도, **Context**가 결정할 수도 있다(트레이드오프).
- **전략 패턴과 다이어그램은 같지만** 목적이 다르다: 전략=클라이언트가 알고리즘 지정, 상태=Context가 내부적으로 상태 전환.
- 단점: 클래스 수가 늘어난다(유연성의 대가). TS/JS에서는 **판별 유니언·XState**로 상태 머신을 표현하기도 한다.

---

## 다른 챕터와의 관계

- **1장 전략**: 클래스 구조가 동일한 "쌍둥이" 패턴. 목적으로 구분한다(위 비교표).
- **9장 단일 책임**: `WinnerState`를 분리할지 논의에서 이 원칙이 판단 기준이 된다.
- **11장 프록시**: 다음 장에서 이 뽑기 기계에 원격 모니터링(프록시)을 붙인다("11장에서 만나요"라는 예고).

---

## 보너스: 원서 복습 요소

### 🧩 디자인 퍼즐 — 당첨 상태 다이어그램

"동전 있음"에서 손잡이를 돌릴 때 **당첨(10%)**이면 알맹이 2개를 내보내고, 아니면 일반 판매. 알맹이가 0이면 매진으로 전환.

### 🧠 뇌 단련 (Brain Power)

1. 동전 없이 손잡이를 돌려도 `dispense()`가 호출되는 문제를 어떻게 막을까? (→ `turnCrank`가 성공 여부 반환)
2. 여러 `GumballMachine` 인스턴스가 상태 객체를 **공유**하려면? (→ 상태를 정적 인스턴스로, `handle()`에 Context 전달)

### 🎙️ 방구석 토크 — 전략 vs 상태

- 전략: 클라이언트가 전략 지정, 실행 중 유연 교체(상속 대체).
- 상태: Context가 정해진 전환 규칙에 따라 스스로 상태 변경(조건문 대체).

### 📝 낱말 퀴즈 (정답 단어 모음)

10장 용어들(정답은 영어): STATE(상태), CONTEXT(Context), GUMBALL(뽑기), WINNER(당첨), TRANSITION(전환), STRATEGY(전략), COMPOSITION(구성), DELEGATE(위임), ENCAPSULATE(캡슐화), NOQUARTER/HASQUARTER/SOLD/SOLDOUT(각 상태).
