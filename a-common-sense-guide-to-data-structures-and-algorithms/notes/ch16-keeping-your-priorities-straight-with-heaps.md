# Chapter 16: Keeping Your Priorities Straight with Heaps (힙으로 우선순위 유지하기)

## 핵심 질문

"항상 최댓값(최우선순위)에 즉시 접근"해야 하는 우선순위 큐를 어떻게 빠르게 구현하는가? 완벽히 정렬하지 않는 "약한 정렬"이 왜 오히려 장점이 되는가? 트리를 배열에 담으면 어떤 문제가 풀리는가?

---

## 1. 우선순위 큐

**우선순위 큐(*priority queue - 삭제·접근은 앞에서만 하되, 삽입 시 항상 우선순위 순서를 유지하는 리스트*)**는 큐(FIFO)와 달리 도착 순서가 아니라 **우선순위**로 처리 순서를 정한다. 대표 예가 병원 응급실의 중증도 분류: 치명상 환자(중증도 10)는 감기 환자보다 늦게 와도 큐 맨 앞에 선다.

우선순위 큐도 추상 데이터 타입이다. 정렬된 배열로 구현하면(배열 끝을 큐의 앞으로 삼아):

- 삭제(배열 끝에서): **O(1)**
- 삽입(자리 찾기 + 시프트): **O(N)** ← 병목

삽입이 O(N)이면 항목이 많아질 때 지연이 생긴다. 더 나은 기반이 **힙**이다.

## 2. 힙의 두 조건

**이진 힙(*binary heap - 힙 조건을 만족하는 완전 이진 트리. 최대 힙과 최소 힙이 있다*)** (이하 최대 힙 기준):

1. **힙 조건(heap condition)**: 각 노드의 값은 **모든 자손보다 크다** (최소 힙은 반대 — 그 외 모든 면에서 동일)
2. **완전(complete) 트리**: 각 레벨이 왼쪽부터 빠짐없이 채워져 있다. 바닥 줄에는 빈 자리가 있을 수 있지만 **빈 자리 오른쪽에 노드가 있으면 안 된다**

BST와의 차이에 주의: BST는 "오른쪽 자식 > 노드"지만, 힙은 "노드 > 모든 자손"이다 — 서로 전혀 다른 조직이다.

## 3. 힙의 속성

- **약한 정렬(weakly ordered)**: 자손이 조상보다 클 수 없다는 질서는 있지만 **검색에는 무용**하다 — 값 3이 루트 100의 왼쪽에 있을지 오른쪽에 있을지 알 수 없다. 그래서 힙에는 보통 검색 연산을 구현하지 않는다
- **루트 = 항상 최댓값** (최소 힙은 최솟값) — 우선순위 큐의 "최우선 항목"에 정확히 대응
- **마지막 노드(last node)**: 바닥 레벨의 가장 오른쪽 노드 — 삽입·삭제 알고리즘의 열쇠

## 4. 힙 삽입 — 위로 트리클링

1. 새 값을 **마지막 노드 자리**(바닥 가장 오른쪽 다음 자리)에 넣는다 (완전성 유지!)
2. 새 노드를 부모와 비교해 **부모보다 크면 스왑**
3. 자신보다 큰 부모를 만날 때까지 반복 — 노드가 위로 **트리클링(trickling)**된다

효율: 트리의 레벨 수는 약 log N이므로 최악에 꼭대기까지 올라가도 **O(log N)**.

## 5. 힙 삭제 — 루트만, 아래로 트리클링

힙에서는 **루트 노드만 삭제**한다(우선순위 큐의 동작과 일치).

1. **마지막 노드를 루트 자리로** 옮긴다 (원래 루트는 삭제됨)
2. 힙 조건이 깨졌으므로 새 루트("트리클 노드")를 아래로 트리클링한다:
   - 두 자식 중 **더 큰 쪽**과 비교해, 트리클 노드가 작으면 스왑
   - 자신보다 큰 자식이 없을 때까지 반복

