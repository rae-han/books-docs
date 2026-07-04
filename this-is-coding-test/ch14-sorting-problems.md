# Chapter 14: 정렬 기출문제

> Ch 06에서 배운 정렬 유형의 기출문제 모음(Q23~Q26). **다중 기준 정렬**, **중앙값**, **실패율 계산 후 정렬**, **최소 힙 그리디**가 핵심이다.

## 핵심 질문

- 여러 정렬 기준을 비교 함수 하나에 어떻게 우선순위대로 담는가?
- "거리의 합 최소"가 왜 **중앙값**인가?
- 합치는 비용 최소화는 왜 **최소 힙**(매번 가장 작은 둘)인가?

---

## Q23 국영수

| 항목 | 값 |
|------|-----|
| 난이도 | ★★ 중하 |
| 기출 | 백준 10825 |

### 문제 요약

학생들을 ① 국어 ↓ ② 영어 ↑ ③ 수학 ↓ ④ 이름 ↑(사전순) 기준으로 정렬해 이름 출력.

### 핵심 아이디어

비교 함수에서 **기준을 우선순위 순으로** `||`로 연결한다. 내림차순은 `b - a`, 오름차순은 `a - b`, 문자열은 `<`/`>` 비교(JS 문자열 비교는 UTF-16 = 아스키 순이라 대문자 우선).

```ts
interface Student {
  name: string;
  korean: number;
  english: number;
  math: number;
}

function solve(input: string): string {
  const lines = input.split("\n");
  const n = Number(lines[0]);
  const students: Student[] = lines.slice(1, 1 + n).map((line) => {
    const [name, k, e, m] = line.split(" ");
    return { name, korean: Number(k), english: Number(e), math: Number(m) };
  });

  students.sort((a, b) => {
    if (a.korean !== b.korean) {
      return b.korean - a.korean; // 국어 내림
    }
    if (a.english !== b.english) {
      return a.english - b.english; // 영어 오름
    }
    if (a.math !== b.math) {
      return b.math - a.math; // 수학 내림
    }
    return a.name < b.name ? -1 : a.name > b.name ? 1 : 0; // 이름 오름
  });

  return students.map((s) => s.name).join("\n");
}
```

> **핵심 통찰**: 다중 기준 정렬은 **비교 함수 하나에 `if`로 단계적으로** 담는 게 정석이다. 각 기준에서 같으면 다음 기준으로 넘어간다. 파이썬은 `key=lambda x: (-x[1], x[2], -x[3], x[0])` 튜플로 하지만, TS는 비교 함수가 직관적이다.

## Q24 안테나

| 항목 | 값 |
|------|-----|
| 난이도 | ★ 하 |
| 기출 | 2019 SW마에스트로 입학테스트 |

### 문제 요약

일직선 위 집들로부터 **거리 합이 최소**가 되는 위치(집 위치 중)를 구하라. 여러 개면 가장 작은 값.

예: `[1,5,7,9]` → `5`

### 핵심 아이디어

"모든 점까지 거리 합 최소"는 **중앙값**이다. 정렬 후 가운데 값(짝수면 작은 쪽 = 인덱스 `(N-1)/2`)을 고른다.

```ts
function antenna(positions: number[]): number {
  const sorted = [...positions].sort((a, b) => a - b);
  return sorted[Math.floor((sorted.length - 1) / 2)]; // 중앙값(작은 쪽)
}
console.log(antenna([1, 5, 7, 9])); // 5
```

> **핵심 통찰**: 1차원에서 거리 합(`Σ|x − p|`)을 최소화하는 p는 **중앙값**이라는 것은 잘 알려진 성질이다. 정렬만 하면 O(N log N)에 끝난다.

## Q25 실패율

| 항목 | 값 |
|------|-----|
| 난이도 | ★★ 중하 |
| 기출 | 2019 카카오 신입공채 1차 |

### 문제 요약

각 스테이지의 실패율(= 도달했으나 못 깬 수 / 도달한 수)을 구해, **실패율 내림차순**(같으면 번호 오름차순)으로 스테이지 번호를 반환.

예: N=5, `stages=[2,1,2,6,2,4,3,3]` → `[3,4,2,1,5]`

### 핵심 아이디어

스테이지별 도달자 수를 센 뒤, 남은 인원(`remaining`)을 줄여 가며 실패율을 계산하고 정렬한다.

```ts
function failureRate(N: number, stages: number[]): number[] {
  const reached = new Array(N + 2).fill(0);
  for (const s of stages) {
    reached[s]++;
  }
  const rates: [number, number][] = [];
  let remaining = stages.length;
  for (let i = 1; i <= N; i++) {
    const rate = remaining > 0 ? reached[i] / remaining : 0; // 도달자 0이면 실패율 0
    rates.push([i, rate]);
    remaining -= reached[i];
  }
  rates.sort((a, b) => b[1] - a[1] || a[0] - b[0]); // 실패율 내림, 같으면 번호 오름
  return rates.map((r) => r[0]);
}
console.log(failureRate(5, [2, 1, 2, 6, 2, 4, 3, 3])); // [3,4,2,1,5]
```

## Q26 카드 정렬하기

| 항목 | 값 |
|------|-----|
| 난이도 | ★★ 중하 |
| 기출 | 백준 1715 |

### 문제 요약

정렬된 카드 묶음들을 두 개씩 합칠 때(비용 = 두 묶음 합), 전체 **최소 비교 횟수**를 구하라.

예: `[10,20,40]` → `100`

### 핵심 아이디어

매번 **가장 작은 두 묶음**을 합치는 게 최적(허프만 코딩과 동일한 그리디). **최소 힙**으로 가장 작은 둘을 꺼내 합치고, 합을 다시 넣으며 비용을 누적한다.

```ts
// MinHeap은 Ch 09에서 정의한 클래스를 재사용한다.
function mergeCards(cards: number[]): number {
  const heap = new MinHeap<number>((a, b) => a - b);
  for (const c of cards) {
    heap.push(c);
  }
  let result = 0;
  while (heap.size > 1) {
    const a = heap.pop()!;
    const b = heap.pop()!;
    const sum = a + b;
    result += sum;
    heap.push(sum);
  }
  return result;
}
console.log(mergeCards([10, 20, 40])); // 100  (10+20=30, 30+40=70)
```

> **핵심 통찰**: "합치는 비용 = 크기의 합"이고 **여러 번 합쳐질수록 비용이 누적**되므로, 작은 묶음일수록 일찍(여러 번) 합쳐지게 해야 한다 → 매번 최소 둘을 합치는 그리디. 이는 Ch 09의 다익스트라처럼 **최소 힙**이 핵심 도구다.

---

## 요약

- **국영수**: 다중 기준은 비교 함수에 **우선순위 순으로 `if` 단계** (내림 `b-a`, 오름 `a-b`, 문자열 `<`/`>`).
- **안테나**: 거리 합 최소 = **중앙값**, 정렬 후 가운데.
- **실패율**: 도달자 수를 세며 `remaining`을 줄여 실패율 계산 → 내림차순 정렬.
- **카드 정렬하기**: 매번 가장 작은 둘을 합치는 **최소 힙 그리디**(허프만).
- 정렬 기출의 핵심은 **무엇을 키로 정렬하느냐**를 정확히 파악하는 것이다(Ch 06).
