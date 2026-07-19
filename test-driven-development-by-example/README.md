# 테스트 주도 개발 (Test-Driven Development: By Example)

> *Test-Driven Development: By Example* (Kent Beck, Addison-Wesley, 2002)
> 한국어판: 『테스트 주도 개발』 (김창준·강규영 옮김, 인사이트, 2014)

TDD 창시자 켄트 벡이 TDD의 철학과 실천법을 **직접 시연**하는 책. 이론 설명이 아니라 실제 코딩 세션을 따라가며 TDD를 체험하게 만드는 구조로, **Red(실패하는 테스트) → Green(최소한의 코드로 통과) → Refactor(중복 제거)**의 리듬이 책 전체를 관통한다.

## 책 정보

| 항목 | 내용 |
|------|------|
| **저자** | 켄트 벡(Kent Beck) |
| **역자** | 김창준·강규영 |
| **출판** | 인사이트, 2014 (원서: Addison-Wesley, 2002) |
| **예제 언어** | Part I: Java (Money) / Part II: Python (xUnit) |
| **대상 독자** | TDD를 처음 배우거나, 알지만 리듬을 체득하지 못한 개발자 |

## 개요

TDD의 모든 실천법은 두 가지 단순한 규칙에서 파생된다 — ① 자동화된 테스트가 실패할 때만 새 코드를 작성한다 ② 중복을 제거한다.

Part I·II는 각각 하나의 완전한 프로젝트(다중 통화 Money, 테스트 프레임워크 xUnit)를 TDD로 처음부터 끝까지 구현하며 켄트 벡의 사고 과정을 실시간으로 보여준다. 때로는 놀라울 정도로 작은 단계로 진행하는데, 이것이 TDD의 리듬이다 — 자신감이 있으면 큰 단계로, 불확실하면 작은 단계로. 각 챕터는 **TODO 리스트**로 해야 할 일과 완료한 일을 명시적으로 추적한다. Part III는 이 기법들을 실무 적용 가능한 패턴으로 정리한다.

## 목차

