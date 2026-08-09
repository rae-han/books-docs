# Chapter 07: 이진 탐색 (Binary Search)

> 정렬된 데이터에서 탐색 범위를 절반씩 좁혀 O(log N)에 찾는 알고리즘. 탐색 범위가 1,000만을 넘거나 값의 범위가 10억대면 가장 먼저 의심해야 할 도구다.

## 핵심 질문

- 이진 탐색은 왜 O(log N)이며, 전제 조건은 무엇인가?
- 최적화 문제를 어떻게 **"결정 문제"** 로 바꿔(파라메트릭 서치) 이진 탐색으로 푸는가?
- TypeScript에서 중간점 계산의 오버플로·실수 함정을 어떻게 피하는가?

## 1. 순차 탐색 vs 이진 탐색

| 탐색 | 전제 | 시간복잡도 | 비고 |
|------|------|-----------|------|
| 순차 탐색(*Sequential Search*) | 없음 | O(N) | 앞에서부터 하나씩. `includes`, `indexOf` 내부 동작 |
| 이진 탐색(*Binary Search*) | **정렬되어 있어야 함** | O(log N) | 범위를 절반씩 좁힘 |

이진 탐색은 **시작점·끝점·중간점** 세 위치를 쓴다. 중간점의 값과 목표값을 비교해, 목표가 더 작으면 왼쪽 절반(끝점을 당김), 크면 오른쪽 절반(시작점을 밀어냄)으로 범위를 좁힌다. 데이터 32개면 5번(log₂32), 10억개여도 약 30번 만에 끝난다.

## 2. 이진 탐색 구현

```python
# Python (책 원본) — 반복문 버전
def binary_search(array, target, start, end):
    while start <= end:
        mid = (start + end) // 2
        if array[mid] == target:
            return mid
        elif array[mid] > target:
            end = mid - 1
        else:
            start = mid + 1
    return None
```

```ts
// TypeScript — 반복문 버전
function binarySearch(array: number[], target: number, start: number, end: number): number {
  while (start <= end) {
    const mid = Math.floor((start + end) / 2);
    if (array[mid] === target) {
      return mid;
    } else if (array[mid] > target) {
      end = mid - 1; // 왼쪽 절반
    } else {
      start = mid + 1; // 오른쪽 절반
    }
  }
  return -1; // 못 찾음 (파이썬 None 대응)
}
```

재귀로도 구현할 수 있다. 동작은 같다.

```ts
function binarySearchRec(array: number[], target: number, start: number, end: number): number {
  if (start > end) {
    return -1;
  }
  const mid = Math.floor((start + end) / 2);
  if (array[mid] === target) {
    return mid;
  } else if (array[mid] > target) {
    return binarySearchRec(array, target, start, mid - 1);
  } else {
    return binarySearchRec(array, target, mid + 1, end);
  }
}
```

> **함정**: 파이썬의 `(start + end) // 2`(정수 나눗셈)를 TS에서 `(start + end) >> 1`(비트 시프트)로 옮기면 위험하다. 비트 연산은 피연산자를 **32비트 정수로 변환**하므로, `start + end`가 약 21.4억(2³¹)을 넘으면 음수가 된다. 떡볶이 문제처럼 값이 10억대면 합이 20억을 넘을 수 있으니, 반드시 **`Math.floor((start + end) / 2)`** 를 써라 (JS `number`는 2⁵³까지 안전).

## 3. (참고) 트리와 이진 탐색 트리

이진 탐색의 전제는 "정렬"이다. 데이터베이스·파일시스템은 대용량 데이터를 **트리** 자료구조로 항상 정렬 상태로 유지해 빠른 탐색을 보장한다. 그중 가장 단순한 형태가 **이진 탐색 트리**다.

- 왼쪽 자식 노드 < 부모 노드 < 오른쪽 자식 노드

루트부터 비교하며 작으면 왼쪽, 크면 오른쪽으로 내려가 O(log N)에 조회한다. 직접 구현을 요구하는 문제는 드물어 개념만 알아 두면 된다.

