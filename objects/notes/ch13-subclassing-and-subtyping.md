# Chapter 13: Subclassing and Subtyping (서브클래싱과 서브타이핑)

## 핵심 질문

상속의 올바른 용도는 코드 재사용인가, 타입 계층의 구현인가? 서브클래싱과 서브타이핑의 차이는 무엇이며, 리스코프 치환 원칙은 올바른 상속 관계를 어떻게 정의하는가? 클라이언트 관점에서 행동 호환성이란 무엇이며, 계약에 의한 설계는 서브타이핑 관계를 어떻게 보장하는가?

---

## 1. 타입

객체지향 프로그래밍에서 타입의 의미를 이해하려면 프로그래밍 언어 관점에서의 타입과 개념 관점에서의 타입을 함께 살펴볼 필요가 있다.

### 1.1 개념 관점의 타입

개념 관점에서 타입이란 우리가 인지하는 세상의 사물의 종류를 의미한다. 다시 말해 우리가 인식하는 객체들에 적용하는 개념이나 아이디어를 가리켜 타입이라고 부른다. 타입은 사물을 분류하기 위한 틀로 사용된다. 예를 들어, 자바, 루비, 자바스크립트, C를 프로그래밍 언어라고 부를 때, 이것들을 프로그래밍 언어라는 타입으로 분류하고 있는 것이다.

어떤 대상이 타입으로 분류될 때 그 대상을 타입의 **인스턴스**(*Instance - 특정 타입에 속하는 개별 객체*)라고 부른다. 자바, 루비, 자바스크립트, C는 프로그래밍 언어의 인스턴스다. 일반적으로 타입의 인스턴스를 객체라고 부른다.

타입은 세 가지 요소로 구성된다:

| 요소 | 의미 | 예시 |
|---|---|---|
| **심볼**(*Symbol*) | 타입에 붙인 이름 | '프로그래밍 언어' |
| **내연**(*Intension*) | 타입에 속하는 객체들이 가지는 공통적인 속성이나 행동 | '컴퓨터에게 특정한 작업을 지시하기 위한 어휘와 문법적 규칙의 집합' |
| **외연**(*Extension*) | 타입에 속하는 객체들의 집합 | 자바, 루비, 자바스크립트, C 등 |

### 1.2 프로그래밍 언어 관점의 타입

프로그래밍 언어 관점에서 타입은 연속적인 비트에 의미와 제약을 부여하기 위해 사용된다. 하드웨어는 데이터를 0과 1로 구성된 일련의 비트 조합으로 취급하지만, 비트 자체에는 타입이라는 개념이 존재하지 않는다. 비트에 담긴 데이터를 문자열로 다룰지, 정수로 다룰지는 전적으로 데이터를 사용하는 애플리케이션에 의해 결정된다.

프로그래밍 언어에서 타입은 두 가지 목적을 위해 사용된다:

1. **타입에 수행될 수 있는 유효한 오퍼레이션의 집합을 정의한다**: 자바에서 `+` 연산자는 원시형 숫자 타입이나 문자열 타입의 객체에는 사용할 수 있지만 다른 클래스의 인스턴스에 대해서는 사용할 수 없다. 모든 객체지향 언어들은 객체의 타입에 따라 적용 가능한 연산자의 종류를 제한함으로써 프로그래머의 실수를 막아준다.

2. **타입에 수행되는 오퍼레이션에 대해 미리 약속된 문맥을 제공한다**: 자바에서 `a + b`라는 연산이 있을 때 `a`와 `b`의 타입이 `int`라면 두 수를 더할 것이다. 하지만 `a`와 `b`의 타입이 `String`이라면 두 문자열을 하나의 문자열로 합칠 것이다. 따라서 `a`와 `b`에 부여된 타입이 `+` 연산자의 문맥을 정의한다.

정리하면 타입은 적용 가능한 오퍼레이션의 종류와 의미를 정의함으로써 코드의 의미를 명확하게 전달하고 개발자의 실수를 방지하기 위해 사용된다.

### 1.3 객체지향 패러다임 관점의 타입

지금까지의 내용을 바탕으로 타입을 다음과 같은 두 가지 관점에서 정의할 수 있다:

- **개념 관점**: 타입이란 공통의 특징을 공유하는 대상들의 분류다.
- **프로그래밍 언어 관점**: 타입이란 동일한 오퍼레이션을 적용할 수 있는 인스턴스들의 집합이다.

이 두 정의를 객체지향 패러다임의 관점에서 조합해 보자. 프로그래밍 언어의 관점에서 타입은 호출 가능한 오퍼레이션의 집합을 정의한다. 객체지향 프로그래밍에서 오퍼레이션은 객체가 수신할 수 있는 메시지를 의미한다. 따라서 **객체의 타입이란 객체가 수신할 수 있는 메시지의 종류를 정의하는 것**이다.

객체가 수신할 수 있는 메시지의 집합을 가리키는 용어가 바로 **퍼블릭 인터페이스**다. 객체지향 프로그래밍에서 타입을 정의하는 것은 객체의 퍼블릭 인터페이스를 정의하는 것과 동일하다.

> **핵심 통찰**: 객체의 퍼블릭 인터페이스가 객체의 타입을 결정한다. 따라서 동일한 퍼블릭 인터페이스를 제공하는 객체들은 동일한 타입으로 분류된다. 어떤 객체들이 동일한 상태를 가지고 있더라도 퍼블릭 인터페이스가 다르다면 서로 다른 타입으로 분류된다. 반대로 내부 상태는 다르지만 동일한 퍼블릭 인터페이스를 공유한다면 동일한 타입으로 분류된다.

객체를 바라볼 때는 항상 객체가 외부에 제공하는 행동에 초점을 맞춰야 한다. 객체의 타입을 결정하는 것은 내부의 속성이 아니라 객체가 외부에 제공하는 행동이다.

---

## 2. 타입 계층

### 2.1 타입 사이의 포함 관계

