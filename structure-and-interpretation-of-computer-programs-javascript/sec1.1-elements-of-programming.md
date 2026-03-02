# Section 1.1: The Elements of Programming (프로그래밍의 요소)

## 핵심 질문

강력한 프로그래밍 언어가 갖추어야 할 근본적인 메커니즘은 무엇이며, 단순한 요소들로부터 어떻게 복잡한 프로그램을 구축하는가?

---

## 핵심 개념

| 개념 | 정의 |
|------|------|
| **원시 표현식(Primitive expressions)** | 언어가 다루는 가장 단순한 개체 — 숫자, 문자열, 기본 연산자 |
| **결합 수단(Means of combination)** | 단순한 요소로부터 복합 요소를 구성하는 방법 |
| **추상화 수단(Means of abstraction)** | 복합 요소에 이름을 붙여 단위로 조작하는 방법 |
| **치환 모델(Substitution model)** | 함수 적용을 이해하기 위한 사고 모델 — 매개변수를 인수 값으로 치환 |
| **적용 순서 평가(Applicative-order)** | 인수를 먼저 평가한 후 함수를 적용하는 방식 (JavaScript가 사용) |
| **정상 순서 평가(Normal-order)** | 표현식을 완전히 전개한 후 축소하는 방식 |
| **블록 구조(Block structure)** | 함수 내부에 함수를 정의하여 이름 공간을 관리하는 방식 |
| **렉시컬 스코핑(Lexical scoping)** | 자유 변수가 함수 정의 시점의 환경을 참조하는 규칙 |

---

## 1. 프로그래밍의 세 가지 메커니즘

프로그래밍 언어는 단순히 컴퓨터에게 작업을 지시하는 수단이 아니다. 그것은 **프로세스에 대한 우리의 아이디어를 조직화하는 프레임워크**다. 모든 강력한 프로그래밍 언어는 세 가지 메커니즘을 갖추어야 한다:

1. **원시 표현식(Primitive expressions)** — 언어가 다루는 가장 단순한 개체
2. **결합 수단(Means of combination)** — 단순한 요소로부터 복합 요소를 구성하는 방법
3. **추상화 수단(Means of abstraction)** — 복합 요소에 이름을 붙여 단위로 조작하는 방법

프로그래밍에서 다루는 두 가지 근본 요소가 있다:

- **데이터(Data)** — 조작하고자 하는 "것"
- **함수(Functions)** — 데이터를 조작하는 규칙의 기술

> **핵심 통찰**: 이 섹션에서는 데이터와 함수의 구분이 명확해 보이지만, Chapter 2에서 이 경계가 흐려지고, Chapter 4에서는 데이터로서의 프로그램(프로그램도 데이터다)이라는 개념이 등장한다. SICP 전체를 관통하는 주제 중 하나다.

---

## 2. 표현식 (Expressions)

### 2.1 원시 표현식

가장 단순한 표현식은 숫자다. 인터프리터에 숫자를 입력하면 그 값 자체를 반환한다:

```javascript
486;
// 486
```

### 2.2 연산자 조합 (Operator Combinations)

숫자와 연산자를 결합하여 **복합 표현식**을 만든다:

```javascript
137 + 349;    // 486
1000 - 334;   // 666
5 * 99;       // 495
10 / 4;       // 2.5
2.7 + 10;     // 12.7
```

JavaScript는 **중위 표기법(infix notation)** 을 사용한다 — 연산자가 피연산자 사이에 위치한다. 원서의 Scheme은 전위 표기법(*Prefix notation — `(+ 137 349)`처럼 연산자가 피연산자 앞에 오는 표기법. Lisp/Scheme의 특징이며, 가변 개수의 인수를 자연스럽게 지원한다.*)을 사용했다.

### 2.3 연산자 우선순위와 중첩

곱셈과 나눗셈은 덧셈과 뺄셈보다 우선순위가 높다. 같은 우선순위의 연산자는 **좌결합(left-associative)** 으로 평가된다. 괄호로 그룹화를 명시할 수 있다:

```javascript
3 * 5 + 10 / 2;                          // (3*5) + (10/2) = 20
3 * 2 * (3 - 5 + 4) + 27 / 6 * 10;      // 57
```

### 2.4 REPL

인터프리터는 **읽기-평가-출력 루프(Read-Eval-Print Loop, REPL)** 로 동작한다. 표현식을 입력하면 평가하여 결과를 출력하고, 다음 입력을 기다린다. 별도의 출력 명령이 필요 없다.

---

## 3. 이름 붙이기와 환경 (Naming and the Environment)

### 3.1 상수 선언

추상화의 가장 기본적인 형태는 **이름 붙이기**다. `const` 키워드로 값에 이름을 연결한다:

```javascript
const size = 2;
size;           // 2
5 * size;       // 10
```

이름을 사용하면 점진적으로 복잡한 프로그램을 구축할 수 있다:

```javascript
const pi = 3.14159;
const radius = 10;
pi * radius * radius;   // 314.159

const circumference = 2 * pi * radius;
circumference;          // 62.8318
```

### 3.2 환경 (Environment)

인터프리터는 이름-값 연결을 추적하는 메모리 구조를 유지한다. 이것을 **환경(environment)** 이라 부른다. `const size = 2;`는 환경에 `size → 2`라는 연결을 추가한다.

> **핵심 통찰**: 이름 붙이기는 가장 단순한 추상화 수단이지만, 그 효과는 강력하다. 환경이 없다면 인터프리터는 매번 같은 계산을 반복해야 하고, 프로그래머는 점진적으로 프로그램을 구성할 수 없다. 환경은 Section 3.2에서 **환경 모델**로 형식화되며, 프로그램의 의미를 정의하는 핵심 구조가 된다.

---

## 4. 연산자 조합의 평가 (Evaluating Operator Combinations)

### 4.1 평가 규칙

연산자 조합을 평가하는 규칙은 두 단계로 이루어진다:

1. 조합의 모든 **피연산자 표현식을 평가**한다
2. 연산자가 나타내는 **함수를 인수 값에 적용**한다

이 규칙 자체가 **재귀적(recursive)** 이다 — 피연산자가 또 다른 조합일 수 있으므로, 평가 규칙을 반복 적용해야 한다.

### 4.2 트리 축적 (Tree Accumulation)

`(2 + 4 * 6) * (3 + 12)` 같은 중첩된 조합의 평가 과정은 **트리**로 시각화할 수 있다:

```
              390
               |
               *
              / \
            26   15
            |     |
            +     +
           / \   / \
          2  24  3  12
              |
              *
             / \
            4   6
```

값이 말단 노드에서 위로 "스며올라가는" 이 과정을 **트리 축적(tree accumulation)** 이라 한다.

### 4.3 원시 표현식의 평가

재귀의 종료 조건으로서, 원시 표현식은 다음과 같이 평가된다:

- **숫자 리터럴**은 해당 숫자 값으로 평가된다
- **이름**은 환경에서 연결된 값으로 평가된다

### 4.4 특수 형식 (Special Forms)

`const x = 3;` 같은 **선언(declaration)** 은 일반 평가 규칙을 따르지 않는다. 이것은 `x`를 평가하여 그 값을 찾는 것이 아니라, `x`에 값 3을 **연결**하는 것이다. 이처럼 고유한 평가 규칙을 가진 구문을 **특수 형식(special form)** 이라 한다.

> **핵심 통찰**: 범용 평가 규칙과 특수 형식의 구분은 Chapter 4의 메타순환 평가기에서 핵심적인 역할을 한다. 평가기는 각 표현식의 유형을 판별하고, 일반 적용(apply)과 특수 형식을 구분하여 처리한다.

---

## 5. 복합 함수 (Compound Functions)

### 5.1 함수 선언

**함수 선언(function declaration)** 은 이름 붙이기보다 한 단계 높은 추상화 수단이다. 복합 연산에 이름을 부여하고, 그것을 하나의 단위로 다룰 수 있게 한다:

