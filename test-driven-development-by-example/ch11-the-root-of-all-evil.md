# Chapter 11: The Root of All Evil (모든 악의 근원)

## 핵심 질문

더 이상 아무런 고유 동작이 없는 서브클래스(Dollar, Franc)를 **안전하게 제거**하려면 어떤 과정을 거쳐야 하는가? 불필요한 코드를 제거하는 것이 왜 중요하며, TDD에서 이를 어떤 시점에 수행하는가?

---

## 1. 문제 인식: 빈 서브클래스

### 1.1 현재 Dollar와 Franc의 상태

Chapter 10에서 `times()`를 Money 슈퍼클래스로 올린 후, Dollar와 Franc에 남아 있는 코드는 생성자뿐이다:

```java
class Dollar extends Money {
    Dollar(int amount, String currency) {
        super(amount, currency);
    }
}

class Franc extends Money {
    Franc(int amount, String currency) {
        super(amount, currency);
    }
}
```

이 서브클래스들은:
- `equals()`? → Money에 있다
- `times()`? → Money에 있다
- `currency()`? → Money에 있다
- 고유 필드? → 없다
- 고유 메서드? → 없다

**아무런 고유 동작이 없다.** 단지 팩토리 메서드에서 `new Dollar(...)`, `new Franc(...)`를 호출하기 때문에 존재할 뿐이다.

### 1.2 "모든 악의 근원"

챕터 제목 "The Root of All Evil"은 이 **불필요한 서브클래스**를 가리킨다. 불필요한 코드는 복잡성의 근원이다:

- 이해해야 할 코드가 늘어난다
- 수정할 때 고려해야 할 곳이 늘어난다
- "이 클래스는 무슨 역할인가?"라는 불필요한 질문을 만든다

> **핵심 통찰**: 소프트웨어에서 "악의 근원"은 복잡한 코드가 아니라 **불필요한 코드**다. 아무런 가치를 제공하지 않으면서 유지보수 비용만 발생시킨다. TDD의 리팩토링 단계에서 이러한 코드를 적극적으로 제거해야 한다.

---

## 2. 서브클래스 제거 전략

### 2.1 팩토리 메서드에서의 참조 변경

Dollar와 Franc이 참조되는 곳은 **팩토리 메서드** 뿐이다:

```java
static Money dollar(int amount) {
    return new Dollar(amount, "USD");
}

static Money franc(int amount) {
    return new Franc(amount, "CHF");
}
```

이 팩토리 메서드에서 `new Dollar(...)` 대신 `new Money(...)`를 사용하면, Dollar 클래스에 대한 참조가 사라진다. Franc도 마찬가지다.

### 2.2 테스트에서의 참조 확인

테스트 코드에서 `Dollar`나 `Franc`를 직접 참조하는 곳이 있는지 확인해야 한다. Chapter 8에서 팩토리 메서드를 도입했기 때문에, 대부분의 테스트는 이미 `Money.dollar()`, `Money.franc()`를 사용하고 있다.

---

## 3. TDD 사이클

### 3.1 Red/Green — 팩토리 메서드 변경

이 챕터는 새로운 기능을 추가하는 것이 아니라 **기존 기능을 유지하면서 코드를 제거**하는 리팩토링이다. 따라서 새 테스트를 작성하기보다는 기존 테스트가 계속 통과하는지 확인하면서 진행한다.

**Step 1**: `Money.dollar()` 팩토리 메서드 변경:

```java
// 변경 전
static Money dollar(int amount) {
    return new Dollar(amount, "USD");
}

// 변경 후
static Money dollar(int amount) {
    return new Money(amount, "USD");
}
```

테스트 실행 — **Green Bar!**

Chapter 10에서 `equals()`를 통화 비교로 변경했기 때문에, `new Money(10, "USD")`와 `new Dollar(10, "USD")`는 동등하다. 기존 테스트가 모두 통과한다.

**Step 2**: `Money.franc()` 팩토리 메서드 변경:

```java
// 변경 전
static Money franc(int amount) {
    return new Franc(amount, "CHF");
}

// 변경 후
static Money franc(int amount) {
    return new Money(amount, "CHF");
}
```

테스트 실행 — **Green Bar!**

### 3.2 Refactor — 서브클래스 삭제

이제 Dollar와 Franc 클래스를 참조하는 코드가 **어디에도 없다**. 안전하게 삭제할 수 있다.

**Step 3**: Dollar 클래스 삭제.

**Step 4**: Franc 클래스 삭제.

테스트 실행 — **Green Bar!**

### 3.3 테스트 코드 정리

서브클래스가 사라졌으므로, 서브클래스의 존재를 전제로 한 테스트가 있다면 정리해야 한다.

