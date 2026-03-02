# Clean Architecture

**저자**: Robert C. Martin (Uncle Bob)
**출판**: 2017, Prentice Hall / 한국어판 2019, 인사이트

---

## 책 소개

"Clean Architecture: A Craftsman's Guide to Software Structure and Design"은 소프트웨어 아키텍처의 보편적 원칙을 다루는 책이다. 같은 저자의 "Clean Code"가 코드 수준의 품질에 집중한다면, 이 책은 **시스템 수준의 구조와 설계**에 집중한다.

Robert C. Martin(Uncle Bob)은 1970년부터 축적한 50년 가까운 소프트웨어 개발 경험에서 추출한 아키텍처 원칙을 제시한다. 이 책의 핵심 전제는 단순하다:

> **소프트웨어 아키텍처의 목표는 필요한 시스템을 만들고 유지보수하는 데 투입되는 인력을 최소화하는 데 있다.**

### 이 책의 특징

- **보편적 원칙**: 특정 언어, 프레임워크, 플랫폼에 종속되지 않는 아키텍처의 불변 원칙을 다룬다. SOLID 원칙, 컴포넌트 원칙, 경계 설계가 핵심이다.
- **의존성 규칙**: 소스 코드 의존성은 반드시 안쪽으로, 고수준 정책을 향해야 한다는 단 하나의 규칙으로 모든 아키텍처 원칙을 통합한다.
- **경험에서 나온 교훈**: 부록에서 1970년대부터 1990년대까지의 프로젝트를 회고하며, 원칙이 어떻게 실패와 성공의 경험에서 귀납적으로 도출되었는지를 보여준다.
- **실용적 관점**: 이론뿐 아니라 세부사항(데이터베이스, 웹, 프레임워크)을 어떻게 다뤄야 하는지, 실제 사례 연구를 통해 아키텍처를 어떻게 적용하는지를 구체적으로 제시한다.

### Clean Code vs Clean Architecture

| 구분 | Clean Code (2008) | Clean Architecture (2017) |
|------|-------------------|---------------------------|
| 핵심 주제 | 깨끗한 **코드** 작성법 | 깨끗한 **시스템 구조** 설계법 |
| 다루는 범위 | 변수명, 함수, 클래스, 테스트 | 컴포넌트, 경계, 의존성, 배포 |
| 대상 독자 | 코드 품질을 높이고 싶은 개발자 | 시스템 설계를 이해하고 싶은 개발자/아키텍트 |
| 핵심 질문 | "좋은 코드란 무엇인가?" | "좋은 아키텍처란 무엇인가?" |
| 핵심 원칙 | 이름, 함수, 주석, 포맷팅 | SOLID, 컴포넌트 원칙, 의존성 규칙 |

---

## 이 저장소의 목적

이 저장소는 "Clean Architecture"의 내용을 챕터별로 상세하게 정리한 학습 자료이다. 각 챕터의 핵심 원칙, 코드 예시, 다이어그램을 책을 대체할 수 있을 정도로 충실하게 담고 있으며, 다음과 같은 용도로 활용할 수 있다:

- 소프트웨어 아키텍처의 보편적 원칙을 체계적으로 학습하는 교재
- 시스템 설계 시 의존성과 경계를 판단하는 기준으로 참조하는 가이드
- 팀 내 아키텍처 토론과 스터디 자료

---

## 목차

### Part 1: 소개

- [Chapter 1: What Is Design and Architecture? (설계와 아키텍처란?)](ch01-what-is-design-and-architecture.md)
- [Chapter 2: A Tale of Two Values (두 가지 가치에 대한 이야기)](ch02-a-tale-of-two-values.md)

### Part 2: 벽돌부터 시작하기: 프로그래밍 패러다임

- [Chapter 3: Paradigm Overview (패러다임 개요)](ch03-paradigm-overview.md)
- [Chapter 4: Structured Programming (구조적 프로그래밍)](ch04-structured-programming.md)
- [Chapter 5: Object-Oriented Programming (객체 지향 프로그래밍)](ch05-object-oriented-programming.md)
- [Chapter 6: Functional Programming (함수형 프로그래밍)](ch06-functional-programming.md)

### Part 3: 설계 원칙

