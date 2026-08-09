# Chapter 8: Managing Dependencies (의존성 관리하기)

## 핵심 질문

잘 설계된 객체지향 애플리케이션은 작고 응집도 높은 객체들의 협력으로 이루어진다. 협력은 필수적이지만 과도한 협력은 설계를 곤경에 빠트린다. 협력을 위해 필요한 의존성은 유지하면서도 변경을 방해하는 의존성은 제거하려면 어떻게 해야 하는가? 유연하고 재사용 가능한 설계를 만들기 위해 의존성을 어떻게 관리해야 하는가?

---

## 1. 의존성 이해하기

### 1.1 변경과 의존성

어떤 객체가 협력하기 위해 다른 객체를 필요로 할 때 두 객체 사이에 **의존성**(*Dependency - 한 객체가 다른 객체의 변경에 영향을 받을 수 있는 관계*)이 존재하게 된다. 의존성은 실행 시점과 구현 시점에서 서로 다른 의미를 가진다.

| 시점 | 의미 |
|---|---|
| **실행 시점** | 의존하는 객체가 정상적으로 동작하기 위해서는 실행 시에 의존 대상 객체가 반드시 존재해야 한다 |
| **구현 시점** | 의존 대상 객체가 변경될 경우 의존하는 객체도 함께 변경된다 |

