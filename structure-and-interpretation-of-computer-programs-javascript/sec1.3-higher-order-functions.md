# Section 1.3: Formulating Abstractions with Higher-Order Functions (고차 함수를 이용한 추상화)

## 핵심 질문

함수를 값으로 다룬다는 것 — 함수를 인수로 전달하고, 함수를 반환값으로 사용하는 것 — 은 추상화의 힘을 어떻게 극적으로 증폭시키는가?

---

## 핵심 개념

| 개념 | 정의 |
|------|------|
| **고차 함수(Higher-order function)** | 함수를 인수로 받거나 함수를 반환하는 함수 |
| **람다 표현식(Lambda expression)** | 이름 없이 함수를 생성하는 표현식 — JavaScript의 화살표 함수 |
| **고정점(Fixed point)** | f(x) = x를 만족하는 값 x |
| **평균 감쇠(Average damping)** | 고정점 탐색의 수렴을 돕기 위해 f(x)와 x의 평균을 사용하는 기법 |
| **일급 시민(First-class citizen)** | 이름을 붙이고, 인수로 전달하고, 반환값으로 사용하고, 데이터 구조에 포함시킬 수 있는 요소 |

---

## 1. 인수로서의 함수 (Functions as Arguments)

### 1.1 패턴 인식: 세 가지 합산

다음 세 함수를 비교한다:

**정수의 합**:

```javascript
function sum_integers(a, b) {
    return a > b
           ? 0
           : a + sum_integers(a + 1, b);
}
```

**정수의 세제곱의 합**:

```javascript
function sum_cubes(a, b) {
    return a > b
           ? 0
           : cube(a) + sum_cubes(a + 1, b);
}
```

**π/8에 수렴하는 라이프니츠 급수**:

```javascript
function pi_sum(a, b) {
    return a > b
           ? 0
           : 1 / (a * (a + 2)) + pi_sum(a + 4, b);
}
```

세 함수는 거의 동일한 구조를 공유한다. 다른 것은 (1) 각 항에 적용하는 함수, (2) 다음 항을 구하는 함수뿐이다.

### 1.2 합산 추상화 (The Summation Abstraction)

공통 패턴을 추출하여 고차 함수로 만든다:

```javascript
function sum(term, a, next, b) {
    return a > b
           ? 0
           : term(a) + sum(term, next(a), next, b);
}
```

`sum`은 **함수를 인수로 받는 함수** — 고차 함수다. `term`은 각 항에 적용할 함수이고, `next`는 다음 항을 계산하는 함수다.

이제 앞의 세 함수를 `sum`으로 표현할 수 있다:

```javascript
function identity(x) { return x; }
function inc(x) { return x + 1; }

function sum_integers(a, b) {
    return sum(identity, a, inc, b);
}
```

```javascript
function sum_cubes(a, b) {
    return sum(cube, a, inc, b);
}
```

```javascript
function pi_sum(a, b) {
    function pi_term(x) { return 1 / (x * (x + 2)); }
    function pi_next(x) { return x + 4; }
    return sum(pi_term, a, pi_next, b);
}

8 * pi_sum(1, 1000);  // 3.139592655589783 (π에 근사)
```

### 1.3 적분 (Integration)

`sum`을 사용하여 정적분을 수치적으로 근사한다:

```javascript
function integral(f, a, b, dx) {
    function add_dx(x) { return x + dx; }
    return sum(f, a + dx / 2, add_dx, b) * dx;
}

integral(cube, 0, 1, 0.01);   // 0.24998750000000042 (정확한 값: 0.25)
integral(cube, 0, 1, 0.001);  // 0.249999875000001
```

> **핵심 통찰**: `sum`이라는 하나의 고차 함수로 정수의 합, 세제곱의 합, 급수의 합, 적분을 **모두** 표현할 수 있다. 이것이 고차 함수의 힘이다. 공통 패턴을 인식하고, 변하는 부분을 매개변수(함수)로 추출하면, 하나의 추상화로 무한히 많은 구체적 계산을 표현할 수 있다.

---

## 2. 람다 표현식으로 함수 구성하기 (Constructing Functions Using Lambda Expressions)

### 2.1 화살표 함수 (Arrow Functions)

