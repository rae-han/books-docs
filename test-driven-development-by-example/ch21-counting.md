# Chapter 21: Counting (세기)

## 핵심 질문

테스트 프레임워크가 테스트 실행 결과를 어떻게 수집하고 보고하는가? "몇 개의 테스트를 실행했고, 몇 개가 실패했는가"라는 정보를 어떻게 깔끔하게 추적할 수 있는가?

---

## 1. 문제 인식: 테스트 결과의 부재

### 1.1 현재의 한계

Chapter 20까지 만든 프레임워크는 테스트를 실행할 수 있지만, **결과를 보고하는 기능이 없다**. 테스트가 성공했는지 실패했는지를 알려면 `assert`가 예외를 던지지 않았는지를 간접적으로 확인해야 한다.

실제 테스트 프레임워크는 실행 후에 이런 요약을 보여준다:

```
5 run, 0 failed
```

또는 실패가 있을 때:

```
5 run, 2 failed
```

이것은 프로그래머에게 **즉각적인 피드백**을 준다. Green Bar(모두 통과)인지 Red Bar(실패 있음)인지를 한눈에 알 수 있다.

### 1.2 TestResult의 필요성

테스트 실행 결과를 수집하는 전용 객체가 필요하다. Kent Beck은 이것을 **TestResult**라고 부른다.

| 역할 | 설명 |
|------|------|
| 실행 횟수 추적 | 몇 개의 테스트가 실행되었는가? |
| 실패 횟수 추적 | 몇 개의 테스트가 실패했는가? |
| 요약 출력 | `"N run, M failed"` 형식의 문자열 반환 |

> **핵심 통찰**: TestResult를 별도의 객체로 분리하는 것은 **단일 책임 원칙(SRP)** 의 적용이다. TestCase는 테스트 실행에 집중하고, TestResult는 결과 수집에 집중한다. 각 객체가 자신의 역할에만 관심을 가진다.

---

## 2. TDD 사이클

### 2.1 Red — 첫 번째 테스트: 결과 요약

우리가 원하는 동작을 먼저 테스트로 표현한다. 하나의 테스트를 실행하면 결과가 `"1 run, 0 failed"`여야 한다:

```python
class TestCaseTest(TestCase):
    def testResult(self):
        test = WasRun("testMethod")
        result = test.run()
        assert("1 run, 0 failed" == result.summary())
```

이 테스트에는 두 가지 새로운 것이 있다:
1. `run()`이 **`TestResult` 객체를 반환**한다
2. `TestResult`에 `summary()` 메서드가 있다

이 테스트는 실패한다 — `run()`이 아무것도 반환하지 않으며, `TestResult` 클래스도 존재하지 않는다. Red Bar!

### 2.2 Green — TestResult 구현

**Step 1**: `TestResult` 클래스 생성

가장 간단한 구현부터 시작한다. Fake It 전략을 사용할 수도 있지만, 여기서는 구현이 충분히 명백(Obvious Implementation)하므로 바로 작성한다:

```python
class TestResult:
    def __init__(self):
        self.runCount = 0

    def testStarted(self):
        self.runCount = self.runCount + 1

    def summary(self):
        return "%d run, 0 failed" % self.runCount
```

`TestResult`의 구조:
- `runCount`: 실행된 테스트 수를 추적하는 카운터
- `testStarted()`: 테스트가 시작될 때 호출되어 카운터를 증가
- `summary()`: `"N run, 0 failed"` 형식의 문자열 반환 (실패 횟수는 아직 하드코딩)

**Step 2**: `TestCase.run()`에서 `TestResult`를 생성하고 반환

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
        method = getattr(self, self.name)
        method()
        self.tearDown()
        return result
