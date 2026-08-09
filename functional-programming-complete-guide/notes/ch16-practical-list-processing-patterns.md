# Chapter 16: Practical List Processing Patterns (실전 데이터와 리스트 프로세싱 패턴)

> **참고**: 이 장은 멀티패러다임 노트 5장의 이관본으로, 본문의 `[코드 5-N]` 번호는 원본 기준이다. 본문에서 사용하는 FXTS의 `pipe`·`fx`는 이 가이드 3장(go/pipe)과 10장(FxIterable)에서 직접 구현한 도구들의 실전 라이브러리 판이다.

## 핵심 질문

함수형 프로그래밍은 수열이나 간단한 데이터를 다루는 수준을 넘어 실제 커머스 데이터, 백엔드 스케줄러, 비동기/동시성 프로그래밍 같은 현실 문제를 얼마나 효과적으로 해결할 수 있을까? 또한 리스트 프로세싱의 다양한 조합을 패턴화하면 어떻게 복잡한 문제를 구조적이고 선언적으로 풀 수 있을까?

---

함수형 프로그래밍은 단순히 개념이나 추상적인 아이디어가 아니다. 현실 세계의 데이터와 문제를 해결할 때 오히려 훨씬 실용적이며 개발자와 서비스에 실질적인 가치를 제공한다.

리스트 프로세싱은 함수형 프로그래밍의 핵심 도구 중 하나로 데이터를 필터링하고 변환하며 이를 바탕으로 원하는 결과를 만들어내는 과정을 간결하고 명확하게 설계할 수 있도록 돕는다. 이 장에서는 단순히 수열을 다루던 함수형 코드가 현실 세계의 문제를 얼마나 잘 다루는지 그리고 우리가 매일 접하는 다양한 문제에 얼마나 폭넓게 활용될 수 있는지 탐구한다.

또한 함수형 프로그래밍을 실제 백엔드 프로그래밍에 적용하여 실질적인 문제를 해결하는 방법을 다룬다. 특히 데이터 처리와 비동기 작업, 병렬성, 시스템 제약 조건 같은 현실적인 문제를 함수형 스타일로 접근하는 방법을 탐구한다.

---

## 1. 실전 데이터 다루기

그동안 이 책에서는 대부분 수열을 중심으로 다뤄왔다. 이번 절에서는 실전에서 자주 접하는 데이터 구조를 다루며 함수형 프로그래밍의 응용력을 높여본다.

### 1.1 2차원 배열에서 숫자 다루기

다음은 간단한 2차원 배열에서 홀수의 제곱을 모두 더하는 코드다.

```typescript
// [코드 5-1] 홀수의 제곱을 모두 더하기
const numbers = [
  [1, 2],
  [3, 4, 5],
  [6, 7, 8],
  [9, 10]
];

const oddSquareSum = numbers
  .flat()                       // 2차원 배열을 1차원 배열로 펼침
  .filter(a => a % 2 === 1)    // 홀수만 필터링
  .map(a => a * a)              // 제곱
  .reduce((a, b) => a + b, 0); // 합산

console.log(oddSquareSum); // 165
```

`flat`으로 중첩된 배열을 펼치고 `filter`로 홀수를 골라낸 뒤 `map`으로 제곱한 값을 `reduce`로 모두 더했다.

### 1.2 농구팀 데이터 다루기

이번에는 실무에서 사용할 만한 데이터를 다뤄본다. 플레이어와 팀이라는 구조로 데이터를 구성했으며 각 팀에는 여러 플레이어가 소속되어 있다.

```typescript
// [코드 5-2] 30점 이상 득점자의 점수 총합
type Player = {
  name: string;
  score: number;
};

type Team = {
  name: string;
  players: Player[];
};

const teams: Team[] = [
  {
    name: 'Bears', players: [
      { name: 'Luka', score: 32 },
      { name: 'Anthony', score: 28 },
      { name: 'Kevin', score: 15 },
      { name: 'Jaylen', score: 14 },
    ]
  },
  {
    name: 'Lions', players: [
      { name: 'Stephen', score: 37 },
      { name: 'Zach', score: 20 },
      { name: 'Nikola', score: 19 },
      { name: 'Austin', score: 22 },
    ]
  },
  {
    name: 'Wolves', players: [
      { name: 'Jayson', score: 32 },
      { name: 'Klay', score: 37 },
      { name: 'Andrew', score: 15 },
      { name: 'Patrick', score: 14 },
    ]
  },
  {
    name: 'Tigers', players: [
      { name: 'DeMar', score: 37 },
      { name: 'Marcus', score: 21 },
      { name: 'Al', score: 19 },
      { name: 'Dennis', score: 22 },
    ]
  },
];

const totalHighScorers = teams
  .map(team => team.players)                // 팀 객체 구조를 선수들의 2차원 배열로 변환
  .flat()                                    // 1차원 배열로 펼침
  .filter(player => player.score >= 30)      // 30점 이상 득점한 선수만 필터링
  .map(player => player.score)               // 점수로 변환
  .reduce((a, b) => a + b, 0);              // 합산

console.log(totalHighScorers); // 175
```

`map`과 `flat`을 함께 사용한 코드는 `flatMap`으로 대체할 수 있다. `flatMap`은 `map`을 수행한 후 `flat`까지 한 번에 처리하는 메서드다.

```typescript
// [코드 5-3] flatMap 사용
const totalHighScorers2 = teams
  .flatMap(team => team.players)             // 모든 팀의 선수 배열을 펼침
  .filter(player => player.score >= 30)      // 30점 이상 득점한 선수만 필터링
  .map(player => player.score)               // 점수로 변환
  .reduce((a, b) => a + b, 0);              // 합산

console.log(totalHighScorers2); // 175
```

2차원 배열 예제와 농구팀 데이터 예제를 비교해 보면 구조가 거의 동일하다. 함수형 프로그래밍에서는 데이터를 다루는 일반적인 패턴을 제공함으로써 이를 다양한 데이터 형태에 쉽게 적용할 수 있다.

### 1.3 커머스 데이터 다루기

쇼핑몰이나 커머스 서비스에서는 장바구니 데이터를 처리하는 일이 흔하다. 선택된 상품의 전체 수량이나 가격을 계산하는 작업은 자주 발생한다.

