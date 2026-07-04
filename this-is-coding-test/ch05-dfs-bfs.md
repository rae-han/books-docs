# Chapter 05: DFS/BFS (탐색 알고리즘)

> 그래프를 탐색하는 두 기둥. 깊이 우선 탐색(DFS)은 스택·재귀로, 너비 우선 탐색(BFS)은 큐로 동작한다. 격자·그래프 문제의 절반은 이 둘로 풀린다.

## 핵심 질문

- DFS와 BFS는 각각 어떤 자료구조에 기반하며, 언제 무엇을 선택하는가?
- 2차원 격자(맵)를 어떻게 **그래프로 모델링**하는가?
- TypeScript에서 큐를 효율적으로 구현하려면? (배열 `shift()`의 함정)

## 1. 사전 지식 — 스택, 큐, 재귀

DFS/BFS를 이해하려면 **스택·큐·재귀**가 전제된다.

### 스택과 큐

| 자료구조 | 구조 | 삽입/삭제 |
|------|------|-----------|
| 스택(*Stack*) | 선입후출(LIFO) | 한쪽 끝에서만 넣고 뺀다 |
| 큐(*Queue*) | 선입선출(FIFO) | 한쪽에서 넣고 반대쪽에서 뺀다 |

```ts
// 스택: 배열의 push / pop으로 그대로 구현
const stack: number[] = [];
stack.push(5);
stack.push(2);
stack.push(3);
stack.pop(); // 3 제거
console.log(stack); // [5, 2]  (최하단부터)
console.log([...stack].reverse()); // [2, 5]  (최상단부터)
```

> **함정**: 파이썬은 큐를 `collections.deque`로 만들어 `popleft()`가 **O(1)** 이다. TypeScript에서 배열 `shift()`로 흉내 내면 **O(n)** 이라(앞을 빼면 전체가 한 칸씩 당겨짐) BFS에서 입력이 크면 시간 초과가 난다. **머리 포인터(head index)** 방식을 쓰자.

```ts
// 큐: push로 넣고, shift() 대신 head 포인터로 꺼낸다 (O(1))
const queue: number[] = [];
let head = 0;
queue.push(5);
queue.push(2);
const first = queue[head++]; // 5를 꺼냄 (실제 배열은 그대로 둠)
```

### 재귀 함수

재귀 함수(*Recursive Function - 자기 자신을 다시 호출하는 함수*)는 **종료 조건**이 반드시 있어야 한다. 없으면 무한 호출로 스택이 넘친다. 대표 예제가 팩토리얼이다.

```ts
// 반복적 구현
function factorialIterative(n: number): number {
  let result = 1;
  for (let i = 1; i <= n; i++) {
    result *= i;
  }
  return result;
}

// 재귀적 구현 — 점화식 factorial(n) = n × factorial(n-1)을 그대로 옮김
function factorialRecursive(n: number): number {
  if (n <= 1) {
    // 종료 조건: n이 1 이하면 1 반환
    return 1;
  }
  return n * factorialRecursive(n - 1);
}

console.log(factorialIterative(5)); // 120
console.log(factorialRecursive(5)); // 120
```

> **핵심 통찰**: 재귀는 수학의 **점화식**을 그대로 코드로 옮긴 것이다. 이 사고방식은 Ch 08 다이나믹 프로그래밍으로 직접 이어진다. 컴퓨터 내부에서 재귀 호출은 **스택**으로 처리되므로, DFS를 재귀로 간결히 구현할 수 있다.

## 2. 그래프 표현 — 인접 행렬 vs 인접 리스트

그래프는 노드(*Node, 정점*)와 간선(*Edge*)으로 표현한다. 코드로는 두 방식이 있다.

| 방식 | 표현 | 메모리 | "두 노드가 연결됐나?" 조회 |
|------|------|--------|---------------------------|
| 인접 행렬(*Adjacency Matrix*) | 2차원 배열 | 노드 수의 제곱 (낭비 가능) | O(1) — `graph[a][b]` |
| 인접 리스트(*Adjacency List*) | 노드별 연결 목록 | 연결된 것만 저장 (효율적) | O(연결 수) — 순회 필요 |

