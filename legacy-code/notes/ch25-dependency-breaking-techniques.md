# Chapter 25: 의존 관계 제거 기법 (Dependency-Breaking Techniques)

## 핵심 질문

레거시 코드에서 테스트를 작성하려면 의존성을 해제해야 한다. 의존성의 종류와 상황에 따라 어떤 기법을 적용해야 하는가? 각 기법의 구체적인 절차와 주의사항은 무엇인가?

---

## 1. 의존성 해제 기법 카탈로그

이 장은 책에서 가장 긴 장으로, 이전 장들에서 언급된 의존성 해제 기법들의 **상세한 절차와 예시를 카탈로그 형태로 정리**한 것이다. 각 기법은 알파벳 순서로 나열되어 있으며, 필요할 때 레퍼런스로 찾아볼 수 있도록 구성되어 있다.

의존성 해제의 두 가지 목적을 다시 상기하자:

1. **Sensing (감지)**: 코드의 내부 동작을 외부에서 확인할 수 있게 만든다.
2. **Separation (분리)**: 코드를 테스트 하네스에서 독립적으로 실행할 수 있게 만든다.

---

## 2. Adapt Parameter (매개변수 적응)

### 한 줄 설명
매개변수의 타입을 래핑하여, 테스트에서 대체 가능한 인터페이스를 만든다.

### 적용 상황
- 메서드의 매개변수가 **외부 라이브러리 타입이나 테스트하기 어려운 타입**일 때
- 해당 타입을 직접 수정할 수 없지만, 메서드에서 사용하는 기능은 일부분일 때

### 절차
1. 매개변수 타입이 제공하는 기능 중 **메서드가 실제로 사용하는 기능을 파악**한다.
2. 해당 기능만 포함하는 **인터페이스(또는 래퍼 클래스)를 생성**한다.
3. 원래 타입을 감싸는 **프로덕션 구현체**를 만든다.
4. 메서드의 매개변수 타입을 새 **인터페이스로 변경**한다.
5. 테스트에서 **가짜(fake) 구현체**를 만들어 전달한다.

### 코드 예시

변경 전:

```java
public class ARMDispatcher {
    public void dispatch(HttpServletRequest request) {
        String type = request.getParameter("type");
        if ("login".equals(type)) {
            // 로그인 처리...
        }
        // ...
    }
}
```

`HttpServletRequest`는 서블릿 컨테이너가 제공하는 객체이므로, 테스트에서 직접 생성하기 어렵다.

변경 후:

```java
// 1. 필요한 기능만 담은 인터페이스
public interface ParameterSource {
    String getParameter(String name);
}

// 2. 프로덕션 구현체
public class ServletParameterSource implements ParameterSource {
    private HttpServletRequest request;

    public ServletParameterSource(HttpServletRequest request) {
        this.request = request;
    }

    public String getParameter(String name) {
        return request.getParameter(name);
    }
}

// 3. 메서드 시그니처 변경
public class ARMDispatcher {
    public void dispatch(ParameterSource source) {
        String type = source.getParameter("type");
        if ("login".equals(type)) {
            // ...
        }
    }
}

// 4. 테스트용 가짜 구현체
public class FakeParameterSource implements ParameterSource {
    private Map<String, String> params = new HashMap<>();

    public void addParameter(String name, String value) {
        params.put(name, value);
    }

    public String getParameter(String name) {
        return params.get(name);
    }
}
```

---

## 3. Break Out Method Object (메서드 객체 추출)

### 한 줄 설명
거대한 메서드를 별도의 클래스로 추출하여, 지역 변수를 인스턴스 변수로 변환하고 자유롭게 리팩토링한다.

### 적용 상황
- **Monster Method**를 분해해야 하는데, 지역 변수가 너무 많아 Extract Method로는 매개변수 폭발이 일어날 때
- 메서드의 로직이 원래 클래스의 나머지 부분과 비교적 독립적일 때

### 절차
1. 새 클래스를 생성한다.
2. 원래 메서드의 **매개변수를 새 클래스의 생성자 매개변수**로 만든다.
3. 원래 메서드의 **지역 변수를 새 클래스의 인스턴스 변수**로 선언한다.
4. 원래 객체에 대한 참조(`this`)도 인스턴스 변수로 추가한다.
5. 새 클래스에 `run()` 메서드를 만들고, 원래 메서드의 **본문을 복사**한다.
6. 지역 변수 참조를 인스턴스 변수 참조로 변환한다.
7. 원래 메서드를 **위임 호출**로 대체한다.
8. 새 클래스 안에서 **자유롭게 Extract Method**를 수행한다.

### 코드 예시

```java
// 원래 코드
class Reservation {
    int calculateFee(Date start, Date end, List<Room> rooms) {
        int total = 0;
        int nights = /* 복잡한 날짜 계산 */;
        double rate = 0;
        // ... 300줄의 복잡한 계산 로직 ...
        return total;
    }
}

// Method Object로 추출
class FeeCalculation {
    Reservation reservation;
    Date start;
    Date end;
    List<Room> rooms;
    int total;
    int nights;
    double rate;

    FeeCalculation(Reservation reservation, Date start, Date end, List<Room> rooms) {
        this.reservation = reservation;
        this.start = start;
        this.end = end;
        this.rooms = rooms;
    }

    int run() {
        total = 0;
        nights = /* 복잡한 날짜 계산 */;
        rate = 0;
        // ... 원래 300줄을 그대로 복사 ...
        return total;
    }
}

// 원래 메서드는 위임만
class Reservation {
    int calculateFee(Date start, Date end, List<Room> rooms) {
        return new FeeCalculation(this, start, end, rooms).run();
    }
}
```

> 이 기법의 상세한 설명은 Chapter 22에서도 다루고 있다.

---

## 4. Definition Completion (정의 완성)

### 한 줄 설명
C/C++에서 선언(declaration)과 정의(definition)를 분리하여, 테스트에서 대체 정의를 제공한다.

### 적용 상황
- **C/C++ 코드**에서 헤더 파일에 선언된 클래스의 멤버 함수를 테스트할 때
- 클래스의 일부 멤버 함수만 테스트용으로 대체하고 싶을 때

### 절차
1. 헤더 파일(.h)에 클래스의 **선언**을 유지한다.
2. 프로덕션 소스 파일(.cpp)에 **프로덕션 정의**를 작성한다.
3. 테스트 소스 파일(.cpp)에 **테스트용 대체 정의**를 작성한다.
4. 빌드 시 **테스트 파일을 프로덕션 파일 대신 링크**한다.

### 코드 예시

