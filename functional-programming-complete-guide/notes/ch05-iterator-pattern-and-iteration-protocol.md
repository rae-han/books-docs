# Chapter 5: Iterator Pattern and Iteration Protocol (반복자 패턴과 이터레이션 프로토콜)

## 핵심 질문

객체지향 디자인 패턴의 반복자 패턴과 함수형 패러다임의 일급 함수는 어떻게 만나 멀티패러다임 언어로의 발전을 이끌었는가? 이터레이션 프로토콜은 왜 상속이 아닌 인터페이스로 설계되었는가?

---

Part 1에서는 배열의 `length`와 인덱스에 기대어 함수형 도구들을 만들었다. Part 2에서는 그 기반을 언어의 표준 규약인 **이터레이션 프로토콜** 위로 옮긴다. 과거에는 함수형 패러다임을 사용하려면 함수형 언어를, 객체지향 패러다임을 사용하려면 객체지향 언어를 선택해야 했다. 그러나 오늘날 대부분의 언어는 멀티패러다임 언어로 발전했고, 그 변화의 시작점에 이 장의 두 주인공 — 반복자 패턴과 일급 함수 — 이 있다.

객체지향 기반 언어들은 반복자 패턴을 통해 지연성 있는 이터레이션 프로토콜을 구현했다. 이후 일급 함수가 추가되면서 이를 바탕으로 `map`, `filter`, `reduce`, `take` 같은 이터레이터 헬퍼 함수들이 구현될 수 있었다. 시간이 흐르며 이러한 함수들은 언어의 핵심 기능으로 자리잡아 빌트인 형태로 제공되기 시작했다. 객체지향 디자인 패턴인 반복자 패턴과 함수형 패러다임의 일급 함수가 만나 지연 평가와 리스트 프로세싱(*List Processing - 리스트 형태의 데이터를 map, filter, reduce 등의 함수로 처리하는 패러다임*)을 구현해 나간 것이다.

---

## 1. GoF의 반복자 패턴

반복자 패턴은 객체지향 디자인 패턴 중 하나로, 컬렉션의 요소를 순차적으로 접근하는 규약을 제시한다. GoF(*Gang of Four - 에릭 감마, 리처드 헬름, 랄프 존슨, 존 블리시디스를 가리키는 별칭*)가 1994년에 발표한 「GoF의 디자인 패턴」에서 소개되었다.

다음은 반복자의 구조를 타입스크립트의 인터페이스 정의로 표현한 코드다.

```typescript
// Iterator 인터페이스
interface IteratorYieldResult<T> { // ①
  done?: false;
  value: T;
}

interface IteratorReturnResult { // ②
  done: true;
  value: undefined;
}

interface Iterator<T> { // ③
  next(): IteratorYieldResult<T> | IteratorReturnResult;
}
```

- ① `IteratorYieldResult<T>`: `done`이 `false`인 경우와 `value`가 `T` 타입인 값을 나타낸다. 반복자가 아직 완료되지 않았음을 의미한다.
- ② `IteratorReturnResult`: `done`이 `true`이고 `value`가 `undefined`인 값을 나타낸다. 반복자가 완료되었음을 의미한다.
- ③ `Iterator<T>`: `next()` 메서드를 가진 인터페이스로 `IteratorYieldResult<T>` 또는 `IteratorReturnResult` 중 하나를 반환한다.

반복자 패턴은 컬렉션의 내부 구조를 노출하는 대신 `next()` 같은 public 메서드로 내부 요소에 접근할 수 있도록 설계되었다. 이는 컬렉션의 실제 구조와 상관없이 다양한 컬렉션 스타일 데이터의 요소를 일관된 방식으로 순회할 수 있게 한다.

> **참고**: 위 코드는 핵심을 간결하게 전달하기 위해 축약된 형태다. 타입스크립트가 공식 제공하는 Iterator 인터페이스는 `lib.es2015.iterable.d.ts` 파일에서 확인할 수 있다.

## 2. ArrayLike로부터 Iterator 생성하기

다음은 `ArrayLike`를 받아 이를 순회하는 Iterator를 생성하는 클래스다. 함수와 객체 리터럴로 더 간결하게 구현할 수도 있지만 이번에는 `class`와 `implements`를 사용하는 좀 더 전통적인 방식을 따랐다.

