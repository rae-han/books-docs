# Chapter 20: 이 클래스는 너무 비대해서 더 이상 확장하고 싶지 않다 (This Class Is Too Big and I Don't Want It to Get Any Bigger)

## 핵심 질문

클래스가 너무 커져서 이해하기 어렵고 변경하기 두려울 때, 어떻게 하면 안전하게 클래스를 분해하고 각 부분의 책임을 명확하게 만들 수 있는가?

---

## 1. 거대한 클래스(God Class)의 문제점

소프트웨어 시스템이 성장하면서 특정 클래스가 점점 커지는 현상은 매우 흔하다. Feathers는 이런 거대한 클래스가 가진 문제를 다음과 같이 정리한다.

### 1.1 왜 클래스는 커지는가?

클래스가 비대해지는 이유는 여러 가지가 있다:

| 원인 | 설명 |
|------|------|
| **편의성** | 기존 클래스에 기능을 추가하는 것이 새 클래스를 만드는 것보다 쉽다 |
| **관련성의 착각** | "이 기능도 이 클래스와 관련이 있으니까" 라는 이유로 계속 추가 |
| **테스트 부재** | 테스트가 없어서 새 클래스를 추출하는 리팩토링이 두렵다 |
| **시간 압박** | 일정이 촉박하여 "일단 여기에 넣자"는 결정이 반복된다 |
| **지식 부족** | 단일 책임 원칙 등의 설계 원칙에 대한 인식이 부족하다 |

### 1.2 거대한 클래스의 구체적 문제

1. **이해하기 어렵다**: 수천 줄의 클래스에서 특정 기능이 어디에 있는지 찾기 어렵다. 클래스의 전체 동작을 머릿속에 담기 불가능하다.
2. **변경이 위험하다**: 한 기능을 변경했을 때 같은 클래스 내의 다른 기능에 의도치 않은 영향을 줄 수 있다. 인스턴스 변수를 여러 메서드가 공유하므로 변경의 파급 효과를 예측하기 어렵다.
3. **테스트가 어렵다**: 클래스가 너무 많은 의존성을 가지고 있어 테스트 하네스에 넣기 어렵다. 하나의 기능만 테스트하고 싶어도 클래스 전체를 인스턴스화해야 한다.
4. **재사용이 불가능하다**: 클래스의 일부 기능만 다른 곳에서 사용하고 싶어도, 클래스 전체가 따라온다.
5. **변경 충돌이 빈번하다**: 여러 개발자가 같은 클래스를 동시에 수정하면서 머지 충돌이 자주 발생한다.

> 클래스가 너무 크면 숨을 곳이 많다. 코드가 숨어 있으면 변경이 어렵고, 변경이 어려우면 더 나빠지기만 한다.

---

## 2. Single Responsibility Principle (SRP)

거대한 클래스 문제를 해결하는 핵심 원칙은 **단일 책임 원칙(Single Responsibility Principle, SRP)** 이다.

### 2.1 SRP의 정의

> **클래스는 변경의 이유(reason to change)가 하나만 있어야 한다.**

이것은 클래스가 "하나의 일만 해야 한다"는 것과는 미묘하게 다르다. "하나의 일"은 주관적이고 모호하지만, "변경의 이유"는 좀 더 구체적이다.

### 2.2 "변경의 이유"를 기준으로 책임 분리

예를 들어, 다음 클래스를 살펴보자:

```java
public class Employee {
    private String name;
    private String address;
    private double salary;
    private List<TimeCard> timeCards;

    // 급여 계산
    public double calculatePay() { ... }
    public void adjustSalary(double amount) { ... }

    // 시간 기록 관리
    public void addTimeCard(TimeCard card) { ... }
    public List<TimeCard> getTimeCards() { ... }

    // 보고서 생성
    public String generatePayStub() { ... }
    public String generateTaxReport() { ... }

    // 데이터베이스 저장
    public void save() { ... }
    public static Employee load(int id) { ... }
}
```

이 클래스에는 몇 가지 "변경의 이유"가 존재하는가?

| 변경의 이유 | 관련 메서드 | 변경 시나리오 |
|------------|------------|-------------|
| **급여 계산 규칙 변경** | `calculatePay()`, `adjustSalary()` | 세금 계산 방식 변경, 초과근무 수당 규칙 변경 |
| **시간 기록 방식 변경** | `addTimeCard()`, `getTimeCards()` | 출퇴근 기록 형식 변경, 원격 근무 추적 추가 |
| **보고서 형식 변경** | `generatePayStub()`, `generateTaxReport()` | 보고서 레이아웃 변경, 새로운 보고서 추가 |
| **데이터 저장 방식 변경** | `save()`, `load()` | DB 스키마 변경, ORM 도입, 다른 DB로 마이그레이션 |

