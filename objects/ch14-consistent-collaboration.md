# Chapter 14: Consistent Collaboration (일관성 있는 협력)

## 핵심 질문

유사한 기능을 구현하는 코드가 서로 다른 패턴을 따르면 어떤 문제가 발생하는가? 설계에 일관성을 부여하려면 변하는 것과 변하지 않는 것을 어떻게 분리하고 캡슐화해야 하는가?

---

## 1. 핸드폰 과금 시스템 변경하기

### 1.1 기본 정책 확장

11장에서 구현한 핸드폰 과금 시스템의 요금 정책을 수정해야 한다고 가정하자. 기존에는 일반 요금제와 심야 할인 요금제 두 가지가 있었다. 이번 장에서는 기본 정책을 4가지 방식으로 확장한다. 부가 정책에 대한 요구사항은 변화가 없다.

| 유형 | 형식 | 예 |
|---|---|---|
| **고정요금 방식** | A초당 B원 | 10초당 18원 |
| **시간대별 방식** | A시부터 B시까지 C초당 D원 | 00시~19시 10초당 18원, 19시~24시 10초당 15원 |
| **요일별 방식** | 평일에는 A초당 B원, 공휴일에는 A초당 C원 | 평일 10초당 38원, 공휴일 10초당 19원 |
| **구간별 방식** | 초기 A분 동안 B초당 C원, A분 초과 시 B초당 D원 | 초기 1분 10초당 50원, 1분 이후 10초당 20원 |

각 기본 정책을 간단히 살펴보면:

- **고정요금 방식**: 일정 시간 단위로 동일한 요금을 부과한다. 기존의 '일반 요금제'와 동일하다.
- **시간대별 방식**: 하루 24시간을 특정 시간 구간으로 나눈 후 각 구간별로 서로 다른 요금을 부과한다. 기존의 '심야 할인 요금제'는 밤 10시를 기준으로 요금을 부과한 시간대별 방식이다.
- **요일별 방식**: 요일별로 요금을 차등 부과한다.
- **구간별 방식**: 전체 통화 시간을 일정한 구간에 따라 나누고 각 구간별로 요금을 차등 부과한다.

기본 정책과 부가 정책을 조합하면 다양한 요금제를 만들 수 있다:

```
기본 정책                    부가 정책
┌──────────────┐     ┌────────────────────────┐
│ 고정요금 방식  │     │ 세금 정책               │
│ 시간대별 방식  │ ──→ │ 기본 요금 할인 정책       │
│ 요일별 방식   │     │ 세금 정책 + 기본 요금 할인  │
│ 구간별 방식   │     │ (없음)                   │
└──────────────┘     └────────────────────────┘
```

이번 장에서 구현하게 될 클래스 구조는 다음과 같다. 짙은 색으로 표현된 클래스들이 새로운 기본 정책을 구현한 클래스들이다.

```
                    Phone
                      │ ratePolicy
                      ▼
                «interface»
                 RatePolicy
               calculateFee(phone)
                 ▲          ▲
                 │          │ next
    BasicRatePolicy    AdditionalRatePolicy
   +calculateFee()    +calculateFee()
   #calculateCallFee()  #afterCalculated()
         ▲                    ▲
    ┌────┼──────┬──────┐    ┌──┴──────────┐
    │    │      │      │    │             │
FixedFee Time  DayOf  Duration  RateDiscount  Taxable
Policy   OfDay  Week  Discount  ablePolicy    Policy
         Disc.  Disc.  Policy
         Policy Policy
```

### 1.2 고정요금 방식 구현하기

가장 간단한 고정요금 방식부터 시작하자. 고정요금 방식은 기존의 일반 요금제와 동일하기 때문에 기존의 `RegularPolicy` 클래스의 이름을 `FixedFeePolicy`로 수정하기만 하면 된다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class FixedFeePolicy extends BasicRatePolicy {
    private Money amount;
    private Duration seconds;

    public FixedFeePolicy(Money amount, Duration seconds) {
        this.amount = amount;
        this.seconds = seconds;
    }

    @Override
    protected Money calculateCallFee(Call call) {
        return amount.times(call.getDuration().getSeconds() / seconds.getSeconds());
    }
}
```

</details>

```typescript
// TypeScript
class FixedFeePolicy extends BasicRatePolicy {
    constructor(
        private amount: Money,
        private seconds: number // Duration in seconds
    ) {
        super();
    }

    protected calculateCallFee(call: Call): Money {
        return this.amount.times(
            Math.floor(call.getDuration() / this.seconds)
        );
    }
}
```

### 1.3 시간대별 방식 구현하기

시간대별 방식에 따라 요금을 계산하기 위해서는 통화 기간을 정해진 시간대별로 나눈 후 각 시간대별로 서로 다른 계산 규칙을 적용해야 한다. 예를 들어 0시부터 19시까지는 10초당 18원, 19시부터 24시까지는 10초당 15원을 부과하는 시간대별 방식이 있다면, 18시부터 20시까지 2시간 통화를 한 가입자의 경우 18시~19시는 10초당 18원, 19시~20시는 10초당 15원이 부과된다.

여기서 한 가지 고려해야 할 조건이 있다. **통화가 여러 날에 걸쳐 이뤄질 수 있다**는 점이다. 1월 1일 10시부터 1월 3일 15시까지 3일에 걸친 통화의 경우, 먼저 날짜별로 통화 시간을 분리한 후 각 날짜에 대해 시간대별 요금을 계산해야 한다.

```
통화: 1/1 10시 ─────────────────────────────── 1/3 15시

날짜별 분리:
  1/1: [10시 ──── 24시]    1/2: [0시 ──── 24시]    1/3: [0시 ── 15시]

시간대별 분리 (0~19시: 18원/10초, 19~24시: 15원/10초):
  1/1: [10시─19시] [19시─24시]
  1/2: [0시─19시]  [19시─24시]
  1/3: [0시─15시]
  → 총 5개 구간으로 분리 후 각 구간별 요금 계산
```

시간대별 방식을 구현하는 데 있어 핵심은 규칙에 따라 통화 시간을 분할하는 방법을 결정하는 것이다. 이를 위해 기간을 편하게 관리할 수 있는 `DateTimeInterval` 클래스를 추가한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class DateTimeInterval {
    private LocalDateTime from;
    private LocalDateTime to;

    public static DateTimeInterval of(LocalDateTime from, LocalDateTime to) {
        return new DateTimeInterval(from, to);
    }

    public static DateTimeInterval toMidnight(LocalDateTime from) {
        return new DateTimeInterval(
            from,
            LocalDateTime.of(from.toLocalDate(), LocalTime.of(23, 59, 59, 999_999_999)));
    }

    public static DateTimeInterval fromMidnight(LocalDateTime to) {
        return new DateTimeInterval(
            LocalDateTime.of(to.toLocalDate(), LocalTime.of(0, 0)),
            to);
    }

    public static DateTimeInterval during(LocalDate date) {
        return new DateTimeInterval(
            LocalDateTime.of(date, LocalTime.of(0, 0)),
            LocalDateTime.of(date, LocalTime.of(23, 59, 59, 999_999_999)));
    }

    private DateTimeInterval(LocalDateTime from, LocalDateTime to) {
        this.from = from;
        this.to = to;
    }

    public Duration duration() {
        return Duration.between(from, to);
    }

    public LocalDateTime getFrom() { return from; }
    public LocalDateTime getTo() { return to; }
}
```

</details>

```typescript
// TypeScript
class DateTimeInterval {
    private constructor(
        private from: Date,
        private to: Date
    ) {}

    static of(from: Date, to: Date): DateTimeInterval {
        return new DateTimeInterval(from, to);
    }

    static toMidnight(from: Date): DateTimeInterval {
        const midnight = new Date(from);
        midnight.setHours(23, 59, 59, 999);
        return new DateTimeInterval(from, midnight);
    }

    static fromMidnight(to: Date): DateTimeInterval {
        const midnight = new Date(to);
        midnight.setHours(0, 0, 0, 0);
        return new DateTimeInterval(midnight, to);
    }

    static during(date: Date): DateTimeInterval {
        const start = new Date(date);
        start.setHours(0, 0, 0, 0);
        const end = new Date(date);
        end.setHours(23, 59, 59, 999);
        return new DateTimeInterval(start, end);
    }

    duration(): number {
        return (this.to.getTime() - this.from.getTime()) / 1000;
    }

    getFrom(): Date { return this.from; }
    getTo(): Date { return this.to; }
}
```

