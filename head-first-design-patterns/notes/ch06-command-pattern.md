# Chapter 06: The Command Pattern (커맨드 패턴)

## 핵심 질문

- "무언가를 **요청하는 객체**"와 "그 요청을 **실제로 처리하는 객체**"를 어떻게 완전히 분리할까?
- 서로 인터페이스가 제각각인 수많은 기기를, 버튼 하나로 어떻게 일관되게 제어할까?
- 요청을 **객체로 캡슐화**하면 무엇이 가능해지는가? (실행 취소·큐·로그·매크로)

---

## 1. 문제 — 홈오토메이션 리모컨

7개의 슬롯(각 ON/OFF 버튼) + UNDO 버튼을 가진 리모컨 API를 만들어야 한다. 문제는 제어할 협력 업체 클래스들이 **공통 인터페이스가 없다**는 것이다: `Light.on()/off()`, `Stereo.on()/setCd()/setVolume()`, `Hottub.jetsOn()/setTemperature()`, `GarageDoor.up()/down()`... 게다가 앞으로 기기가 더 추가된다.

> 나쁜 설계: 리모컨 안에 `if (슬롯1 == 조명) light.on(); else if (슬롯1 == 욕조) hottub.jetsOn(); ...`처럼 짜면, 기기가 추가될 때마다 리모컨 코드를 고쳐야 한다.

---

## 2. 객체마을 식당 비유

커맨드 패턴의 등장인물은 식당에 다 있다.

```
 고객 ──주문──▶ 종업원 ──orderUp()──▶ 주방장
(클라이언트)    (인보커)   주문서(커맨드)   (리시버)
```

- **주문서(Order)** = 커맨드. 주문 내용을 캡슐화하고, `orderUp()` 하나만 노출한다.
- **종업원(Waitress)** = 인보커. 주문서를 받아 `orderUp()`을 호출할 뿐, 무슨 요리인지·누가 만드는지 모른다.
- **주방장(Cook)** = 리시버. 실제로 요리하는 법을 아는 유일한 존재.

> **핵심 통찰**: 종업원과 주방장은 **주문서 덕분에 완전히 분리**된다. 종업원은 `orderUp()`만 알면 되고, 주방장은 주문서로 할 일을 전달받는다. 서로 직접 대화하지 않는다.

| 객체마을 식당 | 커맨드 패턴 |
|--------------|------------|
| 고객 | 클라이언트(Client) |
| 주문서 | 커맨드 객체(Command) |
| `orderUp()` | `execute()` |
| 종업원 | 인보커(Invoker) |
| `takeOrder()` | `setCommand()` |
| 주방장 | 리시버(Receiver) |

---

## 3. 커맨드 인터페이스와 첫 커맨드

```typescript
/** 모든 커맨드가 구현하는 인터페이스. */
interface Command {
  /** 요청을 실행한다. */
  execute(): void;
}

/** 조명을 켜는 커맨드 — 리시버(Light)와 행동(on)을 묶는다. */
class LightOnCommand implements Command {
  constructor(private light: Light) {}

  execute(): void {
    this.light.on(); // 리시버에 위임
  }
}
```

인보커(간단 버전)는 슬롯에 커맨드를 담고, 버튼이 눌리면 `execute()`만 호출한다.

```typescript
class SimpleRemoteControl {
  private slot!: Command;

  setCommand(command: Command): void {
    this.slot = command;
  }

  buttonWasPressed(): void {
    this.slot.execute(); // 무슨 일이 일어나는지 모른 채 실행만
  }
}

// 클라이언트
const remote = new SimpleRemoteControl();
const light = new Light();
remote.setCommand(new LightOnCommand(light));
remote.buttonWasPressed(); // 조명이 켜졌습니다
```

<details>
<summary>Java 원본</summary>

```java
public interface Command {
    void execute();
}

public class LightOnCommand implements Command {
    Light light;
    public LightOnCommand(Light light) {
        this.light = light;
    }
    public void execute() {
        light.on();
    }
}

public class SimpleRemoteControl {
    Command slot;
    public void setCommand(Command command) {
        slot = command;
    }
    public void buttonWasPressed() {
        slot.execute();
    }
}
```
</details>

