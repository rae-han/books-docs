# Chapter 25: Abstract Server, Adapter, and Bridge Patterns (추상 서버, 어댑터, 브리지 패턴)

## 핵심 질문

`Switch`가 `Light`를 직접 제어하면 무엇이 잘못되는가? 같은 의존성 역전 원리를 적용하는 세 가지 패턴 — 추상 서버, 어댑터, 브리지 — 은 각각 어떤 상황에 적합한가? 그리고 — 임시방편(*kludge - 임시방편적이고 어색한 해결책*)을 어떻게 어댑터 안에 가두어 시스템 전체를 오염시키지 않을 수 있는가?

> 정치인은 어디나 다 똑같다. 그들은 강이 있지도 않은 곳에 다리를 놓겠다고 약속한다.<br>— 니키타 흐루시초프(Nikita Khrushchev)

---

## 1. Switch-Light 문제 — 단순함의 함정

1990년대 중반 `comp.object` 뉴스그룹에서 벌어졌던 토론에서, 단순한 탁상 스탠드 내부에서 돌아갈 소프트웨어를 설계하는 문제가 등장했다. 탁상 스탠드에는 전구 하나와 스위치가 있다. 스위치에게 켜져 있는지 꺼져 있는지를 물어볼 수 있고, 전구에게 켤지 끌지를 명령할 수 있다.

### 1.1 가장 단순한 설계

```
┌─────────┐         ┌───────────┐
│ Switch  │────────▶│   Light   │
└─────────┘         ├───────────┤
                    │ + turnOn  │
                    │ + turnOff │
                    └───────────┘
```

<details>
<summary>원문 Java 코드</summary>

```java
// Java - 가장 단순하지만 문제 있는 설계
public class Light {
    public void turnOn() { /* ... */ }
    public void turnOff() { /* ... */ }
}

public class Switch {
    private Light light;

    public Switch(Light light) {
        this.light = light;
    }

    public void poll() {
        if (isOn()) {
            light.turnOn();
        } else {
            light.turnOff();
        }
    }

    private boolean isOn() { /* 하드웨어 상태 확인 */ return true; }
}
```

</details>

```typescript
// TypeScript - 가장 단순하지만 문제 있는 설계
class Light {
  turnOn(): void {
    /* ... */
  }
  turnOff(): void {
    /* ... */
  }
}

class Switch {
  constructor(private light: Light) {}

  poll(): void {
    if (this.isOn()) {
      this.light.turnOn();
    } else {
      this.light.turnOff();
    }
  }

  private isOn(): boolean {
    return true;
  }
}
```

### 1.2 무엇이 문제인가?

이 설계는 의존 관계 역전 원칙(*DIP - Dependency Inversion Principle*)과 개방 폐쇄 원칙(*OCP - Open-Closed Principle*) 두 가지를 동시에 위반한다.

| 원칙 | 위반의 모습 |
|------|-------------|
| **DIP 위반** | `Switch`가 구체 클래스인 `Light`에 직접 의존한다. 추상 클래스에 의존하는 편이 낫다. |
| **OCP 위반** | `Switch`가 필요할 때마다 `Light`도 같이 끌고 다녀야 한다. `Switch`는 `Light` 외의 객체를 제어할 수 있도록 확장하기 힘들다. |

### 1.3 잘못된 확장: 상속

전구 말고 다른 것을 제어하려고 `Switch`로부터 상속받은 서브클래스를 만든다고 가정해 보자.

```
┌──────────┐         ┌───────────┐
│  Switch  │────────▶│   Light   │
└────┬─────┘         └───────────┘
     │
     ▼
┌────────────┐         ┌─────────┐
│ FanSwitch  │────────▶│   Fan   │
└────────────┘         └─────────┘
```

이 방식은 문제를 해결하지 못한다. `FanSwitch`는 여전히 간접적으로 `Light`에 대한 의존 관계를 갖고 있고(상속을 통해), `FanSwitch`를 쓰는 곳마다 `Light`도 같이 가져가야 한다. 이 상속 관계는 DIP까지 위반한다.

---

## 2. 추상 서버 패턴 (Abstract Server)

이 문제를 해결하기 위해 디자인 패턴 중 가장 간단한 축에 속하는 **추상 서버(Abstract Server) 패턴**을 사용한다. `Switch`와 `Light` 사이에 인터페이스를 하나 도입함으로써, 이 인터페이스를 구현하는 것이라면 무엇이든 `Switch`가 제어할 수 있게 만든다.

### 2.1 구조

```
┌─────────┐         ┌────────────────┐
│ Switch  │────────▶│  «interface»   │
└─────────┘         │  Switchable    │
                    ├────────────────┤
                    │ + turnOn       │
                    │ + turnOff      │
                    └────────┬───────┘
                             ▲
                             │
                    ┌────────┴───────┐
                    │     Light      │
                    ├────────────────┤
                    │ + turnOn       │
                    │ + turnOff      │
                    └────────────────┘
```

