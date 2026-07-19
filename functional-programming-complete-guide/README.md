# 함수형 프로그래밍 완전 가이드 (Functional Programming Complete Guide)

> 자체 구성 가이드. 두 개의 개인 학습 노트를 하나의 커리큘럼으로 재조립했다.
> 소스 1: [multi-paradigm-programming/](../multi-paradigm-programming/) — 『멀티패러다임 프로그래밍』(유인동, 한빛미디어, 2025) 책 노트
> 소스 2: [fp/](../fp/) — Notion 함수형 JS 노트 이관본 (FP with ES6+ · Functional JS · 실전 함수형)

ES5 시절의 `_filter`/`_map` 직접 구현부터 ES6+ 이터레이션 프로토콜, 지연 평가, 타입 시스템, 비동기/동시성, 그리고 OOP와 FP를 결합하는 멀티패러다임 설계까지 — **함수형 자바스크립트/타입스크립트를 개념 → 메커니즘 → 실전 순서로 학습**한다.

같은 주제가 여러 소스에 있으면 **멀티패러다임 > ES6+(FP with ES6+) > ES5(Functional JS)** 우선순위로 본문을 삼고, 하위 소스는 빌드업 과정·비교 관점으로 남겼다.

## 책 정보

| 항목 | 내용 |
|------|------|
| **성격** | 자체 구성 가이드 (5 Parts, 19개 챕터) — 두 학습 노트의 주제별 병합 |
| **소스** | 『멀티패러다임 프로그래밍』(유인동, 한빛미디어, 2025) 노트 + Notion 함수형 JS 노트(FP with ES6+ 10편·Functional JS 11편·실전 1편) |
| **언어** | TypeScript 위주 (비교용 JS/Haskell/Clojure 병용) |
| **대상 독자** | 함수형 JS/TS를 개념부터 실전까지 체계적으로 배우려는 개발자 |

---

## 전체 목차

### Part 1 — 함수형 프로그래밍 기초 (개념)

패러다임의 지도를 그리고, 함수를 값으로 다루는 사고방식을 ES5 스타일 직접 구현으로 다진다.

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|---|---|---|---|
| [1](ch01-what-is-functional-programming.md) | **What Is Functional Programming?** | 순수 함수 · 참조 투명성 · 일급 함수 · 고차 함수 · 클로저 | 패러다임 지도와 FP의 필수 개념 |
| [2](ch02-from-imperative-to-functional.md) | **From Imperative to Functional** | `_filter`/`_map` 빌드업 · 다형성 | for/if 절차 코드를 함수형으로 — 첫 리팩터링과 보조 함수 위임 |
| [3](ch03-currying-and-composition.md) | **Currying and Composition** | 커링 · `go`/`pipe` · reduce | 인자를 기억하는 함수와 순차 실행 — 함수 조합으로 함수 만들기 |
| [4](ch04-collection-centric-programming.md) | **Collection-Centric Programming** | 수집/거르기/찾기/축약 · group_by | 컬렉션 다루기 4유형과 파생 헬퍼(pluck·reject·compact 등) |

### Part 2 — 이터러블 중심 (메커니즘)

ES6 이터레이션 프로토콜 위에서 세 패러다임이 만나는 지점을 파고든다.

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|---|---|---|---|
| [5](ch05-iterator-pattern-and-iteration-protocol.md) | **Iterator Pattern and Iteration Protocol** | 이터레이터 · `Symbol.iterator` · 인터페이스 vs 상속 | GoF 반복자 패턴이 언어 표준(이터레이션 프로토콜)이 되기까지 |
| [6](ch06-generators.md) | **Generators** | 제너레이터 · `yield*` · 무한 시퀀스 | 문장으로 이터레이터를 만든다 — 명령형과 FP의 다리 |
| [7](ch07-higher-order-functions-for-iterables.md) | **Higher-Order Functions for Iterables** | forEach/map/filter 구현 · IteratorClose · reduce 오버로드 | 이터러블에 타입을 입힌 고차 함수 3종과 에러 관리 |
| [8](ch08-lazy-evaluation.md) | **Lazy Evaluation** | 지연 평가 · `L.*` · take/find · 결합 법칙 | 평가를 미루는 이터레이터 — 중첩 실행 순서와 효율 |

