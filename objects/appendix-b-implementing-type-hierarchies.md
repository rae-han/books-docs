# Appendix B: Implementing Type Hierarchies (타입 계층의 구현)

## 핵심 질문

타입과 클래스는 동일한 개념인가? 타입 계층을 구현하는 다양한 방법(클래스, 인터페이스, 추상 클래스, 덕 타이핑, 믹스인)은 각각 어떤 장단점을 가지며, 어떤 상황에서 어떤 방법을 선택해야 하는가?

---

## 1. 타입 ≠ 클래스

13장에서 살펴본 것처럼 객체지향 프로그래밍에서 타입과 타입 계층은 핵심 개념이다. 그러나 많은 사람들이 가진 흔한 오해는 **타입과 클래스가 동일한 개념**이라는 것이다. 이것은 사실이 아니다.

| 개념 | 의미 | 초점 |
|---|---|---|
| **타입** | 개념의 분류. 객체의 퍼블릭 인터페이스를 가리킨다 | 객체가 **무엇을 할 수 있는가** (행동) |
| **클래스** | 타입을 구현하는 한 가지 방법. 객체의 내부 상태와 오퍼레이션 구현을 정의한다 | 객체가 **어떻게 하는가** (구현) |

타입은 다양한 방법으로 구현할 수 있다. 타입의 개념을 이해하는 데 가장 큰 걸림돌은 바로 타입을 구현하는 방법이 다양하다는 점이다. 심지어 타입을 구현할 수 있는 독자적인 방법을 제공하는 언어도 있다.

타입 계층은 타입보다 상황이 더 복잡한데, 다양한 방식으로 구현된 타입들을 하나의 타입 계층 안에 조합할 수 있기 때문이다. 예를 들어 자바에서는 인터페이스와 클래스를 이용해 개별 타입을 구현한 후 이 두 가지 종류의 타입 구현체를 함께 포함하도록 타입 계층을 구성할 수 있다.

이 부록을 읽을 때 다음 두 가지 사항을 염두에 두어야 한다:

1. **타입 계층은 다형성 구현 방법이다**: 타입 계층은 동일한 메시지에 대한 행동 호환성을 전제로 하기 때문에, 여기서 언급하는 모든 방법은 타입 계층을 구현하는 방법인 동시에 다형성을 구현하는 방법이기도 하다. 공통적으로 슈퍼타입에 대해 전송한 메시지를 서브타입별로 다르게 처리할 수 있는 방법을 제공하며, 12장에서 설명한 동적 메서드 탐색과 유사한 방식을 이용해 적절한 메서드를 검색한다.

2. **리스코프 치환 원칙 준수는 우리의 책임이다**: 여기서 제시하는 방법을 이용해 타입과 타입 계층을 구현한다고 해서 서브타이핑 관계가 보장되는 것은 아니다. 13장에서 설명한 것처럼 올바른 타입 계층이 되기 위해서는 서브타입이 슈퍼타입을 대체할 수 있도록 리스코프 치환 원칙을 준수해야 한다. 리스코프 치환 원칙은 특정한 구현 방법에 의해 보장될 수 없기 때문에 클라이언트 관점에서 타입을 동일하게 다룰 수 있도록 의미적으로 행동 호환성을 보장하는 것은 전적으로 우리의 책임이다.

---

## 2. 클래스를 이용한 타입 계층 구현

클래스 기반의 객체지향 언어를 사용하는 대부분의 사람들은 "타입"이라는 말에서 반사적으로 "클래스"를 떠올린다. 타입은 객체의 퍼블릭 인터페이스를 가리키기 때문에 결과적으로 클래스는 객체의 타입과 구현을 동시에 정의하는 것과 같다. 이것이 객체지향 언어에서 클래스를 사용자 정의 타입(*user-defined data type*)이라고 부르는 이유다.

10장에서 구현한 `Phone` 클래스를 살펴보자.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Phone {
    private Money amount;
    private Duration seconds;
    private List<Call> calls = new ArrayList<>();

    public Phone(Money amount, Duration seconds) {
        this.amount = amount;
        this.seconds = seconds;
    }

    public Money calculateFee() {
        Money result = Money.ZERO;
        for (Call call : calls) {
            result = result.plus(
                amount.times(call.getDuration().getSeconds() / seconds.getSeconds())
            );
        }
        return result;
    }
}
```

</details>

```typescript
// TypeScript
class Phone {
    private amount: Money;
    private seconds: Duration;
    private calls: Call[] = [];

    constructor(amount: Money, seconds: Duration) {
        this.amount = amount;
        this.seconds = seconds;
    }

    calculateFee(): Money {
        let result = Money.ZERO;
        for (const call of this.calls) {
            result = result.plus(
                this.amount.times(call.getDuration().getSeconds() / this.seconds.getSeconds())
            );
        }
        return result;
    }
}
```

`Phone`의 인스턴스는 `calculateFee` 메시지를 수신할 수 있는 퍼블릭 메서드를 구현한다. 이 메서드는 결과적으로 `Phone`의 퍼블릭 인터페이스를 구성한다. 타입은 퍼블릭 인터페이스를 의미하기 때문에 `Phone` 클래스는 `Phone` 타입을 구현한다고 말할 수 있다. `Phone`은 `calculateFee` 메시지에 응답할 수 있는 타입을 선언하는 동시에 객체 구현을 정의하고 있는 것이다.

### 타입과 클래스가 갈라지는 시점

`Phone`의 경우처럼 타입을 구현할 수 있는 방법이 단 한 가지만 존재하는 경우에는 타입과 클래스를 동일하게 취급해도 무방하다. 그러나 **타입을 구현할 수 있는 다양한 방법이 존재하는 순간**부터 클래스와 타입은 갈라지기 시작한다.

`Phone`과 퍼블릭 인터페이스는 동일하지만 다른 방식으로 구현해야 하는 객체가 필요하다고 가정해 보자. 퍼블릭 인터페이스는 유지하면서 새로운 구현을 가진 객체를 추가할 수 있는 가장 간단한 방법은 **상속**을 이용하는 것이다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class NightlyDiscountPhone extends Phone {
    private static final int LATE_NIGHT_HOUR = 22;
    private Money nightlyAmount;

    public NightlyDiscountPhone(Money nightlyAmount, Money regularAmount, Duration seconds) {
        super(regularAmount, seconds);
        this.nightlyAmount = nightlyAmount;
    }

    @Override
    public Money calculateFee() {
        Money result = super.calculateFee();
        for (Call call : getCalls()) {
            if (call.getFrom().getHour() >= LATE_NIGHT_HOUR) {
                result = result.minus(
                    getAmount().minus(nightlyAmount).times(
                        call.getDuration().getSeconds() / getSeconds().getSeconds()
                    )
                );
            }
        }
        return result;
    }
}
```

</details>

```typescript
// TypeScript
class NightlyDiscountPhone extends Phone {
    private static readonly LATE_NIGHT_HOUR = 22;
    private nightlyAmount: Money;

    constructor(nightlyAmount: Money, regularAmount: Money, seconds: Duration) {
        super(regularAmount, seconds);
        this.nightlyAmount = nightlyAmount;
    }

    override calculateFee(): Money {
        let result = super.calculateFee();
        for (const call of this.getCalls()) {
            if (call.getFrom().getHour() >= NightlyDiscountPhone.LATE_NIGHT_HOUR) {
                result = result.minus(
                    this.getAmount().minus(this.nightlyAmount).times(
                        call.getDuration().getSeconds() / this.getSeconds().getSeconds()
                    )
                );
            }
        }
        return result;
    }
}
```