<details>
<summary>원문 Java 코드</summary>

```java
// Java - 추상 서버 패턴
public interface Switchable {
    void turnOn();
    void turnOff();
}

public class Light implements Switchable {
    public void turnOn() { /* ... */ }
    public void turnOff() { /* ... */ }
}

public class Switch {
    private Switchable switchable;

    public Switch(Switchable switchable) {
        this.switchable = switchable;
    }

    public void poll() {
        if (isOn()) {
            switchable.turnOn();
        } else {
            switchable.turnOff();
        }
    }

    private boolean isOn() { return true; }
}
```

</details>

```typescript
// TypeScript - 추상 서버 패턴
interface Switchable {
  turnOn(): void;
  turnOff(): void;
}

class Light implements Switchable {
  turnOn(): void {
    /* ... */
  }
  turnOff(): void {
    /* ... */
  }
}

class Switch {
  constructor(private switchable: Switchable) {}

  poll(): void {
    if (this.isOn()) {
      this.switchable.turnOn();
    } else {
      this.switchable.turnOff();
    }
  }

  private isOn(): boolean {
    return true;
  }
}
```

이렇게 하면 DIP와 OCP가 동시에 충족된다. `Switch`는 추상 인터페이스에만 의존하고, 새로운 `Switchable` 구현체(예: `Fan`, `Heater`)를 추가해도 `Switch`는 변경되지 않는다.

### 2.2 인터페이스는 누가 소유하는가?

흥미로운 곁가지로 들어가서, 인터페이스의 클라이언트를 위하는 쪽으로 인터페이스 이름을 지었다는 점에 주목하자. 인터페이스 이름이 `ILight`가 아니라 `Switchable`이다.

> **핵심 통찰**: 인터페이스는 그 인터페이스의 파생 클래스가 아니라 **클라이언트에게 속한다**. 인터페이스와 그 파생형 사이의 논리적 구속력보다, 클라이언트와 인터페이스 사이의 논리적 구속력이 더 강하다. `Switchable` 없이 `Switch`를 배치한다는 사실은 상상할 수 없을 만큼 강한 결속이지만, `Light` 없이 `Switchable`을 배치하는 것은 충분히 가능하다.

이러한 논리적 구속력의 강약은 물리적 구속력의 강약과 일치하지 않는다. 연관(association)보다 상속(inheritance)이 훨씬 강력한 물리적 구속력을 지니기 때문이다.

1990년대 초반에는 물리적 구속력이 지배적이라고 생각해 동일한 상속 계층 구조에 속한 클래스들을 동일한 물리적 패키지에 넣도록 권장하기도 했다. 하지만 최근 10년 동안 우리는 상속 계층 구조는 보통 한 패키지에 들어가지 않아야 한다는 것을 배웠다. 오히려 **클라이언트와 그 클라이언트가 제어하는 인터페이스들이 함께 패키지에 들어가야** 한다.

> **핵심 통찰**: 이런 논리적 구속력과 물리적 구속력의 불일치는 C++나 Java 같은 정적 타입 언어의 산물이다. 스몰토크, 파이썬, 루비 같은 동적 타입 언어는 행위의 다형성을 상속을 통해 다루지 않기 때문에 이러한 불일치가 없다.

---

## 3. 어댑터 패턴 (Adapter)

추상 서버 설계에도 또 다른 문제가 있는데, **단일 책임 원칙(SRP)을 위반할 가능성**이 있다는 점이다. 변경의 이유가 다를 수도 있는 `Light`와 `Switchable` 두 가지를 묶어 놓았다. 다음 경우라면 어떻게 해야 하는가?

- `Light`가 다른 것으로부터 상속을 받을 수 없는 경우 (Java의 단일 상속 제약 등)
- `Light`가 서드파티에서 사온 것이라 소스 코드가 없는 경우
- `Switch`로 제어하고 싶은 다른 클래스가 있는데 그 클래스가 `Switchable`로부터 파생받을 수 없는 경우

여기서 **어댑터(Adapter) 패턴**이 등장한다.

### 3.1 객체 어댑터 (Object Adapter)

```
┌─────────┐         ┌────────────────┐
│ Switch  │────────▶│  «interface»   │
└─────────┘         │  Switchable    │
                    └────────┬───────┘
                             ▲
                             │
                    ┌────────┴────────┐    «delegates»    ┌───────────┐
                    │  LightAdapter   │──────────────────▶│   Light   │
                    ├─────────────────┤                   ├───────────┤
                    │ + turnOn        │                   │ + turnOn  │
                    │ + turnOff       │                   │ + turnOff │
                    └─────────────────┘                   └───────────┘
```

