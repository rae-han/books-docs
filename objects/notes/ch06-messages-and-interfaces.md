# Chapter 6: Messages and Interfaces (메시지와 인터페이스)

## 핵심 질문

객체지향 애플리케이션의 가장 중요한 재료는 클래스인가, 메시지인가? 유연하고 재사용 가능한 퍼블릭 인터페이스를 설계하려면 어떤 원칙과 기법을 따라야 하는가?

---

## 1. 클래스가 아니라 메시지다

객체지향 프로그래밍에 대한 가장 흔한 오해는 애플리케이션이 클래스의 집합으로 구성된다는 것이다. 대부분의 입문자들은 분석, 설계, 구현을 아우르는 전체 개발 활동의 중심에 클래스를 놓는다. 물론 클래스는 중요하다. 클래스는 개발자가 직접 만지고, 실험하고, 고쳐볼 수 있는 실제적이면서도 구체적인 도구다. 하지만 말 그대로 도구일 뿐이다. 클래스라는 구현 도구에 지나치게 집착하면 경직되고 유연하지 못한 설계에 이를 확률이 높아진다.

훌륭한 객체지향 코드를 얻기 위해서는 클래스가 아니라 객체를 지향해야 한다. 좀 더 정확하게 말해서 협력 안에서 객체가 수행하는 **책임**에 초점을 맞춰야 한다. 여기서 중요한 것은 책임이 객체가 수신할 수 있는 메시지의 기반이 된다는 것이다.

> **핵심 통찰**: 객체지향 애플리케이션의 가장 중요한 재료는 클래스가 아니라 객체들이 주고받는 **메시지**다. 클래스 사이의 정적인 관계에서 메시지 사이의 동적인 흐름으로 초점을 전환하는 것은 미숙함을 벗어나 숙련된 객체지향 설계자로 성장하기 위한 첫걸음이다. 애플리케이션은 클래스로 구성되지만 메시지를 통해 정의된다[Metz12].

객체가 수신하는 메시지들이 객체의 퍼블릭 인터페이스를 구성한다. 훌륭한 퍼블릭 인터페이스를 얻기 위해서는 책임 주도 설계 방법을 따르는 것만으로는 부족하다. 유연하고 재사용 가능한 퍼블릭 인터페이스를 만드는 데 도움이 되는 설계 원칙과 기법을 익히고 적용해야 한다.

---

## 2. 협력과 메시지

### 2.1 클라이언트-서버 모델

협력은 어떤 객체가 다른 객체에게 무언가를 요청할 때 시작된다. 메시지는 객체 사이의 협력을 가능하게 하는 매개체다. 객체가 다른 객체에게 접근할 수 있는 유일한 방법은 메시지를 전송하는 것뿐이다. 객체는 자신의 희망을 메시지라는 형태로 전송하고, 메시지를 수신한 객체는 요청을 적절히 처리한 후 응답한다. 이처럼 메시지를 매개로 하는 요청과 응답의 조합이 두 객체 사이의 협력을 구성한다.

두 객체 사이의 협력 관계를 설명하기 위해 사용하는 전통적인 메타포는 **클라이언트-서버 모델**(*Client-Server Model*)이다. 협력 안에서 메시지를 전송하는 객체를 **클라이언트**, 메시지를 수신하는 객체를 **서버**라고 부른다. 협력은 클라이언트가 서버의 서비스를 요청하는 단방향 상호작용이다.

```
┌──────────┐   가격을 계산하라   ┌─────────┐
│ Screening│ ─────────────────▶ │  Movie  │
│(클라이언트)│ ◀───────────────── │ (서버)   │
└──────────┘      예매 요금      └─────────┘
```

Movie가 최종 예매 요금을 계산하기 위해서는 할인 요금이 필요하지만 Movie에는 할인 요금을 계산하기 위해 필요한 정보가 부족하다. 따라서 Movie는 DiscountPolicy의 인스턴스에 메시지를 전송해서 할인 요금을 반환받는다. 여기서 Movie는 클라이언트의 역할을 수행하게 된다.

```
┌─────────┐  할인 요금을 계산하라  ┌────────────────┐
│  Movie  │ ──────────────────▶ │DiscountPolicy  │
│(클라이언트)│ ◀────────────────── │    (서버)       │
└─────────┘      할인 요금       └────────────────┘
```

Movie의 예에서 알 수 있는 것처럼 객체는 협력에 참여하는 동안 클라이언트와 서버의 역할을 **동시에** 수행하는 것이 일반적이다. 협력의 관점에서 객체는 두 가지 종류의 메시지 집합으로 구성된다. 하나는 객체가 수신하는 메시지의 집합이고 다른 하나는 외부의 객체에게 전송하는 메시지의 집합이다.

```
              가격을 계산하라      할인 요금을 계산하라
Screening ──────────────────▶ Movie ──────────────────▶ DiscountPolicy
          ◀────────────────── │     ◀──────────────────
                예매 요금       │          할인 요금
                               │
                         클라이언트이면서
                          동시에 서버
```

여기서 요점은 객체가 독립적으로 수행할 수 있는 것보다 더 큰 책임을 수행하기 위해서는 다른 객체와 협력해야 한다는 것이다. 그리고 두 객체 사이의 협력을 가능하게 해주는 매개체가 바로 **메시지**라는 것이다.

### 2.2 메시지와 메시지 전송

**메시지**(*message*)는 객체들이 협력하기 위해 사용할 수 있는 유일한 의사소통 수단이다. 한 객체가 다른 객체에게 도움을 요청하는 것을 **메시지 전송**(*message sending*) 또는 **메시지 패싱**(*message passing*)이라고 부른다. 이때 메시지를 전송하는 객체를 **메시지 전송자**(*message sender*), 메시지를 수신하는 객체를 **메시지 수신자**(*message receiver*)라고 부른다.

메시지는 **오퍼레이션명**(*operation name*)과 **인자**(*argument*)로 구성되며, 메시지 전송은 여기에 **메시지 수신자**를 추가한 것이다. 따라서 메시지 전송은 메시지 수신자, 오퍼레이션명, 인자의 조합이다.

```
          수신자    오퍼레이션명       인자
            │          │              │
            ▼          ▼              ▼
        condition.isSatisfiedBy(screening);
        ├──────────────────────────────────┤
                    메시지 전송

        ├──────┤
         수신자
                   ├───────────────────────┤
                          메시지
                   (오퍼레이션명 + 인자)
```

### 2.3 메시지와 메서드

메시지를 수신했을 때 실제로 어떤 코드가 실행되는지는 메시지 수신자의 실제 타입이 무엇인가에 달려 있다. `condition.isSatisfiedBy(screening)`이라는 메시지 전송 구문에서 메시지 수신자인 `condition`은 `DiscountCondition`이라는 인터페이스 타입으로 정의돼 있지만 실제로 실행되는 코드는 인터페이스를 실체화한 클래스의 종류에 따라 달라진다.

- `condition`이 `PeriodCondition`의 인스턴스라면 `PeriodCondition`에 구현된 `isSatisfiedBy` 메서드가 실행된다.
- `condition`이 `SequenceCondition`의 인스턴스라면 `SequenceCondition`에 구현된 `isSatisfiedBy` 메서드가 실행된다.

이처럼 메시지를 수신했을 때 실제로 실행되는 함수 또는 프로시저를 **메서드**라고 부른다. 중요한 것은 코드상에서 동일한 이름의 변수(`condition`)에게 동일한 메시지를 전송하더라도 **객체의 타입에 따라 실행되는 메서드가 달라질 수 있다**는 것이다.

기술적인 관점에서 객체 사이의 메시지 전송은 전통적인 방식의 함수 호출이나 프로시저 호출과는 다르다. 전통적인 방식의 개발자는 어떤 코드가 실행될지를 정확하게 알고 있는 상황에서 함수 호출이나 프로시저 호출 구문을 작성한다. 다시 말해 코드의 의미가 컴파일 시점과 실행 시점에 동일하다는 것이다. 반면 객체는 메시지와 메서드라는 두 가지 서로 다른 개념을 **실행 시점에 연결**해야 하기 때문에 컴파일 시점과 실행 시점의 의미가 달라질 수 있다.

> 객체들로 구성된 시스템 안의 행동은 두 가지 방법으로 명세할 수 있다: 메시지와 메서드. 계산을 메시지와 메서드로 분리하고 실행 시간에 수신자의 클래스에 기반해서 메시지를 메서드에 바인딩하는 것은 일반적인 프로시저 호출의 관점에서 아주 작은 변화처럼 보이지만 이 작은 변화가 커다란 차이를 만든다[Beck96].

메시지와 메서드의 구분은 메시지 전송자와 메시지 수신자가 **느슨하게 결합**될 수 있게 한다. 메시지 전송자는 자신이 어떤 메시지를 전송해야 하는지만 알면 된다. 수신자가 어떤 클래스의 인스턴스인지, 어떤 방식으로 요청을 처리하는지 모르더라도 원활한 협력이 가능하다. 메시지 수신자 역시 누가 메시지를 전송하는지 알 필요가 없다. 단지 메시지가 도착했다는 사실만 알면 된다. 실행 시점에 메시지와 메서드를 바인딩하는 메커니즘은 두 객체 사이의 결합도를 낮춤으로써 유연하고 확장 가능한 코드를 작성할 수 있게 만든다.

