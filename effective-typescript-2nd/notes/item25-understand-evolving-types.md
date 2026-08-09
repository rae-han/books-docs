# Item 25: 진화하는 타입 이해하기 (Understand Evolving Types)

## 핵심 질문

`const nums = []`로 시작한 배열이 어떻게 `number[]`가 되는가? "변수의 타입은 선언 시 결정된다"는 규칙의 유일한 예외는 무엇인가?

타입스크립트에서 변수의 타입은 일반적으로 선언될 때 결정된다. 이후 좁혀질 수는 있어도(Item 22) 새 값을 포함하도록 **확장**될 수는 없다. 그런데 주목할 만한 예외가 하나 있다 - 진화하는 타입(*evolving type - null·undefined·[]로 초기화된 변수의 타입이 이후의 할당·push에 따라 확장되는 것*)이다.

## 1. 진화하는 배열

숫자 범위를 만드는 함수를 타입스크립트로 옮기면 기대대로 동작한다.

```typescript
function range(start: number, limit: number) {
  const nums = [];
  for (let i = start; i < limit; i++) {
    nums.push(i);
  }
  return nums;
  // ^? const nums: number[]
}
```

자세히 보면 놀랍다 - `[]`로 초기화된 `nums`가 어떻게 `number[]`가 됐을까? 리터럴에서 타입을 끌어내는 통상의 규칙(Item 20)이 아니다. 세 위치에서 타입을 확인해 보면 이야기가 보인다.

```typescript
function range(start: number, limit: number) {
  const nums = [];
  //    ^? const nums: any[]
  for (let i = start; i < limit; i++) {
    nums.push(i);
    // ^? const nums: any[]
  }
  return nums;
  // ^? const nums: number[]
}
```

`nums`의 타입은 미분화 배열 `any[]`로 시작하지만, number 값들을 push한 뒤에는 `number[]`로 **진화**한다. 좁히기(정제)와는 다른 현상이다 - 빈 배열의 타입은 다른 요소를 push하면 **확장**된다.

```typescript
const result = [];
//    ^? const result: any[]
result.push('a');
result
// ^? const result: string[]
result.push(1);
result
// ^? const result: (string | number)[]
```

조건문에서는 분기마다 타입이 다를 수도 있다. 배열이 아닌 단순 값으로도 같은 동작을 볼 수 있다.

```typescript
let value;
// ^? let value: any
if (Math.random() < 0.5) {
  value = /hello/;
  value
  // ^? let value: RegExp
} else {
  value = 12;
  value
  // ^? let value: number
}
value
// ^? let value: number | RegExp
```

> **참고**: 편집기에서는 헷갈릴 수 있다 - 타입은 할당하거나 push한 **다음에야** 진화하므로, 할당이 있는 줄에서 확인하면 여전히 `any`/`any[]`로 보인다.

이 구문은 타입 구문의 필요를 줄이는 편리한 수단이다. "evolving any"라고도 부르는데, 변수가 암시적 `any` 타입을 갖긴 하지만 위험한 `any`는 아니다(뒤에 설명). "evolving let"·"evolving arrays"라고도 한다.

## 2. null/undefined 초기화도 진화한다

변수를 처음에 `null`이나 `undefined`로 설정하는 경우에도 진화가 발동한다. try/catch에서 값을 설정할 때 흔히 나온다.

```typescript
let value = null;
// ^? let value: any
try {
  value = doSomethingRiskyAndReturnANumber();
  value
  // ^? let value: number
} catch (e) {
  console.warn('alas!');
}
value
// ^? let value: number | null
```

## 3. 안전장치 - 쓰기 전에 읽으면 에러

진화하는 타입을 값을 설정하거나 push하기 **전에** 사용하려 하면 암시적 any 에러가 난다.

```typescript
function range(start: number, limit: number) {
  const nums = [];
  //    ~~~~ Variable 'nums' implicitly has type 'any[]' in some
  //         locations where its type cannot be determined
  if (start === limit) {
    return nums;
    //     ~~~~ Variable 'nums' implicitly has an 'any[]' type
  }
  for (let i = start; i < limit; i++) {
    nums.push(i);
  }
  return nums;
}
```

바꿔 말해 진화하는 타입은 **쓸 때만 any**다. 아직 any인 상태에서 읽으려 하면 에러가 난다. Item 5가 경고한 무서운 `any`가 아니다 - 다른 `any`처럼 애플리케이션 전체로 퍼지지 않는다.

또 하나의 제약: **암시적 any 타입은 함수 호출을 통해서는 진화하지 않는다.** 화살표 함수가 추론을 걸어 넘어뜨린다.

```typescript
function makeSquares(start: number, limit: number) {
  const nums = [];
  //    ~~~~ Variable 'nums' implicitly has type 'any[]' in some locations
  range(start, limit).forEach(i => {
    nums.push(i * i);
  });
  return nums;
  //     ~~~~ Variable 'nums' implicitly has an 'any[]' type
}
```

타입 추론 개선은 타입스크립트에서 `forEach` 루프보다 for-of 루프를 선호할 좋은 이유다. 다만 이 경우에는 배열의 `map` 메서드로 한 문장으로 변환해서 순회와 진화하는 타입 자체를 피하는 것이 더 낫다(함수형 구문과 타입 흐름은 Item 26).

## 4. 통상적인 주의사항은 그대로

진화하는 타입에도 타입 추론의 일반적 주의사항이 따른다. 내 배열의 올바른 타입이 정말 `(string|number)[]`인가? 아니면 `number[]`여야 하는데 string을 잘못 push한 것인가? 더 나은 에러 체크를 위해 진화하는 타입 대신 명시적 타입 구문을 쓰거나, 최소한 함수의 반환 타입이라도 명시해서 구현 오류가 타입 시그니처로 새어 나가지 않게 하는 것(Item 18)을 여전히 고려할 만하다.

## 기억해야 할 것들

- 타입스크립트의 타입은 보통 정제되기만 하지만, `null`·`undefined`·`[]`로 초기화된 값의 타입은 진화할 수 있다.
- 이 구문이 나타나는 곳을 인식하고 이해하며, 내 코드에서 타입 구문의 필요를 줄이는 데 활용하라.
- 더 나은 에러 체크를 위해서는 진화하는 타입 대신 명시적 타입 구문을 고려하라.