영화 예매 시스템의 `PeriodCondition` 클래스를 예로 들어보자.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class PeriodCondition implements DiscountCondition {
    private DayOfWeek dayOfWeek;
    private LocalTime startTime;
    private LocalTime endTime;

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
interface DiscountCondition {
    isSatisfiedBy(screening: Screening): boolean;
}

class PeriodCondition implements DiscountCondition {
    constructor(
        private dayOfWeek: number,   // 0(일) ~ 6(토)
        private startTime: string,   // "HH:mm" 형식
        private endTime: string
    ) {}

    isSatisfiedBy(screening: Screening): boolean {
        const startTime = screening.getStartTime();
        return startTime.getDay() === this.dayOfWeek &&
               this.startTime <= this.toTimeString(startTime) &&
               this.endTime >= this.toTimeString(startTime);
    }

    private toTimeString(date: Date): string {
        return `${String(date.getHours()).padStart(2, "0")}:${String(date.getMinutes()).padStart(2, "0")}`;
    }
}
```

실행 시점에 `PeriodCondition`의 인스턴스가 정상적으로 동작하기 위해서는 `Screening`의 인스턴스가 존재해야 한다. 만약 `Screening`의 인스턴스가 존재하지 않거나 `getStartTime` 메시지를 이해할 수 없다면 `PeriodCondition`의 `isSatisfiedBy` 메서드는 예상대로 동작하지 않을 것이다.

이처럼 어떤 객체가 예정된 작업을 정상적으로 수행하기 위해 다른 객체를 필요로 하는 경우 두 객체 사이에 의존성이 존재한다고 말한다. **의존성은 방향성을 가지며 항상 단방향이다.** `Screening`이 변경될 때 `PeriodCondition`이 영향을 받게 되지만 그 역은 성립하지 않는다.

```
PeriodCondition ─ ─ ─ ─ ▶ Screening
  (의존하는 객체)          (의존 대상)
```

`PeriodCondition`의 코드를 다시 살펴보면, `PeriodCondition`은 다음 네 가지 대상에 대해 의존성을 가진다:

```
       ┌─────────────────────┐
       │  «interface»        │
       │  DiscountCondition  │
       └─────────┬───────────┘
                 △ (실체화)
       ┌─────────┴───────────┐
       │  PeriodCondition    │──────▶ Screening (메서드 인자)
       └─────────────────────┘
           │           │
           ▼           ▼
       DayOfWeek   LocalTime
       (인스턴스 변수)
```

| 의존 대상 | 의존성의 원인 |
|---|---|
| `DiscountCondition` | 인터페이스에 정의된 오퍼레이션을 퍼블릭 인터페이스의 일부로 포함 (실체화 관계) |
| `DayOfWeek` | 인스턴스 변수의 타입으로 사용 (연관 관계) |
| `LocalTime` | 인스턴스 변수의 타입으로 사용 (연관 관계) |
| `Screening` | 메서드 인자의 타입으로 사용 (의존 관계) |

설계와 관련된 대부분의 용어들은 변경과 관련이 있다. 의존성 역시 마찬가지다. 두 요소 사이의 의존성은 의존되는 요소가 변경될 때 의존하는 요소도 함께 변경될 수 있다는 것을 의미한다. 따라서 **의존성은 변경에 의한 영향의 전파 가능성을 암시한다**.

> **핵심 통찰**: 이 장에서 말하는 '의존성'은 UML의 의존 관계(dependency)와는 다르다. UML은 두 요소 사이에 존재할 수 있는 다양한 관계(실체화, 연관, 의존, 일반화/특수화, 합성, 집합 등)의 하나로 '의존 관계'를 정의한다. 반면 이 장의 '의존성'은 두 요소 사이에 변경에 의해 영향을 주고받는 힘의 역학관계가 존재한다는 사실에 초점을 맞춘다. 따라서 UML에 정의된 **모든 관계는 의존성이라는 개념을 포함한다**.

### 1.2 의존성 전이

의존성은 전이될 수 있다. `Screening`의 코드를 살펴보면 `Screening`이 `Movie`, `LocalDateTime`, `Customer`에 의존한다는 사실을 알 수 있다.

의존성 전이(*Transitive Dependency - A가 B에, B가 C에 의존할 때 A가 C에도 간접적으로 의존하게 되는 현상*)가 의미하는 것은 `PeriodCondition`이 `Screening`에 의존할 경우 `PeriodCondition`은 `Screening`이 의존하는 대상에 대해서도 자동적으로 의존하게 된다는 것이다.

```
PeriodCondition ─ ─ ▶ Screening ─ ─ ▶ Movie
                      (직접 의존)      (간접 의존 - 전이)
```

의존성은 함께 변경될 수 있는 **가능성**을 의미하기 때문에 모든 경우에 의존성이 전이되는 것은 아니다. 의존성이 실제로 전이될지 여부는 **변경의 방향**과 **캡슐화의 정도**에 따라 달라진다. `Screening`이 내부 구현을 효과적으로 캡슐화하고 있다면 `Screening`에 의존하고 있는 `PeriodCondition`까지는 변경이 전파되지 않을 것이다. 의존성 전이는 변경에 의해 영향이 널리 전파될 수도 있다는 경고일 뿐이다.

의존성은 전이될 수 있기 때문에 두 종류로 구분된다:

| 종류 | 설명 | 예시 |
|---|---|---|
| **직접 의존성** (*Direct Dependency*) | 한 요소가 다른 요소에 직접 의존하는 경우. 코드에 명시적으로 드러남 | `PeriodCondition` → `Screening` |
| **간접 의존성** (*Indirect Dependency*) | 직접적인 관계는 없지만 의존성 전이에 의해 영향이 전파되는 경우. 코드에 명시적으로 드러나지 않음 | `PeriodCondition` → `Movie` |

의존성의 대상은 객체일 수도 있고, 모듈이나 더 큰 규모의 실행 시스템일 수도 있다. 하지만 **의존성의 본질은 변하지 않는다. 의존성이란 의존하고 있는 대상의 변경에 영향을 받을 수 있는 가능성이다.**

### 1.3 런타임 의존성과 컴파일타임 의존성

의존성과 관련해서 다뤄야 하는 또 다른 주제는 **런타임 의존성**(*Run-time Dependency*)과 **컴파일타임 의존성**(*Compile-time Dependency*)의 차이다.

- **런타임**: 말 그대로 애플리케이션이 실행되는 시점을 가리킨다.
- **컴파일타임**: 일반적으로 코드를 컴파일하는 시점을 가리키지만, 문맥에 따라서는 **코드 그 자체**를 가리키기도 한다. 동적 타입 언어의 경우에는 컴파일타임이 존재하지 않기 때문에, 컴파일타임 의존성이라는 용어가 중요하게 생각하는 것은 시간이 아니라 우리가 작성한 **코드의 구조**다.

객체지향 애플리케이션에서 런타임의 주인공은 **객체**다. 따라서 런타임 의존성이 다루는 주제는 **객체 사이의 의존성**이다. 반면 코드 관점에서 주인공은 **클래스**다. 따라서 컴파일타임 의존성이 다루는 주제는 **클래스 사이의 의존성**이다.

여기서 중요한 것은 **런타임 의존성과 컴파일타임 의존성이 다를 수 있다**는 것이다. 사실 유연하고 재사용 가능한 코드를 설계하기 위해서는 두 종류의 의존성을 서로 다르게 만들어야 한다.

영화 예매 시스템을 예로 들어 살펴보자. `Movie`는 가격을 계산하기 위해 비율 할인 정책과 금액 할인 정책 모두를 적용할 수 있게 설계해야 한다.

```
  [컴파일타임 의존성 - 코드 구조]

  Movie ─ ─ ─ ─ ▶ DiscountPolicy (추상 클래스)
                        △
                   ┌────┴────┐
                   │         │
        AmountDiscount   PercentDiscount
           Policy           Policy
```

`Movie` 클래스에서 `AmountDiscountPolicy` 클래스와 `PercentDiscountPolicy` 클래스로 향하는 어떤 의존성도 존재하지 않는다. `Movie` 클래스는 오직 추상 클래스인 `DiscountPolicy` 클래스에만 의존한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Movie {
    private DiscountPolicy discountPolicy;

    public Movie(String title, Duration runningTime, Money fee,
                 DiscountPolicy discountPolicy) {
        // ...
        this.discountPolicy = discountPolicy;
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
    constructor(
        private title: string,
        private runningTime: number,
        private fee: Money,
        private discountPolicy: DiscountPolicy
    ) {}

    calculateMovieFee(screening: Screening): Money {
        return this.fee.minus(
            this.discountPolicy.calculateDiscountAmount(screening)
        );
    }
}
```

하지만 런타임 의존성을 살펴보면 상황이 완전히 달라진다.

```
  [런타임 의존성 - 실행 시점]

  Movie 인스턴스 ──▶ AmountDiscountPolicy 인스턴스
         또는
  Movie 인스턴스 ──▶ PercentDiscountPolicy 인스턴스
```

코드 작성 시점의 `Movie` 클래스는 할인 정책을 구현한 두 클래스의 존재를 모르지만, 실행 시점의 `Movie` 객체는 두 클래스의 인스턴스와 협력할 수 있게 된다. **이것이 핵심이다.** 유연하고 재사용 가능한 설계를 창조하기 위해서는 동일한 소스코드 구조를 가지고 다양한 실행 구조를 만들 수 있어야 한다.

어떤 클래스의 인스턴스가 다양한 클래스의 인스턴스와 협력하기 위해서는 협력할 인스턴스의 구체적인 클래스를 알아서는 안 된다. 실제로 협력할 객체가 어떤 것인지는 런타임에 해결해야 한다.

> **컴파일타임 구조와 런타임 구조 사이의 거리가 멀면 멀수록 설계가 유연해지고 재사용 가능해진다.**

> 객체지향 프로그램의 실행 구조는 소스코드 구조와 일치하지 않는 경우가 종종 있다. 코드 구조는 컴파일 시점에 확정되는 것이고 이 구조에는 고정된 상속 클래스 관계들이 포함된다. 그러나 프로그램의 실행 시점 구조는 협력하는 객체에 따라서 달라질 수 있다. 즉, 두 구조는 전혀 다른 별개의 독립성을 갖는다. ... 시스템의 실행 시점 구조는 언어가 아닌 설계자가 만든 타입들 간의 관련성으로 만들어진다[GOF94].

### 1.4 컨텍스트 독립성

유연하고 확장 가능한 설계를 만들기 위해서는 컴파일타임 의존성과 런타임 의존성이 달라야 한다는 사실을 이해했을 것이다. 클래스는 자신과 협력할 객체의 구체적인 클래스에 대해 알아서는 안 된다. 구체적인 클래스를 알면 알수록 그 클래스가 사용되는 특정한 문맥에 강하게 결합되기 때문이다.

`Movie` 클래스 안에 `PercentDiscountPolicy` 클래스에 대한 컴파일타임 의존성을 명시적으로 표현하는 것은 `Movie`가 비율 할인 정책이 적용된 영화의 요금을 계산하는 문맥에서 사용될 것이라고 가정하는 것이다. 반면 추상 클래스인 `DiscountPolicy`에 대한 컴파일타임 의존성을 명시하는 것은 `Movie`가 할인 정책에 따라 요금을 계산하지만 구체적으로 어떤 정책을 따르는지는 결정하지 않았다고 선언하는 것이다.

**클래스가 특정한 문맥에 강하게 결합될수록 다른 문맥에서 사용하기는 더 어려워진다.** 클래스가 사용될 특정한 문맥에 대해 최소한의 가정만으로 이루어져 있다면 다른 문맥에서 재사용하기가 더 수월해진다. 이를 **컨텍스트 독립성**(*Context Independence*)이라고 부른다.

설계가 유연해지기 위해서는 가능한 한 자신이 실행될 컨텍스트에 대한 구체적인 정보를 최대한 적게 알아야 한다.

> 시스템을 구성하는 객체가 컨텍스트 독립적이라면 해당 시스템은 변경하기 쉽다. 여기서 컨텍스트 독립적이라는 말은 각 객체가 해당 객체를 실행하는 시스템에 관해 아무것도 알지 못한다는 의미다. 이렇게 되면 행위의 단위(객체)를 가지고 새로운 상황에 적용할 수 있다. ... 컨텍스트 독립성을 따르면 다양한 컨텍스트에 적용할 수 있는 응집력 있는 객체를 만들 수 있고 객체 구성 방법을 재설정해서 변경 가능한 시스템으로 나아갈 수 있다[Freeman09].

### 1.5 의존성 해결하기

클래스가 실행 컨텍스트에 독립적인데도 어떻게 런타임에 실행 컨텍스트에 적절한 객체들과 협력할 수 있을까?

컴파일타임 의존성은 구체적인 런타임 의존성으로 대체돼야 한다. 이처럼 컴파일타임 의존성을 실행 컨텍스트에 맞는 적절한 런타임 의존성으로 교체하는 것을 **의존성 해결**이라고 부른다. 의존성을 해결하기 위해서는 일반적으로 다음과 같은 세 가지 방법을 사용한다:

1. **객체를 생성하는 시점에 생성자를 통해 의존성 해결**
2. **객체 생성 후 setter 메서드를 통해 의존성 해결**
3. **메서드 실행 시 인자를 이용해 의존성 해결**

#### 방법 1: 생성자를 통한 의존성 해결

`Movie` 객체를 생성할 때 `AmountDiscountPolicy`의 인스턴스를 생성자에 인자로 전달한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
Movie avatar = new Movie("아바타",
    Duration.ofMinutes(120),
    Money.wons(10000),
    new AmountDiscountPolicy(...));

Movie starWars = new Movie("스타워즈",
    Duration.ofMinutes(180),
    Money.wons(11000),
    new PercentDiscountPolicy(...));
```

</details>

```typescript
// TypeScript
const avatar = new Movie("아바타", 120, Money.wons(10000),
    new AmountDiscountPolicy(/* ... */));

const starWars = new Movie("스타워즈", 180, Money.wons(11000),
    new PercentDiscountPolicy(/* ... */));
```

이를 위해 `Movie` 클래스는 `DiscountPolicy` 타입의 인자를 받는 생성자를 정의한다. `PercentDiscountPolicy` 인스턴스와 `AmountDiscountPolicy` 인스턴스 모두를 선택적으로 전달할 수 있다.

#### 방법 2: setter 메서드를 통한 의존성 해결

`Movie` 인스턴스가 생성된 후에도 `DiscountPolicy`를 설정할 수 있는 setter 메서드를 제공한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
Movie avatar = new Movie(/* ... */);
avatar.setDiscountPolicy(new AmountDiscountPolicy(...));

// 중간에 정책 변경 가능
avatar.setDiscountPolicy(new PercentDiscountPolicy(...));
```

</details>

```typescript
// TypeScript
const avatar = new Movie(/* ... */);
avatar.setDiscountPolicy(new AmountDiscountPolicy(/* ... */));

// 중간에 정책 변경 가능
avatar.setDiscountPolicy(new PercentDiscountPolicy(/* ... */));
```

setter 메서드를 이용하는 방식은 객체를 생성한 이후에도 의존 대상을 변경할 수 있는 가능성을 열어 놓고 싶은 경우에 유용하다. 실행 시점에 의존 대상을 변경할 수 있기 때문에 설계를 좀 더 유연하게 만들 수 있다.

**단점은 객체가 생성된 후에 협력에 필요한 의존 대상을 설정하기 때문에, 객체를 생성하고 의존 대상을 설정하기 전까지는 객체의 상태가 불완전할 수 있다는 점이다.**

```typescript
// TypeScript
const avatar = new Movie(/* ... */);
avatar.calculateMovieFee(/* ... */); // 예외 발생! discountPolicy가 아직 없다
avatar.setDiscountPolicy(new AmountDiscountPolicy(/* ... */));
```

#### 방법 3: 생성자 + setter 혼합 (권장)

더 좋은 방법은 **생성자 방식과 setter 방식을 혼합**하는 것이다. 항상 객체를 생성할 때 의존성을 해결해서 완전한 상태의 객체를 생성한 후, 필요에 따라 setter 메서드를 이용해 의존 대상을 변경할 수 있게 하는 것이다. 이 방법은 시스템의 상태를 안정적으로 유지하면서도 유연성을 향상시킬 수 있기 때문에 의존성 해결을 위해 가장 선호되는 방법이다.

```typescript
// TypeScript
const avatar = new Movie("아바타", 120, Money.wons(10000),
    new PercentDiscountPolicy(/* ... */)); // 생성 시 완전한 상태

avatar.setDiscountPolicy(new AmountDiscountPolicy(/* ... */)); // 이후 변경 가능
```

#### 방법 4: 메서드 인자를 통한 의존성 해결

`Movie`가 항상 할인 정책을 알 필요 없이, 가격을 계산할 때만 일시적으로 알아도 무방하다면 메서드의 인자를 이용해 의존성을 해결할 수도 있다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Movie {
    public Money calculateMovieFee(Screening screening,
                                   DiscountPolicy discountPolicy) {
        return fee.minus(discountPolicy.calculateDiscountAmount(screening));
    }
}
```

</details>

```typescript
// TypeScript
class Movie {
    calculateMovieFee(screening: Screening,
                      discountPolicy: DiscountPolicy): Money {
        return this.fee.minus(
            discountPolicy.calculateDiscountAmount(screening)
        );
    }
}
```

메서드 인자를 사용하는 방식은 협력 대상에 대해 지속적으로 의존 관계를 맺을 필요 없이 **메서드가 실행되는 동안만 일시적으로 의존 관계가 존재해도 무방하거나, 메서드가 실행될 때마다 의존 대상이 매번 달라져야 하는 경우**에 유용하다. 하지만 대부분의 경우에 매번 동일한 객체를 인자로 전달하고 있다면 생성자나 setter 메서드를 이용하는 방식으로 변경하는 것이 좋다.

---

## 2. 유연한 설계

설계를 유연하고 재사용 가능하게 만들기로 결정했다면 의존성을 관리하는 데 유용한 몇 가지 원칙과 기법을 익힐 필요가 있다.

### 2.1 의존성과 결합도

객체지향 패러다임의 근간은 협력이다. 객체들이 협력하기 위해서는 서로의 존재와 수행 가능한 책임을 알아야 한다. 이런 지식들이 객체 사이의 의존성을 낳는다. 따라서 **모든 의존성이 나쁜 것은 아니다**. 의존성은 객체들의 협력을 가능하게 만드는 매개체라는 관점에서는 바람직한 것이다.

문제는 **의존성의 존재가 아니라 의존성의 정도**다.

`Movie`가 `PercentDiscountPolicy`에 직접 의존하는 경우를 생각해 보자:

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Movie {
    private PercentDiscountPolicy percentDiscountPolicy;

    public Movie(String title, Duration runningTime, Money fee,
                 PercentDiscountPolicy percentDiscountPolicy) {
        // ...
        this.percentDiscountPolicy = percentDiscountPolicy;
    }

    public Money calculateMovieFee(Screening screening) {
        return fee.minus(
            percentDiscountPolicy.calculateDiscountAmount(screening)
        );
    }
}
```

</details>

```typescript
// TypeScript
class Movie {
    constructor(
        private title: string,
        private runningTime: number,
        private fee: Money,
        private percentDiscountPolicy: PercentDiscountPolicy  // 구체 클래스!
    ) {}

    calculateMovieFee(screening: Screening): Money {
        return this.fee.minus(
            this.percentDiscountPolicy.calculateDiscountAmount(screening)
        );
    }
}
```

이 코드는 `Movie`를 `PercentDiscountPolicy`라는 구체적인 클래스에 의존하게 만들기 때문에 다른 종류의 할인 정책이 필요한 문맥에서 `Movie`를 재사용할 수 있는 가능성을 없애 버렸다.

**바람직한 의존성이란 재사용성과 관련이 있다.** 어떤 의존성이 다양한 환경에서 클래스를 재사용할 수 없도록 제한한다면 그 의존성은 바람직하지 못한 것이다. 어떤 의존성이 다양한 환경에서 재사용할 수 있다면 그 의존성은 바람직한 것이다.

바람직한 의존성과 바람직하지 못한 의존성을 가리키는 좀 더 세련된 용어가 존재한다. **결합도**(*Coupling*)가 바로 그것이다.

| 용어 | 의미 | 재사용성 |
|---|---|---|
| **느슨한 결합도** (*Loose Coupling*) | 의존성이 바람직할 때 | 다양한 환경에서 재사용 가능 |
| **강한 결합도** (*Tight Coupling*) | 의존성이 바람직하지 못할 때 | 특정 컨텍스트에 강하게 묶임 |

> **핵심 통찰**: 의존성과 결합도를 동의어로 사용하는 경우가 많지만 사실 두 용어는 서로 다른 관점에서 관계의 특성을 설명한다. **의존성**은 두 요소 사이의 관계 유무를 설명한다("의존성이 존재한다" 또는 "의존성이 존재하지 않는다"). **결합도**는 두 요소 사이에 존재하는 의존성의 정도를 상대적으로 표현한다("결합도가 강하다" 또는 "결합도가 느슨하다").

### 2.2 지식이 결합을 낳는다

결합도의 정도는 한 요소가 자신이 의존하고 있는 다른 요소에 대해 **알고 있는 정보의 양**으로 결정된다. 한 요소가 다른 요소에 대해 더 많은 정보를 알고 있을수록 두 요소는 강하게 결합된다.

- `Movie`가 `PercentDiscountPolicy`에 직접 의존하는 경우: `Movie`는 협력할 객체가 **비율 할인 정책에 따라** 할인 요금을 계산할 것이라는 사실을 알고 있다.
- `Movie`가 `DiscountPolicy`에 의존하는 경우: 구체적인 계산 방법은 알 필요가 없다. 그저 **할인 요금을 계산한다**는 사실만 알고 있을 뿐이다.

**더 많이 알수록 더 많이 결합된다.** 더 많이 알고 있다는 것은 더 적은 컨텍스트에서 재사용 가능하다는 것을 의미한다. 결합도를 느슨하게 유지하려면 협력하는 대상에 대해 **더 적게 알아야** 한다. 결합도를 느슨하게 만들기 위해서는 협력하는 대상에 대해 필요한 정보 외에는 최대한 감추는 것이 중요하다.

이 목적을 달성할 수 있는 가장 효과적인 방법은 **추상화**다.

### 2.3 추상화에 의존하라

추상화란 어떤 양상, 세부사항, 구조를 좀 더 명확하게 이해하기 위해 특정 절차나 물체를 의도적으로 생략하거나 감춤으로써 복잡도를 극복하는 방법이다. 추상화를 사용하면 현재 다루고 있는 문제를 해결하는 데 불필요한 정보를 감출 수 있다. 따라서 대상에 대해 알아야 하는 지식의 양을 줄일 수 있기 때문에 결합도를 느슨하게 유지할 수 있다.

일반적으로 추상화와 결합도의 관점에서 의존 대상을 다음과 같이 구분하는 것이 유용하다. **목록에서 아래쪽으로 갈수록 클라이언트가 알아야 하는 지식의 양이 적어지기 때문에 결합도가 느슨해진다.**

| 의존 대상 | 알아야 하는 지식 | 결합도 |
|---|---|---|
| **구체 클래스** | 클래스의 이름, 내부 구현, 생성자 인자 등 | 강함 |
| **추상 클래스** | 추상화된 인터페이스, 메서드 시그니처 (내부 구현과 자식 클래스 종류는 숨김) | 중간 |
| **인터페이스** | 오직 메시지를 수신할 수 있다는 사실만 (상속 계층도 모름) | 느슨함 |

구체 클래스에 비해 추상 클래스는 메서드의 내부 구현과 자식 클래스의 종류에 대한 지식을 클라이언트에게 숨길 수 있다. 인터페이스에 의존하면 상속 계층을 모르더라도 협력이 가능해진다. **의존하는 대상이 더 추상적일수록 결합도는 더 낮아진다. 이것이 핵심이다.**

### 2.4 명시적인 의존성

아래 코드에는 한 가지 실수로 인해 결합도가 불필요하게 높아졌다:

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Movie {
    private DiscountPolicy discountPolicy;

    public Movie(String title, Duration runningTime, Money fee) {
        // ...
        this.discountPolicy = new AmountDiscountPolicy(...); // 문제!
    }
}
```

</details>

```typescript
// TypeScript
class Movie {
    private discountPolicy: DiscountPolicy;

    constructor(title: string, runningTime: number, fee: Money) {
        // ...
        this.discountPolicy = new AmountDiscountPolicy(/* ... */); // 문제!
    }
}
```

인스턴스 변수 `discountPolicy`는 추상 클래스인 `DiscountPolicy` 타입으로 선언돼 있다. 유연하고 재사용 가능할 것처럼 보인다. 하지만 생성자를 보면 그렇지 않다는 사실을 알 수 있다. 생성자에서 구체 클래스인 `AmountDiscountPolicy`의 인스턴스를 직접 생성해서 대입하고 있다. 따라서 `Movie`는 추상 클래스인 `DiscountPolicy`뿐만 아니라 구체 클래스인 `AmountDiscountPolicy`에도 의존하게 된다.

```
  Movie ─ ─ ─ ─ ▶ DiscountPolicy (인스턴스 변수 타입)
    │
    └ ─ ─ ─ ─ ─ ▶ AmountDiscountPolicy (생성자 내부에서 직접 생성)
```

의존성의 대상을 생성자의 인자로 전달받는 방법과 생성자 안에서 직접 생성하는 방법 사이의 가장 큰 차이점은 **퍼블릭 인터페이스를 통해 할인 정책을 설정할 수 있는 방법을 제공하는지 여부**다.

| 유형 | 설명 | 특징 |
|---|---|---|
| **명시적인 의존성** (*Explicit Dependency*) | 생성자, setter 메서드, 메서드 인자를 통해 의존성이 퍼블릭 인터페이스에 노출됨 | 유연, 재사용 가능 |
| **숨겨진 의존성** (*Hidden Dependency*) | 내부에서 인스턴스를 직접 생성하여 의존성이 퍼블릭 인터페이스에 표현되지 않음 | 경직, 파악 어려움 |

의존성이 명시적이지 않으면 의존성을 파악하기 위해 내부 구현을 직접 살펴볼 수밖에 없다. 커다란 클래스에 정의된 긴 메서드 내부 어딘가에서 인스턴스를 생성하는 코드를 파악하는 것은 쉽지 않을뿐더러 심지어 고통스러울 수도 있다.

더 커다란 문제는 의존성이 명시적이지 않으면 **클래스를 다른 컨텍스트에서 재사용하기 위해 내부 구현을 직접 변경해야 한다**는 것이다.

올바른 해결 방법은 다음과 같다:

```typescript
// TypeScript
class Movie {
    constructor(
        private title: string,
        private runningTime: number,
        private fee: Money,
        private discountPolicy: DiscountPolicy  // 명시적 의존성!
    ) {}
}
```

> **핵심 통찰**: 의존성은 명시적으로 표현돼야 한다. 의존성을 구현 내부에 숨겨두지 마라. 유연하고 재사용 가능한 설계란 퍼블릭 인터페이스를 통해 의존성이 명시적으로 드러나는 설계다. 클래스가 다른 클래스에 의존하는 것은 부끄러운 일이 아니다. 경계해야 할 것은 의존성 자체가 아니라 **의존성을 감추는 것**이다.

### 2.5 new는 해롭다

대부분의 언어에서는 클래스의 인스턴스를 생성할 수 있는 `new` 연산자를 제공한다. 하지만 `new`를 잘못 사용하면 클래스 사이의 결합도가 극단적으로 높아진다. 결합도 측면에서 `new`가 해로운 이유는 크게 두 가지다:

1. **`new` 연산자를 사용하기 위해서는 구체 클래스의 이름을 직접 기술해야 한다.** 따라서 `new`를 사용하는 클라이언트는 추상화가 아닌 구체 클래스에 의존할 수밖에 없기 때문에 결합도가 높아진다.
2. **`new` 연산자는 생성하려는 구체 클래스뿐만 아니라 어떤 인자를 이용해 클래스의 생성자를 호출해야 하는지도 알아야 한다.** 따라서 `new`를 사용하면 클라이언트가 알아야 하는 지식의 양이 늘어나기 때문에 결합도가 높아진다.

`AmountDiscountPolicy`의 인스턴스를 직접 생성하는 `Movie` 클래스의 코드를 좀 더 자세히 살펴보자:

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Movie {
    private DiscountPolicy discountPolicy;

    public Movie(String title, Duration runningTime, Money fee) {
        this.discountPolicy = new AmountDiscountPolicy(
            Money.wons(800),
            new SequenceCondition(1),
            new SequenceCondition(10),
            new PeriodCondition(DayOfWeek.MONDAY,
                LocalTime.of(10, 0), LocalTime.of(11, 59)),
            new PeriodCondition(DayOfWeek.THURSDAY,
                LocalTime.of(10, 0), LocalTime.of(20, 59))
        );
    }
}
```

</details>

```typescript
// TypeScript
class Movie {
    private discountPolicy: DiscountPolicy;

    constructor(title: string, runningTime: number, fee: Money) {
        this.discountPolicy = new AmountDiscountPolicy(
            Money.wons(800),
            new SequenceCondition(1),
            new SequenceCondition(10),
            new PeriodCondition(1, "10:00", "11:59"),  // 월요일
            new PeriodCondition(4, "10:00", "20:59")   // 목요일
        );
    }
}
```

`Movie` 클래스가 `AmountDiscountPolicy`의 인스턴스를 생성하기 위해서는 생성자에 전달되는 인자를 알고 있어야 한다. 엎친 데 덮친 격으로 `AmountDiscountPolicy`의 생성자에서 참조하는 두 구체 클래스인 `SequenceCondition`과 `PeriodCondition`에도 의존하도록 만든다. 그리고 다시 이 두 클래스의 인스턴스를 생성하는 데 필요한 인자들의 정보에 대해서도 `Movie`를 결합시킨다.

```
  Movie ─ ─ ─ ─ ─ ─ ─ ─ ▶ DiscountPolicy
    │
    ├──▶ AmountDiscountPolicy   (구체 클래스)
    ├──▶ SequenceCondition      (구체 클래스)
    └──▶ PeriodCondition        (구체 클래스)
```

**해결 방법은 인스턴스를 생성하는 로직과 생성된 인스턴스를 사용하는 로직을 분리하는 것이다.** `Movie`는 인스턴스를 생성해서는 안 된다. 단지 해당하는 인스턴스를 사용하기만 해야 한다. 이를 위해 `Movie`는 외부로부터 이미 생성된 인스턴스를 전달받아야 한다.

```typescript
// TypeScript
// Movie는 사용만 한다
class Movie {
    constructor(
        private title: string,
        private runningTime: number,
        private fee: Money,
        private discountPolicy: DiscountPolicy  // 외부에서 전달받음
    ) {}
}

// 생성의 책임은 클라이언트에게
const avatar = new Movie("아바타", 120, Money.wons(10000),
    new AmountDiscountPolicy(
        Money.wons(800),
        new SequenceCondition(1),
        new SequenceCondition(10),
        new PeriodCondition(1, "10:00", "11:59"),
        new PeriodCondition(4, "10:00", "20:59")
    )
);
```

사용과 생성의 책임을 분리해서 `Movie`의 결합도를 낮추면 설계를 유연하게 만들 수 있다. `Movie`의 생성자가 구체 클래스인 `AmountDiscountPolicy`가 아니라 추상 클래스인 `DiscountPolicy`를 인자로 받아들이도록 선언돼 있다는 점에 주목하라. 생성의 책임을 클라이언트로 옮김으로써 이제 `Movie`는 `DiscountPolicy`의 모든 자식 클래스와 협력할 수 있게 됐다.

> **핵심 통찰**: 사용과 생성의 책임을 분리하고, 의존성을 생성자에 명시적으로 드러내고, 구체 클래스가 아닌 추상 클래스에 의존하게 함으로써 설계를 유연하게 만들 수 있다. 그리고 그 출발은 **객체를 생성하는 책임을 객체 내부가 아니라 클라이언트로 옮기는 것**에서 시작한다. 이 예제는 올바른 객체가 올바른 책임을 수행하게 하는 것이 훌륭한 설계를 창조하는 기반이라는 사실을 잘 보여준다.

### 2.6 가끔은 생성해도 무방하다

클래스 안에서 객체의 인스턴스를 직접 생성하는 방식이 유용한 경우도 있다. 주로 **협력하는 기본 객체를 설정하고 싶은 경우**가 여기에 속한다.

예를 들어, `Movie`가 대부분의 경우에는 `AmountDiscountPolicy`의 인스턴스와 협력하고 가끔씩만 `PercentDiscountPolicy`의 인스턴스와 협력한다고 가정해 보자. 이런 상황에서 모든 경우에 인스턴스를 생성하는 책임을 클라이언트로 옮긴다면 클라이언트들 사이에 중복 코드가 늘어나고 `Movie`의 사용성도 나빠질 것이다.

이 문제를 해결하는 방법은 **기본 객체를 생성하는 생성자를 추가하고 이 생성자에서 `DiscountPolicy`의 인스턴스를 인자로 받는 생성자를 체이닝하는 것**이다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Movie {
    private DiscountPolicy discountPolicy;

    public Movie(String title, Duration runningTime, Money fee) {
        this(title, runningTime, fee, new AmountDiscountPolicy(...));
    }

    public Movie(String title, Duration runningTime, Money fee,
                 DiscountPolicy discountPolicy) {
        // ...
        this.discountPolicy = discountPolicy;
    }
}
```

</details>

```typescript
// TypeScript
class Movie {
    private discountPolicy: DiscountPolicy;

    constructor(title: string, runningTime: number, fee: Money);
    constructor(title: string, runningTime: number, fee: Money,
                discountPolicy: DiscountPolicy);
    constructor(
        private title: string,
        private runningTime: number,
        private fee: Money,
        discountPolicy?: DiscountPolicy
    ) {
        this.discountPolicy = discountPolicy
            ?? new AmountDiscountPolicy(/* 기본값 */);
    }
}
```

첫 번째 생성자의 내부에서 두 번째 생성자를 호출한다(생성자 체이닝). 클라이언트는 대부분의 경우에 간략한 생성자를 통해 `AmountDiscountPolicy`의 인스턴스와 협력하면서도, 컨텍스트에 적절한 `DiscountPolicy`의 인스턴스로 의존성을 교체할 수 있다.

이 방법은 메서드를 오버로딩하는 경우에도 사용할 수 있다:

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Movie {
    public Money calculateMovieFee(Screening screening) {
        return calculateMovieFee(screening, new AmountDiscountPolicy(...));
    }

    public Money calculateMovieFee(Screening screening,
                                   DiscountPolicy discountPolicy) {
        return fee.minus(discountPolicy.calculateDiscountAmount(screening));
    }
}
```

</details>

```typescript
// TypeScript
class Movie {
    calculateMovieFee(screening: Screening): Money;
    calculateMovieFee(screening: Screening,
                      discountPolicy: DiscountPolicy): Money;
    calculateMovieFee(screening: Screening,
                      discountPolicy?: DiscountPolicy): Money {
        const policy = discountPolicy
            ?? new AmountDiscountPolicy(/* 기본값 */);
        return this.fee.minus(policy.calculateDiscountAmount(screening));
    }
}
```

이 예는 **설계가 트레이드오프 활동**이라는 사실을 다시 한번 상기시킨다. 여기서 트레이드오프의 대상은 결합도와 사용성이다. 구체 클래스에 의존하게 되더라도 클래스의 사용성이 더 중요하다면 결합도를 높이는 방향으로 코드를 작성할 수 있다. 그럼에도 가급적 구체 클래스에 대한 의존성을 제거할 수 있는 방법을 찾아보기 바란다. 종종 모든 결합도가 모이는 새로운 클래스를 추가함으로써 사용성과 유연성이라는 두 마리 토끼를 잡을 수 있는 경우도 있다. 9장에서 살펴볼 **FACTORY**가 바로 그런 경우다.

### 2.7 표준 클래스에 대한 의존은 해롭지 않다

의존성이 불편한 이유는 그것이 항상 변경에 대한 영향을 암시하기 때문이다. 따라서 **변경될 확률이 거의 없는 클래스라면 의존성이 문제가 되지 않는다.** 자바라면 JDK에 포함된 표준 클래스가 이 부류에 속한다. TypeScript라면 빌트인 객체(`Array`, `Map`, `Set` 등)가 해당한다. 이런 클래스들에 대해서는 구체 클래스에 의존하거나 직접 인스턴스를 생성하더라도 문제가 없다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public abstract class DiscountPolicy {
    private List<DiscountCondition> conditions = new ArrayList<>();
}
```

</details>

```typescript
// TypeScript
abstract class DiscountPolicy {
    private conditions: DiscountCondition[] = [];  // 직접 생성해도 OK
}
```

비록 클래스를 직접 생성하더라도 가능한 한 추상적인 타입을 사용하는 것이 확장성 측면에서 유리하다. 위 Java 코드에서 `conditions`의 타입으로 인터페이스인 `List`를 사용한 것은 이 때문이다. 이렇게 하면 다양한 `List` 타입의 객체로 `conditions`를 대체할 수 있게 설계의 유연성을 높일 수 있다.

따라서 **의존성에 의한 영향이 적은 경우에도 추상화에 의존하고 의존성을 명시적으로 드러내는 것은 좋은 설계 습관이다.**

---

## 3. 컨텍스트 확장하기

`Movie`의 설계가 유연하고 재사용 가능한 이유를 실제로 입증하기 위해 지금까지와는 다른 컨텍스트에서 `Movie`를 확장해서 재사용하는 두 가지 예를 살펴보겠다.

### 3.1 할인 혜택을 제공하지 않는 영화

쉽게 생각할 수 있는 방법은 `discountPolicy`에 `null` 값을 할당하는 것이다:

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Movie {
    public Movie(String title, Duration runningTime, Money fee) {
        this(title, runningTime, fee, null);
    }

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
    constructor(title: string, runningTime: number, fee: Money) {
        // discountPolicy = null
    }

    calculateMovieFee(screening: Screening): Money {
        if (this.discountPolicy === null) {  // 예외 케이스!
            return this.fee;
        }
        return this.fee.minus(
            this.discountPolicy.calculateDiscountAmount(screening)
        );
    }
}
```

이 코드는 제대로 동작하지만 한 가지 문제가 있다. 지금까지의 `Movie`와 `DiscountPolicy` 사이의 **협력 방식에 어긋나는 예외 케이스가 추가된 것**이다. 그리고 이 예외 케이스를 처리하기 위해 `Movie`의 내부 코드를 직접 수정해야 했다. 어떤 경우든 코드 내부를 직접 수정하는 것은 버그의 발생 가능성을 높이는 것이라는 점을 기억하라.

**해결책은 할인 정책이 존재하지 않는다는 사실을 예외 케이스로 처리하지 말고 기존에 `Movie`와 `DiscountPolicy`가 협력하던 방식을 따르도록 만드는 것이다.** 다시 말해 할인 정책이 존재하지 않는다는 사실을 **할인 정책의 한 종류**로 간주하는 것이다.

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
    protected getDiscountAmount(screening: Screening): Money {
        return Money.ZERO;
    }
}
```

이제 `Movie` 클래스에 특별한 `if` 문을 추가하지 않고도 할인 혜택을 제공하지 않는 영화를 구현할 수 있다. 간단히 `NoneDiscountPolicy`의 인스턴스를 `Movie`의 생성자에 전달하면 되는 것이다.

```typescript
// TypeScript
const avatar = new Movie("아바타", 120, Money.wons(10000),
    new NoneDiscountPolicy());
