# Chapter 24: The Observer Pattern (옵저버 패턴 — 패턴으로 돌아가기)

## 핵심 질문

디자인 패턴(*Design Pattern - 자주 등장하는 설계 문제에 대한 재사용 가능한 해결책*)은 설계의 시작점인가, 도착점인가? 옵저버(*Observer - 한 객체의 상태 변화를 다른 여러 객체에 자동으로 통지하는 패턴*) 패턴은 어떻게 만들어지는가 — 처음부터 의도해서 만드는가, 아니면 문제를 풀다 보니 자연스럽게 도달하는가? 그리고 — 옵저버 패턴이 어떻게 SOLID 원칙을 구현해 내는가?

> 옵저버는 GoF의 가장 유명한 패턴 중 하나이지만, 동시에 가장 오용되기 쉬운 패턴이기도 하다.

---

## 1. 패턴은 시작이 아니라 도착점이다

이 장의 목표는 조금 특별하다. 옵저버 패턴을 설명하긴 하지만, 이는 부차적인 목적일 뿐이고, 근본적인 목적은 **패턴을 사용해서 설계와 코드를 진화시키는 방법**을 보여주는 데 있다.

### 1.1 패턴을 끼워 넣지 마라

이전 장들에서도 패턴은 많이 사용해 왔다. 하지만 대부분의 경우 어떻게 코드가 패턴을 사용하는 방향으로 진화했는지를 보여주지 않고 그냥 패턴 사용을 기정사실화한 적이 많았다. 따라서 **패턴이란 코드나 설계에 완전한 형태로 끼워 넣을 수 있는 것**이라는 인상을 심어 주었을지도 모르겠다. 하지만 저자는 이런 식의 패턴 사용을 권장하지 않는다.

> **Uncle Bob의 경험**: 나는 오히려 작업 중인 코드를 그 코드의 필요에 맞는 방향으로 진화시키는 편을 선호한다. 결합, 단순화, 표현 능력에 관련된 문제를 해결하기 위해 코드를 리팩토링하다 보면 코드가 어떤 패턴과 비슷한 형태가 되는 것을 발견하는 경우가 생긴다. 그런 일이 생기면 그때 비로소 패턴의 이름이 들어가도록 클래스와 변수의 이름을 바꾸고, 더 정규적인 형태로 그 패턴을 사용하기 위해 코드의 구조도 변경한다. **즉, 코드가 패턴으로 "돌아가는" 것이다.**

### 1.2 이 장이 보여주려 하는 것

이 장에서는 간단한 문제를 하나 제시하고 어떻게 설계와 코드가 그 문제를 풀기 위해 진화해 가는지를 보일 것이다. 이 진화의 결과는 결국 옵저버 패턴이 되는 것으로 끝난다.

> **핵심 통찰**: 패턴을 외워서 적용하는 것과 문제 해결을 거쳐 패턴으로 자연스럽게 도달하는 것은 천지 차이다. 전자는 과잉설계로 이어지지만, 후자는 코드의 실제 필요에 정확히 부합하는 설계를 만들어 낸다.

---

## 2. 문제: 디지털 시계

여기 시계 객체가 하나 있다. 이 객체는 운영체제에서 보내는 밀리초 인터럽트(틱(*tic - 운영체제가 일정 시간 간격으로 보내는 시간 신호*))를 잡아서 날짜와 시각으로 바꾼다. 이 객체는 밀리초에서 초, 초에서 분, 분에서 시, 시에서 날짜를 계산하는 방법을 안다. 한마디로, **이 객체는 시간에 대해 알고 있다.**

```
        ┌──────────────────┐
        │       OS         │
        └────────┬─────────┘
                 │ tic (밀리초 인터럽트)
                 ▼
        ┌──────────────────┐
        │      Clock       │
        ├──────────────────┤
        │ + getSeconds()   │
        │ + getMinutes()   │
        │ + getHours()     │
        │ + tic()          │
        └──────────────────┘
```

