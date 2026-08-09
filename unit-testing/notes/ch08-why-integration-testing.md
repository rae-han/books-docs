# Chapter 8: Why Integration Testing? (왜 통합 테스트인가?)

## 핵심 질문

단위 테스트만으로는 왜 충분하지 않은가? 통합 테스트는 어떤 역할을 하며, **얼마나 많은** 통합 테스트를 작성해야 하는가? 관리 의존성과 비관리 의존성을 통합 테스트에서 어떻게 다르게 다루는가?

---

## 1. 통합 테스트의 역할

### 1.1 단위 테스트의 한계

Chapter 7에서 코드를 네 가지 유형으로 분류했다:

- **도메인 모델/알고리즘** → 단위 테스트
- **컨트롤러** → **통합 테스트**
- Trivial 코드 → 테스트 없음
- 과도하게 복잡한 코드 → 리팩터링으로 분해

단위 테스트는 도메인 모델의 비즈니스 로직을 검증하지만, **컨트롤러가 이 모든 것을 올바르게 연결하는지**는 검증하지 못한다:

```
데이터 읽기 → 도메인 호출 → 결과 저장 → 이벤트 발행
     ↑            ↑            ↑           ↑
  이 연결이 올바른지를 검증하는 것이 통합 테스트의 역할
```

### 1.2 통합 테스트의 정의 (재확인)

Chapter 2에서 정의한 것을 상기하면, 단위 테스트의 세 가지 속성 중 **하나라도 충족하지 못하면** 통합 테스트다:

1. 작은 코드 조각을 검증한다
2. 빠르게 실행된다
3. 격리된 방식으로 실행된다

통합 테스트는 보통 프로세스 외부 의존성(DB, 파일 시스템 등)을 사용하므로 느리고, 여러 컴포넌트를 한 번에 검증하므로 범위가 넓다.

---

## 2. 어떤 통합 테스트를 작성할 것인가?

### 2.1 통합 테스트의 수

Khorikov의 가이드라인:

```
단위 테스트 : 통합 테스트 = 다수 : 소수

도메인 모델의 비즈니스 로직 → 단위 테스트로 철저히 검증 (분기마다)
컨트롤러의 연결 → 통합 테스트로 핵심 경로만 검증 (happy path + 주요 에러)
```

### 2.2 통합 테스트에서 검증하는 것

통합 테스트의 목적은 컨트롤러가 다음을 올바르게 수행하는지 확인하는 것이다:

1. **외부 데이터 조회**가 올바른가?
2. **도메인 모델 호출**이 올바른 순서와 매개변수로 이루어지는가?
3. **결과 저장**이 올바른가? (관리 의존성)
4. **외부 통신**이 올바른가? (비관리 의존성)

### 2.3 예제: 이메일 변경의 통합 테스트

```csharp
[Fact]
public void Changing_email_from_corporate_to_non_corporate()
{
    // Arrange
    var db = new TestDatabase();
    db.SeedUser(userId: 1, email: "user@mycorp.com", type: UserType.Employee);
    db.SeedCompany(domainName: "mycorp.com", numberOfEmployees: 10);

    var messageBusMock = new Mock<IMessageBus>();     // 비관리 의존성은 Mock
    var sut = new UserController(db.Context, messageBusMock.Object);

    // Act
    sut.ChangeEmail(userId: 1, newEmail: "user@gmail.com");

    // Assert: 관리 의존성(DB)은 상태 검증
    var user = db.Context.Users.Find(1);
    Assert.Equal("user@gmail.com", user.Email);
    Assert.Equal(UserType.Customer, user.Type);

    var company = db.Context.Companies.First();
    Assert.Equal(9, company.NumberOfEmployees);

    // Assert: 비관리 의존성(메시지 버스)은 상호작용 검증
    messageBusMock.Verify(
        x => x.Publish(It.Is<EmailChanged>(e => e.Email == "user@gmail.com")),
        Times.Once);
}
```

> **핵심 통찰**: 통합 테스트에서 **관리 의존성(DB)은 실제 인스턴스**를 사용하고, **비관리 의존성(메시지 버스)은 Mock**을 사용한다. 이것이 Chapter 5에서 확립된 원칙의 실전 적용이다. DB의 쿼리 방식은 구현 세부사항이므로 상태(결과)를 검증하고, 메시지 버스로의 발행은 외부에서 관찰 가능한 동작이므로 상호작용을 검증한다.

---

## 3. 관리 의존성: 실제 DB 사용

### 3.1 왜 DB를 Mock하면 안 되는가?

DB를 Mock하면:

| 문제 | 설명 |
|------|------|
| **리팩터링 내성 저하** | SQL 쿼리나 ORM 호출 방식이 바뀌면 테스트가 깨진다 |
| **회귀 방지 부족** | 실제 DB와의 상호작용에서 발생하는 버그를 잡지 못한다 |
| **거짓 자신감** | Mock은 통과하지만 실제 DB에서 실패하는 경우 |

### 3.2 테스트 DB 관리

실제 DB를 사용하되, 테스트 간 격리를 보장해야 한다:

```csharp
// 트랜잭션으로 격리
public class IntegrationTest : IDisposable
{
    protected readonly TestDatabase Database;

    public IntegrationTest()
    {
        Database = new TestDatabase();
        Database.BeginTransaction();           // 테스트 시작 시 트랜잭션 시작
    }

    public void Dispose()
    {
        Database.RollbackTransaction();        // 테스트 종료 시 롤백
        Database.Dispose();
    }
}
```

