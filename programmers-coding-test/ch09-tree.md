# Chapter 09: Tree (트리)

## 핵심 질문

계층 구조를 표현하는 트리는 어떻게 정의되며, 이진 트리는 어떻게 표현하고 순회하는가? 이진 탐색 트리는 어떤 원리로 O(log N) 탐색을 가능하게 하는가?

## 1. 트리의 개념

트리(tree)는 계층 구조를 표현하는 자료구조로, 나무를 거꾸로 뒤집어 놓은 모양이다. 가장 위가 **루트 노드(root node)** 이고, 그 아래로 가지가 뻗어 나간다.

### 트리 용어

| 용어 | 의미 |
|------|------|
| **노드(node)** | 트리를 구성하는 요소 |
| **루트 노드(root node)** | 가장 위에 있는 노드 |
| **간선(edge)** | 노드와 노드를 잇는 단방향 선 |
| **부모/자식 노드** | 간선으로 연결된 두 노드 중 위쪽이 부모, 아래쪽이 자식 |
| **형제 노드(sibling)** | 같은 부모를 갖는 노드들 |
| **리프 노드(leaf node)** | 자식이 없는 말단 노드 |
| **차수(degree)** | 특정 노드에서 아래로 향하는 간선의 개수 |
| **레벨(level)** | 루트로부터 특정 노드까지 거치는 간선 수 (루트는 0) |
| **높이(height)** | 트리에서 가장 큰 레벨 값 |

### 트리의 활용 분야

- **파일 시스템**: 디렉터리 계층 구조.
- **인공지능**: 의사 결정 트리(decision tree).
- **자동 완성**: 트라이(trie) 구조로 접두사 검색.
- **데이터베이스**: B-트리, B+트리로 인덱싱.

> **합격 조언**: 코딩 테스트에서는 **이진 트리(binary tree)** 만 알면 충분하다. 이진 트리는 모든 노드의 차수가 2 이하인 트리다.

## 2. 이진 트리 표현하기

### 배열로 표현하기

루트 노드를 인덱스 1에 두고:
- 왼쪽 자식: `부모 인덱스 × 2`
- 오른쪽 자식: `부모 인덱스 × 2 + 1`

루트 노드를 인덱스 0에 두면:
- 왼쪽 자식: `부모 인덱스 × 2 + 1`
- 오른쪽 자식: `부모 인덱스 × 2 + 2`

```
       1
      / \
     2   3
    / \ / \
   4  5 6  7

배열: [_, 1, 2, 3, 4, 5, 6, 7]   (인덱스 1 시작)
또는: [1, 2, 3, 4, 5, 6, 7]      (인덱스 0 시작)
```

> **함정**: 자식이 없는 곳은 빈 슬롯으로 남아 메모리가 낭비된다. 다만 코딩 테스트 수준에서는 배열 표현이 구현이 단순해 자주 쓰인다.

### 포인터로 표현하기

```javascript
class Node {
  constructor(value) {
    this.value = value;
    this.left = null;
    this.right = null;
  }
}
```

메모리 낭비는 없지만 구현이 약간 더 복잡하다.

## 3. 이진 트리 순회 (Traversal)

### 세 가지 순회 방식

| 순회 | 방문 순서 | 활용 |
|------|----------|------|
| **전위(preorder)** | 부모 → 왼쪽 → 오른쪽 | 트리 복사, 직관적 출력 |
| **중위(inorder)** | 왼쪽 → 부모 → 오른쪽 | 이진 탐색 트리에서 정렬된 순서 |
| **후위(postorder)** | 왼쪽 → 오른쪽 → 부모 | 트리 삭제 (자식부터 삭제) |

### 알고리즘 트레이스 (전위 순회)

```
       1
      / \
     2   3
    / \ / \
   4  5 6  7

전위: 1 → 2 → 4 → 5 → 3 → 6 → 7
중위: 4 → 2 → 5 → 1 → 6 → 3 → 7
후위: 4 → 5 → 2 → 6 → 7 → 3 → 1
```

> **핵심 통찰**: 순회의 핵심 표현은 "**현재 노드를 부모 노드로 생각했을 때**"다. 재귀적으로 적용되며, 좌/우 서브트리에서도 같은 규칙이 작동한다.

