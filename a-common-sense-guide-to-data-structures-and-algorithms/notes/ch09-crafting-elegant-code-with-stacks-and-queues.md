# Chapter 9: Crafting Elegant Code with Stacks and Queues (스택과 큐로 간결한 코드 생성)

## 핵심 질문

배열에서 기능을 "빼기만 한" 자료 구조가 왜 존재하는가? 제약이 어떻게 버그를 막고 코드를 읽기 쉽게 만드는가? 임시 데이터는 어떤 순서로 처리해야 하는가?

---

## 1. 속도가 아닌 간결함을 주는 자료 구조

지금까지의 자료 구조 논의는 연산 성능 중심이었지만, 자료 구조는 **더 간단하고 읽기 쉬운 코드**를 만드는 데도 기여한다. 스택과 큐는 완전히 새로운 구조가 아니라 **제약을 갖는 배열**일 뿐인데, 바로 그 제약 덕분에 간결해진다.

둘의 전문 분야는 **임시 데이터** 처리다 - 식당 주문처럼 처리 후에는 의미가 없어 버려도 되는 데이터. 핵심은 **처리 순서**다.

## 2. 스택 - LIFO

**스택(*stack - 끝에서만 삽입·삭제·읽기가 가능한 원소 리스트*)**의 세 가지 제약:

- 데이터는 스택의 **끝에만 삽입**할 수 있다
- 데이터는 스택의 **끝에서만 삭제**할 수 있다
- 스택의 **마지막 원소만 읽을** 수 있다

접시 더미가 좋은 비유다 - 맨 위 접시만 보이고, 맨 위에만 얹거나 뺄 수 있다. 그래서 스택의 끝을 **위(top)**, 시작을 **밑(bottom)**이라 부른다. 삽입은 **푸시(push)**, 삭제는 **팝(pop)**이다.

스택의 동작 원리를 요약하는 두문자어가 **LIFO(Last In, First Out)** - 마지막에 푸시된 항목이 가장 먼저 팝된다. 항상 마지막에 교실에 들어와 가장 먼저 나가는 게으른 학생과 같다.

## 3. 추상 데이터 타입

대부분의 언어에 스택은 내장돼 있지 않다 - 구현은 사용자의 몫이다:

```typescript
class Stack<T> {
  private data: T[] = [];

  push(element: T): void {
    this.data.push(element);
  }
  pop(): T | undefined {
    return this.data.pop();
  }
  read(): T | undefined {
    return this.data[this.data.length - 1];
  }
}
```

배열을 감싸되 **인터페이스를 제한**했다 - 원래 배열은 아무 인덱스나 읽을 수 있지만, 이 클래스를 통하면 마지막 항목만 읽을 수 있다.

> **핵심 통찰**: 스택은 특정 데이터 구조가 아니라 **규칙의 집합**이다. 내부가 배열이든 뭐든 LIFO로 동작하는 리스트면 스택이다. 이런 구조를 **추상 데이터 타입(*abstract data type - 내장 데이터 구조 위에 이론적 규칙 집합으로 정의되는 자료 구조*)**이라 부른다. Ch1의 집합도, 앞으로 나올 많은 자료 구조(우선순위 큐 등)도 추상 데이터 타입이다.

## 4. 스택 다뤄보기 - 괄호 린터

JavaScript **린터**(코드 문법 검사기)의 괄호 검사 부분을 만들어 보자. 괄호 문법 오류는 세 타입이다:

1. **타입 1**: 여는 괄호에 대응하는 닫는 괄호가 없음 - `(var x = 2;`
2. **타입 2**: 여는 괄호 없이 닫는 괄호가 나옴 - `var x = 2;)`
3. **타입 3**: 닫는 괄호가 직전에 열린 괄호와 종류가 다름 - `(var x = [1, 2, 3)];`

스택 기반 알고리즘: 문자를 왼쪽부터 읽으며 -

1. 괄호가 아닌 문자는 무시
2. **여는 괄호 → 푸시** ("닫히기를 기다리는 괄호"로 등록)
3. **닫는 괄호 → 팝해서 대조**: 종류가 다르면 타입 3 오류, 스택이 비어 팝할 게 없으면 타입 2 오류, 일치하면 계속
4. 줄 끝에서 **스택에 괄호가 남아 있으면** 타입 1 오류

`(var x = {y: [1, 2, 3]})`를 처리하면 `(`, `{`, `[`가 차례로 쌓였다가 `]`, `}`, `)`에서 차례로 팝되며 전부 일치 - 오류 없음. **가장 나중에 열린 괄호가 가장 먼저 닫혀야 한다**는 문제의 구조가 정확히 LIFO다.

