# 클린 소프트웨어 (Agile Software Development, Principles, Patterns, and Practices)

> *Agile Software Development, Principles, Patterns, and Practices* (Robert C. Martin, Prentice Hall, 2003)
> 한국어판: 『클린 소프트웨어 — 애자일 원칙과 패턴, 그리고 실천 방법』 (이용원·김정민·정지호 옮김, 제이펍, 2017)

Uncle Bob의 객체지향 설계 고전. 애자일 실천 방법에서 시작해 SOLID 원칙, 패키지 설계 원칙, 디자인 패턴, 그리고 세 가지 사례 연구(급여 관리·기상 관측기·ETS 시험 시스템)로 이어진다.

## 책 정보

| 항목 | 내용 |
|------|------|
| **저자** | 로버트 C. 마틴(Robert C. Martin, Uncle Bob) |
| **역자** | 이용원·김정민·정지호 |
| **출판** | 제이펍, 2017 (원서: Prentice Hall, 2003) |
| **예제 언어** | Java·C++ (노트는 TypeScript 병기) |
| **대상 독자** | SOLID·패턴이 "실제 변경 압박 속에서" 어떻게 등장하는지 보고 싶은 개발자 |

## 개요

핵심 메시지는 "**소프트웨어 설계는 단번에 완성되지 않는다**"이다 — 변화를 두려워하지 않고, 변화가 일어날 때 그것을 신호로 삼아 점진적으로 개선하는 것이 진정한 설계다. 패턴은 시작점이 아니라 도착점이며, 사전에 적용하는 것이 아니라 변경의 필요에 따라 도달하는 것이다.

사상적 출발점은 잭 리브스의 1992년 에세이(부록 D) — **소스 코드가 곧 설계 문서이며, UML 다이어그램은 스케치일 뿐**이라는 통찰이다. SOLID 원칙(PART 2)과 패키지 원칙(PART 4)은 이후 『클린 아키텍처』(2017)에서 아키텍처 수준으로 확장된다.

## 목차

### PART 1: 애자일 개발 (Ch 1-6)

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 1 | [Agile Practices](ch01-agile-practices.md) | 애자일 선언문 · 12원칙 | 애자일 4가지 가치와 12원칙 — 프로세스 악순환을 깨는 법 |
| 2 | [Extreme Programming Overview](ch02-extreme-programming-overview.md) | XP · 짝 프로그래밍 · 지속적 통합 | XP 12가지 실천 방법 개관 |
| 3 | [Planning](ch03-planning.md) | 스토리 포인트 · 속도 | 탐색→릴리즈→반복의 3단계 계획과 속도 측정 |
| 4 | [Testing](ch04-testing.md) | 테스트 주도 개발 · 인수 테스트 | TDD는 검증이 아니라 설계 활동이다 |
| 5 | [Refactoring](ch05-refactoring.md) | 리팩터링 · 소수 생성기 | 동작 변경 없는 구조 개선 — 단계별 시연 |
| 6 | [A Programming Episode](ch06-programming-episode.md) | 볼링 게임 · 짝 TDD | 볼링 점수판 TDD 실전 — UML이 사라지고 코드가 설계가 되는 과정 |

### PART 2: 애자일 설계 (Ch 7-12) — SOLID

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 7 | [What Is Agile Design?](ch07-what-is-agile-design.md) | 설계 악취 7가지 | 경직성·취약성·부동성·점착성·불필요한 복잡성·반복·불투명성 |
| 8 | [SRP](ch08-single-responsibility-principle.md) | 단일 책임 원칙 | 한 클래스는 단 한 가지의 변경 이유만 가져야 한다 |
| 9 | [OCP](ch09-open-closed-principle.md) | 개방-폐쇄 원칙 | 확장에는 열려, 수정에는 닫혀 — 추상화로 확보 |
| 10 | [LSP](ch10-liskov-substitution-principle.md) | 리스코프 치환 원칙 | IS-A는 행위에 관한 것 — 치환 가능성이 기준 |
| 11 | [DIP](ch11-dependency-inversion-principle.md) | 의존 관계 역전 원칙 | 상위·하위 모듈 모두 추상화에 의존하라 |
| 12 | [ISP](ch12-interface-segregation-principle.md) | 인터페이스 분리 원칙 | 사용하지 않는 메서드에 의존하지 마라 |