```

핵심 변경:
1. `TestResult` 객체를 생성한다
2. `testStarted()`를 호출하여 카운트를 증가시킨다
3. 기존 로직(setUp → testMethod → tearDown)을 실행한다
4. `result`를 **반환**한다

테스트를 실행한다:

```python
TestCaseTest("testResult").run()
```

통과! `result.summary()`가 `"1 run, 0 failed"`를 반환한다. Green Bar!

### 2.3 Refactor — 실패 횟수의 하드코딩

현재 `summary()`에서 실패 횟수가 `0`으로 하드코딩되어 있다:

```python
def summary(self):
    return "%d run, 0 failed" % self.runCount  # 0은 하드코딩!
```

이것은 Fake It과 비슷한 상황이다. 아직 실패를 추적하는 기능이 없으므로 0으로 놔둔다. 실패 추적은 TODO 리스트에 있고, Chapter 22에서 다룬다.

지금은 이 정도의 불완전함을 수용한다. **동작하는 불완전한 코드가, 동작하지 않는 완전한 코드보다 낫다.**

> **핵심 통찰**: Kent Beck은 `summary()`에서 `0 failed`를 하드코딩하는 것에 불편함을 느끼지 않는다. 이것은 다음 단계에서 해결할 문제다. TDD에서는 **한 번에 하나씩** 해결한다. 지금은 "실행 횟수 추적"이라는 하나의 목표에 집중하고 있다.

---

## 3. 기존 테스트와의 공존

### 3.1 testTemplateMethod 수정

`run()`이 이제 `TestResult`를 반환하므로, 기존의 `testTemplateMethod`도 여전히 동작하는지 확인해야 한다:

```python
class TestCaseTest(TestCase):
    def testTemplateMethod(self):
        test = WasRun("testMethod")
        test.run()
        assert("setUp testMethod tearDown " == test.log)

    def testResult(self):
        test = WasRun("testMethod")
        result = test.run()
        assert("1 run, 0 failed" == result.summary())
```

`testTemplateMethod`는 `run()`의 반환값을 사용하지 않으므로 (`test.run()`의 반환값을 변수에 담지 않음), `run()`이 `TestResult`를 반환하도록 바뀌어도 기존 동작에 영향이 없다.

두 테스트를 모두 실행한다:

```python
TestCaseTest("testTemplateMethod").run()
TestCaseTest("testResult").run()
```

둘 다 통과한다. 기존 기능을 깨뜨리지 않고 새 기능을 추가했다.

### 3.2 여러 테스트 실행의 번거로움

지금은 각 테스트를 수동으로 하나씩 실행해야 한다:

```python
TestCaseTest("testTemplateMethod").run()
TestCaseTest("testResult").run()
```

테스트가 늘어나면 이것은 점점 더 번거로워진다. **TestSuite**가 필요하다. 이것은 Chapter 23의 주제다.

---

## 4. TestResult의 설계 분석

### 4.1 Collecting Parameter 패턴

`TestResult`는 **Collecting Parameter** 패턴의 예다. 이 패턴에서:

1. 결과를 수집할 객체를 만든다 (`TestResult`)
2. 여러 작업을 실행하면서 결과를 그 객체에 누적한다 (`testStarted()`)
3. 작업이 끝나면 수집된 결과를 확인한다 (`summary()`)

이 패턴은 나중에 `TestSuite`와 함께 더 강력해진다. 여러 테스트가 **하나의 `TestResult` 객체에 결과를 누적**하면, 전체 테스트 스위트의 요약을 한 번에 볼 수 있다.

### 4.2 왜 run()이 TestResult를 반환하는가?

두 가지 설계 선택이 가능하다:

| 방법 | 코드 | 장단점 |
|------|------|--------|
| **반환** | `result = test.run()` | 단순하고 함수형 스타일. 호출자가 결과를 받아 처리 |
| **매개변수** | `test.run(result)` | TestSuite에서 여러 테스트가 같은 result에 누적 가능 |

Kent Beck은 지금은 **반환 방식**을 사용하지만, Chapter 23에서 `TestSuite`를 구현할 때 **매개변수 방식**으로 바꿀 수도 있다. 지금은 더 단순한 방식을 선택한다.

---

## 5. 이 챕터에서 완성된 코드

```python
class TestResult:
    def __init__(self):
        self.runCount = 0

    def testStarted(self):
        self.runCount = self.runCount + 1

    def summary(self):
        return "%d run, 0 failed" % self.runCount


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
        method = getattr(self, self.name)
        method()
        self.tearDown()
        return result


