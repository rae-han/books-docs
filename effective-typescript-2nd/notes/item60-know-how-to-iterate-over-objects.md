# Item 60: 객체 순회하는 법 알기 (Know How to Iterate Over Objects)

## 핵심 질문

멀쩡히 실행되는 for-in 루프에 왜 타입 에러가 나는가? 객체를 순회하는 올바른 방법들은 무엇인가?

이 코드는 잘 실행되는데 타입스크립트는 에러를 낸다. 왜?

```typescript
const obj = {
  one: 'uno',
  two: 'dos',
  three: 'tres',
};
for (const k in obj) {
  //       ^? const k: string
  const v = obj[k];
  //        ~~~~~~ Element implicitly has an 'any' type
  //               because type ... has no index signature
}
```

`k`의 타입은 `string`인데, 인덱싱하려는 객체의 타입에는 특정 키 세 개(`'one'`·`'two'`·`'three'`)뿐이다. 그 셋 말고도 문자열은 많으니 실패할 수밖에 없다. 키에 타입 단언으로 더 좁은 타입을 주면 고쳐진다.

```typescript
for (const kStr in obj) {
  const k = kStr as keyof typeof obj;
  //    ^? const k: "one" | "two" | "three"
  const v = obj[k];  // OK
}
```

## 1. 왜 k는 string으로 추론되는가

진짜 질문은 이것이다 — 왜 `k`가 `"one" | "two" | "three"`가 아니라 `string`인가? 조금 다른 예를 보자.

```typescript
interface ABC {
  a: string;
  b: string;
  c: number;
}
function foo(abc: ABC) {
  for (const k in abc) {
    //       ^? const k: string
    const v = abc[k];
    //        ~~~~~~ Element implicitly has an 'any' type
    //               because type 'ABC' has no index signature
  }
}
```

같은 에러이고 같은 단언(`k as keyof ABC`)으로 "고칠" 수 있다. 하지만 이 경우 **타입스크립트의 항의가 옳다.**

```typescript
const x = {a: 'a', b: 'b', c: 2, d: new Date()};
foo(x);  // OK!
```

`foo`는 `ABC`에 할당 가능한 **아무** 값으로나 호출될 수 있다 — a·b·c만 가진 값이 아니라. 다른 속성이 더 있을 가능성이 얼마든지 있다(Item 4). 그래서 타입스크립트는 확신할 수 있는 유일한 타입인 `string`을 준다.

여기서 `keyof ABC` 단언에는 또 다른 함정이 있다.

```typescript
function foo(abc: ABC) {
  for (const kStr in abc) {
    let k = kStr as keyof ABC;
    //  ^? let k: keyof ABC ("a" | "b" | "c"와 동등)
    const v = abc[k];
    //    ^? const v: string | number
  }
}
```

k에게 `"a" | "b" | "c"`가 너무 좁다면 v에게 `string | number`는 확실히 너무 좁다 — 위 예에서 값 하나는 `Date`였고, 무엇이든 될 수 있다. 런타임 혼돈으로 이어질 수 있다. Item 9의 말대로 단언 앞에서는 긴장해야 한다 — 타입스크립트가 뭔가 알고 있을지 모른다.

타입스크립트가 for-in에서 string을 추론하는 또 하나의 이유는 **프로토타입 오염**(prototype pollution)이다 — `Object.prototype`에 정의된 속성이 모든 객체에 상속되는 보안 문제인데, 상속된 속성도 for-in에 열거되므로 string이 더 안전한 선택이다. (`Object.entries`는 상속된 속성을 제외한다.)

## 2. 상황별 올바른 방법

**추가 속성이 있을 수 있는 객체 — Object.entries.** 키와 값을 동시에 순회한다. 타입이 다루기 편하진 않아도 최소한 **정직**하다.

```typescript
function foo(abc: ABC) {
  for (const [k, v] of Object.entries(abc)) {
    //          ^? const k: string
    console.log(v);
    //          ^? const v: any
  }
}
```

**키를 정확히 알 때 — 명시적 키 목록.** 더 정밀한 타입을 얻는 안전한 방법은 관심 있는 키를 명시적으로 나열하는 것이다.

```typescript
function foo(abc: ABC) {
  const keys = ['a', 'b', 'c'] as const;
  for (const k of keys) {
    //         ^? const k: "a" | "b" | "c"
    const v = abc[k];
    //    ^? const v: string | number
  }
}
```

ABC의 모든 키를 커버하는 것이 목적이라면 keys 배열을 타입과 동기화할 방법이 필요하다(Item 61의 Record 기법 참고).

**불변으로 아는 객체 — for-in + 단언.** 처음 예제처럼 객체 리터럴을 바로 다루고 있어 키를 정확히 안다면 `as keyof typeof obj` 단언이 정당하다.

**Map — 애초에 함정이 없다.**

```typescript
const m = new Map([
  ['one', 'uno'],
  ['two', 'dos'],
  ['three', 'tres'],
]);
// ^? const m: Map<string, string>
for (const [k, v] of m.entries()) {
  //          ^? const k: string
  console.log(v);
  //          ^? const v: string
}
```

Map은 객체와 같은 구조적 동작이 없어서 순회가 쉽다 — 단언이나 any를 거치지 않고는 `Map<string, string>`에 number 값을 넣을 수 없다. 다만 데이터가 JSON이나 객체를 쓰도록 설계된 API에서 온다면 덜 편할 수 있다(객체 타입을 Map으로 바꿔 타입 안전성을 올리는 예는 Item 16).

## 기억해야 할 것들

- 함수가 매개변수로 받는 객체에는 추가 키가 있을 수 있음을 인지하라.
- 아무 객체의 키와 값을 순회할 때는 `Object.entries`를 사용하라.
- 키가 정확히 무엇인지 알 때는 명시적 타입 단언과 함께 for-in 루프를 사용하라.
- 순회하기 더 쉬운 Map을 객체의 대안으로 고려하라.