최소 4가지 변경의 이유가 있다. SRP에 따르면 이 클래스는 4개의 클래스로 분리되어야 한다.

### 2.3 SRP 위반의 증상

- **클래스 설명에 "그리고(and)"가 들어간다**: "이 클래스는 급여를 계산하고, 시간 기록을 관리하고, 보고서를 생성한다."
- **메서드 그룹이 서로 다른 인스턴스 변수를 사용한다**: 급여 관련 메서드는 `salary`를, 보고서 관련 메서드는 형식 관련 필드를 주로 사용한다.
- **변경이 클래스의 한 부분에만 영향을 준다**: 보고서 형식을 바꾸는데 급여 계산 코드는 전혀 관련이 없다.

---

## 3. 거대 클래스에서 책임을 식별하는 기법들

클래스를 분리하려면 먼저 어떤 책임들이 섞여 있는지 식별해야 한다. Feathers는 다섯 가지 기법을 제시한다.

### 3.1 Method Grouping (메서드 그룹화)

가장 직관적인 방법이다. 클래스의 모든 메서드를 나열하고, 관련된 것끼리 그룹으로 묶는다.

#### 절차

1. 클래스의 모든 `public` 메서드를 나열한다.
2. 함께 사용되거나 관련된 메서드끼리 그룹을 만든다.
3. 각 그룹에 이름을 붙인다. 이 이름이 새 클래스의 후보가 된다.

#### 예시

```
RuleEngine 클래스의 메서드 목록:

[규칙 관리]
- addRule(Rule rule)
- removeRule(String ruleId)
- getRule(String ruleId)
- getAllRules()

[규칙 실행]
- evaluate(Context context)
- evaluateRule(String ruleId, Context context)

[규칙 검증]
- validateRule(Rule rule)
- validateAllRules()
- getValidationErrors()

[규칙 저장/로드]
- saveRules(String filename)
- loadRules(String filename)
- exportToXml()
- importFromXml(String xml)
```

이 그룹화에서 다음과 같은 클래스 후보가 도출된다:
- `RuleRepository`: 규칙 관리 + 저장/로드
- `RuleEvaluator`: 규칙 실행
- `RuleValidator`: 규칙 검증

> **핵심**: 그룹이 자연스럽게 만들어지면 그것은 분리해야 할 강한 신호다. 그룹화가 어렵고 메서드들이 얽혀 있다면, 더 깊은 분석이 필요하다.

### 3.2 Hidden Method (숨겨진 메서드)

**`private` 메서드가 많은 클래스는 별도 클래스로 추출해야 할 신호**라는 관찰이다.

#### 논리

- `private` 메서드는 클래스 내부의 복잡한 로직을 캡슐화한다.
- `private` 메서드가 많다는 것은 클래스 내부에 상당한 양의 숨겨진 복잡성이 있다는 뜻이다.
- 이 숨겨진 복잡성은 종종 별도의 책임을 나타낸다.
- `private` 메서드 그룹을 별도 클래스로 추출하면, 해당 메서드들이 새 클래스의 `public` 메서드가 되어 **직접 테스트할 수 있게** 된다.

```java
// Before: private 메서드가 많은 클래스
public class OrderProcessor {
    public void processOrder(Order order) {
        validateOrder(order);
        double total = calculateTotal(order);
        double tax = calculateTax(total, order.getState());
        double discount = applyDiscounts(order, total);
        // ...
    }

    private void validateOrder(Order order) { /* 50줄 */ }
    private double calculateTotal(Order order) { /* 30줄 */ }
    private double calculateTax(double amount, String state) { /* 40줄 */ }
    private double applyDiscounts(Order order, double total) { /* 60줄 */ }
    // ... 더 많은 private 메서드들
}
```

```java
// After: private 메서드를 별도 클래스로 추출
public class TaxCalculator {
    public double calculateTax(double amount, String state) {
        // 이제 public 메서드로 직접 테스트 가능!
        // ... 40줄의 세금 계산 로직 ...
    }
}

public class DiscountEngine {
    public double applyDiscounts(Order order, double total) {
        // 이제 public 메서드로 직접 테스트 가능!
        // ... 60줄의 할인 로직 ...
    }
}

public class OrderProcessor {
    private TaxCalculator taxCalculator;
    private DiscountEngine discountEngine;

    public void processOrder(Order order) {
        validateOrder(order);
        double total = calculateTotal(order);
        double tax = taxCalculator.calculateTax(total, order.getState());
        double discount = discountEngine.applyDiscounts(order, total);
        // ...
    }
}
```

