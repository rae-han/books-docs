# Chapter 9: 뚝딱! 테스트 하네스에 클래스 제대로 넣기 (I Can't Get This Class into a Test Harness)

## 핵심 질문

클래스를 테스트 하네스에서 인스턴스화할 수 없는 네 가지 주요 원인은 무엇이며, 각각을 어떻게 해결하여 테스트 가능한 상태로 만들 수 있는가?

---

## 1. 클래스를 테스트 하네스에 넣기 어려운 이유

레거시 코드에서 테스트를 작성하려 할 때 가장 먼저 부딪히는 벽은 **"클래스의 객체를 테스트 코드에서 생성할 수 없다"** 는 문제이다. 프로덕션 코드에서는 잘 동작하는 클래스가 테스트 환경에서는 생성조차 되지 않는 경우가 허다하다.

Feathers는 이 문제의 네 가지 주요 원인을 식별한다:

| 원인 | 설명 | 증상 |
|------|------|------|
| **생성자의 복잡한 의존성** | 생성자가 생성하기 어려운 객체를 요구 | DB 연결, 서블릿 컨텍스트 등이 필요 |
| **생성자에서 많은 일을 함** | 생성자가 부수 효과를 일으킴 | 파일 쓰기, 네트워크 연결, DB 접근 |
| **숨겨진 의존성** | 내부에서 직접 의존 객체를 생성 | `new`로 직접 생성, 테스트에서 교체 불가 |
| **전역 의존성 (싱글톤)** | 전역 상태에 의존 | `Singleton.getInstance()` 호출 |

이 장은 책에서 가장 **실전적이고 구체적인 챕터** 중 하나로, 각 문제에 대한 상세한 코드 예시와 해결 기법을 제시한다.

---

## 2. 문제 1: 생성자의 복잡한 의존성

### 2.1 문제 상황

```java
public class InvoiceUpdateResponder {
    private InvoiceUpdateServlet servlet;
    private DBConnection connection;

    public InvoiceUpdateResponder(InvoiceUpdateServlet servlet,
                                   DBConnection connection) {
        this.servlet = servlet;
        this.connection = connection;
    }

    public String getContent() {
        Invoice invoice = servlet.getInvoice();
        // connection을 사용한 처리...
        return invoice.format();
    }
}
```

이 클래스를 테스트하려면 `InvoiceUpdateServlet`과 `DBConnection` 객체가 필요하다. 그런데:
- `InvoiceUpdateServlet`은 서블릿 컨테이너에서만 생성 가능하다.
- `DBConnection`은 실제 데이터베이스 연결이 필요하다.

### 2.2 해결: Extract Interface (인터페이스 추출)

의존 객체의 인터페이스를 추출하여, 테스트에서 **가짜 객체(fake object)** 를 주입할 수 있게 한다.

**1단계: 필요한 메서드만 포함하는 인터페이스를 추출한다**

```java
// InvoiceUpdateServlet에서 실제로 사용하는 메서드만 인터페이스로 추출
public interface InvoiceSource {
    Invoice getInvoice();
}

// 기존 클래스가 인터페이스를 구현
public class InvoiceUpdateServlet implements InvoiceSource {
    public Invoice getInvoice() {
        // 실제 서블릿 구현...
    }
}
```

**2단계: 의존하는 클래스가 인터페이스를 사용하도록 변경한다**

```java
public class InvoiceUpdateResponder {
    private InvoiceSource source;         // 인터페이스에 의존
    private DBConnection connection;

    public InvoiceUpdateResponder(InvoiceSource source,
                                   DBConnection connection) {
        this.source = source;
        this.connection = connection;
    }

    public String getContent() {
        Invoice invoice = source.getInvoice();
        return invoice.format();
    }
}
```

**3단계: 테스트에서 가짜 객체를 만들어 주입한다**

```java
// 테스트용 가짜 구현
public class FakeInvoiceSource implements InvoiceSource {
    private Invoice invoice;

    public FakeInvoiceSource(Invoice invoice) {
        this.invoice = invoice;
    }

    public Invoice getInvoice() {
        return invoice;
    }
}

// 테스트 코드
public void testGetContent() {
    Invoice testInvoice = new Invoice("INV-001", 1000);
    InvoiceSource fakeSource = new FakeInvoiceSource(testInvoice);
    DBConnection fakeConnection = new FakeDBConnection();

    InvoiceUpdateResponder responder =
        new InvoiceUpdateResponder(fakeSource, fakeConnection);

    String content = responder.getContent();
    assertTrue(content.contains("INV-001"));
}
```

