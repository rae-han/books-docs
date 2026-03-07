# Chapter 03: Structuring Design Patterns (디자인 패턴 구조화)

## 핵심 질문

> 디자인 패턴은 어떤 구조로 문서화되며, 모범적인 패턴 문서를 작성하기 위한 조건과 체크리스트는 무엇인가?

---

## 1. 디자인 패턴의 구조: 세 가지 핵심 요소

디자인 패턴은 단순한 코드 조각이 아니다. 패턴은 **문제가 발생하는 상황**, **그 상황에서 작용하는 힘**, **그 힘을 해소하는 구성** 세 가지 요소로 이루어진다. 이 구조는 건축가 크리스토퍼 알렉산더가 제안한 것으로, 소프트웨어 디자인 패턴에도 그대로 적용된다.

### 세 가지 핵심 요소

| 요소 | 영문 | 설명 |
|------|------|------|
| **컨텍스트** | Context | 패턴이 적용되는 **상황**을 설명한다. 어떤 환경에서 문제가 발생하는가? |
| **집중 목표** | System of Forces | 해당 컨텍스트 안에서 작용하는 **상충하는 힘들**(*forces*)을 설명한다. 서로 대립하는 요구 사항이 무엇인가? |
| **구성** | Configuration | 상충하는 힘들을 해소하여 **균형을 이루는 해결 방법**을 설명한다 |

이 세 가지 요소는 서로 긴밀하게 연결되어 있다. 컨텍스트가 달라지면 작용하는 힘도 달라지고, 따라서 적절한 구성도 달라진다. 같은 "옵저버 패턴"이라도 UI 이벤트 처리와 분산 시스템 메시징에서의 적용은 상당히 다를 수 있다.

### 세 가지 요소의 구체적 예시: 싱글턴 패턴

```typescript
// 컨텍스트:
// 애플리케이션 전체에서 하나의 설정 객체만 존재해야 한다.
// 여러 모듈에서 동시에 설정에 접근하고 수정할 수 있다.

// 집중 목표 (상충하는 힘들):
// 힘 1: 어디서든 설정에 접근할 수 있어야 한다 (접근성)
// 힘 2: 설정 객체가 여러 개 생기면 상태 불일치가 발생한다 (일관성)
// 힘 3: 전역 변수는 네임스페이스를 오염시킨다 (캡슐화)

// 구성 (힘의 해소):
class AppConfig {
  private static instance: AppConfig | null = null;
  private settings: Map<string, unknown> = new Map();

  private constructor() {}

  static getInstance(): AppConfig {
    if (!AppConfig.instance) {
      AppConfig.instance = new AppConfig();
    }
    return AppConfig.instance;
  }

  get<T>(key: string): T | undefined {
    return this.settings.get(key) as T | undefined;
  }

  set(key: string, value: unknown): void {
    this.settings.set(key, value);
  }
}

// 접근성: getInstance()로 어디서든 접근 가능
// 일관성: 단 하나의 인스턴스만 존재
// 캡슐화: private constructor로 직접 생성 방지
```

> **핵심 통찰**: 디자인 패턴의 핵심은 코드가 아니라 **상충하는 힘들 사이의 균형**이다. 같은 패턴이라도 컨텍스트(상황)가 다르면 적용 방식이 달라지며, 집중 목표(힘)가 다르면 아예 다른 패턴을 선택해야 할 수도 있다.

---

## 2. 패턴 구성 요소: 필수 5가지와 보조 8가지

GoF의 디자인 패턴 이후, 패턴 커뮤니티에서는 패턴을 문서화할 때 포함해야 할 구성 요소를 정립했다. 이 중 **가장 중요한 5가지**를 먼저 살펴보고, 나머지 보조 요소를 이어서 설명한다.

### 핵심 5가지 구성 요소

| # | 구성 요소 | 설명 |
|---|-----------|------|
| 1 | **이름** (*Pattern Name*) | 패턴의 목적을 직관적으로 전달하는 이름. 개발자 간 의사소통의 핵심 |
| 2 | **설명** (*Description*) | 패턴이 무엇인지 간략하게 서술 |
| 3 | **컨텍스트 개요** (*Context Outline*) | 패턴이 효과적으로 사용되는 상황과 조건 설명 |
| 4 | **문제 제시** (*Problem Statement*) | 패턴이 해결하고자 하는 문제를 명확히 기술 |
| 5 | **해결 방법** (*Solution*) | 문제를 해결하는 방법을 단계별로 설명 |

### 보조 8가지 구성 요소

