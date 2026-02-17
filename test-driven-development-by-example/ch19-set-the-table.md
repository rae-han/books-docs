# Chapter 19: Set the Table (테이블 차리기)

## 핵심 질문

여러 테스트가 공통으로 필요한 준비 작업을 어떻게 깔끔하게 처리하는가? 테스트마다 동일한 초기화 코드를 반복하지 않으면서도, 각 테스트가 독립적으로 실행되도록 보장하려면 어떻게 해야 하는가?

---

## 1. 문제 인식: 테스트 픽스처(Test Fixture)

### 1.1 테스트에 필요한 준비물

실제 테스트를 작성하다 보면, 여러 테스트가 **동일한 객체 구조**를 필요로 하는 경우가 많다.

예를 들어, Part I의 Money 예제에서:

```python
# testMultiplication
five = Dollar(5)
product = five.times(2)
# ...

# testEquality
five_a = Dollar(5)
five_b = Dollar(5)
# ...
```

`Dollar(5)`라는 객체 생성이 여러 테스트에서 반복된다. 이러한 **테스트에 필요한 공통 객체와 데이터**를 **테스트 픽스처(Test Fixture)** 라고 한다.

### 1.2 픽스처 반복의 문제

픽스처 코드를 각 테스트에서 반복하면:

- **중복**: 같은 코드가 여러 곳에 존재한다
- **유지보수 비용**: 픽스처 구조가 바뀌면 모든 테스트를 수정해야 한다
- **가독성 저하**: 테스트의 핵심 로직이 준비 코드에 묻힌다

### 1.3 해결책: setUp()

xUnit의 해결책은 `setUp()` 메서드다. **각 테스트 메서드가 실행되기 전에 자동으로 호출**되는 메서드로, 공통 픽스처를 한 곳에서 준비한다.

> **핵심 통찰**: "테이블 차리기(Set the Table)"라는 챕터 제목은 비유다. 식사(테스트 실행) 전에 테이블을 차리는 것(setUp)처럼, 테스트 전에 필요한 환경을 준비한다. 여러 명이 식사를 해도(여러 테스트가 실행되어도) 매번 깨끗한 테이블을 차린다.

---

## 2. 테스트 픽스처 설정의 두 가지 접근

Kent Beck은 테스트 픽스처를 설정하는 두 가지 패턴을 대비한다:

| 접근 | 방식 | 장단점 |
|------|------|--------|
| **인라인 셋업** | 각 테스트 메서드 안에서 직접 준비 | 테스트가 자기 완결적, 하지만 중복 발생 |
| **외부 셋업 (setUp)** | setUp() 메서드에서 한번에 준비 | 중복 제거, 하지만 테스트 읽을 때 setUp을 같이 봐야 함 |

Kent Beck은 두 가지를 모두 사용하되, **3개 이상의 테스트에서 같은 준비 코드가 반복되면** `setUp()`으로 추출하는 것을 권장한다.

---

## 3. TDD 사이클

### 3.1 Red — setUp()이 호출되는지 테스트

`TestCaseTest`에 새 테스트를 추가한다. `setUp()` 메서드가 테스트 메서드 전에 호출되는지 확인해야 한다.

어떻게 확인할 수 있을까? Chapter 18에서 만든 `WasRun`의 `wasRun` 플래그와 같은 전략을 사용한다. `setUp()`이 호출되면 플래그를 설정하는 것이다.

```python
class TestCaseTest(TestCase):
    def testRunning(self):
        test = WasRun("testMethod")
        assert(not test.wasRun)
        test.run()
        assert(test.wasRun)

    def testSetUp(self):
        test = WasRun("testMethod")
        test.run()
        assert(test.wasSetUp)
```

이 테스트는 실패한다 — `WasRun`에 `wasSetUp` 속성이 없기 때문이다. Red Bar!

### 3.2 Green — setUp() 호출 구현

두 가지를 수정해야 한다:

1. `TestCase.run()`에서 테스트 메서드 전에 `setUp()`을 호출하도록 변경
2. `WasRun`에 `setUp()` 메서드를 추가하여 `wasSetUp` 플래그 설정

**Step 1**: `TestCase`에 `setUp()` 추가

```python
class TestCase:
    def __init__(self, name):
        self.name = name

    def setUp(self):
        pass  # 기본 구현은 아무것도 하지 않는다

    def run(self):
        self.setUp()  # 테스트 메서드 전에 setUp 호출!
        method = getattr(self, self.name)
        method()
```

`setUp()`의 기본 구현은 `pass`다. 하위 클래스가 필요에 따라 오버라이드한다.

**Step 2**: `WasRun`에서 `setUp()` 오버라이드

