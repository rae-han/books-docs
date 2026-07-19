# 좋은 코드, 나쁜 코드 (Good Code, Bad Code: Think Like a Software Engineer)

> *Good Code, Bad Code: Think Like a Software Engineer* (Tom Long, Manning, 2021)
> 한국어판: 『좋은 코드, 나쁜 코드 — 프로그래머의 코드 품질 개선법』 (차건회 옮김, 제이펍, 2022)

구글 소프트웨어 엔지니어 톰 롱이 **높은 품질의 코드**를 만드는 구체적 원칙을 정리한 실무서. "이 코드가 미래에 어떻게 잘못될 수 있는가"를 늘 염두에 두고, 코드 품질을 **6대 핵심 요소**로 나누어 코드 수준의 실천으로 풀어낸다.

## 책 정보

| 항목 | 내용 |
|------|------|
| **저자** | 톰 롱(Tom Long) |
| **역자** | 차건회 |
| **출판** | 제이펍, 2022 (원서: Manning, 2021) |
| **예제 언어** | 언어 중립 의사코드 (노트는 TypeScript 병기) |
| **대상 독자** | "돌아가는 코드"에서 "품질 좋은 코드"로 넘어가려는 주니어~미드 개발자 |

## 개요

코드 품질의 6대 핵심 요소 — **읽기 쉬움 · 예측 가능 · 오용 방지 · 모듈화 · 재사용/일반화 · 테스트 용이** — 가 책의 뼈대다. Part 1이 이론(품질·추상화 계층·코드 계약·오류), Part 2가 요소별 실천(Ch5~9가 6대 요소와 1:1 대응), Part 3이 단위 테스트다.

이 노트는 원서의 언어 중립 **의사코드**를 `<details>`로 접고 **TypeScript 변환본**을 펼쳐 병기한다.

## 목차

### Part 1: 이론 (Ch 1-4)

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 1 | [Code Quality](ch01-code-quality.md) | 코드 품질 6대 요소 · 고품질 코드의 4가지 목표 | 품질은 취향이 아니다 — 6대 요소와 목표의 지도 |
| 2 | [Layers of Abstraction](ch02-layers-of-abstraction.md) | 추상화 계층 · 함수/클래스/인터페이스 분리 | 문제를 깔끔한 계층으로 분해하라 — 거대 클래스의 해체 |
| 3 | [Other Engineers and Code Contracts](ch03-other-engineers-and-code-contracts.md) | 코드 계약 · 세부 조항 · 체크와 어서션 | 코드는 다른 엔지니어와의 계약 — 암묵을 명시로 |
| 4 | [Errors](ch04-errors.md) | 오류 · 복구 가능성 · 명시적/암시적 전달 | 오류를 숨기지 마라 — 복구 가능성 기준의 전달 전략 |

### Part 2: 실전 (Ch 5-9) — 6대 요소별 실천

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 5 | [Make Code Readable](ch05-make-code-readable.md) | 가독성 · 명명 · 주석 | 서술적 이름과 코드 줄 수의 함정 — 읽기 쉬움의 기법 |
| 6 | [Avoid Surprises](ch06-avoid-surprises.md) | 예측 가능성 · 매직 값 · 열거형 | 놀라게 하지 마라 — 반환값·부수 효과의 기대치 관리 |
| 7 | [Make Code Hard to Misuse](ch07-make-code-hard-to-misuse.md) | 오용 방지 · 불변성 · 타입 안전 | 잘못 쓰기 어렵게 — 컴파일러가 실수를 잡게 하라 |
| 8 | [Make Code Modular](ch08-make-code-modular.md) | 모듈화 · 의존성 주입 · 인터페이스 | 변경이 국소화되는 구조 — 구현 세부에서 분리 |
| 9 | [Make Code Reusable and Generalizable](ch09-make-code-reusable-and-generalizable.md) | 재사용성 · 일반화 · 가정 최소화 | 가정을 줄일수록 재사용 가능해진다 |

### Part 3: 단위 테스트 (Ch 10-11)

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 10 | [Unit Testing Principles](ch10-unit-testing-principles.md) | 단위 테스트 원칙 · 기능 vs 구현 · 테스트 더블 | 구현이 아니라 동작을 테스트하라 |
| 11 | [Unit Testing Practices](ch11-unit-testing-practices.md) | 하나의 동작 · 공유 설정 주의 | 좋은 테스트 작성의 실제 — 각 동작을 격리해 검증 |

### 부록

| 부록 | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| A | [Chocolate Brownie Recipe](appendix-a-chocolate-brownie-recipe.md) | 가독성 비유 | Ch1의 읽기 어려운 레시피의 "읽기 쉬운 버전" |
| B | [Null Safety and Optionals](appendix-b-null-safety-and-optionals.md) | 널 안전성 · 옵셔널 | null 다루기 — 널 안전성과 옵셔널 타입 |
| C | [Additional Code Examples](appendix-c-additional-code-examples.md) | 추가 예제 | 본문 보조 예제 코드 모음 |

## 학습 가이드

1. **Part 1(Ch1~4)로 어휘부터** — 특히 Ch1의 6대 요소가 이후 모든 챕터의 평가 기준
2. **Part 2(Ch5~9)는 요소별 독립** — 지금 코드베이스에서 아픈 요소부터 골라 읽어도 된다
3. **Part 3(Ch10~11)은 세트로** — 원칙(무엇을) 다음에 실천(어떻게)
4. 각 챕터의 `코드 품질 6대 요소 연결` 절로 장 간 관계를 추적할 수 있다

## 핵심 개념 맵

- **코드 품질 6대 요소**: 읽기 쉬움 · 예측 가능 · 오용 방지 · 모듈화 · 재사용/일반화 · 테스트 용이 — Ch5~9·10이 각각을 실천으로
- **"미래에 어떻게 잘못될 수 있는가"**: 품질 판단의 기본 질문 — 오늘의 편의보다 내일의 오용 가능성
- **추상화 계층**: 한 번에 한 계층만 생각하게 — 거대 함수/클래스 해체의 기준 (Ch2)
- **코드 계약**: 명백한 것 > 세부 조항 > 주석 — 계약이 명시적일수록 오용이 어렵다 (Ch3·7)
- **오류는 복구 가능성으로 분류**: 복구 가능(호출자에게 신호) vs 불가능(빠른 실패) (Ch4)
- **테스트는 기능(동작) 기준**: 구현에 결합된 테스트는 리팩터링을 방해한다 (Ch10~11)

## 시그니처 요소와 표기 규칙

- 각 챕터 공통: `핵심 질문` → 번호 섹션(나쁜 예 → 좋은 예 대비) → `코드 품질 6대 요소 연결` → `요약`
- 코드: 원서 의사코드 `<details>` 접기 + TypeScript 변환본 펼침
- `>` blockquote 스타일 콜아웃 (refactoring-2nd·fundamentals-2nd와 동일 계열)

## origin 분리

- `0~14, 99` = 16개 파일 (0=서문/목차, 1~11=Ch1~Ch11 — 파트 표지는 각 파트 첫 챕터 파일 맨 앞, 12=부록A, 13=부록B, 14=부록C, 99=색인). 원본 14,073줄 = 합계 일치, 페이지 순차 검증 완료