```cpp
// header.h (선언)
class NetworkConnection {
public:
    void send(const std::string& data);
    std::string receive();
};

// production.cpp (프로덕션 정의)
void NetworkConnection::send(const std::string& data) {
    // 실제 네트워크 전송 로직
    socket.write(data);
}

// test_stubs.cpp (테스트용 정의)
void NetworkConnection::send(const std::string& data) {
    // 테스트: 전송 대신 기록만 함
    sentData.push_back(data);
}
```

---

## 5. Encapsulate Global References (전역 참조 캡슐화)

### 한 줄 설명
전역 변수나 전역 함수를 클래스로 캡슐화하여 테스트에서 교체 가능하게 만든다.

### 적용 상황
- 코드가 **전역 변수나 전역 함수에 직접 의존**할 때
- 전역 상태 때문에 **테스트가 서로 간섭**할 때

### 절차
1. 관련된 전역 변수와 전역 함수를 **하나의 클래스로 묶는다**.
2. 전역 참조를 사용하는 코드를 **새 클래스의 인스턴스를 통해 접근하도록 변경**한다.
3. 테스트에서 **클래스의 인스턴스를 교체**하여 원하는 동작을 주입한다.

### 코드 예시

변경 전:

```cpp
// 전역 변수
double exchange_rate;
std::string base_currency;

// 전역 함수
double convert(double amount, std::string target) {
    return amount * exchange_rate;
}

// 사용하는 코드
void processPayment(double amount) {
    double usd = convert(amount, "USD");  // 전역 함수 직접 호출
    // ...
}
```

변경 후:

```cpp
// 전역 참조를 클래스로 캡슐화
class CurrencyConverter {
public:
    double exchange_rate;
    std::string base_currency;

    virtual double convert(double amount, std::string target) {
        return amount * exchange_rate;
    }
};

// 사용하는 코드: 인스턴스를 통해 접근
void processPayment(double amount, CurrencyConverter& converter) {
    double usd = converter.convert(amount, "USD");
    // ...
}

// 테스트: 가짜 구현 사용
class FakeCurrencyConverter : public CurrencyConverter {
public:
    double convert(double amount, std::string target) override {
        return amount; // 1:1 변환
    }
};
```

---

## 6. Expose Static Method (정적 메서드 노출)

### 한 줄 설명
인스턴스 변수에 의존하지 않는 로직을 static 메서드로 추출하여, 객체 생성 없이 테스트한다.

### 적용 상황
- 메서드 내에 **인스턴스 상태에 의존하지 않는 독립적인 로직**이 있을 때
- 해당 클래스의 **인스턴스를 생성하기 어려울 때** (복잡한 생성자, 숨겨진 의존성 등)

### 절차
1. 메서드에서 **인스턴스 변수나 메서드를 사용하지 않는 코드 블록을 식별**한다.
2. 해당 블록을 **public static 메서드로 추출**한다.
3. 필요한 데이터는 **매개변수로 전달**한다.
4. 테스트에서 **클래스 인스턴스 생성 없이 static 메서드를 직접 호출**한다.

### 코드 예시

```java
// 변경 전: 인스턴스를 생성해야만 테스트 가능
public class BillingStatement {
    // 복잡한 의존성...
    public BillingStatement(Database db, MailServer mail, ...) { }

    public String formatAmount(double amount) {
        // 이 로직은 인스턴스 상태와 무관!
        String result = String.format("$%.2f", amount);
        if (amount < 0) {
            result = "(" + result + ")";
        }
        return result;
    }
}

// 변경 후: static 메서드로 노출
public class BillingStatement {
    // ...

    // 인스턴스 없이 테스트 가능
    public static String formatAmount(double amount) {
        String result = String.format("$%.2f", amount);
        if (amount < 0) {
            result = "(" + result + ")";
        }
        return result;
    }
}

// 테스트
public void testFormatAmount() {
    assertEquals("$100.00", BillingStatement.formatAmount(100.0));
    assertEquals("($50.00)", BillingStatement.formatAmount(-50.0));
}
```

---

## 7. Extract and Override Call (호출 추출 및 오버라이드)

### 한 줄 설명
의존성이 있는 메서드 호출을 별도 메서드로 추출한 후, 테스트용 서브클래스에서 오버라이드한다.

### 적용 상황
- 메서드 내에서 **외부 서비스나 복잡한 객체를 호출**하는 부분이 있을 때
- 해당 호출만 **테스트에서 격리**하고 싶을 때

### 절차
1. 의존성이 있는 **호출을 식별**한다.
2. 해당 호출을 **protected 메서드로 추출**한다.
3. 테스트에서 **서브클래스를 만들어 해당 메서드를 오버라이드**한다.

### 코드 예시

```java
// 변경 전
public class OrderProcessor {
    public void process(Order order) {
        // 비즈니스 로직...
        double total = calculateTotal(order);

        // 외부 서비스 호출 (테스트에서 실행하고 싶지 않음)
        PaymentGateway gateway = new PaymentGateway();
        gateway.charge(order.getAccountId(), total);

        // 추가 로직...
    }
}

// 변경 후: 호출을 메서드로 추출
public class OrderProcessor {
    public void process(Order order) {
        double total = calculateTotal(order);
        chargePayment(order.getAccountId(), total);
        // 추가 로직...
    }

    // 추출된 메서드 (오버라이드 가능)
    protected void chargePayment(String accountId, double amount) {
        PaymentGateway gateway = new PaymentGateway();
        gateway.charge(accountId, amount);
    }
}

// 테스트용 서브클래스
class TestingOrderProcessor extends OrderProcessor {
    public String chargedAccountId;
    public double chargedAmount;

    @Override
    protected void chargePayment(String accountId, double amount) {
        // 실제 결제 대신 기록만 함
        this.chargedAccountId = accountId;
        this.chargedAmount = amount;
    }
}

// 테스트
public void testProcessChargesCorrectAmount() {
    TestingOrderProcessor processor = new TestingOrderProcessor();
    Order order = createTestOrder(100.0);
    processor.process(order);
    assertEquals(100.0, processor.chargedAmount, 0.01);
}
```

---

## 8. Extract and Override Factory Method (팩토리 메서드 추출 및 오버라이드)

### 한 줄 설명
생성자에서 직접 객체를 생성하는 코드를 팩토리 메서드로 추출하여, 테스트에서 다른 객체로 교체한다.

### 적용 상황
- **생성자에서 복잡한 객체를 직접 생성**하고 있을 때
- 해당 객체가 **테스트에서 사용하기 어려운 외부 의존성**일 때

### 절차
1. 생성자에서 **객체 생성 코드를 식별**한다.
2. 해당 코드를 **protected 팩토리 메서드로 추출**한다.
3. 테스트에서 **서브클래스를 만들어 팩토리 메서드를 오버라이드**한다.

### 코드 예시

