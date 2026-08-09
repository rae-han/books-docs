# Chapter 16: 변경이 가능할 만큼 코드를 이해하지 못하는 경우 (I Don't Understand the Code Well Enough to Change It)

## 핵심 질문

레거시 코드를 충분히 이해하지 못한 상태에서 변경해야 할 때, 코드의 구조와 의도를 효과적으로 파악하기 위한 실용적 기법들은 무엇인가?

---

## 1. 코드 이해의 어려움

레거시 코드를 다룰 때 가장 흔하게 마주치는 상황 중 하나는, 코드를 충분히 이해하지 못한 상태에서 변경을 해야 하는 것이다. 코드가 무엇을 하는지, 왜 그렇게 작성되었는지, 변경하면 어떤 영향이 있는지 파악하기 어렵다.

### 1.1 코드를 이해하기 어려운 이유

| 원인 | 설명 |
|------|------|
| **문서 부재** | 설계 문서가 없거나, 있더라도 코드와 동기화되지 않음 |
| **원작자 부재** | 코드를 작성한 사람이 팀을 떠났거나, 기억하지 못함 |
| **복잡한 의존성** | 클래스 간, 모듈 간 의존 관계가 복잡하게 얽혀 있음 |
| **일관성 부재** | 여러 사람이 서로 다른 스타일로 코드를 작성하여 패턴이 일관되지 않음 |
| **암묵적 지식** | 코드에 표현되지 않은 도메인 지식이나 비즈니스 규칙이 있음 |
| **코드의 양** | 수만~수십만 줄의 코드에서 관련 부분을 찾는 것 자체가 어려움 |

이런 상황에서 코드를 이해하기 위해 무작정 코드를 읽는 것은 비효율적이다. Feathers는 코드를 체계적으로 이해하기 위한 네 가지 실용적 기법을 제시한다.

---

## 2. 기법 1: Notes/Sketching (메모와 스케치)

### 2.1 개요

가장 기본적이면서도 강력한 기법이다. 코드를 읽으면서 **종이에 메모하고, 관계를 스케치**하는 것이다. 화면만 보면서 머릿속으로 이해하려 하지 말고, 반드시 물리적으로(또는 디지털 도구로) 기록하면서 읽어야 한다.

### 2.2 구체적 방법

**1) 클래스 간 관계를 스케치한다**

코드를 읽으면서 등장하는 클래스들의 관계를 다이어그램으로 그린다. 완벽한 UML일 필요는 없다. 중요한 것은 **관계를 시각화**하는 것이다.

```
[간단한 스케치 예시]

OrderProcessor
    │
    ├──→ PaymentService
    │        │
    │        └──→ CreditCardGateway
    │
    ├──→ InventoryManager
    │        │
    │        └──→ WarehouseDB
    │
    └──→ NotificationService
             │
             ├──→ EmailSender
             └──→ SMSSender
```

**2) 시퀀스를 따라간다**

특정 시나리오에서 코드가 어떤 순서로 실행되는지 추적하며 시퀀스를 기록한다.

```
[주문 처리 시퀀스 메모 예시]

1. OrderController.createOrder() 호출
2. → OrderValidator.validate() 로 주문 유효성 검사
3. → OrderProcessor.process() 호출
4.    → PaymentService.charge() 로 결제
5.    → InventoryManager.reserve() 로 재고 예약
6.    → OrderRepository.save() 로 주문 저장
7. → NotificationService.notify() 로 알림 발송
```

**3) 의문점을 기록한다**

코드를 읽으면서 이해가 되지 않는 부분, 의아한 부분을 즉시 기록해둔다:

- "이 null 체크는 왜 하는가?"
- "이 예외를 삼키는(swallow) 이유가 무엇인가?"
- "이 메서드 이름과 실제 동작이 일치하지 않는데?"
- "이 매직 넘버 42는 무엇을 의미하는가?"

### 2.3 왜 효과적인가

메모와 스케치가 효과적인 이유:

1. **작업 기억(Working Memory)의 한계를 보완한다**: 인간의 작업 기억은 한 번에 7(+-2)개의 항목만 유지할 수 있다. 복잡한 코드는 이 한계를 쉽게 초과한다. 종이에 기록하면 작업 기억의 부담을 줄일 수 있다.
2. **시각적 패턴 인식을 활용한다**: 관계를 다이어그램으로 그리면, 텍스트로 읽을 때 보이지 않던 패턴이나 구조가 눈에 들어온다.
3. **능동적 읽기를 강제한다**: 단순히 코드를 스크롤하는 것과 달리, 기록하면서 읽으면 각 줄의 의미를 적극적으로 해석하게 된다.

---

## 3. 기법 2: Listing Markup (리스팅 마크업)

### 3.1 개요

