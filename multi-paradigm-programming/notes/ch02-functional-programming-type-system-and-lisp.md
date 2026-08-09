# Chapter 2: Functional Programming, Type System, and LISP (함수형 프로그래밍과 타입 시스템 그리고 LISP)

## 핵심 질문

프로그래밍 패러다임과 언어는 끊임없이 진화하며 오늘날 우리는 객체지향, 함수형, 명령형 등 다양한 패러다임이 공존하는 멀티패러다임 언어의 시대를 살고 있다. 함수형 프로그래밍의 핵심 개념과 이를 뒷받침하는 타입스크립트의 타입 시스템을 어떻게 결합하면 더 안전하고 유지보수하기 쉬운 코드를 작성할 수 있을까? 그리고 함수형 프로그래밍의 뿌리인 LISP의 설계 철학은 현대 멀티패러다임 언어에 어떤 영향을 주고 있을까?

---

## 1. 타입 추론과 함수 타입 그리고 제네릭

타입스크립트는 자바스크립트에 강력한 타입 시스템을 추가하여 코드의 안정성과 가독성을 높인다. 타입스크립트의 타입 추론을 통해 개발자는 명시적인 타입 선언 없이도 안전한 코드를 작성할 수 있다. 고차 함수와 제네릭을 활용하면 복잡한 함수형 프로그래밍 패턴을 구현할 수 있다. 또한 객체지향 클래스와 함수형 함수의 결합을 통해 더욱 유연하고 강력한 코드를 작성할 수 있다.

### 1.1 타입 추론

타입스크립트의 타입 추론(*Type Inference - 코드 작성 시 타입을 명시적으로 선언하지 않아도 컴파일러가 자동으로 타입을 추론해주는 기능*)은 코드의 간결성을 유지하면서도 타입 안정성을 확보할 수 있게 한다.

#### 타입 추론의 기본적인 콘셉트

다음 코드에서 `a`는 명시적으로 타입이 선언되지 않았지만 타입스크립트는 `10`이라는 값을 통해 `a`의 타입을 `number`로 추론한다. 따라서 이후 `a`에 다른 타입의 값을 할당하려고 하면 타입 오류가 발생한다.

```typescript
// [코드 2-1] 타입 추론 기본 예시
let a = 10;
```

[코드 2-1]과 같은 상황에서는 타입을 명시적으로 선언하지 않아도 된다. IDE에서도 타입스크립트가 어떻게 타입을 추론하는지 가이드를 제공하므로 코딩 과정과 유지보수에 용이하다.

#### 변수와 상수의 타입 추론

타입스크립트는 변수를 선언할 때 초기화된 값으로부터 타입을 추론한다.

```typescript
// [코드 2-2] 변수 타입 추론
let message = "Hello, TypeScript!";
```

[코드 2-2]에서 `message`는 명시적인 타입 선언 없이도 `string` 타입으로 추론된다. 다음은 상수 타입 추론 예제이며 다음 코드에서 주석은 타입 가이드 박스를 표현한 것이다. 즉 IDE에서 `selected` 등에 마우스를 올리면 보이는 플로팅 박스에 표시되는 내용이다.

```typescript
// [코드 2-3] 상수 타입 추론
const selected = true;
// [const selected: true]
let checked = true;
// [let checked: boolean]
```

[코드 2-3]에서 `const`로 선언된 `selected`는 값을 재할당할 수 없기에 값이 바뀔 수 없어 타입이 `true`로 추론된다. 반면 `let`으로 선언된 `checked`는 값을 재할당하여 변경할 수 있으므로 타입이 `boolean`으로 추론된다.

#### 함수의 반환 타입 추론

타입스크립트는 함수의 반환 타입도 자동으로 추론할 수 있다.

```typescript
// [코드 2-4] 반환 타입 추론 1
function add(a: number, b: number) {
  return a + b;
}
```

[코드 2-4]에서 `add` 함수는 `number` 타입의 인자를 받아 `number` 타입의 값을 반환한다. 반환 타입을 명시적으로 지정하지 않았지만 타입스크립트는 함수의 반환 타입을 `a`와 `b`를 통해 `number`로 추론한다.

```typescript
// [코드 2-5] 반환 타입 추론 2
function add(a: string, b: string) {
  return a + b;
}
```

같은 코드에서 [코드 2-5]처럼 `a`와 `b`의 타입을 `string`으로 변경하면 반환 타입도 `string`이 된다.

```typescript
// [코드 2-6] 반환 타입 추론 3
function add(a: string, b: string) {
  return parseInt(a) + parseInt(b);
}
```

타입스크립트는 `parseInt(a)`와 `parseInt(b)`가 `number` 타입의 값을 반환한다는 사실을 알고 있기 때문에 각 결과의 자리를 `number`로 추론하여 `add` 함수의 반환 타입을 `number`로 추론하게 된다.

따라서 [코드 2-7]처럼 명시적으로 반환 타입을 지정할 수도 있으며 이는 타입스크립트의 타입 추론과 일치한다.

```typescript
// [코드 2-7] 명시적인 반환 타입 지정
function add(a: string, b: string): number {
  return parseInt(a) + parseInt(b);
}
```

#### 객체의 속성 타입 추론

타입스크립트는 객체 리터럴의 속성 타입도 추론할 수 있다.

```typescript
// [코드 2-8] 객체의 속성 타입 추론
let user = {
  name: "Marty",
  age: 30,
};
```

[코드 2-8]에서 `user` 객체의 `name` 속성은 `string` 타입으로, `age` 속성은 `number` 타입으로 추론된다.

#### 함수 인자의 타입 추론

타입스크립트는 함수 인자의 타입도 추론할 수 있다.

```typescript
// [코드 2-9] 함수 인자의 타입 추론
let strs = ['a', 'b', 'c'];
strs.forEach(str => console.log(str.toUpperCase())); // [str: string]
```

[코드 2-9]에서 타입스크립트는 `strs`를 `string[]`으로 추론한다. 그리고 `forEach` 메서드는 `strs` 배열의 요소 타입을 기반으로 화살표 함수의 `str` 타입도 `string`으로 추론한다. 따라서 `toUpperCase()` 메서드를 사용할 수 있어서 자동완성이 동작하며 정상적으로 컴파일된다.

타입스크립트의 타입 추론 사례 중 이 부분이 특히 매력적이다. 고차 함수에서도 타입 추론이 동작하므로 인자로 전달받은 함수의 인자 타입을 추론할 수 있어 화살표 함수를 간결하게 작성할 수 있다. 따라서 화살표 함수의 간결한 표현을 유지하면서도 타입 안전성을 확보할 수 있다.

앞으로 이번 장에서 사용자 정의 고차 함수도 이와 동일하게 타입 추론이 동작하도록 구현하는 법을 알아보겠다.

#### 제네릭을 통한 타입 추론

타입스크립트에서 제네릭 함수를 사용하면 하나의 함수가 다양한 타입을 지원하여 다형성이 높은 함수가 된다. `identity` 함수는 인자로 받은 값의 타입을 그대로 반환하는 제네릭 함수의 좋은 예이다. `identity`는 제네릭 타입 매개변수 `T`를 사용한다. 이 함수는 인자 `arg`의 타입을 `T`로 받아 동일한 타입 `T`를 반환한다.

이해를 돕고자 설명을 덧붙이면 `identity`를 평가하는 표현식에서 전달한 인자 `arg`의 타입으로 `T`의 실제 타입이 정해지며 해당 타입이 `identity`의 반환 타입이 된다.

```typescript
// [코드 2-10] identity<T> 함수
function identity<T>(arg: T): T {
  return arg;
}

const a = identity("hi");                        // ① [const a: "hi"]
const b = identity(1);                           // ② [const b: 1]
const c = identity<string>("a");                 // ③ [const c: string]
const d = identity<number>(1);                   // ④ [const d: number]
class User {}
const e = identity(new User());                  // ⑤ [const e: User]
const f = identity((n: number) => n % 2 === 1);  // ⑥ [const f: (n: number) => boolean]
```

이 예제는 `identity` 함수가 어떻게 제네릭 타입을 받아들여 다양한 타입을 처리할 수 있는지 잘 보여준다. 각 예에서 인자 `arg`의 타입에 따라 `T`의 실제 타입이 결정되며 그에 따라 반환 타입도 동일한 타입 `T`로 추론된다.

먼저 ① `identity` 함수에 문자열 `"hi"`를 전달하면 제네릭 타입 매개변수 `T`가 `"hi"`가 되고 `a`의 타입 역시 `"hi"`로 추론된다. 같은 방식으로 ② `identity` 함수에 `1`을 전달하면 `T`가 `1`이 되고 `b`의 타입 역시 `1`이 된다.

다음으로 ③ `identity<string>("a")`와 같이 `T`를 명시적으로 `string`으로 지정하고 인자는 `"a"`를 전달한다. 이때 `c`의 타입은 `string`으로 결정된다. 마찬가지로 ④ `identity` 함수에 `T`를 명시적으로 `number`로 지정하고 인자는 숫자 `1`을 전달하면 `d`의 타입은 `number`로 결정된다.

객체를 전달하는 경우도 동일하게 작동한다. ⑤ `User`의 인스턴스를 전달하면 `T`가 `User`로 결정되고 `e`의 타입 역시 `User`가 된다.

마지막으로 ⑥ `(n: number) => n % 2 === 1`이라는 함수를 전달하면 타입스크립트는 이 함수의 타입을 `(n: number) => boolean`으로 추론하고 `f`의 타입을 `(n: number) => boolean`으로 지정한다.

타입스크립트의 타입 추론은 코드의 가독성과 안전성을 높이는 데 중요한 역할을 한다. 이러한 방식 덕분에 개발자는 타입 시스템을 도입하고도 높은 생산성을 유지할 수 있다.

### 1.2 함수 타입과 제네릭

타입스크립트는 함수형 프로그래밍을 지원하기 위해 고차 함수, 함수 타입, 제네릭 등의 다양한 기능을 제공한다. 먼저 함수 타입을 명시적으로 정의하면 함수의 입력과 출력 타입을 명확하게 표현할 수 있다. 또한 제네릭을 활용하면 폭넓은 타입을 지원하는 범용 함수를 만들 수 있다. 특히 고차 함수는 인자로 전달받은 함수의 매개변수 타입을 추론하고 함께 전달된 다른 인자들의 타입과도 연계해 타입을 유연하게 추론하도록 돕는다.

#### 함수의 타입을 정의하는 여러 가지 방법

타입스크립트에서는 함수의 타입을 여러 가지 방식으로 정의할 수 있다. 이를 통해 함수의 시그니처를 명확히 하고 코드의 안정성과 가독성을 높일 수 있다.

가장 기본적인 방법은 함수의 매개변수와 반환값에 타입을 명시하는 것이다.

```typescript
// [코드 2-11] 기본적인 함수 타입 정의
function add(a: number, b: number): number {
  return a + b;
}
const result: number = add(2, 3); // 5
```

[코드 2-11]에서 `add` 함수는 `number` 타입의 매개변수 두 개를 받아 `number` 타입의 값을 반환한다. 함수의 시그니처를 명확히 함으로써 함수 호출 시 타입 오류를 방지할 수 있다.

타입스크립트는 함수 오버로드를 지원하여 동일한 함수명으로 다양한 시그니처를 정의할 수 있다. 이를 통해 함수의 유연성을 높이고 다양한 입력 타입을 처리할 수 있다.

```typescript
// [코드 2-12] 함수 오버로드
function double(a: number): number;
function double(a: string): string;
function double(a: number | string): number | string {
  if (typeof a === 'number') {
    return a * 2;
  } else {
    return a + a;
  }
}
const num: number = double(10); // 20
const str: string = double('Hi'); // 'HiHi'
```

함수 구현부에서 `typeof` 연산자를 사용한 타입 가드는 런타임에서 `a`의 타입을 검사하여 타입에 따라 다른 로직을 실행하도록 한다. 컴파일 타임에서도 타입스크립트가 `if` 블록 내에서 타입을 정확하게 구분하여 추론한다. 이를 타입스크립트에서는 타입 가드(*Type Guard*)에 의한 타입 좁히기(*Type Narrowing*)라고 부른다. `if (typeof a === 'number')` 블록 안에서는 `a`가 `number` 타입으로 추론되며 `else` 블록 안에서는 `a`가 `string` 타입으로 추론된다. 이러한 타입 추론 덕분에 컴파일 타임에서 타입 안정성을 확보할 수 있다.

