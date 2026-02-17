# Chapter 6: 고칠 것은 많고 시간은 없고 (I Don't Have Much Time and I Have to Change It)

## 핵심 질문

시간이 부족한 상황에서 레거시 코드를 변경해야 할 때, 테스트 없이 빠르게 변경하는 것이 정말 더 빠른 방법인가? 안전하게 변경할 수 있는 실용적인 기법에는 무엇이 있는가?

---

## 1. 시간 압박 속의 딜레마

개발자들이 레거시 코드에서 가장 자주 하는 변명은 **"시간이 없다"** 이다. 새로운 기능을 추가하거나 버그를 수정해야 하는데, 테스트를 작성하고 코드를 정리할 시간이 없다고 느낀다. 그래서 기존 코드에 직접 변경을 밀어 넣고, "나중에 정리하겠다"고 스스로 약속한다. 하지만 그 "나중"은 거의 오지 않는다.

> Pay now or pay more later. 지금 투자하지 않으면 나중에 더 큰 비용을 치른다.

Feathers는 이 장에서 **테스트 없이 변경하는 것이 결코 더 빠르지 않다**는 것을 강조한다. 단기적으로는 테스트 작성 시간을 절약하는 것처럼 보이지만, 장기적으로는 디버깅 시간, 회귀 버그 수정 시간, 코드 이해 시간이 기하급수적으로 증가한다.

### 1.1 테스트와 함께 변경하는 것이 결국 더 빠른 이유

| 접근 방식 | 단기적 | 장기적 |
|-----------|--------|--------|
| **테스트 없이 변경** | 빠르게 느껴짐 | 버그 증가, 이해 어려움, 변경 비용 급증 |
| **테스트와 함께 변경** | 약간 느리게 느껴짐 | 안정적, 변경 용이, 비용 점진적 감소 |

그럼에도 불구하고 현실에서는 정말로 시간이 부족한 경우가 있다. 이 장에서 소개하는 네 가지 기법은 **기존 코드를 최소한으로 건드리면서도 새로운 코드는 테스트 가능하게 작성하는** 타협점을 제시한다.

---

## 2. Sprout Method (발아 메서드)

### 2.1 개념

Sprout Method는 기존 메서드에 새로운 기능을 추가해야 할 때, **기존 코드 사이에 새 코드를 끼워넣는 대신, 새 기능을 별도의 메서드로 작성**하고 기존 메서드에서 이를 호출하는 기법이다.

핵심 아이디어는 간단하다: **새로 작성하는 코드만큼은 반드시 테스트를 갖추자.**

### 2.2 예시: 변경 전

다음은 트랜잭션 리스트에 항목을 추가하는 Java 코드이다:

```java
public class TransactionGate {
    public void postEntries(List entries) {
        for (Iterator it = entries.iterator(); it.hasNext(); ) {
            Entry entry = (Entry) it.next();
            entry.postDate();
        }
        transactionBundle.getListManager().add(entries);
    }
}
```

여기에 **중복 항목을 걸러내는 기능**을 추가해야 한다고 가정하자. 테스트 없이 변경한다면 기존 메서드 안에 직접 중복 제거 로직을 넣게 된다:

```java
// 나쁜 예: 기존 메서드에 직접 코드를 끼워넣음
public void postEntries(List entries) {
    List entriesToAdd = new LinkedList();
    for (Iterator it = entries.iterator(); it.hasNext(); ) {
        Entry entry = (Entry) it.next();
        if (!transactionBundle.getListManager().hasEntry(entry)) {
            entriesToAdd.add(entry);
        }
    }
    for (Iterator it = entriesToAdd.iterator(); it.hasNext(); ) {
        Entry entry = (Entry) it.next();
        entry.postDate();
    }
    transactionBundle.getListManager().add(entriesToAdd);
}
```

이 방식은 기존 코드와 새 코드가 뒤섞여서, 무엇이 원래 있던 동작이고 무엇이 새로 추가된 동작인지 구분하기 어렵다.

### 2.3 예시: Sprout Method 적용

