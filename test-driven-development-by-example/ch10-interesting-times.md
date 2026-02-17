# Chapter 10: Interesting Times (흥미로운 시간들)

## 핵심 질문

Dollar와 Franc의 `times()` 메서드가 거의 동일할 때, 어떻게 이 중복을 제거하여 **슈퍼클래스로 올릴** 수 있는가? 두 메서드를 **완전히 동일하게** 만드는 핵심 전략은 무엇인가?

---

## 1. 문제 인식: times()의 중복

### 1.1 현재 상황

Chapter 9에서 통화(currency)를 도입한 후, Dollar와 Franc의 `times()` 메서드는 다음과 같다:

```java
// Dollar.java
Money times(int multiplier) {
    return Money.dollar(amount * multiplier);
}

// Franc.java
Money times(int multiplier) {
    return Money.franc(amount * multiplier);
}
```

두 메서드의 차이는 단 하나 — `Money.dollar()`를 호출하느냐, `Money.franc()`를 호출하느냐뿐이다.

### 1.2 목표

두 `times()` 메서드를 **완전히 동일하게** 만들어서 Money 슈퍼클래스로 올리는 것이 이 챕터의 목표다.

---

## 2. 팩토리 메서드를 직접 생성자 호출로 대체

### 2.1 첫 번째 시도 — 직접 Money 생성자 호출

팩토리 메서드 대신 `new Money(...)`를 직접 호출하면 두 메서드가 동일해질까?

```java
// Dollar
Money times(int multiplier) {
    return new Money(amount * multiplier, "USD");
}

// Franc
Money times(int multiplier) {
    return new Money(amount * multiplier, "CHF");
}
```

아직 `"USD"` vs `"CHF"` 차이가 있다. 하지만 이 통화 문자열은 **자기 자신의 currency 필드**와 같다! 따라서:

```java
// Dollar
Money times(int multiplier) {
    return new Money(amount * multiplier, currency);
}

// Franc
Money times(int multiplier) {
    return new Money(amount * multiplier, currency);
}
```

이제 두 메서드가 **완전히 동일**하다!

### 2.2 문제: Money는 추상 클래스

하지만 `new Money(...)`는 Money가 추상 클래스이기 때문에 컴파일되지 않는다. Money를 **구체 클래스(concrete class)** 로 만들어야 한다.

---

## 3. TDD 사이클

### 3.1 Red — Money를 직접 생성하는 테스트

Money가 구체 클래스가 되면 `new Money(10, "USD")`로 직접 생성할 수 있어야 한다. 이것이 제대로 동작하는지 확인하는 테스트가 필요하다. 사실 기존 테스트들이 이미 이 역할을 하고 있지만, Kent Beck은 조심스럽게 진행한다.

현재 `equals()`는 **클래스를 비교**하고 있다:

```java
public boolean equals(Object object) {
    Money money = (Money) object;
    return amount == money.amount
        && getClass().equals(money.getClass());
}
```

`times()`에서 `new Money(10, "USD")`를 반환하면, 이 객체의 클래스는 `Money`이다. 그런데 `Money.dollar(10)`은 `new Dollar(10, "USD")`를 반환하므로 클래스가 `Dollar`이다. 이 둘을 `equals()`로 비교하면 **클래스가 다르므로 같지 않다고 판단**한다.

이것은 문제다. `new Money(10, "USD")`와 `Money.dollar(10)`은 같은 10 USD를 나타내므로 동등해야 한다.

### 3.2 equals() 변경 — 클래스 비교를 통화 비교로

이 문제를 해결하려면 `equals()`에서 클래스 비교를 **통화 비교**로 바꿔야 한다:

```java
public boolean equals(Object object) {
    Money money = (Money) object;
    return amount == money.amount
        && currency().equals(money.currency());
}
```

하지만 이 변경이 기존 테스트를 깨뜨리지 않는지 확인해야 한다. Kent Beck은 **먼저 테스트를 작성**한다:

```java
public void testDifferentClassEquality() {
    assertTrue(new Money(10, "USD").equals(new Dollar(10, "USD")));
}
```

이 테스트를 실행하려면 Money가 구체 클래스여야 한다.

### 3.3 Green — Money를 구체 클래스로 변경

