# Item 20: 변수가 타입을 얻는 방식 이해하기 (Understand How a Variable Gets Its Type)

## 핵심 질문

`let x = 'x'`의 타입은 왜 `"x"`가 아니라 `string`인가? 넓히기(widening)를 통제하는 도구들 — const, as const, satisfies — 은 각각 무엇을 하는가?

Item 7에서 봤듯 런타임의 변수는 하나의 값을 갖지만, 타입스크립트가 코드를 검사하는 정적 분석 시점의 변수는 가능한 값들의 집합, 즉 타입을 갖는다. 상수로 변수를 초기화하며 타입을 명시하지 않으면 타입 체커는 **지정된 값 하나로부터 가능한 값들의 집합을 결정**해야 한다. 이 과정이 타입스크립트에서 넓히기(*widening - 리터럴 값으로부터 그것을 포함하는 더 넓은 타입을 추론하는 과정*)다. 이를 이해하면 에러의 원인을 파악하고 타입 구문을 더 효과적으로 쓸 수 있다.

## 1. 넓히기가 만드는 에러

벡터 라이브러리를 만든다고 하자.

```typescript
interface Vector3 { x: number; y: number; z: number; }
function getComponent(vector: Vector3, axis: 'x' | 'y' | 'z') {
  return vector[axis];
}

let x = 'x';
let vec = {x: 10, y: 20, z: 30};
getComponent(vec, x);
//                ~ Argument of type 'string' is not assignable
//                  to parameter of type '"x" | "y" | "z"'
```

이 코드는 잘 실행되는데 왜 에러일까? `x`의 타입이 `string`으로 추론됐는데 `getComponent`는 더 구체적인 타입을 기대하기 때문이다 — 넓히기가 낳은 타입 에러다.

넓히기는 본질적으로 모호하다. 주어진 값에는 가능한 타입이 많다.

```typescript
const mixed = ['x', 1];
```

`mixed`의 타입 후보: `('x' | 1)[]`, `['x', 1]`, `[string, number]`, `readonly [string, number]`, `(string|number)[]`, `readonly (string|number)[]`, `[any, any]`, `any[]` … 더 많은 문맥이 없으면 어느 것이 "맞는지" 알 수 없고, 타입스크립트는 의도를 추측해야 한다(이 경우 `(string|number)[]`). 아무리 똑똑해도 마음을 읽을 수는 없으니 100% 맞히지 못하고, 그 결과가 방금 본 것 같은 뜻밖의 에러다.

첫 예제에서 `x`가 `string`으로 추론된 것은 이런 코드를 허용하기 위해서다.

```typescript
let x = 'x';
x = 'a';
x = 'Four score and seven years ago...';
```

`x = /x|y|z/`나 `x = ['x','y','z']`도 유효한 자바스크립트지만, 타입스크립트는 **구체성과 유연성 사이에서 균형**을 잡는다. 변수 타입은 선언 후에 전혀 다른 것으로 바뀌지 않으므로(Item 19) `string`이 `string|RegExp`나 `any`보다 합리적이다. `let`으로 할당된 원시 값의 일반 규칙: **"기저 타입(base type)"으로 확장된다** — `"x"`→`string`, `39`→`number`, `true`→`boolean`. (null과 undefined는 다르게 처리된다 — Item 25.)

## 2. 넓히기 통제 ① — const

`let` 대신 `const`로 선언하면 더 좁은 타입을 얻는다. 실제로 첫 예제의 에러도 고쳐진다.

```typescript
const x = 'x';
//    ^? const x: "x"
let vec = {x: 10, y: 20, z: 30};
getComponent(vec, x);  // OK
```

재할당이 불가능하니 이후 할당에 에러를 낼 위험 없이 더 정밀한 타입을 추론할 수 있고, 리터럴 타입 `"x"`는 `"x"|"y"|"z"`에 할당 가능하다.

하지만 const가 만병통치는 아니다 — **객체와 배열에는 여전히 모호함**이 있다. 자바스크립트에서는 문제없는 이 코드를 보자.

```typescript
const obj = {
  x: 1,
};
obj.x = 3;    // OK
obj.x = '3';
//  ~ Type 'string' is not assignable to type 'number'
obj.y = 4;
//  ~ Property 'y' does not exist on type '{ x: number; }'
obj.z = 5;
//  ~ Property 'z' does not exist on type '{ x: number; }'
obj.name = 'Pythagoras';
//  ~~~~ Property 'name' does not exist on type '{ x: number; }'
```

`obj`의 타입은 구체성 스펙트럼 어디로든 추론될 수 있다 — 구체적인 끝에 `{readonly x: 1}`, 더 일반적으로 `{x: number}`, 더 나가면 `{[key: string]: number}`, `object`, `any`/`unknown`. 객체에서 타입스크립트는 "최선의 공통 타입(best common type)"을 추론하는데, **각 속성을 `let`으로 할당한 것처럼** 취급한다. 그래서 `obj`는 `{x: number}` — `x`에 다른 number는 재할당할 수 있지만 string은 안 되고, 직접 할당으로 다른 속성을 추가할 수도 없다. (객체를 한 번에 만들어야 하는 좋은 이유다 — Item 21.)

## 3. 넓히기 통제 ② — 명시적 구문, 문맥, as const

