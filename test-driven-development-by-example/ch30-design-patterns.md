# Chapter 30: Design Patterns (설계 패턴)

## 핵심 질문

TDD에서 자연스럽게 등장하는 설계 패턴들은 무엇이며, TDD의 관점에서 각 패턴이 어떤 역할을 하는가?

---

## 1. 개요

이 챕터는 GoF(Gang of Four)의 설계 패턴 카탈로그를 다시 설명하려는 것이 **아니다**. 대신 TDD를 실천하면서 자연스럽게 등장하는 패턴들을 TDD의 맥락에서 설명한다. 핵심 질문은 "이 패턴이 TDD에서 언제, 왜 필요한가?"다.

Kent Beck은 TDD에서 패턴이 등장하는 방식이 전통적 설계와 다르다고 강조한다:

- **전통적 설계**: "앞으로 이런 변경이 있을 것이니 이 패턴을 미리 적용하자" (예측 기반)
- **TDD**: "중복을 제거하고 의도를 명확히 하다 보니 이 패턴이 나타났다" (발견 기반)

이 차이는 미묘하지만 중요하다. TDD에서 패턴은 **목적지가 아니라 결과**다.

---

## 2. Command (커맨드)

### 2.1 정의

**계산(computation)을 객체로 표현한다.** 메서드 호출 대신, 할 일을 객체로 만들어 나중에 실행하거나 전달할 수 있게 한다.

### 2.2 TDD에서의 맥락

Command 패턴은 "언제 실행할지"와 "무엇을 실행할지"를 분리할 때 유용하다. TDD에서는 다음 상황에서 자주 등장한다:

- 실행 시점을 늦추고 싶을 때 (지연 실행)
- 실행 이력을 기록하고 싶을 때 (Undo/Redo)
- 다양한 연산을 동일한 인터페이스로 다루고 싶을 때

### 2.3 예시

```java
// Command 인터페이스
interface Command {
    void execute();
}

// 구체적 커맨드들
class DepositCommand implements Command {
    private Account account;
    private int amount;

    DepositCommand(Account account, int amount) {
        this.account = account;
        this.amount = amount;
    }

    public void execute() {
        account.deposit(amount);
    }
}

class WithdrawCommand implements Command {
    private Account account;
    private int amount;

    WithdrawCommand(Account account, int amount) {
        this.account = account;
        this.amount = amount;
    }

    public void execute() {
        account.withdraw(amount);
    }
}
```

테스트에서의 활용:

```java
public void testDepositCommand() {
    Account account = new Account(100);
    Command command = new DepositCommand(account, 50);
    command.execute();
    assertEquals(150, account.balance());
}

public void testCommandQueue() {
    Account account = new Account(100);
    List<Command> commands = new ArrayList<>();
    commands.add(new DepositCommand(account, 50));
    commands.add(new WithdrawCommand(account, 30));

    for (Command cmd : commands) {
        cmd.execute();
    }
    assertEquals(120, account.balance());
}
```

> **핵심 통찰**: Command 패턴은 TDD에서 자주 등장하지 않지만, "메시지를 객체로 만들기"라는 핵심 아이디어는 가치가 있다. 함수를 일급 시민(first-class citizen)으로 다룰 수 있는 현대 언어에서는 클로저나 람다가 Command의 역할을 대체하기도 한다.

---

## 3. Value Object (값 객체)

### 3.1 정의

**상태가 변하지 않는 불변(immutable) 객체로, 동등성(equality)을 값으로 판단한다.** 한 번 생성되면 내부 값이 절대 변하지 않는다.

### 3.2 TDD에서의 맥락

Part I의 `Dollar`와 `Franc`가 Value Object의 전형적인 예다. TDD에서 Value Object는 매우 자연스럽게 등장한다:

1. 테스트에서 "같은 값이면 같은 객체"라는 assertion을 쓰고 싶다 → equals() 구현 필요
2. "곱하기 연산의 결과가 원본을 변경하지 않아야 한다"는 테스트를 작성한다 → 불변성 필요
3. 이 두 가지가 합쳐져 Value Object가 된다

