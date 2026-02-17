# Chapter 2: Degenerate Objects (퇴화 객체)

## 핵심 질문

객체의 연산이 객체 자신을 변경하는 **부작용(side effect)** 문제를 TDD로 어떻게 해결하는가? 값 객체(Value Object)란 무엇이며, 왜 중요한가?

---

## 1. 문제 인식: 부작용

### 1.1 이전 챕터의 문제점

Chapter 1에서 작성한 테스트를 다시 보자:

```java
public void testMultiplication() {
    Dollar five = new Dollar(5);
    five.times(2);
    assertEquals(10, five.amount);
}
```

이 코드의 문제: `five.times(2)` 호출 후 `five.amount`가 10이 된다. **`five`라는 변수 이름이 거짓말을 하고 있다** — 더 이상 5달러가 아니기 때문이다.

만약 같은 Dollar 객체에 대해 연산을 두 번 하고 싶다면?

```java
public void testMultiplication() {
    Dollar five = new Dollar(5);
    five.times(2);
    assertEquals(10, five.amount);
    five.times(3);
    assertEquals(15, five.amount);  // 실패! amount는 30 (10 × 3)
}
```

`times()`가 `five` 객체 자체를 변경하기 때문에, 두 번째 `times(3)`은 원래의 5가 아니라 이미 변경된 10에 3을 곱한다. 이것이 **부작용(side effect)** 이다.

### 1.2 부작용이 위험한 이유

부작용이 있는 객체는:

- 사용 순서에 따라 결과가 달라진다 (**순서 의존성**)
- 한 곳에서 변경한 것이 다른 곳에 예상치 못한 영향을 준다
- 같은 객체를 여러 곳에서 공유하면 버그가 발생하기 쉽다

> **핵심 통찰**: 부작용은 복잡성의 주요 원인이다. 객체를 사용할 때 "이 객체를 이전에 누가 변경했는가?"를 항상 추적해야 하므로 인지 부하가 증가한다.

---

## 2. 해결책: 값 객체 (Value Object)

### 2.1 값 객체란?

**값 객체(Value Object)** 는 생성 후 상태가 변경되지 않는(immutable) 객체다. 연산을 수행하면 자신을 변경하는 대신 **새 객체를 반환**한다.

일상의 비유:
- **참조 객체**: 은행 계좌 — `account.deposit(100)`은 계좌 자체의 잔액을 변경한다
- **값 객체**: 지폐 — 5달러 지폐에 2를 곱해도 그 지폐가 10달러 지폐로 바뀌지는 않는다. 대신 새로운 10달러 지폐가 생긴다

### 2.2 값 객체의 특성

| 특성 | 설명 |
|------|------|
| **불변성(Immutability)** | 생성 후 상태가 변경되지 않는다 |
| **동등성(Equality)** | 같은 값을 가진 두 객체는 동등하다 (identity가 아닌 value 비교) |
| **대체 가능성(Substitutability)** | 같은 값의 객체는 서로 대체 가능하다 |
| **부작용 없음(Side-effect free)** | 연산이 원본을 변경하지 않고 새 객체를 반환한다 |

값 객체를 사용하면 TODO 리스트의 "Dollar 부작용" 문제를 해결할 수 있다.

---

## 3. TDD 사이클

### 3.1 Red — 원하는 동작을 테스트로 표현

`times()`가 새 Dollar 객체를 반환하도록 테스트를 변경한다:

```java
public void testMultiplication() {
    Dollar five = new Dollar(5);
    Dollar product = five.times(2);
    assertEquals(10, product.amount);
    product = five.times(3);
    assertEquals(15, product.amount);
}
```

핵심 변경점:
- `five.times(2)`의 반환값을 `product`라는 새 변수에 담는다
- `five` 객체는 변경되지 않으므로, `five.times(3)`은 항상 5 × 3 = 15다
- `times()`의 반환 타입이 `void`에서 `Dollar`로 바뀌어야 한다

