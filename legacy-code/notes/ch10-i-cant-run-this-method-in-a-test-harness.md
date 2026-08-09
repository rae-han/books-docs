# Chapter 10: 테스트 하네스에서 이 메소드를 실행할 수 없다 (I Can't Run This Method in a Test Harness)

## 핵심 질문

테스트 하네스에서 특정 메서드를 실행할 수 없을 때, 어떤 장애물들이 존재하며 각각을 어떻게 극복할 수 있는가?

---

## 1. 메서드를 테스트에서 실행하기 어려운 이유들

Chapter 9에서는 클래스의 인스턴스를 테스트 하네스에 올리는 문제를 다루었다면, 이 장에서는 **개별 메서드를 테스트에서 실행하는 것이 어려운 상황**을 다룬다. 인스턴스를 생성할 수 있더라도 메서드를 직접 호출하여 테스트하는 데는 별도의 장벽이 존재한다.

메서드를 테스트 하네스에서 실행하기 어려운 주요 이유는 네 가지다:

| 장애물 | 설명 |
|--------|------|
| **메서드가 private** | 접근 제한자 때문에 테스트 코드에서 직접 호출할 수 없음 |
| **테스트하기 어려운 부수효과** | 메서드가 데이터베이스 기록, 네트워크 호출, UI 변경 등 검증하기 어려운 부수효과를 발생시킴 |
| **매개변수 생성의 어려움** | 메서드에 전달해야 하는 매개변수 객체를 테스트에서 쉽게 만들 수 없음 |
| **숨겨진 의존성** | 메서드 내부에서 직접 접근하거나 감지하기 어려운 객체에 의존함 |

이 장에서는 각 장애물에 대해 구체적인 해결 기법을 제시한다.

---

## 2. Private 메서드 테스트 전략

### 2.1 근본적인 질문: Private 메서드를 테스트해야 하는가?

Private 메서드를 테스트해야 할 필요성을 느낀다면, 먼저 한 발 물러서 생각해봐야 한다. 대부분의 경우 private 메서드는 public 메서드를 통해 간접적으로 테스트할 수 있다. Public 메서드가 private 메서드를 호출하므로, public 메서드에 대한 충분한 테스트가 있다면 private 메서드도 함께 검증된다.

하지만 실무에서는 private 메서드를 직접 테스트하고 싶은 유혹을 느끼는 상황이 있다:

- Private 메서드 안에 복잡한 로직이 있어 독립적으로 검증하고 싶을 때
- Public 메서드를 통한 간접 호출로는 특정 경로를 충분히 커버하기 어려울 때
- Private 메서드가 너무 많은 일을 하고 있을 때

### 2.2 핵심 원칙: 별도 클래스로의 이동 신호

> Private 메서드를 직접 테스트해야 한다고 느끼면, 그것은 그 메서드를 public으로 만들어야 할 **새로운 클래스**로 이동시켜야 한다는 신호다.

이것이 Feathers가 이 장에서 가장 강조하는 원칙이다. Private 메서드에 독립적으로 테스트해야 할 만큼 복잡한 로직이 있다면, 그것은 **클래스가 너무 많은 책임을 지고 있다**는 설계 문제의 징후다.

```java
// Before: 복잡한 private 메서드가 있는 클래스
public class ReportGenerator {
    public String generateReport(List<Sale> sales) {
        // ... 다른 로직 ...
        String formattedTable = formatSalesTable(sales);
        // ... 다른 로직 ...
        return result;
    }

    // 이 메서드를 직접 테스트하고 싶다면?
    private String formatSalesTable(List<Sale> sales) {
        // 복잡한 포맷팅 로직 (50줄 이상)
        // 다양한 경계 조건 처리
        // ...
    }
}
```

```java
// After: 별도 클래스로 추출
public class SalesTableFormatter {
    public String format(List<Sale> sales) {
        // 기존의 복잡한 포맷팅 로직
        // 이제 public이므로 직접 테스트 가능
    }
}

public class ReportGenerator {
    private SalesTableFormatter formatter = new SalesTableFormatter();

    public String generateReport(List<Sale> sales) {
        // ... 다른 로직 ...
        String formattedTable = formatter.format(sales);
        // ... 다른 로직 ...
        return result;
    }
}
```

이렇게 하면 `SalesTableFormatter`의 `format` 메서드를 독립적으로, 쉽게 테스트할 수 있다.

### 2.3 접근성 완화 (Relaxing Access)

