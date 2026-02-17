# Chapter 17: Money Retrospective (Money 회고)

## 핵심 질문

Part I의 17개 챕터를 통해 무엇을 만들었는가? TDD 과정에서 어떤 교훈을 얻었는가? 처음부터 설계했다면 결과가 달랐을까? 그리고 아직 남은 것은 무엇인가?

---

## 1. 우리가 만든 것: 다중 통화 산술 시스템

### 1.1 최종 시스템 개요

17개 챕터에 걸쳐 다음과 같은 시스템을 TDD로 구현했다:

```
Expression (interface)
├── Money (단일 통화 금액)
└── Sum (두 Expression의 합)

Bank (환율 관리 및 표현식 환산)
└── Pair (환율 조회 키, 내부 클래스)
```

이 시스템은 다음을 지원한다:

- **다중 통화**: USD, CHF 등 어떤 통화든 표현 가능
- **산술 연산**: 덧셈(plus), 곱셈(times)
- **혼합 통화 계산**: `$5 + 10 CHF = $10` (환율 적용)
- **환율 관리**: 환율 등록, 조회, 변환
- **표현식 트리**: 복잡한 산술 표현식을 트리로 표현하고 평가

### 1.2 코드 지표

Kent Beck은 최종 코드의 지표를 다음과 같이 제시한다:

| 지표 | 값 |
|------|-----|
| 프로덕션 코드 줄 수 | 약 50줄 |
| 테스트 코드 줄 수 | 약 75줄 |
| 테스트 수 | 약 15개 |
| 클래스 수 | 5개 (Money, Sum, Bank, Pair, Expression) |
| 테스트-코드 비율 | 약 1.5:1 |

> **핵심 통찰**: 테스트 코드가 프로덕션 코드보다 많다. 이것은 TDD 프로젝트에서 일반적인 현상이다. Kent Beck은 이것을 문제로 보지 않는다 — 테스트는 코드의 동작을 문서화하고, 변경의 안전망을 제공하며, 설계를 이끌어내는 자산이다.

---

## 2. 설계 회고: Expression 메타포

### 2.1 Expression이라는 핵심 메타포

Part I의 가장 중요한 설계 결정은 **금융 계산을 산술 표현식(Expression)으로 모델링**한 것이다.

```
$5 + 10 CHF
```

이것은 단순히 "숫자 두 개를 더하는 것"이 아니다. 서로 다른 통화의 금액은 환율이 적용되기 전까지는 합칠 수 없다. 따라서 `$5 + 10 CHF`는 **아직 평가되지 않은 표현식** — 즉, "나중에 환율이 주어지면 계산될 수 있는 것"이다.

이 메타포를 통해:
- `$5`는 리터럴(literal) — `Money` 객체
- `$5 + 10 CHF`는 합(sum) — `Sum` 객체
- `bank.reduce(expression, "USD")`는 평가(evaluation) — 특정 환율로 표현식을 계산

### 2.2 Expression 메타포의 장점

| 장점 | 설명 |
|------|------|
| **지연 평가(Lazy Evaluation)** | 표현식을 만드는 시점과 평가하는 시점이 분리된다. 같은 표현식을 다른 환율로 평가할 수 있다. |
| **합성 가능성(Composability)** | Expression은 다른 Expression과 결합할 수 있다. `(a + b).times(2).plus(c)` 같은 복잡한 표현식이 자연스럽게 표현된다. |
| **확장 가능성(Extensibility)** | 새로운 Expression 타입(곱, 차 등)을 쉽게 추가할 수 있다. |
| **테스트 용이성(Testability)** | 표현식 생성과 평가를 독립적으로 테스트할 수 있다. |

### 2.3 Expression 메타포의 한계

Kent Beck은 이 메타포가 완벽하지 않다는 것을 인정한다:

- **나눗셈**: `$10 / 2`는 구현되지 않았다. Sum과 유사한 `Division` 클래스를 만들 수 있겠지만, 통화 간 나눗셈(`$10 / 5 CHF`)의 의미가 불분명하다.
- **뺄셈**: `$10 - $3`도 구현되지 않았다. 음수 금액의 의미를 고려해야 한다.
- **반올림**: 정수 나눗셈만 사용하고 있어 실제 금융 계산에는 부적합하다.

---

## 3. 사용된 설계 패턴 회고

### 3.1 값 객체 (Value Object)

Money는 전형적인 값 객체다:
- 생성 후 변경 불가능 (immutable)
- 값이 같으면 동등 (value-based equality)
- 연산이 새 객체를 반환 (side-effect free)