어댑터가 `Switchable`로부터 상속을 받은 다음 실제 일은 `Light`에게 위임한다. 이제 켜거나 끌 수만 있다면 어떤 객체라도 `Switch`로 제어할 수 있다. 제어할 객체가 `Switchable`과 동일한 `turnOn`, `turnOff` 메소드를 가질 필요도 없다. 어댑터가 말 그대로 그 객체의 인터페이스와 `Switchable` 인터페이스 사이의 어댑터 역할을 해주면 된다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java - 객체 어댑터
public class Light {
    public void activate() { /* 다른 이름의 메소드 */ }
    public void deactivate() { /* ... */ }
}

public class LightAdapter implements Switchable {
    private Light light;

    public LightAdapter(Light light) {
        this.light = light;
    }

    public void turnOn() {
        light.activate();
    }

    public void turnOff() {
        light.deactivate();
    }
}
```

</details>

```typescript
// TypeScript - 객체 어댑터
class Light {
  activate(): void {
    /* 다른 이름의 메소드 */
  }
  deactivate(): void {
    /* ... */
  }
}

class LightAdapter implements Switchable {
  constructor(private light: Light) {}

  turnOn(): void {
    this.light.activate();
  }

  turnOff(): void {
    this.light.deactivate();
  }
}
```

### 3.2 클래스 어댑터 (Class Adapter)

```
┌─────────┐         ┌────────────────┐         ┌───────────┐
│ Switch  │────────▶│  «interface»   │         │   Light   │
└─────────┘         │  Switchable    │         ├───────────┤
                    └────────┬───────┘         │ + turnOn  │
                             ▲                 │ + turnOff │
                             │                 └─────┬─────┘
                             │                       ▲
                             │                       │
                             └────────┬──────────────┘
                                      │
                             ┌────────┴────────┐
                             │  LightAdapter   │   (다중 상속)
                             ├─────────────────┤
                             │ + turnOn        │
                             │ + turnOff       │
                             └─────────────────┘
```

이 형태에서 어댑터는 `Switchable` 인터페이스와 `Light` 클래스로부터 동시에 상속을 받는다. 클래스 어댑터는 객체 어댑터보다 약간 더 효율적이고 사용하기도 약간 더 쉽지만, 그 대가로 상속에서 강한 결합이 생긴다.

> **핵심 통찰**: 탄스타플(*TANSTAAFL - There Ain't No Such Thing As A Free Lunch, 공짜 점심 같은 건 없다*). 어댑터는 싸게 먹히지 않는다. 새로 클래스도 작성해야 하고, 어댑터를 인스턴스화한 다음 어댑터가 중개할 객체와 연결해야 하며, 어댑터를 호출할 때마다 위임 때문에 추가적인 시간과 공간이라는 대가를 지불해야 한다. 따라서 매번 어댑터를 쓰고 싶지는 않을 것이다. 대부분의 경우 추상 서버 패턴만으로 충분하다.

---

## 4. 모뎀 문제 — 어댑터와 LSP

### 4.1 출발점: 평화로운 모뎀 계층 구조

모두 `Modem` 인터페이스를 사용하는 모뎀 클라이언트가 많이 있다. `Modem` 인터페이스는 `HayesModem`, `USRoboticsModem`, `ErniesModem` 등 여러 파생형에서 구현된다. OCP, LSP, DIP가 충분히 잘 지켜지고 있다.

```
                    ┌─────────────────┐
                    │  «interface»    │
                    │     Modem       │
                    ├─────────────────┤
                    │ + dial          │
                    │ + hangup        │
                    │ + send          │
                    │ + receive       │
                    └────────┬────────┘
                             ▲
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────┴──────┐    ┌────────┴───────┐    ┌──────┴──────┐
│ HayesModem   │    │ USRobotics     │    │ ErniesModem │
└──────────────┘    │ Modem          │    └─────────────┘
                    └────────────────┘

           ┌─────────────────┐
           │ Modem Clients   │────▶ (Modem 사용)
           └─────────────────┘
