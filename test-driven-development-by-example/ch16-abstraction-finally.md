# Chapter 16: Abstraction, Finally (드디어 추상화)

## 핵심 질문

Expression 인터페이스를 완전한 추상화로 만들려면 무엇이 필요한가? Sum도 Money처럼 `plus()`와 `times()`를 지원할 수 있는가? Expression 트리를 진정한 의미에서 일반화하려면?

---

## 1. 추상화의 필요성

### 1.1 현재의 불완전함

Chapter 15에서 `$5 + 10 CHF = $10`을 달성했다. 하지만 현재 시스템에는 빈틈이 있다:

- `Money`는 `plus()`와 `times()`를 지원한다
- `Sum`은 `reduce()`만 지원한다 — `plus()`와 `times()`가 없다

이것은 무슨 의미인가? `$5 + 10 CHF`의 결과(Sum)에 다시 `$5`를 더하거나, 2를 곱할 수 없다는 뜻이다:

```java
// 이것이 안 된다:
Expression sum = fiveBucks.plus(tenFrancs);
Expression total = sum.plus(fiveBucks);    // 컴파일 에러!
Expression doubled = sum.times(2);         // 컴파일 에러!
```

Expression 인터페이스에 `plus()`와 `times()`가 없기 때문이다.

### 1.2 이 챕터의 목표

`Expression` 인터페이스에 `plus()`와 `times()`를 추가하고, `Sum`과 `Money` 모두 이를 구현하여, **어떤 Expression이든 plus와 times를 자유롭게 호출할 수 있도록** 만든다.

## TODO 리스트 (챕터 시작 시점)

- [x] ~~$5 + 10 CHF = $10 (환율이 2:1인 경우)~~
- [ ] $5 + $5에서 Money 반환하기
- [ ] **Expression.plus**
- [ ] **Expression.times**

---

## 2. TDD 사이클

### 2.1 첫 번째 사이클: Sum.plus()

#### Red — Sum에 plus()를 호출하는 테스트

```java
public void testSumPlusMoney() {
    Expression fiveBucks = Money.dollar(5);
    Expression tenFrancs = Money.franc(10);
    Bank bank = new Bank();
    bank.addRate("CHF", "USD", 2);
    Expression sum = new Sum(fiveBucks, tenFrancs).plus(fiveBucks);
    Money result = bank.reduce(sum, "USD");
    assertEquals(Money.dollar(15), result);
}
```

이 테스트가 하는 일:
1. `$5 + 10 CHF = $10 (USD)` — Sum 생성
2. 이 Sum에 `$5`를 더한다 → `($5 + 10 CHF) + $5`
3. `reduce("USD")` → `$10 + $5 = $15`

현재 `Sum`에 `plus()` 메서드가 없으므로 **컴파일 에러**. Red Bar.

#### Green — Sum.plus() 구현

```java
// Sum.java
public Expression plus(Expression addend) {
    return new Sum(this, addend);
}
```

`Sum.plus()`는 `this`(현재 Sum)와 새로운 `addend`를 합치는 새로운 `Sum`을 반환한다. 이것은 Money.plus()와 동일한 구조다:

```java
// Money.java (이미 구현되어 있음)
public Expression plus(Expression addend) {
    return new Sum(this, addend);
}
```

`Expression` 인터페이스에도 `plus()`를 추가한다:

```java
// Expression.java
interface Expression {
    Money reduce(Bank bank, String to);
    Expression plus(Expression addend);
}
```

**테스트 통과! Green Bar!**

#### Refactor

`Money.plus()`와 `Sum.plus()`의 코드가 완전히 동일하다:

```java
// Money.plus()
public Expression plus(Expression addend) {
    return new Sum(this, addend);
}

// Sum.plus()
public Expression plus(Expression addend) {
    return new Sum(this, addend);
}
```

이 중복을 제거할 수 있을까? 공통 상위 클래스에 올리거나 default 메서드로 만들 수 있지만, Kent Beck은 이 단계에서는 그대로 둔다. 두 곳의 중복은 아직 리팩토링할 만큼 부담스럽지 않다.

> **핵심 통찰**: TDD에서 중복 제거는 중요하지만, **모든 중복을 즉시 제거해야 하는 것은 아니다.** 두 곳의 중복은 용인할 수 있고, 세 번째가 나타나면("Rule of Three") 그때 추출한다. Kent Beck은 여기서 실용적인 판단을 보여준다.

---

### 2.2 두 번째 사이클: Sum.times()

#### Red — Sum에 times()를 호출하는 테스트

```java
public void testSumTimes() {
    Expression fiveBucks = Money.dollar(5);
    Expression tenFrancs = Money.franc(10);
    Bank bank = new Bank();
    bank.addRate("CHF", "USD", 2);
    Expression sum = new Sum(fiveBucks, tenFrancs).times(2);
    Money result = bank.reduce(sum, "USD");
    assertEquals(Money.dollar(20), result);
}
```

