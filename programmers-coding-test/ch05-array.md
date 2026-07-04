# Chapter 05: Array (배열)

## 핵심 질문

배열은 어떤 자료구조이며 어떤 연산이 빠르고 어떤 연산이 느린가? 자바스크립트의 배열은 일반 배열과 어떻게 다르며, 코딩 테스트에서 어떤 함정에 자주 빠지는가?

## 1. 배열의 개념

배열은 같은 타입의 원소들을 그룹화해서 관리하는 가장 기본적인 자료구조다. 같은 타입의 변수가 여러 개 필요할 때 자주 쓴다. 학생 1,000명의 점수를 정수형 변수 1,000개로 따로 선언해 관리하면 비효율적이지만 배열을 쓰면 하나의 이름으로 묶어 관리할 수 있고, **인덱스(index)로 임의 접근(random access)** 할 수 있다는 큰 장점을 얻는다.

### 배열 선언 — 세 가지 방법

자바스크립트에서 길이 6인 배열은 다음 세 가지 방법으로 만들 수 있다.

```javascript
// 1. 리터럴
const arr = [0, 0, 0, 0, 0, 0];

// 2. Array 생성자 — 빈 배열을 만든 뒤 채워 넣기
const arr1 = new Array(6); // [undefined, undefined, ...]
const arr2 = [...new Array(6)].map((_, i) => i + 1); // [1, 2, 3, 4, 5, 6]

// 3. fill() — 특정 값으로 채우기
const arr3 = new Array(6).fill(0); // [0, 0, 0, 0, 0, 0]
```

> **핵심 통찰**: 자바스크립트의 배열은 `Array` 객체로 구현되어 있어 다른 언어의 배열과 내부 구조가 다르다. 동적으로 크기를 조절할 수 있고 슬라이싱·삽입·삭제·연결 등 풍부한 메서드를 제공해서 코딩 테스트에서 고려할 사항이 줄어든다.

### 배열의 차원

2차원·3차원 배열을 자주 쓰지만 컴퓨터 메모리는 1차원이다. 즉, 다차원 배열도 실제로는 메모리에 1차원으로 연속 할당된다.

```javascript
// 2차원 배열 리터럴
const arr = [
  [1, 2, 3, 4],
  [5, 6, 7, 8],
  [9, 10, 11, 12],
];

console.log(arr[2][3]); // 12
arr[2][3] = 15;

// 3 × 4 배열을 동적으로 생성 — 0으로 초기화
const grid = [...new Array(3)].map(() => new Array(4).fill(0));
```

2차원 배열의 메모리 배치를 그림으로 보면 다음과 같다.

```
[사람이 보는 모습]            [메모리에 저장된 실제 모습]
   0  1  2                   주소(낮은 → 높은)
0  1  2  3      ───────►     1 → arr[0][0]
1  4  5  6                   2 → arr[0][1]
                             3 → arr[0][2]
                             4 → arr[1][0]
                             5 → arr[1][1]
                             6 → arr[1][2]
```

행 단위로 평탄화해 0행, 1행 순서로 1차원 공간에 저장된다. 이 특성을 알아야 행렬 문제에서 인덱스 계산 실수를 줄일 수 있다.

## 2. 배열의 효율성 — 시간 복잡도

| 연산 | 시간 복잡도 | 이유 |
|------|------------|------|
| 임의 접근 (`arr[i]`) | O(1) | 인덱스로 메모리 위치를 직접 계산 |
| 맨 뒤 삽입/삭제 (`push`/`pop`) | O(1) | 다른 데이터에 영향 없음 |
| 맨 앞 삽입/삭제 (`unshift`/`shift`) | O(N) | 모든 데이터를 한 칸씩 밀어야 함 |
| 중간 삽입/삭제 (`splice`) | O(N) | 삽입 지점 뒤의 N개를 밀어야 함 |
| 탐색 (`includes`, `indexOf`) | O(N) | 처음부터 순회 |

### 맨 앞에 삽입할 경우