```typescript
// ArrayLike로부터 Iterator를 생성하는 클래스
/* lib.es5.ts
interface ArrayLike<T> {
  readonly length: number;
  readonly [n: number]: T;
}
*/
class ArrayLikeIterator<T> implements Iterator<T> {
  private index = 0;
  constructor(private arrayLike: ArrayLike<T>) {}

  next(): IteratorResult<T> {
    if (this.index < this.arrayLike.length) {
      return {
        value: this.arrayLike[this.index++],
        done: false,
      };
    } else {
      return {
        value: undefined,
        done: true,
      };
    }
  }
}

const arrayLike: ArrayLike<number> = {
  0: 10,
  1: 20,
  2: 30,
  length: 3,
};

const iterator: Iterator<number> = new ArrayLikeIterator(arrayLike);

console.log(iterator.next()); // { value: 10, done: false }
console.log(iterator.next()); // { value: 20, done: false }
console.log(iterator.next()); // { value: 30, done: false }
console.log(iterator.next()); // { value: undefined, done: true }
```

`ArrayLikeIterator`는 GoF의 반복자 패턴을 따르고 있다. `ArrayLike`는 0부터 시작하는 number 키와 `length` 속성을 가진 타입으로, 자바스크립트에는 `Array`, `arguments`, `NodeList` 등 이 조건을 만족하는 값이 많다. 따라서 `ArrayLikeIterator`로 꼭 `Array`가 아니더라도 다양한 컬렉션을 순회하는 객체를 만들 수 있다 — 2장에서 `_keys`로 우회했던 유사 배열 문제를 패턴 수준에서 다루기 시작한 것이다.

```typescript
// array를 ArrayLikeIterator로 만들어 순회하기
const array: Array<string> = ['a', 'b', 'c'];
const iterator2: Iterator<string> = new ArrayLikeIterator(array);

console.log(iterator2.next()); // { value: 'a', done: false }
console.log(iterator2.next()); // { value: 'b', done: false }
console.log(iterator2.next()); // { value: 'c', done: false }
console.log(iterator2.next()); // { value: undefined, done: true }
```

당연하게도 `next()`를 실행한 만큼만 요소를 순회하고, 실행하지 않으면 순회하지 않는다. **이터레이터의 바로 이 특성을 활용하여 지연 평가를 구현할 수 있다.**

## 3. 지연성 있는 reverse 만들기

### 3.1 Array의 reverse() 메서드

`array.reverse()` 메서드는 호출 시점에 원본 배열의 순서를 뒤집는다. 인덱스로 요소에 접근하기 전에 이미 요소들의 순서가 반전되어 있다.

```typescript
// 원본 배열의 순서를 뒤집는 array.reverse 메서드
const array = ['A', 'B'];
array.reverse(); // array의 순서를 반대로 미리 모두 변경해둠
console.log(array[0], array[1]); // B A
```

이렇게 미리 변경해 두는 동작이 당연하게 여겨질 수 있지만, 대규모 데이터 처리나 성능이 중요한 경우에는 불필요한 메모리 이동과 연산을 유발할 수 있다.

### 3.2 이터레이터의 지연성을 이용한 reverse

이터레이터를 활용하면 배열을 실제로 뒤집지 않고도 역순으로 순회할 수 있다. 이터레이터는 필요할 때마다 값을 하나씩 꺼내는 지연 평가를 지원하므로 모든 요소를 미리 뒤집어둘 필요가 없다.

```typescript
// Iterator를 반환하는 reverse 함수
function reverse<T>(arrayLike: ArrayLike<T>): Iterator<T> {
  let idx = arrayLike.length;
  return {
    next() {
      if (idx === 0) {
        return { value: undefined, done: true };
      } else {
        return { value: arrayLike[--idx], done: false };
      }
    },
  };
}

const array = ['A', 'B'];
const reversed = reverse(array);

console.log(array); // ['A', 'B'] (원본 배열은 그대로)
console.log(reversed.next().value, reversed.next().value);
// B A
```

이 `reverse` 함수는 객체를 실제로 뒤집지 않고도 역순으로 순회하는 이터레이터를 반환한다. 원본 배열을 변경하지 않는 것도 의미가 있지만, 더 중요한 점은 **`reverse`를 호출하는 순간에는 아무 일도 일어나지 않고** `reversed.next().value`를 실행할 때마다 배열을 역순으로 하나씩 효율적으로 꺼낸다는 사실이다.