### 3.3 Decisions That Can Change (변경될 수 있는 결정)

설계 시 내린 "결정" 중에서 **향후 변경될 가능성이 있는 것들**을 식별하고, 이를 별도 클래스로 분리하는 기법이다. 이는 정보 은닉(Information Hiding) 원칙과 직접적으로 연결된다.

#### 변경 가능한 결정의 예

| 결정 | 변경 가능성 |
|------|------------|
| 데이터 저장 형식 (XML, JSON, DB) | 높음 |
| 외부 서비스와의 통신 프로토콜 | 중간~높음 |
| 알고리즘의 구체적 구현 | 중간 |
| UI 렌더링 방식 | 높음 |
| 로깅 방식 | 중간 |

```java
// Before: 여러 "결정"이 하나의 클래스에 혼재
public class DataProcessor {
    public void process(String inputFile) {
        // 결정 1: 파일 형식은 CSV
        BufferedReader reader = new BufferedReader(new FileReader(inputFile));
        String line;
        while ((line = reader.readLine()) != null) {
            String[] fields = line.split(",");
            // ... CSV 파싱 로직 ...
        }

        // 결정 2: 결과 저장은 MySQL
        Connection conn = DriverManager.getConnection("jdbc:mysql://...");
        PreparedStatement stmt = conn.prepareStatement("INSERT INTO ...");
        // ... DB 저장 로직 ...

        // 결정 3: 알림은 이메일
        Transport.send(createEmailMessage(results));
    }
}
```

```java
// After: 각 "결정"을 별도 클래스로 분리
public class DataProcessor {
    private DataReader reader;          // 결정 1: 입력 형식
    private DataStore store;            // 결정 2: 저장 방식
    private NotificationService notifier; // 결정 3: 알림 방식

    public void process(String input) {
        List<Record> records = reader.read(input);
        // ... 처리 로직 ...
        store.save(records);
        notifier.notify(results);
    }
}
```

이렇게 하면 입력 형식이 CSV에서 JSON으로 바뀌어도 `DataReader`의 구현체만 교체하면 되고, `DataProcessor` 클래스는 변경할 필요가 없다.

### 3.4 Internal Relationships (내부 관계 분석)

인스턴스 변수와 메서드 간의 사용 관계를 분석하여 자연스러운 클래스 경계를 발견하는 기법이다. 이 기법의 핵심 도구는 **Feature Sketch**다.

#### Feature Sketch 만들기

Feature Sketch는 클래스 내의 변수와 메서드 사이의 의존 관계를 시각화한 다이어그램이다.

**절차:**

1. 클래스의 모든 인스턴스 변수를 나열한다.
2. 클래스의 모든 메서드를 나열한다.
3. 각 메서드가 어떤 인스턴스 변수를 사용하는지 선으로 연결한다.
4. 각 메서드가 어떤 다른 메서드를 호출하는지 선으로 연결한다.
5. 자연스럽게 분리되는 클러스터를 관찰한다.

#### 예시

```java
public class OrderManagement {
    // 인스턴스 변수
    private List<Order> orders;           // (A)
    private OrderValidator validator;     // (B)
    private List<Customer> customers;     // (C)
    private EmailService emailService;    // (D)
    private ReportFormatter formatter;    // (E)

    // 메서드
    public void addOrder(Order order) {          // uses: A, B
        validator.validate(order);
        orders.add(order);
    }
    public void removeOrder(int orderId) {       // uses: A
        orders.removeIf(o -> o.getId() == orderId);
    }
    public Order getOrder(int orderId) {         // uses: A
        return orders.stream().filter(...).findFirst().orElse(null);
    }
    public void notifyCustomer(int customerId) { // uses: C, D
        Customer c = findCustomer(customerId);
        emailService.send(c.getEmail(), "...");
    }
    public void notifyAllCustomers() {           // uses: C, D
        for (Customer c : customers) {
            emailService.send(c.getEmail(), "...");
        }
    }
    public String generateOrderReport() {        // uses: A, E
        return formatter.format(orders);
    }
    public String generateCustomerReport() {     // uses: C, E
        return formatter.format(customers);
    }
}
```