> **실무 팁**: 파이썬은 입력이 많으면 `input()` 대신 `sys.stdin.readline()`으로 시간 초과를 피한다. Node.js(TS)에서는 `require("fs").readFileSync(0, "utf8")`로 입력 전체를 한 번에 읽어 줄 단위로 쪼개는 방식이 표준이다 (한 줄씩 `readline` 이벤트보다 빠르다).

## 4. 파라메트릭 서치 — 최적화를 결정 문제로

파라메트릭 서치(*Parametric Search*)는 **최적화 문제("조건을 만족하는 가장 큰/작은 값은?")를 결정 문제("이 값으로 조건을 만족하는가? 예/아니오")로 바꿔** 푸는 기법이다. 답의 후보 범위에 대해 이진 탐색을 돌리며, 각 중간점에서 "예/아니오"를 판정해 범위를 좁힌다.

> **핵심 통찰**: "조건을 만족하는 최댓값/최솟값"을 묻고 **답의 범위가 매우 넓다(수억 단위)** 면 파라메트릭 서치를 의심하라. 후보 값 자체를 이진 탐색 대상으로 삼는 것이 핵심 전환이다.

---

## 5. 실전 문제 1 — 부품 찾기

| 항목 | 값 |
|------|-----|
| 난이도 | ★★ 중하 |
| 풀이 시간 | 30분 |
| 시간 제한 | 1초 |
| 메모리 | 128MB |

### 문제 요약

가게 부품 N개와 손님 요청 M개가 주어진다. 각 요청 부품이 가게에 있으면 `yes`, 없으면 `no`를 출력하라. (N ≤ 100만, M ≤ 10만)

예: 부품 `[8,3,7,9,2]`, 요청 `[5,7,9]` → `no yes yes`

### 핵심 아이디어

부품을 정렬한 뒤 각 요청을 이진 탐색한다. 전체 O((N+M) log N). 또는 **집합(`Set`)** 으로 O(1) 조회하면 더 간결하다.

### 코드

```ts
const input = `5
8 3 7 9 2
3
5 7 9`;

const lines = input.split("\n");
const n = Number(lines[0]);
const array = lines[1].split(" ").map(Number);
array.sort((a, b) => a - b); // 이진 탐색을 위해 정렬
const targets = lines[3].split(" ").map(Number);

function binarySearch(arr: number[], target: number, start: number, end: number): number {
  while (start <= end) {
    const mid = Math.floor((start + end) / 2);
    if (arr[mid] === target) {
      return mid;
    } else if (arr[mid] > target) {
      end = mid - 1;
    } else {
      start = mid + 1;
    }
  }
  return -1;
}

const result = targets.map((t) => (binarySearch(array, t, 0, n - 1) !== -1 ? "yes" : "no"));
console.log(result.join(" ")); // no yes yes
```

> **핵심 통찰**: 파이썬의 `x in array`(리스트)는 사실 O(N) 순차 탐색이다. TS의 `array.includes(x)`도 마찬가지. **존재 여부만** 필요하면 `new Set(array)`로 만들어 `set.has(x)`(O(1))를 쓰는 게 정답이다. 이 문제는 이진 탐색·계수 배열·집합 세 가지로 모두 풀린다.

## 6. 실전 문제 2 — 떡볶이 떡 만들기

| 항목 | 값 |
|------|-----|
| 난이도 | ★★★ 중 |
| 풀이 시간 | 40분 |
| 시간 제한 | 2초 |
| 메모리 | 128MB |

### 문제 요약

높이가 제각각인 떡들을 절단기 높이 H로 자른다. H보다 긴 부분만 잘린다. 잘린 떡의 합이 **최소 M 이상**이 되게 하는 **H의 최댓값**을 구하라. (떡 개수 ≤ 100만, 높이 ≤ 10억)

예: 떡 `[19,15,10,17]`, M=6 → H=`15` (잘린 합 = 4+0+0+2 = 6)

### 핵심 아이디어

