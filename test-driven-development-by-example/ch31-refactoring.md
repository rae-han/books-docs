# Chapter 31: Refactoring (리팩토링)

## 핵심 질문

TDD의 "Refactor" 단계에서 사용하는 구체적인 리팩토링 기법들은 무엇이며, 각각 언제 적용하는가?

---

## 1. 개요

TDD의 사이클은 Red → Green → **Refactor**다. Green 단계에서 "동작하는 코드"를 만들었다면, Refactor 단계에서 "깨끗한 코드"로 만든다. Kent Beck은 이 단계를 "죄를 짓고(Green), 속죄하는(Refactor)" 과정에 비유한다.

이 챕터에서 다루는 리팩토링들은 Martin Fowler의 "Refactoring" 책에서 다루는 것들과 겹치지만, TDD의 맥락에서 특히 자주 사용되는 것들을 선별하여 정리한다. 각 리팩토링이 Part I 또는 Part II에서 실제로 사용된 지점도 함께 설명한다.

리팩토링의 대전제:

> **핵심 통찰**: 리팩토링은 **테스트가 통과하는 상태에서만** 수행한다. Green Bar가 없으면 리팩토링하지 않는다. 리팩토링 중 테스트가 실패하면, 리팩토링을 되돌리고 더 작은 단계로 다시 시도한다.

---

## 2. Reconcile Differences (차이 조정)

### 2.1 정의

**두 개의 유사한 코드를 점진적으로 동일하게 만든 다음, 하나로 통합한다.**

### 2.2 적용 시점

비슷하지만 미묘하게 다른 코드가 두 곳에 있을 때 사용한다. 핵심은 **한 번에 통합하지 않고, 먼저 두 코드를 완전히 동일하게 만든 후 통합**하는 것이다.

### 2.3 Part I에서의 사례: Dollar와 Franc

Part I에서 이 기법이 가장 극적으로 사용된 곳은 `Dollar`와 `Franc`의 통합이다:

```java
// 1단계: 차이를 확인한다
class Dollar extends Money {
    Dollar(int amount, String currency) {
        super(amount, currency);
    }
    Money times(int multiplier) {
        return Money.dollar(amount * multiplier);
    }
}

class Franc extends Money {
    Franc(int amount, String currency) {
        super(amount, currency);
    }
    Money times(int multiplier) {
        return Money.franc(amount * multiplier);
    }
}
```

두 클래스의 차이점은 `Money.dollar()` vs `Money.franc()` 뿐이다.

```java
// 2단계: 차이를 제거하여 동일하게 만든다
class Dollar extends Money {
    Money times(int multiplier) {
        return new Money(amount * multiplier, currency);
    }
}

class Franc extends Money {
    Money times(int multiplier) {
        return new Money(amount * multiplier, currency);
    }
}
```

이제 두 `times()` 메서드가 완전히 동일하다.

```java
// 3단계: 상위 클래스로 올린다
class Money {
    Money times(int multiplier) {
        return new Money(amount * multiplier, currency);
    }
}
// Dollar와 Franc 하위 클래스 제거 가능
```

### 2.4 단계

1. 두 코드 조각의 차이점을 식별한다
2. 차이점을 하나씩 제거하여 코드를 동일하게 만든다 (각 단계마다 테스트 실행)
3. 완전히 동일해지면 하나로 통합한다
4. 테스트를 실행하여 확인한다

> **핵심 통찰**: 이 기법의 핵심은 "통합하기 전에 먼저 동일하게 만들기"다. 한 번에 두 코드를 합치려 하면 실수가 생기기 쉽다. 대신, 작은 단계로 차이를 하나씩 줄여가면 안전하게 통합할 수 있다. 매 단계마다 테스트가 통과하는 것을 확인한다.

---

## 3. Isolate Change (변경 격리)

### 3.1 정의

**무언가를 변경하기 전에, 변경 대상을 나머지 코드로부터 격리한다.**

### 3.2 적용 시점

큰 메서드나 클래스에서 일부분만 변경하고 싶을 때 사용한다. 변경 대상이 다른 코드와 얽혀 있으면, 먼저 변경 대상을 분리하고 나서 변경한다.

### 3.3 예시

```java
// 이 메서드의 세금 계산 로직을 바꾸고 싶다
public Money calculateTotal(Order order) {
    Money subtotal = Money.zero();
    for (Item item : order.getItems()) {
        subtotal = subtotal.plus(item.price().times(item.quantity()));
    }
    // 세금 계산 (변경하고 싶은 부분)
    Money tax = subtotal.times(0.08);
    Money shipping = calculateShipping(order);
    return subtotal.plus(tax).plus(shipping);
}
```

