# Chapter 22: '괴물 메소드'를 변경해야 하는데 테스트 코드를 작성하지 못하겠다 (I Need to Change a Monster Method and I Can't Write Tests for It)

## 핵심 질문

수백, 수천 줄에 달하는 거대한 메서드(Monster Method)를 변경해야 하는데 테스트를 작성할 수 없을 때, 어떻게 안전하게 리팩토링할 수 있는가? Monster Method의 유형에 따라 어떤 전략이 효과적인가?

---

## 1. Monster Method란 무엇인가

Monster Method는 수백 줄에서 수천 줄에 달하는 극도로 긴 메서드를 말한다. 레거시 코드에서 매우 흔하게 발견되며, 시간이 지남에 따라 개발자들이 기존 메서드에 계속 코드를 추가하면서 괴물처럼 성장한 결과물이다.

Monster Method는 다음과 같은 문제를 야기한다:

- **이해 불가**: 메서드 전체를 한 번에 이해하는 것이 불가능하다.
- **테스트 불가**: 메서드 내부의 특정 동작만 격리하여 테스트할 수 없다.
- **변경 위험**: 한 부분을 변경하면 다른 부분에 어떤 영향을 미칠지 예측하기 어렵다.
- **중복 코드**: 메서드 내에서 비슷한 로직이 반복되는 경우가 많다.

Feathers는 Monster Method를 두 가지 유형으로 분류한다: **Bulleted Method**와 **Snarled Method**.

---

## 2. Monster Method의 두 가지 유형

### 2.1 Bulleted Method (총알형 메서드)

Bulleted Method는 **들여쓰기가 거의 없고, 한 줄씩 순차적으로 실행되는 긴 메서드**이다. 마치 총알 목록(bullet list)처럼 코드가 위에서 아래로 일직선으로 나열된다.

```java
void processOrder(Order order) {
    // 섹션 1: 주문 검증 (20줄)
    String customerName = order.getCustomerName();
    if (customerName == null) customerName = "Unknown";
    String address = order.getAddress();
    // ... 검증 로직 계속 ...

    // 섹션 2: 가격 계산 (30줄)
    double basePrice = 0;
    for (Item item : order.getItems()) {
        basePrice += item.getPrice();
    }
    double tax = basePrice * taxRate;
    // ... 가격 계산 로직 계속 ...

    // 섹션 3: 재고 확인 (25줄)
    for (Item item : order.getItems()) {
        int stock = inventory.getStock(item.getId());
        // ... 재고 확인 로직 계속 ...
    }

    // 섹션 4: 결제 처리 (40줄)
    PaymentResult result = paymentGateway.charge(total);
    // ... 결제 처리 로직 계속 ...

    // 섹션 5: 배송 준비 (35줄)
    ShippingLabel label = createLabel(address);
    // ... 배송 준비 로직 계속 ...
}
```

**Bulleted Method의 특징:**

- 코드 블록들이 **비교적 독립적인 단계(step)**로 구성되어 있다.
- 각 섹션 사이에 **빈 줄이나 주석으로 구분**되어 있는 경우가 많다.
- 들여쓰기 수준이 낮아 **구조가 단순**하다.
- 리팩토링하기가 상대적으로 **수월**하다. 각 섹션을 별도 메서드로 추출하기 쉽다.

### 2.2 Snarled Method (엉킨 메서드)

Snarled Method는 **복잡한 조건문과 루프가 깊게 중첩(nested)되어 서로 얽혀있는 메서드**이다. "snarl"은 실타래가 엉켜있는 모습을 의미한다.

```java
void generateReport(List<Record> records) {
    for (int i = 0; i < records.size(); i++) {
        Record record = records.get(i);
        if (record.isActive()) {
            for (int j = 0; j < record.getEntries().size(); j++) {
                Entry entry = record.getEntries().get(j);
                if (entry.getType() == CREDIT) {
                    if (entry.getAmount() > threshold) {
                        // 30줄의 처리 로직...
                        if (record.getRegion().equals("US")) {
                            // 또 다른 20줄...
                            for (Tax tax : applicableTaxes) {
                                if (tax.appliesTo(entry)) {
                                    // 15줄의 세금 계산...
                                }
                            }
                        } else {
                            // 국제 처리 25줄...
                        }
                    } else {
                        // 소액 처리 15줄...
                    }
                } else if (entry.getType() == DEBIT) {
                    // 또 다른 복잡한 중첩 구조...
                }
            }
        }
    }
}
```

