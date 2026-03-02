# Section 2.3: Symbolic Data (기호 데이터)

## 핵심 질문

숫자뿐 아니라 **기호(symbol)** 를 데이터로 다룰 수 있다면, 프로그램이 수학적 표현식이나 논리식을 직접 조작할 수 있지 않은가?

---

## 핵심 개념

| 개념 | 정의 |
|------|------|
| **기호(Symbol)** | 문자열로 표현되는 원자적 데이터 — `"x"`, `"+"`, `"deriv"` |
| **인용(Quotation)** | 표현식 자체를 데이터로 취급하는 메커니즘 |
| **기호 미분(Symbolic differentiation)** | 수학적 표현식의 도함수를 기호적으로 계산 |
| **집합 표현(Set representation)** | 동일한 추상 데이터를 다양한 방식으로 표현하는 예제 |
| **허프만 인코딩(Huffman encoding)** | 가변 길이 이진 코드를 트리로 표현하는 데이터 압축 기법 |

---

## 1. 인용 (Quotation)

### 1.1 기호의 필요성

지금까지 데이터는 숫자와 쌍뿐이었다. 기호를 도입하면 `"x"`, `"y"`, `"+"` 같은 이름 자체를 데이터로 다룰 수 있다.

SICP JavaScript Edition에서는 문자열을 기호로 사용한다:

```javascript
const a = 1;
const b = 2;
list("a", "b");           // list("a", "b") — 기호 "a"와 "b"의 리스트
list(a, b);                // list(1, 2) — 변수 a와 b의 값의 리스트
```

기호의 동등성 비교:

```javascript
"a" === "a";    // true
"a" === "b";    // false
```

### 1.2 기호를 포함하는 리스트

```javascript
function memq(item, x) {
    return is_null(x)
           ? null
           : item === head(x)
             ? x
             : memq(item, tail(x));
}

memq("apple", list("pear", "banana", "prune"));     // null
memq("apple", list("x", "sauce", "y", "apple", "pear"));
// list("apple", "pear")
```

---

## 2. 기호 미분 (Symbolic Differentiation)

### 2.1 미분 규칙의 프로그래밍

SICP의 가장 인상적인 예제 중 하나. 수학적 미분 규칙을 프로그램으로 번역한다:

| 규칙 | 수학 | 코드 |
|------|------|------|
| 상수의 미분 | dc/dx = 0 | `is_number(exp)` → `0` |
| 변수의 미분 | dx/dx = 1, dy/dx = 0 | `is_variable(exp)` → 같은 변수면 `1`, 다르면 `0` |
| 합의 미분 | d(u+v)/dx = du/dx + dv/dx | `is_sum(exp)` → `make_sum(deriv(addend, var), deriv(augend, var))` |
| 곱의 미분 | d(uv)/dx = u·dv/dx + v·du/dx | `is_product(exp)` → 곱 규칙 적용 |

```javascript
function deriv(exp, variable) {
    return is_number(exp)
           ? 0
           : is_variable(exp)
             ? is_same_variable(exp, variable) ? 1 : 0
             : is_sum(exp)
               ? make_sum(deriv(addend(exp), variable),
                          deriv(augend(exp), variable))
               : is_product(exp)
                 ? make_sum(make_product(multiplier(exp),
                                        deriv(multiplicand(exp), variable)),
                            make_product(deriv(multiplier(exp), variable),
                                        multiplicand(exp)))
                 : error(exp, "unknown expression type -- deriv");
}
```

### 2.2 표현식의 표현

합과 곱을 리스트로 표현한다:

```javascript
function make_sum(a1, a2) { return list("+", a1, a2); }
function make_product(m1, m2) { return list("*", m1, m2); }
function is_sum(x) { return is_pair(x) && head(x) === "+"; }
function addend(s) { return head(tail(s)); }
function augend(s) { return head(tail(tail(s))); }
```

실행 예:

```javascript
deriv(list("+", "x", 3), "x");
// list("+", 1, 0)  →  해석: 1 + 0

deriv(list("*", "x", "y"), "x");
// list("+", list("*", "x", 0), list("*", 1, "y"))
// 해석: x*0 + 1*y
```

### 2.3 단순화 (Simplification)

결과가 `list("+", 1, 0)` 같이 단순화되지 않은 형태다. 생성자에서 단순화 규칙을 적용한다:

```javascript
function make_sum(a1, a2) {
    return number_equal(a1, 0)
           ? a2
           : number_equal(a2, 0)
             ? a1
             : is_number(a1) && is_number(a2)
               ? a1 + a2
               : list("+", a1, a2);
}

function make_product(m1, m2) {
    return number_equal(m1, 0) || number_equal(m2, 0)
           ? 0
           : number_equal(m1, 1)
             ? m2
             : number_equal(m2, 1)
               ? m1
               : is_number(m1) && is_number(m2)
                 ? m1 * m2
                 : list("*", m1, m2);
}
```

이제 `deriv(list("*", "x", "y"), "x")`는 `"y"`를 반환한다.