상속을 이용하면 자식 클래스가 부모 클래스의 구현뿐만 아니라 퍼블릭 인터페이스도 물려받을 수 있기 때문에 타입 계층을 쉽게 구현할 수 있다. 하지만 10장에서 살펴본 것처럼 상속은 자식 클래스를 부모 클래스의 구현에 강하게 결합시키기 때문에 **구체 클래스를 상속받는 것은 피해야 한다**. 가급적 추상 클래스를 상속받거나 인터페이스를 구현하는 방법을 사용해야 한다.

> **핵심 통찰**: 클래스는 타입을 구현할 수 있는 다양한 방법 중 하나일 뿐이다. 비교적 최근에 발표된 객체지향 언어들은 클래스를 사용하지 않고도 타입을 구현할 수 있는 방법을 제공한다. 대표적인 것이 자바와 C#의 인터페이스다.

---

## 3. 인터페이스를 이용한 타입 계층 구현

간단한 게임을 개발하고 있다고 가정하자. 게임은 사용자와 상호작용할 수 있는 다양한 객체들로 구성된다. 수많은 객체들 중에서 실제로 플레이어의 게임플레이에 영향을 미치는 객체들을 동일한 타입으로 분류하기를 원한다고 가정하자. 이 객체들의 타입을 `GameObject`라고 부를 것이다.

게임 안에는 `GameObject` 타입으로 분류될 수 있는 다양한 객체들이 존재한다. 화면상에서 폭발 효과를 표현하는 `Explosion`과 사운드 효과를 표현하는 `Sound`가 대표적인 예다. 이 중에서 `Explosion`과 `Sound`는 게임에 필요한 다양한 효과 중 하나이기 때문에 이들을 다시 `Effect` 타입으로 분류할 수 있다. `Explosion`은 화면에 표시될 수 있기 때문에 `Displayable` 타입으로도 분류할 수 있다. `Displayable` 타입에는 적대적인 `Monster`와 플레이어가 직접 조작 가능한 `Player` 타입도 존재한다.

```
             GameObject
            /          \
     Displayable      Effect
      /     \         /    \
   Player  Monster  Explosion Sound
```

### 다중 분류 문제

이제 클래스와 상속을 이용해 이 객체들을 구현하는 방법을 생각해 보자. `Explosion` 타입은 `Effect` 타입인 동시에 `Displayable` 타입이기 때문에 `Effect` 클래스와 `Displayable` 클래스를 동시에 상속받아야 한다. 문제는 대부분의 언어들이 **다중 상속을 지원하지 않는다**는 데 있다.

```
             GameObject
            /          \
     Displayable      Effect
      /   \   \       /    \
  Player Monster Explosion Sound
                  ↑
           Effect와 Displayable을
           동시에 상속받아야 한다 (불가능!)
```

게다가 이 클래스들을 동일한 상속 계층 안에 구현하고 싶지도 않다. 클래스들을 상속 관계로 연결하면 자식 클래스가 부모 클래스의 구현에 강하게 결합될 확률이 높다. 결과적으로 상속 계층 안의 클래스 하나를 변경했는데도 게임에 포함된 수많은 자식 클래스들이 영향을 받을 수 있다.

### 인터페이스로 해결하기

상속으로 인한 결합도 문제를 피하고 다중 상속이라는 구현 제약도 해결할 수 있는 방법은 클래스가 아닌 **인터페이스**를 사용하는 것이다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public interface GameObject {
    String getName();
}

public interface Displayable extends GameObject {
    Point getPosition();
    void update(Graphics graphics);
}

public interface Collidable extends Displayable {
    boolean collideWith(Collidable other);
}

public interface Effect extends GameObject {
    void activate();
}
```

</details>

```typescript
// TypeScript
interface GameObject {
    getName(): string;
}

interface Displayable extends GameObject {
    getPosition(): Point;
    update(graphics: Graphics): void;
}

interface Collidable extends Displayable {
    collideWith(other: Collidable): boolean;
}

interface Effect extends GameObject {
    activate(): void;
}
```

`Displayable` 인터페이스가 `GameObject`를 확장한다는 사실에 주목하라. 이것은 `Displayable` 타입을 `GameObject` 타입의 서브타입으로 정의한다. 결과적으로 `Displayable` 타입의 모든 인스턴스는 `GameObject` 타입의 인스턴스 집합에도 포함된다. 이처럼 인터페이스가 다른 인터페이스를 확장하도록 만들면 슈퍼타입과 서브타입 간의 타입 계층을 구성할 수 있다.

화면에 표시될 수 있는 `Displayable` 타입의 인스턴스들 중에는 다른 요소들과의 충돌로 인해 이동에 제약을 받거나 피해를 입는 등의 처리가 필요한 객체들이 존재한다. 이런 객체들을 위해 `Collidable` 타입을 정의하고 충돌 체크를 위한 `collideWith` 오퍼레이션을 추가한다. 충돌을 체크하는 객체들은 모두 화면에 표시 가능해야 하기 때문에 `Collidable` 타입은 `Displayable` 타입의 서브타입이어야 한다.

### 타입을 구현하는 클래스들

이제 타입에 속할 객체들을 구현하자. 자바와 C#에서는 인터페이스를 이용해 타입의 퍼블릭 인터페이스를 정의하고 클래스를 이용해 객체를 구현하는 것이 일반적인 패턴이다. 인터페이스와 클래스를 함께 조합하면 다중 상속의 딜레마에 빠지지 않을 수 있고 단일 상속 계층으로 인한 결합도 문제도 피할 수 있다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Player implements Collidable {
    @Override public String getName() { ... }
    @Override public boolean collideWith(Collidable other) { ... }
    @Override public Point getPosition() { ... }
    @Override public void update(Graphics graphics) { ... }
}

public class Monster implements Collidable {
    @Override public String getName() { ... }
    @Override public boolean collideWith(Collidable other) { ... }
    @Override public Point getPosition() { ... }
    @Override public void update(Graphics graphics) { ... }
}

public class Sound implements Effect {
    @Override public String getName() { ... }
    @Override public void activate() { ... }
}

public class Explosion implements Displayable, Effect {
    @Override public String getName() { ... }
    @Override public Point getPosition() { ... }
    @Override public void update(Graphics graphics) { ... }
    @Override public void activate() { ... }
}
```

</details>

```typescript
// TypeScript
class Player implements Collidable {
    getName(): string { ... }
    collideWith(other: Collidable): boolean { ... }
    getPosition(): Point { ... }
    update(graphics: Graphics): void { ... }
}

class Monster implements Collidable {
    getName(): string { ... }
    collideWith(other: Collidable): boolean { ... }
    getPosition(): Point { ... }
    update(graphics: Graphics): void { ... }
}

class Sound implements Effect {
    getName(): string { ... }
    activate(): void { ... }
}

class Explosion implements Displayable, Effect {
    getName(): string { ... }
    getPosition(): Point { ... }
    update(graphics: Graphics): void { ... }
    activate(): void { ... }
}
```