화살표 함수는 간결한 문법을 제공하며 함수의 타입을 정의할 때도 유용하다.

```typescript
// [코드 2-13] 화살표 함수
const multiply = (a: number, b: number): number => a * b;
const num: number = multiply(4, 5); // 20
```

이처럼 화살표 함수를 사용할 때도 매개변수와 반환 타입을 명시적으로 선언하여 타입 안전성을 확보할 수 있다. 하지만 타입스크립트는 타입 추론이 강력하기 때문에 매개변수의 타입만 명시해도 충분하다.

```typescript
// [코드 2-14] 화살표 함수 (타입 추론)
const multiply = (a: number, b: number) => a * b;
const num: number = multiply(4, 5); // 20
```

[코드 2-14]에서는 매개변수의 타입만 명시했지만 타입스크립트가 함수의 반환 타입을 `number`로 추론한다. 이렇게 타입 추론을 통해 코드의 간결함과 타입 안전성을 동시에 유지할 수 있다.

```typescript
// [코드 2-15] 함수 타입 별칭
type Add = (a: number, b: number) => number;
const add: Add = (a, b) => a + b;
```

[코드 2-15]에서는 `Add`라는 함수 타입 별칭을 정의하여 `(a: number, b: number) => number` 형태의 함수를 나타낸다. 그런 다음 `add`라는 함수 변수를 `Add` 타입으로 선언하면 타입에 맞게 가이드를 받으며 구현할 수 있다. 이렇게 함수 타입을 별칭으로 정의하면 여러 곳에서 동일한 함수 타입을 재사용할 수 있다.

이제 지금까지 알아본 다양한 함수 타입 정의 방법을 바탕으로 고차 함수와 제네릭을 활용하여 더 복잡하고 유연한 함수형 프로그래밍 패턴을 구현하는 방법을 살펴보겠다.

#### constant와 제네릭

`constant` 함수는 인자로 입력받은 값을 항상 그대로 돌려주는 함수를 반환한다. 이 함수는 특정 값을 캡처하여 호출될 때마다 해당 값을 반환하는 함수이다. 이런 함수를 제네릭으로 구현하면 다양한 타입의 값을 처리할 수 있다.

```typescript
// [코드 2-16] constant 함수와 타입
function constant<T>(a: T): () => T {
  return () => a;
}
const getFive = constant(5);
const ten: number = getFive() + getFive();
console.log(ten); // 10

const getHi = constant("Hi");
const hi2: string = getHi() + getHi();
console.log(hi2); // HiHi
```

예제에서는 `constant(5)`로 생성된 함수 `getFive`를 호출하여 두 값을 더해 `ten`에 저장한다. 같은 방식으로 `constant("Hi")`로 생성된 함수 `getHi`를 호출하여 두 값을 더해 `hi2`에 저장한다.

`constant` 함수는 제네릭을 사용하여 어떤 타입의 값도 처리할 수 있으며 타입스크립트의 타입 추론 덕분에 명시적인 타입 선언 없이도 올바르게 동작한다. [코드 2-16]의 동작 방식을 자세히 살펴보면 다음과 같다.

1. `constant` 함수 옆에 제네릭 `<T>`를 작성하여 이 함수에서 `T` 타입을 사용하겠다고 선언한다.
2. `T`를 활용하여 `constant` 함수의 인자 `a`의 타입을 `T`로 정의한다.
3. `constant` 함수는 `T` 타입의 값을 인자로 받아 `T` 타입의 값을 반환하는 함수를 반환한다.
4. 반환되는 함수의 타입을 `() => T`로 정의하여 인자를 받지 않고 `T` 타입의 값을 반환한다고 명시한다.
5. `constant` 함수가 `a`로 받은 `5`로 인해 `T`가 `number`로 추론되고 반환되는 함수 `getFive`의 반환 타입도 `number`가 된다.
6. `constant` 함수가 `a`로 받은 `"Hi"`로 인해 `T`가 `string`으로 추론되고 반환되는 함수 `getHi`의 반환 타입도 `string`이 된다.
7. 제네릭을 잘 활용했기 때문에 `constant` 함수는 어떤 타입의 값이든 처리할 수 있으며 타입 추론 덕분에 반환되는 함수의 타입도 정확히 추론된다.

> **참고**: 여기서 `identity` 함수와 다르게 `5`나 `"Hi"`를 받고도 `T`가 각각 `number`와 `string`으로 추론된 이유는 타입스크립트에서는 고차 함수가 다루는 일급 함수의 인자나 반환값을 추론할 때 넓은 타입으로 추론하는 경향이 있기 때문이다. 이는 중요한 부분은 아니지만 참고로 알아두면 좋다.

지금까지 타입 추론과 함수 타입, 제네릭에 대한 기본적인 개념을 익혔다. 이러한 개념과 기능을 잘 연습하면 타입스크립트와 같은 멀티패러다임 언어에서 더욱 안전한 코드를 작성할 수 있다.

---

## 2. 멀티패러다임 언어에서 함수형 타입 시스템

지금까지 알아본 타입 추론과 함수 타입, 제네릭 등의 기본적인 개념과 문법은 함수형 고차 함수에 타입 시스템을 적용하기 위한 기초다. 이제 이터러블 헬퍼 함수에 타입 시스템을 적용하면서 멀티패러다임 언어에서의 함수형 타입 시스템에 대해 알아보겠다.

### 2.1 이터레이션 프로토콜과 타입 다시 보기

`Iterator`, `Iterable`, `IterableIterator`에 일급 함수를 더한 함수형 고차 함수들을 만들어보겠다. 그러려면 먼저 1장에서 소개한 코드와 개념을 제대로 이해하고 있어야 한다. 이번 절에서는 앞에서 배운 개념들을 다시 정리해보겠다.

```typescript
// [코드 2-17] Iterator, Iterable, IterableIterator 타입 다시 보기
interface IteratorYieldResult<T> {
  done?: false;
  value: T;
}

interface IteratorReturnResult {
  done: true;
  value: undefined;
}

interface Iterator<T> { // 타입스크립트의 Iterator 인터페이스 중 필요한 부분만 남겼습니다.
  next(): IteratorYieldResult<T> | IteratorReturnResult;
}

interface Iterable<T> {
  [Symbol.iterator](): Iterator<T>;
}

interface IterableIterator<T> extends Iterator<T> {
  [Symbol.iterator](): IterableIterator<T>;
}
```

다음은 복습을 위한 체크리스트로서 우리는 다음 개념들을 바탕으로 타입 시스템을 적용하는 방법을 배울 것이다.

1. 이터레이션 프로토콜과 관련된 세 가지 값인 `Iterator`, `Iterable`, `IterableIterator`에 대해 알고 있다.
2. `for...of` 문으로 순회할 수 있는 값은 오직 이터러블이다.
3. 전개 연산자로 배열을 만들 수 있는 값도 오직 이터러블이다.
4. `IterableIterator`를 만드는 함수를 구현할 때 반환값을 `{ next() {...}, [Symbol.iterator]() {...} }` 형식으로 구현할 수 있으며 이 객체는 이터레이터이자 동시에 이터러블이다.
5. 제너레이터로도 이터레이터를 만들 수 있으며 제너레이터의 실행 결과는 `IterableIterator`이다.
6. 제너레이터의 `yield`와 이터레이터의 `next()`의 관계를 이해하고 있다.
7. 이터레이터에 고차 함수를 조합하여 `forEach`, `map`, `filter`를 만들 수 있으며 이터레이션 프로토콜을 지원하여 언어의 기능과 상호작용하도록 만들 수 있다.

[코드 2-17]은 이번 장의 핵심 내용을 간결하게 전달하기 위해 일부러 축약된 형태를 사용했다. 실제 에디터에서 이대로 작성하면 중복 타입 선언이나 추론 오류가 발생한다. 타입스크립트에서 공식적으로 제공하는 `Iterator` 인터페이스는 `lib.es2015.iterable.d.ts` 파일에서 확인할 수 있다.

### 2.2 함수형 고차 함수와 타입 시스템

우리가 구현하는 반복자 패턴을 활용한 함수형 고차 함수들은 이터러블 자료구조를 중심으로 구성되므로 이를 이터러블 헬퍼 함수라고 부를 수 있다. 이 절에서는 이터러블 헬퍼 함수에 타입 시스템을 적용하는 방법을 다룬다.

#### forEach와 타입

`forEach` 함수는 주어진 이터러블의 각 요소에 대해 지정된 함수를 실행하는 함수이다. 이를 다음과 같이 제네릭 타입을 사용하여 구현할 수 있다.

```typescript
// [코드 2-18] forEach 함수와 타입
function forEach<A>(f: (a: A) => void, iterable: Iterable<A>): void {
  for (const a of iterable) {
    f(a);
  }
}

const array = [1, 2, 3];
forEach(a => console.log(a.toFixed(2)), array); // [a: number]
// 1.00
// 2.00
// 3.00
```

[코드 2-18]에서 사용된 타입 정의와 실행 과정을 하나씩 자세히 살펴보겠다. 이를 통해 이터러블과 고차 함수, 일급 함수, 제네릭 간의 유기적 연결성을 제대로 이해하길 바란다.

1. `forEach` 옆에 제네릭 `<A>`를 작성하여 함수에서 `A` 타입을 사용하겠다고 선언한다.
2. `A`를 활용하여 `f` 함수의 타입을 인자로 `a: A`를 받아 `void`를 반환하는 타입으로 정의한다.
3. `f` 함수의 인자 `a`의 타입을 앞에서 선언한 제네릭 타입 `A`로 선언한다.
4. 그리고 `iterable`의 타입을 `A`를 요소로 갖는 `Iterable<A>`라고 정의한다.
5. 이해를 돕고자 설명을 덧붙이자면 '`<A>`를 선언하고 `a: A`와 `Iterable<A>`를 작성하여 `iterable`의 요소 타입이 `A`이며 그 `A`가 `f` 함수의 인자 `a`가 되도록 연결해주었다'라고 할 수 있다.
6. `iterable`의 타입은 `Iterable<A>`이기에 `for (const a of iterable)`에서 `a`의 타입은 `A`이다.
7. `forEach`가 받은 `array: number[]`로 인해 `Iterable<A>`로 `Iterable<number>`가 되고 `f`의 `a`도 `number`가 된다.
8. 제네릭을 잘 활용했기 때문에 `a`는 `number` 타입으로 정확히 추론되며 `toFixed(2)` 메서드를 안전하게 호출할 수 있다.

#### map과 타입

`map` 함수는 이터러블의 각 요소에 특정 함수를 적용하여 변환된 값을 새로운 이터러블로 생성하는 함수이다. 이를 제너레이터와 제네릭 타입을 사용하여 구현할 수 있다.

```typescript
// [코드 2-19] 제너레이터로 구현한 map 함수와 타입
function* map<A, B>(f: (a: A) => B, iterable: Iterable<A>): IterableIterator<B> {
  for (const a of iterable) {
    yield f(a);
  }
}

const array = ['1', '2', '3'];
const mapped = map(a => parseInt(a), array); // [a: string]
// [const mapped: IterableIterator<number>]
const array2: number[] = [...mapped];
console.log(array2);
// [1, 2, 3]

const [head] = map(a => a.toUpperCase(), ['a', 'b', 'c']);
console.log(head); // [head: string]
// A
```

이번에도 하나씩 자세히 살펴보겠다.

1. `map<A, B>`를 작성하여 제네릭 타입 `A`와 `B`를 만든다.
2. `map` 함수는 `A` 타입을 입력받아 `B` 타입을 출력하는 함수 `f`와 `Iterable<A>`를 인자로 받아 `IterableIterator<B>`를 반환하도록 정의되었다.
3. 첫 번째 경우 `map` 함수를 실행할 때 전달한 `array`가 `Iterable<string>`으로 해석되어 `A`는 `string`이 된다.
4. `a => parseInt(a)`의 반환 타입에 의해 `B`가 `number`가 되어 `map(a => parseInt(a), array)`의 반환 타입이 `IterableIterator<number>`가 된다.
5. 따라서 `mapped` 역시 `IterableIterator<number>`로 추론되고 `mapped`를 전개 연산자로 배열로 변환한 값인 `array2`가 `number[]` 타입으로 잘 처리된다.
6. 두 번째 경우 `[head]`로 구조 분해 할당을 했고 역시 `string`으로 타입이 제대로 추론되었다.

