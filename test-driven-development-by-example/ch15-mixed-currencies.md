# Chapter 15: Mixed Currencies (혼합 통화)

## 핵심 질문

서로 다른 통화를 더하는 연산 — TODO 리스트의 첫 번째이자 가장 핵심적인 항목 — 을 어떻게 구현하는가? `$5 + 10 CHF = $10`이라는 목표를 드디어 달성할 수 있는가?

---

## 1. 드디어 핵심 목표에 도달

### 1.1 Chapter 1에서 시작된 여정

Chapter 1의 첫 번째 TODO 리스트에서 가장 처음 적었던 항목을 기억하는가?

> `$5 + 10 CHF = $10 (환율이 2:1인 경우)`

이것은 전체 Money 예제의 **존재 이유**다. 다중 통화 보고서를 만들려면, 서로 다른 통화의 금액을 합산할 수 있어야 한다. Chapter 1에서는 이 문제가 너무 커서 더 작은 문제(`$5 × 2 = $10`)부터 시작했다. 그리고 14개 챕터에 걸쳐:

- Dollar 클래스를 만들고 (Chapter 1)
- 값 객체로 바꾸고 (Chapter 2)
- equals()를 구현하고 (Chapter 3)
- Franc을 추가하고 (Chapter 5)
- 공통 상위 클래스 Money로 통합하고 (Chapter 6~11)
- Expression과 Sum으로 덧셈을 모델링하고 (Chapter 12~13)
- 환율 변환을 구현했다 (Chapter 14)

이 모든 것이 이 한 줄의 테스트를 위한 준비였다.

### 1.2 이 챕터의 목표

`$5 + 10 CHF`를 환율 2:1로 계산하여 `$10`을 얻는 것이다.

## TODO 리스트 (챕터 시작 시점)

- [ ] **$5 + 10 CHF = $10 (환율이 2:1인 경우)**
- [ ] $5 + $5에서 Money 반환하기

---

## 2. TDD 사이클

### 2.1 Red — 혼합 통화 덧셈 테스트

```java
public void testMixedAddition() {
    Expression fiveBucks = Money.dollar(5);
    Expression tenFrancs = Money.franc(10);
    Bank bank = new Bank();
    bank.addRate("CHF", "USD", 2);
    Money result = bank.reduce(fiveBucks.plus(tenFrancs), "USD");
    assertEquals(Money.dollar(10), result);
}
```

이 테스트가 하는 일을 단계별로 분해하면:

1. `Money.dollar(5)` — 5달러 생성
2. `Money.franc(10)` — 10프랑 생성
3. `bank.addRate("CHF", "USD", 2)` — 환율 등록: 2 CHF = 1 USD
4. `fiveBucks.plus(tenFrancs)` — $5 + 10 CHF → Sum 객체 생성
5. `bank.reduce(sum, "USD")` — Sum을 USD로 환산
   - $5 → $5 (이미 USD)
   - 10 CHF → $5 (10 ÷ 2)
   - $5 + $5 = $10
6. 결과는 `Money.dollar(10)`과 같아야 한다

**테스트 결과: 실패!** `Money.dollar(15)`가 반환된다. 왜?

### 2.2 실패 원인 분석

`Sum.reduce()`를 살펴보자:

```java
// Sum.java — 현재 코드
public Money reduce(Bank bank, String to) {
    int amount = augend.amount + addend.amount;
    return new Money(amount, to);
}
```

문제가 보이는가? `augend.amount + addend.amount`에서 **각 피연산자를 먼저 목표 통화로 변환하지 않고** 그냥 금액을 더하고 있다. `5(USD) + 10(CHF) = 15`가 되어 버린다. 10 CHF를 먼저 5 USD로 변환한 후 더해야 한다.

### 2.3 Green — Sum.reduce()에서 각 피연산자를 reduce

핵심 수정: 각 피연산자를 먼저 목표 통화로 `reduce()`한 후에 더한다:

```java
// Sum.java — 수정 후
public Money reduce(Bank bank, String to) {
    int amount = augend.reduce(bank, to).amount
               + addend.reduce(bank, to).amount;
    return new Money(amount, to);
}
```

변경점을 비교하면:

```
// 변경 전 (잘못된 코드)
int amount = augend.amount + addend.amount;

// 변경 후 (올바른 코드)
int amount = augend.reduce(bank, to).amount
           + addend.reduce(bank, to).amount;
```

