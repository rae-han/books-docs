# Chapter 12: Addition, Finally (드디어 더하기)

## 핵심 질문

다중 통화 덧셈(`$5 + 10 CHF = $10`)을 구현하기 위한 **설계**는 어떤 모습이어야 하는가? 복잡한 문제를 다룰 때 TDD는 어떻게 설계를 **점진적으로 발견**하게 도와주는가?

---

## 1. 드디어 덧셈

### 1.1 지금까지의 여정

Chapter 1에서 설정한 TODO 리스트의 첫 번째 항목은 `$5 + 10 CHF = $10 (환율이 2:1인 경우)`이었다. 11개 챕터에 걸쳐 곱셈, 동등성, 통화, 서브클래스 제거 등을 처리했고, 이제 드디어 이 핵심 기능에 착수할 때가 되었다.

하지만 `$5 + 10 CHF`는 환율 변환을 포함하는 복잡한 문제다. Kent Beck은 여기서도 TDD의 원칙을 따른다: **작은 것부터 시작한다.**

### 1.2 작은 걸음: $5 + $5 = $10

다중 통화 덧셈 대신, 같은 통화끼리의 덧셈부터 시작한다:

```
$5 + 10 CHF = $10  ← 이것은 너무 크다
$5 + $5 = $10       ← 이것부터 시작하자
```

같은 통화끼리의 덧셈은 환율 변환이 필요 없으므로 더 단순하다. 하지만 **덧셈의 기본 메커니즘**은 동일하다.

> **핵심 통찰**: Kent Beck은 Chapter 1에서도 같은 전략을 사용했다. `$5 + 10 CHF` 대신 `$5 × 2`부터 시작했다. TDD에서는 항상 **해결할 수 있는 가장 작은 문제**를 먼저 선택한다. 작은 성공이 쌓여서 큰 문제를 해결하는 기반이 된다.

---

## 2. 설계의 핵심: Expression (수식) 패턴

### 2.1 순진한 접근 vs 유연한 접근

`$5 + $5 = $10`을 구현하는 가장 순진한 방법은:

```java
// 순진한 접근 — Money에 plus 메서드 추가
Money plus(Money addend) {
    return new Money(amount + addend.amount, currency);
}
```

이 방법은 같은 통화끼리의 덧셈에는 동작한다. 하지만 **다중 통화 덧셈**을 처리할 수 없다. `$5 + 10 CHF`의 결과는 환율에 따라 달라지므로, **단순히 amount를 더하는 것으로는 해결할 수 없다.**

### 2.2 핵심 통찰: 덧셈은 즉시 수행하지 않는다

Kent Beck의 핵심 설계 아이디어:

> 덧셈의 결과를 즉시 Money로 변환하지 말고, **"수식(Expression)"으로 보관**해두었다가, 나중에 특정 통화로 **환산(reduce)** 할 때 계산한다.

이것은 마치 수학에서 `(5 USD + 10 CHF)`를 하나의 **수식**으로 보관하고, "USD로 환산해라"라는 명령을 받았을 때 비로소 계산하는 것과 같다.

### 2.3 비유: 금융 수식

```
(5 USD + 10 CHF) × 2 + 3 EUR
```

이 전체가 하나의 Expression이다. 이 Expression을 "USD로 환산해라"라고 하면, 각 통화를 환율에 따라 USD로 변환한 후 계산한다.

### 2.4 Expression 패턴의 참여자

Kent Beck은 세 가지 개념을 도입한다:

| 개념 | 역할 | 비유 |
|------|------|------|
| **Expression** | 금융 수식을 나타내는 인터페이스 | 수학 수식 전체 |
| **Sum** | 두 Expression의 덧셈을 나타내는 클래스 | `a + b` |
| **Bank** | Expression을 특정 통화로 환산하는 클래스 | 은행 (환율 적용) |
| **Money** | 단일 통화의 금액 (Expression의 가장 단순한 형태) | 숫자 하나 |

```
Money ---implements---> Expression <---implements--- Sum
                             |
                        Bank.reduce()
                             |
                          Money (결과)
```

> **핵심 통찰**: 이 설계에서 핵심적인 결정은 **Money.plus()가 Money를 반환하지 않고 Expression을 반환한다**는 것이다. 이것은 "즉시 계산"에서 "지연 계산"으로의 전환이다. 실제 계산(환율 적용)은 Bank.reduce()에서 수행된다. 이 분리가 다중 통화 지원의 핵심이다.

---

## 3. TDD 사이클

### 3.1 Red — $5 + $5 = $10 테스트 작성

Kent Beck은 원하는 API를 테스트에 먼저 표현한다:

```java
public void testSimpleAddition() {
    Money five = Money.dollar(5);
    Expression sum = five.plus(five);
    Bank bank = new Bank();
    Money reduced = bank.reduce(sum, "USD");
    assertEquals(Money.dollar(10), reduced);
}
```

이 테스트가 표현하는 의도:
1. 5 USD + 5 USD를 수행한다 → 결과는 Expression(수식)이다
2. Bank에게 이 Expression을 "USD"로 환산하라고 요청한다
3. 결과는 10 USD다

