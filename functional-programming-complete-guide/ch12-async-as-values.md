# Chapter 12: Async as Values (값으로 다루는 비동기)

## 핵심 질문

콜백과 Promise의 진짜 차이는 무엇인가? 비동기 상황을 "일급 값"으로 다룬다는 것은 무엇을 가능하게 하며, Promise.race·all·allSettled·any는 그 위에서 어떤 제어를 제공하는가?

---

비동기 프로그래밍은 특정 작업이 완료될 때까지 기다리지 않고 다른 작업을 계속 수행하는 프로그래밍 방식이다. 자바스크립트 환경에서는 주로 IO 작업에 활용된다 — 브라우저는 긴 IO 작업 동안에도 UI의 반응성을 유지하고, 프런트엔드에서는 API 통신과 애니메이션 시점 핸들링에, 백엔드에서는 파일 시스템·데이터베이스·네트워크 통신에 사용된다.

자바스크립트가 실행되는 환경은 대부분 싱글 스레드 기반의 비동기 IO로 프로그램의 동시 실행을 제어한다. Node.js는 싱글 스레드로 동작하지만 비동기 IO를 통해 외부 자원에게 병렬 작업을 맡기고 실행 순서를 제어한다. 따라서 프로그래머는 **비동기적으로 일어나는 작업의 실행 순서를 정확하게 제어**할 수 있어야 한다. Part 4는 그 제어를 값(12장) → 합성(13장) → 지연성·동시성(14장) → 에러 핸들링(15장) 순으로 쌓아 올린다.

---

## 1. 콜백 패턴과 Promise 패턴

자바스크립트에서 비동기를 다루는 방법은 크게 콜백 패턴, 그리고 Promise 기반의 메서드 체인 또는 async/await와 함께 사용하는 Promise 패턴이 있다.

콜백 패턴으로 의도적인 비동기 상황(특정 시간 이후 전달)을 만들면 다음과 같다.

```typescript
const add10 = (a, callback) => {
	setTimeout(() => callback(a + 10), 100);
};

add10(1, console.log); // 0.1초 뒤에 11 출력
```

Promise 패턴은 다음과 같다.

```typescript
const add10 = (a) => {
	return new Promise((resolve) => setTimeout(() => resolve(a + 10), 100));
};

add10(1).then(console.log);
```

가장 상징적인 차이는 **`return`**이다. 눈에 띄는 차이는 연속 실행에서 드러난다.

```typescript
add10(1, (res) => {
	add10(res, (res) => {
		add10(res, console.log);
	});
});
```

```typescript
add10(1)
	.then(add10)
	.then(add10)
	.then(console.log);
```

콜백 패턴은 콜백 지옥이 생기는 반면 Promise 패턴은 읽기 편하다. 하지만 이것은 표면적 차이일 뿐이다.

## 2. 비동기를 값으로 만드는 Promise

콜백과 Promise의 본질적 차이는 모양이나 결과를 꺼내는 방법(then)이 아니다. **Promise 패턴은 `Promise` 클래스로 만들어진 인스턴스를 반환하며, 그 인스턴스는 대기·성공·실패를 다루는 일급 값**이라는 점이 가장 중요하다.

콜백 패턴에서는 비동기 상황이 **코드와 컨텍스트로만** 표현된다. 반면 Promise 패턴에서는 비동기 상황에 대한 **값**을 만들어 리턴한다.

```typescript
const callback = add10(1, console.log);
const promise = add10(1).then(console.log);
```

`callback`은 `undefined`이고 `promise`는 Promise 객체다. 콜백에서는 반환값이 중요하지 않고, setTimeout이 일어난다는 코드적 상황과 끝났을 때 어떤 함수를 실행해 준다는 컨텍스트만 남는다. Promise는 코드를 평가했을 때 **즉시 값이 리턴**되고, 그 값으로 이후에 하고 싶은 일을 계속 이어갈 수 있다.

