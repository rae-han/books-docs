# 컴퓨터 프로그램의 구조와 해석 (SICP: JavaScript Edition)

> *Structure and Interpretation of Computer Programs, JavaScript Edition* (Harold Abelson, Gerald Jay Sussman with Julie Sussman / JavaScript 개편: Martin Henz, Tobias Wrigstad, MIT Press, 2022)
> 한국어판: 『컴퓨터 프로그램의 구조와 해석: 자바스크립트 에디션』 (류광 옮김, 인사이트) · 온라인: https://sicp.sourceacademy.org/

1985년 초판 이래 컴퓨터 과학 교육의 고전인 MIT 입문 교재("마법사 책"). JavaScript Edition은 원서의 Scheme 코드를 JavaScript로 옮기면서 SICP의 핵심 철학 — **계산적 사고와 추상화의 힘** — 을 온전히 보존한다.

## 책 정보

| 항목 | 내용 |
|------|------|
| **원저자** | 해럴드 에이블슨·제럴드 제이 서스먼 (MIT) |
| **JS 개편** | 마틴 헨츠·토비아스 브리스타드 |
| **역자** | 류광 |
| **출판** | 인사이트 (원서: MIT Press, 2022) |
| **예제 언어** | JavaScript (화살표 함수·const 등 현대 문법) |
| **대상 독자** | CS 기초 개념을 체계적으로 배우려는 개발자, 함수형 프로그래밍의 원리를 깊이 이해하고 싶은 개발자 |

## 개요

특정 언어의 문법이나 라이브러리가 아니라 **프로그래밍의 본질적 개념**을 가르치는 책이다. 함수를 값으로 다루기, 데이터 추상화, 상태와 변이, 메타언어적 추상화, 기계 수준의 계산까지 — 한 권이 소프트웨어의 가장 낮은 수준부터 가장 높은 수준까지 관통한다.

원시 요소에서 시작해 점점 강력한 추상화를 쌓아올리고 마침내 언어 자체를 구현하는 데까지 나아간다. 뉴턴의 제곱근, 유리수 연산, Picture Language, 기호 미분, 회로 시뮬레이터, 레지스터 머신 등 정교하게 설계된 예제로 개념을 체화시킨다.

## 목차

### Chapter 1: Building Abstractions with Functions (함수를 이용한 추상화 구축)

| Sec | 제목 | 핵심 단어 | 한 줄 요약 |
|-----|------|-----------|-----------|
| 1.1 | [The Elements of Programming](sec1.1-elements-of-programming.md) | 원시 요소 · 결합 · 추상화 · 치환 모델 | 프로그래밍의 3대 메커니즘과 치환 모델 — 뉴턴 제곱근 예제 |
| 1.2 | [Functions and the Processes They Generate](sec1.2-functions-and-processes.md) | 재귀 프로세스 · 반복 프로세스 · 트리 재귀 · 증가 차수 | 함수가 생성하는 프로세스의 '모양' — 재귀와 반복, 계산 복잡도 |
| 1.3 | [Formulating Abstractions with Higher-Order Functions](sec1.3-higher-order-functions.md) | 고차 함수 · 람다 표현식 · 일급 함수 · 고정점 | 함수를 받고 반환하는 함수로 '일반적 방법' 자체를 추상화 |

### Chapter 2: Building Abstractions with Data (데이터를 이용한 추상화 구축)

| Sec | 제목 | 핵심 단어 | 한 줄 요약 |
|-----|------|-----------|-----------|
| 2.1 | [Introduction to Data Abstraction](sec2.1-data-abstraction.md) | 데이터 추상화 · 추상화 장벽 · 쌍 | 유리수 연산 — 표현과 사용을 분리하는 추상화 장벽 |
| 2.2 | [Hierarchical Data and the Closure Property](sec2.2-hierarchical-data.md) | 닫힘 성질 · 리스트 · 트리 · 그림 언어 | 쌍이라는 접착제로 계층 구조 구축 — Picture Language |
| 2.3 | [Symbolic Data](sec2.3-symbolic-data.md) | 기호 데이터 · 기호 미분 · 집합 표현 | 기호를 데이터로 다루기 — 수식을 미분하는 프로그램 |
| 2.4 | [Multiple Representations for Abstract Data](sec2.4-multiple-representations.md) | 다중 표현 · 태그 데이터 · 데이터 지향 프로그래밍 | 복소수 예제 — 한 데이터에 여러 표현이 공존하는 시스템 설계 |
| 2.5 | [Systems with Generic Operations](sec2.5-generic-operations.md) | 제네릭 연산 · 강제 변환 · 타입 타워 | 정수→유리수→실수→복소수를 아우르는 제네릭 산술 패키지 |

### Chapter 3: Modularity, Objects, and State (모듈성, 객체, 그리고 상태)