우리가 만들고 싶은 것은 데스크탑 컴퓨터 위에 놓여서 날짜와 시간을 계속 보여주는 **디지털 시계**다. 가장 단순한 방법은 다음과 같다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public void displayTime() {
    while (true) {
        int sec = clock.getSeconds();
        int min = clock.getMinutes();
        int hour = clock.getHours();
        showTime(hour, min, sec);
    }
}
```

</details>

```typescript
// TypeScript
function displayTime(): void {
    while (true) {
        const sec = clock.getSeconds();
        const min = clock.getMinutes();
        const hour = clock.getHours();
        showTime(hour, min, sec);
    }
}
```

### 2.1 폴링의 문제

하지만 이 코드는 좋은 방법이 아니다. 시각이 바뀔 때마다 표시하기 위해 **사용 가능한 모든 CPU 사이클을 다 잡아먹는다**. 시각은 대부분 바뀌지 않으므로 화면 갱신의 대다수는 사실 필요가 없다. 디지털 손목시계나 벽시계라면 모를까, 컴퓨터 데스크탑에서 이런 CPU 잡아먹는 귀신을 돌리고 싶어 하는 사람은 없다.

근본적인 문제는 `Clock`에서 `DigitalClock`으로 **자료를 효율적으로 전달하는 방법**이다.

---

## 3. 진화 1단계 — 테스트 가능한 분리

`Clock`과 `DigitalClock`은 이미 존재한다고 가정하자. 관심사는 이 둘을 연결하는 방법이다. 연결이 올바른지는 `Clock`에서 얻은 데이터와 `DigitalClock`으로 보낸 데이터가 동일한지 확인해 보면 된다.

### 3.1 인터페이스 도입

`Clock`인 것처럼 행세하는 인터페이스 하나(`TimeSource`)와 `DigitalClock`인 것처럼 행세하는 또 다른 인터페이스(`TimeSink`)를 만든 다음, 이 인터페이스들을 구현하는 의사 객체(*mock object - 테스트를 위해 실제 객체의 동작을 흉내 내는 가짜 객체*)들을 만들어 연결을 검증한다.

```
   ┌──────────────────┐
   │   ClockDriver    │
   └─────┬──────┬─────┘
         │      │
   ┌─────▼──┐ ┌─▼────────┐
   │«iface» │ │«iface»   │
   │TimeSrc │ │TimeSink  │
   └────▲───┘ └────▲─────┘
        │          │
   ┌────┴──┐  ┌────┴────┐
   │Clock  │  │Digital  │
   │       │  │ Clock   │
   └───────┘  └─────────┘
        ▲          ▲
   ┌────┴──────────┴───┐
   │ ClockDriverTest   │
   └───────────────────┘
```

> **핵심 통찰**: 어떻게 설계를 테스트해 볼지 생각해 본 결과로 **설계에 인터페이스를 추가했다**. 테스트를 먼저 생각해 보는 것이 설계에서 결합을 줄이는 데 도움이 되었다.

### 3.2 ClockDriver의 동작

`ClockDriver`는 효율적이어야 하므로 `TimeSource`에서 시각이 바뀔 때 그것을 감지할 수 있어야 한다. 폴링은 다시 CPU 사이클 문제를 만든다. 가장 간단한 방법은 **시각이 바뀌었을 때 `Clock`이 `ClockDriver`에게 말해 주는 것**이다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java - ClockDriver.java
public class ClockDriver {
    private TimeSink itsSink;

    public ClockDriver(TimeSource source, TimeSink sink) {
        source.setDriver(this);
        itsSink = sink;
    }

    public void update(int hours, int minutes, int seconds) {
        itsSink.setTime(hours, minutes, seconds);
    }
}

// MockTimeSource.java
public class MockTimeSource implements TimeSource {
    private ClockDriver itsDriver;

    public void setTime(int hours, int minutes, int seconds) {
        itsDriver.update(hours, minutes, seconds);
    }

    public void setDriver(ClockDriver driver) {
        itsDriver = driver;
    }
}

// TimeSource.java
public interface TimeSource {
    void setDriver(ClockDriver driver);
}

// TimeSink.java
public interface TimeSink {
    void setTime(int hours, int minutes, int seconds);
}
```

</details>

```typescript
// TypeScript
class ClockDriver {
    private itsSink: TimeSink;

    constructor(source: TimeSource, sink: TimeSink) {
        source.setDriver(this);
        this.itsSink = sink;
    }

    update(hours: number, minutes: number, seconds: number): void {
        this.itsSink.setTime(hours, minutes, seconds);
    }
}

class MockTimeSource implements TimeSource {
    private itsDriver!: ClockDriver;

    setTime(hours: number, minutes: number, seconds: number): void {
        this.itsDriver.update(hours, minutes, seconds);
    }

    setDriver(driver: ClockDriver): void {
        this.itsDriver = driver;
    }
}

interface TimeSource {
    setDriver(driver: ClockDriver): void;
}

interface TimeSink {
    setTime(hours: number, minutes: number, seconds: number): void;
}
```

### 3.3 첫 번째 문제 — TimeSource → ClockDriver 의존

`TimeSource`에서 `ClockDriver`로 의존 관계가 생긴다. 이는 `setDriver` 메소드의 인자가 `ClockDriver`이기 때문이다. **이 말은 `TimeSource` 객체는 항상 `ClockDriver` 객체를 사용해야 한다는 의미가 되므로 만족스럽지 않다.**

