# Chapter 18: 그래프 이론 기출문제

> Ch 10에서 배운 그래프 이론 유형의 기출문제 모음(Q41~Q45). **Union-Find**, **크루스칼 MST**, **위상 정렬**을 다양한 형태로 응용한다.

## 핵심 질문

- 연결성·집합 판정은 Union-Find로 어떻게 푸는가?
- "최소 비용 연결"은 크루스칼 MST, 간선이 너무 많으면 어떻게 줄이는가?
- 순서 결정/모호성/사이클은 위상 정렬로 어떻게 판정하는가?

> Union-Find의 `find`/`union`은 Ch 10에서 정의한 경로 압축 버전을 재사용한다.

---

## Q41 여행 계획

| 항목 | 값 |
|------|-----|
| 난이도 | ★★ 중하 |
| 기출 | 핵심 유형 |

### 문제 요약

여행지 연결 정보(인접 행렬)가 주어질 때, 여행 계획의 **모든 도시가 같은 집합**(서로 오갈 수 있음)이면 YES.

예: N=5, 계획 `[2,3,4,3]` → `YES`

### 핵심 아이디어

연결된 도시들을 Union-Find로 합친 뒤, 계획의 모든 도시가 **같은 루트**인지 확인한다.

```ts
function travelPlan(n: number, matrix: number[][], plan: number[]): string {
  const parent = Array.from({ length: n + 1 }, (_, i) => i);
  const find = (x: number): number => {
    if (parent[x] !== x) {
      parent[x] = find(parent[x]);
    }
    return parent[x];
  };
  const union = (a: number, b: number) => {
    const ra = find(a);
    const rb = find(b);
    if (ra < rb) {
      parent[rb] = ra;
    } else {
      parent[ra] = rb;
    }
  };

  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      if (matrix[i][j] === 1) {
        union(i + 1, j + 1);
      }
    }
  }
  const root = find(plan[0]);
  for (const city of plan) {
    if (find(city) !== root) {
      return "NO";
    }
  }
  return "YES";
}
```

## Q42 탑승구

| 항목 | 값 |
|------|-----|
| 난이도 | ★★★ 중 |
| 기출 | CCC |

### 문제 요약

각 비행기는 `1~g[i]`번 탑승구 중 하나에 도킹(영구). 도킹 불가하면 중단. **최대 도킹 수**를 구하라.

예: G=4, 비행기 `[4,1,1]` → `2`

### 핵심 아이디어

각 비행기를 **가능한 가장 큰 번호** 탑승구에 도킹하는 그리디. Union-Find로 "g 이하의 빈 탑승구"를 O(α)에 찾는다(`find(g)`가 빈 자리, 도킹하면 그 자리를 `자리−1`에 합쳐 다음 후보로).

```ts
function gates(g: number, planes: number[]): number {
  const parent = Array.from({ length: g + 1 }, (_, i) => i);
  const find = (x: number): number => {
    if (parent[x] !== x) {
      parent[x] = find(parent[x]);
    }
    return parent[x];
  };

  let count = 0;
  for (const gi of planes) {
    const slot = find(gi); // gi 이하의 빈 탑승구
    if (slot === 0) {
      break; // 도킹 불가 → 중단
    }
    parent[slot] = slot - 1; // 사용 처리, 다음 후보는 slot-1
    count++;
  }
  return count;
}
```

> **핵심 통찰**: "가능한 큰 자리에 배정 + 그 자리를 한 칸 아래로 연결"은 **Union-Find로 빈 슬롯을 추적**하는 전형적 그리디다. `find(g)`가 0이면 1~g가 모두 차서 도킹 불가다.

## Q43 어두운 길

| 항목 | 값 |
|------|-----|
| 난이도 | ★★★ 중 |
| 기출 | University of Ulm Local Contest |

### 문제 요약

모든 집이 연결되도록 가로등(도로)을 남길 때, **비활성화로 절약할 수 있는 최대 금액**.

예: N=7, 도로 11개 → `51`

### 핵심 아이디어

**전체 도로 비용 − MST 비용** = 절약액. 크루스칼로 MST를 구한다.

```ts
function darkRoad(n: number, edges: [number, number, number][]): number {
  let total = 0;
  for (const [, , z] of edges) {
    total += z;
  }
  const parent = Array.from({ length: n }, (_, i) => i);
  const find = (x: number): number => {
    if (parent[x] !== x) {
      parent[x] = find(parent[x]);
    }
    return parent[x];
  };

  edges.sort((p, q) => p[2] - q[2]);
  let mst = 0;
  for (const [x, y, z] of edges) {
    if (find(x) !== find(y)) {
      parent[find(x)] = find(y);
      mst += z;
    }
  }
  return total - mst;
}
```

## Q44 행성 터널

| 항목 | 값 |
|------|-----|
| 난이도 | ★★★ 상 |
| 기출 | 백준 2887 |

### 문제 요약

3차원 좌표 행성들을 연결하는 비용은 `min(|Δx|, |Δy|, |Δz|)`. 모두 연결하는 **최소 비용**. (N ≤ 100,000)

예: 5개 행성 → `4`

### 핵심 아이디어

