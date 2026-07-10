# Chapter 14: Laziness and Concurrency (지연성과 동시성)

## 핵심 질문

Promise는 생성 즉시 실행된다 — 그렇다면 비동기 실행을 어떻게 지연하고, 부하를 조절하며, 동기와 비동기를 하나의 파이프라인으로 다룰 수 있는가?

---

이 장은 Part 4의 기술적 심장부다. 먼저 Promise의 "즉시 실행" 성질이 만드는 문제를 확인하고(1~3절), 3장에서 만든 `go`/`pipe`/`reduce`와 8장의 지연 함수들에 Promise 지원을 직접 구현해 넣는다(4~8절). 이어서 지연된 함수열을 병렬로 평가하는 `C.*` 함수들을 만들고(9절), 마지막으로 같은 문제를 타입 시스템으로 푸는 멀티패러다임 세대의 해법 — AsyncIterator와 `toAsync` — 을 다룬 뒤(10~12절) 두 접근을 비교한다(13절).

---

## 1. Promise 실행을 지연하려면

`Promise.all`은 모든 Promise를 동시에 병렬로 실행한다. 그런데 부하를 조절하고 싶다면 — 예를 들어 6개의 비동기 작업을 한 번에 3개씩 실행하고 싶다면 — 어떻게 해야 할까?

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

이 코드는 2000ms 정도 걸릴 것이라는 기대와 달리 약 1000ms 만에 모든 Promise가 완료된다. **Promise 객체는 생성되는 즉시 실행되기 때문이다.** `getFile` 같은 함수가 호출되는 순간 이미 Promise가 시작된다. `Promise.all`은 이미 실행된 Promise들을 받아 완료를 대기하는 함수일 뿐, Promise의 시작 자체를 제어하는 함수가 아니다.

해결하려면 아직 Promise들이 실행되지 않은 상태에서 그룹을 나누고 각 그룹이 순차적으로 실행되도록 해야 한다. 방법은 간단하다 — `() =>`와 `()`를 추가하면 된다.