기존의 `Call` 클래스는 통화 기간을 저장하기 위해 `from`과 `to`라는 두 개의 인스턴스 변수를 포함하고 있었다. 이제 `DateTimeInterval` 타입을 사용할 수 있으므로 하나의 인스턴스 변수로 묶을 수 있다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Call {
    private DateTimeInterval interval;

    public Call(LocalDateTime from, LocalDateTime to) {
        this.interval = DateTimeInterval.of(from, to);
    }

    public Duration getDuration() { return interval.duration(); }
    public LocalDateTime getFrom() { return interval.getFrom(); }
    public LocalDateTime getTo() { return interval.getTo(); }
    public DateTimeInterval getInterval() { return interval; }

    public List<DateTimeInterval> splitByDay() {
        return interval.splitByDay();
    }
}
```

</details>

```typescript
// TypeScript
class Call {
    private interval: DateTimeInterval;

    constructor(from: Date, to: Date) {
        this.interval = DateTimeInterval.of(from, to);
    }

    getDuration(): number { return this.interval.duration(); }
    getFrom(): Date { return this.interval.getFrom(); }
    getTo(): Date { return this.interval.getTo(); }
    getInterval(): DateTimeInterval { return this.interval; }

    splitByDay(): DateTimeInterval[] {
        return this.interval.splitByDay();
    }
}
```

전체 통화 시간을 분할하는 작업은 두 개의 단계로 나뉜다:

1. 통화 기간을 **일자별**로 분리한다.
2. 일자별로 분리된 기간을 다시 **시간대별 규칙**에 따라 분리한 후 각 기간에 대해 요금을 계산한다.

두 작업을 객체의 책임으로 할당해 보자. 책임을 할당하는 기본 원칙은 **정보 전문가에게 할당하는 것**이다.

- **통화 기간을 일자 단위로 나누는 작업**: 통화 기간에 대한 정보를 가장 잘 알고 있는 객체는 `Call`이다. 하지만 `Call`은 기간 자체를 처리하는 방법에 대해서는 전문가가 아니다. 기간을 처리하는 전문가는 `DateTimeInterval`이다. 따라서 `Call`이 `DateTimeInterval`에게 분할을 요청하도록 협력을 설계한다.
- **시간대별로 분할하는 작업**: 시간대별 기준을 잘 알고 있는 요금 정책이며, `TimeOfDayDiscountPolicy` 클래스가 담당한다.

```
협력 흐름:

  TimeOfDayDiscountPolicy ──1: splitByDay()──→ Call ──2: splitByDay()──→ DateTimeInterval
       │                        ◀── intervals ──┘         ◀── intervals ──┘
       │
       ├── 3: from(interval)  ← 시간대별 시작 시간 계산
       └── 4: to(interval)    ← 시간대별 종료 시간 계산
```

`DateTimeInterval`의 `splitByDay` 메서드는 통화 기간을 일자별로 분할해서 반환한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class DateTimeInterval {
    public List<DateTimeInterval> splitByDay() {
        if (days() > 0) {
            return splitByDay(days());
        }
        return Arrays.asList(this);
    }

    private long days() {
        return Duration.between(
            from.toLocalDate().atStartOfDay(),
            to.toLocalDate().atStartOfDay()
        ).toDays();
    }

    private List<DateTimeInterval> splitByDay(long days) {
        List<DateTimeInterval> result = new ArrayList<>();
        addFirstDay(result);
        addMiddleDays(result, days);
        addLastDay(result);
        return result;
    }

    private void addFirstDay(List<DateTimeInterval> result) {
        result.add(DateTimeInterval.toMidnight(from));
    }

    private void addMiddleDays(List<DateTimeInterval> result, long days) {
        for (int loop = 1; loop < days; loop++) {
            result.add(DateTimeInterval.during(from.toLocalDate().plusDays(loop)));
        }
    }

    private void addLastDay(List<DateTimeInterval> result) {
        result.add(DateTimeInterval.fromMidnight(to));
    }
}
```

</details>

```typescript
// TypeScript
class DateTimeInterval {
    splitByDay(): DateTimeInterval[] {
        const daysDiff = this.days();
        if (daysDiff > 0) {
            return this.splitByDays(daysDiff);
        }
        return [this];
    }

    private days(): number {
        const fromStart = new Date(this.from);
        fromStart.setHours(0, 0, 0, 0);
        const toStart = new Date(this.to);
        toStart.setHours(0, 0, 0, 0);
        return Math.floor(
            (toStart.getTime() - fromStart.getTime()) / (1000 * 60 * 60 * 24)
        );
    }

    private splitByDays(days: number): DateTimeInterval[] {
        const result: DateTimeInterval[] = [];
        result.push(DateTimeInterval.toMidnight(this.from));
        for (let i = 1; i < days; i++) {
            const date = new Date(this.from);
            date.setDate(date.getDate() + i);
            result.push(DateTimeInterval.during(date));
        }
        result.push(DateTimeInterval.fromMidnight(this.to));
        return result;
    }
}
```

이제 `TimeOfDayDiscountPolicy` 클래스를 구현해 보자. 이 클래스에서 가장 중요한 것은 시간에 따라 서로 다른 요금 규칙을 정의하는 방법이다. 하나의 통화 시간대를 구성하는 데는 **시작 시간, 종료 시간, 단위 시간, 단위 요금**이 필요하다.

시간대별 방식을 담당한 개발자는 이 문제를 4개의 서로 다른 `List`를 가지는 것으로 해결했다. 같은 규칙에 포함된 요소들은 `List` 안에서 **동일한 인덱스**에 위치한다.

```
  인덱스     0          1
starts   [00:00]     [19:00]
ends     [19:00]     [24:00]
durations [10초]      [10초]
amounts   [18원]      [15원]
```

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class TimeOfDayDiscountPolicy extends BasicRatePolicy {
    private List<LocalTime> starts = new ArrayList<>();
    private List<LocalTime> ends = new ArrayList<>();
    private List<Duration> durations = new ArrayList<>();
    private List<Money> amounts = new ArrayList<>();

    @Override
    protected Money calculateCallFee(Call call) {
        Money result = Money.ZERO;
        for (DateTimeInterval interval : call.splitByDay()) {
            for (int loop = 0; loop < starts.size(); loop++) {
                result = result.plus(
                    amounts.get(loop).times(
                        Duration.between(
                            from(interval, starts.get(loop)),
                            to(interval, ends.get(loop))
                        ).getSeconds() / durations.get(loop).getSeconds()
                    )
                );
            }
        }
        return result;
    }

    private LocalTime from(DateTimeInterval interval, LocalTime from) {
        return interval.getFrom().toLocalTime().isBefore(from)
            ? from : interval.getFrom().toLocalTime();
    }

    private LocalTime to(DateTimeInterval interval, LocalTime to) {
        return interval.getTo().toLocalTime().isAfter(to)
            ? to : interval.getTo().toLocalTime();
    }
}
```

</details>

```typescript
// TypeScript
class TimeOfDayDiscountPolicy extends BasicRatePolicy {
    private starts: number[];    // 시작 시간 (시 단위)
    private ends: number[];      // 종료 시간 (시 단위)
    private durations: number[]; // 단위 시간 (초)
    private amounts: Money[];    // 단위 요금

    constructor(
        starts: number[], ends: number[],
        durations: number[], amounts: Money[]
    ) {
        super();
        this.starts = starts;
        this.ends = ends;
        this.durations = durations;
        this.amounts = amounts;
    }

    protected calculateCallFee(call: Call): Money {
        let result = Money.ZERO;
        for (const interval of call.splitByDay()) {
            for (let i = 0; i < this.starts.length; i++) {
                const fromTime = this.from(interval, this.starts[i]);
                const toTime = this.to(interval, this.ends[i]);
                const seconds = (toTime - fromTime) * 3600;
                result = result.plus(
                    this.amounts[i].times(
                        Math.floor(seconds / this.durations[i])
                    )
                );
            }
        }
        return result;
    }

    private from(interval: DateTimeInterval, from: number): number {
        const intervalHour = interval.getFrom().getHours();
        return intervalHour < from ? from : intervalHour;
    }

