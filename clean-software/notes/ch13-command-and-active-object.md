# Chapter 13: Command and Active Object Patterns (커맨드와 액티브 오브젝트 패턴)

## 핵심 질문

지금까지 기술된 모든 디자인 패턴 중에서도 단순하기 그지없는 인터페이스 하나로 이루어진 커맨드 패턴이 어떻게 데이터베이스 트랜잭션부터 장치 제어, 멀티스레딩의 핵심, GUI의 실행/취소까지 그토록 광범위한 영역에서 쓰일 수 있는가? "함수를 객체화한다"는 행위는 객체지향의 신성모독인가, 아니면 두 패러다임이 부딪치는 경계에서 일어나는 흥미로운 사건인가?

> 그 어느 누구도 다른 사람들에게 명령할 권한을 자연으로부터 받은 사람은 없다.<br>— 데니스 디드로(Denis Diderot), 1713~1784

---

## 1. 커맨드 패턴 — 단순함의 극치

커맨드 패턴(*Command Pattern - 명령(요청)을 객체로 캡슐화하는 GoF 디자인 패턴*)은 지난 수년간 기술되어 온 모든 디자인 패턴 중에서도 가장 단순하면서도 세련된 것이다. 그 단순성은 정말 믿기 어려울 정도다. 메소드 하나만 가진 인터페이스, 그 이상도 이하도 아니다.

### 1.1 인터페이스 한 줄

```
   «interface»
   ┌─────────────┐
   │  Command    │
   ├─────────────┤
   │ + execute() │
   └─────────────┘
```

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public interface Command {
    void execute();
}
```

</details>

```typescript
// TypeScript
interface Command {
  execute(): void;
}
```

아무런 변수도 없고, 메소드 하나뿐인 인터페이스. 이게 패턴이라고 부를 만한 것인가 싶을 정도다. 하지만 이 패턴은 아주 흥미로운 어떤 선을 넘어버렸다.

### 1.2 패턴이 넘어선 선 — 함수의 객체화

대부분의 클래스는 **한 벌의 메소드와 그에 대응하는 변수 집합을 결합**한다. 그러나 커맨드 패턴은 그렇지 않다. 오히려 **함수를 캡슐화해서 변수에서 해방**시킨다.

엄격한 객체지향 관점에서 보자면 이것은 저주나 다름없다. 함수형 분해(*functional decomposition - 시스템을 데이터가 아닌 함수 단위로 쪼개는 접근*)의 기미를 보이며, 함수의 역할을 클래스 수준으로 격상시킨다. 신성모독이라는 비판이 나올 만하다. 하지만 두 패러다임이 부딪치는 이 경계에서 재미있는 일들이 일어나기 시작한다.

> **핵심 통찰**: 커맨드 패턴은 "클래스는 데이터와 메소드를 함께 묶는다"는 객체지향의 정설을 위반한다. 함수를 일급 객체로 격상시키고, 실행할 행위(*what to do*)와 그것을 실행하는 시점/주체(*when/who*)를 분리한다. 이 분리가 패턴의 단순성에 어울리지 않는 막강한 유연성을 가져온다.

---

## 2. 단순 적용 — 하드웨어 제어와 Sensor 배선

저자는 복사기 제조사에서 새 복사기의 실시간 임베디드 소프트웨어 설계를 컨설팅하며 커맨드 패턴을 다음과 같이 적용했다.

### 2.1 장치 제어 커맨드 계층

```
            «interface»
            ┌─────────────┐
            │   Command   │
            ├─────────────┤
            │ + execute() │
            └──────┬──────┘
                   △
   ┌───────────────┼──────────────┬──────────────┬──────────────┬──────────────┐
   │               │              │              │              │              │
RelayOn        RelayOff        MotorOn       MotorOff       ClutchOn       ClutchOff
Command        Command         Command       Command        Command        Command
```

각 클래스의 역할은 분명하다. `RelayOnCommand`의 `execute()`를 호출하면 릴레이(*relay - 다른 회로의 전기적 변화에 따라 전기 회로를 개폐하는 장치*)가 켜진다. `MotorOffCommand`의 `execute()`를 호출하면 모터가 꺼진다. 모터나 릴레이의 위치는 생성자에 인자로 넘긴다.

```typescript
// TypeScript
interface Command {
  execute(): void;
}

