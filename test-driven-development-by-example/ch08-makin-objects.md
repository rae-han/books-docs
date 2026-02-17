# Chapter 8: Makin' Objects (객체 만들기)

## 핵심 질문

테스트 코드에서 Dollar와 Franc이라는 **구체적인 하위 클래스**에 직접 의존하는 것이 왜 문제이며, **팩토리 메서드(Factory Method)** 를 통해 어떻게 이 의존성을 줄일 수 있는가?

---

## 1. 문제 인식: 테스트의 구체 클래스 의존

### 1.1 현재 테스트 코드의 모습

현재 테스트들은 Dollar와 Franc이라는 구체 클래스를 직접 참조하고 있다:

```java
public void testMultiplication() {
    Dollar five = new Dollar(5);           // Dollar를 직접 참조
    assertEquals(new Dollar(10), five.times(2));
    assertEquals(new Dollar(15), five.times(3));
}

public void testFrancMultiplication() {
    Franc five = new Franc(5);             // Franc을 직접 참조
    assertEquals(new Franc(10), five.times(2));
    assertEquals(new Franc(15), five.times(3));
}

public void testEquality() {
    assertTrue(new Dollar(5).equals(new Dollar(5)));   // Dollar 직접 참조
    assertFalse(new Dollar(5).equals(new Dollar(6)));
    assertTrue(new Franc(5).equals(new Franc(5)));     // Franc 직접 참조
    assertFalse(new Franc(5).equals(new Franc(6)));
    assertFalse(new Dollar(5).equals(new Franc(5)));
}
```

### 1.2 이것이 왜 문제인가?

테스트가 구체 클래스에 의존하면:

1. **Dollar/Franc 클래스를 변경하거나 제거하면 테스트도 수정해야 한다** — Dollar와 Franc의 중복을 제거하고 싶은데(TODO 리스트의 "Dollar/Franc 중복"), 테스트가 이 클래스들에 직접 묶여 있으면 리팩토링이 어렵다.

2. **추상화 수준이 낮다** — 테스트는 "5달러를 만든다"가 아니라 "`new Dollar(5)` 생성자를 호출한다"고 말하고 있다. 비즈니스 의미보다 구현 세부사항에 가깝다.

3. **미래의 유연성이 떨어진다** — 나중에 Dollar/Franc 하위 클래스를 없애고 Money 하나로 통합하고 싶다면(실제로 Chapter 11에서 그렇게 한다), 모든 테스트를 수정해야 한다.

> **핵심 통찰**: 테스트는 **무엇을**(5달러를 만든다) 표현해야지, **어떻게를**(Dollar 클래스의 생성자를 호출한다) 표현해서는 안 된다. 구체 클래스에 대한 직접 참조는 "어떻게"에 해당한다.

### 1.3 해결 방향: 팩토리 메서드

테스트가 Money라는 상위 타입만 알고, Dollar/Franc이라는 구체 클래스는 모르게 만들려면 **팩토리 메서드(Factory Method)** 가 필요하다:

```java
// 현재: 테스트가 Dollar를 직접 안다
Dollar five = new Dollar(5);

// 목표: 테스트는 Money만 안다
Money five = Money.dollar(5);
```

---

## 2. TDD 사이클

### 2.1 Step 1: times()의 반환 타입을 Money로 변경

먼저 Dollar의 `times()` 반환 타입을 `Dollar`에서 `Money`로 변경한다:

```java
// Dollar.java
class Dollar extends Money {
    Dollar(int amount) {
        this.amount = amount;
    }

    Money times(int multiplier) {         // Dollar → Money
        return new Dollar(amount * multiplier);
    }
}
```

Franc에도 동일하게 적용한다:

```java
// Franc.java
class Franc extends Money {
    Franc(int amount) {
        this.amount = amount;
    }

    Money times(int multiplier) {         // Franc → Money
        return new Franc(amount * multiplier);
    }
}
```

**테스트 실행 → 모든 테스트 통과!**

반환 타입을 `Money`로 변경해도, 실제로 반환되는 객체는 여전히 `Dollar`나 `Franc`이다. 다형성(polymorphism) 덕분에 문제가 없다.

### 2.2 Step 2: Money에 팩토리 메서드 추가

Money 클래스에 Dollar를 생성하는 팩토리 메서드를 추가한다:

```java
// Money.java
class Money {
    protected int amount;

    static Money dollar(int amount) {
        return new Dollar(amount);
    }

    public boolean equals(Object object) {
        Money money = (Money) object;
        return amount == money.amount
            && getClass().equals(money.getClass());
    }
}
```

이제 테스트에서 `new Dollar(5)` 대신 `Money.dollar(5)`를 사용할 수 있다.

### 2.3 Step 3: 테스트에서 Dollar 참조를 Money로 교체

곱하기 테스트를 변경한다:

```java
// Before
public void testMultiplication() {
    Dollar five = new Dollar(5);
    assertEquals(new Dollar(10), five.times(2));
    assertEquals(new Dollar(15), five.times(3));
}

// After
public void testMultiplication() {
    Money five = Money.dollar(5);
    assertEquals(Money.dollar(10), five.times(2));
    assertEquals(Money.dollar(15), five.times(3));
}
```

핵심 변경점:
- `Dollar five` → `Money five` — 변수 타입을 상위 타입으로 변경
- `new Dollar(5)` → `Money.dollar(5)` — 직접 생성자 호출 대신 팩토리 메서드 사용

**테스트 실행 → 모든 테스트 통과!**

### 2.4 Step 4: Franc에도 팩토리 메서드 추가

Franc용 팩토리 메서드도 추가한다:

```java
// Money.java
class Money {
    protected int amount;

    static Money dollar(int amount) {
        return new Dollar(amount);
    }

    static Money franc(int amount) {
        return new Franc(amount);
    }

    public boolean equals(Object object) {
        Money money = (Money) object;
        return amount == money.amount
            && getClass().equals(money.getClass());
    }
}
```

### 2.5 Step 5: 나머지 테스트도 변경

Franc 곱하기 테스트:

```java
// Before
public void testFrancMultiplication() {
    Franc five = new Franc(5);
    assertEquals(new Franc(10), five.times(2));
    assertEquals(new Franc(15), five.times(3));
}

// After
public void testFrancMultiplication() {
    Money five = Money.franc(5);
    assertEquals(Money.franc(10), five.times(2));
    assertEquals(Money.franc(15), five.times(3));
}
```

동등성 테스트:

```java
// Before
public void testEquality() {
    assertTrue(new Dollar(5).equals(new Dollar(5)));
    assertFalse(new Dollar(5).equals(new Dollar(6)));
    assertTrue(new Franc(5).equals(new Franc(5)));
    assertFalse(new Franc(5).equals(new Franc(6)));
    assertFalse(new Dollar(5).equals(new Franc(5)));
}

// After
public void testEquality() {
    assertTrue(Money.dollar(5).equals(Money.dollar(5)));
    assertFalse(Money.dollar(5).equals(Money.dollar(6)));
    assertTrue(Money.franc(5).equals(Money.franc(5)));
    assertFalse(Money.franc(5).equals(Money.franc(6)));
    assertFalse(Money.dollar(5).equals(Money.franc(5)));
}
```

**모든 테스트 통과! Green Bar!**

---

## 3. 팩토리 메서드의 효과

### 3.1 의존성 변화

| 요소 | Before | After |
|------|--------|-------|
| 테스트가 아는 것 | Dollar, Franc, Money | **Money만** |
| 생성 방법 | `new Dollar(5)`, `new Franc(5)` | `Money.dollar(5)`, `Money.franc(5)` |
| 변수 타입 | `Dollar`, `Franc` | `Money` |
| 하위 클래스 의존 | 테스트에서 직접 의존 | Money 내부에 캡슐화 |

### 3.2 이것이 가능하게 하는 것

팩토리 메서드를 통해 테스트가 구체 클래스에서 분리되면:

1. **Dollar/Franc 클래스를 자유롭게 변경할 수 있다** — 테스트는 `Money.dollar(5)`만 호출하므로, 내부 구현이 어떻게 바뀌든 상관없다

2. **하위 클래스를 제거할 수 있다** — `Money.dollar(5)`가 Dollar 대신 Money를 직접 반환해도 테스트는 통과할 것이다

3. **새로운 통화를 쉽게 추가할 수 있다** — `Money.yen(100)` 같은 팩토리 메서드만 추가하면 된다

