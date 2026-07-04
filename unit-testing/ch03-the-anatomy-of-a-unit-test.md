# Chapter 3: The Anatomy of a Unit Test (단위 테스트의 구조)

## 핵심 질문

좋은 단위 테스트는 어떤 구조를 갖는가? AAA 패턴이란 무엇이며, 테스트의 가독성과 유지보수성을 높이기 위해 어떤 관행을 따라야 하는가?

---

## 1. AAA 패턴

### 1.1 세 단계

AAA(*Arrange-Act-Assert — 준비-실행-검증. 단위 테스트의 세 단계를 나타내는 패턴이다.*)는 단위 테스트를 세 단계로 구성하는 패턴이다:

```csharp
[Fact]
public void Sum_of_two_numbers()
{
    // Arrange (준비)
    double first = 10;
    double second = 20;
    var calculator = new Calculator();

    // Act (실행)
    double result = calculator.Sum(first, second);

    // Assert (검증)
    Assert.Equal(30, result);
}
```

| 단계 | 역할 | 비중 |
|------|------|------|
| **Arrange** | SUT와 의존성을 원하는 상태로 준비한다 | 가장 큼 (보통 전체의 대부분) |
| **Act** | SUT의 동작을 호출한다 | 보통 **한 줄** |
| **Assert** | 결과를 검증한다 | 한 줄 또는 소수의 줄 |

AAA 패턴은 Given-When-Then 패턴과 동일한 구조다. 이름만 다를 뿐 의미는 같다:
- Given = Arrange
- When = Act
- Then = Assert

### 1.2 주석을 넣을 것인가?

`// Arrange`, `// Act`, `// Assert` 주석을 넣는 것은 선택사항이다. Khorikov는 다음 기준을 제안한다:

- **세 단계가 명확히 구분되면** → 주석 생략 가능 (빈 줄로 구분)
- **Arrange 단계가 길어서 경계가 모호하면** → 주석 추가

빈 줄로 구분하는 것만으로 충분한 경우가 대부분이다:

```csharp
[Fact]
public void Sum_of_two_numbers()
{
    double first = 10;
    double second = 20;
    var calculator = new Calculator();

    double result = calculator.Sum(first, second);

    Assert.Equal(30, result);
}
```

---

## 2. 여러 개의 Arrange, Act, Assert를 피하라

### 2.1 안티패턴: 다중 Act

하나의 테스트에 여러 Act(실행) 단계가 있으면, 그것은 **하나의 테스트가 아니라 여러 테스트를 합쳐 놓은 것**이다:

```csharp
// 나쁜 예: 다중 Act
[Fact]
public void Purchase_and_inventory_check()
{
    // Arrange
    var store = new Store();
    store.AddInventory(Product.Shampoo, 10);
    var customer = new Customer();

    // Act 1
    bool success = customer.Purchase(store, Product.Shampoo, 5);

    // Assert 1
    Assert.True(success);
    Assert.Equal(5, store.GetInventory(Product.Shampoo));

    // Act 2
    success = customer.Purchase(store, Product.Shampoo, 10);

    // Assert 2
    Assert.False(success);
    Assert.Equal(5, store.GetInventory(Product.Shampoo));
}
```

이 테스트는 두 개의 동작을 검증한다:
1. 재고가 충분할 때 구매 성공
2. 재고가 부족할 때 구매 실패

### 2.2 해결: 테스트 분리

각 동작을 독립적인 테스트로 분리해야 한다:

```csharp
[Fact]
public void Purchase_succeeds_when_enough_inventory()
{
    var store = new Store();
    store.AddInventory(Product.Shampoo, 10);
    var customer = new Customer();

    bool success = customer.Purchase(store, Product.Shampoo, 5);

    Assert.True(success);
    Assert.Equal(5, store.GetInventory(Product.Shampoo));
}

[Fact]
public void Purchase_fails_when_not_enough_inventory()
{
    var store = new Store();
    store.AddInventory(Product.Shampoo, 10);
    var customer = new Customer();

    bool success = customer.Purchase(store, Product.Shampoo, 15);

    Assert.False(success);
    Assert.Equal(10, store.GetInventory(Product.Shampoo));
}
```

