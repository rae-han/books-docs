# Chapter 2: What is a Unit Test? (단위 테스트란 무엇인가?)

## 핵심 질문

"단위(unit)"란 무엇인가? 이 질문에 대한 답이 다르면 테스트 작성 방식 전체가 달라진다. Classical 학파와 London 학파는 왜 다른 방식으로 테스트를 작성하며, 어느 쪽이 더 나은가?

---

## 1. 단위 테스트의 정의

### 1.1 세 가지 속성

Khorikov는 단위 테스트를 다음 세 가지 속성으로 정의한다:

1. **작은 코드 조각(unit of code)을 검증한다**
2. **빠르게 실행된다**
3. **격리된 방식(isolated manner)으로 실행된다**

첫 두 속성은 대부분 동의한다. 논쟁은 세 번째 속성인 **"격리"의 의미**에서 갈린다. 이 "격리"를 어떻게 해석하느냐에 따라 두 학파가 나뉜다.

### 1.2 두 학파의 분기점

| | **London 학파** (Mockist) | **Classical 학파** (Detroit) |
|---|---|---|
| **격리 대상** | 테스트 대상 시스템(SUT(*System Under Test — 테스트 대상 시스템. 테스트에서 검증하려는 대상 클래스 또는 메서드를 가리킨다.*))을 **협력자(collaborator)로부터** 격리 | 테스트 **케이스들을 서로** 격리 |
| **Mock 사용** | 불변 의존성을 제외한 모든 의존성을 Mock으로 대체 | 공유 의존성만 Mock으로 대체 |
| **"단위"의 범위** | 하나의 클래스 | 하나의 동작(behavior) — 여러 클래스에 걸칠 수 있음 |
| **대표 인물** | Steve Freeman, Nat Pryce (GOOS 저자) | Kent Beck, Martin Fowler |

> **핵심 통찰**: "단위 테스트"라는 같은 용어를 사용하면서도 두 학파의 실천법은 매우 다르다. London 학파는 클래스를 격리하여 테스트하고, Classical 학파는 동작을 격리하여 테스트한다. 이 차이가 테스트 설계 전체에 영향을 미친다.

---

## 2. London 학파의 접근법

### 2.1 핵심 아이디어: 클래스 격리

London 학파에서 "격리"란, **테스트 대상 클래스를 모든 협력자로부터 분리**하는 것이다. 협력자는 Mock(또는 Stub)으로 대체한다.

예를 들어 온라인 상점의 구매 기능을 테스트한다고 하자:

```csharp
// 프로덕션 코드
public class Store
{
    public bool HasEnoughInventory(Product product, int quantity) { /* ... */ }
    public void RemoveInventory(Product product, int quantity) { /* ... */ }
}

public class Customer
{
    public bool Purchase(Store store, Product product, int quantity)
    {
        if (!store.HasEnoughInventory(product, quantity))
            return false;

        store.RemoveInventory(product, quantity);
        return true;
    }
}
```

London 학파 스타일의 테스트:

```csharp
[Fact]
public void Purchase_succeeds_when_enough_inventory()
{
    // Arrange
    var storeMock = new Mock<IStore>();                          // Store를 Mock으로 대체
    storeMock
        .Setup(x => x.HasEnoughInventory(Product.Shampoo, 5))
        .Returns(true);
    var customer = new Customer();

    // Act
    bool success = customer.Purchase(storeMock.Object, Product.Shampoo, 5);

    // Assert
    Assert.True(success);
    storeMock.Verify(                                           // Store의 메서드가 호출되었는지 검증
        x => x.RemoveInventory(Product.Shampoo, 5),
        Times.Once);
}
```

`Store`는 실제 객체가 아니라 Mock이다. `Customer`는 완전히 격리되어 테스트된다.

### 2.2 London 학파의 장점

| 장점 | 설명 |
|------|------|
| **세밀한 격리** | 테스트 실패 시 원인을 정확히 한 클래스로 좁힐 수 있다 |
| **간단한 테스트 구조** | 의존성 그래프가 복잡해도 Mock으로 끊어내면 테스트가 단순해진다 |
| **한 번에 한 클래스** | 클래스별로 테스트를 작성하므로 체계적으로 접근 가능하다 |

### 2.3 London 학파의 문제점

Khorikov는 London 학파의 접근법에 중요한 문제가 있다고 지적한다:

**문제 1: 구현 세부사항에 결합된다**

위 테스트에서 `storeMock.Verify(x => x.RemoveInventory(...))`는 Customer가 Store의 `RemoveInventory` 메서드를 호출하는지를 검증한다. 이것은 **구현 세부사항(implementation detail)**이다. Customer가 재고를 줄이는 방법이 바뀌면 — 예를 들어 다른 메서드를 호출하게 되면 — 동작은 올바른데도 테스트가 깨진다.

**문제 2: 과도한 명세(overspecification)**

Mock을 많이 사용할수록, 테스트는 "무엇을 하는가(what)"가 아니라 "어떻게 하는가(how)"를 검증하게 된다. 이는 **리팩터링 내성(resistance to refactoring)**을 떨어뜨린다.

