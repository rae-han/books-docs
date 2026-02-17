# Test-Driven Development: By Example (테스트 주도 개발)

**저자**: Kent Beck
**출판**: 2002, Addison-Wesley Professional
**한국어판**: 테스트 주도 개발, 인사이트(Insight) 출판

---

## 책 소개

"Test-Driven Development: By Example"은 TDD(테스트 주도 개발)의 창시자 Kent Beck이 TDD의 철학과 실천법을 직접 시연하는 책이다. 이 책의 독특한 점은 **이론을 설명하는 것이 아니라, 실제 코딩 세션을 통해 TDD를 체험하게 만드는 구조**라는 것이다.

> **TDD의 두 가지 단순한 규칙:**
> 1. 자동화된 테스트가 실패할 때만 새 코드를 작성한다.
> 2. 중복을 제거한다.

이 두 규칙에서 TDD의 모든 실천법이 파생된다. Red(실패하는 테스트 작성) → Green(최소한의 코드로 테스트 통과) → Refactor(중복 제거 및 설계 개선)의 리듬이 이 책 전체를 관통한다.

### 이 책의 특징

- **시연 중심(By Example)**: Part I과 Part II는 각각 하나의 완전한 프로젝트를 TDD로 처음부터 끝까지 구현하는 과정을 보여준다. 독자는 Kent Beck의 사고 과정을 실시간으로 따라갈 수 있다.
- **TODO 리스트**: Kent Beck은 각 챕터에서 해야 할 일(TODO)과 완료한 일을 명시적으로 추적한다. 이것은 TDD의 핵심 습관 중 하나다.
- **의도적으로 작은 단계**: 때로는 놀라울 정도로 작은 단계로 진행한다. 이것이 TDD의 리듬이다 — 자신감이 있을 때는 큰 단계로, 불확실할 때는 작은 단계로 진행한다.
- **실용적 패턴**: Part III에서는 TDD를 실무에 적용하기 위한 구체적인 패턴들을 정리한다.

---

## 이 저장소의 목적

이 저장소는 "Test-Driven Development: By Example"의 내용을 챕터별로 상세하게 정리한 학습 자료이다. 각 챕터의 TDD 사이클, 코드 변화 과정, 설계 결정을 책을 대체할 수 있을 정도로 충실하게 담고 있으며, 다음과 같은 용도로 활용할 수 있다:

- TDD를 처음 배우는 개발자를 위한 단계별 학습 가이드
- TDD의 사고 과정과 리듬을 체험하는 실습 자료
- 팀 내 TDD 도입을 위한 스터디 교재

---

## 목차

### Part I: The Money Example (다중 통화 예제)

Part I은 다중 통화를 지원하는 Money 객체를 TDD로 구현하는 과정을 17개 챕터에 걸쳐 보여준다. Java를 사용하며, 점진적으로 설계가 진화하는 모습을 관찰할 수 있다.

