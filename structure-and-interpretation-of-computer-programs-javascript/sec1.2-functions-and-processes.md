# Section 1.2: Functions and the Processes They Generate (함수와 그것이 생성하는 프로세스)

## 핵심 질문

함수가 실행될 때 실제로 어떤 형태의 계산 과정(프로세스)이 펼쳐지는가? 같은 재귀 함수라도 전혀 다른 프로세스를 생성할 수 있다는 것은 무엇을 의미하는가?

---

## 핵심 개념

| 개념 | 정의 |
|------|------|
| **재귀적 프로세스(Recursive process)** | 연산이 지연(deferred)되어 쌓이는 프로세스 — 확장 후 축소 |
| **반복적 프로세스(Iterative process)** | 상태 변수만으로 진행 상황을 완전히 기술할 수 있는 프로세스 |
| **트리 재귀(Tree recursion)** | 함수가 자신을 두 번 이상 호출하여 트리 형태로 확장되는 프로세스 |
| **증가 차수(Order of growth)** | 입력 크기에 따른 자원(시간, 공간) 사용량의 증가율 |
| **꼬리 재귀(Tail recursion)** | 재귀 호출이 함수의 마지막 동작인 경우 — 반복적 프로세스를 생성 |

---

## 1. 선형 재귀와 반복 (Linear Recursion and Iteration)

### 1.1 팩토리얼: 두 가지 구현

`n!`을 계산하는 두 가지 방법을 비교하면 재귀적 프로세스와 반복적 프로세스의 차이가 명확해진다.

**재귀적 프로세스를 생성하는 구현**:

```javascript
function factorial(n) {
    return n === 1
           ? 1
           : n * factorial(n - 1);
}
```

`factorial(6)`의 실행 과정:

```
factorial(6)
6 * factorial(5)
6 * (5 * factorial(4))
6 * (5 * (4 * factorial(3)))
6 * (5 * (4 * (3 * factorial(2))))
6 * (5 * (4 * (3 * (2 * factorial(1)))))
6 * (5 * (4 * (3 * (2 * 1))))
6 * (5 * (4 * (3 * 2)))
6 * (5 * (4 * 6))
6 * (5 * 24)
6 * 120
720
```

먼저 **확장(expand)** — 지연된 곱셈 연산이 쌓인다. 그 다음 **축소(contract)** — 실제 곱셈이 수행된다. 이것이 **재귀적 프로세스**다.

**반복적 프로세스를 생성하는 구현**:

```javascript
function factorial(n) {
    return fact_iter(1, 1, n);
}

function fact_iter(product, counter, max_count) {
    return counter > max_count
           ? product
           : fact_iter(counter * product, counter + 1, max_count);
}
```

`factorial(6)`의 실행 과정:

```
factorial(6)
fact_iter(1, 1, 6)
fact_iter(1, 2, 6)
fact_iter(2, 3, 6)
fact_iter(6, 4, 6)
fact_iter(24, 5, 6)
fact_iter(120, 6, 6)
fact_iter(720, 7, 6)
720
```

확장도 축소도 없다. 각 단계에서 `product`, `counter`, `max_count` 세 변수만으로 계산 상태를 **완전히 기술**할 수 있다. 이것이 **반복적 프로세스**다.

### 1.2 핵심 구분: 재귀적 함수 vs 재귀적 프로세스

| 구분 | 재귀적 함수 (Recursive function) | 재귀적 프로세스 (Recursive process) |
|------|------|------|
| 정의 | 함수가 자기 자신을 호출하는 **구문적** 사실 | 프로세스가 확장 후 축소하는 **실행** 패턴 |
| 예시 | 위의 두 구현 모두 재귀적 함수 | 첫 번째 구현만 재귀적 프로세스 |

> **핵심 통찰**: `fact_iter`는 자기 자신을 호출하므로 **재귀적 함수**이지만, 생성하는 프로세스는 **반복적**이다. 재귀적 함수가 반드시 재귀적 프로세스를 생성하는 것은 아니다. 이 구분을 혼동하는 것은 매우 흔한 실수다.

### 1.3 꼬리 재귀 (Tail Recursion)

`fact_iter`에서 재귀 호출 `fact_iter(...)`는 함수의 **마지막 동작(tail position)** 이다 — 호출 결과에 추가 연산을 하지 않고 그대로 반환한다. 이런 경우를 **꼬리 호출(tail call)** 이라 한다.

반면 첫 번째 구현에서 `n * factorial(n - 1)`은 꼬리 호출이 아니다 — `factorial(n - 1)`의 결과에 `n *`이라는 지연된 연산이 남아 있다.