`Player`는 화면에 표시될 뿐만 아니라 다른 객체들과의 충돌을 체크해야 하므로 `Collidable` 타입을 구현한다. `Monster` 역시 마찬가지다. `Sound`는 화면에 표시되거나 충돌 여부를 체크할 필요 없이 특정 이벤트 발생 시 활성화되면 되므로 `Effect`만 구현한다. `Explosion`은 화면에 표시될 수 있으면서 동시에 특정 조건에 의해 활성화되는 효과이므로 `Displayable`과 `Effect`를 **동시에** 구현한다.

```
         <<interface>>          <<interface>>
          GameObject              Effect
         getName()             activate()
            ↑    ↑                  ↑
            |    |                  |
  <<interface>>  <<interface>>     |
  Displayable    Effect            |
  getPosition()  activate()        |
  update()                         |
      ↑                            |
      |                            |
  <<interface>>                    |
  Collidable                       |
  collideWith()                    |
      ↑                            |
   ┌──┴──┐           ┌────────────┤
 Player  Monster  Explosion     Sound
```

이 그림으로부터 다음과 같은 사실을 알 수 있다:

- **여러 클래스가 동일한 타입을 구현할 수 있다**: `Player`와 `Monster` 클래스는 서로 다른 클래스지만 동일한 `Collidable` 인터페이스를 구현하고 있기 때문에 동일한 메시지에 응답할 수 있다. 따라서 서로 다른 클래스를 이용해서 구현됐지만 타입은 동일하다.
- **하나의 클래스가 여러 타입을 구현할 수 있다**: `Explosion`의 인스턴스는 `Displayable` 인터페이스와 동시에 `Effect` 인터페이스도 구현한다. 따라서 `Explosion`의 인스턴스는 `Displayable` 타입인 동시에 `Effect` 타입이기도 하다.

> **핵심 통찰**: 인터페이스를 이용해 타입을 정의하고 클래스를 이용해 객체를 구현하면 클래스 상속을 사용하지 않고도 타입 계층을 구현할 수 있다. 중요한 것은 클래스 자체가 아니라 타입이다. 타입이 식별된 후에 타입에 속하는 객체를 구현하기 위해 클래스를 사용하는 것이다.

### 실전 예제: 할인 조건

영화 예매 시스템에서도 할인 조건을 구현한 타입 계층을 구현하기 위해 자바의 인터페이스와 클래스를 사용했다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public interface DiscountCondition {
    boolean isSatisfiedBy(Screening screening);
}

public class SequenceCondition implements DiscountCondition {
    public boolean isSatisfiedBy(Screening screening) { ... }
}

public class PeriodCondition implements DiscountCondition {
    public boolean isSatisfiedBy(Screening screening) { ... }
}
```

</details>

```typescript
// TypeScript
interface DiscountCondition {
    isSatisfiedBy(screening: Screening): boolean;
}

class SequenceCondition implements DiscountCondition {
    isSatisfiedBy(screening: Screening): boolean { ... }
}

class PeriodCondition implements DiscountCondition {
    isSatisfiedBy(screening: Screening): boolean { ... }
}
```

이 예제에서는 할인 조건이라는 타입을 정의하기 위해 인터페이스로 `DiscountCondition`을 정의했다. 클래스인 `SequenceCondition`과 `PeriodCondition`은 `DiscountCondition` 타입으로 분류될 객체들에 대한 구현을 담고 있다.

> 객체의 클래스는 객체의 구현을 정의한다. 클래스는 객체의 내부 상태와 오퍼레이션 구현 방법을 정의하는 것이고 객체의 타입은 인터페이스만을 정의하는 것으로 객체가 반응할 수 있는 오퍼레이션의 집합을 정의한다. 하나의 객체가 여러 타입을 가질 수 있고 서로 다른 클래스의 객체들이 동일한 타입을 가질 수 있다. 즉, 객체의 구현은 다를지라도 인터페이스는 같을 수 있다는 의미다 [GOF94].

클래스와 타입의 차이점을 이해하는 것은 설계 관점에서 매우 중요하다. 타입은 동일한 퍼블릭 인터페이스를 가진 객체들의 범주다. 클래스는 타입에 속하는 객체들을 구현하기 위한 구현 메커니즘이다. 객체지향에서 중요한 것은 협력 안에서 객체가 제공하는 행동이라는 사실을 기억하라. 따라서 중요한 것은 클래스 자체가 아니라 타입이다.

---

## 4. 추상 클래스를 이용한 타입 계층 구현

클래스 상속을 이용해 구현을 공유하면서도 결합도로 인한 부작용을 피하는 방법도 있다. 바로 **추상 클래스**를 이용하는 방법이다. 영화 예매 시스템에서는 할인 정책을 구현하기 위한 `DiscountPolicy`가 추상 클래스에 해당한다.

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
        return screening.getMovieFee();
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
        for (const each of this.conditions) {
            if (each.isSatisfiedBy(screening)) {
                return this.getDiscountAmount(screening);
            }
        }
        return screening.getMovieFee();
    }

    protected abstract getDiscountAmount(screening: Screening): Money;
}
```

이제 추상 클래스인 `DiscountPolicy`를 상속받는 구체 클래스를 추가함으로써 타입 계층을 구현할 수 있다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class AmountDiscountPolicy extends DiscountPolicy {
    @Override
    protected Money getDiscountAmount(Screening screening) {
        return discountAmount;
    }
}

