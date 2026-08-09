# Item 24: 타입 추론에 문맥이 어떻게 쓰이는지 이해하기 (Understand How Context Is Used in Type Inference)

## 핵심 질문

인라인으로는 통과하던 코드가 변수로 뽑아내면 왜 에러가 되는가? 값과 그 사용 문맥이 분리될 때 무슨 일이 일어나는가?

타입스크립트는 값만이 아니라 **값이 놓인 문맥**도 고려해 타입을 추론한다. 보통은 잘 동작하지만 가끔 놀라움을 준다. 자바스크립트에서는 실행 순서만 안 바꾸면 표현식을 상수로 뽑아내도 동작이 같다.

```typescript
// 인라인 형태
setLanguage('JavaScript');
// 참조 형태
let language = 'JavaScript';
setLanguage(language);
```

매개변수가 `string`이면 타입스크립트에서도 이 리팩터링은 문제없다. 그런데 Item 35의 조언대로 더 정밀한 문자열 리터럴 유니온으로 바꾸면:

```typescript
type Language = 'JavaScript' | 'TypeScript' | 'Python';
function setLanguage(language: Language) { /* ... */ }

setLanguage('JavaScript');  // OK

let language = 'JavaScript';
setLanguage(language);
//          ~~~~~~~~ Argument of type 'string' is not assignable
//                   to parameter of type 'Language'
```

**인라인 형태**에서는 함수 선언으로부터 매개변수가 `Language` 타입이어야 함을 알고, 문자열 리터럴 `'JavaScript'`는 여기에 할당 가능하다. 하지만 **변수로 뽑아내면** 할당 시점에 타입을 추론해야 하고, 통상의 알고리즘(Item 20)에 따라 `string`이 되어 `Language`에 할당할 수 없다.

> **참고**: 변수의 최종 사용처를 보고 타입을 추론하는 언어도 있지만, 그것도 혼란스럽긴 마찬가지다. 타입스크립트를 만든 아네르스 하일스베르는 이를 "떨어져 있는 것들의 으스스한 상호작용(spooky action at a distance)"이라 부른다. 타입스크립트는 대체로 변수가 **처음 도입될 때** 타입을 결정한다(주목할 예외는 Item 25).

해법은 두 가지다.

**① 타입 구문으로 가능한 값을 제약** — 언어 이름에 오타(`'Typescript'`)가 있으면 잡아 주는 덤도 있다.

```typescript
let language: Language = 'JavaScript';
setLanguage(language);  // OK
```

**② 상수로 만들기** — 바뀔 수 없다고 알리면 더 정밀한 리터럴 타입 `"JavaScript"`가 추론된다.

```typescript
const language = 'JavaScript';
//    ^? const language: "JavaScript"
setLanguage(language);  // OK
```

근본 문제는 **값을 사용 문맥에서 분리**했다는 것이다. 괜찮을 때도 있지만 아닐 때가 많다. 문맥 상실이 에러를 낳는 나머지 사례들을 보자.

## 1. 튜플 타입

```typescript
// 매개변수는 (위도, 경도) 쌍이다.
function panTo(where: [number, number]) { /* ... */ }

panTo([10, 20]);  // OK

const loc = [10, 20];
//    ^? const loc: number[]
panTo(loc);
//    ~~~ Argument of type 'number[]' is not assignable to
//        parameter of type '[number, number]'
```

`loc`은 `number[]`(길이 미상의 숫자 배열)로 추론되어 튜플에 할당할 수 없다. 이미 `const`인데도 그렇다. 타입 구문으로 의도를 정확히 알리면 된다.

```typescript
const loc: [number, number] = [10, 20];
panTo(loc);  // OK
```

또 다른 방법은 const 문맥(Item 20)이다 — `const`의 얕은 상수가 아니라 **깊은 상수**를 의도한다고 알린다.

```typescript
const loc = [10, 20] as const;
//    ^? const loc: readonly [10, 20]
panTo(loc);
//    ~~~ The type 'readonly [10, 20]' is 'readonly'
//        and cannot be assigned to the mutable type '[number, number]'
```

