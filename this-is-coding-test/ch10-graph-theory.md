# Chapter 10: 그래프 이론 (Graph Theory)

> DFS/BFS(Ch 05)와 최단 경로(Ch 09) 외의 핵심 그래프 알고리즘. **서로소 집합(Union-Find)**, **최소 신장 트리(크루스칼)**, **위상 정렬**을 다룬다.

## 핵심 질문

- 서로소 집합(Union-Find)은 무엇을 빠르게 하며, **경로 압축**은 왜 필요한가?
- 최소 신장 트리(MST)를 크루스칼 알고리즘으로 어떻게 찾는가?
- 위상 정렬은 어떤 "순서가 정해진 작업" 문제를 푸는가?

## 1. 그래프 vs 트리 (복습)

| | 그래프 | 트리 |
|------|------|------|
| 방향성 | 방향/무방향 | 방향 (부모→자식) |
| 순환성 | 순환 가능 | 비순환 |
| 루트 | 없음 | 존재 |
| 모델 | 네트워크 | 계층 |

표현은 **인접 행렬**(O(V²) 메모리, O(1) 조회)과 **인접 리스트**(O(E) 메모리, O(V) 조회) 두 가지(Ch 05 참고). 문제의 노드·간선 수에 맞게 고른다.

## 2. 서로소 집합 (Union-Find)

서로소 집합(*Disjoint Set - 공통 원소가 없는 집합들*)은 "이 둘이 **같은 집합(연결됨)** 인가?"를 빠르게 판단하는 자료구조다. 두 연산으로 동작한다.

- `find(x)`: x가 속한 집합의 **루트(대표)** 를 찾는다.
- `union(a, b)`: a와 b가 속한 두 집합을 합친다.

### 2.1 find / union + 경로 압축

```python
# Python (책 원본) — 경로 압축 적용
def find_parent(parent, x):
    if parent[x] != x:
        parent[x] = find_parent(parent, parent[x])  # 경로 압축
    return parent[x]

def union_parent(parent, a, b):
    a = find_parent(parent, a)
    b = find_parent(parent, b)
    if a < b:
        parent[b] = a
    else:
        parent[a] = b
```

```ts
// TypeScript
function findParent(parent: number[], x: number): number {
  if (parent[x] !== x) {
    // 경로 압축: 루트를 직접 부모로 갱신
    parent[x] = findParent(parent, parent[x]);
  }
  return parent[x];
}

function unionParent(parent: number[], a: number, b: number): void {
  const rootA = findParent(parent, a);
  const rootB = findParent(parent, b);
  if (rootA < rootB) {
    parent[rootB] = rootA; // 번호가 작은 쪽을 부모로
  } else {
    parent[rootA] = rootB;
  }
}

// 부모 테이블 초기화: 각자 자기 자신이 부모
const parent = Array.from({ length: n + 1 }, (_, i) => i);
```

> **함정**: 경로 압축(`parent[x] = findParent(...)`)이 없으면 트리가 한 줄로 길어져 `find`가 O(V)까지 느려진다. 한 줄 추가로 거의 상수 시간이 되므로 **반드시 포함**한다. 또 `parent`는 `Array.from({length}, (_, i) => i)`로 "자기 자신"으로 초기화해야 한다.

### 2.2 사이클 판별

무방향 그래프에서 간선을 하나씩 union하다가, **두 노드의 루트가 이미 같으면 사이클**이다.

```ts
let cycle = false;
for (const [a, b] of edges) {
  if (findParent(parent, a) === findParent(parent, b)) {
    cycle = true; // 이미 연결됨 → 사이클
    break;
  }
  unionParent(parent, a, b);
}
```

## 3. 신장 트리와 크루스칼 (MST)

신장 트리(*Spanning Tree*)는 모든 노드를 포함하면서 사이클이 없는 부분 그래프다(간선 = 노드 수 − 1). 그중 **간선 비용 합이 최소**인 것이 최소 신장 트리(MST)이며, **크루스칼 알고리즘**(그리디)으로 찾는다.

1. 간선을 비용 **오름차순 정렬**한다.
2. 비용이 작은 간선부터 확인해, **사이클이 안 생기면**(두 루트가 다르면) MST에 포함한다.

```ts
function kruskal(v: number, edges: [number, number, number][]): number {
  const parent = Array.from({ length: v + 1 }, (_, i) => i);
  // [비용, a, b] 를 비용 기준 정렬 (비교 함수 필수!)
  edges.sort((x, y) => x[0] - y[0]);
  let result = 0;
  for (const [cost, a, b] of edges) {
    if (findParent(parent, a) !== findParent(parent, b)) {
      unionParent(parent, a, b);
      result += cost;
    }
  }
  return result;
}
```

**시간복잡도**: O(E log E) — 간선 정렬이 지배적.

