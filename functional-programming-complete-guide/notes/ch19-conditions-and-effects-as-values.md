# Chapter 19: Conditions and Effects as Values (조건과 효과를 값으로)

## 핵심 질문

부수효과와 조건 분기까지 값으로 다룬다면 코드는 어떻게 달라지는가? Result 타입·패턴 매칭·Effect는 각각 무엇을 값으로 만들며, 실무에서 함수형 라이브러리(fp-ts vs fxts)는 어떤 기준으로 고르는가?

---

이 가이드의 마지막 장이다. 지금까지 함수를 값으로(1장), 코드를 리스트로(11장), 비동기를 값으로(12장), 실패를 값으로(13장) 다뤄 왔다. 이 장은 그 사고를 끝까지 밀어붙인다 — **효과(effect)와 조건(condition) 자체를 값으로** 다루는 최신 흐름(Result 타입, TC39 패턴 매칭, Effect-TS)을 살펴보고, 실무 라이브러리 선택 논의로 마무리한다.

---

## 1. 함수 합성 vs 함수 조합의 합성

먼저 용어 하나를 정리하자. 다음 둘은 모두 "합성"처럼 보이지만 성격이 다르다.

**함수 합성:**

```typescript
const f = (x: number) => x + 1
const g = (x: number) => x * 2
const h = (x: number) => f(g(x)) // 2를 곱한 뒤 1 더하기
```

**함수 적용의 합성:**

```typescript
const h = async (f, g) => {
	await f();
	await g();
}
```

여러 함수를 **값의 흐름**으로 연결해서 하나의 함수로 만드는 것이 함수 합성이다. 값을 변형하는 함수 합성과 달리, 작업을 순서대로 실행하는 것은 **함수 적용의 합성**이다. 이 구분은 함수형 프로그래밍에서 중요하다 — 전자는 3장의 pipe와 13장의 모나드가 다루는 영역이고, 후자는 15장의 async/await(문장의 흐름)가 다루는 영역이다.

## 2. 값으로 다루는 부수효과 — Result 타입

부수효과가 있는 코드는 보통 이렇게 생겼다.

```typescript
const result = await apiCall()
if (result.ok) {
  alert('성공')
}
```

함수형 프로그래밍에서는 순수 함수와 순수 효과를 구분하고, 이런 효과도 값으로 다루려고 한다.

```typescript
type Result<T, E> = { type: 'ok'; value: T } | { type: 'err'; error: E }

const handlePayment = async (): Promise<Result<SuccessData, ErrorInfo>> => {
  try {
    const res = await api()
    return { type: 'ok', value: res }
  } catch (err) {
    return { type: 'err', error: err }
  }
}
```

이 코드는 `try/catch` 없이 로직을 안전하게 처리할 수 있고, 그 **결과값(Result)을 기준으로 분기한 후 실제 효과만 따로 실행한다.** 판별 유니언(discriminated union)이므로 `type`을 좁히면 타입스크립트가 `value`/`error` 접근을 안전하게 검증해 준다.

> **핵심 통찰**: Result 타입은 하스켈 `Either`(11장)의 타입스크립트 일상 코드 판이며, `Promise.reject`로 실패를 값으로 만들던 Kleisli 합성(13장)의 동기·명시적 버전이다. 같은 아이디어 — **실패는 던지는 것이 아니라 반환하는 것** — 가 세 번째 옷을 입고 나타난 것이다.

## 3. 조건을 값으로 다룬다면 — 패턴 매칭

패턴 매칭이 언어 레벨에서 지원되는 (모던한) 언어에서는 `if/else` 같은 제어문보다 **조건 자체를 값처럼** 다루는 방식이 흔하다. 자바스크립트에서도 현재 TC39의 Stage 1까지 올라와 논의 중이다.

기존 자바스크립트 조건문의 단점은 이렇다.

- **`switch`** 문은 오직 값의 동등성(`===`)만 비교할 수 있고, fallthrough(의도치 않은 다음 case 실행), 스코프 불명확, 표현식으로 사용 불가 등 많은 한계가 있다.
- **`if/else`**는 강력하지만, 중첩 구조나 값 추출이 필요한 경우 매우 장황하고 반복적이다.
- **구조 분해**는 값 추출은 가능하지만, 조건 분기와 결합이 어렵다.

패턴 매칭은 함수형 언어에서 널리 쓰이는 선언적 분기 방식으로, 값 중심·불변 데이터·구조 분해 등 함수형 패러다임에 매우 적합하다. 복잡한 데이터 구조를 간결하게 처리할 수 있다.

