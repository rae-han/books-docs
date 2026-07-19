# 클린 아키텍처 (Clean Architecture: A Craftsman's Guide to Software Structure and Design)

> *Clean Architecture: A Craftsman's Guide to Software Structure and Design* (Robert C. Martin, Prentice Hall, 2017)
> 한국어판: 『클린 아키텍처 — 소프트웨어 구조와 설계의 원칙』 (송준이 옮김, 인사이트, 2019)

소프트웨어 아키텍처의 보편적 원칙을 다루는 책. 같은 저자의 『클린 코드』가 코드 수준의 품질에 집중한다면, 이 책은 **시스템 수준의 구조와 설계**에 집중한다.

## 책 정보

| 항목 | 내용 |
|------|------|
| **저자** | 로버트 C. 마틴(Robert C. Martin, Uncle Bob) |
| **역자** | 송준이 |
| **출판** | 인사이트, 2019 (원서: Prentice Hall, 2017) |
| **구성** | 6부 34장 + 부록(아키텍처 고고학) |
| **대상 독자** | 시스템 설계를 이해하고 싶은 개발자·아키텍트 |

## 개요

Uncle Bob이 1970년부터 축적한 50년 가까운 경험에서 추출한 아키텍처 원칙을 제시한다. 핵심 전제는 단순하다 — **소프트웨어 아키텍처의 목표는 필요한 시스템을 만들고 유지보수하는 데 투입되는 인력을 최소화하는 것**이다.

특정 언어·프레임워크에 종속되지 않는 불변의 원칙(SOLID, 컴포넌트 원칙, 경계 설계)을 다루며, 모든 내용이 **의존성 규칙**(소스 코드 의존성은 반드시 안쪽, 고수준 정책을 향한다) 하나로 수렴한다. 부록에서는 1970~90년대 프로젝트를 회고하며 원칙이 실패와 성공의 경험에서 어떻게 귀납적으로 도출됐는지 보여준다. 『클린 코드』(코드) → 『클린 코더』(태도) → 『클린 아키텍처』(구조)로 이어지는 시리즈의 세 번째 책이다.

## 목차

### Part 1: 소개 (Ch 1-2)

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 1 | [What Is Design and Architecture?](ch01-what-is-design-and-architecture.md) | 설계 = 아키텍처 · 엉망진창의 비용 | 설계와 아키텍처는 같은 것 — 좋은 아키텍처의 목표는 인력 최소화 |
| 2 | [A Tale of Two Values](ch02-a-tale-of-two-values.md) | 행위 vs 구조 · 아이젠하워 매트릭스 | 행위(긴급)보다 구조(중요)가 더 높은 가치 — 아키텍처를 위해 투쟁하라 |

### Part 2: 벽돌부터 시작하기 — 프로그래밍 패러다임 (Ch 3-6)

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 3 | [Paradigm Overview](ch03-paradigm-overview.md) | 세 패러다임 | 각 패러다임은 무언가를 '빼앗는' 규율이다 |
| 4 | [Structured Programming](ch04-structured-programming.md) | 구조적 프로그래밍 · goto 제거 | 직접적 제어 이동에 부과된 규율 — 테스트 가능한 단위의 토대 |
| 5 | [Object-Oriented Programming](ch05-object-oriented-programming.md) | 다형성 · 의존성 역전 | OOP의 본질은 다형성 — 의존성 방향을 마음대로 제어하는 힘 |
| 6 | [Functional Programming](ch06-functional-programming.md) | 불변성 · 가변성 분리 | 변수 할당에 부과된 규율 — 경합·교착의 근원 제거 |

