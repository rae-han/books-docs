# Chapter 15: Design Patterns and Frameworks (디자인 패턴과 프레임워크)

## 핵심 질문

디자인 패턴은 어떻게 설계를 재사용하는가? 프레임워크는 설계와 코드를 어떻게 함께 재사용하는가? STRATEGY, TEMPLATE METHOD, DECORATOR 패턴은 각각 어떤 변경을 캡슐화하며, 제어 역전(IoC)은 프레임워크의 재사용성과 어떤 관계인가?

---

## 1. 디자인 패턴과 설계 재사용

### 1.1 소프트웨어 패턴

워드 커닝험(Ward Cunningham)과 켄트 벡(Kent Beck)이 크리스토퍼 알렉산더(Christopher Alexander)의 패턴 개념을 소프트웨어 개발 커뮤니티에 소개한 이후, 패턴은 소프트웨어 개발에서 중요한 화두가 되어 왔다. GoF가 저술한 《GoF의 디자인 패턴》[GOF94]에 의해 패턴이 대중화된 이후 수많은 저작물이 쏟아져 나왔다.

패턴에 관해 반복적으로 언급되는 핵심적인 특징이 있다:

- 패턴은 반복적으로 발생하는 **문제와 해법의 쌍**으로 정의된다 [Buschman96]
- 패턴을 사용함으로써 이미 알려진 문제와 해법을 문서로 정리하고, 이 지식을 다른 사람과 **의사소통**할 수 있다 [Alur03]
- 패턴은 추상적인 원칙과 실제 코드 작성 사이의 **간극을 메워 주며** 실질적인 코드 작성을 돕는다 [Beck07]
- 패턴의 요점은 패턴이 **실무에서 탄생**했다는 점이다 [Fowler02]

마틴 파울러(Martin Fowler)의 패턴 정의가 이 모든 특징을 함축한다:

> 내가 사용하는 패턴 정의는 하나의 실무 컨텍스트(practical context)에서 유용하게 사용해 왔고 다른 실무 컨텍스트에서도 유용할 것이라고 예상되는 아이디어(idea)다. [Fowler96]

패턴은 한 컨텍스트에서 유용한 동시에 다른 컨텍스트에서도 유용한 '아이디어'다. 일반적으로 패턴으로 인정하기 위한 조건으로 **3의 규칙**(Rule of Three) [Alur03]을 언급한다. 이 규칙에 따르면 최소 세 가지의 서로 다른 시스템에 특별한 문제 없이 적용할 수 있고 유용한 경우에만 패턴으로 간주할 수 있다.

> **핵심 통찰**: 패턴이 지닌 가장 큰 가치는 **경험을 통해 축적된 실무 지식을 효과적으로 요약하고 전달할 수 있다는 점**이다. 패턴은 치열한 실무 현장의 역학 관계 속에서 검증되고 입증된 자산이다. 실무 경험이 적은 초보자라 하더라도 패턴을 익히고 반복적으로 적용하는 과정에서 유연하고 품질 높은 소프트웨어를 개발하는 방법을 익힐 수 있다.

패턴에서 가장 중요한 요소는 패턴의 **'이름'**이다. 패턴의 이름은 커뮤니티가 공유할 수 있는 중요한 어휘집을 제공한다. "인터페이스를 하나 추가하고 이 인터페이스를 구체화하는 클래스를 만든 후 객체의 생성자나 setter 메서드에 할당해서 런타임 시에 알고리즘을 바꿀 수 있게 하자"는 장황한 대화가 "**STRATEGY 패턴을 적용하자**"는 단순한 대화로 바뀐다. 패턴의 이름은 높은 수준의 대화를 가능하게 하는 원천이다.

패턴은 홀로 존재하지 않는다. 특정 패턴 내에 포함된 컴포넌트와 컴포넌트 간의 관계는 더 작은 패턴에 의해 서술될 수 있으며, 패턴들을 포함하는 더 큰 패턴 내에 통합될 수 있다. 크리스토퍼 알렉산더는 연관된 패턴들의 집합들이 모여 하나의 **패턴 언어**(Pattern Language)를 구성한다고 정의한다.

### 1.2 패턴 분류

패턴을 분류하는 가장 일반적인 방법은 범위나 적용 단계에 따라 4가지로 나누는 것이다:

| 분류 | 범위 | 특징 | 언어 독립성 |
|---|---|---|---|
| **아키텍처 패턴** | 시스템 전체 구조 | 서브시스템들의 책임 정의, 관계 조직화 규칙 제공 | 독립적 |
| **디자인 패턴** | 중간 규모 | 특정 설계 문제 해결, 협력하는 컴포넌트 간의 반복 구조 서술 | 독립적 |
| **분석 패턴** | 도메인 개념 | 업무 모델링 시 발견되는 공통 구조 표현 | 독립적 |
| **이디엄** | 언어별 하위 레벨 | 특정 언어의 기능을 사용해 컴포넌트 구현 방법 서술 | **종속적** |

이디엄은 특정 프로그래밍 언어에 국한된 하위 레벨 패턴이다. 예를 들어, C++의 COUNT POINTER 이디엄(참조되지 않는 객체를 스스로 삭제)은 가비지 컬렉션 메커니즘을 가진 자바에서는 유용하지 않다.

### 1.3 패턴과 책임-주도 설계

객체지향 설계에서 가장 중요한 일은 올바른 책임을 올바른 객체에게 할당하고 객체 간의 유연한 협력 관계를 구축하는 일이다. 패턴은 공통으로 사용할 수 있는 **역할, 책임, 협력의 템플릿**이다.

