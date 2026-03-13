# Chapter 02: "Pattern"-ity Testing, Proto-Patterns, and the Rule of Three (패턴성 검증, 프로토 패턴, 그리고 세 가지 법칙)

## 핵심 질문

> 어떤 아이디어가 "디자인 패턴"이라 불릴 자격을 얻으려면 어떤 검증 과정을 거쳐야 하며, 프로토 패턴은 어떻게 성숙한 패턴으로 발전하는가?

---

## 1. 프로토 패턴이란

모든 디자인 패턴은 처음부터 완성된 형태로 태어나지 않는다. 누군가가 반복되는 문제에 대한 해결책을 발견하고 이를 문서화하더라도, 그것이 곧바로 "패턴"으로 인정되는 것은 아니다. 이처럼 **아직 충분한 검증을 거치지 않은 미숙한 패턴**을 프로토 패턴(*Proto-Pattern — 커뮤니티의 완전한 검증을 통과하지 못한 패턴 후보*)이라고 한다.

프로토 패턴은 다음과 같은 상태에 있는 해결책이다:

- 특정 개발자나 소수의 팀에서만 사용된 경험이 있다
- 커뮤니티 전반에서 폭넓게 검증되지 않았다
- 아직 정형화된 패턴 문서 형식을 갖추지 못했다

프로토 패턴은 미래의 패턴이 될 **씨앗**과 같다. 모든 프로토 패턴이 패턴이 되는 것은 아니지만, 모든 패턴은 한때 프로토 패턴이었다.

> **핵심 통찰**: 프로토 패턴은 "아직 패턴이 아닌 것"이 아니라 "패턴이 되어가는 과정에 있는 것"이다. 새로운 해결책을 발견했다면 그것을 프로토 패턴으로 인식하고, 검증 과정을 통해 성숙시키는 자세가 필요하다.

---

## 2. 패턴성 검증: 좋은 패턴의 특징

어떤 해결책이 진정한 디자인 패턴으로 인정받으려면 **패턴성 검증**(*"Pattern"-ity Testing — 해결책이 패턴으로서의 자격을 갖추었는지 체계적으로 평가하는 과정*)이라는 과정을 거쳐야 한다. 이 검증은 해결책이 다음 특징들을 갖추고 있는지 확인하는 과정이다.

### 좋은 패턴이 갖추어야 할 특징

| 특징 | 설명 |
|------|------|
| **특정 문제를 해결한다** | 단순히 원칙이나 전략을 포착하는 것이 아니라, 반복적으로 발생하는 **구체적인 문제**에 대한 해결책을 제공해야 한다 |
| **명쾌한 해결책이 존재하지 않는다** | 패턴이 해결하는 문제는 간단한 원칙만으로는 풀 수 없는, 일정 수준의 **간접성**(*indirection*)이 필요한 문제여야 한다 |
| **확실한 기능을 설명한다** | 해결책은 기능과 구조를 명확히 설명해야 하며, 그 설명만으로 패턴을 구현할 수 있어야 한다 |
| **관계를 설명한다** | 시스템의 구조와 메커니즘뿐 아니라, 더 깊은 수준의 **모듈 간 관계**를 기술해야 한다 |

크리스토퍼 알렉산더(*Christopher Alexander*)는 패턴이 **과정(process)**이면서 동시에 **결과물(thing)**이라고 말했다. 패턴은 단순히 정적인 해결책이 아니라, 문제를 해결해나가는 과정 그 자체이기도 하다. 패턴을 읽는 사람은 해결책의 최종 형태뿐 아니라 그 해결책에 이르는 사고 과정까지 이해할 수 있어야 한다.

### 패턴성 검증의 예시

좋은 패턴이 되기 위한 특징을 TypeScript 코드로 살펴보자.

```typescript
// 나쁜 예: "모든 변수에 타입을 붙여라" — 이것은 원칙이지 패턴이 아니다
const name: string = "hello";
const count: number = 42;

// 좋은 예: 옵저버 패턴 — 구체적 문제(상태 변경 통지)를 해결하는 패턴
interface Observer<T> {
  update(data: T): void;
}

class EventEmitter<T> {
  private observers: Observer<T>[] = [];

  subscribe(observer: Observer<T>): void {
    this.observers.push(observer);
  }

  notify(data: T): void {
    this.observers.forEach(observer => observer.update(data));
  }
}
```

위 예시에서 "타입을 붙여라"는 좋은 습관이지만 패턴이 아니다. 반면 옵저버 패턴은 **"한 객체의 상태 변화를 여러 의존 객체에 통지해야 하는 문제"**라는 구체적인 문제를 해결하므로 패턴이 될 수 있다.

