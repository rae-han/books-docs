# Chapter 12: Backtracking (백트래킹)

## 핵심 질문

가능성이 없는 경로는 미리 가지치고, 가능성이 있는 경로만 깊이 탐색하려면 어떻게 해야 하는가? 유망 함수는 어떻게 정의하고, 완전 탐색과 어떤 차이가 있는가?

## 1. 백트래킹 개념

지하철 개찰구에서 지갑을 두고 온 걸 깨달았다고 해보자. 집으로 돌아가는 길에 옆집 문 앞에 섰다가 "여긴 우리 집이 아니구나" 하고 곧장 우리 집으로 돌아온다. 이렇게 **가능성이 없는 곳을 알아보고 되돌아가는 것이 백트래킹(backtracking)** 이다.

### 백트래킹 알고리즘이란?

가능성이 없는 곳에서는 되돌아가고, 가능성이 있는 곳을 탐색하는 알고리즘. 모든 경우를 탐색하는 **완전 탐색(brute force)** 보다 효율적이다. 단, 문제마다 효율이 달라 시간 복잡도를 일반화하기 어렵다.

> **핵심 통찰**: 백트래킹과 완전 탐색의 차이는 "유망 함수의 유무"다. 유망 함수가 답이 될 가능성이 없다고 판단한 경로는 아예 탐색하지 않으므로 그만큼 시간을 절약한다.

DFS도 더 이상 갈 곳이 없을 때 백트래킹을 활용한다. 백트래킹 알고리즘은 그보다 한 단계 더 나아가, **해가 될 가능성이 없는 경로를 미리 잘라낸다**. 이를 가지치기(pruning) 또는 분기한정(branch and bound)이라고도 부른다.

### 유망 함수(promising function)

백트래킹의 핵심은 "해가 될 가능성을 판단하는 것"이고, 그 판단을 **유망 함수**가 한다.

백트래킹 알고리즘은 다음 4단계를 따른다.

1. 유효한 해의 집합을 정의한다.
2. 정의한 집합을 그래프로 표현한다.
3. 유망 함수를 정의한다.
4. 백트래킹으로 해를 찾는다.

### 예시: 합이 6을 넘는 경우 찾기

`{1, 2, 3, 4}`에서 두 수를 뽑아 합이 6을 초과하는 경우를 찾는다고 해보자(순서가 다르면 다른 경우로 친다). 유망 함수는 "처음에 뽑은 숫자가 3 미만이면 백트래킹"으로 정의한다.

```
시작점
├── [1] ──❌ (유망 함수 통과 못함, 백트래킹)
├── [2] ──❌ (유망 함수 통과 못함, 백트래킹)
├── [3] ✓
│   ├── [3, 1] = 4   (답 아님)
│   ├── [3, 2] = 5   (답 아님)
│   └── [3, 4] = 7   ✓ 정답
└── [4] ✓
    ├── [4, 1] = 5   (답 아님)
    ├── [4, 2] = 6   (답 아님)
    └── [4, 3] = 7   ✓ 정답
```

`[1]`, `[2]`로 시작하는 경로는 유망 함수에서 걸러지므로 그 하위 경로 6개를 모두 건너뛴다.

> **합격 조언**: 유망 함수는 같은 문제에서도 다양하게 정의할 수 있다. 더 강한 조건을 발견하면 탐색 공간이 크게 줄어든다. "현재까지의 합이 ~보다 크면 백트래킹" 같은 누적 조건이 자주 쓰인다.

## 2. 핵심 코드 패턴

### 백트래킹의 일반 템플릿

```javascript
function backtrack(state) {
  // 1. 종료 조건 — 해를 찾으면 결과에 추가
  if (isSolution(state)) {
    results.push([...state]); // 깊은 복사 주의
    return;
  }

  // 2. 후보 선택 — 분기
  for (const choice of candidates(state)) {
    // 3. 유망 함수 — 가지치기
    if (!isPromising(state, choice)) continue;

    // 4. 선택
    state.push(choice);
    backtrack(state);

    // 5. 되돌리기 (백트래킹의 핵심)
    state.pop();
  }
}
```

**핵심**: 재귀 호출 후 반드시 **상태를 원래대로 되돌려야** 한다. `state.pop()`이 빠지면 다른 분기에서 잘못된 상태로 탐색하게 된다.

