# Chapter 13: DFS/BFS 기출문제

> Ch 05에서 배운 DFS/BFS와 완전 탐색의 기출문제 모음(Q15~Q22). 격자 탐색, "벽/장애물 N개 설치" 완전 탐색, 회전·연합 같은 시뮬레이션이 결합된다.

## 핵심 질문

- 최단 거리는 BFS, "모든 배치 시도 후 탐색"은 완전 탐색 + BFS 조합인가?
- 벽·장애물을 정해진 개수만큼 설치하는 문제는 **조합 완전 탐색**으로 푸는가?
- 회전·연합·전염 같은 상태 변화를 정확히 BFS로 모델링했는가?

> 조합·순열 헬퍼(`combinations`, `permutations`)는 Ch 12에서 정의한 것을 재사용한다.

---

## Q15 특정 거리의 도시 찾기

| 항목 | 값 |
|------|-----|
| 난이도 | ★★ 중하 |
| 기출 | 백준 18352 |

### 문제 요약

모든 도로 거리가 1인 단방향 그래프에서, X에서 **최단 거리가 정확히 K**인 도시를 오름차순 출력. 없으면 -1.

예: N=4, K=2, X=1, 도로 `(1,2)(1,3)(2,3)(2,4)` → `4`

### 핵심 아이디어

가중치 1 최단 거리이므로 **BFS**. 거리 배열을 채운 뒤 K인 도시를 모은다.

```ts
function solve(input: string): number[] {
  const lines = input.split("\n");
  const [n, m, k, x] = lines[0].split(" ").map(Number);
  const graph: number[][] = Array.from({ length: n + 1 }, () => []);
  for (let i = 1; i <= m; i++) {
    const [a, b] = lines[i].split(" ").map(Number);
    graph[a].push(b);
  }
  const dist = new Array(n + 1).fill(-1);
  dist[x] = 0;
  const queue = [x];
  let head = 0;
  while (head < queue.length) {
    const now = queue[head++];
    for (const next of graph[now]) {
      if (dist[next] === -1) {
        dist[next] = dist[now] + 1;
        queue.push(next);
      }
    }
  }
  const result: number[] = [];
  for (let i = 1; i <= n; i++) {
    if (dist[i] === k) {
      result.push(i);
    }
  }
  return result.length > 0 ? result : [-1];
}
```

## Q16 연구소

| 항목 | 값 |
|------|-----|
| 난이도 | ★★★ 중 |
| 기출 | 백준 14502 |

### 문제 요약

빈 칸(0)에 **벽 3개를 세워** 바이러스(2) 확산을 막을 때 **안전 영역(0) 최대 크기**를 구하라.

### 핵심 아이디어

빈 칸 중 3개를 고르는 **조합 완전 탐색**(N,M ≤ 8이라 가능). 각 배치마다 BFS로 바이러스를 퍼뜨리고 남은 0을 센다.

```ts
function lab(n: number, m: number, board: number[][]): number {
  const empties: [number, number][] = [];
  const viruses: [number, number][] = [];
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < m; j++) {
      if (board[i][j] === 0) {
        empties.push([i, j]);
      } else if (board[i][j] === 2) {
        viruses.push([i, j]);
      }
    }
  }
  const dx = [-1, 1, 0, 0];
  const dy = [0, 0, -1, 1];
  let maxSafe = 0;

  for (const combo of combinations(empties, 3)) {
    const temp = board.map((row) => [...row]);
    for (const [x, y] of combo) {
      temp[x][y] = 1;
    }
    // 바이러스 BFS 확산
    const queue = viruses.map((v): [number, number] => [v[0], v[1]]);
    let head = 0;
    while (head < queue.length) {
      const [x, y] = queue[head++];
      for (let d = 0; d < 4; d++) {
        const nx = x + dx[d];
        const ny = y + dy[d];
        if (nx >= 0 && nx < n && ny >= 0 && ny < m && temp[nx][ny] === 0) {
          temp[nx][ny] = 2;
          queue.push([nx, ny]);
        }
      }
    }
    let safe = 0;
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < m; j++) {
        if (temp[i][j] === 0) {
          safe++;
        }
      }
    }
    maxSafe = Math.max(maxSafe, safe);
  }
  return maxSafe;
}
```

## Q17 경쟁적 전염

| 항목 | 값 |
|------|-----|
| 난이도 | ★★★ 중 |
| 기출 | 백준 18405 |

### 문제 요약

