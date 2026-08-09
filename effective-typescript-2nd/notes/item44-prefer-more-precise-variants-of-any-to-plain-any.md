# Item 44: 그냥 any보다 더 정밀한 any 변종 선호하기 (Prefer More Precise Variants of any to Plain any)

## 핵심 질문

any를 쓸 수밖에 없을 때도 `any[]`·`Record<string, any>`·`() => any`가 그냥 any보다 나은 이유는?

`any` 타입은 자바스크립트로 표현 가능한 **모든** 값을 아우른다. 광대한 도메인이다! 모든 숫자와 문자열은 물론 모든 배열·객체·정규식·함수·클래스·DOM 요소, 거기에 null과 undefined까지. any를 쓸 때는 자문하라 — **정말로 이것보다 구체적인 무언가를 생각하고 있지 않았나?** 정규식이나 함수가 넘어와도 괜찮은가?

답이 "아니오"인 경우가 많고, 그렇다면 더 구체적인 타입으로 타입 안전성을 일부 지킬 수 있다.

## 1. any[] — 배열이라는 것은 안다면

```typescript
function getLengthBad(array: any) {  // 이렇게 하지 말 것!
  return array.length;
}

function getLength(array: any[]) {   // 이쪽이 낫다
  return array.length;
}
```

`any[]` 버전이 세 가지 면에서 낫다.

1. 함수 본문의 `array.length` 참조가 타입 체크된다.
2. 반환 타입이 any 대신 `number`로 추론된다.
3. `getLength` 호출에서 매개변수가 배열인지 검사된다.

```typescript
getLengthBad(/123/);  // 에러 없음, undefined 반환
getLength(/123/);
//        ~~~~~
// Argument of type 'RegExp' is not assignable to parameter of type 'any[]'.

getLengthBad(null);   // 에러 없음, 런타임에 예외
getLength(null);
//        ~~~~
// Argument of type 'null' is not assignable to parameter of type 'any[]'.
```

배열의 배열을 기대하면 `any[][]`를 쓰면 된다.

## 2. Record<string, any> — 객체라는 것은 안다면

어떤 객체인지는 몰라도 객체라는 것은 안다면 `{[key: string]: any}` 또는 `Record<string, any>`:

```typescript
function hasAKeyThatEndsWithZ(o: Record<string, any>) {
  for (const key in o) {
    if (key.endsWith('z')) {
      console.log(key, o[key]);
      return true;
    }
  }
  return false;
}
```

이 상황에서는 모든 비원시 타입을 포함하는 `object` 타입을 쓸 수도 있다. 조금 다른 점은, 키 열거는 되지만 **값 접근은 안 된다**는 것이다.

```typescript
function hasAKeyThatEndsWithZ(o: object) {
  for (const key in o) {
    if (key.endsWith('z')) {
      console.log(key, o[key]);
      //               ~~~~~~ Element implicitly has an 'any' type
      //                      because type '{}' has no index signature
      return true;
    }
  }
  return false;
}
```

객체 타입의 순회는 타입스크립트에서 특히 까다롭다 — 우회법은 Item 60에서 자세히.

## 3. 함수 타입 — Function 대신 시그니처

함수 타입을 기대한다면 any를 피하라. 구체성의 수준에 따라 선택지가 있다.

```typescript
type Fn0 = () => any;                // 매개변수 없이 호출 가능한 아무 함수
type Fn1 = (arg: any) => any;        // 매개변수 1개
type FnN = (...args: any[]) => any;  // 매개변수 개수 무관 — "Function" 타입과 동일
```

전부 any보다 정밀하므로 any보다 낫다. 마지막 예에서 나머지 매개변수의 타입이 `any[]`인 것에 주목 — any도 동작하지만 덜 정밀하다.

```typescript
const numArgsBad = (...args: any) => args.length;
//    ^? const numArgsBad: (...args: any) => any
const numArgsBetter = (...args: any[]) => args.length;
//    ^? const numArgsBetter: (...args: any[]) => number
```

반환 타입이 다르다. 나머지 매개변수는 `any[]`의 아마 가장 흔한 용처일 것이다.

> **참고**: 배열이 필요한데 요소 타입은 무관하다면 `any[]` 대신 `unknown[]`을 쓸 수 있을지 살펴보라. 더 안전하므로 그쪽이 낫다(unknown은 Item 46).

## 기억해야 할 것들

- any를 쓸 때, 정말로 아무 자바스크립트 값이나 허용되는지 생각해 보라.
- 데이터를 더 정확하게 모델링한다면 `any[]`, `{[id: string]: any}`, `() => any`처럼 더 정밀한 형태의 any를 선호하라.