수학에서 집합은 다른 집합을 포함할 수 있다. 타입 역시 객체들의 집합이기 때문에 다른 타입을 포함하는 것이 가능하다. 타입 안에 포함된 객체들을 좀 더 상세한 기준으로 묶어 새로운 타입을 정의하면 이 새로운 타입은 자연스럽게 기존 타입의 부분집합이 된다.

```
┌────────────────── 프로그래밍 언어 ──────────────────┐
│                                                      │
│  ┌──── 객체지향 언어 ────┐                           │
│  │  ┌─ 클래스 기반 ─┐    │                           │
│  │  │  Java         │    │   ┌─── 절차적 언어 ───┐   │
│  │  │  C++          │    │   │  C                │   │
│  │  │  Ruby         │    │   │  Pascal           │   │
│  │  └───────────────┘    │   └───────────────────┘   │
│  │  ┌─ 프로토타입 기반 ─┐│                           │
│  │  │  JavaScript      ││                           │
│  │  │  Self            ││                           │
│  │  └──────────────────┘│                           │
│  └───────────────────────┘                           │
└──────────────────────────────────────────────────────┘
```

타입이 다른 타입에 포함될 수 있기 때문에 동일한 인스턴스가 하나 이상의 타입으로 분류되는 것도 가능하다. 자바는 '프로그래밍 언어'인 동시에 '객체지향 언어'에 속하며 더 세부적으로 '클래스 기반 언어' 타입에 속한다.

다른 타입을 포함하는 타입과 포함되는 타입 사이에는 다음과 같은 관계가 성립한다:

| 관점 | 포함하는 타입 | 포함되는 타입 |
|---|---|---|
| **외연** (집합) | 더 크다 (더 많은 인스턴스) | 더 작다 (더 적은 인스턴스) |
| **내연** (정의) | 더 일반적이다 | 더 특수하다 |

이것은 포함 관계로 연결된 타입 사이에 개념적으로 **일반화**(*Generalization - 더 보편적이고 추상적으로 만드는 과정*)와 **특수화**(*Specialization - 더 구체적이고 문맥 종속적으로 만드는 과정*) 관계가 존재한다는 것을 의미한다.

### 2.2 슈퍼타입과 서브타입

타입 계층을 구성하는 두 타입 간의 관계에서 더 일반적인 타입을 **슈퍼타입**(*Supertype*)이라고 부르고 더 특수한 타입을 **서브타입**(*Subtype*)이라고 부른다.

```
       프로그래밍 언어        ← 슈퍼타입
       /            \
  객체지향 언어    절차적 언어  ← 서브타입
   /        \
클래스 기반  프로토타입 기반
언어         언어              ← 더 특수한 서브타입
```

슈퍼타입과 서브타입이라는 용어는 슈퍼셋(*Superset*)과 서브셋(*Subset*)으로부터 유래한 것이다.

| 타입 | 내연 관점 | 외연 관점 |
|---|---|---|
| **슈퍼타입** | 타입 정의가 상대적으로 일반적이다 | 집합이 다른 집합의 모든 멤버를 포함한다 |
| **서브타입** | 타입 정의가 상대적으로 구체적이다 | 집합에 포함되는 인스턴스들이 더 큰 집합에 포함된다 |

### 2.3 객체지향 프로그래밍과 타입 계층

객체의 타입을 결정하는 것은 퍼블릭 인터페이스다. 따라서 퍼블릭 인터페이스의 관점에서 슈퍼타입과 서브타입을 다음과 같이 정의할 수 있다:

- **슈퍼타입**: 서브타입이 정의한 퍼블릭 인터페이스를 일반화시켜 상대적으로 범용적이고 넓은 의미로 정의한 것이다.
- **서브타입**: 슈퍼타입이 정의한 퍼블릭 인터페이스를 특수화시켜 상대적으로 구체적이고 좁은 의미로 정의한 것이다.

> **핵심 통찰**: 서브타입의 인스턴스는 슈퍼타입의 인스턴스로 간주될 수 있다. 이 사실이 이번 장의 핵심이다. 그리고 상속과 다형성의 관계를 이해하기 위한 출발점이다.

---

## 3. 서브클래싱과 서브타이핑

객체지향 프로그래밍 언어에서 타입을 구현하는 일반적인 방법은 클래스를 이용하는 것이다. 타입 계층을 구현하는 일반적인 방법은 상속을 이용하는 것이다. 상속을 이용해 타입 계층을 구현한다는 것은 부모 클래스가 슈퍼타입의 역할을, 자식 클래스가 서브타입의 역할을 수행하도록 클래스 사이의 관계를 정의한다는 것을 의미한다.

### 3.1 언제 상속을 사용해야 하는가?

마틴 오더스키(Martin Odersky)는 다음과 같은 질문을 해 보고 두 질문에 모두 '예'라고 답할 수 있는 경우에만 상속을 사용하라고 조언한다:

1. **상속 관계가 is-a 관계를 모델링하는가?**
   일반적으로 "자식 클래스는 부모 클래스다"라고 말해도 이상하지 않다면 상속을 사용할 후보로 간주할 수 있다.

2. **클라이언트 입장에서 부모 클래스의 타입으로 자식 클래스를 사용해도 무방한가?**
   상속 계층을 사용하는 클라이언트의 입장에서 부모 클래스와 자식 클래스의 차이점을 몰라야 한다. 이를 자식 클래스와 부모 클래스 사이의 **행동 호환성**이라고 부른다.

설계 관점에서 상속을 적용할지 여부를 결정하기 위해 첫 번째 질문보다는 **두 번째 질문에 초점을 맞추는 것이 중요하다**. 클라이언트의 관점에서 두 클래스에 대해 기대하는 행동이 다르다면, 비록 그것이 어휘적으로 is-a 관계로 표현할 수 있다 하더라도 상속을 사용해서는 안 된다.

### 3.2 is-a 관계의 함정

