# Chapter 7: Higher-Order Functions for Iterables (이터러블 고차 함수)

## 핵심 질문

forEach·map·filter를 세 가지 방식(for...of, while, 객체 리터럴)으로 구현하면 무엇이 보이는가? 타입 시스템은 이 함수들에 어떻게 입혀지며, reduce의 초깃값 생략 같은 유연한 스펙은 어떻게 안전하게 처리하는가?

---

2장에서는 `length`와 인덱스에 기대어 `_map`·`_filter`를 만들었다. 이제 5장의 이터레이션 프로토콜과 6장의 제너레이터 위에서 같은 함수들을 다시 만든다. 반복자 패턴을 활용하고 이터레이션 프로토콜을 준수하는 함수를 구현하는 패턴에 익숙해지는 것이 목표다. 전반부(1~7절)는 타입 정의 없이 자바스크립트로 패턴에 집중하고, 후반부(8~11절)에서 타입 시스템을 입힌다.

---

## 1. 인자와 반환값으로 대화하기

구현에 앞서, 이 함수들이 공유하는 태도를 짚고 가자. 데이터를 수집하는 기본적인 map을 만든다고 할 때, 처음에는 이렇게 쓰기 쉽다.

```typescript
const products = [
  { name: "반팔티", price: 15000 },
  { name: "긴팔티", price: 20000 },
  { name: "핸드폰케이스", price: 15000 },
  { name: "후드티", price: 30000 },
  { name: "바지", price: 25000 },
];

const map = () => {
  let result = [];

  for (const item of products) {
    result.push(item.name);
  }

  console.log(result);
};

map();
```

함수형 프로그래밍은 **인자와 반환값으로 대화하는 것**을 지향한다. 내부 로직에서 작업(출력 등)을 하기보다, 리턴된 값으로 변화를 일으키거나 사용하는 것이 함수형다운 사고방식이다. 전체 값에 대한 로그를 찍고 싶다면 map 내부가 아니라 리턴된 값으로 출력한다. 여기에 "무엇을 수집할 것인지"를 보조 함수에 완전히 위임하면(2장에서 확인한 추상화) 다음 형태가 된다.

```typescript
const map = (fn, iter) => {
	let result = [];

	for (const a of iter) {
		result.push(fn(a));
	}

	return result;
};

console.log(map((p) => p.name, products));
```

매개변수 이름을 `iter`라고 지은 것은 이 함수가 받는 값이 **이터러블 프로토콜을 따른다**는 뜻이다. 그래서 이 map은 다형성이 굉장히 높다 — 값이 배열이 아니어도, 이터러블(배열, Set, Map, DOM NodeList, 제너레이터의 반환값)이라면 무엇이든 적용할 수 있다.

```typescript
console.log(
  map(
    (p) => p.name,
    (function* () {
      yield { name: "반팔티", price: 15000 };
      yield { name: "긴팔티", price: 20000 };
      yield { name: "바지", price: 25000 };
    })()
  )
); // [ '반팔티', '긴팔티', '바지' ]
```

이 장의 나머지는 이 태도 — 반환값으로 대화하고, 로직은 보조 함수에 위임하고, 이터러블 프로토콜로 다형성을 얻는다 — 를 forEach·map·filter·reduce에 걸쳐 여러 구현 방식으로 체화하는 과정이다.

## 2. forEach — for...of와 while

`forEach`는 함수와 이터러블을 받아 이터러블을 순회하면서 각 요소에 인자로 받은 함수를 적용하는 고차 함수다.

```javascript
// function forEach(f, iterable) { for...of }
function forEach(f, iterable) {
  for (const value of iterable) {
    f(value);
  }
}

const array = [1, 2, 3];
forEach(console.log, array);
// 1
// 2
// 3
```

`for...of` 문으로 이터러블의 각 요소를 순회하며 함수 `f`에 `value`를 전달한다. 같은 함수를 `while` 루프로 이터레이터를 직접 조작하며 구현할 수도 있다.

```javascript
// function forEach(f, iterable) { while }
function forEach(f, iterable) {
  const iterator = iterable[Symbol.iterator]();
  let result = iterator.next();
  while (!result.done) {
    f(result.value);
    result = iterator.next();
  }
}

const set = new Set([4, 5, 6]);
forEach(console.log, set);
// 4
// 5
// 6
```