코드를 **인쇄하여 종이 위에서 펜으로 표시**하는 기법이다. 디지털 환경에서만 코드를 보는 것과 달리, 종이 위에서는 자유롭게 밑줄, 원, 화살표, 메모를 추가할 수 있다.

### 3.2 구체적 마크업 방법

Feathers는 다음과 같은 마크업을 제안한다:

**1) 책임 분리 표시**

하나의 메서드 안에서 서로 다른 책임을 수행하는 코드 블록을 **다른 색깔이나 기호로 구분**한다.

```java
public void processOrder(Order order) {
    // ─── [검증 책임] ───────────────────
    if (order.getItems().isEmpty()) {
        throw new InvalidOrderException("주문 항목이 비어 있습니다");
    }
    if (order.getTotal().isNegative()) {
        throw new InvalidOrderException("주문 금액이 잘못되었습니다");
    }

    // ─── [결제 책임] ───────────────────
    PaymentResult result = paymentService.charge(
        order.getCustomerId(), order.getTotal()
    );
    if (!result.isSuccess()) {
        throw new PaymentFailedException(result.getMessage());
    }

    // ─── [재고 책임] ───────────────────
    for (OrderItem item : order.getItems()) {
        inventoryManager.reserve(item.getProductId(), item.getQuantity());
    }

    // ─── [저장 책임] ───────────────────
    order.setStatus(OrderStatus.CONFIRMED);
    orderRepository.save(order);

    // ─── [알림 책임] ───────────────────
    notificationService.sendOrderConfirmation(order);
}
```

이렇게 표시하면, 하나의 메서드가 얼마나 많은 책임을 가지고 있는지 시각적으로 명확해진다. 각 책임은 잠재적으로 별도의 메서드나 클래스로 추출할 수 있는 후보다.

**2) 메서드 경계 표시**

긴 메서드에서 논리적으로 분리될 수 있는 구간을 선으로 나눈다. 이 구간들은 나중에 Extract Method를 적용할 후보가 된다.

**3) 영향 범위 표시**

특정 변수가 사용되는 범위, 특정 조건문이 영향을 미치는 범위를 괄호나 화살표로 표시한다.

```java
public void processData(List<Record> records) {
    int total = 0;                      // ┐
    int validCount = 0;                 // │ total, validCount의
    for (Record r : records) {          // │ 사용 범위
        if (r.isValid()) {              // │
            total += r.getValue();      // │
            validCount++;               // │
        }                               // │
    }                                   // ┘

    double average = 0;                 // ┐
    if (validCount > 0) {               // │ average의
        average = (double) total        // │ 사용 범위
                    / validCount;       // │
    }                                   // ┘

    report.setSummary(total, average);  // total, average만 필요
}
```

### 3.3 마크업의 가치

리스팅 마크업은 다음과 같은 통찰을 제공한다:

- **메서드가 너무 많은 책임을 가지고 있는가?** 다른 색으로 표시된 영역이 많으면 그렇다.
- **어디에서 코드를 분리할 수 있는가?** 책임 경계가 자연스러운 분리 지점이 된다.
- **변수의 수명이 적절한가?** 변수가 메서드 전체에 걸쳐 사용되면 추출 시 파라미터가 많아질 수 있다.

---

## 4. 기법 3: Scratch Refactoring (임시 리팩토링)

### 4.1 개요

**Scratch Refactoring**은 코드를 이해하기 위한 목적으로 **임시로 리팩토링을 수행**하는 기법이다. 핵심 전제는 **변경 내용을 절대 저장하지 않는다**는 것이다. 모든 변경은 버릴 것을 전제로 한다.

> **Scratch Refactoring의 목적은 코드를 개선하는 것이 아니라, 코드를 이해하는 것이다.**

### 4.2 수행 방법

1. **버전 관리에서 현재 상태를 확인**한다 (깨끗한 상태인지 확인).
2. 코드를 **자유롭게 리팩토링**한다:
   - 메서드 이름을 자신이 이해한 의미로 변경한다
   - 긴 메서드를 작은 메서드로 분리한다
   - 변수 이름을 더 의미 있는 이름으로 바꾼다
   - 조건문을 정리한다
   - 중복을 제거한다
3. 리팩토링 과정에서 코드에 대한 이해가 깊어진다.
4. 충분히 이해했다고 느끼면, **모든 변경을 버린다** (`git checkout .` 또는 `git stash drop`).

### 4.3 구체적 예시

```java
// [원본 코드 - 이해하기 어려움]
public void proc(int op, String data, int flags) {
    if (op == 1) {
        if ((flags & 0x02) != 0) {
            String[] parts = data.split("\\|");
            if (parts.length > 2) {
                db.execute("INSERT INTO tbl_a VALUES(?,?,?)",
                    parts[0], parts[1], parts[2]);
            }
        } else {
            db.execute("INSERT INTO tbl_a VALUES(?)", data);
        }
    } else if (op == 2) {
        db.execute("DELETE FROM tbl_a WHERE col1 = ?", data);
    }
}
```

