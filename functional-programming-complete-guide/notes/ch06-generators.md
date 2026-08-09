# Chapter 6: Generators (제너레이터)

## 핵심 질문

제너레이터는 어떻게 명령형 코드로 이터레이터를 만드는가? "문장을 값으로 만든다"는 것은 무슨 뜻이며, 제너레이터의 조합은 어떻게 재사용성을 높이는가?

---

5장에서 객체 리터럴로 이터레이터를 직접 구현했다. 이 장의 제너레이터는 같은 이터레이터를 **명령형 코드로** 생성하는 도구다. 실제로 어떤 문제는 명령형 스타일로 해결하는 것이 더 효율적이면서 직관적일 때가 있다. 제너레이터는 객체지향(반복자 패턴), 함수형(일급 함수), 명령형 스타일이 서로 협력할 수 있게 하는 중요한 기반을 제공한다.

---

## 1. 제너레이터 기본 문법

제너레이터는 명령형 스타일로 이터레이터를 작성할 수 있게 해주는 문법이다. 제너레이터 함수는 `function*` 키워드로 정의되며 호출 시 곧바로 실행되지 않고 이터레이터 객체를 반환한다. 이 객체를 통해 함수의 실행 흐름을 외부에서 제어할 수 있다.

### 1.1 yield와 next

제너레이터 함수가 반환한 이터레이터에 대해 `next()` 메서드를 호출하면 제너레이터 함수의 본문이 `yield` 키워드를 만날 때까지 실행된다. `yield` 키워드를 통해 외부로 값을 반환하고, 이후 `next()`를 다시 호출하면 이전 실행 지점부터 이어서 함수가 재개된다. 이렇게 `yield`와 `next()`를 조합하면 함수 내부 상태를 유지하며 순차적으로 값을 반환하는 구조를 쉽게 구현할 수 있다.

```typescript
// 간단한 generator 함수
function* generator() {
  yield 1;
  yield 2;
  yield 3;
}

const iter = generator();

console.log(iter.next()); // { value: 1, done: false }
console.log(iter.next()); // { value: 2, done: false }
console.log(iter.next()); // { value: 3, done: false }
console.log(iter.next()); // { value: undefined, done: true }
```

`generator` 함수는 호출 즉시 이터레이터 객체를 반환한다. `iter.next()`를 호출할 때마다 `yield` 지점까지 실행되어 값을 반환하고 함수의 실행을 일시 중지한다. 만일 `yield 1;`과 `yield 2;` 사이에 `console.log('hi');`가 있다면 다음과 같이 동작한다.

```typescript
// 제너레이터의 일시 중지
function* generator() {
  yield 1;
  console.log('hi');
  yield 2;
  yield 3;
}

const iter = generator();

console.log(iter.next());
// { value: 1, done: false }
console.log(iter.next()); // hi ← 이때 console.log('hi');가 실행됨
// { value: 2, done: false }
console.log(iter.next());
// { value: 3, done: false }
console.log(iter.next());
// { value: undefined, done: true }
```

`iter.next()`를 처음 호출하면 1이 반환되고 함수는 `console.log('hi');` 이전 지점에서 일시 중지된다. 두 번째 호출에서 'hi'가 출력되고 2가 반환된다.

### 1.2 제너레이터와 제어문

제너레이터는 명령형으로 구현하기 때문에 조건문을 사용할 수 있다.

```typescript
// 조건문을 사용한 제너레이터
function* generator(condition: boolean) {
  yield 1;
  if (condition) {
    yield 2;
  }
  yield 3;
}

const iter1 = generator(false);

console.log(iter1.next()); // { value: 1, done: false }
console.log(iter1.next()); // { value: 3, done: false }
console.log(iter1.next()); // { value: undefined, done: true }
```

조건이 `false`이므로 `yield 2;`는 실행되지 않고 바로 3이 반환된다. `true`를 전달하면 두 번째 `yield`가 실행된다. 이처럼 제너레이터 안에서 `if` 문을 사용하여 **이터레이터가 리스트를 만드는 로직을 제어**할 수 있다.

### 1.3 yield* 키워드

`yield*` 키워드는 제너레이터 함수 안에서 이터러블을 순회하며 해당 이터러블이 제공하는 요소들을 순차적으로 반환하도록 해준다. `[2, 3]` 같은 배열은 이터러블이므로 `for...of` 문이나 전개 연산자뿐 아니라 `yield*`를 통해서도 순회할 수 있다.