`next()`로 각 요소를 순회하고 `result.done`이 `true`일 때 멈춘다. `Set`도 이터러블이므로 그대로 동작한다.

> **참고**: 두 `forEach`는 동일하게 동작하며 실제로 언어 내부에서 하는 일도 거의 동일하다. 자바스크립트의 `for...of` 내부에는 비정상 종료 등 여러 예외 상황을 처리하기 위한 로직이 포함되어 있는데, 그 차이가 다음 절의 주제다.

## 3. for...of의 이터레이터 종료 처리 — IteratorClose

`for...of`와 수동 `while` 루프의 가장 큰 차이는 **이터레이터 종료 처리**(*IteratorClose*)다. ECMAScript 명세에 따르면, `for...of` 루프가 `break`, `return`, 또는 예외(`throw`)로 인해 중간에 빠져나올 때 엔진은 자동으로 이터레이터의 `return()` 메서드를 호출한다. 이터레이터가 보유한 리소스를 정리할 기회를 주기 위함이다.

```javascript
// 리소스를 보유하는 이터러블 예시
function createResourceIterable() {
  console.log('리소스 획득');
  return {
    [Symbol.iterator]() {
      let i = 0;
      return {
        next() {
          return i < 5
            ? { value: i++, done: false }
            : { value: undefined, done: true };
        },
        return() {
          console.log('리소스 해제'); // 정리 로직
          return { value: undefined, done: true };
        },
      };
    },
  };
}

// for...of: break 시 return()이 자동 호출된다
for (const value of createResourceIterable()) {
  if (value === 2) break;
  console.log(value);
}
// 리소스 획득
// 0
// 1
// 리소스 해제 ← 엔진이 자동으로 iterator.return()을 호출

// while: break 시 return()이 호출되지 않는다
const iterable = createResourceIterable();
const iterator = iterable[Symbol.iterator]();
let result = iterator.next();
while (!result.done) {
  if (result.value === 2) break;
  console.log(result.value);
  result = iterator.next();
}
// 리소스 획득
// 0
// 1
// (리소스 해제가 호출되지 않음 — 리소스 누수 가능)
```

제너레이터로 만든 이터레이터도 동일한 혜택을 받는다. 제너레이터에는 `return()` 메서드가 자동으로 존재하며, 호출 시 제너레이터 내부의 `finally` 블록이 실행된다.

```javascript
function* numbersWithCleanup() {
  try {
    yield 1;
    yield 2;
    yield 3;
  } finally {
    console.log('제너레이터 정리 완료');
  }
}

for (const n of numbersWithCleanup()) {
  if (n === 2) break;
  console.log(n);
}
// 1
// 제너레이터 정리 완료 ← finally 블록이 실행됨
```

실무에서 이 차이가 두드러지는 대표적인 예는 파일 읽기, 데이터베이스 커서, 네트워크 스트림 등 외부 리소스를 순회하는 경우다. `for...of`를 사용하면 루프가 어떤 이유로 중단되더라도 리소스가 안전하게 해제된다. 배열·`Set`·`Map` 같은 인메모리 컬렉션은 별도의 정리가 필요 없어 차이가 드러나지 않을 뿐이다.

## 4. map — 세 가지 구현

첫 번째는 제너레이터 + `for...of` 구현이다.

```javascript
// function* map(f, iterable) { for...of }
function* map(f, iterable) {
  for (const value of iterable) {
    yield f(value);
  }
}

const array = [1, 2, 3];
const mapped = map((x) => x * 2, array);
console.log([...mapped]); // [2, 4, 6]

const mapped2 = map((x) => x * 3, naturals(3));
forEach(console.log, mapped2);
// 3
// 6
// 9
```

`map`은 이터러블을 인자로 받아 이터레이터를 반환하고, 반환 결과는 동시에 이터러블이다. 그래서 전개 연산자·`for...of`·`forEach`·`naturals`와 모두 조합된다.

두 번째는 제너레이터 + `while` 구현이다.