### PART 3: 급여 관리 사례 연구 (Ch 13-19)

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 13 | [Command and Active Object](ch13-command-and-active-object.md) | 커맨드 패턴 · 액티브 오브젝트 | 함수의 객체화 — 트랜잭션·Undo·멀티스레드 큐 |
| 14 | [Template Method and Strategy](ch14-template-method-and-strategy.md) | 템플릿 메서드 · 전략 패턴 | 알고리즘 골격 공유의 두 방식 — 상속 vs 위임 |
| 15 | [Facade and Mediator](ch15-facade-and-mediator.md) | 퍼사드 · 중재자 | 정책 강제의 두 방식 — 가시적 vs 비가시적 |
| 16 | [Singleton and Monostate](ch16-singleton-and-monostate.md) | 싱글턴 · 모노스테이트 | 단일성 강제의 두 방식 — 구조적 vs 행위적 |
| 17 | [Null Object](ch17-null-object-pattern.md) | 널 오브젝트 패턴 | null 체크를 다형성으로 대체 |
| 18 | [Payroll Case Study: Iteration 1](ch18-payroll-case-study-iteration-1.md) | 유스케이스 분석 · 패턴 적용 | 급여 시스템 분석 — Command+Strategy 4중 적용 |
| 19 | [Payroll Case Study: Implementation](ch19-payroll-case-study-implementation.md) | TDD 구현 · 다단계 추상화 | 트랜잭션 구현부터 Payday 핵심 로직까지 |

### PART 4: 급여 관리 시스템 패키징 (Ch 20-22)

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 20 | [Principles of Package Design](ch20-principles-of-package-design.md) | REP/CCP/CRP · ADP/SDP/SAP · 메인 시퀀스 | 패키지 응집 3원칙 + 결합 3원칙 |
| 21 | [Factory Pattern](ch21-factory-pattern.md) | 팩토리 · 추상 팩토리 | new의 DIP 위반을 팩토리로 해결 |
| 22 | [Payroll Case Study: Packaging](ch22-payroll-case-study-packaging.md) | 패키지 분할 · A/I 척도 | 50개 클래스에 패키지 6원칙 적용·측정 |

### PART 5: 기상 관측기 사례 연구 (Ch 23-27)

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 23 | [Composite](ch23-composite-pattern.md) | 컴포지트 패턴 | 일대다를 일대일로 — 단일과 집합을 같은 인터페이스로 |
| 24 | [Observer](ch24-observer-pattern.md) | 옵저버 패턴 · 패턴으로의 진화 | TDD로 진화하다 보면 패턴의 정규형에 도달한다 |
| 25 | [Abstract Server, Adapter, Bridge](ch25-abstract-server-adapter-bridge.md) | 추상 서버 · 어댑터 · 브리지 | 같은 의존성 역전의 세 가지 변형 |
| 26 | [Proxy and Stairway to Heaven](ch26-proxy-and-stairway-to-heaven.md) | 프록시 · 천국의 계단 | 서드파티 API 격리와 영속성 분리 |
| 27 | [Case Study: Weather Station](ch27-case-study-weather-station.md) | 종합 사례 | Observer·Bridge·Factory·Proxy의 종합 적용 |

