# Chapter 3: Equality for All (모두를 위한 동등성)

## 핵심 질문

값 객체(Value Object)에서 동등성(equality)은 왜 필요하며, TDD로 어떻게 구현하는가? 두 개의 테스트 케이스로 일반화를 이끌어내는 **삼각측량(Triangulation)** 전략이란 무엇인가?

---

## 1. 동등성이 필요한 이유

### 1.1 값 객체의 핵심 계약

Chapter 2에서 Dollar를 값 객체(Value Object)로 만들었다. 값 객체의 핵심 성질은 **같은 값을 가진 두 객체는 동등해야 한다**는 것이다.

일상의 비유로 생각해보자:

- 내 지갑에 있는 5달러 지폐와 당신 지갑에 있는 5달러 지폐는 **같다**. 물리적으로 다른 지폐이지만, "5달러"라는 가치가 같으므로 동등하다.
- 마찬가지로, `new Dollar(5)`로 만든 두 객체는 메모리 주소는 다르지만 "5달러"라는 값이 같으므로 동등해야 한다.

### 1.2 Java에서의 문제

Java에서 `==` 연산자는 **참조 비교**(같은 메모리 주소인지)를 한다. 값 비교를 하려면 `equals()` 메서드를 오버라이드해야 한다:

```java
Dollar a = new Dollar(5);
Dollar b = new Dollar(5);

a == b;       // false — 서로 다른 객체이므로
a.equals(b);  // Object의 기본 equals()는 == 과 동일하므로 역시 false
```

`equals()`를 오버라이드하지 않으면, 값 객체로서의 Dollar는 제대로 동작하지 않는다. 예를 들어 `assertEquals(new Dollar(5), new Dollar(5))`도 실패한다.

### 1.3 TODO 리스트 확인

Chapter 2 종료 시점의 TODO 리스트에서 `equals()`가 대기 중이었다:

- [ ] $5 + 10 CHF = $10 (환율이 2:1인 경우)
- [x] ~~$5 × 2 = $10~~
- [ ] amount를 private으로 만들기
- [x] ~~Dollar 부작용(side effect)?~~
- [ ] Money 반올림?
- [ ] **equals()**
- [ ] hashCode()
- [ ] null과의 동등성
- [ ] 다른 객체와의 동등성

이제 `equals()`를 구현할 차례다.

---

## 2. TDD 사이클

### 2.1 Red — 동등성 테스트 작성

같은 값을 가진 두 Dollar 객체가 동등한지 테스트한다:

```java
public void testEquality() {
    assertTrue(new Dollar(5).equals(new Dollar(5)));
}
```

이 테스트는 **실패**한다. `Dollar`는 `equals()`를 오버라이드하지 않았으므로 `Object`의 기본 `equals()`가 사용된다. `Object.equals()`는 `==`와 동일하게 참조를 비교하므로, 서로 다른 두 객체는 항상 `false`를 반환한다.

**Red Bar!**

### 2.2 Green — Fake It으로 시작

가장 빠르게 테스트를 통과시키는 방법은 무엇인가? 무조건 `true`를 반환하면 된다:

```java
// Dollar.java
public boolean equals(Object object) {
    return true;
}
```

**테스트 통과! Green Bar!**

물론 이것은 분명히 잘못된 구현이다. `new Dollar(5).equals(new Dollar(6))`도 `true`를 반환할 것이다. 하지만 Kent Beck은 이것을 **의도적으로** 한다. 지금 테스트가 하나뿐이므로, 이 하나의 테스트를 통과시키는 가장 단순한 코드를 먼저 작성한 것이다.

> **핵심 통찰**: "무조건 true를 반환"하는 것은 터무니없어 보이지만, 이것이 바로 TDD의 Fake It 전략이다. 핵심은 **다음 테스트가 이 가짜 구현을 깨뜨릴 것**이라는 점이다. 테스트를 하나 더 추가하면 일반화가 강제된다.

### 2.3 삼각측량(Triangulation) — 두 번째 테스트 추가

Kent Beck은 여기서 **삼각측량(Triangulation)** 전략을 사용한다. 삼각측량이란 **두 개 이상의 예제를 사용하여 올바른 일반화를 이끌어내는 기법**이다.

하나의 테스트(`$5 == $5`)만으로는 `return true`라는 가짜 구현을 허용한다. 그러나 두 번째 테스트(`$5 != $6`)를 추가하면, `return true`로는 더 이상 통과할 수 없다:

```java
public void testEquality() {
    assertTrue(new Dollar(5).equals(new Dollar(5)));
    assertFalse(new Dollar(5).equals(new Dollar(6)));
}
```

두 번째 단언(`assertFalse`)이 **실패**한다. `equals()`가 무조건 `true`를 반환하기 때문이다.

**Red Bar!**

### 2.4 Green — 진짜 구현

이제 `return true`로는 두 테스트를 모두 통과시킬 수 없다. 실제로 금액을 비교해야 한다:

```java
// Dollar.java
public boolean equals(Object object) {
    Dollar dollar = (Dollar) object;
    return amount == dollar.amount;
}
```

구현 내용:
1. 파라미터를 `Dollar`로 캐스팅한다
2. 두 Dollar의 `amount`를 비교한다

**두 테스트 모두 통과! Green Bar!**

### 2.5 Refactor — 정리할 것이 있는가?

이 코드에는 몇 가지 개선 여지가 있다:

- `null`을 전달하면 `ClassCastException`이 발생한다 → TODO 리스트에 이미 있다
- `Dollar`가 아닌 다른 객체를 전달하면 역시 에러가 발생한다 → TODO 리스트에 이미 있다
- `hashCode()`도 구현해야 한다 → TODO 리스트에 이미 있다

