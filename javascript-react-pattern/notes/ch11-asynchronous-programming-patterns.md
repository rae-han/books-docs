# Chapter 11: Asynchronous Programming Patterns (비동기 프로그래밍 패턴)

## 핵심 질문

> 자바스크립트의 비동기 프로그래밍은 콜백에서 Promise, async/await로 어떻게 진화했으며, 실무에서 비동기 코드를 견고하고 유지보수 가능하게 작성하려면 어떤 패턴을 적용해야 하는가?

---

## 1. 비동기 프로그래밍 기초

### 동기 vs 비동기

자바스크립트에서 **동기 코드**(*Synchronous Code*)는 **블로킹**(*Blocking*) 방식으로 실행된다. 코드가 순서대로 한 문장씩 실행되며, 현재 문장이 완료되어야 다음 문장으로 넘어간다.

```typescript
function synchronousFunction(): void {
  // 동기 함수 동작 — 내부 코드가 모두 실행된 후 반환
}

synchronousFunction();
// 이 줄은 위 함수가 완전히 끝난 후에야 실행된다
```

반면 **비동기 코드**(*Asynchronous Code*)는 **논블로킹**(*Non-blocking*) 방식으로 실행된다. 자바스크립트 엔진은 오래 걸리는 작업을 백그라운드에서 실행하면서, 나머지 코드의 실행을 즉시 이어간다.

```typescript
async function asynchronousFunction(): Promise<void> {
  // 비동기 함수 동작 — 백그라운드에서 실행
}

asynchronousFunction();
// 함수 내부의 코드는 백그라운드에서 실행되며, 이 줄로 즉시 제어권이 반환된다
```

비동기 코드는 **네트워크 요청**, **데이터베이스 읽기/쓰기**, **파일 I/O** 등 오래 걸리는 작업에 적합하다.

### 이벤트 루프와 실행 모델

자바스크립트는 **싱글 스레드** 언어이지만, **이벤트 루프**(*Event Loop*)를 통해 비동기 작업을 처리한다.

```
┌─────────────────────────────┐
│         Call Stack           │  ← 현재 실행 중인 함수
├─────────────────────────────┤
│      Microtask Queue         │  ← Promise 콜백, queueMicrotask
├─────────────────────────────┤
│      Macrotask Queue         │  ← setTimeout, setInterval, I/O
└─────────────────────────────┘
```

| 큐 | 우선순위 | 예시 |
|---|---|---|
| **Microtask** | 높음 (매 태스크 후 즉시 처리) | `Promise.then`, `queueMicrotask`, `MutationObserver` |
| **Macrotask** | 낮음 (microtask 큐가 빈 후 처리) | `setTimeout`, `setInterval`, `requestAnimationFrame` |

> **핵심 통찰**: 자바스크립트의 비동기 모델을 이해하려면 이벤트 루프의 작동 방식을 반드시 알아야 한다. Promise 콜백(microtask)은 setTimeout 콜백(macrotask)보다 항상 먼저 실행된다.

---

## 2. 콜백에서 async/await까지 — 비동기의 진화

자바스크립트의 비동기 처리는 세 단계로 진화해왔다. 같은 HTTP 요청 작업을 각 방식으로 비교해보면 그 차이가 명확하다.

### 2.1 콜백 패턴

콜백(*Callback*)은 다른 함수에 인수로 전달되어, 비동기 작업이 완료된 후 실행되는 함수다. Node.js의 **에러 우선 콜백**(*Error-First Callback*) 컨벤션이 대표적이다.

```typescript
type Callback<T> = (error: Error | null, data?: T) => void;

function makeRequest(url: string, callback: Callback<unknown>): void {
  fetch(url)
    .then(response => response.json())
    .then(data => callback(null, data))
    .catch(error => callback(error));
}

makeRequest('https://api.example.com/data', (error, data) => {
  if (error) {
    console.error(error);
  } else {
    console.log(data);
  }
});
```

### 콜백 지옥 (Pyramid of Doom)

콜백의 최대 단점은 **콜백 지옥**(*Callback Hell*)이다. 순차적인 비동기 작업이 중첩되면 코드가 피라미드 형태로 깊어진다.

```typescript
// 나쁜 예 — 콜백 지옥
makeRequest('https://api.example.com/1', (error, data1) => {
  if (error) { console.error(error); return; }
  makeRequest('https://api.example.com/2', (error, data2) => {
    if (error) { console.error(error); return; }
    makeRequest('https://api.example.com/3', (error, data3) => {
      if (error) { console.error(error); return; }
      // data1, data2, data3을 다루기
    });
  });
});
```

콜백 지옥의 문제점은 **가독성 저하**, **에러 처리의 반복**, **제어 흐름 파악의 어려움**이다. 이러한 문제를 해결하기 위해 Promise가 도입되었다.

### 2.2 Promise 패턴

프로미스(*Promise*)는 비동기 작업의 **최종 완료 또는 실패**를 나타내는 객체다. 세 가지 상태를 가진다.

| 상태 | 설명 |
|---|---|
| **대기** (*Pending*) | 초기 상태. 아직 이행되지도, 거부되지도 않은 상태 |
| **이행** (*Fulfilled*) | 작업이 성공적으로 완료된 상태 |
| **거부** (*Rejected*) | 작업이 실패한 상태 |

```typescript
function makeRequest(url: string): Promise<unknown> {
  return new Promise((resolve, reject) => {
    fetch(url)
      .then(response => response.json())
      .then(data => resolve(data))
      .catch(error => reject(error));
  });
}

makeRequest('https://api.example.com/data')
  .then(data => console.log(data))
  .catch(error => console.error(error));
```

Promise는 `.then()` 체이닝으로 콜백 지옥을 평탄화하고, `.catch()`로 에러를 한 곳에서 처리할 수 있게 해준다.

### 2.3 async/await 패턴

