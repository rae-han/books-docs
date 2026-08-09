# Section 5.5: Compilation (컴파일)

## 핵심 질문

인터프리터가 프로그램을 **실행할 때마다** 분석하는 반면, 컴파일러는 프로그램을 **미리** 기계 코드로 번역한다. 이 차이가 어떤 성능 이점을 가져오며, 컴파일러는 어떻게 구현하는가?

---

## 핵심 개념

| 개념 | 정의 |
|------|------|
| **컴파일러(Compiler)** | 소스 프로그램을 타깃 언어(기계어)로 번역하는 프로그램 |
| **인터프리터 vs 컴파일러** | 실행 시 분석 vs 미리 번역 |
| **명령 시퀀스(Instruction sequence)** | 컴파일러가 생성하는 레지스터 머신 명령의 리스트 |
| **레지스터 사용 분석** | 명령 시퀀스가 필요로 하는(needed) / 수정하는(modified) 레지스터 추적 |
| **연결 코드(Linkage)** | 컴파일된 코드 실행 후 어디로 가야 하는지 지정 |

---

## 1. 인터프리터 vs 컴파일러

### 1.1 핵심 차이

| 인터프리터 (Section 5.4) | 컴파일러 (Section 5.5) |
|--------------------------|----------------------|
| 실행 시 표현식 유형 분석 | 컴파일 시 분석 완료 |
| 매 실행마다 분석 반복 | 분석은 한 번만 |
| 범용 디스패치 오버헤드 | 직접 코드로 변환 |
| 유연함 (대화형 개발) | 빠름 (미리 최적화) |

### 1.2 컴파일러의 구조

```javascript
function compile(component, target, linkage) {
    return is_literal(component)
           ? compile_literal(component, target, linkage)
           : is_name(component)
             ? compile_name(component, target, linkage)
             : is_application(component)
               ? compile_application(component, target, linkage)
               : is_conditional(component)
                 ? compile_conditional(component, target, linkage)
                 : is_lambda_expression(component)
                   ? compile_lambda(component, target, linkage)
                   : is_sequence(component)
                     ? compile_sequence(component, target, linkage)
                     : // ...
}
```

Section 4.1의 `evaluate`와 거의 동일한 구조! 차이는 **값을 계산하는 대신** 값을 계산하는 **명령을 생성**한다는 것이다.

---

## 2. 컴파일러가 생성하는 코드

### 2.1 리터럴 컴파일

```javascript
compile(parse("5"), "val", "next");
// → assign("val", constant(5))
```

### 2.2 함수 적용 컴파일

```javascript
compile(parse("f(1, 2)"), "val", "next");
// →
//   1. f를 평가하여 fun에 저장
//   2. 1을 평가하여 argl에 추가
//   3. 2를 평가하여 argl에 추가
//   4. fun을 argl에 적용하여 val에 저장
```

인터프리터와 달리, 표현식 유형 분석(`is_literal?`, `is_application?`)이 **실행 시가 아니라 컴파일 시**에 수행된다.

---

## 3. 레지스터 사용 최적화

### 3.1 불필요한 save/restore 제거

인터프리터는 보수적으로 모든 레지스터를 저장/복원한다. 컴파일러는 **실제로 필요한 경우만** 저장한다:

```
// 인터프리터: 항상 save/restore
save("env"),
save("continue"),
// ...
restore("continue"),
restore("env"),

// 컴파일러: 분석 후 불필요하면 제거
// env가 변경되지 않는다면 save/restore 생략
```

이것이 컴파일된 코드가 더 빠른 주된 이유 중 하나다.

---

## 4. 컴파일과 인터프리팅의 통합

### 4.1 인터프리터에서 컴파일된 코드 호출

컴파일된 코드와 인터프리트되는 코드가 **같은 레지스터 머신**에서 실행되므로 혼합이 가능하다:

- 컴파일된 함수가 인터프리트되는 함수를 호출 가능
- 인터프리트되는 코드가 컴파일된 함수를 호출 가능

이를 통해 **대화형 개발의 유연성**과 **컴파일의 효율성**을 동시에 얻을 수 있다.

> **핵심 통찰**: SICP의 마지막 섹션은 책 전체의 주제를 극적으로 완성한다. Chapter 1에서 시작한 "추상화의 탑"이 여기서 완전체가 된다: JavaScript 프로그램 → 메타순환 평가기 → 레지스터 머신 → 컴파일러 → 기계어. 그리고 이 모든 것을 **같은 언어(JavaScript)** 로 기술할 수 있다는 것이 핵심이다. 프로그래밍 언어는 사고를 위한 도구이면서 동시에 사고의 대상이다.

---

## 주요 예제

### 팩토리얼의 컴파일된 코드

```javascript
compile(parse("function factorial(n) { return n === 1 ? 1 : n * factorial(n - 1); }"),
        "val", "next");
```

생성되는 레지스터 머신 코드는 Section 5.4의 명시적 제어 평가기가 같은 프로그램을 실행할 때보다 상당히 짧다. 표현식 유형 분석, 환경 조회의 오버헤드가 제거되었기 때문이다.

---

## 요약

- **컴파일러**는 소스 프로그램을 레지스터 머신 코드로 미리 번역하여, 실행 시 분석 오버헤드를 제거한다.
- 컴파일러의 구조는 `evaluate`와 거의 동일하지만, **값 대신 명령을 생성**한다.
- **레지스터 사용 분석**으로 불필요한 save/restore를 제거하여 코드를 최적화한다.
- 컴파일된 코드와 인터프리트되는 코드를 **혼합 실행**할 수 있어, 유연성과 효율성을 동시에 얻는다.
- SICP 전체의 추상화 탑이 이 섹션에서 완성된다.

---

## 다른 섹션과의 관계

- **Section 4.1 (Metacircular Evaluator)**: 컴파일러와 동일한 구조. 차이는 값을 계산하느냐 코드를 생성하느냐.
- **Section 5.4 (Explicit-Control Evaluator)**: 컴파일된 코드의 타깃이 되는 레지스터 머신. 인터프리터 vs 컴파일러의 성능 비교 기준.
- **Section 5.2 (Register-Machine Simulator)**: 컴파일된 코드를 시뮬레이터에서 실행할 수 있다.
- **Section 5.3 (Storage Allocation and GC)**: 컴파일된 코드도 GC가 필요하다.
- **Section 1.1 ~ 5.4 (전체)**: SICP의 여정이 여기서 완성. 추상화의 가장 높은 수준(언어 설계)에서 가장 낮은 수준(기계어)까지 관통한다.
