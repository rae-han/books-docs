# Item 68: API 주석에 TSDoc 사용하기 (Use TSDoc for API Comments)

## 핵심 질문

같은 내용의 주석인데 왜 어떤 것은 편집기 툴팁에 뜨고 어떤 것은 안 뜨는가?

인사말을 만드는 함수에 저자가 친절하게 주석을 달았다.

```typescript
// Generate a greeting. Result is formatted for display.
function greet(name: string, title: string) {
  return `Hello ${title} ${name}`;
}
```

하지만 함수 **사용자**가 읽을 문서라면 JSDoc 스타일 주석이 낫다.

```typescript
/** Generate a greeting. Result is formatted for display. */
function greetJSDoc(name: string, title: string) {
  return `Hello ${title} ${name}`;
}
```

이유: 함수를 호출할 때 JSDoc 스타일 주석을 **툴팁으로 띄워 주는** 거의 보편적인 편집기 관례가 있기 때문이다. 인라인 주석(`//`)은 그런 대접을 받지 못한다. 타입스크립트 언어 서비스가 이 관례를 지원하니 활용해야 한다. **공개 API를 설명하는 주석이라면 JSDoc이어야 한다.** 타입스크립트 맥락에서 이 주석을 TSDoc이라 부르기도 한다.

## 1. @param, @returns, 타입 정의

`@param`·`@returns` 같은 익숙한 관례를 쓸 수 있다.

```typescript
/**
 * Generate a greeting.
 * @param name Name of the person to greet
 * @param title The person's title
 * @returns A greeting formatted for human consumption.
 */
function greetFullTSDoc(name: string, title: string) {
  return `Hello ${title} ${name}`;
}
```

이렇게 하면 함수 호출을 입력하는 동안 편집기가 **현재 매개변수에 해당하는 문서**를 보여 준다. 타입 정의에도 쓸 수 있다.

```typescript
/** A measurement performed at a time and place. */
interface Measurement {
  /** Where was the measurement made? */
  position: Vector3D;
  /** When was the measurement made? In seconds since epoch. */
  time: number;
  /** Observed momentum */
  momentum: Vector3D;
}
```

`Measurement` 객체의 개별 필드를 들여다볼 때 문맥에 맞는 문서가 뜬다. 필드별 문서는 **동형(homomorphic) 매핑된 타입을 통과할 때도 따라간다**(Item 15) — `Partial`·`Pick` 같은 헬퍼 타입에도 포함된다. 제네릭 타입의 타입 매개변수는 `@template` 태그로 문서화한다(Item 50).

## 2. 마크다운, 그리고 하지 말 것

TSDoc 주석은 **마크다운으로 서식**이 지정되므로 볼드·이탤릭·불릿 리스트를 쓸 수 있다. 다만 문서로 에세이를 쓰지는 말 것 — 최고의 주석은 짧고 요점만 담는다.

JSDoc에는 타입 정보를 지정하는 관례(`@param {string} name ...`)가 있지만 **피해야 한다** — 타입스크립트 타입이 있다(Item 31).

## 3. @deprecated

폐기된 심벌은 `@deprecated` 태그로 표시하라. 폐기 사실을 분명히 알릴 뿐 아니라 TSDoc의 가장 공격적인 기능을 켠다 — **@deprecated 심벌은 보통 취소선으로 렌더링된다.** 심벌을 들여다보지 않아도 폐기됐음을 알 수 있다.

> **실무 팁**: 메서드를 폐기 표시할 때는 사용자를 위해 **새 대안이 무엇인지** 함께 알려라. 최소한 폐기에 관한 문서 링크라도 포함하라.

## 기억해야 할 것들

- export되는 함수·클래스·타입의 문서화에 JSDoc/TSDoc 형식 주석을 사용하라. 편집기가 사용자에게 가장 적절한 순간에 정보를 띄워 준다.
- `@param`·`@returns`·마크다운 서식을 사용하라.
- 문서에 타입 정보를 넣지 마라(Item 31).
- 폐기된 API는 `@deprecated`로 표시하라.