이 테스트는 여러 컴파일 에러를 발생시킨다:
- `Expression` 인터페이스가 없다
- `Money.plus()` 메서드가 없다
- `Bank` 클래스가 없다
- `Bank.reduce()` 메서드가 없다

### 3.2 Green — 최소한의 코드로 테스트 통과

Kent Beck은 컴파일 에러를 하나씩 해결하면서, **가장 단순한 구현**으로 테스트를 통과시킨다.

**Step 1**: Expression 인터페이스 생성:

```java
interface Expression {
}
```

빈 인터페이스다. 아직 어떤 메서드가 필요한지 알지 못하므로 비워둔다.

**Step 2**: Money에 plus() 메서드 추가:

```java
// Money.java
Expression plus(Money addend) {
    return new Money(amount + addend.amount, currency);
}
```

그리고 Money가 Expression을 구현하도록 선언한다:

```java
class Money implements Expression {
    // ... 기존 코드
}
```

여기서 `plus()`는 단순히 amount를 더한 새 Money를 반환한다. 이것은 **Fake It** 전략이다 — 실제로는 Sum 객체를 반환해야 하지만, 지금은 테스트를 통과시키는 것이 우선이다.

**Step 3**: Bank 클래스 생성:

```java
class Bank {
    Money reduce(Expression source, String to) {
        return Money.dollar(10);  // Fake It!
    }
}
```

`reduce()`도 하드코딩된 값을 반환한다. 역시 Fake It이다.

**테스트 실행 — Green Bar!**

### 3.3 Refactor — Fake It에서 진짜 구현으로

지금 코드에는 두 가지 하드코딩이 있다:

1. `Money.plus()`가 Money를 반환한다 (Sum이어야 한다)
2. `Bank.reduce()`가 `Money.dollar(10)`을 반환한다 (실제 계산이어야 한다)

이것을 단계적으로 수정해나간다. 하지만 이 챕터에서는 먼저 **Sum 클래스를 도입**하는 것에 집중한다.

**Step 4**: `Money.plus()`가 Sum을 반환하도록 변경:

```java
Expression plus(Money addend) {
    return new Sum(this, addend);
}
```

**Step 5**: Sum 클래스 생성:

```java
class Sum implements Expression {
    Money augend;  // 피가산수 (더해지는 수)
    Money addend;  // 가산수 (더하는 수)

    Sum(Money augend, Money addend) {
        this.augend = augend;
        this.addend = addend;
    }
}
```

> **용어 설명**: `augend`와 `addend`는 덧셈의 수학적 용어다.
> - augend: 피가산수 (더해지는 수, 왼쪽)
> - addend: 가산수 (더하는 수, 오른쪽)
> - 예: `5 + 3`에서 5가 augend, 3이 addend

**Step 6**: `Bank.reduce()`에서 Sum을 처리:

```java
class Bank {
    Money reduce(Expression source, String to) {
        Sum sum = (Sum) source;  // 지금은 Sum만 처리
        int amount = sum.augend.amount + sum.addend.amount;
        return new Money(amount, to);
    }
}
```

여기서 `(Sum) source`라는 캐스팅은 분명히 문제가 있다 — source가 항상 Sum인 것은 아니다. 하지만 **지금은** 테스트를 통과시키는 것이 우선이다. 이 문제는 TODO 리스트에 적어둔다.

**테스트 실행 — Green Bar!**

---

## 4. 이 시점의 전체 코드

### 4.1 Expression 인터페이스

```java
interface Expression {
}
```

### 4.2 Money 클래스

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

### 4.3 Sum 클래스

```java
class Sum implements Expression {
    Money augend;
    Money addend;

    Sum(Money augend, Money addend) {
        this.augend = augend;
        this.addend = addend;
    }
}
```

### 4.4 Bank 클래스

```java
class Bank {
    Money reduce(Expression source, String to) {
        Sum sum = (Sum) source;
        int amount = sum.augend.amount + sum.addend.amount;
        return new Money(amount, to);
    }
}
```

### 4.5 테스트

```java
public void testSimpleAddition() {
    Money five = Money.dollar(5);
    Expression sum = five.plus(five);
    Bank bank = new Bank();
    Money reduced = bank.reduce(sum, "USD");
    assertEquals(Money.dollar(10), reduced);
}
```

---

## 5. 설계 결정 분석

### 5.1 왜 Bank가 필요한가?

`plus()`가 직접 결과를 계산하지 않고 Bank를 통해 reduce하는 이유:

| 방식 | 코드 | 문제점 |
|------|------|--------|
| 직접 계산 | `five.plus(tenCHF)` → Money | 환율 정보를 Money가 알아야 한다 |
| Bank 통해 계산 | `bank.reduce(expression, "USD")` → Money | 환율 정보는 Bank에 집중 |

환율은 **외부 정보**다. Money 객체가 환율을 알 필요가 없다. 환율 관리는 Bank의 책임이다. 이 분리 덕분에:

- Money는 단순하게 유지된다 (값 객체)
- 환율이 바뀌어도 Money 코드는 변경되지 않는다
- 서로 다른 Bank 인스턴스가 서로 다른 환율을 가질 수 있다

