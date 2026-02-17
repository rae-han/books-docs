# Chapter 23: How Suite It Is (스위트의 멋)

## 핵심 질문

여러 개의 테스트를 하나로 묶어서 한 번에 실행하려면 어떻게 해야 하는가? 개별 테스트와 테스트 묶음을 동일한 방식으로 다룰 수 있는가?

---

## 1. 문제 인식: 테스트를 일일이 실행하는 고통

### 1.1 현재의 한계

Chapter 22까지의 코드에서 테스트를 실행하려면 이렇게 해야 한다:

```python
TestCaseTest("testTemplateMethod").run()
TestCaseTest("testResult").run()
TestCaseTest("testFailedResult").run()
```

테스트가 3개일 때는 괜찮다. 하지만 테스트가 50개, 100개로 늘어나면? 매번 새 테스트를 추가할 때마다 맨 아래에 실행 코드를 추가해야 한다. 이것은 **확장 가능하지 않다(not scalable)**.

### 1.2 TestSuite의 필요성

필요한 것은 여러 테스트를 하나의 **컬렉션**으로 묶고, `run()` 한 번으로 **모든 테스트를 실행**하는 방법이다. 이것이 **TestSuite**다.

원하는 사용법:

```python
suite = TestSuite()
suite.add(TestCaseTest("testTemplateMethod"))
suite.add(TestCaseTest("testResult"))
suite.add(TestCaseTest("testFailedResult"))
result = suite.run()
print(result.summary())  # "3 run, 0 failed"
```

> **핵심 통찰**: TestSuite는 **Composite 패턴**의 전형적인 예다. 개별 테스트(TestCase)와 테스트 묶음(TestSuite) 모두 `run()` 메서드를 가진다. 사용자는 하나의 테스트를 실행하든 100개의 테스트를 묶어 실행하든 **같은 인터페이스**를 사용한다.

---

## 2. Composite 패턴

### 2.1 패턴 설명

Composite 패턴은 **개별 객체와 객체의 컬렉션을 동일하게 취급**할 수 있게 하는 설계 패턴이다.

```
         ┌──────────┐
         │  "run()" │  ← 공통 인터페이스
         └────┬─────┘
              │
     ┌────────┴────────┐
     │                 │
┌────┴─────┐    ┌──────┴──────┐
│ TestCase │    │  TestSuite  │
│ (잎)     │    │ (컴포지트)  │
│ run()    │    │ run()       │
│ — 자신을 │    │ — 포함된    │
│   실행   │    │   모든 것을 │
│          │    │   실행      │
└──────────┘    └─────────────┘
                      │
               ┌──────┴──────┐
               │ tests 리스트│
               │ [TestCase,  │
               │  TestCase,  │
               │  TestSuite] │ ← TestSuite도 포함 가능!
               └─────────────┘
```

핵심: `TestSuite`의 `tests` 리스트에는 `TestCase`뿐만 아니라 **다른 `TestSuite`도 넣을 수 있다**. 이것이 Composite의 진정한 힘이다 — 트리 구조로 테스트를 조직할 수 있다.

### 2.2 실제 사례

```python
# 단위 테스트 스위트
unit_suite = TestSuite()
unit_suite.add(MoneyTest("testMultiplication"))
unit_suite.add(MoneyTest("testEquality"))

# 통합 테스트 스위트
integration_suite = TestSuite()
integration_suite.add(DatabaseTest("testConnection"))

# 전체 스위트 (스위트의 스위트!)
all_tests = TestSuite()
all_tests.add(unit_suite)
all_tests.add(integration_suite)

result = all_tests.run()  # 모든 테스트 실행
```

---

## 3. TDD 사이클

### 3.1 Red — TestSuite 테스트

`TestSuite`를 사용하여 여러 테스트를 실행하고, 결과가 올바른지 확인하는 테스트를 작성한다:

```python
class TestCaseTest(TestCase):
    def testSuite(self):
        suite = TestSuite()
        suite.add(WasRun("testMethod"))
        suite.add(WasRun("testBrokenMethod"))
        result = suite.run()
        assert("2 run, 1 failed" == result.summary())
```