`testDifferentClassEquality` 테스트를 확인해보자:

```java
public void testDifferentClassEquality() {
    assertTrue(new Money(10, "USD").equals(new Dollar(10, "USD")));
}
```

이 테스트는 `Dollar` 클래스가 더 이상 존재하지 않으므로 **삭제**한다. 이 테스트는 서브클래스에서 슈퍼클래스로 전환하는 과정에서 필요했던 것이지, 영구적으로 필요한 테스트가 아니었다.

> **핵심 통찰**: 테스트도 코드다. 더 이상 가치를 제공하지 않는 테스트는 제거해야 한다. 리팩토링 과정에서 작성한 "발판(scaffolding)" 테스트는 리팩토링이 완료된 후 제거하는 것이 자연스럽다.

---

## 4. 제거 후의 코드

### 4.1 최종 코드 — Money 하나로 통합

```java
// Money.java — 이것이 전부다!
class Money {
    protected int amount;
    protected String currency;

    Money(int amount, String currency) {
        this.amount = amount;
        this.currency = currency;
    }

    static Money dollar(int amount) {
        return new Money(amount, "USD");
    }

    static Money franc(int amount) {
        return new Money(amount, "CHF");
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

    public String toString() {
        return amount + " " + currency;
    }
}
```

### 4.2 파일 구조의 변화

```
변경 전:                    변경 후:
├── Money.java              ├── Money.java
├── Dollar.java (삭제됨)
├── Franc.java  (삭제됨)
```

Money 하나로 모든 것이 표현된다. Dollar는 `Money(amount, "USD")`, Franc는 `Money(amount, "CHF")`일 뿐이다.

### 4.3 테스트 코드

```java
public void testMultiplication() {
    Money five = Money.dollar(5);
    assertEquals(Money.dollar(10), five.times(2));
    assertEquals(Money.dollar(15), five.times(3));
}

public void testEquality() {
    assertTrue(Money.dollar(5).equals(Money.dollar(5)));
    assertFalse(Money.dollar(5).equals(Money.dollar(6)));
    assertFalse(Money.franc(5).equals(Money.dollar(5)));
}

public void testCurrency() {
    assertEquals("USD", Money.dollar(1).currency());
    assertEquals("CHF", Money.franc(1).currency());
}
```

테스트 코드에서 `Dollar`와 `Franc`라는 단어가 완전히 사라졌다. 모든 것이 `Money.dollar()`, `Money.franc()`이라는 팩토리 메서드를 통해 표현된다.

---

## 5. 이 챕터의 교훈

### 5.1 코드 제거의 가치

| 관점 | 서브클래스 있을 때 | 서브클래스 제거 후 |
|------|------------------|-----------------|
| **파일 수** | 3개 (Money, Dollar, Franc) | 1개 (Money) |
| **클래스 수** | 3개 | 1개 |
| **상속 관계** | 있음 (이해 비용 발생) | 없음 |
| **동작 이해** | 3개 클래스를 오가며 확인 | 1개 클래스만 확인 |
| **변경 시 고려사항** | 슈퍼클래스-서브클래스 일관성 | 단일 클래스만 고려 |

### 5.2 점진적 제거의 중요성

이 챕터에서 서브클래스를 한 번에 삭제하지 않았다. 순서는:

1. `Money.dollar()`에서 `new Dollar(...)` → `new Money(...)` (테스트 실행)
2. `Money.franc()`에서 `new Franc(...)` → `new Money(...)` (테스트 실행)
3. Dollar 클래스 삭제 (테스트 실행)
4. Franc 클래스 삭제 (테스트 실행)

각 단계마다 테스트를 실행했다. 만약 2단계에서 문제가 발생했다면, 1단계의 변경은 안전하다는 것을 이미 확인한 상태다. **문제의 범위가 항상 "방금 한 변경"으로 한정된다.**

### 5.3 팩토리 메서드의 역할

Chapter 8에서 도입한 팩토리 메서드(`Money.dollar()`, `Money.franc()`)가 이 챕터에서 빛을 발한다. 만약 팩토리 메서드 없이 테스트 코드 곳곳에서 `new Dollar(5)`를 직접 호출했다면, 서브클래스를 제거할 때 모든 테스트를 수정해야 했을 것이다.

팩토리 메서드는 **객체 생성의 세부사항을 캡슐화**한다. 내부 구현이 `new Dollar(5, "USD")`에서 `new Money(5, "USD")`로 바뀌어도 외부(테스트 코드)는 전혀 영향을 받지 않는다.