Chapter 2에서 `times()`가 자신을 변경하는 대신 새 Dollar를 반환하도록 바꾼 것이 출발점이었다. 이 결정이 이후 모든 설계에 영향을 미쳤다.

### 3.2 Composite 패턴

Expression 트리는 Composite 패턴의 적용이다:
- `Money` — Leaf (단말 노드)
- `Sum` — Composite (합성 노드)
- `Expression` — Component (공통 인터페이스)

클라이언트(Bank)는 Money인지 Sum인지 구분하지 않고 `Expression`으로 다룬다. `reduce()`, `plus()`, `times()` 모두 다형적으로 동작한다.

### 3.3 팩토리 메서드 (Factory Method)

`Money.dollar(5)`, `Money.franc(10)`은 팩토리 메서드다. 원래 Dollar와 Franc이 별도 클래스였을 때 이 메서드들이 생겼고, 두 클래스를 Money로 통합한 후에도 유지되었다. 통화 문자열을 직접 사용하는 것보다 의도가 명확하다.

### 3.4 Imposter (사칭자) 패턴

Sum은 Money의 "사칭자(imposter)"라고 볼 수 있다. Money처럼 `plus()`, `times()`, `reduce()`를 지원하지만, 내부 구조는 완전히 다르다. Expression 인터페이스를 통해 다형성을 달성한다.

---

## 4. TDD 과정 회고

### 4.1 얼마나 작은 단계였는가?

Kent Beck이 Part I에서 취한 단계의 크기를 돌아보면:

**매우 작은 단계:**
- Chapter 1: `amount = 10` 하드코딩으로 첫 테스트 통과 (Fake It)
- Chapter 3: `return true`로 equals 통과 후 점진적 일반화
- Chapter 6: Dollar와 Franc의 equals를 상위 클래스로 올리기

**비교적 큰 단계:**
- Chapter 11: Dollar/Franc 서브클래스 제거
- Chapter 12: Sum과 Expression 인터페이스 한꺼번에 도입
- Chapter 14: Pair 클래스와 해시테이블 한 번에 구현

Kent Beck은 자신감이 있을 때는 큰 단계를, 불확실할 때는 작은 단계를 밟았다. 그리고 큰 단계에서 예상치 못한 Red Bar가 나오면 즉시 작은 단계로 되돌아갔다.

### 4.2 Green Bar 전략의 사용 패턴

Part I에서 사용한 세 가지 Green Bar 전략의 분포:

| 전략 | 사용 빈도 | 대표적인 사용 시점 |
|------|-----------|-------------------|
| **Fake It** | 중간 | Chapter 1(amount = 10), Chapter 3(return true) |
| **Obvious Implementation** | 높음 | Chapter 2(new Dollar(amount * multiplier)), Chapter 14(Sum.reduce) |
| **Triangulation** | 낮음 | Chapter 3(equals에서 두 번째 테스트로 일반화 유도) |

Kent Beck은 대부분의 경우 Obvious Implementation을 사용했다. 불확실할 때만 Fake It으로 전환했고, Triangulation은 가끔 사용했다.

> **핵심 통찰**: 전문가는 대부분의 경우 Obvious Implementation을 사용할 수 있다. 하지만 Red Bar가 예상치 못하게 나타날 때 Fake It으로 전환하는 **유연성**이 중요하다. 큰 단계가 실패하면 작은 단계로 돌아가는 능력 — 이것이 TDD 숙련의 핵심이다.

### 4.3 테스트 순서의 중요성

Chapter 1에서 `$5 + 10 CHF = $10`이 아닌 `$5 × 2 = $10`을 먼저 테스트한 것은 핵심적인 결정이었다. 만약 처음부터 혼합 통화 덧셈을 시도했다면:

- 한 번에 해야 할 것이 너무 많다 (Money 클래스, 두 통화, 환율, Expression 트리...)
- 어디서 실패하는지 파악하기 어렵다
- 심리적으로 압도당한다

대신 가장 작은 문제에서 시작하여 점진적으로 확장함으로써, 항상 **작동하는 코드** 위에서 다음 단계를 밟을 수 있었다.

---

## 5. 사전 설계(Upfront Design)와의 비교

### 5.1 만약 처음부터 설계했다면?

경험 많은 개발자가 사전에 설계한다면, 아마 다음과 같은 구조를 그렸을 것이다:

```
Amount (금액 + 통화)
ExchangeRateService (환율 관리)
CurrencyConverter (통화 변환)
MoneyArithmetic (산술 연산)
```

이것은 합리적인 설계지만, TDD를 통해 도출된 설계와는 다르다. TDD의 결과물은:

```
Money (금액 + 통화 + 연산)
Expression (산술 표현식 추상화)
Sum (합산 표현식)
Bank (환율 + 표현식 평가)
```