`async/await`는 Promise를 기반으로 구축된 문법적 설탕(*Syntactic Sugar*)이다. 비동기 코드를 마치 동기 코드처럼 작성할 수 있게 해준다.

```typescript
async function makeRequest(url: string): Promise<unknown> {
  try {
    const response: Response = await fetch(url);
    const data: unknown = await response.json();
    return data;
  } catch (error) {
    console.error(error);
    throw error;
  }
}
```

### 세 방식의 비교

| 특성 | 콜백 | Promise | async/await |
|---|---|---|---|
| **가독성** | 중첩이 깊어지면 나쁨 | `.then()` 체이닝으로 평탄화 | 동기 코드처럼 읽힘 |
| **에러 처리** | 각 콜백마다 수동 체크 | `.catch()`로 체인 전체 처리 | `try-catch` 블록 |
| **디버깅** | 스택 트레이스 단절 | 개선됨 | 동기 코드와 동일한 스택 트레이스 |
| **취소** | 불가 | 불가 (별도 패턴 필요) | AbortController와 결합 가능 |
| **반환값** | 없음 (콜백으로 전달) | Promise 객체 | Promise 객체 (암시적) |

> **Osmani의 조언**: async/await는 Promise를 기반으로 구축되었으므로, Promise의 동작 원리를 이해하지 못한 채 async/await만 사용하면 디버깅이 어려워진다. 두 가지 모두 확실히 이해하는 것이 중요하다.

---

## 3. 체이닝과 파이프라인

### 3.1 Promise 체이닝

**프로미스 체이닝**(*Promise Chaining*)은 여러 비동기 작업을 `.then()`으로 연결하여 순차적으로 실행하는 패턴이다. 각 `.then()`은 새로운 Promise를 반환하므로 체인을 계속 이어갈 수 있다.

```typescript
interface RawData {
  items: string[];
  total: number;
}

interface ProcessedData {
  items: string[];
  total: number;
  processedAt: Date;
}

function fetchData(url: string): Promise<RawData> {
  return fetch(url).then(res => res.json());
}

function processData(data: RawData): ProcessedData {
  return { ...data, processedAt: new Date() };
}

function formatOutput(data: ProcessedData): string {
  return `총 ${data.total}개 항목 처리 완료 (${data.processedAt.toISOString()})`;
}

// Promise 체이닝
fetchData('https://api.example.com/items')
  .then(data => processData(data))
  .then(processed => formatOutput(processed))
  .then(output => console.log(output))
  .catch(error => console.error('파이프라인 실패:', error));
```

### 3.2 비동기 파이프라인

**파이프라인 패턴**은 함수형 프로그래밍 기법을 활용하여 변환 함수들을 조합하는 고급 패턴이다. async/await와 결합하면 가독성이 크게 향상된다.

```typescript
// 제네릭 파이프라인 함수
type AsyncTransform<T> = (data: T) => Promise<T> | T;

function createPipeline<T>(...transforms: AsyncTransform<T>[]) {
  return async (initialValue: T): Promise<T> => {
    let result = initialValue;
    for (const transform of transforms) {
      result = await transform(result);
    }
    return result;
  };
}

// 사용 예시
interface UserData {
  name: string;
  email: string;
  verified: boolean;
}

const processUser = createPipeline<UserData>(
  async (user) => ({ ...user, name: user.name.trim() }),
  async (user) => ({ ...user, email: user.email.toLowerCase() }),
  async (user) => {
    const isVerified = await checkEmailVerification(user.email);
    return { ...user, verified: isVerified };
  }
);

const result = await processUser({ name: '  홍길동 ', email: 'HONG@Example.COM', verified: false });
```

### 3.3 비동기 함수 조합 (Composition)

여러 비동기 함수를 조합하여 복잡한 로직을 구성하는 패턴이다.

```typescript
async function fetchUser(id: number): Promise<User> {
  const response = await fetch(`/api/users/${id}`);
  return response.json();
}

async function fetchUserPosts(userId: number): Promise<Post[]> {
  const response = await fetch(`/api/users/${userId}/posts`);
  return response.json();
}

async function enrichPostsWithComments(posts: Post[]): Promise<EnrichedPost[]> {
  return Promise.all(
    posts.map(async (post) => {
      const comments = await fetch(`/api/posts/${post.id}/comments`).then(r => r.json());
      return { ...post, comments };
    })
  );
}

// 조합: 여러 비동기 함수를 순차적으로 연결
async function getUserFeed(userId: number): Promise<EnrichedPost[]> {
  const user = await fetchUser(userId);
  const posts = await fetchUserPosts(user.id);
  const enrichedPosts = await enrichPostsWithComments(posts);
  return enrichedPosts;
}
```

> **핵심 통찰**: 파이프라인과 함수 조합의 핵심은 **각 단계를 독립적으로 테스트 가능한 순수 함수**로 만드는 것이다. 비동기 코드도 함수형 프로그래밍 원칙을 적용하면 유지보수성이 크게 향상된다.

---

## 4. 에러 처리

비동기 코드에서 에러 처리는 동기 코드보다 복잡하다. 적절한 패턴을 사용하지 않으면 에러가 조용히 무시되거나, 예측 불가능한 동작을 유발한다.

### 4.1 기본 try-catch 패턴

```typescript
async function fetchWithErrorHandling(url: string): Promise<unknown> {
  try {
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof TypeError) {
      // 네트워크 에러 (오프라인 등)
      console.error('네트워크 에러:', error.message);
    } else if (error instanceof SyntaxError) {
      // JSON 파싱 에러
      console.error('응답 파싱 에러:', error.message);
    } else {
      // HTTP 에러 또는 기타
      console.error('요청 실패:', error);
    }
    throw error; // 상위로 전파
  }
}
```

### 4.2 Result 패턴 — 에러를 값으로 다루기

Go 언어 스타일의 에러 처리를 TypeScript에 적용하면, `try-catch` 없이도 타입 안전한 에러 처리가 가능하다.

