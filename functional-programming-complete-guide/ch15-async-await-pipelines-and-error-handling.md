# Chapter 15: async/await, Pipelines, and Error Handling (async/await와 파이프라인 그리고 에러 핸들링)

## 핵심 질문

async/await와 파이프라인은 각각 어떤 문제를 푸는 도구인가? 비동기 에러는 왜 try/catch에 잡히지 않으며, 잡히게 하려면 무엇이 필요한가?

---

"async/await가 있는데 왜 파이프라인이 필요한가?"는 함수형 비동기 프로그래밍에서 가장 자주 나오는 질문이다. 이 장은 두 도구가 **해결하려는 문제 자체가 다르다**는 것을 코드로 확인하고, 동기·비동기 에러 핸들링의 원리를 정리한 뒤, 안정적인 소프트웨어를 위한 원칙으로 마무리한다.

---

## 1. async/await 기본

async/await는 비동기 상황을 보다 동기적인 코드로 다루기 위한 방법이다. 하스켈의 do notation과도 비슷하다. 비동기적으로 일어나는 일들을 **동기적인 문장으로** 다룰 수 있게 해준다.

`async`를 사용한 함수 내부에서는 `await`를 사용할 수 있는데, `await`는 Promise가 결과를 만들 때까지 실행을 멈추고 다 만들어졌을 때 다음 흐름을 이어간다. 결국 Promise 기반이므로 Promise를 잘 알아야 한다 — `await`로 멈출 대상이 Promise를 return해야 하기 때문에, 결국 어디선가는 Promise가 있어야 한다.

```typescript
const delay500 = (a, time = 500) =>
  new Promise((resolve) => setTimeout(() => resolve(a), time));

async function f1() {
  const a = await delay500(10);
  const b = await delay500(20);

  console.log(a + b); // 30
}
```

또 하나의 특징: `a`, `b`가 동기적으로 떨어지므로 그 값으로 평가한 값을 반환하면 밖에서도 값을 알 수 있을 것 같지만, 아니다. 어디까지나 **그 블록 안에서만** 동기적이고, `async`를 선언하면 그 함수는 Promise를 리턴하는 함수가 된다 — 심지어 안에 `await`가 없어도 마찬가지다.

```typescript
async function f1() {
  const a = await delay500(10);
  const b = await delay500(20);
  
  return a + b;
}

console.log(f1()); // Promise { <pending> }
```

```typescript
f1().then(console.log);
(async () => {
	console.log(await f1());
})()
```

`f1` 같은 함수를 실행하면 즉시 Promise 값이 나오고, Promise로 평가되는 값을 `await`가 평가한다고 생각하면 좋다. 당연히 이미 만들어진 Promise도 `await`로 꺼낼 수 있다.

```typescript
const p = Promise.resolve(10);
(async () => {
  console.log(await p);
})();
```

## 2. Array.prototype.map을 쓰지 않는 이유

다음 함수를 보자.

```typescript
export const delay = (a, time = 100) =>
  new Promise((resolve) =>
    setTimeout(() => {
      resolve(a);
    }, time),
  );

function fn() {
  const list = [1, 2, 3, 4];

  const res = list.map((a) => delay(a * a));

  console.log(res);
}
fn();
```

```typescript
[
  Promise { <pending> },
  Promise { <pending> },
  Promise { <pending> },
  Promise { <pending> }
]
```

`res`에는 Promise 객체들이 담기고, 실제 평가된 값이 아니므로 합산 같은 연산을 할 수 없다. 콜백에 async/await를 붙여 보자.

```typescript
function fn() {
  const list = [1, 2, 3, 4];

  const res = list.map(async (a) => await delay(a * a));

  console.log(res);
}
```

async 함수는 항상 Promise를 반환하므로 결과는 똑같이 Promise 배열이다. 바깥에 `await`를 붙여도 마찬가지다.

```typescript
async function fn() {
  const list = [1, 2, 3, 4];

  const res = await list.map(async (a) => await delay(a * a));

  console.log(res);
}
```

map의 결과는 **배열이지 Promise가 아니므로** `await`가 비동기 상황을 제어해 줄 수 없다. 반면 14장에서 만든 map(비동기 대응 로직 내장)을 사용하면 잘 제어된다.

```typescript
async function fn() {
  const list = [1, 2, 3, 4];

  const res = await map((a) => delay(a * a), list);

  console.log(res); // [1, 4, 9, 16]
}
```

두 코드를 비교하면 명확하다.