```typescript
// [코드 5-5] reduce에 모든 로직을 몰아넣은 방식
type Product = {
  name: string;
  price: number;
  quantity: number;
  selected: boolean;
};

const products: Product[] = [
  { name: '티셔츠', price: 10000, quantity: 1, selected: true },
  { name: '셔츠', price: 30000, quantity: 2, selected: false },
  { name: '바지', price: 15000, quantity: 2, selected: true },
];

const sumSelectedQuantities = (products: Product[]) =>
  products.reduce((total, prd) => {
    if (prd.selected) {
      return total + prd.quantity;
    } else {
      return total;
    }
  }, 0);

const calcSelectedPrices = (products: Product[]) =>
  products.reduce((total, prd) => {
    if (prd.selected) {
      return total + prd.price * prd.quantity;
    } else {
      return total;
    }
  }, 0);

console.log(sumSelectedQuantities(products)); // 선택된 상품의 총 수량: 3
console.log(calcSelectedPrices(products));     // 선택된 상품의 총 가격: 40000
```

`reduce`를 사용하여 비교적 간결해지긴 했지만 여전히 `if-else`문과 모든 로직을 `reduce` 내부에 몰아넣으면서 코드가 복잡하고 읽기 어렵다. 다음과 같이 `filter`, `map`, `reduce`로 역할을 분리하면 더 간결해진다.

```typescript
// [코드 5-6] filter, map, reduce로 역할 분리
const sumSelectedQuantities = (products: Product[]) =>
  products
    .filter(prd => prd.selected)           // 선택된 상품만 필터링
    .map(prd => prd.quantity)              // 수량만 추출
    .reduce((a, b) => a + b, 0);

const calcSelectedPrices = (products: Product[]) =>
  products
    .filter(prd => prd.selected)           // 선택된 상품만 필터링
    .map(prd => prd.price * prd.quantity)  // 총 가격 계산
    .reduce((a, b) => a + b, 0);
```

`filter`, `map`, `reduce`로 역할을 명확히 분리하면 코드의 가독성이 크게 향상된다. 각 단계에서 어떤 작업이 수행되는지 명확히 드러나기 때문에 이해하기 쉽다.

### 1.4 커머스 데이터 다루기 2

현실적인 커머스 환경에서는 장바구니 데이터가 단순히 상품명, 가격, 수량으로만 구성되지 않는다. 의류 상품의 경우 사이즈나 색상 옵션이 추가될 수 있으며 옵션마다 가격이나 수량이 달라질 수 있다.

```typescript
// [코드 5-7] 옵션이 추가된 장바구니 데이터 구조
type Option = {
  name: string;
  price: number;
  quantity: number;
};

type Product = {
  name: string;
  price: number;
  selected: boolean;
  options: Option[];
};

const products: Product[] = [
  {
    name: '티셔츠', price: 10000, selected: true,
    options: [
      { name: 'L', price: 0, quantity: 3 },
      { name: 'XL', price: 1000, quantity: 2 },
      { name: '2XL', price: 3000, quantity: 2 },
    ]
  },
  {
    name: '셔츠', price: 30000, selected: false,
    options: [
      { name: 'L', price: 0, quantity: 2 },
      { name: 'XL', price: 1000, quantity: 5 },
      { name: '2XL', price: 3000, quantity: 4 },
    ]
  },
  {
    name: '바지', price: 15000, selected: true,
    options: [
      { name: 'XL', price: 500, quantity: 3 },
      { name: '2XL', price: 3000, quantity: 5 },
    ]
  }
];
```

데이터 구조가 더 복잡해졌지만 함수형 프로그래밍을 통해 동일한 접근 방식으로 처리할 수 있다.

```typescript
// [코드 5-8] 옵션 데이터를 포함한 전체 수량과 가격 계산
const sumSelectedQuantities2 = (products: Product[]) =>
  products
    .filter(prd => prd.selected)                           // 선택된 상품만 필터링
    .map(prd => prd.options)                               // 각 상품의 옵션 배열로 변환
    .flat()                                                // 옵션 배열을 펼쳐 1차원 배열로 변환
    .map(opt => opt.quantity)                              // 각 옵션의 수량 추출
    .reduce((a, b) => a + b, 0);                          // 총합 계산

const calcSelectedPrices2 = (products: Product[]) =>
  products
    .filter(prd => prd.selected)                           // 선택된 상품만 필터링
    .map(prd => prd.options.map(
      opt => (prd.price + opt.price) * opt.quantity        // 옵션별 최종 가격 계산
    ))
    .flat()                                                // 모든 옵션의 가격 배열을 펼침
    .reduce((a, b) => a + b, 0);                          // 총합 계산

console.log(sumSelectedQuantities2(products)); // 선택된 상품의 총 수량: 15
console.log(calcSelectedPrices2(products));     // 선택된 상품의 총 가격: 214500
```

가격 계산 로직을 함수로 추출하면 가독성과 재사용성이 더 높아진다.

```typescript
// [코드 5-10] 비슷한 구조를 가진 코드로 정리
const calcProductPrice = (prd: Product) => prd.price * prd.quantity;

const calcProductOptionPrices = (prd: Product) =>
  prd.options.map(opt => (prd.price + opt.price) * opt.quantity);

const calcTotalPrice = (products: Product[]) =>
  products
    .flatMap(calcProductOptionPrices)
    .reduce((a, b) => a + b, 0);

const calcSelectedPrices = (products: Product[]) => calcTotalPrice(
  products.filter(prd => prd.selected)
);

console.log(calcTotalPrice(products));     // 모든 상품 총 가격: 561500
console.log(calcSelectedPrices(products)); // 선택된 상품의 총 가격: 214500
```

같은 로직을 명령형으로 작성하면(원서 [코드 5-12]) 중첩 `for`문과 조건문, 임시 변수 선언과 `push` 누적이 하나의 긴 흐름으로 이어져 각 단계의 의도가 드러나지 않고, 일부만 수정·재사용·테스트하기도 어렵다. 리스트 프로세싱은 `filter`·`map`·`reduce`로 각 작업이 분리되어 있어 이런 문제를 자연스럽게 피한다.

### 1.5 일관된 접근 방식으로 문제 해결하기

지금까지 함수형 프로그래밍을 활용하여 다양한 데이터 구조를 처리하는 방법을 살펴보았다. 함수형 프로그래밍의 이점을 정리하면 다음과 같다.