### 2.3 Extract Interface의 핵심 원칙

- **모든 메서드를 인터페이스에 넣지 않는다**: 테스트에서 실제로 필요한 메서드만 포함한다.
- **인터페이스 이름은 역할을 반영**한다: `InvoiceUpdateServlet`의 인터페이스는 `InvoiceSource`처럼 역할 기반 이름을 사용한다.
- **점진적으로 적용**한다: 한 번에 모든 의존성의 인터페이스를 추출할 필요 없이, 테스트에 필요한 것부터 하나씩 추출한다.

---

## 3. 문제 2: 생성자에서 많은 일을 하는 경우

### 3.1 문제 상황

```java
public class CreditValidator {
    private RGHConnection connection;
    private CreditMaster master;

    public CreditValidator(RGHConnection connection,
                           CreditMaster master,
                           String validatorID) {
        this.connection = connection;
        this.master = master;

        // 생성자에서 많은 일을 함!
        Certificate cert = CertificateAuthority.getCertificate(
            connection, validatorID);
        if (cert.isExpired()) {
            throw new InvalidCertificateException("Certificate expired");
        }
        connection.authenticate(cert);
        // 데이터베이스 초기화, 캐시 워밍업 등...
    }
}
```

이 생성자는:
- 인증서를 가져와서 유효성을 검증한다.
- 네트워크 연결을 인증한다.
- 객체 생성 자체에 부수 효과(side effect)가 있다.

테스트에서 이 객체를 생성하면 **실제 네트워크 연결이 시도되고, 인증서 서버에 접근**하려 한다.

### 3.2 해결: Parameterize Constructor (생성자 매개변수화)

생성자가 내부에서 직접 생성하는 객체를 **외부에서 매개변수로 받을 수 있게** 변경한다.

```java
public class CreditValidator {
    private RGHConnection connection;
    private CreditMaster master;
    private Certificate certificate;

    // 새로운 생성자: 인증서를 외부에서 주입
    public CreditValidator(RGHConnection connection,
                           CreditMaster master,
                           Certificate certificate) {
        this.connection = connection;
        this.master = master;
        this.certificate = certificate;
    }

    // 기존 생성자는 새 생성자를 호출 (하위 호환성 유지)
    public CreditValidator(RGHConnection connection,
                           CreditMaster master,
                           String validatorID) {
        this(connection, master,
             CertificateAuthority.getCertificate(connection, validatorID));
        // 추가 초기화...
    }
}
```

테스트에서는 새 생성자를 사용한다:

```java
public void testValidateCredit() {
    FakeRGHConnection connection = new FakeRGHConnection();
    CreditMaster master = new CreditMaster("test-data");
    Certificate fakeCert = new FakeCertificate(/* 유효한 테스트 인증서 */);

    CreditValidator validator =
        new CreditValidator(connection, master, fakeCert);

    // 이제 네트워크 접근 없이 테스트 가능
    assertTrue(validator.validateCredit(1000));
}
```

### 3.3 Parameterize Constructor의 핵심

- **기존 생성자를 유지**하면서 새 생성자를 추가한다 → 기존 프로덕션 코드의 변경이 최소화된다.
- 새 생성자는 **의존 객체를 외부에서 주입**받는다 → 테스트에서 가짜 객체 사용 가능.
- 기존 생성자가 새 생성자를 **위임 호출(delegation)** 하도록 만든다.

---

## 4. 문제 3: 숨겨진 의존성 (Hidden Dependencies)

### 4.1 문제 상황

```java
public class PayrollCalculator {
    private TaxCalculator taxCalc;
    private BenefitsCalculator benefitsCalc;

    public PayrollCalculator() {
        // 생성자 내부에서 직접 의존 객체를 생성 - 숨겨진 의존성!
        this.taxCalc = new TaxCalculator();
        this.benefitsCalc = new BenefitsCalculator(
            DatabaseConnectionManager.getConnection());
    }

    public Money calculatePay(Employee employee) {
        Money gross = employee.getGrossPay();
        Money tax = taxCalc.calculateTax(gross);
        Money benefits = benefitsCalc.calculateDeductions(employee);
        return gross.subtract(tax).subtract(benefits);
    }
}
```

`PayrollCalculator`의 생성자 시그니처만 보면 매개변수가 없어서 쉽게 생성할 수 있을 것 같지만, 내부에서 `TaxCalculator`와 `BenefitsCalculator`를 직접 생성한다. `BenefitsCalculator`는 데이터베이스 연결까지 필요로 한다. 이것이 **숨겨진 의존성**이다.