```typescript
async function fn1() {
  const list = [1, 2, 3, 4];
  const response = list.map(async (a) => await delay(a * a)); // 1
  console.log(response); // [Promise, Promise, Promise, Promise]
  const result = await response;
  console.log(result); // 여전히 Promise 배열
}

async function fn2() {
  const list = [1, 2, 3, 4];
  const response = map((a) => delay(a * a), list); // 2
  console.log(response); // Promise { <pending> }
  const result = await response;
  console.log(result); // [1, 4, 9, 16]
}
```

2번 위치에는 배열로 만들 수 있는 **Promise 하나**가 있고, 1번 위치에는 **Promise들이 들어 있는 배열**이 있다. `await`는 Promise를 풀 수 있을 뿐, Promise 배열을 풀 수는 없다.

> **참고**: 표준 도구만으로 풀려면 `await Promise.all(list.map(...))`이 되지만, 이는 전부 병렬 실행이다. 순차/부분 병렬/지연 제어까지 필요하다면 14장의 파이프라인 도구들이 필요해진다.

## 3. async/await vs 파이프라인 — 목적이 다르다

async/await가 해결하려는 문제와 파이프라인(체이닝)이 해결하려는 문제는 서로 다르다.

- **async/await의 목적**: 표현식(`Promise.then.then.then`)에 갇혀 있는 로직을 **문장으로** 다루기 위한 것이다. 특정 부분을 함수 체인이 아닌 문장형으로 풀어놓는 도구다.
- **파이프라인의 목적**: map·filter·reduce를 이터러블 중심으로 사고하면서, 명령형 프로그래밍을 하지 않고 **함수 합성을 더 안전하게** 하기 위한 것이다.

즉 파이프라인은 함수를 **합성하는** 것이 목적이고, async/await는 합성이 아니라 **풀어놓는** 것이 목적이다. 헷갈리기 쉬운 부분: 파이프라인 코드는 동기와 비동기의 모습이 동일하기 때문에 "비동기를 동기적으로 표현하기 위한 것"으로 생각할 수 있지만, 그 목적이 아니라 **동기든 비동기든 상관없이 함수 합성을 안전하게 끝까지 연결**하는 것이 목적이다.

다음 코드를 보자.

```typescript
function f3() {
  return go(
    [1, 2, 3, 4, 5, 6, 7, 8],
    L.map((a) => delay(a * a)),
    L.filter((a) => a % 2),
    L.map((a) => delay(a + 1)),
    take(3),
    reduce((a, b) => delay(a + b)),
  );
}

go(f3(), console.log); // 38
```

이 코드가 해결하려 한 것은 "async/await를 쓰지 않는 것"이 아니라, 복잡한 for·if·break 로직을 쉽고 안전하게 코딩하는 것 — **명령형 코드의 문제**다. 같은 로직을 명령형 + async/await로 풀면 이렇다.

```typescript
async function f4(list) {
  let temp = [];
  for (const a of list) {
    const b = await delay(a * a);
    if (await delay(b % 2)) {
      const c = await delay(b + 1);
      temp.push(c);
      if (temp.length == 3) break;
    }
  }
  let res = temp[0],
    i = 0;
  while (++i < temp.length) {
    res = await delay(res + temp[i]);
  }
  return res;
}
```

보다시피 async/await는 **명령형으로 비동기 상황을 문장으로 풀어서** 해결할 때 쓰인다. 함수 안쪽에서 문장을 쓰려고 할 때 필요한 것이 await다.

극단적인 실험 — `delay`를 즉시 값이 떨어지는 함수로 바꿔 보자.

```typescript
export const delay = (a) => a;
```

`f3`은 아무 상관없이 값이 나오지만, `f4`는 여전히 Promise 객체가 나온다. 비동기가 일어나지 않아도 이미 async 함수이기 때문이다. `f4`는 비동기가 사라지면 await 키워드를 제거하는 리팩터링을 해야 한다. 논리적으로 두 코드가 해결하는 문제가 다르다는 뜻이다 — `f3`은 async/await를 안 쓰려고 만든 코드가 아니므로 변할 것이 없고, `f4`는 async/await로 해결할 문제(비동기 문장화)가 사라지면 키워드도 필요 없어진다.