스콧 마이어스(Scott Meyers)는 <<이펙티브 C++>>에서 새와 펭귄의 예를 들어 is-a 관계가 직관을 쉽게 배신할 수 있다는 사실을 보여준다.

먼저 익숙한 두 가지 사실에서 이야기를 시작해 보자:

- 펭귄은 새다
- 새는 날 수 있다

두 가지 사실을 조합하면 아래와 유사한 코드를 얻게 된다:

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Bird {
    public void fly() { /* ... */ }
}

public class Penguin extends Bird {
    // ...
}
```

</details>

```typescript
// TypeScript
class Bird {
    fly(): void { /* ... */ }
}

class Penguin extends Bird {
    // ...
}
```

안타깝게도 이 코드의 반은 맞고 반은 틀리다. 펭귄은 분명 새지만 날 수 없는 새다. 하지만 코드는 분명히 "펭귄은 새고, 따라서 날 수 있다"라고 주장하고 있다.

이 예는 **어휘적인 정의가 아니라 기대되는 행동에 따라 타입 계층을 구성해야 한다**는 사실을 잘 보여준다. 어휘적으로 펭귄은 새지만, 새의 정의에 '날 수 있다'는 행동이 포함된다면 펭귄은 새의 서브타입이 될 수 없다.

### 3.3 행동 호환성

펭귄이 새가 아니라는 사실을 받아들이기 위한 출발점은 **타입이 행동과 관련이 있다**는 사실에 주목하는 것이다. 타입의 이름 사이에 개념적으로 어떤 연관성이 있다고 하더라도 행동에 연관성이 없다면 is-a 관계를 사용하지 말아야 한다.

행동의 호환 여부를 판단하는 기준은 **클라이언트의 관점**이다:

- 클라이언트가 두 타입이 동일하게 행동할 것이라고 기대한다면 두 타입을 타입 계층으로 묶을 수 있다.
- 클라이언트가 두 타입이 동일하게 행동하지 않을 것이라고 기대한다면 두 타입을 타입 계층으로 묶어서는 안 된다.

다음과 같이 클라이언트가 날 수 있는 새만을 원한다고 가정해 보자:

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public void flyBird(Bird bird) {
    // 인자로 전달된 모든 bird는 날 수 있어야 한다
    bird.fly();
}
```

</details>

```typescript
// TypeScript
function flyBird(bird: Bird): void {
    // 인자로 전달된 모든 bird는 날 수 있어야 한다
    bird.fly();
}
```

현재 `Penguin`은 `Bird`의 자식 클래스이기 때문에 컴파일러는 업캐스팅을 허용한다. 따라서 `flyBird` 메서드의 인자로 `Penguin`의 인스턴스가 전달되는 것을 막을 수 있는 방법이 없다. 하지만 `Penguin`은 날 수 없고, 클라이언트는 모든 bird가 날 수 있기를 기대하기 때문에 `flyBird` 메서드로 전달돼서는 안 된다.

**상속 관계를 유지하면서 문제를 해결하기 위한 세 가지 시도와 그 한계:**

| 시도 | 방법 | 문제점 |
|---|---|---|
| **1. 빈 구현** | `Penguin`의 `fly`를 오버라이딩해서 아무 일도 하지 않게 한다 | 모든 bird가 날 수 있다는 클라이언트의 기대를 만족시키지 못한다 |
| **2. 예외 던지기** | `Penguin`의 `fly`에서 `UnsupportedOperationException`을 던진다 | 클라이언트가 예외를 기대하지 않으므로 행동이 호환되지 않는다 |
| **3. instanceof 체크** | `flyBird`에서 `bird instanceof Penguin`을 확인한다 | 새로운 날 수 없는 새가 추가될 때마다 코드를 수정해야 하므로 개방-폐쇄 원칙을 위반한다 |

### 3.4 클라이언트의 기대에 따라 계층 분리하기

행동 호환성을 만족시키지 않는 상속 계층을 그대로 유지한 채 클라이언트의 기대를 충족시킬 수 있는 방법을 찾기란 쉽지 않다. 문제를 해결할 수 있는 방법은 클라이언트의 기대에 맞게 상속 계층을 분리하는 것뿐이다.

**방법 1: 상속 계층 분리**

날 수 있는 새와 날 수 없는 새를 명확하게 구분할 수 있게 상속 계층을 분리하면 서로 다른 요구사항을 가진 클라이언트를 만족시킬 수 있다:

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Bird {
    // ...
}

public class FlyingBird extends Bird {
    public void fly() { /* ... */ }
}

public class Penguin extends Bird {
    // ...
}

public void flyBird(FlyingBird bird) {
    bird.fly();
}
```

</details>

```typescript
// TypeScript
class Bird {
    // ...
}

class FlyingBird extends Bird {
    fly(): void { /* ... */ }
}

class Penguin extends Bird {
    // ...
}

function flyBird(bird: FlyingBird): void {
    bird.fly();
}
```

```
              Bird
             /    \
      FlyingBird   Penguin
        fly()

  ┌─────────────────────┐     ┌──────────────────┐
  │ 날 수 있는 새와     │     │ 날지 못하는 새와  │
  │ 협력하는 클라이언트  │────▶│ 협력하는          │
  │ → FlyingBird 타입    │     │ 클라이언트        │
  └─────────────────────┘     │ → Bird 타입       │
                              └──────────────────┘
```

이제 `FlyingBird` 타입의 인스턴스만이 `fly` 메시지를 수신할 수 있다. 날 수 없는 `Bird`의 서브타입인 `Penguin`의 인스턴스에게 `fly` 메시지를 전송할 수 있는 방법은 없다.

**방법 2: 인터페이스 분리**

이 문제를 해결하는 또 다른 방법은 클라이언트에 따라 인터페이스를 분리하는 것이다. `fly` 오퍼레이션을 가진 `Flyer` 인터페이스와 `walk` 오퍼레이션을 가진 `Walker` 인터페이스로 분리하면 `Bird`와 `Penguin`은 자신이 수행할 수 있는 인터페이스만 구현할 수 있다:

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public interface Flyer {
    void fly();
}

public interface Walker {
    void walk();
}

public class Bird implements Flyer, Walker {
    public void fly() { /* ... */ }
    public void walk() { /* ... */ }
}

public class Penguin implements Walker {
    public void walk() { /* ... */ }
}
```

