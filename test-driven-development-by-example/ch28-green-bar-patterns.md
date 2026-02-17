# Chapter 28: Green Bar Patterns (Green Bar 패턴)

## 핵심 질문

실패하는 테스트(Red Bar)를 어떻게 통과시키는가? 상수를 반환해야 하는가, 바로 올바른 구현을 작성해야 하는가, 아니면 두 번째 테스트로 일반화를 강제해야 하는가? 단일 원소에 대해 먼저 구현하고 컬렉션으로 확장하는 전략은 어떻게 작동하는가?

---

## 1. 이 챕터의 위치와 역할

TDD의 Red-Green-Refactor 사이클에서, 이 챕터는 **Green 단계** — 실패하는 테스트를 통과시키는 과정에 관한 패턴을 다룬다. Chapter 26이 "어떤 테스트를 작성할 것인가?(Red)"를 다루었다면, Chapter 28은 "그 테스트를 어떻게 통과시킬 것인가?(Green)"를 다룬다.

이 챕터에서 다루는 4개 패턴:

| 패턴 | 핵심 전략 | 사용 시점 |
|------|----------|----------|
| Fake It ('Til You Make It) | 상수를 반환하고 점진적으로 일반화 | 구현 방법이 불확실할 때 |
| Triangulation | 두 번째 테스트로 일반화를 강제 | 올바른 추상화가 불분명할 때 |
| Obvious Implementation | 올바른 구현을 바로 작성 | 구현이 명백할 때 |
| One to Many | 단수에서 복수로 점진 확장 | 컬렉션을 다뤄야 할 때 |

---

## 2. Fake It ('Til You Make It) (가짜로 만들기)

### 문제

테스트를 통과시키는 코드를 작성해야 하는데, 올바른 구현이 무엇인지 확신이 서지 않는다. 어떻게 시작해야 하는가?

### 패턴

**테스트가 기대하는 정확한 값(상수)을 반환하여 테스트를 통과시킨다. 그 다음, 리팩토링 단계에서 상수를 변수로 점진적으로 대체하여 일반적인 구현으로 진화시킨다.**

### 설명

Fake It은 TDD에서 가장 특징적이고, 처음 접하는 사람에게 가장 반직관적인 전략이다. "정답을 하드코딩하는 게 무슨 의미가 있지?"라는 의문이 자연스럽다. Kent Beck은 세 가지 이유를 제시한다:

**1. 심리적 효과 — Green Bar의 안도감**

Red Bar(실패)에서 Green Bar(성공)로 전환되는 순간, 프로그래머는 "올바른 방향으로 가고 있다"는 확신을 얻는다. 이 확신이 다음 단계를 진행할 동력이 된다.

**2. 범위 제어 — 한 번에 하나씩**

상수로 시작하면, "테스트를 통과시키는 문제"와 "올바른 구현을 만드는 문제"를 분리할 수 있다. 두 문제를 동시에 풀려 하면 복잡도가 곱해진다.

**3. 중복 제거가 구현을 이끌어낸다**

Fake It 후의 리팩토링에서, 테스트에 있는 데이터와 코드에 있는 상수 사이의 **중복을 제거**하면 자연스럽게 일반적인 구현이 만들어진다.

### Part I Chapter 1에서의 사용

이것은 Part I에서 가장 처음 사용된 전략이다:

```java
// 테스트
public void testMultiplication() {
    Dollar five = new Dollar(5);
    five.times(2);
    assertEquals(10, five.amount);
}
```

```java
// Step 1: Fake It — 상수 반환
class Dollar {
    int amount = 10;  // 하드코딩!
    Dollar(int amount) {}
    void times(int multiplier) {}
}
// Green Bar!
```

```java
// Step 2: 중복 제거 — 10은 어디서 왔는가? 5 × 2에서 왔다
class Dollar {
    int amount;
    Dollar(int amount) {
        this.amount = amount;  // 5를 받아서
    }
    void times(int multiplier) {
        amount *= multiplier;  // 2를 곱한다
    }
}
// 여전히 Green Bar! 그리고 이제 일반적인 구현이다
```

이 과정에서 핵심은 **"10"이라는 중복**이다:
- 테스트가 `assertEquals(10, ...)`이라고 말한다
- 코드가 `amount = 10`이라고 말한다
- 이 중복을 제거하면 `amount = 5 * 2`, 즉 `amount *= multiplier`가 된다

### Fake It의 진화 과정 시각화

```
테스트: assertEquals(10, five.amount)
                        ↕ 중복
코드:   amount = 10
              ↓ 10 → 5 * 2
        amount = 5 * 2
              ↓ 5 → amount (생성자 파라미터)
        amount = amount * 2
              ↓ 2 → multiplier (메서드 파라미터)
        amount = amount * multiplier
              ↓ 최종 형태
        amount *= multiplier
```

매 단계에서 하나의 상수를 하나의 변수로 대체했다. 이것이 Fake It의 리팩토링 절차다.

> **핵심 통찰**: Fake It은 "속임수"가 아니라 **발견의 과정**이다. 상수에서 시작하여 중복을 제거하면, 올바른 구현이 자연스럽게 드러난다. 이것은 "구현을 설계한다"가 아니라 "구현이 발견된다"에 가깝다. 테스트와 코드 사이의 중복 제거가 구현을 이끌어내는 힘이다.

---

## 3. Triangulation (삼각측량)

### 문제

Fake It으로 상수를 반환했는데, 이 상수를 어떻게 일반화해야 할지 모르겠다. 한 가지 예제만으로는 올바른 추상화가 무엇인지 판단하기 어렵다.

### 패턴

**두 번째 테스트 케이스를 추가하여, 첫 번째 테스트에서 통과한 가짜 구현이 깨지도록 한다. 두 테스트를 동시에 통과시키려면 일반화가 불가피해진다.**

### 설명

삼각측량은 측량학에서 온 비유다:

```
관측점 A만 있으면 → 대상의 위치를 선(line) 위로만 좁힐 수 있다
관측점 A + B가 있으면 → 대상의 정확한 위치를 특정할 수 있다

테스트 1개만 있으면 → return 상수로 통과 가능 (위치 특정 불가)
테스트 2개가 있으면 → 일반적 구현이 필요 (위치 특정)
```

### Part I Chapter 3에서의 사용

Chapter 3에서 `equals()` 구현 시 삼각측량을 사용했다:

```java
// 테스트 1: 같은 값은 동등
assertTrue(new Dollar(5).equals(new Dollar(5)));
```

```java
// Fake It: 무조건 true
public boolean equals(Object object) {
    return true;  // 테스트 1 통과!
}
```

```java
// 테스트 2: 다른 값은 비동등 (삼각측량!)
assertFalse(new Dollar(5).equals(new Dollar(6)));
// return true 로는 이 테스트를 통과시킬 수 없다!
```

```java
// 일반화가 강제된다
public boolean equals(Object object) {
    Dollar dollar = (Dollar) object;
    return amount == dollar.amount;  // 실제 비교
}
// 두 테스트 모두 통과!
```

### 삼각측량의 사고 과정

```
Step 1: 테스트 → assertTrue($5 == $5)
        코드  → return true         ← Fake It
        상태  → Green (하지만 가짜)

Step 2: 테스트 추가 → assertFalse($5 == $6)
        코드  → return true         ← 테스트 2 실패!
        상태  → Red

Step 3: 코드 일반화 → return amount == dollar.amount
        상태  → Green (그리고 진짜)
```

### 삼각측량을 사용해야 하는 경우

Kent Beck은 삼각측량을 **"올바른 추상화가 무엇인지 확신이 서지 않을 때"** 사용한다고 말한다:

- 알고리즘의 일반화 방향이 불분명할 때
- 경계 조건이 복잡할 때
- "이것만 처리하면 되나, 저것도 처리해야 하나?"가 불확실할 때

반면, 추상화가 명백하다면 삼각측량은 불필요하다. 바로 Obvious Implementation을 사용할 수 있다.

> **핵심 통찰**: 삼각측량은 **과잉 설계를 방지하는 장치**다. 하나의 예제에서 성급하게 일반화하면, 실제로 필요하지 않은 복잡성을 추가할 수 있다. 두 번째 예제가 "정말로 일반화가 필요한가?"를 검증하고, "어떤 방향으로 일반화해야 하는가?"를 안내한다.

---

## 4. Obvious Implementation (명백한 구현)

### 문제

테스트를 통과시키는 올바른 구현이 머릿속에 명백하게 떠오른다. 그래도 Fake It이나 삼각측량을 거쳐야 하는가?

### 패턴

**구현이 명백하면 바로 작성한다.** Fake It이나 삼각측량은 불확실할 때의 도구이지, 항상 사용해야 하는 의식(ritual)이 아니다.

### 설명

Kent Beck은 TDD를 **의식이 아니라 도구**로 바라본다. 구현이 명백하면 곧장 작성하고, 테스트를 실행하여 확인한다. 불확실하면 Fake It으로 돌아간다.

### Part I Chapter 2에서의 사용

Chapter 2에서 `times()` 메서드를 값 객체 패턴에 맞게 수정할 때:

```java
// 테스트
public void testMultiplication() {
    Dollar five = new Dollar(5);
    Dollar product = five.times(2);
    assertEquals(10, product.amount);
    product = five.times(3);
    assertEquals(15, product.amount);
}
```

```java
// Obvious Implementation — 바로 올바른 구현을 작성
Dollar times(int multiplier) {
    return new Dollar(amount * multiplier);
}
```

여기서 Kent Beck은 Fake It을 사용하지 않았다. `new Dollar(amount * multiplier)`라는 구현이 명백했기 때문이다.

### Obvious Implementation의 위험 신호

Obvious Implementation은 **확신이 있을 때만** 사용해야 한다. 다음과 같은 신호가 나타나면 Fake It으로 전환해야 한다:

```
"명백한 구현"을 작성했는데...
  → 테스트가 실패한다 → Fake It으로 전환!
  → 다시 작성했는데 또 실패한다 → 반드시 Fake It으로 전환!
  → 예상치 못한 에러가 나온다 → Fake It으로 전환!
```

Kent Beck의 경험 법칙:

> Obvious Implementation을 시도해서 Red Bar가 나오는 것은 괜찮다. 두 번 연속 Red Bar가 나오면, 그것은 "지금 당신의 확신 수준이 실제 난이도에 비해 과대평가되어 있다"는 신호다. 작은 단계로 돌아가라.

### Fake It vs Obvious Implementation — 실무적 판단

```
확신 높음, 문제 단순 → Obvious Implementation
  예: 단순한 getter 메서드, 기본 연산

확신 중간 → Obvious Implementation 시도, Red Bar 시 Fake It으로 전환
  예: 약간 복잡한 로직, 익숙하지만 간간이 실수하는 패턴

확신 낮음, 문제 복잡 → Fake It 또는 Triangulation
  예: 새로운 알고리즘, 이해가 불완전한 도메인
```

> **핵심 통찰**: Obvious Implementation은 **자신감의 표현**이다. 하지만 그 자신감이 틀렸을 때, TDD는 즉각적인 피드백(Red Bar)으로 알려준다. 중요한 것은 "항상 작은 단계를 밟아야 한다"가 아니라, **"Red Bar가 나오면 작은 단계로 돌아가는 규율"**이 있는가이다.

---

## 5. One to Many (하나에서 여럿으로)

### 문제

컬렉션(리스트, 배열 등)을 다루는 코드를 구현해야 한다. 처음부터 컬렉션을 처리하는 코드를 작성하면 복잡하다. 어떻게 시작해야 하는가?

### 패턴

**먼저 단일 원소에 대해 동작하는 코드를 작성한다. 그 다음, 컬렉션에 대해 동작하도록 확장한다. 단수(singular)에서 시작하여 복수(plural)로 진화시킨다.**

### 설명

One to Many는 점진적 일반화의 전략이다. 컬렉션을 처리하는 코드는 항상 단일 원소를 처리하는 코드보다 복잡하다. 따라서 **단일 원소를 올바르게 처리하는 것**을 먼저 확인하고, 그 다음에 여러 원소로 확장한다.

### 예시: 합계 계산

"숫자 리스트의 합계를 구하는 함수"를 TDD로 구현한다고 하자.

**Step 1**: 단일 원소에 대한 테스트

```java
// 하나의 숫자에 대한 합계
public void testSumSingle() {
    assertEquals(5, sum(5));
}
```

```java
// 가장 단순한 구현
int sum(int value) {
    return value;
}
// Green!
```

**Step 2**: 두 개의 원소에 대한 테스트

```java
// 두 숫자의 합계
public void testSumTwo() {
    assertEquals(7, sum(3, 4));
}
```

```java
// 구현 변경 — 가변 인자 도입
int sum(int... values) {
    int result = 0;
    for (int value : values) {
        result += value;
    }
    return result;
}
// Green!
```

**Step 3**: 컬렉션에 대한 테스트

```java
// 리스트로 받기
public void testSumList() {
    List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);
    assertEquals(15, sum(numbers));
}
```

### Part I에서의 적용

Part I에서 Kent Beck은 One to Many를 여러 곳에서 사용했다. 예를 들어, `Expression`에서 더하기를 구현할 때:

1. 먼저 **단일 Money 객체의 reduce** (통화 변환)를 구현
2. 그 다음 **Sum 객체(두 Money의 합)의 reduce**를 구현
3. 최종적으로 **임의의 Expression 트리의 reduce**를 구현

```java
// Step 1: 단일 Money의 reduce
Money reduced = bank.reduce(Money.dollar(1), "USD");
assertEquals(Money.dollar(1), reduced);

// Step 2: 두 Money의 합(Sum)의 reduce
Expression sum = new Sum(Money.dollar(3), Money.dollar(4));
Money reduced = bank.reduce(sum, "USD");
assertEquals(Money.dollar(7), reduced);

// Step 3: 다중 통화의 합
Expression sum = Money.dollar(5).plus(Money.franc(10));
Money reduced = bank.reduce(sum, "USD");
assertEquals(Money.dollar(10), reduced);
```

### One to Many의 단계별 전략

```
1. 단일 원소 → 하드코딩 또는 단순 반환
   sum(5) → return 5

2. 두 개의 원소 → 기본 연산
   sum(3, 4) → return a + b

3. N개의 원소 → 루프 또는 재귀
   sum(1,2,3,4,5) → for 루프로 합산

4. 컬렉션 → 컬렉션 API 활용
   sum(List<Integer>) → list.stream().mapToInt(...).sum()
```

이 과정에서 **각 단계는 이전 단계의 테스트를 깨뜨리지 않으면서** 진행된다. 이것이 One to Many의 안전함이다.

> **핵심 통찰**: One to Many는 "간단한 것부터"라는 TDD 원칙을 데이터 구조에 적용한 것이다. 컬렉션을 처리하는 코드에서 가장 흔한 버그는 "빈 컬렉션", "원소 하나", "원소 둘" 같은 경계 조건에서 발생한다. One to Many로 접근하면 이런 경계 조건을 자연스럽게 커버할 수 있다.

---

## 6. 네 가지 Green Bar 전략 비교

### 언제 어떤 전략을 사용하는가?

| 전략 | 확신 수준 | 코드 복잡도 | 접근법 |
|------|----------|-----------|--------|
| **Fake It** | 낮음 | 높음 | 상수 → 변수 치환으로 점진적 일반화 |
| **Triangulation** | 낮음 | 높음 | 두 번째 테스트로 일반화 강제 |
| **Obvious Implementation** | 높음 | 낮음 | 바로 올바른 구현 작성 |
| **One to Many** | 중간 | 컬렉션 관련 | 단수에서 복수로 확장 |

### 전략 선택 플로차트

```
테스트가 실패한다 (Red Bar)
    │
    ├─ 올바른 구현이 즉시 떠오르는가?
    │    ├─ Yes → Obvious Implementation 사용
    │    │        ├─ 테스트 통과 → 완료!
    │    │        └─ 테스트 실패 → Fake It으로 전환
    │    │
    │    └─ No → 어떤 종류의 불확실성인가?
    │         ├─ "어떻게 구현해야 할지 모르겠다"
    │         │    → Fake It 사용 (상수 → 중복 제거 → 일반화)
    │         │
    │         ├─ "어떤 추상화가 올바른지 모르겠다"
    │         │    → Triangulation 사용 (두 번째 테스트 추가)
    │         │
    │         └─ "컬렉션을 다뤄야 하는데 복잡하다"
    │              → One to Many 사용 (단수 → 복수)
    │
    └─ 어떤 전략을 사용하든, Red Bar가 계속되면?
         → 한 단계 더 작은 전략으로 전환
```

### 전략 간 전환의 실제 예

```java
// 1. Obvious Implementation 시도
Dollar times(int multiplier) {
    return new Dollar(amount * multiplier);
}
// → Green! 성공. 끝.

// 만약 실패했다면...

// 2. Fake It으로 전환
Dollar times(int multiplier) {
    return new Dollar(10);  // 상수
}
// → Green. 이제 중복 제거:
Dollar times(int multiplier) {
    return new Dollar(amount * multiplier);
}
// → 여전히 Green. 일반화 완료.

// 만약 일반화 방향이 불확실했다면...

// 3. Triangulation으로 전환
// 테스트 추가: assertEquals(new Dollar(15), five.times(3))
// → 두 테스트를 모두 통과시키려면 amount * multiplier가 필수
```

### Part I과 Part II에서의 전략 사용 빈도

| 전략 | Part I (Money 예제) | Part II (xUnit 예제) |
|------|--------------------|--------------------|
| Fake It | Chapter 1 (`amount = 10`), Chapter 3 (`return true`) | Chapter 18 (하드코딩된 테스트 결과) |
| Triangulation | Chapter 3 (`$5==$5`, `$5!=$6`) | 명시적으로는 적게 사용 |
| Obvious Implementation | Chapter 2 (`new Dollar(amount * multiplier)`) | Chapter 18~23 전반에서 빈번히 사용 |
| One to Many | Chapter 12~16 (단일 Money → Sum → Expression 트리) | Chapter 23 (단일 TestCase → TestSuite) |

---

## 7. 패턴 간의 관계

```
Red Bar (테스트 실패)
    │
    ├─ Fake It ──┐
    │            │──→ Green Bar (테스트 통과) ──→ Refactor (중복 제거)
    ├─ Triangulation ─┤
    │            │
    ├─ Obvious Implementation ─┘
    │
    └─ One to Many
         └─ 내부적으로 Fake It, Triangulation,
            Obvious Implementation을 활용
```

네 패턴은 배타적이 아니라 **보완적**이다:

- One to Many 과정에서 각 단계에 Fake It이나 Obvious Implementation을 사용할 수 있다
- Fake It으로 시작했다가 Triangulation으로 일반화할 수 있다
- Obvious Implementation이 실패하면 Fake It으로 돌아갈 수 있다

Kent Beck이 강조하는 것은 **유연한 전환**이다. 하나의 전략에 고집하지 않고, 상황에 맞게 전략을 바꿀 수 있는 것이 숙련된 TDD 실천자의 특징이다.

---

## 요약

- **Fake It ('Til You Make It)**: 상수를 반환하여 Green Bar를 얻고, 리팩토링(중복 제거)을 통해 일반적인 구현으로 진화시킨다. 구현 방법이 불확실할 때 사용하며, Part I Chapter 1에서 `amount = 10`이 대표적 사례다.
- **Triangulation**: 두 번째 테스트를 추가하여 Fake It의 가짜 구현을 깨뜨리고, 일반화를 강제한다. 올바른 추상화가 불분명할 때 사용하며, Part I Chapter 3의 `equals()` 구현이 대표적 사례다.
- **Obvious Implementation**: 올바른 구현이 명백하면 바로 작성한다. 확신이 있을 때 사용하며, 연속 실패 시 Fake It으로 전환해야 한다는 규율이 동반된다.
- **One to Many**: 단일 원소에 대해 먼저 동작하는 코드를 만들고, 컬렉션으로 확장한다. 경계 조건(빈 컬렉션, 원소 하나 등)을 자연스럽게 커버하게 된다.
- 네 가지 전략은 **배타적이 아니라 보완적**이다. 상황에 맞게 유연하게 전환하는 것이 숙련된 TDD의 핵심이다.

---

## 다른 챕터와의 관계

- **Chapter 1 (Multi-Currency Money)**: Fake It 패턴이 최초로 사용된 챕터. `amount = 10`에서 시작하여 `amount *= multiplier`로 진화하는 과정을 보여준다.
- **Chapter 2 (Degenerate Objects)**: Obvious Implementation 패턴이 사용된 챕터. `new Dollar(amount * multiplier)`를 바로 작성했다.
- **Chapter 3 (Equality for All)**: Triangulation 패턴이 사용된 챕터. `return true`에서 `return amount == dollar.amount`로 삼각측량을 통해 일반화했다.
- **Chapter 12-16 (Addition ~ Abstraction)**: One to Many 패턴이 대규모로 적용된 구간. 단일 Money → Sum → Expression 트리로 점진적 확장이 이루어졌다.
- **Chapter 23 (How Suite It Is)**: Part II에서 One to Many의 사례. 단일 TestCase를 실행하는 코드에서 TestSuite(여러 TestCase의 컬렉션)를 실행하는 코드로 확장했다.
- **Chapter 26 (Red Bar Patterns)**: Red Bar를 어떻게 만드느냐가 이 챕터와 직결된다. 좋은 Red Bar(적절한 난이도의 실패하는 테스트)가 있어야 Green Bar 전략이 효과적이다.
- **Chapter 25 (TDD Patterns)**: Test Data와 Evident Data 패턴이 Fake It에서 특히 중요하다. Fake It에서 사용하는 상수가 테스트의 데이터와 명백한 관계를 가져야 중복 제거가 수월해진다.
