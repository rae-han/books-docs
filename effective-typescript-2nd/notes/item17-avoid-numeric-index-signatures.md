# Item 17: 숫자 인덱스 시그니처 피하기 (Avoid Numeric Index Signatures)

## 핵심 질문

자바스크립트에서 객체의 키가 숫자일 수 없다면, 배열의 숫자 인덱스는 대체 무엇인가? 내 타입에 `[n: number]`를 쓰면 안 되는 이유는?

자바스크립트는 기벽으로 유명한 언어다. 암시적 타입 강제(`"0" == 0`이 true)는 `===`/`!==`로 피하면 되지만, **객체 모델의 기벽**은 타입스크립트 타입 시스템이 일부를 모델링하고 있어서 더 중요하다(객체 래퍼는 Item 10에서 봤고, 이 아이템은 또 다른 기벽이다).

## 1. 자바스크립트 객체의 키는 문자열(또는 심벌)뿐이다

자바스크립트에서 객체는 키/값 쌍의 모음이다. 키는 보통 문자열이고(ES2015부터는 심벌도), 값은 무엇이든 된다. 파이썬이나 자바 같은 "해시 가능한" 객체 개념이 없어서, 복잡한 객체를 키로 쓰려 하면 `toString`이 호출되어 문자열로 변환된다.

```javascript
> x = {}
> x[[1, 2, 3]] = 2
> x
{ '1,2,3': 2 }
```

특히 **숫자는 키가 될 수 없다**. 속성 이름으로 숫자를 쓰면 런타임이 문자열로 변환한다.

```javascript
> { 1: 2, 3: 4 }
{ '1': 2, '3': 4 }
```

그럼 배열은? 분명 객체다(`typeof []` → `'object'`). 그런데 숫자 인덱스를 쓰는 것이 지극히 자연스럽다. 이것들도 문자열로 변환될까? 가장 기묘한 기벽 하나로, 답은 "그렇다"이다. 문자열 키로도 배열 요소에 접근할 수 있고, `Object.keys`는 문자열을 돌려준다.

```javascript
> x = [1, 2, 3]
> x['1']
2
> Object.keys(x)
[ '0', '1', '2' ]
```

## 2. 타입스크립트의 숫자 키는 "유용한 허구"다

타입스크립트는 숫자 키를 허용하고 문자열 키와 **구별**하는 방식으로 이를 모델링한다. `lib.es5.d.ts`의 `Array` 선언을 파 보면(Item 6):

```typescript
interface Array<T> {
  // ...
  [n: number]: T;
}
```

이것은 순전히 **허구**다 - ECMAScript 표준이 요구하는 대로 런타임은 문자열 키를 받아들인다. 하지만 실수를 잡아 주는 유용한 허구다.

```typescript
const xs = [1, 2, 3];
const x0 = xs[0];    // OK
const x1 = xs['1'];  // 문자열화된 숫자 상수도 OK

const inputEl = document.getElementsByTagName('input')[0];
const xN = xs[inputEl.value];
//         ~~~~~~~~~~~~~~~~~ Index expression is not of type 'number'.
```

이 경우 `inputEl.valueAsNumber`가 더 적절하며 타입 에러도 고쳐 준다.

허구는 허구라는 것을 기억해야 한다. 타입 시스템의 다른 모든 측면처럼 런타임에는 지워지므로(Item 3) `Object.keys`는 여전히 문자열을 돌려준다.

```typescript
const keys = Object.keys(xs);
//    ^? const keys: string[]
```

패턴은 이렇다: **숫자 인덱스 시그니처는 "넣을 때는 대체로 숫자여야 하지만 꺼낼 때는 문자열"** 이라는 뜻이다. 혼란스럽게 들린다면, 실제로 혼란스럽기 때문이다!

## 3. 대안 - Array, 튜플, ArrayLike, Iterable

일반 규칙으로, **타입의 인덱스 시그니처에 `number`를 쓸 이유는 거의 없다.** 숫자로 인덱싱할 무언가가 필요하면 `Array`나 튜플 타입을 쓰면 된다. `number` 인덱스 타입은 숫자 속성이 자바스크립트에 실재한다는 오해를 자신에게든 코드 독자에게든 심어 줄 수 있다.

"배열은 `push`·`concat` 같은 프로토타입 속성이 잔뜩 있어서 받기 싫다"는 반론이 나온다면 좋은 신호다 - 구조적으로 생각하고 있다는 뜻이니까(Item 4). 임의 길이의 튜플이나 배열 비슷한 구조를 정말 받고 싶다면 `ArrayLike`가 있다.

```typescript
function checkedAccess<T>(xs: ArrayLike<T>, i: number): T {
  if (i >= 0 && i < xs.length) {
    return xs[i];
  }
  throw new Error(`Attempt to access ${i} which is past end of array.`)
}
```

(안전한 배열 접근을 위한 `noUncheckedIndexedAccess` 옵션도 있다 - Item 48.)

`ArrayLike`는 `length`와 숫자 인덱스 시그니처만 가진다. 이름대로 `NodeList` 같은 배열 유사 구조를 넘길 수 있게 해 준다. 드물게 이것이 필요한 경우에는 일반 배열 대신 쓰되, **키는 여전히 진짜로는 문자열**임을 기억하라.

```typescript
const tupleLike: ArrayLike<string> = {
  '0': 'A',
  '1': 'B',
  length: 2,
};  // OK
```

순회만 가능하면 된다면 `Iterable` 타입을 쓸 수도 있다 - 제너레이터 표현식도 넘길 수 있게 된다(Item 30).

> **핵심 통찰**: 자바스크립트(그리고 타입스크립트)의 객체 키는 문자열 아니면 심벌이다. 숫자 인덱스 타입은 `Array` 타입을 편하게 쓰기 위한 양보로 이해하는 것이 최선이다. 숫자 인덱스는 실재하지 않는다 - 내 타입에서는 쓰지 마라.

## 기억해야 할 것들

- 배열은 객체이므로 키는 숫자가 아니라 문자열이다. 인덱스 시그니처의 `number`는 버그를 잡기 위해 설계된 순수 타입스크립트 구문이다.
- 인덱스 시그니처에 `number`를 직접 쓰기보다 `Array`·튜플·`ArrayLike`·`Iterable` 타입을 선호하라.
