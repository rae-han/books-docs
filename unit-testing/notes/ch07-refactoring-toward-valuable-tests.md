# Chapter 7: Refactoring Toward Valuable Tests (가치 있는 테스트를 위한 리팩터링)

## 핵심 질문

테스트의 가치는 프로덕션 코드의 설계에 크게 의존한다. 코드를 **네 가지 유형**으로 분류했을 때, 어떤 유형이 테스트 가치가 가장 높으며, **험블 객체(Humble Object)** 패턴으로 어떻게 테스트하기 어려운 코드를 테스트하기 쉬운 코드로 변환할 수 있는가?

---

## 1. 코드의 네 가지 유형

### 1.1 두 가지 축

Khorikov는 프로덕션 코드를 두 가지 축으로 분류한다:

- **도메인 유의성/복잡도**: 코드가 비즈니스 로직을 얼마나 담고 있는가? 또는 얼마나 복잡한가?
- **협력자 수**: 코드가 얼마나 많은 의존성(협력자)과 상호작용하는가?

### 1.2 네 가지 사분면

```
                협력자 수 많음
                    │
     과도하게 복잡한  │  컨트롤러
     코드            │  (Controllers)
     (Overcomplicated│
      code)         │
────────────────────┼────────────────────
     도메인 모델/    │  Trivial 코드
     알고리즘       │
     (Domain model) │
                    │
                도메인 유의성/복잡도 높음
```

| 사분면 | 도메인 유의성 | 협력자 수 | 테스트 가치 |
|--------|-------------|----------|-----------|
| **도메인 모델/알고리즘** | 높음 | 적음 | **최고** — 반드시 테스트 |
| **Trivial 코드** | 낮음 | 적음 | **최저** — 테스트 불필요 |
| **컨트롤러** | 낮음 | 많음 | 중간 — 통합 테스트로 |
| **과도하게 복잡한 코드** | 높음 | 많음 | **분해 필요** |

### 1.3 각 사분면의 예시

```csharp
// 도메인 모델/알고리즘: 높은 도메인 유의성, 적은 협력자 → 테스트 가치 최고
public class PriceEngine
{
    public decimal CalculateDiscount(Product[] products)
    {
        decimal discount = products.Length * 0.01m;
        return Math.Min(discount, 0.2m);
    }
}

// Trivial 코드: 낮은 도메인 유의성, 적은 협력자 → 테스트 불필요
public class Product
{
    public string Name { get; set; }
}

// 컨트롤러: 낮은 도메인 유의성, 많은 협력자 → 통합 테스트
public class OrderController
{
    public void PlaceOrder(OrderDto dto)
    {
        var order = _mapper.Map(dto);
        _repository.Save(order);
        _messageBus.Publish(new OrderPlaced(order.Id));
    }
}

// 과도하게 복잡한 코드: 높은 도메인 유의성, 많은 협력자 → 분해 필요!
public class User
{
    public void ChangeEmail(string newEmail)
    {
        // 비즈니스 규칙 + DB 접근 + 이메일 발송이 한 메서드에...
    }
}
```

> **핵심 통찰**: 테스트 노력을 **도메인 모델/알고리즘**에 집중하라. 이 영역은 도메인 유의성이 높고 협력자가 적어, 단위 테스트의 ROI가 가장 높다. 반면 trivial 코드(getter/setter)는 테스트해봐야 얻는 것이 없고, 컨트롤러는 통합 테스트가 더 적합하다.

---

## 2. 과도하게 복잡한 코드 분해

### 2.1 문제: 비즈니스 로직 + 외부 의존성

"과도하게 복잡한 코드"는 비즈니스 로직과 프로세스 외부 의존성이 **한 곳에 뒤섞인** 코드다. 테스트하려면 Mock을 대량으로 사용해야 하고, 그러면 리팩터링 내성이 떨어진다.

### 2.2 예제: 사용자 이메일 변경

```csharp
// 과도하게 복잡한 코드: 비즈니스 로직 + 외부 의존성
public class User
{
    public string Email { get; private set; }
    public UserType Type { get; private set; }

    public void ChangeEmail(string newEmail, IDatabase database, IMessageBus messageBus)
    {
        // 1. 회사 데이터 조회 (외부 의존성)
        Company company = database.GetCompany();

        // 2. 비즈니스 로직: 이메일 도메인으로 직원/비직원 판별
        string emailDomain = newEmail.Split('@')[1];
        bool isEmployee = emailDomain == company.DomainName;
        UserType newType = isEmployee ? UserType.Employee : UserType.Customer;

        // 3. 비즈니스 로직: 직원 수 업데이트
        if (Type != newType)
        {
            int delta = newType == UserType.Employee ? 1 : -1;
            company.NumberOfEmployees += delta;
            database.SaveCompany(company);      // 외부 의존성
        }

        Email = newEmail;
        Type = newType;
        database.SaveUser(this);                // 외부 의존성
        messageBus.Publish(new EmailChanged(Email)); // 외부 의존성
    }
}
```