```java
public class TransactionGate {
    public void postEntries(List entries) {
        List entriesToAdd = uniqueEntries(entries);  // 새 메서드 호출
        for (Iterator it = entriesToAdd.iterator(); it.hasNext(); ) {
            Entry entry = (Entry) it.next();
            entry.postDate();
        }
        transactionBundle.getListManager().add(entriesToAdd);
    }

    // Sprout Method: 새로 작성한 메서드, 테스트 가능
    List uniqueEntries(List entries) {
        List result = new LinkedList();
        for (Iterator it = entries.iterator(); it.hasNext(); ) {
            Entry entry = (Entry) it.next();
            if (!transactionBundle.getListManager().hasEntry(entry)) {
                result.add(entry);
            }
        }
        return result;
    }
}
```

`uniqueEntries` 메서드는 **독립적으로 테스트할 수 있다**:

```java
public void testUniqueEntries() {
    TransactionGate gate = new TransactionGate(/* 테스트용 설정 */);
    // 중복 항목이 포함된 리스트 준비
    List entries = Arrays.asList(entry1, entry2, entry1);
    List result = gate.uniqueEntries(entries);
    assertEquals(2, result.size());
    // ...
}
```

### 2.4 Sprout Method 적용 절차

1. **변경이 필요한 위치를 식별**한다.
2. 변경이 기존 메서드 안에 연속된 코드 블록으로 표현될 수 있다면, **그 블록을 새 메서드 호출로 대체하는 코드를 작성**한다.
3. **새 메서드에 필요한 지역 변수를 파악**하고, 이를 새 메서드의 매개변수로 전달한다.
4. 새 메서드가 기존 메서드에 **값을 반환해야 하는지 판단**한다.
5. **테스트 주도 개발(TDD)로 새 메서드를 개발**한다.
6. 기존 메서드에서 **새 메서드를 호출**한다.

### 2.5 장점과 단점

**장점:**
- 기존 코드와 새 코드가 **명확히 분리**된다.
- 새 코드는 **테스트 가능**하다.
- 기존 메서드의 변경이 **최소화**된다 (호출문 한 줄 추가).
- 시간 투자가 적으면서도 코드 품질이 개선된다.

**단점:**
- 기존 메서드는 **여전히 테스트되지 않은 상태**로 남는다.
- 기존 메서드가 점점 더 많은 메서드를 호출하게 되면, **조정자(coordinator) 역할만 하는 비대한 메서드**가 될 수 있다.
- 원래 메서드의 전체적인 알고리즘 흐름을 이해하기가 더 어려워질 수 있다.

> Sprout Method는 포기가 아니다. "이 메서드에서는 아직 테스트를 만들 수 없지만, 최소한 새 코드만큼은 테스트하겠다"는 실용적인 선택이다.

---

## 3. Sprout Class (발아 클래스)

### 3.1 개념

Sprout Class는 Sprout Method와 같은 개념이지만 **클래스 레벨**에서 적용한다. 기존 클래스를 테스트 하네스에 넣는 것이 **매우 어렵거나 불가능**할 때, 새로운 기능을 **완전히 새로운 클래스**로 작성하는 기법이다.

### 3.2 Sprout Class를 사용하는 경우

다음과 같은 상황에서 Sprout Class가 적합하다:

1. **기존 클래스의 생성자가 너무 복잡**하여 테스트 하네스에 넣을 수 없을 때
2. 기존 클래스에 **숨겨진 의존성(hidden dependency)** 이 너무 많을 때
3. 추가하려는 기능이 **완전히 독립적인 책임**을 가질 때
4. Sprout Method를 쓰고 싶지만, 기존 클래스의 인스턴스를 **테스트에서 생성할 수 없**을 때

### 3.3 예시

기존에 `QuarterlyReportGenerator` 클래스가 있고, 보고서에 새로운 헤더 행을 추가해야 한다고 하자:

```java
public class QuarterlyReportGenerator {
    // 매우 복잡한 생성자, 데이터베이스 연결, 설정 파일 등 의존성 다수
    public QuarterlyReportGenerator(DBConnection db, ConfigManager config,
                                     AuthService auth, ...) {
        // ...
    }

    public String generate() {
        // 수백 줄의 복잡한 보고서 생성 로직
        ...
    }
}
```

이 클래스를 테스트 하네스에 넣는 것은 현실적으로 불가능하다. 새 헤더 행을 추가하는 기능을 Sprout Class로 분리한다:

```java
// Sprout Class: 완전히 새로운 클래스, 독립적으로 테스트 가능
public class QuarterlyReportHeaderProducer {
    public String makeHeader() {
        return "Report Header\n"
             + "Generated: " + new Date() + "\n"
             + "---------------------\n";
    }
}
```

