# Chapter 4: Asynchronous Programming (비동기 프로그래밍)

## 핵심 질문

Promise를 단순히 소비하는 수준을 넘어 값으로 다루고, 반복자 패턴과 결합하여 비동기 실행 순서를 제어하려면 어떻게 해야 할까? 지연 평가와 리스트 프로세싱이 비동기 프로그래밍에서 왜 강력한 도구가 되며, 타입 시스템을 활용하면 동기와 비동기를 어떻게 일관된 방식으로 다룰 수 있을까?

---

비동기 프로그래밍은 특정 작업이 완료될 때까지 기다리지 않고 다른 작업을 계속 수행하는 프로그래밍 방식이다. 따라서 프로그램이 동시에 여러 작업을 수행할 수 있어 효율성을 높인다. 자바스크립트를 사용하는 환경에서는 주로 IO 작업에 활용된다. 브라우저는 비동기 패러다임을 기반으로 긴 IO 작업 동안에도 UI의 반응성을 유지한다. 프런트엔드 개발에서는 주로 API 통신과 애니메이션 시점 핸들링 등에 사용되며 백엔드 프로그래밍에서는 파일 시스템, 데이터베이스 및 쿼리 핸들링, 각종 네트워크 통신 등에 사용된다.

자바스크립트가 실행되는 환경에서는 대부분 싱글 스레드 기반의 비동기 IO를 통해 프로그램의 동시 실행을 제어한다. 예를 들어 Node.js는 싱글 스레드로 동작하지만 비동기 IO를 통해 외부 자원에게 병렬 작업을 맡기고 실행 순서를 제어한다. 따라서 프로그래머는 비동기적으로 일어나는 작업의 실행 순서를 정확하게 제어할 수 있어야 한다.

이 장에서는 Promise를 값으로 다루고 반복자 패턴과 조합하여 비동기 실행 순서를 제어하는 방법을 배운다. 또한 비동기와 동시성 제어에 강점을 보이는 함수형 패러다임과 타입 시스템을 적용하여 비동기 프로그래밍의 안전성과 가독성을 높이는 방법을 살펴본다.

---

## 1. 값으로 다루는 비동기

Promise는 비동기 작업의 결과를 값으로 다룰 수 있게 하는 객체이자 규약이다. 반복자 패턴의 구현체인 이터레이터가 그랬던 것처럼 많은 프로그래밍 언어들이 Promise와 동일한 기능을 제공한다. 한편으로 Promise는 비동기 상황을 타입 수준에서 다룰 수 있게 한다. 타입 시스템을 통해 컴파일 타임에 안전한 합성이 가능해지고 런타임에서는 다양한 비동기 상황을 보다 효과적으로 제어할 수 있다. 이러한 Promise를 반복자 패턴과 조합하면 매우 강력한 비동기 프로그래밍 모델을 만들 수 있다.

### 1.1 Promise

Promise는 비동기 작업의 성공 또는 실패를 처리하는 데 사용하는 객체다. 비동기를 다루는 표준화된 값과 규약은 개발자와 언어가 이를 정확하고 안전하게 다룰 수 있게 한다. Promise는 비동기 작업의 완료 여부와 관계없이 즉시 객체를 생성하여 값으로 다룰 수 있게 하고 비동기 작업의 결과가 필요한 시점에 꺼내보거나 에러를 처리할 수 있도록 한다.

Promise는 생성 즉시 대기(*Pending*) 상태로 시작하고 작업이 성공하면 이행(*Fulfilled*) 상태로, 실패하면 거부(*Rejected*) 상태로 전환된다. Promise는 여러 Promise를 조합(합성)하여 순차적으로 실행하거나 동시 실행하도록 제어할 수 있으며 async/await 등과 함께 동작하여 비동기 로직을 간단하게 표현할 수도 있다.

#### Promise 연관 기능과 도입 시점

Promise는 ES6이 도입되기 이전 2010~2013년 사이부터 많은 개발자들이 서드파티에서 직접 구현하여 미리 사용하고 있었다. 대표적인 라이브러리로는 Q, Bluebird, When.js 등이 있었으며 보다 쉽게 비동기 프로그래밍을 할 수 있도록 도와주었다. 그러다 2015년 ES6에서 Promise가 표준화되면서 자바스크립트에서 비동기 프로그래밍을 위한 일관된 방법이 제공되었다.

Promise와 관련된 기술과 도입 시점은 다음과 같다.

**ECMAScript 2015(ES6)**
- `Promise`: 비동기 작업의 성공 또는 실패를 처리하는 객체
- `Promise.all`: 병렬로 실행된 모든 Promise가 완료될 때까지 기다린 후 결과를 배열로 반환
- `Promise.race`: 병렬로 실행된 여러 Promise 중 가장 먼저 완료된 Promise의 결과나 에러를 반환
- `Promise.resolve`: 기존 값을 Promise로 변환하거나 이미 Promise인 값을 그대로 반환
- `Promise.reject`: 실패한 이유와 함께 거부된 Promise를 반환

**ECMAScript 2017(ES8)**
- `async/await`: 비동기 함수를 정의하고 Promise의 결과를 기다릴 수 있는 구문

**ECMAScript 2018(ES9)**
- `Promise.finally`: Promise가 완료되면 (성공 또는 실패와 관계없이) 항상 실행되는 콜백을 지정
- `for await...of`: 비동기 이터러블 객체를 반복할 수 있는 구문
- `AsyncIterator`: 비동기 이터레이션을 지원하는 인터페이스
- `AsyncGenerator`: 비동기 작업을 수행하면서 값을 생성할 수 있는 비동기 제너레이터 함수. `async`와 `function*` 키워드를 함께 사용하여 정의

**ECMAScript 2020(ES11)**
- `Promise.allSettled`: 여러 Promise를 병렬로 실행하고 모든 Promise가 완료될 때까지 기다린 후 각 Promise의 결과(성공 또는 실패)를 객체 형태로 반환

