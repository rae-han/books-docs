# Chapter 07: Queue (큐)

## 핵심 질문

먼저 들어간 데이터를 먼저 꺼내는 선입선출(FIFO) 자료구조는 어떤 문제에 적합한가? 자바스크립트에 큐가 없는데 어떻게 구현하며, `shift()`로 흉내 내는 방식은 어떤 한계가 있는가?

## 1. 큐의 개념

큐(queue)는 "줄을 서다"라는 뜻이다. 먼저 들어간 데이터가 먼저 나오는 자료구조. 맛집에서 줄을 선 순서대로 입장하는 것과 같다.

**선입선출(FIFO, First In First Out)** 이라고 하며, 삽입 연산은 **푸시(push)**, 꺼내는 연산은 **팝(pop)** 이라고 한다.

### 동작 원리

```
빈 큐 → push(2) → push(5) → pop() → pop()

[ ]    [2]      [2, 5]    [5]    [ ]
       ↑ rear   ↑ front   ↑      
       front    rear      front=rear
                          
pop 결과: 2 → 5 (들어간 순서대로)
```

### 큐의 특성을 활용하는 분야

- **작업 대기열**: 서버에 들어오는 클라이언트 요청을 들어온 순서대로 처리.
- **이벤트 처리**: 키보드 입력, 마우스 움직임 등 발생 순서로 처리.
- **BFS 탐색**: 그래프 너비 우선 탐색의 핵심 자료구조.

> **핵심 통찰**: "들어온 순서대로 처리"라는 단서가 보이면 큐를 떠올려라. 스택과 정반대의 처리 순서이지만, 두 자료구조는 자주 함께 등장한다.

## 2. 큐의 ADT

| 구분 | 정의 | 설명 |
|------|------|------|
| 연산 | `boolean isFull()` | 큐가 가득 찼으면 true |
| | `boolean isEmpty()` | 큐가 비었으면 true |
| | `void push(item)` | 큐 뒤(rear)에 데이터를 추가 |
| | `Item pop()` | 큐 앞(front)의 데이터를 꺼내고 반환 |
| 상태 | `int front` | 가장 처음 팝 위치 |
| | `int rear` | 가장 최근 푸시 위치 |
| | `Item data[maxSize]` | 데이터를 관리하는 배열 |

스택과 다른 점은 `top` 하나가 아니라 `front`(앞)와 `rear`(뒤) 두 포인터를 사용한다는 것이다. 큐는 **앞에서 빼고 뒤에서 넣기** 때문이다.

### 선형 큐의 한계와 원형 큐

선형 큐는 `front`가 앞으로 이동하면서 그 앞쪽 메모리 공간을 활용하지 못한다. 이를 개선한 것이 **원형 큐**(circular queue) — `front`와 `rear`가 배열을 도는 방식.

> **합격 조언**: 자바스크립트는 배열의 길이를 자동으로 관리하므로 코딩 테스트에서는 원형 큐를 직접 구현할 필요가 거의 없다. 메모리가 빡빡한 임베디드 환경에서나 의미 있는 최적화다.

## 3. JavaScript에서의 큐 구현

자바스크립트는 표준 라이브러리에 큐가 없다. 세 가지 접근 방식이 있다.

### 방법 1: `shift()` 메서드로 흉내 내기

가장 간단하지만 **`shift()`는 O(N)** 이라는 치명적 단점이 있다. 데이터가 적으면 V8이 최적화해주지만, 큰 큐에서는 시간 초과 위험.

```javascript
const queue = [];
queue.push(1);
queue.push(2);
const first = queue.shift(); // 1, O(N)
```

### 방법 2: 배열 + 포인터로 직접 구현 — 권장

`front` 포인터를 증가시키기만 하고 실제로 배열에서 제거하지 않는 방식. 모든 연산 O(1).

```javascript
class Queue {
  items = [];
  front = 0;
  rear = 0;

  constructor(array = []) {
    this.items = [...array];
    this.rear = array.length;
  }

  push(item) {
    this.items.push(item);
    this.rear++;
  }

  pop() {
    return this.items[this.front++];
  }

  first() {
    return this.items[this.front];
  }

  size() {
    return this.rear - this.front;
  }

  isEmpty() {
    return this.front === this.rear;
  }
}
```