```

### 4.2 새 요구사항: 전용 모뎀

고객이 전화 다이얼을 걸지 않는 종류의 모뎀들이 있는데, 이런 모뎀은 전용 회선의 양쪽에 놓이기 때문에 **전용 모뎀(*dedicated modem - 다이얼 없이 전용 회선으로 통신하는 모뎀*)**이라고 한다. 이 전용 모뎀을 사용하는 새로운 애플리케이션 몇 개가 있는데, 이를 `DedUsers`라고 부른다. 하지만 고객은 지금 있는 모뎀 클라이언트들도 모두 전용 회선을 쓸 수 있게 되기를 바라며, **모뎀 클라이언트 애플리케이션 몇백 개를 고치고 싶지는 않다**고 한다.

### 4.3 이상적인 해결책 (사용 불가)

```
                ┌─────────────────┐    ┌─────────────────┐
                │  «interface»    │    │  «interface»    │
                │    Dialler      │    │     Modem       │
                ├─────────────────┤    ├─────────────────┤
                │ + dial          │    │ + send          │
                │ + hangup        │    │ + receive       │
                └────────┬────────┘    └────────┬────────┘
                         ▲                      ▲
              ┌──────────┴──────────────────────┤
              │                                 │
        Modem Clients                      DedUsers
              │                                 │
              ▼                                 ▼
   ┌──────────────────┐               ┌──────────────────┐
   │ HayesModem,      │               │ DedicatedModem   │
   │ USRobotics,      │               │                  │
   │ ErniesModem      │               │                  │
   └──────────────────┘               └──────────────────┘
```

인터페이스 분리 원칙(*ISP - Interface Segregation Principle*)을 적용하여 `Dialler`와 `Modem`을 분리한 이상적인 구조다. 하지만 이렇게 하려면 모든 모뎀 클라이언트를 수정해야 하는데, 고객이 이를 막고 있다.

### 4.4 임시방편: LSP 위반의 유혹

`Modem`으로부터 `DedicatedModem`을 파생한 다음, `dial`과 `hangup` 함수를 아무것도 하지 않는 함수로 구현하는 방법도 가능할 것이다.

<details>
<summary>원문 C++ 코드</summary>

```cpp
class DedicatedModem : public Modem {
public:
    virtual void dial(char phoneNumber[10]) {
        // 아무것도 하지 않음 - LSP 위반!
    }
    virtual void hangup() {
        // 아무것도 하지 않음
    }
    virtual void send(char c) { /* ... */ }
    virtual char receive() { /* ... */ }
};
```

</details>

```typescript
// TypeScript - LSP 위반의 위험이 있는 퇴화된 구현
class DedicatedModem implements Modem {
  dial(phoneNumber: string): void {
    // 아무것도 하지 않음 - LSP 위반!
  }
  hangup(): void {
    // 아무것도 하지 않음
  }
  send(c: string): void {
    /* ... */
  }
  receive(): string {
    return "";
  }
}
```

하지만 **퇴화된 함수(*degenerate function - 본래 의미를 잃고 빈 구현이 된 함수*)는 LSP를 위반하게 될지도 모른다는 신호**다. 모뎀 클라이언트는 아직 다이얼하지 않은 모뎀으로부터 글자가 들어올 것이라고 예상하지 않는다. 하지만 `DedicatedModem`은 `dial`이 호출되기 이전에도 글자를 보내고, `hangup`이 호출된 다음에도 그럴 것이다. 따라서 `DedicatedModem`이 일부 모뎀 클라이언트와 충돌할 수도 있다.

### 4.5 더 나쁜 임시방편: 연결 상태 시뮬레이션

이 문제를 임시방편으로 고칠 수 있다. `DedicatedModem`에서 `dial`과 `hangup` 메소드의 연결 상태를 흉내 내면 된다. `dial`이 호출되지 않았거나 `hangup`이 호출된 후라면 글자를 보내지 않으면 된다. 이제 `DedUsers`에게 그들도 `dial`과 `hangup`을 호출해야 한다는 사실을 납득시키기만 하면 된다.

```
   Modem Clients          ┌──────────────────┐
        │                  │  Dial/Hangup은   │
        ▼                  │  연결 상태를     │
   ┌─────────┐             │  시뮬레이션      │
   │  Modem  │◀─┐          │                  │
   └─────────┘  │          └──────────────────┘
                │
                │          ┌──────────────────┐
                └──────────│ DedicatedModem   │◀── DedUser
                           └──────────────────┘
