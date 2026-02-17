# Chapter 29: xUnit Patterns (xUnit 패턴)

## 핵심 질문

테스트 프레임워크(xUnit)를 효과적으로 사용하기 위한 패턴들은 무엇이며, 각 패턴이 해결하는 문제는 무엇인가?

---

## 1. 개요

Part II에서 우리는 Python으로 xUnit 스타일의 테스트 프레임워크를 직접 구현했다. 이 챕터에서는 그 과정에서 자연스럽게 등장한 패턴들을 체계적으로 정리한다. 이 패턴들은 특정 언어나 프레임워크에 종속되지 않으며, JUnit(Java), pytest(Python), NUnit(C#), RSpec(Ruby) 등 거의 모든 xUnit 계열 프레임워크에 적용된다.

xUnit 패턴은 "테스트를 어떻게 구조화하고, 작성하고, 실행할 것인가"에 대한 답을 제공한다. 각 패턴은 독립적으로도 가치가 있지만, 함께 사용될 때 강력한 테스트 인프라를 형성한다.

---

## 2. Assertion (단언)

### 2.1 문제

테스트가 통과했는지 실패했는지를 어떻게 판정하는가?

### 2.2 해결

**Boolean 표현식을 사용하여 기대값과 실제값을 비교하고, 불일치 시 테스트를 실패로 표시한다.** 이것이 assertion(단언)이다.

테스트의 가치는 자동화된 판정에 있다. 프로그래머가 출력을 눈으로 확인해야 한다면 테스트의 의미가 퇴색된다. Assertion은 "이 조건이 참이어야 한다"고 프로그램에게 선언하는 것이다.

### 2.3 주요 Assertion 유형

| Assertion | 설명 | 사용 예 |
|-----------|------|---------|
| `assertEqual(expected, actual)` | 두 값이 같은지 확인 | `assertEqual(10, five.times(2).amount)` |
| `assertTrue(condition)` | 조건이 참인지 확인 | `assertTrue(result.isSuccess())` |
| `assertFalse(condition)` | 조건이 거짓인지 확인 | `assertFalse(list.isEmpty())` |
| `assertNull(value)` | 값이 null인지 확인 | `assertNull(map.get("missing"))` |
| `assertNotNull(value)` | 값이 null이 아닌지 확인 | `assertNotNull(user.getId())` |
| `assertRaises(exception)` | 예외가 발생하는지 확인 | Exception Test 패턴 참조 |

### 2.4 Part II와의 연결

Part II(Chapter 21)에서 우리가 구현한 `TestCase` 프레임워크의 `assert` 메서드가 바로 이 패턴의 구현이었다:

```python
class TestCase:
    def assert_true(self, condition):
        if not condition:
            raise AssertionError
```

### 2.5 작성 원칙

Assertion을 작성할 때 중요한 원칙이 있다:

1. **구체적인 assertion을 사용한다**: `assertTrue(expected == actual)` 대신 `assertEqual(expected, actual)`을 사용하면, 실패 시 "expected 10 but got 7"처럼 유의미한 메시지를 볼 수 있다.
2. **테스트당 assertion 수를 적절히 유지한다**: 하나의 테스트에 너무 많은 assertion이 있다면, 그 테스트가 너무 많은 것을 검증하려 하는 신호일 수 있다.
3. **메시지를 포함한다**: `assertEqual(10, result, "할인 적용 후 금액이 틀림")` 처럼 실패 이유를 명시하면 디버깅이 쉬워진다.

> **핵심 통찰**: Assertion은 테스트의 **목적**을 선언한다. 테스트가 무엇을 검증하는지 assertion만 보고도 알 수 있어야 한다. 잘 작성된 assertion은 테스트의 문서 역할을 한다.

---

## 3. Fixture (픽스처)

### 3.1 문제

여러 테스트가 공통으로 필요로 하는 객체들을 어떻게 관리하는가?

### 3.2 해결

**공통 객체를 `setUp()` 메서드에서 인스턴스 변수로 생성한다.** 각 테스트 메서드가 실행되기 전에 `setUp()`이 자동으로 호출되어 깨끗한 상태의 fixture를 제공한다.

### 3.3 Fixture가 필요한 이유

다음과 같이 여러 테스트에서 같은 객체를 반복 생성하는 코드를 생각해보자:

```java
// 중복이 있는 테스트 코드
public void testMultiplication() {
    Dollar five = new Dollar(5);
    assertEquals(new Dollar(10), five.times(2));
}

public void testEquality() {
    Dollar five = new Dollar(5);
    assertTrue(five.equals(new Dollar(5)));
}

public void testToString() {
    Dollar five = new Dollar(5);
    assertEquals("5 USD", five.toString());
}
```

`Dollar five = new Dollar(5)`가 세 번 반복된다. Fixture 패턴을 적용하면:

```java
// Fixture를 사용한 테스트 코드
public class DollarTest extends TestCase {
    private Dollar five;

    public void setUp() {
        five = new Dollar(5);
    }

    public void testMultiplication() {
        assertEquals(new Dollar(10), five.times(2));
    }

    public void testEquality() {
        assertTrue(five.equals(new Dollar(5)));
    }

    public void testToString() {
        assertEquals("5 USD", five.toString());
    }
}
```

### 3.4 Part II와의 연결

Part II(Chapter 19, "Set the Table")에서 `setUp()` 메서드를 xUnit에 추가했다. `TestCase.run()`에서 `setUp()`을 먼저 호출하고 나서 테스트 메서드를 실행하는 구조였다:

```python
class TestCase:
    def run(self, result):
        result.testStarted()
        self.setUp()
        try:
            method = getattr(self, self.name)
            method()
        except:
            result.testFailed()
        self.tearDown()
        return result

    def setUp(self):
        pass  # 서브클래스에서 오버라이드
```

### 3.5 Fixture 사용 시 주의점

| 장점 | 주의점 |
|------|--------|
| 코드 중복 제거 | 너무 많은 객체를 fixture에 넣으면 테스트의 의도가 불분명해진다 |
| 테스트 간 일관성 보장 | 각 테스트가 어떤 fixture를 사용하는지 파악하기 어려울 수 있다 |
| 변경 시 한 곳만 수정 | fixture 변경이 의도치 않은 테스트 실패를 유발할 수 있다 |

> **핵심 통찰**: Fixture는 "중복 제거"와 "가독성" 사이의 균형이다. 테스트를 읽는 사람이 `setUp()`을 보지 않고도 테스트의 의도를 파악할 수 있어야 한다. fixture가 너무 복잡하다면 테스트 클래스를 분리하는 것을 고려한다.

---

## 4. External Fixture (외부 픽스처)

### 4.1 문제

파일, 데이터베이스 연결, 네트워크 소켓 등 외부 자원을 사용하는 테스트에서, 테스트 후 자원을 어떻게 정리하는가?

### 4.2 해결

**`tearDown()` 메서드에서 외부 자원을 해제한다.** `tearDown()`은 테스트가 성공하든 실패하든 예외가 발생하든 항상 실행되도록 보장해야 한다.

### 4.3 예시

```python
class DatabaseTest(TestCase):
    def setUp(self):
        self.connection = Database.connect("test_db")
        self.connection.begin_transaction()

    def testInsert(self):
        self.connection.execute("INSERT INTO users (name) VALUES ('Kent')")
        result = self.connection.execute("SELECT * FROM users WHERE name='Kent'")
        self.assert_true(len(result) == 1)

    def tearDown(self):
        self.connection.rollback()
        self.connection.close()
```

파일을 사용하는 예시:

```python
class FileTest(TestCase):
    def setUp(self):
        self.file = open("/tmp/test_output.txt", "w")

    def testWrite(self):
        self.file.write("hello")
        self.file.close()
        with open("/tmp/test_output.txt", "r") as f:
            self.assert_true(f.read() == "hello")

    def tearDown(self):
        import os
        if os.path.exists("/tmp/test_output.txt"):
            os.remove("/tmp/test_output.txt")
```

### 4.4 Part II와의 연결

Part II(Chapter 20, "Cleaning Up After")에서 정확히 이 패턴을 구현했다. `tearDown()` 호출을 `try-finally` 블록 안에 넣어 테스트 실패 여부와 관계없이 정리 코드가 실행되도록 보장했다:

```python
class TestCase:
    def run(self, result):
        result.testStarted()
        self.setUp()
        try:
            method = getattr(self, self.name)
            method()
        except:
            result.testFailed()
        self.tearDown()  # 항상 실행됨
        return result
```

### 4.5 왜 중요한가

| External Fixture가 없으면 | External Fixture가 있으면 |
|---------------------------|--------------------------|
| 테스트가 환경을 오염시킨다 | 각 테스트가 깨끗한 환경에서 시작한다 |
| 테스트 순서에 따라 결과가 달라진다 | 테스트 순서에 독립적이다 |
| 자원 누수가 발생한다 | 자원이 확실히 해제된다 |
| CI/CD 파이프라인에서 문제를 일으킨다 | 안정적인 자동화가 가능하다 |

> **핵심 통찰**: `tearDown()`은 `setUp()`의 거울이다. `setUp()`에서 할당한 모든 외부 자원은 `tearDown()`에서 해제해야 한다. "테스트가 실행되기 전과 후의 세상이 동일해야 한다"는 원칙을 기억하라.

---

## 5. Test Method (테스트 메서드)

### 5.1 문제

테스트를 어떻게 구조화하는가? 하나의 테스트 메서드에는 무엇이 들어가야 하는가?

### 5.2 해결

**하나의 테스트 메서드는 하나의 시나리오를 검증한다.** 메서드 이름은 그 시나리오를 설명해야 한다.

### 5.3 명명 규칙

좋은 테스트 메서드 이름은 테스트가 무엇을 검증하는지 즉시 알려준다:

```java
// 나쁜 이름
public void test1() { ... }
public void testDollar() { ... }

// 좋은 이름
public void testMultiplication() { ... }
public void testEqualityBetweenDifferentCurrencies() { ... }
public void testRoundingWhenConverting() { ... }
```

### 5.4 테스트 메서드의 구조: AAA 패턴

대부분의 테스트 메서드는 세 부분으로 구성된다:

```java
public void testMultiplicationByTwo() {
    // Arrange (준비)
    Dollar five = new Dollar(5);

    // Act (실행)
    Dollar result = five.times(2);

    // Assert (검증)
    assertEquals(new Dollar(10), result);
}
```

| 단계 | 역할 | 주의점 |
|------|------|--------|
| **Arrange** | 테스트에 필요한 객체와 상태 준비 | Fixture로 추출할 수 있다 |
| **Act** | 테스트 대상 행위 실행 | 보통 한 줄이다 |
| **Assert** | 기대 결과 검증 | 테스트의 핵심 목적이 여기 있다 |

### 5.5 하나의 시나리오, 하나의 테스트

하나의 테스트 메서드가 여러 시나리오를 검증하면 문제가 생긴다:

```java
// 나쁜 예: 너무 많은 시나리오
public void testDollarOperations() {
    Dollar five = new Dollar(5);
    assertEquals(new Dollar(10), five.times(2));   // 곱하기
    assertEquals(new Dollar(15), five.times(3));   // 또 다른 곱하기
    assertTrue(five.equals(new Dollar(5)));          // 동등성
    assertFalse(five.equals(new Dollar(6)));         // 비동등성
}

// 좋은 예: 각각 분리
public void testMultiplicationByTwo() {
    assertEquals(new Dollar(10), new Dollar(5).times(2));
}

public void testMultiplicationByThree() {
    assertEquals(new Dollar(15), new Dollar(5).times(3));
}

public void testEquality() {
    assertTrue(new Dollar(5).equals(new Dollar(5)));
}

public void testInequality() {
    assertFalse(new Dollar(5).equals(new Dollar(6)));
}
```

분리하면 어떤 시나리오가 실패했는지 즉시 알 수 있고, 실패한 테스트의 이름이 곧 문제의 설명이 된다.

> **핵심 통찰**: 테스트 메서드의 이름은 **실행 가능한 명세(executable specification)**다. `testMultiplicationByTwo`가 실패하면 "2를 곱하는 기능에 문제가 있다"는 것을 이름만으로 알 수 있다. 이것이 하나의 테스트에 하나의 시나리오를 넣는 이유다.

---

## 6. Exception Test (예외 테스트)

### 6.1 문제

코드가 특정 상황에서 올바르게 예외를 던지는지 어떻게 테스트하는가?

### 6.2 해결

**예외가 발생해야 하는 코드를 실행하고, 예외가 실제로 발생하는지 확인한다.** 예외가 발생하지 않으면 테스트 실패로 처리한다.

### 6.3 구현 방법

**방법 1: try-catch 패턴**

```java
public void testDivisionByZero() {
    try {
        new Dollar(10).divideBy(0);
        fail("ArithmeticException이 발생해야 한다");  // 여기에 도달하면 실패
    } catch (ArithmeticException e) {
        // 기대한 예외가 발생함 — 성공
    }
}
```

핵심은 `fail()` 호출이다. 예외가 발생하지 않고 이 줄에 도달하면 테스트가 실패한다.

**방법 2: 프레임워크 지원 (현대적 방식)**

```java
// JUnit 4+
@Test(expected = ArithmeticException.class)
public void testDivisionByZero() {
    new Dollar(10).divideBy(0);
}
```

```python
# Python unittest
def testDivisionByZero(self):
    with self.assertRaises(ZeroDivisionError):
        Dollar(10).divide_by(0)
```

```python
# pytest
def test_division_by_zero():
    with pytest.raises(ZeroDivisionError):
        Dollar(10).divide_by(0)
```

### 6.4 예외 메시지 검증

단순히 예외 타입뿐 아니라, 예외 메시지까지 검증하면 더 정확한 테스트가 된다:

```python
def testNegativeAmount(self):
    with self.assertRaises(ValueError) as context:
        Dollar(-5)
    self.assertEqual("금액은 0 이상이어야 합니다", str(context.exception))
```

> **핵심 통찰**: 예외도 코드의 행위(behavior)다. "이 상황에서 예외가 발생해야 한다"는 요구사항은 "이 상황에서 10을 반환해야 한다"와 동일한 수준의 중요성을 가진다. Exception Test는 에러 경로도 TDD로 다룰 수 있게 해준다.

---

## 7. All Tests (모든 테스트)

### 7.1 문제

시스템의 모든 테스트를 한 번에 실행하려면 어떻게 해야 하는가?

### 7.2 해결

**모든 테스트 스위트(suite)를 하나의 스위트로 합성(compose)한다.** Composite 패턴을 활용하여 개별 테스트와 테스트 스위트를 동일하게 취급한다.

### 7.3 구조

```
AllTests
├── MoneyTests
│   ├── testMultiplication
│   ├── testEquality
│   └── testCurrencyConversion
├── BankTests
│   ├── testReduce
│   └── testExchangeRate
└── ExpressionTests
    ├── testAddition
    └── testMixedCurrency
```

### 7.4 구현

Part II에서 구현한 `TestSuite`가 이 패턴의 핵심이다:

```python
class TestSuite:
    def __init__(self):
        self.tests = []

    def add(self, test):
        self.tests.append(test)

    def run(self, result):
        for test in self.tests:
            test.run(result)
        return result
```

모든 테스트를 조합하는 코드:

```python
suite = TestSuite()

# 개별 테스트 추가
suite.add(TestMultiplication("testMultiply"))
suite.add(TestMultiplication("testMultiplyByZero"))

# 하위 스위트 추가 (Composite)
bank_suite = TestSuite()
bank_suite.add(TestBank("testReduce"))
bank_suite.add(TestBank("testExchangeRate"))
suite.add(bank_suite)

# 모든 테스트 실행
result = TestResult()
suite.run(result)
print(result.summary())  # "5 run, 0 failed"
```

### 7.5 Part II와의 연결

Chapter 23("How Suite It Is")에서 `TestSuite`를 구현했다. `TestSuite`와 `TestCase`가 동일한 `run(result)` 인터페이스를 공유하여 Composite 패턴을 구현했다. 이 덕분에 개별 테스트든 테스트 그룹이든 동일하게 실행할 수 있다.

### 7.6 현대적 관행

현대 테스트 프레임워크들은 테스트 발견(test discovery)을 자동화한다:

| 프레임워크 | 자동 발견 방법 |
|-----------|---------------|
| JUnit | `@Test` 어노테이션이 붙은 메서드 자동 탐색 |
| pytest | `test_`로 시작하는 파일과 함수 자동 탐색 |
| Go testing | `Test`로 시작하는 함수 자동 탐색 |
| Jest | `*.test.js` 또는 `*.spec.js` 파일 자동 탐색 |

자동 발견이 있더라도 "All Tests" 개념은 중요하다. CI/CD 파이프라인에서 `npm test` 또는 `mvn test` 한 줄로 모든 테스트를 실행할 수 있어야 한다. 테스트가 하나라도 실패하면 빌드가 실패해야 한다.

> **핵심 통찰**: "모든 테스트를 한 번에 실행할 수 있는가?"는 TDD 실천의 기본 전제다. 테스트 실행이 번거롭거나 느리면 개발자는 테스트를 점점 덜 실행하게 되고, TDD의 리듬이 깨진다. 테스트 실행은 **일상적이고 빈번하고 자동적**이어야 한다.

---

## 8. 패턴들의 관계

xUnit 패턴들은 서로 연결되어 완전한 테스트 인프라를 형성한다:

```
TestCase (테스트의 단위)
├── Test Method (하나의 시나리오)
│   └── Assertion (검증)
│       └── Exception Test (예외 검증)
├── Fixture (공통 준비)
│   └── External Fixture (외부 자원 정리)
└── All Tests (전체 실행)
    └── TestSuite (Composite 패턴)
```

| 패턴 | Part II 참조 | 핵심 역할 |
|------|-------------|-----------|
| Assertion | Chapter 21 | 통과/실패 판정 |
| Fixture | Chapter 19 | 테스트 준비 |
| External Fixture | Chapter 20 | 자원 정리 |
| Test Method | Chapter 18 | 시나리오 격리 |
| Exception Test | — | 에러 경로 검증 |
| All Tests | Chapter 23 | 전체 실행 |

---

## 요약

- **Assertion**은 테스트의 핵심 — 기대값과 실제값을 비교하여 통과/실패를 자동 판정한다. 구체적인 assertion 메서드(`assertEqual` 등)를 사용하면 실패 메시지가 유의미해진다.
- **Fixture**는 여러 테스트가 공유하는 객체를 `setUp()`에서 준비하여 중복을 제거한다. 단, 테스트의 가독성을 해치지 않도록 주의한다.
- **External Fixture**는 파일, DB 등 외부 자원을 `tearDown()`에서 확실히 정리한다. 테스트 전후로 환경이 동일해야 한다.
- **Test Method**는 하나의 시나리오를 하나의 메서드에 담는다. 메서드 이름이 실행 가능한 명세 역할을 한다.
- **Exception Test**는 에러 경로를 검증한다. 예외도 코드의 행위이며, 테스트해야 하는 대상이다.
- **All Tests**는 모든 테스트를 한 번에 실행할 수 있는 구조다. Composite 패턴으로 테스트를 합성한다.
- 이 모든 패턴은 Part II에서 직접 구현했으며, 현대 xUnit 프레임워크의 근간을 이룬다.

---

## 다른 챕터와의 관계

- **Chapter 18~24 (Part II: xUnit Example)**: 이 챕터의 모든 패턴을 직접 TDD로 구현한 과정이다. Part II를 읽은 후 이 챕터를 읽으면 "왜 그렇게 만들었는지"를 패턴 수준에서 이해할 수 있다.
- **Chapter 25 (TDD Patterns)**: Test Method와 Assertion은 TDD 패턴의 핵심 도구다. 25장에서 다룬 "테스트 목록"과 결합하면 테스트 작성의 완전한 워크플로가 된다.
- **Chapter 27 (Testing Patterns)**: xUnit 패턴이 "프레임워크를 어떻게 사용하는가"라면, 테스팅 패턴은 "테스트를 어떻게 설계하는가"다. 두 관점이 결합되어야 효과적인 테스트를 작성할 수 있다.
- **Chapter 30 (Design Patterns)**: All Tests의 TestSuite는 Composite 패턴의 적용이다. Fixture의 `setUp()`은 Template Method 패턴이다. 설계 패턴이 xUnit 구현 곳곳에 녹아 있다.
