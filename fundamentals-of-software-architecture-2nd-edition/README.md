# Fundamentals of Software Architecture: The Basics (2nd Edition)

> *Fundamentals of Software Architecture: The Basics* (2nd Edition) (Mark Richards, Neal Ford, O'Reilly, 2025)
> 한국어판: 『소프트웨어 아키텍처 The Basics』 (한빛미디어)

마크 리처즈(*Mark Richards - 분산 아키텍처 전문 소프트웨어 아키텍트, DeveloperToArchitect.com 창립자*)와 닐 포드(*Neal Ford - 쏘우트웍스 이사, 밈 랭글러*)의 소프트웨어 아키텍처 입문 고전 **개정 2판**. 아키텍처를 **엔지니어링 접근 방식**으로 바라보며, 아키텍처 특성을 정의·측정·거버넌스하는 법부터 다양한 아키텍처 스타일, 그리고 아키텍트에게 필요한 기법과 소프트 스킬까지 다룬다.

---

## 책의 핵심 메시지 — 세 가지 법칙

> **소프트웨어 아키텍처 제1법칙**<br>소프트웨어 아키텍처의 모든 것은 트레이드오프이다.

> **소프트웨어 아키텍처 제2법칙**<br>'어떻게(방법)'보다 '왜(이유)'가 더 중요하다.

> **소프트웨어 아키텍처 제3법칙**<br>대부분의 아키텍처적 결정은 양자택일이 아니라 양극단 사이의 스펙트럼에 있는 한 지점이다.

- **아키텍처는 콘텍스트다**: 모든 결정은 그 당시 환경의 결과물이다. 정적이지 않고 끊임없이 변한다
- **아키텍처 = 구조 + 특성 + 결정 + 원칙**: "마이크로서비스입니다"는 구조만 말한 것
- **깊이보다 폭**: 아키텍트는 한 기술의 전문가보다 여러 기술의 장단점을 아는 사람
- **아키텍처 특성이 스타일을 결정한다**: 스타일의 차별화는 '도메인'이 아니라 '아키텍처 특성 지원'에 있다

> **1판(24장) → 2판(27장) 주요 변경점**: **제3법칙 신규 추가**, 그리고 4개 신규 장 — **Ch11 모듈형 모놀리스**, **Ch20 아키텍처 패턴**, **Ch26 아키텍처 교차점**, **Ch27 법칙 재검토**. 생성형 AI가 아키텍처에 미치는 영향(Ch21·26)도 새로 반영됐다.

---

## 학습 가이드

### 처음 읽는 경우

**전체 순서대로 읽는 것을 권장**한다. Ch1으로 아키텍처의 정의와 아키텍트의 역할을 잡고, 제1부(Ch2-8)로 아키텍처 특성·모듈성·컴포넌트라는 어휘를 습득한 뒤, 제2부(Ch9-20)에서 다양한 스타일을 트레이드오프 관점으로 비교하고, 제3부(Ch21-27)에서 실전 기법과 소프트 스킬을 익힌다.

### 아키텍처 특성(품질 속성)이 궁금하다면

- Ch4 (특성 정의) → Ch5 (특성 식별) → Ch6 (측정·거버넌스) → Ch7 (특성 범위)

### 아키텍처 스타일을 비교하고 싶다면

- Ch9 (기초) → Ch10-18 (9가지 스타일) → Ch19 (스타일 선택) → Ch20 (패턴)
- 각 스타일 장의 **아키텍처 특성 등급표(별점 scorecard)** 로 트레이드오프를 한눈에 비교

### 아키텍트의 실전 스킬에 초점을 둔다면

- Ch21 (아키텍처 결정·ADR) → Ch22 (위험 분석·리스크스토밍) → Ch23 (도식화)
- Ch24 (유능한 팀) → Ch25 (협상·리더십) → Ch26 (교차점) → Ch27 (법칙 재검토)

---

## 전체 목차

### 서론

| Ch | 제목 | 핵심 |
|---|---|---|
| [1](ch01-introduction.md) | **Introduction (서론)** | 아키텍처의 4요소(구조·특성·결정·원칙), 아키텍트 8가지 기대치, 세 가지 법칙 |

### 제1부 — 기초 (Foundations)

아키텍처를 이해하는 데 필요한 기본 어휘와 개념.

| Ch | 제목 | 핵심 |
|---|---|---|
| [2](ch02-architectural-thinking.md) | **Architectural Thinking (아키텍처적 사고)** | 아키텍처 vs 설계 스펙트럼, 지식 피라미드, 깊이보다 너비 |
| [3](ch03-modularity.md) | **Modularity (모듈성)** | 결합·응집, **동변성(connascence)**(정적/동적), 세분도 |
| [4](ch04-defining-architecture-characteristics.md) | **아키텍처 특성의 정의** | 운영·구조·횡단 특성, 암묵/명시, "-성" 속성 |
| [5](ch05-identifying-architecture-characteristics.md) | **아키텍처 특성의 식별** | 비즈니스 요구 → 특성, 확장성 vs 탄력성, 복합 특성 |
| [6](ch06-measuring-and-governing-architecture-characteristics.md) | **특성의 측정과 거버넌스** | 순환 복잡도, **적합성 함수(fitness function)** |
| [7](ch07-scope-of-architecture-characteristics.md) | **아키텍처 특성의 범위** | **아키텍처 퀀텀**, 정적/동적 결합 |
| [8](ch08-component-based-thinking.md) | **컴포넌트 기반 사고** | 기술 분할 vs 도메인 분할, 엔티티 함정 |

### 제2부 — 아키텍처 스타일 (Architecture Styles)

각 스타일의 토폴로지·데이터·트레이드오프. 스타일 장에는 **아키텍처 특성 등급표(별점)** 포함.

| Ch | 제목 | 분할 | 핵심 |
|---|---|---|---|
| [9](ch09-foundations.md) | **아키텍처 스타일의 기초** | — | 분산 컴퓨팅의 오해, 모놀리스 vs 분산, 스코어카드 읽는 법 |
| [10](ch10-layered-architecture-style.md) | **Layered (계층형)** | 기술 | 닫힌 계층·격리, 싱크홀 안티패턴 |
| [11](ch11-modular-monolith-architecture-style.md) | **Modular Monolith (모듈형 모놀리스)** 🆕 | 도메인 | 도메인 모듈·단일 배포, 동급 간 vs 중재자 |
| [12](ch12-pipeline-architecture-style.md) | **Pipeline (파이프라인)** | 기술 | 파이프·필터(생산자·변환자·검사자·소비자) |
| [13](ch13-microkernel-architecture-style.md) | **Microkernel (마이크로커널)** | 기술/도메인 | 코어 + 플러그인, 커스텀화 격리 |
| [14](ch14-service-based-architecture-style.md) | **Service-Based (서비스 기반)** | 도메인 | 성긴 도메인 서비스, "가장 실용적인 분산" |
| [15](ch15-event-driven-architecture-style.md) | **Event-Driven (이벤트 주도)** | 기술 | 코레오그래피 vs 중재자, 이벤트 vs 메시지 |
| [16](ch16-space-based-architecture-style.md) | **Space-Based (공간 기반)** | 기술 | 처리 단위·데이터 그리드, 극한 확장성 |
| [17](ch17-orchestration-driven-service-oriented-architecture.md) | **Orchestration-Driven SOA** | 기술 | 서비스 분류 체계, 재사용의 재앙(역사적 교훈) |
| [18](ch18-microservices-architecture-style.md) | **Microservices (마이크로서비스)** | 도메인 | 경계 컨텍스트·무공유, 사가·사이드카 |
| [19](ch19-choosing-the-appropriate-architecture-style.md) | **적절한 스타일 선택** | — | 결정 기준, 동형성, 모놀리스 vs 분산 |
| [20](ch20-architectural-patterns.md) | **Architectural Patterns (아키텍처 패턴)** 🆕 | — | 육각형·서비스 메시, 오케/코레오, CQRS, 브로커 |

### 제3부 — 기법과 소프트 스킬 (Techniques and Soft Skills)

| Ch | 제목 | 핵심 |
|---|---|---|
| [21](ch21-architecture-decisions.md) | **Architecture Decisions (아키텍처적 결정)** | 세 안티패턴, **ADR**, 생성형 AI |
| [22](ch22-analyzing-architecture-risk.md) | **아키텍처 위험 분석** | 위험 평가 행렬·표, **리스크스토밍** |
| [23](ch23-diagramming-architecture.md) | **아키텍처 도식화** | 표현 일관성, UML·C4·ArchiMate |
| [24](ch24-making-teams-effective.md) | **유능한 팀 만들기** | 아키텍트 성향, 탄력적 리더십, 체크리스트 |
| [25](ch25-negotiation-and-leadership-skills.md) | **협상과 리더십 스킬** | 협상 기법, 4C, 솔선수범 |
| [26](ch26-architecture-intersections.md) | **Architecture Intersections (아키텍처 교차점)** 🆕 | 9개 교차점(구현·인프라·데이터·팀·비즈니스·AI 등) |
| [27](ch27-software-architecture-laws-revisited.md) | **법칙 재검토** 🆕 | 세 법칙 종합, 트레이드오프 분석, 마지막 조언 |

### 부록

| 부록 | 제목 | 핵심 |
|---|---|---|
| [A](appendix-a-discussion-questions.md) | **토론용 질문 모음** | 장별 자율평가 질문 (27개 장) |

---

## 아홉 가지 아키텍처 스타일 한눈에 보기

| 스타일 | 강점(별 4~5) | 약점(별 1~2) | 언제 |
|---|---|---|---|
| 계층형 | 단순성·비용 | 확장성·탄력성·내결함성 | 작고 단순한 앱, 빠른 시작 |
| 모듈형 모놀리스 | 모듈성·유지보수성·비용 | 확장성·내결함성·탄력성 | 도메인 분리를 원하나 분산은 부담일 때 |
| 파이프라인 | 단순성·비용 | 확장성·내결함성 | 데이터 변환·ETL·단방향 처리 |
| 마이크로커널 | 단순성·비용 | 확장성·탄력성·내결함성 | 제품·커스텀화(IDE·세무·보험) |
| 서비스 기반 | 비용·단순성·민첩성·내결함성 | 확장성·탄력성 | 실용적 분산, 마이크로서비스 디딤돌 |
| 이벤트 주도 | 성능·확장성·탄력성·내결함성·진화성 | 단순성·테스트성 | 고성능·고확장, 비동기 반응 |
| 공간 기반 | 성능·확장성·탄력성·반응성 | 단순성·테스트성·비용 | 극한·가변 고부하(티켓·경매) |
| 오케스트레이션 SOA | (확장성·탄력성 어느 정도) | 대부분 낮음 | (역사적) 통합 아키텍처엔 ESB 유효 |
| 마이크로서비스 | 배포성·테스트성·내결함성·확장성·탄력성·진화성 | 성능·단순성·비용 | 도메인 분리·클라우드 네이티브 |

---

## 시그니처 요소와 표기 규칙

- **소프트웨어 아키텍처 법칙**: `> **소프트웨어 아키텍처 제N법칙**<br>내용` 형식 (이 책의 시그니처)
- **아키텍처 특성 등급표(별점 scorecard)**: 스타일 장(Ch10·12-18)마다 13개 특성(분할 방식·퀀텀 수·성능·확장성·탄력성·반응성·내결함성·모듈성·배포성·진화성·유지보수성·비용·단순성·테스트성)을 ★로 평가
  - ⚠️ **별점 재구성 주의**: 원본 OCR의 별점 격자표가 훼손되어, 각 스타일 장의 등급표는 **본문 서술에 근거해 재구성**했다(각 장 등급표 아래 `> **참고**` 주석으로 명시). 정확한 별점은 원서를 확인할 것
- **핵심 통찰**: `> **핵심 통찰**:` 콜아웃(Notion 업로드 시 💡 콜아웃 블록으로 변환)
- **외부 인용**: 레이블 없는 `> 인용문<br>— 이름` (닐 포드·프레드 브룩스·마틴 파울러·제럴드 와인버그 등)

---

## 자매판

- **[fundamentals-of-software-architecture-1st-edition/](../fundamentals-of-software-architecture-1st-edition/)** — 1판 『소프트웨어 아키텍처 101』 (24장 + 부록A). 1판은 `:::` 콜아웃 스타일, 2판은 `>` blockquote 스타일 사용