**Snarled Method의 특징:**

- **깊은 들여쓰기**: 조건문과 루프가 4~5단계 이상 중첩된다.
- **교차 의존성**: 내부 블록이 외부 블록의 변수를 참조하여, 블록을 독립적으로 추출하기 어렵다.
- **제어 흐름이 복잡**: if-else, for, while, switch가 뒤얽혀 있어 실행 경로를 추적하기 어렵다.
- 리팩토링이 Bulleted Method보다 **훨씬 어렵다**.

### 2.3 두 유형의 비교

| 특성 | Bulleted Method | Snarled Method |
|------|----------------|----------------|
| 들여쓰기 | 얕음 (1~2 수준) | 깊음 (4~5+ 수준) |
| 코드 블록 간 관계 | 비교적 독립적 | 서로 얽혀 있음 |
| 변수 공유 | 섹션 간 일부 공유 | 중첩 블록 간 광범위하게 공유 |
| 리팩토링 난이도 | 상대적으로 쉬움 | 매우 어려움 |
| 추출 전략 | 순차적 단계를 메서드로 추출 | 먼저 조건문/루프 본문을 추출 |

> 대부분의 Monster Method는 순수한 Bulleted나 순수한 Snarled가 아니라, 두 유형이 혼합된 형태이다. 리팩토링할 때는 먼저 Snarled 부분을 해소한 후, Bulleted 형태로 만들고, 그 다음에 섹션별로 추출하는 것이 효과적이다.

---

## 3. Monster Method를 테스트 없이 리팩토링하는 전략

Monster Method의 가장 큰 딜레마는 다음과 같다:

1. **리팩토링하려면 테스트가 필요**하다 (안전망 없이 변경하면 위험하다).
2. **테스트를 작성하려면 리팩토링이 필요**하다 (메서드가 너무 커서 테스트할 수 없다).

이것은 닭과 달걀의 문제이다. Feathers는 이 교착 상태를 깨기 위한 여러 기법을 제시한다.

### 3.1 핵심 원칙: 안전한 기계적 변환

테스트 없이 리팩토링할 때의 핵심 원칙은 **기계적이고 규칙적인 변환(mechanical transformation)** 만 수행하는 것이다. 사람이 "이렇게 바꿔도 동작이 같을 것이다"라고 판단하는 것이 아니라, **변환 규칙 자체가 동작 보존을 보장하는** 변환만 수행한다.

가장 대표적인 안전한 변환은:
- **Extract Method**: 코드 블록을 새 메서드로 추출 (자동화 도구 사용 권장)
- **변수 이름 변경 없이** 그대로 이동
- **매개변수와 반환 타입을 정확히 보존**하며 추출

---

## 4. Extract Method (메서드 추출)

### 4.1 기본 개념

Extract Method는 긴 메서드 안의 코드 블록을 **별도의 메서드로 추출**하는 리팩토링 기법이다. Monster Method를 작은 메서드들로 분해하는 가장 기본적이고 핵심적인 기법이다.

```java
// 추출 전
void processOrder(Order order) {
    // ... 100줄의 코드 ...

    // 가격 계산 부분 (추출 대상)
    double basePrice = 0;
    for (Item item : order.getItems()) {
        basePrice += item.getPrice() * item.getQuantity();
    }
    double discount = calculateDiscount(basePrice, order.getCustomerType());
    double total = basePrice - discount;

    // ... 나머지 100줄의 코드 ...
}
```

```java
// 추출 후
void processOrder(Order order) {
    // ... 100줄의 코드 ...

    double total = calculateTotal(order);

    // ... 나머지 100줄의 코드 ...
}

double calculateTotal(Order order) {
    double basePrice = 0;
    for (Item item : order.getItems()) {
        basePrice += item.getPrice() * item.getQuantity();
    }
    double discount = calculateDiscount(basePrice, order.getCustomerType());
    return basePrice - discount;
}
```

### 4.2 테스트 없이 Extract Method를 수행할 때의 위험

테스트가 없는 상태에서 수동으로 Extract Method를 수행하면 다음과 같은 실수가 발생할 수 있다:

1. **변수 누락**: 추출된 블록이 원래 메서드의 지역 변수를 사용하고 있었는데, 매개변수로 전달하는 것을 잊는 경우
2. **부수 효과(side effect) 누락**: 추출된 블록이 원래 메서드의 상태를 변경하고 있었는데, 이를 반영하지 않는 경우
3. **변수 초기화 순서 변경**: 추출 과정에서 변수의 초기화나 사용 순서가 바뀌는 경우
4. **반환값 누락**: 여러 변수가 동시에 변경되는 경우, 하나만 반환하고 나머지를 잊는 경우

### 4.3 자동화 도구 활용 권장

Feathers는 Extract Method를 수행할 때 **반드시 IDE의 자동 리팩토링 도구를 사용할 것을 강력히 권장**한다.

> 자동 리팩토링 도구가 있다면, 테스트 없이도 Extract Method를 안전하게 수행할 수 있다. 도구가 변수 참조, 반환값, 매개변수를 자동으로 분석해주기 때문이다.

대부분의 현대 IDE(IntelliJ IDEA, Eclipse, Visual Studio 등)는 Extract Method를 지원한다. 도구가:
- 추출 대상 블록이 사용하는 **모든 변수를 분석**하고
- 필요한 **매개변수를 자동으로 생성**하며
- **반환값을 올바르게 처리**한다.

자동화 도구가 없는 경우에는, 아래에서 설명하는 Sensing Variable이나 다른 기법을 통해 위험을 줄일 수 있다.

---

## 5. Introduce Sensing Variable (감지 변수 도입)

### 5.1 개념

Introduce Sensing Variable은 Monster Method 내에 **임시 변수를 추가하여 메서드의 중간 상태를 외부에서 감지(sense)할 수 있게 만드는** 기법이다. 테스트를 작성할 수 없는 거대한 메서드에서, 리팩토링의 정확성을 확인하기 위한 임시 조치이다.

### 5.2 적용 절차

1. Monster Method 내에서 **확인하고 싶은 중간 상태**를 식별한다.
2. 해당 지점에 **인스턴스 변수(sensing variable)를 추가**하고, 중간 값을 기록한다.
3. 테스트에서 Monster Method를 실행한 후, **sensing variable의 값을 확인**한다.
4. 리팩토링을 수행한다.
5. 리팩토링 후 동일한 테스트를 실행하여 **sensing variable의 값이 동일한지 확인**한다.
6. 검증이 완료되면 **sensing variable을 제거**한다.

### 5.3 예시

Monster Method의 중간에서 특정 계산이 올바르게 이루어지는지 확인하고 싶다고 하자:

```java
public class OrderProcessor {
    // Sensing Variable 추가 (임시)
    public int sensingTotalItems = -1;
    public double sensingSubtotal = -1;

    void processOrder(Order order) {
        // ... 앞부분 50줄 ...

        int totalItems = 0;
        double subtotal = 0;
        for (Item item : order.getItems()) {
            totalItems += item.getQuantity();
            subtotal += item.getPrice() * item.getQuantity();
        }

        // Sensing: 중간 상태 기록
        sensingTotalItems = totalItems;
        sensingSubtotal = subtotal;

        // ... 뒷부분 100줄 ...
    }
}
```

테스트 코드:

```java
public void testProcessOrderCalculation() {
    OrderProcessor processor = new OrderProcessor();
    Order order = createTestOrder(); // 알려진 테스트 데이터

    processor.processOrder(order);

    assertEquals(5, processor.sensingTotalItems);
    assertEquals(150.0, processor.sensingSubtotal, 0.01);
}
```

이제 이 테스트가 통과하는 상태에서 리팩토링을 수행하고, 리팩토링 후에도 같은 값이 나오는지 확인한다.

### 5.4 주의사항

- Sensing Variable은 **반드시 임시로만 사용**해야 한다. 리팩토링이 완료되면 제거한다.
- 프로덕션 코드에 테스트 전용 변수가 남아있으면 안 된다.
- Sensing Variable을 제거하는 것을 잊지 않도록, **커밋 전에 반드시 확인**한다.

> Sensing Variable은 우아한 기법이 아니다. 하지만 Monster Method에 테스트를 작성하는 것 자체가 불가능할 때, 리팩토링의 안전성을 확보하기 위한 실용적인 방법이다.