```java
// 변경 전
public class ReportGenerator {
    private Database database;
    private MailService mailer;

    public ReportGenerator() {
        // 생성자에서 직접 생성 → 테스트 어려움
        this.database = new OracleDatabase("prod-connection-string");
        this.mailer = new SmtpMailService("smtp.company.com");
    }
}

// 변경 후: 팩토리 메서드로 추출
public class ReportGenerator {
    private Database database;
    private MailService mailer;

    public ReportGenerator() {
        this.database = createDatabase();
        this.mailer = createMailService();
    }

    protected Database createDatabase() {
        return new OracleDatabase("prod-connection-string");
    }

    protected MailService createMailService() {
        return new SmtpMailService("smtp.company.com");
    }
}

// 테스트용 서브클래스
class TestingReportGenerator extends ReportGenerator {
    @Override
    protected Database createDatabase() {
        return new InMemoryDatabase();  // 테스트용 DB
    }

    @Override
    protected MailService createMailService() {
        return new FakeMailService();  // 메일 발송 안 함
    }
}
```

> **주의**: Java에서 생성자 내에서 오버라이드된 메서드를 호출하는 것은 위험할 수 있다. 서브클래스의 필드가 아직 초기화되지 않은 상태에서 메서드가 호출될 수 있기 때문이다. C++에서는 생성자에서의 가상 함수 호출이 의도대로 동작하지 않으므로 이 기법을 적용할 수 없다.

---

## 9. Extract and Override Getter (Getter 추출 및 오버라이드)

### 한 줄 설명
인스턴스 변수에 대한 직접 접근을 getter 메서드로 변환하고, 지연 초기화(lazy initialization)를 통해 테스트에서 의존성을 교체한다.

### 적용 상황
- 생성자에서 객체를 직접 생성하여 인스턴스 변수에 할당하는데, Extract and Override Factory Method를 사용할 수 없을 때 (예: C++에서)
- **지연 초기화 패턴**으로 전환하여 의존성 교체를 가능하게 하고 싶을 때

### 절차
1. 생성자에서 생성되는 객체에 대한 **getter 메서드를 만든다**.
2. getter에서 **지연 초기화**를 구현한다.
3. 코드 내에서 인스턴스 변수 직접 접근을 **getter 호출로 변경**한다.
4. 테스트에서 **서브클래스를 만들어 getter를 오버라이드**한다.

### 코드 예시

```java
// 변경 전
public class Processor {
    private Connection connection;

    public Processor() {
        this.connection = new RealConnection("db-host:5432");
    }

    public void execute() {
        connection.query("SELECT ...");  // 직접 접근
    }
}

// 변경 후: getter + 지연 초기화
public class Processor {
    private Connection connection = null;

    public Processor() {
        // 생성자에서는 생성하지 않음
    }

    protected Connection getConnection() {
        if (connection == null) {
            connection = new RealConnection("db-host:5432");
        }
        return connection;
    }

    public void execute() {
        getConnection().query("SELECT ...");  // getter를 통해 접근
    }
}

// 테스트용 서브클래스
class TestingProcessor extends Processor {
    @Override
    protected Connection getConnection() {
        return new FakeConnection();
    }
}
```

---

## 10. Extract Implementer (구현자 추출)

### 한 줄 설명
기존 클래스의 구현을 새 클래스로 이동하고, 기존 클래스를 인터페이스로 변환한다.

### 적용 상황
- 기존 클래스를 **인터페이스로 만들고 싶지만**, 많은 코드가 해당 클래스를 직접 참조하고 있을 때
- Extract Interface(인터페이스 추출)와 비슷하지만, **기존 이름을 인터페이스로 유지하고 싶을 때**

### 절차
1. 기존 클래스의 **모든 비정적(non-static) public 메서드를 포함하는 인터페이스를 정의**한다. 이때 인터페이스의 이름은 **기존 클래스의 이름을 사용**한다.
2. 기존 클래스의 이름을 **새 이름(구현 클래스)으로 변경**한다.
3. 기존 클래스 이름으로 **인터페이스를 생성**한다.
4. 이름이 변경된 클래스가 **새 인터페이스를 구현하도록** 한다.
5. 컴파일하여 **직접 인스턴스화하는 곳을 찾아 새 클래스명으로 수정**한다.

### 코드 예시

```java
// 변경 전
public class ModelNode {
    private List<ModelNode> children;

    public void addChild(ModelNode child) { ... }
    public List<ModelNode> getChildren() { ... }
    public void render(Canvas canvas) { ... }
}

// 변경 후
// 1. 기존 이름으로 인터페이스 생성
public interface ModelNode {
    void addChild(ModelNode child);
    List<ModelNode> getChildren();
    void render(Canvas canvas);
}

// 2. 구현을 새 클래스로 이동
public class ProductionModelNode implements ModelNode {
    private List<ModelNode> children;

    public void addChild(ModelNode child) { ... }
    public List<ModelNode> getChildren() { ... }
    public void render(Canvas canvas) { ... }
}

// 3. 인스턴스 생성 부분만 수정
// 변경 전: ModelNode node = new ModelNode();
// 변경 후: ModelNode node = new ProductionModelNode();
```

### Extract Implementer vs Extract Interface

| 특성 | Extract Implementer | Extract Interface |
|------|-------------------|-------------------|
| 기존 이름 | 인터페이스가 가져감 | 클래스가 유지 |
| 참조 코드 변경 | 인스턴스 생성부만 | 타입 선언부 변경 |
| 적합한 상황 | 참조가 매우 많을 때 | 이름 충돌이 없을 때 |

---

## 11. Extract Interface (인터페이스 추출)

### 한 줄 설명
기존 클래스에서 인터페이스를 추출하여, 테스트에서 가짜 구현을 제공할 수 있게 한다.

### 적용 상황
- 클래스에 **직접 의존하고 있어서 테스트에서 교체할 수 없을 때**
- **특정 메서드들만 테스트에서 가짜로 대체**하고 싶을 때

### 절차
1. 대체하고 싶은 클래스에서 **테스트에 필요한 메서드를 식별**한다.
2. 해당 메서드들을 포함하는 **인터페이스를 생성**한다.
3. 기존 클래스가 **인터페이스를 구현하도록** 한다.
4. 의존하는 코드의 타입 선언을 **인터페이스 타입으로 변경**한다.
5. 테스트에서 **가짜 구현 클래스를 만들어 사용**한다.

### 코드 예시