> **핵심 통찰**: 하나의 테스트는 **하나의 동작(behavior)**만 검증해야 한다. 다중 Act는 테스트의 집중도를 떨어뜨리고, 첫 번째 Assert가 실패하면 이후 검증이 실행되지 않아 디버깅이 어려워진다. 단, 하나의 동작이 여러 결과를 낳을 수 있으므로, 하나의 Act에 **여러 Assert**가 있는 것은 괜찮다.

---

## 3. Act 단계: 한 줄이 이상적

### 3.1 Act가 두 줄 이상이면 의심하라

Act 단계가 두 줄 이상이면, SUT의 API 설계에 문제가 있을 수 있다:

```csharp
// 의심스러운 예: Act가 두 줄
[Fact]
public void Purchase_succeeds_when_enough_inventory()
{
    var store = new Store();
    store.AddInventory(Product.Shampoo, 10);
    var customer = new Customer();

    bool success = customer.Purchase(store, Product.Shampoo, 5);
    store.RemoveInventory(Product.Shampoo, 5);   // ← 이 줄이 왜 필요한가?

    Assert.True(success);
    Assert.Equal(5, store.GetInventory(Product.Shampoo));
}
```

이 예에서 `Purchase`를 호출한 후 `RemoveInventory`를 별도로 호출해야 한다면, 이것은 **캡슐화 위반**이다. `Purchase` 메서드가 재고 감소까지 내부적으로 처리해야 한다.

### 3.2 불변 위반(Invariant Violation) 방지

Act가 여러 줄이면, 클라이언트가 중간 단계를 빠뜨려 객체를 잘못된 상태로 만들 수 있다. 이것은 **불변 위반**이다. SUT의 API를 개선하여 하나의 메서드 호출로 완전한 동작이 이루어지도록 해야 한다.

> **핵심 통찰**: Act 단계가 **한 줄**이면 SUT의 API가 잘 설계되었다는 신호다. 두 줄 이상이면 캡슐화가 부족하다는 경고 신호일 수 있다. 물론 예외가 있지만, 기본적으로 한 줄을 목표로 해야 한다.

---

## 4. Assert 단계: 얼마나 많은 Assert가 적절한가?

### 4.1 Assert 수의 원칙

"테스트당 Assert는 하나만" 주장하는 사람들이 있지만, Khorikov는 이를 **너무 엄격한 규칙**이라고 본다. 핵심은 Assert의 수가 아니라, **하나의 동작을 검증하는가**이다.

```csharp
// 좋은 예: 하나의 동작, 여러 Assert
[Fact]
public void Purchase_succeeds_when_enough_inventory()
{
    var store = new Store();
    store.AddInventory(Product.Shampoo, 10);
    var customer = new Customer();

    bool success = customer.Purchase(store, Product.Shampoo, 5);

    Assert.True(success);                                    // 동작의 결과 1
    Assert.Equal(5, store.GetInventory(Product.Shampoo));    // 동작의 결과 2
}
```

구매 동작은 두 가지 결과를 낳는다: (1) 성공 여부 반환, (2) 재고 감소. 둘 다 **같은 동작의 결과**이므로 하나의 테스트에서 검증하는 것이 올바르다.

### 4.2 Assert가 너무 많을 때

Assert가 너무 많아지면(예: 10개 이상), 테스트가 **너무 많은 것을 검증**하고 있거나, SUT가 한 번의 동작에서 **너무 많은 일을 하고 있다**는 신호다. 이 경우:

1. SUT의 동작을 더 작은 단위로 분리하거나
2. 커스텀 Assert 메서드로 여러 Assert를 하나의 의미 있는 검증으로 묶는다

---

## 5. Arrange 단계: 재사용과 가독성

### 5.1 테스트 픽스처(Test Fixture) 재사용

Arrange 단계가 길어지면, 여러 테스트에서 중복되는 설정 코드를 재사용하고 싶은 유혹이 있다. 하지만 **잘못된 재사용은 테스트의 가독성을 해친다**.

**안티패턴: 생성자에서 모든 것을 초기화**