```typescript
// yield*를 사용한 제너레이터
function* generator() {
  yield 1;
  yield* [2, 3];
  yield 4;
}

const iter = generator();

console.log(iter.next()); // { value: 1, done: false }  ①
console.log(iter.next()); // { value: 2, done: false }  ②
console.log(iter.next()); // { value: 3, done: false }  ③
console.log(iter.next()); // { value: 4, done: false }  ④
console.log(iter.next()); // { value: undefined, done: true }
```

1. `iter.next()`를 호출하면 `yield 1`이 실행되어 1을 반환하고 함수는 일시 중지된다.
2. 두 번째 호출에서 `yield* [2, 3]`이 실행되어 배열의 요소를 차례로 반환하기 시작한다 — `yield 2`를 한 것과 동일하다.
3. 세 번째 호출은 `yield 3`을 한 것과 동일하게 3을 반환한다.
4. 네 번째 호출에서 `yield 4`가 실행된다.

`yield* iterable`은 `for (const val of iterable) yield val;`과 같다 — 이 등가 관계는 8장의 `L.flatten`을 간결하게 만드는 열쇠가 된다.

### 1.4 naturals 제너레이터 함수

다음은 자연수의 무한 시퀀스를 생성하는 제너레이터 함수다.

```typescript
// naturals 제너레이터 함수
function* naturals() {
  let n = 1;
  while (true) {
    yield n++;
  }
}

const iter = naturals();

console.log(iter.next()); // { value: 1, done: false }
console.log(iter.next()); // { value: 2, done: false }
console.log(iter.next()); // { value: 3, done: false }
// 계속해서 호출할 수 있다.
```

`naturals`는 무한 루프를 사용하지만 `iter.next()`를 호출할 때만 `n`을 반환하고 다시 일시 중지하기 때문에 프로세스나 브라우저가 멈추지 않는다. 이터레이터는 지연적인 특성을 가지는데 제너레이터 역시 이터레이터를 반환하며, 내부 코드도 `next()`를 실행한 만큼만 평가된다. **제너레이터는 코드를 지연 실행한다.**

## 2. 제너레이터로 작성한 reverse

5장에서 객체 리터럴로 구현했던 `reverse`를 제너레이터로 다시 작성해 보자.

```typescript
// 제너레이터로 작성한 reverse 함수
function* reverse<T>(arrayLike: ArrayLike<T>): IterableIterator<T> {
  let idx = arrayLike.length;
  while (idx--) {
    yield arrayLike[idx];
  }
}

const array = ['A', 'B', 'C', 'D', 'E', 'F'];
const reversed = reverse(array);

console.log(reversed.next().value); // F
console.log(reversed.next().value); // E
console.log(reversed.next().value); // D
```

객체 리터럴 판은 `idx`라는 상태를 바라보는 `next()` 메서드를 가진 객체로 구현했고, 제너레이터 판은 제어문을 활용한 명령형 코드로 작성했다. 구현은 다르지만 동작은 동일하고, 해결한 문제도 동일하다.

> **핵심 통찰**: 현대 언어에서는 동일한 문제를 객체지향 방식(이터레이터 객체 직접 구현)이나 명령형(제너레이터) 등 여러 패러다임 중 하나를 선택해 해결할 수 있다. 이터레이터를 객체지향으로도, 명령형으로도, 함수형으로도 구현하며 이들이 서로 1:1:1로 호환되는 것 — 이것이 이 가이드 전체를 관통하는 관점이다(11장에서 Generator:Iterator:LISP = IP:OOP:FP로 확장된다).

## 3. 제너레이터로 만든 이터레이터도 이터러블

제너레이터는 항상 `IterableIterator`를 반환한다. 5장의 `map`을 제너레이터로 다시 구현해 보자.

```typescript
// map 함수
function* map<A, B>(
  f: (value: A) => B, iterable: Iterable<A>
): IterableIterator<B> {
  for (const value of iterable) {
    yield f(value);
  }
}
```

`map` 함수는 `f` 함수와 이터러블 객체를 인자로 받아 각 요소에 `f`를 적용한 결과를 `yield`로 반환한다.

```typescript
// 제너레이터로 만든 map 함수 사용 예제
const array = [1, 2, 3, 4];
const mapped: IterableIterator<number> = map((x) => x * 2, array); // ①
const iterator = mapped[Symbol.iterator]();

console.log(mapped.next().value);   // ② 2
console.log(iterator.next().value); // ③ 4
console.log([...iterator]);         // ④ [6, 8]
```

