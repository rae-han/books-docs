# Chapter 25: Test-Driven Development Patterns (TDD 패턴)

## 핵심 질문

TDD를 실천할 때 반복적으로 등장하는 메타-패턴들은 무엇인가? 테스트는 무엇이며, 어떻게 작성하고, 어떤 순서로 실행해야 하며, 테스트 데이터는 어떻게 선택해야 하는가?

---

## 1. 이 챕터의 위치와 역할

Part III는 Part I(Money 예제)과 Part II(xUnit 예제)에서 **암묵적으로** 사용한 기법들을 **명시적인 패턴**으로 정리하는 구간이다. Chapter 25는 그 첫 번째 장으로, TDD 자체에 대한 메타-패턴을 다룬다. 즉, "어떻게 테스트를 작성하고 실행할 것인가?"라는 근본적인 질문에 대한 답을 패턴 형태로 제시한다.

이 챕터에서 다루는 7개 패턴:

| 패턴 | 핵심 질문 |
|------|----------|
| Test (명사로서의 테스트) | 테스트란 무엇인가? |
| Isolated Test | 테스트들은 서로 어떤 관계여야 하는가? |
| Test List | 작업 시작 전에 무엇을 해야 하는가? |
| Test First | 테스트는 언제 작성하는가? |
| Assert First | 테스트 코드는 어디서부터 작성하는가? |
| Test Data | 테스트에서 어떤 데이터를 사용해야 하는가? |
| Evident Data | 테스트의 의도를 어떻게 명확히 표현하는가? |

---

## 2. Test (명사로서의 테스트)

### 문제

소프트웨어를 개발할 때, 코드가 올바르게 동작하는지 어떻게 확인하는가?

### 패턴

**자동화된 테스트를 작성한다.** 테스트란 "컴퓨터가 자동으로 실행하여 결과를 판정하는 프로그램"이다.

### 설명

Kent Beck은 테스트를 **명사**로 정의한다. 테스트는 동사("테스트하다")가 아니라 명사("테스트")다. 즉, 테스트는 한 번 수행하고 버리는 행위가 아니라, **영구적으로 보관하고 반복 실행하는 자산**이다.

수동 테스트와 자동화된 테스트의 차이:

| 수동 테스트 | 자동화된 테스트 |
|-------------|----------------|
| 사람이 실행하고 눈으로 확인한다 | 컴퓨터가 실행하고 자동으로 판정한다 |
| 시간이 지나면 잊혀진다 | 코드베이스에 영구적으로 존재한다 |
| 변경 후 재실행이 번거롭다 | 변경 후 즉시 재실행할 수 있다 |
| 회귀 버그를 놓치기 쉽다 | 회귀 버그를 즉시 감지한다 |

Kent Beck이 강조하는 핵심은, 테스트가 단순한 검증 수단이 아니라 **설계 도구**이기도 하다는 점이다. 테스트를 먼저 작성하면 코드의 인터페이스를 사용자 관점에서 설계하게 된다.

### Part I에서의 예시

Part I Chapter 1에서 작성한 첫 테스트가 바로 이 패턴의 실례다:

```java
public void testMultiplication() {
    Dollar five = new Dollar(5);
    five.times(2);
    assertEquals(10, five.amount);
}
```

이 테스트는 한 번 작성한 후 폐기되지 않는다. Part I 전체에 걸쳐 계속 실행되며, 코드를 변경할 때마다 기존 동작이 깨지지 않았는지 확인해준다.

> **핵심 통찰**: 테스트는 일회용 검증 행위가 아니라, 코드베이스와 함께 살아가는 **실행 가능한 명세서**다. "이 코드가 어떻게 동작해야 하는가?"를 코드로 표현한 것이 테스트다.

---

## 3. Isolated Test (격리된 테스트)

### 문제

테스트 A가 실패하면 테스트 B도 연쇄적으로 실패하는 상황에서, 실제 문제가 어디에 있는지 어떻게 파악하는가?

