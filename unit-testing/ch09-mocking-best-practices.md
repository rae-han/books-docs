# Chapter 9: Mocking Best Practices (목 모범 사례)

## 핵심 질문

Mock의 가치를 극대화하려면 어떤 모범 사례를 따라야 하는가? Mock은 **얼마나 많이** 사용해야 하며, **어디에** 적용해야 하는가? Spy와 Mock의 차이는 무엇이며, 언제 어느 것을 사용하는가?

---

## 1. Mock의 가치 극대화

### 1.1 Chapter 5 원칙 재확인

Mock을 올바르게 사용하기 위한 핵심 원칙을 정리하면:

| 원칙 | 설명 |
|------|------|
| **비관리 의존성에만 Mock** | 메시지 버스, SMTP, 외부 API 등 다른 시스템이 관찰하는 의존성 |
| **관리 의존성은 실제 사용** | 전용 DB, 파일 시스템 등 애플리케이션만 접근하는 의존성 |
| **Stub 검증 금지** | Stub의 호출 방식은 구현 세부사항 |

### 1.2 Mock의 수

통합 테스트에서 Mock은 **비관리 의존성의 수만큼만** 존재해야 한다:

```csharp
// 비관리 의존성이 2개면 Mock도 2개
public class OrderControllerTests
{
    [Fact]
    public void Placing_order_sends_email_and_publishes_event()
    {
        var db = new TestDatabase();              // 관리 의존성: 실제
        var emailMock = new Mock<IEmailGateway>(); // 비관리 의존성: Mock
        var busMock = new Mock<IMessageBus>();     // 비관리 의존성: Mock
        var sut = new OrderController(db.Context, emailMock.Object, busMock.Object);

        sut.PlaceOrder(new OrderDto { /* ... */ });

        // 관리 의존성: 상태 검증
        Assert.NotNull(db.Context.Orders.Find(orderId));

        // 비관리 의존성: 상호작용 검증
        emailMock.Verify(x => x.SendConfirmation(It.IsAny<string>()), Times.Once);
        busMock.Verify(x => x.Publish(It.IsAny<OrderPlaced>()), Times.Once);
    }
}
```

---

## 2. Mock vs Spy

### 2.1 차이점

| | Mock | Spy |
|---|---|---|
| **생성 방식** | Mock 프레임워크(Moq 등)로 자동 생성 | 수동으로 클래스를 작성 |
| **검증 방식** | `mock.Verify(...)` | 내부 상태 확인 |
| **가독성** | 프레임워크 API 의존 | 테스트 코드가 더 명확할 수 있음 |

### 2.2 Spy 예제

```csharp
// Spy: 수동으로 작성한 테스트 더블
public class FakeMessageBus : IMessageBus
{
    public List<object> SentMessages { get; } = new();

    public void Publish(object message)
    {
        SentMessages.Add(message);                  // 호출 기록
    }
}

// 테스트에서 사용
[Fact]
public void Placing_order_publishes_event()
{
    var bus = new FakeMessageBus();                  // Spy 사용
    var sut = new OrderController(db.Context, bus);

    sut.PlaceOrder(new OrderDto());

    Assert.Single(bus.SentMessages);                // 상태 검증처럼 읽힌다
    Assert.IsType<OrderPlaced>(bus.SentMessages[0]);
}
```

Spy는 Mock 프레임워크 없이 상호작용을 검증할 수 있다. 코드가 더 직관적일 수 있지만, 직접 클래스를 작성해야 하는 비용이 있다.

### 2.3 언제 무엇을 사용하는가?

Khorikov는 두 가지 모두 유효한 접근법이라고 본다. 선택 기준:

- **Spy**: 검증 로직이 복잡하거나, 여러 테스트에서 같은 가짜 객체를 재사용할 때
- **Mock 프레임워크**: 간단한 검증이나, 일회성 설정이 필요할 때

---

## 3. Mock 검증의 모범 사례

### 3.1 메시지의 구조까지 검증하라

비관리 의존성으로 보내는 메시지는 **계약(contract)**이다. 다른 시스템이 이 메시지를 소비하므로, 구조와 내용이 정확해야 한다:

```csharp
// 불충분: 메시지 타입만 확인
busMock.Verify(x => x.Publish(It.IsAny<OrderPlaced>()), Times.Once);

// 충분: 메시지 내용까지 확인
busMock.Verify(x => x.Publish(It.Is<OrderPlaced>(e =>
    e.OrderId == expectedOrderId &&
    e.CustomerId == expectedCustomerId &&
    e.TotalAmount == 100m)),
    Times.Once);
```

### 3.2 호출 횟수도 검증하라

메시지가 **한 번만** 발행되어야 하는데 두 번 발행되면 문제다:

```csharp
// 좋은 예: 정확한 횟수 검증
busMock.Verify(x => x.Publish(It.IsAny<OrderPlaced>()), Times.Once);

// 더 좋은 예: 예상치 못한 다른 메시지도 검증
busMock.VerifyNoOtherCalls();   // 위에서 검증한 것 외에 다른 호출이 없는지 확인
```