```csharp
// 나쁜 예
public class CustomerTests
{
    private readonly Store _store;
    private readonly Customer _customer;

    public CustomerTests()   // 생성자에서 모든 것을 준비
    {
        _store = new Store();
        _store.AddInventory(Product.Shampoo, 10);
        _customer = new Customer();
    }

    [Fact]
    public void Purchase_succeeds_when_enough_inventory()
    {
        bool success = _customer.Purchase(_store, Product.Shampoo, 5);

        Assert.True(success);
        Assert.Equal(5, _store.GetInventory(Product.Shampoo));
    }

    [Fact]
    public void Purchase_fails_when_not_enough_inventory()
    {
        bool success = _customer.Purchase(_store, Product.Shampoo, 15);

        Assert.False(success);
        Assert.Equal(10, _store.GetInventory(Product.Shampoo));
    }
}
```

이 접근법에는 두 가지 문제가 있다:

| 문제 | 설명 |
|------|------|
| **테스트 간 결합** | 생성자의 Arrange를 수정하면 모든 테스트에 영향을 미친다 |
| **가독성 저하** | 테스트만 봐서는 어떤 상태가 준비되었는지 알 수 없다. 생성자를 찾아가야 한다 |

### 5.2 권장: 비공개 팩토리 메서드

```csharp
// 좋은 예
public class CustomerTests
{
    [Fact]
    public void Purchase_succeeds_when_enough_inventory()
    {
        var store = CreateStoreWithInventory(Product.Shampoo, 10);
        var customer = CreateCustomer();

        bool success = customer.Purchase(store, Product.Shampoo, 5);

        Assert.True(success);
        Assert.Equal(5, store.GetInventory(Product.Shampoo));
    }

    [Fact]
    public void Purchase_fails_when_not_enough_inventory()
    {
        var store = CreateStoreWithInventory(Product.Shampoo, 10);
        var customer = CreateCustomer();

        bool success = customer.Purchase(store, Product.Shampoo, 15);

        Assert.False(success);
        Assert.Equal(10, store.GetInventory(Product.Shampoo));
    }

    private Store CreateStoreWithInventory(Product product, int quantity)
    {
        var store = new Store();
        store.AddInventory(product, quantity);
        return store;
    }

    private Customer CreateCustomer() => new Customer();
}
```

비공개 팩토리 메서드는 Arrange 코드를 줄이면서도 **각 테스트가 자체적으로 완결**되도록 한다. 테스트를 읽을 때 생성자로 이동할 필요 없이, 팩토리 메서드의 이름만으로 어떤 준비가 이루어지는지 이해할 수 있다.

> **핵심 통찰**: 테스트 간 Arrange 코드 공유에는 **비공개 팩토리 메서드**를 사용하라. 생성자(또는 setUp 메서드)에 공통 초기화 코드를 넣는 것은 테스트의 가독성과 독립성을 해친다. 각 테스트는 Arrange-Act-Assert 전체를 읽는 것만으로 완전히 이해할 수 있어야 한다.

---

## 6. 테스트 네이밍

### 6.1 엄격한 네이밍 규칙을 피하라

많은 팀에서 다음과 같은 네이밍 규칙을 사용한다:

```
[테스트 대상 메서드]_[시나리오]_[기대 결과]
```

예: `Purchase_WhenEnoughInventory_ReturnsTrue`

Khorikov는 이 규칙이 **너무 기계적**이라고 본다. 문제점:

1. **메서드 이름에 결합**: 메서드 이름이 바뀌면 테스트 이름도 바꿔야 한다
2. **가독성 저하**: 밑줄과 약어로 가득 찬 이름은 읽기 어렵다
3. **동작이 아니라 구현을 기술**: 메서드 이름을 포함하면 "무엇을 하는가"가 아니라 "어떻게 하는가"에 초점이 맞춰진다

### 6.2 권장: 동작을 서술하는 이름

```csharp
// 나쁜 예: 기계적 네이밍
[Fact]
public void IsDeliveryValid_InvalidDate_ReturnsFalse() { }

// 좋은 예: 동작을 서술
[Fact]
public void Delivery_with_a_past_date_is_invalid() { }
```

좋은 테스트 이름의 특성:

- **비개발자도 이해할 수 있다** — 비즈니스 동작을 서술하므로
- **밑줄로 단어를 구분한다** — 가독성을 위해
- **메서드 이름을 포함하지 않는다** — 구현이 아니라 동작에 초점
- **"should" 사용을 피한다** — 테스트는 사실을 진술한다. "should be"가 아니라 "is"를 사용한다