### 패턴

**테스트들은 서로 완전히 독립적이어야 한다.** 한 테스트의 실행이 다른 테스트의 결과에 영향을 주어서는 안 된다. 테스트 실행 순서가 결과에 영향을 주어서도 안 된다.

### 설명

테스트 격리의 핵심 원칙:

1. **테스트 간 공유 상태 금지**: 한 테스트에서 생성한 데이터가 다른 테스트에 보여서는 안 된다
2. **실행 순서 무관**: 테스트를 어떤 순서로 실행하든 같은 결과가 나와야 한다
3. **각 테스트는 자신의 환경을 직접 설정**: 이전 테스트가 만들어놓은 환경에 의존하지 않는다

격리 위반의 전형적 사례:

```java
// 나쁜 예 — 테스트 간 상태 공유
static Dollar sharedDollar = new Dollar(5);

public void testMultiplication() {
    sharedDollar.times(2);
    assertEquals(10, sharedDollar.amount);
    // sharedDollar의 amount가 이제 10으로 변경됨!
}

public void testAddition() {
    // sharedDollar.amount가 10인 상태에서 시작...
    // testMultiplication이 먼저 실행되었을 때만 통과!
}
```

```java
// 좋은 예 — 각 테스트가 독립적
public void testMultiplication() {
    Dollar five = new Dollar(5);  // 자체 생성
    Dollar result = five.times(2);
    assertEquals(new Dollar(10), result);
}

public void testAddition() {
    Dollar five = new Dollar(5);  // 자체 생성
    Dollar result = five.plus(five);
    assertEquals(new Dollar(10), result);
}
```

### Part II에서의 예시

Part II에서 xUnit을 구현할 때, `setUp()` 메서드가 바로 Isolated Test 패턴을 지원하기 위해 존재한다. 매 테스트 실행 전에 `setUp()`이 호출되어 깨끗한 환경을 보장한다:

```python
class TestCaseTest(TestCase):
    def setUp(self):
        self.result = TestResult()  # 매 테스트마다 새 결과 객체

    def testRunning(self):
        test = WasRun("testMethod")
        test.run(self.result)
        assert test.wasRun  # 이전 테스트와 무관하게 동작
```

> **핵심 통찰**: 테스트 격리는 편의성이 아니라 **필수 조건**이다. 테스트가 서로 의존하면, 하나의 실패가 연쇄 실패를 일으켜 디버깅이 극도로 어려워진다. 테스트 격리를 위해 약간의 중복 코드(setup)를 감수하는 것은 그만한 가치가 있다.

---

## 4. Test List (테스트 목록)

### 문제

"다음에 무엇을 해야 하지?"라는 생각이 머릿속을 맴돌며 현재 작업에 집중하지 못할 때, 어떻게 해야 하는가?

### 패턴

**코딩을 시작하기 전에 작성해야 할 테스트 목록을 만든다.** 떠오르는 모든 테스트를 목록에 적고, 현재는 하나의 테스트에만 집중한다. 작업 중 새로운 테스트가 떠오르면 목록에 추가한다.

### 설명

Test List는 Part I과 Part II에서 **TODO 리스트**라는 이름으로 계속 사용된 패턴이다. Kent Beck은 코딩을 시작하기 전에 항상 다음을 수행한다:

1. 구현해야 할 기능을 생각한다
2. 각 기능을 검증할 수 있는 테스트를 목록으로 작성한다
3. 리팩토링이 필요한 부분도 목록에 포함한다
4. 한 번에 하나씩 처리한다

목록 작성의 규칙:

- **완벽할 필요 없다** — 작업하면서 항목을 추가하거나 삭제할 수 있다
- **너무 길면 안 된다** — 10개 이상이면 필터링이 필요하다는 신호다
- **구현할 수 없는 항목도 적는다** — 나중에 작은 항목으로 분해할 수 있다

### Part I에서의 예시

Part I Chapter 1에서 시작된 TODO 리스트:

```
- [ ] $5 + 10 CHF = $10 (환율이 2:1인 경우)
- [ ] $5 × 2 = $10
- [ ] amount를 private으로 만들기
- [ ] Dollar 부작용(side effect)?
- [ ] Money 반올림?
```

이 목록은 챕터가 진행될수록 항목이 추가되고 완료되면서 진화했다. Chapter 3에서 `equals()`와 `hashCode()`가 추가되었고, Chapter 5에서 `Franc` 관련 항목이 추가되었다.

> **핵심 통찰**: Test List는 GTD(Getting Things Done)의 TDD 버전이다. 머릿속의 걱정을 종이(또는 코드) 위로 꺼내놓으면, 뇌가 "기억하기"에서 해방되어 "현재 문제 해결하기"에 집중할 수 있다. 프로그래밍에서 가장 큰 적은 산만함이며, Test List는 그것에 대한 해독제다.

---

## 5. Test First (테스트 우선)

### 문제

코드를 먼저 작성하고 나중에 테스트를 추가하려고 하면, 테스트를 건너뛰게 되거나 테스트하기 어려운 코드를 만들게 된다. 테스트는 언제 작성해야 하는가?

### 패턴

**코드를 작성하기 전에 테스트를 먼저 작성한다.**

### 설명

"나중에 테스트를 추가해야지"라는 생각은 거의 실현되지 않는다. 코드가 동작하면 다음 기능으로 넘어가고 싶은 유혹이 강하기 때문이다. Kent Beck은 이 문제에 대해 두 가지 관점에서 Test First를 정당화한다.

**심리적 관점**: 테스트를 먼저 작성하면 스트레스가 줄어든다. "이 코드가 동작할까?"라는 불안 대신, "테스트가 통과하면 동작하는 것이다"라는 확신을 갖게 된다.

**설계적 관점**: 테스트를 먼저 작성하면 코드의 **사용자 관점**에서 인터페이스를 설계하게 된다. 구현 세부사항에 끌려가지 않고, "이 코드를 어떻게 사용하고 싶은가?"를 먼저 생각하게 된다.

코드 우선 vs 테스트 우선의 비교:

| 코드 우선 | 테스트 우선 |
|-----------|-----------|
| 구현 관점에서 인터페이스 설계 | 사용자 관점에서 인터페이스 설계 |
| "이걸 어떻게 만들지?" | "이걸 어떻게 사용하고 싶지?" |
| 테스트를 나중에 추가 (또는 건너뜀) | 테스트가 코드와 함께 성장 |
| 테스트하기 어려운 코드 가능성 | 테스트 용이한 코드가 자연스럽게 만들어짐 |

### Part I에서의 예시

Part I의 모든 챕터에서 예외 없이 Test First가 적용되었다. Chapter 1에서 `Dollar` 클래스는 아직 존재하지도 않는데 테스트를 먼저 작성했다:

```java
// Dollar 클래스가 아직 없다!
public void testMultiplication() {
    Dollar five = new Dollar(5);  // 컴파일 에러 — Dollar가 없음
    five.times(2);
    assertEquals(10, five.amount);
}
```

이 테스트가 먼저 존재했기 때문에, `Dollar` 클래스의 인터페이스(`생성자에 int`, `times(int)`, `amount 필드`)가 자연스럽게 결정되었다.

> **핵심 통찰**: Test First는 단순한 습관이 아니라 **설계 기법**이다. 테스트를 먼저 작성하면 "이 코드를 사용하는 입장에서 가장 편한 인터페이스가 무엇인가?"를 강제로 고민하게 된다. 이것이 좋은 API를 만드는 가장 확실한 방법이다.

---

## 6. Assert First (단언 우선)

### 문제

테스트를 작성할 때, 어디서부터 시작해야 하는가? 설정(setup) 코드부터? 실행(act) 코드부터?

### 패턴

**테스트를 작성할 때, 단언(assertion)부터 먼저 작성하고 역순으로 올라간다.**