class RelayOnCommand implements Command {
  constructor(private readonly relayId: string) {}

  execute(): void {
    Hardware.activateRelay(this.relayId);
  }
}

class MotorOffCommand implements Command {
  constructor(private readonly motorId: string) {}

  execute(): void {
    Hardware.stopMotor(this.motorId);
  }
}
```

### 2.2 Sensor가 주도하는 Command

복사기는 이벤트 주도적(*event-driven - 이벤트 발생에 따라 동작이 결정되는 방식*)이다. 종이 한 장이 용지 통로의 일정한 위치에 이르렀음을 광센서가 감지하면 특정 클러치(*clutch - 축과 축을 접속하거나 차단하는 기계 부품*)를 접속시켜야 한다. 이를 위해서는 해당 `ClutchOnCommand`를 그 광센서에 묶어 두면 된다.

```
   ┌──────────┐    holds    ┌──────────┐
   │  Sensor  │ ──────────▶ │ Command  │
   └──────────┘             └──────────┘
        │                         │
        │ when event detected     │
        └──────── execute() ──────▶
```

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Sensor {
    private final Command boundCommand;

    public Sensor(Command boundCommand) {
        this.boundCommand = boundCommand;
    }

    public void onEventDetected() {
        boundCommand.execute();
    }
}
```

</details>

```typescript
// TypeScript
class Sensor {
  constructor(private readonly boundCommand: Command) {}

  onEventDetected(): void {
    this.boundCommand.execute();
  }
}
```

이 구조의 굉장한 장점은 다음과 같다:

- **Sensor는 자신이 하는 일을 모른다**. 그저 이벤트를 탐지하면 묶여 있는 Command의 `execute()`를 호출할 뿐이다.
- Sensor는 개별 클러치나 릴레이에 대해 알 필요가 없다.
- Sensor는 용지 통로의 기계적 구조를 알 필요가 없다.

어떤 센서가 이벤트를 알렸을 때 어떤 릴레이를 닫을지 결정하는 복잡한 문제는 **초기화 함수**의 몫으로 넘어간다. 시스템 초기화 도중 어떤 시점에 각 Sensor는 적절한 Command와 묶이게 된다. 모든 논리적 배선(*wiring - Sensor와 Command 간의 논리적 상호 연결*)을 한 곳에 모은다.

> **핵심 통찰**: 커맨드 패턴은 **시스템의 논리적 상호 연결을 연결된 장치에서 분리**해 낸다. Sensor가 어떤 Command와 묶여 있는지를 설명하는 텍스트 파일을 만들 수도 있다. 시스템의 배선이 프로그램 밖에서 완전히 결정될 수 있고, 재컴파일 없이 변경될 수도 있다.

---

## 3. 트랜잭션 — 검증과 실행의 분리

커맨드 패턴의 또 다른 일반적인 사용법은 트랜잭션의 생성과 실행이다. 급여 관리 사례 연구에서 이어질 작업이기도 하다.

### 3.1 Employee 데이터베이스 문제

직원들의 데이터베이스를 관리하는 시스템을 작성한다고 하자. 사용자는 새 직원을 추가하고, 기존 직원을 삭제하고, 직원의 속성을 변경한다.

```
                  ┌────────────────────┐
                  │      Employee      │
                  ├────────────────────┤
                  │ - name             │
                  │ - address          │
                  └─────────┬──────────┘
                            │ has
                            ▼
                  «interface»
                  ┌────────────────────┐
                  │ PayClassification  │
                  ├────────────────────┤
                  │ + calculatePay()   │
                  └─────────△──────────┘
                            │
       ┌────────────────────┼────────────────────┐
       │                    │                    │
SalariedClassification  HourlyClassification  CommissionedClassification
- monthlyPay            - hourlyRate          - basePay
                        ▼ TimeCard            - commissionRate
                                              ▼ SalesReceipt
```

사용자가 새 직원을 추가하려고 마음을 정했다면 직원 레코드를 생성하는 데 필요한 모든 정보를 지정해야 한다. 시스템은 그 정보에 따라 동작하기 전에 **문법적으로나 의미적으로 옳은지 검증**해야 한다.

