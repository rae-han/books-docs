# Chapter 13: Recursive Algorithms for Speed (속도를 높이는 재귀 알고리즘)

## 핵심 질문

프로그래밍 언어들이 내장 정렬로 채택한 퀵 정렬은 어떻게 동작하는가? "분할"이라는 한 번의 작업이 어떻게 재귀와 만나 O(N log N)을 만드는가? 정렬하지 않고도 "두 번째로 작은 값"을 찾는 방법은?

---

## 1. 왜 퀵 정렬인가

실무에서는 버블·선택·삽입 정렬을 직접 쓰지 않는다 — 대부분의 언어에 내장 정렬 함수가 있고, 그 내부가 흔히 **퀵 정렬(Quicksort)**이다. 그럼에도 퀵 정렬을 공부하는 이유는 **재귀로 알고리즘 속도를 크게 올리는 법**을 배울 수 있어서다. 퀵 정렬은 최악(역순 배열)에서는 삽입·선택 정렬과 비슷하지만, 대부분 일어나는 **평균 시나리오에서 훨씬 빠르다**.

## 2. 분할(Partitioning)

**분할(*partition - 임의의 수(피벗)를 기준으로 작은 값은 왼쪽, 큰 값은 오른쪽에 두는 작업*)**의 절차 (피벗은 항상 처리 범위의 가장 오른쪽 값으로 선택):

1. **왼쪽 포인터**를 오른쪽으로 옮기다 피벗보다 크거나 같은 값에서 멈춘다
2. **오른쪽 포인터**를 왼쪽으로 옮기다 피벗보다 작거나 같은 값(또는 배열 맨 앞)에서 멈춘다
3. 왼쪽 포인터가 오른쪽 포인터에 도달/추월했으면 4단계로, 아니면 **두 포인터의 값을 교환**하고 1~3 반복
4. 왼쪽 포인터의 값과 **피벗을 교환**한다

분할이 끝나면 배열이 다 정렬되진 않았어도 **피벗 자신은 최종 위치에 있고**, 왼쪽은 전부 피벗보다 작고 오른쪽은 전부 크다. `[0, 5, 2, 1, 6, 3]`(피벗 3)을 분할하면 5↔1 교환을 거쳐 `[0, 1, 2, 3, 6, 5]`가 된다.

```typescript
class SortableArray {
  constructor(public array: number[]) {}

  partition(leftPointer: number, rightPointer: number): number {
    const pivotIndex = rightPointer;          // 가장 오른쪽 값이 피벗
    const pivot = this.array[pivotIndex];
    rightPointer -= 1;                         // 피벗 바로 왼쪽에서 시작

    while (true) {
      while (this.array[leftPointer] < pivot) {
        leftPointer += 1;
      }
      while (this.array[rightPointer] > pivot) {
        rightPointer -= 1;
      }
      if (leftPointer >= rightPointer) {
        break;
      }
      [this.array[leftPointer], this.array[rightPointer]] =
        [this.array[rightPointer], this.array[leftPointer]];
      leftPointer += 1;
    }
    // 왼쪽 포인터 위치와 피벗 교환 — 피벗이 최종 위치로
    [this.array[leftPointer], this.array[pivotIndex]] =
      [this.array[pivotIndex], this.array[leftPointer]];
    return leftPointer;  // 피벗의 최종 인덱스 반환
  }
}
```

## 3. 퀵 정렬 = 분할 + 재귀

1. 배열을 분할한다 → 피벗이 제자리를 찾는다
2. 피벗의 왼쪽·오른쪽 하위 배열을 **각각 또 하나의 배열로 보고** 재귀적으로 1~2를 반복한다
3. 하위 배열의 원소가 0개 또는 1개면 기저 조건 — 아무것도 하지 않는다