```
삽입 전:  [1, 3, 4, 5]
            ↓ 맨 앞에 2 삽입
삽입 중:  [_, 1, 3, 4, 5]   ← 모든 원소를 한 칸씩 밀어야 함 (O(N))
삽입 후:  [2, 1, 3, 4, 5]
```

### 배열을 선택할 때 고려할 점

1. **할당 가능한 메모리 크기 확인**: 정수형 1차원 배열은 보통 1,000만 개, 2차원은 3,000 × 3,000 정도가 한계다.
2. **중간 삽입 빈도 확인**: 빈번하면 시간 초과 위험. 다른 자료구조(연결 리스트, 데크 등)를 검토.

> 자바스크립트의 배열은 크기가 변할 수 있어 다른 언어의 "리스트"처럼 쓸 수 있다. 이 노트에서는 크기를 고정해 쓰면 "배열", 가변 크기로 쓰면 "리스트"라고 부른다.

## 3. 핵심 코드 패턴

### 1차원 배열 0으로 초기화

```javascript
const arr = new Array(N).fill(0);
```

### 2차원 배열 0으로 초기화

```javascript
const arr = Array.from({ length: R }, () => new Array(C).fill(0));
// 또는
const arr = [...new Array(R)].map(() => new Array(C).fill(0));
```

> **함정**: `new Array(R).fill(new Array(C).fill(0))`처럼 쓰면 모든 행이 **같은 참조**를 공유한다. 한 행만 수정해도 모든 행이 변경되니 절대 쓰지 말 것.

### 인덱스와 값을 동시에 순회

```javascript
for (const [i, value] of arr.entries()) {
  // ...
}
```

### 중복 제거 + 정렬

```javascript
const result = [...new Set(arr)].sort((a, b) => a - b);
```

### 좌표를 Set의 키로 쓰기 (방문 체크)

```javascript
const visited = new Set();
visited.add(`${x},${y}`); // 객체 대신 문자열로 저장
```

## 4. JavaScript 빌트인 메서드 레퍼런스

배열 챕터에서 자주 쓰는 메서드 모음.

### 추가

| 메서드 | 동작 | 시간 복잡도 | 비고 |
|--------|------|------------|------|
| `arr.push(x)` | 맨 뒤 추가 | O(1) | 원본 변경 |
| `arr.unshift(x)` | 맨 앞 추가 | O(N) | 원본 변경. 데이터 적으면 V8이 최적화 (~15,000개까지) |
| `arr.concat([x, y])` | 새 배열로 연결 | O(N) | 원본 유지, 새 배열 반환 |
| `[...arr, x, y]` | 스프레드로 연결 | O(N) | 새 배열 반환 |
| `arr.splice(i, 0, x)` | 인덱스 i에 삽입 | O(N) | 원본 변경 |

### 삭제

| 메서드 | 동작 | 시간 복잡도 | 반환값 |
|--------|------|------------|-------|
| `arr.pop()` | 맨 뒤 삭제 | O(1) | 삭제된 원소 |
| `arr.shift()` | 맨 앞 삭제 | O(N) | 삭제된 원소 |
| `arr.splice(i, k)` | 인덱스 i부터 k개 삭제 | O(N) | 삭제된 배열 |

### 변환·조회

| 메서드 | 동작 | 비고 |
|--------|------|------|
| `arr.map(fn)` | 각 원소 변환 → 새 배열 | 원본 유지 |
| `arr.filter(fn)` | 조건 만족만 → 새 배열 | 원본 유지 |
| `arr.reduce((acc, x) => ..., init)` | 누적 | 원본 유지 |
| `arr.sort((a, b) => a - b)` | 오름차순 정렬 | **원본 변경**, 인수 없으면 문자열로 비교 |
| `arr.toSorted((a, b) => a - b)` | 오름차순 정렬 | 원본 유지, ES2023 |
| `arr.entries()` | `[index, value]` 이터레이터 | `for...of`와 함께 |
| `arr.includes(x)` | 포함 여부 | O(N) |

### sort의 비교 함수 규칙