### 3.2 Transaction 패턴 구조

커맨드 객체가 검증되지 않은 데이터의 저장소 역할을 하고, 검증 메소드와 실행 메소드를 각각 구현한다.

```
   «interface»
   ┌──────────────────┐
   │   Transaction    │
   ├──────────────────┤
   │ + validate()     │
   │ + execute()      │
   └────────△─────────┘
            │
            │
   ┌──────────────────────────┐
   │ AddEmployeeTransaction   │
   ├──────────────────────────┤
   │ - name                   │
   │ - address                │ ◀── 검증되지 않은 데이터
   │ - PayClassification      │
   ├──────────────────────────┤
   │ + validate()             │
   │ + execute()              │
   └──────────────────────────┘
```

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public interface Transaction {
    boolean validate();
    void execute();
}

public class AddEmployeeTransaction implements Transaction {
    private String name;
    private String address;
    private PayClassification classification;

    public AddEmployeeTransaction(String name, String address,
                                  PayClassification classification) {
        this.name = name;
        this.address = address;
        this.classification = classification;
    }

    public boolean validate() {
        // 데이터가 문법적/의미적으로 옳은지 확인.
        // 이미 같은 직원이 존재하지는 않는지도 확인.
        return EmployeeRepository.notExists(name)
            && classification.isValid();
    }

    public void execute() {
        Employee e = new Employee(name, address);
        e.setClassification(classification);
        EmployeeRepository.save(e);
    }
}
```

</details>

```typescript
// TypeScript
interface Transaction {
  validate(): boolean;
  execute(): void;
}

class AddEmployeeTransaction implements Transaction {
  constructor(
    private readonly name: string,
    private readonly address: string,
    private readonly classification: PayClassification,
  ) {}

  validate(): boolean {
    return (
      EmployeeRepository.notExists(this.name) &&
      this.classification.isValid()
    );
  }

  execute(): void {
    const e = new Employee(this.name, this.address);
    e.setClassification(this.classification);
    EmployeeRepository.save(e);
  }
}
```

`validate` 메소드는 데이터가 이치에 맞는지 확인한다. 트랜잭션의 데이터가 기존 데이터베이스 상태와 일치하는지도 확인한다(예: 그 직원이 이미 존재하지 않는다는 사실). `execute` 메소드는 검증된 데이터로 데이터베이스를 갱신한다.

### 3.3 물리적, 시간적 분리

이런 방식의 장점은 다음을 극적으로 분리한다는 데 있다:

| 분리되는 코드 | 책임 |
|---|---|
| 사용자에게서 데이터를 받는 코드 (GUI 등) | 입력 수집 |
| 데이터를 검증하고 작업하는 코드 (Transaction) | 비즈니스 로직 |
| 업무 객체 자체 (Employee, PayClassification) | 도메인 |

만약 검증과 실행 알고리즘이 GUI 코드 안에 있다면, 다른 인터페이스(웹, CLI, 배치)에서 이 코드를 재사용할 수 없게 된다. Transaction 클래스로 떼어 놓으면 입력 인터페이스와 물리적으로 분리되고, 데이터베이스 조작 방법을 아는 코드를 업무 실체 자체로부터 분리한 것이기도 하다.

> **핵심 통찰**: 트랜잭션을 객체로 만든다는 것은 **공간(GUI/도메인 분리)뿐 아니라 시간까지 분리**할 수 있다는 뜻이다. 데이터를 받은 즉시 검증/실행할 필요가 없다. 트랜잭션 객체를 목록에 모아두었다가 자정에 일괄 실행할 수도 있다. 낮에는 입력만 받고 밤에 일괄 처리하는 배치 시스템이 이렇게 구현된다.

### 3.4 시간적 분리 예시

```typescript
// TypeScript — 낮에 입력만 받고 자정에 실행
class TransactionQueue {
  private readonly pending: Transaction[] = [];

  enqueue(t: Transaction): void {
    if (t.validate()) {
      this.pending.push(t);
    } else {
      throw new Error("Invalid transaction");
    }
  }

