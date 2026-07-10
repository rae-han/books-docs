# Chapter 13: Monads and Kleisli Composition (모나드와 Kleisli 합성)

## 핵심 질문

모나드는 왜 "함수 합성을 안전하게 하는 도구"인가? Kleisli 합성은 에러가 있을 수 있는 세계에서 무엇을 보장하며, Promise는 어떤 종류의 모나드인가?

---

12장에서 Promise가 비동기 상황을 값으로 만든다는 것을 확인했다. 이 장에서는 한 걸음 더 들어가, Promise를 **합성의 관점**에서 바라본다. 함수 합성이 실패할 수 있는 두 가지 상황 — 값이 없거나 잘못된 경우, 그리고 시점이 맞지 않는 경우 — 에서 모나드라는 아이디어가 어떻게 합성을 안전하게 만드는지, 그리고 에러가 날 수 있는 상황의 합성 규칙인 Kleisli 합성을 Promise가 어떻게 지원하는지 살펴본다.

> **참고**: 자바스크립트는 동적 타입 언어이고 타입을 중심으로 사고하며 프로그래밍하는 언어는 아니기 때문에, 모나드나 대수 구조 타입 같은 개념이 표면에 잘 드러나지 않는 경향이 있다. 자바스크립트와 비슷한 경향을 가진 Clojure, LISP, Scheme 같은 언어에서도 모나드라는 개념을 특별히 중시해 이야기하지 않는다 — 실제로 "모나드"라는 이름의 값이나 객체가 있는 것이 아니기 때문이다. 개념은 이름이 아니라 **동작**으로 이해하는 것이 좋다.

---

## 1. 합성 관점에서의 Promise와 모나드

Promise는 비동기 상황에서 함수 합성을 안전하게 하기 위한 도구다. 비동기 값을 가지고 연속적인 함수 실행을 안전하게 하는 모나드라고 설명할 수 있다. 모나드를 알려면 먼저 함수 합성을 봐야 한다.

`f . g`라는 함수 합성은 `f(g(x))`와 같다. `x`라는 인자를 받았을 때 `g`를 실행하고, 그 결과를 그대로 `f`에게 전달한다. 이렇게 연속적으로 함수가 실행되는 합성을 **상황에 따라 안전하게** 하기 위한 개념이 모나드이고, 그 구현체 중 비동기 상황을 안전하게 합성하는 것이 Promise다.

모나드는 결국 함수 합성을 안전하게 하기 위한 도구다. **모나드는 값이 들어 있는 박스**라고 생각하면 된다. 컨테이너(박스)에 값이 들어 있고, 이 값을 통해 함수 합성을 안전하게 해나가는 것이다.

```typescript
const g = a => a + 1;
const f = a => a * a;

console.log(f(g(1))); // 4
console.log(f(g())); // NaN
```

첫 번째 출력은 `g`와 `f`를 합성한 함수에 1을 전달해 원하는 결과를 잘 얻었다. 하지만 두 번째처럼 빈 값을 넣으면 비정상적인 값(`NaN`)이 만들어지고, 심지어 잘못된 값인 채로 로그를 찍는 **효과**까지 일어났다. `g`에게 어떤 값이 올지 알 수 없는 현실의 프로그래밍에서는, 잘못됐을 때 로그를 출력하고 싶지 않고 외부에 영향을 주고 싶지 않은데도 효과가 흘러가서 문제를 일으킨다.

이런 상황 — 어떤 값이 들어올지 알 수 없는 상황 — 에서 함수 합성을 안전하게 하는 아이디어가 모나드다.

```typescript
const g = a => a + 1;
const f = a => a * a;

const result = [1].map(g).map(f);
console.log(result); // [4]
```

여기서 `[1]`이 모나드다. 박스(`[]`)가 있고, 박스 안에 연산에 필요한 재료가 들어 있다. 함수 합성을 할 때는 박스가 가진 메서드(`map`)를 통해 한다 — 위에서는 `map`으로 `g`, `f`를 연속 실행하도록 합성했다.