**Step 1**: Money에서 `abstract` 키워드를 제거하고, `times()` 메서드에 기본 구현을 제공한다:

```java
class Money {
    protected int amount;
    protected String currency;

    Money(int amount, String currency) {
        this.amount = amount;
        this.currency = currency;
    }

    Money times(int multiplier) {
        return new Money(amount * multiplier, currency);
    }

    // ...
}
```

**Step 2**: `equals()`에서 클래스 비교를 통화 비교로 변경:

```java
public boolean equals(Object object) {
    Money money = (Money) object;
    return amount == money.amount
        && currency().equals(money.currency());
}
```

**테스트 실행 — Green Bar!**

`testDifferentClassEquality` 테스트가 통과한다. `new Money(10, "USD")`와 `new Dollar(10, "USD")`가 같다고 판단된다. 통화와 금액이 같으면 클래스와 관계없이 동등하다.

> **핵심 통찰**: `equals()`에서 클래스 비교를 통화 비교로 바꾼 것은 단순한 코드 변경이 아니다. 이것은 **"Dollar는 USD 통화를 가진 Money다"** 라는 개념적 전환을 의미한다. 서브클래스의 정체성이 "타입"에서 "데이터"로 이동했다.

### 3.4 Refactor — times()를 슈퍼클래스로 올리기

이제 Dollar와 Franc의 `times()`를 변경할 수 있다.

**Step 1**: Dollar의 `times()`에서 팩토리 메서드 대신 직접 생성자를 호출:

```java
// Dollar.java (변경 전)
Money times(int multiplier) {
    return Money.dollar(amount * multiplier);
}

// Dollar.java (변경 후)
Money times(int multiplier) {
    return new Money(amount * multiplier, currency);
}
```

테스트 실행 — Green Bar.

**Step 2**: Franc에도 동일하게 적용:

```java
// Franc.java (변경 전)
Money times(int multiplier) {
    return Money.franc(amount * multiplier);
}

// Franc.java (변경 후)
Money times(int multiplier) {
    return new Money(amount * multiplier, currency);
}
```

테스트 실행 — Green Bar.

**Step 3**: 이제 Dollar와 Franc의 `times()` 메서드가 **완전히 동일**하다. 그리고 이 구현은 Money 슈퍼클래스에 이미 존재한다! 따라서 서브클래스에서 `times()`를 **삭제**할 수 있다:

```java
// Money.java — times()가 여기에만 존재
class Money {
    // ...

    Money times(int multiplier) {
        return new Money(amount * multiplier, currency);
    }
}

// Dollar.java — times() 삭제됨
class Dollar extends Money {
    Dollar(int amount, String currency) {
        super(amount, currency);
    }
}

// Franc.java — times() 삭제됨
class Franc extends Money {
    Franc(int amount, String currency) {
        super(amount, currency);
    }
}
```

테스트 실행 — **Green Bar!**

---

## 4. 리팩토링의 핵심 전략 분석

### 4.1 두 메서드를 같게 만들기 위한 전략

| 단계 | 전략 | 효과 |
|------|------|------|
| 1 | 팩토리 메서드(`Money.dollar()`) → 직접 생성자(`new Money(...)`) | 두 메서드의 호출 대상 통일 |
| 2 | 하드코딩된 통화("USD", "CHF") → 인스턴스 변수(`currency`) | 두 메서드의 파라미터 통일 |
| 3 | 서브클래스의 메서드 삭제 → 슈퍼클래스 메서드 사용 | 중복 제거 완료 |

핵심은 **"차이를 없애기 위해 한 단계씩 접근"** 한다는 것이다. 두 메서드의 차이가 `Money.dollar()` vs `Money.franc()`였을 때, 이를 한 번에 해결하지 않고:

1. 먼저 두 메서드가 같은 **형태**를 갖도록 만든다
2. 그 다음 다른 **값**을 변수로 대체한다
3. 마지막으로 동일해진 메서드를 올린다

### 4.2 이 과정에서의 안전장치

```
Dollar.times() 수정 → 테스트 → Green
Franc.times() 수정 → 테스트 → Green
서브클래스 times() 삭제 → 테스트 → Green
```