```javascript
function square(x) {
    return x * x;
}
```

일반 형식:

```javascript
function name(parameters) {
    return expression;
}
```

### 5.2 함수 적용

정의된 함수는 원시 연산처럼 사용할 수 있다:

```javascript
square(21);          // 441
square(2 + 5);       // 49
square(square(3));   // 81
```

### 5.3 함수의 조합

함수를 결합하여 더 복잡한 함수를 구성할 수 있다:

```javascript
function sum_of_squares(x, y) {
    return square(x) + square(y);
}

sum_of_squares(3, 4);   // 25
```

그리고 이것을 다시 다른 함수의 구성 요소로 사용한다:

```javascript
function f(a) {
    return sum_of_squares(a + 1, a * 2);
}

f(5);   // 136  →  square(6) + square(10) = 36 + 100
```

> **핵심 통찰**: `sum_of_squares`의 정의만 보면 `square`가 내장 함수인지, 라이브러리에서 가져온 것인지, 사용자가 정의한 복합 함수인지 **구분할 수 없다**. 이것이 추상화의 핵심이다 — 복합 함수는 사용 시점에서 원시 함수와 구별 불가능하다. 이 원칙은 Chapter 2의 데이터 추상화에서도 동일하게 적용된다.

---

## 6. 치환 모델 (The Substitution Model)

### 6.1 치환에 의한 함수 적용

복합 함수를 인수에 적용할 때, **함수 본문의 매개변수를 대응하는 인수 값으로 치환**한다:

```
f(5)
→ sum_of_squares(5 + 1, 5 * 2)
→ sum_of_squares(6, 10)
→ square(6) + square(10)
→ (6 * 6) + (10 * 10)
→ 36 + 100
→ 136
```

### 6.2 치환 모델의 위치

치환 모델은 함수 적용에 대해 **생각하는 도구**이지, 인터프리터의 실제 동작 방식이 아니다. 실제 인터프리터는 텍스트 치환 대신 **매개변수에 대한 지역 환경**을 사용한다.

SICP는 점점 정교해지는 계산 모델을 단계적으로 도입한다:

| 모델 | 도입 시점 | 한계 |
|------|----------|------|
| 치환 모델 | Section 1.1 (현재) | 변이(mutation)를 설명할 수 없다 |
| 환경 모델 | Section 3.2 | 대입과 상태를 설명할 수 있다 |
| 메타순환 평가기 | Section 4.1 | 언어의 완전한 의미를 정의한다 |

## 계산 모델

### 적용 순서 vs 정상 순서

치환 모델 내에서도 두 가지 평가 전략이 가능하다:

**적용 순서 평가 (Applicative-order evaluation)**:

인수를 **먼저 평가**한 후 함수를 적용한다. JavaScript가 사용하는 방식이다.

```
f(5)
→ sum_of_squares(5 + 1, 5 * 2)
→ sum_of_squares(6, 10)          // 인수를 먼저 계산
→ square(6) + square(10)
→ 36 + 100
→ 136
```

**정상 순서 평가 (Normal-order evaluation)**:

인수를 평가하지 않고 표현식을 **완전히 전개**한 후, 축소한다:

```
f(5)
→ sum_of_squares(5 + 1, 5 * 2)
→ square(5 + 1) + square(5 * 2)              // 전개만, 계산하지 않음
→ (5 + 1) * (5 + 1) + (5 * 2) * (5 * 2)     // 완전히 전개
→ 6 * 6 + 10 * 10                            // 이제 축소
→ 36 + 100
→ 136
```

| 구분 | 적용 순서 (Applicative-order) | 정상 순서 (Normal-order) |
|------|------|------|
| 평가 시점 | 인수를 **즉시** 평가 | 인수를 **필요할 때** 평가 |
| 중복 계산 | 없음 — 각 인수를 한 번만 평가 | 있음 — `(5 + 1)`이 두 번 계산됨 |
| JavaScript | **사용함** | 사용하지 않음 |
| 관련 개념 | 즉시 평가(Eager evaluation) | 지연 평가(Lazy evaluation) |