```

### 3.2 중복 할인 정책

두 번째 예는 금액 할인 정책과 비율 할인 정책을 혼합해서 적용할 수 있는 **중복 할인 정책**을 구현하는 것이다.

가장 간단하게 구현할 수 있는 방법은 `Movie`가 `DiscountPolicy`의 인스턴스들로 구성된 `List`를 인스턴스 변수로 갖게 하는 것이다. 하지만 이 방법은 중복 할인 정책을 구현하기 위해 기존의 할인 정책의 협력 방식과는 다른 **예외 케이스를 추가**하게 만든다.

이 문제 역시 같은 방법으로 해결할 수 있다. **중복 할인 정책을 할인 정책의 한 가지로 간주하는 것이다.** 중복 할인 정책을 구현하는 `OverlappedDiscountPolicy`를 `DiscountPolicy`의 자식 클래스로 만들면 기존의 `Movie`와 `DiscountPolicy` 사이의 협력 방식을 수정하지 않고도 여러 개의 할인 정책을 적용할 수 있다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class OverlappedDiscountPolicy extends DiscountPolicy {
    private List<DiscountPolicy> discountPolicies = new ArrayList<>();

    public OverlappedDiscountPolicy(DiscountPolicy... discountPolicies) {
        this.discountPolicies = Arrays.asList(discountPolicies);
    }

    @Override
    protected Money getDiscountAmount(Screening screening) {
        Money result = Money.ZERO;
        for (DiscountPolicy each : discountPolicies) {
            result = result.plus(each.calculateDiscountAmount(screening));
        }
        return result;
    }
}
```

