# Chapter 27: Testing Patterns (테스팅 패턴)

## 핵심 질문

테스트를 더 효과적으로 작성하기 위한 구체적인 기법에는 어떤 것들이 있는가? 테스트가 너무 복잡해지면 어떻게 하는가? 외부 의존성이 있는 코드는 어떻게 테스트하는가? 작업을 중단하고 재개할 때 어떻게 해야 하는가?

---

## 1. 이 챕터의 위치와 역할

Chapter 25가 "TDD의 메타-패턴"을, Chapter 26이 "Red Bar를 만드는 패턴"을 다루었다면, Chapter 27은 **테스트 작성의 구체적인 기법**을 다룬다. 여기서 다루는 패턴들은 테스트의 설계와 구조에 관한 것으로, 실무에서 자주 부딪히는 문제에 대한 해결책이다.

이 챕터에서 다루는 7개 패턴:

| 패턴 | 핵심 질문 |
|------|----------|
| Child Test | 테스트가 너무 크면 어떻게 하는가? |
| Mock Object | 느리거나 복잡한 외부 의존성을 어떻게 테스트하는가? |
| Self Shunt | 테스트 객체와 목(mock) 객체를 어떻게 결합하는가? |
| Log String | 메서드 호출 순서를 어떻게 검증하는가? |
| Crash Test Dummy | 에러 처리 코드를 어떻게 테스트하는가? |
| Broken Test | 작업을 중단할 때 어떻게 해야 하는가? |
| Clean Check-in | 코드를 저장소에 커밋할 때 어떤 상태여야 하는가? |

---

## 2. Child Test (자식 테스트)

### 문제

테스트를 작성했는데, 이 테스트를 통과시키려면 너무 많은 코드를 한 번에 작성해야 한다. Red Bar에서 Green Bar까지의 거리가 너무 멀다.

### 패턴

**큰 테스트를 더 작은 테스트들로 분해한다.** 큰 테스트가 나타내는 문제의 부분 집합을 테스트하는 작은 테스트(자식 테스트)를 먼저 작성하고, 이 자식 테스트들을 하나씩 통과시킨다. 모든 자식 테스트가 통과하면, 원래의 큰 테스트도 통과할 수 있게 된다.

### 설명

Child Test의 절차:

1. 큰 테스트를 작성한다 (또는 이미 존재하는 큰 테스트가 실패한다)
2. 이 테스트가 실패하는 원인을 분석한다
3. 원인 중 가장 작은 부분을 다루는 **자식 테스트**를 작성한다
4. 자식 테스트를 통과시킨다
5. 다음 자식 테스트를 작성한다
6. 모든 자식 테스트가 통과하면, 원래 큰 테스트를 다시 시도한다

### 예시

```java
// 원래의 큰 테스트 — 이것을 한 번에 통과시키기 어렵다
public void testOrderTotal() {
    Order order = new Order();
    order.addItem(new Item("Widget", 25.00, 3));    // 25 × 3 = 75
    order.addItem(new Item("Gadget", 10.00, 2));    // 10 × 2 = 20
    order.setTaxRate(0.1);                            // 세금 10%
    order.setDiscount(0.05);                          // 할인 5%
    assertEquals(99.275, order.getTotal(), 0.001);
    // (75 + 20) × (1 - 0.05) × (1 + 0.1) = 95 × 0.95 × 1.1 = ...
}
```

이 테스트를 통과시키려면 Item 클래스, 소계 계산, 할인 적용, 세금 계산이 모두 한꺼번에 필요하다. Child Test로 분해한다:

```java
// 자식 테스트 1: 아이템의 소계 계산
public void testItemSubtotal() {
    Item item = new Item("Widget", 25.00, 3);
    assertEquals(75.00, item.getSubtotal(), 0.001);
}

// 자식 테스트 2: 주문의 소계 (여러 아이템의 합)
public void testOrderSubtotal() {
    Order order = new Order();
    order.addItem(new Item("Widget", 25.00, 3));  // 75
    order.addItem(new Item("Gadget", 10.00, 2));  // 20
    assertEquals(95.00, order.getSubtotal(), 0.001);
}

// 자식 테스트 3: 할인 적용
public void testOrderWithDiscount() {
    Order order = new Order();
    order.addItem(new Item("Widget", 100.00, 1));
    order.setDiscount(0.1);  // 10% 할인
    assertEquals(90.00, order.getDiscountedTotal(), 0.001);
}

// 자식 테스트 4: 세금 적용
public void testOrderWithTax() {
    Order order = new Order();
    order.addItem(new Item("Widget", 100.00, 1));
    order.setTaxRate(0.1);  // 10% 세금
    assertEquals(110.00, order.getTotal(), 0.001);
}
```