```javascript
// function* map(f, iterable) { while }
function* map(f, iterable) {
  const iterator = iterable[Symbol.iterator]();
  while (true) {                                // ①
    const { value, done } = iterator.next();    // ②
    if (done) break;                            // ③
    yield f(value);                             // ④
  }
}

const mapped = map(
  ([k, v]) => `${k}: ${v}`,
  new Map([['a', 1], ['b', 2]]),
);
forEach(console.log, mapped);
// a: 1
// b: 2
```

- ① 무한 루프를 만든다.
- ② `next()`의 결과를 구조 분해한다.
- ③ `done`이 `true`인 경우 `break;`를 수행한다.
- ④ `value`에 인자로 받은 함수 `f`를 적용한 결과를 `yield`로 반환한다.

`Map`의 요소인 엔트리 역시 이터러블이기에 구조 분해를 이용할 수 있다.

세 번째는 객체 리터럴로 `IterableIterator`를 직접 만드는 구현이다.

```javascript
// function map(f, iterable) { return { next, ... } }
function map(f, iterable) {
  const iterator = iterable[Symbol.iterator]();
  return {                                         // ①
    next() {
      const { done, value } = iterator.next();
      return done
        ? { done, value }
        : { done, value: f(value) };               // ②
    },
    [Symbol.iterator]() {                          // ③
      return this;
    },
  };
}

const iterator = (function* () {                   // ④
  yield 1;
  yield 2;
  yield 3;
})();

const mapped = map((x) => x * 10, iterator);      // ⑤

console.log([...mapped]); // [10, 20, 30]
```

- ① 이 `map` 함수는 `IterableIterator` 객체를 직접 만들어 반환한다.
- ② `next` 메서드를 직접 구현하여 각 요소 `value`에 함수 `f`를 적용한 결과를 반환한다.
- ③ 이터러블 프로토콜을 따르도록 `[Symbol.iterator]` 메서드를 추가한다.
- ④ 익명 제너레이터 함수로 1, 2, 3을 순차 생성하는 이터레이터를 만들어 `map`에 전달한다.
- ⑤ `map`은 각 요소에 `x * 10`을 적용할 준비를 해둔 이터레이터를 만든다.

## 5. filter — 세 가지 구현과 꼬리 호출 최적화

`filter`는 이터러블의 각 요소에 대해 조건을 확인하여 만족하는 요소들만 반환하는 고차 함수다.

```javascript
// function* filter(f, iterable) { for...of }
function* filter(f, iterable) {
  for (const value of iterable) {
    if (f(value)) {
      yield value;
    }
  }
}

const array = [1, 2, 3, 4, 5];
const filtered = filter((x) => x % 2 === 0, array);
console.log([...filtered]); // [2, 4]
```

```javascript
// function* filter(f, iterable) { while }
function* filter(f, iterable) {
  const iterator = iterable[Symbol.iterator]();
  while (true) {
    const { value, done } = iterator.next();
    if (done) break;       // 여기까지 동일
    if (f(value)) {
      yield value;
    }
  }
}
```

`map`과 `filter`의 `while` 구현을 비교해 보면, 루프 바깥 부분과 `done`으로 종료하는 곳까지는 동일하고 내부 구현만 다르다. 이 패턴이 익숙해지면 함수형 고차 함수들을 쉽게 구현할 수 있다.

객체 리터럴 구현은 흥미로운 지점이 있다 — 반복문 없이 재귀로 순회한다.

```javascript
// function filter(f, iterable) { return { next, ... } }
function filter(f, iterable) {
  const iterator = iterable[Symbol.iterator]();
  return {
    next() {
      const { done, value } = iterator.next();
      if (done) return { done, value };       // ③
      if (f(value)) return { done, value };   // ①
      return this.next();                     // ② 재귀 호출
    },
    [Symbol.iterator]() {
      return this;
    },
  };
}

console.log(...filter((x) => x % 2 === 1, [1, 2, 3, 4, 5])); // 1 3 5
```

- ① 조건 함수 `f`를 만족하면 `{ done, value }`를 그대로 반환한다.
- ② 만족하지 않으면 재귀적으로 `this.next()`를 다시 실행하여 순회를 계속한다.
- ③ 모든 순회를 마쳐 `done`이 `true`가 되면 그대로 반환하여 종료한다.