> **핵심 통찰**: 팩토리 메서드는 **생성과 사용을 분리**한다. 사용하는 쪽(테스트)은 어떤 구체 클래스가 생성되는지 몰라도 된다. 이것은 나중에 Dollar/Franc 하위 클래스를 제거할 때 핵심적인 준비 작업이 된다.

### 3.3 times() 선언 위치에 대한 고려

한 가지 주목할 점: 테스트에서 `five.times(2)`를 호출하는데, `five`의 타입이 `Money`이므로 `times()` 메서드가 Money에 선언되어 있어야 한다. 현재 `times()`는 Dollar와 Franc에만 있다.

이 문제를 해결하기 위해 Money에 추상 메서드를 선언할 수 있다:

```java
abstract class Money {
    protected int amount;

    abstract Money times(int multiplier);

    static Money dollar(int amount) {
        return new Dollar(amount);
    }

    static Money franc(int amount) {
        return new Franc(amount);
    }

    public boolean equals(Object object) {
        Money money = (Money) object;
        return amount == money.amount
            && getClass().equals(money.getClass());
    }
}
```

Money를 `abstract`로 선언하고, `times()`를 추상 메서드로 선언한다. Dollar와 Franc이 이를 구현한다.

**모든 테스트 통과!**

---

## 4. testFrancMultiplication이 정말 필요한가?

### 4.1 중복 테스트의 문제

팩토리 메서드로 전환한 후, 두 곱하기 테스트를 비교해보자:

```java
public void testMultiplication() {
    Money five = Money.dollar(5);
    assertEquals(Money.dollar(10), five.times(2));
    assertEquals(Money.dollar(15), five.times(3));
}

public void testFrancMultiplication() {
    Money five = Money.franc(5);
    assertEquals(Money.franc(10), five.times(2));
    assertEquals(Money.franc(15), five.times(3));
}
```

이 두 테스트는 **거의 동일하다**. 유일한 차이는 `dollar` vs `franc`뿐이다. Dollar와 Franc의 `times()` 구현이 동일하므로(둘 다 `new X(amount * multiplier)` 패턴), 하나를 제거해도 테스트 커버리지에 큰 영향이 없다.

Kent Beck은 이 중복 테스트를 **아직 제거하지 않는다**. Dollar와 Franc의 `times()` 구현이 아직 통합되지 않았기 때문이다. 통합이 완료되면 하나를 제거할 수 있을 것이다.

---

## 5. 코드 진화 과정 전체 추적

**Before (Chapter 7 종료 시점)**:

```java
class Money {
    protected int amount;

    public boolean equals(Object object) {
        Money money = (Money) object;
        return amount == money.amount
            && getClass().equals(money.getClass());
    }
}

class Dollar extends Money {
    Dollar(int amount) { this.amount = amount; }
    Dollar times(int multiplier) {
        return new Dollar(amount * multiplier);
    }
}

class Franc extends Money {
    Franc(int amount) { this.amount = amount; }
    Franc times(int multiplier) {
        return new Franc(amount * multiplier);
    }
}
```

**After (Chapter 8 종료 시점)**:

```java
abstract class Money {
    protected int amount;

    abstract Money times(int multiplier);

    static Money dollar(int amount) {
        return new Dollar(amount);
    }

    static Money franc(int amount) {
        return new Franc(amount);
    }

    public boolean equals(Object object) {
        Money money = (Money) object;
        return amount == money.amount
            && getClass().equals(money.getClass());
    }
}

class Dollar extends Money {
    Dollar(int amount) { this.amount = amount; }
    Money times(int multiplier) {
        return new Dollar(amount * multiplier);
    }
}

class Franc extends Money {
    Franc(int amount) { this.amount = amount; }
    Money times(int multiplier) {
        return new Franc(amount * multiplier);
    }
}
```

주요 변경점 요약:

| 변경 사항 | 이유 |
|----------|------|
| Money를 abstract로 변경 | times()를 추상 메서드로 선언하기 위해 |
| times() 반환 타입을 Money로 변경 | 상위 타입으로 통일 |
| 팩토리 메서드 `dollar()`, `franc()` 추가 | 테스트에서 구체 클래스 의존 제거 |
| 테스트에서 `new Dollar()` → `Money.dollar()` | 추상화 수준 향상 |

