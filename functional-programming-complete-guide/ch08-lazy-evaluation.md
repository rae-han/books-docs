# Chapter 8: Lazy Evaluation (지연 평가)

## 핵심 질문

지연 평가는 실제로 어떤 순서로 코드를 실행하는가? map·filter 같은 "지연하는 함수"와 take·reduce·find 같은 "결과를 만드는 함수"는 어떻게 역할이 나뉘며, 이 조합은 어떻게 무한 수열과 대용량 데이터를 효율적으로 다루게 해주는가?

---

7장에서 이터러블을 다루는 고차 함수를 만들었다. 이 장에서는 그 함수들이 가진 가장 강력한 성질인 **지연성**을 파고든다. 먼저 즉시 평가 함수와 지연 평가 함수를 직접 만들어 성능을 비교하고, 중첩된 이터레이터가 실제로 어떤 순서로 평가되는지 로그와 이터레이터 구현으로 추적한다. 마지막으로 지연 평가 위에서 find, every, some, flatten, flatMap, concat을 조합해 만든다.

**표기법 안내 — 같은 원리, 세 가지 표기.** 이 장에는 두 소스의 코드가 함께 실려 있어 표기가 섞여 있다. 셋 다 "지연 이터레이터를 조합한다"는 같은 원리의 다른 표기다.

| 표기 | 예 | 맥락 |
|---|---|---|
| `L.*` + `go`/`pipe` | `go(iter, L.filter(f), take(1))` | ES6+ 노트 계열(fxjs). 동적 타입 JS에서 파이프라인 가독성이 좋다 |
| 자유 함수 중첩 | `head(filter(f, iterable))` | 언어 중립적, LISP식 중첩 |
| `fx()` 체이닝 | `fx(iter).filter(f).take(1)` | 멀티패러다임 책 계열. 10장에서 직접 구현한다 |

`go`/`pipe` 스타일이 `fx` 체이닝으로 진화한 데는 이유가 있다. 타입스크립트에서 가변 인자 파이프라인(`pipe(f1, f2, f3, ...)`)은 단계 사이의 타입을 이어주기 위해 수많은 오버로드 시그니처가 필요하고, 중간 단계에서 추론이 끊기기 쉽다. 반면 메서드 체이닝은 각 메서드가 자신의 원소 타입 `A`를 아는 상태에서 시작하므로 타입 추론이 자연스럽게 흐른다. 파이프 연산자(`|>`)가 아직 표준화 논의(Stage 2) 단계에 머물러 있는 상황에서, 클래스 체이닝은 언어 기능만으로 파이프라인 표현력과 타입 안전을 동시에 얻는 실용적 해법이다.

> **핵심 통찰**: 이 장의 코드 표기가 섞여 있는 것은 의도된 것이다. `L.*`/`go` 세대(동적 타입 JS)와 `fx` 체이닝 세대(정적 타입 TS)를 나란히 두면, 같은 지연 평가 원리가 타입 시스템이라는 제약 아래 어떻게 다른 표면 문법으로 수렴했는지가 보인다. 3장에서 go/pipe를 만들고, 10장에서 FxIterable을 만들며 이 진화를 각각 확인한다.

---

## 1. 지연 평가란 — 제때 계산법

**지연 평가(*Lazy Evaluation*)**는 "게으른 평가"라고도 하지만, 실제로는 필요할 때까지 계산을 미루고 정말 필요할 때만 계산하는 영리한 평가 방식이다. 값을 미리 계산해 두지 않고, 실제로 그 값이 필요해질 때 코드를 실행해서 값을 만들어낸다. 이런 방식은 불필요한 계산과 메모리 사용을 줄이고, 무한한 데이터 구조도 다룰 수 있게 해준다. 그런 이유로 제때 계산법(*call-by-need*)이라 표현되기도 한다.

ES6 이전에는 자바스크립트에서 지연 평가를 위한 공식적인 프로토콜(규약)이 없어 공식적인 구현이 어려웠다. 하지만 ES6 이후 제너레이터와 이터레이터, 그리고 이터러블 프로토콜이 도입되면서 언어 차원에서 지연 평가를 표준적으로 지원하게 됐다. 그래서 코드를 값처럼 다루고, 안전하게 조합할 수 있게 된 것이다.

## 2. 즉시 평가 range vs 지연 평가 L.range

숫자를 받아 그 크기의 배열을 리턴하는 함수를 만든다면 아래와 같이 만들 수 있다.

```typescript
const range = (length) => {
	let i = -1;
	const result = [];

	while (++i < length) {
		result.push(i);
	}

	return result;
};
```

이 함수를 이용해 합을 구한다면 다음과 같다.

```typescript
const list = range(5);
console.log(reduce(add, list)); // 10
```

이 `range` 함수를 제너레이터를 사용해 느긋한 함수로 만들 수 있다.

```typescript
const L = {};

L.range = function* (length) {
	let i = -1;

	while (++i < length) {
		yield i;
	}
}
```

결과 값은 같다.

```typescript
const list = L.range(5);
console.log(reduce(add, list)); // 10
```

하지만 실제로 양쪽의 `list`를 확인하면 앞은 배열, 뒤는 이터레이터로 서로 다르다.