> **패턴 정의 — 커맨드 패턴 (Command Pattern)**<br>요청 내역을 객체로 캡슐화해서, 서로 다른 요청 내역에 따라 클라이언트를 매개변수화한다. 이로써 요청을 큐에 저장하거나, 로그로 기록하거나, 작업 취소 기능을 사용할 수 있다.

```
 Client ──▶ Invoker ──execute()──▶ Command ──action()──▶ Receiver
           setCommand()         «interface»
                              ConcreteCommand
                              (리시버+행동을 보유)
```

---

## 4. 7슬롯 리모컨과 NoCommand (널 객체)

```typescript
class RemoteControl {
  private onCommands: Command[] = [];
  private offCommands: Command[] = [];

  constructor() {
    const noCommand = new NoCommand(); // 기본값: 아무 일도 안 하는 커맨드
    for (let i = 0; i < 7; i++) {
      this.onCommands[i] = noCommand;
      this.offCommands[i] = noCommand;
    }
  }

  setCommand(slot: number, onCommand: Command, offCommand: Command): void {
    this.onCommands[slot] = onCommand;
    this.offCommands[slot] = offCommand;
  }

  onButtonWasPushed(slot: number): void {
    this.onCommands[slot].execute();
  }
  offButtonWasPushed(slot: number): void {
    this.offCommands[slot].execute();
  }
}

/** 널 객체(Null Object) — 아무 일도 하지 않는 커맨드. */
class NoCommand implements Command {
  execute(): void {}
}
```

> **핵심 통찰**: `NoCommand`는 **널 객체(Null Object)** 다. 슬롯에 명령이 아직 없어도 `execute()` 호출이 안전하도록, `null` 검사 대신 "아무 일도 안 하는 객체"를 기본값으로 둔다. 널 객체도 일종의 디자인 패턴으로 분류하기도 한다.

---

## 5. TS/JS 관점 — 함수가 곧 커맨드

> **핵심 통찰**: 자바스크립트는 **함수가 일급 객체**라, 커맨드가 하나의 연산(`execute`)만 필요하면 **함수 자체가 커맨드**가 된다. 자바 8의 람다도 같은 이유로 구상 커맨드 클래스를 없앨 수 있다.

```typescript
// 커맨드가 execute 하나뿐이면, 클래스 대신 함수로 충분하다
type Command = () => void;

const remote = new Map<number, Command>();
const light = new Light();
remote.set(0, () => { light.on(); });   // LightOnCommand 클래스가 사라진다
remote.get(0)?.();                       // 조명이 켜졌습니다
```

<details>
<summary>Java 람다 버전</summary>

```java
// 구상 커맨드 클래스(LightOnCommand 등)를 지우고 람다로
remoteControl.setCommand(0,
    () -> livingRoomLight.on(),
    () -> livingRoomLight.off());
```
람다로 리모컨 앱의 클래스를 22개 → 9개로 줄일 수 있다. 단, `Command`에 추상 메서드가 **하나뿐일 때만** 가능하다.
</details>

> 하지만 `undo`처럼 **여러 연산**이 필요하거나 **상태를 저장**해야 하면, 함수 하나로는 부족하고 **객체(클래스)** 가 낫다(아래 §6·§7).

---

## 6. 실행 취소 (undo)

`Command`에 `undo()`를 추가한다. `execute()`의 **정반대** 작업을 한다.

```typescript
interface Command {
  execute(): void;
  undo(): void; // 추가
}

class LightOnCommand implements Command {
  constructor(private light: Light) {}
  execute(): void {
    this.light.on();
  }
  undo(): void {
    this.light.off(); // execute의 반대
  }
}
```

인보커는 **마지막으로 실행한 커맨드**를 기억했다가, UNDO 버튼에서 그 `undo()`를 호출한다.

```typescript
class RemoteControlWithUndo {
  private undoCommand: Command = new NoCommand();
  // ... onCommands/offCommands ...

  onButtonWasPushed(slot: number): void {
    this.onCommands[slot].execute();
    this.undoCommand = this.onCommands[slot]; // 마지막 명령 기록
  }

  undoButtonWasPushed(): void {
    this.undoCommand.undo(); // 마지막 작업 취소
  }
}
```

### 상태를 저장하는 undo — CeilingFan

