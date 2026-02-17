# Chapter 12: 클래스 의존 관계, 반드시 없애야 할까? (I Need to Make Many Changes in One Area)

## 핵심 질문

한 영역에서 여러 변경이 필요할 때, 관련된 모든 클래스의 의존성을 깨뜨려야 하는가? 아니면 더 효율적인 방법이 있는가?

---

## 1. 문제 상황: 여러 변경, 여러 클래스

레거시 코드에서 하나의 기능을 변경하거나 추가하려면, 한 클래스만 수정하는 경우는 드물다. 보통 여러 클래스에 걸쳐 변경이 필요하다. 이때 직면하는 현실적 문제:

- 변경에 관련된 클래스가 5~10개 이상일 수 있다
- 각 클래스마다 의존성을 깨뜨리고 테스트를 작성하려면 며칠이 걸릴 수 있다
- 그렇다고 테스트 없이 변경하면 위험하다

> 이 장의 핵심 메시지: **모든 클래스에 개별 테스트를 작성할 필요는 없다.** 영향이 모이는 상위 지점을 찾으면, 적은 노력으로 충분한 안전망을 확보할 수 있다.

### 1.1 구체적 시나리오

다음과 같은 결제 시스템을 상상해보자:

```java
public class PaymentProcessor {
    private AccountValidator validator;
    private FeeCalculator feeCalculator;
    private TransactionLogger logger;
    private NotificationService notifier;

    public Receipt processPayment(PaymentRequest request) {
        Account account = validator.validate(request.getAccountId());
        double fee = feeCalculator.calculate(request.getAmount(), account.getType());
        double totalAmount = request.getAmount() + fee;

        Transaction tx = new Transaction(account, totalAmount);
        logger.log(tx);
        notifier.notifyCustomer(account, tx);

        return new Receipt(tx, fee);
    }
}
```

여기서 수수료 계산 방식을 변경해야 하고, 이에 따라 `FeeCalculator`, `Transaction`, `Receipt`, `NotificationService`의 메시지 포맷, 그리고 `TransactionLogger`의 로그 형식까지 여러 곳을 수정해야 한다고 하자.

각 클래스(`AccountValidator`, `FeeCalculator`, `TransactionLogger`, `NotificationService`)마다 의존성을 깨뜨리고 독립적으로 테스트를 작성하는 것은 상당한 노력이 필요하다. 더 효율적인 방법이 있을까?

---

## 2. Interception Point (차단 지점) 찾기

### 2.1 상위 수준에서 영향을 차단

모든 하위 클래스에 개별 테스트를 작성하는 대신, **변경 영향이 모이는 상위 지점**을 찾아 그곳에서 테스트를 작성하는 것이 핵심 전략이다.

위 예시에서 영향 스케치를 그려보면:

```
FeeCalculator.calculate() 변경
  │
  ├──→ totalAmount 값 변경
  │      │
  │      ├──→ Transaction 생성에 영향
  │      │       │
  │      │       ├──→ logger.log(tx) 영향
  │      │       └──→ notifier.notifyCustomer() 영향
  │      │
  │      └──→ Receipt 생성에 영향
  │
  └──→ fee 값 변경
         │
         └──→ Receipt 생성에 영향

모든 영향이 모이는 곳: processPayment()의 반환값인 Receipt
```

`Receipt` 객체에 필요한 정보가 모두 담겨 있다면, `processPayment()`의 반환값을 검증하는 것만으로도 수수료 계산 변경의 영향을 상당 부분 감지할 수 있다.

### 2.2 상위 수준 Interception Point의 장점

```java
// 상위 수준에서 차단하는 테스트
@Test
public void testProcessPaymentWithNewFeeStructure() {
    // 필요한 최소한의 의존성만 설정
    PaymentProcessor processor = createProcessorWithFakes();
    PaymentRequest request = new PaymentRequest("ACC-001", 100.0);

    Receipt receipt = processor.processPayment(request);

    // 상위 수준에서 결과를 검증
    assertEquals(100.0, receipt.getBaseAmount(), 0.01);
    assertEquals(2.5, receipt.getFee(), 0.01);  // 새로운 수수료 구조
    assertEquals(102.5, receipt.getTotalAmount(), 0.01);
}
```