```python
class WasRun(TestCase):
    def __init__(self, name):
        self.wasRun = None
        TestCase.__init__(self, name)

    def setUp(self):
        self.wasSetUp = 1  # setUp이 호출되었음을 기록

    def testMethod(self):
        self.wasRun = 1
```

테스트 실행:

```python
TestCaseTest("testSetUp").run()
```

통과! `setUp()`이 `testMethod()` 전에 호출되어 `wasSetUp`이 `1`로 설정된다. Green Bar!

### 3.3 Refactor — setUp()을 활용하여 WasRun 간소화

이제 `setUp()`이 동작하므로, `WasRun`의 초기화를 `setUp()`으로 옮길 수 있다:

```python
class WasRun(TestCase):
    def setUp(self):
        self.wasRun = None   # __init__에서 setUp으로 이동
        self.wasSetUp = 1

    def testMethod(self):
        self.wasRun = 1
```

`__init__`에서 `self.wasRun = None`을 설정하던 것을 `setUp()`으로 이동했다. `__init__`에서는 더 이상 `WasRun` 고유의 초기화를 하지 않으므로, `__init__` 자체를 삭제할 수 있다 (상위 클래스 `TestCase.__init__`이 자동으로 호출된다... 는 Python에서는 아니지만, 여기서는 `name` 설정은 `TestCase.__init__`이 담당한다).

실제로 정리하면:

```python
class WasRun(TestCase):
    def setUp(self):
        self.wasRun = None
        self.wasSetUp = 1

    def testMethod(self):
        self.wasRun = 1
```

> **핵심 통찰**: `setUp()`은 단순히 편의 기능이 아니다. 핵심 가치는 **각 테스트가 깨끗한 상태에서 시작하도록 보장**하는 것이다. `run()`이 매번 `setUp()`을 호출하므로, 이전 테스트가 남긴 부작용이 다음 테스트에 영향을 주지 않는다. 이것이 **테스트 격리(Test Isolation)** 의 기반이다.

---

## 4. 로그 문자열로 실행 순서 추적하기

### 4.1 문제: 호출 순서를 어떻게 검증하는가?

`setUp()`이 `testMethod()` **전에** 호출되는 것이 중요하다. 하지만 현재의 `wasSetUp` 플래그만으로는 순서를 확인할 수 없다 — 두 메서드가 모두 호출되었다는 것만 알 수 있지, 어떤 순서로 호출되었는지는 알 수 없다.

### 4.2 해결: 로그 문자열(Log String)

Kent Beck은 **로그 문자열** 기법을 도입한다. 각 메서드가 호출될 때마다 자신의 이름을 문자열에 추가하는 것이다:

```python
class WasRun(TestCase):
    def setUp(self):
        self.log = "setUp "   # 로그 문자열 시작

    def testMethod(self):
        self.log = self.log + "testMethod "  # 로그에 추가
```

이제 `testMethod()` 실행 후 `self.log`를 확인하면 `"setUp testMethod "`가 된다. **호출 순서**가 문자열에 기록된다!

테스트도 더 간단해진다:

```python
class TestCaseTest(TestCase):
    def testTemplateMethod(self):
        test = WasRun("testMethod")
        test.run()
        assert("setUp testMethod " == test.log)
```

이 하나의 테스트가 두 가지를 동시에 검증한다:
1. `setUp()`이 호출되었다 (`"setUp"` 문자열이 존재)
2. `setUp()`이 `testMethod()` **전에** 호출되었다 (문자열 순서)

### 4.3 기존 테스트 정리

로그 문자열 테스트가 기존의 `testRunning`과 `testSetUp`을 대체하므로, 이들을 하나로 합칠 수 있다:

```python
class TestCaseTest(TestCase):
    def testTemplateMethod(self):
        test = WasRun("testMethod")
        test.run()
        assert("setUp testMethod " == test.log)

TestCaseTest("testTemplateMethod").run()
```

`testRunning`과 `testSetUp`은 더 이상 필요하지 않다. `testTemplateMethod` 하나가 모든 것을 검증한다.

> **핵심 통찰**: 로그 문자열은 **메서드 호출 순서를 검증하는 강력한 기법**이다. mock 객체의 `verify()` 호출이 하는 일을 단순한 문자열 비교로 달성한다. 이 기법은 Kent Beck이 xUnit을 넘어 실무에서도 자주 사용하는 패턴이다.

---

## 5. 이 챕터에서 완성된 코드

```python
class TestCase:
    def __init__(self, name):
        self.name = name

    def setUp(self):
        pass

    def run(self):
        self.setUp()
        method = getattr(self, self.name)
        method()


class WasRun(TestCase):
    def setUp(self):
        self.log = "setUp "

    def testMethod(self):
        self.log = self.log + "testMethod "


class TestCaseTest(TestCase):
    def testTemplateMethod(self):
        test = WasRun("testMethod")
        test.run()
        assert("setUp testMethod " == test.log)


TestCaseTest("testTemplateMethod").run()
```

