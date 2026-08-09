# Chapter 24: Jumps, Loops, and Calls (점프, 반복, 호출)

## 핵심 질문

> 프로그램의 실행 흐름을 바꾸는 점프, 반복, 서브루틴 호출은 어떻게 동작하며, 스택(stack)이 왜 필수적인가?

---

## 1. 순차 실행의 한계

Chapter 23의 CPU는 명령어를 주소 순서대로 실행한다 (PC가 매번 +1). 하지만 실제 프로그램에는:

- **조건 분기**: "만약 ~이면 A를 하고, 아니면 B를 하라" (if-else)
- **반복**: "~할 때까지 반복하라" (while, for)
- **코드 재사용**: "이 함수를 호출하라" (function call)

이 모든 것은 PC를 **임의의 주소로 변경**하는 능력이 필요하다.

---

## 2. 무조건 점프 (Unconditional Jump)

```
JUMP addr    ; PC ← addr
```

PC를 지정된 주소로 변경하여 다음 명령어를 그 주소에서 가져온다.

```
주소 00: LOAD  10
주소 02: ADD   11
주소 04: JUMP  00    ; ← 주소 00으로 돌아감 → 무한 루프!
```

이것만으로는 끝나지 않는 무한 루프가 된다. 탈출 조건이 필요하다 → 조건부 점프.

---

## 3. 조건부 점프 (Conditional Jump)

ALU의 **상태 플래그(Ch 21)**를 확인하여 점프 여부를 결정한다:

| 명령어 | 조건 | 의미 |
|--------|------|------|
| JZ addr | Zero = 1 | 결과가 0이면 점프 |
| JNZ addr | Zero = 0 | 결과가 0이 아니면 점프 |
| JC addr | Carry = 1 | 올림이 있으면 점프 |
| JN addr | Negative = 1 | 결과가 음수면 점프 |

### 3.1 if-else 구현

고급 언어의 `if (a == b) { X } else { Y }`:

```
      LOAD  a
      SUB   b         ; a - b 계산, 결과가 0이면 Z=1
      JZ    equal     ; Z=1이면 equal로 점프
      ; --- else 부분 (Y) ---
      ...
      JUMP  end
equal:
      ; --- if 부분 (X) ---
      ...
end:
      ; 계속
```

### 3.2 반복문 (Loop) 구현

고급 언어의 `for (i=10; i>0; i--) { ... }`:

```
      LOAD  #10       ; i = 10
      STORE counter
loop:
      ; --- 루프 본문 ---
      ...
      ; --- i 감소 ---
      LOAD  counter
      SUB   #1        ; i = i - 1
      STORE counter
      JNZ   loop      ; i ≠ 0이면 루프 반복
      ; i = 0이면 여기로 탈출
```

> **핵심 통찰**: 조건부 점프는 **컴퓨터를 범용 기계로 만드는 핵심 능력**이다. 순차 실행만으로는 단순 계산기에 불과하지만, 조건부 점프를 추가하면 어떤 알고리즘이든 구현할 수 있다. Alan Turing이 증명한 "범용 튜링 기계"의 핵심 요소 중 하나가 바로 조건 분기다.

---

## 4. 서브루틴과 호출 (Subroutine & Call)

### 4.1 문제

같은 코드 블록이 프로그램의 여러 곳에서 필요하다면? 복사-붙여넣기는 낭비이고 유지보수가 어렵다.

### 4.2 CALL과 RET

- **CALL addr**: 현재 PC를 저장하고, addr로 점프
- **RET (Return)**: 저장해둔 PC로 복귀

```
주소 00: ...
주소 02: CALL  20     ; PC(=04)를 저장, 주소 20으로 점프
주소 04: ...          ; ← RET 후 여기로 돌아옴
...
주소 20: ...          ; 서브루틴 시작
주소 22: ...
주소 24: RET          ; 저장된 PC(=04)로 복귀
```

### 4.3 중첩 호출 문제

서브루틴 A가 서브루틴 B를 호출하면? 리턴 주소가 2개 필요하다.

```
main:  CALL A     ; 리턴 주소 1 저장
A:     CALL B     ; 리턴 주소 2 저장
B:     RET        ; 리턴 주소 2로 복귀 (→ A)
A:     RET        ; 리턴 주소 1로 복귀 (→ main)
```