이 모든 문제를 지금 해결하지 않는다. **TODO 리스트에 있으니 잊어버리지 않을 것**이다. 지금은 `equals()`가 기본적으로 동작하는 것으로 충분하다.

---

## 3. 삼각측량(Triangulation) 전략 상세

### 3.1 삼각측량이란?

삼각측량은 측량학에서 온 비유다. 하나의 관측점만으로는 위치를 특정할 수 없지만, **두 개 이상의 관측점**이 있으면 정확한 위치를 계산할 수 있다.

TDD에서의 삼각측량:
- **관측점 1**: `assertTrue(new Dollar(5).equals(new Dollar(5)))` — 같은 금액은 동등해야 한다
- **관측점 2**: `assertFalse(new Dollar(5).equals(new Dollar(6)))` — 다른 금액은 동등하지 않아야 한다

하나의 테스트만으로는 `return true`라는 퇴화된(degenerate) 구현이 가능하다. 두 번째 테스트를 추가하면 **일반화를 강제**한다.

### 3.2 세 가지 Green Bar 전략 비교

| 전략 | 설명 | 이 챕터에서의 사용 |
|------|------|-------------------|
| **Fake It** | 상수를 반환하여 테스트를 통과시킨다 | `return true` |
| **Triangulation** | 두 개 이상의 테스트로 일반화를 강제한다 | `$5==$5`와 `$5!=$6` |
| **Obvious Implementation** | 명백한 구현을 바로 작성한다 | (이 챕터에서는 사용하지 않음) |

### 3.3 삼각측량은 언제 사용하는가?

Kent Beck은 삼각측량에 대해 다음과 같이 말한다:

> 삼각측량은 **올바른 추상화가 무엇인지 확신이 서지 않을 때** 사용한다. 어떻게 일반화해야 할지 모르겠으면, 다른 예제를 하나 더 추가하라.

실무에서의 활용:
- 알고리즘의 올바른 일반화가 불명확할 때
- 경계 조건을 탐색할 때
- 가짜 구현(Fake It)에서 진짜 구현으로 넘어가는 다리 역할

> **핵심 통찰**: 삼각측량은 가장 보수적인 TDD 전략이다. 하나의 예제에서 바로 일반화하는 대신, **두 번째 예제가 일반화를 강제할 때까지 기다린다.** 이것은 과잉 설계(over-engineering)를 방지하는 효과적인 방법이다.

---

## 4. 코드 진화 과정 전체 추적

이 챕터에서 코드가 어떻게 진화했는지 단계별로 정리한다:

**Step 1**: Chapter 2 종료 시점의 Dollar 클래스

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

**Step 2**: Fake It — `equals()` 추가 (무조건 true)

```java
class Dollar {
    int amount;

    Dollar(int amount) {
        this.amount = amount;
    }

    Dollar times(int multiplier) {
        return new Dollar(amount * multiplier);
    }

    public boolean equals(Object object) {
        return true;  // Fake It!
    }
}
```

**Step 3**: 삼각측량 후 — `equals()` 진짜 구현

```java
class Dollar {
    int amount;

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
    int amount;

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
    assertEquals(10, product.amount);
    product = five.times(3);
    assertEquals(15, product.amount);
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
- [ ] amount를 private으로 만들기
- [x] ~~Dollar 부작용(side effect)?~~
- [ ] Money 반올림?
- [x] ~~equals()~~
- [ ] hashCode()
- [ ] null과의 동등성
- [ ] 다른 객체와의 동등성

`equals()`가 완료되었다. 하지만 null 처리, 다른 타입과의 비교, hashCode()는 아직 남아 있다. 이들은 필요해질 때 처리할 것이다.

---

## 요약

- **값 객체**는 같은 값을 가진 두 객체가 동등해야 한다. 이를 위해 `equals()` 메서드를 구현해야 한다.
- **삼각측량(Triangulation)**: 두 개 이상의 테스트 케이스를 사용하여 일반적인 구현을 이끌어내는 전략이다. 하나의 테스트만으로는 가짜 구현이 가능하지만, 두 번째 테스트가 일반화를 강제한다.
- `$5 == $5` (같은 값은 동등)과 `$5 != $6` (다른 값은 비동등) 두 테스트로 `equals()` 구현을 완성했다.
- `equals()` 구현은 아직 불완전하다 — null 처리, 다른 타입 처리, hashCode()가 남아 있다. 하지만 **지금 필요한 만큼만 구현**하고 나머지는 TODO 리스트에 남긴다.
- TDD에서는 완벽을 추구하지 않는다. **동작하는 코드를 먼저 만들고**, 필요에 따라 개선한다.

---

## 다른 챕터와의 관계

- **Chapter 2 (Degenerate Objects)**: Dollar를 값 객체로 만들면서 `equals()` 필요성이 제기되었다. 이 챕터에서 그 요구를 충족시켰다.
- **Chapter 4 (Privacy)**: `equals()`가 존재하므로, 테스트에서 `product.amount` 대신 `assertEquals(new Dollar(10), product)`로 비교할 수 있게 된다. 이것이 `amount`를 private으로 만드는 열쇠가 된다.
- **Chapter 5 (Franc-ly Speaking)**: Franc 클래스를 만들 때 Dollar를 복사하는데, `equals()` 역시 복사된다. 이 중복은 Chapter 6에서 해결된다.
- **Chapter 6 (Equality for All, Redux)**: Dollar와 Franc의 `equals()` 중복을 공통 상위 클래스 Money로 올린다.
- **Chapter 7 (Apples and Oranges)**: `equals()`에 클래스 비교를 추가한다 — `Dollar(5).equals(Franc(5))`가 `false`를 반환하도록 한다.
- **Chapter 25 (TDD Patterns)**: 삼각측량이 TDD의 공식적인 패턴으로 정리된다.
