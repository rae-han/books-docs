# Chapter 09: 최단 경로 (Shortest Path)

> 가장 짧은 경로를 찾는 "길 찾기" 알고리즘. **한 지점 → 모든 지점**은 다익스트라, **모든 지점 → 모든 지점**은 플로이드 워셜로 푼다.

## 핵심 질문

- 다익스트라와 플로이드 워셜은 각각 언제 선택하는가?
- TypeScript에는 우선순위 큐가 없는데, 다익스트라를 어떻게 효율적으로 구현하는가?
- 두 알고리즘의 시간복잡도와 그 근거는 무엇인가?

## 1. 최단 경로 개요

| 알고리즘 | 용도 | 시간복잡도 | 분류 |
|------|------|-----------|------|
| 다익스트라(*Dijkstra*) | 한 지점 → 다른 모든 지점 (**음의 간선 없음**) | O(E log V) | 그리디 |
| 플로이드 워셜(*Floyd-Warshall*) | 모든 지점 → 모든 지점 | O(N³) | 다이나믹 프로그래밍 |

> **핵심 통찰**: 다익스트라는 "매번 최단 거리 노드를 선택"하므로 **그리디**(Ch 03), 플로이드 워셜은 "거쳐 가는 노드 k 기준 점화식"으로 갱신하므로 **DP**(Ch 08)다. 즉 앞 챕터들의 사고방식이 그대로 최단 경로에 적용된다.

## 2. 다익스트라 — 한 지점에서 모든 지점

음의 간선이 없을 때, 시작 노드에서 각 노드까지의 최단 거리를 구한다. 원리는 "방문 안 한 노드 중 **최단 거리가 가장 짧은 노드**를 골라, 그 노드를 거치는 경로로 최단 거리 테이블을 갱신"하는 것의 반복이다.

매번 최단 노드를 **선형 탐색**하면 O(V²)이지만, **우선순위 큐(최소 힙)** 로 O(log V)에 꺼내면 전체 O(E log V)로 빨라진다.

### 2.1 우선순위 큐 — TypeScript에서 직접 구현

> **함정**: 파이썬은 `heapq`(최소 힙)를 표준 제공하지만, **JavaScript/TypeScript에는 내장 우선순위 큐가 없다**. 코딩 테스트에서 다익스트라·프림 등을 쓰려면 **최소 힙을 직접 구현**해야 한다. 아래 클래스를 외워 두면 유용하다.

```ts
class MinHeap<T> {
  private heap: T[] = [];
  // compare(a, b) < 0 이면 a가 우선(먼저 pop)
  constructor(private compare: (a: T, b: T) => number) {}

  get size(): number {
    return this.heap.length;
  }

  push(item: T): void {
    this.heap.push(item);
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

  private bubbleUp(i: number): void {
    while (i > 0) {
      const parent = Math.floor((i - 1) / 2);
      if (this.compare(this.heap[i], this.heap[parent]) >= 0) {
        break;
      }
      [this.heap[i], this.heap[parent]] = [this.heap[parent], this.heap[i]];
      i = parent;
    }
  }

  private bubbleDown(i: number): void {
    const n = this.heap.length;
    while (true) {
      let smallest = i;
      const left = 2 * i + 1;
      const right = 2 * i + 2;
      if (left < n && this.compare(this.heap[left], this.heap[smallest]) < 0) {
        smallest = left;
      }
      if (right < n && this.compare(this.heap[right], this.heap[smallest]) < 0) {
        smallest = right;
      }
      if (smallest === i) {
        break;
      }
      [this.heap[i], this.heap[smallest]] = [this.heap[smallest], this.heap[i]];
      i = smallest;
    }
  }
}
```

### 2.2 다익스트라 코드

```python
# Python (책 원본) — heapq 사용
import heapq

def dijkstra(start):
    q = []
    heapq.heappush(q, (0, start))  # (거리, 노드)
    distance[start] = 0
    while q:
        dist, now = heapq.heappop(q)
        if distance[now] < dist:   # 이미 더 짧은 경로로 처리됨 → 무시
            continue
        for next_node, weight in graph[now]:
            cost = dist + weight
            if cost < distance[next_node]:
                distance[next_node] = cost
                heapq.heappush(q, (cost, next_node))
```

