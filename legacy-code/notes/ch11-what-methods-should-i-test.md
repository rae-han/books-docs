# Chapter 11: 코드를 변경해야 한다 (I Need to Make a Change. What Methods Should I Test?)

## 핵심 질문

코드를 변경해야 할 때, 그 변경의 영향 범위를 어떻게 파악하고, 어디에 테스트를 작성해야 가장 효과적으로 변경을 보호할 수 있는가?

---

## 1. Effect Reasoning (영향 추론)

코드를 변경하기 전에, 그 변경이 시스템의 다른 부분에 어떤 영향을 미치는지 이해해야 한다. 이것을 **Effect Reasoning(영향 추론)** 이라 한다. 영향 추론은 "이 코드를 바꾸면 어디가 달라지는가?"라는 질문에 답하는 과정이다.

레거시 코드에서 영향 추론이 중요한 이유:

- 테스트가 없는 코드에서는 변경의 영향을 자동으로 감지할 방법이 없다
- 모든 곳에 테스트를 작성할 시간이 없으므로, **가장 효과적인 지점**을 골라야 한다
- 영향 범위를 잘못 추정하면 예상치 못한 버그가 발생한다

### 1.1 영향 추론의 기본 원리

어떤 코드 조각의 영향을 추론하려면, 해당 코드가 **변경하는 것**과 그 변경이 **전파되는 경로**를 추적해야 한다. 이를 위해 다음 질문들을 던진다:

1. 이 메서드가 어떤 값을 반환하는가? 그 반환값을 누가 사용하는가?
2. 이 메서드가 어떤 객체의 상태를 변경하는가? 그 객체를 누가 참조하는가?
3. 이 메서드가 전역 상태나 정적 상태를 변경하는가?

---

## 2. Effect Propagation (영향 전파)

영향은 여러 경로를 통해 전파된다. Feathers는 네 가지 주요 전파 경로를 식별한다.

### 2.1 반환값을 통한 전파 (Return Value Propagation)

가장 추적하기 쉬운 형태의 전파다. 메서드가 값을 반환하면, 그 값을 사용하는 모든 곳이 영향 범위에 들어간다.

```java
public class PriceCalculator {
    private double basePrice;
    private double taxRate;

    public double getTotal() {
        return basePrice + (basePrice * taxRate);  // ← 반환값
    }
}

// getTotal()의 반환값을 사용하는 곳
public class Invoice {
    private PriceCalculator calculator;

    public String format() {
        double total = calculator.getTotal();  // ← 여기가 영향 받음
        return "Total: $" + total;
    }
}
```

`getTotal()`의 계산 로직을 변경하면, `Invoice.format()`도 영향을 받는다. 반환값 전파를 추적하려면 **호출자(caller)를 찾아 올라가면** 된다.

### 2.2 매개변수 수정을 통한 전파 (Parameter Modification Propagation)

메서드가 전달받은 매개변수 객체의 상태를 변경하는 경우, 호출자가 보유한 해당 객체를 통해 영향이 전파된다.

```java
public class OrderProcessor {
    public void applyDiscount(Order order, double discountRate) {
        double discount = order.getTotal() * discountRate;
        order.setDiscount(discount);  // ← 매개변수 객체의 상태 변경
        order.setTotal(order.getTotal() - discount);  // ← 매개변수 객체의 상태 변경
    }
}

// 호출하는 쪽
public class CheckoutService {
    public void checkout(Order order) {
        processor.applyDiscount(order, 0.1);
        // 이 시점에서 order의 상태가 변경되어 있음
        receipt.print(order);  // ← 영향 받음
        database.save(order);  // ← 영향 받음
    }
}
```

`applyDiscount`가 `order` 매개변수의 상태를 변경하므로, 이후 `order`를 사용하는 `receipt.print()`과 `database.save()` 모두 영향을 받는다. 이 전파 경로는 반환값 전파보다 추적이 어려울 수 있다.

### 2.3 전역 변수/정적 변수 수정을 통한 전파 (Global/Static Variable Propagation)

가장 추적하기 어렵고 위험한 형태의 전파다. 전역 상태를 변경하면, 해당 전역 상태를 읽는 시스템의 **모든 부분**이 잠재적 영향 범위가 된다.

