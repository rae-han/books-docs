# 오브젝트 (Objects)

> **코드로 이해하는 객체지향 설계**

## 책 정보

| 항목 | 내용 |
|------|------|
| **저자** | 조영호 |
| **출판사** | 위키북스 |
| **출판년도** | 2019 |
| **대상 독자** | 객체지향 프로그래밍 경험이 있는 소프트웨어 개발자 |

## 책 소개

객체지향이란 무엇인가라는 질문에 대한 저자의 두 번째 대답이다. 전작 《객체지향의 사실과 오해》가 은유와 사고실험을 통해 역할/책임/협력의 개념을 풀어냈다면, 이 책은 **코드**라는 개발자에게 가장 친숙한 도구를 이용해 객체지향 설계의 핵심 원칙을 설명한다.

티켓 판매 시스템, 영화 예매 시스템, 전화 요금 계산 시스템이라는 세 가지 예제를 반복적으로 발전시키며, 절차적 코드가 왜 문제인지, 캡슐화와 다형성이 어떻게 변경에 유연한 설계를 만드는지를 단계별로 보여준다. 추상적인 원칙을 코드로 증명하고, 나쁜 설계와 좋은 설계를 나란히 비교함으로써 "왜 그래야 하는가"에 대한 직관을 길러준다.

## 자매편과의 관계

이 책은 《[객체지향의 사실과 오해](../the-essence-of-object-orientation-객체지향의-사실과-오해/README.md)》의 후속작이다. 전작이 객체지향의 첫 번째 걸음(객체를 바라보는 것)과 두 번째 걸음(협력하는 공동체로 바라보는 것)을 다뤘다면, 이 책은 세 번째 걸음(적절한 역할과 책임 부여)과 네 번째 걸음(프로그래밍 언어로 표현하는 기술)에 초점을 맞춘다. 두 책은 독립적으로 읽을 수 있다.

## 목차

### 본문

| 챕터 | 제목 | 파일 |
|------|------|------|
| Chapter 1 | 객체, 설계 | [ch01-objects-and-design.md](ch01-objects-and-design.md) |
| Chapter 2 | 객체지향 프로그래밍 | [ch02-object-oriented-programming.md](ch02-object-oriented-programming.md) |
| Chapter 3 | 역할, 책임, 협력 | [ch03-roles-responsibilities-collaboration.md](ch03-roles-responsibilities-collaboration.md) |
| Chapter 4 | 설계 품질과 트레이드오프 | [ch04-design-quality-and-tradeoffs.md](ch04-design-quality-and-tradeoffs.md) |
| Chapter 5 | 책임 할당하기 | [ch05-assigning-responsibilities.md](ch05-assigning-responsibilities.md) |
| Chapter 6 | 메시지와 인터페이스 | [ch06-messages-and-interfaces.md](ch06-messages-and-interfaces.md) |
| Chapter 7 | 객체 분해 | [ch07-object-decomposition.md](ch07-object-decomposition.md) |
| Chapter 8 | 의존성 관리하기 | [ch08-managing-dependencies.md](ch08-managing-dependencies.md) |
| Chapter 9 | 유연한 설계 | [ch09-flexible-design.md](ch09-flexible-design.md) |
| Chapter 10 | 상속과 코드 재사용 | [ch10-inheritance-and-code-reuse.md](ch10-inheritance-and-code-reuse.md) |
| Chapter 11 | 합성과 유연한 설계 | [ch11-composition-and-flexible-design.md](ch11-composition-and-flexible-design.md) |
| Chapter 12 | 다형성 | [ch12-polymorphism.md](ch12-polymorphism.md) |
| Chapter 13 | 서브클래싱과 서브타이핑 | [ch13-subclassing-and-subtyping.md](ch13-subclassing-and-subtyping.md) |
| Chapter 14 | 일관성 있는 협력 | [ch14-consistent-collaboration.md](ch14-consistent-collaboration.md) |
| Chapter 15 | 디자인 패턴과 프레임워크 | [ch15-design-patterns-and-frameworks.md](ch15-design-patterns-and-frameworks.md) |

### 부록

