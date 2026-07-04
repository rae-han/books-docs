# Chapter 4: Design Quality and Tradeoffs (설계 품질과 트레이드오프)

## 핵심 질문

데이터 중심 설계와 책임 중심 설계는 어떤 차이가 있는가? 캡슐화, 응집도, 결합도라는 세 가지 품질 기준으로 평가했을 때, 왜 데이터 중심 설계는 변경에 취약한 구조를 만들어 내는가?

---

## 1. 데이터 중심의 영화 예매 시스템

객체지향 설계에서 시스템을 객체로 분할하는 방법은 크게 두 가지다.

| 분할 방법 | 중심축 | 초점 | 객체를 바라보는 시각 |
|---|---|---|---|
| **데이터 중심** | 상태(데이터) | 객체가 포함하는 데이터 | 독립된 데이터 덩어리 |
| **책임 중심** | 책임(행동) | 객체가 수행하는 행동 | 협력하는 공동체의 일원 |

결론부터 말하면, 훌륭한 객체지향 설계는 데이터가 아니라 **책임**에 초점을 맞춰야 한다. 그 이유는 **변경**과 관련이 있다.

- **객체의 상태는 구현에 속한다.** 구현은 불안정하기 때문에 변하기 쉽다. 상태를 분할의 중심축으로 삼으면 구현 세부사항이 인터페이스에 스며들어 캡슐화가 무너진다.
- **객체의 책임은 인터페이스에 속한다.** 객체는 책임을 드러내는 안정적인 인터페이스 뒤로 상태를 캡슐화함으로써 구현 변경이 외부로 퍼지는 것을 방지한다.

> **핵심 통찰**: 데이터 중심의 관점에서 객체는 자신이 포함하는 데이터를 조작하는 데 필요한 오퍼레이션을 정의한다. 책임 중심의 관점에서 객체는 다른 객체가 요청할 수 있는 오퍼레이션을 위해 필요한 상태를 보관한다. 전자는 "데이터가 무엇인가?"를 묻고, 후자는 "책임이 무엇인가?"를 묻는다.

2장에서는 책임을 기준으로 분할한 영화 예매 시스템을 살펴봤다. 이번 장에서는 관점을 바꿔 **데이터를 기준으로 분할**한 설계를 살펴보고, 왜 나쁜지 비교해 본다.

### 1.1 데이터를 준비하자

데이터 중심 설계는 "이 객체가 내부에 저장해야 하는 **데이터가 무엇인가**?"를 묻는 것으로 시작한다. Movie에 저장될 데이터를 결정하는 것으로 시작하자.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Movie {
    private String title;
    private Duration runningTime;
    private Money fee;
    private List<DiscountCondition> discountConditions;

    private MovieType movieType;
    private Money discountAmount;
    private double discountPercent;
}
```

</details>

```typescript
// TypeScript
class Movie {
    private title: string;
    private runningTime: number;      // milliseconds
    private fee: Money;
    private discountConditions: DiscountCondition[];

    private movieType: MovieType;
    private discountAmount: Money;
    private discountPercent: number;
}
```

데이터 중심의 Movie 클래스에는 책임 중심 설계와 비교했을 때 두드러지는 차이점이 있다:

1. **할인 조건 목록(`discountConditions`)이 Movie 안에 직접 포함**돼 있다. 이전 설계에서는 DiscountPolicy라는 별도 클래스로 분리했었다.
2. **할인 금액(`discountAmount`)과 할인 비율(`discountPercent`)을 Movie에서 직접 정의**하고 있다. 할인 정책을 별도 클래스로 분리하지 않았다.
3. **할인 정책의 종류를 결정하는 열거형 `movieType`**이 추가됐다.

한 시점에 `discountAmount`와 `discountPercent` 중 하나의 값만 사용된다. 어떤 값을 사용할지는 `movieType`이 결정한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public enum MovieType {
    AMOUNT_DISCOUNT,    // 금액 할인 정책
    PERCENT_DISCOUNT,   // 비율 할인 정책
    NONE_DISCOUNT       // 미적용
}
```

</details>

```typescript
// TypeScript
enum MovieType {
    AMOUNT_DISCOUNT = "AMOUNT_DISCOUNT",     // 금액 할인 정책
    PERCENT_DISCOUNT = "PERCENT_DISCOUNT",   // 비율 할인 정책
    NONE_DISCOUNT = "NONE_DISCOUNT",         // 미적용
}
```

> **핵심 통찰**: 객체의 종류를 저장하는 인스턴스 변수(`movieType`)와 종류에 따라 배타적으로 사용되는 인스턴스 변수(`discountAmount`, `discountPercent`)를 하나의 클래스에 함께 포함시키는 패턴은 데이터 중심 설계에서 흔히 볼 수 있는 전형적인 안티패턴이다.

이제 캡슐화의 원칙에 따라 내부 데이터가 외부로 노출되지 않도록 접근자(*Accessor - getter*)와 수정자(*Mutator - setter*)를 추가한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Movie {
    public MovieType getMovieType() {
        return movieType;
    }

    public void setMovieType(MovieType movieType) {
        this.movieType = movieType;
    }

    public Money getFee() {
        return fee;
    }

    public void setFee(Money fee) {
        this.fee = fee;
    }

    public List<DiscountCondition> getDiscountConditions() {
        return Collections.unmodifiableList(discountConditions);
    }

    public void setDiscountConditions(List<DiscountCondition> discountConditions) {
        this.discountConditions = discountConditions;
    }

    public Money getDiscountAmount() {
        return discountAmount;
    }

    public void setDiscountAmount(Money discountAmount) {
        this.discountAmount = discountAmount;
    }

    public double getDiscountPercent() {
        return discountPercent;
    }

    public void setDiscountPercent(double discountPercent) {
        this.discountPercent = discountPercent;
    }
}
```

</details>

```typescript
// TypeScript
class Movie {
    getMovieType(): MovieType { return this.movieType; }
    setMovieType(movieType: MovieType): void { this.movieType = movieType; }

    getFee(): Money { return this.fee; }
    setFee(fee: Money): void { this.fee = fee; }

    getDiscountConditions(): readonly DiscountCondition[] {
        return [...this.discountConditions];
    }
    setDiscountConditions(conditions: DiscountCondition[]): void {
        this.discountConditions = conditions;
    }

    getDiscountAmount(): Money { return this.discountAmount; }
    setDiscountAmount(amount: Money): void { this.discountAmount = amount; }

    getDiscountPercent(): number { return this.discountPercent; }
    setDiscountPercent(percent: number): void { this.discountPercent = percent; }
}
```

### 1.2 할인 조건 구현

할인 조건에는 순번 조건과 기간 조건 두 가지가 있다. 역시 데이터 중심으로 접근하므로, "할인 조건을 구현하는 데 필요한 데이터는 무엇인가?"를 먼저 묻는다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public enum DiscountConditionType {
    SEQUENCE,   // 순번 조건
    PERIOD      // 기간 조건
}
```