### 3.3 Mock을 시스템 경계 바로 옆에 배치하라

Mock은 **애플리케이션의 가장 바깥쪽**에 배치해야 한다:

```
나쁜 예:                    좋은 예:
Controller                 Controller
  → DomainService            → DomainService
    → Mock<IRepository>        → Repository
                                 → Mock<IMessageBus>

내부 계층을 Mock          시스템 경계에서 Mock
→ 구현 세부사항에 결합    → 외부 통신만 검증
```

```csharp
// 나쁜 예: 내부 서비스를 Mock
var serviceMock = new Mock<IDomainService>();
var sut = new Controller(serviceMock.Object);

// 좋은 예: 시스템 경계의 비관리 의존성을 Mock
var busMock = new Mock<IMessageBus>();
var sut = new Controller(new DomainService(), db.Context, busMock.Object);
```

> **핵심 통찰**: Mock은 **시스템의 가장자리(boundary)**에 위치해야 한다. 내부 계층(도메인 서비스, 리포지토리 인터페이스)을 Mock하면, 테스트가 구현 세부사항에 결합되어 리팩터링 내성이 떨어진다. Mock은 외부 세계와의 **접점**에만 놓으라.

---

## 4. 컨트롤러에서 비즈니스 로직 유출 방지

### 4.1 문제: 컨트롤러가 너무 똑똑해짐

Mock 검증이 복잡해진다면, 컨트롤러에 **비즈니스 로직이 유출**되었을 수 있다:

```csharp
// 컨트롤러에 비즈니스 로직 유출
public void ChangeEmail(int userId, string newEmail)
{
    var user = _db.GetUser(userId);
    var company = _db.GetCompany();

    // 이 조건문은 비즈니스 로직 → 도메인 모델로 가야 함
    if (user.Email != newEmail)
    {
        string domain = newEmail.Split('@')[1];
        bool isEmployee = domain == company.DomainName;
        // ...
    }
}
```

### 4.2 해결: CanExecute/Execute 패턴

도메인 모델이 "할 수 있는지"와 "실행"을 분리:

```csharp
public class User
{
    public string CanChangeEmail(string newEmail)
    {
        if (Email == newEmail)
            return "New email is the same as the current one";
        return null;   // null = 실행 가능
    }

    public void ChangeEmail(string newEmail, string companyDomain, int employeeCount)
    {
        // ... 비즈니스 로직 ...
    }
}

// 컨트롤러는 단순 오케스트레이션만
public void ChangeEmail(int userId, string newEmail)
{
    var user = _db.GetUser(userId);
    string error = user.CanChangeEmail(newEmail);
    if (error != null)
        return BadRequest(error);

    var company = _db.GetCompany();
    user.ChangeEmail(newEmail, company.DomainName, company.NumberOfEmployees);
    _db.SaveUser(user);
    // ...
}
```

---

## 5. 통합 테스트에서 Mock 사용 패턴 정리

### 5.1 의사결정 흐름

```
통합 테스트에서 이 의존성을 어떻게 다룰 것인가?

1. 프로세스 내부 의존성인가?
   → 실제 객체 사용 (도메인 모델, 서비스 등)

2. 관리 의존성(전용 DB)인가?
   → 실제 인스턴스 사용 + 상태 검증

3. 비관리 의존성(메시지 버스, 외부 API)인가?
   → Mock/Spy 사용 + 상호작용 검증
     - 메시지 내용과 구조를 정확히 검증
     - 호출 횟수도 검증
     - 예상치 못한 호출이 없는지 확인
```

### 5.2 Anti-patterns

| 안티패턴 | 문제 | 해결 |
|---------|------|------|
| DB를 Mock | 리팩터링 내성 저하, 회귀 방지 부족 | 실제 DB 사용 |
| 도메인 서비스를 Mock | 내부 구현에 결합 | 실제 객체 사용 |
| Stub 호출을 Verify | 입력 수단을 검증하는 것은 무의미 | Stub은 설정만, 검증 안 함 |
| Mock이 5개 이상 | 테스트가 너무 많은 것을 검증 | 테스트 분리 또는 설계 재검토 |

---

## 요약

- Mock은 **비관리 의존성에만** 사용한다. 관리 의존성(DB)은 실제 인스턴스를 사용한다.
- **Spy**는 수동으로 작성한 Mock이다. 복잡한 검증이나 재사용이 필요할 때 유용하다.
- Mock 검증 시 **메시지의 구조와 내용, 호출 횟수**까지 확인하라. 외부 메시지는 계약이다.
- Mock은 **시스템 경계(boundary)**에 배치하라. 내부 계층을 Mock하면 구현에 결합된다.
- Mock 검증이 복잡해지면 **컨트롤러에 비즈니스 로직이 유출**되었을 수 있다. 도메인 모델로 이동시켜라.
- **CanExecute/Execute 패턴**으로 도메인 로직과 오케스트레이션을 분리한다.