### Part 3 — 타입 시스템과 LISP

멀티패러다임 언어의 나머지 두 축: 타입 시스템과 메타프로그래밍.

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|---|---|---|---|
| [9](ch09-type-inference-and-generics.md) | **Type Inference and Generics** | 타입 추론 · 제네릭 · 함수 타입 | 고차 함수에 타입을 — 중첩 고차 함수의 추론까지 |
| [10](ch10-fxiterable-and-metaprogramming.md) | **FxIterable and Metaprogramming** | FxIterable · 파이프 연산자 · LISP 매크로 | 클래스+고차 함수+제네릭의 조합 — 코드가 데이터가 되는 LISP까지 |
| [11](ch11-learning-from-haskell.md) | **Learning from Haskell** | 하스켈 · 언어 차원 커링 · IO · Either | FP의 원형에서 배우기 — IP:OOP:FP 대응 관계 |

### Part 4 — 비동기

비동기를 값·지연성·타입으로 다루는 세 가지 층위.

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|---|---|---|---|
| [12](ch12-async-as-values.md) | **Async as Values** | Promise · race/all/allSettled/any | 비동기를 일급 값으로 — Promise 조합기와 타임아웃 |
| [13](ch13-monads-and-kleisli-composition.md) | **Monads and Kleisli Composition** | 모나드 · Kleisli 합성 · `then` 규칙 | 함수 합성을 안전하게 — 모나드 박스와 Kleisli 화살표 |
| [14](ch14-laziness-and-concurrency.md) | **Laziness and Concurrency** | nop · `C.*` · toAsync · FxAsyncIterable | 지연성과 동시성 — nop 방식과 toAsync 방식 두 계보 |
| [15](ch15-async-await-pipelines-and-error-handling.md) | **async/await, Pipelines, and Error Handling** | async/await vs 파이프라인 · 에러 핸들링 | 두 도구는 목적이 다르다 — 안정적 비동기 에러 처리 원칙 |

### Part 5 — 실전과 멀티패러다임

세 패러다임을 실제 문제에 조합해 적용한다.

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|---|---|---|---|
| [16](ch16-practical-list-processing-patterns.md) | **Practical List Processing Patterns** | FXTS · 리스트 프로세싱 패턴 9종 | 실전 데이터 다루기 — 백엔드 동기화 스케줄러까지 |
| [17](ch17-multi-paradigm-design.md) | **Multi-Paradigm Design** | 템플릿 엔진 · TaskPool | 구조는 OOP, 로직은 FP — 패러다임 조합 설계 |
| [18](ch18-oop-frontend-applications.md) | **OOP Frontend Applications** | 커스텀 이벤트 · 전략/상태 패턴 · View | Setting/Todo 앱으로 보는 OOP 프런트엔드 설계 |
| [19](ch19-conditions-and-effects-as-values.md) | **Conditions and Effects as Values** | Result 타입 · 패턴 매칭 · Effect-TS | 조건과 효과를 값으로 — fp-ts vs fxts 선택 기준 |

---

## 소스 매핑

각 장이 어느 원본에서 왔는지의 대조표. `멀티파` = [multi-paradigm-programming/](../multi-paradigm-programming/), `es6` = [fp/fp-with-es6-plus/](../fp/fp-with-es6-plus/), `es5` = [fp/functional-js/](../fp/functional-js/).

