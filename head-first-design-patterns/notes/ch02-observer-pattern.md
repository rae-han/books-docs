# Chapter 02: The Observer Pattern (옵저버 패턴)

## 핵심 질문

- 한 객체의 상태가 바뀌었을 때, 그 값에 관심 있는 **여러 객체에게 어떻게 자동으로 알릴까**?
- 새로운 관심 객체(디스플레이)를 추가·제거할 때 **원본 객체의 코드를 건드리지 않으려면** 어떻게 설계해야 할까?
- "느슨한 결합(loose coupling)"이란 무엇이고, 왜 시스템을 변화에 강하게 만드는가?
- 데이터를 주제가 **보낼지(push)** 옵저버가 **가져올지(pull)**, 무엇이 더 나은가?

---

## 1. Weather-O-Rama 기상 스테이션 프로젝트

`Weather-O-Rama`사는 `WeatherData` 객체를 기반으로 한 기상 스테이션을 의뢰했다. `WeatherData`는 현재 기상 조건(온도·습도·기압)을 추적하며, 우리는 이 데이터를 실시간으로 갱신하는 **디스플레이 3개**(현재 조건, 기상 통계, 기상 예보)를 만들어야 한다. 게다가 **다른 개발자가 새 디스플레이를 자유롭게 추가**할 수 있도록 확장 가능해야 한다.

`WeatherData` 클래스에는 게터 3개(`getTemperature()`, `getHumidity()`, `getPressure()`)가 있고, 새 측정값이 들어올 때마다 `measurementsChanged()`가 호출된다. 우리 코드는 이 메서드 안에 들어간다.

---

## 2. 첫 시도 (나쁜 예) — 구상 디스플레이에 직접 의존

가장 먼저 떠오르는 구현은 이렇다.

```typescript
// ❌ 나쁜 예
measurementsChanged(): void {
  const temp = this.getTemperature();
  const humidity = this.getHumidity();
  const pressure = this.getPressure();

  // 구체적인 디스플레이 객체들을 직접 호출한다
  this.currentConditionsDisplay.update(temp, humidity, pressure);
  this.statisticsDisplay.update(temp, humidity, pressure);
  this.forecastDisplay.update(temp, humidity, pressure);
}
```

<details>
<summary>Java 원본</summary>

```java
public void measurementsChanged() {
    float temp = getTemperature();
    float humidity = getHumidity();
    float pressure = getPressure();

    currentConditionsDisplay.update(temp, humidity, pressure);
    statisticsDisplay.update(temp, humidity, pressure);
    forecastDisplay.update(temp, humidity, pressure);
}
```
</details>

무엇이 문제인가?

> **핵심 통찰**: 이 코드는 **구상 클래스**(`currentConditionsDisplay` 등)에 직접 의존한다. 따라서 (1) 디스플레이를 추가·제거하려면 이 코드를 **매번 고쳐야** 하고, (2) **실행 중에는** 디스플레이를 더하거나 뺄 수 없으며, (3) 바뀌는 부분(디스플레이 집합)을 캡슐화하지 못했다. (1장의 원칙 위반이다.)

그나마 잘한 점은 모든 디스플레이가 `update(temp, humidity, pressure)`라는 **공통 인터페이스**를 쓴다는 것이다. 여기서 옵저버 패턴이 등장한다.

---

## 3. 옵저버 패턴 = 신문사와 구독자

신문 구독을 떠올리면 옵저버 패턴을 쉽게 이해할 수 있다.

- 신문사가 신문을 발행한다. → **주제(Subject)**
- 독자가 구독 신청을 하면, 새 신문이 나올 때마다 배달받는다. → **옵저버(Observer)**
- 구독을 해지하면 더 이상 받지 않는다.
- 언제든 새 독자가 구독하거나 기존 독자가 해지할 수 있다.

즉 **신문사(주제)가 상태(신문)를 관리**하고, **구독자(옵저버)는 등록/해지**하며, 주제의 상태가 바뀌면(새 신문) 등록된 옵저버 전원에게 자동 전달된다.

> 오늘의 5분 드라마: 헤드헌터(주제)가 구직자 명단을 관리하고, 자바 개발자(옵저버)들이 명단에 등록한다. 일자리가 나오면 명단의 모두에게 연락이 간다. 어떤 개발자가 스스로 직장을 구하면 명단에서 빠진다(해지). 흥미롭게도, 스스로 주제가 되어 자기만의 옵저버를 거느리는 개발자도 생긴다 — 한 객체가 **주제이자 옵저버**일 수 있다.

---

## 4. 옵저버 패턴의 정의

