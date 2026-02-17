# Chapter 6: Equality for All, Redux (동등성 재검토)

## 핵심 질문

Dollar와 Franc에 동일하게 존재하는 `equals()` 중복을 어떻게 제거하는가? 공통 상위 클래스(superclass)를 도입하여 코드를 통합하는 과정에서, TDD는 어떤 역할을 하는가?

---

## 1. 문제 인식: equals() 중복

### 1.1 현재 상태의 코드

Chapter 5에서 Dollar를 복사하여 Franc를 만들었다. 그 결과, 두 클래스의 `equals()` 메서드가 거의 동일하다:

```java
// Dollar.equals()
public boolean equals(Object object) {
    Dollar dollar = (Dollar) object;
    return amount == dollar.amount;
}

// Franc.equals()
public boolean equals(Object object) {
    Franc franc = (Franc) object;
    return amount == franc.amount;
}
```

차이점은 **캐스팅 타입**뿐이다: `Dollar` vs `Franc`. 나머지 로직은 완전히 동일하다.

### 1.2 중복 제거 전략

이 중복을 제거하는 방법: **공통 상위 클래스를 만들어 `equals()`를 올린다.**

Kent Beck은 `Money`라는 상위 클래스를 도입한다.

---

## 2. TDD 사이클

이 챕터의 TDD 사이클은 전형적인 "Red → Green → Refactor"와 약간 다르다. **기존 테스트가 이미 통과하는 상태에서 리팩토링을 진행**하며, 각 리팩토링 단계마다 **테스트가 여전히 통과하는지 확인**하는 방식이다.

### 2.1 Step 1: Money 클래스 생성

먼저 빈 Money 클래스를 만든다:

```java
class Money {
}
```

그리고 Dollar가 Money를 상속하도록 변경한다:

```java
class Dollar extends Money {
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

**테스트 실행 → 모든 테스트 통과!** 아직 아무 동작도 바뀌지 않았으니 당연하다. 하지만 확인하는 것이 중요하다.

### 2.2 Step 2: amount 필드를 Money로 이동

`amount` 필드는 Dollar와 Franc에서 동일하다. 이것을 Money로 올린다:

```java
class Money {
    protected int amount;
}
```

`protected`를 사용하는 이유: 하위 클래스(Dollar, Franc)에서 접근할 수 있어야 하기 때문이다. 원래 `private`이었지만, 상위 클래스로 올리면서 `protected`로 변경한다.

Dollar에서 `amount` 필드 선언을 제거한다:

```java
class Dollar extends Money {
    // private int amount;  ← 제거! Money에서 상속받음

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

**테스트 실행 → 모든 테스트 통과!**

### 2.3 Step 3: equals()를 Money로 이동

이제 핵심 단계다. Dollar의 `equals()`에서 캐스팅 타입을 `Dollar`에서 `Money`로 변경한다:

```java
// Dollar.java — equals()의 캐스팅 타입 변경
public boolean equals(Object object) {
    Money money = (Money) object;          // Dollar → Money
    return amount == money.amount;
}
```

이것이 가능한 이유: `amount`가 이제 Money 클래스에 있으므로, `Money` 타입으로 캐스팅해도 `amount`에 접근할 수 있다.

**테스트 실행 → 모든 테스트 통과!**

이제 이 `equals()` 메서드는 Dollar에 특화된 부분이 전혀 없다. Money로 올릴 수 있다:

```java
class Money {
    protected int amount;

    public boolean equals(Object object) {
        Money money = (Money) object;
        return amount == money.amount;
    }
}
```

Dollar에서 `equals()`를 제거한다:

```java
class Dollar extends Money {
    Dollar(int amount) {
        this.amount = amount;
    }

    Dollar times(int multiplier) {
        return new Dollar(amount * multiplier);
    }

    // equals() 제거 — Money에서 상속받음
}
```

**테스트 실행 → 모든 테스트 통과!**

### 2.4 Step 4: Franc에도 동일하게 적용

이제 Franc도 Money를 상속하고, `equals()`를 제거한다:

```java
class Franc extends Money {
    Franc(int amount) {
        this.amount = amount;
    }

    Franc times(int multiplier) {
        return new Franc(amount * multiplier);
    }

    // equals() 제거 — Money에서 상속받음
    // amount 필드도 제거 — Money에서 상속받음
}
```

**테스트 실행 → 모든 테스트 통과!**

### 2.5 Franc의 동등성 테스트 추가

Kent Beck은 여기서 하나의 고민을 한다: Franc의 동등성을 테스트하는 코드가 없다. Dollar의 동등성은 `testEquality`에서 테스트하고 있지만, Franc의 동등성은 테스트하지 않고 있다.

Money의 `equals()`가 Dollar와 Franc 모두에게 올바르게 동작하는지 확인하기 위해, Franc에 대한 동등성 테스트를 추가한다:

```java
public void testEquality() {
    assertTrue(new Dollar(5).equals(new Dollar(5)));
    assertFalse(new Dollar(5).equals(new Dollar(6)));
    assertTrue(new Franc(5).equals(new Franc(5)));
    assertFalse(new Franc(5).equals(new Franc(6)));
}
```

**테스트 실행 → 모든 테스트 통과!**

> **핵심 통찰**: 리팩토링을 할 때, 기존 테스트만으로 충분한지 항상 자문해야 한다. 공통 코드를 추출했다면, 그 공통 코드가 **모든 사용처**에서 올바르게 동작하는지 확인하는 테스트가 필요하다.

---

## 3. 리팩토링의 각 단계와 안전성

### 3.1 작은 단계의 중요성

이 챕터에서의 리팩토링은 여러 작은 단계로 나뉜다:

| 단계 | 변경 내용 | 테스트 실행 |
|------|----------|-----------|
| 1 | Money 클래스 생성, Dollar extends Money | 통과 |
| 2 | amount를 Money로 이동 (private → protected) | 통과 |
| 3 | Dollar.equals()의 캐스팅을 Money로 변경 | 통과 |
| 4 | equals()를 Money로 이동, Dollar에서 제거 | 통과 |
| 5 | Franc extends Money, Franc.equals() 제거 | 통과 |

**매 단계마다 테스트를 실행**한다. 이것이 핵심이다. 만약 4번과 5번 사이에서 테스트가 실패했다면, 문제의 원인이 5번 단계에 있다는 것을 즉시 알 수 있다.

### 3.2 "너무 작은 단계 아닌가?"

경험 많은 개발자라면 이 모든 변경을 한 번에 할 수 있을 것이다. Kent Beck도 그것을 알고 있다. 하지만 의도적으로 작은 단계를 밟는다.

이유:
1. **실패했을 때 원인을 좁힐 수 있다** — 최근 변경만 되돌리면 된다
2. **TDD의 리듬을 보여주기 위해** — 책에서 TDD를 가르치는 중이다
3. **실무에서도 유용하다** — 복잡한 리팩토링일수록 작은 단계가 안전하다

> **핵심 통찰**: 자신감이 있을 때는 큰 단계로, 불확실할 때는 작은 단계로. **하지만 어떤 크기의 단계를 선택하든, 각 단계 후에 테스트를 실행해야 한다.** 이것이 TDD가 리팩토링을 안전하게 만드는 방법이다.

---

## 4. 코드 진화 과정 전체 추적

**Before (Chapter 5 종료 시점)**:

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

// Franc.java
class Franc {
    private int amount;

    Franc(int amount) {
        this.amount = amount;
    }

    Franc times(int multiplier) {
        return new Franc(amount * multiplier);
    }

    public boolean equals(Object object) {
        Franc franc = (Franc) object;
        return amount == franc.amount;
    }
}
```

**After (Chapter 6 종료 시점)**:

```java
// Money.java (새로 추가)
class Money {
    protected int amount;

    public boolean equals(Object object) {
        Money money = (Money) object;
        return amount == money.amount;
    }
}

// Dollar.java (간소화)
class Dollar extends Money {
    Dollar(int amount) {
        this.amount = amount;
    }

    Dollar times(int multiplier) {
        return new Dollar(amount * multiplier);
    }
}

// Franc.java (간소화)
class Franc extends Money {
    Franc(int amount) {
        this.amount = amount;
    }