```java
// [Scratch Refactoring 후 - 이해를 위한 임시 코드]
public void processRecord(int operation, String data, int flags) {
    if (operation == OPERATION_INSERT) {
        if (hasMultipleFieldsFlag(flags)) {
            insertMultipleFields(data);
        } else {
            insertSingleField(data);
        }
    } else if (operation == OPERATION_DELETE) {
        deleteRecord(data);
    }
}

private static final int OPERATION_INSERT = 1;
private static final int OPERATION_DELETE = 2;
private static final int FLAG_MULTIPLE_FIELDS = 0x02;

private boolean hasMultipleFieldsFlag(int flags) {
    return (flags & FLAG_MULTIPLE_FIELDS) != 0;
}

private void insertMultipleFields(String data) {
    String[] fields = data.split("\\|");
    if (fields.length > 2) {
        db.execute("INSERT INTO tbl_a VALUES(?,?,?)",
            fields[0], fields[1], fields[2]);
    }
}

private void insertSingleField(String data) {
    db.execute("INSERT INTO tbl_a VALUES(?)", data);
}

private void deleteRecord(String data) {
    db.execute("DELETE FROM tbl_a WHERE col1 = ?", data);
}
```

리팩토링 과정에서 다음을 이해하게 된다:
- `op`은 삽입/삭제를 구분하는 연산 코드였다
- `flags`의 비트 2는 데이터에 여러 필드가 파이프(`|`)로 구분되어 있음을 나타낸다
- `tbl_a`에 대한 CRUD 중 삽입과 삭제를 처리하는 코드였다

### 4.4 Scratch Refactoring의 핵심 규칙

| 규칙 | 설명 |
|------|------|
| **반드시 버린다** | 이 리팩토링의 목적은 이해이지 개선이 아니다. 변경을 저장하면 테스트 없이 수행한 리팩토링이 프로덕션에 반영되는 위험이 있다 |
| **테스트 없이 해도 된다** | 일반적인 리팩토링과 달리, 목적이 변경이 아닌 이해이므로 테스트가 없어도 괜찮다 |
| **과감하게 한다** | 평소라면 하지 않을 큰 변경도 과감하게 시도한다. 어차피 버릴 것이므로 부담이 없다 |
| **이해에 집중한다** | 코드를 "올바르게" 리팩토링하려고 하지 말고, 자신이 이해하기 쉬운 형태로 바꾸는 데 집중한다 |

### 4.5 Scratch Refactoring의 심리적 효과

이 기법의 강력한 점은 **심리적 부담을 제거**한다는 것이다:

- "잘못 바꾸면 어쩌지?" → 어차피 버릴 것이므로 상관없다
- "테스트가 없는데 리팩토링해도 되나?" → 프로덕션에 반영하지 않으므로 괜찮다
- "이 구조가 올바른 건지 모르겠다" → 정답을 찾는 것이 아니라 이해하는 것이 목적이다

코드를 마음대로 바꿔볼 수 있다는 자유로움이, 코드에 대한 이해를 극적으로 높여준다.

---

## 5. 기법 4: Delete Unused Code (미사용 코드 삭제)

### 5.1 개요

레거시 코드베이스에는 **더 이상 사용되지 않는 코드**가 상당량 존재하는 경우가 많다. 한때는 필요했지만 지금은 호출되지 않는 메서드, 주석 처리된 코드 블록, 사용되지 않는 클래스 등이 코드의 이해를 방해한다.

### 5.2 미사용 코드가 이해를 방해하는 이유

```java
public class OrderService {

    // 현재 사용되는 메서드
    public Order createOrder(Customer customer, List<Item> items) {
        // ...
    }

    // 사용되지 않는 메서드 (하지만 읽는 사람은 이것을 모른다)
    public Order createBulkOrder(Customer customer, List<Item> items,
                                  int discount) {
        // 50줄의 복잡한 로직...
    }

    // 주석 처리된 코드 (왜 주석 처리했는지 알 수 없다)
    // public void applyDiscount(Order order, DiscountPolicy policy) {
    //     if (policy.isApplicable(order)) {
    //         order.setDiscount(policy.calculate(order));
    //     }
    // }

    // 또 다른 사용되지 않는 메서드
    public void reprocessFailedOrders() {
        // 30줄의 로직...
    }

    public void cancelOrder(Order order) {
        // ...
    }
}
```

코드를 읽는 사람은 어떤 메서드가 실제로 사용되는지, 어떤 메서드가 죽은 코드인지 즉시 알 수 없다. 미사용 코드를 이해하는 데 시간과 에너지를 낭비하게 된다.