> **핵심 통찰**: 크루스칼은 **정렬(Ch 06) + 그리디(Ch 03) + 사이클 판별(Union-Find)** 의 결합이다. "가장 싼 간선부터, 사이클만 피해서" 고르면 항상 최적이라는 게 그리디 정당성의 핵심이다.

## 4. 위상 정렬

위상 정렬(*Topological Sort*)은 **방향 그래프에서 순서(선후 관계)를 지키며 노드를 나열**하는 것이다. "선수 과목을 먼저 듣는 순서"가 대표 예다. **진입 차수(*in-degree, 들어오는 간선 수*)** 와 큐를 쓴다.

1. 진입 차수가 0인 노드를 큐에 넣는다.
2. 큐에서 꺼내며, 그 노드에서 나가는 간선을 제거(인접 노드의 진입 차수 −1)하고, 0이 된 노드를 큐에 넣는다.

```ts
function topologySort(v: number, graph: number[][], indegree: number[]): number[] {
  const result: number[] = [];
  const queue: number[] = [];
  let head = 0; // O(1) 큐 (Ch 05 패턴)

  for (let i = 1; i <= v; i++) {
    if (indegree[i] === 0) {
      queue.push(i);
    }
  }
  while (head < queue.length) {
    const now = queue[head++];
    result.push(now);
    for (const next of graph[now]) {
      indegree[next]--;
      if (indegree[next] === 0) {
        queue.push(next);
      }
    }
  }
  return result;
}
```

**시간복잡도**: O(V + E).

> **함정**: 모든 노드를 방문하기 전에 큐가 비면 **사이클**이 있다는 뜻이다(사이클 노드는 진입 차수가 0이 안 됨). 큐는 `shift()` 대신 **head 포인터**로 O(1) 처리한다(Ch 05).

---

## 5. 실전 문제 1 — 팀 결성

| 항목 | 값 |
|------|-----|
| 난이도 | ★★ 중하 |
| 풀이 시간 | 20분 |
| 시간 제한 | 2초 |
| 기출 | 핵심 유형 |

### 문제 요약

`0 a b`(팀 합치기)와 `1 a b`(같은 팀 확인) 연산을 처리해, 확인 연산마다 YES/NO를 출력하라. (N, M ≤ 100,000)

예: 7명, 8개 연산 → `NO NO YES`

### 코드

```ts
const input = `7 8
0 1 3
1 1 7
0 7 6
1 7 1
0 3 7
0 4 2
0 1 1
1 1 1`;

const lines = input.split("\n");
const [n, m] = lines[0].split(" ").map(Number);
const parent = Array.from({ length: n + 1 }, (_, i) => i);
const output: string[] = [];

for (let i = 1; i <= m; i++) {
  const [oper, a, b] = lines[i].split(" ").map(Number);
  if (oper === 0) {
    unionParent(parent, a, b); // 팀 합치기
  } else {
    // 같은 팀 확인
    output.push(findParent(parent, a) === findParent(parent, b) ? "YES" : "NO");
  }
}
console.log(output.join("\n")); // NO\nNO\nYES
```

## 6. 실전 문제 2 — 도시 분할 계획

| 항목 | 값 |
|------|-----|
| 난이도 | ★★★ 중 |
| 풀이 시간 | 40분 |
| 시간 제한 | 2초 |
| 기출 | 백준 1647 |

### 문제 요약

마을(N개 집, M개 길)을 **2개의 분리된 마을**로 나누되, 남는 길 유지비 합을 최소로 하라. (N ≤ 100,000, M ≤ 1,000,000)

예: 7집 12길 → `8`

### 핵심 아이디어

전체에서 **MST를 구한 뒤, 그 MST에서 가장 비싼 간선 하나를 제거**하면 두 개의 연결된 부분(=두 마을)이 된다. 크루스칼로 MST를 만들며 마지막에 포함된(=가장 비싼) 간선을 빼면 답이다.

### 코드

```ts
const input = `7 12
1 2 3
1 3 2
3 2 1
2 5 2
3 4 4
7 3 6
5 1 5
1 6 2
6 4 1
6 5 3
4 5 3
6 7 4`;

const lines = input.split("\n");
const [v, e] = lines[0].split(" ").map(Number);
const parent = Array.from({ length: v + 1 }, (_, i) => i);
const edges: [number, number, number][] = [];
for (let i = 1; i <= e; i++) {
  const [a, b, cost] = lines[i].split(" ").map(Number);
  edges.push([cost, a, b]);
}
edges.sort((x, y) => x[0] - y[0]);

let result = 0;
let last = 0; // MST에 포함된 가장 비싼 간선
for (const [cost, a, b] of edges) {
  if (findParent(parent, a) !== findParent(parent, b)) {
    unionParent(parent, a, b);
    result += cost;
    last = cost;
  }
}
console.log(result - last); // 8 (가장 비싼 간선 제거 → 마을 2개)
```