</details>

```typescript
// TypeScript
interface Flyer {
    fly(): void;
}

interface Walker {
    walk(): void;
}

class Bird implements Flyer, Walker {
    fly(): void { /* ... */ }
    walk(): void { /* ... */ }
}

class Penguin implements Walker {
    walk(): void { /* ... */ }
}
```

```
  Client1 ───▶ <<interface>>    <<interface>> ◀─── Client2
                  Flyer             Walker
                  fly()             walk()
                    △                 △
                    │                 │
                  Bird            Penguin
```

인터페이스를 클라이언트의 기대에 따라 분리함으로써 변경에 의해 영향을 제어하는 설계 원칙을 **인터페이스 분리 원칙**(*Interface Segregation Principle, ISP*)이라고 부른다.

만약 `Penguin`이 `Bird`의 코드를 재사용해야 한다면 어떻게 해야 할까? `Penguin`이 `Bird`를 상속받으면 퍼블릭 인터페이스에 `fly` 오퍼레이션이 추가되기 때문에 이 방법을 사용할 수는 없다. 더 좋은 방법은 **합성**을 사용하는 것이다.

```
  Client1 ───▶ <<interface>>    <<interface>> ◀─── Client2
                  Flyer             Walker
                  fly()             walk()
                    △                 △
                    │                 │
                  Bird ◁──────── Penguin
                        (합성)
```

> **핵심 통찰**: 설계가 꼭 현실 세계를 반영할 필요는 없다. 중요한 것은 설계가 반영할 도메인의 요구사항이고 그 안에서 클라이언트가 객체에게 요구하는 행동이다. 현재의 요구사항이 날 수 있는 행동에 관심이 없다면 상속 계층에 `FlyingBird`를 추가하는 것은 설계를 불필요하게 복잡하게 만든다. 현실을 정확하게 묘사하는 것이 아니라 요구사항을 실용적으로 수용하는 것을 목표로 삼아야 한다.

### 3.5 서브클래싱과 서브타이핑의 정의

상속은 두 가지 목적으로 사용된다. 사람들은 이 두 가지 목적에 특별한 이름을 붙였다:

| 구분 | 서브클래싱 | 서브타이핑 |
|---|---|---|
| **목적** | 코드 재사용 | 타입 계층 구성 |
| **행동 호환성** | 자식과 부모의 행동이 호환되지 않는다 | 자식과 부모의 행동이 호환된다 |
| **대체 가능성** | 자식 인스턴스가 부모를 대체할 수 없다 | 자식 인스턴스가 부모를 대체할 수 있다 |
| **다른 이름** | 구현 상속, 클래스 상속 | 인터페이스 상속 |

> 클래스 상속은 객체의 구현을 정의할 때 이미 정의된 객체의 구현을 바탕으로 한다. 즉, 코드 공유의 방법이다. 이에 비해 인터페이스 상속(서브타이핑)은 객체가 다른 곳에서 사용될 수 있음을 의미한다. ... 인터페이스 상속 관계를 갖는 경우 프로그램에는 슈퍼타입으로 정의하지만 런타임에 서브타입의 객체로 대체할 수 있다. - GoF

서브클래싱과 서브타이핑을 나누는 기준은 상속을 사용하는 목적이다. 코드를 재사용할 목적으로 상속을 사용했다면 서브클래싱이다. 자식 클래스의 인스턴스를 부모 클래스의 인스턴스 대신 사용할 목적으로 상속을 사용했다면 서브타이핑이다.

서브타이핑 관계가 유지되기 위해서는 서브타입이 슈퍼타입이 하는 모든 행동을 동일하게 할 수 있어야 한다. 즉, 어떤 타입이 다른 타입의 서브타입이 되기 위해서는 **행동 호환성**(*Behavioral Substitution*)을 만족시켜야 한다. 행동 호환성을 만족하는 상속 관계는 부모 클래스를 새로운 자식 클래스로 대체하더라도 시스템이 문제없이 동작할 것이라는 것을 보장해야 한다. 다시 말해서 자식 클래스와 부모 클래스 사이의 행동 호환성은 부모 클래스에 대한 자식 클래스의 **대체 가능성**(*Substitutability*)을 포함한다.

---

## 4. 리스코프 치환 원칙

1988년 바바라 리스코프(Barbara Liskov)는 올바른 상속 관계의 특징을 정의하기 위해 **리스코프 치환 원칙**(*Liskov Substitution Principle, LSP*)을 발표했다.

> 여기서 요구되는 것은 다음의 치환 속성과 같은 것이다. S형의 각 객체 o1에 대해 T형의 객체 o2가 하나 있고, T에 의해 정의된 모든 프로그램 P에서 T가 S로 치환될 때, P의 동작이 변하지 않으면 S는 T의 서브타입이다. - Barbara Liskov

리스코프 치환 원칙을 한 마디로 정리하면 **"서브타입은 그것의 기반 타입에 대해 대체 가능해야 한다"**는 것으로, 클라이언트가 "차이점을 인식하지 못한 채 기반 클래스의 인터페이스를 통해 서브클래스를 사용할 수 있어야 한다"는 것이다.

### 4.1 Stack과 Vector: LSP 위반 사례

10장에서 살펴본 `Stack`과 `Vector`는 리스코프 치환 원칙을 위반하는 전형적인 예다. 클라이언트가 부모 클래스인 `Vector`에 대해 기대하는 행동을 `Stack`에 대해서는 기대할 수 없기 때문이다.

