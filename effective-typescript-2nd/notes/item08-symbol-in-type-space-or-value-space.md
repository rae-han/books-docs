# Item 8: 심벌이 타입 공간에 있는지 값 공간에 있는지 구별하기 (Know How to Tell Whether a Symbol Is in the Type Space or Value Space)

## 핵심 질문

같은 이름이 타입을 가리킬 때와 값을 가리킬 때를 어떻게 구별하는가? `typeof`·`extends`·`in` 같은 키워드가 문맥에 따라 다른 뜻이 되는 이유는?

타입스크립트의 심벌은 두 공간 중 하나에 존재한다: **타입 공간(type space)** 과 **값 공간(value space)**. 혼란스러운 것은 **같은 이름이 공간에 따라 다른 것을 가리킬 수 있다**는 점이다.

## 1. 같은 이름, 두 공간

```typescript
interface Cylinder {
  radius: number;
  height: number;
}
const Cylinder = (radius: number, height: number) => ({radius, height});
```

`interface Cylinder`는 타입 공간에, `const Cylinder`는 값 공간에 같은 이름의 심벌을 도입한다. **둘은 서로 아무 관련이 없다.** 문맥에 따라 `Cylinder`는 타입일 수도 값일 수도 있고, 이것이 에러를 낳는다.

```typescript
function calculateVolume(shape: unknown) {
  if (shape instanceof Cylinder) {
    shape.radius
    //    ~~~~~~ Property 'radius' does not exist on type '{}'
  }
}
```

의도는 `shape`가 `Cylinder` **타입**인지 검사하는 것이었겠지만, `instanceof`는 자바스크립트의 런타임 연산자라 **값**에 작용한다. 그래서 `instanceof Cylinder`는 타입이 아니라 함수(값)를 가리킨다.

## 2. 어느 공간인지 구별하는 법

한눈에 알기 어려울 때는 심벌이 등장하는 **문맥**으로 판단해야 한다. 타입 공간의 구문 다수가 값 공간의 구문과 생김새가 똑같아서 특히 헷갈린다.

```typescript
type T1 = 'string literal';    // 타입 공간 (리터럴 타입)
const v1 = 'string literal';   // 값 공간
type T2 = 123;                 // 타입 공간
const v2 = 123;                // 값 공간
```

`type`이나 `interface` 다음의 심벌은 타입 공간, `const`나 `let` 선언으로 도입된 심벌은 값이다. 두 공간의 직관을 기르는 가장 좋은 방법 중 하나는 **타입스크립트 플레이그라운드**다 - 생성된 자바스크립트를 나란히 보여 주는데, 타입은 컴파일 시 지워지므로(Item 3) **사라지는 심벌은 타입 공간에 있던 것**이다.

문장 하나 안에서도 두 공간을 오간다. 타입 선언(`:`)이나 단언(`as`) 뒤는 타입 공간, 할당의 `=` 뒤는 값 공간이다.

```typescript
const jane: Person = { first: 'Jane', last: 'Jacobs' };
//          ------   ------------------------------- 값
//          └ 타입
```

특히 함수 문장은 두 공간을 반복해서 오간다.

```typescript
function email(to: Person, subject: string, body: string): Response {
  //           --  ------   -------  ------  ----  ------   -------- 타입
  //           └ to, subject, body는 값
  // ...
}
```

## 3. class와 enum은 타입과 값을 동시에 도입한다

첫 예제의 `Cylinder`를 클래스로 바꾸면 에러가 사라진다.

```typescript
class Cylinder {
  radius: number;
  height: number;
  constructor(radius: number, height: number) {
    this.radius = radius;
    this.height = height;
  }
}

function calculateVolume(shape: unknown) {
  if (shape instanceof Cylinder) {
    shape
    // ^? (parameter) shape: Cylinder
    shape.radius
    //    ^? (property) Cylinder.radius: number
  }
}
```

클래스가 도입하는 **타입은 그 형태(속성과 메서드)에 기반**하고, **값은 생성자**다.

## 4. 공간에 따라 뜻이 달라지는 연산자와 키워드

