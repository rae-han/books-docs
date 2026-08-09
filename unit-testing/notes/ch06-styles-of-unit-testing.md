# Chapter 6: Styles of Unit Testing (단위 테스트 스타일)

## 핵심 질문

단위 테스트에는 어떤 스타일이 있으며, 각 스타일의 장단점은 무엇인가? 네 가지 기둥에 비추어 어떤 스타일이 가장 우수하며, **함수형 아키텍처(functional architecture)**는 왜 테스트하기 좋은 코드를 만드는가?

---

## 1. 세 가지 테스트 스타일

### 1.1 출력 기반 테스트(Output-based Testing)

SUT에 입력을 넣고, **반환값(출력)**을 검증한다. SUT의 부수 효과(side effect)가 없다:

```csharp
// 출력 기반 테스트
[Fact]
public void Discount_of_two_products()
{
    var product1 = new Product("Hand wash");
    var product2 = new Product("Shampoo");

    decimal discount = PriceEngine.CalculateDiscount(product1, product2);

    Assert.Equal(0.02m, discount);
}
```

`CalculateDiscount`는 입력(두 제품)을 받아 출력(할인율)을 반환할 뿐이다. 외부 상태를 변경하지 않는다.

### 1.2 상태 기반 테스트(State-based Testing)

SUT의 동작 후 **상태 변화**를 검증한다:

```csharp
// 상태 기반 테스트
[Fact]
public void Adding_a_product_to_an_order()
{
    var product = new Product("Hand wash");
    var order = new Order();

    order.AddProduct(product);

    Assert.Equal(1, order.Products.Count);              // 상태 변화 검증
    Assert.Contains(product, order.Products);
}
```

`AddProduct` 호출 후 `order.Products`의 상태가 변했는지를 검증한다.

### 1.3 커뮤니케이션 기반 테스트(Communication-based Testing)

SUT가 협력자와 **올바르게 상호작용했는지**를 검증한다. Mock을 사용한다:

```csharp
// 커뮤니케이션 기반 테스트
[Fact]
public void Sending_a_greetings_email()
{
    var emailMock = new Mock<IEmailGateway>();
    var sut = new Controller(emailMock.Object);

    sut.GreetUser("user@example.com");

    emailMock.Verify(                                   // 상호작용 검증
        x => x.SendGreetingsEmail("user@example.com"),
        Times.Once);
}
```

### 1.4 세 스타일 비교

| 기준 | 출력 기반 | 상태 기반 | 커뮤니케이션 기반 |
|------|----------|----------|----------------|
| **검증 대상** | 반환값 | 상태 변화 | 메서드 호출 |
| **의존 도구** | 없음 | 없음 | Mock 프레임워크 |
| **예시** | `Assert.Equal(0.02m, discount)` | `Assert.Equal(1, order.Count)` | `mock.Verify(...)` |

---

## 2. 네 가지 기둥으로 스타일 비교

### 2.1 종합 비교

| 기둥 | 출력 기반 | 상태 기반 | 커뮤니케이션 기반 |
|------|----------|----------|----------------|
| **회귀 방지** | 동일 | 동일 | 동일 |
| **리팩터링 내성** | **최고** | 좋음 | **낮음** |
| **유지보수성** | **최고** | 중간 | 낮음 |
| **빠른 피드백** | 동일 | 동일 | 동일 |

### 2.2 출력 기반이 최고인 이유

**리팩터링 내성**: 출력 기반 테스트는 SUT의 반환값만 검증하므로, 내부 구현이 어떻게 바뀌든 결과만 같으면 통과한다. 구현 세부사항에 결합될 여지가 가장 적다.

**유지보수성**: Assert가 간결하고 직관적이다. Mock 설정 코드가 필요 없고, 상태를 탐색할 필요도 없다.

```csharp
// 출력 기반: 한 줄 Assert
Assert.Equal(0.02m, discount);

// 상태 기반: 여러 줄의 상태 탐색
Assert.Equal(1, order.Products.Count);
Assert.Contains(product, order.Products);
Assert.Equal("Hand wash", order.Products[0].Name);

// 커뮤니케이션 기반: Mock 설정 + 검증
emailMock.Verify(x => x.SendGreetingsEmail("user@example.com"), Times.Once);
```