### 5.3 과감히 삭제하라

> **버전 관리 시스템이 있으니, 삭제된 코드는 언제든 복원할 수 있다. 과감히 삭제하라.**

주석 처리한 채로 남겨두는 것은 좋은 방법이 아니다. 주석 처리된 코드는:
- 왜 주석 처리되었는지 알 수 없다 (버그 때문인가? 임시인가? 더 이상 필요 없는 건가?)
- 코드의 양을 늘려 읽기 어렵게 만든다
- 시간이 지나면 주변 코드와 호환되지 않게 되어 복원해도 동작하지 않을 가능성이 높다

삭제의 원칙:

| 대상 | 판단 기준 | 조치 |
|------|----------|------|
| 호출되지 않는 메서드 | IDE의 "Find Usages"로 확인 | 삭제 |
| 주석 처리된 코드 | 버전 관리에 이력이 있음 | 삭제 |
| 도달 불가능한 코드 | 조건에 의해 절대 실행되지 않는 코드 | 삭제 |
| 사용되지 않는 import/include | 정적 분석 도구로 확인 | 삭제 |
| 사용되지 않는 변수 | 컴파일러 경고로 확인 | 삭제 |

---

## 6. 코드 이해와 변경의 관계

### 6.1 이해의 깊이와 변경의 안전성

네 가지 기법은 각각 다른 수준의 이해를 제공한다:

| 기법 | 이해의 수준 | 소요 시간 |
|------|-----------|----------|
| **Notes/Sketching** | 전체 구조와 흐름 파악 | 짧음 (수십 분) |
| **Listing Markup** | 메서드 수준의 책임과 구조 파악 | 중간 (수 시간) |
| **Scratch Refactoring** | 코드의 세부 동작과 의도 파악 | 김 (수 시간~하루) |
| **Delete Unused Code** | 실제로 중요한 코드 식별 | 짧음 (수십 분) |

### 6.2 기법의 조합

이 기법들은 상호 배타적이 아니다. 상황에 따라 조합하여 사용하면 효과적이다:

```
[권장 순서]

1. Delete Unused Code: 노이즈를 먼저 제거
   ↓
2. Notes/Sketching: 전체 구조 파악
   ↓
3. Listing Markup: 관심 영역의 세부 구조 파악
   ↓
4. Scratch Refactoring: 핵심 코드의 동작과 의도 파악
```

### 6.3 이해 없이 변경하면 안 되는가?

현실에서는 코드를 완전히 이해하기 전에 변경해야 하는 압박을 받는 경우가 많다. 하지만 이해 없이 변경하면:

- 의도하지 않은 동작 변경을 일으킬 확률이 높아진다
- 변경의 영향 범위를 파악하지 못하여 다른 곳이 깨질 수 있다
- 이미 복잡한 코드를 더 복잡하게 만들 수 있다

코드를 이해하는 데 시간을 투자하는 것은 **낭비가 아니라 투자**다. 이해에 투자한 시간은 변경의 정확성과 안전성으로 돌아온다.

---

## 요약

- 레거시 코드를 이해하기 위한 네 가지 실용적 기법이 있다:
  1. **Notes/Sketching**: 코드를 읽으면서 메모하고, 클래스 관계와 실행 흐름을 스케치한다.
  2. **Listing Markup**: 코드를 인쇄하여 책임 분리, 메서드 경계, 변수 범위 등을 시각적으로 표시한다.
  3. **Scratch Refactoring**: 코드를 이해하기 위해 임시로 리팩토링한다. **변경 내용은 반드시 버린다.**
  4. **Delete Unused Code**: 사용되지 않는 코드를 과감히 삭제하여 이해해야 할 코드의 양을 줄인다.
- Scratch Refactoring은 **테스트 없이도 수행 가능**하다. 목적이 이해이지 변경이 아니기 때문이다.
- 미사용 코드의 삭제는 **버전 관리 시스템이 있으므로** 안전하다. 주석 처리 대신 삭제하라.
- 코드를 이해하는 데 투자하는 시간은 **안전한 변경을 위한 필수 투자**다.
- 네 가지 기법은 조합하여 사용할 때 가장 효과적이다.

---

## 다음 챕터와의 연결

Chapter 17 "내 애플리케이션은 뼈대가 약하다 (My Application Has No Structure)"에서는 개별 코드 수준이 아닌 **아키텍처 수준에서 구조가 없는 애플리케이션**의 문제를 다룬다. 시스템의 전체적 구조를 파악하기 위한 기법들 — Telling the Story, CRC Cards, Naked CRC, Conversation Scrutiny — 을 통해 시스템 수준의 이해를 높이는 방법을 살펴본다.