각 자식 테스트는 한 가지 기능만 검증하며, 한 번에 통과시킬 수 있다.

> **핵심 통찰**: Child Test는 Chapter 26의 One Step Test와 연결된다. 테스트가 "한 걸음" 이상을 요구하면, 그 걸음을 여러 개의 작은 걸음으로 나눈다. 큰 테스트를 작성한 것 자체는 실수가 아니다 — 그것은 목적지를 설정한 것이다. 실수는 그 큰 테스트를 한 번에 통과시키려 하는 것이다.

---

## 3. Mock Object (목 객체)

### 문제

테스트 대상 코드가 데이터베이스, 네트워크, 파일 시스템 등 **느리거나 비결정적인 외부 자원**에 의존한다. 이런 코드를 어떻게 빠르고 안정적으로 테스트하는가?

### 패턴

**실제 객체 대신, 예측 가능한 동작을 하는 가짜 객체(Mock Object)를 만들어 사용한다.** 목 객체는 실제 객체와 같은 인터페이스를 구현하지만, 미리 정해진 값을 반환하거나 호출 기록을 남긴다.

### 설명

실제 데이터베이스를 사용하는 테스트의 문제점:

| 문제 | 영향 |
|------|------|
| 느리다 (네트워크 접속, 디스크 I/O) | 테스트 실행 시간 증가 → TDD 리듬 깨짐 |
| 비결정적이다 (데이터가 변할 수 있음) | 같은 테스트가 때로는 통과, 때로는 실패 |
| 설정이 복잡하다 (스키마, 초기 데이터) | 테스트 작성이 번거로움 |
| 다른 테스트에 영향을 줄 수 있다 | Isolated Test 원칙 위반 |

Mock Object는 이 모든 문제를 해결한다:

```java
// 실제 DB를 사용하는 코드
public class OrderService {
    private Database db;

    public OrderService(Database db) {
        this.db = db;
    }

    public Order findOrder(String id) {
        ResultSet rs = db.query("SELECT * FROM orders WHERE id = ?", id);
        return new Order(rs.getString("name"), rs.getDouble("total"));
    }
}
```

```java
// Mock을 사용한 테스트
public void testFindOrder() {
    // Mock DB 생성 — 실제 DB 없이 동작
    MockDatabase mockDb = new MockDatabase();
    mockDb.setupResult("SELECT * FROM orders WHERE id = ?",
        new MockResultSet("Widget Order", 99.95));

    OrderService service = new OrderService(mockDb);
    Order order = service.findOrder("123");

    assertEquals("Widget Order", order.getName());
    assertEquals(99.95, order.getTotal(), 0.001);
}
```

Mock Object의 핵심 구조:

```
실제 코드:     OrderService → Database(인터페이스) → 실제 DB
테스트 코드:   OrderService → Database(인터페이스) → MockDatabase
```

`OrderService`는 `Database` **인터페이스**에만 의존하므로, 실제 DB든 Mock이든 상관없이 동작한다. 이것은 **의존성 역전(Dependency Inversion)** 원칙의 실전적 적용이다.

### Mock Object의 종류

| 종류 | 역할 | 예시 |
|------|------|------|
| **Stub** | 미리 정해진 값을 반환 | `mockDb.setupResult(...)` |
| **Mock** | 호출 여부와 인자를 검증 | `verify(mockDb).query("...", "123")` |
| **Fake** | 간략화된 실제 구현 | 인메모리 DB |

> **핵심 통찰**: Mock Object는 단순한 테스트 편의 기능이 아니라, **설계를 개선하는 도구**이기도 하다. 목을 사용하려면 의존성을 주입(injection)할 수 있는 구조여야 하는데, 이것은 자연스럽게 **낮은 결합도(low coupling)**를 유도한다. "이 코드를 어떻게 목으로 대체하지?"라는 질문은 "이 코드의 의존성 구조가 건강한가?"라는 질문과 같다.

---

## 4. Self Shunt (셀프 션트)

### 문제