하지만 `Array` 자체는 최종적으로 필요한 값이 아니다. Array는 개발자가 효과를 만들거나 값을 다룰 때 쓰는 **도구**이지 사용자 화면에 노출되는 결론이 아니다. 결론은 `forEach` 같은 함수로 로그를 출력하거나 HTML을 넣는 등 외부 세상에 효과를 만들 때 나온다.

```typescript
[1].map(g).map(f).forEach(r => console.log(r)); // 4
```

이때 박스가 비어 있다면? **아무 일도 일어나지 않는다.**

```typescript
[].map(g).map(f).forEach(r => console.log(r)); // 아무 일도 없음
```

모나드 형태의 Array로 합성하면 잘못된 값이 왔을 때 효과를 일으키지 않는 방식으로 다룰 수 있다. **부수효과가 일어나기 전에 함수들을 안전하게 합성해 두는 기법**이다.

그럼 Promise는 어떤 합성을 하는 걸까? 생김새부터 비슷하다 — `resolve`로 값을 만들고 `then`으로 합성한다.

```typescript
Array.of(1).map(g).map(f).forEach(r => console.log(r)); 
Promise.resolve(1).then(g).then(f).then(r => console.log(r))
```

다만 안전하게 만드는 대상이 다르다. Array 모나드가 "값이 있거나 없거나" 하는 상황에서의 안전한 합성이라면, Promise는 **비동기 상황, 즉 시점**에서의 안전한 합성이다.

```typescript
Array.of().map(g).map(f).forEach(r => console.log(r)); // 출력 없음
Promise.resolve().then(g).then(f).then(r => console.log(r)) // NaN
```

빈 값에 대해서는 Promise가 보호해 주지 않는다(NaN이 나온다). 대신 Promise는 "어떤 시점 이후에야 값을 알 수 있는" 효과를 가진 모나드로서, **함수 합성을 하는 시점을 안전하게** 만든다.

```typescript
new Promise(resolve => setTimeout(() => resolve(1), 100)).then(g).then(f).then(r => console.log(r)); // 4
```

정리하면 — Array가 값이 없을 수도 있고 filter로 좁혀질 수도 있는 상황에서 연속 실행을 안전하게 합성한다면, Promise는 딜레이가 필요한 상황에서도 **함수를 적절한 시점에 평가해 합성**시키기 위한 도구다.

> **핵심 통찰**: 모나드는 "값이 든 박스 + 합성 메서드"다. 박스의 종류마다 지켜주는 것이 다르다 — Array는 값의 유무로부터, Promise는 시점으로부터 합성을 지킨다. 11장의 하스켈 `Maybe`(값의 부재)와 `Either`(실패 이유)도 같은 구도의 다른 박스다.

## 2. Kleisli Composition 관점에서의 Promise

Promise는 크레이슬리 합성(*Kleisli Composition 또는 Kleisli Arrow - 오류가 있을 수 있는 상황에서의 함수 합성을 안전하게 하는 규칙*)을 지원하는 도구이기도 하다.

수학적 프로그래밍이라면 안전하고 정확한 상수·변수로 합성이 이뤄지고 평가되지만, 현실 프로그래밍에는 상태와 효과(Effect)가 있어 외부 세상에 의존할 수밖에 없다. 예를 들어 `f(g(x))`로 합성했을 때 동일한 정의역 `x`라면 `f(g(x)) = f(g(x))`가 성립해야 하지만, `g`가 외부 세계의 값(이를테면 시간에 따라 변하는 상태)을 바라보고 있다면 성립을 보장할 수 없다.