- **STRATEGY 패턴**: 다양한 알고리즘을 동적으로 교체할 수 있는 역할과 책임의 집합을 제공한다
- **BRIDGE 패턴**: 추상화의 조합으로 인한 클래스의 폭발적인 증가 문제를 해결하기 위해, 역할과 책임을 추상화와 구현의 두 개의 커다란 집합으로 분해함으로써 설계를 확장 가능하게 만든다
- **OBSERVER 패턴**: 유연한 통지 메커니즘을 구축하기 위해 객체 간의 결합도를 낮출 수 있는 역할과 책임의 집합을 제공한다

> **핵심 통찰**: 패턴의 구성 요소는 **클래스가 아니라 '역할'**이다. 디자인 패턴의 구성 요소가 클래스와 메서드가 아니라 역할과 책임이라는 사실을 이해하는 것이 중요하다. 어떤 구현 코드가 어떤 디자인 패턴을 따른다고 이야기할 때는 역할, 책임, 협력의 관점에서 유사성을 공유한다는 것이지 특정한 구현 방식을 강제하는 것은 아니다.

COMPOSITE 패턴을 예로 들어 보자. 《GoF의 디자인 패턴》에 수록된 COMPOSITE 패턴의 구성 요소인 Component, Composite, Leaf는 클래스가 아니라 **협력에 참여하는 객체들의 역할**이다.

```
                       COMPOSITE 패턴의 일반 구조
┌──────────┐        ┌───────────────────┐
│  Client  │───────▶│    Component      │◀────── children
│          │        │  + operation()    │
└──────────┘        └─────────┬─────────┘
                        ┌─────┴─────┐
               ┌────────┴──┐   ┌────┴──────────────┐
               │   Leaf    │   │    Composite       │
               │ operation │   │ operation()        │
               └───────────┘   │ add(Component)     │
                               │ remove(Component)  │
                               └────────────────────┘
```

역할이라는 사실은 패턴 템플릿을 구현할 수 있는 다양한 방법이 존재함을 암시한다:

**방법 1: 하나의 클래스가 여러 역할 수행** — 하나의 `TagNode` 클래스가 Component, Composite, Leaf 역할 모두를 수행할 수 있다.

**방법 2: 다수의 클래스가 동일한 역할 수행** — 8장에서 살펴본 중복 할인 정책에서, `OverlappedDiscountPolicy`는 Composite 역할을, `AmountDiscountPolicy`와 `PercentDiscountPolicy`가 Leaf 역할을 수행한다. 서로 다른 두 클래스가 동일한 Leaf라는 역할을 수행한다.

```
                  영화 예매 시스템의 COMPOSITE 패턴
                 ┌──────────────────────────┐
                 │   DiscountPolicy         │ ◀── Component 역할
  ┌──────────┐   │   + calculateDiscount()  │
  │  Movie   │──▶│                          │
  └──────────┘   └────────────┬─────────────┘
                      ┌───────┼───────┐
                      ▼       ▼       ▼
              ┌──────────┐ ┌──────────┐ ┌───────────────────┐
              │ Amount   │ │ Percent  │ │ Overlapped        │
              │ Discount │ │ Discount │ │ DiscountPolicy    │
              │ Policy   │ │ Policy   │ │                   │
              └──────────┘ └──────────┘ └───────────────────┘
               Leaf 역할    Leaf 역할      Composite 역할
```

---

## 2. 캡슐화와 디자인 패턴

대부분의 디자인 패턴은 협력을 일관성 있고 유연하게 만드는 것을 목적으로 한다. 따라서 각 디자인 패턴은 **특정한 변경을 캡슐화하기 위한 독자적인 방법**을 정의하고 있다. 디자인 패턴에서 중요한 것은 구현 방법이나 구조가 아니라, **어떤 변경을 캡슐화하는지**를 이해하는 것이다.

### 2.1 STRATEGY 패턴: 알고리즘 변경을 캡슐화

영화 예매 시스템에서 `Movie`가 `DiscountPolicy` 상속 계층을 합성 관계로 유지하는 설계는 사실 **STRATEGY 패턴**을 적용한 것이다. STRATEGY 패턴의 목적은 **알고리즘의 변경을 캡슐화**하는 것이고, 이를 구현하기 위해 **객체 합성**을 이용한다.

```
                      STRATEGY 패턴에 기반한 설계
  ┌──────────┐       ┌──────────────────────────┐
  │  Movie   │──────▶│   DiscountPolicy         │ ◀── 추상 Strategy
  │          │       │   + calculateDiscount()  │
  └──────────┘       └────────────┬─────────────┘
                          ┌───────┴───────┐
                          ▼               ▼
                  ┌──────────────┐ ┌──────────────┐
                  │  Amount      │ │  Percent     │
                  │  Discount    │ │  Discount    │
                  │  Policy      │ │  Policy      │
                  └──────────────┘ └──────────────┘
                   Concrete Strategy  Concrete Strategy
```

영화에 적용될 할인 정책의 종류는 `Movie`가 참조하는 `DiscountPolicy`의 서브클래스가 무엇이냐에 따라 결정된다. STRATEGY 패턴을 이용하면 `Movie`와 `DiscountPolicy` 사이의 결합도를 낮게 유지할 수 있기 때문에 **런타임에 알고리즘을 변경할 수 있다**.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Movie {
    private DiscountPolicy discountPolicy;

    public Movie(String title, Duration runningTime, Money fee,
                 DiscountPolicy discountPolicy) {
        this.discountPolicy = discountPolicy;
    }

    public Money calculateMovieFee(Screening screening) {
        return fee.minus(discountPolicy.calculateDiscountAmount(screening));
    }

    // 런타임에 알고리즘 교체 가능
    public void changeDiscountPolicy(DiscountPolicy discountPolicy) {
        this.discountPolicy = discountPolicy;
    }
}
```

</details>

```typescript
// TypeScript
class Movie {
    private discountPolicy: DiscountPolicy;

