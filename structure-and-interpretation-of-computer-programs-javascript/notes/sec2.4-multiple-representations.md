# Section 2.4: Multiple Representations for Abstract Data (추상 데이터의 다중 표현)

## 핵심 질문

하나의 데이터 추상화에 **여러 가지 표현이 공존**해야 할 때, 어떻게 시스템을 설계하면 각 표현이 독립적으로 발전할 수 있는가?

---

## 핵심 개념

| 개념 | 정의 |
|------|------|
| **타입 태그(Type tag)** | 데이터에 표현 방식을 나타내는 태그를 부착하는 기법 |
| **데이터 지향 프로그래밍(Data-directed programming)** | 연산-타입 테이블을 사용하여 디스패치를 관리하는 기법 |
| **메시지 전달(Message passing)** | 데이터 객체가 연산 이름을 받아 스스로 처리하는 기법 |
| **부가적 설계(Additive design)** | 기존 코드를 수정하지 않고 새 표현을 추가할 수 있는 설계 |

---

## 1. 복소수의 두 가지 표현

### 1.1 문제 설정

복소수를 표현하는 두 가지 자연스러운 방법:

| 표현 | 구성 | 장점 |
|------|------|------|
| 직교 좌표(Rectangular) | 실수부 + 허수부 | 덧셈에 유리 |
| 극 좌표(Polar) | 크기 + 각도 | 곱셈에 유리 |

두 표현이 **동시에** 시스템에 존재해야 한다면? 한 팀은 직교 좌표를, 다른 팀은 극 좌표를 선호할 수 있다.

### 1.2 타입 태그 (Tagged Data)

각 데이터에 표현 방식을 나타내는 **태그**를 부착한다:

```javascript
function attach_tag(type_tag, contents) {
    return pair(type_tag, contents);
}
function type_tag(datum) { return head(datum); }
function contents(datum) { return tail(datum); }
```

```javascript
function make_from_real_imag_rectangular(x, y) {
    return attach_tag("rectangular", pair(x, y));
}

function make_from_mag_ang_polar(r, a) {
    return attach_tag("polar", pair(r, a));
}
```

선택자에서 태그를 검사하여 분기한다:

```javascript
function real_part(z) {
    return is_rectangular(z)
           ? real_part_rectangular(contents(z))
           : is_polar(z)
             ? real_part_polar(contents(z))
             : error(z, "unknown type -- real_part");
}
```

### 1.3 한계: 조건 분기의 증식

새 표현을 추가할 때마다 **모든 제네릭 연산의 조건 분기를 수정**해야 한다. 시스템이 커지면 유지보수가 불가능해진다.

---

## 2. 데이터 지향 프로그래밍 (Data-Directed Programming)

### 2.1 연산-타입 테이블

연산과 타입의 **2차원 테이블**로 디스패치를 관리한다:

|  | 직교 좌표 (rectangular) | 극 좌표 (polar) |
|--|------------------------|----------------|
| real_part | real_part_rectangular | real_part_polar |
| imag_part | imag_part_rectangular | imag_part_polar |
| magnitude | magnitude_rectangular | magnitude_polar |
| angle | angle_rectangular | angle_polar |

```javascript
function install_rectangular_package() {
    // 내부 함수 정의
    function real_part(z) { return head(z); }
    function imag_part(z) { return tail(z); }
    // ... 기타 연산

    // 테이블에 등록
    put("real_part", list("rectangular"), real_part);
    put("imag_part", list("rectangular"), imag_part);
    // ...
}
```

제네릭 연산은 테이블에서 적절한 함수를 찾아 적용한다:

```javascript
function apply_generic(op, args) {
    const type_tags = map(type_tag, args);
    const fun = get(op, type_tags);
    return fun !== undefined
           ? apply(fun, map(contents, args))
           : error(list(op, type_tags), "no method for these types");
}

function real_part(z) { return apply_generic("real_part", list(z)); }
function imag_part(z) { return apply_generic("imag_part", list(z)); }
```

