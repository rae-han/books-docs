# Chapter 2: Object-Oriented Programming (객체지향 프로그래밍)

## 핵심 질문

영화 예매 시스템이라는 구체적인 예제를 통해 객체지향 프로그래밍의 핵심 메커니즘인 상속, 다형성, 추상화는 어떻게 유연하고 확장 가능한 설계를 가능하게 하는가? 그리고 코드 재사용을 위해 상속보다 합성을 선호해야 하는 이유는 무엇인가?

---

## 1. 영화 예매 시스템

### 1.1 요구사항 살펴보기

이 장에서 다루는 예제는 온라인 **영화 예매 시스템**이다. 먼저 두 가지 용어를 구분해야 한다:

| 용어 | 의미 | 예시 |
|---|---|---|
| **영화**(*Movie*) | 영화에 대한 기본 정보 (제목, 상영시간, 가격) | "아바타", 120분, 10,000원 |
| **상영**(*Screening*) | 실제로 관객이 영화를 관람하는 사건 (상영일자, 시간, 순번) | 2019.12.26 목요일 7회 18:00 |

하나의 영화는 하루 중 다양한 시간대에 걸쳐 한 번 이상 상영될 수 있다. 사용자가 실제로 예매하는 대상은 영화가 아니라 **상영**이다. 특정 시간에 상영되는 영화를 관람할 수 있는 권리를 구매하기 위해 돈을 지불하는 것이다.

**할인 규칙**은 두 가지로 나뉜다:

**할인 조건**(*Discount Condition - 가격의 할인 여부를 결정하는 규칙*)은 두 종류가 있다:

- **순서 조건**(*Sequence Condition*): 상영 순번을 이용해 할인 여부를 결정한다. 예를 들어, 순번이 1이면 매일 첫 번째로 상영되는 영화를 예매한 사용자에게 할인 혜택을 제공한다.
- **기간 조건**(*Period Condition*): 영화 상영 시작 시간을 이용해 할인 여부를 결정한다. 요일, 시작 시간, 종료 시간의 세 부분으로 구성되며, 영화 시작 시간이 해당 기간 안에 포함될 경우 요금을 할인한다.

**할인 정책**(*Discount Policy - 할인 요금을 결정하는 규칙*)은 두 종류가 있다:

- **금액 할인 정책**(*Amount Discount Policy*): 예매 요금에서 일정 금액을 할인한다.
- **비율 할인 정책**(*Percent Discount Policy*): 정가에서 일정 비율의 요금을 할인한다.

### 1.2 할인 규칙 적용 예시

| 영화 | 할인 정책 | 할인 조건 |
|---|---|---|
| **아바타** (10,000원) | 금액 할인 (800원) | 순번 조건: 1회, 10회 / 기간 조건: 월요일 10:00~12:00, 목요일 18:00~21:00 |
| **타이타닉** (11,000원) | 비율 할인 (10%) | 기간 조건: 화요일 14:00~17:00, 목요일 10:00~14:00 / 순번 조건: 2회 |
| **스타워즈: 깨어난 포스** (10,000원) | 없음 | 없음 |

핵심 규칙:

- 영화별로 **하나의 할인 정책만** 할당할 수 있다 (할인 정책을 지정하지 않는 것도 가능)
- 할인 조건은 **여러 개를 함께** 지정할 수 있으며, 순서 조건과 기간 조건을 섞는 것도 가능
- 할인을 적용하려면 할인 조건과 할인 정책을 **조합**해서 사용한다: 먼저 예매 정보가 할인 조건 중 하나라도 만족하는지 검사하고, 만족하면 할인 정책을 이용해 할인 요금을 계산한다
- 할인 정책은 1인 기준이므로, 예약 인원이 2명이면 할인 금액도 2배

예매가 완료되면 시스템은 제목, 상영 정보, 인원, 정가, 결제 금액을 포함하는 예매 정보를 생성한다.

---

## 2. 객체지향 프로그래밍을 향해

### 2.1 협력, 객체, 클래스

클래스 기반의 객체지향 언어에 익숙한 사람은 프로그램을 작성할 때 가장 먼저 어떤 클래스가 필요한지 고민한다. 대부분의 사람들은 클래스를 결정한 후에 클래스에 어떤 속성과 메서드가 필요한지 고민한다.

안타깝게도 이것은 객체지향의 본질과는 거리가 멀다. 진정한 객체지향 패러다임으로의 전환은 **클래스가 아닌 객체에 초점을 맞출 때**에만 얻을 수 있다. 이를 위해서는 두 가지에 집중해야 한다:

1. **어떤 객체들이 필요한지 먼저 고민하라**: 클래스는 공통적인 상태와 행동을 공유하는 객체들을 추상화한 것이다. 따라서 클래스의 윤곽을 잡기 위해서는 어떤 객체들이 어떤 상태와 행동을 가지는지를 먼저 결정해야 한다.
2. **객체를 협력하는 공동체의 일원으로 보라**: 객체는 홀로 존재하지 않는다. 다른 객체에게 도움을 주거나 의존하면서 살아가는 협력적인 존재다. 객체를 협력하는 공동체의 일원으로 바라보는 것은 설계를 유연하고 확장 가능하게 만든다.

> **핵심 통찰**: 훌륭한 협력이 훌륭한 객체를 낳고, 훌륭한 객체가 훌륭한 클래스를 낳는다. 객체들의 모양과 윤곽이 잡히면 공통된 특성과 상태를 가진 객체들을 타입으로 분류하고, 이 타입을 기반으로 클래스를 구현하라.

### 2.2 도메인의 구조를 따르는 프로그램 구조

도메인(*Domain - 문제를 해결하기 위해 사용자가 프로그램을 사용하는 분야*)이라는 용어를 살펴보자. 영화 예매 시스템의 목적은 영화를 좀 더 쉽고 빠르게 예매하려는 사용자의 문제를 해결하는 것이다.

객체지향 패러다임이 강력한 이유는 요구사항을 분석하는 초기 단계부터 프로그램을 구현하는 마지막 단계까지 **객체라는 동일한 추상화 기법**을 사용할 수 있기 때문이다. 도메인을 구성하는 개념들이 프로그램의 객체와 클래스로 매끄럽게 연결될 수 있다.

```
[도메인 구조]

┌───────────┐  1    *  ┌───────────┐
│   Movie   │─────────▶│ Screening │
│  (영화)   │          │  (상영)   │
└───────────┘          └───────────┘
      │ 0..1                 │ 1
      ▼                     │
┌────────────────┐          ▼  *
│ DiscountPolicy │   ┌─────────────┐
│ (할인 정책)    │   │ Reservation │
└────────────────┘   │   (예매)    │
      │ 1..*         └─────────────┘
      ▼
┌───────────────────┐
│ DiscountCondition │
│   (할인 조건)     │
└───────────────────┘
       ╱    ╲
      ▼      ▼
  Sequence  Period
  Condition Condition
```

클래스의 이름은 대응되는 도메인 개념의 이름과 동일하거나 유사하게 짓고, 클래스 사이의 관계도 도메인 개념 사이에 맺어진 관계와 유사하게 만들어서 프로그램의 구조를 이해하고 예상하기 쉽게 만들어야 한다.

---

## 3. 클래스 구현하기

### 3.1 Screening 클래스