### 3.3 Part I과의 연결

Chapter 2에서 `Dollar.times()`의 부작용 문제를 해결할 때 Value Object가 등장했다:

```java
// 부작용이 있는 버전 (나쁜 예)
public void times(int multiplier) {
    amount *= multiplier;  // 원본이 변경됨!
}

// 테스트
Dollar five = new Dollar(5);
five.times(2);
assertEquals(10, five.amount);
five.times(3);
assertEquals(15, five.amount);  // 실패! 30이 됨
```

```java
// Value Object 버전 (좋은 예)
public Dollar times(int multiplier) {
    return new Dollar(amount * multiplier);  // 새 객체 반환
}

// 테스트
Dollar five = new Dollar(5);
assertEquals(new Dollar(10), five.times(2));
assertEquals(new Dollar(15), five.times(3));  // five는 여전히 5
```

### 3.4 Value Object의 특성

| 특성 | 설명 | TDD 이점 |
|------|------|----------|
| **불변(Immutable)** | 생성 후 상태 변경 불가 | 부작용 없이 안전하게 공유 가능 |
| **값 동등성(Value Equality)** | 내부 값이 같으면 같은 객체 | `assertEqual`에서 자연스럽게 비교 가능 |
| **대체 가능(Substitutable)** | 같은 값의 두 객체는 교환 가능 | 테스트에서 기대값을 쉽게 만들 수 있음 |
| **자기 완결적(Self-contained)** | 필요한 모든 정보를 내부에 보유 | 테스트 설정이 단순해짐 |

### 3.5 equals()와 hashCode()

Value Object를 만들면 반드시 `equals()`와 `hashCode()`를 함께 구현해야 한다. Part I에서 TDD로 이들을 구현한 과정이 Chapter 3("Equality for All")이었다:

```java
public boolean equals(Object object) {
    Money money = (Money) object;
    return amount == money.amount
        && currency().equals(money.currency());
}

public int hashCode() {
    return amount;
}
```

> **핵심 통찰**: Value Object는 TDD에서 가장 자주 등장하는 패턴이다. "테스트에서 assertEqual으로 비교하고 싶다"는 욕구가 자연스럽게 Value Object로 이끈다. 불변성은 테스트의 예측 가능성을 높이고, 부작용에서 오는 혼란을 제거한다.

---

## 4. Null Object (널 객체)

### 4.1 정의

**null 검사를 제거하기 위해, 아무것도 하지 않는(do-nothing) 특별한 객체를 사용한다.** 기존 인터페이스를 구현하되, 모든 메서드가 기본값을 반환하거나 아무 작업도 하지 않는다.

### 4.2 문제 상황

null 검사가 코드 전체에 퍼지는 상황:

```java
// null 검사가 코드를 오염시키는 예
public String formatUser(User user) {
    if (user == null) {
        return "Anonymous";
    }
    if (user.getEmail() == null) {
        return user.getName();
    }
    return user.getName() + " <" + user.getEmail() + ">";
}
```

### 4.3 해결

```java
// Null Object 적용
class NullUser implements User {
    public String getName() { return "Anonymous"; }
    public String getEmail() { return ""; }
}

// null 검사가 사라진 코드
public String formatUser(User user) {
    if (user.getEmail().isEmpty()) {
        return user.getName();
    }
    return user.getName() + " <" + user.getEmail() + ">";
}
```

### 4.4 TDD에서의 등장 과정

TDD에서 Null Object는 다음과 같은 흐름으로 자연스럽게 등장한다:

1. 테스트를 작성하다가 null 처리 코드가 반복됨을 발견한다
2. 리팩토링 단계에서 "null 대신 뭔가를 넣을 수는 없을까?"라고 생각한다
3. 기존 인터페이스를 구현하는 "빈" 객체를 만든다
4. 조건문이 사라지고 코드가 단순해진다