## 4. 이진 탐색 트리 (BST)

이진 탐색 트리는 다음 규칙을 따르는 이진 트리다.

- 어떤 노드 V의 **왼쪽 서브트리** 모든 노드 값 < V 값
- V의 **오른쪽 서브트리** 모든 노드 값 ≥ V 값

이 성질 덕분에 탐색 시 한쪽 서브트리를 통째로 제외할 수 있어 **O(log N)** 탐색이 가능하다 (균형이 잡힌 경우).

### BST 삽입 알고리즘

```
3 → 4 → 2 → 8 → 9 → 7 → 1 순으로 삽입

3을 루트로
4 > 3 → 오른쪽
2 < 3 → 왼쪽
8 > 3, 8 > 4 → 4의 오른쪽
9 > 3, 9 > 4, 9 > 8 → 8의 오른쪽
7 > 3, 7 > 4, 7 < 8 → 8의 왼쪽
1 < 3, 1 < 2 → 2의 왼쪽
```

### 시간 복잡도

| 상황 | 시간 복잡도 |
|------|------------|
| 균형 이진 탐색 트리 | O(log N) |
| 균형이 깨진 경우 (한쪽으로 치우침) | O(N) |

> **합격 조언**: 균형을 자동으로 유지하는 트리(AVL, Red-Black)가 있지만 코딩 테스트에 직접 구현할 일은 거의 없다. 자바스크립트도 표준 라이브러리에 없다.

## 5. 핵심 코드 패턴

### 배열 트리 순회 (재귀)

```javascript
function preorder(nodes, idx) {
  if (idx >= nodes.length) return "";
  let ret = `${nodes[idx]} `;
  ret += preorder(nodes, idx * 2 + 1); // 0-base 시작
  ret += preorder(nodes, idx * 2 + 2);
  return ret;
}

function inorder(nodes, idx) {
  if (idx >= nodes.length) return "";
  let ret = inorder(nodes, idx * 2 + 1);
  ret += `${nodes[idx]} `;
  ret += inorder(nodes, idx * 2 + 2);
  return ret;
}

function postorder(nodes, idx) {
  if (idx >= nodes.length) return "";
  let ret = postorder(nodes, idx * 2 + 1);
  ret += postorder(nodes, idx * 2 + 2);
  ret += `${nodes[idx]} `;
  return ret;
}
```

### BST 클래스

```javascript
class Node {
  constructor(key) {
    this.left = null;
    this.right = null;
    this.val = key;
  }
}

class BST {
  constructor() {
    this.root = null;
  }

  insert(key) {
    if (!this.root) {
      this.root = new Node(key);
      return;
    }
    let curr = this.root;
    while (true) {
      if (key < curr.val) {
        if (curr.left) {
          curr = curr.left;
        } else {
          curr.left = new Node(key);
          return;
        }
      } else {
        if (curr.right) {
          curr = curr.right;
        } else {
          curr.right = new Node(key);
          return;
        }
      }
    }
  }

  search(key) {
    let curr = this.root;
    while (curr && curr.val !== key) {
      curr = key < curr.val ? curr.left : curr.right;
    }
    return curr;
  }
}
```

### 인접 리스트로 트리 구축 (edges 배열)

```javascript
function buildTree(n, edges) {
  const tree = Array.from({ length: n }, () => []);
  for (const [from, to] of edges) {
    tree[from].push(to);
  }
  return tree;
}
```

### 부모 매핑 (자식→부모 추적)

```javascript
const parent = {};
for (let i = 0; i < enroll.length; i++) {
  parent[enroll[i]] = referral[i];
}
```

### BFS로 트리 탐색 (최단 거리)

```javascript
const queue = [[start, 0]]; // [노드, 거리]
const visited = new Set([start]);

while (queue.length > 0) {
  const [cur, dist] = queue.shift();
  if (cur === target) return dist;
  for (const next of tree[cur]) {
    if (!visited.has(next)) {
      visited.add(next);
      queue.push([next, dist + 1]);
    }
  }
}
```