---

## 4. 진화 2단계 — ClockObserver 인터페이스 도입

`TimeSource`를 `ClockDriver` 말고도 누구든 쓸 수 있게 하고 싶다. `TimeSource`가 사용하고 `ClockDriver`가 구현할 인터페이스를 하나 만들면 이 문제를 해결할 수 있다. 이 인터페이스를 `ClockObserver`라고 부르자.

```
                ┌─────────────────┐
                │ «interface»     │
                │ ClockObserver   │
                │ + update()      │
                └────────▲────────┘
                         │ implements
                ┌────────┴────────┐
                │  ClockDriver    │
                │  + update()     │
                └────────┬────────┘
                         │
       ┌─────────────────┴─────────────┐
       ▼                               ▼
┌──────────────┐                ┌─────────────┐
│ «interface»  │                │ «interface» │
│ TimeSource   │                │ TimeSink    │
│ + setObserver│                │ + setTime   │
└──────▲───────┘                └──────▲──────┘
       │                               │
┌──────┴───────┐                ┌──────┴──────┐
│MockTimeSource│                │MockTimeSink │
└──────────────┘                └─────────────┘
```

<details>
<summary>원문 Java 코드</summary>

```java
// ClockObserver.java
public interface ClockObserver {
    void update(int hours, int minutes, int seconds);
}

// ClockDriver.java
public class ClockDriver implements ClockObserver {
    private TimeSink itsSink;

    public ClockDriver(TimeSource source, TimeSink sink) {
        source.setObserver(this);
        itsSink = sink;
    }

    public void update(int hours, int minutes, int seconds) {
        itsSink.setTime(hours, minutes, seconds);
    }
}

// TimeSource.java
public interface TimeSource {
    void setObserver(ClockObserver observer);
}
```

</details>

```typescript
// TypeScript
interface ClockObserver {
    update(hours: number, minutes: number, seconds: number): void;
}

class ClockDriver implements ClockObserver {
    private itsSink: TimeSink;

    constructor(source: TimeSource, sink: TimeSink) {
        source.setObserver(this);
        this.itsSink = sink;
    }

    update(hours: number, minutes: number, seconds: number): void {
        this.itsSink.setTime(hours, minutes, seconds);
    }
}

interface TimeSource {
    setObserver(observer: ClockObserver): void;
}
```

이제 누구나 `ClockObserver`를 구현하고 자신을 인자로 해서 `setObserver`를 부르기만 하면 `TimeSource`를 활용할 수 있다.

---

## 5. 진화 3단계 — ClockDriver 자체를 제거

이제 여러 개의 `TimeSink`가 시각을 받을 수 있게 하고 싶다. 하나는 디지털 시계에, 다른 하나는 약속 알림 서비스에, 또 다른 하나는 심야 백업 시작에 쓸 수도 있다. **하나의 `TimeSource`가 여러 `TimeSink` 객체에 시각을 공급할 수 있었으면 좋겠다.**

### 5.1 깨달음 — TimeSink와 ClockObserver는 같다

`ClockObserver`와 `TimeSink`를 보니, 둘 다 `setTime`(혹은 `update`) 메소드가 있다. **`TimeSink`가 `ClockObserver`를 구현하게 만들어도 될 것 같다.** 그렇다면 테스트 프로그램은 `MockTimeSink`를 하나 만들어서 그것을 인자로 `TimeSource`의 `setObserver`를 호출하면 된다. `ClockDriver`(와 `TimeSink`)를 모두 없앨 수 있다!

> **Uncle Bob의 경험**: 왜 처음에는 `ClockDriver`가 필요하다고 생각했는지 모르겠다. 코드를 진화시키다 보면 처음 도입한 추상이 사실 불필요했음을 발견하는 일이 종종 있다.

<details>
<summary>원문 Java 코드</summary>

```java
// MockTimeSink.java
public class MockTimeSink implements ClockObserver {
    private int itsHours;
    private int itsMinutes;
    private int itsSeconds;

    public int getSeconds() { return itsSeconds; }
    public int getMinutes() { return itsMinutes; }
    public int getHours()   { return itsHours; }

    public void update(int hours, int minutes, int seconds) {
        itsHours = hours;
        itsMinutes = minutes;
        itsSeconds = seconds;
    }
}
```

</details>

```typescript
// TypeScript
class MockTimeSink implements ClockObserver {
    private itsHours = 0;
    private itsMinutes = 0;
    private itsSeconds = 0;

    getSeconds(): number { return this.itsSeconds; }
    getMinutes(): number { return this.itsMinutes; }
    getHours():   number { return this.itsHours; }

    update(hours: number, minutes: number, seconds: number): void {
        this.itsHours = hours;
        this.itsMinutes = minutes;
        this.itsSeconds = seconds;
    }
}
```

