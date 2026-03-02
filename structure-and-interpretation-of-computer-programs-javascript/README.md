# Structure and Interpretation of Computer Programs, JavaScript Edition (컴퓨터 프로그램의 구조와 해석)

**원저**: Harold Abelson, Gerald Jay Sussman with Julie Sussman (MIT)
**JavaScript 개편**: Martin Henz, Tobias Wrigstad
**출판**: 2022, MIT Press
**온라인**: https://sicp.sourceacademy.org/

---

## 책 소개

"Structure and Interpretation of Computer Programs"(SICP)는 1985년 초판 이래 컴퓨터 과학 교육의 고전으로 자리잡은 MIT의 입문 교재다. JavaScript Edition은 원서의 Scheme 코드를 JavaScript로 번역하면서도, SICP의 핵심 철학 — **계산적 사고(computational thinking)** 와 **추상화의 힘** — 을 온전히 보존한다.

이 책이 다른 프로그래밍 입문서와 근본적으로 다른 점은, 특정 언어의 문법이나 라이브러리를 가르치는 것이 아니라 **프로그래밍의 본질적 개념**을 가르친다는 것이다. 함수를 값으로 다루는 것, 데이터 추상화, 상태와 변이, 메타언어적 추상화, 그리고 기계 수준의 계산까지 — 한 권의 책이 소프트웨어의 가장 낮은 수준부터 가장 높은 수준까지 관통한다.

### 이 책의 특징

- **"마법사 책"**: SICP는 표지의 마법사 그림 때문에 "마법사 책(Wizard Book)"이라는 별명으로 불린다. 프로그래밍을 일종의 마법 — 추상적 주문(코드)으로 프로세스라는 정령을 부리는 행위 — 으로 비유한다.
- **아래에서 위로, 위에서 아래로**: 원시 요소에서 시작하여 점점 더 강력한 추상화를 쌓아올리고, 마침내 언어 자체를 구현하는 데까지 나아간다.
- **핵심 예제 중심**: Newton의 제곱근 방법, 유리수 연산, Picture Language, 기호 미분, 회로 시뮬레이터, 레지스터 머신 등 정교하게 설계된 예제를 통해 개념을 체화시킨다.
- **JavaScript Edition**: Martin Henz와 Tobias Wrigstad가 원서의 Scheme 코드를 JavaScript로 번역했다. 화살표 함수, const/let, 구조 분해 등 현대적 JavaScript 문법을 활용하면서도 원서의 교육적 순서를 충실히 따른다.

---

## 이 저장소의 목적

이 저장소는 SICP JavaScript Edition의 내용을 섹션별로 상세하게 정리한 학습 자료다. 각 섹션의 핵심 개념, 코드 예제, 계산 모델, 연습 문제를 책을 대체할 수 있을 정도로 충실하게 담고 있으며, 다음과 같은 용도로 활용할 수 있다:

- 컴퓨터 과학의 기초 개념을 체계적으로 학습하려는 개발자
- 함수형 프로그래밍의 원리를 깊이 이해하고 싶은 개발자
- SICP를 JavaScript로 학습하려는 스터디 그룹의 교재

---

## 목차

### Chapter 1: Building Abstractions with Functions (함수를 이용한 추상화 구축)

함수를 일급 시민(*First-class citizen — 변수에 저장하고, 함수의 인수로 전달하고, 함수의 반환값으로 사용할 수 있는 값*)으로 다루는 프로그래밍의 기초를 다진다. 원시 요소, 결합, 추상화라는 세 가지 메커니즘으로 시작하여, 재귀, 반복, 고차 함수까지 나아간다.

- [Section 1.1: The Elements of Programming (프로그래밍의 요소)](sec1.1-elements-of-programming.md)
- [Section 1.2: Functions and the Processes They Generate (함수와 그것이 생성하는 프로세스)](sec1.2-functions-and-processes.md)
- [Section 1.3: Formulating Abstractions with Higher-Order Functions (고차 함수를 이용한 추상화)](sec1.3-higher-order-functions.md)