    Franc times(int multiplier) {
        return new Franc(amount * multiplier);
    }
}
```

변화를 정리하면:

| 요소 | Before | After |
|------|--------|-------|
| `amount` 필드 | Dollar, Franc 각각에 존재 | Money에 한 번만 존재 |
| `equals()` | Dollar, Franc 각각에 존재 | Money에 한 번만 존재 |
| 클래스 계층 | Dollar, Franc (독립) | Money ← Dollar, Franc |
| 중복 코드 | amount 2번, equals 2번 | amount 1번, equals 1번 |

---

## 5. 이 챕터에서 완성된 코드

```java
// Money.java
class Money {
    protected int amount;

    public boolean equals(Object object) {
        Money money = (Money) object;
        return amount == money.amount;
    }
}
```

```java
// Dollar.java
class Dollar extends Money {
    Dollar(int amount) {
        this.amount = amount;
    }

    Dollar times(int multiplier) {
        return new Dollar(amount * multiplier);
    }
}
```

```java
// Franc.java
class Franc extends Money {
    Franc(int amount) {
        this.amount = amount;
    }

    Franc times(int multiplier) {
        return new Franc(amount * multiplier);
    }
}
```

```java
// 테스트
public void testMultiplication() {
    Dollar five = new Dollar(5);
    assertEquals(new Dollar(10), five.times(2));
    assertEquals(new Dollar(15), five.times(3));
}

public void testFrancMultiplication() {
    Franc five = new Franc(5);
    assertEquals(new Franc(10), five.times(2));
    assertEquals(new Franc(15), five.times(3));
}

public void testEquality() {
    assertTrue(new Dollar(5).equals(new Dollar(5)));
    assertFalse(new Dollar(5).equals(new Dollar(6)));
    assertTrue(new Franc(5).equals(new Franc(5)));
    assertFalse(new Franc(5).equals(new Franc(6)));
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
- [x] ~~$5 CHF × 2 = $10 CHF~~
- [ ] Dollar/Franc 중복
- [x] ~~공통 equals()~~
- [ ] 공통 times()
- [ ] **Franc과 Dollar 비교**
- [ ] 통화(Currency)?

`공통 equals()`가 완료되었다. Dollar와 Franc의 `equals()` 중복이 Money로 통합되었다. 하지만 아직 **Franc과 Dollar 비교** 문제가 남아 있다 — `Dollar(5).equals(Franc(5))`는 현재 `true`를 반환한다. 이것은 다음 챕터의 주제다.

---

## 요약

- Dollar와 Franc의 **`equals()` 중복**을 제거하기 위해 공통 상위 클래스 **Money**를 도입했다.
- `amount` 필드와 `equals()` 메서드를 Money로 올렸다.
- 리팩토링은 **작은 단계**로 나누어 진행했으며, **매 단계마다 테스트를 실행**하여 안전성을 확보했다.
- Franc의 동등성 테스트가 없었으므로 추가했다 — 공통 코드가 모든 사용처에서 동작하는지 확인하기 위해.
- `amount`의 접근 제어자가 `private`에서 `protected`로 변경되었다 — 상속을 위한 트레이드오프다.
- **상속을 사용한 중복 제거**는 가장 기본적인 리팩토링 기법 중 하나다. TDD에서는 테스트가 리팩토링의 안전망이 된다.

---

## 다른 챕터와의 관계

- **Chapter 3 (Equality for All)**: Dollar의 `equals()`를 처음 구현한 챕터다. 이 챕터에서 그것을 Money로 일반화했다.
- **Chapter 5 (Franc-ly Speaking)**: Franc을 만들면서 생긴 중복을 이 챕터에서 해결하기 시작했다.
- **Chapter 7 (Apples and Oranges)**: Money.equals()가 클래스를 구분하지 않는 문제를 발견한다. `Dollar(5).equals(Franc(5))`가 `true`를 반환하는 버그를 수정한다.
- **Chapter 10 (Interesting Times)**: `times()` 중복을 제거한다. 이 챕터에서 `equals()`에 대해 한 것과 동일한 작업을 `times()`에 대해 수행한다.
- **Chapter 11 (The Root of All Evil)**: Dollar와 Franc 하위 클래스를 완전히 제거하고, Money 하나로 통합한다.