### 순열 (permutation) — 순서 있음

```javascript
function permutations(arr, n) {
  if (n === 0) return [[]];

  const result = [];
  arr.forEach((fixed, idx) => {
    const rest = [...arr];
    rest.splice(idx, 1);
    const perms = permutations(rest, n - 1);
    const combine = perms.map((p) => [fixed, ...p]);
    result.push(...combine);
  });
  return result;
}
```

### 조합 (combination) — 순서 없음

중복 허용하지 않는 조합:

```javascript
function combinations(arr, n) {
  if (n === 1) return arr.map((v) => [v]);
  const result = [];
  arr.forEach((fixed, idx, original) => {
    const rest = original.slice(idx + 1); // 자신 이후 원소만
    const combis = combinations(rest, n - 1);
    const combine = combis.map((v) => [fixed, ...v]);
    result.push(...combine);
  });
  return result;
}
```

중복 허용하는 조합 (같은 원소를 여러 번 뽑을 수 있음):

```javascript
function combinationsWithRepetition(arr, n) {
  if (n === 1) return arr.map((v) => [v]);
  const result = [];
  arr.forEach((fixed, idx, original) => {
    const rest = original.slice(idx); // 자신부터 (중복 허용)
    const combis = combinationsWithRepetition(rest, n - 1);
    const combine = combis.map((v) => [fixed, ...v]);
    result.push(...combine);
  });
  return result;
}
```

| 함수 | `[0, 1, 2]`에서 2개 뽑기 |
|------|------------------------|
| `combinations` | `[0,1] [0,2] [1,2]` |
| `combinationsWithRepetition` | `[0,0] [0,1] [0,2] [1,1] [1,2] [2,2]` |

### 방문 체크 — 좌표

```javascript
const visited = new Set();
visited.add(`${r},${c}`);   // 객체가 아닌 문자열로 직렬화
```

### 분기 한정 — 시간 단축

```javascript
if (currentSum + candidate > target) continue; // 가지치기
```

## 3. JavaScript 빌트인 메서드 레퍼런스

| 메서드 | 동작 | 백트래킹 활용 |
|--------|------|--------------|
| `Math.max(...arr)`, `Math.min(...arr)` | 배열 최대/최솟값 | 최적해 갱신 |
| `arr.includes(x)` | 포함 여부 | 행/열 중복 체크 |
| `arr.some(fn)` | 하나라도 만족 | 열 중복 체크 |
| `Array(n).fill(false)` | boolean 배열 | 방문 표시 |
| `Set` | 빠른 중복 체크 | 방문 좌표 저장 |
| `arr.concat(x)` | 새 배열 반환 | 상태 변형 없이 분기 |

## 4. 몸풀기 문제

### 문제 47: 1부터 N까지 숫자 중 합이 10이 되는 조합

> 정수 N을 받아 1부터 N까지 숫자 중 합이 10이 되는 조합을 배열로 반환하라. 같은 숫자는 한 번만 선택, 조합은 오름차순 정렬.
> 권장 시간 복잡도: O(N!)

**입출력 예**:

| N | result |
|---|-----|
| 5 | `[[1,2,3,4], [1,4,5], [2,3,5]]` |
| 2 | `[]` |
| 7 | `[[1,2,3,4], [1,2,7], [1,3,6], [1,4,5], [2,3,5], [3,7], [4,6]]` |

**유망 함수**:
- 합이 10이 되면 결과에 추가하고 종료.
- 합이 10보다 커지면 백트래킹.

```javascript
function solution(N) {
  const results = [];

  function backtrack(sum, selectedNums, start) {
    if (sum === 10) { // 합이 10이면 결과 추가
      results.push(selectedNums);
      return;
    }

    for (let i = start; i <= N; i++) {
      if (sum + i <= 10) { // 유망 함수: 합이 10 이하일 때만
        backtrack(sum + i, selectedNums.concat(i), i + 1);
      }
    }
  }

  backtrack(0, [], 1);
  return results;
}
```

> **핵심 통찰**: `start` 파라미터로 "이전에 뽑은 숫자보다 큰 값만" 뽑게 만들면, 자연스럽게 오름차순이 보장되고 중복 조합도 사라진다.

