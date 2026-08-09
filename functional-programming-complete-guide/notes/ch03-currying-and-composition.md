# Chapter 3: Currying and Composition (커링과 함수 합성)

## 핵심 질문

커링은 함수 호출 방식을 어떻게 바꾸며, 왜 파이프라인에 필수적인가? `go`와 `pipe`는 중첩 함수 호출을 어떻게 읽기 좋은 흐름으로 바꾸는가? 그리고 이 스타일은 타입 시스템과 만나 어디로 진화하는가?

---

2장 마지막 코드에는 `_map(_filter(users, ...), _get('name'))`처럼 함수 호출이 중첩되면서 안쪽부터 읽어야 하는 불편함이 남아 있었다. 이 장에서는 커링으로 함수의 인자 받는 방식을 유연하게 만들고, `reduce`를 뿌리로 `go`/`pipe`를 만들어 중첩 호출을 위에서 아래로 읽히는 파이프라인으로 바꾼다.

같은 아이디어가 es5 시절 `_curry`/`_pipe`/`_go`로 먼저 구현됐었는데, 그 구현들은 이 장 후반의 es6 판과 하는 일이 같으므로 **코드 대신 "어떤 우회가 필요했고 무엇이 그것을 대체했는지"만 설명으로 남긴다**. es6판이 없는 고유 개념(`_curryr`)과 커링의 실전 가치를 보여주는 풀이는 코드로 유지한다.

---

## 1. 커링 — 인자를 나눠 받는 함수 변환

커링(*Currying - 여러 인자를 받는 함수를, 인자를 하나씩 받는 함수들의 연쇄로 바꾸는 기법*)은 여러 개의 인자를 가진 함수를 호출할 때 파라미터 수보다 적은 인자를 받으면, 누락된 파라미터를 마저 받는 함수를 리턴하는 기법이다. 함수 하나가 n개의 인자를 받는 과정을 n개의 함수가 각각의 인자를 받도록 나누고, 모든 인자가 채워졌을 때 본체를 실행하도록 바꾸는 것이다. **커링은 함수를 호출하지 않는다. 다만 변환할 뿐이다.**

```javascript
f(x)(y) = x + y
// 여기서 f(x) = g 라고 보면
g(y) = x + y 
// 이 시점에서 x는 더 이상 변수가 아니라 상수이다.
f(1)(2) = g(2) = 1 + 2 = 3
```

이렇게 변형된 함수의 형태를 커리한 형태(*curried form*)라고 한다. 상황에 따라 `add(1, 2)`와 `add(1)(2)` 두 호출이 모두 동작하도록 만들 수도 있다 — 인자가 모두 들어왔으면 즉시 실행하고, 아니면 나머지를 기다리는 함수를 리턴하는 방식이다.

es5 시절에는 이 판별을 `arguments.length`(함수 선언문) 또는 `b !== undefined`(화살표 함수) 검사로 구현했다. 그 구현은 이 장 5절의 es6 `curry`(나머지 매개변수 기반)와 하는 일이 같으므로 완성형은 그쪽에서 본다. 다음 절의 `_curryr` 코드가 es5식 판별 기법의 실물 예시를 겸한다.

## 2. _curryr — 평가 순서 뒤집기

```javascript
const sub = _curry((a, b) => a - b);

const sub10 = sub(10);
console.log(sub10(5)); // 5
```

위 코드에서 `sub10`은 "10을 빼는" 듯한 이름인데, 실제로는 "10에서 들어온 인자를 빼는" 함수가 되어 버렸다. 부분 적용 시 먼저 채우고 싶은 인자가 **오른쪽** 인자인 경우가 많다. 이럴 때 `_curryr`(curry right)로 평가 순서를 뒤집는다.

```javascript
function _curryr(fn) {
  return function(a, b) {
    return arguments.length === 2 ? fn(a, b) : function(b) {
      return fn(b, a); // 미리 받은 함수 본체를 안쪽에서 평가
    }
  }
}
```

```javascript
const _curryr = fn => (a, b) => b !== undefined ? fn(a, b) : (b => fn(b, a));
```