### 설명

대부분의 테스트는 다음 구조를 따른다:

1. **Arrange(준비)**: 테스트에 필요한 객체와 데이터를 설정한다
2. **Act(실행)**: 테스트 대상 코드를 실행한다
3. **Assert(단언)**: 기대하는 결과를 검증한다

Assert First 패턴은 이 순서를 **거꾸로** 작성할 것을 권한다. 왜냐하면, 단언을 먼저 작성하면 **"내가 원하는 결과가 무엇인가?"**를 가장 먼저 명확히 하게 되기 때문이다.

### 단계별 작성 과정

예를 들어, "소켓을 통해 통신하는 시스템"을 테스트한다고 하자.

**Step 1**: 단언부터 작성한다 — "결과가 어떠해야 하는가?"

```java
// Step 1: 내가 기대하는 결과
assertTrue(socket.isClosed());
```

**Step 2**: 결과를 만들려면 어떤 행동이 필요한가?

```java
// Step 2: 소켓을 닫는 행동 추가
socket.close();
assertTrue(socket.isClosed());
```

**Step 3**: 행동을 수행하려면 어떤 준비가 필요한가?

```java
// Step 3: 소켓 생성 추가
Socket socket = new Socket("localhost", defaultPort());
socket.close();
assertTrue(socket.isClosed());
```

**Step 4**: 완전한 테스트 형태로 정리

```java
public void testSocketCloses() {
    Socket socket = new Socket("localhost", defaultPort());
    socket.close();
    assertTrue(socket.isClosed());
}
```

### Assert First가 효과적인 이유

```
일반적 사고: "먼저 이것을 준비하고, 그 다음 이것을 실행하고, 그러면 이런 결과가 나올 것이다"
Assert First 사고: "이런 결과를 원한다 → 그러려면 이런 실행이 필요하다 → 그러려면 이런 준비가 필요하다"
```

Assert First는 **목표 지향적 사고**를 유도한다. "나는 어디로 가고 있는가?"를 먼저 명확히 하면, 불필요한 설정 코드나 엉뚱한 방향으로의 탈선을 방지할 수 있다.

> **핵심 통찰**: Assert First는 테스트 작성의 "나침반"이다. 목적지(기대 결과)를 먼저 정하면, 그곳에 도달하기 위한 경로(실행 코드와 설정 코드)가 자연스럽게 결정된다. 설정부터 시작하면 "이게 정말 필요한 설정인가?"를 판단하기 어렵다.

---

## 7. Test Data (테스트 데이터)

### 문제

테스트에서 어떤 데이터를 사용해야 하는가? 실제 운영 데이터를 사용해야 하는가? 아니면 인위적으로 만든 데이터를 사용해야 하는가?

### 패턴

**테스트에서 사용하는 데이터는 의미 있는 최소한의 데이터여야 한다.** 불필요하게 큰 숫자나 복잡한 데이터 구조를 사용하지 않는다. 1, 2, 3과 같은 작은 숫자로 충분하다면, 굳이 1000이나 3.14159를 사용하지 않는다.

### 설명

테스트 데이터 선택의 원칙:

1. **같은 의미를 전달하는 여러 데이터 중 가장 단순한 것을 선택한다**
2. **매직 넘버를 피하고, 각 숫자가 고유한 역할을 하도록 한다**
3. **실제 데이터(real data)가 필요한 경우는 별도로 구분한다**

나쁜 예와 좋은 예:

```java
// 나쁜 예 — 불필요하게 큰 숫자, 의미 불분명
public void testMultiplication() {
    Dollar price = new Dollar(1472);
    Dollar result = price.times(37);
    assertEquals(new Dollar(54464), result);
}
```

```java
// 좋은 예 — 작고 명확한 숫자
public void testMultiplication() {
    Dollar five = new Dollar(5);
    Dollar result = five.times(2);
    assertEquals(new Dollar(10), result);
}
```

