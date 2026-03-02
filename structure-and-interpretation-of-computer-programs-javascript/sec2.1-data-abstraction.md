# Section 2.1: Introduction to Data Abstraction (데이터 추상화 입문)

## 핵심 질문

데이터를 "사용하는 방법"과 "표현하는 방법"을 분리한다는 것은 무엇을 의미하며, 이 분리가 왜 프로그램 설계의 핵심인가?

---

## 핵심 개념

| 개념 | 정의 |
|------|------|
| **데이터 추상화(Data abstraction)** | 데이터의 사용과 표현을 분리하는 프로그래밍 방법론 |
| **추상화 장벽(Abstraction barrier)** | 사용 인터페이스와 구현 세부사항을 분리하는 경계 |
| **쌍(Pair)** | 두 값을 묶는 복합 데이터의 기본 단위 — `pair(a, b)` |
| **생성자(Constructor)** | 데이터 객체를 생성하는 함수 — `make_rat(n, d)` |
| **선택자(Selector)** | 데이터 객체의 구성 요소를 추출하는 함수 — `numer(x)`, `denom(x)` |
| **위시풀 씽킹(Wishful thinking)** | 아직 구현하지 않은 함수가 존재한다고 가정하고 설계하는 전략 |

---

## 1. 복합 데이터의 필요성

### 1.1 왜 데이터를 결합해야 하는가

Section 1에서는 함수로 추상화를 구축했다. 그러나 숫자만으로는 "유리수", "점", "구간" 같은 복합 개념을 자연스럽게 표현할 수 없다.

유리수 산술을 생각하자. 분자와 분모가 항상 짝으로 다뤄져야 한다. 이 둘을 별개의 변수로 관리하면:

```javascript
// 복합 데이터 없이: 분자와 분모를 따로 관리
function add_rat(n1, d1, n2, d2) {
    return ???;  // 결과의 분자와 분모를 동시에 반환할 수 없다!
}
```

반환값이 두 개(분자와 분모)인데, 함수는 하나의 값만 반환할 수 있다. **복합 데이터**가 필요한 이유다.

### 1.2 추상화 장벽의 효과

복합 데이터를 도입하면:
- 프로그램의 **모듈성**이 높아진다
- 프로그래밍 언어의 **표현력**이 증가한다
- 데이터 표현을 **독립적으로 변경**할 수 있다

---

## 2. 유리수 연산 (Rational Number Arithmetic)

### 2.1 위시풀 씽킹 (Wishful Thinking)

아직 유리수를 어떻게 표현할지 결정하지 않았다. 하지만 **생성자와 선택자가 존재한다고 가정**하고 연산을 먼저 설계한다:

- `make_rat(n, d)` — 분자 n, 분모 d인 유리수를 생성
- `numer(x)` — 유리수 x의 분자
- `denom(x)` — 유리수 x의 분모

이제 유리수 산술을 구현할 수 있다:

```javascript
function add_rat(x, y) {
    return make_rat(numer(x) * denom(y) + numer(y) * denom(x),
                    denom(x) * denom(y));
}

function sub_rat(x, y) {
    return make_rat(numer(x) * denom(y) - numer(y) * denom(x),
                    denom(x) * denom(y));
}

function mul_rat(x, y) {
    return make_rat(numer(x) * numer(y),
                    denom(x) * denom(y));
}

function div_rat(x, y) {
    return make_rat(numer(x) * denom(y),
                    denom(x) * numer(y));
}

function equal_rat(x, y) {
    return numer(x) * denom(y) === numer(y) * denom(x);
}
```

> **핵심 통찰**: 위시풀 씽킹은 단순한 지연이 아니다. 이것은 **설계 전략**이다. 생성자와 선택자가 올바르게 동작한다고 가정하면, 그 위에 구축되는 연산을 **데이터 표현에 독립적으로** 설계할 수 있다. 이 전략은 소프트웨어 엔지니어링 전반에서 핵심적인 역할을 한다.

### 2.2 쌍 (Pairs)

JavaScript에서 두 값을 묶는 기본 단위는 **쌍(pair)** 이다:

```javascript
const x = pair(1, 2);
head(x);  // 1
tail(x);  // 2
```

- `pair(a, b)` — a와 b를 묶어 쌍을 생성
- `head(p)` — 쌍의 첫 번째 요소
- `tail(p)` — 쌍의 두 번째 요소

