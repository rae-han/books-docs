# Chapter 18: First Steps to xUnit (xUnit의 첫 걸음)

## 핵심 질문

테스트 프레임워크를 테스트 프레임워크 자체로 테스트하면서 만들 수 있는가? 아직 존재하지 않는 도구를 사용하여 그 도구를 만드는 "부트스트래핑(bootstrapping)" 문제를 어떻게 해결하는가?

---

## 1. Part II의 시작: 왜 xUnit을 만드는가?

### 1.1 Part I에서 Part II로

Part I에서는 다중 통화 Money 객체를 Java로 구현하면서 TDD의 기본 리듬을 경험했다. Part II에서는 **완전히 다른 종류의 문제**에 TDD를 적용한다 — 바로 **테스트 프레임워크 자체**를 만드는 것이다.

Part II의 언어는 **Python**이다. Kent Beck은 의도적으로 다른 언어를 선택했다. TDD는 특정 언어나 도구에 종속되지 않는 **보편적인 개발 방법론**임을 보여주기 위해서다.

### 1.2 부트스트래핑 문제

xUnit 프레임워크를 만들 때 독특한 문제가 있다:

> **"테스트를 실행하려면 테스트 프레임워크가 필요한데, 그 테스트 프레임워크가 아직 존재하지 않는다."**

이것이 **부트스트래핑 문제(Bootstrap Problem)** 다. 닭이 먼저인가, 달걀이 먼저인가와 같은 상황이다.

Kent Beck의 해결책은 우아하다:

1. 처음에는 아주 원시적인 방법(print 문)으로 테스트 결과를 확인한다
2. 프레임워크가 조금씩 만들어지면, **만들어진 부분을 사용하여 나머지를 테스트**한다
3. 결국 프레임워크가 **자기 자신을 테스트**하게 된다

> **핵심 통찰**: 부트스트래핑은 TDD에만 있는 문제가 아니다. 컴파일러를 컴파일러로 컴파일하는 "셀프 호스팅(self-hosting)"과 같은 개념이다. 작은 씨앗에서 시작하여 점점 더 강력한 도구를 만들어가는 과정이다.

### 1.3 xUnit이란?