---

## 6. Break Out a Method Object (메서드 객체 추출)

### 6.1 개념

Break Out a Method Object는 **Monster Method를 통째로 별도의 클래스로 추출**하는 강력한 기법이다. 원래 메서드의 **지역 변수들이 새 클래스의 인스턴스 변수**가 되고, 메서드의 본문이 새 클래스의 메서드가 된다.

이 기법은 Martin Fowler의 "Replace Method with Method Object" 리팩토링과 동일하다.

### 6.2 왜 Method Object가 필요한가

Monster Method에서 직접 Extract Method를 하려고 하면, **지역 변수가 너무 많아서** 추출이 어려운 경우가 있다. 추출하려는 코드 블록이 메서드의 지역 변수 10개를 사용한다면, 새 메서드에 10개의 매개변수를 전달해야 한다. 이는 비현실적이다.

Method Object로 추출하면:
- 모든 지역 변수가 **인스턴스 변수**가 되므로, 매개변수 전달 문제가 사라진다.
- 새 클래스 안에서 **자유롭게 Extract Method를 수행**할 수 있다.

### 6.3 적용 절차

1. **새 클래스를 생성**한다. 클래스 이름은 Monster Method의 이름에서 유래하는 것이 좋다.
2. **원래 메서드의 매개변수와 지역 변수를 모두 새 클래스의 인스턴스 변수**로 선언한다.
3. 원래 메서드가 속한 객체(`this`)에 대한 참조도 새 클래스의 인스턴스 변수로 추가한다.
4. 새 클래스에 **`run()` 또는 `execute()` 같은 메서드를 만들고**, 원래 메서드의 본문을 복사한다.
5. 지역 변수 참조를 인스턴스 변수 참조로 변환한다 (변수 이름이 같으므로 대부분 자동).
6. **원래 메서드를 수정**하여, 새 클래스의 인스턴스를 생성하고 `run()`을 호출하도록 변경한다.
7. 컴파일이 되는지 확인한다.
8. 이제 **새 클래스 안에서 자유롭게 Extract Method**를 수행한다.

### 6.4 예시

원래 Monster Method:

```java
public class OrderProcessor {
    private Inventory inventory;
    private PaymentGateway gateway;

    void processOrder(Order order, Customer customer) {
        // 지역 변수들
        double subtotal = 0;
        double tax = 0;
        double shipping = 0;
        List<Item> unavailable = new ArrayList<>();
        boolean isPremium = customer.isPremium();

        // ... 300줄의 복잡한 로직 ...
        // subtotal, tax, shipping, unavailable, isPremium 등을
        // 광범위하게 사용
    }
}
```

Step 1~5: Method Object 클래스 생성

```java
public class OrderProcessingCommand {
    // 원래 객체에 대한 참조
    private OrderProcessor processor;

    // 원래 메서드의 매개변수 → 인스턴스 변수
    private Order order;
    private Customer customer;

    // 원래 메서드의 지역 변수 → 인스턴스 변수
    private double subtotal;
    private double tax;
    private double shipping;
    private List<Item> unavailable;
    private boolean isPremium;

    public OrderProcessingCommand(OrderProcessor processor,
                                   Order order, Customer customer) {
        this.processor = processor;
        this.order = order;
        this.customer = customer;
    }

    void run() {
        subtotal = 0;
        tax = 0;
        shipping = 0;
        unavailable = new ArrayList<>();
        isPremium = customer.isPremium();

        // ... 원래 300줄의 로직을 그대로 복사 ...
        // 지역 변수 참조가 인스턴스 변수 참조로 자연스럽게 전환됨
    }
}
```

Step 6: 원래 메서드 수정

```java
public class OrderProcessor {
    private Inventory inventory;
    private PaymentGateway gateway;

    void processOrder(Order order, Customer customer) {
        new OrderProcessingCommand(this, order, customer).run();
    }
}
```

Step 8: 새 클래스 안에서 Extract Method 자유롭게 수행

```java
public class OrderProcessingCommand {
    // ... 인스턴스 변수들 ...

    void run() {
        calculateSubtotal();
        checkInventory();
        calculateTax();
        calculateShipping();
        processPayment();
        createShipment();
    }

    private void calculateSubtotal() {
        // 추출된 메서드: subtotal 계산 로직
        // 인스턴스 변수에 직접 접근 가능 → 매개변수 불필요
    }

    private void checkInventory() {
        // 추출된 메서드: 재고 확인 로직
    }

    // ... 나머지 추출된 메서드들 ...
}
```