**가장 나중에 저장된 주소가 가장 먼저 필요하다** → LIFO(Last In, First Out) → **스택(Stack)**

---

## 5. 스택 (Stack)

### 5.1 스택이란?

**스택**은 LIFO(Last In, First Out) 구조의 메모리 영역이다:

```
PUSH: 스택 위에 쌓기      POP: 스택 위에서 꺼내기

│       │                │       │
│  [C]  │ ← 꼭대기       │       │
│  [B]  │                │  [B]  │ ← 새 꼭대기
│  [A]  │                │  [A]  │
└───────┘                └───────┘
  C를 POP                  C가 꺼내짐
```

> **Petzold의 비유**: 스택은 식당의 접시 더미와 같다. 접시를 올려놓고(PUSH) 꺼내는(POP) 것은 항상 맨 위에서만 한다. 가장 나중에 올린 접시를 가장 먼저 꺼낸다.

### 5.2 스택 포인터 (Stack Pointer, SP)

**SP 레지스터**가 스택의 현재 꼭대기 주소를 추적한다:

- **PUSH**: SP 감소 → 메모리[SP]에 값 저장
- **POP**: 메모리[SP]에서 값 읽음 → SP 증가

(스택은 보통 높은 주소에서 낮은 주소 방향으로 성장)

### 5.3 CALL과 RET의 실제 동작

```
CALL addr:
  1. SP = SP - 2 (또는 -1, 주소 크기에 따라)
  2. 메모리[SP] = PC (현재 PC = 리턴 주소)
  3. PC = addr (서브루틴으로 점프)

RET:
  1. PC = 메모리[SP] (리턴 주소 복원)
  2. SP = SP + 2 (스택에서 제거)
```

중첩 호출도 완벽하게 처리:

```
main → CALL A: 스택에 main리턴주소 PUSH
  A → CALL B: 스택에 A리턴주소 PUSH
    B → RET: A리턴주소 POP → A로 복귀
  A → RET: main리턴주소 POP → main으로 복귀
```

---

## 6. 하드웨어가 소프트웨어를 지원하는 방법

| 고급 언어 구조 | 기계어 구현 |
|---------------|-------------|
| if-else | CMP + 조건부 JUMP |
| while/for | CMP + 조건부 JUMP (역방향) |
| function call | CALL + RET + 스택 |
| return value | 누산기 또는 특정 레지스터에 저장 |
| local variables | 스택에 할당 |
| recursion | 스택의 LIFO 특성으로 자연스럽게 지원 |

> **핵심 통찰**: 고급 프로그래밍 언어의 모든 제어 구조(if, while, for, function)는 결국 **점프(JUMP), 조건부 점프, CALL, RET**이라는 기계어 명령어로 변환된다. 그리고 이 명령어들은 **PC를 변경하고 스택을 조작하는** 하드웨어 동작으로 환원된다.

---

## 요약

- **무조건 점프(JUMP)**: PC를 임의의 주소로 변경
- **조건부 점프**: ALU 플래그(Z, C, N, V)에 따라 점프 여부 결정 — if-else와 반복의 기초
- **서브루틴 호출(CALL/RET)**: 리턴 주소를 스택에 PUSH하고 서브루틴으로 점프. RET로 스택에서 POP하여 복귀
- **스택**: LIFO 구조. SP가 꼭대기를 추적. 중첩 호출과 재귀를 자연스럽게 지원
- 모든 고급 언어의 제어 구조는 이 기본 명령어들로 환원된다

## 다른 챕터와의 관계

- **← [Chapter 21: The Arithmetic Logic Unit](ch21-the-arithmetic-logic-unit.md)**: ALU 플래그가 조건부 점프의 기초
- **← [Chapter 23: CPU Control Signals](ch23-cpu-control-signals.md)**: JUMP, CALL 명령어의 페치-디코드-실행 과정
- **→ [Chapter 25: Peripherals](ch25-peripherals.md)**: 인터럽트도 스택을 사용하여 현재 상태를 저장
- **→ [Chapter 27: Coding](ch27-coding.md)**: 고급 언어의 if/while/function이 이 명령어들로 컴파일됨
