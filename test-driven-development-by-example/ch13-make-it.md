# Chapter 13: Make It (만들어 보자)

## 핵심 질문

`Bank.reduce()`의 하드코딩과 타입 캐스팅을 어떻게 **제대로 된 구현**으로 대체하는가? reduce 로직을 Bank에 집중시킬 것인가, 아니면 Expression 구현체(Sum, Money)에 **다형적으로 위임**할 것인가?

---

## 1. 이전 챕터의 문제점

### 1.1 Bank.reduce()의 현재 구현

Chapter 12에서 작성한 `Bank.reduce()`는 문제가 많다:

```java
class Bank {
    Money reduce(Expression source, String to) {
        Sum sum = (Sum) source;                            // 문제 1: 캐스팅
        int amount = sum.augend.amount + sum.addend.amount; // 문제 2: Sum의 내부 접근
        return new Money(amount, to);                       // 문제 3: 환율 미적용
    }
}
```

**문제 1**: `(Sum) source` — source가 Money일 수도 있는데, 무조건 Sum으로 캐스팅한다.

**문제 2**: Bank가 Sum의 내부 구조(`augend`, `addend`)를 직접 접근한다. 이것은 **캡슐화 위반**이다.

**문제 3**: 환율 변환이 없다. `$5 + 10 CHF`를 처리할 수 없다. (이것은 이후 챕터에서 다룬다.)

이 챕터에서는 문제 1과 2를 해결한다.

---

## 2. 첫 번째 과제: Sum.reduce()

### 2.1 리팩토링 전략 — reduce를 Sum에 위임

Bank가 Sum의 내부를 직접 계산하는 대신, **Sum 자신이 reduce를 수행**하도록 위임한다:

```java
// 현재: Bank가 Sum의 내부를 직접 접근
int amount = sum.augend.amount + sum.addend.amount;

// 목표: Sum에게 reduce를 위임
Money result = sum.reduce(to);
```

이것은 **다형성(polymorphism)** 의 기본 원칙이다 — "데이터를 가진 객체가 그 데이터를 처리하는 로직도 가져야 한다."

### 2.2 TDD 사이클 — Sum.reduce()

#### Red — 테스트 작성

Sum을 직접 reduce하는 테스트를 작성한다:

```java
public void testReduceSum() {
    Expression sum = new Sum(Money.dollar(3), Money.dollar(4));
    Bank bank = new Bank();
    Money result = bank.reduce(sum, "USD");
    assertEquals(Money.dollar(7), result);
}
```

기존 `testSimpleAddition`과 비슷하지만, Sum을 직접 생성하여 reduce하는 것에 초점을 맞춘다.

현재 구현으로도 이 테스트는 통과한다 — Bank.reduce()가 이미 Sum을 처리하기 때문이다. 하지만 **구조를 개선**하기 위해 리팩토링을 진행한다.

#### Green → Refactor — reduce 로직을 Sum으로 이동

**Step 1**: Sum에 `reduce()` 메서드를 추가한다:

```java
class Sum implements Expression {
    Money augend;
    Money addend;

    Sum(Money augend, Money addend) {
        this.augend = augend;
        this.addend = addend;
    }

    public Money reduce(String to) {
        int amount = augend.amount + addend.amount;
        return new Money(amount, to);
    }
}
```

**Step 2**: Bank.reduce()에서 Sum.reduce()를 호출하도록 변경:

```java
class Bank {
    Money reduce(Expression source, String to) {
        Sum sum = (Sum) source;
        return sum.reduce(to);
    }
}
```

테스트 실행 — **Green Bar!**

이제 Bank는 Sum의 내부 구조를 직접 접근하지 않는다. 대신 Sum에게 "너 자신을 reduce해라"라고 위임한다.

> **핵심 통찰**: 이 리팩토링은 "데이터 + 그 데이터를 다루는 로직"을 같은 곳에 두는 **객체지향의 기본 원칙**을 적용한 것이다. Bank가 `sum.augend.amount + sum.addend.amount`를 직접 계산하는 것은 절차적 프로그래밍이다. Sum이 스스로 계산하는 것이 객체지향적이다.

---

