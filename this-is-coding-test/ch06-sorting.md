# Chapter 06: 정렬 (Sorting)

> 데이터를 기준에 따라 순서대로 나열하는 알고리즘. 이진 탐색(Ch 07)의 전처리이자, 코딩 테스트와 기술 면접의 단골 주제다.

## 핵심 질문

- 선택·삽입·퀵·계수 정렬은 각각 어떤 상황에서 유리한가? (시간복잡도 관점)
- TypeScript의 `arr.sort()`는 왜 숫자를 제대로 정렬하지 못하는가?
- 데이터 범위가 한정될 때 O(N+K)로 정렬하는 방법은?

## 1. 네 가지 정렬 한눈에 보기

| 정렬 | 평균 | 최악 | 특징 |
|------|------|------|------|
| 선택 정렬 | O(N²) | O(N²) | 가장 작은 것을 골라 앞으로. 느리지만 "최솟값 찾기" 패턴은 자주 쓰임 |
| 삽입 정렬 | O(N²) | O(N²) | 적절한 위치에 삽입. **거의 정렬된 데이터면 O(N)** 으로 빠름 |
| 퀵 정렬 | O(N log N) | O(N²) | 피벗 기준 분할정복. 실무·라이브러리의 근간 |
| 계수 정렬 | O(N+K) | O(N+K) | 값 범위(K)가 작을 때 최고속. 메모리 주의 |

> **핵심 통찰**: 코딩 테스트의 정렬 문제는 대개 ① 라이브러리로 푸는 문제, ② 정렬 원리를 묻는 문제, ③ 계수 정렬 같은 특수 정렬이 필요한 문제로 나뉜다. **원리(선택·삽입·퀵)를 손으로 짤 줄 알되**, 실전에선 라이브러리를 쓰는 게 정석이다.

## 2. 선택 정렬

매 단계 **정렬 안 된 부분에서 가장 작은 값을 찾아 맨 앞과 교환**한다.

```python
# Python (책 원본)
array = [7, 5, 9, 0, 3, 1, 6, 2, 4, 8]
for i in range(len(array)):
    min_index = i
    for j in range(i + 1, len(array)):
        if array[min_index] > array[j]:
            min_index = j
    array[i], array[min_index] = array[min_index], array[i]  # 스왑
```

```ts
// TypeScript
const array = [7, 5, 9, 0, 3, 1, 6, 2, 4, 8];
for (let i = 0; i < array.length; i++) {
  let minIndex = i;
  for (let j = i + 1; j < array.length; j++) {
    if (array[minIndex] > array[j]) {
      minIndex = j;
    }
  }
  // 구조 분해 할당으로 스왑 — 파이썬의 a, b = b, a 대응
  [array[i], array[minIndex]] = [array[minIndex], array[i]];
}
// [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
```

> **핵심 통찰**: 파이썬의 튜플 스왑 `a, b = b, a`는 TS에서 **구조 분해 할당 `[a, b] = [b, a]`** 로 그대로 옮긴다. C처럼 임시 변수가 필요 없다.

## 3. 삽입 정렬

데이터를 하나씩 보며 **앞쪽 정렬된 구간의 적절한 위치에 끼워 넣는다**. 자기보다 작은 값을 만나면 멈춘다.

```ts
const array = [7, 5, 9, 0, 3, 1, 6, 2, 4, 8];
for (let i = 1; i < array.length; i++) {
  for (let j = i; j > 0; j--) {
    if (array[j] < array[j - 1]) {
      [array[j], array[j - 1]] = [array[j - 1], array[j]];
    } else {
      // 자기보다 작은 데이터를 만나면 멈춤
      break;
    }
  }
}
```

> **핵심 통찰**: 삽입 정렬은 **거의 정렬된 입력**에서 최선 O(N)으로 동작한다. "데이터가 거의 정렬돼 있다"는 조건이 보이면 퀵 정렬보다 유리할 수 있다.

## 4. 퀵 정렬

**피벗(기준)** 을 잡아 작은 값은 왼쪽, 큰 값은 오른쪽으로 분할한 뒤 양쪽을 재귀 정렬한다. 파이썬 리스트 컴프리헨션을 TS `filter`로 옮기면 직관적이다.

```ts
function quickSort(array: number[]): number[] {
  // 원소가 1개 이하면 그대로 반환 (종료 조건)
  if (array.length <= 1) {
    return array;
  }
  const pivot = array[0]; // 첫 번째 원소를 피벗으로
  const tail = array.slice(1);
  const leftSide = tail.filter((x) => x <= pivot);
  const rightSide = tail.filter((x) => x > pivot);
  return [...quickSort(leftSide), pivot, ...quickSort(rightSide)];
}

console.log(quickSort([5, 7, 9, 0, 3, 1, 6, 2, 4, 8]));
// [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
```