먼저 변경 대상을 격리한다:

```java
// 1단계: Extract Method로 격리
public Money calculateTotal(Order order) {
    Money subtotal = calculateSubtotal(order);
    Money tax = calculateTax(subtotal);         // 격리됨!
    Money shipping = calculateShipping(order);
    return subtotal.plus(tax).plus(shipping);
}

private Money calculateTax(Money subtotal) {
    return subtotal.times(0.08);
}
```

이제 `calculateTax()`만 독립적으로 변경하고 테스트할 수 있다:

```java
// 2단계: 격리된 부분을 안전하게 변경
private Money calculateTax(Money subtotal) {
    return taxPolicy.calculate(subtotal);  // 정책 객체로 위임
}
```

### 3.4 왜 중요한가

| 격리 없이 변경 | 격리 후 변경 |
|---------------|-------------|
| 변경이 주변 코드에 영향을 줄 수 있다 | 변경 범위가 명확하다 |
| 테스트하기 어렵다 | 격리된 부분만 독립적으로 테스트 가능 |
| 실수 시 원인 파악이 어렵다 | 문제 발생 시 격리된 부분에 한정된다 |

> **핵심 통찰**: "변경하기 전에 변경을 쉽게 만들어라. (경고: 이것은 어려울 수 있다.) 그다음 쉬운 변경을 하라." — Kent Beck. Isolate Change는 "변경을 쉽게 만드는" 첫 번째 단계다.

---

## 4. Migrate Data (데이터 이주)

### 4.1 정의

**한 표현(representation)에서 다른 표현으로 점진적으로 전환한다.** 두 표현을 일시적으로 공존시키면서 안전하게 이주한다.

### 4.2 적용 시점

데이터의 내부 표현을 바꿔야 할 때 사용한다. 한 번에 바꾸면 연쇄적으로 많은 코드가 깨질 수 있으므로, 점진적으로 이주한다.

### 4.3 Part I에서의 사례: currency 도입

Part I에서 `Dollar`와 `Franc`를 구분하는 방식을 클래스 타입에서 `currency` 문자열로 전환할 때 이 기법을 사용했다:

```java
// 1단계: 새 표현 추가 (기존 표현 유지)
class Dollar extends Money {
    private String currency;  // 새 표현 추가

    Dollar(int amount) {
        this.amount = amount;
        this.currency = "USD";  // 새 표현에 값 설정
    }
}

// 2단계: 새 표현을 사용하는 코드 추가
class Money {
    String currency() {
        return currency;
    }
}

// 3단계: 기존 표현(클래스 타입)에 의존하는 코드를 새 표현(currency)으로 교체
// 기존: instanceof Dollar
// 변경: currency.equals("USD")

// 4단계: 기존 표현 제거 (Dollar, Franc 클래스 제거)
```

### 4.4 단계

1. 새로운 표현을 추가한다 (기존 표현은 그대로 둔다)
2. 새로운 표현에 올바른 값을 설정한다
3. 기존 표현을 사용하는 코드를 하나씩 새 표현으로 전환한다 (각 단계마다 테스트)
4. 기존 표현을 제거한다

> **핵심 통찰**: Migrate Data의 핵심은 "두 표현의 공존 기간"이다. 이 기간 동안 두 표현이 항상 동기화되어야 한다. 한 번에 전환하면 빠르게 느껴질 수 있지만, 실패했을 때 원인을 찾기 어렵다. 점진적 이주는 느려 보이지만 각 단계가 안전하다.

---

## 5. Extract Method (메서드 추출)

### 5.1 정의

**코드의 일부를 별도의 메서드로 분리하고, 원래 위치에서 새 메서드를 호출한다.**

### 5.2 적용 시점

- 메서드가 너무 길 때
- 코드 블록에 주석이 필요할 때 (주석 대신 메서드 이름으로 의도 표현)
- 같은 코드가 반복될 때
- Isolate Change의 첫 단계로

### 5.3 예시

```java
// 추출 전
public void printReport(Order order) {
    // 헤더 출력
    System.out.println("===================");
    System.out.println("주문 보고서");
    System.out.println("날짜: " + order.getDate());
    System.out.println("===================");

    // 항목 출력
    for (Item item : order.getItems()) {
        System.out.println(item.name() + ": " + item.price());
    }

    // 합계 출력
    Money total = Money.zero();
    for (Item item : order.getItems()) {
        total = total.plus(item.price());
    }
    System.out.println("합계: " + total);
}
```