    constructor(
        private title: string,
        private runningTime: number,
        private fee: Money,
        discountPolicy: DiscountPolicy,
    ) {
        this.discountPolicy = discountPolicy;
    }

    calculateMovieFee(screening: Screening): Money {
        return this.fee.minus(
            this.discountPolicy.calculateDiscountAmount(screening),
        );
    }

    // 런타임에 알고리즘 교체 가능
    changeDiscountPolicy(discountPolicy: DiscountPolicy): void {
        this.discountPolicy = discountPolicy;
    }
}
```

### 2.2 TEMPLATE METHOD 패턴: 상속을 이용한 알고리즘 캡슐화

변경을 캡슐화하는 방법이 합성만 있는 것은 아니다. **상속**을 이용할 수도 있다. 알고리즘을 캡슐화하기 위해 합성 관계가 아닌 **상속 관계를 사용하는 것**을 TEMPLATE METHOD 패턴이라고 부른다.

```
                   TEMPLATE METHOD 패턴에 기반한 설계
              ┌─────────────────────────────────────┐
              │            Movie                    │
              │  + calculateFee()                   │──── 변하지 않는 부분
              │  # calculateDiscountAmount()  {추상} │     (부모 클래스)
              └──────────────────┬──────────────────┘
                      ┌──────────┴──────────┐
                      ▼                     ▼
         ┌──────────────────────┐  ┌──────────────────────┐
         │  AmountDiscountMovie │  │  PercentDiscountMovie │
         │  # calculateDiscount │  │  # calculateDiscount  │  변하는 부분
         │    Amount()          │  │    Amount()           │  (자식 클래스)
         └──────────────────────┘  └───────────────────────┘
```

변하지 않는 부분은 부모 클래스로, 변하는 부분은 자식 클래스로 분리함으로써 변경을 캡슐화한다. 부모 클래스의 `calculateFee` 메서드 안에서 추상 메서드인 `calculateDiscountAmount`를 호출하고, 자식 클래스들이 이 메서드를 오버라이딩해서 변하는 부분을 구현한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public abstract class Movie {
    private String title;
    private Money fee;

    public Money calculateFee(Screening screening) {
        // 변하지 않는 부분: 기본 알고리즘 구조
        return fee.minus(calculateDiscountAmount(screening));
    }

    // 변하는 부분: 자식 클래스에서 구현
    protected abstract Money calculateDiscountAmount(Screening screening);
}

public class AmountDiscountMovie extends Movie {
    private Money discountAmount;

    @Override
    protected Money calculateDiscountAmount(Screening screening) {
        return discountAmount;
    }
}

public class PercentDiscountMovie extends Movie {
    private double percent;

    @Override
    protected Money calculateDiscountAmount(Screening screening) {
        return getFee().times(percent);
    }
}
```

</details>

```typescript
// TypeScript
abstract class Movie {
    constructor(
        private title: string,
        private fee: Money,
    ) {}

    // 변하지 않는 부분: 기본 알고리즘 구조
    calculateFee(screening: Screening): Money {
        return this.fee.minus(this.calculateDiscountAmount(screening));
    }

    protected getFee(): Money {
        return this.fee;
    }

    // 변하는 부분: 자식 클래스에서 구현
    protected abstract calculateDiscountAmount(screening: Screening): Money;
}

class AmountDiscountMovie extends Movie {
    constructor(
        title: string,
        fee: Money,
        private discountAmount: Money,
    ) {
        super(title, fee);
    }

    protected calculateDiscountAmount(screening: Screening): Money {
        return this.discountAmount;
    }
}

class PercentDiscountMovie extends Movie {
    constructor(
        title: string,
        fee: Money,
        private percent: number,
    ) {
        super(title, fee);
    }

    protected calculateDiscountAmount(screening: Screening): Money {
        return this.getFee().times(this.percent);
    }
}
```

TEMPLATE METHOD 패턴은 부모 클래스가 알고리즘의 기본 구조를 정의하고 구체적인 단계는 자식 클래스에서 정의하게 함으로써 변경을 캡슐화한다. 다만 합성보다는 결합도가 높은 상속을 사용했기 때문에 STRATEGY 패턴처럼 **런타임에 객체의 알고리즘을 변경하는 것은 불가능**하다. 하지만 알고리즘 교체 같은 요구사항이 없다면 상대적으로 STRATEGY 패턴보다 **복잡도를 낮출 수 있다**는 장점이 있다.

### 2.3 DECORATOR 패턴: 선택적 행동의 조합을 캡슐화

핸드폰 과금 시스템의 설계는 **DECORATOR 패턴**을 기반으로 한다. DECORATOR 패턴은 객체의 행동을 동적으로 추가할 수 있게 해 주는 패턴으로서, 기본적으로 객체의 행동을 결합하기 위해 **객체 합성**을 사용한다. DECORATOR 패턴은 **선택적인 행동의 개수와 순서에 대한 변경을 캡슐화**할 수 있다.

```
               DECORATOR 패턴에 기반한 핸드폰 과금 시스템
  ┌───────┐   ratePolicy   ┌───────────────────┐
  │ Phone │───────────────▶│  <<interface>>     │ ◀── Component
  │       │                │  RatePolicy        │
  └───────┘                │  + calculateFee()  │
                           └─────────┬──────────┘
                               ┌─────┴──────┐
                               ▼            ▼
               ┌─────────────────┐  ┌──────────────────────┐
               │ BasicRatePolicy │  │ AdditionalRatePolicy │ ◀── Decorator
               │                 │  │                      │
               │ + calculateFee()│  │ + calculateFee()     │──── next ──▶ RatePolicy
               │ # calcCallFee() │  │ # afterCalculated()  │
               └─────────────────┘  └──────────┬───────────┘
                ConcreteComponent         ┌─────┴─────┐
                                          ▼           ▼
                              ┌──────────────┐  ┌──────────────────┐
                              │ TaxablePolicy│  │ RateDiscountable │
                              │              │  │ Policy           │
                              └──────────────┘  └──────────────────┘
                              ConcreteDecorator  ConcreteDecorator
```

