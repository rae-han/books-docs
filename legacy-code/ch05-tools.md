# Chapter 5: 도구 (Tools)

## 핵심 질문

레거시 코드를 안전하게 변경하고 테스트하기 위해 어떤 도구들을 활용할 수 있는가?

---

## 1. 자동화된 리팩토링 도구 (Automated Refactoring Tools)

### 1.1 리팩토링 도구란

자동화된 리팩토링 도구는 IDE나 별도 도구를 통해 **코드의 구조적 변환을 자동으로 수행**하는 도구다. 예를 들어:

- **Rename(이름 변경)**: 변수, 메서드, 클래스의 이름을 모든 참조 지점에서 일괄 변경
- **Extract Method(메서드 추출)**: 코드 블록을 선택하면 별도의 메서드로 추출
- **Extract Interface(인터페이스 추출)**: 클래스에서 인터페이스를 자동 생성
- **Push Up / Pull Down**: 상속 계층에서 메서드를 위아래로 이동
- **Inline Method / Variable**: 메서드나 변수를 인라인화

대표적인 도구로는 IntelliJ IDEA, Eclipse(Java), ReSharper(C#), Visual Studio 등이 있다.

### 1.2 리팩토링 도구가 가능한 이유

리팩토링 도구가 안전하게 동작할 수 있는 이유는, 이 도구들이 **구조적 변경만 수행하고 동작은 보존**하도록 설계되었기 때문이다.

예를 들어 "Rename" 리팩토링은:

1. 해당 이름의 모든 참조를 정확히 찾는다 (텍스트 검색이 아닌 구문 분석 기반).
2. 이름 충돌이 없는지 확인한다.
3. 모든 참조를 일괄 변경한다.

이 과정에서 프로그램의 동작은 전혀 바뀌지 않는다. 이름이 달라졌을 뿐, 실행되는 코드는 동일하다.

### 1.3 리팩토링 도구 사용 시 주의사항

Feathers는 리팩토링 도구의 가치를 인정하면서도 다음과 같은 주의를 당부한다:

| 주의사항 | 설명 |
|----------|------|
| **도구를 맹신하지 말라** | 리팩토링 도구도 버그가 있을 수 있다. 특히 복잡한 리팩토링(generics, reflection 관련)은 도구가 잘못 수행할 수 있다. |
| **테스트와 함께 사용하라** | 리팩토링 도구가 동작 보존을 보장하더라도, 테스트로 확인하는 것이 안전하다. |
| **한 번에 하나씩** | 여러 리팩토링을 연쇄적으로 수행하지 말고, 한 단계씩 수행하고 결과를 확인하라. |

> 리팩토링 도구는 강력하지만, **"테스트 없이 리팩토링 도구만으로 안전하다"는 것은 위험한 생각**이다. 도구는 보조 수단이지, 테스트를 대체하는 것이 아니다.

### 1.4 레거시 코드에서의 특별한 가치

레거시 코드에서 리팩토링 도구가 특히 유용한 상황:

- **테스트를 넣기 위한 초기 변경 단계**: Chapter 2에서 설명한 "레거시 코드의 딜레마"에서, 테스트 없이 수행해야 하는 초기 코드 변경을 리팩토링 도구가 안전하게 수행해줄 수 있다.
- **Extract Method**: 큰 메서드에서 테스트 가능한 단위를 추출할 때
- **Extract Interface**: Object Seam을 만들기 위해 인터페이스를 추출할 때
- **Rename**: 코드의 의도를 명확히 하여 이해하기 쉽게 만들 때

---

## 2. Mock 객체 프레임워크

### 2.1 Mock 프레임워크의 역할

Chapter 3에서 소개한 Mock Object를 직접 작성하는 대신, **Mock 프레임워크를 사용하면 런타임에 동적으로 Mock 객체를 생성**할 수 있다.

### 2.2 Mock 프레임워크의 장단점

| 장점 | 단점 |
|------|------|
| Mock 클래스를 직접 작성할 필요 없음 | 학습 곡선이 있음 |
| 기대 동작을 간결하게 설정 가능 | 과도한 사용 시 테스트가 구현에 결합됨 |
| 호출 검증이 자동화됨 | 복잡한 Mock 설정은 읽기 어려울 수 있음 |

### 2.3 Feathers의 관점

Feathers는 Mock 프레임워크가 유용한 도구임을 인정하지만, 이 책에서는 **직접 작성한 단순한 Fake Object를 더 선호**한다. 그 이유는:

1. **명시적이다**: Fake 클래스를 직접 읽으면 어떤 동작이 교체되었는지 바로 알 수 있다.
2. **레거시 코드에 점진적으로 적용하기 쉽다**: Mock 프레임워크를 도입하는 것 자체가 추가적인 변경이다.
3. **디버깅이 쉽다**: 문제가 생겼을 때 Fake 클래스를 직접 살펴볼 수 있다.

---

## 3. 단위 테스트 하네스 (Unit Testing Harness)

### 3.1 xUnit 프레임워크 계열

레거시 코드에 테스트를 작성하려면 **테스트 하네스(test harness)** 가 필요하다. 가장 널리 사용되는 것이 **xUnit 계열** 프레임워크다.

xUnit은 Kent Beck이 Smalltalk용으로 만든 SUnit에서 시작되어, 다양한 언어로 포팅되었다:

| 언어 | 프레임워크 | 비고 |
|------|-----------|------|
| **Java** | JUnit | 가장 널리 알려진 xUnit 구현 |
| **C++** | CppUnitLite | Feathers가 이 책에서 주로 사용. 경량 버전 |
| **C#** | NUnit | .NET 환경의 표준 테스트 프레임워크 |
| **Python** | unittest (PyUnit) | Python 표준 라이브러리에 포함 |
| **C++** | CppUnit | JUnit의 직접적인 C++ 포팅 |
| **Smalltalk** | SUnit | xUnit의 원조 |

### 3.2 xUnit의 기본 구조

xUnit 프레임워크는 다음과 같은 공통 구조를 가진다:

#### 테스트 케이스 (Test Case)

```java
// JUnit 예시
public class OrderTest extends TestCase {

    public void testDiscountForBulkOrder() {
        Order order = new Order();
        order.addItem(new Item("Widget", 10.00), 100);

        double total = order.calculateTotal();

        assertEquals(900.00, total, 0.01);  // 10% 대량 할인 적용
    }
}
```

#### 셋업과 티어다운 (setUp / tearDown)

```java
public class DatabaseTest extends TestCase {
    private FakeDatabase db;

    // 각 테스트 메서드 실행 전에 호출
    protected void setUp() {
        db = new FakeDatabase();
        db.addTestData();
    }

    // 각 테스트 메서드 실행 후에 호출
    protected void tearDown() {
        db.clear();
    }

    public void testQuery() {
        List results = db.query("SELECT * FROM users");
        assertEquals(3, results.size());
    }

    public void testInsert() {
        db.insert("users", new User("newuser"));
        assertEquals(4, db.count("users"));
    }
}
```

#### 테스트 스위트 (Test Suite)

```java
// 여러 테스트 케이스를 묶어서 실행
public class AllTests {
    public static Test suite() {
        TestSuite suite = new TestSuite();
        suite.addTestSuite(OrderTest.class);
        suite.addTestSuite(DatabaseTest.class);
        suite.addTestSuite(UserTest.class);
        return suite;
    }
}
```

### 3.3 xUnit의 핵심 원칙

xUnit 프레임워크가 공유하는 핵심 원칙:

1. **테스트는 독립적이다**: 각 테스트 메서드는 다른 테스트에 의존하지 않으며, 실행 순서에 영향을 받지 않는다.
2. **테스트는 자동 판정된다**: 사람이 출력을 보고 판단하는 것이 아니라, assert 문으로 자동으로 성공/실패가 결정된다.
3. **setUp/tearDown으로 환경을 관리한다**: 테스트 전후로 필요한 설정과 정리를 수행한다.
4. **테스트는 빠르게 실행된다**: Chapter 2에서 강조한 빠른 피드백 루프를 위해 필수적이다.

### 3.4 CppUnitLite

Feathers는 C++ 예시에서 **CppUnitLite**를 사용한다. CppUnit(JUnit의 직접 포팅)이 C++에서는 지나치게 복잡했기 때문에, Feathers가 **더 간결한 버전**을 만든 것이다.

```cpp
// CppUnitLite 예시
#include "TestHarness.h"

TEST(OrderTest, DiscountForBulkOrder)
{
    Order order;
    order.addItem(Item("Widget", 10.00), 100);

    double total = order.calculateTotal();

    DOUBLES_EQUAL(900.00, total, 0.01);
}
```

CppUnitLite의 특징:

- 매크로를 활용하여 **테스트 작성이 간결**하다.
- 등록(registration) 없이 테스트가 자동으로 발견된다.
- 의존성이 적어 레거시 프로젝트에 쉽게 추가할 수 있다.

---

## 4. 통합 테스트 프레임워크

### 4.1 FIT (Framework for Integrated Test)

**FIT**는 Ward Cunningham이 만든 통합 테스트 프레임워크로, **비개발자(고객, 기획자)도 테스트를 작성**할 수 있도록 설계되었다.

- 테스트를 **HTML 테이블** 형태로 작성한다.
- 비즈니스 규칙을 표 형태로 표현하므로 비개발자도 이해하기 쉽다.
- **Fixture** 클래스가 HTML 테이블과 실제 코드를 연결한다.

FIT 테스트 예시 (HTML 테이블):

| discount | quantity | expected_total |
|----------|----------|---------------|
| 0.1 | 100 | 900.00 |
| 0.0 | 10 | 100.00 |
| 0.2 | 50 | 400.00 |

### 4.2 Fitnesse

**Fitnesse**는 FIT를 기반으로 한 **위키 기반 테스트 프레임워크**다. Robert C. Martin과 Micah Martin이 개발했다.

- **위키 페이지**에서 테스트를 작성하고 실행할 수 있다.
- 웹 브라우저에서 테스트를 작성, 실행, 결과 확인이 모두 가능하다.
- 팀 전체(개발자, QA, 기획자)가 함께 사용할 수 있다.

### 4.3 통합 테스트 프레임워크의 위치

Feathers는 통합 테스트 프레임워크의 가치를 인정하면서도, 이 책의 초점은 **단위 테스트**임을 분명히 한다:

| 테스트 유형 | 역할 | 이 책에서의 비중 |
|------------|------|----------------|
| **단위 테스트 (xUnit)** | 코드 수준의 빠른 피드백, 의존성 격리 | 핵심 도구 |
| **통합 테스트 (FIT/Fitnesse)** | 비즈니스 규칙 수준의 검증, 팀 협업 | 보조 도구 |

---

## 5. 도구 선택의 원칙

이 장은 상대적으로 짧고 도구 소개 위주이지만, Feathers가 전달하려는 핵심 메시지가 있다:

### 5.1 도구는 수단이지 목적이 아니다

> 어떤 도구를 사용하느냐보다, **테스트를 작성하고 피드백을 얻는 습관**이 더 중요하다.

가장 세련된 Mock 프레임워크를 사용해도, 테스트를 실행하지 않으면 의미가 없다. 가장 단순한 xUnit 프레임워크라도, 꾸준히 테스트를 작성하고 실행하면 엄청난 가치를 제공한다.

### 5.2 레거시 코드에 도구를 도입할 때

레거시 프로젝트에 테스트 인프라를 처음 도입할 때 고려할 점:

1. **가장 단순한 도구부터 시작하라**: 복잡한 도구를 한 번에 도입하지 말고, xUnit 프레임워크 하나부터 시작한다.
2. **도구 도입 자체를 최소화하라**: 도구를 추가하는 것도 변경이다. 레거시 시스템에 대한 변경은 최소화해야 한다.
3. **팀이 사용할 수 있는 도구를 선택하라**: 가장 좋은 도구가 아니라, 팀이 실제로 사용할 도구가 가장 좋은 도구다.

---

## 요약

- **자동화된 리팩토링 도구**는 구조적 변경을 안전하게 수행한다. 하지만 맹신하지 말고 테스트와 함께 사용해야 한다.
- **Mock 프레임워크**는 동적으로 Mock 객체를 생성한다. 유용하지만 Feathers는 단순한 Fake Object를 선호한다.
- **xUnit 프레임워크**(JUnit, CppUnitLite, NUnit 등)는 단위 테스트의 표준 도구다. 테스트의 독립성, 자동 판정, 빠른 실행이 핵심 원칙이다.
- **FIT/Fitnesse** 같은 통합 테스트 프레임워크는 비즈니스 규칙 수준의 테스트에 유용하다.
- 도구는 수단이지 목적이 아니다. 가장 중요한 것은 **테스트를 작성하고 피드백을 얻는 습관**이다.

---

## 다음 챕터와의 연결

Chapter 5까지가 Part I(서론 부분)이다. Chapter 6부터는 Part II로, 레거시 코드에서 만나는 **구체적인 문제 상황들**을 다룬다. Chapter 6 **"고칠 것은 많고 시간은 없고 (I Don't Have Much Time and I Have to Change It)"** 에서는 시간 압박 속에서도 안전하게 변경하기 위한 실용적인 기법들 — Sprout Method, Sprout Class, Wrap Method, Wrap Class — 을 소개한다.