```typescript
const a = add10(1);
const b = a.then((v) => v + 5);
const c = b.then((v) => v + 5);
const d = c.then((v) => v + 5);
d.then(console.log);
```

비동기로 일어난 상황을 값으로 다룰 수 있고, 값으로 다룰 수 있다는 것은 그것이 **일급**이라는 뜻이다(1장). 변수에 담고, 함수에 전달하고, 원하는 시점에 꺼낸다 — 비동기 상황이 코드가 아니라 값으로 다뤄지고 있다.

## 3. Promise의 상태와 연관 기능 연표

Promise는 비동기 작업의 성공 또는 실패를 처리하는 데 사용하는 객체이자 규약이다. 생성 즉시 대기(*Pending*) 상태로 시작하고, 작업이 성공하면 이행(*Fulfilled*), 실패하면 거부(*Rejected*) 상태로 전환된다. 표준화된 값과 규약은 개발자와 언어가 비동기를 정확하고 안전하게 다룰 수 있게 한다 — 반복자 패턴의 구현체인 이터레이터가 그랬듯, 많은 언어들이 Promise와 동일한 기능을 제공한다.

Promise는 ES6 표준화(2015) 이전인 2010~2013년경부터 Q, Bluebird, When.js 같은 서드파티 라이브러리로 이미 널리 쓰이고 있었다. 연관 기능의 도입 연표는 다음과 같다.

- **ES2015(ES6)**: `Promise`, `Promise.all`, `Promise.race`, `Promise.resolve`, `Promise.reject`
- **ES2017(ES8)**: `async/await`
- **ES2018(ES9)**: `Promise.finally`, `for await...of`, `AsyncIterator`, `AsyncGenerator`
- **ES2020(ES11)**: `Promise.allSettled`
- **ES2021(ES12)**: `Promise.any`
- **ES2022(ES13)**: `Array.fromAsync`

비동기 기술이 ECMAScript에서 지속적으로 발전·보강되는 이유는 이것이 자바스크립트에서 IO를 다루는 핵심 기술이기 때문이다.

이후 장까지 계속 사용할 `delay` 함수를 정의해 둔다 — `time`만큼 대기한 후 `value`를 반환하는 Promise를 즉시 생성해 반환한다.

```typescript
function delay<T>(time: number, value: T): Promise<T> {
  return new Promise((resolve) => setTimeout(resolve, time, value));
}
```

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

## 4. new Promise를 직접 사용해 본 적 있는가

멀티패러다임 노트의 저자는 면접에서 종종 이런 질문을 던진다고 한다.

- 실제 업무에서 `new Promise()`를 직접 사용해 본 경험이 있나요?
- Promise 인스턴스를 인자로 받아 처리하는 함수를 구현해 본 적이 있나요?
- `Promise.all`이나 `Promise.race`를 사용해 본 경험은 있나요?

요즘은 Web API와 Node.js를 비롯한 대부분의 라이브러리가 이미 Promise 기반 인터페이스를 제공하므로 `new Promise`를 직접 작성할 일이 많지 않다. 하지만 기존에 제공되지 않는 **고유한 방식의 병렬 실행 제어 함수**를 구현해야 한다면 `new Promise()`를 직접 생성하고 제어하는 로직이 필요하다. 이는 주어진 헬퍼를 활용하는 것을 넘어, 비동기 프로그래밍에서 발생하는 특정 문제를 자체 알고리즘으로 풀어내는 경험을 의미한다(14장의 `C.reduce`, 17장의 `TaskPool`이 그 사례다).

## 5. 값으로서의 Promise 활용 — go1

비동기 상황이 값이라는 것은 함수에 전달할 수 있고, Promise인지 아닌지 확인할 수도 있다는 뜻이다. 다음과 같은 `go1` 함수가 있다고 하자.

```typescript
const go1 = (a, f) => f(a);
const add5 = a => a + 5;

console.log(go1(10, add5)); // 15
```