기존 클래스에서는 이 새 클래스를 사용한다:

```java
public class QuarterlyReportGenerator {
    public String generate() {
        // 새 클래스 호출
        String header = new QuarterlyReportHeaderProducer().makeHeader();
        // 기존 로직 계속...
        ...
    }
}
```

`QuarterlyReportHeaderProducer`에 대한 테스트는 간단하게 작성할 수 있다:

```java
public void testMakeHeader() {
    QuarterlyReportHeaderProducer producer = new QuarterlyReportHeaderProducer();
    String header = producer.makeHeader();
    assertNotNull(header);
    assertTrue(header.contains("Report Header"));
}
```

### 3.4 장점과 단점

**장점:**
- 기존 클래스를 테스트 하네스에 넣을 필요가 없다.
- 새 클래스는 **처음부터 깨끗하게, 테스트와 함께** 작성할 수 있다.
- 나중에 보면 이 새 클래스가 **적절한 책임 분리**의 시작점이 되기도 한다.

**단점:**
- 개념적으로 하나의 동작이 **두 클래스에 걸쳐 분산**될 수 있다.
- 클래스가 너무 작고 많아지면 코드 탐색이 어려워질 수 있다.
- "이것을 위해 새 클래스가 필요한가?"라는 기계적인 느낌이 들 수 있다. 하지만 **시간이 지나면 이 클래스가 자연스러운 설계 요소로 자리 잡는 경우가 많다**.

---

## 4. Wrap Method (감싸기 메서드)

### 4.1 개념

Wrap Method는 기존 메서드에 **새로운 동작을 추가해야 하지만, 기존 동작과 새 동작이 시간적으로 함께 실행되어야 할 때** (즉, 하나의 호출 시점에 두 동작이 모두 수행되어야 할 때) 사용하는 기법이다.

핵심 아이디어: 기존 메서드의 **이름을 바꾸고**, 원래 이름으로 새 메서드를 만들어서 **기존 메서드와 새 동작을 순서대로 호출**한다.

### 4.2 예시: 변경 전

직원의 급여를 지급하는 메서드가 있다:

```java
public class Employee {
    public void pay() {
        Money amount = new Money();
        for (Iterator it = timecards.iterator(); it.hasNext(); ) {
            Timecard card = (Timecard) it.next();
            if (payPeriod.contains(card.getDate())) {
                amount.add(card.getHours() * payRate);
            }
        }
        payDispatcher.pay(this, date, amount);
    }
}
```

요구사항: 급여를 지급할 때마다 **로그 파일에 직원 이름을 기록**해야 한다.

### 4.3 변형 1: 기존 메서드 이름 변경 방식

```java
public class Employee {
    // 원래 pay() → dispatchPay()로 이름 변경
    private void dispatchPay() {
        Money amount = new Money();
        for (Iterator it = timecards.iterator(); it.hasNext(); ) {
            Timecard card = (Timecard) it.next();
            if (payPeriod.contains(card.getDate())) {
                amount.add(card.getHours() * payRate);
            }
        }
        payDispatcher.pay(this, date, amount);
    }

    // 새 동작을 별도 메서드로 작성 (테스트 가능)
    void logPayment() {
        logFile.writeEntry(this.name, date);
    }

    // 원래 이름의 메서드가 두 동작을 순서대로 호출
    public void pay() {
        logPayment();
        dispatchPay();
    }
}
```

이렇게 하면 **기존 `pay()`를 호출하던 모든 코드는 변경 없이** 새로운 동작(로깅)을 함께 수행하게 된다.

### 4.4 변형 2: 새 이름으로 추출하는 방식

기존 메서드 이름을 바꾸는 것이 부담스러울 때, 대안으로 **새 통합 메서드에 새 이름을 부여**하는 방식이 있다:

```java
public class Employee {
    // 기존 메서드는 그대로 유지
    public void pay() {
        Money amount = new Money();
        for (Iterator it = timecards.iterator(); it.hasNext(); ) {
            Timecard card = (Timecard) it.next();
            if (payPeriod.contains(card.getDate())) {
                amount.add(card.getHours() * payRate);
            }
        }
        payDispatcher.pay(this, date, amount);
    }

    // 새 통합 메서드
    public void makePayment() {
        logPayment();
        pay();
    }

    void logPayment() {
        logFile.writeEntry(this.name, date);
    }
}
```

