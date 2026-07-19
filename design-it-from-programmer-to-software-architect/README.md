# 개발자에서 아키텍트로 (Design It!: From Programmer to Software Architect)

> *Design It!: From Programmer to Software Architect* (Michael Keeling, Pragmatic Bookshelf, 2017)
> 한국어판: 『개발자에서 아키텍트로 — 38가지 팀 활동을 활용한 실전 소프트웨어 아키텍트 훈련법』 (김영재 옮김, 한빛미디어, 2021)

마이클 킬링(*Michael Keeling - IBM Watson 프로젝트에서 소프트웨어 아키텍트로 활동. 실전 아키텍처 워크숍 강연자*)의 실전 아키텍처 훈련서. 개발자가 아키텍트로 성장하기 위한 마인드셋·전략·기법을 **38가지 팀 활동 카탈로그**로 풀어내고, **라이언하트 프로젝트**를 하나의 사례 연구로 관통한다.

## 책 정보

| 항목 | 내용 |
|------|------|
| **저자** | 마이클 킬링(Michael Keeling) |
| **역자** | 김영재 |
| **출판** | 한빛미디어, 2021 (원서: Pragmatic Bookshelf, 2017) |
| **구성** | 본문(Ch1-13) + 활동 카탈로그(Ch14-17, 38가지) |
| **대상 독자** | 아키텍트로 성장하려는 개발자, 팀 설계 워크숍을 이끌어야 하는 리드 |

## 개요

소프트웨어 아키텍처를 **디자인 싱킹**의 관점에서 바라보며, 개인의 지식이 아니라 **팀 활동을 통해 함께 설계**하는 방법을 제시한다. 아키텍처는 사회적 활동이다 — 아무리 훌륭한 설계도 팀이 이해하지 못하면 쓸모없으며, 아키텍트의 최우선 책무는 팀의 설계 역량을 키우는 것이다.

Part 1이 마인드셋(아키텍트의 역할, 디자인 싱킹), Part 2가 설계 프로세스 전체 흐름(전략→이해관계자→ASR→선택→패턴→모델링→스튜디오→시각화→문서화→평가→팀), Part 3이 마인드셋별 38가지 활동 카탈로그다. 스프링필드시 RFP 시스템(라이언하트 프로젝트) 사례가 전 장을 관통한다.

## 목차

### Part 1: 소프트웨어 아키텍처 (Ch 1-2)

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 1 | [Becoming a Software Architect](ch01-becoming-a-software-architect.md) | 아키텍트의 역할 · 3가지 구조 · 품질 속성 | 아키텍트의 6가지 역할과 아키텍처의 정의 — 라이언하트 프로젝트 개막 |
| 2 | [Design Thinking Fundamentals](ch02-design-thinking-fundamentals.md) | 디자인 싱킹 · HART 원칙 · 4가지 마인드셋 | 이해→탐색→실현→평가 마인드셋과 생각-실행-확인 순환 |

### Part 2: 아키텍처 설계의 기초 (Ch 3-13)

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 3 | [Designing Strategies](ch03-designing-strategies.md) | 만족화 · 스위트 스폿 · 위험 기반 설계 | 얼마나 미리 설계할 것인가 — 위험이 설계 투자량을 결정한다 |
| 4 | [Empathizing with Stakeholders](ch04-empathizing-with-stakeholders.md) | 이해관계자 맵 · 비즈니스 목표 | 설계는 공감에서 시작 — 이해관계자와 비즈니스 목표 정의 |
| 5 | [Architecturally Significant Requirements](ch05-architecturally-significant-requirements.md) | ASR · 품질 속성 시나리오 · 콘웨이 법칙 | 아키텍처를 결정짓는 요구사항 4카테고리와 ASR 워크북 |
| 6 | [Choosing Architecture](ch06-choosing-architecture.md) | 분기와 융합 · 의사결정 매트릭스 · 책임 있는 마지막 순간 | 대안을 벌리고 좁히기 — 트레이드오프 기반 아키텍처 선택 |
| 7 | [Patterns](ch07-patterns.md) | 레이어 · 포트와 어댑터 · 파이프-필터 · 발행/구독 | 검증된 출발점 — 10가지 아키텍처 패턴 카탈로그 |
| 8 | [Modeling Complexity](ch08-modeling-complexity.md) | 메타모델 · 개념 개별화 · 이름 짓기 | 의미 있는 모델로 복잡도 관리 — 모델을 코드로 구현 |
| 9 | [Architecture Design Studio](ch09-architecture-design-studio.md) | 디자인 스튜디오 · 샤레트 · 만들기-공유-비평 | 아키텍처 워크숍 운영법 — 3F 원칙과 7단계 |
| 10 | [Visualizing Design](ch10-visualizing-design.md) | 뷰 · C4 모델 · 다이어그램 원칙 | 설계를 보이게 — 5가지 뷰와 C4 모델 계층 |
| 11 | [Documenting Architecture](ch11-documenting-architecture.md) | SAD · ADR · 아키텍처 하이쿠 | 상황에 맞는 문서화 — 무겁게(SAD)부터 가볍게(하이쿠·ADR)까지 |
| 12 | [Evaluating Architecture](ch12-evaluating-architecture.md) | 아키텍처 평가 · ATAM · 루브릭 | 설계를 시험대에 — 산출물·루브릭·통찰의 평가 3요소 |
| 13 | [Empowering the Architect](ch13-empowering-the-architect.md) | 함께 설계 · 위임 레벨 · 안전한 훈련 | 팀 전체를 아키텍트로 — 7가지 위임 레벨과 성장 지원 |