기본 동작을 덮어쓰는 방법들:

**① 명시적 타입 구문**

```typescript
const obj: { x: string | number } = { x: 1 };
//    ^? const obj: { x: string | number; }
```

**② 추가 문맥 제공** — 값을 함수 인수로 넘기는 등(Item 24).

**③ const 단언(`as const`)** — `let`/`const`(값 공간)와 혼동하지 말 것. 순수 타입 수준 구문이다.

```typescript
const obj1 = { x: 1, y: 2 };
//    ^? const obj1: { x: number; y: number; }
const obj2 = { x: 1 as const, y: 2 };
//    ^? const obj2: { x: 1; y: number; }
const obj3 = { x: 1, y: 2 } as const;
//    ^? const obj3: { readonly x: 1; readonly y: 2; }
```

값 뒤에 `as const`를 쓰면 **가능한 가장 좁은 타입**을 추론한다 — 넓히기가 없다. 진짜 상수라면 보통 이것이 원하는 것이다. 배열에 쓰면 튜플 타입을 얻는다.

```typescript
const arr1 = [1, 2, 3];
//    ^? const arr1: number[]
const arr2 = [1, 2, 3] as const;
//    ^? const arr2: readonly [1, 2, 3]
```

문법이 비슷해도 const 단언을 타입 단언(`as T`)과 혼동하면 안 된다 — 타입 단언은 피하는 게 좋지만(Item 9), **const 단언은 타입 안전성을 해치지 않으며 언제나 OK**다.

**④ 헬퍼 함수** — 튜플 타입으로 추론하되 각 요소는 기저 타입으로 넓히고 싶다면:

```typescript
function tuple<T extends unknown[]>(...elements: T) { return elements; }

const arr3 = tuple(1, 2, 3);
//    ^? const arr3: [number, number, number]
const mix = tuple(4, 'five', true);
//    ^? const mix: [number, string, boolean]
```

`tuple` 함수는 런타임에는 아무 역할이 없고 타입스크립트의 추론을 원하는 방향으로 이끈다. `Object.freeze`도 추론을 이끈다.

```typescript
const frozenArray = Object.freeze([1, 2, 3]);
//    ^? const frozenArray: readonly number[]
const frozenObj = Object.freeze({x: 1, y: 2});
//    ^? const frozenObj: Readonly<{ x: 1; y: 2; }>
```

const 단언처럼 추론 타입에 `readonly` 한정자가 들어가지만(표시는 달라도 `frozenObj`의 타입은 `obj3`과 정확히 같다), 차이가 있다 — freeze는 **자바스크립트 런타임이 강제**하고, 대신 **얕다**. const 단언은 깊다(readonly는 Item 14).

## 4. 넓히기 통제 ③ — satisfies

`satisfies` 연산자는 값이 타입의 요구사항을 **만족하는지 확인**하면서, 더 넓은 타입으로 추론되는 것을 막아 추론을 이끈다.

```typescript
type Point = [number, number];

const capitals1 = { ny: [-73.7562, 42.6526], ca: [-121.4944, 38.5816] };
//    ^? const capitals1: { ny: number[]; ca: number[]; }

const capitals2 = {
  ny: [-73.7562, 42.6526], ca: [-121.4944, 38.5816]
} satisfies Record<string, Point>;
//    ^? const capitals2: { ny: [number, number]; ca: [number, number]; }
```

혼자 두면 타입스크립트는 값들을 `let`처럼 `number[]`로 넓히지만, `satisfies`가 `Point` 너머로 넓혀지는 것을 막는다. 같은 타입의 **구문(annotation)** 과 비교해 보면:

```typescript
const capitals3: Record<string, Point> = capitals2;
capitals3.pr;  // 런타임에 undefined
//        ^? Point
capitals2.pr;
//        ~~ Property 'pr' does not exist on type '{ ny: ...; ca: ...; }'
```

`satisfies`에서 나온 타입은 **정확한 키**를 유지해서 에러를 잡아 준다. 그리고 객체 일부가 타입에 할당 불가능하면 에러를 보고한다.

```typescript
const capitalsBad = {
  ny: [-73.7562, 42.6526, 148],
  //  ~~ Type '[number, number, number]' is not assignable to type 'Point'.
  ca: [-121.4944, 38.5816, 26],
  //  ~~ Type '[number, number, number]' is not assignable to type 'Point'.
} satisfies Record<string, Point>;
```

const 단언보다 나은 점이다 — 에러가 객체를 **사용하는 곳이 아니라 정의하는 곳**에서 보고된다.

> **핵심 통찰**: 넓히기 때문으로 의심되는 잘못된 에러를 만나면 도구 상자를 떠올려라 — `let`→`const` 변경, 명시적 타입 구문, `tuple`·`Object.freeze` 같은 헬퍼, const 단언, satisfies 절. 그리고 언제나처럼 편집기에서 타입을 확인하는 것이 직관을 세우는 열쇠다(Item 6).

## 기억해야 할 것들

- 타입스크립트가 리터럴에서 타입을 넓혀서 추론하는 방식을 이해하라.
- 이 동작에 영향을 주는 방법들에 익숙해져라: `const`, 타입 구문, 문맥, 헬퍼 함수, `as const`, `satisfies`.