### 3.3 지연 평가의 효율성

두 방식의 차이는 다음 상황에서 드러난다.

```typescript
// 지연 평가가 더 효율적인 상황
const array = ['A', 'B', 'C', 'D', 'E', 'F'];
array.reverse(); // array의 순서를 반대로 미리 모두 변경해둠
console.log(array[0], array[1]); // F E

const array2 = ['A', 'B', 'C', 'D', 'E', 'F'];
const reversed = reverse(array2);
console.log(array2); // ['A', 'B', 'C', 'D', 'E', 'F']
console.log(reversed.next().value, reversed.next().value); // F E
```

`reverse` 함수를 활용한 `array2`에서는 필요한 만큼만 두 번 역방향으로 순회하여 연산과 메모리 사용을 최소화한다. 원본도 함께 필요하다면 차이는 더 커진다.

```typescript
// 만일 원본도 필요하다면?
const array = ['A', 'B', 'C', 'D', 'E', 'F'];
const reversed = [...array].reverse(); // 복사하여 반전해둠
console.log(reversed[0], reversed[1], array[0], array[1]);
// F E A B

const array2 = ['A', 'B', 'C', 'D', 'E', 'F'];
const reversed2 = reverse(array2);
console.log(reversed2.next().value, reversed2.next().value, array2[0], array2[1]);
// F E A B
```

전자는 원본을 지키기 위해 동일한 크기의 배열을 복사한 다음 전체를 반전시켰다. 반면 후자는 원래도 원본을 변경하지 않기 때문에 복사가 필요하지 않다.

## 4. 지연 평가되는 map — 반복자 패턴과 일급 함수의 만남

이번에는 `Iterator<A>`와 A를 B로 변환하는 `transform` 함수를 받아 지연된 `Iterator<B>`를 반환하는 `map` 함수다. 1장에서 정의한 일급 함수·고차 함수 개념이 반복자 패턴과 처음 만나는 지점이다.

```typescript
// Iterator<A>를 받아서 Iterator<B>를 반환하는 map 함수
function map<A, B>(transform: (value: A) => B, iterator: Iterator<A>): Iterator<B> {
  return {
    next(): IteratorResult<B> {
      const { value, done } = iterator.next();
      return done
        ? { value, done }
        : { value: transform(value), done };
    },
  };
}
```

`map` 함수도 `next()`를 실행하기 전까지는 아무런 작업을 하지 않는다. 외부에서 `next()`를 호출하면 그때 원본 이터레이터의 `next()`를 호출하여 값을 가져오고, `done`이 `false`이면 `transform`을 적용해 반환한다. 이처럼 고차 함수는 인자로 받은 함수를 **원하는 시점에 실행시킬 수 있는 구조**를 갖는다.

```typescript
// map(f, reverse(array))
const array = ['A', 'B', 'C', 'D', 'E', 'F'];
const iterator = map((str) => str.toLowerCase(), reverse(array));

console.log(iterator.next().value, iterator.next().value); // f e
```

`reverse(array)`가 배열을 역순으로 순회하는 이터레이터를 만들고, `map`은 각 요소에 `str => str.toLowerCase()`를 적용할 준비가 된 이터레이터를 만든다. 여기서는 이터레이터를 두 번만 순회하므로 작업도 두 번만 수행한다.

> **핵심 통찰**: 반복자 패턴의 지연성은 지연 평가가 가능한 객체를 생성할 수 있게 해주고, 일급 함수는 고차 함수를 정의할 수 있게 한다. 이 두 가지를 조합하면 `map`, `filter`, `take`, `reduce` 등의 지연 평가를 활용하는 고도화된 리스트 프로세싱 함수를 구현할 수 있다.

## 5. 멀티패러다임의 교차점

자바스크립트는 ES6부터 반복자 패턴의 구현체인 Iterator를 중심으로 `Map`, `Set`, `Array`, WebAPI의 `NodeList` 등을 포함한 코어 환경의 모든 컬렉션 타입에 일관된 순회 규약을 도입했다. 이 이터레이션 프로토콜은 `for...of` 문, 전개 연산자(`...`), 구조 분해와 함께 사용되며, `IterableIterator`를 생성할 수 있는 제너레이터 함수도 추가되었다. `AsyncGenerator`, `Array.fromAsync`, `Iterator Helpers` 등은 이 프로토콜이 현재도 계속 진화하고 있음을 보여준다.