| # | 구성 요소 | 설명 |
|---|-----------|------|
| 6 | **설계 내용** (*Design*) | 패턴의 구조적 설계와 사용자와의 상호작용 방식 |
| 7 | **구현 방법** (*Implementation*) | 패턴을 실제 코드로 구현하는 방법 안내 |
| 8 | **시각적 설명** (*Illustrations*) | 다이어그램, UML 등 패턴의 시각적 표현 |
| 9 | **예제** (*Examples*) | 패턴의 최소 구현 코드 |
| 10 | **필수 연계** (*Co-requisites*) | 이 패턴이 작동하기 위해 함께 필요한 다른 패턴 |
| 11 | **관계성** (*Relations*) | 이 패턴과 유사하거나 관련된 다른 패턴 |
| 12 | **알려진 용도** (*Known Usage*) | 실제 프로젝트에서 사용된 사례 |
| 13 | **토론** (*Discussions*) | 패턴의 장단점, 트레이드오프, 커뮤니티 의견 |

### 패턴 문서 작성 예시: 옵저버 패턴

실제 패턴 문서가 어떤 모습인지, 옵저버 패턴을 예시로 간략히 작성해 보자.

```
이름: 옵저버 (Observer)

설명: 객체 간 일대다 의존 관계를 정의하여, 한 객체의 상태가 변경되면
      모든 의존 객체에 자동으로 통지하고 갱신하는 패턴

컨텍스트 개요: 여러 UI 컴포넌트가 동일한 데이터 소스에 의존하며,
              데이터 변경 시 모든 컴포넌트가 동기화되어야 하는 상황

문제 제시: 데이터 소스를 직접 참조하면 강한 결합이 발생하며,
          새로운 컴포넌트를 추가할 때마다 데이터 소스를 수정해야 한다

해결 방법: Subject(발행자)와 Observer(구독자) 인터페이스를 정의하고,
          Subject가 Observer 목록을 관리하여 상태 변경 시 일괄 통지한다

필수 연계: 없음 (독립적으로 사용 가능)

관계성: Mediator 패턴 (중앙 집중적 통신), Pub/Sub 패턴 (이벤트 채널 기반)

알려진 용도: DOM EventListener, React의 useState, RxJS Observable,
           Node.js EventEmitter
```

---

## 3. 패턴 카드: 패턴의 요약본

패턴 문서의 전체 내용을 빠르게 파악할 수 있도록 **패턴 카드** 형식으로 요약할 수 있다. 패턴 카드는 팀 내부 패턴 카탈로그나 빠른 참조용으로 유용하다.

### 패턴 카드 예시: 옵저버 패턴

| 항목 | 내용 |
|------|------|
| **이름** | 옵저버 (Observer) |
| **카테고리** | 행위 패턴 |
| **의도** | 객체 간 일대다 의존 관계를 정의하여 상태 변경을 자동 전파 |
| **적용 시기** | 한 객체의 변경이 다른 객체들에 반영되어야 할 때 |
| **구조** | Subject → Observer[] |
| **결과** | 느슨한 결합, 동적 구독 관리, 브로드캐스트 통신 |
| **관련 패턴** | Mediator, Pub/Sub, Event Emitter |

```typescript
// 패턴 카드에 포함될 최소 구현
interface Subject<T> {
  subscribe(observer: (data: T) => void): () => void;
  notify(data: T): void;
}

function createSubject<T>(): Subject<T> {
  const observers = new Set<(data: T) => void>();

  return {
    subscribe(observer) {
      observers.add(observer);
      return () => observers.delete(observer); // 구독 해제 함수 반환
    },
    notify(data) {
      observers.forEach(observer => observer(data));
    },
  };
}
```

---

## 4. 모범 패턴의 조건

모든 패턴 문서가 동일한 품질을 가지는 것은 아니다. 모범적인 패턴(*well-written pattern*)이 되려면 다음 조건을 충족해야 한다.

### 충분한 참고 자료

패턴은 단독으로 존재할 수 없다. 모범 패턴은 반드시 **충분한 참고 자료**와 **선행 연구**를 바탕으로 해야 한다.

- 해당 패턴이 처음 제안된 논문이나 서적
- 패턴이 사용된 실제 프로젝트의 사례
- 관련된 다른 패턴과의 비교 분석
- 커뮤니티에서의 토론과 피드백

### 필요성 근거

패턴이 존재해야 하는 **명확한 이유**가 있어야 한다. "이런 패턴이 있으면 좋겠다"가 아니라 "이 패턴 없이는 이 문제를 효과적으로 해결하기 어렵다"는 근거가 필요하다.