### 3.1 filter와 if문

**filter**는 컬렉션에서 "조건을 만족하는 값만 골라내는 함수형 고차 함수"다. 내부적으로는 각 요소마다 if문으로 조건을 검사하지만, 코드 흐름이 아니라 **'값'을 만드는 데** 집중한다. **if문**은 "조건에 따라 코드 흐름을 바꾼다"는 명령형 제어문이다 — 값이 아니라 "어떤 블록을 실행할지"를 결정하며, 단일 값이나 흐름 제어에 적합하다. (2장의 "if를 predicate로", 7장의 "if 없는 filter"가 이 구분의 실습이었다.)

### 3.2 패턴 매칭이 더하는 것

- 단순 비교뿐 아니라 구조체/객체/튜플/enum 등 복잡한 데이터 구조를 한 번에 분해하고,
- 여러 패턴을 한 번에 선언적으로 나열할 수 있다.
- if문은 boolean 조건 하나만 검사할 수 있지만, **패턴 매칭은 구조·타입·값·여러 조건을 동시에 검사하고 분해**할 수 있다.

11장에서 본 하스켈의 `safeDiv _ 0 = Left ...`가 정확히 이것이다 — 함수 오버로드·if문·타입 가드·구조 분해의 역할을 패턴 하나가 해결했다. 18장의 상태 패턴(`FilterState`의 predicate 캡슐화)은 같은 문제의 객체지향적 답이라는 점에서 대비해 볼 만하다.

## 4. 번외 — Effect-TS

효과를 값으로 다루는 아이디어를 라이브러리 차원에서 끝까지 밀어붙인 것이 Effect-TS다.

- **Promise**: 비동기 연산의 결과(성공/실패)를 값으로 캡슐화한다.
- **패턴 매칭**: 조건 분기와 값 추출을 선언적으로, 값 자체처럼 다룬다.
- **Effect**:
	- 네트워크 요청, 파일 IO, 실패, 성공, 의존성 주입 등 "실행의 효과"를 값(Effect 객체)으로 표현한다.
	- Effect 객체는 **실행 전까지 아무 일도 일어나지 않으며**, 여러 Effect를 조합하고, 변환하고, 조건에 따라 분기하는 등 모든 효과를 값처럼 조립할 수 있다.

"실행 전까지 아무 일도 일어나지 않는다"는 성질에 주목하자 — 14장에서 Promise의 즉시 실행 문제를 `() => Promise`로 풀었던 바로 그 지연성이, Effect에서는 타입이 있는 일급 개념으로 승격되어 있다. 하스켈의 `IO` 타입(11장)이 타입스크립트 생태계에 이식된 형태라고 볼 수 있다.

## 5. 실무 라이브러리 선택 — fp-ts vs fxts

원 노트에 남아 있던 커뮤니티 Q&A다. 현업에서 fp-ts와 fxts 중 도입을 고민하는 질문에 대한 답변들로, 이 가이드가 다뤄온 두 갈래(추상화 중심 vs 이터러블 중심)의 실무 버전이다.

먼저 유인동 님이 lodash·ramda 대비 fxjs의 장점으로 정리했던 내용(fxts에도 해당):

1. 대부분의 라이브러리들이 Promise를 잘 지원하지 못한다.
2. Promise를 잘 지원하지 못하면 async/await와 함께 사용하지 못한다.
3. async/await를 사용하지 못하면 비동기 에러 핸들링이 어려워진다.
4. fxjs는 ES6 표준 이터러블 프로토콜을 따르고 있어 이터러블/이터레이터/제너레이터와 잘 조합된다.
5. fxjs는 Promise를 잘 지원한다.
6. fxjs는 지연 평가와 Promise가 함께 잘 동작한다.
7. fxjs는 async/await와 함께 사용할 수 있으며, 비동기 에러 핸들링이 쉽다.
8. fxjs는 병렬적 동시 평가를 다루는 많은 함수들이 있다(C.takeAll, C.takeRace, C.race, C.map 등).
9. fxjs는 함수 하나하나가 간결하고 이해하기 쉽게 잘 작성되어 있다.
10. fxjs는 tree shaking을 잘 지원한다.
11. fxjs는 이전/최신 브라우저, CommonJS, ESM 등의 환경을 모두 잘 지원한다.
12. fxjs는 슬랙 채널을 운영하고 있다.
13. 다른 라이브러리에서 아래 코드가 동작하는지 테스트해 보라 — 대부분 1번 상황에서 이상한 값이 나오고, 2번 상황에서는 에러 핸들링이 안 되고 에러가 터질 것이다.