### 6.5 장점

- **매개변수 폭발 문제 해결**: 지역 변수가 인스턴스 변수가 되므로, 추출된 메서드에 매개변수를 전달할 필요가 없다.
- **자유로운 분해**: 새 클래스 안에서 마음껏 Extract Method를 수행할 수 있다.
- **테스트 용이**: 새 클래스는 독립적으로 생성하고 테스트할 수 있다.
- **원래 클래스의 변경 최소화**: 원래 메서드는 위임 호출 한 줄로 대체된다.

### 6.6 단점

- 클래스가 하나 추가된다.
- 원래 객체의 private 멤버에 접근해야 할 때 접근 제한자를 조정해야 할 수 있다.
- "메서드 하나를 위한 클래스"가 처음에는 어색하게 느껴질 수 있다. 하지만 시간이 지나면 이 클래스가 적절한 책임을 가진 객체로 발전하는 경우가 많다.

---

## 7. Skeletonize Method (메서드 골격화)

### 7.1 개념

Skeletonize Method는 Snarled Method를 다룰 때 특히 유용한 기법이다. **조건문과 루프의 본문(body)을 메서드로 추출하여, 원래 메서드에는 제어 구조의 뼈대(skeleton)만 남기는** 것이다.

### 7.2 적용 방법

복잡하게 중첩된 조건문과 루프가 있을 때, **가장 안쪽의 본문부터 바깥쪽으로** 추출해 나간다.

추출 전:

```java
void generateReport(List<Record> records) {
    for (int i = 0; i < records.size(); i++) {
        Record record = records.get(i);
        if (record.isActive()) {
            for (Entry entry : record.getEntries()) {
                if (entry.getType() == CREDIT) {
                    if (entry.getAmount() > threshold) {
                        // 30줄의 고액 신용 처리 로직
                        double adjusted = entry.getAmount() * rate;
                        report.addLine(record.getName(), adjusted);
                        // ...
                    } else {
                        // 15줄의 소액 신용 처리 로직
                        report.addLine(record.getName(), entry.getAmount());
                        // ...
                    }
                } else if (entry.getType() == DEBIT) {
                    // 25줄의 차변 처리 로직
                    // ...
                }
            }
        }
    }
}
```

Skeletonize 적용 후:

```java
void generateReport(List<Record> records) {
    for (int i = 0; i < records.size(); i++) {
        Record record = records.get(i);
        if (record.isActive()) {
            for (Entry entry : record.getEntries()) {
                if (entry.getType() == CREDIT) {
                    if (entry.getAmount() > threshold) {
                        processHighValueCredit(record, entry);
                    } else {
                        processLowValueCredit(record, entry);
                    }
                } else if (entry.getType() == DEBIT) {
                    processDebit(record, entry);
                }
            }
        }
    }
}
```

이제 원래 메서드에는 **제어 흐름의 뼈대만 남아** 있고, 실제 로직은 각 추출된 메서드에 들어 있다.

### 7.3 Skeletonize의 장점

- 원래 메서드의 **전체적인 제어 흐름(알고리즘 구조)이 한눈에 보인다**.
- 추출된 각 메서드는 **개별적으로 테스트 가능**하다.
- Snarled Method를 **Bulleted Method 형태로 변환**하는 효과가 있다.
- 변수 공유 범위가 줄어들어 코드 이해가 쉬워진다.

### 7.4 Skeletonize vs. Extract Method

Skeletonize는 Extract Method의 특수한 적용 방식이다. 일반적인 Extract Method가 "코드 블록을 추출한다"는 범용적 기법이라면, Skeletonize는 **"조건문/루프의 본문만 선택적으로 추출하여 뼈대를 남긴다"** 는 구체적인 전략이다.

---

## 8. Find Sequence (시퀀스 찾기)

### 8.1 개념

Find Sequence는 **긴 메서드에서 독립적인 단계(step)를 식별**하는 기법이다. 특히 Bulleted Method에서 유용하다. 메서드를 위에서 아래로 읽으며 "여기서부터 여기까지는 하나의 독립적인 작업이다"라고 경계를 표시하는 것이다.