전형적인 **파라메트릭 서치**다. H의 후보 범위는 `0 ~ max(높이)`로 최대 10억. "H로 잘랐을 때 합이 M 이상인가?"라는 결정 문제를 이진 탐색으로 좁힌다.

- 잘린 합 ≥ M → 더 높이 잘라도 될지 모름 → `result = mid`로 기록하고 시작점을 올림(오른쪽 탐색)
- 잘린 합 < M → 너무 많이 잘림 → 끝점을 내림(왼쪽 탐색)

"덜 자를수록(H가 클수록) 좋다"이므로, 조건을 만족할 때마다 `result`를 갱신하면 자연스레 최댓값이 남는다.

### 코드

```ts
const input = `4 6
19 15 10 17`;

const lines = input.split("\n");
const [n, m] = lines[0].split(" ").map(Number);
const array = lines[1].split(" ").map(Number);

let start = 0;
let end = Math.max(...array);
let result = 0;

while (start <= end) {
  let total = 0;
  const mid = Math.floor((start + end) / 2); // 절단기 높이 H
  for (const x of array) {
    // 잘린 떡의 양 계산
    if (x > mid) {
      total += x - mid;
    }
  }
  if (total < m) {
    // 떡이 부족 → 더 많이 자르기 (왼쪽 탐색)
    end = mid - 1;
  } else {
    // 떡이 충분 → 덜 자르기 (오른쪽 탐색), 최댓값 후보 기록
    result = mid;
    start = mid + 1;
  }
}

console.log(result); // 15
```

**시간복잡도**: O(N log(max H)) — 약 100만 × 30 ≈ 3,000만 연산.

> **함정**: "최대한 덜 잘랐을 때(H가 클 때)가 정답"이므로 조건 만족 시 `result = mid`로 **기록한 뒤** 오른쪽으로 더 탐색한다. 단순히 같음(`==`)을 찾는 게 아니라 **"조건을 만족하는 경계"** 를 찾는 변형임에 주의.

---

## 자주 하는 실수

| 실수 | 원인 | 해결 |
|------|------|------|
| 정렬 안 하고 이진 탐색 | 전제 조건 위반 | 탐색 전 `sort((a,b)=>a-b)` 필수 |
| 중간점을 `(s+e) >> 1` | 32비트 변환으로 오버플로 | `Math.floor((s+e)/2)` |
| `(s+e)/2` 그대로 사용 | 실수(소수점) 인덱스 | `Math.floor` 로 정수화 |
| 존재 검사에 `includes` 남발 | O(N) 반복 | `new Set()` + `has` (O(1)) |
| 파라메트릭에서 경계 갱신 누락 | 최댓값/최솟값 못 잡음 | 조건 만족 시 `result` 갱신 후 진행 |

## 패턴 체크리스트

- [ ] 데이터가 정렬돼 있는가(또는 정렬 가능한가)? → 이진 탐색 후보
- [ ] 탐색 범위/값이 1,000만~10억대인가? → O(log N) 알고리즘 필요
- [ ] "조건을 만족하는 최대/최소값"인가? → 파라메트릭 서치(결정 문제로 변환)
- [ ] 중간점을 `Math.floor((s+e)/2)`로 안전하게 계산했는가?
- [ ] 단순 존재 검사면 `Set.has()`로 충분한가?

## 요약

- 이진 탐색 = **정렬 전제**, 범위를 절반씩 → O(log N). 시작·끝·중간점 세 변수로 구현.
- TS 중간점은 **`Math.floor((s+e)/2)`** — `>>`는 20억 넘으면 오버플로, `/2`만으론 실수.
- **파라메트릭 서치**: 최적화("최대 H?")를 결정 문제("H면 조건 만족?")로 바꿔 이진 탐색 (떡볶이 떡).
- 단순 존재 검사는 `Set.has()`(O(1))가 `includes`(O(N))보다 우수 (부품 찾기).
- 정렬(Ch 06)이 이진 탐색의 전제 — 두 챕터는 짝을 이룬다.