- [Chapter 7: SRP: The Single Responsibility Principle (단일 책임 원칙)](ch07-srp-the-single-responsibility-principle.md)
- [Chapter 8: OCP: The Open-Closed Principle (개방-폐쇄 원칙)](ch08-ocp-the-open-closed-principle.md)
- [Chapter 9: LSP: The Liskov Substitution Principle (리스코프 치환 원칙)](ch09-lsp-the-liskov-substitution-principle.md)
- [Chapter 10: ISP: The Interface Segregation Principle (인터페이스 분리 원칙)](ch10-isp-the-interface-segregation-principle.md)
- [Chapter 11: DIP: The Dependency Inversion Principle (의존성 역전 원칙)](ch11-dip-the-dependency-inversion-principle.md)

### Part 4: 컴포넌트 원칙

- [Chapter 12: Components (컴포넌트)](ch12-components.md)
- [Chapter 13: Component Cohesion (컴포넌트 응집도)](ch13-component-cohesion.md)
- [Chapter 14: Component Coupling (컴포넌트 결합)](ch14-component-coupling.md)

### Part 5: 아키텍처

- [Chapter 15: What Is Architecture? (아키텍처란?)](ch15-what-is-architecture.md)
- [Chapter 16: Independence (독립성)](ch16-independence.md)
- [Chapter 17: Boundaries: Drawing Lines (경계: 선 긋기)](ch17-boundaries-drawing-lines.md)
- [Chapter 18: Boundary Anatomy (경계 해부학)](ch18-boundary-anatomy.md)
- [Chapter 19: Policy and Level (정책과 수준)](ch19-policy-and-level.md)
- [Chapter 20: Business Rules (업무 규칙)](ch20-business-rules.md)
- [Chapter 21: Screaming Architecture (소리치는 아키텍처)](ch21-screaming-architecture.md)
- [Chapter 22: The Clean Architecture (클린 아키텍처)](ch22-the-clean-architecture.md)
- [Chapter 23: Presenters and Humble Objects (프레젠터와 험블 객체)](ch23-presenters-and-humble-objects.md)
- [Chapter 24: Partial Boundaries (부분적 경계)](ch24-partial-boundaries.md)
- [Chapter 25: Layers and Boundaries (계층과 경계)](ch25-layers-and-boundaries.md)
- [Chapter 26: The Main Component (메인 컴포넌트)](ch26-the-main-component.md)
- [Chapter 27: Services: Great and Small (서비스: 크고 작은 모든)](ch27-services-great-and-small.md)
- [Chapter 28: The Test Boundary (테스트 경계)](ch28-the-test-boundary.md)
- [Chapter 29: Clean Embedded Architecture (클린 임베디드 아키텍처)](ch29-clean-embedded-architecture.md)

### Part 6: 세부사항

- [Chapter 30: The Database Is a Detail (데이터베이스는 세부사항이다)](ch30-the-database-is-a-detail.md)
- [Chapter 31: The Web Is a Detail (웹은 세부사항이다)](ch31-the-web-is-a-detail.md)
- [Chapter 32: Frameworks Are Details (프레임워크는 세부사항이다)](ch32-frameworks-are-details.md)
- [Chapter 33: Case Study: Video Sales (사례 연구: 비디오 판매)](ch33-case-study-video-sales.md)
- [Chapter 34: The Missing Chapter (빠져 있는 장)](ch34-the-missing-chapter.md)

### Part 7: 부록

- [Appendix A: Architecture Archaeology (아키텍처 고고학)](appendix-architecture-archaeology.md)

---

## 학습 가이드

### 추천 읽기 순서

이 책은 앞에서 뒤로 순서대로 읽는 것이 자연스럽다. 각 파트의 개념이 이전 파트 위에 쌓이기 때문이다. 하지만 이미 설계 경험이 있는 개발자라면 관심 분야부터 읽어도 된다.

**1단계: 문제 인식 — 왜 아키텍처가 중요한가 (Chapter 1~2)**

소프트웨어 아키텍처의 목표와 가치를 이해한다. "설계와 아키텍처는 같다"는 전제와, 행위(behavior)보다 구조(architecture)가 더 높은 가치를 가진다는 핵심 논증을 먼저 파악한다. 이후 모든 원칙의 근거가 되므로 반드시 먼저 읽는다.