| Ch | 본문 (우선) | 보완 |
|---|---|---|
| 1 | 멀티파 ch00·ch01 §1.4 | es5 개론, es6 0-개론 |
| 2 | es5 1-절차지향 | es5 4-다형성 |
| 3 | es6 4-코드를-값으로 | es5 2-커링, es5 3-연속적인-함수-실행 |
| 4 | es5 컬렉션-중심 5편 | — |
| 5 | 멀티파 ch01 §1·§3·§5 | es6 1-리스트와-이터러블 |
| 6 | 멀티파 ch01 §2 | es6 2-제너레이터 |
| 7 | 멀티파 ch01 §4 + ch02 §2.2 | es6 3-map-filter-reduce |
| 8 | 멀티파 ch03 §3·§4 | es6 5-지연성-1, es6 6-지연성-2 |
| 9 | 멀티파 ch02 §1·§2.1·§2.3 | — |
| 10 | 멀티파 ch02 §3 | — |
| 11 | 멀티파 ch03 §1·§2 | — |
| 12 | 멀티파 ch04 §1 | es6 7 §1~3 |
| 13 | es6 7 §4~5·§7 | 멀티파 ch03 §2.8(Either) 교차 |
| 14 | 멀티파 ch04 §2·§3 | es6 7 §6, es6 8 |
| 15 | 멀티파 ch04 §4 | es6 9 |
| 16 | 멀티파 ch05 | es5 group_by/count_by 교차 링크 |
| 17 | 멀티파 ch06 | — |
| 18 | 멀티파 ch07 | — |
| 19 | fp 실전-함수형-프로그래밍 | fp-ts-vs-fxts |

---

## 코드 표기법 로드맵

이 가이드의 코드 표기는 하나로 통일되어 있지 않고, **학습 순서를 따라 진화**한다. 같은 원리가 시대와 타입 시스템의 제약에 따라 어떻게 다른 표면 문법으로 수렴했는지 자체가 학습 내용이다.

`_filter(list, f)` (es5) → `go(list, filter(f), ...)` + `L.*`/`C.*` (es6/fxjs) → `fx(list).filter(f)` (FxIterable, TS) → FXTS `pipe`·`fx` (실전 라이브러리)

| 표기 | 정체 | 주 등장 장 | 정의/구현 위치 |
|---|---|---|---|
| `_filter`·`_go` 등 `_` 접두어 | es5 직접 구현 (인덱스·arguments 기반) | Ch2·4 | Ch2 (Ch3는 개념 설명만) |
| `go`·`pipe`·`curry` | es6 파이프라인 (전개 연산자·나머지 매개변수) | Ch3~4·8·14~15 | Ch3 §5 |
| `map(f, iterable)` 자유 함수 | 이터러블 헬퍼 (표기 중립, 타입 부여) | Ch5~9 | Ch7 |
| `L.*`(지연)·`C.*`(병렬)·`nop` | fxjs 계열 직접 구현 | Ch8·14 | Ch8 §4, Ch14 §6·9 |
| `fx()` 체이닝 | FxIterable/FxAsyncIterable (TS 클래스) | Ch8 일부·10~11·14 | Ch10 §2, Ch14 §12 |
| FXTS `pipe`·`fx`·`concurrent` | 실전 라이브러리 | Ch16~17 | 선택 기준: Ch19 §5 |

왜 표기가 바뀌는가 — 동적 타입 JS에서는 `go`/`pipe` + `L.*` 파이프라인이 간결하고 충분했지만, 타입스크립트의 가변 인자 파이프는 단계 간 타입을 잇는 오버로드가 다수 필요하고 중간에서 추론이 끊기기 쉽다. 그래서 각 메서드가 원소 타입을 아는 상태에서 시작하는 **메서드 체이닝(fx)**으로 진화했다. 혼재는 의도된 것이다 — 같은 원리의 두 세대를 나란히 두어 진화 이유를 학습 내용으로 삼는다. 상세는 Ch8 서두의 표기법 안내와 Ch14 §13(nop 방식 vs toAsync 방식 비교)을 참고한다.

---

## 학습 가이드

### 처음 읽는 경우