```java
// 변경 전
public class TaxCalculator {
    public double calculateTax(double amount, String state) {
        // 복잡한 세금 계산 (외부 서비스 호출 포함)
    }
}

public class InvoiceProcessor {
    private TaxCalculator calculator;

    public InvoiceProcessor(TaxCalculator calculator) {
        this.calculator = calculator;
    }
}

// 변경 후
public interface TaxSource {
    double calculateTax(double amount, String state);
}

public class TaxCalculator implements TaxSource {
    public double calculateTax(double amount, String state) {
        // 복잡한 세금 계산
    }
}

public class InvoiceProcessor {
    private TaxSource calculator;  // 인터페이스 타입으로 변경

    public InvoiceProcessor(TaxSource calculator) {
        this.calculator = calculator;
    }
}

// 테스트용 가짜 구현
public class FakeTaxSource implements TaxSource {
    public double calculateTax(double amount, String state) {
        return amount * 0.1;  // 단순 10% 세금
    }
}
```

---

## 12. Introduce Instance Delegator (인스턴스 위임자 도입)

### 한 줄 설명
static 메서드를 호출하는 코드에 대해, 동일한 기능의 인스턴스 메서드를 추가하여 오버라이드 가능하게 만든다.

### 적용 상황
- 코드가 **static 메서드에 의존**하고 있는데, static 메서드는 오버라이드할 수 없어 테스트에서 교체가 어려울 때

### 절차
1. static 메서드와 **동일한 시그니처의 인스턴스 메서드를 추가**한다.
2. 인스턴스 메서드에서 **static 메서드를 호출**한다.
3. 의존하는 코드를 **인스턴스 메서드를 호출하도록 변경**한다.
4. 테스트에서 **서브클래스를 만들어 인스턴스 메서드를 오버라이드**한다.

### 코드 예시

```java
// 변경 전
public class BankingServices {
    public static void transfer(Account from, Account to, double amount) {
        // 실제 이체 로직 (테스트에서 실행하면 안 됨)
    }
}

// 사용하는 코드
public class PayrollProcessor {
    public void payEmployee(Employee emp) {
        BankingServices.transfer(companyAccount, emp.getAccount(), emp.getSalary());
    }
}

// 변경 후: 인스턴스 위임자 추가
public class BankingServices {
    public static void transfer(Account from, Account to, double amount) {
        // 실제 이체 로직
    }

    // 인스턴스 위임자
    public void doTransfer(Account from, Account to, double amount) {
        transfer(from, to, amount);
    }
}

// 사용하는 코드: 인스턴스를 통해 호출
public class PayrollProcessor {
    private BankingServices bankingServices;

    public PayrollProcessor(BankingServices bankingServices) {
        this.bankingServices = bankingServices;
    }

    public void payEmployee(Employee emp) {
        bankingServices.doTransfer(companyAccount, emp.getAccount(), emp.getSalary());
    }
}
```

---

## 13. Introduce Static Setter (정적 Setter 도입)

### 한 줄 설명
싱글톤(Singleton) 패턴의 인스턴스를 테스트에서 교체할 수 있도록 static setter를 추가한다.

### 적용 상황
- **싱글톤 패턴**으로 구현된 클래스에 의존하고 있을 때
- 테스트에서 **싱글톤 인스턴스를 가짜로 교체**하고 싶을 때

### 절차
1. 싱글톤 클래스에 **인터페이스를 추출**한다 (또는 기존 메서드를 virtual로 만든다).
2. 싱글톤에 **static setter 메서드를 추가**하여 인스턴스를 교체할 수 있게 한다.
3. 테스트에서 **가짜 구현을 setter로 주입**한다.
4. 테스트 후 **원래 인스턴스를 복원**한다 (tearDown에서).

### 코드 예시

```java
// 변경 전: 교체 불가능한 싱글톤
public class PermissionManager {
    private static PermissionManager instance;

    private PermissionManager() { }

    public static PermissionManager getInstance() {
        if (instance == null) {
            instance = new PermissionManager();
        }
        return instance;
    }

    public boolean hasPermission(String userId, String permission) {
        // 데이터베이스 조회...
    }
}

// 변경 후: static setter 추가
public class PermissionManager {
    private static PermissionManager instance;

    protected PermissionManager() { }  // protected로 변경

    public static PermissionManager getInstance() {
        if (instance == null) {
            instance = new PermissionManager();
        }
        return instance;
    }

    // 테스트용 static setter
    public static void setInstance(PermissionManager manager) {
        instance = manager;
    }

    // 인스턴스 리셋 (테스트 tearDown용)
    public static void resetInstance() {
        instance = null;
    }

    public boolean hasPermission(String userId, String permission) {
        // 데이터베이스 조회...
    }
}

// 테스트
public void testAccessControl() {
    // 가짜 구현 주입
    PermissionManager fake = new PermissionManager() {
        public boolean hasPermission(String userId, String permission) {
            return true;  // 항상 허용
        }
    };
    PermissionManager.setInstance(fake);

    // 테스트 수행...

    // 원래 상태 복원
    PermissionManager.resetInstance();
}
```

> **주의**: static setter는 프로덕션 코드에서 의도치 않게 사용될 위험이 있다. 가능하다면 더 안전한 대안(Parameterize Constructor 등)을 먼저 고려하라.

---

## 14. Link Substitution (링크 대체)

### 한 줄 설명
링크 타임에 다른 구현체를 연결하여, 프로덕션 구현 대신 테스트용 구현을 사용한다.

### 적용 상황
- **C/C++ 코드**에서 특정 라이브러리나 모듈의 구현을 테스트용으로 교체하고 싶을 때
- 소스 코드를 수정하지 않고 의존성을 교체하고 싶을 때

### 절차
1. 교체하고 싶은 함수나 클래스의 **동일한 시그니처를 가진 테스트용 구현**을 작성한다.
2. 빌드 설정에서 **프로덕션 구현 대신 테스트용 구현을 링크**하도록 한다.
3. 동일한 심볼이 두 번 링크되지 않도록 **프로덕션 구현을 제외**한다.

### 코드 예시

```cpp
// production/network.cpp
void sendPacket(const Packet& packet) {
    // 실제 네트워크 전송
    socket.send(packet.serialize());
}

// test/fake_network.cpp
std::vector<Packet> sentPackets;

void sendPacket(const Packet& packet) {
    // 테스트: 전송 대신 기록
    sentPackets.push_back(packet);
}

// Makefile에서 링크 대상을 교체
# 프로덕션 빌드: production/network.o 를 링크
# 테스트 빌드: test/fake_network.o 를 링크
```

---

## 15. Parameterize Constructor (생성자 매개변수화)

### 한 줄 설명
생성자가 내부에서 직접 생성하는 객체를 매개변수로 받도록 변경하여, 테스트에서 대체 객체를 주입한다.

### 적용 상황
- 생성자에서 **의존성 객체를 직접 생성**하고 있어서, 테스트에서 해당 의존성을 교체할 수 없을 때
- **의존성 주입(Dependency Injection)** 을 도입하고 싶을 때

### 절차
1. 생성자에서 생성되는 **객체를 식별**한다.
2. 해당 객체를 **매개변수로 받는 새 생성자를 추가**한다.
3. 기존 생성자에서 **새 생성자를 호출**하여 기본 객체를 전달한다 (하위 호환성 유지).
4. 테스트에서 **가짜 객체를 매개변수로 전달**한다.