하지만 현실적으로 클래스를 분리하는 것이 당장은 부담스러울 수 있다. 이럴 때 쓸 수 있는 **실용적 타협안**이 접근성 완화다.

**방법 1: protected로 변경**

```java
// private 대신 protected로 변경
protected String formatSalesTable(List<Sale> sales) { ... }
```

테스트 클래스에서 해당 클래스를 상속하면 protected 메서드에 접근할 수 있다:

```java
// 테스트용 서브클래스
public class TestableReportGenerator extends ReportGenerator {
    // protected 메서드에 접근 가능
}
```

**방법 2: package-private (default access)으로 변경 (Java)**

```java
// 접근 제한자를 제거하여 같은 패키지에서 접근 가능하게 함
String formatSalesTable(List<Sale> sales) { ... }
```

테스트 클래스를 같은 패키지에 배치하면 해당 메서드에 접근할 수 있다.

**방법 3: 리플렉션 사용 (최후의 수단)**

일부 언어에서는 리플렉션을 통해 private 메서드에 접근할 수 있다. 하지만 이 방법은 테스트가 깨지기 쉽고, 코드의 의도를 파악하기 어렵게 만들므로 최후의 수단으로만 사용해야 한다.

### 2.4 접근성 완화의 트레이드오프

접근성 완화는 캡슐화(encapsulation)를 약화시키는 대가가 있다. 하지만 Feathers는 다음과 같이 말한다:

> 테스트 가능성과 캡슐화 사이에서 선택해야 한다면, 테스트 가능성을 우선시하라. 테스트가 있으면 캡슐화 위반으로 인한 문제를 빠르게 감지할 수 있지만, 테스트 없이 캡슐화만 유지하면 코드가 어떻게 깨지고 있는지 알 수조차 없다.

접근성 완화는 일시적 조치여야 한다. 궁극적으로는 클래스를 분리하여 메서드를 자연스럽게 public으로 만드는 것이 올바른 방향이다.

---

## 3. 매개변수 문제 해결

메서드를 테스트하고 싶은데, 해당 메서드에 전달해야 하는 매개변수 객체를 테스트 환경에서 쉽게 생성할 수 없는 경우가 있다. 매개변수 타입이 복잡한 의존성을 가지거나, 생성자에서 무거운 초기화를 수행하거나, 특정 환경(데이터베이스, 네트워크 등)에 의존하는 경우가 대표적이다.

### 3.1 Extract Interface (인터페이스 추출)

가장 일반적이고 강력한 기법이다. 매개변수 타입에 대한 인터페이스를 추출하고, 테스트에서는 해당 인터페이스의 가짜(fake) 구현을 전달한다.

```java
// Before: HttpServletRequest는 직접 생성하기 매우 어렵다
public class PermissionChecker {
    public boolean hasPermission(HttpServletRequest request) {
        String userId = request.getParameter("userId");
        String resource = request.getParameter("resource");
        // ... 권한 확인 로직 ...
    }
}
```

`HttpServletRequest`는 서블릿 컨테이너가 생성하는 객체이므로 테스트에서 직접 만들기 어렵다. 인터페이스를 추출하면:

```java
// 필요한 메서드만 포함하는 인터페이스 추출
public interface ParameterSource {
    String getParameter(String name);
}

// 프로덕션 구현: HttpServletRequest를 감싸는 어댑터
public class ServletParameterSource implements ParameterSource {
    private HttpServletRequest request;

    public ServletParameterSource(HttpServletRequest request) {
        this.request = request;
    }

    public String getParameter(String name) {
        return request.getParameter(name);
    }
}

// 변경된 PermissionChecker
public class PermissionChecker {
    public boolean hasPermission(ParameterSource source) {
        String userId = source.getParameter("userId");
        String resource = source.getParameter("resource");
        // ... 권한 확인 로직 ...
    }
}
```

이제 테스트에서는 간단한 fake 구현을 만들 수 있다:

```java
// 테스트용 fake 구현
public class FakeParameterSource implements ParameterSource {
    private Map<String, String> params = new HashMap<>();

    public void addParameter(String name, String value) {
        params.put(name, value);
    }

    public String getParameter(String name) {
        return params.get(name);
    }
}

// 테스트
@Test
public void testAdminHasPermission() {
    FakeParameterSource source = new FakeParameterSource();
    source.addParameter("userId", "admin");
    source.addParameter("resource", "config");

    PermissionChecker checker = new PermissionChecker();
    assertTrue(checker.hasPermission(source));
}
```

### 3.2 Pass Null (null 전달)