</details>

```typescript
// TypeScript
enum DiscountConditionType {
    SEQUENCE = "SEQUENCE",   // 순번 조건
    PERIOD = "PERIOD",       // 기간 조건
}
```

DiscountCondition은 할인 조건의 타입(`type`)을 포함하며, 순번 조건에서만 사용되는 상영 순번(`sequence`)과 기간 조건에서만 사용되는 요일(`dayOfWeek`), 시작 시간(`startTime`), 종료 시간(`endTime`)을 함께 포함한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class DiscountCondition {
    private DiscountConditionType type;

    private int sequence;

    private DayOfWeek dayOfWeek;
    private LocalTime startTime;
    private LocalTime endTime;

    public DiscountConditionType getType() { return type; }
    public void setType(DiscountConditionType type) { this.type = type; }

    public DayOfWeek getDayOfWeek() { return dayOfWeek; }
    public void setDayOfWeek(DayOfWeek dayOfWeek) { this.dayOfWeek = dayOfWeek; }

    public LocalTime getStartTime() { return startTime; }
    public void setStartTime(LocalTime startTime) { this.startTime = startTime; }

    public LocalTime getEndTime() { return endTime; }
    public void setEndTime(LocalTime endTime) { this.endTime = endTime; }

    public int getSequence() { return sequence; }
    public void setSequence(int sequence) { this.sequence = sequence; }
}
```

</details>

```typescript
// TypeScript
class DiscountCondition {
    private type: DiscountConditionType;
    private sequence: number;
    private dayOfWeek: number;       // 0(일) ~ 6(토)
    private startTime: string;       // "HH:mm"
    private endTime: string;         // "HH:mm"

    getType(): DiscountConditionType { return this.type; }
    setType(type: DiscountConditionType): void { this.type = type; }

    getDayOfWeek(): number { return this.dayOfWeek; }
    setDayOfWeek(dayOfWeek: number): void { this.dayOfWeek = dayOfWeek; }

    getStartTime(): string { return this.startTime; }
    setStartTime(startTime: string): void { this.startTime = startTime; }

    getEndTime(): string { return this.endTime; }
    setEndTime(endTime: string): void { this.endTime = endTime; }

    getSequence(): number { return this.sequence; }
    setSequence(sequence: number): void { this.sequence = sequence; }
}
```

### 1.3 Screening, Reservation, Customer

같은 방식으로 나머지 클래스들을 구현한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Screening {
    private Movie movie;
    private int sequence;
    private LocalDateTime whenScreened;

    public Movie getMovie() { return movie; }
    public void setMovie(Movie movie) { this.movie = movie; }

    public LocalDateTime getWhenScreened() { return whenScreened; }
    public void setWhenScreened(LocalDateTime whenScreened) {
        this.whenScreened = whenScreened;
    }

    public int getSequence() { return sequence; }
    public void setSequence(int sequence) { this.sequence = sequence; }
}

public class Reservation {
    private Customer customer;
    private Screening screening;
    private Money fee;
    private int audienceCount;

    public Reservation(Customer customer, Screening screening,
                       Money fee, int audienceCount) {
        this.customer = customer;
        this.screening = screening;
        this.fee = fee;
        this.audienceCount = audienceCount;
    }

    // getter/setter 생략
}

public class Customer {
    private String name;
    private String id;

    public Customer(String name, String id) {
        this.name = name;
        this.id = id;
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

    getMovie(): Movie { return this.movie; }
    setMovie(movie: Movie): void { this.movie = movie; }

    getWhenScreened(): Date { return this.whenScreened; }
    setWhenScreened(whenScreened: Date): void { this.whenScreened = whenScreened; }

    getSequence(): number { return this.sequence; }
    setSequence(sequence: number): void { this.sequence = sequence; }
}

class Reservation {
    constructor(
        private customer: Customer,
        private screening: Screening,
        private fee: Money,
        private audienceCount: number,
    ) {}
}

class Customer {
    constructor(
        private name: string,
        private id: string,
    ) {}
}
```

### 1.4 데이터 클래스 관계

```
┌──────────────┐     ┌─────────────────────┐     ┌───────────────────────┐
│  Screening   │────▶│       Movie         │────▶│  DiscountCondition    │
│──────────────│     │─────────────────────│     │───────────────────────│
│ movie        │     │ title               │     │ type                  │
│ sequence     │     │ runningTime         │     │ sequence              │
│ whenScreened │     │ fee                 │     │ dayOfWeek             │
└──────────────┘     │ movieType           │     │ startTime             │
                     │ discountAmount      │     │ endTime               │
                     │ discountPercent     │     └───────────────────────┘
                     │ discountConditions  │
                     └─────────────────────┘

┌──────────────┐     ┌──────────────┐
│ Reservation  │────▶│   Customer   │
│──────────────│     │──────────────│
│ customer     │     │ name         │
│ screening    │     │ id           │
│ fee          │     └──────────────┘
│ audienceCount│
└──────────────┘
```

### 1.5 영화를 예매하자

