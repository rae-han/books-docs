# Chapter 11: Graph (그래프)

## 핵심 질문

노드와 간선으로 표현되는 비선형 자료구조인 그래프는 어떻게 구현하고 탐색하는가? DFS, BFS, 다익스트라, 벨만-포드는 각각 어떤 문제에 적합한가?

## 1. 그래프의 개념

그래프는 **노드(vertex)** 와 **간선(edge)** 으로 데이터 간의 관계를 표현하는 비선형 자료구조다. 간선에는 **방향**과 **가중치**가 있을 수 있다.

### 그래프 용어

| 용어 | 의미 |
|------|------|
| **노드 (vertex)** | 데이터를 담는 점 |
| **간선 (edge)** | 노드를 연결하는 선 |
| **가중치 (weight)** | 간선의 비용·거리·정도 |
| **차수 (degree)** | 한 노드에 연결된 간선의 수 |
| **경로 (path)** | 시작 노드에서 끝 노드까지 거치는 노드들의 순서 |
| **사이클 (cycle)** | 시작과 끝이 같은 경로 |

### 그래프의 종류

| 분류 기준 | 종류 |
|----------|------|
| **방향성** | 방향 그래프(directed) / 무방향 그래프(undirected) |
| **가중치** | 가중치 그래프(weighted) / 비가중 그래프(unweighted) |
| **순환** | 순환 그래프(cyclic) / 비순환 그래프(acyclic) — DAG는 방향성 비순환 그래프 |

> **핵심 통찰**: 트리는 사이클이 없고 모든 노드가 연결된 특수한 그래프다. 그래프 알고리즘 대부분은 트리에도 적용된다.

## 2. 그래프 구현

### 인접 행렬 (Adjacency Matrix)

`matrix[i][j] = 가중치` (간선이 없으면 0 또는 Infinity).

```javascript
// N×N 배열로 초기화
const matrix = Array.from({ length: N }, () => new Array(N).fill(0));

// u → v로 가중치 w인 간선
matrix[u][v] = w;

// 무방향이면 양쪽 모두
matrix[v][u] = w;
```

| 항목 | 비용 |
|------|------|
| 메모리 | O(N²) |
| 간선 존재 확인 | O(1) |
| 인접 노드 순회 | O(N) |

**적합**: 노드 수가 적고(≤ 1,000) 간선이 많은 밀집 그래프, 빠른 간선 조회.

### 인접 리스트 (Adjacency List)

각 노드별로 인접 노드를 리스트로 저장.

```javascript
const adj = Array.from({ length: N }, () => []);

// u → v로 가중치 w
adj[u].push([v, w]);

// 무방향
adj[v].push([u, w]);
```

| 항목 | 비용 |
|------|------|
| 메모리 | O(N + E) |
| 간선 존재 확인 | O(deg(u)) |
| 인접 노드 순회 | O(deg(u)) |

**적합**: 희소 그래프(노드 많고 간선 적음), 노드 ≥ 10,000.

### 선택 기준

| 노드 수 | 추천 |
|--------|------|
| ~1,000 | 인접 행렬 (O(1) 조회의 이점) |
| > 1,000 | 인접 리스트 (메모리 절약) |

## 3. 그래프 탐색

### DFS (깊이 우선 탐색)

한쪽 방향으로 끝까지 가다가 막히면 백트래킹. **스택 또는 재귀**로 구현.

```javascript
function dfs(node, visited, adj, result) {
  visited.add(node);
  result.push(node);
  for (const next of adj[node] || []) {
    if (!visited.has(next)) {
      dfs(next, visited, adj, result);
    }
  }
}
```

**활용**: 모든 경로 탐색, 사이클 검출, 위상 정렬, 연결 요소 카운팅.

### BFS (너비 우선 탐색)

가까운 노드부터 차례로 방문. **큐**로 구현.