```

### 4.6 의존 관계의 얽힘 — 임시방편의 비용

몇 달 후, 고객이 다시 와서 새로운 변경사항을 주문한다. 임의 길이의 전화번호를 다이얼할 수 있게 해 달라는 것이다(국제전화, 신용카드 전화 등). `dial`의 인자가 `char[10]`이었으므로 모든 모뎀 클라이언트를 다 바꿔야 한다.

그런데 **`DedUser`를 작성한 사람들한테도 가서 코드를 변경해야 한다고 말해야 한다.** 이들이 `dial` 호출을 하는 것은 그 호출이 필요해서가 아니라 우리가 그렇게 해야만 한다고 말해서다. 이제 우리가 하라는 대로 했기 때문에 비용이 많이 드는 유지보수 작업을 해야 한다.

> **Uncle Bob의 경험**: 이 예는 많은 프로젝트에서 벌어지곤 하는 지저분한 의존 관계 얽힘의 한 예다. 시스템 한 부분에서 사용한 임시방편이 결과적으로는 원래 전혀 관련이 없어야 하는 시스템의 다른 부분에서 문제를 일으키는 지저분한 의존 관계 흐름을 만든다.

### 4.7 구해주러 온 어댑터

맨 처음 문제를 풀기 위해 어댑터를 사용했더라면 이러한 큰 낭패를 피할 수 있었을 것이다.

```
   Modem Clients                                        DedUser
        │                                                  │
        ▼                                                  ▼
   ┌──────────┐                                  ┌──────────────────┐
   │  Modem   │                                  │  «interface»     │
   │«interface»│                                 │ DedicatedModem   │
   └────┬─────┘                                  ├──────────────────┤
        ▲                                        │ + send           │
        │                                        │ + receive        │
        ├──────────────┐                         └────────┬─────────┘
        │              │                                  ▲
   ┌────┴───┐  ┌───────┴──────────────┐                  │
   │ Hayes  │  │ DedicatedModemAdapter│◀───«delegates»───┘
   │ Modem  │  ├──────────────────────┤
   │  ...   │  │ + dial (simulate)    │
   └────────┘  │ + hangup (simulate)  │
               │ + send (delegate)    │
               │ + receive (delegate) │
               └──────────────────────┘
```

<details>
<summary>원문 Java 코드</summary>

```java
// Java - 어댑터 해결방법
public interface DedicatedModem {
    void send(char c);
    char receive();
}

public class DedicatedModemImpl implements DedicatedModem {
    public void send(char c) { /* 실제 송신 */ }
    public char receive() { /* 실제 수신 */ return ' '; }
}

public class DedicatedModemAdapter implements Modem {
    private DedicatedModem dedicatedModem;

    public DedicatedModemAdapter(DedicatedModem m) {
        this.dedicatedModem = m;
    }

    public void dial(String pno) {
        // 연결 상태 시뮬레이션
    }

    public void hangup() {
        // 연결 상태 시뮬레이션
    }

    public void send(char c) {
        dedicatedModem.send(c);
    }

    public char receive() {
        return dedicatedModem.receive();
    }
}
```

</details>

```typescript
// TypeScript - 어댑터 해결방법
interface DedicatedModem {
  send(c: string): void;
  receive(): string;
}

class DedicatedModemImpl implements DedicatedModem {
  send(c: string): void {
    /* 실제 송신 */
  }
  receive(): string {
    return "";
  }
}

class DedicatedModemAdapter implements Modem {
  constructor(private dedicatedModem: DedicatedModem) {}

  dial(pno: string): void {
    // 연결 상태 시뮬레이션
  }

  hangup(): void {
    // 연결 상태 시뮬레이션
  }

  send(c: string): void {
    this.dedicatedModem.send(c);
  }

  receive(): string {
    return this.dedicatedModem.receive();
  }
}
```

### 4.8 어댑터의 진정한 가치 — 임시방편의 격리

이전에 봤던 모든 어려움이 제거된다:

- `Modem`의 클라이언트들은 자기 예상대로 동작하는 연결을 보게 된다
- `DedUsers`는 `dial`이나 `hangup`을 만지작거리지 않아도 된다
- 전화번호 요구사항이 변경되더라도 `DedUsers`는 영향받지 않는다

어댑터를 배치함으로써 ISP와 OCP 위반을 모두 고친 것이다.

> **핵심 통찰**: 임시방편은 그대로 남아 있지만 — 어댑터는 여전히 연결 상태를 흉내 내고 있다 — **모든 의존 관계 화살표의 방향이 어댑터에서 외부로 나가는 방향**이다. 임시방편은 거의 대부분의 사람이 있는지도 모르는 어댑터 안에 갇혀서 시스템으로부터 분리되어 있다. 어댑터에 의존하는 유일한 고정된 의존 관계가 있다면, 그것은 아마 어딘가에 있는 팩토리의 구현뿐일 것이다.

---

## 5. 브리지 패턴 (Bridge)

이 문제를 풀기 위한 또 다른 방법도 있다. 전용 모뎀에 대한 필요 때문에 `Modem` 타입 계층 구조에 새로운 **자유도(*degrees of freedom - 어떤 물체의 상태를 표시할 수 있는 최소한의 독립된 변수의 수*)**가 추가되었다.

처음에 `Modem`은 단지 여러 하드웨어 장치들에 대한 인터페이스일 뿐이었다 — `HayesModem`, `USRModem`, `ErniesModem`. 하지만 이제 `Modem` 계층 구조를 나누는 또 다른 방법이 생겼다: `DialModem`과 `DedicatedModem`.

### 5.1 단순 결합의 폭발

```
                    ┌────────┐
                    │ Modem  │
                    └────┬───┘
                         ▲
              ┌──────────┴──────────┐
              │                     │
         ┌────┴─────┐         ┌─────┴─────────┐
         │DialModem │         │DedicatedModem │
         └────┬─────┘         └───────┬───────┘
              ▲                       ▲
       ┌──────┼──────┐         ┌──────┼──────┐
       │      │      │         │      │      │
   Hayes    USR   Ernie's   Hayes   USR   Ernie's
   Dial     Dial   Dial     Ded     Ded   Ded