- **일관성**: 다양한 데이터 구조에 동일한 패턴으로 적용할 수 있어 코드가 예측 가능하고 읽기 쉬워진다.
- **가독성**: 로직을 분리해 작성함으로써 각 작업의 역할이 명확히 드러나며 가독성을 크게 향상시킬 수 있다.
- **재사용성**: `filter`, `map`, `reduce` 단계를 독립적으로 작성하면 다른 데이터 처리 작업에서도 재사용할 수 있다.
- **유지보수성**: 단계별로 코드를 수정하거나 확장하기 쉽다.
- **디버깅 용이성**: 각 단계의 중간 데이터를 쉽게 확인할 수 있어 오류를 빠르게 찾아낼 수 있다.

---

## 2. 더 많은 문제에 적용하기

이 절에서는 함수형 프로그래밍을 더 넓은 문제 범위로 적용하려 할 때 알아두면 좋은 여러 함수를 다룬다. 이를 효과적으로 살펴보고자 타입스크립트 기반의 함수형 프로그래밍 라이브러리인 FXTS를 활용한다.

FXTS는 Iterable/AsyncIterable 프로토콜에 기반한 다양한 리스트 프로세싱 함수 세트와 타입 추론, 비동기/병렬/동시성 프로그래밍을 강력하게 지원하여 실제 업무 환경에서 유용하게 활용할 수 있다.

> **참고**: 이 오픈 소스 프로젝트는 조현우 님이 주도해 개발한 것으로 탄탄한 기본기와 프로그래밍 언어 전반에 대한 깊은 통찰을 바탕으로 설계된 고수준의 함수형 라이브러리다. 네이버와 네이버페이 등에서 풍부한 경험을 쌓은 뒤 현재는 마플코퍼레이션에서 테크 리드로 활약 중인 조현우 님은 저자에게도 많은 배움을 주는 존경하는 동료이자 훌륭한 개발자다.

### 2.1 pipe 함수

`pipe`는 여러 함수를 연속적으로 적용하여 값을 처리하는 함수다. `pipe`는 주로 두 개 이상의 함수를 합성하고 코드의 표현력을 높이기 위해 사용한다.

```typescript
// [코드 5-13] pipe를 사용한 함수의 연속 적용
import { pipe } from "@fxts/core";

const result = pipe(
  10,
  a => a + 4,  // a = 10
  a => a / 2,  // a = 14
);

console.log(result); // 7
```

`pipe`의 로직은 `reduce`라고 표현할 수 있다. `pipe`는 `reduce`를 활용해 여러 함수를 이터러블로 다루며 각 함수의 결과를 다음 함수에 연속적으로 전달하여 최종 결과를 생성한다.

#### 커링과 함께 사용하기

`pipe`는 커링을 지원하는 함수와 결합될 때 강력한 타입 추론을 제공한다.

```typescript
// [코드 5-14] 커링이 적용된 add 함수
const add = (a: number) => (b: number) => a + b;  // ①
const result = add(10)(5);   // ②
console.log(result); // 15

const add10 = add(10);       // 인자가 a만 적용된 상태의 함수
console.log(add10(5)); // 15

const result2: number = pipe( // ③
  5,
  add(10),
  add(5),
);
console.log(result2); // 20
```

FXTS의 리스트 프로세싱 함수들은 커링을 지원하면서도 `pipe` 함수를 통해 타입 추론을 제공한다.

```typescript
// [코드 5-15] pipe와 map, filter, forEach
import { pipe, map, filter, forEach } from "@fxts/core";

pipe(
  ['1', '2', '3', '4', '5'],
  map(a => parseInt(a)),       // [a: string]
  filter(a => a % 2 === 1),    // [a: number]
  forEach(console.log),
);
// 1
// 3
// 5
```

`pipe`는 체이닝보다 유연한 코드 구성을 제공한다. 체이닝은 주로 클래스의 메서드를 통해 확장되지만 `pipe`는 라이브러리가 제공하지 않는 함수나 사용자 정의 로직을 자유롭게 조합할 수 있다.

```typescript
// [코드 5-16] pipe에 console.log 사용하기
import { pipe, map, filter, reduce } from "@fxts/core";

pipe(
  ['1', '2', '3', '4', '5'],
  map(a => parseInt(a)),
  filter(a => a % 2 === 1),
  reduce((a, b) => a + b),
  console.log,
);
// 9
```

`console.log`는 `pipe` 함수가 구현된 라이브러리에서 제공하는 함수가 아니지만 자연스럽게 조합해 사용되었다. 이처럼 `pipe`는 라이브러리와 무관한 일반 함수도 유연하게 통합할 수 있다.

### 2.2 pipe와 비동기 함수 합성

`pipe`를 활용하면 동기 함수와 비동기 함수를 자연스럽게 결합하여 선언적으로 작업 흐름을 표현할 수 있다.

```typescript
// [코드 5-18] 비동기 함수 합성
import { pipe, delay } from "@fxts/core";

const result = await pipe(
  Promise.resolve(5),                 // 초기 비동기 값
  a => a + 10,                        // 동기 함수: a는 5
  async a => {                        // 비동기 함수: a는 15
    await delay(1000);                // 1초 대기
    return a * 2;
  },
  a => a - 5,                         // 동기 함수: a는 30
);

console.log(result); // 결과: 25
```

`pipe`는 비동기 함수의 결과(Promise)를 자동으로 처리하여 다음 함수의 인자로 전달하며 각 단계에서 정확한 타입 추론을 제공한다.

```typescript
// [코드 5-19] 비동기 리스트 프로세싱과 합성
import { pipe, toAsync, map, filter, toArray, fx } from "@fxts/core";

const arr = [1, 2, 3, 4, 5];

// pipeline
const result2 = await pipe(
  arr,
  toAsync,
  map(a => Promise.resolve(a + 10)),  // Promise<number>를 반환해도
  filter(a => a % 2 === 0),           // filter의 a는 Promise가 벗겨진 11, 12, 13...
  toArray,
  arr => arr.reverse(),
);
console.log(result2); // [14, 12]

// chaining
const result3 = await fx(arr)
  .toAsync()
  .map(a => Promise.resolve(a + 10))
  .filter(a => a % 2 === 0)
  .toArray()
  .then(arr => arr.reverse());
console.log(result3); // [14, 12]
```