| 특성 | 재귀적 프로세스 | 반복적 프로세스 |
|------|----------------|----------------|
| 공간 복잡도 | Θ(n) — 지연된 연산 체인 | Θ(1) — 상태 변수만 |
| 시간 복잡도 | Θ(n) | Θ(n) |
| 꼬리 호출 | 아님 | **꼬리 호출** |
| 중단 후 재개 | 지연된 연산 체인 필요 | 상태 변수만으로 재개 가능 |

> **핵심 통찰**: 꼬리 재귀 최적화를 지원하는 언어에서는 반복적 프로세스가 상수 공간에서 실행된다. SICP의 JavaScript Edition은 이를 전제로 한다. 그러나 현실의 JavaScript 엔진 중 꼬리 호출 최적화를 완전히 지원하는 것은 Safari(JavaScriptCore)뿐이며, V8(Chrome/Node.js)은 지원하지 않는다.

---

## 2. 트리 재귀 (Tree Recursion)

### 2.1 피보나치 수: 트리 재귀의 전형

```javascript
function fib(n) {
    return n === 0
           ? 0
           : n === 1
             ? 1
             : fib(n - 1) + fib(n - 2);
}
```

`fib(5)`의 실행 과정은 트리 형태로 펼쳐진다:

```
                         fib(5)
                        /      \
                   fib(4)        fib(3)
                  /     \        /     \
             fib(3)    fib(2)  fib(2)  fib(1)
            /    \     /    \   /   \     |
        fib(2) fib(1) fib(1) fib(0) fib(1) fib(0)  1
        /   \    |      |     |      |      |
    fib(1) fib(0) 1     1     0      1      0
      |      |
      1      0
```

`fib(3)`이 두 번, `fib(2)`가 세 번, `fib(1)`이 다섯 번 계산된다. 엄청난 중복이다.

| 특성 | 값 |
|------|-----|
| 시간 복잡도 | Θ(φⁿ), 여기서 φ = (1 + √5) / 2 ≈ 1.618 (황금비) |
| 공간 복잡도 | Θ(n) — 트리의 최대 깊이 |
| `fib(40)` 호출 횟수 | 약 3억 3천만 번 |

### 2.2 피보나치: 반복적 버전

```javascript
function fib(n) {
    return fib_iter(1, 0, n);
}

function fib_iter(a, b, count) {
    return count === 0
           ? b
           : fib_iter(a + b, a, count - 1);
}
```

| 단계 | a | b | count |
|------|---|---|-------|
| 시작 | 1 | 0 | 5 |
| 1 | 1 | 1 | 4 |
| 2 | 2 | 1 | 3 |
| 3 | 3 | 2 | 2 |
| 4 | 5 | 3 | 1 |
| 5 | 8 | 5 | 0 → 반환 5 |

시간 Θ(n), 공간 Θ(1). 트리 재귀의 지수적 시간에 비해 극적인 차이다.

> **핵심 통찰**: 트리 재귀가 항상 나쁜 것은 아니다. 피보나치에서는 비효율적이지만, 계층적 데이터를 다루는 프로세스에서는 자연스럽고 강력한 도구다 (Section 2.2에서 본격적으로 활용). 또한 **메모이제이션**(Section 3.3)을 적용하면 중복 계산을 제거하면서도 트리 재귀의 명확성을 유지할 수 있다.

### 2.3 잔돈 바꾸기 (Counting Change)

트리 재귀가 자연스러운 문제의 대표적 예: 1달러를 50센트, 25센트, 10센트, 5센트, 1센트 동전으로 바꾸는 방법의 수.

```javascript
function count_change(amount) {
    return cc(amount, 5);
}

function cc(amount, kinds_of_coins) {
    return amount === 0
           ? 1
           : amount < 0 || kinds_of_coins === 0
             ? 0
             : cc(amount, kinds_of_coins - 1)
               +
               cc(amount - first_denomination(kinds_of_coins),
                  kinds_of_coins);
}

function first_denomination(kinds_of_coins) {
    return kinds_of_coins === 1 ? 1
         : kinds_of_coins === 2 ? 5
         : kinds_of_coins === 3 ? 10
         : kinds_of_coins === 4 ? 25
         : kinds_of_coins === 5 ? 50
         : 0;
}

count_change(100);  // 292
```

핵심 관찰: n종류의 동전으로 금액 a를 바꾸는 방법의 수 = **(첫 번째 종류의 동전을 사용하지 않는 경우)** + **(첫 번째 종류의 동전을 적어도 하나 사용하는 경우)**. 이 재귀적 분해가 트리 재귀를 자연스럽게 만든다.