- [Chapter 1: Multi-Currency Money (다중 통화 Money)](ch01-multi-currency-money.md)
- [Chapter 2: Degenerate Objects (퇴화 객체)](ch02-degenerate-objects.md)
- [Chapter 3: Equality for All (모두를 위한 동등성)](ch03-equality-for-all.md)
- [Chapter 4: Privacy (프라이버시)](ch04-privacy.md)
- [Chapter 5: Franc-ly Speaking (프랑에 대해 말하자면)](ch05-franc-ly-speaking.md)
- [Chapter 6: Equality for All, Redux (동등성 재검토)](ch06-equality-for-all-redux.md)
- [Chapter 7: Apples and Oranges (사과와 오렌지)](ch07-apples-and-oranges.md)
- [Chapter 8: Makin' Objects (객체 만들기)](ch08-makin-objects.md)
- [Chapter 9: Times We're Livin' In (우리가 사는 시대)](ch09-times-were-livin-in.md)
- [Chapter 10: Interesting Times (흥미로운 시간들)](ch10-interesting-times.md)
- [Chapter 11: The Root of All Evil (모든 악의 근원)](ch11-the-root-of-all-evil.md)
- [Chapter 12: Addition, Finally (드디어 더하기)](ch12-addition-finally.md)
- [Chapter 13: Make It (만들어 보자)](ch13-make-it.md)
- [Chapter 14: Change (변경)](ch14-change.md)
- [Chapter 15: Mixed Currencies (혼합 통화)](ch15-mixed-currencies.md)
- [Chapter 16: Abstraction, Finally (드디어 추상화)](ch16-abstraction-finally.md)
- [Chapter 17: Money Retrospective (Money 회고)](ch17-money-retrospective.md)

### Part II: The xUnit Example (xUnit 예제)

Part II는 TDD를 사용하여 테스트 프레임워크 자체를 구현한다. Python을 사용하며, "테스트로 테스트를 만드는" 부트스트래핑 과정이 핵심이다.

- [Chapter 18: First Steps to xUnit (xUnit의 첫 걸음)](ch18-first-steps-to-xunit.md)
- [Chapter 19: Set the Table (테이블 차리기)](ch19-set-the-table.md)
- [Chapter 20: Cleaning Up After (뒷정리)](ch20-cleaning-up-after.md)
- [Chapter 21: Counting (세기)](ch21-counting.md)
- [Chapter 22: Dealing with Failure (실패 다루기)](ch22-dealing-with-failure.md)
- [Chapter 23: How Suite It Is (스위트의 멋)](ch23-how-suite-it-is.md)
- [Chapter 24: xUnit Retrospective (xUnit 회고)](ch24-xunit-retrospective.md)

### Part III: Patterns for Test-Driven Development (TDD 패턴)

Part III는 Part I, II에서 사용한 기법들을 패턴으로 정리한다. TDD를 실무에 적용하기 위한 실질적인 가이드다.

- Chapter 25: Test-Driven Development Patterns (TDD 패턴)
- Chapter 26: Red Bar Patterns (Red Bar 패턴)
- Chapter 27: Testing Patterns (테스팅 패턴)
- Chapter 28: Green Bar Patterns (Green Bar 패턴)
- [Chapter 29: xUnit Patterns (xUnit 패턴)](ch29-xunit-patterns.md)
- [Chapter 30: Design Patterns (설계 패턴)](ch30-design-patterns.md)
- [Chapter 31: Refactoring (리팩토링)](ch31-refactoring.md)
- [Chapter 32: Mastering TDD (TDD 마스터하기)](ch32-mastering-tdd.md)

---

## 학습 가이드

### 추천 읽기 순서

이 책은 순서대로 읽는 것을 강력히 권장한다. 특히 Part I은 각 챕터가 이전 챕터의 코드 위에 쌓이기 때문에 건너뛰면 맥락을 잃게 된다.

**1단계: Money Example로 TDD 체험 (Chapter 1~17)**

TDD의 리듬을 처음 경험하는 단계이다. 첫 테스트에서 시작하여 완전한 다중 통화 시스템을 만들어가는 과정을 따라가며, Red → Green → Refactor 사이클에 익숙해진다. 특히 Chapter 1~5에서 TDD의 기본 리듬을 잡는 것이 중요하다. Chapter 17의 회고에서는 전체 과정을 돌아보며 TDD의 핵심 원칙을 정리한다.

**2단계: xUnit 구현으로 심화 (Chapter 18~24)**

Part I에서 배운 TDD를 더 어려운 문제에 적용한다. 테스트 프레임워크로 테스트 프레임워크를 만드는 "부트스트래핑"은 TDD의 힘을 실감하게 해준다. Python으로 작성되어 다른 언어에서의 TDD도 경험할 수 있다.

**3단계: 패턴으로 체계화 (Chapter 25~32)**

Part I, II에서 암묵적으로 사용한 기법들을 명시적인 패턴으로 정리한다. TDD를 실무에 적용할 때 참조할 수 있는 실용적인 가이드다. 특히 Chapter 25(TDD 패턴)와 Chapter 32(TDD 마스터하기)는 TDD 실천에 대한 Kent Beck의 철학이 담겨 있다.

---

## 핵심 개념 요약

이 책의 모든 내용은 하나의 중심 리듬으로 수렴한다:

> **Red → Green → Refactor**

1. **Red**: 실패하는 테스트를 작성한다. 아직 존재하지 않는 코드에 대한 테스트를 먼저 쓴다.
2. **Green**: 테스트를 통과시키는 **최소한의** 코드를 작성한다. 여기서 "최소한"이 핵심이다 — 아름다운 코드가 아니라 동작하는 코드를 먼저 만든다.
3. **Refactor**: 중복을 제거하고 설계를 개선한다. 테스트가 통과하는 상태를 유지하면서 코드를 깨끗하게 만든다.

이 사이클에서 Kent Beck이 강조하는 핵심 원칙들:

- **작은 단계(Small Steps)**: 자신감이 낮을 때는 아주 작은 단계로, 자신감이 높을 때는 큰 단계로 진행한다. 하지만 문제가 생기면 언제든 작은 단계로 돌아간다.
- **삼각측량(Triangulation)**: 두 개 이상의 예제가 있어야 올바른 일반화를 할 수 있다. 하나의 테스트만으로 일반적인 해결책을 만들지 않는다.
- **명백한 구현(Obvious Implementation)**: 구현이 명백할 때는 바로 작성한다. 하지만 확신이 없으면 Fake It(가짜로 만들기)부터 시작한다.
- **TODO 리스트 관리**: 떠오르는 아이디어를 즉시 TODO 리스트에 적고, 현재 작업에 집중한다. 한 번에 한 가지만 한다.

---

## TDD의 핵심 전략: Green Bar를 만드는 세 가지 방법

| 전략 | 설명 | 사용 시점 |
|------|------|----------|
| **Fake It (가짜로 만들기)** | 상수를 반환하여 테스트를 통과시키고, 점진적으로 변수로 대체 | 어떻게 구현할지 불확실할 때 |
| **Obvious Implementation (명백한 구현)** | 올바른 구현을 바로 작성 | 구현 방법이 명확할 때 |
| **Triangulation (삼각측량)** | 두 개 이상의 테스트로 일반화를 유도 | 올바른 추상화가 불분명할 때 |