`BasicRatePolicy`(기본 정책)는 ConcreteComponent 역할을, `AdditionalRatePolicy`(부가 정책)는 Decorator 역할을 수행한다. `TaxablePolicy`와 `RateDiscountablePolicy`는 ConcreteDecorator 역할이다. Decorator가 내부에 `next`라는 이름으로 다른 `RatePolicy`를 참조하기 때문에, 부가 정책을 자유롭게 조합할 수 있다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public interface RatePolicy {
    Money calculateFee(Phone phone);
}

public abstract class BasicRatePolicy implements RatePolicy {
    @Override
    public Money calculateFee(Phone phone) {
        Money result = Money.ZERO;
        for (Call call : phone.getCalls()) {
            result = result.plus(calculateCallFee(call));
        }
        return result;
    }

    protected abstract Money calculateCallFee(Call call);
}

public abstract class AdditionalRatePolicy implements RatePolicy {
    private RatePolicy next;

    public AdditionalRatePolicy(RatePolicy next) {
        this.next = next;
    }

    @Override
    public Money calculateFee(Phone phone) {
        Money fee = next.calculateFee(phone);
        return afterCalculated(fee);
    }

    protected abstract Money afterCalculated(Money fee);
}

public class TaxablePolicy extends AdditionalRatePolicy {
    private double taxRatio;

    public TaxablePolicy(double taxRatio, RatePolicy next) {
        super(next);
        this.taxRatio = taxRatio;
    }

    @Override
    protected Money afterCalculated(Money fee) {
        return fee.plus(fee.times(taxRatio));
    }
}
```

</details>

```typescript
// TypeScript
interface RatePolicy {
    calculateFee(phone: Phone): Money;
}

abstract class BasicRatePolicy implements RatePolicy {
    calculateFee(phone: Phone): Money {
        let result = Money.ZERO;
        for (const call of phone.getCalls()) {
            result = result.plus(this.calculateCallFee(call));
        }
        return result;
    }

    protected abstract calculateCallFee(call: Call): Money;
}

abstract class AdditionalRatePolicy implements RatePolicy {
    constructor(private next: RatePolicy) {}

    calculateFee(phone: Phone): Money {
        const fee = this.next.calculateFee(phone);
        return this.afterCalculated(fee);
    }

    protected abstract afterCalculated(fee: Money): Money;
}

class TaxablePolicy extends AdditionalRatePolicy {
    constructor(
        private taxRatio: number,
        next: RatePolicy,
    ) {
        super(next);
    }

