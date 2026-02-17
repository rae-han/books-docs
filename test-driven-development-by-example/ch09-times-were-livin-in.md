# Chapter 9: Times We're Livin' In (우리가 사는 시대)

## 핵심 질문

Dollar와 Franc를 하나의 Money 클래스로 통합하기 위해 **통화(currency)** 개념을 어떻게 도입하는가? 서브클래스를 구별하는 기준이 "클래스"에서 "필드 값"으로 전환되는 과정은 어떻게 진행되는가?

---

## 1. 이전 챕터까지의 상황

### 1.1 현재 코드 구조

Chapter 8까지의 작업으로 다음과 같은 구조가 형성되어 있다:

```
Money (추상 클래스)
├── amount (protected 필드)
├── equals(Object)
├── static dollar(int amount) — 팩토리 메서드
├── static franc(int amount)  — 팩토리 메서드
│
├── Dollar extends Money
│   └── times(int multiplier)
│
└── Franc extends Money
    └── times(int multiplier)
```

`Dollar`와 `Franc`의 `times()` 메서드는 거의 동일하다:

```java
// Dollar
Dollar times(int multiplier) {
    return Money.dollar(amount * multiplier);
}

// Franc
Franc times(int multiplier) {
    return Money.franc(amount * multiplier);
}
```

두 서브클래스의 차이는 이제 `times()`에서 `Money.dollar()`를 호출하느냐, `Money.franc()`를 호출하느냐뿐이다. 이 차이를 제거하려면 **통화(currency)** 라는 개념이 필요하다.

### 1.2 현재 TODO 리스트

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
- [ ] **공용 times**
- [x] ~~Franc와 Dollar 비교하기~~
- [ ] **통화(Currency)?**
- [x] ~~testFrancMultiplication을 제거해야 하나?~~

Kent Beck은 이 시점에서 "통화(Currency)?" 항목을 다루기로 결정한다.

---

## 2. 통화 개념 도입의 동기

### 2.1 왜 통화가 필요한가?

현재 Dollar와 Franc를 구별하는 것은 **클래스 자체**다. 즉, `instanceof Dollar`인지 `instanceof Franc`인지로 구분한다. 하지만 서브클래스를 제거하려면 이 구분 기준을 **클래스**에서 **데이터(필드 값)**로 전환해야 한다.

통화(currency)를 문자열 필드로 도입하면:
- `Dollar` → `Money(currency: "USD")`
- `Franc` → `Money(currency: "CHF")`

이렇게 되면 서브클래스 없이도 통화를 구별할 수 있다.

### 2.2 Kent Beck의 접근 방식

Kent Beck은 큰 그림을 먼저 그리지 않는다. "통화 필드를 도입하고, equals()를 수정하고, times()를 올리고, 서브클래스를 삭제한다"라는 전체 계획을 세우지 않는다. 대신 **가장 작은 첫 걸음** — `currency()` 메서드를 추가하는 것 — 부터 시작한다.

> **핵심 통찰**: TDD에서는 전체 리팩토링 계획을 세우고 한꺼번에 실행하지 않는다. 한 단계를 완료하고, 테스트가 통과하는 것을 확인한 후, 다음 단계를 결정한다. 이것은 큰 리팩토링을 안전하게 만드는 핵심 전략이다.

---

## 3. TDD 사이클

### 3.1 Red — 통화를 반환하는 테스트 작성

먼저 각 Money 객체가 자신의 통화를 알고 있는지 테스트한다:

```java
public void testCurrency() {
    assertEquals("USD", Money.dollar(1).currency());
    assertEquals("CHF", Money.franc(1).currency());
}
```

이 테스트는 컴파일 에러를 발생시킨다 — `currency()` 메서드가 아직 존재하지 않기 때문이다.

### 3.2 Green — currency() 메서드 구현

Kent Beck은 단계적으로 접근한다.

**Step 1**: Money에 추상 메서드를 선언한다:

```java
// Money.java
abstract class Money {
    protected int amount;

    abstract String currency();

    // ... equals(), dollar(), franc() 등
}
```

**Step 2**: 각 서브클래스에서 구현한다:

```java
// Dollar.java
class Dollar extends Money {
    String currency() {
        return "USD";
    }

    // ... times() 등
}
```

```java
// Franc.java
class Franc extends Money {
    String currency() {
        return "CHF";
    }

    // ... times() 등
}
```

