# Chapter 5: Franc-ly Speaking (프랑에 대해 말하자면)

## 핵심 질문

다중 통화 시스템의 첫 번째 확장으로, Dollar와 유사한 Franc(스위스 프랑) 클래스가 필요할 때 TDD에서는 어떻게 접근하는가? 복사-붙여넣기(copy-paste)는 TDD에서 허용되는가?

---

## 1. 새로운 요구사항: 스위스 프랑

### 1.1 TODO 리스트에서 다음 항목 선택

현재 TODO 리스트:

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

첫 번째 항목(`$5 + 10 CHF = $10`)은 아직 너무 크다. 다중 통화 더하기를 구현하려면 먼저 Franc(스위스 프랑)이라는 개념 자체가 필요하다. 그래서 `$5 CHF × 2 = $10 CHF`부터 시작한다.

### 1.2 전략적 선택: 어떻게 구현할 것인가?

Franc 클래스를 만드는 방법은 여러 가지가 있다:

1. **처음부터 추상화**: Dollar와 Franc의 공통 상위 클래스 Money를 먼저 설계하고, 두 통화를 하위 클래스로 만든다
2. **복사-붙여넣기 후 정리**: Dollar를 그대로 복사하여 Franc를 만들고, 나중에 중복을 제거한다

Kent Beck은 **2번**을 선택한다. 이것은 의도적인 결정이다.

> **핵심 통찰**: TDD에서 중복은 악이지만, **Green Bar를 얻는 것이 최우선**이다. 복사-붙여넣기로 빠르게 Green Bar를 얻고, 그 다음에 중복을 제거하는 것이 Kent Beck의 전략이다. "먼저 동작하게 만들고(Make it work), 그 다음에 올바르게 만든다(Make it right)."

---

## 2. TDD 사이클

### 2.1 Red — Franc 곱하기 테스트 작성

Dollar의 곱하기 테스트와 거의 동일한 Franc 테스트를 작성한다:

```java
public void testFrancMultiplication() {
    Franc five = new Franc(5);
    assertEquals(new Franc(10), five.times(2));
    assertEquals(new Franc(15), five.times(3));
}
```

이 테스트는 **컴파일 에러**가 발생한다. `Franc` 클래스가 존재하지 않기 때문이다.

**Red Bar!**

### 2.2 Green — Dollar를 복사하여 Franc 생성

가장 빠르게 Green Bar를 얻는 방법: **Dollar 클래스를 통째로 복사하여 이름만 Franc으로 바꾼다.**

```java
// Franc.java — Dollar.java를 복사한 것!
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

변경된 부분은 오직:
- 클래스 이름: `Dollar` → `Franc`
- `times()`의 반환 타입: `Dollar` → `Franc`
- `equals()`의 캐스팅 타입: `Dollar` → `Franc`

**테스트 통과! Green Bar!**

### 2.3 Refactor — 지금은 하지 않는다 (그러나 인식한다)

이 시점에서 코드는 **끔찍한 상태**다. Dollar와 Franc 사이에 엄청난 중복이 있다:

```java
// Dollar.java                           // Franc.java
class Dollar {                           class Franc {
    private int amount;                      private int amount;

    Dollar(int amount) {                     Franc(int amount) {
        this.amount = amount;                    this.amount = amount;
    }                                        }

    Dollar times(int multiplier) {           Franc times(int multiplier) {
        return new Dollar(amount *               return new Franc(amount *
            multiplier);                             multiplier);
    }                                        }