이 `next()`는 반복문 없이 자신의 메서드를 재귀 호출하는 객체지향적인 코드로 매우 간결하다. 또한 ②의 `this.next()` 호출이 함수의 마지막 동작이고 그 결과가 직접 반환되므로 꼬리 호출 최적화(*Tail Call Optimization, TCO - 함수의 마지막 동작이 재귀 호출일 때 스택을 재사용하는 최적화*)가 가능한 구조다. 그러나 아쉽게도 ES6 스펙에 포함된 꼬리 호출 최적화를 V8 엔진은 지원하지 않아 스택 오버플로의 위험이 있다.

이 문제는 다음과 같이 해결한다.

```javascript
// do...while, while로 변경
function filter(f, iterable) {
  const iterator = iterable[Symbol.iterator]();
  return {
    next() {
      do {
        const { done, value } = iterator.next();
        if (done) return { done, value };
        if (f(value)) return { done, value };
      } while (true); // 재귀 호출과 동일한 위치이며 거의 동일한 표현
    },
    [Symbol.iterator]() {
      return this;
    },
  };
}

// while만 사용하면 좀 더 간결하다.
function filter(f, iterable) {
  const iterator = iterable[Symbol.iterator]();
  return {
    next() {
      while (true) {
        const { done, value } = iterator.next();
        if (done) return { done, value };
        if (f(value)) return { value };
      }
    },
    [Symbol.iterator]() {
      return this;
    },
  };
}
```

함수 전체를 무한 루프로 감싸 재귀 호출과 거의 유사한 구조를 유지하면서도 안전하게 최적화했다. 현대 언어 중 스칼라와 코틀린은 꼬리 재귀 함수를 반복문 형태로 변환해 스택 오버플로를 방지한다 — 스칼라는 `@tailrec` 애노테이션으로 더 다양한 패턴을, 코틀린은 `tailrec` 키워드로 특정 형태의 꼬리 재귀에 한해 최적화를 제공한다.

## 6. 고차 함수 조합하기

지금까지 작성한 함수들을 함께 활용해 보자.

```javascript
// 고차 함수 조합
forEach(console.log,         // ④
  map(x => x * 10,           // ③
    filter(x => x % 2 === 1, // ②
      naturals(5))));         // ①
// 10
// 30
// 50
```

함수가 많이 중첩되어 읽기 불편할 수 있지만, 이는 LISP 계열 언어에서 흔히 사용하는 컨벤션이다. **오른쪽 아래에서 왼쪽 위로** 올라가며 읽으면 쉽다.

- ① `naturals(5)` 결과를
- ② `x % 2 === 1` 조건으로 필터링하고
- ③ `x * 10`으로 변환한 다음
- ④ 모두 콘솔에 출력하라

`naturals(5)`로 1~5의 자연수를 생성하는 이터레이터를 만들고, `filter`가 홀수만 걸러내는 이터레이터를, `map`이 10배 값을 생성하는 이터레이터를 만든다 — 모두 평가가 지연된 객체다. 마지막 `forEach`가 순회를 시작하면 그제야 값이 하나씩 흐른다(이 실행 순서의 정밀한 추적은 8장에서).

## 7. 재미난 filter — if 없는 필터링

```javascript
// function* filter(f, iterable) { [].filter() }
function* filter(f, iterable) {
  for (const value of iterable) {
    yield* [value].filter(f);
  }
}

const array = [1, 2, 3, 4, 5];
const filtered = filter((x) => x % 2 === 0, array);
console.log([...filtered]); // [2, 4]
```

이 코드의 재미 포인트는 **`if` 문 없이 필터링을 구현했다**는 것이다.

1. `[value].filter(f)` → 조건을 통과하면 `[value]`, 실패하면 `[]`을 반환한다.
2. `yield* [value]` → `value`를 yield한다.
3. `yield* []` → 빈 이터러블이므로 아무것도 yield하지 않고 다음 반복으로 넘어간다.