타입스크립트의 타입 시스템을 잘 사용하면 타입 안정성을 유지하면서도 유연하게 제네릭 타입을 활용한 고차 함수를 구현할 수 있다.

#### filter와 타입

`filter` 함수는 `Iterable<A>`를 받아 필터링된 `IterableIterator<A>`를 만드는 함수라고 할 수 있다.

```typescript
// [코드 2-20] 제너레이터로 구현한 filter 함수와 타입
function* filter<A>(f: (a: A) => boolean, iterable: Iterable<A>): IterableIterator<A> {
  for (const a of iterable) {
    if (f(a)) {
      yield a;
    }
  }
}

const array = [1, 2, 3, 4];
const filtered = filter(a => a % 2 === 0, array); // [a: number]
const array2: number[] = [...filtered]; // [const filtered: IterableIterator<number>]
console.log(array2);
// [2, 4]
```

원서에서는 독자 연습으로 남겨두었지만, `forEach`와 `map`에서 다룬 타입 흐름 분석을 `filter`에도 적용해보면 다음과 같다.

1. `filter<A>`를 작성하여 제네릭 타입 `A`를 만든다.
2. `filter` 함수는 `A` 타입을 입력받아 `boolean`을 반환하는 함수 `f`와 `Iterable<A>`를 인자로 받아 `IterableIterator<A>`를 반환하도록 정의되었다. `map`과 달리 `B` 타입이 없는 이유는 `filter`가 요소를 변환하지 않고 걸러내기만 하기 때문이다.
3. `filter` 함수를 실행할 때 전달한 `array`가 `Iterable<number>`로 해석되어 `A`는 `number`가 된다.
4. `f`의 인자 `a`도 `number`가 되어 `a % 2 === 0`이라는 산술 연산이 타입 안전하게 동작한다.
5. 반환 타입은 `IterableIterator<A>` 즉 `IterableIterator<number>`가 되어 `filtered`를 전개 연산자로 배열로 변환한 `array2`가 `number[]` 타입으로 잘 처리된다.

`map`은 `A → B` 변환이 있어 제네릭이 두 개(`A`, `B`)였지만, `filter`는 요소 타입이 변하지 않으므로 `A` 하나면 충분하다. 이 차이가 `filter`의 타입 정의가 `map`보다 단순한 이유이다.

여기서 `filter` 함수는 제네릭 타입 `A`를 사용하였고 `filter`의 인자 `f`의 `a`와 인자 `iterable`의 요소 타입을 `A`로 지정했다. 그리고 `filter`가 반환하는 `IterableIterator`의 요소 타입도 `A`로 지정했다. `filter` 함수는 인자로 받은 이터러블의 요소 자체는 변경하지 않고 필터링만 수행하는 함수이기 때문이다.

#### reduce와 타입

마지막으로 `reduce` 함수를 간결하게 구현하고 타입을 추가해보겠다.

```typescript
// [코드 2-21] reduce 함수와 타입
function reduce<A, Acc>(
  f: (acc: Acc, a: A) => Acc, acc: Acc, iterable: Iterable<A>
): Acc {
  for (const a of iterable) {
    acc = f(acc, a);
  }
  return acc;
}

const array = [1, 2, 3];
const sum = reduce((acc, a) => acc + a, 0, array);
console.log(sum); // [const sum: number]
// 6

const strings = ['a', 'b', 'c'];
const abc = reduce((acc, a) => `${acc}${a}`, '', strings);
console.log(abc); // [const abc: string]
// abc
```

`reduce` 함수는 `(acc: Acc, a: A) => Acc` 타입의 함수를 받고 초깃값 `acc: Acc`와 `Iterable<A>`를 받는다. 요소를 순회하면서 `f(acc, a)`를 실행하여 누적값을 계산하고 최종적으로 누적값을 반환한다.

이를 타입 정의 관점에서 하나씩 자세히 살펴보겠다.

1. `reduce<A, Acc>`를 작성하여 제네릭 타입 `A`와 `Acc`를 만든다.
2. `reduce` 함수는 `Acc` 타입의 초깃값 `acc`와 `A` 타입의 요소를 가진 `Iterable<A>`를 인자로 받는다.
3. 그리고 `Acc` 타입의 초깃값과 `A` 타입의 현재 값을 받아 `Acc` 타입의 새로운 누적값을 반환하는 함수 `f`를 인자로 받는다.
4. 함수는 이터러블의 각 요소를 순회하면서 `f(acc, a)`를 실행하여 누적값을 갱신한다.
5. 마지막으로 `reduce` 함수는 최종 누적값 `Acc`를 반환한다.

이처럼 함수의 동작을 타입 중심으로 설명하면 개발자 간 소통을 보다 원활하고 정확하게 할 수 있다.

#### reduce 함수 오버로드

자바스크립트의 `Array.prototype.reduce`는 초깃값을 생략할 수 있다. 여기서 함께 만든 이터러블을 다루는 `reduce`도 동일한 스펙을 지원하도록 구현하고자 한다.

- 초깃값이 있을 때는 세 개의 인자를 받는다.
- 초깃값을 생략하고자 할 때는 `f`와 `iterable`만을 받는다. 이때 이터러블의 첫 번째 요소가 초깃값이 된다.
- 초깃값 없이 빈 배열이 전달된 경우에는 누적할 수 없고 타입이 올바르지 않으므로 에러를 발생시킨다.

이렇게 구현하려면 함수 오버로드를 사용해야 한다. 함수 오버로드 또는 메서드 오버로드는 함수나 메서드의 시그니처를 여러 개 정의하고 실제 구현은 하나만 제공하는 방식이다. 이로써 하나의 함수명으로 다양한 호출 방식에 대응할 수 있다.

```typescript
// [코드 2-22] reduce(f, iterable)
function baseReduce<A, Acc>(
  f: (acc: Acc, a: A) => Acc, acc: Acc, iterator: Iterator<A>
): Acc {
  while (true) {
    const { done, value } = iterator.next();
    if (done) break;
    acc = f(acc, value);
  }
  return acc;
}

// ①
function reduce<A, Acc>(
  f: (acc: Acc, a: A) => Acc, acc: Acc, iterable: Iterable<A>
): Acc;
// ②
function reduce<A, Acc>(
  f: (a: A, b: A) => Acc, iterable: Iterable<A>
): Acc;
function reduce<A, Acc>(
  f: (a: Acc | A, b: A) => Acc,
  accOrIterable: Acc | Iterable<A>,
  iterable?: Iterable<A>
): Acc {
  if (iterable === undefined) { // ③
    const iterator = (accOrIterable as Iterable<A>)[Symbol.iterator]();
    const { done, value: acc } = iterator.next();
    if (done) throw new TypeError("'reduce' of empty iterable with no initial value");
    return baseReduce(f, acc, iterator) as Acc;
  }
  return baseReduce(f, accOrIterable as Acc, iterable[Symbol.iterator]()); // ④
}
```

함수 시그니처 부분(①, ②)과 구현 부분(③, ④)을 설명하면 다음과 같다.

- **① `reduce<A, Acc>(f: (acc: Acc, a: A) => Acc, acc: Acc, iterable: Iterable<A>): Acc`**: 제네릭 타입 `A`와 `Acc`를 선언하고 초깃값 `acc: Acc`와 `Iterable<A>`를 인자로 받는다. `(acc: Acc, a: A) => Acc` 타입의 함수를 인자로 받아 누적값을 계산한 다음 최종적으로 `Acc` 타입의 값을 반환한다.
- **② `reduce<A, Acc>(f: (a: A, b: A) => Acc, iterable: Iterable<A>): Acc`**: 제네릭 타입 `A`와 `Acc`를 선언하고 초깃값 없이 `Iterable<A>`와 `(a: A, b: A) => Acc` 타입의 함수를 인자로 받는다. 이터러블의 첫 번째 요소를 초깃값으로 사용하여 누적값을 계산한 다음 최종적으로 `Acc` 타입의 값을 반환한다.
- **③ 마지막 인자인 `iterable`이 없는 경우 (`iterable === undefined`)**: 두 번째 인자인 `accOrIterable`이 이터러블이다. `[Symbol.iterator]()` 메서드를 실행해 이터레이터로 변환하고 `next()` 메서드로 첫 번째 요소를 꺼낸다. 빈 이터러블이면 에러를 발생시키고 요소가 있으면 `baseReduce`를 실행한다.
- **④ 세 개의 인자를 모두 받은 경우 (else)**: 두 번째 인자인 `accOrIterable`이 초깃값이고 `iterable`은 이터러블이다. `baseReduce`를 실행하여 이터레이터의 각 요소를 순회하면서 `f(acc, value)`를 실행하여 누적값을 갱신한다. 최종적으로 누적된 값을 반환한다.

다음은 이렇게 구현한 `reduce`를 사용하는 예시이다.

```typescript
// [코드 2-22a] reduce 사용 예제
// 첫 번째 reduce 함수: 초깃값을 포함한 예제
const array = [1, 2, 3];
const sum = reduce((acc, a) => acc + a, 0, array);
console.log(sum); // [const sum: number]
// 6

const strings = ['a', 'b', 'c'];
const abc = reduce((acc, a) => `${acc}${a}`, '', strings);
console.log(abc); // [const abc: string]
// abc

// 두 번째 reduce 함수: 초깃값을 포함하지 않은 예제
const array2 = [1, 2, 3];
const sum2 = reduce((a, b) => a + b, array2);
console.log(sum2); // [const sum2: number]
// 6

const words = ['hello', 'beautiful', 'world'];
const sentence = reduce((a, b) => `${a} ${b}`, words);
console.log(sentence); // [const sentence: string]
// hello beautiful world

const array3 = [3, 2, 1];
const str = reduce((a, b) => `${a}${b}`, array3);
console.log(str); // [const str: string]
// 321
```

`"hello beautiful world"` 예시와 같은 문제에서는 특히 초깃값을 생략하는 패턴을 사용할 때 코드를 더욱 간결하게 만들고 가독성을 높일 수 있다.

#### reduce의 에러 관리

자바스크립트의 `reduce`는 초깃값을 생략한 상태에서 호출되면 배열의 첫 요소를 초깃값으로 삼아 순회를 시작한다. 만약 빈 배열이라면 초깃값으로 삼을 요소조차 없고 값을 산출할 수 없는 상황이므로 `TypeError`를 던져 처리를 중단한다. `Array.prototype.reduce`, `IterableHelpers`의 `reduce` 그리고 이 절에서 구현한 `reduce` 모두 초깃값을 생략한 상황에서 빈 배열이나 빈 이터러블을 만났을 때 에러를 전파하도록 구현되어 있다. 그렇다면 이러한 에러 처리를 어떻게 바라보고 또 어떻게 관리해야 좋을까?

첫 번째, **초깃값을 명시적으로 넣는 방법**이 있다. 이는 가장 간단한 해결 방식이다. 빈 배열이라도 `reduce`가 에러 없이 진행되며 사용자가 직접 결정한 초깃값(예: `0` 또는 `''` 등)을 반환할 수 있다. 이 방식은 '빈 배열이면 어떤 값을 반환할지'를 명확하게 정한다.

하지만 초깃값만으로는 모든 상황을 해결할 수 없다. 예를 들어 [코드 2-22a]의 `"hello beautiful world"` 같은 사례에서 초깃값을 넣으면 보조 함수(`f`)에서 `if`문으로 '빈 값이면(첫 순회)'에 대한 예외 처리를 해야 한다. 그렇게 되면 모든 순회에서 추가 조건문을 거치게 되고 코드도 복잡해진다. 결론적으로 초깃값을 넣는 방식이 적합한지 여부는 전체 로직과 보조 함수의 동작에 따라 결정해야 한다.

두 번째, **빈 배열인 경우를 미리 체크해 기본값으로 반환하는 early return 방법**이 있다. 실제로 프로그램의 정상 동작 범위에서 빈 배열이 충분히 들어올 수 있고 그때 반환할 기본값이 의미가 있다면 이 방식을 적용할 수 있다. 예를 들면 ``arr => arr.length === 0 ? '' : arr.reduce((a, b) => `${a} ${b}`)`` 와 같은 형태를 취한다. 이 방법은 `Array`, `Set`처럼 길이를 미리 알 수 있는 자료구조일 때 가능하다.

