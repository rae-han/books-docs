# Item 27: 콜백 대신 async 함수로 타입 흐름 개선하기 (Use async Functions Instead of Callbacks to Improve Type Flow)

## 핵심 질문

콜백보다 프로미스, 프로미스보다 async/await를 써야 하는 타입 관점의 이유는 무엇인가?

고전 자바스크립트는 비동기를 콜백으로 모델링했고, 그 결과가 악명 높은 "파멸의 피라미드(pyramid of doom)"다.

```typescript
fetchURL(url1, function(response1) {
  fetchURL(url2, function(response2) {
    fetchURL(url3, function(response3) {
      // ...
      console.log(1);
    });
    console.log(2);
  });
  console.log(3);
});
console.log(4);
// 출력: 4 3 2 1
```

중첩이 깊고 실행 순서가 코드 순서와 반대라 읽기 어렵다. 동시 요청이나 에러 시 중단을 원하면 더 혼란스러워진다.

ES2015의 프로미스(*Promise - 미래에 사용 가능해질 무언가의 표현. future라고도 부름*)가 피라미드를 깨뜨렸다.

```typescript
const page1Promise = fetch(url1);
page1Promise.then(response1 => {
  return fetch(url2);
}).then(response2 => {
  return fetch(url3);
}).then(response3 => {
  // ...
}).catch(error => {
  // ...
});
```

중첩이 줄고 실행 순서가 코드 순서와 일치하며, 에러 처리 통합과 `Promise.all` 같은 고차 도구 사용이 쉬워졌다. ES2017의 `async`/`await`는 더 간결하게 만든다.

```typescript
async function fetchPages() {
  try {
    const response1 = await fetch(url1);
    const response2 = await fetch(url2);
    const response3 = await fetch(url3);
    // ...
  } catch (e) {
    // ...
  }
}
```

`await`는 각 프로미스가 해소될 때까지 함수 실행을 멈춘다. async 함수 안에서 거부되는 프로미스를 await하면 예외를 던지므로 익숙한 try/catch를 쓸 수 있다(예외처럼 타입스크립트에서 프로미스 거부도 타입이 없다). `async`·`await`는 최신 런타임이 다 지원하고, ES5 이전을 타깃해도 컴파일러가 정교한 변환으로 동작하게 해 준다 — **런타임이 무엇이든 타입스크립트에서는 async/await를 쓸 수 있다.**

## 1. 콜백보다 프로미스를 선호할 이유

1. **프로미스는 콜백보다 합성이 쉽다.**
2. **타입이 콜백보다 프로미스를 훨씬 잘 타고 흐른다.**

동시 요청은 `Promise.all` 합성으로 해결되고, await와 구조 분해의 궁합이 특히 좋다.

```typescript
async function fetchPages() {
  const [response1, response2, response3] = await Promise.all([
    fetch(url1), fetch(url2), fetch(url3)
  ]);
  // ...
}
```

세 `response` 변수의 타입이 전부 `Response`로 추론된다. 콜백으로 같은 동시 요청을 짜면 장치도 더 필요하고 타입 구문도 필요하다(`numDone` 카운터, `responses: string[]` 배열, 완료 검사…). 에러 처리를 넣거나 `Promise.all`만큼 일반적으로 만드는 것은 더 어렵다.

입력 프로미스 중 첫 번째가 해소될 때 해소되는 `Promise.race`와도 추론이 잘 맞는다 — 프로미스에 타임아웃을 다는 일반적 방법:

```typescript
function timeout(timeoutMs: number): Promise<never> {
  return new Promise((resolve, reject) => {
    setTimeout(() => reject('timeout'), timeoutMs);
  });
}

async function fetchWithTimeout(url: string, timeoutMs: number) {
  return Promise.race([fetch(url), timeout(timeoutMs)]);
}
```

`fetchWithTimeout`의 반환 타입은 구문 없이 `Promise<Response>`로 추론된다. 이유를 파 보면 흥미롭다 — `Promise.race`의 반환 타입은 입력 타입들의 유니온, 즉 `Promise<Response | never>`인데, `never`(공집합)와의 유니온은 아무 일도 하지 않으므로(Item 7) `Promise<Response>`로 단순화된다.