ReservationAgency는 데이터 클래스들을 조합해서 영화 예매 절차를 구현하는 클래스다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class ReservationAgency {
    public Reservation reserve(Screening screening, Customer customer,
                               int audienceCount) {
        Movie movie = screening.getMovie();

        boolean discountable = false;
        for (DiscountCondition condition : movie.getDiscountConditions()) {
            if (condition.getType() == DiscountConditionType.PERIOD) {
                discountable =
                    screening.getWhenScreened().getDayOfWeek()
                        .equals(condition.getDayOfWeek()) &&
                    condition.getStartTime()
                        .compareTo(screening.getWhenScreened().toLocalTime()) <= 0 &&
                    condition.getEndTime()
                        .compareTo(screening.getWhenScreened().toLocalTime()) >= 0;
            } else {
                discountable =
                    condition.getSequence() == screening.getSequence();
            }

            if (discountable) {
                break;
            }
        }

        Money fee;
        if (discountable) {
            Money discountAmount = Money.ZERO;

            switch (movie.getMovieType()) {
                case AMOUNT_DISCOUNT:
                    discountAmount = movie.getDiscountAmount();
                    break;
                case PERCENT_DISCOUNT:
                    discountAmount = movie.getFee().times(movie.getDiscountPercent());
                    break;
                case NONE_DISCOUNT:
                    discountAmount = Money.ZERO;
                    break;
            }

            fee = movie.getFee().minus(discountAmount);
        } else {
            fee = movie.getFee();
        }

        return new Reservation(customer, screening, fee, audienceCount);
    }
}
```

</details>

```typescript
// TypeScript
class ReservationAgency {
    reserve(screening: Screening, customer: Customer,
            audienceCount: number): Reservation {
        const movie = screening.getMovie();

        let discountable = false;
        for (const condition of movie.getDiscountConditions()) {
            if (condition.getType() === DiscountConditionType.PERIOD) {
                const screenedDate = screening.getWhenScreened();
                discountable =
                    screenedDate.getDay() === condition.getDayOfWeek() &&
                    condition.getStartTime() <= toTimeString(screenedDate) &&
                    condition.getEndTime() >= toTimeString(screenedDate);
            } else {
                discountable =
                    condition.getSequence() === screening.getSequence();
            }

            if (discountable) break;
        }

        let fee: Money;
        if (discountable) {
            let discountAmount = Money.ZERO;

            switch (movie.getMovieType()) {
                case MovieType.AMOUNT_DISCOUNT:
                    discountAmount = movie.getDiscountAmount();
                    break;
                case MovieType.PERCENT_DISCOUNT:
                    discountAmount = movie.getFee().times(movie.getDiscountPercent());
                    break;
                case MovieType.NONE_DISCOUNT:
                    discountAmount = Money.ZERO;
                    break;
            }

            fee = movie.getFee().minus(discountAmount);
        } else {
            fee = movie.getFee();
        }

        return new Reservation(customer, screening, fee, audienceCount);
    }
}
```

`reserve` 메서드는 크게 두 부분으로 나뉜다:

1. **할인 가능 여부 확인** (for 문): DiscountCondition을 순회하며 타입에 따라 기간 조건 또는 순번 조건으로 판단한다.
2. **예매 요금 계산** (if 문): `discountable`이 `true`이면 할인 정책(금액/비율/미적용)에 따라 할인 요금을 계산하고, `false`이면 기본 요금을 사용한다.

모든 제어 로직이 ReservationAgency 한 곳에 집중되어 있다. 데이터 클래스들은 단지 데이터를 저장하고 꺼내주는 역할만 한다.

---

## 2. 설계 트레이드오프

데이터 중심 설계와 책임 중심 설계의 장단점을 비교하기 위해 **캡슐화**, **응집도**, **결합도** 세 가지 품질 척도를 사용한다.

### 2.1 캡슐화

상태와 행동을 하나의 객체 안에 모으는 이유는 내부 구현을 외부로부터 감추기 위해서다. 여기서 **구현**(*Implementation*)이란 나중에 변경될 가능성이 높은 어떤 것을 가리킨다.

- **변경될 가능성이 높은 부분**: 구현
- **상대적으로 안정적인 부분**: 인터페이스

객체지향의 가장 중요한 원리는 **불안정한 구현 세부사항을 안정적인 인터페이스 뒤로 캡슐화하는 것**이다. 캡슐화는 외부에서 알 필요가 없는 부분을 감춤으로써 대상을 단순화하는 추상화의 한 종류다.

> 복잡성을 다루기 위한 가장 효과적인 도구는 추상화다. 다양한 추상화 유형을 사용할 수 있지만 객체지향 프로그래밍에서 복잡성을 취급하는 주요한 추상화 방법은 캡슐화다. 그러나 프로그래밍할 때 객체지향 언어를 사용한다고 해서 캡슐화가 잘 될 것이라고 보장할 수는 없다. 훌륭한 프로그래밍 기술을 적용해서 캡슐화를 향상시킬 수는 있겠지만, 객체지향 프로그래밍을 통해 전반적으로 얻을 수 있는 장점은 오직 설계 과정 동안 캡슐화를 목표로 인식할 때만 달성될 수 있다 [Wirfs-Brock89].

> 유지보수성이 목표다. 여기서 유지보수성이란 두려움 없이, 주저함 없이, 저항감 없이 코드를 변경할 수 있는 능력을 말한다. ··· 가장 중요한 동료는 캡슐화다. 우리는 시스템의 한 부분을 다른 부분으로부터 감춤으로써 뜻밖의 피해가 발생할 수 있는 가능성을 사전에 방지할 수 있다 [Bain08].

정리하면 **캡슐화란 변경 가능성이 높은 부분을 객체 내부로 숨기는 추상화 기법**이다. 변경될 수 있는 어떤 것이라도 캡슐화해야 한다. 이것이 바로 객체지향 설계의 핵심이다.

### 2.2 응집도와 결합도

응집도(*Cohesion*)와 결합도(*Coupling*)는 구조적 설계 시대에 소프트웨어 품질을 측정하기 위해 소개된 기준이지만, 객체지향 시대에도 여전히 유효하다.

| 척도 | 정의 | 좋은 설계 |
|---|---|---|
| **응집도** | 모듈 내부 요소들이 연관돼 있는 정도. 객체에 얼마나 관련 높은 책임들을 할당했는지를 나타낸다 | **높은** 응집도 |
| **결합도** | 다른 모듈에 대해 얼마나 많은 지식을 갖고 있는지. 객체가 협력에 필요한 적절한 수준의 관계만을 유지하는지를 나타낸다 | **낮은** 결합도 |

핵심은 두 개념 모두 **변경**과 깊이 연관돼 있다는 것이다.

**변경의 관점에서 본 응집도:**

```
높은 응집도 (High Cohesion)          낮은 응집도 (Low Cohesion)

┌──────────┐                        ┌──────┐ ┌──────┐ ┌──────┐
│ ████████ │ ← 변경이 하나의         │ ██   │ │  ██  │ │   ██ │
│ ████████ │   모듈 안에서만          │      │ │      │ │      │
│ ████████ │   발생                  │      │ │      │ │      │
└──────────┘                        └──────┘ └──────┘ └──────┘
                                    ↑ 변경이 여러 모듈에 분산
```

- 하나의 변경을 수용하기 위해 모듈 전체가 함께 변경된다면: **응집도가 높다**
- 모듈의 일부만 변경된다면: **응집도가 낮다**
- 하나의 변경에 대해 하나의 모듈만 변경된다면: **응집도가 높다**
- 다수의 모듈이 함께 변경된다면: **응집도가 낮다**

**변경의 관점에서 본 결합도:**

```
낮은 결합도 (Low Coupling)           높은 결합도 (High Coupling)

     ┌───┐                               ┌───┐
     │ A │                               │ A │
     └─┬─┘                               └─┬─┘
       │                            ┌───┬──┼──┬───┐
     ┌─▼─┐                        ┌─▼─┐┌▼┐┌▼┐┌▼┐┌▼┐
     │ B │                        │ B ││C││D││E││F│
     └───┘                        └───┘└─┘└─┘└─┘└─┘