이 테스트가 하는 일:
1. `$5 + 10 CHF` — Sum 생성
2. 이 Sum에 2를 곱한다 → `($5 + 10 CHF) × 2 = ($5 × 2) + (10 CHF × 2) = $10 + 20 CHF`
3. `reduce("USD")` → `$10 + $10 = $20`

현재 `Sum`에 `times()` 메서드가 없으므로 **컴파일 에러**. Red Bar.

#### Green — Sum.times() 구현

```java
// Sum.java
public Expression times(int multiplier) {
    return new Sum(augend.times(multiplier), addend.times(multiplier));
}
```

Sum의 times()는 **분배 법칙(distributive property)** 을 적용한다:

```
(a + b) × n = (a × n) + (b × n)
```

즉, Sum의 각 피연산자에 multiplier를 곱한 후 새로운 Sum을 만든다.

`Expression` 인터페이스에 `times()`도 추가한다:

```java
// Expression.java
interface Expression {
    Money reduce(Bank bank, String to);
    Expression plus(Expression addend);
    Expression times(int multiplier);
}
```

**테스트 통과! Green Bar!**

#### Refactor

`Sum.times()`에서 `augend.times(multiplier)`를 호출하고 있다. `augend`는 `Expression` 타입이므로, `Expression` 인터페이스에 `times()`가 선언되어 있어야 한다. 위에서 이미 추가했으므로 문제없다.

---

## 3. 완성된 Expression 인터페이스

### 3.1 최종 인터페이스

```java
interface Expression {
    Money reduce(Bank bank, String to);
    Expression plus(Expression addend);
    Expression times(int multiplier);
}
```

이 세 가지 메서드가 Expression의 전체 프로토콜이다:

| 메서드 | 역할 | 반환 타입 |
|--------|------|-----------|
| `reduce(Bank, String)` | 이 표현식을 특정 통화로 환산 | `Money` (구체적인 값) |
| `plus(Expression)` | 이 표현식에 다른 표현식을 더함 | `Expression` (새 표현식) |
| `times(int)` | 이 표현식에 배수를 곱함 | `Expression` (새 표현식) |

> **핵심 통찰**: `plus()`와 `times()`는 `Expression`을 반환하고, `reduce()`만 `Money`를 반환한다. 이것은 **Expression을 만드는 연산**과 **Expression을 평가하는 연산**의 구분이다. 덧셈과 곱셈은 표현식을 만들고, reduce는 표현식을 계산한다. 이것은 컴파일러 이론의 AST(Abstract Syntax Tree)와 인터프리터 패턴을 연상시킨다.

### 3.2 구현 클래스별 메서드 비교

| 메서드 | Money | Sum |
|--------|-------|-----|
| `reduce(bank, to)` | `new Money(amount / bank.rate(currency, to), to)` | `augend.reduce(bank, to).amount + addend.reduce(bank, to).amount` |
| `plus(addend)` | `new Sum(this, addend)` | `new Sum(this, addend)` |
| `times(multiplier)` | `new Money(amount * multiplier, currency)` | `new Sum(augend.times(multiplier), addend.times(multiplier))` |

`plus()`는 Money와 Sum에서 동일하지만, `reduce()`와 `times()`는 각각 다르게 구현된다:

- **Money.times()**: 자신의 amount에 multiplier를 곱한 새 Money를 반환
- **Sum.times()**: 분배 법칙을 적용하여 각 피연산자에 multiplier를 곱한 새 Sum을 반환

---

## 4. Expression 트리의 완전한 모습

### 4.1 표현식 트리 시각화

`($5 + 10 CHF).times(2).plus($3)`를 트리로 그리면:

```
         Sum [plus]
        /          \
   Sum [times(2)]    $3
   /          \
Sum [×2]    Sum [×2]
  |            |
 $10       20 CHF
```

위를 reduce("USD")하면 (환율 2 CHF = 1 USD):

```
$10.reduce → $10
20 CHF.reduce → $10
Sum($10, $10).reduce → $20
$3.reduce → $3
Sum($20, $3).reduce → $23
```

### 4.2 Composite 패턴

이 구조는 **Composite 패턴**의 전형적인 예다:

- **Leaf (단말)**: `Money` — 더 이상 분해되지 않는 값
- **Composite (합성)**: `Sum` — 두 개의 Expression을 포함하는 합성 노드
- **Component (공통 인터페이스)**: `Expression` — Money와 Sum 모두 동일한 인터페이스 제공

Composite 패턴의 핵심 이점: 클라이언트가 Money인지 Sum인지 구분할 필요 없이 `Expression`으로 다룰 수 있다.

---

## 5. 이 챕터에서 변경된 전체 코드

### 5.1 Expression.java

```java
interface Expression {
    Money reduce(Bank bank, String to);
    Expression plus(Expression addend);
    Expression times(int multiplier);
}
```