### 코드 예시

```java
// 변경 전
public class MailChecker {
    private MailReceiver receiver;

    public MailChecker() {
        this.receiver = new Pop3MailReceiver("mail.company.com");
    }
}

// 변경 후: 생성자 매개변수화
public class MailChecker {
    private MailReceiver receiver;

    // 새 생성자: 외부에서 주입 가능
    public MailChecker(MailReceiver receiver) {
        this.receiver = receiver;
    }

    // 기존 생성자: 하위 호환성 유지
    public MailChecker() {
        this(new Pop3MailReceiver("mail.company.com"));
    }
}

// 테스트
public void testCheckMail() {
    FakeMailReceiver fakeReceiver = new FakeMailReceiver();
    fakeReceiver.addMessage(new Message("test@test.com", "Hello"));

    MailChecker checker = new MailChecker(fakeReceiver);  // 가짜 주입
    checker.check();
    // ...
}
```

---

## 16. Parameterize Method (메서드 매개변수화)

### 한 줄 설명
메서드가 내부에서 직접 생성하거나 참조하는 객체를 매개변수로 받도록 변경한다.

### 적용 상황
- 메서드 내에서 **의존성 객체를 직접 생성하거나 전역 참조**를 사용할 때
- 해당 의존성을 **테스트에서 교체**하고 싶을 때

### 절차
1. 메서드 내에서 생성되거나 참조되는 **의존성 객체를 식별**한다.
2. 해당 객체를 **매개변수로 받는 새 메서드를 추가**한다.
3. 기존 메서드에서 **새 메서드를 호출**하여 기본 객체를 전달한다.
4. 테스트에서 **가짜 객체를 매개변수로 전달**한다.

### 코드 예시

```java
// 변경 전
public class MessageRouter {
    public void route(Message message) {
        // 메서드 내부에서 직접 생성
        ExternalRouter router = ExternalRouter.getInstance();
        router.send(message.getDestination(), message.getContent());
    }
}

// 변경 후
public class MessageRouter {
    // 기존 메서드: 하위 호환성 유지
    public void route(Message message) {
        route(message, ExternalRouter.getInstance());
    }

    // 새 메서드: 의존성을 매개변수로 받음
    public void route(Message message, ExternalRouter router) {
        router.send(message.getDestination(), message.getContent());
    }
}

// 테스트
public void testRouting() {
    FakeExternalRouter fakeRouter = new FakeExternalRouter();
    MessageRouter router = new MessageRouter();
    router.route(testMessage, fakeRouter);  // 가짜 라우터 주입
    assertEquals("dest@test.com", fakeRouter.getLastDestination());
}
```

---

## 17. Primitivize Parameter (매개변수 원시화)

### 한 줄 설명
복잡한 매개변수를 원시 타입(primitive)이나 단순 타입으로 변환하여, 별도 함수에서 핵심 로직을 테스트한다.

### 적용 상황
- 테스트하려는 로직이 **복잡한 객체를 매개변수로 받지만**, 실제로는 해당 객체의 **일부 원시 데이터만 사용**할 때
- 복잡한 객체를 테스트에서 생성하기 어려울 때

### 절차
1. 메서드에서 복잡한 매개변수의 **어떤 데이터를 사용하는지 파악**한다.
2. 해당 데이터를 **원시 타입 매개변수로 받는 새 메서드를 생성**한다.
3. 원래 메서드에서 **새 메서드를 호출**하며, 복잡한 객체에서 데이터를 꺼내 전달한다.
4. 새 메서드를 **독립적으로 테스트**한다.

### 코드 예시

```java
// 변경 전: 복잡한 객체를 매개변수로 받음
public class ShippingCalculator {
    public double calculateCost(Order order) {
        // order에서 사용하는 것은 weight와 destination뿐
        double weight = 0;
        for (Item item : order.getItems()) {
            weight += item.getWeight();
        }
        String zone = getZone(order.getDestination().getZipCode());
        return weight * getRate(zone);
    }
}

// 변경 후: 핵심 로직을 원시 타입으로 분리
public class ShippingCalculator {
    public double calculateCost(Order order) {
        double totalWeight = 0;
        for (Item item : order.getItems()) {
            totalWeight += item.getWeight();
        }
        return calculateCostForWeight(totalWeight,
                                       order.getDestination().getZipCode());
    }

    // 원시 타입만 받는 메서드 → 테스트 용이
    double calculateCostForWeight(double weight, String zipCode) {
        String zone = getZone(zipCode);
        return weight * getRate(zone);
    }
}

// 테스트: 복잡한 Order 객체 생성 불필요
public void testCalculateCostForWeight() {
    ShippingCalculator calc = new ShippingCalculator();
    assertEquals(25.0, calc.calculateCostForWeight(5.0, "90210"), 0.01);
}
```

---

## 18. Pull Up Feature (기능 상향 이동)

### 한 줄 설명
테스트하려는 기능을 추상 상위 클래스로 끌어올리고, 테스트용 하위 클래스를 만들어 의존성을 제거한다.

### 적용 상황
- 클래스에 테스트하려는 로직과 **테스트하기 어려운 의존성이 함께 있을 때**
- 테스트하려는 로직을 **의존성으로부터 분리**하고 싶을 때

### 절차
1. 테스트하려는 메서드를 포함하는 **추상 클래스를 생성**한다.
2. 테스트하려는 메서드를 **추상 클래스로 이동(Pull Up)** 한다.
3. 의존성이 있는 부분은 **추상 메서드로 선언**한다.
4. 기존 클래스가 **추상 클래스를 상속**하고, 추상 메서드를 구현한다.
5. 테스트에서 **추상 클래스의 다른 하위 클래스를 만들어** 추상 메서드에 가짜 구현을 제공한다.

### 코드 예시

```java
// 변경 전
public class PaymentProcessor {
    private CreditCardGateway gateway;  // 테스트 어려운 의존성

    public double calculateFee(double amount) {
        // 이 로직을 테스트하고 싶음
        double baseFee = amount * 0.029;
        if (amount > 1000) {
            baseFee += 5.00;
        }
        return baseFee;
    }

    public void process(Payment payment) {
        double fee = calculateFee(payment.getAmount());
        gateway.charge(payment.getCardNumber(), payment.getAmount() + fee);
    }
}

// 변경 후: 추상 클래스로 분리
public abstract class AbstractPaymentProcessor {
    // 테스트 가능한 로직을 상위 클래스에
    public double calculateFee(double amount) {
        double baseFee = amount * 0.029;
        if (amount > 1000) {
            baseFee += 5.00;
        }
        return baseFee;
    }

    // 의존성이 있는 부분은 추상으로
    protected abstract void chargeGateway(String cardNumber, double amount);

    public void process(Payment payment) {
        double fee = calculateFee(payment.getAmount());
        chargeGateway(payment.getCardNumber(), payment.getAmount() + fee);
    }
}

// 프로덕션 하위 클래스
public class PaymentProcessor extends AbstractPaymentProcessor {
    private CreditCardGateway gateway;

    protected void chargeGateway(String cardNumber, double amount) {
        gateway.charge(cardNumber, amount);
    }
}

// 테스트용 하위 클래스
public class TestablePaymentProcessor extends AbstractPaymentProcessor {
    protected void chargeGateway(String cardNumber, double amount) {
        // 아무것도 하지 않음
    }
}
```