## 3. 두 번째 과제: Bank.reduce(Money)

### 3.1 문제: source가 Money인 경우

현재 `Bank.reduce()`는 `(Sum) source`로 캐스팅하므로, source가 Money이면 **ClassCastException**이 발생한다.

하지만 Money도 Expression이다. `bank.reduce(Money.dollar(1), "USD")`는 당연히 `Money.dollar(1)`을 반환해야 한다 (통화가 같으므로 환율 변환 불필요).

### 3.2 TDD 사이클 — Money.reduce()

#### Red — 테스트 작성

```java
public void testReduceMoney() {
    Bank bank = new Bank();
    Money result = bank.reduce(Money.dollar(1), "USD");
    assertEquals(Money.dollar(1), result);
}
```

이 테스트는 실패한다 — `Bank.reduce()`에서 `(Sum) source` 캐스팅 시 ClassCastException이 발생한다.

#### Green — Money에도 reduce() 추가

**Step 1**: Money에 `reduce()` 메서드를 추가한다:

```java
class Money implements Expression {
    // ... 기존 코드

    public Money reduce(String to) {
        return this;
    }
}
```

Money는 이미 단일 통화의 금액이므로, reduce의 결과는 자기 자신이다. (통화 변환은 아직 다루지 않는다.)

**Step 2**: Bank.reduce()에서 다형성을 활용:

```java
class Bank {
    Money reduce(Expression source, String to) {
        if (source instanceof Money) {
            return ((Money) source).reduce(to);
        }
        Sum sum = (Sum) source;
        return sum.reduce(to);
    }
}
```

테스트 실행 — **Green Bar!**

하지만 이 코드에는 문제가 있다 — `instanceof`를 사용한 타입 체크는 좋지 않은 패턴이다. 다형성을 제대로 활용하면 `instanceof`가 필요 없어진다.

### 3.3 Refactor — instanceof 제거, Expression에 reduce() 추가

핵심 아이디어: Expression 인터페이스에 `reduce()` 메서드를 선언하면, Bank는 **source의 타입을 알 필요가 없다**.

**Step 1**: Expression 인터페이스에 reduce() 추가:

```java
interface Expression {
    Money reduce(String to);
}
```

이미 Money와 Sum 모두에 `reduce(String to)` 메서드가 있으므로, 이 인터페이스를 선언해도 컴파일 에러가 발생하지 않는다.

**Step 2**: Bank.reduce()를 다형성으로 단순화:

```java
class Bank {
    Money reduce(Expression source, String to) {
        return source.reduce(to);
    }
}
```

**테스트 실행 — Green Bar!**

`instanceof`도 사라지고, 캐스팅도 사라졌다. Bank는 Expression의 구체적인 타입을 알 필요가 없다. 다형성이 알아서 처리한다.

> **핵심 통찰**: `instanceof`와 타입 캐스팅은 종종 **인터페이스에 메서드가 빠져있다는 신호**다. "이 객체가 Sum인지 Money인지 확인해야 한다면, 둘 다 같은 메서드를 가져야 하는 것은 아닌가?" 이 질문이 다형적 설계로 이어진다.

---

## 4. Bank에서 환율을 전달할 필요성

### 4.1 미래의 문제 예고

현재 `Sum.reduce(String to)`와 `Money.reduce(String to)`는 환율 정보가 없다. 다중 통화 환산을 하려면 환율이 필요하고, 환율은 Bank가 알고 있다.

따라서 미래에는 reduce의 시그니처가 다음과 같이 바뀔 것이다:

```java
// 현재
Money reduce(String to);

// 미래
Money reduce(Bank bank, String to);
```

하지만 Kent Beck은 **지금 이 변경을 하지 않는다**. 현재 테스트가 환율 변환을 요구하지 않기 때문이다. 이 변경은 환율 변환 테스트를 작성할 때 (Chapter 14에서) 자연스럽게 이루어질 것이다.

이것이 TDD의 원칙이다: **필요한 시점에만 변경한다.**

---

## 5. 리팩토링 과정 전체 요약

### 5.1 Bank.reduce()의 진화