### 2.3 zip 함수

프로그래밍을 하다 보면 `i++`처럼 증가하는 인덱스를 사용해야 하는 상황이 있다. `zip` 함수는 두 배열을 결합하여 entries 형태의 이터러블을 생성하는 함수다.

```typescript
// [코드 5-22] zip(keys, values)
import { zip } from "@fxts/core";

const keys = ['name', 'job', 'location'];
const values = ['Marty', 'Programmer', 'New York'];

const iterator = zip(keys, values);
console.log(iterator.next()); // { done: false, value: ['name', 'Marty'] }
console.log(iterator.next()); // { done: false, value: ['job', 'Programmer'] }
console.log(iterator.next()); // { done: false, value: ['location', 'New York'] }
console.log(iterator.next()); // { done: true, value: undefined }

const obj = Object.fromEntries(zip(keys, values));
console.log(obj);
// { name: 'Marty', job: 'Programmer', location: 'New York' }
```

```typescript
// [코드 5-23] pipe와 함께 사용
pipe(
  zip(keys, values),
  Object.fromEntries,
  console.log,
);
// { name: 'Marty', job: 'Programmer', location: 'New York' }

pipe(
  values,
  zip(keys),  // 커링
  Object.fromEntries,
  console.log,
);
// { name: 'Marty', job: 'Programmer', location: 'New York' }
```

### 2.4 인덱스가 값으로 필요할 때

증가하는 인덱스가 필요한 대부분의 상황은 `zip`을 사용해 선언적으로 해결할 수 있다. `range` 함수를 활용하면 동적으로 숫자를 생성할 수 있다.

```typescript
// [코드 5-25] range 함수로 동적인 숫자 생성
import { range, zip } from "@fxts/core";

const strings = ['a', 'b', 'c', 'd', 'e'];
const iter2 = zip(range(Infinity), strings);

for (const a of iter2) {
  console.log(a);
}
// [0, 'a']
// [1, 'b']
// [2, 'c']
// [3, 'd']
// [4, 'e']
```

`range(Infinity)`는 무한 이터레이터를 생성한다. `zip(range(Infinity), strings)`는 `strings`가 끝날 때까지 인덱스와 문자열을 묶어 반환한다.

### 2.5 콜라츠 추측 - 1이 될 때까지 세기

콜라츠 추측(*Collatz Conjecture*)은 1937년 독일 수학자 로타르 콜라츠가 제안한 수학적 추측으로 모든 양의 정수에 대해 다음 규칙을 적용할 때 항상 1로 수렴한다는 내용이다.

**규칙**:
1. 주어진 수가 짝수라면 그 수를 2로 나눈다.
2. 주어진 수가 홀수라면 그 수에 3을 곱하고 1을 더한다.
3. 이 과정을 반복한다.

```typescript
// [코드 5-26] collatzCount 함수
import { range, pipe, zip, find, head } from "@fxts/core";

// 숫자가 start부터 증가되는 이터레이터를 만드는 재사용 가능한 함수
const count = (start = 1) => range(start, Infinity);

// 초깃값과 함수를 받아 무한히 반복하여 적용하는 재사용 가능한 함수
function* repeatApply<A>(f: (acc: A) => A, acc: A) {
  while (true) yield acc = f(acc);
}

const nextCollatzValue = (num: number) =>
  num % 2 === 0   // 짝수이면
    ? num / 2
    : num * 3 + 1;

const collatzCount = (num: number) => pipe(
  zip(
    count(),                               // ① 카운트 이터레이터
    repeatApply(nextCollatzValue, num),     // 콜라츠 작업을 무한 반복 적용
  ),                                        // zip으로 작업 결과에 카운팅 숫자 추가 [cnt, val]
  find(([cnt, val]) => val === 1),         // 결과가 1이 될 때까지 이터레이터를 소비
  collatz => collatz!,                      // ⑤ !로 단언 (콜라츠 추측은 참일 것)
  head,                                     // ⑥ [cnt, val] 중 cnt를 반환
);

console.log(collatzCount(1)); // 3
console.log(collatzCount(4)); // 2
console.log(collatzCount(5)); // 5
```

이 코드는 '콜라츠 작업을 1이 될 때까지 수행하고 횟수를 반환한다'는 문제 정의를 거의 그대로 표현하고 있다. 또한 시간 복잡도 측면에서도 효율적으로 작성되었다. 지연 평가되는 이터레이터를 `find`로 필요한 만큼만 소비하여 처리하기 때문이다.

검증 관점에서도 이점이 있다. `count`, `repeatApply`, `nextCollatzValue`, `zip`, `find`, `head` 같은 구성 요소는 각각 하는 일이 단순해서 개별적으로 테스트하고 검증하기 쉽다. 그리고 `collatzCount`는 이 함수들을 상태 변화나 추가 조건문 없이 순차적으로 조합한 하나의 표현식일 뿐이므로, 각 함수가 검증되어 있다면 조합이 실패할 가능성은 매우 낮다. 이처럼 코드 동작에 대한 신뢰를 빠르게 확보할 수 있다는 점은 함수형 프로그래밍이 개발 생산성을 높이는 중요한 요소다.

### 2.6 break를 대신하는 take, takeWhile, takeUntilInclusive

`break`는 명령형 코드에서 반복문의 불필요한 반복을 줄이고 시간 복잡도를 낮추기 위해 사용된다. 함수형 프로그래밍에서도 이와 비슷한 역할을 하는 `take`, `find`, `some`, `every`, `head` 등의 함수들이 존재한다.

- **takeWhile**: 조건이 `true`일 동안의 요소를 반환하며 조건이 처음으로 `false`가 되는 순간 평가를 멈추고 소비를 중단한다. 단, 조건을 평가하기 위해 `false`로 판정된 첫 번째 값은 소비된다.
- **takeUntilInclusive**: 조건이 `true`가 되는 순간 해당 값을 포함해 반환하며 소비를 중단한다. 이후의 요소는 추가로 소비되지 않는다.