`Screening` 클래스는 사용자들이 예매하는 대상인 '상영'을 구현한다. 상영할 영화(`movie`), 순번(`sequence`), 상영 시작 시간(`whenScreened`)을 인스턴스 변수로 포함한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Screening {
    private Movie movie;
    private int sequence;
    private LocalDateTime whenScreened;

    public Screening(Movie movie, int sequence, LocalDateTime whenScreened) {
        this.movie = movie;
        this.sequence = sequence;
        this.whenScreened = whenScreened;
    }

    public LocalDateTime getStartTime() {
        return whenScreened;
    }

    public boolean isSequence(int sequence) {
        return this.sequence == sequence;
    }

    public Money getMovieFee() {
        return movie.getFee();
    }
}
```

</details>

```typescript
// TypeScript
class Screening {
    private movie: Movie;
    private sequence: number;
    private whenScreened: Date;

    constructor(movie: Movie, sequence: number, whenScreened: Date) {
        this.movie = movie;
        this.sequence = sequence;
        this.whenScreened = whenScreened;
    }

    getStartTime(): Date {
        return this.whenScreened;
    }

    isSequence(sequence: number): boolean {
        return this.sequence === sequence;
    }

    getMovieFee(): Money {
        return this.movie.getFee();
    }
}
```

여기서 주목할 점은 인스턴스 변수의 가시성은 `private`이고 메서드의 가시성은 `public`이라는 것이다. 클래스를 구현할 때 가장 중요한 것은 **클래스의 경계를 구분 짓는 것**이다. 클래스는 내부와 외부로 구분되며, 훌륭한 클래스를 설계하기 위한 핵심은 어떤 부분을 외부에 공개하고 어떤 부분을 감출지를 결정하는 것이다.

### 3.2 자율적인 객체

두 가지 중요한 사실을 알아야 한다:

1. **객체는 상태(state)와 행동(behavior)을 함께 가지는 복합적인 존재다**: 객체지향 이전의 패러다임에서는 데이터와 기능이라는 독립적인 존재를 서로 엮어 프로그램을 구성했다. 객체지향은 객체라는 단위 안에 데이터와 기능을 한 덩어리로 묶음으로써 문제 영역의 아이디어를 적절하게 표현할 수 있게 했다. 이처럼 데이터와 기능을 객체 내부로 함께 묶는 것을 **캡슐화**라고 부른다.

2. **객체는 스스로 판단하고 행동하는 자율적인 존재다**: 대부분의 객체지향 프로그래밍 언어들은 캡슐화에서 한 걸음 더 나아가 외부에서의 접근을 통제할 수 있는 **접근 제어**(*Access Control*) 메커니즘도 함께 제공한다. `public`, `protected`, `private` 같은 **접근 수정자**(*Access Modifier*)가 그것이다.

객체 내부에 대한 접근을 통제하는 이유는 **객체를 자율적인 존재로 만들기 위해서**다. 외부에서는 객체가 어떤 상태에 놓여 있는지, 어떤 생각을 하고 있는지 알아서는 안 되며, 결정에 직접적으로 개입하려고 해서도 안 된다.

캡슐화와 접근 제어는 객체를 두 부분으로 나눈다:

| 구분 | 접근 가능 범위 | 포함 요소 |
|---|---|---|
| **퍼블릭 인터페이스**(*Public Interface*) | 외부에서 접근 가능 | `public`으로 지정된 메서드 |
| **구현**(*Implementation*) | 내부에서만 접근 가능 | `private` 메서드, `protected` 메서드, 속성 |

> **핵심 통찰**: 인터페이스와 구현의 분리(*Separation of Interface and Implementation*) 원칙은 훌륭한 객체지향 프로그램을 만들기 위해 따라야 하는 핵심 원칙이다. 일반적으로 객체의 상태는 숨기고 행동만 외부에 공개해야 한다.

### 3.3 프로그래머의 자유

프로그래머의 역할을 **클래스 작성자**(*Class Creator*)와 **클라이언트 프로그래머**(*Client Programmer*)로 구분하는 것이 유용하다[Eckel06]:

| 역할 | 목표 |
|---|---|
| **클래스 작성자** | 새로운 데이터 타입을 프로그램에 추가. 클라이언트 프로그래머에게 필요한 부분만 공개하고 나머지는 숨김 |
| **클라이언트 프로그래머** | 클래스 작성자가 추가한 데이터 타입을 사용하여 애플리케이션을 빠르고 안정적으로 구축 |

클래스 작성자가 내부 구현을 감추는 것을 **구현 은닉**(*Implementation Hiding*)이라고 부른다. 구현 은닉은 양쪽 모두에게 유용하다:

- **클라이언트 프로그래머**: 내부 구현을 무시한 채 인터페이스만 알면 클래스를 사용할 수 있으므로 머릿속에 담아둬야 하는 지식의 양이 줄어든다.
- **클래스 작성자**: 인터페이스를 바꾸지 않는 한 외부에 미치는 영향을 걱정하지 않고도 내부 구현을 마음대로 변경할 수 있다.

> 설계가 필요한 이유는 변경을 관리하기 위해서라는 것을 기억하라. 객체지향 언어는 객체 사이의 의존성을 적절히 관리함으로써 변경에 대한 파급효과를 제어할 수 있는 다양한 방법을 제공한다. 가장 대표적인 것이 바로 접근 제어다. 변경될 가능성이 있는 세부적인 구현 내용을 `private` 영역 안에 감춤으로써 변경으로 인한 혼란을 최소화할 수 있다.

---

## 4. 협력하는 객체들의 공동체

### 4.1 예매 기능 구현

`Screening`의 `reserve` 메서드는 영화를 예매한 후 예매 정보를 담고 있는 `Reservation`의 인스턴스를 생성해서 반환한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Screening {
    public Reservation reserve(Customer customer, int audienceCount) {
        return new Reservation(customer, this, calculateFee(audienceCount), audienceCount);
    }

    private Money calculateFee(int audienceCount) {
        return movie.calculateMovieFee(this).times(audienceCount);
    }
}
```

</details>

```typescript
// TypeScript
class Screening {
    reserve(customer: Customer, audienceCount: number): Reservation {
        return new Reservation(customer, this, this.calculateFee(audienceCount), audienceCount);
    }

    private calculateFee(audienceCount: number): Money {
        return this.movie.calculateMovieFee(this).times(audienceCount);
    }
}
```

`reserve` 메서드는 `calculateFee`라는 `private` 메서드를 호출해서 요금을 계산한 후 그 결과를 `Reservation`의 생성자에 전달한다. `calculateFee` 메서드는 `Movie`의 `calculateMovieFee` 메서드를 호출하여 1인당 예매 요금을 얻고, 여기에 인원 수(`audienceCount`)를 곱해서 전체 예매 요금을 구한다.

### 4.2 Money 클래스