```javascript
function bfs(start, adj) {
  const queue = [start];
  const visited = new Set([start]);
  const result = [];

  while (queue.length > 0) {
    const node = queue.shift();
    result.push(node);
    for (const next of adj[node] || []) {
      if (!visited.has(next)) {
        visited.add(next);
        queue.push(next);
      }
    }
  }
  return result;
}
```

**활용**: **가중치 없는 그래프의 최단 거리**, 레벨별 탐색, 최소 단계.

> **핵심 통찰**: BFS는 **간선 1개를 거리 1로 보는 그래프의 최단 거리**를 보장한다. 가중치가 있으면 다익스트라 또는 벨만-포드를 써야 한다.

### DFS vs BFS 비교

| 항목 | DFS | BFS |
|------|-----|-----|
| 자료구조 | 스택/재귀 | 큐 |
| 최단 거리 보장 | ❌ | ✅ (가중치 없을 때) |
| 메모리 | 트리 깊이만큼 | 너비만큼 |
| 활용 | 백트래킹, 모든 경로 | 최단 거리, 레벨 탐색 |

## 4. 최단 경로 알고리즘

### 다익스트라 (Dijkstra) — 양의 가중치

**시작 노드부터 모든 노드까지의 최단 거리**를 구한다. 음의 가중치가 있으면 안 됨.

**알고리즘**:
1. `distances[]`를 무한대로 초기화, `distances[start] = 0`.
2. 우선순위 큐(MinHeap)에 `[0, start]` 푸시.
3. 큐에서 거리가 최소인 노드를 꺼내 인접 노드를 갱신:
   - `distances[u] + weight < distances[v]`이면 `distances[v]` 갱신, 큐에 푸시.
4. 큐가 빌 때까지 반복.

```javascript
class MinHeap {
  constructor() { this.items = []; }
  size() { return this.items.length; }
  push(item) {
    this.items.push(item);
    this.bubbleUp();
  }
  pop() {
    if (this.size() === 0) return null;
    const min = this.items[0];
    this.items[0] = this.items[this.size() - 1];
    this.items.pop();
    this.bubbleDown();
    return min;
  }
  swap(a, b) {
    [this.items[a], this.items[b]] = [this.items[b], this.items[a]];
  }
  bubbleUp() {
    let idx = this.size() - 1;
    while (idx > 0) {
      const parent = Math.floor((idx - 1) / 2);
      if (this.items[parent][0] <= this.items[idx][0]) break;
      this.swap(idx, parent);
      idx = parent;
    }
  }
  bubbleDown() {
    let idx = 0;
    while (idx * 2 + 1 < this.size()) {
      const left = idx * 2 + 1;
      const right = idx * 2 + 2;
      const smaller =
        right < this.size() && this.items[right][0] < this.items[left][0]
          ? right
          : left;
      if (this.items[idx][0] <= this.items[smaller][0]) break;
      this.swap(idx, smaller);
      idx = smaller;
    }
  }
}

function dijkstra(graph, start) {
  const distances = {};
  for (const node in graph) distances[node] = Infinity;
  distances[start] = 0;

  const queue = new MinHeap();
  queue.push([0, start]);

  while (queue.size() > 0) {
    const [curDist, u] = queue.pop();
    if (distances[u] < curDist) continue; // 이미 처리한 노드 스킵

    for (const v in graph[u]) {
      const weight = graph[u][v];
      const newDist = curDist + weight;
      if (newDist < distances[v]) {
        distances[v] = newDist;
        queue.push([newDist, v]);
      }
    }
  }
  return distances;
}
```

**시간 복잡도**: O((N + E) log N).

> **함정**: 음의 가중치에서 다익스트라는 정답을 보장하지 않는다. **그리디**로 동작해 한 번 확정한 노드를 다시 갱신하지 않기 때문.

### 벨만-포드 (Bellman-Ford) — 음의 가중치 가능

**모든 간선을 N-1번 반복**하며 거리 갱신. 음의 사이클(순회할수록 비용 감소)도 검출 가능.