Feature Sketch를 그리면 다음과 같은 클러스터가 보인다:

```
클러스터 1 (주문 관리):
  [orders] ←→ addOrder(), removeOrder(), getOrder()
  [validator] ←→ addOrder()

클러스터 2 (고객 알림):
  [customers] ←→ notifyCustomer(), notifyAllCustomers()
  [emailService] ←→ notifyCustomer(), notifyAllCustomers()

클러스터 3 (보고서 생성):
  [formatter] ←→ generateOrderReport(), generateCustomerReport()
  [orders] ←→ generateOrderReport()
  [customers] ←→ generateCustomerReport()
```

클러스터 1과 2는 명확하게 분리된다. 클러스터 3은 양쪽 데이터를 모두 사용하지만, `formatter`라는 고유한 의존성을 가지고 있다. 이 분석을 통해 `OrderRepository`, `CustomerNotifier`, `ReportGenerator` 등의 클래스로 분리할 수 있다.

> **핵심 통찰**: Feature Sketch에서 클러스터 사이를 연결하는 선이 적을수록 분리가 자연스럽다. 선이 많이 교차하면 더 신중한 분석이 필요하다.

### 3.5 Looking for Primary Responsibility (주요 책임 찾기)

클래스의 **이름이 암시하는 핵심 책임**에 집중하고, 그 외의 것들을 분리하는 접근이다.

#### 절차

1. 클래스의 이름을 본다. 이 이름이 의미하는 "핵심 책임"은 무엇인가?
2. 클래스의 모든 메서드를 나열한다.
3. 각 메서드가 핵심 책임에 해당하는지 판단한다.
4. 핵심 책임에 해당하지 않는 메서드들을 별도 클래스로 추출한다.

```java
// 클래스 이름: "Order"
// 핵심 책임: 주문 데이터를 표현하고 관리하는 것

public class Order {
    // ✅ 핵심 책임: 주문 데이터 관리
    public void addItem(Item item) { ... }
    public void removeItem(int itemId) { ... }
    public List<Item> getItems() { ... }
    public double getTotal() { ... }

    // ❌ 핵심이 아님: 세금 계산 → TaxCalculator로 추출
    public double calculateTax() { ... }

    // ❌ 핵심이 아님: 배송 처리 → ShippingService로 추출
    public void ship() { ... }
    public String getTrackingNumber() { ... }

    // ❌ 핵심이 아님: 보고서 생성 → OrderReportGenerator로 추출
    public String toHtml() { ... }
    public String toPdf() { ... }
}
```

이 기법은 특히 "이 클래스가 정말로 해야 하는 일은 무엇인가?"라는 질문에 집중하게 만든다는 점에서 유용하다.

---

## 4. Interface Segregation Principle (ISP)

### 4.1 클래스 분리 전에 인터페이스로 먼저 분리

클래스를 물리적으로 쪼개는 것은 위험하고 시간이 걸리는 작업이다. 그 전 단계로, **인터페이스를 통해 논리적으로 먼저 분리**하는 것이 안전하다.

**Interface Segregation Principle (ISP)** 의 핵심:

> 클라이언트는 자신이 사용하지 않는 메서드에 의존하지 않아야 한다.

### 4.2 클라이언트별로 다른 인터페이스 제공

거대한 클래스의 클라이언트가 각각 다른 메서드 그룹을 사용한다면, 각 클라이언트에 맞는 인터페이스를 정의할 수 있다.

```java
// 거대한 클래스
public class ScheduleManager {
    // 스케줄 조회 메서드들
    public List<Event> getEventsForDay(Date date) { ... }
    public List<Event> getEventsForWeek(Date startDate) { ... }
    public Event getEvent(int eventId) { ... }

    // 스케줄 편집 메서드들
    public void addEvent(Event event) { ... }
    public void removeEvent(int eventId) { ... }
    public void moveEvent(int eventId, Date newDate) { ... }

    // 알림 관련 메서드들
    public void setReminder(int eventId, int minutesBefore) { ... }
    public void cancelReminder(int eventId) { ... }
    public List<Reminder> getUpcomingReminders() { ... }
}
```

클라이언트별 인터페이스를 정의한다:

```java
// 스케줄 표시 화면에서 사용하는 인터페이스
public interface ScheduleViewer {
    List<Event> getEventsForDay(Date date);
    List<Event> getEventsForWeek(Date startDate);
    Event getEvent(int eventId);
}

// 스케줄 편집 화면에서 사용하는 인터페이스
public interface ScheduleEditor {
    void addEvent(Event event);
    void removeEvent(int eventId);
    void moveEvent(int eventId, Date newDate);
}

// 알림 시스템에서 사용하는 인터페이스
public interface ReminderManager {
    void setReminder(int eventId, int minutesBefore);
    void cancelReminder(int eventId);
    List<Reminder> getUpcomingReminders();
}

// 기존 클래스가 모든 인터페이스를 구현
public class ScheduleManager
    implements ScheduleViewer, ScheduleEditor, ReminderManager {
    // ... 기존 구현 그대로 ...
}
```

### 4.3 ISP의 장점

이렇게 하면 **물리적 클래스 분리 없이도** 다음과 같은 이점을 얻는다:

| 이점 | 설명 |
|------|------|
| **의존성 명확화** | 각 클라이언트가 어떤 기능에 의존하는지 명확해진다 |
| **테스트 용이** | 인터페이스별로 Mock을 만들어 테스트할 수 있다 |
| **점진적 분리** | 나중에 인터페이스별로 별도 클래스를 만들어 구현을 이전할 수 있다 |
| **변경 영향 최소화** | 한 인터페이스의 변경이 다른 클라이언트에 영향을 주지 않는다 |

```java
// Before: ScheduleManager 전체에 의존
public class CalendarWidget {
    private ScheduleManager scheduleManager;  // 불필요한 메서드까지 접근 가능
}

// After: 필요한 인터페이스에만 의존
public class CalendarWidget {
    private ScheduleViewer scheduleViewer;  // 조회 기능만 사용
}
```

> ISP는 물리적 분리로 가는 디딤돌이다. 인터페이스를 먼저 분리해두면, 나중에 실제로 클래스를 분리할 때 클라이언트 코드를 변경할 필요가 없다.

---

## 5. Strategy Pattern과 위임을 통한 책임 분리

### 5.1 Strategy Pattern

알고리즘이나 동작이 다양하게 변할 수 있는 부분을 별도 클래스로 추출하고, 인터페이스를 통해 교체 가능하게 만드는 패턴이다.

```java
// Before: 모든 할인 로직이 OrderProcessor에 포함
public class OrderProcessor {
    public double calculateDiscount(Order order) {
        if (order.getCustomer().isVip()) {
            return order.getTotal() * 0.15;
        } else if (order.getItems().size() > 10) {
            return order.getTotal() * 0.10;
        } else if (isHolidaySeason()) {
            return order.getTotal() * 0.05;
        }
        return 0;
    }
}
```

```java
// After: Strategy Pattern으로 분리
public interface DiscountStrategy {
    double calculateDiscount(Order order);
}

public class VipDiscount implements DiscountStrategy {
    public double calculateDiscount(Order order) {
        return order.getTotal() * 0.15;
    }
}

public class BulkDiscount implements DiscountStrategy {
    public double calculateDiscount(Order order) {
        return order.getTotal() * 0.10;
    }
}

public class HolidayDiscount implements DiscountStrategy {
    public double calculateDiscount(Order order) {
        return order.getTotal() * 0.05;
    }
}

public class OrderProcessor {
    private DiscountStrategy discountStrategy;

    public OrderProcessor(DiscountStrategy discountStrategy) {
        this.discountStrategy = discountStrategy;
    }

    public double calculateDiscount(Order order) {
        return discountStrategy.calculateDiscount(order);
    }
}
```

### 5.2 위임(Delegation)

클래스의 일부 기능을 다른 클래스에 위임하는 것은 클래스 분해의 가장 기본적인 방법이다.

```java
// Before: 모든 것을 직접 수행
public class UserManager {
    public void createUser(String name, String email) {
        // 유효성 검사 (30줄)
        // 데이터베이스 저장 (20줄)
        // 환영 이메일 발송 (15줄)
        // 감사 로그 기록 (10줄)
    }
}

// After: 각 역할을 위임
public class UserManager {
    private UserValidator validator;
    private UserRepository repository;
    private WelcomeEmailSender emailSender;
    private AuditLogger auditLogger;

    public void createUser(String name, String email) {
        validator.validate(name, email);
        User user = repository.save(new User(name, email));
        emailSender.sendWelcomeEmail(user);
        auditLogger.log("User created: " + user.getId());
    }
}
```

위임을 통해 `UserManager`는 **조정자(coordinator)** 역할만 남게 되고, 각 세부 작업은 전문화된 클래스가 담당한다.