```typescript
// [코드 5-28] takeWhile, takeUntilInclusive 실행 결과
import { fx } from "@fxts/core";

fx([1, 2, 3, 0, 0, 0, 5, 6])
  .takeWhile(a => a >= 1)
  .forEach(a => console.log(a));
// 1, 2, 3 (0에서 false → 중단, 결과: [1, 2, 3])

fx([0, 10, 1, 3, 5, 0, 4, 2])
  .takeUntilInclusive(a => a === 5)
  .forEach(a => console.log(a));
// 0, 10, 1, 3, 5 (5에서 true → 포함 후 중단, 결과: [0, 10, 1, 3, 5])
```

정리하자면 `takeWhile`은 결과물의 완전성을 보장하는 데 초점을 맞추며 조건을 만족하는 구간만 추출하는 데 유용하다. 반면 `takeUntilInclusive`는 조건 만족과 소비 중단의 효율성에 초점을 맞추며 특정 조건에 도달하는 순간 작업을 멈추는 데 유용하다.

### 2.7 함수의 조합으로 만들어내는 로직

이 절에서는 `pipe`, `zip`, `range`, `take`, `takeWhile`, `takeUntilInclusive` 그리고 이들을 보조하는 다양한 함수를 탐구했다. 처음에는 명령형으로만 해결할 수 있을 것 같던 문제들 역시 리스트 프로세싱을 통해 선언적이고 유연하게 접근할 수 있음을 확인할 수 있었다.

---

## 3. 백엔드 비동기 프로그래밍

이 절에서는 백엔드 프로그래밍에서 자주 직면하는 문제를 함수형 스타일과 리스트 프로세싱을 활용해 해결해본다. 예제로는 특정 시간에 반복적으로 실행되는 스케줄러 작업과 같은 프로그램을 작성한다.

### 3.1 커머스 플랫폼의 결제 프로세스 문제

결제 과정에서 네트워크 장애, 브라우저 종료, 서버 장애 등 다양한 이유 때문에 결제 성공 알림이 커머스 플랫폼에 정상적으로 전달되지 못하는 상황이 발생할 수 있다. 이를 해결하려면 주기적으로 PG사의 결제 데이터를 조회하여 우리 커머스 플랫폼의 데이터와 대조하는 작업이 필요하다.

### 3.2 결제 내역 동기화 스케줄러 만들기

먼저 PG사 SDK와 StoreDB를 가상으로 정의한다.

```typescript
// [코드 5-29] PG사 SDK
type Payment = {
  pg_uid: string;
  store_order_id: number;
  amount: number;
};

const PgApi = {
  async getPayments(page: number) {
    console.log(`결제 내역 요청: https://pg.com/payments?page=${page}`);
    await delay(500);
    const payments = pgDataPaymentsPages[page - 1] ?? [];
    console.log(
      `${payments.length}건: ${payments.map(p => p.pg_uid).join(', ') || '-'}`
    );
    return payments;
  },
  async cancelPayment(pg_uid: string) {
    console.log(`취소 요청: ${pg_uid}`);
    await delay(300);
    return {
      code: 200,
      message: `${pg_uid}: 취소 및 환불 완료`,
      pg_uid,
    };
  }
};
```

```typescript
// [코드 5-30] StoreDB
type Order = {
  id: number;
  amount: number;
  is_paid: boolean;
};

const StoreDB = {
  async getOrders(ids: number[]): Promise<Order[]> {
    console.log(`SELECT * FROM orders WHERE IN (${ids}) AND is_paid = true;`);
    await delay(100);
    return [
      { id: 1, amount: 15000, is_paid: true },
      { id: 3, amount: 10000, is_paid: true },
      { id: 5, amount: 45000, is_paid: true },
      { id: 7, amount: 20000, is_paid: true },
      { id: 8, amount: 30000, is_paid: true },
    ];
  }
};
```

원서는 이 코드를 단계적으로 발전시킨다(원서 [코드 5-31]~[코드 5-35]). 먼저 주석으로 '1. 결제 내역 가져오기 → 2. 주문 데이터와 매칭 → 3. 누락 결제 취소'라는 전체 계획을 세우고, 언제 끝날지 모르는 반복 작업을 무한 이터러블 `range(1, Infinity)`로 표현한 뒤 임시 `take(5)`와 가짜 데이터로 뼈대부터 검증한다. 이후 `PgApi.getPayments`를 연결하고 `takeWhile(({ length }) => length > 0)`을 적용하는데, `takeWhile`은 조건이 거짓이 되는 요소까지 소비하므로 데이터가 없는 페이지에 한 번 더 요청이 발생한다(4번 요청). 한 페이지의 최대 결제 내역이 3개라는 사실을 이용해 `takeUntilInclusive(({ length }) => length < 3)`으로 바꾸면 처음으로 3건 미만이 반환되는 순간 즉시 멈춘다(3번 요청). 완성된 코드는 다음과 같다.

```typescript
// [코드 5-36] takeUntilInclusive 적용
import { fx, range } from "@fxts/core";

async function syncPayments() {
  // 1. PG사의 결제 내역(payments) 가져오기
  const payments = await
    fx(range(1, Infinity))                                    // 언제 끝날지 모르는 작업 목록
      .toAsync()                                               // 비동기 작업으로 변환
      .map(page => PgApi.getPayments(page))                   // 결제 내역 가져오기 API 요청
      .takeUntilInclusive(({ length }) => length < 3)         // 처음으로 3보다 적을 때 즉시 멈춤
      .flat()                                                  // 2차원 이터레이터를 1차원으로 변경
      .toArray();                                              // 이터러블을 Array로 변환

  // 2. PG사 결제 내역과 일치하는 커머스 플랫폼의 주문 데이터를 조회
  const orders = await StoreDB.getOrders(
    payments.map(p => p.store_order_id)
  );

  // 3. 누락된 결제 취소 및 환불 처리
  await fx(payments)
    .toAsync()
    .reject(p => orders.some(order => order.id === p.store_order_id))
    .forEach(async p => {
      const { message } = await PgApi.cancelPayment(p.pg_uid);
      console.log(message);
    });
  // PG12: 취소 및 환불 완료
  // PG14: 취소 및 환불 완료
  // PG16: 취소 및 환불 완료
}
```

### 3.3 해시 기반 접근으로 시간 복잡도 최적화

기존 코드는 `reject` 단계에서 `orders.some`으로 `orders` 배열을 순회하며 결제 데이터와 주문 데이터를 매칭했다. 이는 최악의 경우 O(n * m)의 시간 복잡도를 가질 수 있다. `orders`를 해시 구조로 변환하여 O(1)로 확인할 수 있도록 최적화한다.

```typescript
// [코드 5-38] 해시로 변경하여 조회하기
const ordersById = Object.fromEntries(
  map(order => [order.id, true], orders)
);
// {1: true, 3: true, 5: true, 7: true, 8: true}

