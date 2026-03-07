# Learning JavaScript Design Patterns (자바스크립트 + 리액트 디자인 패턴)

> **Addy Osmani** 저, *Learning JavaScript Design Patterns* (2nd Edition, O'Reilly, 2023) 학습 노트

---

## 개요

이 노트는 Addy Osmani의 「Learning JavaScript Design Patterns」 2판을 기반으로, **책 없이도 핵심 개념을 학습할 수 있는 수준**으로 상세하게 정리한 한국어 학습 자료다. 원서의 15개 챕터를 재구성하여 16개 챕터로 나누었으며, 모든 코드 예시는 **TypeScript**로 작성되었다.

### 원서와의 차이점

| 항목 | 원서 (2023) | 이 노트 (2026) |
|------|-------------|-----------------|
| **언어** | JavaScript (ES2022) | TypeScript |
| **React** | React 18 | React 19 (use, Server Actions, React Compiler) |
| **Next.js** | Next.js 13 | Next.js 15 (App Router, PPR) |
| **상태 관리** | Redux 중심 | Zustand, Jotai 등 경량 라이브러리 포함 |
| **모듈** | AMD/CJS/UMD 상세 | ES Modules 중심, 역사적 포맷은 최소화 |
| **렌더링** | CSR/SSR/SSG/ISR | + RSC, Islands Architecture, Streaming SSR, PPR |
| **ECMAScript** | ES2022 | ES2024+ (Decorators, `using`, `Promise.withResolvers()`) |
| **챕터 구성** | Ch7 통합 (모든 패턴) | 생성/구조/행위 3개 챕터로 분리 |

---

## 목차

### Part I: 기초 (Foundation)

| 챕터 | 제목 | 핵심 내용 |
|------|------|-----------|
| [Ch01](ch01-introduction-to-design-patterns.md) | Introduction to Design Patterns | 디자인 패턴의 역사 (알렉산더 → GoF), 패턴의 정의와 가치, 현대 JS에서의 위치 |
| [Ch02](ch02-patternity-testing-and-proto-patterns.md) | "Pattern"-ity Testing, Proto-Patterns, and the Rule of Three | 프로토 패턴, 패턴 검증 기준, 세 가지 법칙 |
| [Ch03](ch03-structuring-design-patterns.md) | Structuring Design Patterns | 패턴 문서화 방법, 디자인 패턴의 구조와 구성 요소 |
| [Ch04](ch04-anti-patterns.md) | Anti-Patterns | 안티패턴의 정의, JS/React에서 흔한 안티패턴, 리팩터링 방향 |

### Part II: 언어 기반 (Language Foundations)

| 챕터 | 제목 | 핵심 내용 |
|------|------|-----------|
| [Ch05](ch05-modern-javascript-syntax-and-features.md) | Modern JavaScript Syntax and Features | ES2015~ES2024+ 주요 문법, 클래스, 모듈, 비동기, `#private`, `using` |
| [Ch06](ch06-categories-of-design-patterns.md) | Categories of Design Patterns | GoF 23가지 패턴의 생성/구조/행위 분류 체계, 각 카테고리 개요 |

### Part III: 디자인 패턴 (Design Patterns)

| 챕터 | 제목 | 다루는 패턴 |
|------|------|-------------|
| [Ch07](ch07-creational-patterns.md) | Creational Patterns | Constructor, Factory Method, Abstract Factory, Builder, Singleton, Prototype |
| [Ch08](ch08-structural-patterns.md) | Structural Patterns | Facade, Mixin, Decorator, Flyweight, Adapter, Proxy, Composite |
| [Ch09](ch09-behavioral-patterns.md) | Behavioral Patterns | Observer, Mediator, Command, Iterator, Strategy, State, Template Method, Chain of Responsibility, Visitor |

### Part IV: 아키텍처 패턴 (Architectural Patterns)

| 챕터 | 제목 | 핵심 내용 |
|------|------|-----------|
| [Ch10](ch10-mv-star-patterns.md) | MV* Patterns | MVC, MVP, MVVM의 원리와 차이, 현대 프레임워크에서의 진화 |
| [Ch11](ch11-asynchronous-programming-patterns.md) | Asynchronous Programming Patterns | Promise, async/await, AsyncIterator, Observable, Signals, 동시성 제어 |
| [Ch12](ch12-modular-javascript-design-patterns.md) | Modular JavaScript Design Patterns | AMD/CJS/UMD 역사, ES Modules, Import Maps, 번들러(Vite, Turbopack), Tree Shaking |
| [Ch13](ch13-namespacing-patterns.md) | Namespacing Patterns | 전통적 네임스페이스 기법, ES Modules 시대의 재평가 |

### Part V: 리액트 패턴 (React Patterns)

| 챕터 | 제목 | 핵심 내용 |
|------|------|-----------|
| [Ch14](ch14-react-design-patterns.md) | React Design Patterns | HOC, Render Props, Hooks, 합성 패턴, 상태 관리, Code Splitting, React 19 |
| [Ch15](ch15-rendering-patterns.md) | Rendering Patterns | CSR, SSR, SSG, ISR, Streaming SSR, RSC, Islands Architecture, PPR, Core Web Vitals |
| [Ch16](ch16-react-application-structure.md) | React Application Structure | 폴더 구조, 상태 관리 전략, Next.js App Router, 데이터 패칭, Server Actions |

---

## 각 챕터 공통 구성

모든 챕터는 다음 구조를 따른다:

- **핵심 질문** — 챕터가 답하고자 하는 근본적 물음
- **번호 섹션** — 본문 내용 (상세 설명 + 코드 예시)
- **패턴 카드** — 각 디자인 패턴의 의도, 사용 시점, 장단점 요약 (Ch07~Ch09)
- **최신 업데이트 (2026)** — 원서 출판 이후 변경된 기술 동향
- **실무 적용 가이드** — 실무 적용 체크리스트
- **요약** — 핵심 포인트 불릿 정리
- **다른 챕터와의 관계** — 챕터 간 연결고리

---

## 특수 요소

- `> **Osmani의 조언**:` — 저자의 실용적 조언
- `> **핵심 통찰**:` — 주요 인사이트 강조
- `### 패턴 카드: [패턴명]` — 패턴 요약 (의도, 사용 시점, 장단점)
- `### 전통 vs 현대` — 전통적 구현과 현대적 구현의 코드 비교
- `### JS vs TS 비교` — TypeScript 고유 기능이 가치를 더하는 경우의 비교

---

## 대상 독자

- 자바스크립트/타입스크립트 기본 문법을 알고 있는 개발자
- 디자인 패턴을 체계적으로 학습하고 싶은 프론트엔드 개발자
- React/Next.js 프로젝트에서 패턴 기반 설계를 적용하고 싶은 개발자

---

## 원서 정보

- **제목**: Learning JavaScript Design Patterns (2nd Edition)
- **저자**: Addy Osmani
- **출판사**: O'Reilly Media
- **출판년도**: 2023
- **ISBN**: 978-1-098-13987-7