**실행 흐름 상세**:

```
1. TestCaseTest("testTemplateMethod").run()
2. → TestCase.run() 실행
3.   → self.setUp() 호출 → TestCaseTest에 setUp이 없으므로 TestCase.setUp() → pass
4.   → getattr(self, "testTemplateMethod") → testTemplateMethod 메서드 획득
5.   → testTemplateMethod() 실행
6.     → test = WasRun("testMethod") 생성
7.     → test.run() 호출
8.       → WasRun.setUp() 실행 → self.log = "setUp "
9.       → getattr(self, "testMethod") → testMethod 메서드 획득
10.      → testMethod() 실행 → self.log = "setUp testMethod "
11.    → assert("setUp testMethod " == test.log) → 통과!
```

---

## 6. Template Method 패턴의 등장

이 챕터에서 `TestCase.run()`은 **Template Method 패턴**의 전형적인 예가 되었다:

```python
def run(self):
    self.setUp()        # 1단계: 준비 (하위 클래스에서 오버라이드)
    method = getattr(self, self.name)
    method()            # 2단계: 실행 (하위 클래스의 테스트 메서드)
```

Template Method 패턴은:
- **상위 클래스**가 알고리즘의 **뼈대(skeleton)** 를 정의한다
- **하위 클래스**가 특정 단계를 **오버라이드**하여 구체적인 동작을 제공한다

| 단계 | 상위 클래스(TestCase) | 하위 클래스(WasRun) |
|------|----------------------|-------------------|
| setUp() | `pass` (기본: 아무것도 안 함) | 로그 초기화, 객체 준비 |
| 테스트 메서드 | `getattr()`로 동적 호출 | `testMethod()` 구체 구현 |

나중에 `tearDown()`이 추가되면 이 뼈대가 더 완성된다:

```python
def run(self):        # 최종 형태 (미리보기)
    self.setUp()      # 준비
    method()          # 실행
    self.tearDown()   # 정리
```

---

## TODO 리스트 (챕터 종료 시점)

- [x] ~~테스트 메서드 호출하기~~
- [x] ~~setUp 먼저 호출하기~~
- [ ] tearDown 나중에 호출하기
- [ ] 테스트 메서드가 실패해도 tearDown 호출하기
- [ ] 여러 테스트 실행하기
- [ ] 수집된 결과를 출력하기
- [x] ~~WasRun에서 로그 문자열 사용하기~~
- [ ] 실패한 테스트 보고하기
- [ ] setUp 에러를 잡아서 보고하기
- [ ] TestSuite 만들기

`setUp 먼저 호출하기`와 `WasRun에서 로그 문자열 사용하기`가 완료되었다. 다음 챕터에서는 `tearDown()`을 구현한다.

---

## 요약

- **테스트 픽스처(Test Fixture)** 는 테스트에 필요한 공통 객체와 데이터다. 여러 테스트에서 반복되는 픽스처 코드를 `setUp()`으로 추출한다.
- `setUp()`은 **각 테스트 메서드 전에 자동으로 호출**되어 깨끗한 상태를 보장한다. 이것이 테스트 격리의 기반이다.
- `TestCase.run()`은 **Template Method 패턴**이다. `setUp()` → 테스트 메서드 → (나중에 `tearDown()`)의 뼈대를 정의하고, 하위 클래스가 각 단계를 구체화한다.
- **로그 문자열(Log String)** 기법: 각 메서드가 호출될 때 이름을 문자열에 추가하여, 호출 순서를 검증한다. 단순하지만 강력한 테스트 기법이다.
- `wasRun`, `wasSetUp` 같은 개별 플래그들이 하나의 로그 문자열로 통합되면서 테스트가 더 간결하고 표현력 있어졌다.

---

## 다른 챕터와의 관계

- **Chapter 18 (First Steps to xUnit)**: 이 챕터에서 만든 `TestCase`와 `WasRun`에 `setUp()` 기능을 추가했다. `WasRun`의 플래그 기반 추적이 로그 문자열로 진화했다.
- **Chapter 20 (Cleaning Up After)**: `tearDown()` 메서드를 추가하여 테스트 생명주기를 완성한다. 로그 문자열이 `"setUp testMethod tearDown "`으로 확장된다.
- **Chapter 27 (Testing Patterns)**: Part III에서 Test Fixture 패턴과 setUp의 올바른 사용법이 체계적으로 정리된다.
- **Chapter 29 (xUnit Patterns)**: Template Method 패턴이 xUnit의 핵심 설계 결정으로 분석된다.
- **Chapter 30 (Design Patterns)**: Template Method와 같은 설계 패턴이 TDD 맥락에서 어떻게 활용되는지 정리된다.