await fx(payments)
  .toAsync()
  .reject(p => ordersById[p.store_order_id])  // O(1)로 매칭된 결제 내역 제거
  .forEach(async p => {
    const { message } = await PgApi.cancelPayment(p.pg_uid);
    console.log(message);
  });
```

대규모 데이터셋의 경우 `Object`보다 `Map`을 사용하는 것이 성능 면에서 더 효율적이다.

### 3.4 안정적인 비동기 작업 간격 유지

`syncPayments`를 일정한 시간 간격으로 반복 실행하도록 구현한다.

```typescript
// [코드 5-40] 안정적인 비동기 반복
async function runScheduler() {
  await fx(range(Infinity))
    .toAsync()
    .forEach(() => Promise.all([
      syncPayments(),
      delay(10000)
    ]));
}
```

`Promise.all`을 사용해 `syncPayments()`와 `delay(10000)`을 동시에 실행한다. `syncPayments`가 10초보다 오래 걸리면 `syncPayments`의 실행 시간이 작업 간격을 결정하고, 10초보다 적게 걸리면 `delay(10000)`으로 인해 충분히 대기한 후에 반복 작업이 실행된다.

### 3.5 최대 요청 크기 제한을 효과적으로 처리하기

`StoreDB.getOrders` 함수가 한 번에 처리할 수 있는 요청 크기를 5개로 제한한다면 `chunk`를 활용해 요청을 분할한다.

```typescript
// [코드 5-43] 요청을 안전하게 분할하기: chunk와 flatMap
const orders = await
  fx(payments)
    .map(p => p.store_order_id)       // ① ID 추출
    .chunk(5)                          // ② 5개씩 분할
    .toAsync()                         // ③ 비동기 전환
    .flatMap(StoreDB.getOrders)        // ④ 분할된 그룹별로 조회 후 평탄화
    .toArray();                        // ⑤ 배열로 변환
```

### 3.6 사전 카운트로 효율 높이기

PG사에 페이지 카운트를 빠르게 반환하는 API가 있다면 `range(1, Infinity)` 대신 `range(1, totalPages + 1)`을 사용하여 정확히 필요한 만큼만 요청할 수 있다.

```typescript
// [코드 5-45] 사전 카운트 활용
const totalPages = await PgApi.getPageCount();
const payments = await
  fx(range(1, totalPages + 1))
    .toAsync()
    .map(page => PgApi.getPayments(page))
    .flat()
    .toArray();
```

### 3.7 병렬성으로 효율 높이기

총 몇 페이지를 요청해야 하는지 알면 병렬 처리를 활용하여 요청 시간을 단축할 수 있다. `concurrent` 메서드를 추가하면 인자로 전달받은 수만큼 동시에 이터레이터를 소비한다. 예를 들어 1초씩 걸리는 비동기 작업 6개를 순차로 소비하면 6초가 걸리지만, `concurrent(2)`를 추가하면 3초, `concurrent(4)`면 2초로 줄어든다(원서 [코드 5-46]~[코드 5-47]).

```typescript
// [코드 5-48] 병렬 요청
const payments = await
  fx(range(1, totalPages + 1))
    .toAsync()
    .map(page => PgApi.getPayments(page))
    .concurrent(totalPages)        // totalPages 개수만큼 동시에 병렬로 요청
    .flat()
    .toArray();
```

[코드 5-36]에서는 `getPayments` 3회를 순차 수행해 총 1500ms 정도가 걸렸지만, [코드 5-48]은 50ms가 걸리는 `getPageCount` 1회 후 `getPayments` 3회를 동시에 실행해 약 550ms에 끝난다. 순차 처리는 각 응답 시간의 합이 전체 시간이 되고, 병렬 처리는 가장 오래 걸리는 요청 하나가 전체 시간을 결정하기 때문이다.

요청 제한에 의해 동시에 최대 2개의 요청으로 제한해야 한다면 `concurrent(2)`를 전달하면 된다.

```typescript
// [코드 5-49] 병렬 크기 제한
const RATE_LIMIT = 2;
const payments = await
  fx(range(1, totalPages + 1))
    .toAsync()
    .map(page => PgApi.getPayments(page))
    .concurrent(RATE_LIMIT)        // 항상 최대 2개씩 동시 요청
    .flat()
    .toArray();
```

### 3.8 리스트 프로세싱 기반 비동기/동시성 프로그래밍

지금까지 백엔드 프로그래밍에서 자주 직면하는 문제를 해결하기 위한 리스트 프로세싱의 여러 접근 방식을 살펴보았다. 데이터 불일치 해결, 해시 기반 시간 복잡도 최적화, 안정적인 비동기 작업 간격 유지, 최대 요청 크기 제한 처리, 사전 카운트 활용, 병렬 요청 등의 기법은 현대적인 백엔드 시스템 설계에서 신뢰성과 확장성을 확보하는 데 중요한 역할을 한다.

---

## 4. 리스트 프로세싱 패턴화

지금까지 다양한 문제를 해결하며 리스트 프로세싱의 실질적 이점을 경험했다. 이 절에서는 리스트 프로세싱의 다양한 조합을 좀 더 구조적으로 이해할 수 있도록 패턴화된 사례를 소개한다.

### 4.1 변형-누적 패턴

변형-누적(*map-reduce*) 패턴은 리스트 프로세싱에서 가장 널리 사용되는 패턴 중 하나다. 초기 이터러블을 `map`으로 변형한 뒤 `reduce`로 누적하여 최종 결과를 도출하는 방식이다. 프로그램의 결과물이 단일 값일 때 주로 사용한다.

```typescript
// [코드 5-50] 상품의 총 수량
const totalQuantity = products =>
  products
    .map(product => product.quantity)
    .reduce((a, b) => a + b, 0);