### 2.4 퍼블릭 인터페이스와 오퍼레이션

객체는 안과 밖을 구분하는 뚜렷한 경계를 가진다. 외부의 객체는 오직 객체가 공개하는 메시지를 통해서만 객체와 상호작용할 수 있다. 이처럼 객체가 의사소통을 위해 외부에 공개하는 메시지의 집합을 **퍼블릭 인터페이스**라고 부른다.

프로그래밍 언어의 관점에서 퍼블릭 인터페이스에 포함된 메시지를 **오퍼레이션**(*operation*)이라고 부른다. 오퍼레이션은 수행 가능한 어떤 행동에 대한 **추상화**다. 흔히 오퍼레이션이라고 부를 때는 내부의 구현 코드는 제외하고 단순히 메시지와 관련된 시그니처를 가리키는 경우가 대부분이다. 예를 들어 `DiscountCondition` 인터페이스에 정의된 `isSatisfiedBy`가 오퍼레이션에 해당한다.

그에 비해 메시지를 수신했을 때 실제로 실행되는 코드는 메서드라고 부른다. `SequenceCondition`과 `PeriodCondition`에 정의된 각각의 `isSatisfiedBy`는 실제 구현을 포함하기 때문에 메서드라고 부른다.

```
  1. 메시지 전송
┌────────┐           ┌────────┐
│ Client │──────────▶│ Server │
└────────┘           └────────┘
                  operation (인터페이스)
                     │
          2. 오퍼레이션 호출
                     │
                     ▼
                  method (구현)
                     │
              3. 메서드 실행
```

프로그래밍 언어의 관점에서 객체가 다른 객체에게 메시지를 전송하면 런타임 시스템은 메시지 전송을 오퍼레이션 호출로 해석하고, 메시지를 수신한 객체의 실제 타입을 기반으로 적절한 메서드를 찾아 실행한다.

### 2.5 시그니처

오퍼레이션(또는 메서드)의 이름과 파라미터 목록을 합쳐 **시그니처**(*signature*)라고 부른다. 오퍼레이션은 실행 코드 없이 시그니처만을 정의한 것이다. 메서드는 이 시그니처에 구현을 더한 것이다. 일반적으로 메시지를 수신하면 오퍼레이션의 시그니처와 동일한 메서드가 실행된다.

하나의 오퍼레이션에 대해 오직 하나의 메서드만 존재하는 경우 세상은 꽤나 단순해진다. 이런 경우에는 굳이 오퍼레이션과 메서드를 구분할 필요가 없다. 하지만 다형성의 축복을 받기 위해서는 하나의 오퍼레이션에 대해 다양한 메서드를 구현해야만 한다. 따라서 오퍼레이션의 관점에서 **다형성이란 동일한 오퍼레이션 호출에 대해 서로 다른 메서드들이 실행되는 것**이라고 정의할 수 있다.

### 2.6 용어 정리

| 용어 | 정의 |
|---|---|
| **메시지** | 객체가 다른 객체와 협력하기 위해 사용하는 의사소통 메커니즘. 전송자와 수신자 양쪽 모두를 포함하는 개념 |
| **오퍼레이션** | 객체가 다른 객체에게 제공하는 추상적인 서비스. 메시지 수신자의 인터페이스를 강조하며, 전송자는 고려하지 않음 |
| **메서드** | 메시지에 응답하기 위해 실행되는 코드 블록. 오퍼레이션의 구현. 동일한 오퍼레이션이라도 메서드는 다를 수 있음 |
| **퍼블릭 인터페이스** | 객체가 협력에 참여하기 위해 외부에서 수신할 수 있는 메시지의 묶음 |
| **시그니처** | 오퍼레이션이나 메서드의 명세. 이름과 인자의 목록을 포함 |

> **핵심 통찰**: 객체가 수신할 수 있는 메시지가 객체의 퍼블릭 인터페이스와 그 안에 포함될 오퍼레이션을 결정한다. 객체의 퍼블릭 인터페이스가 객체의 품질을 결정하기 때문에 결국 **메시지가 객체의 품질을 결정한다**고 할 수 있다.

---

## 3. 인터페이스와 설계 품질

3장에서 살펴본 것처럼 좋은 인터페이스는 **최소한의 인터페이스**와 **추상적인 인터페이스**라는 조건을 만족해야 한다.

- **최소한의 인터페이스**: 꼭 필요한 오퍼레이션만을 인터페이스에 포함한다.
- **추상적인 인터페이스**: 어떻게 수행하는지가 아니라 무엇을 하는지를 표현한다.

최소주의를 따르면서도 추상적인 인터페이스를 설계할 수 있는 가장 좋은 방법은 **책임 주도 설계 방법**을 따르는 것이다. 책임 주도 설계 방법은 메시지를 먼저 선택함으로써 협력과는 무관한 오퍼레이션이 인터페이스에 스며드는 것을 방지한다. 또한 객체가 메시지를 선택하는 것이 아니라 메시지가 객체를 선택하게 함으로써 클라이언트의 의도를 메시지에 표현할 수 있게 한다.

퍼블릭 인터페이스의 품질에 영향을 미치는 원칙과 기법:

1. **디미터 법칙**
2. **묻지 말고 시켜라**
3. **의도를 드러내는 인터페이스**
4. **명령-쿼리 분리**

---

## 4. 디미터 법칙 (Law of Demeter)

### 4.1 문제: 내부 구조에 대한 결합

4장에서 살펴본 절차적인 방식의 영화 예매 시스템 코드를 보자.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class ReservationAgency {
    public Reservation reserve(Screening screening, Customer customer, int audienceCount) {
        Movie movie = screening.getMovie();
        boolean discountable = false;
        for (DiscountCondition condition : movie.getDiscountConditions()) {
            if (condition.getType() == DiscountConditionType.PERIOD) {
                discountable = screening.getWhenScreened().getDayOfWeek().equals(condition.getDayOfWeek()) &&
                    condition.getStartTime().compareTo(screening.getWhenScreened().toLocalTime()) <= 0 &&
                    condition.getEndTime().compareTo(screening.getWhenScreened().toLocalTime()) >= 0;
            } else {
                discountable = condition.getSequence() == screening.getSequence();
            }
            if (discountable) {
                break;
            }
        }
        // ...
    }
}
```

</details>

```typescript
// TypeScript
class ReservationAgency {
    reserve(screening: Screening, customer: Customer, audienceCount: number): Reservation {
        const movie = screening.getMovie();
        let discountable = false;
        for (const condition of movie.getDiscountConditions()) {
            if (condition.getType() === DiscountConditionType.PERIOD) {
                discountable = screening.getWhenScreened().getDay() === condition.getDayOfWeek() &&
                    condition.getStartTime() <= screening.getWhenScreened().toLocalTime() &&
                    condition.getEndTime() >= screening.getWhenScreened().toLocalTime();
            } else {
                discountable = condition.getSequence() === screening.getSequence();
            }
            if (discountable) break;
        }
        // ...
    }
}
```

이 코드의 가장 큰 단점은 `ReservationAgency`와 인자로 전달된 `Screening` 사이의 결합도가 너무 높기 때문에 `Screening`의 내부 구현을 변경할 때마다 `ReservationAgency`도 함께 변경된다는 것이다. 문제의 원인은 `ReservationAgency`가 `Screening`뿐만 아니라 `Movie`와 `DiscountCondition`에도 직접 접근하기 때문이다.

```
┌──────────────────┐
│ ReservationAgency │──────┬───────────┬────────────────────┐
│    reserve()     │      │           │                    │
└──────────────────┘      │           │                    │
        │                 ▼           ▼                    ▼
        │          ┌───────────┐ ┌─────────┐  ┌──────────────────┐
        │          │ Screening │ │  Movie  │  │DiscountCondition │
        │          │ sequence  │ │ title   │  │ type             │
        │          │ whenScr.  │ │ fee     │  │ sequence         │
        │          └───────────┘ │ discCond│  │ dayOfWeek        │
        │                        └─────────┘  │ startTime/endTime│
        │                                     └──────────────────┘
        ▼
  Screening의 내부 구조와 강하게 결합
  → 변경에 취약한 ReservationAgency