public class PercentDiscountPolicy extends DiscountPolicy {
    @Override
    protected Money getDiscountAmount(Screening screening) {
        return screening.getMovieFee().times(percent);
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

### 구체 클래스 상속 vs 추상 클래스 상속: 두 가지 차이점

구체 클래스로 타입을 정의해서 상속받는 방법과 추상 클래스로 타입을 정의해서 상속받는 방법 사이에는 두 가지 중요한 차이점이 있다.

**첫 번째: 의존하는 대상의 추상화 정도가 다르다**

| 방식 | 자식 클래스의 의존 대상 | 결합도 |
|---|---|---|
| 구체 클래스 상속 (`Phone → NightlyDiscountPhone`) | 부모 클래스의 **구체적인 내부 구현** | 높다. 부모 구현이 변경되면 자식도 함께 변경될 가능성이 높다 |
| 추상 클래스 상속 (`DiscountPolicy → Amount/Percent`) | **추상 메서드의 시그니처**에만 의존 | 낮다. 추상 메서드 명세가 변경되지 않는 한 영향을 받지 않는다 |

`Phone`의 경우, 자식 클래스인 `NightlyDiscountPhone`의 `calculateFee` 메서드가 부모 클래스인 `Phone`의 `calculateFee` 메서드의 구체적인 내부 구현에 강하게 결합된다. 따라서 `Phone`의 내부 구현이 변경될 경우 `NightlyDiscountPhone`도 함께 변경될 가능성이 높다.

이에 비해 추상 클래스인 `DiscountPolicy`의 경우, 자식 클래스인 `AmountDiscountPolicy`와 `PercentDiscountPolicy`가 `DiscountPolicy`의 내부 구현이 아닌 추상 메서드의 시그니처에만 의존한다. 자식 클래스들은 `DiscountPolicy`가 어떤 식으로 구현돼 있는지 알 필요 없이, 단지 추상 메서드로 정의된 `getDiscountAmount` 메서드를 오버라이딩하면 된다.

여기서 부모 클래스와 자식 클래스 **모두** 추상 메서드인 `getDiscountAmount`에 의존한다는 사실이 중요하다. 이것은 **의존성 역전 원칙(DIP)**의 변형이다:

```
        DiscountPolicy (고차원 모듈)
    +calculateDiscountAmount()
    #getDiscountAmount()  ◀─── 추상 메서드
            ▲                        ▲
            │ 의존                    │ 의존
    ┌───────┴──────────┐             │
AmountDiscountPolicy  PercentDiscountPolicy (저차원 모듈)
 #getDiscountAmount()  #getDiscountAmount()
```

`DiscountPolicy`의 구체 메서드인 `calculateDiscountAmount`가 추상 메서드 `getDiscountAmount`를 호출하며, 자식 클래스들은 모두 이 추상 메서드의 시그니처를 준수한다. 구체적인 메서드가 추상적인 메서드에 의존하기 때문에 의존성 역전 원칙을 따른다고 할 수 있다. 결과적으로 이 설계는 유연한 동시에 변화에 안정적이다.

**두 번째: 상속을 사용하는 의도가 다르다**

`Phone`은 상속을 염두에 두고 설계된 것이 아니다. `Phone`의 설계자는 나중에 `NightlyDiscountPhone`이라는 개념이 추가될 것이라는 사실을 알지 못했다. 따라서 `Phone`에는 미래의 확장을 위한 어떤 준비도 돼 있지 않다. 사실 `NightlyDiscountPhone`의 개발자가 `Phone`의 코드를 재사용하기 위해 상속을 사용한 것은 트릭에 가깝다.

그에 반해 `DiscountPolicy`는 **처음부터 상속을 염두에 두고 설계된 클래스**다. `DiscountPolicy`는 추상 클래스이기 때문에 자신의 인스턴스를 직접 생성할 수 없다. `DiscountPolicy`의 유일한 목적은 자식 클래스를 추가하는 것이다. 이 클래스는 추상 메서드를 제공함으로써 상속 계층을 쉽게 확장할 수 있게 하고 결합도로 인한 부작용을 방지할 수 있는 안전망을 제공한다.

> **핵심 통찰**: 모든 구체 클래스의 부모 클래스를 항상 추상 클래스로 만들기 위해 노력하라. 의존하는 대상이 더 추상적일수록 결합도는 낮아지고, 결합도가 낮아질수록 변경으로 인한 영향도는 줄어든다.

---

## 5. 추상 클래스와 인터페이스 결합하기

대부분의 객체지향 언어들은 하나의 부모 클래스만 가질 수 있도록 허용하는 단일 상속만 지원한다. 이 경우 여러 타입으로 분류되는 타입이 문제가 될 수 있는데, 오직 클래스만을 이용해 타입을 구현할 경우 `Explosion`처럼 다중 상속을 이용해서 해결할 수밖에 없기 때문이다. 클래스와 단일 상속만으로 이 문제를 해결할 수는 없기 때문에 대부분의 경우 해결 방법은 타입 계층을 오묘한 방식으로 비트는 것이다.

자바와 C#에서 제공하는 인터페이스를 이용해 타입을 정의하면 다중 상속 문제를 해결할 수 있다. 클래스가 구현할 수 있는 인터페이스의 수에는 제한이 없기 때문에 하나의 클래스가 하나 이상의 타입으로 분류 가능하도록 손쉽게 확장할 수 있다.

물론 인터페이스만을 사용하는 방법에도 단점은 있다. 자바 8 이전 버전이나 C#에서 제공하는 인터페이스에는 구현 코드를 포함시킬 수 없기 때문에 **인터페이스만으로는 중복 코드를 제거하기 어렵다**는 점이다.

### 골격 구현 추상 클래스

효과적인 접근 방법은 **인터페이스를 이용해 타입을 정의**하고, 특정 상속 계층에 국한된 코드를 공유할 필요가 있을 경우에는 **추상 클래스를 이용해 코드 중복을 방지**하는 것이다. 이런 형태로 추상 클래스를 사용하는 방식을 **골격 구현 추상 클래스**(*skeletal implementation abstract class*)라고 부른다.

> 인터페이스가 메서드 구현 부분을 포함하지는 않지만 인터페이스를 사용해 타입을 정의한다고 해서 프로그래머가 구현을 하는 데 도움을 못 주는 것은 아니다. 외부에 공개한 각각의 중요한 인터페이스와 연관시킨 골격 구현 추상 클래스를 제공함으로써 인터페이스와 추상 클래스의 장점을 결합할 수 있다. 그렇게 함으로써 인터페이스는 여전히 타입을 정의하지만 골격 구현 클래스는 그것을 구현하는 모든 일을 맡는다 [Bloch08].

`DiscountPolicy` 타입은 추상 클래스를 이용해서 구현했기 때문에, `DiscountPolicy` 타입에 속하는 모든 객체들은 하나의 상속 계층 안에 묶여야 하는 제약을 가진다. 이제 상속 계층에 대한 제약을 완화시켜 `DiscountPolicy` 타입으로 분류될 수 있는 객체들이 구현 시에 서로 다른 상속 계층에 속할 수 있도록 만들고 싶다고 가정해 보자.

가장 좋은 방법은 인터페이스와 추상 클래스를 결합하는 것이다. `DiscountPolicy` 타입을 추상 클래스에서 인터페이스로 변경하고, 공통 코드를 담을 골격 구현 추상 클래스인 `DefaultDiscountPolicy`를 추가한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public interface DiscountPolicy {
    Money calculateDiscountAmount(Screening screening);
}

public abstract class DefaultDiscountPolicy implements DiscountPolicy {
    private List<DiscountCondition> conditions = new ArrayList<>();

    public DefaultDiscountPolicy(DiscountCondition... conditions) {
        this.conditions = Arrays.asList(conditions);
    }

    @Override
    public Money calculateDiscountAmount(Screening screening) {
        for (DiscountCondition each : conditions) {
            if (each.isSatisfiedBy(screening)) {
                return getDiscountAmount(screening);
            }
        }
        return screening.getMovieFee();
    }

    abstract protected Money getDiscountAmount(Screening screening);
}

public class AmountDiscountPolicy extends DefaultDiscountPolicy { ... }
public class PercentDiscountPolicy extends DefaultDiscountPolicy { ... }
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
        for (const each of this.conditions) {
            if (each.isSatisfiedBy(screening)) {
                return this.getDiscountAmount(screening);
            }
        }
        return screening.getMovieFee();
    }

    protected abstract getDiscountAmount(screening: Screening): Money;
}

class AmountDiscountPolicy extends DefaultDiscountPolicy { ... }
class PercentDiscountPolicy extends DefaultDiscountPolicy { ... }
```

```
    <<interface>>
    DiscountPolicy
 calculateDiscountAmount()
            ▲
            │ implements
  DefaultDiscountPolicy
 +calculateDiscountAmount()
 #getDiscountAmount()
         ▲
    ┌────┴─────┐
 Amount       Percent
 DiscountPolicy  DiscountPolicy
