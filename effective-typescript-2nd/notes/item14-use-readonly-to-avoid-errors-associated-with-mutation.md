# Item 14: readonly를 사용해 변경으로 인한 오류 방지하기 (Use readonly to Avoid Errors Associated with Mutation)

## 핵심 질문

의도치 않은 변경(mutation)이 낳는 버그를 타입 시스템으로 어떻게 막는가? `readonly`는 정확히 무엇을 막고, 무엇을 막지 못하는가?

삼각수(1, 1+2=3, 1+2+3=6, …)를 출력하는 코드가 있다.

```typescript
function printTriangles(n: number) {
  const nums = [];
  for (let i = 0; i < n; i++) {
    nums.push(i);
    console.log(arraySum(nums));
  }
}

> printTriangles(5);
0
1
2
3
4
```

기대한 숫자가 아니다! 문제는 `arraySum`의 구현에 있다.

```typescript
function arraySum(arr: number[]) {
  let sum = 0, num;
  while ((num = arr.pop()) !== undefined) {
    sum += num;
  }
  return sum;
}
```

합계는 계산하지만 **배열을 비우는 부수효과**가 있다. 자바스크립트 배열은 가변이므로 타입스크립트는 아무 불만이 없다. 문제는 `printTriangles`가 `arraySum`이 `nums`를 수정하지 않는다고 **가정**했다는 것이다.

변경(mutation)은 찾기 힘든 수많은 버그의 근본 원인이다. 자바스크립트의 기본값은 가변이지만, 타입스크립트의 `readonly` 한정자가 뜻밖의 변경을 잡고 방지하도록 도와준다. 참고로 자바스크립트 원시 값은 이미 불변이다 - string·number·boolean에는 값을 변경하는 메서드가 없다(`let` 변수를 다른 원시 값으로 재할당할 수는 있지만 원시 값 자체를 바꾸는 것은 아니다). 문제는 배열과 객체다.

## 1. readonly 속성과 Readonly<T>

객체 타입의 속성에 붙인 `readonly`는 그 속성으로의 할당을 막는다.

```typescript
interface PartlyMutableName {
  readonly first: string;
  last: string;
}
const jackie: PartlyMutableName = { first: 'Jacqueline', last: 'Kennedy' };
jackie.last = 'Onassis';  // OK
jackie.first = 'Jacky';
//     ~~~~~ Cannot assign to 'first' because it is a read-only property.
```

보통은 모든 속성의 할당을 막고 싶은데, 그 용도의 제네릭 유틸리티 타입 `Readonly<T>`가 있다.

```typescript
interface FullyMutableName {
  first: string;
  last: string;
}
type FullyImmutableName = Readonly<FullyMutableName>;
//   ^? type FullyImmutableName = {
//        readonly first: string;
//        readonly last: string;
//      }
```

함수가 객체 매개변수를 받고 수정하지 않는다면, 그 타입을 `Readonly`로 감싸서 호출자에게 알리고 구현에서 강제하는 것이 좋다.

## 2. 두 가지 중요한 함정

**함정 1 - 얕다(shallow)**: `const` 선언처럼, `readonly` 속성은 재할당은 안 되지만 **변경은 된다**.

```typescript
interface Outer {
  inner: {
    x: number;
  }
}
const obj: Readonly<Outer> = { inner: { x: 0 }};
obj.inner = { x: 1 };
//  ~~~~~ Cannot assign to 'inner' because it is a read-only property
obj.inner.x = 1;  // OK!
```

타입 별칭을 만들어 편집기로 확인하면 `inner`에는 `readonly`가 붙었지만 `x`에는 안 붙은 것이 보인다. 깊은(deep) readonly 타입에 대한 내장 지원은 없다. 제네릭으로 만들 수는 있지만 제대로 만들기 까다로우니 직접 만들지 말고 라이브러리를 쓰는 것이 좋다 - ts-essentials의 `DeepReadonly`가 한 구현이다.

**함정 2 - 속성에만 적용된다**: 기저 객체를 변경하는 **메서드**는 제거하지 못한다.

```typescript
const date: Readonly<Date> = new Date();
date.setFullYear(2037);  // OK - 하지만 date를 변경한다!
```

## 3. Array vs ReadonlyArray

클래스의 가변·불변 버전이 모두 필요하면 보통 직접 분리해야 한다. 표준 라이브러리의 훌륭한 예가 `Array`와 `ReadonlyArray` 인터페이스다.

```typescript
interface Array<T> {
  length: number;
  // (비변경 메서드) toString, join, …
  // (변경 메서드) pop, shift, …
  [n: number]: T;
}

interface ReadonlyArray<T> {
  readonly length: number;
  // (비변경 메서드) toString, join, …
  readonly [n: number]: T;
}
```