  runAll(): void {
    while (this.pending.length > 0) {
      const t = this.pending.shift()!;
      t.execute();
    }
  }
}
```

낮 동안 사용자 입력으로부터 `AddEmployeeTransaction`, `DeleteEmployeeTransaction` 등을 만들어 `enqueue`로 검증만 해두고, 자정에 `runAll`로 일괄 적용한다.

---

## 4. Undo — 되돌리기 가능한 커맨드

커맨드 패턴에 `undo()` 메소드를 추가하면 되돌리기를 구현할 수 있다. `execute()`가 수행한 동작을 구체적으로 기억하도록 만들면, `undo()`는 그 동작을 되돌려 시스템을 원래 상태로 복귀시킬 수 있다.

```
   «interface»
   ┌───────────────┐
   │    Command    │
   ├───────────────┤
   │ + execute()   │
   │ + undo()      │
   └───────────────┘
```

### 4.1 도형 그리기 예제

사용자가 스크린에 기하 도형을 그릴 수 있는 애플리케이션을 상상해 보자.

```
사용자가 '원 그리기' 버튼 클릭
            │
            ▼
   DrawCircleCommand 생성 → execute()
            │
            ▼
   (마우스 추적 → 클릭으로 중심 잡고 → 다시 클릭으로 반지름 확정)
            │
            ▼
   원을 화면 도형 목록에 추가 + 원의 ID를 private 변수에 저장
            │
            ▼
   완료된 명령 스택에 push
            │
   사용자가 '취소' 버튼 클릭
            │
            ▼
   스택에서 pop → undo() 호출
            │
            ▼
   저장된 ID로 원을 찾아 도형 목록에서 삭제
```

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class DrawCircleCommand implements Command {
    private final DrawingCanvas canvas;
    private int createdCircleId = -1;

    public DrawCircleCommand(DrawingCanvas canvas) {
        this.canvas = canvas;
    }

    public void execute() {
        Circle c = canvas.interactivelyCreateCircle();
        createdCircleId = c.getId();
        canvas.addShape(c);
    }

    public void undo() {
        canvas.removeShapeById(createdCircleId);
    }
}
```

</details>

```typescript
// TypeScript
interface Command {
  execute(): void;
  undo(): void;
}

class DrawCircleCommand implements Command {
  private createdCircleId = -1;

  constructor(private readonly canvas: DrawingCanvas) {}

  execute(): void {
    const circle = this.canvas.interactivelyCreateCircle();
    this.createdCircleId = circle.id;
    this.canvas.addShape(circle);
  }

  undo(): void {
    this.canvas.removeShapeById(this.createdCircleId);
  }
}
```

> **핵심 통찰**: 명령을 취소하는 방법을 아는 코드는 **항상 그 명령을 수행하는 방법을 아는 코드와 함께** 있어야 한다. 같은 클래스 안에 `execute()`와 `undo()`를 모두 둠으로써, 두 책임이 자연스럽게 결합된 채로 응집된다. SRP에 위배되지 않는 이유는 둘 다 "이 명령의 의미"라는 하나의 책임에 속하기 때문이다.

---

## 5. 액티브 오브젝트 패턴 — 함수로 만든 스레드

저자가 좋아하는 커맨드 패턴 응용 방식 중 하나는 액티브 오브젝트(*Active Object - 멀티스레딩을 동기 호출 형태로 흉내 내는 패턴*) 패턴이다. 이 패턴은 다중 제어 스레드 구현을 위한 오래된 기법으로, 수천 개의 산업 시스템에서 단순한 멀티태스킹의 핵심부가 되어 왔다.

### 5.1 ActiveObjectEngine

아이디어는 아주 간단하다. `ActiveObjectEngine`은 Command 객체의 연결 리스트를 유지한다. 사용자는 엔진에 새 명령을 추가하거나 `run()`을 호출할 수 있다. `run()`은 단순히 각 명령을 실행하고 제거하면서 리스트를 훑어 나가는 함수다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
import java.util.LinkedList;

public class ActiveObjectEngine {
    private LinkedList<Command> itsCommands = new LinkedList<>();

    public void addCommand(Command c) {
        itsCommands.add(c);
    }

    public void run() throws Exception {
        while (!itsCommands.isEmpty()) {
            Command c = itsCommands.getFirst();
            itsCommands.removeFirst();
            c.execute();
        }
    }
}

public interface Command {
    void execute() throws Exception;
}
```

</details>

```typescript
// TypeScript
interface Command {
  execute(): void;
}

