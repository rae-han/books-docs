# Item 22: 타입 좁히기 이해하기 (Understand Type Narrowing)

## 핵심 질문

타입스크립트는 어떤 코드를 보고 타입을 좁히는가? 좁혀지지 않는 경우와 잘못 좁히는 시도는 어떤 것인가?

좁히기(*narrowing - 넓은 타입에서 더 구체적인 타입으로 가는 과정. refinement(정제)라고도 함*)의 가장 흔한 예는 null 체크다.

```typescript
const elem = document.getElementById('what-time-is-it');
//    ^? const elem: HTMLElement | null
if (elem) {
  elem.innerHTML = 'Party Time'.blink();
  // ^? const elem: HTMLElement
} else {
  elem
  // ^? const elem: null
  alert('No element #what-time-is-it');
}
```

`elem`이 null이면 첫 분기는 실행되지 않으므로, 타입스크립트는 이 블록 안에서 유니온 타입에서 null을 제외할 수 있다. 컴파일러가 코드의 실행 경로를 따라가기 때문에 이를 제어 흐름 분석(*control flow analysis - 코드의 실행 경로를 따라 각 위치에서의 타입을 계산하는 것*)이라고도 한다.

주목할 점: 같은 심벌 `elem`이 코드의 **위치마다 다른 정적 타입**을 갖는다. 프로그래밍 언어 중에서는 다소 특이한 능력이다 — C++·자바·러스트에서 변수는 평생 하나의 타입을 가지며, 좁히려면 새 변수를 만들어야 한다. 타입스크립트에서 심벌은 **위치에서의 타입**을 갖는다. 이를 활용할 줄 알면 더 간결하고 관용적인 타입스크립트를 쓰게 된다.

## 1. 타입을 좁히는 여러 방법

**분기에서 throw/return** — 블록의 나머지에서 타입이 좁혀진다.

```typescript
const elem = document.getElementById('what-time-is-it');
if (!elem) throw new Error('Unable to find #what-time-is-it');
elem.innerHTML = 'Party Time'.blink();
// ^? const elem: HTMLElement
```

**instanceof**

```typescript
function contains(text: string, search: string | RegExp) {
  if (search instanceof RegExp) {
    return !!search.exec(text);
    //       ^? (parameter) search: RegExp
  }
  return text.includes(search);
  //                   ^? (parameter) search: string
}
```

**속성 체크(`in`)**

```typescript
interface Apple { isGoodForBaking: boolean; }
interface Orange { numSlices: number; }
function pickFruit(fruit: Apple | Orange) {
  if ('isGoodForBaking' in fruit) {
    fruit
    // ^? (parameter) fruit: Apple
  } else {
    fruit
    // ^? (parameter) fruit: Orange
  }
}
```

**일부 내장 함수** — `Array.isArray` 등.

```typescript
function contains(text: string, terms: string | string[]) {
  const termList = Array.isArray(terms) ? terms : [terms];
  //    ^? const termList: string[]
}
```

## 2. 잘못된 좁히기 시도 — 타입스크립트가 맞을 때

타입스크립트는 조건문을 통한 타입 추적에 꽤 능하다. 타입 단언을 추가하기 전에 다시 생각하라 — 타입스크립트가 내가 놓친 것을 알고 있을 수 있다! 유니온에서 null을 제외하는 **잘못된** 방법:

```typescript
const elem = document.getElementById('what-time-is-it');
if (typeof elem === 'object') {
  elem;
  // ^? const elem: HTMLElement | null
}
```

자바스크립트에서 `typeof null`이 `"object"`이므로 이 체크로는 null이 제외되지 않는다! falsy 원시 값에서도 비슷한 놀라움이 있다.

```typescript
function maybeLogX(x?: number | string | null) {
  if (!x) {
    console.log(x);
    //          ^? (parameter) x: string | number | null | undefined
  }
}
```

빈 문자열과 0도 falsy이므로 그 분기에서 x는 여전히 string이나 number일 수 있다. 타입스크립트가 옳다!

## 3. 태그된 유니온과 사용자 정의 타입 가드

타입 체커의 좁히기를 돕는 흔한 방법이 명시적 "태그"다.

```typescript
interface UploadEvent { type: 'upload'; filename: string; contents: string }
interface DownloadEvent { type: 'download'; filename: string; }
type AppEvent = UploadEvent | DownloadEvent;

function handleEvent(e: AppEvent) {
  switch (e.type) {
    case 'download':
      console.log('Download', e.filename);
      //                      ^? (parameter) e: DownloadEvent
      break;
    case 'upload':
      console.log('Upload', e.filename, e.contents.length, 'bytes');
      //                    ^? (parameter) e: UploadEvent
      break;
  }
}
```