핵심 차이: `pop`·`shift` 같은 **변경 메서드가 `ReadonlyArray`에는 없고**, `length`와 인덱스 타입에 `readonly`가 붙어 배열 크기 변경과 요소 할당이 막힌다. 둘 다 워낙 흔해서 전용 문법이 있다 - `T[]`와 `readonly T[]`.

`T[]`가 `readonly T[]`보다 엄격히 더 많은 것을 할 수 있으므로, **`T[]`가 `readonly T[]`의 서브타입**이다(방향을 헷갈리기 쉽다 - Item 7을 기억하라). 즉 가변 배열을 readonly 배열에 할당할 수는 있지만 역은 안 된다.

```typescript
const a: number[] = [1, 2, 3];
const b: readonly number[] = a;   // OK
const c: number[] = b;
//    ~ Type 'readonly number[]' is 'readonly' and cannot be
//      assigned to the mutable type 'number[]'
```

당연한 규칙이다 - 타입 단언도 없이 `readonly`를 벗겨낼 수 있다면 한정자가 무슨 소용이겠는가.

## 4. 처음 예제 고치기

`printTriangles`가 `arraySum`의 변경을 막고 싶다면 readonly 뷰를 넘겨 보면 된다.

```typescript
console.log(arraySum(nums as readonly number[]));
//                   ~~~~~~~~~~~~~~~~~~~~~~~~~
// The type 'readonly number[]' is 'readonly' and cannot be
// assigned to the mutable type 'number[]'.
```

`nums` 자체는 여전히 `push`해야 하므로 readonly로 선언할 수 없고, `arraySum`이 변경하지 못하게만 하고 싶은 것이다. `arraySum`이 가변 배열을 받는다고 선언되어 있으니 타입 에러가 난다. 해법은 `arraySum`이 readonly 배열을 받게 하는 것 - 그러면 이번엔 구현 안에서 에러가 난다.

```typescript
function arraySum(arr: readonly number[]) {
  let sum = 0, num;
  while ((num = arr.pop()) !== undefined) {
    //             ~~~ 'pop' does not exist on type 'readonly number[]'
    sum += num;
  }
  return sum;
}
```

`pop`은 `Array`에는 있고 `ReadonlyArray`에는 없으니 당연한 에러다. 변경하지 않는 구현으로 고친다.

```typescript
function arraySum(arr: readonly number[]) {
  let sum = 0;
  for (const num of arr) {
    sum += num;
  }
  return sum;
}

> printTriangles(5)
0
1
3
6
10
```

## 5. readonly 매개변수 선언의 효과와 전염성

매개변수에 읽기 전용 타입(배열의 `readonly`, 객체 타입의 `Readonly`)을 주면 세 가지가 일어난다.

1. 타입스크립트가 함수 본문에서 매개변수가 변경되지 않는지 검사한다.
2. 호출자에게 함수가 매개변수를 변경하지 않는다고 광고한다.
3. 호출자가 readonly 배열이나 `Readonly` 객체를 넘길 수 있게 된다.

함수가 매개변수를 변경하지 않는다면 readonly로 선언하라. 단점은 거의 없다 - 더 넓은 타입 집합으로 호출할 수 있게 되고(Item 30), 부주의한 변경이 잡힌다. (readonly 매개변수도 **재할당**은 가능하다 - `const`가 아니라 `let`으로 선언된 변수 같은 것이다. 재할당은 호출자에게 보이지 않지만 변경은 보인다.)

문제는 매개변수를 readonly로 표시하지 않은 함수를 호출해야 할 때다. 그 함수가 변경을 하지 않고 내 통제 하에 있다면 readonly로 만들어라. **readonly는 전염되는 경향이 있다** - 한 함수에 붙이면 그 함수가 호출하는 함수들에도 붙여야 한다. 계약이 명확해지고 타입 안전성이 좋아지므로 좋은 일이다. 하지만 다른 라이브러리의 함수라면 타입 선언을 못 바꿀 수 있으니 타입 단언(`param as number[]`)을 쓰거나 타입 선언을 패치(Item 71)해야 한다.

> **핵심 통찰**: 자바스크립트에는 "명시하지 않는 한 함수는 매개변수를 변경하지 않는다"는 암묵적 가정이 있다. 하지만 이런 암묵적 이해는 타입 체크에서 문제를 일으킨다(Item 31, 33). 사람 독자에게도 tsc에게도, 명시적인 것이 낫다.

## 기억해야 할 것들

- 함수가 매개변수를 수정하지 않는다면 배열은 `readonly`, 객체 타입은 `Readonly`로 선언하라. 함수의 계약이 명확해지고 구현 안의 부주의한 변경이 방지된다.
- `readonly`와 `Readonly`는 얕으며, `Readonly`는 메서드가 아니라 속성에만 적용된다는 것을 이해하라.
- `readonly`로 변경 관련 오류를 방지하고, 코드에서 변경이 일어나는 지점을 찾아라.
- `const`와 `readonly`의 차이를 이해하라: 전자는 재할당을 막고, 후자는 변경을 막는다.
