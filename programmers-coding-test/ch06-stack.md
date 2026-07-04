# Chapter 06: Stack (스택)

## 핵심 질문

먼저 들어간 데이터를 가장 나중에 꺼내는 후입선출(LIFO) 자료구조는 어떤 문제에 적합한가? 자바스크립트 배열로 어떻게 스택을 구현하며, 어떤 문제가 스택을 떠올리게 하는가?

## 1. 스택의 개념

스택(stack)의 어원은 "쌓는다"이다. 먼저 입력한 데이터가 가장 나중에 나오는 자료구조다. 티슈 박스가 좋은 비유다. 먼저 넣은 티슈가 가장 아래에 깔리고, 우리는 가장 위의 티슈부터 사용한다.

**후입선출(LIFO, Last In First Out)** 또는 **선입후출(FILO)** 이라 부른다. 삽입 연산을 **푸시(push)**, 꺼내는 연산을 **팝(pop)** 이라고 한다.

### 동작 원리

```
빈 스택 → push(1) → push(2) → pop() → push(3) → pop() → pop()

[ ]      [1]      [1,2]     [1]      [1,3]     [1]      [ ]
                              ↑                  ↑
                            top=1              top=1
```

> **핵심 통찰**: "가장 최근에 넣은 데이터를 먼저 처리해야 하는 상황"이면 스택을 떠올려라. 괄호 짝 맞추기, 함수 호출 스택, 실행 취소(undo) 등이 대표적이다.

## 2. 스택의 ADT (추상 자료형)

ADT(Abstract Data Type)는 인터페이스만 있고 실제 구현은 되지 않은 자료형이다. 자료구조의 설계도 같은 것.

| 구분 | 정의 | 설명 |
|------|------|------|
| 연산 | `boolean isFull()` | 스택이 가득 찼으면 true |
| | `boolean isEmpty()` | 스택이 비었으면 true |
| | `void push(item)` | 데이터를 푸시 |
| | `Item pop()` | 최근 푸시한 데이터를 팝하고 반환 |
| 상태 | `int top` | 최근 푸시한 데이터의 위치 |
| | `Item data[maxSize]` | 데이터를 관리하는 배열 |

> **합격 조언**: 자료구조의 세부 동작을 이해하면 코딩 테스트뿐 아니라 면접에도 큰 도움이 된다. 자료구조의 성능과 특성을 알아야 효율적인 알고리즘을 떠올릴 수 있다.

### push 연산의 내부 동작

```
push(3)
  ① isFull()로 가득 찼는지 확인
  ② top을 1만큼 증가
  ③ data[top]에 3 저장
```

### pop 연산의 내부 동작

```
pop()
  ① isEmpty()로 비었는지 확인
  ② top이 가리키는 데이터를 반환
  ③ top을 1만큼 감소
```

`data[top]`에 데이터가 남아있어도 `top`이 가리키지 않으면 "비어있다고 본다". 스택의 핵심은 **`top`의 위치**다.

## 3. JavaScript에서의 스택 구현

자바스크립트는 표준 라이브러리에 별도의 스택 클래스가 없다. 하지만 배열의 `push()`와 `pop()`이 정확히 스택 연산이다.

```javascript
const stack = [];

stack.push(1);         // [1]
stack.push(2);         // [1, 2]
stack.push(3);         // [1, 2, 3]

const top = stack.pop();         // 3, 스택: [1, 2]
const next = stack.pop();        // 2, 스택: [1]
const isEmpty = stack.length === 0;
```

자바스크립트의 배열은 동적 크기이므로 `isFull()`은 일반적으로 필요 없다. `isEmpty()`는 `stack.length === 0`으로 충분하다.

## 4. 핵심 코드 패턴

### 빈 스택 체크 후 팝

```javascript
if (stack.length > 0) {
  const top = stack.pop();
  // ...
}
```

### top 원소 확인 (팝 없이)

```javascript
const top = stack[stack.length - 1];
```

### 짝 매칭 패턴

```javascript
for (const c of s) {
  if (isOpening(c)) {
    stack.push(c);
  } else {
    if (stack.length === 0 || !match(stack[stack.length - 1], c)) {
      return false;
    }
    stack.pop();
  }
}
return stack.length === 0;
```

### 인덱스 저장으로 거리 계산 (모노톤 스택)

