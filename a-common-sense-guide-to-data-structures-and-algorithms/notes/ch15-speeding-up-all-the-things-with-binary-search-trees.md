# Chapter 15: Speeding Up All the Things with Binary Search Trees (이진 탐색 트리로 속도 향상)

## 핵심 질문

정렬 순서를 유지하면서도 검색·삽입·삭제가 전부 빠른 자료 구조가 가능한가? 정렬된 배열(삽입 느림)과 해시 테이블(순서 없음)이 못 채우는 자리를 트리는 어떻게 채우는가?

---

## 1. 왜 이진 탐색 트리인가

데이터를 항상 정렬 상태로 유지하고 싶다면(정렬 알고리즘은 아무리 빨라도 O(N log N)이므로 매번 재정렬은 낭비):

- **정렬된 배열**: 읽기 O(1), 검색 O(log N)이지만 **삽입·삭제가 O(N)** — 시프트 비용
- **해시 테이블**: 검색·삽입·삭제 O(1)이지만 **순서가 없다**

**순서 유지 + 빠른 검색·삽입·삭제**를 모두 원할 때의 답이 이진 탐색 트리다.

## 2. 트리 용어

**트리(*tree - 각 노드가 여러 노드로의 링크를 가질 수 있는 노드 기반 자료 구조*)**의 용어:

- **루트(root)**: 가장 상위 노드 (그림에서 꼭대기)
- **부모(parent) / 자식(child)**: 직접 연결된 상하 관계. **조상(ancestor)/자손(descendant)**은 그 확장
- **레벨(level)**: 트리의 같은 줄. 루트가 첫 번째 레벨
- **균형(balanced) 트리**: 모든 노드에서 양쪽 하위 트리의 노드 개수가 같은 트리 — 한쪽이 더 많으면 **불균형(imbalanced)**

## 3. 이진 탐색 트리의 정의

- **이진 트리**: 각 노드의 자식이 0, 1, 2개
- **이진 탐색 트리(binary search tree, BST)**: 추가 규칙 — 자식은 왼쪽·오른쪽 최대 하나씩이며, **왼쪽 자손은 모두 그 노드보다 작고, 오른쪽 자손은 모두 크다**

```typescript
class TreeNode {
  constructor(
    public value: number,
    public leftChild: TreeNode | null = null,
    public rightChild: TreeNode | null = null,
  ) {}
}

const root = new TreeNode(50, new TreeNode(25), new TreeNode(75));
```

(루트에 "왼쪽 자식이 둘" 달려 있으면 이진 트리일 수는 있어도 이진 **탐색** 트리는 아니다.)

## 4. 검색 — O(log N)

알고리즘: 루트를 "현재 노드"로 → 값을 비교 → 찾는 값이 작으면 왼쪽 하위 트리로, 크면 오른쪽으로 → 찾거나 바닥에 닿을 때까지 반복.

> **핵심 통찰**: 왼쪽/오른쪽을 선택하는 순간 **반대쪽 하위 트리 전체가 검색에서 제외**된다 — 단계마다 남은 노드의 절반을 제거하는 O(log N) 패턴이다. 다른 관점: 균형 이진 트리는 **노드 N개에 레벨이 약 log N개**다(레벨을 하나 추가할 때마다 노드 수가 약 2배). 검색은 레벨을 하나씩 내려가므로 최대 log N단계다.

```typescript
function search(searchValue: number, node: TreeNode | null): TreeNode | null {
  // 기저 조건: 노드가 없거나(값이 트리에 없음) 찾는 값
  if (node === null || node.value === searchValue) {
    return node;
  } else if (searchValue < node.value) {
    return search(searchValue, node.leftChild);
  } else {
    return search(searchValue, node.rightChild);
  }
}
```

레벨이 무한할 수 있는 트리는 "임의 깊이" 구조이므로 재귀가 자연스럽다(Ch10).

## 5. 삽입 — O(log N), BST의 강점

새 값이 들어갈 자리를 검색(log N)한 뒤, 자식이 없는 지점에 1단계로 붙인다 — (log N)+1 → **O(log N)**.