> **핵심 통찰**: 치환 모델로 표현할 수 있는 함수에 대해서는 두 방식 모두 동일한 결과를 산출한다. 하지만 정상 순서 평가는 Section 3.5의 **스트림**과 Section 4.2의 **지연 평가**에서 핵심적인 역할을 한다. 무한한 데이터 구조를 다루는 것이 정상 순서 평가 덕분에 가능해진다.

---

## 7. 조건 표현식과 술어 (Conditional Expressions and Predicates)

### 7.1 조건 표현식

JavaScript에서 조건은 **삼항 연산자(conditional expression)** 로 표현한다:

```javascript
predicate ? consequent_expression : alternative_expression
```

**절댓값 함수** — 가장 기본적인 조건 활용 예:

```javascript
function abs(x) {
    return x >= 0 ? x : -x;
}
```

다중 조건은 조건 표현식을 **중첩**하여 표현한다:

```javascript
function abs(x) {
    return x > 0
           ? x
           : x === 0
             ? 0
             : -x;
}
```

### 7.2 술어 (Predicates)

**술어**란 `true` 또는 `false`를 반환하는 표현식이다:

- 비교 연산자: `>=`, `>`, `<`, `<=`, `===`, `!==`
- 논리 연산자: `&&`(논리곱), `||`(논리합), `!`(부정)

### 7.3 논리 연산자의 특수성

`&&`와 `||`는 일반 연산자가 아니라 **구문 형식(syntactic forms)** 이다. 우측 표현식이 항상 평가되는 것은 아니다(단축 평가(*Short-circuit evaluation — `false && f()`에서 `f()`는 호출되지 않으며, `true || f()`에서도 `f()`는 호출되지 않는다. 이 성질은 Section 4.1의 메타순환 평가기에서 조건문을 특수 형식으로 처리해야 하는 이유와 직접적으로 연결된다.*)):

```javascript
// && 는 다음과 동치:
// expression1 ? expression2 : false

// || 는 다음과 동치:
// expression1 ? true : expression2
```

활용 예:

```javascript
function greater_or_equal(x, y) {
    return x > y || x === y;
}

// 또는 드 모르간의 법칙을 활용:
function greater_or_equal(x, y) {
    return !(x < y);
}
```

---

## 8. 뉴턴 방법에 의한 제곱근 (Square Roots by Newton's Method)

### 8.1 선언적 지식 vs 명령적 지식

수학과 컴퓨터 과학의 근본적 차이가 여기서 드러난다:

| 수학 (선언적 지식) | 컴퓨터 과학 (명령적 지식) |
|-------------------|------------------------|
| "sqrt(x)는 y² = x 이고 y ≥ 0인 y" | "추측값 y를 반복적으로 개선하여 sqrt(x)를 구하라" |
| **무엇(what)** 을 기술 | **어떻게(how)** 를 기술 |
| 성질을 정의 | 절차를 정의 |

수학적 정의는 `sqrt(x)`가 무엇인지를 완벽하게 기술하지만, 그것을 **어떻게 계산하는지**는 말해주지 않는다.

> **핵심 통찰**: 이 구분은 Chapter 4.4의 논리 프로그래밍에서 정점에 달한다. 논리 프로그래밍은 선언적 지식("무엇")만으로 프로그래밍하는 패러다임이다 — 컴퓨터가 "어떻게"를 스스로 찾아낸다.

### 8.2 뉴턴의 연속 근사법

추측값 `guess`로 `sqrt(x)`를 구할 때, `guess`와 `x / guess`의 평균을 새 추측값으로 사용한다:

| 추측값 | 몫 (x / 추측값) | 평균 (새 추측값) |
|--------|-----------------|------------------|
| 1 | 2 / 1 = 2 | (1 + 2) / 2 = 1.5 |
| 1.5 | 2 / 1.5 = 1.3333 | (1.5 + 1.3333) / 2 = 1.4167 |
| 1.4167 | 2 / 1.4167 = 1.4118 | (1.4167 + 1.4118) / 2 = 1.4142 |
| 1.4142 | ... | ... |

