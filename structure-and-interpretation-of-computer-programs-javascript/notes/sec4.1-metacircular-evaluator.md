# Section 4.1: The Metacircular Evaluator (메타순환 평가기)

## 핵심 질문

프로그래밍 언어를 **그 언어 자체로** 구현한다는 것은 무엇을 의미하며, 이를 통해 프로그래밍 언어의 본질에 대해 무엇을 알 수 있는가?

---

## 핵심 개념

| 개념 | 정의 |
|------|------|
| **메타순환 평가기(Metacircular evaluator)** | 평가 대상 언어와 구현 언어가 동일한 인터프리터 |
| **evaluate** | 환경에서 표현식을 평가하는 함수 — 평가기의 핵심 |
| **apply** | 함수를 인수에 적용하는 함수 — evaluate와 상호 재귀 |
| **구문 추상화(Syntactic abstraction)** | 표현식의 구조를 분석하는 함수들 |

---

## 1. 평가기의 핵심 구조: evaluate와 apply

### 1.1 evaluate

환경에서 표현식을 평가한다. 표현식의 유형에 따라 분기한다:

```javascript
function evaluate(component, env) {
    return is_literal(component)
           ? literal_value(component)
           : is_name(component)
             ? lookup_symbol_value(symbol_of_name(component), env)
             : is_application(component)
               ? apply(evaluate(function_expression(component), env),
                       list_of_values(arg_expressions(component), env))
               : is_operator_combination(component)
                 ? evaluate(operator_combination_to_application(component), env)
                 : is_conditional(component)
                   ? eval_conditional(component, env)
                   : is_lambda_expression(component)
                     ? make_function(
                           lambda_parameter_symbols(component),
                           lambda_body(component),
                           env)
                     : is_sequence(component)
                       ? eval_sequence(sequence_statements(component), env)
                       : is_block(component)
                         ? eval_block(component, env)
                         : is_return_statement(component)
                           ? eval_return_statement(component, env)
                           : is_declaration(component)
                             ? eval_declaration(component, env)
                             : is_assignment(component)
                               ? eval_assignment(component, env)
                               : error(component, "unknown component type");
}
```

### 1.2 apply

함수를 인수에 적용한다:

```javascript
function apply(fun, args) {
    if (is_primitive_function(fun)) {
        return apply_primitive_function(fun, args);
    } else if (is_compound_function(fun)) {
        const result = evaluate(
                           function_body(fun),
                           extend_environment(
                               function_parameters(fun),
                               args,
                               function_environment(fun)));
        return is_return_value(result)
               ? return_value_content(result)
               : undefined;
    } else {
        error(fun, "unknown function type -- apply");
    }
}
```

### 1.3 evaluate-apply 순환

```
evaluate(표현식, 환경)
    ↓ 함수 적용인 경우
apply(함수, 인수)
    ↓ 복합 함수인 경우
evaluate(함수 본문, 확장된 환경)
    ↓ ...
```

이 두 함수의 **상호 재귀**가 프로그래밍 언어의 의미를 완전히 정의한다.

> **핵심 통찰**: evaluate-apply 순환은 SICP 전체에서 가장 중요한 그림이다. 모든 프로그래밍 언어의 핵심은 이 순환에 있다 — 표현식을 평가하고, 함수를 적용하고, 그 과정에서 다시 표현식을 평가하는 끝없는 순환. 이 구조를 이해하면 어떤 프로그래밍 언어든 구현할 수 있다.

---

## 2. 환경 구현

### 2.1 프레임과 환경

Section 3.2의 환경 모델이 코드로 구현된다:

```javascript
function extend_environment(symbols, vals, base_env) {
    return pair(make_frame(symbols, vals), base_env);
}

function lookup_symbol_value(symbol, env) {
    // 환경 체인을 따라 올라가며 바인딩 탐색
}

function assign_symbol_value(symbol, val, env) {
    // 바인딩을 찾아 값 변경
}
```

---

## 3. 구문 추상화 (Syntactic Abstraction)

