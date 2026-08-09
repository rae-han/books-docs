# Chapter 5: Mocks and Test Fragility (목과 테스트 취약성)

## 핵심 질문

Mock은 언제 사용해야 하고 언제 피해야 하는가? Mock의 남용이 테스트를 취약하게 만드는 근본적인 이유는 무엇이며, **관찰 가능한 동작(observable behavior)**과 **구현 세부사항(implementation detail)**을 구분하는 원칙적인 방법은 무엇인가?

---

## 1. Mock과 Stub의 구분

### 1.1 테스트 더블의 유형

테스트 더블(*Test Double — 테스트에서 프로덕션 의존성을 대체하는 모든 가짜 객체의 총칭*)은 크게 두 범주로 나뉜다:

```
테스트 더블 (Test Double)
├── Mock 계열 — 나가는 상호작용(outgoing interaction) 검증
│   ├── Mock: 프레임워크로 생성, 행위 검증
│   └── Spy: 수동으로 작성, 행위 검증
│
└── Stub 계열 — 들어오는 상호작용(incoming interaction)에 응답 제공
    ├── Stub: 미리 준비된 응답 반환
    ├── Dummy: 전달만 되고 사용되지 않는 객체
    └── Fake: 실제 구현의 경량 버전 (예: 인메모리 DB)
```

### 1.2 핵심 차이: 검증 대상

| | Mock | Stub |
|---|---|---|
| **방향** | SUT → 외부 (나가는 호출) | 외부 → SUT (들어오는 데이터) |
| **검증** | 호출이 **이루어졌는지** 검증 | 검증하지 않음 — 값을 제공할 뿐 |
| **예시** | 이메일 발송 확인, 메시지 큐 발행 확인 | DB에서 데이터 조회, 설정 값 제공 |

```csharp
// Mock: 나가는 상호작용을 검증
var emailMock = new Mock<IEmailGateway>();
sut.PlaceOrder(order);
emailMock.Verify(x => x.SendReceipt(order.Email), Times.Once);   // ← 검증

// Stub: 들어오는 데이터를 제공
var dbStub = new Mock<IDatabase>();
dbStub.Setup(x => x.GetCustomer(42)).Returns(new Customer());    // ← 데이터 제공
sut.PlaceOrder(order);
// dbStub에 대해서는 Verify하지 않는다
```