`Money`는 금액과 관련된 다양한 계산을 구현하는 클래스다. 1장에서 금액을 구현하기 위해 `Long` 타입을 사용했던 것을 기억하라. `Long` 타입은 변수의 크기나 연산자의 종류와 관련된 구현 관점의 제약은 표현할 수 있지만, 저장하는 값이 금액과 관련돼 있다는 **의미**를 전달할 수는 없다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Money {
    public static final Money ZERO = Money.wons(0);
    private final BigDecimal amount;

    public static Money wons(long amount) {
        return new Money(BigDecimal.valueOf(amount));
    }

    public static Money wons(double amount) {
        return new Money(BigDecimal.valueOf(amount));
    }

    Money(BigDecimal amount) {
        this.amount = amount;
    }

    public Money plus(Money amount) {
        return new Money(this.amount.add(amount.amount));
    }

    public Money minus(Money amount) {
        return new Money(this.amount.subtract(amount.amount));
    }

    public Money times(double percent) {
        return new Money(this.amount.multiply(BigDecimal.valueOf(percent)));
    }

    public boolean isLessThan(Money other) {
        return amount.compareTo(other.amount) < 0;
    }

    public boolean isGreaterThanOrEqual(Money other) {
        return amount.compareTo(other.amount) >= 0;
    }
}
```

</details>

```typescript
// TypeScript
class Money {
    static readonly ZERO = Money.wons(0);
    private readonly amount: number;

    private constructor(amount: number) {
        this.amount = amount;
    }

    static wons(amount: number): Money {
        return new Money(amount);
    }

    plus(other: Money): Money {
        return new Money(this.amount + other.amount);
    }

    minus(other: Money): Money {
        return new Money(this.amount - other.amount);
    }

    times(multiplier: number): Money {
        return new Money(this.amount * multiplier);
    }

    isLessThan(other: Money): boolean {
        return this.amount < other.amount;
    }

    isGreaterThanOrEqual(other: Money): boolean {
        return this.amount >= other.amount;
    }
}
```

> **핵심 통찰**: 의미를 좀 더 명시적이고 분명하게 표현할 수 있다면 객체를 사용해서 해당 개념을 구현하라. 그 개념이 비록 하나의 인스턴스 변수만 포함하더라도 개념을 명시적으로 표현하는 것은 전체적인 설계의 명확성과 유연성을 높이는 첫걸음이다.

### 4.3 Reservation 클래스

`Reservation` 클래스는 고객(`customer`), 상영 정보(`screening`), 예매 요금(`fee`), 인원 수(`audienceCount`)를 속성으로 포함한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Reservation {
    private Customer customer;
    private Screening screening;
    private Money fee;
    private int audienceCount;

    public Reservation(Customer customer, Screening screening, Money fee, int audienceCount) {
        this.customer = customer;
        this.screening = screening;
        this.fee = fee;
        this.audienceCount = audienceCount;
    }
}
```

</details>

```typescript
// TypeScript
class Reservation {
    constructor(
        private customer: Customer,
        private screening: Screening,
        private fee: Money,
        private audienceCount: number
    ) {}
}
```

### 4.4 협력 다이어그램

영화를 예매하기 위해 `Screening`, `Movie`, `Reservation` 인스턴스들은 서로의 메서드를 호출하며 상호작용한다. 이처럼 시스템의 어떤 기능을 구현하기 위해 객체들 사이에 이뤄지는 상호작용을 **협력**(*Collaboration*)이라고 부른다.

```
                    2: calculateFee(count)
  1: reserve           ┌─────────┐
  (customer, count)    │         ▼
────────▶ :Screening ─────▶ :Movie
              │         3: calculateMovieFee(screening)
              │
              │  4: «create»
              ▼
         :Reservation
```

### 4.5 협력에 관한 짧은 이야기

객체의 내부 상태는 외부에서 접근하지 못하도록 감춰야 한다. 대신 외부에 공개하는 퍼블릭 인터페이스를 통해 내부 상태에 접근할 수 있도록 허용한다. 객체가 다른 객체와 상호작용할 수 있는 유일한 방법은 **메시지를 전송**(*Send a Message*)하는 것뿐이다. 메시지를 수신한 객체는 스스로의 결정에 따라 자율적으로 메시지를 처리할 방법을 결정한다. 이처럼 수신된 메시지를 처리하기 위한 자신만의 방법을 **메서드**(*Method*)라고 부른다.

메시지와 메서드를 구분하는 것은 매우 중요하다. `Screening`이 `Movie`의 `calculateMovieFee` '메서드를 호출한다'고 말했지만, 사실은 `Screening`이 `Movie`에게 `calculateMovieFee` **메시지를 전송한다**라고 말하는 것이 더 적절하다. `Screening`은 `Movie` 안에 `calculateMovieFee` 메서드가 존재하고 있는지조차 알지 못한다. 단지 `Movie`가 `calculateMovieFee` 메시지에 응답할 수 있다고 믿고 메시지를 전송할 뿐이다.

> **핵심 통찰**: 메시지와 메서드의 구분에서부터 **다형성**(*Polymorphism*)의 개념이 출발한다. 메시지를 처리하는 방법을 결정하는 것은 메시지를 수신한 객체 스스로의 문제다. 이것이 객체가 메시지를 처리하는 방법을 자율적으로 결정할 수 있다고 말하는 이유다.

---

## 5. 할인 요금 구하기

### 5.1 할인 요금 계산을 위한 협력 시작하기

`Movie`는 제목(`title`), 상영시간(`runningTime`), 기본 요금(`fee`), 할인 정책(`discountPolicy`)을 속성으로 가진다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Movie {
    private String title;
    private Duration runningTime;
    private Money fee;
    private DiscountPolicy discountPolicy;

    public Movie(String title, Duration runningTime, Money fee, DiscountPolicy discountPolicy) {
        this.title = title;
        this.runningTime = runningTime;
        this.fee = fee;
        this.discountPolicy = discountPolicy;
    }

    public Money getFee() {
        return fee;
    }

    public Money calculateMovieFee(Screening screening) {
        return fee.minus(discountPolicy.calculateDiscountAmount(screening));
    }
}
```

</details>

```typescript
// TypeScript
class Movie {
    private title: string;
    private runningTime: number; // minutes
    private fee: Money;
    private discountPolicy: DiscountPolicy;

    constructor(title: string, runningTime: number, fee: Money, discountPolicy: DiscountPolicy) {
        this.title = title;
        this.runningTime = runningTime;
        this.fee = fee;
        this.discountPolicy = discountPolicy;
    }

    getFee(): Money {
        return this.fee;
    }

    calculateMovieFee(screening: Screening): Money {
        return this.fee.minus(this.discountPolicy.calculateDiscountAmount(screening));
    }
}
```

`calculateMovieFee` 메서드는 `discountPolicy`에 `calculateDiscountAmount` 메시지를 전송해 할인 요금을 반환받는다. `Movie`는 기본 요금인 `fee`에서 반환된 할인 요금을 차감한다.

이 메서드에는 이상한 점이 있다. 어떤 할인 정책을 사용할 것인지 결정하는 코드가 어디에도 존재하지 않는다. 영화 예매 시스템에는 금액 할인 정책과 비율 할인 정책 두 가지 종류가 존재하는데, 코드 어디에도 할인 정책을 판단하는 코드는 없다. 단지 `discountPolicy`에게 메시지를 전송할 뿐이다.

이 코드에는 객체지향에서 중요하다고 여겨지는 두 가지 개념이 숨겨져 있다. 하나는 **상속**(*Inheritance*)이고 다른 하나는 **다형성**이다. 그리고 그 기반에는 **추상화**(*Abstraction*)라는 원리가 숨겨져 있다.

### 5.2 할인 정책과 할인 조건

할인 정책은 금액 할인 정책(`AmountDiscountPolicy`)과 비율 할인 정책(`PercentDiscountPolicy`)으로 구분된다. 두 클래스는 대부분의 코드가 유사하고 할인 요금을 계산하는 방식만 조금 다르다. 중복 코드를 제거하기 위해 공통 코드를 부모 클래스인 `DiscountPolicy`에 둔다.

`DiscountPolicy`는 인스턴스를 직접 생성할 필요가 없으므로 추상 클래스(*Abstract Class*)로 구현한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public abstract class DiscountPolicy {
    private List<DiscountCondition> conditions = new ArrayList<>();

    public DiscountPolicy(DiscountCondition... conditions) {
        this.conditions = Arrays.asList(conditions);
    }

    public Money calculateDiscountAmount(Screening screening) {
        for (DiscountCondition each : conditions) {
            if (each.isSatisfiedBy(screening)) {
                return getDiscountAmount(screening);
            }
        }
        return Money.ZERO;
    }

    abstract protected Money getDiscountAmount(Screening screening);
}
```

