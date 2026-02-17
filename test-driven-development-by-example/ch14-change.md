# Chapter 14: Change (변경)

## 핵심 질문

서로 다른 통화 간의 환율 변환을 `Bank.reduce()`에 어떻게 통합하는가? 환율 정보를 관리하기 위한 검색(lookup) 메커니즘은 어떻게 설계하는가?

---

## 1. 현재 상황과 다음 단계

### 1.1 Chapter 13까지의 성과

Chapter 13까지 구현된 시스템은 다음과 같다:

- **Money**: 금액과 통화를 가진 값 객체. `times()`, `plus()`, `equals()` 지원
- **Expression**: 산술 표현식을 나타내는 인터페이스
- **Sum**: 두 Expression의 합을 나타내는 클래스
- **Bank**: `reduce(Expression, String)` — Expression을 특정 통화로 환산

현재 `Bank.reduce()`는 같은 통화끼리의 덧셈만 처리할 수 있다. 예를 들어 `$5 + $5 = $10`은 되지만, `2 CHF → 1 USD` 같은 환율 변환은 아직 지원하지 않는다.

### 1.2 이 챕터의 목표

이 챕터에서는 환율 변환(currency conversion)을 구현한다. 핵심 시나리오는:

> **2 CHF를 USD로 변환하면 1 USD가 되어야 한다** (환율 2:1)

이를 위해 필요한 것들:
1. Bank에 환율을 등록하는 메서드 (`addRate`)
2. Bank에서 환율을 조회하는 메서드 (`rate`)
3. 환율을 저장하기 위한 자료 구조 (해시테이블 + Pair 클래스)
4. `reduce()` 시 환율을 적용하는 로직

## TODO 리스트 (챕터 시작 시점)

- [ ] $5 + 10 CHF = $10 (환율이 2:1인 경우)
- [ ] **$5 + $5에서 Money 반환하기**
- [ ] ~~Bank.reduce(Money)~~
- [ ] **Money에 대한 통화 변환을 수행하는 Reduce**
- [ ] Reduce(Bank, String)

---

## 2. TDD 사이클

### 2.1 첫 번째 사이클: 2 CHF → 1 USD 변환 테스트

#### Red — 실패하는 테스트 작성

가장 핵심적인 테스트부터 작성한다. 2 프랑을 달러로 변환하면 1 달러가 되어야 한다:

```java
public void testReduceMoneyDifferentCurrency() {
    Bank bank = new Bank();
    bank.addRate("CHF", "USD", 2);
    Money result = bank.reduce(Money.franc(2), "USD");
    assertEquals(Money.dollar(1), result);
}
```

이 테스트는 여러 가지를 한꺼번에 요구한다:

- `bank.addRate("CHF", "USD", 2)` — Bank에 "2 CHF = 1 USD"라는 환율을 등록
- `bank.reduce(Money.franc(2), "USD")` — 2 프랑을 달러로 변환
- 결과는 1 달러여야 한다

현재 `Bank.reduce()`는 통화 변환을 하지 않으므로 이 테스트는 **실패**한다. 2 프랑이 그대로 반환되어 `Money.dollar(1)`과 같지 않다.

#### Green — 최소한의 코드로 테스트 통과시키기

`Money.reduce()`에서 환율을 적용하여 통화를 변환해야 한다. 현재 `Money.reduce()`는 다음과 같다:

```java
// 변경 전
public Money reduce(String to) {
    return this;
}
```

환율을 적용하도록 수정한다. 하지만 여기서 문제가 있다 — `Money.reduce()`는 Bank의 환율 정보에 접근할 수 없다. Bank를 매개변수로 전달해야 한다:

```java
// Money.java - 변경 후
public Money reduce(Bank bank, String to) {
    int rate = (currency.equals("CHF") && to.equals("USD"))
        ? 2
        : 1;
    return new Money(amount / rate, to);
}
```

이것은 명백히 **Fake It** 이다. 환율 2가 하드코딩되어 있고, CHF→USD만 처리한다. 하지만 테스트는 통과한다! Green Bar.

