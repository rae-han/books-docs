# Chapter 00: JavaScript/TypeScript 기본 문법 (코딩 테스트용)

> 이 챕터는 책의 부록 A "코딩 테스트를 위한 파이썬 문법"을 **JavaScript/TypeScript 환경**으로 옮긴 버전이다. 책의 모든 알고리즘 예제는 Python으로 작성되었지만, 본 학습 노트에서는 TypeScript를 주 언어로 삼는다.

## 핵심 질문

- 코딩 테스트에서 자주 쓰이는 JS/TS 자료형과 메서드는 무엇인가?
- 각 자료구조 연산의 **시간복잡도**는 얼마인가?
- Python의 `itertools`, `heapq`, `bisect` 같은 표준 라이브러리는 JS에 없다 — 어떻게 대체하는가?
- 백준 / 프로그래머스 환경에서 입출력은 어떻게 처리하는가?

## 1. 수 자료형

### 정수 / 실수 / 부동소수점

JS의 `number`는 모두 **IEEE 754 64-bit double** 하나로 처리된다 (Python처럼 정수/실수가 분리되지 않음). 안전 정수 범위는 `Number.MAX_SAFE_INTEGER` = 2^53 - 1.

```ts
const a = 1e9;        // 10억 (지수 표기)
const b = 752.5e1;    // 7525
const c = 3954e-3;    // 3.954

// 정수 범위 초과 시 BigInt 사용
const big = 9007199254740993n;  // 'n' 접미사
const bigSum = big + 1n;
```

### 부동소수점 정확도 문제

```ts
const x = 0.3 + 0.6;
console.log(x);          // 0.8999999999999999
console.log(x === 0.9);  // false ❌

// 해결법 1: 반올림 후 비교
console.log(Number(x.toFixed(4)) === 0.9);  // true ✅
console.log(Math.abs(x - 0.9) < 1e-9);      // true ✅
```

> **핵심 통찰**: 코딩 테스트에서 실수형을 직접 비교하지 말 것. **`Math.abs(a - b) < 1e-9`** 같은 epsilon 비교를 쓴다.

### 수 연산

```ts
const a = 7, b = 3;

console.log(a / b);          // 2.3333... (Python과 같음)
console.log(a % b);          // 1 (나머지)
console.log(Math.floor(a / b));  // 2 (몫, Python의 //)
console.log(Math.trunc(a / b));  // 2 (음수일 때 floor와 다름)
console.log(a ** b);         // 343 (거듭제곱)
```

> **자주 하는 실수**: Python `int(A / B)`는 0 방향 절단(truncate) — JS에서는 `Math.trunc(a / b)` 또는 `~~(a / b)`. `Math.floor`는 음수에서 결과가 다르다 (`Math.floor(-1.5) === -2`, `Math.trunc(-1.5) === -1`).

## 2. 배열 (Python의 list 대체)

### 생성

```ts
// 리터럴
const a: number[] = [1, 2, 3, 4, 5];

// 빈 배열
const empty: number[] = [];

// 크기 N, 모두 0
const n = 10;
const zeros = Array(n).fill(0);                       // [0,0,...,0]

// 2D 배열 (n × m, 모두 0) — 주의: fill은 참조 공유 X
const rows = 3, cols = 4;
const grid = Array.from({ length: rows }, () => Array(cols).fill(0));

// ❌ 잘못된 2D 초기화 — 모든 행이 같은 배열 참조
const wrong = Array(rows).fill(Array(cols).fill(0));
wrong[0][0] = 1;
console.log(wrong);  // 모든 행의 [0]이 1로 바뀜!
```

### 인덱싱과 슬라이싱

```ts
const a = [1, 2, 3, 4, 5, 6, 7, 8, 9];

// 음수 인덱싱 (Python의 a[-1]) → JS는 a.at() 또는 a[a.length - 1]
console.log(a.at(-1));          // 9
console.log(a.at(-3));          // 7

// 슬라이싱 (Python의 a[1:4]) → arr.slice(start, end)
console.log(a.slice(1, 4));     // [2, 3, 4]
console.log(a.slice(-3));       // [7, 8, 9]
```

### "리스트 컴프리헨션" 대체

Python: `[i for i in range(20) if i % 2 === 1]`
JS/TS:

```ts
// 0~19 중 홀수만
const odds = Array.from({ length: 20 }, (_, i) => i).filter((i) => i % 2 === 1);
// [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]

// 1~9의 제곱
const squares = Array.from({ length: 9 }, (_, i) => (i + 1) ** 2);
// [1, 4, 9, 16, 25, 36, 49, 64, 81]
```

### 주요 메서드와 시간복잡도

| 메서드 | 동작 | 시간복잡도 |
|---|---|---|
| `arr.push(x)` | 끝에 추가 | **O(1)** |
| `arr.pop()` | 끝에서 제거 | **O(1)** |
| `arr.unshift(x)` | 앞에 추가 | ⚠️ **O(N)** |
| `arr.shift()` | 앞에서 제거 | ⚠️ **O(N)** |
| `arr.splice(i, 1)` | 중간 제거/삽입 | **O(N)** |
| `arr.slice(s, e)` | 부분 복사 | **O(end-start)** |
| `arr.indexOf(x)` | 선형 탐색 | **O(N)** |
| `arr.includes(x)` | 포함 여부 | **O(N)** |
| `arr.sort(cmp)` | 정렬 | **O(N log N)** |
| `arr.reverse()` | 뒤집기 | **O(N)** |

> **함정**: `unshift` / `shift`가 O(N)이다. **큐(Queue)** 가 필요하면 배열의 `shift`를 그대로 쓰면 O(N²) 위험이 있어서 인덱스 포인터를 직접 관리하거나 양방향 큐(Deque)를 별도로 구현해야 한다.

### 정렬 — 디폴트 비교 함수의 함정

`Array.prototype.sort`의 디폴트는 **각 원소를 문자열로 변환한 뒤 사전순 비교**다. 숫자에 그대로 쓰면 의도와 다른 결과가 나온다.

```ts
const arr = [10, 2, 33, 4];

arr.sort();
console.log(arr);  // ❌ [10, 2, 33, 4]
// 이유: "10" < "2" < "33" < "4" (사전순으로 첫 글자 비교)

[10, 2, 33, 4].sort((a, b) => a - b);  // ✅ [2, 4, 10, 33] (오름차순)
[10, 2, 33, 4].sort((a, b) => b - a);  // ✅ [33, 10, 4, 2] (내림차순)
```

> **항상 비교 함수를 명시하라**. `arr.sort()`만 쓰면 거의 100% 버그.

## 3. 문자열

JS 문자열은 **불변(immutable)**. Python과 동일.

```ts
const s = "Hello, World!";

// 길이
console.log(s.length);        // 13

// 인덱스 접근
console.log(s[0]);            // 'H'
console.log(s.at(-1));        // '!'

// 자르기
console.log(s.slice(0, 5));   // 'Hello'
console.log(s.substring(7));  // 'World!'

// 변환
console.log(s.toUpperCase()); // 'HELLO, WORLD!'
console.log(s.toLowerCase()); // 'hello, world!'

// 검색
console.log(s.includes("World"));    // true
console.log(s.indexOf("World"));     // 7
console.log(s.startsWith("Hello"));  // true

// 분리/결합
console.log(s.split(", "));          // ['Hello', 'World!']
console.log(["a", "b", "c"].join("-")); // 'a-b-c'

// 반복
console.log("ab".repeat(3));  // 'ababab'

// 문자열 → 배열 → 문자열 (가공할 때)
const chars = [...s];          // 또는 s.split('')
chars.reverse();
const reversed = chars.join("");
```

### 문자 ↔ 코드 변환

```ts
"A".charCodeAt(0);            // 65
String.fromCharCode(65);      // 'A'

// 알파벳 인덱스 자주 쓰이는 패턴
const idx = "c".charCodeAt(0) - "a".charCodeAt(0);  // 2
```

## 4. 튜플

JS에는 별도의 튜플 타입이 없다. **배열로 표현**한다. **TypeScript**에서는 튜플 타입을 명시할 수 있다.

```ts
// JS: 그냥 배열
const point = [3, 4];

// TS: 길이와 타입 고정 튜플
const pair: [number, string] = [1, "apple"];
const triple: readonly [number, number, number] = [1, 2, 3];

// 그래프 가중치 표현 (다익스트라 등에서 자주 사용)
const edge: [number, number] = [nodeIdx, weight];
```