`Vector`를 사용하는 클라이언트는 임의의 위치에 요소를 추가하거나 임의의 위치에 있는 요소를 추출할 것이라고 예상한다. 그러나 `Stack`의 클라이언트는 `Stack`이 임의의 위치에서의 조회나 추가를 금지할 것이라고 예상한다. `Stack`과 `Vector`가 서로 다른 클라이언트와 협력해야 한다는 것을 의미한다.

```
  Vector의 클라이언트               Stack의 클라이언트
  - get(index), add(index, e)      - push(e), pop()
  - 임의 위치 접근 기대              - LIFO 접근만 기대

  Vector의 퍼블릭 인터페이스 ⊃ Stack이 허용해야 할 인터페이스
  → 행동이 호환되지 않는다 → 서브클래싱 관계 (서브타이핑 X)
```

### 4.2 Rectangle과 Square: LSP 위반의 고전적 사례

대부분의 사람들은 "정사각형은 직사각형이다(Square is-a Rectangle)"라는 이야기를 당연하게 생각한다. 하지만 정사각형은 직사각형이 아닐 수 있다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Rectangle {
    private int x, y, width, height;

    public Rectangle(int x, int y, int width, int height) {
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
    }

    public int getWidth() { return width; }
    public void setWidth(int width) { this.width = width; }
    public int getHeight() { return height; }
    public void setHeight(int height) { this.height = height; }
    public int getArea() { return width * height; }
}

public class Square extends Rectangle {
    public Square(int x, int y, int size) {
        super(x, y, size, size);
    }

    @Override
    public void setWidth(int width) {
        super.setWidth(width);
        super.setHeight(width);
    }

    @Override
    public void setHeight(int height) {
        super.setWidth(height);
        super.setHeight(height);
    }
}
```

</details>

```typescript
// TypeScript
class Rectangle {
    constructor(
        private x: number,
        private y: number,
        private width: number,
        private height: number
    ) {}

    getWidth(): number { return this.width; }
    setWidth(width: number): void { this.width = width; }
    getHeight(): number { return this.height; }
    setHeight(height: number): void { this.height = height; }
    getArea(): number { return this.width * this.height; }
}

class Square extends Rectangle {
    constructor(x: number, y: number, size: number) {
        super(x, y, size, size);
    }

    override setWidth(width: number): void {
        super.setWidth(width);
        super.setHeight(width);
    }

    override setHeight(height: number): void {
        super.setWidth(height);
        super.setHeight(height);
    }
}
```

정사각형은 너비와 높이가 동일해야 한다. 따라서 `Square` 클래스는 `setWidth`와 `setHeight`를 오버라이딩해서 너비와 높이가 항상 같도록 보장한다.

문제는 `Rectangle`과 협력하는 클라이언트에서 발생한다:

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public void resize(Rectangle rectangle, int width, int height) {
    rectangle.setWidth(width);
    rectangle.setHeight(height);
    assert rectangle.getWidth() == width && rectangle.getHeight() == height;
}
```

</details>

```typescript
// TypeScript
function resize(rectangle: Rectangle, width: number, height: number): void {
    rectangle.setWidth(width);
    rectangle.setHeight(height);
    console.assert(
        rectangle.getWidth() === width && rectangle.getHeight() === height
    );
}
```

`resize` 메서드의 인자로 `Rectangle` 대신 `Square`를 전달하면 문제가 발생한다:

```typescript
const square = new Square(10, 10, 10);
resize(square, 50, 100);
// Square의 setHeight(100)이 width도 100으로 변경
// → getWidth() === 50 단언이 실패!
```

`Square`의 `setWidth`와 `setHeight`는 항상 너비와 높이를 같게 설정한다. 위 코드에 따르면 `Square`의 너비와 높이는 항상 더 나중에 설정된 `height`의 값으로 설정된다. 따라서 `width`와 `height` 값을 다르게 설정할 경우 메서드 실행이 실패한다.

직사각형은 너비와 높이가 다를 수 있다고 가정하지만, 정사각형은 너비와 높이가 항상 동일하다고 가정한다. `resize` 메서드의 구현은 `Rectangle`이 세운 가정에 기반하기 때문에 직사각형의 너비와 높이를 독립적으로 변경할 수 있다고 가정한다. 하지만 `Rectangle`의 자리에 `Square`를 전달할 경우 이 가정은 무너진다.

> **핵심 통찰**: `resize` 메서드의 관점에서 `Rectangle` 대신 `Square`를 사용할 수 없기 때문에 `Square`는 `Rectangle`이 아니다. `Square`는 `Rectangle`의 구현을 재사용하고 있을 뿐이다. 두 클래스는 리스코프 치환 원칙을 위반하기 때문에 서브타이핑 관계가 아니라 서브클래싱 관계다.

### 4.3 클라이언트와 대체 가능성

리스코프 치환 원칙은 **"클라이언트와 격리한 채로 본 모델은 의미 있게 검증하는 것이 불가능하다"**는 아주 중요한 결론을 이끈다. 어떤 모델의 유효성은 클라이언트의 관점에서만 검증 가능하다.

다른 정보 없이 `Square`가 `Rectangle`을 상속한 클래스 다이어그램과 마주하는 어떤 사람이라도 `Square`가 `Rectangle`의 서브타입이라고 입을 모을 것이다. 그러나 일단 클라이언트와의 협력 관계 속으로 모델을 밀어 넣는 순간 지금까지 올바르다고 생각했던 서브타입이 올바르지 않다는 사실을 깨닫게 될 것이다.

대체 가능성을 결정하는 것은 클라이언트다.

### 4.4 is-a 관계 다시 살펴보기

사실 마틴 오더스키의 두 질문을 별개로 취급할 필요는 없다. 클라이언트 관점에서 자식 클래스의 행동이 부모 클래스의 행동과 호환되지 않고 그로 인해 대체가 불가능하다면, 어휘적으로 is-a라고 말할 수 있다 하더라도 그 관계를 is-a 관계라고 할 수 없다.