</details>

```typescript
// TypeScript
abstract class DiscountPolicy {
    private conditions: DiscountCondition[];

    constructor(...conditions: DiscountCondition[]) {
        this.conditions = conditions;
    }

    calculateDiscountAmount(screening: Screening): Money {
        for (const condition of this.conditions) {
            if (condition.isSatisfiedBy(screening)) {
                return this.getDiscountAmount(screening);
            }
        }
        return Money.ZERO;
    }

    protected abstract getDiscountAmount(screening: Screening): Money;
}
```

`DiscountPolicy`는 `DiscountCondition`의 리스트인 `conditions`를 인스턴스 변수로 가지기 때문에 하나의 할인 정책은 여러 개의 할인 조건을 포함할 수 있다. `calculateDiscountAmount` 메서드는 전체 할인 조건에 대해 차례대로 `isSatisfiedBy` 메서드를 호출한다. 할인 조건을 만족하는 것이 하나라도 존재하면 추상 메서드(*Abstract Method*)인 `getDiscountAmount` 메서드를 호출해 할인 요금을 계산한다. 만족하는 할인 조건이 하나도 없으면 0원을 반환한다.

이처럼 부모 클래스에 기본적인 알고리즘의 흐름을 구현하고 중간에 필요한 처리를 자식 클래스에게 위임하는 디자인 패턴을 **TEMPLATE METHOD 패턴**[GOF94]이라고 부른다.

`DiscountCondition`은 인터페이스를 이용해 선언된다:

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public interface DiscountCondition {
    boolean isSatisfiedBy(Screening screening);
}
```

</details>

```typescript
// TypeScript
interface DiscountCondition {
    isSatisfiedBy(screening: Screening): boolean;
}
```

**순서 조건** (`SequenceCondition`):

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class SequenceCondition implements DiscountCondition {
    private int sequence;

    public SequenceCondition(int sequence) {
        this.sequence = sequence;
    }

    public boolean isSatisfiedBy(Screening screening) {
        return screening.isSequence(sequence);
    }
}
```

</details>

```typescript
// TypeScript
class SequenceCondition implements DiscountCondition {
    constructor(private sequence: number) {}

    isSatisfiedBy(screening: Screening): boolean {
        return screening.isSequence(this.sequence);
    }
}
```

**기간 조건** (`PeriodCondition`):

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class PeriodCondition implements DiscountCondition {
    private DayOfWeek dayOfWeek;
    private LocalTime startTime;
    private LocalTime endTime;

    public PeriodCondition(DayOfWeek dayOfWeek, LocalTime startTime, LocalTime endTime) {
        this.dayOfWeek = dayOfWeek;
        this.startTime = startTime;
        this.endTime = endTime;
    }

    public boolean isSatisfiedBy(Screening screening) {
        return screening.getStartTime().getDayOfWeek().equals(dayOfWeek) &&
            startTime.compareTo(screening.getStartTime().toLocalTime()) <= 0 &&
            endTime.compareTo(screening.getStartTime().toLocalTime()) >= 0;
    }
}
```

</details>

```typescript
// TypeScript
class PeriodCondition implements DiscountCondition {
    constructor(
        private dayOfWeek: number,  // 0=Sun, 1=Mon, ...
        private startTime: string,  // "HH:mm"
        private endTime: string     // "HH:mm"
    ) {}

    isSatisfiedBy(screening: Screening): boolean {
        const startTime = screening.getStartTime();
        const day = startTime.getDay();
        const time = `${String(startTime.getHours()).padStart(2, "0")}:${String(startTime.getMinutes()).padStart(2, "0")}`;

        return day === this.dayOfWeek &&
            this.startTime <= time &&
            this.endTime >= time;
    }
}
```

**금액 할인 정책** (`AmountDiscountPolicy`):

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class AmountDiscountPolicy extends DiscountPolicy {
    private Money discountAmount;

    public AmountDiscountPolicy(Money discountAmount, DiscountCondition... conditions) {
        super(conditions);
        this.discountAmount = discountAmount;
    }

    @Override
    protected Money getDiscountAmount(Screening screening) {
        return discountAmount;
    }
}
```

</details>

```typescript
// TypeScript
class AmountDiscountPolicy extends DiscountPolicy {
    private discountAmount: Money;

    constructor(discountAmount: Money, ...conditions: DiscountCondition[]) {
        super(...conditions);
        this.discountAmount = discountAmount;
    }

    protected getDiscountAmount(screening: Screening): Money {
        return this.discountAmount;
    }
}
```

**비율 할인 정책** (`PercentDiscountPolicy`):

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class PercentDiscountPolicy extends DiscountPolicy {
    private double percent;

    public PercentDiscountPolicy(double percent, DiscountCondition... conditions) {
        super(conditions);
        this.percent = percent;
    }

    @Override
    protected Money getDiscountAmount(Screening screening) {
        return screening.getMovieFee().times(percent);
    }
}
```

</details>

```typescript
// TypeScript
class PercentDiscountPolicy extends DiscountPolicy {
    private percent: number;

    constructor(percent: number, ...conditions: DiscountCondition[]) {
        super(...conditions);
        this.percent = percent;
    }

    protected getDiscountAmount(screening: Screening): Money {
        return screening.getMovieFee().times(this.percent);
    }
}
```

### 5.3 클래스 관계 다이어그램

```
┌──────────┐                    ┌──────────────────┐
│  Movie   │  discountPolicy    │  DiscountPolicy   │
│          │───────────────────▶│  {abstract}       │
│ -title   │                    │                   │
│ -running │                    │ +calculateDiscount│
│ -fee     │                    │  Amount()         │
│ -discount│                    │ #getDiscountAmount│
│  Policy  │                    │  () {abstract}    │
│          │                    └──────────────────┘
│ +getFee()│                       ▲           ▲
│ +calcMF()│                       │           │
└──────────┘                       │           │
                          ┌────────┘           └────────┐
                          │                             │
                 ┌────────────────┐           ┌─────────────────┐
                 │ AmountDiscount │           │ PercentDiscount │
                 │    Policy      │           │     Policy      │
                 │                │           │                 │
                 │ -discountAmount│           │ -percent        │
                 │ #getDiscount() │           │ #getDiscount()  │
                 └────────────────┘           └─────────────────┘

                    conditions ▼
              ┌────────────────────────┐
              │ «interface»            │
              │ DiscountCondition      │
              │ +isSatisfiedBy()       │
              └────────────────────────┘
                     ▲           ▲
                     │           │
            ┌────────┘           └────────┐
   ┌────────────────────┐    ┌─────────────────┐
   │ SequenceCondition  │    │ PeriodCondition  │
   │ -sequence          │    │ -dayOfWeek       │
   │ +isSatisfiedBy()   │    │ -startTime       │
   └────────────────────┘    │ -endTime         │
                             │ +isSatisfiedBy() │
                             └─────────────────┘