이렇게 하는 편이 훨씬 간단하다.

---

## 6. 진화 4단계 — 여러 옵저버 등록 지원

`setObserver` 함수를 `registerObserver`로 바꾸고, 등록된 `ClockObserver` 인스턴스들의 목록(`Vector`)에 저장한 다음 갱신 시 순회하도록 만든다.

<details>
<summary>원문 Java 코드</summary>

```java
// TimeSource.java
public interface TimeSource {
    void registerObserver(ClockObserver observer);
}

// MockTimeSource.java
import java.util.Iterator;
import java.util.Vector;

public class MockTimeSource implements TimeSource {
    private Vector itsObservers = new Vector();

    public void setTime(int hours, int minutes, int seconds) {
        Iterator i = itsObservers.iterator();
        while (i.hasNext()) {
            ClockObserver observer = (ClockObserver) i.next();
            observer.update(hours, minutes, seconds);
        }
    }

    public void registerObserver(ClockObserver observer) {
        itsObservers.add(observer);
    }
}
```

</details>

```typescript
// TypeScript
interface TimeSource {
    registerObserver(observer: ClockObserver): void;
}

class MockTimeSource implements TimeSource {
    private itsObservers: ClockObserver[] = [];

    setTime(hours: number, minutes: number, seconds: number): void {
        for (const observer of this.itsObservers) {
            observer.update(hours, minutes, seconds);
        }
    }

    registerObserver(observer: ClockObserver): void {
        this.itsObservers.push(observer);
    }
}
```

### 6.1 또 다른 통찰 — 등록/갱신 로직은 TimeSource에 속한다

`Clock`이나 `TimeSource`의 모든 파생 클래스마다 똑같은 등록과 갱신 코드를 만들기는 싫다. 따라서 관련된 모든 코드를 `TimeSource`로 옮긴다. 그러면 `TimeSource`를 인터페이스에서 클래스로 바꾸어야 하지만 코드 중복이 해결된다.

<details>
<summary>원문 Java 코드</summary>

```java
// TimeSource.java (클래스로 변경)
import java.util.Iterator;
import java.util.Vector;

public class TimeSource {
    private Vector itsObservers = new Vector();

    protected void notify(int hours, int minutes, int seconds) {
        Iterator i = itsObservers.iterator();
        while (i.hasNext()) {
            ClockObserver observer = (ClockObserver) i.next();
            observer.update(hours, minutes, seconds);
        }
    }

    public void registerObserver(ClockObserver observer) {
        itsObservers.add(observer);
    }
}

// MockTimeSource.java (이제 거의 비어 있다)
public class MockTimeSource extends TimeSource {
    public void setTime(int hours, int minutes, int seconds) {
        notify(hours, minutes, seconds);
    }
}
```

</details>

```typescript
// TypeScript
class TimeSource {
    private itsObservers: ClockObserver[] = [];

    protected notify(hours: number, minutes: number, seconds: number): void {
        for (const observer of this.itsObservers) {
            observer.update(hours, minutes, seconds);
        }
    }

    registerObserver(observer: ClockObserver): void {
        this.itsObservers.push(observer);
    }
}

class MockTimeSource extends TimeSource {
    setTime(hours: number, minutes: number, seconds: number): void {
        this.notify(hours, minutes, seconds);
    }
}
```

---

## 7. 진화 5단계 — Clock과 TimeSource 분리

`MockTimeSource`는 `TimeSource`에서 직접 상속을 받고 있다. 이 말은 **`Clock`도 `TimeSource`에서 파생되어야 한다는 뜻**이다. `Clock`이 옵저버 등록이나 갱신에 의존해야 할까닭이 있을까? `Clock`은 단지 시간에 대해서만 아는 클래스인데 말이다.

### 7.1 C++ 해법 — 다중 상속

C++에서는 다중 상속으로 풀 수 있다. `TimeSource`와 `Clock`을 모두 상속받는 `ObservableClock` 서브클래스를 만들면 된다.

```cpp
// C++ - ObservableClock.cc
class ObservableClock : public Clock, public TimeSource {
public:
    virtual void tic() {
        Clock::tic();
        TimeSource::notify(getHours(), getMinutes(), getSeconds());
    }
    virtual void setTime(int hours, int minutes, int seconds) {
        Clock::setTime(hours, minutes, seconds);
        TimeSource::notify(hours, minutes, seconds);
    }
};
```

