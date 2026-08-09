# Chapter 15: 이진 탐색 기출문제

> Ch 07에서 배운 이진 탐색 유형의 기출문제 모음(Q27~Q30). **lower/upper bound**, **고정점**, **파라메트릭 서치**, **길이별 이진 탐색**이 핵심이다.

## 핵심 질문

- 값의 개수·범위는 lower/upper bound로 어떻게 O(log N)에 구하는가?
- "조건을 만족하는 최대 거리"는 왜 파라메트릭 서치인가?
- 정렬 + 이진 탐색으로 카운팅 문제를 어떻게 가속하는가?

> 파이썬의 `bisect_left`/`bisect_right`에 해당하는 **lower/upper bound**를 직접 구현해 둔다(TS에 내장 없음).

```ts
function lowerBound(arr: string[] | number[], target: string | number): number {
  let lo = 0;
  let hi = arr.length;
  while (lo < hi) {
    const mid = Math.floor((lo + hi) / 2);
    if (arr[mid] < target) {
      lo = mid + 1;
    } else {
      hi = mid;
    }
  }
  return lo; // target 이상이 처음 등장하는 위치
}

function upperBound(arr: string[] | number[], target: string | number): number {
  let lo = 0;
  let hi = arr.length;
  while (lo < hi) {
    const mid = Math.floor((lo + hi) / 2);
    if (arr[mid] <= target) {
      lo = mid + 1;
    } else {
      hi = mid;
    }
  }
  return lo; // target 초과가 처음 등장하는 위치
}
```

---

## Q27 정렬된 배열에서 특정 수의 개수 구하기

| 항목 | 값 |
|------|-----|
| 난이도 | ★★ 중하 |
| 기출 | Zoho 인터뷰 |

### 문제 요약

오름차순 배열에서 값 x의 **등장 횟수**를 O(log N)에 구하라. 없으면 -1.

예: `[1,1,2,2,2,2,3]`, x=2 → `4` / x=4 → `-1`

### 핵심 아이디어

`upperBound(x) − lowerBound(x)`가 x의 개수다.

```ts
function countByValue(arr: number[], x: number): number {
  const count = upperBound(arr, x) - lowerBound(arr, x);
  return count > 0 ? count : -1;
}
console.log(countByValue([1, 1, 2, 2, 2, 2, 3], 2)); // 4
```

## Q28 고정점 찾기

| 항목 | 값 |
|------|-----|
| 난이도 | ★ 하 |
| 기출 | Amazon 인터뷰 |

### 문제 요약

오름차순(서로 다른 원소) 배열에서 **`a[i] === i`인 고정점**을 O(log N)에 찾아라. 없으면 -1.

예: `[-15,-6,1,3,7]` → `3`

### 핵심 아이디어

`a[mid]`와 `mid`를 비교한다. `a[mid] < mid`면 고정점은 오른쪽(원소가 인덱스보다 작으니), `a[mid] > mid`면 왼쪽에 있다(원소들이 서로 달라 단조 증가폭 ≥ 1이므로).

```ts
function fixedPoint(arr: number[]): number {
  let lo = 0;
  let hi = arr.length - 1;
  while (lo <= hi) {
    const mid = Math.floor((lo + hi) / 2);
    if (arr[mid] === mid) {
      return mid;
    }
    if (arr[mid] < mid) {
      lo = mid + 1;
    } else {
      hi = mid - 1;
    }
  }
  return -1;
}
console.log(fixedPoint([-15, -6, 1, 3, 7])); // 3
```

## Q29 공유기 설치

| 항목 | 값 |
|------|-----|
| 난이도 | ★★★ 중 |
| 기출 | 백준 2110 |

### 문제 요약

집 N개에 공유기 C개를 설치해 **가장 인접한 두 공유기 사이 거리를 최대화**하라.

예: 집 `[1,2,8,4,9]`, C=3 → `3`

### 핵심 아이디어

전형적인 **파라메트릭 서치**(Ch 07). "거리 D 이상으로 C개를 설치할 수 있는가?"를 이진 탐색한다. 집을 정렬하고, 거리 D로 그리디하게 놓아 본다.