**테스트 통과! Green Bar!**

### 3.3 Refactor — 통화를 인스턴스 변수로 옮기기

두 서브클래스의 `currency()` 메서드를 보자:

```java
// Dollar:  return "USD";
// Franc:   return "CHF";
```

반환하는 **문자열 값**만 다르다. 이 중복을 제거하려면 통화를 **인스턴스 변수**로 저장하면 된다.

**Step 1**: Dollar에 인스턴스 변수 도입:

```java
class Dollar extends Money {
    private String currency;

    Dollar(int amount) {
        this.amount = amount;
        currency = "USD";
    }

    String currency() {
        return currency;
    }
}
```

테스트 실행 — 여전히 Green Bar.

**Step 2**: Franc에도 동일하게 적용:

```java
class Franc extends Money {
    private String currency;

    Franc(int amount) {
        this.amount = amount;
        currency = "CHF";
    }

    String currency() {
        return currency;
    }
}
```

테스트 실행 — Green Bar.

**Step 3**: 이제 두 서브클래스의 `currency()` 구현이 완전히 동일하다:

```java
// Dollar: return currency;
// Franc:  return currency;
```

`currency` 필드와 `currency()` 메서드를 **Money 슈퍼클래스로 올릴 수 있다**:

```java
abstract class Money {
    protected int amount;
    protected String currency;

    String currency() {
        return currency;
    }

    // ...
}
```

테스트 실행 — Green Bar.

---

## 4. 팩토리 메서드에서 통화 설정

### 4.1 생성자에 통화 전달

현재 통화 문자열은 각 서브클래스의 생성자에서 하드코딩되어 있다 (`currency = "USD"`, `currency = "CHF"`). 이것을 **생성자 파라미터**로 전달하도록 바꾸면 더 유연해진다.

**Step 1**: Dollar 생성자에 통화 파라미터 추가:

```java
class Dollar extends Money {
    Dollar(int amount, String currency) {
        this.amount = amount;
        this.currency = currency;
    }
}
```

이렇게 하면 `Money.dollar()` 팩토리 메서드도 수정해야 한다:

```java
static Money dollar(int amount) {
    return new Dollar(amount, "USD");
}
```

**Step 2**: Franc에도 동일하게 적용:

```java
class Franc extends Money {
    Franc(int amount, String currency) {
        this.amount = amount;
        this.currency = currency;
    }
}

static Money franc(int amount) {
    return new Franc(amount, "CHF");
}
```

테스트 실행 — Green Bar.

### 4.2 생성자를 슈퍼클래스로 올리기

두 서브클래스의 생성자가 이제 완전히 동일하다:

```java
// Dollar:
Dollar(int amount, String currency) {
    this.amount = amount;
    this.currency = currency;
}

// Franc:
Franc(int amount, String currency) {
    this.amount = amount;
    this.currency = currency;
}
```

이 공통 로직을 Money 슈퍼클래스로 올린다:

```java
abstract class Money {
    protected int amount;
    protected String currency;

    Money(int amount, String currency) {
        this.amount = amount;
        this.currency = currency;
    }

    String currency() {
        return currency;
    }

    // ...
}
```

서브클래스는 슈퍼클래스 생성자를 호출한다:

```java
class Dollar extends Money {
    Dollar(int amount, String currency) {
        super(amount, currency);
    }
    // ...
}

class Franc extends Money {
    Franc(int amount, String currency) {
        super(amount, currency);
    }
    // ...
}
```

테스트 실행 — Green Bar.

---

## 5. 이 챕터의 코드 진화 요약

### 5.1 전체 변화 과정

| 단계 | 변경 내용 | 목적 |
|------|----------|------|
| 1 | `currency()` 추상 메서드 추가 | 통화 조회 인터페이스 정의 |
| 2 | Dollar/Franc에서 문자열 반환 | 테스트 통과 (Green) |
| 3 | 인스턴스 변수 `currency` 도입 | 하드코딩된 문자열을 변수로 |
| 4 | `currency` 필드를 Money로 올림 | 중복 제거 (Pull Up Field) |
| 5 | 생성자에 currency 파라미터 추가 | 하드코딩 제거 |
| 6 | 팩토리 메서드에서 통화 전달 | 통화를 외부에서 주입 |
| 7 | 생성자를 Money로 올림 | 중복 제거 (Pull Up Constructor) |

