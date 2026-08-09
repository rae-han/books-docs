# Chapter 10: Set (집합)

## 핵심 질문

상호 배타적 집합(Disjoint Set)은 어떻게 표현하며, 두 원소가 같은 집합에 속하는지 어떻게 빠르게 판별하는가? 유니온-파인드(Union-Find) 알고리즘은 어떻게 동작하고, 어떤 문제에서 떠올려야 하는가?

## 1. 집합의 개념

집합은 **순서와 중복이 없는 원소들**을 갖는 자료구조다. `{1, 6, 6, 4, 3}`은 집합으로 보면 `{1, 6, 4, 3}`이고 `{6, 1, 3, 4}`와도 같다.

### 상호 배타적 집합 (Disjoint Set)

이 챕터에서 다루는 "집합"은 **상호 배타적 집합**, 즉 **교집합이 없는 집합 관계**다.

```
집합 A = {1, 2, 3}
집합 B = {4, 5, 6}        ← 상호 배타적 (A ∩ B = ∅)

집합 A = {1, 2, 5}
집합 B = {4, 5, 6}        ← 상호 배타적 X (5가 양쪽에)
```

### 상호 배타적 집합의 활용 분야

- **그래프 사이클 탐지**: 그래프 알고리즘에서 가장 많이 쓰이는 용도.
- **최소 신장 트리(MST)**: 크루스칼 알고리즘에서 간선 추가 시 사이클 형성 여부 체크.
- **이미지 분할**: 사람과 배경을 겹치지 않게 분할.
- **클러스터링**: 작업 간 의존 관계 그룹화.

> **핵심 통찰**: "두 원소가 같은 그룹인지 빠르게 판단", "여러 원소를 그룹으로 묶기"가 단서가 보이면 유니온-파인드를 떠올려라. 특히 **그래프의 사이클 검출**에 자주 쓰인다.

## 2. 집합의 연산

집합은 **배열을 활용한 트리**로 표현한다. 각 집합에는 **루트 노드(대표 원소)** 가 있다.

### 배열 기반 트리 표현

규칙:
- **배열의 인덱스 = 노드 자신**
- **배열의 값 = 부모 노드**
- **루트 노드는 자기 자신을 부모로 가짐** (`parent[root] === root`)

```
집합 A:                    배열 표현 (parent[]):
       1                   인덱스: 1 2 3 4 5 6 7 8 9
      / \                  값:    1 1 1 - 2 - 1 - 3
     2   7                 (인덱스 4, 6, 8은 다른 집합)
    / \
   3   5
   |
   9

집합 A의 모든 원소: 1, 2, 3, 5, 7, 9
원소 9에서 1까지: 9 → 3 → 2 → 1 (루트)
```

### 파인드(Find) 연산

특정 노드가 속한 집합의 **루트 노드**를 찾는다. 두 노드의 루트가 같으면 같은 집합.

```javascript
function find(parent, x) {
  if (parent[x] === x) return x; // 자기 자신이 루트
  return find(parent, parent[x]);
}
```

**문제**: 트리가 길게 늘어지면 최악 O(N).

### 경로 압축 (Path Compression)

파인드 시 거쳐 간 모든 노드를 직접 루트에 연결.

```javascript
function find(parent, x) {
  if (parent[x] === x) return x;
  parent[x] = find(parent, parent[x]); // 경로 압축
  return parent[x];
}
```

```
경로 압축 전:        경로 압축 후:
   1                   1
   |                  /|\
   2                 2 3 4
   |
   3
   |
   4

find(4) 한 번 호출 후 모든 노드가 루트에 직접 연결됨.
```

> **핵심 통찰**: 파인드 한 번 호출하면 그 경로의 모든 노드가 루트로 직접 연결된다. 다음 파인드 호출은 O(1).

### 유니온(Union) 연산

두 집합을 합친다 = 두 집합의 루트 노드를 같게 만든다.

```javascript
function union(parent, x, y) {
  const rootX = find(parent, x);
  const rootY = find(parent, y);
  if (rootX !== rootY) {
    parent[rootY] = rootX; // 한쪽 루트를 다른 쪽 루트의 자식으로
  }
}
```

