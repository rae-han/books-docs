# Chapter 22: Dealing with Failure (실패 다루기)

## 핵심 질문

테스트가 실패했을 때 프레임워크는 어떻게 이를 감지하고 보고하는가? 하나의 테스트가 실패해도 나머지 테스트는 계속 실행되어야 하는데, 예외를 어떻게 잡아서 결과에 기록하는가?

---

## 1. 문제 인식: 실패를 보고해야 한다

### 1.1 현재의 한계

Chapter 21에서 만든 `TestResult`는 실행 횟수만 추적한다. 실패 횟수는 `0`으로 하드코딩되어 있다:

```python
def summary(self):
    return "%d run, 0 failed" % self.runCount  # 실패 횟수가 항상 0!
```

이것은 심각한 한계다. 테스트 프레임워크의 **가장 중요한 기능**은 "어떤 테스트가 실패했는가"를 알려주는 것이기 때문이다.

### 1.2 실패의 종류

테스트에서 발생할 수 있는 실패는 두 가지다:

| 종류 | 설명 | 예시 |
|------|------|------|
| **Assertion Failure** | 테스트의 기대값과 실제값이 다름 | `assert(1 == 2)` |
| **Error** | 테스트 실행 중 예기치 않은 예외 발생 | `NameError`, `TypeError` 등 |

Python에서는 둘 다 **예외(Exception)** 로 표현된다. `assert`가 실패하면 `AssertionError`가 발생하고, 다른 에러도 각각의 예외를 발생시킨다. 따라서 **예외를 잡아서 기록**하면 실패를 추적할 수 있다.

> **핵심 통찰**: 실패를 "보고"한다는 것은, 실패가 발생해도 프로그램이 중단되지 않고 **결과에 기록**된다는 뜻이다. 실패한 테스트가 있어도 나머지 테스트는 계속 실행되어야 한다. 하나의 실패가 전체 테스트 실행을 멈추게 해서는 안 된다.

---

## 2. TDD 사이클

### 2.1 Red — 실패한 테스트 보고를 테스트

실패하는 테스트를 실행했을 때, `TestResult`가 `"1 run, 1 failed"`를 보고하는지 확인하는 테스트를 작성한다.

먼저, **항상 실패하는 테스트 메서드**가 필요하다:

```python
class WasRun(TestCase):
    def setUp(self):
        self.log = "setUp "

    def testMethod(self):
        self.log = self.log + "testMethod "

    def testBrokenMethod(self):
        raise Exception  # 항상 예외를 던지는 테스트

    def tearDown(self):
        self.log = self.log + "tearDown "
```

`testBrokenMethod`는 의도적으로 예외를 발생시킨다. 이것을 사용하여 실패 보고를 테스트한다:

```python
class TestCaseTest(TestCase):
    def testFailedResult(self):
        test = WasRun("testBrokenMethod")
        result = test.run()
        assert("1 run, 1 failed" == result.summary())
```

이 테스트를 실행하면:

1. `WasRun("testBrokenMethod").run()`이 호출된다
2. `testBrokenMethod()`에서 `Exception`이 발생한다
3. 현재 코드에서는 이 예외가 **잡히지 않고 전파**된다
4. 프로그램이 **충돌**한다 — `result.summary()`에 도달하지도 못한다

Red Bar! (사실 Red Bar라기보다는 프로그램 자체가 죽는 상황이다)

### 2.2 Green — 예외를 잡아서 기록

`TestCase.run()`에서 테스트 메서드 호출을 `try/except`로 감싸서 예외를 잡는다:

**Step 1**: `TestResult`에 실패 카운터 추가

```python
class TestResult:
    def __init__(self):
        self.runCount = 0
        self.failureCount = 0  # 실패 카운터 추가

    def testStarted(self):
        self.runCount = self.runCount + 1

    def testFailed(self):
        self.failureCount = self.failureCount + 1  # 실패 시 호출

    def summary(self):
        return "%d run, %d failed" % (self.runCount, self.failureCount)
```

변경 사항:
- `failureCount` 필드 추가
- `testFailed()` 메서드 추가 — 테스트가 실패할 때 호출
- `summary()`에서 하드코딩된 `0` 대신 `self.failureCount` 사용

**Step 2**: `TestCase.run()`에서 예외를 잡아 기록

```python
class TestCase:
    def __init__(self, name):
        self.name = name

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def run(self):
        result = TestResult()
        result.testStarted()
        self.setUp()
        try:
            method = getattr(self, self.name)
            method()
        except:
            result.testFailed()
        self.tearDown()
        return result
```

핵심: `method()` 호출을 `try/except`로 감쌌다. 예외가 발생하면 `result.testFailed()`를 호출하여 실패를 기록하고, 프로그램은 **계속 실행**된다. `tearDown()`도 실행되며, 결과가 정상적으로 반환된다.

테스트를 실행한다:

```python
TestCaseTest("testFailedResult").run()
```

통과! `result.summary()`가 `"1 run, 1 failed"`를 반환한다. Green Bar!

### 2.3 Refactor — bare except의 문제

현재 코드에서 `except:` (bare except)를 사용하고 있다. 이것은 **모든 예외를 잡는다** — `KeyboardInterrupt`, `SystemExit` 등 시스템 예외까지. 실무에서는 이것이 위험할 수 있다.

더 나은 방식:

```python
try:
    method = getattr(self, self.name)
    method()
except Exception:
    result.testFailed()
```

`except Exception:`은 사용자 정의 예외와 일반적인 런타임 에러만 잡고, 시스템 종료 관련 예외는 잡지 않는다. Kent Beck의 예제에서는 단순함을 위해 bare except를 사용하지만, 실무에서는 이 구분이 중요하다.

> **핵심 통찰**: Kent Beck은 이 시점에서 완벽한 예외 처리를 하지 않는다. `except:`가 bare except라는 것을 알지만, **지금 해결해야 할 문제는 "실패를 기록할 수 있는가"** 이다. 더 세밀한 예외 처리는 필요할 때 추가할 수 있다.

---

## 3. tearDown()과 예외의 관계

### 3.1 현재 코드에서의 흐름

`try/except` 블록의 위치를 다시 살펴보자:

```python
def run(self):
    result = TestResult()
    result.testStarted()
    self.setUp()
    try:
        method = getattr(self, self.name)
        method()
    except:
        result.testFailed()
    self.tearDown()      # try/except 밖에 있으므로 항상 실행된다!
    return result
```

`self.tearDown()`은 `try/except` 블록 **밖에** 있다. 따라서:

- 테스트가 성공하면: `setUp → method → tearDown` (정상 흐름)
- 테스트가 실패하면: `setUp → method(예외) → except절 → tearDown` (실패해도 tearDown 실행)

예외가 `except`에서 잡히므로, `tearDown()`에 도달하지 못할 일이 없다. **테스트 실패 시에도 tearDown이 호출되는 것**이 보장된다!

### 3.2 setUp()에서의 실패는?

그러나 `setUp()`은 `try/except` 밖에 있다. 만약 `setUp()`에서 예외가 발생하면:

```python
def run(self):
    result = TestResult()
    result.testStarted()
    self.setUp()          # 여기서 예외가 발생하면?
    try:                  # 이 줄에 도달하지 못한다
        method = getattr(self, self.name)
        method()
    except:
        result.testFailed()
    self.tearDown()       # 여기도 도달하지 못한다!
    return result         # 여기도!
```

`setUp()` 실패는 아직 처리되지 않는다. TODO 리스트에 "setUp 에러를 잡아서 보고하기"가 있지만, 이 챕터에서는 다루지 않는다.

---

## 4. 전체 테스트 실행 및 검증

### 4.1 모든 테스트 동시 실행

현재까지의 모든 테스트를 실행한다:

```python
TestCaseTest("testTemplateMethod").run()
TestCaseTest("testResult").run()
TestCaseTest("testFailedResult").run()
```

세 테스트 모두 통과한다:

| 테스트 | 검증 내용 |
|--------|----------|
| `testTemplateMethod` | `setUp → testMethod → tearDown` 순서로 실행되는가? |
| `testResult` | 성공한 테스트가 `"1 run, 0 failed"`를 보고하는가? |
| `testFailedResult` | 실패한 테스트가 `"1 run, 1 failed"`를 보고하는가? |

### 4.2 실패 보고의 의미

이제 프레임워크가 **자동으로 실패를 감지하고 보고**한다. 프로그래머는 더 이상:

- 테스트가 예외로 죽는 것을 지켜볼 필요가 없다
- 어떤 테스트가 실패했는지 추측할 필요가 없다
- 실패한 테스트 때문에 나머지 테스트를 실행하지 못할 걱정을 할 필요가 없다

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

    def run(self):
        result = TestResult()
        result.testStarted()
        self.setUp()
        try:
            method = getattr(self, self.name)
            method()
        except:
            result.testFailed()
        self.tearDown()
        return result


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
        test.run()
        assert("setUp testMethod tearDown " == test.log)

    def testResult(self):
        test = WasRun("testMethod")
        result = test.run()
        assert("1 run, 0 failed" == result.summary())

    def testFailedResult(self):
        test = WasRun("testBrokenMethod")
        result = test.run()
        assert("1 run, 1 failed" == result.summary())