**ECMAScript 2021(ES12)**
- `Promise.any`: 여러 Promise 중 가장 먼저 이행된 Promise의 값을 반환. 모든 Promise가 거부된 경우 거부된 모든 이유를 포함하는 단일 에러를 반환

**ECMAScript 2022(ES13)**
- `Array.fromAsync`: 비동기 이터러블을 처리하여 배열을 생성

이처럼 Promise를 포함한 비동기 프로그래밍 기술이 ECMAScript에서 지속적으로 발전되고 보강되는 이유는 이것이 자바스크립트에서의 IO를 다루는 핵심 기술이기 때문이다.

#### Promise를 반환하는 delay 함수

`delay` 함수는 `time`만큼 대기한 후 `value`로 받은 값을 반환하는 Promise를 생성하여 즉시 반환하는 함수다.

```typescript
function delay<T>(time: number, value: T): Promise<T> {
  return new Promise((resolve) => setTimeout(resolve, time, value));
}
```

다음은 `delay` 함수의 반환값인 Promise를 다루는 예제다.

```typescript
// then으로 합성
function test() {
  console.time('test');
  delay(1000, "Hello, world!").then((result) => { // [result: string]
    console.log(result); // 1초 후에 "Hello, world!" 출력
    return delay(2000, 40);
  }).then((result) => { // [result: number]
    console.log(result); // 2초 후에 40 출력
    console.timeEnd('test'); // 약 3000ms
  });
}
```

```typescript
// async/await (ES8)
async function test2() {
  console.time('test2');
  const result1 = await delay(1000, "Hello, world!"); // [result1: string]
  console.log(result1); // 1초 후에 "Hello, world!" 출력
  const result2 = await delay(2000, 40); // [result2: number]
  console.log(result2); // 2초 후에 40 출력
  console.timeEnd('test2'); // 약 3000ms
}
```

### 1.2 new Promise를 직접 사용해 본 적 있는가

면접에서 저자는 종종 다음과 같은 질문을 던진다.

- 실제 업무에서 `new Promise()`를 직접 사용해 본 경험이 있나요?
- Promise 인스턴스를 인자로 받아 처리하는 함수를 구현해 본 적이 있나요?
- `Promise.all`이나 `Promise.race`를 사용해 본 경험은 있나요?

요즘 들어 `new Promise`를 직접 작성하는 일이 많지는 않다. 최근에는 Web API와 Node.js를 비롯한 대부분의 서드파티 라이브러리에서 이미 Promise 기반의 인터페이스를 제공하고 있기 때문이다. 하지만 `Promise.all`이나 `Promise.race`와 달리 기존에 제공되지 않는 고유한 방식의 병렬 실행 제어 함수를 구현해야 한다면 `new Promise()`를 직접 생성하고 제어하는 로직이 필요할 수 있다. 이는 단순히 주어진 라이브러리나 헬퍼 함수를 활용하는 것을 넘어 비동기 프로그래밍에서 발생하는 특정 문제를 자체 알고리즘으로 풀어내는 경험을 의미한다.

### 1.3 Promise.race

`Promise.race`는 병렬로 실행된 여러 Promise 중 가장 먼저 완료된 Promise의 결과나 에러를 반환한다.

```typescript
const promise1 = new Promise((resolve) => setTimeout(resolve, 500, 'one'));
const promise2 = new Promise((resolve) => setTimeout(resolve, 100, 'two'));

await Promise.race([promise1, promise2]).then((value) => {
  console.log(value); // "two"가 출력된다. (먼저 완료된 Promise)
});
```

### 1.4 IO 작업에 타임아웃 설정하기

친구 목록을 가져오는 `/friends` API의 응답이 5초 이상 지연되었을 때 '현재 네트워크 환경이 좋지 않습니다.'와 같은 메시지를 출력하고자 한다면 `Promise.race`를 활용하면 좋다.

```typescript
function getRandomValue<T>(a: T, b: T): T {
  const randomIndex = Math.floor(Math.random() * 2);
  return randomIndex === 0 ? a : b;
}

type User = {
  name: string;
}

function getFriends(): Promise<User[]> {
  return delay(
    getRandomValue(60, 6_000), // 0.06초 or 6초
    [{ name: 'Marty' }, { name: 'Michael' }, { name: 'Sarah' }]
  );
}

const result = await Promise.race([
  getFriends(),
  delay(5000, 'timeout')
]);

if (result === 'timeout') {
  console.log("현재 네트워크 환경이 좋지 않습니다.");
} else {
  const friends = result as User[];
  console.log("친구 목록 렌더링:", friends.map(({ name }) => `<li>${name}</li>`));
}
```

> **참고**: AbortController는 비동기 작업을 취소할 수 있도록 도와주는 웹 API로 주로 fetch 요청에 제한 시간을 설정하거나 중단하는 데 사용된다.

### 1.5 응답 속도에 따라 다른 전략으로 UI 렌더링하기

채팅방에 '친구 초대하기'라는 버튼이 있고 버튼을 누를 때 친구 목록을 가져오는 창을 렌더링한다고 가정해 보자. 만일 `/friends` API의 응답이 100ms 내로 완료되면 즉시 친구 목록 창을 렌더링하고 그보다 오래 걸리면 로딩 표시를 띄운 후 응답이 완료되었을 때 렌더링하도록 만들고자 한다.

```typescript
function toggleLoadingIndicator(show: boolean): void {
  if (show) {
    console.log("append loading...");
  } else {
    console.log("remove loading...");
  }
}

async function renderFriendsPicker(): Promise<void> {
  const friendsPromise = getFriends();
  const result = await Promise.race([
    friendsPromise,
    delay(100, 'isSlow')
  ]);

  if (result === 'isSlow') {
    toggleLoadingIndicator(true);
    await friendsPromise;
    toggleLoadingIndicator(false);
  }

  const friends = await friendsPromise;
  console.log("친구 목록 렌더링:",
    friends.map(({ name }) => `<li>${name}</li>`));
}
```