세 번째, **`try/catch`로 에러를 처리하는 방법**이 있다. 만약 빈 배열(혹은 빈 이터러블)이 프로그램의 정상 범위에 속하지 않고 초깃값 역시 사용할 이유가 없는 상황이라면 `try/catch`로 처리할 수 있다. 또는 '이 경우는 에러가 맞으니 해결이 필요하다'라는 명확한 의도 아래 에러를 그대로 던지도록 둘 수도 있다. 이렇게 '정상 범위가 아니다'라는 사실을 개발자가 인지하고 최종적으로 어딘가에서 에러를 감지하도록 준비해야 한다.

마지막으로 지연 이터레이터인 경우에는 지연 이터레이터를 `reduce`에 전달하기 전에 배열로 변환해 길이를 체크하거나, 끝까지 평가를 미루면서 `reduce`에 넘기고 에러를 처리하는 두 가지 접근이 가능하다. 전자를 택하면 '빈 배열인지 미리 파악하여 기본값을 반환'하는 로직이 가능해지고, 후자를 택한다면 '빈 이터레이터가 `reduce`에 들어가 발생한 에러를 던지거나 `try/catch`로 처리'하는 방향을 선택해야 한다. 결국 초깃값 없이 `reduce`를 사용하며 지연 이터레이터를 전달하려면, 에러 처리를 할 것인지 아니면 이상 상황이 발생하지 않는다고 가정해도 되는지를 판단해 적절한 방식으로 결정해야 한다.

이 책의 4장까지 다루는 내용 전반에서 에러 핸들링이나 옵셔널한 상황의 값 처리 등에 관한 여러 관점을 제시한다. 해당 부분을 모두 확인한 뒤 다시 이곳 내용을 살펴보면 더욱 도움이 될 것이다.

### 2.3 함수 시그니처와 중첩된 함수들의 타입 추론

지금까지는 타입을 적용한 고차 함수를 하나씩만 실행했다. 타입을 잘 정의한 함수는 함수들을 중첩하여 평가할 때도 코드 전반에서 타입 추론을 원활하게 처리한다. 고차 함수에 인자로 전달된 모든 함수의 인자 타입이 추론되므로 개발자는 직접 타입을 정의하지 않고도 안전한 코드를 작성할 수 있다.

```typescript
// [코드 2-23] map + filter + forEach
function* naturals(end = Infinity): IterableIterator<number> { /* ... */ }
function forEach<A>(f: (a: A) => void, iterable: Iterable<A>): void { /* ... */ }
function* map<A, B>(f: (a: A) => B, iterable: Iterable<A>): IterableIterator<B> { /* ... */ }
function* filter<A>(f: (a: A) => boolean, iterable: Iterable<A>): IterableIterator<A> { /* ... */ }

function printNumber(n: number) {
  return console.log(n);
}

forEach(printNumber,
  map(n => n * 10,           // [n: number]
    filter(n => n % 2 === 1, // [n: number]
      naturals(5))));

forEach(printNumber,
  filter(n => n % 2 === 1,            // [n: number]
    map(text => parseInt(text),        // [text: string]
      map(el => el.textContent!,       // [el: HTMLDivElement]
        document.querySelectorAll('div')))));
```

코드의 상단에서는 함수들의 시그니처를 정의해 타입 추론이 원활하도록 했고 실행부와 함께 살펴볼 수 있도록 구성했다. [코드 2-23]의 예시들은 주석에 표현된 것처럼 타입 추론이 잘 이루어지며 `printNumber` 함수에 `number` 타입의 인자를 전달하는 것으로 처리된다.

지금까지 함수형 고차 함수 또는 이터러블 헬퍼 함수에 타입 시스템을 적용하는 방법을 자세히 알아보았다. 이러한 개념을 활용하면 더욱 안전한 고차 함수를 만들 수 있으며 이러한 함수 세트를 잘 구성하면 안전하고 효율적이며 유연하고 생산성이 높은 함수형 프로그래밍을 구현할 수 있다.

---

## 3. 멀티패러다임 언어와 메타프로그래밍 - LISP로부터

앞서 우리는 함수형 프로그래밍에서 자주 사용하는 고차 함수에 타입을 부여하여 다형성이 높으면서도 타입 안전한 함수를 구현하는 방법을 살펴보았다. 이 절에서는 이러한 고차 함수들에 클래스를 결합하고 이터러블 패턴을 적용함으로써 데이터 스트림을 한층 가독성 높게 처리하는 구조를 만들어본다. 이러한 패턴은 이미 많은 현대 언어의 표준 라이브러리에서 널리 활용되고 있으며 개발자가 데이터 흐름을 명확하고 직관적으로 표현하는 데 큰 도움을 준다.

이번 절의 예제들에서는 제네릭과 일급 함수, 클래스, 이터러블 프로토콜 등 다양한 언어 기능을 조합해 유연하고 확장성 높은 추상화를 구축하는 과정을 살펴본다. 이를 통해 메타프로그래밍에서 얻을 법한 코드 표현력의 향상, 런타임에서의 기능 변형을 구현하고 마치 언어 자체를 확장한 듯한 경험을 얻을 수 있다.

여기서 메타프로그래밍(*Metaprogramming - 프로그램이 자기 자신이나 다른 프로그램을 데이터처럼 바라보며 분석·변형·생성하거나 실행하는 프로그래밍 기법*)이란 프로그램이 코드를 데이터로 다루면서 동적으로 조작하고 확장하는 방식으로, 전통적인 LISP 계열 언어에서 극대화되었다. 이를 활용하면 코드 구조나 평가 과정을 직접 재정의하거나 매크로를 통해 언어 구문을 자유롭게 다룰 수 있다.

타입스크립트나 현대 멀티패러다임 언어들은 LISP 계열 언어만큼 메타프로그래밍을 직접 지원하지는 않지만 앞에서 살펴본 여러 언어적 기능을 전략적으로 결합하면 메타프로그래밍의 이점을 실용적으로 구현할 수 있다. 이 절에서는 LISP 계열 언어들에서나 가능해 보였던 풍부한 추상화와 동적 변형을 멀티패러다임 언어에서 달성하는 방법과 전략을 탐구해본다.

### 3.1 Pipe Operator

그전에 잠시 미래에 다녀오겠다. 아니 어쩌면 과거일 수도 있다. [코드 2-23]에서 가져온 다음 예제 코드처럼 오른쪽 아래에서 왼쪽 위 방향으로 읽어야 하는 코드는 익숙하지 않아 가독성이 떨어질 수 있다. LISP는 지연 평가와 메타프로그래밍 측면에서 탁월한 강점이 있으므로 개발자가 직접 `pipe` 함수를 만들어 이러한 문제를 해결할 수 있다.

또한 몇몇 언어에서는 이미 Pipe Operator를 지원하여 가독성 문제를 효과적으로 완화하고 있다. 다음 예제에서 Pipe Operator를 사용한 사례를 볼 수 있다.

```typescript
// [코드 2-24] Pipe Operator
// [코드 2-23] 중...
forEach(printNumber,
  map(n => n * 10,
    filter(n => n % 2 === 1,
      naturals(5))));
// 10
// 30
// 50

// Pipe Operator (Stage 2)
naturals(5)
  |> filter(n => n % 2 === 1, %)
  |> map(n => n * 10, %)
  |> forEach(printNumber, %)
// 10
// 30
// 50
```

지금까지 작성한 고차 함수들의 인자 순서를 `map(iterable, f)`가 아닌 `map(f, iterable)`로 설계한 이유는 정통 함수형 언어들의 고차 함수 인자 순서를 따랐기 때문이다. 이렇게 설계하면 `map(f, iterable)` 순서로 함수들을 중첩해서 표현하거나 Pipe Operator로 표현하거나 커링(*Currying*)을 지원할 때 가독성을 높일 수 있다. 만일 `map(iterable, f)` 순서라면 다음과 같이 작성해야 한다.

```typescript
// [코드 2-25] 인자 순서가 반대일 때
forEach(map(filter(naturals(5), n => n % 2 === 1), n => n * 10), printNumber);

naturals(5)
  |> filter(%, n => n % 2 === 1)
  |> map(%, n => n * 10)
  |> forEach(%, printNumber)
```

확실히 [코드 2-24]의 코드가 더 가독성이 좋다. Pipe Operator 코드는 괜찮은 편이지만 고차 함수의 첫 번째 인자 자리에 `%`가 있어서 시선을 방해한다.

### 3.2 클래스와 고차 함수, 반복자, 타입 시스템을 조합하기

자바스크립트에 Pipe Operator가 도입될 가능성을 잠시 살펴보았지만 이를 마냥 기다릴 필요는 없다. 지금 바로 객체지향 패러다임의 클래스와 이터러블, 함수형 함수, 타입 시스템을 적절히 결합하여 가독성 문제를 해결해보겠다.

#### 제네릭 클래스로 Iterable 확장하기

먼저 `Iterable`을 확장한 클래스를 만들기 위해 [코드 2-26]과 같은 제네릭 클래스를 만들었다. `FxIterable<A>`라고 작성하여 제네릭 클래스로 정의하고 내부적으로 `iterable: Iterable<A>` 프로퍼티를 갖도록 했다.

```typescript
// [코드 2-26] FxIterable<A> 클래스 정의
class FxIterable<A> {
  private iterable: Iterable<A>;
  constructor(iterable: Iterable<A>) {
    this.iterable = iterable;
  }
}
```

[코드 2-27]에서는 `private iterable: Iterable<A>`와 같은 형태로 접근 제어자(`private`)를 생성자 매개변수에 직접 명시했다. 이를 통해 필드를 정의하는 코드와 값을 할당하는 코드를 생략하고도 `iterable` 필드가 클래스 내부에 자동으로 생성된다. 이 방법으로 클래스 정의를 간결하게 만들 수 있다.

```typescript
// [코드 2-27] FxIterable<A> 간결한 클래스 정의
class FxIterable<A> {
  constructor(private iterable: Iterable<A>) {}
}
```

`FxIterable<A>`의 타입 파라미터 `A`는 `FxIterable` 클래스의 인스턴스를 생성하는 시점에 전달하는 `iterable` 인자의 타입에 따라 결정된다. 이는 제네릭 함수의 타입 파라미터가 함수 호출 시점에 인자 타입에 따라 정해지는 방식과 유사하다.

이제 이 제네릭 클래스에 다양한 고차 함수들을 메서드로 추가할 수 있다.

#### FxIterable<A>에 map 메서드 추가하기

다음으로 `FxIterable` 클래스에 `map` 메서드를 추가하고 이전에 작성한 `map` 함수를 활용하여 메서드를 구현해보겠다.

```typescript
// [코드 2-28] FxIterable<A>에 map 메서드 추가
class FxIterable<A> {
  constructor(private iterable: Iterable<A>) {}
  map<B>(f: (a: A) => B): FxIterable<B> {
    return new FxIterable(map(a => f(a), this.iterable));
  }
}

const mapped = new FxIterable(['a', 'b'])
  .map(a => a.toUpperCase())
  .map(b => b + b);
// [const mapped: FxIterable<string>]
// [a: string]
// [b: string]
```

`map` 메서드는 `this.iterable`에 `map(f)`를 적용한 이터러블 이터레이터를 만든 후 `FxIterable<B>`를 생성하여 반환한다. `FxIterable` 클래스의 인스턴스는 체이닝 방식으로 `map`을 연속적으로 실행할 수 있다.

이를 통해 코드를 위에서 아래로 읽을 수 있으며 제네릭을 잘 활용하여 타입 추론도 원활하게 된다. `mapped`는 `FxIterable<string>`의 인스턴스이고 `a`는 `string`이다.

#### `fx(iterable: Iterable<A>): FxIterable<A>`로 간결하게 표현하기

코드에서 `new FxIterable(['a', 'b'])` 부분을 조금 더 간결하게 변경해보겠다. `FxIterable`의 인스턴스를 쉽게 생성하기 위한 헬퍼 함수 `fx`를 추가한다.

```typescript
// [코드 2-29] fx 헬퍼 함수 추가
function fx<A>(iterable: Iterable<A>): FxIterable<A> {
  return new FxIterable(iterable);
}

const mapped2 = fx(['a', 'b'])
  .map(a => a.toUpperCase())
  .map(b => b + b);
// [const mapped2: FxIterable<string>]
```