### Part 3: 아키텍트의 은빛 도구상자 (Ch 14-17) — 38가지 활동 카탈로그

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 14 | [When You Want to Understand the Problem](ch14-understanding-the-problem.md) | 이해하기 마인드셋 · 활동 1-10 | 문제를 이해하고 싶을 때 — 이해관계자 인터뷰·GQM 등 10개 활동 |
| 15 | [When You Want to Explore Solutions](ch15-exploring-solutions.md) | 탐색하기 마인드셋 · 활동 11-19 | 해결책을 찾고 싶을 때 — 컴포넌트 책임 카드 등 9개 활동 |
| 16 | [When You Want to Make Design Tangible](ch16-making-design-tangible.md) | 실현하기 마인드셋 · 활동 20-29 | 설계를 손에 잡히게 — ADR·아키텍처 하이쿠 등 10개 활동 |
| 17 | [When You Want to Evaluate Design Alternatives](ch17-evaluating-design-alternatives.md) | 평가하기 마인드셋 · 활동 30-38 | 대안을 평가하고 싶을 때 — 위험 폭풍·시나리오 훑기 등 9개 활동 |

## 학습 가이드

1. **처음이라면 Part 1 → 2 → 3 순서대로** — 마인드셋을 잡고 전체 흐름을 익힌 뒤, 활동 카탈로그(Ch14-17)는 필요할 때 골라 쓴다
2. **아키텍트 성장 경로**: Ch1(역할) → Ch2(디자인 싱킹) → Ch3(위험 기반 전략) → Ch13(팀과 함께)
3. **팀 워크숍 실전**: Ch9(디자인 스튜디오) → Ch14~17(활동 카탈로그) → Ch12(평가·ATAM)
4. **문서화 고민**: Ch10(C4 모델·뷰) → Ch11(ADR·하이쿠)
5. **설계 결정법**: Ch5(ASR) → Ch6(의사결정 매트릭스) → Ch7(패턴) → Ch8(모델링)

## 핵심 개념 맵

- **아키텍처 = 사회적 활동**: 팀을 위해서가 아니라 팀과 함께 설계 — 아키텍트의 책무는 팀의 설계 역량 성장 (Ch1·13)
- **디자인 싱킹 4마인드셋**: 이해→탐색→실현→평가의 순환 — Part 3의 활동 카탈로그가 이 축으로 분류된다 (Ch2·14~17)
- **위험이 설계량을 결정**: 위험이 크면 미리 설계, 작으면 바로 구현 — 만족화(satisficing)와 스위트 스폿 (Ch3)
- **ASR → 선택 → 평가**: 품질 속성 시나리오로 요구를 구체화하고, 트레이드오프 매트릭스로 고르고, 루브릭으로 검증 (Ch5·6·12)
- **결정은 최대한 늦추되 후회는 최소화** — 책임 있는 마지막 순간(Last Responsible Moment) (Ch6)
- **보여야 공유된다**: 뷰·C4·ADR — 시각화와 문서화는 설계 그 자체의 일부 (Ch10·11)

## 라이언하트 프로젝트 (사례 연구)

책 전체를 관통하는 사례 — **스프링필드시 예산 집행부의 RFP(*Request For Proposal - 제안 요청서*) 시스템 현대화**.

- Ch4: 이해관계자 인터뷰 → 비즈니스 목표 도출 / Ch5: ASR 워크숍 → 워크북 완성
- Ch6: 의사결정 매트릭스로 아키텍처 선택 / Ch8: 도메인 모델 확립 / Ch9: 디자인 스튜디오
- Ch10~11: 시각화·문서화 / Ch12: 아키텍처 평가 / Ch13: 성대한 결말 — 10억 원 절약

## 인용문

전 책 통합 모음은 [루트 QUOTES.md](../QUOTES.md) 참조.

> 팀을 위해서가 아니라, 팀과 함께 설계하라.<br>— 마이클 킬링 (위치: Ch1, 책 전체의 슬로건)

> 물이 장애물을 만났을 때 자연스럽게 흘러가듯, 소프트웨어도 장애물을 만날 때 쉽게 변경 가능한 곳으로만 흘러간다. 아키텍처가 없는 소프트웨어는 가장 저항이 적은 방향만 찾아서 결과적으로 무거워지거나 흐트러진다.<br>— 마이클 킬링 (위치: Ch1)

## 시그니처 요소와 표기 규칙

- `## 핵심 질문` (인라인 텍스트) → 번호 섹션 → `## 요약` 구성
- `> **핵심 통찰**:` 콜아웃 (💡 gray_bg) / 레이블 없는 `>` 인용문 (저자 경험담·외부 인용) / `> **직접 해보기**:` 실습 안내
- `## N. 라이언하트 프로젝트 사례` — 사례 연구 별도 섹션 (Ch1-13)
- Ch14-17은 활동 카탈로그 구조: `## 활동 개요` 표 + `## 활동 N: 활동명 (영문명)` (목적/참가자/소요 시간/준비물/실행 단계/지침과 팁)

## origin 분리

- `0~17, 18~19, 99` = 21개 파일 (0=서문/목차, 1~17=Ch1~Ch17, 18=부록 기여자들, 19=참고문헌, 99=찾아보기)