## 주요 예제

### 뉴턴 방법으로 구현한 제곱근 함수

이 예제는 SICP의 첫 번째 핵심 예제로, 재귀적 함수 호출만으로 반복을 구현하는 방법을 보여준다:

```javascript
function sqrt(x) {
    return sqrt_iter(1, x);
}

function sqrt_iter(guess, x) {
    return is_good_enough(guess, x)
           ? guess
           : sqrt_iter(improve(guess, x), x);
}

function improve(guess, x) {
    return average(guess, x / guess);
}

function average(x, y) {
    return (x + y) / 2;
}

function is_good_enough(guess, x) {
    return abs(square(guess) - x) < 0.001;
}
```

실행 결과:

```javascript
sqrt(9);                          // 3.00009155413138
sqrt(100 + 37);                   // 11.704699917758145
sqrt(sqrt(2) + sqrt(3));          // 1.7739279023207892
square(sqrt(1000));               // 1000.000369924366
```

이 코드의 구조를 분석하면:

- `sqrt` — 최상위 진입점, 초기 추측값 1로 시작
- `sqrt_iter` — 핵심 반복 로직 (추측이 충분히 좋으면 반환, 아니면 개선 후 재귀)
- `improve` — 추측값 개선 (뉴턴 방법의 핵심)
- `is_good_enough` — 종료 조건 (추측값의 제곱이 x에 충분히 가까운가)
- `average`, `square`, `abs` — 보조 함수

> **핵심 통찰**: 이 프로그램에는 `while`이나 `for` 같은 반복문이 없다. **재귀 호출**만으로 반복이 구현된다. `sqrt_iter`는 자기 자신을 호출하되, 매번 개선된 추측값을 전달한다. 이것이 함수형 프로그래밍에서 반복을 표현하는 기본 방식이며, Section 1.2에서 재귀와 반복의 관계를 더 깊이 탐구한다.

---

## 9. 블랙박스 추상화로서의 함수 (Functions as Black-Box Abstractions)

### 9.1 절차적 분해 (Procedural Decomposition)

제곱근 프로그램은 문제를 하위 문제로 분해하는 좋은 예다. `sqrt`는 `sqrt_iter`에 의존하고, `sqrt_iter`는 `is_good_enough`와 `improve`에 의존하며, 각각은 또 다른 하위 함수에 의존한다.

핵심은 각 함수가 **블랙박스**로 기능한다는 것이다. `square`를 사용할 때 그것이 어떻게 구현되었는지 알 필요가 없다. 다음 두 구현은 사용자 관점에서 동일하다:

```javascript
// 직접 곱셈
function square(x) {
    return x * x;
}

// 수학 함수를 이용한 우회 구현
function square(x) {
    return math_exp(double(math_log(x)));
}

function double(x) {
    return x + x;
}
```

### 9.2 지역 이름과 속박 변수 (Local Names and Bound Variables)

함수의 매개변수는 **속박 변수(bound variable)** 다. 매개변수의 구체적인 이름은 함수 외부에 영향을 미치지 않는다:

```javascript
// 다음 두 함수는 완전히 동일하다:
function square(x) { return x * x; }
function square(y) { return y * y; }
```

함수 본문에서 매개변수가 아닌 이름은 **자유 변수(free variable)** 다:

```javascript
function is_good_enough(guess, x) {
    return abs(square(guess) - x) < 0.001;
}
// 속박 변수: guess, x  (매개변수)
// 자유 변수: abs, square, <, -  (외부에서 참조)
```

속박 변수의 이름을 바꾸어도 함수의 의미는 변하지 않지만, 자유 변수의 이름을 바꾸면 의미가 바뀐다. `abs`를 `cos`로 바꾸면 전혀 다른 함수가 된다.

### 9.3 블록 구조 (Block Structure)

앞서 정의한 제곱근 프로그램의 문제점: `sqrt_iter`, `improve`, `is_good_enough`가 모두 최상위 이름 공간에 노출된다. 이 보조 함수들은 `sqrt` 안에서만 의미가 있는데, 다른 함수와 이름이 충돌할 수 있다.

