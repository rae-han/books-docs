# Chapter 11: Unit Testing Anti-patterns (단위 테스트 안티패턴)

## 핵심 질문

피해야 할 단위 테스트 안티패턴은 무엇인가? 프라이빗 메서드 테스트, 테스트를 위한 코드 노출, 도메인 지식 유출, 구체 클래스 Mock 등의 관행이 왜 해로우며, 어떻게 대안을 찾는가?

---

## 1. 안티패턴 1: 프라이빗 메서드 테스트

### 1.1 유혹

프라이빗 메서드에 복잡한 로직이 있으면, 직접 테스트하고 싶은 유혹이 든다:

```csharp
public class Order
{
    public decimal GetTotalPrice()
    {
        return _items.Sum(x => CalculateItemPrice(x));   // 프라이빗 메서드 호출
    }

    private decimal CalculateItemPrice(OrderItem item)   // 복잡한 로직
    {
        decimal price = item.UnitPrice * item.Quantity;
        if (item.Quantity > 10)
            price *= 0.9m;   // 대량 할인
        if (_customer.IsVip)
            price *= 0.95m;  // VIP 할인
        return price;
    }
}
```

### 1.2 왜 안티패턴인가?

프라이빗 메서드를 직접 테스트하면:

| 문제 | 설명 |
|------|------|
| **구현 세부사항에 결합** | 프라이빗 메서드의 시그니처가 바뀌면 테스트가 깨진다 |
| **리팩터링 방해** | 메서드를 합치거나 분리하면 테스트를 전면 수정해야 한다 |
| **캡슐화 위반** | 테스트를 위해 접근 제한을 느슨하게 만들게 된다 |

### 1.3 올바른 접근

프라이빗 메서드는 **공개 API를 통해 간접적으로** 테스트한다:

```csharp
[Theory]
[InlineData(5, 100, false, 500)]       // 일반 고객, 소량
[InlineData(15, 100, false, 1350)]     // 일반 고객, 대량 (10% 할인)
[InlineData(15, 100, true, 1282.5)]    // VIP 고객, 대량 (10% + 5% 할인)
public void Total_price_accounts_for_quantity_and_vip_discounts(
    int quantity, decimal unitPrice, bool isVip, decimal expectedTotal)
{
    var customer = new Customer(isVip: isVip);
    var order = new Order(customer);
    order.AddItem(new OrderItem(unitPrice, quantity));

    decimal total = order.GetTotalPrice();        // 공개 메서드를 통해 테스트

    Assert.Equal(expectedTotal, total);
}
```

### 1.4 프라이빗 메서드가 너무 복잡하면?

프라이빗 메서드가 독립적으로 테스트하고 싶을 정도로 복잡하다면, 그것은 **별도 클래스로 추출**해야 한다는 신호다:

```csharp
// 추출 전
private decimal CalculateItemPrice(OrderItem item) { /* 복잡한 로직 */ }

// 추출 후
public class PriceCalculator    // 새로운 공개 클래스
{
    public decimal Calculate(OrderItem item, Customer customer)
    {
        // 같은 로직이지만 이제 공개 API로 테스트 가능
    }
}
```

> **핵심 통찰**: 프라이빗 메서드를 직접 테스트하고 싶다면, 두 가지 중 하나다: (1) 공개 API를 통해 충분히 테스트할 수 있는데 간과하고 있거나, (2) 로직이 **별도 클래스로 추출되어야** 한다는 설계 신호다. 어느 쪽이든, 프라이빗 메서드를 직접 테스트하는 것은 답이 아니다.

---

## 2. 안티패턴 2: 테스트를 위한 코드 노출

### 2.1 문제

테스트를 위해 프로덕션 코드의 접근 제한을 변경하는 것:

```csharp
// 나쁜 예: 테스트를 위해 internal로 변경
public class User
{
    internal string NormalizeName(string name)    // private → internal (테스트 목적)
    {
        return name.Trim().ToLower();
    }
}

// InternalsVisibleTo로 테스트 프로젝트에 노출
[assembly: InternalsVisibleTo("MyApp.Tests")]
```

### 2.2 왜 안티패턴인가?

- 캡슐화를 깨뜨린다 — 테스트가 구현 세부사항에 접근하게 된다
- 프로덕션 코드의 **설계를 테스트에 맞추는 것**이다 (반대여야 한다)
- 테스트가 구현에 결합되어 리팩터링 내성이 떨어진다

### 2.3 올바른 접근

- 공개 API를 통해 간접 테스트하거나
- 로직을 별도 클래스로 추출하여 공개 API로 만들거나
- **테스트를 위해 접근 제한을 변경하는 것은 설계의 부채**임을 인식한다