### Part 3: 설계 원칙 (Ch 7-11) — SOLID

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 7 | [SRP: The Single Responsibility Principle](ch07-srp-the-single-responsibility-principle.md) | 단일 책임 원칙 · 액터 | 모듈은 하나의 액터에 대해서만 책임진다 — 함수 하나의 얘기가 아니다 |
| 8 | [OCP: The Open-Closed Principle](ch08-ocp-the-open-closed-principle.md) | 개방-폐쇄 원칙 · 방향성 제어 | 확장에 열리고 수정에 닫히게 — 컴포넌트 계층으로 보호하라 |
| 9 | [LSP: The Liskov Substitution Principle](ch09-lsp-the-liskov-substitution-principle.md) | 리스코프 치환 원칙 · 정사각형/직사각형 | 치환 가능성 — 위반하면 상위 수준에 조건문이 오염된다 |
| 10 | [ISP: The Interface Segregation Principle](ch10-isp-the-interface-segregation-principle.md) | 인터페이스 분리 원칙 | 사용하지 않는 것에 의존하지 마라 |
| 11 | [DIP: The Dependency Inversion Principle](ch11-dip-the-dependency-inversion-principle.md) | 의존성 역전 · 추상 팩토리 | 추상화에 의존하라 — 제어 흐름과 의존 방향의 분리 |

### Part 4: 컴포넌트 원칙 (Ch 12-14)

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 12 | [Components](ch12-components.md) | 컴포넌트 · 배포 단위의 역사 | 컴포넌트 = 배포 단위 — 링커·라이브러리의 역사에서 배우기 |
| 13 | [Component Cohesion](ch13-component-cohesion.md) | REP · CCP · CRP | 어떤 클래스를 한 컴포넌트로 묶나 — 응집 3원칙의 장력 |
| 14 | [Component Coupling](ch14-component-coupling.md) | ADP · SDP · SAP · 메인 시퀀스 | 컴포넌트 간 관계 — 순환 금지·안정 방향 의존·안정=추상 |

### Part 5: 아키텍처 (Ch 15-29)

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 15 | [What Is Architecture?](ch15-what-is-architecture.md) | 아키텍처 정의 · 선택지 보존 | 좋은 아키텍처는 결정을 미룰 수 있게 한다 |
| 16 | [Independence](ch16-independence.md) | 독립성 · 유스케이스/개발/배포 분리 | 수직·수평 분리로 유스케이스와 팀·배포의 독립성 확보 |
| 17 | [Boundaries: Drawing Lines](ch17-boundaries-drawing-lines.md) | 경계 · 플러그인 아키텍처 | 어디에 선을 긋는가 — 업무 규칙과 세부사항 사이 |
| 18 | [Boundary Anatomy](ch18-boundary-anatomy.md) | 경계 형태 · 배포/스레드/프로세스/서비스 | 경계 횡단의 물리적 형태들 |
| 19 | [Policy and Level](ch19-policy-and-level.md) | 정책 · 수준 | 수준 = 입력과 출력으로부터의 거리 — 고수준일수록 안쪽 |
| 20 | [Business Rules](ch20-business-rules.md) | 엔티티 · 유스케이스 | 핵심 업무 규칙(엔티티)과 애플리케이션 규칙(유스케이스)의 구분 |
| 21 | [Screaming Architecture](ch21-screaming-architecture.md) | 소리치는 아키텍처 | 아키텍처는 프레임워크가 아니라 유스케이스를 소리쳐야 한다 |
| 22 | [The Clean Architecture](ch22-the-clean-architecture.md) | 의존성 규칙 · 동심원 · 경계 횡단 | 이 책의 중심 — 엔티티→유스케이스→어댑터→프레임워크 동심원 |
| 23 | [Presenters and Humble Objects](ch23-presenters-and-humble-objects.md) | 험블 객체 · 프레젠터 | 테스트하기 어려운 부분을 얇게 — 험블 객체 패턴 |
| 24 | [Partial Boundaries](ch24-partial-boundaries.md) | 부분적 경계 | 완전한 경계는 비싸다 — 부분 경계 전략 3가지 |
| 25 | [Layers and Boundaries](ch25-layers-and-boundaries.md) | 계층과 경계 · 움퍼스 사냥 게임 | 경계는 어디에나 있을 수 있다 — 비용과 저울질하라 |
| 26 | [The Main Component](ch26-the-main-component.md) | 메인 컴포넌트 | Main은 가장 바깥의 가장 지저분한 컴포넌트 — 궁극의 세부사항 |
| 27 | [Services: Great and Small](ch27-services-great-and-small.md) | 서비스 · 마이크로서비스 비판 | 서비스 분리 자체는 아키텍처가 아니다 — 경계가 아키텍처다 |
| 28 | [The Test Boundary](ch28-the-test-boundary.md) | 테스트 경계 · 테스트 API | 테스트도 시스템 컴포넌트 — 깨지기 쉬운 테스트 문제 |
| 29 | [Clean Embedded Architecture](ch29-clean-embedded-architecture.md) | 임베디드 · HAL/OSAL | 펌웨어를 줄이고 하드웨어를 세부사항으로 |