이제 더욱 간결하게 작성할 수 있으며 가독성도 향상되었다.

#### filter, forEach 메서드 만들기

이번에는 `filter`와 `forEach` 메서드를 추가해보겠다.

```typescript
// [코드 2-30] FxIterable<A>에 filter, forEach 메서드 추가
class FxIterable<A> {
  constructor(private iterable: Iterable<A>) {}
  map<B>(f: (a: A) => B): FxIterable<B> {
    return new FxIterable(map(f, this.iterable));
  }
  filter(f: (a: A) => boolean): FxIterable<A> {
    return new FxIterable(filter(f, this.iterable));
  }
  forEach(f: (a: A) => void): void {
    return forEach(f, this.iterable);
  }
}
```

[코드 2-29]에서 정의한 `fx` 함수를 활용하면 `FxIterable` 내부 코드를 더 간결하게 표현할 수 있다.

```typescript
// [코드 2-30a] new FxIterable(...)도 fx(...)로 간결하게 변경
class FxIterable<A> {
  constructor(private iterable: Iterable<A>) {}
  map<B>(f: (a: A) => B): FxIterable<B> {
    return fx(map(f, this.iterable));
  }
  filter(f: (a: A) => boolean): FxIterable<A> {
    return fx(filter(f, this.iterable));
  }
  forEach(f: (a: A) => void): void {
    return forEach(f, this.iterable);
  }
}
```

이제 `forEach`로 순회하여 출력 효과를 만들 수 있다.

```typescript
// [코드 2-31] map, forEach 사용 예제
fx(['a', 'b'])
  .map(a => a.toUpperCase())
  .map(a => a + a)
  .forEach(a => console.log(a));
// AA
// BB
```

이제 앞서 작성했었던 [코드 2-24]를 `fx`를 활용하여 작성해보겠다.

```typescript
// [코드 2-32] naturals, filter, map, forEach
// 함수 중첩
forEach(printNumber,
  map(n => n * 10,
    filter(n => n % 2 === 1,
      naturals(5))));

// 파이프 오퍼레이터
naturals(5)
  |> filter(n => n % 2 === 1, %)
  |> map(n => n * 10, %)
  |> forEach(printNumber, %)

// 체이닝
fx(naturals(5))
  .filter(n => n % 2 === 1)
  .map(n => n * 10)
  .forEach(printNumber);
// 10
// 30
// 50
```

이제 꽤 완성된 모습이다. 예제를 보면 함수 중첩과 파이프 오퍼레이터를 사용한 방식도 충분히 가독성이 있지만 체이닝 방식은 현대 언어의 접근 방식과 매우 유사하여 익숙하기도 할뿐더러 가독성이 뛰어나다. 체이닝 방식은 연속적인 메서드 호출을 통해 데이터 변환 방식을 직관적으로 표현할 수 있으며 각 단계가 명확하게 드러나기 때문에 코드의 흐름을 쉽게 파악할 수 있다.

특히 자바스크립트의 `Array` 메서드 체이닝이나 자바의 스트림 API와 같이 이미 친숙한 패턴을 활용하기 때문에 개발자들이 쉽게 이해하고 사용할 수 있다. 이는 앞서 말했듯이 멀티패러다임 언어들에서 차용하고 있는 방식이다.

또한 체이닝 방식은 사용할 수 있는 메서드를 IDE에서 힌트로 제공받을 수 있다. 따라서 개발자들이 코드를 작성할 때 더욱 편리하게 작업할 수 있는 장점도 있다.

#### reduce 메서드 만들기

이번에는 `reduce` 메서드를 추가해보겠다.

```typescript
// [코드 2-33] FxIterable<A>에 reduce 메서드 추가
class FxIterable<A> {
  constructor(private iterable: Iterable<A>) {}
  // ... 메서드 생략 ...
  reduce<Acc>(f: (acc: Acc, a: A) => Acc, acc: Acc): Acc {
    return reduce(f, acc, this.iterable);
  }
}
```

이처럼 간단하게 추가할 수 있다. 다만 `reduce`는 앞서 구현한 것처럼 메서드 오버로드를 통해 두 가지 호출 방식을 지원해야 한다. 타입스크립트에서 메서드 오버로드는 함수 오버로드와 동일한 방식으로 처리된다. 즉 함수나 메서드의 시그니처를 여러 개 정의하고 실제 구현은 하나만 제공하는 방식이다.

```typescript
// [코드 2-34] reduce 메서드 오버로드
class FxIterable<A> {
  constructor(private iterable: Iterable<A>) {}
  // ... 메서드 생략 ...
  reduce<Acc>(f: (acc: Acc, a: A) => Acc, acc: Acc): Acc;       // ①
  reduce<Acc>(f: (a: A, b: A) => Acc): Acc;                     // ②
  reduce<Acc>(f: (a: Acc | A, b: A) => Acc, acc?: Acc): Acc {
    return acc === undefined
      ? reduce(f, this.iterable)   // ③
      : reduce(f, acc, this.iterable); // ④
  }
}
```

메서드의 시그니처 부분(①, ②)과 구현 부분(③, ④)을 설명하면 다음과 같다.

- **① `reduce<Acc>(f: (acc: Acc, a: A) => Acc, acc: Acc): Acc`**: 이 시그니처는 `reduce` 메서드가 초깃값 `acc`를 포함하여 호출될 때 사용되며 제네릭 타입 `Acc`를 사용하여 누적값의 타입을 정의한다. 함수 `f`는 누적값 `acc`와 이터러블의 각 요소 `a`를 받아 새로운 누적값을 반환하는 함수이다. `A`는 `private Iterable<A>`의 요소 타입이다.
- **② `reduce<Acc>(f: (a: A, b: A) => Acc): Acc`**: 이 시그니처는 `reduce` 메서드가 초깃값 없이 호출될 때 사용된다. 이때 이터러블의 첫 번째 요소가 초깃값으로 사용되고 `A`는 `private Iterable<A>`의 요소 타입이다. 제네릭 타입 `Acc`는 누적값의 타입이다.
- **③ `acc`가 `undefined`인 경우**: `reduce(f, this.iterable)`을 호출한다. 이때 `reduce` 함수 내부에서 이터러블의 첫 번째 요소를 초깃값으로 처리한다.
- **④ `acc`가 `undefined`가 아닌 경우**: `reduce(f, acc, this.iterable)`을 호출한다. 이때는 명시된 `acc`가 초깃값으로 사용된다.

이제 `reduce` 메서드는 다음과 같이 초깃값이 있을 때와 없을 때 모두 유연하게 사용할 수 있다.

```typescript
// [코드 2-35] reduce 메서드 사용 예제
// 초깃값이 없을 때
const num = fx(naturals(5))             // FxIterable<number> (1, 2, 3, 4, 5)
  .filter(n => n % 2 === 1)             // FxIterable<number> (1, 3, 5)
  .map(n => n * 10)                     // FxIterable<number> (10, 30, 50)
  .reduce((a, b) => a + b);             // [a: number] [b: number]
console.log(num); // [num: number]
// 90

// 초깃값이 있을 때
const num2 = fx(naturals(5))            // FxIterable<number> (1, 2, 3, 4, 5)
  .filter(n => n % 2 === 1)             // FxIterable<number> (1, 3, 5)
  .map(n => n * 10)                     // FxIterable<number> (10, 30, 50)
  .reduce((a, b) => a + b, 10);         // [a: number] [b: number]
console.log(num2); // [num2: number]
// 100
```

이로써 우리는 `map`, `filter`, `reduce`, `forEach` 메서드를 구현하여 체이닝을 활용한 가독성 좋고 안전하며 유지보수하기 쉬운 코드를 작성할 수 있게 되었다.

### 3.3 LISP(클로저)에서 배우기 - 코드가 데이터, 데이터가 코드

잠시 LISP에 대해 이야기하겠다. LISP는 독특한 문법과 철학을 바탕으로 프로그래밍 언어 역사에서 매우 중요한 위치를 차지하고 있다. LISP의 가장 큰 특징은 '코드가 데이터이고 데이터가 코드'라는 개념이다. 이를 통해 프로그래밍 언어의 구문을 데이터 구조로 표현하고 조작할 수 있다.

결과적으로 프로그램이 동적으로 새로운 코드를 생성하고 실행할 수 있어 메타프로그래밍을 비롯한 다양한 고급 기법을 손쉽게 구현할 수 있다. 이러한 특성은 코드의 유연성과 확장성을 극대화할 수 있는 기반이 된다.

이번 절에서는 LISP 계열 언어인 클로저(*Clojure*)를 예로 들어 LISP의 기본 개념과 매크로, 메타프로그래밍 등에 대해 알아보겠다. 나아가 이러한 아이디어를 타입스크립트로 적용해보며 멀티패러다임 언어에 대한 관점을 확장해보겠다.

#### 클로저

클로저는 리치 히키(*Rich Hickey*)가 2007년에 개발한 함수형 프로그래밍 언어로 LISP 계열에 속한다. JVM 위에서 실행되며 현대적인 LISP 언어의 특성과 함께 자바의 강력한 라이브러리 생태계를 활용할 수 있다. 클로저는 불변성과 일급 함수를 강조하며 동시성 프로그래밍과 관련된 강력한 기능들을 지원하는 언어이다. 또한 클로저는 코드와 데이터를 동일하게 취급한다. 클로저의 이러한 특성은 메타프로그래밍을 가능하게 하며 코드의 유연성과 확장성을 높인다.

#### 클로저 시작하기 - S-표현식

LISP의 S-표현식은 리스트 형태의 구문 표현을 의미한다. 이를 통해 코드와 데이터를 동일한 구조(리스트)로 다룰 수 있다. 이는 곧 코드 자체를 데이터로 조작할 수 있다는 이야기이다. 예를 들어 `(+ 1 2)`는 LISP에서 숫자 1과 2를 더하는 코드이자 동시에 리스트 형태의 데이터이다.

```clojure
;; [코드 2-36] 실행될 코드가 곧 리스트
(+ 1 2)
```

- 첫 번째 요소: 연산자(함수) `+`
- 나머지 요소: 피연산자 `1`과 `2`

[코드 2-36]은 두 수를 더하는 표현식인 동시에 리스트 구조로 해석할 수 있다. LISP 계열 언어에서는 함수 호출이 리스트 구조로 이루어지며 리스트의 첫 번째 요소가 함수, 그 뒤 요소들이 함수에 전달할 인자이다.

이해를 돕기 위해 이를 타입스크립트로 단순화해 표현하면 다음과 같다.

```typescript
// [코드 2-37] 리스트는 값
[add, 1, 2]
```

하나의 배열에 두 수를 더하는 `add` 함수와 나머지 요소인 `1`과 `2`가 담겨 있다. `[add, 1, 2]` 자체는 배열이고 데이터이다. 이때 이 데이터를 평가하는 함수가 있다면 데이터를 코드로 만들어 평가할 수 있을 것이다.

```typescript
// [코드 2-37a] 리스트를 평가하는 함수
type Evaluatable<A, B> = [(...args: A[]) => B, ...A[]]; // ①
function evaluation<A, B>(expr: Evaluatable<A, B>) {     // ②
  const [fn, ...args] = expr;
  return fn(...args);
}

const add = (a: number, b: number) => a + b;
const result: number = evaluation([add, 1, 2]);           // ③
console.log(result); // 3
```

[코드 2-37a]는 타입스크립트로 함수를 호출하는 과정을 리스트 형태의 데이터로 표현하고 이를 평가하는 방식으로 LISP의 '코드가 데이터'라는 개념 일부를 설명하는 코드이다.

- **① `Evaluatable<A, B>` 타입 정의**: 첫 번째 요소는 함수 타입 `((...args: A[]) => B)`이며 그 뒤로 함수의 인자에 해당하는 값들이 이어지는 형태를 정의했다. `[add, 1, 2]`는 함수 `add`와 그에 전달할 인자 `1`, `2`를 담은 배열 구조를 타입으로 명확히 표현한 것이다.
- **② `evaluation` 함수**: `evaluation` 함수는 `Evaluatable<A, B>` 타입의 값을 입력받는다. 구조 분해 할당을 이용해 첫 번째 요소를 함수(`fn`), 나머지 요소들을 인자 배열(`args`)로 추출한다. 이어서 `fn(...args)`를 호출해 그 결과를 반환한다. 이는 리스트 형태로 표현된 '코드'를 실제 함수 호출로 '평가'하는 과정이다.
- **③ 사용 예제**: `add` 함수는 두 수를 더하는 단순한 함수이다. `[add, 1, 2]`라는 배열은 '`add` 함수를 인자 `1`과 `2`로 호출한다'는 의미를 갖는 데이터 구조이다. 이를 `evaluation([add, 1, 2])`로 평가하면 내부적으로 `add(1, 2)`가 실행되어 결과 `3`을 반환한다.