### 4.2 해결: Extract and Override (추출 후 오버라이드)

의존 객체를 생성하는 코드를 **별도 메서드로 추출**하고, 테스트에서 그 메서드를 **오버라이드**한다.

**1단계: 의존 객체 생성 코드를 메서드로 추출한다**

```java
public class PayrollCalculator {
    private TaxCalculator taxCalc;
    private BenefitsCalculator benefitsCalc;

    public PayrollCalculator() {
        this.taxCalc = createTaxCalculator();
        this.benefitsCalc = createBenefitsCalculator();
    }

    // 추출된 팩토리 메서드들
    protected TaxCalculator createTaxCalculator() {
        return new TaxCalculator();
    }

    protected BenefitsCalculator createBenefitsCalculator() {
        return new BenefitsCalculator(
            DatabaseConnectionManager.getConnection());
    }

    public Money calculatePay(Employee employee) {
        Money gross = employee.getGrossPay();
        Money tax = taxCalc.calculateTax(gross);
        Money benefits = benefitsCalc.calculateDeductions(employee);
        return gross.subtract(tax).subtract(benefits);
    }
}
```

**2단계: 테스트에서 서브클래스를 만들어 팩토리 메서드를 오버라이드한다**

```java
// 테스트용 서브클래스
public class TestingPayrollCalculator extends PayrollCalculator {

    @Override
    protected TaxCalculator createTaxCalculator() {
        return new FakeTaxCalculator();  // 가짜 객체 반환
    }

    @Override
    protected BenefitsCalculator createBenefitsCalculator() {
        return new FakeBenefitsCalculator();  // 가짜 객체 반환
    }
}

// 테스트 코드
public void testCalculatePay() {
    PayrollCalculator calculator = new TestingPayrollCalculator();
    Employee employee = new Employee("John", new Money(5000));

    Money pay = calculator.calculatePay(employee);

    assertEquals(new Money(3500), pay);  // 세금과 공제 후 금액
}
```

### 4.3 Extract and Override의 변형들

**Extract and Override Factory Method** (위의 예시): 객체 생성 코드를 추출하여 오버라이드한다.

**Extract and Override Getter**: getter를 통해 의존 객체에 접근하도록 하고, getter를 오버라이드한다.

```java
public class PayrollCalculator {
    private TaxCalculator taxCalc;

    public PayrollCalculator() {
        this.taxCalc = new TaxCalculator();
    }

    // getter를 통해 접근
    protected TaxCalculator getTaxCalculator() {
        return taxCalc;
    }

    public Money calculatePay(Employee employee) {
        Money gross = employee.getGrossPay();
        Money tax = getTaxCalculator().calculateTax(gross);  // getter 사용
        return gross.subtract(tax);
    }
}
```

```java
// 테스트용 서브클래스
public class TestingPayrollCalculator extends PayrollCalculator {
    private TaxCalculator fakeTaxCalc = new FakeTaxCalculator();

    @Override
    protected TaxCalculator getTaxCalculator() {
        return fakeTaxCalc;  // 가짜 객체 반환
    }
}
```

### 4.4 Extract and Override의 핵심

- 기존 클래스의 변경이 **매우 작다** (메서드 추출과 접근 제어자 변경 정도).
- 프로덕션 코드의 **동작은 전혀 바뀌지 않는다**.
- 테스트용 서브클래스에서 **원하는 의존성만 교체**할 수 있다.
- C++에서는 virtual 메서드로 선언해야 오버라이드가 가능하다.

---

## 5. 문제 4: 전역 의존성 - 싱글톤 문제

### 5.1 싱글톤이 테스트를 어렵게 만드는 이유

```java
public class PermitRepository {
    private static PermitRepository instance;

    // private 생성자: 외부에서 인스턴스 생성 불가
    private PermitRepository() {
        // 데이터베이스 연결, 캐시 초기화 등
    }

    // 전역 접근점
    public static PermitRepository getInstance() {
        if (instance == null) {
            instance = new PermitRepository();
        }
        return instance;
    }

    public Permit getPermit(String id) {
        // 데이터베이스에서 조회
    }
}
```

이 싱글톤을 사용하는 클래스:

```java
public class PermitValidator {
    public boolean validate(String permitId) {
        Permit permit = PermitRepository.getInstance().getPermit(permitId);
        return permit != null && !permit.isExpired();
    }
}
```