```ts
// TypeScript — 위 MinHeap 사용
const INF = 1e9;

function dijkstra(start: number, graph: [number, number][][], n: number): number[] {
  const distance = new Array(n + 1).fill(INF);
  // [거리, 노드] 를 거리 기준 최소 힙으로
  const pq = new MinHeap<[number, number]>((a, b) => a[0] - b[0]);

  pq.push([0, start]);
  distance[start] = 0;

  while (pq.size > 0) {
    const [dist, now] = pq.pop()!;
    // 이미 더 짧은 경로로 처리된 노드면 무시
    if (distance[now] < dist) {
      continue;
    }
    for (const [next, weight] of graph[now]) {
      const cost = dist + weight;
      if (cost < distance[next]) {
        distance[next] = cost;
        pq.push([cost, next]);
      }
    }
  }
  return distance;
}
```

**시간복잡도**: O(E log V). 노드의 개수 5,000개를 넘으면 O(V²) 단순 버전 대신 이 힙 버전을 써야 한다.

> **함정**: `if (distance[now] < dist) continue;`가 핵심이다. 같은 노드가 더 큰 거리로 큐에 여러 번 들어갈 수 있는데, 이미 더 짧게 처리됐다면 건너뛴다. 이 검사가 없으면 불필요한 재처리로 느려진다.

## 3. 플로이드 워셜 — 모든 지점에서 모든 지점

거쳐 가는 노드 `k`를 1부터 N까지 늘려 가며, "a→b 직접" vs "a→k→b 경유"를 비교해 더 짧은 쪽으로 갱신한다. **2차원 DP 테이블**을 쓴다.

> 점화식: `D[a][b] = min(D[a][b], D[a][k] + D[k][b])`

```ts
const INF = 1e9;

function floydWarshall(n: number, edges: [number, number, number][]): number[][] {
  // (n+1)×(n+1) 테이블을 INF로 초기화
  const graph = Array.from({ length: n + 1 }, () => new Array(n + 1).fill(INF));
  // 자기 자신으로 가는 비용은 0
  for (let i = 1; i <= n; i++) {
    graph[i][i] = 0;
  }
  // 간선 정보 입력
  for (const [a, b, c] of edges) {
    graph[a][b] = c;
  }
  // 점화식에 따라 3중 반복
  for (let k = 1; k <= n; k++) {
    for (let a = 1; a <= n; a++) {
      for (let b = 1; b <= n; b++) {
        graph[a][b] = Math.min(graph[a][b], graph[a][k] + graph[k][b]);
      }
    }
  }
  return graph;
}
```

**시간복잡도**: O(N³). N이 작을 때(보통 ≤ 500)만 쓴다.

> **함정**: 반복문 순서는 **반드시 `k`(경유 노드)가 가장 바깥**이어야 한다. a, b가 바깥에 오면 아직 갱신 안 된 중간값을 참조해 틀린 답이 나온다.

---

## 4. 실전 문제 1 — 미래 도시

| 항목 | 값 |
|------|-----|
| 난이도 | ★★★ 중 |
| 풀이 시간 | 40분 |
| 시간 제한 | 1초 |
| 기출 | M 기업 코딩 테스트 |

### 문제 요약

1번 회사에서 출발해 **K번을 거쳐 X번**으로 가는 최소 이동 시간을 구하라. 모든 도로는 양방향, 비용 1. 도달 불가면 -1. (N, M ≤ 100)

예: N=5, 도로 7개, X=4, K=5 → `3` (1→3→5→4)

### 핵심 아이디어

N이 작고 "여러 지점 간 최단 거리"가 필요하므로 **플로이드 워셜**이 적합하다. 답은 `d[1][K] + d[K][X]`.

### 코드

```ts
const input = `5 7
1 2
1 3
1 4
2 4
3 4
3 5
4 5
4 5`;

const lines = input.split("\n");
const [n, m] = lines[0].split(" ").map(Number);
const INF = 1e9;
const graph = Array.from({ length: n + 1 }, () => new Array(n + 1).fill(INF));
for (let i = 1; i <= n; i++) {
  graph[i][i] = 0;
}
for (let i = 1; i <= m; i++) {
  const [a, b] = lines[i].split(" ").map(Number);
  graph[a][b] = 1; // 양방향
  graph[b][a] = 1;
}
const [x, k] = lines[m + 1].split(" ").map(Number);

for (let via = 1; via <= n; via++) {
  for (let a = 1; a <= n; a++) {
    for (let b = 1; b <= n; b++) {
      graph[a][b] = Math.min(graph[a][b], graph[a][via] + graph[via][b]);
    }
  }
}

const result = graph[1][k] + graph[k][x];
console.log(result >= INF ? -1 : result); // 3
```