```java
public class Configuration {
    private static String locale = "en_US";

    public static void setLocale(String newLocale) {
        locale = newLocale;  // ← 전역 정적 변수 수정
    }

    public static String getLocale() {
        return locale;
    }
}

// 이 전역 상태를 읽는 곳 - 어디서든 영향 받을 수 있음
public class MessageFormatter {
    public String format(String key) {
        String locale = Configuration.getLocale();  // ← 영향 받음
        return ResourceBundle.getBundle("messages", locale).getString(key);
    }
}

public class CurrencyFormatter {
    public String format(double amount) {
        String locale = Configuration.getLocale();  // ← 영향 받음
        return NumberFormat.getCurrencyInstance(new Locale(locale)).format(amount);
    }
}
```

`Configuration.setLocale()`을 호출하면 `MessageFormatter`와 `CurrencyFormatter`는 물론, `Configuration.getLocale()`을 호출하는 **모든 클래스**가 영향을 받는다.

> 전역 변수를 통한 영향 전파는 코드의 어디서든 발생할 수 있기 때문에, 영향 범위를 한정하기 매우 어렵다. 이것이 전역 상태가 위험한 핵심 이유 중 하나다.

### 2.4 멤버 변수 수정을 통한 전파 (Member Variable Propagation)

메서드가 자신이 속한 클래스의 멤버 변수(인스턴스 변수)를 변경하면, 해당 멤버 변수를 사용하는 같은 클래스의 다른 메서드들이 영향을 받는다.

```java
public class ShoppingCart {
    private List<Item> items = new ArrayList<>();
    private double totalPrice = 0;

    public void addItem(Item item) {
        items.add(item);                       // ← 멤버 변수 수정
        totalPrice += item.getPrice();         // ← 멤버 변수 수정
    }

    public double getTotalPrice() {
        return totalPrice;                     // ← 영향 받음
    }

    public int getItemCount() {
        return items.size();                   // ← 영향 받음
    }

    public List<Item> getItems() {
        return Collections.unmodifiableList(items);  // ← 영향 받음
    }
}
```

`addItem()`이 `items`와 `totalPrice`를 수정하므로, `getTotalPrice()`, `getItemCount()`, `getItems()` 모두 영향을 받는다. 그리고 이 메서드들의 반환값을 사용하는 외부 코드로 영향이 다시 전파된다.

### 2.5 영향 전파 규칙 정리

| 전파 경로 | 추적 난이도 | 영향 범위 |
|-----------|-------------|-----------|
| 반환값 | 쉬움 | 호출자와 그 호출자의 호출자 |
| 매개변수 수정 | 중간 | 매개변수 객체를 참조하는 모든 코드 |
| 멤버 변수 수정 | 중간 | 같은 객체의 다른 메서드 + 그 메서드의 호출자 |
| 전역/정적 변수 수정 | 어려움 | 해당 전역 상태를 읽는 모든 코드 |

---

## 3. Effect Sketch (영향 스케치)

### 3.1 영향 스케치란?

영향 스케치는 변경이 미치는 영향을 **시각적으로** 표현하는 다이어그램이다. 변수, 메서드, 반환값 사이의 영향 관계를 화살표로 나타내어, 변경의 파급 범위를 한눈에 파악할 수 있게 한다.

화살표의 의미: A → B는 "A가 변경되면 B에 영향을 미친다"는 뜻이다.

### 3.2 영향 스케치 그리는 방법

다음 예시 코드에 대해 영향 스케치를 그려보자:

```java
public class Employee {
    private String name;
    private double salary;
    private Department department;

    public void promote(double raiseAmount) {
        salary += raiseAmount;
    }

    public double getSalary() {
        return salary;
    }

    public String getTaxReport() {
        return name + ": $" + getSalary() + " (Dept: " + department.getName() + ")";
    }

    public double calculateDepartmentBudgetImpact() {
        return department.getTotalBudget() - getSalary();
    }
}
```

`promote()` 메서드를 변경한다고 할 때의 영향 스케치:

```
promote()
  │
  ├──→ salary (멤버 변수 수정)
  │      │
  │      ├──→ getSalary() (salary를 읽음)
  │      │       │
  │      │       ├──→ getTaxReport() (getSalary() 호출)
  │      │       │       │
  │      │       │       └──→ getTaxReport()의 호출자들
  │      │       │
  │      │       └──→ calculateDepartmentBudgetImpact() (getSalary() 호출)
  │      │               │
  │      │               └──→ 이 메서드의 호출자들
  │      │
  │      └──→ (salary를 직접 읽는 다른 메서드가 있다면)
  │
  └──→ promote()의 반환값 (void이므로 해당 없음)
```