이처럼 Promise를 변수에 담거나 `Promise.race` 같은 함수에 전달하거나 원할 때 꺼내서 사용하는 등 원하는 실행 타이밍에 맞게 대기를 거는 방식으로 Promise를 값으로 다룰 수 있다.

### 1.6 Promise.all

`Promise.all`은 주어진 모든 Promise가 이행될 때까지 기다렸다가 모든 결과를 배열로 반환하는 함수다. 만약 주어진 Promise 중 하나라도 거부(*Rejected*)되면 `Promise.all`은 즉시 거부되고 거부 이유를 반환한다.

```typescript
type File = {
  name: string;
  body: string;
  size: number;
};

function getFile(name: string, size = 1000): Promise<File> {
  return delay(size, { name, body: '...', size });
}

const files = await Promise.all([
  getFile('img.png', 500),
  getFile('book.pdf', 1000),
  getFile('index.html', 1500)
]);

console.log(files);
// 약 1,500ms 뒤:
// [
//   { name: 'img.png', body: '...', size: 500 },
//   { name: 'book.pdf', body: '...', size: 1000 },
//   { name: 'index.html', body: '...', size: 1500 }
// ]
```

`getFile`이 세 번 호출될 때 총 실행 시간은 3000ms 정도지만 병렬로 실행되기 때문에 가장 오래 걸리는 Promise의 실행 시간인 1500ms 후에 결과가 완성된다.

거부된 Promise가 포함된 경우는 다음과 같다.

```typescript
try {
  const files = await Promise.all([
    getFile('img.png'),
    getFile('book.pdf'),
    getFile('index.html'),
    delay(500, Promise.reject('파일 다운로드 실패'))
  ]);
  console.log(files); // 이 줄은 실행되지 않는다.
} catch (error) {
  // 약 500ms 뒤
  console.error(error); // '파일 다운로드 실패'
}
```

### 1.7 Promise.allSettled

`Promise.allSettled`는 주어진 모든 Promise가 완료될 때까지 기다린 후 각 Promise의 성공 결과나 실패 결과를 객체로 담아 반환한다.

```typescript
const files = await Promise.allSettled([
  getFile('img.png'),
  getFile('book.pdf'),
  getFile('index.html'),
  Promise.reject('파일 다운로드 실패')
]);

console.log(files);
// 약 1000ms 뒤:
// [
//   { status: 'fulfilled', value: { name: 'img.png', body: '...', size: 1000 } },
//   { status: 'fulfilled', value: { name: 'book.pdf', body: '...', size: 1000 } },
//   { status: 'fulfilled', value: { name: 'index.html', body: '...', size: 1000 } },
//   { status: 'rejected', reason: '파일 다운로드 실패' }
// ]
```

오해하지 말아야 할 것은 `Promise.all`의 상황이 문제라서 이를 해결하기 위해 `Promise.allSettled`가 나온 것이 아니며 용도가 다르다는 점이다. 에러가 전파되는 것을 원할 때는 여전히 `Promise.all`을 사용하는 것이 맞다.

ES11 이전에는 `settlePromise` 같은 간단한 함수를 만들어 `map`과 함께 사용하는 식으로 대체할 수 있었다.

```typescript
const settlePromise = <T>(promise: Promise<T>) =>
  promise
    .then(value => ({ status: 'fulfilled', value }))
    .catch(reason => ({ status: 'rejected', reason }));

const files = await Promise.all([
  getFile('img.png'),
  getFile('book.pdf'),
  getFile('index.html'),
  Promise.reject('파일 다운로드 실패')
].map(settlePromise));
```

이 코드는 Promise를 함수형 고차 함수와 함께 값으로 다루는 예다. `map`을 사용하여 각 Promise에 `settlePromise` 함수를 적용하고 `Promise.all`을 사용하여 모든 Promise가 완료될 때까지 기다리면 `Promise.allSettled`와 동일한 결과를 반환한다.

### 1.8 Promise.any

`Promise.race`가 가장 먼저 완료된 Promise를 이행되든 거부되든 상관없이 즉시 그 결과나 에러를 반환한다면 `Promise.any`는 여러 Promise 중 가장 먼저 이행된 Promise의 값을 반환한다. 단 모든 Promise가 거부된 경우에는 거부된 모든 이유를 포함하는 단일 에러를 반환한다.

```typescript
const file = await Promise.any([
  getFile('img.png', 1500),
  getFile('book.pdf', 700),
  getFile('index.html', 900),
  delay(100, Promise.reject('파일 다운로드 실패'))
]);

console.log(file);
// 약 700ms 후
// { name: 'book.pdf', body: '...', size: 700 }
```

---

## 2. 지연성으로 다루는 비동기

이 절에서는 `Promise.all`이나 `Promise.race`처럼 또 다른 비동기 상황을 다루는 재사용 가능한 함수를 만들면서 Promise를 값으로 다루는 사고를 좀 더 확장하고자 한다. 또한 반복자 패턴, 지연 평가, 리스트 프로세싱과 함께 Promise를 다루는 방법과 그 이유에 대해 탐구해 본다.

### 2.1 Promise 실행을 지연하려면

`Promise.all`에서는 모든 Promise를 동시에 병렬로 실행한다. 그런데 만약 부하를 조절하고 싶다면 어떻게 해야 할까? 6개의 병렬적인 비동기 작업을 한 번에 3개씩 실행되도록 하는 함수를 만들고 싶다고 하자.

```typescript
// 첫 번째 시도 - 문제가 있는 코드
async function executeWithLimit<T>(
  promises: Promise<T>[],
  limit: number
): Promise<T[]> {
  const result1 = await Promise.all([promises[0], promises[1], promises[2]]);
  const result2 = await Promise.all([promises[3], promises[4], promises[5]]);
  return [...result1, ...result2];
}
```