> **핵심 통찰**: 반드시 **더 큰 자식과** 스왑해야 한다. 작은 자식과 스왑하면 그 작은 값이 다른 자식의 부모가 되면서 즉시 힙 조건이 깨진다.

삭제도 log N개 레벨을 내려가므로 **O(log N)**.

## 6. 힙 vs 정렬된 배열

| 연산 | 정렬된 배열 | 힙 |
|------|-------------|-----|
| 삽입 | O(N) — 느림 | O(log N) — 매우 빠름 |
| 삭제 | O(1) — 엄청나게 빠름 | O(log N) — 매우 빠름 |

> **핵심 통찰**: 우선순위 큐는 삽입과 삭제를 **거의 같은 비율**로 수행한다(들어온 환자는 모두 치료된다). 어느 하나가 느리면 전체가 느려지므로, "때로는 엄청 빠르고 때로는 느린" 정렬된 배열보다 **일관되게 매우 빠른** 힙이 낫다.

## 7. 마지막 노드 문제와 배열 구현

삽입·삭제 모두 "마지막 노드"에서 시작하는데, 링크 기반 트리에서 마지막 노드를 찾으려면 모든 노드를 뒤져야 한다 — **마지막 노드 문제**. 왜 하필 마지막 노드여야 하나? **완전성(균형)을 지키기 위해서**다. 아무 자리에나 삽입하거나 아무 노드로 루트를 대체하면 힙이 한쪽으로 기울고, 불균형 트리는 O(N)으로 퇴화한다. 균형이 곧 O(log N)의 전제다.

해법: **힙을 배열로 구현**한다. 루트를 인덱스 0에, 이후 레벨을 위→아래·왼쪽→오른쪽으로 훑으며 인덱스를 차례로 할당하면:

> **핵심 통찰**: **마지막 노드 = 항상 배열의 마지막 원소.** 마지막 노드 찾기가 O(1)이 되고, 삽입도 "배열 끝에 추가"로 끝난다. 이것이 힙을 배열로 구현하는 이유다.

부모·자식 이동은 링크 대신 **인덱스 공식**으로:

- 왼쪽 자식: `index * 2 + 1`
- 오른쪽 자식: `index * 2 + 2`
- 부모: `(index - 1) / 2` (정수 나눗셈)

```typescript
class Heap {
  private data: number[] = [];

  rootNode(): number | undefined {
    return this.data[0];
  }
  lastNode(): number | undefined {
    return this.data[this.data.length - 1];
  }
  private leftChildIndex(index: number): number {
    return index * 2 + 1;
  }
  private rightChildIndex(index: number): number {
    return index * 2 + 2;
  }
  private parentIndex(index: number): number {
    return Math.floor((index - 1) / 2);
  }

  insert(value: number): void {
    this.data.push(value);                    // 마지막 노드로 추가
    let newNodeIndex = this.data.length - 1;
    // 위로 트리클링: 루트가 아니면서 부모보다 큰 동안
    while (
      newNodeIndex > 0 &&
      this.data[newNodeIndex] > this.data[this.parentIndex(newNodeIndex)]
    ) {
      const parentIdx = this.parentIndex(newNodeIndex);
      [this.data[parentIdx], this.data[newNodeIndex]] =
        [this.data[newNodeIndex], this.data[parentIdx]];
      newNodeIndex = parentIdx;
    }
  }

  delete(): void {
    this.data[0] = this.data.pop()!;          // 마지막 노드를 루트에
    let trickleNodeIndex = 0;
    while (this.hasGreaterChild(trickleNodeIndex)) {
      const largerChildIndex = this.calculateLargerChildIndex(trickleNodeIndex);
      [this.data[trickleNodeIndex], this.data[largerChildIndex]] =
        [this.data[largerChildIndex], this.data[trickleNodeIndex]];
      trickleNodeIndex = largerChildIndex;
    }
  }

  private hasGreaterChild(index: number): boolean {
    return (
      (this.data[this.leftChildIndex(index)] !== undefined &&
        this.data[this.leftChildIndex(index)] > this.data[index]) ||
      (this.data[this.rightChildIndex(index)] !== undefined &&
        this.data[this.rightChildIndex(index)] > this.data[index])
    );
  }
  private calculateLargerChildIndex(index: number): number {
    if (this.data[this.rightChildIndex(index)] === undefined) {
      return this.leftChildIndex(index);
    }
    return this.data[this.rightChildIndex(index)] > this.data[this.leftChildIndex(index)]
      ? this.rightChildIndex(index)
      : this.leftChildIndex(index);
  }
}
```

