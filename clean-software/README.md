# 클린 소프트웨어: 애자일 원칙, 패턴, 그리고 실천 방법

> *Agile Software Development, Principles, Patterns, and Practices* (Robert C. Martin, 2003)
> 한국어판: 『클린 소프트웨어』 (이용원/김정민/정지호 옮김, 제이펍, 2017)

Uncle Bob (Robert C. Martin) 의 객체지향 설계 고전. 애자일 실천 방법부터 시작해 SOLID 원칙, 패키지 설계 원칙, 디자인 패턴, 그리고 세 가지 실제 사례 연구(급여 관리, 기상 관측기, ETS 시험 시스템)로 이어진다. 이 노트는 책 없이도 핵심 개념을 학습할 수 있을 정도로 상세하게 정리한 한국어 학습 노트다.

---

## 책의 핵심 메시지

> **소프트웨어 설계는 단번에 완성되지 않는다.** 변화를 두려워하지 않고, 변화가 일어날 때 그것을 신호로 삼아 점진적으로 개선하는 것이 진정한 설계다.

- **잭 리브스의 통찰**: 소스 코드가 곧 설계 문서다. UML 다이어그램은 스케치일 뿐이다.
- **애자일의 마라톤**: 빠르지만 지속 가능한 속도로, 매번 동작하는 소프트웨어를 만든다.
- **SOLID**: 변경에 강한 객체지향 설계의 다섯 가지 핵심 원칙.
- **패턴은 시작이 아니라 도착점**: 좋은 설계는 사전에 적용하는 것이 아니라 변경의 필요에 따라 도달하는 것이다.

---

## 학습 가이드

이 책은 6개의 PART로 구성되어 있다. 권장 학습 순서:

### 처음 읽는 경우
**전체 순서대로 읽는 것을 권장**한다. PART 1에서 애자일 가치관을 잡고, PART 2에서 SOLID로 설계의 어휘를 습득한 다음, PART 3~6에서 실제 사례를 따라가면서 패턴이 자연스럽게 등장하는 과정을 경험할 수 있다.

### 빠르게 핵심만 보고 싶다면
1. Ch1 (애자일 실천 방법) — 애자일 12가지 원칙
2. Ch7 (애자일 설계란?) — 7가지 설계 악취
3. Ch8~Ch12 (SOLID 5원칙)
4. Ch20 (패키지 설계 6원칙)
5. Appendix D (소스 코드는 곧 설계다)

### SOLID 만 보고 싶다면
- Ch7 (설계 악취) → Ch8 (SRP) → Ch9 (OCP) → Ch10 (LSP) → Ch11 (DIP) → Ch12 (ISP)

### 패턴만 보고 싶다면
- Ch13 (Command) / Ch14 (Template Method, Strategy) / Ch15 (Facade, Mediator)
- Ch16 (Singleton, Monostate) / Ch17 (Null Object) / Ch21 (Factory)
- Ch23 (Composite) / Ch24 (Observer) / Ch25 (Adapter, Bridge) / Ch26 (Proxy)
- Ch28 (Visitor 패밀리) / Ch29 (State)

---

## 전체 목차

### PART 1 — 애자일 개발

소프트웨어 개발에서 "민첩함"이 무엇을 의미하는지, 그리고 그것이 실제 개발 실천 방법에 어떻게 녹아드는지 다룬다.

| Ch | 제목 | 핵심 |
|---|---|---|
| [1](ch01-agile-practices.md) | **Agile Practices (애자일 실천 방법)** | 애자일 선언문 4가지 가치 + 12가지 원칙. 프로세스 악순환을 깨는 법 |
| [2](ch02-extreme-programming-overview.md) | **Extreme Programming Overview (XP 소개)** | XP 12가지 실천 방법: 짝 프로그래밍, TDD, 단순 설계, 지속적 통합, 리팩토링 등 |
| [3](ch03-planning.md) | **Planning (계획 세우기)** | 초기 탐색, 스토리 포인트, 속도(velocity), 릴리즈/반복/태스크 3단계 계획 |
| [4](ch04-testing.md) | **Testing (테스트)** | TDD는 검증이 아닌 설계 활동. 단위 테스트와 인수 테스트 |
| [5](ch05-refactoring.md) | **Refactoring (리팩토링)** | 동작 변경 없는 구조 개선. 소수 생성기 단계별 리팩토링 |
| [6](ch06-programming-episode.md) | **A Programming Episode (프로그래밍 에피소드)** | 볼링 게임 TDD 실전 — UML이 사라지고 Scorer가 등장하는 과정 |

### PART 2 — 애자일 설계