> **핵심 통찰**: `reduce()` 메서드에 `Bank`를 매개변수로 전달하는 것은 중요한 설계 결정이다. 환율 정보는 Bank가 관리해야 하는 책임이므로, Money가 Bank에게 환율을 물어보는 것이 자연스럽다. 이것은 **정보 전문가(Information Expert)** 패턴이다 — 정보를 가진 객체에게 해당 정보를 사용하는 책임을 부여한다.

`Bank`를 매개변수로 전달하면서 `Expression` 인터페이스와 `Sum.reduce()`도 함께 수정해야 한다:

```java
// Expression.java
Money reduce(Bank bank, String to);

// Sum.java
public Money reduce(Bank bank, String to) {
    int amount = augend.amount + addend.amount;
    return new Money(amount, to);
}

// Bank.java
public Money reduce(Expression source, String to) {
    return source.reduce(this, to);
}
```

`Bank.reduce()`에서 `this`를 전달함으로써, Expression이 환율 변환에 필요한 Bank 참조를 받을 수 있게 되었다.

#### Refactor — 환율 하드코딩 제거

`Money.reduce()`의 환율 하드코딩을 제거해야 한다. 환율 조회 책임은 Bank에 있어야 한다:

```java
// Money.java - 리팩토링 후
public Money reduce(Bank bank, String to) {
    int rate = bank.rate(currency, to);
    return new Money(amount / rate, to);
}
```

이제 `bank.rate("CHF", "USD")`가 2를 반환해야 한다. 하드코딩을 Money에서 Bank로 옮긴 셈이다:

```java
// Bank.java - 일단 하드코딩으로
int rate(String from, String to) {
    return (from.equals("CHF") && to.equals("USD"))
        ? 2
        : 1;
}
```

테스트 여전히 통과. 하지만 아직 하드코딩이 남아 있다. 이것을 해시테이블로 일반화해야 한다.

---

### 2.2 두 번째 사이클: Pair 클래스로 환율 키 만들기

#### 설계 결정: 환율 저장소

환율을 해시테이블에 저장하려면 **키(key)** 가 필요하다. `"CHF"` → `"USD"` 변환의 키는 두 통화의 쌍(pair)이다. 이를 위해 `Pair` 클래스를 만든다.

```java
// Pair.java
private class Pair {
    private String from;
    private String to;

    Pair(String from, String to) {
        this.from = from;
        this.to = to;
    }

    public boolean equals(Object object) {
        Pair pair = (Pair) object;
        return from.equals(pair.from) && to.equals(pair.to);
    }

    public int hashCode() {
        return 0;
    }
}
```

**주목할 점:**
- `Pair`는 `private` 클래스다 — Bank 내부에서만 사용하는 구현 세부사항이다
- `hashCode()`가 `0`을 반환한다! 이것은 의도적인 것이다

> **핵심 통찰**: `hashCode()`가 0을 반환하면 모든 Pair가 같은 해시 버킷에 들어간다. 이것은 해시테이블의 성능을 O(1)에서 O(n)으로 저하시킨다. 하지만 **현재 테스트에서는 환율이 하나뿐**이므로 성능 문제가 발생하지 않는다. Kent Beck은 "나중에 문제가 되면 그때 고치겠다"고 한다. 이것이 TDD의 철학이다 — **필요할 때까지 최적화하지 않는다.** TODO 리스트에 적어두고 넘어간다.

#### Bank에 환율 해시테이블 추가

```java
// Bank.java
private Hashtable rates = new Hashtable();

void addRate(String from, String to, int rate) {
    rates.put(new Pair(from, to), new Integer(rate));
}

int rate(String from, String to) {
    Integer rate = (Integer) rates.get(new Pair(from, to));
    return rate.intValue();
}
```

이제 `bank.addRate("CHF", "USD", 2)` 호출 시 해시테이블에 환율이 저장되고, `bank.rate("CHF", "USD")`로 조회할 수 있다.

---

### 2.3 세 번째 사이클: 동일 통화 환율 (Identity Rate)

#### Red — 같은 통화끼리의 환율

USD를 USD로 변환하면 환율이 1이어야 한다. 하지만 현재 구현에서는 해시테이블에 USD→USD 환율이 등록되어 있지 않으므로 `NullPointerException`이 발생할 수 있다.

```java
public void testIdentityRate() {
    assertEquals(1, new Bank().rate("USD", "USD"));
}
```