### Part 6: 세부사항 (Ch 30-34)

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 30 | [The Database Is a Detail](ch30-the-database-is-a-detail.md) | 데이터베이스 = 세부사항 | 데이터 모델은 중요하지만 DB 기술은 세부사항이다 |
| 31 | [The Web Is a Detail](ch31-the-web-is-a-detail.md) | 웹 = 세부사항 · GUI 진자 | UI 기술은 반복 진동해 왔다 — 웹도 IO 장치일 뿐 |
| 32 | [Frameworks Are Details](ch32-frameworks-are-details.md) | 프레임워크 = 세부사항 · 비대칭 결혼 | 프레임워크와 결혼하지 마라 — 일방적 헌신의 위험 |
| 33 | [Case Study: Video Sales](ch33-case-study-video-sales.md) | 사례 연구 · 컴포넌트 다이어그램 | 비디오 판매 시스템으로 원칙 종합 적용 |
| 34 | [The Missing Chapter](ch34-the-missing-chapter.md) | 패키지 구조 · 구현 세부사항 (Simon Brown) | 계층/기능/포트와 어댑터/컴포넌트 기준 패키징 — 구현이 따라주지 않으면 무너진다 |

### 부록

| 부록 | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| A | [Architecture Archaeology](appendix-architecture-archaeology.md) | 아키텍처 고고학 | Uncle Bob 45년 프로젝트 회고 — 원칙이 도출된 경험들 |

## 학습 가이드

1. **1단계 (Ch1~2)**: 문제 인식 — 행위보다 구조가 높은 가치라는 핵심 논증
2. **2단계 (Ch3~6)**: 패러다임 — 특히 Ch5의 "다형성 = 의존성 역전의 메커니즘"이 이후 전부의 기반
3. **3단계 (Ch7~11)**: SOLID — 모듈 수준의 벽돌 규격
4. **4단계 (Ch12~14)**: 컴포넌트 원칙 — 벽돌을 벽으로 (REP·CCP·CRP / ADP·SDP·SAP)
5. **5단계 (Ch15~29)**: 아키텍처 본론 — **Ch22(클린 아키텍처)가 중심**, 경계·정책·험블 객체
6. **6단계 (Ch30~34)**: 세부사항 — DB·웹·프레임워크를 플러그인으로 다루는 법 + 사례 연구
7. **부록**: 원칙이 나온 역사적 맥락

## 핵심 개념 맵

모든 내용은 하나의 규칙으로 수렴한다 — **의존성 규칙: 소스 코드 의존성은 반드시 안쪽으로, 고수준 정책을 향해야 한다.**

### 모듈 수준: SOLID 원칙

| 원칙 | 의미 | 한 줄 요약 |
|------|------|-----------|
| **SRP** | 단일 책임 원칙 | 모듈은 하나의 액터(*actor - 변경을 요청하는 사람 또는 그룹*)에 대해서만 책임진다 |
| **OCP** | 개방-폐쇄 원칙 | 확장에는 열려 있고, 수정에는 닫혀 있어야 한다 |
| **LSP** | 리스코프 치환 원칙 | 하위 타입은 상위 타입을 대체할 수 있어야 한다 |
| **ISP** | 인터페이스 분리 원칙 | 사용하지 않는 것에 의존하지 말아야 한다 |
| **DIP** | 의존성 역전 원칙 | 추상화에 의존해야지, 구체화에 의존하면 안 된다 |