---

## 3. 증가 차수 (Orders of Growth)

프로세스가 소비하는 자원(시간과 공간)을 입력 크기 n의 함수로 표현한다.

**Θ(f(n)) 표기법**: R(n)이 Θ(f(n))이라 함은, n이 충분히 클 때 k₁·f(n) ≤ R(n) ≤ k₂·f(n)을 만족하는 상수 k₁, k₂가 존재한다는 의미다.

| 프로세스 | 시간 | 공간 |
|----------|------|------|
| 팩토리얼 (재귀적) | Θ(n) | Θ(n) |
| 팩토리얼 (반복적) | Θ(n) | Θ(1) |
| 피보나치 (트리 재귀) | Θ(φⁿ) | Θ(n) |
| 피보나치 (반복적) | Θ(n) | Θ(1) |

증가 차수는 정확한 실행 시간이 아니라, 문제 크기가 커질 때의 **증가 추세**를 나타낸다. 상수 배수는 무시한다.

---

## 4. 거듭제곱 (Exponentiation)

### 4.1 선형 재귀 — Θ(n) 시간, Θ(n) 공간

```javascript
function expt(b, n) {
    return n === 0
           ? 1
           : b * expt(b, n - 1);
}
```

### 4.2 선형 반복 — Θ(n) 시간, Θ(1) 공간

```javascript
function expt(b, n) {
    return expt_iter(b, n, 1);
}

function expt_iter(b, counter, product) {
    return counter === 0
           ? product
           : expt_iter(b, counter - 1, b * product);
}
```

### 4.3 빠른 거듭제곱 (Fast Exponentiation) — Θ(log n)

핵심 관찰:
- b^n = (b^(n/2))² (n이 짝수일 때)
- b^n = b · b^(n-1) (n이 홀수일 때)

```javascript
function fast_expt(b, n) {
    return n === 0
           ? 1
           : is_even(n)
             ? square(fast_expt(b, n / 2))
             : b * fast_expt(b, n - 1);
}

function is_even(n) {
    return n % 2 === 0;
}
```

`fast_expt(2, 10)`의 실행:

```
fast_expt(2, 10)
square(fast_expt(2, 5))
square(2 * fast_expt(2, 4))
square(2 * square(fast_expt(2, 2)))
square(2 * square(square(fast_expt(2, 1))))
square(2 * square(square(2 * fast_expt(2, 0))))
square(2 * square(square(2 * 1)))
→ ... → 1024
```

10단계가 아니라 단 몇 단계만에 계산이 완료된다. n을 반으로 나누므로 **Θ(log n)** 시간과 공간이 소요된다.

> **핵심 통찰**: "문제를 반으로 나누면 로그가 된다"는 원리는 컴퓨터 과학 전반에 걸쳐 반복적으로 등장한다. 이진 탐색, 병합 정렬, 그리고 여기서의 빠른 거듭제곱이 모두 같은 원리다.

---

## 5. 최대공약수 (Greatest Common Divisors)

### 5.1 유클리드 알고리즘

두 정수 a, b의 최대공약수(GCD)를 구하는 유클리드 알고리즘:

> GCD(a, b) = GCD(b, a mod b)

```javascript
function gcd(a, b) {
    return b === 0
           ? a
           : gcd(b, a % b);
}
```

`gcd(206, 40)`의 실행:

```
gcd(206, 40)
gcd(40, 6)      // 206 % 40 = 6
gcd(6, 4)       // 40 % 6 = 4
gcd(4, 2)       // 6 % 4 = 2
gcd(2, 0)       // 4 % 2 = 0
2
```

### 5.2 라메의 정리 (Lamé's Theorem)

유클리드 알고리즘이 k단계를 거친다면, 두 수 중 작은 수는 k번째 피보나치 수 이상이어야 한다. 따라서 시간 복잡도는 **Θ(log n)** 이다.

> **핵심 통찰**: 유클리드 알고리즘은 알려진 가장 오래된 알고리즘 중 하나(기원전 약 300년)이면서, 그 효율성 분석에 피보나치 수열이 등장한다는 점이 우아하다. Section 1.2.2에서 배운 피보나치와의 뜻밖의 연결이다.

---

## 6. 소수 판정 (Testing for Primality)

### 6.1 시행 나눗셈 (Trial Division) — Θ(√n)

```javascript
function smallest_divisor(n) {
    return find_divisor(n, 2);
}

function find_divisor(n, test_divisor) {
    return square(test_divisor) > n
           ? n
           : test_divisor % n === 0
             ? test_divisor
             : find_divisor(n, test_divisor + 1);
}

function is_prime(n) {
    return n === smallest_divisor(n);
}
```