> Python처럼 "변경 불가능"은 TS에서 `readonly` 키워드로 표현. 하지만 코딩 테스트에서 굳이 readonly를 쓸 일은 드물다.

## 5. 객체 / Map (Python의 dict 대체)

### 두 가지 선택지

```ts
// 1) Object — 키는 자동으로 문자열로 변환됨
const obj: Record<string, number> = {};
obj["사과"] = 1;
obj["바나나"] = 2;

// 2) Map — 모든 타입의 키 가능, 순서 보장, 명시적 size
const map = new Map<string, number>();
map.set("사과", 1);
map.set("바나나", 2);
console.log(map.get("사과"));  // 1
console.log(map.has("사과"));  // true
console.log(map.size);          // 2
map.delete("사과");
```

### 시간복잡도

| 연산 | Object | Map |
|---|---|---|
| 삽입/삭제/조회 | 평균 O(1) | 평균 O(1) |
| 키 순서 보장 | △ (대부분 X) | ✅ 삽입 순서 |
| 키 타입 | string/Symbol | **모든 타입** |
| 크기 | `Object.keys(obj).length` (O(N)) | `map.size` (O(1)) |

> **권장**: 코딩 테스트에서는 **`Map`** 을 기본으로 쓰자. 키 충돌(`__proto__` 등)도 없고, 숫자 키도 그대로 쓸 수 있고, `size` 가 빠르다.

### 순회

```ts
// Object
for (const key of Object.keys(obj))   { /* ... */ }
for (const val of Object.values(obj)) { /* ... */ }
for (const [k, v] of Object.entries(obj)) { /* ... */ }

// Map
for (const [k, v] of map) { /* ... */ }
for (const k of map.keys())   { /* ... */ }
for (const v of map.values()) { /* ... */ }
```

## 6. Set (집합 자료형)

```ts
const s = new Set<number>([1, 1, 2, 3, 4, 4, 5]);
console.log(s);  // Set(5) {1, 2, 3, 4, 5}

s.add(6);
s.delete(1);
console.log(s.has(3));  // true
console.log(s.size);    // 5

// 중복 제거 트릭
const arr = [1, 1, 2, 3, 3];
const unique = [...new Set(arr)];  // [1, 2, 3]
```

### 합집합 / 교집합 / 차집합

JS Set에는 Python `|`, `&`, `-` 같은 직접 연산자가 없다 (ES2025부터 일부 메서드가 추가되긴 함).

```ts
const a = new Set([1, 2, 3, 4, 5]);
const b = new Set([3, 4, 5, 6, 7]);

const union     = new Set([...a, ...b]);                              // 합집합
const intersect = new Set([...a].filter((x) => b.has(x)));            // 교집합
const diff      = new Set([...a].filter((x) => !b.has(x)));           // 차집합
```

| 연산 | 시간복잡도 |
|---|---|
| `add` / `delete` / `has` | 평균 **O(1)** |

## 7. 입출력

코딩 테스트 환경에 따라 입출력 방식이 다르다.

### 백준 (Node.js, stdin)

```ts
const readline = require("readline");
const rl = readline.createInterface({ input: process.stdin });

const lines: string[] = [];
rl.on("line", (line) => lines.push(line));
rl.on("close", () => {
  // 첫 줄: 정수 N
  const n = Number(lines[0]);

  // 둘째 줄: 공백 구분 정수 N개
  const arr = lines[1].split(" ").map(Number);

  // 답 출력
  console.log(arr.reduce((s, x) => s + x, 0));
});
```

### 빠른 입출력 (대용량 입력)

```ts
// 한 번에 다 읽고 처리
const input = require("fs").readFileSync("/dev/stdin").toString().trim().split("\n");
const n = Number(input[0]);
const arr = input[1].split(" ").map(Number);
```

> **함정**: 입력이 큰 문제(N ≥ 100,000)에서 `readline`을 라인마다 처리하면 느릴 수 있다. **`fs.readFileSync`** 로 한 번에 읽는 게 빠르다 (Python의 `sys.stdin.readline` 트릭과 동일한 이유).

### 프로그래머스

함수 형태로 제출. 입출력은 신경 쓸 필요 없음.