</details>

```typescript
// TypeScript
class OverlappedDiscountPolicy extends DiscountPolicy {
    private discountPolicies: DiscountPolicy[];

    constructor(...discountPolicies: DiscountPolicy[]) {
        super();
        this.discountPolicies = discountPolicies;
    }

    protected getDiscountAmount(screening: Screening): Money {
        return this.discountPolicies.reduce(
            (result, policy) =>
                result.plus(policy.calculateDiscountAmount(screening)),
            Money.ZERO
        );
    }
}
```

이제 `OverlappedDiscountPolicy`의 인스턴스를 생성해서 `Movie`에 전달하는 것만으로도 중복 할인을 쉽게 적용할 수 있다.

```typescript
// TypeScript
const avatar = new Movie("아바타", 120, Money.wons(10000),
    new OverlappedDiscountPolicy(
        new AmountDiscountPolicy(/* ... */),
        new PercentDiscountPolicy(/* ... */)
    )
);
```

```
  [Movie의 컨텍스트 확장]

  Movie ─ ─ ─ ▶ DiscountPolicy (추상)
                      △
              ┌───────┼───────┬──────────┐
              │       │       │          │
          Amount   Percent   None    Overlapped
          Discount Discount Discount  Discount
          Policy   Policy   Policy    Policy
                                       │
                                       ├──▶ Amount...
                                       └──▶ Percent...
```