이 경우에는 **호출 측 코드를 `pay()` → `makePayment()`로 변경**해야 한다.

### 4.5 Wrap Method 적용 절차

1. 변경해야 할 메서드를 식별한다.
2. 새로운 동작이 기존 동작의 **전(before)** 또는 **후(after)** 에 실행되어야 하는지 판단한다.
3. **기존 메서드의 이름을 변경**하고 (변형 1), 원래 이름의 메서드를 새로 만든다.
4. 새 메서드에서 **이름이 바뀐 기존 메서드**와 **새로운 동작 메서드**를 호출한다.
5. 새로운 동작 메서드를 **TDD로 개발**한다.

### 4.6 장점과 단점

**장점:**
- 기존 메서드의 **내부 코드를 전혀 수정하지 않는다**.
- 새 동작과 기존 동작이 **명확히 분리**된다.
- `logPayment()`은 독립적으로 **테스트 가능**하다.
- 기존 코드의 동작 보존이 **확실**하다.

**단점:**
- 기존 메서드의 이름이 바뀌므로, **메서드 이름의 의미가 달라질 수 있다**.
- 변형 1에서는 원래 이름이 이제 **두 가지 일을 하는 메서드**가 되므로, 이름이 부정확해질 수 있다.
- Sprout Method와 달리, 기존 동작과 새 동작의 **실행 순서에 의미가 있을 때만** 자연스럽다.

---

## 5. Wrap Class (감싸기 클래스)

### 5.1 개념

Wrap Class는 Wrap Method의 **클래스 레벨 버전**이다. 기존 클래스를 감싸는(wrap) 새로운 클래스를 만들어, 기존 동작에 새 동작을 추가한다. 이것은 GoF의 **Decorator 패턴**과 본질적으로 동일하다.

### 5.2 예시

앞의 `Employee` 예시를 Wrap Class로 구현하면:

```java
// 기존 Employee 클래스는 수정하지 않음
public class Employee {
    public void pay() {
        Money amount = new Money();
        for (Iterator it = timecards.iterator(); it.hasNext(); ) {
            Timecard card = (Timecard) it.next();
            if (payPeriod.contains(card.getDate())) {
                amount.add(card.getHours() * payRate);
            }
        }
        payDispatcher.pay(this, date, amount);
    }
}
```

```java
// Wrap Class: Decorator 패턴 적용
public class LoggingEmployee extends Employee {
    private Employee wrapped;

    public LoggingEmployee(Employee employee) {
        this.wrapped = employee;
    }

    public void pay() {
        logPayment();
        wrapped.pay();
    }

    private void logPayment() {
        logFile.writeEntry(wrapped.getName(), date);
    }
}
```

또는 인터페이스를 활용한 형태:

```java
public interface Payable {
    void pay();
}

public class LoggingPayable implements Payable {
    private Payable wrapped;

    public LoggingPayable(Payable wrapped) {
        this.wrapped = wrapped;
    }

    public void pay() {
        logPayment();
        wrapped.pay();
    }

    private void logPayment() {
        // 로깅 로직
    }
}
```

호출 측 코드:

```java
// 변경 전
employee.pay();

// 변경 후
LoggingEmployee loggingEmployee = new LoggingEmployee(employee);
loggingEmployee.pay();
```

### 5.3 Wrap Class를 사용하는 경우

1. 추가하려는 동작이 **완전히 독립적**이고, 기존 클래스의 책임과 **별개의 관심사**일 때
2. 기존 클래스가 **이미 너무 비대**해서, 더 이상 책임을 추가하고 싶지 않을 때
3. 동일한 종류의 추가 동작(로깅, 감사, 트랜잭션 관리 등)을 **여러 클래스에 일관되게 적용**해야 할 때
4. 기존 클래스를 수정할 수 없거나, 수정이 너무 위험할 때

### 5.4 장점과 단점

**장점:**
- **기존 클래스를 전혀 수정하지 않는다**.
- 관심사의 분리(Separation of Concerns)가 명확하다.
- 새 동작을 **쉽게 테스트**할 수 있다.
- 동일한 래핑 패턴을 **재사용**할 수 있다.
- 필요에 따라 래핑을 **추가하거나 제거**할 수 있다 (유연성).