```java
// 추출 후
public void printReport(Order order) {
    printHeader(order);
    printItems(order);
    printTotal(order);
}

private void printHeader(Order order) {
    System.out.println("===================");
    System.out.println("주문 보고서");
    System.out.println("날짜: " + order.getDate());
    System.out.println("===================");
}

private void printItems(Order order) {
    for (Item item : order.getItems()) {
        System.out.println(item.name() + ": " + item.price());
    }
}

private Money calculateTotal(Order order) {
    Money total = Money.zero();
    for (Item item : order.getItems()) {
        total = total.plus(item.price());
    }
    return total;
}

private void printTotal(Order order) {
    System.out.println("합계: " + calculateTotal(order));
}
```

### 5.4 TDD에서의 빈도

Extract Method는 TDD에서 **가장 자주 사용하는 리팩토링**이다. Green을 만든 후 "이 코드를 이해하기 쉽게 만들려면?"이라고 생각하면 대부분 Extract Method가 답이다.

> **핵심 통찰**: 좋은 메서드 이름은 주석을 대체한다. `// 합계를 계산한다`라는 주석을 다는 대신 `calculateTotal()`이라는 메서드를 만들면, 코드가 스스로 설명하게 된다. Extract Method는 코드의 "무엇을"과 "어떻게"를 분리하는 가장 기본적인 도구다.

---

## 6. Inline Method (메서드 인라인)

### 6.1 정의

**메서드 호출을 메서드의 본문으로 대체한다.** Extract Method의 역연산이다.

### 6.2 적용 시점

- 메서드 본문이 메서드 이름만큼이나 명확할 때
- 잘못된 추상화를 해체할 때
- 메서드를 재구성하기 전에 한 곳으로 모을 때

### 6.3 예시

```java
// 인라인 전 — 메서드가 오히려 가독성을 해친다
class Account {
    boolean isOverdrawn() {
        return !isPositiveBalance();
    }

    boolean isPositiveBalance() {
        return balance > 0;
    }
}

// 인라인 후 — 더 명확하다
class Account {
    boolean isOverdrawn() {
        return balance <= 0;
    }
}
```

### 6.4 TDD에서의 맥락

Inline Method는 "리팩토링을 위한 리팩토링"으로 자주 사용된다. 여러 메서드에 분산된 로직을 한 곳으로 모은 다음, 다시 더 나은 구조로 Extract하는 중간 단계로 활용한다:

```
Extract (나쁜 분리) → Inline (한 곳으로 모음) → Extract (좋은 분리)
```

> **핵심 통찰**: Inline Method는 "추상화를 되돌리는" 능력이다. 모든 추상화가 좋은 것은 아니다. 잘못된 추상화는 코드를 더 이해하기 어렵게 만든다. Inline Method로 추상화를 해체한 후, 더 나은 방향으로 다시 추상화할 수 있다.

---

## 7. Extract Interface (인터페이스 추출)

### 7.1 정의

**구체 클래스에서 인터페이스를 추출하여, 클라이언트가 구체 클래스 대신 인터페이스에 의존하도록 한다.**

### 7.2 적용 시점

- 두 번째 구현이 필요해질 때 (Imposter를 도입하고 싶을 때)
- 테스트에서 Mock/Stub을 사용하고 싶을 때
- 구체 클래스에 대한 의존성을 줄이고 싶을 때

### 7.3 Part I에서의 사례

`Expression` 인터페이스는 `Money` 클래스에서 추출되었다:

```java
// 추출 전: Money만 있는 상태
class Money {
    Money reduce(Bank bank, String to) { ... }
    Expression plus(Money addend) { ... }
    Money times(int multiplier) { ... }
}

// Sum이 필요해짐 → 공통 인터페이스 추출
interface Expression {
    Money reduce(Bank bank, String to);
    Expression plus(Expression addend);
    Expression times(int multiplier);
}

class Money implements Expression { ... }
class Sum implements Expression { ... }
```

### 7.4 단계

1. 구체 클래스의 메서드 중 공개해야 할 메서드를 식별한다
2. 인터페이스를 선언하고 해당 메서드 시그니처를 넣는다
3. 구체 클래스가 인터페이스를 구현하도록 선언한다
4. 클라이언트가 구체 클래스 대신 인터페이스를 참조하도록 변경한다