class WasRun(TestCase):
    def setUp(self):
        self.log = "setUp "

    def testMethod(self):
        self.log = self.log + "testMethod "

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


TestCaseTest("testTemplateMethod").run()
TestCaseTest("testResult").run()
```

---

## 6. 코드 변화 추적

이 챕터에서 추가되거나 변경된 부분:

| 변경 | 설명 |
|------|------|
| `TestResult` 클래스 신규 | `runCount`, `testStarted()`, `summary()` |
| `TestCase.run()` 수정 | `TestResult` 생성, `testStarted()` 호출, `result` 반환 |
| `testResult` 테스트 추가 | `run()`이 올바른 `TestResult`를 반환하는지 검증 |

변경의 크기가 여전히 작다는 점에 주목하라. `TestResult`라는 새 클래스를 도입했지만, 그 내부는 매우 단순하다 — 카운터 하나와 포매팅 메서드 하나가 전부다.

---

## TODO 리스트 (챕터 종료 시점)

- [x] ~~테스트 메서드 호출하기~~
- [x] ~~setUp 먼저 호출하기~~
- [x] ~~tearDown 나중에 호출하기~~
- [ ] 테스트 메서드가 실패해도 tearDown 호출하기
- [ ] 여러 테스트 실행하기
- [x] ~~수집된 결과를 출력하기~~
- [x] ~~WasRun에서 로그 문자열 사용하기~~
- [ ] 실패한 테스트 보고하기
- [ ] setUp 에러를 잡아서 보고하기
- [ ] TestSuite 만들기

`수집된 결과를 출력하기`가 완료되었다. 다음 챕터에서는 실패한 테스트를 `TestResult`에 보고하는 기능을 구현한다.

---

## 요약

- **TestResult** 클래스를 도입하여 테스트 실행 결과를 수집한다. `runCount`로 실행 횟수를 추적하고, `summary()`로 `"N run, M failed"` 형식의 요약을 반환한다.
- `TestCase.run()`이 **`TestResult`를 생성하고 반환**하도록 변경되었다. 호출자는 반환된 결과를 통해 테스트 실행 상황을 파악할 수 있다.
- `summary()`에서 실패 횟수가 `0`으로 **하드코딩**되어 있다. 이것은 다음 챕터에서 해결할 문제다 — 한 번에 하나씩 해결하는 TDD의 원칙을 따른다.
- **Collecting Parameter 패턴**: `TestResult`는 여러 테스트의 결과를 하나의 객체에 누적한다. 나중에 `TestSuite`와 결합하면 더욱 강력해진다.
- 기존 테스트(`testTemplateMethod`)를 깨뜨리지 않으면서 새 기능(`testResult`)을 추가했다. 이것이 TDD가 보장하는 **회귀 안전성(regression safety)** 이다.

---

## 다른 챕터와의 관계

- **Chapter 20 (Cleaning Up After)**: 이 챕터에서 만든 `setUp → testMethod → tearDown` 흐름 위에 결과 수집 기능을 추가했다. `run()`의 역할이 "실행만 하기"에서 "실행하고 결과를 보고하기"로 확장되었다.
- **Chapter 22 (Dealing with Failure)**: `TestResult`에 실패 횟수 추적 기능을 추가한다. `summary()`의 하드코딩된 `0`이 실제 실패 카운트로 대체된다.
- **Chapter 23 (How Suite It Is)**: `TestSuite`가 여러 테스트를 실행하면서 하나의 `TestResult`에 결과를 누적한다. Collecting Parameter 패턴이 본격적으로 활용된다.
- **Chapter 28 (Green Bar Patterns)**: 이 챕터에서 사용한 Obvious Implementation 전략이 Part III에서 패턴으로 정리된다.