```ts
// 인접 행렬: 연결 안 된 곳은 무한(INF)
const INF = 999999999;
const matrix = [
  [0, 7, 5],
  [7, 0, INF],
  [5, INF, 0],
];

// 인접 리스트: [연결노드, 거리] 쌍을 노드별로 저장
const adjList: [number, number][][] = Array.from({ length: 3 }, () => []);
adjList[0].push([1, 7], [2, 5]);
adjList[1].push([0, 7]);
adjList[2].push([0, 5]);
```

## 3. DFS — 깊이 우선 탐색

DFS(*Depth-First Search*)는 한 경로로 **최대한 깊이** 들어갔다가 막히면 되돌아와 다른 경로를 탐색한다. **스택**(주로 재귀)으로 구현한다.

동작: ① 시작 노드를 방문 처리 → ② 인접 노드 중 방문 안 한 곳으로 깊이 들어감 → ③ 막히면 직전으로 되돌아감.

```python
# Python (책 원본)
def dfs(graph, v, visited):
    visited[v] = True
    print(v, end=' ')
    for i in graph[v]:
        if not visited[i]:
            dfs(graph, i, visited)
```

```ts
// TypeScript
function dfs(graph: number[][], v: number, visited: boolean[], order: number[]) {
  visited[v] = true;
  order.push(v); // 방문 순서 기록 (책의 print 대응)
  for (const next of graph[v]) {
    if (!visited[next]) {
      dfs(graph, next, visited, order);
    }
  }
}

// 0번은 비우고 1~8번 노드 사용 (인접 리스트)
const graph = [
  [],
  [2, 3, 8], // 1
  [1, 7], // 2
  [1, 4, 5], // 3
  [3, 5], // 4
  [3, 4], // 5
  [7], // 6
  [2, 6, 8], // 7
  [1, 7], // 8
];
const visited = new Array(9).fill(false);
const order: number[] = [];
dfs(graph, 1, visited, order);
console.log(order.join(" ")); // 1 2 7 6 8 3 4 5
```

**시간복잡도**: O(N) — 노드 수에 비례.

> **함정**: 재귀 DFS는 노드가 매우 많으면 **호출 스택 한도**를 넘길 수 있다(파이썬도 기본 1,000, Node.js도 한계가 있다). 깊이가 깊은 그래프는 명시적 스택 배열로 바꾸거나, 큐 기반 BFS를 고려한다.

## 4. BFS — 너비 우선 탐색

BFS(*Breadth-First Search*)는 시작점에서 **가까운 노드부터** 차례로 탐색한다. **큐**로 구현하며, 간선 가중치가 모두 1이면 **최단 거리**를 그대로 구할 수 있다.

```python
# Python (책 원본) — deque의 popleft()는 O(1)
from collections import deque

def bfs(graph, start, visited):
    queue = deque([start])
    visited[start] = True
    while queue:
        v = queue.popleft()
        print(v, end=' ')
        for i in graph[v]:
            if not visited[i]:
                queue.append(i)
                visited[i] = True
```

```ts
// TypeScript — shift() 대신 head 포인터로 O(1) 큐
function bfs(graph: number[][], start: number, visited: boolean[]): number[] {
  const queue: number[] = [start];
  let head = 0;
  visited[start] = true;
  const order: number[] = [];
  while (head < queue.length) {
    const v = queue[head++];
    order.push(v);
    for (const next of graph[v]) {
      if (!visited[next]) {
        queue.push(next);
        visited[next] = true;
      }
    }
  }
  return order;
}

const visited2 = new Array(9).fill(false);
console.log(bfs(graph, 1, visited2).join(" ")); // 1 2 3 8 7 4 5 6
```

**시간복잡도**: O(N). 일반적으로 실제 수행 속도는 DFS보다 빠른 편이다.