> **핵심 통찰**: 미분 프로그램은 데이터 추상화의 힘을 극적으로 보여준다. `deriv` 함수는 미분 규칙만 알면 되고, 표현식의 구체적 표현(리스트)은 생성자와 선택자 뒤에 숨겨져 있다. 단순화를 추가할 때도 **`deriv`는 수정하지 않고** 생성자(`make_sum`, `make_product`)만 수정하면 된다.

---

## 3. 집합의 표현 (Representing Sets)

동일한 추상 데이터 타입(집합)을 **여러 가지 방식으로 표현**할 수 있음을 보여준다.

### 3.1 비순서 리스트 (Unordered Lists)

```javascript
function is_element_of_set(x, set) {
    return is_null(set)
           ? false
           : equal(x, head(set))
             ? true
             : is_element_of_set(x, tail(set));
}
```

| 연산 | 시간 복잡도 |
|------|-----------|
| `is_element_of_set` | Θ(n) |
| `adjoin_set` | Θ(n) |
| `intersection_set` | Θ(n²) |

### 3.2 순서 리스트 (Ordered Lists)

원소를 정렬된 순서로 유지하면 `intersection_set`이 Θ(n)으로 개선된다.

### 3.3 이진 탐색 트리 (Binary Search Trees)

트리를 리스트로 표현한다: `list(entry, left_branch, right_branch)`.

```javascript
function is_element_of_set(x, set) {
    return is_null(set)
           ? false
           : x === entry(set)
             ? true
             : x < entry(set)
               ? is_element_of_set(x, left_branch(set))
               : is_element_of_set(x, right_branch(set));
}
```

| 연산 | 시간 복잡도 |
|------|-----------|
| `is_element_of_set` | Θ(log n) (균형 트리) |
| `adjoin_set` | Θ(log n) (균형 트리) |

> **핵심 통찰**: 동일한 추상 인터페이스(`is_element_of_set`, `adjoin_set`, ...)를 유지하면서 내부 표현만 바꾸면 성능이 극적으로 변한다. 이것이 추상화 장벽의 실질적 이점이다 — 사용하는 코드를 수정하지 않고 성능을 개선할 수 있다.

---

## 4. 허프만 인코딩 트리 (Huffman Encoding Trees)

### 4.1 가변 길이 코드

고정 길이 코드(ASCII)와 달리, **빈도가 높은 문자에 짧은 코드**를 할당하면 전체 메시지 길이를 줄일 수 있다. 허프만 코드가 이를 최적으로 수행한다.

### 4.2 허프만 트리 구조

잎(leaf) 노드는 기호와 빈도를 담고, 내부 노드는 왼쪽/오른쪽 자식과 기호 집합, 총 빈도를 담는다:

```javascript
function make_leaf(symbol, weight) {
    return list("leaf", symbol, weight);
}

function make_code_tree(left, right) {
    return list(left,
                right,
                append(symbols(left), symbols(right)),
                weight(left) + weight(right));
}
```

### 4.3 디코딩

```javascript
function decode(bits, tree) {
    function decode_1(bits, current_branch) {
        if (is_null(bits)) {
            return null;
        } else {
            const next_branch = choose_branch(head(bits), current_branch);
            return is_leaf(next_branch)
                   ? pair(symbol_leaf(next_branch),
                          decode_1(tail(bits), tree))
                   : decode_1(tail(bits), next_branch);
        }
    }
    return decode_1(bits, tree);
}
```

트리와 리스트를 결합한 정교한 데이터 구조의 예시다.

---

## 요약

- **기호 데이터**를 도입하면 프로그램이 수학적 표현식, 논리식 등을 직접 조작할 수 있다.
- **기호 미분**은 데이터 추상화와 재귀의 결합이 수학적 규칙을 자연스럽게 프로그램으로 번역할 수 있음을 보여준다.
- **집합의 다중 표현**(비순서 리스트, 순서 리스트, 이진 탐색 트리)은 추상화 장벽 아래에서 표현을 교체하면 성능이 극적으로 변할 수 있음을 보여준다.
- **허프만 인코딩**은 트리와 리스트를 결합한 복합 데이터 구조의 실용적 예시다.

---

## 다른 섹션과의 관계

- **Section 2.1 (Data Abstraction)**: 기호 미분에서 추상화 장벽의 위력이 실증된다. 단순화를 추가할 때 `deriv`를 수정하지 않는다.
- **Section 2.4 (Multiple Representations)**: 집합의 다중 표현이 더 일반적인 "동일한 데이터에 대한 다중 표현"으로 확장된다.
- **Section 2.5 (Generic Operations)**: 기호 데이터와 수치 데이터를 통합하는 제네릭 산술 시스템이 구축된다.
- **Section 4.1 (Metacircular Evaluator)**: 기호 미분의 `deriv`와 메타순환 평가기의 `evaluate`는 놀랍도록 유사한 구조를 가진다 — 둘 다 표현식의 유형에 따라 분기하여 재귀적으로 처리한다.
- **Section 4.4 (Logic Programming)**: 기호 데이터 조작이 논리 프로그래밍의 기초가 된다. 패턴 매칭과 통일(unification)은 기호 처리의 정점이다.
