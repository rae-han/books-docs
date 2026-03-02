# Section 4.2: Lazy Evaluation (지연 평가)

## 핵심 질문

함수의 인수를 **호출 시점이 아니라 사용 시점에** 평가한다면, 프로그래밍 모델이 어떻게 달라지며 Section 3.5의 스트림을 언어 수준에서 지원할 수 있는가?

---

## 핵심 개념

| 개념 | 정의 |
|------|------|
| **지연 평가(Lazy evaluation)** | 표현식을 값이 실제로 필요한 시점까지 평가를 미루는 전략 |
| **정상 순서 평가(Normal-order evaluation)** | 모든 인수를 지연 평가하는 전략 — 적용 순서의 반대 |
| **썽크(Thunk)** | 아직 평가되지 않은 표현식 + 평가 환경을 담은 객체 |
| **강제(Force)** | 썽크를 실제로 평가하여 값을 얻는 연산 |
| **게으른 리스트(Lazy list)** | 지연 평가를 지원하는 언어에서 자연스럽게 생성되는 리스트 |

---

## 1. 정상 순서 평가와 지연 평가

### 1.1 적용 순서의 한계

Section 1.1에서 본 Exercise 1.5:

```javascript
function p() { return p(); }
function test(x, y) { return x === 0 ? 0 : y; }
test(0, p());  // 적용 순서: 무한 루프 / 정상 순서: 0
```

적용 순서는 `p()`를 먼저 평가하므로 무한 루프. 정상 순서는 `y`가 실제로 필요할 때만 평가하므로 `0` 반환.

### 1.2 지연 평가 인터프리터

Section 4.1의 메타순환 평가기를 수정하여 **정상 순서 평가**를 구현한다. 핵심 변경:

- **함수 적용 시**: 인수를 즉시 평가하지 않고 **썽크**로 감싼다
- **값이 필요할 때**: 썽크를 **강제(force)** 하여 평가한다
- **연산자, 조건 술어**: 값이 필요하므로 강제한다
- **함수 인수**: 지연된다

```javascript
function actual_value(exp, env) {
    return force_it(evaluate(exp, env));
}

function delay_it(exp, env) {
    return list("thunk", exp, env);
}

function force_it(obj) {
    if (is_thunk(obj)) {
        const result = actual_value(thunk_exp(obj), thunk_env(obj));
        set_head(obj, "evaluated_thunk");
        set_head(tail(obj), result);
        return result;
    } else if (is_evaluated_thunk(obj)) {
        return thunk_value(obj);
    } else {
        return obj;
    }
}
```

메모이제이션: 한 번 강제된 썽크는 결과를 저장하여 중복 평가를 방지한다.

---

## 2. 게으른 리스트 (Lazy Lists)

### 2.1 스트림이 필요 없어진다

지연 평가 인터프리터에서는 일반 `pair`가 자동으로 지연된다. Section 3.5의 스트림 전용 연산이 불필요해진다:

```javascript
// 지연 평가 인터프리터에서:
function integers_from(n) {
    return pair(n, integers_from(n + 1));
}
// pair의 두 번째 인수가 자동으로 지연되므로 무한 루프 없음!
```

> **핵심 통찰**: Section 3.5에서 스트림을 위해 `pair` 대신 `stream_pair`를 사용하고, `tail` 대신 `stream_tail`을 사용해야 했던 것은 JavaScript가 적용 순서를 사용하기 때문이었다. 지연 평가를 언어 수준에서 지원하면 이 구분이 사라진다. 리스트와 스트림이 **통합**된다.

---

## 3. 지연 평가의 절충

| 측면 | 적용 순서 (Applicative) | 정상 순서 (Normal) |
|------|------------------------|--------------------|
| 평가 시점 | 즉시 | 필요할 때 |
| 부작용 예측 | 쉬움 | 어려움 |
| 무한 데이터 | 특별한 구조 필요 | 자연스러움 |
| 성능 | 예측 가능 | 예측 어려움 (메모이제이션 필요) |
| 디버깅 | 쉬움 | 어려움 |

---

## 요약

- 메타순환 평가기를 수정하여 **정상 순서(지연) 평가** 인터프리터를 구현할 수 있다.
- **썽크**는 아직 평가되지 않은 표현식 + 환경을 담은 객체이며, 필요할 때 **강제**된다.
- 지연 평가를 지원하면 리스트와 스트림이 통합되어, 무한 데이터 구조가 자연스럽게 지원된다.
- 대입과 지연 평가의 결합은 예측하기 어려운 동작을 만들므로 주의가 필요하다.

---

## 다른 섹션과의 관계

- **Section 1.1 (The Elements of Programming)**: 적용 순서 vs 정상 순서의 차이가 실제 인터프리터로 구현된다.
- **Section 3.5 (Streams)**: 스트림을 위한 별도 연산이 불필요해진다. 게으른 리스트로 통합.
- **Section 4.1 (Metacircular Evaluator)**: 기본 평가기의 수정 버전. `evaluate`의 함수 적용 부분만 변경.
- **Section 4.3 (Nondeterministic Computing)**: 또 다른 평가 전략 변형.
