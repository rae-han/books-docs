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

### 장별 에피그래프

이 책의 시그니처 — 거의 모든 장이 문학·역사 인용으로 문을 연다.

> 교회 첨탑 위의 풍향계가 강철로 만들어졌다 해도, 바람에 따라 움직이는 중요한 기술을 이해하지 않았다면 곧 폭풍에 부서졌을 것이다.<br>— 하인리히 하이네(Heinrich Heine) (위치: Ch1)

> 개발자로서 우리가 기억해야 할 것은 XP가 마을에서 유일한 게임이 아니라는 것이다.<br>— 피트 맥브린(Pete McBreen), 『Software Craftsmanship』 (위치: Ch2)

> 말하고 있는 것을 측정하고 그것을 수치로 표현할 수 있을 때, 비로소 그것에 대해 아는 것이다. 그러나 측정하지 못하고 수치로도 표현하지 못한다면, 그 지식은 빈약하고 만족스럽지 못한 것이다.<br>— 켈빈(Kelvin) 경, 1883 (위치: Ch3)

> 불은 황금을 시험하고, 역경은 강한 사람을 시험한다.<br>— 세네카(Seneca) (위치: Ch4)

> 풍족한 세상에서 점점 더 부족해지고 있는 유일한 것은 사람들의 주의력이다.<br>— 케빈 켈리(Kevin Kelly), 『와이어드(Wired)』 (위치: Ch5)

> 설계와 프로그래밍은 사람이 하는 일이다. 그것을 잊어버리면 모든 것을 잃게 된다.<br>— 비야네 스트로스트룹(Bjarne Stroustrup), 1991 (위치: Ch6)

> 소프트웨어 개발 생명 주기를 검토한 후, 공학 설계의 기준을 실제로 만족시킬 유일한 소프트웨어 문서는 소스 코드 목록뿐임을 알 수 있었다.<br>— 잭 리브스(Jack Reeves), 「What Is Software Design?」 (C++ Journal, 1992) (위치: Ch7)

> 신비스러운 비밀들을 드러낸 것에 대한 책임은 다른 사람이 아닌 바로 부처 스스로 가져야 한다…<br>— E. 코범 브루어(E. Cobham Brewer), 『Dictionary of Phrase and Fable』(1898) (위치: Ch8)

> 모든 시스템은 생명 주기 동안에 변화한다. 이것은 개발 중인 시스템이 첫 번째 버전보다 오래 남길 원한다면 반드시 염두에 두어야 할 사실이다.<br>— 이바 야콥슨(Ivar Jacobson) (위치: Ch9)

> 더는 국가의 중요한 일들이 인간의 나약함을 흔들지도 모르는 무수한 가능성에 휘둘리지 않게 해야 한다.<br>— 토머스 눈 탈파우드(Thomas Noon Talfourd) 경 (위치: Ch11)

> 인터페이스 분리 원칙은 '비대한' 인터페이스의 단점을 해결한다. 비대한 인터페이스를 가지는 클래스는 응집력 없는 인터페이스를 가지는 클래스다.<br>— 로버트 C. 마틴 (위치: Ch12)

> 그 어느 누구도 다른 사람들에게 명령할 권한을 자연으로부터 받은 사람은 없다.<br>— 데니스 디드로(Denis Diderot) (위치: Ch13)

> 인생에서의 최고의 전략은 근면이다.<br>— 중국 속담 (위치: Ch14)

> 클래스 상속보다는 차라리 복합(composition)이 더 낫다.<br>— GoF(감마·헬름·존슨·블리시디스), 『Design Patterns』(1995) (위치: Ch14)

> 상징이 체면을 지켜주는 외벽이 되어서 꿈의 외설스러움을 숨겨준다.<br>— 메이슨 쿨리(Mason Cooley) (위치: Ch15)

> 존재의 무한한 지복이여! 이것이 있다. 그리고 그 외에는 아무것도 없다.<br>— 에드윈 애벗(Edwin A. Abbott), 『Flatland(평면세계)』 중점에 대해 (위치: Ch16)

> 너무 흠이 없어 흠이 되고, 시릴 정도로 정확하며, 화려하게 비어 있는, 죽어 있는 완벽함, 그 이상은 없다.<br>— 알프레드 테니슨(Alfred Tennyson) (위치: Ch17)

> 아름다운 것은 모두 그 자체로 아름답고, 그 자체로 완전하며, 찬양할 만한 점이 따로 있는 것은 아니다.<br>— 마르쿠스 아우렐리우스(Marcus Aurelius) (위치: Ch18)

> 공장을 짓는 사람은 사원(寺院)을 짓고 있는 셈이다.<br>— 캘빈 쿨리지(Calvin Coolidge) (위치: Ch21)

> 경험상의 규칙: 어떤 것이 영리하고 정교하다고 생각된다면, 조심해라. 그 생각이 여러분의 방종일 가능성이 크다.<br>— 도널드 A. 노먼(Donald A. Norman), 『The Design of Everyday Things』 (위치: Ch22)

> 정치인은 어디나 다 똑같다. 그들은 강이 있지도 않은 곳에 다리를 놓겠다고 약속한다.<br>— 니키타 흐루시초프(Nikita Khrushchev) (위치: Ch25)

> 어떤 늦은 방문객이 문 밖에서 들어오기를 청하고 있어. 그것뿐 아무것도 아니야.<br>— 에드거 앨런 포(Edgar Allan Poe), 「갈가마귀(The Raven)」 중 (위치: Ch28)

> 변화의 수단이 없는 국가는 자기 보전의 수단이 없는 국가다.<br>— 에드먼드 버크(Edmund Burke) (위치: Ch29)

### 본문 인용

> 적어도 세 번 이상 그 프레임워크를 기반으로 애플리케이션을 구축해봐야(그리고 실패해봐야) 그 도메인에 맞는 올바른 아키텍처를 구축했다는 자신감이 그런대로 생길 수 있다.<br>— 레베카 워프스-브록(Rebecca Wirfs-Brock) (위치: Ch30)

> 격렬한 개발 와중의 이런 모든 수정, 사소한 변경, 작은 조정에도 불구하고, "소프트웨어의 설계는 흐트러지지 않았다."<br>— 피트 브리팅햄(Pete Britingham), ETS의 NCARB 프로젝트 관리자 (위치: Ch30)

## 시그니처 요소와 표기 규칙

- `> **Uncle Bob의 경험**:` — 저자의 실제 프로젝트 경험담 / `> **핵심 통찰**:` 콜아웃
- 코드 예제: **Java/C++ 원본**(`<details>` 접기) + **TypeScript 변환**(항상 펼침)
- ASCII/유니코드 클래스·상태·패키지 의존 다이어그램
- `## 자주 하는 실수`(SOLID 챕터 중심) · `## 설계 원칙` 요약 테이블