```

### 5.4 오버라이딩과 오버로딩

많은 사람들이 **오버라이딩**(*Overriding*)과 **오버로딩**(*Overloading*)의 개념을 혼동한다:

| 개념 | 정의 | 특징 |
|---|---|---|
| **오버라이딩** | 부모 클래스에 정의된 같은 이름, 같은 파라미터 목록을 가진 메서드를 자식 클래스에서 재정의 | 자식 클래스의 메서드가 부모 클래스의 메서드를 **가린다** |
| **오버로딩** | 메서드의 이름은 같지만 파라미터의 목록이 다름 | 두 메서드가 사이좋게 **공존**한다 |

<details>
<summary>원문 Java 코드</summary>

```java
// Java - 오버로딩 예시
public class Money {
    public Money plus(Money amount) {
        return new Money(this.amount.add(amount.amount));
    }

    public Money plus(long amount) {
        return new Money(this.amount.add(BigDecimal.valueOf(amount)));
    }
}
```

</details>

```typescript
// TypeScript - 오버로딩 예시 (함수 시그니처 오버로딩)
class Money {
    plus(amount: Money): Money;
    plus(amount: number): Money;
    plus(amount: Money | number): Money {
        if (amount instanceof Money) {
            return new Money(this.amount + amount.amount);
        }
        return new Money(this.amount + amount);
    }
}
```

### 5.5 할인 정책 구성하기

`Movie`의 생성자는 오직 하나의 `DiscountPolicy` 인스턴스만 받을 수 있도록 선언돼 있고, `DiscountPolicy`의 생성자는 여러 개의 `DiscountCondition` 인스턴스를 허용한다. 이처럼 생성자의 파라미터 목록을 이용해 초기화에 필요한 정보를 전달하도록 강제하면 **올바른 상태를 가진 객체의 생성을 보장**할 수 있다.

다음은 '아바타'에 대한 할인 정책과 할인 조건을 설정한 것이다:

<details>
<summary>원문 Java 코드</summary>

```java
// Java
Movie avatar = new Movie("아바타",
    Duration.ofMinutes(120),
    Money.wons(10000),
    new AmountDiscountPolicy(Money.wons(800),
        new SequenceCondition(1),
        new SequenceCondition(10),
        new PeriodCondition(DayOfWeek.MONDAY, LocalTime.of(10, 0), LocalTime.of(11, 59)),
        new PeriodCondition(DayOfWeek.THURSDAY, LocalTime.of(10, 0), LocalTime.of(20, 59))));

Movie titanic = new Movie("타이타닉",
    Duration.ofMinutes(180),
    Money.wons(11000),
    new PercentDiscountPolicy(0.1,
        new PeriodCondition(DayOfWeek.TUESDAY, LocalTime.of(14, 0), LocalTime.of(16, 59)),
        new SequenceCondition(2),
        new PeriodCondition(DayOfWeek.THURSDAY, LocalTime.of(10, 0), LocalTime.of(13, 59))));
```

</details>

```typescript
// TypeScript
const avatar = new Movie("아바타",
    120,
    Money.wons(10000),
    new AmountDiscountPolicy(Money.wons(800),
        new SequenceCondition(1),
        new SequenceCondition(10),
        new PeriodCondition(1, "10:00", "11:59"),  // 월요일
        new PeriodCondition(4, "10:00", "20:59")   // 목요일
    )
);

const titanic = new Movie("타이타닉",
    180,
    Money.wons(11000),
    new PercentDiscountPolicy(0.1,
        new PeriodCondition(2, "14:00", "16:59"),  // 화요일
        new SequenceCondition(2),
        new PeriodCondition(4, "10:00", "13:59")   // 목요일
    )
);
```

---

## 6. 상속과 다형성

### 6.1 컴파일 시간 의존성과 실행 시간 의존성

`Movie` 클래스는 코드 수준에서 `DiscountPolicy`에만 의존하고 있다. `AmountDiscountPolicy`나 `PercentDiscountPolicy`에 의존하는 곳은 코드 어디에서도 찾을 수 없다. 그러나 실행 시점에 `Movie`의 인스턴스는 `AmountDiscountPolicy`나 `PercentDiscountPolicy`의 인스턴스에 의존하게 된다.

```
[코드 수준 의존성 (컴파일 시간)]

   Movie ──────▶ DiscountPolicy {abstract}
                      ▲           ▲
                      │           │
            AmountDiscount  PercentDiscount
                Policy          Policy


[실행 시간 의존성 - 금액 할인 적용 시]

   :Movie ──────▶ :AmountDiscountPolicy
   (title=아바타)   (discountAmount=800원)


[실행 시간 의존성 - 비율 할인 적용 시]

   :Movie ──────▶ :PercentDiscountPolicy
   (title=아바타)   (percent=10%)
