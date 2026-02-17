# Chapter 24: xUnit Retrospective (xUnit 회고)

## 핵심 질문

Part II에서 우리는 무엇을 만들었고, 무엇을 배웠는가? 테스트 프레임워크를 TDD로 만드는 과정은 어떤 통찰을 주는가? 우리가 만든 것과 실제 xUnit 프레임워크 사이에는 어떤 차이가 있는가?

---

## 1. Part II 전체 회고

### 1.1 여정의 요약

Chapter 18부터 23까지, 6개의 챕터에 걸쳐 Python으로 xUnit 테스트 프레임워크를 TDD로 구현했다. 각 챕터에서 한 가지 기능을 추가하며, 아무것도 없는 상태에서 동작하는 프레임워크를 만들었다:

| 챕터 | 추가한 기능 | 핵심 개념 |
|------|-----------|----------|
| **Ch 18** | TestCase, 메서드 동적 호출 | 부트스트래핑, getattr() 리플렉션 |
| **Ch 19** | setUp() | Template Method 패턴, 로그 문자열 |
| **Ch 20** | tearDown() | 테스트 생명주기, 리소스 정리 |
| **Ch 21** | TestResult (실행 횟수) | Collecting Parameter 패턴 |
| **Ch 22** | 실패 보고 (failureCount) | 예외 처리, try/except |
| **Ch 23** | TestSuite | Composite 패턴, 매개변수 방식 전환 |

### 1.2 최종 아키텍처

```
┌─────────────────────────────────────────────────────┐
│                    TestSuite                         │
│  tests: [TestCase | TestSuite]                       │
│  run(result): 각 test에 대해 test.run(result) 호출   │
└─────────────────────┬───────────────────────────────┘
                      │ Composite 패턴
┌─────────────────────┴───────────────────────────────┐
│                    TestCase                           │
│  name: str (테스트 메서드 이름)                        │
│  run(result):                                        │
│    result.testStarted()                              │
│    self.setUp()                                      │
│    try: getattr(self, self.name)()                   │
│    except: result.testFailed()                       │
│    self.tearDown()                                   │
│  setUp(): pass (오버라이드 가능)                       │
│  tearDown(): pass (오버라이드 가능)                    │
└─────────────────────────────────────────────────────┘
                      │ 결과 수집
┌─────────────────────┴───────────────────────────────┐
│                   TestResult                         │
│  runCount: int                                       │
│  failureCount: int                                   │
│  testStarted(): runCount += 1                        │
│  testFailed(): failureCount += 1                     │
│  summary(): "N run, M failed"                        │
└─────────────────────────────────────────────────────┘
```

클래스 3개, 메서드 약 10개. 전체 코드가 50줄도 안 되는 작은 프레임워크지만, xUnit의 **핵심 구조를 모두 갖추고** 있다.

---

## 2. 부트스트래핑의 우아함

### 2.1 자기 참조의 아름다움

Part II의 가장 인상적인 측면은 **프레임워크가 자기 자신을 테스트한다**는 것이다:

```python
# 프레임워크 코드
class TestCase:
    def run(self, result): ...

class TestSuite:
    def run(self, result): ...

class TestResult:
    def summary(self): ...

# 프레임워크의 테스트 코드 — 프레임워크 자체를 사용!
class TestCaseTest(TestCase):  # ← TestCase를 상속
    def testSuite(self):
        suite = TestSuite()    # ← TestSuite를 사용
        suite.add(...)
        result = TestResult()  # ← TestResult를 사용
        suite.run(result)
        assert("2 run, 1 failed" == result.summary())

# 실행 — TestSuite로 실행!
suite = TestSuite()
suite.add(TestCaseTest("testTemplateMethod"))
suite.add(TestCaseTest("testResult"))
suite.add(TestCaseTest("testFailedResult"))
suite.add(TestCaseTest("testSuite"))
result = TestResult()
suite.run(result)
print(result.summary())
```

`TestSuite`가 `TestCaseTest`의 `testSuite` 테스트를 실행하고, 그 테스트 안에서 또 `TestSuite`를 만들어 테스트한다. 이 자기 참조적 구조는 **프레임워크가 올바르게 동작한다는 강력한 증거**다.