ES6는 또한 `class` 문법을 도입하여 자바스크립트를 객체지향적으로도 크게 발전시켰다. 더 흥미로운 점은 정통적인 객체지향 디자인 패턴인 반복자 패턴이 함수형 패러다임의 일급 함수와 만나며 서로의 가치를 더욱 높이고 있다는 사실이다. 여기에 명령형 패러다임으로 작성되는 제너레이터(6장)까지 이 조합과 호환된다. 세 가지 패러다임이 하나의 언어 안에서 협력하여 언어를 멀티패러다임적으로 발전시키고 있다.

세 패러다임이 만난 시작점이자 통로가 반복자 패턴과 일급 함수라고 할 수 있다. 특히 반복자 패턴은 어느 한 언어에 내장된 기능이나 국한된 개념이 아니라, 일급 객체와 메서드만 지원된다면 어떤 환경에서도 구현 가능한 언어 독립적 방법론이다. GoF는 다양한 순회 전략을 사용자 정의 Iterator 클래스로 체계화해 보여주었고, 무엇을 순회할지·어떻게 순회할지·누가 제어할지를 값(객체)으로 캡슐화해 다루도록 했다. 이렇게 반복 규약을 분리하여 기능을 확장하는 방식은 코드를 데이터처럼 다루며 개발자가 언어 표현력을 스스로 확장해야 한다는 LISP(*LISt Processing - 1950년대 후반 존 매카시가 개발한 고전 함수형 언어로, Scheme, Common Lisp, Clojure 등 파생 언어들이 현대 언어 설계에 큰 영향을 주었다*)의 철학과도 맞닿아 있다.

## 6. 이터레이션 프로토콜

이터레이션 프로토콜은 ES6(ECMAScript 2015)에서 도입된 자바스크립트의 규약이다. 어떤 객체가 이터러블인지 여부를 나타내는 규칙과, 해당 규칙을 따르는 문법들을 제공하는 언어 전반의 규약이다.

### 6.1 순회의 진화 — for에서 for...of로

- **ES5의 for 문**(`for (var i = 0; ...)`)은 **어떻게** 순회할지를 명령한다. 인덱스 `i`와 `length`에 의존하므로 배열·문자열 등 인덱스가 있는 자료형에만 쓸 수 있다.
- **ES6의 for...of 문**은 **무엇을** 순회할지 선언한다. 내부적으로 `[Symbol.iterator]()`를 호출하므로 배열, Set, Map, 문자열 등 이터러블 객체 전체에 쓸 수 있고, 인덱스가 없는 Set·Map도 순회할 수 있다.

```typescript
const list = [1, 2, 3];
const str = 'abc';

for (var i = 0; i < list.length; i++) {
	console.log(list[i]); // 1 2 3
}
for (var i = 0; i < str.length; i++) {
	console.log(str[i]); // a b c
}

for (const a of list) {
	console.log(a); // 1 2 3
}
for (const a of str) {
	console.log(a); // a b c
}
```

`for...of`는 특정 키(`i`)로 접근해서 값을 순회하는 것이 아니다. 그런 동작 원리가 숨겨져 있는 것도 아니다 — Set과 Map은 인덱스로 접근하면 `undefined`가 나온다. 순회 가능한 객체의 `Symbol.iterator` 키에는 함수가 들어 있으며, 만약 이 함수를 지우면 그 객체는 더 이상 순회할 수 없다(`TypeError: ... is not iterable`). 자바스크립트 개발자라면 ES6가 어떤 규약을 열어주었고 순회를 어떻게 추상화했는지 생각해 볼 필요가 있다.

### 6.2 이터레이터, 이터러블, 이터레이션 프로토콜

자연수를 생성하는 이터레이터를 반환하는 함수를 일반 함수(객체 리터럴)로 만들어 보자. 끝나는 값을 설정할 수 있도록 `end` 인자를 추가하고, 기본값은 `Infinity`다.

```typescript
// naturals(): Iterator
function naturals(end = Infinity): Iterator<number> {
  let n = 1;
  return {
    next(): IteratorResult<number> {
      return n <= end
        ? { value: n++, done: false }
        : { value: undefined, done: true };
    },
  };
}

const iterator = naturals(3);

console.log(iterator.next().value); // 1
console.log(iterator.next().value); // 2
console.log(iterator.next().value); // 3
console.log(iterator.next().done);  // true
```

