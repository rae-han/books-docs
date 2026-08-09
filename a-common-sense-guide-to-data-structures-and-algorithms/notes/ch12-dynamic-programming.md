# Chapter 12: Dynamic Programming (동적 프로그래밍)

## 핵심 질문

우아해 보이는 재귀 함수가 왜 O(2ᴺ)이라는 최악의 카테고리로 굴러떨어지는가? "하위 문제 중첩"이란 무엇이며, 해시 테이블 하나로 O(2ᴺ)을 O(N)으로 바꾸는 메모이제이션은 어떻게 동작하는가?

---

## 1. 불필요한 재귀 호출

재귀는 문제를 풀지만, 제대로 쓰지 않으면 O(2ᴺ) 같은 최악의 빅 오를 만드는 주범이 된다. 배열 최댓값을 찾는 재귀 함수를 보자:

```typescript
function max(array: number[]): number {
  if (array.length === 1) {
    return array[0];  // 기저 조건
  }
  // ⚠️ max()가 두 번 호출된다!
  if (array[0] > max(array.slice(1))) {
    return array[0];
  } else {
    return max(array.slice(1));
  }
}
```

조건문 앞뒤로 `max(array.slice(1))`이 **두 번** 나온다. `max([1,2,3,4])`의 호출 사슬을 바닥부터 따라가 보면: `max([4])`는 1번이면 충분한데 8번 호출되고, `max([3,4])`는 4번, 전체 호출은 **15번**에 이른다. 함수 첫 줄에 `console.log("RECURSION")`을 넣어 보면 직접 확인할 수 있다.

## 2. 빅 오를 위한 작은 개선

해법은 단순하다 — **한 번만 호출하고 결과를 변수에 저장**한다:

```typescript
function max(array: number[]): number {
  if (array.length === 1) {
    return array[0];
  }
  // 나머지 배열의 최댓값을 한 번만 계산해 저장
  const maxOfRemainder = max(array.slice(1));
  return array[0] > maxOfRemainder ? array[0] : maxOfRemainder;
}
```

호출이 15번에서 **4번**으로 줄었다.

## 3. 재귀의 효율성

개선된 max는 원소 N개에 대해 N번 호출 → **O(N)** (루프 없는 O(N)이다 — 빅 오 원리는 재귀에도 똑같이 적용된다). 반면 원래 함수는 호출 횟수가 1, 3, 7, 15, 31… — 데이터가 1 커질 때마다 약 2배씩 늘어나는 **O(2ᴺ)** 패턴이다.

> **핵심 통찰**: **불필요한 재귀 호출을 피하는 것이 재귀를 빠르게 만드는 핵심 비결이다.** "결과를 변수에 저장"이라는 사소해 보이는 변화가 O(2ᴺ)을 O(N)으로 바꾼다. 자신을 두 번 호출하는 함수를 보면 머릿속에 경고음이 울려야 한다.

## 4. 하위 문제 중첩 — 피보나치

**피보나치 수열**(0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55…)의 N번째 수:

```typescript
function fib(n: number): number {
  if (n === 0 || n === 1) {
    return n;                        // 기저 조건
  }
  return fib(n - 2) + fib(n - 1);    // ⚠️ 자신을 두 번 호출
}
```

매우 간결하지만 자신을 두 번 호출한다 — 경고음! fib(6)의 호출 트리를 그리면 fib(3)이 3번, fib(2)가 5번… 전형적인 O(2ᴺ)이다.

그런데 이번엔 max처럼 "변수에 저장"만으로 안 된다. **fib(n−2)와 fib(n−1) 둘 다** 계산해야 하고, 한쪽 결과가 다른 쪽을 대신하지 못하기 때문이다. 이것이 **하위 문제 중첩(*overlapping subproblems - 여러 하위 문제가 같은 더 작은 하위 문제들을 중복 호출하는 상황*)**이다 — fib(4)와 fib(5)가 둘 다 fib(3)을 호출하는 식으로, 같은 계산이 반복된다.

## 5. 메모이제이션을 통한 동적 프로그래밍

**동적 프로그래밍(*dynamic programming - 하위 문제가 중첩되는 재귀 문제를 최적화하는 절차*)**이 해법이다("동적"이라는 단어에 의미를 두지 말자 — 동적인 요소는 없다). 두 기법 중 첫째가 **메모이제이션(*memoization - 먼저 계산한 함수 결과를 해시 테이블에 기억해 두어 재귀 호출을 줄이는 기법*)**이다.

fib(3)을 처음 계산하면 결과를 해시 테이블에 저장한다: `{3: 2}`. 이후 fib(4)가 fib(3)을 호출하려 할 때 **먼저 해시 테이블을 확인**하고, 있으면 재계산 없이 그 값을 쓴다. **하지 않았던 계산만 수행하게 되는 것**이다.

해시 테이블은 어떻게 모든 재귀 호출이 공유할까? — **두 번째 인자로 전달**한다(Ch11의 추가 인자 비법). 해시 테이블은 메모리 내 객체라 호출 사이에서, 심지어 호출 스택을 되감을 때도 같은 것이 전달된다.

```typescript
function fib(n: number, memo: Record<number, number> = {}): number {
  if (n === 0 || n === 1) {
    return n;
  }
  // 이미 계산했는지 memo를 먼저 확인
  if (!memo[n]) {
    // 없을 때만 재귀 계산 후 저장
    memo[n] = fib(n - 2, memo) + fib(n - 1, memo);
  }
  return memo[n];
}
```