- `[ 0, 1, 2, 3, 4 ]`
- `Object [Generator] {}`

그런데도 둘 다 같은 결과를 만든 이유는, `reduce` 함수가 이터러블 프로토콜을 따르기 때문에 이터레이터도 평가할 수 있어서다.

두 함수의 결정적인 차이는 **평가 시점**이다. `range` 함수는 `list`에 담기는 단계에서 코드가 완전히 평가되지만, `L.range`는 다르다. 실제 평가를 일으키는 `reduce` 부분을 주석 처리하고 `while` 문 안에서 로그를 찍어 보면, `range`는 인덱스 `i`가 출력되지만 `L.range`는 아무것도 출력되지 않는다. 함수의 어떤 부분도 아직 실행되지 않은 것이다.

`L.range`의 코드가 평가되는 시점은 이터레이터 내부를 순회할 때마다 하나씩이다. `next()`를 하기 전에는 어떤 코드도 동작하지 않는다. 즉 `L.range`는 배열로 바로 평가되는 것이 아니라 `reduce` 함수 안에서 해당 값이 필요해질 때 평가가 이뤄진다.

효율 차이도 있다. `range`는 Array를 다 만든 후 배열로 전달되어 동작하고, `L.range`는 Array를 만들지 않고 하나씩 값을 꺼내기만 한다. 조금 더 깊이 보면, `range`가 만든 배열은 `reduce` 안에서 다시 이터레이터로 변환된 다음 순회된다. 반면 `L.range`는 실행됐을 때 이미 이터레이터이고, well-formed 이터레이터는 `[Symbol.iterator]()`가 자기 자신을 반환하므로 그대로 순회에 들어간다. 그래서 좀 더 효율적이다.

간단한 테스트 함수로 비교해 보자.

```typescript
const test = (name, time, fn) => {
	console.time(name);
	while (time--) {
		fn();
	}
	console.timeEnd(name);
};
```

```typescript
test('range', 10, () => reduce(add, range(1000000)));
test('L.range', 10, () => reduce(add, L.range(1000000)));
```

환경에 따라 다르겠지만 `L.range` 함수가 평균 30% 정도 더 빠른 것을 확인할 수 있다.

## 3. take — 필요한 만큼만

`take`는 이터러블에서 특정 개수의 요소를 추출하는 함수다.

```typescript
const take = (l, iter) => {
	let res = [];

	for (const a of iter) {
		res.push(a);

		if (res.length >= l) {
			return res;
		}
	}

	return res;
};
```

이터러블을 받아 순회하며 값을 모으는 단순한 로직이다. 그리고 앞서 만든 지연성을 가진 `L.range`도 그대로 사용할 수 있다. 전혀 다른 함수지만 모두 이터러블 프로토콜을 따르고 있기 때문이다.

```typescript
console.log(take(5, range(100))); // [0, 1, 2, 3, 4]
console.log(take(5, L.range(100))); // [0, 1, 2, 3, 4]
```

첫 번째 코드는 100개 값을 전부 만들고 순회하지만, 두 번째 코드는 필요한 5개 값만 꺼내 쓰므로 효율적이다. 나아가 `L.range(Infinity)`처럼 무한 수열을 전달해도 문제없다 — 어차피 필요한 만큼만 평가하기 때문이다. `take` 역시 curry를 적용해 파이프라인에서 쓰기 좋게 만들 수 있다.

정리하면, 제너레이터/이터레이터를 리턴하는 함수를 실행했을 때 해당 연산이 그 안에서 즉시 이뤄지지 않고 미뤄지다가, 필요할 때 값을 꺼내 쓰는 기법이 지연 평가다.

## 4. L.map과 L.filter

7장에서 만든 즉시 평가 `map`을 제너레이터 기반의 지연 함수로 다시 구현해 보자. 필요할 때만 값을 변환한다.

```typescript
L.map = function* (f, iter) {
	for (const a of iter) {
		yield f(a);
	}
};
```

이 함수는 제너레이터 프로토콜을 따르고, 그 반환값(`value`, `done` 프로퍼티)은 이터레이터 프로토콜 사양을 충족한다. `filter`도 마찬가지다.

```typescript
L.filter = function* (f, iter) {
	for (const a of iter) {
		if (f(a)) {
			yield a;
		}
	}
};
```

즉시 평가 함수와 코드 모양은 거의 같지만, `yield` 덕분에 순회 한 번마다 멈추는 함수가 되었다. 이 차이가 실행 순서를 완전히 바꾼다.

## 5. 중첩 이터레이터의 실행 순서

지연 평가를 지원하는 자료구조인 이터레이터의 실제 실행 순서를 면밀히 살펴보자.

### 5.1 제너레이터 로그로 확인하기

각 함수의 루프 내부에 로그를 남기면, `take`·`map`·`filter`를 조합해 만든 중첩 이터레이터가 어떤 순서로 실행되는지 추적할 수 있다.

