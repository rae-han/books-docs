# Item 71: 모듈 보강으로 타입 개선하기 (Use Module Augmentation to Improve Types)

## 핵심 질문

`JSON.parse`가 any를 반환하는 역사적 유산을 내 프로젝트에서만이라도 고칠 수 있을까?

자바스크립트에 암시적 전역과 타입 강제 같은 "나쁜 부분들"이 있듯 타입스크립트에도 역사적 사마귀가 있다. 그중 하나가 **any를 반환하는 `JSON.parse`의 타입 선언**이다.

```typescript
declare let apiResponse: string;
const response = JSON.parse(apiResponse);
const cacheExpirationTime = response.lastModified + 3600;
//    ^? const cacheExpirationTime: any
```

response에 타입을 주지 않으면 any가 코드 곳곳으로 조용히 퍼진다(Item 5). `unknown`(Item 46)을 반환하는 편이 나을 텐데 왜 안 그럴까? unknown은 2018년 7월의 타입스크립트 3.0에서야 도입됐고, 그전에 이미 어마어마한 코드가 쓰여 있어서 `JSON.parse`의 반환 타입 변경은 극도로 파괴적이었을 것이다. 타입스크립트 팀은 실용주의에 양보했다 — 미래 코드가 약간 덜 안전해지는 대신 기존 코드는 깨지지 않는다.

## 1. 선언 병합으로 JSON.parse 고치기

하지만 타입스크립트 팀이 이 시그니처를 유지하기로 했다고 나도 그래야 하는 것은 아니다. Item 13에서 봤듯 인터페이스에는 타입 별칭에 없는 특수 능력이 있다 — **선언 병합**. `lib.es5.d.ts`의 선언은 이렇다.

```typescript
interface JSON {
  parse(
    text: string,
    reviver?: (this: any, key: string, value: any) => any
  ): any;
  // ...
}
declare var JSON: JSON;
```

내 프로젝트의 타입 선언 파일에 같은 이름의 인터페이스를 정의하면 타입스크립트가 라이브러리 선언과 병합한다.

```typescript
// declarations/safe-json.d.ts
interface JSON {
  parse(
    text: string,
    reviver?: (this: any, key: string, value: any) => any
  ): unknown;   // 반환 타입이 바뀌었다
}
```

결과는 함수 오버로드(Item 52)와 비슷하다. lib이 내 코드보다 먼저 로드되므로 **내 오버로드가 항상 이긴다.** 이제 `JSON.parse`가 unknown을 반환한다.

```typescript
const response = JSON.parse(apiResponse);
//    ^? const response: unknown
const cacheExpirationTime = response.lastModified + 3600;
//                          ~~~~~~~~ response is of type 'unknown'.
```

쓰려면 타입 단언이 필요한데, 정확히 원하던 것이다.

```typescript
interface ApiResponse {
  lastModified: number;
}
const response = JSON.parse(apiResponse) as ApiResponse;
const cacheExpirationTime = response.lastModified + 3600;  // OK
```

역시 any를 반환하는 fetch API의 `Response.prototype.json()`에도 비슷하게 할 수 있다.

```typescript
// declarations/safe-response.d.ts
interface Body {
  json(): Promise<unknown>;
}
```

## 2. 논쟁적인 개선도 가능 — Set(string) 금지하기

위 변경들은 명백한 승리였다. 내 코드에만 영향을 주는 변경이므로, 더 넓은 생태계에서는 결코 통과 못 할 **논쟁적인 변경**도 자유롭게 할 수 있다. 언어 명세상 `Set` 생성자는 문자열을 받을 수 있는데 결과가 기대와 다를 수 있다.

```javascript
> new Set('abc')
Set(3) { 'a', 'b', 'c' }
```

`'abc'` 하나가 든 집합을 의도했다면 버그가 된다. 어느 쪽이든 타입이 `Set<string>`이고 이것이 자바스크립트의 동작이라 타입스크립트는 이 실수를 잡아 줄 수 없다. 하지만 **내 코드에서 Set 생성자에 문자열을 넘기는 것을 금지하지 말라는 법은 없다.** `lib.es2015.iterable.d.ts`의 생성자 오버로드(`new <T>(iterable?: Iterable<T> | null): Set<T>`)를 "쳐내는(knock out)" 방법:

```typescript
// declarations/ban-set-string-constructor.d.ts:
interface SetConstructor {
  new (str: string): void;
}
```

이제 문자열로 Set을 만드는 것 자체는 타입 에러가 아니지만 **void가 반환**되므로 결과로 뭔가 하려는 순간 문제의 단서를 얻는다.

```typescript
const s = new Set('abc');
//    ^? const s: void
console.log(s.has('abc'));
//            ~~~ Property 'has' does not exist on type 'void'.
```

더 강한 힌트를 주려면 에러 메시지를 담은 문자열 리터럴 타입을 반환하게 하고 `@deprecated`(Item 68)로 취소선까지 씌울 수 있다.

```typescript
interface SetConstructor {
  /** @deprecated */
  new (str: string): 'Error! new Set(string) is banned.';
}

const s = new Set('abc');
//    ^? const s: "Error! new Set(string) is banned."
```

완벽한 해법은 아니다 — Set을 생성하는 시점에 타입 에러가 나는 것이 더 좋겠지만 타입스크립트에서는 불가능하고, 이 기법의 실전 적용은 대개 이런 모습이 된다.

## 3. 큰 힘에는 큰 책임 — 주의사항

1. **타입 체크에만 영향을 준다.** `JSON.parse`와 Set 생성자의 런타임 동작은 내 코드에서든 라이브러리 코드에서든 바뀌지 않는다.
2. **내장 타입을 더 엄격·정밀하게 만들거나 특정 구문을 금지하는 데** 쓰는 것이 최선이다. 런타임 현실을 반영하지 않는 선언을 추가하면 혼란스러운 상황이 된다 — 틀린 타입은 타입이 없는 것보다 나쁠 수 있다(Item 40).
3. Set 생성자는 void나 에러 문자열을 반환하게 해서 쳐냈지만, **이미 void를 반환하는 함수·메서드를 금지하는 데는** 이 수법이 잘 안 통한다.

선언 병합으로 내장 타입을 개선했지만, 같은 기법을 서드파티 @types와 번들된 타입 선언에도 쓸 수 있다. 내장 타입 개선 모음은 npm의 **ts-reset** 패키지에서 찾을 수 있다.

## 기억해야 할 것들

- 선언 병합으로 기존 API를 개선하거나 문제 있는 구문을 금지하라.
- void나 에러 문자열 반환으로 메서드를 "쳐내고" `@deprecated`로 표시하라.
- 오버로드는 타입 수준에만 적용된다는 것을 기억하라. 타입이 현실에서 벗어나게 하지 마라.