이 방식의 장점:

| 장점 | 설명 |
|------|------|
| **적은 테스트 수** | 모든 하위 클래스에 개별 테스트를 작성하지 않아도 됨 |
| **적은 의존성 해제** | 상위 수준에서만 의존성을 대체하면 됨 |
| **빠른 안전망 확보** | 변경을 시작하기 전에 빠르게 보호망을 구축할 수 있음 |
| **통합적 검증** | 여러 클래스 간의 상호작용도 함께 검증됨 |

---

## 3. Pinch Point (병목 지점) 활용

### 3.1 Pinch Point란?

Chapter 11에서 소개된 Pinch Point를 이 장에서 더 깊이 다룬다. **Pinch Point**는 여러 변경의 영향이 **자연스럽게 하나로 모이는 좁은 지점**이다. 이 지점은 시스템의 구조에 의해 자연스럽게 형성되며, 의도적으로 만드는 것이 아니라 **발견하는** 것이다.

```
ClassA의 변경 ──→ methodA1 ──→ methodA2 ──┐
                                            │
ClassB의 변경 ──→ methodB1 ────────────────┼──→ PinchPoint ──→ ...
                                            │
ClassC의 변경 ──→ methodC1 ──→ methodC2 ──┘
```

### 3.2 Pinch Point 찾는 방법

**Step 1: 영향 스케치를 그린다**

각 변경 지점에서 시작하여 영향이 전파되는 경로를 추적한다.

**Step 2: 영향 경로들이 합류하는 지점을 찾는다**

여러 영향 경로가 하나의 메서드나 객체를 통과하는 곳이 Pinch Point 후보다.

**Step 3: 테스트 가능성을 확인한다**

해당 지점에서 결과를 검증할 수 있는지 (반환값, 객체 상태 등) 확인한다.

### 3.3 Pinch Point 활용 예시

```java
public class InventorySystem {
    private Warehouse warehouse;
    private SupplierManager supplierManager;
    private PricingEngine pricingEngine;

    // 여러 변경이 필요한 영역
    // 변경 1: warehouse의 재고 계산 로직
    // 변경 2: supplierManager의 공급 시간 계산
    // 변경 3: pricingEngine의 할인 로직

    // Pinch Point: 세 변경의 영향이 모두 이 메서드를 통과함
    public OrderFulfillment planFulfillment(Order order) {
        int stock = warehouse.getAvailableStock(order.getProductId());
        int supplyDays = supplierManager.getSupplyTime(order.getProductId());
        double price = pricingEngine.calculatePrice(
            order.getProductId(), order.getQuantity());

        return new OrderFulfillment(
            order, stock, supplyDays, price,
            stock >= order.getQuantity(),
            estimateDeliveryDate(stock, supplyDays, order.getQuantity())
        );
    }
}
```

`planFulfillment()`이 Pinch Point다. 세 가지 변경의 영향이 모두 이 메서드를 통과하므로, 이 메서드의 반환값(`OrderFulfillment`)을 검증하면 세 변경 모두의 영향을 감지할 수 있다:

```java
@Test
public void testPlanFulfillmentReflectsAllChanges() {
    // fake 의존성으로 InventorySystem 구성
    FakeWarehouse warehouse = new FakeWarehouse();
    warehouse.setStock("PROD-001", 50);

    FakeSupplierManager supplier = new FakeSupplierManager();
    supplier.setSupplyTime("PROD-001", 3);

    FakePricingEngine pricing = new FakePricingEngine();
    pricing.setPrice("PROD-001", 10, 29.99);  // 10개일 때 29.99

    InventorySystem system = new InventorySystem(warehouse, supplier, pricing);
    Order order = new Order("PROD-001", 10);

    OrderFulfillment result = system.planFulfillment(order);

    // Pinch Point에서 모든 영향을 한 번에 검증
    assertTrue(result.isInStock());
    assertEquals(29.99, result.getPrice(), 0.01);
    assertNotNull(result.getEstimatedDeliveryDate());
}
```

### 3.4 Higher-level 테스트의 활용

