# A Philosophy of Software Design (소프트웨어 설계의 철학)

> *A Philosophy of Software Design* (2nd Edition, John Ousterhout, Yaknyam Press, 2021)

스탠퍼드 CS190 소프트웨어 설계 수업을 기반으로 한 설계 철학서. 단 하나의 전제 — **소프트웨어 설계의 가장 근본적인 문제는 복잡성(complexity) 관리다** — 에서 출발해, 언어·프레임워크가 아니라 "좋은 설계란 무엇인가"라는 근본 질문에 집중한다.

## 책 정보

| 항목 | 내용 |
|------|------|
| **저자** | 존 아우스터하우트(John Ousterhout) — Tcl 창시자, Raft 합의 알고리즘 공동 개발자 |
| **출판** | Yaknyam Press, 2nd Edition 2021 (한국어판 없음 — 원서 학습) |
| **분량** | 200쪽 미만, 22개 챕터 |
| **대상 독자** | 설계 판단 기준을 세우고 싶은 모든 개발자. 코드 리뷰어에게 특히 유용 |

## 개요

각 챕터가 하나의 명확한 원칙을 다루는 짧은 책이다. 챕터마다 원칙을 위반하는 징후인 **Red Flag**를 명시해 코드 리뷰·설계 검토의 체크리스트로 쓸 수 있게 했다.

일부 주장은 논쟁적이다 — 클린 코드의 "짧은 메서드" 철학에 대한 반론(깊은 모듈이 우선), "주석을 먼저 쓰라"는 강한 입장, TDD·애자일에 대한 비평 등. 동의 여부와 무관하게 설계에 대해 깊이 생각하게 만드는 것이 이 책의 가치다.

## 목차

### Part I: 복잡성의 본질 (Ch 1-2)

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 1 | [Introduction](ch01-introduction.md) | 복잡성 · 점진적 설계 | 설계의 근본 문제는 복잡성 — 책 전체의 문제 제기 |
| 2 | [The Nature of Complexity](ch02-the-nature-of-complexity.md) | 복잡성 정의 · 변경 증폭 · 인지 부하 · 알려지지 않은 미지 | 복잡성의 3가지 증상과 2가지 원인(의존성·모호성) — 복잡성은 조금씩 쌓인다 |