**시간복잡도**: 평균 O(N log N), 최악 O(N²). 이미 정렬된 입력에서 첫 원소를 피벗으로 삼으면 최악이 된다.

## 5. 계수 정렬

**값의 범위(0~K)만큼 카운트 배열**을 만들어 등장 횟수를 센 뒤, 인덱스 순서로 출력한다. 비교를 하지 않아 O(N+K)로 매우 빠르다.

```ts
const array = [7, 5, 9, 0, 3, 1, 6, 2, 9, 1, 4, 8, 0, 5, 2];
const count = new Array(Math.max(...array) + 1).fill(0);
for (const x of array) {
  count[x]++; // 값에 해당하는 인덱스 증가
}

const result: number[] = [];
for (let i = 0; i < count.length; i++) {
  for (let j = 0; j < count[i]; j++) {
    result.push(i); // 등장 횟수만큼 인덱스 출력
  }
}
console.log(result.join(" ")); // 0 0 1 1 2 2 3 4 5 5 6 7 8 9 9
```

> **함정**: 계수 정렬은 값의 범위가 크면 메모리가 폭발한다(0과 999,999 단 둘만 있어도 100만 칸 필요). **동일 값이 많이 중복되고 범위가 좁을 때**(예: 0~100 성적)만 쓴다. 또한 `Math.max(...array)`는 배열이 매우 크면 인자 전개로 스택 오버플로가 나니, 큰 배열은 `array.reduce((m, x) => Math.max(m, x), 0)`을 쓴다.

## 6. 정렬 라이브러리 — TS `sort()`의 함정

실전에서는 직접 구현 대신 내장 정렬을 쓴다. 파이썬은 `sorted()`(새 리스트) / `list.sort()`(제자리)를 제공하며 둘 다 O(N log N)을 보장한다.

```ts
const array = [7, 5, 9, 0, 3, 1, 6, 2, 4, 8];

const asc = [...array].sort((a, b) => a - b); // 오름차순
const desc = [...array].sort((a, b) => b - a); // 내림차순

// key 정렬: 튜플의 두 번째 원소 기준 (파이썬 key=lambda 대응)
const fruits: [string, number][] = [["바나나", 2], ["사과", 5], ["당근", 3]];
fruits.sort((a, b) => a[1] - b[1]); // [["바나나",2],["당근",3],["사과",5]]
```

> **함정**: TypeScript의 `Array.prototype.sort()`는 **비교 함수를 안 넘기면 원소를 문자열로 바꿔 사전순 정렬**한다. `[10, 9, 2].sort()` → `[10, 2, 9]`(❌). 숫자는 반드시 `(a, b) => a - b`를 넘겨야 한다. 또한 `sort()`는 **원본을 제자리 변경**하므로, 원본을 지키려면 `[...arr].sort(...)` 또는 `arr.toSorted(...)`(ES2023)를 쓴다.

---

## 7. 실전 문제 1 — 위에서 아래로

| 항목 | 값 |
|------|-----|
| 난이도 | ★ 하 |
| 풀이 시간 | 15분 |
| 시간 제한 | 1초 |
| 기출 | T 기업 코딩 테스트 |

### 문제 요약

N개의 수를 **내림차순**으로 정렬해 출력하라. (N ≤ 500, 각 수 ≤ 100,000)

예: `[15, 27, 12]` → `27 15 12`

### 코드

```ts
const input = `3
15
27
12`;

const lines = input.split("\n");
const n = Number(lines[0]);
const array = lines.slice(1, 1 + n).map(Number);

array.sort((a, b) => b - a); // 내림차순
console.log(array.join(" ")); // 27 15 12
```

**시간복잡도**: O(N log N). 데이터가 작아 어떤 정렬을 써도 되지만 라이브러리가 가장 간결하다.

## 8. 실전 문제 2 — 성적이 낮은 순서로 학생 출력하기

| 항목 | 값 |
|------|-----|
| 난이도 | ★ 하 |
| 풀이 시간 | 20분 |
| 시간 제한 | 1초 |
| 기출 | D 기업 프로그래밍 콘테스트 예선 |

### 문제 요약

N명의 (이름, 성적)이 주어질 때 **성적이 낮은 순**으로 이름을 출력하라. (N ≤ 100,000)

예: `홍길동 95`, `이순신 77` → `이순신 홍길동`

### 핵심 아이디어

(이름, 점수)로 묶어 **점수를 key로 정렬**한다. 데이터가 10만 개이므로 O(N log N) 라이브러리 정렬이 적합하다.

### 코드

