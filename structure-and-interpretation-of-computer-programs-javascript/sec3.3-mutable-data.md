# Section 3.3: Modeling with Mutable Data (변이 가능한 데이터로 모델링)

## 핵심 질문

데이터 구조 자체를 변경할 수 있다면(변이), 어떤 새로운 데이터 구조와 프로그래밍 패턴이 가능해지며, 어떤 새로운 문제가 등장하는가?

---

## 핵심 개념

| 개념 | 정의 |
|------|------|
| **변이자(Mutator)** | 데이터 구조를 변경하는 연산 — `set_head`, `set_tail` |
| **공유 구조(Shared structure)** | 여러 데이터 구조가 동일한 쌍을 공유하는 상태 |
| **큐(Queue)** | FIFO 방식의 변이 가능한 데이터 구조 |
| **테이블(Table)** | 키-값 쌍의 변이 가능한 컬렉션 |
| **정체성(Identity)** | 변이 가능한 데이터에서 "같은 객체"의 의미 |

---

## 1. 변이 가능한 리스트 구조

### 1.1 set_head와 set_tail

쌍의 구성 요소를 **변경**하는 변이자:

```javascript
const x = pair(1, 2);
set_head(x, 3);    // x는 이제 pair(3, 2)
set_tail(x, 4);    // x는 이제 pair(3, 4)
```

### 1.2 공유와 변이의 위험

```javascript
const x = list(1, 2);
const z1 = pair(x, x);         // x를 공유!

set_head(head(z1), "wow");
// z1 = pair(list("wow", 2), list("wow", 2))
// head(z1)과 tail(z1)이 같은 x를 가리키므로 둘 다 변경된다!
```

공유가 없다면:

```javascript
const z2 = pair(list(1, 2), list(1, 2));  // 독립적인 리스트
set_head(head(z2), "wow");
// z2 = pair(list("wow", 2), list(1, 2))
// 한쪽만 변경된다
```

> **핵심 통찰**: 변이와 공유가 결합되면 프로그램의 동작을 예측하기 어려워진다. 이것이 함수형 프로그래밍이 변이를 피하려는 근본적 이유다. 변이를 사용하면 데이터의 "정체성"이 중요해지고, `===`(같은 객체인가)와 `equal`(같은 값인가)의 구분이 필요해진다.

---

## 2. 큐 (Queues)

### 2.1 효율적인 큐 구현

리스트의 앞에서 꺼내고(`delete_queue`) 뒤에 넣는(`insert_queue`) FIFO 구조. 뒤에 넣으려면 리스트 끝을 알아야 하는데, **뒤쪽 포인터(rear pointer)** 를 유지하여 Θ(1)에 삽입한다:

```javascript
function make_queue() {
    return pair(null, null);  // (front_ptr, rear_ptr)
}

function insert_queue(queue, item) {
    const new_pair = pair(item, null);
    if (is_empty_queue(queue)) {
        set_head(queue, new_pair);
        set_tail(queue, new_pair);
    } else {
        set_tail(tail(queue), new_pair);
        set_tail(queue, new_pair);
    }
    return queue;
}
```

---

## 3. 테이블 (Tables)

### 3.1 1차원 테이블

키-값 쌍의 리스트:

```javascript
function lookup(key, table) {
    const record = assoc(key, tail(table));
    return record === undefined ? undefined : tail(record);
}

function insert(key, value, table) {
    const record = assoc(key, tail(table));
    if (record !== undefined) {
        set_tail(record, value);
    } else {
        set_tail(table, pair(pair(key, value), tail(table)));
    }
}
```

### 3.2 2차원 테이블

Section 2.4의 데이터 지향 프로그래밍에서 사용한 `put`/`get`이 여기서 구현된다.

---

## 4. 디지털 회로 시뮬레이터 (A Simulator for Digital Circuits)

변이 가능한 데이터의 가장 정교한 예제. 와이어(wire)에 신호가 전파되는 것을 시뮬레이션한다:

```javascript
function inverter(input, output) {
    function invert_input() {
        const new_value = logical_not(get_signal(input));
        after_delay(inverter_delay,
                    () => set_signal(output, new_value));
    }
    add_action(input, invert_input);
}

function and_gate(a1, a2, output) {
    function and_action() {
        const new_value = logical_and(get_signal(a1), get_signal(a2));
        after_delay(and_gate_delay,
                    () => set_signal(output, new_value));
    }
    add_action(a1, and_action);
    add_action(a2, and_action);
}
```

각 와이어가 **상태(현재 신호)** 와 **동작 리스트(신호 변경 시 실행할 함수들)** 를 가진다. 이것은 **이벤트 기반 프로그래밍** 또는 **콜백 패턴**의 원형이다.

> **핵심 통찰**: 회로 시뮬레이터는 대입, 변이 가능한 데이터, 지역 상태, 고차 함수가 모두 결합된 예제다. 와이어는 상태를 가진 객체이고, `add_action`은 콜백을 등록하며, 시뮬레이션은 이벤트 루프로 진행된다. 현대 프론트엔드 프레임워크의 반응형(reactive) 시스템과 놀랍도록 유사하다.

---

## 5. 제약 전파 시스템 (Constraint Propagation)

### 5.1 제약 기반 프로그래밍

섭씨-화씨 변환기를 **제약(constraint)** 으로 표현:

```
9 * C = 5 * (F - 32)
```

어느 방향으로든 계산 가능하다. C를 넣으면 F가 나오고, F를 넣으면 C가 나온다. 이것은 함수(단방향)가 아니라 **관계(양방향)** 다.

커넥터(connector)가 값을 가지며, 제약이 커넥터 간의 관계를 유지한다. 값이 설정되면 제약을 통해 다른 커넥터로 전파된다.

---

## 요약

- **변이자**(`set_head`, `set_tail`)를 도입하면 리스트, 큐, 테이블 등 효율적인 변이 가능 데이터 구조를 구축할 수 있다.
- **공유 구조 + 변이**는 예측하기 어려운 동작을 만든다. 정체성(identity)과 동등성(equality)의 구분이 중요해진다.
- **디지털 회로 시뮬레이터**는 상태, 변이, 고차 함수, 이벤트 기반 프로그래밍이 결합된 정교한 예제다.
- **제약 전파 시스템**은 함수(단방향)를 넘어 관계(양방향)로 프로그래밍하는 패러다임을 소개한다.

---

## 다른 섹션과의 관계

- **Section 2.1 (Data Abstraction)**: 쌍의 생성자/선택자에 변이자가 추가된다.
- **Section 2.5 (Generic Operations)**: 연산-타입 테이블이 여기서 변이 가능한 테이블로 구현된다.
- **Section 3.4 (Concurrency)**: 변이 가능한 공유 데이터가 동시성 문제의 원인이 된다.
- **Section 3.5 (Streams)**: 변이 없이 시간 변화를 모델링하는 대안. 회로 시뮬레이터의 스트림 버전이 제시된다.