`augend.reduce(bank, to)` — 왼쪽 피연산자를 목표 통화로 변환
`addend.reduce(bank, to)` — 오른쪽 피연산자를 목표 통화로 변환

이렇게 하면:
- `Money.dollar(5).reduce(bank, "USD")` → `Money.dollar(5)` (변환 불필요)
- `Money.franc(10).reduce(bank, "USD")` → `Money.dollar(5)` (10 ÷ 2 = 5)
- 합계: `5 + 5 = 10` → `Money.dollar(10)`

**테스트 통과! Green Bar!**

> **핵심 통찰**: 이 수정은 단 한 줄이지만, 의미는 크다. 각 피연산자가 자신을 목표 통화로 변환할 수 있다는 것은 `reduce()`가 **재귀적으로 동작**한다는 의미다. Sum의 augend나 addend가 또 다른 Sum이라면? 그 Sum도 자신의 피연산자를 reduce할 것이다. 이것이 Expression 트리의 힘이다 — 아무리 복잡한 산술 표현식도 재귀적으로 처리할 수 있다.

### 2.4 Refactor — 타입 정리

테스트 코드를 다시 보자:

```java
Expression fiveBucks = Money.dollar(5);
Expression tenFrancs = Money.franc(10);
```

`fiveBucks`와 `tenFrancs`의 타입이 `Expression`이다. 원래는 `Money`였을 수도 있지만, Kent Beck은 의도적으로 `Expression`으로 선언한다. 왜?

- `plus()`는 `Expression` 인터페이스의 메서드여야 한다
- 만약 `Money` 타입으로 선언하면 `Money.plus()`만 호출 가능하다
- `Expression` 타입으로 선언하면 어떤 Expression이든 `plus()`를 호출할 수 있다

하지만 현재 `Expression` 인터페이스에는 `plus()`가 선언되어 있지 않다! 이것은 다음 챕터(Chapter 16)에서 다룰 문제다. 지금은 이 테스트가 약간의 캐스팅이 필요할 수 있지만, 핵심 기능은 동작한다.

---

## 3. "$5 + 10 CHF = $10" 달성의 의미

### 3.1 14개 챕터의 여정

| 챕터 | 달성한 것 | $5 + 10 CHF를 위한 기여 |
|------|-----------|------------------------|
| Ch 1 | Dollar 곱하기 | Money의 기본 구조 |
| Ch 2 | 값 객체 패턴 | 불변 객체로 안전한 연산 |
| Ch 3 | equals() | 값 비교 가능 |
| Ch 5 | Franc 추가 | 두 번째 통화 도입 |
| Ch 6~11 | Money 통합 | 하나의 Money 클래스로 다중 통화 지원 |
| Ch 12 | Expression, Sum | 덧셈의 추상적 표현 |
| Ch 13 | Bank.reduce() | 표현식을 특정 통화로 환산 |
| Ch 14 | 환율 변환 | 다른 통화로 변환 가능 |
| **Ch 15** | **혼합 통화 덧셈** | **최종 목표 달성!** |

### 3.2 TDD의 작은 걸음

$5 + 10 CHF = $10이라는 문제를 직접 풀려 했다면, 처음부터 Expression 트리, 환율 해시테이블, Pair 클래스 등을 한꺼번에 설계해야 했을 것이다. 하지만 TDD의 작은 걸음 방식으로:

1. 가장 단순한 문제($5 × 2)에서 시작하여
2. 각 단계에서 하나의 테스트만 추가하고
3. 그 테스트를 통과시키는 데 필요한 최소한의 코드만 작성하고
4. 중복을 제거하며 설계를 개선했다

그 결과, 자연스럽게 현재의 설계가 도출되었다.

> **핵심 통찰**: Kent Beck이 "$5 + 10 CHF = $10" 테스트를 Chapter 1이 아닌 Chapter 15에서야 통과시킨 것은 의도적이다. 큰 문제를 작은 문제들로 분해하고, 각 작은 문제를 해결하면서 점진적으로 큰 문제의 해결책이 쌓여간다. 이것이 TDD에서 "어떤 테스트를 먼저 작성할 것인가?"가 중요한 이유다.

---

## 4. Sum.reduce()의 재귀적 구조