그런데 이 반환값을 `for...of`에 넣으면 타입 에러가 난다.

```typescript
// 타입 에러
const iterator2 = naturals(3);

// TS2488: Type Iterator<number, any, undefined>
// must have a [Symbol.iterator]() method that returns an iterator.
for (const num of iterator2) {
  console.log(num);
}
```

제대로 동작하게 하려면 `[Symbol.iterator]() { return this; }`를 추가하면 된다.

```typescript
// Symbol.iterator 메서드 추가
function naturals(end = Infinity): IterableIterator<number> {
  let n = 1;
  return {
    next(): IteratorResult<number> {
      return n <= end
        ? { value: n++, done: false }
        : { value: undefined, done: true };
    },
    [Symbol.iterator]() {
      return this;
    },
  };
}

const iterator = naturals(3);

for (const num of iterator) {
  console.log(num);
}
// 1
// 2
// 3
```

이제 `for...of`가 이터러블 객체의 `[Symbol.iterator]()`를 호출해 이터레이터를 얻고, 자동으로 `next()`를 호출하면서 자연수를 순회한다. 반환 타입은 이터레이터이면서 동시에 이터러블인 `IterableIterator<number>`가 되었다.

```typescript
// Iterator<T>, Iterable<T>, IterableIterator<T>
interface IteratorYieldResult<T> {
  done?: false;
  value: T;
}

interface IteratorReturnResult {
  done: true;
  value: undefined;
}

interface Iterator<T> {
  next(): IteratorYieldResult<T> | IteratorReturnResult;
}

interface Iterable<T> {
  [Symbol.iterator](): Iterator<T>;
}

interface IterableIterator<T> extends Iterator<T> {
  [Symbol.iterator](): IterableIterator<T>;
}
```

정리하면 다음과 같다.

- **Iterator**: `{ value, done }` 객체를 반환하는 `next()` 메서드를 가진 값
- **Iterable**: 이터레이터를 반환하는 `[Symbol.iterator]()` 메서드를 가진 값
- **IterableIterator**: 이터레이터면서 이터러블인 값
- **이터레이션 프로토콜**: 이터러블을 `for...of` 문, 전개 연산자 등과 함께 동작하도록 한 규약

이터레이터가 자기 자신을 반환하는 `[Symbol.iterator]` 메서드를 가지고 있을 때 **well-formed 이터레이터**라고 부른다. well-formed 이터레이터는 `Symbol.iterator`를 다시 호출해도 새로운 이터레이터가 아니라 **현재 상태를 가진 기존 이터레이터**가 사용된다. 그래서 순회가 중간에 멈췄더라도 이어서 순회할 수 있고, 이미 `next()`로 순회를 끝낸 이터레이터를 `for...of`에 넣으면 아무것도 순회하지 않는다.

```typescript
const arr = [1, 2, 3];
const iter = arr[Symbol.iterator]();

console.log(iter[Symbol.iterator]() === iter); // true — 자기 자신을 반환

console.log(iter.next()); // { value: 1, done: false }
console.log(iter.next()); // { value: 2, done: false }
console.log(iter.next()); // { value: 3, done: false }
console.log(iter.next()); // { value: undefined, done: true }

for (const item of arr) {
  console.log(item); // 1, 2, 3 — 배열은 매번 새 이터레이터를 만든다
}

for (const item of iter) { // 이미 next()로 순회를 끝냈기 때문에 순회하지 않는다.
	console.log(item);
}
```

### 6.3 내장 이터러블

자바스크립트의 내장 이터러블들을 살펴보자.

```typescript
// 이터러블인 Array
const array = [1, 2, 3];
const arrayIterator = array[Symbol.iterator]();

console.log(arrayIterator.next()); // { value: 1, done: false }
console.log(arrayIterator.next()); // { value: 2, done: false }
console.log(arrayIterator.next()); // { value: 3, done: false }
console.log(arrayIterator.next()); // { value: undefined, done: true }

for (const value of array) {
  console.log(value);
}
// 1
// 2
// 3
```