| 구문 | 값 공간에서 | 타입 공간에서 |
|------|------------|--------------|
| `typeof` | JS 런타임 `typeof` 연산자 - 8가지 문자열 중 하나를 반환 | 값을 받아 그 타입스크립트 타입을 반환 |
| `obj['field']` | 속성 접근 (`obj.field`와 동일) | 다른 타입의 속성 타입 조회 (`.` 표기는 불가) |
| `this` | JS의 `this` 키워드 (Item 69) | "다형적 this" - this의 타입스크립트 타입. 서브클래스 메서드 체인에 유용 |
| `&` / `\|` | 비트 AND / OR | 인터섹션 / 유니온 |
| `const` | 새 변수 선언 | `as const` - 리터럴(표현식)의 추론 타입을 바꿈 (Item 20) |
| `extends` | 서브클래스 정의 (`class A extends B`) | 서브타입(`interface A extends B`) 또는 제네릭 제약(`<T extends number>`) |
| `in` | 루프(`for (key in object)`) 또는 `in` 연산자 | 매핑된 타입 (Item 15) |
| `!` | 논리 NOT (`!x`) | 널 아님 단언 (`x!` - Item 9) |

`typeof`는 특히 중요하다.

```typescript
type T1 = typeof jane;
//   ^? type T1 = Person
type T2 = typeof email;
//   ^? type T2 = (to: Person, subject: string, body: string) => Response

const v1 = typeof jane;   // 값은 "object"
const v2 = typeof email;  // 값은 "function"
```

타입 문맥의 `typeof`는 값의 **타입스크립트 타입**을 돌려준다. 값 문맥의 `typeof`는 자바스크립트 런타임 타입의 문자열을 돌려주는데, 런타임 타입 시스템은 정적 타입 시스템보다 훨씬 단순하다 - 무한히 다양한 타입스크립트 타입과 달리 가능한 반환값이 8개뿐이다(`"string"`, `"number"`, `"boolean"`, `"undefined"`, `"object"`, `"function"`, `"symbol"`, `"bigint"`).

속성 타입 조회는 대괄호 표기만 가능하며, 인덱스 자리에는 유니온을 포함해 어떤 타입이든 넣을 수 있다.

```typescript
const first: Person['first'] = jane['first'];  // 또는 jane.first
//           --------------- 타입

type PersonEl = Person['first' | 'last'];
//   ^? type PersonEl = string
type Tuple = [string, number, Date];
type TupleEl = Tuple[number];
//   ^? type TupleEl = string | number | Date
```

## 5. 두 공간의 혼동이 낳는 실제 에러

타입스크립트가 내 코드를 전혀 이해하지 못하는 것 같다면 두 공간의 혼동일 가능성이 크다. `email` 함수를 객체 매개변수로 바꾸고(왜 좋은지는 Item 38) 자바스크립트처럼 구조 분해를 하면:

```typescript
function email({
  to: Person,
  // ~~~~~~ Binding element 'Person' implicitly has an 'any' type
  subject: string,
  // ~~~~~~ Binding element 'string' implicitly has an 'any' type
  body: string
  // ~~~~~~ Binding element 'string' implicitly has an 'any' type
}) { /* ... */ }
```

`Person`과 `string`이 **값 문맥**으로 해석된 것이다 - `Person`이라는 변수와 `string`이라는 변수 두 개를 만들려는 코드가 되어 버렸다(구조 분해의 `속성: 이름`은 이름 바꾸기 문법이다). 타입과 값을 분리해서 써야 한다.

```typescript
function email(
  {to, subject, body}: {to: Person, subject: string, body: string}
) {
  // ...
}
```

훨씬 장황해 보이지만 실무에서는 매개변수 타입에 이름을 붙여 두거나 문맥에서 추론(Item 24)되는 경우가 많다.

> **핵심 통찰**: 헷갈리는 코드를 만나면 "이 심벌은 컴파일 후 자바스크립트에 남는가?"를 물어보라. 남으면 값, 지워지면 타입이다. 두 공간의 닮은 구문들은 처음엔 혼란스럽지만, 익숙해지면 오히려 연상 기호로 유용해진다.

## 기억해야 할 것들

- 타입스크립트 표현식을 읽을 때 타입 공간인지 값 공간인지 구별할 줄 알아야 한다. 타입스크립트 플레이그라운드로 직관을 길러라.
- 모든 값에는 정적 타입이 있지만 타입 공간에서만 접근할 수 있다. `type`·`interface` 같은 타입 공간 구문은 지워지며 값 공간에서 접근할 수 없다.
- `class`·`enum` 같은 구문은 타입과 값을 모두 도입한다.
- `typeof`·`this`를 비롯한 많은 연산자와 키워드가 타입 공간과 값 공간에서 다른 의미를 갖는다.