때로는 매개변수를 아예 만들 필요가 없다. 테스트하려는 코드 경로에서 특정 매개변수를 사용하지 않는다면, 그냥 `null`을 전달하면 된다.

```java
// 이 메서드에서 command 매개변수는 특정 경로에서만 사용됨
public void processOrder(Order order, Command command) {
    if (order.isPriority()) {
        // command를 사용하지 않는 경로
        expediteOrder(order);
    } else {
        command.execute(order);
    }
}

// 우선 주문 처리 경로만 테스트할 때
@Test
public void testPriorityOrderIsExpedited() {
    Order priorityOrder = new Order();
    priorityOrder.setPriority(true);

    // command는 이 경로에서 사용되지 않으므로 null 전달
    processor.processOrder(priorityOrder, null);
    // ... assertions ...
}
```

Pass Null의 장점:

- **매우 빠르게** 테스트를 작성할 수 있다
- 인터페이스 추출 같은 리팩토링 없이 바로 적용 가능

Pass Null의 주의점:

- 해당 매개변수가 사용되지 않는다는 확신이 있어야 한다
- 만약 잘못 판단하면 `NullPointerException`이 발생하므로, 테스트 실행 시 바로 알 수 있다
- **null 안전한 언어(Kotlin, Swift 등)에서는 이 기법을 직접 적용하기 어려울 수 있다**

> Pass Null은 "빈약한(meager)" 기법처럼 보이지만, 레거시 코드에서 첫 테스트를 작성할 때 매우 실용적이다. 완벽한 테스트가 아니어도, 테스트가 없는 것보다는 훨씬 낫다.

### 3.3 Subclass and Override Method

매개변수 자체를 바꾸기 어렵지만, 매개변수와 관련된 동작을 우회하고 싶을 때 사용한다. 테스트 대상 클래스를 상속하여 문제가 되는 메서드만 오버라이드한다.

```java
public class AccountProcessor {
    public void processAccount(Account account, TaxCalculator calculator) {
        // calculator의 생성이 매우 복잡하다면?
        double tax = calculator.calculateTax(account.getBalance());
        account.debit(tax);
    }
}
```

만약 `TaxCalculator`의 생성이 어렵다면, 메서드를 추출하고 오버라이드할 수 있다:

```java
public class AccountProcessor {
    public void processAccount(Account account, TaxCalculator calculator) {
        double tax = getTax(calculator, account.getBalance());
        account.debit(tax);
    }

    // 추출된 메서드
    protected double getTax(TaxCalculator calculator, double balance) {
        return calculator.calculateTax(balance);
    }
}

// 테스트용 서브클래스
public class TestingAccountProcessor extends AccountProcessor {
    @Override
    protected double getTax(TaxCalculator calculator, double balance) {
        return balance * 0.1; // 고정된 세율 반환
    }
}
```

---

## 4. 부수효과 감지

메서드가 값을 반환하지 않고, 대신 데이터베이스에 기록하거나, 메일을 보내거나, 다른 시스템을 호출하는 등의 **부수효과(side effect)** 만 발생시키는 경우, 테스트에서 그 효과를 어떻게 감지(sense)할 것인가가 문제다.

### 4.1 Extract and Override Call

이 기법은 테스트하기 어려운 메서드 호출을 별도의 메서드로 추출한 뒤, 테스트에서 그 메서드를 오버라이드하여 부수효과를 제거하거나 감지할 수 있게 만드는 방법이다.

```java
// Before: sendEmail 호출이 테스트를 어렵게 만듦
public class OrderProcessor {
    public void processOrder(Order order) {
        // ... 주문 처리 로직 ...
        order.setStatus("PROCESSED");

        // 실제 이메일을 보내므로 테스트에서 실행하기 곤란
        EmailService.send(order.getCustomerEmail(),
                         "Your order has been processed",
                         buildConfirmationBody(order));

        // ... 후속 로직 ...
    }
}
```

**Step 1: 문제가 되는 호출을 별도 메서드로 추출**

```java
public class OrderProcessor {
    public void processOrder(Order order) {
        // ... 주문 처리 로직 ...
        order.setStatus("PROCESSED");

        sendConfirmationEmail(order);  // 추출된 메서드 호출

        // ... 후속 로직 ...
    }

    // 추출된 메서드
    protected void sendConfirmationEmail(Order order) {
        EmailService.send(order.getCustomerEmail(),
                         "Your order has been processed",
                         buildConfirmationBody(order));
    }
}
```

