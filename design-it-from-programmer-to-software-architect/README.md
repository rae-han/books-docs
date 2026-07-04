# Design It!: From Programmer to Software Architect

> *Design It!: From Programmer to Software Architect* (Michael Keeling, 2017)
> 한국어판: 『개발자에서 아키텍트로 — 38가지 팀 활동을 활용한 실전 소프트웨어 아키텍트 훈련법』 (김영재 옮김, 한빛미디어, 2021)

마이클 킬링(*Michael Keeling - IBM Watson 프로젝트에서 소프트웨어 아키텍트로 활동. 실전 아키텍처 워크숍 강연자*)의 실전 아키텍처 훈련서. 개발자가 아키텍트로 성장하기 위한 마인드셋·전략·기법을 **38가지 팀 활동 카탈로그**로 풀어내고, **라이언하트 프로젝트(스프링필드시 예산 집행부 시스템)** 를 하나의 사례 연구로 관통한다. 소프트웨어 아키텍처를 **디자인 싱킹**의 관점에서 바라보며, 개인의 지식이 아니라 **팀 활동을 통해 함께 설계**하는 방법을 제시한다.

---

## 책의 핵심 메시지

> **팀을 위해서가 아니라, 팀과 함께 설계하라.**

- **아키텍처는 사회적 활동이다**: 아무리 훌륭한 설계도 팀이 이해하지 못하면 쓸모없다. 아키텍트의 최우선 책무는 팀의 설계 역량을 키우는 것
- **디자인 싱킹으로 접근하라**: 문제 이해 → 해결책 탐색 → 실현 → 평가의 순환. 마인드셋을 상황에 맞게 전환한다
- **트레이드오프가 곧 설계다**: 완벽한 아키텍처는 없다. 품질 속성 간의 트레이드오프를 이해하고 선택하는 것이 아키텍트의 일
- **팀 활동으로 함께 설계하라**: 워크숍·스튜디오·촌평 회의 등 검증된 38가지 활동을 실전에서 활용
- **점진적으로 완성하라**: 결정을 최대한 늦추되(Last Responsible Moment) 후회는 최소화한다

---

## 학습 가이드

### 처음 읽는 경우

**Part 1 → 2 → 3 순서대로**. Part 1(Ch1-2)로 마인드셋을 잡고, Part 2(Ch3-13)로 설계·문서화·평가·팀 이끌기의 전체 흐름을 익힌 뒤, Part 3(Ch14-17)의 활동 카탈로그는 실전에서 필요할 때 골라 쓴다.

### 개발자가 아키텍트로 성장하려면

- Ch1 (아키텍트가 되다) — 역할의 6가지 축
- Ch2 (디자인 싱킹 기초) — HART 원칙과 4가지 마인드셋
- Ch3 (설계 전략 고안하기) — 위험 기반 설계
- Ch13 (아키텍트에게 힘 실어주기) — 팀과 함께 설계하기

### 팀 워크숍 실전에 초점을 둔다면

- Ch9 (디자인 스튜디오) — 아키텍처 워크숍 운영법
- Ch14-17 (활동 카탈로그) — 38가지 검증된 활동
- Ch12 (아키텍처 평가하기) — ATAM과 경량 평가

### 아키텍처 문서화가 고민이라면

- Ch10 (설계 시각화하기) — C4 모델, 5가지 뷰
- Ch11 (아키텍처 문서화하기) — ADR, 아키텍처 하이쿠

### 설계 결정을 내리는 방법이 궁금하다면

- Ch5 (아키텍처 핵심 요구사항 - ASR)
- Ch6 (아키텍처 선택하기) — 의사결정 매트릭스
- Ch7 (아키텍처 패턴) — 10가지 패턴 카탈로그
- Ch8 (의미있는 모델로 복잡도 관리)

---

## 전체 목차

### Part 1 — 소프트웨어 아키텍처 (Ch1-2)

아키텍트의 역할과 디자인 싱킹 관점.