| 부록 | 제목 | 파일 |
|------|------|------|
| Appendix A | 계약에 의한 설계 | [appendix-a-design-by-contract.md](appendix-a-design-by-contract.md) |
| Appendix B | 타입 계층의 구현 | [appendix-b-implementing-type-hierarchies.md](appendix-b-implementing-type-hierarchies.md) |
| Appendix C | 동적인 협력, 정적인 코드 | [appendix-c-dynamic-collaboration-static-code.md](appendix-c-dynamic-collaboration-static-code.md) |

## 읽기 순서

1~15장은 순서대로 읽는 것이 가장 효과적이다. 아래 다이어그램은 챕터 간 주요 의존 관계를 보여준다.

```
[Ch1: 객체, 설계]
     │  코드로 시작하는 객체지향 입문
     │  티켓 판매 시스템 리팩터링
     ▼
[Ch2: 객체지향 프로그래밍] ◀─────────────────────────────┐
     │  영화 예매 시스템 (책임 중심 설계)                    │
     │  상속, 다형성, 추상화                               │ 비교
     ▼                                                   │
[Ch3: 역할, 책임, 협력]                                    │
     │  객체지향 설계의 핵심 재료                            │
     ▼                                                   │
[Ch4: 설계 품질과 트레이드오프] ─────────────────────────────┘
     │  영화 예매 시스템 (데이터 중심 설계)
     │  캡슐화, 응집도, 결합도
     ▼
[Ch5: 책임 할당하기]
     │  GRASP 패턴
     ▼
[Ch6: 메시지와 인터페이스]
     │  디미터 법칙, 묻지 말고 시켜라
     │  명령-쿼리 분리
     ▼
[Ch7: 객체 분해] ── 역사적 배경: 프로시저 → 모듈 → ADT → 클래스
     │
     ▼
[Ch8: 의존성 관리하기] ──┐
     │                   │
     ▼                   ▼
[Ch9: 유연한 설계]    [Ch10: 상속과 코드 재사용]
     │  OCP, DIP, DI       │  전화 요금 시스템
     │  FACTORY             │  취약한 기반 클래스
     │                      ▼
     │                [Ch11: 합성과 유연한 설계]
     │                      │  상속 → 합성 전환
     │                      │  믹스인 (Scala)
     │                      ▼
     └───────────────▶[Ch12: 다형성]
                            │  동적 메서드 탐색
                            │  self/super 참조
                            ▼
                      [Ch13: 서브클래싱과 서브타이핑]
                            │  LSP, 행동 호환성
                            ▼
                      [Ch14: 일관성 있는 협력]
                            │  조건 로직 → 객체 탐색
                            │  캡슐화의 4가지 종류
                            ▼
                      [Ch15: 디자인 패턴과 프레임워크]
                            │  STRATEGY, TEMPLATE METHOD
                            │  DECORATOR, IoC
                            ▼
                      [부록 A~C: 심화]
                        A: 계약에 의한 설계 (DBC)
                        B: 타입 계층의 구현
                        C: 동적 협력 → 정적 코드
```

## 핵심 예제 도메인

이 책은 세 가지 도메인 예제를 반복 발전시키며 개념을 설명한다:

| 도메인 | 등장 챕터 | 역할 |
|--------|-----------|------|
| **티켓 판매 시스템** | Ch1, Ch6 | 객체지향 입문, 절차적 → 객체지향 리팩터링 |
| **영화 예매 시스템** | Ch2~Ch5, Ch8~Ch9, Ch13, Ch15 | 책임 중심 설계의 핵심 예제, 다양한 원칙 적용 |
| **전화 요금 계산 시스템** | Ch10~Ch11, Ch14 | 상속/합성/일관성 있는 협력의 실전 예제 |

## 챕터별 특수 요소

이 책의 학습 노트에는 다음과 같은 특수 요소가 포함된다:

- `## 리팩터링 과정`: 나쁜 코드 → 좋은 코드로의 단계별 개선 추적 테이블
- `## 설계 원칙`: 챕터별 OOP 설계 원칙 정리 테이블
- `### 나쁜 설계` / `### 좋은 설계`: before/after 코드 블록 대비
- **클래스 다이어그램**: ASCII/유니코드 박스 문자로 클래스 관계 시각화
- `> **핵심 통찰**:` 핵심 인사이트 콜아웃
- `>` (레이블 없는 인용문): 저자의 경험담 및 외부 인용
- **코드 예제**: Java(원본)는 `<details>` 접기, TypeScript(변환)는 항상 펼침