A 변경 시 1개 모듈 영향             A 변경 시 4개 모듈 영향
```

- 한 모듈의 **내부 구현**을 변경했을 때 다른 모듈에 영향: **결합도가 높다**
- **퍼블릭 인터페이스**를 수정했을 때만 다른 모듈에 영향: **결합도가 낮다**

결합도가 높아도 상관없는 경우도 있다. **변경될 확률이 매우 적은 안정적인 모듈**에 의존하는 것은 문제가 되지 않는다. 예를 들어 표준 라이브러리의 `String`이나 `ArrayList`는 변경될 확률이 매우 낮기 때문에 결합도에 대해 고민할 필요가 없다. 그러나 **직접 작성한 코드**는 항상 불안정하며 언제라도 변경될 가능성이 높으므로 낮은 결합도를 유지하려고 노력해야 한다.

> **핵심 통찰**: 캡슐화의 정도가 응집도와 결합도에 영향을 미친다. 캡슐화를 지키면 모듈 안의 응집도는 높아지고 모듈 사이의 결합도는 낮아진다. 캡슐화를 위반하면 응집도는 낮아지고 결합도는 높아진다. 따라서 응집도와 결합도를 고려하기 전에 **먼저 캡슐화를 향상시키기 위해 노력하라**.

---

## 3. 데이터 중심 설계의 문제점

기능적 측면에서 데이터 중심 설계와 책임 중심 설계는 완전히 동일하다. 하지만 설계 관점에서는 완전히 다르다. 근본적 차이는 **캡슐화를 다루는 방식**이다.

- **데이터 중심 설계**: 캡슐화를 위반하고 객체의 내부 구현을 인터페이스의 일부로 만든다.
- **책임 중심 설계**: 객체의 내부 구현을 안정적인 인터페이스 뒤로 캡슐화한다.

데이터 중심 설계의 대표적인 문제점 세 가지를 살펴보자.

### 3.1 캡슐화 위반

데이터 중심으로 설계한 Movie 클래스를 보면, 메서드를 통해서만 내부 상태에 접근할 수 있으므로 캡슐화 원칙을 지키는 것처럼 보인다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Movie {
    private Money fee;

    public Money getFee() {
        return fee;
    }

    public void setFee(Money fee) {
        this.fee = fee;
    }
}
```

</details>

```typescript
// TypeScript
class Movie {
    private fee: Money;

    getFee(): Money {
        return this.fee;
    }

    setFee(fee: Money): void {
        this.fee = fee;
    }
}
```

안타깝게도 접근자와 수정자 메서드는 **객체 내부 상태에 대한 어떤 정보도 캡슐화하지 못한다**. `getFee`와 `setFee`는 Movie 내부에 `Money` 타입의 `fee`라는 인스턴스 변수가 존재한다는 사실을 퍼블릭 인터페이스에 노골적으로 드러낸다.

Movie가 캡슐화 원칙을 어기게 된 근본적인 원인은 **객체가 수행할 책임이 아니라 내부에 저장할 데이터에 초점을 맞췄기 때문**이다. 구현을 캡슐화할 수 있는 적절한 책임은 **협력이라는 문맥을 고려할 때만** 얻을 수 있다.

앨런 홀럽(Allen Holub)은 접근자와 수정자에 과도하게 의존하는 설계 방식을 **추측에 의한 설계 전략**(*Design-by-Guessing Strategy*) [Holub04]이라고 부른다. 이 전략은 객체가 사용될 협력을 고려하지 않고, 다양한 상황에서 사용될 것이라는 막연한 추측을 기반으로 설계를 진행한다. 결과적으로 내부 상태를 드러내는 메서드를 최대한 많이 추가해야 한다는 압박에 시달리게 되고, 대부분의 내부 구현이 퍼블릭 인터페이스에 그대로 노출된다.

### 3.2 높은 결합도

데이터 중심 설계는 접근자와 수정자를 통해 내부 구현을 인터페이스의 일부로 만들기 때문에 캡슐화를 위반한다. 객체 내부의 구현이 인터페이스에 드러나면 클라이언트가 **구현에 강하게 결합**된다.

예를 들어 `fee`의 타입을 변경한다고 가정하면:
1. `getFee` 메서드의 반환 타입도 수정해야 한다.
2. `getFee`를 호출하는 ReservationAgency의 구현도 함께 수정해야 한다.

`getFee`를 사용하는 것은 인스턴스 변수 `fee`의 가시성을 `private`에서 `public`으로 변경하는 것과 거의 동일하다.

결합도 측면에서 또 다른 단점은, **여러 데이터 객체를 사용하는 제어 로직이 특정 객체 안에 집중**된다는 것이다. ReservationAgency가 모든 데이터 객체에 의존하고 있어, 어떤 데이터 객체를 변경하더라도 ReservationAgency를 함께 변경해야 한다.

```
                    ┌──────────────────┐
                    │ ReservationAgency│ ← 모든 의존성이 모이는 결합도의 집결지
                    │   reserve()      │
                    └───┬──┬──┬──┬──┬──┘
                        │  │  │  │  │
          ┌─────────────┘  │  │  │  └──────────────┐
          ▼                ▼  │  ▼                  ▼
    ┌──────────┐  ┌───────┐  │  ┌──────────────┐  ┌──────────┐
    │Screening │  │ Movie │  │  │DiscountCond. │  │ Customer │
    └──────────┘  └───────┘  │  └──────────────┘  └──────────┘
                             ▼
                      ┌─────────────┐
                      │ Reservation │
                      └─────────────┘
```

시스템 안의 **어떤 변경도 ReservationAgency의 변경을 유발**한다. 데이터 중심 설계는 전체 시스템을 하나의 거대한 의존성 덩어리로 만들어 버리기 때문에, 어떤 변경이라도 발생하면 시스템 전체가 요동친다.

### 3.3 낮은 응집도

서로 다른 이유로 변경되는 코드가 하나의 모듈 안에 공존할 때 모듈의 응집도가 낮다고 말한다. ReservationAgency의 코드를 수정해야 하는 경우를 살펴보자:

- 할인 정책이 추가될 경우
- 할인 정책별로 할인 요금을 계산하는 방법이 변경될 경우
- 할인 조건이 추가되는 경우
- 할인 조건별로 할인 여부를 판단하는 방법이 변경될 경우
- 예매 요금을 계산하는 방법이 변경될 경우

낮은 응집도는 두 가지 측면에서 문제를 일으킨다:

1. **변경과 무관한 코드가 영향을 받는다.** 할인 정책을 선택하는 코드와 할인 조건을 판단하는 코드가 함께 존재하기 때문에, 새로운 할인 정책을 추가하는 작업이 할인 조건에도 영향을 미칠 수 있다.
2. **하나의 요구사항 변경을 반영하기 위해 여러 모듈을 동시에 수정해야 한다.** 새로운 할인 정책을 추가하려면 `MovieType`에 열거형 값 추가, `ReservationAgency`의 switch 문에 case 절 추가, `Movie`에 필요한 데이터 추가 등 **세 개의 클래스를 함께 수정**해야 한다.

