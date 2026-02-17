# A Philosophy of Software Design

**저자**: John Ousterhout (Stanford University)
**출판**: 2nd Edition, 2021, Yaknyam Press

---

## 책 소개

"A Philosophy of Software Design"은 스탠포드 대학교 CS190 소프트웨어 설계 수업을 기반으로 한 소프트웨어 설계 철학서이다. 이 책의 핵심 전제는 단순하다:

> **소프트웨어 설계의 가장 근본적인 문제는 복잡성(complexity)을 관리하는 것이다.**

대부분의 프로그래밍 서적이 특정 언어, 프레임워크, 패턴을 다루는 반면, 이 책은 **"좋은 설계란 무엇인가?"** 라는 근본적인 질문에 집중한다. 저자 John Ousterhout는 Tcl 언어 창시자이자 Raft 합의 알고리즘의 공동 개발자로, 수십 년간의 소프트웨어 개발 경험과 교육 경험에서 추출한 설계 원칙들을 제시한다.

### 이 책의 특징

- **짧고 명확하다**: 200페이지 미만으로, 각 챕터가 하나의 명확한 원칙을 다룬다.
- **Red Flag를 제시한다**: 각 원칙을 위반하는 징후(Red Flag)를 구체적으로 명시하여, 코드 리뷰나 설계 검토 시 실용적인 체크리스트로 활용할 수 있다.
- **논쟁적이다**: 일부 주장(예: Clean Code의 짧은 메서드 철학에 대한 반론)은 소프트웨어 커뮤니티에서 활발한 논쟁을 불러일으켰다. 동의 여부를 떠나 설계에 대해 깊이 생각하게 만든다.

---

## 이 저장소의 목적

이 저장소는 "A Philosophy of Software Design"의 내용을 챕터별로 상세하게 정리한 학습 자료이다. 각 챕터의 핵심 원칙, Red Flag, 예시를 책을 대체할 수 있을 정도로 충실하게 담고 있으며, 다음과 같은 용도로 활용할 수 있다:

- 소프트웨어 설계 원칙을 체계적으로 학습하는 교재
- 코드 리뷰 시 설계 판단의 기준으로 참조하는 가이드
- 팀 내 설계 토론과 스터디 자료

---

## 목차

### Part I: 복잡성의 본질
- [Chapter 1: Introduction (모든 것은 복잡성에 관한 것이다)](ch01-introduction.md)
- [Chapter 2: The Nature of Complexity (복잡성의 본질)](ch02-the-nature-of-complexity.md)