### 3.3 영향 스케치의 실용적 가치

영향 스케치를 그리면:

1. **테스트를 어디에 작성해야 하는지** 명확해진다 (영향의 끝점)
2. **변경이 예상보다 넓은 범위에 영향을 미치는지** 파악할 수 있다
3. **Interception Point(차단 지점)** 와 **Pinch Point(병목 지점)** 를 찾을 수 있다 (이것이 핵심)

> 영향 스케치를 종이에 직접 그려볼 필요는 없다. 중요한 것은 이러한 사고 방식을 머릿속에서 수행하는 것이다. 하지만 복잡한 코드에서는 실제로 그려보는 것이 큰 도움이 된다.

---

## 4. 영향 전파 규칙과 주의점

### 4.1 영향 전파의 연쇄 (Chaining)

영향은 여러 단계에 걸쳐 연쇄적으로 전파될 수 있다:

```
메서드 A가 멤버 변수 x를 수정
  → 메서드 B가 x를 읽어서 반환
    → 메서드 C가 B의 반환값을 사용하여 매개변수 obj를 수정
      → 메서드 D가 obj를 읽어서 전역 변수를 수정
        → ...
```

이론적으로는 영향이 무한히 전파될 수 있지만, 실무에서는 보통 몇 단계 안에서 영향 범위가 좁혀진다.

### 4.2 주의점: 과도한 영향 추적의 함정

영향 추적을 너무 깊이 파고들면 시스템 전체가 영향 범위에 들어가 버린다. 이것은 비현실적이다. 실용적 관점에서:

- **변경 지점에서 가까운 영향**에 집중한다
- **가장 가능성 높은 전파 경로**를 우선 추적한다
- 전역 상태를 통한 전파는 특별히 주의한다
- 완벽한 분석보다는 **충분히 좋은 분석**을 목표로 한다

### 4.3 주의점: 슈퍼클래스와 인터페이스

다형성(polymorphism)이 있을 때 영향 추적이 복잡해진다:

```java
public void process(Validator validator) {
    if (validator.isValid(data)) {  // ← 어떤 구현체의 isValid?
        // ...
    }
}
```

`Validator`가 인터페이스이고 여러 구현체가 있다면, 어떤 구현체가 실행될지 런타임에 결정된다. 영향 추적 시 **모든 가능한 구현체**를 고려해야 할 수 있다.

---

## 5. Characterization Testing의 기초적 언급

이 장에서 Feathers는 **Characterization Test(특성 테스트)** 라는 개념을 간략히 언급한다. 변경의 영향 범위를 파악한 후, 그 범위의 현재 동작을 기록하는 테스트를 작성하는 것이다. Characterization Test의 상세한 내용은 Chapter 13에서 본격적으로 다루지만, 여기서의 핵심은:

- 영향 범위를 파악한 후, 그 범위에 대한 **현재 동작을 기록하는 테스트**를 먼저 작성한다
- 이 테스트가 변경 중에 기존 동작이 깨지지 않았음을 보장하는 **안전망** 역할을 한다
- "올바른" 동작이 아니라 "현재" 동작을 기록하는 것이 핵심이다

---

## 6. 어디에 테스트를 작성할지 결정하는 전략

영향 스케치를 그리고 전파 경로를 파악했다면, 이제 **어디에 테스트를 작성할 것인가**를 결정해야 한다. 여기서 두 가지 핵심 개념이 등장한다.

### 6.1 Interception Point (차단 지점)

**Interception Point**는 변경의 영향을 **감지(sense)** 할 수 있는 지점이다. 즉, 테스트에서 값을 확인하거나 동작을 검증할 수 있는 장소다.

영향 스케치에서 영향이 전파되는 경로 위의 모든 지점이 잠재적 Interception Point다. 하지만 실용적으로 좋은 Interception Point는:

- **접근하기 쉬운** 지점 (public 메서드, 반환값이 있는 메서드)
- **변경과 가까운** 지점 (너무 멀리 떨어진 지점은 다른 요인의 영향도 받음)
- **의미가 명확한** 지점 (테스트가 무엇을 검증하는지 이해하기 쉬움)