태그된 유니온(판별 유니온)은 타입스크립트 어디에나 있다(Chapter 4에서 재론). switch를 쓸 때는 모든 가능성을 다뤘는지 테스트하는 것이 좋다 — 방법은 Item 59.

타입스크립트가 타입을 알아내지 못하면 도와주는 특수 함수를 도입할 수 있다.

```typescript
function isInputElement(el: Element): el is HTMLInputElement {
  return 'value' in el;
}

function getElementContent(el: HTMLElement) {
  if (isInputElement(el)) {
    return el.value;
    //     ^? (parameter) el: HTMLInputElement
  }
  return el.textContent;
  //     ^? (parameter) el: HTMLElement
}
```

사용자 정의 타입 가드(*user-defined type guard - 반환 타입이 타입 서술어인 함수*)라고 하며, `el is HTMLInputElement` 부분이 타입 서술어(*type predicate - 함수가 true를 반환하면 매개변수의 타입을 좁혀도 된다고 알리는 반환 타입*)다. 배열의 `filter`처럼 타입 가드로 배열·객체 안의 타입을 좁힐 수 있는 함수들도 있다.

```typescript
const formEls = document.querySelectorAll('.my-form *');
const formInputEls = [...formEls].filter(isInputElement);
//    ^? const formInputEls: HTMLInputElement[]
```

**주의**: 사용자 정의 타입 가드는 타입 단언(`el as HTMLInputElement`)보다 안전하지 않다 — 가드의 본문이 반환하는 타입 서술어와 일치하는지 검사해 주는 것은 아무것도 없다. (실제로 위 예에서도 `value` 속성이 있으면서 `HTMLInputElement`가 아닌 Element가 몇 있다.)

## 4. 코드를 살짝 고쳐 타입스크립트를 돕기

Map을 쓰는 이 코드는 올바르지만 타입 에러가 난다.

```typescript
const nameToNickname = new Map<string, string>();
declare let yourName: string;
let nameToUse: string;
if (nameToNickname.has(yourName)) {
  nameToUse = nameToNickname.get(yourName);
  // ~~~~~~ Type 'string | undefined' is not assignable to type 'string'
} else {
  nameToUse = yourName;
}
```

타입스크립트는 Map의 `has`와 `get`의 관계를 이해하지 못한다 — `has` 체크가 이후 `get`의 undefined 가능성을 제거한다는 것을 모른다. 살짝 고치면 에러가 사라진다(동작도 그대로).

```typescript
const nickname = nameToNickname.get(yourName);
let nameToUse: string;
if (nickname !== undefined) {
  nameToUse = nickname;
} else {
  nameToUse = yourName;
}
```

이 패턴은 흔하며 널 병합 연산자 `??`로 더 간결하게 쓸 수 있다.

```typescript
const nameToUse = nameToNickname.get(yourName) ?? yourName;
```

조건문에서 타입 체커와 싸우고 있다면, 타입스크립트가 따라올 수 있게 코드를 고칠 수 없는지 생각해 보라.

## 5. 좁혀지지 않는 경우 — 콜백

타입이 **좁혀지지 않는** 때를 아는 것도 중요하다. 대표적으로 콜백 안:

```typescript
function logLaterIfNumber(obj: { value: string | number }) {
  if (typeof obj.value === "number") {
    setTimeout(() => console.log(obj.value.toFixed()));
    //                           ~~~~~~~~~
    // Property 'toFixed' does not exist on type 'string | number'.
  }
}
```

`typeof` 체크로 좁혔는데 왜 유니온으로 되돌아갔을까? 호출 코드가 이럴 수 있기 때문이다.

```typescript
const obj: { value: string | number } = { value: 123 };
logLaterIfNumber(obj);
obj.value = 'Cookie Monster';
```

콜백이 실행될 시점에는 `obj.value`의 타입이 바뀌어 좁히기가 무효가 된다. 이 코드는 런타임에 예외를 던지며, 타입스크립트의 경고가 옳다.

> **핵심 통찰**: 타입이 어떻게 좁혀지는지 이해하면 타입 추론의 직관이 생기고 에러의 의미가 읽히며, 타입 체커와 생산적인 관계를 맺게 된다.

## 기억해야 할 것들

- 타입스크립트가 조건문 등 제어 흐름에 근거해 타입을 좁히는 방식을 이해하라.
- 태그된/판별 유니온과 사용자 정의 타입 가드로 좁히기 과정을 도와라.
- 타입스크립트가 더 쉽게 따라오도록 코드를 리팩터링할 수 있는지 생각해 보라.
