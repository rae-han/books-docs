# Item 53: 조건부 타입에서 유니온의 분배 통제하는 법 알기 (Know How to Control the Distribution of Unions over Conditional Types)

## 핵심 질문

조건부 타입은 언제 유니온 위로 분배되고, 어떻게 켜거나 끄는가? boolean과 never가 만드는 놀라움은 무엇인가?

Item 52에서 조건부 타입이 유니온 위로 분배되는 것이 `double` 함수 타이핑에 도움이 되는 것을 봤다. 분배는 대체로 원하는 동작이지만 항상은 아니다.

## 1. 분배를 끄고 싶을 때 - [T] 한 요소 튜플

첫 인수가 둘째보다 작은지 판정하는 `isLessThan`을 만들자. 날짜·숫자·문자열에 동작하되, 편의로 첫 인수가 Date면 둘째로 number(에포크 이후 밀리초)도 허용하고 싶다.

```typescript
type Comparable<T> =
  T extends Date ? Date | number:
  T extends number ? number :
  T extends string ? string :
  never;

declare function isLessThan<T>(a: T, b: Comparable<T>): boolean;

isLessThan(new Date(), new Date());  // OK
isLessThan(new Date(), Date.now());  // OK - Date/number 비교 허용
isLessThan(12, 23);                  // OK
isLessThan('A', 'B');                // OK
isLessThan(12, 'B');
//             ~~~ Argument of type 'string' is not assignable to
//                 parameter of type 'number'.
```

기대대로 허용/거부되는 것 같다. 그런데 이렇게 쓰인 `Comparable`은 유니온 위로 분배된다. 바람직한가? 아니다.

```typescript
let dateOrStr = Math.random() < 0.5 ? new Date() : 'A';
//  ^? let dateOrStr: Date | string
isLessThan(dateOrStr, 'B')  // OK로 통과하지만 에러여야 한다
```

둘째 매개변수는 두 가능성의 유니온이 아니라 **인터섹션**이어야 한다. `(Date | number) & string`은 never이므로 이 호출은 아예 허용되면 안 된다.

분배를 어떻게 막을까? **유니온은 조건이 순수 타입(`T extends ...`)일 때만 분배된다.** 그러니 표현식을 살짝 복잡하게 만들면 된다. 표준 방법은 T를 한 요소 튜플 `[T]`로 감싸는 것이다.

```typescript
type Comparable<T> =
  [T] extends [Date] ? Date | number:
  [T] extends [number] ? number :
  [T] extends [string] ? string :
  never;
```

`[A]`는 A가 B에 할당 가능할 때만 `[B]`에 할당 가능하므로 표면적으로는 동작이 안 바뀌어야 할 것 같다. 하지만 `[T]`는 순수 타입이 아니라서 유니온이 더 이상 분배되지 않고, 다른 유효한 호출들을 깨지 않으면서 원하는 에러를 얻는다.

```typescript
isLessThan(dateOrStr, 'B');
//                    ~~~ Argument of type 'string' is not assignable to
//                        parameter of type 'never'.
```

## 2. 분배를 켜고 싶을 때 - 형식만을 위한 조건 추가

상황이 반대일 때도 있다 - 분배가 안 되는 조건부 타입을 분배시키고 싶은 경우. 보통 제네릭 타입 구현 방식의 의도치 않은 결과다. 요소가 전부 T인 N-튜플을 만드는 `NTuple<T, N>`을 누산기로 구현해 보자.

```typescript
type NTuple<T, N extends number> = NTupleHelp<T, N, []>;

type NTupleHelp<T, N extends number, Acc extends T[]> =
  Acc['length'] extends N
    ? Acc
    : NTupleHelp<T, N, [T, ...Acc]>;
```

트릭은 튜플 타입의 `length`가 원하는 숫자와 일치할 때까지 요소를 추가하는 것이다(배열 타입의 `'length'` 조회는 number지만 **튜플 타입에서는 0·1·2 같은 정밀한 숫자 리터럴 타입**이 나온다). N이 숫자 하나면 기대대로 동작한다.

```typescript
type PairOfStrings = NTuple<string, 2>;
//   ^? type PairOfStrings = [string, string]
type TripleOfNumbers = NTuple<number, 3>;
//   ^? type TripleOfNumbers = [number, number, number]
```

하지만 N이 유니온이면:

```typescript
type PairOrTriple = NTuple<bigint, 2 | 3>;
//   ^? type PairOrTriple = [bigint, bigint]
```