### 5.2 Sum.java

```java
class Sum implements Expression {
    Expression augend;
    Expression addend;

    Sum(Expression augend, Expression addend) {
        this.augend = augend;
        this.addend = addend;
    }

    public Money reduce(Bank bank, String to) {
        int amount = augend.reduce(bank, to).amount
                   + addend.reduce(bank, to).amount;
        return new Money(amount, to);
    }

    public Expression plus(Expression addend) {
        return new Sum(this, addend);
    }

    public Expression times(int multiplier) {
        return new Sum(augend.times(multiplier), addend.times(multiplier));
    }
}
```

### 5.3 Money.java (참고 — 이미 구현되어 있던 메서드들)

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

    public Expression plus(Expression addend) {
        return new Sum(this, addend);
    }

    public Expression times(int multiplier) {
        return new Money(amount * multiplier, currency);
    }

    public Money reduce(Bank bank, String to) {
        int rate = bank.rate(currency, to);
        return new Money(amount / rate, to);
    }

    public boolean equals(Object object) {
        Money money = (Money) object;
        return amount == money.amount
            && currency().equals(money.currency());
    }

    String currency() {
        return currency;
    }

    public String toString() {
        return amount + " " + currency;
    }
}
```

---

## 6. 남은 TODO 항목: "$5 + $5에서 Money 반환하기"

TODO 리스트에 아직 남아 있는 `$5 + $5에서 Money 반환하기`를 살펴보자. 현재 `$5 + $5`의 결과는 `Sum`이다. 이것을 `reduce()`하면 `Money.dollar(10)`이 되지만, `reduce()` 전에는 Sum이다.

같은 통화끼리의 덧셈은 Sum 대신 바로 Money를 반환하는 것이 더 효율적일 수 있다. 하지만 Kent Beck은 이 최적화를 구현하지 않기로 결정한다. 현재 설계에서 Sum은 항상 `reduce()`를 통해 Money가 되므로, 기능적으로 문제가 없기 때문이다.

> **핵심 통찰**: TODO 리스트의 모든 항목을 구현해야 하는 것은 아니다. 때로는 "이건 필요하지 않다"라고 판단하고 **삭제**하는 것이 올바른 결정이다. YAGNI(You Aren't Gonna Need It) 원칙이다.

---

## TODO 리스트 (챕터 종료 시점)

- [x] ~~$5 + 10 CHF = $10 (환율이 2:1인 경우)~~
- [ ] ~~$5 + $5에서 Money 반환하기~~ (불필요하다고 판단하여 삭제)
- [x] ~~Expression.plus~~
- [x] ~~Expression.times~~

모든 핵심 기능이 구현되었다! Part I의 Money 예제가 사실상 완성된 것이다. 다음 챕터(Chapter 17)에서 전체 과정을 회고한다.

---

## 요약

- `Expression` 인터페이스에 **`plus()`와 `times()`를 추가**하여 완전한 산술 표현식 인터페이스를 완성했다.
- **Sum.plus()**: `new Sum(this, addend)` — Money.plus()와 동일한 구조.
- **Sum.times()**: `new Sum(augend.times(multiplier), addend.times(multiplier))` — **분배 법칙**을 적용하여 각 피연산자에 배수를 곱한다.
- Expression 트리는 **Composite 패턴**이다. Money가 단말 노드, Sum이 합성 노드, Expression이 공통 인터페이스다.
- `plus()`와 `times()`는 Expression을 반환하고, `reduce()`만 Money를 반환한다. **표현식 생성과 표현식 평가가 분리**된 구조다.
- TODO 리스트에서 불필요한 항목(`$5 + $5에서 Money 반환하기`)을 삭제했다. 모든 TODO를 구현하는 것이 목표가 아니다.

---

## 다른 챕터와의 관계

- **Chapter 12 (Addition, Finally)**: Expression 인터페이스와 Sum 클래스의 기본 구조를 만들었다. 이 챕터에서 plus()와 times()를 추가하여 인터페이스를 완성했다.
- **Chapter 15 (Mixed Currencies)**: Sum.reduce()에서 각 피연산자를 reduce()하도록 수정했다. 이 재귀 구조 위에 Sum.plus()와 Sum.times()가 자연스럽게 쌓인다.
- **Chapter 17 (Money Retrospective)**: Part I 전체를 돌아보며, Expression 메타포의 의미, 설계 결정들, TDD 과정을 회고한다.
- **Chapter 2 (Degenerate Objects)**: 값 객체 패턴을 도입했다. Money가 값 객체이고, Sum도 사실상 값 객체다 — 모든 연산이 새 객체를 반환한다.
- **Chapter 30 (Design Patterns)**: Composite 패턴, Value Object 패턴 등 이 챕터에서 사용한 설계 패턴이 Part III에서 체계적으로 정리된다.