이 테스트는 **컴파일 에러**가 발생한다 — `times()`의 반환 타입이 `void`이기 때문이다. 이것이 Red Bar다.

### 3.2 Green — 최소한의 변경으로 테스트 통과

`times()`가 새 Dollar를 반환하도록 수정한다:

```java
class Dollar {
    int amount;

    Dollar(int amount) {
        this.amount = amount;
    }

    Dollar times(int multiplier) {
        return new Dollar(amount * multiplier);
    }
}
```

변경 사항:
1. 반환 타입: `void` → `Dollar`
2. 구현: `amount *= multiplier` → `return new Dollar(amount * multiplier)`

이제 `five.times(2)`를 호출해도 `five` 객체의 `amount`는 여전히 5이다. 새로운 Dollar 객체(amount = 10)가 반환될 뿐이다.

**테스트 통과! Green Bar!**

### 3.3 Refactor — 중복이 있는가?

이번에는 명백한 중복이 없다. Fake It 전략을 사용하지 않고 **Obvious Implementation(명백한 구현)** 으로 바로 갔기 때문이다. `return new Dollar(amount * multiplier)`는 너무 명확해서 단계를 더 나눌 필요가 없었다.

> **핵심 통찰**: 모든 단계에서 Fake It을 써야 하는 것은 아니다. 구현이 명백하면 바로 작성한다. 중요한 것은 **Red Bar가 예상치 못하게 나타날 때** 더 작은 단계로 돌아갈 준비가 되어 있는 것이다.

---

## 4. "퇴화 객체(Degenerate Objects)"란?

### 4.1 챕터 제목의 의미

"Degenerate"는 수학에서 "퇴화된", "특수한 경우로 축소된"이라는 뜻이다. Kent Beck은 이 용어를 **객체의 동작이 가장 단순한 형태로 축소된 상태**를 의미하는 데 사용한다.

이 챕터에서 Dollar 객체는:
- 처음에는 **변이 가능한 객체**(mutable object)였다 — `times()`가 자신을 변경
- 이제는 **값 객체**(value object)가 되었다 — `times()`가 새 객체를 반환

값 객체는 참조 객체보다 "퇴화된" — 더 제한적이고 단순한 — 형태다. 하지만 이 **단순함이 곧 강점**이다. 부작용이 없으므로 추론하기 쉽고, 공유해도 안전하다.

### 4.2 TDD에서 퇴화 전략

Kent Beck은 객체의 동작을 구현할 때 **가장 단순한(퇴화된) 형태에서 시작**하는 것을 권장한다:

1. 상수를 반환하는 것에서 시작 (가장 퇴화된 형태)
2. 변수를 도입하여 일반화
3. 필요에 따라 더 복잡한 동작 추가

이것은 Chapter 1의 Fake It 전략과 일맥상통한다.

---

## 5. 값 객체 도입의 파급 효과

값 객체를 사용하기로 결정하면 새로운 요구사항이 생긴다:

### 5.1 동등성 비교가 필요하다

```java
Dollar a = new Dollar(5);
Dollar b = new Dollar(5);
// a == b는 false (Java에서 ==는 참조 비교)
// a.equals(b)가 true여야 한다
```

값 객체는 같은 값을 가지면 동등해야 한다. 이를 위해 `equals()` 메서드를 구현해야 한다. → TODO 리스트에 추가

### 5.2 해시 코드도 필요하다

`equals()`를 오버라이드하면 `hashCode()`도 오버라이드해야 한다 (Java의 계약). → TODO 리스트에 추가 (하지만 당장은 다루지 않는다)

### 5.3 null 처리, 다른 타입과의 비교

`equals(null)`, `equals("문자열")` 등도 고려해야 한다. → 필요할 때 다루기로 한다

---

## 6. 이 챕터에서 완성된 코드

```java
// Dollar.java
class Dollar {
    int amount;

    Dollar(int amount) {
        this.amount = amount;
    }

    Dollar times(int multiplier) {
        return new Dollar(amount * multiplier);
    }
}
```