첫 번째 테스트에서 `1472 × 37 = 54464`를 검증하지만, 이 숫자들은 아무런 추가 의미도 전달하지 않는다. `5 × 2 = 10`으로 충분히 곱하기가 동작하는지 검증할 수 있으며, 의도도 더 명확하다.

### 예외: 실제 데이터가 필요한 경우

다음과 같은 경우에는 실제(또는 실제에 가까운) 데이터를 사용해야 한다:

- **성능 테스트**: 실제 규모의 데이터를 사용해야 의미가 있다
- **실제 데이터에서 발견된 버그**: 해당 데이터로 회귀 테스트를 작성해야 한다
- **외부 시스템과의 통합**: 실제 프로토콜에 맞는 데이터가 필요하다

> **핵심 통찰**: 테스트 데이터의 목표는 **의도를 명확히 전달하는 것**이다. 큰 숫자가 "이 테스트는 실제 데이터를 사용한다"는 느낌을 줄 수 있지만, 실제로는 테스트의 의도를 흐리게 만든다. 작고 단순한 데이터가 더 좋은 문서가 된다.

---

## 8. Evident Data (명백한 데이터)

### 문제

테스트를 읽는 사람이 "이 테스트가 무엇을 검증하는지" 쉽게 이해할 수 있게 하려면 어떻게 해야 하는가?

### 패턴

**테스트에서 입력값과 기대 결과값 사이의 관계를 명백하게 드러낸다.** 기대값을 계산된 상수가 아니라, 계산 과정이 보이는 표현식으로 작성한다.

### 설명

Evident Data의 핵심은 "테스트를 읽는 사람이 **왜 이 기대값이 나오는지** 바로 알 수 있어야 한다"는 것이다.

```java
// 나쁜 예 — 기대값의 출처가 불분명
public void testCurrencyConversion() {
    Bank bank = new Bank();
    bank.addRate("CHF", "USD", 2);
    Money result = bank.reduce(Money.franc(100), "USD");
    assertEquals(Money.dollar(50), result);
}
// 독자: "왜 50달러가 되는 거지?" → 100 / 2 = 50임을 머리로 계산해야 함
```

```java
// 좋은 예 — 입력과 기대값의 관계가 명백
public void testCurrencyConversion() {
    Bank bank = new Bank();
    bank.addRate("CHF", "USD", 2);
    Money result = bank.reduce(Money.franc(100), "USD");
    assertEquals(Money.dollar(100 / 2), result);
}
// 독자: "100 CHF를 환율 2로 나누면 50 USD" → 즉시 이해 가능
```

두 번째 테스트에서 `Money.dollar(100 / 2)`라고 쓰면, "100프랑을 환율 2로 나누면 50달러"라는 관계가 코드에 직접 드러난다. `Money.dollar(50)`이라고 쓰면, 독자가 직접 역산해야 한다.

### Part I에서의 예시

Part I Chapter 12에서 다중 통화 더하기를 테스트할 때:

```java
// Part I에서의 실제 테스트
public void testMixedAddition() {
    Expression fiveBucks = Money.dollar(5);
    Expression tenFrancs = Money.franc(10);
    Bank bank = new Bank();
    bank.addRate("CHF", "USD", 2);
    Money result = bank.reduce(fiveBucks.plus(tenFrancs), "USD");
    assertEquals(Money.dollar(10), result);
}
// 5 USD + 10 CHF = 5 + (10 / 2) = 5 + 5 = 10 USD
// 이 계산 과정이 테스트의 숫자 선택에 녹아 있다
```

여기서 Kent Beck은 환율을 `2:1`로 설정했다. `1.5:1` 같은 실제적인 환율 대신 계산이 명백한 숫자를 선택하여, 독자가 테스트의 의도를 즉시 파악할 수 있게 했다.

> **핵심 통찰**: Evident Data는 Test Data의 확장이다. Test Data가 "작은 데이터를 사용하라"고 했다면, Evident Data는 "데이터 간의 관계를 명백히 드러내라"고 한다. 좋은 테스트는 **그 자체로 문서**이며, 기대값이 왜 그 값인지를 코드가 설명해야 한다.