배열의 "있거나 없거나"라는 성질과, `yield*`가 빈 이터러블에 대해 아무것도 하지 않는 성질을 조합해 `if` 문의 역할을 대체했다 — **조건 분기를 데이터 구조의 존재 여부로 치환**한 것이다. 이 방식도 지연 평가를 지원하며 시간 복잡도는 O(n)으로 동일하다(단일 요소 배열 생성과 `Array.prototype.filter` 호출의 오버헤드는 매우 작다). 너무 진지하게 볼 필요는 없지만, 이터러블을 다루는 프로그래밍 아이디어를 확장해 주는 접근이다.

## 8. 고차 함수에 타입 입히기

지금까지 만든 함수들은 이터러블 자료구조를 중심으로 구성되므로 **이터러블 헬퍼 함수**라고 부를 수 있다. 이제 타입 시스템을 적용해 보자(타입 추론·제네릭의 기초는 9장에서 더 깊게 다루지만, 이 절은 함수 정의만으로 읽을 수 있다).

### 8.1 forEach와 타입

```typescript
// forEach 함수와 타입
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

1. `forEach` 옆에 제네릭 `<A>`를 작성하여 함수에서 `A` 타입을 사용하겠다고 선언한다.
2. `A`를 활용하여 `f` 함수의 타입을 인자로 `a: A`를 받아 `void`를 반환하는 타입으로 정의한다.
3. `iterable`의 타입을 `A`를 요소로 갖는 `Iterable<A>`라고 정의한다.
4. 풀어 말하면 '`<A>`를 선언하고 `a: A`와 `Iterable<A>`를 작성하여, `iterable`의 요소 타입이 `A`이며 그 `A`가 `f` 함수의 인자 `a`가 되도록 연결해 주었다'라고 할 수 있다.
5. `forEach`가 받은 `array: number[]`로 인해 `Iterable<A>`가 `Iterable<number>`가 되고 `f`의 `a`도 `number`가 된다.
6. 제네릭을 잘 활용했기 때문에 `a`는 `number`로 정확히 추론되며 `toFixed(2)`를 안전하게 호출할 수 있다.

### 8.2 map과 타입

```typescript
// 제너레이터로 구현한 map 함수와 타입
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

1. `map<A, B>`를 작성하여 제네릭 타입 `A`와 `B`를 만든다.
2. `map`은 `A`를 입력받아 `B`를 출력하는 함수 `f`와 `Iterable<A>`를 받아 `IterableIterator<B>`를 반환한다.
3. 첫 번째 경우 전달한 `array`가 `Iterable<string>`으로 해석되어 `A`는 `string`이 된다.
4. `a => parseInt(a)`의 반환 타입에 의해 `B`가 `number`가 되어 반환 타입이 `IterableIterator<number>`가 된다.
5. `mapped`를 전개 연산자로 배열로 변환한 `array2`가 `number[]`로 잘 처리된다.
6. 두 번째 경우 `[head]` 구조 분해도 `string`으로 제대로 추론된다.

### 8.3 filter와 타입

```typescript
// 제너레이터로 구현한 filter 함수와 타입
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

`map`은 `A → B` 변환이 있어 제네릭이 두 개였지만, `filter`는 요소를 변환하지 않고 걸러내기만 하므로 `A` 하나면 충분하다. 인자 `f`의 `a`, `iterable`의 요소, 반환 `IterableIterator`의 요소가 모두 같은 `A`다 — 이 차이가 filter의 타입 정의가 map보다 단순한 이유다.

### 8.4 reduce와 타입

```typescript
// reduce 함수와 타입
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

`reduce`는 `(acc: Acc, a: A) => Acc` 타입의 함수와 `Acc` 타입의 초깃값, `Iterable<A>`를 받아 요소를 순회하며 누적값을 계산하고 최종 누적값 `Acc`를 반환한다. 이처럼 **함수의 동작을 타입 중심으로 설명하면 개발자 간 소통을 보다 원활하고 정확하게** 할 수 있다.

## 9. reduce 함수 오버로드 — 초깃값 생략

자바스크립트의 `Array.prototype.reduce`는 초깃값을 생략할 수 있다. 이터러블 `reduce`도 동일한 스펙을 지원하도록 구현해 보자.