```java
// DollarTest.java
public void testMultiplication() {
    Dollar five = new Dollar(5);
    Dollar product = five.times(2);
    assertEquals(10, product.amount);
    product = five.times(3);
    assertEquals(15, product.amount);
}
```

---

## TODO 리스트 (챕터 종료 시점)

- [ ] $5 + 10 CHF = $10 (환율이 2:1인 경우)
- [x] ~~$5 × 2 = $10~~
- [ ] amount를 private으로 만들기
- [x] ~~Dollar 부작용(side effect)?~~
- [ ] Money 반올림?
- [ ] equals()
- [ ] hashCode()
- [ ] null과의 동등성
- [ ] 다른 객체와의 동등성

부작용 문제가 해결되었고, 값 객체 도입으로 새로운 TODO 항목들(equals, hashCode 등)이 추가되었다.

---

## 7. 값 객체 vs 참조 객체 비교

| 특성 | 값 객체 (Value Object) | 참조 객체 (Reference Object) |
|------|----------------------|---------------------------|
| **변경 가능성** | 불변 (Immutable) | 변경 가능 (Mutable) |
| **동등성 기준** | 값이 같으면 동등 | 동일 인스턴스여야 동등 |
| **부작용** | 없음 | 있을 수 있음 |
| **공유 안전성** | 안전하게 공유 가능 | 공유 시 주의 필요 |
| **예시** | 날짜, 금액, 좌표 | 고객, 주문, 계좌 |
| **TDD 관점** | 테스트 작성이 쉬움 | 상태 관리 때문에 테스트가 복잡해짐 |

> **핵심 통찰**: Kent Beck이 Dollar를 값 객체로 만든 것은 단순히 부작용을 없애기 위해서만이 아니다. **값 객체는 테스트하기 쉽다.** 상태가 변하지 않으므로 테스트의 결과가 이전 테스트의 영향을 받지 않는다. TDD에서 값 객체를 선호하는 것은 자연스러운 일이다.

---

## 요약

- **부작용(side effect)** 은 객체의 연산이 객체 자신을 변경하는 것으로, 버그의 주요 원인이다.
- **값 객체(Value Object)** 패턴: 연산이 자신을 변경하는 대신 새 객체를 반환한다. 불변이므로 안전하게 공유 가능하다.
- 이 챕터에서 `times()`의 반환 타입을 `void`에서 `Dollar`로 바꾸고, 새 객체를 반환하도록 수정했다.
- 구현이 명백할 때는 **Obvious Implementation** 전략을 사용할 수 있다. Fake It이 항상 필요한 것은 아니다.
- 값 객체를 도입하면 **동등성(equality)** 구현이 필요해진다 — 이것이 다음 챕터의 주제다.
- **퇴화(degenerate)** 란 가장 단순한 형태를 의미한다. TDD는 단순한 것에서 시작하여 필요에 따라 복잡성을 추가한다.

---

## 다른 챕터와의 관계

- **Chapter 1 (Multi-Currency Money)**: 이 챕터의 TODO 리스트에서 "Dollar 부작용" 문제를 가져왔다. Chapter 1에서 시작한 Dollar 클래스를 값 객체로 진화시켰다.
- **Chapter 3 (Equality for All)**: 값 객체의 핵심 요구사항인 `equals()` 메서드를 TDD로 구현한다. `new Dollar(5).equals(new Dollar(5))`가 `true`를 반환하도록 만든다.
- **Chapter 4 (Privacy)**: `amount`를 private으로 만든다. 값 객체의 equals가 있으면 테스트에서 `product.amount` 대신 `product.equals(new Dollar(10))`으로 비교할 수 있으므로 amount를 외부에 노출할 필요가 없어진다.
- **Chapter 30 (Design Patterns)**: 값 객체 패턴이 Part III에서 TDD의 핵심 설계 패턴으로 정리된다.