```typescript
// 지연 평가의 실행 순서
function* filter<A>(f: (a: A) => boolean, iterable: Iterable<A>): IterableIterator<A> {
  const iterator = iterable[Symbol.iterator]();
  while (true) {
    console.log('filter');
    const { value, done } = iterator.next();
    if (done) break;
    if (f(value)) yield value;
  }
}

function* map<A, B>(f: (a: A) => B, iterable: Iterable<A>): IterableIterator<B> {
  const iterator = iterable[Symbol.iterator]();
  while (true) {
    console.log('map');
    const { value, done } = iterator.next();
    if (done) break;
    yield f(value);
  }
}

function* take<A>(limit: number, iterable: Iterable<A>): IterableIterator<A> {
  const iterator = iterable[Symbol.iterator]();
  while (true) {
    console.log('take limit:', limit);
    const { value, done } = iterator.next();
    if (done) break;
    yield value;
    if (--limit === 0) break;
  }
}

const iterable = fx([1, 2, 3, 4, 5])
  .filter(a => a % 2 === 1)
  .map(a => a * a)
  .take(2);

for (const a of iterable) {
  console.log('result:', a);
}
// ??
```

이 코드는 어떤 순서로 로그를 출력할까? (1) filter가 모두 실행된 다음 map이 모두 실행되거나, (2) filter → map → take 순으로 하나씩 실행될 것이라 예상하기 쉽다. 하지만 실제 결과는 다르다.

```
// 실제 출력 결과 (value 로그를 추가한 버전 기준)
// take limit: 2
// map
// filter
// filter value f(value): 1 true
// map value f(value): 1 1
// take value: 1
// result: 1
// -
// take limit: 1
// map
// filter
// filter value f(value): 2 false
// filter
// filter value f(value): 3 true
// map value f(value): 3 9
// take value: 9
// result: 9
// -
```

결과를 보면 반대로 `take limit: 2`가 먼저 출력되고 이어서 `map`, `filter` 순으로 출력된다. `take`까지 실행한 결과로 만들어진 이터레이터의 `next()`를 `for...of`문이 처음 호출할 때, `take` 함수의 `while` 루프부터 실행되기 때문이다. 루프 내부에서 `take limit: 2`를 출력하고, 바로 다음 줄에서 `take`는 자신이 인자로 받은 이터레이터의 `next()`를 호출한다. 이 이터레이터는 `map`까지 실행한 이터레이터이므로 `map`의 `while` 루프 내부가 실행되어 `map`이 출력되고, 같은 원리로 `filter`가 출력된다.

### 5.2 이터레이터로 직접 살펴보기

왜 이런 순서가 되는지 확인하기 위해 `map`과 `take`의 반환값을 객체지향 방식의 이터레이터로 직접 구현해 보자.

```javascript
// map, take 함수 (순수 자바스크립트)
function map(f, iterable) {
  const iterator = iterable[Symbol.iterator]();
  return {
    next() {
      const { done, value } = iterator.next();
      return done
        ? { done, value }
        : { done, value: f(value) };
    },
    [Symbol.iterator]() {
      return this;
    }
  };
}

function take(limit, iterable) {
  const iterator = iterable[Symbol.iterator]();
  return {
    next() {
      if (limit === 0) return { done: true };
      const { done, value } = iterator.next();
      if (done) return { done, value };
      limit--;
      return { done, value };
    },
    [Symbol.iterator]() {
      return this;
    }
  };
}

const mapped = map(a => a * a, [10, 20, 30]);
const taked = take(2, mapped);

console.log(taked.next());
// take limit: 2 → map → map value f(value): 10 100 → take value: 100
// { done: false, value: 100 }

console.log(taked.next());
// take limit: 1 → map → map value f(value): 20 400 → take value: 400
// { done: false, value: 400 }

console.log(taked.next());
// { done: true }
```

첫 번째 `taked.next()`를 호출하면 `take`가 반환한 이터레이터의 `next` 메서드가 호출되고, 내부에서 `iterator.next()`로 `mapped`의 `next`를 호출한다. `mapped`는 다시 원본 배열의 이터레이터를 호출해 10을 받고, `f(value)`로 100으로 변환하여 반환한다. 최종적으로 `take`는 `{ done: false, value: 100 }`을 반환한다.

### 5.3 단순화해서 살펴보기

이 시각을 가지고 핵심 부분만 코드로 표현하면 다음과 같다.

```javascript
// 중첩 이터레이터의 내부 실행을 단순화하여 표현
const filtered = {
  next() {
    return iterator.next();
  }
}

const mapped = {
  next() {
    return filtered.next();
  }
}

const taked = {
  next() {
    return mapped.next();
  }
}

taked.next();
```

`taked.next()`를 실행하면 take → map → filter 순으로 진행하여 결과를 반환하면서 다시 filter → map → take 방향으로 돌아온다. `take`가 반환하는 이터레이터의 구현부를 보면 `{ next() {} }` 안에서 다시 `next()`를 실행한다. 말 그대로 이터레이터가 중첩되어 있다.

### 5.4 가로 평가와 세로 평가

즉시 평가 함수로 같은 로직을 구성하면 평가 방향이 다르다.

```typescript
go(
	range(10),
	map((n) => n + 1),
	filter((n) => n % 2),
	take(2),
	console.log,
);
```