이런 상황에서 특정한 규칙을 만들어 합성을 안전하게 만드는 것이 Kleisli 합성이다. 규칙은 이렇다 — `g`에서 에러 없이 동작하면 `f(g(x)) = f(g(x))`이고, 만약 **`g`에서 에러가 난 경우에는 `f(g(x)) = g(x)`가 되도록** 합성한다. 즉 `g`가 문제를 만나면 `g`가 반환한 값이 `f`와 합성돼도 마치 합성하지 않은 것과 같아지는 것이다.

코드로 살펴보자.

```typescript
const users = [
  { id: 1, name: 'AA' },
  { id: 2, name: 'BB' },
  { id: 3, name: 'CC' },
];

const getUserById = (id) =>
  find((user) => user.id === id, users);
const getName = ({ name }) => name;

const f = getName;
const g = getUserById;

const fg = (id) => f(g(id));

console.log(fg(2) === fg(2)); // true
```

`id`로 사용자를 찾는 `g`와 이름을 꺼내는 `f`를 합성해 같은 인자를 전달하면 두 결과는 같다. 그런데 실세계에서는 `users`의 상태가 변할 수 있다.

```typescript
const before = fg(2);

users.pop();
users.pop();

const after = fg(2);

console.log(before == after);
```

이 코드는 비교까지 가지도 못하고 `after`를 만드는 동안 에러가 난다 — `g(2)`가 `undefined`를 반환하고 `f`가 `undefined`에서 `name`을 구조 분해하려 하기 때문이다. `f`와 `g` 각각은 안전한 함수지만 **합성한 상황에서** 위험해질 수 있다.

상황에 따라 에러가 날 수 있는 세계에서, 합성하면서도 에러가 나지 않게 하는 것이 Kleisli Arrow다. Promise로 이렇게 작성해 보자.

```typescript
const fg = (id) =>
  Promise.resolve(id).then(g).then(f);
```

사실 이것만으로는 여전히 같은 에러가 난다. 핵심은 `g`가 **실패를 값으로 반환**하도록 만드는 것이다.

```typescript
const getUserById = (id) =>
  find((user) => user.id === id, users) || Promise.reject('없어요!!');
```

사용자를 찾지 못하면 `Promise.reject('없어요!!')` — rejected 상태가 들어 있는 값 — 를 반환한다. 이렇게 하면 `g`만 단독으로 실행했을 때와 합성 함수 `fg`를 실행했을 때 결과가 같아진다. rejected Promise에 대해 `then(f)`는 **아무 일도 하지 않고 통과**시키기 때문이다 — `f(g(x)) = g(x)`가 실현된 것이다.

`fg`를 합성할 때 catch를 쓰면 어떻게 될까?

```typescript
const fg = (id) =>
  Promise.resolve(id)
    .then(g)
    .then(f)
    .catch((e) => e);
```

그렇다면 아래 두 결과는 같다.

```typescript
users.pop();
users.pop();

fg(2).then(console.log); // 없어요!!
g(2).then(console.log).catch(console.log); // 없어요!!
```

에러가 난 지점 이후의 합성(`then(f)`)은 모두 건너뛰어지고, 흐름은 catch로 모인다. **에러가 있을 수 있는 세계에서, 실패를 값(rejected Promise)으로 만들어 합성 규칙을 지키는 것** — 이것이 Promise가 지원하는 Kleisli 합성이다.

> **참고**: 하스켈은 같은 문제를 `Either`(Left에 실패 이유, Right에 성공 값)와 `Maybe`(Nothing/Just) 타입으로 푼다(11장). 실패를 예외(throw)가 아니라 **타입이 있는 값**으로 흐르게 한다는 점에서 Promise.reject와 같은 구도다. 19장의 `Result<T, E>` 타입은 이 아이디어를 타입스크립트 일상 코드로 가져온 것이다.

## 3. promise.then의 중요한 규칙

Promise에는 중요한 규칙이 있다. **then 메서드로 결과를 꺼냈을 때 그 값은 반드시 Promise가 아니다.**

```typescript
Promise.resolve(Promise.resolve(Promise.resolve(1))).then(console.log); // 1
```