호출 횟수는 N에 대해 (2N)−1 — 상수를 버리면 **O(N)**. O(2ᴺ)에서의 극적인 개선이다. 알고리즘의 핵심(fib(n−2)+fib(n−1))은 그대로이고, "이미 계산한 것은 다시 계산하지 않는다"만 더해졌다.

## 6. 상향식을 통한 동적 프로그래밍

두 번째 기법 **상향식(bottom-up)**은 사실 "재귀 대신 루프로 푼다"는 뜻이다. 반복도 중첩 하위 문제의 중복 호출을 없애는 엄연한 방법이므로 동적 프로그래밍으로 간주된다.

```typescript
function fib(n: number): number {
  if (n === 0) {
    return 0;
  }
  let a = 0;  // 수열의 첫 번째 수
  let b = 1;  // 수열의 두 번째 수
  for (let i = 1; i < n; i++) {
    const temp = a;
    a = b;
    b = temp + a;  // 다음 수 = 앞 두 수의 합
  }
  return b;
}
```

1부터 N까지의 단순 루프 → **O(N)**. 메모이제이션과 같은 효율이다.

### 메모이제이션 vs 상향식

| 기준 | 메모이제이션 | 상향식 |
|------|-------------|--------|
| 접근 | 재귀 유지 + 결과 캐싱 | 재귀 제거(루프) |
| 오버헤드 | 호출 스택 + 해시 테이블 메모리 | 없음(최소) |
| 적합한 경우 | 재귀가 훨씬 직관적인 문제 | 반복도 충분히 직관적인 문제 |

> **핵심 통찰**: 재귀는 메모이제이션을 써도 호출 스택·해시 테이블만큼 **추가 메모리 오버헤드**가 있다. 따라서 **재귀가 매우 직관적이지 않은 이상 일반적으로 상향식이 낫고**, 재귀가 확실히 직관적이면(계단 문제를 루프로 푼다고 상상해 보라) 재귀 + 메모이제이션을 쓴다.

---

## 요약

- 재귀의 최대 함정: **불필요한 중복 호출.** 같은 재귀 호출이 코드에 두 번 나오면 O(2ᴺ)행이다
- 1차 처방: **한 번 호출해 변수에 저장** (max 예제 — O(2ᴺ)→O(N))
- 그걸로 안 되는 경우가 **하위 문제 중첩**(피보나치) — 서로 다른 하위 문제들이 같은 더 작은 하위 문제를 중복 계산
- **동적 프로그래밍** = 하위 문제 중첩의 최적화. 기법 ① **메모이제이션**(해시 테이블 캐시를 인자로 공유) ② **상향식**(루프로 전환)
- 둘 다 O(2ᴺ)→O(N). 선택 기준은 **직관성 vs 메모리 오버헤드**
- 빅 오 분석은 루프뿐 아니라 재귀 호출 횟수에도 그대로 적용된다

## 연습 문제 (해답 예시)

1. **합이 100을 넘게 만드는 수를 제외하고 합산하는 함수의 불필요한 재귀 제거** — `addUntil100(나머지)`가 세 번 등장하므로 한 번만 호출해 변수에 저장한다:

   ```typescript
   function addUntil100(array: number[]): number {
     if (array.length === 0) {
       return 0;
     }
     const sumOfRemainder = addUntil100(array.slice(1));  // 한 번만!
     if (array[0] + sumOfRemainder > 100) {
       return sumOfRemainder;
     }
     return array[0] + sumOfRemainder;
   }
   ```

2. **골롬 수열 메모이제이션** — memo 해시 테이블을 인자로 추가하고, 계산 전 확인·계산 후 저장한다:

   ```typescript
   function golomb(n: number, memo: Record<number, number> = {}): number {
     if (n === 1) {
       return 1;
     }
     if (!memo[n]) {
       memo[n] = 1 + golomb(n - golomb(golomb(n - 1, memo), memo), memo);
     }
     return memo[n];
   }
   ```

3. **유일 경로 메모이제이션** — 키가 두 값(rows, columns)이므로 `[rows, columns]` 조합을 키로 쓴다:

   ```typescript
   function uniquePaths(
     rows: number, columns: number,
     memo: Record<string, number> = {},
   ): number {
     if (rows === 1 || columns === 1) {
       return 1;
     }
     const key = `${rows},${columns}`;
     if (!memo[key]) {
       memo[key] = uniquePaths(rows - 1, columns, memo)
                 + uniquePaths(rows, columns - 1, memo);
     }
     return memo[key];
   }
   ```

## 다른 챕터와의 관계

- **Ch10·Ch11 (재귀)**: 재귀 3부작의 완결 — 이해(10), 작성(11), 최적화(12)
- **Ch7 (일상적인 코드 속 빅 오)**: 암호 크래커에서 처음 본 O(2ᴺ)이 재귀에서 어떻게 발생하는지 규명됐다
- **Ch8 (해시 테이블)**: 메모이제이션의 캐시가 바로 해시 테이블 — O(1) 룩업이 전제 조건이다
- **Ch19 (공간 제약)**: 호출 스택·memo 테이블의 메모리 비용이 공간 복잡도로 정식 분석된다