두 코드 모두 비동기로 동작한다면 시간 복잡도는 같다. `f3`의 map·filter·map·take 조합은 `f4`의 for문(break로 최적화된)과 같은 만큼만 순회한다. 하지만 같은 동작이라도 — `f3`이 전체 동작을 파악하는 시간이 빠르고 테스트도 쉽다. 결정적으로 `f3`은 `take`를 `C.take`로 바꾸는 것만으로 병렬 평가를 적용할 수 있지만, `f4`에서 병렬 평가를 적용하려면 for문 사이사이를 뜯어 배열에 모으고 `Promise.all`로 푸는 대공사가 필요하다.

## 4. async/await와 파이프라인을 함께 사용하기

물론 둘은 함께 쓴다. 하스켈에도 이런 스타일의 코드가 있다.

```typescript
async function f5(list) {
  const r1 = await go(
    list,
    L.map((a) => delay(a * a)),
    L.filter((a) => delay(a % 2)),
    L.map((a) => delay(a + 1)),
    C.take(2),
    reduce((a, b) => delay(a + b)),
  );

  const r2 = await go(
    list,
    L.map((a) => delay(a * a)),
    L.filter((a) => delay(a % 2)),
    reduce((a, b) => delay(a + b)),
  );

  const r3 = await delay(r1 + r2);

  return r3 + 10;
}

go(f5([1, 2, 3, 4, 5, 6, 7, 8]), (a) => console.log(a, 'f5'));
```

**로직의 조각은 파이프라인으로 선언**하고, 그 조각들의 결과를 **문장 흐름(await)으로 엮는** 구성이다. 각 도구가 잘하는 일을 맡는다.

## 5. 동기 상황에서의 에러 핸들링

에러 핸들링 방법은 언어마다 특징과 선호가 다르다. 자바스크립트에서 가장 간편한 핸들링은 **비슷한 값으로 흘려보내거나, 에러를 일으키는 것**이다.

빈 배열은 그대로 흘러간다.

```typescript
function f7(list) {
  return list
    .map((a) => a + 10)
    .filter((a) => a % 2)
    .slice(0, 2);
}

console.log(f7([])); // []
```

`undefined`가 올 수 있으면 기본 매개변수로, `null` 같은 값이 올 수 있으면 `(list || [])`로 흘려보낸다.

```typescript
function f7(list = []) {
  return list
    .map((a) => a + 10)
    .filter((a) => a % 2)
    .slice(0, 2);
}

console.log(f7());
```

```typescript
function f7(list) {
  return (list || [])
    .map((a) => a + 10)
    .filter((a) => a % 2)
    .slice(0, 2);
}

console.log(f7(null));
```

try-catch로 처리한다면 이렇다 — 보조 함수가 잘못돼도 비슷한 값(빈 배열)으로 흘려보내고, catch에서 어떤 에러인지 확인할 수도 있다.

```typescript
function f7(list = []) {
  try {
    return list
      .map((a) => JSON.parse(a))
      .filter((a) => a % 2)
      .slice(0, 2);
  } catch (error) {
    return [];
  }
}

console.log(f7(['1', '2', '3', '4'])); // [1, 3]
console.log(f7(['1', '2', '3', '%'])); // []
```

## 6. 비동기 상황에서의 에러 핸들링 — 왜 catch가 안 잡히는가

비동기 상황에서는 에러 핸들링이 더 복잡하다. 순회 중간에 비동기가 있는 코드를 보자.

```typescript
function f8(list = []) {
  try {
    return list
      .map(
        (a) =>
          new Promise((resolve) => {
            resolve(JSON.parse(a));
          }),
      )
      .filter((a) => a % 2)
      .slice(0, 2);
  } catch (error) {
    console.log('error!!', error);
    return [];
  }
}

console.log(f8(['1', '2', '3', '4']));
```

map 안에서 에러가 나도 catch 문에서 잡히지 않는다. 빈 배열이 출력된다면 catch에 걸린 것이 아니라, map에서 filter까지 엉뚱한 값(Promise 객체들)이 내려가 만들어진 결과다.

Promise executor 스코프에서 에러가 나면 해당 Promise는 rejected가 된다.

```typescript
const p = new Promise((resolve) => {
  resolve(JSON.parse('{'));
});
console.log(p); // Promise { <rejected> SyntaxError: Expected property name or '}' in JSON at position 1 }
```

하지만 여전히 try/catch에는 잡히지 않는다 — **catch로 흐름이 들어가지 않기** 때문이다. 근본 원인은 `Array.prototype.map`·`filter` 같은 함수들이 Promise를 제어할 수 있는 함수가 아니라는 것이다. async/await를 덧붙여도 마찬가지다.