---

## 6. 실질적 리팩토링 단계

거대한 클래스를 분해하는 실제 작업 절차를 정리하면 다음과 같다.

### 6.1 단계별 접근

```
1단계: 현재 상태 파악
  └─ 메서드 목록 작성
  └─ Feature Sketch 그리기
  └─ 책임 식별 (5가지 기법 활용)

2단계: 인터페이스 분리 (ISP)
  └─ 클라이언트별 인터페이스 정의
  └─ 기존 클래스가 인터페이스를 구현하도록 변경
  └─ 클라이언트 코드가 인터페이스에 의존하도록 변경

3단계: 테스트 확보
  └─ 기존 동작을 검증하는 테스트 작성
  └─ 분리할 각 책임에 대한 테스트 작성

4단계: 클래스 추출
  └─ 한 번에 하나의 책임만 추출
  └─ 추출 후 테스트 실행으로 기존 동작 보존 확인
  └─ 반복

5단계: 정리
  └─ 불필요한 중간 계층 제거
  └─ 이름 정리
  └─ 최종 테스트 확인
```

### 6.2 Extract Class 리팩토링

Feathers가 제시하는 핵심 리팩토링은 **Extract Class**다:

1. 추출할 메서드 그룹과 관련 인스턴스 변수를 식별한다.
2. 새 클래스를 만든다.
3. 관련 인스턴스 변수를 새 클래스로 이동한다.
4. 관련 메서드를 새 클래스로 이동한다.
5. 원래 클래스에서 새 클래스의 인스턴스를 보유하고, 기존 메서드를 위임으로 변경한다.
6. 모든 테스트를 실행하여 기존 동작이 보존되었는지 확인한다.

```java
// 1. 원래 클래스에서 위임으로 변경
public class OrderManagement {
    private OrderRepository orderRepository;  // 추출된 클래스

    // 기존 메서드를 위임으로 변경 (클라이언트 코드는 변경 불필요)
    public void addOrder(Order order) {
        orderRepository.addOrder(order);
    }

    public Order getOrder(int orderId) {
        return orderRepository.getOrder(orderId);
    }
}
```

### 6.3 주의사항

- **한 번에 너무 많이 추출하지 않는다**: 한 번에 하나의 책임만 추출하고, 테스트를 확인한 후 다음으로 넘어간다.
- **위임 단계를 건너뛰지 않는다**: 먼저 위임으로 변경하고, 클라이언트 코드가 안정되면 그때 직접 참조로 전환한다.
- **이름을 신중하게 짓는다**: 추출된 클래스의 이름이 그 책임을 명확히 나타내야 한다.
- **테스트를 매 단계마다 실행한다**: 리팩토링의 안전망은 테스트뿐이다.

---

## 요약

- **거대한 클래스(God Class)** 는 이해, 변경, 테스트, 재사용을 모두 어렵게 만든다.
- **Single Responsibility Principle (SRP)**: 클래스는 "변경의 이유"가 하나만 있어야 한다.
- 책임을 식별하는 다섯 가지 기법:
  1. **Method Grouping**: 관련 메서드를 그룹으로 묶기
  2. **Hidden Method**: `private` 메서드가 많으면 별도 클래스 추출 신호
  3. **Decisions That Can Change**: 변경 가능한 결정을 별도 클래스로 분리
  4. **Internal Relationships (Feature Sketch)**: 변수와 메서드의 사용 관계를 시각화하여 클러스터 발견
  5. **Looking for Primary Responsibility**: 클래스 이름이 암시하는 핵심 책임에 집중
- **Interface Segregation Principle (ISP)**: 물리적 분리 전에 인터페이스로 먼저 논리적 분리를 수행한다.
- **Strategy Pattern**과 **위임(Delegation)** 은 책임 분리의 핵심 수단이다.
- 클래스 분해는 **한 번에 하나의 책임씩**, **테스트를 매 단계마다 확인하며** 진행한다.

---

## 다음 챕터와의 연결

Chapter 21 **"반복되는 동일한 수정, 그만할 수는 없을까? (I'm Changing the Same Code All Over the Place)"** 에서는 코드 중복이 왜 시스템을 변경하기 어렵게 만드는지, 그리고 중복을 효과적으로 제거하는 기법들(Extract Method, Template Method Pattern, Pull Up Method 등)을 소개한다. 중복 제거가 어떻게 설계 개선의 시작점이 되는지도 다룬다.
