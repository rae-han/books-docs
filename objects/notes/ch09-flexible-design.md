# Chapter 9: Flexible Design (유연한 설계)

## 핵심 질문

유연하고 재사용 가능한 설계를 만들기 위한 원칙에는 무엇이 있는가? 개방-폐쇄 원칙, 생성과 사용의 분리, 의존성 주입, 의존성 역전 원칙은 어떻게 설계의 유연성을 높이며, 유연성은 언제 가치 있고 언제 불필요한 복잡성이 되는가?

---

## 1. 개방-폐쇄 원칙 (Open-Closed Principle)

8장에서는 유연하고 재사용 가능한 설계를 만들기 위한 다양한 의존성 관리 기법들을 소개했다. 이번 장에서는 이 기법들을 **원칙**이라는 관점에서 정리한다. 이름을 가진 설계 원칙을 통해 기법들을 정리하는 것은 개념과 메커니즘을 또렷하게 정리할 수 있게 도와줄 뿐만 아니라 설계를 논의할 때 사용할 수 있는 공통의 어휘를 익힌다는 점에서도 가치가 있다.

로버트 마틴은 확장 가능하고 변화에 유연하게 대응할 수 있는 설계를 만들 수 있는 원칙 중 하나로 **개방-폐쇄 원칙**(*Open-Closed Principle, OCP*)을 고안했다[Martin02]. 개방-폐쇄 원칙은 다음과 같은 문장으로 요약할 수 있다.

> 소프트웨어 개체(클래스, 모듈, 함수 등등)는 **확장에 대해 열려 있어야 하고**, **수정에 대해서는 닫혀 있어야 한다**.

여기서 키워드는 **확장**과 **수정**이다. 이 둘은 순서대로 애플리케이션의 '동작'과 '코드'의 관점을 반영한다.

| 개념 | 의미 |
|---|---|
| **확장에 대해 열려 있다** | 애플리케이션의 요구사항이 변경될 때 이 변경에 맞게 새로운 '동작'을 추가해서 애플리케이션의 기능을 확장할 수 있다 |
| **수정에 대해 닫혀 있다** | 기존의 '코드'를 수정하지 않고도 애플리케이션의 동작을 추가하거나 변경할 수 있다 |

처음에는 동작을 확장하는 것과 코드를 수정하지 않는 것이 서로 대립되는 개념으로 보일 수도 있다. 일반적으로 애플리케이션의 동작을 확장하기 위해서는 코드를 수정하지 않는가? 어떻게 코드를 수정하지 않고도 새로운 동작을 추가할 수 있단 말인가?

### 1.1 컴파일타임 의존성을 고정시키고 런타임 의존성을 변경하라

사실 개방-폐쇄 원칙은 **런타임 의존성**과 **컴파일타임 의존성**에 관한 이야기다. 런타임 의존성은 실행 시에 협력에 참여하는 객체들 사이의 관계다. 컴파일타임 의존성은 코드에서 드러나는 클래스들 사이의 관계다. 유연하고 재사용 가능한 설계에서 런타임 의존성과 컴파일타임 의존성은 서로 다른 구조를 가진다.

영화 예매 시스템의 할인 정책을 의존성 관점에서 다시 살펴보자. 컴파일타임 의존성 관점에서 `Movie` 클래스는 추상 클래스인 `DiscountPolicy`에 의존한다. 런타임 의존성 관점에서 `Movie` 인스턴스는 `AmountDiscountPolicy`와 `PercentDiscountPolicy` 인스턴스에 의존한다.

```
  ┌─ 컴파일타임 의존성 ──────────────────────┐
  │                                         │
  │    Movie ─────────▶ DiscountPolicy      │
  │                         △               │
  └─────────────────────────┼───────────────┘
                     ┌──────┴──────┐
               AmountDiscount  PercentDiscount
                 Policy          Policy

  ┌─ 런타임 의존성 ──────────────────────────┐
  │                                         │
  │  :Movie ───▶ :AmountDiscountPolicy      │
  │  :Movie ───▶ :PercentDiscountPolicy     │
  │                                         │
  └─────────────────────────────────────────┘
```

사실 할인 정책 설계는 이미 개방-폐쇄 원칙을 따르고 있다. 8장에서 중복 할인 정책(`OverlappedDiscountPolicy`)을 추가했던 것을 떠올려 보자. 중복 할인 정책을 추가하기 위해 한 일은 `DiscountPolicy`의 자식 클래스로 `OverlappedDiscountPolicy` 클래스를 추가한 것뿐이다. 기존의 `Movie`, `DiscountPolicy`, `AmountDiscountPolicy`, `PercentDiscountPolicy` 중 어떤 코드도 수정하지 않았다. `NoneDiscountPolicy`의 구현 역시 마찬가지다. 기존 코드는 전혀 손대지 않은 채 `NoneDiscountPolicy` 클래스를 추가하는 것만으로 할인 정책이 적용되지 않는 영화를 구현할 수 있었다.

두 경우 모두 기존 클래스는 전혀 수정하지 않은 채 애플리케이션의 동작을 확장했다. 단순히 새로운 클래스를 추가하는 것만으로 `Movie`를 새로운 컨텍스트에 사용되도록 확장할 수 있었던 것이다.

```
  ┌─ 컴파일타임 의존성 (변경 없음) ─────────────────────┐
  │                                                   │
  │    Movie ─────────▶ DiscountPolicy                │
  │                         △                         │
  └─────────────────────────┼─────────────────────────┘
                     ┌──────┼──────┐
               AmountDiscount  PercentDiscount
                 Policy     │    Policy
                            │
                      Overlapped        ← 새로 추가
                    DiscountPolicy

  ┌─ 런타임 의존성 (확장됨) ────────────────────────────┐
  │                                                   │
  │  :Movie ───▶ :AmountDiscountPolicy                │
  │  :Movie ───▶ :PercentDiscountPolicy               │
  │  :Movie ───▶ :OverlappedDiscountPolicy  ← 새로움  │
  │                                                   │
  └───────────────────────────────────────────────────┘
```

개방-폐쇄 원칙을 수용하는 코드는 **컴파일타임 의존성을 수정하지 않고도 런타임 의존성을 쉽게 변경할 수 있다**. 의존성 관점에서 개방-폐쇄 원칙을 따르는 설계란 컴파일타임 의존성은 유지하면서 런타임 의존성의 가능성을 확장하고 수정할 수 있는 구조라고 할 수 있다.

### 1.2 추상화가 핵심이다

개방-폐쇄 원칙의 핵심은 **추상화에 의존하는 것**이다. 여기서 '추상화'와 '의존'이라는 두 개념 모두가 중요하다.

추상화란 핵심적인 부분만 남기고 불필요한 부분은 생략함으로써 복잡성을 극복하는 기법이다. 추상화 과정을 거치면 문맥이 바뀌더라도 변하지 않는 부분만 남게 되고 문맥에 따라 변하는 부분은 생략된다. 추상화를 사용하면 생략된 부분을 문맥에 적합한 내용으로 채워 넣음으로써 각 문맥에 적합하게 기능을 구체화하고 확장할 수 있다.

개방-폐쇄 원칙의 관점에서:

- **생략되지 않고 남겨지는 부분**: 다양한 상황에서의 공통점을 반영한 추상화의 결과물이다. 공통적인 부분은 문맥이 바뀌더라도 변하지 않는다. 따라서 **수정에 대해 닫혀 있다**.
- **추상화를 통해 생략된 부분**: 확장의 여지를 남긴다. 언제라도 생략된 부분을 채워 넣음으로써 새로운 문맥에 맞게 기능을 **확장할 수 있다**.

이해를 돕기 위해 `DiscountPolicy`의 코드를 살펴보자.

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