### Chapter 2: Building Abstractions with Data (데이터를 이용한 추상화 구축)

데이터 추상화의 원리를 탐구한다. 쌍(pair)에서 시작하여 계층적 데이터 구조, 기호 데이터, 다중 표현, 제네릭 연산 시스템까지 구축한다.

- [Section 2.1: Introduction to Data Abstraction (데이터 추상화 입문)](sec2.1-data-abstraction.md)
- [Section 2.2: Hierarchical Data and the Closure Property (계층적 데이터와 닫힘 성질)](sec2.2-hierarchical-data.md)
- [Section 2.3: Symbolic Data (기호 데이터)](sec2.3-symbolic-data.md)
- [Section 2.4: Multiple Representations for Abstract Data (추상 데이터의 다중 표현)](sec2.4-multiple-representations.md)
- [Section 2.5: Systems with Generic Operations (제네릭 연산 시스템)](sec2.5-generic-operations.md)

### Chapter 3: Modularity, Objects, and State (모듈성, 객체, 그리고 상태)

상태와 변이를 도입하고, 이것이 프로그래밍 모델에 가져오는 근본적 변화를 탐구한다. 환경 모델, 변이 가능한 데이터, 동시성, 스트림이라는 대안까지 다룬다.

- [Section 3.1: Assignment and Local State (대입과 지역 상태)](sec3.1-assignment-and-local-state.md)
- [Section 3.2: The Environment Model of Evaluation (평가의 환경 모델)](sec3.2-environment-model.md)
- [Section 3.3: Modeling with Mutable Data (변이 가능한 데이터로 모델링)](sec3.3-mutable-data.md)
- [Section 3.4: Concurrency: Time Is of the Essence (동시성: 시간이 본질이다)](sec3.4-concurrency.md)
- [Section 3.5: Streams (스트림)](sec3.5-streams.md)

### Chapter 4: Metalinguistic Abstraction (메타언어적 추상화)

프로그래밍 언어 자체를 구현하는 가장 강력한 추상화를 다룬다. JavaScript 인터프리터를 JavaScript로 구현하는 메타순환 평가기에서 시작하여, 지연 평가, 비결정적 컴퓨팅, 논리 프로그래밍까지 나아간다.

- [Section 4.1: The Metacircular Evaluator (메타순환 평가기)](sec4.1-metacircular-evaluator.md)
- [Section 4.2: Lazy Evaluation (지연 평가)](sec4.2-lazy-evaluation.md)
- [Section 4.3: Nondeterministic Computing (비결정적 컴퓨팅)](sec4.3-nondeterministic-computing.md)
- [Section 4.4: Logic Programming (논리 프로그래밍)](sec4.4-logic-programming.md)

### Chapter 5: Computing with Register Machines (레지스터 머신으로 계산하기)

추상화의 가장 아래 수준으로 내려간다. 레지스터 머신의 설계와 시뮬레이션, 메모리 관리와 가비지 컬렉션, 명시적 제어 평가기, 그리고 컴파일러 구현까지 — 소프트웨어가 하드웨어 위에서 실제로 어떻게 동작하는지를 밝힌다.

- [Section 5.1: Designing Register Machines (레지스터 머신 설계)](sec5.1-register-machines.md)
- [Section 5.2: A Register-Machine Simulator (레지스터 머신 시뮬레이터)](sec5.2-register-machine-simulator.md)
- [Section 5.3: Storage Allocation and Garbage Collection (저장소 할당과 가비지 컬렉션)](sec5.3-storage-and-gc.md)
- [Section 5.4: The Explicit-Control Evaluator (명시적 제어 평가기)](sec5.4-explicit-control-evaluator.md)
- [Section 5.5: Compilation (컴파일)](sec5.5-compilation.md)

---

## 학습 가이드

### 추천 읽기 순서