```typescript
async function executeWithLimit<T>(
  fs: (() => Promise<T>)[],
  limit: number
): Promise<T[]> {
  const result1 = await Promise.all([fs[0](), fs[1](), fs[2]()]);
  const result2 = await Promise.all([fs[3](), fs[4](), fs[5]()]);
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

**Promise를 함수로 감싸서 필요할 때 실행되도록 실행을 지연한 것이다.**

## 2. 명령형 vs 함수형 executeWithLimit

위 하드코딩(6개 고정)을 일반화해 보자. ChatGPT에게 맡기면 다음과 같은 명령형 코드를 생성한다.

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

잘 동작하지만 읽기가 상당히 어렵다. 3개씩 안전하게 그룹화하기 위한 외부 `for`와 내부 `for`의 조건들이 복잡하다.

리스트 프로세싱 관점으로 계획하면 이렇게 된다.

- `[() => P, () => P, () => P, () => P, ...]`
- `[[() => P, () => P, () => P], ...]` — 3개씩 그룹화
- `[[P, P, P], ...]` — 함수 실행
- `[P<[T, T, T]>, ...]` — 3개씩 대기하도록 `Promise.all`로 감싸기
- `P<[[T, T, T], ...]>` — `Promise.all`들의 결과 꺼내기
- `P<[T, T, T, T, ...]>` — 1차원 배열로 평탄화

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

`i++` 같은 상태 변화, `j < limit && (i + j) < fs.length` 같은 조건절이 없다. `push` 대신 `fromAsync`, `arr.flat()` 같은 선언적 표현을 쓴다.

## 3. 지연성 — 효과적인 비동기 핸들링의 계단

`executeWithLimit` 구현의 핵심은 지연성이다.

- 함수는 Promise 실행을 지연한 함수(`() => Promise`)를 인자로 받는다.
- `map(f => f())`는 모든 함수를 즉시 실행하는 것처럼 보이지만, 이 `map`은 Array의 map과 달리 **지연 평가되는 map**이다.
- 따라서 `fromAsync`에서 요소 하나를 꺼낼 때 해당 청크 안의 함수들만 실행되고, 다음 `map`에서 `Promise.all`로 감싸진다.
- `fromAsync`는 이 결과를 `for await...of`로 꺼내므로 `Promise.all`의 결과를 대기 후 꺼낸다.

지연 평가는 단순히 성능 개선을 위한 도구가 아니다. 이터레이터와 일급 함수를 **원하는 시점에 평가하는 코드 패턴**을 통해 로직을 재사용 가능한 형태로 만들 수 있다.

## 4. go, pipe, reduce의 비동기 지원 — 직접 구현

이제 관점을 바꿔, 3장에서 만든 파이프라인 함수들이 비동기를 만나면 어떻게 되는지 직접 확인하고 고쳐 보자. `go`/`pipe`/`reduce`는 함수를 연속으로 실행하는 합성 함수들이다. 여기에도 Promise의 "비동기를 값으로 다루는" 성질을 이용해, 비동기 상황에 잘 대응하고 중간에 reject나 에러가 나면 뒤로 흘려보내는 기법을 적용할 수 있다.

```typescript
go(
  1,
  (a) => a + 10,
  (a) => a + 100,
  (a) => a + 1000,
  console.log,
); // 1111
```

특정 지점에 Promise를 리턴하는 함수가 합성되면 비정상 동작한다.

```typescript
go(
  1,
  (a) => a + 10,
  (a) => Promise.resolve(a + 100),
  (a) => a + 1000,
  (a) => a + 10000,
  console.log,
); // [object Promise]100010000
```

12장의 `go1` 기법을 쓰면 된다. `go`와 `pipe`는 `reduce`로 구현했으므로 **reduce만 고치면 나머지도 정상 동작**한다.

```typescript
export const reduce = curry((fn, acc, iter) => {
  if (!iter) {
    iter = acc[Symbol.iterator]();
    acc = iter.next().value;
  }

  iter = iter[Symbol.iterator]();
  let cur;
  while (!(cur = iter.next()).done) {
    const a = cur.value;
    // acc = fn(acc, a); // 기존 코드
    acc = acc instanceof Promise ? acc.then((acc) => fn(acc, a)) : fn(acc, a);
  }
  return acc;
});
```

이 정도 수정으로도 해결은 되지만 좋은 코드는 아니다. Promise를 한 번 만나면 이후의 모든 합성이 Promise 체인에 붙어 **연속적으로 비동기로** 실행된다(`+1000`, `+10000`까지). 개발자가 비동기가 아닌 구간은 하나의 콜스택에서 동기적으로 실행되길 바랐다면, 불필요한 로드로 성능 저하가 생긴다.

다음과 같이 수정하면 해결된다.

```typescript
export const reduce = curry((fn, acc, iter) => {
  if (!iter) {
    iter = acc[Symbol.iterator]();
    acc = iter.next().value;
  } else {
    iter = iter[Symbol.iterator]();
  }

  return (function recur(acc) {
    let cur;
    while (!(cur = iter.next()).done) {
      const a = cur.value;
      acc = fn(acc, a); // 1
      if (acc instanceof Promise) { // 2
        return acc.then(recur); // 3
      }
    }
    return acc;
  })(acc);
});
```

재귀할 수 있도록 유명 함수 `recur`를 만들고, 일단 함수를 적용해 본 뒤(1) Promise라면(2) then으로 풀어 `recur`를 이어 실행한다(3). 동기 구간은 `acc = fn(acc, a)`로 같은 콜스택에서 처리되고, 비동기를 만나면 그 지점에서만 콜스택이 나뉜다.

```typescript
go(
  1,
  (a) => a + 10, // 동기로 처리
  (a) => Promise.resolve(a + 100),
  (a) => a + 1000, // 동기로 아래 코드와
  (a) => a + 10000, // 하나의 콜스택에서 처리
  console.log,
);
```

다만 첫 값 자체가 Promise면 여전히 잘못된 결과가 나온다 — 첫 값은 Promise 검사 없이 바로 합성되기 때문이다. `go1`(별칭 `lift`)로 첫 `acc`를 풀어서 전달하면 해결된다.

```typescript
const lift = (a, f) => (a instanceof Promise ? a.then(f) : f(a));
const go1 = lift;