---

## 19. Push Down Dependency (의존성 하향 이동)

### 한 줄 설명
테스트하기 어려운 의존성을 하위 클래스로 밀어내고, 상위 클래스에서 테스트한다.

### 적용 상황
- 클래스에 **테스트하려는 로직과 테스트하기 어려운 의존성이 같이 있을 때**
- Pull Up Feature의 반대 방향: 로직을 올리는 대신, **의존성을 내린다**

### 절차
1. 기존 클래스를 **추상 클래스로 변경**한다.
2. 테스트하기 어려운 의존성과 관련된 코드를 **추상 메서드로 만든다**.
3. **구체적 하위 클래스를 생성**하여 추상 메서드를 구현한다 (원래의 의존성 코드를 여기로 이동).
4. 기존 코드에서 클래스를 **인스턴스화하는 부분을 하위 클래스로 변경**한다.
5. 테스트에서는 **상위 클래스(추상 클래스)를 대상으로**, 의존성 없는 다른 하위 클래스를 만들어 테스트한다.

### 코드 예시

```java
// 변경 전
public class Scheduler {
    private HardwareDriver driver;  // 테스트 어려운 의존성

    public List<Task> prioritize(List<Task> tasks) {
        // 이 로직을 테스트하고 싶음
        tasks.sort(Comparator.comparing(Task::getPriority));
        return tasks;
    }

    public void execute(List<Task> tasks) {
        List<Task> sorted = prioritize(tasks);
        for (Task task : sorted) {
            driver.dispatch(task);  // 하드웨어 의존성
        }
    }
}

// 변경 후: 의존성을 하위 클래스로 밀어냄
public abstract class Scheduler {
    public List<Task> prioritize(List<Task> tasks) {
        tasks.sort(Comparator.comparing(Task::getPriority));
        return tasks;
    }

    public void execute(List<Task> tasks) {
        List<Task> sorted = prioritize(tasks);
        for (Task task : sorted) {
            dispatchTask(task);
        }
    }

    protected abstract void dispatchTask(Task task);
}

// 프로덕션 하위 클래스
public class HardwareScheduler extends Scheduler {
    private HardwareDriver driver;

    protected void dispatchTask(Task task) {
        driver.dispatch(task);
    }
}

// 테스트: 상위 클래스의 로직만 테스트
public class TestableScheduler extends Scheduler {
    protected void dispatchTask(Task task) {
        // 아무것도 하지 않음
    }
}
```

---

## 20. Replace Function with Function Pointer (함수를 함수 포인터로 교체)

### 한 줄 설명
C에서 일반 함수 호출을 함수 포인터를 통한 호출로 교체하여, 테스트에서 다른 함수로 교체한다.

### 적용 상황
- **C 언어**에서 함수에 대한 의존성을 교체하고 싶을 때
- 클래스나 인터페이스가 없어 다른 객체지향 기법을 사용할 수 없을 때

### 절차
1. 교체하고 싶은 함수의 **시그니처와 동일한 함수 포인터 타입을 선언**한다.
2. 해당 함수 포인터를 가리키는 **전역 변수를 생성**하고, 프로덕션 함수로 초기화한다.
3. 함수를 직접 호출하는 코드를 **함수 포인터를 통한 호출로 변경**한다.
4. 테스트에서 **함수 포인터에 가짜 함수를 할당**한다.

### 코드 예시

```c
// 변경 전
void send_command(int command_id, const char* data) {
    // 하드웨어와 통신
    hardware_write(COMMAND_PORT, command_id);
    hardware_write(DATA_PORT, data);
}

void process(int id) {
    // ...
    send_command(CMD_START, payload);  // 직접 호출
}

// 변경 후: 함수 포인터 도입
typedef void (*send_command_fn)(int command_id, const char* data);

// 프로덕션 구현
void real_send_command(int command_id, const char* data) {
    hardware_write(COMMAND_PORT, command_id);
    hardware_write(DATA_PORT, data);
}

// 함수 포인터 (기본값: 프로덕션 구현)
send_command_fn send_command = real_send_command;

void process(int id) {
    // ...
    send_command(CMD_START, payload);  // 함수 포인터를 통한 호출
}

// 테스트용 가짜 구현
int last_command_id = -1;
void fake_send_command(int command_id, const char* data) {
    last_command_id = command_id;  // 기록만 함
}

// 테스트
void test_process() {
    send_command = fake_send_command;  // 가짜로 교체
    process(42);
    assert(last_command_id == CMD_START);
    send_command = real_send_command;  // 복원
}
```

---

## 21. Replace Global Reference with Getter (전역 참조를 Getter로 교체)

### 한 줄 설명
전역 변수에 대한 직접 참조를 getter 메서드로 교체하여, 테스트에서 서브클래스를 통해 오버라이드한다.

### 적용 상황
- 메서드가 **전역 변수를 직접 참조**하고 있을 때
- 전역 변수의 값을 **테스트에서 제어**하고 싶을 때

### 절차
1. 전역 변수에 대한 **getter 메서드를 추가**한다.
2. 메서드 내의 전역 변수 직접 참조를 **getter 호출로 변경**한다.
3. 테스트에서 **서브클래스를 만들어 getter를 오버라이드**한다.

### 코드 예시

```java
// 변경 전
public class Authenticator {
    public boolean authenticate(String userId, String password) {
        // 전역 참조
        UserDatabase db = Application.globalDatabase;
        User user = db.findUser(userId);
        return user != null && user.checkPassword(password);
    }
}

// 변경 후
public class Authenticator {
    public boolean authenticate(String userId, String password) {
        UserDatabase db = getDatabase();  // getter를 통해 접근
        User user = db.findUser(userId);
        return user != null && user.checkPassword(password);
    }

    protected UserDatabase getDatabase() {
        return Application.globalDatabase;
    }
}

// 테스트용 서브클래스
class TestingAuthenticator extends Authenticator {
    private UserDatabase testDb;

    TestingAuthenticator(UserDatabase testDb) {
        this.testDb = testDb;
    }

    @Override
    protected UserDatabase getDatabase() {
        return testDb;
    }
}
```