| | DFS | BFS |
|------|------|------|
| 동작 원리 | 스택 (재귀) | 큐 |
| 탐색 방향 | 깊이 우선 | 너비 우선 |
| 대표 용도 | 연결 요소·경로 존재 | **최단 거리**(가중치 1) |

## 5. 2차원 격자를 그래프로 보기

게임 맵 같은 2차원 배열은 **각 칸을 노드, 상하좌우 인접 칸을 간선**으로 보면 그래프 탐색 문제가 된다. Ch 04의 `dx`/`dy` 방향 배열이 그대로 쓰인다.

```ts
const dx = [-1, 1, 0, 0]; // 상, 하
const dy = [0, 0, -1, 1]; // 좌, 우
```

> **핵심 통찰**: "맵에서 영역 개수 세기", "최소 이동 횟수" 같은 문제를 만나면 **격자를 그래프로 치환**하라. 영역·연결은 DFS, 최단 거리는 BFS가 정석이다.

---

## 6. 실전 문제 1 — 음료수 얼려 먹기 (DFS)

| 항목 | 값 |
|------|-----|
| 난이도 | ★★ 중하 |
| 풀이 시간 | 30분 |
| 시간 제한 | 1초 |
| 메모리 | 128MB |

### 문제 요약

N×M 얼음틀에서 `0`(구멍)이 상하좌우로 붙어 있으면 하나의 아이스크림이다. 만들어지는 **아이스크림 개수**를 구하라.

예: 아래 4×5 틀 → `3`

```
00110
00011
11111
00000
```

### 핵심 아이디어

모든 칸을 순회하며, **아직 안 녹인 `0`을 만나면 DFS로 연결된 `0`을 전부 `1`로 칠한다**. DFS 한 번이 곧 아이스크림 한 덩이다.

### 코드

```ts
const input = `4 5
00110
00011
11111
00000`;

const lines = input.split("\n");
const [n, m] = lines[0].split(" ").map(Number);
// 공백 없는 문자열 → 숫자 배열: split("")
const graph = lines.slice(1, 1 + n).map((line) => line.split("").map(Number));

function dfs(x: number, y: number): boolean {
  // 범위를 벗어나면 종료
  if (x < 0 || x >= n || y < 0 || y >= m) {
    return false;
  }
  // 아직 방문 안 한 구멍(0)이면
  if (graph[x][y] === 0) {
    graph[x][y] = 1; // 방문 처리
    // 상하좌우 재귀 호출
    dfs(x - 1, y);
    dfs(x + 1, y);
    dfs(x, y - 1);
    dfs(x, y + 1);
    return true;
  }
  return false;
}

let result = 0;
for (let i = 0; i < n; i++) {
  for (let j = 0; j < m; j++) {
    if (dfs(i, j)) {
      result++;
    }
  }
}
console.log(result); // 3
```

**시간복잡도**: O(N × M) — 각 칸을 한 번씩 방문.

> **핵심 통찰**: 파이썬의 `list(map(int, input()))` 는 `"00110"` 같은 **붙은 문자열을 한 자리씩** 숫자 배열로 만든다. TS에서는 **`line.split("").map(Number)`** 가 정확한 대응이다(`split(" ")`가 아님에 주의).

## 7. 실전 문제 2 — 미로 탈출 (BFS)

| 항목 | 값 |
|------|-----|
| 난이도 | ★★ 중하 |
| 풀이 시간 | 30분 |
| 시간 제한 | 1초 |
| 메모리 | 128MB |

### 문제 요약

N×M 미로에서 `(0,0)`→`(N-1,M-1)`까지 최소 이동 칸 수를 구하라. `0`은 괴물(벽), `1`은 길. 시작·끝 칸을 모두 포함해 센다.

예: 아래 5×6 미로 → `10`

```
101010
111111
000001
111111
111111
```

### 핵심 아이디어