Part 1부터 순서대로. Part 1(개념·ES5 직접 구현)이 손에 익으면 Part 2(ES6 프로토콜)가 "언어가 이 패턴을 표준화한 것"으로 읽힌다.

### 이미 FP 기초가 있다면

- Part 2 (Ch5-8) — 이터레이션 프로토콜과 지연 평가부터
- Part 4 (Ch12-15) — 비동기를 값으로 다루는 관점
- Part 5 (Ch16-18) — 실전 조합

### 비동기만 집중하고 싶다면

Ch12(값) → Ch13(합성 안전성) → Ch14(지연·동시성) → Ch15(에러 핸들링) 순서가 하나의 완결된 트랙이다.

### 설계 관점이 궁금하다면

Ch5(인터페이스 vs 상속) → Ch10(FxIterable) → Ch17(구조=OOP·로직=FP) → Ch18(프런트엔드 응용)

---

## 핵심 개념 맵

- **일급 함수 → 고차 함수 → 커링/합성**: 함수로 함수를 만든다 — FP의 뼈대 (Part 1)
- **이터레이션 프로토콜 = 세 패러다임의 교차점**: 반복자 패턴(OOP)·제너레이터(명령형)·리스트 프로세싱(FP)이 같은 규약 위에서 만난다 (Part 2)
- **지연 평가**: 평가 시점을 다루는 기술 — `L.*` 구현과 fx 체이닝이 같은 원리의 두 표기 (Ch8·10)
- **비동기도 값이다**: Promise(값) → 모나드/Kleisli(안전한 합성) → `C.*`(동시성 제어)로 층위가 쌓인다 (Part 4)
- **표기법의 진화 자체가 커리큘럼**: `_f` → `go/pipe` → `fx()` → FXTS — 타입 시스템 제약이 표면 문법을 바꾼다 (코드 표기법 로드맵 참조)
- **멀티패러다임 설계**: 구조=OOP·로직=FP·문장=명령형의 조합이 실전의 답 (Part 5)

---

## 인용문

전 책 통합 모음은 [루트 QUOTES.md](../QUOTES.md) 참조.

> 우리는 함수형, 객체지향, 명령형 패러다임을 제공하는 멀티패러다임 언어를 효율적으로 활용하는 법을 배워야 한다. 많은 툴이 개선되었고 이제는 어떻게 잘 사용할지를 배울 차례다. 그리고 이제는 오랫동안 각기 고유했고 심지어 갈등 속에 있던 패러다임들을 섞어야 할 때다.<br>— 마이크 루키데스(Mike Loukides) (위치: Ch1 — 멀티파 서문 재인용)

> 함수형 사고방식은 문제의 해결 방법을 동사(함수)들로 구성(조합)하는 것.<br>— 마이클 포거스(Michael Fogus) (위치: Ch1)

---

## 노트의 구성 요소

- `## 핵심 질문` — 챕터가 답하려는 물음 (인라인 텍스트)
- 번호가 매겨진 주요 섹션 (`## 1.`, `## 2.`, ...)
- `> **핵심 통찰**:` 콜아웃 — 핵심 인사이트
- `> **참고**:` — 보조 정보
- `(*Term - 설명*)` 인라인 이탤릭 — 처음 등장하는 용어 설명
- 코드는 **TypeScript** 위주(비교용 JS/Haskell/Clojure 등 병용). 코드 블록은 원본 노트의 코드를 유지
- `## 요약` — 챕터 마지막 불릿 정리
- `## 다른 챕터와의 관계` — 교차 링크

---

## 관련 폴더

- [multi-paradigm-programming/](../multi-paradigm-programming/) — 원본 책 노트 (ch00~07)
- [fp/](../fp/) — 원본 Notion 이관 노트 (fp-with-es6-plus 10편 + functional-js 11편 + 실전 함수형)
- [structure-and-interpretation-of-computer-programs-javascript/](../structure-and-interpretation-of-computer-programs-javascript/) — 함수형 사고의 뿌리 (SICP)