```typescript
go(
	L.range(10),
	L.map((n) => n + 1),
	L.filter((n) => n % 2),
	take(2),
	console.log,
);
```

즉시 평가 버전은 `range(10)`의 모든 값이 `map`을 통과하고, 그 결과 전체가 `filter`를 통과한 뒤에야 `take`에 도착한다 — 값이 **가로로** 만들어진다. 지연 평가 버전은 실행 자체는 위에서 아래로 이뤄지지만, 브레이크 포인트를 찍어 보면 가장 먼저 진입하는 곳은 `take`다. `take`의 `iter` 매개변수에는 배열이 아니라 이터레이터(`Object [Generator] {}`)가 들어오고, `take`가 `next()`를 호출하는 순간 값 하나가 L.filter → L.map → L.range를 거슬러 올라가며 필요한 만큼만 평가된다 — 값이 **세로로** 만들어진다.

well-formed 이터레이터는 자기 자신이 이터레이터면서 `[Symbol.iterator]()`가 자기 자신을 반환하므로, `take` 안에서 `iter[Symbol.iterator]()`를 실행해도 `iter`는 여전히 같은 이터레이터다. 그래서 배열 같은 이터러블을 받아도, 제너레이터가 만든 이터레이터를 받아도 똑같이 동작한다. 이런 식으로 다형성이 잘 유지되도록 만들어져 있다.

> **참고**: 이 추적에 쓰인 `while (!(cur = iter.next()).done)` 형태의 명령형 구현은 7장에서 만든 고차 함수들의 while 판과 같은 형태다. `for...of`가 숨기고 있는 일을 드러내 보면 지연 평가의 흐름이 눈에 보인다.

## 6. map·filter 계열 함수들의 결합 법칙

map·filter 계열 함수는 이터러블 프로토콜을 따를 때, 함수 조합의 순서와 방식이 달라져도 결과가 달라지지 않는 결합 법칙을 가진다.

- 이 결합 법칙은 **이터러블 프로토콜을 따르는 map·filter**에서만 성립한다. Array의 map·filter 같은 메서드는 즉시 평가이기 때문에 해당되지 않는다.
- 지연 평가를 사용할 때 이 결합 법칙이 더욱 자연스럽게 적용된다. 각 값이 필요할 때마다, 필요한 연산만 순차적으로(세로로) 적용되기 때문이다.

## 7. 지연하는 함수와 결과를 만드는 함수

map·filter가 이터러블에 함수를 합성만 해두고 연산을 미루는 지연 함수라면, **reduce와 take는 이터러블 체인을 깨뜨려 즉시 평가하고 결과를 생성하는 함수**다. reduce·take가 연산의 시작을 알려 결과 값을 만들어내고, 함수를 종료하거나 다음 로직으로 이어간다.

물론 take도 값을 2개만 yield하는 식으로 지연성을 줄 수 있지만, 실제로 몇 개의 값이 들어올지 모르는 상황에서 특정 개수의 값으로 축약해 완성하는 성격을 띤다. 정리하면 **reduce는 모든 연산을 실행해 단일 값으로 축약**하고 **take는 필요한 개수만 추출해 배열로 완성**한다. 둘 다 이터러블 체인의 끝에서 사용되며, 실제 연산을 트리거하는 함수다.

### 7.1 예시: query string 만들기

```typescript
const obj = {
	limit: 10,
	offset: 10,
	type: 'notice',
};

go(
	obj,
	Object.entries,
	map(([k, v]) => `${k}=${v}`),
	reduce((acc, cur) => `${acc}&${cur}`),
	console.log,
);

const queryStr = pipe(
	Object.entries,
	map(([k, v]) => `${k}=${v}`),
	reduce((acc, cur) => `${acc}&${cur}`),
);
console.log(queryStr(obj));
```

### 7.2 reduce로 만드는 join

Array 프로토타입의 `join`이 아니라, 이터러블 프로토콜을 따라 순회 가능한 모든 값에 쓸 수 있는 다형성 높은 `join`을 만들 수 있다.

```typescript
const join = curry((sep = ',', iter) => reduce((a, b) => `${a}${sep}${b}`, iter));
```

이 함수는 이터러블 프로토콜을 따르므로 즉시 평가된 값뿐 아니라 지연 평가된(미뤄져 있는) 약속된 결과도 받을 수 있다.

```typescript
const queryStr = pipe(
  Object.entries,
  L.map(([k, v]) => `${k}=${v}`),
  join('&'),
)
```

pipe 중간에 함수를 끼워 중간 값을 확인해 보면 `Object.entries`는 즉시 결과를 만드는 함수임을 알 수 있다.

```typescript
const queryStr = pipe(
	Object.entries,
	(a) => (console.log(a), a), // 1
  function(a) {
    console.log(a) // 2
    return a;
  },
	L.map(([k, v]) => `${k}=${v}`),
	join('&'),
);
```

이때 `Object.entries`도 이터레이터로 결과를 흘려보내도록 지연 버전을 만들 수 있다.

```typescript
L.entries = function *(obj) {
  for (const k in obj) yield [k, obj[k]];
};
```