```typescript
async function f9(list = []) {
  try {
    return await list
      .map(
        async (a) =>
          await new Promise((resolve) => {
            resolve(JSON.parse(a));
          }),
      )
      .filter((a) => a % 2)
      .slice(0, 2);
  } catch (error) {
    console.log('error!!', error);
    return [];
  }
}

console.log(f9(['1', '2', '3', '4'])); // Promise { <pending> } — 핸들링 실패
console.log(f9(['1', '2', '3', '4']).then(console.log).catch(console.log)); // 역시 실패
```

## 7. 파이프라인과 await의 협력 — 에러가 잡히게 만들기

비동기 대응이 된 파이프라인(14장)으로 바꾸면 상황이 달라진다.

```typescript
async function f10(list) {
  try {
    return go(
      list,
      map((a) => new Promise((resolve) => resolve(JSON.parse(a)))),
      filter((a) => a % 2),
      take(2),
    );
  } catch (error) {
    console.log('error!!', error);
    return [];
  }
}

console.log(
  f10(['1', '2', '3', '?'])
    .then(console.log)
    .catch((error) => console.log('에러 핸들링 하겠다', error)),
);
```

이때 에러는 함수 **실행부**의 catch("에러 핸들링 하겠다")로 떨어진다. 함수 **구현부**의 catch("error!!")로는 여전히 안 간다. 구현부 catch로 가려면 **try 블록 안이 `await`로 rejected Promise를 평가**해야 하기 때문이다.

```typescript
async function f10(list) {
  try {
    return await Promise.reject('error~~!!'); // await가 있어야
  } catch (error) {
    console.log('error!!', error); // 여기로 떨어진다
    return [];
  }
}
```

즉 첫 코드에서 `await` 하나만 걸어주면 함수 내부 catch에서 에러 핸들링이 된다.

```typescript
async function f10(list) {
  try {
    return await go(
      list,
      map((a) => new Promise((resolve) => resolve(JSON.parse(a)))),
      filter((a) => a % 2),
      take(2),
    );
  } catch (error) {
    console.log('error!!', error);
    return [];
  }
}

console.log(f10(['1', '2', '3', '?']).then(console.log)); // error!! ... 후 []
```

여기서 `await`가 평가하는 대상(go의 반환값)이 **안에서 일어난 일이 모두 추적되고, 함수 합성이 연속적으로 잘 되어 있고, 잘 결론지어진 Promise**여야 한다는 점이 핵심이다. 14장에서 reduce·take가 에러를 Kleisli 방식으로 안전하게 뒤로 전파하도록 만들어 뒀기 때문에 이 한 줄이 동작하는 것이다.

여담으로 재미있는 동작 — map·filter에 지연성을 주면 에러가 오기 전에 평가가 끝나므로 문제없이 값을 꺼낸다. 이것도 개발자의 선택지다.

```typescript
async function f10(list) {
  try {
    return await go(
      list,
      L.map((a) => new Promise((resolve) => resolve(JSON.parse(a)))),
      L.filter((a) => a % 2),
      take(2),
    );
  } catch (error) {
    console.log('error!!', error);
    return [];
  }
}

console.log(f10(['1', '2', '3', '?']).then(console.log)); // ['1', '3'] 상당 — '?'까지 가기 전에 take(2) 충족
```

구현부에서 에러를 catch하고 빈 배열을 리턴하므로, 실행부에서는 더 이상 에러가 나오지 않는다.

```typescript
console.log(
  f10(['1', '2', '3', '?'])
    .then((a) => console.log('then', a)) // []
    .catch((e) => console.log('catch', e)), // 아무런 로그가 찍히지 않음.
);
```

> **핵심 통찰**: 에러 핸들링을 잘 하려면 await에 Promise를 잘 걸어야 하고, Promise를 잘 걸려면 함수 안쪽에서 나는 에러들이 중간에 나도 전체 Promise에 Kleisli 방식으로 안전하게 합성되어 뒤로 연결될 준비가 돼 있어야 한다. 명령형으로 작성하면 함수 체인이 없으므로 필요한 지점마다 직접 에러 처리를 걸어야 한다.

## 8. 실전 — 에러가 새는 코드와 개선

여러 이미지를 불러와 높이 합을 구하는 코드로 원칙을 확인하자.

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

잘 동작하는 듯 보이지만 문제가 있다.