---

## 22. Subclass and Override Method (서브클래스 생성 및 메서드 오버라이드)

### 한 줄 설명
테스트 대상 클래스의 서브클래스를 만들어, 테스트하기 어려운 메서드를 오버라이드한다.

### 적용 상황
- 클래스 내에 **테스트하기 어려운 의존성을 가진 메서드가 일부 있을 때**
- 해당 메서드만 **격리**하여 나머지 로직을 테스트하고 싶을 때
- **가장 기본적이고 범용적인** 의존성 해제 기법

### 절차
1. 테스트하기 어려운 동작을 하는 **메서드를 식별**한다.
2. 해당 메서드를 **protected virtual(또는 non-final)** 로 만든다.
3. **테스트용 서브클래스를 생성**한다.
4. 서브클래스에서 해당 **메서드를 오버라이드**한다.
5. 테스트에서 **서브클래스의 인스턴스를 사용**한다.

### 코드 예시

```java
// 원래 클래스
public class NotificationService {
    public void notifyUser(String userId, String message) {
        User user = findUser(userId);
        String formatted = formatMessage(user, message);
        sendEmail(user.getEmail(), formatted);  // 테스트에서 실행 곤란
        logNotification(userId, message);
    }

    protected void sendEmail(String email, String content) {
        // 실제 이메일 발송
        SmtpClient client = new SmtpClient("smtp.company.com");
        client.send(email, content);
    }

    protected void logNotification(String userId, String message) {
        // 데이터베이스에 기록
        auditDb.insert(userId, message, new Date());
    }
}

// 테스트용 서브클래스
class TestingNotificationService extends NotificationService {
    public List<String> sentEmails = new ArrayList<>();
    public List<String> loggedMessages = new ArrayList<>();

    @Override
    protected void sendEmail(String email, String content) {
        sentEmails.add(email + ": " + content);  // 기록만
    }

    @Override
    protected void logNotification(String userId, String message) {
        loggedMessages.add(userId + ": " + message);  // 기록만
    }
}

// 테스트
public void testNotifyUser() {
    TestingNotificationService service = new TestingNotificationService();
    service.notifyUser("user123", "Your order has shipped");

    assertEquals(1, service.sentEmails.size());
    assertTrue(service.sentEmails.get(0).contains("Your order has shipped"));
}
```

> Subclass and Override Method는 이 책에서 **가장 자주 사용되는 의존성 해제 기법**이다. 다른 많은 기법들(Extract and Override Call, Extract and Override Factory Method 등)이 이 기법의 변형이다.

---

## 23. Supersede Instance Variable (인스턴스 변수 대체)

### 한 줄 설명
인스턴스 변수를 교체할 수 있는 setter(또는 메서드)를 제공하여, 테스트에서 의존성을 교체한다.

### 적용 상황
- 생성자에서 **인스턴스 변수가 초기화**되는데, 해당 객체를 테스트에서 교체하고 싶을 때
- Parameterize Constructor를 적용하기 어려운 경우 (예: 생성자가 이미 매우 복잡하거나, 생성자를 수정할 수 없을 때)

### 절차
1. 교체하고 싶은 인스턴스 변수를 식별한다.
2. 해당 변수를 교체할 수 있는 **메서드(setter)를 추가**한다.
3. 테스트에서 **객체 생성 후 setter를 호출**하여 가짜 객체로 교체한다.

### 코드 예시

```java
// 변경 전
public class Engine {
    private FuelInjector injector;

    public Engine() {
        // 생성자에서 복잡한 초기화
        injector = new FuelInjector(loadCalibrationData());
        injector.calibrate();
    }
}

// 변경 후: supersede 메서드 추가
public class Engine {
    private FuelInjector injector;

    public Engine() {
        injector = new FuelInjector(loadCalibrationData());
        injector.calibrate();
    }

    // 테스트용: 인스턴스 변수를 교체할 수 있는 메서드
    void supersedeInjector(FuelInjector newInjector) {
        this.injector = newInjector;
    }
}

// 테스트
public void testEngine() {
    Engine engine = new Engine();  // 생성자는 그대로 실행
    engine.supersedeInjector(new FakeFuelInjector());  // 이후 교체
    // 테스트 수행...
}
```

> **주의**: Supersede Instance Variable은 객체가 **이미 생성된 후** 의존성을 교체하는 것이므로, 생성자에서 해당 의존성을 사용하는 로직이 이미 실행된 상태이다. 이 점을 고려해야 한다. 가능하다면 Parameterize Constructor를 우선 고려하라.

---

## 24. Template Redefinition (템플릿 재정의)

### 한 줄 설명
C++ 템플릿을 이용하여, 템플릿 매개변수로 의존성 타입을 교체한다.

### 적용 상황
- **C++ 코드**에서 클래스의 의존성을 교체하고 싶을 때
- 가상 함수(virtual function) 오버헤드를 피하고 싶을 때
- 컴파일 타임에 의존성을 교체하고 싶을 때

### 절차
1. 교체하고 싶은 의존성 타입을 **템플릿 매개변수**로 만든다.
2. 의존성 타입을 사용하는 부분을 **템플릿 매개변수로 변경**한다.
3. 프로덕션 코드에서는 **실제 타입으로 인스턴스화**한다.
4. 테스트에서는 **가짜 타입으로 인스턴스화**한다.

### 코드 예시

```cpp
// 변경 전
class OrderProcessor {
    DatabaseConnection connection;
public:
    void process(Order& order) {
        connection.save(order);  // DatabaseConnection에 직접 의존
    }
};

// 변경 후: 템플릿으로 의존성 교체 가능
template <typename ConnectionType>
class OrderProcessor {
    ConnectionType connection;
public:
    void process(Order& order) {
        connection.save(order);
    }
};

// 프로덕션 코드
using ProductionOrderProcessor = OrderProcessor<DatabaseConnection>;

// 테스트
class FakeConnection {
public:
    std::vector<Order> savedOrders;
    void save(Order& order) {
        savedOrders.push_back(order);
    }
};

void test_process() {
    OrderProcessor<FakeConnection> processor;
    Order order;
    processor.process(order);
    // 검증...
}
```

> **참고**: 이 기법은 C++에서 "정적 다형성(static polymorphism)"이라고도 불리며, 런타임 오버헤드 없이 의존성을 교체할 수 있다는 장점이 있다. 단, 템플릿은 코드가 복잡해지고 컴파일 시간이 길어질 수 있다.

---

## 25. Text Redefinition (텍스트 재정의)

### 한 줄 설명
인터프리터 언어(Ruby, Python 등)에서 클래스나 메서드를 런타임에 재정의하여 의존성을 교체한다.