또는 각 테스트 전에 데이터를 정리하는 방식:

```csharp
// 데이터 초기화로 격리
public IntegrationTest()
{
    Database = new TestDatabase();
    Database.CleanUp();                        // 이전 데이터 삭제
}
```

Khorikov는 **테스트 시작 시 데이터 정리** 방식을 선호한다. 트랜잭션 롤백은 때때로 프로덕션 동작(트랜잭션 커밋)을 정확히 반영하지 못하기 때문이다.

---

## 4. 비관리 의존성: Mock 사용

### 4.1 Mock의 올바른 사용

비관리 의존성(메시지 버스, SMTP, 외부 API)은 Mock으로 대체하고 **상호작용을 검증**한다:

```csharp
// 올바른 Mock 사용: 비관리 의존성
messageBusMock.Verify(
    x => x.Publish(It.Is<EmailChanged>(e =>
        e.Email == "user@gmail.com" &&
        e.OldEmail == "user@mycorp.com")),
    Times.Once);
```

### 4.2 Mock 검증의 범위

Mock으로 검증할 때는 **메시지의 구조와 내용까지** 확인해야 한다. 다른 시스템이 이 메시지를 소비하기 때문이다:

```csharp
// 불충분한 검증
messageBusMock.Verify(x => x.Publish(It.IsAny<EmailChanged>()), Times.Once);
// → 이벤트가 발행되었다는 것만 확인. 내용은 모름

// 충분한 검증
messageBusMock.Verify(x => x.Publish(
    It.Is<EmailChanged>(e =>
        e.Email == "user@gmail.com" &&
        e.UserId == 1)),
    Times.Once);
// → 이벤트의 내용까지 확인
```

---

## 5. 통합 테스트의 계층

### 5.1 인터페이스 사용에 대한 입장

Khorikov는 불필요한 인터페이스를 만들지 말라고 주장한다:

| 경우 | 인터페이스 필요? |
|------|---------------|
| 관리 의존성 (전용 DB) | **아니오** — 구현이 하나뿐이므로 불필요 |
| 비관리 의존성 (메시지 버스) | **예** — Mock으로 대체해야 하므로 |

인터페이스는 **구현이 둘 이상이거나 Mock이 필요할 때**만 만든다. "테스트를 위해" 인터페이스를 만드는 것은 과도한 추상화다.

### 5.2 로깅은 어떻게 테스트하는가?

로깅은 특수한 경우다:

- **지원 로깅(*Support logging — 개발팀이 프로덕션 문제를 진단하기 위해 사용하는 로그*)**: 구현 세부사항이므로 테스트하지 않는다
- **진단 로깅(*Diagnostic logging — 외부 시스템이나 운영팀에게 비즈니스적으로 의미 있는 이벤트를 알리는 로그*)**: 관찰 가능한 동작이므로 테스트할 수 있다 (비관리 의존성처럼 취급)

---

## 6. 통합 테스트 모범 사례

### 6.1 가이드라인 정리

| 원칙 | 설명 |
|------|------|
| **핵심 경로(happy path)에 집중** | 모든 경로를 통합 테스트할 필요 없음. 비즈니스 분기는 단위 테스트로 |
| **관리 의존성은 실제 사용** | DB를 Mock하지 말라 |
| **비관리 의존성은 Mock** | 메시지 버스, 외부 API는 Mock으로 |
| **테스트 간 격리 보장** | DB 상태 초기화 또는 트랜잭션 롤백 |
| **최소한의 통합 테스트** | 컨트롤러당 1-3개. 연결이 올바른지만 확인 |

### 6.2 테스트 전략 전체 그림

```
┌─────────────────────────────────────────┐
│          E2E 테스트 (극소수)              │
│    전체 시스템 동작 확인                   │
├─────────────────────────────────────────┤
│       통합 테스트 (소수)                  │
│    컨트롤러 연결 확인                     │
│    관리 의존성: 실제 DB                   │
│    비관리 의존성: Mock                    │
├─────────────────────────────────────────┤
│       단위 테스트 (다수)                  │
│    도메인 모델/알고리즘 검증              │
│    출력/상태 기반, Mock 없음              │
└─────────────────────────────────────────┘
```

> **핵심 통찰**: 통합 테스트는 "**모든 것이 올바르게 연결되어 있는가?**"를 검증한다. 비즈니스 로직의 세부 분기는 단위 테스트가 담당하고, 통합 테스트는 컨트롤러가 데이터를 올바르게 읽고, 도메인을 호출하고, 결과를 저장하고, 이벤트를 발행하는 **전체 흐름**을 검증한다.

---

## 요약

- **단위 테스트만으로는 충분하지 않다**. 컨트롤러가 도메인 모델, DB, 외부 시스템을 올바르게 연결하는지는 통합 테스트로 검증해야 한다.
- 통합 테스트는 **핵심 경로(happy path)**에 집중하여 소수만 작성한다. 분기 검증은 단위 테스트의 영역.
- **관리 의존성(전용 DB)은 실제 인스턴스**를 사용하고, **비관리 의존성(메시지 버스)은 Mock**을 사용한다.
- DB를 Mock하면 리팩터링 내성이 떨어지고 회귀 방지도 부족해진다. **실제 DB로 테스트**하라.
- 테스트 간 DB 상태 격리를 보장하라. **테스트 시작 시 데이터 정리** 방식이 권장된다.
- 인터페이스는 Mock이 필요한 **비관리 의존성에만** 만든다.