> **핵심 통찰**: 팩토리 메서드는 미래의 변경을 대비하여 "미리" 만드는 것이 아니다. Chapter 8에서 팩토리 메서드를 도입한 이유는 서브클래스 삭제를 예견했기 때문이 아니라, 그 시점에서 코드의 중복을 줄이기 위해서였다. 하지만 결과적으로 이 챕터의 리팩토링을 크게 쉽게 만들었다. **좋은 설계는 종종 예상치 못한 변경도 쉽게 만든다.**

---

## 6. Chapter 5~11의 여정 회고

Chapter 5에서 Franc를 도입한 이후 11개 챕터에 걸쳐 일어난 일을 돌아보면:

| 챕터 | 핵심 작업 | 방향 |
|------|----------|------|
| Ch 5 | Franc 클래스 도입 (Dollar 복사) | 중복 생성 |
| Ch 6 | 공용 equals()를 Money로 올림 | 중복 제거 |
| Ch 7 | Dollar ≠ Franc 비교 추가 | 구분 강화 |
| Ch 8 | 팩토리 메서드 도입 | 캡슐화 |
| Ch 9 | 통화(currency) 필드 도입 | 데이터 기반 구분 |
| Ch 10 | 공용 times()를 Money로 올림 | 중복 제거 |
| **Ch 11** | **Dollar/Franc 서브클래스 삭제** | **중복 제거 완료** |

주목할 점: Chapter 5에서 **의도적으로 중복을 만들었다**. TDD에서는 먼저 테스트를 통과시키는 것이 우선이므로, 기존 Dollar 코드를 복사하여 Franc를 빠르게 만들었다. 그리고 Chapter 6~11에 걸쳐 그 중복을 **체계적으로, 안전하게** 제거했다.

이것이 TDD의 리듬이다: **먼저 동작하게 만들고(Green), 그 다음 깨끗하게 만든다(Refactor).**

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
- [x] ~~**Dollar/Franc 중복 제거 완료**~~
- [x] ~~공용 equals~~
- [x] ~~공용 times~~
- [x] ~~Franc와 Dollar 비교하기~~
- [x] ~~통화(Currency)?~~
- [x] ~~testFrancMultiplication을 제거해야 하나?~~
- [ ] **$5 + $5 = $10**
- [ ] $5 + $5에서 Money 반환하기

이제 서브클래스가 완전히 제거되었으므로, 다음 큰 목표는 **다중 통화 덧셈**이다.

---

## 요약

- Dollar와 Franc 서브클래스는 **모든 고유 동작이 슈퍼클래스로 올라간 후** 빈 껍데기가 되었다.
- 팩토리 메서드에서 `new Dollar(...)` / `new Franc(...)`를 `new Money(...)`로 변경하여 서브클래스에 대한 **모든 참조를 제거**했다.
- 참조가 없어진 Dollar, Franc 클래스를 **삭제**했다.
- 서브클래스의 존재를 전제로 한 테스트(`testDifferentClassEquality`)도 함께 제거했다.
- 불필요한 코드는 **복잡성의 근원**이다. TDD의 리팩토링 단계에서 적극적으로 제거해야 한다.
- Chapter 5에서 의도적으로 만든 중복이 Chapter 6~11에 걸쳐 체계적으로 제거되었다. 이것이 TDD의 **"먼저 동작하게, 그 다음 깨끗하게"** 리듬이다.
- 팩토리 메서드(`Money.dollar()`, `Money.franc()`)가 객체 생성을 캡슐화함으로써, 내부 구현 변경 시 테스트 코드 수정이 불필요했다.

---

## 다른 챕터와의 관계

- **Chapter 5 (Franc-ly Speaking)**: Franc 서브클래스를 Dollar를 복사하여 만들었다. 이 챕터에서 그 서브클래스를 제거했다. Chapter 5~11은 "중복 생성 → 중복 제거"의 완전한 사이클이다.
- **Chapter 8 (Makin' Objects)**: 팩토리 메서드를 도입했다. 이 챕터에서 팩토리 메서드 덕분에 서브클래스 제거가 외부 코드에 영향을 주지 않았다.
- **Chapter 10 (Interesting Times)**: `times()`를 Money로 올리고 `equals()`의 클래스 비교를 통화 비교로 변경했다. 이 두 변경이 이 챕터에서의 서브클래스 제거를 가능하게 만들었다.
- **Chapter 12 (Addition, Finally)**: 서브클래스 중복이 해결되었으므로, 드디어 다중 통화 덧셈이라는 큰 과제에 착수한다.
- **Chapter 17 (Money Retrospective)**: Part I 전체를 돌아보며, 이 서브클래스 생성-제거 사이클의 의미를 분석한다.
