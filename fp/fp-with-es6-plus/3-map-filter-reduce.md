# 3. map, filter, reduce

## 1. map
데이터를 수집하는 기본적인 map 함수를 만들어 보자.
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
함수형 프로그래밍은 인자와 반환 값으로 대화 하는 것을 지향한다. 즉 내부 로직에서 작업을 하기보다 리턴 된 값으로 변화를 일으키거나 사용하는 것이 더 함수형 프로그래밍 다운 사고 방식이다. 예를 들어 만약 전체 값에대한 로그를 찍고 싶다면 저 map 함수 내부가 아니라 리턴 된 값으로 출력 시킨다.
```typescript
const map = (iter) => {
  let result = [];

  for (const a of iter) {
    result.push(a.name);
  }

  return result;
};

console.log(map(products));
```
iterator 라고 지은 이유는 map 함수가 받는 값이 이터레이터블 프로토콜을 따른다 라는 뜻에서 명명 했다.
위 함수는 데이터를 직접적인 변화를 일으키는 다른 메서드나 함수에 보내는 것이 아니라 결과를 return 시켜 사용하게끔 한다.
또한 위와 같이 문장은 직접적으로 어떤 값을 수집할 것인지 작성해야한다. map 함수는 이 부분을 추상화 시킬 수 있다. 함수를 받아 어떤 값을 수집할 것인지 완전히 위임하는 식이다.
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
이 map 함수는 함수를 값으로 다루기 때문에 어떤 값을 수집할 것인지 위임할 수 있다.
이 map 함수는 이터러블 프로토콜을 다루고 있기 때문에 다형성이 굉장히 높다. 즉 값이 배열이 아니어도 이터러블(배열, Set, Map, DOM NodeList 등) map을 적용할 수 있다.
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

## 2. filter
거르는 함수인 filter 함수도 map 함수와 같이 구현해보자. 우선 기본 구현은 아래와 같다.
```typescript
let result = [];

for (const a of products) {
  if (a.price > 20000) {
    result.push(a);
  }
}

console.log(result);
```
먼저 부수 효과로 출력을 하지 않고 return 한 값으로 출력 하게 해준다. 그 어떤 값이든 받을 수 있도록 이터러블 프로토콜을 따르도록 한다. 또한 어떤 조건일 때 거릴 것인지 보조 함수에 완전히 위임해준다.
```typescript
const filter = (fn, iter) => {
  let result = [];

  for (const a of iter) {
    if (fn(item)) {
      result.push(a);
    }
  }

  return result;
};

console.log(filter((p) => p.price > 20000, products));
```

## 3. reduce
reduce는 이터러블 값을 값을 하나의 값으로 축약하는 함수이다.
```typescript
const numbers = [1, 2, 3, 4, 5];

let total = 0;

for (const a of numbers) {
  total += a;
}

console.log(total); // 15
```
위 코드를 참조 했을 때 reduce 함수의 내부는 초기 값으로 시작해서 보조 함수를 재귀적으로 실행해 하나의 값으로 만들도록 구현해주면 된다.
만약 add 라는 함수가 있다면 아래와 같이 동작할 것이다.
```typescript
const add = (a, b) => a + b;

console.log(add(add(add(add(add(0, 1), 2), 3), 4), 5));
```
reduce 함수를 구현하면 아래와 같다.
```typescript
const add = (a, b) => a + b;

const reduce = (fn, acc, iter) => {
  for (const a of iter) {
    acc = fn(acc, a);
  }
  return acc;
};

console.log(reduce(add, 0, numbers)); // 15
```
자바스크립트에서는 acc 값이 없어도 사용 가능하다. 해당 부분을 반영하면 아래와 같다.
생략 했을 경우 내부적으로 첫 번째 값을 꺼내 초기 값으로 만들어 주면 된다.
```typescript
const reduce = (fn, acc, iter) => {
  if (!iter) {
    iter = acc[Symbol.iterator]();
    acc = iter.next().value;
  }

  for (const a of iter) {
    acc = fn(acc, a);
  }
  return acc;
};

console.log(reduce(add, numbers));
```
reduce 같은 경우 보조 함수를 통해 어떻게 축약할지 완전히 위임하기 때문에 복잡한 형태의 데이터를 특정 값으로 축약해 나가는 것도 어려움이 없다.