    private to(interval: DateTimeInterval, to: number): number {
        const intervalHour = interval.getTo().getHours();
        return intervalHour > to ? to : intervalHour;
    }
}
```

### 1.4 요일별 방식 구현하기

요일별 방식은 요일별로 요금 규칙을 다르게 설정할 수 있다. 각 규칙은 **요일의 목록, 단위 시간, 단위 요금**이라는 세 가지 요소로 구성된다.

시간대별 방식을 개발한 프로그래머는 4개의 `List`를 이용해 규칙을 정의했지만, 요일별 방식을 개발하는 프로그래머는 규칙을 `DayOfWeekDiscountRule`이라는 **하나의 클래스**로 구현하는 것이 더 나은 설계라고 판단했다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class DayOfWeekDiscountRule {
    private List<DayOfWeek> dayOfWeeks = new ArrayList<>();
    private Duration duration = Duration.ZERO;
    private Money amount = Money.ZERO;

    public DayOfWeekDiscountRule(List<DayOfWeek> dayOfWeeks,
                                  Duration duration, Money amount) {
        this.dayOfWeeks = dayOfWeeks;
        this.duration = duration;
        this.amount = amount;
    }

    public Money calculate(DateTimeInterval interval) {
        if (dayOfWeeks.contains(interval.getFrom().getDayOfWeek())) {
            return amount.times(
                interval.duration().getSeconds() / duration.getSeconds()
            );
        }
        return Money.ZERO;
    }
}
```

</details>

```typescript
// TypeScript
class DayOfWeekDiscountRule {
    constructor(
        private dayOfWeeks: number[], // 0=Sunday, 1=Monday, ...
        private duration: number,     // 단위 시간 (초)
        private amount: Money         // 단위 요금
    ) {}

    calculate(interval: DateTimeInterval): Money {
        if (this.dayOfWeeks.includes(interval.getFrom().getDay())) {
            return this.amount.times(
                Math.floor(interval.duration() / this.duration)
            );
        }
        return Money.ZERO;
    }
}
```

요일별 방식 역시 통화 기간이 여러 날에 걸쳐 있을 수 있다. 따라서 시간대별 방식과 동일하게 통화 기간을 날짜 경계로 분리하고 분리된 각 통화 기간을 요일별로 설정된 요금 정책에 따라 적절하게 계산해야 한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class DayOfWeekDiscountPolicy extends BasicRatePolicy {
    private List<DayOfWeekDiscountRule> rules = new ArrayList<>();

    public DayOfWeekDiscountPolicy(List<DayOfWeekDiscountRule> rules) {
        this.rules = rules;
    }

    @Override
    protected Money calculateCallFee(Call call) {
        Money result = Money.ZERO;
        for (DateTimeInterval interval : call.getInterval().splitByDay()) {
            for (DayOfWeekDiscountRule rule : rules) {
                result = result.plus(rule.calculate(interval));
            }
        }
        return result;
    }
}
```

</details>

```typescript
// TypeScript
class DayOfWeekDiscountPolicy extends BasicRatePolicy {
    constructor(private rules: DayOfWeekDiscountRule[]) {
        super();
    }

    protected calculateCallFee(call: Call): Money {
        let result = Money.ZERO;
        for (const interval of call.getInterval().splitByDay()) {
            for (const rule of this.rules) {
                result = result.plus(rule.calculate(interval));
            }
        }
        return result;
    }
}
```

### 1.5 비일관성의 문제

잠시 숨을 고르고 지금까지 작업한 고정요금 방식, 시간대별 방식, 요일별 방식의 구현 클래스를 살펴보자. `FixedFeePolicy`, `TimeOfDayDiscountPolicy`, `DayOfWeekDiscountPolicy`의 세 클래스는 통화 요금을 정확하게 계산하고, 응집도와 결합도 측면에서도 특별히 문제는 없어 보인다. 클래스들을 따로 떨어뜨려 놓고 살펴보면 그럭저럭 괜찮은 구현으로 보이기까지 한다.

**하지만 이 클래스들을 함께 모아 놓고 보면 그동안 보이지 않던 문제점이 보이기 시작한다.**

현재 구현의 가장 큰 문제점은 이 클래스들이 유사한 문제를 해결하고 있음에도 불구하고 **설계에 일관성이 없다**는 것이다. 세 클래스는 기본 정책을 구현한다는 공통의 목적을 공유하지만, 정책을 구현하는 방식은 완전히 다르다.

| 정책 | 규칙 구성 방식 |
|---|---|
| `FixedFeePolicy` | 오직 하나의 규칙, `amount`와 `seconds` 인스턴스 변수 사용 |
| `TimeOfDayDiscountPolicy` | 4개의 `List`로 규칙 관리 (starts, ends, durations, amounts) |
| `DayOfWeekDiscountPolicy` | `DayOfWeekDiscountRule`이라는 별도 객체로 규칙 관리 |

> **핵심 통찰**: 비일관성은 두 가지 상황에서 발목을 잡는다. 하나는 **새로운 구현을 추가해야 하는 상황**이고, 다른 하나는 **기존의 구현을 이해해야 하는 상황**이다. 이 장애물이 문제인 이유는 개발자로서 우리가 수행하는 대부분의 활동이 코드를 추가하고 이해하는 일과 깊숙히 연관돼 있기 때문이다.

**새로운 구현 추가의 어려움**: 구간별 방식을 추가해야 하는 개발자 입장에서, `TimeOfDayDiscountPolicy`처럼 다수의 `List`를 유지할 것인가? `DayOfWeekDiscountPolicy`처럼 독립적인 객체를 추가할 것인가? `FixedFeePolicy`처럼 전혀 다른 새로운 방법을 고안할 것인가? 어떤 방식을 선택하더라도 구간별 방식을 구현하는 데는 문제가 없지만, 전체적인 일관성이라는 측면에서 보면 어떤 방식을 따르더라도 문제가 더 커지게 된다. 새로운 기본 정책을 추가하면 추가할수록 코드 사이의 일관성은 점점 더 어긋나게 된다.

**코드 이해의 어려움**: 요일별 방식의 구현을 이해하면 시간대별 방식을 이해하는 게 쉬울까? 그렇지 않다. 대부분의 사람들은 유사한 요구사항을 구현하는 코드는 유사한 방식으로 구현될 것이라고 예상한다. 하지만 유사한 요구사항이 서로 다른 방식으로 구현돼 있다면 요구사항이 유사하다는 사실 자체도 의심하게 된다. 유사한 요구사항을 구현하는 서로 다른 구조의 코드는 코드를 이해하는 데 **심리적인 장벽**을 만든다.

### 1.6 구간별 방식 구현하기 (비일관성 문제의 심화)

구간별 방식을 구현하는 개발자는 기존 방법과는 전혀 다른 새로운 방법을 선택했다. 이 개발자는 요일별 방식처럼 규칙을 정의하는 새로운 클래스를 추가하되, 코드를 재사용하기 위해 `FixedFeePolicy` 클래스를 상속받기로 결정했다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class DurationDiscountRule extends FixedFeePolicy {
    private Duration from;
    private Duration to;

    public DurationDiscountRule(Duration from, Duration to,
                                 Money amount, Duration seconds) {
        super(amount, seconds);
        this.from = from;
        this.to = to;
    }

    public Money calculate(Call call) {
        if (call.getDuration().compareTo(to) > 0) {
            return Money.ZERO;
        }
        if (call.getDuration().compareTo(from) < 0) {
            return Money.ZERO;
        }
        // 부모 클래스의 calculateFee(phone)은 Phone을 파라미터로 받는다.
        // calculateFee(phone)을 재사용하기 위해
        // 데이터를 전달할 용도로 임시 Phone을 만든다.
        Phone phone = new Phone(null);
        phone.call(new Call(
            call.getFrom().plus(from),
            call.getDuration().compareTo(to) > 0
                ? call.getFrom().plus(to)
                : call.getTo()));
        return super.calculateFee(phone);
    }
}
```

</details>

```typescript
// TypeScript
class DurationDiscountRule extends FixedFeePolicy {
    private from: number; // Duration in seconds
    private to: number;   // Duration in seconds

    constructor(from: number, to: number, amount: Money, seconds: number) {
        super(amount, seconds);
        this.from = from;
        this.to = to;
    }

    calculate(call: Call): Money {
        if (call.getDuration() > this.to) return Money.ZERO;
        if (call.getDuration() < this.from) return Money.ZERO;

        // 부모 클래스의 calculateFee를 재사용하기 위해 임시 Phone을 만든다
        const phone = new Phone(null);
        const adjustedFrom = new Date(
            call.getFrom().getTime() + this.from * 1000
        );
        const adjustedTo = call.getDuration() > this.to
            ? new Date(call.getFrom().getTime() + this.to * 1000)
            : call.getTo();
        phone.call(new Call(adjustedFrom, adjustedTo));
        return super.calculateFee(phone);
    }
}
```

