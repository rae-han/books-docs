# Section 3.1: Assignment and Local State (대입과 지역 상태)

## 핵심 질문

지금까지의 프로그래밍은 순수 함수적이었다 — 같은 인수에 같은 결과를 반환했다. **대입(assignment)** 을 도입하면 무엇이 근본적으로 달라지며, 왜 그럼에도 필요한가?

---

## 핵심 개념

| 개념 | 정의 |
|------|------|
| **대입(Assignment)** | 이름에 연결된 값을 변경하는 연산 — `let x = 3;` 후 `x = 5;` |
| **지역 상태(Local state)** | 객체가 시간에 따라 변하는 내부 상태를 가지는 것 |
| **참조 투명성(Referential transparency)** | 표현식을 그 값으로 대체해도 프로그램 의미가 변하지 않는 성질 |
| **명령형 프로그래밍(Imperative programming)** | 대입을 사용하여 상태 변화를 기술하는 프로그래밍 스타일 |

---

## 1. 지역 상태 변수 (Local State Variables)

### 1.1 은행 계좌 예제

잔고가 100인 은행 계좌를 모델링한다. `withdraw(25)` → 75, 다시 `withdraw(25)` → 50. **같은 함수 호출인데 다른 결과**를 반환해야 한다:

```javascript
function make_withdraw(balance) {
    return amount => {
               if (balance >= amount) {
                   balance = balance - amount;  // 대입!
                   return balance;
               } else {
                   return "insufficient funds";
               }
           };
}

const W1 = make_withdraw(100);
W1(50);   // 50
W1(30);   // 20
W1(20);   // 0
W1(10);   // "insufficient funds"
```

`balance = balance - amount`이 **대입**이다. `balance`의 값이 호출할 때마다 변한다.

### 1.2 대입의 대가

대입 이전에는 **치환 모델**로 프로그램을 이해할 수 있었다. 대입을 도입하면:

```javascript
const W1 = make_withdraw(100);
const W2 = make_withdraw(100);

W1(50);  // 50
W2(70);  // 30 — W1과 W2는 독립적인 상태를 가진다
```

`W1`과 `W2`는 `make_withdraw(100)`으로 동일하게 생성되었지만, 각자 **독립적인 `balance`** 를 가진다. 치환 모델에서는 이것을 설명할 수 없다.

> **핵심 통찰**: 대입은 **시간(time)** 의 개념을 프로그래밍에 도입한다. 대입 이전에는 `f(x)`의 값이 언제 평가하든 동일했다(참조 투명성). 대입 이후에는 "언제" 평가하느냐가 중요해진다. 이것이 Section 3.4의 동시성 문제로 이어진다.

---

## 2. 대입의 이점 (Benefits of Assignment)

### 2.1 캡슐화

몬테카를로 시뮬레이션에서 난수 생성기의 상태를 캡슐화할 수 있다:

```javascript
function make_rand() {
    let x = random_init;
    return () => {
               x = rand_update(x);
               return x;
           };
}

const rand = make_rand();
```

`rand`를 호출할 때마다 다른 난수를 반환하지만, 내부 상태 `x`는 외부에서 접근할 수 없다. 상태가 캡슐화된다.

### 2.2 대입 없이 같은 효과를 얻는 방법

대입 없이도 같은 계산을 수행할 수 있지만, 난수 상태를 **명시적으로 전달**해야 한다:

```javascript
function rand_update_approach(x) {
    // x를 매번 인수로 전달해야 한다
    const x1 = rand_update(x);
    const x2 = rand_update(x1);
    // ...
}
```

상태 전달이 프로그램 전체에 퍼져나가 코드가 복잡해진다. 대입은 이 복잡성을 **지역화**한다.

---

## 3. 대입의 비용 (Costs of Assignment)

### 3.1 참조 투명성의 상실

대입 이전:

```javascript
const x = 10;
// x + x 는 항상 20. x를 10으로 치환 가능.
```

대입 이후:

```javascript
let x = 10;
x = x + 1;
// 이제 x는 11. "x + x"의 결과는 시점에 따라 다르다.
```

"같음(sameness)"의 의미가 복잡해진다. `W1`과 `W2`는 "같은가"? 생성 방식은 같지만 독립적 상태를 가진다.

### 3.2 함수형 프로그래밍 vs 명령형 프로그래밍

| 함수형 프로그래밍 | 명령형 프로그래밍 |
|-----------------|-----------------|
| 대입 없음 | 대입 사용 |
| 참조 투명성 유지 | 참조 투명성 상실 |
| 치환 모델로 추론 가능 | 환경 모델 필요 (Section 3.2) |
| 시간 독립적 | 시간 의존적 |
| 동시성에 안전 | 동시성 문제 발생 가능 |

> **핵심 통찰**: SICP는 대입의 도입을 "낙원에서의 추방"에 비유한다. 치환 모델이라는 단순하고 우아한 세계를 떠나, 시간과 정체성이라는 복잡한 현실로 들어간다. 그러나 현실 세계를 모델링하려면 이 복잡성을 받아들여야 한다.

---

## 요약

- **대입**은 이름에 연결된 값을 변경하며, 지역 상태를 가진 객체를 만들 수 있게 한다.
- 대입은 **캡슐화**를 통해 모듈성을 높이지만, **참조 투명성**을 파괴하고 **치환 모델**을 무력화한다.
- "같음"의 의미가 **정체성(identity)** 의 문제로 바뀐다 — 동일한 방식으로 생성된 두 객체가 다를 수 있다.
- 함수형 프로그래밍과 명령형 프로그래밍 사이의 근본적 긴장이 드러난다.

---

## 다른 섹션과의 관계

- **Section 1.1 (The Elements of Programming)**: 치환 모델이 여기서 한계에 도달한다. 대입을 설명하려면 새로운 모델이 필요하다.
- **Section 2.4 (Multiple Representations)**: 메시지 전달 + 대입 = 상태를 가진 객체. OOP의 본질이다.
- **Section 3.2 (The Environment Model)**: 대입을 설명하는 새로운 평가 모델이 도입된다.
- **Section 3.4 (Concurrency)**: 대입이 도입한 "시간" 문제가 동시성에서 폭발한다.
- **Section 3.5 (Streams)**: 대입 없이 시간 변화를 모델링하는 대안을 제시한다.
