# Chapter 18: Connecting Everything with Graphs (그래프로 뭐든지 연결하기)

## 핵심 질문

"앨리스의 친구는 누구인가"를 O(1)에 답하는 자료 구조는 무엇인가? 깊이 우선과 너비 우선은 언제 갈리는가? 그리고 가장 저렴한 항공 경로는 어떻게 계산되는가?

---

## 1. 그래프 - 관계에 특화된 자료 구조

친구 관계를 2차원 배열 `[["Alice","Bob"], ["Bob","Cynthia"], …]`로 저장하면 앨리스의 친구를 찾는 데 전체를 뒤져야 한다 - O(N). **그래프(*graph - 데이터가 서로 어떻게 연결되는지 표현하는 데 특화된 자료 구조*)**를 쓰면 O(1)이다.

### 1.1 그래프 대 트리

**모든 트리는 그래프이지만, 모든 그래프가 트리는 아니다.** 트리로 규정되려면:

- **사이클(cycle)**(서로 순환 참조하는 노드들)이 없어야 하고
- 모든 노드가 (간접적으로라도) **연결**되어 있어야 한다

그래프는 사이클이 있어도 되고(앨리스→다이애나→밥→앨리스), 연결되지 않은 정점(친구가 없는 신규 가입자)이 있어도 된다.

### 1.2 용어

- 그래프에서 노드는 **정점(vertex)**, 정점을 잇는 선은 **간선(edge)**
- 간선으로 연결된 정점들은 서로 **인접(adjacent)**하며 **이웃(neighbor)**이라 부른다
- 모든 정점이 어떻게든 연결된 그래프는 **연결 그래프(connected graph)**

### 1.3 구현

가장 기초적으로는 해시 테이블로 표현한다 - O(1) 룩업의 비결:

```typescript
const friends: Record<string, string[]> = {
  Alice: ["Bob", "Diana", "Fred"],
  Bob: ["Alice", "Cynthia", "Diana"],
  // ...
};
friends["Alice"];  // O(1)
```

**방향 그래프(*directed graph - 관계에 방향이 있는 그래프. 팔로우처럼 상호적이지 않은 관계를 표현*)**도 같은 방식으로 저장한다(배열에 "내가 팔로우하는 사람"만 담음).

객체 지향 구현:

```typescript
class Vertex {
  adjacentVertices: Vertex[] = [];
  constructor(public value: string) {}

  addAdjacentVertex(vertex: Vertex): void {
    if (this.adjacentVertices.includes(vertex)) {
      return;  // 무한 상호 등록 방지
    }
    this.adjacentVertices.push(vertex);
    vertex.addAdjacentVertex(this);  // 무방향 그래프: 상호 등록
  }
}
```

(참고: 인접 정점을 리스트로 저장하는 이 방식은 **인접 리스트**, 2차원 배열로 저장하는 대안은 **인접 행렬**이라 부른다. 이 책은 더 직관적인 인접 리스트를 쓴다. 또한 이후 논의는 연결 그래프를 가정한다 - 비연결 그래프는 모든 정점을 배열 등에 따로 보관해야 할 수 있다.)

## 2. 그래프 탐색

그래프에서 "탐색"은 보통 **한 정점에서 출발해 연결된 특정 정점을 찾는 것**(= 경로 찾기)을 뜻한다. **경로(path)**는 한 정점에서 다른 정점으로 가는 간선들의 순열이다. 특정 정점 찾기, 두 정점의 연결 여부 확인, 전체 순회 등에 쓰인다.

> **핵심 통찰**: 그래프 탐색의 관건은 **방문한 정점의 기록**이다. 그래프에는 사이클이 있을 수 있어서(트리·파일시스템과 달리) 기록하지 않으면 무한 순환에 빠진다. 방문 정점을 해시 테이블에 담아 O(1)로 확인한다.

### 2.1 깊이 우선 탐색 (DFS)