    protected afterCalculated(fee: Money): Money {
        return fee.plus(fee.times(this.taxRatio));
    }
}
```

### 2.4 COMPOSITE 패턴: 객체의 수를 캡슐화

`OverlappedDiscountPolicy`의 예를 통해 살펴본 COMPOSITE 패턴은 **개별 객체와 복합 객체라는 객체의 수와 관련된 변경을 캡슐화**하는 것이 목적이다. `Movie`는 자신과 협력해야 하는 `DiscountPolicy` 인스턴스가 단일 객체인지 복합 객체인지를 알 필요가 없다. 다시 말해서 **협력하는 객체의 수를 변경하더라도 `Movie`에 영향을 미치지 않는다**.

### 2.5 디자인 패턴이 캡슐화하는 변경 요약

| 디자인 패턴 | 캡슐화 대상 | 캡슐화 방법 | 런타임 교체 |
|---|---|---|---|
| **STRATEGY** | 알고리즘의 변경 | 객체 합성(인터페이스 + 위임) | 가능 |
| **TEMPLATE METHOD** | 알고리즘의 변경 | 상속(추상 메서드 오버라이딩) | 불가능 |
| **DECORATOR** | 선택적 행동의 개수와 순서 | 객체 합성(동일 인터페이스 + 위임 체인) | 가능 |
| **COMPOSITE** | 객체의 수(개별 vs 복합) | 객체 합성(트리 구조) | 가능 |

---

## 3. 패턴은 출발점이다

### 3.1 패턴 만능주의의 위험

패턴은 출발점이지 목적지가 아니다. 많은 전문가들은 널리 요구되는 유연성이나 공통적으로 발견되는 특정한 설계 이슈를 해결하기 위해 적절한 디자인 패턴을 이용해 설계를 시작한다. 그러나 패턴은 설계의 **목표**가 돼서는 안 된다. 패턴은 단지 목표로 하는 설계에 이를 수 있는 방향을 제시하는 **나침반**에 불과하다.

패턴을 사용하면서 부딪히게 되는 대부분의 문제는 패턴을 **맹목적으로** 사용할 때 발생한다. 조슈아 케리에브스키(Joshua Kerievsky)는 이를 **'패턴 만능주의'**라고 부른다.

> 패턴에 처음 입문한 사람들은 패턴의 강력함에 매료된 나머지 아무리 사소한 설계라도 패턴을 적용해 보려고 시도한다. 그러나 명확한 트레이드오프 없이 패턴을 남용하면 설계가 불필요하게 복잡해지게 된다.

타당한 이유 없이 패턴을 적용하면 패턴에 익숙한 사람들은 설계의 의도를 이해하지 못하게 되고, 패턴을 알지 못하는 사람들은 불필요하게 복잡한 설계를 따라가느라 시간을 낭비하게 된다.

> **핵심 통찰**: **정당한 이유 없이 사용된 모든 패턴은 설계를 복잡하게 만드는 장애물이다.** 패턴은 복잡성의 가치가 단순성을 넘어설 때만 정당화돼야 한다. 패턴을 적용할 때는 항상 설계를 좀 더 단순하고 명확하게 만들 수 있는 방법이 없는지를 고민해야 한다.

### 3.2 패턴을 향한 리팩터링

조슈아 케리에브스키는 패턴을 가장 효과적으로 적용하는 방법은 **패턴을 지향하거나 패턴을 목표로 리팩터링**하는 것이라고 이야기한다. 그는 패턴이 적용된 최종 결과를 이해하는 것보다는 **패턴을 목표로 리팩터링하는 이유를 이해하는 것**이 훨씬 가치 있으며, 훌륭한 소프트웨어 설계가 발전해 온 과정을 공부하는 것이 훌륭한 설계 자체를 공부하는 것보다 훨씬 중요하다고 이야기한다.

| 접근 방식 | 설명 |
|---|---|
| **패턴 구조를 그대로 적용** | 컨텍스트의 적절성을 무시하고 패턴의 구조에만 초점 → 불필요한 복잡성 증가 |
| **패턴을 목표로 리팩터링** | 현재 코드의 문제를 인식하고 패턴이 제시하는 방향으로 점진적으로 개선 → 적절한 복잡성 |

패턴은 출발점이다. 패턴은 공통적인 문제에 적절한 해법을 제공하지만, 공통적인 해법이 우리가 직면한 문제에 적합하지 않을 수도 있다. 문제를 분석하고 창의력을 발휘함으로써 **패턴을 현재의 문제에 적합하도록 적절하게 수정하라**. 비록 패턴이 현재의 문제에 딱 들어맞지 않는다고 해도 참조할 수 있는 모범적인 역할과 책임의 집합을 알고 있는 것은 큰 도움이 될 것이다.

---

## 4. 프레임워크와 코드 재사용

### 4.1 코드 재사용 대 설계 재사용

디자인 패턴은 프로그래밍 언어에 독립적으로 재사용 가능한 설계 아이디어를 제공하는 것을 목적으로 한다. 따라서 언어에 종속적인 구현 코드를 정의하지 않기 때문에, 디자인 패턴을 적용하기 위해서는 설계 아이디어를 프로그래밍 언어의 특성에 맞춰 가공해야 하고 **매번 구현 코드를 재작성해야 한다는 단점**이 있다.

오랜 시간 동안 개발자들은 부품을 조립해서 제품을 만드는 것처럼 별도의 프로그래밍 없이 기존 컴포넌트를 조립해서 애플리케이션을 구축하는 방법을 추구해 왔다. 그러나 로버트 L. 글래스가 주장한 것처럼 **소프트웨어 다양성** 때문에 두 가지 문제가 아주 비슷한 경우는 거의 없고, 다양한 도메인에 재사용 가능한 컴포넌트라는 개념은 비현실적이다.

| 재사용 방식 | 장점 | 한계 |
|---|---|---|
| **컴포넌트 기반 재사용** (코드만 재사용) | 별도 구현 없이 조립 가능 | 소프트웨어 다양성으로 인해 비현실적 |
| **디자인 패턴** (설계만 재사용) | 언어 독립적, 유연한 설계 | 매번 유사한 코드를 재작성해야 함 |
| **프레임워크** (설계 + 코드 재사용) | 설계와 구현 코드를 함께 재사용 | 프레임워크의 아키텍처에 종속 |

가장 이상적인 형태의 재사용 방법은 **설계 재사용과 코드 재사용을 적절한 수준으로 조합하는 것**이다. 이 질문에 대한 객체지향 커뮤니티의 대답이 바로 **프레임워크**다.

### 4.2 프레임워크의 정의

프레임워크란 다음 두 가지 관점에서 정의할 수 있다:

1. **구조적 관점**: 추상 클래스나 인터페이스를 정의하고 인스턴스 사이의 상호작용을 통해 시스템 전체 혹은 일부를 구현해 놓은 재사용 가능한 설계
2. **목적 관점**: 애플리케이션 개발자가 현재의 요구사항에 맞게 커스터마이징할 수 있는 애플리케이션의 골격(*Skeleton - 전체적인 뼈대 구조*)

프레임워크는 코드를 재사용함으로써 설계 아이디어를 재사용한다. 프레임워크는 애플리케이션의 아키텍처를 제공하며 문제 해결에 필요한 설계 결정과 이에 필요한 기반 코드를 함께 포함한다.

> 프레임워크는 애플리케이션에 대한 아키텍처를 제공한다. 즉, 프레임워크는 클래스와 객체들의 분할, 전체 구조, 클래스와 객체들 간의 상호작용, 객체와 클래스 조합 방법, 제어 흐름에 대해 미리 정의한다. 비록 프레임워크가 즉시 업무에 투입할 수 있는 구체적인 서브클래스를 포함하고 있기는 하지만 프레임워크는 코드의 재사용보다는 **설계 자체의 재사용을 중요시한다** [GOF94].

### 4.3 상위 정책과 하위 정책으로 패키지 분리하기

프레임워크의 핵심은 추상 클래스나 인터페이스와 같은 **추상화**라고 할 수 있다. 추상화가 일관성 있는 협력을 만드는 핵심 재료이기 때문이다.

핸드폰 과금 시스템에서, 구체적인 클래스들은 `RatePolicy`, `AdditionalRatePolicy`, `FeeCondition` 같은 추상화에 의존하지만, 추상화들은 구체 클래스에 의존하지 않는다. 이 설계는 9장에서 살펴본 **의존성 역전 원칙**(*DIP, Dependency Inversion Principle - 상위 수준의 모듈이 하위 수준의 모듈에 의존하면 안 되며, 둘 모두 추상화에 의존해야 한다는 원칙*)에 기반하고 있다.

상위 정책은 상대적으로 변경에 안정적이지만 세부 사항은 자주 변경된다:

| 구분 | 내용 | 변경 빈도 |
|---|---|---|
| **상위 정책** | 요금제가 기본 정책과 부가 정책으로 구성되고 다양한 순서로 조합될 수 있다는 규칙 | 낮음 (안정적) |
| **세부 사항** | 시간대별 방식, 요일별 방식, 구간별 방식과 같은 구체적 정책 종류 | 높음 (자주 변경) |

만약 변하지 않는 상위 정책이 자주 변하는 세부 사항에 의존한다면 변경에 대한 파급 효과로 인해 상위 정책이 불안정해진다. 또한 상위 정책은 세부 사항보다 더 다양한 상황에서 재사용될 수 있어야 하지만, 상위 정책이 세부 사항에 의존하면 상위 정책이 필요한 모든 경우에 세부 사항도 항상 함께 존재해야 하기 때문에 **재사용성이 낮아진다**.

이 문제를 해결하기 위한 첫걸음은 **변하는 부분과 변하지 않는 부분을 별도의 패키지로 분리하는 것**이다:

```
  ┌─────────────────────────────────────────────────┐
  │          상위 정책 패키지 (프레임워크)               │
  │                                                 │
  │  Phone ──▶ <<interface>> RatePolicy             │
  │                    ▲                            │
  │           ┌────────┴────────┐                   │
  │  BasicRatePolicy    AdditionalRatePolicy        │
  │           │                                     │
  │  <<interface>> FeeCondition    FeeRule           │
  └──────────────────────▲──────────────────────────┘
                         │ 의존
  ┌──────────────────────┴──────────────────────────┐
  │          하위 정책 패키지 (애플리케이션)              │
  │                                                 │
  │  TimeOfDayFeeCondition  DayOfWeekFeeCondition   │
  │  DurationFeeCondition   FixedFeeCondition       │
  │  TaxablePolicy          RateDiscountablePolicy  │
  └─────────────────────────────────────────────────┘