export const reduce = curry((fn, acc, iter) => {
  if (!iter) {
    iter = acc[Symbol.iterator]();
    acc = iter.next().value;
  } else {
    iter = iter[Symbol.iterator]();
  }

  return go1(acc, function recur(acc) {
    let cur;
    while (!(cur = iter.next()).done) {
      const a = cur.value;
      acc = fn(acc, a);
      if (acc instanceof Promise) {
        return acc.then(recur);
      }
    }
    return acc;
  });
});
```

reject가 등장하면 이후 함수는 실행되지 않고 끝나며, catch로 처리할 수 있다.

```typescript
go(
  Promise.resolve(1),
  (a) => a + 10,
  (a) => Promise.reject('error~~!!'),
  (a) => a + 1000,  // 실행되지 않음
  (a) => a + 10000, // 실행되지 않음
  console.log,
).catch(console.log); // error~~!!
```

이제 `reduce`와 그 파생 함수들은 Promise를 만나면 **다형적으로** 대응하고, 함수 합성도 안전하게(13장의 Kleisli) 처리한다. Promise를 `then.then.then` 콜백 지옥 해결용으로만 쓰는 것이 아니라, **Promise라는 값을 가지고 원하는 시점에 원하는 방식으로 받아 둔 함수를 실행하는 고차 함수**를 만드는 식으로 응용하는 것이다.

## 5. L.map과 take의 Promise 지원

8장의 지연 함수들도 Promise 값을 만나면 깨진다.

```typescript
go(
  [Promise.resolve(1), Promise.resolve(2), Promise.resolve(3)],
  L.map((a) => a + 10),
  take(2),
  console.log,
); // [ '[object Promise]10', '[object Promise]10' ]
```

`L.map`에 `go1`을 적용한다.

**(기존)**
```typescript
L.map = curry(function* (fn, iter) {
  for (const a of iter) {
    yield fn(a);
  }
});
```

**(go1 적용)**
```typescript
L.map = curry(function* (fn, iter) {
  for (const a of iter) {
    yield go1(a, fn);
  }
});
```

이렇게 하면 Promise 체인으로 연결해 "어떤 값이 될 예정인 값"으로 만들어 줄 수 있다. 이제 `take`가 Promise로 감싸진 값을 풀 수 있어야 한다. 중간까지 만들어 본 코드는 이렇다.

```typescript
export const take = curry((l, iter) => {
  let res = [];

  iter = iter[Symbol.iterator]();
  let cur;
  while (!(cur = iter.next()).done) {
    const a = cur.value;

    if (a instanceof Promise) {
      return a.then((a) => { // 1
        res.push(a);

        if (res.length >= l) {
          return res;
        }

        // 이 부분에서 다시 while문을 돌려줘야 한다.
      });
    }

    res.push(a);

    if (res.length >= l) {
      return res;
    }
  }

  return res;
});
```

Promise면 then으로 꺼내고, 값이 부족하면 다시 while로 돌아가 순회해야 한다. 하지만 Promise 값을 꺼낼 때 이미 `return`(1)을 해버려 함수를 빠져나가므로 되돌아가기 어렵다. 4절의 reduce처럼 **재귀할 부분을 잘라 유명 함수로** 만든다.

```typescript
export const take = curry((l, iter) => {
  let res = [];
  iter = iter[Symbol.iterator]();

  return (function recur() {
    let cur;
    while (!(cur = iter.next()).done) {
      const a = cur.value;

      if (a instanceof Promise) {
        return a.then((a) => { // 4
          res.push(a); // 3

          if (res.length >= l) { // 1
            return res;
          }

          return recur(); // 2
        });
      }

      res.push(a);

      if (res.length >= l) {
        return res;
      }
    }

    return res;
  })();
});
```

코드 정리 — 1·2를 삼항으로 합치고, 3까지 콤마 연산자로 합치면 한 줄이 된다.

```typescript
return a.then((a) => ((res.push(a), res).length >= l ? res : recur()));
```

완성된 코드는 다음과 같다.

```typescript
export const take = curry((l, iter) => {
  let res = [];
  iter = iter[Symbol.iterator]();

  return (function recur() {
    let cur;
    while (!(cur = iter.next()).done) {
      const a = cur.value;

      if (a instanceof Promise) {
        return a.then((a) => ((res.push(a), res).length >= l ? res : recur()));
      }

      res.push(a);

      if (res.length >= l) {
        return res;
      }
    }

    return res;
  })();
});
```

이제 매퍼 함수가 Promise를 리턴하는 경우도 동작한다.

```typescript
go(
  [1, 2, 3],
  L.map((a) => Promise.resolve(a + 10)),
  take(2),
  console.log,
);
```

이 경우 `go1` 입장에서 들어오는 값 자체는 Promise가 아니므로 `f(a)`가 실행되지만, `f(a)`의 결과가 Promise로 평가되므로 take에서 풀려 정상 동작한다. `takeAll`도 take로 만든 함수이므로 함께 정상 동작하고, `map = curry(pipe(L.map, takeAll))`이므로 즉시 평가 map도 비동기를 지원하게 됐다.

```typescript
go(
  [1, 2, 3],
  map((a) => a + 10),
  console.log,
);
```

## 6. L.filter와 nop — Kleisli 합성의 실전

filter에서 지연 평가와 Promise를 함께 지원하려면 **Kleisli 합성**(13장)을 활용해야 한다. 아래 코드는 동작하지 않는다.

```typescript
go(
  [1, 2, 3, 4, 5],
  L.map((a) => Promise.resolve(a * a)),
  L.filter((a) => a % 2),
  take(2),
  console.log,
);
```

`L.map`을 통과한 Promise가 `L.filter`의 보조 함수 인자로 넘어오기 때문이다. 우선 `go1`을 적용해 보자.

**(기존)**
```typescript
L.filter = curry(function* (fn, iter) {
  for (const a of iter) {
    if (fn(a)) yield a;
  }
});
```

**(go1 적용 — 아직 불완전)**
```typescript
L.filter = curry(function* (fn, iter) {
  for (const a of iter) {
    const b = go1(a, fn);
    if (b) yield a;
  }
});
```

이렇게 하면 홀수 두 개가 아니라 `[1, 4]`가 나온다. `b`가 Promise 객체라서 **항상 truthy**이기 때문이다. 다음과 같이 수정한다.

```typescript
const nop = Symbol('nop');
L.filter = curry(function* (fn, iter) {
  for (const a of iter) {
    const b = go1(a, fn);

    if (b instanceof Promise) {
      yield b.then((b) => {
        return b ? a : Promise.reject(nop);
      });
    } else if (b) {
      yield a;
    }
  }
});
```

- `b`가 Promise면 풀어서 판단한다. 푼 값이 참이면 `a`를 리턴한다(여기서 `a`는 풀리지 않은 Promise일 수 있지만 다른 곳(take)에서 풀어 쓸 것이므로 그대로 보내도 된다).
- 푼 값이 거짓이면 **아무 일도 일어나지 않게** 해야 한다. 여기서 Kleisli 합성을 쓴다 — `Promise.reject`를 하면 이후 값은 다음 코드로 흘러가지 않는다. 다만 "아무 일도 하지 않길 바라는 reject"인지 "정말 에러가 난 reject"인지 구별해야 하므로 `Symbol('nop')`이라는 구분자를 만들어, catch에서 nop이 오면 아무 일도 하지 않도록 처리한다.

take에서 nop 에러를 통과시키는 코드를 더한다.

```typescript
export const take = curry((l, iter) => {
  let res = [];
  iter = iter[Symbol.iterator]();

  return (function recur() {
    let cur;
    while (!(cur = iter.next()).done) {
      const a = cur.value;

      if (a instanceof Promise) {
        return a
          .then((a) => {
            res.push(a);

            return res.length >= l ? res : recur();
          })
          .catch((e) => (e === nop ? recur() : Promise.reject(e)));
      }

      res.push(a);

      if (res.length >= l) {
        return res;
      }
    }

    return res;
  })();
});
```

catch해서 에러가 `nop`이면 다시 순회를 재개(`recur()`)하고, 아니면 진짜 에러이므로 다시 reject해 아래로 전파한다. then이 아무리 많아도 결국 catch로 모인다.

## 7. reduce에서 nop 지원

기존 reduce로 아래 로직을 실행하면 Promise를 지원하지 못한다.

```typescript
go(
  [1, 2, 3, 4],
  L.map((a) => Promise.resolve(a * a)),
  L.filter((a) => Promise.resolve(a % 2)),
  reduce(add),
  console.log,
); // 1[object Promise][object Promise][object Promise]
```

4절의 reduce는 첫 값(acc)의 Promise만 풀었지, **iter로 들어오는 각 요소가 Promise인 경우**를 처리하지 못한다. 문제 지점은 `acc = fn(acc, a);` 한 줄이다. 해결하려는 일을 함수로 격리하면 문제가 쉬워진다.

```typescript
// 요소가 Promise면 풀어서 누적하는 reduceF
const reduceF = (acc, a, f) =>
  a instanceof Promise ? a.then((a) => f(acc, a)) : f(acc, a);

