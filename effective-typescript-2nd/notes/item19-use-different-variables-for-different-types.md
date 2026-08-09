# Item 19: 다른 타입에는 다른 변수 사용하기 (Use Different Variables for Different Types)

## 핵심 질문

자바스크립트에서는 변수를 다른 타입의 값으로 재사용해도 문제없는데, 타입스크립트에서는 왜 안 되는가?

자바스크립트에서는 변수 하나를 다른 목적, 다른 타입의 값으로 재사용하는 것이 문제가 안 된다.

```javascript
let productId = "12-34-56";
fetchProduct(productId);              // string을 기대
productId = 123456;
fetchProductBySerialNumber(productId);  // number를 기대
```

타입스크립트에서는 에러가 두 개 난다.

```typescript
let productId = "12-34-56";
fetchProduct(productId);
productId = 123456;
// ~~~~~~ Type 'number' is not assignable to type 'string'
fetchProductBySerialNumber(productId);
//                         ~~~~~~~~~
// Argument of type 'string' is not assignable to parameter of type 'number'
```

값 `"12-34-56"`을 보고 타입스크립트가 `productId`의 타입을 `string`으로 추론했고, string에 number를 할당할 수 없어서 에러다. 여기서 타입스크립트 변수에 대한 핵심 통찰이 나온다.

> **핵심 통찰**: **변수의 값은 바뀔 수 있지만 타입은 일반적으로 바뀌지 않는다.** 타입이 바뀌는 흔한 방식은 좁히기(Item 22)뿐인데, 이는 타입이 작아지는 것이지 새 값을 포함하도록 커지는 것이 아니다. (주목할 예외가 Item 25에 있지만, 예외이지 규칙이 아니다.)

## 1. 유니온으로 고칠 수는 있지만

타입이 바뀌지 않으려면 string과 number를 모두 아우를 만큼 넓어야 한다 — 유니온 타입 `string | number`의 정의 그 자체다.

```typescript
let productId: string | number = "12-34-56";
fetchProduct(productId);
productId = 123456;                     // OK
fetchProductBySerialNumber(productId);  // OK
```

에러는 사라진다. 흥미롭게도 타입스크립트는 첫 호출에서는 진짜 string이고 두 번째에서는 진짜 number라는 것을 할당에 근거해 알아낸다(유니온의 좁히기). 하지만 유니온 타입은 나중에 더 많은 문제를 만들 수 있다 — `string`이나 `number` 같은 단순 타입보다 다루기 어렵고, 보통 뭔가 하기 전에 무엇인지 체크해야 한다.

## 2. 더 나은 해법 — 새 변수

```typescript
const productId = "12-34-56";
fetchProduct(productId);

const serial = 123456;
fetchProductBySerialNumber(serial);  // OK
```

앞 버전의 두 `productId`는 의미적으로 서로 무관했다 — 변수를 재사용했다는 사실로만 이어져 있었을 뿐이다. 타입 체커에게 혼란스러웠고 사람 독자에게도 혼란스럽다. 변수 두 개 버전이 나은 이유는:

1. 무관한 두 개념(ID와 시리얼 번호)을 분리한다.
2. 더 구체적인 변수 이름을 쓸 수 있다.
3. 타입 추론이 좋아진다 — 타입 구문이 필요 없다.
4. 더 단순한 타입이 된다(`string | number` 대신 string과 number).
5. `let` 대신 `const`로 선언할 수 있다 — 사람도 타입 체커도 추론하기 쉬워진다.

이 장에서 반복해 등장할 일반 주제: **변경(mutation)은 타입 체커가 코드를 따라가기 어렵게 만든다.** 타입이 바뀌는 변수를 피하라. 다른 개념에 다른 이름을 쓰면 사람에게도 타입 체커에게도 코드가 명확해진다. `let`보다 `const`가 훨씬 많아야 한다.

## 3. 가려진(shadowed) 변수와 혼동하지 말 것

```typescript
const productId = "12-34-56";
fetchProduct(productId);
{
  const productId = 123456;  // OK
  fetchProductBySerialNumber(productId);  // OK
}
```

두 `productId`는 이름만 같을 뿐 서로 아무 관계가 없는 **별개의 변수**라 타입이 달라도 괜찮다. 타입스크립트는 혼동하지 않지만 사람 독자는 혼동할 수 있다. 일반적으로 다른 개념에는 다른 이름을 쓰는 것이 좋고, 많은 팀이 eslint의 `no-shadow` 같은 린터 룰로 이런 가림을 금지한다.

이 아이템은 스칼라 값에 집중했지만 객체에도 비슷한 고려가 적용된다(Item 21).

## 기억해야 할 것들

- 변수의 값은 바뀔 수 있지만 타입은 일반적으로 바뀌지 않는다.
- 사람 독자와 타입 체커 모두의 혼란을 피하려면, 다른 타입의 값에 변수를 재사용하지 마라.