### 8.2 적용 방법

1. **메서드를 처음부터 끝까지 읽으며**, 논리적으로 독립된 단계를 식별한다.
2. 각 단계의 **시작과 끝에 주석이나 빈 줄로 표시**한다.
3. 각 단계가 **다음 단계에 전달하는 데이터(변수)를 파악**한다.
4. 단계 간의 의존성이 최소화되도록 경계를 조정한다.
5. 각 단계를 **별도 메서드로 추출**한다.

### 8.3 예시

```java
void initialize() {
    // ---- 단계 1: 설정 파일 로드 ----
    Properties props = new Properties();
    FileInputStream fis = new FileInputStream("config.properties");
    props.load(fis);
    fis.close();
    String dbUrl = props.getProperty("db.url");
    String dbUser = props.getProperty("db.user");

    // ---- 단계 2: 데이터베이스 연결 ----
    Connection conn = DriverManager.getConnection(dbUrl, dbUser, dbPass);
    conn.setAutoCommit(false);

    // ---- 단계 3: 캐시 초기화 ----
    cache = new HashMap<>();
    Statement stmt = conn.createStatement();
    ResultSet rs = stmt.executeQuery("SELECT * FROM lookup_table");
    while (rs.next()) {
        cache.put(rs.getString("key"), rs.getString("value"));
    }
    rs.close();
    stmt.close();

    // ---- 단계 4: 리스너 등록 ----
    eventBus.register(new OrderListener(conn));
    eventBus.register(new InventoryListener(cache));
}
```

각 단계를 식별한 후 추출하면:

```java
void initialize() {
    Properties props = loadConfiguration();
    Connection conn = connectToDatabase(props);
    Map<String, String> cache = initializeCache(conn);
    registerListeners(conn, cache);
}
```

### 8.4 시퀀스 식별의 단서

- **빈 줄**: 개발자가 무의식적으로 단계 사이에 빈 줄을 넣는 경우가 많다.
- **주석**: "// 다음은 ~를 처리한다" 같은 주석이 단계의 시작을 나타낸다.
- **변수 선언 묶음**: 여러 변수가 한꺼번에 선언되는 부분이 새로운 단계의 시작일 수 있다.
- **변수 사용 범위**: 특정 변수가 일정 범위 내에서만 사용되면, 그 범위가 하나의 단계일 가능성이 높다.

---

## 9. 리팩토링 전략 선택 가이드

Monster Method의 유형에 따라 적합한 전략이 다르다:

### 9.1 Bulleted Method 리팩토링 전략

```
1. Find Sequence로 독립적인 단계를 식별
2. 각 단계를 Extract Method로 추출
3. 추출된 메서드에 대해 테스트 작성
4. 테스트의 보호 아래 추가 리팩토링
```

### 9.2 Snarled Method 리팩토링 전략

```
1. Skeletonize: 조건문/루프의 본문을 Extract Method로 추출
2. 뼈대만 남은 메서드에서 Find Sequence 적용
3. 시퀀스를 Extract Method로 추출
4. 추출된 메서드에 대해 테스트 작성
```

### 9.3 매개변수가 너무 많을 때

```
1. Break Out a Method Object로 메서드를 클래스로 추출
2. 새 클래스 안에서 자유롭게 Extract Method 적용
3. Skeletonize + Find Sequence 조합 활용
```

### 9.4 판단 플로차트

```
Monster Method를 변경해야 한다
├── 자동 리팩토링 도구가 있는가?
│   ├── YES → 도구를 사용하여 Extract Method 수행
│   │         ├── Bulleted → Find Sequence 후 단계별 추출
│   │         └── Snarled → Skeletonize 후 추출
│   └── NO  → 수동으로 진행해야 함
│             ├── 지역 변수가 많아 Extract가 어려운가?
│             │   ├── YES → Break Out a Method Object
│             │   └── NO  → 조심스럽게 Extract Method
│             └── Introduce Sensing Variable로 안전성 확보
```

---

## 10. 자동화 도구 활용의 중요성

Feathers는 Monster Method를 다룰 때 **자동화된 리팩토링 도구의 사용을 강력히 권장**한다.

### 10.1 자동화 도구의 장점