- ① `map((x) => x * 2, array)`: `array`의 각 요소에 2배 연산을 적용할 준비가 된 `IterableIterator<number>`를 반환한다.
- ② `mapped.next()`와 `iterator.next()`: 같은 이터레이터를 참조하므로(well-formed) 이미 소비된 요소는 다시 나오지 않는다.
- ④ 전개 연산자(`...iterator`): 남은 요소만을 배열로 만들어 `[6, 8]`을 얻는다.

제너레이터로 만든 이터레이터도 이터러블이므로 `for...of` 문으로 순회할 수 있고, `naturals()` 같은 다른 이터레이터와도 조합할 수 있다.

```typescript
// map((x) => x * 2, naturals(4))
let acc = 0;
for (const num of map((x) => x * 2, naturals(4))) {
  acc += num;
}

console.log(acc); // 20
```

`map`에 배열이 아닌 지연 평가되는 이터레이터를 전달했고, 실행 과정에서 배열을 만들지 않고도 `acc`에 모든 값을 더했다. 일반 함수로 이터레이터를 만들 수 있고, 제너레이터로도 생성할 수 있으며, 서로 주고받으며 `for...of`나 `next()`로 순회할 수 있다 — 이터레이션 프로토콜이 패러다임 사이의 전환과 조합을 가능하게 한다.

## 4. return 값은 순회에 포함되지 않는다

제너레이터에서 주의할 동작 하나. 제너레이터 함수의 `return` 값은 `next()`로는 확인되지만 **순회에는 포함되지 않는다.**

```typescript
let isSecond = false;
function* generator() {
  yield 1;
  if (isSecond) yield 2;
  yield 3;
  return 100; // 리턴 값이 있지만 순회 시에는 포함되지 않음
}

let iter = generator(); // 제너레이터를 실행한 결과는 이터레이터
console.log(iter[Symbol.iterator]() === iter); // true - 이터레이터는 자기 자신을 반환하는 Symbol.iterator 메서드를 가짐

console.log(iter.next()); // { value: 1, done: false }
console.log(iter.next()); // { value: 3, done: false } (isSecond가 false이므로 2는 생략됨)
console.log(iter.next()); // { value: 100, done: true } (return 값)
console.log(iter.next()); // { done: true } (value가 없음)

// for...of로 순회 시 return 값은 포함되지 않음
for (const a of generator()) console.log(a); // 1, 3
```

`return 100`은 `{ value: 100, done: true }`로 나타난다 — `done`이 `true`이므로 `for...of`·전개 연산자 등 이터레이션 프로토콜 기반 순회는 이 값을 소비하지 않는다.

## 5. 제너레이터 조합으로 재사용성 높이기

제너레이터가 조합 가능한 부품이라는 것을 홀수 생성기를 개선해 가며 확인해 보자.

### 5.1 기본 홀수 생성기

```typescript
function* odds(l) {
  for (let i = 0; i < l; i++) {
    if(i % 2) yield i;
  }
}
```

- 특징: 0부터 l-1까지 직접 반복하며, 홀수 생성과 범위 제한이 결합돼 있다.
- 단점: 무한 수열 생성이 불가능하며, 재사용성이 낮고 확장성이 떨어진다.

### 5.2 무한 수열 도입

```typescript
function* infinity(i = 0) {
  while (true) yield i++;
}

function* odds(l) {
  for (const i of infinity(1)) {
    if (i % 2) yield i;
    if (i >= l) return;
  }
}
```

- 개선점: 무한 수열을 생성하는 부분을 분리했고, 조건문으로 부분 값 매칭이 가능하며, 확장성이 높다.
- 한계: 여전히 홀수 생성과 범위 제어가 결합돼 있어 다른 필터 조건을 적용하기 어렵다.

### 5.3 모듈화

```typescript
function* infinity(i = 0) {
  while (true) yield i++;
}

function* limit(l, iter) {
  for (const a of iter) {
    yield a;
    if (a >= l) return;
  }
}

function* odds(l) {
  for (const a of limit(l, infinity(1))) {
    if (a % 2) yield a;
  }
}
```

계층이 분리됐다.

- **`infinity`**: 순차적 숫자 생성 (기본 데이터 소스)
- **`limit`**: 범위 제한 필터 (중간 처리기)
- **`odds`**: 홀수 필터 (최종 처리기)