```typescript
type Result<T, E = Error> =
  | { ok: true; value: T }
  | { ok: false; error: E };

async function safeAsync<T>(promise: Promise<T>): Promise<Result<T>> {
  try {
    const value = await promise;
    return { ok: true, value };
  } catch (error) {
    return { ok: false, error: error instanceof Error ? error : new Error(String(error)) };
  }
}

// 사용 예시
async function loadUserProfile(id: number): Promise<void> {
  const result = await safeAsync(fetchUser(id));

  if (!result.ok) {
    console.error('사용자 조회 실패:', result.error.message);
    return;
  }

  // result.value의 타입이 자동으로 User로 좁혀진다
  console.log('사용자:', result.value.name);
}
```

### JavaScript vs TypeScript

TypeScript의 **판별 유니온**(*Discriminated Union*)은 Result 패턴에서 큰 이점을 제공한다.

```typescript
// TypeScript — ok 필드로 타입이 자동 좁혀짐
const result = await safeAsync(fetchData());
if (result.ok) {
  console.log(result.value); // ✅ value 접근 가능, error 접근 불가
} else {
  console.log(result.error); // ✅ error 접근 가능, value 접근 불가
}
```

JavaScript에서는 이러한 타입 안전성이 없으므로, 런타임에 직접 `ok` 필드를 체크해야 하며 실수로 잘못된 필드에 접근할 위험이 있다.

### 4.3 Promise 체인에서의 에러 처리

`.catch()`는 체인 전체의 에러를 한 곳에서 처리할 수 있지만, **어디에 배치하느냐에 따라** 동작이 달라진다.

```typescript
// .catch()의 위치에 따른 차이
fetchData('/api/data')
  .then(data => processData(data))     // processData에서 에러 발생 시
  .catch(error => fallbackData)         // fallbackData로 복구
  .then(data => formatOutput(data))     // 복구된 데이터로 계속 진행
  .then(output => console.log(output))
  .catch(error => console.error(error)); // formatOutput 이후의 에러만 처리
```

> **Osmani의 조언**: 비동기 에러 처리에서 가장 흔한 실수는 `catch` 블록 없이 Promise를 사용하거나, `async` 함수의 반환값을 `await` 없이 무시하는 것이다. 처리되지 않은 Promise 거부(*Unhandled Rejection*)는 Node.js에서 프로세스 크래시를 유발할 수 있다.

---

## 5. 병렬 처리

여러 비동기 작업을 동시에 실행하는 것은 성능 최적화의 핵심이다. JavaScript는 네 가지 병렬 처리 유틸리티를 제공한다.

### 5.1 Promise.all — 전부 성공해야 하는 경우

모든 Promise가 이행되면 결과 배열을 반환하고, **하나라도 거부되면 즉시 실패**한다.

```typescript
interface ApiResponses {
  users: User[];
  posts: Post[];
  comments: Comment[];
}

async function loadDashboard(): Promise<ApiResponses> {
  const [users, posts, comments] = await Promise.all([
    fetch('/api/users').then(r => r.json()) as Promise<User[]>,
    fetch('/api/posts').then(r => r.json()) as Promise<Post[]>,
    fetch('/api/comments').then(r => r.json()) as Promise<Comment[]>,
  ]);

  return { users, posts, comments };
}
```

### 5.2 Promise.allSettled — 결과와 무관하게 모두 완료 대기

모든 Promise가 **이행 또는 거부된 후** 각각의 결과를 배열로 반환한다. 하나가 실패해도 나머지 결과를 잃지 않는다.

```typescript
interface BatchResult<T> {
  succeeded: T[];
  failed: { reason: string }[];
}

async function batchFetch<T>(urls: string[]): Promise<BatchResult<T>> {
  const results = await Promise.allSettled(
    urls.map(url => fetch(url).then(r => r.json() as Promise<T>))
  );

  const succeeded: T[] = [];
  const failed: { reason: string }[] = [];

  for (const result of results) {
    if (result.status === 'fulfilled') {
      succeeded.push(result.value);
    } else {
      failed.push({ reason: result.reason?.message ?? 'Unknown error' });
    }
  }

  return { succeeded, failed };
}

// 사용: 일부 URL이 실패해도 나머지 결과를 활용
const { succeeded, failed } = await batchFetch<User>([
  '/api/users/1', '/api/users/2', '/api/users/999'
]);
console.log(`성공: ${succeeded.length}, 실패: ${failed.length}`);
```

### 5.3 Promise.race — 가장 빠른 결과

여러 Promise 중 **가장 먼저 이행 또는 거부되는** 결과를 반환한다. 타임아웃 구현에 유용하다.

```typescript
function withTimeout<T>(promise: Promise<T>, ms: number): Promise<T> {
  const timeout = new Promise<never>((_, reject) =>
    setTimeout(() => reject(new Error(`${ms}ms 타임아웃 초과`)), ms)
  );

  return Promise.race([promise, timeout]);
}

// 사용: 3초 내에 응답이 없으면 타임아웃
try {
  const data = await withTimeout(fetch('/api/slow-endpoint'), 3000);
  console.log('응답 수신:', data);
} catch (error) {
  console.error(error.message); // "3000ms 타임아웃 초과"
}
```

### 5.4 Promise.any — 첫 번째 성공

여러 Promise 중 **가장 먼저 이행되는** 결과를 반환한다. 모두 거부되면 `AggregateError`를 던진다. 가장 빠른 미러 서버 선택 등에 유용하다.

```typescript
async function fetchFromFastestMirror(mirrors: string[]): Promise<unknown> {
  try {
    const data = await Promise.any(
      mirrors.map(url => fetch(url).then(r => r.json()))
    );
    return data;
  } catch (error) {
    if (error instanceof AggregateError) {
      console.error('모든 미러 서버 실패:', error.errors);
    }
    throw error;
  }
}

const data = await fetchFromFastestMirror([
  'https://mirror1.example.com/data',
  'https://mirror2.example.com/data',
  'https://mirror3.example.com/data',
]);
```