매 초 바이러스가 상하좌우로 증식하되 **번호가 낮은 종류부터** 먼저 퍼진다. S초 후 (X,Y)의 바이러스 종류를 구하라.

예: 3×3에 1,2,3 배치, S=2, (3,2) → `3`

### 핵심 아이디어

`[번호, 시간, x, y]`를 **번호 오름차순으로 정렬한 큐**로 BFS. 같은 시간대에서는 번호 낮은 것이 먼저 처리되도록 초기 정렬을 유지한다.

```ts
function infection(n: number, board: number[][], s: number, tx: number, ty: number): number {
  const viruses: [number, number, number, number][] = [];
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      if (board[i][j] !== 0) {
        viruses.push([board[i][j], 0, i, j]); // [번호, 시간, x, y]
      }
    }
  }
  viruses.sort((a, b) => a[0] - b[0]); // 번호 낮은 순
  const dx = [-1, 1, 0, 0];
  const dy = [0, 0, -1, 1];
  let head = 0;
  while (head < viruses.length) {
    const [virus, time, x, y] = viruses[head++];
    if (time === s) {
      break;
    }
    for (let d = 0; d < 4; d++) {
      const nx = x + dx[d];
      const ny = y + dy[d];
      if (nx >= 0 && nx < n && ny >= 0 && ny < n && board[nx][ny] === 0) {
        board[nx][ny] = virus;
        viruses.push([virus, time + 1, nx, ny]);
      }
    }
  }
  return board[tx - 1][ty - 1];
}
```

## Q18 괄호 변환

| 항목 | 값 |
|------|-----|
| 난이도 | ★★ 중하 |
| 기출 | 2020 카카오 신입공채 1차 |

### 문제 요약

"균형 잡힌 괄호 문자열"을 정해진 **재귀 규칙**으로 "올바른 괄호 문자열"로 변환.

예: `(()())()` → 그대로, `)(` → `()`, `()))((()` → `()(())()`

### 핵심 아이디어

문제의 재귀 절차를 그대로 옮긴다(DFS 사고). 균형점에서 u, v를 분리하고, u가 올바르면 `u + solve(v)`, 아니면 규칙대로 재조립한다.

```ts
function isCorrect(s: string): boolean {
  let count = 0;
  for (const ch of s) {
    if (ch === "(") {
      count++;
    } else {
      count--;
      if (count < 0) {
        return false;
      }
    }
  }
  return count === 0;
}

function transform(p: string): string {
  if (p === "") {
    return "";
  }
  // 균형점에서 u, v 분리
  let count = 0;
  let split = 0;
  for (let i = 0; i < p.length; i++) {
    count += p[i] === "(" ? 1 : -1;
    if (count === 0) {
      split = i + 1;
      break;
    }
  }
  const u = p.slice(0, split);
  const v = p.slice(split);

  if (isCorrect(u)) {
    return u + transform(v);
  }
  // u가 올바르지 않은 경우 규칙대로 재조립
  let result = "(" + transform(v) + ")";
  for (const ch of u.slice(1, -1)) {
    result += ch === "(" ? ")" : "(";
  }
  return result;
}
```

## Q19 연산자 끼워 넣기

| 항목 | 값 |
|------|-----|
| 난이도 | ★★ 중하 |
| 기출 | 백준 14888 |

### 문제 요약

N개의 수 사이에 +, −, ×, ÷를 끼워 넣어(순서 고정) 만들 수 있는 식의 **최댓값·최솟값**을 구하라. ÷는 정수 나눗셈(0 방향 절삭).

예: `[3,4,5]`, +1·×1 → `35, 17` / `[1,2,3,4,5,6]`, +2·−1·×1·÷1 → `54, -24`

### 핵심 아이디어

남은 연산자 개수를 들고 **DFS 완전 탐색**(N ≤ 11). 각 단계에서 가능한 연산자를 모두 시도한다.

```ts
function operators(nums: number[], ops: number[]): [number, number] {
  const n = nums.length;
  let maxVal = -Infinity;
  let minVal = Infinity;

  function dfs(i: number, current: number, add: number, sub: number, mul: number, div: number) {
    if (i === n) {
      maxVal = Math.max(maxVal, current);
      minVal = Math.min(minVal, current);
      return;
    }
    if (add > 0) {
      dfs(i + 1, current + nums[i], add - 1, sub, mul, div);
    }
    if (sub > 0) {
      dfs(i + 1, current - nums[i], add, sub - 1, mul, div);
    }
    if (mul > 0) {
      dfs(i + 1, current * nums[i], add, sub, mul - 1, div);
    }
    if (div > 0) {
      dfs(i + 1, Math.trunc(current / nums[i]), add, sub, mul, div - 1); // 0 방향 절삭
    }
  }
  dfs(1, nums[0], ops[0], ops[1], ops[2], ops[3]);
  return [maxVal, minVal];
}
```