    public boolean equals(Object object) {   public boolean equals(Object object) {
        Dollar dollar = (Dollar) object;         Franc franc = (Franc) object;
        return amount == dollar.amount;          return amount == franc.amount;
    }                                        }
}                                        }
```

두 클래스가 **거의 완전히 동일하다**. Kent Beck은 이 중복을 분명히 인식하고 있으며, TODO 리스트에 기록한다. 하지만 **지금은** 중복 제거를 하지 않는다.

왜인가?

1. **Green Bar를 막 얻었다** — 동작하는 상태에서 변경을 시작하는 것이 안전하다
2. **중복 제거는 별개의 작업이다** — 새 기능 추가와 리팩토링을 동시에 하면 위험하다
3. **한 번에 한 가지만** — TDD의 핵심 원칙

---

## 3. "복사-붙여넣기가 허용된다고?"

### 3.1 TDD에서의 복사-붙여넣기

소프트웨어 개발에서 복사-붙여넣기는 보통 **안티패턴**으로 간주된다. 하지만 Kent Beck은 TDD에서는 다른 관점을 제시한다:

| 관점 | 일반적인 개발 | TDD |
|------|-------------|-----|
| 복사-붙여넣기 | 악이다. 처음부터 추상화해야 한다 | Green Bar를 빠르게 얻기 위한 **임시** 전략이다 |
| 중복 | 피해야 한다 | 만들어도 되지만, **반드시 다음 단계에서 제거**해야 한다 |
| 추상화 시점 | 코드를 작성하기 전 | 동작하는 코드가 있은 후 |

### 3.2 복사-붙여넣기의 전제 조건

Kent Beck의 복사-붙여넣기 전략이 동작하려면 반드시 다음 조건이 충족되어야 한다:

1. **중복을 TODO 리스트에 명시적으로 기록한다** — 잊지 않기 위해
2. **가능한 빨리 중복을 제거한다** — 다음 몇 챕터 안에
3. **테스트가 중복 제거 과정을 보호한다** — 리팩토링 중 실수하면 테스트가 잡아낸다

> **핵심 통찰**: 중복을 만드는 것이 TDD의 죄가 아니다. **중복을 인식하지 못하거나, 인식하고도 방치하는 것**이 죄다. Kent Beck은 중복을 만들면서 동시에 TODO 리스트에 적어 놓았다. 이것은 "나는 이 빚을 알고 있고, 갚을 것이다"라는 약속이다.

### 3.3 대안: 처음부터 추상화했다면?

만약 Dollar를 복사하지 않고 처음부터 Money 상위 클래스를 설계했다면 어떠했을까?

- 설계에 더 많은 시간이 걸렸을 것이다
- 추상화가 맞는지 확신하기 어려웠을 것이다 (구체적인 예제가 하나뿐이었으므로)
- Green Bar를 얻기까지 더 많은 단계가 필요했을 것이다

Kent Beck의 철학: **구체적인 예제가 두 개 이상 있을 때 추상화하라.** Dollar 하나만 있을 때는 추상화의 방향이 불확실했다. 이제 Dollar와 Franc이 모두 있으므로, **무엇이 공통이고 무엇이 다른지** 명확하게 보인다.

---

## 4. 코드 진화 과정 전체 추적

**Step 1**: Chapter 4 종료 시점 — Dollar만 존재

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

**Step 2**: Franc 클래스 추가 (Dollar를 복사)

```java
// Franc.java (새 파일)
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

---

## 5. 이 챕터에서 완성된 코드

```java
// Dollar.java (변경 없음)
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
// Franc.java (새로 추가)
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

```java
// 테스트
public void testMultiplication() {
    Dollar five = new Dollar(5);
    assertEquals(new Dollar(10), five.times(2));
    assertEquals(new Dollar(15), five.times(3));
}

public void testEquality() {
    assertTrue(new Dollar(5).equals(new Dollar(5)));
    assertFalse(new Dollar(5).equals(new Dollar(6)));
}

public void testFrancMultiplication() {
    Franc five = new Franc(5);
    assertEquals(new Franc(10), five.times(2));
    assertEquals(new Franc(15), five.times(3));
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
- [ ] **Dollar/Franc 중복**
- [ ] **공통 equals()**
- [ ] **공통 times()**
- [ ] **Franc과 Dollar 비교**
- [ ] **통화(Currency)?**

`$5 CHF × 2 = $10 CHF`가 완료되었지만, 대가로 많은 중복 관련 TODO 항목이 추가되었다. 이것은 **기술 부채(technical debt)** 를 의도적으로 떠안은 것이다. 다음 챕터들에서 하나씩 갚아나갈 것이다.

---

## 요약

- 다중 통화 지원의 첫 단계로 **Franc(스위스 프랑)** 클래스를 만들었다.
- Dollar 클래스를 **통째로 복사**하여 Franc를 만들었다 — 이것은 의도적인 TDD 전략이다.
- 복사-붙여넣기로 **Green Bar를 빠르게 얻었고**, 대신 TODO 리스트에 중복 제거 항목을 추가했다.
- TDD에서 복사-붙여넣기는 **임시적인 전략**이다. 반드시 중복을 제거하는 단계가 뒤따라야 한다.
- **구체적인 예제가 두 개 이상 있을 때** 추상화하는 것이 더 안전하다. Dollar 하나만 있을 때보다, Dollar와 Franc 두 개가 있을 때 공통점과 차이점이 명확하게 보인다.
- 이 챕터는 TDD의 핵심 원칙 "**먼저 동작하게 만들고, 그 다음에 올바르게 만든다**"를 가장 극적으로 보여주는 챕터다.

---

## 다른 챕터와의 관계

- **Chapter 1~4**: Dollar 클래스의 전체 개발 과정이 이 챕터에서 Franc에 그대로 복제되었다. 4개 챕터에 걸친 작업을 1분 만에 복사한 셈이다.
- **Chapter 6 (Equality for All, Redux)**: Dollar와 Franc의 `equals()` 중복을 제거하기 위해 공통 상위 클래스 Money를 도입한다. 이 챕터의 기술 부채를 갚기 시작하는 첫 단계다.
- **Chapter 7 (Apples and Oranges)**: Dollar(5)와 Franc(5)가 동등하게 취급되는 문제를 발견하고 해결한다.
- **Chapter 10 (Interesting Times)**: Dollar와 Franc의 `times()` 중복을 제거한다.
- **Chapter 11 (The Root of All Evil)**: Dollar와 Franc 하위 클래스 자체를 제거한다 — 이 챕터에서 만든 Franc 클래스가 최종적으로 사라지는 시점이다.