```typescript
// 필요성 근거의 예: 전략 패턴이 왜 필요한가?

// 패턴 없이 — 조건문이 계속 늘어남
function calculateDiscount(type: string, amount: number): number {
  if (type === "vip") return amount * 0.2;
  if (type === "member") return amount * 0.1;
  if (type === "student") return amount * 0.15;
  if (type === "senior") return amount * 0.12;
  // 새 할인 유형이 추가될 때마다 이 함수를 수정해야 한다
  // OCP(개방-폐쇄 원칙) 위반
  return 0;
}

// 전략 패턴 적용 — 새 전략 추가 시 기존 코드 수정 불필요
interface DiscountStrategy {
  calculate(amount: number): number;
}

class VipDiscount implements DiscountStrategy {
  calculate(amount: number): number {
    return amount * 0.2;
  }
}

class MemberDiscount implements DiscountStrategy {
  calculate(amount: number): number {
    return amount * 0.1;
  }
}

class StudentDiscount implements DiscountStrategy {
  calculate(amount: number): number {
    return amount * 0.15;
  }
}

function applyDiscount(strategy: DiscountStrategy, amount: number): number {
  return strategy.calculate(amount);
}
```

> **Osmani의 조언**: 패턴을 문서화할 때 가장 중요한 것은 **"왜"**에 답하는 것이다. 코드의 "어떻게"보다 "왜 이런 구조가 필요한지"를 명확히 설명하는 패턴이 가치 있는 패턴이다.

---

## 5. 패턴 작성 체크리스트

패턴을 작성하거나 기존 패턴을 평가할 때 사용할 수 있는 **다섯 가지 체크리스트**가 있다. 이 체크리스트는 자신의 프로토 패턴을 패턴으로 발전시킬 때도, 타인의 패턴을 평가할 때도 유용하다.

### 다섯 가지 평가 기준

| # | 기준 | 질문 | 설명 |
|---|------|------|------|
| 1 | **실용성** (*Practicality*) | 이론이 아닌 실무에서 적용 가능한가? | 학술적으로만 의미 있는 패턴은 실용적이지 않다 |
| 2 | **모범 사례** (*Best Practices*) | 업계의 모범 사례를 반영하는가? | 검증되지 않은 실험적 방법이 아닌 업계 표준에 기반해야 한다 |
| 3 | **사용자에 대한 솔직함** (*Transparency*) | 패턴의 한계와 트레이드오프를 솔직히 기술하는가? | 장점만 나열하고 단점을 숨기는 패턴 문서는 신뢰할 수 없다 |
| 4 | **독창성 불필요** (*Originality Not Required*) | 기존 패턴의 검증된 발전인가? | 완전히 새로운 것을 만들 필요는 없다. 기존 패턴의 개선도 가치 있다 |
| 5 | **훌륭한 예시** (*Strong Examples*) | 패턴의 효과를 증명하는 좋은 예시가 있는가? | 추상적 설명만으로는 부족하며 구체적인 코드 예시가 필수적이다 |

네 번째 기준 "독창성 불필요"는 특히 주목할 만하다. 이미 검증된 패턴을 현대적 맥락(TypeScript, React 등)에 맞게 재해석하는 것도 충분히 가치 있는 작업이다. 완전히 새로운 패턴을 만들어야 한다는 부담을 가질 필요가 없다.

### 체크리스트 적용 예시

새로운 패턴을 발견했다고 가정하고, 체크리스트를 적용해 보자.

```typescript
// 후보 패턴: "타입 가드 팩토리 패턴"
// — 런타임 타입 검사 함수를 자동 생성하는 패턴

// 1. 실용성 ✅ — API 응답 검증에서 실제로 필요
function createTypeGuard<T>(
  schema: Record<keyof T, string>
): (value: unknown) => value is T {
  return (value: unknown): value is T => {
    if (typeof value !== "object" || value === null) return false;
    return Object.entries(schema).every(
      ([key, type]) => typeof (value as Record<string, unknown>)[key] === type
    );
  };
}

interface User {
  name: string;
  age: number;
}

const isUser = createTypeGuard<User>({ name: "string", age: "number" });

// 2. 모범 사례 ⚠️ — Zod, io-ts 같은 라이브러리가 이미 이 문제를 해결
// 3. 사용자에 대한 솔직함 ✅ — 중첩 객체 검증 불가 등 한계 기술 가능
// 4. 독창성 불필요 ✅ — Validation 패턴의 TypeScript 맥락 적용
// 5. 훌륭한 예시 ✅ — API 응답 검증 예시가 명확

// 결론: 기준 2를 충족하지 못하므로 독립 패턴보다는
//       기존 패턴(Validation 패턴)의 TypeScript 변형으로 문서화하는 것이 적절하다
```