**시간 복잡도**: O(N!) — 다만 유망 함수로 실제 연산은 훨씬 적다.

### 문제 48: 스도쿠 퍼즐

> 9×9 스도쿠 보드를 받아 빈 칸(0)을 채운 보드를 반환하라.
> 권장 시간 복잡도: O(9^M) (M은 빈 칸 개수)

**규칙**:
- 가로 줄·세로 줄에 1~9가 각 한 번씩.
- 3×3 박스에도 1~9가 각 한 번씩.

**유망 함수**: 행, 열, 3×3 박스에 같은 숫자가 있으면 백트래킹.

```javascript
function solution(board) {
  function isValid(num, row, col) {
    return !(inRow(num, row) || inCol(num, col) || inBox(num, row, col));
  }

  function inRow(num, row) {
    return board[row].includes(num);
  }

  function inCol(num, col) {
    return board.some((row) => row[col] === num);
  }

  function inBox(num, row, col) {
    const boxRow = Math.floor(row / 3) * 3;
    const boxCol = Math.floor(col / 3) * 3;
    for (let i = boxRow; i < boxRow + 3; i++) {
      for (let j = boxCol; j < boxCol + 3; j++) {
        if (board[i][j] === num) return true;
      }
    }
    return false;
  }

  function findEmptyPosition() {
    for (let i = 0; i < 9; i++) {
      for (let j = 0; j < 9; j++) {
        if (board[i][j] === 0) return [i, j];
      }
    }
    return null;
  }

  function findSolution() {
    const emptyPos = findEmptyPosition();
    if (!emptyPos) return true; // 빈 칸 없으면 완성

    const [row, col] = emptyPos;
    for (let num = 1; num <= 9; num++) {
      if (isValid(num, row, col)) {
        board[row][col] = num;
        if (findSolution()) return true; // 정답 찾음
        board[row][col] = 0; // 백트래킹: 원래대로
      }
    }
    return false;
  }

  findSolution();
  return board;
}
```

> **합격 조언**: 3×3 박스의 시작 인덱스는 `Math.floor(row / 3) * 3`으로 구한다. 행 인덱스 0~2 → 박스 시작 0, 3~5 → 3, 6~8 → 6.

**시간 복잡도**: O(9^M) — M은 빈 칸 개수. 유망 함수로 대부분의 경로를 잘라낸다.

## 5. 합격자가 되는 모의테스트

### 문제 49: 피로도 — 프로그래머스