- **기계적 정확성**: 변수 참조 분석, 매개변수 생성, 반환값 처리를 정확하게 수행한다.
- **속도**: 수백 줄의 코드를 몇 초 만에 추출할 수 있다.
- **일관성**: 같은 변환을 항상 동일하게 수행한다.
- **안전성**: 사람이 범하기 쉬운 실수(변수 누락, 타입 불일치 등)를 방지한다.

### 10.2 도구가 없을 때의 대안

자동화 도구가 없을 때는 다음 원칙을 따른다:

1. **한 번에 하나의 변환만** 수행한다.
2. **Preserve Signatures** (Chapter 23): 시그니처를 보존하며 변환한다.
3. **컴파일 후 확인**: 매 변환 후 반드시 컴파일하여 오류를 확인한다.
4. **Sensing Variable**을 활용하여 동작이 보존되었는지 확인한다.
5. **작은 단위**로 변환하고, 각 단계에서 중간 확인을 한다.

---

## 11. Monster Method의 실전 리팩토링 예시

### 11.1 시나리오

500줄짜리 `render()` 메서드가 있다고 가정하자. 이 메서드는 문서를 렌더링하며, Snarled와 Bulleted가 혼합된 형태이다.

### 11.2 단계별 접근

**1단계: 전체 구조 파악**

메서드를 훑어보며 대략적인 구조를 파악한다. 주석이나 빈 줄을 단서로 삼는다.

**2단계: Skeletonize (Snarled 부분 해소)**

깊게 중첩된 조건문/루프의 본문을 먼저 추출한다.

```java
// Before
for (Element el : elements) {
    if (el.isVisible()) {
        if (el.getType() == TEXT) {
            // 40줄의 텍스트 렌더링
        } else if (el.getType() == IMAGE) {
            // 35줄의 이미지 렌더링
        }
    }
}

// After Skeletonize
for (Element el : elements) {
    if (el.isVisible()) {
        if (el.getType() == TEXT) {
            renderText(el);
        } else if (el.getType() == IMAGE) {
            renderImage(el);
        }
    }
}
```

**3단계: Find Sequence (Bulleted 부분 식별)**

Skeletonize 후 드러난 순차적 단계를 식별한다.

**4단계: 각 시퀀스를 Extract Method로 추출**

**5단계: 추출된 메서드에 테스트 작성**

이제 작은 메서드들은 테스트 가능하다.

**6단계: 테스트의 보호 아래 추가 리팩토링**

---

## 요약

- Monster Method는 **Bulleted Method**(순차적, 얕은 들여쓰기)와 **Snarled Method**(복잡한 중첩, 깊은 들여쓰기) 두 유형으로 분류된다.
- **Extract Method**는 Monster Method를 분해하는 가장 기본적인 기법이며, 자동화 도구 사용이 강력히 권장된다.
- **Introduce Sensing Variable**은 테스트를 작성할 수 없는 메서드에서 중간 상태를 확인하기 위한 임시 변수를 추가하는 기법이다.
- **Break Out a Method Object**는 지역 변수가 너무 많아 Extract Method가 어려울 때, 메서드 전체를 별도 클래스로 추출하는 강력한 기법이다.
- **Skeletonize Method**는 조건문/루프의 본문을 추출하여 제어 구조의 뼈대만 남기는 기법으로, Snarled Method에 특히 효과적이다.
- **Find Sequence**는 Bulleted Method에서 독립적인 단계를 식별하여 추출하는 기법이다.
- 핵심 전략: Snarled 부분을 먼저 Skeletonize하고, Bulleted 형태로 만든 다음, Find Sequence로 단계를 식별하여 추출한다.
- 테스트 없이 리팩토링할 때는 **기계적이고 안전한 변환만** 수행해야 한다.

---

## 다음 챕터와의 연결

Chapter 23 **"기존 동작을 건드리지 않았음을 어떻게 확인할 수 있을까? (How Do I Know That I'm Not Breaking Anything?)"** 에서는 Monster Method를 리팩토링하든, 작은 변경을 하든, 기존 동작을 보존하는 것이 핵심이다. 초의식적 편집(Hyperaware Editing), 단일 목표 편집(Single-Goal Editing), 시그니처 보존(Preserve Signatures), 컴파일러에 기대기(Lean on the Compiler), 짝 프로그래밍(Pair Programming) 등 변경의 안전성을 높이는 실천법을 소개한다.