```

### 인터페이스 + 추상 클래스 결합의 장점

인터페이스와 추상 클래스를 함께 사용하는 방법은 추상 클래스만 사용하는 방법에 비해 두 가지 장점이 있다:

1. **다양한 구현 방법이 필요할 경우 새로운 추상 클래스를 추가해서 쉽게 해결할 수 있다**: 예를 들어, 금액 할인 정책을 더 빠른 속도로 처리할 수 있는 방법과 메모리를 더 적게 차지하는 방법 모두를 구현해 놓고 상황에 따라 적절한 방법을 선택하게 할 수 있다.

2. **이미 부모 클래스가 존재하는 클래스라 하더라도 인터페이스를 추가함으로써 새로운 타입으로 쉽게 확장할 수 있다**: `DiscountPolicy` 타입이 추상 클래스로 구현돼 있는 경우에 이 문제를 해결할 수 있는 유일한 방법은 상속 계층을 다시 조정하는 것뿐이다.

여러분의 설계가 상속 계층에 얽매이지 않는 타입 계층을 요구한다면 인터페이스로 타입을 정의하라. 추상 클래스로 기본 구현을 제공해서 중복 코드를 제거하라. 하지만 이런 복잡성이 필요하지 않다면 타입을 정의하기 위해 인터페이스나 추상 클래스 둘 중 하나만 사용하라.

| 상황 | 권장 방법 |
|---|---|
| 타입의 구현 방법이 단 한 가지이거나 단일 상속 계층으로 충분한 경우 | 클래스나 추상 클래스를 이용해 타입을 정의 |
| 상속 계층에 얽매이지 않는 유연한 타입 계층이 필요한 경우 | 인터페이스로 타입 정의 + 추상 클래스로 코드 중복 제거 |

---

## 6. 덕 타이핑 사용하기

덕 타이핑(*duck typing*)은 주로 동적 타입 언어에서 사용하는 방법으로서 다음과 같은 덕 테스트(*duck test*)를 프로그래밍 언어에 적용한 것이다:

> 어떤 새가 오리처럼 걷고, 오리처럼 헤엄치며, 오리처럼 꽥꽥 소리를 낸다면 나는 이 새를 오리라고 부를 것이다.
>
> — 제임스 윗콤 릴리(James Whitcomb Riley)

덕 테스트는 어떤 대상의 행동이 오리와 같다면 그것을 오리라는 타입으로 취급해도 무방하다는 것이다. 다시 말해 **객체가 어떤 인터페이스에 정의된 행동을 수행할 수만 있다면 그 객체를 해당 타입으로 분류해도 문제가 없다**.

### 정적 타입 언어의 한계

안타깝게도 자바 같은 대부분의 정적 타입 언어에서는 덕 타이핑을 지원하지 않는다. 다음의 `Employee`, `SalariedEmployee`, `HourlyEmployee` 클래스를 보자.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public interface Employee {
    Money calculatePay(double taxRate);
}

public class SalariedEmployee {
    private String name;
    private Money basePay;

    public SalariedEmployee(String name, Money basePay) {
        this.name = name;
        this.basePay = basePay;
    }

    public Money calculatePay(double taxRate) {
        return basePay.minus(basePay.times(taxRate));
    }
}

public class HourlyEmployee {
    private String name;
    private Money basePay;
    private int timeCard;

    public HourlyEmployee(String name, Money basePay, int timeCard) {
        this.name = name;
        this.basePay = basePay;
        this.timeCard = timeCard;
    }

    public Money calculatePay(double taxRate) {
        return basePay.times(timeCard).minus(basePay.times(timeCard).times(taxRate));
    }
}
```

</details>

```typescript
// TypeScript
interface Employee {
    calculatePay(taxRate: number): Money;
}

class SalariedEmployee {
    constructor(private name: string, private basePay: Money) {}

    calculatePay(taxRate: number): Money {
        return this.basePay.minus(this.basePay.times(taxRate));
    }
}

class HourlyEmployee {
    constructor(
        private name: string,
        private basePay: Money,
        private timeCard: number
    ) {}

    calculatePay(taxRate: number): Money {
        return this.basePay.times(this.timeCard).minus(
            this.basePay.times(this.timeCard).times(taxRate)
        );
    }
}
```

`SalariedEmployee`와 `HourlyEmployee` 클래스는 `Employee` 인터페이스에 정의된 `calculatePay` 오퍼레이션과 동일한 시그니처를 가진 퍼블릭 메서드를 포함하고 있다. 동일한 퍼블릭 인터페이스를 공유하기 때문에 동일한 타입으로 취급할 수 있다고 예상할 것이다.

하지만 자바 같은 대부분의 정적 타입 언어에서는 두 클래스를 동일한 타입으로 취급하기 위해서는 **코드상의 타입이 동일하게 선언돼 있어야만 한다**. 단순히 동일한 시그니처의 메서드를 포함한다고 해서 같은 타입으로 판단하지 않는다.

```java
// Java
public Money calculate(Employee employee, double taxRate) {
    return employee.calculatePay(taxRate);
}

calculate(new SalariedEmployee(...), 0.01);  // 컴파일 에러!
calculate(new HourlyEmployee(...), 0.01);    // 컴파일 에러!
```

이 메서드에 `SalariedEmployee`와 `HourlyEmployee` 인스턴스를 전달하기 위해서는 두 클래스가 `Employee` 인터페이스를 **명시적으로** 구현하게 해야 한다.

```java
// Java
public class SalariedEmployee implements Employee { ... }
public class HourlyEmployee implements Employee { ... }
```

### 동적 타입 언어의 덕 타이핑: Ruby

반면 런타임에 타입을 결정하는 동적 타입 언어는 특정한 클래스를 상속받거나 인터페이스를 구현하지 않고도 객체가 수신할 수 있는 메시지의 집합으로 객체의 타입을 결정할 수 있다.

```ruby
# Ruby
class SalariedEmployee
  def initialize(name, basePay)
    @name = name
    @basePay = basePay
  end

  def calculatePay(taxRate)
    @basePay - (@basePay * taxRate)
  end
end

class HourlyEmployee
  def initialize(name, basePay, timeCard)
    @name = name
    @basePay = basePay
    @timeCard = timeCard
  end

  def calculatePay(taxRate)
    (@basePay * @timeCard) - (@basePay * @timeCard) * taxRate
  end
end
```

루비 같은 동적 타입 언어에서는 명시적으로 동일한 클래스를 상속받거나 동일한 인터페이스를 구현하지 않더라도 시그니처가 동일한 메서드를 가진 클래스는 같은 타입으로 취급할 수 있다. `SalariedEmployee`와 `HourlyEmployee` 클래스의 인스턴스는 `calculatePay(taxRate)`라는 동일한 시그니처를 가진 메서드를 구현하고 있기 때문에 동일한 타입으로 간주할 수 있다.

```ruby
# Ruby
def calculate(employee, taxRate)
  employee.calculatePay(taxRate)
end

calculate(SalariedEmployee.new(...), 0.01)  # 성공!
calculate(HourlyEmployee.new(...), 0.01)    # 성공!
```