쌍은 중첩할 수 있다:

```javascript
const x = pair(1, pair(2, 3));
head(x);           // 1
head(tail(x));     // 2
tail(tail(x));     // 3
```

### 2.3 유리수의 구현

이제 쌍을 사용하여 생성자와 선택자를 구현한다:

```javascript
function make_rat(n, d) {
    const g = gcd(n, d);
    return pair(n / g, d / g);
}

function numer(x) {
    return head(x);
}

function denom(x) {
    return tail(x);
}
```

`gcd`를 사용하여 생성 시점에 약분한다:

```javascript
function print_rat(x) {
    return display(stringify(numer(x)) + " / " + stringify(denom(x)));
}

const one_half = make_rat(1, 2);
print_rat(one_half);  // "1 / 2"

const one_third = make_rat(1, 3);
print_rat(add_rat(one_half, one_third));  // "5 / 6"
print_rat(add_rat(one_third, one_third));  // "2 / 3"
```

---

## 3. 추상화 장벽 (Abstraction Barriers)

### 3.1 층위 구조

유리수 시스템은 여러 층위(layer)로 구성된다:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  유리수를 사용하는 프로그램
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  add_rat  sub_rat  mul_rat  ...       ← 유리수 연산
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  make_rat  numer  denom               ← 생성자/선택자
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  pair  head  tail                     ← 쌍 연산
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

각 수평선이 **추상화 장벽**이다. 장벽 위의 코드는 장벽 아래의 구현 세부사항에 의존하지 않는다.

### 3.2 장벽 위반의 위험

만약 `add_rat`에서 `numer`와 `denom` 대신 `head`와 `tail`을 직접 사용한다면?

```javascript
// 나쁜 예: 추상화 장벽을 뚫는 구현
function add_rat(x, y) {
    return pair(head(x) * tail(y) + head(y) * tail(x),
                tail(x) * tail(y));
}
```

동작은 하지만, `make_rat`의 구현을 바꾸면(예: 쌍 대신 배열 사용) `add_rat`도 수정해야 한다. 추상화 장벽을 지키면 변경이 국소화된다.

> **핵심 통찰**: 추상화 장벽은 단순히 "좋은 습관"이 아니다. 이것은 **변경의 전파를 차단**하는 구조적 방어선이다. Section 2.4에서 이 원리가 "다중 표현"으로 확장되고, Section 2.5에서 "제네릭 연산"으로 정점에 달한다.

---

## 4. 데이터란 무엇인가 (What Is Meant by Data?)

### 4.1 데이터의 조건적 정의

`pair`, `head`, `tail`이 데이터 구현인가? 어떤 조건을 만족해야 "쌍"이라 할 수 있는가?

**쌍이 만족해야 할 조건**: 임의의 x, y에 대해

```
head(pair(x, y)) === x
tail(pair(x, y)) === y
```

이 조건만 만족하면, 구현 방식은 상관없다. 놀랍게도, **함수만으로** 쌍을 구현할 수 있다:

```javascript
function pair(x, y) {
    return m => m === 0 ? x : y;
}

function head(z) {
    return z(0);
}

function tail(z) {
    return z(1);
}
```

`pair(1, 2)`는 "0을 받으면 1을, 아니면 2를 반환하는 함수"를 반환한다. 데이터 구조가 아니라 **함수**다!

검증:

```javascript
head(pair(1, 2))  →  pair(1, 2)(0)  →  (m => m === 0 ? 1 : 2)(0)  →  1  ✓
tail(pair(1, 2))  →  pair(1, 2)(1)  →  (m => m === 0 ? 1 : 2)(1)  →  2  ✓
```

### 4.2 Church 인코딩

더 나아가, 0과 1이라는 숫자조차 없이 쌍을 구현할 수 있다:

```javascript
function pair(x, y) {
    return f => f(x, y);
}

function head(z) {
    return z((p, q) => p);
}

function tail(z) {
    return z((p, q) => q);
}
```

이것이 **처치 인코딩(Church encoding)** 의 일부다. 데이터와 함수의 경계가 완전히 사라진다.

> **핵심 통찰**: 이 예제는 SICP 전체에서 가장 철학적인 통찰 중 하나다. **데이터는 특정 조건을 만족하는 함수의 집합으로 정의할 수 있다.** 데이터와 코드의 경계는 우리가 생각하는 것보다 훨씬 유동적이다. 이 주제는 Chapter 4에서 "코드로서의 데이터, 데이터로서의 코드"로 정점에 달한다.