이 코드는 2000ms 정도 소요될 것이라는 기대와 달리 약 1000ms 만에 모든 Promise가 완료된다. **Promise 객체는 생성되는 즉시 실행되기 때문이다.** 즉 `getFile` 함수가 호출되는 순간 이미 Promise가 시작된다. `Promise.all`은 이미 실행된 모든 Promise를 받아 모두 완료될 때까지 대기했다가 결과를 반환하는 함수일 뿐 Promise의 시작 자체를 제어하는 함수는 아니다.

이를 해결하려면 아직 Promise들이 실행되지 않은 상태에서 그룹을 나누고 각 그룹이 순차적으로 실행되도록 해야 한다. 방법은 간단하다. `() =>`와 `()`를 추가하면 된다.

```typescript
async function executeWithLimit<T>(
  fs: (() => Promise<T>)[],
  limit: number
): Promise<T[]> {
  const result1 = await Promise.all([fs[0](), fs[1](), fs[2]]);
  const result2 = await Promise.all([fs[3](), fs[4](), fs[5]]);
  return [...result1, ...result2];
}

const files: File[] = await executeWithLimit([
  () => getFile('1-img.png'),
  () => getFile('2-book.pdf'),
  () => getFile('3-index.html'),
  () => getFile('4-img2.png'),
  () => getFile('5-book.pdf'),
  () => getFile('6-index.html'),
], 3);
// 즉시 3개 출력: 1-img.png 시작, 2-book.pdf 시작, 3-index.html 시작
// 약 1000ms 뒤, 아래 3개 출력: 4-img2.png 시작, 5-book.pdf 시작, 6-index.html 시작
// 약 2000ms 뒤: 모든 파일 완료
```

Promise를 함수로 감싸서 필요할 때 실행되도록 실행을 지연한 것이다.

### 2.2 ChatGPT가 명령형으로 구현한 동시성 핸들링 함수

ChatGPT에게 `executeWithLimit` 구현을 맡기면 다음과 같은 명령형 코드를 생성한다.

```typescript
async function executeWithLimit<T>(
  fs: (() => Promise<T>)[],
  limit: number
): Promise<T[]> {
  const results: T[] = [];
  for (let i = 0; i < fs.length; i += limit) {
    const batchPromises: Promise<T>[] = [];
    for (let j = 0; j < limit && (i + j) < fs.length; j++) {
      batchPromises.push(fs[i + j]());
    }
    const batchResults = await Promise.all(batchPromises);
    results.push(...batchResults);
  }
  return results;
}
```

이 코드는 잘 동작하지만 읽기가 상당히 어렵다. 3개씩 안전하게 그룹화하기 위한 외부 `for`문과 내부 `for`문의 조건들이 복잡하다.

### 2.3 함수형으로 구현한 동시성 핸들링 함수

`executeWithLimit` 함수의 구현을 리스트 프로세싱 관점으로 계획하면 다음과 같다.

- `[() => P, () => P, () => P, () => P, ...]`
- `[[() => P, () => P, () => P], ...]` - 3개씩 그룹화
- `[[P, P, P], ...]` - 함수 실행
- `[P<[T, T, T]>, ...]` - 3개씩 대기하도록 `Promise.all`로 감싸기
- `P<[[T, T, T], ...]>` - `Promise.all`들의 결과 꺼내기
- `P<[T, T, T, T, ...]>` - 1차원 배열로 평탄화

```typescript
async function fromAsync<T>(
  iterable: Iterable<Promise<T>> | AsyncIterable<T>
): Promise<T[]> {
  const arr: T[] = [];
  for await (const a of iterable) {
    arr.push(a);
  }
  return arr;
}

const executeWithLimit = <T>(fs: (() => Promise<T>)[], limit: number): Promise<T[]> =>
  fx(fs)
    .map(f => f())              // [P<T>, P<T>, P<T>, ...] - 비동기 함수 지연 실행
    .chunk(limit)               // [[P<T>, P<T>, P<T>], ...] - 3개씩 그룹화
    .map(ps => Promise.all(ps)) // [P<[T, T, T]>, ...] - 3개씩 대기
    .to(fromAsync)              // P<[[T, T, T], ...]> - 결과 꺼내기
    .then(arr => arr.flat());   // P<[T, T, T, T, ...]> - 평탄화
```

위 계획에서는 '그룹화 후 함수 실행' 순서였지만 코드는 `map(f => f())`를 먼저 두었다. `map`과 `chunk`가 모두 지연 평가되므로 순서를 바꿔도 실제 실행 시점은 동일하고(소비 시점에 청크 단위로 함수가 실행된다) 이 순서가 더 간결하다 — 원서도 계획 순서대로 구현한 버전([코드 4-18])을 이 형태([코드 4-19])로 다듬는다.

이 코드에서는 `i++`나 `j++` 같은 상태 변화, `j < limit && (i + j) < fs.length` 같은 조건절이 없다. 또한 `push(fs[i + j]())`나 `push(...batchResults)` 같은 명령형 표현 대신 `fromAsync`, `arr.flat()` 같은 선언적 표현을 사용한다.

### 2.4 효과적인 비동기 핸들링으로 가는 계단 - 지연성

`executeWithLimit` 함수 구현의 핵심은 지연성이다. 지연성은 효과적인 비동기 핸들링으로 나아가는 데 중요한 징검다리 역할을 한다.

- `executeWithLimit` 함수는 Promise 실행을 지연한 함수를 인자로 받는다.
- `map(f => f())`는 모든 함수를 실행하는 것처럼 보이지만 이때 `map`은 Array의 `map`과 달리 지연 평가되는 `map`이다.
- 따라서 `fromAsync`에서 하나의 요소를 꺼낼 때 해당 청크 안에 있는 함수들만 실행하고 그 다음 `map`에서 `Promise.all`로 감싼다.
- `fromAsync`는 이 결과를 `for await...of`로 꺼내므로 `Promise.all`의 결과를 대기 후 꺼낸다.