목 객체를 별도의 클래스로 만드는 것이 번거롭다. 테스트 하나를 위해 목 클래스를 하나 더 만들어야 하는가?

### 패턴

**테스트 클래스 자체가 목 객체의 역할을 하게 한다.** 테스트 대상 코드가 필요로 하는 인터페이스를 테스트 클래스가 직접 구현하여, 테스트 클래스를 목 객체로 전달한다.

### 설명

Self Shunt(자기 단락)는 전기 용어에서 온 비유다. 전기 회로에서 "shunt"는 전류를 다른 경로로 우회시키는 것을 의미한다. 마찬가지로, 테스트 대상 코드가 호출하는 것을 **테스트 클래스 자체로 우회**시킨다.

### 예시

이벤트를 발생시키는 컴포넌트를 테스트한다고 하자:

```java
// 테스트 대상: 이벤트를 리스너에게 알려주는 컴포넌트
public interface ActionListener {
    void actionPerformed(String action);
}

public class Button {
    private ActionListener listener;

    public void setListener(ActionListener listener) {
        this.listener = listener;
    }

    public void click() {
        if (listener != null) {
            listener.actionPerformed("clicked");
        }
    }
}
```

별도의 목 클래스를 만드는 방법:

```java
// 방법 1: 별도의 Mock 클래스 생성
class MockListener implements ActionListener {
    String lastAction;
    public void actionPerformed(String action) {
        this.lastAction = action;
    }
}

public void testButtonClick() {
    Button button = new Button();
    MockListener mock = new MockListener();
    button.setListener(mock);
    button.click();
    assertEquals("clicked", mock.lastAction);
}
```

Self Shunt를 사용하는 방법:

```java
// 방법 2: Self Shunt — 테스트 클래스가 직접 인터페이스 구현
public class ButtonTest extends TestCase implements ActionListener {
    String lastAction;

    public void actionPerformed(String action) {
        this.lastAction = action;  // 테스트 클래스가 직접 기록
    }

    public void testButtonClick() {
        Button button = new Button();
        button.setListener(this);  // this = 테스트 클래스 자체
        button.click();
        assertEquals("clicked", lastAction);
    }
}
```

Self Shunt의 장점:

- 별도의 목 클래스를 만들지 않아도 된다
- 테스트와 목의 로직이 한 곳에 있어 가독성이 좋다
- 간단한 경우에 코드량이 줄어든다

Self Shunt의 단점:

- 테스트 클래스가 여러 인터페이스를 구현하면 복잡해질 수 있다
- 여러 테스트가 다른 목 동작을 필요로 하면 혼란스러울 수 있다

> **핵심 통찰**: Self Shunt는 Mock Object의 경량 버전이다. 목 객체가 단순히 "호출되었는가?"만 확인하는 경우, 별도의 클래스를 만드는 것은 과도한 인프라다. 테스트 클래스 자체가 그 역할을 겸하면 코드가 더 간결해진다. 다만, 목의 로직이 복잡해지면 별도의 클래스로 분리하는 것이 낫다.

---

## 5. Log String (로그 문자열)

### 문제

메서드들이 올바른 순서로 호출되는지 어떻게 검증하는가? 예를 들어, `setUp()` → `testMethod()` → `tearDown()` 순서가 보장되는지 어떻게 테스트하는가?

### 패턴

**각 메서드가 호출될 때 문자열에 자기 이름을 덧붙인다.** 모든 호출이 끝나면, 이 문자열을 기대하는 순서와 비교한다.

### 설명

Log String은 Part II에서 xUnit을 구현할 때 핵심적으로 사용된 패턴이다. 메서드 호출 순서를 추적하는 가장 단순한 방법이다.

### Part II에서의 실제 사용

Part II Chapter 19-20에서, `setUp()` → `testMethod()` → `tearDown()` 호출 순서를 검증하기 위해 Log String을 사용했다:

```python
class WasRun(TestCase):
    def __init__(self, name):
        TestCase.__init__(self, name)

    def setUp(self):
        self.log = "setUp "        # 로그 시작

    def testMethod(self):
        self.log = self.log + "testMethod "   # 로그에 추가

    def tearDown(self):
        self.log = self.log + "tearDown "     # 로그에 추가
```

```python
# 테스트: 호출 순서 검증
class TestCaseTest(TestCase):
    def testTemplateMethod(self):
        test = WasRun("testMethod")
        result = TestResult()
        test.run(result)
        assert "setUp testMethod tearDown " == test.log
        # log가 "setUp testMethod tearDown " 이면
        # 세 메서드가 올바른 순서로 호출된 것이다
```