> **참고**: 두 구현이 곧 es5식 인자 개수 판별의 두 갈래다. 화살표 함수는 자신의 `arguments` 객체를 갖지 않으므로 화살표 판에서는 `arguments.length` 대신 `b !== undefined`로 판별한다 — 두 번째 인자로 `undefined`를 명시적으로 넘기는 경우는 구분하지 못하는 트레이드오프가 있다.

```javascript
const sub = _curryr((a, b) => a - b);

const sub10 = sub(10);
console.log(sub10(5)); // -5
```

2장에서 만든 `_get`도 `_curryr`로 정의하면, 키만 먼저 받아 두는 함수를 자연스럽게 만들 수 있다.

```javascript
const user = { id: 1, name: '이름값', age: 31 };

// 일반적인 get
const _get = (obj, key) => obj == null ? undefined : obj[key];

console.log(user.name); // 이름값
console.log(_get(user, 'name')); // 이름값

const _curriedGet = _curryr((obj, key) => obj == null ? undefined : obj[key]);
const getName = _curriedGet('name');
console.log(getName(user)); // 어떤 역할을 하는 함수인지 좀 더 명확하다.
```

> **참고**: 오른쪽 우선(`_curryr`)이 필요했던 근본 이유는 es5 노트의 함수들이 `_map(list, f)`처럼 **데이터를 왼쪽에** 두었기 때문이다. 이 장 5절부터의 es6 판은 `map(f, iterable)`처럼 **보조 함수를 왼쪽**에 두므로 왼쪽 우선 `curry`만으로 파이프라인이 자연스럽다. 이 인자 순서 설계의 근거는 10장(Pipe Operator)에서 다시 다룬다.

## 3. 축약과 파이프라인의 뿌리 — _reduce, _pipe, _go

es5 노트는 파이프라인을 세 단계로 쌓아 올렸다. 구현 코드는 es6 판과 중복되므로 개념과 우회의 역사만 정리한다.

**`_reduce` — 축약.** 초기값 `memo`를 두고 리스트의 요소로 보조 함수를 반복 실행해 하나의 값으로 접는 함수다(`inject` 혹은 `foldl`이라고도 불린다). 요소가 3개라면 다음과 같이 재귀적으로 호출하는 형태가 된다.

```javascript
_reduce([1, 2, 3], add, 0);

memo = add(0, 1);
memo = add(memo, 2);
memo = add(memo, 3);

add(add(add(0, 1), 2), 3);
```

모든 데이터가 보조 함수를 통해 하나의 값으로 접혀 들어간다 — 그래서 "축약"이다. es5 구현에서는 초깃값 생략을 `arguments.length === 2`로 판별하고, 첫 요소를 잘라내기 위해 `Array.prototype.slice.call(list, 1)`(`_rest`)로 유사 배열까지 대응해야 했다. 이 우회들은 이후 언어 발전이 근본적으로 대체한다 — 유사 배열 문제는 이터레이션 프로토콜(5장)이, 구현 완성형은 이터러블 기반 `reduce`와 타입 오버로드(7장)가 맡는다.

**`_pipe` — 합성.** 함수만 인자로 받아, 그 함수들을 연속으로 실행하는 하나의 함수로 합성한다. 내부는 결국 `_reduce`다 — **함수로 구성된 배열을 받아, 인자를 함수들에 연속 적용한 최종 결과로 축약**한다. `_reduce`가 더 추상화된 레벨이고 `_pipe`는 특화된 함수다.

**`_go` — 즉시 실행.** 첫 번째 인자로 받은 **값**을 두 번째 인자(함수)에 넘기고, 그 결과를 다음 함수에 넘기기를 반복해 마지막 결과를 리턴한다. `_pipe`가 합성된 함수를 리턴한다면, `_go`는 합성한 함수에 인자를 넣어 즉시 실행한다. es5에서는 가변 인자를 받기 위해 `arguments`와 `_rest`, `_pipe.apply(null, fns)` 조합이 필요했는데, es6의 나머지 매개변수와 전개 연산자(`...fns`)가 이를 한 줄로 대체했다.