지연 평가는 단순히 성능 개선이나 최적화를 위한 도구에 그치지 않는다. 이터레이터와 전달받은 일급 함수를 원하는 시점에 평가하는 코드 패턴을 통해 로직을 재사용 가능한 형태로 만들 수 있다.

---

## 3. 타입으로 다루는 비동기

이 절에서는 타입, 인터페이스, 규약을 기반으로 비동기를 다루는 패턴을 알아본다. AsyncIterator, AsyncIterable이라는 타입이자 규약 그리고 이를 다루는 AsyncGenerator, 비동기 고차 함수 그리고 그것을 묶는 비동기 리스트 프로세싱 클래스의 조합과 설계를 통해 타입 시스템에 기반한 비동기 핸들링 패턴을 다룬다.

### 3.1 AsyncIterator, AsyncIterable, AsyncGenerator 프로토콜

자바스크립트는 AsyncIterator, AsyncIterable, AsyncGenerator와 같은 프로토콜을 제공하여 비동기 작업의 순차적 처리를 지원한다.

#### AsyncIterator, AsyncIterable 인터페이스

```typescript
interface IteratorYieldResult<T> {
  done?: false;
  value: T;
}

interface IteratorReturnResult {
  done: true;
  value: undefined;
}

interface AsyncIterator<T> {
  next(): Promise<IteratorYieldResult<T> | IteratorReturnResult>;
}

interface AsyncIterable<T> {
  [Symbol.asyncIterator](): AsyncIterator<T>;
}

interface AsyncIterableIterator<T> extends AsyncIterator<T> {
  [Symbol.asyncIterator](): AsyncIterableIterator<T>;
}
```

- `IteratorYieldResult<T>`: `done`이 `false`인 경우와 `value`가 T 타입인 값을 나타낸다. AsyncIterator가 아직 완료되지 않았음을 의미한다.
- `IteratorReturnResult`: `done`이 `true`이고 `value`가 `undefined`인 값을 나타낸다. AsyncIterator가 완료되었음을 의미한다.
- `AsyncIterator<T>`: Promise를 반환하는 `next` 메서드를 가진 인터페이스다.
- `AsyncIterable<T>`: `AsyncIterator<T>`를 반환하는 `Symbol.asyncIterator` 메서드를 가진 인터페이스다.
- `AsyncIterableIterator<T>`: `AsyncIterator<T>`를 상속받아 `Symbol.asyncIterator` 메서드를 추가로 구현한 인터페이스다.

#### AsyncGenerator 기본 문법

```typescript
async function* stringsAsyncTest(): AsyncIterableIterator<string> {
  yield delay(1000, 'a');
  const b = await delay(500, 'b') + 'c';
  yield b;
}

async function test() {
  const asyncIterator: AsyncIterableIterator<string> = stringsAsyncTest();
  const result1 = await asyncIterator.next();
  console.log(result1.value); // 1000ms 후: a
  const result2 = await asyncIterator.next();
  console.log(result2.value); // 이후 500ms 후: bc
  const { done } = await asyncIterator.next();
  console.log(done); // true
}
```

#### toAsync 함수

`toAsync` 함수는 동기적인 Iterable 또는 Promise가 포함된 Iterable을 받아 비동기적으로 처리할 수 있는 AsyncIterable로 변환한다.

```typescript
// AsyncIterator 직접 구현 방식
function toAsync<T>(iterable: Iterable<T | Promise<T>>): AsyncIterable<Awaited<T>> {
  return {
    [Symbol.asyncIterator](): AsyncIterator<Awaited<T>> {
      const iterator = iterable[Symbol.iterator]();
      return {
        async next() {
          const { done, value } = iterator.next();
          return done ? { done, value } : { done, value: await value };
        }
      };
    }
  };
}
```

```typescript
// AsyncGenerator를 사용하는 방식 (더 간결)
async function* toAsync<T>(
  iterable: Iterable<T | Promise<T>>
): AsyncIterableIterator<Awaited<T>> {
  for await (const value of iterable) {
    yield value;
  }
}
```

### 3.2 AsyncIterable을 다루는 고차 함수

#### AsyncIterator를 직접 구현한 mapAsync 함수

`mapSync` 함수는 Iterable을 다루고 `mapAsync` 함수는 AsyncIterable을 다룬다.

```typescript
function mapAsync<A, B>(
  f: (a: A) => B,
  asyncIterable: AsyncIterable<A>
): AsyncIterableIterator<Awaited<B>> {
  const asyncIterator = asyncIterable[Symbol.asyncIterator]();
  return {
    async next() {
      const { done, value } = await asyncIterator.next();
      return done
        ? { done, value }
        : { done, value: await f(value) };
    },
    [Symbol.asyncIterator]() {
      return this;
    }
  };
}
```

사실상 `mapSync`와 `mapAsync` 함수는 코드와 값이 흐르는 방식이 완전히 동일하다. 다만 `mapAsync`는 비동기 이터러블을 다룰 수 있도록 설계되었다.

AsyncGenerator로 구현하면 더 간결하다.

```typescript
async function* mapAsync<A, B>(
  f: (a: A) => B,
  asyncIterable: AsyncIterable<A>
): AsyncIterableIterator<Awaited<B>> {
  for await (const value of asyncIterable) {
    yield f(value);
  }
}
```

> **참고**: 처음부터 `mapAsync`를 제너레이터로만 구현할 수도 있지만 제너레이터를 작성할 때는 항상 코드가 이터레이터로 변환되는 것, `yield`가 `next()`의 `value`가 되는 것, `return;`이 `{ done: true }`가 되는 것을 떠올리며 작성할 수 있어야 한다.

#### AsyncGenerator로 만든 filterAsync 함수