```

중요한 것은 **패키지 사이의 의존성 방향**이다. 의존성 역전 원리에 따라 추상화에만 의존하도록 의존성의 방향을 조정하고 추상화를 경계로 패키지를 분리했기 때문에, **세부 사항을 구현한 패키지는 항상 상위 정책을 구현한 패키지에 의존**해야 한다. 그 역방향으로는 의존성이 존재하지 않는다.

상위 정책을 구현하고 있는 패키지가 세부 사항을 구현한 패키지로부터 완벽하게 분리됐으므로, 상위 정책 패키지를 다른 애플리케이션에 재사용할 수 있다. 이것은 8장에서 설명한 **컨텍스트 독립성의 패키지 버전**이다.

좀 더 나아가, 상위 정책 패키지가 충분히 안정적이고 성숙했다면 하위 정책 패키지로부터 완벽히 분리해서 **별도의 배포 단위**로 만들 수 있다. 다시 말해 재사용 가능한 요금 계산 로직을 구현한 **프레임워크가 만들어진 것**이다.

---

## 5. 제어 역전 원리

### 5.1 의존성 역전과 제어 역전

상위 정책을 재사용한다는 것은 결국 도메인에 존재하는 핵심 개념들 사이의 **협력 관계를 재사용**한다는 것을 의미한다. 객체지향 설계의 재사용성은 개별 클래스가 아니라 **객체들 사이의 공통적인 협력 흐름**으로부터 나온다. 그리고 그 뒤에는 항상 **의존성 역전 원리**라는 강력한 지원군이 존재한다.

> 사실, 좋은 객체지향 설계의 증명이 바로 이와 같은 의존성의 역전이다. 프로그램이 어떤 언어로 작성됐는가는 상관없다. 프로그램의 의존성이 역전돼 있다면, 이것은 객체지향 설계를 갖는 것이다. 그 의존성이 역전돼 있지 않다면, 절차적 설계를 갖는 것이다. [Martin02]

의존성 역전은 의존성의 방향뿐만 아니라 **제어 흐름의 주체 역시 역전**시킨다. 전통적인 구조에서는 상위 정책의 코드가 하부의 구체적인 코드를 호출한다. 즉 애플리케이션 코드가 재사용 가능한 라이브러리나 툴킷의 코드를 호출한다.

그러나 의존성을 역전시킨 객체지향 구조에서는 반대로 **프레임워크가 애플리케이션에 속하는 서브클래스의 메서드를 호출**한다. 이를 **제어 역전**(Inversion of Control) 원리, 또는 **할리우드 원리**(Hollywood Principle)라고 한다.

```
  전통적 구조 (라이브러리 사용)          제어 역전 (프레임워크 사용)

  ┌──────────────────┐              ┌──────────────────┐
  │  애플리케이션 코드  │              │   프레임워크 코드   │
  │  (제어 주체)       │              │  (제어 주체)       │
  └────────┬─────────┘              └────────┬─────────┘
           │ 호출                             │ 호출
           ▼                                 ▼
  ┌──────────────────┐              ┌──────────────────┐
  │  라이브러리 코드    │              │  애플리케이션 코드  │
  │  (피호출)         │              │  (피호출)          │
  └──────────────────┘              └──────────────────┘