```javascript
const stack = [];
for (let i = 0; i < arr.length; i++) {
  while (stack.length > 0 && condition(arr[stack[stack.length - 1]], arr[i])) {
    const j = stack.pop();
    answer[j] = i - j; // 거리 계산
  }
  stack.push(i);
}
```

## 5. JavaScript 빌트인 메서드 레퍼런스

| 메서드 | 동작 | 시간 복잡도 |
|--------|------|------------|
| `arr.push(x)` | 맨 뒤 추가 | O(1) |
| `arr.pop()` | 맨 뒤 제거하고 반환 | O(1) |
| `arr[arr.length - 1]` | top 원소 조회 | O(1) |
| `arr.length === 0` | 비었는지 확인 | O(1) |
| `arr.length` | 스택 크기 | O(1) |

## 6. 몸풀기 문제

### 문제 08: 괄호 짝 맞추기

> 소괄호 `(`와 `)`가 마구 섞인 문자열에서 정상으로 열고 닫혔는지 판별하는 함수.
> 권장 시간 복잡도: O(N)

**접근 아이디어**: 닫힌 괄호가 나오기 직전의 **가장 최근(가장 가까운)** 열린 괄호와 짝을 이뤄야 한다. "가장 최근"이 곧 스택을 의미한다.

**알고리즘**:
1. 문자열을 순회하며 열린 괄호는 푸시.
2. 닫힌 괄호가 나오면 팝(짝 상쇄).
3. 끝까지 돌고 스택이 비었으면 짝이 맞은 것.

```javascript
function solution(s) {
  const stack = [];
  for (const c of s) {
    if (c === "(") {
      stack.push(c);
    } else if (c === ")") {
      if (stack.length === 0) return false;
      stack.pop();
    }
  }
  return stack.length === 0;
}
```

**시간 복잡도**: O(N)

### 문제 09: 10진수를 2진수로 변환하기

> 10진수를 받아 2진수 문자열로 변환해 반환.
> 권장 시간 복잡도: O(log N)

**알고리즘**: 10진수를 2로 나눈 나머지를 차곡차곡 쌓고, 마지막에 거꾸로 읽어내면 2진수가 된다. 정확히 LIFO 패턴.

**알고리즘 트레이스** (`13`):

```
13 ÷ 2 = 6 ... 1   (push 1) → [1]
 6 ÷ 2 = 3 ... 0   (push 0) → [1, 0]
 3 ÷ 2 = 1 ... 1   (push 1) → [1, 0, 1]
 1 ÷ 2 = 0 ... 1   (push 1) → [1, 0, 1, 1]

pop 순서: 1 → 1 → 0 → 1  →  "1101"
```

```javascript
function solution(decimal) {
  const stack = [];
  while (decimal > 0) {
    stack.push(decimal % 2);
    decimal = Math.floor(decimal / 2);
  }

  let binary = "";
  while (stack.length > 0) {
    binary += stack.pop();
  }
  return binary;
}
```

> **함정**: `Math.floor(decimal / 2)`를 빠뜨리고 `decimal / 2`만 쓰면 부동소수점 때문에 무한 루프에 빠진다. 정수 나눗셈은 명시적으로 `Math.floor`나 비트 연산(`>> 1`)을 쓸 것.

**시간 복잡도**: O(log N)

## 7. 합격자가 되는 모의테스트

### 문제 10: 괄호 회전하기 — 프로그래머스