```typescript
class Linter {
  private stack = new Stack<string>();

  lint(text: string): string | true {
    for (const char of text) {
      if (this.isOpeningBrace(char)) {
        this.stack.push(char);
      } else if (this.isClosingBrace(char)) {
        const poppedOpeningBrace = this.stack.pop();
        if (!poppedOpeningBrace) {
          return `${char} doesn't have opening brace`;   // 타입 2
        }
        if (this.isNotAMatch(poppedOpeningBrace, char)) {
          return `${char} has mismatched opening brace`; // 타입 3
        }
      }
    }
    if (this.stack.read()) {
      return `${this.stack.read()} does not have closing brace`; // 타입 1
    }
    return true;
  }

  private isOpeningBrace(char: string): boolean {
    return ["(", "[", "{"].includes(char);
  }
  private isClosingBrace(char: string): boolean {
    return [")", "]", "}"].includes(char);
  }
  private isNotAMatch(openingBrace: string, closingBrace: string): boolean {
    return closingBrace !== ({ "(": ")", "[": "]", "{": "}" } as const)[openingBrace];
  }
}
```

## 5. 제약을 갖는 데이터 구조의 중요성

스택이 제약 있는 배열일 뿐이라면 그냥 배열을 쓰면 안 될까? 제약이 중요한 이유 두 가지:

1. **잠재적 버그 방지**: 린터 알고리즘은 위에서만 제거해야 동작한다. 배열이라면 실수로 중간에서 삭제하는 코드가 들어올 수 있지만, 스택은 그것을 **원천적으로 불가능**하게 만든다
2. **새로운 사고 모델 제공**: 스택은 LIFO 프로세스라는 사고의 틀을 준다. 코드에서 스택을 발견한 다른 개발자는 그 즉시 "LIFO 기반 프로세스"임을 읽어낸다 - 익숙하고 명쾌하게 읽히는 코드가 된다

스택 활용 예: 워드 프로세서의 **되돌리기(undo)** - 키스트로크를 푸시해 두고, 되돌리기를 누르면 가장 최근 것부터 팝한다.

## 6. 큐 - FIFO

**큐(*queue - 끝에서 삽입하고 앞에서 삭제하는, 순서 보존형 임시 데이터 구조*)**는 스택과 비슷하지만 처리 순서가 반대다. 극장 줄과 같다 - 맨 앞 사람이 먼저 입장한다. **FIFO(First In, First Out)**. 큐의 시작을 **앞(front)**, 끝을 **뒤(back)**라 부른다.

세 가지 제약(스택과 대비):

- 데이터는 큐의 **끝에만 삽입** (스택과 동일) - **인큐(enqueue)**
- 데이터는 큐의 **앞에서만 삭제** (스택과 정반대) - **디큐(dequeue)**
- 큐의 **앞 원소만 읽기** 가능 (스택과 정반대)

```typescript
class Queue<T> {
  private data: T[] = [];

  enqueue(element: T): void {
    this.data.push(element);
  }
  dequeue(): T | undefined {
    return this.data.shift();  // 첫 원소를 제거해 반환
  }
  read(): T | undefined {
    return this.data[0];
  }
}
```

### 6.1 큐 다뤄보기 - 출력 잡 관리자

네트워크의 여러 컴퓨터에서 출력 요청을 받아 **요청받은 순서대로** 출력하는 프린터 인터페이스:

```typescript
class PrintManager {
  private queue = new Queue<string>();

  queuePrintJob(document: string): void {
    this.queue.enqueue(document);
  }
  run(): void {
    while (this.queue.read()) {
      this.print(this.queue.dequeue()!);  // 디큐하며 순서대로 출력
    }
  }
  private print(document: string): void {
    console.log(document);
  }
}
```

큐는 요청 순서를 보존하므로 **비동기 요청 처리**의 완벽한 도구이며, 이륙 대기 비행기·진료 대기 환자처럼 정해진 순서로 이벤트가 발생하는 실세계 모델링에도 흔히 쓰인다.

---

## 요약

- 스택·큐 = **제약을 갖는 배열**. 제약이 (1) 버그를 원천 차단하고 (2) LIFO/FIFO라는 사고 모델·가독성을 제공한다
- **스택 = LIFO** (푸시/팝, 위에서만): 괄호 린터, 되돌리기 기능 - "가장 최근 것부터 처리"
- **큐 = FIFO** (인큐는 뒤, 디큐는 앞): 출력 잡, 백그라운드 워커 - "들어온 순서대로 처리"
- 둘 다 **추상 데이터 타입**: 내부 구현이 아니라 규칙 집합으로 정의된다
- 임시 데이터 처리의 핵심 질문은 "**어떤 순서로 처리할 것인가**"다

## 연습 문제 (해답 예시)

1. **콜센터 대기 시스템에는 스택과 큐 중 무엇을?** - **큐.** 먼저 전화 건 사람부터 순서대로 연결해야 한다(FIFO).
2. **1~6을 순서대로 푸시 후 두 번 팝하면 읽히는 값은?** - **4.** (6, 5가 팝되고 맨 위는 4)
3. **1~6을 순서대로 인큐 후 두 번 디큐하면 읽히는 값은?** - **3.** (1, 2가 디큐되고 맨 앞은 3)
4. **스택으로 문자열 뒤집기** - 문자열의 각 문자를 스택에 푸시한 뒤, 스택이 빌 때까지 팝하며 새 문자열에 이어 붙인다. LIFO 순서가 곧 역순이다.

   ```typescript
   function reverse(string: string): string {
     const stack = new Stack<string>();
     for (const char of string) {
       stack.push(char);
     }
     let newString = "";
     while (stack.read()) {
       newString += stack.pop();
     }
     return newString;
   }
   ```

## 다른 챕터와의 관계

- **Ch1 (자료 구조가 중요한 까닭)**: 집합의 "중복 금지"에 이어, 제약이 자료 구조의 정체성을 만든다는 주제가 심화됐다
- **Ch10 (재귀)**: 컴퓨터가 재귀 함수 호출을 추적하는 **호출 스택**이 바로 이 장의 스택이다
- **Ch16 (힙)**: 큐에 "우선순위" 규칙을 더한 우선순위 큐가 등장하고, 힙이 그 구현체가 된다
- **Ch18 (그래프)**: 너비 우선 탐색(BFS)이 큐를, 깊이 우선 탐색(DFS)이 스택(재귀)을 사용한다
