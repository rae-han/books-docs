# Unit Testing: Principles, Practices, and Patterns

**Vladimir Khorikov** 저 | Manning Publications, 2020

---

## 개요

이 책은 단위 테스트의 **"왜"와 "어떻게"**를 체계적으로 다룬다. 단순히 테스트를 작성하는 기법이 아니라, **좋은 테스트와 나쁜 테스트를 구분하는 원칙**을 제시한다. Khorikov는 좋은 단위 테스트의 네 가지 기둥(회귀 방지, 리팩터링 내성, 빠른 피드백, 유지보수성)이라는 프레임워크를 통해, 테스트의 모든 의사결정 — Mock 사용 여부, 테스트 스타일 선택, 통합 테스트 범위 등 — 을 일관된 원칙으로 평가한다.

### 핵심 메시지

- 테스트의 목표는 버그를 잡는 것이 아니라 **소프트웨어의 지속 가능한 성장**을 가능하게 하는 것이다
- **리팩터링 내성**은 타협 불가능한 기둥이다 — 구현 세부사항이 아닌 동작을 검증하라
- Mock은 **비관리 의존성**(외부 시스템이 관찰하는 의존성)에만 사용하라
- 코드를 테스트하기 어렵다면, 그것은 **설계를 개선하라**는 신호다

---

## 목차

### Part 1: 단위 테스트의 기초 (Ch 1-3)

| 챕터 | 제목 | 핵심 주제 |
|------|------|----------|
| [Chapter 1](ch01-the-goal-of-unit-testing.md) | The Goal of Unit Testing | 단위 테스트의 목표: 지속 가능한 성장, 커버리지 지표의 함정 |
| [Chapter 2](ch02-what-is-a-unit-test.md) | What is a Unit Test? | Classical vs London 학파, 단위 테스트 vs 통합 테스트 |
| [Chapter 3](ch03-the-anatomy-of-a-unit-test.md) | The Anatomy of a Unit Test | AAA 패턴, 테스트 네이밍, 매개변수화 테스트 |

### Part 2: 좋은 테스트의 기준 (Ch 4-7)

| 챕터 | 제목 | 핵심 주제 |
|------|------|----------|
| [Chapter 4](ch04-the-four-pillars-of-a-good-unit-test.md) | The Four Pillars of a Good Unit Test | 네 가지 기둥, 리팩터링 내성의 중요성, 테스트 피라미드 |
| [Chapter 5](ch05-mocks-and-test-fragility.md) | Mocks and Test Fragility | Mock vs Stub, 관찰 가능한 동작 vs 구현 세부사항, 육각형 아키텍처 |
| [Chapter 6](ch06-styles-of-unit-testing.md) | Styles of Unit Testing | 출력/상태/커뮤니케이션 기반 테스트, 함수형 아키텍처 |
| [Chapter 7](ch07-refactoring-toward-valuable-tests.md) | Refactoring Toward Valuable Tests | 코드의 네 가지 유형, 험블 객체 패턴, 도메인 이벤트 |

### Part 3: 통합 테스트 (Ch 8-10)

| 챕터 | 제목 | 핵심 주제 |
|------|------|----------|
| [Chapter 8](ch08-why-integration-testing.md) | Why Integration Testing? | 통합 테스트의 역할, 관리 vs 비관리 의존성 처리 |
| [Chapter 9](ch09-mocking-best-practices.md) | Mocking Best Practices | Mock vs Spy, 시스템 경계에 Mock 배치, CanExecute/Execute |
| [Chapter 10](ch10-testing-the-database.md) | Testing the Database | DB 형상 관리, 테스트 데이터 생명주기, ORM 주의사항 |

### Part 4: 안티패턴 (Ch 11)

| 챕터 | 제목 | 핵심 주제 |
|------|------|----------|
| [Chapter 11](ch11-unit-testing-anti-patterns.md) | Unit Testing Anti-patterns | 프라이빗 메서드 테스트, 도메인 지식 유출, 코드 오염, 시간 처리 |

---

## 핵심 프레임워크

### 좋은 단위 테스트의 네 가지 기둥

```
1. 회귀 방지 (Protection against regressions)
   → 버그를 얼마나 잘 찾아내는가?

2. 리팩터링 내성 (Resistance to refactoring)    ← 타협 불가
   → 거짓 양성을 얼마나 적게 만드는가?

3. 빠른 피드백 (Fast feedback)
   → 얼마나 빨리 실행되는가?

4. 유지보수성 (Maintainability)
   → 이해하고 수정하기 얼마나 쉬운가?
```

### Mock 사용 의사결정

```
의존성이 프로세스 외부인가?
├── 아니오 → 실제 객체 사용
└── 예 → 외부 시스템이 관찰 가능한가?
    ├── 아니오 (관리 의존성: 전용 DB) → 실제 인스턴스 사용
    └── 예 (비관리 의존성: 메시지 버스) → Mock 사용
```

### 코드 유형별 테스트 전략

```
도메인 모델/알고리즘  → 단위 테스트 (출력/상태 기반)
컨트롤러             → 통합 테스트 (핵심 경로만)
Trivial 코드        → 테스트 없음
과도하게 복잡한 코드  → 험블 객체 패턴으로 분해 후 위 전략 적용
```
