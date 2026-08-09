# Item 63: 옵셔널 never 속성으로 배타적 OR 모델링하기 (Use Optional Never Properties to Model Exclusive Or)

## 핵심 질문

타입스크립트의 `|`가 "둘 다"를 허용한다면, "둘 중 하나만"은 어떻게 표현하는가?

일상 언어의 "또는"은 배타적 OR이다. 포괄적 OR을 쓰는 것은 프로그래머와 논리학자뿐이다. 타입스크립트에서 이 둘은 헷갈리기 쉽다.

```typescript
interface ThingOne {
  shirtColor: string;
}
interface ThingTwo {
  hairColor: string;
}
type Thing = ThingOne | ThingTwo;
```

마지막 줄을 보통 "Thing은 ThingOne **또는** ThingTwo"라고 읽는다. 하지만 자바스크립트의 런타임 `||`처럼 타입 수준의 `|`도 **포괄적 OR**이다. 어떤 것이 ThingOne이면서 동시에 ThingTwo이지 말라는 법이 없다.

```typescript
const bothThings = {
  shirtColor: 'red',
  hairColor: 'blue',
};
const thing1: ThingOne = bothThings;  // OK
const thing2: ThingTwo = bothThings;  // OK
```

구조적 타입 시스템(Item 4) 때문이다 — 두 타입 모두 선언에 없는 추가 속성을 허용한다(잉여 속성 체크가 이를 가릴 때도 있지만 — Item 11).

## 1. 표준 트릭 — 옵셔널 never

정말 배타적 OR을 원한다면? 인터페이스에 **옵셔널 never 타입**을 넣어 속성을 금지하는 것이 표준 트릭이다.

```typescript
interface OnlyThingOne {
  shirtColor: string;
  hairColor?: never;
}
interface OnlyThingTwo {
  hairColor: string;
  shirtColor?: never;
}
type ExclusiveThing = OnlyThingOne | OnlyThingTwo;
```

이제 아까의 할당들이 전부 막힌다.

```typescript
const thing1: OnlyThingOne = bothThings;
//    ~~~~~~ Types of property 'hairColor' are incompatible.
const thing2: OnlyThingTwo = bothThings;
//    ~~~~~~ Types of property 'shirtColor' are incompatible.
const allThings: ExclusiveThing = {
  //  ~~~~~~~~~ Types of property 'hairColor' are incompatible.
  shirtColor: 'red',
  hairColor: 'blue',
};
```

**어떤 값도 never에 할당할 수 없기 때문**에 동작한다. 그런데 속성이 옵셔널이라 빠져나갈 길이 정확히 하나 있다 — **그 속성을 갖지 않는 것.**

## 2. 유니온 밖에서도 — Vector2D의 z 금지

이 트릭은 유니온에만 유용한 것이 아니다. Item 4에서 봤듯 구조적 타이핑은 2차원·3차원 벡터의 좋은 모델이 아니다. 옵셔널 never로 2D 벡터의 `z` 속성을 직접 금지할 수 있다.

```typescript
interface Vector2D {
  x: number;
  y: number;
  z?: never;
}

function norm(v: Vector2D) {
  return Math.sqrt(v.x ** 2 + v.y ** 2);
}
const v = {x: 3, y: 4, z: 5};
const d = norm(v);
//             ~ Types of property 'z' are incompatible.
```

`z?: never`가 없었다면 이 호출은 구조적으로 유효해서(의미적으로는 틀렸어도) 에러가 아니었을 것이다. Vector2D 문제의 또 다른 접근인 브랜드는 Item 64에서.

## 3. 대안들 — 태그된 유니온, XOR 제네릭

**태그된 유니온**(Item 34)으로도 배타적 OR을 얻을 수 있다.

```typescript
interface ThingOneTag {
  type: 'one';
  shirtColor: string;
}
interface ThingTwoTag {
  type: 'two';
  hairColor: string;
}
type Thing = ThingOneTag | ThingTwoTag;
```

문자열이 'one'이면서 'two'일 수는 없으니 두 타입 사이에 겹침이 없고, 포괄적/배타적 OR의 구별 자체가 사라진다. 가능할 때 태그된 유니온을 쓸 좋은 이유가 또 하나 늘었다.

옵셔널 never 속성을 손으로 붙이는 대신 **제네릭 XOR 헬퍼**를 정의할 수도 있다.

```typescript
type XOR<T1, T2> =
  (T1 & {[k in Exclude<keyof T2, keyof T1>]?: never}) |
  (T2 & {[k in Exclude<keyof T1, keyof T2>]?: never});

type ExclusiveThing = XOR<ThingOne, ThingTwo>;
const allThings: ExclusiveThing = {
  //  ~~~~~~~~~ Types of property 'hairColor' are incompatible.
  shirtColor: 'red',
  hairColor: 'blue',
};
```

태그된 유니온이 타입스크립트에서 배타적 타입을 만드는 더 흔한 방법이지만, **명시적 태그를 추가할 수 없거나 하고 싶지 않은 상황**에서 옵셔널 never 트릭이 도움이 된다.

## 기억해야 할 것들

- 타입스크립트에서 "또는"은 "포괄적 OR"이다: `A | B`는 A, B, 또는 둘 다를 뜻한다. 코드에서 "둘 다"의 가능성을 고려하고, 처리하거나 금지하라.
- 편리한 곳에서는 태그된 유니온으로 배타적 OR을 모델링하라.
- 그렇지 않은 곳에서는 옵셔널 never 속성의 사용을 고려하라.