**2단계: 프로그래밍 패러다임 — 아키텍처의 토대 (Chapter 3~6)**

세 가지 프로그래밍 패러다임(구조적, 객체지향, 함수형)이 아키텍처에 어떤 의미를 가지는지를 다룬다. 특히 Chapter 5의 다형성이 의존성 역전의 핵심 메커니즘이라는 점은 이후 모든 내용의 기반이 된다.

**3단계: SOLID 설계 원칙 — 벽돌의 규격 (Chapter 7~11)**

모듈 수준의 다섯 가지 설계 원칙을 다룬다. SRP, OCP, LSP, ISP, DIP는 이 책의 가장 기초적인 원칙이며, 이후 컴포넌트 원칙과 아키텍처 원칙의 토대다.

**4단계: 컴포넌트 원칙 — 벽돌을 벽으로 (Chapter 12~14)**

모듈을 컴포넌트로 묶는 원칙(응집도)과 컴포넌트 간 관계를 관리하는 원칙(결합)을 다룬다. REP, CCP, CRP, ADP, SDP, SAP 등 여섯 가지 컴포넌트 원칙은 실제 시스템 설계에서 직접 활용되는 도구다.

**5단계: 아키텍처 — 전체 그림 (Chapter 15~29)**

이 책의 핵심이다. 아키텍처의 정의, 경계 설계, 의존성 규칙, 클린 아키텍처 패턴, 그리고 이를 서비스, 테스트, 임베디드 시스템에 적용하는 방법을 다룬다. 특히 Chapter 22(클린 아키텍처)는 이 책의 가장 중심적인 내용이다.

**6단계: 세부사항과 실전 — 현실 적용 (Chapter 30~34)**

데이터베이스, 웹, 프레임워크가 왜 "세부사항"인지를 설명하고, 사례 연구와 실제 코드 구조를 통해 아키텍처를 적용하는 방법을 보여준다. Chapter 34는 다른 저자(Simon Brown)가 패키지 구조와 아키텍처의 관계를 다룬 보충 챕터다.

**7단계: 부록 — 역사적 맥락 (Appendix A)**

Uncle Bob의 45년 경력을 아키텍처 관점에서 회고한다. 이론이 아닌 경험에서 원칙이 어떻게 도출되었는지를 이해하는 데 도움이 된다.

---

## 핵심 개념 요약

이 책의 모든 내용은 하나의 중심 규칙으로 수렴한다:

> **의존성 규칙(The Dependency Rule): 소스 코드 의존성은 반드시 안쪽으로, 고수준 정책을 향해야 한다.**

이를 달성하기 위해 Uncle Bob이 제시하는 핵심 원칙들을 계층별로 정리하면 다음과 같다:

### 모듈 수준: SOLID 원칙

| 원칙 | 의미 | 한 줄 요약 |
|------|------|-----------|
| **SRP** | 단일 책임 원칙 | 모듈은 하나의 액터(*actor — 변경을 요청하는 사람 또는 그룹. SRP에서 "책임"은 코드가 아니라 이 액터에 의해 정의된다.*)에 대해서만 책임진다 |
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

### 아키텍처 수준: 클린 아키텍처

클린 아키텍처는 동심원 구조로, 안쪽이 고수준 정책(엔티티, 유스케이스)이고 바깥쪽이 세부사항(UI, 데이터베이스, 프레임워크)이다. 핵심 규칙은 단 하나다 — **의존성은 반드시 안쪽을 향해야 한다.** 바깥쪽의 어떤 것도 안쪽에 영향을 주어서는 안 된다.

| 계층 | 포함 요소 | 변경 빈도 |
|------|----------|----------|
| **엔티티** | 핵심 업무 규칙, 핵심 업무 데이터 | 가장 낮음 |
| **유스케이스** | 애플리케이션 업무 규칙 | 낮음 |
| **인터페이스 어댑터** | 컨트롤러, 프레젠터, 게이트웨이 | 중간 |
| **프레임워크와 드라이버** | 웹, DB, UI, 외부 인터페이스 | 가장 높음 |

세부사항(데이터베이스, 웹, 프레임워크)은 **플러그인**처럼 교체 가능해야 하며, 업무 규칙은 이들 세부사항에 대해 아무것도 알지 못해야 한다.