export const reduce = curry((fn, acc, iter) => {
  if (!iter) {
    iter = acc[Symbol.iterator]();
    acc = iter.next().value;
  } else {
    iter = iter[Symbol.iterator]();
  }

  return go1(acc, function recur(acc) {
    let cur;
    while (!(cur = iter.next()).done) {
      acc = reduceF(acc, cur.value, fn);
      // 참고로 recur(acc)의 acc는 항상 promise를 푼 값을 받기 때문에, a만 체크해 주면 된다.
      if (acc instanceof Promise) {
        return acc.then(recur);
      }
    }
    return acc;
  });
});
```

`reduceF`에 nop 에러 처리를 더한다. then의 두 번째 인자(reject 핸들러)를 이용하는 방법이다.

```typescript
const nop = Symbol('nop');

const reduceF = (acc, a, f) =>
  a instanceof Promise
    ? a.then(
        (a) => f(acc, a),
        (e) => (e === nop ? acc : Promise.reject(e)),
      )
    : f(acc, a);
```

- **에러가 nop이면**: "의도된 예외"이므로 무시하고 현재까지의 누적값(acc)을 그대로 반환 → 이후 합성(체인, reduce)을 계속한다.
- **에러가 nop이 아니면**: 의도한 것이 아니므로 더 이상 합성하지 않고 `Promise.reject`로 에러를 아래로 전파한다(즉시 종료·에러 전파 — throw와 동일한 효과).

한 가지 더 정리하면, 초깃값 생략 시 `iter.next()`로 첫 값을 꺼내는 부분도 비동기가 일어날 수 있으므로 문장이 아닌 표현식으로 안전하게 합성하면 좋다. "head를 뽑고, head가 뽑힌 나머지 이터레이터로 reduce한다"로 읽으면 된다.

```typescript
export const head = (iter) => go1(take(1, iter), ([a]) => a);