BST 순회(Ch15)·파일시스템 순회(Ch10)와 본질적으로 같은 재귀 알고리즘:

1. 임의 정점에서 시작, 해시 테이블에 방문 기록
2. 인접 정점들을 순회 - 방문한 정점은 무시
3. 방문하지 않은 인접 정점에 **재귀적으로 DFS**

```typescript
function dfsTraverse(
  vertex: Vertex,
  visitedVertices: Record<string, boolean> = {},
): void {
  visitedVertices[vertex.value] = true;
  console.log(vertex.value);
  for (const adjacentVertex of vertex.adjacentVertices) {
    if (visitedVertices[adjacentVertex.value]) {
      continue;
    }
    dfsTraverse(adjacentVertex, visitedVertices);
  }
}
```

(특정 값을 찾는 `dfs`는 여기에 "찾으면 그 정점을 반환하고, 재귀 결과가 있으면 위로 전달"을 더한 형태다.)

### 2.2 너비 우선 탐색 (BFS)

BFS는 재귀 대신 **큐**를 쓴다:

1. 시작 정점을 방문 기록하고 큐에 추가
2. 큐가 빌 때까지: 큐에서 정점을 꺼내 "현재 정점"으로 → 인접 정점 중 미방문 정점을 **방문 기록 후 큐에 추가**

```typescript
function bfsTraverse(startingVertex: Vertex): void {
  const queue = new Queue<Vertex>();
  const visitedVertices: Record<string, boolean> = {};
  visitedVertices[startingVertex.value] = true;
  queue.enqueue(startingVertex);

  while (queue.read()) {
    const currentVertex = queue.dequeue()!;
    console.log(currentVertex.value);
    for (const adjacentVertex of currentVertex.adjacentVertices) {
      if (!visitedVertices[adjacentVertex.value]) {
        visitedVertices[adjacentVertex.value] = true;
        queue.enqueue(adjacentVertex);
      }
    }
  }
}
```

### 2.3 DFS 대 BFS

> **핵심 통찰**: **BFS는 시작 정점에서 가까운 정점부터 나선형으로 퍼지고, DFS는 즉시 최대한 멀리 갔다가 막히면 돌아온다.** 질문은 하나 - "시작점 가까이에 있고 싶은가, 빨리 멀어지고 싶은가?"
>
> - 앨리스의 **직접 친구**만 찾기 → BFS (DFS는 친구의 친구까지 헤매고 온다)
> - 가계도에서 **증손주** 찾기 → DFS (BFS는 모든 자식·손주를 다 거쳐야 바닥에 닿는다)

### 2.4 그래프 탐색의 효율성 - O(V + E)

최악(전체 순회/없는 정점 찾기)에는 모든 정점 방문 + **각 정점의 인접 정점 확인**이 든다. 정점 수만으로는 부족하다 - 같은 5개 정점이라도 간선이 많은 그래프(21단계)와 적은 그래프(13단계)의 단계가 다르다.

그래서 변수 두 개로 표현한다: **O(V + E)** (V = 정점 수, E = 간선 수). 실제로는 각 간선이 양쪽에서 두 번씩 확인되어 V + 2E지만, 상수를 버려 O(V + E)다. 핵심 직관: **간선이 많을수록 탐색이 느려진다.** DFS든 BFS든 같다 - 다만 상황에 맞는 방식을 고르면 최악 시나리오에 이를 확률을 줄인다.

(현실 소프트웨어에서는 관계 데이터를 Neo4j 같은 **그래프 데이터베이스**에 저장하곤 한다 - 이 장의 개념들이 그 기반이다.)

## 3. 가중 그래프

**가중 그래프(*weighted graph - 간선에 추가 정보(가중치)를 붙인 그래프*)**는 도시 간 거리, 항공료 등을 모델링한다(방향이 있을 수도 있다 - 댈러스→토론토 $138, 토론토→댈러스 $216). 구현은 인접 "배열"을 인접 "해시 테이블"(정점 → 가중치)로 바꾸면 된다:

```typescript
class City {
  routes = new Map<City, number>();
  constructor(public name: string) {}

  addRoute(city: City, price: number): void {
    this.routes.set(city, price);
  }
}
```

**최단 경로 문제(Shortest Path Problem)**: 애틀랜타에서 엘패소로 가는 직항이 없을 때, 경유를 허용하면 경로마다 비용이 다르다 - 최소 비용 경로를 찾는 알고리즘은?

## 4. 데이크스트라의 알고리즘

1959년 에츠허르 데이크스트라가 고안한 최단 경로 알고리즘. 뜻밖의 이득: 끝나면 **시작 도시에서 "모든" 알려진 도시로 가는 최소 비용**을 얻는다.

두 개의 표(해시 테이블)를 유지한다:

- `cheapestPricesTable`: 시작 도시 → 각 도시의 현재까지 최소 비용 (시작 도시 자신은 0)
- `cheapestPreviousStopoverCityTable`: 각 도시로 최소 비용으로 가기 위한 **직전 경유 도시**

알고리즘:

1. 시작 도시를 방문해 "현재 도시"로
2. 현재 도시의 각 인접 도시에 대해, **시작 도시→현재 도시 최소 비용 + 현재 도시→인접 도시 비용**을 계산
3. 그 값이 표의 기존 값보다 싸면(또는 표에 없으면) 두 표를 갱신
4. **미방문 도시 중 시작 도시에서 가장 싸게 갈 수 있는 도시**를 다음 현재 도시로
5. 알려진 도시를 모두 방문할 때까지 반복

항공료 예제의 백미는 12단계: 애틀랜타→엘패소 최소 비용이 300달러(덴버 경유)로 기록돼 있었지만, 시카고를 방문하면서 200+80=**280달러** 경로가 발견되어 표가 갱신된다 - "이미 아는 답"도 더 싼 경유지가 발견되면 갱신된다는 것이 알고리즘의 핵심 동학이다.

**경로 복원**: 최종 비용은 첫 표에 있지만 실제 경로는 둘째 표로 얻는다 - 목적지에서 직전 경유지를 따라 **거슬러 올라간** 뒤 뒤집는다: 엘패소←시카고←덴버←애틀랜타 → `애틀랜타 → 덴버 → 시카고 → 엘패소`.

```typescript
function dijkstraShortestPath(startingCity: City, finalDestination: City): string[] {
  const cheapestPricesTable: Record<string, number> = {};
  const cheapestPreviousStopoverCityTable: Record<string, string> = {};
  const unvisitedCities: City[] = [];              // (이상적으로는 우선순위 큐)
  const visitedCities: Record<string, boolean> = {};

  cheapestPricesTable[startingCity.name] = 0;
  let currentCity: City | undefined = startingCity;

  while (currentCity) {
    visitedCities[currentCity.name] = true;
    const index = unvisitedCities.indexOf(currentCity);
    if (index !== -1) {
      unvisitedCities.splice(index, 1);
    }

    for (const [adjacentCity, price] of currentCity.routes) {
      if (!visitedCities[adjacentCity.name]) {
        unvisitedCities.push(adjacentCity);        // 새 도시 "발견"
      }
      const priceThroughCurrentCity =
        cheapestPricesTable[currentCity.name] + price;

      if (
        cheapestPricesTable[adjacentCity.name] === undefined ||
        priceThroughCurrentCity < cheapestPricesTable[adjacentCity.name]
      ) {
        cheapestPricesTable[adjacentCity.name] = priceThroughCurrentCity;
        cheapestPreviousStopoverCityTable[adjacentCity.name] = currentCity.name;
      }
    }
    // 미방문 도시 중 시작 도시에서 가장 저렴한 도시로 이동
    currentCity = unvisitedCities.reduce<City | undefined>(
      (cheapest, city) =>
        !cheapest || cheapestPricesTable[city.name] < cheapestPricesTable[cheapest.name]
          ? city
          : cheapest,
      undefined,
    );
  }

  // 경로 복원: 목적지에서 거슬러 올라간 뒤 뒤집기
  const shortestPath: string[] = [];
  let currentCityName = finalDestination.name;
  while (currentCityName !== startingCity.name) {
    shortestPath.push(currentCityName);
    currentCityName = cheapestPreviousStopoverCityTable[currentCityName];
  }
  shortestPath.push(startingCity.name);
  return shortestPath.reverse();
}
```

