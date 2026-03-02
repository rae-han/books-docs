# Section 2.5: Systems with Generic Operations (제네릭 연산 시스템)

## 핵심 질문

서로 다른 타입의 데이터에 대해 **같은 연산(add, mul 등)** 이 다르게 동작해야 할 때, 타입 간 변환과 타입 계층을 포함한 범용적인 시스템을 어떻게 설계하는가?

---

## 핵심 개념

| 개념 | 정의 |
|------|------|
| **제네릭 연산(Generic operation)** | 여러 타입에 대해 동작하는 연산 — `add(x, y)`가 정수, 유리수, 복소수 모두에서 동작 |
| **타입 강제 변환(Coercion)** | 한 타입을 다른 타입으로 자동 변환하는 기법 |
| **타입 계층(Type hierarchy)** | 타입 간의 하위-상위 관계 — 정수 ⊂ 유리수 ⊂ 실수 ⊂ 복소수 |
| **타입 올림(Raising)** | 하위 타입을 상위 타입으로 변환 |
| **타입 내림(Dropping/Simplifying)** | 가능하면 상위 타입을 하위 타입으로 단순화 |

---

## 1. 제네릭 산술 시스템

### 1.1 시스템 구조

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  add  sub  mul  div                    ← 제네릭 연산
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  apply_generic (타입 태그 기반 디스패치)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  정수 패키지  유리수 패키지  복소수 패키지  ← 타입별 구현
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                                복소수 내부:
                                직교/극 좌표 패키지
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

```javascript
function add(x, y) { return apply_generic("add", list(x, y)); }
function sub(x, y) { return apply_generic("sub", list(x, y)); }
function mul(x, y) { return apply_generic("mul", list(x, y)); }
function div(x, y) { return apply_generic("div", list(x, y)); }
```

각 패키지가 자신의 타입에 대한 연산을 테이블에 등록한다. `apply_generic`이 인수의 타입 태그를 보고 적절한 구현을 찾아 호출한다.

### 1.2 타입 간 연산의 문제

`add(정수, 복소수)` — 서로 다른 타입의 인수는 어떻게 처리하는가?

**나이브한 접근**: 모든 타입 쌍에 대한 크로스 타입 연산을 등록한다. n개 타입이 있으면 n² 개의 조합이 필요하다. 비현실적이다.

---

## 2. 타입 강제 변환 (Coercion)

### 2.1 강제 변환 테이블

타입 간 변환 함수를 별도 테이블에 등록한다:

```javascript
put_coercion("integer", "rational", integer_to_rational);
put_coercion("rational", "complex", rational_to_complex);
```

`apply_generic`이 같은 타입의 연산을 찾지 못하면, 한 인수를 다른 인수의 타입으로 변환하여 재시도한다.

### 2.2 타입 계층과 타워 (Type Tower)

수학적 수 체계는 자연스러운 **타워(tower)** 구조를 형성한다:

```
정수 → 유리수 → 실수 → 복소수
  ↑                          ↑
 하위                       상위
```

**타입 올림(Raising)**: 하위 → 상위. 정수 3을 복소수 3+0i로 변환.
**타입 내림(Dropping)**: 상위 → 하위. 복소수 3+0i를 정수 3으로 단순화.

```javascript
function raise(x) { return apply_generic("raise", list(x)); }

// 정수 패키지에서:
put("raise", list("integer"),
    n => make_rational(n, 1));

// 유리수 패키지에서:
put("raise", list("rational"),
    x => make_complex_from_real_imag(numer(x) / denom(x), 0));
```

> **핵심 통찰**: 타입 계층은 수학의 수 체계만의 문제가 아니다. 프로그래밍 언어의 타입 시스템, 객체 지향의 상속 계층, 데이터베이스의 스키마 진화 등에서 동일한 문제가 반복된다. SICP는 이 문제의 본질을 추상적으로 다루면서, 단순한 타워가 아닌 DAG(방향 비순환 그래프) 형태의 복잡한 타입 관계도 언급한다.

---

## 3. 다항식 연산 (Polynomial Arithmetic)

### 3.1 다항식을 제네릭 시스템에 통합

다항식도 하나의 "타입"으로 제네릭 산술 시스템에 추가할 수 있다:

```javascript
function install_polynomial_package() {
    // 내부 표현: 변수 + 항 리스트
    function make_poly(variable, term_list) {
        return pair(variable, term_list);
    }

    function add_poly(p1, p2) {
        return is_same_variable(variable(p1), variable(p2))
               ? make_poly(variable(p1),
                           add_terms(term_list(p1), term_list(p2)))
               : error(list(p1, p2), "polys not in same var -- add_poly");
    }

    // 테이블에 등록
    put("add", list("polynomial", "polynomial"),
        (p1, p2) => tag(add_poly(p1, p2)));
}
```

### 3.2 계수의 제네릭 연산

다항식의 **계수(coefficient)** 가 정수, 유리수, 복소수, 심지어 **다항식**(다항식의 다항식!)일 수 있다. 계수에 대한 연산에 `add`, `mul` 같은 제네릭 연산을 사용하면 이 모든 경우가 자동으로 처리된다.

```
3x² + 2x + 1                    → 계수가 정수인 다항식
(3/4)x² + (2/3)x + 1/2          → 계수가 유리수인 다항식
(2+3i)x² + (1-i)x + 4           → 계수가 복소수인 다항식
(y² + 1)x² + (2y - 1)x + y³    → 계수가 다항식인 다항식!
```

> **핵심 통찰**: 제네릭 연산의 진정한 힘은 **재귀적 적용**에 있다. 다항식의 계수가 다항식일 수 있으므로, 다항식 덧셈은 계수의 덧셈을 호출하고, 계수가 다항식이면 다시 다항식 덧셈이 호출된다. 추상화 장벽과 제네릭 디스패치가 결합되어 무한한 깊이의 조합이 자동으로 동작한다.

---

## 요약

- **제네릭 연산 시스템**은 여러 타입에 대해 통일된 인터페이스(`add`, `mul` 등)를 제공하며, 데이터 지향 프로그래밍으로 구현한다.
- **타입 강제 변환**은 서로 다른 타입 간의 연산을 가능하게 하며, **타입 계층(타워)** 구조로 체계화된다.
- **다항식 산술**은 제네릭 시스템의 표현력을 극대화하는 예제로, 계수 자체가 제네릭 연산을 사용하므로 재귀적 조합이 가능하다.
- 제네릭 시스템의 설계는 **부가적(additive)** 이어야 한다 — 새 타입 추가 시 기존 코드 수정이 최소화되어야 한다.

---

## 다른 섹션과의 관계

- **Section 2.4 (Multiple Representations)**: 타입 태그와 데이터 지향 프로그래밍이 이 섹션의 기초다.
- **Section 2.1 (Data Abstraction)**: 추상화 장벽이 제네릭 시스템의 각 층위를 분리한다.
- **Section 3.3 (Mutable Data)**: 연산-타입 테이블을 변이 가능한 데이터(해시 테이블)로 구현한다.
- **Section 4.1 (Metacircular Evaluator)**: 평가기의 `evaluate` 함수는 표현식 타입에 따라 다른 처리를 하는 제네릭 연산이다.