export const reduce = curry((fn, acc, iter) => {
  if (!iter) {
    return reduce(fn, head((iter = acc[Symbol.iterator]())), iter);
  }

  iter = iter[Symbol.iterator]();

  return go1(acc, function recur(acc) {
    let cur;
    while (!(cur = iter.next()).done) {
      acc = reduceF(acc, cur.value, fn);
      if (acc instanceof Promise) {
        return acc.then(recur);
      }
    }
    return acc;
  });
});
```

애플리케이션 레벨 코드에서 늘 이렇게까지 할 필요는 없지만, 사내에서 많이 재사용되거나 라이브러리로 만든 함수라면 비동기 상황까지 다형적으로 처리해 줄 필요가 있다.

## 8. 지연 평가 + Promise의 효율성

이제 지연·즉시 평가 함수 모두가 동기·비동기 상황을 지원한다. 효율을 확인해 보자.

```typescript
go(
  [1, 2, 3, 4, 5, 6, 7, 8],
  L.map(
    (a) => new Promise((resolve) => setTimeout(() => resolve(a * a), 1000)),
  ),
  L.filter(
    (a) => new Promise((resolve) => setTimeout(() => resolve(a % 2), 1000)),
  ),
  take(2),
  console.log,
);
```

1부터 8까지 전체를 순회하는 것이 아니라 **1부터 3까지만** 순회한다(2는 filter까지만 가고 map의 결과가 걸러짐). 필요한 상황에만 비동기 작업을 실행하므로, 지연 평가가 비동기 세계에서 곧바로 **부하 절감**으로 이어진다.

## 9. 지연된 함수열을 병렬적으로 평가하기 — C.reduce, C.take, C.map

### 9.1 왜 병렬 평가인가

자바스크립트가 싱글 스레드라서 병렬 프로그래밍이 필요 없다는 것은 오해다. 자바스크립트는 **로직 제어를** 싱글 스레드로 비동기적으로 할 뿐, 병렬 처리가 필요한 상황은 얼마든지 있다. PostgreSQL 같은 DB에 쿼리들을 병렬로 출발시켜 결과를 한 번에 받거나, Redis에 여러 키를 동시에 조회하거나, Node.js가 이미지 처리 명령을 네트워크·IO로 외부에 보내고 시점만 관리하는 경우 — **작업을 동시에 출발시켰다가 하나의 로직으로 귀결시키는** 제어가 필요하다.

```typescript
const delay1000 = (a) =>
  new Promise((resolve) =>
    setTimeout(() => {
      console.log('hi! concurrent.');
      resolve(a);
    }, 500),
  );

