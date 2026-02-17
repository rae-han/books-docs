# Chapter 7: Apples and Oranges (사과와 오렌지)

## 핵심 질문

Dollar(5)와 Franc(5)는 같은가? 서로 다른 통화의 동일 금액은 동등해야 하는가? `equals()` 구현에서 **클래스(타입) 비교**는 왜 필요하며, 이것은 나중에 어떻게 발전하는가?

---

## 1. 문제 발견: 5달러 = 5프랑?

### 1.1 현재 equals()의 동작

Chapter 6에서 `equals()`를 Money 클래스로 올렸다:

```java
// Money.java
public boolean equals(Object object) {
    Money money = (Money) object;
    return amount == money.amount;
}
```

이 코드는 **amount만 비교**한다. 그래서 다음과 같은 일이 벌어진다:

```java
new Dollar(5).equals(new Franc(5));  // true를 반환한다!
```

5달러와 5프랑은 **다른 통화**이므로 동등하지 않아야 한다. 하지만 현재 구현은 amount(5)만 비교하므로 `true`를 반환한다.

### 1.2 현실에서의 비유

이것은 "사과와 오렌지를 비교하는" 문제다 — 영어에서 "comparing apples and oranges"는 **본질적으로 다른 것을 비교하는 오류**를 뜻하는 관용구다. 5달러와 5프랑은 숫자는 같지만 **종류가 다르다**. 마치 사과 5개와 오렌지 5개가 다른 것처럼.

> **핵심 통찰**: 동등성 비교는 단순히 "값이 같은가?"만이 아니라 "**같은 종류**의 값인가?"도 확인해야 한다. 이것을 놓치면 서로 다른 통화가 같다고 판단하는 심각한 버그가 발생한다.

---

## 2. TDD 사이클

### 2.1 Red — 실패해야 하는 테스트 작성

Dollar와 Franc이 동등하지 않음을 확인하는 테스트를 추가한다:

```java
public void testEquality() {
    assertTrue(new Dollar(5).equals(new Dollar(5)));
    assertFalse(new Dollar(5).equals(new Dollar(6)));
    assertTrue(new Franc(5).equals(new Franc(5)));
    assertFalse(new Franc(5).equals(new Franc(6)));
    assertFalse(new Dollar(5).equals(new Franc(5)));  // 새로 추가!
}
```

마지막 줄이 새로 추가된 테스트다: `Dollar(5)`와 `Franc(5)`는 같지 않아야 한다.

이 테스트는 **실패**한다. 현재 `equals()`는 amount만 비교하므로 `Dollar(5).equals(Franc(5))`가 `true`를 반환한다.

**Red Bar!**

### 2.2 Green — 클래스 비교 추가

`equals()`에서 amount뿐만 아니라 **클래스(타입)**도 비교하도록 수정한다:

```java
// Money.java
public boolean equals(Object object) {
    Money money = (Money) object;
    return amount == money.amount
        && getClass().equals(money.getClass());
}
```

`getClass()`는 Java에서 객체의 **런타임 클래스**를 반환한다:
- `new Dollar(5).getClass()` → `Dollar.class`
- `new Franc(5).getClass()` → `Franc.class`

이제 `Dollar(5).equals(Franc(5))`는:
1. `amount == money.amount` → `5 == 5` → `true`
2. `getClass().equals(money.getClass())` → `Dollar.class.equals(Franc.class)` → `false`
3. `true && false` → **`false`**

**테스트 통과! Green Bar!**

### 2.3 Refactor — 클래스 비교 vs 통화 비교

Kent Beck은 여기서 잠시 멈추고 생각한다. 클래스를 비교하는 것이 **올바른 방법**인가?

현재 접근:
```java
getClass().equals(money.getClass())  // Dollar.class == Franc.class?
```

대안적 접근:
```java
currency.equals(money.currency)      // "USD" == "CHF"?
```

**클래스 비교**는 구현에 의존하는 방법이다 — Dollar와 Franc이 별개의 클래스라는 사실에 의존한다. **통화 비교**는 도메인 개념에 의존하는 방법이다 — 통화가 같은지를 비교한다.

Kent Beck은 현재는 **클래스 비교**를 유지한다. 이유:

1. 아직 통화(currency) 개념이 도입되지 않았다
2. 통화 개념을 도입하려면 먼저 다른 작업(TODO 리스트의 "통화?" 항목)이 필요하다
3. 현재의 테스트를 통과시키는 데 클래스 비교가 충분하다

> **핵심 통찰**: TDD에서는 **지금 필요한 만큼만** 구현한다. 통화 비교가 더 "올바른" 설계일 수 있지만, 그것은 통화 개념이 실제로 필요해질 때 도입한다. 미리 설계하면 과잉 엔지니어링이 된다.

---

## 3. 클래스 비교의 한계

### 3.1 왜 클래스 비교는 임시적인 해결책인가?

클래스 비교가 문제가 되는 시나리오:

```java
// 만약 Dollar를 직접 사용하지 않고, Money의 팩토리 메서드를 사용한다면?
Money fiveUSD = Money.dollar(5);   // 내부적으로 Dollar를 반환할 수도 있고,
                                   // Money를 직접 반환할 수도 있다

// 만약 Dollar와 Franc의 차이가 클래스가 아니라 currency 필드로만 구분된다면?
// getClass() 비교는 더 이상 작동하지 않는다
```

클래스 비교 vs 통화 비교:

| 측면 | 클래스 비교 (`getClass()`) | 통화 비교 (`currency`) |
|------|--------------------------|---------------------|
| **구현 의존성** | 높음 — 별도 클래스가 필요 | 낮음 — 필드로 구분 가능 |
| **유연성** | 낮음 — 클래스 구조에 묶임 | 높음 — 클래스 구조와 무관 |
| **현재 적합성** | 적합 — Dollar/Franc이 별도 클래스 | 불필요 — 아직 currency 개념 없음 |
| **미래 적합성** | 부적합 — 하위 클래스 제거 시 깨짐 | 적합 — 통화 추가 시 자연스럽게 동작 |

### 3.2 Kent Beck의 의도

Kent Beck은 이 불완전함을 **알고 있다**. 하지만 TDD의 원칙에 따라:

1. 현재 테스트가 통과한다 → 충분하다
2. 미래의 문제는 미래의 테스트가 드러낼 것이다
3. TODO 리스트에 "통화(Currency)?" 항목이 있으므로 잊지 않을 것이다

이것이 TDD의 **점진적 설계(incremental design)** 철학이다. 완벽한 설계를 한 번에 만드는 것이 아니라, 테스트가 요구할 때마다 설계를 진화시킨다.

---

## 4. 코드 진화 과정 전체 추적

**Step 1**: Chapter 6 종료 시점의 Money.equals()

```java
class Money {
    protected int amount;

    public boolean equals(Object object) {
        Money money = (Money) object;
        return amount == money.amount;    // amount만 비교
    }
}
```

**Step 2**: 클래스 비교 추가

```java
class Money {
    protected int amount;

    public boolean equals(Object object) {
        Money money = (Money) object;
        return amount == money.amount
            && getClass().equals(money.getClass());  // 클래스도 비교!
    }
}
```

---

## 5. 이 챕터에서 완성된 코드

```java
// Money.java
class Money {
    protected int amount;

    public boolean equals(Object object) {
        Money money = (Money) object;
        return amount == money.amount
            && getClass().equals(money.getClass());
    }
}
```

```java
// Dollar.java (변경 없음)
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
// Franc.java (변경 없음)
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
    assertFalse(new Dollar(5).equals(new Franc(5)));
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

`Franc과 Dollar 비교`가 완료되었다 — 클래스 비교를 통해 서로 다른 통화가 동등하지 않도록 만들었다. `통화(Currency)?` 항목은 여전히 남아 있다. 이것은 클래스 비교를 통화 비교로 교체하는 작업이 될 것이다.

---

## 요약

- `Dollar(5).equals(Franc(5))`가 `true`를 반환하는 **버그를 발견**했다 — 서로 다른 통화의 동일 금액이 동등하게 취급되는 문제.
- `equals()`에 **`getClass()` 비교**를 추가하여, 같은 클래스의 객체만 동등할 수 있도록 수정했다.
- **클래스 비교는 임시적인 해결책**이다. 더 나은 방법은 통화(currency) 필드를 비교하는 것이지만, 아직 통화 개념이 도입되지 않았으므로 현재는 클래스 비교로 충분하다.
- TDD에서는 **지금 필요한 만큼만 구현**한다. 미래의 더 나은 설계는 미래의 테스트가 요구할 때 도입한다.
- "사과와 오렌지" — 비교의 대상이 같은 **종류**인지 확인하는 것은 동등성 구현의 기본적인 요구사항이다.

---

## 다른 챕터와의 관계

- **Chapter 3 (Equality for All)**: `equals()`를 처음 구현한 챕터다. 그때는 Dollar만 있었으므로 클래스 비교가 필요 없었다.
- **Chapter 6 (Equality for All, Redux)**: `equals()`를 Money로 올렸지만, 클래스 비교를 추가하지 않아 버그가 잠재해 있었다. 이 챕터에서 그 버그를 수정했다.
- **Chapter 8 (Makin' Objects)**: 팩토리 메서드를 도입하여 Dollar/Franc 생성을 추상화한다. 이것은 클래스 비교에서 통화 비교로 전환하기 위한 준비 단계가 된다.
- **Chapter 9 (Times We're Livin' In)**: 통화(currency) 개념을 도입한다. 이 챕터에서 임시로 사용한 클래스 비교가 통화 비교로 교체되는 시점이다.
- **Chapter 11 (The Root of All Evil)**: Dollar와 Franc 클래스가 제거된다. 이 시점에서 클래스 비교는 더 이상 작동하지 않으므로, 통화 비교로의 전환이 필수적이었다.
