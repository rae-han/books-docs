# Section 2.2: Hierarchical Data and the Closure Property (계층적 데이터와 닫힘 성질)

## 핵심 질문

쌍을 이용해 구축한 복합 데이터에서, 결합 수단 자체가 만든 결과를 다시 결합할 수 있다는 **닫힘 성질(closure property)** 은 데이터 구조의 표현력에 어떤 영향을 미치는가?

---

## 핵심 개념

| 개념 | 정의 |
|------|------|
| **닫힘 성질(Closure property)** | 결합 수단으로 만든 결과를 그 결합 수단에 다시 사용할 수 있는 성질 |
| **리스트(List)** | 쌍의 체인으로 구성된 순차 데이터 구조 — `list(1, 2, 3)` |
| **트리(Tree)** | 원소가 다시 리스트인 리스트 — 계층적 데이터 구조 |
| **map** | 리스트의 각 원소에 함수를 적용하여 새 리스트를 생성하는 고차 함수 |
| **시퀀스 연산(Sequence operations)** | map, filter, accumulate 등 리스트를 신호 흐름처럼 처리하는 패턴 |

---

## 1. 시퀀스의 표현 (Representing Sequences)

### 1.1 리스트 구조

쌍의 닫힘 성질 덕분에 **리스트**를 구성할 수 있다:

```javascript
pair(1, pair(2, pair(3, pair(4, null))));
// 편의 표기: list(1, 2, 3, 4)
```

`null`은 빈 리스트를 나타낸다. 리스트는 다음과 같이 시각화된다:

```
[1, [2, [3, [4, null]]]]
```

### 1.2 리스트 연산

```javascript
function list_ref(items, n) {
    return n === 0
           ? head(items)
           : list_ref(tail(items), n - 1);
}

function length(items) {
    return is_null(items)
           ? 0
           : 1 + length(tail(items));
}

function append(list1, list2) {
    return is_null(list1)
           ? list2
           : pair(head(list1), append(tail(list1), list2));
}
```

### 1.3 리스트에 대한 map

**`map`** 은 리스트의 각 원소에 함수를 적용하여 새 리스트를 만드는 고차 함수다:

```javascript
function map(f, items) {
    return is_null(items)
           ? null
           : pair(f(head(items)), map(f, tail(items)));
}

map(x => x * x, list(1, 2, 3, 4));  // list(1, 4, 9, 16)
map(abs, list(-10, 2.5, -11.6, 17));  // list(10, 2.5, 11.6, 17)
```

> **핵심 통찰**: `map`은 단순한 편의 함수가 아니다. 이것은 **추상화 장벽**을 확립한다. `map`을 사용하면 "리스트의 각 원소를 변환한다"는 의도가 명확해지고, 리스트의 내부 구조(쌍의 체인)에 대한 지식이 숨겨진다. 리스트를 `head`/`tail`로 직접 분해하는 것과는 추상화 수준이 다르다.

---

## 2. 계층적 구조 (Hierarchical Structures)

### 2.1 트리로서의 리스트

리스트의 원소가 다시 리스트일 수 있다. 이것이 **트리**다:

```javascript
const x = pair(list(1, 2), list(3, 4));
// ((1, 2), (3, 4)) — 트리로 보면:
//       *
//      / \
//    (1,2) (3,4)
```

### 2.2 트리에 대한 재귀

트리의 잎(leaf)의 수를 세는 함수:

```javascript
function count_leaves(x) {
    return is_null(x)
           ? 0
           : !is_pair(x)
             ? 1
             : count_leaves(head(x)) + count_leaves(tail(x));
}
```

트리의 모든 잎에 함수를 적용하는 `tree_map`:

```javascript
function tree_map(f, tree) {
    return map(sub_tree =>
                   is_pair(sub_tree)
                   ? tree_map(f, sub_tree)
                   : f(sub_tree),
               tree);
}

tree_map(square, list(1, list(2, list(3, 4)), 5));
// list(1, list(4, list(9, 16)), 25)
```

---

## 3. 시퀀스 연산 (Sequence Operations)

### 3.1 신호 흐름으로서의 리스트 처리

복잡한 리스트 처리를 **filter → map → accumulate** 파이프라인으로 구성한다:

```javascript
function filter(predicate, sequence) {
    return is_null(sequence)
           ? null
           : predicate(head(sequence))
             ? pair(head(sequence), filter(predicate, tail(sequence)))
             : filter(predicate, tail(sequence));
}

function accumulate(op, initial, sequence) {
    return is_null(sequence)
           ? initial
           : op(head(sequence),
                accumulate(op, initial, tail(sequence)));
}
```

**홀수인 잎의 제곱의 합**:

```javascript
function sum_odd_squares(tree) {
    return accumulate((x, y) => x + y,
                      0,
                      map(square,
                          filter(is_odd,
                                 enumerate_tree(tree))));
}
```

**짝수 피보나치 수의 리스트**:

```javascript
function even_fibs(n) {
    return accumulate(pair,
                      null,
                      filter(is_even,
                             map(fib,
                                 enumerate_interval(0, n))));
}
```

> **핵심 통찰**: `enumerate → filter → map → accumulate` 파이프라인은 Unix의 파이프(`|`)와 같은 사고방식이다. 각 단계가 독립적이어서 재조합이 자유롭다. 이 패턴은 현대 JavaScript의 `Array.prototype.filter().map().reduce()`와 직접적으로 대응된다.

---