이 테스트는 **실패**한다. `rates.get(new Pair("USD", "USD"))`가 `null`을 반환하고, `null.intValue()`에서 NullPointerException이 발생한다.

#### Green — 동일 통화 처리

```java
// Bank.java
int rate(String from, String to) {
    if (from.equals(to)) return 1;
    Integer rate = (Integer) rates.get(new Pair(from, to));
    return rate.intValue();
}
```

`from`과 `to`가 같은 통화면 환율 1을 반환한다. **테스트 통과!**

#### Refactor

이 구현은 충분히 깔끔하다. 특별한 리팩토링이 필요하지 않다.

---

## 3. 전체 코드 진화 과정

이 챕터에서의 코드 변화를 한눈에 정리한다:

### 3.1 Expression 인터페이스

```java
// 변경 전
interface Expression {
    Money reduce(String to);
}

// 변경 후 — Bank 매개변수 추가
interface Expression {
    Money reduce(Bank bank, String to);
}
```

### 3.2 Money 클래스

```java
// 변경 전
public Money reduce(String to) {
    return this;
}

// 변경 후 — 환율 적용
public Money reduce(Bank bank, String to) {
    int rate = bank.rate(currency, to);
    return new Money(amount / rate, to);
}
```

### 3.3 Sum 클래스

```java
// 변경 전
public Money reduce(String to) {
    int amount = augend.amount + addend.amount;
    return new Money(amount, to);
}

// 변경 후 — Bank 매개변수 추가
public Money reduce(Bank bank, String to) {
    int amount = augend.amount + addend.amount;
    return new Money(amount, to);
}
```

### 3.4 Bank 클래스

```java
// 변경 전
public Money reduce(Expression source, String to) {
    return source.reduce(to);
}

// 변경 후 — 환율 관리 기능 추가
class Bank {
    private Hashtable rates = new Hashtable();

    public Money reduce(Expression source, String to) {
        return source.reduce(this, to);
    }

    void addRate(String from, String to, int rate) {
        rates.put(new Pair(from, to), new Integer(rate));
    }

    int rate(String from, String to) {
        if (from.equals(to)) return 1;
        Integer rate = (Integer) rates.get(new Pair(from, to));
        return rate.intValue();
    }
}
```

### 3.5 Pair 클래스 (Bank 내부)

```java
private class Pair {
    private String from;
    private String to;

    Pair(String from, String to) {
        this.from = from;
        this.to = to;
    }

    public boolean equals(Object object) {
        Pair pair = (Pair) object;
        return from.equals(pair.from) && to.equals(pair.to);
    }

    public int hashCode() {
        return 0;  // 의도적으로 단순화 — 성능보다 정확성 우선
    }
}
```

---

## 4. 설계 결정 분석

### 4.1 환율 조회의 책임: Money vs Bank

환율 변환 로직을 어디에 둘 것인가라는 중요한 설계 질문이 있다:

| 선택지 | 장점 | 단점 |
|--------|------|------|
| **Money가 환율을 알고 있다** | Money 자체가 자급자족 | Money가 모든 환율을 알아야 함 — 책임 과다 |
| **Bank가 환율을 관리한다** | 관심사 분리, 환율 중앙 관리 | reduce()에 Bank를 전달해야 함 |

Kent Beck은 **Bank가 환율을 관리하는 방식**을 선택한다. Money는 단순한 값 객체로 남고, Bank가 금융 도메인의 지식(환율)을 관리한다. 이것은 **Single Responsibility Principle**에 부합한다.

### 4.2 Pair 클래스: 값 객체의 또 다른 예

`Pair` 클래스는 해시테이블의 키로 사용되기 위해 만들어졌다. 핵심 특성:

- **값 객체**: 두 Pair가 같은 from/to를 가지면 동등하다
- **equals()**: 값 기반 동등성 비교
- **hashCode()**: `0`으로 단순화 — "나중에 필요하면 개선"
- **private**: 외부에 노출되지 않는 구현 세부사항

> **핵심 통찰**: Pair의 `hashCode()`가 0인 것은 TDD의 "지금 필요한 것만 구현한다" 원칙의 극단적인 예다. 완벽한 해시 함수를 고민하는 대신, 동작하는 가장 단순한 구현을 선택하고 TODO 리스트에 기록한다. 실제 성능 문제가 발생하면 그때 개선하면 된다.

