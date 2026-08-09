# Chapter 10: Recursively Recurse with Recursion (재귀를 사용한 재귀적 반복)

## 핵심 질문

함수가 자기 자신을 호출하면 무슨 일이 벌어지는가? 무한 호출을 막는 장치는 무엇인가? 컴퓨터는 "아직 안 끝난 함수들"을 어떻게 기억하며, 몇 단계나 깊은지 모르는 문제는 왜 재귀로 풀리는가?

---

## 1. 재귀란

```typescript
function blah(): void {
  blah();
}
```

이 함수를 호출하면 자신을 무한대로 호출한다. **재귀(*recursion - 함수가 자기 자신을 호출하는 것*)**는 이렇게 무한 루프로도 쓸 수 있지만(쓸모없다), 올바르게 활용하면 까다로운 문제를 마법처럼 간단하게 푸는 강력한 도구이며, 이후 나올 고급 알고리즘들의 토대다.

## 2. 루프 대신 재귀

NASA 우주선 발사 카운트다운 함수(10부터 0까지 출력)를 루프 없이 재귀로:

```typescript
function countdown(number: number): void {
  console.log(number);
  countdown(number - 1);  // 자기 자신 호출
}
```

`countdown(10)` → 10 출력 → `countdown(9)` → 9 출력 → … 루프 구조 없이 함수 호출만으로 반복이 일어난다.

**루프를 쓸 수 있는 곳이면 거의 어디든 재귀도 쓸 수 있다.** 다만 쓸 수 있다고 무조건 써야 하는 것은 아니다 - 재귀는 명쾌한 코드를 위한 하나의 도구이고, 이 예제에서는 for 루프보다 나을 것이 없다. 재귀가 진짜 빛나는 예제는 이 장 끝에 나온다.

## 3. 기저 조건

위 구현은 0에서 멈추지 않고 -1, -2, …를 무한 출력한다. 조건을 추가하자:

```typescript
function countdown(number: number): void {
  console.log(number);
  if (number === 0) {
    return;                  // 더 이상 자신을 호출하지 않음
  } else {
    countdown(number - 1);
  }
}
```

> **핵심 통찰**: 함수가 더 이상 반복되지 않는 경우를 **기저 조건(*base case - 재귀가 멈추는 조건*)**이라 부른다. **모든 재귀 함수에는 기저 조건이 적어도 하나 있어야 한다** - 없으면 무한 재귀다.

## 4. 재귀 코드 읽기 - "냅킨" 방법

재귀에는 두 스킬이 있다: 읽기와 작성하기(작성은 Ch11). 읽기 연습 대상은 **계승(*factorial - N × (N-1) × … × 1. 예: 3! = 6, 5! = 120*)**:

```typescript
function factorial(number: number): number {
  if (number === 1) {
    return 1;                              // 기저 조건
  } else {
    return number * factorial(number - 1); // 재귀
  }
}
```

읽는 절차:

1. **기저 조건을 찾는다** - `number === 1`이면 1 반환
2. 기저 조건에서의 동작을 확인한다: `factorial(1)` → 1. 냅킨에 기록
3. **"끝에서 두 번째" 조건**으로 간다: `factorial(2)` → `2 * factorial(1)` → 냅킨을 보면 1 → 2. 기록
4. 한 단계씩 위로: `factorial(3)` → `3 * factorial(2)` → 3 × 2 = 6
5. 이런 식으로 기저 조건부터 위로 쌓아 올리며 추론한다

**기저 조건에서 시작해 위로 올라가는 것**이 재귀 코드를 추론하는 훌륭한 방법이다.

## 5. 컴퓨터의 눈으로 바라본 재귀 - 호출 스택

`factorial(3)`을 실행할 때 컴퓨터의 사정은 복잡하다. `factorial(3)`이 **끝나기 전에** `factorial(2)`가 시작되고, 그것이 끝나기 전에 `factorial(1)`이 시작된다. 컴퓨터는 "돌아가서 마저 실행해야 할 함수들"을 어떻게 기억할까?

> **핵심 통찰**: 컴퓨터는 Ch9의 스택으로 실행 중인 함수를 기록한다 - 이를 **호출 스택(*call stack - 호출됐지만 아직 완료되지 않은 함수들을 기록하는 스택*)**이라 부른다. **가장 최근에 호출된 함수가 가장 먼저 완료되어야** 하므로 LIFO인 스택이 재귀에 이상적이다.

`factorial(3)` 실행 흐름:

1. `factorial(3)` 호출 → 완료 전에 `factorial(2)` 호출 (스택: `[factorial(3)]`)
2. `factorial(2)` → 완료 전에 `factorial(1)` 호출 (스택: `[factorial(3), factorial(2)]`)
3. `factorial(1)`은 기저 조건 - 1을 반환하며 완료
4. 스택 맨 위를 팝: `factorial(2)` 마저 실행 → 2 × 1 = 2 반환
5. 팝: `factorial(3)` 완료 → 3 × 2 = 6
6. 스택이 비면 재귀 종료

각 재귀 호출이 계산 결과를 "부모" 함수에 반환해 최초 호출이 최종 값을 얻는 것을 **호출 스택을 통해 값 위로 전달하기(passing a value up through the call stack)**라 부른다.

**스택 오버플로(*stack overflow - 무한 재귀 등으로 호출 스택이 메모리를 다 채워 발생하는 오류*)**: 무한 재귀에서는 같은 함수가 끝없이 푸시되다가 메모리가 차면 컴퓨터가 재귀를 강제 중단시킨다.

## 6. 파일시스템 순회 - 재귀가 빛나는 곳

> **핵심 통찰**: **몇 단계나 깊이 들어가야 하는지 모르는 문제**가 재귀와 자연스럽게 들어맞는 유형이다.

디렉터리의 모든 하위 디렉터리(그 하위의 하위까지 전부)를 출력하고 싶다. 루프 방식은 "한 단계 아래"용 루프, "두 단계 아래"용 중첩 루프…를 미리 짜야 하는데, **깊이를 모르면 불가능**하다. 재귀라면:

```typescript
import * as fs from "fs";

function findDirectories(directory: string): void {
  for (const filename of fs.readdirSync(directory)) {
    const fullPath = `${directory}/${filename}`;
    if (fs.statSync(fullPath).isDirectory()) {
      console.log(fullPath);
      findDirectories(fullPath);  // 하위 디렉터리에 재귀 호출
    }
  }
}

findDirectories(".");
```

하위 디렉터리를 찾을 때마다 그 디렉터리에 같은 함수를 호출하므로, **하위 디렉터리가 더 없을 때까지 임의의 깊이로** 파고든다. (이 순회 순서의 시각화는 Ch18의 깊이 우선 탐색에서 다시 정밀하게 다룬다.)

---

## 요약

- **재귀 = 자기 자신을 호출하는 함수.** 루프가 가능한 곳 대부분에 쓸 수 있지만, 도구일 뿐 만능은 아니다
- **기저 조건은 필수** - 없으면 무한 재귀 → 스택 오버플로
- 재귀 읽기: **기저 조건부터 위로** 냅킨에 기록하며 추론한다
- 컴퓨터는 **호출 스택(LIFO)**으로 미완료 함수를 기록하고, 완료된 값은 스택을 통해 부모로 전달된다
- 재귀의 킬러 유스케이스: **깊이를 미리 알 수 없는 다단계 문제** (파일시스템 순회 등)

## 연습 문제 (해답 예시)

1. **`printEveryOther(low, high)`(low부터 2씩 증가 출력)의 기저 조건은?** - **`low > high`.** 이때 재귀 호출 없이 반환한다.
2. **`factorial`이 (n-2)로 재귀하도록 고장 났을 때 `factorial(10)`의 결과는?** - 10 × 8 × 6 × 4 × 2 × factorial(0)인데 **기저 조건(n === 1)에 절대 도달하지 못한다.** 0, -1, -2…로 무한 재귀하다 **스택 오버플로**가 난다.
3. **`sum(low, high)`에 빠진 기저 조건 추가** - low와 high가 같아지면 재귀를 멈춘다:

   ```typescript
   function sum(low: number, high: number): number {
     if (high === low) {
       return low;
     }
     return high + sum(low, high - 1);
   }
   ```

4. **중첩 배열 안의 모든 숫자만 출력하는 재귀 함수** - 원소가 배열이면 재귀, 숫자면 출력:

   ```typescript
   function printNumbers(array: unknown[]): void {
     for (const element of array) {
       if (Array.isArray(element)) {
         printNumbers(element);   // 배열이면 파고든다 (깊이를 몰라도 된다)
       } else {
         console.log(element);
       }
     }
   }
   ```

## 다른 챕터와의 관계

- **Ch9 (스택과 큐)**: 호출 스택은 스택의 가장 유명한 실전 응용이다
- **Ch11 (재귀적으로 작성하는 법)**: 읽기에 이어 재귀 코드를 직접 작성하는 요령을 다룬다
- **Ch12 (동적 프로그래밍)**: 재귀의 숨은 비용(중복 호출)과 그 치료법이 나온다
- **Ch13 (퀵 정렬)·Ch15 (BST)·Ch17 (트라이)·Ch18 (그래프 DFS)**: 이후 알고리즘·자료 구조의 순회가 전부 재귀 위에 서 있다