이 메서드는 비즈니스 로직(이메일 도메인 판별, 직원 수 계산)과 외부 의존성(DB, 메시지 버스)이 뒤섞여 있다.

---

## 3. 험블 객체 패턴(Humble Object Pattern)

### 3.1 핵심 아이디어

험블 객체 패턴은 **테스트하기 어려운 코드에서 비즈니스 로직을 추출**하여, 비즈니스 로직은 테스트하기 쉬운 곳에, 나머지는 테스트하기 어렵지만 단순한 곳("험블" 객체)에 둔다:

```
과도하게 복잡한 코드
    │
    ├── 비즈니스 로직 → 도메인 모델 (테스트하기 쉬움)
    │
    └── 외부 의존성 오케스트레이션 → 컨트롤러/험블 객체 (단순하여 테스트 불필요 또는 통합 테스트)
```

### 3.2 리팩터링 적용

```csharp
// Step 1: 비즈니스 로직을 도메인 모델로 추출
public class User
{
    public string Email { get; private set; }
    public UserType Type { get; private set; }

    // 순수한 비즈니스 로직 — 외부 의존성 없음
    public void ChangeEmail(string newEmail, string companyDomainName, int numberOfEmployees)
    {
        string emailDomain = newEmail.Split('@')[1];
        bool isEmployee = emailDomain == companyDomainName;
        UserType newType = isEmployee ? UserType.Employee : UserType.Customer;

        if (Type != newType)
        {
            int delta = newType == UserType.Employee ? 1 : -1;
            NumberOfEmployeesChanged = delta;
        }

        Email = newEmail;
        Type = newType;
    }

    public int NumberOfEmployeesChanged { get; private set; }
}
```

```csharp
// Step 2: 컨트롤러(험블 객체)가 오케스트레이션
public class UserController
{
    private readonly IDatabase _database;
    private readonly IMessageBus _messageBus;

    public void ChangeEmail(int userId, string newEmail)
    {
        // 1. 데이터 읽기
        User user = _database.GetUser(userId);
        Company company = _database.GetCompany();

        // 2. 비즈니스 결정 (도메인 모델에 위임)
        user.ChangeEmail(newEmail, company.DomainName, company.NumberOfEmployees);

        // 3. 결정 실행
        _database.SaveUser(user);
        company.NumberOfEmployees += user.NumberOfEmployeesChanged;
        _database.SaveCompany(company);
        _messageBus.Publish(new EmailChanged(user.Email));
    }
}
```

### 3.3 리팩터링 후 테스트

```csharp
// 도메인 모델 테스트: 출력/상태 기반, Mock 없음
[Fact]
public void Changing_email_from_corporate_to_non_corporate()
{
    var sut = new User(userId: 1, email: "user@mycorp.com", type: UserType.Employee);

    sut.ChangeEmail("user@gmail.com", "mycorp.com", 10);

    Assert.Equal("user@gmail.com", sut.Email);
    Assert.Equal(UserType.Customer, sut.Type);
    Assert.Equal(-1, sut.NumberOfEmployeesChanged);
}
```

Mock이 하나도 없다. 빠르고, 리팩터링에 강하고, 이해하기 쉽다.

> **핵심 통찰**: 험블 객체 패턴의 핵심은 "**비즈니스 로직은 외부 의존성을 모르게 하라**"이다. 도메인 모델은 결정만 내리고, 결정의 실행(DB 저장, 메시지 발행)은 컨트롤러에 맡긴다. 이렇게 하면 가장 중요한 코드(비즈니스 로직)를 가장 좋은 테스트(출력/상태 기반)로 검증할 수 있다.

---

## 4. 컨트롤러의 복잡도 관리

### 4.1 컨트롤러가 복잡해지는 경우

비즈니스 로직의 결정이 여러 단계에 걸쳐 외부 데이터에 의존하면, 컨트롤러가 복잡해질 수 있다:

```csharp
// 컨트롤러가 너무 복잡해진 경우
public void ChangeEmail(int userId, string newEmail)
{
    User user = _database.GetUser(userId);
    string emailDomain = newEmail.Split('@')[1];

    // DB 조회가 비즈니스 로직 중간에 끼어듦
    Company company = _database.GetCompanyByDomain(emailDomain);

    if (company != null)
    {
        user.AssignToCompany(company);
        // 또 다른 조회...
        var permissions = _database.GetPermissions(company.Id);
        user.GrantPermissions(permissions);
    }

    _database.SaveUser(user);
}
```