### 4.3 정수 나눗셈의 한계

`amount / rate`에서 정수 나눗셈을 사용하고 있다. 3 CHF를 2:1 환율로 변환하면 `3 / 2 = 1`(나머지 버림)이 된다. 이것은 명백한 한계이지만, Kent Beck은 일부러 무시한다. Money 반올림 문제는 TODO 리스트에 이미 있으므로, 지금은 핵심 기능(환율 변환)에만 집중한다.

---

## 5. TDD에서 배우는 교훈

### 5.1 Fake It → 점진적 일반화

이 챕터에서의 진화 과정:

```
하드코딩 (rate = 2)
  → Bank에 위임 (bank.rate())
    → 해시테이블로 일반화 (rates.get(new Pair(...)))
      → 특수 케이스 처리 (identity rate)
```

각 단계마다 테스트가 있었고, 각 단계에서 Green Bar를 유지했다. 한 번도 "빨간 불"이 오래 지속된 적이 없다.

### 5.2 매개변수 추가의 파급 효과

`reduce()`에 `Bank` 매개변수를 추가하는 것은 작은 변경 같지만, `Expression` 인터페이스, `Money`, `Sum`, `Bank` 네 곳을 모두 수정해야 했다. 이것이 인터페이스 변경의 비용이다. 하지만 **모든 기존 테스트가 통과하는 상태를 유지하면서** 변경했기 때문에 안전했다.

---

## TODO 리스트 (챕터 종료 시점)

- [ ] $5 + 10 CHF = $10 (환율이 2:1인 경우)
- [ ] $5 + $5에서 Money 반환하기
- [x] ~~Bank.reduce(Money)~~
- [x] ~~Money에 대한 통화 변환을 수행하는 Reduce~~
- [x] ~~Reduce(Bank, String)~~

환율 변환이 구현되었다! `$5 + 10 CHF = $10`의 마지막 퍼즐 조각이 거의 다 맞춰지고 있다. 다음 챕터에서는 드디어 혼합 통화 덧셈을 완성한다.

---

## 요약

- **환율 변환**을 `Bank.reduce()`에 통합했다. 2 CHF를 USD로 변환하면 1 USD가 된다.
- `reduce()` 메서드에 **Bank를 매개변수로 전달**하여, Expression이 환율 정보에 접근할 수 있게 했다.
- **Pair 클래스**를 해시테이블의 키로 사용하여 환율을 저장한다. `equals()`와 `hashCode()`를 오버라이드했다.
- `hashCode()`는 **0을 반환**하도록 단순화했다 — 성능보다 정확성을 우선하고, 필요할 때 개선한다.
- **Identity rate**: 같은 통화끼리의 환율은 항상 1이다 (`USD → USD = 1`).
- `bank.addRate(from, to, rate)`로 환율을 등록하고, `bank.rate(from, to)`로 조회한다.
- TDD의 Fake It 전략으로 하드코딩에서 시작하여 점진적으로 일반화했다.

---

## 다른 챕터와의 관계

- **Chapter 12 (Addition, Finally)**: `Bank.reduce()`의 기본 구조를 만들었다. 이 챕터에서 환율 변환 기능을 추가하여 `reduce()`를 완성에 가깝게 만들었다.
- **Chapter 13 (Make It)**: `Sum.reduce()`와 `Money.reduce()`의 기본 구현을 만들었다. 이 챕터에서 `reduce()` 시그니처에 Bank를 추가하여 환율 변환을 가능하게 했다.
- **Chapter 15 (Mixed Currencies)**: 이 챕터에서 구현한 환율 변환을 바탕으로, 드디어 `$5 + 10 CHF = $10`을 구현한다.
- **Chapter 3 (Equality for All)**: Pair 클래스에서 `equals()`를 오버라이드하는 것은 Chapter 3에서 Money에 `equals()`를 구현한 것과 같은 패턴이다. 값 객체에는 값 기반 동등성이 필수적이다.
- **Chapter 30 (Design Patterns)**: Pair는 값 객체 패턴의 또 다른 적용 사례다. Part III에서 이 패턴이 체계적으로 정리된다.