```

새로운 하드웨어를 추가할 때마다 클래스를 2개씩 만들어야 한다. 새로운 연결 타입을 추가하면 하드웨어마다 클래스를 3개씩 만들어야 한다. **이 두 가지 자유도가 모두 쉽게 바뀌는 성질의 것이라면, 얼마 지나지 않아 엄청난 수의 파생 클래스가 생길 것이다.**

### 5.2 브리지 패턴의 구조

이렇게 타입 계층 구조의 자유도가 하나 이상인 상황이라면 **브리지(Bridge) 패턴**이 종종 도움이 된다. 계층 구조를 합치는 대신 각각을 분리해 놓고 브리지를 통해 서로 하나로 연결한다.

```
Modem Clients
     │
     ▼
┌───────────────┐
│ «interface»   │
│    Modem      │
├───────────────┤
│ + dial        │
│ + hangup      │
│ + send        │
│ + receive     │
└───────┬───────┘
        ▲
        │
┌───────┴────────────────┐
│ ModemConnection        │           ┌─────────────────────┐
│ Controller (abstract)  │           │  «interface»        │
├────────────────────────┤───────────│  ModemImplementation│
│ # dialImp              │«delegates»├─────────────────────┤
│ # hangImp              │           │ + dial              │
│ # sendImp              │           │ + hangup            │
│ # receiveImp           │           │ + send              │
│ + dial                 │           │ + receive           │
│ + hangup               │           └──────────┬──────────┘
│ + send                 │                      ▲
│ + receive              │           ┌──────────┼──────────┐
└──────┬─────────────────┘           │          │          │
       ▲                          Hayes      Ernie's    USRobotics
       │                          Modem      Modem      Modem
┌──────┴─────────┐  ┌──────────────┐
│ DialModem      │  │ DedModem     │
│ Controller     │  │ Controller   │
└────────────────┘  └──────────────┘
                          ▲
                          │
                    ┌─────┴──────────┐
                    │ «interface»    │
                    │ DedicatedModem │
                    └────────────────┘
                          │
                          ▼
                       DedUser
```

### 5.3 동작 방식

- `Modem` 사용자는 그대로 `Modem` 인터페이스를 사용한다
- `ModemConnectionController`가 `Modem` 인터페이스를 구현한다
- `ModemConnectionController`의 파생형들이 연결 메커니즘을 제어한다
- `DialModemController`는 `dial`과 `hangup` 호출을 `ModemConnectionController` 기반 클래스의 `dialImp`와 `hangImp`에게 전달한다
- 이 메소드들은 적절한 하드웨어 제어기가 구현하고 있는 `ModemImplementation`에게 실제 작업을 위임한다
- `DedModemController`의 `dial`과 `hangup` 구현은 연결 상태를 흉내 내기만 한다
- `DedModemController`의 `send`와 `receive`는 `sendImp`와 `receiveImp`에게 위임한다

<details>
<summary>원문 Java 코드</summary>

```java
// Java - 브리지 패턴
public interface Modem {
    void dial(String pno);
    void hangup();
    void send(char c);
    char receive();
}

public interface ModemImplementation {
    void dial(String pno);
    void hangup();
    void send(char c);
    char receive();
}

public abstract class ModemConnectionController implements Modem {
    protected ModemImplementation imp;

    protected void dialImp(String pno)  { imp.dial(pno); }
    protected void hangImp()            { imp.hangup(); }
    protected void sendImp(char c)      { imp.send(c); }
    protected char receiveImp()         { return imp.receive(); }
}

public class DialModemController extends ModemConnectionController {
    public void dial(String pno)   { dialImp(pno); }
    public void hangup()           { hangImp(); }
    public void send(char c)       { sendImp(c); }
    public char receive()          { return receiveImp(); }
}

public class DedModemController extends ModemConnectionController {
    public void dial(String pno)   { /* 시뮬레이션 */ }
    public void hangup()           { /* 시뮬레이션 */ }
    public void send(char c)       { sendImp(c); }
    public char receive()          { return receiveImp(); }
}
```

</details>

```typescript
// TypeScript - 브리지 패턴
interface Modem {
  dial(pno: string): void;
  hangup(): void;
  send(c: string): void;
  receive(): string;
}