## 6. JavaScript 빌트인 메서드 레퍼런스

| 도구 | 활용 |
|------|------|
| `class Node` | 트리 노드 정의 |
| 재귀 함수 | 트리 순회의 자연스러운 구현 |
| `Array.from({length: n}, () => [])` | 인접 리스트 초기화 |
| `Math.ceil(n / 2)` | 토너먼트 다음 라운드 번호 |
| `new Set()` | 방문 체크 |

## 7. 몸풀기 문제

### 문제 26: 트리 순회

> 이진 트리를 표현한 배열 `nodes`(루트 인덱스 0)에 대해 전위/중위/후위 순회 결과를 반환.
> 권장 시간 복잡도: O(N)

```javascript
function preorder(nodes, idx) {
  if (idx >= nodes.length) return "";
  return `${nodes[idx]} ` +
    preorder(nodes, idx * 2 + 1) +
    preorder(nodes, idx * 2 + 2);
}

function inorder(nodes, idx) {
  if (idx >= nodes.length) return "";
  return inorder(nodes, idx * 2 + 1) +
    `${nodes[idx]} ` +
    inorder(nodes, idx * 2 + 2);
}

function postorder(nodes, idx) {
  if (idx >= nodes.length) return "";
  return postorder(nodes, idx * 2 + 1) +
    postorder(nodes, idx * 2 + 2) +
    `${nodes[idx]} `;
}

function solution(nodes) {
  return [
    preorder(nodes, 0).slice(0, -1),
    inorder(nodes, 0).slice(0, -1),
    postorder(nodes, 0).slice(0, -1),
  ];
}
```

> **함정**: 마지막에 공백이 붙으므로 `slice(0, -1)`로 제거.

**시간 복잡도**: O(N)

### 문제 27: 이진 탐색 트리 구현

> `lst`로 BST를 구축하고 `searchList`의 각 값이 트리에 있는지 boolean 배열로 반환.

```javascript
class Node {
  constructor(key) {
    this.left = null;
    this.right = null;
    this.val = key;
  }
}

class BST {
  constructor() {
    this.root = null;
  }

  insert(key) {
    const newNode = new Node(key);
    if (!this.root) {
      this.root = newNode;
      return;
    }
    let curr = this.root;
    while (true) {
      if (key < curr.val) {
        if (curr.left) curr = curr.left;
        else { curr.left = newNode; return; }
      } else {
        if (curr.right) curr = curr.right;
        else { curr.right = newNode; return; }
      }
    }
  }

  search(key) {
    let curr = this.root;
    while (curr && curr.val !== key) {
      curr = key < curr.val ? curr.left : curr.right;
    }
    return curr !== null;
  }
}

function solution(lst, searchList) {
  const bst = new BST();
  for (const key of lst) bst.insert(key);
  return searchList.map((v) => bst.search(v));
}
```

**시간 복잡도**: O(N²) 최악, O(N log N) 평균.

## 8. 합격자가 되는 모의테스트

### 문제 28: 예상 대진표 — 프로그래머스

