# Section 5.1: Designing Register Machines (레지스터 머신 설계)

## 핵심 질문

Chapter 1~4에서 다룬 함수, 재귀, 인터프리터를 실제 하드웨어에 가까운 수준에서 실행하려면 어떤 **기계(machine)** 를 설계해야 하는가?

---

## 핵심 개념

| 개념 | 정의 |
|------|------|
| **레지스터 머신(Register machine)** | 레지스터, 연산, 컨트롤러로 구성된 추상적 계산 장치 |
| **레지스터(Register)** | 하나의 값을 저장하는 저장 공간 |
| **컨트롤러(Controller)** | 명령 시퀀스를 순서대로 실행하는 제어 장치 |
| **데이터 경로(Data path)** | 레지스터와 연산 사이의 데이터 흐름 |
| **스택(Stack)** | 재귀 구현을 위한 LIFO 저장소 |

---

## 1. 레지스터 머신의 구조

### 1.1 기본 구성 요소

레지스터 머신은 세 요소로 구성된다:

1. **레지스터**: 값을 저장 — `val`, `continue`, `n` 등
2. **연산**: 레지스터의 값을 조합하여 새 값을 생성 — `+`, `*`, `=` 등
3. **컨트롤러**: 명령(assign, test, branch, goto)을 순서대로 실행

### 1.2 GCD 머신

유클리드 알고리즘을 레지스터 머신으로:

```
controller(
    "test_b",
    test(list(op("="), reg("b"), constant(0))),
    branch(label("gcd_done")),
    assign("t", list(op("remainder"), reg("a"), reg("b"))),
    assign("a", reg("b")),
    assign("b", reg("t")),
    go_to(label("test_b")),
    "gcd_done"
)
```

이 머신은 두 레지스터(`a`, `b`)와 보조 레지스터(`t`)만으로 GCD를 계산한다.

---

## 2. 재귀를 위한 스택

### 2.1 팩토리얼 머신

재귀적 팩토리얼은 **스택**이 필요하다. 재귀 호출 전에 현재 상태를 스택에 저장하고, 복귀 후 복원한다:

```
controller(
    assign("continue", label("fact_done")),
    "fact_loop",
    test(list(op("="), reg("n"), constant(1))),
    branch(label("base_case")),
    save("continue"),
    save("n"),
    assign("n", list(op("-"), reg("n"), constant(1))),
    assign("continue", label("after_fact")),
    go_to(label("fact_loop")),
    "after_fact",
    restore("n"),
    restore("continue"),
    assign("val", list(op("*"), reg("n"), reg("val"))),
    go_to(reg("continue")),
    "base_case",
    assign("val", constant(1)),
    go_to(reg("continue")),
    "fact_done"
)
```

`continue` 레지스터가 "복귀 주소"를 담는다 — 함수 호출의 반환 주소에 해당한다.

> **핵심 통찰**: Chapter 1에서 분석한 "재귀적 프로세스는 Θ(n) 공간, 반복적 프로세스는 Θ(1) 공간"이 레지스터 머신에서 명확해진다. 재귀적 프로세스는 스택을 사용하고, 반복적 프로세스(꼬리 재귀)는 스택 없이 `go_to`만으로 구현된다.

---

## 3. 데이터 경로 다이어그램

레지스터 머신의 동작을 시각적으로 표현:

```
  ┌───┐     ┌───┐
  │ a │     │ b │
  └─┬─┘     └─┬─┘
    │    rem   │
    └───→◯←───┘
         │
    ┌────↓────┐
    │    t    │
    └─────────┘
```

화살표가 데이터 흐름, 원이 연산을 나타낸다.

---

## 요약

- **레지스터 머신**은 레지스터, 연산, 컨트롤러로 구성된 추상적 계산 장치다.
- **스택**은 재귀 구현에 필수적이며, `save`/`restore`로 상태를 보존/복원한다.
- **반복적 프로세스**(꼬리 재귀)는 스택 없이 구현 가능하다 — `go_to`만 사용.
- 레지스터 머신 설계는 Chapter 1의 프로세스 분석을 하드웨어 수준에서 검증한다.

---

## 다른 섹션과의 관계

- **Section 1.2 (Functions and the Processes They Generate)**: 재귀적/반복적 프로세스의 공간 복잡도가 스택 사용으로 설명된다.
- **Section 5.2 (Register-Machine Simulator)**: 이 섹션에서 설계한 머신을 JavaScript로 시뮬레이션한다.
- **Section 5.4 (Explicit-Control Evaluator)**: 메타순환 평가기를 레지스터 머신으로 번역한다.