> **패턴 정의 — 옵저버 패턴 (Observer Pattern)**<br>객체들 사이에 일대다(one-to-many) 의존성을 정의한다. 어떤 객체의 상태가 바뀌면, 그 객체에 의존하는 모든 객체에게 연락이 가고 자동으로 내용이 갱신된다.

옵저버 패턴은 보통 **Subject 인터페이스**와 **Observer 인터페이스**를 갖춘 클래스 구조로 구현한다.

```
        «interface»                         «interface»
         Subject         observers          Observer
    ┌──────────────────┐  0..*   ┌────────>┌──────────────┐
    │ registerObserver()│◇───────┘         │ update()     │
    │ removeObserver()  │                   └──────────────┘
    │ notifyObservers() │                          △
    └──────────────────┘                    ┌──────┴────────┐
            △                          ConcreteObserverA  ...B
    ┌───────────────┐                       update()
    │ ConcreteSubject│                       // 기타 옵저버용 메서드
    │ getState()     │
    │ setState()     │
    └───────────────┘
```

---

## 5. 느슨한 결합 (디자인 원칙 4)

> 스승: 단단하게 짠 바구니와 유연하게 짠 바구니 중 어느 것이 덜 부서질까?<br>제자: 유연한 바구니입니다.<br>스승: 그렇다면 객체들이 서로 덜 단단하게 결합되어 있다면, 시스템도 덜 부서지지 않겠는가? 느슨하게 결합된 객체는 서로 **의존은 하되, 상대의 세세한 내부는 알 필요가 없다.**

> **디자인 원칙 4**<br>상호작용하는 객체 사이에서는 가능하면 느슨한 결합을 사용해야 한다.

옵저버 패턴이 만들어내는 느슨한 결합의 위력은 다음과 같다.

- 주제는 옵저버가 **`Observer` 인터페이스를 구현한다**는 사실만 안다. 구상 클래스가 무엇인지, 무슨 일을 하는지는 몰라도 된다.
- 옵저버는 **언제든 새로 추가**할 수 있다(주제는 인터페이스 구현 객체 목록에만 의존).
- **새 형식의 옵저버**를 추가해도 주제 코드는 바뀌지 않는다.
- 주제와 옵저버는 서로 **독립적으로 재사용**할 수 있다.
- 한쪽이 바뀌어도 인터페이스 계약만 지키면 다른 쪽에 영향을 주지 않는다.

> **핵심 통찰**: 느슨하게 결합하는 디자인은 객체 사이의 상호의존성을 최소화하므로, 변경 사항이 생겨도 무난히 처리하는 유연한 시스템을 만든다.

---

## 6. 기상 스테이션 설계

3개의 인터페이스로 설계한다.

- `Subject`: 옵저버 등록/해지/알림
- `Observer`: 상태 변경 시 호출되는 `update()`
- `DisplayElement`: 화면 표시용 `display()` (디스플레이 공통)

```typescript
/** 주제(관찰 대상) — 옵저버를 등록·해지하고 알림을 보낸다. */
interface Subject {
  /** 옵저버를 등록한다. */
  registerObserver(o: Observer): void;
  /** 옵저버를 해지한다. */
  removeObserver(o: Observer): void;
  /** 등록된 모든 옵저버에게 상태 변경을 알린다. */
  notifyObservers(): void;
}

/** 옵저버 — 주제의 상태가 바뀌면 통보받는다. */
interface Observer {
  /** 주제의 상태가 바뀌었을 때 호출된다. */
  update(temp: number, humidity: number, pressure: number): void;
}

/** 화면에 표시되는 디스플레이 요소. */
interface DisplayElement {
  /** 디스플레이를 화면에 표시한다. */
  display(): void;
}
```

<details>
<summary>Java 원본</summary>

```java
public interface Subject {
    void registerObserver(Observer o);
    void removeObserver(Observer o);
    void notifyObservers();
}

public interface Observer {
    void update(float temp, float humidity, float pressure);
}

public interface DisplayElement {
    void display();
}
```
</details>

---

## 7. 구현

### 주제: WeatherData