> 대괄호 `[]`, 중괄호 `{}`, 소괄호 `()`가 섞인 문자열 `s`를 왼쪽으로 x칸 회전시켰을 때 올바른 괄호 문자열이 되게 하는 x의 개수를 반환하라.
> 제약: s 길이 ≤ 1,000
> [프로그래머스 #76502](https://programmers.co.kr/learn/courses/30/lessons/76502)

**접근 아이디어**:
- 회전을 직접 만들지 말고 **인덱스 모듈러**로 시뮬레이션 — `s[(i + j) % n]`.
- 각 회전마다 짝 맞추기를 새로 수행.

```javascript
function solution(s) {
  const n = s.length;
  let answer = 0;

  for (let i = 0; i < n; i++) {
    const stack = [];
    let isCorrect = true;

    for (let j = 0; j < n; j++) {
      const c = s[(i + j) % n]; // 회전 시뮬레이션

      if (c === "[" || c === "(" || c === "{") {
        stack.push(c);
      } else {
        if (stack.length === 0) {
          isCorrect = false;
          break;
        }
        const top = stack[stack.length - 1];
        if (
          (c === "]" && top === "[") ||
          (c === ")" && top === "(") ||
          (c === "}" && top === "{")
        ) {
          stack.pop();
        } else {
          isCorrect = false;
          break;
        }
      }
    }

    if (isCorrect && stack.length === 0) {
      answer += 1;
    }
  }

  return answer;
}
```

> **핵심 통찰**: 배열을 실제로 회전시키면 O(N)의 비용이 생긴다. **시작 인덱스 + 모듈러 연산**으로 회전을 표현하면 추가 비용 없이 같은 효과를 낸다.

**시간 복잡도**: O(N²)

### 문제 11: 짝지어 제거하기 — 프로그래머스

> 알파벳 소문자 문자열에서 같은 알파벳 2개가 붙어있는 짝을 찾아 제거하고 앞뒤를 이어 붙인다. 모두 제거할 수 있으면 1, 아니면 0을 반환.
> 제약: 길이 ≤ 1,000,000
> [프로그래머스 #12973](https://programmers.co.kr/learn/courses/30/lessons/12973)

**접근 아이디어**: O(N²) 이중 반복문은 100만 길이에 절대 통과 못 한다. 스택을 써서 O(N)으로 풀어야 한다.

**핵심 관찰**: 현재 문자와 **가장 최근 문자**(스택의 top)를 비교한다는 것이 LIFO와 정확히 맞는다. 짝을 만나면 팝, 아니면 푸시. 마지막에 스택이 비어있으면 모두 제거된 것.

**알고리즘 트레이스** (`baabaa`):

```
b → push       [b]
a → push       [b, a]
a → top과 같음, pop  [b]
b → top과 같음, pop  []
a → push       [a]
a → top과 같음, pop  []
```

```javascript
function solution(s) {
  const stack = [];
  for (const c of s) {
    if (stack.length > 0 && stack[stack.length - 1] === c) {
      stack.pop();
    } else {
      stack.push(c);
    }
  }
  return stack.length === 0 ? 1 : 0;
}
```

> **합격 조언**: "직전과 비교", "가장 최근과 매칭"이라는 단서가 보이면 스택을 떠올리는 감각을 키워야 한다. 처음에는 안 떠오르더라도 정답을 본 후 그 알고리즘이 어떻게 도출됐는지 곱씹어보면 된다.

**시간 복잡도**: O(N)

### 문제 12: 주식 가격 — 프로그래머스

> 초 단위 주가 배열 `prices`가 주어질 때, 각 초의 주가가 떨어지지 않은 시간(초)을 배열로 반환하라.
> 제약: 길이 ≤ 100,000 — O(N) 알고리즘 필수
> [프로그래머스 #42584](https://programmers.co.kr/learn/courses/30/lessons/42584)

**접근 아이디어**: O(N²) 이중 반복문은 정확성은 통과해도 효율성에서 시간 초과. **모노톤 스택**(monotonic stack)으로 O(N) 해결.

**알고리즘**:
1. 스택에는 인덱스를 저장.
2. 현재 가격이 스택 top의 가격보다 낮으면 → top 원소의 길이 확정 → 팝.
3. 그렇지 않으면 → 스택에 푸시.
4. 끝까지 남은 인덱스는 가격이 끝까지 떨어지지 않은 것 → `n - 1 - j`로 계산.

**알고리즘 트레이스** (`prices = [1, 6, 9, 5, 3]`):

```
i=0  push 0    stack=[0]
i=1  prices[0]=1 < prices[1]=6 → push 1   stack=[0, 1]
i=2  prices[1]=6 < prices[2]=9 → push 2   stack=[0, 1, 2]
i=3  prices[2]=9 > prices[3]=5 → pop 2, answer[2] = 3-2 = 1
     prices[1]=6 > prices[3]=5 → pop 1, answer[1] = 3-1 = 2
     prices[0]=1 < prices[3]=5 → push 3   stack=[0, 3]
i=4  prices[3]=5 > prices[4]=3 → pop 3, answer[3] = 4-3 = 1
     prices[0]=1 < prices[4]=3 → push 4   stack=[0, 4]
끝   남은 인덱스: 0, 4
     answer[4] = 4-4 = 0
     answer[0] = 4-0 = 4

결과: [4, 2, 1, 1, 0]
```

```javascript
function solution(prices) {
  const n = prices.length;
  const answer = new Array(n).fill(0);
  const stack = [0];

  for (let i = 1; i < n; i++) {
    while (
      stack.length > 0 &&
      prices[i] < prices[stack[stack.length - 1]]
    ) {
      const j = stack.pop();
      answer[j] = i - j;
    }
    stack.push(i);
  }

  // 끝까지 안 떨어진 가격
  while (stack.length > 0) {
    const j = stack.pop();
    answer[j] = n - 1 - j;
  }

  return answer;
}
```

> **핵심 통찰**: "다음으로 작은 값까지의 거리"는 **모노톤 스택**의 전형적 응용이다. 이중 반복문 대신 각 원소가 푸시/팝 한 번씩만 되므로 O(N).

**시간 복잡도**: O(N)

### 문제 13: 크레인 인형뽑기 게임 — 2019 카카오

> N×N 격자의 각 열에 인형이 쌓여있다. 크레인이 `moves`에 따라 각 열에서 가장 위의 인형을 뽑아 바구니에 쌓는다. 같은 인형 2개가 연속으로 쌓이면 사라진다. 사라진 인형의 총 개수를 반환하라.
> [프로그래머스 #64061](https://programmers.co.kr/learn/courses/30/lessons/64061)

**접근 아이디어**: 두 종류의 스택이 필요하다.
- **각 열별 스택** (`lanes[]`): board를 열 단위로 변환. 0이 아닌 값만 저장. board의 아래쪽이 스택의 top이 되도록 push 순서를 잡는다.
- **바구니 스택** (`bucket`): 인형이 들어가는 순서대로 쌓이고, top과 동일한 인형이 들어오면 팝.

```javascript
function solution(board, moves) {
  // ① 각 열을 스택으로 변환
  const lanes = [...Array(board[0].length)].map(() => []);

  // board의 가장 아래(큰 row 인덱스)부터 push → 위쪽이 스택의 top
  for (let i = board.length - 1; i >= 0; i--) {
    for (let j = 0; j < board[0].length; j++) {
      if (board[i][j]) {
        lanes[j].push(board[i][j]);
      }
    }
  }

  // ② 바구니 시뮬레이션
  const bucket = [];
  let answer = 0;

  for (const m of moves) {
    if (lanes[m - 1].length > 0) {
      const doll = lanes[m - 1].pop();
      if (bucket.length > 0 && bucket[bucket.length - 1] === doll) {
        bucket.pop();
        answer += 2;
      } else {
        bucket.push(doll);
      }
    }
  }

  return answer;
}
```

> **함정**: board를 행 우선으로 보는 시각에서 열별 스택으로 변환할 때 인덱스 방향이 헷갈린다. board의 **아래쪽이 먼저 들어가야** 위쪽이 top이 된다 — `i = board.length - 1`부터 역순 순회.

**시간 복잡도**: O(N² + M)

### 문제 14: 표 편집 — 2021 카카오 (고난이도)

> n행 표에서 행 선택/삭제/복구 명령을 처리한 후, 어떤 행이 남고 삭제됐는지 `O`/`X` 문자열로 반환하라.
> - `U X` / `D X`: 위/아래로 X칸 이동
> - `C`: 현재 행 삭제, 바로 아래 행 선택 (마지막이면 위)
> - `Z`: 가장 최근 삭제 행 복구 (선택 위치는 안 바뀜)
> 제약: n ≤ 1,000,000, cmd 개수 ≤ 200,000
> [프로그래머스 #81303](https://programmers.co.kr/learn/courses/30/lessons/81303)

**접근 아이디어**: 실제 배열을 삽입/삭제하면 O(N) 비용이 매번 발생해 시간 초과. **이중 연결 리스트**를 배열로 시뮬레이션한다.

- `up[k]`: 행 k의 바로 위 행 인덱스
- `down[k]`: 행 k의 바로 아래 행 인덱스
- 삭제: `up[down[k]] = up[k]`, `down[up[k]] = down[k]` (k의 위·아래를 직접 연결)
- 복구: 삭제 시 `up[k]`, `down[k]`를 그대로 두므로, 복구할 때 `down[up[k]] = k`, `up[down[k]] = k`만 다시 잇기.

가상 공간 트릭: 배열 양 끝에 `+1`씩 가상 공간을 두면 양 끝 행 처리도 같은 식으로 통일된다. 따라서 배열 크기는 `n + 2`.

**삭제 후 복구의 우아함**:

```
삭제 시: up[down[k]] = up[k]     ← k의 아래 행이 k의 위 행을 가리킴
        down[up[k]] = down[k]   ← k의 위 행이 k의 아래 행을 가리킴
        (단, up[k], down[k]는 그대로 둠 — 복구 시 활용)

복구 시: down[up[k]] = k         ← k의 위 행이 다시 k를 가리킴
        up[down[k]] = k         ← k의 아래 행이 다시 k를 가리킴
```

삭제 시 k의 위/아래 정보를 보존했기에 복구가 단순해진다.

```javascript
function solution(n, k, cmd) {
  const deleted = []; // 삭제 이력 스택
  const up = [...new Array(n + 2)].map((_, i) => i - 1);
  const down = [...new Array(n + 1)].map((_, i) => i + 1);

  k += 1; // 가상 공간 보정

  for (const item of cmd) {
    if (item[0] === "C") {
      deleted.push(k);
      up[down[k]] = up[k];
      down[up[k]] = down[k];
      k = n < down[k] ? up[k] : down[k]; // 마지막이면 위로
    } else if (item[0] === "Z") {
      const restore = deleted.pop();
      down[up[restore]] = restore;
      up[down[restore]] = restore;
    } else {
      const [action, num] = item.split(" ");
      if (action === "U") {
        for (let i = 0; i < num; i++) k = up[k];
      } else {
        for (let i = 0; i < num; i++) k = down[k];
      }
    }
  }

  // 결과 문자열 생성
  const answer = new Array(n).fill("O");
  for (const i of deleted) {
    answer[i - 1] = "X"; // 가상 공간 보정 되돌리기
  }
  return answer.join("");
}
```

> **핵심 통찰**: 삽입·삭제가 빈번한 시퀀스를 O(1)로 처리하려면 연결 리스트가 필요하다. 객체 기반 연결 리스트 대신 **`up`/`down` 두 배열**로 같은 자료구조를 만들 수 있다.

> **함정**: 마지막 행을 삭제했을 때 `down[k]`는 가상 공간 인덱스(n)를 가리킨다. `n < down[k]`로 가상 공간인지 검사하고, 그러면 `up[k]`(위)로 이동. 이 케이스를 빠뜨리면 마지막 행 처리가 망가진다.

**시간 복잡도**: O(N + M) — N은 표 크기, M은 명령어 개수.

## 8. 함정/실수 노트

| 함정 | 설명 |
|------|------|
| 빈 스택 팝 시도 | `pop()`은 빈 배열에서 `undefined` 반환. 항상 `length` 체크 후 팝 |
| `Math.floor` 누락 | `decimal / 2`만 쓰면 부동소수점이 영원히 줄어들지 않아 무한 루프 |
| 회전을 실제로 수행 | `slice`/`concat`으로 회전 배열을 만들면 O(N) 추가 비용 — 인덱스 모듈러로 처리 |
| 모노톤 스택의 인덱스 vs 값 | 거리를 계산하려면 인덱스를 저장해야 함 |
| 이중 연결 리스트의 가상 공간 | 양 끝 처리를 통일하려면 +2 크기 배열 |
| 짝 매칭 시 `top` 비교 누락 | 닫힌 괄호의 종류와 스택 top의 짝이 맞는지 반드시 검증 |
| 인덱스로 push 후 length 비교 | board를 열 단위로 변환할 때 행 인덱스 방향에 주의 |

## 9. 요약

- **스택은 후입선출(LIFO) 자료구조**다. 푸시·팝·top 조회 모두 O(1).
- **자바스크립트는 배열의 `push`/`pop`이 곧 스택**이다. 별도 클래스가 필요 없다.
- 스택 문제의 가장 큰 어려움은 "이게 스택 문제구나"를 알아차리는 것이다. **"가장 최근", "직전", "짝 맞추기", "되돌리기"** 같은 키워드를 단서로 보라.
- **모노톤 스택**은 "다음으로 작은/큰 값까지의 거리" 류 문제에서 O(N)으로 푸는 표준 패턴이다.
- **연결 리스트의 배열 시뮬레이션**(`up[]`/`down[]`)은 삽입·삭제가 빈번한 시퀀스 문제에서 O(1)을 가능하게 한다.
- **인덱스를 스택에 저장**하면 거리·길이 계산이 자연스러워진다.

## 리마인드 (저자)

1. 스택은 후입선출(LIFO) 방식으로 데이터를 관리하는 자료구조다.
2. 자바스크립트의 배열은 `push()`, `pop()` 메서드로 요소를 추가·제거할 수 있어 배열을 스택처럼 사용할 수 있다.