단점: `front`와 `rear`가 계속 증가해 메모리가 누적된다. 다만 코딩 테스트 수준에서는 문제 없음.

### 방법 3: 연결 리스트로 구현

메모리 효율은 가장 좋지만 구현 코드가 길다. 시간 압박이 있는 코딩 테스트에서는 방법 2를 선호.

```javascript
class Node {
  constructor(data) {
    this.data = data;
    this.next = null;
  }
}

class Queue {
  constructor() {
    this.head = null;
    this.tail = null;
    this.size = 0;
  }

  push(data) {
    const newNode = new Node(data);
    if (!this.head) {
      this.head = newNode;
      this.tail = newNode;
    } else {
      this.tail.next = newNode;
      this.tail = newNode;
    }
    this.size++;
  }

  pop() {
    if (!this.head) return null;
    const removed = this.head;
    this.head = this.head.next;
    if (!this.head) this.tail = null;
    this.size--;
    return removed.data;
  }

  isEmpty() {
    return this.size === 0;
  }
}
```

> **핵심 통찰**: 코딩 테스트에서는 **방법 2(배열 + front/rear 포인터)** 를 외워두는 게 가장 실용적이다. shift() 함정은 피하면서 구현이 짧다.

## 4. 핵심 코드 패턴

### 큐 빠르게 만들기 (방법 2 압축형)

```javascript
const queue = [];
let front = 0;

queue.push(item);          // push
const item = queue[front++]; // pop (단, length 체크 필요)
const isEmpty = front === queue.length;
```

### 회전 큐 패턴 (요세푸스 등)

```javascript
// k-1번 앞에서 빼서 뒤로 옮기고, k번째 원소를 제거
for (let i = 0; i < k - 1; i++) {
  queue.push(queue.pop());
}
queue.pop(); // k번째 제거
```

### BFS 패턴

```javascript
const queue = [start];
const visited = new Set([start]);

while (queue.length > 0) {
  const cur = queue.shift(); // 작은 데이터면 shift도 OK
  for (const next of neighbors(cur)) {
    if (!visited.has(next)) {
      visited.add(next);
      queue.push(next);
    }
  }
}
```

## 5. JavaScript 빌트인 메서드 레퍼런스

| 메서드/패턴 | 동작 | 시간 복잡도 |
|-----------|------|------------|
| `arr.push(x)` | 뒤(rear)에 추가 | O(1) |
| `arr.shift()` | 앞(front)에서 제거 후 반환 | O(N) ⚠️ |
| `arr[front++]` | 직접 인덱스로 큐 흉내 | O(1) |
| 클래스 구현 | 위 패턴을 캡슐화 | O(1) |

## 6. 몸풀기 문제

### 문제 15: 요세푸스 문제

> N명이 원형으로 서있고 1번부터 K번째 사람을 차례로 제거한다. 마지막에 살아남는 사람의 번호를 반환하라.
> 권장 시간 복잡도: O(N × K)

**접근 아이디어**: 원형 구조를 큐로 시뮬레이션. K-1번 만큼 앞에서 빼서 뒤로 보내면, K번째 원소가 자연스럽게 큐의 앞으로 온다. 그걸 팝해서 제거.

**알고리즘 트레이스** (`N=5, K=3`):

```
초기:        [1, 2, 3, 4, 5]
1, 2를 뒤로:  [3, 4, 5, 1, 2]
3 제거:      [4, 5, 1, 2]

4, 5를 뒤로:  [1, 2, 4, 5]
1 제거:      [2, 4, 5]

2, 4를 뒤로:  [5, 2, 4]
5 제거:      [2, 4]

2, 4를 뒤로:  [4, 2]
4 제거:      [2]

남은 사람: 2
```