| Sec | 제목 | 핵심 단어 | 한 줄 요약 |
|-----|------|-----------|-----------|
| 3.1 | [Assignment and Local State](sec3.1-assignment-and-local-state.md) | 대입 · 지역 상태 · 참조 투명성 | 은행 계좌로 대입 도입 — 얻는 것(모듈성)과 잃는 것(치환 모델) |
| 3.2 | [The Environment Model of Evaluation](sec3.2-environment-model.md) | 환경 모델 · 프레임 · 클로저 | 대입 이후의 새 평가 모델 — 이름-값 바인딩의 프레임 체인 |
| 3.3 | [Modeling with Mutable Data](sec3.3-mutable-data.md) | 변이 가능 데이터 · 큐 · 테이블 · 회로 시뮬레이터 | 변이 데이터 구조와 이벤트 주도 디지털 회로 시뮬레이션 |
| 3.4 | [Concurrency: Time Is of the Essence](sec3.4-concurrency.md) | 동시성 · 직렬 변환기 · 교착 상태 | 상태 + 시간 = 동시성 문제 — 공유 상태의 본질적 어려움 |
| 3.5 | [Streams](sec3.5-streams.md) | 스트림 · 지연 평가 · 무한 수열 | 상태 없이 시간을 모델링하는 대안 — 스트림 패러다임 |

### Chapter 4: Metalinguistic Abstraction (메타언어적 추상화)

| Sec | 제목 | 핵심 단어 | 한 줄 요약 |
|-----|------|-----------|-----------|
| 4.1 | [The Metacircular Evaluator](sec4.1-metacircular-evaluator.md) | 메타순환 평가기 · evaluate/apply | JavaScript로 JavaScript 인터프리터를 — 평가기의 심장 evaluate-apply 루프 |
| 4.2 | [Lazy Evaluation](sec4.2-lazy-evaluation.md) | 지연 평가 · 썽크 · 정규 순서 | 평가 규칙을 바꿔 만드는 게으른 언어 |
| 4.3 | [Nondeterministic Computing](sec4.3-nondeterministic-computing.md) | 비결정적 컴퓨팅 · amb · 백트래킹 | amb 연산자로 '탐색'을 언어에 내장 — 논리 퍼즐 풀기 |
| 4.4 | [Logic Programming](sec4.4-logic-programming.md) | 논리 프로그래밍 · 질의 언어 · 단일화 | 선언적 지식으로 계산하는 질의 언어 구현 |

### Chapter 5: Computing with Register Machines (레지스터 머신으로 계산하기)

| Sec | 제목 | 핵심 단어 | 한 줄 요약 |
|-----|------|-----------|-----------|
| 5.1 | [Designing Register Machines](sec5.1-register-machines.md) | 레지스터 머신 · 데이터 경로 · 컨트롤러 | GCD 머신 — 계산을 기계 수준의 언어로 기술 |
| 5.2 | [A Register-Machine Simulator](sec5.2-register-machine-simulator.md) | 시뮬레이터 · 어셈블러 | 레지스터 머신 시뮬레이터를 JavaScript로 구현 |
| 5.3 | [Storage Allocation and Garbage Collection](sec5.3-storage-and-gc.md) | 벡터 · 가비지 컬렉션 · stop-and-copy | 리스트가 메모리에 놓이는 법과 GC 알고리즘 |
| 5.4 | [The Explicit-Control Evaluator](sec5.4-explicit-control-evaluator.md) | 명시적 제어 평가기 · 꼬리 호출 | 4장의 평가기를 레지스터 머신 명령으로 번역 |
| 5.5 | [Compilation](sec5.5-compilation.md) | 컴파일 · 코드 생성 · 레지스터 최적화 | 인터프리터에서 컴파일러로 — 번역의 원리 |

## 학습 가이드

순서대로 읽는 것을 강력히 권장한다 — 각 챕터가 이전 챕터의 개념 위에 새 층을 쌓는다.

1. **Ch1 — 함수적 추상화**: 특히 1.1의 치환 모델과 1.3의 고차 함수가 이후 전체의 토대
2. **Ch2 — 데이터 추상화**: 2.2의 닫힘 성질, 2.4의 데이터 지향 프로그래밍이 핵심
3. **Ch3 — 상태와 환경**: 변이 도입으로 치환 모델이 무너지고 환경 모델로 전환. 3.5 스트림은 우아한 대안
4. **Ch4 — 언어 구현**: 궁극의 추상화. 4.1 메타순환 평가기가 백미
5. **Ch5 — 기계 수준**: 4장의 인터프리터를 레지스터 머신으로, 마지막엔 컴파일러로

## 핵심 개념 맵

### 세 가지 핵심 메커니즘

| 메커니즘 | 설명 | 예시 |
|----------|------|------|
| **원시 요소(Primitives)** | 언어가 제공하는 가장 단순한 개체 | 숫자, 문자열, 기본 연산자 |
| **결합 수단(Combination)** | 단순한 요소를 합쳐 복합 요소를 만드는 방법 | 연산자 조합, 함수 적용, 쌍 구성 |
| **추상화 수단(Abstraction)** | 복합 요소에 이름을 붙여 단위로 다루는 방법 | `const`, `function`, 데이터 추상화 |

### 다섯 개의 계산 모델

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

## 시그니처 요소와 표기 규칙

- `## 핵심 개념` — 섹션에서 도입되는 중요 개념 정의
- `## 주요 예제` — SICP 핵심 예제 코드와 상세 설명
- `## 계산 모델` — 치환 모델·환경 모델 등 평가 모델 설명
- `## 연습 문제 하이라이트` — 유명한 연습 문제 소개와 풀이
- 파일 네이밍: `sec{챕터}.{섹션}-{영문-kebab-case}.md`

## Notion DB 구조

- 위치: Raehan's Must reads 하위 챕터 DB (재업로드 완료, 전체 22파일)