### 2.2 부트스트래핑의 단계

| 단계 | 검증 방법 | 챕터 |
|------|----------|------|
| 1단계 | `print` 문으로 직접 확인 | Ch 18 초반 |
| 2단계 | `assert`로 자동 확인, 하지만 수동 실행 | Ch 18 중반 |
| 3단계 | `TestCase`를 사용하여 `TestCase`를 테스트 | Ch 18 후반 |
| 4단계 | `TestSuite`로 모든 테스트를 묶어 실행 | Ch 23 |

각 단계에서 **이전 단계에서 만든 도구로 다음 단계를 만들었다**. 이것은 컴파일러의 셀프 호스팅과 같은 원리다.

> **핵심 통찰**: 부트스트래핑은 "닭이 먼저냐 달걀이 먼저냐"의 문제가 아니다. **아주 작은 시작점**(print 문)에서 출발하여, 만들어진 것을 사용하여 더 많은 것을 만드는 **점진적 성장**의 과정이다. TDD 자체가 이런 점진적 성장의 방법론이다.

---

## 3. 우리가 만든 것 vs 실제 xUnit 프레임워크

### 3.1 구현한 것

| 기능 | 상태 | 설명 |
|------|------|------|
| TestCase | 완료 | 메서드 이름으로 테스트 실행 |
| setUp / tearDown | 완료 | 테스트 생명주기 |
| TestResult | 완료 | 실행/실패 카운트, summary() |
| TestSuite | 완료 | 여러 테스트 묶어 실행 |
| 실패 보고 | 완료 | 예외를 잡아 카운트 |

### 3.2 구현하지 않은 것

실제 xUnit 프레임워크에는 있지만 우리 프레임워크에는 없는 것들:

#### (1) Assertion 메서드

우리 프레임워크에서는 Python의 기본 `assert`를 사용했다:

```python
assert("1 run, 0 failed" == result.summary())
```

실제 프레임워크는 더 풍부한 assertion을 제공한다:

```python
# JUnit
assertEquals(expected, actual)
assertTrue(condition)
assertNotNull(obj)
assertThrows(ExceptionType.class, () -> ...)

# pytest
assert result == expected  # 실패 시 상세한 diff 출력
pytest.raises(ValueError)
```

우리의 `assert`는 실패 시 `AssertionError`만 던지고 **무엇이 잘못되었는지 알려주지 않는다**. 실제 프레임워크는 기대값과 실제값을 비교하여 차이를 보여준다.

#### (2) 테스트 검색(Test Discovery)

우리 프레임워크에서는 각 테스트를 수동으로 등록해야 한다:

```python
suite = TestSuite()
suite.add(TestCaseTest("testTemplateMethod"))
suite.add(TestCaseTest("testResult"))
# ... 일일이 추가
```

실제 프레임워크는 **자동으로 테스트를 찾는다**:

```python
# pytest — 파일 이름이 test_로 시작하고, 함수 이름이 test_로 시작하면 자동 실행
def test_multiplication():
    assert Dollar(5).times(2).amount == 10

# JUnit — @Test 어노테이션이 붙은 메서드를 자동 발견
@Test
public void testMultiplication() { ... }
```

#### (3) 상세한 실패 보고

우리 프레임워크의 결과:

```
4 run, 1 failed
```

실제 프레임워크의 결과:

```
======================== FAILURES ========================
______________ TestMoney.test_multiplication ______________

    def test_multiplication(self):
        five = Dollar(5)
>       assert five.times(2).amount == 11
E       assert 10 == 11
E        +  where 10 = Dollar(10).amount

test_money.py:15: AssertionError
================ 1 failed, 3 passed in 0.02s ================
```

어떤 테스트가 실패했는지, **어떤 줄에서, 어떤 값이 달랐는지**까지 보여준다.

#### (4) 기타 기능