**단점:**
- **클래스 수가 증가**한다.
- 래핑이 중첩되면 **코드 추적이 어려워질 수 있다**.
- 호출 측 코드에서 **객체 생성 방식을 변경**해야 한다.

---

## 6. 네 가지 기법의 비교와 선택 기준

| 기법 | 적용 단위 | 기존 코드 수정 | 새 코드 테스트 | 적합한 상황 |
|------|-----------|---------------|---------------|-------------|
| **Sprout Method** | 메서드 | 호출문 1줄 추가 | 가능 | 기존 메서드에 새 기능 삽입 |
| **Sprout Class** | 클래스 | 호출문 1줄 추가 | 가능 | 기존 클래스를 테스트 하네스에 넣기 어려울 때 |
| **Wrap Method** | 메서드 | 이름 변경 | 가능 | 기존 동작 전/후에 새 동작 추가 |
| **Wrap Class** | 클래스 | 없음 | 가능 | 독립적인 관심사 추가, Decorator 패턴 |

### 6.1 선택 가이드

```
새 기능을 추가해야 한다
├── 기존 메서드 안에 끼워넣어야 하는가?
│   ├── YES → 기존 클래스를 테스트 하네스에 넣을 수 있는가?
│   │         ├── YES → Sprout Method
│   │         └── NO  → Sprout Class
│   └── NO  → 기존 동작의 전/후에 실행되어야 하는가?
│             ├── YES → 클래스 수준의 분리가 필요한가?
│             │         ├── YES → Wrap Class
│             │         └── NO  → Wrap Method
│             └── NO  → Sprout Method (또는 Sprout Class)
```

---

## 7. "나중에 정리하겠다"는 거짓말

Feathers는 이 장을 통해 반복적으로 강조하는 메시지가 있다:

> 테스트 없이 코드를 변경하고 "나중에 테스트를 추가하겠다"고 말하는 것은 자기기만이다. 나중에 돌아와 테스트를 추가하는 일은 거의 일어나지 않는다.

이 네 가지 기법은 **"지금 당장 완벽하게 할 수는 없지만, 최소한 새 코드만큼은 테스트하겠다"** 는 실용적인 타협이다. 중요한 것은 **전체 시스템을 한 번에 개선하려는 것이 아니라, 변경할 때마다 조금씩 더 나은 상태로 만드는 것**이다.

### 7.1 점진적 개선의 철학

```
변경 요청 → 테스트 없이 기존 코드에 밀어넣기 (X)
변경 요청 → Sprout/Wrap으로 새 코드를 테스트와 함께 작성 (O)
```

매번 이런 선택을 하면, 시간이 지남에 따라:
- **테스트가 있는 코드의 비율이 점진적으로 증가**한다.
- 새로 작성된 부분은 **안전하게 변경 가능한 상태**로 남는다.
- 기존 코드도 점차 테스트 하네스에 넣을 기회가 생긴다.

---

## 요약

- **시간이 부족하다는 이유로 테스트 없이 코드를 변경하면, 장기적으로 더 큰 비용을 치른다.**
- **Sprout Method**: 새 기능을 별도 메서드로 추출하고 테스트를 작성한 후, 기존 메서드에서 호출한다.
- **Sprout Class**: 기존 클래스를 테스트 하네스에 넣기 어려울 때, 새 기능을 완전히 새로운 클래스로 작성한다.
- **Wrap Method**: 기존 메서드의 이름을 바꾸고, 원래 이름의 메서드에서 기존 동작과 새 동작을 순서대로 호출한다.
- **Wrap Class**: Decorator 패턴으로 기존 클래스를 감싸서 새 동작을 추가한다.
- 네 기법 모두 **기존 코드의 변경을 최소화하면서 새 코드를 테스트 가능하게 만드는** 것이 목표이다.
- 완벽하지 않더라도, **매 변경마다 조금씩 나아지는 것**이 핵심 철학이다.

---

## 다음 챕터와의 연결

Chapter 7 **"코드 하나 바꾸는 데 왜 이리 오래 걸리지? (It Takes Forever to Make a Change)"** 에서는 코드 이해에 시간이 오래 걸리고, 빌드 시간이 길고, 의존성이 복잡하게 얽혀 있을 때 어떻게 해결할 수 있는지, 특히 **의존성 구조를 개선하여 빌드 시간과 변경 비용을 줄이는 방법**을 소개한다.
