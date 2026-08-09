# Item 52: 오버로드 시그니처보다 조건부 타입 선호하기 (Prefer Conditional Types to Overload Signatures)

## 핵심 질문

입력 타입에 따라 반환 타입이 달라지는 함수는 무엇으로 타이핑해야 하는가? 오버로드는 어디서 실패하고 조건부 타입은 어떻게 그것을 해결하는가?

이 자바스크립트 함수의 타입 선언을 써 보자.

```javascript
function double(x) {
  return x + x;
}
```

`double`은 string이나 number를 받는다. **시도 ① - 유니온 타입**: 정확하지만 덜 정밀하다.

```typescript
declare function double(x: string | number): string | number;
const num = double(12);
//    ^? const num: string | number   - number여야 하는데
const str = double('x');
//    ^? const str: string | number   - string이어야 하는데
```

**시도 ② - 제네릭**: 정밀을 노리다 과녁을 지나쳤다.

```typescript
declare function double<T extends string | number>(x: T): T;
const num = double(12);
//    ^? const num: 12      - 12를 두 배 하면 24인데!
const str = double('x');
//    ^? const str: "x"     - 'x'를 두 배 하면 'xx'인데!
```

리터럴 타입이 그대로 반환 타입이 되어 버렸다 - 부정확한 타입이다(Item 40).

**시도 ③ - 오버로드 시그니처**: 진전이지만 미묘한 버그가 남는다.

```typescript
declare function double(x: number): number;
declare function double(x: string): string;

const num = double(12);   // number ✔
const str = double('x');  // string ✔

function f(x: string | number) {
  return double(x);
  //            ~ Argument of type 'string | number' is not assignable
  //              to parameter of type 'string'
}
```

이 `double(x)` 호출은 안전하고 `string|number`를 반환해야 한다. 오버로드는 **하나씩 순서대로 처리되며 일치하는 것을 찾는다** - 마지막(string) 오버로드에서 `string|number`가 string에 할당 불가라 실패한 것이다. 세 번째 오버로드를 추가할 수도 있지만 더 나은 해법이 있다.

## 1. 조건부 타입 - 타입 공간의 if 문

조건부 타입(*conditional type - `T extends U ? X : Y` 형태로, 타입 관계에 따라 분기하는 타입*)은 타입 공간의 조건문이다. 이런 경우에 안성맞춤이다.

```typescript
declare function double<T extends string | number>(
  x: T
): T extends string ? string : number;
```

자바스크립트의 삼항 연산자처럼 읽는다: T가 string의 서브타입이면(string·문자열 리터럴·리터럴 유니온·템플릿 리터럴 타입) 반환은 string, 아니면 number. 이 선언으로 모든 예제가 동작한다.

```typescript
const num = double(12);   // number ✔
const str = double('x');  // string ✔
function f(x: string | number) {
  return double(x);       // string | number ✔
}
```

유니온 예제가 동작하는 이유는 **조건부 타입이 유니온 위로 분배(distribute)** 되기 때문이다.

```
(string|number) extends string ? string : number
→ (string extends string ? string : number) |
  (number extends string ? string : number)
→ string | number
```

분배는 타입스크립트 타입 시스템의 설계다 - 꼭 이래야 했던 것은 아니지만, 이 경우처럼 많은 경우에 올바르고 극히 편리하다.

> **핵심 통찰**: 오버로드는 개별적으로 취급되지만, 조건부 타입은 타입 체커가 **하나의 표현식으로 분석하며 유니온 위로 분배**할 수 있다. 그래서 개별 케이스의 유니온으로 일반화된다 - 오버로드로 쓴 선언보다 조건부 타입 버전이 더 올바른 경우가 많다.

조건부 타입을 쓸 때마다 유니온 위로 분배되길 원하는지 생각하라. 보통은 원하지만 항상은 아니다 - 분배가 틀린 상황과 통제법은 Item 53에서.

## 2. 그래도 오버로드가 나은 경우

유니온 케이스가 있을 법하지 않거나, 함수가 정말로 완전히 다른 시그니처를 가진 둘 이상의 함수처럼 동작한다면, 유니온 처리에 공들일 가치가 없고 별도 오버로드가 더 읽기 좋을 수 있다. 다만 그 상황이라면 **아예 두 개의 다른 함수가 더 명확하지 않은지** 생각해 보라. Node 표준 라이브러리가 좋은 예다 - `readFile`의 콜백 버전과 프로미스 버전을 별도 함수로 제공한다. 인수에 따라 다르게 동작하는 단일 함수로 만들 수도 있었지만, 콜백을 쓸지 프로미스를 쓸지는 보통 미리 알기 때문에 두 함수가 더 명확하고 단순하다.

## 3. 구현 전략 - 단일 오버로드

타입 이야기만 했지만 구현도 짚어 두자. 오버로드된 함수나 조건부 타입을 반환하는 함수의 구현은 종종 어색하고 본문에 타입 단언이 필요하다 - **타입스크립트는 변수에 조건부 타입을 추론해 주지 않는다.** 한 전략은 **단일 오버로드**로 호출자용 시그니처와 구현용 시그니처를 분리하는 것이다.

```typescript
function double<T extends string | number>(
  x: T
): T extends string ? string : number;
function double(x: string | number): string | number {
  return typeof x === 'string' ? x + x : x + x;
}
```

외부에 보이는 API에는 조건부 타입을, 구현에는 더 단순한 타입을 쓴다. (typeof 체크가 이상해 보이지만 타입 단언을 아껴 준다.) 타입스크립트가 두 시그니처의 호환성을 어느 정도 검사하지만 완벽하지는 않으므로, 타입 테스트가 여전히 중요하다(Item 55).

## 기억해야 할 것들

- 오버로드된 타입 시그니처보다 조건부 타입을 선호하라. 유니온 위로 분배됨으로써 조건부 타입은 추가 오버로드 없이 유니온 타입을 지원하는 선언을 가능케 한다.
- 유니온 케이스가 있을 법하지 않다면, 함수를 다른 이름의 둘 이상의 함수로 나누는 것이 더 명확하지 않을지 고려하라.
- 조건부 타입으로 선언된 함수를 구현할 때는 단일 오버로드 전략을 고려하라.