> **핵심 통찰**: TDD에서 인터페이스는 "두 번째 구현이 필요할 때" 추출한다. 미리 인터페이스를 만들지 않는다. "지금은 구현이 하나뿐이니 구체 클래스를 직접 사용하고, 나중에 두 번째 구현이 필요하면 그때 인터페이스를 추출하면 된다"는 것이 TDD의 접근 방식이다.

---

## 8. Move Method (메서드 이동)

### 8.1 정의

**메서드를 그것이 속해야 할 클래스로 이동한다.** 메서드가 자신이 속한 클래스보다 다른 클래스의 데이터를 더 많이 사용한다면, 그 클래스로 옮기는 것이 자연스럽다.

### 8.2 적용 시점

Kent Beck은 메서드 이동의 신호로 **Feature Envy**(기능 질투)를 든다:

```java
// Feature Envy — Printer가 Order의 내부를 너무 많이 들여다본다
class Printer {
    String formatOrder(Order order) {
        return order.getCustomerName() + ": "
            + order.getItems().size() + " items, "
            + order.getTotal() + " total";
    }
}
```

이 메서드는 `Order`의 데이터만 사용한다. `Order`로 이동하는 것이 자연스럽다:

```java
// Move Method 후
class Order {
    String format() {
        return customerName + ": "
            + items.size() + " items, "
            + total + " total";
    }
}
```

### 8.3 TDD에서의 맥락

TDD에서 Move Method는 "코드를 작성하고 보니 이 메서드의 위치가 적절하지 않다"는 깨달음에서 시작된다. Green을 만든 후 리팩토링 단계에서 수행한다.

> **핵심 통찰**: 메서드는 자신이 사용하는 데이터 가까이에 있어야 한다. 데이터와 그 데이터를 조작하는 로직이 떨어져 있으면, 변경할 때 여러 파일을 동시에 수정해야 하는 상황이 생긴다. Move Method로 데이터와 행위를 함께 놓으면 변경이 국소화된다.

---

## 9. Method Object (메서드 객체)

### 9.1 정의

**복잡한 메서드를 별도의 클래스로 전환한다.** 메서드의 매개변수와 지역 변수가 새 클래스의 필드가 되고, 메서드 본문이 새 클래스의 메서드가 된다.

### 9.2 적용 시점

메서드가 너무 복잡해서 Extract Method만으로는 정리할 수 없을 때 사용한다. 특히 많은 지역 변수와 매개변수가 서로 얽혀 있어 일부를 추출하기 어려운 경우에 유용하다.

### 9.3 예시

```java
// 복잡한 메서드 — 많은 지역 변수와 매개변수
class Order {
    Money calculatePrice(
            List<Item> items, Customer customer,
            DiscountPolicy discount, TaxPolicy tax) {
        Money basePrice = Money.zero();
        Money itemDiscount = Money.zero();
        Money memberDiscount = Money.zero();
        // ... 수십 줄의 복잡한 계산 로직
        // basePrice, itemDiscount, memberDiscount가
        // 서로 의존하여 Extract Method가 어렵다
    }
}
```

```java
// Method Object로 전환
class PriceCalculator {
    // 매개변수 → 필드
    private List<Item> items;
    private Customer customer;
    private DiscountPolicy discount;
    private TaxPolicy tax;

    // 지역 변수 → 필드
    private Money basePrice;
    private Money itemDiscount;
    private Money memberDiscount;

    PriceCalculator(List<Item> items, Customer customer,
                    DiscountPolicy discount, TaxPolicy tax) {
        this.items = items;
        this.customer = customer;
        this.discount = discount;
        this.tax = tax;
    }

    Money calculate() {
        computeBasePrice();
        computeItemDiscount();
        computeMemberDiscount();
        return applyTax();
    }

    // 이제 Extract Method가 쉽다 — 지역 변수가 필드이므로
    private void computeBasePrice() { ... }
    private void computeItemDiscount() { ... }
    private void computeMemberDiscount() { ... }
    private Money applyTax() { ... }
}

// 원래 클래스에서는 위임
class Order {
    Money calculatePrice(List<Item> items, Customer customer,
                         DiscountPolicy discount, TaxPolicy tax) {
        return new PriceCalculator(items, customer, discount, tax)
                .calculate();
    }
}
```

### 9.4 TDD에서의 단계