**Step 2: 테스트에서 오버라이드**

```java
// 테스트용 서브클래스
public class TestingOrderProcessor extends OrderProcessor {
    public boolean confirmationEmailSent = false;
    public String lastEmailRecipient = null;

    @Override
    protected void sendConfirmationEmail(Order order) {
        // 실제 이메일을 보내지 않고, 호출 사실만 기록
        confirmationEmailSent = true;
        lastEmailRecipient = order.getCustomerEmail();
    }
}

// 테스트
@Test
public void testProcessOrderSendsConfirmation() {
    TestingOrderProcessor processor = new TestingOrderProcessor();
    Order order = new Order("customer@example.com", /* ... */);

    processor.processOrder(order);

    assertTrue(processor.confirmationEmailSent);
    assertEquals("customer@example.com", processor.lastEmailRecipient);
}
```

이 기법의 핵심은 **프로덕션 코드의 구조 변경은 최소한으로 하면서(메서드 추출만), 테스트 가능성은 크게 높일 수 있다**는 점이다.

### 4.2 Extract and Override를 연쇄적으로 적용

하나의 메서드에 여러 부수효과가 있을 때, Extract and Override를 여러 번 적용할 수 있다:

```java
public class ReportService {
    public void generateMonthlyReport(int month) {
        List<Data> data = queryDatabase(month);
        String report = formatReport(data);
        writeToFileSystem(report);
        notifyStakeholders(report);
        updateAuditLog(month);
    }

    // 각각을 별도 protected 메서드로 추출
    protected List<Data> queryDatabase(int month) { /* ... */ }
    protected void writeToFileSystem(String report) { /* ... */ }
    protected void notifyStakeholders(String report) { /* ... */ }
    protected void updateAuditLog(int month) { /* ... */ }
}
```

테스트에서 필요한 것만 선택적으로 오버라이드할 수 있다.

### 4.3 Command/Query Separation (명령-질의 분리) 원칙

Feathers는 부수효과 문제를 논하면서 **Command/Query Separation(CQS)** 원칙을 언급한다. 이 원칙은 Bertrand Meyer가 제안한 것으로:

- **Query (질의)**: 값을 반환하지만 시스템의 상태를 변경하지 않는다
- **Command (명령)**: 시스템의 상태를 변경하지만 값을 반환하지 않는다

```java
// CQS를 따르지 않는 메서드 - 상태 변경과 값 반환을 동시에 함
public int processAndGetCount(Order order) {
    database.save(order);          // Command: 상태 변경
    emailService.send(order);       // Command: 부수효과
    return database.getOrderCount(); // Query: 값 반환
}
```

```java
// CQS를 따르는 분리
public void processOrder(Order order) {   // Command
    database.save(order);
    emailService.send(order);
}

public int getOrderCount() {              // Query
    return database.getOrderCount();
}
```

CQS를 따르면 테스트가 훨씬 쉬워진다:
- **Query는** 반환값만 확인하면 되므로 테스트가 간단하다
- **Command는** 상태 변경만 검증하면 되므로 관심사가 분리된다

> Command/Query Separation은 코드를 이해하기 쉽게 만들 뿐 아니라, 테스트하기도 훨씬 쉽게 만든다.

---

## 5. 숨겨진 의존성 문제

메서드 내부에서 전역 객체나 싱글턴에 접근하거나, `new` 키워드로 직접 의존 객체를 생성하는 경우, 외부에서 이를 대체할 수 없어 테스트가 어려워진다.

### 5.1 전역 참조와 싱글턴

```java
public class PricingEngine {
    public double calculatePrice(Item item) {
        // 싱글턴에 직접 접근 - 테스트에서 대체 불가
        double taxRate = TaxConfiguration.getInstance().getTaxRate();
        double discount = PromotionManager.getInstance().getDiscount(item);

        return item.getBasePrice() * (1 + taxRate) * (1 - discount);
    }
}
```

이 경우 **Parameterize Method (매개변수화)** 또는 **Introduce Instance Delegator (인스턴스 위임자 도입)** 기법을 사용할 수 있다.

**매개변수화:**

```java
public double calculatePrice(Item item, double taxRate, double discount) {
    return item.getBasePrice() * (1 + taxRate) * (1 - discount);
}
```

**인스턴스 위임자 도입:**