설계는 한 번에 완성되지 않는다. 어떤 신호가 설계의 부패를 알려주고, 어떤 원칙으로 부패를 막을 수 있는가.

| Ch | 제목 | 핵심 |
|---|---|---|
| [7](ch07-what-is-agile-design.md) | **What Is Agile Design? (애자일 설계란?)** | 설계 7가지 악취: 경직성/취약성/부동성/점착성/불필요한 복잡성/반복/불투명성 |
| [8](ch08-single-responsibility-principle.md) | **SRP (단일 책임 원칙)** | 한 클래스는 단 한 가지의 변경 이유만을 가져야 한다 |
| [9](ch09-open-closed-principle.md) | **OCP (개방-폐쇄 원칙)** | 확장에는 열려, 수정에는 닫혀 — 추상화로 확장 가능성을 확보 |
| [10](ch10-liskov-substitution-principle.md) | **LSP (리스코프 치환 원칙)** | 서브타입은 기본 타입과 치환 가능해야 한다. IS-A는 행위에 관한 것 |
| [11](ch11-dependency-inversion-principle.md) | **DIP (의존 관계 역전 원칙)** | 상위 모듈은 하위에 의존하지 않고, 둘 다 추상화에 의존한다 |
| [12](ch12-interface-segregation-principle.md) | **ISP (인터페이스 분리 원칙)** | 클라이언트는 자신이 사용하지 않는 메서드에 의존해서는 안 된다 |

### PART 3 — 급여 관리 사례 연구

가상의 급여 관리 시스템을 처음부터 만들어가면서 패턴과 SOLID 원칙이 실제 코드에서 어떻게 작동하는지 보여준다.

| Ch | 제목 | 핵심 |
|---|---|---|
| [13](ch13-command-and-active-object.md) | **Command and Active Object (커맨드와 액티브 오브젝트)** | 함수의 객체화. 트랜잭션, Undo, 멀티스레드 큐 |
| [14](ch14-template-method-and-strategy.md) | **Template Method and Strategy (템플릿 메소드와 스트래터지)** | 알고리즘 골격을 공유하는 두 가지 방식: 상속 vs 위임 |
| [15](ch15-facade-and-mediator.md) | **Facade and Mediator (퍼사드와 미디에이터)** | 정책을 가시적으로 강제 vs 비가시적으로 시행 |
| [16](ch16-singleton-and-monostate.md) | **Singleton and Monostate (싱글톤과 모노스테이트)** | 단일성을 강제하는 두 가지 방식: 구조적 vs 행위적 |
| [17](ch17-null-object-pattern.md) | **Null Object (널 오브젝트)** | null 체크를 다형성으로 해결 |
| [18](ch18-payroll-case-study-iteration-1.md) | **Payroll Case Study — Iteration 1 (사례 연구: 반복의 시작)** | 7개 유스케이스 분석, Command + Strategy 4중 적용 |
| [19](ch19-payroll-case-study-implementation.md) | **Payroll Case Study — Implementation (사례 연구: 구현)** | TDD로 트랜잭션 구현, ChangeEmployee 다단계 추상화, Payday 핵심 로직 |

### PART 4 — 급여 관리 시스템 패키징

PART 3의 클래스 약 50개를 어떻게 패키지로 묶을 것인가. 패키지 단위의 응집도/결합도/안정성 분석.

| Ch | 제목 | 핵심 |
|---|---|---|
| [20](ch20-principles-of-package-design.md) | **Principles of Package Design (패키지 설계 원칙)** | 응집도(REP/CCP/CRP) + 결합도(ADP/SDP/SAP) 6원칙 + 메인 시퀀스 |
| [21](ch21-factory-pattern.md) | **Factory Pattern (팩토리 패턴)** | new 키워드의 DIP 위반 해결. Abstract Factory와 스푸핑 |
| [22](ch22-payroll-case-study-packaging.md) | **Payroll Case Study Part 2: Packaging** | 50개 클래스에 6가지 패키지 원칙 적용, A/I 척도 측정 |

### PART 5 — 기상 관측기 사례 연구

분산 임베디드 시스템의 점진적 진화 — Composite, Observer, Adapter, Bridge, Proxy 등 다양한 패턴이 변경의 압박 속에서 자연스럽게 등장한다.