이 예제는 `Movie`를 수정하지 않고도 할인 정책을 적용하지 않는 새로운 기능을 추가하는 것이 얼마나 간단한지를 잘 보여준다. 우리는 단지 원하는 기능을 구현한 `DiscountPolicy`의 자식 클래스를 추가하고 이 클래스의 인스턴스를 `Movie`에 전달하기만 하면 된다.

설계를 유연하게 만들 수 있었던 이유는 `Movie`가 `DiscountPolicy`라는 추상화에 의존하고, 생성자를 통해 `DiscountPolicy`에 대한 의존성을 명시적으로 드러냈으며, `new`와 같이 구체 클래스를 직접적으로 다뤄야 하는 책임을 `Movie` 외부로 옮겼기 때문이다.

> **핵심 통찰**: 결합도를 낮춤으로써 얻게 되는 **컨텍스트의 확장**이라는 개념이 유연하고 재사용 가능한 설계를 만드는 핵심이다. 추상화에 자식 클래스를 추가함으로써 간단하게 `Movie`가 사용될 컨텍스트를 확장할 수 있었다.

---

## 4. 조합 가능한 행동

다양한 종류의 할인 정책이 필요한 컨텍스트에서 `Movie`를 재사용할 수 있었던 이유는 **코드를 직접 수정하지 않고도 협력 대상인 `DiscountPolicy` 인스턴스를 교체할 수 있었기 때문이다.**