(연결 리스트로도 힙을 구현할 수 있지만 배열 방식이 더 널리 쓰인다. 배열로 이진 트리를 구현하는 이 기법은 BST 등 어떤 이진 트리에도 쓸 수 있으며, 힙은 그 이점 — 마지막 노드 O(1) — 이 가장 뚜렷한 첫 사례다.)

## 8. 우선순위 큐로 쓰이는 힙

가장 높은 우선순위 항목이 항상 루트에 있어 즉시 접근되고, 처리(삭제)하면 다음 순위가 자동으로 꼭대기로 올라온다. 삽입·삭제 모두 O(log N).

> **핵심 통찰**: **힙의 약한 정렬이 오히려 장점이다.** 완벽히 정렬하지 않기에 삽입이 O(log N)으로 빠르고, 그러면서도 "항상 필요한 그 값(최댓값)"에는 언제든 접근할 수 있을 만큼은 정렬되어 있다. 필요한 만큼만 질서를 유지하는 설계다.

---

## 요약

- **우선순위 큐** = 앞에서만 접근·삭제 + 삽입 시 순서 유지. 정렬된 배열 구현은 삽입 O(N)이 병목
- **힙** = 힙 조건(노드 > 모든 자손) + 완전 트리. 루트가 항상 최댓값, 검색에는 부적합(약한 정렬)
- **삽입**: 마지막 노드로 넣고 위로 트리클링 — O(log N) / **삭제**: 루트를 마지막 노드로 덮고 아래로(더 큰 자식과) 트리클링 — O(log N)
- 완전성 유지 = 균형 유지 = O(log N)의 전제 → **마지막 노드**가 삽입·삭제의 기준점
- **배열 구현**이 마지막 노드 문제를 해결: 마지막 노드 = 배열 끝, 자식 = `2i+1`/`2i+2`, 부모 = `(i−1)/2`
- 삽입·삭제가 균형 있게 일어나는 우선순위 큐에는 "일관되게 매우 빠른" 힙이 최적

## 연습 문제 (해답 예시)

1. **힙 [10, 9, 4, 2, 1, 3]에 11 삽입** — 11이 마지막 노드(4의 자식)로 들어간 뒤 4와 스왑, 다시 10과 스왑되어 **루트가 11**이 된다 (11이 루트, 그 아래 9와 10, 바닥에 2, 1, 3, 4).
2. **1번 힙에서 루트 삭제** — 마지막 노드 4가 루트로 올라간 뒤 더 큰 자식 10과 스왑되며 내려간다 → 루트 10, 그 아래 9와 4.
3. **55, 22, 34, 10, 2, 99, 68을 삽입한 힙에서 하나씩 팝하면?** — 힙은 팝할 때마다 최댓값을 내놓으므로 **내림차순**: 99, 68, 55, 34, 22, 10, 2. (이것이 힙 정렬의 원리이기도 하다)

## 다른 챕터와의 관계

- **Ch9 (스택과 큐)**: 큐에 "우선순위" 규칙을 더한 추상 데이터 타입이 우선순위 큐 — 그 최적 구현체가 힙
- **Ch15 (이진 탐색 트리)**: 같은 이진 트리라도 규칙(BST: 좌<우 정렬 / 힙: 부모>자손)이 다르면 특기가 다르다 — 검색 vs 최댓값 접근
- **Ch14 (노드 기반 자료 구조)**: 트리를 링크가 아닌 **배열**로 구현하는 대안을 처음 보여준 장
- **Ch18 (그래프)**: 데이크스트라 알고리즘의 성능 개선에 우선순위 큐(힙)가 쓰인다
