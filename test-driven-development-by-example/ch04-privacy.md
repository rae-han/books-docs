# Chapter 4: Privacy (프라이버시)

## 핵심 질문

`equals()`를 구현한 후, 테스트 코드를 어떻게 개선할 수 있는가? 테스트에서 구현 세부사항(amount 필드)에 대한 의존을 제거하면 어떤 이점이 있으며, 이것이 캡슐화(encapsulation)와 어떤 관계가 있는가?

---

## 1. 테스트의 냄새: 구현 세부사항에 대한 의존

### 1.1 현재 테스트의 문제점

Chapter 2에서 작성한 곱하기 테스트를 다시 보자:

```java
public void testMultiplication() {
    Dollar five = new Dollar(5);
    Dollar product = five.times(2);
    assertEquals(10, product.amount);    // amount 필드에 직접 접근!
    product = five.times(3);
    assertEquals(15, product.amount);    // amount 필드에 직접 접근!
}
```

이 테스트는 `Dollar` 객체의 **내부 구현**인 `amount` 필드에 직접 접근하고 있다. `assertEquals(10, product.amount)`는 "결과의 amount가 10이다"라고 말하고 있다. 하지만 우리가 진짜 검증하고 싶은 것은 **"5달러에 2를 곱하면 10달러가 된다"** 이다.

### 1.2 왜 이것이 문제인가?

테스트가 구현 세부사항에 의존하면:

- `amount` 필드의 이름이 바뀌면 테스트도 수정해야 한다
- `amount` 필드의 타입이 `int`에서 `double`로 바뀌면 테스트도 수정해야 한다
- 테스트가 **무엇을 검증하는지**(What)보다 **어떻게 검증하는지**(How)에 집중하게 된다

> **핵심 통찰**: 좋은 테스트는 **객체의 행동(behavior)** 을 검증하지, 객체의 **내부 상태(state)** 를 들여다보지 않는다. `product.amount == 10`이 아니라, `product`가 `Dollar(10)`과 동등한지를 검증해야 한다.

### 1.3 해결의 열쇠: equals()

Chapter 3에서 `equals()`를 구현했다. 이제 `new Dollar(5).equals(new Dollar(5))`가 `true`를 반환한다. 이것은 테스트에서 `amount` 필드에 직접 접근하지 않고도 Dollar 객체를 비교할 수 있다는 뜻이다.

---

## 2. TDD 사이클

### 2.1 테스트 변경: amount 접근 제거

이 챕터의 TDD 사이클은 기존 챕터들과 조금 다르다. 새로운 기능을 추가하는 것이 아니라, **기존 테스트를 개선**한 다음 그 개선이 가능하게 하는 코드 변경을 한다.

기존 테스트:

```java
public void testMultiplication() {
    Dollar five = new Dollar(5);
    Dollar product = five.times(2);
    assertEquals(10, product.amount);    // int와 비교
    product = five.times(3);
    assertEquals(15, product.amount);    // int와 비교
}
```

개선된 테스트:

```java
public void testMultiplication() {
    Dollar five = new Dollar(5);
    Dollar product = five.times(2);
    assertEquals(new Dollar(10), product);   // Dollar 객체와 비교!
    product = five.times(3);
    assertEquals(new Dollar(15), product);   // Dollar 객체와 비교!
}
```

핵심 변경점:
- `assertEquals(10, product.amount)` → `assertEquals(new Dollar(10), product)`
- 정수 리터럴과 필드 접근 대신, **Dollar 객체 간의 동등성 비교**를 사용한다
- 이것은 `equals()` 메서드가 올바르게 동작하기 때문에 가능하다

테스트가 통과한다! `Dollar(10).equals(product)`가 `true`를 반환하기 때문이다.

### 2.2 amount를 private으로 만들기

이제 테스트 코드에서 `amount` 필드에 접근하는 곳이 없다. `Dollar` 클래스 내부에서만 `amount`를 사용한다:

- 생성자: `this.amount = amount`
- `times()`: `return new Dollar(amount * multiplier)`
- `equals()`: `return amount == dollar.amount`

외부에서 `amount`에 접근할 필요가 없으므로, `private`으로 변경할 수 있다:

```java
class Dollar {
    private int amount;   // public → private

    Dollar(int amount) {
        this.amount = amount;
    }

    Dollar times(int multiplier) {
        return new Dollar(amount * multiplier);
    }

    public boolean equals(Object object) {
        Dollar dollar = (Dollar) object;
        return amount == dollar.amount;
    }
}
```

**모든 테스트 통과! Green Bar!**

### 2.3 Refactor — 추가 정리

이번 변경은 리팩토링 자체가 목적이었으므로, 추가적인 Refactor 단계는 필요 없다.

---

## 3. 테스트 간의 결합도와 위험성

### 3.1 주의할 점: 순환 참조의 위험

Kent Beck은 이 변경에 수반되는 위험을 솔직하게 언급한다.

테스트를 변경한 후, `testMultiplication`은 **`equals()`가 올바르게 동작한다는 것에 의존**하게 된다:

```
testMultiplication → assertEquals(new Dollar(10), product) → Dollar.equals()
```

만약 `equals()`에 버그가 있으면, `testMultiplication`도 잘못된 결과를 줄 수 있다. 이것은 두 테스트 사이에 **결합도**가 생겼다는 뜻이다.

| 이전 | 이후 |
|------|------|
| `testMultiplication`이 `amount` 필드에 직접 의존 | `testMultiplication`이 `equals()`에 의존 |
| `testEquality`와 독립적 | `testEquality`가 실패하면 `testMultiplication`의 결과도 의심해야 함 |

### 3.2 왜 이 위험을 감수하는가?

Kent Beck은 이 결합을 **감수할 만한 트레이드오프**로 본다:

1. **`equals()` 테스트가 이미 존재한다**: `testEquality`가 `equals()`의 올바른 동작을 검증하고 있다. `equals()`에 버그가 생기면 `testEquality`가 먼저 실패할 것이다.

2. **캡슐화의 이점이 크다**: `amount`를 private으로 만들면, Dollar의 내부 표현을 자유롭게 변경할 수 있다. 예를 들어 `amount`의 타입을 `int`에서 `long`이나 `BigDecimal`로 바꿔도 테스트를 수정할 필요가 없다.

3. **테스트가 의도를 더 명확히 표현한다**: `assertEquals(new Dollar(10), product)`는 "결과가 10달러다"라는 **비즈니스 의미**를 직접 전달한다. `assertEquals(10, product.amount)`는 "결과 객체의 amount 필드가 10이다"라는 **구현 세부사항**을 말할 뿐이다.

> **핵심 통찰**: TDD에서 테스트 간의 약간의 결합은 허용할 수 있다 — **다른 테스트가 그 의존성을 충분히 커버하고 있다면.** 완벽한 격리보다 명확한 의도 표현이 더 가치 있을 때가 있다.

---

## 4. 코드 진화 과정 전체 추적

**Step 1**: Chapter 3 종료 시점 — 테스트가 amount에 직접 접근

```java
// 테스트
public void testMultiplication() {
    Dollar five = new Dollar(5);
    Dollar product = five.times(2);
    assertEquals(10, product.amount);       // ← amount 직접 접근
    product = five.times(3);
    assertEquals(15, product.amount);       // ← amount 직접 접근
}

// Dollar.java
class Dollar {
    int amount;  // ← public (기본 접근 제어자)
    // ...
}
```

**Step 2**: 테스트 변경 — Dollar 객체로 비교

```java
// 테스트
public void testMultiplication() {
    Dollar five = new Dollar(5);
    Dollar product = five.times(2);
    assertEquals(new Dollar(10), product);  // ← Dollar 객체 비교
    product = five.times(3);
    assertEquals(new Dollar(15), product);  // ← Dollar 객체 비교
}
```