- 초깃값이 있을 때는 세 개의 인자를 받는다.
- 초깃값을 생략할 때는 `f`와 `iterable`만 받고, 이터러블의 첫 번째 요소가 초깃값이 된다.
- 초깃값 없이 빈 이터러블이 전달되면 누적할 수 없으므로 에러를 발생시킨다.

이렇게 구현하려면 함수 오버로드(*Function Overload - 함수의 시그니처를 여러 개 정의하고 실제 구현은 하나만 제공하는 방식*)를 사용해야 한다. 하나의 함수명으로 다양한 호출 방식에 대응할 수 있다.

```typescript
// reduce(f, iterable)
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

- ① 첫 번째 시그니처: 초깃값 `acc: Acc`와 `Iterable<A>`, `(acc: Acc, a: A) => Acc` 함수를 받아 `Acc`를 반환한다.
- ② 두 번째 시그니처: 초깃값 없이 `(a: A, b: A) => Acc` 함수와 `Iterable<A>`만 받는다. 이터러블의 첫 요소가 초깃값이 된다.
- ③ 마지막 인자 `iterable`이 없는 경우: 두 번째 인자 `accOrIterable`이 이터러블이다. 이터레이터로 변환해 첫 요소를 꺼내고, 빈 이터러블이면 에러를 던지며, 요소가 있으면 `baseReduce`를 실행한다.
- ④ 세 인자를 모두 받은 경우: `accOrIterable`이 초깃값이고 `iterable`이 이터러블이다.

```typescript
// reduce 사용 예제
// 초깃값을 포함한 예제
const array = [1, 2, 3];
const sum = reduce((acc, a) => acc + a, 0, array);
console.log(sum); // 6

// 초깃값을 포함하지 않은 예제
const array2 = [1, 2, 3];
const sum2 = reduce((a, b) => a + b, array2);
console.log(sum2); // 6

const words = ['hello', 'beautiful', 'world'];
const sentence = reduce((a, b) => `${a} ${b}`, words);
console.log(sentence); // [const sentence: string]
// hello beautiful world

const array3 = [3, 2, 1];
const str = reduce((a, b) => `${a}${b}`, array3);
console.log(str); // 321
```

`"hello beautiful world"` 같은 문제에서는 초깃값을 생략하는 패턴이 코드를 더욱 간결하게 만들고 가독성을 높인다 — 초깃값 `''`를 넣으면 첫 순회에서 `' hello'`처럼 공백이 앞에 붙는 문제를 보조 함수에서 따로 처리해야 하기 때문이다.

> **참고**: 3장의 es5 `_reduce`는 같은 스펙(초깃값 생략)을 `arguments.length` 검사로 처리했다. 접근은 같고, 이 절의 판은 타입 시그니처(오버로드)로 그 스펙을 **언어와 소통 가능한 형태**로 격상시킨 것이다.

## 10. reduce의 에러 관리

초깃값을 생략한 `reduce`가 빈 이터러블을 만나면 `TypeError`를 던진다. 이 에러 처리를 어떻게 바라보고 관리해야 할까?

**첫 번째, 초깃값을 명시적으로 넣는 방법.** 가장 간단한 해결 방식이다. 빈 배열이라도 에러 없이 진행되며 사용자가 직접 결정한 초깃값(`0`, `''` 등)을 반환한다. '빈 배열이면 어떤 값을 반환할지'를 명확하게 정하는 방식이다. 하지만 초깃값만으로 모든 상황을 해결할 수는 없다 — `"hello beautiful world"` 사례처럼 초깃값을 넣으면 보조 함수에서 '빈 값이면(첫 순회)'에 대한 예외 처리를 해야 하고, 모든 순회에서 추가 조건문을 거치게 되어 코드가 복잡해진다. 초깃값 방식이 적합한지는 전체 로직과 보조 함수의 동작에 따라 결정해야 한다.

**두 번째, 빈 배열을 미리 체크해 기본값을 반환하는 early return 방법.** 프로그램의 정상 동작 범위에서 빈 배열이 충분히 들어올 수 있고 그때 반환할 기본값이 의미가 있다면 적용할 수 있다. 예를 들어 ``arr => arr.length === 0 ? '' : arr.reduce((a, b) => `${a} ${b}`)`` 같은 형태다. `Array`·`Set`처럼 길이를 미리 알 수 있는 자료구조일 때 가능하다.

**세 번째, `try/catch`로 에러를 처리하는 방법.** 빈 이터러블이 프로그램의 정상 범위에 속하지 않고 초깃값을 쓸 이유도 없다면 `try/catch`로 처리하거나, '이 경우는 에러가 맞으니 해결이 필요하다'는 명확한 의도 아래 에러를 그대로 던지도록 둘 수 있다. '정상 범위가 아니다'라는 사실을 개발자가 인지하고 최종적으로 어딘가에서 에러를 감지하도록 준비해야 한다.

마지막으로 **지연 이터레이터인 경우**에는 두 가지 접근이 가능하다 — `reduce`에 전달하기 전에 배열로 변환해 길이를 체크하거나(빈 배열이면 기본값 반환 로직이 가능해짐), 끝까지 평가를 미루면서 `reduce`에 넘기고 에러를 처리하는 방식이다. 초깃값 없이 지연 이터레이터를 전달하려면, 에러 처리를 할 것인지 아니면 이상 상황이 발생하지 않는다고 가정해도 되는지를 판단해 결정해야 한다.

에러 핸들링과 옵셔널한 값 처리에 대한 여러 관점은 Part 4(특히 15장)에서 이어진다.

## 11. 중첩된 함수들의 타입 추론

타입을 잘 정의한 함수는 함수들을 중첩하여 평가할 때도 코드 전반에서 타입 추론을 원활하게 처리한다. 고차 함수에 인자로 전달된 모든 함수의 인자 타입이 추론되므로, 개발자는 직접 타입을 정의하지 않고도 안전한 코드를 작성할 수 있다.

```typescript
// map + filter + forEach
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