**알고리즘**:
1. `distances[]`를 무한대로, `distances[start] = 0`.
2. **N-1번 반복** — 매번 모든 간선을 보고 `distances[u] + weight < distances[v]`이면 갱신.
3. **N번째 반복**에도 갱신이 일어나면 → 음의 사이클 존재.

```javascript
function bellmanFord(graph, source) {
  const n = graph.length;
  const distance = new Array(n).fill(Infinity);
  distance[source] = 0;
  const predecessor = new Array(n).fill(null);

  // N-1번 반복
  for (let i = 0; i < n - 1; i++) {
    for (let u = 0; u < n; u++) {
      for (const [v, weight] of graph[u]) {
        if (distance[u] + weight < distance[v]) {
          distance[v] = distance[u] + weight;
          predecessor[v] = u;
        }
      }
    }
  }

  // 음의 사이클 검출
  for (let u = 0; u < n; u++) {
    for (const [v, weight] of graph[u]) {
      if (distance[u] + weight < distance[v]) {
        return [-1]; // 음의 사이클
      }
    }
  }

  return [distance, predecessor];
}
```

**시간 복잡도**: O(N × E).

### 다익스트라 vs 벨만-포드

| 항목 | 다익스트라 | 벨만-포드 |
|------|-----------|----------|
| 음의 가중치 | ❌ | ✅ |
| 음의 사이클 검출 | ❌ | ✅ |
| 시간 복잡도 | O((N+E) log N) | O(N × E) |
| 적합 | 빠른 최단 거리 (양의 가중치) | 음의 가중치 처리 |

## 5. 핵심 코드 패턴

### 그래프 입력 → 인접 리스트

```javascript
const adj = Array.from({ length: N + 1 }, () => []);
for (const [u, v, w] of edges) {
  adj[u].push([v, w]);
  adj[v].push([u, w]); // 무방향이면
}
```

### 격자 BFS (4방향)

```javascript
const dy = [-1, 1, 0, 0];
const dx = [0, 0, -1, 1];

function bfs(grid, sy, sx) {
  const n = grid.length;
  const m = grid[0].length;
  const dist = Array.from({ length: n }, () => new Array(m).fill(-1));
  dist[sy][sx] = 0;
  const queue = [[sy, sx]];

  while (queue.length > 0) {
    const [y, x] = queue.shift();
    for (let i = 0; i < 4; i++) {
      const ny = y + dy[i];
      const nx = x + dx[i];
      if (ny < 0 || ny >= n || nx < 0 || nx >= m) continue;
      if (dist[ny][nx] !== -1 || grid[ny][nx] === 0) continue;
      dist[ny][nx] = dist[y][x] + 1;
      queue.push([ny, nx]);
    }
  }
  return dist;
}
```

### 연결 요소 카운팅 (DFS)

```javascript
function countComponents(n, adj) {
  const visited = new Array(n).fill(false);
  let count = 0;
  for (let i = 0; i < n; i++) {
    if (!visited[i]) {
      count++;
      dfs(i, visited, adj);
    }
  }
  return count;
}
```

## 6. JavaScript 빌트인 메서드 레퍼런스

| 도구 | 활용 |
|------|------|
| `Array.from({length: N}, () => [])` | 인접 리스트 초기화 |
| `Set` | 방문 노드 추적 |
| `MinHeap` (직접 구현) | 다익스트라의 우선순위 큐 |
| `queue.shift()` | BFS의 dequeue (작은 큐에서만) |
| 클래스 `Queue` | BFS의 효율적 큐 |

## 7. 몸풀기 문제

### 문제 38: 깊이 우선 탐색 순회

> 그래프와 시작 노드가 주어질 때 DFS 결과를 배열로 반환.