```typescript
const queryStr = pipe(
  L.entries,
  L.map(([k, v]) => `${k}=${v}`),
  join('&'),
  console.log,
)
```

### 7.3 takeAll — 지연 함수로 즉시 평가 함수 만들기

지연성을 가진 L.map, L.filter로 즉시 평가하는 map, filter를 만들 수 있다. 지연 평가로 만든 이터러블(제너레이터)을 `take(Infinity)`로 한 번에 모두 평가시키면 된다.

```typescript
const map = curry((fn, iter) => go(
  iter,
  L.map(fn),
  take(Infinity) // take를 통해 모두 가져와준다.
))
```

go 대신 pipe를 쓰면 더 간결해진다.

```typescript
const map = curry(pipe(L.map, take(Infinity)));
```

filter도 같다.

```typescript
const filter = curry(pipe(L.filter, take(Infinity)));
```

반복되는 `take(Infinity)`를 `takeAll`이라는 이름으로 만들어 두면 더 좋다.

```typescript
const takeAll = take(Infinity);
```

```typescript
const map = curry(pipe(L.map, takeAll));

const filter = curry(pipe(L.filter, takeAll));
```

> **핵심 통찰**: 즉시 평가 함수는 지연 함수의 특수한 경우로 환원된다. `map = L.map + takeAll`. 지연이 기본이고, 즉시는 "끝까지 평가하기로 결정한 지연"일 뿐이다.

## 8. find — 지연 평가와 안전한 합성

### 8.1 find의 시그니처와 두 언어의 해법

map이나 filter가 연산을 지연한 이터레이터를 만들어 리스트 프로세싱을 이어가게 하는 유형이라면, `find`는 지연된 이터레이터를 평가하여 **결과를 만드는 유형**의 함수다. find는 이터러블을 순회하면서 요소마다 `f`로 조건을 검사해 참으로 평가되는 첫 번째 요소를 반환하고, 만족하는 값이 없으면 `undefined`를 반환한다.

```typescript
// 타입스크립트의 find 함수 시그니처
type Find = <A>(f: (a: A) => boolean, iterable: Iterable<A>) => A | undefined;
```

하스켈의 find 시그니처도 보자.

```haskell
-- 하스켈의 find 함수 시그니처
find :: (a -> Bool) -> [a] -> Maybe a
```

최종 반환값 `Maybe a`는 조건을 만족하는 첫 요소가 있으면 `Just a`를, 없으면 `Nothing`을 반환하는 타입이다. 하스켈은 안전한 함수 합성을 위해 `A | undefined` 같은 상황을 `Maybe` 타입의 값으로 다룬다.

```haskell
-- 하스켈에서 find 함수 사용 예제
import Data.Maybe (fromMaybe)
import Data.List (find)

main :: IO ()
main = do
  let result = fromMaybe 0 (find even [1, 3, 5])
  print result  -- 출력: 0
```

`find even [1, 3, 5]`의 결과는 `Maybe` 타입인데, 리스트에 짝수가 없으므로 `Nothing`을 반환한다. `fromMaybe`는 `Nothing`일 경우 기본값 0을 반환한다. 프로그래밍 언어들은 값이 없을 수 있는(옵셔널한) 상황에 각기 다른 해법을 제안한다 — 하스켈은 선언적인 타입과 값으로 명확히 표현하고, 타입스크립트는 `?.`, `!`, `??` 연산자로 해결 방법을 제시한다.

### 8.2 find 구현 — 명령형에서 함수형까지

명령형으로 작성하면 다음과 같다.

```typescript
// 명령형 코드로 작성한 find 함수
function find<A>(f: (a: A) => boolean, iterable: Iterable<A>): A | undefined {
  const iterator = iterable[Symbol.iterator]();
  while (true) {
    const { value, done } = iterator.next();
    if (done) break;
    if (f(value)) return value;
  }
  return undefined;
}

const result = find(a => a > 2, [1, 2, 3, 4]);
console.log(result);
// 3
```

함수형 방식으로는, 지연 평가를 지원하는 filter에서 `next()`를 한 번만 평가하면 find와 동일한 로직·효율이 된다. 한 번만 평가한다면 `yield`는 사실상 `return`과 같기 때문이다.

```typescript
// 함수형 코드로 작성한 find (1)
function find<A>(f: (a: A) => boolean, iterable: Iterable<A>): A | undefined {
  return filter(f, iterable).next().value;
}

// 함수형 코드로 작성한 find (2)
const head = <A>(
  iterable: Iterable<A>
): A | undefined => iterable[Symbol.iterator]().next().value;

const find = <A>(
  f: (a: A) => boolean,
  iterable: Iterable<A>
): A | undefined => head(filter(f, iterable));

// 함수형 코드로 작성한 find (3)
const find = <A>(f: (a: A) => boolean, iterable: Iterable<A>): A | undefined =>
  fx(iterable)
    .filter(f)
    .to(head);
```

세 가지 방식 모두 명령형 find와 동일한 효율을 제공하면서도 코드가 간결하다. 각 패러다임으로 작성한 코드는 서로를 완전히 대체할 수 있으며, 필요하다면 섞어서 사용할 수도 있다.

### 8.3 로그로 확인하는 효율 차이 — filter vs L.filter