```java
// 예: promote() 변경의 Interception Point 선택
// 방법 1: getSalary()에서 차단 - 변경과 가까움
@Test
public void testPromoteRaisesSalary() {
    Employee emp = new Employee("John", 50000, dept);
    emp.promote(5000);
    assertEquals(55000, emp.getSalary(), 0.01);  // ← Interception Point
}

// 방법 2: getTaxReport()에서 차단 - 변경과 멀지만 더 넓은 범위 커버
@Test
public void testPromoteAffectsTaxReport() {
    Employee emp = new Employee("John", 50000, dept);
    emp.promote(5000);
    assertTrue(emp.getTaxReport().contains("55000"));  // ← Interception Point
}
```

### 6.2 Pinch Point (병목 지점)

**Pinch Point**는 여러 영향 경로가 **하나로 모이는 좁은 지점**이다. 이 지점에서 테스트를 작성하면, **적은 수의 테스트로 많은 변경을 커버**할 수 있다.

영향 스케치에서 여러 화살표가 모이는 곳이 바로 Pinch Point다:

```
변경1 ──→ 메서드A ──┐
                     │
변경2 ──→ 메서드B ──┼──→ 메서드X ──→ ...
                     │
변경3 ──→ 메서드C ──┘
```

위에서 `메서드X`가 Pinch Point다. `메서드X`에 테스트를 작성하면 변경1, 변경2, 변경3의 영향을 모두 감지할 수 있다.

```java
// 예: 여러 변경이 총 가격 계산에 모이는 경우
public class ShoppingCart {
    public void addItem(Item item) { /* 변경 1 */ }
    public void applyDiscount(double rate) { /* 변경 2 */ }
    public void setShipping(double cost) { /* 변경 3 */ }

    // Pinch Point: 위의 세 변경이 모두 이 메서드에 영향을 미침
    public double getFinalTotal() {
        double subtotal = 0;
        for (Item item : items) {
            subtotal += item.getPrice();
        }
        subtotal -= subtotal * discountRate;
        subtotal += shippingCost;
        return subtotal;
    }
}

// Pinch Point에서 테스트하면 적은 수의 테스트로 넓은 범위를 커버
@Test
public void testFinalTotalIncludesAllFactors() {
    ShoppingCart cart = new ShoppingCart();
    cart.addItem(new Item("Widget", 100));
    cart.applyDiscount(0.1);
    cart.setShipping(5);
    assertEquals(95.0, cart.getFinalTotal(), 0.01);
}
```

### 6.3 좋은 Interception Point 선택의 Heuristic

1. **가능하면 Pinch Point를 찾아라**: 적은 테스트로 넓은 범위를 커버할 수 있다
2. **변경에 가까운 지점을 선호하라**: 멀리 떨어진 지점은 다른 요인의 영향을 받아 테스트가 불안정해질 수 있다
3. **반환값이 있는 메서드를 선호하라**: 값을 비교하는 것이 부수효과를 검증하는 것보다 쉽다
4. **public 메서드를 선호하라**: 접근이 쉽고 테스트 작성이 간단하다

---

## 요약

- **Effect Reasoning(영향 추론)** 은 코드 변경의 파급 범위를 파악하는 기법이다.
- 영향은 **반환값, 매개변수 수정, 멤버 변수 수정, 전역/정적 변수 수정**의 네 가지 경로를 통해 전파된다.
- **Effect Sketch(영향 스케치)** 를 그리면 변경의 영향 범위를 시각적으로 파악하고, 테스트 작성 위치를 결정할 수 있다.
- **Interception Point(차단 지점)** 는 영향을 감지할 수 있는 지점이며, 이 중 여러 영향이 모이는 **Pinch Point(병목 지점)** 를 찾으면 효율적으로 테스트를 작성할 수 있다.
- 완벽한 영향 분석보다는 **충분히 좋은 분석**을 지향하고, 가장 효과적인 지점에 테스트를 배치하는 것이 중요하다.
- Characterization Test를 사용하여 현재 동작을 기록하면 변경의 안전망을 확보할 수 있다.

---

## 다음 챕터와의 연결

Chapter 12 "클래스 의존 관계, 반드시 없애야 할까? (I Need to Make Many Changes in One Area)"에서는 **한 영역에서 여러 변경이 필요할 때** Pinch Point를 활용하여 모든 클래스에 개별 테스트를 작성하지 않고도 충분한 커버리지를 확보하는 전략을 심화하여 다룬다.