1. 새 클래스를 만든다
2. 원래 메서드의 매개변수와 지역 변수를 필드로 선언한다
3. 원래 메서드의 본문을 새 클래스의 메서드로 복사한다
4. 원래 메서드에서 새 클래스를 생성하고 위임한다
5. 테스트 실행 → 통과 확인
6. 이제 새 클래스 내에서 자유롭게 Extract Method 등 리팩토링 수행

> **핵심 통찰**: Method Object는 "복잡한 메서드를 해체하기 위한 발판"이다. 직접적인 목적은 코드를 더 깔끔하게 만드는 것이지만, 진짜 가치는 이후의 리팩토링을 가능하게 만드는 것에 있다. 지역 변수가 필드가 되면 Extract Method의 장벽이 사라진다.

---

## 10. Add Parameter (매개변수 추가)

### 10.1 정의

**메서드가 추가 정보를 필요로 할 때, 매개변수를 추가한다.**

### 10.2 TDD에서의 맥락

TDD에서 새 테스트를 작성할 때 기존 메서드에 정보가 부족하면 매개변수를 추가한다. 이것은 가장 단순한 리팩토링이지만, 주의가 필요하다.

```java
// 기존 테스트와 코드
public void testMultiplication() {
    Dollar five = new Dollar(5);
    assertEquals(new Dollar(10), five.times(2));
}

// 새 요구사항: 통화 정보가 필요해짐
public void testMultiplicationWithCurrency() {
    Money five = new Money(5, "USD");  // 매개변수 추가
    assertEquals(new Money(10, "USD"), five.times(2));
}
```

### 10.3 주의사항

매개변수가 계속 늘어나면 설계에 문제가 있다는 신호다:

```java
// 매개변수가 너무 많은 메서드 — 나쁜 신호
Money calculate(int amount, String currency, double rate,
                boolean taxIncluded, String discountCode,
                Date validUntil, Customer customer) { ... }
```

이 경우 관련 매개변수들을 객체로 묶거나(Introduce Parameter Object), Method Parameter to Constructor Parameter를 적용하는 것을 고려한다.

> **핵심 통찰**: 매개변수 추가는 가장 쉬운 리팩토링이지만, 무분별한 추가는 메서드의 복잡도를 높인다. "이 매개변수가 정말 이 메서드에 필요한가?"를 항상 질문해야 한다.

---

## 11. Method Parameter to Constructor Parameter (메서드 매개변수를 생성자 매개변수로)

### 11.1 정의

**같은 매개변수가 여러 메서드에 반복적으로 전달되면, 생성자에서 한 번만 받아 필드에 저장한다.**

### 11.2 예시

```java
// 리팩토링 전: 같은 매개변수가 반복된다
class Converter {
    Money convert(Money amount, String targetCurrency, Bank bank) {
        double rate = bank.getRate(amount.currency(), targetCurrency);
        return new Money(amount.amount() * rate, targetCurrency);
    }

    Money[] convertAll(Money[] amounts, String targetCurrency, Bank bank) {
        Money[] results = new Money[amounts.length];
        for (int i = 0; i < amounts.length; i++) {
            results[i] = convert(amounts[i], targetCurrency, bank);
        }
        return results;
    }
}

// 사용
converter.convert(fiveDollars, "CHF", bank);
converter.convertAll(portfolio, "CHF", bank);
```

`targetCurrency`와 `bank`가 매번 반복된다.

```java
// 리팩토링 후: 생성자로 이동
class Converter {
    private String targetCurrency;
    private Bank bank;

    Converter(String targetCurrency, Bank bank) {
        this.targetCurrency = targetCurrency;
        this.bank = bank;
    }

    Money convert(Money amount) {
        double rate = bank.getRate(amount.currency(), targetCurrency);
        return new Money(amount.amount() * rate, targetCurrency);
    }

    Money[] convertAll(Money[] amounts) {
        Money[] results = new Money[amounts.length];
        for (int i = 0; i < amounts.length; i++) {
            results[i] = convert(amounts[i]);
        }
        return results;
    }
}

// 사용 — 훨씬 깔끔하다
Converter converter = new Converter("CHF", bank);
converter.convert(fiveDollars);
converter.convertAll(portfolio);
```

### 11.3 TDD에서의 등장

이 리팩토링은 테스트 코드에서 먼저 불편함을 느낄 때 등장한다:

```java
// 테스트에서 같은 매개변수가 반복되어 불편하다
public void testSingleConversion() {
    converter.convert(fiveDollars, "CHF", bank);  // bank가 반복
}
public void testMultipleConversion() {
    converter.convertAll(portfolio, "CHF", bank);  // bank가 반복
}
```