이 테스트의 의미:
- 2개의 테스트를 스위트에 추가한다: 하나는 성공(`testMethod`), 하나는 실패(`testBrokenMethod`)
- 스위트를 실행한다
- 결과가 `"2 run, 1 failed"`여야 한다

이 테스트는 실패한다 — `TestSuite` 클래스가 아직 없기 때문이다. Red Bar!

### 3.2 Green — TestSuite 구현

**Step 1**: `TestSuite` 클래스 생성

```python
class TestSuite:
    def __init__(self):
        self.tests = []

    def add(self, test):
        self.tests.append(test)

    def run(self):
        result = TestResult()
        for test in self.tests:
            test.run(result)
        return result
```

구조:
- `tests`: 테스트 객체들을 담는 리스트
- `add(test)`: 리스트에 테스트 추가
- `run()`: 하나의 `TestResult`를 만들고, 각 테스트에 전달하여 실행

**주의**: `test.run(result)` — 이전에는 `test.run()`이 `TestResult`를 **내부에서 생성**했는데, 이제는 `TestResult`를 **외부에서 받아야** 한다. 왜? 여러 테스트가 **같은 `TestResult` 객체에 결과를 누적**해야 하기 때문이다.

**Step 2**: `TestCase.run()` 수정 — `TestResult`를 매개변수로 받기

```python
class TestCase:
    def __init__(self, name):
        self.name = name

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def run(self, result):
        result.testStarted()
        self.setUp()
        try:
            method = getattr(self, self.name)
            method()
        except:
            result.testFailed()
        self.tearDown()
```

변경 사항:
1. `run(self)` → `run(self, result)`: `TestResult`를 매개변수로 받는다
2. `result = TestResult()` 삭제: 더 이상 내부에서 생성하지 않는다
3. `return result` 삭제: 반환 대신 매개변수로 받은 `result`에 기록한다

이것이 **Collecting Parameter 패턴**의 완성이다. Chapter 21에서 언급했던 "반환 방식 vs 매개변수 방식"의 전환이 여기서 일어난다.

**Step 3**: 기존 테스트 수정

`run()`의 시그니처가 바뀌었으므로, 기존 테스트도 수정해야 한다:

```python
class TestCaseTest(TestCase):
    def testTemplateMethod(self):
        test = WasRun("testMethod")
        result = TestResult()
        test.run(result)
        assert("setUp testMethod tearDown " == test.log)

    def testResult(self):
        test = WasRun("testMethod")
        result = TestResult()
        test.run(result)
        assert("1 run, 0 failed" == result.summary())

    def testFailedResult(self):
        test = WasRun("testBrokenMethod")
        result = TestResult()
        test.run(result)
        assert("1 run, 1 failed" == result.summary())

    def testSuite(self):
        suite = TestSuite()
        suite.add(WasRun("testMethod"))
        suite.add(WasRun("testBrokenMethod"))
        result = TestResult()
        suite.run(result)
        assert("2 run, 1 failed" == result.summary())
```

모든 테스트에서 `TestResult`를 먼저 생성하고 `run()`에 전달하는 패턴으로 바뀌었다.

> 참고: `TestSuite.run()`도 매개변수 방식으로 수정한다:

```python
class TestSuite:
    def __init__(self):
        self.tests = []

    def add(self, test):
        self.tests.append(test)

    def run(self, result):
        for test in self.tests:
            test.run(result)
```

`TestSuite.run(result)`는 받은 `result`를 각 `test.run(result)`에 그대로 전달한다. 모든 테스트의 결과가 하나의 `TestResult`에 누적된다.

테스트를 실행한다:

```python
suite = TestSuite()
suite.add(TestCaseTest("testTemplateMethod"))
suite.add(TestCaseTest("testResult"))
suite.add(TestCaseTest("testFailedResult"))
suite.add(TestCaseTest("testSuite"))
result = TestResult()
suite.run(result)
print(result.summary())  # "4 run, 0 failed"
```

통과! **TestSuite가 자기 자신을 테스트하는 데 사용되고 있다.** 부트스트래핑의 아름다움이다. Green Bar!

### 3.3 Refactor — 인터페이스의 통일