- **불필요한 부하**: 에러가 발생해도 나머지 URL에 대해 이미지 다운로드를 모두 시도한다(`Array.map`이 모든 Promise를 이미 출발시켰기 때문).
- **부수효과**: 이 상황이 POST나 DB INSERT를 제어하는 코드라면 불필요한 요청으로 부수효과가 발생한다.

14장의 `toAsync` 체인으로 바꾸면:

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

첫 번째 URL에서 에러가 발생하면 나머지 요청을 멈추고 즉시 에러를 처리한다. Promise와 AsyncIterator를 안전하게 제어하고 의도대로 정확하게 동작하면서 가독성도 높다.

## 9. 에러가 제대로 발생되도록 하는 것이 핵심

비동기 프로그래밍에서 가장 중요한 것은 단순히 에러를 핸들링하는 것이 아니라 **에러가 제대로 발생되도록 설계**하는 것이다.

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

이 접근의 이점은 다음과 같다.

- **순수 함수 유지**: 에러를 발생시키고 호출자에게 위임하는 것이 바람직하다.
- **유연한 에러 처리**: 각 호출자가 자신에게 필요한 방식으로 에러를 핸들링할 수 있다.
- **에러를 감추지 않음**: 에러를 명확히 발생시키고 위임하면 문제를 조기에 탐지하고 적절히 대응할 수 있다.

## 10. 안정적인 소프트웨어와 비동기 프로그래밍

에러가 제대로 발생되도록 설계하기 위한 원칙이다.

- **Promise, async/await, try/catch를 정확히 이해하고 활용하기**: 비동기 작업에서 에러가 명확히 드러나도록 작성한다.
- **에러를 숨기지 않고 명확히 드러내기**: 감추기보다 발생하도록 두고 상위 레벨에서 처리하거나 로깅 도구로 모니터링한다.
- **순수 함수는 에러를 발생시키도록 설계**: 순수 함수 내부에서 에러를 처리하려 하면 함수의 목적이 흐려진다.
- **제너레이터/이터레이터/이터러블을 활용한 선언적 프로그래밍**: 비동기 이터러블로 에러 발생 시점을 제어하고 에러 전파 흐름을 선언적으로 표현한다.
- **에러 핸들링 코드는 부수효과 코드 근처에 작성**: 네트워크 요청, 파일 입출력 등 부수효과를 발생시키는 코드 근처에서 처리해야 원인과 해결 방안이 명확해진다.

## 요약

- **async/await는 문장의 도구, 파이프라인은 합성의 도구**다 — 전자는 Promise 체인을 문장으로 풀고, 후자는 명령형 없이 함수 합성을 안전하게 연결한다. 목적이 다르므로 대립하지 않고 함께 쓴다(조각은 파이프라인, 흐름은 await).
- `Array.prototype.map`에 async 콜백을 쓰면 **Promise 배열**이 되고 await로 풀 수 없다 — 비동기 대응 map은 **배열이 될 Promise 하나**를 반환한다.
- async 함수는 await가 없어도 항상 Promise를 반환하며, 비동기가 사라지면 리팩터링이 필요하다 — 파이프라인 코드는 동기/비동기에 무관하게 동일하다.
- try/catch가 비동기 에러를 잡으려면 **try 안에서 await가 rejected Promise를 평가**해야 하고, 그 Promise는 내부 에러가 끝까지 합성·전파되도록 만들어져 있어야 한다.
- `Array.map`은 모든 Promise를 즉시 출발시켜 에러 후에도 부하·부수효과를 만든다 — 지연 순차 실행(toAsync 체인)은 에러 지점에서 즉시 멈춘다.
- **에러는 숨기지 말고 제대로 발생시켜 호출자에게 위임**하라 — 순수 함수는 던지고, 부수효과 근처에서 잡는다.

## 다른 챕터와의 관계

- **7장**: reduce의 에러 관리(초깃값·early return·try/catch)가 이 장의 비동기 버전으로 확장됐다.
- **13장**: "에러를 값으로(reject)" 만드는 Kleisli 합성이 await·try/catch와 연결되는 지점이 이 장의 7절이다.
- **14장**: 이 장에서 await에 "잘 걸리는" Promise는 14장에서 만든 파이프라인(recur·nop·toAsync)이 보장한 것이다.
- **16장**: 백엔드 실전(결제 동기화 스케줄러)에서 이 원칙들이 실제 코드로 적용된다.
- **19장**: 에러를 던지는 대신 Result 타입으로 반환하는 또 다른 설계가 등장한다 — "효과를 값으로"의 연장선.
