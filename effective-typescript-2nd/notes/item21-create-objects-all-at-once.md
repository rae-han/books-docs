# Item 21: 객체를 한 번에 만들기 (Create Objects All at Once)

## 핵심 질문

객체를 조각조각 만들면 타입스크립트에서 무슨 문제가 생기는가? 조건부 속성은 어떻게 타입 안전하게 추가하는가?

Item 19에서 봤듯 변수의 값은 바뀌어도 타입은 일반적으로 바뀌지 않는다. 그래서 어떤 자바스크립트 패턴은 타입스크립트로 모델링하기 쉽고 어떤 것은 어렵다. 특히 **객체는 조각조각이 아니라 한 번에 만드는 것이 좋다.**

## 1. 조각조각 만들기의 문제

자바스크립트에서 2차원 점 객체를 만드는 한 방법:

```typescript
const pt = {};
//    ^? const pt: {}
pt.x = 3;
// ~ Property 'x' does not exist on type '{}'
pt.y = 4;
// ~ Property 'y' does not exist on type '{}'
```

첫 줄에서 `pt`의 타입이 값 `{}`로부터 추론됐고, 알려진 속성에만 할당할 수 있기 때문이다. `Point` 인터페이스를 정의하면 반대 문제가 생긴다.

```typescript
interface Point { x: number; y: number; }
const pt: Point = {};
//    ~~ Type '{}' is missing the following properties from type 'Point': x, y
pt.x = 3;
pt.y = 4;
```

타입 단언이 해법처럼 보이지만:

```typescript
const pt = {} as Point;
pt.x = 3;
pt.y = 4;  // OK
```

이 패턴의 문제는 **사용 전에 모든 속성을 할당했는지 타입스크립트가 검사하지 않는다**는 것이다. `pt.y` 할당을 빼먹어도 타입 체크는 통과하고 NaN이나 런타임 예외로 이어질 수 있다. Item 9에서 봤듯 단언은 첫 번째로 집는 도구가 아니어야 한다. 최선은 **타입 선언과 함께 한 번에 정의하는 것**이다.

```typescript
const pt: Point = {
  x: 3,
  y: 4,
};
```

## 2. 작은 객체들로 큰 객체 만들기 - 스프레드

작은 객체들로 큰 객체를 만들 때도 여러 단계로 하지 마라.

```typescript
const pt = {x: 3, y: 4};
const id = {name: 'Pythagoras'};
const namedPoint = {};
Object.assign(namedPoint, pt, id);
namedPoint.name;
//         ~~~~ Property 'name' does not exist on type '{}'
```

객체 스프레드 문법 `...`으로 한 번에 만들면 된다.

```typescript
const namedPoint = {...pt, ...id};
//    ^? const namedPoint: { name: string; x: number; y: number; }
namedPoint.name;  // OK
```

스프레드로 **필드를 하나씩, 타입 안전하게** 쌓아 올릴 수도 있다. 열쇠는 갱신마다 새 변수를 써서 각각 새 타입을 얻게 하는 것이다(Item 19).

```typescript
const pt0 = {};
const pt1 = {...pt0, x: 3};
const pt: Point = {...pt1, y: 4};  // OK
```

이렇게 단순한 객체에는 에두른 방법이지만, 객체에 속성을 추가하며 타입스크립트가 새 타입을 추론하게 하는 유용한 기법이다. 마지막 줄의 타입 선언이 필요한 속성을 다 추가했는지 보장한다.

## 3. 조건부 속성 추가

속성을 조건부로, 타입 안전하게 추가하려면 **아무 속성도 추가하지 않는 `{}` 또는 falsy 값**과 스프레드를 결합한다.

```typescript
declare let hasMiddle: boolean;
const firstLast = {first: 'Harry', last: 'Truman'};
const president = {...firstLast, ...(hasMiddle ? {middle: 'S'} : {})};
//    ^? const president: {
//         middle?: string;
//         first: string;
//         last: string;
//       }
// 또는: const president = {...firstLast, ...(hasMiddle && {middle: 'S'})};
```

추론된 타입에 옵셔널 속성이 생겼다. 여러 필드를 한꺼번에 조건부로 추가할 수도 있다.

```typescript
declare let hasDates: boolean;
const nameTitle = {name: 'Khufu', title: 'Pharaoh'};
const pharaoh = { ...nameTitle, ...(hasDates && {start: -2589, end: -2566})};
//    ^? const pharaoh: {
//         start?: number;
//         end?: number;
//         name: string;
//         title: string;
//       }
```

`start`와 `end`가 둘 다 옵셔널이 됐으므로, 읽을 때는 undefined 가능성을 고려해야 한다.

```typescript
const {start} = pharaoh;
//     ^? const start: number | undefined
```

## 4. 변환으로 만드는 객체/배열

다른 객체나 배열을 **변환**해서 만들 때의 "한 번에 만들기"는 루프 대신 내장 함수형 구문이나 Lodash 같은 유틸리티 라이브러리를 쓰는 것이다(Item 26).

## 기억해야 할 것들

- 객체는 조각조각이 아니라 한 번에 만드는 것을 선호하라.
- 타입 안전하게 속성을 추가하려면 여러 객체와 객체 스프레드 문법(`{...a, ...b}`)을 사용하라.
- 객체에 조건부로 속성을 추가하는 법을 알아 두라.