```ts
const input = `2
홍길동 95
이순신 77`;

const lines = input.split("\n");
const n = Number(lines[0]);
const students: [string, number][] = lines.slice(1, 1 + n).map((line) => {
  const [name, score] = line.split(" ");
  return [name, Number(score)];
});

students.sort((a, b) => a[1] - b[1]); // 점수 오름차순
console.log(students.map((s) => s[0]).join(" ")); // 이순신 홍길동
```

**시간복잡도**: O(N log N).

## 9. 실전 문제 3 — 두 배열의 원소 교체

| 항목 | 값 |
|------|-----|
| 난이도 | ★★ 중하 |
| 풀이 시간 | 20분 |
| 시간 제한 | 2초 |
| 기출 | 국제 알고리즘 대회 |

### 문제 요약

배열 A, B(각 N개)가 있다. 최대 K번 "A의 원소 ↔ B의 원소"를 교체해 **A의 원소 합을 최대**로 만들어라.

예: N=5, K=3, A=`[1,2,5,4,3]`, B=`[5,5,6,6,5]` → `26`

### 핵심 아이디어

**A는 오름차순, B는 내림차순**으로 정렬한 뒤, 앞에서부터 "A의 작은 값 < B의 큰 값"일 때만 교체한다. A의 작은 값이 B의 큰 값보다 크거나 같아지면 더 교체해도 손해이므로 멈춘다. (그리디 + 정렬)

### 코드

```ts
const input = `5 3
1 2 5 4 3
5 5 6 6 5`;

const lines = input.split("\n");
const [n, k] = lines[0].split(" ").map(Number);
const a = lines[1].split(" ").map(Number);
const b = lines[2].split(" ").map(Number);

a.sort((x, y) => x - y); // A 오름차순
b.sort((x, y) => y - x); // B 내림차순

for (let i = 0; i < k; i++) {
  // A의 원소가 B의 원소보다 작을 때만 교체
  if (a[i] < b[i]) {
    [a[i], b[i]] = [b[i], a[i]];
  } else {
    // 더 교체하면 손해이므로 중단
    break;
  }
}

console.log(a.reduce((sum, x) => sum + x, 0)); // 26
```

**시간복잡도**: O(N log N) — 정렬이 지배적.

> **핵심 통찰**: 이 문제는 **정렬 + 그리디**의 결합이다. "합을 최대로"라는 목표를 위해 A의 가장 약한 카드를 B의 가장 강한 카드와 바꾸는 것이 매 단계 최선의 선택이며, 교체 이득이 사라지는 순간 멈추는 것이 정당성의 핵심이다.

---

## 자주 하는 실수

| 실수 | 원인 | 해결 |
|------|------|------|
| `arr.sort()` 로 숫자 정렬 | 기본이 **문자열 사전순** | `arr.sort((a, b) => a - b)` |
| `sort()` 후 원본이 바뀜 | `sort()`는 제자리 변경 | `[...arr].sort()` 또는 `arr.toSorted()` |
| 계수 정렬에 큰 범위 사용 | 메모리 폭발 | 값 범위 좁고 중복 많을 때만 사용 |
| `Math.max(...hugeArr)` | 인자 전개 스택 초과 | `arr.reduce((m, x) => Math.max(m, x), 0)` |
| 퀵 정렬 최악 케이스 간과 | 정렬된 입력 + 첫 원소 피벗 | 실전은 라이브러리 사용 (O(N log N) 보장) |

## 패턴 체크리스트

- [ ] 단순 정렬인가? → 라이브러리 `sort((a,b)=>a-b)` (비교 함수 필수!)
- [ ] 특정 필드 기준 정렬인가? → key 비교 함수 `(a,b)=>a.x-b.x`
- [ ] 값 범위가 좁고(예: 0~100) 중복 많은가? → 계수 정렬 O(N+K)
- [ ] 거의 정렬된 입력인가? → 삽입 정렬 고려 (최선 O(N))
- [ ] 원본 배열을 보존해야 하는가? → `[...arr].sort()` / `toSorted()`

## 요약

- 정렬은 **이진 탐색(Ch 07)의 전제**이자 면접 단골. 원리(선택·삽입·퀵)는 손으로, 실전은 라이브러리로.
- 선택 O(N²) / 삽입 O(N²)·거의정렬 O(N) / 퀵 평균 O(N log N) / 계수 O(N+K)·범위 한정.
- **TS `sort()`는 비교 함수 없으면 문자열 정렬** — 숫자는 `(a,b)=>a-b` 필수. 원본 보존은 `[...arr]`/`toSorted`.
- 파이썬 튜플 스왑 → TS 구조 분해 `[a,b]=[b,a]`. key 정렬 → 비교 함수에 필드 지정.
- 두 배열 원소 교체처럼 **정렬 + 그리디** 결합 문제가 자주 나온다.
