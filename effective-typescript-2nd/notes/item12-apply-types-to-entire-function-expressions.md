# Item 12: 가능하면 함수 표현식 전체에 타입 적용하기 (Apply Types to Entire Function Expressions When Possible)

## 핵심 질문

매개변수와 반환 타입을 하나하나 쓰는 대신 함수 전체에 타입을 한 번에 적용하면 무엇이 좋아지는가?

자바스크립트(그리고 타입스크립트)는 함수 문장(statement)과 함수 표현식(expression)을 구분한다.

```typescript
function rollDice1(sides: number): number { /* ... */ }         // 문장
const rollDice2 = function(sides: number): number { /* ... */ }; // 표현식
const rollDice3 = (sides: number): number => { /* ... */ };      // 표현식
```

타입스크립트에서 함수 표현식의 장점은 매개변수 타입과 반환 타입을 따로따로 명시하는 대신 **함수 전체에 타입 선언을 한 번에 적용**할 수 있다는 것이다.

```typescript
type DiceRollFn = (sides: number) => number;
const rollDice: DiceRollFn = sides => { /* ... */ };
```

편집기에서 `sides`에 마우스를 올리면 타입스크립트가 이미 `number`로 알고 있다. 이렇게 짧은 예에서는 함수 타입의 가치가 크지 않지만, 이 기법은 여러 가능성을 열어 준다.

## 1. 반복 줄이기

숫자 산술 함수 여러 개를 쓴다면:

```typescript
function add(a: number, b: number) { return a + b; }
function sub(a: number, b: number) { return a - b; }
function mul(a: number, b: number) { return a * b; }
function div(a: number, b: number) { return a / b; }
```

반복되는 함수 시그니처를 함수 타입 하나로 통합할 수 있다.

```typescript
type BinaryFn = (a: number, b: number) => number;
const add: BinaryFn = (a, b) => a + b;
const sub: BinaryFn = (a, b) => a - b;
const mul: BinaryFn = (a, b) => a * b;
const div: BinaryFn = (a, b) => a / b;
```

타입 구문 개수가 줄었고 구현 로직과 분리되어 로직이 더 잘 드러난다. 덤으로 모든 함수 표현식의 반환 타입이 `number`인지 검사도 얻었다.

라이브러리들은 흔한 함수 시그니처의 타입을 종종 제공한다 — 예를 들어 React 타이핑의 `MouseEventHandler`는 매개변수에 `MouseEvent`를 쓰는 대신 함수 전체에 적용할 수 있다. 라이브러리 저자라면 흔한 콜백의 타입 선언을 제공하는 것을 고려하라.

## 2. 다른 함수의 시그니처 맞추기 — typeof fn

다른 함수의 시그니처와 일치시켜야 할 때도 함수 전체 타입이 유용하다. 브라우저의 `fetch`로 예를 들면:

```typescript
async function getQuote() {
  const response = await fetch('/quote?by=Mark+Twain');
  const quote = await response.json();
  return quote;
}
```

여기엔 버그가 있다 — `/quote` 요청이 실패하면 응답 본문에는 "404 Not Found" 같은 설명이 들어 있을 가능성이 높다. JSON이 아니므로 `response.json()`은 잘못된 JSON에 대한 메시지와 함께 거부된 프로미스를 반환하고, **진짜 에러였던 404를 가려 버린다**. `fetch`의 에러 응답이 거부된 프로미스가 되지 않는다는 사실은 잊기 쉽다.

상태 체크를 대신해 주는 `checkedFetch`를 만들자. `lib.dom.d.ts`의 `fetch` 타입 선언은 이렇다.

```typescript
declare function fetch(
  input: RequestInfo, init?: RequestInit,
): Promise<Response>;
```

따라서 이렇게 쓸 수 있다.