### 4.2 세 가지 선택지

| 선택지 | 장점 | 단점 |
|--------|------|------|
| 도메인 모델에 외부 의존성 주입 | 도메인 로직이 한 곳에 | 도메인 모델이 외부에 의존 (나쁜 설계) |
| 컨트롤러에서 모든 데이터를 미리 읽기 | 도메인 모델 순수 유지 | 성능 저하 (불필요한 데이터 조회) |
| **도메인 이벤트 사용** | 도메인 순수 + 필요 시 조회 | 약간의 복잡도 추가 |

### 4.3 도메인 이벤트(Domain Events) 접근법

도메인 모델이 결정 과정에서 "이 일이 일어났다"를 이벤트로 기록하면, 컨트롤러는 이벤트를 보고 필요한 외부 작업을 수행한다:

```csharp
public class User
{
    public List<IDomainEvent> DomainEvents { get; } = new();

    public void ChangeEmail(string newEmail, string companyDomainName, int numberOfEmployees)
    {
        // ... 비즈니스 로직 ...
        Email = newEmail;
        DomainEvents.Add(new EmailChangedEvent(newEmail));   // 이벤트 기록
    }
}
```

이렇게 하면 도메인 모델은 순수하게 유지되고, 컨트롤러는 이벤트를 소비하여 외부 작업을 수행한다.

---

## 5. 최적의 단위 테스트 커버리지

### 5.1 사분면별 테스트 전략

| 사분면 | 테스트 전략 | 커버리지 목표 |
|--------|-----------|-------------|
| **도메인 모델/알고리즘** | 단위 테스트 (출력/상태 기반) | **높음** |
| **Trivial 코드** | 테스트하지 않음 | **0%** |
| **컨트롤러** | 통합 테스트 (Chapter 8) | **핵심 경로만** |
| **과도하게 복잡한 코드** | 리팩터링으로 분해 후 위 전략 적용 | — |

### 5.2 조건부 로직의 테스트

비즈니스 규칙에 조건 분기가 많으면, 각 분기를 매개변수화 테스트로 커버한다:

```csharp
[Theory]
[InlineData("user@mycorp.com", "mycorp.com", UserType.Employee)]
[InlineData("user@gmail.com", "mycorp.com", UserType.Customer)]
public void Differentiates_a_corporate_email_from_non_corporate(
    string email, string companyDomain, UserType expectedType)
{
    var sut = new User(userId: 1, email: "old@example.com", type: UserType.Customer);

    sut.ChangeEmail(email, companyDomain, 10);

    Assert.Equal(expectedType, sut.Type);
}
```

---

## 6. 리팩터링 프로세스 정리

전체 리팩터링 과정을 단계별로 정리하면:

```
1. "과도하게 복잡한 코드"를 식별한다
   (비즈니스 로직 + 많은 협력자가 한 곳에)

2. 비즈니스 로직을 도메인 모델로 추출한다
   (외부 의존성 제거 → 순수 함수 또는 상태 변경만)

3. 오케스트레이션을 컨트롤러(험블 객체)로 이동한다
   (데이터 읽기 → 도메인 호출 → 결과 실행)

4. 도메인 모델에 단위 테스트를 작성한다
   (출력/상태 기반, Mock 없음)

5. 컨트롤러의 핵심 경로를 통합 테스트로 검증한다
   (Chapter 8에서 다룸)
```

> **핵심 통찰**: 테스트의 가치는 프로덕션 코드의 **설계에 크게 의존**한다. 나쁜 설계(비즈니스 로직과 외부 의존성의 혼합)에서는 좋은 테스트를 작성할 수 없다. "코드를 테스트하기 어렵다"는 것은 대부분 "코드의 설계를 개선해야 한다"는 신호다.

---

## 요약

- 프로덕션 코드는 **도메인 유의성**과 **협력자 수**에 따라 네 가지 유형으로 분류된다.
- **도메인 모델/알고리즘**이 테스트 가치가 가장 높다. **Trivial 코드**는 테스트하지 않는다.
- **과도하게 복잡한 코드**(비즈니스 로직 + 많은 협력자)는 **험블 객체 패턴**으로 분해한다.
- 험블 객체 패턴: 비즈니스 로직은 **도메인 모델**(순수)로, 오케스트레이션은 **컨트롤러**(험블)로.
- 도메인 모델은 **출력/상태 기반** 단위 테스트로, 컨트롤러는 **통합 테스트**로 검증한다.
- **도메인 이벤트**를 활용하면 도메인 모델의 순수성을 유지하면서도 컨트롤러의 복잡도를 관리할 수 있다.
- "코드를 테스트하기 어렵다"는 것은 대부분 "코드의 **설계를 개선해야 한다**"는 신호다.