```
   ┌─────────┐    ┌────────────┐
   │  Clock  │    │ TimeSource │
   └────▲────┘    └─────▲──────┘
        │               │
        └───────┬───────┘ (다중 상속)
                │
       ┌────────┴─────────┐
       │ ObservableClock  │
       └──────────────────┘
```

### 7.2 자바 해법 — 위임을 이용한 꼼수

자바에서는 클래스 다중 상속이 불가능하므로 **위임(delegation)** 을 이용해야 한다.

<details>
<summary>원문 Java 코드</summary>

```java
// TimeSource.java (다시 인터페이스로)
public interface TimeSource {
    void registerObserver(ClockObserver observer);
}

// TimeSourceImplementation.java
import java.util.Iterator;
import java.util.Vector;

public class TimeSourceImplementation {
    private Vector itsObservers = new Vector();

    public void notify(int hours, int minutes, int seconds) {
        Iterator i = itsObservers.iterator();
        while (i.hasNext()) {
            ClockObserver observer = (ClockObserver) i.next();
            observer.update(hours, minutes, seconds);
        }
    }

    public void registerObserver(ClockObserver observer) {
        itsObservers.add(observer);
    }
}

// MockTimeSource.java
public class MockTimeSource implements TimeSource {
    TimeSourceImplementation tsImp = new TimeSourceImplementation();

    public void registerObserver(ClockObserver observer) {
        tsImp.registerObserver(observer);
    }

    public void setTime(int hours, int minutes, int seconds) {
        tsImp.notify(hours, minutes, seconds);
    }
}
```

</details>

```typescript
// TypeScript
interface TimeSource {
    registerObserver(observer: ClockObserver): void;
}

class TimeSourceImplementation {
    private itsObservers: ClockObserver[] = [];

    notify(hours: number, minutes: number, seconds: number): void {
        for (const observer of this.itsObservers) {
            observer.update(hours, minutes, seconds);
        }
    }

    registerObserver(observer: ClockObserver): void {
        this.itsObservers.push(observer);
    }
}

class MockTimeSource implements TimeSource {
    private tsImp = new TimeSourceImplementation();

    registerObserver(observer: ClockObserver): void {
        this.tsImp.registerObserver(observer);
    }

    setTime(hours: number, minutes: number, seconds: number): void {
        this.tsImp.notify(hours, minutes, seconds);
    }
}
```

그다지 보기 좋지는 않지만, `MockTimeSource`가 어떤 클래스로부터도 상속받지 않는다는 장점은 있다. 즉, `ObservableClock`을 만들 때 `Clock`을 상속받고, `TimeSource`를 구현하고, 등록과 갱신은 `TimeSourceImplementation`에 위임할 수 있다.

---

## 8. 진화 6단계 — Push-Model에서 Pull-Model로

자, 미궁 속으로 들어가기 전인 진화 4단계로 다시 돌아가자. **`TimeSource`라는 이름은 이 클래스가 지금 하는 일을 보면 말도 안 되는 이름이다.** 옵저버 패턴은 이런 종류의 클래스를 **Subject** 라고 부른다.

### 8.1 push-model의 한계

지금 옵저버는 **"데이터를 밀어내는 방식"(push-model - 관찰 대상이 데이터를 `notify`/`update` 메소드의 인자로 전달하는 방식)** 이다. 이 방식은 시각을 알려주는 일에만 특화된 우리 클래스를 더 일반적인 클래스로 만들 수 없게 한다.

### 8.2 pull-model로 전환

**"데이터를 끌어오는 방식"(pull-model - 옵저버가 갱신 신호를 받으면 관찰 대상에게 데이터를 요청하는 방식)** 으로 바꾸면, `TimeSource`라는 이름을 `Subject`로 바꿀 수 있게 되어 누구든 옵저버 패턴임을 쉽게 알아볼 수 있다.

`notify`와 `update` 메소드에서 시각을 건네주는 대신, `MockTimeSink`가 `MockTimeSource`에게 시각을 묻게 만든다. `MockTimeSink`가 `MockTimeSource`에 대해 직접 알면 안 되므로, `MockTimeSink`가 시각을 얻을 때 쓸 인터페이스를 하나 만든다. 이 인터페이스의 이름을 (이제 다른 의미로) **`TimeSource`** 라고 부른다.