```javascript
function solution(graph, start) {
  const adjList = {};
  for (const [u, v] of graph) {
    if (!adjList[u]) adjList[u] = [];
    adjList[u].push(v);
  }

  const visited = new Set();
  const result = [];

  function dfs(node) {
    visited.add(node);
    result.push(node);
    for (const next of adjList[node] || []) {
      if (!visited.has(next)) dfs(next);
    }
  }

  dfs(start);
  return result;
}
```

### 문제 39: 너비 우선 탐색 순회

> BFS 결과를 배열로 반환. 큐는 표준 패턴.

```javascript
function solution(graph, start) {
  const adjList = {};
  for (const [u, v] of graph) {
    if (!adjList[u]) adjList[u] = [];
    adjList[u].push(v);
  }

  const visited = new Set([start]);
  const queue = [start];
  const result = [start];

  while (queue.length > 0) {
    const node = queue.shift();
    for (const next of adjList[node] || []) {
      if (!visited.has(next)) {
        visited.add(next);
        queue.push(next);
        result.push(next);
      }
    }
  }
  return result;
}
```

### 문제 40: 다익스트라 알고리즘

> 위 [4. 최단 경로 알고리즘](#4-최단-경로-알고리즘)의 다익스트라 구현 참고.

### 문제 41: 벨만-포드 알고리즘

> 위 [4. 최단 경로 알고리즘](#4-최단-경로-알고리즘)의 벨만-포드 구현 참고.

## 8. 합격자가 되는 모의테스트

### 문제 42: 게임 맵 최단 거리 — 프로그래머스

> N×M 격자에서 (0,0)에서 (N-1, M-1)까지의 최단 경로 길이. 0은 벽, 1은 통로.
> [프로그래머스 #1844](https://school.programmers.co.kr/learn/courses/30/lessons/1844)

**접근 아이디어**: 가중치 없는 격자 → BFS.

```javascript
function solution(maps) {
  const n = maps.length;
  const m = maps[0].length;
  const dy = [-1, 1, 0, 0];
  const dx = [0, 0, -1, 1];

  const dist = Array.from({ length: n }, () => new Array(m).fill(-1));
  dist[0][0] = 1;
  const queue = [[0, 0]];

  while (queue.length > 0) {
    const [y, x] = queue.shift();
    if (y === n - 1 && x === m - 1) return dist[y][x];

    for (let i = 0; i < 4; i++) {
      const ny = y + dy[i];
      const nx = x + dx[i];
      if (ny < 0 || ny >= n || nx < 0 || nx >= m) continue;
      if (dist[ny][nx] !== -1 || maps[ny][nx] === 0) continue;
      dist[ny][nx] = dist[y][x] + 1;
      queue.push([ny, nx]);
    }
  }

  return -1;
}
```

> **핵심 통찰**: "최단 거리" + "가중치 없음(또는 모두 동일)" = BFS. 격자 문제의 표준 해법.

**시간 복잡도**: O(N × M)

### 문제 43: 네트워크 — 프로그래머스

> N개의 컴퓨터와 연결 정보 `computers[i][j]`. 네트워크 개수(연결 요소 개수) 반환.
> [프로그래머스 #43162](https://programmers.co.kr/learn/courses/30/lessons/43162)

**접근 아이디어**: 연결 요소 카운팅 — 방문 안 한 노드에서 DFS/BFS 시작할 때마다 +1.

```javascript
function solution(n, computers) {
  const visited = new Array(n).fill(false);
  let count = 0;

  function dfs(node) {
    visited[node] = true;
    for (let i = 0; i < n; i++) {
      if (computers[node][i] === 1 && !visited[i]) {
        dfs(i);
      }
    }
  }

  for (let i = 0; i < n; i++) {
    if (!visited[i]) {
      count++;
      dfs(i);
    }
  }
  return count;
}
```

**시간 복잡도**: O(N²)

### 문제 44: 배달 — 프로그래머스

> N개의 마을과 가중치 그래프. 1번 마을에서 K 시간 이내로 갈 수 있는 마을 수 반환.
> [프로그래머스 #12978](https://programmers.co.kr/learn/courses/30/lessons/12978)

**접근 아이디어**: 1번 노드에서 모든 노드까지 다익스트라. K 이하인 노드 카운트.

```javascript
function solution(N, road, K) {
  const adj = Array.from({ length: N + 1 }, () => []);
  for (const [a, b, c] of road) {
    adj[a].push([b, c]);
    adj[b].push([a, c]); // 무방향
  }

  const distances = new Array(N + 1).fill(Infinity);
  distances[1] = 0;

  const queue = new MinHeap();
  queue.push([0, 1]);

  while (queue.size() > 0) {
    const [d, u] = queue.pop();
    if (distances[u] < d) continue;

    for (const [v, w] of adj[u]) {
      const nd = d + w;
      if (nd < distances[v]) {
        distances[v] = nd;
        queue.push([nd, v]);
      }
    }
  }

  return distances.filter((d) => d <= K).length;
}
```

> **함정**: 같은 두 마을 사이에 여러 개의 도로가 있을 수 있다. `adj[a].push([b, c])`로 모두 추가하고 다익스트라가 알아서 최소를 찾게 둔다.

**시간 복잡도**: O((N + E) log N)

### 문제 45: 경주로 건설 — 2020 KAKAO BLIND

> N×N 격자에서 (0,0)에서 (N-1,N-1)까지 도로 건설. 직선은 100원, 코너는 600원. 최소 비용.
> [프로그래머스 #67259](https://school.programmers.co.kr/learn/courses/30/lessons/67259)

**접근 아이디어**: 코너 비용이 다르므로 단순 BFS로는 부족. **방향까지 상태에 포함한 다익스트라/BFS**. `dist[y][x][direction]`.

```javascript
function solution(board) {
  const n = board.length;
  const dy = [-1, 1, 0, 0]; // 상, 하, 좌, 우
  const dx = [0, 0, -1, 1];

  // dist[y][x][direction] (0~3, 4는 시작)
  const INF = Infinity;
  const dist = Array.from({ length: n }, () =>
    Array.from({ length: n }, () => new Array(4).fill(INF))
  );

  const queue = new MinHeap();
  queue.push([0, 0, 0, 4]); // [비용, y, x, 방향]

  let answer = INF;

  while (queue.size() > 0) {
    const [cost, y, x, dir] = queue.pop();

    if (y === n - 1 && x === n - 1) {
      answer = Math.min(answer, cost);
      continue;
    }

    for (let i = 0; i < 4; i++) {
      const ny = y + dy[i];
      const nx = x + dx[i];
      if (ny < 0 || ny >= n || nx < 0 || nx >= n) continue;
      if (board[ny][nx] === 1) continue;

      const newCost = dir === 4 || dir === i
        ? cost + 100
        : cost + 600; // 방향이 바뀌면 코너

      if (newCost < dist[ny][nx][i]) {
        dist[ny][nx][i] = newCost;
        queue.push([newCost, ny, nx, i]);
      }
    }
  }

  return answer;
}
```

> **핵심 통찰**: 가중치가 다른 격자 문제는 BFS 대신 **다익스트라**. 그리고 "방향에 따라 비용이 다르다"면 **방향을 상태**로 추가한다 (`dist[y][x][dir]`).

**시간 복잡도**: O(N² log N)

### 문제 46: 전력망을 둘로 나누기 — 프로그래머스

> N개 송전탑 트리에서 간선 하나를 끊어 두 개의 서브트리로 만든다. 두 서브트리 노드 수의 차이가 최소가 되는 값을 반환.
> [프로그래머스 #86971](https://programmers.co.kr/learn/courses/30/lessons/86971)

**접근 아이디어**:
1. 각 간선을 하나씩 끊어보며 두 서브트리의 크기 차이 계산.
2. 끊은 후 BFS/DFS로 한쪽 서브트리의 크기 측정.

```javascript
function solution(n, wires) {
  let minDiff = Infinity;

  for (let i = 0; i < wires.length; i++) {
    const adj = Array.from({ length: n + 1 }, () => []);
    for (let j = 0; j < wires.length; j++) {
      if (i === j) continue; // 이 간선은 끊었음
      const [a, b] = wires[j];
      adj[a].push(b);
      adj[b].push(a);
    }

    // BFS로 1번 노드와 연결된 노드 수 세기
    const visited = new Array(n + 1).fill(false);
    visited[1] = true;
    const queue = [1];
    let count = 0;
    while (queue.length > 0) {
      const node = queue.shift();
      count++;
      for (const next of adj[node]) {
        if (!visited[next]) {
          visited[next] = true;
          queue.push(next);
        }
      }
    }

    const diff = Math.abs(count - (n - count));
    minDiff = Math.min(minDiff, diff);
  }

  return minDiff;
}
```

> **합격 조언**: 간선이 적으니(N-1) 모든 간선을 시도해도 O(N²)로 충분하다. 더 빠른 풀이는 트리 DP로 가능하지만 이 문제 규모에선 단순 풀이로 충분.

**시간 복잡도**: O(N²)

## 9. 함정/실수 노트

| 함정 | 설명 |
|------|------|
| `queue.shift()`의 O(N) | 큰 BFS는 클래스 `Queue` 또는 인덱스 패턴 |
| 무방향 그래프의 양방향 추가 | `adj[u].push(v)`만 하면 한 방향만 |
| 다익스트라에서 음의 가중치 | 정답 보장 안 됨 — 벨만-포드로 |
| BFS vs 다익스트라 혼동 | 가중치가 다르면 BFS 안 됨 |
| 격자 4방향 vs 8방향 | 문제마다 다름 — `dy`/`dx` 배열 정확히 |
| `MinHeap` 직접 구현 | 자바스크립트는 표준 라이브러리에 없음 |
| 우선순위 큐의 중복 푸시 | `if (distances[u] < curDist) continue;`로 스킵 |
| 방문 체크 시점 | BFS는 푸시할 때, DFS는 진입할 때 — 일관성 유지 |
| 상태 차원 누락 | 방향, 키 보유 등 상태가 있으면 visited에 차원 추가 |

## 10. 요약

- **그래프는 노드와 간선으로 데이터 관계를 표현**한다. 방향성, 가중치, 순환 여부에 따라 종류가 나뉜다.
- **인접 행렬과 인접 리스트**가 두 가지 표현 방법. 노드 수와 밀집도에 따라 선택.
- **DFS는 깊이 우선** — 백트래킹, 모든 경로 탐색에 적합.
- **BFS는 너비 우선** — **가중치 없는 그래프의 최단 거리**를 보장.
- **다익스트라는 양의 가중치 그래프의 최단 거리** — 우선순위 큐 + 그리디.
- **벨만-포드는 음의 가중치를 처리**하고 음의 사이클을 검출. O(N × E).
- **격자 문제**는 그래프의 변형 — `dy`/`dx` 배열로 4방향 이동을 깔끔하게 처리.
- **상태 공간 다익스트라**: 좌표 + 방향/키 등 상태를 visited 차원에 추가.
- **연결 요소 카운팅**: 방문 안 한 노드에서 DFS/BFS 시작할 때마다 카운트 +1.

## 리마인드 (저자)

1. 그래프는 노드와 간선의 집합이며, 방향성과 가중치에 따라 다양하게 분류된다.
2. 그래프 표현은 인접 행렬과 인접 리스트가 있다.
3. 그래프 탐색은 DFS와 BFS로 한다. BFS는 가중치 없는 그래프의 최단 거리를 보장한다.
4. 가중치가 있는 최단 경로는 다익스트라(양의 가중치) 또는 벨만-포드(음의 가중치 가능)로 구한다.