이제 여러 개의 `DurationDiscountRule`을 이용해 `DurationDiscountPolicy`를 구현할 수 있다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class DurationDiscountPolicy extends BasicRatePolicy {
    private List<DurationDiscountRule> rules = new ArrayList<>();

    public DurationDiscountPolicy(List<DurationDiscountRule> rules) {
        this.rules = rules;
    }

    @Override
    protected Money calculateCallFee(Call call) {
        Money result = Money.ZERO;
        for (DurationDiscountRule rule : rules) {
            result = result.plus(rule.calculate(call));
        }
        return result;
    }
}
```

</details>

```typescript
// TypeScript
class DurationDiscountPolicy extends BasicRatePolicy {
    constructor(private rules: DurationDiscountRule[]) {
        super();
    }

    protected calculateCallFee(call: Call): Money {
        let result = Money.ZERO;
        for (const rule of this.rules) {
            result = result.plus(rule.calculate(call));
        }
        return result;
    }
}
```

`DurationDiscountPolicy` 클래스는 할인 요금을 정상적으로 계산하고, 각 클래스는 하나의 책임만을 수행한다. 하지만 이 설계를 훌륭하다고 말하기는 어려운데, 기본 정책을 구현하는 기존 클래스들과 일관성이 없기 때문이다.

> 코드 재사용을 위한 상속은 해롭다. `DurationDiscountRule`이 `FixedFeePolicy`를 상속받는 이유는 `FixedFeePolicy`의 인스턴스 변수(`amount`, `seconds`)와 `calculateFee` 메서드를 재사용하기 위해서다. 즉 코드 재사용을 위해 상속을 사용한 것이다. 부모 클래스인 `FixedFeePolicy`는 상속을 위해 설계된 클래스가 아니며, `DurationDiscountRule`은 `FixedFeePolicy`의 서브타입이 아니다. 이 코드는 이해하기도 어렵다. `calculateFee`를 재사용하기 위해 `DurationDiscountRule`의 `calculate` 메서드 안에서 `Phone`과 `Call`의 인스턴스를 생성하는 것이 부자연스러워 보인다. 이것은 상속을 위해 설계되지 않은 `FixedFeePolicy`를 재사용하기 위해 억지로 코드를 비튼 결과다.

**결론은 유사한 기능을 서로 다른 방식으로 구현해서는 안 된다는 것이다.** 유사한 기능은 유사한 방식으로 구현해야 한다. 객체지향에서 기능을 구현하는 유일한 방법은 객체 사이의 협력을 만드는 것뿐이므로, 유지보수 가능한 시스템을 구축하는 첫걸음은 **협력을 일관성 있게 만드는 것**이다.

---

## 2. 설계에 일관성 부여하기

일관성 있는 설계를 만드는 데 가장 훌륭한 조언은 **다양한 설계 경험을 익히라**는 것이다. 풍부한 설계 경험을 가진 사람은 어떤 변경이 중요한지, 그리고 그 변경을 어떻게 다뤄야 하는지에 대한 통찰력을 가지게 된다. 하지만 이런 설계 경험을 단기간에 쌓아올리는 것은 쉽지 않다.

일관성 있는 설계를 위한 두 번째 조언은 **널리 알려진 디자인 패턴을 학습하고 변경이라는 문맥 안에서 디자인 패턴을 적용해 보라**는 것이다. 디자인 패턴은 특정한 변경에 대해 일관성 있는 설계를 만들 수 있는 경험 법칙을 모아 놓은 일종의 설계 템플릿이다.

비록 디자인 패턴이 반복적으로 적용할 수 있는 설계 구조를 제공한다고 하더라도 모든 경우에 적합한 패턴을 찾을 수 있는 것은 아니다. 따라서 협력을 일관성 있게 만들기 위해 다음과 같은 **기본 지침**을 따르는 것이 도움이 된다.

1. **변하는 개념을 변하지 않는 개념으로부터 분리하라.**
2. **변하는 개념을 캡슐화하라.**

> 애플리케이션에서 달라지는 부분을 찾아내고, 달라지지 않는 부분으로부터 분리시킨다. 이것은 여러 설계 원칙 중에서 첫 번째 원칙이다. 즉, 코드에서 새로운 요구사항이 있을 때마다 바뀌는 부분이 있다면 그 행동을 바뀌지 않는 다른 부분으로부터 골라내서 분리해야 한다는 것을 알 수 있다. 이 원칙은 다음과 같은 식으로 생각할 수도 있다. "바뀌는 부분을 따로 뽑아서 캡슐화한다. 그렇게 하면 나중에 바뀌지 않는 부분에는 영향을 미치지 않은 채로 그 부분만 고치거나 확장할 수 있다"[Freeman04].

### 2.1 조건 로직 대 객체 탐색

다음은 4장에서 절차적인 방식으로 구현했던 `ReservationAgency`의 기본 구조다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class ReservationAgency {
    public Reservation reserve(Screening screening, Customer customer,
                                int audienceCount) {
        for (DiscountCondition condition : movie.getDiscountConditions()) {
            if (condition.getType() == DiscountConditionType.PERIOD) {
                // 기간 조건인 경우
            } else {
                // 회차 조건인 경우
            }
        }

        if (discountable) {
            switch (movie.getMovieType()) {
                case AMOUNT_DISCOUNT:
                    // 금액 할인 정책인 경우
                case PERCENT_DISCOUNT:
                    // 비율 할인 정책인 경우
                case NONE_DISCOUNT:
                    // 할인 정책이 없는 경우
            }
        } else {
            // 할인 적용이 불가능한 경우
        }
    }
}
```

</details>

```typescript
// TypeScript
class ReservationAgency {
    reserve(screening: Screening, customer: Customer,
            audienceCount: number): Reservation {
        for (const condition of movie.getDiscountConditions()) {
            if (condition.getType() === DiscountConditionType.PERIOD) {
                // 기간 조건인 경우
            } else {
                // 회차 조건인 경우
            }
        }

        if (discountable) {
            switch (movie.getMovieType()) {
                case MovieType.AMOUNT_DISCOUNT:
                    // 금액 할인 정책인 경우
                case MovieType.PERCENT_DISCOUNT:
                    // 비율 할인 정책인 경우
                case MovieType.NONE_DISCOUNT:
                    // 할인 정책이 없는 경우
            }
        } else {
            // 할인 적용이 불가능한 경우
        }
    }
}
```

위 코드에는 두 개의 조건 로직이 존재한다. 하나는 **할인 조건의 종류**를 결정하는 부분이고, 다른 하나는 **할인 정책**을 결정하는 부분이다. 이 설계가 나쁜 이유는 **변경의 주기가 서로 다른 코드가 한 클래스 안에 뭉쳐 있기 때문**이다. 또한 새로운 할인 정책이나 할인 조건을 추가하기 위해서는 기존 코드의 내부를 수정해야 하기 때문에 오류가 발생할 확률이 높아진다.

절차지향 프로그램에서 변경을 처리하는 전통적인 방법은 **조건문의 분기를 추가하거나 개별 분기 로직을 수정**하는 것이다.

**객체지향은 조금 다른 접근 방법을 취한다.** 객체지향에서 변경을 다루는 전통적인 방법은 **조건 로직을 객체 사이의 이동으로 바꾸는 것**이다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Movie {
    private DiscountPolicy discountPolicy;

    public Money calculateMovieFee(Screening screening) {
        return fee.minus(discountPolicy.calculateDiscountAmount(screening));
    }
}
```

</details>

```typescript
// TypeScript
class Movie {
    private discountPolicy: DiscountPolicy;

    calculateMovieFee(screening: Screening): Money {
        return this.fee.minus(
            this.discountPolicy.calculateDiscountAmount(screening)
        );
    }
}
```

`Movie`는 현재의 할인 정책이 어떤 종류인지 확인하지 않는다. 단순히 현재의 할인 정책을 나타내는 `discountPolicy`에 필요한 메시지를 전송할 뿐이다. 할인 정책의 종류를 체크하던 조건문이 `discountPolicy`로의 **객체 이동**으로 대체된 것이다.

```
절차적 방식:
  ReservationAgency
  ├── if (PERIOD) → 기간 조건 로직
  ├── else → 회차 조건 로직
  ├── case AMOUNT → 금액 할인 로직
  └── case PERCENT → 비율 할인 로직