> **핵심 통찰**: London 학파의 테스트는 **SUT가 협력자와 어떻게 상호작용하는지**를 검증하는 경향이 있다. 이것은 구현 세부사항이다. 구현이 바뀌면 동작이 올바르더라도 테스트가 깨진다. 이것은 Chapter 4에서 다루는 "좋은 테스트의 네 가지 기둥" 중 하나인 **리팩터링 내성**을 심각하게 훼손한다.

---

## 3. Classical 학파의 접근법

### 3.1 핵심 아이디어: 테스트 간 격리

Classical 학파에서 "격리"란, **테스트 케이스들이 서로 영향을 주지 않도록** 하는 것이다. 클래스를 격리하는 것이 아니라, 테스트 실행이 다른 테스트의 결과에 영향을 미치지 않도록 한다.

따라서 **공유 의존성(shared dependency)**만 격리하면 된다. 공유 의존성이란 테스트 간에 상태를 공유하는 의존성이다 — 예를 들어 데이터베이스, 파일 시스템, 정적 필드 등.

같은 예제를 Classical 학파로 작성하면:

```csharp
[Fact]
public void Purchase_succeeds_when_enough_inventory()
{
    // Arrange
    var store = new Store();                                    // 실제 Store 객체 사용
    store.AddInventory(Product.Shampoo, 10);
    var customer = new Customer();

    // Act
    bool success = customer.Purchase(store, Product.Shampoo, 5);

    // Assert
    Assert.True(success);
    Assert.Equal(5, store.GetInventory(Product.Shampoo));       // 결과 상태를 검증
}
```

실제 `Store` 객체를 사용한다. Mock이 없다. 그리고 `RemoveInventory`가 호출되었는지가 아니라, **재고가 실제로 5개 줄었는지**를 검증한다.

### 3.2 Classical vs London: 같은 시나리오, 다른 검증

| | London 학파 | Classical 학파 |
|---|---|---|
| **Store** | Mock 객체 | 실제 객체 |
| **검증 대상** | `RemoveInventory`가 **호출되었는지** (행위 검증) | 재고가 **5개인지** (상태 검증) |
| **리팩터링 시** | Store 내부 구현이 바뀌면 테스트 깨짐 | 최종 결과만 같으면 테스트 통과 |

> **핵심 통찰**: Classical 학파의 테스트는 **최종 결과(end result)**를 검증하므로, 내부 구현이 바뀌어도 결과가 같으면 테스트가 통과한다. 이것이 **리팩터링 내성**이 높은 이유다. Khorikov는 이 책 전체에서 Classical 학파의 접근법을 권장한다.

---

## 4. 의존성의 분류

Classical 학파에서 어떤 의존성을 Mock으로 대체하고 어떤 것은 실제로 사용할지를 결정하려면, 의존성을 올바르게 분류해야 한다.

### 4.1 공유 의존성 vs 비공개 의존성

```
의존성(Dependency)
├── 공유 의존성(Shared) — 테스트 간에 상태를 공유
│   ├── 데이터베이스
│   ├── 파일 시스템
│   └── 정적 가변 필드(static mutable field)
│
└── 비공개 의존성(Private) — 테스트마다 새로 생성
    ├── 값 객체 (예: new Store())
    └── 불변 의존성 (예: 설정 값)
```

### 4.2 Mock 사용 기준

| 의존성 유형 | Classical 학파 | London 학파 |
|------------|---------------|-------------|
| **공유 의존성** (DB, 파일 시스템) | Mock/Stub으로 대체 | Mock/Stub으로 대체 |
| **비공개 가변 의존성** (new Store()) | 실제 객체 사용 | Mock으로 대체 |
| **불변 의존성** (값 객체, 설정 값) | 실제 객체 사용 | 실제 객체 사용 |

Classical 학파에서 Mock으로 대체하는 것은 **공유 의존성뿐**이다. 비공개 의존성은 얼마든지 실제 객체를 사용해도 테스트 간 격리에 문제가 없기 때문이다.

---

## 5. 단위 테스트 vs 통합 테스트

### 5.1 Classical 학파의 정의

Classical 학파에서 단위 테스트의 세 가지 속성을 다시 보면:

1. 작은 코드 조각을 검증한다
2. 빠르게 실행된다
3. 격리된 방식으로 실행된다 → **공유 의존성으로부터 격리**

이 세 가지를 **모두** 만족하면 단위 테스트, **하나라도** 만족하지 않으면 통합 테스트다:

| 조건 | 충족하지 못하면 |
|------|---------------|
| 작은 코드 조각 검증 | 통합 테스트 (너무 많은 코드를 한 번에 검증) |
| 빠르게 실행 | 통합 테스트 (DB, 네트워크 등 외부 의존성 사용) |
| 격리된 실행 | 통합 테스트 (공유 상태가 테스트 간 누수) |

### 5.2 E2E 테스트와의 관계