xUnit은 **단위 테스트 프레임워크의 아키텍처**를 의미한다. Kent Beck과 Erich Gamma가 1997년에 SUnit(Smalltalk)에서 시작한 패턴으로, 이후 JUnit(Java), pytest(Python), NUnit(C#) 등 거의 모든 언어에 xUnit 스타일의 프레임워크가 존재한다.

xUnit의 핵심 구조:

| 요소 | 역할 |
|------|------|
| **TestCase** | 개별 테스트를 표현하는 기본 단위 |
| **setUp()** | 각 테스트 전에 실행되는 준비 코드 |
| **tearDown()** | 각 테스트 후에 실행되는 정리 코드 |
| **TestSuite** | 여러 테스트를 모아서 실행하는 컬렉션 |
| **TestResult** | 테스트 실행 결과를 수집하는 객체 |

이 챕터에서는 이 중 **TestCase**와 **테스트 메서드 호출**부터 시작한다.

---

## 2. TODO 리스트: xUnit 프로젝트의 시작

Part I의 Money 예제와 마찬가지로, 해야 할 일의 목록을 먼저 작성한다:

- [ ] **테스트 메서드 호출하기**
- [ ] setUp 먼저 호출하기
- [ ] tearDown 나중에 호출하기
- [ ] 테스트 메서드가 실패해도 tearDown 호출하기
- [ ] 여러 테스트 실행하기
- [ ] 수집된 결과를 출력하기
- [ ] **WasRun에서 로그 문자열 사용하기**
- [ ] 실패한 테스트 보고하기
- [ ] setUp 에러를 잡아서 보고하기
- [ ] TestSuite 만들기

> **핵심 통찰**: TODO 리스트의 첫 번째 항목이 "테스트 메서드 호출하기"인 것에 주목하라. Kent Beck은 가장 기본적이고 작은 기능에서 시작한다. "테스트 프레임워크를 만든다"는 큰 목표를 작은 단계로 분해하는 것이 TDD의 핵심이다.

---

## 3. TDD 사이클

### 3.1 Red — 첫 번째 테스트: 테스트 메서드를 호출할 수 있는가?

가장 기본적인 질문에서 시작한다: **테스트 메서드를 이름으로 호출할 수 있는가?**

아직 테스트 프레임워크가 없으므로, 수동으로 확인해야 한다. Kent Beck은 `WasRun`이라는 작은 클래스를 만드는 것에서 시작한다. 이 클래스의 역할은 단순하다 — **테스트 메서드가 실제로 호출되었는지를 기록**하는 것이다.

먼저 우리가 원하는 동작을 코드로 표현해 보자:

```python
test = WasRun("testMethod")
print(test.wasRun)    # None — 아직 실행되지 않았다
test.testMethod()
print(test.wasRun)    # 1 — 실행되었다
```

이것이 우리의 첫 번째 "테스트"다. 아직 프레임워크가 없으므로 `print`문으로 결과를 확인한다. 이것은 다소 원시적이지만, 부트스트래핑의 첫 발걸음으로는 충분하다.

`WasRun` 클래스를 구현한다:

```python
class WasRun:
    def __init__(self, name):
        self.wasRun = None
        self.name = name

    def testMethod(self):
        self.wasRun = 1
```

실행하면:

```
None
1
```

좋다! 테스트 메서드를 직접 호출하면 `wasRun`이 `1`로 변한다. 하지만 이것은 우리가 원하는 것이 아니다. **메서드 이름을 문자열로 받아서 동적으로 호출**하고 싶다. 즉, `test.testMethod()`가 아니라 `test.run()`을 호출하면 생성자에서 받은 이름(`"testMethod"`)에 해당하는 메서드가 실행되어야 한다.

### 3.2 Green — Python의 리플렉션으로 동적 호출

Python에는 `getattr()`이라는 강력한 내장 함수가 있다. 이 함수는 **객체에서 이름(문자열)으로 속성이나 메서드를 찾아 반환**한다.

```python
# getattr() 예시
class Foo:
    def bar(self):
        return "hello"

foo = Foo()
method = getattr(foo, "bar")  # foo 객체에서 "bar"라는 이름의 메서드를 가져온다
result = method()              # 가져온 메서드를 호출한다
print(result)                  # "hello"
```

이것을 활용하여 `WasRun`에 `run()` 메서드를 추가한다:

```python
class WasRun:
    def __init__(self, name):
        self.wasRun = None
        self.name = name

    def testMethod(self):
        self.wasRun = 1

    def run(self):
        method = getattr(self, self.name)
        method()
```

이제 테스트를 수정한다:

```python
test = WasRun("testMethod")
print(test.wasRun)    # None
test.run()            # testMethod() 대신 run() 호출!
print(test.wasRun)    # 1
```

실행 결과:

```
None
1
```

**동작한다!** `run()` 메서드가 `self.name`에 저장된 문자열(`"testMethod"`)을 사용하여 `getattr()`으로 해당 메서드를 찾아 호출한다.

> **핵심 통찰**: `getattr()`은 Python의 리플렉션(reflection) 기능이다. 이것은 xUnit 프레임워크의 핵심 메커니즘이다. Java의 JUnit도 내부적으로 `Method.invoke()`라는 리플렉션을 사용하여 같은 일을 한다. 리플렉션이 없었다면 각 테스트를 호출하기 위해 거대한 if-else 체인이 필요했을 것이다.

### 3.3 Refactor — TestCase 추출

지금 `WasRun`의 `run()` 메서드를 보면, 이 메서드는 `WasRun` 고유의 로직이 아니다. **어떤 테스트든 이름으로 메서드를 호출하는 것**은 보편적인 기능이다. 따라서 이것을 상위 클래스 `TestCase`로 추출한다.

```python
class TestCase:
    def __init__(self, name):
        self.name = name

    def run(self):
        method = getattr(self, self.name)
        method()
```

`WasRun`은 이제 `TestCase`를 상속받는다:

```python
class WasRun(TestCase):
    def __init__(self, name):
        self.wasRun = None
        TestCase.__init__(self, name)

    def testMethod(self):
        self.wasRun = 1
```

테스트를 다시 실행한다:

```python
test = WasRun("testMethod")
print(test.wasRun)    # None
test.run()
print(test.wasRun)    # 1
```

여전히 동작한다. `run()`은 이제 `TestCase`에 있고, `WasRun`은 `TestCase`를 상속받아 자동으로 `run()`을 사용한다. `TestCase`를 상속받는 **어떤 클래스든** `run()`을 호출하면 생성자에서 지정한 이름의 메서드가 실행된다.

---

## 4. TestCaseTest: 테스트를 테스트하기

### 4.1 프레임워크로 프레임워크를 테스트하기

이제 `TestCase`가 기본적으로 동작하므로, **`print`문 대신 `TestCase`를 사용하여 테스트를 작성**할 수 있다. 부트스트래핑의 핵심 전환점이다.

```python
class TestCaseTest(TestCase):
    def testRunning(self):
        test = WasRun("testMethod")
        assert(not test.wasRun)
        test.run()
        assert(test.wasRun)

TestCaseTest("testRunning").run()
```

`TestCaseTest`는 `TestCase`를 상속받는다. 즉, **우리가 방금 만든 프레임워크를 사용하여 프레임워크 자체를 테스트**하고 있다!

실행하면 아무 에러 없이 조용히 종료된다. `assert`가 실패하면 `AssertionError`가 발생할 것이다. 에러가 없으므로 테스트가 통과한 것이다.

### 4.2 부트스트래핑의 구조

이 시점에서의 클래스 관계를 정리하면:

```
TestCase (상위 클래스)
├── WasRun (테스트 대상이자 헬퍼 — "테스트 메서드가 호출되었나?"를 추적)
│   └── testMethod() — 실행되면 wasRun = 1로 설정
└── TestCaseTest (테스트 코드 — WasRun을 사용하여 TestCase의 동작을 검증)
    └── testRunning() — WasRun.run()이 testMethod를 호출하는지 확인
```

| 클래스 | 역할 |
|--------|------|
| `TestCase` | 프레임워크의 핵심 — 메서드 이름으로 테스트를 실행 |
| `WasRun` | 테스트 더블(test double) — 메서드 호출 여부를 기록 |
| `TestCaseTest` | 프레임워크의 테스트 — TestCase의 동작이 올바른지 검증 |

> **핵심 통찰**: `WasRun`은 일종의 **Self-Shunt** 패턴이다. 테스트 대상(`TestCase`)의 하위 클래스로서, 특정 메서드가 호출되었는지 스스로 기록한다. 별도의 mock 라이브러리가 필요 없다 — 프레임워크가 아직 없으니 당연하다.

---

## 5. 이 챕터에서 완성된 코드

```python
class TestCase:
    def __init__(self, name):
        self.name = name

    def run(self):
        method = getattr(self, self.name)
        method()


class WasRun(TestCase):
    def __init__(self, name):
        self.wasRun = None
        TestCase.__init__(self, name)

    def testMethod(self):
        self.wasRun = 1


class TestCaseTest(TestCase):
    def testRunning(self):
        test = WasRun("testMethod")
        assert(not test.wasRun)
        test.run()
        assert(test.wasRun)


TestCaseTest("testRunning").run()
```

이 코드의 실행 흐름:

1. `TestCaseTest("testRunning")` — `TestCaseTest` 객체 생성, `name = "testRunning"`
2. `.run()` — `TestCase.run()` 호출
3. `getattr(self, "testRunning")` — `testRunning` 메서드를 동적으로 찾음
4. `method()` — `testRunning()` 실행
5. `testRunning()` 내부에서 `WasRun("testMethod")` 생성 및 `run()` 호출
6. `WasRun.run()`이 `getattr(self, "testMethod")`로 `testMethod()` 호출
7. `testMethod()`가 `self.wasRun = 1` 설정
8. `assert(test.wasRun)` 통과 — 테스트 성공!

---

## 6. 핵심 설계 결정 분석

### 6.1 왜 메서드 이름을 문자열로 전달하는가?

```python
# 왜 이렇게 하는가?
TestCaseTest("testRunning")

# 왜 이렇게 하지 않는가?
TestCaseTest(TestCaseTest.testRunning)
```

메서드 이름을 문자열로 전달하는 이유:

1. **유연성**: 나중에 테스트 검색(test discovery)을 구현할 때, 클래스의 메서드 이름을 문자열로 탐색할 수 있다
2. **직렬화**: 문자열은 저장하거나 전달하기 쉽다
3. **전통**: Smalltalk의 SUnit이 이 방식을 사용했고, Kent Beck은 그 전통을 따른다

### 6.2 왜 상속을 사용하는가?

`WasRun`이 `TestCase`를 상속받는 구조는 **Template Method 패턴**이다:

- `TestCase.run()`이 **알고리즘의 뼈대**를 정의한다 (메서드 이름으로 찾아서 호출)
- 하위 클래스(`WasRun`, `TestCaseTest`)가 **구체적인 테스트 메서드**를 정의한다

이 패턴 덕분에 새 테스트를 추가할 때마다 `TestCase`를 수정할 필요가 없다. 하위 클래스를 만들고 테스트 메서드를 정의하면 된다.

---

## TODO 리스트 (챕터 종료 시점)

- [x] ~~테스트 메서드 호출하기~~
- [ ] setUp 먼저 호출하기
- [ ] tearDown 나중에 호출하기
- [ ] 테스트 메서드가 실패해도 tearDown 호출하기
- [ ] 여러 테스트 실행하기
- [ ] 수집된 결과를 출력하기
- [ ] WasRun에서 로그 문자열 사용하기
- [ ] 실패한 테스트 보고하기
- [ ] setUp 에러를 잡아서 보고하기
- [ ] TestSuite 만들기

첫 번째 항목 "테스트 메서드 호출하기"가 완료되었다. 다음 챕터에서는 `setUp()`을 구현한다.

---

## 요약

- **Part II**는 Python으로 xUnit 테스트 프레임워크를 TDD로 구현하는 과정이다.
- **부트스트래핑 문제**: 테스트 프레임워크를 만들려면 테스트가 필요한데, 프레임워크가 아직 없다. 처음에는 `print`문으로 시작하여, 프레임워크가 만들어지면 자기 자신을 테스트하도록 전환한다.
- **TestCase 클래스**: 메서드 이름을 문자열로 받아 `getattr()`(리플렉션)으로 동적 호출한다. 이것이 xUnit의 핵심 메커니즘이다.
- **WasRun**: `TestCase`를 상속받아 테스트 메서드 호출 여부를 기록하는 헬퍼 클래스다.
- **TestCaseTest**: `TestCase`를 상속받아 프레임워크 자체를 테스트하는 클래스다. 프레임워크가 자기 자신을 테스트하는 부트스트래핑이 시작된다.
- Python의 `getattr()`은 Java의 리플렉션(`Method.invoke()`)과 같은 역할을 하며, xUnit 구현의 핵심이다.

---

## 다른 챕터와의 관계

- **Chapter 19 (Set the Table)**: `setUp()` 메서드를 추가하여 각 테스트 전에 공통 준비 코드를 실행할 수 있게 만든다. `WasRun`의 초기화 코드가 `setUp()`으로 이동한다.
- **Chapter 20 (Cleaning Up After)**: `tearDown()` 메서드로 테스트 후 정리를 구현한다. `setUp() → testMethod() → tearDown()`이라는 테스트 생명주기가 완성된다.
- **Chapter 23 (How Suite It Is)**: `TestSuite`로 여러 테스트를 묶어 실행하는 기능을 추가한다. Composite 패턴이 적용된다.
- **Chapter 24 (xUnit Retrospective)**: Part II 전체를 돌아보며, 여기서 만든 프레임워크와 실제 xUnit 프레임워크를 비교한다.
- **Chapter 29 (xUnit Patterns)**: Part III에서 이 챕터에서 사용한 패턴(TestCase, TestSuite 등)이 체계적으로 정리된다.
- **Chapter 1 (Multi-Currency Money)**: Part I과 Part II는 같은 TDD 리듬(Red → Green → Refactor)을 따르지만, 언어와 문제 영역이 다르다. 비교하면서 읽으면 TDD의 보편성을 느낄 수 있다.
