# Chapter 20: Cleaning Up After (뒷정리)

## 핵심 질문

테스트가 사용한 리소스를 어떻게 안전하게 정리하는가? 테스트가 실패하더라도 정리 코드가 반드시 실행되도록 보장할 수 있는가?

---

## 1. 문제 인식: 테스트 후 정리의 필요성

### 1.1 왜 뒷정리가 필요한가?

테스트는 종종 외부 리소스를 사용한다:

| 리소스 | setUp()에서 | tearDown()에서 |
|--------|------------|---------------|
| 데이터베이스 연결 | 연결 열기 | 연결 닫기 |
| 임시 파일 | 파일 생성 | 파일 삭제 |
| 네트워크 소켓 | 소켓 열기 | 소켓 닫기 |
| 테스트 데이터 | 데이터 삽입 | 데이터 삭제 |
| 전역 상태 변경 | 상태 변경 | 상태 복원 |

`setUp()`에서 리소스를 열었다면, 테스트가 끝난 후 반드시 닫아야 한다. 그렇지 않으면:

- 리소스 누수(resource leak)가 발생한다
- 다음 테스트에 영향을 준다 (테스트 격리 위반)
- 테스트를 많이 실행하면 시스템이 불안정해진다

### 1.2 setUp()과의 대칭성

`setUp()`이 테스트 전의 준비라면, `tearDown()`은 테스트 후의 정리다. 이 둘은 **대칭적**이다:

```
setUp()    → 자원 할당 (acquire)
testMethod → 테스트 실행
tearDown() → 자원 해제 (release)
```

이것은 프로그래밍에서 흔히 보이는 **acquire/release** 패턴이다. Python의 `with` 문, Java의 `try-with-resources`, C++의 RAII와 같은 개념이다.

> **핵심 통찰**: `setUp()`과 `tearDown()`은 단독으로 의미 있는 것이 아니라 **쌍(pair)** 으로 의미가 있다. `setUp()`에서 열었으면 `tearDown()`에서 닫는다. 이 대칭 구조가 테스트 격리를 보장한다.

---

## 2. TDD 사이클

### 2.1 Red — tearDown()이 호출되는지 테스트

Chapter 19에서 도입한 로그 문자열 기법을 그대로 활용한다. `tearDown()`이 호출되면 로그에 `"tearDown "`이 추가되어야 한다:

```python
class TestCaseTest(TestCase):
    def testTemplateMethod(self):
        test = WasRun("testMethod")
        test.run()
        assert("setUp testMethod tearDown " == test.log)
```

기존 테스트에서 기대하는 로그 문자열을 `"setUp testMethod "`에서 `"setUp testMethod tearDown "`으로 변경했다.

이 테스트를 실행하면 실패한다:

```
AssertionError
# 실제 log: "setUp testMethod "
# 기대 log: "setUp testMethod tearDown "
```

`tearDown()`이 아직 구현되지 않았으므로 로그에 기록되지 않는다. Red Bar!

### 2.2 Green — tearDown() 구현

두 곳을 수정한다:

**Step 1**: `TestCase.run()`에서 테스트 메서드 후에 `tearDown()`을 호출

```python
class TestCase:
    def __init__(self, name):
        self.name = name

    def setUp(self):
        pass

    def tearDown(self):
        pass  # 기본 구현: 아무것도 하지 않는다

    def run(self):
        self.setUp()
        method = getattr(self, self.name)
        method()
        self.tearDown()  # 테스트 메서드 후에 tearDown 호출!
```

**Step 2**: `WasRun`에서 `tearDown()` 오버라이드하여 로그에 기록

```python
class WasRun(TestCase):
    def setUp(self):
        self.log = "setUp "

    def testMethod(self):
        self.log = self.log + "testMethod "

    def tearDown(self):
        self.log = self.log + "tearDown "
```

테스트 실행:

```python
TestCaseTest("testTemplateMethod").run()
```

통과! 로그 문자열이 `"setUp testMethod tearDown "`으로 정확히 일치한다. Green Bar!

### 2.3 Refactor — Template Method 완성

이 시점에서 `TestCase.run()`을 보면 Template Method 패턴이 완전한 형태를 갖추었다:

```python
def run(self):
    self.setUp()        # 1단계: 준비
    method = getattr(self, self.name)
    method()            # 2단계: 실행
    self.tearDown()     # 3단계: 정리
```

이것은 xUnit 프레임워크의 **테스트 생명주기(Test Lifecycle)** 다:

```
┌─────────────────────────────────────────┐
│            TestCase.run()               │
│                                         │
│  ┌───────────┐                          │
│  │ setUp()   │ ← 매 테스트 전에 실행     │
│  └─────┬─────┘                          │
│        ▼                                │
│  ┌───────────┐                          │
│  │ testXxx() │ ← 실제 테스트 메서드      │
│  └─────┬─────┘                          │
│        ▼                                │
│  ┌────────────┐                         │
│  │ tearDown() │ ← 매 테스트 후에 실행    │
│  └────────────┘                         │
└─────────────────────────────────────────┘
```

---

## 3. 남은 문제: 실패 시 tearDown()

### 3.1 현재 구현의 취약점

현재 `run()` 메서드를 다시 보자:

```python
def run(self):
    self.setUp()
    method = getattr(self, self.name)
    method()
    self.tearDown()
```

만약 `method()` — 즉, 테스트 메서드 — 에서 **예외가 발생**하면 어떻게 되는가?

```python
class BrokenTest(TestCase):
    def setUp(self):
        self.resource = open_database_connection()

    def testSomething(self):
        raise Exception("테스트 실패!")  # 여기서 예외 발생

    def tearDown(self):
        self.resource.close()  # 이 코드는 실행되지 않는다!
```

`method()` 호출에서 예외가 발생하면, `self.tearDown()` 줄에 도달하지 못한다. 데이터베이스 연결이 닫히지 않고 누수된다.

### 3.2 해결은 나중으로

Kent Beck은 이 문제를 인식하지만, **지금은 해결하지 않는다**. TODO 리스트에 이미 "테스트 메서드가 실패해도 tearDown 호출하기"가 있다. 지금은 기본적인 `tearDown()` 호출 메커니즘을 구현한 것에 만족한다.

이 접근법은 TDD의 핵심 원칙 중 하나다:

> **핵심 통찰**: 문제를 인식했다면 TODO 리스트에 기록하고, 현재 작업에 집중하라. 한 번에 모든 것을 해결하려 하면 아무것도 완성하지 못한다. 작동하는 간단한 버전을 먼저 만들고, 점진적으로 견고하게 만들어 간다.

실제로 이 문제는 Chapter 22에서 예외 처리를 다룰 때 함께 해결할 수 있다. Python의 `try/finally` 구문을 사용하면 된다:

```python
# 미리보기: 나중에 이렇게 바뀔 것이다
def run(self):
    self.setUp()
    try:
        method = getattr(self, self.name)
        method()
    finally:
        self.tearDown()  # 예외가 발생해도 반드시 실행
```

하지만 지금은 이 단계까지 가지 않는다.

---

## 4. 테스트 생명주기의 중요성

### 4.1 왜 매 테스트마다 setUp/tearDown인가?

테스트 격리를 위해 `setUp()`과 `tearDown()`은 **매 테스트 메서드마다** 실행된다. 5개의 테스트가 있다면:

```
setUp → test1 → tearDown
setUp → test2 → tearDown
setUp → test3 → tearDown
setUp → test4 → tearDown
setUp → test5 → tearDown
```

**한 번의 setUp으로 5개의 테스트를 모두 실행하는 것이 아니다.** 이렇게 하면:

- test1이 데이터를 변경하면 test2에 영향을 준다
- test3이 실패하면 test4, test5도 영향받을 수 있다
- 테스트 실행 순서에 따라 결과가 달라질 수 있다

매번 `setUp/tearDown`을 실행하면 성능은 조금 떨어지지만, **테스트가 서로 독립적**이라는 보장을 얻는다. 이것이 테스트의 신뢰성을 위해 지불할 만한 비용이다.

### 4.2 실제 xUnit 프레임워크와의 비교