> **함정**: 정수 나눗셈은 `Math.floor`가 아니라 **`Math.trunc`**(0 방향 절삭)다. 파이썬 `//`(음의 무한대 방향)와 다르며, 문제의 "C++14 기준(음수는 양수로 바꿔 몫 취하고 음수화)"과 일치한다.

## Q20 감시 피하기

| 항목 | 값 |
|------|-----|
| 난이도 | ★★★ 중 |
| 기출 | 백준 18428 |

### 문제 요약

빈 칸(X)에 **장애물 3개**를 설치해, 모든 학생(S)이 선생님(T)의 4방향 직선 시야에서 벗어날 수 있으면 `YES`.

### 핵심 아이디어

빈 칸 중 3개를 고르는 **조합 완전 탐색** + 각 선생님의 4방향 시야 검사(장애물에 막힐 때까지 직진).

```ts
function avoidWatch(n: number, board: string[][]): string {
  const empties: [number, number][] = [];
  const teachers: [number, number][] = [];
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      if (board[i][j] === "X") {
        empties.push([i, j]);
      } else if (board[i][j] === "T") {
        teachers.push([i, j]);
      }
    }
  }
  const dx = [-1, 1, 0, 0];
  const dy = [0, 0, -1, 1];

  const isWatched = (b: string[][]): boolean => {
    for (const [tx, ty] of teachers) {
      for (let d = 0; d < 4; d++) {
        let nx = tx;
        let ny = ty;
        while (true) {
          nx += dx[d];
          ny += dy[d];
          if (nx < 0 || nx >= n || ny < 0 || ny >= n) {
            break;
          }
          if (b[nx][ny] === "O") {
            break; // 장애물에 막힘
          }
          if (b[nx][ny] === "S") {
            return true; // 학생 발각
          }
        }
      }
    }
    return false;
  };

  for (const combo of combinations(empties, 3)) {
    const temp = board.map((row) => [...row]);
    for (const [x, y] of combo) {
      temp[x][y] = "O";
    }
    if (!isWatched(temp)) {
      return "YES";
    }
  }
  return "NO";
}
```

## Q21 인구 이동

| 항목 | 값 |
|------|-----|
| 난이도 | ★★★ 중 |
| 기출 | 백준 16234 |

### 문제 요약

인접 두 나라의 인구 차가 L 이상 R 이하면 국경을 열고, 연결된 **연합**의 인구를 평균(소수점 버림)으로 균등화한다. 인구 이동이 **몇 번** 일어나는지 구하라.

예: N=2, L=20, R=50, `[[50,30],[20,40]]` → `1`

### 핵심 아이디어

매 라운드 BFS로 **연합**을 찾아 평균을 적용한다. 이동이 한 번도 없으면 종료. 라운드 수가 답이다.

```ts
function populationMove(n: number, l: number, r: number, board: number[][]): number {
  const dx = [-1, 1, 0, 0];
  const dy = [0, 0, -1, 1];
  let count = 0;

  while (true) {
    const visited = Array.from({ length: n }, () => new Array(n).fill(false));
    let moved = false;
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        if (visited[i][j]) {
          continue;
        }
        // 연합 BFS
        const union: [number, number][] = [[i, j]];
        visited[i][j] = true;
        let head = 0;
        let sum = board[i][j];
        while (head < union.length) {
          const [x, y] = union[head++];
          for (let d = 0; d < 4; d++) {
            const nx = x + dx[d];
            const ny = y + dy[d];
            if (nx >= 0 && nx < n && ny >= 0 && ny < n && !visited[nx][ny]) {
              const diff = Math.abs(board[x][y] - board[nx][ny]);
              if (diff >= l && diff <= r) {
                visited[nx][ny] = true;
                union.push([nx, ny]);
                sum += board[nx][ny];
              }
            }
          }
        }
        if (union.length > 1) {
          const avg = Math.floor(sum / union.length);
          for (const [x, y] of union) {
            board[x][y] = avg;
          }
          moved = true;
        }
      }
    }
    if (!moved) {
      break;
    }
    count++;
  }
  return count;
}
```

## Q22 블록 이동하기