### 병렬 처리 유틸리티 비교

| 메서드 | 성공 조건 | 실패 조건 | 사용 시나리오 |
|---|---|---|---|
| `Promise.all` | 모두 이행 | 하나라도 거부 | 모든 데이터가 필요한 경우 |
| `Promise.allSettled` | 항상 (모두 완료) | 없음 | 부분 실패를 허용하는 경우 |
| `Promise.race` | 첫 번째 완료 (이행/거부) | 첫 번째 완료가 거부인 경우 | 타임아웃, 경쟁 조건 |
| `Promise.any` | 첫 번째 이행 | 모두 거부 | 가장 빠른 성공 결과 필요 |

### 5.5 동시성 제한 (Concurrency Limiter)

`Promise.all`로 수천 개의 요청을 동시에 보내면 서버에 과부하가 걸린다. 동시 실행 수를 제한하는 패턴이 필요하다.

```typescript
async function limitConcurrency<T>(
  tasks: (() => Promise<T>)[],
  limit: number
): Promise<T[]> {
  const results: T[] = [];
  const executing: Set<Promise<void>> = new Set();

  for (const task of tasks) {
    const promise = task().then(result => {
      results.push(result);
      executing.delete(promise);
    });
    executing.add(promise);

    if (executing.size >= limit) {
      await Promise.race(executing);
    }
  }

  await Promise.all(executing);
  return results;
}

// 사용: 최대 5개의 동시 요청
const urls = Array.from({ length: 100 }, (_, i) => `/api/items/${i}`);
const tasks = urls.map(url => () => fetch(url).then(r => r.json()));

const results = await limitConcurrency(tasks, 5);
```

> **핵심 통찰**: 병렬 처리는 강력하지만, 무제한 병렬은 리소스 고갈을 초래한다. 실무에서는 항상 동시성 상한을 설정하고, `Promise.allSettled`로 부분 실패에 대비하는 것이 좋다.

---

## 6. 순차 처리

비동기 작업을 **순서대로** 실행해야 하는 경우가 있다. 이전 작업의 결과가 다음 작업의 입력이 되는 경우가 대표적이다.

### 6.1 async/await를 이용한 순차 실행

가장 직관적인 방법이다.

```typescript
async function sequentialRequests(): Promise<void> {
  const step1 = await fetchData('/api/step1');
  const step2 = await fetchData(`/api/step2?ref=${step1.id}`);
  const step3 = await fetchData(`/api/step3?ref=${step2.id}`);
  console.log('최종 결과:', step3);
}
```

### 6.2 배열을 이용한 동적 순차 실행

작업 목록이 동적으로 결정되는 경우, `reduce` 또는 `for...of`를 사용한다.

```typescript
// for...of — 가독성 우수 (권장)
async function processSequentially<T, R>(
  items: T[],
  processor: (item: T) => Promise<R>
): Promise<R[]> {
  const results: R[] = [];
  for (const item of items) {
    const result = await processor(item);
    results.push(result);
  }
  return results;
}

// reduce — 함수형 스타일
async function processWithReduce<T, R>(
  items: T[],
  processor: (item: T) => Promise<R>
): Promise<R[]> {
  return items.reduce<Promise<R[]>>(
    async (accPromise, item) => {
      const acc = await accPromise;
      const result = await processor(item);
      return [...acc, result];
    },
    Promise.resolve([])
  );
}

// 사용
const userIds = [1, 2, 3, 4, 5];
const users = await processSequentially(userIds, id => fetchUser(id));
```

---

## 7. 재시도 (Retry with Exponential Backoff)

네트워크 요청은 일시적인 장애로 실패할 수 있다. **지수 백오프**(*Exponential Backoff*) 전략으로 재시도하면 서버 부하를 줄이면서 복구 가능성을 높인다.

### 7.1 기본 재시도

```typescript
interface RetryOptions {
  maxRetries: number;
  baseDelay: number;      // 밀리초
  maxDelay?: number;       // 밀리초
  backoffFactor?: number;  // 지수 배수 (기본 2)
}

async function withRetry<T>(
  fn: () => Promise<T>,
  options: RetryOptions
): Promise<T> {
  const { maxRetries, baseDelay, maxDelay = 30_000, backoffFactor = 2 } = options;

  let lastError: Error | undefined;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));

      if (attempt === maxRetries) break;

      // 지수 백오프 + 지터(jitter)
      const delay = Math.min(
        baseDelay * Math.pow(backoffFactor, attempt) + Math.random() * 1000,
        maxDelay
      );

      console.warn(`시도 ${attempt + 1}/${maxRetries + 1} 실패. ${delay.toFixed(0)}ms 후 재시도...`);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }

  throw new Error(`${maxRetries + 1}회 시도 후 실패: ${lastError?.message}`);
}

// 사용
const data = await withRetry(
  () => fetch('https://api.example.com/data').then(r => r.json()),
  { maxRetries: 3, baseDelay: 1000 }
);
```

### 7.2 조건부 재시도

모든 에러를 재시도할 필요는 없다. HTTP 4xx 에러는 재시도해도 결과가 같지만, 5xx이나 네트워크 에러는 재시도할 가치가 있다.