이것이 바로 덕 타이핑이다. `calculatePay(taxRate)`라는 행동을 수행할 수 있으면 이 객체를 `Employee`라고 부를 수 있는 것이다. 마치 꽥꽥거리는 모든 것을 오리라고 부르는 것처럼 말이다.

### TypeScript의 구조적 타이핑

TypeScript는 정적 타입 언어이면서도 **구조적 타이핑**(*structural typing*)을 지원한다. 이것은 덕 타이핑의 정적 타입 버전이라 할 수 있다. 명시적으로 `implements`를 선언하지 않아도 구조가 호환되면 동일한 타입으로 취급한다.

```typescript
// TypeScript
interface Employee {
    calculatePay(taxRate: number): Money;
}

class SalariedEmployee {
    constructor(private name: string, private basePay: Money) {}

    calculatePay(taxRate: number): Money {
        return this.basePay.minus(this.basePay.times(taxRate));
    }
}

class HourlyEmployee {
    constructor(
        private name: string,
        private basePay: Money,
        private timeCard: number
    ) {}

    calculatePay(taxRate: number): Money {
        return this.basePay.times(this.timeCard).minus(
            this.basePay.times(this.timeCard).times(taxRate)
        );
    }
}

function calculate(employee: Employee, taxRate: number): Money {
    return employee.calculatePay(taxRate);
}

calculate(new SalariedEmployee(...), 0.01);  // 성공! implements 없이도 가능
calculate(new HourlyEmployee(...), 0.01);    // 성공! 구조만 호환되면 된다
```

TypeScript에서 `SalariedEmployee`와 `HourlyEmployee`는 `Employee` 인터페이스를 명시적으로 구현(`implements`)하지 않았지만, `calculatePay(taxRate: number): Money`라는 동일한 시그니처의 메서드를 가지고 있으므로 `Employee` 타입으로 취급된다. 이것이 구조적 타이핑의 핵심이다.

> **핵심 통찰**: 덕 타이핑은 타입이 행동에 대한 것이라는 사실을 강조한다. 두 객체가 동일하게 행동한다면 내부 구현이 어떤 방식이든 상관없다. 타입 관점에서 두 객체는 동일한 타입인 것이다. 덕 타이핑은 클래스나 인터페이스에 대한 의존성을 메시지에 대한 의존성으로 대체한다. 결과적으로 코드는 낮은 결합도를 유지하고 변경에 유연하게 대응할 수 있다.

### C#의 dynamic 키워드

정적 타입 언어 중에서도 부분적으로나마 덕 타이핑을 지원하는 언어들이 있다. C#의 닷넷 프레임워크 버전 4에 적용된 `dynamic` 키워드를 사용하면 덕 타이핑을 흉내 낼 수 있다.

```csharp
// C#
public class SalariedEmployee
{
    private string name;
    private decimal basePay;

    public SalariedEmployee(string name, decimal basePay)
    {
        this.name = name;
        this.basePay = basePay;
    }

    public decimal CalculatePay(decimal taxRate)
    {
        return basePay - basePay * taxRate;
    }
}

public class HourlyEmployee
{
    private string name;
    private decimal basePay;
    private int timeCard;

    public HourlyEmployee(string name, decimal basePay, int timeCard)
    {
        this.name = name;
        this.basePay = basePay;
        this.timeCard = timeCard;
    }

    public decimal CalculatePay(decimal taxRate)
    {
        return (basePay * timeCard) - (basePay * timeCard) * taxRate;
    }
}
```

`SalariedEmployee` 클래스와 `HourlyEmployee` 클래스를 동일한 타입으로 묶어주는 어떤 선언도 존재하지 않는다. 하지만 아래와 같이 `dynamic` 키워드를 추가하면 `CalculatePay` 메시지에 응답할 수 있는 어떤 객체라도 파라미터로 전달하는 것이 가능해진다. `Calculate` 메서드는 클래스나 인터페이스 수준의 결합도를 메시지 수준의 결합도로 낮춘다.

```csharp
// C#
public decimal Calculate(dynamic employee, decimal taxRate)
{
    return employee.CalculatePay(taxRate);
}

Calculate(new SalariedEmployee(...), 0.01m);  // 성공!
Calculate(new HourlyEmployee(...), 0.01m);    // 성공!
```

### C++의 템플릿

C++에서 제네릭 프로그래밍을 구현하는 템플릿(*template*)은 타입 안전성과 덕 타이핑이라는 두 가지 장점을 성공적으로 조합한다.

```cpp
// C++
class SalariedEmployee {
private:
    string name;
    long base_pay;
public:
    SalariedEmployee(string name, long base_pay);
    long calculate_pay(double tax_rate);
};

long SalariedEmployee::calculate_pay(double tax_rate) {
    return base_pay - (base_pay * tax_rate);
}

class HourlyEmployee {
private:
    string name;
    long base_pay;
    int time_card;
public:
    HourlyEmployee(string name, long base_pay, int time_card);
    long calculate_pay(double tax_rate);
};

long HourlyEmployee::calculate_pay(double tax_rate) {
    return (base_pay * time_card) - (base_pay * time_card) * tax_rate;
}
```

두 클래스는 동일한 시그니처를 가지는 `calculate_pay(double tax_rate)` 메서드를 구현하고 있지만, 두 클래스를 동일한 타입으로 묶어주는 어떤 명시적인 타입 선언도 존재하지 않는다. C++ 컴파일러의 관점에서 두 클래스는 별개의 타입이다.

하지만 아래와 같이 템플릿을 사용하면 관계가 없는 두 클래스를 동일한 타입으로 취급하는 것이 가능하다.

```cpp
// C++
template <typename T>
long calculate(T employee, double tax_rate) {
    return employee.calculate_pay(tax_rate);
}
```

`calculate` 함수는 첫 번째 파라미터로 임의의 타입 `T`의 인스턴스를 취하는 함수 템플릿(*function template*)이다. `calculate` 함수가 타입 파라미터 `T`에게 요구하는 것은 단 한 가지다. 인자로 전달되는 객체의 클래스가 `calculate_pay` 메시지를 이해해야 한다는 것이다. 따라서 `calculate` 함수의 첫 번째 파라미터에 대해 덕 타이핑을 지원한다.

더 반가운 소식은 첫 번째 `T` 타입 인자로 전달되는 객체가 `calculate_pay` 함수를 구현하고 있는지를 **런타임이 아닌 컴파일 시점에 체크**할 수 있다는 것이다. 따라서 C++의 템플릿 시스템은 정적 타입 언어의 장점인 타입 안전성까지도 보장해 준다.

### 덕 타이핑의 트레이드오프

| 방식 | 유연성 | 타입 안전성 | 비용 |
|---|---|---|---|
| **동적 타입 언어 (Ruby)** | 매우 높음 | 낮음 (런타임 오류) | 없음 |
| **C# dynamic** | 높음 | 낮음 (런타임 오류) | 없음 |
| **C++ 템플릿** | 높음 | 높음 (컴파일 타임 체크) | 타입별 함수 복사본 생성으로 프로그램 크기 증가 |
| **TypeScript 구조적 타이핑** | 높음 | 높음 (컴파일 타임 체크) | 없음 |

