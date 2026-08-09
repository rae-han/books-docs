# Chapter 10: Testing the Database (데이터베이스 테스트)

## 핵심 질문

데이터베이스를 포함하는 통합 테스트를 어떻게 작성하는가? DB 스키마 관리, 트랜잭션, 테스트 데이터 생명주기는 어떻게 처리하며, **리포지토리 테스트**와 **컨트롤러 통합 테스트**는 어떻게 다른가?

---

## 1. 데이터베이스 테스트의 전제 조건

### 1.1 DB를 형상 관리하라

프로덕션 코드가 Git으로 관리되듯, **DB 스키마도 형상 관리**해야 한다:

- **마이그레이션 기반 접근법**: 스키마 변경을 마이그레이션 스크립트로 관리 (Flyway, Liquibase, EF Core Migrations 등)
- 마이그레이션 스크립트는 **소스 코드의 일부**로 취급한다
- 참조 데이터(*Reference data — 애플리케이션이 동작하기 위해 미리 존재해야 하는 데이터. 상태 코드, 카테고리 등*)도 마이그레이션에 포함한다

```
프로젝트 저장소
├── src/
│   ├── Domain/
│   ├── Application/
│   └── Infrastructure/
├── tests/
│   ├── UnitTests/
│   └── IntegrationTests/
└── migrations/           ← DB 스키마도 소스 관리
    ├── V001_CreateUsers.sql
    ├── V002_AddCompanyTable.sql
    └── V003_AddEmailIndex.sql
```

### 1.2 모든 개발자에게 별도 DB 인스턴스

통합 테스트의 격리를 보장하려면:

| 접근법 | 장점 | 단점 |
|--------|------|------|
| 공유 DB 인스턴스 | 설정 간단 | 개발자 간 충돌, 테스트 불안정 |
| **개발자별 별도 인스턴스** | 완전한 격리 | 인스턴스 관리 비용 |
| 인메모리 DB (SQLite 등) | 빠르고 격리 쉬움 | 프로덕션 DB와 동작 차이 |

Khorikov는 **개발자별 별도 DB 인스턴스**를 권장한다. 인메모리 DB는 프로덕션 DB와 동작이 달라(트랜잭션, 제약 조건, 함수 등) 거짓 자신감을 줄 수 있다.

---

## 2. 테스트 데이터 생명주기

### 2.1 네 가지 방식

| 방식 | 설명 | Khorikov 권장 |
|------|------|-------------|
| **테스트 시작 시 정리** | 각 테스트 시작 전에 이전 데이터 삭제 | **권장** |
| 테스트 종료 시 정리 | 각 테스트 후에 데이터 삭제 | 비권장 (실패 시 정리 안 됨) |
| 트랜잭션 래핑 | 테스트를 트랜잭션으로 감싸고 롤백 | 비권장 (프로덕션 동작과 다름) |
| 인메모리 DB | 매번 새로 생성 | 비권장 (DB 차이) |

### 2.2 테스트 시작 시 정리 구현

```csharp
public abstract class IntegrationTestBase
{
    protected readonly TestDatabase Database;

    protected IntegrationTestBase()
    {
        Database = new TestDatabase();
        CleanDatabase();                           // 모든 테스트 전에 실행
    }

    private void CleanDatabase()
    {
        // 참조 무결성 순서를 고려하여 삭제
        Database.Execute("DELETE FROM OrderItems");
        Database.Execute("DELETE FROM Orders");
        Database.Execute("DELETE FROM Users");
        Database.Execute("DELETE FROM Companies");
    }
}
```

### 2.3 왜 트랜잭션 래핑을 피하는가?

```csharp
// 트랜잭션 래핑 방식 — 비권장
[Fact]
public void Test()
{
    using var transaction = db.BeginTransaction();

    // ... 테스트 실행 ...

    transaction.Rollback();    // 항상 롤백
}
```

문제점:
- 프로덕션에서는 **커밋**하는데, 테스트에서는 **롤백**한다 — 동작이 다르다
- 프로덕션에서 커밋 시 발생하는 제약 조건 위반을 테스트에서 잡지 못한다
- 암묵적 트랜잭션과 명시적 트랜잭션의 동작 차이가 버그를 숨길 수 있다

---

## 3. 테스트 데이터 준비

### 3.1 Object Mother 패턴

테스트 데이터를 생성하는 팩토리 메서드를 모아둔 클래스:

```csharp
public static class TestDataFactory
{
    public static User CreateUser(
        string email = "user@example.com",
        UserType type = UserType.Customer)
    {
        return new User(
            userId: Guid.NewGuid(),
            email: email,
            type: type);
    }

    public static Company CreateCompany(
        string domainName = "mycorp.com",
        int numberOfEmployees = 10)
    {
        return new Company(domainName, numberOfEmployees);
    }
}
```

```csharp
// 테스트에서 사용
[Fact]
public void Changing_email_updates_type()
{
    var user = TestDataFactory.CreateUser(email: "user@mycorp.com", type: UserType.Employee);
    Database.Save(user);
    // ...
}
```

### 3.2 Builder 패턴

더 복잡한 데이터 구성이 필요할 때:

```csharp
public class UserBuilder
{
    private string _email = "user@example.com";
    private UserType _type = UserType.Customer;

    public UserBuilder WithEmail(string email) { _email = email; return this; }
    public UserBuilder WithType(UserType type) { _type = type; return this; }

    public User Build() => new User(Guid.NewGuid(), _email, _type);
}

// 사용
var user = new UserBuilder()
    .WithEmail("admin@mycorp.com")
    .WithType(UserType.Employee)
    .Build();
```