즉시 평가 filter로 find를 만들면 왜 비효율적인지 로그로 직접 확인할 수 있다. 우선 조건을 만족하는 값을 모두 거른 뒤 하나를 꺼내는 구성이다.

```typescript
const users = [
	{ age: 32 },
	{ age: 31 },
	{ age: 37 },
	{ age: 28 },
	{ age: 25 },
	{ age: 32 },
	{ age: 31 },
	{ age: 37 },
];

const find = (fn, iter) =>
	go(
		iter,
		filter(fn),
		take(1), // 하나만 꺼내도록.
		([a]) => a, // 배열을 깨서 값이 나가도록.
	);
```

이 함수는 하나의 값만 꺼내면 되는데 전체를 순회한다. 아래 로직으로 확인할 수 있다.

```typescript
const find = (fn, iter) =>
	go(
		iter,
		filter((a) => (console.log(a), fn(a))), // 전체 값이 로그에 찍힘
		take(1),
		([a]) => a,
	);
```

이때 filter 대신 지연성을 가진 L.filter를 사용하기만 해도, 평가(결과 연산)가 take까지 미뤄져 하나하나 꺼내며 확인하게 된다.

```typescript
const find = (fn, iter) =>
	go(
		iter,
		L.filter((a) => (console.log(a), fn(a))), // age가 28인 아이템까지만 찍힘
		take(1),
		([a]) => a,
	);
```

마지막으로 커링까지 적용하면 다음과 같다.

```typescript
const find = curry((fn, iter) => go(
  iter,
  L.filter(fn),
  take(1),
  ([a]) => a,
))

console.log(find((user) => user.age < 30)(users));
```

이렇게 만들면 find는 "어떤 이터러블을 해석하면서 필터를 하다가 첫 번째 것 하나를 찾으면 구조 분해해 꺼내준다"라고 읽히므로 이해하기 쉽다. for 문이나 if 문이 없다.

### 8.4 타입스크립트에서의 안전한 합성

```typescript
// 안전한 합성을 위한 연산자 ?. ?? !
const desserts = [
  { name: 'Chocolate', price: 5000 },
  { name: 'Latte', price: 3500 },
  { name: 'Coffee', price: 3000 }
];

// ① 옵셔널 체이닝 연산자(?.)를 통해 name 프로퍼티에 안전하게 접근
const dessert = find(({ price }) => price < 2000, desserts);
console.log(dessert?.name ?? 'TAT');
// TAT

// ② Non-null 단언 연산자(!)를 통해 무조건 찾을 상황을 의도하고 있다고 언어와 소통
const dessert2 = find(({ price }) => price < Infinity, desserts)!;
console.log(dessert2.name);
// Chocolate
```

①번 방식(옵셔널 체이닝)은 값이 실제로 없을 때도 런타임 에러 없이 `undefined` 처리된다. 반면 ②번 방식(Non-null 단언)은 값이 없는데도 존재한다고 단언하므로 실제로 값이 없다면 런타임 에러가 발생할 수 있다.

②번 방식은 개발자가 '이 로직에서는 값이 반드시 존재하도록 설계했다'는 의도를 언어에 전달하는 수단이다. '이곳에서는 `null`이나 `undefined`가 나타나지 않는 상황이며, 만약 실제로 값이 없다면 그것은 설계가 어긋난 상황이므로 런타임 에러가 발생해야만 한다'는 의도의 표현이다. 따라서 에러가 발생한다면 `!`를 없앨 것이 아니라 런타임에서 값을 찾지 못하는 이유를 찾아 해결해야 한다.

## 9. every와 some

### 9.1 map + reduce로 구현하기

`every`는 주어진 함수 `f`가 모든 요소에 대해 `true`를 반환하면 `true`를, 그렇지 않으면 `false`를 반환해야 한다.

```typescript
// every 함수 시그니처
// all :: (a -> Bool) -> [a] -> Bool
function every<A>(f: (a: A) => boolean, iterable: Iterable<A>): boolean {}
```

함수형 프로그래밍에서는 리스트를 단계별로 변환하며 최종 결과를 도출하는 방식으로 사고한다. 먼저 모든 요소를 `boolean`으로 변환한 뒤 `&&`로 모두 연결하면 원하는 결과를 얻을 수 있다.

```typescript
// every 함수 구현
function every<A>(f: (a: A) => boolean, iterable: Iterable<A>): boolean {
  return fx(iterable)
    .map(f)
    .reduce((a, b) => a && b, true);
}

const isOdd = (a: number) => a % 2 === 1;
console.log(every(isOdd, [1, 3, 5]));
// true
console.log(every(isOdd, [1, 2, 5]));
// false
```

`reduce`의 누적 함수로 `a && b`를 전달하여 `(boolean && boolean && boolean)`과 동일한 효과를 냈다. "한 번의 reduce에서 `f(b)`처럼 구현하지 않고 왜 map과 reduce로 나누어 순회하지?"라는 의문이 생길 수 있지만, 지연 이터레이터의 특성상 각 요소가 map을 통과한 직후 즉시 reduce에 소비되므로 실제로는 한 번만 순회하며 O(n) 시간이 걸린다.