이로써 데이터(배열)로 표현된 코드(함수 호출)를 `evaluation` 함수를 통해 실제로 실행해볼 수 있다.

이 타입스크립트 예제는 런타임 시점에만 코드 구조를 데이터로 활용한다. 반면 LISP는 컴파일 타임에도 코드를 데이터로 다룰 수 있다. 따라서 코드 자체를 변환하고 최종적으로 런타임에 실행될 코드를 재구성하는 등 더욱 강력한 조작 능력을 갖추고 있다. 이에 대한 자세한 내용은 이후에 다시 살펴보겠다.

### 3.4 클로저에서 map이 실행될 때

다음 코드는 리스트의 각 요소에 10을 더한 값을 반환하는 예이다.

```clojure
;; [코드 2-38] map 사용 예제
(map #(+ % 10) [1 2 3 4])
```

이 코드는 다음과 같이 동작한다.

- 첫 번째 요소: 함수 `map`
- 두 번째 요소: 익명 함수 `#(+ % 10)` (현재 요소에 10을 더하는 함수)
- 세 번째 요소: 벡터 `[1 2 3 4]` (클로저에서 `[]`는 벡터, `()`는 리스트를 의미)

`map` 함수는 주어진 함수 `#(+ % 10)`를 벡터의 각 요소에 적용한 결과를 반환한다. 이를 평가하면 결과는 `(11 12 13 14)`라는 리스트 형태의 지연 시퀀스가 된다. 다만 아직 어디에도 소비되지 않았으므로 실제로 값이 필요할 때 평가가 완료된다.

`#(+ % 10)`은 리더 매크로에 의해 `(fn [x] (+ x 10))` 형태의 익명 함수로 확장된다. 클로저에서는 함수 정의도 리스트 형태로 표현하므로 함수 정의 구문 자체를 '코드이자 데이터 구조'로 다룰 수 있다. 여기서 리더 매크로란 클로저와 같은 언어가 소스 코드를 읽는 reader 단계에서 특정 기호나 패턴을 미리 정해진 형태의 다른 코드로 치환하는 기능을 말한다.

#### 앞에서부터 두 개의 값 꺼내기

다음 코드는 `let`과 구조 분해를 통해 `map`의 결과에서 앞의 두 값을 추출하여 출력하는 예이다.

```clojure
;; [코드 2-39] let과 구조 분해
(let [[first second] (map #(+ % 10) [1 2 3 4])]
  (println first second))
;; 11 12
```

`(map #(+ % 10) [1 2 3 4])`를 통해 `(11 12 13 14)` 형태의 지연 시퀀스가 생성된다. `let`에서 `[first second]`로 구조를 분해하면 처음 두 요소(11과 12)를 추출하면서 필요한 부분만 평가한다. `map`은 지연 평가되므로 실제로 필요할 때만 요소를 계산한다. `println`을 통해 `first`와 `second` 값을 출력하면 결과는 `11 12`이다. 참고로 `;;`는 클로저의 주석 문법이다.

LISP 계열 언어에서는 코드가 리스트 형태로 표현되며 리스트는 평가되기 전까지는 단순한 데이터 구조에 불과하다. 평가 과정이 시작되면 이 리스트는 실제 함수 호출이나 로직으로 해석되어 실행된다. 예를 들어 `#(+ % 10)`에 의해 만들어지는 `(fn [x] (+ x 10))`이라는 익명 함수 역시 아직 평가되지 않은 '구문(코드)'이자 리스트 형태로 구성된 '값'이다.

이러한 값이 `(map f list)`와 같은 또 다른 리스트 구조의 코드와 결합되는 과정에서 클로저는 필요한 시점까지 평가를 지연시킨다. 그리고 마침내 평가가 필요한 순간이 되면 중첩된 리스트들의 조합을 실제 로직으로 완성하고 실행한다. 이처럼 코드와 데이터를 동일한 형태로 다루며 필요할 때 점진적으로 평가하는 것이 LISP 계열 언어의 특징이자 핵심적인 강점 중 하나이다.

### 3.5 멀티패러다임 언어에서 사용자가 만든 코드이자 클래스를 리스트로 만들기

클로저로 만든 [코드 2-39]와 동일한 시간 복잡도(지연 평가 지원)를 가지면서 동일한 표현력을 가지도록 `FxIterable` 클래스를 확장해보겠다. `FxIterable`을 어떻게 변경해야 할까? `let`과 `[first second]`와 같이 구조 분해 할당을 할 수 있도록 `FxIterable`을 `Array`로 변환하는 메서드를 만들어야 할까? 일단 코드를 작성해보겠다.

```typescript
// [코드 2-40] toArray() 메서드 추가
class FxIterable<A> {
  constructor(private iterable: Iterable<A>) {}
  // ... 메서드 생략 ...
  toArray(): A[] {                                              // ①
    return [...this.iterable];
  }
}

const [first, second] = fx([1, 2, 3, 4]).map(a => a + 10).toArray(); // ②
console.log(first, second); // 11 12                             // ③
```

이 코드는 다음과 같이 동작한다.

- ① 추가한 `toArray()` 메서드는 내부 이터러블을 배열로 변환하여 반환한다. `return [...this.iterable];` 문장을 통해 이터러블 객체를 전개 연산자를 사용해 배열로 변환한다.
- ② `fx` 함수는 `FxIterable` 인스턴스를 생성한다. `map()` 메서드를 사용하여 각 요소에 10을 더한 후 `toArray()` 메서드를 통해 변환된 배열을 반환한다.
- ③ 구조 분해 할당을 통해 배열의 첫 번째와 두 번째 값을 `first`와 `second` 변수에 바인딩하면 출력 결과는 11과 12가 된다.

원하는 결과는 얻었지만 `map(...)` 뒤에 `.toArray()`라는 코드가 추가된 점과 `toArray()`를 할 때 모든 요소를 평가하여 길이가 4인 배열이 만들어지는 점이 [코드 2-39]와 비교하여 아쉬운 점이다.

이 문제를 어떻게 해결할 수 있을까? 우리는 이미 답을 알고 있다. `FxIterable` 클래스를 다음과 같이 확장하면 `FxIterable`을 LISP가 추구하는 리스트로 만들 수 있다. 바로 `FxIterable`을 지금까지 계속 다뤘던 이터레이션 프로토콜을 따르는 값으로 만드는 것이다.

```typescript
// [코드 2-41] LISP의 리스트 같은 이터러블
class FxIterable<A> {
  constructor(private iterable: Iterable<A>) {}
  [Symbol.iterator]() {
    return this.iterable[Symbol.iterator]();
  }
  // ... 메서드 생략 ...
}

const [first, second] = fx([1, 2, 3, 4]).map(a => a + 10);
console.log(first, second); // 11 12
```

이 문제를 해결하는 데는 `FxIterable`을 이터러블로 만드는 것만으로 충분하다. `FxIterable` 클래스에 `[Symbol.iterator]()` 메서드를 구현하여 `this.iterable`을 이터레이터로 변환하여 반환한다. 그러면 `toArray()` 메서드 없이도 `first`와 `second` 값을 추출할 수 있다. 따라서 두 값을 추출하기 위해 10을 더하는 연산이 단 두 번만 실행된다.

### 3.6 LISP의 확장성 - 매크로와 메타프로그래밍

다시 LISP로 돌아와 생각해보자. 아직 평가되지 않은 상태에서 10을 더할 리스트가 있다면 여기에 동적으로 다른 코드를 추가할 수 있다. 예를 들어 홀수만 제거한다거나 특정 요소를 제외하는 등의 새 기능을 얼마든지 붙일 수 있다.

개발자가 특정 로직으로 요소를 제거하는 함수를 만들고 이를 리스트의 첫 번째 요소로 둔다면, 그 리스트는 마치 새로운 연산자와 함수로 구성된 코드처럼 동작한다. 이러한 과정을 통해 개발자가 스스로 언어의 기능을 확장하고 `let`과 같은 기존 언어 기능과 자연스럽게 연계할 수 있다.

다음은 `reject`라는 함수를 직접 정의하여 기존 언어에 없던 연산을 클로저에 추가하는 예이다.

```clojure
;; [코드 2-42] reject 함수 적용
(defn reject [pred coll]                                        ;; ①
  (filter (complement pred) coll))

(let [[first second] (reject odd? (map #(+ % 10) [1 2 3 4 5 6]))] ;; ②
  (println first second))                                         ;; ③
;; 12 14                                                          ;; ④
```

[코드 2-42]는 다음과 같이 동작한다.

1. `reject` 함수는 `pred` 조건을 만족하지 않는 요소들만 남기기 위해 `filter`와 `complement`를 사용한다.
2. 3행의 코드를 오른쪽 끝부터 살펴보면 `(map #(+ % 10) [1 2 3 4 5 6])`은 각각에 10을 더해 `(11 12 13 14 15 16)`을 생성한다. `reject odd?`는 홀수인 요소를 제거하므로 `(12 14 16)`을 반환한다. `let`에서 `[first second]` 구조 분해를 통해 `(12 14 16)` 중 처음 두 요소를 `first`와 `second`에 바인딩한다.
3. `println`을 통해 `first`와 `second` 값을 출력하면 ④ `12 14`를 결과로 확인할 수 있다.

LISP에서는 개발자가 원하는 로직을 직접 함수로 정의하여 언어 기능에 자연스럽게 통합한다. 또한 코드 평가를 지연시키는 LISP의 특성 덕분에 이를 유연하게 확장할 수 있음을 보여준다.

#### 매크로

LISP 계열 언어에서 매크로는 단순한 텍스트 치환이 아니라 코드(리스트 형태)를 입력받아 코드(리스트 형태)를 반환하는 하나의 함수라 할 수 있다. 매크로는 컴파일 타임에 작동하여 코드가 아직 실행되지 않은 '구문' 상태일 때 원하는 형태로 재구성한다. 이를 통해 최종적으로 실행될 코드를 유연하게 동적으로 만들어내고 원하는 새로운 문법이나 기능을 언어에 손쉽게 추가할 수도 있다.

여기서는 유명한 예제인 `unless` 매크로를 예로 들어보겠다.

```clojure
;; [코드 2-43] unless 매크로
(defmacro unless [test body]
  `(if (not ~test) ~body nil))
```

코드의 `unless` 정의를 보면 `test`와 `body`는 매크로에게 전달되는 '코드 형태의 인자'이다. 함수 호출에서는 인자들이 먼저 평가된 뒤 함수에 전달되지만 매크로에서는 인자들이 평가되지 않은 '원본 코드 형태'로 주어진다. 이 말은 `unless` 매크로가 `test`와 `body`를 마치 함수의 인자처럼 받되, 그 값을 실행하지 않고 코드 구조(리스트) 자체로 취급한다는 의미이다.

예를 들어 다음 코드를 살펴보자.

```clojure
;; [코드 2-44] unless 매크로 사용 예제
(unless false
  (println "조건이 거짓이므로 이 문장은 실행됩니다."))
```

여기서 `false`는 [코드 2-43]의 `unless` 매크로에서 `test` 인자로, `(println "조건이 거짓이므로 이 문장은 실행됩니다.")`는 `body` 인자로 전달된다. 이때 이들은 평가되지 않은 코드 조각(리스트) 형태 그대로 매크로에 넘어간다. 그리고 `unless` 매크로는 이 코드 조각들을 활용해 컴파일 타임에 다음과 같은 새로운 코드를 생성한다.

```clojure
;; [코드 2-45] unless 매크로 변환 후 실제로 실행될 코드
(if (not false)
  (println "조건이 거짓이므로 이 문장은 실행됩니다.")
  nil)