E2E(End-to-End) 테스트는 통합 테스트의 부분집합이다. 다른 점은 **외부 의존성을 Mock으로 대체하지 않는다**는 것이다:

```
테스트 유형 스펙트럼:

  단위 테스트 ←──────────────────────────→ E2E 테스트
  (격리 높음, 속도 빠름)              (격리 낮음, 속도 느림)
       ↑                                    ↑
  Mock 많이 사용                      Mock 거의 안 사용
  실행 빠름                          실행 느림
  범위 좁음                          범위 넓음
```

> **핵심 통찰**: 단위 테스트와 통합 테스트는 이분법이 아니라 **스펙트럼**이다. 중요한 것은 각 테스트 유형의 장단점을 이해하고, 상황에 맞는 균형을 찾는 것이다. Chapter 8에서 이 주제를 심도 있게 다룬다.

---

## 6. Khorikov의 선택: Classical 학파

### 6.1 왜 Classical인가?

Khorikov는 이 책 전체에서 Classical 학파의 접근법을 채택한다. 핵심 이유는 다음과 같다:

1. **리팩터링 내성**: Classical 학파의 테스트는 구현 세부사항이 아니라 최종 결과를 검증하므로, 리팩터링 시 깨지지 않는다
2. **테스트 가치**: 동작을 검증하는 테스트가 상호작용을 검증하는 테스트보다 더 의미 있는 보호를 제공한다
3. **유지보수 용이**: Mock 설정 코드가 줄어들어 테스트가 간결해진다

### 6.2 London 학파가 유용한 경우

그러나 London 학파의 Mock 사용이 적절한 경우도 있다:

- **프로세스 외부 의존성(*Out-of-process dependency — 애플리케이션과 별도의 프로세스에서 실행되는 의존성. 데이터베이스, 메시지 버스, SMTP 서버 등이 해당한다.*)**과의 상호작용을 검증할 때 (예: 이메일 전송, 메시지 큐)
- 이러한 경우는 Chapter 5(Mocks and Test Fragility)와 Chapter 8(Why Integration Testing?)에서 자세히 다룬다

---

## 7. 두 학파 비교 요약

| 기준 | London 학파 | Classical 학파 |
|------|------------|---------------|
| "단위"의 정의 | 하나의 클래스 | 하나의 동작 (여러 클래스 가능) |
| 격리 대상 | SUT를 협력자로부터 격리 | 테스트를 다른 테스트로부터 격리 |
| Mock 범위 | 불변 의존성 제외 전부 | 공유 의존성만 |
| 검증 방식 | 행위 검증 (메서드 호출 확인) | 상태 검증 (결과 값 확인) |
| 테스트 실패 원인 특정 | 쉬움 (한 클래스에 국한) | 어려울 수 있음 (여러 클래스 관여) |
| 리팩터링 내성 | **낮음** (구현 변경 시 깨짐) | **높음** (결과만 같으면 통과) |
| Khorikov의 권장 | 특수한 경우에만 사용 | **기본 접근법으로 권장** |

---

## 요약

- 단위 테스트는 **작은 코드 조각을 빠르게, 격리된 방식으로 검증**하는 테스트다.
- "격리"의 의미에 따라 **London 학파**(클래스 격리)와 **Classical 학파**(테스트 간 격리)로 나뉜다.
- London 학파는 SUT의 모든 협력자를 Mock으로 대체하고 **행위(interaction)**를 검증한다.
- Classical 학파는 공유 의존성만 Mock으로 대체하고 **최종 결과(state)**를 검증한다.
- London 학파의 테스트는 구현 세부사항에 결합되어 **리팩터링 내성이 낮다**.
- Khorikov는 Classical 학파를 기본 접근법으로 권장하며, 이 책 전체가 이 관점을 따른다.
- 단위 테스트의 세 가지 속성 중 하나라도 충족하지 못하면 **통합 테스트**로 분류된다.

---

## 다른 챕터와의 관계

- **Chapter 1 (The Goal of Unit Testing)**: "좋은 테스트란 무엇인가?"라는 질문을 던졌다면, 이 챕터는 그 전제 조건인 "단위 테스트란 무엇인가?"를 정의한다.
- **Chapter 3 (The Anatomy of a Unit Test)**: 단위 테스트의 정의를 확립한 후, 실제 테스트의 구조(AAA 패턴, 네이밍 등)를 다룬다.
- **Chapter 4 (The Four Pillars of a Good Unit Test)**: 이 챕터에서 예고한 "리팩터링 내성"이 네 가지 기둥 중 하나로 등장한다. London 학파의 문제점이 이 프레임워크로 체계적으로 설명된다.
- **Chapter 5 (Mocks and Test Fragility)**: Mock의 올바른 사용법을 다룬다. London 학파의 무분별한 Mock 사용이 왜 테스트를 취약하게 만드는지, 어떤 경우에 Mock이 적절한지를 깊이 파고든다.
- **Chapter 8 (Why Integration Testing?)**: 단위 테스트만으로 충분하지 않은 영역을 통합 테스트가 어떻게 보완하는지를 다룬다.