### Part II: 설계 원칙
- [Chapter 3: Working Code Isn't Enough (동작하는 코드만으로는 부족하다)](ch03-working-code-isnt-enough.md)
- [Chapter 4: Modules Should Be Deep (모듈은 깊어야 한다)](ch04-modules-should-be-deep.md)
- [Chapter 5: Information Hiding and Leakage (정보 은닉과 정보 누출)](ch05-information-hiding-and-leakage.md)
- [Chapter 6: General-Purpose Modules are Deeper (범용 모듈이 더 깊다)](ch06-general-purpose-modules-are-deeper.md)
- [Chapter 7: Different Layer, Different Abstraction (계층이 다르면 추상화도 달라야 한다)](ch07-different-layer-different-abstraction.md)
- [Chapter 8: Pull Complexity Downwards (복잡성을 아래로 끌어내려라)](ch08-pull-complexity-downwards.md)
- [Chapter 9: Better Together Or Better Apart? (합치는 게 나은가, 분리하는 게 나은가?)](ch09-better-together-or-better-apart.md)
- [Chapter 10: Define Errors Out Of Existence (에러를 정의 밖으로 내보내라)](ch10-define-errors-out-of-existence.md)
- [Chapter 11: Design it Twice (두 번 설계하라)](ch11-design-it-twice.md)

### Part III: 주석과 이름
- [Chapter 12: Why Write Comments? The Four Excuses (왜 주석을 써야 하는가)](ch12-why-write-comments.md)
- [Chapter 13: Comments Should Describe Things That Aren't Obvious (주석은 명확하지 않은 것을 설명해야 한다)](ch13-comments-should-describe-things-that-arent-obvious.md)
- [Chapter 14: Choosing Names (이름 짓기)](ch14-choosing-names.md)
- [Chapter 15: Write The Comments First (주석을 먼저 작성하라)](ch15-write-the-comments-first.md)

### Part IV: 기존 코드와 일관성
- [Chapter 16: Modifying Existing Code (기존 코드 수정하기)](ch16-modifying-existing-code.md)
- [Chapter 17: Consistency (일관성)](ch17-consistency.md)
- [Chapter 18: Code Should be Obvious (코드는 명확해야 한다)](ch18-code-should-be-obvious.md)

### Part V: 더 넓은 시각
- [Chapter 19: Software Trends (소프트웨어 트렌드)](ch19-software-trends.md)
- [Chapter 20: Designing for Performance (성능을 위한 설계)](ch20-designing-for-performance.md)
- [Chapter 21: Decide What Matters (무엇이 중요한지 결정하라)](ch21-decide-what-matters.md)
- [Chapter 22: Conclusion (결론)](ch22-conclusion.md)

---

## 학습 가이드

### 추천 읽기 순서

이 책은 앞에서 뒤로 순서대로 읽는 것을 권장한다. 각 챕터의 개념이 이전 챕터 위에 쌓이기 때문이다. 하지만 이미 설계 경험이 있는 개발자라면 관심 분야부터 읽어도 무방하다.

**1단계: 문제 정의 (Chapter 1~2)**

소프트웨어 설계가 왜 어려운지, 복잡성이란 정확히 무엇인지를 이해한다. 이후 모든 원칙의 근거가 되므로 반드시 먼저 읽는다.

**2단계: 핵심 설계 원칙 (Chapter 3~11)**

이 책의 가장 중요한 부분이다. "깊은 모듈", "정보 은닉", "복잡성을 아래로 끌어내리기" 등 Ousterhout의 핵심 설계 철학을 다룬다. 특히 Chapter 4(깊은 모듈)는 이 책의 가장 중심적인 개념이다.

**3단계: 주석과 이름 (Chapter 12~15)**

코드의 가독성과 유지보수성에 직결되는 주석, 이름 짓기에 대한 원칙을 다룬다. 저자는 주석에 대해 상당히 강한 입장(주석을 먼저 쓰라!)을 취하므로, 기존 관점과 비교하며 읽으면 유익하다.

**4단계: 실무 적용과 트렌드 (Chapter 16~22)**

기존 코드 수정, 일관성, 소프트웨어 트렌드(애자일, 디자인 패턴, TDD 등)에 대한 저자의 시각을 다룬다.

---

## 핵심 개념 요약

이 책의 모든 내용은 하나의 중심 명제로 수렴한다:

> **소프트웨어 설계의 목표는 복잡성을 최소화하는 것이다.**

복잡성은 시스템의 크기가 아니라 **개발자가 시스템을 이해하고 수정하는 것이 얼마나 어려운가**로 정의된다. 복잡성을 관리하는 두 가지 핵심 전략은 (1) **복잡성을 제거하여 코드를 단순하고 명확하게 만드는 것**과 (2) **복잡성을 캡슐화하여 한 번에 다뤄야 하는 양을 줄이는 것**이다.

이를 위해 Ousterhout가 제시하는 핵심 원칙들:

- **깊은 모듈(Deep Module)**: 단순한 인터페이스 뒤에 강력한 기능을 숨겨라
- **정보 은닉(Information Hiding)**: 설계 결정을 모듈 내부에 가두어라
- **전략적 프로그래밍(Strategic Programming)**: "빨리 동작하게"가 아니라 "좋은 설계"를 목표로 하라
- **복잡성을 아래로(Pull Complexity Downwards)**: 사용하기 쉽게 만들고, 구현이 복잡성을 흡수하게 하라
- **두 번 설계하라(Design it Twice)**: 첫 번째 아이디어에 만족하지 말고 대안을 비교하라

---

## Red Flags (경고 신호)

이 책의 특징적인 요소로, 각 챕터에서 설계 문제를 알려주는 Red Flag를 제시한다. 주요 Red Flag들:

- **Shallow Module**: 인터페이스가 복잡한데 기능은 단순한 모듈
- **Information Leakage**: 같은 설계 결정이 여러 모듈에 분산되어 있음
- **Temporal Decomposition**: 실행 순서에 따라 모듈을 나누어 정보가 분산됨
- **Overexposure**: 드물게 사용되는 기능이 일반적인 API에 노출됨
- **Pass-Through Method**: 거의 아무 일도 하지 않고 다른 메서드를 호출하기만 하는 메서드
- **Repetition**: 같은 코드 패턴이 반복됨
- **Special-General Mixture**: 범용 메커니즘에 특수 목적 코드가 섞여 있음
- **Conjoined Methods**: 두 메서드를 함께 읽어야만 하나의 메서드를 이해할 수 있음
- **Comment Repeats Code**: 주석이 코드를 그대로 반복함
- **Vague Name**: 이름이 모호하여 여러 의미로 해석 가능함
- **Hard to Pick Name**: 정확한 이름을 짓기 어려운 것은 설계가 명확하지 않다는 신호
- **Nonobvious Code**: 코드를 읽어도 동작을 쉽게 이해할 수 없음