SICP는 순서대로 읽는 것을 강력히 권장한다. 각 챕터가 이전 챕터에서 구축한 개념 위에 새로운 층을 쌓기 때문이다.

**1단계: 함수적 추상화의 기초 (Chapter 1)**

프로그래밍의 세 가지 핵심 메커니즘(원시 요소, 결합, 추상화)을 배우고, 재귀적 사고와 고차 함수의 힘을 경험한다. 특히 Section 1.1의 치환 모델과 Section 1.3의 고차 함수는 이후 모든 챕터의 토대가 된다.

**2단계: 데이터 추상화 (Chapter 2)**

함수뿐 아니라 데이터도 추상화의 대상이 된다는 것을 배운다. 쌍(pair)이라는 단순한 접착제로 복잡한 데이터 구조를 구축하고, 추상화 장벽의 개념을 익힌다. Section 2.2의 닫힘 성질과 Section 2.4의 데이터 지향 프로그래밍은 핵심이다.

**3단계: 상태와 환경 (Chapter 3)**

변이를 도입하면서 프로그래밍 모델이 근본적으로 바뀐다. 치환 모델의 한계를 인식하고 환경 모델로 전환한다. Section 3.5의 스트림은 상태 없이 시간 변화를 모델링하는 우아한 대안을 제시한다.

**4단계: 언어 구현 (Chapter 4)**

프로그래밍의 궁극적 추상화 — 새로운 언어를 만드는 것. JavaScript 안에서 JavaScript 인터프리터를 구현하고, 평가 규칙을 변경하여 전혀 다른 계산 모델(지연 평가, 비결정적 컴퓨팅, 논리 프로그래밍)을 실현한다.

**5단계: 기계 수준의 계산 (Chapter 5)**

추상화의 최하단으로 내려가 프로세서가 어떻게 명령을 실행하는지를 이해한다. 4장의 인터프리터를 레지스터 머신으로 번역하고, 최종적으로 컴파일러를 구현한다.

---

## SICP의 핵심 주제

### 세 가지 핵심 메커니즘

모든 강력한 프로그래밍 언어가 갖추어야 할 메커니즘:

| 메커니즘 | 설명 | 예시 |
|----------|------|------|
| **원시 요소(Primitives)** | 언어가 제공하는 가장 단순한 개체 | 숫자, 문자열, 기본 연산자 |
| **결합 수단(Combination)** | 단순한 요소를 합쳐 복합 요소를 만드는 방법 | 연산자 조합, 함수 적용, 쌍 구성 |
| **추상화 수단(Abstraction)** | 복합 요소에 이름을 붙여 단위로 다루는 방법 | `const`, `function`, 데이터 추상화 |

### 다섯 개의 계산 모델

SICP는 점점 정교해지는 평가 모델을 단계적으로 도입한다:

| 모델 | 도입 시점 | 설명 |
|------|----------|------|
| **치환 모델** | Section 1.1 | 함수 적용을 텍스트 치환으로 이해 |
| **환경 모델** | Section 3.2 | 이름-값 바인딩을 프레임 체인으로 관리 |
| **메타순환 평가기** | Section 4.1 | JavaScript로 구현한 JavaScript 인터프리터 |
| **명시적 제어 평가기** | Section 5.4 | 레지스터 머신으로 구현한 평가기 |
| **컴파일러** | Section 5.5 | 소스 코드를 기계어로 번역 |

### 추상화의 네 가지 층위

| 층위 | 챕터 | 핵심 아이디어 |
|------|------|-------------|
| **함수적 추상화** | Chapter 1 | 함수로 계산 과정을 캡슐화 |
| **데이터 추상화** | Chapter 2 | 추상화 장벽으로 표현과 사용을 분리 |
| **상태와 모듈성** | Chapter 3 | 대입으로 객체 정체성 부여, 스트림으로 대안 제시 |
| **언어적 추상화** | Chapter 4-5 | 새로운 언어를 만들어 문제 영역에 맞는 표현력 확보 |