```typescript
async function* filterAsync<A>(
  f: (a: A) => boolean | Promise<boolean>,
  asyncIterable: AsyncIterable<A>
): AsyncIterableIterator<A> {
  for await (const value of asyncIterable) {
    if (await f(value)) {
      yield value;
    }
  }
}

for await (const a of filterAsync(a => a % 2 === 1, toAsync([1, 2, 3]))) {
  console.log(a);
}
// 1
// 3
```

### 3.3 동기와 비동기를 동시에 지원하는 함수로 만드는 규약 - toAsync

`toAsync` 함수는 일반 Iterable을 AsyncIterable로 변환하여 런타임에서 값을 처리할 뿐만 아니라 컴파일 타임에 타입이 변경되는 것을 선언한다. `toAsync` 함수를 실행함으로써 앞으로 비동기적으로 값을 다룰 것임을 컴파일 타임에 선언하는 효과가 있다.

#### 동기와 비동기를 모두 지원하는 map 함수

타입스크립트에서는 인자 타입에 따라 함수 오버로드를 통해 하나의 함수로 두 가지 이상의 역할을 수행할 수 있다.

```typescript
function isIterable<T = unknown>(a: Iterable<T> | unknown): a is Iterable<T> {
  return typeof a?.[Symbol.iterator] === "function";
}

function map<A, B>(
  f: (a: A) => B,
  iterable: Iterable<A>
): IterableIterator<B>;
function map<A, B>(
  f: (a: A) => B,
  asyncIterable: AsyncIterable<A>
): AsyncIterableIterator<Awaited<B>>;
function map<A, B>(
  f: (a: A) => B,
  iterable: Iterable<A> | AsyncIterable<A>
): IterableIterator<B> | AsyncIterableIterator<Awaited<B>> {
  return isIterable(iterable)
    ? mapSync(f, iterable)
    : mapAsync(f, iterable);
}
```

`map` 함수는 `mapSync`와 `mapAsync`의 시그니처를 함수 오버로드로 적용하고 하나의 함수로 통합하여 구현한다. `isIterable`로 타입을 검사하여 동기면 `mapSync`, 비동기면 `mapAsync`로 분기한다.

오버로드된 시그니처가 컴파일 타임에 어떻게 추론되는지 대표 사례로 확인해 보자(원서 [코드 4-30]은 6가지 사례를 다룬다).

```typescript
// 컴파일 타임 타입 추론 (원서 [코드 4-30]에서 발췌)
const iter1: IterableIterator<string> = map(
  (a: number) => a.toFixed(),
  [1, 2]
); // 동기 이터러블 → mapSync로 추론

const iter2: IterableIterator<Promise<string>> = map(
  (a: number) => Promise.resolve(a.toFixed()),
  [1, 2]
); // 동기 이터러블 + Promise 반환 보조 함수 → Promise가 풀리지 않은 채 요소 타입이 된다

const iter3: AsyncIterableIterator<string> = map(
  (a: number) => Promise.resolve(a.toFixed()),
  toAsync([1, 2])
); // toAsync를 거치면 mapAsync로 동작 → Awaited<B>가 적용되어 풀린 string으로 추론
```

동기 이터러블에서는 보조 함수가 Promise를 반환해도 요소 타입이 `Promise<string>` 그대로지만, `toAsync`로 비동기 이터러블임을 선언하면 `Awaited<B>`가 적용되어 풀린 타입으로 추론된다. 타입 시스템이 함수의 동작이 동기일지 비동기일지를 결정하고 이를 컴파일 타임에 보증하는 것이다.

```typescript
// 동기적 배열 처리: mapSync
console.log([...map(a => a * 10, [1, 2])]);
// [10, 20]

// 비동기 이터러블 처리: mapAsync
for await (const a of map(a => delay(100, a * 10), toAsync([1, 2]))) {
  console.log(a);
}
// 100ms 뒤: 10
// 다시 100ms 뒤: 20
```

#### 동기와 비동기를 모두 지원하는 filter 함수

`map`과 동일한 패턴으로 `filter` 함수도 구현한다. 특히 동기 이터러블에 비동기 조건 함수를 사용하면 타입 에러가 발생하는데, 이는 의도한 결과다. `Promise.resolve(true)`와 `Promise.resolve(false)` 모두 객체이고 객체는 참 같은 값(*Truthy*)으로 평가되므로 결과를 꺼내보지 않고는 제대로 평가할 수 없기 때문이다.

```typescript
function filter<A>(
  f: (a: A) => boolean,
  iterable: Iterable<A>
): IterableIterator<A>;
function filter<A>(
  f: (a: A) => boolean | Promise<boolean>,
  asyncIterable: AsyncIterable<A>
): AsyncIterableIterator<A>;
function filter<A>(
  f: (a: A) => boolean | Promise<boolean>,
  iterable: Iterable<A> | AsyncIterable<A>
): IterableIterator<A> | AsyncIterableIterator<A> {
  return isIterable(iterable)
    ? filterSync(f as (a: A) => boolean, iterable)
    : filterAsync(f, iterable);
}
```

### 3.4 타입 시스템 + 비동기 함수형 함수 + 클래스

타입 시스템과 비동기 함수형 함수, 클래스를 결합하면 비동기 작업을 더욱 구조화하여 일관성 있게 관리할 수 있다.

#### FxIterable과 FxAsyncIterable

`toAsync` 메서드를 통해 `FxIterable` 타입을 `FxAsyncIterable`로 변환하며 이어주는데 같은 함수로 같은 문제를 해결하지만 약간 다르게 표현한다.