**Step 3**: amount를 private으로 변경

```java
// Dollar.java
class Dollar {
    private int amount;  // ← private으로 변경!

    Dollar(int amount) {
        this.amount = amount;
    }

    Dollar times(int multiplier) {
        return new Dollar(amount * multiplier);
    }

    public boolean equals(Object object) {
        Dollar dollar = (Dollar) object;
        return amount == dollar.amount;
    }
}
```

---

## 5. 이 챕터에서 완성된 코드

```java
// Dollar.java
class Dollar {
    private int amount;

    Dollar(int amount) {
        this.amount = amount;
    }

    Dollar times(int multiplier) {
        return new Dollar(amount * multiplier);
    }

    public boolean equals(Object object) {
        Dollar dollar = (Dollar) object;
        return amount == dollar.amount;
    }
}
```

```java
// 테스트
public void testMultiplication() {
    Dollar five = new Dollar(5);
    Dollar product = five.times(2);
    assertEquals(new Dollar(10), product);
    product = five.times(3);
    assertEquals(new Dollar(15), product);
}

public void testEquality() {
    assertTrue(new Dollar(5).equals(new Dollar(5)));
    assertFalse(new Dollar(5).equals(new Dollar(6)));
}
```

---

## TODO 리스트 (챕터 종료 시점)

- [ ] $5 + 10 CHF = $10 (환율이 2:1인 경우)
- [x] ~~$5 × 2 = $10~~
- [x] ~~amount를 private으로 만들기~~
- [x] ~~Dollar 부작용(side effect)?~~
- [ ] Money 반올림?
- [x] ~~equals()~~
- [ ] hashCode()
- [ ] null과의 동등성
- [ ] 다른 객체와의 동등성
- [ ] $5 CHF × 2 = $10 CHF

`amount를 private으로 만들기`가 완료되었다. 또한 앞으로 다중 통화를 위해 `$5 CHF × 2 = $10 CHF` 항목이 TODO 리스트에 추가된다. 이것은 다음 챕터의 주제다.

---

## 요약

- `equals()`가 존재하므로 테스트에서 `product.amount` 대신 `assertEquals(new Dollar(10), product)`로 비교할 수 있다.
- 테스트에서 **구현 세부사항**(amount 필드) 대신 **행동**(Dollar 객체의 동등성)을 검증하도록 변경했다.
- 외부에서 `amount`에 접근할 필요가 없어졌으므로 `private`으로 변경했다.
- 이 변경으로 `testMultiplication`이 `equals()`에 의존하게 되는 **결합도**가 생겼지만, `testEquality`가 이를 커버하고 있으므로 허용 가능한 트레이드오프다.
- **캡슐화(encapsulation)** 는 단순히 필드를 private으로 만드는 것이 아니다. **테스트가 내부 구현에 의존하지 않도록 만드는 것**이 진정한 캡슐화다.
- 이 챕터는 TDD에서 **리팩토링이 새 기능 추가만큼 중요하다**는 것을 보여준다. 기존 코드를 개선하는 것도 가치 있는 작업이다.

---

## 다른 챕터와의 관계

- **Chapter 3 (Equality for All)**: `equals()` 구현이 이 챕터의 전제 조건이었다. `equals()` 없이는 Dollar 객체 간의 비교가 불가능했을 것이다.
- **Chapter 5 (Franc-ly Speaking)**: Dollar와 동일한 구조의 Franc 클래스를 만든다. 이때 `private int amount`도 함께 복사된다.
- **Chapter 6 (Equality for All, Redux)**: Dollar와 Franc이 같은 `equals()` 로직을 가지게 되면서, 공통 상위 클래스 Money로 끌어올리는 리팩토링이 필요해진다.
- **Chapter 17 (Money Retrospective)**: Money 예제의 전체 회고에서, 테스트와 구현 사이의 결합도에 대한 논의가 이어진다.