### 일반적인 예시

```java
// Java에서의 Log String 패턴
public class ProcessorTest extends TestCase {
    String log = "";

    public void testProcessingOrder() {
        Processor processor = new Processor() {
            @Override
            void validate() { log += "validate "; }
            @Override
            void transform() { log += "transform "; }
            @Override
            void save() { log += "save "; }
        };

        processor.process();
        assertEquals("validate transform save ", log);
    }
}
```

### Log String vs 다른 방법들

| 방법 | 장점 | 단점 |
|------|------|------|
| **Log String** | 단순, 순서 검증 가능 | 같은 메서드 여러 번 호출 시 복잡 |
| **호출 횟수 카운터** | 횟수 검증 정확 | 순서 검증 불가 |
| **boolean 플래그** | 가장 단순 | 순서 검증 불가, 여러 호출 구분 불가 |
| **목 프레임워크** | 강력하고 유연 | 설정 코드가 길어짐 |

> **핵심 통찰**: Log String은 **관찰자(Observer) 패턴의 테스트 버전**이다. 복잡한 목 프레임워크 없이도 "어떤 메서드가 어떤 순서로 호출되었는가?"를 명쾌하게 검증할 수 있다. 단순한 문자열 비교 하나로 복잡한 호출 시퀀스를 확인할 수 있다는 점에서, 이 패턴의 우아함이 돋보인다.

---

## 6. Crash Test Dummy (충돌 테스트 더미)

### 문제

에러 처리 코드를 테스트하려면 실제로 에러를 발생시켜야 한다. 하지만 디스크 풀(disk full), 네트워크 장애, 메모리 부족 같은 에러를 테스트 환경에서 의도적으로 발생시키기 어렵다. 어떻게 테스트하는가?

### 패턴

**무조건 예외를 던지는 특수한 객체(Crash Test Dummy)를 만들어, 에러 처리 코드를 강제로 실행시킨다.**

### 설명

Crash Test Dummy(충돌 테스트 더미)는 자동차 안전 테스트에서 사용하는 인형(crash test dummy)에서 이름을 따왔다. 실제 사람 대신 인형을 충돌에 넣어 안전 장치를 테스트하듯, 실제 에러 대신 인위적인 에러를 발생시켜 에러 처리를 테스트한다.

### 예시

파일 쓰기 실패 시의 에러 처리를 테스트:

```java
// 테스트 대상: 파일에 로그를 기록하는 Logger
public class Logger {
    private FileWriter writer;

    public Logger(FileWriter writer) {
        this.writer = writer;
    }

    public boolean log(String message) {
        try {
            writer.write(message);
            return true;
        } catch (IOException e) {
            return false;  // 에러 처리: false 반환
        }
    }
}
```

```java
// Crash Test Dummy: 항상 IOException을 던지는 FileWriter
class FailingWriter extends FileWriter {
    public FailingWriter() throws IOException {
        super("/dev/null");  // 형식적인 생성자 호출
    }

    @Override
    public void write(String str) throws IOException {
        throw new IOException("디스크 풀!");  // 항상 실패
    }
}

// 테스트: 쓰기 실패 시 false를 반환하는지 검증
public void testLogFailure() throws IOException {
    Logger logger = new Logger(new FailingWriter());
    assertFalse(logger.log("test message"));
}
```

실제 디스크 풀을 만들지 않아도, `FailingWriter`가 `IOException`을 던지므로 `Logger`의 에러 처리 경로가 실행된다.

### Crash Test Dummy vs Mock Object

| Crash Test Dummy | Mock Object |
|------------------|-------------|
| 항상 예외를 던진다 | 정상적인 동작을 흉내낸다 |
| 에러 처리 코드를 테스트 | 정상 경로를 테스트 |
| 단순 (예외 던지기만 하면 됨) | 복잡할 수 있음 (반환값 설정, 호출 검증) |

Crash Test Dummy는 Mock Object의 특수한 경우로, "에러 상황"만을 시뮬레이션한다.

> **핵심 통찰**: 에러 처리 코드는 정상 경로보다 테스트하기 어렵지만, 정상 경로보다 **중요할 수 있다.** 시스템이 정상 동작할 때는 잘 돌아가지만, 에러가 발생했을 때 올바르게 처리하지 못하면 데이터 손실이나 시스템 장애로 이어진다. Crash Test Dummy는 이런 에러 경로를 테스트 가능하게 만든다.