### 랭크 기반 유니온 (Union by Rank)

랭크 = 트리의 높이. 항상 **랭크가 작은 트리를 큰 트리 아래에** 붙여 트리가 한쪽으로 치우치지 않게 한다.

```javascript
function union(parent, rank, x, y) {
  const rootX = find(parent, x);
  const rootY = find(parent, y);
  if (rootX === rootY) return;

  if (rank[rootX] < rank[rootY]) {
    parent[rootX] = rootY;
  } else if (rank[rootX] > rank[rootY]) {
    parent[rootY] = rootX;
  } else {
    parent[rootY] = rootX;
    rank[rootX] += 1; // 같으면 한쪽 랭크 증가
  }
}
```

**경로 압축 + 랭크 기반 유니온**을 같이 쓰면 거의 O(1) (정확히는 역 아커만 함수 α(N) ≈ 상수)에 동작한다.

## 3. 핵심 코드 패턴

### 유니온-파인드 표준 구현

```javascript
class UnionFind {
  constructor(n) {
    this.parent = Array.from({ length: n }, (_, i) => i);
    this.rank = new Array(n).fill(0);
  }

  find(x) {
    if (this.parent[x] === x) return x;
    this.parent[x] = this.find(this.parent[x]); // 경로 압축
    return this.parent[x];
  }

  union(x, y) {
    const rootX = this.find(x);
    const rootY = this.find(y);
    if (rootX === rootY) return false;

    if (this.rank[rootX] < this.rank[rootY]) {
      this.parent[rootX] = rootY;
    } else if (this.rank[rootX] > this.rank[rootY]) {
      this.parent[rootY] = rootX;
    } else {
      this.parent[rootY] = rootX;
      this.rank[rootX] += 1;
    }
    return true; // 합쳤음
  }

  isConnected(x, y) {
    return this.find(x) === this.find(y);
  }
}
```

### Set 객체로 중복 제거

```javascript
const unique = new Set(arr);
const uniqueArray = [...new Set(arr)];
```

### 사이클 검출 (그래프)

```javascript
const uf = new UnionFind(n);
for (const [u, v] of edges) {
  if (uf.isConnected(u, v)) {
    return true; // 사이클 발견
  }
  uf.union(u, v);
}
return false;
```

### 크루스칼 알고리즘 (최소 신장 트리)

```javascript
edges.sort((a, b) => a[2] - b[2]); // 비용 오름차순
const uf = new UnionFind(n);
let totalCost = 0;
let edgeCount = 0;

for (const [u, v, cost] of edges) {
  if (uf.union(u, v)) {
    totalCost += cost;
    edgeCount += 1;
    if (edgeCount === n - 1) break; // MST 완성
  }
}
```

## 4. JavaScript 빌트인 메서드 레퍼런스

| 도구 | 활용 |
|------|------|
| `new Set(arr)` | 중복 제거 |
| `set.has(x)` | 포함 여부 |
| `set.add(x)` / `set.delete(x)` | 추가/삭제 |
| `set.size` | 원소 개수 |
| `[...set]` | 배열 변환 |
| 클래스 `UnionFind` | 직접 구현 (외워두면 좋음) |

## 5. 몸풀기 문제

### 문제 33: 간단한 유니온-파인드 알고리즘 구현하기

> `operations` 배열의 명령(`['u', x, y]` 또는 `['f', x]`)을 처리한 후 집합의 개수를 반환.
> 권장 시간 복잡도: O(N)

```javascript
function find(parents, x) {
  if (parents[x] === x) return x;
  parents[x] = find(parents, parents[x]);
  return parents[x];
}

function union(parents, x, y) {
  const rootX = find(parents, x);
  const rootY = find(parents, y);
  parents[rootY] = rootX;
}

function solution(k, operations) {
  const parents = Array.from({ length: k }, (_, i) => i);

  for (const op of operations) {
    if (op[0] === "u") {
      union(parents, op[1], op[2]);
    } else if (op[0] === "f") {
      find(parents, op[1]);
    }
  }

  // 모든 노드의 루트를 찾아 고유한 루트의 개수 = 집합 개수
  const roots = new Set();
  for (let i = 0; i < k; i++) {
    roots.add(find(parents, i));
  }
  return roots.size;
}
```