```typescript
// 이터러블인 Set
const set = new Set([1, 2, 3]);
const setIterator = set[Symbol.iterator]();

console.log(setIterator.next()); // { value: 1, done: false }
console.log(setIterator.next()); // { value: 2, done: false }
console.log(setIterator.next()); // { value: 3, done: false }
console.log(setIterator.next()); // { value: undefined, done: true }
```

```typescript
// 이터러블인 Map
const map = new Map([['a', 1], ['b', 2], ['c', 3]]);
const mapIterator = map[Symbol.iterator]();

console.log(mapIterator.next()); // { value: ['a', 1], done: false }

for (const [key, value] of map) {
  console.log(`${key}: ${value}`);
}
// a: 1  b: 2  c: 3
```

`map.entries()`, `map.values()`, `map.keys()`는 각각 엔트리·값·키의 `IterableIterator`를 반환한다. 흥미로운 점은 이들이 well-formed 이터레이터라서, `next()`로 일부를 소비한 뒤 `for...of`를 시작하면 **그 다음 값부터 순회가 이어진다**는 것이다.

```typescript
// Map의 values() 메서드
const mapValues = map.values();

console.log(mapValues.next()); // { value: 1, done: false }

// for...of 문을 사용하여 나머지 값을 순회한다.
for (const value of mapValues) {
  console.log(value);
}
// 2
// 3
```

이터레이터는 내부적으로 현재 위치를 기억하고 순회가 진행됨에 따라 위치를 갱신한다. `map.keys()`도 같은 방식으로 동작한다.

## 7. 언어와 이터러블의 상호작용

이터러블은 언어의 다양한 기능과 상호작용한다. 전개 연산자와 구조 분해가 대표적이다 — 둘 다 이터레이션 프로토콜을 따르는 값을 기대한다.

```typescript
// array 병합
const array = [1, 2, 3];
const array2 = [...array, 4, 5, 6];

console.log(array2); // [1, 2, 3, 4, 5, 6]
```

```typescript
// Set 객체 배열로 변환
const set = new Set([1, 2, 3]);
const array = [...set];

console.log(array); // [1, 2, 3] — Array.from(set)과 동일
```

```typescript
// 전개 연산자로 인자를 펼쳐서 전달
const numbers = [1, 2, 3];

function sum(...nums: number[]): number {
  return nums.reduce((a, b) => a + b, 0);
}

console.log(sum(...numbers)); // 6
```

구조 분해 할당은 이터러블의 요소들을 개별 변수에 할당한다.

```typescript
// 구조 분해 할당
const array = [1, 2, 3];
const [first, second] = array;

console.log(first);  // 1
console.log(second); // 2
```

```typescript
// head와 tail 추출
const array = [1, 2, 3, 4];
const [head, ...tail] = array;

console.log(head); // 1
console.log(tail); // [2, 3, 4]
```

사용자 정의 이터러블도 똑같이 상호작용한다.

```typescript
// naturals 전개
const array = [0, ...naturals(3)];

console.log(array); // [0, 1, 2, 3]
```

이처럼 개발자가 직접 만든 객체도 이터레이션 프로토콜만 따르면 언어의 다양한 기능과 협업할 수 있다. 이런 규약을 만들 수 있는 바탕에 1절의 반복자 패턴이 있다.

## 8. 이터러블 프로토콜이 상속이 아닌 인터페이스로 설계된 이유

객체지향에서 익숙한 개념 중 하나는 상속(*Inheritance*)이다. 상속은 코드를 추상화해 기능을 공유하는 좋은 도구다. 그런데 반복자 패턴과 이터레이터를 지원하는 헬퍼 함수들은 상속이 아닌 인터페이스로 설계되어 있다. 왜일까?

> **참고**: 이 절에서 '상속'과 '인터페이스'가 가리키는 것<br>- **상속(inheritance)**: `class A extends B {}`처럼 기존 클래스의 구성과 구현 모두를 물려받는 '클래스 상속'.<br>- **인터페이스(interface)**: 시그니처(메서드/프로퍼티의 타입 정의)만을 정의하는 것. `class X implements Y {}` 형식으로 클래스가 해당 시그니처를 구현한다. 인터페이스는 구현 코드 없이 시그니처만 지정한다.

### 8.1 WebAPI의 NodeList도 이터러블

DOM을 다루다 보면 만나는 `NodeList`는 문서 내의 노드들을 컬렉션 형태로 나타내며 이터러블 프로토콜을 따른다. 따라서 `for...of`, 전개 연산자 등과 함께 활용할 수 있다.