`PermitValidator`를 테스트하려면 `PermitRepository`가 필요한데:
- **생성자가 private**이므로 새 인스턴스를 만들 수 없다.
- `getInstance()`는 **항상 같은 인스턴스**를 반환한다.
- 그 인스턴스는 **실제 데이터베이스에 연결**된다.
- 테스트 간에 **상태가 공유**되어 테스트 격리가 안 된다.

### 5.2 해결: Introduce Static Setter (정적 setter 도입)

싱글톤의 제약을 **완화**하여 테스트에서 인스턴스를 교체할 수 있게 한다.

**1단계: 인터페이스를 추출한다**

```java
public interface PermitSource {
    Permit getPermit(String id);
}
```

**2단계: 싱글톤 클래스가 인터페이스를 구현하고, 정적 setter를 추가한다**

```java
public class PermitRepository implements PermitSource {
    private static PermitSource instance;

    private PermitRepository() {
        // 실제 초기화...
    }

    public static PermitSource getInstance() {
        if (instance == null) {
            instance = new PermitRepository();
        }
        return instance;
    }

    // 테스트용 정적 setter
    public static void setInstance(PermitSource newInstance) {
        instance = newInstance;
    }

    // 테스트 후 정리를 위한 메서드
    public static void resetInstance() {
        instance = null;
    }

    public Permit getPermit(String id) {
        // 실제 구현...
    }
}
```

**3단계: 테스트에서 가짜 인스턴스를 주입한다**

```java
public class FakePermitRepository implements PermitSource {
    private Map<String, Permit> permits = new HashMap<>();

    public void addPermit(String id, Permit permit) {
        permits.put(id, permit);
    }

    public Permit getPermit(String id) {
        return permits.get(id);
    }
}

// 테스트 코드
public class PermitValidatorTest extends TestCase {

    protected void setUp() {
        // 가짜 리포지토리 주입
        FakePermitRepository fakeRepo = new FakePermitRepository();
        fakeRepo.addPermit("P-001", new Permit("P-001", false));
        PermitRepository.setInstance(fakeRepo);
    }

    protected void tearDown() {
        // 테스트 후 정리
        PermitRepository.resetInstance();
    }

    public void testValidPermit() {
        PermitValidator validator = new PermitValidator();
        assertTrue(validator.validate("P-001"));
    }

    public void testInvalidPermit() {
        PermitValidator validator = new PermitValidator();
        assertFalse(validator.validate("NON-EXISTENT"));
    }
}
```

### 5.3 싱글톤 패턴 완화에 대한 고려사항

> 싱글톤에 setter를 추가하는 것은 캡슐화를 깨뜨리는 것처럼 보인다. 하지만 테스트 불가능한 코드를 방치하는 것보다는 낫다.

Feathers는 이에 대해 실용적인 입장을 취한다:

- **이상적으로는** 싱글톤 자체를 제거하고 의존성 주입으로 전환해야 한다.
- 하지만 **당장은** setter를 추가해서 테스트를 가능하게 만드는 것이 현실적이다.
- setter는 **테스트 인프라의 일부**로 간주한다.
- 프로덕션 코드에서 setter를 호출하지 않도록 **팀 규칙**으로 관리한다.

### 5.4 더 나은 방향: 싱글톤에서 의존성 주입으로

시간이 허락할 때, 싱글톤 의존성을 **생성자 주입으로 전환**하는 것이 최종 목표이다:

```java
// 최종 목표: 의존성 주입
public class PermitValidator {
    private PermitSource permitSource;

    public PermitValidator(PermitSource permitSource) {
        this.permitSource = permitSource;
    }

    public boolean validate(String permitId) {
        Permit permit = permitSource.getPermit(permitId);
        return permit != null && !permit.isExpired();
    }
}
```

이렇게 되면 싱글톤의 setter가 더 이상 필요 없고, 테스트도 더 깔끔해진다.

---

## 6. 추가 기법: Supersede Instance Variable (인스턴스 변수 대체)

### 6.1 개념

Supersede Instance Variable는 **객체 생성 후에 인스턴스 변수를 교체할 수 있는 메서드를 제공**하는 기법이다. 생성자에서 의존 객체가 만들어지지만, 나중에 **테스트용으로 교체**할 수 있게 한다.

### 6.2 예시

```java
public class MessageProcessor {
    private Dispatcher dispatcher;

    public MessageProcessor() {
        this.dispatcher = new ProductionDispatcher();
    }

    // Supersede Instance Variable: 테스트에서 dispatcher를 교체할 수 있게 함
    void supersedeDispatcher(Dispatcher newDispatcher) {
        this.dispatcher = newDispatcher;
    }

    public void process(Message message) {
        dispatcher.dispatch(message);
    }
}
```