```

```typescript
// [코드 5-51] QueryString을 객체로 변환
const queryString = "name=Marty%20Yoo&age=41&city=Seoul";
const queryObject = queryString
  .split("&")
  .map(param => param.split("="))
  .map(entry => entry.map(decodeURIComponent))
  .map(([key, val]) => ({ [key]: val }))
  .reduce((a, b) => Object.assign(a, b), {});

console.log(queryObject);
// {name: "Marty Yoo", age: "41", city: "Seoul"}
```

`join`이나 `Object.fromEntries`, `Array.fromAsync` 같은 헬퍼 함수들도 본질적으로는 `reduce`로 구현할 수 있는 동작을 추상화한 함수다. 변형-누적은 그만큼 근본적인 패턴이다.

### 4.2 중첩-변형 패턴

중첩-변형(*nested-map*) 패턴은 중첩된 데이터 구조를 처리하거나 데이터의 계층을 따라 각 수준에서 변형을 수행할 때 사용하는 패턴이다. `map(map(f))`처럼 `map` 안에서 다시 `map`을 호출하는 경우에 적합하다.

```typescript
// [코드 5-56] 달력 출력 포맷팅 (원서 달력 생성 예제에서 발췌)
import { pipe, map, join } from "@fxts/core";

const formatCalendar = (calendarWeeks: number[][]) =>
  pipe(
    calendarWeeks,
    map(map(day => (day < 10 ? ` ${day}` : `${day}`))),   // 중첩-변형: 안쪽 요소(날짜)를 두 자리 문자열로
    map(join(' ')),                                         // 각 주(안쪽 배열)를 하나의 문자열로 누적
    join('\n'),                                             // 주 단위 문자열들을 줄바꿈으로 누적
  );

console.log(formatCalendar([
  [29, 30, 1, 2, 3, 4, 5],
  [6, 7, 8, 9, 10, 11, 12],
]));
// 29 30  1  2  3  4  5
//  6  7  8  9 10 11 12
```

원서 [코드 5-56]은 여기에 `range`로 지난달·이번달·다음달 날짜를 만들고 `flat`으로 평탄화한 뒤 `chunk(7)`로 주 단위로 재분할하는 `generateCalendar`를 합성하여 완전한 달력을 생성한다. 2차원 배열의 안쪽 요소를 `map(map(f))`으로 변형하고 `map(join(' '))`과 `join('\n')`으로 레벨마다 차례로 누적해 올라오는 구조가 중첩-변형 패턴의 전형이다.

### 4.3 반복자-효과 패턴

반복자-효과(*iterator-forEach*) 패턴은 이터레이터를 만들어 둔 후 지연 평가를 통해 데이터를 소비하며 부수적인 효과(`forEach`)를 발생시키는 패턴이다. 작업 자체가 목적이 되는 경우에 적합하다.

`forEach`는 반환 값이 없는 메서드로 명시적으로 부수 효과를 수반하는 동작을 수행하기 위해 설계되었다. 데이터의 순수한 변환은 `map`, `filter`, `reduce`에서 처리되고 DOM 삭제, 파일 저장, 로그 작성, API 호출 등의 부수 효과는 `forEach` 내에서 처리된다.

때로는 부수 효과를 일으키면서도 실행 결과를 반환해야 하는 경우가 있다. 이때는 `mapEffect` 같은 함수명을 사용하여, `map`과 유사하게 동작하지만 부수 효과를 포함한 동작임을 이름으로 명확히 표현할 수 있다.

```typescript
// [코드 5-59a] 결제 취소 — 부수 효과 구간을 이름으로 드러내기
await fx(payments)
  .toAsync()
  .reject(p => ordersMapById.has(p.store_order_id))  // ordersMapById: orders를 Map 해시로 변환(3.3절)
  .mapEffect(p => PgApi.cancelPayment(p.pg_uid))     // 부수 효과 + 결과 반환
  .forEach(res => console.log(res.message));         // 부수 효과만
```

이렇게 순수한 변환(`map`·`filter`·`reduce`)과 부수 효과(`forEach`·`mapEffect`)를 구분하면 어떤 코드 블록에서 어떤 변화가 일어나는지 예측하기 쉬워 디버깅과 유지보수가 용이해진다. 부수 효과를 의도적으로 허용하되 그 구간을 이름으로 명확히 구분하는 것 — 순수 함수와 부수 효과의 격리라는 함수형 프로그래밍의 철학을 실현하는 실용적인 도구다.

### 4.4 필터-중단 패턴

필터-중단(*filter-take*) 패턴은 데이터를 조건에 따라 필터링한(`filter`) 후 일부 데이터만 선택하여(`take`) 소비하는 패턴이다. 대규모 데이터에서 특정 조건을 만족하는 일부 데이터만 빠르게 추출해야 할 때 유용하다.

```typescript
// [코드 5-60] find, some, every 함수
const find = <A>(f: (a: A) => boolean, iterable: Iterable<A>) =>
  pipe(
    iterable,
    filter(f),
    take(1),
    ([found]) => found as A | undefined
  );

const some = <A>(f: (a: A) => boolean, iterable: Iterable<A>) =>
  pipe(
    iterable,
    filter(f),
    take(1),
    ([...arr]) => arr.length === 1,
  );

const every = <A>(f: (a: A) => boolean, iterable: Iterable<A>) =>
  pipe(
    iterable,
    reject(f),
    take(1),
    ([...arr]) => arr.length === 0,
  );
```

### 4.5 무한-중단 패턴

무한-중단(*range-take*) 패턴은 끝이 없는 데이터 스트림에서 필요한 만큼만 데이터를 추출하기 위한 패턴이다. `range`를 사용해 무한히 증가하는 숫자나 특정 규칙을 따르는 데이터를 생성하고 `take`를 이용해 원하는 개수만큼 데이터를 추출한다. 명령형 스타일로 비유하자면 `while-break` 구조와 유사한 역할을 한다.

### 4.6 분할-평탄 패턴

분할-평탄(*chunk-flat*) 패턴은 데이터를 일정 크기로 분할한 뒤 다시 평탄화하여(`flat`) 원하는 형태로 변환하는 기법이다. 요청 크기 제한이 있는 API 호출이나 페이지 단위로 데이터를 처리할 때 이 패턴을 적용할 수 있다.

```typescript
// [코드 5-63] API 요청 크기 제한 적용
const orders = await
  fx(payments)
    .map(p => p.store_order_id)
    .chunk(5)              // 요청을 5개씩 분할
    .toAsync()
    .map(StoreDB.getOrders)
    .flat()                // 평탄화
    .toArray();
