# Chapter 17: 최단 경로 기출문제

> Ch 09에서 배운 최단 경로 유형의 기출문제 모음(Q37~Q40). **플로이드 워셜**, **도달 가능성 판정**, **격자 다익스트라**, **BFS 최단 거리**가 핵심이다.

## 핵심 질문

- 모든 쌍 최단 거리는 플로이드 워셜, 한 점 출발은 다익스트라/BFS인가?
- "순위를 정확히 알 수 있다" 같은 문제를 어떻게 도달 가능성으로 환원하는가?
- 비용이 간선이 아니라 **칸(노드)에** 있을 때 다익스트라를 어떻게 적용하는가?

> 격자 다익스트라에는 Ch 09의 `MinHeap`을 재사용한다.

---

## Q37 플로이드

| 항목 | 값 |
|------|-----|
| 난이도 | ★★★ 중 |
| 기출 | 백준 11404 |

### 문제 요약

n개 도시의 모든 쌍 (A,B) 최소 비용을 구하라. 같은 노선이 여러 개일 수 있고, 도달 불가는 0.

### 핵심 아이디어

전형적인 **플로이드 워셜**(n ≤ 100). 같은 노선은 **최솟값**으로 초기화하고, 도달 불가(INF)는 0으로 출력한다.

```ts
function floyd(n: number, edges: [number, number, number][]): number[][] {
  const INF = 1e9;
  const adj = Array.from({ length: n + 1 }, () => new Array(n + 1).fill(INF));
  for (let i = 1; i <= n; i++) {
    adj[i][i] = 0;
  }
  for (const [a, b, c] of edges) {
    adj[a][b] = Math.min(adj[a][b], c); // 중복 노선은 최솟값
  }
  for (let k = 1; k <= n; k++) {
    for (let a = 1; a <= n; a++) {
      for (let b = 1; b <= n; b++) {
        adj[a][b] = Math.min(adj[a][b], adj[a][k] + adj[k][b]);
      }
    }
  }
  const result: number[][] = [];
  for (let a = 1; a <= n; a++) {
    const row: number[] = [];
    for (let b = 1; b <= n; b++) {
      row.push(adj[a][b] >= INF ? 0 : adj[a][b]); // 도달 불가 → 0
    }
    result.push(row);
  }
  return result;
}
```

## Q38 정확한 순위

| 항목 | 값 |
|------|-----|
| 난이도 | ★★★ 중 |
| 기출 | K 대회 |

### 문제 요약

학생 성적 비교 결과(`A < B`)가 주어질 때, **순위를 정확히 알 수 있는 학생 수**를 구하라. (N ≤ 500)

예: N=6, 비교 `(1,5)(3,4)(4,2)(4,6)(5,2)(5,4)` → `1`

### 핵심 아이디어

플로이드 워셜로 **도달 가능성**을 구한다. 학생 i가 다른 모든 학생과 "i→j 또는 j→i 관계"가 있으면(자신 포함 N개와 비교 가능) i의 순위는 확정이다.

```ts
function exactRank(n: number, comparisons: [number, number][]): number {
  const INF = 1e9;
  const adj = Array.from({ length: n + 1 }, () => new Array(n + 1).fill(INF));
  for (let i = 1; i <= n; i++) {
    adj[i][i] = 0;
  }
  for (const [a, b] of comparisons) {
    adj[a][b] = 1; // a가 b보다 낮음
  }
  for (let k = 1; k <= n; k++) {
    for (let a = 1; a <= n; a++) {
      for (let b = 1; b <= n; b++) {
        adj[a][b] = Math.min(adj[a][b], adj[a][k] + adj[k][b]);
      }
    }
  }
  let count = 0;
  for (let i = 1; i <= n; i++) {
    let known = 0;
    for (let j = 1; j <= n; j++) {
      if (adj[i][j] !== INF || adj[j][i] !== INF) {
        known++; // i와 j의 상대 순위를 안다
      }
    }
    if (known === n) {
      count++; // 모든 학생과 비교 가능 → 순위 확정
    }
  }
  return count;
}
```

> **핵심 통찰**: "순위 확정" = "나보다 위인 사람 + 아래인 사람 = N−1명"이고, 이는 **도달 가능성**(adj[i][j] 또는 adj[j][i]가 유한)으로 판정된다. 최단 경로 알고리즘을 거리가 아닌 **연결성** 판정에 쓰는 응용이다.

