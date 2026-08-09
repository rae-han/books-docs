# Chapter 14: Node-Based Data Structures (노드 기반 자료 구조)

## 핵심 질문

메모리 곳곳에 흩어진 데이터 조각들이 어떻게 하나의 리스트가 되는가? 배열과 겉모습이 같은 연결 리스트가 언제, 왜 배열을 압도하는가? 링크를 하나 더 달면(이중 연결) 무엇이 가능해지는가?

---

## 1. 연결 리스트와 노드

**노드(*node - 컴퓨터 메모리 곳곳에 흩어져 있을 수 있는 데이터 조각*)**는 이후 여러 장(트리·그래프)의 토대 개념이다. 그 가장 단순한 형태가 **연결 리스트(*linked list - 각 노드가 데이터와 함께 다음 노드의 주소(링크)를 갖는 리스트*)**다.

배열은 **연속된** 메모리 셀 블록이 필요하고 인덱스는 "시작 주소 + n"으로 즉시 계산된다(Ch1). 반면 연결 리스트의 노드들은 메모리 어디든 흩어질 수 있다 - 그렇다면 어떤 노드들이 같은 리스트인지 어떻게 알까? **각 노드가 다음 노드의 메모리 주소, 즉 링크(link)를 함께 저장**하기 때문이다. 각 노드는 셀 2개(데이터 + 링크)를 쓰고, 마지막 노드(테일)의 링크는 null이다. 첫 노드는 헤드라 부른다.

데이터가 흩어져도 된다는 점은 그 자체로 장점이다 - 배열처럼 커다란 연속 블록을 찾을 필요가 없다.

```typescript
class Node<T> {
  nextNode: Node<T> | null = null;
  constructor(public data: T) {}
}

class LinkedList<T> {
  constructor(public firstNode: Node<T> | null = null) {}
}
```

`LinkedList` 인스턴스의 역할은 **첫 번째 노드를 추적하는 것뿐**이다. 여기서 결정적인 사실: **연결 리스트는 첫 번째 노드에만 즉시 접근할 수 있다.**

## 2. 4대 연산 분석

### 2.1 읽기 - O(N)

세 번째 노드를 읽으려면 첫 노드에서 링크를 두 번 따라가야 한다. 어떤 노드든 **항상 첫 노드부터 사슬을 따라가야** 하므로 마지막 노드 읽기는 N단계 - **최악 O(N)**. 배열의 O(1)에 비해 심각한 약점이다.

```typescript
read(index: number): T | null {
  let currentNode = this.firstNode;
  let currentIndex = 0;
  while (currentIndex < index) {
    currentNode = currentNode?.nextNode ?? null;
    currentIndex++;
    if (!currentNode) {
      return null;  // 리스트 끝을 지나침
    }
  }
  return currentNode!.data;
}
```

### 2.2 검색 - O(N)

첫 노드부터 링크를 따라가며 값을 대조 - 배열의 선형 검색과 같은 **O(N)**.

### 2.3 삽입 - 앞에서는 O(1)

연결 리스트가 빛나는 순간이다. 배열은 **앞에 삽입**할 때 전체를 시프트해야 해서 최악 O(N)이지만, 연결 리스트는 **새 노드를 만들어 그 링크가 기존 첫 노드를 가리키게** 하면 끝 - **O(1)**. 데이터 시프트가 전혀 없다.

중간 삽입은? 삽입 자체는 1단계(앞 노드의 링크만 바꿈)지만 **그 앞 노드까지 가는 데** O(N)이 든다. 따라서 끝 삽입이 최악(N+1단계)이다.

| 시나리오 | 배열 | 연결 리스트 |
|----------|------|-------------|
| 앞에 삽입 | 최악 (O(N)) | 최선 (O(1)) |
| 중간에 삽입 | 평균 | 평균 |
| 끝에 삽입 | 최선 (O(1)) | 최악 (O(N)) |