```java
// Version 1 (Chapter 12) — 하드코딩
Money reduce(Expression source, String to) {
    return Money.dollar(10);
}

// Version 2 (Chapter 12) — Sum만 처리, 내부 접근
Money reduce(Expression source, String to) {
    Sum sum = (Sum) source;
    int amount = sum.augend.amount + sum.addend.amount;
    return new Money(amount, to);
}

// Version 3 (이 챕터) — Sum에 위임, 하지만 캐스팅
Money reduce(Expression source, String to) {
    Sum sum = (Sum) source;
    return sum.reduce(to);
}

// Version 4 (이 챕터) — instanceof 사용
Money reduce(Expression source, String to) {
    if (source instanceof Money)
        return ((Money) source).reduce(to);
    Sum sum = (Sum) source;
    return sum.reduce(to);
}

// Version 5 (이 챕터, 최종) — 다형성
Money reduce(Expression source, String to) {
    return source.reduce(to);
}
```

5단계에 걸쳐 진화했다. 각 단계는 테스트를 통과하는 상태를 유지하면서 진행되었다.

### 5.2 핵심 리팩토링 기법

| 단계 | 기법 | 설명 |
|------|------|------|
| V2 → V3 | **Move Method** (메서드 이동) | 계산 로직을 Bank에서 Sum으로 이동 |
| V3 → V4 | **Add Polymorphic Case** | Money도 reduce() 가능하도록 |
| V4 → V5 | **Replace Conditional with Polymorphism** | instanceof를 인터페이스 메서드로 대체 |

---

## 6. 이 챕터에서 완성된 코드

### 6.1 Expression 인터페이스

```java
interface Expression {
    Money reduce(String to);
}
```

### 6.2 Money 클래스

```java
class Money implements Expression {
    protected int amount;
    protected String currency;

    Money(int amount, String currency) {
        this.amount = amount;
        this.currency = currency;
    }

    static Money dollar(int amount) {
        return new Money(amount, "USD");
    }

    static Money franc(int amount) {
        return new Money(amount, "CHF");
    }

    Money times(int multiplier) {
        return new Money(amount * multiplier, currency);
    }

    Expression plus(Money addend) {
        return new Sum(this, addend);
    }

    public Money reduce(String to) {
        return this;
    }

    String currency() {
        return currency;
    }

    public boolean equals(Object object) {
        Money money = (Money) object;
        return amount == money.amount
            && currency().equals(money.currency());
    }

    public String toString() {
        return amount + " " + currency;
    }
}
```

### 6.3 Sum 클래스

```java
class Sum implements Expression {
    Money augend;
    Money addend;

    Sum(Money augend, Money addend) {
        this.augend = augend;
        this.addend = addend;
    }

    public Money reduce(String to) {
        int amount = augend.amount + addend.amount;
        return new Money(amount, to);
    }
}
```

### 6.4 Bank 클래스

```java
class Bank {
    Money reduce(Expression source, String to) {
        return source.reduce(to);
    }
}
```

### 6.5 테스트

```java
public void testSimpleAddition() {
    Money five = Money.dollar(5);
    Expression sum = five.plus(five);
    Bank bank = new Bank();
    Money reduced = bank.reduce(sum, "USD");
    assertEquals(Money.dollar(10), reduced);
}

public void testReduceSum() {
    Expression sum = new Sum(Money.dollar(3), Money.dollar(4));
    Bank bank = new Bank();
    Money result = bank.reduce(sum, "USD");
    assertEquals(Money.dollar(7), result);
}

public void testReduceMoney() {
    Bank bank = new Bank();
    Money result = bank.reduce(Money.dollar(1), "USD");
    assertEquals(Money.dollar(1), result);
}
```

---

## 7. 설계의 아름다움

### 7.1 Bank.reduce()의 단순함

최종 `Bank.reduce()`는 단 한 줄이다:

```java
return source.reduce(to);
```

이것은 Bank가 Expression의 **구체적인 구조를 전혀 모른다**는 의미다. Expression이 Sum이든 Money이든, 미래에 Multiply나 Negate 같은 새로운 Expression이 추가되든, Bank의 코드는 변경할 필요가 없다.

### 7.2 Open-Closed Principle (개방-폐쇄 원칙)