```ts
function router(houses: number[], c: number): number {
  houses.sort((a, b) => a - b);
  let lo = 1;
  let hi = houses[houses.length - 1] - houses[0];
  let result = 0;

  while (lo <= hi) {
    const mid = Math.floor((lo + hi) / 2); // 거리 후보 D
    // D 이상 간격으로 그리디 설치
    let count = 1;
    let last = houses[0];
    for (let i = 1; i < houses.length; i++) {
      if (houses[i] - last >= mid) {
        count++;
        last = houses[i];
      }
    }
    if (count >= c) {
      result = mid; // D로 충분 → 더 늘려 보기
      lo = mid + 1;
    } else {
      hi = mid - 1; // D가 너무 큼 → 줄이기
    }
  }
  return result;
}
console.log(router([1, 2, 8, 4, 9], 3)); // 3
```

> **핵심 통찰**: "최대 거리"라는 최적화 문제를 "거리 D로 C개 설치 가능?"이라는 **결정 문제**로 바꾸는 게 파라메트릭 서치의 본질이다(Ch 07 떡볶이 떡과 동일한 발상).

## Q30 가사 검색

| 항목 | 값 |
|------|-----|
| 난이도 | ★★★ 상 |
| 기출 | 2020 카카오 신입공채 1차 |

### 문제 요약

`?`(접두사 또는 접미사 위치)가 포함된 키워드가 매치되는 단어 수를 구하라. `?`는 글자 하나에 매치.

예: words=`[frodo,front,frost,frozen,frame,kakao]`, queries=`[fro??,????o,fr???,fro???,pro?]` → `[3,2,4,1,0]`

### 핵심 아이디어

`?`가 접미사면(`fro??`) **길이별로 정렬된 단어 배열**에서 `froaa`~`frozz` 범위를 이진 탐색한다. `?`가 접두사면(`????o`) **단어를 뒤집어** 같은 방식으로 처리한다. 길이가 다르면 매치 불가이므로 **길이별 그룹화**가 핵심이다.

```ts
function solutionLyrics(words: string[], queries: string[]): number[] {
  const byLength = new Map<number, string[]>();
  const byLengthRev = new Map<number, string[]>();
  for (const w of words) {
    const len = w.length;
    if (!byLength.has(len)) {
      byLength.set(len, []);
      byLengthRev.set(len, []);
    }
    byLength.get(len)!.push(w);
    byLengthRev.get(len)!.push([...w].reverse().join(""));
  }
  for (const arr of byLength.values()) {
    arr.sort();
  }
  for (const arr of byLengthRev.values()) {
    arr.sort();
  }

  const result: number[] = [];
  for (const q of queries) {
    const len = q.length;
    let arr: string[] | undefined;
    let pattern: string;
    if (q[0] === "?") {
      arr = byLengthRev.get(len); // 접두사 ? → 뒤집어서 접미사화
      pattern = [...q].reverse().join("");
    } else {
      arr = byLength.get(len);
      pattern = q;
    }
    if (!arr) {
      result.push(0);
      continue;
    }
    const low = pattern.replace(/\?/g, "a"); // ? → 가장 작은 글자
    const high = pattern.replace(/\?/g, "z"); // ? → 가장 큰 글자
    result.push(upperBound(arr, high) - lowerBound(arr, low));
  }
  return result;
}
console.log(solutionLyrics(
  ["frodo", "front", "frost", "frozen", "frame", "kakao"],
  ["fro??", "????o", "fr???", "fro???", "pro?"],
)); // [3, 2, 4, 1, 0]
```

> **핵심 통찰**: `?`를 `a`~`z`로 치환해 **탐색 범위의 양 끝**을 만들고, 그 사이 개수를 `upperBound − lowerBound`로 센다. 접두사 `?`는 문자열을 뒤집어 접미사 문제로 환원하는 게 정석 기법이다.

---

## 요약

- **특정 수 개수**: `upperBound(x) − lowerBound(x)`.
- **고정점**: `a[mid]` vs `mid` 비교로 방향 결정 (서로 다른 원소라 단조성 보장).
- **공유기 설치**: "거리 D로 C개 가능?"의 **파라메트릭 서치** + 그리디 배치.
- **가사 검색**: **길이별 정렬 + 이진 탐색**, `?`는 `a`/`z` 치환으로 범위화, 접두사 `?`는 뒤집기.
- TS엔 `bisect`가 없으니 **lower/upper bound를 직접** 준비해 두는 게 핵심.