`pi_sum`에서 `pi_term`, `pi_next` 같은 보조 함수를 매번 이름 붙여 정의하는 것은 번거롭다. **람다 표현식**(JavaScript의 화살표 함수)을 사용하면 이름 없이 함수를 생성할 수 있다:

```javascript
function pi_sum(a, b) {
    return sum(x => 1 / (x * (x + 2)),
               a,
               x => x + 4,
               b);
}
```

일반 형식:

```javascript
(parameters) => expression
```

람다 표현식은 **이름이 없을 뿐**, `function` 선언으로 만든 함수와 완전히 동일한 함수를 생성한다:

```javascript
// 다음 두 표현은 동등하다:
const square = x => x * x;
function square(x) { return x * x; }
```

### 2.2 const를 이용한 지역 변수

람다 표현식은 지역 변수를 만드는 데도 활용된다. 다음과 같은 수학 함수를 구현한다고 하자:

> f(x, y) = x(1 + xy)² + y(1 - y) + (1 + xy)(1 - y)

`a = 1 + xy`, `b = 1 - y`로 놓으면:

> f(x, y) = xa² + yb + ab

```javascript
function f(x, y) {
    const a = 1 + x * y;
    const b = 1 - y;
    return x * square(a) + y * b + a * b;
}
```

`const`는 사실 **즉시 호출되는 람다 표현식**의 구문적 편의(syntactic sugar)로 이해할 수 있다:

```javascript
function f(x, y) {
    return (a => (b => x * square(a) + y * b + a * b)(1 - y))(1 + x * y);
}
```

> **핵심 통찰**: `const` 선언을 람다 표현식으로 환원할 수 있다는 사실은 단순한 트릭이 아니다. 이것은 Section 4.1의 메타순환 평가기에서 `const` 선언의 의미를 정의할 때 직접적으로 활용된다. 또한 함수가 얼마나 근본적인 개념인지를 보여준다 — 변수 바인딩조차 함수 적용으로 표현할 수 있다.

---

## 3. 일반적 방법으로서의 함수 (Functions as General Methods)

### 3.1 반분법 (Half-Interval Method)

연속 함수 f에 대해, f(a) < 0 < f(b)이면 a와 b 사이에 f(x) = 0인 근이 존재한다. 구간을 반으로 나누어 근을 찾는다:

```javascript
function search(f, neg_point, pos_point) {
    const midpoint = average(neg_point, pos_point);
    if (close_enough(neg_point, pos_point)) {
        return midpoint;
    }
    else {
        const test_value = f(midpoint);
        return test_value > 0
               ? search(f, neg_point, midpoint)
               : test_value < 0
                 ? search(f, midpoint, pos_point)
                 : midpoint;
    }
}

function close_enough(x, y) {
    return abs(x - y) < 0.001;
}
```

활용 예:

```javascript
half_interval_method(math_sin, 2, 4);       // 3.14111328125 ≈ π
half_interval_method(x => x * x * x - 2 * x - 3, 1, 2);  // 1.89306640625
```

### 3.2 고정점 (Fixed Points)

함수 f의 **고정점(fixed point)** 은 f(x) = x를 만족하는 값 x다. 초기 추측에서 시작하여 f를 반복 적용하면 고정점에 수렴할 수 있다:

x, f(x), f(f(x)), f(f(f(x))), ...

```javascript
const tolerance = 0.00001;

function fixed_point(f, first_guess) {
    function close_enough(x, y) {
        return abs(x - y) < tolerance;
    }
    function try_with(guess) {
        const next = f(guess);
        return close_enough(guess, next)
               ? next
               : try_with(next);
    }
    return try_with(first_guess);
}
```

활용 예:

```javascript
fixed_point(math_cos, 1);  // 0.7390822985224023
fixed_point(y => math_sin(y) + math_cos(y), 1);  // 1.2587315962971173
```

### 3.3 제곱근을 고정점으로 표현

sqrt(x) = y라 함은 y = x/y, 즉 y가 함수 y ↦ x/y의 **고정점**이라는 뜻이다. 그러나 단순히 `fixed_point(y => x / y, 1)`을 시도하면 진동(*oscillation — y = 1에서 시작하면 다음 값은 2, 그 다음은 1, 다시 2... 무한히 반복된다. 평균 감쇠는 이 진동을 제거하여 수렴을 보장한다.*)한다:

```
추측: 1
다음: 2/1 = 2
다음: 2/2 = 1
다음: 2/1 = 2
...  (무한 진동)
```