```typescript
async function checkedFetch(input: RequestInfo, init?: RequestInit) {
  const response = await fetch(input, init);
  if (!response.ok) {
    // async 함수에서 예외는 거부된 프로미스가 된다
    throw new Error(`Request failed: ${response.status}`);
  }
  return response;
}
```

동작하지만 더 간결하게 쓸 수 있다.

```typescript
const checkedFetch: typeof fetch = async (input, init) => {
  const response = await fetch(input, init);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response;
}
```

함수 문장을 함수 표현식으로 바꾸고 **함수 전체에 타입(`typeof fetch`)을 적용**했다. `input`과 `init`의 타입이 추론되고, 반환 타입이 `fetch`와 같다는 것까지 보장된다. 예를 들어 `throw` 대신 `return`을 썼다면 타입스크립트가 실수를 잡는다.

```typescript
const checkedFetch: typeof fetch = async (input, init) => {
  //  ~~~~~~~~~~~~
  //  'Promise<Response | HTTPError>' is not assignable to 'Promise<Response>'
  //    Type 'Response | HTTPError' is not assignable to type 'Response'
  const response = await fetch(input, init);
  if (!response.ok) {
    return new Error('Request failed: ' + response.status);
  }
  return response;
}
```

첫 번째(문장) 버전에서 같은 실수를 했다면 에러는 구현이 아니라 **`checkedFetch`를 호출하는 코드**에서 났을 것이다. 함수 전체에 타입을 적용한 덕에 더 간결해졌을 뿐 아니라 **더 안전**해졌다 — 에러가 발생 지점 가까이에서 잡힌다.

## 3. 매개변수만 맞추고 반환 타입은 바꾸기 — Parameters

다른 함수의 매개변수 타입은 그대로 쓰되 반환 타입을 바꾸고 싶다면? 나머지 매개변수와 내장 `Parameters` 유틸리티 타입으로 가능하다.

```typescript
async function fetchANumber(
  ...args: Parameters<typeof fetch>
): Promise<number> {
  const response = await checkedFetch(...args);
  const num = Number(await response.text());
  if (isNaN(num)) {
    throw new Error(`Response was not a number.`);
  }
  return num;
}

fetchANumber
// ^? function fetchANumber(
//      input: RequestInfo | URL, init?: RequestInit | undefined
//    ): Promise<number>
```

편집기에서 확인하면 `args`는 아예 보이지 않고 `fetch`의 매개변수 이름으로 대체되어 있다 — 정확히 원하던 것이다. 다만 문법이 함수 전체 타입보다 번잡하므로, 그냥 매개변수 타입을 풀어 쓰는 것이 나은지는 판단이 필요하다(제네릭 맥락의 나머지 매개변수는 Item 62).

## 4. 이미 매일 누리고 있는 혜택

의식하든 아니든, **콜백을 다른 함수에 넘길 때마다** 이 기법의 혜택을 받고 있다. 배열의 `map`이나 `filter`를 쓰면 타입스크립트가 콜백 매개변수의 타입을 추론해서 함수 표현식 전체에 적용해 준다(문맥을 통한 타입 추론은 Item 24).

> **핵심 통찰**: 핵심 단어는 "여럿"과 "반복"이다. 같은(또는 관련된) 시그니처의 함수가 여럿일 때 함수 타입을 쓰는 것이지, 모든 함수의 타입을 뽑아내라는 뜻이 아니다. 고유한 시그니처를 가진 단독 함수라면 구식 함수 문장으로 충분하다.

## 기억해야 할 것들

- 매개변수와 반환 타입 대신 함수 표현식 전체에 타입 구문을 적용하는 것을 고려하라.
- 같은 타입 시그니처를 반복해서 쓰고 있다면 함수 타입을 뽑아내거나 이미 있는 것을 찾아보라.
- 라이브러리 저자라면 흔한 콜백의 타입을 제공하라.
- 다른 함수의 시그니처를 맞출 때는 `typeof fn`을, 반환 타입을 바꿔야 할 때는 `Parameters`와 나머지 매개변수를 사용하라.