수정된 `Sum.reduce()`가 어떻게 복잡한 표현식을 처리하는지 살펴보자:

### 4.1 단순한 경우: $5 + 10 CHF

```
bank.reduce($5 + 10 CHF, "USD")
  → Sum($5, 10 CHF).reduce(bank, "USD")
    → $5.reduce(bank, "USD")       → $5
    → 10 CHF.reduce(bank, "USD")   → $5  (10 ÷ 2)
    → $5 + $5 = $10
```

### 4.2 복잡한 경우: ($5 + 10 CHF) + $3 (아직 구현되지 않은 미래의 시나리오)

```
bank.reduce(($5 + 10 CHF) + $3, "USD")
  → Sum(Sum($5, 10 CHF), $3).reduce(bank, "USD")
    → Sum($5, 10 CHF).reduce(bank, "USD")  → $10  (위의 결과)
    → $3.reduce(bank, "USD")               → $3
    → $10 + $3 = $13
```

Expression 트리의 각 노드가 자신을 `reduce()`할 수 있기 때문에, 아무리 깊이 중첩되어도 재귀적으로 처리된다. 이것이 **Composite 패턴**의 힘이다.

---

## 5. 이 챕터에서 변경된 코드

### 5.1 Sum.java (핵심 변경)

```java
// Sum.java
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
}
```

### 5.2 테스트 코드

```java
public void testMixedAddition() {
    Expression fiveBucks = Money.dollar(5);
    Expression tenFrancs = Money.franc(10);
    Bank bank = new Bank();
    bank.addRate("CHF", "USD", 2);
    Money result = bank.reduce(fiveBucks.plus(tenFrancs), "USD");
    assertEquals(Money.dollar(10), result);
}
```

---

## TODO 리스트 (챕터 종료 시점)

- [x] ~~$5 + 10 CHF = $10 (환율이 2:1인 경우)~~
- [ ] $5 + $5에서 Money 반환하기
- [ ] Expression.plus
- [ ] Expression.times

TODO 리스트의 첫 번째 항목이 드디어 완료되었다! 하지만 새로운 항목들이 추가되었다. `Expression`이 `plus()`와 `times()`를 직접 지원해야 한다는 것이다. 이것은 다음 챕터(Chapter 16)에서 다룬다.

---

## 요약

- **$5 + 10 CHF = $10** — Chapter 1에서 시작된 핵심 목표를 드디어 달성했다.
- 수정은 놀라울 정도로 간단했다: `Sum.reduce()`에서 각 피연산자를 `reduce()`한 후 더하도록 변경하면 끝이다.
- `augend.reduce(bank, to).amount + addend.reduce(bank, to).amount` — 이 한 줄이 핵심이다.
- 이 수정이 가능했던 이유는 이전 14개 챕터에서 **Expression 인터페이스, reduce() 프로토콜, 환율 변환**을 차근차근 쌓아왔기 때문이다.
- **Expression 트리는 재귀적**으로 동작한다. 아무리 복잡한 표현식도 각 노드가 자신을 reduce()하면서 처리된다.
- TDD의 작은 걸음 방식으로 14개 챕터에 걸쳐 점진적으로 해결책을 쌓아올린 결과, 최종 수정은 단 한 줄로 끝났다.

---

## 다른 챕터와의 관계

- **Chapter 1 (Multi-Currency Money)**: 이 챕터에서 달성한 `$5 + 10 CHF = $10`은 Chapter 1의 첫 번째 TODO 항목이었다. 15개 챕터에 걸친 여정이 완결되었다.
- **Chapter 12 (Addition, Finally)**: Expression과 Sum의 기본 구조를 만들었다. 이 챕터에서 Sum.reduce()를 수정하여 혼합 통화 덧셈을 완성했다.
- **Chapter 14 (Change)**: 환율 변환 기능을 구현했다. 이 기능이 있어야 Sum.reduce()에서 각 피연산자를 목표 통화로 변환할 수 있다.
- **Chapter 16 (Abstraction, Finally)**: Expression 인터페이스에 `plus()`와 `times()`를 추가하여 표현식 트리를 더 유연하게 만든다.
- **Chapter 17 (Money Retrospective)**: Part I 전체를 회고하면서, 이 챕터에서 달성한 것의 의미를 돌아본다.