---

## 3. 안티패턴 3: 도메인 지식 유출

### 3.1 테스트에서 프로덕션 로직 재구현

```csharp
// 안티패턴: 테스트가 프로덕션 로직을 복제
[Fact]
public void Discount_is_calculated_correctly()
{
    var products = new[] { new Product(), new Product(), new Product() };

    decimal discount = PriceEngine.CalculateDiscount(products);

    // 테스트가 프로덕션 로직을 그대로 재구현!
    decimal expectedDiscount = products.Length * 0.01m;
    Assert.Equal(expectedDiscount, discount);
}
```

이 테스트에서 `products.Length * 0.01m`은 `CalculateDiscount`의 **내부 알고리즘을 복제**한 것이다. 알고리즘이 잘못되어도 테스트도 같이 잘못되므로 버그를 잡을 수 없다.

### 3.2 올바른 접근: 하드코딩된 기대값

```csharp
// 올바른 예: 하드코딩된 기대값
[Fact]
public void Discount_of_three_products()
{
    var products = new[] { new Product(), new Product(), new Product() };

    decimal discount = PriceEngine.CalculateDiscount(products);

    Assert.Equal(0.03m, discount);    // 미리 계산된 하드코딩 값
}
```

`0.03m`은 **미리 손으로 계산한 값**이다. 프로덕션 로직과 독립적이므로, 알고리즘에 버그가 있으면 테스트가 실패한다.

> **핵심 통찰**: 테스트의 기대값(expected)에 **프로덕션 로직을 재사용하지 말라**. 기대값은 미리 계산된 상수(하드코딩)여야 한다. 테스트가 프로덕션 로직을 복제하면, 둘 다 같은 방식으로 잘못될 수 있어 회귀 방지 능력이 0이 된다.

---

## 4. 안티패턴 4: 코드 오염(Code Pollution)

### 4.1 정의

코드 오염이란 **테스트에서만 필요한 코드가 프로덕션 코드에 침투**하는 것이다:

```csharp
// 코드 오염: 테스트 전용 생성자
public class Logger
{
    private readonly bool _isTestEnvironment;

    public Logger(bool isTestEnvironment = false)    // 테스트 전용 매개변수!
    {
        _isTestEnvironment = isTestEnvironment;
    }

    public void Log(string message)
    {
        if (_isTestEnvironment)
            return;                                   // 테스트에서는 아무것도 안 함
        // 실제 로깅 로직...
    }
}
```

### 4.2 왜 해로운가?

- 프로덕션 코드에 **테스트 관련 분기**가 생긴다
- 코드의 복잡도가 올라간다
- `isTestEnvironment` 같은 플래그가 프로덕션에 실수로 `true`가 되면 기능이 동작하지 않는다

### 4.3 올바른 접근: 인터페이스로 분리

```csharp
public interface ILogger
{
    void Log(string message);
}

// 프로덕션 구현
public class Logger : ILogger
{
    public void Log(string message) { /* 실제 로깅 */ }
}

// 테스트용 구현 (테스트 프로젝트에만 존재)
public class FakeLogger : ILogger
{
    public void Log(string message) { /* 아무것도 안 함 */ }
}
```

---

## 5. 안티패턴 5: 구체 클래스 Mock

### 5.1 문제

인터페이스가 아닌 구체 클래스를 Mock하는 것:

```csharp
// 안티패턴: 구체 클래스 Mock
var loggerMock = new Mock<Logger>();            // 구체 클래스를 Mock
var sut = new OrderService(loggerMock.Object);
```

### 5.2 왜 해로운가?

- 구체 클래스의 **가상(virtual) 메서드만** Mock 가능 — 제약이 많다
- 생성자가 복잡하면 Mock 생성 자체가 어렵다
- 구체 클래스의 **일부 동작만 오버라이드**하면, 나머지 실제 로직이 실행되어 예측 불가능한 결과를 낳는다

### 5.3 올바른 접근

Mock이 필요한 의존성은 **인터페이스로 추상화**한다. 단, Chapter 8에서 언급했듯이 인터페이스는 **Mock이 필요한 비관리 의존성에만** 만든다.

---

## 6. 안티패턴 6: 시간 처리

### 6.1 문제: DateTime.Now 직접 사용

```csharp
// 안티패턴: 시간에 직접 의존
public class Delivery
{
    public bool IsValid => DateTime.Now < _scheduledDate;   // 테스트마다 결과가 달라진다!
}
```