`DiscountPolicy`는 할인 여부를 판단해서 요금을 계산하는 `calculateDiscountAmount` 메서드와 조건을 만족할 때 할인된 요금을 계산하는 추상 메서드인 `getDiscountAmount` 메서드로 구성돼 있다. 여기서 **변하지 않는 부분**은 할인 여부를 판단하는 로직이고, **변하는 부분**은 할인된 요금을 계산하는 방법이다. 따라서 `DiscountPolicy`는 추상화다. 추상화 과정을 통해 생략된 부분은 할인 요금을 계산하는 방법이다. 우리는 상속을 통해 생략된 부분을 구체화함으로써 할인 정책을 확장할 수 있는 것이다.

> **핵심 통찰**: 변하지 않는 부분을 고정하고 변하는 부분을 생략하는 추상화 메커니즘이 개방-폐쇄 원칙의 기반이 된다. 언제라도 추상화의 생략된 부분을 채워 넣음으로써 새로운 문맥에 맞게 기능을 확장할 수 있다. 따라서 추상화는 설계의 확장을 가능하게 한다.

단순히 어떤 개념을 추상화했다고 해서 수정에 대해 닫혀 있는 설계를 만들 수 있는 것은 아니다. 개방-폐쇄 원칙에서 **폐쇄를 가능하게 하는 것은 의존성의 방향**이다. 수정에 대한 영향을 최소화하기 위해서는 모든 요소가 추상화에 의존해야 한다. `Movie` 클래스를 살펴보자.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Movie {
    // ...
    private DiscountPolicy discountPolicy;

    public Movie(String title, Duration runningTime, Money fee, DiscountPolicy discountPolicy) {
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
    private discountPolicy: DiscountPolicy;

    constructor(
        private title: string,
        private runningTime: number,
        private fee: Money,
        discountPolicy: DiscountPolicy
    ) {
        this.discountPolicy = discountPolicy;
    }

    calculateMovieFee(screening: Screening): Money {
        return this.fee.minus(
            this.discountPolicy.calculateDiscountAmount(screening)
        );
    }
}
```

`Movie`는 할인 정책을 추상화한 `DiscountPolicy`에 대해서만 의존한다. 의존성은 변경의 영향을 의미하고 `DiscountPolicy`는 변하지 않는 추상화라는 사실에 주목하라. `Movie`는 안정된 추상화인 `DiscountPolicy`에 의존하기 때문에 할인 정책을 추가하기 위해 `DiscountPolicy`의 자식 클래스를 추가하더라도 영향을 받지 않는다. 따라서 `Movie`와 `DiscountPolicy`는 수정에 대해 닫혀 있다.

```
  Movie ─────────▶ DiscountPolicy (추상화)
                        │
           ┌────────────┼────────────┐
    AmountDiscount  PercentDiscount  ...새 정책
      Policy          Policy

  추상화 → 확장을 가능하게 한다
  추상화에 대한 의존 → 폐쇄를 가능하게 한다
```

올바른 추상화를 설계하고 추상화에 대해서만 의존하도록 관계를 제한함으로써 설계를 유연하게 확장할 수 있다.

여기서 주의할 점은 추상화를 했다고 해서 모든 수정에 대해 설계가 폐쇄되는 것은 아니라는 것이다. 수정에 대해 닫혀 있고 확장에 대해 열려 있는 설계는 공짜로 얻어지지 않는다. 변경에 의한 파급효과를 최대한 피하기 위해서는 **변하는 것과 변하지 않는 것이 무엇인지를 이해하고 이를 추상화의 목적으로 삼아야만 한다**. 추상화가 수정에 대해 닫혀 있을 수 있는 이유는 변경되지 않을 부분을 신중하게 결정하고 올바른 추상화를 주의 깊게 선택했기 때문이라는 사실을 기억하라.

---

## 2. 생성 사용 분리 (Separating Use from Creation)

`Movie`가 오직 `DiscountPolicy`라는 추상화에만 의존하기 위해서는 `Movie` 내부에서 `AmountDiscountPolicy` 같은 구체 클래스의 인스턴스를 생성해서는 안 된다. 아래 코드에서 `Movie`의 할인 정책을 비율 할인 정책으로 변경할 수 있는 방법은 단 한 가지밖에 없다. 바로 `AmountDiscountPolicy`의 인스턴스를 생성하는 부분을 `PercentDiscountPolicy`의 인스턴스를 생성하도록 직접 코드를 수정하는 것뿐이다. 이것은 동작을 추가하거나 변경하기 위해 기존의 코드를 수정하도록 만들기 때문에 개방-폐쇄 원칙을 위반한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Movie {
    // ...
    private DiscountPolicy discountPolicy;

    public Movie(String title, Duration runningTime, Money fee) {
        // ...
        this.discountPolicy = new AmountDiscountPolicy(...);
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
    private discountPolicy: DiscountPolicy;

    constructor(
        private title: string,
        private runningTime: number,
        private fee: Money
    ) {
        // 구체 클래스에 직접 의존 — OCP 위반!
        this.discountPolicy = new AmountDiscountPolicy(/* ... */);
    }

    calculateMovieFee(screening: Screening): Money {
        return this.fee.minus(
            this.discountPolicy.calculateDiscountAmount(screening)
        );
    }
}
```

결합도가 높아질수록 개방-폐쇄 원칙을 따르는 구조를 설계하기가 어려워진다. 알아야 하는 지식이 많으면 결합도도 높아진다. 특히 **객체 생성에 대한 지식은 과도한 결합도를 초래하는 경향**이 있다. 객체의 타입과 생성자에 전달해야 하는 인자에 대한 과도한 지식은 코드를 특정한 컨텍스트에 강하게 결합시킨다.

물론 객체 생성을 피할 수는 없다. 어딘가에서는 반드시 객체를 생성해야 한다. 문제는 객체 생성이 아니다. **부적절한 곳에서 객체를 생성한다는 것이 문제**다. `Movie`의 코드를 자세히 살펴보면 생성자 안에서는 `DiscountPolicy`의 인스턴스를 **생성**하고, `calculateMovieFee` 메서드 안에서는 이 객체에게 메시지를 **전송**(사용)한다는 것을 알 수 있다.

```
  Movie ──── «use» ──────▶ DiscountPolicy (추상화)
    │
    └──── «create» ──────▶ AmountDiscountPolicy (구체 클래스)
```

메시지를 전송하지 않고 객체를 생성하기만 한다면 아무런 문제가 없었을 것이다. 또는 객체를 생성하지 않고 메시지를 전송하기만 했다면 괜찮았을 것이다. **동일한 클래스 안에서 객체 생성과 사용이라는 두 가지 이질적인 목적을 가진 코드가 공존하는 것이 문제**인 것이다.

> **핵심 통찰**: 유연하고 재사용 가능한 설계를 원한다면 객체와 관련된 두 가지 책임을 서로 다른 객체로 분리해야 한다. 하나는 객체를 **생성**하는 것이고, 다른 하나는 객체를 **사용**하는 것이다. 한마디로 말해서 객체에 대한 **생성과 사용을 분리**(*separating use from creation*)[Bain08]해야 한다.

> 소프트웨어 시스템은 (응용 프로그램 객체를 제작하고 의존성을 서로 "연결"하는) 시작 단계와 (시작 단계 이후에 이어지는) 실행 단계를 분리해야 한다[Martin08].

### 2.1 클라이언트에게 생성 책임 위임하기

사용으로부터 생성을 분리하는 데 사용되는 가장 보편적인 방법은 **객체를 생성할 책임을 클라이언트로 옮기는 것**이다. 다시 말해서 `Movie`의 클라이언트가 적절한 `DiscountPolicy` 인스턴스를 생성한 후 `Movie`에게 전달하게 하는 것이다.

`Movie`에게 금액 할인 정책을 적용할지, 비율 할인 정책을 적용할지를 알고 있는 것은 그 시점에 `Movie`와 협력할 **클라이언트**이기 때문이다. 현재의 컨텍스트에 관한 결정권을 가지고 있는 클라이언트로 컨텍스트에 대한 지식을 옮김으로써 `Movie`는 특정한 클라이언트에 결합되지 않고 독립적일 수 있다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Client {
    public Money getAvatarFee() {
        Movie avatar = new Movie("아바타",
            Duration.ofMinutes(120),
            Money.wons(10000),
            new AmountDiscountPolicy(...));
        return avatar.getFee();
    }
}
```

</details>

```typescript
// TypeScript
class Client {
    getAvatarFee(): Money {
        const avatar = new Movie(
            "아바타",
            120,
            Money.wons(10000),
            new AmountDiscountPolicy(/* ... */)  // 클라이언트가 생성 책임을 가짐
        );
        return avatar.getFee();
    }
}
```

```
  ┌─ 생성 책임 분리 후 ────────────────────────────────────┐
  │                                                       │
  │  Client ── «create» ──▶ AmountDiscountPolicy          │
  │    │                                                  │
  │    └── «use» ──▶ Movie ── «use» ──▶ DiscountPolicy   │
  │                                                       │
  └───────────────────────────────────────────────────────┘
```

`Movie`의 의존성을 추상화인 `DiscountPolicy`로만 제한하기 때문에 확장에 대해서는 열려 있으면서도 수정에 대해서는 닫혀 있는 코드를 만들 수 있는 것이다.

### 2.2 FACTORY 추가하기

생성 책임을 `Client`로 옮긴 배경에는 `Movie`는 특정 컨텍스트에 묶여서는 안 되지만 `Client`는 묶여도 상관이 없다는 전제가 깔려 있다. 하지만 `Movie`를 사용하는 `Client`도 특정한 컨텍스트에 묶이지 않기를 바란다고 가정해 보자.

`Client`의 코드를 다시 살펴보면 `Movie`의 인스턴스를 **생성**하는 동시에 `getFee` 메시지도 함께 **전송**한다는 것을 알 수 있다. `Client` 역시 생성과 사용의 책임을 함께 지니고 있는 것이다.

이 경우 객체 생성과 관련된 책임만 전담하는 별도의 객체를 추가하고 `Client`는 이 객체를 사용하도록 만들 수 있다. 이처럼 생성과 사용을 분리하기 위해 객체 생성에 특화된 객체를 **FACTORY**라고 부른다[Evans03].

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Factory {
    public Movie createAvatarMovie() {
        return new Movie("아바타",
            Duration.ofMinutes(120),
            Money.wons(10000),
            new AmountDiscountPolicy(...));
    }
}
```

</details>

```typescript
// TypeScript
class Factory {
    createAvatarMovie(): Movie {
        return new Movie(
            "아바타",
            120,
            Money.wons(10000),
            new AmountDiscountPolicy(/* ... */)
        );
    }
}
```

이제 `Client`는 `Factory`를 사용해서 생성된 `Movie`의 인스턴스를 반환받아 사용하기만 하면 된다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Client {
    private Factory factory;

    public Client(Factory factory) {
        this.factory = factory;
    }

    public Money getAvatarFee() {
        Movie avatar = factory.createAvatarMovie();
        return avatar.getFee();
    }
}
```

</details>

```typescript
// TypeScript
class Client {
    constructor(private factory: Factory) {}

    getAvatarFee(): Money {
        const avatar = this.factory.createAvatarMovie();
        return avatar.getFee();
    }
}
```

FACTORY를 사용하면 `Movie`와 `AmountDiscountPolicy`를 생성하는 책임 모두를 FACTORY로 이동할 수 있다. 이제 `Client`에는 사용과 관련된 책임만 남게 되는데 하나는 FACTORY를 통해 생성된 `Movie` 객체를 얻기 위한 것이고 다른 하나는 `Movie`를 통해 가격을 계산하기 위한 것이다. `Client`는 오직 사용과 관련된 책임만 지고 생성과 관련된 어떤 지식도 가지지 않을 수 있다.

```
  ┌─ FACTORY 추가 후 ──────────────────────────────────────────┐
  │                                                           │
  │  Client ── «use» ──▶ Movie ── «use» ──▶ DiscountPolicy   │
  │    │                                         △            │
  │    └── «use» ──▶ Factory                     │            │
  │                    │                         │            │
  │                    ├── «create» ──▶ Movie    │            │
  │                    └── «create» ──▶ AmountDiscountPolicy  │
  │                                                           │
  └───────────────────────────────────────────────────────────┘
```

### 2.3 순수한 가공물에게 책임 할당하기

5장에서 책임 할당 원칙을 패턴의 형태로 기술한 GRASP 패턴에 관해 살펴봤다. 책임 할당의 가장 기본이 되는 원칙은 책임을 수행하는 데 필요한 정보를 가장 많이 알고 있는 **INFORMATION EXPERT**에게 책임을 할당하는 것이다. 도메인 모델은 INFORMATION EXPERT를 찾기 위해 참조할 수 있는 일차적인 재료다.

방금 전에 추가한 `Factory`는 도메인 모델에 속하지 않는다는 사실에 주목하라. FACTORY를 추가한 이유는 순수하게 기술적인 결정이다. 전체적으로 결합도를 낮추고 재사용성을 높이기 위해 도메인 개념에게 할당돼 있던 객체 생성 책임을 도메인 개념과는 아무런 상관이 없는 가공의 객체로 이동시킨 것이다.

크레이그 라만은 시스템을 객체로 분해하는 데는 크게 두 가지 방식이 존재한다고 설명한다[Larman04]:

| 분해 방식 | 설명 |
|---|---|
| **표현적 분해** (*representational decomposition*) | 도메인에 존재하는 사물 또는 개념을 표현하는 객체들을 이용해 시스템을 분해하는 것. 도메인 모델에 담겨 있는 개념과 관계를 따르며 도메인과 소프트웨어 사이의 표현적 차이를 최소화하는 것을 목적으로 한다. 객체지향 설계를 위한 가장 기본적인 접근법이다. |
| **행위적 분해** (*behavioral decomposition*) | 도메인 개념을 표현하는 객체에게 책임을 할당하는 것만으로는 부족할 때, 설계자가 편의를 위해 임의로 만들어낸 가공의 객체에게 책임을 할당하는 것. |

종종 도메인 개념을 표현하는 객체에게 책임을 할당하는 것만으로는 부족한 경우가 발생한다. 모든 책임을 도메인 객체에게 할당하면 낮은 응집도, 높은 결합도, 재사용성 저하와 같은 심각한 문제점에 봉착하게 될 가능성이 높아진다. 이 경우 도메인 개념을 표현한 객체가 아닌 설계자가 편의를 위해 임의로 만들어낸 가공의 객체에게 책임을 할당해서 문제를 해결해야 한다. 크레이그 라만은 이처럼 책임을 할당하기 위해 창조되는 도메인과 무관한 인공적인 객체를 **PURE FABRICATION**(*순수한 가공물*)이라고 부른다[Larman04].

어떤 행동을 추가하려고 하는데 이 행동을 책임질 마땅한 도메인 개념이 존재하지 않는다면 PURE FABRICATION을 추가하고 이 객체에게 책임을 할당하라. 그 결과로 추가된 PURE FABRICATION은 보통 특정한 행동을 표현하는 것이 일반적이다. 따라서 PURE FABRICATION은 표현적 분해보다는 행위적 분해에 의해 생성되는 것이 일반적이다.

> 객체지향 애플리케이션은 도메인 개념뿐만 아니라 설계자들이 임의적으로 창조한 인공적인 추상화들을 포함하고 있다. 애플리케이션 내에서 인공적으로 창조한 객체들이 도메인 개념을 반영하는 객체들보다 오히려 더 많은 비중을 차지하는 것이 일반적이다. 이것은 현대적인 도시가 자연물보다는 건물이나 도로와 같은 인공물로 가득 차 있는 것과 유사하다.

설계자로서의 역할은 도메인 추상화를 기반으로 애플리케이션 로직을 설계하는 동시에 품질의 측면에서 균형을 맞추는 데 필요한 객체들을 창조하는 것이다. 도메인 개념을 표현하는 객체와 순수하게 창조된 가공의 객체들이 모여 자신의 역할과 책임을 다하고 조화롭게 협력하는 애플리케이션을 설계하는 것이 목표여야 한다.

먼저 도메인의 본질적인 개념을 표현하는 추상화를 이용해 애플리케이션을 구축하기 시작하라. 만약 도메인 개념이 만족스럽지 못하다면 주저하지 말고 인공적인 객체를 창조하라. 객체지향이 실세계를 모방해야 한다는 헛된 주장에 현혹될 필요가 없다. 우리가 애플리케이션을 구축하는 것은 사용자들이 원하는 기능을 제공하기 위해서지 실세계를 모방하거나 시뮬레이션하기 위한 것이 아니다.

> **핵심 통찰**: FACTORY는 객체의 생성 책임을 할당할 만한 도메인 객체가 존재하지 않을 때 선택할 수 있는 PURE FABRICATION이다. 대부분의 디자인 패턴은 PURE FABRICATION을 포함한다. 도메인 모델에서 출발해서 설계에 유연성을 추가하기 위해 책임을 이리저리 옮기다 보면 많은 PURE FABRICATION을 추가하게 된다는 사실을 알게 될 것이다.

---

## 3. 의존성 주입 (Dependency Injection)

생성과 사용을 분리하면 `Movie`에는 오로지 인스턴스를 **사용**하는 책임만 남게 된다. 이것은 외부의 다른 객체가 `Movie`에게 생성된 인스턴스를 전달해야 한다는 것을 의미한다. 이처럼 사용하는 객체가 아닌 외부의 독립적인 객체가 인스턴스를 생성한 후 이를 전달해서 의존성을 해결하는 방법을 **의존성 주입**(*Dependency Injection*)[Fowler04]이라고 부른다. 이 기법을 의존성 주입이라고 부르는 이유는 외부에서 의존성의 대상을 해결한 후 이를 사용하는 객체 쪽으로 **주입**하기 때문이다.

의존성 주입은 근본적으로 8장에서 설명한 의존성 해결 방법과 관련이 깊다. 의존성 해결은 컴파일타임 의존성과 런타임 의존성의 차이점을 해소하기 위한 다양한 메커니즘을 포괄한다. 의존성 주입은 의존성을 해결하기 위해 의존성을 객체의 퍼블릭 인터페이스에 명시적으로 드러내서 외부에서 필요한 런타임 의존성을 전달할 수 있도록 만드는 방법을 포괄하는 명칭이다.

의존성 주입에서는 의존성을 해결하는 세 가지 방법을 가리키는 별도의 용어를 정의한다.

| 주입 방식 | 설명 | 특징 |
|---|---|---|
| **생성자 주입** (*constructor injection*) | 객체를 생성하는 시점에 생성자를 통한 의존성 해결 | 객체의 생명주기 전체에 걸쳐 관계를 유지. 필수 의존성을 명확하게 표현 |
| **setter 주입** (*setter injection*) | 객체 생성 후 setter 메서드를 통한 의존성 해결 | 런타임에 의존 대상 교체 가능. 단, 호출 누락 시 비정상 상태 생성 가능 |
| **메서드 주입** (*method injection*) | 메서드 실행 시 인자를 이용한 의존성 해결 | 의존성이 한두 개 메서드에서만 사용될 때 적합 |

### 3.1 생성자 주입

다음은 `Movie` 생성자의 인자로 `AmountDiscountPolicy`의 인스턴스를 전달해서 `DiscountPolicy` 클래스에 대한 컴파일타임 의존성을 런타임 의존성으로 대체하는 예를 나타낸 것이다. `Movie`의 생성자를 이용해 의존성을 주입하기 때문에 **생성자 주입**이라고 부른다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
Movie avatar = new Movie("아바타",
    Duration.ofMinutes(120),
    Money.wons(10000),
    new AmountDiscountPolicy(...));
```

</details>

```typescript
// TypeScript
const avatar = new Movie(
    "아바타",
    120,
    Money.wons(10000),
    new AmountDiscountPolicy(/* ... */)  // 생성자 주입
);
```

### 3.2 setter 주입

setter 주입은 이미 생성된 `Movie`에 대해 setter 메서드를 이용해 의존성을 해결한다. setter 주입의 장점은 의존성의 대상을 런타임에 변경할 수 있다는 것이다. 생성자 주입을 통해 설정된 인스턴스는 객체의 생명주기 전체에 걸쳐 관계를 유지하는 반면, setter 주입을 사용하면 언제라도 의존 대상을 교체할 수 있다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
avatar.setDiscountPolicy(new AmountDiscountPolicy(...));
```

</details>

```typescript
// TypeScript
avatar.setDiscountPolicy(new AmountDiscountPolicy(/* ... */));
```

setter 주입의 단점은 객체가 올바로 생성되기 위해 어떤 의존성이 필수적인지를 명시적으로 표현할 수 없다는 것이다. setter 메서드는 객체가 생성된 후에 호출돼야 하기 때문에 setter 메서드 호출을 누락한다면 객체는 비정상적인 상태로 생성될 것이다.

### 3.3 메서드 주입

메서드 주입은 메서드 호출 주입(*method call injection*)이라고도 부르며 메서드가 의존성을 필요로 하는 유일한 경우일 때 사용할 수 있다[Hall14]. 생성자 주입을 통해 의존성을 전달받으면 객체가 올바른 상태로 생성되는 데 필요한 의존성을 명확하게 표현할 수 있다는 장점이 있지만 주입된 의존성이 한두 개의 메서드에서만 사용된다면 각 메서드의 인자로 전달하는 것이 더 나은 방법일 수 있다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
avatar.calculateDiscountAmount(screening, new AmountDiscountPolicy(...));
```

</details>

```typescript
// TypeScript
avatar.calculateDiscountAmount(
    screening,
    new AmountDiscountPolicy(/* ... */)  // 메서드 주입
);
```

### 3.4 숨겨진 의존성은 나쁘다

의존성 주입 외에도 의존성을 해결할 수 있는 다양한 방법이 존재한다. 그중에서 가장 널리 사용되는 대표적인 방법은 **SERVICE LOCATOR** 패턴[Alur03]이다. SERVICE LOCATOR는 의존성을 해결할 객체들을 보관하는 일종의 저장소다. 외부에서 객체에게 의존성을 전달하는 의존성 주입과 달리 SERVICE LOCATOR의 경우 객체가 직접 SERVICE LOCATOR에게 의존성을 해결해 줄 것을 요청한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Movie {
    private DiscountPolicy discountPolicy;

    public Movie(String title, Duration runningTime, Money fee) {
        this.title = title;
        this.runningTime = runningTime;
        this.fee = fee;
        this.discountPolicy = ServiceLocator.discountPolicy();
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
        private fee: Money
    ) {
        // SERVICE LOCATOR에게 의존성 해결 요청
        this.discountPolicy = ServiceLocator.discountPolicy();
    }
}
```

`ServiceLocator`는 `DiscountPolicy`의 인스턴스를 등록하고 반환할 수 있는 메서드를 구현한 저장소다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class ServiceLocator {
    private static ServiceLocator soleInstance = new ServiceLocator();
    private DiscountPolicy discountPolicy;

    public static DiscountPolicy discountPolicy() {
        return soleInstance.discountPolicy;
    }

    public static void provide(DiscountPolicy discountPolicy) {
        soleInstance.discountPolicy = discountPolicy;
    }

    private ServiceLocator() {}
}
```

</details>

```typescript
// TypeScript
class ServiceLocator {
    private static soleInstance = new ServiceLocator();
    private discountPolicy: DiscountPolicy | null = null;

    static getDiscountPolicy(): DiscountPolicy {
        return this.soleInstance.discountPolicy!;
    }

    static provide(discountPolicy: DiscountPolicy): void {
        this.soleInstance.discountPolicy = discountPolicy;
    }

    private constructor() {}
}
```

사용 방법은 다음과 같다. `Movie`의 인스턴스가 `AmountDiscountPolicy`의 인스턴스에 의존하기를 원한다면 `ServiceLocator`에 인스턴스를 등록한 후 `Movie`를 생성하면 된다.

```typescript
// TypeScript
ServiceLocator.provide(new AmountDiscountPolicy(/* ... */));
const avatar = new Movie("아바타", 120, Money.wons(10000));
```

여기까지만 보면 SERVICE LOCATOR 패턴은 의존성을 해결할 수 있는 가장 쉽고 간단한 도구인 것처럼 보인다. 하지만 SERVICE LOCATOR 패턴의 가장 큰 단점은 **의존성을 감춘다**는 것이다. `Movie`는 `DiscountPolicy`에 의존하고 있지만 `Movie`의 퍼블릭 인터페이스 어디에도 이 의존성에 대한 정보가 표시돼 있지 않다. 의존성은 암시적이며 코드 깊숙한 곳에 숨겨져 있다.

숨겨진 의존성이 나쁜 이유를 이해하기 위해 다음과 같이 `Movie`를 생성하는 코드와 마주쳤다고 가정해 보자.

```typescript
// TypeScript
const avatar = new Movie("아바타", 120, Money.wons(10000));
```

위 코드를 읽는 개발자는 인스턴스 생성에 필요한 모든 인자를 `Movie`의 생성자에 전달하고 있기 때문에 `Movie`는 온전한 상태로 생성될 것이라고 예상할 것이다. 하지만 아래 코드를 실행해 보면 `NullPointerException`(또는 TypeScript에서는 런타임 오류)이 발생한다.

```typescript
// TypeScript
avatar.calculateMovieFee(screening); // 💥 오류! discountPolicy가 null
```

디버깅을 시작한 개발자는 인스턴스 변수인 `discountPolicy`의 값이 `null`이라는 사실을 알게 되고 코드를 분석하기 시작할 것이다. 그리고 마침내 `Movie`의 생성자가 `ServiceLocator`를 이용해 의존성을 해결한다는 사실을 알게 되고 `Movie`의 인스턴스를 생성하기 바로 전에 다음과 같은 코드를 추가해서 문제를 해결할 것이다.

```typescript
// TypeScript
ServiceLocator.provide(new PercentDiscountPolicy(/* ... */));
const avatar = new Movie("아바타", 120, Money.wons(10000));
```

숨겨진 의존성이 가지는 문제점을 정리하면 다음과 같다:

1. **의존성 문제가 런타임에 발견된다**: 의존성을 구현 내부로 감출 경우 의존성과 관련된 문제가 컴파일타임이 아닌 런타임에 가서야 발견된다.
2. **단위 테스트 작성이 어렵다**: `ServiceLocator`는 내부적으로 정적 변수를 사용해 객체들을 관리하기 때문에 모든 단위 테스트 케이스에 걸쳐 `ServiceLocator`의 상태를 공유하게 된다. 이것은 각 단위 테스트는 서로 고립돼야 한다는 단위 테스트의 기본 원칙을 위반한 것이다[Meszaros07].
3. **캡슐화를 위반한다**: 클래스의 사용법을 익히기 위해 구현 내부를 샅샅이 뒤져야 한다면 그 클래스의 캡슐화는 무너진 것이다. 숨겨진 의존성이 가지는 가장 큰 문제점은 의존성을 이해하기 위해 코드의 내부 구현을 이해할 것을 강요한다는 것이다.
4. **설정 시점과 해결 시점이 멀리 떨어진다**: `ServiceLocator`의 `provide` 메서드를 실행하는 코드와 `Movie`의 인스턴스를 실행하는 코드가 멀리 떨어져 있으면 디버깅이 매우 어려워진다.

> **핵심 통찰**: 의존성 주입은 이 문제를 깔끔하게 해결한다. 필요한 의존성은 클래스의 퍼블릭 인터페이스에 명시적으로 드러난다. 의존성을 이해하기 위해 코드 내부를 읽을 필요가 없기 때문에 의존성 주입은 객체의 캡슐을 단단하게 보호한다. 이야기의 핵심은 "의존성 주입이 SERVICE LOCATOR 패턴보다 좋다"가 아니라 **명시적인 의존성이 숨겨진 의존성보다 좋다**는 것이다.

가급적 의존성을 객체의 퍼블릭 인터페이스에 노출하라. 의존성을 구현 내부에 숨기면 숨길수록 코드를 이해하기도, 수정하기도 어려워진다.

어쩔 수 없이 SERVICE LOCATOR 패턴을 사용해야 하는 경우도 있다. 의존성 주입을 지원하는 프레임워크를 사용하지 못하는 경우나 깊은 호출 계층에 걸쳐 동일한 객체를 계속해서 전달해야 하는 고통을 견디기 어려운 경우에는 어쩔 수 없이 SERVICE LOCATOR 패턴을 사용하는 것을 고려하라.

> 접근해야 할 객체가 있다면 전역 메커니즘 대신, 필요한 객체를 인수로 넘겨줄 수는 없는지부터 생각해 보자. 이 방법은 굉장히 쉬운 데다 결합을 명확하게 보여줄 수 있다. 대부분은 이렇게만 해도 충분하다.
>
> 하지만 직접 객체를 넘기는 방식이 불필요하거나 도리어 코드를 읽기 어렵게 하기도 한다. 로그나 메모리 관리 같은 정보가 모듈의 공개 API에 포함돼 있어서는 안 된다. 렌더링 함수 매개변수에는 렌더링에 관련된 것만 있어야 하며 로그 같은 것이 섞여 있어서는 곤란하다.
>
> 또한 어떤 시스템은 본질적으로 하나뿐이다. 대부분의 게임 플랫폼에는 오디오나 디스플레이 시스템이 하나만 있다. 이런 환경적인 특징을 10겹의 메서드 계층을 통해 가장 깊숙이 들어 있는 함수에 전달하는 것은 쓸데없이 복잡성을 늘리는 셈이다[Nystrom14].

가능하다면 의존성을 명시적으로 표현할 수 있는 기법을 사용하라. 의존성 주입은 의존성을 명시적으로 명시할 수 있는 방법 중 하나일 뿐이다. 요점은 **명시적인 의존성에 초점을 맞추는 것**이다. 그리고 이 방법이 유연성을 향상시키는 가장 효과적인 방법이다.

---

## 4. 의존성 역전 원칙 (Dependency Inversion Principle)

### 4.1 추상화와 의존성 역전

`Movie`를 다음과 같이 구현했을 때 어떤 문제가 발생할지를 예상할 수 있을 것이다. `Movie`는 구체 클래스에 대한 의존성으로 인해 결합도가 높아지고 재사용성과 유연성이 저해된다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Movie {
    private AmountDiscountPolicy discountPolicy;
}
```

</details>

```typescript
// TypeScript
class Movie {
    private discountPolicy: AmountDiscountPolicy;  // 구체 클래스에 의존!
}
```

이 설계가 변경에 취약한 이유는 요금을 계산하는 **상위 정책이 요금을 계산하는 데 필요한 구체적인 방법에 의존하기 때문**이다. `Movie`는 가격 계산이라는 더 높은 수준의 개념을 구현한다. 그에 비해 `AmountDiscountPolicy`는 영화의 가격에서 특정한 금액만큼을 할인해 주는 더 구체적인 수준의 메커니즘을 담당하고 있다. 다시 말해서 상위 수준 클래스인 `Movie`가 하위 수준 클래스인 `AmountDiscountPolicy`에 의존하는 것이다.

```
  Movie ─────────▶ AmountDiscountPolicy
  (상위 수준)           (하위 수준)

  상위 수준이 하위 수준에 의존 → 변경에 취약!
```

객체 사이의 협력이 존재할 때 그 협력의 본질을 담고 있는 것은 **상위 수준의 정책**이다. `Movie`와 `AmountDiscountPolicy` 사이의 협력이 가지는 본질은 영화의 가격을 계산하는 것이다. 어떻게 할인 금액을 계산할 것인지는 협력의 본질이 아니다. 다시 말해서 어떤 협력에서 중요한 정책이나 의사결정, 비즈니스의 본질을 담고 있는 것은 상위 수준의 클래스다.

그러나 이런 상위 수준의 클래스가 하위 수준의 클래스에 의존한다면 하위 수준의 변경에 의해 상위 수준 클래스가 영향을 받게 될 것이다. 하위 수준의 `AmountDiscountPolicy`를 `PercentDiscountPolicy`로 변경한다고 해서 상위 수준의 `Movie`가 영향을 받아서는 안 된다. 상위 수준의 `Movie`의 변경으로 인해 하위 수준의 `AmountDiscountPolicy`가 영향을 받아야 한다.

이 설계는 재사용성에도 문제가 있다. `Movie`를 재사용하기 위해서는 `Movie`가 의존하는 `AmountDiscountPolicy` 역시 함께 재사용해야 한다. 대부분의 경우 우리가 재사용하려는 대상은 상위 수준의 클래스라는 점을 기억하라.

이 경우에도 해결사는 **추상화**다. `Movie`와 `AmountDiscountPolicy` 모두가 추상화에 의존하도록 수정하면 하위 수준 클래스의 변경으로 인해 상위 수준의 클래스가 영향을 받는 것을 방지할 수 있다. 또한 상위 수준을 재사용할 때 하위 수준의 클래스에 얽매이지 않고도 다양한 컨텍스트에서 재사용이 가능하다. 이것이 `Movie`와 `AmountDiscountPolicy` 사이에 추상 클래스인 `DiscountPolicy`가 자리 잡고 있는 이유다.

```
  ┌─ 의존성 역전 적용 전 ──────────────────────┐
  │                                           │
  │  Movie ─────────▶ AmountDiscountPolicy    │
  │  (상위)              (하위)                │
  │                                           │
  └───────────────────────────────────────────┘

  ┌─ 의존성 역전 적용 후 ──────────────────────┐
  │                                           │
  │  Movie ─────────▶ DiscountPolicy (추상화)  │
  │                        △                  │
  │                        │                  │
  │               AmountDiscountPolicy        │
  │               PercentDiscountPolicy       │
  │                                           │
  │  상위 수준과 하위 수준 모두 추상화에 의존!    │
  └───────────────────────────────────────────┘
```

가장 중요한 조언은 **추상화에 의존하라**는 것이다. 유연하고 재사용 가능한 설계를 원한다면 모든 의존성의 방향이 추상 클래스나 인터페이스와 같은 추상화를 따라야 한다. 구체 클래스는 의존성의 시작점이어야 한다. 의존성의 목적지가 돼서는 안 된다.

이제 지금까지 살펴본 내용들을 정리해 보자.

1. **상위 수준의 모듈은 하위 수준의 모듈에 의존해서는 안 된다. 둘 모두 추상화에 의존해야 한다.**
2. **추상화는 구체적인 사항에 의존해서는 안 된다. 구체적인 사항은 추상화에 의존해야 한다.**

이를 **의존성 역전 원칙**(*Dependency Inversion Principle, DIP*)[Martin02]이라고 부른다. 이 용어를 최초로 착안한 로버트 마틴은 '역전(inversion)'이라는 단어를 사용한 이유에 대해 의존성 역전 원칙을 따르는 설계는 의존성의 방향이 전통적인 절차형 프로그래밍과는 반대 방향으로 나타나기 때문이라고 설명한다.

> 수년 동안, 많은 사람들이 왜 필자가 이 원칙의 이름에 '역전'이란 단어를 사용했는지 질문해 왔다. 이것은 구조적 분석 설계와 같은 좀 더 전통적인 소프트웨어 개발 방법에서는 소프트웨어 구조에서 상위 수준의 모듈이 하위 수준의 모듈에 의존하는, 그리고 정책이 구체적인 것에 의존하는 경향이 있었기 때문이다. 실제로 이런 방법의 목표 중 하나는 상위 수준의 모듈이 하위 수준의 모듈을 호출하는 방법을 묘사하는 서브프로그램의 계층 구조를 정의하는 것이었다. ... 잘 설계된 객체지향 프로그램의 의존성 구조는 전통적인 절차적 방법에 의해 일반적으로 만들어진 의존성 구조에 대해 '역전'된 것이다[Martin02].

### 4.2 의존성 역전 원칙과 패키지

의존성 역전 원칙과 관련해서 한 가지 더 언급할 가치가 있는 내용이 있다. **역전은 의존성의 방향뿐만 아니라 인터페이스의 소유권에도 적용된다**는 것이다.

할인 정책과 관련된 패키지의 구조가 다음과 같다고 가정해 보자.

```
  ┌─ 전통적인 모듈 구조 ────────────────────────────────┐
  │                                                    │
  │  ┌─ 패키지 A ───┐     ┌─ 패키지 B ──────────────┐  │
  │  │              │     │                         │  │
  │  │   Movie ─────┼────▶│ DiscountPolicy          │  │
  │  │              │     │     △                    │  │
  │  └──────────────┘     │     ├── AmountDiscount   │  │
  │                       │     │     Policy         │  │
  │                       │     └── PercentDiscount  │  │
  │                       │           Policy         │  │
  │                       └─────────────────────────┘  │
  │                                                    │
  └────────────────────────────────────────────────────┘
```

`Movie`가 `DiscountPolicy`에 의존하고 있다. `Movie`를 정상적으로 컴파일하기 위해서는 `DiscountPolicy` 클래스가 필요하다. 문제는 `DiscountPolicy`가 포함돼 있는 패키지 안에 `AmountDiscountPolicy` 클래스와 `PercentDiscountPolicy` 클래스가 포함돼 있다는 것이다. 이것은 `DiscountPolicy` 클래스에 의존하기 위해서는 반드시 같은 패키지에 포함된 `AmountDiscountPolicy` 클래스와 `PercentDiscountPolicy` 클래스도 함께 존재해야 한다는 것을 의미한다.

C++ 같은 언어에서는 같은 패키지 안에 존재하는 불필요한 클래스들로 인해 빈번한 재컴파일과 재배포가 발생할 수 있다. `DiscountPolicy`가 포함된 패키지 안의 어떤 클래스가 수정되더라도 패키지 전체가 재배포돼야 한다. 이로 인해 이 패키지에 의존하는 `Movie` 클래스가 포함된 패키지 역시 재컴파일돼야 한다. `Movie`에 의존하는 또 다른 패키지가 있다면 컴파일은 의존성의 그래프를 타고 애플리케이션 코드 전체로 번져갈 것이다.

`Movie`의 재사용을 위해 필요한 것이 `DiscountPolicy`뿐이라면 `DiscountPolicy`를 `Movie`와 같은 패키지로 모으고 `AmountDiscountPolicy`와 `PercentDiscountPolicy`를 별도의 패키지에 위치시켜 의존성 문제를 해결할 수 있다. 마틴 파울러는 이 기법을 가리켜 **SEPARATED INTERFACE** 패턴[Fowler02]이라고 부른다.

```
  ┌─ 인터페이스 소유권을 역전시킨 모듈 구조 ────────────────────┐
  │                                                          │
  │  ┌─ 패키지 A ─────────────────┐  ┌─ 패키지 B ──────────┐ │
  │  │                            │  │                     │ │
  │  │  Movie ──▶ DiscountPolicy  │  │ AmountDiscount      │ │
  │  │                    △       │  │   Policy ───────┐   │ │
  │  └────────────────────┼───────┘  │                 │   │ │
  │                       │          │ PercentDiscount │   │ │
  │                       └──────────┤   Policy ───────┘   │ │
  │                                  │       │             │ │
  │                                  │       ▼             │ │
  │                                  │  (DiscountPolicy에  │ │
  │                                  │   의존)              │ │
  │                                  └─────────────────────┘ │
  │                                                          │
  └──────────────────────────────────────────────────────────┘
```

`Movie`와 추상 클래스인 `DiscountPolicy`를 하나의 패키지로 모으는 것은 `Movie`를 특정한 컨텍스트로부터 완벽하게 독립시킨다. `Movie`를 다른 컨텍스트에서 재사용하기 위해서는 단지 `Movie`와 `DiscountPolicy`가 포함된 패키지만 재사용하면 된다. 새로운 할인 정책을 위해 새로운 패키지를 추가하고 새로운 `DiscountPolicy`의 자식 클래스를 구현하기만 하면 상위 수준의 협력 관계를 재사용할 수 있다.

전통적인 설계 패러다임은 인터페이스의 소유권을 클라이언트 모듈이 아닌 **서버 모듈에 위치**시킨다. 반면 잘 설계된 객체지향 애플리케이션에서는 인터페이스의 소유권을 서버가 아닌 **클라이언트에 위치**시킨다.

> **핵심 통찰**: 유연하고 재사용 가능하며 컨텍스트에 독립적인 설계는 전통적인 패러다임이 고수하는 의존성의 방향을 역전시킨다. 전통적인 패러다임에서는 상위 수준 모듈이 하위 수준 모듈에 의존했다면 객체지향 패러다임에서는 상위 수준 모듈과 하위 수준 모듈이 모두 추상화에 의존한다. 전통적인 패러다임에서는 인터페이스가 하위 수준 모듈에 속했다면 객체지향 패러다임에서는 인터페이스가 상위 수준 모듈에 속한다. 훌륭한 객체지향 설계를 위해서는 의존성을 역전시켜야 한다.

---

## 5. 유연성에 대한 조언

### 5.1 유연한 설계는 유연성이 필요할 때만 옳다

유연하고 재사용 가능한 설계란 런타임 의존성과 컴파일타임 의존성의 차이를 인식하고 동일한 컴파일타임 의존성으로부터 다양한 런타임 의존성을 만들 수 있는 코드 구조를 가지는 설계를 의미한다. 하지만 유연하고 재사용 가능한 설계가 **항상 좋은 것은 아니다**. 설계의 미덕은 단순함과 명확함으로부터 나온다. 단순하고 명확한 설계를 가진 코드는 읽기 쉽고 이해하기도 편하다. 유연한 설계는 이와는 다른 길을 걷는다. 변경하기 쉽고 확장하기 쉬운 구조를 만들기 위해서는 단순함과 명확함의 미덕을 버리게 될 가능성이 높다.

유연한 설계라는 말의 이면에는 **복잡한 설계**라는 의미가 숨어 있다.

| 유연한 설계 | 단순한 설계 |
|---|---|
| 복잡하고 암시적이다 | 단순하고 명확하다 |
| 변경하기 쉽고 확장하기 쉽다 | 읽기 쉽고 이해하기 편하다 |
| 클래스 구조와 객체 구조 사이의 거리가 멀다 | 정적 구조가 곧 동적 구조다 |

변경은 예상이 아니라 **현실**이어야 한다. 미래에 변경이 일어날지도 모른다는 막연한 불안감은 불필요하게 복잡한 설계를 낳는다. 아직 일어나지 않은 변경은 변경이 아니다.

유연성은 항상 복잡성을 수반한다. 유연하지 않은 설계는 단순하고 명확하다. 유연한 설계는 복잡하고 암시적이다. 객체지향에 입문한 개발자들이 가장 이해하기 어려워하는 부분이 바로 코드 상에 표현된 정적인 클래스의 구조와 실행 시점의 동적인 객체 구조가 다르다는 사실이다.

설계가 유연할수록 클래스 구조와 객체 구조 사이의 거리는 점점 떨어진다. 따라서 유연함은 단순성과 명확성의 희생 위에서 자라난다. 유연한 설계를 단순하고 명확하게 만드는 유일한 방법은 사람들 간의 긴밀한 커뮤니케이션뿐이다. 복잡성이 필요한 이유와 합리적인 근거를 제시하지 않는다면 어느 누구도 설계를 만족스러운 해법으로 받아들이지 않을 것이다.

**불필요한 유연성은 불필요한 복잡성을 낳는다.** 단순하고 명확한 해법이 그런대로 만족스럽다면 유연성을 제거하라. 유연성은 코드를 읽는 사람들이 복잡함을 수용할 수 있을 때만 가치가 있다. 하지만 복잡성에 대한 걱정보다 유연하고 재사용 가능한 설계의 필요성이 더 크다면 코드의 구조와 실행 구조를 다르게 만들어라.

> 우리의 지적 능력은 정적인 관계에 더 잘 들어맞고, 시간에 따른 진행 과정을 시각화하는 능력은 상대적으로 덜 발달했다. 이러한 이유로 우리는 (자신의 한계를 알고 있는 현명한 프로그래머로서) 정적인 프로그램과 동적인 프로세스 사이의 간극을 줄이기 위해 최선을 다해야 하며, 이를 통해 프로그램(텍스트 공간에 흩뿌려진)과 (시간에 흩뿌려진) 진행 과정 사이를 가능한 한 일치시켜야 한다[Dijkstra68].

### 5.2 협력과 책임이 중요하다

마지막으로 하고 싶은 말은 객체의 **협력과 책임이 중요하다**는 것이다. 지금까지 클래스를 중심으로 구현 메커니즘 관점에서 의존성을 설명했지만 설계를 유연하게 만들기 위해서는 협력에 참여하는 객체가 다른 객체에게 **어떤 메시지를 전송하는지**가 중요하다.

`Movie`가 다양한 할인 정책과 협력할 수 있는 이유는 무엇인가? 모든 할인 정책이 `Movie`가 전송하는 `calculateDiscountAmount` 메시지를 이해할 수 있기 때문이다. 이들 모두 요금을 계산하기 위한 협력에 참여하면서 할인 요금을 계산하는 책임을 수행할 수 있으며 `Movie`의 입장에서 동일한 역할을 수행할 수 있다.

```
                          PercentDiscountPolicy
                        ╱
  Movie ───▶ DiscountPolicy ─── OverlappedDiscountPolicy
        calculateDiscount  ╲
          Amount()           AmountDiscountPolicy
                            ╲
                              NoneDiscountPolicy

  Movie의 관점에서 동일한 역할을 수행하는 객체들
```

설계를 유연하게 만들기 위해서는 먼저 역할, 책임, 협력에 초점을 맞춰야 한다. 다양한 컨텍스트에서 협력을 재사용할 필요가 없다면 설계를 유연하게 만들 당위성도 함께 사라진다. 객체들이 메시지 전송자의 관점에서 동일한 책임을 수행하는지 여부를 판단할 수 없다면 공통의 추상화를 도출할 수 없다. 동일한 역할을 통해 객체들을 대체 가능하게 만들지 않았다면 협력에 참여하는 객체들을 교체할 필요가 없다.

> **핵심 통찰**: 초보자가 자주 저지르는 실수 중 하나는 객체의 역할과 책임이 자리를 잡기 전에 너무 성급하게 객체 생성에 집중하는 것이다. 객체를 생성할 책임을 담당할 객체나 객체 생성 메커니즘을 결정하는 시점은 책임 할당의 **마지막 단계**로 미뤄야만 한다. 중요한 비즈니스 로직을 처리하기 위해 책임을 할당하고 협력의 균형을 맞추는 것이 객체 생성에 관한 책임을 할당하는 것보다 우선이다.

불필요한 SINGLETON 패턴[GOF94]은 객체 생성에 관해 너무 이른 시기에 고민하고 결정할 때 도입되는 경향이 있다. 핵심은 **객체를 생성하는 방법에 대한 결정은 모든 책임이 자리를 잡은 후 가장 마지막 시점에 내리는 것이 적절하다**는 것이다.

> 프로젝트를 진행하는 동안, 필자의 설계 접근법들을 반영하고 있었다. 필자는 거의 무의식적으로 시종일관 수행했던 일들을 알아냈다. 그것은 바로 객체가 무엇이 되고 싶은지를 알게 될 때까지 객체들을 어떻게 인스턴스화할 것인지에 대해 전혀 신경 쓰지 않았다는 것이다. 이때 가장 중요한 관심거리는 마치 객체가 이미 존재하는 것처럼 이들 간의 관계를 신경 쓰는 일이다.
>
> 이렇게 추측했던 이유는 설계 동안 머릿속에 기억해야 할 객체 수를 최소화해야 하기 때문이다. 보통 요구사항을 충족시킬 수 있는 객체를 인스턴스화하는 방법에 대해 생각하는 것을 뒤로 미룰 때 위험을 최소화한 상태로 작업할 수 있다. 너무 일찍 결정하는 것은 비생산적이다.
>
> 객체를 생성하는 방법을 여러분 자신이 신경 쓰기 전에 시스템에 필요한 것(책임)들을 생각하자[Shalloway01].

의존성을 관리해야 하는 이유는 역할, 책임, 협력의 관점에서 설계가 유연하고 재사용 가능해야 하기 때문이다. 따라서 역할, 책임, 협력에 먼저 집중하라. 이번 장에서 설명한 다양한 기법들을 적용하기 전에 역할, 책임, 협력의 모습이 선명하게 그려지지 않는다면 의존성을 관리하는 데 들이는 모든 노력이 물거품이 될 수도 있다는 사실을 명심하라.

---

## 설계 원칙

| 원칙 | 핵심 내용 | 효과 |
|---|---|---|
| **개방-폐쇄 원칙 (OCP)** | 추상화에 의존하여 컴파일타임 의존성을 고정하고 런타임 의존성을 변경하라 | 기존 코드 수정 없이 기능 확장 가능 |
| **생성과 사용 분리** | 객체의 생성 책임과 사용 책임을 서로 다른 객체에 할당하라 | 특정 컨텍스트로부터의 독립, OCP 준수 |
| **FACTORY / PURE FABRICATION** | 도메인에 적절한 생성 책임자가 없다면 인공적인 객체를 창조하라 | 결합도 감소, 재사용성 향상 |
| **의존성 주입 (DI)** | 의존성을 퍼블릭 인터페이스에 명시적으로 드러내고 외부에서 주입하라 | 캡슐화 보호, 테스트 용이, 컴파일타임 오류 검출 |
| **의존성 역전 원칙 (DIP)** | 상위 수준과 하위 수준 모듈 모두 추상화에 의존하라. 인터페이스 소유권도 역전하라 | 상위 수준의 재사용성 확보, 변경 영향 최소화 |

---

## 요약

- **개방-폐쇄 원칙(OCP)**: 소프트웨어 개체는 확장에 대해 열려 있어야 하고 수정에 대해 닫혀 있어야 한다. 이를 달성하는 핵심은 **추상화에 의존하는 것**이다. 컴파일타임 의존성을 고정시키고 런타임 의존성을 변경함으로써 기존 코드 수정 없이 기능을 확장할 수 있다.
- **생성과 사용의 분리**: 동일한 객체 안에서 객체의 생성과 사용이라는 두 가지 이질적인 책임이 공존하면 결합도가 높아진다. 생성 책임을 클라이언트로 옮기거나 **FACTORY** 객체를 도입하여 분리하라.
- **PURE FABRICATION**: 도메인 개념을 표현하는 객체에게 모든 책임을 할당하면 응집도와 결합도 문제가 발생할 수 있다. 도메인과 무관한 인공적인 객체를 창조하여 기술적인 책임을 할당하라.
- **의존성 주입(DI)**: 외부의 독립적인 객체가 인스턴스를 생성한 후 전달해서 의존성을 해결하는 방법이다. 생성자 주입, setter 주입, 메서드 주입 세 가지 방식이 있으며, **명시적인 의존성이 숨겨진 의존성보다 항상 좋다**.
- **SERVICE LOCATOR 패턴**은 의존성을 감추기 때문에 캡슐화를 위반하고, 런타임에야 문제가 발견되며, 단위 테스트를 어렵게 만든다. 가능하다면 의존성 주입을 사용하라.
- **의존성 역전 원칙(DIP)**: 상위 수준의 모듈은 하위 수준의 모듈에 의존해서는 안 되며, 둘 모두 추상화에 의존해야 한다. 인터페이스의 소유권 역시 역전시켜 상위 수준 모듈에 위치시켜야 한다.
- **유연성은 항상 복잡성을 수반한다**. 불필요한 유연성은 불필요한 복잡성을 낳는다. 변경이 현실적으로 필요할 때만 유연한 설계를 도입하라.
- 의존성을 관리하기 전에 먼저 **역할, 책임, 협력**에 집중하라. 객체 생성에 관한 결정은 모든 책임이 자리를 잡은 후 가장 마지막 시점에 내리는 것이 적절하다.

---

## 다른 챕터와의 관계

- **Chapter 2 (객체지향 프로그래밍)**: 2장에서 설계한 영화 예매 시스템의 할인 정책 구조(`Movie` → `DiscountPolicy` → `AmountDiscountPolicy`/`PercentDiscountPolicy`)가 이 장의 모든 원칙을 설명하는 핵심 예제로 반복 등장한다. 2장에서 직관적으로 만들었던 설계가 사실은 OCP, DIP를 따르고 있었음을 이 장에서 원칙적으로 확인할 수 있다.
- **Chapter 5 (책임 할당하기)**: 5장에서 소개한 GRASP 패턴 중 INFORMATION EXPERT와 PURE FABRICATION이 이 장에서 다시 등장한다. FACTORY가 도메인 모델에 속하지 않는 PURE FABRICATION이라는 점을 5장의 개념과 연결하여 설명한다.
- **Chapter 8 (의존성 관리하기)**: 8장에서 다룬 의존성 해결 방법(생성자, setter, 메서드)이 이 장에서 의존성 주입이라는 이름으로 체계화된다. 8장의 컴파일타임/런타임 의존성, 명시적 의존성 개념이 이 장의 OCP와 DIP 설명의 토대가 된다. 8장에서 추가한 `OverlappedDiscountPolicy`가 OCP의 실례로 재활용된다.
- **Chapter 14 (일관성 있는 협력)**: 이 장에서 언급된 "대부분의 디자인 패턴은 PURE FABRICATION을 포함한다"는 주장이 14장에서 구체적으로 다뤄진다.
- **Appendix A (계약에 의한 설계)**: 이 장에서 다룬 인터페이스 중심 설계의 한계, 즉 인터페이스만으로는 구체적인 계약 조건을 표현할 수 없다는 점을 부록 A에서 계약에 의한 설계로 보완한다.