is-a 관계로 표현된 문장을 볼 때마다 문장 앞에 **"클라이언트 입장에서"**라는 말이 빠져 있다고 생각하라:

- (클라이언트 입장에서) 정사각형은 직사각형이다.
- (클라이언트 입장에서) 펭귄은 새다.

결론적으로 **상속이 서브타이핑을 위해 사용될 경우에만 is-a 관계다**. 서브클래싱을 구현하기 위해 상속을 사용했다면 is-a 관계라고 말할 수 없다.

### 4.5 리스코프 치환 원칙은 유연한 설계의 기반이다

리스코프 치환 원칙을 따르는 설계는 유연할 뿐만 아니라 확장성이 높다. 새로운 자식 클래스를 추가하더라도 클라이언트의 입장에서 동일하게 행동하기만 한다면 클라이언트를 수정하지 않고도 상속 계층을 확장할 수 있다.

8장에서 중복 할인 정책을 구현하기 위해 기존의 `DiscountPolicy` 상속 계층에 새로운 자식 클래스인 `OverlappedDiscountPolicy`를 추가하더라도 클라이언트를 수정할 필요가 없었던 것을 기억하는가?

```
  Movie ──────────▶ DiscountPolicy (추상 클래스)
                    # getDiscountAmount()
                         △
              ┌──────────┼──────────────┐
    Amount           Percent         Overlapped
  DiscountPolicy   DiscountPolicy   DiscountPolicy
```

이 설계는 의존성 역전 원칙(DIP), 리스코프 치환 원칙(LSP), 개방-폐쇄 원칙(OCP)이 한데 어우러져 설계를 확장 가능하게 만든 대표적인 예다:

| 원칙 | 적용 |
|---|---|
| **DIP** | `Movie`와 `OverlappedDiscountPolicy` 모두 추상 클래스인 `DiscountPolicy`에 의존한다 |
| **LSP** | `Movie` 관점에서 `DiscountPolicy` 대신 `OverlappedDiscountPolicy`와 협력하더라도 아무런 문제가 없다 |
| **OCP** | 새로운 `OverlappedDiscountPolicy`를 추가하더라도 `Movie`에는 영향을 끼치지 않는다 |

> **핵심 통찰**: 리스코프 치환 원칙이 어떻게 개방-폐쇄 원칙을 지원하는지 눈여겨보라. 자식 클래스가 클라이언트의 관점에서 부모 클래스를 대체할 수 있다면 기능 확장을 위해 자식 클래스를 추가하더라도 코드를 수정할 필요가 없어진다. 따라서 리스코프 치환 원칙은 개방-폐쇄 원칙을 만족하는 설계를 위한 전제 조건이다. 일반적으로 리스코프 치환 원칙 위반은 잠재적인 개방-폐쇄 원칙 위반이다.

### 4.6 타입 계층과 리스코프 치환 원칙

한 가지 잊지 말아야 하는 사실은 클래스 상속은 타입 계층을 구현할 수 있는 다양한 방법 중 하나일 뿐이라는 것이다. 자바와 C#의 인터페이스나 스칼라의 트레이트, 동적 타입 언어의 덕 타이핑 등의 기법을 사용하면 클래스 사이의 상속을 사용하지 않고도 서브타이핑 관계를 구현할 수 있다.

물론 이런 기법을 사용하는 경우에도 리스코프 치환 원칙을 준수해야만 서브타이핑 관계라고 말할 수 있다. 구현 방법은 중요하지 않다. 핵심은 구현 방법과 무관하게 **클라이언트의 관점에서 슈퍼타입에 대해 기대하는 모든 것이 서브타입에게도 적용돼야 한다**는 것이다.

---

## 5. 계약에 의한 설계와 서브타이핑

클라이언트와 서버 사이의 협력을 의무(*Obligation*)와 이익(*Benefit*)으로 구성된 계약의 관점에서 표현하는 것을 **계약에 의한 설계**(*Design By Contract, DBC*)라고 부른다. 계약에 의한 설계는 세 가지 요소로 구성된다:

| 요소 | 의미 | 책임 |
|---|---|---|
| **사전조건**(*Precondition*) | 메서드를 정상적으로 실행하기 위해 만족시켜야 하는 조건 | 클라이언트의 의무 |
| **사후조건**(*Postcondition*) | 메서드가 실행된 후에 서버가 클라이언트에게 보장해야 하는 조건 | 서버의 의무 |
| **클래스 불변식**(*Class Invariant*) | 메서드 실행 전과 실행 후에 인스턴스가 만족시켜야 하는 조건 | 양쪽 모두 |

리스코프 치환 원칙과 계약에 의한 설계 사이의 관계를 한 문장으로 요약할 수 있다:

> **서브타입이 리스코프 치환 원칙을 만족시키기 위해서는 클라이언트와 슈퍼타입 간에 체결된 '계약'을 준수해야 한다.**

### 5.1 영화 예매 시스템에서의 계약

이해를 돕기 위해 `DiscountPolicy`와 협력하는 `Movie` 클래스를 예로 들어보자.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Movie {
    public Money calculateMovieFee(Screening screening) {
        return fee.minus(discountPolicy.calculateDiscountAmount(screening));
    }
}
```

</details>

```typescript
// TypeScript
class Movie {
    calculateMovieFee(screening: Screening): Money {
        return this.fee.minus(
            this.discountPolicy.calculateDiscountAmount(screening)
        );
    }
}
```

`Movie`는 `DiscountPolicy`의 인스턴스에게 `calculateDiscountAmount` 메시지를 전송하는 클라이언트다. 코드를 살펴보면 직접적으로 언급하지 않았을 뿐 암묵적인 사전조건과 사후조건이 존재한다:

**사전조건**: `calculateDiscountAmount` 메서드는 인자로 전달된 `screening`이 null이 아니고 영화 시작 시간이 아직 지나지 않았다고 가정한다.

```java
assert screening != null &&
       screening.getStartTime().isAfter(LocalDateTime.now());