- 비율 할인 정책이 필요한가? → `PercentDiscountPolicy`의 인스턴스를 `Movie`에 연결하면 된다.
- 금액 할인 정책이 필요한가? → `AmountDiscountPolicy`의 인스턴스를 끼워 넣으면 된다.
- 중복 할인을 원하는가? → `OverlappedDiscountPolicy`를 조합하라.
- 할인을 제공하고 싶지 않다면? → `NoneDiscountPolicy`의 인스턴스를 전달하면 된다.

어떤 `DiscountPolicy`의 인스턴스를 `Movie`에 연결하느냐에 따라 `Movie`의 행동이 달라진다.

**유연하고 재사용 가능한 설계는 응집도 높은 책임들을 가진 작은 객체들을 다양한 방식으로 연결함으로써 애플리케이션의 기능을 쉽게 확장할 수 있다.** 유연하고 재사용 가능한 설계는 객체가 어떻게(how) 하는지를 장황하게 나열하지 않고도 객체들의 조합을 통해 **무엇(what)을 하는지**를 표현하는 클래스들로 구성된다.

따라서 클래스의 인스턴스를 생성하는 코드를 보는 것만으로 객체가 어떤 일을 하는지를 쉽게 파악할 수 있다. 코드에 드러난 로직을 해석할 필요 없이 객체가 어떤 객체와 연결됐는지를 보는 것만으로도 객체의 행동을 쉽게 예상하고 이해할 수 있기 때문이다. 다시 말해 **선언적으로 객체의 행동을 정의할 수 있는 것**이다.