세 함수의 관계 — `reduce`(축약) 위에 `pipe`(합성)가, 그 위에 `go`(즉시 실행)가 선다 — 는 es6 판에서도 동일하며, 완성형 구현은 5절에서 만든다.

## 4. _curryr로 파이프라인 다듬기

파이프라인에서 `_filter`·`_map` 같은 함수는 항상 "데이터 + 보조 함수" 형태로 감싸는 익명 함수가 필요했다. `_curryr`로 평가 순서를 뒤집으면 보조 함수만 먼저 넘겨 데이터를 기다리는 함수를 만들 수 있다.

```javascript
// 이 작업을 하기 전에 const(상수)로 선언된 _map, _filter를 let(변수)으로 바꿔줘야 한다.
_map = _curryr(_map);
_filter = _curryr(_filter);
```

파이프라인이 다음과 같이 간결해진다.

```javascript
_go(
  users,
  _filter((user) => user.age >= 30),
  _map(_get('name')),
  console.log,
)

_go(
  users,
  _filter((user) => user.age < 30),
  _map(_get('age')),
  console.log,
)
```

내부 동작을 풀어 보면 이렇다.

```javascript
// _curryr 함수를 사용하기 전
let memo = users;
memo = (users => _filter(users, user => user.age >= 30))(memo);
memo = (users => _map(users, _get('name')))(memo);
memo = console.log(memo);

// _curryr 함수로 함수에 변형을 준 후
let memo = users;
memo = _filter(user => user.age >= 30)(memo);
memo = _map(_get('age'))(memo);
memo = console.log(memo);
```

코드가 훨씬 간결하고, 배열 메서드 체이닝과 비슷한 정도의 표현력을 보여준다. 인자와 보조 함수를 받는 `_filter`·`_map`을 `_curryr`로 다시 만들었고, 보조 함수 하나만 넘기면 인자가 오른쪽부터 적용되는 또 다른 함수가 리턴된다. 그리고 `_go`가 값과 함수들을 받아 함수를 연속 실행하면서 값을 변화시켜 나간다.

함수의 평가 시점을 다루면서, 사이드 이펙트 없는 순수 함수들로 구성될 때 이런 조합성이 만들어진다. **순수 함수의 평가 시점을 다루면서 조합성을 강조하고 추상화의 단위를 함수로 하는 프로그래밍** — 이것이 함수형 프로그래밍이다.

## 5. ES6+ 판 — go, pipe, curry

이제 같은 아이디어를 ES6+ 스타일(이터러블 기반 `reduce`, 전개 연산자, 나머지 매개변수)로 정련해 이후 장(7~15장)에서 계속 쓸 `go`, `pipe`, `curry`를 만든다. 함수형 프로그래밍에서는 코드(함수)를 값처럼 다루기 때문에 함수가 실행되는 시점을 원하는 대로 제어할 수 있고, 이로 인해 표현력이 높아진다.

### 5.1 go

`go`는 여러 인자를 받아 첫 번째 인자를 시작값으로 두고, 나머지 인자(함수)들을 차례로 적용해 가며 값을 전달하는 함수다. `reduce`로 구현한다 — 3절에서 정리한 "pipe/go의 뿌리는 reduce"가 코드 한 줄로 드러난다.

```typescript
const go = (...args) => {
  return reduce((a, f) => f(a), args);
};

go(
  0,
  (a) => a + 1,
  (a) => a + 10,
  (a) => a + 100,
  console.log
);
```

### 5.2 pipe

`pipe`는 `go`와 달리 함수를 리턴한다. `go`가 인자와 함수를 받아 즉시 값을 평가한다면, `pipe`는 함수들을 먼저 합성해 두고, 합성된 함수가 나중에 인자를 받아 평가한다. `go`를 이용해 인자만 나중에 받게 하면 된다.

```typescript
const pipe =
  (...fns) =>
  (arg) =>
    go(arg, ...fns);
```

그런데 `go`는 필요하면 처음에 인자를 2개 이상 받을 수 있지만, 위의 `pipe`가 리턴한 함수는 그럴 수 없다.

