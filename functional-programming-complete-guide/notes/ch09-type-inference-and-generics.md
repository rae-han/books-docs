# Chapter 9: Type Inference and Generics (타입 추론과 제네릭)

## 핵심 질문

타입스크립트의 타입 추론은 어떻게 명시적 선언 없이도 안전한 코드를 가능하게 하는가? 함수 타입과 제네릭은 고차 함수와 만나 어떤 추론 능력을 발휘하는가?

---

7장에서 이터러블 고차 함수에 타입을 입히며 제네릭을 실전으로 사용했다. Part 3에서는 그 기반을 체계적으로 다진다 — 이 장에서 타입 추론·함수 타입·제네릭의 원리를 정리하고, 10장에서 클래스·LISP과 조합하며, 11장에서 하스켈을 통해 타입 중심 사고를 확장한다.

타입스크립트는 자바스크립트에 강력한 타입 시스템을 추가하여 코드의 안정성과 가독성을 높인다. 타입 추론을 통해 개발자는 명시적인 타입 선언 없이도 안전한 코드를 작성할 수 있고, 고차 함수와 제네릭을 활용하면 복잡한 함수형 프로그래밍 패턴을 구현할 수 있다.

> **참고**: 이 장의 `[코드 2-N]` 번호는 원본 멀티패러다임 노트(ch02) 기준이다. 주석의 `[const a: "hi"]` 형태는 IDE에서 마우스를 올리면 보이는 타입 가이드 박스를 표현한 것이다.

---

## 1. 타입 추론

타입스크립트의 타입 추론(*Type Inference - 코드 작성 시 타입을 명시적으로 선언하지 않아도 컴파일러가 자동으로 타입을 추론해주는 기능*)은 코드의 간결성을 유지하면서도 타입 안정성을 확보할 수 있게 한다.

### 1.1 기본 콘셉트와 변수·상수의 추론

다음 코드에서 `a`는 명시적으로 타입이 선언되지 않았지만 타입스크립트는 `10`이라는 값을 통해 `a`의 타입을 `number`로 추론한다. 이후 `a`에 다른 타입의 값을 할당하려고 하면 타입 오류가 발생한다.

```typescript
// [코드 2-1] 타입 추론 기본 예시
let a = 10;
```

변수는 초기화된 값으로부터 타입이 추론된다.

```typescript
// [코드 2-2] 변수 타입 추론
let message = "Hello, TypeScript!";
```

`const`와 `let`은 추론 결과가 다르다.

```typescript
// [코드 2-3] 상수 타입 추론
const selected = true;
// [const selected: true]
let checked = true;
// [let checked: boolean]
```

`const`로 선언된 `selected`는 재할당할 수 없어 값이 바뀔 수 없으므로 타입이 리터럴 `true`로 추론된다. 반면 `let`으로 선언된 `checked`는 변경할 수 있으므로 `boolean`으로 추론된다.

### 1.2 함수의 반환 타입 추론

```typescript
// [코드 2-4] 반환 타입 추론 1
function add(a: number, b: number) {
  return a + b;
}
```

반환 타입을 명시하지 않았지만 `a`와 `b`를 통해 `number`로 추론된다. 인자 타입을 `string`으로 바꾸면 반환 타입도 `string`이 된다.

```typescript
// [코드 2-5] 반환 타입 추론 2
function add(a: string, b: string) {
  return a + b;
}
```

```typescript
// [코드 2-6] 반환 타입 추론 3
function add(a: string, b: string) {
  return parseInt(a) + parseInt(b);
}
```

타입스크립트는 `parseInt`가 `number`를 반환한다는 사실을 알기 때문에 `add`의 반환 타입을 `number`로 추론한다. 명시적으로 지정할 수도 있으며 이는 추론과 일치한다.

```typescript
// [코드 2-7] 명시적인 반환 타입 지정
function add(a: string, b: string): number {
  return parseInt(a) + parseInt(b);
}
```

### 1.3 객체 속성과 함수 인자의 추론

```typescript
// [코드 2-8] 객체의 속성 타입 추론
let user = {
  name: "Marty",
  age: 30,
};
```

`user`의 `name`은 `string`, `age`는 `number`로 추론된다. 함수 인자의 추론은 특히 매력적이다.

```typescript
// [코드 2-9] 함수 인자의 타입 추론
let strs = ['a', 'b', 'c'];
strs.forEach(str => console.log(str.toUpperCase())); // [str: string]
```