### 5.2 왜 Expression 인터페이스인가?

Money도 Expression이고, Sum도 Expression이다. 이 인터페이스가 있으면:

```java
Expression a = Money.dollar(5);                    // 단순 금액
Expression b = new Sum(Money.dollar(5), Money.franc(10));  // 덧셈
Expression c = new Sum(a, b);                      // 중첩된 수식

bank.reduce(a, "USD");  // → 5 USD
bank.reduce(b, "USD");  // → 5 + (10 ÷ 환율) USD
bank.reduce(c, "USD");  // → 5 + 5 + (10 ÷ 환율) USD
```

Expression은 **재귀적 구조(Composite Pattern)** 를 가능하게 한다. 수식 안에 수식이 들어갈 수 있다. 이것은 미래의 복잡한 금융 계산을 위한 유연한 기반이다.

### 5.3 지금 코드의 한계와 TODO

현재 코드에는 의도적인 한계가 있다:

1. **`Bank.reduce()`가 Sum만 처리한다** — source가 Money인 경우를 처리하지 못한다
2. **환율 변환이 없다** — 같은 통화의 덧셈만 동작한다
3. **`(Sum) source` 캐스팅** — 타입 안전하지 않다

이것들은 모두 다음 챕터에서 다룰 문제이다. TDD에서는 **현재 테스트가 요구하는 것만** 구현한다.

> **핵심 통찰**: 이 챕터에서 가장 중요한 것은 코드가 아니라 **설계**다. Expression/Sum/Bank라는 구조를 발견한 것이 핵심이다. Kent Beck은 이 설계를 "미리 계획"하지 않았다. 테스트를 작성하면서 — 원하는 API를 먼저 표현하면서 — 자연스럽게 이 구조가 드러났다. TDD는 설계를 **발견**하는 도구이기도 하다.

---

## 6. Metaphor(은유)의 힘

Kent Beck은 이 설계를 **수학적 수식의 은유**에서 가져왔다고 말한다:

- Money는 **숫자** (리프 노드)
- Sum은 **덧셈 연산** (중간 노드)
- Bank.reduce()는 **계산 실행** (평가)
- Expression은 **수식 전체** (트리)

이것은 컴파일러의 AST(Abstract Syntax Tree)와도 유사하다:

```
     Sum (Expression)
    /    \
Money(5)  Money(5)     → bank.reduce() → Money(10)
```

이 은유가 설계의 방향을 안내한다. "덧셈 외에 어떤 연산이 필요한가?" → "곱셈도 Expression이 될 수 있지 않을까?" → "times()도 Expression을 반환하게 하면?" 이런 식으로 은유가 설계의 확장 방향을 자연스럽게 제시한다.

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
- [x] ~~**$5 + $5 = $10**~~
- [ ] $5 + $5에서 Money 반환하기
- [ ] **Bank.reduce(Money)**
- [ ] **Money에 대한 reduce 처리**
- [ ] **Sum.plus**
- [ ] **Expression.times**

`$5 + $5 = $10`이 완료되었다. 하지만 Bank.reduce()가 Sum만 처리하는 문제 등 여러 TODO가 추가되었다.

---

## 요약

- `$5 + 10 CHF = $10`이라는 큰 문제 대신, `$5 + $5 = $10`이라는 **작은 문제**부터 시작했다.
- 핵심 설계 결정: `Money.plus()`는 Money가 아닌 **Expression**을 반환한다. 실제 계산은 `Bank.reduce()`에서 수행된다.
- **Expression** 인터페이스, **Sum** 클래스, **Bank** 클래스를 도입했다.
- Money는 Expression의 가장 단순한 형태이고, Sum은 두 Expression의 덧셈이다.
- Bank는 환율 정보를 가지고 Expression을 특정 통화의 Money로 환산하는 책임을 진다.
- 현재 `Bank.reduce()`는 Sum만 처리하며, 환율 변환도 없다. 이것은 다음 챕터들에서 해결될 것이다.
- **TDD에서 설계는 "계획"이 아니라 "발견"이다.** 테스트를 작성하면서 원하는 API를 먼저 표현하면, 필요한 구조가 자연스럽게 드러난다.

---

## 다른 챕터와의 관계

- **Chapter 1 (Multi-Currency Money)**: TODO 리스트의 첫 항목 `$5 + 10 CHF = $10`을 향한 첫 걸음이 이 챕터에서 시작되었다.
- **Chapter 11 (The Root of All Evil)**: 서브클래스 제거가 완료되어 코드가 단순해진 상태에서 새로운 설계(Expression 패턴)를 도입했다.
- **Chapter 13 (Make It)**: `Bank.reduce()`를 Sum과 Money 각각에 대해 제대로 구현한다.
- **Chapter 14 (Change)**: Bank에 환율 정보를 추가하여 다중 통화 환산을 구현한다.
- **Chapter 15 (Mixed Currencies)**: 드디어 `$5 + 10 CHF = $10` 테스트를 통과시킨다.
- **Chapter 16 (Abstraction, Finally)**: Sum.plus(), Expression.times() 등 Expression 패턴을 완성한다.