> **Osmani의 조언**: 패턴은 단순한 코딩 습관이나 원칙이 아니다. 패턴은 반드시 **구체적인 문제**를 해결해야 하며, 그 해결 과정에서 일정 수준의 복잡성(간접성)이 수반된다. 만약 해결책이 너무 단순하다면, 그것은 패턴이 아니라 모범 사례(*best practice*)에 가깝다.

---

## 3. 패턴렛: 패턴의 씨앗

패턴렛(*Patternlet — 완전한 검증 없이 간략한 설명과 코드 조각으로 공유되는 패턴 후보*)이란 패턴에 대한 **간단한 설명을 덧붙여 공개하는 코드 조각**이다. 패턴이 되기 전, 아이디어를 빠르게 공유하고 커뮤니티의 피드백을 받기 위한 형식이다.

패턴렛은 다음과 같은 구조를 가진다:

- **이름**: 패턴의 간결한 이름
- **간략한 설명**: 어떤 문제를 어떻게 해결하는지 1~2문장으로 설명
- **코드 조각**: 핵심 아이디어를 보여주는 최소한의 코드

### 패턴렛 예시

```
이름: 지연 초기화 프록시
설명: 비용이 큰 객체의 생성을 실제로 사용하는 시점까지 미루어 초기 로딩 성능을 개선한다.
```

```typescript
class HeavyResource {
  constructor() {
    console.log("비용이 큰 초기화 수행...");
    // 대량의 데이터 로딩, DB 연결 등
  }

  process(): string {
    return "처리 완료";
  }
}

class LazyProxy {
  private instance: HeavyResource | null = null;

  process(): string {
    if (!this.instance) {
      this.instance = new HeavyResource();
    }
    return this.instance.process();
  }
}

// HeavyResource는 process()를 호출하는 시점에 비로소 생성된다
const proxy = new LazyProxy();
// ... 다른 작업 수행 ...
proxy.process(); // 이 시점에서 HeavyResource 생성
```

패턴렛은 완전한 패턴 문서가 아니므로, 컨텍스트나 적용 사례, 장단점 분석 등이 빠져 있다. 하지만 아이디어를 빠르게 전파하고 검증을 시작하는 출발점으로서 중요한 역할을 한다.

---

## 4. 세 가지 법칙 (Rule of Three)

프로토 패턴이 패턴으로 승격되기 위한 가장 중요한 기준 중 하나가 **세 가지 법칙**(*Rule of Three*)이다. 이 법칙에 따르면 패턴은 다음 세 가지 핵심 영역에서 검증되어야 한다.

### 세 가지 법칙의 구성

| 법칙 | 설명 | 검증 질문 |
|------|------|-----------|
| **목적 적합성** (*Fitness of Purpose*) | 패턴이 유용하다고 간주되는가 | "이 패턴은 실제 문제를 해결하는가?" |
| **유용성** (*Fitness of Use*) | 패턴이 성공적으로 사용된 사례가 있는가 | "이 패턴은 성공적으로 적용된 실제 사례가 있는가?" |
| **적용 가능성** (*Fitness of Applicability*) | 패턴이 다양한 상황에 적용 가능한가 | "이 패턴을 다른 프로젝트, 다른 팀에서도 쓸 수 있는가?" |

### 세 가지 법칙의 핵심: 반복 사용

세 가지 법칙의 근본 정신은 **반복**에 있다. 해결책이 한 번의 성공으로 패턴이 되는 것이 아니라, **서로 다른 상황에서 반복적으로 성공**해야만 패턴으로 인정받을 수 있다.

```typescript
// 예: "커스텀 훅으로 데이터 페칭을 추상화하라"가 패턴이 되려면...

// 1. 목적 적합성 — 실제 문제를 해결하는가?
// 컴포넌트마다 반복되는 loading/error/data 상태 관리를 줄여준다
function useFetch<T>(url: string) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    fetch(url)
      .then(res => res.json())
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false));
  }, [url]);

  return { data, loading, error };
}

// 2. 유용성 — 실제 사용 사례가 있는가?
// SWR, React Query(TanStack Query), useSWR 등 수많은 라이브러리가 이 패턴을 따른다

// 3. 적용 가능성 — 다양한 상황에 적용 가능한가?
// REST API, GraphQL, WebSocket 등 어떤 데이터 소스에도 적용 가능하다
```

> **핵심 통찰**: "세 가지 법칙"은 패턴의 품질을 보증하는 최소한의 기준이다. 아무리 우아한 해결책이라도 한두 번의 성공으로는 부족하며, **다양한 컨텍스트에서 반복적으로 효과가 입증**되어야 비로소 패턴이라 부를 수 있다.

---

## 5. 프로토 패턴에서 패턴으로의 성숙 과정