### 5.2 두 설계의 차이

| 측면 | 사전 설계 | TDD 설계 |
|------|-----------|----------|
| **핵심 추상화** | Amount, Service | Expression, Money |
| **환율 변환** | 별도 서비스 | Bank.reduce() 안에 통합 |
| **산술 연산** | 유틸리티 메서드 | 다형적 Expression 트리 |
| **확장성** | 새 서비스 클래스 추가 | 새 Expression 구현 추가 |
| **검증** | 설계 후 구현하면서 검증 | 매 단계마다 테스트로 검증 |

Kent Beck은 TDD로 도출된 설계가 반드시 "더 좋다"고 주장하지는 않는다. 다만 TDD 설계는 **모든 것이 테스트로 검증되었다**는 확신을 제공한다. 사전 설계는 아름다울 수 있지만, 실제로 동작하는지는 구현해 봐야 안다.

> **핵심 통찰**: TDD는 "설계를 하지 않는 것"이 아니다. **설계를 다른 방식으로 하는 것**이다. 사전에 추상적으로 설계하는 대신, 테스트를 통해 **구체적인 예제에서 추상화를 도출**한다. 두 접근법 모두 장단점이 있으며, 실무에서는 둘을 적절히 조합하는 것이 효과적이다.

---

## 6. 아직 남은 것들

### 6.1 구현되지 않은 기능

Part I의 Money 시스템에는 실제 금융 시스템으로 사용하기에는 빠진 것이 많다:

| 기능 | 상태 | 설명 |
|------|------|------|
| 뺄셈 (minus) | 미구현 | `$10 - $3 = $7` |
| 나눗셈 (divide) | 미구현 | `$10 / 2 = $5` |
| 반올림 (rounding) | 미구현 | 정수 나눗셈만 사용 중 |
| Bank 영속성 | 미구현 | 환율이 메모리에만 존재 |
| Pair.hashCode() | 성능 미흡 | 항상 0을 반환 |
| 양방향 환율 | 미구현 | CHF→USD만 등록하면 USD→CHF 자동 계산 안 됨 |

### 6.2 이것들을 구현하지 않은 이유

Kent Beck은 이것들을 의도적으로 구현하지 않았다. TDD에서는 **테스트가 요구하지 않는 코드는 작성하지 않는다.** 뺄셈이 필요한 테스트가 없으므로 뺄셈을 구현하지 않은 것이다.