| Ch | 제목 | 핵심 |
|---|---|---|
| [1](ch01-becoming-a-software-architect.md) | **Becoming a Software Architect (소프트웨어 아키텍트가 되다)** | 아키텍트의 6가지 역할, 3가지 구조(모듈·컴포넌트-커넥터·할당), 품질 속성, 라이언하트 프로젝트 소개 |
| [2](ch02-design-thinking-fundamentals.md) | **Design Thinking Fundamentals (디자인 싱킹 기초)** | HART 4원칙, 4가지 디자인 마인드셋(이해/탐색/실현/평가), 생각-실행-확인 순환 |

### Part 2 — 아키텍처 설계의 기초 (Ch3-13)

설계 전략부터 시각화·문서화·평가·팀 이끌기까지의 전체 흐름.

| Ch | 제목 | 핵심 |
|---|---|---|
| [3](ch03-designing-strategies.md) | **Designing Strategies (설계 전략 고안하기)** | Satisficing, 배리 베임 sweet spot, 조건-결과 위험 템플릿, 능동적/수동적 설계 |
| [4](ch04-empathizing-with-stakeholders.md) | **Empathizing with Stakeholders (이해관계자와 공감하기)** | 이해관계자 맵, 벳 볼 로데의 고객 경험 아키텍처 4단계, 비즈니스 목표 정의 |
| [5](ch05-architecturally-significant-requirements.md) | **Architecturally Significant Requirements (ASR)** | ASR 4카테고리, 품질 속성 시나리오 6요소, 콘웨이 법칙, ASR 워크북 |
| [6](ch06-choosing-architecture.md) | **Choosing Architecture (아키텍처 선택하기)** | 분기·융합, 스무디 믹서기 비유, 의사결정 매트릭스, Last Responsible Moment |
| [7](ch07-patterns.md) | **Patterns (패턴으로 기초 만들기)** | 10가지 패턴(레이어, 포트-어댑터, 파이프-필터, SOA, 발행/구독, 공유 데이터 등) |
| [8](ch08-modeling-complexity.md) | **Modeling Complexity (의미있는 모델로 복잡도 관리하기)** | 메타모델 설계, 개념 개별화, 알로 벨시의 이름 짓기, 코드로 모델 구현 |
| [9](ch09-architecture-design-studio.md) | **Architecture Design Studio (아키텍처 디자인 스튜디오 운영하기)** | 샤레트 유래, 3F 원칙, 7단계 실행, 만들기-공유-비평, 원격 협업 |
| [10](ch10-visualizing-design.md) | **Visualizing Design (설계 시각화하기)** | 5가지 뷰 유형, 6가지 다이어그램 원칙, C4 모델 계층 |
| [11](ch11-documenting-architecture.md) | **Documenting Architecture (아키텍처 문서화하기)** | 4가지 서술 방법, SAD·ADR·아키텍처 하이쿠, Views and Beyond·4+1·C4 |
| [12](ch12-evaluating-architecture.md) | **Evaluating Architecture (아키텍처 평가하기)** | 3요소(산출물·루브릭·통찰력), ATAM, 아키텍처 이슈의 무지개 6색 |
| [13](ch13-empowering-the-architect.md) | **Empowering the Architect (아키텍트에게 힘 실어주기)** | 팀과 함께 설계, 안전한 훈련 4가지, 유르헌 아펠로의 7가지 위임 레벨 |

### Part 3 — 아키텍트의 은빛 도구상자 (Ch14-17): 38가지 활동 카탈로그

디자인 싱킹의 4가지 마인드셋(이해/탐색/실현/평가)에 맞춘 활동 카탈로그.

| Ch | 제목 | 마인드셋 | 활동 개수 |
|---|---|---|---|
| [14](ch14-understanding-the-problem.md) | **When You Want to Understand the Problem (문제를 이해하고 싶을 때)** | 이해하기 | 10개 (활동 1-10) |
| [15](ch15-exploring-solutions.md) | **When You Want to Explore Solutions (해결책을 찾고 싶을 때)** | 탐색하기 | 9개 (활동 11-19) |
| [16](ch16-making-design-tangible.md) | **When You Want to Make Design Tangible (손에 잡히는 설계를 만들고 싶을 때)** | 실현하기 | 10개 (활동 20-29) |
| [17](ch17-evaluating-design-alternatives.md) | **When You Want to Evaluate Design Alternatives (설계 대안을 평가하고 싶을 때)** | 평가하기 | 9개 (활동 30-38) |

