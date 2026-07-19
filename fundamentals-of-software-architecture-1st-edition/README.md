# 소프트웨어 아키텍처 101 (Fundamentals of Software Architecture, 1st Edition)

> *Fundamentals of Software Architecture: An Engineering Approach* (Mark Richards & Neal Ford, O'Reilly, 2020)
> 한국어판: 『소프트웨어 아키텍처 101 — 엔지니어링 접근 방식으로 배우는 소프트웨어 아키텍처 기초』 (이일웅 옮김, 한빛미디어, 2021)

마크 리처즈(*Mark Richards - 분산 아키텍처 전문 소프트웨어 아키텍트, DeveloperToArchitect.com 창립자*)와 닐 포드(*Neal Ford - 쏘우트웍스 이사, 밈랭글러*)의 소프트웨어 아키텍처 입문 고전. 아키텍처를 **엔지니어링 접근 방식**으로 바라보며, 아키텍처 특성의 정의·측정·거버넌스부터 아키텍처 스타일 비교, 아키텍트의 테크닉과 소프트 스킬까지 다룬다.

## 책 정보

| 항목 | 내용 |
|------|------|
| **저자** | 마크 리처즈(Mark Richards) · 닐 포드(Neal Ford) |
| **역자** | 이일웅 |
| **출판** | 한빛미디어, 2021 (원서: O'Reilly, 2020) |
| **구성** | 서론 + PART I 기초 + PART II 스타일 + PART III 테크닉·소프트 스킬 |
| **대상 독자** | 아키텍처를 처음 체계적으로 배우는 개발자, 아키텍트 지망자 |

## 개요

이 책의 뼈대는 두 개의 법칙이다 — **제1법칙: 소프트웨어 아키텍처의 모든 것은 다 트레이드오프다**, **제2법칙: '어떻게'보다 '왜'가 더 중요하다**. 아키텍처는 구조 하나로 정의되지 않고 **구조 + 아키텍처 특성 + 결정 + 설계 원칙**의 조합이며, 모든 결정은 그 당시 콘텍스트의 결과물이다.

PART I은 아키텍처를 말하는 데 필요한 어휘(아키텍처 사고·모듈성·특성·퀀텀·컴포넌트), PART II는 8가지 아키텍처 스타일을 토폴로지와 **아키텍처 특성 등급표(별점 scorecard)**로 비교, PART III는 결정 기록(ADR)·리스크 분석·도식화·팀·협상·커리어를 다룬다. 같은 저자의 2판(『The Basics』)은 별도 폴더 [fundamentals-of-software-architecture-2nd-edition/](../fundamentals-of-software-architecture-2nd-edition/)에 있다.

## 목차

### 서론

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 1 | [Introduction](ch01-introduction.md) | 아키텍처 4요소 · 아키텍트 기대치 · 아키텍처 법칙 | 아키텍처 = 구조+특성+결정+원칙, 아키텍트의 8가지 기대치와 제1·2법칙 |

### PART I: 기초 (Ch 2-8)

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 2 | [Architectural Thinking](ch02-architectural-thinking.md) | 아키텍처 사고 · 기술 깊이 vs 폭 | 아키텍트는 깊이보다 폭 — 꽁꽁 언 원시인 안티패턴 경계 |
| 3 | [Modularity](ch03-modularity.md) | 응집도 · 커플링 · 커네이선스 · 메인 시퀀스 | 모듈성을 측정하는 도구들 — 구심/원심 결합과 추상도·불안정도 |
| 4 | [Defining Architecture Characteristics](ch04-defining-architecture-characteristics.md) | 아키텍처 특성 · 운영/구조/횡단 특성 | '-ilities'의 세계 — 특성의 3기준과 분류 |
| 5 | [Identifying Architecture Characteristics](ch05-identifying-architecture-characteristics.md) | 특성 식별 · 도메인 관심사 · 아키텍처 카타 | 도메인 요구에서 아키텍처 특성을 뽑아내는 법 |
| 6 | [Measuring and Governing](ch06-measuring-and-governing-architecture-characteristics.md) | 특성 측정 · 순환 복잡도 · 피트니스 함수 | 특성을 측정 가능하게 — 피트니스 함수로 거버넌스 자동화 |
| 7 | [Scope of Architecture Characteristics](ch07-scope-of-architecture-characteristics.md) | 아키텍처 퀀텀 · 커네이선스 · 바운디드 컨텍스트 | 특성의 적용 범위 — 시스템 전체가 아니라 퀀텀 단위로 |
| 8 | [Component-Based Thinking](ch08-component-based-thinking.md) | 컴포넌트 · 기술/도메인 분할 · 콘웨이 법칙 | 컴포넌트 식별 프로세스 — 기술 분할 vs 도메인 분할 |

### PART II: 아키텍처 스타일 (Ch 9-18) — 토폴로지 + 별점 등급표

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 9 | [Foundations](ch09-foundations.md) | 스타일 분류 · 분산 컴퓨팅 오류 | 모놀리식/분산 분류와 분산 컴퓨팅 8대 오류 |
| 10 | [Layered](ch10-layered-architecture-style.md) | 레이어드 · 관심사 분리 · 싱크홀 | 기술 분할의 기본형 — 레이어 격리와 싱크홀 안티패턴 |
| 11 | [Pipeline](ch11-pipeline-architecture-style.md) | 파이프-필터 · 4종 필터 | 단방향 파이프와 4종 필터(생산자·변환자·테스터·소비자) |
| 12 | [Microkernel](ch12-microkernel-architecture-style.md) | 마이크로커널 · 플러그인 · 레지스트리 | 코어 시스템 + 플러그인 — 커스터마이즈 가능한 제품형 구조 |
| 13 | [Service-Based](ch13-service-based-architecture-style.md) | 서비스 기반 · 도메인 서비스 · 단일 DB | 분산의 실용적 절충 — 굵은 도메인 서비스와 공유 DB |
| 14 | [Event-Driven](ch14-event-driven-architecture-style.md) | 이벤트 기반 · 브로커/미디에이터 · 비동기 | 브로커 vs 미디에이터 토폴로지 — 고성능 비동기의 대가 |
| 15 | [Space-Based](ch15-space-based-architecture-style.md) | 공간 기반 · 튜플 스페이스 · 프로세싱 유닛 | DB 병목 제거 — 인메모리 그리드로 극단적 확장성 |
| 16 | [Orchestration-Driven SOA](ch16-orchestration-driven-service-oriented-architecture.md) | SOA · ESB · 재사용의 대가 | 전사적 재사용을 노린 오케스트레이션 SOA — 역사적 교훈 |
| 17 | [Microservices](ch17-microservices-architecture.md) | 마이크로서비스 · 바운디드 컨텍스트 · 사가 | 바운디드 컨텍스트 단위의 극단적 분리 — 세분도와 데이터 격리 |
| 18 | [Choosing the Appropriate Style](ch18-choosing-the-appropriate-architecture-style.md) | 스타일 선정 · 특성 우선순위 | 정답은 없다 — 특성 우선순위가 스타일을 결정한다 |

### PART III: 테크닉과 소프트 스킬 (Ch 19-24)

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 19 | [Architecture Decisions](ch19-architecture-decisions.md) | 아키텍처 결정 레코드 · 결정 안티패턴 | 결정을 기록하라 — ADR의 구조(제목·상태·콘텍스트·결정·결과) |
| 20 | [Analyzing Architecture Risk](ch20-analyzing-architecture-risk.md) | 리스크 매트릭스 · 리스크 스토밍 | 가능성×영향 매트릭스와 팀 단위 리스크 스토밍 |
| 21 | [Diagramming and Presenting](ch21-diagramming-and-presenting-architecture.md) | C4 · UML · 점진적 공개 | 아키텍처를 그리고 발표하는 기술 |
| 22 | [Making Teams Effective](ch22-making-teams-effective.md) | 아키텍트 3유형 · 탄력적 경계 | 통제·조력·무관심 — 팀에 맞는 경계 설정 |
| 23 | [Negotiation and Leadership Skills](ch23-negotiation-and-leadership-skills.md) | 협상 · 4C · 모범 리더십 | 이해관계자별 협상 전술과 아키텍트의 리더십 |
| 24 | [Developing a Career Path](ch24-developing-a-career-path.md) | 20분 규칙 · 기술 레이더 | 매일 20분 — 아키텍트의 지속 학습 전략 |

### 부록

| 부록 | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| A | [Self-Assessment Questions](appendix-a-self-assessment-questions.md) | 자율평가 | 1~24장 복습용 자율평가 질문 모음 |

## 학습 가이드

1. **처음이라면 순서대로** — Ch1(정의·법칙) → PART I(어휘) → PART II(스타일 비교) → PART III(실전 스킬)
2. **아키텍처 특성 트랙**: Ch4(정의) → Ch5(식별) → Ch6(측정·거버넌스) → Ch7(범위·퀀텀)
3. **스타일 비교 트랙**: Ch9(기초) → Ch10~17(8가지 스타일 — 별점 등급표로 트레이드오프 비교) → Ch18(선정)
4. **실전 스킬 트랙**: Ch19(ADR) → Ch20(리스크) → Ch21(도식화) → Ch22~24(팀·협상·커리어)

## 핵심 개념 맵

- **제1법칙(트레이드오프)** 이 전체를 지배 — 스타일 장의 별점 등급표는 트레이드오프의 정량화다
- **제2법칙(왜 > 어떻게)** → ADR — 결정의 이유를 기록해야 아키텍처가 유지된다 (Ch19)
- **아키텍처 = 구조+특성+결정+원칙**: "마이크로서비스입니다"는 구조만 말한 것 (Ch1)
- **아키텍처 특성이 스타일을 결정**: 도메인 관심사 → 특성 식별 → 우선순위 → 스타일 선정의 흐름 (Ch4~7·18)
- **아키텍처 퀀텀**: 독립 배포 가능한 최소 단위 — 특성은 시스템이 아니라 퀀텀 범위로 판단 (Ch7)
- **측정과 거버넌스**: 특성은 선언이 아니라 피트니스 함수로 지속 검증 (Ch6)
- **아키텍트는 깊이보다 폭** — 기술 폭 + 소프트 스킬(협상·리더십·20분 규칙)이 커리어를 만든다 (Ch2·22~24)

## 인용문

전 책 통합 모음은 [루트 QUOTES.md](../QUOTES.md) 참조.

> 소프트웨어 아키텍처의 모든 것은 다 트레이드오프다.<br>— 마크 리처즈·닐 포드, 소프트웨어 아키텍처 제1법칙 (위치: Ch1)

> '어떻게'보다 '왜'가 더 중요하다.<br>— 마크 리처즈·닐 포드, 소프트웨어 아키텍처 제2법칙 (위치: Ch1)

## 시그니처 요소와 표기 규칙

- `> **소프트웨어 아키텍처 제N법칙**<br>내용` — 이 책의 시그니처 콜아웃
- **아키텍처 특성 등급표** — 스타일 장(Ch10-17)마다 별점(★) scorecard + ASCII/유니코드 토폴로지 다이어그램
- `## 핵심 질문` → 번호 섹션 → `> **핵심 통찰**:` → `## 요약` 구성, `(*Term - 설명*)` 용어 이탤릭
- 1판 노트는 `:::` 콜아웃 스타일 사용 (2판 노트는 `>` blockquote 스타일 — 판별 차이 주의)

## origin 분리

- `0~25, 99` = 27개 파일 (0=서문/목차, 1~24=Ch1~Ch24, 25=부록A 자율평가문제, 99=찾아보기)
- 페이지 번호: OCR 캡처 불충분(본문 러닝 헤더 3개만) → 순차 검증 생략, 라인 합계로 무결성 확인