```

여기서 이야기하고 싶은 것은 **코드의 의존성과 실행 시점의 의존성이 서로 다를 수 있다**는 것이다. 유연하고, 쉽게 재사용할 수 있으며, 확장 가능한 객체지향 설계가 가지는 특징은 코드의 의존성과 실행 시점의 의존성이 다르다는 것이다.

한 가지 간과해서는 안 되는 사실은 코드의 의존성과 실행 시점의 의존성이 **다르면 다를수록 코드를 이해하기 어려워진다**는 것이다. 코드를 이해하기 위해서는 코드뿐만 아니라 객체를 생성하고 연결하는 부분을 찾아야 하기 때문이다. 반면 코드의 의존성과 실행 시점의 의존성이 다르면 다를수록 코드는 더 **유연해지고 확장 가능해진다**.

> **핵심 통찰**: 설계가 유연해질수록 코드를 이해하고 디버깅하기는 점점 더 어려워진다. 반면 유연성을 억제하면 코드를 이해하고 디버깅하기는 쉬워지지만 재사용성과 확장 가능성은 낮아진다. 훌륭한 객체지향 설계자로 성장하기 위해서는 항상 유연성과 가독성 사이에서 고민해야 한다.

### 6.2 차이에 의한 프로그래밍

상속은 기존 클래스를 기반으로 새로운 클래스를 쉽고 빠르게 추가할 수 있는 간편한 방법을 제공한다. 상속을 이용하면 부모 클래스의 구현은 공유하면서도 행동이 다른 자식 클래스를 쉽게 추가할 수 있다.

`AmountDiscountPolicy`와 `PercentDiscountPolicy`는 `DiscountPolicy`에서 정의한 추상 메서드인 `getDiscountAmount` 메서드를 오버라이딩해서 `DiscountPolicy`의 행동을 수정한다. 이처럼 부모 클래스와 **다른 부분만을 추가**해서 새로운 클래스를 쉽고 빠르게 만드는 방법을 **차이에 의한 프로그래밍**(*Programming by Difference*)이라고 부른다.

### 6.3 상속과 인터페이스

상속이 가치 있는 이유는 부모 클래스가 제공하는 모든 **인터페이스**를 자식 클래스가 물려받을 수 있기 때문이다. 상속을 주로 코드 재사용의 관점에서 바라보는 것은 부적절하다.

인터페이스는 객체가 이해할 수 있는 메시지의 목록을 정의한다. 상속을 통해 자식 클래스는 부모 클래스가 수신할 수 있는 모든 메시지를 수신할 수 있기 때문에, 외부 객체는 자식 클래스를 부모 클래스와 동일한 타입으로 간주할 수 있다.

```typescript
// TypeScript
class Movie {
    calculateMovieFee(screening: Screening): Money {
        return this.fee.minus(this.discountPolicy.calculateDiscountAmount(screening));
    }
}
```

`Movie`가 `calculateDiscountAmount` 메시지를 전송할 때, 실제로 실행되는 메서드는 `Movie`와 협력하는 객체의 실제 클래스가 무엇인지에 따라 달라진다. `Movie`는 자신이 협력하는 객체가 `calculateDiscountAmount` 메시지를 이해할 수 있다는 사실만 알고 있다.

자식 클래스가 부모 클래스를 대신하는 것을 **업캐스팅**(*Upcasting - 자식 클래스가 부모 클래스의 타입으로 자동 형변환되는 것*)이라고 부른다. 이름은 상속 계층을 그림으로 표현할 때 부모 클래스를 위에, 자식 클래스를 아래에 위치시키는 것이 일반적인 방법이기 때문에 붙여졌다.

### 6.4 다형성

`Movie`는 동일한 메시지를 전송하지만 실제로 어떤 메서드가 실행될 것인지는 메시지를 수신하는 객체의 클래스가 무엇이냐에 따라 달라진다. 이를 **다형성**이라고 부른다.

다형성은 컴파일 시간 의존성과 실행 시간 의존성이 다를 수 있다는 사실을 기반으로 한다. 다형성은 동일한 메시지를 수신했을 때 객체의 타입에 따라 다르게 응답할 수 있는 능력을 의미한다. 따라서 다형적인 협력에 참여하는 객체들은 모두 같은 메시지를 이해할 수 있어야 한다. 다시 말해 인터페이스가 동일해야 한다.

`AmountDiscountPolicy`와 `PercentDiscountPolicy`가 다형적인 협력에 참여할 수 있는 이유는 이들이 `DiscountPolicy`로부터 동일한 인터페이스를 물려받았기 때문이다.

다형성을 구현하는 방법은 매우 다양하지만, 메시지에 응답하기 위해 실행될 메서드를 컴파일 시점이 아닌 **실행 시점에 결정**한다는 공통점이 있다. 다시 말해 메시지와 메서드를 **실행 시점에 바인딩**한다는 것이다. 이를 **지연 바인딩**(*Lazy Binding*) 또는 **동적 바인딩**(*Dynamic Binding*)이라고 부른다. 이에 비해 전통적인 함수 호출처럼 컴파일 시점에 실행될 함수나 프로시저를 결정하는 것을 **초기 바인딩**(*Early Binding*) 또는 **정적 바인딩**(*Static Binding*)이라고 부른다.

---

## 7. 추상화와 유연성

### 7.1 추상화의 힘

`DiscountPolicy`는 `AmountDiscountPolicy`와 `PercentDiscountPolicy`보다 추상적이고, `DiscountCondition`은 `SequenceCondition`과 `PeriodCondition`보다 추상적이다. 두 경우 모두 더 추상적인 타입이 결합도를 낮추고 유연한 설계를 만든다.

추상화를 사용하면 세부적인 내용을 무시한 채 상위 정책을 쉽고 간단하게 표현할 수 있다. 이것은 세부사항에 억눌리지 않고 상위 개념만으로도 도메인의 중요한 개념을 설명할 수 있게 한다.

영화 예매 요금 계산의 전체 흐름을 추상화 수준에서 서술하면 다음과 같다:

> 영화 예매 요금은 최대 하나의 '할인 정책'과 다수의 '할인 조건'을 이용해 계산할 수 있다.

이것은 "영화의 예매 요금은 '금액 할인 정책'과 '두 개의 순서 조건, 한 개의 기간 조건'을 이용해서 계산할 수 있다"라는 문장을 포괄할 수 있다. 추상화를 이용해 상위 정책을 표현하면 기존 구조를 수정하지 않고도 새로운 기능을 쉽게 추가하고 확장할 수 있다.

### 7.2 유연한 설계: NoneDiscountPolicy

영화에 할인 정책이 적용돼 있지 않은 경우는 어떻게 처리할 것인가? 다음과 같이 할인 정책이 없는 경우를 `Movie`에서 예외적으로 처리하는 방법이 있다:

### 나쁜 설계

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Movie {
    public Money calculateMovieFee(Screening screening) {
        if (discountPolicy == null) {
            return fee;
        }
        return fee.minus(discountPolicy.calculateDiscountAmount(screening));
    }
}
```

</details>

```typescript
// TypeScript
class Movie {
    calculateMovieFee(screening: Screening): Money {
        if (this.discountPolicy === null) {
            return this.fee;
        }
        return this.fee.minus(this.discountPolicy.calculateDiscountAmount(screening));
    }
}
```

이 방식의 문제점은 할인 정책이 없는 경우를 예외 케이스로 취급하기 때문에 **지금까지 일관성 있던 협력 방식이 무너지게 된다**는 것이다. 기존 할인 정책의 경우에는 할인할 금액을 계산하는 책임이 `DiscountPolicy`의 자식 클래스에 있었지만, 할인 정책이 없는 경우에는 할인 금액이 0원이라는 사실을 결정하는 책임이 `Movie`로 넘어온다.

### 좋은 설계

일관성을 지키면서 할인 정책이 없는 경우를 처리하는 방법은 **0원이라는 할인 요금을 계산하는 할인 정책**을 추가하는 것이다:

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class NoneDiscountPolicy extends DiscountPolicy {
    @Override
    protected Money getDiscountAmount(Screening screening) {
        return Money.ZERO;
    }
}
```

</details>

```typescript
// TypeScript
class NoneDiscountPolicy extends DiscountPolicy {
    constructor() {
        super();  // 할인 조건 없음
    }