```
              ┌──────────────────────┐
              │      Subject         │
              │ + registerObserver() │
              │ # notifyObservers()  │
              └──────────▲───────────┘
                         │ extends
                         │
              ┌──────────┴───────────┐
              │   MockTimeSource     │
              │   + setTime()        │
              │   + getHours()       │
              │   + getMinutes()     │
              │   + getSeconds()     │
              └──────────┬───────────┘
                         │ implements
                         ▼
              ┌──────────────────────┐
              │ «interface»          │
              │ TimeSource           │
              │ + getHours()         │
              │ + getMinutes()       │
              │ + getSeconds()       │
              └──────────────────────┘
                         ▲
                         │ 참조
              ┌──────────┴───────────┐
              │ «interface» Observer │
              │ + update()           │
              └──────────▲───────────┘
                         │ implements
              ┌──────────┴───────────┐
              │   MockTimeSink       │
              └──────────────────────┘
```

### 8.3 최종 코드

<details>
<summary>원문 Java 코드</summary>

```java
// Observer.java
public interface Observer {
    void update();
}

// Subject.java
import java.util.Iterator;
import java.util.Vector;

public class Subject {
    private Vector itsObservers = new Vector();

    protected void notifyObservers() {
        Iterator i = itsObservers.iterator();
        while (i.hasNext()) {
            Observer observer = (Observer) i.next();
            observer.update();
        }
    }

    public void registerObserver(Observer observer) {
        itsObservers.add(observer);
    }
}

// TimeSource.java
public interface TimeSource {
    int getHours();
    int getMinutes();
    int getSeconds();
}

// MockTimeSource.java
public class MockTimeSource extends Subject implements TimeSource {
    private int itsHours;
    private int itsMinutes;
    private int itsSeconds;

    public void setTime(int hours, int minutes, int seconds) {
        itsHours = hours;
        itsMinutes = minutes;
        itsSeconds = seconds;
        notifyObservers();
    }

    public int getHours()   { return itsHours; }
    public int getMinutes() { return itsMinutes; }
    public int getSeconds() { return itsSeconds; }
}

// MockTimeSink.java
public class MockTimeSink implements Observer {
    private int itsHours;
    private int itsMinutes;
    private int itsSeconds;
    private TimeSource itsSource;

    public MockTimeSink(TimeSource source) {
        itsSource = source;
    }

    public int getSeconds() { return itsSeconds; }
    public int getMinutes() { return itsMinutes; }
    public int getHours()   { return itsHours; }

    public void update() {
        itsHours = itsSource.getHours();
        itsMinutes = itsSource.getMinutes();
        itsSeconds = itsSource.getSeconds();
    }
}
```

</details>

```typescript
// TypeScript
interface Observer {
    update(): void;
}

class Subject {
    private itsObservers: Observer[] = [];

    protected notifyObservers(): void {
        for (const observer of this.itsObservers) {
            observer.update();
        }
    }

    registerObserver(observer: Observer): void {
        this.itsObservers.push(observer);
    }
}

interface TimeSource {
    getHours(): number;
    getMinutes(): number;
    getSeconds(): number;
}

class MockTimeSource extends Subject implements TimeSource {
    private itsHours = 0;
    private itsMinutes = 0;
    private itsSeconds = 0;

    setTime(hours: number, minutes: number, seconds: number): void {
        this.itsHours = hours;
        this.itsMinutes = minutes;
        this.itsSeconds = seconds;
        this.notifyObservers();
    }

    getHours():   number { return this.itsHours; }
    getMinutes(): number { return this.itsMinutes; }
    getSeconds(): number { return this.itsSeconds; }
}

class MockTimeSink implements Observer {
    private itsHours = 0;
    private itsMinutes = 0;
    private itsSeconds = 0;

    constructor(private itsSource: TimeSource) {}

    getSeconds(): number { return this.itsSeconds; }
    getMinutes(): number { return this.itsMinutes; }
    getHours():   number { return this.itsHours; }

    update(): void {
        this.itsHours = this.itsSource.getHours();
        this.itsMinutes = this.itsSource.getMinutes();
        this.itsSeconds = this.itsSource.getSeconds();
    }
}
```

### 8.4 최종 테스트

<details>
<summary>원문 Java 코드</summary>

```java
import junit.framework.TestCase;

public class ObserverTest extends TestCase {
    private MockTimeSource source;
    private MockTimeSink sink;

    public ObserverTest(String name) { super(name); }

    public void setUp() {
        source = new MockTimeSource();
        sink   = new MockTimeSink(source);
        source.registerObserver(sink);
    }

    private void assertSinkEquals(MockTimeSink sink,
                                  int hours, int minutes, int seconds) {
        assertEquals(hours,   sink.getHours());
        assertEquals(minutes, sink.getMinutes());
        assertEquals(seconds, sink.getSeconds());
    }

    public void testTimeChange() {
        source.setTime(3, 4, 5);
        assertSinkEquals(sink, 3, 4, 5);
        source.setTime(7, 8, 9);
        assertSinkEquals(sink, 7, 8, 9);
    }

    public void testMultipleSinks() {
        MockTimeSink sink2 = new MockTimeSink(source);
        source.registerObserver(sink2);
        source.setTime(12, 13, 14);
        assertSinkEquals(sink,  12, 13, 14);
        assertSinkEquals(sink2, 12, 13, 14);
    }
}
```