```ts
function solution(n: number, arr: number[]): number {
  return arr.reduce((s, x) => s + x, 0);
}
```

### 출력 — 문자열 + 숫자

JS는 Python과 달리 `+`로 자동 형변환된다.

```ts
const answer = 7;
console.log("정답은 " + answer + "입니다.");        // OK
console.log(`정답은 ${answer}입니다.`);              // 템플릿 리터럴 (권장)
```

## 8. 표준 기능 — Python 라이브러리 대체

코딩 테스트 책의 부록은 Python 6대 표준 라이브러리(`itertools`, `heapq`, `bisect`, `collections`, `math`, 내장)를 다룬다. JS/TS는 표준 라이브러리가 빈약하니 **직접 구현하거나 npm 패키지**를 써야 한다.

### 8.1 내장 함수 / 메서드

| Python | JS/TS |
|---|---|
| `sum([1,2,3])` | `[1,2,3].reduce((s, x) => s + x, 0)` |
| `min(7,3,5,2)` | `Math.min(7,3,5,2)` |
| `max(7,3,5,2)` | `Math.max(7,3,5,2)` |
| `min(arr)` | `Math.min(...arr)` (배열 spread) |
| `sorted(arr)` | `[...arr].sort((a,b) => a-b)` (원본 보존) |
| `sorted(arr, reverse=True)` | `[...arr].sort((a,b) => b-a)` |
| `sorted(arr, key=lambda x: x[1])` | `[...arr].sort((a,b) => a[1]-b[1])` |
| `eval("2+3")` | ⚠️ `eval("2+3")` (위험, 코테서도 가능하면 피하기) |

> **함정**: `Math.min(...arr)`는 `arr` 길이가 매우 클 때(스택 한계 초과) 에러가 난다. 안전하게는 `arr.reduce((m, x) => Math.min(m, x), Infinity)`.

### 8.2 순열과 조합 (Python `itertools`)

JS에 내장 X. 직접 구현해야 한다.

```ts
// 순열 (permutations)
function permutations<T>(arr: T[], r: number): T[][] {
  if (r === 1) {
    return arr.map((v) => [v]);
  }
  const result: T[][] = [];
  arr.forEach((fixed, i) => {
    const rest = [...arr.slice(0, i), ...arr.slice(i + 1)];
    permutations(rest, r - 1).forEach((p) => {
      result.push([fixed, ...p]);
    });
  });
  return result;
}

// 조합 (combinations)
function combinations<T>(arr: T[], r: number): T[][] {
  if (r === 1) {
    return arr.map((v) => [v]);
  }
  const result: T[][] = [];
  arr.forEach((fixed, i) => {
    combinations(arr.slice(i + 1), r - 1).forEach((c) => {
      result.push([fixed, ...c]);
    });
  });
  return result;
}

console.log(permutations(["A", "B", "C"], 2));
// [['A','B'],['A','C'],['B','A'],['B','C'],['C','A'],['C','B']]

console.log(combinations(["A", "B", "C"], 2));
// [['A','B'],['A','C'],['B','C']]
```

### 8.3 힙 / 우선순위 큐 (Python `heapq`)

JS에 내장 X. 코테에선 **MinHeap을 직접 구현**한다 (외부 라이브러리 사용 불가).

```ts
class MinHeap<T> {
  private heap: T[] = [];

  size(): number {
    return this.heap.length;
  }

  push(value: T): void {
    this.heap.push(value);
    this.bubbleUp(this.heap.length - 1);
  }

  pop(): T | undefined {
    if (this.heap.length === 0) {
      return undefined;
    }
    const top = this.heap[0];
    const last = this.heap.pop()!;
    if (this.heap.length > 0) {
      this.heap[0] = last;
      this.bubbleDown(0);
    }
    return top;
  }

  peek(): T | undefined {
    return this.heap[0];
  }

  private bubbleUp(i: number): void {
    while (i > 0) {
      const parent = Math.floor((i - 1) / 2);
      if (this.heap[parent] <= this.heap[i]) {
        break;
      }
      [this.heap[parent], this.heap[i]] = [this.heap[i], this.heap[parent]];
      i = parent;
    }
  }

  private bubbleDown(i: number): void {
    const n = this.heap.length;
    while (true) {
      const l = 2 * i + 1, r = 2 * i + 2;
      let smallest = i;
      if (l < n && this.heap[l] < this.heap[smallest]) {
        smallest = l;
      }
      if (r < n && this.heap[r] < this.heap[smallest]) {
        smallest = r;
      }
      if (smallest === i) {
        break;
      }
      [this.heap[smallest], this.heap[i]] = [this.heap[i], this.heap[smallest]];
      i = smallest;
    }
  }
}

// 사용
const pq = new MinHeap<number>();
pq.push(3); pq.push(1); pq.push(2);
console.log(pq.pop()); // 1
console.log(pq.pop()); // 2

// MaxHeap이 필요하면 음수로 push했다가 pop 후 다시 양수로 (Python heapq 트릭과 동일)
// 또는 비교 로직을 부등호 반대로 직접 구현
```