어떤 요구사항 변경을 수용하기 위해 하나 이상의 클래스를 수정해야 하는 것은 **설계의 응집도가 낮다는 증거**다.

#### 단일 책임 원칙 (SRP)

로버트 마틴(Robert C. Martin)은 모듈의 응집도가 변경과 연관이 있다는 사실을 강조하기 위해 **단일 책임 원칙**(*Single Responsibility Principle, SRP*) [Martin02]이라는 설계 원칙을 제시했다. 클래스는 **단 한 가지의 변경 이유만** 가져야 한다는 것이다.

한 가지 주의할 점은, 단일 책임 원칙에서 '책임'이라는 말이 **'변경의 이유'**라는 의미로 사용된다는 것이다. 이는 역할·책임·협력에서 이야기하는 책임과는 다르며, 변경과 관련된 더 큰 개념을 가리킨다.

---

## 4. 자율적인 객체를 향해

### 4.1 캡슐화를 지켜라

캡슐화는 설계의 제1원리다. 데이터 중심 설계가 낮은 응집도와 높은 결합도라는 문제로 몸살을 앓게 된 근본적인 원인은 캡슐화 원칙을 위반했기 때문이다. 객체는 자신이 어떤 데이터를 가지고 있는지를 내부에 캡슐화하고, 스스로의 상태를 책임져야 한다. 외부에서는 인터페이스에 정의된 메서드를 통해서만 상태에 접근할 수 있어야 한다.

여기서 말하는 메서드는 단순히 속성의 값을 반환하거나 변경하는 접근자/수정자를 의미하는 것이 아니다. **객체가 책임져야 하는 무언가를 수행하는 메서드**다. 속성의 가시성을 `private`으로 설정해도 접근자와 수정자를 통해 속성을 외부로 제공한다면 캡슐화를 위반하는 것이다.

#### Rectangle 예제

사각형을 표현하는 간단한 클래스 Rectangle로 캡슐화 위반의 문제를 구체적으로 살펴보자.

### 나쁜 설계

<details>
<summary>원문 Java 코드</summary>

```java
// Java
class Rectangle {
    private int left;
    private int top;
    private int right;
    private int bottom;

    public Rectangle(int left, int top, int right, int bottom) {
        this.left = left;
        this.top = top;
        this.right = right;
        this.bottom = bottom;
    }

    public int getLeft() { return left; }
    public void setLeft(int left) { this.left = left; }
    public int getTop() { return top; }
    public void setTop(int top) { this.top = top; }
    public int getRight() { return right; }
    public void setRight(int right) { this.right = right; }
    public int getBottom() { return bottom; }
    public void setBottom(int bottom) { this.bottom = bottom; }
}

// 외부에서 사각형의 크기를 변경하는 코드
class AnyClass {
    void anyMethod(Rectangle rectangle, int multiple) {
        rectangle.setRight(rectangle.getRight() * multiple);
        rectangle.setBottom(rectangle.getBottom() * multiple);
    }
}
```

</details>

```typescript
// TypeScript
class Rectangle {
    constructor(
        private left: number,
        private top: number,
        private right: number,
        private bottom: number,
    ) {}

    getLeft(): number { return this.left; }
    setLeft(left: number): void { this.left = left; }
    getTop(): number { return this.top; }
    setTop(top: number): void { this.top = top; }
    getRight(): number { return this.right; }
    setRight(right: number): void { this.right = right; }
    getBottom(): number { return this.bottom; }
    setBottom(bottom: number): void { this.bottom = bottom; }
}

// 외부에서 사각형의 크기를 변경
function anyMethod(rectangle: Rectangle, multiple: number): void {
    rectangle.setRight(rectangle.getRight() * multiple);
    rectangle.setBottom(rectangle.getBottom() * multiple);
}
```

이 코드에는 두 가지 문제가 있다:

1. **코드 중복**: 다른 곳에서도 사각형의 크기를 증가시키는 코드가 필요하면 `getRight`/`getBottom`으로 값을 가져와 수정자로 설정하는 유사한 코드가 반복된다.
2. **변경에 취약**: Rectangle이 `right`와 `bottom` 대신 `length`와 `height`를 사용하도록 수정하면, 접근자/수정자의 이름이 바뀌고, 이 메서드를 사용하던 모든 코드에 영향을 미친다.

### 좋은 설계

<details>
<summary>원문 Java 코드</summary>

```java
// Java
class Rectangle {
    public void enlarge(int multiple) {
        right *= multiple;
        bottom *= multiple;
    }
}
```

</details>

```typescript
// TypeScript
class Rectangle {
    enlarge(multiple: number): void {
        this.right *= multiple;
        this.bottom *= multiple;
    }
}
```

Rectangle을 변경하는 주체를 외부 객체에서 **Rectangle 자신**으로 이동시켰다. 자신의 크기를 Rectangle 스스로 증가시키도록 **책임을 이동**시킨 것이다. 이것이 바로 객체가 자기 스스로를 책임진다는 말의 의미다.

### 4.2 스스로 자신의 데이터를 책임지는 객체

상태와 행동을 객체라는 하나의 단위로 묶는 이유는 객체 스스로 자신의 상태를 처리할 수 있게 하기 위해서다. 객체를 설계할 때 "이 객체가 어떤 데이터를 포함해야 하는가?"라는 질문은 다음 **두 개의 질문으로 분리**해야 한다:

1. 이 객체가 어떤 데이터를 포함해야 하는가?
2. 이 객체가 데이터에 대해 수행해야 하는 **오퍼레이션**은 무엇인가?

두 질문을 조합하면 객체의 내부 상태를 저장하는 방식과 호출할 수 있는 오퍼레이션의 집합, 즉 새로운 데이터 타입을 만들 수 있다.

#### DiscountCondition 개선

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class DiscountCondition {
    private DiscountConditionType type;
    private int sequence;
    private DayOfWeek dayOfWeek;
    private LocalTime startTime;
    private LocalTime endTime;

    public DiscountConditionType getType() {
        return type;
    }

    public boolean isDiscountable(DayOfWeek dayOfWeek, LocalTime time) {
        if (type != DiscountConditionType.PERIOD) {
            throw new IllegalArgumentException();
        }
        return this.dayOfWeek.equals(dayOfWeek) &&
               this.startTime.compareTo(time) <= 0 &&
               this.endTime.compareTo(time) >= 0;
    }

    public boolean isDiscountable(int sequence) {
        if (type != DiscountConditionType.SEQUENCE) {
            throw new IllegalArgumentException();
        }
        return this.sequence == sequence;
    }
}
```

</details>

```typescript
// TypeScript
class DiscountCondition {
    private type: DiscountConditionType;
    private sequence: number;
    private dayOfWeek: number;
    private startTime: string;
    private endTime: string;