### 3.1 표현식 분석 함수들

`evaluate`가 표현식의 **유형을 판별**하고 **구성 요소를 추출**하는 함수들:

```javascript
function is_literal(component) { ... }
function literal_value(component) { ... }
function is_name(component) { ... }
function symbol_of_name(component) { ... }
function is_application(component) { ... }
function function_expression(component) { ... }
function arg_expressions(component) { ... }
// ...
```

이 함수들이 **구문 추상화 장벽**을 형성한다. `evaluate`는 표현식의 구체적 표현(파싱 결과의 형태)에 의존하지 않는다.

> **핵심 통찰**: Section 2.3의 `deriv`(기호 미분)와 `evaluate`는 놀랍도록 유사한 구조를 가진다. 둘 다 표현식의 유형에 따라 분기하고, 재귀적으로 하위 표현식을 처리한다. `deriv`는 수학적 표현식을 미분하고, `evaluate`는 프로그램 표현식을 실행한다. 패턴은 동일하다.

---

## 4. 평가기의 확장

### 4.1 데이터로서의 프로그램 (Programs as Data)

메타순환 평가기의 가장 심오한 통찰: **프로그램은 데이터 구조**이며, 다른 프로그램이 조작할 수 있다. `evaluate`는 프로그램(데이터)을 입력받아 그 의미(실행 결과)를 산출하는 함수일 뿐이다.

### 4.2 분석과 실행의 분리

`evaluate`를 두 단계로 나눌 수 있다:
1. **분석(Analysis)**: 표현식의 구조를 분석 — 환경에 독립적
2. **실행(Execution)**: 분석 결과를 환경에서 실행

```javascript
function analyze(component) {
    return is_literal(component)
           ? env => literal_value(component)
           : is_name(component)
             ? env => lookup_symbol_value(symbol_of_name(component), env)
             : is_application(component)
               ? analyze_application(component)
               : // ...
}
```

같은 함수를 여러 번 호출할 때, 분석은 한 번만 수행하고 실행만 반복하므로 효율적이다.

---

## 주요 예제

### JavaScript로 JavaScript 인터프리터 구현

이 섹션 전체가 하나의 거대한 예제다. 약 300줄의 JavaScript 코드로 JavaScript의 핵심 기능을 갖춘 인터프리터를 구현한다:

- 리터럴 평가, 이름 탐색
- 함수 선언과 적용
- 조건 표현식
- 시퀀스와 블록
- 상수/변수 선언
- 대입

이 인터프리터 위에서 팩토리얼, 피보나치, 제곱근 등 Chapter 1~3의 모든 예제를 실행할 수 있다.

---

## 요약

- **메타순환 평가기**는 JavaScript로 구현한 JavaScript 인터프리터다.
- **evaluate**와 **apply**의 상호 재귀가 언어의 의미를 완전히 정의한다.
- **구문 추상화**는 표현식의 구체적 형태와 평가 로직을 분리한다.
- 프로그램은 **데이터 구조**이며, 다른 프로그램이 조작할 수 있다.
- 분석과 실행을 분리하면 같은 코드의 반복 실행이 효율적이 된다.

---

## 다른 섹션과의 관계

- **Section 1.1 (The Elements of Programming)**: 평가 규칙이 `evaluate`로 코드화된다. 특수 형식의 목록이 `evaluate`의 조건 분기가 된다.
- **Section 2.3 (Symbolic Data)**: `deriv`와 `evaluate`의 구조적 유사성. 표현식 조작의 확장.
- **Section 3.2 (The Environment Model)**: 환경 모델이 `extend_environment`, `lookup_symbol_value`로 구현된다.
- **Section 4.2 (Lazy Evaluation)**: `evaluate`를 약간 수정하면 지연 평가 인터프리터가 된다.
- **Section 4.3 (Nondeterministic Computing)**: `evaluate`에 비결정적 선택을 추가한다.
- **Section 5.4 (Explicit-Control Evaluator)**: `evaluate`를 레지스터 머신으로 번역한다.