타입스크립트는 `strs`를 `string[]`으로 추론하고, `forEach`는 배열의 요소 타입을 기반으로 화살표 함수의 `str` 타입을 `string`으로 추론한다. **고차 함수에서도 타입 추론이 동작하므로** 인자로 전달받은 함수의 인자 타입까지 추론되어, 화살표 함수의 간결한 표현을 유지하면서도 타입 안전성을 확보할 수 있다. 7장에서 만든 사용자 정의 고차 함수들이 정확히 이 성질을 활용했다.

### 1.4 제네릭을 통한 타입 추론

제네릭 함수를 사용하면 하나의 함수가 다양한 타입을 지원하는 다형성 높은 함수가 된다. 인자로 받은 값의 타입을 그대로 반환하는 `identity`가 좋은 예다 — `identity`를 평가하는 표현식에서 전달한 인자 `arg`의 타입으로 `T`의 실제 타입이 정해지며, 해당 타입이 반환 타입이 된다.

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

- ① 문자열 `"hi"`를 전달하면 `T`가 `"hi"`가 되고 `a`의 타입 역시 `"hi"`로 추론된다.
- ② `1`을 전달하면 `T`가 `1`이 되고 `b`의 타입 역시 `1`이 된다.
- ③ `identity<string>("a")`처럼 `T`를 명시적으로 `string`으로 지정하면 `c`의 타입은 `string`으로 결정된다.
- ④ 마찬가지로 `T`를 `number`로 지정하면 `d`의 타입은 `number`가 된다.
- ⑤ `User`의 인스턴스를 전달하면 `T`가 `User`로 결정되고 `e`의 타입 역시 `User`가 된다.
- ⑥ 함수를 전달하면 그 함수의 타입 `(n: number) => boolean`이 `T`가 되어 `f`의 타입으로 지정된다.

> **참고**: 4장에서 es5로 만든 `_identity`가 "값을 그대로 리턴하는 함수"의 조합적 가치를 보여줬다면, 이 `identity<T>`는 같은 함수가 타입 세계에서 갖는 의미 — 타입을 그대로 통과시키는 항등 사상 — 를 보여준다.

## 2. 함수 타입과 제네릭

함수 타입을 명시적으로 정의하면 함수의 입력과 출력 타입을 명확하게 표현할 수 있고, 제네릭을 활용하면 폭넓은 타입을 지원하는 범용 함수를 만들 수 있다. 특히 고차 함수는 인자로 전달받은 함수의 매개변수 타입을 추론하고 함께 전달된 다른 인자들의 타입과도 연계해 타입을 유연하게 추론하도록 돕는다.

### 2.1 함수의 타입을 정의하는 여러 가지 방법

가장 기본적인 방법은 매개변수와 반환값에 타입을 명시하는 것이다.

```typescript
// [코드 2-11] 기본적인 함수 타입 정의
function add(a: number, b: number): number {
  return a + b;
}
const result: number = add(2, 3); // 5
```

**함수 오버로드**는 동일한 함수명으로 다양한 시그니처를 정의할 수 있게 한다.

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

구현부의 `typeof` 검사는 런타임에서 타입에 따라 다른 로직을 실행하게 하고, 컴파일 타임에서도 타입스크립트가 `if` 블록 내에서 타입을 정확하게 구분해 추론한다. 이를 타입 가드(*Type Guard*)에 의한 타입 좁히기(*Type Narrowing*)라고 부른다 — `if (typeof a === 'number')` 블록 안에서 `a`는 `number`, `else` 블록 안에서는 `string`으로 추론된다.

화살표 함수는 매개변수의 타입만 명시해도 반환 타입이 추론된다.

```typescript
// [코드 2-13] 화살표 함수
const multiply = (a: number, b: number): number => a * b;

// [코드 2-14] 화살표 함수 (타입 추론)
const multiply = (a: number, b: number) => a * b;
const num: number = multiply(4, 5); // 20
```

**함수 타입 별칭**을 정의하면 여러 곳에서 동일한 함수 타입을 재사용할 수 있다.

```typescript
// [코드 2-15] 함수 타입 별칭
type Add = (a: number, b: number) => number;
const add: Add = (a, b) => a + b;
```

`add`를 `Add` 타입으로 선언하면 타입 가이드를 받으며 구현할 수 있다.

### 2.2 constant와 제네릭

`constant` 함수는 입력받은 값을 항상 그대로 돌려주는 함수를 반환한다 — 특정 값을 캡처하여 호출될 때마다 반환하는, 1장에서 본 클로저의 타입 버전이다.

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

동작 방식을 자세히 보면 다음과 같다.