```typescript
class WeatherData implements Subject {
  private observers: Observer[] = [];
  private temperature = 0;
  private humidity = 0;
  private pressure = 0;

  registerObserver(o: Observer): void {
    this.observers.push(o);
  }

  removeObserver(o: Observer): void {
    const i = this.observers.indexOf(o);
    if (i >= 0) {
      this.observers.splice(i, 1);
    }
  }

  // 핵심: 등록된 모든 옵저버에게 통보한다
  notifyObservers(): void {
    for (const observer of this.observers) {
      observer.update(this.temperature, this.humidity, this.pressure);
    }
  }

  measurementsChanged(): void {
    this.notifyObservers();
  }

  // 테스트용 — 실제 장비 대신 측정값을 수동 주입
  setMeasurements(temperature: number, humidity: number, pressure: number): void {
    this.temperature = temperature;
    this.humidity = humidity;
    this.pressure = pressure;
    this.measurementsChanged();
  }
}
```

<details>
<summary>Java 원본</summary>

```java
public class WeatherData implements Subject {
    private List<Observer> observers;
    private float temperature;
    private float humidity;
    private float pressure;

    public WeatherData() {
        observers = new ArrayList<Observer>();
    }

    public void registerObserver(Observer o) {
        observers.add(o);
    }

    public void removeObserver(Observer o) {
        observers.remove(o);
    }

    public void notifyObservers() {
        for (Observer observer : observers) {
            observer.update(temperature, humidity, pressure);
        }
    }

    public void measurementsChanged() {
        notifyObservers();
    }

    public void setMeasurements(float temperature, float humidity, float pressure) {
        this.temperature = temperature;
        this.humidity = humidity;
        this.pressure = pressure;
        measurementsChanged();
    }
}
```
</details>

### 옵저버: CurrentConditionsDisplay

```typescript
class CurrentConditionsDisplay implements Observer, DisplayElement {
  private temperature = 0;
  private humidity = 0;

  // 생성자에서 주제에 자신을 옵저버로 등록한다
  constructor(private weatherData: Subject) {
    this.weatherData.registerObserver(this);
  }

  update(temperature: number, humidity: number, _pressure: number): void {
    this.temperature = temperature;
    this.humidity = humidity;
    this.display();
  }

  display(): void {
    console.log(`현재 상태: 온도 ${this.temperature}F, 습도 ${this.humidity}%`);
  }
}
```

<details>
<summary>Java 원본</summary>

```java
public class CurrentConditionsDisplay implements Observer, DisplayElement {
    private float temperature;
    private float humidity;
    private WeatherData weatherData;

    public CurrentConditionsDisplay(WeatherData weatherData) {
        this.weatherData = weatherData;
        weatherData.registerObserver(this); // 자신을 옵저버로 등록
    }

    public void update(float temperature, float humidity, float pressure) {
        this.temperature = temperature;
        this.humidity = humidity;
        display();
    }

    public void display() {
        System.out.println("현재 상태: 온도 " + temperature + "F, 습도 " + humidity + "%");
    }
}
```
</details>

> **무엇이든 물어보세요 (Q&A)**
>
> **Q. 주제 레퍼런스(`weatherData`)를 왜 필드에 저장하죠? 생성자에서만 쓰는데요.**
> A. 나중에 옵저버 목록에서 **탈퇴(`removeObserver`)** 할 때 다시 필요하기 때문이다. 미리 저장해 두면 유용하다.

---

## 8. 테스트

```typescript
const weatherData = new WeatherData();

new CurrentConditionsDisplay(weatherData);
// new StatisticsDisplay(weatherData);
// new ForecastDisplay(weatherData);

weatherData.setMeasurements(80, 65, 30.4); // 세 디스플레이 자동 갱신
weatherData.setMeasurements(82, 70, 29.2);
weatherData.setMeasurements(78, 90, 29.2);
```

`setMeasurements()` 한 번 호출로 등록된 모든 디스플레이가 자동으로 갱신된다. 새 디스플레이는 `new XxxDisplay(weatherData)` 한 줄이면 추가되고, `WeatherData` 코드는 전혀 바뀌지 않는다.

---

## 9. 푸시(push) vs 풀(pull)

지금 설계는 주제가 옵저버에게 데이터를 **밀어 넣는(push)** 방식이다. `update(temp, humidity, pressure)`로 모든 값을 강제로 전달한다.

> 방구석 토크 — 주제와 옵저버의 논쟁<br><br>**옵저버**: 왜 내가 필요할 때가 아니라 당신이 필요할 때 상태를 뿌리는 거죠? 필요한 것만 가져가게 해 주세요.<br>**주제**: 하지만 매번 여러 번 게터를 호출해야 할 텐데요?<br>**옵저버**: 그래도 당신이 새 상태(예: 풍속)를 추가하면, 지금 방식은 **모든 옵저버의 `update()` 시그니처를 다 고쳐야** 하잖아요. 내가 게터로 당겨오면 게터 하나만 추가하면 되고요.