√n까지만 검사하면 충분하므로 Θ(√n) 시간이 소요된다.

### 6.2 페르마 검사 (Fermat Test) — Θ(log n)

**페르마의 소정리**: n이 소수이면, n보다 작은 모든 양의 정수 a에 대해 aⁿ mod n = a가 성립한다.

```javascript
function expmod(base, exp, m) {
    return exp === 0
           ? 1
           : is_even(exp)
             ? square(expmod(base, exp / 2, m)) % m
             : (base * expmod(base, exp - 1, m)) % m;
}

function fermat_test(n) {
    function try_it(a) {
        return expmod(a, n, n) === a;
    }
    return try_it(1 + math_floor(math_random() * (n - 1)));
}

function fast_is_prime(n, times) {
    return times === 0
           ? true
           : fermat_test(n)
             ? fast_is_prime(n, times - 1)
             : false;
}
```

핵심 아이디어:
- `expmod`는 빠른 거듭제곱과 동일한 원리로 Θ(log n)에 모듈러 거듭제곱을 계산
- 무작위로 선택한 a에 대해 페르마의 소정리를 검증
- 여러 번 반복하여 확률을 높임

### 6.3 확률적 알고리즘 (Probabilistic Algorithms)

페르마 검사는 **확률적 알고리즘**이다 — 합성수를 소수로 잘못 판정할 (극히 낮은) 가능성이 있다. 카마이클 수(*Carmichael numbers — 소수가 아니면서 모든 a에 대해 페르마의 소정리를 만족하는 수. 예: 561, 1105, 1729. 매우 드물지만 존재한다.*)가 그런 예외적 경우다.

| 방법 | 시간 복잡도 | 확실성 |
|------|-----------|--------|
| 시행 나눗셈 | Θ(√n) | 확정적 |
| 페르마 검사 | Θ(log n) | 확률적 |

> **핵심 통찰**: 확률적 알고리즘은 "거의 확실한" 답을 매우 빠르게 얻을 수 있다. 이 절충은 암호학의 기초다 — RSA 암호화에서 큰 소수를 찾을 때 바로 이런 확률적 소수 판정법을 사용한다.

---

## 주요 예제

### 잔돈 바꾸기 문제

이 예제는 트리 재귀가 문제의 구조를 자연스럽게 반영하는 경우를 보여준다. 1달러(100센트)를 5종류의 미국 동전으로 바꾸는 방법은 정확히 **292가지**다.

재귀적 분해의 핵심: "n종류의 동전으로 금액 a를 바꾸는 방법의 수"를 두 개의 더 작은 문제로 나눈다:
1. 첫 번째 동전을 **사용하지 않는** 방법의 수 (n-1종류로 a를 바꿈)
2. 첫 번째 동전을 **적어도 하나 사용**하는 방법의 수 (n종류로 a-d를 바꿈, d는 첫 번째 동전의 액면)

이 분해를 반복하면 트리가 생성되며, 종료 조건은:
- 금액이 0이면 → 1 (방법이 하나 있음: 아무 동전도 사용하지 않는 것)
- 금액이 음수이면 → 0 (불가능)
- 동전 종류가 0이면 → 0 (불가능)

---

## 연습 문제 하이라이트

### Exercise 1.9: 재귀적 프로세스 vs 반복적 프로세스 판별

두 가지 덧셈 구현이 생성하는 프로세스를 분석하라:

```javascript
// 버전 1
function plus(a, b) {
    return a === 0 ? b : inc(plus(dec(a), b));
}

// 버전 2
function plus(a, b) {
    return a === 0 ? b : plus(dec(a), inc(b));
}
```

**버전 1** — `plus(4, 5)`:
```
plus(4, 5)
inc(plus(3, 5))
inc(inc(plus(2, 5)))
inc(inc(inc(plus(1, 5))))
inc(inc(inc(inc(plus(0, 5)))))
inc(inc(inc(inc(5))))
inc(inc(inc(6)))
inc(inc(7))
inc(8)
9
```
→ **재귀적 프로세스**: `inc`가 지연되어 쌓인다.

**버전 2** — `plus(4, 5)`:
```
plus(4, 5)
plus(3, 6)
plus(2, 7)
plus(1, 8)
plus(0, 9)
9
```
→ **반복적 프로세스**: 확장도 축소도 없다.

### Exercise 1.10: 아커만 함수

