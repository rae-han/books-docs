# Fundamentals of Software Architecture (1st Edition)

> *Fundamentals of Software Architecture: An Engineering Approach* (Mark Richards, Neal Ford, O'Reilly, 2020)
> 한국어판: 『소프트웨어 아키텍처 101 — 엔지니어링 접근 방식으로 배우는 소프트웨어 아키텍처 기초』 (이일웅 옮김, 한빛미디어, 2021)

마크 리처즈(*Mark Richards - 분산 아키텍처 전문 소프트웨어 아키텍트, DeveloperToArchitect.com 창립자*)와 닐 포드(*Neal Ford - 쏘우트웍스 이사, 밈랭글러*)의 소프트웨어 아키텍처 입문 고전. 아키텍처를 **엔지니어링 접근 방식**으로 바라보며, 아키텍처 특성을 정의·측정·거버넌스하는 법부터 다양한 아키텍처 스타일, 그리고 아키텍트에게 필요한 테크닉과 소프트 스킬까지 다룬다.

---

## 책의 핵심 메시지

> **소프트웨어 아키텍처의 모든 것은 다 트레이드오프다.**
> — 소프트웨어 아키텍처 제1법칙

> **'어떻게'보다 '왜'가 더 중요하다.**
> — 소프트웨어 아키텍처 제2법칙

- **아키텍처는 콘텍스트다**: 모든 결정은 그 당시 환경의 결과물이다. 정적이지 않고 끊임없이 변한다
- **아키텍처 = 구조 + 특성 + 결정 + 원칙**: "마이크로서비스입니다"는 구조만 말한 것
- **깊이보다 폭**: 아키텍트는 한 기술의 전문가보다 여러 기술의 장단점을 아는 사람
- **아키텍처 특성이 스타일을 결정한다**: 우선순위가 높은 품질 특성이 아키텍처 스타일 선택을 이끈다

---

## 학습 가이드

### 처음 읽는 경우

**전체 순서대로 읽는 것을 권장**한다. Ch1으로 아키텍처의 정의와 아키텍트의 역할을 잡고, PART I(Ch2-8)로 아키텍처 특성·모듈성·컴포넌트라는 어휘를 습득한 뒤, PART II(Ch9-18)에서 다양한 스타일을 트레이드오프 관점으로 비교하고, PART III(Ch19-24)에서 실전 테크닉과 소프트 스킬을 익힌다.

### 아키텍처 특성(품질 속성)이 궁금하다면

- Ch4 (특성 정의) → Ch5 (특성 식별) → Ch6 (측정·거버넌스) → Ch7 (특성 범위)

### 아키텍처 스타일을 비교하고 싶다면

- Ch9 (기초) → Ch10-17 (8가지 스타일) → Ch18 (스타일 선정)
- 각 스타일 장의 **아키텍처 특성 등급표(별점 scorecard)** 로 트레이드오프를 한눈에 비교

### 아키텍트의 실전 스킬에 초점을 둔다면

- Ch19 (아키텍처 결정, ADR) → Ch20 (리스크 분석) → Ch21 (도식화·프레젠테이션)
- Ch22 (팀) → Ch23 (협상·리더십) → Ch24 (커리어)

---

## 전체 목차

### 서론

| Ch | 제목 | 핵심 |
|---|---|---|
| [1](ch01-introduction.md) | **Introduction (서론)** | 아키텍처의 4요소(구조·특성·결정·원칙), 아키텍트 8가지 기대치, 제1·2법칙 |

### PART I — 기초 (Foundations)

아키텍처를 이해하는 데 필요한 기본 어휘와 개념.

| Ch | 제목 | 핵심 |
|---|---|---|
| [2](ch02-architectural-thinking.md) | **Architectural Thinking (아키텍처 사고)** | 아키텍처 vs 설계, 기술 깊이 vs 폭, 꽁꽁 언 원시인 안티패턴 |
| [3](ch03-modularity.md) | **Modularity (모듈성)** | 응집도, 구심/원심 커플링, 추상도·불안정도·메인 시퀀스로부터의 거리, 커네이선스 |
| [4](ch04-defining-architecture-characteristics.md) | **Defining Architecture Characteristics (아키텍처 특성 정의)** | 특성 3기준, 명시적/암묵적, 운영·구조·횡단 특성 |
| [5](ch05-identifying-architecture-characteristics.md) | **Identifying Architecture Characteristics (아키텍처 특성 식별)** | 도메인 관심사 → 특성 도출, 아키텍처 카타 |
| [6](ch06-measuring-and-governing-architecture-characteristics.md) | **Measuring and Governing (측정 및 거버넌스)** | 운영/구조/프로세스 측정치, 순환 복잡도, 피트니스 함수 |
| [7](ch07-scope-of-architecture-characteristics.md) | **Scope of Architecture Characteristics (특성 범위)** | 아키텍처 퀀텀, 커네이선스, 바운디드 컨텍스트 |
| [8](ch08-component-based-thinking.md) | **Component-Based Thinking (컴포넌트 기반 사고)** | 모듈 vs 컴포넌트, 기술/도메인 분할, 콘웨이 법칙, 컴포넌트 식별 |

### PART II — 아키텍처 스타일 (Architecture Styles)

각 스타일을 토폴로지와 **아키텍처 특성 등급표(별점)** 로 비교한다.

| Ch | 제목 | 핵심 |
|---|---|---|
| [9](ch09-foundations.md) | **Foundations (기초)** | 스타일 vs 패턴, 기초 패턴, 모놀리식/분산 분류, 분산 컴퓨팅 8대 오류 |
| [10](ch10-layered-architecture-style.md) | **Layered (레이어드)** | 관심사 분리, 레이어 격리, 싱크홀 안티패턴 |
| [11](ch11-pipeline-architecture-style.md) | **Pipeline (파이프라인)** | 파이프-필터, 4종 필터(생산자·변환자·테스터·소비자) |
| [12](ch12-microkernel-architecture-style.md) | **Microkernel (마이크로커널)** | 코어 시스템 + 플러그인, 레지스트리, 계약 |
| [13](ch13-service-based-architecture-style.md) | **Service-Based (서비스 기반)** | 분산 매크로 레이어드, 도메인 서비스, 단일 DB |
| [14](ch14-event-driven-architecture-style.md) | **Event-Driven (이벤트 기반)** | 브로커 vs 미디에이터 토폴로지, 비동기, 데이터 손실 방지 |
| [15](ch15-space-based-architecture-style.md) | **Space-Based (공간 기반)** | 튜플 스페이스, 프로세싱 유닛·가상 미들웨어, 극단적 확장성 |
| [16](ch16-orchestration-driven-service-oriented-architecture.md) | **Orchestration-Driven SOA (오케스트레이션 기반 SOA)** | 비즈니스/엔터프라이즈/앱/인프라 서비스, ESB, 재사용의 대가 |
| [17](ch17-microservices-architecture.md) | **Microservices (마이크로서비스)** | 바운디드 컨텍스트, 세분도, 데이터 격리, 사가 |
| [18](ch18-choosing-the-appropriate-architecture-style.md) | **Choosing the Appropriate Style (최적의 스타일 선정)** | 특성 우선순위 → 스타일 결정, 모놀리식 vs 분산 |

### PART III — 테크닉과 소프트 스킬 (Techniques and Soft Skills)

| Ch | 제목 | 핵심 |
|---|---|---|
| [19](ch19-architecture-decisions.md) | **Architecture Decisions (아키텍처 결정)** | 결정 안티패턴, ADR(제목·상태·콘텍스트·결정·결과) |
| [20](ch20-analyzing-architecture-risk.md) | **Analyzing Architecture Risk (리스크 분석)** | 리스크 매트릭스(가능성×영향), 리스크 스토밍 |
| [21](ch21-diagramming-and-presenting-architecture.md) | **Diagramming and Presenting (도식화·프레젠테이션)** | C4·UML·아키메이트, 점진적 공개, 발표 안티패턴 |
| [22](ch22-making-teams-effective.md) | **Making Teams Effective (개발팀을 효율적으로)** | 아키텍트 3유형, 탄력적 경계, 팀 경고 신호 |
| [23](ch23-negotiation-and-leadership-skills.md) | **Negotiation and Leadership Skills (협상과 리더십)** | 이해관계자별 협상, 4C, 모범을 보여 리드 |
| [24](ch24-developing-a-career-path.md) | **Developing a Career Path (커리어 패스 개발)** | 20분 규칙, 기술 레이더, T자형/파이형 확장 |

### 부록

| Appendix | 제목 | 핵심 |
|---|---|---|
| [A](appendix-a-self-assessment-questions.md) | **Self-Assessment Questions (자율평가문제)** | 1~24장 자율평가 질문 모음 (복습용) |

---

## 노트의 구성 요소

각 챕터는 다음 요소로 구성되어 있다:

- `## 핵심 질문` — 챕터가 답하려는 물음 (인라인 텍스트)
- 번호가 매겨진 주요 섹션 (`## 1.`, `## 2.`, ...)
- `> **핵심 통찰**:` 콜아웃 — 챕터의 핵심 인사이트 (💡 gray_bg)
- 레이블 없는 `>` 인용문 — 저자(마크·닐)의 경험담과 외부 인용
- `> **소프트웨어 아키텍처 제N법칙**` — 이 책의 시그니처, 아키텍처 법칙
- **아키텍처 특성 등급표** — 스타일 장(Ch10-17)마다 별점(★) scorecard
- ASCII/유니코드 **토폴로지 다이어그램**
- `(*Term - 설명*)` 인라인 이탤릭 — 처음 등장하는 용어 설명
- `## 요약` — 챕터 마지막 불릿 정리

---

## 판(edition) 참고

이 폴더는 **1판**(소프트웨어 아키텍처 101)이다. 원서 동일 저자의 **2판**(*The Basics*)은 별도 폴더 [fundamentals-of-software-architecture-2nd-edition/](../fundamentals-of-software-architecture-2nd-edition/) 에 있다.

---

## 관련 책

- [design-it-from-programmer-to-software-architect/](../design-it-from-programmer-to-software-architect/) — 마이클 킬링의 실전 아키텍처 훈련서 (팀 활동 카탈로그)
- [clean-software/](../clean-software/) — 로버트 C. 마틴의 애자일 원칙·패턴·실천 방법
- [the-hexagonal-developer/](../the-hexagonal-developer/) — 최범균의 시니어 개발자 성장론
- [philosophy-of-software-design/](../philosophy-of-software-design/) — John Ousterhout의 소프트웨어 설계 철학