```typescript
// 1
async function f1() {
  const res = await go(
    [1, 2, 3, 4, 5],
    L.map(a => new Promise(resolve => resolve(a * a))),
    L.filter(a => new Promise(resolve => resolve(a % 2))),
    L.take(3),
    reduce((a, b) => a + b));

  return res * 10
}

f1().then(console.log); // 350

// 2
async function f2() {
  try {
    return await go(
      [{ val: 1 }, { val: 2 }, null, { val: 4 }, { val: 5 }],
      L.map(({val}) => new Promise(resolve => resolve(val + 10))),
      L.filter(a => a % 2),
      L.take(3),
      reduce((a, b) => a + b));
  } catch (e) {
    return 0;
  }
}

f2().then(console.log); // 0
```

이 테스트 코드가 검증하는 것이 바로 14장(지연+Promise, nop)과 15장(await + try/catch로 잡히는 에러)의 내용이다 — 우리가 직접 구현해 본 그 메커니즘이 라이브러리 선택 기준이 된다.

fp-ts와의 컨셉 차이에 대한 답변:

> The goal of fp-ts is to empower developers to write pure FP apps and libraries built atop higher order abstractions. It includes the most popular data types, type classes, and abstractions from languages like Haskell, PureScript, and Scala.

**fp-ts는 타입 추상화에 더 초점**이 맞추어져 있다 — 하스켈·PureScript·스칼라의 데이터 타입, 타입 클래스, 고차 추상화를 타입스크립트로 가져오는 것이 목표다. 반면 **fxts는 ES6 이터러블 프로토콜 위의 지연 평가·비동기 리스트 프로세싱**이 중심이다.

정리하면 선택 기준은 이렇다.

| 관점 | fxts (fxjs 계열) | fp-ts |
|---|---|---|
| 중심 개념 | 이터러블 프로토콜, 지연 평가, 동시성 | 대수적 타입 클래스(Functor/Monad 등), 순수 FP 추상화 |
| 뿌리 | 이 가이드의 Part 2·4 (이터레이터·nop·C.*) | 이 가이드의 11·13·19장 (하스켈·모나드·Either) |
| 어울리는 팀 | 리스트 프로세싱 중심의 실용적 FP | 하스켈식 순수 FP 설계를 지향하는 팀 |

## 요약

- **함수 합성**(값의 흐름으로 연결)과 **함수 적용의 합성**(작업의 순차 실행)은 다른 개념이다 — 전자는 pipe·모나드의 영역, 후자는 async/await의 영역.
- **Result 타입**은 실패를 던지지 않고 판별 유니언 값으로 반환한다 — Either(11장)·Kleisli(13장)와 같은 계보의 실무 패턴으로, 분기는 값으로 하고 실제 효과만 따로 실행한다.
- **패턴 매칭**(TC39 Stage 1)은 switch·if/else·구조 분해의 한계를 넘어 구조·타입·값·조건을 동시에 검사·분해하는 선언적 분기다 — 조건을 값으로 다루는 언어 차원의 답.
- **Effect-TS**는 실행의 효과 자체를 실행 전까지 아무 일도 일어나지 않는 값(Effect)으로 만들어 조립한다 — 하스켈 IO의 타입스크립트 생태계 판.
- **fxts는 이터러블·지연·동시성 중심, fp-ts는 타입 클래스·순수 FP 추상화 중심** — 팀의 지향점에 따라 선택한다. 라이브러리 검증 기준(지연+Promise 조합, await로 잡히는 에러)은 이 가이드에서 직접 구현하며 확인한 그 성질들이다.

## 다른 챕터와의 관계

- **1장**: "순수하지 못한 작업의 격리"가 이 장에서 Result·Effect라는 구체적 도구로 완성됐다.
- **11장**: Either·패턴 매칭·IO 타입이 이 장의 Result·TC39 패턴 매칭·Effect-TS의 원형이다.
- **13장**: 실패를 값으로 만드는 Kleisli 합성이 Result 타입의 이론적 배경이다.
- **14·15장**: fxts 선택 기준(지연+Promise, 에러 핸들링)이 곧 그 두 장에서 직접 구현한 메커니즘이다.
- **18장**: 상태 패턴의 predicate 캡슐화(객체지향의 "조건을 값으로")와 이 장의 패턴 매칭(함수형의 답)을 대비해 볼 수 있다.