이것은 YAGNI(You Aren't Gonna Need It) 원칙의 적용이다. 미래에 필요할 것 같은 기능을 미리 구현하는 것은:
- 불필요한 코드를 만들 수 있고
- 실제로 필요할 때의 요구사항과 다를 수 있으며
- 유지보수 부담을 증가시킨다

---

## 7. Part I에서 배운 TDD의 핵심 교훈

### 7.1 리듬의 중요성

TDD는 **Red → Green → Refactor**의 리듬이다. 이 리듬이 주는 것:

- **안전감**: 항상 Green Bar(동작하는 코드) 위에서 작업한다
- **집중**: 한 번에 하나의 작은 문제만 해결한다
- **피드백**: 매 몇 분마다 "지금까지 괜찮은가?"에 대한 답을 얻는다

### 7.2 TODO 리스트는 나침반이다

17개 챕터를 관통하는 TODO 리스트는:
- 다음에 무엇을 할지 알려주는 **로드맵**이었다
- 머릿속의 아이디어를 꺼내놓는 **외부 메모리**였다
- 진행 상황을 확인할 수 있는 **진척도 지표**였다

### 7.3 작은 단계의 힘

$5 + 10 CHF = $10이라는 문제를 해결하기 위해 17개 챕터가 필요했다. 하지만 각 챕터에서는 하나의 작은 문제만 풀었고, 각 문제의 해결은 대부분 몇 줄의 코드 변경이었다. **큰 문제를 작은 문제의 연쇄로 바꾸는 것** — 이것이 TDD의 본질이다.

### 7.4 테스트는 문서다

15개의 테스트 메서드 이름을 읽는 것만으로도 시스템이 무엇을 하는지 알 수 있다:

```
testMultiplication         → Money는 곱할 수 있다
testEquality               → 같은 값의 Money는 동등하다
testCurrency               → Money는 통화를 가진다
testSimpleAddition         → 같은 통화의 Money를 더할 수 있다
testReduceSum              → Sum을 특정 통화로 환산할 수 있다
testReduceMoney            → Money를 특정 통화로 환산할 수 있다
testReduceMoneyDifferentCurrency → 다른 통화의 Money를 변환할 수 있다
testIdentityRate           → 같은 통화의 환율은 1이다
testMixedAddition          → 다른 통화의 Money를 더할 수 있다
testSumPlusMoney           → Sum에 Money를 더할 수 있다
testSumTimes               → Sum에 배수를 곱할 수 있다
```

이것이 **실행 가능한 명세서(executable specification)** 다.

> **핵심 통찰**: 좋은 테스트 이름은 시스템의 행동을 문서화한다. 코드가 변경되면 테스트도 함께 변경되므로, 이 문서는 항상 최신 상태를 유지한다. 주석이나 문서는 코드와 동기화되지 않을 수 있지만, 테스트는 실행할 때마다 자동으로 검증된다.

---

## 8. Part II와 Part III로의 연결

### 8.1 Part II: xUnit 예제 (Chapter 18~24)

Part I에서는 **기존 테스트 프레임워크(JUnit)를 사용**하여 TDD를 했다. Part II에서는 한 발 더 나아가 **테스트 프레임워크 자체를 TDD로 만든다.** Python을 사용하며, "테스트로 테스트를 만드는" 부트스트래핑이 핵심이다.

Part I에서 배운 TDD 리듬을 다른 언어, 다른 도메인에 적용하는 연습이다.

### 8.2 Part III: TDD 패턴 (Chapter 25~32)

Part I과 II에서 **암묵적으로 사용한 기법들**을 Part III에서 **명시적인 패턴으로 정리**한다:

- Chapter 25: TDD 패턴 — 어떤 테스트를 먼저 작성할 것인가?
- Chapter 26: Red Bar 패턴 — 실패하는 테스트를 어떻게 잘 작성하는가?
- Chapter 27: Testing 패턴 — 테스트를 어떻게 구성하는가?
- Chapter 28: Green Bar 패턴 — Fake It, Triangulation, Obvious Implementation의 체계적 정리
- Chapter 30: Design 패턴 — Value Object, Composite 등 TDD에서 자주 등장하는 설계 패턴

Part I에서 직관적으로 사용했던 것들이 Part III에서 이름과 구조를 얻는다.

---

## 요약

- Part I에서 17개 챕터에 걸쳐 **다중 통화 산술 시스템**을 TDD로 구현했다.
- 최종 코드는 약 **50줄의 프로덕션 코드**와 **75줄의 테스트 코드**, **15개의 테스트**로 구성된다.
- **Expression 메타포**가 핵심 설계 결정이었다. 금융 계산을 산술 표현식 트리로 모델링하여, 합성 가능하고 확장 가능한 구조를 만들었다.
- 사용된 주요 설계 패턴: **Value Object, Composite, Factory Method, Imposter**.
- TDD의 세 가지 Green Bar 전략(Fake It, Obvious Implementation, Triangulation) 중 **Obvious Implementation이 가장 자주** 사용되었고, 불확실할 때 Fake It으로 전환했다.
- **사전 설계와 TDD 설계**는 다른 결과를 낳을 수 있다. TDD 설계의 강점은 모든 것이 테스트로 검증되었다는 확신이다.
- 아직 **뺄셈, 나눗셈, 반올림, 영속성** 등이 구현되지 않았지만, 이는 YAGNI 원칙에 따라 의도적으로 미구현한 것이다.
- **TODO 리스트**는 17개 챕터를 관통하는 나침반 역할을 했다.
- **테스트는 실행 가능한 명세서**다. 테스트 이름만 읽어도 시스템의 행동을 파악할 수 있다.

---

## 다른 챕터와의 관계

- **Chapter 1 (Multi-Currency Money)**: Part I의 시작점. `$5 × 2 = $10`이라는 첫 번째 테스트에서 출발하여 여기까지 도달했다.
- **Chapter 15 (Mixed Currencies)**: `$5 + 10 CHF = $10` — Part I의 핵심 목표를 달성한 챕터. 이 회고의 가장 중요한 이정표다.
- **Chapter 16 (Abstraction, Finally)**: Expression 인터페이스를 완성한 챕터. Expression 메타포의 최종 형태를 보여준다.
- **Chapter 18 (First Steps to xUnit)**: Part II의 시작. Part I에서 배운 TDD를 테스트 프레임워크 구현에 적용한다.
- **Chapter 25~28 (TDD/Red Bar/Testing/Green Bar Patterns)**: Part I에서 암묵적으로 사용한 TDD 기법들이 Part III에서 명시적인 패턴으로 정리된다.
- **Chapter 32 (Mastering TDD)**: TDD를 마스터하기 위한 실천적 조언. Part I의 경험을 바탕으로 한 Kent Beck의 철학이 담겨 있다.