1. `constant` 함수 옆에 제네릭 `<T>`를 작성하여 이 함수에서 `T` 타입을 사용하겠다고 선언한다.
2. `T`를 활용하여 인자 `a`의 타입을 `T`로 정의한다.
3. `constant`는 `T` 타입의 값을 받아 `T` 타입의 값을 반환하는 함수를 반환한다.
4. 반환되는 함수의 타입을 `() => T`로 정의하여 인자 없이 `T`를 반환한다고 명시한다.
5. `a`로 받은 `5`로 인해 `T`가 `number`로 추론되고 `getFive`의 반환 타입도 `number`가 된다.
6. `a`로 받은 `"Hi"`로 인해 `T`가 `string`으로 추론되고 `getHi`의 반환 타입도 `string`이 된다.

> **참고**: `identity`와 다르게 `constant`는 `5`나 `"Hi"`를 받고도 `T`가 리터럴이 아닌 `number`·`string`으로 추론됐다. 타입스크립트는 고차 함수가 다루는 일급 함수의 인자나 반환값을 추론할 때 넓은 타입으로 추론하는 경향이 있기 때문이다. 중요한 부분은 아니지만 참고로 알아두면 좋다.

## 3. 이터레이션 프로토콜과 타입 다시 보기

`Iterator`, `Iterable`, `IterableIterator`에 일급 함수를 더한 함수형 고차 함수들을 타입과 함께 다루려면(7장) 다음 개념들이 전제된다.

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

복습 체크리스트 — 아래를 모두 설명할 수 있어야 한다(각각 5~7장에서 다뤘다).

1. 이터레이션 프로토콜과 관련된 세 가지 값인 `Iterator`, `Iterable`, `IterableIterator`에 대해 알고 있다.
2. `for...of` 문으로 순회할 수 있는 값은 오직 이터러블이다.
3. 전개 연산자로 배열을 만들 수 있는 값도 오직 이터러블이다.
4. `IterableIterator`를 만드는 함수를 구현할 때 반환값을 `{ next() {...}, [Symbol.iterator]() {...} }` 형식으로 구현할 수 있으며 이 객체는 이터레이터이자 동시에 이터러블이다.
5. 제너레이터로도 이터레이터를 만들 수 있으며 제너레이터의 실행 결과는 `IterableIterator`이다.
6. 제너레이터의 `yield`와 이터레이터의 `next()`의 관계를 이해하고 있다.
7. 이터레이터에 고차 함수를 조합하여 `forEach`, `map`, `filter`를 만들 수 있으며 이터레이션 프로토콜을 지원하여 언어의 기능과 상호작용하도록 만들 수 있다.

> **참고**: [코드 2-17]은 핵심을 간결하게 전달하기 위해 축약된 형태다. 실제 에디터에서 이대로 작성하면 중복 타입 선언이나 추론 오류가 발생한다. 공식 `Iterator` 인터페이스는 `lib.es2015.iterable.d.ts`에서 확인할 수 있다.

## 요약

- **타입 추론**은 변수·상수(`const`는 리터럴, `let`은 넓은 타입)·함수 반환·객체 속성·고차 함수의 콜백 인자까지 미친다 — 명시적 선언 없이도 안전성과 생산성을 함께 얻는다.
- **제네릭**은 인자의 타입으로 `T`가 결정되고 그 `T`가 반환 타입까지 흐르게 한다(`identity<T>`, `constant<T>`) — 다형성 높은 함수의 타입적 기반이다.
- 함수 타입은 **명시·오버로드·화살표·타입 별칭**으로 정의할 수 있으며, 오버로드 구현부의 타입 가드는 컴파일 타임 타입 좁히기와 런타임 분기를 동시에 제공한다.
- 고차 함수의 타입 추론(콜백 인자 추론)이 함수형 프로그래밍과 타입 시스템이 만나는 핵심 접점이다.
- 이터레이션 프로토콜의 세 인터페이스(Iterator/Iterable/IterableIterator)가 이후 모든 타입 적용(7장 고차 함수, 10장 FxIterable, 14장 AsyncIterable)의 어휘다.

## 다른 챕터와의 관계

- **1장**: `constant`는 클로저(4.3절)의 타입 버전이고, `identity`는 4장 `_identity`의 타입 버전이다.
- **7장**: 이 장의 제네릭·추론 원리가 forEach/map/filter/reduce의 타입 정의로 실전 적용됐다.
- **10장**: 제네릭 **클래스**(`FxIterable<A>`)로 확장되어 체이닝과 타입 추론을 결합한다.
- **11장**: 하스켈의 함수 시그니처 표기가 타입 중심 사고를 언어 밖으로 확장한다.
- **14장**: 함수 오버로드가 동기/비동기 통합 API(`map`·`filter`·`reduce`)의 도구로 쓰였다.