---

## 라이언하트 프로젝트 (사례 연구)

책 전체를 관통하는 사례로 **스프링필드시 예산 집행부의 RFP(*Request For Proposal - 제안 요청서*) 시스템 현대화**가 사용된다.

**배경**: 예산 부족으로 비용을 삭감해야 하는 스프링필드시. 시장은 예산 집행부 업무를 개선하고 싶어한다. 화장지·의료용품·농구공까지 다양한 물품을 조달하며, 이 과정을 지역 신문에 RFP로 공고하고 있다.

챕터마다 라이언하트 프로젝트가 어떻게 진행되는지 다음 활동으로 이어진다:
- Ch4: 이해관계자 인터뷰 → 비즈니스 목표 도출
- Ch5: ASR 워크숍 → 워크북 완성
- Ch6: 의사결정 매트릭스로 아키텍처 선택
- Ch8: 도메인 모델 확립
- Ch9: 디자인 스튜디오 진행
- Ch10-11: 시각화·문서화
- Ch12: 아키텍처 평가
- Ch13: **성대한 결말** — 10억 원 절약

---

## 노트의 구성 요소

각 챕터는 다음 요소로 구성되어 있다:

- `## 핵심 질문` — 챕터가 답하려는 물음 (인라인 텍스트)
- 번호가 매겨진 주요 섹션 (`## 1.`, `## 2.`, ...)
- `> **핵심 통찰**:` 콜아웃 — 챕터의 핵심 인사이트 (💡 gray_bg)
- 레이블 없는 `>` 인용문 — 저자 마이클 킬링의 경험담과 외부 인용
- `> **직접 해보기**:` — 실전 실습 안내 (blockquote)
- `(*Term - 설명*)` 인라인 이탤릭 — 처음 등장하는 용어 설명
- 비교/카테고리 정리하는 마크다운 표
- `## N. 라이언하트 프로젝트 사례` — 사례 연구 별도 섹션
- `## 요약` — 챕터 마지막 불릿 정리

Ch14-17 (활동 카탈로그)은 다른 구조:
- `## 활동 개요` — 챕터의 활동 요약 표
- `## 활동 N: 활동명 (영문명)` — 각 활동
  - **목적** / **참가자** / **소요 시간** / **준비물** / **실행 단계** / **지침과 팁**

---

## 책의 인상적인 인용

> 팀을 위해서가 아니라, 팀과 함께 설계하라.

> 아무리 멋진 아키텍처를 설계해도 아무도 이해하지 못한다면 쓸모없다.

> 물이 장애물을 만났을 때 자연스럽게 흘러가듯, 소프트웨어도 장애물을 만날 때 쉽게 변경 가능한 곳으로만 흘러간다. 아키텍처가 없는 소프트웨어는 가장 저항이 적은 방향만 찾아서 결과적으로 무거워지거나 흐트러진다.

> 소프트웨어 시스템은 결코 완벽하게 나누어떨어지지 않는다. 타협해야만 한다. 이 과정에서 실수도 하겠지. 시스템을 만들다 보면 아키텍처 곳곳에 기술 부채도 쌓이기 시작한다.

---

## 관련 책

- [the-hexagonal-developer/](../the-hexagonal-developer/) — 최범균의 시니어 개발자 성장론
- [the-software-craftsman/](../the-software-craftsman/) — 산드로 만쿠소의 소프트웨어 장인정신
- [code-that-fits-in-your-head/](../code-that-fits-in-your-head/) — 마크 시먼의 휴리스틱 소프트웨어 공학
- [clean-software/](../clean-software/) — 로버트 C. 마틴의 애자일 원칙·패턴·실천 방법
- [philosophy-of-software-design/](../philosophy-of-software-design/) — John Ousterhout의 소프트웨어 설계 철학
- [objects/](../objects/) — 조영호의 객체지향 설계