---

## 주요 예제

### 유리수 산술 시스템

이 예제는 데이터 추상화의 원리를 완전히 보여주는 자기 완결적 시스템이다:

1. **생성자/선택자**로 추상화 장벽 구축 (`make_rat`, `numer`, `denom`)
2. 장벽 위에 **연산** 구현 (`add_rat`, `mul_rat`, ...)
3. 장벽 아래에서 **표현** 구현 (쌍 사용)
4. 표현을 바꿔도 연산은 변경 불필요

약분을 생성 시점에 할 수도 있고, 선택 시점에 할 수도 있다:

```javascript
// 대안: 선택 시점에 약분
function make_rat(n, d) {
    return pair(n, d);
}

function numer(x) {
    const g = gcd(head(x), tail(x));
    return head(x) / g;
}

function denom(x) {
    const g = gcd(head(x), tail(x));
    return tail(x) / g;
}
```

두 구현 모두 동일한 외부 동작을 제공한다. 이것이 추상화 장벽의 힘이다.

---

## 연습 문제 하이라이트

### Exercise 2.1: 부호 처리가 개선된 make_rat

양수 유리수는 분자와 분모가 모두 양수, 음수 유리수는 분자만 음수가 되도록 `make_rat`을 개선하라:

```javascript
function make_rat(n, d) {
    const g = gcd(abs(n), abs(d));
    return d < 0
           ? pair(-n / g, -d / g)
           : pair(n / g, d / g);
}
```

### Exercise 2.4: 함수로 쌍 구현 (Church Pairs)

`pair`, `head`, `tail`을 함수만으로 구현하라:

```javascript
function pair(x, y) {
    return f => f(x, y);
}

function head(z) {
    return z((p, q) => p);
}

// tail을 구현하라:
function tail(z) {
    return z((p, q) => q);
}
```

### Exercise 2.6: Church 수 (Church Numerals)

0과 1조차 함수로 표현할 수 있다:

```javascript
const zero = f => x => x;

function add_1(n) {
    return f => x => f(n(f)(x));
}
```

- `zero`는 f를 **0번** 적용하는 함수
- `add_1(zero)` = `one` = f를 **1번** 적용하는 함수
- `add_1(one)` = `two` = f를 **2번** 적용하는 함수

자연수가 **"함수를 n번 적용하는 것"** 으로 정의된다. 이것이 Church 수의 본질이다.

---

## 요약

- **데이터 추상화**는 데이터의 사용과 표현을 **생성자와 선택자**로 분리한다.
- **추상화 장벽**은 프로그램을 층위로 나누어, 한 층의 변경이 다른 층에 영향을 미치지 않게 한다.
- **위시풀 씽킹**은 아직 구현하지 않은 인터페이스가 존재한다고 가정하고 설계하는 강력한 전략이다.
- **쌍(pair)** 은 복합 데이터를 구축하는 기본 접착제이며, 함수만으로도 구현할 수 있다.
- 데이터는 특정 **조건(계약)** 을 만족하는 함수의 집합으로 정의할 수 있다. 데이터와 함수의 경계는 유동적이다.

---

## 다른 섹션과의 관계

- **Section 1.3 (Higher-Order Functions)**: 함수를 일급 시민으로 다루는 능력이 데이터 추상화의 기초가 된다. Church 인코딩은 함수만으로 데이터 구조를 구현할 수 있음을 보여준다.
- **Section 2.2 (Hierarchical Data)**: 쌍을 중첩하여 리스트, 트리 등 계층적 데이터 구조를 구축한다. "닫힘 성질"이 핵심이다.
- **Section 2.3 (Symbolic Data)**: 숫자뿐 아니라 기호를 데이터로 다루면서 데이터 추상화의 범위가 확장된다.
- **Section 2.4 (Multiple Representations)**: 하나의 추상화에 **여러 가지 표현**이 공존할 수 있게 한다. 추상화 장벽이 다중 표현의 기초다.
- **Section 3.3 (Mutable Data)**: 변이 가능한 데이터를 도입하면 `pair`가 `set_head`, `set_tail`로 확장되면서, 데이터의 정체성(identity) 문제가 등장한다.