> 게임의 피로도 시스템. 각 던전은 [최소 필요 피로도, 소모 피로도]를 가진다. 현재 피로도 `k`로 최대한 많이 탐험할 수 있는 던전 수를 반환하라.
> 제약: k ≤ 5,000, 던전 개수 ≤ 8
> [프로그래머스 #87946](https://school.programmers.co.kr/learn/courses/30/lessons/87946)

**유망 함수**: 현재 피로도가 던전의 최소 필요 피로도보다 낮으면 백트래킹.

**알고리즘 트레이스** (`k=80, dungeons=[[80,20],[50,40],[30,10]]`):

```
시작 80
├── [80,20] → 60
│   ├── [50,40] → 20 → [30,10] ❌ (20 < 30, 백트래킹)
│   └── [30,10] → 50 → [50,40] → 10 ✓ (3 던전)
├── [50,40] → 40
│   └── [80,20] ❌
└── [30,10] → 70
    ├── [80,20] ❌ (70 < 80)
    └── [50,40] → 30 → [80,20] ❌
```

```javascript
function dfs(curk, cnt, dungeons, visited) {
  let answerMax = cnt;

  for (let i = 0; i < dungeons.length; i++) {
    // 유망 함수: 피로도 충분 + 미방문
    if (curk >= dungeons[i][0] && visited[i] === 0) {
      visited[i] = 1;
      answerMax = Math.max(
        answerMax,
        dfs(curk - dungeons[i][1], cnt + 1, dungeons, visited)
      );
      visited[i] = 0; // 백트래킹: 방문 해제
    }
  }

  return answerMax;
}

function solution(k, dungeons) {
  const visited = Array(dungeons.length).fill(0);
  return dfs(k, 0, dungeons, visited);
}
```

> **함정**: `visited[i] = 0`으로 되돌리는 부분을 빠뜨리면 다른 분기에서 "이미 방문한 것처럼" 동작해 답이 틀어진다. 백트래킹의 본질인 **상태 복원**을 잊지 말 것.

**시간 복잡도**: O(N!) — 던전 개수 N이 작아서 가능.

### 문제 50: N-퀸 — 프로그래머스

> N×N 체스판에 N개의 퀸을 서로 공격할 수 없도록 배치하는 경우의 수를 반환하라.
> 권장 시간 복잡도: O(N!)
> [프로그래머스 #12952](https://school.programmers.co.kr/learn/courses/30/lessons/12952)

**유망 함수**: 같은 행, 같은 열, 같은 대각선에 다른 퀸이 있으면 백트래킹.

**대각선 관리 트릭**:
- `diagonal1[i + y]` — 오른쪽 위 ↘ 왼쪽 아래 방향 (행+열이 일정)
- `diagonal2[i - y + n]` — 왼쪽 위 ↗ 오른쪽 아래 방향 (행-열이 일정, 음수 방지로 +n)

대각선 배열 크기는 `n*2`로 잡는다 (대각선 개수가 `2n - 1`이므로).

```javascript
function solution(n) {
  function search(n, y, width, diagonal1, diagonal2) {
    let answer = 0;

    // 모든 행에 퀸이 놓였으면 한 가지 해
    if (y === n) {
      answer += 1;
    } else {
      // 현재 행의 모든 열을 시도
      for (let i = 0; i < n; i++) {
        // 유망 함수: 같은 열·대각선에 퀸이 있으면 스킵
        if (width[i] || diagonal1[i + y] || diagonal2[i - y + n]) {
          continue;
        }

        // 퀸 배치
        width[i] = diagonal1[i + y] = diagonal2[i - y + n] = true;
        answer += search(n, y + 1, width, diagonal1, diagonal2);
        // 백트래킹: 원래대로
        width[i] = diagonal1[i + y] = diagonal2[i - y + n] = false;
      }
    }

    return answer;
  }

  return search(
    n, 0,
    Array(n).fill(false),
    Array(n * 2).fill(false),
    Array(n * 2).fill(false)
  );
}
```

> **핵심 통찰**: 대각선 정보를 `Set`이 아닌 boolean 배열로 관리하면 인덱스 접근이 O(1)이고 메모리도 효율적이다. 두 대각선의 행+열, 행-열이 같은 칸들끼리 묶이는 성질을 이용한다.

**시간 복잡도**: O(N!) — 각 행에 한 개의 퀸만 들어가므로 첫 행 N개, 두 번째 N-1개...

### 문제 51: 양궁 대회 — 2022 KAKAO BLIND

> 어피치가 화살 n발을 다 쏜 후 라이언이 n발을 쏜다. 0~10점 과녁에서 더 많이 맞힌 사람이 점수를 가져간다. 라이언이 가장 큰 점수 차로 우승하는 화살 분배(0~10점 각 몇 발)를 반환하라. 동점이면 어피치 승. 라이언이 우승할 수 없으면 `[-1]`. 가장 큰 점수 차가 같으면 **낮은 점수를 더 많이 맞힌 경우**를 반환.
> 제약: 1 ≤ n ≤ 10
> [프로그래머스 #92342](https://school.programmers.co.kr/learn/courses/30/lessons/92342)

**접근 아이디어**:
- 화살을 어디에 맞히는지는 **순서가 무관**(점수에 영향 X)이므로 **조합** 문제.
- 한 과녁을 여러 번 맞힐 수 있으므로 **중복 허용 조합**.
- 모든 가능한 라이언 분배에 대해 점수 차를 계산하고 최댓값 갱신.

```javascript
function combinationsWithRepetition(arr, n) {
  if (n === 1) return arr.map((v) => [v]);
  const result = [];
  arr.forEach((fixed, idx, original) => {
    const rest = original.slice(idx);
    const combis = combinationsWithRepetition(rest, n - 1);
    const combine = combis.map((v) => [fixed, ...v]);
    result.push(...combine);
  });
  return result;
}

function solution(n, info) {
  let maxdiff = 0;
  let maxComb = {};

  function calculateScore(combi) {
    let scoreApeach = 0;
    let scoreLion = 0;
    for (let i = 1; i <= 10; i++) {
      const lionShots = combi.filter((x) => x === i).length;
      if (info[10 - i] < lionShots) {
        scoreLion += i;
      } else if (info[10 - i] > 0) {
        scoreApeach += i;
      }
    }
    return [scoreApeach, scoreLion];
  }

  function updateMax(diff, cnt) {
    if (diff > maxdiff) { // ">"가 아닌 ">="를 쓰면 동점 처리 망가짐
      maxComb = { ...cnt };
      maxdiff = diff;
    }
  }

  // 0~10에서 n개 뽑는 중복 조합 — combi는 라이언이 점수별로 쏜 횟수
  for (const combi of combinationsWithRepetition([...Array(11).keys()], n)) {
    const cnt = combi.reduce((acc, cur) => {
      acc[cur] = (acc[cur] || 0) + 1;
      return acc;
    }, {});

    const [scoreApeach, scoreLion] = calculateScore(combi);
    const diff = scoreLion - scoreApeach;
    updateMax(diff, cnt);
  }

  if (maxdiff > 0) {
    const answer = Array(11).fill(0);
    for (const score of Object.keys(maxComb)) {
      answer[10 - score] = maxComb[score];
    }
    return answer;
  } else {
    return [-1];
  }
}
```

> **함정**: "동점일 때 낮은 점수를 더 많이 맞힌 경우 반환" 조건을 처리하려면 `diff > maxdiff` (strict)로 비교해야 한다. `>=`로 하면 나중에 발견된(점수가 더 높은 쪽이 많은) 경우로 덮어쓰여 버린다. `combinationsWithRepetition`의 탐색 순서가 낮은 점수부터이므로, **먼저 발견된 답이 자동으로 "낮은 점수를 더 많이 맞힌" 답**이 된다.

> **함정**: 두 사람 모두 0발인 과녁은 누구도 점수를 못 가져간다. `else if (info[10 - i] > 0)`의 strict 비교를 빠뜨리지 말 것.

**시간 복잡도**: O(2^11) — 각 과녁마다 맞힌다/안 맞힌다 두 상태이므로.

### 문제 52: 외벽 점검 — 2020 KAKAO BLIND

> 둘레 n m의 원형 외벽. 취약 지점 배열 `weak`와 친구별 1시간 이동 거리 `dist`가 주어진다. 모든 취약 지점을 점검할 최소 친구 수를 반환하라. 불가능하면 `-1`.
> 제약: n ≤ 200, weak ≤ 15, dist ≤ 8
> [프로그래머스 #60062](https://school.programmers.co.kr/learn/courses/30/lessons/60062)

**접근 핵심**:

1. **친구 이동 방향은 한 방향만 고려해도 된다**. 시계 방향 탐색이 반시계 방향의 결과를 모두 커버한다.
2. **원형을 선형으로**: 11에서 1로 가는 이동은 11에서 13으로 가는 이동과 같다. `weak`에 `weak[i] + n`을 추가해 배열을 두 배로 늘리면 된다.
3. **친구 배치 순서는 순열**(같은 거리 친구가 어느 위치에 가는지가 결과를 결정).

**알고리즘**:
1. weak 확장: `[1, 5, 6, 10]` → `[1, 5, 6, 10, 13, 17, 18, 22]`.
2. 모든 시작점 × 모든 친구 순열 조합으로 탐색.
3. 시작점부터 친구를 차례로 배치. 다음 weak 지점이 현재 친구의 도달 범위를 넘으면 다음 친구 투입.

```javascript
function permutations(arr, n) {
  if (n === 0) return [[]];
  const result = [];
  arr.forEach((fixed, idx) => {
    const rest = [...arr];
    rest.splice(idx, 1);
    const perms = permutations(rest, n - 1);
    const combine = perms.map((p) => [fixed, ...p]);
    result.push(...combine);
  });
  return result;
}

function solution(n, weak, dist) {
  // ① 원형 → 선형: weak를 두 배로 확장
  const length = weak.length;
  for (let i = 0; i < length; i++) {
    weak.push(weak[i] + n);
  }

  // ② 초깃값: 친구 수 + 1 (못 풀면 그대로)
  let answer = dist.length + 1;

  // ③ 모든 시작 weak × 친구 순열
  for (let i = 0; i < length; i++) {
    for (const friends of permutations(dist, dist.length)) {
      let cnt = 1;
      let position = weak[i] + friends[cnt - 1];

      // ④ 시작 weak[i]부터 length개 점검 시도
      for (let j = i; j < i + length; j++) {
        if (position < weak[j]) {
          cnt += 1;
          if (cnt > dist.length) break; // 친구 부족
          position = weak[j] + friends[cnt - 1];
        }
      }

      answer = Math.min(answer, cnt);
    }
  }

  return answer <= dist.length ? answer : -1;
}
```

> **핵심 통찰**: 회전 대칭이 있는 원형 문제는 "선형 + 시작점 순회"로 바꿀 수 있다. 배열을 2배 확장하는 트릭은 원형 문제에서 광범위하게 쓰인다.

**시간 복잡도**: O(M² × N!) — M=weak 길이, N=dist 길이. 친구 순열이 비싸지만 dist ≤ 8이라 가능.

### 문제 53: 사라지는 발판 — 2022 KAKAO BLIND (고난이도)

> 두 플레이어 A, B가 1×1 발판 위에서 게임. 자기 차례에 상하좌우로 이동하면 밟고 있던 발판이 사라진다. 이동할 곳이 없으면 패배. A부터 시작. 양 플레이어가 **최적의 플레이**를 했을 때 이동 횟수의 합을 반환하라.
> 제약: 보드 ≤ 5×5
> [프로그래머스 #92345](https://school.programmers.co.kr/learn/courses/30/lessons/92345)

**최적의 플레이 정의**:
- 이길 수 있다면 **최대한 빨리** 이긴다.
- 질 수밖에 없다면 **최대한 오래** 버틴다.

**미니맥스 백트래킹**의 전형. 현재 플레이어가 모든 가능한 이동을 시도하고, 그 결과로:
- 한 번이라도 이기는 수가 있으면 → 현재 플레이어는 이긴다 → **승리 경로 중 최소 step**.
- 모든 수가 진다면 → 현재 플레이어는 진다 → **패배 경로 중 최대 step**.

```javascript
function solution(board, aloc, bloc) {
  const ROW = board.length;
  const COL = board[0].length;
  const DR = [-1, 0, 1, 0];
  const DC = [0, 1, 0, -1];

  function isValidPos(r, c) {
    return 0 <= r && r < ROW && 0 <= c && c < COL;
  }

  function recursiveFunc(alphaPos, betaPos, visited, step) {
    const [r, c] = step % 2 === 0 ? alphaPos : betaPos;
    let canMove = false;
    let isOpponentWinner = true;
    const winSteps = [];
    const loseSteps = [];

    for (let i = 0; i < 4; i++) {
      const nr = r + DR[i];
      const nc = c + DC[i];

      if (
        isValidPos(nr, nc) &&
        !visited.has(`${nr},${nc}`) &&
        board[nr][nc]
      ) {
        canMove = true;

        // 이동 후 같은 칸이면 즉시 현재 플레이어 승리
        if (alphaPos[0] === betaPos[0] && alphaPos[1] === betaPos[1]) {
          return [true, step + 1];
        }

        // 재귀: 반환값은 "다음 차례 = 상대 플레이어" 기준
        const [opponentWin, stepsLeft] = step % 2 === 0
          ? recursiveFunc([nr, nc], betaPos, new Set([...visited, `${r},${c}`]), step + 1)
          : recursiveFunc(alphaPos, [nr, nc], new Set([...visited, `${r},${c}`]), step + 1);

        isOpponentWinner = isOpponentWinner && opponentWin;

        if (opponentWin) {
          winSteps.push(stepsLeft);  // 상대가 이김 = 나는 짐
        } else {
          loseSteps.push(stepsLeft); // 상대가 짐 = 나는 이김
        }
      }
    }

    if (!canMove) {
      return [false, step]; // 못 움직이면 현재 플레이어 패
    }

    if (isOpponentWinner) {
      // 모든 경우에 상대가 이김 = 나는 무조건 짐 → 최대한 오래 버티기
      return [false, Math.max(...winSteps)];
    }

    // 이기는 경우가 있음 → 최단 승리
    return [true, Math.min(...loseSteps)];
  }

  const [, steps] = recursiveFunc(aloc, bloc, new Set(), 0);
  return steps;
}
```

> **함정**: 재귀 호출의 반환값은 **호출한 후의 상태 = 상대 플레이어 차례**의 결과다. 따라서 `opponentWin === true`면 상대가 이긴다는 뜻이고, 현재 플레이어 입장에서는 패배 경로다. 시점 전환을 헷갈리지 말 것.

> **함정**: `visited`를 매번 새로 만들어야 한다. 같은 Set을 공유하면 다른 분기의 방문 정보가 섞인다. `new Set([...visited, ...])`로 매번 복사.

> **핵심 통찰**: 게임 이론 문제는 "현재 플레이어가 이기는가?"와 "그때 이동 횟수는?"을 함께 반환하는 패턴이 표준이다. 미니맥스 + 백트래킹.

**시간 복잡도**: O(4^(M·N)) — 각 칸에서 상하좌우 4개 분기.

## 6. 함정/실수 노트

| 함정 | 설명 |
|------|------|
| 백트래킹 후 상태 복원 누락 | `visited[i] = 0` 등을 빠뜨리면 다른 분기에서 잘못된 상태 |
| 결과 배열에 참조 그대로 push | `state` 자체를 push하면 이후 변경이 결과에도 반영. `[...state]`로 복사 |
| `Set`에 객체 직접 저장 | 좌표쌍은 `` `${r},${c}` `` 같은 문자열로 직렬화 |
| `combinations` vs `combinationsWithRepetition` | 같은 원소를 여러 번 뽑을 수 있는지로 결정 — 양궁 대회는 후자 |
| `>=` vs `>`로 최댓값 갱신 | "처음 발견한 값을 우선" 조건이 있으면 strict 비교(`>`)를 써야 함 |
| 미니맥스에서 시점 혼동 | 재귀 반환값은 다음 차례(상대) 기준임을 명심 |
| 원형 배열을 그대로 처리 | 배열 2배 확장 트릭으로 선형화 |
| 대각선 인덱스 음수 | `i - y + n`처럼 양수 오프셋 추가 |
| 가지치기 빠뜨려서 시간 초과 | 누적 합·도달 가능성 등 강한 유망 함수 추가 |

## 7. 요약

- **백트래킹은 가능성이 없는 경로를 미리 가지치는 탐색 기법**이다. 완전 탐색의 부분 집합이지만 효율이 훨씬 좋다.
- **유망 함수가 백트래킹의 핵심**이다. 강한 유망 함수일수록 탐색 공간이 줄어든다.
- **상태 복원**이 백트래킹의 형식적 본질이다. 재귀 호출 후 변경한 상태를 반드시 되돌려야 한다.
- **순열·조합·중복 조합**의 차이를 명확히 알고 있어야 한다. 문제의 "순서가 의미 있는가?" "중복이 가능한가?"로 판단.
- **방문 체크는 boolean 배열 또는 Set**(좌표는 문자열로 직렬화)을 활용.
- **원형 문제는 배열 2배 확장**으로 선형화한다.
- **N-퀸의 대각선 관리**는 `행+열`과 `행-열` 두 배열로 O(1) 체크가 가능하다.
- **게임 이론은 미니맥스 + 백트래킹**으로 풀며, 재귀 반환값의 시점이 다음 차례(상대) 기준임에 주의한다.

## 리마인드 (저자)

1. 백트래킹은 해를 찾는 도중 현재 경로가 해가 될 수 없다고 판단하면 해당 경로를 포기하고 이전으로 되돌아가 다른 경로를 탐색하는 방법이다.
2. 백트래킹에서 현재 경로가 해가 될 수 있는지 확인하는 함수를 유망 함수라고 한다.
3. 깊이 우선 탐색은 그래프나 트리의 모든 노드를 방문하는 알고리즘이고, 백트래킹은 특정 조건에 부합하는 해결책을 찾기 위해 가능한 모든 경로를 탐색하는 알고리즘이다.