### 2.2 부가적 설계 (Additive Design)

새 표현을 추가할 때 **기존 코드를 수정할 필요가 없다**. 새로운 패키지를 설치(install)하기만 하면 된다:

```javascript
function install_polar_package() {
    // 내부에서 극 좌표 연산 정의
    // 테이블에 등록
    put("real_part", list("polar"), ...);
    // ...
}
```

> **핵심 통찰**: 데이터 지향 프로그래밍은 시스템의 **부가적(additive) 확장**을 가능하게 한다. 새 타입이나 새 연산을 추가할 때 기존 코드를 건드리지 않는다. 이것은 객체 지향의 다형성(polymorphism)과 동일한 문제를 해결하지만, 함수와 테이블이라는 더 유연한 메커니즘을 사용한다.

---

## 3. 메시지 전달 (Message Passing)

데이터 지향 프로그래밍의 대안으로, **데이터 객체가 메시지를 받아 스스로 처리**하는 방식:

```javascript
function make_from_real_imag(x, y) {
    function dispatch(op) {
        return op === "real_part"
               ? x
               : op === "imag_part"
                 ? y
                 : op === "magnitude"
                   ? math_sqrt(x * x + y * y)
                   : op === "angle"
                     ? math_atan(y, x)
                     : error(op, "unknown op -- make_from_real_imag");
    }
    return dispatch;
}
```

사용:

```javascript
const z = make_from_real_imag(3, 4);
z("real_part");   // 3
z("magnitude");   // 5
```

객체가 **함수**로 표현된다 — Section 2.1의 "함수로 쌍 구현"과 동일한 원리다.

| 방식 | 새 타입 추가 | 새 연산 추가 |
|------|------------|------------|
| 데이터 지향 | 새 패키지 설치 (기존 수정 없음) | 각 패키지에 연산 추가 필요 |
| 메시지 전달 | 새 생성자 정의 (기존 수정 없음) | 각 생성자에 case 추가 필요 |

> **핵심 통찰**: 이것이 소프트웨어 설계에서 유명한 **Expression Problem**이다. 타입 추가가 쉬운 설계(메시지 전달/OOP)와 연산 추가가 쉬운 설계(데이터 지향/함수형) 사이의 근본적 긴장이다. SICP는 이 문제를 1980년대에 이미 명확하게 제시했다.

---

## 요약

- **타입 태그**로 데이터에 표현 방식을 부착하면 다중 표현이 공존할 수 있다.
- **데이터 지향 프로그래밍**은 연산-타입 테이블로 디스패치를 관리하며, 부가적 확장을 가능하게 한다.
- **메시지 전달**은 객체가 메시지를 받아 스스로 처리하는 방식이며, 객체 지향 프로그래밍의 핵심 아이디어와 일치한다.
- 두 방식 모두 장단점이 있으며, 새 **타입 추가** vs 새 **연산 추가**에 대한 근본적 긴장(Expression Problem)이 존재한다.

---

## 다른 섹션과의 관계

- **Section 2.1 (Data Abstraction)**: 추상화 장벽이 다중 표현의 기초다. 생성자/선택자를 유지하면서 내부 표현을 교체할 수 있다.
- **Section 2.3 (Symbolic Data)**: 타입 태그는 기호 데이터의 활용 사례다. `"rectangular"`, `"polar"` 같은 문자열 태그를 사용한다.
- **Section 2.5 (Generic Operations)**: 다중 표현을 더 확장하여 **타입 간 변환(coercion)** 과 **타입 계층(type hierarchy)** 을 도입한다.
- **Section 3.1 (Assignment and Local State)**: 메시지 전달 + 대입을 결합하면 상태를 가진 객체가 된다. 객체 지향 프로그래밍의 탄생이다.
- **Section 4.1 (Metacircular Evaluator)**: `evaluate` 함수가 표현식 타입에 따라 분기하는 것은 데이터 지향 프로그래밍과 동일한 패턴이다.