> **핵심 통찰**: 테스트 데이터 생성을 **팩토리 메서드나 빌더 패턴**으로 중앙화하라. 테스트마다 데이터를 인라인으로 생성하면 중복이 많아지고, 스키마 변경 시 모든 테스트를 수정해야 한다.

---

## 4. 리포지토리 테스트

### 4.1 리포지토리를 별도로 테스트해야 하는가?

Khorikov의 답: **대부분의 경우 별도로 테스트하지 않는다**.

```
컨트롤러 통합 테스트
├── 컨트롤러 호출
│   ├── 리포지토리를 통한 DB 읽기     ← 자연스럽게 검증됨
│   ├── 도메인 모델 호출
│   └── 리포지토리를 통한 DB 쓰기     ← 자연스럽게 검증됨
│
└── 결과 검증 (DB 상태 + 외부 통신)
```

컨트롤러의 통합 테스트가 리포지토리의 읽기/쓰기를 **자연스럽게 포함**하므로, 리포지토리만 별도로 테스트할 필요가 거의 없다.

### 4.2 리포지토리를 별도로 테스트하는 경우

다만, 리포지토리에 **복잡한 쿼리 로직**이 있으면 별도 테스트가 가치 있다:

```csharp
// 복잡한 쿼리가 있는 리포지토리
public class OrderRepository
{
    public IReadOnlyList<Order> GetOrdersByDateRange(
        DateTime start, DateTime end, OrderStatus? status = null)
    {
        var query = _context.Orders
            .Where(o => o.CreatedAt >= start && o.CreatedAt <= end);

        if (status.HasValue)
            query = query.Where(o => o.Status == status.Value);

        return query
            .Include(o => o.Items)
            .OrderByDescending(o => o.CreatedAt)
            .ToList();
    }
}
```

이 경우 다양한 필터 조합을 검증하는 별도 통합 테스트가 의미 있다.

---

## 5. ORM 관련 주의사항

### 5.1 지연 로딩(Lazy Loading)과 테스트

ORM의 지연 로딩은 테스트에서 거짓 양성/음성을 만들 수 있다:

```csharp
// 테스트에서 동작하지만 프로덕션에서 실패하는 경우
[Fact]
public void Test()
{
    var order = db.Orders.Find(orderId);
    // 테스트: 같은 DbContext에서 관련 데이터가 이미 추적 중 → Items 로딩 성공
    // 프로덕션: 다른 요청, Items가 로딩되지 않음 → NullReferenceException
    Assert.NotEmpty(order.Items);
}
```

### 5.2 해결: 프로덕션과 동일한 조건

- 테스트에서도 프로덕션과 **동일한 방식으로 데이터를 로드**하라
- Arrange에서 데이터를 저장한 후, **DbContext를 새로 생성**하여 Act에서 사용하라

```csharp
[Fact]
public void Test()
{
    // Arrange: 데이터 저장
    using (var arrangeContext = new AppDbContext(connectionString))
    {
        arrangeContext.Orders.Add(order);
        arrangeContext.SaveChanges();
    }

    // Act: 새 컨텍스트로 조회 (프로덕션과 동일)
    using (var actContext = new AppDbContext(connectionString))
    {
        var sut = new OrderController(actContext);
        // ...
    }
}
```

> **핵심 통찰**: 통합 테스트에서 **프로덕션과 동일한 조건**을 만들어야 한다. ORM 캐시, 지연 로딩, 변경 추적 등이 테스트에서는 작동하지만 프로덕션에서 실패하는 미묘한 버그를 숨길 수 있다. Arrange와 Act에서 **별도의 DbContext를 사용**하는 것이 가장 확실한 방법이다.

---

## 6. 테스트 구성 정리

### 6.1 통합 테스트 프로젝트 구조

```
IntegrationTests/
├── Infrastructure/
│   ├── TestDatabase.cs           — DB 연결/정리
│   ├── IntegrationTestBase.cs    — 기본 클래스 (정리, 팩토리)
│   └── TestDataFactory.cs        — Object Mother
├── Controllers/
│   ├── UserControllerTests.cs
│   └── OrderControllerTests.cs
└── Repositories/                  — 복잡한 쿼리만
    └── OrderRepositoryTests.cs
```

### 6.2 테스트 격리 체크리스트

| 체크 항목 | 설명 |
|----------|------|
| 각 테스트가 독립적으로 실행 가능한가? | 테스트 순서에 의존하지 않아야 함 |
| DB 상태가 테스트 시작 시 정리되는가? | 이전 테스트의 잔여 데이터 없어야 함 |
| Arrange/Act에서 별도 DbContext를 사용하는가? | ORM 캐시 문제 방지 |
| 참조 데이터가 올바르게 준비되는가? | 마이그레이션 또는 시드로 |

---

## 요약

- DB 스키마를 **형상 관리**(마이그레이션)하라. DB도 소스 코드의 일부다.
- 개발자별 **별도 DB 인스턴스**를 사용하라. 인메모리 DB는 프로덕션과 동작이 다르다.
- 테스트 데이터 정리는 **테스트 시작 시** 수행하라. 트랜잭션 래핑은 프로덕션 동작과 다르다.
- **Object Mother** 또는 **Builder** 패턴으로 테스트 데이터 생성을 중앙화하라.
- 리포지토리는 대부분 **컨트롤러 통합 테스트에서 자연스럽게 검증**된다. 복잡한 쿼리만 별도 테스트.
- ORM의 지연 로딩/캐시 문제를 피하기 위해, Arrange와 Act에서 **별도 DbContext**를 사용하라.