```

### 4.7 변형-평탄 패턴

변형-평탄(*map-flat*) 패턴은 데이터를 변형한(`map`) 뒤 결과를 평탄화하여(`flat`) 하나의 연속된 데이터 흐름으로 만드는 기법이다. `map(f).flat()`은 매우 자주 사용되는 패턴으로 이를 간결하게 처리하기 위해 `flatMap`과 같은 함수를 제공하기도 한다.

```typescript
// [코드 5-65] 데이터 다루기
const totalHighScorers = teams
  .flatMap(team => team.players)          // 변형 후 평탄화
  .map(player => player.score)
  .reduce((a, b) => a + b, 0);
```

### 4.8 결합-누적 패턴

결합-누적(*zip-reduce*) 패턴은 여러 이터러블을 결합한(`zip`) 후 이를 순회하며 최종 결과를 누적하는(`reduce`) 패턴이다.

```typescript
// [코드 5-67] 리스트에 고유 ID 부여
const items = ["Apple", "Banana", "Cherry"];

const itemsWithIds = pipe(
  zip(range(Infinity), items),
  map(([id, item]) => ({ id, item })),
  toArray
);
// [{ id: 0, item: "Apple" }, { id: 1, item: "Banana" }, { id: 2, item: "Cherry" }]
```

### 4.9 해시-매치 패턴

해시-매치(*hash-match*) 패턴은 데이터를 효율적으로 구성하거나 조회하기 위해 해시 구조(키-값 맵)를 생성하는 데 사용된다. `indexBy`, `groupBy`와 같은 작업이 이에 해당한다.

```typescript
// [코드 5-68] posts와 users 매칭
const usersById = indexBy(user => user.id, users);
const postsWithUsers = posts.map(post => ({
  ...post,
  user: usersById[post.user_id],
}));
```

```typescript
// [코드 5-69] posts와 comments 매칭 (groupBy)
const commentsByPostId = groupBy(comment => comment.post_id, comments);
const postsWithComments = posts.map(post => ({
  ...post,
  comments: commentsByPostId[post.id] || [],
}));
```

### 4.10 리스트 프로세싱 함수 유형별 개념 정리

리스트 프로세싱 함수를 다음과 같은 관점으로 분류할 수 있다.

| 유형 | 설명 | 예시 함수 |
|------|------|-----------|
| **지연 중간 연산** | 결과가 실제로 필요할 때까지 연산을 미루며 이 단계만으로는 최종 결과가 나오지 않는다 | `map`, `filter`, `zip` 등 |
| **단축(short-circuit) 중간 연산** | 특정 조건이 충족되면 그 시점에서 더 이상 데이터를 읽지 않아 불필요한 연산을 건너뛴다 | `take`, `takeWhile`, `takeUntilInclusive` 등 |
| **터미널 연산** | 실제 이터러블을 전부(또는 조건부로) 소비하여 최종 결과를 만들어낸다. 한 번 연산을 호출하면 지연이 해제되고 실제 순회가 일어난다 | `find`, `every`, `some`, `reduce` 등 |
| **폴드/리듀스 연산** | 터미널 연산 중에서도 시퀀스 전체를 하나의 값으로 누적하여 반환하는 연산이다 | `reduce`, `groupBy`, `indexBy`, `Promise.all`, `Array.fromAsync` 등 |
| **부수 효과** | 출력/로그/파일 쓰기 등 외부 상태를 변화시키는 연산이다 | `forEach` 등 |

---

## 요약

- **실전 데이터 다루기**: 함수형 프로그래밍은 다양한 데이터 구조에 동일한 패턴을 적용함으로써 코드의 일관성과 예측 가능성을 높인다. `filter`, `map`, `reduce` 등으로 작업을 명확히 분리하여 각 단계의 역할을 드러내고 가독성을 크게 향상시킨다.
- **더 많은 문제에 적용하기**: `pipe`, `zip`, `range`, `takeWhile`, `takeUntilInclusive` 등의 함수들은 함수형 프로그래밍을 다양한 명령형 문제에 효과적으로 적용할 수 있도록 확장한다. 특히 `take` 계열 함수들은 단순히 데이터를 일부 추출하는 유틸리티가 아니라 반복 작업의 실행 범위를 결정하고 제어하는 강력한 도구다.
- **백엔드 비동기 프로그래밍**: 스케줄러 설계, 데이터 불일치 문제 해결, 효율적인 데이터 매칭, 비동기 작업 간격 유지, 부하 관리, 요청 크기 제한, 병렬성 제어와 같은 현실적인 백엔드 과제를 리스트 프로세싱으로 구조적으로 다룰 수 있다.
- **리스트 프로세싱 패턴화**: 변형-누적, 중첩-변형, 반복자-효과, 필터-중단, 무한-중단, 분할-평탄, 변형-평탄, 결합-누적, 해시-매치 등의 패턴을 익히고 활용하면 코드의 동작을 예측하고 설명하기가 쉬워지고 단위별 테스트와 재사용이 가능해진다.
- 리스트 프로세싱은 복잡한 문제를 간단하고 선언적으로 표현할 수 있는 강력한 도구이며, 이를 패턴화하고 재조합하여 응용력을 높이면 생산성을 극대화하는 개발 환경을 구축할 수 있다.

## 다른 챕터와의 관계

- **2·11장**: "명령형 문장 → 리스트 프로세싱" 대응이 이 장의 패턴 9종으로 실전 완성됐다.
- **4장**: es5의 `_group_by`/`_count_by`가 이 장의 해시-매치 패턴(`groupBy`/`indexBy`)으로 재등장해 O(1) 매칭 최적화에 쓰인다.
- **8장**: take·takeWhile·takeUntilInclusive가 "필터-중단"·"무한-중단" 패턴의 핵심 재료다.
- **14·15장**: 백엔드 스케줄러의 동시성 제어(`concurrent`)와 에러 전파 설계가 Part 4의 원칙 위에 서 있다.
- **17장**: 이 장의 함수형 로직이 구조(OOP)와 결합하는 설계로 이어진다.