```typescript
function fx<A>(iterable: Iterable<A>): FxIterable<A>;
function fx<A>(asyncIterable: AsyncIterable<A>): FxAsyncIterable<A>;
function fx<A>(
  iterable: Iterable<A> | AsyncIterable<A>
): FxIterable<A> | FxAsyncIterable<A> {
  return isIterable(iterable)
    ? new FxIterable(iterable)
    : new FxAsyncIterable(iterable);
}

class FxIterable<A> {
  constructor(private iterable: Iterable<A>) {}

  [Symbol.iterator]() {
    return this.iterable[Symbol.iterator]();
  }

  map<B>(f: (a: A) => B) {
    return fx(map(f, this));
  }

  filter(f: (a: A) => boolean) {
    return fx(filter(f, this));
  }

  toArray() {
    return [...this];
  }

  toAsync() {
    return fx(toAsync(this));
  }
}

class FxAsyncIterable<A> {
  constructor(private asyncIterable: AsyncIterable<A>) {}

  [Symbol.asyncIterator]() {
    return this.asyncIterable[Symbol.asyncIterator]();
  }

  map<B>(f: (a: A) => B) {
    return fx(map(f, this));
  }

  filter(f: (a: A) => boolean | Promise<boolean>) {
    return fx(filter(f, this));
  }

  toArray() {
    return fromAsync(this);
  }
}
```

원서 [코드 4-35]는 `implements Iterable<A>`/`implements AsyncIterable<A>`와 명시적 반환 타입을 붙여 작성한 버전으로, `implements`를 이용하면 인터페이스를 만족시키는 데 필요한 구현이 완료되었는지 컴파일 타임에 가이드를 받을 수 있다. 위 코드는 반환 타입 추론을 타입스크립트에게 위임하여 더 간결하게 쓴 버전(원서 [코드 4-36])이다.

```typescript
async function test() {
  // ① filterSync -> mapSync로 동작
  console.log(
    fx(naturals(4))
      .filter(isOdd)
      .map(a => a * 10)
      .toArray()
  );
  // [10, 30]

  // ② toAsync -> filterAsync -> mapAsync로 동작
  const iter2 = fx(naturals(4))
    .toAsync()
    .filter(a => delay(100, isOdd(a)))
    .map(a => a.toFixed(2));

  for await (const a of iter2) {
    console.log(a);
  }
  // 100ms 뒤: 1.00
  // 다시 200ms 뒤: 3.00

  // ③ filter -> toAsync -> mapAsync로 동작
  console.log(
    await fx(naturals(4))
      .filter(isOdd)
      .toAsync()
      .map(a => delay(100, a * 10))
      .toArray()
  );
  // 200ms 뒤: [10, 30]
}
```

`toAsync` 메서드는 `FxIterable`의 메서드 체인을 `FxAsyncIterable`의 메서드 체인으로 연결하여 동기와 비동기 작업을 자연스럽게 결합할 수 있게 한다.

#### 타입 시스템을 활용한 비동기 로직 검증

`toAsync`를 사용하지 않고 비동기 필터링을 시도하면 타입 오류가 발생한다.

```typescript
const iter2 = fx(naturals(4))
  .filter(a => delay(100, isOdd(a))) // 타입 오류 발생 (TS2322)
  .map(a => a.toFixed());
// TS2322: Type 'Promise<boolean>' is not assignable to type 'boolean'
```

ECMAScript는 Iterable과 AsyncIterable을 용도에 적합하게 구분하여 설계하였고 타입스크립트는 이 구조를 활용하여 강력한 타입 검사를 제공한다.

#### 동기와 비동기를 모두 지원하는 reduce 함수

`map`과 `filter`가 이터러블을 반환하는 함수라면 `reduce`는 최종 결과를 만들어 내는 함수다. `reduce`는 Iterable<A>를 받아 순회하면서 누적된 값을 합산해 Acc를 만들거나 AsyncIterable<A>를 받아 Promise<Acc>를 반환하는 함수다.

```typescript
function reduce<A, Acc>(
  f: (acc: Acc, a: A) => Acc, acc: Acc, iterable: Iterable<A>
): Acc;
function reduce<A, Acc>(
  f: (acc: Acc, a: A) => Acc | Promise<Acc>, acc: Acc, asyncIterable: AsyncIterable<A>
): Promise<Acc>;
function reduce<A, Acc>(
  f: any, acc: Acc, iterable: Iterable<A> | AsyncIterable<A>
): Acc | Promise<Acc> {
  return isIterable(iterable)
    ? reduceSync(f, acc, iterable)
    : reduceAsync(f, acc, iterable);
}
```

```typescript
// FxIterable/FxAsyncIterable에 reduce 적용
const result: number =
  fx(naturals(4))
    .filter(isOdd)
    .map(a => a * 10)
    .reduce((acc, a) => acc + a, 0);

const resultPromise: Promise<number> =
  fx(naturals(4))
    .filter(isOdd)
    .map(a => delay(100, a * 10))
    .toAsync()
    .reduce((acc, a) => acc + a, 0);

console.log(result, await resultPromise);
// 40 40
```

---

## 4. 비동기 에러 핸들링

비동기 프로그래밍에서 에러를 효과적으로 처리하는 것은 필수다. 비동기 로직의 특성상 에러가 발생했을 때 코드가 어디서 실행되고 있는지 명확하게 파악하기 어려울 수 있다. 특히 네트워크 요청, 파일 읽기/쓰기, 데이터베이스 연동과 같이 외부 시스템과 상호작용하는 작업은 에러 가능성이 높으므로 이를 효율적으로 핸들링하는 방법이 중요하다.

### 4.1 여러 이미지를 불러와서 높이 구하기

```typescript
function loadImage(url: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.src = url;
    image.onload = function() {
      resolve(image);
    };
    image.onerror = function() {
      reject(new Error(`load error: ${url}`));
    };
  });
}

async function calcTotalHeight(urls: string[]) {
  try {
    const totalHeight = await urls
      .map(async (url) => {
        const img = await loadImage(url);
        return img.height;
      })
      .reduce(
        async (a, b) => await a + await b,
        Promise.resolve(0)
      );
    return totalHeight;
  } catch (e) {
    console.error('Error:', e);
  }
}
```