```

### 5.2 훅(Hook)

프레임워크에서는 일반적인 해결책만 제공하고, 애플리케이션에 따라 달라질 수 있는 특정한 동작은 비워 둔다. 이렇게 완성되지 않은 채로 남겨진 동작을 **훅**(Hook)이라고 부른다. 훅의 구현 방식은 애플리케이션의 컨텍스트에 따라 달라진다. 재정의된 훅은 제어 역전 원리에 따라 **프레임워크가 원하는 시점에 호출**된다.

핸드폰 과금 시스템의 프레임워크에서, 전체적인 협력 흐름은 프레임워크에 정의돼 있다. 특정한 기본 정책을 구현하는 개발자는 `FeeCondition`을 대체할 서브타입만 개발하면 프레임워크에 정의된 플로우에 따라 요금이 계산된다.

```
  프레임워크가 제어하는 협력 흐름

  Phone ──(1: calculateFee)──▶ BasicRatePolicy
                                    │
                            (2*: calculateFee)
                                    │
                                    ▼
                                FeeRule ──(3: findTimeIntervals)──▶ FeeCondition
                                                                    (훅: 개발자 구현)
```

여기서 협력을 제어하는 것은 **프레임워크**다. 우리는 프레임워크가 적절한 시점에 실행할 것으로 예상되는 코드를 작성할 뿐이다.

> 할리우드에서 캐스팅 담당자가 오디션을 보러 온 배우에게 "먼저 연락하지 마세요. 저희가 연락 드리겠습니다"라고 말하는 것처럼 프레임워크는 자신을 찾지 말라고 이야기한다.

### 5.3 라이브러리 vs 프레임워크

| 특성 | 라이브러리 | 프레임워크 |
|---|---|---|
| **제어 주체** | 애플리케이션이 라이브러리를 호출 | 프레임워크가 애플리케이션 코드를 호출 |
| **재사용 대상** | 코드 | 설계 + 코드 |
| **의존성 방향** | 애플리케이션 → 라이브러리 | 애플리케이션 → 프레임워크 (추상화 의존) |
| **확장 방식** | 필요한 기능을 선택적으로 호출 | 훅(Hook)을 구현하여 확장 |
| **제어 흐름** | 애플리케이션이 결정 | 프레임워크가 결정 (제어 역전) |

> **핵심 통찰**: 설계 수준의 재사용은 애플리케이션과 기반 소프트웨어 간에 **제어를 바꾸게 한다**. 라이브러리를 사용하면 애플리케이션이 필요한 코드를 호출하지만, 프레임워크를 재사용할 때는 프레임워크가 제공하는 메인 프로그램을 재사용하고 이 메인 프로그램이 호출하는 코드를 애플리케이션 개발자가 작성해야 한다. 언제 자신의 코드가 호출될 것인지를 스스로 제어할 수 없다. **제어 주체는 자신이 아닌 프레임워크로 넘어간 것**이다 [GOF94].

---

## 6. 나아가기: 학습의 세 단계

앨리스터 코어번(Alistair Cockburn)은 사람들이 새로운 기술을 학습하기 위해서는 일반적으로 세 가지 단계를 거치게 된다고 설명한다.

| 단계 | 이름 | 특징 |
|---|---|---|
| 1단계 | **따라 하는 수준** | 제대로 활용할 수 있는 단 하나의 절차를 찾아 그대로 모방한다. 성공의 달콤함이 보상이다. |
| 2단계 | **분리 수준** | 단 하나의 절차로는 모든 문제를 해결할 수 없다는 사실을 깨닫고, 다양한 절차를 학습하며 트레이드오프한다. |
| 3단계 | **거침없는 수준** | 절차는 중요하지 않게 된다. 직관적으로 적절한 해법을 떠올리고, 자신만의 방법으로 문제를 해결한다. |

이 책은 독자가 '따라 하는 수준'이라고 가정하고 가장 이상적인 절차와 방법을 통해 객체지향 설계를 설명했다. 다음 단계인 **'분리 수준'으로 나아가기 위한 세 가지 기법**이 있다:

- **디자인 패턴**(Design Pattern): 반복적으로 발생하는 문제와 해법의 쌍을 담고 있기 때문에 고품질의 설계를 짧은 시간에 얻을 수 있는 지름길을 제공한다. 디자인 패턴을 익히고 적용해 보는 것은 설계를 트레이드오프할 수 있는 능력을 기를 수 있는 가장 좋은 방법이다.
- **리팩터링**(Refactoring): 코드의 행동은 변경하지 않은 채 코드의 구조를 개선하는 활동이다. 관점을 '구현 전에 설계하기'에서 '항상 설계하기'로 바꾼다. 구현 전에 설계를 완성해야 한다는 강박관념에서 해방시켜 준다.
- **테스트-주도 개발**(Test-Driven Development): '거침없는 수준'에 이른 사람들이 제시한 독창적인 설계 방법이다. 전통적인 설계-구현-테스트의 순서를 **테스트-구현-설계의 순서**로 바꾼다. 메시지를 먼저 선택하고 메시지가 객체를 선택하게 한다는 책임-주도 설계와도 잘 어울린다.

> **핵심 통찰**: 어떤 기법도 홀로 존재하지 않는다. 책임-주도 설계에서 제공하는 다양한 책임 관점의 시각을 테스트-주도 개발에 적용할 수 있다. 책임-주도 설계에서 이야기하는 올바른 역할, 책임, 협력의 분리를 향해 리팩터링해 나아갈 수 있다. 디자인 패턴은 역할, 책임, 협력에 관한 일종의 모범 답안을 제공한다.

---

## 설계 원칙

| 원칙 | 설명 |
|---|---|
| **패턴은 역할, 책임, 협력의 템플릿** | 패턴의 구성 요소는 클래스가 아니라 역할이다. 디자인 패턴은 구체적인 구현 방법이 아니라 역할과 책임, 협력의 템플릿을 제안한다 |
| **캡슐화할 변경을 파악하라** | 각 디자인 패턴은 특정한 종류의 변경을 캡슐화한다. 어떤 변경을 캡슐화하는지, 어떤 방법(합성 vs 상속)을 사용하는지를 이해하는 것이 핵심이다 |
| **패턴은 출발점이지 목적지가 아니다** | 패턴을 맹목적으로 따르지 말고 현재 문제에 맞게 수정하라. 패턴을 목표로 리팩터링하는 것이 가장 효과적이다 |
| **프레임워크는 설계 + 코드 재사용** | 디자인 패턴이 설계만 재사용한다면, 프레임워크는 설계와 코드를 함께 재사용한다. 이를 위해 의존성 역전 원칙이 필수적이다 |
| **제어 역전(IoC)이 프레임워크의 핵심** | 라이브러리와 달리 프레임워크에서는 제어 주체가 프레임워크로 이동한다. 훅(Hook)을 통해 확장 포인트를 제공한다 |
| **상위 정책과 하위 정책을 분리하라** | 의존성 역전 원칙에 따라 추상화를 경계로 패키지를 분리하면, 상위 정책 패키지를 독립적으로 재사용할 수 있다 |

---

## 요약

- **소프트웨어 패턴**: 패턴은 하나의 실무 컨텍스트에서 유용하게 사용해 왔고 다른 실무 컨텍스트에서도 유용할 것이라고 예상되는 아이디어다. 최소 세 가지 서로 다른 시스템에 적용할 수 있어야 패턴으로 인정된다(3의 규칙).
- **패턴 분류**: 아키텍처 패턴(시스템 전체), 디자인 패턴(중간 규모), 분석 패턴(도메인 개념), 이디엄(언어별 하위 레벨)의 4가지로 분류한다.
- **패턴의 본질**: 패턴의 구성 요소는 클래스가 아니라 역할이다. 따라서 하나의 클래스가 여러 역할을 수행할 수도 있고, 여러 클래스가 동일한 역할을 수행할 수도 있다.
- **STRATEGY 패턴**: 알고리즘의 변경을 캡슐화하며, 객체 합성을 이용한다. 런타임에 알고리즘을 교체할 수 있다.
- **TEMPLATE METHOD 패턴**: 알고리즘의 변경을 캡슐화하며, 상속을 이용한다. 런타임 교체는 불가능하지만 복잡도가 낮다.
- **DECORATOR 패턴**: 선택적인 행동의 개수와 순서에 대한 변경을 캡슐화하며, 객체 합성(위임 체인)을 이용한다.
- **COMPOSITE 패턴**: 개별 객체와 복합 객체라는 객체의 수와 관련된 변경을 캡슐화한다.
- **패턴은 출발점**: 패턴을 맹목적으로 적용하면 불필요한 복잡성이 증가한다. 패턴을 목표로 리팩터링하는 것이 가장 효과적이다.
- **프레임워크**: 설계 재사용과 코드 재사용을 적절한 수준으로 조합한다. 의존성 역전 원칙에 기반하여 상위 정책과 하위 정책을 분리한다.
- **제어 역전(IoC)**: 라이브러리와 달리 프레임워크에서는 제어 주체가 프레임워크로 이동한다. 프레임워크는 훅(Hook)을 통해 애플리케이션 코드를 적절한 시점에 호출한다.
- **나아가기**: 디자인 패턴, 리팩터링, 테스트-주도 개발을 익히고 적용함으로써 '따라 하는 수준'에서 '분리 수준'으로 나아가야 한다.

---

## 다른 챕터와의 관계

- **Chapter 14 (일관성 있는 협력)**: 디자인 패턴은 특정한 변경을 일관성 있게 다룰 수 있는 협력 템플릿을 제공하고, 프레임워크는 특정한 변경을 일관성 있게 다룰 수 있는 확장 가능한 코드 템플릿을 제공한다. 14장에서 다룬 일관성 있는 협력의 개념이 이 장에서 패턴과 프레임워크로 확장된다.
- **Chapter 9 (유연한 설계)**: 이 장에서 프레임워크의 핵심 원리로 다룬 의존성 역전 원칙(DIP)은 9장에서 유연한 설계의 원칙 중 하나로 소개된 것이다. 의존성 역전이 어떻게 프레임워크의 재사용성과 제어 역전으로 이어지는지를 구체적으로 보여준다.
- **Chapter 8 (의존성 관리하기)**: 8장에서 설명한 컨텍스트 독립성 개념이 이 장에서 패키지 수준으로 확장된다. 상위 정책 패키지가 하위 정책 패키지로부터 독립됨으로써 다른 애플리케이션에서 재사용 가능해진다.
- **Chapter 11 (합성과 유연한 설계)**: 이 장에서 다룬 STRATEGY, DECORATOR, COMPOSITE 패턴은 모두 합성을 통한 설계의 구체적 사례다. 11장에서 설명한 합성의 장점(유연성, 캡슐화, 느슨한 결합)이 디자인 패턴이라는 형태로 정리되어 있다.
- **Chapter 10 (상속과 코드 재사용)**: TEMPLATE METHOD 패턴은 상속을 이용한 캡슐화의 대표적 사례다. 10장에서 경고한 상속의 위험을 인식하면서도, 적절한 상황에서 상속이 합성보다 단순한 해법을 제공할 수 있음을 보여준다.
- **Chapter 1 (객체, 설계)**: 1장에서 강조한 "이론보다 실무가 먼저"라는 관점이 이 장에서 재확인된다. 패턴은 실무에서 탄생한 경험의 산물이며, '따라 하는 수준'에서 '분리 수준'으로 나아가는 것은 실무 경험의 축적을 통해서만 가능하다.