> **핵심 통찰**: 테스트 이름은 **비즈니스 동작을 평이한 영어로 서술**해야 한다. `Delivery_with_a_past_date_is_invalid`는 누구나 읽을 수 있다. `IsDeliveryValid_InvalidDate_ReturnsFalse`는 코드를 읽는 느낌이다. 테스트는 시스템의 **살아있는 문서**이므로, 읽기 쉬워야 한다.

---

## 7. 매개변수화된 테스트(Parameterized Tests)

### 7.1 테스트 중복 줄이기

비슷한 시나리오를 여러 입력값으로 검증해야 할 때, 매개변수화된 테스트가 유용하다:

```csharp
// 매개변수화 전: 중복된 테스트
[Fact]
public void Delivery_with_a_past_date_is_invalid()
{
    var delivery = new Delivery(DateTime.Now.AddDays(-1));
    Assert.False(delivery.IsValid);
}

[Fact]
public void Delivery_with_today_date_is_invalid()
{
    var delivery = new Delivery(DateTime.Now);
    Assert.False(delivery.IsValid);
}

[Fact]
public void Delivery_with_a_future_date_is_valid()
{
    var delivery = new Delivery(DateTime.Now.AddDays(1));
    Assert.True(delivery.IsValid);
}
```

```csharp
// 매개변수화 후: 하나의 테스트로 통합
[Theory]
[InlineData(-1, false)]
[InlineData(0, false)]
[InlineData(1, true)]
public void Detects_an_invalid_delivery_date(int daysFromNow, bool expected)
{
    var delivery = new Delivery(DateTime.Now.AddDays(daysFromNow));

    bool isValid = delivery.IsValid;

    Assert.Equal(expected, isValid);
}
```

### 7.2 매개변수화의 한계

매개변수화된 테스트는 **간단한 입력-출력 매핑**에 적합하다. 하지만 다음 경우에는 별도 테스트를 유지하는 것이 낫다:

- 시나리오마다 **Arrange 단계가 다를 때**
- 테스트 이름이 시나리오를 **충분히 설명하지 못할 때**
- **긍정적 테스트와 부정적 테스트**가 근본적으로 다른 시나리오를 나타낼 때

> **핵심 통찰**: 매개변수화된 테스트와 개별 테스트 사이에는 **가독성과 코드 양의 트레이드오프**가 있다. 매개변수화하면 코드가 줄지만, 각 시나리오의 의도가 덜 명확해진다. Khorikov는 긍정적 케이스와 부정적 케이스를 **각각 별도의 매개변수화 테스트**로 분리할 것을 권한다.

---

## 8. Fluent Assertions

### 8.1 가독성 향상

Fluent Assertions 라이브러리를 사용하면 Assert 코드를 더 읽기 쉽게 만들 수 있다:

```csharp
// 기본 Assert
Assert.Equal(30, result);

// Fluent Assertions
result.Should().Be(30);
```

더 복잡한 검증에서 차이가 두드러진다:

```csharp
// 기본 Assert
Assert.Equal(5, store.GetInventory(Product.Shampoo));
Assert.True(success);

// Fluent Assertions
store.GetInventory(Product.Shampoo).Should().Be(5);
success.Should().BeTrue();
```

Fluent Assertions는 선택사항이지만, 테스트의 **가독성**을 높이는 데 기여한다.

---

## 요약

- 단위 테스트는 **AAA(Arrange-Act-Assert)** 패턴을 따른다. Given-When-Then과 동일한 구조다.
- 하나의 테스트에는 **하나의 Act**(하나의 동작)만 있어야 한다. 다중 Act는 여러 테스트를 합쳐 놓은 것이다.
- Act 단계가 **한 줄**이면 SUT의 API가 잘 설계되었다는 신호다. 두 줄 이상이면 캡슐화 부족을 의심하라.
- 하나의 Act에 **여러 Assert**는 괜찮다. 핵심은 Assert 수가 아니라, 하나의 동작을 검증하는가이다.
- Arrange 코드 재사용에는 생성자가 아닌 **비공개 팩토리 메서드**를 사용하라.
- 테스트 이름은 **동작을 평이한 영어로 서술**해야 한다. 기계적 네이밍 규칙을 피하라.
- **매개변수화된 테스트**로 비슷한 시나리오의 중복을 줄일 수 있지만, 가독성과의 트레이드오프를 고려하라.