객체지향 방식:
  Movie ──calculateDiscountAmount──→ DiscountPolicy ──isSatisfiedBy──→ DiscountCondition
    │                                  ▲                                  ▲
    │ (조건 로직 = 객체 이동)           │ (서브타입 캡슐화)                   │
    │                           ┌──────┴──────┐                  ┌────────┴────────┐
    │                     AmountDiscount  PercentDiscount   SequenceCondition  PeriodCondition
    │                     Policy          Policy
    └── "어떤 정책인지 판단하지 않음. 단지 메시지를 전송할 뿐."
```

**다형성**(*Polymorphism*)은 바로 이런 조건 로직을 객체 사이의 이동으로 바꾸기 위해 객체지향이 제공하는 설계 기법이다. 객체지향적인 코드는 조건을 판단하지 않는다. 단지 다음 객체로 이동할 뿐이다.

### 2.2 클래스 분리의 기준

조건 로직을 객체 사이의 이동으로 대체하기 위해서는 커다란 클래스를 더 작은 클래스들로 분리해야 한다. **가장 중요한 기준은 변경의 이유와 주기**다. 클래스는 명확히 단 하나의 이유에 의해서만 변경돼야 하고, 클래스 안의 모든 코드는 함께 변경돼야 한다. 간단하게 말해서 **단일 책임 원칙**을 따르도록 클래스를 분리해야 한다는 것이다.

큰 메서드 안에 뭉쳐 있던 조건 로직들을 변경의 압력에 맞춰 작은 클래스들로 분리하고 나면, 인스턴스들 사이의 협력 패턴에 일관성을 부여하기가 더 쉬워진다. 유사한 행동을 수행하는 작은 클래스들이 자연스럽게 **역할**이라는 추상화로 묶이게 되고, 역할 사이에서 이뤄지는 협력 방식이 전체 설계의 일관성을 유지할 수 있게 이끌어 주기 때문이다.

따라서 일관성 있는 협력을 만들기 위한 지침 정리:

| 지침 | 내용 |
|---|---|
| **지침 1** | 변하는 개념을 변하지 않는 개념으로부터 분리하라 |
| **지침 2** | 변하는 개념을 캡슐화하라 |

> **핵심 통찰**: 핵심은 훌륭한 추상화를 찾아 추상화에 의존하도록 만드는 것이다. 추상화에 대한 의존은 결합도를 낮추고, 결과적으로 대체 가능한 역할로 구성된 협력을 설계할 수 있게 해준다. 따라서 **선택하는 추상화의 품질이 캡슐화의 품질을 결정**한다.

### 2.3 캡슐화 다시 살펴보기

많은 사람들은 캡슐화에 관한 이야기를 들으면 반사적으로 **데이터 은닉**(*Data Hiding*)을 떠올린다. 데이터 은닉이란 오직 외부에 공개된 메서드를 통해서만 객체의 내부에 접근할 수 있게 제한함으로써 객체 내부의 상태 구현을 숨기는 기법이다.

그러나 **캡슐화는 데이터 은닉 이상**이다. GOF가 저술한 《GoF의 디자인 패턴》[GOF94]에는 캡슐화와 관련해서 중요한 조언이 들어 있다.

> 설계에서 무엇이 변화될 수 있는지 고려하라. 이 접근법은 재설계의 원인에 초점을 맞추는 것과 반대되는 것이다. 설계에 변경을 강요하는 것이 무엇인지에 대해 고려하기보다는 재설계 없이 변경할 수 있는 것이 무엇인지 고려하라. 여기서의 초점은 많은 디자인 패턴의 주제인 변화하는 개념을 캡슐화하는 것이다[GOF94].

GOF의 조언에 따르면 캡슐화란 단순히 데이터를 감추는 것이 아니라, 소프트웨어 안에서 변할 수 있는 모든 **'개념'**을 감추는 것이다.

> 캡슐화란 변하는 어떤 것이든 감추는 것이다[Bain08, Shalloway01].

소프트웨어 안에서 변할 수 있는 것은 다양하다. 이를 네 가지 종류의 캡슐화로 분류할 수 있다.

| 캡슐화 종류 | 설명 | 기법 | 예시 |
|---|---|---|---|
| **데이터 캡슐화** | 클래스의 내부 데이터를 감춘다 | `private` 인스턴스 변수 + 메서드 접근 | `Movie`의 `title` 필드 |
| **메서드 캡슐화** | 클래스의 내부 행동을 감춘다 | `protected` 메서드 | `DiscountPolicy`의 `getDiscountAmount` |
| **객체 캡슐화** | 객체 사이의 관계를 감춘다 | **합성** | `Movie`가 `DiscountPolicy`를 `private`으로 포함 |
| **서브타입 캡슐화** | 서브타입의 종류를 감춘다 | **다형성** | `Movie`가 `AmountDiscountPolicy`의 존재를 모름 |

일반적으로 데이터 캡슐화와 메서드 캡슐화는 **개별 객체에 대한 변경**을 관리하기 위해 사용하고, 객체 캡슐화와 서브타입 캡슐화는 **협력에 참여하는 객체들의 관계에 대한 변경**을 관리하기 위해 사용한다.

변경을 캡슐화할 수 있는 다양한 방법이 존재하지만, 협력을 일관성 있게 만들기 위해 가장 일반적으로 사용하는 방법은 **서브타입 캡슐화와 객체 캡슐화를 조합**하는 것이다. 서브타입 캡슐화는 **인터페이스 상속**을 사용하고, 객체 캡슐화는 **합성**을 사용한다.

서브타입 캡슐화와 객체 캡슐화를 적용하는 방법:

1. **변하는 부분을 분리해서 타입 계층을 만든다**: 변하는 부분들의 공통적인 행동을 추상 클래스나 인터페이스로 추상화한 후, 변하는 부분들이 이 추상화를 상속받게 만든다.
2. **변하지 않는 부분의 일부로 타입 계층을 합성한다**: 의존성 주입과 같이 결합도를 느슨하게 유지할 수 있는 방법을 이용해 오직 추상화에만 의존하게 만든다.

---

## 3. 일관성 있는 기본 정책 구현하기

### 3.1 변경 분리하기

일관성 있는 협력을 만들기 위한 첫 번째 단계는 변하는 개념과 변하지 않는 개념을 분리하는 것이다.

| 방식 | 규칙 패턴 |
|---|---|
| 고정요금 방식 | [단위 시간]당 [요금]원 |
| 시간대별 방식 | [시작 시간]~[종료 시간]까지 [단위 시간]당 [요금]원 |
| 요일별 방식 | [요일]별 [단위 시간]당 [요금]원 |
| 구간별 방식 | [통화 구간] 동안 [단위 시간]당 [요금]원 |

시간대별, 요일별, 구간별 방식의 공통점:

- 기본 정책은 한 개 이상의 **'규칙'**으로 구성된다.
- 하나의 **'규칙'**은 **'적용 조건'**과 **'단위 요금'**의 조합이다.

```
                   적용 조건            단위 요금
시간대별 방식:  ┌─ 00시~19시까지  ───  10초당 18원 ─┐ 규칙
               └─ 19시~24시까지  ───  10초당 15원 ─┘ 규칙

요일별 방식:   ┌─ 평일          ───  10초당 38원 ─┐ 규칙
               └─ 공휴일        ───  10초당 19원 ─┘ 규칙

구간별 방식:   ┌─ 초기 1분 동안  ───  10초당 50원 ─┐ 규칙
               └─ 1분 이후      ───  10초당 20원 ─┘ 규칙