---

## 9. 패턴 간의 관계

이 챕터의 7개 패턴은 서로 긴밀하게 연결되어 있다:

```
Test (테스트란 무엇인가?)
  ├─ Isolated Test (테스트들은 독립적이어야 한다)
  ├─ Test List (작성할 테스트 목록을 먼저 만든다)
  │    └─ Test First (테스트를 코드보다 먼저 작성한다)
  │         └─ Assert First (단언을 먼저 작성한다)
  └─ Test Data + Evident Data (데이터 선택 전략)
       ├─ Test Data (작고 단순한 데이터를 사용한다)
       └─ Evident Data (데이터 간 관계를 명백히 한다)
```

전체 흐름으로 요약하면:

1. **Test List**로 해야 할 테스트 목록을 만든다
2. 목록에서 하나를 골라 **Test First**로 테스트를 먼저 작성한다
3. 테스트 작성 시 **Assert First**로 기대 결과부터 작성한다
4. 테스트 데이터는 **Test Data**(작고 단순한)와 **Evident Data**(관계가 명백한)를 적용한다
5. 각 테스트는 **Isolated Test**를 지켜 다른 테스트와 독립적이게 한다
6. 이 모든 것이 **Test**(자동화된 검증 프로그램)라는 결과물을 만든다

---

## 요약

- **Test**: 테스트는 자동화된 프로그램이다. 한 번 작성하면 영구적으로 보관하고 반복 실행하는 자산이다.
- **Isolated Test**: 테스트들은 서로 완전히 독립적이어야 한다. 실행 순서가 결과에 영향을 주면 안 된다. `setUp()`으로 매 테스트마다 깨끗한 환경을 보장한다.
- **Test List**: 코딩 전에 작성할 테스트 목록을 만든다. 머릿속의 걱정을 종이 위로 꺼내놓아 현재 작업에 집중한다.
- **Test First**: 코드보다 테스트를 먼저 작성한다. 이것은 습관이 아니라 설계 기법이다 — 사용자 관점의 인터페이스가 자연스럽게 만들어진다.
- **Assert First**: 테스트 작성 시 단언(기대 결과)부터 시작하고 역순으로 올라간다. 목표 지향적 사고를 유도한다.
- **Test Data**: 의미를 전달하는 최소한의 데이터를 사용한다. `5 × 2 = 10`이면 충분하다.
- **Evident Data**: 입력값과 기대 결과값 사이의 관계를 명백히 드러낸다. `assertEquals(Money.dollar(100 / 2), result)`처럼 계산 과정을 코드에 녹인다.

---

## 다른 챕터와의 관계

- **Chapter 1 (Multi-Currency Money)**: 이 챕터에서 정리된 모든 패턴(Test First, Fake It, Test List 등)이 Chapter 1에서 실전으로 시연되었다. Part I 전체가 이 패턴들의 실례 모음이다.
- **Chapter 18 (First Steps to xUnit)**: Part II에서도 동일한 패턴들이 Python 환경에서 적용된다. 특히 Isolated Test를 지원하기 위해 `setUp()` / `tearDown()`을 구현했다.
- **Chapter 26 (Red Bar Patterns)**: "어떤 테스트를 목록에서 골라야 하는가?"에 대한 구체적인 전략을 제공한다. Test List에서 다음 테스트를 선택하는 기준이 된다.
- **Chapter 27 (Testing Patterns)**: 테스트 작성의 구체적인 기법(Mock Object, Self Shunt 등)을 다룬다. 이 챕터의 메타-패턴 위에 구축되는 실전 패턴이다.
- **Chapter 28 (Green Bar Patterns)**: 테스트를 통과시키는 구체적인 전략(Fake It, Triangulation, Obvious Implementation)을 다룬다. Test First로 작성된 테스트를 Green으로 만드는 방법이다.