```javascript
function A(x, y) {
    return y === 0
           ? 0
           : x === 0
             ? 2 * y
             : y === 1
               ? 2
               : A(x - 1, A(x, y - 1));
}
```

- `A(1, n)` = 2ⁿ (거듭제곱)
- `A(2, n)` = 2^2^...^2 (n번 — 테트레이션(*Tetration — 반복된 거듭제곱. 예: ²²² = 2^(2^2) = 2^4 = 16. 거듭제곱이 곱셈의 반복이듯, 테트레이션은 거듭제곱의 반복이다.*))
- `A(3, n)` = 상상을 초월하는 증가율

아커만 함수는 원시 재귀 함수로 표현할 수 없는 **계산 가능 함수**의 예로, 계산 이론에서 중요한 위치를 차지한다.

### Exercise 1.16: 빠른 거듭제곱의 반복적 버전

빠른 거듭제곱을 **반복적 프로세스**로 구현하라. 힌트: (bⁿ/²)² = (b²)ⁿ/² 를 이용하고, 불변량 a·bⁿ을 유지한다.

```javascript
function fast_expt_iter(b, n) {
    return fast_expt_helper(1, b, n);
}

function fast_expt_helper(a, b, n) {
    return n === 0
           ? a
           : is_even(n)
             ? fast_expt_helper(a, b * b, n / 2)
             : fast_expt_helper(a * b, b, n - 1);
}
```

불변량: 매 단계에서 `a * b^n`의 값이 일정하다. 이것이 반복적 프로세스 설계의 핵심 기법이다.

### Exercise 1.19: 피보나치의 Θ(log n) 계산

피보나치 변환 T: (a, b) → (a + b, a)를 행렬로 표현하면 빠른 거듭제곱 기법을 적용하여 **Θ(log n)** 에 피보나치 수를 계산할 수 있다. 행렬의 제곱이 변환의 합성에 대응한다.

---

## 요약

- **재귀적 프로세스**는 지연된 연산의 체인이 확장 후 축소되며, Θ(n) 공간을 사용한다. **반복적 프로세스**는 고정된 수의 상태 변수로 진행 상황을 완전히 기술하며, Θ(1) 공간을 사용한다.
- **재귀적 함수 ≠ 재귀적 프로세스**. 재귀적 함수도 꼬리 재귀이면 반복적 프로세스를 생성한다.
- **트리 재귀**는 지수적 시간이 소요될 수 있지만, 문제의 구조를 자연스럽게 반영할 때 유용하다.
- **증가 차수(Θ 표기법)** 는 자원 소비의 성장률을 표현한다. "문제를 반으로 나누면 Θ(log n)"이라는 원리가 반복적으로 등장한다.
- **유클리드 알고리즘**은 GCD를 Θ(log n)에 계산하며, **페르마 검사**는 소수 판정을 Θ(log n)에 확률적으로 수행한다.
- 같은 문제에 대해 Θ(n), Θ(log n), Θ(√n) 등 전혀 다른 복잡도의 알고리즘이 가능하다. 알고리즘의 **설계**가 성능을 결정한다.

---

## 다른 섹션과의 관계

- **Section 1.1 (The Elements of Programming)**: `sqrt_iter`의 재귀가 사실 반복적 프로세스를 생성한다는 것을 이 섹션에서 이해할 수 있다. Section 1.1에서 "반복문 없이 재귀로 반복"이라고 했던 것의 정확한 의미가 밝혀진다.
- **Section 1.3 (Higher-Order Functions)**: 이 섹션에서 구현한 알고리즘들이 Section 1.3에서 고차 함수로 일반화된다. 예를 들어 `sum` 패턴, `accumulate` 패턴 등.
- **Section 2.2 (Hierarchical Data)**: 트리 재귀가 계층적 데이터 구조를 처리하는 자연스러운 방식으로 재등장한다. 리스트의 리스트를 다루는 `map`, `filter` 등에서 트리 재귀가 핵심이다.
- **Section 3.5 (Streams)**: 반복적 프로세스를 스트림으로 표현하는 방법을 다룬다. Newton의 제곱근 근사를 "추측값의 스트림"으로 표현할 수 있다.
- **Section 4.1 (The Metacircular Evaluator)**: 이 섹션에서 분석한 "함수 호출 시 무슨 일이 일어나는가"를 메타순환 평가기가 코드로 구현한다.
- **Section 5.4 (Explicit-Control Evaluator)**: 꼬리 재귀 최적화가 레지스터 머신 수준에서 어떻게 구현되는지를 보여준다. 반복적 프로세스가 상수 공간에서 실행되는 메커니즘이 드러난다.