## 4. 그림 언어 (A Picture Language)

### 4.1 닫힘 성질의 극치

SICP는 **그림 언어(Picture Language)** 라는 작은 도메인 특화 언어를 구축하여, 닫힘 성질과 고차 함수의 힘을 극적으로 보여준다.

기본 요소인 **painter(그림자)** 를 `beside`, `below`, `flip_vert`, `flip_horiz` 같은 결합자로 조합한다:

```javascript
function right_split(painter, n) {
    if (n === 0) {
        return painter;
    } else {
        const smaller = right_split(painter, n - 1);
        return beside(painter, below(smaller, smaller));
    }
}

function corner_split(painter, n) {
    if (n === 0) {
        return painter;
    } else {
        const up = up_split(painter, n - 1);
        const right = right_split(painter, n - 1);
        const corner = corner_split(painter, n - 1);
        return beside(below(painter, up),
                      below(right, corner));
    }
}
```

이 그림 언어가 강력한 이유:

| 원리 | 적용 |
|------|------|
| 닫힘 성질 | `beside(p1, p2)`의 결과도 painter → 다시 `beside`에 사용 가능 |
| 고차 함수 | `square_of_four` — painter 변환 함수를 받아 4개의 그림을 조합 |
| 추상화 장벽 | painter의 실제 렌더링은 프레임 좌표 변환으로 구현되지만, 사용자는 조합만 신경 쓰면 됨 |

> **핵심 통찰**: 그림 언어는 Lisp/JavaScript의 문법을 사용하지만, 그 안에서 **새로운 언어**를 정의한 것이다. 이것이 Chapter 4에서 본격적으로 다루는 "메타언어적 추상화"의 맛보기다. 어떤 문제 영역에 맞는 언어를 설계하고 구현하는 것이 프로그래밍의 궁극적 형태다.

---

## 주요 예제

### 시퀀스 연산 파이프라인

같은 데이터에서 서로 다른 정보를 추출하는 두 프로그램이 **동일한 파이프라인 구조**를 공유함을 보여준다:

```
enumerate → filter → map → accumulate

예1: 트리의 잎 → 홀수만 → 제곱 → 합산
예2: 0~n 정수 → fib 적용 → 짝수만 → 리스트 구성
```

이 구조적 유사성은 `enumerate`, `filter`, `map`, `accumulate`를 모듈화해야만 보인다. 프로그램을 분해하지 않으면 숨겨져 있다.

---

## 연습 문제 하이라이트

### Exercise 2.17~2.18: 리스트의 마지막 원소와 역순

기본 리스트 연산을 직접 구현하는 연습.

### Exercise 2.19: 잔돈 바꾸기의 리스트 버전

Section 1.2.2의 `count_change`를 동전 종류를 리스트로 받도록 재작성. 데이터 추상화를 적용하면 동전 종류를 자유롭게 변경할 수 있다.

### Exercise 2.21: square_list의 두 가지 구현

```javascript
// map 사용
function square_list(items) {
    return map(x => x * x, items);
}
```

### Exercise 2.33: accumulate로 map, append, length 구현

```javascript
function map(f, sequence) {
    return accumulate((x, rest) => pair(f(x), rest), null, sequence);
}
```

`map`, `append`, `length`가 모두 `accumulate`의 특수한 경우임을 보여준다.

### Exercise 2.40~2.42: 중첩 매핑과 여덟 여왕 문제

`flatmap`을 활용한 중첩 매핑으로 순열과 조합을 생성하고, 여덟 여왕 문제를 해결한다. 시퀀스 연산의 표현력이 극대화되는 예제다.

---

## 요약

- **닫힘 성질**은 결합 수단으로 만든 결과를 다시 결합에 사용할 수 있는 성질이다. 쌍의 닫힘 성질 덕분에 리스트, 트리 등 계층적 데이터를 구축할 수 있다.
- **리스트**는 쌍의 체인이며, `map`, `filter`, `accumulate`라는 고차 함수로 처리한다.
- 복잡한 데이터 처리는 **enumerate → filter → map → accumulate** 파이프라인으로 구조화할 수 있다.
- **그림 언어**는 닫힘 성질, 고차 함수, 추상화 장벽을 결합한 도메인 특화 언어의 예시다.
- `map`과 `accumulate`는 추상화 장벽의 역할을 한다 — 리스트의 내부 구조를 숨기고 의도를 명확히 한다.

---

## 다른 섹션과의 관계

- **Section 2.1 (Data Abstraction)**: 쌍이라는 기본 접착제 위에 리스트와 트리가 구축된다. 추상화 장벽이 `map`, `filter` 수준으로 올라간다.
- **Section 2.3 (Symbolic Data)**: 리스트로 기호 표현식을 다루면서, 시퀀스 연산이 기호 계산에 적용된다.
- **Section 1.3 (Higher-Order Functions)**: `sum`, `product`, `accumulate` 패턴이 데이터 구조로 확장된다.
- **Section 3.3 (Mutable Data)**: 변이 가능한 리스트(큐, 테이블)를 도입하면 닫힘 성질이 새로운 차원으로 확장된다.
- **Section 3.5 (Streams)**: 리스트의 지연 평가 버전인 스트림이 무한 데이터 구조를 가능하게 한다.
- **Section 4.1 (Metacircular Evaluator)**: 프로그램 자체가 리스트로 표현된다. 이 섹션에서 배운 리스트 처리 기법이 인터프리터 구현의 기초가 된다.