interface ModemImplementation {
  dial(pno: string): void;
  hangup(): void;
  send(c: string): void;
  receive(): string;
}

abstract class ModemConnectionController implements Modem {
  protected imp!: ModemImplementation;

  protected dialImp(pno: string): void {
    this.imp.dial(pno);
  }
  protected hangImp(): void {
    this.imp.hangup();
  }
  protected sendImp(c: string): void {
    this.imp.send(c);
  }
  protected receiveImp(): string {
    return this.imp.receive();
  }

  abstract dial(pno: string): void;
  abstract hangup(): void;
  abstract send(c: string): void;
  abstract receive(): string;
}

class DialModemController extends ModemConnectionController {
  dial(pno: string): void {
    this.dialImp(pno);
  }
  hangup(): void {
    this.hangImp();
  }
  send(c: string): void {
    this.sendImp(c);
  }
  receive(): string {
    return this.receiveImp();
  }
}

class DedModemController extends ModemConnectionController {
  dial(pno: string): void {
    /* 시뮬레이션 */
  }
  hangup(): void {
    /* 시뮬레이션 */
  }
  send(c: string): void {
    this.sendImp(c);
  }
  receive(): string {
    return this.receiveImp();
  }
}
```

`ModemConnectionController`의 `imp` 함수 4개의 접근성이 보호(`protected`)라는 것에 주목하자. 오직 `ModemConnectionController`의 파생형들만이 이 함수들을 사용하기 때문이다.

### 5.4 브리지의 강점

이 구조는 복잡하지만 흥미롭다. 모뎀 사용자에게 아무 영향을 주지 않으면서도 만들 수 있는 구조이지만, 그럼에도 **연결에 대한 정책과 하드웨어 구현의 완벽한 분리**를 가능하게 한다.

- `ModemConnectionController`의 파생형들마다 연결에 대한 새로운 정책을 나타낸다
- 정책들은 자신의 정책을 구현하기 위해 `sendImp`, `receiveImp`, `dialImp`, `hangImp`를 사용할 수 있다
- 사용자에게 영향을 주지 않고 새로운 `imp` 함수들을 만들 수도 있다
- 연결 컨트롤러 클래스에 새로운 인터페이스를 추가할 때 ISP를 사용할 수도 있다 — `dial`/`hangup` 수준보다 높은 수준의 API를 향해 모뎀 클라이언트들이 천천히 옮겨갈 수 있는 이주 경로를 만들 수 있다

---

## 6. 세 패턴 비교

| 항목 | 추상 서버 (Abstract Server) | 어댑터 (Adapter) | 브리지 (Bridge) |
|------|----------------------------|------------------|------------------|
| **목적** | 클라이언트가 추상에 의존 | 호환되지 않는 인터페이스 연결 | 두 자유도를 독립적으로 변경 |
| **구조** | 클라이언트 → 인터페이스 ← 서버 | 클라이언트 → 인터페이스 ← 어댑터 → 어댑티 | 추상 계층 + 구현 계층 (브리지로 연결) |
| **상속 사용** | 서버가 인터페이스 구현 | 클래스 어댑터(상속) / 객체 어댑터(위임) | 양쪽 모두 독립적 상속 + 위임 |
| **비용** | 매우 낮음 — 인터페이스 하나만 추가 | 중간 — 어댑터 클래스 작성, 위임 오버헤드 | 높음 — 두 계층 구조 + 브리지 |
| **언제 쓰는가** | DIP/OCP 적용 — 가장 흔한 경우 | 서드파티/레거시 코드와 통합, 인터페이스 불일치 | 자유도가 둘 이상이고 둘 다 자주 변경됨 |
| **임시방편 격리** | 해당 없음 | **어댑터 안에 격리** — 핵심 장점 | 컨트롤러 안에 정책 격리 |
| **단점** | SRP 위반 가능 — 서버가 인터페이스 책임도 짐 | 위임 오버헤드, 객체 수 증가 | 복잡도 — 강한 확신 없으면 권장 안 함 |

---

## 7. 자주 하는 실수

| 안티패턴 | 문제 | 해결 |
|----------|------|------|
| **구체 클래스에 직접 의존** | DIP/OCP 위반, 확장 불가 | 추상 서버 패턴 — 인터페이스 도입 |
| **상속으로 확장** (`FanSwitch extends Switch`) | DIP 여전히 위반, 결합 가중 | 인터페이스 기반 다형성 사용 |
| **인터페이스 이름을 파생형 위주로 짓기** (`ILight`) | 인터페이스가 파생형에 종속 | 클라이언트 위주 명명 (`Switchable`) |
| **퇴화된 함수로 LSP 위반** | 빈 구현이 클라이언트 예상을 깨뜨림 | 어댑터로 인터페이스를 맞추기 |
| **임시방편을 시스템 전체에 퍼뜨림** | 의존 관계 얽힘, 유지보수 폭증 | 임시방편을 어댑터 안에 격리 |
| **자유도가 1개인데 브리지 적용** | 불필요한 복잡성 | 자유도가 둘 이상이고 둘 다 변경될 때만 브리지 |
| **모든 경우에 어댑터 사용** | 위임 오버헤드, 클래스 폭증 | 대부분의 경우 추상 서버로 충분 |

---

## 8. 결론

`Modem` 시나리오의 진정한 문제점은 초기 설계자들이 설계를 잘못했기 때문이란 말을 꺼내고 싶은 유혹을 느꼈을 수도 있다. 초기 설계자들은 연결과 통신이 별개의 개념이라는 사실을 알고 있어야 했다. 조금만 더 분석했다면, 이 사실을 발견하고 설계를 제대로 고칠 수도 있었다.

> **핵심 통찰**: 하지만 그건 말도 안 되는 소리다! 이 세상에 충분한 분석 같은 것은 없다. 완벽한 소프트웨어 구조를 생각해 내기 위해 얼마나 많은 시간을 쏟아붓든 상관없이, **고객은 언제나 그 구조를 망쳐버릴 새로운 변경사항을 들고 나온다**는 사실을 알게 될 것이다.

이것을 벗어날 수 있는 방법은 없다. 완벽한 구조란 존재하지 않는다. 오직 **지금 드는 비용과 얻을 수 있는 이점 사이의 균형을 잘 잡는 구조**들만 있을 뿐이다. 시간이 흐르면서 시스템에 대한 요구사항이 변경되면 이 구조들도 변경되어야 한다. **이런 변경들을 잘해 나갈 수 있는 비결은 시스템을 되도록 단순하고 유연하게 유지하는 것**이다.

| 해결 방법 | 평가 |
|-----------|------|
| **어댑터** | 단순하고 정확하다. 모든 의존 관계가 계속 올바른 방향을 가리키게 만들고, 구현하기도 매우 쉽다. |
| **브리지** | 상당히 복잡하다. 연결과 통신 정책을 분리할 필요와 새로운 연결 정책을 추가할 필요가 있다는 **강한 확신이 없다면 권하지 않는다**. |

> **Uncle Bob의 경험**: 언제나 마찬가지로 여기서 배울 교훈은, **어떤 패턴을 사용할 때 이점만 생기는 것이 아니라 비용도 따라온다**는 것이다. 지금 풀고 있는 문제에 가장 잘 맞는 패턴을 사용해야 한다.

---

## 요약

- **세 패턴은 같은 의존성 역전 원리의 변형**이다. 클라이언트가 구체 클래스에 의존하지 않도록 인터페이스를 도입하는 것이 공통 아이디어다.
- **추상 서버 (Abstract Server)** — 가장 단순한 형태. 클라이언트와 서버 사이에 인터페이스를 두어 DIP와 OCP를 충족시킨다. 대부분의 경우 이것으로 충분하다.
- **어댑터 (Adapter)** — 호환되지 않는 인터페이스를 연결한다. **객체 어댑터(위임 기반)**와 **클래스 어댑터(다중 상속 기반)**가 있다. 클래스 어댑터는 더 효율적이지만 강한 결합이 생긴다.
- **인터페이스의 소유권은 클라이언트에게 있다.** `ILight`가 아니라 `Switchable`로 이름 짓는 이유다. 클라이언트와 인터페이스 사이의 구속력이 인터페이스와 파생형 사이의 구속력보다 강하다.
- **어댑터의 진정한 가치는 임시방편의 격리**다. 보기 흉한 코드는 어댑터 안에 갇히고, 모든 의존 관계 화살표는 어댑터에서 외부로만 나간다. 시스템의 나머지가 오염되지 않는다.
- **퇴화된 함수는 LSP 위반의 신호**다. 빈 구현을 가진 파생 클래스는 클라이언트 예상을 깨뜨려 시스템 전반에 의존 관계 얽힘을 만든다.
- **브리지 (Bridge)** — 타입 계층의 자유도가 둘 이상일 때 사용한다. 추상화 계층과 구현 계층을 분리해 각각을 독립적으로 확장 가능하게 만든다. 복잡도가 높아 강한 확신이 있을 때만 권장된다.
- **완벽한 구조는 존재하지 않는다.** 비용과 이점의 균형을 잡아야 하며, 시스템을 단순하고 유연하게 유지하는 것이 핵심이다.
- **모든 패턴은 이점과 비용을 동시에 갖는다.** 지금 풀고 있는 문제에 가장 잘 맞는 패턴을 선택하라.