| 프레임워크 | setUp (매 테스트) | tearDown (매 테스트) | 일회성 setUp |
|-----------|-------------------|---------------------|-------------|
| JUnit | `@Before` / `@BeforeEach` | `@After` / `@AfterEach` | `@BeforeClass` / `@BeforeAll` |
| pytest | `setup_method` | `teardown_method` | `setup_class` |
| NUnit | `[SetUp]` | `[TearDown]` | `[OneTimeSetUp]` |

대부분의 실제 프레임워크는 "매 테스트마다"와 "클래스 전체에서 한 번만"이라는 두 수준의 setUp/tearDown을 모두 제공한다. Kent Beck의 xUnit에서는 간단히 "매 테스트마다"만 구현한다.

---

## 5. 이 챕터에서 완성된 코드

```python
class TestCase:
    def __init__(self, name):
        self.name = name

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def run(self):
        self.setUp()
        method = getattr(self, self.name)
        method()
        self.tearDown()


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


TestCaseTest("testTemplateMethod").run()
```

코드 변경 요약:

| 변경 | 위치 | 내용 |
|------|------|------|
| `tearDown()` 기본 구현 추가 | `TestCase` | `pass` (빈 메서드) |
| `tearDown()` 호출 추가 | `TestCase.run()` | 테스트 메서드 뒤에 `self.tearDown()` |
| `tearDown()` 오버라이드 | `WasRun` | 로그에 `"tearDown "` 추가 |
| 기대 로그 수정 | `TestCaseTest` | `"setUp testMethod tearDown "` |

---

## TODO 리스트 (챕터 종료 시점)

- [x] ~~테스트 메서드 호출하기~~
- [x] ~~setUp 먼저 호출하기~~
- [x] ~~tearDown 나중에 호출하기~~
- [ ] 테스트 메서드가 실패해도 tearDown 호출하기
- [ ] 여러 테스트 실행하기
- [ ] 수집된 결과를 출력하기
- [ ] ~~WasRun에서 로그 문자열 사용하기~~
- [ ] 실패한 테스트 보고하기
- [ ] setUp 에러를 잡아서 보고하기
- [ ] TestSuite 만들기

`tearDown 나중에 호출하기`가 완료되었다. "테스트 메서드가 실패해도 tearDown 호출하기"는 아직 미완성 — Chapter 22에서 예외 처리와 함께 다룬다.

---

## 요약

- **tearDown()** 은 각 테스트 후에 자동으로 호출되어 리소스를 정리한다. `setUp()`과 대칭을 이룬다.
- `TestCase.run()`의 Template Method가 완성되었다: `setUp()` → `testMethod()` → `tearDown()`. 이것이 xUnit의 **테스트 생명주기**다.
- **로그 문자열**로 세 단계의 호출 순서를 `"setUp testMethod tearDown "`으로 검증할 수 있다.
- 현재 구현에는 **약점**이 있다: 테스트 메서드에서 예외가 발생하면 `tearDown()`이 호출되지 않는다. 이것은 TODO 리스트에 기록하고, 나중에 해결한다.
- **테스트 격리(Test Isolation)**: 매 테스트마다 `setUp/tearDown`을 실행하여 테스트 간 간섭을 방지한다. 성능보다 격리를 우선시한다.
- 이 챕터의 변경은 매우 작았다 — `tearDown()` 메서드 추가와 `run()`에서의 호출 한 줄. **작은 단계**로 진행하는 TDD의 리듬이 여전히 유지된다.

---

## 다른 챕터와의 관계

- **Chapter 19 (Set the Table)**: `setUp()`을 구현한 챕터. 이 챕터에서 대칭이 되는 `tearDown()`을 추가하여 테스트 생명주기를 완성했다.
- **Chapter 21 (Counting)**: 테스트 실행 결과를 수집하는 `TestResult` 클래스를 도입한다. `run()`이 결과를 반환하기 시작한다.
- **Chapter 22 (Dealing with Failure)**: 테스트 실패 시 예외 처리를 구현한다. `tearDown()`이 실패 시에도 호출되는 문제를 함께 다룰 수 있다.
- **Chapter 29 (xUnit Patterns)**: setUp/tearDown의 올바른 사용법과 anti-pattern이 정리된다. 특히 "setUp에서 너무 많은 것을 하지 말 것"이라는 가이드라인이 있다.