### 컴포넌트 수준: 6가지 원칙

| 범주 | 원칙 | 한 줄 요약 |
|------|------|-----------|
| 응집도 | **REP** | 재사용 단위는 릴리스 단위다 |
| 응집도 | **CCP** | 같은 이유로 변경되는 클래스는 같은 컴포넌트에 |
| 응집도 | **CRP** | 함께 사용되지 않는 클래스는 같은 컴포넌트에 넣지 마라 |
| 결합 | **ADP** | 컴포넌트 의존성 그래프에 순환이 있으면 안 된다 |
| 결합 | **SDP** | 안정성이 높은 방향으로 의존하라 |
| 결합 | **SAP** | 안정된 컴포넌트는 추상적이어야 한다 |

### 아키텍처 수준: 클린 아키텍처 동심원

| 계층 | 포함 요소 | 변경 빈도 |
|------|----------|----------|
| **엔티티** | 핵심 업무 규칙, 핵심 업무 데이터 | 가장 낮음 |
| **유스케이스** | 애플리케이션 업무 규칙 | 낮음 |
| **인터페이스 어댑터** | 컨트롤러, 프레젠터, 게이트웨이 | 중간 |
| **프레임워크와 드라이버** | 웹, DB, UI, 외부 인터페이스 | 가장 높음 |

세부사항(데이터베이스·웹·프레임워크)은 **플러그인**처럼 교체 가능해야 하며, 업무 규칙은 이들에 대해 아무것도 알지 못해야 한다.

## 인용문

전 책 통합 모음은 [루트 QUOTES.md](../QUOTES.md) 참조.

> 소프트웨어 아키텍처의 목표는 필요한 시스템을 만들고 유지보수하는 데 투입되는 인력을 최소화하는 데 있다.<br>— 로버트 C. 마틴 (위치: Ch1)

> 내겐 두 가지 유형의 문제가 있습니다. 하나는 긴급하며, 다른 하나는 중요합니다. 긴급한 문제는 중요하지 않으며, 중요한 문제는 절대 긴급하지 않습니다.<br>— 드와이트 D. 아이젠하워, 1954년 노스웨스턴 대학교 강연 (위치: Ch2)

> 소프트웨어를 제대로 만들게 되면 마법과도 같은 일이 벌어진다. … 제대로 된 소프트웨어를 만들면 아주 적은 인력만으로도 새로운 기능을 추가하거나 유지보수할 수 있다. 변경은 단순해지고 빠르게 반영할 수 있다. 결함은 적어지고 잦아든다. 최소한의 노력으로 기능과 유연성을 최대화할 수 있다.<br>— 로버트 C. 마틴 (위치: 서문)

> 각 패러다임은 프로그래머에게서 권한을 박탈한다. 어느 패러다임도 새로운 권한을 부여하지 않는다. 패러다임은 무엇을 해야 할지를 말하기보다는 무엇을 해서는 안 되는지를 말해준다.<br>— 로버트 C. 마틴 (위치: Ch3)

## 시그니처 요소와 표기 규칙

- `> **핵심 통찰**:` 콜아웃, 레이블 없는 `>` 인용문(Uncle Bob의 프로젝트 회고)
- 의존성 방향을 표현하는 ASCII 다이어그램(컴포넌트·경계 횡단)

## origin 분리

- `0~35, 99` = 37개 파일 (0=서문/목차/추천사, 1~34=1장~34장 — 부 표지는 각 부 첫 챕터 파일 맨 앞, 35=부록A, 99=찾아보기). 원본 11,764줄 = 합계 일치
- 페이지 번호: 부분 캡처·형식 혼재로 순차 검증 생략, 라인 합계로 무결성 확인