| 연산 | 시간복잡도 |
|---|---|
| `push` / `pop` | **O(log N)** |
| `peek` | **O(1)** |

### 8.4 이진 탐색 (Python `bisect`)

JS에 내장 X. 직접 구현.

```ts
// lower_bound: 정렬된 배열에서 target 이상이 처음 나오는 인덱스
function lowerBound(arr: number[], target: number): number {
  let lo = 0, hi = arr.length;
  while (lo < hi) {
    const mid = (lo + hi) >> 1;
    if (arr[mid] < target) {
      lo = mid + 1;
    } else {
      hi = mid;
    }
  }
  return lo;
}

// upper_bound: target 초과가 처음 나오는 인덱스
function upperBound(arr: number[], target: number): number {
  let lo = 0, hi = arr.length;
  while (lo < hi) {
    const mid = (lo + hi) >> 1;
    if (arr[mid] <= target) {
      lo = mid + 1;
    } else {
      hi = mid;
    }
  }
  return lo;
}

// 활용: target의 등장 횟수 = upperBound - lowerBound
const a = [1, 2, 4, 4, 4, 8, 9];
console.log(upperBound(a, 4) - lowerBound(a, 4));  // 3
```

| 연산 | 시간복잡도 |
|---|---|
| `lowerBound` / `upperBound` | **O(log N)** |

### 8.5 Deque / Counter (Python `collections`)

#### Deque (양방향 큐)

JS 배열의 `shift`는 O(N)이라 큰 N에서 BFS가 느려진다. 두 가지 회피책:

```ts
// 방법 1: 인덱스 포인터로 O(1) shift 흉내
const queue: number[] = [];
let head = 0;
queue.push(1); queue.push(2);
const front = queue[head++];   // O(1) "shift"

// 방법 2: 연결리스트 기반 Deque 클래스 직접 구현
class Deque<T> {
  private map = new Map<number, T>();
  private head = 0;
  private tail = 0;
  pushFront(v: T) { this.map.set(--this.head, v); }
  pushBack(v: T)  { this.map.set(this.tail++, v); }
  popFront(): T | undefined {
    const v = this.map.get(this.head);
    this.map.delete(this.head++);
    return v;
  }
  popBack(): T | undefined {
    const v = this.map.get(--this.tail);
    this.map.delete(this.tail);
    return v;
  }
  size(): number { return this.tail - this.head; }
}
```

#### Counter (등장 횟수)

```ts
// Python: Counter("hello") → {'h':1, 'e':1, 'l':2, 'o':1}
const counter = new Map<string, number>();
for (const ch of "hello") {
  counter.set(ch, (counter.get(ch) ?? 0) + 1);
}
console.log(counter);  // Map(4) { 'h' => 1, 'e' => 1, 'l' => 2, 'o' => 1 }
```

### 8.6 Math (Python `math`)

| Python | JS |
|---|---|
| `math.factorial(5)` | 직접 구현 (`for` 또는 `Array.from`) |
| `math.sqrt(7)` | `Math.sqrt(7)` |
| `math.gcd(21, 14)` | 직접 구현 (유클리드 호제법) |
| `math.pi` | `Math.PI` |
| `math.e` | `Math.E` |
| `math.log(10)` | `Math.log(10)` |
| `math.pow(2, 10)` | `Math.pow(2, 10)` 또는 `2 ** 10` |