</details>

```typescript
// TypeScript
describe('Observer', () => {
    let source: MockTimeSource;
    let sink: MockTimeSink;

    beforeEach(() => {
        source = new MockTimeSource();
        sink   = new MockTimeSink(source);
        source.registerObserver(sink);
    });

    function assertSinkEquals(
        sink: MockTimeSink,
        hours: number, minutes: number, seconds: number,
    ): void {
        expect(sink.getHours()).toBe(hours);
        expect(sink.getMinutes()).toBe(minutes);
        expect(sink.getSeconds()).toBe(seconds);
    }

    test('timeChange', () => {
        source.setTime(3, 4, 5);
        assertSinkEquals(sink, 3, 4, 5);
        source.setTime(7, 8, 9);
        assertSinkEquals(sink, 7, 8, 9);
    });

    test('multipleSinks', () => {
        const sink2 = new MockTimeSink(source);
        source.registerObserver(sink2);
        source.setTime(12, 13, 14);
        assertSinkEquals(sink,  12, 13, 14);
        assertSinkEquals(sink2, 12, 13, 14);
    });
});
```

> **핵심 통찰**: 처음에 어떤 설계 문제를 가지고 시작한 다음, 합리적인 진화를 거쳐서 **정규 옵저버 패턴**이라는 결과를 얻었다. 처음부터 옵저버를 의도하지 않았더라도, 문제를 하나씩 해결해 나가다 보면 코드가 옵저버 방향으로 가고 있다는 사실이 점점 분명해진다. 그때 이름을 바꾸고 정규형(*canonical form - 패턴의 표준적이고 인정받는 형태*)으로 정리하면 된다.

---

## 9. 옵저버 패턴 — 정규형

이제 예제를 다 살펴봤으니 옵저버 패턴이 무엇인지 정리해 볼 수 있다.

### 9.1 정규형 구조

```
              ┌──────────────────────┐
              │      Subject         │
              │ + register(Observer) │
              │ # notify()           │
              └──────────▲───────────┘
                         │
              ┌──────────┴───────────┐
              │       Clock          │
              └──────────────────────┘
                         │
                         │
              ┌──────────┴───────────┐
              │ «interface» Observer │
              │ + update()           │
              └──────────▲───────────┘
                         │
              ┌──────────┴───────────┐
              │   DigitalClock       │
              └──────────────────────┘
```

`Clock`은 `DigitalClock`의 관찰 대상이다. `DigitalClock`은 `Clock`의 `Subject` 인터페이스를 통해 자신을 등록한다. `Clock`은 시각이 변경되면 `Subject`의 `notify` 메소드를 호출하고, `notify`는 등록된 모든 `Observer`의 `update` 메소드를 호출한다. `DigitalClock`은 `update` 메시지를 받으면 `Clock`에게 시각을 묻고, 화면에 표시한다.

### 9.2 옵저버 패턴의 두 가지 방식

| 방식 | 데이터 흐름 | 적합한 경우 |
|------|-------------|--------------|
| **pull-model** (데이터를 끌어오는 방식) | `update()`는 인자 없음. 옵저버가 관찰 대상에게 변경된 데이터를 요청 | 관찰 대상이 단순할 때, Subject/Observer를 재사용 가능한 라이브러리 요소로 만들고 싶을 때 |
| **push-model** (데이터를 밀어내는 방식) | `notify(hint)` 와 `update(hint)`. 관찰 대상이 변경 단서를 인자로 전달 | 관찰 대상이 복잡해 옵저버가 어떤 변경인지 단서가 필요할 때 (예: 직원 기록의 어느 필드가 바뀌었는지) |

> **핵심 통찰**: 두 옵저버 방식 가운데 하나를 고르는 기준은 **관찰 대상 객체의 복잡도**다. 관찰 대상이 복잡해 옵저버가 변경 단서를 받아야 한다면 push-model, 단순하다면 pull-model로 충분하다.

### 9.3 옵저버의 위험

> **Uncle Bob의 경험**: 옵저버는 한번 이해하고 나면 도처에서 사용 예를 볼 수 있게 되는 패턴이다. 이 패턴의 **간접 참조**는 매우 훌륭한데, 객체들이 명시적으로 관찰 대상을 호출하도록 작성하는 대신 옵저버로 등록만 하면 된다. 하지만 너무 극단적으로 사용하기 쉽다. **옵저버의 지나친 사용은 시스템을 이해하거나 추적하기 굉장히 어렵게 만든다.**