fixture에 `bank`를 넣어도 메서드 호출마다 전달해야 하는 것은 변하지 않는다. 이때 생성자로 이동하면 깔끔해진다.

> **핵심 통찰**: "같은 매개변수를 세 번 이상 전달하고 있다면" 생성자로 옮기는 것을 고려하라. 이것은 단순한 코드 정리를 넘어, 객체가 **무엇에 대한 것인지**(identity)를 명확히 하는 효과도 있다. `Converter`가 `bank`와 `targetCurrency`를 가지면, "특정 은행의 특정 통화 변환기"라는 정체성이 생긴다.

---

## 12. 리팩토링 패턴의 관계와 적용 순서

리팩토링들은 단독으로 적용되기보다 순서를 가지고 결합되는 경우가 많다:

```
일반적인 리팩토링 흐름:

[복잡한 코드 발견]
    ↓
Isolate Change (변경할 부분 격리)
    ↓
Extract Method (메서드로 분리)
    ↓
Move Method (적절한 클래스로 이동)
    ↓
Reconcile Differences (유사 코드 통합)
    ↓
Extract Interface (인터페이스 추출)
```

```
데이터 표현 변경 흐름:

[새로운 표현이 필요]
    ↓
Add Parameter (새 표현을 매개변수로 추가)
    ↓
Migrate Data (기존 표현을 새 표현으로 교체)
    ↓
Method Parameter to Constructor Parameter (반복되는 매개변수 정리)
```

```
복잡한 메서드 해체 흐름:

[Extract Method가 어려운 복잡한 메서드]
    ↓
Method Object (별도 클래스로 전환)
    ↓
Extract Method (이제 쉽게 추출 가능)
    ↓
Inline Method (불필요한 중간 메서드 제거)
```

---

## 요약

- **Reconcile Differences**는 유사한 코드를 동일하게 만든 후 통합한다. Dollar/Franc 통합이 대표적이다.
- **Isolate Change**는 변경 대상을 나머지 코드로부터 분리한다. 안전한 변경의 첫 단계다.
- **Migrate Data**는 데이터 표현을 점진적으로 전환한다. 두 표현을 일시적으로 공존시키는 것이 핵심이다.
- **Extract Method**는 TDD에서 가장 자주 사용하는 리팩토링이다. 코드의 의도를 메서드 이름으로 표현한다.
- **Inline Method**는 Extract Method의 역연산으로, 잘못된 추상화를 해체하거나 재구성을 위한 중간 단계로 사용한다.
- **Extract Interface**는 두 번째 구현이 필요할 때 추출한다. 미리 만들지 않는 것이 TDD의 접근이다.
- **Move Method**는 메서드를 그것이 사용하는 데이터 가까이로 이동시킨다.
- **Method Object**는 복잡한 메서드를 클래스로 전환하여 이후 리팩토링을 가능하게 한다.
- **Add Parameter**는 메서드에 정보를 추가하지만, 남용하면 복잡도가 증가한다.
- **Method Parameter to Constructor Parameter**는 반복되는 매개변수를 생성자로 올려 객체의 정체성을 명확히 한다.
- 모든 리팩토링은 **테스트가 통과하는 상태에서** 수행하며, 각 단계마다 테스트를 실행하여 확인한다.

---

## 다른 챕터와의 관계

- **Chapter 1~17 (Part I: Money Example)**: 이 챕터의 거의 모든 리팩토링이 Part I에서 실전으로 사용되었다. 특히 Reconcile Differences(Dollar/Franc 통합), Migrate Data(currency 도입), Factory Method(Money.dollar()), Extract Interface(Expression) 등이 핵심적이었다.
- **Chapter 28 (Green Bar Patterns)**: Green을 만드는 패턴과 리팩토링 패턴은 TDD 사이클의 두 축이다. Green Bar 패턴으로 동작하는 코드를 만들고, 이 챕터의 패턴으로 깨끗한 코드로 만든다.
- **Chapter 30 (Design Patterns)**: 설계 패턴은 리팩토링의 "목적지"다. Reconcile Differences → Template Method, Extract Interface → Pluggable Object 등, 리팩토링을 적용하면 설계 패턴이 자연스럽게 등장한다.
- **Chapter 32 (Mastering TDD)**: 32장에서 다루는 "TDD가 어떻게 좋은 설계로 이어지는가?"에 대한 구체적 답이 이 챕터의 리팩토링 기법들이다. 작은 리팩토링의 축적이 좋은 설계를 만든다.