### 적용 상황
- **인터프리터 언어**에서 테스트하기 어려운 메서드를 교체하고 싶을 때
- 동적 언어의 유연성을 활용하여 **런타임에 메서드를 교체**할 수 있을 때

### 절차
1. 교체하고 싶은 메서드를 식별한다.
2. 테스트 파일에서 **해당 메서드를 재정의**한다.
3. 재정의된 메서드가 **가짜 동작**을 수행하도록 한다.

### 코드 예시

Ruby:

```ruby
# 프로덕션 코드
class PaymentGateway
  def charge(account_id, amount)
    # 실제 결제 처리 (외부 API 호출)
    HttpClient.post("https://api.payment.com/charge",
                    { account: account_id, amount: amount })
  end
end

class OrderProcessor
  def process(order)
    gateway = PaymentGateway.new
    gateway.charge(order.account_id, order.total)
  end
end

# 테스트: 메서드를 재정의
class PaymentGateway
  attr_reader :last_account_id, :last_amount

  def charge(account_id, amount)
    @last_account_id = account_id
    @last_amount = amount
    # 실제 결제하지 않음
  end
end

def test_process
  processor = OrderProcessor.new
  processor.process(test_order)
  # 검증...
end
```

Python:

```python
# 프로덕션 코드
class EmailService:
    def send(self, to, subject, body):
        # 실제 이메일 발송
        smtp_client.send_mail(to, subject, body)

# 테스트: monkey patching
def test_notification():
    sent_emails = []

    def fake_send(self, to, subject, body):
        sent_emails.append((to, subject, body))

    # 메서드를 런타임에 교체
    original_send = EmailService.send
    EmailService.send = fake_send

    try:
        # 테스트 수행
        notifier = Notifier()
        notifier.notify_user("user@test.com", "Hello")
        assert len(sent_emails) == 1
    finally:
        # 원래 메서드 복원
        EmailService.send = original_send
```

> **주의**: Text Redefinition은 매우 강력하지만, 남용하면 코드의 예측 가능성이 크게 떨어진다. 테스트 목적으로만 제한적으로 사용해야 한다.

---

## 26. 기법 선택 가이드

### 26.1 의존성 유형별 적합한 기법

| 의존성 유형 | 추천 기법 |
|------------|----------|
| 매개변수가 테스트하기 어려운 타입 | Adapt Parameter, Primitivize Parameter |
| 생성자에서 객체를 직접 생성 | Parameterize Constructor, Extract and Override Factory Method |
| 메서드 내에서 객체를 직접 생성/참조 | Parameterize Method, Extract and Override Call |
| 전역 변수/함수 의존 | Encapsulate Global References, Replace Global Reference with Getter |
| 싱글톤 의존 | Introduce Static Setter, Parameterize Constructor |
| static 메서드 의존 | Introduce Instance Delegator, Expose Static Method |
| 클래스 전체의 의존성 | Extract Interface, Extract Implementer, Subclass and Override Method |
| 거대한 메서드 | Break Out Method Object |
| C/C++ 특화 | Definition Completion, Link Substitution, Template Redefinition |
| C 특화 | Replace Function with Function Pointer |
| 동적 언어 특화 | Text Redefinition |
| 상속 계층에서의 의존성 | Pull Up Feature, Push Down Dependency |

### 26.2 언어별 적용 가능한 기법

| 기법 | Java | C++ | C | Ruby/Python |
|------|------|-----|---|-------------|
| Adapt Parameter | O | O | - | O |
| Break Out Method Object | O | O | - | O |
| Definition Completion | - | O | O | - |
| Encapsulate Global References | O | O | O | O |
| Expose Static Method | O | O | - | - |
| Extract and Override Call | O | O | - | O |
| Extract and Override Factory Method | O | - | - | O |
| Extract and Override Getter | O | O | - | O |
| Extract Implementer | O | O | - | O |
| Extract Interface | O | O | - | O |
| Introduce Instance Delegator | O | O | - | O |
| Introduce Static Setter | O | O | - | O |
| Link Substitution | - | O | O | - |
| Parameterize Constructor | O | O | - | O |
| Parameterize Method | O | O | O | O |
| Primitivize Parameter | O | O | O | O |
| Pull Up Feature | O | O | - | O |
| Push Down Dependency | O | O | - | O |
| Replace Function with Function Pointer | - | - | O | - |
| Replace Global Reference with Getter | O | O | - | O |
| Subclass and Override Method | O | O | - | O |
| Supersede Instance Variable | O | O | - | O |
| Template Redefinition | - | O | - | - |
| Text Redefinition | - | - | - | O |

### 26.3 상황별 빠른 선택

```
테스트를 작성하려는데 의존성이 방해한다
├── 어떤 종류의 의존성인가?
│   ├── 매개변수 → Adapt Parameter 또는 Primitivize Parameter
│   ├── 생성자에서 생성되는 객체 → Parameterize Constructor
│   ├── 메서드 내부의 호출 → Extract and Override Call
│   ├── 전역 변수/싱글톤 → Replace Global Reference with Getter
│   └── 클래스 자체 → Extract Interface 또는 Subclass and Override Method
├── 간단하게 해결하고 싶다
│   └── Subclass and Override Method (가장 범용적)
└── 근본적으로 해결하고 싶다
    └── Extract Interface + Parameterize Constructor (의존성 주입)
```

---

## 요약

- 이 장은 **24가지 의존성 해제 기법**을 카탈로그 형태로 정리한 레퍼런스이다.
- 각 기법은 **특정 유형의 의존성 문제를 해결**하기 위해 설계되었다.
- **Subclass and Override Method**가 가장 범용적이고 자주 사용되는 기법이다.
- **Parameterize Constructor**와 **Extract Interface**는 의존성 주입의 기본 패턴이다.
- **Extract and Override Call**은 메서드 내부의 특정 호출만 격리할 때 효과적이다.
- C/C++ 환경에서는 **Definition Completion, Link Substitution, Template Redefinition** 등 언어 특화 기법을 활용한다.
- 동적 언어에서는 **Text Redefinition**으로 런타임에 메서드를 재정의할 수 있다.
- 의존성의 유형과 상황에 따라 **적절한 기법을 선택**하는 것이 중요하며, 여러 기법을 조합하여 사용하는 경우도 많다.

---

## 부록과의 연결

이 장은 책의 마지막 본문 장이다. 이후의 부록에서는 리팩토링 기법에 대한 추가 참조 자료와, 이 책에서 다룬 기법들을 실제 프로젝트에 적용할 때 참고할 수 있는 정보를 제공한다. 이 장의 24가지 의존성 해제 기법은 이전 장들에서 "의존성을 해제하라"고 언급될 때마다 구체적으로 어떻게 해야 하는지를 알려주는 실전 도구 상자(toolbox)이다.