각 단계마다 테스트를 실행한다. 만약 어느 단계에서 Red Bar가 나타나면, **방금 한 변경만 되돌리면 된다**. 이것이 TDD에서 작은 단계를 강조하는 이유다.

> **핵심 통찰**: 리팩토링의 핵심 기법 중 하나는 **"차이를 줄이기"**다. 두 코드 조각이 비슷하지만 다를 때, 차이를 하나씩 제거하여 완전히 같게 만든 후 하나를 삭제한다. 이때 각 단계에서 테스트를 실행하면 안전하게 진행할 수 있다.

---

## 5. 이 챕터에서 완성된 코드

```java
// Money.java
class Money {
    protected int amount;
    protected String currency;

    Money(int amount, String currency) {
        this.amount = amount;
        this.currency = currency;
    }

    static Money dollar(int amount) {
        return new Dollar(amount, "USD");
    }

    static Money franc(int amount) {
        return new Franc(amount, "CHF");
    }

    Money times(int multiplier) {
        return new Money(amount * multiplier, currency);
    }

    String currency() {
        return currency;
    }

    public boolean equals(Object object) {
        Money money = (Money) object;
        return amount == money.amount
            && currency().equals(money.currency());
    }
}
```

```java
// Dollar.java — times()가 없다!
class Dollar extends Money {
    Dollar(int amount, String currency) {
        super(amount, currency);
    }
}
```

```java
// Franc.java — times()가 없다!
class Franc extends Money {
    Franc(int amount, String currency) {
        super(amount, currency);
    }
}
```

Dollar와 Franc에는 이제 **생성자밖에 남지 않았다**. 이 빈 껍데기 서브클래스들은 다음 챕터에서 제거될 운명이다.

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
- [x] ~~동등성 비교와 클래스 비교~~
- [x] ~~5 CHF × 2 = 10 CHF~~
- [x] ~~Dollar/Franc 중복~~
- [x] ~~공용 equals~~
- [x] ~~**공용 times**~~
- [x] ~~Franc와 Dollar 비교하기~~
- [x] ~~통화(Currency)?~~
- [x] ~~testFrancMultiplication을 제거해야 하나?~~

"공용 times" 항목이 완료되었다. `times()`는 이제 Money 슈퍼클래스에만 존재하며, Dollar와 Franc는 빈 서브클래스가 되었다.

---

## 요약

- Dollar와 Franc의 `times()` 메서드 차이를 **한 단계씩** 제거하여 완전히 동일하게 만들었다.
- 핵심 전략: **팩토리 메서드 호출을 직접 생성자 호출로 대체**하고, **하드코딩된 통화를 인스턴스 변수로 대체**했다.
- Money를 추상 클래스에서 **구체 클래스로 변경**하여 `new Money(amount, currency)`가 가능하게 했다.
- `equals()`의 **클래스 비교를 통화 비교로 변경**하여, 다른 클래스라도 같은 통화와 금액이면 동등하게 만들었다.
- `times()`를 Money 슈퍼클래스로 올리고 서브클래스에서 삭제했다.
- 결과적으로 Dollar와 Franc에는 **생성자만 남아** 사실상 빈 클래스가 되었다.
- 모든 변경은 **작은 단계**로 이루어졌고, 각 단계마다 테스트를 실행하여 안전성을 확인했다.

---

## 다른 챕터와의 관계

- **Chapter 9 (Times We're Livin' In)**: 통화(currency) 필드와 생성자를 도입했다. 이 챕터에서 그 통화 필드를 `times()` 메서드에서 활용하여 중복을 제거했다.
- **Chapter 7 (Apples and Oranges)**: `equals()`에 클래스 비교를 도입했다. 이 챕터에서 그것을 통화 비교로 대체했다.
- **Chapter 11 (The Root of All Evil)**: 이 챕터에서 빈 껍데기가 된 Dollar와 Franc 서브클래스를 완전히 제거한다.
- **Chapter 8 (Makin' Objects)**: 팩토리 메서드를 도입했다. 이 챕터에서 `times()` 내부의 팩토리 메서드 호출을 직접 생성자 호출로 대체했지만, 외부에서 사용하는 팩토리 메서드(`Money.dollar()`, `Money.franc()`)는 유지된다.