## 2. 프로미스보다 async/await를 선호할 이유

`setTimeout` 같은 콜백 API를 감쌀 때처럼 날 프로미스가 필요한 경우도 있다. 하지만 선택할 수 있다면 async/await가 낫다.

1. 보통 더 간결하고 곧은 코드가 된다.
2. **async 함수는 항상 프로미스를 반환하도록 강제된다.**

두 번째 성질이 헷갈리는 버그 부류를 통째로 막아 준다. async 함수는 정의상 아무것도 await하지 않아도 항상 프로미스를 반환한다.

```typescript
async function getNumber() { return 42; }
// ^? function getNumber(): Promise<number>

const getNumber = async () => 42;
// ^? const getNumber: () => Promise<number>

// 날 프로미스 등가물:
const getNumber = () => Promise.resolve(42);
```

즉시 사용 가능한 값에 프로미스를 반환하는 것이 이상해 보일 수 있지만, 중요한 규칙을 강제해 준다.

> **핵심 통찰**: **함수는 항상 동기로 실행되거나 항상 비동기로 실행되어야 한다. 절대 둘을 섞으면 안 된다.**

이 규칙을 깨면 어떤 혼돈이 오는지, `fetchURL`에 캐시를 달아 보자.

```typescript
// 이렇게 하지 말 것!
const _cache: {[url: string]: string} = {};
function fetchWithCache(url: string, callback: (text: string) => void) {
  if (url in _cache) {
    callback(_cache[url]);   // 캐시 히트 시 동기 호출!
  } else {
    fetchURL(url, text => {
      _cache[url] = text;
      callback(text);
    });
  }
}

let requestStatus: 'loading' | 'success' | 'error';
function getUser(userId: string) {
  fetchWithCache(`/user/${userId}`, profile => {
    requestStatus = 'success';
  });
  requestStatus = 'loading';
}
```

콜백 즉시 호출이 최적화처럼 보이지만 클라이언트가 쓰기 극도로 어려운 함수가 됐다. `getUser` 호출 후 `requestStatus`의 값은? **프로필이 캐시됐는지에 전적으로 달렸다.** 캐시가 없으면 'success', 있으면 'success'가 됐다가 도로 'loading'이 된다. 이런!

양쪽을 async로 만들면 일관된 동작이 강제된다.

```typescript
const _cache: {[url: string]: string} = {};
async function fetchWithCache(url: string) {
  if (url in _cache) {
    return _cache[url];
  }
  const response = await fetch(url);
  const text = await response.text();
  _cache[url] = text;
  return text;
}

let requestStatus: 'loading' | 'success' | 'error';
async function getUser(userId: string) {
  requestStatus = 'loading';
  const profile = await fetchWithCache(`/user/${userId}`);
  requestStatus = 'success';
}
```

이제 `requestStatus`가 'success'로 끝난다는 것이 완전히 투명하다. 콜백이나 날 프로미스로는 반쯤 동기인 코드를 우연히 만들기 쉽지만 async로는 어렵다.

async 함수에서 프로미스를 반환해도 또 다른 프로미스로 감싸이지 않는다 — 반환 타입은 `Promise<Promise<T>>`가 아니라 `Promise<T>`다. 이것도 타입스크립트가 직관을 세워 준다.

```typescript
async function getJSON(url: string) {
  const response = await fetch(url);
  const jsonPromise = response.json();
  //    ^? const jsonPromise: Promise<any>
  return jsonPromise;
}
getJSON
// ^? function getJSON(url: string): Promise<any>
```

## 기억해야 할 것들

- 합성과 타입 흐름이 더 좋은 프로미스를 콜백보다 선호하라.
- 가능하면 날 프로미스보다 `async`/`await`를 선호하라. 더 간결하고 곧은 코드가 되며 에러 부류 전체가 사라진다.
- 함수가 프로미스를 반환한다면 async로 선언하라.