값과 함수를 받아 함수에 값을 적용하는 함수다. `go1`이 잘 동작하려면 `f`가 동기 함수이고 `a`도 동기적으로 알 수 있는 값이어야 한다. Promise가 들어가면 정상 동작하지 않는다.

```typescript
console.log(go1(Promise.resolve(10), add5)); // [object Promise]5
```

```typescript
const delay100 = a => new Promise(resolve => setTimeout(() => resolve(a), 100));

console.log(go1(delay100(10), add5)); // [object Promise]5
```

동기·비동기 모두 정상 동작하게 하려면 값이 Promise인지 확인하고 분기하면 된다.

```typescript
const go1 = (a, f) => a instanceof Promise ? a.then(f) : f(a);
const add5 = a => a + 5;

const delay100 = a => new Promise(resolve => setTimeout(() => resolve(a), 100));

console.log(go1(delay100(10), add5)); // Promise { <pending> }
```

값을 꺼내 보려면 then을 이어주면 된다.

```typescript
go1(delay100(10), add5).then(console.log);
```

기존 동기 함수와 표현이 다른 것이 신경 쓰인다면 다음과 같이 완전히 같은 모양으로 쓸 수도 있다 — 값 부분을 제외하면 동일하다.

```typescript
go1(go1(10, add5), console.log);
go1(go1(delay100(10), add5), console.log);
```

`go1`을 통해 일급으로 다뤄지는 인자가 비동기 상황인지 확인하고, 즉시 결과를 만들거나 결과를 만들어 갈 수 있다. 동기 값(10)은 `console.log`까지 즉시 실행되고, `delay100`을 쓴 쪽은 `Promise { <pending> }`이 되어 계속 이어갈 수 있다. **결과의 상황을 일급 값으로 만들어 작업을 연결해 나갈 수 있다는 것** — 이것이 Promise의 가장 중요한 특징이다. 이 작은 `go1`(다른 이름으로 `lift`)이 14장에서 파이프라인 전체에 비동기 지원을 넣는 열쇠가 된다.

## 6. Promise.race — 경주시키기

`Promise.race`는 병렬로 실행된 여러 Promise 중 **가장 먼저 완료된** Promise의 결과나 에러를 반환한다.

```typescript
const promise1 = new Promise((resolve) => setTimeout(resolve, 500, 'one'));
const promise2 = new Promise((resolve) => setTimeout(resolve, 100, 'two'));

await Promise.race([promise1, promise2]).then((value) => {
  console.log(value); // "two"가 출력된다. (먼저 완료된 Promise)
});
```

### 6.1 IO 작업에 타임아웃 설정하기

친구 목록을 가져오는 `/friends` API의 응답이 5초 이상 지연되면 '현재 네트워크 환경이 좋지 않습니다.' 메시지를 출력하고 싶다면 `Promise.race`가 적합하다.

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

> **참고**: AbortController는 비동기 작업을 취소할 수 있도록 도와주는 웹 API로, 주로 fetch 요청에 제한 시간을 설정하거나 중단하는 데 사용된다.

### 6.2 응답 속도에 따라 다른 전략으로 UI 렌더링하기

'친구 초대하기' 버튼을 눌렀을 때, API 응답이 100ms 내로 완료되면 즉시 친구 목록 창을 렌더링하고 그보다 오래 걸리면 로딩 표시를 띄운 후 렌더링하고 싶다고 하자.

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

포인트는 `friendsPromise`를 **변수에 담아** race에도 전달하고, 필요할 때 다시 `await`한다는 것이다. Promise를 변수에 담고, 함수에 전달하고, 원하는 실행 타이밍에 맞게 대기를 거는 것 — 값으로 다루기 때문에 가능한 제어다.

## 7. Promise.all, allSettled, any

### 7.1 Promise.all

`Promise.all`은 주어진 모든 Promise가 이행될 때까지 기다렸다가 모든 결과를 배열로 반환한다. 하나라도 거부되면 즉시 거부되고 거부 이유를 반환한다.

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