Pinch Point에서의 테스트는 자연스럽게 **더 높은 수준(higher-level)의 테스트**가 된다. 개별 클래스의 단위 테스트가 아니라, 여러 클래스의 협력을 검증하는 테스트다.

이런 higher-level 테스트의 특성:

```
단위 테스트 (Unit Test)
├── 개별 클래스의 개별 메서드를 독립적으로 테스트
├── 빠르고 정확한 실패 진단 가능
└── 작성에 시간이 많이 걸릴 수 있음 (의존성 해제 필요)

Pinch Point 테스트 (Higher-level Test)
├── 여러 클래스의 협력 결과를 검증
├── 적은 수의 테스트로 넓은 범위 커버
├── 실패 시 정확한 원인 파악이 어려울 수 있음
└── 빠르게 안전망을 구축할 수 있음
```

> Pinch Point 테스트는 완벽한 단위 테스트를 대체하는 것이 아니라, **변경을 시작하기 위한 출발점**이다. 이 안전망 아래에서 변경을 수행하고, 시간이 허락하면 점진적으로 더 세밀한 단위 테스트를 추가한다.

---

## 4. Pinch Point Trap (병목 지점의 함정)

### 4.1 통합 테스트로의 전락

Pinch Point 테스트에 너무 의존하면 위험한 함정에 빠질 수 있다. Pinch Point 테스트가 점점 많아지면, 결국 **통합 테스트(integration test)** 가 되어버린다.

통합 테스트의 문제점:

| 문제 | 설명 |
|------|------|
| **느린 실행 속도** | 여러 클래스를 함께 실행하므로 단위 테스트보다 느림 |
| **불명확한 실패 원인** | 테스트가 실패했을 때 어떤 클래스의 어떤 변경이 원인인지 파악하기 어려움 |
| **깨지기 쉬움** | 관련된 클래스 중 하나만 변경되어도 테스트가 깨질 수 있음 |
| **유지보수 부담** | 시스템 변경에 따라 테스트도 자주 수정해야 함 |

### 4.2 함정에 빠지는 과정

```
1단계: "모든 클래스에 단위 테스트를 쓸 시간이 없으니, Pinch Point에서 테스트하자"
  → 합리적인 판단

2단계: "Pinch Point 테스트가 잘 동작하니, 새로운 변경도 여기서 테스트하자"
  → 편리하지만 주의 필요

3단계: "이제 Pinch Point 테스트가 50개가 되었고, 실행에 30초 걸린다"
  → 문제 시작

4단계: "테스트가 자주 깨지고, 실패 원인을 찾기 어렵다"
  → Pinch Point Trap에 빠진 상태
```

### 4.3 함정 회피 전략

Pinch Point 테스트는 **임시 안전망**으로 사용하고, 점진적으로 단위 테스트로 전환해야 한다:

1. **Pinch Point 테스트를 먼저 작성**하여 안전망을 확보한다
2. **변경을 수행**한다
3. **변경한 코드에 대해 단위 테스트를 작성**한다
4. 단위 테스트가 충분히 갖춰지면, **불필요해진 Pinch Point 테스트를 제거**하거나 축소한다

> Pinch Point 테스트를 "발판(scaffolding)"으로 생각하라. 건물을 지을 때 발판이 필요하지만, 건물이 완성되면 발판은 제거한다. Pinch Point 테스트도 마찬가지다.

---

## 5. 점진적 의존성 해제 전략

### 5.1 전체 전략: 바깥에서 안으로

한 영역에서 여러 변경이 필요할 때의 권장 접근법:

```
Step 1: 영향 스케치를 그려 Pinch Point를 찾는다
         ↓
Step 2: Pinch Point에서 higher-level 테스트를 작성한다
         ↓
Step 3: higher-level 테스트의 보호 아래 변경을 수행한다
         ↓
Step 4: 변경한 개별 클래스에 대해 단위 테스트를 작성한다
         ↓
Step 5: 단위 테스트가 충분하면 higher-level 테스트를 축소한다
```

### 5.2 의존성 해제의 우선순위

모든 의존성을 한 번에 해제할 필요는 없다. 우선순위를 정하자:

1. **Pinch Point에서의 테스트를 가능하게 하는 의존성**을 먼저 해제한다 (예: 데이터베이스 연결, 네트워크 호출)
2. **변경 대상 클래스의 의존성**을 다음으로 해제한다
3. 나머지는 **필요할 때** 해제한다

```java
// 예: Pinch Point 테스트를 위해 최소한의 의존성만 해제
public class InventorySystem {
    // 데이터베이스 의존성만 fake로 교체 (테스트 실행을 위해 필수)
    // 나머지는 실제 객체 사용 가능
    public InventorySystem(WarehouseRepository repo,
                           SupplierManager supplier,  // 실제 객체 가능
                           PricingEngine pricing) {    // 실제 객체 가능
        // ...
    }
}
```

---

## 6. 실용적 조언: 완벽하지 않아도 충분한 커버리지

### 6.1 "Good Enough" 원칙

Feathers는 레거시 코드에서 **완벽한 테스트 커버리지를 추구하지 말라**고 조언한다:

- 100%의 커버리지보다, **변경 영역에 대한 적절한 커버리지**가 중요하다
- Higher-level 테스트가 개별 단위 테스트만큼 정밀하지 않더라도, **테스트가 없는 것보다 훨씬 낫다**
- 시간이 제한되어 있을 때는 **Pinch Point 테스트로 시작**하는 것이 현명하다

### 6.2 실무에서의 판단 기준

| 상황 | 권장 접근법 |
|------|------------|
| 시간이 충분 | 개별 클래스 단위 테스트 작성 후 변경 |
| 시간이 부족 | Pinch Point 테스트 → 변경 → 나중에 단위 테스트 추가 |
| 매우 급한 변경 | Pinch Point 테스트만이라도 작성 후 변경 |
| 한 번만 하는 작은 변경 | Pinch Point 테스트로 충분할 수 있음 |
| 자주 변경되는 영역 | 점진적으로 단위 테스트를 충실히 갖추어야 함 |

### 6.3 팀 차원의 점진적 개선

한 영역에서 작업할 때마다 조금씩 테스트를 추가하면, 시간이 지남에 따라 레거시 코드의 테스트 커버리지가 점점 높아진다:

```
1차 작업: Pinch Point 테스트 3개 작성
  ↓
2차 작업: 기존 Pinch Point 테스트 유지 + ClassA 단위 테스트 5개 추가
  ↓
3차 작업: ClassB, ClassC 단위 테스트 추가 + 불필요한 Pinch Point 테스트 제거
  ↓
시간이 지남에 따라 충실한 단위 테스트 기반 확보
```

---

## 요약

- 한 영역에서 여러 변경이 필요할 때, **모든 클래스에 개별 테스트를 작성할 필요는 없다**.
- **Interception Point(차단 지점)** 를 찾아 변경 영향이 모이는 상위 지점에서 테스트하면, 적은 노력으로 안전망을 확보할 수 있다.
- **Pinch Point(병목 지점)** 는 여러 영향이 자연스럽게 모이는 좁은 지점으로, 가장 효율적인 테스트 위치다.
- 단, **Pinch Point Trap**에 주의해야 한다. Pinch Point 테스트에 너무 의존하면 느리고 깨지기 쉬운 통합 테스트가 되어버린다.
- Pinch Point 테스트는 **임시 발판(scaffolding)** 으로 사용하고, 점진적으로 단위 테스트로 전환해야 한다.
- **완벽하지 않아도 충분한 커버리지**를 확보하는 실용적 접근이 중요하며, 작업할 때마다 조금씩 테스트를 추가하는 점진적 개선 전략을 따른다.

---

## 다음 챕터와의 연결

Chapter 13 "변경해야 하는데, 어떤 테스트를 작성해야 할지 모르겠다 (I Need to Make a Change, but I Don't Know What Tests to Write)"에서는 **Characterization Test(특성 테스트)** 를 본격적으로 다룬다. 코드의 현재 동작을 그대로 기록하는 테스트를 작성하는 구체적인 절차와, 어디까지 테스트를 작성할 것인지에 대한 heuristic을 제공한다.