```java
// TDD 과정에서의 진화
// 1단계: null 체크가 있는 테스트
public void testNoDiscount() {
    Order order = new Order(100, null);  // 할인 없음
    assertEquals(100, order.total());
}

// Order 내부: if (discount == null) return price; else return price - discount.amount();

// 2단계: Null Object 도입 후
public void testNoDiscount() {
    Order order = new Order(100, Discount.none());
    assertEquals(100, order.total());
}

// Discount.none()이 NullDiscount를 반환, amount()가 0을 반환
// Order 내부: return price - discount.amount();  // null 체크 불필요
```

> **핵심 통찰**: Null Object는 Imposter(사칭자) 패턴의 한 형태다. 실제 객체를 "흉내 내되" 아무것도 하지 않는 객체다. TDD에서 조건문을 다형성으로 대체하는 리팩토링 과정에서 자연스럽게 등장한다.

---

## 5. Template Method (템플릿 메서드)

### 5.1 정의

**알고리즘의 골격을 상위 클래스에 정의하고, 특정 단계를 하위 클래스가 채우도록 한다.** 전체 흐름은 고정되어 있고, 세부 구현만 달라진다.

### 5.2 Part II와의 연결

Part II에서 구현한 `TestCase.run()`이 바로 Template Method다:

```python
class TestCase:
    def run(self, result):
        result.testStarted()
        self.setUp()        # 하위 클래스가 오버라이드
        try:
            method = getattr(self, self.name)
            method()         # 하위 클래스가 정의한 테스트 메서드
        except:
            result.testFailed()
        self.tearDown()     # 하위 클래스가 오버라이드
        return result

    def setUp(self):
        pass  # 기본: 아무것도 안 함

    def tearDown(self):
        pass  # 기본: 아무것도 안 함
```

알고리즘의 골격(`run`)은 고정되어 있다:
1. 테스트 시작 기록
2. `setUp()` 실행 ← **하위 클래스가 결정**
3. 테스트 메서드 실행 ← **하위 클래스가 결정**
4. 예외 처리
5. `tearDown()` 실행 ← **하위 클래스가 결정**

### 5.3 TDD에서의 등장 과정

Template Method는 보통 리팩토링 과정에서 등장한다:

1. 비슷한 구조의 코드가 두 군데 이상에서 반복된다
2. 공통 부분과 다른 부분을 식별한다
3. 공통 부분을 상위 클래스로 올린다
4. 다른 부분을 추상 메서드로 만든다

```java
// 리팩토링 전: 두 클래스에 비슷한 코드
class CsvExporter {
    public String export(List<Record> records) {
        String header = "name,email,age\n";         // 다름
        StringBuilder body = new StringBuilder();
        for (Record r : records) {
            body.append(formatCsv(r));               // 다름
        }
        return header + body.toString();
    }
}

class JsonExporter {
    public String export(List<Record> records) {
        String header = "[\n";                       // 다름
        StringBuilder body = new StringBuilder();
        for (Record r : records) {
            body.append(formatJson(r));              // 다름
        }
        return header + body.toString() + "]";
    }
}

// 리팩토링 후: Template Method
abstract class Exporter {
    public final String export(List<Record> records) {
        StringBuilder result = new StringBuilder();
        result.append(header());                     // 추상
        for (Record r : records) {
            result.append(formatRecord(r));          // 추상
        }
        result.append(footer());                     // 추상
        return result.toString();
    }

    protected abstract String header();
    protected abstract String formatRecord(Record r);
    protected abstract String footer();
}
```

> **핵심 통찰**: Template Method는 "변하는 것과 변하지 않는 것을 분리"하는 패턴이다. TDD에서 두 개 이상의 유사한 구현을 리팩토링할 때 자연스럽게 등장한다. 중요한 것은 미리 Template Method를 설계하는 것이 아니라, 중복을 제거하다가 발견하는 것이다.