### 3.4 평균 감쇠 (Average Damping)

해결책: y와 x/y의 **평균**을 다음 추측값으로 사용한다. 즉 y ↦ (y + x/y) / 2의 고정점을 구한다:

```javascript
function sqrt(x) {
    return fixed_point(y => average(y, x / y), 1);
}
```

이것이 바로 Section 1.1에서 구현한 **뉴턴 방법**이다! 같은 알고리즘이 "고정점 탐색 + 평균 감쇠"라는 더 추상적인 관점에서 재해석된다.

> **핵심 통찰**: Section 1.1에서 "어떻게" 수준으로 구현한 뉴턴 방법이, 고차 함수의 관점에서 보면 **고정점 탐색**이라는 일반적 방법의 특수한 경우임이 드러난다. 추상화 수준을 높이면 개별 알고리즘들 사이의 공통 구조가 보이기 시작한다.

---

## 4. 반환값으로서의 함수 (Functions as Returned Values)

### 4.1 평균 감쇠를 함수로 표현

평균 감쇠를 **함수를 반환하는 함수**로 일반화한다:

```javascript
function average_damp(f) {
    return x => average(x, f(x));
}
```

`average_damp`는 함수 `f`를 받아서, `x`와 `f(x)`의 평균을 반환하는 **새로운 함수**를 만든다:

```javascript
average_damp(square)(10);  // average(10, 100) = 55
```

이제 제곱근을 더 명확하게 표현할 수 있다:

```javascript
function sqrt(x) {
    return fixed_point(average_damp(y => x / y), 1);
}
```

이 정의를 말로 풀면: "y ↦ x/y 함수에 평균 감쇠를 적용한 것의 고정점을 구하라." 세 개의 개념이 각각 명확하게 분리되어 있다.

세제곱근도 동일한 패턴으로:

```javascript
function cube_root(x) {
    return fixed_point(average_damp(y => x / (y * y)), 1);
}
```

### 4.2 뉴턴 방법의 일반화