go(
  [1, 2, 3, 4, 5],
  L.map((a) => delay1000(a * a)),
  L.filter((a) => a % 2),
  reduce(add),
  console.log,
);
```

이 코드는 지연성이 있으므로 reduce 이전까지 함수들이 대기하다가, 값이 필요해질 때 **하나씩(세로로)** 평가된다. 즉 요소마다 대기 시간이 누적된다. 지금은 reduce가 값을 하나씩 기다리지만, 동시에 출발시킨 후 값을 더할 수 있다면 부하는 생겨도 최종 결과는 훨씬 빨라진다.

이때 필요한 것이 **동시성(Concurrency)으로 동작하는 reduce**다. 함수형 프로그래밍에서는 상태나 외부 값에 의존하지 않으므로 각 라인이 개별적으로 동작해도 정상 동작하고, 그만큼 병렬 코드를 만드는 것이 단순해진다.

```typescript
C.reduce = curry((fn, acc, iter) =>
  iter ? reduce(fn, acc, [...iter]) : reduce(fn, [...acc]),
);
```

핵심은 전개 연산자 `[...iter]`다 — 지연된 이터레이터를 **즉시 소비**해 모든 대기 함수(L.map, L.filter)를 한꺼번에 출발시키고, 그 다음 reduce가 순회하며 앞에서부터 값을 꺼내(비동기 제어) 누적한다.

```typescript
console.time('')
go(
  [1, 2, 3, 4, 5],
  L.map((a) => delay1000(a * a)),
  L.filter((a) => a % 2),
  C.reduce(add),
  console.log,
  (_) => console.timeEnd(''),
); // 약 0.5~1초 뒤 전체 평가 됨.
```

기존 reduce가 첫 번째 값의 전체 대기열을 마친 후 2로 넘어갔다면, `C.reduce`는 모든 함수열을 실행해 놓고 비동기 제어로 앞에서부터 누적한다. delay 작업이 외부 환경에서 병렬 처리되어도 되는 상황이라면 `C.reduce`로 바꾸는 것만으로 효율적인 프로그래밍이 된다.

### 9.2 Uncaught 에러 로그 문제와 catchNoop

그런데 아래처럼 filter 뒤에 추가 평가가 있으면, 값은 정상적으로 나오지만 콘솔에 에러가 출력된다 — `Uncaught (in promise) Symbol(nop)`.

```typescript
go(
  [1, 2, 3, 4, 5],
  L.map((a) => delay1000(a * a)),
  L.filter((a) => a % 2),
  L.map((a) => delay1000(a * a)),
  C.reduce(add),
  console.log,
);
```

자바스크립트의 특성상 콜스택에 `Promise.reject`로 평가되는 코드가 있으면 그 시점에 에러 로그가 출력되며, 나중에 catch해도 이미 출력된 로그는 지울 수 없다.

```typescript
const p = Promise.reject('hi'); // Uncaught (in promise) hi
p.catch(a => console.log('해결: ', a)); // 이 시점은 이미 에러 로그가 찍힌 후다.
```

개발자가 인지하고 있는 nop 에러는 이후 콜스택에서 캐치할 것이므로, "알고 있으니 로그를 찍을 필요 없다"고 Promise에 미리 알려주면 된다. 여기서 중요한 테크닉 — **catch를 해서 반환된 Promise를 전달하는 것이 아니라, catch만 임시로 걸어 두고 원본 Promise를 전달한다.**

```typescript
let p = Promise.reject('hi');
p.catch(a => `${a} catch`); // p에 재할당하지 않음 — 에러 로그만 억제됨

p.catch(a => `${a} re catch`); // 원하는 시점에 다시 catch 가능
```

만약 `p = p.catch(...)`처럼 catch까지 적용된 Promise를 전달하면 이미 처리가 끝난 값이라 다시 catch할 수 없다. catch를 걸어두기만 하면 p는 reject 상태를 유지한 채 에러 로그만 억제되고, 원하는 시점에 캐치할 수 있다.

이를 함수로 정리한다.

```typescript
function noop() {}
const catchNoop = ([...arr]) => (
  arr.forEach((a) => (a instanceof Promise ? a.catch(noop) : a)), arr
);