```typescript
quicksort(leftIndex: number, rightIndex: number): void {
  // 기저 조건: 원소 0~1개
  if (rightIndex - leftIndex <= 0) {
    return;
  }
  const pivotIndex = this.partition(leftIndex, rightIndex);
  this.quicksort(leftIndex, pivotIndex - 1);   // 피벗 왼쪽
  this.quicksort(pivotIndex + 1, rightIndex);  // 피벗 오른쪽
}
```

놀랍도록 간결하다 — "왼쪽·오른쪽은 재귀에 맡긴다"는 Ch11의 하향식 사고 그 자체다.

## 4. 퀵 정렬의 효율성 — O(N log N)

**한 번의 분할**: 모든 원소를 피벗과 비교(N번) + 평균 N/4번 교환 ≈ 1.25N → **O(N)**.

**전체**: 피벗이 대략 가운데 놓인다고 가정하면(평균), 분할할 때마다 배열이 절반 크기의 하위 배열 둘로 나뉜다. 크기 1이 될 때까지 반으로 나누는 횟수는 **log N**이고, 각 "층"에서 분할되는 원소 수를 전부 합치면 N이다(모든 하위 배열은 원래 배열의 조각이므로).

> **핵심 통찰**: **퀵 정렬 ≈ (층수 log N) × (층마다 N단계) = O(N log N).** 처음 배우는 카테고리로, 그래프에서 O(N)보다 약간 위, O(N²)보다 한참 아래에 있다. 원소 8개 ≈ 24단계, 16개 ≈ 64단계, 32개 ≈ 160단계.

## 5. 최악의 시나리오 — O(N²)

퀵 정렬의 최선은 "이미 정렬된 배열"이 아니라 **분할마다 피벗이 하위 배열 한가운데 놓일 때**다(값이 잘 섞여 있을 때 흔히 일어난다). 최악은 **피벗이 항상 한쪽 끝에 놓일 때** — 배열이 완전히 오름차순/내림차순일 때다. 이때는 분할이 배열을 반으로 나누지 못하고 크기가 1씩만 줄어든 하위 배열이 이어져, 비교 횟수가 N + (N−1) + … + 1 ≈ N²/2 → **O(N²)**.

| 시나리오 | 삽입 정렬 | 퀵 정렬 |
|----------|-----------|---------|
| 최선 | O(N) | O(N log N) |
| 평균 | O(N²) | O(N log N) |
| 최악 | O(N²) | O(N²) |

**평균에서의 압도적 우위**(O(N²) vs O(N log N)) 때문에 많은 언어가 내장 정렬을 퀵 정렬로 구현한다 — Ch6의 "평균 시나리오가 중요하다"는 교훈의 완성형이다.

## 6. 퀵 셀렉트 — 정렬 없이 K번째 값 찾기

무작위 배열에서 "열 번째로 작은 값"이나 중앙값을 찾고 싶다(정렬 자체는 불필요). 전체를 정렬하면 O(N log N)이지만, **퀵 셀렉트(*Quickselect - 분할을 반복하되 찾는 값이 있는 쪽 절반만 파고드는 알고리즘. 퀵 정렬과 이진 검색의 하이브리드*)**는 더 빠르다.

원리: 분할하면 피벗이 최종 위치에 놓이므로 "피벗은 X번째로 작은 값"임을 알게 된다. 찾는 K번째가 피벗보다 왼쪽이면 **왼쪽 하위 배열만** 다시 분할한다 — 이진 검색처럼 절반을 버린다.

```typescript
quickselect(kthLowestValue: number, leftIndex: number, rightIndex: number): number {
  // 기저 조건: 셀이 하나면 그것이 찾는 값
  if (rightIndex - leftIndex <= 0) {
    return this.array[leftIndex];
  }
  const pivotIndex = this.partition(leftIndex, rightIndex);
  if (kthLowestValue < pivotIndex) {
    return this.quickselect(kthLowestValue, leftIndex, pivotIndex - 1);
  } else if (kthLowestValue > pivotIndex) {
    return this.quickselect(kthLowestValue, pivotIndex + 1, rightIndex);
  } else {
    return this.array[pivotIndex];  // 피벗이 정확히 K번째
  }
}
```