class ActiveObjectEngine {
  private readonly itsCommands: Command[] = [];

  addCommand(c: Command): void {
    this.itsCommands.push(c);
  }

  run(): void {
    while (this.itsCommands.length > 0) {
      const c = this.itsCommands.shift()!;
      c.execute();
    }
  }
}
```

이것은 그다지 특별해 보이지 않는다. 하지만 연결 리스트에 있는 Command 객체 중 하나가 **자기를 복제하여 리스트에 다시 넣는다면** 어떤 일이 일어날지 생각해 보자. 이 리스트는 절대 비지 않고, `run()` 함수는 절대로 복귀하지 않는다.

### 5.2 SleepCommand — 자기를 다시 큐에 넣는 명령

지정된 시간만큼 기다린 뒤 `wakeup` 명령을 실행하는 `SleepCommand`를 구현해 보자.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class SleepCommand implements Command {
    private Command wakeupCommand;
    private ActiveObjectEngine engine;
    private long sleepTime;
    private long startTime = 0;
    private boolean started = false;

    public SleepCommand(long milliseconds, ActiveObjectEngine e,
                        Command wakeupCommand) {
        this.sleepTime = milliseconds;
        this.engine = e;
        this.wakeupCommand = wakeupCommand;
    }

    public void execute() throws Exception {
        long currentTime = System.currentTimeMillis();
        if (!started) {
            started = true;
            startTime = currentTime;
            engine.addCommand(this);
        } else if ((currentTime - startTime) < sleepTime) {
            engine.addCommand(this);
        } else {
            engine.addCommand(wakeupCommand);
        }
    }
}
```

</details>

```typescript
// TypeScript
class SleepCommand implements Command {
  private startTime = 0;
  private started = false;

  constructor(
    private readonly sleepTime: number,
    private readonly engine: ActiveObjectEngine,
    private readonly wakeupCommand: Command,
  ) {}

  execute(): void {
    const currentTime = Date.now();
    if (!this.started) {
      this.started = true;
      this.startTime = currentTime;
      this.engine.addCommand(this);
    } else if (currentTime - this.startTime < this.sleepTime) {
      this.engine.addCommand(this);
    } else {
      this.engine.addCommand(this.wakeupCommand);
    }
  }
}
```

`SleepCommand`가 실행되면:

1. 처음 실행이면 시작 시간을 기록하고 자신을 큐에 다시 넣는다.
2. 지연 시간이 아직 지나지 않았으면 자신을 큐에 다시 넣는다.
3. 지연 시간이 지났으면 `wakeupCommand`를 큐에 넣는다.

### 5.3 멀티스레드 시스템과의 유사성

이 프로그램과 어떤 이벤트를 기다리는 멀티스레드 프로그램 사이에는 명확한 유사성이 있다.

| 전통적 멀티스레드 | 액티브 오브젝트 (RTC 태스크) |
|---|---|
| 스레드가 이벤트를 기다릴 때 OS 시스템 콜을 호출해 **블록(block)** | **블록하지 않음**. 이벤트가 아직이면 자신을 다시 큐에 넣음 |
| 각 스레드마다 별도의 런타임 스택 필요 | **모든 RTC 태스크가 같은 런타임 스택 공유** |
| 컨텍스트 스위칭 비용 발생 | 컨텍스트 스위칭 없음 |
| OS 스케줄러가 결정 | 협력적 — Command가 자발적으로 양보 |

RTC(*Run-To-Completion - 각 Command 인스턴스가 다음 Command가 실행되기 전에 완료까지 실행되는 모델*)라는 이름이 내포하는 의미는 **Command 인스턴스가 블록하지 않는다**는 것이다. 이는 많은 스레드가 실행되고 메모리가 제한된 시스템(임베디드)에서 강력한 이점이 된다.

> **Uncle Bob의 경험**: 나는 복사기 임베디드 소프트웨어를 만들 때 이 패턴을 사용했고, 그 외에도 수많은 실시간 임베디드 시스템에서 이 기법의 변형을 보아 왔다. 운영체제의 멀티스레딩이 없거나, 있더라도 메모리·스택 비용을 감당할 수 없을 때, 액티브 오브젝트는 "함수로 만든 스레드"라는 형태로 멀티태스킹의 환상을 제공한다.