주석에 표현된 것처럼 모든 보조 함수의 인자 타입이 추론되어, `printNumber`에 `number` 타입의 인자가 전달되는 것까지 안전하게 처리된다. 이러한 함수 세트를 잘 구성하면 안전하고 효율적이며 유연하고 생산성 높은 함수형 프로그래밍을 구현할 수 있다.

## 요약

- 이터러블 고차 함수의 공통 태도: **반환값으로 대화**하고, 로직은 보조 함수에 위임하며, 이터러블 프로토콜로 다형성을 얻는다.
- forEach·map·filter는 각각 **for...of / while / 객체 리터럴** 세 방식으로 구현할 수 있고, 세 구현은 완전히 호환된다 — 명령형·객체지향·프로토콜 직접 조작의 1:1:1 관계.
- `for...of`는 `break`·예외로 중단될 때 이터레이터의 `return()`을 자동 호출한다(**IteratorClose**) — 외부 리소스를 순회할 때 결정적인 차이다.
- 객체 리터럴 filter의 재귀 `next()`는 TCO가 가능한 구조지만 V8이 지원하지 않으므로 무한 루프 형태로 바꿔 안전하게 만든다.
- 제네릭 타입 매개변수로 이터러블의 요소 타입과 보조 함수의 인자 타입을 연결하면(`Iterable<A>` ↔ `(a: A) => B`), 중첩 조합에서도 타입 추론이 끝까지 흐른다.
- reduce의 초깃값 생략은 **함수 오버로드**로 표현하고, 빈 이터러블 에러는 초깃값 명시·early return·try/catch·(지연이라면) 사전 변환 중 상황에 맞게 관리한다.

## 다른 챕터와의 관계

- **2장**: es5 `_map`/`_filter`(length 기반)가 이 장에서 프로토콜 기반으로 진화했다.
- **3장**: es5 `_reduce`의 초깃값 생략(arguments 검사)이 이 장에서 타입 오버로드로 정식화됐다.
- **5·6장**: 이 장의 구현들은 이터레이션 프로토콜(5장)과 제너레이터(6장) 위에 서 있다.
- **8장**: 이 장의 함수들이 반환하는 "평가가 지연된 이터레이터"의 실행 순서를 정밀 추적한다.
- **9장**: 이 장에서 실전으로 사용한 제네릭·타입 추론의 원리를 다룬다.
- **10장**: 같은 함수들이 FxIterable 클래스의 메서드로 옮겨져 체이닝과 타입 추론을 동시에 얻는다.