    protected getDiscountAmount(screening: Screening): Money {
        return Money.ZERO;
    }
}
```

이제 할인 정책이 없는 영화를 생성할 때 `NoneDiscountPolicy`의 인스턴스를 연결하면 된다:

```typescript
// TypeScript
const starWars = new Movie("스타워즈: 깨어난 포스",
    150,
    Money.wons(10000),
    new NoneDiscountPolicy()
);
```

중요한 것은 기존의 `Movie`와 `DiscountPolicy`는 **수정하지 않고** `NoneDiscountPolicy`라는 새로운 클래스를 추가하는 것만으로 애플리케이션의 기능을 확장했다는 것이다. 추상화를 중심으로 코드의 구조를 설계하면 유연하고 확장 가능한 설계를 만들 수 있다.

> **핵심 통찰**: 추상화가 유연한 설계를 가능하게 하는 이유는 설계가 구체적인 상황에 결합되는 것을 방지하기 때문이다. `Movie`는 특정한 할인 정책에 묶이지 않는다. `DiscountPolicy`를 상속받고 있다면 어떤 클래스와도 협력이 가능하다. 유연성이 필요한 곳에 추상화를 사용하라.

### 7.3 추상 클래스와 인터페이스 트레이드오프

`NoneDiscountPolicy` 클래스의 코드를 자세히 살펴보면 `getDiscountAmount()` 메서드가 어떤 값을 반환하더라도 상관없다는 사실을 알 수 있다. 부모 클래스인 `DiscountPolicy`에서 할인 조건이 없을 경우에는 `getDiscountAmount()` 메서드를 호출하지 않기 때문이다. 이것은 `DiscountPolicy`와 `NoneDiscountPolicy`를 개념적으로 결합시킨다.

이 문제를 해결하는 방법은 `DiscountPolicy`를 **인터페이스**로 바꾸고 `NoneDiscountPolicy`가 `calculateDiscountAmount()` 오퍼레이션을 직접 오버라이딩하도록 변경하는 것이다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public interface DiscountPolicy {
    Money calculateDiscountAmount(Screening screening);
}

public abstract class DefaultDiscountPolicy implements DiscountPolicy {
    // 기존 DiscountPolicy의 내용...
}

public class NoneDiscountPolicy implements DiscountPolicy {
    @Override
    public Money calculateDiscountAmount(Screening screening) {
        return Money.ZERO;
    }
}
```

</details>

```typescript
// TypeScript
interface DiscountPolicy {
    calculateDiscountAmount(screening: Screening): Money;
}

abstract class DefaultDiscountPolicy implements DiscountPolicy {
    private conditions: DiscountCondition[];

    constructor(...conditions: DiscountCondition[]) {
        this.conditions = conditions;
    }

    calculateDiscountAmount(screening: Screening): Money {
        for (const condition of this.conditions) {
            if (condition.isSatisfiedBy(screening)) {
                return this.getDiscountAmount(screening);
            }
        }
        return Money.ZERO;
    }

    protected abstract getDiscountAmount(screening: Screening): Money;
}

class NoneDiscountPolicy implements DiscountPolicy {
    calculateDiscountAmount(screening: Screening): Money {
        return Money.ZERO;
    }
}
```

변경 후의 구조:

```
┌──────────┐    discountPolicy    ┌──────────────────────┐
│  Movie   │─────────────────────▶│ «interface»           │
│          │                      │ DiscountPolicy        │
└──────────┘                      │ +calculateDiscount()  │
                                  └──────────────────────┘
                                     ▲              ▲
                                     │              │
                        ┌────────────┘              └──────────┐
                        │                                      │
               ┌────────────────────┐              ┌──────────────────┐
               │ DefaultDiscount    │              │ NoneDiscount     │
               │ Policy {abstract}  │              │ Policy           │
               │                    │              │ +calculateDisc() │
               │ +calculateDisc()   │              └──────────────────┘
               │ #getDiscAmount()   │
               └────────────────────┘
                    ▲           ▲
                    │           │
           AmountDiscount  PercentDiscount
              Policy          Policy
```

어떤 설계가 더 좋은가? 이상적으로는 인터페이스를 사용하도록 변경한 설계가 더 좋을 것이다. 현실적으로는 `NoneDiscountPolicy`만을 위해 인터페이스를 추가하는 것이 과하다는 생각이 들 수도 있다. 이 책에서는 설명을 단순화하기 위해 인터페이스를 사용하지 않는 원래의 설계에 기반해서 설명을 이어간다.

> 구현과 관련된 모든 것들이 트레이드오프의 대상이 될 수 있다. 여러분이 작성하는 모든 코드에는 합당한 이유가 있어야 한다. 비록 아주 사소한 결정이더라도 트레이드오프를 통해 얻어진 결론과 그렇지 않은 결론 사이의 차이는 크다. 고민하고 트레이드오프하라.

---

## 8. 코드 재사용

### 8.1 상속 vs 합성

상속은 코드를 재사용하기 위해 널리 사용되는 방법이다. 하지만 코드 재사용을 위해서는 상속보다는 **합성**(*Composition - 다른 객체의 인스턴스를 자신의 인스턴스 변수로 포함해서 재사용하는 방법*)이 더 좋은 방법이라는 이야기를 많이 들었을 것이다.

`Movie`가 `DiscountPolicy`의 코드를 재사용하는 방법이 바로 합성이다. 이 설계를 상속으로 변경할 수도 있다. `Movie`를 직접 상속받아 `AmountDiscountMovie`와 `PercentDiscountMovie`라는 두 개의 클래스를 추가하면 합성을 사용한 기존 방법과 기능적 관점에서 완벽히 동일하다.

```
[상속으로 구현한 할인 정책]

              Movie {abstract}
          +calculateMovieFee()
          #getDiscountAmount()
                 ▲          ▲
                 │          │
    AmountDiscount    PercentDiscount
        Movie             Movie
    #getDiscount()    #getDiscount()
```

그럼에도 많은 사람들이 상속 대신 합성을 선호하는 이유는 무엇일까?

### 8.2 상속의 단점

상속은 두 가지 관점에서 설계에 안 좋은 영향을 미친다.

**1. 캡슐화를 위반한다**

상속을 이용하기 위해서는 **부모 클래스의 내부 구조를 잘 알고 있어야 한다**. 부모 클래스의 구현이 자식 클래스에게 노출되기 때문에 캡슐화가 약화된다. 캡슐화의 약화는 자식 클래스가 부모 클래스에 강하게 결합되도록 만들기 때문에 부모 클래스를 변경할 때 자식 클래스도 함께 변경될 확률을 높인다.

**2. 설계를 유연하지 못하게 만든다**

상속은 부모 클래스와 자식 클래스 사이의 관계를 **컴파일 시점에 결정**한다. 따라서 실행 시점에 객체의 종류를 변경하는 것이 불가능하다.

예를 들어, 금액 할인 정책인 영화를 비율 할인 정책으로 변경한다고 가정하자. 상속 기반 설계에서는 `AmountDiscountMovie`의 인스턴스를 `PercentDiscountMovie`의 인스턴스로 변경해야 한다. 대부분의 언어는 이미 생성된 객체의 클래스를 변경하는 기능을 지원하지 않기 때문에 새 인스턴스를 생성한 후 기존 인스턴스의 상태를 복사하는 것이 최선이다.

반면 **합성 기반 설계**에서는 인스턴스 변수를 교체하는 간단한 작업으로 바뀐다:

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Movie {
    private DiscountPolicy discountPolicy;

    public void changeDiscountPolicy(DiscountPolicy discountPolicy) {
        this.discountPolicy = discountPolicy;
    }
}

Movie avatar = new Movie("아바타",
    Duration.ofMinutes(120),
    Money.wons(10000),
    new AmountDiscountPolicy(Money.wons(800), ...));

avatar.changeDiscountPolicy(new PercentDiscountPolicy(0.1, ...));
```

</details>

```typescript
// TypeScript
class Movie {
    private discountPolicy: DiscountPolicy;

    changeDiscountPolicy(discountPolicy: DiscountPolicy): void {
        this.discountPolicy = discountPolicy;
    }
}

const avatar = new Movie("아바타",
    120,
    Money.wons(10000),
    new AmountDiscountPolicy(Money.wons(800), /* ... */)
);