```java
// 테스트 코드
public void testProcess() {
    MessageProcessor processor = new MessageProcessor();
    FakeDispatcher fakeDispatcher = new FakeDispatcher();
    processor.supersedeDispatcher(fakeDispatcher);  // 의존 객체 교체

    processor.process(new Message("Hello"));

    assertEquals("Hello", fakeDispatcher.getLastMessage().getContent());
}
```

### 6.3 주의사항

이 기법은 **Extract and Override보다 덜 선호**된다:

- 객체가 **일시적으로 잘못된 상태**에 놓인다 (생성 직후, supersede 호출 전까지 프로덕션 의존 객체가 사용됨).
- 생성자에서 의존 객체를 사용하는 로직이 있다면, supersede 전에 **이미 부수 효과가 발생**했을 수 있다.
- **C++에서는 특히 주의**가 필요하다: 생성자에서 할당한 메모리를 supersede로 교체하면 메모리 누수가 발생할 수 있다.

Supersede Instance Variable는 다른 기법이 적용하기 어려울 때의 **최후의 수단**으로 사용한다.

---

## 7. C++ 특유의 문제와 해결

### 7.1 C++에서의 인터페이스 추출

C++에는 Java의 `interface` 키워드가 없으므로, **순수 가상 클래스(pure virtual class)** 로 인터페이스를 표현한다:

```cpp
// C++에서의 인터페이스
class PermitSource {
public:
    virtual ~PermitSource() {}
    virtual Permit getPermit(const std::string& id) = 0;
};

class PermitRepository : public PermitSource {
public:
    Permit getPermit(const std::string& id) override {
        // 실제 구현
    }
};

// 테스트용 가짜 구현
class FakePermitSource : public PermitSource {
public:
    Permit getPermit(const std::string& id) override {
        return testPermit;  // 테스트 데이터 반환
    }
private:
    Permit testPermit;
};
```

### 7.2 C++에서 Extract and Override 시 주의사항

C++에서는 **생성자에서 가상 함수 호출이 동적 바인딩되지 않는다**:

```cpp
class Base {
public:
    Base() {
        initialize();  // 주의! 여기서 Derived::initialize()가 호출되지 않음
    }
    virtual void initialize() {
        // Base 버전이 항상 호출됨
    }
};

class Derived : public Base {
public:
    void initialize() override {
        // 생성자에서는 이 버전이 호출되지 않음!
    }
};
```

따라서 C++에서 Extract and Override를 사용할 때는 **생성자 밖에서 초기화 메서드를 호출하는 구조**로 변경해야 할 수 있다.

---

## 8. 각 기법의 비교와 선택 기준

| 기법 | 적합한 상황 | 기존 코드 변경 정도 | 안전성 |
|------|------------|-------------------|--------|
| **Extract Interface** | 생성자 매개변수의 타입이 문제일 때 | 인터페이스 추가, 타입 변경 | 높음 |
| **Parameterize Constructor** | 생성자 내부에서 객체를 직접 생성할 때 | 새 생성자 추가 | 높음 |
| **Extract and Override** | 숨겨진 의존성이 있을 때 | 메서드 추출, protected 변경 | 중간 |
| **Supersede Instance Variable** | 다른 기법 적용이 어려울 때 | setter 추가 | 낮음 |
| **Introduce Static Setter** | 싱글톤 의존성이 있을 때 | 정적 setter 추가 | 중간 |

### 8.1 선택 가이드

```
클래스를 테스트에서 생성할 수 없다
├── 생성자 매개변수를 만들 수 없는가?
│   └── YES → Extract Interface로 인터페이스 추출
│             → 가짜 객체를 매개변수로 전달
│
├── 생성자 내부에서 문제가 발생하는가?
│   ├── 내부에서 객체를 직접 생성하는가?
│   │   └── YES → Parameterize Constructor
│   │             또는 Extract and Override Factory Method
│   │
│   └── 생성자가 부수 효과를 일으키는가?
│       └── YES → Extract and Override로 부수 효과 격리
│                 또는 Supersede Instance Variable (최후 수단)
│
└── 전역 상태 / 싱글톤에 의존하는가?
    └── YES → Introduce Static Setter
              → 장기적으로는 의존성 주입으로 전환
```

---

## 9. 실전 예시: 복합적인 문제 해결