아래 코드를 읽는 것만으로도 "첫 번째 상영, 10번째 상영, 월요일 10시부터 12시 사이 상영, 목요일 10시부터 21시 상영의 경우에는 800원을 할인해 준다"는 사실을 쉽게 이해할 수 있다:

```typescript
// TypeScript
new Movie("아바타", 120, Money.wons(10000),
    new AmountDiscountPolicy(
        Money.wons(800),
        new SequenceCondition(1),
        new SequenceCondition(10),
        new PeriodCondition(1, "10:00", "12:00"),
        new PeriodCondition(4, "10:00", "21:00")
    )
);
```

그리고 인자를 변경하는 것만으로도 새로운 할인 정책과 할인 조건을 적용할 수 있다는 것 역시 알 수 있을 것이다.

---

## 설계 원칙

| 원칙 | 핵심 내용 | 효과 |
|---|---|---|
| **추상화에 의존하라** | 구체 클래스보다 추상 클래스, 추상 클래스보다 인터페이스에 의존하라 | 결합도 감소, 다양한 컨텍스트에서 재사용 |
| **의존성을 명시적으로 드러내라** | 생성자, setter, 메서드 인자를 통해 의존성을 퍼블릭 인터페이스에 노출하라 | 파악 용이, 유연한 교체 |
| **new는 해롭다** | 인스턴스를 생성하는 로직과 사용하는 로직을 분리하라 | 구체 클래스에 대한 불필요한 결합 제거 |
| **컨텍스트 독립성** | 클래스가 실행될 컨텍스트에 대한 구체적인 정보를 최소화하라 | 다양한 컨텍스트에서 재사용 가능 |
| **사용과 생성의 분리** | 객체를 생성하는 책임은 클라이언트에게, 사용하는 책임만 객체에게 | 유연한 설계의 출발점 |

