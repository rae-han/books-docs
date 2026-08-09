# Section 5.4: The Explicit-Control Evaluator (명시적 제어 평가기)

## 핵심 질문

Section 4.1의 메타순환 평가기를 **레지스터 머신**으로 번역하면, 프로그래밍 언어가 실제 하드웨어 위에서 어떻게 실행되는지를 이해할 수 있는가?

---

## 핵심 개념

| 개념 | 정의 |
|------|------|
| **명시적 제어 평가기** | 메타순환 평가기를 레지스터 머신으로 구현한 것 |
| **꼬리 재귀 구현** | 꼬리 위치의 함수 호출이 스택을 소비하지 않도록 하는 구현 |
| **eval-apply 레지스터 머신** | evaluate와 apply의 상호 재귀를 go_to로 구현한 머신 |

---

## 1. 구조

### 1.1 주요 레지스터

| 레지스터 | 역할 |
|----------|------|
| `comp` | 현재 평가 중인 표현식(component) |
| `env` | 현재 환경 |
| `val` | 평가 결과 값 |
| `continue` | 복귀 주소 |
| `fun` | 적용할 함수 |
| `argl` | 인수 리스트 |

### 1.2 evaluate의 레지스터 머신 번역

```
"eval_dispatch",
    test(list(op("is_literal"), reg("comp"))),
    branch(label("ev_literal")),
    test(list(op("is_name"), reg("comp"))),
    branch(label("ev_name")),
    test(list(op("is_application"), reg("comp"))),
    branch(label("ev_application")),
    // ... 각 표현식 유형별 분기
```

Section 4.1의 `evaluate` 함수의 `if-else` 체인이 `test`/`branch` 명령으로 변환된다.

### 1.3 apply의 레지스터 머신 번역

함수 적용:
1. 원시 함수 → 직접 실행
2. 복합 함수 → 새 환경 생성, 본문 평가

```
"apply_dispatch",
    test(list(op("is_primitive_function"), reg("fun"))),
    branch(label("primitive_apply")),
    test(list(op("is_compound_function"), reg("fun"))),
    branch(label("compound_apply")),
    go_to(label("unknown_function_type")),
```

---

## 2. 꼬리 재귀 구현

### 2.1 핵심 최적화

꼬리 위치의 함수 호출에서 **`continue`를 스택에 저장하지 않는다**:

```
// 꼬리 호출이 아닌 경우:
save("continue"),          // 스택에 저장
assign("continue", label("after_call")),
go_to(label("eval_dispatch")),

// 꼬리 호출인 경우:
// save("continue") 없이!
go_to(label("eval_dispatch")),
// 현재의 continue를 그대로 사용
```

이렇게 하면 `fact_iter` 같은 꼬리 재귀 함수가 **Θ(1) 스택 공간**에서 실행된다.

> **핵심 통찰**: Section 1.2에서 "반복적 프로세스는 Θ(1) 공간"이라고 했던 것이 여기서 구현 수준에서 증명된다. 꼬리 호출에서 스택 프레임을 재사용하면, 재귀 함수가 무한 루프처럼 상수 공간에서 실행될 수 있다. 이것이 **꼬리 호출 최적화(TCO)** 의 본질이다.

---

## 3. 전체 그림

명시적 제어 평가기를 통해 SICP의 추상화 탑이 완성된다:

```
Chapter 1-3: JavaScript 프로그램
        ↓ (메타순환 평가기가 해석)
Chapter 4:   evaluate/apply 함수
        ↓ (레지스터 머신으로 번역)
Chapter 5:   레지스터 머신 명령
        ↓ (시뮬레이터가 실행 / 실제 하드웨어가 실행)
             물리적 회로
```

---

## 요약

- **명시적 제어 평가기**는 메타순환 평가기를 레지스터 머신으로 번역한 것이다.
- `evaluate`의 조건 분기 → `test`/`branch`, 재귀 호출 → `save`/`restore` + `go_to`.
- **꼬리 재귀 최적화**: 꼬리 위치에서 `continue`를 스택에 저장하지 않으면 Θ(1) 공간.
- 이 평가기는 JavaScript가 실제 프로세서 위에서 어떻게 실행되는지의 모델이다.

---

## 다른 섹션과의 관계

- **Section 4.1 (Metacircular Evaluator)**: 직접적인 번역 원본. 구조가 거의 1:1 대응.
- **Section 1.2 (Functions and the Processes They Generate)**: 꼬리 재귀 최적화가 여기서 구현.
- **Section 5.1 (Register Machines)**: 레지스터 머신 설계 원리가 적용된다.
- **Section 5.5 (Compilation)**: 평가기 대신 **컴파일러**로 더 효율적인 코드를 생성한다.