`odds`는 순수하게 홀수를 필터링하는 역할만 하므로 다른 필터 함수를 만들려면 해당 부분만 바꾸면 된다. `limit`은 짝수 생성이나 피보나치 수열 등 다른 제너레이터와도 조합할 수 있다. 제너레이터를 중첩하면 **명령형 코드로도 파이프라인과 같은 조합 구조**를 만들 수 있다 — 8장의 지연 파이프라인(L.range → L.map → take)이 정확히 이 구조 위에 서 있다.

## 6. 문장을 값으로 만드는 제너레이터

제너레이터의 본질을 다른 각도에서 표현하면 "순회할 값을 문장으로 표현한 것"이다.

1. **프로그래밍에서 문장(statement)**: 어떤 동작을 수행하는 코드의 한 줄 또는 한 구문이다.
	```typescript
let x = 10;        // 변수 선언 및 할당 (문장)
console.log(x);    // 출력 (문장)
yield 1;           // 값을 내보내고 실행을 멈춤 (문장)
	```
2. **프로그래밍에서 값(value)**: 변수에 저장되거나 함수에서 반환될 수 있는 데이터 그 자체다.
	```typescript
10                // 숫자 값
'hello'           // 문자열 값
true              // 불리언 값
[1, 2, 3]         // 배열 값
	```
3. **"문장을 값으로 만든다"의 의미**: 일반적으로 문장은 실행만 되고 그 결과가 값으로 직접 다뤄지지 않는다. 제너레이터에서 `yield`를 사용하면 **실행되는 문장이 값으로 외부에 전달된다**. 즉 코드의 실행 흐름(문장)을 끊어서, 그 중간 결과(값)를 바깥에서 하나씩 받을 수 있게 만든다.
	```typescript
function* userFlow() {
  const name = yield '이름 입력:';  // 첫 번째 값
  const age = yield '나이 입력:';   // 두 번째 값
  yield `${name}님, ${age}세 환영!`; // 최종 값
}

const flow = userFlow();

// 값 추출 과정
console.log(flow.next().value); // "이름 입력:"
console.log(flow.next('김코딩').value); // "나이 입력:"
console.log(flow.next(25).value); // "김코딩님, 25세 환영!"
	```

`next(인자)`로 값을 넣으면 일시 중지됐던 `yield` 표현식의 결과가 그 인자가 된다 — 문장의 흐름을 외부와 주고받는 대화로 바꾼 것이다. "코드(문장)를 값으로 다룬다"는 이 감각은 11장(코드가 곧 데이터 — LISP)에서 패러다임 전체의 등식으로 확장된다.

## 요약

- 제너레이터는 `function*`과 `yield`로 **명령형 코드에서 이터레이터를 생성**하는 문법이며, `next()`가 호출될 때마다 다음 `yield`까지 실행하고 일시 중지한다 — 코드의 지연 실행.
- `yield*`는 이터러블을 위임 순회하며, `for (const v of iterable) yield v;`와 같다.
- 무한 루프(`while (true) yield n++`)도 안전하다 — 호출한 만큼만 평가되기 때문이다.
- 제너레이터의 `return` 값은 `{ done: true }`와 함께 반환되므로 **순회에 포함되지 않는다.**
- 같은 이터레이터를 객체 리터럴(OOP)로도 제너레이터(명령형)로도 만들 수 있다 — 패러다임 간 1:1 호환.
- `infinity`·`limit`·`odds`처럼 제너레이터를 계층으로 분리하면 명령형 코드로도 조합 가능한 부품이 만들어진다.
- `yield`는 **문장을 값으로** 만든다 — 실행 흐름의 중간 결과를 외부에서 하나씩 받고, `next(인자)`로 되돌려줄 수도 있다.

## 다른 챕터와의 관계

- **5장**: 객체 리터럴로 직접 구현했던 이터레이터·`naturals`를 제너레이터가 대체하며, 제너레이터의 반환값 역시 well-formed 이터러블이다.
- **7장**: 이 장의 제너레이터 `map`이 forEach·filter와 함께 세 가지 구현 방식으로 확장된다.
- **8장**: `yield*`가 `L.flatten`·`deepFlat`·`concat`의 재료이고, `infinity`/`limit` 구조가 지연 파이프라인으로 일반화된다.
- **11장**: "문장을 값으로"가 Generator:Iterator:LISP = IP:OOP:FP 등식으로 확장된다.
- **14장**: 제너레이터의 비동기 판(AsyncGenerator·toAsync)이 등장한다.