---

## 6. 이 챕터에서 완성된 코드

```java
// Money.java
abstract class Money {
    protected int amount;

    abstract Money times(int multiplier);

    static Money dollar(int amount) {
        return new Dollar(amount);
    }

    static Money franc(int amount) {
        return new Franc(amount);
    }

    public boolean equals(Object object) {
        Money money = (Money) object;
        return amount == money.amount
            && getClass().equals(money.getClass());
    }
}
```

```java
// Dollar.java
class Dollar extends Money {
    Dollar(int amount) {
        this.amount = amount;
    }

    Money times(int multiplier) {
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

    Money times(int multiplier) {
        return new Franc(amount * multiplier);
    }
}
```

```java
// 테스트
public void testMultiplication() {
    Money five = Money.dollar(5);
    assertEquals(Money.dollar(10), five.times(2));
    assertEquals(Money.dollar(15), five.times(3));
}

public void testFrancMultiplication() {
    Money five = Money.franc(5);
    assertEquals(Money.franc(10), five.times(2));
    assertEquals(Money.franc(15), five.times(3));
}

public void testEquality() {
    assertTrue(Money.dollar(5).equals(Money.dollar(5)));
    assertFalse(Money.dollar(5).equals(Money.dollar(6)));
    assertTrue(Money.franc(5).equals(Money.franc(5)));
    assertFalse(Money.franc(5).equals(Money.franc(6)));
    assertFalse(Money.dollar(5).equals(Money.franc(5)));
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
- [x] ~~Franc과 Dollar 비교~~
- [ ] 통화(Currency)?
- [ ] testFrancMultiplication 제거?

새로운 TODO 항목으로 `testFrancMultiplication 제거?`가 추가되었다. Dollar와 Franc의 곱하기 테스트가 중복이므로, `times()` 통합 후 하나를 제거할 수 있을 것이다.

---

## 요약

- 테스트에서 **구체 클래스(Dollar, Franc)에 대한 직접 참조**를 제거했다.
- Money 클래스에 **팩토리 메서드** `Money.dollar(5)`, `Money.franc(5)`를 추가했다.
- 테스트의 변수 타입을 `Dollar`/`Franc`에서 **`Money`**로 변경했다.
- `times()`의 반환 타입도 `Money`로 통일하고, Money에 **추상 메서드**로 선언했다.
- 팩토리 메서드는 **생성과 사용을 분리**한다. 테스트는 어떤 구체 클래스가 생성되는지 알 필요가 없다.
- 이 변경은 나중에 **Dollar/Franc 하위 클래스를 제거**하기 위한 핵심 준비 작업이다.
- 테스트가 추상 타입(Money)에만 의존하면, 내부 구현(Dollar, Franc 클래스 구조)을 **자유롭게 리팩토링**할 수 있다.

---

## 다른 챕터와의 관계

- **Chapter 5 (Franc-ly Speaking)**: Dollar를 복사하여 Franc을 만들면서 생긴 중복 문제가, 이 챕터에서 팩토리 메서드를 통해 테스트 레벨에서 해소되기 시작했다.
- **Chapter 6 (Equality for All, Redux)**: Money 상위 클래스를 도입한 챕터. 이 챕터에서 Money를 abstract로 만들고 팩토리 메서드를 추가하여 더 완전한 상위 클래스로 발전시켰다.
- **Chapter 9 (Times We're Livin' In)**: 통화(currency) 개념을 도입한다. 팩토리 메서드 내부에서 통화를 설정하는 방식으로 구현된다.
- **Chapter 10 (Interesting Times)**: Dollar와 Franc의 `times()` 중복을 제거한다. 팩토리 메서드 덕분에 테스트 수정 없이 `times()` 구현을 통합할 수 있다.
- **Chapter 11 (The Root of All Evil)**: Dollar와 Franc 하위 클래스를 완전히 제거한다. 이 챕터에서 만든 팩토리 메서드가 `new Dollar()` 대신 `new Money("USD")`를 반환하도록 변경하면, 테스트는 **아무 변경 없이** 통과한다. 이것이 팩토리 메서드의 진정한 위력이다.
- **Chapter 30 (Design Patterns)**: 팩토리 메서드가 TDD의 핵심 설계 패턴으로 정리된다.