### 5.4 DelayedTyper — 멀티스레드 흉내

`SleepCommand`를 활용하여 여러 "스레드"가 동시에 돌아가는 듯한 동작을 만들어 보자.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class DelayedTyper implements Command {
    private long itsDelay;
    private char itsChar;
    private static ActiveObjectEngine engine = new ActiveObjectEngine();
    private static boolean stop = false;

    public static void main(String[] args) throws Exception {
        engine.addCommand(new DelayedTyper(100, '1'));
        engine.addCommand(new DelayedTyper(300, '3'));
        engine.addCommand(new DelayedTyper(500, '5'));
        engine.addCommand(new DelayedTyper(700, '7'));

        Command stopCommand = new Command() {
            public void execute() { stop = true; }
        };
        engine.addCommand(new SleepCommand(20000, engine, stopCommand));
        engine.run();
    }

    public DelayedTyper(long delay, char c) {
        itsDelay = delay;
        itsChar = c;
    }

    public void execute() throws Exception {
        System.out.print(itsChar);
        if (!stop) {
            delayAndRepeat();
        }
    }

    private void delayAndRepeat() throws Exception {
        engine.addCommand(new SleepCommand(itsDelay, engine, this));
    }
}
```

</details>

```typescript
// TypeScript
class DelayedTyper implements Command {
  private static engine = new ActiveObjectEngine();
  private static stop = false;

  constructor(
    private readonly itsDelay: number,
    private readonly itsChar: string,
  ) {}

  execute(): void {
    process.stdout.write(this.itsChar);
    if (!DelayedTyper.stop) {
      this.delayAndRepeat();
    }
  }

  private delayAndRepeat(): void {
    DelayedTyper.engine.addCommand(
      new SleepCommand(this.itsDelay, DelayedTyper.engine, this),
    );
  }

  static main(): void {
    DelayedTyper.engine.addCommand(new DelayedTyper(100, "1"));
    DelayedTyper.engine.addCommand(new DelayedTyper(300, "3"));
    DelayedTyper.engine.addCommand(new DelayedTyper(500, "5"));
    DelayedTyper.engine.addCommand(new DelayedTyper(700, "7"));

    const stopCommand: Command = {
      execute: () => {
        DelayedTyper.stop = true;
      },
    };
    DelayedTyper.engine.addCommand(
      new SleepCommand(20000, DelayedTyper.engine, stopCommand),
    );
    DelayedTyper.engine.run();
  }
}
```

이 프로그램을 실행하면 다음과 같은 비결정적(*nondeterministic - 같은 입력에도 실행마다 결과가 달라지는*) 출력이 나온다.

```
135711311511371113151131715131113151731111351113711531111357...
1.3571113151317114e+59...
```

CPU 클록과 실제 시간이 완벽하게 동기화되지 않기 때문에 실행마다 문자열이 달라진다. **이런 종류의 비결정적 행위는 멀티스레드 시스템의 특징**이다.

> **핵심 통찰**: 비결정적 행위는 많은 고민과 고통의 원인이 될 수 있다. 실시간 임베디드 시스템 종사자라면 누구나 알듯, 비결정적 행위를 디버깅하는 일은 어렵다. 액티브 오브젝트는 OS 스레드의 메모리·스택 비용을 절감해 주지만, 멀티스레딩 고유의 디버깅 난이도는 그대로 안고 간다.

---

## 패턴 구조

### 커맨드 패턴 기본 구조

```
   Client ──생성──▶ ConcreteCommand ───┐
                                       │ implements
   Invoker ──hold──▶ «interface»       │
                     Command  ◀────────┘
                     + execute()
                          │
                          ▼
                       Receiver  (실제 작업을 수행하는 대상)