> **핵심 통찰**: MST의 간선은 비용 오름차순으로 추가되므로 **마지막에 추가된 간선이 가장 비싸다**. 이걸 빼면 트리가 둘로 쪼개진다. "최소 비용 2분할"을 "MST − 최대 간선"으로 환원하는 발상이 핵심이다.

## 7. 실전 문제 3 — 커리큘럼

| 항목 | 값 |
|------|-----|
| 난이도 | ★★★ 상 |
| 풀이 시간 | 50분 |
| 시간 제한 | 2초 |
| 기출 | 핵심 유형 |

### 문제 요약

각 강의는 선수 강의가 있을 수 있다. 각 강의를 듣기까지의 **최소 시간**을 구하라. (선수 강의를 모두 들어야 수강 가능, 동시 수강 가능)

입력은 `강의시간 [선수강의들...] -1`. 예: 5강의 → `10 20 14 18 17`

### 핵심 아이디어

**위상 정렬 + DP**다. 위상 순서대로 진행하며, 각 강의의 완료 시간을 `result[i] = max(result[i], result[선행] + time[i])`로 갱신한다. "가장 오래 걸리는 선행 경로"를 따라야 하므로 max를 쓴다.

### 코드

```ts
const input = `5
10 -1
10 1 -1
4 1 -1
4 3 1 -1
3 3 -1`;

const lines = input.split("\n");
const v = Number(lines[0]);
const indegree = new Array(v + 1).fill(0);
const graph: number[][] = Array.from({ length: v + 1 }, () => []);
const time = new Array(v + 1).fill(0);

for (let i = 1; i <= v; i++) {
  const data = lines[i].split(" ").map(Number);
  time[i] = data[0]; // 첫 수는 강의 시간
  // 가운데 값들이 선수 강의 (마지막 -1 제외)
  for (let j = 1; j < data.length - 1; j++) {
    const pre = data[j];
    indegree[i]++;
    graph[pre].push(i); // 선수 강의 → 현재 강의
  }
}

function topologySort(): number[] {
  const result = [...time]; // 1차원 배열은 spread로 복사 충분
  const queue: number[] = [];
  let head = 0;
  for (let i = 1; i <= v; i++) {
    if (indegree[i] === 0) {
      queue.push(i);
    }
  }
  while (head < queue.length) {
    const now = queue[head++];
    for (const next of graph[now]) {
      // 가장 오래 걸리는 선행 경로 + 현재 강의 시간
      result[next] = Math.max(result[next], result[now] + time[next]);
      indegree[next]--;
      if (indegree[next] === 0) {
        queue.push(next);
      }
    }
  }
  return result;
}

const result = topologySort();
console.log(result.slice(1).join("\n")); // 10 20 14 18 17
```

> **함정**: 파이썬은 `copy.deepcopy(time)`로 복사했지만, TS에서 **1차원 배열은 `[...time]`**(얕은 복사)로 충분하다(원소가 숫자라 깊이 없음). 단 2차원이면 `time.map((row) => [...row])`가 필요하다.

---

## 자주 하는 실수

| 실수 | 원인 | 해결 |
|------|------|------|
| 경로 압축 누락 | find가 O(V) | `parent[x] = findParent(...)` |
| parent를 0으로 초기화 | 자기 자신이 부모여야 함 | `Array.from({length}, (_, i) => i)` |
| 크루스칼 간선 정렬 누락 | 그리디 전제 깨짐 | `edges.sort((x,y) => x[0]-y[0])` |
| 위상 정렬 큐에 shift() | O(n) | head 포인터로 O(1) |
| deepcopy를 얕은 복사로 (2차원) | 원본 오염 | 2차원은 `arr.map(r => [...r])` |

## 패턴 체크리스트

- [ ] "두 원소가 같은 집합인가/연결됐나"? → **Union-Find**(경로 압축)
- [ ] 무방향 그래프 사이클 판별? → union 중 루트 같으면 사이클
- [ ] "최소 비용으로 전체 연결"? → **크루스칼 MST**
- [ ] "순서/선후 관계가 있는 작업 나열"? → **위상 정렬**(진입 차수 + 큐)
- [ ] 위상 순서로 값 누적이 필요? → 위상 정렬 + DP (max/min 갱신)

## 요약

- **Union-Find**: `find`(루트 찾기) + `union`(합치기), **경로 압축** 필수. 연결성·사이클 판별의 기반.
- **크루스칼(MST)**: 간선 오름차순 정렬 → 사이클 안 생기는 것만 포함. **정렬 + 그리디 + Union-Find**.
- **위상 정렬**: 진입 차수 0부터 큐로 펼침. O(V+E). 큐가 먼저 비면 사이클.
- 도시 분할(MST − 최대 간선), 커리큘럼(위상 정렬 + DP `max`)처럼 **앞 챕터 기법들의 결합**이 그래프 이론의 묘미.
- 이로써 Part 2 이론(Ch 03~10)이 끝난다. Part 3(Ch 11~)은 이 유형들의 기출문제 적용이다.
