# Section 5.2: A Register-Machine Simulator (레지스터 머신 시뮬레이터)

## 핵심 질문

Section 5.1에서 설계한 레지스터 머신을 **JavaScript 프로그램**으로 시뮬레이션할 수 있는가? 기계의 동작을 소프트웨어로 재현한다는 것은 무엇을 의미하는가?

---

## 핵심 개념

| 개념 | 정의 |
|------|------|
| **머신 모델(Machine model)** | 레지스터, 스택, 명령 시퀀스를 데이터 구조로 표현한 것 |
| **명령 실행 함수(Instruction execution procedure)** | 각 명령을 시뮬레이션하는 JavaScript 함수 |
| **어셈블러(Assembler)** | 컨트롤러 텍스트를 실행 가능한 명령 시퀀스로 변환 |

---

## 1. 시뮬레이터 구조

### 1.1 머신 만들기

```javascript
function make_machine(register_names, ops, controller_text) {
    const machine = make_new_machine();
    // 레지스터 할당
    for_each(name => machine("allocate_register")(name), register_names);
    // 연산 설치
    machine("install_operations")(ops);
    // 컨트롤러 어셈블
    machine("install_instruction_sequence")(assemble(controller_text, machine));
    return machine;
}
```

### 1.2 머신 객체

머신은 **메시지 전달** 스타일로 구현된다 (Section 2.4의 패턴):

```javascript
function make_new_machine() {
    let pc = make_register("pc");     // 프로그램 카운터
    let flag = make_register("flag"); // 테스트 결과
    let stack = make_stack();
    let the_instruction_sequence = null;
    // ...
    function dispatch(message) {
        return message === "start"
               ? // 실행 시작
               : message === "get_register"
                 ? // 레지스터 접근
                 : // ...
    }
    return dispatch;
}
```

### 1.3 명령 실행

각 명령 유형(assign, test, branch, go_to, save, restore)에 대한 실행 함수:

```javascript
function make_assign(inst, machine, labels, operations, pc) {
    const target = get_register(machine, assign_reg_name(inst));
    const value_exp = assign_value_exp(inst);
    const value_fun = // value_exp를 계산하는 함수
    return () => {
               set_contents(target, value_fun());
               advance_pc(pc);
           };
}
```

---

## 2. 어셈블러 (Assembler)

### 2.1 역할

컨트롤러 텍스트(기호적 명령)를 **실행 가능한 함수의 리스트**로 변환한다. 레이블을 주소로 해석하고, 레지스터와 연산에 대한 참조를 해결한다.

---

## 3. 모니터링

시뮬레이터에 통계 수집 기능을 추가할 수 있다:

- 실행된 명령 수
- 스택의 최대 깊이
- 레지스터 접근 횟수

> **핵심 통찰**: 시뮬레이터는 Chapter 4의 메타순환 평가기와 유사한 구조를 가진다. 메타순환 평가기는 "JavaScript 프로그램을 해석하는 JavaScript 프로그램"이었고, 시뮬레이터는 "레지스터 머신을 해석하는 JavaScript 프로그램"이다. 한 수준의 추상화가 다른 수준의 추상화를 구현하는 패턴이 반복된다.

---

## 요약

- **레지스터 머신 시뮬레이터**는 Section 5.1의 추상 머신을 JavaScript 프로그램으로 실행한다.
- 시뮬레이터는 **메시지 전달** 스타일로 구현되며, 어셈블러가 명령을 실행 함수로 변환한다.
- 모니터링 기능으로 명령 실행 횟수, 스택 깊이 등을 추적할 수 있다.
- 시뮬레이터 구현 자체가 Chapter 2~4의 기법(데이터 추상화, 메시지 전달, 기호 처리)의 종합적 적용이다.

---

## 다른 섹션과의 관계

- **Section 2.4 (Multiple Representations)**: 머신이 메시지 전달 스타일로 구현된다.
- **Section 4.1 (Metacircular Evaluator)**: 시뮬레이터와 구조적으로 유사하다.
- **Section 5.1 (Register Machines)**: 시뮬레이션 대상이 되는 머신 설계.
- **Section 5.4 (Explicit-Control Evaluator)**: 이 시뮬레이터 위에서 실행된다.