```

시간대별, 요일별, 구간별 방식의 **차이점**은 각 기본 정책별로 요금을 계산하는 **'적용 조건'의 형식이 다르다**는 것이다. 모든 규칙에 '적용 조건'이 포함된다는 사실은 변하지 않지만, 실제 조건의 세부적인 내용은 다르다. **조건의 세부 내용이 바로 변화에 해당한다.**

공통점은 **변하지 않는 부분**이다. 차이점은 **변하는 부분**이다. 따라서 변하지 않는 '규칙'으로부터 변하는 '적용 조건'을 분리해야 한다.

### 3.2 변경 캡슐화하기

변경을 캡슐화하는 가장 좋은 방법은 변하지 않는 부분으로부터 변하는 부분을 분리하는 것이다. 물론 변하는 부분의 공통점을 추상화하는 것도 잊어서는 안 된다.

- 변하지 않는 것: **'규칙'** → `FeeRule` 클래스
- 변하는 것: **'적용 조건'** → `FeeCondition` 인터페이스 (추상화)
  - 시간대별: `TimeOfDayFeeCondition`
  - 요일별: `DayOfWeekFeeCondition`
  - 구간별: `DurationFeeCondition`

`FeeRule`이 `FeeCondition`을 **합성 관계**로 연결하고, 오직 `FeeCondition`에만 의존한다. `FeeRule`은 `FeeCondition`의 어떤 서브타입도 알지 못한다. 따라서 변하는 `FeeCondition`의 서브타입은 변하지 않는 `FeeRule`로부터 캡슐화된다.

```
  BasicRatePolicy ──────→ FeeRule
                            │ feePerDuration
                            │ feeCondition
                            ▼
                      «interface»
                       FeeCondition
                            ▲
              ┌─────────────┼─────────────┐
              │             │             │
        TimeOfDay     DayOfWeek     Duration
       FeeCondition  FeeCondition  FeeCondition
```

### 3.3 협력 패턴 설계하기

변하는 부분과 변하지 않는 부분을 분리하고, 변하는 부분을 적절히 추상화하고 나면, 변하는 부분을 생략한 채 **변하지 않는 부분만을 이용해** 객체 사이의 협력을 이야기할 수 있다. 추상화만으로 구성한 협력은 추상화를 구체적인 사례로 대체함으로써 다양한 상황으로 확장할 수 있게 된다. 다시 말해서 **재사용 가능한 협력 패턴**이 선명하게 드러나는 것이다.

협력 흐름:

1. `BasicRatePolicy`가 `calculateFee` 메시지를 수신한다.
2. `BasicRatePolicy`는 각 `Call`별로 `FeeRule`의 `calculateFee`를 호출한다.
3. `FeeRule`은 `FeeCondition`에게 `findTimeIntervals` 메시지를 전송하여 적용 조건을 만족하는 구간을 반환받는다.
4. `FeeRule`은 `feePerDuration` 정보를 이용해 반환받은 기간만큼의 통화 요금을 계산한다.

```
1: calculateFee(phone)     2: calculateFee(call)     3: findTimeIntervals(call)
──────────────────→         ──────────────────→        ──────────────────→
  BasicRatePolicy              FeeRule                   FeeCondition
```

> **핵심 통찰**: 이 협력에 `FeeCondition`이라는 **추상화**가 참여하고 있다는 것에 주목하라. 만약 시간대별 방식으로 요금을 계산하고 싶다면 `TimeOfDayFeeCondition`의 인스턴스가 `FeeCondition`의 자리를 대신할 것이다.

### 3.4 추상화 수준에서 협력 패턴 구현하기

먼저 '적용 조건'을 표현하는 추상화인 `FeeCondition`에서 시작하자.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public interface FeeCondition {
    List<DateTimeInterval> findTimeIntervals(Call call);
}
```

</details>

```typescript
// TypeScript
interface FeeCondition {
    findTimeIntervals(call: Call): DateTimeInterval[];
}
```

`FeeRule`은 '단위 요금(`feePerDuration`)'과 '적용 조건(`feeCondition`)'을 저장하는 두 개의 인스턴스 변수로 구성된다. `calculateFee` 메서드는 `FeeCondition`에게 `findTimeIntervals` 메시지를 전송해서 조건을 만족하는 시간의 목록을 반환받은 후 `feePerDuration`의 값을 이용해 요금을 계산한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class FeeRule {
    private FeeCondition feeCondition;
    private FeePerDuration feePerDuration;

    public FeeRule(FeeCondition feeCondition, FeePerDuration feePerDuration) {
        this.feeCondition = feeCondition;
        this.feePerDuration = feePerDuration;
    }

    public Money calculateFee(Call call) {
        return feeCondition.findTimeIntervals(call)
            .stream()
            .map(each -> feePerDuration.calculate(each))
            .reduce(Money.ZERO, (first, second) -> first.plus(second));
    }
}
```

</details>

```typescript
// TypeScript
class FeeRule {
    constructor(
        private feeCondition: FeeCondition,
        private feePerDuration: FeePerDuration
    ) {}

    calculateFee(call: Call): Money {
        return this.feeCondition.findTimeIntervals(call)
            .map(each => this.feePerDuration.calculate(each))
            .reduce(
                (first, second) => first.plus(second),
                Money.ZERO
            );
    }
}
```

`FeePerDuration` 클래스는 "단위 시간당 요금"이라는 개념을 표현하고, 이 정보를 이용해 일정 기간 동안의 요금을 계산하는 `calculate` 메서드를 구현한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class FeePerDuration {
    private Money fee;
    private Duration duration;

    public FeePerDuration(Money fee, Duration duration) {
        this.fee = fee;
        this.duration = duration;
    }

    public Money calculate(DateTimeInterval interval) {
        return fee.times(
            Math.ceil((double) interval.duration().toNanos() / duration.toNanos())
        );
    }
}
```

</details>

```typescript
// TypeScript
class FeePerDuration {
    constructor(
        private fee: Money,
        private duration: number // seconds
    ) {}

    calculate(interval: DateTimeInterval): Money {
        return this.fee.times(
            Math.ceil(interval.duration() / this.duration)
        );
    }
}
```

이제 `BasicRatePolicy`가 `FeeRule`의 컬렉션을 이용해 전체 통화 요금을 계산하도록 수정할 수 있다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class BasicRatePolicy implements RatePolicy {
    private List<FeeRule> feeRules = new ArrayList<>();

    public BasicRatePolicy(FeeRule... feeRules) {
        this.feeRules = Arrays.asList(feeRules);
    }

    @Override
    public Money calculateFee(Phone phone) {
        return phone.getCalls()
            .stream()
            .map(call -> calculate(call))
            .reduce(Money.ZERO, (first, second) -> first.plus(second));
    }

    private Money calculate(Call call) {
        return feeRules
            .stream()
            .map(rule -> rule.calculateFee(call))
            .reduce(Money.ZERO, (first, second) -> first.plus(second));
    }
}
```

</details>

```typescript
// TypeScript
class BasicRatePolicy implements RatePolicy {
    private feeRules: FeeRule[];

    constructor(...feeRules: FeeRule[]) {
        this.feeRules = feeRules;
    }

    calculateFee(phone: Phone): Money {
        return phone.getCalls()
            .map(call => this.calculate(call))
            .reduce(
                (first, second) => first.plus(second),
                Money.ZERO
            );
    }

    private calculate(call: Call): Money {
        return this.feeRules
            .map(rule => rule.calculateFee(call))
            .reduce(
                (first, second) => first.plus(second),
                Money.ZERO
            );
    }
}
```

> **핵심 통찰**: 지금까지 구현한 클래스와 인터페이스는 모두 **변하지 않는 추상화**에 해당한다. 이 요소들을 조합하면 전체적인 협력 구조가 완성된다. 다시 말해서 변하지 않는 요소와 추상적인 요소만으로도 요금 계산에 필요한 전체적인 협력 구조를 설명할 수 있다는 것이다. **이것이 핵심이다.** 변하는 것과 변하지 않는 것을 분리하고 변하는 것을 캡슐화한 코드는 오로지 변하지 않는 것과 추상화에 대한 의존성만으로도 전체적인 협력을 구현할 수 있다.

### 3.5 구체적인 협력 구현하기

현재의 요금제가 시간대별 정책인지, 요일별 정책인지, 구간별 정책인지를 결정하는 기준은 **`FeeCondition`을 대체하는 객체의 타입**이 무엇인가에 달려 있다.

#### 시간대별 정책

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class TimeOfDayFeeCondition implements FeeCondition {
    private LocalTime from;
    private LocalTime to;

    public TimeOfDayFeeCondition(LocalTime from, LocalTime to) {
        this.from = from;
        this.to = to;
    }

    @Override
    public List<DateTimeInterval> findTimeIntervals(Call call) {
        return call.getInterval().splitByDay()
            .stream()
            .filter(each -> from(each).isBefore(to(each)))
            .map(each -> DateTimeInterval.of(
                LocalDateTime.of(each.getFrom().toLocalDate(), from(each)),
                LocalDateTime.of(each.getTo().toLocalDate(), to(each))))
            .collect(Collectors.toList());
    }

    private LocalTime from(DateTimeInterval interval) {
        return interval.getFrom().toLocalTime().isBefore(from)
            ? from : interval.getFrom().toLocalTime();
    }

    private LocalTime to(DateTimeInterval interval) {
        return interval.getTo().toLocalTime().isAfter(to)
            ? to : interval.getTo().toLocalTime();
    }
}
```