이 논쟁의 결론이 **풀(pull) 방식**이다. 주제는 "바뀌었다"고만 알리고, 옵저버가 필요한 데이터를 게터로 당겨온다.

```typescript
// 풀 방식: update()에 인자가 없다
interface Observer {
  update(): void;
}

// WeatherData
notifyObservers(): void {
  for (const observer of this.observers) {
    observer.update(); // 인자 없이 "바뀌었다"만 알림
  }
}
// + getTemperature() / getHumidity() / getPressure() 게터 공개

// CurrentConditionsDisplay
update(): void {
  this.temperature = this.weatherData.getTemperature(); // 필요한 것만 당겨옴
  this.humidity = this.weatherData.getHumidity();
  this.display();
}
```

> **핵심 통찰**: 푸시/풀은 구현 선택의 문제지만, 일반적으로 **풀 방식이 더 낫다고 본다**. 주제에 상태가 추가되어도 옵저버들의 `update()` 시그니처를 일괄 수정할 필요가 없어, 확장에 유리하기 때문이다.

---

## 10. 실전 속 옵저버 패턴

옵저버 패턴은 수많은 라이브러리·프레임워크의 핵심이다.

- **자바 스윙(Swing)**: `JButton`에 `ActionListener`(=옵저버, 리스너)를 등록한다. 버튼 클릭 시 등록된 리스너들의 `actionPerformed()`가 호출된다.
- **자바스크립트 이벤트**, 코코아/스위프트의 키-값 옵저빙, **RxJava**, 자바빈의 `PropertyChangeListener` 등.

```typescript
// 개념적으로 동일 — DOM 이벤트도 옵저버 패턴
button.addEventListener("click", () => {
  console.log("그냥 저질러 버렷!!!");
});
button.addEventListener("click", () => {
  console.log("하지 마! 아마 후회할 걸?");
});
```

<details>
<summary>Java 스윙 원본 (내부 클래스 → 람다)</summary>

```java
// 내부 클래스 방식
button.addActionListener(new AngelListener());
button.addActionListener(new DevilListener());

class AngelListener implements ActionListener {
    public void actionPerformed(ActionEvent event) {
        System.out.println("하지 마! 아마 후회할 걸?");
    }
}

// 람다 방식 — ActionListener 구현 클래스가 사라진다
button.addActionListener(event -> System.out.println("하지 마! 아마 후회할 걸?"));
button.addActionListener(event -> System.out.println("그냥 저질러 버렷!!!"));
```
</details>

> **무엇이든 물어보세요 (Q&A)**
>
> **Q. 자바에 내장된 `Observable` 클래스와 `Observer` 인터페이스가 있지 않았나요?**
> A. 있었지만 **자바 9부터 폐기(deprecated)** 되었다. `Observable`이 클래스라서 상속을 강제하고(다중 상속 불가), 내부 상태가 캡슐화되어 있어 유연성이 떨어졌기 때문이다. 오늘날은 직접 구현하거나 `PropertyChangeListener`, `Flow` API(출판-구독) 등을 쓴다.
>
> **Q. 주제가 옵저버에게 알리는 순서를 정해야 하나요?**
> A. JDK는 **알림 순서에 의존하지 말라**고 권고한다. 특정 순서를 가정하는 코드는 깨지기 쉽다.

---

## 연습 문제 (해답 예시)

**1. 첫 구현(§2)의 문제점 고르기**
- ✅ A. 인터페이스가 아닌 구체적 구현에 맞춰 코딩하고 있다.
- ✅ B. 새 디스플레이가 추가될 때마다 코드를 변경해야 한다.
- ✅ C. 실행 중에 디스플레이를 추가·제거할 수 없다.
- ✅ E. 바뀌는 부분(디스플레이 집합)을 캡슐화하지 않았다.
- (D는 틀림 — 디스플레이들은 공통 `update()`를 쓴다. F도 핵심 문제가 아니다.)

**2. 체감 온도 디스플레이 추가하기** — `HeatIndexDisplay`가 `Observer`, `DisplayElement`를 구현하고 생성자에서 `weatherData`에 등록하면 된다. `WeatherData`는 전혀 건드리지 않는다(옵저버 패턴의 확장성).

**3. 디자인 원칙이 옵저버 패턴에서 쓰인 방식**
- *바뀌는 부분 캡슐화*: 변하는 것은 주제의 상태와 옵저버의 개수·형식. 주제를 바꾸지 않고 옵저버를 교체할 수 있다.
- *인터페이스에 맞춰 프로그래밍*: 주제·옵저버 모두 인터페이스로 소통 → 느슨한 결합.
- *상속보다 구성*: 주제는 옵저버들을 **구성(리스트로 보유)** 하며, 실행 중에 관계가 구성된다.