```

**사후조건**: 반환값은 null이 아니어야 하고, 최소한 0원보다는 커야 한다.

```java
assert amount != null && amount.isGreaterThanOrEqual(Money.ZERO);
```

다음은 `calculateDiscountAmount` 메서드에 사전조건과 사후조건을 추가한 것이다:

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public abstract class DiscountPolicy {
    public Money calculateDiscountAmount(Screening screening) {
        checkPrecondition(screening);

        Money amount = Money.ZERO;
        for (DiscountCondition each : conditions) {
            if (each.isSatisfiedBy(screening)) {
                amount = getDiscountAmount(screening);
                checkPostcondition(amount);
                return amount;
            }
        }

        amount = screening.getMovieFee();
        checkPostcondition(amount);
        return amount;
    }

    protected void checkPrecondition(Screening screening) {
        assert screening != null &&
               screening.getStartTime().isAfter(LocalDateTime.now());
    }

    protected void checkPostcondition(Money amount) {
        assert amount != null &&
               amount.isGreaterThanOrEqual(Money.ZERO);
    }

    abstract protected Money getDiscountAmount(Screening screening);
}
```

</details>

```typescript
// TypeScript
abstract class DiscountPolicy {
    calculateDiscountAmount(screening: Screening): Money {
        this.checkPrecondition(screening);

        let amount = Money.ZERO;
        for (const each of this.conditions) {
            if (each.isSatisfiedBy(screening)) {
                amount = this.getDiscountAmount(screening);
                this.checkPostcondition(amount);
                return amount;
            }
        }

        amount = screening.getMovieFee();
        this.checkPostcondition(amount);
        return amount;
    }

    protected checkPrecondition(screening: Screening): void {
        console.assert(
            screening != null &&
            screening.getStartTime() > new Date()
        );
    }

    protected checkPostcondition(amount: Money): void {
        console.assert(
            amount != null &&
            amount.isGreaterThanOrEqual(Money.ZERO)
        );
    }

    protected abstract getDiscountAmount(screening: Screening): Money;
}
```