### 5.2 최종 코드

```java
// Money.java
abstract class Money {
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

    String currency() {
        return currency;
    }

    public boolean equals(Object object) {
        Money money = (Money) object;
        return amount == money.amount
            && getClass().equals(money.getClass());
    }

    abstract Money times(int multiplier);
}
```

```java
// Dollar.java
class Dollar extends Money {
    Dollar(int amount, String currency) {
        super(amount, currency);
    }

    Money times(int multiplier) {
        return Money.dollar(amount * multiplier);
    }
}
```

```java
// Franc.java
class Franc extends Money {
    Franc(int amount, String currency) {
        super(amount, currency);
    }

    Money times(int multiplier) {
        return Money.franc(amount * multiplier);
    }
}
```

> **핵심 통찰**: 이 챕터의 리팩토링은 **작은 단계들의 연속**이었다. 각 단계마다 테스트를 실행하여 Green Bar를 확인했다. 한 번에 "통화 필드 추가 + 생성자 변경 + 메서드 올리기"를 했다면 중간에 실수를 발견하기 어려웠을 것이다. 작은 단계가 안전망 역할을 한다.

---

## 6. equals()에서 클래스 비교의 문제

현재 `equals()`는 `getClass().equals(money.getClass())`로 비교하고 있다. 하지만 통화 필드가 도입되었으므로 곧 **클래스 비교 대신 통화 비교**로 바뀔 수 있다:

```java
// 현재: 클래스로 구분
return amount == money.amount && getClass().equals(money.getClass());

// 미래: 통화로 구분
return amount == money.amount && currency.equals(money.currency);
```

이 변경은 아직 하지 않는다. Dollar와 Franc 서브클래스가 제거될 때 자연스럽게 이루어질 것이다. Kent Beck은 **필요할 때까지 변경을 미룬다**.

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
- [ ] **공용 times**
- [x] ~~Franc와 Dollar 비교하기~~
- [x] ~~**통화(Currency)?**~~
- [x] ~~testFrancMultiplication을 제거해야 하나?~~

"통화(Currency)?" 항목이 완료되었다. 이제 Dollar와 Franc를 구별하는 것은 클래스가 아니라 **통화 문자열("USD", "CHF")**이 될 수 있다. 다음 단계는 `times()`를 공통으로 만드는 것이다.

---

## 요약

- **통화(currency) 개념을 도입**하여 Dollar와 Franc를 "클래스"가 아닌 "데이터(문자열)"로 구별할 수 있는 기반을 마련했다.
- `currency()` 메서드를 먼저 추가하고, 인스턴스 변수로 전환한 후, 슈퍼클래스로 올리는 **점진적 리팩토링**을 수행했다.
- 생성자에 통화 파라미터를 추가하여 **하드코딩을 제거**했다.
- **팩토리 메서드**(`Money.dollar()`, `Money.franc()`)에서 통화 문자열을 전달하는 구조가 완성되었다.
- 모든 변경은 **작은 단계**로 이루어졌고, 각 단계마다 테스트를 실행하여 Green Bar를 확인했다.
- 이 챕터에서 도입한 통화 필드는 서브클래스 제거의 핵심 전제 조건이 된다.

---

## 다른 챕터와의 관계

- **Chapter 7 (Apples and Oranges)**: Dollar와 Franc의 동등성 비교에서 클래스 비교를 도입했다. 이 챕터에서 통화 필드를 도입함으로써, 향후 클래스 비교를 통화 비교로 대체할 수 있는 기반을 만들었다.
- **Chapter 8 (Makin' Objects)**: 팩토리 메서드 `Money.dollar()`, `Money.franc()`를 도입했다. 이 챕터에서 팩토리 메서드가 통화 문자열을 생성자에 전달하는 역할까지 맡게 되었다.
- **Chapter 10 (Interesting Times)**: `times()` 메서드를 Money 슈퍼클래스로 올리는 작업을 수행한다. 이 챕터에서 통화가 도입되었기 때문에 가능해지는 작업이다.
- **Chapter 11 (The Root of All Evil)**: Dollar와 Franc 서브클래스를 완전히 제거한다. 이 챕터에서 통화 필드를 도입한 것이 그 제거의 핵심 전제 조건이었다.