```typescript
interface AdvancedRetryOptions extends RetryOptions {
  shouldRetry?: (error: Error, attempt: number) => boolean;
  onRetry?: (error: Error, attempt: number) => void;
}

async function withSmartRetry<T>(
  fn: () => Promise<T>,
  options: AdvancedRetryOptions
): Promise<T> {
  const {
    maxRetries,
    baseDelay,
    maxDelay = 30_000,
    backoffFactor = 2,
    shouldRetry = () => true,
    onRetry,
  } = options;

  let lastError: Error | undefined;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));

      if (attempt === maxRetries || !shouldRetry(lastError, attempt)) break;

      onRetry?.(lastError, attempt);

      const delay = Math.min(
        baseDelay * Math.pow(backoffFactor, attempt) + Math.random() * 1000,
        maxDelay
      );
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }

  throw lastError;
}

// 사용: 5xx 에러만 재시도
const data = await withSmartRetry(
  async () => {
    const response = await fetch('/api/data');
    if (!response.ok) {
      const error = new Error(`HTTP ${response.status}`);
      (error as any).status = response.status;
      throw error;
    }
    return response.json();
  },
  {
    maxRetries: 3,
    baseDelay: 1000,
    shouldRetry: (error) => {
      const status = (error as any).status;
      return !status || status >= 500; // 네트워크 에러 또는 5xx만 재시도
    },
  }
);
```

> **핵심 통찰**: 지수 백오프에 **지터**(*Jitter — 임의의 시간 편차*)를 추가하는 것이 중요하다. 지터 없이 고정된 백오프만 사용하면 여러 클라이언트가 동시에 재시도하는 **집단 효과**(*Thundering Herd*)가 발생한다.

---

## 8. 메모이제이션과 캐싱

동일한 비동기 작업을 반복 호출하면 불필요한 네트워크 요청과 연산이 발생한다. **메모이제이션**(*Memoization*)으로 결과를 캐싱하면 성능을 크게 개선할 수 있다.

### 8.1 기본 비동기 메모이제이션

```typescript
function asyncMemoize<Args extends unknown[], R>(
  fn: (...args: Args) => Promise<R>
): (...args: Args) => Promise<R> {
  const cache = new Map<string, Promise<R>>();

  return (...args: Args): Promise<R> => {
    const key = JSON.stringify(args);

    if (cache.has(key)) {
      return cache.get(key)!;
    }

    // Promise 자체를 캐싱 — 동시 중복 호출도 하나의 요청으로 처리
    const promise = fn(...args).catch(error => {
      cache.delete(key); // 실패 시 캐시 제거
      throw error;
    });

    cache.set(key, promise);
    return promise;
  };
}

// 사용
const memoizedFetch = asyncMemoize(
  async (url: string): Promise<unknown> => {
    const response = await fetch(url);
    return response.json();
  }
);

// 같은 URL에 대해 네트워크 요청은 한 번만 발생
const [data1, data2] = await Promise.all([
  memoizedFetch('/api/users'),
  memoizedFetch('/api/users'), // 캐시된 Promise 반환
]);
```

여기서 핵심은 **결과가 아니라 Promise 자체를 캐싱**한다는 점이다. 이렇게 하면 같은 인자로 동시에 호출되더라도 실제 비동기 작업은 한 번만 실행된다.

### 8.2 TTL이 있는 캐시

캐시된 데이터가 영원히 유효한 것은 아니다. **만료 시간**(*TTL — Time To Live*)을 설정하면 데이터의 신선도를 보장할 수 있다.

```typescript
interface CacheEntry<T> {
  promise: Promise<T>;
  expiresAt: number;
}

function asyncMemoizeWithTTL<Args extends unknown[], R>(
  fn: (...args: Args) => Promise<R>,
  ttlMs: number
): (...args: Args) => Promise<R> {
  const cache = new Map<string, CacheEntry<R>>();

  return (...args: Args): Promise<R> => {
    const key = JSON.stringify(args);
    const cached = cache.get(key);

    if (cached && cached.expiresAt > Date.now()) {
      return cached.promise;
    }

    const promise = fn(...args).catch(error => {
      cache.delete(key);
      throw error;
    });

    cache.set(key, { promise, expiresAt: Date.now() + ttlMs });
    return promise;
  };
}

// 사용: 5분 TTL
const cachedFetchUser = asyncMemoizeWithTTL(
  (id: number) => fetch(`/api/users/${id}`).then(r => r.json()),
  5 * 60 * 1000
);
```

---

## 9. 데코레이터

비동기 함수에 **로깅**, **타이밍**, **재시도** 같은 횡단 관심사(*Cross-Cutting Concern*)를 추가하는 패턴이다. 고차 함수(*Higher-Order Function*)로 구현한다.

### 9.1 로깅 데코레이터

```typescript
function withLogging<Args extends unknown[], R>(
  fn: (...args: Args) => Promise<R>,
  label?: string
): (...args: Args) => Promise<R> {
  const name = label ?? fn.name ?? 'anonymous';

  return async (...args: Args): Promise<R> => {
    console.log(`[${name}] 시작`, args);
    try {
      const result = await fn(...args);
      console.log(`[${name}] 완료`);
      return result;
    } catch (error) {
      console.error(`[${name}] 실패`, error);
      throw error;
    }
  };
}
```

### 9.2 타이밍 데코레이터

```typescript
function withTiming<Args extends unknown[], R>(
  fn: (...args: Args) => Promise<R>,
  label?: string
): (...args: Args) => Promise<R> {
  const name = label ?? fn.name ?? 'anonymous';

  return async (...args: Args): Promise<R> => {
    const start = performance.now();
    try {
      return await fn(...args);
    } finally {
      const elapsed = performance.now() - start;
      console.log(`[${name}] ${elapsed.toFixed(2)}ms`);
    }
  };
}
```

### 9.3 데코레이터 합성

여러 데코레이터를 합성하여 하나의 함수에 적용할 수 있다.

```typescript
function compose<Args extends unknown[], R>(
  ...decorators: ((fn: (...args: Args) => Promise<R>) => (...args: Args) => Promise<R>)[]
) {
  return (fn: (...args: Args) => Promise<R>): ((...args: Args) => Promise<R>) =>
    decorators.reduceRight((wrapped, decorator) => decorator(wrapped), fn);
}

// 사용: 로깅 + 타이밍 + 재시도를 한 번에 적용
const enhancedFetch = compose(
  fn => withLogging(fn, 'fetchData'),
  fn => withTiming(fn, 'fetchData'),
  fn => withRetryDecorator(fn, { maxRetries: 3, baseDelay: 1000 }),
)(
  async (url: string) => {
    const response = await fetch(url);
    return response.json();
  }
);

const data = await enhancedFetch('/api/data');
```