    getType(): DiscountConditionType {
        return this.type;
    }

    isDiscountableByPeriod(dayOfWeek: number, time: string): boolean {
        if (this.type !== DiscountConditionType.PERIOD) {
            throw new Error("Period condition only");
        }
        return this.dayOfWeek === dayOfWeek &&
               this.startTime <= time &&
               this.endTime >= time;
    }

    isDiscountableBySequence(sequence: number): boolean {
        if (this.type !== DiscountConditionType.SEQUENCE) {
            throw new Error("Sequence condition only");
        }
        return this.sequence === sequence;
    }
}
```

이제 DiscountCondition은 자기 자신의 데이터를 이용해 할인 가능 여부를 스스로 판단한다. 각 `isDiscountable` 메서드 안에서 `type` 값을 이용해 현재의 할인 조건 타입에 맞는 적절한 메서드가 호출됐는지 검증한다.

#### Movie 개선

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Movie {
    private String title;
    private Duration runningTime;
    private Money fee;
    private List<DiscountCondition> discountConditions;

    private MovieType movieType;
    private Money discountAmount;
    private double discountPercent;

    public MovieType getMovieType() {
        return movieType;
    }

    public Money calculateAmountDiscountedFee() {
        if (movieType != MovieType.AMOUNT_DISCOUNT) {
            throw new IllegalArgumentException();
        }
        return fee.minus(discountAmount);
    }

    public Money calculatePercentDiscountedFee() {
        if (movieType != MovieType.PERCENT_DISCOUNT) {
            throw new IllegalArgumentException();
        }
        return fee.minus(fee.times(discountPercent));
    }

    public Money calculateNoneDiscountedFee() {
        if (movieType != MovieType.NONE_DISCOUNT) {
            throw new IllegalArgumentException();
        }
        return fee;
    }

    public boolean isDiscountable(LocalDateTime whenScreened, int sequence) {
        for (DiscountCondition condition : discountConditions) {
            if (condition.getType() == DiscountConditionType.PERIOD) {
                if (condition.isDiscountable(
                    whenScreened.getDayOfWeek(), whenScreened.toLocalTime())) {
                    return true;
                }
            } else {
                if (condition.isDiscountable(sequence)) {
                    return true;
                }
            }
        }
        return false;
    }
}
```

</details>

```typescript
// TypeScript
class Movie {
    private title: string;
    private runningTime: number;
    private fee: Money;
    private discountConditions: DiscountCondition[];

    private movieType: MovieType;
    private discountAmount: Money;
    private discountPercent: number;

    getMovieType(): MovieType {
        return this.movieType;
    }

    calculateAmountDiscountedFee(): Money {
        if (this.movieType !== MovieType.AMOUNT_DISCOUNT) {
            throw new Error("Amount discount only");
        }
        return this.fee.minus(this.discountAmount);
    }

    calculatePercentDiscountedFee(): Money {
        if (this.movieType !== MovieType.PERCENT_DISCOUNT) {
            throw new Error("Percent discount only");
        }
        return this.fee.minus(this.fee.times(this.discountPercent));
    }

    calculateNoneDiscountedFee(): Money {
        if (this.movieType !== MovieType.NONE_DISCOUNT) {
            throw new Error("None discount only");
        }
        return this.fee;
    }

    isDiscountable(whenScreened: Date, sequence: number): boolean {
        for (const condition of this.discountConditions) {
            if (condition.getType() === DiscountConditionType.PERIOD) {
                if (condition.isDiscountableByPeriod(
                    whenScreened.getDay(), toTimeString(whenScreened))) {
                    return true;
                }
            } else {
                if (condition.isDiscountableBySequence(sequence)) {
                    return true;
                }
            }
        }
        return false;
    }
}
```

Movie는 할인 정책 타입에 따라 요금을 계산하는 세 가지 메서드와, 할인 조건 목록을 순회하며 할인 여부를 판단하는 `isDiscountable` 메서드를 직접 구현한다.

#### Screening 개선과 ReservationAgency 간소화

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

    public Money calculateFee(int audienceCount) {
        switch (movie.getMovieType()) {
            case AMOUNT_DISCOUNT:
                if (movie.isDiscountable(whenScreened, sequence)) {
                    return movie.calculateAmountDiscountedFee().times(audienceCount);
                }
                break;
            case PERCENT_DISCOUNT:
                if (movie.isDiscountable(whenScreened, sequence)) {
                    return movie.calculatePercentDiscountedFee().times(audienceCount);
                }
                break;
            case NONE_DISCOUNT:
                return movie.calculateNoneDiscountedFee().times(audienceCount);
        }
        return movie.calculateNoneDiscountedFee().times(audienceCount);
    }
}

public class ReservationAgency {
    public Reservation reserve(Screening screening, Customer customer,
                               int audienceCount) {
        Money fee = screening.calculateFee(audienceCount);
        return new Reservation(customer, screening, fee, audienceCount);
    }
}
```

</details>

```typescript
// TypeScript
class Screening {
    constructor(
        private movie: Movie,
        private sequence: number,
        private whenScreened: Date,
    ) {}

    calculateFee(audienceCount: number): Money {
        switch (this.movie.getMovieType()) {
            case MovieType.AMOUNT_DISCOUNT:
                if (this.movie.isDiscountable(this.whenScreened, this.sequence)) {
                    return this.movie.calculateAmountDiscountedFee()
                        .times(audienceCount);
                }
                break;
            case MovieType.PERCENT_DISCOUNT:
                if (this.movie.isDiscountable(this.whenScreened, this.sequence)) {
                    return this.movie.calculatePercentDiscountedFee()
                        .times(audienceCount);
                }
                break;
            case MovieType.NONE_DISCOUNT:
                return this.movie.calculateNoneDiscountedFee()
                    .times(audienceCount);
        }
        return this.movie.calculateNoneDiscountedFee().times(audienceCount);
    }
}