```html
<!-- NodeList와 for...of 문 -->
<ul>
  <li>1</li>
  <li>2</li>
  <li>3</li>
  <li>4</li>
  <li>5</li>
</ul>
<script>
  const nodeList = document.querySelectorAll('li');

  for (const node of nodeList) {
    console.log(node.textContent);
    // 1 2 3 4 5
  }
</script>
```

그리고 당연하게도 이터러블을 다루는 함수들(7장에서 구현하는 `map`·`filter`·`forEach`)과도 함께 사용할 수 있다.

```javascript
// 이터러블 헬퍼 함수와 함께 활용
forEach(console.log,
  filter(x => x % 2 === 1,
    map(node => parseInt(node.textContent),
      document.querySelectorAll('li'))));
// 1
// 3
// 5

forEach(element => element.remove(),
  filter(node => parseInt(node.textContent) % 2 === 0,
    document.querySelectorAll('li')));
// removed: <li>2</li>
// removed: <li>4</li>
```

### 8.2 상속이 아닌 인터페이스로 해결해야 하는 이유

왜 이터러블을 사용해야 할까? `Array`의 `map`·`filter`를 쓰면 되지 않을까?

```typescript
// NodeList에서 Array.prototype.map을 시도하는 예제
const nodes: NodeList = document.querySelectorAll('li');

console.log(nodes[0], nodes[1], nodes.length);
// <li>1</li> <li>3</li> 3
// nodes는 Array처럼 보인다.

nodes.map(node => node.textContent);
// Uncaught TypeError: nodes.map is not a function
```

`NodeList`는 `Array`가 아니므로 `Array`의 메서드를 사용할 수 없다. 그런데 자바스크립트 표준 라이브러리에서 `Array`를 상속받은 내장 클래스는 없다. `Map`, `Set`, `NodeList`는 `Array`와 동일한 기능이 일부 필요한데도 `Array`를 상속받지 않았다.

핵심은 이들이 모두 **서로 다른 자료구조**를 나타내며 각각 고유한 특성과 동작을 갖도록 설계되었기 때문이다. 상속으로 연결해 의존성이 생기면 불필요한 복잡성이 생기고 최적화된 동작을 보장할 수 없으며, 각 자료구조를 발전시킬 때 서로에게 미칠 영향을 고려해야 하는 어려움이 생긴다.

- **Array**: 인덱스 기반 접근·조작에 최적화되어 있다.
- **Map**: 키-값 쌍을 저장하며 키를 통한 빠른 검색을 제공한다.
- **Set**: 유일한 값을 저장하며 값의 존재 여부를 빠르게 확인한다.

구조적 차이가 있는 자료구조들을 `Array`의 특성에 맞추기 위해 상속하는 것은 부자연스럽고 비효율적이다.

**(가상의 이야기) 한 사람의 결정이 가져온 혼란.** 언어와 브라우저의 표준을 정의하고 구현하는 사람이 어느 날 `NodeList`가 `Array`를 상속받도록 변경하고 배포했다고 상상해 보자. 한 달 뒤 `Array`를 고치고 싶어졌지만, 상속받는 객체가 있어 항상 함께 고려해야 해서 관리가 어려워졌다. `NodeList`에 문제가 발견되어 상속을 제거하고 싶어도, 그 사이 `NodeList`가 `Array`로부터 상속받은 기능을 활용한 코드가 웹에 널리 배포됐다. 이제 상속 관계를 제거하려면 하위 호환성을 위해 `Array`의 모든 기능을 `NodeList`에 포함시켜야 한다. 언어 레벨의 설계일수록 상속을 보수적으로 사용하는 이유다.

**공통 로직을 공유하는 방법.** 이터레이션 프로토콜을 활용하면 상속 없이도 다양한 자료구조를 일관되게 다룰 수 있다. 자료구조가 `Array`, `NodeList`, `Map`, 제너레이터의 반환값, 사용자 정의 이터러블 무엇이든 이터레이션 프로토콜이 **'외부 구조의 다형성'**을 해결한다. 동시에 그 안에 담긴 **'내부 요소의 다형성'**은 고차 함수에 전달되는 보조 함수가 처리한다 — 2장에서 정리한 외부/내부 다형성 구도가 언어 규약 수준에서 재현되는 것이다. 나아가 `Array`·`Map`·`Set`은 자바스크립트 표준 라이브러리지만 `NodeList`는 브라우저 구현 객체다. 인터페이스 기반 규약은 언어나 환경에 따라 달라지는 다양한 구조까지 포용하는 확장성을 제공한다.