---

## 6. Pluggable Object (플러그형 객체)

### 6.1 정의

**조건문을 다형성으로 대체한다.** 두 개 이상의 구현을 같은 인터페이스 뒤에 두고, 조건문 대신 적절한 객체를 선택하여 끼워 넣는다.

### 6.2 TDD에서의 전형적 등장 과정

1. 처음에는 `if-else`로 빠르게 Green을 만든다
2. 비슷한 조건문이 여러 곳에 퍼진다
3. 리팩토링에서 조건문을 인터페이스와 구현체로 분리한다

```java
// 리팩토링 전: 조건문
class TaxCalculator {
    public Money calculate(Order order) {
        if (order.getCountry().equals("US")) {
            return order.total().times(0.08);   // 미국 세금
        } else if (order.getCountry().equals("UK")) {
            return order.total().times(0.20);   // 영국 세금
        } else {
            return Money.zero();
        }
    }
}

// 리팩토링 후: Pluggable Object
interface TaxPolicy {
    Money calculate(Money amount);
}

class USTaxPolicy implements TaxPolicy {
    public Money calculate(Money amount) {
        return amount.times(0.08);
    }
}

class UKTaxPolicy implements TaxPolicy {
    public Money calculate(Money amount) {
        return amount.times(0.20);
    }
}

class NoTaxPolicy implements TaxPolicy {      // Null Object이기도 하다!
    public Money calculate(Money amount) {
        return Money.zero();
    }
}

class TaxCalculator {
    private TaxPolicy policy;

    TaxCalculator(TaxPolicy policy) {
        this.policy = policy;
    }

    public Money calculate(Order order) {
        return policy.calculate(order.total());
    }
}
```

### 6.3 테스트에서의 효과

Pluggable Object를 사용하면 각 정책을 독립적으로 테스트할 수 있다:

```java
public void testUSTax() {
    TaxPolicy policy = new USTaxPolicy();
    assertEquals(Money.dollar(8), policy.calculate(Money.dollar(100)));
}

public void testUKTax() {
    TaxPolicy policy = new UKTaxPolicy();
    assertEquals(Money.dollar(20), policy.calculate(Money.dollar(100)));
}

public void testNoTax() {
    TaxPolicy policy = new NoTaxPolicy();
    assertEquals(Money.zero(), policy.calculate(Money.dollar(100)));
}
```

> **핵심 통찰**: Kent Beck은 "첫 번째 조건문은 괜찮지만, 두 번째 조건문이 나타나면 Pluggable Object를 고려하라"고 말한다. TDD의 리팩토링 단계에서 조건문이 중복되는 것을 발견했을 때 이 패턴으로 전환한다.

---

## 7. Pluggable Selector (플러그형 선택자)

### 7.1 정의

**메서드 이름을 문자열로 저장하고, 리플렉션(reflection)을 사용하여 동적으로 호출한다.** 하위 클래스를 만드는 대신, 호출할 메서드 이름을 매개변수로 받는다.

### 7.2 Part II와의 연결

Part II에서 구현한 `TestCase`가 이 패턴의 대표적 예다:

```python
class TestCase:
    def __init__(self, name):
        self.name = name  # 메서드 이름을 문자열로 저장

    def run(self, result):
        result.testStarted()
        self.setUp()
        try:
            method = getattr(self, self.name)  # 리플렉션으로 메서드 조회
            method()                            # 동적 호출
        except:
            result.testFailed()
        self.tearDown()
        return result
```

사용 시:

```python
# "testMethod"라는 이름의 메서드를 동적으로 호출
test = MyTestCase("testMethod")
test.run(result)
```

### 7.3 언제 사용하는가