`TestCase.run(result)`와 `TestSuite.run(result)` 모두 같은 시그니처를 가진다. 이것이 Composite 패턴의 핵심이다:

```python
# TestCase
def run(self, result):
    # 자기 자신(하나의 테스트)을 실행

# TestSuite
def run(self, result):
    # 포함된 모든 테스트를 실행
    for test in self.tests:
        test.run(result)  # test가 TestCase든 TestSuite든 동일하게 호출
```

`TestSuite.run()`의 `for test in self.tests:` 루프에서 `test`가 `TestCase`인지 `TestSuite`인지 **확인하지 않는다**. 둘 다 `run(result)`를 가지므로 **다형성(polymorphism)** 으로 처리된다.

> **핵심 통찰**: Composite 패턴의 핵심 가치는 **클라이언트 코드의 단순화**다. `TestSuite.run()`은 내부의 각 요소가 개별 테스트인지 하위 스위트인지 모른다. `run(result)`만 호출할 뿐이다. 이 무관심이 곧 유연성이다.

---

## 4. Collecting Parameter 패턴의 완성

### 4.1 패턴의 흐름

```
TestSuite.run(result)
    │
    ├── test1.run(result)  →  result.testStarted() + result.testFailed()?
    │
    ├── test2.run(result)  →  result.testStarted() + result.testFailed()?
    │
    └── test3.run(result)  →  result.testStarted() + result.testFailed()?

    result.summary()  →  "3 run, 1 failed"
```

하나의 `TestResult` 객체가 여러 `run()` 호출을 거치며 결과를 **누적**한다. 마치 바구니를 들고 다니면서 각 과일 가게에서 과일을 담는 것과 같다.

### 4.2 반환 방식에서 매개변수 방식으로의 전환

| 챕터 | 방식 | 코드 | 이유 |
|------|------|------|------|
| Chapter 21 | 반환 | `result = test.run()` | 단순함 우선 |
| Chapter 23 | 매개변수 | `test.run(result)` | 여러 테스트가 같은 result에 누적 필요 |

이 전환은 **필요에 의한 설계 변경**의 좋은 예다. 처음에는 더 단순한 방식(반환)을 사용했고, `TestSuite`가 필요해지자 더 유연한 방식(매개변수)으로 전환했다. TDD에서는 "나중에 필요할 것 같아서" 미리 유연하게 만들지 않는다. **실제로 필요해질 때** 변경한다.

---

## 5. 이 챕터에서 완성된 코드

```python
class TestResult:
    def __init__(self):
        self.runCount = 0
        self.failureCount = 0

    def testStarted(self):
        self.runCount = self.runCount + 1

    def testFailed(self):
        self.failureCount = self.failureCount + 1

    def summary(self):
        return "%d run, %d failed" % (self.runCount, self.failureCount)


class TestCase:
    def __init__(self, name):
        self.name = name

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def run(self, result):
        result.testStarted()
        self.setUp()
        try:
            method = getattr(self, self.name)
            method()
        except:
            result.testFailed()
        self.tearDown()


class TestSuite:
    def __init__(self):
        self.tests = []

    def add(self, test):
        self.tests.append(test)

    def run(self, result):
        for test in self.tests:
            test.run(result)


class WasRun(TestCase):
    def setUp(self):
        self.log = "setUp "

    def testMethod(self):
        self.log = self.log + "testMethod "

    def testBrokenMethod(self):
        raise Exception

    def tearDown(self):
        self.log = self.log + "tearDown "


class TestCaseTest(TestCase):
    def testTemplateMethod(self):
        test = WasRun("testMethod")
        result = TestResult()
        test.run(result)
        assert("setUp testMethod tearDown " == test.log)

    def testResult(self):
        test = WasRun("testMethod")
        result = TestResult()
        test.run(result)
        assert("1 run, 0 failed" == result.summary())

    def testFailedResult(self):
        test = WasRun("testBrokenMethod")
        result = TestResult()
        test.run(result)
        assert("1 run, 1 failed" == result.summary())

    def testSuite(self):
        suite = TestSuite()
        suite.add(WasRun("testMethod"))
        suite.add(WasRun("testBrokenMethod"))
        result = TestResult()
        suite.run(result)
        assert("2 run, 1 failed" == result.summary())


suite = TestSuite()
suite.add(TestCaseTest("testTemplateMethod"))
suite.add(TestCaseTest("testResult"))
suite.add(TestCaseTest("testFailedResult"))
suite.add(TestCaseTest("testSuite"))
result = TestResult()
suite.run(result)
print(result.summary())
```