이번엔 **너무 정밀**해졌다. `panTo`의 시그니처가 `where`를 수정하지 않는다는 약속을 하지 않아서 readonly 타입을 받을 수 없다. 최선은 `panTo`에 readonly 구문을 추가하는 것이다.

```typescript
function panTo(where: readonly [number, number]) { /* ... */ }
const loc = [10, 20] as const;
panTo(loc);  // OK
```

시그니처를 못 바꾸는 상황이면 타입 구문을 써야 한다. const 문맥의 아쉬운 단점도 알아 두자 — 정의에서 실수하면(튜플에 세 번째 요소 추가 등) 에러가 **정의가 아니라 호출부**에서 난다. 깊이 중첩된 객체가 정의에서 먼 곳에서 쓰인다면 특히 혼란스럽다. 그래서 인라인 형태나 타입 선언이 더 낫다.

```typescript
const loc = [10, 20, 30] as const;  // 진짜 에러는 여기인데
panTo(loc);
//    ~~~ Argument of type 'readonly [10, 20, 30]' is not assignable to
//        parameter of type 'readonly [number, number]'
//        Source has 3 element(s) but target allows only 2.
```

## 2. 객체

문자열 리터럴이나 튜플을 담은 큰 객체에서 상수를 뽑아낼 때도 같은 문제가 나온다.

```typescript
type Language = 'JavaScript' | 'TypeScript' | 'Python';
interface GovernedLanguage {
  language: Language;
  organization: string;
}
function complain(language: GovernedLanguage) { /* ... */ }

complain({ language: 'TypeScript', organization: 'Microsoft' });  // OK

const ts = {
  language: 'TypeScript',
  organization: 'Microsoft',
};
complain(ts);
//       ~~ Argument of type '{ language: string; organization: string; }'
//          is not assignable to parameter of type 'GovernedLanguage'
//          Types of property 'language' are incompatible
//          Type 'string' is not assignable to type 'Language'
```

`ts` 객체에서 `language`가 `string`으로 추론됐다. 해법은 앞과 같다 — 타입 구문(`const ts: GovernedLanguage = ...`), const 단언(`as const`), 또는 `satisfies` 연산자(Item 20).

## 3. 콜백

콜백을 다른 함수에 넘길 때 타입스크립트는 문맥으로 콜백 매개변수의 타입을 추론한다.

```typescript
function callWithRandomNumbers(fn: (n1: number, n2: number) => void) {
  fn(Math.random(), Math.random());
}

callWithRandomNumbers((a, b) => {
  //                   ^? (parameter) a: number
  console.log(a + b);
  //              ^? (parameter) b: number
});
```

콜백을 상수로 뽑아내면 그 문맥을 잃고 `noImplicitAny` 에러가 난다.

```typescript
const fn = (a, b) => {
  //        ~    ~ Parameter 'a' implicitly has an 'any' type
  console.log(a + b);
}
callWithRandomNumbers(fn);
```

해법은 매개변수에 타입 구문을 붙이거나, 가능하다면 함수 표현식 전체에 타입 선언을 적용하는 것이다(Item 12). 함수가 한 곳에서만 쓰인다면 인라인 형태를 선호하라 — 구문이 덜 필요하다.

```typescript
const fn = (a: number, b: number) => {
  console.log(a + b);
}
callWithRandomNumbers(fn);
```

## 기억해야 할 것들

- 타입 추론에서 문맥이 어떻게 쓰이는지 알아 두라.
- 변수를 뽑아냈더니 타입 에러가 생기면 타입 구문 추가를 고려하라.
- 변수가 정말 상수라면 const 단언(`as const`)을 써라. 단, 에러가 정의가 아니라 사용처에서 나타날 수 있다는 것을 알아 두라.
- 타입 구문의 필요를 줄이려면 실용적인 범위에서 값을 인라인하는 것을 선호하라.