> **핵심 통찰**: **Stub의 호출을 검증하지 말라(Don't verify stubs)**. 이것은 Khorikov가 반복적으로 강조하는 원칙이다. Stub은 SUT가 결과를 만들어내기 위한 입력을 제공할 뿐이다. Stub이 어떻게 호출되었는지를 검증하면 구현 세부사항에 결합되어 테스트가 취약해진다.

---

## 2. 관찰 가능한 동작 vs 구현 세부사항

### 2.1 정의

Mock을 언제 사용해야 하는지를 결정하려면, 먼저 **관찰 가능한 동작**과 **구현 세부사항**을 구분해야 한다:

| | 관찰 가능한 동작 | 구현 세부사항 |
|---|---|---|
| **정의** | 클라이언트가 목표를 달성하기 위해 사용하는 **공개 API** | 목표 달성의 **중간 과정** |
| **클라이언트에게** | 의미가 있다 | 알 필요가 없다 |
| **변경 시** | 클라이언트 코드도 변경해야 함 | 클라이언트 코드에 영향 없음 |
| **테스트에서** | 검증해야 함 | 검증하면 안 됨 |

### 2.2 잘 설계된 API vs 나쁘게 설계된 API

잘 설계된 코드는 **공개 API = 관찰 가능한 동작**이다. 나쁘게 설계된 코드는 구현 세부사항이 공개 API에 노출된다:

```csharp
// 나쁜 설계: 구현 세부사항이 공개 API에 노출
public class UserController
{
    public void ChangeName(int userId, string newName)
    {
        User user = _database.GetUser(userId);
        user.Name = newName;           // 프로퍼티 직접 노출
        user.NormalizeName();          // 정규화 메서드 공개 — 구현 세부사항!
        _database.SaveUser(user);
    }
}

public class User
{
    public string Name { get; set; }
    public void NormalizeName()        // 클라이언트가 호출해야 하는 이유가 없다
    {
        Name = Name.Trim().ToLower();
    }
}
```

```csharp
// 좋은 설계: 관찰 가능한 동작만 공개
public class User
{
    public string Name { get; private set; }

    public void ChangeName(string newName)   // 하나의 공개 메서드로 완전한 동작
    {
        Name = newName.Trim().ToLower();     // 정규화는 내부에서 처리
    }
}
```

좋은 설계에서는 `NormalizeName`이 내부로 숨겨진다. 테스트도 `ChangeName`의 **결과**(Name이 정규화되었는가?)만 검증하면 된다.

> **핵심 통찰**: 공개 API와 관찰 가능한 동작이 일치하도록 코드를 설계하면, 테스트도 자연스럽게 **구현 세부사항이 아닌 동작**을 검증하게 된다. 테스트 취약성의 근본 원인은 Mock 자체가 아니라, **잘못된 API 설계**에 있는 경우가 많다.

---

## 3. 육각형 아키텍처와 Mock

### 3.1 육각형 아키텍처(Hexagonal Architecture)

Khorikov는 Mock의 올바른 사용을 설명하기 위해 육각형 아키텍처를 도입한다:

```
         외부 세계
    ┌───────────────────┐
    │                   │
    │  ┌─────────────┐  │
    │  │             │  │
    │  │  도메인 모델  │  │
    │  │  (비즈니스   │  │
    │  │   로직)      │  │
    │  │             │  │
    │  └──────┬──────┘  │
    │         │         │
    │  애플리케이션 서비스  │
    │  (오케스트레이션)    │
    │         │         │
    └────┬────┴────┬────┘
         │         │
    ┌────┴───┐ ┌───┴────┐
    │  DB    │ │ 메시지  │
    │        │ │  버스   │
    └────────┘ └────────┘
      프로세스 외부 의존성
```

핵심 원칙:
- **도메인 모델**은 외부 세계를 모른다 — 프로세스 외부 의존성에 직접 접근하지 않는다
- **애플리케이션 서비스**가 도메인 모델과 외부 세계를 연결하는 오케스트레이터 역할을 한다
- 의존성 방향은 항상 **바깥 → 안쪽**이다

### 3.2 애플리케이션 내부 통신 vs 외부 통신

이 구분이 Mock 사용의 핵심이다:

| 통신 유형 | 예시 | Mock 사용 |
|----------|------|----------|
| **애플리케이션 내부 통신** | 도메인 모델 ↔ 도메인 모델, 서비스 → 도메인 | **Mock 하지 않는다** (구현 세부사항) |
| **애플리케이션 외부 통신** | 앱 → 메시지 버스, 앱 → SMTP 서버 | **Mock 한다** (관찰 가능한 동작) |

```csharp
// 내부 통신: Mock하면 안 됨
// Customer가 Store의 메서드를 호출하는 것은 내부 구현
var storeMock = new Mock<IStore>();           // ← 잘못된 Mock
sut.Purchase(storeMock.Object, product, 5);
storeMock.Verify(x => x.RemoveInventory(...)); // ← 구현 세부사항 검증

// 외부 통신: Mock 해야 함
// 앱이 메시지 버스에 이벤트를 발행하는 것은 외부에서 관찰 가능한 부수 효과
var busMock = new Mock<IMessageBus>();        // ← 올바른 Mock
sut.PlaceOrder(order);
busMock.Verify(x => x.Publish(It.IsAny<OrderPlaced>())); // ← 외부 통신 검증
```

> **핵심 통찰**: Mock은 **시스템 경계를 넘는 외부 통신**에만 사용하라. 시스템 내부의 클래스 간 통신을 Mock으로 검증하면, 그것은 구현 세부사항에 결합되어 리팩터링 내성이 떨어진다. 이것이 Chapter 2에서 London 학파의 문제점으로 지적한 것의 체계적인 설명이다.

---

## 4. 관리 의존성 vs 비관리 의존성

### 4.1 프로세스 외부 의존성의 분류

Mock을 더 세밀하게 적용하려면, 프로세스 외부 의존성을 다시 분류해야 한다:

| 유형 | 정의 | 예시 | Mock? |
|------|------|------|-------|
| **관리 의존성 (*Managed dependency*)** | 애플리케이션만 접근하는 외부 의존성. 외부 시스템이 직접 관찰하지 않는다 | 애플리케이션 전용 데이터베이스 | **Mock하지 않는다** |
| **비관리 의존성 (*Unmanaged dependency*)** | 외부 시스템이 관찰할 수 있는 의존성. 다른 애플리케이션도 접근한다 | 메시지 버스, SMTP 서버, 외부 API | **Mock 한다** |

### 4.2 왜 이렇게 구분하는가?

**관리 의존성**(예: 전용 DB)은 애플리케이션의 **구현 세부사항**이다. 외부 세계는 DB의 스키마나 쿼리를 직접 관찰하지 않는다. 따라서 DB와의 상호작용 방식이 바뀌어도 외부에서는 알 수 없다.

**비관리 의존성**(예: 메시지 버스)은 **관찰 가능한 동작**이다. 다른 시스템이 메시지를 소비하므로, 메시지의 형식이나 내용이 바뀌면 외부에 영향을 미친다.

```csharp
// 관리 의존성 (DB): 실제 인스턴스 사용 (통합 테스트)
[Fact]
public void Placing_order_persists_to_database()
{
    using var db = new TestDatabase();                 // 실제 DB
    var sut = new OrderService(db, messageBus);

    sut.PlaceOrder(order);

    var saved = db.Orders.Find(order.Id);
    Assert.NotNull(saved);                             // 상태 검증
}

// 비관리 의존성 (메시지 버스): Mock 사용
[Fact]
public void Placing_order_publishes_event()
{
    var busMock = new Mock<IMessageBus>();              // Mock
    var sut = new OrderService(db, busMock.Object);

    sut.PlaceOrder(order);

    busMock.Verify(                                    // 상호작용 검증
        x => x.Publish(It.IsAny<OrderPlaced>()),
        Times.Once);
}
```

> **핵심 통찰**: **관리 의존성(전용 DB)은 Mock하지 말고, 비관리 의존성(메시지 버스, 외부 API)만 Mock하라.** 이것이 Khorikov의 Mock 사용에 대한 최종 가이드라인이다. 관리 의존성은 통합 테스트에서 실제 인스턴스로 테스트하고, 비관리 의존성은 Mock으로 외부 통신을 검증한다.

---

## 5. Mock을 통한 테스트 취약성의 메커니즘

### 5.1 취약성의 두 가지 경로

```
경로 1: 내부 통신을 Mock → 구현 세부사항에 결합 → 리팩터링 시 거짓 양성
경로 2: 관리 의존성(DB)을 Mock → DB 상호작용은 구현 세부사항 → 거짓 양성

올바른 접근:
외부 통신(비관리 의존성)만 Mock → 관찰 가능한 동작을 검증 → 리팩터링 내성 유지
```

### 5.2 정리: Mock 사용 의사결정 트리

```
의존성이 프로세스 외부인가?
├── 아니오 → Mock 하지 않는다 (실제 객체 사용)
│
└── 예 → 다른 애플리케이션이 관찰 가능한가?
    ├── 아니오 (관리 의존성) → Mock 하지 않는다 (통합 테스트에서 실제 사용)
    └── 예 (비관리 의존성) → Mock 한다
```

---

## 요약

- 테스트 더블은 **Mock 계열**(나가는 상호작용 검증)과 **Stub 계열**(들어오는 데이터 제공)로 나뉜다.
- **Stub의 호출을 검증하지 말라**. Stub은 입력을 제공할 뿐이다.
- 관찰 가능한 동작과 구현 세부사항을 구분하라. **관찰 가능한 동작만 테스트에서 검증**해야 한다.
- 잘 설계된 API는 **공개 API = 관찰 가능한 동작**이다. API 설계가 좋으면 테스트도 자연스럽게 좋아진다.
- 육각형 아키텍처에서, **내부 통신은 Mock하지 않고 외부 통신만 Mock**한다.
- 프로세스 외부 의존성은 **관리 의존성**(전용 DB — Mock 안 함)과 **비관리 의존성**(메시지 버스 — Mock 함)으로 나뉜다.
- Mock을 사용할 유일한 정당한 이유: **비관리 의존성과의 상호작용 검증**.