| 상황 | Pluggable Selector 사용 | 하위 클래스 사용 |
|------|------------------------|-----------------|
| 행위 수가 적고 잘 정의된 경우 | 적합 | 과도함 |
| 행위 수가 많고 복잡한 경우 | 유지보수 어려움 | 적합 |
| 동적으로 행위를 결정해야 하는 경우 | 적합 | 불가능 |
| 컴파일 타임 타입 안전성이 중요한 경우 | 부적합 | 적합 |

### 7.4 주의사항

Pluggable Selector는 강력하지만 위험할 수 있다:

- 컴파일러가 오타를 잡아주지 못한다 (`"testMultiplication"` → `"testMultiplicaton"`)
- IDE에서 메서드 사용처를 추적하기 어렵다
- 남용하면 코드의 흐름을 따라가기 어려워진다

> **핵심 통찰**: Pluggable Selector는 "하위 클래스 하나에 메서드 하나만 오버라이드"하는 패턴이 반복될 때 유용한 대안이다. 하지만 정적 타입 언어에서는 리팩토링 도구의 지원을 받기 어려우므로 신중하게 사용해야 한다. Part II의 xUnit 구현은 이 패턴의 적절한 사용 사례다.

---

## 8. Factory Method (팩토리 메서드)

### 8.1 정의

**객체 생성을 메서드에 위임하여, 클라이언트가 구체 클래스를 직접 참조하지 않도록 한다.** 어떤 클래스의 인스턴스를 생성할지를 하위 클래스나 별도의 메서드가 결정한다.

### 8.2 Part I과의 연결

Part I에서 Factory Method는 핵심적인 역할을 했다. `Dollar`와 `Franc`를 `Money`의 하위 클래스로 통합하는 과정에서, 클라이언트 코드가 구체 클래스를 직접 참조하지 않도록 하기 위해 도입했다 (Chapter 8):

```java
// 팩토리 메서드 도입 전
Dollar five = new Dollar(5);
Franc tenFrancs = new Franc(10);

// 팩토리 메서드 도입 후
Money five = Money.dollar(5);
Money tenFrancs = Money.franc(10);
```

팩토리 메서드 구현:

```java
abstract class Money {
    static Money dollar(int amount) {
        return new Dollar(amount, "USD");
    }

    static Money franc(int amount) {
        return new Franc(amount, "CHF");
    }
}
```

### 8.3 TDD에서 Factory Method가 등장하는 시점

Factory Method는 보통 리팩토링 과정에서 등장한다:

1. 테스트에서 구체 클래스를 직접 생성하고 있다
2. 구체 클래스의 존재가 설계 변경을 방해한다
3. Factory Method를 도입하여 구체 클래스 의존성을 제거한다
4. 이후 구체 클래스를 자유롭게 변경하거나 제거할 수 있다

Part I에서도 이 순서를 따랐다. `Dollar`와 `Franc` 클래스를 제거하고 `Money` 하나로 통합하고 싶었지만, 테스트 코드가 `new Dollar()`를 직접 호출하고 있어서 불가능했다. Factory Method를 도입한 후에야 구체 클래스를 안전하게 제거할 수 있었다.

### 8.4 테스트에서의 효과

```java
// 팩토리 메서드 도입 후, 내부 구현이 바뀌어도 테스트가 안정적이다
public void testEquality() {
    assertTrue(Money.dollar(5).equals(Money.dollar(5)));
    // Dollar 클래스가 사라져도 이 테스트는 영향받지 않음
}
```

> **핵심 통찰**: Factory Method는 TDD에서 "테스트가 구현 세부사항에 의존하는 것"을 해결한다. 구체 클래스를 직접 생성하는 테스트는 구조 변경에 취약하다. Factory Method를 통해 "무엇을 생성하는가"와 "어떻게 생성하는가"를 분리하면, 내부 구조를 자유롭게 리팩토링할 수 있다.

---

## 9. Imposter (사칭자)

### 9.1 정의

**기존 인터페이스의 새로운 구현을 도입하여 시스템의 변화에 대응한다.** 기존 코드가 인터페이스에 의존하고 있을 때, 새로운 구현체를 슬쩍 끼워 넣어 행위를 변경한다.