class ReservationAgency {
    reserve(screening: Screening, customer: Customer,
            audienceCount: number): Reservation {
        const fee = screening.calculateFee(audienceCount);
        return new Reservation(customer, screening, fee, audienceCount);
    }
}
```

### 4.3 두 번째 설계의 클래스 관계

```
┌──────────────────┐     ┌─────────────────────────────────────┐
│    Screening      │────▶│              Movie                  │
│──────────────────│     │─────────────────────────────────────│
│ sequence         │     │ title, runningTime, fee             │
│ whenScreened     │     │ movieType, discountAmount           │
│──────────────────│     │ discountPercent, discountConditions │
│ calculateFee()   │     │─────────────────────────────────────│
└──────────────────┘     │ getMovieType()                      │
                         │ calculateAmountDiscountedFee()      │
                         │ calculatePercentDiscountedFee()     │
                         │ calculateNoneDiscountedFee()        │
                         │ isDiscountable(when, seq)           │
                         └──────────────┬──────────────────────┘
                                        │
                                        ▼
                         ┌─────────────────────────────────────┐
                         │        DiscountCondition            │
                         │─────────────────────────────────────│
                         │ type, sequence                      │
                         │ dayOfWeek, startTime, endTime       │
                         │─────────────────────────────────────│
                         │ getType()                           │
                         │ isDiscountable(dayOfWeek, time)     │
                         │ isDiscountable(sequence)            │
                         └─────────────────────────────────────┘