해결책은 **블록 구조** — 함수 내부에 함수를 정의하는 것이다:

```javascript
function sqrt(x) {
    function is_good_enough(guess) {
        return abs(square(guess) - x) < 0.001;
    }
    function improve(guess) {
        return average(guess, x / guess);
    }
    function sqrt_iter(guess) {
        return is_good_enough(guess)
               ? guess
               : sqrt_iter(improve(guess));
    }
    return sqrt_iter(1);
}
```

주목할 점:

1. **내부 함수는 외부에서 보이지 않는다** — `sqrt_iter`, `improve`, `is_good_enough`는 `sqrt` 바깥에서 접근할 수 없다
2. **`x`를 전달할 필요가 없다** — 내부 함수들은 `sqrt`의 매개변수 `x`를 자유 변수로 직접 참조한다

이것이 **렉시컬 스코핑(lexical scoping)** 이다:

> 함수 내의 자유 변수는 그 함수가 **정의된 환경**(호출된 환경이 아니라)에서 바인딩을 찾는다.

원래 `is_good_enough(guess, x)`에서 `x`는 매개변수였지만, 블록 구조 버전에서 `x`는 `sqrt`의 매개변수를 참조하는 자유 변수다. 이를 통해 인터페이스가 단순해진다.

> **핵심 통찰**: 블록 구조는 **Algol 60**에서 유래한 것으로, 대규모 프로그램 구성의 기초다. 렉시컬 스코핑과 결합하면 **클로저(closure)** 라는 강력한 개념이 된다 — Section 1.3에서 함수를 값으로 반환할 때 이 개념이 본격적으로 활용된다.

---

## 연습 문제 하이라이트

### Exercise 1.3: 세 수 중 큰 두 수의 제곱합

세 개의 수를 인수로 받아 그 중 큰 두 수의 제곱합을 반환하는 함수를 작성하라.

**풀이**:

```javascript
function sum_of_squares_of_two_largest(a, b, c) {
    return a <= b && a <= c
           ? sum_of_squares(b, c)    // a가 가장 작음
           : b <= a && b <= c
             ? sum_of_squares(a, c)  // b가 가장 작음
             : sum_of_squares(a, b); // c가 가장 작음
}
```

이 문제는 조건 표현식과 함수 조합을 연습하기 위한 것이다. 가장 작은 수를 찾아 제외하는 전략이 핵심이다.

### Exercise 1.5: 적용 순서 vs 정상 순서 판별

```javascript
function p() { return p(); }

function test(x, y) {
    return x === 0 ? 0 : y;
}

test(0, p());
```

이 코드의 동작은 평가 전략에 따라 완전히 달라진다:

- **적용 순서**: `test(0, p())`를 평가할 때 인수 `p()`를 먼저 평가한다. `p()`는 `p()`를 반환하고, 그것은 다시 `p()`를 호출하여 **무한 루프**에 빠진다. 프로그램이 종료되지 않는다.
- **정상 순서**: 인수를 평가하지 않고 본문을 전개한다. `0 === 0 ? 0 : p()` → `0`. 조건이 `true`이므로 `p()`는 **결코 평가되지 않는다**. 결과는 `0`이다.

JavaScript는 적용 순서를 사용하므로, 이 코드는 무한 루프에 빠진다.

### Exercise 1.6: 조건문은 왜 특수 형식인가

만약 조건 표현식을 일반 함수로 정의한다면?

```javascript
function conditional(predicate, then_clause, else_clause) {
    return predicate ? then_clause : else_clause;
}
```

이 함수로 `sqrt_iter`를 재작성하면:

```javascript
function sqrt_iter(guess, x) {
    return conditional(is_good_enough(guess, x),
                       guess,
                       sqrt_iter(improve(guess, x), x));
}
```