> N명이 토너먼트로 경기. 참가자 A와 B가 몇 라운드에서 만나는지 반환.
> [프로그래머스 #12985](https://programmers.co.kr/learn/courses/30/lessons/12985)

**접근 아이디어**: 다음 라운드의 번호는 `Math.ceil(현재 / 2)`. A와 B의 다음 라운드 번호가 같아질 때까지 반복.

```javascript
function solution(n, a, b) {
  let answer = 0;
  while (a !== b) {
    a = Math.ceil(a / 2);
    b = Math.ceil(b / 2);
    answer += 1;
  }
  return answer;
}
```

> **핵심 통찰**: 토너먼트는 노드가 한 단계 위로 올라갈 때 두 명을 합쳐 하나로 만드는 트리 구조다. `(N+1)/2` 올림이 부모 인덱스가 된다.

> **함정**: `/ 2`가 아니라 `Math.ceil(/ 2)`. 자바스크립트 `/`는 부동소수점이라 의도한 번호 계산이 안 된다.

**시간 복잡도**: O(log N)

### 문제 29: 다단계 칫솔 판매 — 프로그래머스

> 추천인-피추천인 트리. 각 판매원이 칫솔을 팔면 수익의 10%를 추천인에게 분배(소수점 버림). 1원 미만이면 분배하지 않음. 각 판매원의 최종 수익을 반환.
> [프로그래머스 #77486](https://programmers.co.kr/learn/courses/30/lessons/77486)

**접근 아이디어**:
1. `parent[name] = referral` 매핑으로 자식→부모 추적.
2. 각 판매에 대해 판매원부터 부모를 따라 올라가며 10%씩 분배.

```javascript
function solution(enroll, referral, seller, amount) {
  const parent = {};
  for (let i = 0; i < enroll.length; i++) {
    parent[enroll[i]] = referral[i];
  }

  const total = {};
  for (const name of enroll) total[name] = 0;

  for (let i = 0; i < seller.length; i++) {
    let money = amount[i] * 100;
    let curName = seller[i];

    while (money > 0 && curName !== "-") {
      const distributed = Math.floor(money / 10);
      total[curName] += money - distributed;
      curName = parent[curName];
      money = distributed;
    }
  }

  return enroll.map((name) => total[name]);
}
```

> **함정**: `money - Math.floor(money / 10)`이 자기 몫. 부동소수점 오류를 피하려면 항상 `Math.floor`로 정수 처리.

> **핵심 통찰**: 트리를 `parent[]` 매핑만으로 표현하면 자식→부모 탐색이 O(1)이고, 트리 자체를 안 만들어도 된다. 부모만 알면 되는 경우 자주 쓰는 패턴.

**시간 복잡도**: O(N × M) — N=enroll, M=seller. 트리 깊이는 보통 작음.

### 문제 30: 미로 탈출 — 프로그래머스

> 격자 미로에서 시작점 → 레버 → 출구 순으로 이동하는 최소 시간. 레버를 당기지 않으면 출구로 나갈 수 없음.
> [프로그래머스 #159993](https://school.programmers.co.kr/learn/courses/30/lessons/159993)

**접근 아이디어**: 가중치 없는 격자 + 최단 거리 → **BFS**. 단, **레버 상태(0/1)** 를 좌표와 함께 관리해야 한다 (`visited[y][x][k]`).

```javascript
class Queue {
  items = []; front = 0; rear = 0;
  push(item) { this.items.push(item); this.rear++; }
  pop() { return this.items[this.front++]; }
  isEmpty() { return this.front === this.rear; }
}

function solution(maps) {
  const n = maps.length;
  const m = maps[0].length;
  const visited = Array.from({ length: n }, () =>
    Array.from({ length: m }, () => [false, false])
  );

  const dy = [-1, 1, 0, 0];
  const dx = [0, 0, -1, 1];
  const q = new Queue();
  let endY = -1, endX = -1;

  for (let i = 0; i < n; i++) {
    for (let j = 0; j < m; j++) {
      if (maps[i][j] === "S") {
        q.push([i, j, 0, 0]);
        visited[i][j][0] = true;
      }
      if (maps[i][j] === "E") {
        endY = i;
        endX = j;
      }
    }
  }

  while (!q.isEmpty()) {
    const [y, x, k, time] = q.pop();
    if (y === endY && x === endX && k === 1) return time;

    for (let i = 0; i < 4; i++) {
      const ny = y + dy[i];
      const nx = x + dx[i];

      if (
        ny < 0 || ny >= n || nx < 0 || nx >= m || maps[ny][nx] === "X"
      ) continue;

      const nk = maps[ny][nx] === "L" ? 1 : k;
      if (!visited[ny][nx][nk]) {
        visited[ny][nx][nk] = true;
        q.push([ny, nx, nk, time + 1]);
      }
    }
  }

  return -1;
}
```

> **핵심 통찰**: 단순 좌표만이 아니라 **상태(레버 0/1)** 도 visited의 차원이 된다. "같은 좌표라도 다른 상태로 도달하면 다른 경로"라는 점이 BFS 확장의 핵심.

> **함정**: 출구는 레버가 당겨진 상태(`k === 1`)에서만 종료. 그 전에는 통과만 함.

**시간 복잡도**: O(N × M × 2)

### 문제 31: 양과 늑대 — 2022 KAKAO BLIND (고난이도)

> 이진 트리의 각 노드에 양/늑대 정보. 루트부터 출발해 인접 노드를 방문하며 양과 늑대를 모은다. **늑대 ≥ 양이 되면 모든 양이 잡아먹힘**. 모을 수 있는 양의 최대 수.
> [프로그래머스 #92343](https://programmers.co.kr/learn/courses/30/lessons/92343)

**접근 아이디어**: BFS + 상태 공간 탐색. 상태 = (현재 노드, 양 수, 늑대 수, 다음 방문 가능한 노드 집합). 각 단계에서 가능한 모든 노드 선택을 분기로 시도.

```javascript
function solution(info, edges) {
  const tree = Array.from({ length: info.length }, () => []);
  for (const [from, to] of edges) {
    tree[from].push(to);
  }

  let maxSheep = 0;
  // [현재 노드, 양 수, 늑대 수, 방문 가능한 다음 노드 집합]
  const queue = [[0, 1, 0, new Set()]];

  while (queue.length > 0) {
    const [current, sheep, wolf, visitable] = queue.shift();
    maxSheep = Math.max(maxSheep, sheep);

    // 현재 노드의 자식들을 방문 가능 집합에 추가
    const newVisitable = new Set(visitable);
    for (const next of tree[current]) {
      newVisitable.add(next);
    }

    // 가능한 모든 다음 노드로 분기
    for (const next of newVisitable) {
      const nextVisitable = new Set(newVisitable);
      nextVisitable.delete(next);

      if (info[next] === 0) {
        // 양: 무조건 방문
        queue.push([next, sheep + 1, wolf, nextVisitable]);
      } else {
        // 늑대: 잡아먹히지 않을 때만 방문
        if (sheep > wolf + 1) {
          queue.push([next, sheep, wolf + 1, nextVisitable]);
        }
      }
    }
  }

  return maxSheep;
}
```

> **핵심 통찰**: 이런 게임 류 문제에서는 "현재 위치"만이 아니라 "**앞으로 갈 수 있는 모든 후보**"가 상태의 일부가 된다. Set으로 후보를 관리하며 분기.

> **함정**: 자식 노드를 추가할 때 새 Set을 만들어야 한다. 같은 Set을 공유하면 다른 분기의 정보가 섞인다.

**시간 복잡도**: O(2^N) — info 길이가 17 이하라 가능.

### 문제 32: 길 찾기 게임 — 2019 KAKAO BLIND (고난이도)

> 노드 좌표 `nodeinfo`로 BST를 구축. 규칙: 왼쪽 서브트리는 x값이 작고, 오른쪽 서브트리는 x값이 큼. 같은 레벨은 y값이 같고, 자식은 부모보다 y값이 작음. 전위/후위 순회 결과를 반환.
> [프로그래머스 #42892](https://programmers.co.kr/learn/courses/30/lessons/42892)

**접근 아이디어**:
1. y 내림차순, 같은 y면 x 오름차순으로 노드 정렬 → 첫 번째가 루트.
2. 정렬된 순서대로 BST에 삽입. x 좌표로 좌/우 결정.
3. 비재귀 순회 (스택 사용) — 자바스크립트 재귀 깊이 한계 회피.

```javascript
class Node {
  constructor(info, num) {
    this.info = info;
    this.num = num;
    this.left = null;
    this.right = null;
  }
}

function makeBT(nodeinfo) {
  const nodes = Array.from({ length: nodeinfo.length }, (_, i) => i + 1);
  nodes.sort((a, b) => {
    const [ax, ay] = nodeinfo[a - 1];
    const [bx, by] = nodeinfo[b - 1];
    return ay === by ? ax - bx : by - ay;
  });

  let root = null;
  for (const node of nodes) {
    const newNode = new Node(nodeinfo[node - 1], node);
    if (!root) {
      root = newNode;
      continue;
    }
    let parent = root;
    while (true) {
      if (newNode.info[0] < parent.info[0]) {
        if (parent.left) parent = parent.left;
        else { parent.left = newNode; break; }
      } else {
        if (parent.right) parent = parent.right;
        else { parent.right = newNode; break; }
      }
    }
  }
  return root;
}

function preOrder(root, answer) {
  const stack = [root];
  while (stack.length) {
    const node = stack.pop();
    if (!node) continue;
    answer[0].push(node.num);
    stack.push(node.right); // 스택이라 오른쪽 먼저
    stack.push(node.left);
  }
}

function postOrder(root, answer) {
  const stack = [[root, false]];
  while (stack.length) {
    const [node, visited] = stack.pop();
    if (!node) continue;
    if (visited) {
      answer[1].push(node.num);
    } else {
      stack.push([node, true]);
      stack.push([node.right, false]);
      stack.push([node.left, false]);
    }
  }
}

function solution(nodeinfo) {
  const answer = [[], []];
  const root = makeBT(nodeinfo);
  preOrder(root, answer);
  postOrder(root, answer);
  return answer;
}
```

> **합격 조언**: 자바스크립트는 재귀 깊이가 환경마다 다르지만 약 10,000으로 제한된다. 큰 트리에서는 **스택을 사용한 비재귀 순회**를 고려. 후위 순회는 "방문 표시(visited)" 플래그로 두 번째 방문 시 출력하는 패턴이 표준.

> **핵심 통찰**: y 내림차순 + x 오름차순 정렬은 **레벨별로 위에서 아래로, 같은 레벨에서 왼쪽에서 오른쪽**으로 노드를 처리하는 효과를 낸다. 이 순서로 BST에 삽입하면 자연스럽게 트리가 구성된다.

**시간 복잡도**: O(N²) 최악 (균형 안 잡힌 경우).

## 9. 함정/실수 노트

| 함정 | 설명 |
|------|------|
| 인덱스 0 vs 1 시작 | 자식 인덱스 계산이 달라짐 — 코드에 명시 |
| 후위 순회 비재귀 | "방문 표시" 플래그로 두 번째 방문 시 출력 |
| `Math.ceil(/ 2)` | 토너먼트나 BST 깊이 계산 시 정수 보장 필수 |
| BST 균형 | 입력 순서가 정렬되어 있으면 한쪽으로 치우쳐 O(N) |
| 트리 구축 시 부모 매핑 | 자식→부모 한 방향만 필요하면 단순 객체로 충분 |
| 재귀 깊이 한계 | 자바스크립트 ~10,000. 큰 트리는 스택 사용 |
| BFS의 상태 공간 | 좌표만이 아니라 추가 상태(레버, 키 등)도 visited 차원 |
| Set 공유 vs 복사 | 다른 분기로 갈 때는 `new Set([...visited])`로 복사 |

## 10. 요약

- **트리는 계층 구조의 자료구조**다. 노드, 간선, 부모-자식 관계로 구성된다.
- **이진 트리는 자식이 최대 2개**인 트리. 코딩 테스트의 표준.
- **표현은 배열 또는 포인터**. 배열은 메모리를 낭비하지만 구현이 단순.
- **순회는 전위/중위/후위** 세 종류. 재귀의 자연스러운 활용처.
- **이진 탐색 트리**는 좌측 < 부모 ≤ 우측 규칙으로 O(log N) 탐색을 가능하게 한다.
- **인접 리스트(`tree[from].push(to)`)** 로 임의의 트리를 표현할 수 있다.
- **BFS는 가중치 없는 트리/그래프의 최단 거리**에 표준.
- **상태 공간 탐색**은 좌표 외에 추가 상태(레버, 양/늑대 카운트 등)를 visited의 차원으로 추가.

## 리마인드 (저자)

1. 트리를 표현하는 방법은 배열로 표현하는 방법과 포인터로 표현하는 방법이 있다. 대부분 코딩 테스트에서는 배열로 표현하는 방법을 사용한다.
2. 트리를 순회하는 방법은 전위 순회(VLR), 중위 순회(LVR), 후위 순회(LRV)가 있다.
3. 이진 탐색 트리는 노드가 부모 노드보다 작으면 왼쪽, 부모 노드보다 크면 오른쪽에 위치시켜 탐색 효율을 높인 자료구조다.