---

## 7. Broken Test (깨진 테스트)

### 문제

프로그래밍 세션이 끝나고 퇴근해야 한다. 내일 다시 와서 어디부터 시작해야 할지 어떻게 기억하는가?

### 패턴

**혼자 작업할 때, 마지막에 실패하는 테스트를 하나 남겨두고 작업을 종료한다.** 다음 날 돌아왔을 때, 이 실패하는 테스트가 "여기서 이어서 하면 됩니다"라는 표지판 역할을 한다.

### 설명

Broken Test는 **개인 작업에만** 적용되는 패턴이다. 팀과 공유하는 코드에는 적용하지 않는다 (그것은 Clean Check-in 패턴이 담당한다).

절차:

1. 하루의 작업이 끝날 때, **다음에 할 작업**에 대한 테스트를 작성한다
2. 이 테스트는 당연히 실패한다 (아직 구현하지 않았으므로)
3. **이 실패 상태로 저장하고 퇴근한다**
4. 다음 날, 테스트를 실행한다 → Red Bar가 "어디서 이어가야 하는지"를 알려준다

이점:

- **컨텍스트 복원**: "어디까지 했지?"를 기억할 필요 없다. 테스트가 알려준다.
- **즉시 시작**: 돌아오자마자 Red Bar를 Green으로 만드는 작업에 착수할 수 있다.
- **워밍업**: 간단한 테스트 통과시키기로 하루를 시작하면, 코딩 리듬에 빨리 들어갈 수 있다.

### 주의사항

이 패턴은 **반드시 개인 브랜치 또는 로컬 작업에서만** 사용해야 한다:

```
✓ 로컬에서 혼자 작업할 때 — Broken Test OK
✓ 개인 브랜치에서 — Broken Test OK
✗ 공유 브랜치(main/master)에 커밋 — Broken Test 절대 금지!
✗ CI/CD 파이프라인에 — Broken Test 절대 금지!
```

> **핵심 통찰**: Broken Test는 "내일의 나에게 보내는 메모"이다. 텍스트 메모("내일 할 일: ...")보다 실패하는 테스트가 더 효과적인 이유는, 테스트가 **실행 가능한 명세**이기 때문이다. "다음에 할 일"이 무엇인지뿐만 아니라, 그것이 **어떤 상태에서 시작하는지**까지 코드로 표현된다.

---

## 8. Clean Check-in (깨끗한 체크인)

### 문제

코드를 팀의 공유 저장소에 커밋/체크인할 때, 어떤 상태여야 하는가?

### 패턴

**모든 테스트가 통과하는 상태에서만 코드를 체크인한다.** 실패하는 테스트가 있으면 절대 공유 저장소에 커밋하지 않는다.

### 설명

Clean Check-in은 Broken Test와 **정반대**의 패턴이다:

| Broken Test | Clean Check-in |
|-------------|----------------|
| 개인 작업용 | 팀 공유용 |
| 실패하는 테스트를 남긴다 | 모든 테스트가 통과해야 한다 |
| "내일의 나"를 위한 것 | "팀 전체"를 위한 것 |

Clean Check-in의 원칙:

1. **커밋 전에 모든 테스트를 실행한다**
2. **하나라도 실패하면 커밋하지 않는다**
3. **실패 원인을 해결한 후 다시 시도한다**
4. **"내 로컬에서는 통과했는데..."는 변명이 되지 않는다**

이 원칙이 중요한 이유:

```
개발자 A가 실패하는 테스트와 함께 커밋
    ↓
개발자 B가 최신 코드를 받음
    ↓
개발자 B의 테스트가 실패 — 자신의 코드 문제인가? A의 문제인가?
    ↓
디버깅에 시간 낭비
    ↓
팀 전체의 테스트에 대한 신뢰가 하락
    ↓
"테스트가 실패해도 괜찮아"라는 문화가 형성
    ↓
테스트의 가치가 사라짐
```

이 연쇄 반응을 방지하기 위해, **"공유 저장소의 모든 테스트는 항상 통과한다"**는 팀 규범이 필수적이다.

### 실무에서의 적용

현대적인 개발 환경에서 Clean Check-in은 CI(Continuous Integration) 시스템과 결합된다:

```
개발자가 커밋
    ↓
CI 서버가 자동으로 모든 테스트 실행
    ↓
실패하면: 팀에 알림 → 즉시 수정
통과하면: 다음 단계(배포 등)로 진행
```

> **핵심 통찰**: Clean Check-in은 **팀의 신뢰**를 지키는 패턴이다. "공유 저장소의 테스트는 항상 통과한다"는 규범이 있으면, 테스트 실패는 곧 "무언가 잘못되었다"는 확실한 신호가 된다. 이 신뢰가 없으면 테스트는 "어차피 실패하는 것"이 되어 무시당하고, TDD의 모든 이점이 증발한다.

---

## 9. 패턴 간의 관계

이 챕터의 7개 패턴을 상황별로 정리하면:

```
테스트 구조
├─ Child Test (테스트가 너무 크면 → 분해)
└─ Log String (메서드 호출 순서 → 문자열로 추적)

외부 의존성 처리
├─ Mock Object (느린/복잡한 의존성 → 가짜 객체로 대체)
├─ Self Shunt (테스트 클래스 자체가 → 목 객체 역할)
└─ Crash Test Dummy (에러 상황 → 항상 예외를 던지는 객체)

작업 흐름 관리
├─ Broken Test (개인 작업 중단 → 실패하는 테스트 남기기)
└─ Clean Check-in (팀 공유 커밋 → 모든 테스트 통과 상태)
```

Mock Object, Self Shunt, Crash Test Dummy의 관계:

```
Mock Object (일반적인 가짜 객체)
    ├─ Self Shunt (테스트 클래스 = 목 객체)
    └─ Crash Test Dummy (항상 예외를 던지는 목 객체)
```

Self Shunt와 Crash Test Dummy는 모두 Mock Object의 특수한 형태다.

---

## 요약

- **Child Test**: 큰 테스트를 작은 테스트들로 분해한다. 한 번에 한 걸음씩 진행하는 TDD의 원칙을 테스트 구조에도 적용한다.
- **Mock Object**: 느리거나 복잡한 외부 의존성을 가짜 객체로 대체한다. 테스트를 빠르고 결정적으로 만들며, 부수적으로 좋은 설계(낮은 결합도)를 유도한다.
- **Self Shunt**: 테스트 클래스 자체가 목 객체 역할을 하게 한다. 간단한 경우에 별도의 목 클래스 생성을 피한다.
- **Log String**: 메서드 호출 순서를 문자열 추가로 추적한다. Part II의 xUnit 구현에서 핵심적으로 사용되었다.
- **Crash Test Dummy**: 항상 예외를 던지는 객체로 에러 처리 코드를 테스트한다. 실제 에러 상황을 인위적으로 만들기 어려울 때 사용한다.
- **Broken Test**: 개인 작업을 중단할 때 실패하는 테스트를 남겨, 다음에 이어갈 지점을 표시한다.
- **Clean Check-in**: 팀 공유 저장소에는 모든 테스트가 통과하는 상태에서만 커밋한다. 테스트에 대한 팀의 신뢰를 유지하는 핵심 규범이다.

---

## 다른 챕터와의 관계

- **Chapter 19-20 (Set the Table / Cleaning Up After)**: Log String 패턴이 Part II에서 `setUp()` → `testMethod()` → `tearDown()` 호출 순서를 검증하는 데 실제로 사용되었다.
- **Chapter 22 (Dealing with Failure)**: Crash Test Dummy와 유사한 개념이 Part II에서 테스트 실패 처리를 구현할 때 등장한다.
- **Chapter 25 (TDD Patterns)**: Isolated Test 패턴이 Mock Object의 필요성을 설명한다. 테스트가 외부 자원에 의존하면 격리가 깨지므로, 목으로 대체해야 한다.
- **Chapter 26 (Red Bar Patterns)**: Child Test는 One Step Test의 자연스러운 결과다. 테스트가 "한 걸음"이 아니면 Child Test로 분해한다.
- **Chapter 28 (Green Bar Patterns)**: 이 챕터가 "더 나은 테스트를 작성하는 방법"이라면, Chapter 28은 "그 테스트를 통과시키는 방법"이다.
- **Chapter 29 (xUnit Patterns)**: Mock Object와 Self Shunt가 xUnit 프레임워크의 기능과 어떻게 결합되는지를 다룬다.