C.reduce = curry((fn, acc, iter) =>
  iter ? reduce(fn, acc, catchNoop(iter)) : reduce(fn, catchNoop(acc)),
);
C.take = curry((l, iter) => take(l, catchNoop(iter)));
```

`C.take`도 같은 방식으로 전체 대기열을 병렬 실행한다. take와 C.take의 차이는 최적화 방향의 차이다.

**C.reduce — 최대한 많은 자원으로 빠르게:**
```typescript
go(
  [1, 2, 3, 4, 5, 6, 7, 8, 9],
  L.map((a) => delay1000(a * a)),
  L.filter((a) => a % 2),
  L.map((a) => delay1000(a * a)),
  C.take(2),
  C.reduce(add),
  console.log,
);
```

**reduce — 명령을 덜 실행시켜 부하를 줄이는 방향:**
```typescript
go(
  [1, 2, 3, 4, 5, 6, 7, 8, 9],
  L.map((a) => delay1000(a * a)),
  L.filter((a) => a % 2),
  L.map((a) => delay1000(a * a)),
  C.take(2),
  reduce(add),
  console.log,
);
```

**이터러블 중심으로 사고하면, "하나씩" 평가할지 "병렬적으로" 평가할지를 선언적으로 선택·관리할 수 있다.** 병렬 프로그래밍을 안전하고 쉽게, 선언적으로 다루게 된 것이다.

### 9.3 특정 라인만 병렬 평가 — C.map, C.filter

지금까지는 파이프라인의 끝(reduce·take)에서 앞의 함수열 전체를 병렬 실행할지 결정했다. `C.map`·`C.filter`는 **특정 함수 라인만** 병렬적으로 평가한다. `C.takeAll`을 만들어 두면 구현이 간단하다.

```typescript
C.takeAll = C.take(Infinity);

C.map = curry(pipe(L.map, C.takeAll));
C.filter = curry(pipe(L.filter, C.takeAll));
```

```typescript
C.map((a) => delay1000(a * a), [1, 2, 3]).then(console.log); // [1, 4, 9]
```

즉시 평가(map) / 지연 평가(L.map) / 병렬 평가(C.map), 그리고 동기·비동기 지원 — 이 조각들을 조합해 **원하는 평가 전략을 세우는 식**으로 코딩할 수 있다.

## 10. AsyncIterator, AsyncGenerator, toAsync

이제 같은 문제(동기·비동기를 하나의 파이프라인으로)를 타입 시스템으로 푸는 멀티패러다임 세대의 해법을 보자. 자바스크립트는 AsyncIterator, AsyncIterable, AsyncGenerator 프로토콜로 비동기 작업의 순차 처리를 지원한다.

```typescript
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

5장의 이터레이션 프로토콜과 구조가 같고, 차이는 `next()`가 **Promise를 반환**한다는 것뿐이다. AsyncGenerator는 `async function*`으로 정의한다.

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

`toAsync`는 동기 Iterable(또는 Promise가 포함된 Iterable)을 AsyncIterable로 변환한다.

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

## 11. 동기와 비동기를 동시에 지원하는 규약

### 11.1 mapAsync와 filterAsync

`mapSync`(7장의 map)가 Iterable을 다룬다면 `mapAsync`는 AsyncIterable을 다룬다.

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

사실상 `mapSync`와 `mapAsync`는 코드와 값이 흐르는 방식이 완전히 동일하다 — 비동기 이터러블을 다룰 수 있게 됐을 뿐이다. AsyncGenerator로 더 간결하게 구현할 수 있다.

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

주목할 점: `filterAsync`는 `await f(value)`로 조건을 **풀어서** 판단한다 — 6절에서 nop으로 풀었던 "Promise는 항상 truthy" 문제를, 비동기 세계를 분리함으로써 자연스럽게 해결한 것이다.

### 11.2 오버로드로 통합하기 — 규약으로서의 toAsync

`toAsync`는 런타임 변환일 뿐 아니라 **컴파일 타임 선언**이다 — "이제부터 비동기적으로 값을 다루겠다"를 타입으로 알리는 것이다. 함수 오버로드로 동기·비동기를 하나의 함수로 통합한다.

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

`filter`도 동일한 패턴이다. 특히 **동기 이터러블에 비동기 조건 함수를 쓰면 타입 에러**가 발생하는데, 이는 의도된 결과다 — `Promise.resolve(true)`든 `false`든 모두 객체라서 truthy로 평가되므로, 결과를 꺼내 보지 않고는 제대로 평가할 수 없기 때문이다(6절에서 `[1, 4]`가 나왔던 바로 그 문제를 타입이 컴파일 타임에 막아준다).

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

## 12. FxIterable과 FxAsyncIterable

타입 시스템 + 비동기 함수형 함수 + 클래스를 결합하면 비동기 작업을 구조화해 일관성 있게 관리할 수 있다. `toAsync` 메서드가 `FxIterable` 체인을 `FxAsyncIterable` 체인으로 이어준다.

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

타입 시스템이 비동기 로직을 검증해 준다 — `toAsync` 없이 비동기 필터링을 시도하면 타입 오류가 발생한다.

```typescript
const iter2 = fx(naturals(4))
  .filter(a => delay(100, isOdd(a))) // 타입 오류 발생 (TS2322)
  .map(a => a.toFixed());
// TS2322: Type 'Promise<boolean>' is not assignable to type 'boolean'
```