```javascript
class Queue {
  items = [];
  front = 0;
  rear = 0;

  push(item) {
    this.items.push(item);
    this.rear++;
  }
  pop() {
    return this.items[this.front++];
  }
  size() {
    return this.rear - this.front;
  }
}

function solution(N, K) {
  const queue = new Queue();
  for (let i = 1; i <= N; i++) {
    queue.push(i);
  }

  while (queue.size() > 1) {
    // K-1번 앞→뒤로 회전
    for (let i = 0; i < K - 1; i++) {
      queue.push(queue.pop());
    }
    queue.pop(); // K번째 제거
  }

  return queue.pop();
}
```

> **핵심 통찰**: 원형으로 회전하는 구조는 "앞에서 빼서 뒤로 넣는" 큐 연산으로 자연스럽게 표현된다. 굳이 원형 큐를 구현할 필요는 없다.

**시간 복잡도**: O(N × K) — 각 사람을 제거하는 데 K번의 회전이 필요.

> 더 효율적으로는 세그먼트 트리로 O(N log N)에 풀 수 있지만, 큐 학습 목적에서는 위 풀이가 충분하다.

## 7. 합격자가 되는 모의테스트

### 문제 16: 기능 개발 — 프로그래머스

> 각 기능의 진도(`progresses`)와 개발 속도(`speeds`)가 주어진다. 각 기능은 100% 완료되면 배포되지만, 앞 기능이 완료되지 않으면 뒤 기능은 함께 배포 대기. 각 배포일에 몇 개의 기능이 함께 배포되는지 배열로 반환하라.
> 제약: 작업 개수 ≤ 100
> [프로그래머스 #42586](https://programmers.co.kr/learn/courses/30/lessons/42586)

**접근 아이디어**:
1. 각 기능의 **배포 가능일**을 미리 계산: `Math.ceil((100 - progress) / speed)`.
2. 배포 가능일 배열을 앞에서부터 순회 — 현재 기준일(`maxDay`) 이하면 같은 날 배포(카운트 증가), 더 늦으면 별도 배포(카운트 push 후 리셋).

> **함정**: `Math.ceil`을 빼먹으면 `(100-30)/30 = 2.33...`이 `2`로 잘려서 배포일이 잘못 계산된다. 정수 나눗셈은 항상 ceil/floor 명시.

**알고리즘 트레이스** (`progresses=[93,30,55], speeds=[1,30,5]`):

```
배포 가능일: [7, 3, 9]   (Math.ceil((100-93)/1)=7, Math.ceil((100-30)/30)=3, Math.ceil((100-55)/5)=9)

i=0: maxDay=7, count=1
i=1: 3 ≤ 7 → count=2 (같은 날 배포)
i=2: 9 > 7 → push count=2, maxDay=9, count=1
끝:  push count=1

결과: [2, 1]
```

```javascript
function solution(progresses, speeds) {
  const answer = [];
  const n = progresses.length;

  // ① 각 기능의 배포 가능일 계산
  const daysLeft = progresses.map((progress, i) =>
    Math.ceil((100 - progress) / speeds[i])
  );

  let count = 0;
  let maxDay = daysLeft[0]; // 현재 배포 기준일

  for (let i = 0; i < n; i++) {
    if (daysLeft[i] <= maxDay) {
      count++;
    } else {
      answer.push(count);
      count = 1;
      maxDay = daysLeft[i];
    }
  }
  answer.push(count); // ② 마지막 그룹 빼먹지 말 것

  return answer;
}
```

> **함정**: 마지막 그룹의 `count`를 반복문 밖에서 한 번 더 push해야 한다. 이걸 빼먹는 실수가 흔하다.

> **핵심 통찰**: 큐를 직접 쓰지 않아도 풀 수 있는 큐 문제다. "앞이 끝나야 뒤가 나간다"는 FIFO 의미만 잘 살리면 된다. 코딩 테스트에서는 자료구조보다 **FIFO 원리** 자체를 이해하는 게 중요하다.

**시간 복잡도**: O(N)

### 문제 17: 카드 뭉치 — 프로그래머스

> 카드 뭉치 `cards1`, `cards2`에서 앞부터 한 장씩 꺼내 쓰며, `goal` 순서를 만들 수 있는지 판별. 카드는 한 번만 사용 가능, 순서는 바꿀 수 없음.
> 제약: 길이 ≤ 10
> [프로그래머스 #159994](https://school.programmers.co.kr/learn/courses/30/lessons/159994)

**접근 아이디어**: "앞부터 한 장씩 사용", "순서를 바꿀 수 없음"이 정확히 FIFO. 세 큐(`cards1`, `cards2`, `goal`)를 두고 `goal`의 front를 `cards1`/`cards2`의 front와 비교해 일치하는 쪽을 팝.

```javascript
class Queue {
  items = [];
  front = 0;
  rear = 0;

  constructor(array) {
    this.items = [...array];
    this.rear = array.length;
  }

  push(item) {
    this.items.push(item);
    this.rear++;
  }
  pop() {
    return this.items[this.front++];
  }
  first() {
    return this.items[this.front];
  }
  isEmpty() {
    return this.front === this.rear;
  }
}

function solution(cards1, cards2, goal) {
  const q1 = new Queue(cards1);
  const q2 = new Queue(cards2);
  const qGoal = new Queue(goal);

  while (!qGoal.isEmpty()) {
    if (!q1.isEmpty() && q1.first() === qGoal.first()) {
      q1.pop();
      qGoal.pop();
    } else if (!q2.isEmpty() && q2.first() === qGoal.first()) {
      q2.pop();
      qGoal.pop();
    } else {
      break; // 둘 다 못 쓰면 실패
    }
  }

  return qGoal.isEmpty() ? "Yes" : "No";
}
```

> **함정**: `isEmpty` 체크를 먼저 해야 한다. 빈 큐의 `first()`는 `undefined`인데, `goal`의 front가 마침 `undefined`가 아니면 무한 루프나 잘못된 비교가 일어날 수 있다.

> **핵심 통찰**: "앞부터 순서대로 사용해야 한다"는 제약은 큐의 정의 그 자체다. 카드 뭉치를 큐로 보면 알고리즘이 자명해진다.

**시간 복잡도**: O(N + M) — N은 cards 길이, M은 goal 길이.

## 8. 함정/실수 노트

| 함정 | 설명 |
|------|------|
| `shift()` 남용 | O(N)이라 큰 큐에서 시간 초과. 직접 구현하거나 인덱스 패턴 사용 |
| 마지막 그룹 push 누락 | 그룹 카운팅 패턴에서 반복문 밖에서 한 번 더 push 필요 |
| `Math.ceil` 누락 | 배포 가능일 같은 정수 올림 계산을 누락하면 결과가 틀어짐 |
| 빈 큐 `first()` 호출 | `undefined` 반환되어 비교가 망가짐. `isEmpty` 먼저 체크 |
| `front++` vs `arr.shift()` | 인덱스 증가는 O(1), shift는 O(N) |
| 큐 클래스 매번 새로 작성 | 자주 쓰는 패턴은 외워두면 시간 절약 |

## 9. 요약

- **큐는 선입선출(FIFO) 자료구조**다. front에서 빼고 rear에서 넣는다.
- **자바스크립트는 큐를 제공하지 않는다.** `shift()`는 O(N)이라 큰 데이터에 부적합.
- **`front` 포인터를 증가시키는 방식**이 가장 실용적인 큐 구현이다 — 모든 연산 O(1).
- **원형 회전, 작업 대기열, BFS** 등이 큐의 전형적 용도.
- "앞부터 순서대로", "들어온 순서대로 처리"라는 단서가 큐를 가리킨다.
- **요세푸스 문제**처럼 원형 회전은 큐의 push/pop을 결합해 자연스럽게 표현된다.

## 리마인드 (저자)

1. 큐는 선입선출(FIFO) 방식으로 데이터를 관리하는 자료구조다.
2. 자바스크립트는 큐를 제공하지 않는다. 배열의 `shift()`로 흉내 낼 수 있지만 O(1)이 아니므로 큰 데이터에서는 직접 구현하는 것이 좋다.