**효율성**: 미방문 도시를 단순 배열로 두면 최악(모든 정점이 서로 연결) **O(V²)**. **우선순위 큐(힙, Ch16)**로 바꾸면 더 빠르다 - 데이크스트라에는 여러 변형이 있고 구현이 시간 복잡도를 좌우한다.

---

## 요약

- **그래프 = 관계의 자료 구조.** 트리는 "사이클 없음 + 전부 연결"인 특수한 그래프다
- 용어: 정점·간선·인접(이웃)·경로·연결 그래프·방향 그래프. 구현은 해시 테이블/인접 리스트로 - 이웃 조회 O(1)
- 탐색의 필수 장치: **방문 기록 해시 테이블** (사이클 대비)
- **DFS(재귀)** = 최대한 멀리 먼저 / **BFS(큐)** = 가까운 곳부터 나선형 - "가까이 vs 멀리"가 선택 기준
- 탐색 효율 = **O(V + E)** - 정점 수와 간선 수를 함께 세야 한다
- **가중 그래프** + **데이크스트라**: 두 표(최소 비용, 직전 경유지)를 갱신하며 항상 "가장 싼 미방문 도시"부터 방문 - 최단(최저 비용) 경로와 그 실제 경로까지 얻는다

## 연습 문제 (해답 예시)

1. **"nails" 브라우징 시 추천 제품은?** - nails의 인접 정점: **핀(pins), 망치(hammer), 바늘(needles)**.
2. **A부터 DFS 순회 순서(인접 정점은 알파벳순)** - A에서 가장 먼저 닿는 알파벳순 이웃으로 끝까지 파고들었다가 되돌아오는 순서. 예제 그래프 기준: A, B, E, J, F, O, C, G, K, D, H, L, M, I, N, P.
3. **A부터 BFS 순회 순서** - 레벨(거리)별로 퍼진다: A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P.
4. **BFS를 "값 찾기" 함수로 수정** - 디큐한 현재 정점이 찾는 값이면 반환하고, 인접 정점을 큐에 넣기 전에도 값을 비교해 일치하면 즉시 반환. 큐가 비면 null.
5. **비가중 그래프의 최단 경로(최소 정점 경유)** - BFS의 "가까운 것부터" 성질 + 데이크스트라의 "직전 경유지 표"를 결합한다: BFS로 순회하면서 각 정점을 처음 발견할 때 `previousVertexTable[인접] = 현재 정점`을 기록하고, 목적지에서 표를 거슬러 올라가 경로를 뒤집는다. BFS는 가까운 레벨부터 방문하므로 처음 도달한 경로가 곧 최단 경로다.

## 다른 챕터와의 관계

- **Ch8 (해시 테이블)**: 그래프 구현(O(1) 이웃 조회)·방문 기록·데이크스트라의 두 표까지, 그래프의 온갖 곳에 해시 테이블이 스며 있다
- **Ch9 (큐)·Ch10 (재귀)**: BFS는 큐, DFS는 재귀(호출 스택) - 두 순회 도구의 실전 대결장
- **Ch15 (트리)**: 트리 순회의 일반화가 그래프 탐색이다 (사이클 대비 방문 기록만 추가)
- **Ch16 (힙)**: 데이크스트라의 미방문 목록을 우선순위 큐로 바꾸면 성능이 올라간다