```

### 4.2 디미터 법칙의 정의

이처럼 협력하는 객체의 내부 구조에 대한 결합으로 인해 발생하는 설계 문제를 해결하기 위해 제안된 원칙이 바로 **디미터 법칙**(*Law of Demeter*)이다. 디미터 법칙을 간단하게 요약하면 **객체의 내부 구조에 강하게 결합되지 않도록 협력 경로를 제한하라**는 것이다.

디미터 법칙은 다양한 별명으로 불린다:

| 별명 | 의미 |
|---|---|
| **낯선 자에게 말하지 말라** (Don't talk to strangers) | 직접 알고 있는 객체에게만 메시지를 전송하라 |
| **오직 인접한 이웃하고만 말하라** (Only talk to your immediate neighbors) | 간접적으로 알게 된 객체에는 접근하지 말라 |
| **오직 하나의 도트만 사용하라** (Use only one dot) | 메서드 체인을 통한 깊은 탐색을 피하라 |

디미터 법칙을 따르기 위해서는 클래스가 특정한 조건을 만족하는 대상에게만 메시지를 전송하도록 프로그래밍해야 한다. 모든 클래스 C와 C에 구현된 모든 메서드 M에 대해서, M이 메시지를 전송할 수 있는 모든 객체는 다음에 서술된 클래스의 인스턴스여야 한다:

- **this 객체**
- **메서드의 매개변수**
- **this의 속성** (인스턴스 변수)
- **this의 속성인 컬렉션의 요소**
- **메서드 내에서 생성된 지역 객체**

### 4.3 디미터 법칙 적용

4장에서 결합도 문제를 해결하기 위해 수정한 `ReservationAgency`의 최종 코드를 보자.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class ReservationAgency {
    public Reservation reserve(Screening screening, Customer customer, int audienceCount) {
        Money fee = screening.calculateFee(audienceCount);
        return new Reservation(customer, screening, fee, audienceCount);
    }
}
```

</details>

```typescript
// TypeScript
class ReservationAgency {
    reserve(screening: Screening, customer: Customer, audienceCount: number): Reservation {
        const fee = screening.calculateFee(audienceCount);
        return new Reservation(customer, screening, fee, audienceCount);
    }
}
```

이 코드에서 `ReservationAgency`는 메서드의 인자로 전달된 `Screening` 인스턴스에게만 메시지를 전송한다. `ReservationAgency`는 `Screening` 내부에 대한 어떤 정보도 알지 못한다. `Screening`의 내부 구조에 결합돼 있지 않기 때문에 `Screening`의 내부 구현을 변경할 때 `ReservationAgency`를 함께 변경할 필요가 없다.

```
┌──────────────────┐                    ┌───────────┐
│ ReservationAgency │───calculateFee()──▶│ Screening │
│    reserve()     │                    │           │──▶ Movie ──▶ DiscountCondition
└──────────────────┘                    └───────────┘
                                              │
    ReservationAgency는                    내부 구조는
    Screening에게만 메시지 전송             Screening이 캡슐화
```

### 4.4 기차 충돌 (Train Wreck)

디미터 법칙을 위반하는 코드의 전형적인 모습은 다음과 같다:

```java
screening.getMovie().getDiscountConditions();
```

메시지 전송자가 수신자의 내부 구조에 대해 물어보고 반환받은 요소에 대해 연쇄적으로 메시지를 전송한다. 이와 같은 코드를 **기차 충돌**(*train wreck*)이라고 부르는데, 여러 대의 기차가 한 줄로 늘어서 충돌한 것처럼 보이기 때문이다. 기차 충돌은 클래스의 내부 구현이 외부로 노출됐을 때 나타나는 전형적인 형태로, 메시지 수신자의 캡슐화는 무너지고 메시지 전송자가 메시지 수신자의 내부 구현에 강하게 결합된다.

디미터 법칙을 따르도록 코드를 개선하면 메시지 전송자는 더 이상 메시지 수신자의 내부 구조에 관해 묻지 않게 된다. 단지 자신이 원하는 것이 무엇인지를 명시하고 단순히 수행하도록 요청한다.

```java
screening.calculateFee(audienceCount);
```

### 4.5 디미터 법칙과 캡슐화

디미터 법칙은 캡슐화를 다른 관점에서 표현한 것이다. 디미터 법칙이 가치 있는 이유는 클래스를 캡슐화하기 위해 따라야 하는 **구체적인 지침**을 제공하기 때문이다. 캡슐화 원칙이 클래스 내부의 구현을 감춰야 한다는 사실을 강조한다면, 디미터 법칙은 협력하는 클래스의 캡슐화를 지키기 위해 **접근해야 하는 요소를 제한**한다. 디미터 법칙은 협력과 구현이라는 사뭇 달라 보이는 두 가지 문맥을 하나의 유기적인 개념으로 통합한다.

디미터 법칙을 따르면 **부끄럼 타는 코드**(*shy code*)를 작성할 수 있다. 부끄럼 타는 코드란 불필요한 어떤 것도 다른 객체에게 보여주지 않으며, 다른 객체의 구현에 의존하지 않는 코드를 말한다.

> **핵심 통찰**: 디미터 법칙은 객체가 자기 자신을 책임지는 자율적인 존재여야 한다는 사실을 강조한다. 정보를 처리하는 데 필요한 책임을 정보를 알고 있는 객체에게 할당하기 때문에 응집도가 높은 객체가 만들어진다.

---

## 5. 묻지 말고 시켜라 (Tell, Don't Ask)

### 5.1 원칙