| 기능 | 설명 |
|------|------|
| 테스트 필터링 | 특정 이름 패턴의 테스트만 실행 |
| 픽스처 스코프 | 클래스 수준, 모듈 수준, 세션 수준의 setUp/tearDown |
| 파라미터화 테스트 | 같은 테스트를 다른 입력값으로 반복 실행 |
| 플러그인 시스템 | 코드 커버리지, 성능 프로파일링 등 확장 |
| 병렬 실행 | 여러 테스트를 동시에 실행 |
| Mock/Stub 통합 | 의존성 대체를 위한 도구 통합 |

### 3.3 우리 프레임워크와 실제 프레임워크의 대비

| 측면 | 우리 xUnit | 실제 xUnit (JUnit/pytest) |
|------|-----------|--------------------------|
| 코드 크기 | ~50줄 | 수만 줄 |
| 핵심 구조 | 동일 | 동일 |
| 테스트 실행 | 동일 (getattr/리플렉션) | 동일 + 어노테이션/데코레이터 |
| setUp/tearDown | 동일 | 동일 + 스코프 확장 |
| 결과 보고 | 카운트만 | 카운트 + 상세 diff + 스택 트레이스 |
| 테스트 검색 | 수동 등록 | 자동 검색 |
| 스위트 | 수동 구성 | 자동 구성 |

> **핵심 통찰**: 핵심 구조는 **놀라울 정도로 동일**하다. TestCase, TestSuite, TestResult, setUp/tearDown — 이것들이 모든 xUnit 프레임워크의 뼈대다. 실제 프레임워크는 이 뼈대 위에 편의 기능과 보고 기능을 쌓은 것이다. 50줄의 프레임워크에서 핵심을 이해했다면, JUnit이나 pytest의 내부 구조도 이해할 수 있다.

---

## 4. Part II에서 배운 TDD 교훈

### 4.1 인프라 코드에도 TDD를 적용할 수 있다

많은 개발자가 "비즈니스 로직에는 TDD가 좋지만, 프레임워크나 인프라 코드에는 적용하기 어렵다"고 생각한다. Part II는 이 가정을 반박한다.

**테스트 프레임워크라는 가장 "메타"한 인프라 코드**에도 TDD를 성공적으로 적용했다. 핵심은 동일하다:

1. 원하는 동작을 테스트로 표현한다
2. 최소한의 코드로 테스트를 통과시킨다
3. 중복을 제거한다

### 4.2 작은 단계의 힘

Part II에서의 단계 크기를 보면:

- Ch 18: 메서드 하나를 동적으로 호출 (한 가지 기능)
- Ch 19: setUp() 추가 (한 가지 기능)
- Ch 20: tearDown() 추가 (한 가지 기능)
- Ch 21: 실행 횟수 세기 (한 가지 기능)
- Ch 22: 실패 횟수 세기 (한 가지 기능)
- Ch 23: 여러 테스트 묶기 (한 가지 기능)

**각 챕터에서 정확히 한 가지 기능만 추가했다.** 이 작은 단계 덕분에:

- 각 단계에서 무엇이 변했는지 명확하다
- 문제가 생기면 직전 단계로 돌아가기 쉽다
- 전체 설계가 자연스럽게 진화했다

### 4.3 설계의 점진적 진화

Part II에서 설계가 어떻게 진화했는지 추적해 보면:

**`run()` 메서드의 진화**:

```python
# Ch 18: 가장 단순한 형태
def run(self):
    method = getattr(self, self.name)
    method()

# Ch 19: setUp 추가
def run(self):
    self.setUp()
    method = getattr(self, self.name)
    method()

# Ch 20: tearDown 추가
def run(self):
    self.setUp()
    method = getattr(self, self.name)
    method()
    self.tearDown()

# Ch 21: TestResult 반환
def run(self):
    result = TestResult()
    result.testStarted()
    self.setUp()
    method = getattr(self, self.name)
    method()
    self.tearDown()
    return result

# Ch 22: 예외 처리 추가
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

# Ch 23: 매개변수 방식으로 전환
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

6단계에 걸친 점진적 진화. 처음부터 최종 버전을 설계하지 않았다. **필요에 의해** 한 줄씩 추가되었다. 그리고 최종 결과는 깔끔하다.

> **핵심 통찰**: Kent Beck은 이 과정을 통해 TDD의 핵심 메시지를 전달한다 — **좋은 설계는 한 번에 만들어지는 것이 아니라, 작은 단계를 통해 점진적으로 출현(emerge)하는 것이다.** 테스트가 설계를 이끌어낸다(drive).

---

## 5. Part I과 Part II의 비교

### 5.1 공통점

| 측면 | Part I (Money) | Part II (xUnit) |
|------|---------------|-----------------|
| TDD 리듬 | Red → Green → Refactor | Red → Green → Refactor |
| TODO 리스트 | 사용 | 사용 |
| 단계 크기 | 작은 단계 | 작은 단계 |
| Fake It | 사용 (Ch 1의 `amount = 10`) | 사용 (Ch 21의 `0 failed`) |
| Obvious Implementation | 사용 | 사용 |
| 설계 패턴 | Value Object, Factory Method | Template Method, Composite |

### 5.2 차이점

| 측면 | Part I (Money) | Part II (xUnit) |
|------|---------------|-----------------|
| 언어 | Java | Python |
| 문제 영역 | 비즈니스 로직 (다중 통화) | 인프라 (테스트 프레임워크) |
| 부트스트래핑 | JUnit 사용 (이미 존재) | 자기 자신으로 테스트 (부트스트래핑) |
| 챕터 수 | 17개 | 7개 |
| 초점 | 설계의 진화 | 부트스트래핑과 핵심 구조 |

### 5.3 두 파트를 관통하는 원칙

1. **한 번에 한 가지**: 두 파트 모두 한 번에 하나의 테스트, 하나의 기능에 집중한다.
2. **먼저 동작하게, 그 다음 올바르게, 그 다음 빠르게**: Make it work, make it right, make it fast — Kent Beck이 자주 인용하는 격언이다.
3. **테스트가 설계를 이끈다**: 테스트를 먼저 작성하면, 자연스럽게 테스트하기 쉬운 (즉, 잘 설계된) 코드가 만들어진다.
4. **자신감에 따른 단계 크기 조절**: 확실하면 큰 단계, 불확실하면 작은 단계. 이 원칙이 두 파트 모두에서 일관되게 적용되었다.

---

## 6. Part III로의 다리

Part III는 Part I과 Part II에서 **암묵적으로 사용한 기법들을 명시적인 패턴으로 정리**한다:

| Part I/II에서의 경험 | Part III의 패턴 |
|---------------------|---------------|
| `amount = 10`으로 시작하여 일반화 | **Fake It** (Chapter 28) |
| `return new Dollar(amount * multiplier)` 바로 작성 | **Obvious Implementation** (Chapter 28) |
| Dollar와 Franc의 두 테스트로 일반화 | **Triangulation** (Chapter 28) |
| TestCase.run()의 setUp → test → tearDown 구조 | **Template Method** (Chapter 30) |
| TestSuite와 TestCase의 동일 인터페이스 | **Composite** (Chapter 30) |
| TestResult를 매개변수로 전달 | **Collecting Parameter** (Chapter 30) |
| WasRun의 self-shunt 역할 | **Self-Shunt** (Chapter 27) |
| 로그 문자열로 호출 순서 검증 | **Log String** (Chapter 27) |

> **핵심 통찰**: Part I과 Part II를 읽은 후에 Part III를 읽으면, 패턴이 **추상적인 지식이 아니라 경험에 기반한 실천법**으로 느껴진다. 이것이 Kent Beck이 이 책을 "By Example"로 구성한 이유다. 먼저 경험하고, 그 다음에 체계화한다.

---

## 7. 남은 TODO 항목의 의미

### 7.1 최종 TODO 리스트

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

### 7.2 완료하지 않은 항목

두 가지 항목이 남아 있다:

1. **테스트 메서드가 실패해도 tearDown 호출하기**: Chapter 22에서 `try/except` 도입으로 사실상 해결되었지만, `setUp()` 실패 시의 `tearDown()` 호출은 미해결이다.

2. **setUp 에러를 잡아서 보고하기**: `setUp()`에서 예외가 발생하면 현재 코드에서는 처리되지 않고 전파된다.

Kent Beck은 이 항목들을 **의도적으로 남겨둔다**. 이것은 실무에서의 현실을 반영한다:

- 모든 TODO를 완료하는 것이 항상 필요한 것은 아니다
- 가장 중요한 기능부터 구현하고, 덜 중요한 것은 나중에 (또는 필요할 때) 처리한다
- "충분히 좋은" 시점을 판단하는 것도 중요한 엔지니어링 결정이다

### 7.3 독자를 위한 연습 문제

Kent Beck은 남은 항목들을 **독자의 연습 문제**로 남긴다. 이 책을 읽는 독자가 직접 TDD로 구현해 볼 수 있다:

**연습 1**: `setUp()` 에러 잡기

```python
def run(self, result):
    result.testStarted()
    try:
        self.setUp()
    except:
        result.testFailed()
        return  # setUp이 실패하면 테스트와 tearDown도 건너뛸 것인가?
    try:
        method = getattr(self, self.name)
        method()
    except:
        result.testFailed()
    self.tearDown()