`some`도 같은 방식이다. 모든 값을 `boolean`으로 만든 후 `||`로 묶으면 된다.

```typescript
// some 함수 구현
function some<A>(f: (a: A) => boolean, iterable: Iterable<A>): boolean {
  return fx(iterable)
    .map(f)
    .reduce((a, b) => a || b, false);
}

console.log(some(isOdd, [2, 5, 6]));
// true
console.log(some(isOdd, [2, 4, 6]));
// false
```

### 9.2 지연 평가에 기반한 break 로직 끼워 넣기

사실 some과 every 모두 결과를 만들기 위해 반드시 모든 요소를 순회할 필요는 없다. some은 `true`를 하나라도 만나면, every는 `false`를 하나라도 만나면 순회를 종료할 수 있다.

```typescript
// 효율 높인 some 함수
function some<A>(f: (a: A) => boolean, iterable: Iterable<A>): boolean {
  return fx(iterable)
    .map(f)
    .filter(a => a)
    .take(1)
    .reduce((a, b) => a || b, false);
}

// 효율 높인 every 함수
function every<A>(f: (a: A) => boolean, iterable: Iterable<A>): boolean {
  return fx(iterable)
    .map(f)
    .filter(a => !a)
    .take(1)
    .reduce((a, b) => a && b, true);
}
```

some에서는 `.filter(a => a).take(1)`을 통해 `true`를 하나라도 만나면 더 이상 순회하지 않는다. every에서는 `.filter(a => !a).take(1)`을 통해 `false`를 하나라도 만나면 순회를 종료한다. 반복문을 `if () break;`로 종료한 것과 같은 효율이 됐다 — 지연 평가 위에서는 **break조차 함수(filter + take)의 조합으로 끼워 넣을 수 있다.**

### 9.3 공통 로직을 함수형으로 추상화하기

함수형 프로그래밍은 리스트, 코드, 함수를 값으로 다루므로 공통 로직을 분리하여 추상화하기 편리하다.

```typescript
// accumulateWith 함수
function accumulateWith<A>(
  accumulator: (a: boolean, b: boolean) => boolean,
  acc: boolean,
  taking: (a: boolean) => boolean,
  f: (a: A) => boolean,
  iterable: Iterable<A>
): boolean {
  return fx(iterable)
    .map(f)
    .filter(taking)
    .take(1)
    .reduce(accumulator, acc);
}

function every<A>(f: (a: A) => boolean, iterable: Iterable<A>): boolean {
  return accumulateWith((a, b) => a && b, true, a => !a, f, iterable);
}

function some<A>(f: (a: A) => boolean, iterable: Iterable<A>): boolean {
  return accumulateWith((a, b) => a || b, false, a => a, f, iterable);
}
```

`accumulateWith`로 every와 some의 공통 로직을 추상화했다. 서로 다른 로직을 인자로 전달하는데, 특히 논리가 담긴 코드를 함수로 전달하여 조립하는 면이 특별하다. 이처럼 함수형 프로그래밍은 리팩터링하기 좋고 유지보수성이 뛰어나다.

## 10. flatten, flatMap, concat

### 10.1 L.flatten과 flatten

L.flatten은 이터러블 안에 이터러블이 있을 때 평탄화해 주는 함수다. 우선 이터러블인지 판단하는 `isIterable`부터 만든다.

```typescript
const isIterable = a => a && a[Symbol.iterator];
const isIterable = a => !!a?.[Symbol.iterator]
```

```typescript
L.flatten = function* (iter) {
	for (const a of iter) {
		if (isIterable(a)) {
			// 이터러블이면 추가 작업 해주고 아니면 반환
			for (const b of a) {
				yield b;
			}
		} else {
			yield a;
		}
	}
};
```

L.flatten이 있다면 즉시 평가 flatten은 간단하다.

```typescript
const flatten = pipe(
  L.flatten,
  takeAll,
);
```

### 10.2 yield*와 L.deepFlat

`yield*`를 활용하면 L.flatten을 더 간결하게 바꿀 수 있다. `yield* iterable`은 `for (const val of iterable) yield val;`과 같다(6장 참고).

```typescript
L.flatten = function* (iter) {
	for (const a of iter) {
		if (isIterable(a)) {
			yield* a;
		} else {
			yield a;
		}
	}
};
```

깊은 이터러블을 모두 펼치고 싶다면 재귀로 L.deepFlat을 만들 수 있다.

```typescript
L.deepFlat = function* f(iter) {
	for (const a of iter) {
		if (isIterable(a)) {
			yield* f(a);
		} else {
			yield a;
		}
	}
};
```

```typescript
console.log([...L.deepFlat([1, [2, [3, 4], [[5]]]])]); // [1, 2, 3, 4, 5];
```

### 10.3 L.flatMap과 flatMap

L.flatMap은 map과 flatten을 동시에 하는 함수다. 이 함수가 최신 자바스크립트 스펙(`Array.prototype.flatMap`)에 들어간 이유는 자바스크립트가 기본적으로 지연 평가를 지원하지 않기 때문이다. 즉시 평가에서는 map을 하고 나서 flatten을 하면 두 번 순회하고 중간 배열이 생성된다. flatMap은 이 과정을 한 번에 처리해 효율을 높인다. 시간 복잡도는 큰 차이가 없지만 공간 복잡도(메모리 효율) 때문에 도입됐다.