avatar.changeDiscountPolicy(new PercentDiscountPolicy(0.1, /* ... */));
```

### 8.3 합성

`Movie`가 요금을 계산하기 위해 `DiscountPolicy`의 코드를 재사용하는 방법이 합성이다. 상속이 부모 클래스의 코드와 자식 클래스의 코드를 컴파일 시점에 하나의 단위로 **강하게 결합**하는 데 비해, `Movie`는 `DiscountPolicy`의 인터페이스를 통해 **약하게 결합**된다.

합성은 상속이 가지는 두 가지 문제점을 모두 해결한다:

| 문제 | 상속 | 합성 |
|---|---|---|
| **캡슐화** | 부모 클래스 구현이 자식에게 노출 | 인터페이스를 통해서만 재사용하므로 구현 캡슐화 |
| **유연성** | 컴파일 시점에 관계 결정, 실행 시점 변경 불가 | 인스턴스를 교체하면 되므로 실행 시점 변경 가능 |
| **결합도** | 클래스를 통해 강하게 결합 | 메시지를 통해 느슨하게 결합 |

따라서 코드 재사용을 위해서는 **상속보다는 합성을 선호**하는 것이 더 좋은 방법이다[GOF94].

그렇다고 해서 상속을 절대 사용하지 말라는 것은 아니다. 대부분의 설계에서는 상속과 합성을 함께 사용해야 한다. `Movie`와 `DiscountPolicy`는 합성 관계로 연결돼 있고, `DiscountPolicy`와 `AmountDiscountPolicy`, `PercentDiscountPolicy`는 상속 관계로 연결돼 있다. 코드를 재사용하는 경우에는 상속보다 합성을 선호하는 것이 옳지만, **다형성을 위해 인터페이스를 재사용하는 경우**에는 상속과 합성을 함께 조합해서 사용할 수밖에 없다.

> **핵심 통찰**: 객체지향 프로그래밍의 핵심은 클래스 안에 속성과 메서드를 채워 넣는 작업이나 상속을 이용해 코드를 재사용하는 방법이 아니다. 객체지향에서 가장 중요한 것은 애플리케이션의 기능을 구현하기 위해 협력에 참여하는 객체들 사이의 상호작용이다. 객체들은 협력에 참여하기 위해 역할을 부여받고 역할에 적합한 책임을 수행한다.

---

## 설계 원칙

| 원칙 | 설명 | 예제에서의 적용 |
|---|---|---|
| **추상화** | 세부사항을 무시하고 상위 정책만으로 설계를 표현한다 | `DiscountPolicy`, `DiscountCondition`이라는 추상 타입 사용 |
| **상속** | 부모 클래스의 인터페이스와 구현을 자식 클래스가 물려받는다 | `AmountDiscountPolicy`, `PercentDiscountPolicy`가 `DiscountPolicy` 상속 |
| **다형성** | 동일한 메시지를 수신했을 때 객체의 타입에 따라 다르게 응답한다 | `Movie`가 `calculateDiscountAmount` 메시지를 전송하면 실제 할인 정책에 따라 다른 메서드 실행 |
| **합성** | 다른 객체의 인스턴스를 자신의 인스턴스 변수로 포함하여 재사용한다 | `Movie`가 `DiscountPolicy`를 인스턴스 변수로 포함 |
| **캡슐화** | 객체 내부의 세부사항을 감추고 외부에는 인터페이스만 공개한다 | 모든 클래스의 속성이 `private`, `public` 메서드로만 접근 |
| **인터페이스와 구현의 분리** | 퍼블릭 인터페이스와 내부 구현을 분리하여 변경의 파급효과를 제어한다 | `Movie`는 `DiscountPolicy`의 `calculateDiscountAmount`만 알면 됨 |
| **TEMPLATE METHOD 패턴** | 부모 클래스에 알고리즘 골격을 정의하고, 세부 단계를 자식 클래스에 위임한다 | `DiscountPolicy`의 `calculateDiscountAmount` → `getDiscountAmount` |

---

## 요약

- **객체지향은 클래스가 아닌 객체에 초점을 맞춰야 한다**: 어떤 클래스가 필요한지보다 어떤 객체들이 필요한지를 먼저 고민하고, 객체를 협력하는 공동체의 일원으로 바라봐야 한다.
- **도메인의 구조를 따르는 프로그램 구조**: 클래스의 이름과 관계는 도메인 개념을 반영해야 한다.
- **인터페이스와 구현의 분리**: 객체의 상태는 `private`으로 숨기고 행동만 `public`으로 공개한다. 이것이 자율적인 객체를 만드는 핵심이다.
- **협력하는 객체들의 공동체**: 시스템의 기능은 객체들 간의 협력으로 구현된다. 메시지 전송이 객체 간 상호작용의 유일한 방법이다.
- **상속과 다형성**: 상속은 인터페이스를 물려받아 다형적인 협력을 가능하게 한다. 다형성은 동일한 메시지에 대해 객체 타입에 따라 다른 메서드가 실행되는 것이다.
- **컴파일 시간 의존성 vs 실행 시간 의존성**: 코드 수준의 의존성과 실행 시점의 의존성이 다를 수 있으며, 이것이 유연한 설계의 핵심이다.
- **추상화의 힘**: 추상화를 중심으로 설계하면 기존 코드를 수정하지 않고도 새로운 기능을 추가할 수 있다.
- **합성이 상속보다 낫다**: 코드 재사용을 위해서는 상속보다 합성을 선호하라. 상속은 캡슐화를 위반하고 설계를 유연하지 못하게 만든다. 다만 다형성을 위한 인터페이스 재사용에는 상속이 필요하다.
- **설계는 트레이드오프의 산물**: 유연성과 가독성, 자율성과 결합도 등 항상 균형을 고민해야 한다.

---

## 다른 챕터와의 관계

- **Chapter 1 (객체, 설계)**: 1장에서 직관적으로 체험한 캡슐화, 의존성 관리, 인터페이스와 구현의 분리 등의 개념을 이 장에서 상속, 다형성, 추상화라는 객체지향의 핵심 메커니즘으로 체계화한다. 1장의 티켓 판매 시스템이 `Long` 타입으로 금액을 처리했던 것과 달리, 이 장에서는 `Money`라는 도메인 개념을 객체로 표현하는 방법을 보여준다.
- **Chapter 3 (역할, 책임, 협력)**: 이 장에서 코드를 통해 보여준 객체 간의 협력을 역할, 책임, 협력이라는 개념적 프레임워크로 설명한다. `DiscountPolicy`와 `DiscountCondition`이 수행하는 역할과 책임이 어떻게 협력 안에서 정의되는지를 더 깊이 다룬다.
- **Chapter 4 (설계 품질과 트레이드오프)**: 이 장에서 책임 중심으로 설계한 영화 예매 시스템을 데이터 중심으로 설계하면 어떤 문제가 발생하는지를 대비하여 보여준다. 동일한 요구사항에 대해 캡슐화, 응집도, 결합도라는 기준으로 두 설계를 비교 분석한다.
- **Chapter 10 (상속과 코드 재사용)**: 이 장에서 간략히 언급한 "상속은 캡슐화를 위반하고 설계를 유연하지 못하게 만든다"는 주장을 구체적인 코드 사례를 통해 심층적으로 분석한다.
- **Chapter 11 (합성과 유연한 설계)**: 이 장에서 합성이 상속보다 나은 이유를 간단히 설명했다면, 11장에서는 합성을 활용한 유연한 설계 기법을 다양한 패턴과 함께 본격적으로 다룬다.