`calculateDiscountAmount` 메서드가 정의한 사전조건을 만족시키는 것은 `Movie`의 책임이다:

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Movie {
    public Money calculateMovieFee(Screening screening) {
        if (screening == null ||
            screening.getStartTime().isBefore(LocalDateTime.now())) {
            throw new InvalidScreeningException();
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
        if (screening == null || screening.getStartTime() < new Date()) {
            throw new InvalidScreeningException();
        }
        return this.fee.minus(
            this.discountPolicy.calculateDiscountAmount(screening)
        );
    }
}
```

`DiscountPolicy`의 자식 클래스인 `AmountDiscountPolicy`, `PercentDiscountPolicy`, `OverlappedDiscountPolicy`는 `DiscountPolicy`의 `calculateDiscountAmount` 메서드를 그대로 상속받기 때문에 계약을 변경하지 않는다. 따라서 `Movie`의 입장에서 이 클래스들은 `DiscountPolicy`를 대체할 수 있기 때문에 서브타이핑 관계라고 할 수 있다.

### 5.2 서브타입과 계약

계약의 관점에서 상속이 초래하는 가장 큰 문제는 자식 클래스가 부모 클래스의 메서드를 오버라이딩할 수 있다는 것이다.

**사전조건을 강화하면 서브타입이 될 수 없다:**

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class BrokenDiscountPolicy extends DiscountPolicy {
    @Override
    public Money calculateDiscountAmount(Screening screening) {
        checkPrecondition(screening);                    // 기존의 사전조건
        checkStrongerPrecondition(screening);            // 더 강력한 사전조건
        Money amount = screening.getMovieFee();
        checkPostcondition(amount);                      // 기존의 사후조건
        return amount;
    }

    private void checkStrongerPrecondition(Screening screening) {
        assert screening.getEndTime().toLocalTime()
                        .isBefore(LocalTime.MIDNIGHT);
    }
    // ...
}
```

</details>

```typescript
// TypeScript
class BrokenDiscountPolicy extends DiscountPolicy {
    override calculateDiscountAmount(screening: Screening): Money {
        this.checkPrecondition(screening);               // 기존의 사전조건
        this.checkStrongerPrecondition(screening);       // 더 강력한 사전조건
        const amount = screening.getMovieFee();
        this.checkPostcondition(amount);                 // 기존의 사후조건
        return amount;
    }

    private checkStrongerPrecondition(screening: Screening): void {
        console.assert(
            screening.getEndTime().getHours() < 24  // 자정을 넘기면 안 됨
        );
    }
    // ...
}
```

`Movie`는 오직 `DiscountPolicy`의 사전조건만 알고 있다. `Movie`는 null이 아니면서 시작 시간이 현재 시간 이후인 `Screening`을 전달하면 된다고 생각하기 때문에, 자정이 지난 후에 종료되는 `Screening`을 전달하더라도 문제가 없다고 가정한다. 하지만 `BrokenDiscountPolicy`의 사전조건은 이를 허용하지 않기 때문에 협력은 실패한다.

**사전조건을 약화(또는 동일 유지)하면 서브타입이 될 수 있다:**

사전조건을 제거하면 어떻게 될까? `Movie`는 이미 `DiscountPolicy`가 정의한 사전조건을 만족시키기 위해 null이 아니며 현재 시간 이후에 시작하는 `Screening`을 전달하고 있다. 클라이언트가 이미 자신의 의무를 충실히 수행하고 있기 때문에 이 조건을 체크하지 않는 것이 기존 협력에 어떤 영향도 미치지 않는다.

**사후조건을 강화하면 서브타입이 될 수 있다:**

`BrokenDiscountPolicy`가 `DiscountPolicy`에 정의된 사후조건(amount가 null이 아니고 0원보다 커야 한다)에 "최소 1000원 이상"이라는 새로운 사후조건을 추가한다면, `Movie`는 최소한 0원보다 큰 금액을 반환받기만 하면 협력이 정상적으로 수행됐다고 가정하기 때문에 아무런 문제도 발생하지 않는다.

**사후조건을 약화하면 서브타입이 될 수 없다:**

사후조건을 제거하여 요금 계산 결과가 마이너스라도 그대로 반환하면, `Movie`는 반환된 금액이 0원보다는 크다고 믿고 예매 요금으로 사용할 것이다. 이것은 예매 금액으로 마이너스 금액이 설정되는 원하지 않았던 결과로 이어진다.

### 5.3 계약 규칙 정리

| 조건 | 강화 | 약화 |
|---|---|---|
| **사전조건** | 서브타입이 될 수 없다 | 서브타입이 될 수 있다 |
| **사후조건** | 서브타입이 될 수 있다 | 서브타입이 될 수 없다 |

이 규칙을 직관적으로 이해하면:

- **사전조건**: 서브타입은 슈퍼타입의 클라이언트가 이미 준수하고 있는 규칙보다 더 까다로운 규칙을 요구해서는 안 된다 (같거나 느슨해야 한다).
- **사후조건**: 서브타입은 슈퍼타입이 클라이언트에게 약속한 것보다 더 적게 보장해서는 안 된다 (같거나 더 많이 보장해야 한다).

---

## 설계 원칙

| 원칙 | 설명 | 예제에서의 적용 |
|---|---|---|
| **리스코프 치환 원칙 (LSP)** | 서브타입은 슈퍼타입을 대체할 수 있어야 한다 | `Square`가 `Rectangle`을 대체할 수 없으므로 서브타이핑이 아닌 서브클래싱 |
| **개방-폐쇄 원칙 (OCP)** | 기존 코드 수정 없이 확장 가능해야 한다 | LSP를 만족하면 새 자식 클래스 추가 시 클라이언트 수정 불필요 |
| **인터페이스 분리 원칙 (ISP)** | 클라이언트가 사용하지 않는 메서드에 의존하지 않아야 한다 | `Flyer`와 `Walker` 인터페이스 분리 |
| **의존성 역전 원칙 (DIP)** | 상위 모듈과 하위 모듈 모두 추상화에 의존해야 한다 | `Movie`와 자식 클래스 모두 `DiscountPolicy`에 의존 |
| **계약에 의한 설계 (DBC)** | 사전조건, 사후조건, 불변식으로 협력의 계약을 명시한다 | 서브타입: 사전조건 같거나 약화, 사후조건 같거나 강화 |
| **행동 호환성** | 클라이언트 관점에서 자식이 부모와 동일하게 행동해야 한다 | Penguin은 Bird의 fly 행동과 호환되지 않으므로 서브타입 불가 |

---

## 요약

- **타입은 퍼블릭 인터페이스다**: 객체의 타입을 결정하는 것은 내부 속성이 아니라 외부에 제공하는 행동(퍼블릭 인터페이스)이다.
- **타입 계층은 일반화/특수화 관계다**: 슈퍼타입은 더 일반적인 퍼블릭 인터페이스를, 서브타입은 더 특수한 퍼블릭 인터페이스를 가진다. 서브타입의 인스턴스는 슈퍼타입의 인스턴스로 간주될 수 있다.
- **서브클래싱 vs 서브타이핑**: 코드 재사용 목적의 상속은 서브클래싱(구현 상속)이고, 타입 계층 구성 목적의 상속은 서브타이핑(인터페이스 상속)이다. 올바른 상속은 서브타이핑이다.
- **행동 호환성이 핵심이다**: 두 타입 사이에 행동이 호환될 경우에만 타입 계층으로 묶어야 한다. 행동 호환성의 판단 기준은 클라이언트의 관점이다.
- **is-a는 클라이언트 관점이다**: 어휘적으로 is-a 관계가 성립하더라도 클라이언트 관점에서 행동이 호환되지 않으면 상속을 사용해서는 안 된다. is-a 관계는 클라이언트 입장에서 is-a일 때만 참이다.
- **리스코프 치환 원칙(LSP)**: 서브타입은 기반 타입에 대해 대체 가능해야 하며, 클라이언트가 차이점을 인식하지 못한 채 사용할 수 있어야 한다. LSP는 OCP를 만족하는 설계를 위한 전제 조건이다.
- **계약에 의한 설계**: 서브타입이 슈퍼타입을 대체하려면 사전조건을 강화해서는 안 되고, 사후조건을 약화해서는 안 된다.
- **인터페이스 분리**: 행동이 호환되지 않는 경우 클라이언트의 기대에 따라 인터페이스를 분리하고, 코드 재사용이 필요하면 합성을 사용하라.

---

## 다른 챕터와의 관계

- **Chapter 10 (상속과 코드 재사용)**: 10장에서 다룬 Stack-Vector 문제가 이 장에서 리스코프 치환 원칙 위반의 대표 사례로 재등장한다. 10장의 '코드 재사용 목적의 상속'이 바로 이 장에서 말하는 서브클래싱이다.
- **Chapter 11 (합성과 유연한 설계)**: 서브클래싱의 대안으로 합성을 제시한다. 이 장에서 Penguin이 Bird의 코드를 재사용할 때 합성을 권장하는 것이 11장의 핵심 메시지와 직접 연결된다.
- **Chapter 12 (다형성)**: 12장에서 다룬 서브타입 다형성이 이 장의 서브타이핑 개념과 밀접하게 연관된다. 올바른 타입 계층(서브타이핑)이 있어야 다형성이 정상적으로 동작한다.
- **Chapter 8 (의존성 관리하기)**: 8장의 DiscountPolicy 상속 계층이 이 장에서 DIP, LSP, OCP가 조합된 유연한 설계의 예로 재활용된다.
- **Appendix A (계약에 의한 설계)**: 이 장의 마지막 절에서 소개하는 계약에 의한 설계 개념이 부록 A에서 상세히 다뤄진다.
