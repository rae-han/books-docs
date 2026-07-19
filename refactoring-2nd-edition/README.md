# Refactoring: Improving the Design of Existing Code (2nd Edition)

> *Refactoring: Improving the Design of Existing Code* (2nd Edition, Martin Fowler, Addison-Wesley, 2018)
> 한국어판: 『리팩터링 2판 — 코드 구조를 체계적으로 개선하여 효율적인 리팩터링 구현하기』 (마틴 파울러 지음, 개앞맵시·남기혁 옮김, 한빛미디어)

리팩터링의 고전. **겉보기 동작을 보존한 채 내부 구조를 개선하는** 작은 단계들의 기법을 정의하고, 코드에서 나는 **악취(bad smells)**를 감지해 **카탈로그의 기법**으로 치유하는 법을 다룬다. 2판은 예제를 **JavaScript**로 새로 썼다.

- **코드 예제**: 원서 JavaScript를 `<details>`로 접어 두고 **TypeScript 변환본**을 펼쳐 병기한다.
- **서사형 챕터(Ch1~5)**: `핵심 질문` → 번호 섹션 → `핵심 통찰` → `요약`.
- **카탈로그 챕터(Ch6~12)**: 각 기법을 **스케치 · 배경(Motivation) · 절차(Mechanics)** 틀로 서술하고, 말미에 카탈로그 절 번호로 연결.
- **인용 처리**: 파울러의 원칙 강조는 `> **핵심 통찰**:`, 켄트 벡·제시카 커 등 외부 인용은 레이블 없는 `>`.

카탈로그편(Ch6~12)에서 다루는 리팩터링은 **총 66가지**다.

---

## 전체 목차

### 원칙편 (Ch1~5) — 서사·개념형

| Ch | 제목 | 파일 | 상태 |
|---|---|---|---|
| 1 | **Refactoring: A First Example (리팩터링: 첫 번째 예시)** | [ch01-refactoring-a-first-example.md](ch01-refactoring-a-first-example.md) | ✅ |
| 2 | **Principles in Refactoring (리팩터링 원칙)** | [ch02-principles-in-refactoring.md](ch02-principles-in-refactoring.md) | ✅ |
| 3 | **Bad Smells in Code (코드에서 나는 악취)** | [ch03-bad-smells-in-code.md](ch03-bad-smells-in-code.md) | ✅ |
| 4 | **Building Tests (테스트 구축하기)** | [ch04-building-tests.md](ch04-building-tests.md) | ✅ |
| 5 | **Introducing the Catalog (리팩터링 카탈로그 보는 법)** | [ch05-introducing-the-catalog.md](ch05-introducing-the-catalog.md) | ✅ |

### 카탈로그편 (Ch6~12) — 기법 카탈로그

| Ch | 제목 | 기법 수 | 파일 | 상태 |
|---|---|---|---|---|
| 6 | **A First Set of Refactorings (기본적인 리팩터링)** | 11 | [ch06-a-first-set-of-refactorings.md](ch06-a-first-set-of-refactorings.md) | ✅ |
| 7 | **Encapsulation (캡슐화)** | 9 | [ch07-encapsulation.md](ch07-encapsulation.md) | ✅ |
| 8 | **Moving Features (기능 이동)** | 9 | [ch08-moving-features.md](ch08-moving-features.md) | ✅ |
| 9 | **Organizing Data (데이터 조직화)** | 6 | [ch09-organizing-data.md](ch09-organizing-data.md) | ✅ |
| 10 | **Simplifying Conditional Logic (조건부 로직 간소화)** | 7 | [ch10-simplifying-conditional-logic.md](ch10-simplifying-conditional-logic.md) | ✅ |
| 11 | **Refactoring APIs (API 리팩터링)** | 13 | [ch11-refactoring-apis.md](ch11-refactoring-apis.md) | ✅ |
| 12 | **Dealing with Inheritance (상속 다루기)** | 11 | [ch12-dealing-with-inheritance.md](ch12-dealing-with-inheritance.md) | ✅ |

### 부록

| 부록 | 제목 | 파일 | 상태 |
|---|---|---|---|
| A | **리팩터링 목록 (List of Refactorings)** | [appendix-a-list-of-refactorings.md](appendix-a-list-of-refactorings.md) | ✅ |
| B | **악취 제거 기법 (Smells to Refactorings)** | [appendix-b-smells-to-refactorings.md](appendix-b-smells-to-refactorings.md) | ✅ |

> ✅ = 작성 완료. **전 장(Ch1~12) + 부록 A·B 완성** — 리팩터링 기법 66가지를 모두 다룬다.

## 인용문

전 책 통합 모음은 [루트 QUOTES.md](../QUOTES.md) 참조.

> 컴퓨터가 이해하는 코드는 바보도 작성할 수 있다. 사람이 이해하도록 작성하는 프로그래머가 진정한 실력자다.<br>— 마틴 파울러 (Ch1 리팩터링: 첫 번째 예시)