### Part II: 설계 원칙 (Ch 3-11)

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 3 | [Working Code Isn't Enough](ch03-working-code-isnt-enough.md) | 전략적 프로그래밍 · 전술적 프로그래밍 | '일단 돌아가게'(전술)가 아니라 좋은 설계(전략)에 10~20%를 투자하라 |
| 4 | [Modules Should Be Deep](ch04-modules-should-be-deep.md) | 깊은 모듈 · 얕은 모듈 · 인터페이스와 구현 | 이 책의 중심 개념 — 최고의 모듈은 단순한 인터페이스 뒤에 강력한 기능을 숨긴다 |
| 5 | [Information Hiding and Leakage](ch05-information-hiding-and-leakage.md) | 정보 은닉 · 정보 누출 · 시간적 분해 | 설계 결정을 모듈 안에 가두어라 — 실행 순서로 모듈을 나누면 정보가 샌다 |
| 6 | [General-Purpose Modules are Deeper](ch06-general-purpose-modules-are-deeper.md) | 범용 모듈 · 다소 범용적 설계 | 지금 필요보다 '다소 범용'으로 만들면 인터페이스가 오히려 단순해진다 |
| 7 | [Different Layer, Different Abstraction](ch07-different-layer-different-abstraction.md) | 계층별 추상화 · 통과 메서드 · 데코레이터 | 인접 계층의 추상화가 같다면 설계 문제의 신호 |
| 8 | [Pull Complexity Downwards](ch08-pull-complexity-downwards.md) | 복잡성 하향 · 설정 매개변수 | 사용자를 편하게, 복잡성은 구현(아래)이 흡수하게 |
| 9 | [Better Together Or Better Apart?](ch09-better-together-or-better-apart.md) | 결합과 분리 · 특수-범용 혼합 | 무조건 잘게 나누는 게 답이 아니다 — 합칠지 나눌지의 판단 기준 |
| 10 | [Define Errors Out Of Existence](ch10-define-errors-out-of-existence.md) | 오류 정의 제거 · 예외 마스킹 · 예외 통합 | 예외 처리보다 예외가 아예 생기지 않는 의미론을 정의하라 (unset 예제) |
| 11 | [Design it Twice](ch11-design-it-twice.md) | 두 번 설계하기 | 첫 아이디어에 만족하지 말고 근본적으로 다른 대안을 만들어 비교하라 |

### Part III: 주석과 이름 (Ch 12-15)

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 12 | [Why Write Comments? The Four Excuses](ch12-why-write-comments.md) | 주석의 네 가지 변명 | "좋은 코드는 자기 문서화된다"는 신화에 대한 반박 |
| 13 | [Comments Should Describe Things That Aren't Obvious](ch13-comments-should-describe-things-that-arent-obvious.md) | 인터페이스 주석 · 구현 주석 · 낮은 수준/높은 수준 주석 | 코드로 표현할 수 없는 것(왜, 전제, 추상화)을 주석으로 |
| 14 | [Choosing Names](ch14-choosing-names.md) | 이름 짓기 · 모호한 이름 | 정확하고 일관된 이름 — 이름 짓기가 어렵다면 설계가 불명확하다는 신호 |
| 15 | [Write The Comments First](ch15-write-the-comments-first.md) | 주석 우선 작성 · 설계 도구로서의 주석 | 주석을 먼저 쓰면 설계 검증 도구가 된다 |

### Part IV: 기존 코드와 일관성 (Ch 16-18)

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 16 | [Modifying Existing Code](ch16-modifying-existing-code.md) | 전략적 수정 · 주석 최신화 | 수정도 설계 활동 — 떠날 때는 찾았을 때보다 깨끗하게 |
| 17 | [Consistency](ch17-consistency.md) | 일관성 · 컨벤션 | 일관성은 인지 부하를 줄인다 — 더 나은 아이디어라도 일관성을 깨려면 신중히 |
| 18 | [Code Should be Obvious](ch18-code-should-be-obvious.md) | 명확한 코드 · 가독성 | 명확성은 작성자가 아니라 읽는 사람이 판단한다 |

### Part V: 더 넓은 시각 (Ch 19-22)

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 19 | [Software Trends](ch19-software-trends.md) | 객체지향 · 애자일 · 테스트 주도 개발 · 디자인 패턴 비평 | 유행하는 방법론들을 '복잡성 관점'으로 재평가 |
| 20 | [Designing for Performance](ch20-designing-for-performance.md) | 성능 설계 · 임계 경로 단순화 | 성능과 단순성은 대립하지 않는다 — 임계 경로를 근본적으로 단순하게 |
| 21 | [Decide What Matters](ch21-decide-what-matters.md) | 중요한 것 가려내기 | 무엇이 중요하고 무엇이 아닌지의 구분이 설계 판단의 핵심 (2판 신규) |
| 22 | [Conclusion](ch22-conclusion.md) | 복잡성과의 싸움 | 책 전체 요약 — 설계는 복잡성과의 지속적인 싸움 |

## 학습 가이드

1. **Ch1~2 필독** — 복잡성의 정의(증상 3가지·원인 2가지)가 이후 모든 원칙의 근거
2. **Ch3~11이 본론** — 특히 **Ch4(깊은 모듈)**가 가장 중심 개념. 순서대로 읽되, Ch4·5·8은 세트로
3. **Ch12~15(주석)는 기존 관점과 비교하며** — 저자의 입장이 강해서(주석 먼저!) 클린 코드류와 대조하면 유익
4. **Ch19(트렌드 비평)는 다른 책들과 함께** — TDD·애자일 비평은 실용주의 프로그래머·클린 코더와 교차 검토

## 핵심 개념 맵

- **설계의 목표 = 복잡성 최소화** — 복잡성은 크기가 아니라 "이해하고 수정하기 어려운 정도"
- **복잡성의 증상 3가지**: 변경 증폭, 인지 부하, 알려지지 않은 미지 — 원인은 의존성과 모호성
- **깊은 모듈**: 인터페이스(비용) 대비 기능(이득)이 큰 모듈 — 작게 쪼개기 자체는 미덕이 아니다
- **복잡성을 아래로**: 모듈 사용자가 아니라 구현이 복잡성을 흡수해야 한다 (정보 은닉·오류 정의 제거와 한 몸)
- **전략적 프로그래밍**: 좋은 설계는 공짜가 아니다 — 지속적인 소규모 투자(10~20%)로 산다
- **주석과 이름은 설계 도구** — 짓기 어려움과 쓰기 어려움 자체가 설계 문제의 신호(Red Flag)

## 인용문

전 책 통합 모음은 [루트 QUOTES.md](../QUOTES.md) 참조.

> 소프트웨어 작성의 가장 큰 한계는 우리가 만들고 있는 시스템을 이해하는 능력이다.<br>— 존 아우스터하우트 (위치: Ch2)

> 복잡성은 한 번에 하나씩 쌓인다. 그래서 복잡성에는 무관용이어야 한다.<br>— 존 아우스터하우트 (위치: Ch2)

## Red Flags (경고 신호) — 이 책의 시그니처

각 챕터가 제시하는 설계 문제의 징후. 코드 리뷰 체크리스트로 활용.

- **Shallow Module**: 인터페이스가 복잡한데 기능은 단순한 모듈
- **Information Leakage**: 같은 설계 결정이 여러 모듈에 분산
- **Temporal Decomposition**: 실행 순서 기준으로 모듈을 나눠 정보가 분산됨
- **Overexposure**: 드물게 쓰는 기능이 일반 API에 노출됨
- **Pass-Through Method**: 다른 메서드 호출만 하고 아무 일도 안 하는 메서드
- **Repetition**: 같은 코드 패턴의 반복
- **Special-General Mixture**: 범용 메커니즘에 특수 목적 코드가 섞임
- **Conjoined Methods**: 두 메서드를 함께 읽어야만 이해 가능
- **Comment Repeats Code**: 코드를 그대로 반복하는 주석
- **Vague Name / Hard to Pick Name**: 모호한 이름, 이름 짓기 어려움 = 설계 불명확 신호
- **Nonobvious Code**: 읽어도 동작을 쉽게 이해할 수 없는 코드

## 시그니처 요소와 표기 규칙

- 각 챕터 노트에 `## Red Flags` 절 — 그 장의 경고 신호 정리
- `> **핵심 통찰**:` 콜아웃, 원칙 정의는 `>` 인용 블록