이 설계는 자연스럽게 **개방-폐쇄 원칙(OCP)** 을 따른다:

- **확장에 열려 있다**: 새로운 Expression 구현체(예: Multiply, Negate)를 추가하면 새로운 연산을 지원할 수 있다
- **변경에 닫혀 있다**: 새 Expression을 추가해도 Bank, Money, 기존 Expression의 코드를 수정할 필요가 없다

> **핵심 통찰**: Kent Beck은 OCP를 "미리 적용"하려고 하지 않았다. 테스트를 작성하고, 중복을 제거하고, instanceof를 다형성으로 대체하는 **자연스러운 리팩토링 과정**에서 OCP가 달성되었다. 좋은 설계 원칙은 TDD를 성실히 따르면 자연스럽게 나타나는 경우가 많다.

---

## TODO 리스트 (챕터 종료 시점)

- [ ] $5 + 10 CHF = $10 (환율이 2:1인 경우)
- [x] ~~$5 × 2 = $10~~
- [ ] amount를 private으로 만들기
- [x] ~~Dollar 부작용(side effect)?~~
- [ ] Money 반올림?
- [x] ~~equals()~~
- [ ] hashCode()
- [ ] null과의 동등성
- [x] ~~동등성 비교와 클래스 비교~~
- [x] ~~5 CHF × 2 = 10 CHF~~
- [x] ~~Dollar/Franc 중복 제거 완료~~
- [x] ~~공용 equals~~
- [x] ~~공용 times~~
- [x] ~~Franc와 Dollar 비교하기~~
- [x] ~~통화(Currency)?~~
- [x] ~~testFrancMultiplication을 제거해야 하나?~~
- [x] ~~$5 + $5 = $10~~
- [x] ~~$5 + $5에서 Money 반환하기~~
- [x] ~~**Bank.reduce(Money)**~~
- [x] ~~**Money에 대한 reduce 처리**~~
- [ ] **Bank.reduce()에 환율 적용**
- [ ] Sum.plus
- [ ] Expression.times

Bank.reduce()가 Sum과 Money 모두를 올바르게 처리하게 되었다. 다음 과제는 **환율 적용**이다.

---

## 요약

- `Bank.reduce()`의 로직을 Bank에서 **Sum과 Money 각각으로 위임**했다.
- **Sum.reduce()**: augend와 addend의 amount를 더하여 새 Money를 생성한다.
- **Money.reduce()**: 자기 자신을 반환한다 (환율 변환이 없는 경우).
- Expression 인터페이스에 `reduce(String to)` 메서드를 선언하여, **instanceof 없이 다형성으로** 처리할 수 있게 되었다.
- `Bank.reduce()`는 `return source.reduce(to)` 단 한 줄로 단순화되었다.
- 이 리팩토링은 **Move Method → Add Polymorphic Case → Replace Conditional with Polymorphism** 의 순서로 진행되었다.
- 결과적으로 Open-Closed Principle을 자연스럽게 달성했다: 새 Expression 타입을 추가해도 기존 코드를 변경할 필요가 없다.
- 환율 적용은 아직 구현하지 않았다. 이것은 다음 챕터의 과제이다.

---

## 다른 챕터와의 관계

- **Chapter 12 (Addition, Finally)**: Expression, Sum, Bank의 기본 구조를 도입했다. 이 챕터에서 그 구조를 다형적 설계로 정제했다.
- **Chapter 14 (Change)**: Bank에 환율 정보를 추가하고, reduce에서 환율을 적용한다. reduce의 시그니처가 `reduce(Bank bank, String to)`로 변경된다.
- **Chapter 15 (Mixed Currencies)**: 이 챕터에서 완성한 다형적 구조 덕분에, `$5 + 10 CHF` 같은 다중 통화 덧셈을 자연스럽게 처리할 수 있게 된다.
- **Chapter 16 (Abstraction, Finally)**: Sum.plus(), Expression.times() 등을 구현하여 Expression 패턴을 완성한다.
- **Chapter 30 (Design Patterns)**: 이 챕터에서 사용한 Composite 패턴(Expression/Sum/Money)과 다형성이 Part III에서 설계 패턴으로 정리된다.