> **핵심 통찰**: 집합의 개수는 **고유한 루트 노드의 개수**다. 모든 노드를 파인드해서 Set에 모으면 자연스럽게 집합 수가 나온다.

**시간 복잡도**: O((N + K) × α(N)) ≈ O(N + K)

## 6. 합격자가 되는 모의테스트

### 문제 34: 폰켓몬 — 프로그래머스

> N마리 폰켓몬에서 N/2마리를 골라 가질 수 있는 종류 수의 최댓값을 반환.
> [프로그래머스 #1845](https://programmers.co.kr/learn/courses/30/lessons/1845)

**접근 아이디어**: 종류 수와 N/2 중 작은 값. `Set`으로 중복 제거.

```javascript
function solution(nums) {
  const numSet = new Set(nums);
  const k = nums.length / 2;
  return Math.min(k, numSet.size);
}
```

**시간 복잡도**: O(N)

### 문제 35: 영어 끝말잇기 — 프로그래머스

> N명이 끝말잇기. 단어를 들어온 순서대로 받고, 첫 탈락자의 [번호, 차례]를 반환. 탈락자가 없으면 `[0, 0]`.
> [프로그래머스 #12981](https://programmers.co.kr/learn/courses/30/lessons/12981)

**탈락 조건**:
- 이미 사용한 단어
- 첫 글자가 이전 단어의 마지막 글자와 다름

**번호/차례 계산**:
- 번호 = `(인덱스 % N) + 1`
- 차례 = `Math.floor(인덱스 / N) + 1`

```javascript
function solution(n, words) {
  const usedWords = new Set();
  let prevWord = words[0][0]; // 첫 단어의 첫 글자

  for (let i = 0; i < words.length; i++) {
    const word = words[i];
    if (usedWords.has(word) || word[0] !== prevWord) {
      return [(i % n) + 1, Math.floor(i / n) + 1];
    }
    usedWords.add(word);
    prevWord = word.slice(-1);
  }

  return [0, 0];
}
```

> **핵심 통찰**: "이전 단어의 마지막 글자"를 매번 단어 끝에서 추출하면 O(1). `slice(-1)`이나 `word[word.length - 1]`이 표준 패턴.

**시간 복잡도**: O(N)

### 문제 36: 전화번호 목록 — 프로그래머스

> 전화번호부에서 한 번호가 다른 번호의 접두사면 false, 아니면 true.
> [프로그래머스 #42577](https://school.programmers.co.kr/learn/courses/30/lessons/42577)

**접근 아이디어**: 정렬 후 인접한 두 번호만 비교하면 된다. 정렬하면 한 번호의 접두사는 그 번호 바로 앞에 위치한다.

```javascript
function solution(phone_book) {
  phone_book.sort();
  for (let i = 0; i < phone_book.length - 1; i++) {
    if (phone_book[i + 1].startsWith(phone_book[i])) {
      return false;
    }
  }
  return true;
}
```

> **핵심 통찰**: 사전 순 정렬을 활용하면 O(N²) 비교가 O(N log N) 정렬 + O(N) 인접 비교로 줄어든다. **"정렬 후 인접만 비교"** 는 자주 쓰이는 패턴.

> **함정**: "있다"라는 한글에 끌려 `true`를 반환하지 말 것. 문제는 **접두사가 없으면 true**이다.

**시간 복잡도**: O(N log N)

### 문제 37: 섬 연결하기 — 프로그래머스 (최소 신장 트리)

> N개의 섬과 다리 비용 `costs`가 주어진다. 모든 섬을 연결하는 최소 비용을 반환.
> [프로그래머스 #42861](https://school.programmers.co.kr/learn/courses/30/lessons/42861)

**접근 아이디어**: **크루스칼 알고리즘**. 비용 오름차순으로 간선을 정렬하고, 사이클을 만들지 않는 간선만 추가. 사이클 검출은 유니온-파인드.

**알고리즘**:
1. 간선을 비용 오름차순으로 정렬.
2. 가장 작은 비용 간선부터 시도.
3. 두 끝점이 다른 집합이면 합치고 비용 누적, 같은 집합이면 사이클이므로 스킵.
4. N-1개의 간선이 추가되면 종료.

```javascript
function find(parent, x) {
  if (parent[x] === x) return x;
  parent[x] = find(parent, parent[x]);
  return parent[x];
}

function union(parent, rank, x, y) {
  const rootX = find(parent, x);
  const rootY = find(parent, y);
  if (rank[rootX] < rank[rootY]) {
    parent[rootX] = rootY;
  } else if (rank[rootX] > rank[rootY]) {
    parent[rootY] = rootX;
  } else {
    parent[rootY] = rootX;
    rank[rootX] += 1;
  }
}

function solution(n, costs) {
  costs.sort((a, b) => a[2] - b[2]);
  const parent = Array.from({ length: n }, (_, i) => i);
  const rank = new Array(n).fill(0);

  let minCost = 0;
  let edges = 0;

  for (const [u, v, cost] of costs) {
    if (edges === n - 1) break;

    const rootU = find(parent, u);
    const rootV = find(parent, v);

    if (rootU !== rootV) {
      union(parent, rank, u, v);
      minCost += cost;
      edges += 1;
    }
  }

  return minCost;
}
```

> **핵심 통찰**: 크루스칼은 그리디 + 유니온-파인드의 결합이다. **"최소 비용으로 모든 노드를 연결"** 키워드면 MST를 떠올리고, 사이클 검출에 유니온-파인드를 쓴다.

> **합격 조언**: 다른 MST 알고리즘으로 **프림(Prim)** 도 있다. 정점 기반(우선순위 큐)이라 밀집 그래프에서 유리. 크루스칼은 간선 기반이라 희소 그래프에서 유리.

**시간 복잡도**: O(E log E) — E는 간선 수.

## 7. 함정/실수 노트

| 함정 | 설명 |
|------|------|
| `parent[x] = find(...)` 누락 | 경로 압축이 안 되어 매 호출 O(N) |
| 같은 집합인데 union | `find(x) === find(y)` 체크 후 합칠 것 (사이클 검출에서 활용) |
| 랭크 vs 사이즈 | 랭크는 트리 높이, 사이즈는 노드 개수. 둘 다 가능하지만 일관되게 사용 |
| 0 인덱스 vs 1 인덱스 | parent 배열 초기화 시 일관성 유지 |
| MST에서 N-1 간선 종료 | `edges === n - 1`이면 멈춰야 효율적 |
| `phone_book` 정렬 후 비교 | 인접 비교만으로 충분 — O(N²) 풀이는 시간 초과 |
| 접두사 vs 부분 문자열 | `startsWith`는 접두사. `includes`는 부분 문자열 |
| `Set`에 객체 저장 | 참조 비교 — 좌표는 문자열 직렬화 |

## 8. 요약

- **상호 배타적 집합**은 교집합이 없는 집합. 그래프 사이클 검출의 핵심 도구.
- **유니온-파인드**는 두 연산으로 구성: 같은 집합 여부(find), 두 집합 합치기(union).
- **경로 압축** + **랭크 기반 유니온**으로 거의 O(1) (α(N))에 동작.
- **자바스크립트의 `Set`** 은 중복 제거에 자연스럽게 활용.
- **크루스칼 알고리즘**(MST)은 정렬 + 유니온-파인드의 조합. "최소 비용으로 모두 연결" 패턴.
- **정렬 후 인접 비교**는 O(N²) → O(N log N) 패턴 (전화번호 접두사 등).
- 집합 개수는 **고유한 루트의 개수**.

## 리마인드 (저자)

1. 집합 간 교집합이 없는 집합 관계를 상호 배타적 집합이라고 한다.
2. 상호 배타적 집합은 배열을 활용한 트리로 표현하며 각 집합의 루트 노드는 자기 자신이다.
3. 상호 배타적 집합에는 루트 노드를 찾아주는 파인드 연산, 두 집합을 합치는 유니온 연산이 있다.
4. 집합을 효율적으로 구현하려면 경로 압축과 랭크를 활용하면 된다.