**문제**: 적용 순서 평가에서, `conditional`을 호출하기 전에 세 인수를 **모두** 평가한다. `is_good_enough`가 `true`를 반환하더라도 `sqrt_iter(improve(guess, x), x)`가 평가되어 **무한 재귀**가 발생한다.

이것이 조건 표현식(`? :`)이 일반 함수가 아닌 **특수 형식**이어야 하는 이유다 — 인수의 평가 시점을 제어해야 하기 때문이다.

### Exercise 1.7: `is_good_enough`의 한계

절대 허용 오차(`< 0.001`)는 두 가지 상황에서 문제를 일으킨다:

**매우 작은 수**: `sqrt(0.0001)`의 정확한 답은 `0.01`이지만, 허용 오차 0.001은 이 스케일에서 너무 크다. 결과는 약 `0.03`으로, 실제 값과 3배 차이가 난다.

**매우 큰 수**: 부동소수점의 정밀도 한계로, 매우 큰 수에서는 `square(guess) - x`가 절대 0.001 이하로 내려가지 않을 수 있다. 프로그램이 무한 루프에 빠진다.

**개선**: 절대 허용 오차 대신, **추측값의 변화율**을 기준으로 종료 조건을 판단한다:

```javascript
function is_good_enough(guess, x) {
    return abs(guess - improve(guess, x)) / guess < 0.001;
}
```

이 방식은 추측값의 상대적 변화가 충분히 작아지면 종료하므로, 작은 수와 큰 수 모두에서 올바르게 동작한다.

---

## 요약

- 모든 강력한 프로그래밍 언어는 세 가지 메커니즘을 갖춘다: **원시 요소**, **결합 수단**, **추상화 수단**.
- **환경(environment)** 은 이름-값 연결을 추적하는 메모리 구조로, 추상화의 기초다.
- 연산자 조합의 평가는 **재귀적**이다 — 트리 축적 과정으로 시각화할 수 있다.
- **함수 선언**은 복합 연산에 이름을 붙이는 추상화 수단이다. 복합 함수와 원시 함수는 사용 시점에서 구분되지 않는다.
- **치환 모델**은 함수 적용을 이해하기 위한 사고 모델이다. **적용 순서**(JavaScript)와 **정상 순서**라는 두 가지 평가 전략이 존재한다.
- **뉴턴 방법**은 선언적 지식(무엇)과 명령적 지식(어떻게)의 차이를 보여주는 핵심 예제다. 재귀 호출만으로 반복을 구현한다.
- 함수는 **블랙박스 추상화**로서, 구현 세부사항을 숨기고 인터페이스만 노출한다.
- **블록 구조**와 **렉시컬 스코핑**은 이름 공간을 관리하고 인터페이스를 단순화하는 핵심 기법이다.

---

## 다른 섹션과의 관계

- **Section 1.2 (Functions and the Processes They Generate)**: 이 섹션에서 도입한 재귀를 더 깊이 탐구한다. `sqrt_iter`의 재귀가 사실 **반복적 프로세스**를 생성한다는 것, 그리고 재귀적 프로세스와 반복적 프로세스의 근본적 차이를 분석한다.
- **Section 1.3 (Higher-Order Functions)**: 함수를 "값"으로 다루는 고차 함수를 도입한다. 뉴턴 방법을 일반화하여 "고정점 찾기"라는 더 추상적인 패턴으로 표현한다.
- **Section 3.2 (The Environment Model)**: 치환 모델의 한계를 극복하는 환경 모델을 도입한다. `const`와 함수 적용이 환경을 어떻게 조작하는지를 형식적으로 설명한다.
- **Section 4.1 (The Metacircular Evaluator)**: 이 섹션의 평가 규칙(원시 표현식, 조합, 특수 형식)이 메타순환 평가기의 `evaluate` 함수에서 코드로 구현된다. 개념이 프로그램이 되는 순간이다.
- **Section 4.2 (Lazy Evaluation)**: 정상 순서 평가를 실제로 구현하는 지연 평가 인터프리터를 만든다. Exercise 1.5에서 탐구한 적용 순서와 정상 순서의 차이가 실체화된다.