### PART 6: ETS 사례 연구 (Ch 28-30)

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 28 | [Visitor Pattern Family](ch28-visitor-pattern.md) | 비지터 · 데코레이터 · 확장 객체 | 비지터 패밀리 4형제 — 이중 디스패치의 세계 |
| 29 | [State Pattern](ch29-state-pattern.md) | 상태 패턴 · FSM · SMC | 유한 상태 기계의 4가지 구현 기법 |
| 30 | [The ETS Framework](ch30-ets-framework.md) | 프레임워크 추출 · 재사용 | 실패한 첫 프레임워크 → 점진적 추출로 6:1 생산성 |

### 부록

| 부록 | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| A | [UML Notation I — CGI Example](appendix-a-uml-notation-cgi.md) | UML 정적 다이어그램 | 클래스·객체·유스케이스·시퀀스 표기법 |
| B | [UML Notation II — Statmux](appendix-b-uml-notation-statmux.md) | UML 동적 다이어그램 | 상태 기계·활동·협동 다이어그램 |
| C | [A Satire of Two Companies](appendix-c-satire-of-two-companies.md) | 풍자 · 프로세스 대비 | Rufus(무거운 프로세스) vs Rupert(애자일)의 운명 |
| D | [Source Code Is the Design](appendix-d-source-code-is-the-design.md) | 잭 리브스 에세이 | 소스 코드가 곧 설계다 — 책 전체의 사상적 출발점 |

## 학습 가이드

1. **처음이라면 순서대로** — PART 1(애자일 가치관) → PART 2(SOLID 어휘) → PART 3~6(변경 압박 속에서 패턴이 자연스럽게 등장하는 과정)
2. **빠른 핵심 트랙**: Ch1(12원칙) → Ch7(설계 악취) → Ch8~12(SOLID) → Ch20(패키지 6원칙) → 부록 D
3. **SOLID만**: Ch7 → Ch8(SRP) → Ch9(OCP) → Ch10(LSP) → Ch11(DIP) → Ch12(ISP)
4. **패턴만**: Ch13~17(커맨드·템플릿/전략·퍼사드/중재자·싱글턴·널 오브젝트) → Ch21(팩토리) → Ch23~26(컴포지트·옵저버·어댑터/브리지·프록시) → Ch28~29(비지터·상태)

## 핵심 개념 맵

- **소스 코드가 곧 설계다**: 다이어그램은 스케치 — 검증은 빌드와 테스트로 (부록 D → Ch6)
- **설계 악취 7가지가 신호**: 경직성·취약성·부동성·점착성 등이 보이면 원칙으로 치료 (Ch7)
- **SOLID는 변경 압박에 대한 응답**: 원칙을 미리 바르는 게 아니라 변경의 신호에 따라 적용 (Ch8~12)
- **패턴은 도착점**: TDD와 리팩터링으로 진화하다 보면 패턴의 정규형에 도달한다 (Ch24가 대표 시연)
- **패키지에도 응집과 결합이 있다**: REP/CCP/CRP + ADP/SDP/SAP — 『클린 아키텍처』 컴포넌트 원칙의 원형 (Ch20)
- **애자일 = 지속 가능한 속도**: 매번 동작하는 소프트웨어, 두려움 없는 변경 (PART 1)

## 인용문

전 책 통합 모음은 [루트 QUOTES.md](../QUOTES.md) 참조.

> 그 필요가 급박하고 중요하지 않다면 아무 문서도 만들지 마라.<br>— 로버트 C. 마틴, 문서화에 관한 마틴의 제1법칙 (위치: Ch1)

> 소스 코드는 곧 설계다.<br>— 잭 리브스(Jack Reeves), 1992 에세이 (위치: 부록 D)

## 시그니처 요소와 표기 규칙

- `> **Uncle Bob의 경험**:` — 저자의 실제 프로젝트 경험담 / `> **핵심 통찰**:` 콜아웃
- 코드 예제: **Java/C++ 원본**(`<details>` 접기) + **TypeScript 변환**(항상 펼침)
- ASCII/유니코드 클래스·상태·패키지 의존 다이어그램
- `## 자주 하는 실수`(SOLID 챕터 중심) · `## 설계 원칙` 요약 테이블