프로토 패턴이 완전한 패턴으로 성장하는 과정을 단계별로 정리하면 다음과 같다.

```
[아이디어] → [패턴렛] → [프로토 패턴] → [패턴성 검증] → [패턴]
    ↓            ↓            ↓              ↓            ↓
  문제 발견    간략한       문서화된       세 가지 법칙   커뮤니티에서
              코드 공유    해결책         통과          인정된 패턴
```

### 각 단계에서 필요한 것

| 단계 | 필요 요소 | 예시 |
|------|-----------|------|
| **아이디어** | 반복되는 문제 인식 | "컴포넌트마다 같은 로딩 처리를 반복하고 있다" |
| **패턴렛** | 이름 + 간략 설명 + 코드 조각 | "커스텀 훅 패턴: 데이터 페칭 로직을 훅으로 추출" |
| **프로토 패턴** | 문서화된 해결책 | 문제 정의, 해결 방법, 코드 예시, 장단점 |
| **패턴성 검증** | 세 가지 법칙 충족 | 여러 프로젝트에서 성공적 사용, 커뮤니티 피드백 |
| **패턴** | 정형화된 문서 | GoF 형식 또는 알렉산더 형식의 완전한 패턴 문서 |

---

## 6. 패턴을 만드는 것과 패턴을 인정하는 것의 차이

패턴 커뮤니티에서 중요한 구분이 있다. 패턴은 **발명**(*invent*)하는 것이 아니라 **발견**(*discover*)하는 것이다.

소프트웨어 개발 과정에서 반복적으로 나타나는 문제와 해결책을 **인식하고 문서화**하는 것이 패턴 작성자의 역할이다. 누군가 완전히 새로운 해결책을 고안했더라도, 그것이 단 한 번만 사용되었다면 아직 패턴이라 부를 수 없다.

```typescript
// 흔한 실수: "내가 만든 이 구조가 패턴이다!"
// → 한 프로젝트에서만 사용되었다면 프로토 패턴일 뿐이다

// 올바른 인식: "이 구조가 여러 프로젝트에서 반복적으로 나타나는군!"
// → 세 가지 법칙을 통과한다면 패턴으로 인정될 수 있다
```

> **Osmani의 조언**: 자신의 코드에서 반복적으로 사용하는 구조를 발견했다면, 그것을 프로토 패턴으로 문서화하고 커뮤니티에 공유하라. 하지만 그것을 즉시 "패턴"이라고 부르지는 마라. 커뮤니티의 검증을 거쳐야만 비로소 패턴이라는 이름을 얻을 수 있다.

---

## 7. 현대 JS/TS 생태계에서의 패턴성 판별

프론트엔드 생태계에서는 매년 새로운 라이브러리, 프레임워크, 코딩 관례가 등장한다. 이 중 어떤 것이 진정한 "패턴"이고, 어떤 것이 단순한 라이브러리 관례 또는 유행인지 구분하는 것은 중요하다.

### 패턴 vs 라이브러리 관례 vs 유행

| 분류 | 특징 | 예시 |
|------|------|------|
| **패턴** | 프레임워크에 독립적, 다양한 맥락에서 검증됨 | Observer, Module, Provider, Strategy |
| **라이브러리 관례** | 특정 라이브러리의 권장 사용법, 범용성 제한적 | React의 `useReducer` 관례, Next.js의 파일 기반 라우팅 |
| **유행** | 검증 부족, 특정 시기에 인기를 끌다 사라짐 | Higher-Order Component 남용 (React Hooks 등장 전) |

### 패턴성 판별 체크리스트

새로운 코딩 관례를 접했을 때 다음 질문으로 패턴 여부를 판별할 수 있다.

```typescript
// 패턴성 판별을 위한 사고 모델
interface PatternCandidate {
  name: string;
  solvedProblem: string;          // 1. 구체적인 문제를 해결하는가?
  isNonObvious: boolean;          // 2. 해결책이 자명하지 않은가?
  independentContexts: number;    // 3. 몇 가지 독립적 맥락에서 검증되었는가?
  frameworkIndependent: boolean;  // 4. 특정 프레임워크 없이도 설명 가능한가?
  describedRelationships: boolean;// 5. 구성 요소 간의 관계를 기술하는가?
}

function isLikelyPattern(candidate: PatternCandidate): boolean {
  return (
    candidate.solvedProblem !== "" &&
    candidate.isNonObvious &&
    candidate.independentContexts >= 3 &&
    candidate.frameworkIndependent &&
    candidate.describedRelationships
  );
}
```

### 실전 판별 예시

**예시 1: 커스텀 훅 — 패턴인가, 라이브러리 관례인가?**