```typescript
function insert(value: number, node: TreeNode): void {
  if (value < node.value) {
    if (node.leftChild === null) {
      node.leftChild = new TreeNode(value);  // 기저 조건: 빈 자리에 삽입
    } else {
      insert(value, node.leftChild);
    }
  } else if (value > node.value) {
    if (node.rightChild === null) {
      node.rightChild = new TreeNode(value);
    } else {
      insert(value, node.rightChild);
    }
  }
}
```

정렬된 배열은 검색 O(log N) + **시프트 O(N)**이 들지만 BST는 시프트가 없다. **검색과 삽입이 모두 O(log N)** — 변경이 잦은 애플리케이션에서 결정적이다.

### 5.1 삽입 순서와 균형

> **핵심 통찰**: **정렬된 데이터를 순서대로 삽입하면(1,2,3,4,5) 트리가 한 줄로 늘어져** 완전히 선형이 된다 — 검색 O(N). 같은 데이터를 3,2,4,1,5처럼 섞어 넣으면 균형 트리가 되어 O(log N)이다. 정렬된 배열을 BST로 바꿀 때는 **먼저 순서를 무작위로** 만드는 것이 좋다. 최악(심한 불균형) O(N), 최선(완전 균형) O(log N), 무작위 삽입의 일반적인 경우 ≈ O(log N).

## 6. 삭제 — 가장 까다로운 연산

삭제 알고리즘의 완전한 규칙:

1. **자식이 없는 노드**: 그냥 삭제
2. **자식이 하나**: 노드를 삭제하고 그 자식을 그 자리에 넣는다 (자식이 고아가 되지 않게)
3. **자식이 둘**: 삭제된 노드를 **후속자(successor) 노드** — 삭제된 값보다 큰 값 중 최솟값 — 로 대체한다
4. **후속자 찾기**: 삭제 노드의 오른쪽 자식으로 간 뒤, **왼쪽 자식이 없을 때까지 왼쪽으로만** 내려간 바닥 값
5. **후속자에게 오른쪽 자식이 있으면**: 후속자를 삭제 위치에 넣은 뒤, 후속자의 오른쪽 자식을 **후속자의 원래 부모의 왼쪽 자식**으로 넣는다

```typescript
function deleteNode(valueToDelete: number, node: TreeNode | null): TreeNode | null {
  if (node === null) {
    return null;                       // 기저 조건
  } else if (valueToDelete < node.value) {
    node.leftChild = deleteNode(valueToDelete, node.leftChild);
    return node;                       // 반환값이 부모의 자식 슬롯을 덮어씀
  } else if (valueToDelete > node.value) {
    node.rightChild = deleteNode(valueToDelete, node.rightChild);
    return node;
  } else {
    if (node.leftChild === null) {
      return node.rightChild;          // 오른쪽 자식(또는 null)이 그 자리를 대체
    } else if (node.rightChild === null) {
      return node.leftChild;
    } else {
      // 자식이 둘: lift가 후속자 값을 현재 노드에 복사한다
      node.rightChild = lift(node.rightChild, node);
      return node;
    }
  }
}

function lift(node: TreeNode, nodeToDelete: TreeNode): TreeNode | null {
  if (node.leftChild) {
    node.leftChild = lift(node.leftChild, nodeToDelete);
    return node;
  } else {
    nodeToDelete.value = node.value;   // 후속자 값을 삭제 위치에 복사
    return node.rightChild;            // 후속자의 오른쪽 자식이 부모의 왼쪽 자식이 됨
  }
}
```

이 코드의 요령은 **"재귀 호출의 반환값을 자식 슬롯에 덮어쓰기"**다 — 대부분의 호출은 자기 자신을 반환해 아무 변화가 없지만, 실제 삭제 지점에서는 대체 노드(또는 null)가 반환되어 트리가 연결을 유지한 채 재구성된다. 삭제 역시 검색 + 정리 단계로 **O(log N)** (정렬된 배열의 O(N) 삭제와 대조).

## 7. BST 활용 — 책 제목 리스트와 순회

책 제목을 알파벳순으로 유지·출력·검색하고 변경도 잦은 앱이라면(제목 수백만 개) BST가 적격이다. 그런데 "전체를 알파벳순으로 출력"은 어떻게 할까? — **순회(*traversal - 자료 구조의 모든 노드를 방문하는 과정*)**가 필요하다.