선풍기처럼 **이전 상태로 되돌려야** 하는 경우, 커맨드가 **직전 속도를 저장**한다.

```typescript
class CeilingFanHighCommand implements Command {
  private prevSpeed = CeilingFan.OFF;

  constructor(private ceilingFan: CeilingFan) {}

  execute(): void {
    this.prevSpeed = this.ceilingFan.getSpeed(); // 변경 전 상태 저장
    this.ceilingFan.high();
  }

  undo(): void {
    // 저장해 둔 이전 속도로 복원
    switch (this.prevSpeed) {
      case CeilingFan.HIGH: this.ceilingFan.high(); break;
      case CeilingFan.MEDIUM: this.ceilingFan.medium(); break;
      case CeilingFan.LOW: this.ceilingFan.low(); break;
      case CeilingFan.OFF: this.ceilingFan.off(); break;
    }
  }
}
```

> **핵심 통찰**: 단순 토글(조명)은 반대 동작만으로 undo가 되지만, 상태가 여러 개인 리시버(선풍기 속도)는 **execute 시점에 이전 상태를 저장**해야 정확히 되돌릴 수 있다. UNDO 히스토리(여러 번 취소)는 커맨드를 **스택**에 쌓아 구현한다.

---

## 7. 매크로 커맨드 — 여러 명령을 한 번에

파티 모드(조명↓ + 오디오 ON + TV ON + 욕조 물 채우기)를 버튼 하나로. **다른 커맨드들을 담는 커맨드**를 만든다.

```typescript
class MacroCommand implements Command {
  constructor(private commands: Command[]) {}

  execute(): void {
    for (const command of this.commands) {
      command.execute();
    }
  }

  undo(): void {
    // 실행의 역순으로 undo (중요!)
    for (let i = this.commands.length - 1; i >= 0; i--) {
      this.commands[i].undo();
    }
  }
}

// 사용
const partyOn = new MacroCommand([lightOn, stereoOn, tvOn, hottubOn]);
remoteControl.setCommand(0, partyOn, partyOff);
```

> **핵심 통찰**: 매크로의 `undo()`는 **실행 순서의 역순**으로 각 커맨드를 취소해야 한다(스택처럼). `MacroCommand`는 담을 커맨드를 **동적으로 구성**하므로, 파티 로직을 직접 하드코딩하는 것보다 훨씬 유연하다.

---

## 8. 더 넓은 활용 — 큐·로그·트랜잭션

커맨드는 "리시버 + 일련의 행동"을 **일급 객체로 포장**한 것이라, 만든 뒤 오랜 시간이 지나거나 다른 스레드에서도 실행할 수 있다.

- **작업 큐(Job Queue)**: 커맨드를 큐에 넣고, 워커 스레드/풀이 꺼내 `execute()`. 큐는 계산 내용을 전혀 몰라도 된다. (웹 서버 요청 처리, 스케줄러 등)
- **로그·복구**: `store()`/`load()`를 추가해, 실행 내역을 디스크에 기록하고 시스템 다운 후 재실행해 복구. 스프레드시트의 체크포인트 복구 등.
- **트랜잭션**: 일련의 작업을 전부 처리하거나 전부 롤백.

> 실전 예: 2장의 스윙 `ActionListener`는 **옵저버이자 커맨드**였다. 버튼(인보커)이 클릭되면 `actionPerformed()`(= `execute()`)를 호출하고, 리스너(구상 커맨드)가 처리한다.

---

## 연습 문제 (해답 예시)

**1. `GarageDoorOpenCommand`** — `Command`를 구현하고 `execute()`에서 `garageDoor.up()`을 호출한다. 리모컨에 로드해 버튼을 누르면 "차고 문이 열렸습니다".

**2. OFF 커맨드들** — `LightOffCommand`, `StereoOffCommand`, `TVOffCommand`, `HottubOffCommand`를 각 리시버의 off 계열 메서드와 묶어 만든다.

**3. `MacroCommand.undo()`** — `execute()`가 순방향이면 `undo()`는 **역방향**으로 각 커맨드의 `undo()`를 호출한다(§7 코드).