```typescript
const add = (a, b) => a + b;

go(
  add(0, 1), // 인자를 두 개 받음.
  (a) => a + 1,
  (a) => a + 10,
  (a) => a + 100,
  console.log
);
```

`pipe`도 첫 함수를 실행할 때 인자를 2개 이상 전달할 수 있으면 좋다. 첫 함수만 분리해 받으면 된다.

```typescript
const pipe =
  (fn, ...fns) =>
  (...args) =>
    go(fn(...args), ...fns);
```

참고로 함수가 하나만 들어와도 나머지 매개변수에는 `undefined`가 아닌 빈 배열이 들어오므로 정상 동작한다.

```typescript
const f = pipe(
  (a, b) => a + b,
  (a) => a + 10,
  (a) => a + 100,
  console.log
);

f(0, 1); // 111
```

### 5.3 go로 표현 바꾸기

`go`·`pipe`는 위에서 아래로, 왼쪽에서 오른쪽으로 평가되므로 중첩 표현을 바꿀 수 있다. 아래와 같은 코드가 있다고 하자.

```typescript
console.log(
	reduce(
		add,
		map(
			(p) => p.price,
			filter((p) => p.price < 20000, products),
		),
	),
);
```

`go`를 사용하면 다음과 같이 표현할 수 있다.

```typescript
go(
	products,
	(products) => filter((p) => p.price < 20000, products),
	(products) => map((p) => p.price, products),
	(price) => reduce(add, price),
	(total_price) => console.log(total_price),
);
```

코드는 좀 더 길어지고 어떤 측면에선 간결성이 줄었지만, 읽기에는 편해졌다.

### 5.4 curry

`curry`는 함수를 값으로 다루면서 인자를 원하는 시점에 나눠 받고, 인자가 모두 모였을 때 원래 함수를 실행하는 함수다.

```typescript
const curry =
	(fn) =>
	(arg, ...args) =>
		args.length ? fn(arg, ...args) : (...args) => fn(arg, ...args);
```

```typescript
const add = curry((a, b) => a + b);

console.log(add(1, 2)); // 3
console.log(add(1)(2)); // 3
```

1절의 es5식 판별(`arguments.length`·`b !== undefined`)과 달리 나머지 매개변수(`...args`)를 쓰므로 인자 개수 제한도, `undefined` 인자의 모호함도 없다. `curry`로 `map`, `filter`, `reduce`를 감싸면 이렇게 표현할 수 있다.

```typescript
go(
	products,
	(products) => filter((p) => p.price < 20000)(products),
	(products) => map((p) => p.price)(products),
	(price) => reduce(add)(price),
	(total_price) => console.log(total_price),
);
```

`go`는 이전 단계의 결과를 다음 함수에 전달하고, `map`·`filter`·`reduce`는 curry로 부분 적용할 수 있으므로 최종적으로 다음과 같이 정리된다.

```typescript
go(
	products,
	filter((p) => p.price < 20000),
	map((p) => p.price),
	reduce(add),
	console.log,
);
```

## 6. 함수 조합으로 함수 만들기

```typescript
const add = curry((a, b) => a + b);

const total_price = pipe(
	map((p) => p.price),
	reduce(add),
);

const base_total_price = (predicate) => pipe(filter(predicate), total_price);

go(
	products,
	base_total_price((p) => p.price < 20000),
	console.log,
);

go(
	products,
	base_total_price((p) => p.price >= 20000),
	console.log,
);
```

조건에 해당하는 `predicate` 함수를 제외한 모든 로직이 재사용되고 있다. 이런 식으로 함수형 프로그래밍에서는 고차 함수들을 함수의 조합으로 만들어 가며, 잘게 나눠진 함수들을 계속 작게 만들어 중복을 제거하고 더 많은 곳에서 재사용되게 한다.

> **핵심 통찰**: 파이프라인의 재료는 "값을 받는 함수"가 아니라 "값을 기다리는 함수"다. 커링은 함수를 그 재료로 바꾸는 변환기이며, go/pipe는 그 재료를 조립하는 공장이다.