`sort()`에 전달하는 비교 함수 `(a, b) => ...`의 반환값에 따라 동작한다.

| 반환값 | 의미 |
|--------|------|
| 음수 | a를 b보다 앞에 둔다 |
| 양수 | a를 b보다 뒤에 둔다 |
| 0 | 위치 변경 없음 |

오름차순은 `a - b`, 내림차순은 `b - a`를 반환하면 된다.

> **함정**: 비교 함수를 빠뜨린 `[1, 10, 5, 3, 100].sort()`는 `[1, 10, 100, 3, 5]`를 반환한다. 숫자를 문자열로 바라보고 정렬하기 때문이다. 숫자 정렬에는 항상 비교 함수를 명시할 것.

## 5. 몸풀기 문제

### 문제 01: 배열 정렬하기

> 정수 배열을 받아 오름차순으로 정렬해 반환하라.
> 권장 시간: 10분 / 권장 시간 복잡도: O(N log N)
> 제약: 길이 2 ≤ N ≤ 10⁵, 값 -100,000 ~ 100,000

**접근 아이디어**: N이 최대 10⁵이므로 O(N²) 정렬(버블·삽입)은 시간 초과 위험이 있다. `sort()`의 내장 정렬은 일반적으로 O(N log N)이라 안전하다.

```javascript
function solution(arr) {
  arr.sort((a, b) => a - b);
  return arr;
}
```

> **합격 조언**: O(N²) 버블 정렬과 `sort()` 비교 — 데이터 10,000개 역순 정렬 시 버블 정렬은 약 2,081ms, `sort()`는 약 1ms가 걸린다. 시간 복잡도의 차이가 실측에서도 크게 드러난다.

**시간 복잡도**: O(N log N)

### 문제 02: 배열 제어하기

> 정수 배열의 중복 값을 제거하고 내림차순으로 정렬해 반환하라.
> 권장 시간 복잡도: O(N log N)
> 제약: 길이 2 ≤ N ≤ 1,000

**접근 아이디어**: 중복 제거는 `Set`(해시 기반, O(N)), 정렬은 `sort()`(O(N log N)). 직접 반복문으로 중복 검사하면 O(N²)이라 비효율적이다.

```javascript
function solution(arr) {
  const uniqueArr = [...new Set(arr)]; // 중복 제거
  uniqueArr.sort((a, b) => b - a);     // 내림차순 정렬
  return uniqueArr;
}
```

> **핵심 통찰**: 자바스크립트 내장 기능이 풀어주는 문제를 굳이 직접 구현하지 마라. `Set`은 해시로 동작하므로 중복 제거가 O(N), 정렬은 `sort()`로 O(N log N)이면 충분하다.

**시간 복잡도**: O(N log N)

## 6. 합격자가 되는 모의테스트

### 문제 03: 두 개 뽑아서 더하기 — 프로그래머스