### 9.2 TDD에서의 두 가지 주요 활용

**활용 1: Mock Object(모의 객체)**

테스트에서 느리거나 복잡한 외부 의존성을 대체한다:

```java
// 실제 객체: 네트워크 호출이 필요
class RealExchangeRateService implements ExchangeRateService {
    public double getRate(String from, String to) {
        // HTTP API 호출 (느림, 외부 의존)
        return httpClient.get("/rates/" + from + "/" + to);
    }
}

// Imposter: 테스트용 가짜 구현
class StubExchangeRateService implements ExchangeRateService {
    private Map<String, Double> rates = new HashMap<>();

    public void setRate(String from, String to, double rate) {
        rates.put(from + "->" + to, rate);
    }

    public double getRate(String from, String to) {
        return rates.get(from + "->" + to);
    }
}
```

테스트에서:

```java
public void testCurrencyConversion() {
    StubExchangeRateService rates = new StubExchangeRateService();
    rates.setRate("CHF", "USD", 1.5);
    Bank bank = new Bank(rates);
    assertEquals(Money.dollar(10), bank.convert(Money.franc(15), "USD"));
}
```

**활용 2: Null Object**

앞서 다룬 Null Object도 Imposter의 한 형태다. 실제 객체의 인터페이스를 구현하되, 아무 일도 하지 않는 "사칭자"다.

### 9.3 Imposter의 힘

Imposter 패턴의 핵심은 **기존 코드를 변경하지 않고도 행위를 바꿀 수 있다**는 점이다. 이것은 개방-폐쇄 원칙(Open-Closed Principle)의 구현이며, TDD에서 설계가 유연해지는 핵심 메커니즘이다.

| Imposter 종류 | 용도 | 예시 |
|---------------|------|------|
| Mock Object | 테스트에서 외부 의존성 대체 | 가짜 DB, 가짜 HTTP 서비스 |
| Null Object | null 검사 제거 | 아무것도 하지 않는 로거 |
| Test Double | 테스트에서 복잡한 객체 단순화 | 고정값을 반환하는 서비스 |
| Adapter | 기존 인터페이스에 새 구현 연결 | 서드파티 라이브러리 래핑 |

> **핵심 통찰**: Kent Beck은 "리팩토링 중 어떤 문제를 만나면 '기존 프로토콜을 구현하는 새 객체를 넣으면 해결될까?'라고 먼저 생각하라"고 조언한다. 이것이 Imposter의 사고방식이며, 객체지향 설계의 핵심적인 확장 메커니즘이다.

---

## 10. Composite (컴포지트)

### 10.1 정의

**단일 객체와 객체의 컬렉션을 동일하게 취급한다.** 하나의 인터페이스로 개별 객체와 그룹 모두를 다룰 수 있게 한다.

### 10.2 Part II와의 연결: TestSuite

Part II에서 `TestSuite`는 Composite 패턴의 전형적인 예였다:

```python
class TestSuite:
    def __init__(self):
        self.tests = []

    def add(self, test):
        self.tests.append(test)

    def run(self, result):
        for test in self.tests:
            test.run(result)  # TestCase든 TestSuite든 동일하게 호출
        return result
```

`TestCase`와 `TestSuite` 모두 `run(result)` 메서드를 가진다. `TestSuite`에 `TestCase`를 넣을 수도 있고, 다른 `TestSuite`를 넣을 수도 있다. 이것이 Composite 패턴의 힘이다:

```python
# 개별 테스트
test1 = MoneyTest("testMultiplication")

# 테스트 그룹
money_suite = TestSuite()
money_suite.add(MoneyTest("testMultiplication"))
money_suite.add(MoneyTest("testEquality"))

# 전체 스위트 (스위트 안에 스위트)
all_tests = TestSuite()
all_tests.add(money_suite)          # 스위트 추가
all_tests.add(BankTest("testRate")) # 개별 테스트 추가

# 모두 동일한 방식으로 실행
result = TestResult()
all_tests.run(result)
```