reduce도 오버로드로 동기(Acc 반환)·비동기(Promise<Acc> 반환)를 통합한다.

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

## 13. 두 세대의 비교 — nop 방식 vs toAsync 방식

이 장에서 같은 문제를 두 가지 방식으로 풀었다. 접근이 다르므로 둘 다 알아둘 가치가 있다.

| 관점 | nop 방식 (es6/fxjs 세대) | toAsync 방식 (멀티패러다임/FxTS 세대) |
|---|---|---|
| 세계관 | **하나의 이터레이터 파이프라인**에 Promise를 값으로 흘림 | 동기(Iterable)와 비동기(AsyncIterable) **세계를 분리**하고 toAsync로 명시적 전환 |
| filter의 거짓 신호 | `Promise.reject(Symbol('nop'))` — Kleisli 합성으로 "없음"을 전파 | `await f(value)` — 비동기 세계에서 조건을 풀어 판단 |
| 잘못된 사용 방지 | 런타임 규약(개발자가 nop을 처리해야 함) | **컴파일 타임 타입 에러**(TS2322)로 차단 |
| 동기·비동기 통합 | `instanceof Promise` 런타임 검사(go1) | 함수 오버로드 + `isIterable` 타입 가드 |
| 강점 | 동적 JS에서 간결·다형적, 파이프 중간 어디서든 Promise 허용 | 타입 추론·검증, 의도가 코드(toAsync)에 드러남 |

> **핵심 통찰**: nop 방식은 "모든 값이 Promise일 수 있다"는 가정 위에서 런타임 규약으로 안전을 만들고, toAsync 방식은 "동기와 비동기는 다른 타입"이라는 선언 위에서 컴파일 타임 검증으로 안전을 만든다. 후자가 타입스크립트 시대의 정답에 가깝지만, 전자를 직접 구현해 본 경험이 후자의 설계(왜 toAsync가 필요한가, 왜 동기 filter에 비동기 조건이 금지되는가)를 이해하게 해준다.

## 요약

- **Promise는 생성 즉시 실행**된다 — 실행을 지연하려면 `() => Promise`로 감싸고, 지연 평가 map과 결합하면 부하 조절(`executeWithLimit`)이 선언적으로 풀린다.
- `go`/`pipe`/`reduce`의 비동기 지원 핵심은 **유명 함수 recur** — 동기 구간은 한 콜스택에서, Promise를 만난 지점에서만 then으로 이어 다형적으로 처리한다.
- `L.filter`의 비동기 지원은 **Kleisli 합성**의 실전이다 — 거짓 판정을 `Promise.reject(nop)`로 전파하고, take·reduce가 nop이면 재개, 아니면 재전파한다.
- **catchNoop 테크닉**: catch한 Promise를 전달하지 말고, catch를 걸어두기만 한 원본을 전달한다 — Uncaught 로그는 억제되고 나중에 다시 catch할 수 있다.
- `C.reduce`/`C.take`/`C.map`은 전개 연산자로 지연 함수열을 **즉시 소비해 병렬로 출발**시킨다 — 하나씩(세로) 평가와 병렬 평가를 선언적으로 선택한다.
- **AsyncIterator/toAsync/FxAsyncIterable**은 같은 문제의 타입 시스템 해법이다 — toAsync가 동기→비동기 전환을 선언하고, 오버로드와 타입 가드가 동기·비동기를 하나의 API로 통합하며, 잘못된 조합은 컴파일 타임에 차단된다.

## 다른 챕터와의 관계

- **3장**: `go`/`pipe`/`curry`가 이 장에서 비동기까지 다형적으로 확장됐다.
- **8장**: L.map/L.filter/take의 지연 구조가 이 장의 전제다. "지연 vs 즉시"에 "병렬(C.*)"이 추가됐다.
- **12장**: `go1`(lift)이 파이프라인 전체로 확장됐고, "Promise를 함수로 감싼다"가 지연성의 시작이었다.
- **13장**: nop 기법이 Kleisli 합성의 응용임을 확인했다.
- **15장**: 이 장의 파이프라인들이 async/await·try/catch와 어떻게 협력하는지, 에러 핸들링 관점으로 이어진다.
- **16장**: FXTS의 `concurrent(n)`이 C.* 계열의 실전(라이브러리) 형태로 등장한다. **17장**: TaskPool이 같은 동시성 문제를 클래스(OOP)로 확장한다.