실행 결과:

```
4 run, 0 failed
```

**모든 테스트가 통과!** 그리고 이 결과 자체가 `TestSuite`와 `TestResult`를 사용하여 출력되었다. 프레임워크가 자기 자신을 완전히 테스트하고 보고하고 있다.

---

## 6. 코드 변화 요약

| 변경 | 내용 |
|------|------|
| `TestSuite` 클래스 신규 | `tests` 리스트, `add()`, `run(result)` |
| `TestCase.run()` 수정 | `run()` → `run(self, result)`, 내부 생성 → 외부 수신 |
| `TestCaseTest` 전체 수정 | 모든 테스트에서 `TestResult()`를 먼저 생성하고 전달 |
| 실행 코드 변경 | 개별 `run()` 호출 → `TestSuite`로 묶어서 한 번에 실행 |

---

## TODO 리스트 (챕터 종료 시점)

- [x] ~~테스트 메서드 호출하기~~
- [x] ~~setUp 먼저 호출하기~~
- [x] ~~tearDown 나중에 호출하기~~
- [ ] 테스트 메서드가 실패해도 tearDown 호출하기
- [x] ~~여러 테스트 실행하기~~
- [x] ~~수집된 결과를 출력하기~~
- [x] ~~WasRun에서 로그 문자열 사용하기~~
- [x] ~~실패한 테스트 보고하기~~
- [ ] setUp 에러를 잡아서 보고하기
- [x] ~~TestSuite 만들기~~

`여러 테스트 실행하기`와 `TestSuite 만들기`가 완료되었다. 남은 항목은 엣지 케이스(tearDown의 예외 안전성, setUp 에러)로, Part II에서는 다루지 않고 남겨둔다.

---

## 요약

- **TestSuite**는 여러 테스트를 하나의 컬렉션으로 묶어 한 번에 실행한다. `add(test)`로 테스트를 추가하고 `run(result)`로 실행한다.
- **Composite 패턴**: `TestCase`와 `TestSuite` 모두 `run(result)` 메서드를 가진다. 사용자는 개별 테스트든 스위트든 같은 방식으로 실행할 수 있다. `TestSuite` 안에 다른 `TestSuite`를 넣을 수도 있다.
- **Collecting Parameter 패턴**: `TestResult`를 매개변수로 전달하여 여러 테스트의 결과를 하나의 객체에 누적한다. `run()`의 시그니처가 `run()` → `run(self, result)`로 변경되었다.
- 프레임워크가 이제 **자기 자신을 `TestSuite`로 묶어 테스트하고, `TestResult`로 결과를 보고**한다. 부트스트래핑이 완성되었다.
- 설계 변경(반환 → 매개변수)은 **필요에 의해** 이루어졌다. 미리 예측하여 유연하게 만든 것이 아니라, `TestSuite`가 필요해지자 그에 맞게 변경했다.

---

## 다른 챕터와의 관계

- **Chapter 21 (Counting)**: `TestResult`를 도입한 챕터. 이 챕터에서 `TestResult`의 사용 방식이 "반환"에서 "매개변수 전달"로 진화했다.
- **Chapter 22 (Dealing with Failure)**: 실패 보고 기능이 `TestSuite`와 결합되어, 스위트 내의 개별 실패가 전체 결과에 누적된다.
- **Chapter 24 (xUnit Retrospective)**: Part II 전체를 회고하며, TestSuite를 포함한 전체 구조를 실제 xUnit 프레임워크와 비교한다.
- **Chapter 30 (Design Patterns)**: Composite 패턴과 Collecting Parameter 패턴이 TDD 맥락에서 정리된다.
- **Chapter 12 (Addition, Finally)**: Part I의 Expression 인터페이스처럼, Part II에서도 `run(result)`라는 공통 인터페이스가 다형성의 기반이 된다. 두 파트에서 같은 설계 원칙이 반복된다.