간선이 N²개라 다 만들면 시간 초과. 비용이 **각 축의 차이 중 최소**이므로, **각 축으로 정렬한 인접 행성 쌍만** 후보 간선으로 두면 충분하다(축당 N−1개, 총 3(N−1)개). 이후 크루스칼.

```ts
function planetTunnel(planets: number[][]): number {
  const n = planets.length;
  const edges: [number, number, number][] = [];
  // 각 축으로 정렬 후 인접 쌍만 간선 후보
  for (let axis = 0; axis < 3; axis++) {
    const sorted = planets.map((p, i): [number, number] => [p[axis], i]).sort((a, b) => a[0] - b[0]);
    for (let i = 0; i < n - 1; i++) {
      edges.push([Math.abs(sorted[i][0] - sorted[i + 1][0]), sorted[i][1], sorted[i + 1][1]]);
    }
  }
  edges.sort((a, b) => a[0] - b[0]);

  const parent = Array.from({ length: n }, (_, i) => i);
  const find = (x: number): number => {
    if (parent[x] !== x) {
      parent[x] = find(parent[x]);
    }
    return parent[x];
  };

  let mst = 0;
  for (const [cost, a, b] of edges) {
    if (find(a) !== find(b)) {
      parent[find(a)] = find(b);
      mst += cost;
    }
  }
  return mst;
}
```

> **핵심 통찰**: 완전 그래프 MST에서 간선이 너무 많으면 **유의미한 간선만 추려야** 한다. "비용 = 축 차이의 최소"라는 구조 덕분에, 각 축 정렬 후 인접한 쌍만 보면 모든 MST 후보가 포함된다는 게 핵심 통찰이다.

## Q45 최종 순위

| 항목 | 값 |
|------|-----|
| 난이도 | ★★★ 상 |
| 기출 | NWERC 2010 |

### 문제 요약

작년 순위와 "순위가 바뀐 쌍"이 주어질 때 올해 순위를 구하라. 유일하게 못 정하면 `?`, 모순(사이클)이면 `IMPOSSIBLE`.

예: n=5, 작년 `[5,4,3,2,1]`, 바뀐 쌍 `(2,4)(3,4)` → `5 3 2 4 1`

### 핵심 아이디어

작년 순위로 "앞선 팀 → 뒤진 팀" 간선을 모두 만든 뒤, **바뀐 쌍의 간선 방향을 뒤집는다**(진입 차수도 갱신). 그 후 위상 정렬:
- 위상 정렬 중 큐에 **노드가 2개 이상** 동시에 가능하면 순위가 모호 → `?`
- 노드를 N개 뽑기 전에 **큐가 비면** 사이클 → `IMPOSSIBLE`

```ts
function finalRank(n: number, lastYear: number[], swaps: [number, number][]): string {
  const indegree = new Array(n + 1).fill(0);
  const adj: Set<number>[] = Array.from({ length: n + 1 }, () => new Set());
  // 작년: 앞선 팀 → 뒤진 팀
  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      adj[lastYear[i]].add(lastYear[j]);
      indegree[lastYear[j]]++;
    }
  }
  // 바뀐 쌍 → 간선 방향 뒤집기
  for (const [a, b] of swaps) {
    if (adj[a].has(b)) {
      adj[a].delete(b);
      adj[b].add(a);
      indegree[b]--;
      indegree[a]++;
    } else {
      adj[b].delete(a);
      adj[a].add(b);
      indegree[a]--;
      indegree[b]++;
    }
  }

  const result: number[] = [];
  const queue: number[] = [];
  for (let i = 1; i <= n; i++) {
    if (indegree[i] === 0) {
      queue.push(i);
    }
  }
  let head = 0;
  let ambiguous = false;
  for (let cnt = 0; cnt < n; cnt++) {
    if (head >= queue.length) {
      return "IMPOSSIBLE"; // 큐가 비면 사이클
    }
    if (queue.length - head > 1) {
      ambiguous = true; // 동시 후보 2개 이상 → 모호
    }
    const now = queue[head++];
    result.push(now);
    for (const next of adj[now]) {
      indegree[next]--;
      if (indegree[next] === 0) {
        queue.push(next);
      }
    }
  }
  return ambiguous ? "?" : result.join(" ");
}
console.log(finalRank(5, [5, 4, 3, 2, 1], [[2, 4], [3, 4]])); // 5 3 2 4 1
```

> **핵심 통찰**: "순위" = 모든 팀의 전순서이므로 작년 순위는 **완전한 방향 그래프**다. 위상 정렬에서 **유일성(큐에 1개)** 과 **무모순성(사이클 없음)** 을 동시에 검사하는 것이 이 문제의 핵심이다.

---

## 요약

- **여행 계획**: Union-Find로 연결성 → 계획 도시들이 같은 루트인지.
- **탑승구**: Union-Find로 "빈 슬롯 추적" 그리디.
- **어두운 길**: 크루스칼 MST, 절약 = **전체 − MST**.
- **행성 터널**: 간선 폭발 → **각 축 정렬 인접 쌍만** 후보로 + 크루스칼.
- **최종 순위**: 작년 완전 그래프 + 간선 뒤집기 → 위상 정렬로 **유일성(`?`)·사이클(`IMPOSSIBLE`)** 판정.
- 그래프 이론 기출의 핵심은 **문제를 Union-Find/MST/위상 정렬 중 무엇으로 환원**하느냐다.