세 번의 `getFile` 실행 시간 합은 3000ms지만 병렬로 실행되므로 가장 오래 걸리는 1500ms 후에 결과가 완성된다. 거부가 포함되면 다음과 같다.

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

### 7.2 Promise.allSettled

`Promise.allSettled`는 모든 Promise가 완료될 때까지 기다린 후 각 Promise의 성공/실패 결과를 객체로 담아 반환한다.

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

오해하지 말아야 할 점: `Promise.all`의 동작이 문제라서 `allSettled`가 나온 것이 아니라 **용도가 다르다**. 에러가 전파되기를 원할 때는 여전히 `Promise.all`이 맞다.

ES11 이전에는 `settlePromise` 같은 함수를 만들어 `map`과 함께 대체할 수 있었다.

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

Promise를 함수형 고차 함수와 함께 값으로 다루는 예다 — 각 Promise에 `settlePromise`를 `map`으로 적용하고 `Promise.all`로 기다리면 `allSettled`와 동일한 결과가 된다.

### 7.3 Promise.any

`Promise.race`가 이행이든 거부든 가장 먼저 완료된 결과를 반환한다면, `Promise.any`는 **가장 먼저 이행된** Promise의 값을 반환한다. 모든 Promise가 거부된 경우에만 거부 이유들을 포함한 단일 에러를 반환한다.

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

## 8. 정리 문답

**여러 비동기 작업을 순차적으로 처리하기 위해 콜백 패턴을 깊게 중첩하여 사용할 때 흔히 발생하는 문제점은?**
코드 구조가 복잡해지는 콜백 지옥.

**Promise가 콜백 패턴과 비교하여 비동기 작업의 순차적 연결(chaining)을 용이하게 만드는 핵심 이유는?**
Promise는 비동기 작업 자체를 나타내는 객체를 반환하고, `.then()` 메서드로 다음 작업을 연결할 수 있다.

**Promise가 비동기 상황을 '일급 값'으로 취급한다는 것의 의미는?**
비동기 작업의 상태나 결과를 표현하는 Promise 객체를 변수에 할당하거나 함수의 인자로 전달하는 등 값처럼 다룰 수 있다는 의미다.

## 요약

- 콜백과 Promise의 본질적 차이는 **return** — 콜백은 비동기 상황을 코드·컨텍스트로만 남기지만, Promise는 대기·성공·실패를 담은 **일급 값**을 즉시 반환한다.
- Promise는 Pending → Fulfilled/Rejected 상태를 갖는 표준 규약이며, ES6 표준화 이후 async/await·allSettled·any·fromAsync로 꾸준히 확장되고 있다.
- `go1 = (a, f) => a instanceof Promise ? a.then(f) : f(a)` — 값이 비동기인지 확인해 분기하는 이 한 줄이 동기·비동기를 같은 모양으로 다루는 출발점이다.
- **race**는 타임아웃·응답 속도별 UI 전략에, **all**은 에러 전파가 필요한 병렬 대기에, **allSettled**는 성공/실패를 모두 수집할 때, **any**는 첫 성공만 필요할 때 쓴다 — 용도가 다르다.
- Promise를 변수에 담아 두 번 쓰는 것(race에 넣고, 나중에 다시 await)이 "값으로 다룬다"의 실전 형태다.

## 다른 챕터와의 관계

- **1장**: "일급"의 정의가 이 장에서 비동기 상황에 적용됐다.
- **13장**: then 체이닝이 왜 안전한 합성인지 — 모나드와 Kleisli 관점으로 설명한다.
- **14장**: Promise가 **생성 즉시 실행**된다는 성질이 문제로 등장하고, 지연성과 동시성 제어로 해결한다. `go1`이 파이프라인 전체로 확장된다.
- **15장**: async/await와 파이프라인의 목적 차이, 에러 핸들링을 다룬다.
- **18장**: Promise가 컴포넌트 간 통신의 매개(AlertView·ConfirmView)로 쓰이는 실전 사례가 나온다.