### 10.3 Part I과의 연결: Money + Sum

Part I에서도 Composite 패턴이 등장했다. `Money`와 `Sum`이 모두 `Expression` 인터페이스를 구현한다:

```java
interface Expression {
    Money reduce(Bank bank, String to);
}

class Money implements Expression {
    public Money reduce(Bank bank, String to) {
        // 단일 금액 변환
    }
}

class Sum implements Expression {
    Expression augend;
    Expression addend;

    public Money reduce(Bank bank, String to) {
        int amount = augend.reduce(bank, to).amount
                   + addend.reduce(bank, to).amount;
        return new Money(amount, to);
    }
}
```

`Sum`의 `augend`와 `addend`가 `Money`일 수도 있고 또 다른 `Sum`일 수도 있다. `$5 + 10CHF + $3` 같은 표현식이 재귀적으로 처리된다.

### 10.4 TDD에서 Composite가 등장하는 순서

1. 단일 객체에 대한 테스트를 작성하고 구현한다
2. 컬렉션에 대한 요구가 생긴다
3. 컬렉션도 단일 객체와 같은 인터페이스를 가지면 편리하다는 것을 깨닫는다
4. Composite 패턴으로 통합한다

> **핵심 통찰**: Composite는 "하나를 다루는 코드와 여럿을 다루는 코드가 같으면 좋겠다"는 생각에서 출발한다. TDD에서 단일 객체의 테스트를 먼저 작성하고, 컬렉션에 대한 테스트를 추가할 때 자연스럽게 등장한다.

---

## 11. Collecting Parameter (수집 매개변수)

### 11.1 정의

**여러 객체에 걸쳐 결과를 수집하기 위해, 결과를 담을 객체를 매개변수로 전달한다.**

### 11.2 Part II와의 연결: TestResult

`TestResult`가 바로 Collecting Parameter다:

```python
class TestResult:
    def __init__(self):
        self.runCount = 0
        self.failureCount = 0

    def testStarted(self):
        self.runCount += 1

    def testFailed(self):
        self.failureCount += 1

    def summary(self):
        return f"{self.runCount} run, {self.failureCount} failed"
```

`TestResult` 객체가 여러 테스트를 순회하면서 결과를 수집한다:

```python
result = TestResult()  # 빈 수집 매개변수

# 각 테스트가 result에 결과를 기록
test1.run(result)  # result.runCount = 1
test2.run(result)  # result.runCount = 2
test3.run(result)  # result.runCount = 3, result.failureCount = 1 (실패했다면)

print(result.summary())  # "3 run, 1 failed"
```

### 11.3 왜 반환값 대신 매개변수를 사용하는가

반환값을 사용하면 결과를 합칠 때 복잡해진다:

```python
# 반환값 방식 (번거로움)
result1 = test1.run()
result2 = test2.run()
result3 = test3.run()
merged = result1.merge(result2).merge(result3)

# Collecting Parameter 방식 (깔끔함)
result = TestResult()
test1.run(result)
test2.run(result)
test3.run(result)
# result에 이미 모든 정보가 수집됨
```

특히 Composite 패턴과 함께 사용할 때 위력이 드러난다. `TestSuite.run(result)`가 내부의 모든 `TestCase.run(result)`를 호출하면서 하나의 `result`에 결과를 축적한다.

> **핵심 통찰**: Collecting Parameter는 Composite 패턴의 자연스러운 동반자다. Composite가 "여러 객체를 하나처럼 다루기"라면, Collecting Parameter는 "여러 객체의 결과를 하나로 모으기"다. 둘이 함께 사용되면 복잡한 트리 구조에서도 결과를 깔끔하게 수집할 수 있다.

---

## 12. 패턴 간의 관계

이 챕터의 패턴들은 독립적으로 존재하지 않는다. Part I과 Part II에서 이들이 어떻게 얽혀 있었는지 정리한다:

```
Part I (Money Example)에서의 패턴 맵:
┌────────────────────────────────┐
│ Money = Value Object           │
│ Dollar/Franc → Money = Imposter│
│ Money.dollar() = Factory Method│
│ Sum = Composite                │
│ Expression = interface for     │
│   Pluggable Object             │
└────────────────────────────────┘

Part II (xUnit Example)에서의 패턴 맵:
┌────────────────────────────────┐
│ TestCase.run() = Template Method│
│ TestCase(name) = Pluggable     │
│   Selector                     │
│ TestSuite = Composite          │
│ TestResult = Collecting        │
│   Parameter                    │
└────────────────────────────────┘
```

| 패턴 | Part I 예시 | Part II 예시 |
|------|------------|-------------|
| Value Object | Dollar, Franc, Money | — |
| Null Object | — | (테스트 결과 기본값) |
| Template Method | — | TestCase.run() |
| Pluggable Object | Expression (Money, Sum) | — |
| Pluggable Selector | — | TestCase(name) |
| Factory Method | Money.dollar(), Money.franc() | — |
| Imposter | Franc → Money 통합, Sum | Mock objects |
| Composite | Sum (Expression 트리) | TestSuite |
| Collecting Parameter | — | TestResult |

---

## 요약

- **Command**는 계산을 객체로 표현하여 지연 실행, 큐잉, 이력 관리를 가능하게 한다.
- **Value Object**는 불변 객체로 TDD에서 가장 자연스럽게 등장하는 패턴이다. Part I의 Money가 대표적이다.
- **Null Object**는 null 검사를 제거하기 위해 "아무것도 하지 않는 객체"를 사용한다.
- **Template Method**는 알고리즘의 골격을 정의하고 세부 단계를 위임한다. Part II의 TestCase.run()이 대표적이다.
- **Pluggable Object**는 조건문을 다형성으로 대체하여 유연성을 확보한다.
- **Pluggable Selector**는 메서드 이름을 문자열로 저장하고 리플렉션으로 호출한다. Part II의 TestCase가 대표적이다.
- **Factory Method**는 객체 생성을 캡슐화하여 구체 클래스 의존성을 제거한다. Part I의 Money.dollar()가 대표적이다.
- **Imposter**는 기존 인터페이스의 새 구현을 끼워 넣어 시스템을 확장한다. Mock Object가 대표적이다.
- **Composite**는 단일 객체와 컬렉션을 동일하게 취급한다. Part II의 TestSuite가 대표적이다.
- **Collecting Parameter**는 여러 객체에 걸쳐 결과를 수집한다. Part II의 TestResult가 대표적이다.
- TDD에서 이 패턴들은 **미리 적용하는 것이 아니라, 리팩토링 과정에서 발견**한다.

---

## 다른 챕터와의 관계

- **Chapter 1~17 (Part I: Money Example)**: Value Object, Factory Method, Imposter, Composite, Pluggable Object가 실제로 TDD 과정에서 등장하고 진화하는 모습을 볼 수 있다.
- **Chapter 18~24 (Part II: xUnit Example)**: Template Method, Pluggable Selector, Composite, Collecting Parameter가 테스트 프레임워크 구현에서 어떻게 활용되는지 확인할 수 있다.
- **Chapter 29 (xUnit Patterns)**: xUnit 패턴들은 이 챕터의 설계 패턴들 위에 구축된다. Fixture는 Template Method, All Tests는 Composite, TestResult는 Collecting Parameter다.
- **Chapter 31 (Refactoring)**: 설계 패턴은 리팩토링의 "목적지" 역할을 한다. 31장의 리팩토링 기법을 사용하여 이 챕터의 설계 패턴에 도달한다.
- **Chapter 32 (Mastering TDD)**: "TDD가 어떻게 패턴으로 이어지는가?"라는 질문에 대한 답이 이 챕터에 있다.