**중위 순회(inorder traversal)**가 오름차순 출력을 보장한다:

1. 왼쪽 자식에 재귀 호출
2. 노드를 "방문"(출력)
3. 오른쪽 자식에 재귀 호출

```typescript
function traverseAndPrint(node: TreeNode | null): void {
  if (node === null) {
    return;                        // 기저 조건
  }
  traverseAndPrint(node.leftChild);
  console.log(node.value);
  traverseAndPrint(node.rightChild);
}
```

"왼쪽 전부 → 자신 → 오른쪽 전부" 순서가 BST의 규칙(왼쪽<자신<오른쪽)과 정확히 맞물려 정렬 출력이 된다. 순회는 정의상 노드 N개를 모두 방문하므로 **O(N)**이다.

## 8. 연산 효율 정리

| 연산 | 정렬된 배열 | 해시 테이블 | BST (균형) |
|------|-------------|-------------|-----------|
| 검색 | O(log N) | O(1) | O(log N) |
| 삽입 | O(N) | O(1) | O(log N) |
| 삭제 | O(N) | O(1) | O(log N) |
| 순서 유지 | ✅ | ❌ | ✅ |

---

## 요약

- BST = 이진 트리 + **"왼쪽 자손 < 노드 < 오른쪽 자손"** 규칙 — 순서 유지와 O(log N) 연산을 동시에
- 검색 O(log N)의 두 관점: 단계마다 절반 제거 / 레벨 수 = log N
- **삽입도 O(log N)** (시프트 없음) — 정렬된 배열 대비 결정적 우위. 단 **정렬된 순서로 삽입하면 선형 트리(O(N))**가 되므로 무작위 삽입이 중요
- 삭제 규칙: 자식 0개=제거, 1개=자식 승격, 2개=**후속자**(오른쪽으로 한 번, 그다음 왼쪽 끝)로 대체 (+후속자의 오른쪽 자식 처리)
- **중위 순회**(왼쪽→자신→오른쪽)가 오름차순 출력을 만든다 — O(N)
- 선택 기준: 순서 불필요 → 해시 테이블 / 순서 필요 + 변경 잦음 → BST / 순서 필요 + 거의 안 바뀜 → 정렬된 배열

## 연습 문제 (해답 예시)

1. **[1, 5, 9, 2, 4, 10, 6, 3, 8]을 순서대로 삽입한 트리** — 루트 1, 오른쪽으로 5 (1<5), 5의 오른쪽에 9, 5의 왼쪽에 2, 2의 오른쪽에 4, 9의 오른쪽에 10, 9의 왼쪽에 6, 4의 왼쪽에 3, 6의 오른쪽에 8. (1이 루트가 되면서 왼쪽이 텅 빈 불균형 트리가 된다)
2. **값 1,000개의 균형 BST에서 최대 검색 단계는?** — **약 10단계.** log₂1000 ≈ 10.
3. **BST의 최댓값 찾기** — 오른쪽 자식이 없을 때까지 오른쪽으로만 내려간다:

   ```typescript
   function max(node: TreeNode): number {
     return node.rightChild ? max(node.rightChild) : node.value;
   }
   ```

4. **전위 순회(자신→왼쪽→오른쪽) 출력 순서** — Moby Dick, Great Expectations, Alice in Wonderland, Lord of the Flies, Robinson Crusoe, Pride and Prejudice, The Odyssey.
5. **후위 순회(왼쪽→오른쪽→자신) 출력 순서** — Alice in Wonderland, Lord of the Flies, Great Expectations, Pride and Prejudice, The Odyssey, Robinson Crusoe, Moby Dick.

## 다른 챕터와의 관계

- **Ch2 (이진 검색)**: "가운데에서 절반 제거"를 자료 구조 자체에 새긴 것이 BST — 검색 효율이 같다
- **Ch14 (노드 기반 자료 구조)**: 링크 1개(연결 리스트)에서 2개(왼쪽·오른쪽)로 늘린 노드 구조
- **Ch10 (재귀)**: 검색·삽입·삭제·순회 모두 재귀로 구현되는, 재귀의 실전 무대
- **Ch16 (힙)**: 같은 이진 트리 계열이지만 "정렬 유지" 대신 "최댓값 접근"에 특화된 트리가 나온다