뉴턴 방법(*Newton's method — 여기서의 뉴턴 방법은 Section 1.1의 제곱근 방법보다 더 일반적인 형태다. Section 1.1의 방법은 사실 이 일반적 뉴턴 방법의 특수한 경우다.*): 함수 g(x) = 0의 근을 찾기 위해 고정점 탐색을 사용한다. x의 다음 추측값은:

> x ← x - g(x) / g'(x)

여기서 g'(x)는 g의 도함수다.

**도함수를 함수로 표현**:

```javascript
const dx = 0.00001;

function deriv(g) {
    return x => (g(x + dx) - g(x)) / dx;
}
```

`deriv`는 함수를 받아 함수를 반환하는 고차 함수다:

```javascript
deriv(cube)(5);  // 75.00014999664018 ≈ 3 * 5² = 75
```

**뉴턴 변환 (Newton's Transform)**:

```javascript
function newton_transform(g) {
    return x => x - g(x) / deriv(g)(x);
}

function newtons_method(g, guess) {
    return fixed_point(newton_transform(g), guess);
}
```

**제곱근을 뉴턴 방법으로**:

```javascript
function sqrt(x) {
    return newtons_method(y => square(y) - x, 1);
}
```

"y² - x = 0의 근을 뉴턴 방법으로 찾아라." 문제의 수학적 본질이 코드에 직접 드러난다.

### 4.3 추상화의 한 단계 더 높이

두 가지 제곱근 구현을 비교하면 공통 패턴이 보인다:

```javascript
// 방법 1: 고정점 + 평균 감쇠
function sqrt(x) {
    return fixed_point(average_damp(y => x / y), 1);
}

// 방법 2: 고정점 + 뉴턴 변환
function sqrt(x) {
    return newtons_method(y => square(y) - x, 1);
}
```

공통점: 둘 다 **함수를 변환하여 고정점을 구한다**. 이 패턴을 추출한다:

```javascript
function fixed_point_of_transform(g, transform, guess) {
    return fixed_point(transform(g), guess);
}
```

이제 두 방법을 동일한 프레임워크로 표현할 수 있다:

```javascript
// 평균 감쇠 방법
function sqrt(x) {
    return fixed_point_of_transform(
               y => x / y,
               average_damp,
               1);
}

// 뉴턴 방법
function sqrt(x) {
    return fixed_point_of_transform(
               y => square(y) - x,
               newton_transform,
               1);
}
```

> **핵심 통찰**: 이것이 SICP가 말하는 추상화의 정수다. 처음에는 "제곱근을 구하는 방법"이었던 것이, 추상화를 거듭하면서 **"함수를 변환하여 고정점을 구하는 일반적 프레임워크"** 가 되었다. 구체적 문제에서 출발하여 점점 더 일반적인 패턴을 추출하는 이 과정이 프로그래밍의 핵심이다.

---

## 5. 일급 시민으로서의 함수 (First-Class Functions)

### 5.1 일급 시민의 조건

프로그래밍 언어의 요소가 **일급 시민(first-class citizen)** 이 되려면 다음을 만족해야 한다:

| 권리 | 설명 | JavaScript 함수의 예 |
|------|------|---------------------|
| 이름을 붙일 수 있다 | 변수에 저장 | `const sq = x => x * x;` |
| 인수로 전달할 수 있다 | 다른 함수의 입력 | `sum(cube, 1, inc, 10)` |
| 반환값으로 사용할 수 있다 | 함수가 함수를 생성 | `average_damp(f)` → 새 함수 |
| 데이터 구조에 포함시킬 수 있다 | 배열, 객체의 원소 | `[square, cube, identity]` |

JavaScript에서 함수는 **일급 시민**이다. 숫자나 문자열처럼 자유롭게 다룰 수 있다.

> **핵심 통찰**: 함수를 일급 시민으로 대우하면, 프로그래밍 언어의 표현력이 극적으로 증가한다. 이 섹션에서 본 `sum`, `fixed_point`, `average_damp`, `newton_transform`, `deriv` 등은 모두 함수의 일급 시민 지위 덕분에 가능하다. Chapter 2에서는 함수를 데이터 구조의 일부로 사용하는 것까지 나아간다.

---

## 주요 예제

### 제곱근의 세 가지 추상화 수준

이 섹션의 핵심은 **같은 알고리즘을 점점 더 높은 추상화 수준에서 표현**하는 것이다:

**수준 1 (Section 1.1)** — 구체적 구현:

```javascript
function sqrt(x) {
    function improve(guess) { return average(guess, x / guess); }
    function is_good_enough(guess) {
        return abs(square(guess) - x) < 0.001;
    }
    function sqrt_iter(guess) {
        return is_good_enough(guess) ? guess : sqrt_iter(improve(guess));
    }
    return sqrt_iter(1);
}
```

**수준 2** — 고정점 + 평균 감쇠:

```javascript
function sqrt(x) {
    return fixed_point(average_damp(y => x / y), 1);
}
```

**수준 3** — 일반적 변환 프레임워크:

```javascript
function sqrt(x) {
    return fixed_point_of_transform(y => x / y, average_damp, 1);
}
```

각 수준에서 **동일한 계산**을 수행하지만, 표현의 추상화 수준이 다르다. 수준이 높아질수록 알고리즘의 본질이 더 명확하게 드러나고, 다른 문제에 대한 재사용 가능성이 높아진다.

---

## 연습 문제 하이라이트

### Exercise 1.29: 심프슨 적분 (Simpson's Rule)

심프슨 법칙은 `sum`을 사용하여 더 정확한 수치 적분을 구현하는 문제다. n을 짝수로 놓고 h = (b-a)/n으로 설정한 뒤:

> ∫f = (h/3)[y₀ + 4y₁ + 2y₂ + 4y₃ + ... + 4yₙ₋₁ + yₙ]

여기서 yₖ = f(a + kh). 고차 함수 `sum`을 활용하면 이 공식을 간결하게 구현할 수 있다.

### Exercise 1.30: 반복적 sum

Section 1.3.1의 `sum`은 재귀적 프로세스를 생성한다. 이것을 반복적 프로세스를 생성하도록 재작성하라:

```javascript
function sum(term, a, next, b) {
    function iter(a, result) {
        return a > b
               ? result
               : iter(next(a), result + term(a));
    }
    return iter(a, 0);
}
```

### Exercise 1.31: product — 합산의 일반화

`sum`과 유사한 `product` 고차 함수를 구현하라:

```javascript
function product(term, a, next, b) {
    return a > b
           ? 1
           : term(a) * product(term, next(a), next, b);
}
```

이것으로 `factorial`을 정의할 수 있다:

```javascript
function factorial(n) {
    return product(identity, 1, inc, n);
}
```

또한 월리스 공식(*Wallis product — π/4 = (2·4·4·6·6·8·...)/(3·3·5·5·7·7·...). `product`로 간결하게 표현할 수 있다.*)으로 π를 근사할 수 있다.

### Exercise 1.32: accumulate — 궁극의 일반화

`sum`과 `product`를 모두 포괄하는 `accumulate`를 구현하라:

```javascript
function accumulate(combiner, null_value, term, a, next, b) {
    return a > b
           ? null_value
           : combiner(term(a),
                      accumulate(combiner, null_value, term, next(a), next, b));
}
```

```javascript
// sum = accumulate with + and 0
function sum(term, a, next, b) {
    return accumulate((x, y) => x + y, 0, term, a, next, b);
}

// product = accumulate with * and 1
function product(term, a, next, b) {
    return accumulate((x, y) => x * y, 1, term, a, next, b);
}
```

### Exercise 1.35: 황금비를 고정점으로

φ(황금비)는 x ↦ 1 + 1/x의 고정점이다:

```javascript
fixed_point(x => 1 + 1 / x, 1);  // 1.6180327868852458 ≈ φ
```

### Exercise 1.37: 연분수 (Continued Fractions)

연분수를 계산하는 함수 `cont_frac`를 구현하라:

```javascript
function cont_frac(n, d, k) {
    function recur(i) {
        return i > k
               ? 0
               : n(i) / (d(i) + recur(i + 1));
    }
    return recur(1);
}

// 1/φ 계산
cont_frac(i => 1, i => 1, 11);  // 0.6180555555555556 ≈ 1/φ
```

---

## 요약

- **고차 함수**는 함수를 인수로 받거나 반환하는 함수다. 공통 패턴을 추출하여 강력한 추상화를 만든다.
- **람다 표현식**(화살표 함수)은 이름 없이 함수를 생성한다. 보조 함수를 매번 이름 붙이지 않아도 된다.
- **고정점 탐색**은 많은 수치 계산 알고리즘의 공통 프레임워크다. 뉴턴 방법은 고정점 탐색의 특수한 경우다.
- **평균 감쇠**는 고정점 탐색의 수렴을 돕는 기법이며, 이 자체가 **함수를 받아 함수를 반환**하는 고차 함수로 표현된다.
- `sum` → `product` → `accumulate`로 이어지는 일반화는 고차 함수로 추상화의 수준을 점진적으로 높이는 과정을 보여준다.
- JavaScript에서 함수는 **일급 시민**이다. 이름을 붙이고, 인수로 전달하고, 반환값으로 사용하고, 데이터 구조에 포함시킬 수 있다.

---

## 다른 섹션과의 관계

- **Section 1.1 (The Elements of Programming)**: Section 1.1의 제곱근이 이 섹션에서 "고정점 + 평균 감쇠"로 재해석된다. 추상화 수준이 높아지면서 알고리즘의 본질이 드러나는 과정이다.
- **Section 1.2 (Functions and the Processes They Generate)**: `sum`의 재귀적 버전과 반복적 버전(Exercise 1.30)의 비교는 Section 1.2의 핵심 주제다.
- **Section 2.1 (Introduction to Data Abstraction)**: 함수로 데이터를 표현하는 놀라운 기법이 등장한다. `cons`, `car`, `cdr`을 함수만으로 구현할 수 있다 — 함수의 일급 시민 지위가 데이터 추상화의 기초가 된다.
- **Section 2.2 (Hierarchical Data)**: `map`, `filter`, `accumulate`(reduce) 같은 리스트 고차 함수가 이 섹션의 패턴을 데이터 구조로 확장한다.
- **Section 3.1 (Assignment and Local State)**: `const`로 만든 지역 변수가 `let`(대입)으로 대체되면서 함수의 의미가 근본적으로 바뀐다. 고차 함수와 대입의 결합이 **객체**라는 개념을 낳는다.
- **Section 3.5 (Streams)**: 이 섹션의 합산 추상화(`sum`)를 스트림의 관점에서 재구성한다. 무한 급수를 스트림으로 표현하면 `sum`이 필요 없어진다.