### Part I: The Money Example (Ch 1-17) — 다중 통화 Money를 TDD로

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 1 | [Multi-Currency Money](ch01-multi-currency-money.md) | 첫 테스트 · TODO 리스트 · 가짜 구현 | 컴파일도 안 되는 `$5 × 2 = $10` 테스트에서 시작 — TDD의 첫 리듬 |
| 2 | [Degenerate Objects](ch02-degenerate-objects.md) | 값 객체 · 명백한 구현 | `times()`가 새 객체를 반환하게 — 부작용 제거 |
| 3 | [Equality for All](ch03-equality-for-all.md) | 동등성 · 삼각측량 | 삼각측량(예제 2개)으로 `equals()` 일반화 |
| 4 | [Privacy](ch04-privacy.md) | 캡슐화 · 테스트 의존 | amount를 private으로 — 테스트가 구현이 아닌 인터페이스에 묻게 |
| 5 | [Franc-ly Speaking](ch05-franc-ly-speaking.md) | 복사-붙여넣기 부채 | 죄를 지으며(복붙) Franc을 만들고 TODO에 부채를 기록 |
| 6 | [Equality for All, Redux](ch06-equality-for-all-redux.md) | 상위 클래스 · 중복 제거 | Money 상위 클래스로 `equals()` 끌어올리기 |
| 7 | [Apples and Oranges](ch07-apples-and-oranges.md) | 클래스 비교 | Franc ≠ Dollar — getClass 비교라는 찜찜한 임시 해법 |
| 8 | [Makin' Objects](ch08-makin-objects.md) | 팩토리 메서드 | `Money.dollar()` 팩토리로 하위 클래스의 존재를 숨기기 |
| 9 | [Times We're Livin' In](ch09-times-were-livin-in.md) | 통화 개념 | currency 도입 — 하위 클래스 제거를 향한 포석 |
| 10 | [Interesting Times](ch10-interesting-times.md) | 구현 통일 · 과감한 실험 | 두 `times()`를 동일하게 — 확인하며 전진 |
| 11 | [The Root of All Evil](ch11-the-root-of-all-evil.md) | 하위 클래스 제거 | Dollar·Franc 삭제 — Money 단일 클래스로 |
| 12 | [Addition, Finally](ch12-addition-finally.md) | Expression · Bank 은유 | `$5 + $5` — 수식(Expression)과 은행이라는 은유 도입 |
| 13 | [Make It](ch13-make-it.md) | Sum · reduce | 가짜 구현을 Sum.reduce의 진짜 구현으로 |
| 14 | [Change](ch14-change.md) | 환율 · 환전 | 2CHF → 1USD — Bank에 환율 테이블 |
| 15 | [Mixed Currencies](ch15-mixed-currencies.md) | 혼합 통화 연산 | `$5 + 10CHF` — 서로 다른 통화의 덧셈 완성 |
| 16 | [Abstraction, Finally](ch16-abstraction-finally.md) | Expression 추상화 완성 | Sum.times·plus까지 — Expression 인터페이스로 마무리 |
| 17 | [Money Retrospective](ch17-money-retrospective.md) | 회고 · 테스트 품질 · 메트릭 | Money 전체 회고 — 리듬·은유·테스트 품질 점검 |

### Part II: The xUnit Example (Ch 18-24) — 테스트 프레임워크를 TDD로

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 18 | [First Steps to xUnit](ch18-first-steps-to-xunit.md) | 부트스트래핑 · 자기 참조 | 테스트 프레임워크를 그 자신으로 테스트하는 첫 걸음 (Python) |
| 19 | [Set the Table](ch19-set-the-table.md) | setUp · 템플릿 메서드 | 테스트 전 준비 단계 — 준비(Arrange)의 자리 만들기 |
| 20 | [Cleaning Up After](ch20-cleaning-up-after.md) | tearDown · 로그 문자열 | 뒷정리 tearDown — 플래그 대신 로그 문자열로 호출 순서 검증 |
| 21 | [Counting](ch21-counting.md) | TestResult | 실행 결과 집계 — "1 run, 0 failed" |
| 22 | [Dealing with Failure](ch22-dealing-with-failure.md) | 실패 격리 · 예외 포착 | 한 테스트가 실패해도 나머지는 계속 — 예외를 잡아 결과에 기록 |
| 23 | [How Suite It Is](ch23-how-suite-it-is.md) | TestSuite · 컴포지트 패턴 | 여러 테스트를 묶어 한 번에 — Composite로 테스트 스위트 |
| 24 | [xUnit Retrospective](ch24-xunit-retrospective.md) | 회고 · 프레임워크 학습법 | xUnit 회고 — 자기 프레임워크 구현이 주는 학습 효과 |

### Part III: Patterns for Test-Driven Development (Ch 25-32) — 패턴 카탈로그

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 25 | [Test-Driven Development Patterns](ch25-test-driven-development-patterns.md) | 격리된 테스트 · TODO 리스트 · 단언 우선 | 기본 패턴 — 왜 테스트를 먼저, 어디까지 격리하나 |
| 26 | [Red Bar Patterns](ch26-red-bar-patterns.md) | 시작 테스트 · 학습 테스트 · 회귀 테스트 | 다음 테스트를 고르는 법 — 언제 어떤 테스트를 쓰나 |
| 27 | [Testing Patterns](ch27-testing-patterns.md) | 목 객체 · 자식 테스트 · 깨진 테스트 | 테스트 작성의 세부 기법 — 혼자/팀으로 코딩 마칠 때의 습관 |
| 28 | [Green Bar Patterns](ch28-green-bar-patterns.md) | 가짜로 만들기 · 삼각측량 · 명백한 구현 | 테스트를 통과시키는 세 가지 방법 |
| 29 | [xUnit Patterns](ch29-xunit-patterns.md) | 단언 · 픽스처 · 외부 픽스처 | xUnit 계열 프레임워크를 쓰는 패턴 |
| 30 | [Design Patterns](ch30-design-patterns.md) | 커맨드 · 값 객체 · 널 객체 · 임포스터 | TDD 관점에서 다시 보는 디자인 패턴 |
| 31 | [Refactoring](ch31-refactoring.md) | 차이 일치시키기 · 메서드 추출 | TDD에서의 리팩터링 — 관찰된 사실에 근거해 변경 |
| 32 | [Mastering TDD](ch32-mastering-tdd.md) | 단계 크기 · 피드백 · 열린 질문 | 얼마나 큰 단계로? 무엇을 테스트하나? — TDD 숙련의 질문들 |

## 학습 가이드

1. **Part I(Ch1~17)은 반드시 순서대로** — 각 챕터가 이전 챕터의 코드 위에 쌓이므로 건너뛰면 맥락을 잃는다. Ch1~5에서 기본 리듬을 잡는 것이 중요하고, Ch17 회고가 전체를 정리해 준다
2. **Part II(Ch18~24)로 심화** — 테스트 프레임워크로 테스트 프레임워크를 만드는 부트스트래핑. 다른 언어(Python)에서의 TDD 경험을 겸한다
3. **Part III(Ch25~32)는 레퍼런스** — 앞에서 암묵적으로 쓴 기법들의 명시적 패턴화. Ch25(기본 패턴)와 Ch32(마스터하기)에 켄트 벡의 철학이 응축되어 있다

## 핵심 개념 맵

- **Red → Green → Refactor**: 실패하는 테스트 작성 → 최소한의 코드로 통과(아름다움보다 동작 먼저) → 중복 제거. 이 리듬이 전부다
- **두 가지 규칙**: 테스트가 실패할 때만 새 코드를 쓴다 + 중복을 제거한다 — 모든 실천법의 뿌리
- **Green Bar 3전략**: 가짜로 만들기(상수 반환→점진 대체) / 명백한 구현(확신 있을 때 바로) / 삼각측량(예제 2개로 일반화 유도)
- **작은 단계**: 자신감이 낮으면 작게, 높으면 크게 — 문제가 생기면 언제든 작은 단계로 복귀
- **TODO 리스트**: 떠오르는 일을 즉시 적고 지금 일에 집중 — 한 번에 한 가지만
- **테스트는 두려움을 지루함으로 바꾼다** — TDD의 목적은 확신(자신감)의 관리다

## 시그니처 요소와 표기 규칙

- `## TDD 사이클` — Red → Green → Refactor 단계별 코드 진행
- `## TODO 리스트` — 켄트 벡 스타일 할 일 목록 추적 (완료 항목 취소선)

## Notion DB 구조

- 위치: Raehan's Must reads 하위 챕터 DB (콜아웃 마이그레이션·재업로드 완료, 전체 32파일)