┌──────────────────┐     ┌──────────────┐     ┌──────────────┐
│ ReservationAgency│────▶│  Screening   │     │   Customer   │
│──────────────────│     └──────────────┘     │──────────────│
│ reserve()        │                          │ id, name     │
└──────────────────┘                          └──────────────┘
```

최소한 결합도 측면에서 ReservationAgency에 의존성이 몰려 있던 첫 번째 설계보다 개선된 것으로 보인다. 각 객체가 스스로를 책임지는 구조이기 때문이다.

---

## 5. 하지만 여전히 부족하다

두 번째 설계가 첫 번째보다 향상된 것은 사실이지만, 만족스러운 수준은 아니다. 본질적으로 두 번째 설계 역시 **데이터 중심 설계**에 속한다. 첫 번째 설계에서 발생했던 대부분의 문제가 여전히 발생한다.

### 5.1 캡슐화 위반

DiscountCondition은 자기 자신의 데이터를 스스로 처리하지만, 메서드 시그니처가 내부 구현을 노출한다.

| 메서드 | 노출하는 내부 정보 |
|---|---|
| `isDiscountable(DayOfWeek, LocalTime)` | 내부에 `DayOfWeek` 타입의 요일과 `LocalTime` 타입의 시간 정보가 존재 |
| `isDiscountable(int)` | 내부에 `int` 타입의 순번 정보가 존재 |
| `getType()` | 내부에 `DiscountConditionType`이 존재 |

DiscountCondition의 속성을 변경하면, 두 `isDiscountable` 메서드의 파라미터를 수정하고 해당 메서드를 사용하는 **모든 클라이언트도 함께 수정**해야 한다. 내부 구현의 변경이 외부로 퍼져나가는 파급 효과(*Ripple Effect*)는 캡슐화가 부족하다는 명백한 증거다.

Movie 역시 캡슐화가 부족하다. 파라미터나 반환 값으로 내부 속성을 직접 노출하지 않지만, **할인 정책의 종류**를 노출한다.

| 메서드 | 노출하는 내부 정보 |
|---|---|
| `calculateAmountDiscountedFee()` | 금액 할인 정책이 존재 |
| `calculatePercentDiscountedFee()` | 비율 할인 정책이 존재 |
| `calculateNoneDiscountedFee()` | 할인 미적용 정책이 존재 |

세 개의 메서드는 할인 정책에 금액 할인, 비율 할인, 미적용의 세 가지가 존재한다는 사실을 만천하에 드러내고 있다. 새로운 할인 정책이 추가되거나 제거되면 이 메서드들에 의존하는 모든 클라이언트가 영향을 받는다.

#### 캡슐화의 진정한 의미

> **핵심 통찰**: 캡슐화는 단순히 객체 내부의 데이터를 외부로부터 감추는 것 이상의 의미를 가진다. 캡슐화는 **변경될 수 있는 어떤 것이라도 감추는 것**을 의미한다. 내부 속성을 외부로부터 감추는 것은 '데이터 캡슐화'라고 불리는 캡슐화의 한 종류일 뿐이다. 속성의 타입이건, 할인 정책의 종류건 상관없이 내부 구현의 변경으로 인해 외부 객체가 영향을 받는다면 캡슐화를 위반한 것이다. 설계에서 **변하는 것이 무엇인지 고려하고 변하는 개념을 캡슐화**해야 한다 [GOF94].

### 5.2 높은 결합도

캡슐화 위반으로 인해 DiscountCondition의 내부 구현이 외부로 노출됐기 때문에 Movie와 DiscountCondition 사이의 결합도는 높을 수밖에 없다. DiscountCondition에 대한 어떤 변경이 Movie에 영향을 미치는지 살펴보자:

- DiscountCondition의 기간 할인 조건 명칭이 `PERIOD`에서 다른 값으로 변경되면 → **Movie를 수정해야 한다**
- DiscountCondition의 종류가 추가되거나 삭제되면 → **Movie의 if~else 구문을 수정해야 한다**
- 각 DiscountCondition의 만족 여부를 판단하는 데 필요한 정보가 변경되면 → **Movie의 isDiscountable 메서드 파라미터를 변경해야 하고**, 이는 Screening에 대한 변경까지 초래한다

이 요소들이 DiscountCondition의 **구현**에 속한다는 점에 주목하라. 인터페이스가 아니라 **구현을 변경**하는 경우에도 의존하는 Movie를 변경해야 한다는 것은 두 객체 사이의 결합도가 높다는 것을 의미한다.

### 5.3 낮은 응집도

DiscountCondition이 할인 여부를 판단하는 데 필요한 정보가 변경되면:
1. Movie의 `isDiscountable` 메서드 파라미터를 변경해야 한다
2. Screening에서 Movie의 `isDiscountable` 메서드를 호출하는 부분도 함께 변경해야 한다

결과적으로 할인 조건의 종류를 변경하기 위해 DiscountCondition, Movie, Screening을 **함께 수정**해야 한다. 하나의 변경을 수용하기 위해 코드의 여러 곳을 동시에 변경해야 한다는 것은 설계의 응집도가 낮다는 증거다.

응집도가 낮은 이유는 캡슐화를 위반했기 때문이다. DiscountCondition과 Movie의 내부 구현이 인터페이스에 그대로 노출되고 있고, Screening은 노출된 구현에 직접적으로 의존하고 있다. 원래 DiscountCondition이나 Movie에 위치해야 하는 로직이 Screening으로 새어 나왔기 때문이다.

---

## 6. 데이터 중심 설계의 근본적 실패 원인

두 번째 설계가 변경에 유연하지 못한 이유는 캡슐화를 위반했기 때문이다. 데이터 중심의 설계가 변경에 취약한 근본적인 이유는 **두 가지**다.

### 6.1 너무 이른 시기에 데이터에 관해 결정하도록 강요한다

데이터 중심 설계를 시작할 때 던지는 첫 번째 질문은 "이 객체가 포함해야 하는 **데이터가 무엇인가?**"다. 데이터는 구현의 일부라는 사실을 명심하라. 데이터 주도 설계는 설계를 시작하는 처음부터 데이터에 관해 결정하도록 강요하기 때문에 너무 이른 시기에 내부 구현에 초점을 맞추게 한다.

데이터 중심 설계에 익숙한 개발자들은 일반적으로 데이터와 기능을 분리하는 절차적 프로그래밍 방식을 따른다. 이것은 상태와 행동을 하나의 단위로 캡슐화하는 객체지향 패러다임에 반하는 것이다. 접근자와 수정자를 과도하게 추가하게 되고, 이 데이터 객체를 사용하는 절차를 별도의 객체에 구현하게 된다. 접근자와 수정자는 `public` 속성과 큰 차이가 없기 때문에 캡슐화는 완전히 무너진다. 이것이 **첫 번째 설계가 실패한 이유**다.

### 6.2 협력이라는 문맥을 고려하지 않고 객체를 고립시켜 오퍼레이션을 결정한다

비록 데이터를 처리하는 작업과 데이터를 같은 객체 안에 두더라도, 데이터에 초점이 맞춰져 있다면 만족스러운 캡슐화를 얻기 어렵다. 데이터를 먼저 결정하고 데이터를 처리하는 데 필요한 오퍼레이션을 나중에 결정하는 방식은, 데이터에 관한 지식이 객체의 인터페이스에 고스란히 드러나게 된다. 결과적으로 객체의 인터페이스는 구현을 캡슐화하는 데 실패하고 코드는 변경에 취약해진다. 이것이 **두 번째 설계가 실패한 이유**다.

> **핵심 통찰**: 결론적으로 데이터 중심의 설계는 너무 이른 시기에 데이터에 대해 고민하기 때문에 캡슐화에 실패하게 된다. 객체의 내부 구현이 인터페이스를 어지럽히고 응집도와 결합도에 나쁜 영향을 미치기 때문에 변경에 취약한 코드를 낳게 된다.

---

## 리팩터링 과정

| 단계 | 설계 | ReservationAgency의 역할 | 캡슐화 | 결합도 | 응집도 |
|---|---|---|---|---|---|
| **1단계** (데이터 + getter/setter) | 데이터 클래스 + 외부 제어 객체 | 할인 조건 판단 + 할인 요금 계산 + 예매 생성 **모두 담당** | ❌ getter/setter가 내부 상태 노출 | 🔴 ReservationAgency가 모든 객체에 의존 | 🔴 5가지 이유로 변경됨 |
| **2단계** (데이터에 오퍼레이션 추가) | 각 객체가 자신의 데이터를 처리 | 예매 생성만 담당 | △ 메서드 시그니처가 내부 구현 노출 | 🟡 의존성 분산되었으나 여전히 구현에 결합 | 🟡 여전히 여러 클래스 동시 수정 필요 |
| **이상적** (2장의 책임 중심 설계) | 다형성 + 협력 기반 | 예매 생성만 담당 | ✅ 인터페이스 뒤로 구현 캡슐화 | 🟢 인터페이스에만 의존 | 🟢 변경이 한 곳에 집중 |

---

## 설계 원칙

| 원칙 | 설명 | 데이터 중심 설계의 위반 |
|---|---|---|
| **캡슐화** | 변경 가능성이 높은 부분을 내부에 숨기고, 안정적인 인터페이스만 공개한다 | getter/setter가 내부 상태를 그대로 노출 |
| **높은 응집도** | 하나의 변경 이유로 모듈이 변경되어야 한다 (SRP) | ReservationAgency가 5가지 이유로 변경됨 |
| **낮은 결합도** | 구현이 아닌 인터페이스에 의존한다 | 제어 객체가 모든 데이터 객체의 구현에 의존 |
| **자율적인 객체** | 객체가 자신의 상태를 스스로 책임진다 | 외부 객체가 getter로 데이터를 꺼내 처리 |
| **협력 기반 설계** | 객체가 사용될 문맥(협력)을 고려하여 책임을 할당한다 | 협력을 고려하지 않고 데이터부터 결정 |

---

## 요약

- 객체지향 설계에서 시스템을 분할하는 두 가지 방법은 **데이터 중심**과 **책임 중심**이며, 훌륭한 설계는 책임에 초점을 맞춘다.
- **캡슐화**는 설계의 제1원리다. 변경될 수 있는 어떤 것이라도 감춰야 한다. 데이터뿐 아니라 할인 정책의 종류처럼 **타입 정보**도 캡슐화 대상이다.
- **응집도**와 **결합도**는 변경의 관점에서 평가해야 한다. 하나의 변경을 위해 여러 모듈을 수정해야 한다면 응집도가 낮고 결합도가 높은 것이다.
- getter/setter를 추가하는 것은 캡슐화가 아니다. 속성의 가시성을 `private`으로 설정해도 접근자/수정자를 통해 외부에 노출하면 `public`과 다를 바 없다.
- **추측에 의한 설계 전략**(Design-by-Guessing Strategy)은 협력을 고려하지 않고 막연한 추측으로 접근자/수정자를 추가하는 것이다. 이는 캡슐화를 파괴한다.
- 데이터 중심 설계의 근본적 실패 원인은 두 가지다: (1) 너무 이른 시기에 데이터에 관해 결정하도록 강요한다 (2) 협력이라는 문맥을 고려하지 않고 객체를 고립시켜 오퍼레이션을 결정한다.
- **단일 책임 원칙**(SRP)에서 '책임'은 '변경의 이유'를 의미한다. 클래스는 단 한 가지의 변경 이유만 가져야 한다.
- 객체를 설계할 때는 "어떤 데이터가 필요한가?"가 아니라 "어떤 책임이 필요한가?"를 먼저 물어야 한다.

---

## 다른 챕터와의 관계

- **2장 (객체지향 프로그래밍)**: 2장에서 구현한 책임 중심 설계가 이번 장의 데이터 중심 설계와 대비되는 "좋은 설계"의 기준이 된다. 두 설계는 기능적으로 동일하지만 캡슐화, 응집도, 결합도에서 극적인 차이를 보인다.
- **3장 (역할, 책임, 협력)**: 이번 장에서 데이터 중심 설계가 실패하는 이유가 곧 3장에서 강조한 "협력이라는 문맥 속에서 책임을 할당하라"는 원칙을 어겼기 때문이다.
- **5장 (책임 할당하기)**: 이번 장에서 제기된 문제를 해결하는 구체적인 방법론(GRASP 패턴)을 5장에서 다룬다. 데이터가 아닌 책임을 기반으로 설계하는 체계적인 원칙을 배운다.
- **8장 (의존성 관리하기)**: 이번 장에서 언급한 결합도 문제를 더 깊이 다루며, 의존성을 관리하는 구체적인 기법을 소개한다.