이미 L.map과 L.flatten을 구현했으므로 조합만 하면 된다.

```typescript
L.flatMap = curry(pipe(L.map, L.flatten));
```

```typescript
const value = [
	[1, 2],
	[3, 4],
	[6, 7, 8],
];

const it = L.flatMap(
	map((a) => a * a),
	value,
);
console.log([...it]);
```

즉시 평가 flatMap도 마찬가지다.

```typescript
export const flatMap = curry(pipe(L.flatMap, takeAll));

export const flatMap = curry(pipe(L.map, L.flatten, takeAll));
```

이 함수들로 여러 조합을 만들어 나갈 수 있다.

```typescript
console.log(flatMap(L.range, [1, 2, 3])); // [0, 0, 1, 0, 1, 2]
console.log(map(range, [1, 2, 3])) // [ [ 0 ], [ 0, 1 ], [ 0, 1, 2 ] ]
console.log(flatMap(range, map(a => a + 1, [1, 2, 3]))); // [0, 1, 0, 1, 2, 0, 1, 2, 3]
console.log(take(3,  L.flatMap(L.range, map(a => a + 1, [1, 2, 3])))) // 0 1 0
```

### 10.4 concat으로 더하기

배열 메서드 `concat`은 여러 배열을 하나로 결합하지만, 모든 요소를 즉시 평가하고 결합하여 새 배열을 생성하므로 매우 큰 배열을 결합할 때 메모리 사용량이 증가할 수 있다. 제너레이터로 concat을 구현하면 지연 평가를 통해 요소를 필요할 때마다 처리할 수 있다.

```typescript
// concat 함수
function* concat<T>(...iterables: Iterable<T>[]): IterableIterator<T> {
  for (const iterable of iterables) yield* iterable;
}

const arr = [1, 2, 3, 4];
const iter = concat(arr, [5]);
console.log([...iter]);
// [1, 2, 3, 4, 5]
```

제너레이터 concat은 원본 배열을 변경하지 않고 필요한 시점에만 요소를 생성하므로, 원본 배열을 여러 번 사용해야 하는 상황에 특히 유용하다. take나 some과 함께 사용하면 필요한 만큼만 처리할 수 있어 효율적이다.

```typescript
// take와 concat
const arr1 = [1, 2, 3, 4, 5];
const arr2 = [6, 7, 8, 9, 10];
const iter = take(3, concat(arr1, arr2));
console.log([...iter]); // [1, 2, 3]
// arr2는 순회하지도 않고 종료

// some과 concat
const arr = [3, 4, 5];
console.log(some(n => n < 3, arr));
// false
const iter2 = concat([1, 2], arr);
console.log(some(n => n < 3, iter2));
// true
```

## 요약

- **지연 평가는 제때 계산법**이다: 값을 미리 만들지 않고 `next()`가 호출될 때마다 하나씩 평가한다. ES6의 이터레이션 프로토콜과 제너레이터가 이를 언어 차원에서 표준화했다.
- **즉시 평가는 가로로, 지연 평가는 세로로** 값을 만든다: 중첩 이터레이터는 가장 바깥(take)에서 시작해 안쪽(filter)으로 파고들었다가 값 하나를 들고 돌아온다.
- **map·filter는 지연하는 함수, take·reduce·find는 결과를 만드는 함수**다. 즉시 평가 함수는 `L.map + takeAll`처럼 지연 함수의 특수한 경우로 환원된다.
- 지연 평가 위에서는 **break도 함수 조합**(`filter + take(1)`)으로 표현된다 — find, some, every가 모두 이 원리로 만들어지며, 공통 구조는 `accumulateWith`처럼 다시 함수로 추상화된다.
- 값이 없을 수 있는 상황(find의 `undefined`)에 대해 하스켈은 `Maybe` 타입으로, 타입스크립트는 `?.`/`!`/`??` 연산자로 안전한 합성을 지원한다.
- **flatten·flatMap·concat**도 제너레이터(`yield*`)로 지연 구현하면 중간 배열 없이 필요한 만큼만 처리한다.

## 다른 챕터와의 관계

- **4장**: es5 스타일 `_find`/`_some`/`_every`는 전체 순회 기반이었다. 이 장의 지연 평가판이 그 한계(불필요한 순회)를 해소한다.
- **6장**: `yield*`와 무한 시퀀스(naturals)가 이 장의 L.range·deepFlat·concat의 재료다.
- **7장**: 이 장의 L.map/L.filter는 7장에서 만든 즉시 평가 고차 함수의 제너레이터 판이다.
- **10장**: `fx(...)` 체이닝 표기의 실제 구현(FxIterable)을 다룬다.
- **11장**: find의 `Maybe`가 하스켈의 타입 시스템·패턴 매칭과 어떻게 이어지는지 확장한다.
- **14장**: 지연 평가가 Promise와 만나면 비동기 동시성 제어(`C.reduce`, `C.take`)로 발전한다.