```ts
const factorial = (n: number): number => {
  let result = 1;
  for (let i = 2; i <= n; i++) {
    result *= i;
  }
  return result;
};

const gcd = (a: number, b: number): number => {
  while (b) {
    [a, b] = [b, a % b];
  }
  return a;
};

console.log(factorial(5));  // 120
console.log(gcd(21, 14));   // 7
```

## 자주 하는 실수

| 실수 | 원인 | 해결 |
|---|---|---|
| `arr.sort()` 결과 이상함 | 디폴트는 문자열 정렬 | 항상 `(a,b) => a-b` 명시 |
| 2D 배열 `Array(n).fill(Array(m).fill(0))` | 모든 행이 같은 참조 | `Array.from({length:n}, () => Array(m).fill(0))` |
| `0.1 + 0.2 === 0.3` → false | 부동소수점 | `Math.abs(a-b) < 1e-9` |
| BFS에서 큐로 `arr.shift()` 사용 | O(N²) 시간초과 | 인덱스 포인터 또는 Deque |
| `Math.min(...hugeArr)` 에러 | 스택 한계 초과 | `reduce`로 변경 |
| `obj[1] === obj["1"]` → 같음 | Object 키는 문자열 | 숫자 키가 필요하면 `Map` |
| `typeof null === "object"` | JS 역사적 버그 | `x === null`로 명시 검사 |
| 큰 수 계산 시 정확도 손실 | 2^53 초과 | `BigInt` 사용 |

## 빅오 복잡도 정리

코딩 테스트의 절반은 시간복잡도다. 다음 표를 외우자.

### 자료구조별 핵심 연산

| 자료구조 | 접근 | 검색 | 삽입 | 삭제 |
|---|---|---|---|---|
| Array (인덱스) | O(1) | O(N) | O(N) (중간) / O(1) (끝 push) | O(N) (중간) / O(1) (끝 pop) |
| Stack (배열의 push/pop) | — | O(N) | **O(1)** | **O(1)** |
| Queue (배열의 push/shift) | — | O(N) | O(1) push / **O(N) shift** ⚠️ | — |
| Linked Deque | — | O(N) | **O(1)** 양 끝 | **O(1)** 양 끝 |
| Map / Object | — | **O(1)** 평균 | **O(1)** 평균 | **O(1)** 평균 |
| Set | — | **O(1)** 평균 | **O(1)** 평균 | **O(1)** 평균 |
| MinHeap (이진 힙) | O(1) (peek) | O(N) | **O(log N)** | **O(log N)** (root만) |
| 정렬된 배열 + bisect | O(1) | **O(log N)** | O(N) | O(N) |

### 알고리즘 시간복잡도와 입력 크기 — 1초 기준

| 빅오 | 1초에 가능한 N |
|---|---|
| O(1), O(log N) | 매우 큼 (제한 없음) |
| O(N) | ~10^8 |
| O(N log N) | ~10^6 ~ 10^7 |
| O(N^2) | ~10^4 |
| O(N^3) | ~500 |
| O(2^N) | ~20 (DP/비트마스킹) |
| O(N!) | ~10 (전수 탐색) |

> **핵심 통찰**: 문제를 보고 **N 크기**를 보면 어느 정도 시간복잡도까지 허용되는지 감이 와야 한다. 예: N = 100,000 → O(N log N) 이하만 가능 → 정렬, 이진 탐색, 다익스트라 등.

## 요약

- JS 숫자는 모두 `number` 하나. 큰 정수는 `BigInt`. 부동소수점 비교는 epsilon.
- 배열 정렬 시 **항상 비교 함수 명시** `(a,b) => a-b`.
- 큐가 필요하면 `arr.shift()` 금지. **인덱스 포인터** 또는 **Deque 직접 구현**.
- 사전 자료형은 **`Map`** 을 기본으로 (Object는 키 강제 변환됨).
- 집합은 `Set`. 합/교/차집합은 `[...a]` + `filter`로.
- Python `itertools`/`heapq`/`bisect`는 JS에 없다. **직접 구현 코드를 외워두자.**
- 백준 입력이 크면 `fs.readFileSync('/dev/stdin')`로 한 번에 읽기.
- 시간복잡도 표는 코테의 기본 — 외울 것.