**효율성**: N + N/2 + N/4 + … ≈ **2N → O(N)** (평균). 퀵 정렬은 매 층에서 N개 전부를 분할하지만, 퀵 셀렉트는 필요한 절반만 분할하기 때문이다.

## 7. 다른 알고리즘의 핵심 역할을 하는 정렬

알려진 가장 빠른 정렬은 O(N log N)이다(퀵 정렬 외에 **병합 정렬** 등). 이 사실이 중요한 이유는 **정렬을 부품으로 쓰는 알고리즘의 기준선**이 되기 때문이다.

예: 중복 검사(Ch4). O(N) 해법은 메모리를 더 쓰므로 제외한다면, O(N²) 중첩 루프 대신 — **먼저 정렬하면 중복 값이 이웃하게 되므로** 한 번의 순회로 "현재 값 == 다음 값"만 확인하면 된다:

```typescript
function hasDuplicateValue(array: number[]): boolean {
  array.sort((a, b) => a - b);   // O(N log N)
  for (let i = 0; i < array.length - 1; i++) {
    if (array[i] === array[i + 1]) {
      return true;
    }
  }
  return false;
}
```

(N log N) + N → 최고 차수만 남겨 **O(N log N)**. "정렬 먼저"는 O(N²)을 O(N log N)으로 끌어내리는 범용 전략이며, 정렬을 쓰는 알고리즘의 하한은 항상 O(N log N)이 기준이다.

---

## 요약

- **분할**: 피벗 기준 작은 값/큰 값을 양쪽으로 나누고 피벗을 최종 위치에 — 1회 O(N)
- **퀵 정렬 = 분할 + 좌우 재귀.** 평균 **O(N log N)** (log N층 × 층당 N단계), 최악(정렬/역순 배열) O(N²)
- 삽입 정렬 대비 **평균 시나리오의 우위**가 퀵 정렬을 표준 내장 정렬로 만들었다
- **퀵 셀렉트**: 분할 후 필요한 절반만 파고들어 K번째 값을 **평균 O(N)**에 찾는다 — 정렬 없이
- **"정렬 먼저" 전략**: 정렬(O(N log N))을 부품으로 쓰면 많은 O(N²) 문제가 O(N log N)으로 내려온다

## 연습 문제 (해답 예시)

1. **세 수의 최대곱을 O(N log N)으로** — 배열을 오름차순 정렬한 뒤 마지막 세 수를 곱한다: `array.sort((a, b) => a - b)` 후 `array[n-1] * array[n-2] * array[n-3]` (양수 배열 전제).
2. **빠진 숫자 찾기를 O(N log N)으로** — 정렬한 뒤 한 번 순회하며 `array[i] !== i`인 첫 인덱스 i를 반환한다 (0부터 이어져야 할 자리가 어긋난 지점이 빠진 수).
3. **최댓값 찾기를 세 가지 속도로** —
   - O(N²): 각 원소마다 "나보다 큰 값이 있는지" 전체를 다시 확인
   - O(N log N): 정렬 후 마지막 원소 반환
   - O(N): "지금까지의 최댓값" 하나만 유지하며 한 번 순회 (Ch4 해답과 동일)

## 다른 챕터와의 관계

- **Ch4~6 (단순 정렬 3부작)**: O(N²) 정렬들의 후계자 — 시나리오 분석(Ch6)이 퀵 정렬 채택의 논리다
- **Ch2 (이진 검색)**: "절반 버리기"가 퀵 셀렉트에서 분할과 결합됐다
- **Ch10·11 (재귀)**: 퀵 정렬은 하향식 재귀("좌우는 재귀에 맡긴다")의 대표 실전 사례
- **Ch16 (힙)·Ch19**: O(N log N) 기준선은 힙 연산 분석과 시간-공간 트레이드오프 논의에서 계속 쓰인다