> **핵심 통찰**: 이터레이션 프로토콜은 반복자 패턴에 기반한다. 반복자 패턴처럼 공통의 인터페이스를 만들어 패턴화함으로써 다양한 자료구조에 사용할 공통 로직을 분리할 수 있다. 이 방법은 유지보수성을 높이고 다양한 자료구조에 동일한 패턴을 적용할 수 있는 더 나은 설계 방식을 제공한다.

### 8.3 인터페이스와 클래스 상속

인터페이스는 클래스나 객체가 따라야 할 규약을 정의하여 다양한 클래스가 동일한 방식으로 상호작용하게 한다. 상속은 기존 클래스의 속성과 메서드를 물려받아 코드 재사용성과 확장성을 확보한다. 인터페이스의 장점을 강조했지만 두 기법은 우열이 아니라 **목적과 용도가 다르다**.

| 구분 | 인터페이스 | 상속 |
|------|-----------|------|
| **목적** | 규약 제시, 다형성 지원 | 코드 재사용, 기능 확장 |
| **주요 사용처** | 언어/표준 라이브러리 설계 | SDK/애플리케이션 레벨 |
| **결합도** | 느슨한 결합 | 강한 결합 |
| **예시** | 이터레이션 프로토콜 | GUI 프레임워크의 커스텀 윈도우 |

인터페이스는 언어나 표준 라이브러리 설계 단계에서 자주 사용되고, 상속은 주로 SDK나 애플리케이션 레벨에서 사용된다. 상속이 적합한 사례는 18장(객체지향 프런트엔드)에서 다룬다. 목적과 상황에 맞게 인터페이스와 상속을 적절히 선택하는 것이 좋은 코드로 나아가는 첫걸음이다.

## 요약

- **반복자 패턴**은 컬렉션의 내부 구조를 노출하지 않고 `next()`로 요소에 접근하는 객체지향 디자인 패턴이며, `next()`를 호출한 만큼만 순회하는 특성이 **지연 평가**의 토대가 된다.
- 지연 `reverse`·`map`은 원본을 변경하지 않고, 호출 시점에는 아무 일도 하지 않으며, 필요한 만큼만 연산한다 — 반복자 패턴(지연성)과 일급 함수(고차 함수)의 조합이 리스트 프로세싱의 출발점이다.
- **이터레이션 프로토콜**: Iterator(`next()`) / Iterable(`[Symbol.iterator]()`) / IterableIterator(둘 다)의 규약이며, `for...of`·전개 연산자·구조 분해가 모두 이 규약 위에서 동작한다.
- **well-formed 이터레이터**는 `[Symbol.iterator]()`가 자기 자신을 반환하므로 소비 상태를 유지한 채 이어서 순회할 수 있다.
- 이터레이션 프로토콜이 **상속이 아닌 인터페이스**로 설계된 이유: 서로 다른 자료구조(Array·Map·Set·NodeList)의 고유 특성을 지키면서, 외부 구조의 다형성은 프로토콜이, 내부 요소의 다형성은 보조 함수가 해결하기 때문이다.
- 인터페이스는 규약 제시(언어 설계), 상속은 구현 공유(애플리케이션 레벨) — 목적이 다른 도구다.

## 다른 챕터와의 관계

- **2장**: `_keys`로 우회했던 유사 배열·객체 순회 문제가 이 장의 프로토콜로 언어 수준에서 해결된다. 외부/내부 다형성 구도 역시 프로토콜과 보조 함수의 관계로 재현된다.
- **6장**: 이 장에서 객체 리터럴로 만든 이터레이터를 제너레이터가 명령형 코드로 대체한다.
- **7장**: 이 프로토콜 위에서 forEach·map·filter를 세 가지 방식으로 구현한다.
- **8장**: well-formed 이터레이터의 성질이 지연 평가 파이프라인(take가 이터레이터를 그대로 이어받는 동작)의 전제다.
- **17~18장**: 인터페이스 vs 상속의 선택 기준이 실전 설계(ListView 추상화, 커스텀 View 상속)에서 되살아난다.