### 2.3 커뮤니케이션 기반의 약점

커뮤니케이션 기반 테스트는 **리팩터링 내성이 가장 낮다**. Mock으로 검증하는 상호작용이 구현 세부사항인 경우가 많기 때문이다. Chapter 5에서 다룬 것처럼, 비관리 의존성과의 외부 통신에만 사용해야 한다.

> **핵심 통찰**: **출력 기반 테스트가 가장 우수한 스타일**이다. 리팩터링 내성과 유지보수성 모두에서 최고점을 받는다. 하지만 모든 코드를 출력 기반으로 테스트할 수는 없다. 부수 효과가 없는 코드에만 적용 가능하다. 이 제약을 극복하는 방법이 **함수형 아키텍처**다.

---

## 3. 함수형 아키텍처(Functional Architecture)

### 3.1 함수형 프로그래밍과 출력 기반 테스트

출력 기반 테스트를 최대한 활용하려면, 코드를 **부수 효과 없는 순수 함수**로 작성해야 한다. 함수형 아키텍처는 이를 체계적으로 가능하게 한다.

### 3.2 함수형 핵심, 가변 셸

함수형 아키텍처의 핵심 패턴:

```
┌────────────────────────────────┐
│        가변 셸 (Mutable Shell)    │
│  - 입력 수집 (DB, 파일 읽기)       │
│  - 결정을 실행 (DB 쓰기, 이메일)   │
│                                │
│  ┌────────────────────────┐    │
│  │  함수형 핵심              │    │
│  │  (Functional Core)      │    │
│  │                        │    │
│  │  - 입력 → 결정 (순수 함수) │    │
│  │  - 부수 효과 없음          │    │
│  │  - 테스트하기 쉬움         │    │
│  └────────────────────────┘    │
└────────────────────────────────┘
```

- **함수형 핵심(Functional Core)**: 비즈니스 로직을 담당한다. 입력을 받아 **결정(decision)**을 내리지만, 부수 효과는 일으키지 않는다. 순수 함수로만 구성된다.
- **가변 셸(Mutable Shell)**: 외부 세계와 상호작용한다. 데이터를 읽어 함수형 핵심에 전달하고, 핵심이 내린 결정을 실행한다.

### 3.3 예제: 감사 시스템(Audit System)

파일에 방문자 로그를 기록하는 시스템을 생각하자:

```csharp
// 나쁜 예: 비즈니스 로직과 부수 효과가 섞임
public class AuditManager
{
    private readonly string _directoryName;
    private readonly int _maxEntriesPerFile;

    public void AddRecord(string visitorName, DateTime timeOfVisit)
    {
        string[] filePaths = Directory.GetFiles(_directoryName);    // 부수 효과: 파일 읽기
        // ... 비즈니스 로직: 어떤 파일에 쓸지 결정 ...
        File.AppendAllText(filePath, newRecord);                   // 부수 효과: 파일 쓰기
    }
}
```

이 코드는 테스트하기 어렵다 — 파일 시스템에 의존하기 때문이다.

```csharp
// 좋은 예: 함수형 핵심으로 분리
public class AuditManager    // 함수형 핵심 — 순수 함수
{
    private readonly int _maxEntriesPerFile;

    public FileUpdate AddRecord(
        FileContent[] existingFiles,           // 입력: 현재 파일 상태
        string visitorName,
        DateTime timeOfVisit)
    {
        // 비즈니스 로직만: 어떤 파일에 무엇을 쓸지 결정
        // FileUpdate 객체를 반환 (부수 효과 없음)
    }
}

public class Persister       // 가변 셸 — 부수 효과 담당
{
    public FileContent[] ReadDirectory(string directoryName) { /* ... */ }
    public void ApplyUpdate(FileUpdate update) { /* ... */ }
}

public class ApplicationService   // 오케스트레이터
{
    public void AddRecord(string visitorName, DateTime timeOfVisit)
    {
        FileContent[] files = _persister.ReadDirectory(_directoryName);
        FileUpdate update = _auditManager.AddRecord(files, visitorName, timeOfVisit);
        _persister.ApplyUpdate(update);
    }
}
```