```java
public class PricingEngine {
    private TaxConfiguration taxConfig;
    private PromotionManager promoManager;

    public PricingEngine(TaxConfiguration taxConfig, PromotionManager promoManager) {
        this.taxConfig = taxConfig;
        this.promoManager = promoManager;
    }

    public double calculatePrice(Item item) {
        double taxRate = taxConfig.getTaxRate();
        double discount = promoManager.getDiscount(item);
        return item.getBasePrice() * (1 + taxRate) * (1 - discount);
    }
}
```

### 5.2 Extract and Override로 숨겨진 의존성 분리

```java
public class ShippingCalculator {
    public double calculateShipping(Order order) {
        // 내부에서 직접 생성하는 의존성
        DistanceService service = new DistanceService();
        double distance = service.getDistance(
            order.getWarehouseZip(), order.getDestinationZip());

        if (distance < 100) return 5.0;
        if (distance < 500) return 10.0;
        return 20.0;
    }
}

// Extract and Override 적용
public class ShippingCalculator {
    public double calculateShipping(Order order) {
        double distance = getDistance(
            order.getWarehouseZip(), order.getDestinationZip());

        if (distance < 100) return 5.0;
        if (distance < 500) return 10.0;
        return 20.0;
    }

    protected double getDistance(String fromZip, String toZip) {
        DistanceService service = new DistanceService();
        return service.getDistance(fromZip, toZip);
    }
}

// 테스트
public class TestingShippingCalculator extends ShippingCalculator {
    private double fixedDistance;

    public TestingShippingCalculator(double fixedDistance) {
        this.fixedDistance = fixedDistance;
    }

    @Override
    protected double getDistance(String fromZip, String toZip) {
        return fixedDistance;
    }
}

@Test
public void testShortDistanceShipping() {
    TestingShippingCalculator calc = new TestingShippingCalculator(50.0);
    Order order = new Order(/* ... */);
    assertEquals(5.0, calc.calculateShipping(order), 0.01);
}
```

---

## 6. 기법 선택 가이드

어떤 상황에서 어떤 기법을 사용할지 정리하면:

| 문제 상황 | 권장 기법 | 비고 |
|-----------|-----------|------|
| Private 메서드 테스트 필요 | 별도 클래스로 추출 | 장기적으로 가장 바람직 |
| Private 메서드 (빠른 해결) | 접근성 완화 (protected) | 임시 조치로 활용 |
| 매개변수 생성 어려움 | Extract Interface | 가짜 구현 전달 가능 |
| 매개변수가 사용되지 않음 | Pass Null | 가장 빠른 해결 |
| 부수효과 감지/제거 | Extract and Override Call | 프로덕션 코드 변경 최소화 |
| 부수효과 + 반환값 혼합 | Command/Query Separation | 설계 개선 효과도 있음 |
| 숨겨진 전역/싱글턴 의존성 | Parameterize Method | 의존성을 명시적으로 노출 |
| 내부 객체 생성 | Extract and Override | 생성 로직을 분리 |

---

## 요약

- 메서드를 테스트 하네스에서 실행하기 어려운 이유는 크게 네 가지다: private 접근 제한, 부수효과, 매개변수 생성 어려움, 숨겨진 의존성.
- **Private 메서드를 직접 테스트하고 싶다면**, 그것은 해당 로직이 별도 클래스로 분리되어야 한다는 신호다. 당장은 접근성 완화(protected, package-private)로 대응할 수 있지만, 궁극적으로는 클래스 분리가 올바른 방향이다.
- **매개변수 문제**에는 Extract Interface로 인터페이스를 추출하거나, 사용되지 않는 매개변수에는 Pass Null을 적용한다.
- **부수효과 문제**에는 Extract and Override Call로 문제가 되는 호출을 분리하고, Command/Query Separation 원칙으로 메서드의 책임을 명확히 한다.
- 테스트 가능성과 캡슐화 사이에서 트레이드오프가 있을 때, **테스트 가능성을 우선**시하라.
- 이 기법들은 완벽한 설계를 목표로 하는 것이 아니라, 레거시 코드에 **첫 테스트를 작성하기 위한 실용적 출발점**이다.

---

## 다음 챕터와의 연결

Chapter 11 "코드를 변경해야 한다 (I Need to Make a Change. What Methods Should I Test?)"에서는 변경을 해야 할 때 **어떤 메서드에 테스트를 작성해야 하는지** 판단하는 방법을 다룬다. 변경의 영향 범위를 추론하는 Effect Reasoning과 영향 스케치(Effect Sketch) 기법을 통해, 제한된 시간 안에 가장 효과적인 지점에 테스트를 배치하는 전략을 배운다.