### 9.4 TC39 표준 데코레이터 (Stage 3)

TypeScript 5.0+에서 사용할 수 있는 **표준 데코레이터 문법**을 활용하면 클래스 메서드에 데코레이터를 적용할 수 있다.

```typescript
function asyncLogger<T, Args extends unknown[], R>(
  originalMethod: (...args: Args) => Promise<R>,
  context: ClassMethodDecoratorContext<T>
): (...args: Args) => Promise<R> {
  const methodName = String(context.name);

  return async function (this: T, ...args: Args): Promise<R> {
    console.log(`[${methodName}] 시작`);
    const result = await originalMethod.call(this, ...args);
    console.log(`[${methodName}] 완료`);
    return result;
  };
}

class ApiService {
  @asyncLogger
  async fetchUsers(): Promise<User[]> {
    const response = await fetch('/api/users');
    return response.json();
  }

  @asyncLogger
  async createUser(data: Partial<User>): Promise<User> {
    const response = await fetch('/api/users', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    return response.json();
  }
}
```

### JavaScript vs TypeScript

```typescript
// TypeScript — 표준 데코레이터 문법 (TS 5.0+)
class Service {
  @asyncLogger
  async fetchData(): Promise<Data> { /* ... */ }
}

// JavaScript — 고차 함수로 동일한 효과
const fetchData = withLogging(
  async () => { /* ... */ },
  'fetchData'
);
```

TypeScript의 데코레이터는 **타입 안전성**을 제공하며, `ClassMethodDecoratorContext` 타입을 통해 데코레이터가 적용되는 메서드의 정보에 접근할 수 있다. JavaScript에서는 고차 함수 패턴으로 동일한 기능을 구현하되, 타입 검증은 수동으로 해야 한다.

> **Osmani의 조언**: 데코레이터는 횡단 관심사를 비즈니스 로직으로부터 분리하는 강력한 도구다. 하지만 과도한 데코레이터 사용은 코드의 실행 흐름을 추적하기 어렵게 만든다. 핵심 로직은 항상 명시적으로 유지하라.

---

## 10. 비동기 반복 (Async Iteration)

### 10.1 AsyncIterator 프로토콜

비동기 이터레이터(*Async Iterator*)는 `Symbol.asyncIterator` 메서드를 구현하여, `for await...of` 루프로 순회할 수 있는 객체를 만드는 프로토콜이다.

```typescript
// 비동기 제너레이터 — 가장 간단한 AsyncIterable 생성 방법
async function* createAsyncRange(start: number, end: number): AsyncGenerator<number> {
  for (let i = start; i <= end; i++) {
    await new Promise(resolve => setTimeout(resolve, 100)); // 비동기 딜레이
    yield i;
  }
}

// for await...of로 순회
async function main(): Promise<void> {
  for await (const value of createAsyncRange(1, 5)) {
    console.log(value); // 100ms 간격으로 1, 2, 3, 4, 5 출력
  }
}
```

### 10.2 페이지네이션 처리

비동기 이터레이터의 실용적인 활용 사례 중 하나가 **API 페이지네이션**이다.

```typescript
interface PaginatedResponse<T> {
  data: T[];
  nextCursor: string | null;
}

async function* fetchAllPages<T>(
  baseUrl: string,
  pageSize: number = 20
): AsyncGenerator<T[], void, undefined> {
  let cursor: string | null = null;

  do {
    const url = cursor
      ? `${baseUrl}?cursor=${cursor}&limit=${pageSize}`
      : `${baseUrl}?limit=${pageSize}`;

    const response = await fetch(url);
    const page: PaginatedResponse<T> = await response.json();

    yield page.data;
    cursor = page.nextCursor;
  } while (cursor !== null);
}

// 사용: 모든 페이지를 순회
for await (const users of fetchAllPages<User>('/api/users')) {
  console.log(`${users.length}명의 사용자 처리`);
  for (const user of users) {
    await processUser(user);
  }
}
```

### 10.3 이벤트 스트림 처리

비동기 이터레이터는 WebSocket, Server-Sent Events 같은 **스트림** 데이터 처리에도 적합하다.

```typescript
async function* streamEvents(url: string): AsyncGenerator<MessageEvent> {
  const eventSource = new EventSource(url);

  try {
    while (true) {
      const event = await new Promise<MessageEvent>((resolve, reject) => {
        eventSource.onmessage = resolve;
        eventSource.onerror = reject;
      });
      yield event;
    }
  } finally {
    eventSource.close(); // 이터레이터 종료 시 리소스 정리
  }
}

// 사용
for await (const event of streamEvents('/api/events')) {
  const data = JSON.parse(event.data);
  console.log('이벤트 수신:', data);

  if (data.type === 'END') break; // break 시 finally 블록에서 정리
}
```

> **핵심 통찰**: 비동기 이터레이터의 핵심 가치는 **무한히 이어질 수 있는 비동기 데이터 소스**를 `for await...of` 루프로 간결하게 처리할 수 있다는 점이다. 페이지네이션, 이벤트 스트림, 파일 청크 읽기 등에서 명령형 상태 관리를 제거해준다.

---

## 11. 취소 (AbortController / AbortSignal)

비동기 작업의 **취소**(*Cancellation*)는 원서에서 다루지 않은 중요한 주제다. `AbortController`와 `AbortSignal`을 사용하면 진행 중인 비동기 작업을 안전하게 취소할 수 있다.

### 11.1 기본 사용

```typescript
async function fetchWithAbort(url: string, signal?: AbortSignal): Promise<unknown> {
  const response = await fetch(url, { signal });
  return response.json();
}

// 사용
const controller = new AbortController();

// 5초 후 자동 취소
setTimeout(() => controller.abort(), 5000);

try {
  const data = await fetchWithAbort('/api/slow-data', controller.signal);
  console.log(data);
} catch (error) {
  if (error instanceof DOMException && error.name === 'AbortError') {
    console.log('요청이 취소되었습니다.');
  } else {
    throw error;
  }
}
```