이 코드는 마치 잘 동작하는 듯 보이지만 다음과 같은 문제가 있다.

- **불필요한 부하**: 에러가 발생해도 나머지 URL에 대해 이미지 다운로드를 모두 시도한다.
- **부수 효과**: 위 상황이 POST나 데이터베이스의 INSERT와 같은 API를 제어한다면 불필요한 요청으로 부수 효과가 발생하게 된다.

### 4.2 개선된 비동기 로직

```typescript
async function calcTotalHeight2(urls: string[]) {
  try {
    const totalHeight = await fx(urls)
      .toAsync()
      .map(loadImage)
      .map(img => img.height)
      .reduce((a, b) => a + b, 0);
    return totalHeight;
  } catch (e) {
    console.error('error:', e);
  }
}
```

이 코드는 첫 번째 URL에서 에러가 발생하면 나머지 URL 요청을 멈추고 즉시 에러를 처리한다. Promise와 AsyncIterator를 안전하게 제어하고 의도대로 정확하게 동작하면서도 가독성이 높다.

### 4.3 에러가 제대로 발생되도록 하는 것이 핵심

비동기 프로그래밍에서 가장 중요한 것은 단순히 에러를 핸들링하는 것이 아니라 에러가 제대로 발생되도록 설계하는 것이다.

```typescript
// 에러 핸들링을 내부에서 하지 않고 호출자에게 위임
const getTotalHeight = (urls: string[]) =>
  fx(toAsync(urls))
    .map(loadImage)
    .map(img => img.height)
    .reduce((a, b) => a + b, 0);

// 사용하는 곳에서 에러 핸들링
try {
  const height = await getTotalHeight(urls);
} catch (e) {
  console.error(e);
}

// 또는
async function myFunction(urls: string[]) {
  try {
    return await getTotalHeight(urls);
  } catch {
    return 0;
  }
}
```

이러한 접근 방식의 이점은 다음과 같다.

- **순수 함수 유지**: 에러를 발생시키고 호출자에게 위임하는 것이 바람직하다.
- **유연한 에러 처리**: 각 호출자가 자신에게 필요한 방식으로 에러를 핸들링할 수 있다.
- **에러를 감추지 않음**: 에러를 명확히 발생시키고 호출자에게 위임하면 문제를 조기에 탐지하고 적절히 대응할 수 있다.

### 4.4 안정적인 소프트웨어와 비동기 프로그래밍

에러가 제대로 발생되도록 설계하기 위한 원칙은 다음과 같다.

- **Promise, async/await, try/catch를 정확히 이해하고 활용하기**: 비동기 작업을 수행할 때 에러가 명확히 드러나도록 작성한다.
- **에러를 숨기지 않고 명확히 드러내기**: 에러를 감추기보다는 발생하도록 두고 이를 상위 레벨에서 처리하거나 로깅 도구를 통해 모니터링한다.
- **순수 함수는 에러를 발생시키도록 설계**: 순수 함수 내부에서 에러를 처리하려고 시도하면 함수의 목적이 흐려질 수 있다.
- **제너레이터/이터레이터/이터러블을 활용한 선언적 프로그래밍**: 비동기 이터러블을 통해 에러 발생 시점을 제어하고 에러가 전파되는 흐름을 선언적으로 표현할 수 있다.
- **에러 핸들링 코드는 부수 효과 코드 근처에 작성**: 네트워크 요청, 파일 입출력 등 부수 효과를 발생시키는 코드 근처에서 에러를 처리해야 원인과 해결 방안을 명확히 할 수 있다.

---

## 요약

- **비동기 프로그래밍의 중요성**: 비동기 프로그래밍은 현대 소프트웨어 개발에서 필수적인 기술이다. 비동기 처리를 통해 애플리케이션의 성능과 응답성을 높일 수 있으며 특히 IO 작업이나 네트워크 요청과 같은 시간 소모적인 작업에서 큰 이점을 제공한다.
- **값으로 다루는 비동기**: Promise는 단순한 비동기 작업의 결과뿐만 아니라 값으로 다뤄질 수 있다. `Promise.all`, `Promise.race`와 같은 함수들은 복합적인 비동기 작업의 결과를 한 번에 처리할 수 있게 도와준다. Promise를 변수에 담거나 함수에 전달하거나 원하는 시점에 꺼내는 방식으로 유연하게 비동기를 제어할 수 있다.
- **지연성으로 다루는 비동기**: 지연 평가를 통해 비동기 작업을 미뤄둔 후 원하는 로직에 맞춰 평가하는 방식으로 효율적으로 비동기 작업을 핸들링할 수 있다. `executeWithLimit`와 같은 병렬 로직을 가진 함수를 더욱 쉽고 안전하게 만들 수 있으며 `chunk`, `map`, `fromAsync` 같은 리스트 프로세싱 함수와 결합하여 선언적이고 가독성 높은 코드를 작성할 수 있다.
- **타입으로 다루는 비동기**: 타입스크립트의 타입 시스템은 비동기 함수형 프로그래밍을 구현하는 강력한 도구를 제공한다. `FxIterable`과 `FxAsyncIterable` 클래스는 반복자 패턴을 확장하여 동기 및 비동기 작업을 일관된 방식으로 처리할 수 있게 한다. `toAsync`를 통해 동기에서 비동기로의 전환을 선언적으로 표현하고 컴파일 타임에 비동기 로직을 검증할 수 있다.
- **비동기 에러 핸들링**: 에러가 제대로 발생되도록 설계하는 것이 핵심이다. 순수 함수에서는 에러를 발생시키고 호출자에게 위임하는 것이 바람직하며 부수 효과를 발생시키는 코드 근처에서 에러를 처리해야 한다. AsyncIterator와 지연 평가를 활용하면 에러 발생 시 불필요한 추가 작업을 방지하고 즉시 에러를 전파할 수 있다.