| Ch | 제목 | 핵심 |
|---|---|---|
| [23](ch23-composite-pattern.md) | **Composite (컴포지트)** | 일대다를 일대일로 — 단일과 집합을 같은 인터페이스로 |
| [24](ch24-observer-pattern.md) | **Observer (옵저버)** | "패턴으로 돌아가기" — TDD로 진화 끝에 발견되는 정규형 |
| [25](ch25-abstract-server-adapter-bridge.md) | **Abstract Server, Adapter, Bridge** | 같은 의존성 역전의 세 가지 변형 |
| [26](ch26-proxy-and-stairway-to-heaven.md) | **Proxy and Stairway to Heaven** | 서드파티 API 격리. 영속성 분리. 다이아몬드 상속 |
| [27](ch27-case-study-weather-station.md) | **Case Study: Weather Station (기상 관측기 사례)** | Observer/Bridge/Factory/Proxy의 종합 적용 흐름 |

### PART 6 — ETS 사례 연구

실제 대규모 프로젝트(NCARB 건축사 면허 시험 자동화)의 경험담. State 패턴과 SMC 도구의 실전 활용.

| Ch | 제목 | 핵심 |
|---|---|---|
| [28](ch28-visitor-pattern.md) | **Visitor Pattern Family (비지터 패밀리)** | Visitor, Acyclic Visitor, Decorator, Extension Object 네 가지 |
| [29](ch29-state-pattern.md) | **State Pattern (스테이트)** | FSM 네 가지 구현 기법 (중첩 switch/전이 테이블/스테이트/SMC) |
| [30](ch30-ets-framework.md) | **The ETS Framework (ETS 프레임워크)** | 실패한 첫 프레임워크 → 점진적 추출로 6:1 생산성 향상 |

### 부록

| Appendix | 제목 | 핵심 |
|---|---|---|
| [A](appendix-a-uml-notation-cgi.md) | **UML Notation I — CGI Example** | UML 정적 다이어그램: 클래스/객체/유스케이스/컴포넌트/시퀀스 |
| [B](appendix-b-uml-notation-statmux.md) | **UML Notation II — Statmux** | UML 동적 다이어그램: 상태 기계/활동/협동/메시지 시퀀스 차트 |
| [C](appendix-c-satire-of-two-companies.md) | **A Satire of Two Companies (두 기업에 대한 풍자)** | Rufus(무거운 프로세스) vs Rupert(애자일)의 운명을 가르는 결정들 |
| [D](appendix-d-source-code-is-the-design.md) | **Source Code Is the Design (소스 코드는 곧 설계다)** | 잭 리브스의 1992년 에세이 — 책 전체의 사상적 출발점 |

---

## 노트의 구성 요소

각 챕터는 다음 요소로 구성되어 있다:

- `## 핵심 질문` — 챕터가 답하려는 물음
- 번호가 매겨진 주요 섹션 (`## 1.`, `## 2.`, ...)
- `> **핵심 통찰**:` — 콜아웃 형식의 핵심 인사이트
- `> **Uncle Bob의 경험**:` — 저자의 실제 프로젝트 경험담
- `(*Term - 설명*)` 인라인 이탤릭 — 처음 등장하는 용어 설명
- 코드 예제 — **Java/C++ 원본**(`<details>` 접기) + **TypeScript 변환**(항상 펼침)
- ASCII/유니코드 클래스 다이어그램, 상태 다이어그램, 패키지 의존도
- `## 자주 하는 실수` — 안티패턴 테이블 (SOLID 챕터 중심)
- `## 설계 원칙` — 챕터별 핵심 원칙 요약 테이블
- `## 요약` — 챕터 마지막 불릿 정리

---

## 책의 인상적인 인용

> **Uncle Bob의 첫 번째 법칙**: 그 필요가 급박하고 중요하지 않다면 아무 문서도 만들지 마라.

> 우리는 분석가가 아니다. 분석은 우리가 하는 일의 일부일 뿐이다. 우리는 설계자가 아니다. 설계 역시 우리가 하는 일의 일부일 뿐이다. 우리는 프로그래머다.

> 동작하는 코드만이 변경을 두려워하지 않는 자세를 만든다. 두려워하지 않는 자세만이 코드를 깨끗하게 유지할 수 있다.

> 좋은 설계는 사전에 다이어그램으로 결정되는 것이 아니라, 변경의 신호를 받아 점진적으로 만들어진다.

---

## 관련 책

- [the-clean-coder/](../the-clean-coder/) — 같은 저자의 **프로페셔널리즘** 책
- [objects/](../objects/) — 조영호의 **객체지향 설계** 책 (자매편: [the-essence-of-object-orientation/](../the-essence-of-object-orientation-객체지향의-사실과-오해/))
- [philosophy-of-software-design/](../philosophy-of-software-design/) — John Ousterhout의 **소프트웨어 설계 철학**
- [test-driven-development-by-example/](../test-driven-development-by-example/) — Kent Beck의 **TDD** 원전
- [legacy-code/](../legacy-code/) — Michael Feathers의 **레거시 코드 작업법**