가중치가 모두 1인 최단 거리이므로 **BFS가 정석**이다. 큐로 가까운 칸부터 퍼져 나가며, **방문하는 칸에 "직전 칸 거리 + 1"을 기록**한다. 도착 칸의 값이 곧 최단 거리다.

### 코드

```ts
const input = `5 6
101010
111111
000001
111111
111111`;

const lines = input.split("\n");
const [n, m] = lines[0].split(" ").map(Number);
const graph = lines.slice(1, 1 + n).map((line) => line.split("").map(Number));

const dx = [-1, 1, 0, 0];
const dy = [0, 0, -1, 1];

function bfs(startX: number, startY: number): number {
  const queue: [number, number][] = [[startX, startY]];
  let head = 0; // shift() 대신 head 포인터 (O(1) 큐)

  while (head < queue.length) {
    const [x, y] = queue[head++];
    for (let i = 0; i < 4; i++) {
      const nx = x + dx[i];
      const ny = y + dy[i];
      // 미로 공간을 벗어나면 무시
      if (nx < 0 || ny < 0 || nx >= n || ny >= m) {
        continue;
      }
      // 벽이면 무시
      if (graph[nx][ny] === 0) {
        continue;
      }
      // 처음 방문하는 길(1)이면 거리 기록 후 큐에 추가
      if (graph[nx][ny] === 1) {
        graph[nx][ny] = graph[x][y] + 1;
        queue.push([nx, ny]);
      }
    }
  }
  return graph[n - 1][m - 1];
}

console.log(bfs(0, 0)); // 10
```

**시간복잡도**: O(N × M).

> **함정**: 이 풀이는 길 칸의 값 `1`을 "미방문"의 의미로도 쓴다. 그래서 `graph[nx][ny] === 1` 검사가 **곧 방문 여부 확인**이 된다. 거리 누적값(2 이상)은 자동으로 재방문에서 걸러진다.

---

## 자주 하는 실수

| 실수 | 원인 | 해결 |
|------|------|------|
| BFS 큐를 `arr.shift()`로 구현 | `shift()`는 O(n) | `head` 포인터 또는 환형 큐 사용 |
| 붙은 문자열을 `split(" ")` 로 파싱 | 공백이 없음 | `split("").map(Number)` |
| 방문 처리를 큐에서 **꺼낼 때** 함 | 같은 노드가 큐에 중복 삽입 | **큐에 넣는 순간** `visited` 표시 |
| 재귀 DFS로 거대한 격자 처리 | 호출 스택 초과 | 명시적 스택 또는 BFS로 전환 |
| 최단 거리 문제에 DFS 사용 | DFS는 최단 보장 안 됨 | 가중치 1 최단 거리는 **BFS** |

## 패턴 체크리스트

- [ ] 격자/맵 문제인가? → 칸=노드, 상하좌우=간선으로 **그래프 모델링**했는가?
- [ ] **연결 요소·영역 개수**인가? → DFS (방문 칠하기)
- [ ] **최단 거리·최소 이동**인가? → BFS (거리 누적)
- [ ] 큐를 `head` 포인터로 O(1)로 구현했는가?
- [ ] 방문 처리를 **큐 삽입 시점**에 했는가?

## 요약

- DFS = 스택(재귀), **깊이 우선**. 연결 요소·경로 탐색에 강하다 (음료수 얼려 먹기).
- BFS = 큐, **너비 우선**. 가중치 1 그래프의 **최단 거리**를 구한다 (미로 탈출).
- 2차원 격자는 **그래프로 치환**해 `dx`/`dy`로 탐색 — Ch 04의 방향 배열이 그대로 재사용된다.
- TS 큐는 **`shift()`(O(n)) 대신 `head` 포인터(O(1))** 로 구현해야 시간 초과를 피한다.
- 그래프 표현은 조회 빠른 **인접 행렬**, 메모리 효율 좋은 **인접 리스트** 중 상황에 맞게 선택.
- 재귀-점화식 사고는 Ch 08 DP로, 가중치 있는 최단 경로는 Ch 09(다익스트라)로 확장된다.