---

## 6. 노출 모듈 패턴: 패턴 진화의 사례

크리스티안 하일만(*Christian Heilmann*)은 기존의 모듈 패턴을 개선하여 **노출 모듈 패턴**(*Revealing Module Pattern*)을 만들었다. 이 사례는 기존 패턴의 구체적 문제를 파악하고 이를 개선하여 새로운 패턴을 탄생시키는 과정을 잘 보여준다.

### 기존 모듈 패턴의 문제

```typescript
// 기존 모듈 패턴 — 공개 멤버와 비공개 멤버의 문법이 다르다
const counterModule = (() => {
  let count = 0; // private

  return {
    increment() {    // public — 객체 리터럴 내부에 직접 정의
      count++;
    },
    getCount() {     // public
      return count;
    },
  };
})();

// 문제점:
// 1. 공개 함수는 return {} 안에, 비공개 함수는 바깥에 정의해야 함
// 2. 나중에 공개/비공개를 변경하려면 코드 이동이 필요
// 3. 공개 멤버에서 다른 공개 멤버를 참조하려면 this를 사용해야 함
```

### 노출 모듈 패턴의 개선

```typescript
// 노출 모듈 패턴 — 모든 함수를 동일한 방식으로 정의하고, 마지막에 공개할 것만 선택
const counterModule = (() => {
  let count = 0;

  function increment(): void {     // 비공개와 동일한 문법
    count++;
  }

  function decrement(): void {     // 비공개
    count--;
  }

  function getCount(): number {    // 비공개와 동일한 문법
    return count;
  }

  function reset(): void {         // 비공개
    count = 0;
  }

  // 공개할 API만 선택하여 반환
  return {
    increment,
    getCount,
  };
})();

// 장점:
// 1. 모든 함수가 동일한 문법으로 정의됨 → 일관성
// 2. 공개/비공개 전환이 return 문에서 추가/제거만 하면 됨 → 유연성
// 3. 반환 객체가 모듈의 공개 API를 명확히 보여줌 → 가독성
```

이 사례가 보여주는 것은 **패턴 작성에 독창성이 필수가 아니라는 점**이다. 기존 모듈 패턴의 핵심 의도(캡슐화)는 유지하면서 구현 방식만 개선한 것이 노출 모듈 패턴이다. 이것이 바로 체크리스트의 4번 항목 "독창성 불필요"의 좋은 예시다.

### 전통 vs 현대

| 노출 모듈 패턴 (전통) | ES Modules (현대) |
|------------------------|---------------------|
| 즉시 실행 함수(IIFE)로 스코프 생성 | `import`/`export` 문법으로 모듈 경계 설정 |
| `return` 문으로 공개 API 결정 | `export` 키워드로 공개 멤버 결정 |
| 런타임에 한 번만 실행 | 정적 분석 가능, 트리 셰이킹 지원 |

```typescript
// 현대 ES Module — 노출 모듈 패턴의 정신을 계승
let count = 0;                    // 모듈 스코프 (비공개)

function increment(): void {      // 아직 비공개
  count++;
}

function decrement(): void {      // 비공개로 유지
  count--;
}

function getCount(): number {     // 아직 비공개
  return count;
}

export { increment, getCount };   // 공개할 것만 export
```

> **핵심 통찰**: 노출 모듈 패턴은 패턴 진화의 모범 사례다. 기존 패턴의 **구체적인 문제점**을 파악하고, **핵심 의도는 유지하면서** 구현 방식을 개선했다. 현대의 ES Modules도 같은 정신을 계승하고 있으며, 이는 좋은 패턴이 시대에 맞게 발전할 수 있음을 보여준다.

---

## 7. 패턴 문서화의 현대적 도구와 방법

2026년 현재, 패턴 문서화는 더 이상 책이나 논문에 국한되지 않는다.

| 도구/플랫폼 | 용도 |
|-------------|------|
| **Storybook** | 컴포넌트 패턴의 시각적 문서화 및 인터랙티브 예시 |
| **TypeDoc** | TypeScript 인터페이스를 통한 패턴 구조 자동 문서화 |
| **ADR** (*Architecture Decision Records — 아키텍처 결정 기록*) | 아키텍처 패턴 선택의 근거를 기록하는 문서 형식 |
| **GitHub Discussions** | 오픈 소스 프로젝트에서의 패턴 토론과 피드백 |
| **RFC 문서** | React, Next.js 등 주요 프레임워크의 패턴 제안 형식 |