## 5. 실전 문제 2 — 전보

| 항목 | 값 |
|------|-----|
| 난이도 | ★★★ 상 |
| 풀이 시간 | 60분 |
| 시간 제한 | 1초 |
| 기출 | 유명 알고리즘 대회 |

### 문제 요약

도시 C에서 단방향 통로로 메시지를 보낼 때, **메시지를 받는 도시 수**와 **모두 받는 데 걸리는 시간**(가장 먼 도시까지의 최단 거리)을 구하라. (N ≤ 30,000, M ≤ 200,000)

예: 도시 3, C=1, 통로 `1→2(4)`, `1→3(2)` → `2 4`

### 핵심 아이디어

"한 지점에서 다른 모든 지점까지의 최단 거리"이고 N·M이 크므로 **힙 기반 다익스트라**다. 결과 거리 테이블에서 도달 가능한 노드 수(자신 제외)와 최댓값을 집계한다.

### 코드

```ts
const input = `3 2 1
1 2 4
1 3 2`;

const lines = input.split("\n");
const [n, m, start] = lines[0].split(" ").map(Number);
const graph: [number, number][][] = Array.from({ length: n + 1 }, () => []);
for (let i = 1; i <= m; i++) {
  const [x, y, z] = lines[i].split(" ").map(Number);
  graph[x].push([y, z]); // 단방향
}

const distance = dijkstra(start, graph, n); // 위 2.2의 함수 재사용

let count = 0;
let maxDistance = 0;
for (let i = 1; i <= n; i++) {
  if (distance[i] !== INF) {
    count++;
    maxDistance = Math.max(maxDistance, distance[i]);
  }
}
console.log(count - 1, maxDistance); // 2 4  (시작 노드 제외)
```

> **핵심 통찰**: 다익스트라의 결과는 "시작점에서 모든 노드까지의 최단 거리 배열"이다. 이 배열을 **어떻게 집계하느냐**가 문제마다 다를 뿐, 다익스트라 본체는 거의 그대로 재사용된다. 전보는 단방향이라 `graph[x].push([y, z])`만 넣는 점에 주의.

---

## 자주 하는 실수

| 실수 | 원인 | 해결 |
|------|------|------|
| 다익스트라에 배열을 큐로 사용 | 매번 최소 선형 탐색 O(V) | **MinHeap** 직접 구현 |
| 힙에서 꺼낸 뒤 방문 검사 누락 | 같은 노드 중복 처리 | `if (distance[now] < dist) continue` |
| 플로이드 반복문 순서 오류 | k가 안쪽이면 오답 | **k(경유)를 최바깥** 루프로 |
| 음의 간선에 다익스트라 | 다익스트라 전제 위반 | 벨만-포드 등 다른 알고리즘 |
| 단/양방향 혼동 | 간선 입력 방향 실수 | 양방향이면 `graph[a][b]`·`graph[b][a]` 둘 다 |

## 패턴 체크리스트

- [ ] 한 지점 → 모든 지점, 음의 간선 없음? → **다익스트라**(힙)
- [ ] 모든 지점 → 모든 지점, N ≤ 500? → **플로이드 워셜**(3중 루프)
- [ ] TS라면 **MinHeap**을 준비했는가?
- [ ] 다익스트라에 "이미 처리된 노드 무시" 검사를 넣었는가?
- [ ] 플로이드 워셜에서 **k가 최바깥** 루프인가?
- [ ] 간선이 단방향인지 양방향인지 확인했는가?

## 요약

- **다익스트라**: 1→전체, 음의 간선 없음, **그리디** + 최소 힙 → O(E log V).
- **플로이드 워셜**: 전체→전체, **DP** 점화식 `D[a][b]=min(D[a][b], D[a][k]+D[k][b])` → O(N³), k가 최바깥.
- **TS 핵심**: 우선순위 큐가 없어 **MinHeap을 직접 구현**해야 한다(이 챕터의 가장 큰 자산).
- 미래 도시(플로이드, `d[1][k]+d[k][x]`), 전보(다익스트라 + 결과 집계).
- 그리디(Ch 03)·DP(Ch 08)의 사고가 최단 경로로 확장된다. 다음 Ch 10의 크루스칼(MST)도 그리디 계열이다.