## Q39 화성 탐사

| 항목 | 값 |
|------|-----|
| 난이도 | ★★★ 중 |
| 기출 | ACM-ICPC |

### 문제 요약

N×N 격자에서 (0,0)→(N-1,N-1)로 상하좌우 이동할 때 **지나는 칸 비용의 합 최소**.

예: `[[5,5,4],[3,9,1],[3,2,7]]` → `20`

### 핵심 아이디어

비용이 **칸(노드)에** 있는 격자 다익스트라다. 각 칸을 노드로, "이동 비용 = 도착 칸의 값"으로 두고 MinHeap 다익스트라를 돌린다.

```ts
function mars(n: number, grid: number[][]): number {
  const INF = 1e9;
  const dist = Array.from({ length: n }, () => new Array(n).fill(INF));
  const dx = [-1, 1, 0, 0];
  const dy = [0, 0, -1, 1];
  const pq = new MinHeap<[number, number, number]>((a, b) => a[0] - b[0]); // [거리, x, y]

  dist[0][0] = grid[0][0]; // 시작 칸 비용 포함
  pq.push([grid[0][0], 0, 0]);

  while (pq.size > 0) {
    const [d, x, y] = pq.pop()!;
    if (dist[x][y] < d) {
      continue;
    }
    for (let i = 0; i < 4; i++) {
      const nx = x + dx[i];
      const ny = y + dy[i];
      if (nx >= 0 && nx < n && ny >= 0 && ny < n) {
        const cost = d + grid[nx][ny]; // 도착 칸의 비용 추가
        if (cost < dist[nx][ny]) {
          dist[nx][ny] = cost;
          pq.push([cost, nx, ny]);
        }
      }
    }
  }
  return dist[n - 1][n - 1];
}
```

> **핵심 통찰**: 격자 BFS와 골격은 같지만 **칸마다 비용이 다르므로 BFS가 아닌 다익스트라**(우선순위 큐)를 써야 한다. 가중치가 모두 1이면 BFS, 다르면 다익스트라 — 이 구분이 핵심이다.

## Q40 숨바꼭질

| 항목 | 값 |
|------|-----|
| 난이도 | ★★★ 중 |
| 기출 | USACO |

### 문제 요약

1번 헛간에서 **최단 거리(길 개수)가 가장 먼 헛간**의 번호, 그 거리, 그 거리를 갖는 헛간 개수를 구하라. (양방향, N ≤ 20,000)

예: N=6, 간선 `(3,6)(4,3)(3,2)(1,3)(1,2)(2,4)(5,2)` → `4 2 3`

### 핵심 아이디어

가중치가 모두 1이므로 **BFS**로 충분하다(다익스트라 불필요). 거리 배열에서 최댓값을 갖는 가장 작은 번호와 개수를 집계한다.

```ts
function hideAndSeek(n: number, edges: [number, number][]): [number, number, number] {
  const graph: number[][] = Array.from({ length: n + 1 }, () => []);
  for (const [a, b] of edges) {
    graph[a].push(b);
    graph[b].push(a);
  }
  const dist = new Array(n + 1).fill(-1);
  dist[1] = 0;
  const queue = [1];
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
  let maxDist = 0;
  let node = 1;
  let count = 0;
  for (let i = 1; i <= n; i++) {
    if (dist[i] > maxDist) {
      maxDist = dist[i];
      node = i; // 더 먼 노드 (i가 증가 순회라 가장 작은 번호 유지)
      count = 1;
    } else if (dist[i] === maxDist) {
      count++;
    }
  }
  return [node, maxDist, count];
}
console.log(hideAndSeek(6, [[3, 6], [4, 3], [3, 2], [1, 3], [1, 2], [2, 4], [5, 2]])); // [4, 2, 3]
```

---

## 요약

- **플로이드**: 모든 쌍 최단 거리, 중복 노선은 최솟값, 도달 불가는 0 출력.
- **정확한 순위**: 플로이드 워셜로 **도달 가능성** 판정 — i가 N개 전부와 관계 있으면 순위 확정.
- **화성 탐사**: 비용이 칸에 있는 **격자 다익스트라**(가중치 다름 → BFS 아님).
- **숨바꼭질**: 가중치 1이라 **BFS**로 최단 거리 → 최댓값 집계.
- 핵심 구분: 모든 쌍은 플로이드, 한 점은 다익스트라(가중치 다름)/BFS(가중치 1).