`ReservationAgency`는 `Screening` 내부의 `Movie`에 접근하는 대신 `Screening`에게 직접 요금을 계산하도록 요청했다. 요금을 계산하는 데 필요한 정보를 잘 알고 있는 `Screening`에게 요금을 계산할 책임을 할당한 것이다. 디미터 법칙은 훌륭한 메시지는 **객체의 상태에 관해 묻지 말고 원하는 것을 시켜야 한다**는 사실을 강조한다. **묻지 말고 시켜라**(*Tell, Don't Ask*)는 이런 스타일의 메시지 작성을 장려하는 원칙을 가리키는 용어다.

메시지 전송자는 메시지 수신자의 상태를 기반으로 결정을 내린 후 메시지 수신자의 상태를 바꿔서는 안 된다. 구현하고 있는 로직은 메시지 수신자가 담당해야 할 책임일 것이다. 객체의 외부에서 해당 객체의 상태를 기반으로 결정을 내리는 것은 객체의 캡슐화를 위반한다.

> 절차적인 코드는 정보를 얻은 후에 결정한다. 객체지향 코드는 객체에게 그것을 하도록 시킨다[Sharp00].

### 5.2 효과

묻지 말고 시켜라 원칙을 따르면 밀접하게 연관된 정보와 행동을 함께 가지는 객체를 만들 수 있다. 객체지향의 기본은 함께 변경될 확률이 높은 정보와 행동을 하나의 단위로 통합하는 것이다. 묻지 말고 시켜라 원칙을 따르면 객체의 정보를 이용하는 행동을 객체의 외부가 아닌 내부에 위치시키기 때문에 자연스럽게 정보와 행동을 동일한 클래스 안에 두게 된다.

묻지 말고 시켜라 원칙에 따르도록 메시지를 결정하다 보면 자연스럽게 **정보 전문가**에게 책임을 할당하게 되고 높은 응집도를 가진 클래스를 얻을 확률이 높아진다.

### 5.3 인터페이스 개선 지침

묻지 말고 시켜라 원칙과 디미터 법칙은 훌륭한 인터페이스를 제공하기 위해 포함해야 하는 오퍼레이션에 대한 힌트를 제공한다:

- 내부의 상태를 **묻는** 오퍼레이션을 인터페이스에 포함시키고 있다면 더 나은 방법은 없는지 고민해 보라.
- 내부의 상태를 이용해 어떤 결정을 내리는 로직이 객체 **외부**에 존재하는가? 그렇다면 해당 객체가 책임져야 하는 어떤 행동이 객체 외부로 누수된 것이다.
- **상태를 묻는 오퍼레이션을 행동을 요청하는 오퍼레이션으로 대체**함으로써 인터페이스를 향상시켜라.

> 호출하는 객체는 이웃 객체가 수행하는 역할을 사용해 무엇을 원하는지를 서술해야 하고, 호출되는 객체가 어떻게 해야 하는지를 스스로 결정하게 해야 한다. 이것은 일반적으로 "묻지 말고 시켜라(Tell, Don't Ask)" 스타일, 또는 좀 더 공식적으로는 "디미터 법칙(Law of Demeter)"으로 알려져 있다[Freeman09].

---

## 6. 의도를 드러내는 인터페이스

### 6.1 메서드 명명의 두 가지 방법

켄트 벡(Kent Beck)은 《Smalltalk Best Practice Patterns》[Beck96]에서 메서드를 명명하는 두 가지 방법을 설명했다.

#### 방법 1: "어떻게" 수행하는지를 드러내는 이름

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class PeriodCondition {
    public boolean isSatisfiedByPeriod(Screening screening) { ... }
}

public class SequenceCondition {
    public boolean isSatisfiedBySequence(Screening screening) { ... }
}
```

</details>

```typescript
// TypeScript
class PeriodCondition {
    isSatisfiedByPeriod(screening: Screening): boolean { /* ... */ }
}

class SequenceCondition {
    isSatisfiedBySequence(screening: Screening): boolean { /* ... */ }
}
```

이런 스타일이 좋지 않은 이유는 두 가지다:

1. **메서드에 대해 제대로 커뮤니케이션하지 못한다**: 클라이언트의 관점에서 `isSatisfiedByPeriod`와 `isSatisfiedBySequence` 모두 할인 조건을 판단하는 동일한 작업을 수행한다. 하지만 메서드의 이름이 다르기 때문에 내부 구현을 정확하게 이해하지 못한다면 두 메서드가 동일한 작업을 수행한다는 사실을 알아채기 어렵다.

2. **메서드 수준에서 캡슐화를 위반한다**: 이 메서드들은 클라이언트로 하여금 협력하는 객체의 종류를 알도록 강요한다. `PeriodCondition`을 사용하는 코드를 `SequenceCondition`을 사용하도록 변경하려면 참조하는 객체뿐만 아니라 호출하는 메서드도 변경해야 한다.

#### 방법 2: "무엇을" 하는지를 드러내는 이름

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class PeriodCondition {
    public boolean isSatisfiedBy(Screening screening) { ... }
}

public class SequenceCondition {
    public boolean isSatisfiedBy(Screening screening) { ... }
}
```

</details>

```typescript
// TypeScript
class PeriodCondition {
    isSatisfiedBy(screening: Screening): boolean { /* ... */ }
}

class SequenceCondition {
    isSatisfiedBy(screening: Screening): boolean { /* ... */ }
}
```

변경된 코드는 `PeriodCondition`의 `isSatisfiedBy` 메서드와 `SequenceCondition`의 `isSatisfiedBy` 메서드가 동일한 목적을 가진다는 것을 메서드의 이름을 통해 명확하게 표현한다. 클라이언트의 입장에서 두 메서드는 동일한 메시지를 서로 다른 방법으로 처리하기 때문에 서로 대체 가능하다.

### 6.2 인터페이스로 묶기

자바 같은 정적 타이핑 언어에서 단순히 메서드의 이름이 같다고 해서 동일한 메시지를 처리할 수 있는 것은 아니다. 클라이언트가 두 메서드를 가진 객체를 동일한 타입으로 간주할 수 있도록 **동일한 타입 계층으로 묶어야** 한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public interface DiscountCondition {
    boolean isSatisfiedBy(Screening screening);
}

public class PeriodCondition implements DiscountCondition {
    public boolean isSatisfiedBy(Screening screening) { ... }
}

public class SequenceCondition implements DiscountCondition {
    public boolean isSatisfiedBy(Screening screening) { ... }
}
```

</details>

```typescript
// TypeScript
interface DiscountCondition {
    isSatisfiedBy(screening: Screening): boolean;
}

class PeriodCondition implements DiscountCondition {
    isSatisfiedBy(screening: Screening): boolean { /* ... */ }
}

class SequenceCondition implements DiscountCondition {
    isSatisfiedBy(screening: Screening): boolean { /* ... */ }
}
```

메서드가 어떻게 수행하느냐가 아니라 무엇을 하느냐에 초점을 맞추면 클라이언트의 관점에서 동일한 작업을 수행하는 메서드들을 하나의 타입 계층으로 묶을 수 있는 가능성이 커진다. 그 결과, 다양한 타입의 객체가 참여할 수 있는 유연한 협력을 얻게 되는 것이다.

### 6.3 의도를 드러내는 선택자와 의도를 드러내는 인터페이스

이처럼 어떻게 하느냐가 아니라 무엇을 하느냐에 따라 메서드의 이름을 짓는 패턴을 **의도를 드러내는 선택자**(*Intention Revealing Selector*)라고 부른다. 켄트 벡은 메서드에 의도를 드러낼 수 있는 이름을 붙이기 위해 다음과 같이 생각할 것을 조언한다.

> 매우 다른 두 번째 구현을 상상하라. 그러고는 해당 메서드에 동일한 이름을 붙인다고 상상해 보라. 그렇게 하면 아마도 그 순간 여러분이 할 수 있는 한 가장 추상적인 이름을 메서드에 붙일 것이다[Beck96].

에릭 에반스(Eric Evans)는 《도메인 주도 설계》[Evans03]에서 켄트 벡의 의도를 드러내는 선택자를 인터페이스 레벨로 확장한 **의도를 드러내는 인터페이스**(*Intention Revealing Interface*)를 제시했다. 의도를 드러내는 인터페이스를 한마디로 요약하면 **구현과 관련된 모든 정보를 캡슐화하고 객체의 퍼블릭 인터페이스에는 협력과 관련된 의도만을 표현해야 한다**는 것이다.

> 수행 방법에 관해서는 언급하지 말고 결과와 목적만을 포함하도록 클래스와 오퍼레이션의 이름을 부여하라. 이렇게 하면 클라이언트 개발자가 내부를 이해해야 할 필요성이 줄어든다. 방법이 아닌 의도를 표현하는 추상적인 인터페이스 뒤로 모든 까다로운 메커니즘을 캡슐화해야 한다[Evans03].

---

## 7. 함께 모으기: 티켓 판매 도메인 리팩터링

디미터 법칙, 묻지 말고 시켜라 스타일, 의도를 드러내는 인터페이스를 이해할 수 있는 좋은 방법 중 하나는 이런 원칙을 **위반하는** 코드의 모습을 살펴보는 것이다. 1장에서 살펴본 티켓 판매 도메인이 바로 그것이다.

### 7.1 디미터 법칙을 위반하는 코드

`Theater`의 `enter` 메서드는 디미터 법칙을 위반한 코드의 전형적인 모습을 잘 보여준다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Theater {
    private TicketSeller ticketSeller;

    public Theater(TicketSeller ticketSeller) {
        this.ticketSeller = ticketSeller;
    }

    public void enter(Audience audience) {
        if (audience.getBag().hasInvitation()) {
            Ticket ticket = ticketSeller.getTicketOffice().getTicket();
            audience.getBag().setTicket(ticket);
        } else {
            Ticket ticket = ticketSeller.getTicketOffice().getTicket();
            audience.getBag().minusAmount(ticket.getFee());
            ticketSeller.getTicketOffice().plusAmount(ticket.getFee());
            audience.getBag().setTicket(ticket);
        }
    }
}
```

</details>

```typescript
// TypeScript
class Theater {
    private ticketSeller: TicketSeller;

    constructor(ticketSeller: TicketSeller) {
        this.ticketSeller = ticketSeller;
    }

    enter(audience: Audience): void {
        if (audience.getBag().hasInvitation()) {
            const ticket = this.ticketSeller.getTicketOffice().getTicket();
            audience.getBag().setTicket(ticket);
        } else {
            const ticket = this.ticketSeller.getTicketOffice().getTicket();
            audience.getBag().minusAmount(ticket.getFee());
            this.ticketSeller.getTicketOffice().plusAmount(ticket.getFee());
            audience.getBag().setTicket(ticket);
        }
    }
}
```

디미터 법칙에 따르면 `Theater`가 인자로 전달된 `audience`와 인스턴스 변수인 `ticketSeller`에게 메시지를 전송하는 것은 문제가 없다. 문제는 `Theater`가 `audience`와 `ticketSeller` 내부에 포함된 객체에도 **직접 접근**한다는 것이다.

```java
audience.getBag().minusAmount(ticket.getFee());  // 기차 충돌!
```

이 코드에서 `Theater`는 `Audience`뿐만 아니라 `Audience` 내부에 포함된 `Bag`에게도 메시지를 전송한다. 결과적으로 `Theater`는 `Audience`의 퍼블릭 인터페이스뿐만 아니라 내부 구조에 대해서도 결합된다.

### 7.2 묻지 말고 시켜라 적용

`Theater`는 `TicketSeller`와 `Audience`의 내부 구조에 관해 묻지 말고 원하는 작업을 시켜야 한다.

**Step 1: Theater → TicketSeller에게 시키기**

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class TicketSeller {
    public void setTicket(Audience audience) {
        if (audience.getBag().hasInvitation()) {
            Ticket ticket = ticketOffice.getTicket();
            audience.getBag().setTicket(ticket);
        } else {
            Ticket ticket = ticketOffice.getTicket();
            audience.getBag().minusAmount(ticket.getFee());
            ticketOffice.plusAmount(ticket.getFee());
            audience.getBag().setTicket(ticket);
        }
    }
}

public class Theater {
    public void enter(Audience audience) {
        ticketSeller.setTicket(audience);
    }
}
```

</details>

```typescript
// TypeScript
class TicketSeller {
    setTicket(audience: Audience): void {
        if (audience.getBag().hasInvitation()) {
            const ticket = this.ticketOffice.getTicket();
            audience.getBag().setTicket(ticket);
        } else {
            const ticket = this.ticketOffice.getTicket();
            audience.getBag().minusAmount(ticket.getFee());
            this.ticketOffice.plusAmount(ticket.getFee());
            audience.getBag().setTicket(ticket);
        }
    }
}

class Theater {
    enter(audience: Audience): void {
        this.ticketSeller.setTicket(audience);
    }
}
```

**Step 2: TicketSeller → Audience에게 시키기**

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Audience {
    public Long setTicket(Ticket ticket) {
        if (bag.hasInvitation()) {
            bag.setTicket(ticket);
            return 0L;
        } else {
            bag.setTicket(ticket);
            bag.minusAmount(ticket.getFee());
            return ticket.getFee();
        }
    }
}

public class TicketSeller {
    public void setTicket(Audience audience) {
        ticketOffice.plusAmount(
            audience.setTicket(ticketOffice.getTicket()));
    }
}
```

</details>

```typescript
// TypeScript
class Audience {
    setTicket(ticket: Ticket): number {
        if (this.bag.hasInvitation()) {
            this.bag.setTicket(ticket);
            return 0;
        } else {
            this.bag.setTicket(ticket);
            this.bag.minusAmount(ticket.getFee());
            return ticket.getFee();
        }
    }
}

class TicketSeller {
    setTicket(audience: Audience): void {
        this.ticketOffice.plusAmount(
            audience.setTicket(this.ticketOffice.getTicket()));
    }
}
```

**Step 3: Audience → Bag에게 시키기**

`Audience`의 `setTicket` 메서드를 보면 `Bag`에게 원하는 일을 시키기 전에 `hasInvitation` 메서드를 이용해 초대권을 가지고 있는지를 묻는다. 이 역시 디미터 법칙을 위반한다. 구현을 `Bag`의 `setTicket` 메서드로 이동시키자.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Bag {
    public Long setTicket(Ticket ticket) {
        if (hasInvitation()) {
            this.ticket = ticket;
            return 0L;
        } else {
            this.ticket = ticket;
            minusAmount(ticket.getFee());
            return ticket.getFee();
        }
    }

    private boolean hasInvitation() {
        return invitation != null;
    }

    private void minusAmount(Long amount) {
        this.amount -= amount;
    }
}

public class Audience {
    public Long setTicket(Ticket ticket) {
        return bag.setTicket(ticket);
    }
}
```

</details>

```typescript
// TypeScript
class Bag {
    setTicket(ticket: Ticket): number {
        if (this.hasInvitation()) {
            this.ticket = ticket;
            return 0;
        } else {
            this.ticket = ticket;
            this.minusAmount(ticket.getFee());
            return ticket.getFee();
        }
    }

    private hasInvitation(): boolean {
        return this.invitation !== null;
    }

    private minusAmount(amount: number): void {
        this.amount -= amount;
    }
}

class Audience {
    setTicket(ticket: Ticket): number {
        return this.bag.setTicket(ticket);
    }
}
```

디미터 법칙과 묻지 말고 시켜라 원칙에 따라 코드를 리팩터링한 후에 `Audience` 스스로 자신의 상태를 제어하게 됐다는 점에 주목하라. `Audience`는 자신의 상태를 스스로 관리하고 결정하는 자율적인 존재가 된 것이다.

### 7.3 인터페이스에 의도를 드러내자

안타깝게도 현재의 인터페이스는 클라이언트의 의도를 명확하게 드러내지 못한다. `TicketSeller`의 `setTicket`, `Audience`의 `setTicket`, `Bag`의 `setTicket`은 모두 같은 이름을 가지고 있지만 미묘하게 다른 의도를 가진다. 클라이언트의 의도가 분명하게 드러나도록 객체의 퍼블릭 인터페이스를 개선해야 한다.

| 객체 | 클라이언트의 의도 | 변경 전 | 변경 후 |
|---|---|---|---|
| `TicketSeller` | Audience에게 티켓을 **판매**하는 것 | `setTicket` | `sellTo` |
| `Audience` | 티켓을 **구매**하는 것 | `setTicket` | `buy` |
| `Bag` | 티켓을 **보관**하는 것 | `setTicket` | `hold` |

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class TicketSeller {
    public void sellTo(Audience audience) { ... }
}

public class Audience {
    public Long buy(Ticket ticket) { ... }
}

public class Bag {
    public Long hold(Ticket ticket) { ... }
}
```

</details>

```typescript
// TypeScript
class TicketSeller {
    sellTo(audience: Audience): void { /* ... */ }
}

class Audience {
    buy(ticket: Ticket): number { /* ... */ }
}

class Bag {
    hold(ticket: Ticket): number { /* ... */ }
}
```

오퍼레이션의 이름은 협력이라는 문맥을 반영해야 한다. 오퍼레이션은 클라이언트가 객체에게 무엇을 원하는지를 표현해야 한다. 다시 말해 객체 자신이 아닌 **클라이언트의 의도를 표현하는 이름**을 가져야 한다. `sellTo`, `buy`, `hold`라는 이름은 클라이언트가 객체에게 무엇을 원하는지를 명확하게 표현한다. `setTicket`은 그렇지 않다.

> **핵심 통찰**: 디미터 법칙은 객체 간의 협력을 설계할 때 캡슐화를 위반하는 메시지가 인터페이스에 포함되지 않도록 제한한다. 묻지 말고 시켜라 원칙은 디미터 법칙을 준수하는 협력을 만들기 위한 스타일을 제시한다. 의도를 드러내는 인터페이스 원칙은 객체의 퍼블릭 인터페이스에 어떤 이름이 드러나야 하는지에 대한 지침을 제공함으로써 코드의 목적을 명확하게 커뮤니케이션할 수 있게 해준다.

---

## 8. 원칙의 함정

디미터 법칙과 묻지 말고 시켜라 스타일은 객체의 퍼블릭 인터페이스를 깔끔하고 유연하게 만들 수 있는 훌륭한 설계 원칙이다. 하지만 **절대적인 법칙은 아니다**. 소프트웨어 설계에 법칙이란 존재하지 않는다. 법칙에는 예외가 없지만 원칙에는 예외가 넘쳐난다.

설계가 트레이드오프의 산물이라는 사실을 잊지 말아야 한다. 설계를 적절하게 트레이드오프할 수 있는 능력이 숙련자와 초보자를 구분하는 가장 중요한 기준이라고 할 수 있다. 초보자는 원칙을 맹목적으로 추종한다. 심지어 적용하려는 원칙들이 서로 충돌하는 경우에도 원칙에 정당성을 부여하고 억지로 끼워 맞추려고 노력한다.

> 원칙이 현재 상황에 부적합하다고 판단된다면 과감하게 원칙을 무시하라. 원칙을 아는 것보다 더 중요한 것은 **언제 원칙이 유용하고 언제 유용하지 않은지를 판단할 수 있는 능력**을 기르는 것이다.

### 8.1 디미터 법칙은 하나의 도트(.)를 강제하는 규칙이 아니다

디미터 법칙은 "오직 하나의 도트만을 사용하라"라는 말로 요약되기도 한다. 따라서 대부분의 사람들은 다음과 같은 코드가 기차 충돌을 초래하기 때문에 디미터 법칙을 위반한다고 생각할 것이다.

```typescript
// TypeScript (Java의 IntStream에 대응하는 배열 메서드 체이닝)
[1, 15, 20, 3, 9]
    .filter(x => x > 10)
    .filter((v, i, a) => a.indexOf(v) === i)  // distinct
    .length;
```

하지만 이것은 디미터 법칙을 제대로 이해하지 못한 것이다. 위 코드에서 `filter` 메서드는 모두 동일한 타입(배열)의 인스턴스를 반환한다. 즉, 이들은 배열을 또 다른 배열로 변환한다. 따라서 이 코드는 디미터 법칙을 **위반하지 않는다**.

디미터 법칙은 결합도와 관련된 것이며, 이 결합도가 문제가 되는 것은 **객체의 내부 구조가 외부로 노출되는 경우**로 한정된다. 위 코드에서 배열의 내부 구조가 외부로 노출됐는가? 그렇지 않다. 단지 배열을 다른 배열로 변환할 뿐, 객체를 둘러싸고 있는 캡슐은 그대로 유지된다.

**하나 이상의 도트(.)를 사용하는 모든 케이스가 디미터 법칙 위반인 것은 아니다.** 기차 충돌처럼 보이는 코드라도 객체의 내부 구현에 대한 어떤 정보도 외부로 노출하지 않는다면 그것은 디미터 법칙을 준수한 것이다.

위기의 순간이 온다면 스스로에게 다음과 같은 질문을 하기 바란다: **"과연 여러 개의 도트를 사용한 코드가 객체의 내부 구조를 노출하고 있는가?"**

### 8.2 결합도와 응집도의 충돌

일반적으로 어떤 객체의 상태를 물어본 후 반환된 상태를 기반으로 결정을 내리고 그 결정에 따라 객체의 상태를 변경하는 코드는 묻지 말고 시켜라 스타일로 변경해야 한다. 위임 메서드를 통해 객체의 내부 구조를 감추는 것은 협력에 참여하는 객체들의 결합도를 낮출 수 있는 동시에 객체의 응집도를 높일 수 있는 가장 효과적인 방법이다.

안타깝게도 묻지 말고 시켜라와 디미터 법칙을 준수하는 것이 **항상** 긍정적인 결과로만 귀결되는 것은 아니다. 모든 상황에서 맹목적으로 위임 메서드를 추가하면 같은 퍼블릭 인터페이스 안에 어울리지 않는 오퍼레이션들이 공존하게 된다. 결과적으로 객체는 상관없는 책임들을 한꺼번에 떠안게 되기 때문에 **응집도가 낮아진다**.

영화 예매 시스템의 `PeriodCondition` 클래스를 살펴보자.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class PeriodCondition implements DiscountCondition {
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
    isSatisfiedBy(screening: Screening): boolean {
        return screening.getStartTime().getDay() === this.dayOfWeek &&
            this.startTime <= screening.getStartTime().toLocalTime() &&
            this.endTime >= screening.getStartTime().toLocalTime();
    }
}
```

이 코드는 얼핏 보기에는 `Screening`의 내부 상태를 가져와서 사용하기 때문에 캡슐화를 위반한 것으로 보일 수 있다. 따라서 할인 여부를 판단하는 로직을 `Screening`의 `isDiscountable` 메서드로 옮기면 묻지 말고 시켜라 스타일을 준수할 수 있다고 생각할 것이다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Screening {
    public boolean isDiscountable(DayOfWeek dayOfWeek, LocalTime startTime, LocalTime endTime) {
        return whenScreened.getDayOfWeek().equals(dayOfWeek) &&
            startTime.compareTo(whenScreened.toLocalTime()) <= 0 &&
            endTime.compareTo(whenScreened.toLocalTime()) >= 0;
    }
}

public class PeriodCondition implements DiscountCondition {
    public boolean isSatisfiedBy(Screening screening) {
        return screening.isDiscountable(dayOfWeek, startTime, endTime);
    }
}
```

</details>

```typescript
// TypeScript
class Screening {
    isDiscountable(dayOfWeek: number, startTime: LocalTime, endTime: LocalTime): boolean {
        return this.whenScreened.getDay() === dayOfWeek &&
            startTime <= this.whenScreened.toLocalTime() &&
            endTime >= this.whenScreened.toLocalTime();
    }
}

class PeriodCondition implements DiscountCondition {
    isSatisfiedBy(screening: Screening): boolean {
        return screening.isDiscountable(this.dayOfWeek, this.startTime, this.endTime);
    }
}
```

하지만 이렇게 하면 `Screening`이 기간에 따른 할인 조건을 판단하는 책임을 떠안게 된다. 이것이 `Screening`이 담당해야 하는 본질적인 책임인가? 그렇지 않다. `Screening`의 본질적인 책임은 **영화를 예매하는 것**이다. `Screening`이 직접 할인 조건을 판단하게 되면 객체의 응집도가 낮아진다. 반면 `PeriodCondition`의 입장에서는 할인 조건을 판단하는 책임이 본질적이다.

게다가 `Screening`은 `PeriodCondition`의 인스턴스 변수를 인자로 받기 때문에 `PeriodCondition`의 인스턴스 변수 목록이 변경될 경우에도 영향을 받게 된다. 이것은 `Screening`과 `PeriodCondition` 사이의 결합도를 높인다. 따라서 `Screening`의 캡슐화를 향상시키는 것보다 `Screening`의 응집도를 높이고 `Screening`과 `PeriodCondition` 사이의 결합도를 낮추는 것이 전체적인 관점에서 더 좋은 방법이다.

### 8.3 물어야 하는 경우도 있다

가끔씩은 묻는 것 외에는 다른 방법이 존재하지 않는 경우도 존재한다. 컬렉션에 포함된 객체들을 처리하는 유일한 방법은 객체에게 물어보는 것이다.

```typescript
// TypeScript
let total = 0;
for (const each of movies) {
    total += each.getFee();
}
```

물으려는 객체가 정말로 데이터인 경우도 있다. 로버트 마틴은 《클린 코드》에서 디미터 법칙의 위반 여부는 묻는 대상이 **객체**인지, **자료 구조**인지에 달려 있다고 설명한다. 객체는 내부 구조를 숨겨야 하므로 디미터 법칙을 따르는 것이 좋지만 자료 구조라면 당연히 내부를 노출해야 하므로 디미터 법칙을 적용할 필요가 없다.

> **핵심 통찰**: 객체에게 시키는 것이 항상 가능한 것은 아니다. 가끔씩은 물어야 한다. 소프트웨어 설계에 법칙이란 존재하지 않는다. 원칙을 맹신하지 마라. 원칙이 적절한 상황과 부적절한 상황을 판단할 수 있는 안목을 길러라. 설계는 트레이드오프의 산물이다. 소프트웨어 설계에 존재하는 몇 안 되는 법칙 중 하나는 **"경우에 따라 다르다"**라는 사실을 명심하라.

---

## 9. 명령-쿼리 분리 원칙 (Command-Query Separation)

### 9.1 루틴, 프로시저, 함수

어떤 절차를 묶어 호출 가능하도록 이름을 부여한 기능 모듈을 **루틴**(*routine*)이라고 부른다. 루틴은 다시 **프로시저**(*procedure*)와 **함수**(*function*)로 구분할 수 있다.

| 구분 | 프로시저 | 함수 |
|---|---|---|
| **부수 효과** | 발생시킬 수 있다 | 발생시킬 수 없다 |
| **반환 값** | 없다 | 있다 |
| **목적** | 내부의 상태를 변경 | 필요한 값을 계산해서 반환 |

### 9.2 명령과 쿼리

**명령**(*Command*)과 **쿼리**(*Query*)는 객체의 인터페이스 측면에서 프로시저와 함수를 부르는 또 다른 이름이다. 객체의 상태를 수정하는 오퍼레이션을 **명령**이라고 부르고, 객체와 관련된 정보를 반환하는 오퍼레이션을 **쿼리**라고 부른다. 따라서 개념적으로 명령은 프로시저와 동일하고 쿼리는 함수와 동일하다.

**명령-쿼리 분리 원칙의 요지**는 오퍼레이션은 부수 효과를 발생시키는 명령이거나 부수 효과를 발생시키지 않는 쿼리 중 하나여야 한다는 것이다. **어떤 오퍼레이션도 명령인 동시에 쿼리여서는 안 된다.** 따라서 명령과 쿼리를 분리하기 위해서는 다음의 두 가지 규칙을 준수해야 한다:

- **객체의 상태를 변경하는 명령은 반환 값을 가질 수 없다.**
- **객체의 정보를 반환하는 쿼리는 상태를 변경할 수 없다.**

명령-쿼리 분리 원칙을 한 문장으로 표현하면 **"질문이 답변을 수정해서는 안 된다"**는 것이다.

### 9.3 기계 메타포

버트란드 마이어(Bertrand Meyer)는 명령-쿼리 분리 원칙을 설명할 때 **기계 메타포**를 이용한다. 이 관점에서 객체는 **블랙박스**이며 객체의 인터페이스는 두 종류의 버튼으로 구성된다:

```
    ┌─────────────────────────────────────┐
    │           [디스플레이 패널]             │
    │    현재 상태를 메시지로 표시            │
    ├─────────────────────────────────────┤
    │                                     │
    │  ○ empty    □ insert                │
    │  ○ current  □ delete                │
    │  ○ first    □ merge                 │
    │  ○ last                             │
    │  ○ search                           │
    │                                     │
    │  ○ = 쿼리 (상태 반환, 변경 없음)      │
    │  □ = 명령 (상태 변경, 반환 없음)      │
    └─────────────────────────────────────┘
```

- **둥근 버튼(○) = 쿼리**: 기계의 현재 상태를 디스플레이에 출력하지만 상태는 변경하지 않는다. 명령 버튼을 누르지 않고 쿼리 버튼을 계속 누르면 매번 동일한 메시지가 출력된다.
- **네모 버튼(□) = 명령**: 기계의 상태를 변경하지만 변경된 상태에 관한 어떤 정보도 외부로 제공하지 않는다. 명령 버튼을 누른 후 쿼리 버튼을 누르면 이전과 다른 메시지가 출력될 수 있다.

마틴 파울러(Martin Fowler)는 명령-쿼리 분리 원칙에 따라 작성된 객체의 인터페이스를 **명령-쿼리 인터페이스**(*Command-Query Interface*)라고 부른다.

### 9.4 예제: 반복 일정의 버그

일정 관리 소프트웨어에서 두 가지 핵심 개념을 살펴보자.

- **이벤트**(*Event*): 특정 일자에 실제로 발생하는 사건 (예: "2019년 5월 8일 수요일 10시 30분부터 11시까지 회의")
- **반복 일정**(*RecurringSchedule*): 일주일 단위로 돌아오는 특정 시간 간격에 발생하는 사건 전체 (예: "매주 수요일 10시 30분부터 11시까지 회의")

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Event {
    private String subject;
    private LocalDateTime from;
    private Duration duration;

    public Event(String subject, LocalDateTime from, Duration duration) {
        this.subject = subject;
        this.from = from;
        this.duration = duration;
    }
}

public class RecurringSchedule {
    private String subject;
    private DayOfWeek dayOfWeek;
    private LocalTime from;
    private Duration duration;

    public RecurringSchedule(String subject, DayOfWeek dayOfWeek,
                             LocalTime from, Duration duration) {
        this.subject = subject;
        this.dayOfWeek = dayOfWeek;
        this.from = from;
        this.duration = duration;
    }

    public DayOfWeek getDayOfWeek() { return dayOfWeek; }
    public LocalTime getFrom() { return from; }
    public Duration getDuration() { return duration; }
}
```

</details>

```typescript
// TypeScript
class Event {
    private subject: string;
    private from: Date;
    private duration: number; // minutes

    constructor(subject: string, from: Date, duration: number) {
        this.subject = subject;
        this.from = from;
        this.duration = duration;
    }
}

class RecurringSchedule {
    private subject: string;
    private dayOfWeek: number;    // 0=Sunday, 1=Monday, ...
    private from: string;         // "HH:mm" 형태
    private duration: number;     // minutes

    constructor(subject: string, dayOfWeek: number, from: string, duration: number) {
        this.subject = subject;
        this.dayOfWeek = dayOfWeek;
        this.from = from;
        this.duration = duration;
    }

    getDayOfWeek(): number { return this.dayOfWeek; }
    getFrom(): string { return this.from; }
    getDuration(): number { return this.duration; }
}
```

`Event` 클래스는 현재 이벤트가 `RecurringSchedule`이 정의한 반복 일정 조건을 만족하는지를 검사하는 `isSatisfied` 메서드를 제공한다. 다음 코드의 첫 번째 호출은 예상대로 `false`를 반환한다 (5월 9일은 목요일이므로). 그런데 두 번째로 동일한 `isSatisfied`를 호출하면 놀랍게도 `true`를 반환한다.

```java
RecurringSchedule schedule = new RecurringSchedule("회의", DayOfWeek.WEDNESDAY,
    LocalTime.of(10, 30), Duration.ofMinutes(30));
Event meeting = new Event("회의", LocalDateTime.of(2019, 5, 9, 10, 30), Duration.ofMinutes(30));

assert meeting.isSatisfied(schedule) == false;  // 첫 번째 호출: false (OK)
assert meeting.isSatisfied(schedule) == true;   // 두 번째 호출: true (?!)
```

버그의 정체를 파악하기 위해 `isSatisfied` 메서드를 파헤쳐보자.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Event {
    public boolean isSatisfied(RecurringSchedule schedule) {
        if (from.getDayOfWeek() != schedule.getDayOfWeek() ||
            !from.toLocalTime().equals(schedule.getFrom()) ||
            !duration.equals(schedule.getDuration())) {
            reschedule(schedule);  // ← 여기가 문제!
            return false;
        }
        return true;
    }

    private void reschedule(RecurringSchedule schedule) {
        from = LocalDateTime.of(from.toLocalDate().plusDays(daysDistance(schedule)),
            schedule.getFrom());
        duration = schedule.getDuration();
    }

    private long daysDistance(RecurringSchedule schedule) {
        return schedule.getDayOfWeek().getValue() - from.getDayOfWeek().getValue();
    }
}
```

</details>

```typescript
// TypeScript
class Event {
    isSatisfied(schedule: RecurringSchedule): boolean {
        if (this.from.getDay() !== schedule.getDayOfWeek() ||
            this.getLocalTime() !== schedule.getFrom() ||
            this.duration !== schedule.getDuration()) {
            this.reschedule(schedule);  // ← 여기가 문제!
            return false;
        }
        return true;
    }

    private reschedule(schedule: RecurringSchedule): void {
        // Event의 상태를 RecurringSchedule의 조건에 맞게 변경
        const daysOffset = schedule.getDayOfWeek() - this.from.getDay();
        const newDate = new Date(this.from);
        newDate.setDate(newDate.getDate() + daysOffset);
        // from과 duration을 변경
        this.from = newDate;
        this.duration = schedule.getDuration();
    }
}
```

`isSatisfied` 메서드는 조건을 만족하지 못할 경우 `false`를 반환하기 전에 `reschedule` 메서드를 호출한다. `reschedule` 메서드는 `Event`의 일정을 인자로 전달된 `RecurringSchedule`의 조건에 맞게 **변경**한다. 버그를 찾기 어려웠던 이유는 `isSatisfied`가 **명령과 쿼리의 두 가지 역할을 동시에 수행**하고 있었기 때문이다.

| 역할 | 내용 |
|---|---|
| **쿼리** | Event가 RecurringSchedule의 조건에 부합하는지 판단 후 true/false 반환 |
| **명령** (숨겨진 부수 효과) | 조건에 부합하지 않을 경우 Event의 상태를 조건에 맞게 변경 |

대부분의 사람들은 `isSatisfied` 메서드가 부수 효과를 가질 것이라고 예상하지 못한다. 이름이 "is..."로 시작하기 때문에 순수한 질문(쿼리)으로 인식하기 때문이다.

### 9.5 명령과 쿼리 분리하기

가장 깔끔한 해결책은 명령과 쿼리를 명확하게 분리하는 것이다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Event {
    // 쿼리: 부수 효과 없이 판단만 수행
    public boolean isSatisfied(RecurringSchedule schedule) {
        if (from.getDayOfWeek() != schedule.getDayOfWeek() ||
            !from.toLocalTime().equals(schedule.getFrom()) ||
            !duration.equals(schedule.getDuration())) {
            return false;
        }
        return true;
    }

    // 명령: 상태를 변경하지만 값을 반환하지 않음
    public void reschedule(RecurringSchedule schedule) {
        from = LocalDateTime.of(from.toLocalDate().plusDays(daysDistance(schedule)),
            schedule.getFrom());
        duration = schedule.getDuration();
    }
}
```

</details>

```typescript
// TypeScript
class Event {
    // 쿼리: 부수 효과 없이 판단만 수행
    isSatisfied(schedule: RecurringSchedule): boolean {
        if (this.from.getDay() !== schedule.getDayOfWeek() ||
            this.getLocalTime() !== schedule.getFrom() ||
            this.duration !== schedule.getDuration()) {
            return false;
        }
        return true;
    }

    // 명령: 상태를 변경하지만 값을 반환하지 않음
    reschedule(schedule: RecurringSchedule): void {
        const daysOffset = schedule.getDayOfWeek() - this.from.getDay();
        const newDate = new Date(this.from);
        newDate.setDate(newDate.getDate() + daysOffset);
        this.from = newDate;
        this.duration = schedule.getDuration();
    }
}
```

수정 후의 `isSatisfied` 메서드는 부수 효과를 가지지 않기 때문에 순수한 쿼리가 됐다. `Event`의 인터페이스를 살펴보면, `isSatisfied` 메서드는 반환 값을 돌려주고(`boolean`) `reschedule` 메서드는 반환 값을 돌려주지 않는다(`void`). 인터페이스를 훑어보는 것만으로도 `isSatisfied`가 쿼리이고 `reschedule`이 명령이라는 사실을 한눈에 알 수 있다.

명령과 쿼리를 분리하면서 `reschedule` 메서드의 가시성이 `private`에서 `public`으로 변경됐다. 이제 클라이언트가 직접 명령 실행 여부를 결정할 수 있다:

```typescript
// TypeScript
if (!event.isSatisfied(schedule)) {
    event.reschedule(schedule);
}
```

수정 전보다 `Event`의 상태를 변경하기 위한 인터페이스가 더 복잡해진 것처럼 보이지만, 이 경우에는 명령과 쿼리를 분리함으로써 얻는 이점이 더 크다.

> **핵심 통찰**: 퍼블릭 인터페이스를 설계할 때 부수 효과를 가지는 대신 값을 반환하지 않는 **명령**과, 부수 효과를 가지지 않는 대신 값을 반환하는 **쿼리**를 분리하라. 그 결과, 코드는 예측 가능하고 이해하기 쉬우며 디버깅이 용이한 동시에 유지보수가 수월해질 것이다.

### 9.6 명령-쿼리 분리와 참조 투명성

명령과 쿼리를 엄격하게 분류하면 객체의 부수 효과를 제어하기가 수월해진다. 쿼리는 객체의 상태를 변경하지 않기 때문에 몇 번이고 반복적으로 호출하더라도 상관이 없다. 명령이 개입하지 않는 한 쿼리의 값은 변경되지 않기 때문에 쿼리의 결과를 예측하기 쉬워진다. 또한 쿼리들의 순서를 자유롭게 변경할 수도 있다.

명령과 쿼리를 분리함으로써 명령형 언어의 틀 안에서 **참조 투명성**(*referential transparency*)의 장점을 제한적이나마 누릴 수 있게 된다. 참조 투명성이란 **"어떤 표현식 e가 있을 때 e의 값으로 e가 나타나는 모든 위치를 교체하더라도 결과가 달라지지 않는 특성"**을 의미한다.

수학은 참조 투명성을 엄격하게 준수하는 가장 유명한 체계다. 어떤 함수 f(n)이 존재할 때 n의 값으로 1을 대입하면 그 결과가 3이라고 가정하자. 즉, f(1) = 3이므로:

```
f(1) + f(1) = 6     →    3 + 3 = 6
f(1) * 2    = 6     →    3 * 2 = 6
f(1) - 1    = 2     →    3 - 1 = 2
```

f(1)을 함수의 결과값인 3으로 바꾸더라도 식의 결과는 변하지 않는다. 이것이 바로 참조 투명성이다. f(1)의 값을 항상 3이라고 말할 수 있는 이유는 f(1)의 값이 변하지 않기 때문이다. 이처럼 어떤 값이 변하지 않는 성질을 **불변성**(*immutability*)이라고 부른다.

**불변성, 부수 효과, 참조 투명성의 관계:**

```
불변성 ──▶ 부수 효과 없음 ──▶ 참조 투명성 만족
```

- 수학에서의 함수는 어떤 값도 변경하지 않기 때문에 부수 효과가 존재하지 않는다.
- 부수 효과가 없는 불변의 세상에서는 모든 로직이 참조 투명성을 만족시킨다.

참조 투명성을 만족하는 식은 두 가지 장점을 제공한다:

1. 모든 함수를 이미 알고 있는 하나의 결과값으로 대체할 수 있기 때문에 **식을 쉽게 계산**할 수 있다.
2. 모든 곳에서 함수의 결과값이 동일하기 때문에 **식의 순서를 변경하더라도 각 식의 결과는 달라지지 않는다**.

객체지향 패러다임이 객체의 상태 변경이라는 부수 효과를 기반으로 하기 때문에 참조 투명성은 예외에 가깝다. 하지만 명령-쿼리 분리 원칙을 사용하면 이 균열을 조금이나마 줄일 수 있다. 명령-쿼리 분리 원칙은 부수 효과를 가지는 명령으로부터 부수 효과를 가지지 않는 쿼리를 명백하게 분리함으로써 **제한적이나마 참조 투명성의 혜택을 누릴 수 있게** 된다.

> 부수 효과를 기반으로 하는 프로그래밍 방식을 **명령형 프로그래밍**(*imperative programming*)이라고 부른다. 대부분의 객체지향 프로그래밍 언어들은 명령형 프로그래밍 언어로 분류된다. 최근 주목받고 있는 **함수형 프로그래밍**(*functional programming*)은 부수 효과가 존재하지 않는 수학적인 함수에 기반한다. 따라서 함수형 프로그래밍에서는 참조 투명성의 장점을 극대화할 수 있다.

---

## 10. 책임에 초점을 맞춰라

디미터 법칙을 준수하고 묻지 말고 시켜라 스타일을 따르면서도 의도를 드러내는 인터페이스를 설계하는 아주 쉬운 방법이 있다. **메시지를 먼저 선택하고 그 후에 메시지를 처리할 객체를 선택하는 것**이다.

메시지를 먼저 선택하는 방식이 각 원칙에 미치는 긍정적인 영향:

| 원칙 | 메시지를 먼저 선택하면 |
|---|---|
| **디미터 법칙** | 수신할 객체를 알지 못한 상태에서 메시지를 먼저 선택하기 때문에 객체의 내부 구조에 대해 고민할 필요가 없어진다. 의도적으로 디미터 법칙을 위반할 위험을 최소화할 수 있다. |
| **묻지 말고 시켜라** | 클라이언트의 관점에서 메시지를 선택하기 때문에 필요한 정보를 물을 필요 없이 원하는 것을 표현한 메시지를 전송하면 된다. |
| **의도를 드러내는 인터페이스** | 메시지를 전송하는 클라이언트의 관점에서 메시지의 이름을 정하기 때문에 당연히 그 이름에는 클라이언트가 무엇을 원하는지, 그 의도가 분명하게 드러날 수밖에 없다. |
| **명령-쿼리 분리** | 객체가 단순히 어떤 일을 해야 하는지뿐만 아니라 협력 속에서 객체의 상태를 예측하고 이해하기 쉽게 만들기 위한 방법에 관해 고민하게 된다. |

훌륭한 메시지를 얻기 위한 출발점은 **책임 주도 설계 원칙**을 따르는 것이다. 책임 주도 설계에서는 객체가 메시지를 선택하는 것이 아니라 **메시지가 객체를 선택**하기 때문에 협력에 적합한 메시지를 결정할 수 있는 확률이 높아진다. 우리에게 중요한 것은 협력에 적합한 객체가 아니라 **협력에 적합한 메시지**다.

---

## 설계 원칙

| 원칙 | 핵심 내용 | 효과 |
|---|---|---|
| **디미터 법칙** | 객체의 내부 구조에 강하게 결합되지 않도록 협력 경로를 제한하라 | 캡슐화 강화, 낮은 결합도 |
| **묻지 말고 시켜라** | 객체의 상태를 묻지 말고 원하는 행동을 시켜라 | 높은 응집도, 자율적인 객체 |
| **의도를 드러내는 인터페이스** | 어떻게가 아니라 무엇을 하는지를 표현하는 이름을 사용하라 | 명확한 커뮤니케이션, 유연한 설계 |
| **명령-쿼리 분리** | 명령과 쿼리를 분리하여 부수 효과를 제어하라 | 예측 가능한 코드, 디버깅 용이 |

---

## 요약

- 객체지향의 가장 중요한 재료는 클래스가 아니라 객체들이 주고받는 **메시지**다. 클래스 사이의 정적인 관계에서 메시지 사이의 동적인 흐름으로 초점을 전환해야 한다.
- **메시지, 오퍼레이션, 메서드, 시그니처**는 서로 다른 개념이다. 메시지는 전송자와 수신자 사이의 협력을, 오퍼레이션은 인터페이스의 추상화를, 메서드는 오퍼레이션의 구현을, 시그니처는 이름과 파라미터 목록의 명세를 나타낸다.
- **다형성**이란 동일한 오퍼레이션 호출에 대해 서로 다른 메서드들이 실행되는 것이다.
- **디미터 법칙**은 객체의 내부 구조에 강하게 결합되지 않도록 협력 경로를 제한하는 원칙이다. 기차 충돌(train wreck) 코드는 디미터 법칙 위반의 전형적인 징후다.
- **묻지 말고 시켜라** 원칙은 객체의 상태를 묻고 결정을 내리는 대신, 객체에게 원하는 행동을 직접 시키는 스타일이다. 정보와 행동을 함께 가지는 응집도 높은 객체를 만든다.
- **의도를 드러내는 인터페이스**는 메서드의 이름을 "어떻게" 수행하는지가 아니라 "무엇을" 하는지로 짓는 것이다. 이를 통해 다양한 구현을 하나의 타입 계층으로 묶을 수 있다.
- **명령-쿼리 분리 원칙**은 오퍼레이션을 부수 효과를 가지는 명령과 부수 효과를 가지지 않는 쿼리로 분리하는 것이다. 코드의 예측 가능성과 참조 투명성을 높인다.
- 원칙은 절대적인 법칙이 아니다. **설계는 트레이드오프의 산물**이며, 원칙이 적절한 상황과 부적절한 상황을 판단할 수 있는 안목을 길러야 한다.
- 훌륭한 인터페이스를 설계하는 출발점은 **메시지를 먼저 선택**하는 것이다. 책임 주도 설계에서는 메시지가 객체를 선택하기 때문에 협력에 적합한 메시지를 결정할 수 있는 확률이 높아진다.

---

## 다른 챕터와의 관계

- **Chapter 1 (객체, 설계)**: 이 장에서 디미터 법칙, 묻지 말고 시켜라, 의도를 드러내는 인터페이스를 적용하여 리팩터링하는 예제가 1장의 티켓 판매 도메인이다. 1장에서 직관적으로 개선했던 코드가 사실은 이 장에서 설명하는 원칙들을 따른 결과였음을 알 수 있다.
- **Chapter 3 (역할, 책임, 협력)**: 좋은 인터페이스의 조건인 "최소한의 인터페이스"와 "추상적인 인터페이스"는 3장에서 소개된 개념이다. 이 장에서는 이 조건을 만족시키기 위한 구체적인 원칙과 기법을 제공한다.
- **Chapter 4 (설계 품질과 트레이드오프)**: 4장의 절차적인 ReservationAgency 코드가 이 장에서 디미터 법칙 위반의 예시로 다시 등장한다. 4장에서 데이터 중심 설계가 변경에 취약한 이유가 이 장의 디미터 법칙으로 명확하게 설명된다.
- **Chapter 5 (책임 할당하기)**: 5장의 책임 주도 설계 방법이 이 장의 모든 원칙(디미터 법칙, 묻지 말고 시켜라, 의도를 드러내는 인터페이스, 명령-쿼리 분리)을 자연스럽게 따르게 만든다는 것을 이 장의 마지막 절에서 종합적으로 설명한다.
- **Chapter 7 (객체 분해)**: 이 장에서 살펴본 원칙들이 탄생하게 된 배경인 프로그래밍 패러다임의 역사적 변화를 7장에서 다룬다.
- **Appendix A (계약에 의한 설계)**: 이 장에서 소개한 원칙들이 실행 시점의 구체적인 제약이나 조건을 명확하게 표현하지 못하는 한계를 극복하기 위해 버트란드 마이어가 제안한 "계약에 의한 설계"를 부록 A에서 상세히 다룬다.