```

결국 `unless` 매크로는 `test`와 `body`라는 코드를 입력받아 최종적으로 실행될 새로운 코드 조각을 반환하는 코드 변환기이다. 컴파일러는 반환된 코드를 실제 실행 코드로 사용하게 되므로 매크로를 통해 언어가 제공하지 않는 새로운 구문이나 기능을 마음껏 만들어낼 수 있다.

정리하자면 `test`와 `body`는 매크로에 전달되는 '코드 조각'이며 `unless` 매크로는 코드 조각들을 재구성하여 컴파일 타임에 새로운 코드를 '뱉어내는' 역할을 한다. 이로써 개발자는 자신의 언어 확장 도구를 손쉽게 확보할 수 있다. 이는 LISP 계열 언어가 지닌 강력한 메타프로그래밍 능력 중 하나이다.

#### ->> 매크로

이번에는 `reject` 함수를 적용한 코드를 파이프라인 형태로 표현해보겠다. 클로저에서는 파이프라인 형태의 코드를 표현하기 위해 `->>` 매크로를 사용한다.

```clojure
;; [코드 2-46] 파이프라인으로 표현
(let [[first second] (->> [1 2 3 4 5 6]          ;; ①, ②
                          (map #(+ % 10))         ;; ③
                          (reject odd?))]         ;; ④
  (println first second))                         ;; ⑤
;; 12 14                                          ;; ⑥
```

이 코드는 다음과 같이 동작한다.

1. `->>` 매크로는 첫 번째 인자로 받은 `[1 2 3 4 5 6]`을 그다음 함수의 마지막 인자로 전달한다.
2. `map #(+ % 10)`은 `[1 2 3 4 5 6]`의 각 요소에 10을 더하여 `(11 12 13 14 15 16)`을 생성한다.
3. `reject odd?`는 `map`의 결과 리스트에서 홀수를 제거하여 `(12 14 16)`을 반환한다.
4. `let`을 사용하여 `[first second]`에 리스트의 처음 두 값을 바인딩한다.
5. `println`을 사용하여 `first`와 `second` 값을 출력하면 결과는 `12 14`가 된다.

이 예제는 파이프라인 매크로를 사용하여 코드의 가독성을 높이는 방법을 보여준다. 클로저에서는 `unless`나 `->>`와 같은 매크로를 개발자가 직접 정의할 수 있으며 특수문자나 기호를 활용한 표현도 가능하다. 이를 통해 `->>`와 같은 새로운 구문을 언어에 손쉽게 추가할 수 있고 쉼표 없이 괄호만 사용하는 S-표현식과 결합하여 더욱 간결한 코드를 만들어낼 수 있다. 이러한 강력한 확장성과 유연성은 프로그램의 구문을 데이터 구조로 표현하고 이를 지연된 값처럼 다룰 수 있는 LISP 계열 언어의 특성 덕분이다.

#### reject 메서드를 FxIterable에 추가하기

클로저에서 `reject` 함수를 사용하는 예제와 동일하게 동작하는 `reject` 메서드를 `FxIterable` 클래스에 추가하고 체이닝으로 표현하는 예제를 만들어보겠다.

```typescript
// [코드 2-47] FxIterable 클래스에 reject 메서드 추가
class FxIterable<A> {
  constructor(private iterable: Iterable<A>) {}
  [Symbol.iterator]() {
    return this.iterable[Symbol.iterator]();
  }
  // ... 메서드 생략 ...
  reject(f: (a: A) => boolean): FxIterable<A> {
    return this.filter(a => !f(a));
  }
}

const isOdd = (a: number) => a % 2 === 1;
```

사용 예는 다음과 같다.

```typescript
// [코드 2-48] FxIterable 체이닝과 구조 분해 할당
const [first, second] = fx([1, 2, 3, 4, 5, 6])
  .map(a => a + 10)
  .reject(isOdd);

console.log(first, second);
// 12 14
```

이 코드를 앞서 클로저에서 파이프라인과 구조 분해 할당을 사용한 [코드 2-46]과 비교해보자.

```clojure
;; [코드 2-46 다시 보기] 클로저 파이프라인과 구조 분해 할당
(let [[first second] (->> [1 2 3 4 5 6]
                          (map #(+ % 10))
                          (reject odd?))]
  (println first second))
;; 12 14
```

두 예제 모두 같은 프로그래밍 패러다임과 철학을 공유하며 이를 통해 본질적으로 동일한 의미와 가치를 구현하고 있다.

#### 코드, 객체, 함수가 협력하여 구현한 언어의 확장

우리는 명령형 문법인 구조 분해 할당(*Destructuring Assignment Syntax*), 객체지향 디자인 패턴인 메서드 체이닝 패턴(*Method Chaining Pattern*) 그리고 함수형 고차 함수(*Higher-Order Functions*)가 이터레이션 프로토콜을 매개로 긴밀하게 협력하여 마치 언어를 확장한 것 같은 높은 수준의 추상화와 유연성을 확보하는 과정을 살펴보았다.

```typescript
// [코드 2-48a] FxIterable 체이닝과 구조 분해 할당
const [first, second] = fx([1, 2, 3, 4, 5, 6])
  .map(a => a + 10)
  .reject(isOdd);
```

위 예제 코드를 다음과 같이 분류하여 각각의 역할을 해석할 수 있다.

- **구조 분해 할당**: `const [first, second]`
- **객체지향 메서드 체이닝 패턴**: `fx().map().reject()`
- **함수형 고차 함수와 LISP**: `map = (f: (a: A) => B, iterable: Iterable<A>) => Iterable<B>`

[코드 2-48a]는 이 외에도 명령형 코드인 제너레이터, 객체지향 패턴인 이터레이터, 일급 함수, 클래스, 제네릭과 타입 추론 등의 개념과 기능들이 서로 상호작용하며 많은 가치와 가능성을 담아내고 있다.

또한 이 코드는 특정 도메인이나 문제를 해결하는 구현체가 아니라 어디에서나 사용될 수 있는 범용적인 언어의 면모를 보여준다. 기존 언어의 설계나 철학에서 벗어나지 않았기 때문에 언어의 컴파일 타임 타입 처리와 런타임 에러 처리와도 잘 맞물리며 앞으로 출시될 언어의 신규 기능들과도 문제없이 상호작용할 것이다.

결론적으로 이 코드는 멀티패러다임적으로 구현되었으며 동시에 멀티패러다임 언어가 지원할 모든 기능과 상호작용이 가능할 범용적인 코드이다.

### 3.7 런타임에서 동적으로 기능 확장하기

#### to로 확장하고 객체지향적인 객체와 호흡하기

앞서 우리는 `FxIterable`에 `toArray()`를 만들었다. 그러고 나서 `FxIterable`을 이터러블로 만들었다. `FxIterable`이 이터러블이기 때문에 전개 연산자를 써서 `Array`로 변환할 수 있어 `toArray()`가 반드시 필요한 건 아니다. 하지만 `toArray()`를 이용해서 `Array`로 변환하면 체이닝을 이어갈 수 있다는 특징이 있다. 따라서 `toArray()`를 사용하는 것이 적합한 상황도 있다.

```typescript
// [코드 2-49] toArray() 체이닝
const sorted = fx([5, 2, 3, 1, 4, 5, 3])
  .filter(n => n % 2 === 1)
  .map(n => n * 10)
  .toArray()                  // Array<number>로 변환
  .sort((a, b) => a - b);    // Array.prototype.sort로 오름차순으로 정렬
console.log(sorted);
// [10, 30, 30, 50, 50]

const sorted2 = [...fx([5, 2, 3, 1, 4, 5, 3])
  .filter(n => n % 2 === 1)
  .map(n => n * 10)
]
  .sort((a, b) => a - b);
console.log(sorted2);
// [10, 30, 30, 50, 50]
```

`sorted`는 `toArray()` 메서드를 사용하여 `FxIterable` 객체를 배열로 변환한 후 배열의 `sort` 메서드를 사용하여 요소를 정렬한다. 반면 `sorted2`는 가독성을 비교하기 위해 전개 연산자를 사용했는데 대괄호와 괄호가 중첩되면서 가독성이 떨어지는 면이 있다. 코드의 흐름이 `map`까지 진행되었다가 다시 전개 연산자의 시작 부분으로 올라가고 이후 대괄호가 닫히는 부분으로 돌아가 `sort`를 보게 되기 때문이다. 반면 메서드 체이닝은 순차적으로 읽히고 동작하기 때문에 가독성이 더 좋다.

다음은 개발자가 필요할 때 `toArray`처럼 `FxIterable`을 다른 타입으로 만드는 메서드를 동적으로 확장할 수 있도록 `to`라는 메서드를 제공하는 예이다.

```typescript
// [코드 2-50] 동적으로 컨버터 생성을 가능하게 하는 to 메서드
class FxIterable<A> {
  constructor(private iterable: Iterable<A>) {}
  [Symbol.iterator](): Iterator<A> {
    return this.iterable[Symbol.iterator]();
  }
  // ... 메서드 생략 ...
  to<R>(converter: (iterable: Iterable<A>) => R): R {
    return converter(this.iterable);
  }
}

const sorted = fx([5, 2, 3, 1, 4, 5, 3])
  .filter(n => n % 2 === 1)
  .map(n => n * 10)
  .to(iterable => [...iterable])        // iterable을 받아 전개 연산자로 배열로 변환
  .sort((a, b) => a - b);               // [Array<number>.sort(compareFn?: ...): number[]]
console.log(sorted); // [10, 30, 30, 50, 50]
// const sorted: number[]
```

`Array`로 변환하고 타입도 `Array`로 잘 추론되어 메서드 체이닝을 안전하게 이어갔으며 배열을 정렬하는 고차 함수 `sort`의 `compareFn`의 인자 타입도 `number`로 잘 추론되고 있다.

사실 `FxIterable`은 자체로 곧 `Iterable`이므로 다음과 같이 `this`만을 넘기도록 구현해도 동일하게 동작한다.

```typescript
// [코드 2-51] this로 변경
class FxIterable<A> {
  constructor(private iterable: Iterable<A>) {}
  [Symbol.iterator](): Iterator<A> {
    return this.iterable[Symbol.iterator]();
  }
  // ... 메서드 생략 ...
  filter(f: (a: A) => boolean) {
    return fx(filter(f, this));            // <- return fx(filter(f, this.iterable));
  }
  toArray() {
    return [...this];                      // <- return [...this.iterable];
  }
  to<R>(converter: (iterable: this) => R): R {
    return converter(this);                // <- return converter(this.iterable);
  }
}
```

`converter` 함수의 인자 타입도 `this`로 표현하여 처리했으며 `converter`에 전달한 값 역시 자기 자신인 이터러블이다. 이렇게 작성하면 코드가 간결해지는 동시에 타입 추론 역시 잘 작동하므로 메서드 체이닝을 안전하게 사용할 수 있다.

`to` 메서드를 이용하면 배열이 아닌 값으로도 변환하여 메서드 체이닝을 이어갈 수 있다.

```typescript
// [코드 2-52] Set으로 변환
const set = fx([5, 2, 3, 1, 4, 5, 3])
  .filter(n => n % 2 === 1)
  .map(n => n * 10)                              // [50, 30, 10, 50, 30]
  .to(iterable => new Set(iterable));             // Set으로 만들어지면서 중복된 요소 제거
console.log(set);
// Set(3) {50, 30, 10}

const size = fx([5, 2, 3, 1, 4, 5, 3])
  .filter(n => n % 2 === 1)
  .map(n => n * 10)
  .to(iterable => new Set(iterable))
  .add(10)
  .add(20)
  .size;
// [Set<number>.add(value: number): Set<number>]
// set.size
console.log(size);
// 4
// [size: number]
```

이처럼 `Set`으로 변환할 수 있으며 `Set`의 `add` 메서드와 `size`를 사용하여 `4`를 출력했다. 이 과정에서 타입 추론이 정확하게 이루어져 코드 힌트를 얻으며 안전하게 체이닝을 이어갈 수 있다.

이제 `to` 메서드를 이용하여 어떤 타입으로든 변환하는 기능을 `FxIterable`에 런타임에서 동적으로 추가할 수 있으며 타입 추론도 잘 지원된다. 이를 통해 내장 객체뿐만 아니라 사용자 정의 객체와도 함께 동작할 수 있다.

#### Set의 집합 메서드와 함께 사용하기

자바스크립트의 `Set`은 집합 메서드들을 지원하므로 다음과 같이 객체지향적인 객체와 이터레이션 프로토콜을 조화롭게 결합해 멀티패러다임적으로 활용할 수 있다.

```typescript
// [코드 2-53] Set.prototype.difference
const set = fx([5, 2, 3, 1, 4, 5, 3])
  .filter(n => n % 2 === 1)
  .map(n => n * 10)
  .to(iterable => new Set(iterable))          // Set으로 변환, 중복 요소 제거: Set {50, 30, 10}
  .difference(new Set([10, 20]));              // Set에서 [10, 20]과의 차집합: Set {50, 30}
console.log([...set]);
// [50, 30]
```

예제에서는 주어진 배열에서 홀수를 필터링하고 각 요소에 10을 곱한 뒤 중복된 값을 제거한 `Set`을 생성한다. 이후 다른 `Set`과 차집합을 구하여 최종 결과를 배열로 변환해 출력한다.

#### chain으로 확장하기

`FxIterable`의 활용 폭을 한층 넓히기 위해 `to`와 유사한 개념의 또 다른 메서드를 추가해보겠다. 이번에는 이터러블을 반환하는 함수를 인자로 받아 그 결과를 다시 `FxIterable`로 이어갈 수 있는 `chain` 메서드를 도입한다. 이렇게 하면 동적으로 생성된 이터러블을 바로 체이닝에 포함시켜 다양한 변환을 유연하게 적용할 수 있다.

```typescript
// [코드 2-54] FxIterable 클래스에 chain 메서드 추가
class FxIterable<A> {
  constructor(private iterable: Iterable<A>) {}
  [Symbol.iterator](): Iterator<A> {
    return this.iterable[Symbol.iterator]();
  }
  // ... 메서드 생략 ...
  chain<B>(f: (iterable: this) => Iterable<B>): FxIterable<B> {
    return fx(f(this)); // new FxIterable(f(this));
  }
}
```

`chain`을 활용하면 이터러블을 받아 이터러블을 반환하는 어떤 함수든지 동적으로 만들어 `FxIterable`을 런타임에 확장할 수 있다.

```typescript
// [코드 2-55] chain + Set
const result = fx([5, 2, 3, 1, 4, 5, 3])
  .filter(n => n % 2 === 1)
  .map(n => n * 10)                              // [50, 30, 10, 50, 30]
  .chain(iterable => new Set(iterable))           // Set으로 중복 제거, Set도 이터러블
  .reduce((a, b) => a + b);                       // [FxIterable<number>.reduce<number>(f: ...): number]
console.log(result); // [result: number]
// 90

const result2 = fx([5, 2, 3, 1, 4, 5, 3])
  .filter(n => n % 2 === 1)
  .map(n => n * 10)                              // [50, 30, 10, 50, 30]
  .chain(iterable => new Set(iterable))           // Set으로 중복 제거, Set도 이터러블
  .map(n => n - 10)                               // [FxIterable<number>.map<number>(f: ...): FxIterable<number>]
  .reduce((a, b) => `${a}, ${b}`);                // [FxIterable<number>.reduce<string>(f: ...): string]
console.log(result2); // [result2: string]
// 40, 20, 0
```

지금까지 클래스와 고차 함수, 반복자, 타입 시스템을 조합하고 언어와 긴밀히 호흡하며 `FxIterable`을 더욱 유연하게 확장하는 방법을 살펴보았다.

`chain` 메서드를 추가함으로써 이터러블을 반환하는 함수를 동적으로 적용하거나 컬렉션을 다른 자료구조(예: `Set`)로 변환한 뒤 다시 체이닝을 이어갈 수 있게 되었다. 이를 통해 `FxIterable`은 언어와 자연스럽게 어우러져 타입 안전한 메서드 체이닝을 제공하고 구조 분해 할당 등의 언어 기능과도 매끄럽게 연동할 수 있음을 확인했다.

또한 타입스크립트의 타입 시스템을 효과적으로 활용하여 타입 추론이 원활하게 이뤄지도록 설계했기 때문에 별도의 타입 명시 없이도 안전하게 값 변환 과정과 체이닝을 이어갈 수 있다.

### 3.8 언어를 확장하는 즐거움

개발자가 언어를 즉시 확장할 수 있다는 점, 바로 이것이 메타프로그래밍이 갖는 가장 매력적인 특징이다. 객체지향 기반의 언어가 LISP 계열 언어의 메타프로그래밍 수준에 한 걸음 다가갈 수 있었던 중요한 전환점이 바로 일급 함수의 도입이었다고 생각한다.

과거에도 인터페이스와 반복자 패턴을 활용할 수는 있었다. 하지만 반복자 내부에서 외부 함수를 직접 받아 실행할 수 있는 일급 함수가 없었다면 함수형 패러다임의 다양한 함수를 구현할 수 없었을 것이다.

현대 프로그래밍 언어에서 일급 함수가 도입된 것은 비교적 최근의 일이다. 예컨대 2013년 전후로 모바일 앱 개발에 주로 사용되던 Objective-C(iOS)와 자바(안드로이드) 모두 일급 함수를 지원하지 않았다. 이후 2014년 3월에 출시된 자바 8에서 일급 함수가 도입되었지만 Objective-C는 끝내 이를 지원하지 않았다.

Objective-C에서는 2010년 즈음 블록(*Block*)이라는 유사 기능을 지원했다. 그러나 이는 람다 표현식과는 거리가 있었으며 변수 캡처 문법이 복잡하고 메모리를 직접 관리해야 했다. 또한 표준 라이브러리나 언어의 타입 시스템과도 온전히 통합되지 않아 주로 비동기 프로그래밍에서 컨텍스트를 공유하는 용도로만 제한적으로 쓰였다.

다양한 언어에서 일급 함수와 이터레이션 관련 기능을 도입한 과정은 다음과 같다.

- 자바는 2014년 자바 8에서 일급 함수와 스트림 API를 도입했다.
- 스위프트는 2014년 첫 출시부터 `Sequence`, `Iterator` 프로토콜, 일급 함수를 지원했다.
- 자바스크립트와 타입스크립트는 2015년 ES6부터 이터레이터와 제너레이터를 포함시켰다.
- 코틀린은 2016년 초기 릴리즈부터 일급 함수와 `Iterable` 인터페이스 기반 이터레이션을 제공했다.
- C#은 초기부터 `IEnumerable` 및 `IEnumerator` 인터페이스를 제공했으며 2007년 LINQ 도입으로 다양한 헬퍼 함수를 지원하기 시작했다.

정리하자면 클래스 기반 반복자 패턴에 최근 일급 함수가 결합되면서 다양한 언어들이 멀티패러다임 언어로 진화했다. 또한 이터레이션 프로토콜의 도입으로 일관되고 표준화된 방식으로 언어 기능을 확장할 수 있게 되었다. 그 결과로 개발자는 언어 스펙이나 컴파일러를 변경하지 않고도 클래스와 함수형 고차 함수, 객체지향 패턴, 제네릭, 커링, 이터러블 프로토콜 등을 유기적으로 결합하여 고도화된 추상화와 언어 확장 효과를 얻을 수 있다.

물론 타입스크립트, 스위프트, 코틀린, C#, 자바 등이 LISP 계열 언어의 메타프로그래밍과 동일한 범위나 강도를 제공하지는 않지만 충분히 풍부하고 높은 수준의 추상화를 구현할 수 있다. 게다가 이들 현대 언어들은 강력한 타입 시스템과 다양한 객체지향 프로그래밍 지원 기능을 제공하여 더욱 패턴화된 설계와 구현을 가능하게 하며 다양한 플랫폼에서 폭넓게 활용되는 주류 언어로 자리잡았다.

결과적으로 현대 멀티패러다임 언어들이 제공하는 다양한 기능을 깊이 이해하고 전략적으로 활용하는 능력은 개발자에게 강력한 무기가 된다. 탄탄한 기본기를 바탕으로 다양한 문제에 접근할 때 개발자는 더욱 창의적인 응용력을 발휘하여 문제를 효과적이고 확장성 있게 해결할 수 있을 것이다.

---

## 요약

- **타입스크립트의 타입 추론과 함수 타입**: 타입스크립트는 자바스크립트에 타입 시스템을 추가함으로써 코드의 안정성과 가독성을 높인다. 타입 추론 기능으로 명시적인 타입 선언 없이도 안전한 코드를 작성할 수 있으며 변수와 함수의 반환 타입을 자동으로 추론한다. 예를 들어 `let a = 10;`에서는 `a`가 `number`로 추론되고 `(a: number, b: number) => a + b;`와 같은 함수에서는 반환 타입이 자동으로 `number`로 결정된다.
- **변수와 상수의 타입 추론**: 변수와 상수를 초기화할 때 타입스크립트는 해당 값으로부터 타입을 추론한다. `const selected = true;`를 선언하면 `selected`는 `true`라는 리터럴 타입으로, `let checked = true;`를 선언하면 `checked`는 `boolean` 타입으로 추론된다.
- **제네릭을 통한 타입 추론**: 제네릭 함수는 다양한 타입에 대응할 수 있는 다형적인 함수를 구현하는 데 활용된다. 예를 들어 `function identity<T>(arg: T): T;`와 같은 제네릭 함수는 인자의 타입에 따라 반환 타입을 유연하게 결정한다.
- **함수 타입과 제네릭**: 타입스크립트는 함수형 프로그래밍을 지원하기 위해 고차 함수와 함수 타입, 제네릭과 같은 기능을 제공한다. 이를 통해 함수의 입력과 출력 타입을 명확히 하고 다양한 타입을 수용하는 범용적인 함수를 손쉽게 구현할 수 있다.
- **이터러블 헬퍼 함수**: 이터러블 헬퍼 함수는 이터러블을 중심으로 고차 함수를 구성하는 패턴이다. 타입스크립트를 사용하면 이러한 함수에 대해 정확한 타입 정보를 제공할 수 있어 코드의 안정성과 가독성을 더욱 높일 수 있다. 예를 들어 `function* map<A, B>(f: (a: A) => B, iterable: Iterable<A>): IterableIterator<B>`와 같이 제네릭을 활용하면 입력과 출력 타입을 명확히 지정한 이터레이션 함수를 만들 수 있다.
- **LISP와 메타프로그래밍**: LISP 계열 언어는 코드와 데이터를 동일하게 취급하여 메타프로그래밍을 손쉽게 구현할 수 있다. LISP의 S-표현식은 리스트 형태의 구문으로 코드 자체를 데이터로 다뤄 동적으로 변형하고 생성할 수 있는 강력한 기능을 제공한다.
- **클래스 + 고차 함수 + 이터러블**: `FxIterable` 클래스 예에서 볼 수 있듯이 클래스와 고차 함수 그리고 이터러블을 결합하면 높은 표현력을 가진 추상화를 구현할 수 있다. 예를 들어 `const [first, second] = fx([1, 2, 3, 4]).map(a => a * 10);`과 같이 사용자 정의 객체를 언어의 기능(여기서는 구조 분해)과 유연하게 결합하고 체이닝 패턴을 통해 가독성 높은 코드를 구현할 수 있다.
- **현대 프로그래밍 언어에서 구현 가능한 높은 수준의 추상화**: 일급 함수의 도입과 이터레이션 프로토콜의 확산은 기존 클래스 기반 반복자 패턴을 넘어 현대 프로그래밍 언어에서 다양한 패러다임을 자연스럽게 결합하는 높은 수준의 추상화를 실현하고 있다. 자바 8(2014년), 스위프트(2014년), 자바스크립트·타입스크립트(ES6, 2015년), 코틀린(2016년), C#(LINQ, 2007년) 등 주요 언어들은 일급 함수와 이터러블, 제네릭, 고차 함수, 커링, 풍부한 타입 시스템 등 다채로운 기능을 제공한다. 이로써 언어 스펙이나 컴파일러를 변경하지 않고도 클래스 등 객체지향 요소와 함수형 패러다임의 핵심 개념, 표준화된 이터레이션 방식 등을 유기적으로 결합할 수 있게 되었다. 이를 통해 개발자는 특정 패러다임에 국한되지 않고 필요에 따라 원하는 추상화 수준을 구현하며 다양한 상황에 대응할 수 있다. 이런 탄탄한 개념적 기반은 여러 플랫폼과 문제 영역에서 폭넓게 응용할 수 있는 실용적인 언어 확장과 패턴화를 가능하게 한다.