```

**연습 2**: tearDown의 예외 안전성을 `try/finally`로 보장

```python
def run(self, result):
    result.testStarted()
    self.setUp()
    try:
        method = getattr(self, self.name)
        method()
    except:
        result.testFailed()
    finally:
        self.tearDown()  # 무슨 일이 있어도 실행
```

---

## 요약

- **Part II 전체 회고**: 6개 챕터에 걸쳐 TestCase, TestSuite, TestResult, setUp/tearDown을 구현했다. 약 50줄의 코드로 xUnit의 핵심 구조를 완성했다.
- **부트스트래핑의 우아함**: print 문에서 시작하여, 만들어진 프레임워크가 자기 자신을 테스트하는 단계까지 도달했다. 이것은 TDD의 점진적 성장을 극적으로 보여준다.
- **실제 xUnit과의 비교**: 핵심 구조(TestCase, TestSuite, TestResult, setUp/tearDown)는 동일하다. 실제 프레임워크는 assertion 메서드, 테스트 검색, 상세 보고 등의 편의 기능을 추가한 것이다.
- **인프라 코드에도 TDD가 작동한다**: 비즈니스 로직뿐만 아니라 프레임워크, 라이브러리 등 인프라 코드에도 TDD를 적용할 수 있다.
- **설계의 점진적 출현**: `run()` 메서드가 6단계에 걸쳐 진화한 것처럼, 좋은 설계는 한 번에 만들어지는 것이 아니라 작은 단계를 통해 출현한다.
- **Part III로의 다리**: Part I과 Part II에서 경험한 기법들(Fake It, Template Method, Composite 등)이 Part III에서 명시적인 패턴으로 정리된다.

---

## 다른 챕터와의 관계

- **Chapter 17 (Money Retrospective)**: Part I의 회고 챕터. Part I은 설계의 점진적 진화에 초점을 맞추고, Part II는 부트스트래핑과 인프라 TDD에 초점을 맞춘다. 두 회고를 비교하면 TDD의 보편성을 느낄 수 있다.
- **Chapter 18~23**: 이 챕터가 회고하는 내용의 실제 구현 과정이다.
- **Chapter 25 (TDD Patterns)**: Part III의 시작. Part I과 Part II의 경험을 바탕으로 TDD의 패턴을 체계적으로 정리한다.
- **Chapter 27 (Testing Patterns)**: Self-Shunt, Log String 등 Part II에서 사용한 테스트 기법이 패턴으로 정리된다.
- **Chapter 28 (Green Bar Patterns)**: Fake It, Obvious Implementation, Triangulation — Part I과 Part II 모두에서 사용한 전략이 정리된다.
- **Chapter 29 (xUnit Patterns)**: TestCase, TestSuite, TestResult 등 Part II에서 만든 구조가 패턴으로 분석된다.
- **Chapter 32 (Mastering TDD)**: 책의 최종 챕터에서 TDD의 철학과 실천에 대한 Kent Beck의 결론이 제시된다. Part I과 Part II의 경험이 이 결론의 근거가 된다.