</details>

```typescript
// TypeScript
class TimeOfDayFeeCondition implements FeeCondition {
    constructor(
        private from: number, // 시작 시간 (시 단위, e.g. 0, 19)
        private to: number    // 종료 시간 (시 단위, e.g. 19, 24)
    ) {}

    findTimeIntervals(call: Call): DateTimeInterval[] {
        return call.getInterval().splitByDay()
            .filter(each => this.fromTime(each) < this.toTime(each))
            .map(each => {
                const fromDate = new Date(each.getFrom());
                fromDate.setHours(this.fromTime(each), 0, 0, 0);
                const toDate = new Date(each.getTo());
                toDate.setHours(this.toTime(each), 0, 0, 0);
                return DateTimeInterval.of(fromDate, toDate);
            });
    }

    private fromTime(interval: DateTimeInterval): number {
        const hour = interval.getFrom().getHours();
        return hour < this.from ? this.from : hour;
    }

    private toTime(interval: DateTimeInterval): number {
        const hour = interval.getTo().getHours();
        return hour > this.to ? this.to : hour;
    }
}
```

#### 요일별 정책

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class DayOfWeekFeeCondition implements FeeCondition {
    private List<DayOfWeek> dayOfWeeks = new ArrayList<>();

    public DayOfWeekFeeCondition(DayOfWeek... dayOfWeeks) {
        this.dayOfWeeks = Arrays.asList(dayOfWeeks);
    }

    @Override
    public List<DateTimeInterval> findTimeIntervals(Call call) {
        return call.getInterval()
            .splitByDay()
            .stream()
            .filter(each ->
                dayOfWeeks.contains(each.getFrom().getDayOfWeek()))
            .collect(Collectors.toList());
    }
}
```

</details>

```typescript
// TypeScript
class DayOfWeekFeeCondition implements FeeCondition {
    private dayOfWeeks: number[];

    constructor(...dayOfWeeks: number[]) {
        this.dayOfWeeks = dayOfWeeks;
    }

    findTimeIntervals(call: Call): DateTimeInterval[] {
        return call.getInterval()
            .splitByDay()
            .filter(each =>
                this.dayOfWeeks.includes(each.getFrom().getDay())
            );
    }
}
```

#### 구간별 정책

처음 설계에서 구간별 정책을 추가할 때 겪었던 어려움을 떠올려 보자. 이전의 설계에서는 새로운 기본 정책을 추가하기 위해 따라야 하는 지침이 존재하지 않았기 때문에 개발자는 자신이 선호하는 방식으로 구간별 정책을 추가해야 했다.

협력을 일관성 있게 만들면 문제를 해결할 수 있다. 간단하게 `FeeCondition` 인터페이스를 구현하는 `DurationFeeCondition` 클래스를 추가한 후 `findTimeIntervals` 메서드를 오버라이딩하면 된다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class DurationFeeCondition implements FeeCondition {
    private Duration from;
    private Duration to;

    public DurationFeeCondition(Duration from, Duration to) {
        this.from = from;
        this.to = to;
    }

    @Override
    public List<DateTimeInterval> findTimeIntervals(Call call) {
        if (call.getInterval().duration().compareTo(from) < 0) {
            return Collections.emptyList();
        }

        return Arrays.asList(DateTimeInterval.of(
            call.getInterval().getFrom().plus(from),
            call.getInterval().duration().compareTo(to) > 0
                ? call.getInterval().getFrom().plus(to)
                : call.getInterval().getTo()));
    }
}
```

</details>

```typescript
// TypeScript
class DurationFeeCondition implements FeeCondition {
    constructor(
        private from: number, // 구간 시작 (초)
        private to: number    // 구간 종료 (초)
    ) {}

    findTimeIntervals(call: Call): DateTimeInterval[] {
        if (call.getInterval().duration() < this.from) {
            return [];
        }

        const fromDate = new Date(
            call.getInterval().getFrom().getTime() + this.from * 1000
        );
        const toDate = call.getInterval().duration() > this.to
            ? new Date(
                call.getInterval().getFrom().getTime() + this.to * 1000
              )
            : call.getInterval().getTo();

        return [DateTimeInterval.of(fromDate, toDate)];
    }
}
```

이 예제는 변경을 캡슐화해서 협력을 일관성 있게 만들면 어떤 장점을 얻을 수 있는지를 잘 보여준다:

- 변하지 않는 부분을 **재사용**할 수 있다.
- 새로운 기능을 추가하기 위해 오직 변하는 부분만 구현하면 되기 때문에 원하는 기능을 쉽게 완성할 수 있다.
- 기능을 추가할 때 따라야 하는 구조를 **강제**할 수 있기 때문에 설계의 일관성이 무너지지 않는다.

### 3.6 협력 패턴에 맞추기: 고정요금 정책

여러 개의 '규칙'으로 구성되고, '규칙'이 '적용 조건'과 '단위 요금'의 조합으로 구성되는 시간대별, 요일별, 구간별 정책과 달리, **고정요금 정책은 '규칙'이라는 개념이 필요하지 않고 '단위 요금' 정보만 있으면 충분**하다.

이런 경우에 또 다른 협력 패턴을 적용하는 것이 최선의 선택인가? **그렇지 않다.** 가급적 기존의 협력 패턴에 맞추는 것이 가장 좋은 방법이다. 비록 설계를 약간 비트는 것이 조금은 이상한 구조를 낳더라도 **전체적으로 일관성을 유지할 수 있는 설계를 선택하는 것이 현명**하다.

고정요금 방식의 `FeeCondition`을 추가하고, 인자로 전달된 `Call`의 전체 통화 시간을 반환하게 하면 된다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class FixedFeeCondition implements FeeCondition {
    @Override
    public List<DateTimeInterval> findTimeIntervals(Call call) {
        return Arrays.asList(call.getInterval());
    }
}
```

</details>

```typescript
// TypeScript
class FixedFeeCondition implements FeeCondition {
    findTimeIntervals(call: Call): DateTimeInterval[] {
        return [call.getInterval()];
    }
}
```

개념적으로는 불필요한 `FixedFeeCondition` 클래스를 추가하고, `findTimeIntervals` 메서드의 반환 타입이 `List`임에도 항상 단 하나의 `DateTimeInterval` 인스턴스를 반환한다는 사실이 마음에 조금 걸리지만, **개념적 무결성을 무너뜨리는 것보다는 약간의 부조화를 수용하는 편이 더 낫다.**

> **핵심 통찰**: 기본 정책을 추가하기 위해 **규칙을 지키는 것보다 어기는 것이 더 어렵다**는 점에 주목하라. 일관성 있는 협력은 개발자에게 확장 포인트를 강제하기 때문에 정해진 구조를 우회하기 어렵게 만든다. 개발자는 코드의 형태로 주어진 제약 안에 머물러야 하지만, 작은 문제에 집중할 수 있는 자유를 얻는다.

### 3.7 최종 클래스 구조

```
                         Phone
                           │ ratePolicy
                           ▼
                     «interface»
                      RatePolicy
                    calculateFee(phone)
                      ▲          ▲
                      │          │ next
         BasicRatePolicy    AdditionalRatePolicy
        +calculateFee()         ▲
              │           ┌─────┴──────┐
              ▼      RateDiscount    Taxable
          FeeRule     ablePolicy     Policy
      ┌──────┴──────┐
      ▼              ▼
 FeePerDuration   «interface»
                  FeeCondition
                  findTimeIntervals()
                      ▲
        ┌─────────────┼─────────────┬──────────────┐
        │             │             │              │
   TimeOfDay     DayOfWeek    Duration         Fixed
  FeeCondition  FeeCondition  FeeCondition  FeeCondition