> **핵심 통찰**: **배열과 연결 리스트의 최선·최악 시나리오는 정확히 정반대다.** 배열은 끝이, 연결 리스트는 앞이 유리하다.

```typescript
insertAtIndex(index: number, value: T): void {
  const newNode = new Node(value);
  if (index === 0) {                       // 앞 삽입: O(1)
    newNode.nextNode = this.firstNode;
    this.firstNode = newNode;
    return;
  }
  let currentNode = this.firstNode!;       // 그 외: 앞 노드까지 이동
  for (let i = 0; i < index - 1; i++) {
    currentNode = currentNode.nextNode!;
  }
  newNode.nextNode = currentNode.nextNode;
  currentNode.nextNode = newNode;
}
```

### 2.4 삭제 - 역시 앞에서는 O(1)

첫 노드 삭제는 `firstNode`를 두 번째 노드로 바꾸면 끝(O(1)). 중간 삭제는 앞 노드의 링크가 **삭제 대상 다음 노드를 가리키게** 바꾼다(`currentNode.nextNode = currentNode.nextNode.nextNode`). 삭제된 노드는 메모리에 남지만 리스트와의 연결이 끊겨 실질적으로 제거된다(언어에 따라 가비지 컬렉션이 회수).

삭제 시나리오 표는 삽입과 동일하다(앞=최선, 끝=최악 - 배열과 정반대).

## 3. 연결 리스트 연산 효율 총괄

| 연산 | 배열 | 연결 리스트 |
|------|------|-------------|
| 읽기 | O(1) | O(N) |
| 검색 | O(N) | O(N) |
| 삽입 | O(N) (끝이면 O(1)) | O(N) (앞이면 O(1)) |
| 삭제 | O(N) (끝이면 O(1)) | O(N) (앞이면 O(1)) |

표만 보면 매력이 없다. 연결 리스트의 진가는 **"실제 삽입·삭제 단계가 O(1)"**이라는 점을 활용할 수 있는, 즉 **이미 해당 노드에 접근해 있는** 시나리오에서 나온다.

## 4. 연결 리스트가 빛나는 곳 - 순회하며 삭제

이메일 주소 1,000개를 검토해 유효하지 않은 주소(약 100개)를 전부 삭제하는 애플리케이션:

- **배열**: 읽기 1,000단계 + 삭제할 때마다 뒤 원소 전체 시프트 → 삭제에만 추가 약 **100,000단계**
- **연결 리스트**: 읽기 1,000단계 + 삭제는 링크 변경 1단계씩 → 총 **1,100단계**

> **핵심 통찰**: **전체 리스트를 훑으며 여러 개를 삽입/삭제하는 작업**에는 연결 리스트가 압도적이다. 순회 중이므로 "노드까지 가는 비용"은 이미 지불했고, 남는 것은 O(1) 삭제뿐이기 때문이다.

## 5. 이중 연결 리스트

**이중 연결 리스트(*doubly linked list - 각 노드가 다음 노드와 앞 노드로의 링크 2개를 갖고, 리스트가 첫·마지막 노드를 모두 추적하는 변형*)**:

```typescript
class DoublyNode<T> {
  nextNode: DoublyNode<T> | null = null;
  previousNode: DoublyNode<T> | null = null;
  constructor(public data: T) {}
}

class DoublyLinkedList<T> {
  firstNode: DoublyNode<T> | null = null;
  lastNode: DoublyNode<T> | null = null;

  insertAtEnd(value: T): void {
    const newNode = new DoublyNode(value);
    if (!this.firstNode) {          // 빈 리스트
      this.firstNode = newNode;
      this.lastNode = newNode;
    } else {
      newNode.previousNode = this.lastNode;
      this.lastNode!.nextNode = newNode;
      this.lastNode = newNode;
    }
  }

  removeFromFront(): DoublyNode<T> {
    const removedNode = this.firstNode!;
    this.firstNode = this.firstNode!.nextNode;
    return removedNode;
  }
}
```