---

## 10. 옵저버는 어떻게 OOD 원칙을 구현하는가

옵저버 패턴이 강력한 이유는 SOLID 원칙들을 자연스럽게 구현해 내기 때문이다.

| 원칙 | 옵저버에서의 구현 |
|------|-------------------|
| **OCP** (개방-폐쇄 원칙) | 관찰 대상을 변경하지 않고도 새로운 관찰자를 추가할 수 있다. 이 패턴 사용의 가장 큰 동기 |
| **LSP** (리스코프 치환 원칙) | `Clock`을 `Subject`로, `DigitalClock`을 `Observer`로 교체 가능 |
| **DIP** (의존관계 역전 원칙) | 구체 클래스 `DigitalClock`이 추상 `Observer`에 의존, `Subject`의 구체 메소드도 `Observer`에 의존 |
| **ISP** (인터페이스 분리 원칙) | `Subject`와 `TimeSource`가 `MockTimeSource`의 서로 다른 클라이언트들에게 각자 전문화된 인터페이스를 제공 |

### 10.1 Subject는 추상 클래스인가

`Subject`에 추상 메소드가 없으므로 `Clock`과 `Subject`의 의존 관계가 DIP를 위반한다고 생각할 수도 있다. 하지만 **`Subject`는 자체적으로 인스턴스화되어서는 절대 안 되는 클래스다.** 파생 클래스의 맥락에서만 의미를 지니므로 논리적으로는 추상 클래스다. `Subject`의 생성자를 `protected`로 만들거나 C++라면 순수 가상 소멸자를 만들어 추상성을 강제로 부여할 수 있다.

---

## 11. 다이어그램은 일시적이다 — 보관하지 마라

이 장의 다이어그램 몇 개는 독자의 편의를 위해서 그렸다. 모든 것을 밝히고 설명하려 했기 때문이다. 하지만 저자 자신의 편의를 위해 만든 다이어그램도 있다 — 다음에 어떻게 해야 할지 알기 위해 만든 구조를 뚫어지게 봐야 할 때가 있었기 때문이다.

> **Uncle Bob의 경험**: 책 쓰는 일이 아니었다면, 나는 이런 다이어그램을 종잇조각이나 칠판에 손으로 그렸을 것이다. 그림 그리는 도구를 쓰려고 시간을 쓰지는 않았을 것이다. 코드를 진화시키는 데 도움이 되도록 다이어그램을 사용한 다음에도, 다이어그램을 보관하지는 않았을 것이다. **내가 그린 다이어그램은 언제나 중간 단계일 뿐이었다.** 보통 이런 다이어그램들은 일시적이며, 일이 끝나면 버리는 편이 낫다.

이 정도의 세부 수준에서는 **코드 스스로 충분히 자기를 설명할 수 있는 경우가 대부분**이다. 다만 더 높은 수준에서는 항상 그렇지는 않다.

---

## 요약

- **패턴은 시작이 아니라 도착점이다.** 패턴을 코드에 끼워 넣지 말고, 코드의 필요에 따라 진화시키다 보면 자연스럽게 패턴으로 "돌아가게" 된다
- 디지털 시계 예제는 폴링의 비효율 → 인터페이스 도입 → `ClockObserver` 도출 → `ClockDriver` 제거 → 여러 옵저버 지원 → `TimeSource` 분리 → push-model → pull-model 의 순서로 진화했다
- 진화 과정에서 처음 도입한 추상(`ClockDriver`)이 사실 불필요했음을 발견하는 일이 종종 있다 — **코드가 말해 줄 때까지 들어 보라**
- **테스트를 먼저 생각하는 것**이 설계의 결합을 줄이는 데 큰 도움이 된다 (인터페이스가 자연스럽게 도출됨)
- 옵저버에는 두 가지 방식이 있다:
  - **pull-model**: 옵저버가 변경 후 관찰 대상에게 데이터를 요청 (단순한 경우에 적합)
  - **push-model**: `notify`/`update`의 인자로 변경 단서를 전달 (복잡한 관찰 대상에 적합)
- 옵저버 패턴은 **OCP·LSP·DIP·ISP** 를 모두 자연스럽게 구현한다 — 특히 OCP가 가장 중요한 동기
- 옵저버의 간접 참조는 강력하지만 **남용 금지** — 지나치게 쓰면 시스템 추적이 어려워진다
- 진화 과정에서 그린 다이어그램은 **일시적인 도구**다. 코드가 정착한 뒤에는 보관하지 말고 버리는 편이 낫다