Promise가 중첩돼 있어도 단 한 번의 then으로 안의 결과를 꺼낼 수 있다. 직접 생성해도 마찬가지다.

```typescript
new Promise((resolve) => resolve(new Promise((resolve) => resolve(1)))).then(
  console.log,
); // 1
```

then은 해당 Promise 껍질 하나만 벗겨 안의 Promise를 리턴하는 것이 아니라, 아무리 깊게 대기가 걸려 있어도(체이닝이 많아도) **반드시 안쪽의 값을 한 번에** 꺼낸다. 프로미스 체인이 연속으로 대기 중이어도 원하는 곳에서 then 한 번으로 결과를 받을 수 있다는 뜻이고, 자바스크립트에서 언어와 개발자가 소통하는 중요한 법칙이다.

> **참고**: 모나드 용어로 말하면 Promise의 then은 flat(펼침)을 내장한 flatMap처럼 동작한다 — 중첩된 박스(`Promise<Promise<T>>`)가 자동으로 평탄화되어 `Promise<T>`로 유지된다. 8장의 `L.flatMap`이 배열 세계에서 하던 일을, Promise는 규약 차원에서 항상 수행하는 셈이다.

## 4. 정리 문답

**함수 합성과 모나드 관점에서 Promise는 어떤 도구로 설명될 수 있는가?**
비동기 상황에서도 함수들을 안전하게 연속적으로 합성(compose)할 수 있도록 돕는 도구.

**Kleisli 합성 관점에서 Promise는 어떤 점에 기여하며 안전한 함수 합성을 돕는가?**
함수 실행 중 발생할 수 있는 오류나 실패를 rejected 값으로 만들어 이후 합성을 무효화하고, `.catch()` 등으로 안전하게 처리하며 합성을 이어가거나 멈출 수 있게 한다.

## 요약

- **모나드는 값이 든 박스 + 안전한 합성 메서드**다. `[1].map(g).map(f)`처럼 박스의 메서드로 합성하면, 박스가 비어 있을 때 효과가 일어나지 않는다 — 부수효과 전에 함수들을 안전하게 합성해 두는 기법.
- **Array는 값의 유무**로부터, **Promise는 시점**으로부터 합성을 지킨다 — `then`은 값이 준비된 적절한 시점에 함수를 평가해 합성한다.
- **Kleisli 합성**: 에러가 날 수 있는 세계의 합성 규칙 — `g`가 실패하면 `f(g(x)) = g(x)`. Promise에서는 실패를 `Promise.reject`(값)로 만들면 이후 then들이 통과되어 이 규칙이 실현된다.
- **then의 규칙**: 아무리 중첩된 Promise라도 then은 안쪽 값을 한 번에 꺼낸다(`Promise<Promise<T>>`는 존재하지 않는 것처럼 동작한다).
- 하스켈의 Maybe/Either, 타입스크립트의 Result 타입은 같은 구도의 다른 구현이다.

## 다른 챕터와의 관계

- **1장**: 참조 투명성이 깨지는 현실(외부 상태 의존)이 이 장의 출발 문제였다.
- **8장**: find의 `undefined`와 하스켈 `Maybe`가 "값이 없을 수 있는 상황"의 두 해법이었다 — 이 장은 그것을 합성 규칙으로 일반화했다.
- **11장**: 하스켈의 Either·패턴 매칭이 Kleisli 아이디어의 타입 시스템 버전이다.
- **12장**: then 체이닝의 안전성이 이 장에서 모나드·Kleisli로 설명됐다.
- **14장**: `Symbol('nop')`을 이용한 지연 filter의 비동기 지원이 **Kleisli 합성의 실전 응용**으로 등장한다.
- **19장**: Result 타입·Effect-TS가 "실패와 효과를 값으로"라는 이 장의 아이디어를 애플리케이션 설계로 확장한다.