| 항목 | 값 |
|------|-----|
| 난이도 | ★★★ 상 |
| 기출 | 2020 카카오 신입공채 1차 |

### 문제 요약

2×1 로봇을 (1,1)에서 (N,N)까지 이동(평행 4방향 + 90도 회전)하는 **최소 시간**. 회전 시 대각선 칸에 벽이 없어야 한다.

### 핵심 아이디어

로봇이 차지하는 **두 칸을 하나의 상태**로 보고 BFS. 각 상태에서 평행 이동 4가지 + 회전(가로면 상/하, 세로면 좌/우) 후보를 만든다. 방문 체크는 두 칸을 정렬한 키로 한다.

```ts
function blockMove(board: number[][]): number {
  const n = board.length;
  const inRange = (r: number, c: number) => r >= 0 && r < n && c >= 0 && c < n;
  const key = (pos: number[][]) => {
    const sorted = [...pos].sort((a, b) => a[0] - b[0] || a[1] - b[1]);
    return JSON.stringify(sorted);
  };

  const getNext = (pos: number[][]): number[][][] => {
    const next: number[][][] = [];
    const [[r1, c1], [r2, c2]] = pos;
    const dx = [-1, 1, 0, 0];
    const dy = [0, 0, -1, 1];
    // 평행 이동
    for (let d = 0; d < 4; d++) {
      const nr1 = r1 + dx[d];
      const nc1 = c1 + dy[d];
      const nr2 = r2 + dx[d];
      const nc2 = c2 + dy[d];
      if (inRange(nr1, nc1) && inRange(nr2, nc2) && board[nr1][nc1] === 0 && board[nr2][nc2] === 0) {
        next.push([[nr1, nc1], [nr2, nc2]]);
      }
    }
    // 회전
    if (r1 === r2) {
      // 가로 → 상/하 회전
      for (const dir of [-1, 1]) {
        if (inRange(r1 + dir, c1) && inRange(r2 + dir, c2) && board[r1 + dir][c1] === 0 && board[r2 + dir][c2] === 0) {
          next.push([[r1, c1], [r1 + dir, c1]]);
          next.push([[r2, c2], [r2 + dir, c2]]);
        }
      }
    } else {
      // 세로 → 좌/우 회전
      for (const dir of [-1, 1]) {
        if (inRange(r1, c1 + dir) && inRange(r2, c2 + dir) && board[r1][c1 + dir] === 0 && board[r2][c2 + dir] === 0) {
          next.push([[r1, c1], [r1, c1 + dir]]);
          next.push([[r2, c2], [r2, c2 + dir]]);
        }
      }
    }
    return next;
  };

  const start = [[0, 0], [0, 1]];
  const queue: [number[][], number][] = [[start, 0]];
  let head = 0;
  const visited = new Set([key(start)]);
  while (head < queue.length) {
    const [pos, cost] = queue[head++];
    // 두 칸 중 하나라도 목적지면 도착
    if ((pos[0][0] === n - 1 && pos[0][1] === n - 1) || (pos[1][0] === n - 1 && pos[1][1] === n - 1)) {
      return cost;
    }
    for (const np of getNext(pos)) {
      const k = key(np);
      if (!visited.has(k)) {
        visited.add(k);
        queue.push([np, cost + 1]);
      }
    }
  }
  return -1;
}
```

> **핵심 통찰**: "로봇이 두 칸을 차지"처럼 **상태가 좌표 하나로 안 떨어지는** 문제는, **상태 전체를 노드로** 삼아 BFS한다. 방문 집합 키를 정규화(정렬)해야 같은 상태를 중복 방문하지 않는다.

---

## 요약

- **특정 거리·경쟁적 전염**: BFS로 거리/시간을 채운다(전염은 번호 우선 정렬 큐).
- **연구소·감시 피하기**: 빈 칸 중 **N개 조합 완전 탐색** + BFS/시야 검사 (격자 작음).
- **괄호 변환**: 문제의 **재귀 규칙**을 그대로 구현.
- **연산자 끼워 넣기**: 남은 연산자 들고 DFS 완전 탐색. ÷는 `Math.trunc`.
- **인구 이동**: 매 라운드 연합 BFS + 평균 균등화, 변화 없으면 종료.
- **블록 이동하기**: **두 칸 상태를 노드로** 한 BFS(이동 + 회전), 키 정규화 필수.
- 공통: 입력이 작으면 **완전 탐색 + 탐색**의 조합이 정답인 경우가 많다.