실제 레거시 코드에서는 여러 문제가 **동시에 존재**하는 경우가 흔하다. 다음은 복합적인 문제를 단계적으로 해결하는 예시이다:

### 9.1 문제의 클래스

```java
public class ReportGenerator {
    private DatabaseConnection db;
    private TemplateEngine engine;
    private static ReportGenerator instance;

    private ReportGenerator() {
        // 숨겨진 의존성: 내부에서 직접 생성
        this.db = new DatabaseConnection("prod-server:5432");
        this.engine = TemplateEngine.getInstance();  // 또 다른 싱글톤
    }

    public static ReportGenerator getInstance() {
        if (instance == null) {
            instance = new ReportGenerator();
        }
        return instance;
    }

    public String generate(String reportType) {
        ResultSet data = db.query("SELECT * FROM " + reportType);
        return engine.render(reportType + ".tmpl", data);
    }
}
```

이 클래스에는 **세 가지 문제가 동시에** 존재한다:
1. 싱글톤 (전역 의존성)
2. 숨겨진 의존성 (`DatabaseConnection`을 내부에서 직접 생성)
3. 다른 싱글톤에 의존 (`TemplateEngine.getInstance()`)

### 9.2 단계적 해결

**1단계: Introduce Static Setter로 싱글톤 완화**

```java
public class ReportGenerator {
    // ...
    public static void setInstanceForTesting(ReportGenerator newInstance) {
        instance = newInstance;
    }
    public static void resetInstance() {
        instance = null;
    }
}
```

**2단계: Parameterize Constructor로 숨겨진 의존성 제거**

```java
public class ReportGenerator {
    private DatabaseConnection db;
    private TemplateEngine engine;

    // 테스트용 생성자 추가
    protected ReportGenerator(DatabaseConnection db, TemplateEngine engine) {
        this.db = db;
        this.engine = engine;
    }

    private ReportGenerator() {
        this(new DatabaseConnection("prod-server:5432"),
             TemplateEngine.getInstance());
    }
    // ...
}
```

**3단계: Extract Interface로 의존 타입 추상화**

```java
public interface DataSource {
    ResultSet query(String sql);
}

public interface Renderer {
    String render(String template, ResultSet data);
}

// 테스트용 생성자
protected ReportGenerator(DataSource db, Renderer engine) {
    this.db = db;
    this.engine = engine;
}
```

**4단계: 테스트 작성**

```java
public void testGenerate() {
    FakeDataSource fakeDb = new FakeDataSource();
    fakeDb.addResult("SELECT * FROM sales", testResultSet);
    FakeRenderer fakeRenderer = new FakeRenderer();
    fakeRenderer.setResult("Expected Report Content");

    ReportGenerator generator = new ReportGenerator(fakeDb, fakeRenderer);

    String report = generator.generate("sales");
    assertEquals("Expected Report Content", report);
}
```

---

## 요약

- 클래스를 테스트 하네스에 넣기 어려운 네 가지 주요 원인: **복잡한 생성자 의존성**, **생성자의 과도한 작업**, **숨겨진 의존성**, **전역/싱글톤 의존성**.
- **Extract Interface**: 구체 클래스 의존성을 인터페이스로 바꿔 가짜 객체를 주입할 수 있게 한다.
- **Parameterize Constructor**: 생성자 내부에서 생성하던 객체를 매개변수로 받도록 변경한다.
- **Extract and Override**: 의존 객체 생성 코드를 메서드로 추출하고, 테스트 서브클래스에서 오버라이드한다.
- **Supersede Instance Variable**: 인스턴스 변수를 교체할 수 있는 메서드를 제공한다 (최후의 수단).
- **Introduce Static Setter**: 싱글톤에 테스트용 setter를 추가하여 인스턴스를 교체 가능하게 한다.
- 실제 레거시 코드에서는 **여러 문제가 복합적으로** 존재하며, 기법들을 **조합하여 단계적으로** 해결해야 한다.
- 모든 기법의 궁극적 목표는 **테스트를 작성할 수 있는 상태**를 만드는 것이며, 그 후에 점진적으로 설계를 개선한다.

---

## 다음 챕터와의 연결

Chapter 10 **"이 메서드에서 테스트를 실행할 수 없다 (I Can't Run This Method in a Test Harness)"** 에서는 클래스를 인스턴스화할 수 있게 되었더라도, **특정 메서드를 호출하는 것이 어려운 경우** (private 메서드, 부수 효과가 큰 메서드 등)에 대한 해결 기법을 소개한다.