이 코드는 **비결정적(non-deterministic)**이다. 오늘은 통과하지만 내일은 실패할 수 있다.

### 6.2 해결: 시간을 주입하라

**앰비언트 컨텍스트(*Ambient context — 정적 접근자를 통해 전역적으로 사용 가능한 의존성. DateTime.Now, ConfigurationManager 등이 해당*) 대신 명시적 주입:**

```csharp
// 방법 1: 매개변수로 주입
public bool IsValid(DateTime currentTime)
{
    return currentTime < _scheduledDate;
}

// 방법 2: 인터페이스로 주입
public interface IDateTimeProvider
{
    DateTime Now { get; }
}

public class Delivery
{
    private readonly IDateTimeProvider _dateTime;

    public Delivery(DateTime scheduledDate, IDateTimeProvider dateTime)
    {
        _scheduledDate = scheduledDate;
        _dateTime = dateTime;
    }

    public bool IsValid => _dateTime.Now < _scheduledDate;
}
```

```csharp
// 테스트에서
[Fact]
public void Delivery_with_a_past_date_is_invalid()
{
    var dateTime = new FakeDateTimeProvider(new DateTime(2024, 1, 15));
    var delivery = new Delivery(
        scheduledDate: new DateTime(2024, 1, 10),   // 과거
        dateTime: dateTime);

    Assert.False(delivery.IsValid);                  // 항상 동일한 결과
}
```

Khorikov는 **가능하면 매개변수로 직접 전달**하는 것을 선호한다. 인터페이스는 주입할 수 없는 경우에만 사용한다.

> **핵심 통찰**: `DateTime.Now`는 **숨겨진 의존성(hidden dependency)**이다. 테스트를 비결정적으로 만들고, 특정 시간에만 발생하는 버그를 재현하기 어렵게 만든다. 시간을 **명시적 매개변수**로 전달하라. 이것은 단위 테스트뿐 아니라 코드의 설계를 개선하는 것이기도 하다.

---

## 7. 안티패턴 7: Assert에서 값 비교 대신 참조 비교

### 7.1 문제

```csharp
// 안티패턴: 참조 비교 (의도와 다른 결과)
[Fact]
public void GetUser_returns_correct_user()
{
    var expected = new User("Alice");

    var result = sut.GetUser("Alice");

    Assert.Equal(expected, result);      // User가 Equals를 오버라이드하지 않으면 참조 비교 → 항상 실패
}
```

### 7.2 해결

- 값 객체에서는 `Equals`와 `GetHashCode`를 오버라이드한다
- 또는 **개별 속성을 비교**한다:

```csharp
Assert.Equal("Alice", result.Name);
Assert.Equal(UserType.Customer, result.Type);
```

---

## 8. 안티패턴 요약 테이블

| 안티패턴 | 핵심 문제 | 해결 |
|---------|----------|------|
| 프라이빗 메서드 테스트 | 구현 세부사항에 결합 | 공개 API로 간접 테스트, 또는 별도 클래스 추출 |
| 테스트를 위한 코드 노출 | 캡슐화 위반 | 공개 API로 테스트, 설계 재검토 |
| 도메인 지식 유출 | 회귀 방지 능력 제로 | 하드코딩된 기대값 사용 |
| 코드 오염 | 테스트 코드가 프로덕션에 침투 | 인터페이스로 분리 |
| 구체 클래스 Mock | 부분적 Mock의 위험 | 인터페이스 추상화 |
| DateTime.Now 직접 사용 | 비결정적 테스트 | 시간을 매개변수로 주입 |
| 참조 비교 | 의도와 다른 검증 | Equals 오버라이드 또는 속성 비교 |

---

## 요약

- **프라이빗 메서드를 직접 테스트하지 말라**. 공개 API로 간접 테스트하거나, 복잡하면 별도 클래스로 추출한다.
- **테스트를 위해 프로덕션 코드의 접근 제한을 변경하지 말라**. 이것은 설계의 부채다.
- 테스트의 기대값에 **프로덕션 로직을 재사용하지 말라**. 하드코딩된 상수를 사용한다.
- **코드 오염**을 피하라. 테스트 전용 플래그나 분기는 프로덕션 코드에 있으면 안 된다.
- **구체 클래스를 Mock하지 말라**. 인터페이스를 사용한다.
- `DateTime.Now`를 직접 호출하지 말라. **시간을 명시적으로 주입**한다.
- 이 안티패턴들의 공통 원인은 **구현 세부사항에 대한 결합**이다. 관찰 가능한 동작만 검증하라는 이 책의 핵심 메시지가 여기서도 반복된다.