```

### 3.8 지속적으로 개선하라

> 처음에는 일관성을 유지하는 것처럼 보이던 협력 패턴이 시간이 흐르면서 새로운 요구사항이 추가되는 과정에서 일관성의 벽에 조금씩 금이 가는 경우를 자주 보게 된다. 협력을 설계하는 초기 단계에서 모든 요구사항을 미리 예상할 수 없기 때문에 이것은 잘못이 아니며 꽤나 자연스러운 현상이다. 오히려 새로운 요구사항을 수용할 수 있는 협력 패턴을 향해 설계를 진화시킬 수 있는 좋은 신호로 받아들여야 한다.

**협력은 고정된 것이 아니다.** 만약 현재의 협력 패턴이 변경의 무게를 지탱하기 어렵다면 변경을 수용할 수 있는 협력 패턴을 향해 과감하게 리팩터링하라. 중요한 것은 현재의 설계에 맹목적으로 일관성을 맞추는 것이 아니라, 달라지는 변경의 방향에 맞춰 **지속적으로 코드를 개선하려는 의지**다.

### 3.9 패턴을 찾아라

일관성 있는 협력의 핵심은 변경을 분리하고 캡슐화하는 것이다. 변경을 캡슐화하는 방법이 협력에 참여하는 객체들의 역할과 책임을 결정하고, 이렇게 결정된 협력이 코드의 구조를 결정한다.

유사한 기능에 대해 유사한 협력 패턴을 적용하는 것은 객체지향 시스템에서 **개념적 무결성**(*Conceptual Integrity*)[Brooks95]을 유지할 수 있는 가장 효과적인 방법이다. 개념적 무결성을 일관성과 동일한 뜻으로 간주해도 무방하다. 시스템이 일관성 있는 몇 개의 협력 패턴으로 구성된다면 시스템을 이해하고, 수정하고, 확장하는 데 필요한 노력과 시간을 아낄 수 있다.

> 저자는 개념적 무결성(Conceptual Integrity)이 시스템 설계에서 가장 중요하다고 감히 주장한다. 좋은 기능들이긴 하지만 서로 독립적이고 조화되지 못한 아이디어들을 담고 있는 시스템보다는, 여러 가지 다양한 기능이나 갱신된 내용은 비록 빠졌더라도 하나로 통합된 일련의 설계 아이디어를 반영하는 시스템이 훨씬 좋다[Brooks95].

> 객체지향 설계는 객체의 행동과 그것을 지원하기 위한 구조를 계속 수정해 나가는 작업을 반복해 나가면서 다듬어진다. 객체, 역할, 책임은 계속 진화해 나가는 것이다. 협력자들 간에 부하를 좀 더 균형 있게 배분하는 방법을 새로 만들어내면 나눠 줄 책임이 바뀌게 된다. 이같은 과정을 거치면서 객체들이 자주 통신하는 경로는 더욱 효율적이게 되고, 주어진 작업을 수행하는 표준 방안이 정착된다. 협력 패턴이 드러나는 것이다![Wirfs-Brock03]

협력 패턴과 관련해서 언급할 가치가 있는 두 가지 개념이 있다. 하나는 **패턴**이고 다른 하나는 **프레임워크**다. 이어지는 장에서 두 개념을 간단하게 살펴본다.

---

## 설계 원칙

| 원칙 | 핵심 내용 | 효과 |
|---|---|---|
| **변하는 것과 변하지 않는 것의 분리** | 변하는 개념을 변하지 않는 개념으로부터 분리하라 | 변경의 영향 범위를 한정한다 |
| **변하는 개념의 캡슐화** | 변하는 부분을 추상화한 후 서브타입으로 분리하라 | 기존 코드 수정 없이 확장이 가능하다 |
| **서브타입 캡슐화 + 객체 캡슐화** | 인터페이스 상속(다형성)과 합성을 조합하라 | 유연하고 일관성 있는 협력 구조를 만든다 |
| **조건 로직 → 객체 탐색** | 조건문의 분기를 객체 사이의 이동(다형성)으로 대체하라 | 변경의 주기가 다른 코드를 분리할 수 있다 |
| **일관성 있는 협력 패턴** | 유사한 기능은 유사한 협력 방식으로 구현하라 | 코드의 이해와 확장이 용이해진다 |
| **개념적 무결성** | 기존의 협력 패턴을 따를 수 없는지 항상 고민하라 | 시스템 전체의 일관성을 유지한다 |

---

## 요약

- **비일관성의 문제**: 유사한 기능을 구현하는 클래스들이 서로 다른 패턴을 따르면, 새로운 구현을 추가하기 어렵고 기존 구현을 이해하기도 어렵다. `FixedFeePolicy`, `TimeOfDayDiscountPolicy`, `DayOfWeekDiscountPolicy`는 모두 기본 정책을 구현하지만, 규칙을 구성하는 방식이 완전히 다르다.
- **일관성을 위한 두 가지 지침**: (1) 변하는 개념을 변하지 않는 개념으로부터 분리하라. (2) 변하는 개념을 캡슐화하라. 이 두 지침은 훌륭한 객체지향 설계의 근간이 된다.
- **조건 로직 → 객체 탐색**: 절차적 프로그래밍에서 변경을 처리하는 조건문의 분기를 객체 사이의 이동(다형성)으로 대체하는 것이 객체지향적 접근이다. 객체지향적인 코드는 조건을 판단하지 않는다. 단지 다음 객체로 이동할 뿐이다.
- **캡슐화의 네 가지 종류**: 데이터 캡슐화(private 필드), 메서드 캡슐화(protected 메서드), 객체 캡슐화(합성), 서브타입 캡슐화(다형성). 협력의 일관성을 위해 가장 중요한 것은 서브타입 캡슐화와 객체 캡슐화의 조합이다.
- **일관성 있는 기본 정책 구현**: 변하지 않는 '규칙'을 `FeeRule`로, 변하는 '적용 조건'을 `FeeCondition` 인터페이스와 그 서브타입으로 분리했다. 이를 통해 새로운 기본 정책 추가 시 `FeeCondition`의 서브타입만 구현하면 되는 일관성 있는 구조를 얻었다.
- **협력 패턴에 맞추기**: 고정요금 정책처럼 기존 협력 패턴에 맞지 않는 경우에도, 약간의 부조화를 수용하면서 기존 패턴에 맞추는 것이 전체적인 일관성 측면에서 현명하다.
- **개념적 무결성**: 시스템이 일관성 있는 몇 개의 협력 패턴으로 구성된다면 이해, 수정, 확장에 필요한 노력을 크게 줄일 수 있다. 하나의 협력 구조를 이해하면 그 지식을 다른 코드를 이해하는 데 그대로 적용할 수 있다.
- **지속적 개선**: 협력은 고정된 것이 아니다. 현재의 협력 패턴이 변경의 무게를 지탱하기 어렵다면 과감하게 리팩터링하라.

---

## 다른 챕터와의 관계

- **Chapter 4 (설계 품질과 트레이드오프)**: 4장에서 절차적으로 구현했던 `ReservationAgency`의 조건 로직이 이 장에서 객체 사이의 이동(다형성)으로 대체되는 과정의 출발점이다. 4장의 나쁜 설계가 왜 나쁜지를 "일관성"이라는 새로운 관점에서 재조명한다.
- **Chapter 9 (유연한 설계)**: 9장에서 설명한 개방-폐쇄 원칙(OCP)과 의존성 역전 원칙(DIP)이 이 장의 일관성 있는 협력 구조에서 자연스럽게 달성된다. `FeeRule`이 `FeeCondition` 추상화에만 의존하는 구조는 OCP와 DIP를 동시에 만족한다.
- **Chapter 10 (상속과 코드 재사용)**: `DurationDiscountRule`이 `FixedFeePolicy`를 코드 재사용 목적으로 상속하는 것이 10장에서 경고한 "상속의 오용" 사례다. 일관성 있는 협력으로 리팩터링한 후에는 이런 부자연스러운 상속이 완전히 제거된다.
- **Chapter 11 (합성과 유연한 설계)**: 11장에서 구현한 핸드폰 과금 시스템이 이 장의 출발점이다. 11장의 `BasicRatePolicy`와 `AdditionalRatePolicy` 구조 위에 기본 정책의 내부 구조를 일관성 있게 재설계한다. `FeeRule`이 `FeeCondition`을 합성으로 연결하는 것은 11장에서 강조한 "합성을 통한 캡슐화" 원칙의 적용이다.
- **Chapter 13 (서브클래싱과 서브타이핑)**: 13장에서 설명한 리스코프 치환 원칙을 준수하는 타입 계층이 이 장의 `FeeCondition` 계층에서 구현된다. 각 `FeeCondition` 서브타입은 `FeeCondition` 인터페이스를 완벽히 대체할 수 있다.
- **Chapter 15 (디자인 패턴과 프레임워크)**: 이 장의 마지막에 언급된 "패턴을 찾아라"는 조언이 15장으로 이어진다. 일관성 있는 협력을 반복적으로 적용 가능한 형태로 정리한 것이 디자인 패턴이다.
