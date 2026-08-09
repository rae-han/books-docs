# Section 3.5: Streams (스트림)

## 핵심 질문

변이(대입)를 사용하지 않으면서도 시간에 따라 변하는 현상을 모델링할 수 있는가? 무한한 데이터 구조를 유한한 메모리로 다룰 수 있는가?

---

## 핵심 개념

| 개념 | 정의 |
|------|------|
| **스트림(Stream)** | 지연 평가되는 리스트 — 원소가 필요할 때만 계산됨 |
| **지연 평가(Lazy evaluation)** | 표현식을 값이 필요한 시점까지 평가를 미루는 전략 |
| **메모이제이션(Memoization)** | 이전에 계산한 값을 캐시하여 중복 계산을 방지하는 기법 |
| **암묵적 정의(Implicit definition)** | 스트림을 자기 자신을 참조하여 정의하는 기법 |

---

## 1. 스트림의 기본 아이디어

### 1.1 동기: 시퀀스 연산의 효율 문제

Section 2.2의 `enumerate → filter → map → accumulate` 파이프라인은 우아하지만, 각 단계에서 **전체 리스트를 생성**한다. 10,000개 원소 중 두 번째 소수만 필요해도 10,000개를 모두 처리해야 한다.

### 1.2 지연 평가에 의한 해결

스트림은 **필요할 때만 원소를 계산**한다:

```javascript
function stream_ref(s, n) {
    return n === 0
           ? head(s)
           : stream_ref(stream_tail(s), n - 1);
}
```

`stream_tail`은 즉시 평가하지 않고, 호출될 때 비로소 다음 원소를 계산한다.

```javascript
const ones = pair(1, () => ones);  // 무한 스트림: 1, 1, 1, ...
```

---

## 2. 무한 스트림 (Infinite Streams)

### 2.1 정수 스트림

```javascript
function integers_starting_from(n) {
    return pair(n, () => integers_starting_from(n + 1));
}

const integers = integers_starting_from(1);
// 1, 2, 3, 4, 5, ... (무한!)
```

### 2.2 에라토스테네스의 체 (Sieve of Eratosthenes)

```javascript
function sieve(stream) {
    return pair(head(stream),
                () => sieve(
                          stream_filter(
                              x => x % head(stream) !== 0,
                              stream_tail(stream))));
}

const primes = sieve(integers_starting_from(2));
// 2, 3, 5, 7, 11, 13, ...
```

무한한 소수의 스트림! 각 소수는 **필요할 때만** 계산된다.

> **핵심 통찰**: 에라토스테네스의 체를 스트림으로 표현하면, 알고리즘의 수학적 정의와 프로그램이 거의 동일해진다. "2부터 시작하여, 현재 수의 배수를 모두 걸러내고, 다음 수로 진행"이라는 알고리즘 기술이 그대로 코드가 된다.

### 2.3 암묵적 정의 (Implicit Definitions)

스트림을 **자기 자신을 참조**하여 정의할 수 있다:

```javascript
const ones = pair(1, () => ones);

const integers = pair(1, () => add_streams(ones, integers));
// integers = 1, 2, 3, 4, 5, ...
// 왜? integers = 1, (1+1), (1+2), (1+3), ... = 1, 2, 3, 4, ...

const fibs = pair(0, () => pair(1, () => add_streams(stream_tail(fibs), fibs)));
// fibs = 0, 1, 1, 2, 3, 5, 8, 13, ...
```

피보나치 수열의 수학적 정의 `fib(n) = fib(n-1) + fib(n-2)`가 스트림의 암묵적 정의로 직접 번역된다.

---

## 3. 스트림으로 시뮬레이션

### 3.1 뉴턴 방법의 스트림 표현

Section 1.1의 제곱근 근사를 "추측값의 무한 스트림"으로 표현:

```javascript
function sqrt_stream(x) {
    const guesses = pair(1, () => stream_map(
                                      guess => average(guess, x / guess),
                                      guesses));
    return guesses;
}

// sqrt_stream(2) = 1, 1.5, 1.4167, 1.4142, 1.4142, ...
```

반복 루프가 아니라 **값의 무한 시퀀스**로 계산을 표현한다.

### 3.2 π의 근사 스트림

라이프니츠 급수의 부분합을 스트림으로:

```javascript
const pi_stream = scale_stream(partial_sums(pi_summands(1)), 4);
// 4, 2.667, 3.467, 2.895, 3.340, ... (π에 느리게 수렴)
```

오일러 가속기(Euler transform)를 적용하면 수렴 속도가 극적으로 빨라진다. 가속기를 **무한히 반복** 적용하는 "테이블로(tableau)"도 스트림으로 자연스럽게 표현된다.

---

## 4. 스트림과 대입의 관계

### 4.1 스트림 vs 지역 상태

은행 계좌를 스트림으로 모델링:

```javascript
function stream_withdraw(balance, amount_stream) {
    return pair(balance,
                () => stream_withdraw(
                          balance - head(amount_stream),
                          stream_tail(amount_stream)));
}
```

입력이 "출금 요청의 스트림"이고 출력이 "잔고의 스트림"이다. **대입이 없다!** 시간 변화가 스트림의 인덱스로 표현된다.

### 4.2 한계

여러 독립적 에이전트가 상호작용하는 경우(Peter와 Paul이 동시에 출금), 스트림 모델에서는 출금 요청 스트림을 **병합(merge)** 해야 한다. 이 병합 자체가 비결정적이어서, 결국 동시성 문제가 재등장한다.

> **핵심 통찰**: 스트림은 대입의 대안이지 **만능 해결책이 아니다**. 단일 에이전트의 시간적 변화는 우아하게 모델링하지만, 다중 에이전트의 상호작용에서는 한계가 있다. 이것은 함수형 프로그래밍과 명령형 프로그래밍 사이의 근본적 긴장이 완전히 해소되지 않음을 보여준다.

---

## 요약

- **스트림**은 지연 평가되는 리스트로, 원소가 필요할 때만 계산된다. 무한 데이터 구조를 표현할 수 있다.
- 에라토스테네스의 체, 피보나치 수열, 뉴턴 근사 등이 스트림으로 우아하게 표현된다.
- **암묵적 정의**로 스트림을 자기 자신을 참조하여 정의할 수 있다.
- 스트림은 **대입 없이 시간 변화를 모델링**하는 대안이지만, 다중 에이전트 상호작용에서는 한계가 있다.
- 함수형 프로그래밍과 명령형 프로그래밍 사이의 근본적 긴장은 완전히 해소되지 않는다.

---

## 다른 섹션과의 관계

- **Section 1.1 (The Elements of Programming)**: 뉴턴 방법이 스트림으로 재표현된다. 반복이 무한 스트림이 된다.
- **Section 2.2 (Hierarchical Data)**: 시퀀스 연산(map, filter, accumulate)이 스트림 버전으로 확장된다.
- **Section 3.1 (Assignment and Local State)**: 스트림은 대입의 대안으로 제시된다.
- **Section 3.4 (Concurrency)**: 스트림이 동시성 문제를 회피할 수 있지만 완전히 해결하지는 못한다.
- **Section 4.2 (Lazy Evaluation)**: 스트림의 지연 평가를 언어 수준에서 지원하는 인터프리터를 구축한다. 스트림 전용 구문 없이도 모든 데이터가 지연 평가될 수 있다.