### TypeScript가 패턴 문서화에 미친 영향

TypeScript의 타입 시스템은 패턴의 **구조**와 **계약**을 코드 자체로 표현할 수 있게 했다. 이는 패턴 문서의 "설계 내용"과 "구현 방법" 항목을 더 정밀하게 만들었다.

```typescript
// TypeScript 인터페이스가 곧 패턴의 "설계 문서" 역할을 한다
interface PatternDocument<TContext, TProblem, TSolution> {
  name: string;
  context: TContext;
  problem: TProblem;
  solution: TSolution;
  consequences: {
    benefits: string[];
    liabilities: string[];
  };
}

// 타입 매개변수를 통해 패턴이 적용되는 구체적 상황을 명시할 수 있다
type ObserverPatternDoc = PatternDocument<
  { dataSource: "api" | "websocket" | "database" },
  "다수의 컴포넌트가 동일 데이터 소스에 의존",
  "Subject-Observer 인터페이스로 느슨한 결합 구현"
>;
```

### 팀 내 패턴 카탈로그 구축

실무에서는 팀 내부에 사용하는 패턴 카탈로그를 구축하면 신입 개발자의 온보딩과 코드 리뷰에 큰 도움이 된다.

```typescript
// 팀 내부 패턴 카탈로그를 관리하는 구조 예시
interface TeamPattern {
  name: string;
  category: "creational" | "structural" | "behavioral" | "architectural";
  problem: string;
  solution: string;
  codeExample: string;
  usedIn: string[];           // 이 패턴을 사용 중인 프로젝트
  alternatives: string[];     // 대안 패턴
  addedBy: string;
  addedDate: string;
  lastReviewDate: string;
}

// 팀 패턴 카탈로그는 정기적으로 리뷰하고 업데이트해야 한다
// - 더 이상 사용되지 않는 패턴은 deprecated 표시
// - 새로운 기술 스택에 맞게 예제 코드 갱신
// - 안티패턴으로 판명된 항목은 Ch04의 안티패턴 목록으로 이동
```

> **Osmani의 조언**: 패턴 문서의 완성도에 집착하지 마라. 13가지 구성 요소를 모두 완벽히 채울 필요는 없다. 최소한 **이름, 문제 제시, 해결 방법, 예제, 알려진 용도** 다섯 가지만 있어도 실용적인 패턴 문서가 된다. 나머지는 시간이 지나면서 채워 나가면 된다.

---

## 요약

- 디자인 패턴은 **컨텍스트**(상황), **집중 목표**(상충하는 힘), **구성**(해결 방법)의 세 가지 핵심 요소로 이루어진다
- 완전한 패턴 문서는 **13가지 구성 요소**를 포함하며, 그 중 이름, 설명, 컨텍스트 개요, 문제 제시, 해결 방법이 **핵심 5가지**다
- 모범 패턴의 조건은 **충분한 참고 자료**와 **명확한 필요성 근거**다
- 패턴 작성 체크리스트: **실용성, 모범 사례, 사용자에 대한 솔직함, 독창성 불필요, 훌륭한 예시** 다섯 가지를 평가한다
- 크리스티안 하일만의 **노출 모듈 패턴**은 기존 모듈 패턴을 개선한 패턴 진화의 좋은 사례이며, ES Modules로 그 정신이 계승되었다
- 현대에는 TypeScript 타입 시스템, Storybook, ADR, RFC 등이 패턴 문서화의 새로운 도구로 활용된다

---

## 다른 챕터와의 관계

- **← Ch01 (디자인 패턴 소개)**: Ch01에서 패턴의 정의와 역사를 다루었다면, 이 챕터는 패턴을 **어떻게 체계적으로 기록하는지** 다룬다
- **← Ch02 (프로토 패턴)**: Ch02에서 패턴이 되기 위한 조건을 다루었다면, 이 챕터는 조건을 충족한 패턴을 **어떤 구조로 문서화하는지** 다룬다
- **→ Ch04 (안티패턴)**: 패턴 구조를 이해하면 안티패턴이 왜 "패턴처럼 보이지만 패턴이 아닌지"를 더 명확히 구분할 수 있다
- **→ Ch06 (패턴 카테고리)**: 이 챕터에서 배운 구조화 방법으로 Ch06의 생성/구조/행위 분류 체계를 이해할 수 있다
- **→ Ch07 (디자인 패턴)**: 각 패턴의 문서가 이 챕터에서 다룬 13가지 구성 요소를 따르고 있음을 확인할 수 있다