### 11.2 React에서의 취소 패턴

React 컴포넌트가 언마운트될 때 진행 중인 요청을 취소해야 한다.

```typescript
function useAsyncData<T>(url: string): { data: T | null; loading: boolean; error: Error | null } {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    async function load() {
      try {
        setLoading(true);
        const response = await fetch(url, { signal: controller.signal });
        const json = await response.json();
        setData(json);
      } catch (err) {
        if (err instanceof DOMException && err.name === 'AbortError') return;
        setError(err instanceof Error ? err : new Error(String(err)));
      } finally {
        setLoading(false);
      }
    }

    load();
    return () => controller.abort(); // 언마운트 시 취소
  }, [url]);

  return { data, loading, error };
}
```

### 11.3 AbortSignal.timeout과 AbortSignal.any

```typescript
// AbortSignal.timeout — 간편한 타임아웃 생성
const data = await fetch('/api/data', {
  signal: AbortSignal.timeout(5000) // 5초 타임아웃
});

// AbortSignal.any — 여러 시그널 결합
const userController = new AbortController();
const timeoutSignal = AbortSignal.timeout(10000);

const response = await fetch('/api/data', {
  signal: AbortSignal.any([userController.signal, timeoutSignal])
});

// 사용자가 취소 버튼을 누르거나, 10초 타임아웃 중 먼저 발생하는 것으로 취소
```

---

## 최신 업데이트 (2026)

원서 출판(2023) 이후, 비동기 프로그래밍 관련 자바스크립트 생태계에 중요한 변화가 있었다.

### Promise.withResolvers() (ES2024)

Promise를 생성할 때 `resolve`와 `reject` 함수를 외부에서 접근할 수 있게 하는 유틸리티다. 기존에는 변수를 클로저 밖에 선언하는 패턴이 필요했다.

```typescript
// 기존 패턴 — 어색한 변수 선언
let resolve!: (value: string) => void;
let reject!: (reason: Error) => void;
const promise = new Promise<string>((res, rej) => {
  resolve = res;
  reject = rej;
});

// ES2024 — Promise.withResolvers()
const { promise, resolve, reject } = Promise.withResolvers<string>();

// 실용 예시: Deferred 패턴
function createDeferred<T>() {
  return Promise.withResolvers<T>();
}

const deferred = createDeferred<User>();

// 어딘가에서 나중에 resolve
eventEmitter.on('userLoaded', (user: User) => {
  deferred.resolve(user);
});

const user = await deferred.promise;
```

### Explicit Resource Management (`using` / `await using`)

`Symbol.dispose`와 `Symbol.asyncDispose`를 활용한 **명시적 리소스 관리**가 표준화되었다. 데이터베이스 연결, 파일 핸들, 타이머 같은 리소스의 정리를 보장한다.

```typescript
class DatabaseConnection implements AsyncDisposable {
  private connection: Connection;

  static async create(url: string): Promise<DatabaseConnection> {
    const conn = new DatabaseConnection();
    conn.connection = await connect(url);
    return conn;
  }

  async query(sql: string): Promise<unknown> {
    return this.connection.execute(sql);
  }

  async [Symbol.asyncDispose](): Promise<void> {
    await this.connection.close();
    console.log('데이터베이스 연결 해제');
  }
}

// 사용: 스코프를 벗어나면 자동으로 연결 해제
async function getUsers(): Promise<User[]> {
  await using db = await DatabaseConnection.create('postgres://...');
  const users = await db.query('SELECT * FROM users');
  return users as User[];
  // 여기서 자동으로 db[Symbol.asyncDispose]() 호출
}
```

### JavaScript vs TypeScript

```typescript
// TypeScript — await using 구문으로 타입 안전한 리소스 관리
await using db = await DatabaseConnection.create('...');
// db의 타입이 DatabaseConnection으로 추론되며,
// AsyncDisposable을 구현하지 않은 객체에 using을 사용하면 컴파일 에러

// JavaScript — 동일한 구문이지만 타입 검증 없음
// AsyncDisposable을 구현하지 않은 객체에 사용해도 런타임에서야 에러 발견
```

### Top-level await

모듈의 최상위 수준에서 `await`를 사용할 수 있다. 설정 파일 로드, 데이터베이스 초기화 등에 유용하다.

```typescript
// config.ts — 모듈 초기화 시 비동기 작업 수행
const response = await fetch('/api/config');
export const config: AppConfig = await response.json();

// main.ts — import하면 config가 이미 로드된 상태
import { config } from './config.ts';
console.log(config.apiUrl); // 이미 resolve된 값
```

### Signals 제안 (TC39 Stage 1)

콜백이나 Observable 패턴의 대안으로, **반응형 프로그래밍**(*Reactive Programming*)을 위한 Signals 제안이 진행 중이다. Angular, Solid, Preact에서 이미 자체 구현을 사용하고 있다.

```typescript
// Signals — TC39 제안 (아직 표준 아님, 프레임워크별 API 상이)
// 개념 설명을 위한 의사 코드
const count = new Signal.State(0);
const doubled = new Signal.Computed(() => count.get() * 2);

// 비동기 데이터 흐름에 Signals 적용
const userData = new Signal.State<User | null>(null);

effect(async () => {
  const response = await fetch(`/api/users/${userId.get()}`);
  userData.set(await response.json());
});
```

### 최신 업데이트 요약 테이블