## 7. 파이프라인의 다음 단계 — 타입 추론과 체이닝

이 장에서 만든 `go`/`pipe`/`curry`는 동적 타입 자바스크립트에서 훌륭하게 동작한다. 하지만 타입스크립트로 넘어가면 한계가 드러난다. 가변 인자 파이프라인(`pipe(f1, f2, f3, ...)`)은 단계 사이의 타입을 이어주기 위해 수많은 오버로드 시그니처가 필요하고, 중간 단계에서 추론이 끊기기 쉽다.

이 문제에 대한 해법이 두 갈래로 발전한다.

- **정교하게 타입을 붙인 pipe**: FXTS 같은 라이브러리는 다수의 오버로드로 pipe에 타입을 부여한다(16장에서 실전 사용).
- **메서드 체이닝**: `fx(iterable).map(f).filter(g)`처럼 클래스 체이닝으로 바꾸면, 각 메서드가 자신의 원소 타입을 아는 상태에서 시작하므로 타입 추론이 자연스럽게 흐른다(10장에서 FxIterable로 직접 구현).

파이프 연산자(`|>`)가 언어 표준(Stage 2)에 들어오기 전까지, 이 두 방식이 파이프라인 표현력과 타입 안전을 동시에 얻는 실용적 해법이다. 8장부터 등장하는 `fx(...)` 표기가 바로 이 진화의 결과물이다.

## 요약

- **커링**은 함수를 호출하지 않고 변환한다 — 인자를 나눠 받다가 모두 모이면 본체를 평가하는 커리한 형태로 바꾼다. 부분 적용할 인자가 오른쪽일 때는 `_curryr`로 평가 순서를 뒤집는다(데이터가 왼쪽에 오는 es5식 시그니처의 산물).
- **reduce는 파이프라인의 뿌리**다. pipe는 "함수 배열을 받아 인자에 연속 적용하는 reduce"이고, go는 즉시 실행되는 pipe다 — 이 3층 구조는 es5(`_reduce`/`_pipe`/`_go`)와 es6에서 동일하다.
- es5 구현이 의존하던 우회(`arguments.length` 판별, `slice.call`의 유사 배열 대응, `apply`)는 **나머지 매개변수·전개 연산자·이터레이션 프로토콜(5~7장)이 근본적으로 대체**했다 — 그래서 이 장의 완성형 구현은 es6 판 하나다.
- `_curryr`로 변환한 함수는 보조 함수만 먼저 받아 **데이터를 기다리는 함수**가 되고, 파이프라인이 메서드 체이닝 수준의 표현력을 얻는다.
- 함수 조합으로 함수를 만들면(`base_total_price`) predicate 하나만 갈아 끼우는 수준까지 재사용성이 올라간다.
- 가변 인자 파이프는 TS 타입 추론이 어렵다 — 오버로드를 갖춘 pipe(FXTS)와 메서드 체이닝(FxIterable)으로 진화한다.

## 다른 챕터와의 관계

- **2장**: 중첩 호출(`_map(_filter(...))`)의 가독성 문제가 이 장의 출발점이었고, `_get`이 커링의 첫 실전 사례였다.
- **5·7장**: es5 `_reduce`가 우회로 풀던 유사 배열·초깃값 생략 문제를 이터레이션 프로토콜과 타입 오버로드가 정식으로 해결한다.
- **8장**: `go + L.filter + take(1)` 같은 파이프라인이 지연 평가와 결합해 find를 만든다.
- **10장**: pipe의 타입 추론 한계에 대한 답으로 FxIterable 체이닝과 Pipe Operator, 그리고 `map(f, iterable)` 인자 순서의 설계 근거를 다룬다.
- **11장**: 여기서 직접 만든 커링이 하스켈에서는 언어 기본값임을 확인한다.
- **14장**: `go`/`pipe`/`reduce`가 Promise를 만나 비동기까지 다형적으로 지원하도록 확장된다.
- **16장**: 타입이 갖춰진 FXTS의 `pipe`로 실전 문제를 푼다.