---

## 요약

- 잘 설계된 객체지향 애플리케이션은 작고 응집도 높은 객체들의 협력으로 구성된다. 협력은 필수적이지만 과도한 협력은 **과도한 의존성**을 낳고 변경을 어렵게 만든다.
- **의존성**은 한 요소가 다른 요소의 변경에 영향을 받을 수 있는 가능성이다. 의존성은 방향성을 가지며 항상 단방향이다.
- 의존성은 **전이**될 수 있다. 직접 의존성은 코드에 명시적으로 드러나지만, 간접 의존성은 의존성 전이에 의해 발생한다. 캡슐화가 전이를 차단하는 핵심 무기다.
- **런타임 의존성**과 **컴파일타임 의존성**은 다를 수 있으며, 유연한 설계를 위해서는 이 둘을 서로 다르게 만들어야 한다. 컴파일타임 구조와 런타임 구조 사이의 거리가 멀수록 설계가 유연해진다.
- **컨텍스트 독립성**: 클래스가 사용될 특정한 문맥에 대해 최소한의 가정만으로 이루어져 있을수록 다른 문맥에서 재사용하기 쉽다.
- 의존성을 해결하는 세 가지 방법은 **생성자 주입**, **setter 메서드**, **메서드 인자**다. 가장 선호되는 방법은 생성자 주입과 setter 메서드를 혼합하는 것이다.
- **결합도**는 의존성의 정도를 나타내는 척도다. 바람직한 의존성(느슨한 결합도)은 다양한 환경에서 재사용을 가능하게 하고, 바람직하지 못한 의존성(강한 결합도)은 특정 컨텍스트에 강하게 묶는다.
- 결합도를 느슨하게 유지하려면 **추상화에 의존**해야 한다. 구체 클래스 → 추상 클래스 → 인터페이스 순으로 결합도가 낮아진다.
- 의존성은 **명시적으로 드러내야** 한다. 숨겨진 의존성은 파악하기 어렵고 재사용을 위해 내부 구현을 변경해야 하는 위험을 초래한다.
- `new`는 구체 클래스에 대한 결합도를 극단적으로 높이므로, **사용과 생성의 책임을 분리**해야 한다.
- 유연하고 재사용 가능한 설계는 객체들의 **조합**을 통해 행동을 정의한다. 어떤 객체와 협력하느냐에 따라 객체의 행동이 달라지는 것이 유연한 설계의 특징이다.

---

## 다른 챕터와의 관계

- **Chapter 1 (객체, 설계)**: 1장에서 Theater의 의존성을 줄이기 위해 Audience와 TicketSeller로 책임을 분산시킨 것이 사실은 이 장에서 설명하는 의존성 관리 원칙(명시적인 의존성, 추상화에 의존, 컨텍스트 독립성)을 직관적으로 적용한 결과였다.
- **Chapter 2 (객체지향 프로그래밍)**: 2장에서 Movie가 DiscountPolicy 추상 클래스에 의존하고 런타임에 AmountDiscountPolicy나 PercentDiscountPolicy와 협력하도록 설계한 것이 이 장의 핵심 주제인 "런타임 의존성과 컴파일타임 의존성의 분리"에 해당한다. NoneDiscountPolicy와 OverlappedDiscountPolicy의 예제도 2장의 설계를 확장한 것이다.
- **Chapter 4 (설계 품질과 트레이드오프)**: 4장의 데이터 중심 설계가 변경에 취약했던 근본 원인은 이 장에서 설명하는 강한 결합도, 숨겨진 의존성, 구체 클래스에 대한 직접 의존 때문이다.
- **Chapter 5 (책임 할당하기)**: 5장의 GRASP 패턴 중 "Creator" 패턴이 이 장의 "사용과 생성의 분리" 원칙과 밀접하게 연관된다. 누가 인스턴스를 생성할 것인가라는 문제는 의존성 관리의 핵심 질문이다.
- **Chapter 9 (유연한 설계)**: 이 장에서 다룬 의존성 관리 원칙을 더 깊이 발전시켜 개방-폐쇄 원칙(OCP), 의존성 역전 원칙(DIP), FACTORY 패턴 등 유연한 설계를 위한 고급 기법을 소개한다. 특히 이 장에서 언급한 "사용성과 유연성의 트레이드오프"를 해결하는 FACTORY가 9장의 핵심 주제 중 하나다.