```

| 역할 | 책임 |
|---|---|
| **Command** | `execute()` 인터페이스 정의 |
| **ConcreteCommand** | Receiver를 호출하여 실제 동작 수행 |
| **Receiver** | 명령이 실제로 작용하는 대상 (Hardware, Database 등) |
| **Invoker** | Command를 호출하는 주체 (Sensor, GUI Button 등) |
| **Client** | Command를 생성하고 Receiver와 묶어 Invoker에 전달 |

### 액티브 오브젝트 구조

```
   ┌────────────────────────┐
   │  ActiveObjectEngine    │
   ├────────────────────────┤
   │ - itsCommands: List    │
   ├────────────────────────┤
   │ + addCommand(c)        │
   │ + run()                │
   └───────────┬────────────┘
               │ holds many
               ▼
       «interface» Command
               △
       ┌───────┴────────────┬─────────────────┐
       │                    │                 │
   SleepCommand        DelayedTyper       AppCommand
   (자신을 재투입)     (자신을 재투입)
```

---

## 활용 사례

| 도메인 | 적용 예시 |
|---|---|
| **하드웨어 제어 (임베디드)** | Sensor가 이벤트를 감지하면 묶여 있는 Command 실행. 배선을 텍스트 파일로 외부화 가능 |
| **데이터베이스 트랜잭션** | `AddEmployeeTransaction.validate()` + `execute()`로 입력 검증과 실행 분리 |
| **배치 처리** | 트랜잭션 객체를 큐에 모았다가 자정에 일괄 실행 |
| **Undo/Redo (GUI)** | `execute()`/`undo()` 쌍을 가진 Command를 완료 스택에 push |
| **멀티스레드 흉내 (RTC)** | ActiveObjectEngine + SleepCommand로 OS 스레드 없이 협력적 멀티태스킹 |
| **매크로/스크립트** | 여러 Command를 묶은 CompositeCommand로 매크로 구현 |
| **요청 큐잉/로깅** | 네트워크 요청, 작업 큐를 Command로 직렬화하여 전송·재실행 |

---

## 자주 하는 실수

| 안티패턴 | 문제점 | 해결 |
|---|---|---|
| Command에 너무 많은 상태를 담음 | 함수의 객체화라는 본래 의도가 흐려짐 | Command는 "무엇을 할지"만, 데이터는 Receiver에 |
| `execute()` 안에 분기로 여러 명령 구현 | 다형성을 포기하고 if/else 미궁 | 각 명령마다 별도 ConcreteCommand 클래스 |
| `undo()` 구현 시 외부 상태에 의존 | 실행 시점과 취소 시점의 상태가 다르면 깨짐 | `execute()` 시점의 정보를 Command 내부에 저장 |
| Active Object의 Command가 블록 호출 사용 | RTC 가정이 깨져 다른 Command가 굶주림 | 비블록 폴링 또는 SleepCommand 패턴 사용 |
| 트랜잭션의 `validate()`와 `execute()` 사이에 상태 변경 가능 | 검증 후 실행 사이에 데이터가 바뀌면 일관성 깨짐 | 트랜잭션 락 또는 낙관적 동시성 제어 |

---

## 요약

- **커맨드 패턴은 단순함의 극치다**. `execute()` 메소드 하나만 가진 인터페이스가 함수를 객체로 격상시킨다.
- **함수를 캡슐화하여 변수와 분리**한다. 객체지향의 정설("데이터+메소드")을 위반하지만, 두 패러다임이 부딪치는 경계에서 막강한 유연성이 나온다.
- **하드웨어 제어**에서 Sensor와 Command를 분리하여, 시스템의 논리적 배선을 외부 텍스트 파일로 빼낼 수 있다.
- **트랜잭션**에서 `validate()`와 `execute()`를 분리하여, GUI 코드/도메인/검증 로직을 물리적·시간적으로 분리한다.
- **Undo**는 `execute()`와 `undo()`를 같은 Command 클래스에 묶어 응집도 있게 구현한다.
- **액티브 오브젝트**는 Command가 자신을 큐에 재투입하는 방식으로 OS 스레드 없이 멀티태스킹을 흉내 낸다. RTC 모델은 같은 스택을 공유하여 메모리 효율이 높지만, 멀티스레딩 고유의 비결정성은 그대로 가져간다.
- 커맨드 패턴은 함수를 클래스보다 강조하기 때문에 객체지향 패러다임을 망가뜨린다고 비판받기도 한다. 사실일지 모르나, 소프트웨어 개발 현장에서는 데이터베이스 트랜잭션부터 장치 제어, 멀티스레딩의 핵심, GUI의 실행/취소까지 정말 다양한 용도로 유용하게 쓰인다.