> 객체지향 설계의 목표는 코드의 수정 비용을 줄이는 것이다. 우리는 애플리케이션 설계의 핵심은 메시지라는 점도 알고 있고 엄격하게 정의된 퍼블릭 인터페이스를 구축하는 과정이 왜 중요한지도 알고 있다. 이 기술의 이름은 덕 타이핑이다. 덕 타입은 특정 클래스에 종속되지 않은 퍼블릭 인터페이스다. 여러 클래스를 가로지르는 이런 인터페이스는 클래스에 대한 값비싼 의존을 메시지에 대한 부드러운 의존으로 대치시킨다. 그리고 애플리케이션을 굉장히 유연하게 만들어 준다 [Metz12].

---

## 7. 믹스인과 타입 계층

믹스인(*mixin*)은 객체를 생성할 때 코드 일부를 섞어 넣을 수 있도록 만들어진 일종의 추상 서브클래스다. 언어마다 구현 방법에 차이는 있지만 믹스인을 사용하는 목적은 다양한 객체 구현 안에서 동일한 **행동**을 중복 코드 없이 재사용할 수 있게 만드는 것이다.

여기서 "행동"이라는 단어에 주목하라. 믹스인을 통해 코드를 재사용하는 객체들은 동일한 행동을 공유하게 된다. 다시 말해 공통의 행동이 믹스인된 객체들은 동일한 메시지를 수신할 수 있는 퍼블릭 인터페이스를 공유하게 되는 것이다. 타입은 퍼블릭 인터페이스와 관련이 있기 때문에 **대부분의 믹스인을 구현하는 기법들은 타입을 정의하는 것으로 볼 수 있다**.

### Scala의 트레이트

이해를 돕기 위해 스칼라 언어에서 믹스인을 구현하기 위해 제공하는 트레이트(*trait*)를 살펴보자. 다양한 애플리케이션을 작성하다 보면 동일한 타입의 객체들을 비교해야 할 필요가 있다. 이럴 때마다 매번 모든 클래스에 비교 연산자를 추가하는 것은 고역스러울 수밖에 없다.

이 문제를 해결하기 위해 스칼라는 비교와 관련된 공통적인 구현을 믹스인해서 재사용할 수 있게 `Ordered`라는 트레이트를 제공한다. `Ordered` 트레이트는 내부적으로 추상 메서드 `compare`를 사용해 `<`, `>`, `<=`, `>=` 연산자를 구현한다.

```scala
// Scala
trait Ordered[A] extends Any with Comparable[A] {
  def compare(that: A): Int

  def <  (that: A): Boolean = (this compare that) <  0
  def >  (that: A): Boolean = (this compare that) >  0
  def <= (that: A): Boolean = (this compare that) <= 0
  def >= (that: A): Boolean = (this compare that) >= 0

  def compareTo(that: A): Int = compare(that)
}
```

이제 비교 연산자를 추가하고 싶은 클래스에 `Ordered` 트레이트를 믹스인하고 추상 메서드 `compare`를 오버라이딩하기만 하면 공짜로 `<`, `>`, `<=`, `>=` 연산자를 퍼블릭 인터페이스에 추가할 수 있게 된다. 예를 들어, 금액을 표현하는 `Money` 클래스에 비교 연산자를 추가하고 싶다면 다음과 같이 `Ordered` 트레이트를 믹스인하면 된다.

```scala
// Scala
case class Money(amount: Long) extends Ordered[Money] {
  def + (that: Money): Money = Money(this.amount + that.amount)
  def - (that: Money): Money = Money(this.amount - that.amount)
  def compare(that: Money): Int = (this.amount - that.amount).toInt
}
```

`Ordered` 트레이트는 구현뿐만 아니라 퍼블릭 메서드를 퍼블릭 인터페이스에 추가하기 때문에 이제 `Money`는 `Ordered` 트레이트를 요구하는 모든 위치에서 `Ordered`를 대체할 수 있다. 이것은 서브타입의 요건인 리스코프 치환 원칙을 만족시키기 때문에 `Money`는 `Ordered` 타입으로 분류될 수 있다.

### 간결한 인터페이스 → 풍부한 인터페이스

`Money` 예제는 최근의 객체지향 언어에서 **풍부한 인터페이스**(*rich interface*)를 만들기 위해 믹스인을 사용하는 경향을 잘 보여준다. `Ordered` 트레이트를 믹스인하기 전의 `Money`는 `+` 연산자와 `-` 연산자만을 퍼블릭 인터페이스에 포함하고 있는 **간결한 인터페이스**(*thin interface*)를 가진 클래스였다. 하지만 `Ordered` 트레이트를 믹스인하고 추상 메서드 `compare`를 구현하는 순간 `Money`의 퍼블릭 인터페이스 안에는 `<`, `>`, `<=`, `>=`라는 다수의 연산자가 자동으로 추가된다. 결과적으로 `Money`의 인터페이스는 더 많은 연산자로 인해 풍부해졌다.

> 트레이트의 주된 사용법 중 하나는 어떤 클래스에 그 클래스가 이미 갖고 있는 메서드를 기반으로 하는 새로운 메서드를 추가하는 것이다. 다시 말해서 간결한 인터페이스를 풍부한 인터페이스로 만들 때 트레이트를 사용할 수 있다. ... 트레이트를 이용해 인터페이스를 풍성하게 만들고 싶다면 트레이트에 간결한 인터페이스 역할을 하는 추상 메서드를 구현하고 그런 추상 메서드를 활용해 풍부한 인터페이스 역할을 할 여러 메서드를 같은 트레이트 안에서 구현하면 된다 [Odersky11].

### Java 8의 디폴트 메서드

스칼라의 트레이트와 유사하게 자바 8에 새롭게 추가된 디폴트 메서드(*default method*)는 인터페이스에 메서드의 기본 구현을 추가하는 것을 허용한다. 인터페이스에 디폴트 메서드가 구현돼 있다면 이 인터페이스를 구현하는 클래스는 기본 구현을 가지고 있는 메서드를 구현할 필요가 없다. 디폴트 메서드를 사용하면 추상 클래스가 제공하는 코드 재사용성이라는 혜택을 그대로 누리면서도 특정한 상속 계층에 얽매이지 않는 인터페이스의 장점을 유지할 수 있다.

```java
// Java
public interface DiscountPolicy {
    default Money calculateDiscountAmount(Screening screening) {
        for (DiscountCondition each : getConditions()) {
            if (each.isSatisfiedBy(screening)) {
                return getDiscountAmount(screening);
            }
        }
        return screening.getMovieFee();
    }

    List<DiscountCondition> getConditions();
    Money getDiscountAmount(Screening screening);
}
```

### 디폴트 메서드의 한계

디폴트 메서드가 제공하는 혜택을 누리면서 설계를 견고하게 유지하기 위해서는 디폴트 메서드가 가지는 **한계를 분명하게 인식**하는 것이 중요하다.

인터페이스와 추상 클래스를 혼합했던 방식에서는 보이지 않던 `getConditions` 오퍼레이션과 `getDiscountAmount` 오퍼레이션이 인터페이스에 추가된 것을 확인할 수 있다. 이것은 디폴트 메서드인 `calculateDiscountAmount` 메서드가 내부적으로 두 개의 메서드를 사용하기 때문에 이 인터페이스를 구현하는 모든 클래스들이 해당 메서드의 구현을 제공해야 한다는 것을 명시한 것이다.