첫·마지막 노드에 모두 O(1) 접근이 가능하므로 **양 끝에서의 읽기·삽입·삭제가 전부 O(1)**이다. 또 링크가 양방향이라 **앞뒤 어느 방향으로도 이동**할 수 있다(마지막 노드에서 처음으로 거슬러 오르기도 가능).

## 6. 이중 연결 리스트 기반 큐

큐(Ch9)는 끝에서 삽입하고 앞에서 삭제한다. 배열 기반 큐는 끝 삽입 O(1) + **앞 삭제 O(N)**이 발목을 잡지만, 이중 연결 리스트는 **둘 다 O(1)** - 큐의 완벽한 내부 자료 구조다:

```typescript
class Queue<T> {
  private data = new DoublyLinkedList<T>();

  enqueue(element: T): void {
    this.data.insertAtEnd(element);       // O(1)
  }
  dequeue(): T {
    return this.data.removeFromFront().data;  // O(1)
  }
  read(): T | null {
    return this.data.firstNode?.data ?? null;
  }
}
```

추상 데이터 타입(큐)의 내부 구현을 배열에서 이중 연결 리스트로 갈아끼워 성능을 올린 것 - Ch9에서 말한 "스택/큐는 내부 구조를 가리지 않는다"의 실증이다.

---

## 요약

- **노드 = 흩어진 데이터 + 링크.** 연결 리스트는 첫 노드만 즉시 접근 가능하며, 이후는 링크 사슬을 따른다
- 읽기 O(N)·검색 O(N)으로 배열보다 불리하지만, **실제 삽입·삭제 단계는 O(1)** (앞에서는 접근까지 O(1))
- 배열과 연결 리스트는 최선/최악이 **정반대**: 배열=끝 유리, 연결 리스트=앞 유리
- 킬러 유스케이스: **순회하며 다수 삽입/삭제** - 시프트 비용이 없어 배열 대비 압도적
- **이중 연결 리스트**: 링크 2개 + 첫/마지막 추적 → 양 끝 연산 전부 O(1), 양방향 이동 - **큐의 이상적 내부 구조**
- 노드 개념은 다음 장들(트리·힙·트라이·그래프)의 공통 토대다

## 연습 문제 (해답 예시)

1. **모든 원소 출력 메서드** - 첫 노드부터 `currentNode = currentNode.nextNode`로 순회하며 data를 출력, null이면 종료.
2. **이중 연결 리스트를 거꾸로 출력** - `lastNode`에서 시작해 `previousNode` 링크를 따라가며 출력한다.
3. **마지막 원소 반환(길이 모름)** - 첫 노드부터 `nextNode`가 null인 노드까지 따라가서 그 data를 반환.
4. **리스트 뒤집기** - 세 포인터(previous, current, next)를 유지하며 순회: 각 노드에서 `current.nextNode = previous`로 링크 방향을 뒤집고 세 포인터를 한 칸씩 전진, 끝나면 `firstNode = previous`.
5. **리스트 접근 없이 중간 노드 삭제** - 그 노드를 직접 지울 수는 없지만, **다음 노드의 데이터를 현재 노드에 복사**하고 현재 노드의 링크가 다음다음 노드를 가리키게 하면(`node.data = node.nextNode.data; node.nextNode = node.nextNode.nextNode`) 실질적으로 삭제된다.

## 다른 챕터와의 관계

- **Ch1 (배열)**: "연속 메모리 + 주소 계산"의 배열과 정확히 대칭을 이루는 설계
- **Ch9 (스택과 큐)**: 큐의 내부 구조가 배열→이중 연결 리스트로 업그레이드됐다
- **Ch15 (이진 탐색 트리)**: 노드에 링크를 2개(왼쪽·오른쪽 자식) 달면 트리가 된다
- **Ch17·Ch18 (트라이·그래프)**: 링크 수를 임의로 늘린 노드 구조의 연장선