TestCaseTest("testTemplateMethod").run()
TestCaseTest("testResult").run()
TestCaseTest("testFailedResult").run()
```

---

## 6. 예외 처리 전략 비교

Kent Beck의 xUnit에서 사용한 전략과 다른 접근법을 비교한다:

| 전략 | 동작 | 장점 | 단점 |
|------|------|------|------|
| **예외 전파 (현재 이전)** | 테스트 실패 시 프로그램 중단 | 구현이 단순 | 하나 실패하면 나머지 실행 불가 |
| **try/except (현재)** | 예외를 잡아서 결과에 기록 | 모든 테스트 실행 가능, 요약 제공 | bare except의 위험 |
| **try/finally** | tearDown 보장 | 리소스 정리 보장 | 예외가 여전히 전파됨 |
| **try/except/finally** | 예외도 잡고 tearDown도 보장 | 가장 견고함 | 코드가 복잡해짐 |

현재 코드는 `try/except`를 사용하되, `tearDown()`을 `except` 뒤에 배치하여 항상 실행되도록 했다. `try/finally`와 유사한 효과를 얻으면서도 코드가 단순하다.

> **핵심 통찰**: 완벽한 예외 처리보다 **동작하는 기본 구현**이 우선이다. 엣지 케이스(setUp 실패, tearDown 실패 등)는 필요해지면 그때 처리한다. 이것은 YAGNI(You Aren't Gonna Need It) 원칙과도 일맥상통한다.

---

## TODO 리스트 (챕터 종료 시점)

- [x] ~~테스트 메서드 호출하기~~
- [x] ~~setUp 먼저 호출하기~~
- [x] ~~tearDown 나중에 호출하기~~
- [ ] 테스트 메서드가 실패해도 tearDown 호출하기
- [ ] 여러 테스트 실행하기
- [x] ~~수집된 결과를 출력하기~~
- [x] ~~WasRun에서 로그 문자열 사용하기~~
- [x] ~~실패한 테스트 보고하기~~
- [ ] setUp 에러를 잡아서 보고하기
- [ ] TestSuite 만들기

`실패한 테스트 보고하기`가 완료되었다. `tearDown`의 예외 안전성과 `setUp` 에러 처리는 남아 있다. 다음 챕터에서는 `TestSuite`를 구현하여 여러 테스트를 한꺼번에 실행한다.

> 참고: "테스트 메서드가 실패해도 tearDown 호출하기"는 현재 코드에서 사실상 해결되었다 (`tearDown`이 `try/except` 밖에 있어 항상 실행됨). 하지만 Kent Beck은 이 항목을 명시적으로 "완료"로 표시하지 않는다 — `setUp` 실패 시의 동작이 아직 불확실하기 때문이다.

---

## 요약

- **테스트 실패 보고**는 테스트 프레임워크의 핵심 기능이다. 실패를 감지하고, 기록하고, 실행을 계속하며, 최종 요약을 제공한다.
- `TestResult`에 `failureCount`와 `testFailed()` 메서드를 추가하여 실패를 추적한다. `summary()`가 `"N run, M failed"` 형식으로 실패 횟수까지 보고한다.
- `TestCase.run()`에서 테스트 메서드 호출을 `try/except`로 감싸 예외를 잡는다. 예외가 발생하면 `result.testFailed()`를 호출하여 기록하고, 프로그램은 계속 실행된다.
- `tearDown()`은 `try/except` 블록 밖에 배치하여 **실패 시에도 항상 실행**되도록 했다.
- `setUp()` 실패는 아직 처리하지 않는다 — TODO 리스트에 기록하고 나중에 다룬다.
- `WasRun`에 `testBrokenMethod`를 추가하여 **의도적으로 실패하는 테스트**를 만들었다. 이것으로 실패 보고 기능을 테스트한다.

---

## 다른 챕터와의 관계

- **Chapter 21 (Counting)**: `TestResult`의 `summary()`에서 하드코딩되어 있던 `0 failed`를 실제 실패 카운트로 대체했다. `TestResult`가 "실행 횟수만 세기"에서 "실패 횟수도 세기"로 진화했다.
- **Chapter 20 (Cleaning Up After)**: `tearDown()`이 실패 시에도 호출되는 문제가 이 챕터에서 (부분적으로) 해결되었다. `try/except` 이후에 `tearDown()`이 실행되므로, 테스트 메서드 예외가 `tearDown()`을 건너뛰지 않는다.
- **Chapter 23 (How Suite It Is)**: `TestSuite`에서 여러 테스트를 실행할 때, 하나의 `TestResult`에 모든 결과를 누적한다. 실패한 테스트가 있어도 나머지 테스트는 계속 실행된다.
- **Chapter 27 (Testing Patterns)**: Part III에서 "어떤 테스트가 어떻게 실패했는가"를 더 상세히 보고하는 패턴이 논의된다. 여기서는 단순히 카운트만 했지만, 실제 프레임워크는 실패 메시지와 스택 트레이스도 제공한다.
- **Chapter 28 (Green Bar Patterns)**: 실패를 다루는 이 챕터의 접근법 — 가장 단순한 것부터 시작하여 점진적으로 견고하게 만드는 것 — 이 Green Bar 패턴의 실례다.