`[bigint, bigint] | [bigint, bigint, bigint]`여야 한다. 직접 원인은 누산기가 pair가 되는 순간 `Acc['length'] extends 2 | 3`이 참이 되는 것이지만, 더 깊은 문제는 **조건부 타입이 유니온 위로 분배되지 않고 있다**는 것이다. 조건이 `Acc['length'] extends N`이라 분배에 필요한 순수 `N extends …` 형태로 시작하지 않기 때문이다. 가장 쉬운 수정은 **형식을 갖춘 조건부 타입 하나를 덧대는 것**이다.

```typescript
type NTuple<T, N extends number> =
  N extends number
    ? NTupleHelp<T, N, []>
    : never;
```

N은 number로 제약되어 있으니 이 조건은 항상 참이다(`N extends any`나 `N extends unknown`으로 써도 된다). 유일한 목적은 분배에 맞는 형태의 조건부 타입을 추가하는 것 - 그리고 동작한다!

```typescript
type PairOrTriple = NTuple<bigint, 2 | 3>;
//   ^? type PairOrTriple = [bigint, bigint] | [bigint, bigint, bigint]
```

`NTupleHelp`가 N=2와 N=3으로 각각 인스턴스화되고 결과가 유니온된 것이다. (누산기는 재귀 제네릭의 성능을 개선하는 흔한 기법이다 - Item 57.)

## 3. 놀라움 두 가지 - boolean과 never

**boolean**: true일 때 축하 메시지를 내는 제네릭.

```typescript
type CelebrateIfTrue<V> = V extends true ? 'Huzzah!' : never;

type Party = CelebrateIfTrue<true>;
//   ^? type Party = "Huzzah!"
type NoParty = CelebrateIfTrue<false>;
//   ^? type NoParty = never
type SurpriseParty = CelebrateIfTrue<boolean>;
//   ^? type SurpriseParty = "Huzzah!"   ?!
```

`boolean extends true`가 참일 리 없는데 마지막이 "Huzzah!"라니 놀랍다. 내부적으로 타입스크립트는 boolean을 유니온 `true | false`로 취급한다. 유니온이므로 분배된다.

```
CelebrateIfTrue<boolean>
= CelebrateIfTrue<true | false>
= CelebrateIfTrue<true> | CelebrateIfTrue<false>
= "Huzzah!" | never
= "Huzzah!"
```

원하는 동작이 아닐 것이다. 역시 한 요소 튜플로 분배를 막는다.

```typescript
type CelebrateIfTrue<V> = [V] extends [true] ? 'Huzzah!' : never;
type SurpriseParty = CelebrateIfTrue<boolean>;
//   ^? type SurpriseParty = never
```

**never**: 이 정의를 보면 `AllowIn<T>`는 항상 "Yes"나 "No"(혹은 그 유니온)일 것 같다.

```typescript
type AllowIn<T> = T extends {password: "open-sesame"} ? "Yes" : "No";

type N = AllowIn<never>;
//   ^? type N = never   ?!
```

조건의 어느 쪽도 never가 아닌데 왜? 역시 분배다. **타입스크립트는 never를 빈 유니온으로 취급**하고, 분배할 것이 없으면 빈 것이 돌아온다. `T`를 `T | never`(= T)로 바꿔 보면 이해가 된다.

```
AllowIn<T>
= AllowIn<T | never>
= AllowIn<T> | AllowIn<never>
= AllowIn<T> | never
= AllowIn<T>
```

`T|never`가 T와 같아야 하는 이상, 분배가 적용되는 한 **F를 어떻게 정의하든 `F<never>`는 never**여야 한다. 원치 않으면 역시 한 요소 튜플로 감싸면 된다.

> **핵심 통찰**: 유니온 위 분배는 조건부 타입의 가장 강력하고 유용한 능력이며 대개는 원하는 동작이다. 제네릭 타입을 쓸 때 분배를 원하는지 생각하고, **아무렇지 않아 보이는 리팩터링이 분배를 켜거나 끌 수 있음**을 인지하라.

## 기억해야 할 것들

- 조건부 타입에서 유니온이 분배되길 원하는지 생각하라.
- 조건을 추가하거나 조건을 한 요소 튜플로 감싸서 분배를 켜고 끄는 법을 알아 두라.
- boolean과 never 타입이 유니온으로 분배될 때의 놀라운 동작을 인지하라.