**4. 스윙 앱에서 역할 구분** — 버튼 = **인보커**, `ActionListener` = **커맨드 인터페이스**(`actionPerformed`=`execute`), `AngelListener`/`DevilListener` = **구상 커맨드**, `System.out` = **리시버**, 셋업 클래스 = **클라이언트**.

---

## 디자인 원칙 정리 (누적)

이 장도 **새 원칙은 추가되지 않는다**(커맨드는 "요청의 캡슐화"라는 기법에 집중). 지금까지의 6가지 원칙은 그대로다:

1. 바뀌는 부분을 캡슐화한다. 2. 인터페이스에 맞춰 프로그래밍한다. 3. 상속보다 구성. 4. 느슨한 결합. 5. OCP. 6. DIP.

커맨드 패턴은 특히 **원칙 4(느슨한 결합)** 를 강하게 실현한다 — 인보커와 리시버가 커맨드를 통해 완전히 분리된다.

---

## 요약

- **커맨드 패턴**은 요청(리시버 + 행동)을 **객체로 캡슐화**하여, 요청하는 쪽(인보커)과 처리하는 쪽(리시버)을 분리한다.
- 등장인물: **클라이언트**(커맨드 생성)·**인보커**(`execute()` 호출)·**커맨드**(`execute()` 하나로 캡슐화)·**리시버**(실제 작업).
- **널 객체(`NoCommand`)** 로 `null` 검사를 없앤다.
- `undo()`를 추가하면 **실행 취소**가 가능하다. 상태가 있는 리시버는 execute 시점에 이전 상태를 저장한다.
- **매크로 커맨드**로 여러 명령을 한 번에 실행하고, 역순으로 취소한다.
- 커맨드는 **큐·로그·트랜잭션·스케줄러** 등으로 확장된다.
- TS/JS에서는 연산이 하나뿐이면 **함수 자체가 커맨드**가 된다(람다).

---

## 다른 챕터와의 관계

- **2장 옵저버**: 스윙 `ActionListener`는 옵저버이자 커맨드 — 두 패턴이 함께 쓰인다.
- **1장 전략 vs 커맨드**: 둘 다 "행동을 객체로 캡슐화"하지만, 전략은 **알고리즘 교체**, 커맨드는 **요청 캡슐화(+실행 취소·큐)** 에 초점.
- **14장 (기타 패턴)**: 커맨드의 큐/로그 활용은 트랜잭션·메멘토(상태 저장) 등과 연결된다.

---

## 보너스: 원서 복습 요소

### 🧠 뇌 단련 (Brain Power)

1. 커맨드 패턴에서 인보커와 리시버가 어떻게 분리되는가? (→ 커맨드 객체가 사이에서 요청을 캡슐화)
2. `CeilingFan`의 LOW/MEDIUM/OFF 커맨드도 만들어 보라(HIGH와 동일 구조, 이전 속도 저장).
3. 웹 서버의 요청 처리에 작업 큐를 어떻게 쓸까? (→ 요청을 커맨드로 큐잉, 워커 풀이 소비)

### 🏅 널 객체 (NoCommand) — 패턴 장려상

리턴할 객체가 없고 클라이언트가 `null`을 처리하지 않게 하고 싶을 때, "아무 일도 안 하는 객체"를 기본값으로 둔다.

### 📝 핵심 정리 (Bullet Points)

- 커맨드는 요청하는 객체와 수행하는 객체를 분리한다.
- 인보커는 `execute()`만 호출하고, 커맨드가 리시버에 위임한다.
- `undo()`로 실행 취소, 스택으로 히스토리 취소를 구현한다.
- 매크로 커맨드로 다중 명령을, 큐/로그로 지연 실행·복구를 구현한다.

### 📝 낱말 퀴즈 (정답 단어 모음)

6장 용어들(정답은 영어): COMMAND(커맨드), INVOKER(인보커), RECEIVER(리시버), CLIENT(클라이언트), EXECUTE(execute), UNDO(작업 취소), REQUEST(요청), DECOUPLED(분리), BINDS(연결), WAITRESS(종업원), COOK(요리), OBJECTVILLE(객체마을), VENDORCLASSES(협력 업체 클래스), LIGHT(조명), WEATHER-O-RAMA(웨더오라마), GREENEGGSANDHAM(초록 달걀과 햄).
