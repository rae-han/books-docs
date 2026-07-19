# 자바스크립트 + 리액트 디자인 패턴 (Learning JavaScript Design Patterns, 2nd Edition)

> *Learning JavaScript Design Patterns* (2nd Edition, Addy Osmani, O'Reilly, 2023. ISBN 978-1-098-13987-7)
> 이 폴더는 원서 기반의 한국어 학습 노트 — 원서 15개 챕터를 16개로 재구성, 코드는 전부 TypeScript

크롬 팀의 Addy Osmani가 쓴 JS 생태계 디자인 패턴 책. GoF 패턴의 JS/TS 구현부터 MV* 아키텍처, 비동기·모듈 패턴, React 패턴과 렌더링 전략까지 프런트엔드 관점으로 관통한다.

## 책 정보

| 항목 | 내용 |
|------|------|
| **저자** | 애디 오스마니(Addy Osmani) |
| **원서** | O'Reilly, 2nd Edition 2023 (노트는 2026 기술 동향 반영) |
| **노트 언어** | TypeScript (React 19·Next.js 15 기준 업데이트) |
| **대상 독자** | JS/TS 기본기를 갖추고 패턴 기반 설계를 적용하려는 프런트엔드 개발자 |

## 개요

이 노트는 원서를 기반으로 하되 출판 이후의 변화를 적극 반영했다 — 챕터마다 `최신 업데이트 (2026)` 절이 있다.

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

## 목차

### Part I: 기초 (Ch 1-4)

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 1 | [Introduction to Design Patterns](ch01-introduction-to-design-patterns.md) | 패턴의 역사 · GoF | 알렉산더에서 GoF까지 — 현대 JS에서 패턴의 위치 |
| 2 | ["Pattern"-ity Testing, Proto-Patterns, and the Rule of Three](ch02-patternity-testing-and-proto-patterns.md) | 프로토 패턴 · 3의 법칙 | 패턴이 패턴으로 인정받는 검증 기준 |
| 3 | [Structuring Design Patterns](ch03-structuring-design-patterns.md) | 패턴 문서화 구조 | 좋은 패턴 설명서의 구성 요소 |
| 4 | [Anti-Patterns](ch04-anti-patterns.md) | 안티패턴 | JS/React에서 흔한 안티패턴과 리팩터링 방향 |

### Part II: 언어 기반 (Ch 5-6)

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 5 | [Modern JavaScript Syntax and Features](ch05-modern-javascript-syntax-and-features.md) | ES2015~2024+ · 클래스 · 모듈 | 패턴 구현의 언어 재료 — `#private`·`using`까지 |
| 6 | [Categories of Design Patterns](ch06-categories-of-design-patterns.md) | 생성/구조/행위 분류 | GoF 23가지 패턴의 분류 체계 개관 |

### Part III: 디자인 패턴 (Ch 7-9)

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 7 | [Creational Patterns](ch07-creational-patterns.md) | 팩토리 · 빌더 · 싱글턴 · 프로토타입 | 객체 생성 6패턴의 TS 구현 — ES 모듈=싱글턴 관점 포함 |
| 8 | [Structural Patterns](ch08-structural-patterns.md) | 퍼사드 · 데코레이터 · 어댑터 · 프록시 · 컴포지트 · 믹스인 · 플라이웨이트 | 구조 7패턴 — `Proxy` 내장 객체와 반응성의 관계 |
| 9 | [Behavioral Patterns](ch09-behavioral-patterns.md) | 옵저버 · 중재자 · 커맨드 · 전략 · 상태 · 이터레이터 | 행위 9패턴 — 일급 함수가 패턴을 단순화하는 지점 |

### Part IV: 아키텍처 패턴 (Ch 10-13)

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 10 | [MV* Patterns](ch10-mv-star-patterns.md) | MVC · MVP · MVVM | MV* 삼형제의 원리와 현대 프레임워크에서의 진화 |
| 11 | [Asynchronous Programming Patterns](ch11-asynchronous-programming-patterns.md) | Promise · AsyncIterator · Observable · Signals | 비동기 패턴의 스펙트럼 — 동시성 제어까지 |
| 12 | [Modular JavaScript Design Patterns](ch12-modular-javascript-design-patterns.md) | ES Modules · Import Maps · 번들러 · Tree Shaking | 모듈 시스템의 역사와 현재 — Vite·Turbopack 시대 |
| 13 | [Namespacing Patterns](ch13-namespacing-patterns.md) | 네임스페이스 | 전통적 네임스페이스 기법과 ESM 시대의 재평가 |

### Part V: 리액트 패턴 (Ch 14-16)

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 14 | [React Design Patterns](ch14-react-design-patterns.md) | HOC · Render Props · Hooks · 합성 | React 패턴의 진화 — HOC에서 Hooks·React 19까지 |
| 15 | [Rendering Patterns](ch15-rendering-patterns.md) | CSR/SSR/SSG/ISR · RSC · Islands · PPR | 렌더링 전략 지도 — Core Web Vitals 기준 선택법 |
| 16 | [React Application Structure](ch16-react-application-structure.md) | 폴더 구조 · App Router · Server Actions | 애플리케이션 구조와 데이터 패칭 전략 |

## 학습 가이드

1. **Part I~II(Ch1~6)로 어휘와 재료** — 패턴의 정의·분류와 최신 JS 문법
2. **Part III(Ch7~9)는 패턴 카드 중심으로** — 필요한 패턴만 찾아 읽어도 되는 카탈로그
3. **Part IV(Ch10~13)는 아키텍처 관점** — MV*와 비동기·모듈은 React 이해의 배경 지식
4. **Part V(Ch14~16)가 실무 종착지** — React/Next.js 프로젝트라면 여기부터 역으로 필요한 장을 찾아가도 좋다
5. GoF 패턴을 예제 중심으로 처음 배우려면 [head-first-design-patterns/](../head-first-design-patterns/)를 먼저 — 이 책은 JS 생태계 응용에 강점

## 핵심 개념 맵

- **패턴 = 검증된 어휘**: 3의 법칙을 통과한 반복 해법 — 안티패턴은 그 반면교사 (Ch1~4)
- **언어가 패턴을 흡수한다**: 모듈=싱글턴, `Proxy` 내장, 일급 함수=커맨드/전략 — JS에서 패턴은 더 가볍다 (Ch5·7~9)
- **MV* → 컴포넌트**: MVC/MVVM의 관심사 분리가 React의 컴포넌트+훅 모델로 진화 (Ch10·14)
- **비동기 패턴의 층위**: 콜백 → Promise → AsyncIterator/Observable → Signals (Ch11)
- **렌더링은 트레이드오프**: CSR↔SSR↔RSC 스펙트럼에서 Core Web Vitals 기준으로 선택 (Ch15)
- **패턴 카드 + 최신 업데이트(2026)**: 각 패턴을 의도/사용 시점/장단점으로 요약하고 시효를 관리

## 시그니처 요소와 표기 규칙

- `### 패턴 카드: [패턴명]` — 의도·사용 시점·장단점 요약 (Ch07~09)
- `> **Osmani의 조언**:` / `> **핵심 통찰**:` 콜아웃
- `### 전통 vs 현대` — 전통적 구현과 현대적 구현의 코드 비교
- `### JS vs TS 비교` — TS 고유 기능(매개변수 프로퍼티·private constructor·판별 유니언)이 가치를 더하는 경우만
- `최신 업데이트 (2026)` · `실무 적용 가이드` · `다른 챕터와의 관계` 절