---

## 디자인 원칙 정리 (누적)

1. 바뀌는 부분을 찾아내 캡슐화하고, 바뀌지 않는 부분과 분리한다.
2. 구현보다는 인터페이스(상위 형식)에 맞춰 프로그래밍한다.
3. 상속보다는 구성을 활용한다.
4. **상호작용하는 객체 사이에서는 가능하면 느슨한 결합을 사용한다.** ← 이번 장

---

## 요약

- **옵저버 패턴**은 객체들 사이에 **일대다 의존성**을 정의한다. 주제의 상태가 바뀌면 등록된 모든 옵저버가 자동으로 통보받는다.
- 주제는 옵저버가 **`Observer` 인터페이스를 구현한다는 것 외에는 아무것도 모른다** → 느슨한 결합.
- 그 결과 옵저버를 **실행 중에 자유롭게 추가·제거**할 수 있고, 새 옵저버 형식을 추가해도 주제 코드는 바뀌지 않는다.
- 데이터 전달은 **푸시**(주제가 보냄)와 **풀**(옵저버가 가져옴) 두 방식이 있으며, 확장성 면에서 대체로 **풀이 낫다**.
- 스윙·RxJava·JS 이벤트 등 실전 프레임워크 곳곳에 옵저버 패턴이 쓰인다. 자바 내장 `Observable`은 자바 9부터 폐기됐다.

---

## 다른 챕터와의 관계

- **1장 전략 패턴**: 이 장도 "인터페이스에 맞춰 프로그래밍 + 구성"이라는 원칙 위에 서 있다. 두 패턴 모두 느슨한 결합을 지향한다.
- **12장 복합 패턴 / MVC**: 옵저버 패턴은 MVC의 핵심 축(모델→뷰 통지)이다. 이 장에서 못다 한 옵저버 이야기가 12장에서 완성된다.
- **11장 프록시 패턴**: 원격 옵저버(분산 환경의 상태 통지)로 확장될 수 있다.

---

## 보너스: 원서 복습 요소

### 🎬 5분 드라마 — 헤드헌터와 개발자

헤드헌터(**주제**)가 자바 개발자(**옵저버**) 명단을 관리한다. 새 일자리가 나오면 명단 전원에게 연락이 간다. 수(Sue)는 스스로 직장을 구해 명단에서 빠지고(**해지**), 나중엔 자기만의 옵저버를 거느린 **주제이자 옵저버**가 된다. → 옵저버 패턴의 등록·통지·해지, 그리고 "주제↔옵저버 역할 겸용"을 극적으로 보여준다.

### 🧠 뇌 단련 (Brain Power)

측정값을 `update(temp, humidity, pressure)`로 직접 전달하는 게 정말 좋은가? → 힌트: 나중에 풍속 같은 값이 추가되면 어떻게 될까? 그 변경이 캡슐화되어 있는가, 아니면 여러 곳을 고쳐야 하는가? (→ §9 푸시/풀 논의로 이어진다.)

### 🧲 코드 자석 — ForecastDisplay 조립

냉장고 문에 흩어진 조각들로 `ForecastDisplay`를 완성하는 문제. 정답 구조는 다음과 같다.

```typescript
class ForecastDisplay implements Observer, DisplayElement {
  private currentPressure = 29.92;
  private lastPressure = 0;

  constructor(private weatherData: WeatherData) {
    weatherData.registerObserver(this);
  }

  update(): void {
    this.lastPressure = this.currentPressure;
    this.currentPressure = this.weatherData.getPressure(); // 풀 방식
    this.display();
  }

  display(): void {
    // 기압 변화(lastPressure → currentPressure)로 예보 출력
  }
}
```

### 📝 낱말 퀴즈 (정답 단어 모음)

1·2장 용어들(정답은 영어): OBSERVER(S)(옵저버), SUBJECT(주제), PUBLISHER(신문사), INTERFACE(인터페이스), IMPLEMENTS(구현하다), LOOSE(느슨한), DEPENDENT(의존적), MANY(여러 개), UPDATE(업데이트), NOTIFIED(알림), PUSH(푸시), ORDER(순서), REMOVEOBSERVER(옵저버 해지), PRESSURE(기압), SWING(스윙), HURRICANE(허리케인 — CEO 이름이자 열대성 저기압), DEVILLISTENER(악마의 대답), HEAT(체감 온도), LISTENING(리스너 역할), JOB(직장), MOUSE(마우스).