```typescript
// useFetch: 데이터 페칭 로직의 재사용
function useFetch<T>(url: string): {
  data: T | null;
  loading: boolean;
  error: Error | null;
} {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    fetch(url)
      .then((res) => res.json())
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false));
  }, [url]);

  return { data, loading, error };
}
```

커스텀 훅 **자체**는 React의 라이브러리 관례이다. 그러나 "로직의 재사용을 위해 상태를 캡슐화한다"는 더 넓은 원칙은 범용 **패턴**(Module 패턴, Strategy 패턴)에 해당한다. 이처럼 라이브러리 관례 안에 범용 패턴이 내재되어 있는 경우가 많다.

**예시 2: 컴포지션 패턴 — 프레임워크 독립적인 검증된 패턴**

```tsx
// 나쁜 예: 모든 것을 prop으로 전달
function Card({ title, subtitle, image, actions, footer }: CardProps) {
  return (
    <div>
      <img src={image} />
      <h2>{title}</h2>
      <p>{subtitle}</p>
      <div>{actions}</div>
      <footer>{footer}</footer>
    </div>
  );
}

// 좋은 예: 컴포지션으로 유연하게 구성
function Card({ children }: { children: React.ReactNode }) {
  return <div className="card">{children}</div>;
}

Card.Header = ({ children }: { children: React.ReactNode }) => (
  <div className="card-header">{children}</div>
);

Card.Body = ({ children }: { children: React.ReactNode }) => (
  <div className="card-body">{children}</div>
);

// 사용
<Card>
  <Card.Header>제목</Card.Header>
  <Card.Body>내용</Card.Body>
</Card>
```

컴포지션 패턴은 React뿐 아니라 Vue, Svelte, 심지어 백엔드 시스템에서도 적용되는 범용 패턴이다. 세 가지 법칙을 모두 통과한다.

**예시 3: Server Actions — 아직 프로토 패턴 단계**

```typescript
// Next.js의 Server Actions (2024~)
"use server";

async function submitForm(formData: FormData): Promise<void> {
  const name = formData.get("name") as string;
  await db.users.create({ name });
}

// 판별:
// - 목적 적합성: ✅ 서버-클라이언트 간 데이터 전송 문제를 해결
// - 유용성: ✅ Next.js 생태계에서 활발히 사용 중
// - 적용 가능성: ⚠️ Next.js/React 19에 종속적, 범용 패턴으로 보기 어려움
// → 아직 프로토 패턴 단계. 다른 프레임워크에서도 채택되면 패턴으로 성숙할 가능성 있음
```

> **Osmani의 조언**: 새로운 라이브러리나 프레임워크의 관례를 접했을 때, 그것이 해당 도구에만 국한되는 것인지 아니면 더 넓은 원칙을 반영하는 것인지 구분하라. 후자라면 패턴으로서의 가치를 가진다.

---

## 요약

- **프로토 패턴**은 아직 커뮤니티의 충분한 검증을 거치지 않은 미숙한 패턴이다
- 좋은 패턴은 **구체적 문제 해결**, **간접성**, **명확한 기능 설명**, **관계 기술**이라는 네 가지 특징을 갖추어야 한다
- 크리스토퍼 알렉산더는 패턴이 **과정(process)**이면서 동시에 **결과물(thing)**이라고 정의했다
- **패턴렛**은 패턴의 씨앗으로, 간략한 설명과 코드 조각으로 구성된 공유 형식이다
- **세 가지 법칙**(목적 적합성, 유용성, 적용 가능성)을 모두 통과해야만 패턴으로 인정받을 수 있다
- 패턴은 발명하는 것이 아니라 **반복되는 문제에서 발견**하는 것이다
- 현대 JS/TS 생태계에서는 **패턴**, **라이브러리 관례**, **유행**을 구분하는 안목이 필요하며, 프레임워크 독립성이 핵심 판별 기준이다

---

## 다른 챕터와의 관계

- **← Ch01 (디자인 패턴 소개)**: Ch01에서 "패턴이란 무엇인가"를 정의했다면, 이 챕터는 "무엇이 패턴이 될 수 있는가"를 검증하는 기준을 제시한다
- **→ Ch03 (패턴 구조화)**: 프로토 패턴이 패턴으로 승격되면 Ch03에서 다루는 정형화된 구조로 문서화해야 한다
- **→ Ch04 (안티패턴)**: 패턴성 검증을 통과하지 못한 해결책이 널리 퍼지면 안티패턴이 될 수 있다
- **→ Ch07 (디자인 패턴)**: 이 챕터에서 배운 검증 기준으로 Ch07의 GoF 패턴들이 왜 "패턴"으로 인정받았는지 이해할 수 있다