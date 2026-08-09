# Item 10: 객체 래퍼 타입 피하기 (Avoid Object Wrapper Types (String, Number, Boolean, Symbol, BigInt))

## 핵심 질문

원시 값에 메서드가 있는 것처럼 보이는 이유는 무엇인가? `string`과 `String`은 왜 다르고, 어느 쪽을 써야 하는가?

자바스크립트에는 객체 외에 일곱 가지 원시 값 타입이 있다: string, number, boolean, null, undefined, symbol(ES2015 추가), bigint(ES2020 추가). 원시 값은 **불변이고 메서드가 없다**는 점에서 객체와 구별된다.

## 1. 원시 값에 메서드가 있는 것처럼 보이는 이유

"문자열엔 메서드가 있잖아?"라고 반박할 수 있다.

```javascript
> 'primitive'.charAt(3)
'm'
```

하지만 보이는 게 전부가 아니다. string 원시 값에는 메서드가 없지만, 자바스크립트에는 메서드를 가진 `String` **객체 타입**이 따로 있고, 둘 사이를 자유롭게 변환한다. string 원시 값의 `charAt` 같은 메서드에 접근하면 자바스크립트는 **원시 값을 `String` 객체로 감싸고, 메서드를 호출한 뒤, 그 객체를 버린다**.

`String.prototype`을 몽키 패치(Item 47)해 보면 관찰할 수 있다.

```javascript
// 따라 하지 말 것!
const originalCharAt = String.prototype.charAt;
String.prototype.charAt = function(pos) {
  console.log(this, typeof this, pos);
  return originalCharAt.call(this, pos);
};
console.log('primitive'.charAt(3));
// [String: 'primitive'] object 3
// m
```

메서드 안의 `this`는 string 원시 값이 아니라 `String` 객체 래퍼다. `String` 객체를 직접 만들 수도 있고 가끔은 원시 값처럼 동작하지만, 항상 그렇지는 않다 - 예를 들어 `String` 객체는 오직 자기 자신하고만 같다.

```javascript
> "hello" === new String("hello")
false
> new String("hello") === new String("hello")
false
```

래퍼로의 암시적 변환은 자바스크립트의 기묘한 현상 하나를 설명해 준다 - **원시 값에 속성을 할당하면 사라진다**.

```javascript
> x = "hello"
> x.language = 'English'
'English'
> x.language
undefined
```

`x`가 `String` 인스턴스로 변환되고, `language` 속성은 그 인스턴스에 설정된 뒤, 속성을 가진 객체째로 버려진 것이다.

다른 원시 값에도 래퍼 타입이 있다: `Number`, `Boolean`, `Symbol`, `BigInt` (null과 undefined에는 없다). 래퍼 타입은 원시 값에 메서드를 제공하고 정적 메서드(`String.fromCharCode` 등)를 담기 위해 존재할 뿐, 직접 인스턴스화할 이유는 보통 없다.

## 2. 타입스크립트에서: string ⊂ String, 하지만 역은 아니다

타입스크립트는 원시 타입과 객체 래퍼 타입을 구별해 모델링한다 - `string`/`String`, `number`/`Number`, `boolean`/`Boolean`, `symbol`/`Symbol`, `bigint`/`BigInt`.

자바나 C#에서 온 개발자는 무심코 `String`이라고 쓰기 쉽고, 처음에는 동작하는 것처럼 보이기까지 한다.

```typescript
function getStringLen(foo: String) {
  return foo.length;
}
getStringLen("hello");             // OK
getStringLen(new String("hello")); // OK
```

하지만 `String` 객체를 `string`을 기대하는 메서드에 넘기면 어긋난다.

```typescript
function isGreeting(phrase: String) {
  return ['hello', 'good day'].includes(phrase);
  //                                    ~~~~~~
  // Argument of type 'String' is not assignable to parameter of type 'string'.
  // 'string' is a primitive, but 'String' is a wrapper object.
  // Prefer using 'string' when possible.
}
```

**`string`은 `String`에 할당 가능하지만 `String`은 `string`에 할당할 수 없다.** 헷갈리면 에러 메시지의 조언을 따라 `string`만 쓰면 된다. 타입스크립트에 포함된 타입 선언 전부와 거의 모든 라이브러리의 타이핑이 `string`을 쓴다.

대문자 타입 구문으로도 래퍼 타입을 만나게 될 수 있다.

```typescript
const s: String = "primitive";
const n: Number = 12;
const b: Boolean = true;
```

이것은 타입스크립트 타입만 바꿀 뿐이고, Item 3에서 봤듯 런타임 값에는 영향을 주지 못한다 - 값은 여전히 원시 값이다. 원시 타입이 래퍼에 할당 가능하므로 타입스크립트가 허용은 하지만, 오해를 부르는 데다 불필요하다(Item 18). 원시 타입을 쓰는 것이 낫다.

## 3. 예외 - BigInt와 Symbol 호출

`BigInt`와 `Symbol`은 `new` 없이 **호출**하는 것은 괜찮다. 원시 값을 만들기 때문이다.

```javascript
> typeof BigInt(1234)
'bigint'
> typeof Symbol('sym')
'symbol'
```

이것들은 `BigInt`·`Symbol` **값**이지 타입스크립트 타입이 아니다(Item 8). 호출 결과는 `bigint`·`symbol` 타입의 값이다. bigint는 숫자 리터럴 끝에 `n`을 붙여 직접 만들 수도 있다: `123n`.

> **실무 팁**: typescript-eslint를 쓴다면 `ban-types` 룰이 객체 래퍼 타입 사용을 금지해 준다 (`@typescript-eslint/recommended` 설정에 포함).

## 기억해야 할 것들

- 타입스크립트의 객체 래퍼 타입을 피하라. 대신 원시 타입을 써라: `String` 대신 `string`, `Number` 대신 `number`, `Boolean` 대신 `boolean`, `Symbol` 대신 `symbol`, `BigInt` 대신 `bigint`.
- 객체 래퍼 타입이 원시 값에 메서드를 제공하는 방식을 이해하라. `Symbol`·`BigInt` 호출을 제외하면, 래퍼를 인스턴스화하거나 직접 사용하는 것을 피하라.