이제 `AuditManager`는 순수 함수다. 출력 기반 테스트로 검증할 수 있다:

```csharp
[Fact]
public void A_new_file_is_created_when_current_file_overflows()
{
    var sut = new AuditManager(maxEntriesPerFile: 3);
    var existingFiles = new FileContent[]
    {
        new("audit_001.txt", new[] { "Peter; 2019-04-06", "Jane; 2019-04-06", "Jack; 2019-04-06" })
    };

    FileUpdate update = sut.AddRecord(existingFiles, "Alice", DateTime.Parse("2019-04-06"));

    Assert.Equal("audit_002.txt", update.FileName);
    Assert.Equal("Alice; 2019-04-06", update.NewContent);
}
```

파일 시스템에 접근하지 않는다. 빠르고, 결정적이고, 유지보수가 쉽다.

> **핵심 통찰**: 함수형 아키텍처는 **비즈니스 로직(결정)과 부수 효과(실행)를 분리**한다. 비즈니스 로직은 순수 함수가 되어 출력 기반 테스트로 검증할 수 있고, 부수 효과는 가변 셸로 밀려나 통합 테스트에서 검증한다. 이것이 테스트하기 좋은 코드를 만드는 핵심 전략이다.

---

## 4. 함수형 아키텍처의 한계

### 4.1 모든 곳에 적용할 수 없다

함수형 아키텍처가 항상 실용적인 것은 아니다:

| 상황 | 함수형 아키텍처 적용 가능? |
|------|------------------------|
| 비즈니스 로직이 단순하고 독립적 | **적합** |
| 결정 과정에서 외부 데이터를 추가로 읽어야 함 | **어려움** — 가변 셸이 복잡해짐 |
| 성능이 중요하여 모든 데이터를 미리 읽을 수 없음 | **비실용적** |
| 레거시 코드베이스 | **점진적 도입** 필요 |

### 4.2 성능 트레이드오프

함수형 핵심에 모든 데이터를 미리 전달하려면, 가변 셸이 **필요한 것보다 더 많은 데이터를 읽어야** 할 수 있다. 이것은 성능 저하를 가져올 수 있다.

이 경우 Khorikov는 **전략적으로 타협**할 것을 권한다:
- 핵심 비즈니스 로직은 가능한 한 함수형으로 유지
- 성능이 중요한 부분은 전통적인 방식(상태 기반 테스트)으로 검증

---

## 5. 육각형 아키텍처 vs 함수형 아키텍처

| 측면 | 육각형 아키텍처 | 함수형 아키텍처 |
|------|---------------|---------------|
| **부수 효과 위치** | 도메인 모델 외부 (애플리케이션 서비스) | 함수형 핵심 외부 (가변 셸) |
| **도메인 모델** | 상태를 변경할 수 있음 | 부수 효과 없음 (순수 함수) |
| **테스트 스타일** | 주로 상태 기반 | 주로 출력 기반 |
| **관계** | 함수형 아키텍처는 육각형의 **더 엄격한 버전** |

함수형 아키텍처는 육각형 아키텍처의 원칙(의존성 역전, 도메인 분리)을 따르면서, **부수 효과를 완전히 핵심 밖으로** 밀어낸다.

---

## 요약

- 단위 테스트 스타일: **출력 기반**(반환값 검증), **상태 기반**(상태 변화 검증), **커뮤니케이션 기반**(상호작용 검증).
- 네 가지 기둥에 비추어 **출력 기반 테스트가 가장 우수**하다. 리팩터링 내성과 유지보수성 모두에서 최고.
- 커뮤니케이션 기반(Mock) 테스트는 리팩터링 내성이 **가장 낮다**. 비관리 의존성에만 제한적으로 사용해야 한다.
- **함수형 아키텍처**는 비즈니스 로직을 순수 함수(함수형 핵심)로 분리하여 출력 기반 테스트를 최대한 활용할 수 있게 한다.
- 함수형 핵심 + 가변 셸 패턴: **결정은 순수 함수로, 실행은 가변 셸로**.
- 함수형 아키텍처는 모든 곳에 적용할 수 없다. **성능 트레이드오프**와 실용성을 고려해야 한다.