| 기능 | 상태 (2026) | 주요 이점 |
|---|---|---|
| `Promise.withResolvers()` | **ES2024 표준** | Deferred 패턴의 간결한 구현 |
| `Promise.allSettled()` | **ES2020 표준** | 부분 실패 허용 병렬 처리 |
| `Promise.any()` | **ES2021 표준** | 첫 번째 성공 결과 반환 |
| Explicit Resource Management | **Stage 3 → 구현 중** | `await using`으로 자동 리소스 정리 |
| Top-level `await` | **ES2022 표준** | 모듈 최상위 비동기 초기화 |
| `AbortSignal.any()` | **표준** | 다중 취소 시그널 결합 |
| `AbortSignal.timeout()` | **표준** | 간편한 타임아웃 시그널 |
| TC39 Signals | **Stage 1** | 반응형 비동기 데이터 흐름 |

---

## 실무 적용 가이드

### 패턴 선택 의사결정 트리

```
비동기 작업이 필요하다
├── 단일 요청인가?
│   ├── Yes → async/await + try-catch
│   └── 취소가 필요한가?
│       └── Yes → AbortController 추가
├── 여러 요청인가?
│   ├── 모두 성공해야 하는가?
│   │   └── Yes → Promise.all
│   ├── 부분 실패를 허용하는가?
│   │   └── Yes → Promise.allSettled
│   ├── 가장 빠른 성공만 필요한가?
│   │   └── Yes → Promise.any
│   └── 동시 실행 수를 제한해야 하는가?
│       └── Yes → limitConcurrency 패턴
├── 반복적인 비동기 데이터인가?
│   └── Yes → AsyncGenerator + for await...of
└── 실패 가능성이 높은가?
    └── Yes → withRetry + 지수 백오프
```

### 실무 체크리스트

| 항목 | 확인 사항 |
|---|---|
| **에러 처리** | 모든 Promise에 `.catch()` 또는 `try-catch`가 있는가? |
| **취소** | 컴포넌트 언마운트 시 진행 중인 요청을 취소하는가? |
| **경쟁 조건** | 이전 요청보다 이후 요청이 먼저 도착할 가능성을 처리하는가? |
| **동시성 제한** | 대량 병렬 요청 시 동시 실행 수를 제한하는가? |
| **재시도** | 일시적 장애에 지수 백오프 재시도를 적용하는가? |
| **메모이제이션** | 동일한 요청의 중복 호출을 방지하는가? |
| **타임아웃** | 무한 대기를 방지하는 타임아웃이 설정되어 있는가? |
| **리소스 정리** | EventSource, WebSocket 등 리소스를 확실히 정리하는가? |

### 안티패턴

```typescript
// 안티패턴 1: forEach에서 await (순차 실행됨)
urls.forEach(async (url) => {
  await fetch(url); // ❌ 병렬이 아닌 순차 실행, 반환값도 무시됨
});

// 올바른 방법
await Promise.all(urls.map(url => fetch(url))); // ✅ 병렬 실행

// 안티패턴 2: 불필요한 Promise 래핑
async function getData(): Promise<string> {
  return new Promise((resolve) => {     // ❌ 불필요한 래핑
    resolve('data');
  });
}

async function getData(): Promise<string> {
  return 'data'; // ✅ async 함수는 자동으로 Promise로 래핑
}

// 안티패턴 3: await 후 .then() 혼용
const data = await fetch(url)
  .then(r => r.json());    // ❌ 혼란스러운 스타일 혼용

const response = await fetch(url);
const data = await response.json();  // ✅ 일관된 스타일

// 안티패턴 4: catch 없는 Promise
fetchData('/api/data');  // ❌ Unhandled Promise Rejection 위험
fetchData('/api/data').catch(console.error);  // ✅ 최소한의 에러 처리
```

---

## 요약

- **비동기 프로그래밍의 진화**: 콜백 → Promise → async/await 순으로 발전했으며, 각 단계는 이전 단계의 한계를 해결한다
- **체이닝과 파이프라인**: Promise 체이닝과 함수형 파이프라인을 통해 복잡한 비동기 흐름을 선언적으로 구성할 수 있다
- **에러 처리**: `try-catch`가 기본이며, Result 패턴으로 에러를 값으로 다루면 타입 안전성이 향상된다
- **병렬 처리**: `Promise.all`, `allSettled`, `race`, `any` 네 가지 유틸리티를 상황에 맞게 선택한다. 동시성 제한도 반드시 고려한다
- **재시도**: 지수 백오프와 지터를 결합한 재시도 전략은 네트워크 장애 복구의 핵심이다
- **메모이제이션**: Promise 자체를 캐싱하면 동시 중복 호출까지 방지할 수 있다
- **데코레이터**: 로깅, 타이밍, 재시도 같은 횡단 관심사를 비즈니스 로직으로부터 분리한다
- **비동기 반복**: `AsyncGenerator`와 `for await...of`로 무한 데이터 스트림을 간결하게 처리한다
- **취소**: `AbortController`는 비동기 작업 취소의 표준 방법이며, React 컴포넌트의 정리에 필수적이다
- **최신 표준**: `Promise.withResolvers()`, Explicit Resource Management (`await using`), Top-level await 등이 비동기 패턴을 더욱 강력하게 만든다

---

## 다른 챕터와의 관계

- **← Ch07 (자바스크립트 디자인 패턴)**: Observer 패턴은 이벤트 기반 비동기 처리의 근간이며, 이 장의 비동기 이벤트 처리 패턴과 밀접하게 연관된다
- **← Ch08 (자바스크립트 MV* 패턴)**: MV* 패턴의 Model 계층에서 비동기 데이터 페칭이 핵심적으로 사용되며, 이 장의 에러 처리와 캐싱 패턴이 적용된다
- **→ Ch12 (리액트 디자인 패턴)**: React의 `useEffect`, Suspense, Server Components에서 비동기 데이터 로딩 패턴이 확장되며, 이 장의 AbortController 취소 패턴이 직접 적용된다
- **→ Ch13 (렌더링 패턴)**: SSR, ISR 등 렌더링 전략에서 비동기 데이터 페칭 시점과 방법이 성능에 직접적인 영향을 미친다