문제는 이 메서드들이 인터페이스에 정의돼 있기 때문에 클래스 안에서 **퍼블릭 메서드로 구현돼야 한다**는 것이다. 추상 클래스를 사용했던 경우에는 `getDiscountAmount` 메서드의 가시성이 `protected`였다는 것을 기억하라. `getDiscountAmount` 메서드가 원래는 구현을 위해 추상 클래스 내부에서만 사용될 메서드였기 때문이었다.

하지만 이제 디폴트 메서드 안에서 사용된다는 이유만으로 `public` 메서드가 돼야 한다. 이것은 **외부에 노출할 필요가 없는 메서드를 불필요하게 퍼블릭 인터페이스에 추가**하는 결과를 낳게 된다.

`getConditions` 메서드의 경우에는 문제가 더 심각한데, 클래스 내부에서 `DiscountCondition`의 목록을 관리한다는 사실을 외부에 공개할 뿐만 아니라 `public` 메서드를 제공함으로써 이 목록에 접근할 수 있게 해준다. 이것은 설계의 제1원칙으로 강조해 왔던 **캡슐화를 약화**시킨다.

| 비교 항목 | 추상 클래스 + 인터페이스 | 디폴트 메서드 |
|---|---|---|
| `getDiscountAmount` 가시성 | `protected` (내부 구현용) | `public` (인터페이스 규약) |
| `getConditions` 노출 여부 | 비공개 (추상 클래스 내부) | `public` (캡슐화 위반) |
| 코드 중복 | 없음 (추상 클래스에서 공유) | 있음 (`conditions` 필드와 `getConditions`이 각 클래스에 중복) |
| 인스턴스 변수 | 추상 클래스에서 관리 | 각 구현 클래스에서 개별 관리 |

게다가 이 방법은 `AmountDiscountPolicy`와 `PercentDiscountPolicy` 클래스 사이의 코드 중복을 완벽하게 제거해 주지도 못한다. 인터페이스가 메서드 구현을 포함할 수는 있지만 인스턴스 변수를 포함할 수는 없기 때문에, `conditions` 필드와 `getConditions()` 메서드가 각 구현 클래스에 중복된다.

> **핵심 통찰**: 자바 8에 디폴트 메서드를 추가한 이유는 인터페이스로 추상 클래스의 역할을 대체하려는 것이 아니다. 디폴트 메서드가 추가된 이유는 기존에 널리 사용되고 있는 인터페이스에 새로운 오퍼레이션을 추가할 경우에 발생하는 하위 호환성 문제를 해결하기 위해서지 추상 클래스를 제거하기 위한 것이 아니다. 따라서 타입을 정의하기 위해 디폴트 메서드를 사용할 생각이라면 그 한계를 명확하게 알아두어야 한다.

---

## 설계 원칙

| 원칙 | 설명 |
|---|---|
| **타입 ≠ 클래스** | 타입은 퍼블릭 인터페이스, 클래스는 구현. 하나의 클래스가 여러 타입을, 여러 클래스가 동일한 타입을 구현할 수 있다 |
| **타입 중심 설계** | 클래스가 아니라 타입에 집중하라. 중요한 것은 객체가 외부에 제공하는 행동이다 |
| **추상 클래스 우선** | 구체 클래스를 직접 상속하지 말고, 모든 구체 클래스의 부모 클래스를 추상 클래스로 만들어라 |
| **인터페이스 + 추상 클래스 결합** | 상속 계층에 얽매이지 않는 유연한 타입 계층이 필요하면 인터페이스로 타입을 정의하고 골격 구현 추상 클래스로 중복을 제거하라 |
| **디폴트 메서드의 한계 인식** | 디폴트 메서드는 하위 호환성을 위한 것이지 추상 클래스를 대체하기 위한 것이 아니다 |
| **리스코프 치환 원칙 준수** | 어떤 구현 방법을 사용하든 타입 계층의 올바름은 LSP 준수 여부에 달려 있다 |

---

## 요약

- **타입과 클래스는 동일한 개념이 아니다**. 타입은 객체의 퍼블릭 인터페이스를 의미하고, 클래스는 타입을 구현하는 한 가지 방법일 뿐이다.
- **클래스를 이용한 타입 계층 구현**은 상속을 통해 가장 간단하게 달성할 수 있지만, 구체 클래스 상속은 자식 클래스를 부모 클래스의 구현에 강하게 결합시킨다.
- **인터페이스를 이용한 타입 계층 구현**은 다중 분류를 지원하고, 클래스 상속 없이도 타입 계층을 구성할 수 있으며, 여러 클래스가 동일한 타입을, 하나의 클래스가 여러 타입을 구현할 수 있게 한다.
- **추상 클래스를 이용한 타입 계층 구현**은 추상 메서드를 통해 자식 클래스가 구현이 아닌 추상화에 의존하게 만들며, 의존성 역전 원칙을 따르는 유연한 설계를 가능하게 한다.
- **인터페이스와 추상 클래스를 결합**하면 상속 계층에 얽매이지 않으면서도 코드 중복을 제거할 수 있다. 이를 골격 구현 추상 클래스라고 부른다.
- **덕 타이핑**은 객체가 수행하는 행동에 기반하여 타입을 결정하는 방법으로, 클래스나 인터페이스에 대한 의존성을 메시지에 대한 의존성으로 대체하여 유연성을 높인다. TypeScript의 구조적 타이핑은 컴파일 타임 안전성과 덕 타이핑의 유연성을 결합한다.
- **믹스인**은 간결한 인터페이스를 풍부한 인터페이스로 만들기 위해 사용된다. 스칼라의 트레이트와 자바 8의 디폴트 메서드가 대표적이지만, 디폴트 메서드는 캡슐화 약화와 코드 중복이라는 한계가 있다.
- **어떤 구현 방법을 사용하더라도** 타입 사이에 리스코프 치환 원칙을 준수하지 않는다면 올바른 타입 계층을 구현한 것이 아니다.

---

## 다른 챕터와의 관계

- **10장 (상속과 코드 재사용)**: `Phone`과 `NightlyDiscountPhone`의 구체 클래스 상속 예제가 등장한다. 이 부록은 10장에서 겪은 상속의 문제점을 해결하는 다양한 대안을 제시한다.
- **12장 (다형성)**: 이 부록에서 다루는 모든 타입 계층 구현 방법은 동시에 다형성을 구현하는 방법이기도 하다. 동적 메서드 탐색과 유사한 방식으로 적절한 메서드를 검색한다.
- **13장 (서브클래싱과 서브타이핑)**: 타입과 타입 계층의 개념적 의미를 설명한다. 이 부록은 13장의 개념을 코드로 옮기는 방법을 다룬다. 올바른 타입 계층을 위해서는 리스코프 치환 원칙 준수가 필수다.
- **11장 (합성과 유연한 설계)**: 인터페이스 + 추상 클래스 결합 방식은 상속의 문제를 완화하면서도 합성의 유연성에 가까운 설계를 가능하게 한다.