> 정수 배열 `numbers`에서 서로 다른 인덱스의 두 수를 뽑아 더한 모든 결과를 오름차순으로 담아 반환하라.
> 제약: 길이 2 ≤ N ≤ 100, 값 0 ~ 100
> [프로그래머스 #68644](https://programmers.co.kr/learn/courses/30/lessons/68644)

**접근 아이디어**:
1. 이중 반복문으로 두 수의 모든 조합을 더해 새 배열에 저장.
2. `Set`으로 중복 제거.
3. `sort()`로 오름차순 정렬.

N이 100이라 시간 복잡도는 신경 쓰지 않아도 된다.

**알고리즘 트레이스** (`numbers = [5, 0, 2, 7]`):

```
i\j  0       1        2
1   {5,0}=5
2   {5,2}=7  {0,2}=2
3   {5,7}=12 {0,7}=7  {2,7}=9
```

조합으로 나온 합 `[5, 7, 2, 12, 7, 9]` → 중복 제거 `[5, 7, 2, 12, 9]` → 정렬 `[2, 5, 7, 9, 12]`.

```javascript
function solution(numbers) {
  const ret = [];

  // 두 수의 모든 조합
  for (let i = 0; i < numbers.length; i++) {
    for (let j = 0; j < i; j++) {
      ret.push(numbers[i] + numbers[j]);
    }
  }

  // 중복 제거 + 오름차순 정렬
  return [...new Set(ret)].sort((a, b) => a - b);
}
```

**시간 복잡도**: 조합 O(N²) + 정렬 O(N² log(N²)) → O(N² log N)

### 문제 04: 모의고사 — 프로그래머스

> 수포자 3명이 정해진 패턴으로 모의고사 답을 찍는다. 정답 배열 `answers`가 주어졌을 때 가장 많이 맞힌 사람의 번호를 오름차순으로 반환하라.
> 제약: 답 길이 ≤ 10,000, 정답은 1~5
> [프로그래머스 #42840](https://programmers.co.kr/learn/courses/30/lessons/42840)

각 수포자의 패턴:

| 수포자 | 패턴 (반복) | 길이 |
|-------|------------|-----|
| 1 | 1, 2, 3, 4, 5 | 5 |
| 2 | 2, 1, 2, 3, 2, 4, 2, 5 | 8 |
| 3 | 3, 3, 1, 1, 2, 2, 4, 4, 5, 5 | 10 |

**접근 아이디어**:
1. 수포자의 패턴을 배열로 저장.
2. 정답을 순회하며 각 수포자의 답이 맞는지 비교 — 패턴 길이를 넘어가면 **나머지 연산(`%`)** 으로 다시 처음부터.
3. 최고 점수 = `Math.max(...scores)`를 구한 뒤, 그 점수와 같은 수포자 번호를 모은다.

```javascript
function solution(answers) {
  const patterns = [
    [1, 2, 3, 4, 5],
    [2, 1, 2, 3, 2, 4, 2, 5],
    [3, 3, 1, 1, 2, 2, 4, 4, 5, 5],
  ];

  const scores = [0, 0, 0];

  for (const [i, answer] of answers.entries()) {
    for (const [j, pattern] of patterns.entries()) {
      if (answer === pattern[i % pattern.length]) {
        scores[j] += 1;
      }
    }
  }

  const maxScore = Math.max(...scores);

  const highestScores = [];
  for (let i = 0; i < scores.length; i++) {
    if (scores[i] === maxScore) {
      highestScores.push(i + 1);
    }
  }

  return highestScores;
}
```

> **핵심 통찰**: `i % pattern.length`로 패턴이 무한 반복되는 효과를 얻는다. 정답 길이가 패턴보다 길어도 안전하게 비교할 수 있다.

**시간 복잡도**: O(N) — 패턴 수가 상수(3개)이므로 정답 길이에 비례.

### 문제 05: 행렬의 곱셈 — 프로그래머스

> 2차원 행렬 `arr1`, `arr2`를 받아 행렬 곱 결과를 반환하라.
> 제약: 행·열 길이 2 ≤ N ≤ 100
> [프로그래머스 #12949](https://school.programmers.co.kr/learn/courses/30/lessons/12949)

**행렬 곱 정의**: A가 (M × K), B가 (K × N)일 때 결과는 (M × N). 결과의 (i, j) 성분은 `Σₖ A[i][k] × B[k][j]`.

```javascript
function solution(arr1, arr2) {
  const r1 = arr1.length;
  const c1 = arr1[0].length;
  const c2 = arr2[0].length;

  // 결과 행렬 (r1 × c2) 0으로 초기화
  const ret = [];
  for (let i = 0; i < r1; i++) {
    ret.push(new Array(c2).fill(0));
  }

  for (let i = 0; i < r1; i++) {
    for (let j = 0; j < c2; j++) {
      for (let k = 0; k < c1; k++) {
        ret[i][j] += arr1[i][k] * arr2[k][j];
      }
    }
  }

  return ret;
}
```

> **합격 조언**: 결과 행렬을 미리 만들어 0으로 초기화하면 누적 연산(`+=`)이 자연스러워진다. 결과 행렬 크기를 모르면 행렬 곱 정의(A의 열 개수 = B의 행 개수)를 떠올려라.

**시간 복잡도**: O(N³) — 세 중첩 반복문의 각 차원이 모두 N에 비례.

### 문제 06: 실패율 — 2019 KAKAO BLIND

> 스테이지 N과 사용자별 도전 중인 스테이지 배열 `stages`가 주어진다. 실패율(=해당 스테이지에 도달했지만 클리어 못 한 사용자 수 / 도달한 사용자 수)이 높은 순서로 스테이지 번호를 반환하라. 같은 실패율이면 작은 번호 먼저.
> 제약: N ≤ 500, `stages` 길이 ≤ 200,000
> [프로그래머스 #42889](https://school.programmers.co.kr/learn/courses/30/lessons/42889)

**접근 아이디어**:
1. 각 스테이지에 멈춰 있는 사용자 수를 카운트 — `challenger[stage] += 1`.
2. 스테이지 1부터 N까지 순회하며 실패율 계산. 다음 스테이지의 도달자는 현재 도달자에서 멈춘 사람을 빼면 된다.
3. 실패율 기준 내림차순 정렬.

**알고리즘 트레이스** (`N=5, stages=[2, 1, 2, 6, 2, 4, 3, 3]`):

```
stage  challenger[stage]   total(도달자)   실패율
  1          1                  8         1/8
  2          3                  7         3/7  ← 가장 높음
  3          2                  4         2/4
  4          1                  2         1/2
  5          0                  1         0/1
```

내림차순 정렬: `[3, 4, 2, 1, 5]` (실패율 같은 경우 작은 번호 먼저).

```javascript
function solution(N, stages) {
  // ① 스테이지별 멈춰있는 사용자 수 카운트
  const challenger = new Array(N + 2).fill(0);
  for (const stage of stages) {
    challenger[stage] += 1;
  }

  // ② 실패율 계산
  const fails = {};
  let total = stages.length;

  for (let i = 1; i <= N; i++) {
    if (challenger[i] === 0) {
      fails[i] = 0;
      continue;
    }
    fails[i] = challenger[i] / total;
    total -= challenger[i]; // 다음 스테이지의 도달자
  }

  // ③ 실패율 내림차순 정렬
  const result = Object.entries(fails).sort((a, b) => b[1] - a[1]);

  // ④ 스테이지 번호만 추출
  return result.map((v) => Number(v[0]));
}
```

> **함정**: `challenger` 배열 크기를 `N + 2`로 한 이유 — 인덱스 0은 안 쓰지만, N+1(클리어한 사용자) 인덱스를 안전하게 쓰기 위해서다. 메모리 1칸 낭비로 인덱스 계산을 단순화한다.

> **함정**: `Object.entries(fails)`의 결과는 `[키, 값]` 형태이고 키는 **문자열**이다. 마지막에 `Number(v[0])`로 숫자 변환을 잊지 말 것.

**시간 복잡도**: O(M + N log N) — M은 stages 길이, N은 스테이지 수. 카운트가 O(N + M), 실패율 계산이 O(N), 정렬이 O(N log N).

### 문제 07: 방문 길이 — Summer/Winter Coding

> 명령어(U/D/R/L) 문자열 `dirs`로 캐릭터를 움직일 때, 처음 걸어본 길의 길이를 반환하라. 좌표 평면은 -5 ≤ x, y ≤ 5로 제한된다.
> [프로그래머스 #49994](https://school.programmers.co.kr/learn/courses/30/lessons/49994)

**접근 아이디어**:
1. **중복 경로 처리** → `Set`으로 방문한 경로를 저장.
2. **음수 좌표** → 그냥 좌표 그대로 쓰되, `Set`의 키를 문자열로 만들어서 저장하면 음수도 문제없다.
3. **방향성 제거**: A→B와 B→A는 같은 길이므로 양쪽 다 추가하고, 마지막에 `size / 2`를 반환.

```javascript
function isValidMove(nx, ny) {
  return nx >= -5 && nx <= 5 && ny >= -5 && ny <= 5;
}

function updateLocation(x, y, dir) {
  switch (dir) {
    case "U": return [x, y + 1];
    case "D": return [x, y - 1];
    case "R": return [x + 1, y];
    case "L": return [x - 1, y];
  }
}

function solution(dirs) {
  let x = 0;
  let y = 0;
  const visited = new Set();

  for (const dir of dirs) {
    const [nx, ny] = updateLocation(x, y, dir);

    if (!isValidMove(nx, ny)) continue; // 좌표 평면 벗어나면 무시

    // A→B와 B→A를 둘 다 저장
    visited.add(`${x},${y},${nx},${ny}`);
    visited.add(`${nx},${ny},${x},${y}`);

    [x, y] = [nx, ny];
  }

  return visited.size / 2;
}
```

> **함정**: `Set`에 객체를 직접 넣으면 참조 비교라 중복 검사가 동작하지 않는다. 좌표쌍은 반드시 **문자열**로 직렬화해서 저장할 것.

> **핵심 통찰**: 양방향 그래프의 간선을 처리할 때 자주 쓰는 패턴이다. A→B를 추가할 때 B→A도 함께 추가하면 방향성을 자연스럽게 제거할 수 있다.

**시간 복잡도**: O(N) — `dirs`의 길이만큼 순회.

## 7. 함정/실수 노트

| 함정 | 잘못된 코드 | 올바른 코드 |
|------|------------|------------|
| `sort()`를 인수 없이 호출 | `[1, 10, 5].sort()` → `[1, 10, 5]` | `[1, 10, 5].sort((a, b) => a - b)` |
| 2차원 배열을 같은 참조로 초기화 | `new Array(R).fill(new Array(C).fill(0))` | `Array.from({length: R}, () => new Array(C).fill(0))` |
| `Set`에 객체 넣고 중복 체크 | `set.add({x, y})` | `set.add(\`${x},${y}\`)` |
| `Object.entries()` 키를 그대로 비교 | `entries[0] === 1` (문자열 vs 숫자) | `Number(entries[0]) === 1` |
| `splice`를 호출하고 반환값을 그대로 쓰기 | `arr = arr.splice(0, 2)` | `splice`는 **삭제된 원소**를 반환 — 원본 배열은 수정됨 |
| `unshift` 남용으로 시간 초과 | 큰 배열에 매 반복마다 `unshift` | 끝에 push하고 마지막에 `reverse()`하거나 `Deque` 검토 |
| `arr.indexOf(x)` 반복 호출 | O(N²)로 폭발 | `Set`이나 `Map`으로 O(1) 조회 |

## 8. 요약

- **배열은 같은 타입 데이터를 인덱스로 임의 접근하는 자료구조**다. 자바스크립트의 배열은 동적 크기이며 `Array` 객체로 동작한다.
- **임의 접근과 맨 뒤 추가/삭제는 O(1)**, **맨 앞·중간 삽입/삭제는 O(N)** 이다. 데이터 양이 많고 중간 삽입이 빈번하면 다른 자료구조를 검토할 것.
- **2차원 배열의 메모리 배치는 1차원**이다. 행 단위로 저장된다는 사실이 인덱스 계산의 핵심이다.
- 자바스크립트의 **`Set`은 해시 기반이라 중복 제거가 O(N)** 이다. 직접 구현하지 말 것.
- **`sort()`는 비교 함수가 필수**다. 인수 없이 호출하면 문자열 정렬이 된다.
- **고차 함수(`map`, `filter`, `reduce`)는 원본을 변경하지 않고 새 배열을 반환**한다.
- **좌표·복합 키를 `Set`/`Map`의 키로 쓸 때는 문자열로 직렬화**해야 한다.

## 리마인드 (저자)

1. 자바스크립트에서는 `Array`로 배열을 사용한다.
2. 배열은 임의 접근으로 모든 위치에 바로 접근할 수 있다.
3. 중간에 데이터를 삽입할 일이 많다면 배열은 비효율적이다. 다른 방법을 생각해야 한다.
