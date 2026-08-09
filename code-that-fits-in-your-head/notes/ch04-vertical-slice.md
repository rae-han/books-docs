# Chapter 4: Vertical Slice (수직 슬라이스)

## 핵심 질문

이해관계자에게 가치를 가장 빨리 보여주려면 무엇부터 만들어야 할까? 데이터베이스 스키마부터? 도메인 모델부터? 아니면 "동작하는 소프트웨어를 사용자 앞에 놓는 것"부터? 왜 계층 하나가 아니라 **수직** 슬라이스여야 하는가?

---

## 서두 — 분석 마비에 빠진 팀

몇 년 전, 저자에게 단골 고객이 프로젝트를 도와달라고 요청해왔다. 팀은 거의 반년 동안 아무런 성과를 내지 못하고 작업만 하고 있었다.

작업이 벅찰 정도로 많기도 했지만, **분석 마비(*Analysis Paralysis - 요구사항이 너무 많아 어디부터 손대야 할지 결정하지 못하는 상태*)** 에 사로잡혀 있는 것이 진짜 문제였다.

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 가끔은 **그냥 시작하는 것**이 가장 좋은 전략이다. 계획은 너무 적어도 너무 많아도 좋지 않다. 배포 파이프라인을 이미 구축했다면, 기능이 부족하더라도 작동하는 소프트웨어를 빨리 배포할수록 이해관계자로부터 더 빨리 피드백을 수집할 수 있다.
:::

애플리케이션의 **수직 슬라이스(*Vertical Slice - 사용자 인터페이스부터 데이터 저장소까지 아키텍처의 모든 층을 얇게 관통하는 최소 기능*)** 를 만들고 배포하는 것부터 시작하자.

---

## 1. 동작하는 소프트웨어에서 시작하기

소프트웨어가 동작하는지 어떻게 알 수 있을까? 제품이 배포되고 설치되어 실제 사용자가 사용할 때까지는 확인할 수 없다. 심지어 의도대로 작동하더라도 사용자의 문제를 해결하지 못할 수도 있다.

수직 슬라이스 뒤에 숨어 있는 핵심 개념은 **가능한 한 빨리 작동하는 소프트웨어를 사용자에게 전달**하는 것이다. 사용자 인터페이스부터 데이터 저장소에 이르기까지 전체 과정의 기능을 최대한 간단하게 구현한다.

### 1.1 데이터 수신부터 데이터 보존까지

대부분의 소프트웨어는 외부와 연결하는 두 가지 형태의 경계가 있다. 데이터가 위쪽 경계에 도달하면 애플리케이션은 입력에 다양한 변형을 가한 후 최종적으로 값을 저장할 것인지 결정한다.

데이터 저장소는 전용 데이터베이스일 수도 있고, HTTP 기반 서비스나 메시지 큐, 파일 시스템, 표준 출력 스트림일 수도 있다. 쓰기 전용 시스템(표준 출력), 읽기 전용 시스템(다른 회사의 HTTP API), 읽기-쓰기 시스템(파일 시스템·DB) 등 다양하다. 추상화 수준이 충분히 높은 경우 이 다이어그램은 웹사이트부터 명령줄 유틸리티까지 대부분의 소프트웨어를 설명할 수 있다.

### 1.2 가장 간단한 수직 슬라이스

일반적 아키텍처는 구성 요소를 여러 **계층(*Layer - 관심사별로 코드를 수평으로 나눈 구조. 예: HTTP API 계층 → 도메인 계층 → 데이터 접근 계층*)** 으로 구성한다. 계층은 보통 수평 층으로 표현되고, 데이터는 맨 위로 들어와 맨 아래에서 저장된다.

기능 하나를 온전히 구현하려면 데이터가 들어오는 부분부터 저장되는 계층까지 **모든 계층을 거치면서 이동**해야 한다. 각 계층이 수평 층을 형성하고 있다고 가정하면, 하나의 기능은 모든 계층을 가로지르는 **수직 슬라이스**가 된다.

계층 구조가 아니어도 상관없다. **입력부터 저장까지 아우르는 기능(*End-to-End Feature*)** 을 구현하면 최소 두 가지를 얻는다.

1. 소프트웨어 개발 프로세스 전체 과정에 대한 피드백을 빠르게 받을 수 있다
2. 작동하는 소프트웨어이기 때문에 누군가에게는 쓸모가 있을 수 있다

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: '나중에 필요할지 모르는' 기능을 코드에 추가하는 **추측성 일반화(*Speculative Generality - 미래를 예측해 미리 만들어두는 안티패턴*)** 는 피해야 한다. 수직 슬라이스는 어떤 코드가 필요하고 어떤 코드가 필요 없는지를 매우 효과적으로 알려준다.
:::

---

## 2. 동작하는 골격

코드를 바꿔야 하는 **동기**를 찾자. 이런 동기는 실질적으로 코드에 변화를 이끌어내는 수단(driver)으로 작용한다. 앞서 살펴본 것처럼 경고를 오류로 취급하거나 린터·정적 코드 분석기를 켜는 방법도 이런 외적 수단이다.

소프트웨어의 변화를 이끌어내는 수단이 무엇이냐에 따라 "XX-주도 개발" 방법론들이 나타났다.

| 방법론 | 약어 | 변화의 수단 |
|---|---|---|
| 테스트 주도 개발 | TDD | 자동화된 테스트 |
| 행위 주도 개발 | BDD | 비즈니스 시나리오 |
| 도메인 주도 설계 | DDD | 도메인 모델 |
| 형식 주도 개발 | Type-Driven | 정적 타입 시스템 |
| 속성 주도 개발 | Property-Driven | 무작위 생성 데이터에 대한 속성 |

저자는 종종 **외부 접근 테스트 주도 개발(*Outside-in TDD - 시스템의 고수준 경계(HTTP 등)에서 시작해 필요에 따라 내부 구현으로 파고들며 테스트를 추가하는 기법*)** 을 사용한다.

### 2.1 특성화 테스트 (Characterization Test)

2장에서 만든 `Hello World!` API에 첫 테스트를 추가한다.

```csharp
[Fact]
public async Task HomeIsOk()
{
    using var factory = new WebApplicationFactory<Startup>();
    var client = factory.CreateClient();

    var response = await client
        .GetAsync(new Uri("", UriKind.Relative))
        .ConfigureAwait(false);

    Assert.True(
        response.IsSuccessStatusCode,
        $"Actual status code: {response.StatusCode}.");
}
```

저자는 소스 코드를 먼저 만들고 테스트를 나중에 작성했으므로 엄밀히 TDD 절차를 따른 것은 아니다. 이렇게 이미 있는 소프트웨어의 동작을 특성화(설명)하는 테스트를 **특성화 테스트(*Characterization Test - 이미 존재하는 코드의 현재 동작을 잠금(lock)하기 위해 나중에 작성하는 테스트*)** 라 한다.

빌드 스크립트도 함께 업데이트한다.

```bash
#!/usr/bin/env bash
dotnet test --configuration Release
```

`dotnet build` 대신 `dotnet test`를 호출하는 것뿐이다.

### 2.2 준비-행동-어설트 (AAA 패턴)

위 테스트는 두 문장 + 빈 줄 + 세 줄짜리 단일 문 + 빈 줄 + 세 줄짜리 단일 문 구조로 되어 있다. 이 구조는 **AAA 패턴(*Arrange-Act-Assert - 유닛 테스트를 준비/행동/검증 세 단계로 나누는 규범*)** 을 따랐기 때문이다.

1. **준비(Arrange)**: 테스트에 필요한 모든 것을 준비
2. **행동(Act)**: 테스트하려는 작업을 호출
3. **어설트(Assert)**: 실제 결과와 예상 결과 비교

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 세 단계의 크기가 균형을 이룰 때가 가장 좋다. 테스트 코드를 90° 회전시켰다고 상상했을 때 **행동(Act) 부분이 중앙**에 위치하면 균형이 잘 맞는 것이다.
:----

준비 단계가 너무 길어져 빈 줄을 추가하면 세 단계 구분이 흐려진다. 이는 코드가 커지면서 발생하는 코드 악취다. 매우 짧은 테스트(코드 세 줄 이하)라면 빈 줄을 생략해도 된다.

### 2.3 정적 분석 조절

위 테스트에는 `ConfigureAwait` 호출과 `new Uri("", UriKind.Relative)`처럼 장황한 부분이 있다. 두 문제 모두 정적 분석 규칙 때문이다.

- **`ConfigureAwait` 규칙**: 재사용 가능한 라이브러리에서 교착 상태를 피하기 위한 것. 하지만 테스트 라이브러리는 재사용 라이브러리가 아니므로 이 규칙을 꺼도 된다.
- **`Uri` 규칙**: **"문자열 형식(*Stringly Typed - 원래는 강타입이어야 할 곳을 문자열로 표현하는 안티패턴*)"** 을 피하라는 유용한 규칙. 하지만 리터럴만 쓰는 특정 테스트에서는 예외로 인정할 만하다.

```csharp
[Fact]
[SuppressMessage(
    "Usage", "CA2234: Pass system uri objects instead of strings",
    Justification = "URL isn't passed as variable, but as literal.")]
public async Task HomeIsOk()
{
    using var factory = new WebApplicationFactory<Startup>();
    var client = factory.CreateClient();

    var response = await client.GetAsync("");

    Assert.True(
        response.IsSuccessStatusCode,
        $"Actual status code: {response.StatusCode}.");
}
```

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 규칙을 끌 때는 **왜 껐는지 반드시 문서화**하라. 결정된 내용을 설명하는 것보다 **결정한 이유**를 설명해야 한다. 나중에 코드를 읽는 사람이 이해할 수 있어야 한다.
:::

---

## 3. 외부 접근 개발

우리에게는 이제 동작하는 골격이 있다. 시스템은 쓸모 있는 작업을 처리할 수 있어야 한다. 이 장의 목표는 HTTP 경계에서 데이터 저장에 이르는 시스템의 수직 슬라이스를 구현하는 것이다. 간단한 온라인 레스토랑 예약 시스템을 만들 것이므로, 유효한 예약을 받아 DB에 저장하는 동작이 첫 슬라이스로 적합하다.

### 3.1 JSON 수신 — 응답을 JSON으로

첫 단계는 API의 응답이 JSON 문서인지 확인하는 것이다. 기존 테스트를 확장한다.

```csharp
[Fact]
public async Task HomeReturnsJson()
{
    using var factory = new WebApplicationFactory<Startup>();
    var client = factory.CreateClient();

    using var request = new HttpRequestMessage(HttpMethod.Get, "");
    request.Headers.Accept.ParseAdd("application/json");
    var response = await client.SendAsync(request);

    Assert.True(response.IsSuccessStatusCode, /* ... */);
    Assert.Equal(
        "application/json",
        response.Content.Headers.ContentType?.MediaType);
}
```

세 부분이 바뀌었다. 테스트 이름을 더 구체적으로, `Accept` 헤더를 `application/json`으로 명시적으로 설정, `Content-Type`을 검증하는 어설션 추가. 이제 클라이언트는 HTTP의 **내용 협상(*Content Negotiation - Accept 헤더로 원하는 응답 형식을 요구하는 프로토콜*)** 프로토콜을 사용한다.

이 테스트를 통과시키기 위해 최소한의 컨트롤러를 만든다.

```csharp
[Route("")]
public class HomeController : ControllerBase
{
    public IActionResult Get()
    {
        return Ok(new { message = "Hello, World!" });
    }
}
```

그리고 `Startup`에서 MVC 프레임워크를 등록한다.

```csharp
public sealed class Startup
{
    public static void ConfigureServices(IServiceCollection services)
    {
        services.AddControllers();
    }
    // ...
}
```

### 3.2 예약 게시 (POST)

첫 번째 수직 슬라이스의 기능을 선택할 때 저자의 휴리스틱이다.

1. **구현하기 간단한 기능이어야 한다**
2. **되도록 데이터 입력이 가능해야 한다**

영구 데이터를 사용하는 시스템에서 다른 부분을 테스트하려면 약간의 데이터가 필요하다. 시스템에 데이터를 추가하는 기능부터 시작하면 이 문제가 깔끔히 풀린다.

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 수직 슬라이스를 만들 때는 **모든 조건이 맞아 예외나 오류가 발생하지 않는 상태(happy path)** 를 목표로 삼는다. 잘못될 가능성이 있는 것은 일단 무시하라. 목표는 시스템의 어떤 기능이 **가능한지 증명**하는 것이다.
:::

```csharp
[Fact]
public async Task PostValidReservation()
{
    var response = await PostReservation(new {
        date = "2023-03-10 19:00",
        email = "katinka@example.com",
        name = "Katinka Ingabogovinanana",
        quantity = 2 });

    Assert.True(response.IsSuccessStatusCode, /* ... */);
}
```

고수준 테스트는 어설션이 비교적 쉽게 통과할 수 있게 만들어야 한다. 개발 과정에서 세부사항이 자주 바뀌므로 어설션을 너무 구체적으로 작성하면 자주 수정해야 하기 때문이다.

`PostReservation`은 테스트 유틸리티 헬퍼 메서드다.

```csharp
private async Task<HttpResponseMessage> PostReservation(object reservation)
{
    using var factory = new WebApplicationFactory<Startup>();
    var client = factory.CreateClient();

    string json = JsonSerializer.Serialize(reservation);
    using var content = new StringContent(json);
    content.Headers.ContentType.MediaType = "application/json";

    return await client.PostAsync("reservations", content);
}
```

이렇게 헬퍼로 뽑는 이유는 (1) 테스트의 **가독성**이 좋아지고 (2) URL 자체가 API 계약의 일부가 되지 않도록 감출 수 있기 때문이다.

로버트 마틴의 정의를 빌리면 **추상화란 무관한 것을 제거하고, 본질적인 것을 강조하는 것**이다. 서비스에 어떤 값을 게시하면 성공 여부가 응답으로 돌아오는 형태는 좋은 추상화의 예다.

테스트를 통과시키기 위해 최소한의 컨트롤러를 만든다.

```csharp
[Route("[controller]")]
public class ReservationsController
{
#pragma warning disable CA1822 // 멤버를 static으로 표시하세요.
    public void Post() { }
#pragma warning restore CA1822
}
```

`ASP.NET MVC` 관례상 컨트롤러 메서드는 인스턴스 메서드여야 하므로 정적 코드 분석 규칙을 `#pragma`로 껐다. 저자는 일부러 가장 끔찍한 방법을 선택했다 — TODO 주석과 같은 효과를 노린 것이다.

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 우리의 목표는 코드를 빨리 작성하는 것이 아니라 **지속 가능한 소프트웨어**를 만드는 것이다. 경고를 오류로 취급하면 대가가 따르지만, 속도를 조절하는 것도 감수할 만한 가치가 있다.
:::

### 3.3 유닛 테스트 — 안으로 들어가기

경계 테스트는 통과했지만, 실제로는 아무 데이터도 저장하지 않는다. 다음 유닛 테스트로 동작을 목표에 더 가깝게 유도한다.

```csharp
[Fact]
public async Task PostValidReservationWhenDatabaseIsEmpty()
{
    var db = new FakeDatabase();
    var sut = new ReservationsController(db);
    var dto = new ReservationDto {
        At = "2023-11-24 19:00",
        Email = "juliad@example.net",
        Name = "Julia Domna",
        Quantity = 5
    };

    await sut.Post(dto);

    var expected = new Reservation(
        new DateTime(2023, 11, 24, 19, 0, 0),
        dto.Email,
        dto.Name,
        dto.Quantity);
    Assert.Contains(expected, db);
}
```

여기서 외부 접근 TDD의 핵심이 드러난다 — **시스템 경계에서 시작해서 점차 안쪽으로 들어가면서 작업을 진행**한다.

경계에서 모든 엣지 케이스를 확인하려면 조합이 폭발적으로 증가해 테스트를 수만 개 만들어야 한다. 하지만 유닛 테스트로 내부를 검증하면 이 문제를 해결할 수 있다.

준비 단계에서는 `FakeDatabase`와 **SUT(*System Under Test - 테스트 대상 시스템*)** 를 생성한다. 행동 단계에서는 **DTO(*Data Transfer Object - 데이터 구조만을 담는 객체*)** 를 생성하고 `Post` 메서드로 전달한다. AAA 균형을 위해 DTO 초기화를 준비가 아닌 행동 단계에 두어 2-2-2 구조를 만들었다.

### 3.4 DTO와 도메인 모델

이름이 비슷한 클래스 두 개(`ReservationDto`, `Reservation`)가 필요한 이유는 **역할이 다르기** 때문이다.

```csharp
public class ReservationDto
{
    public string? At { get; set; }
    public string? Email { get; set; }
    public string? Name { get; set; }
    public int Quantity { get; set; }
}
```

DTO의 역할은 **입력 JSON을 데이터 구조로 가져오거나, 데이터 구조를 출력 형태로 변환**하는 것뿐이다. DTO는 캡슐화를 제공하지 않으므로 다른 용도로는 사용할 수 없다. 파울러의 유명한 말처럼:

> 데이터 전송 객체(DTO)는 우리 어머니가 절대 작성하지 말라고 한 객체 중 하나입니다.

반면 `Reservation` 클래스는 **도메인 모델(*Domain Model - 비즈니스 규칙과 개념을 표현하는 코드. 데이터 전달만 하는 DTO와 대비됨*)** 의 일부다.

```csharp
public sealed class Reservation
{
    public Reservation(DateTime at, string email, string name, int quantity)
    {
        At = at;
        Email = email;
        Name = name;
        Quantity = quantity;
    }

    public DateTime At { get; }
    public string Email { get; }
    public string Name { get; }
    public int Quantity { get; }

    public override bool Equals(object? obj)
    {
        return obj is Reservation reservation &&
            At == reservation.At &&
            Email == reservation.Email &&
            Name == reservation.Name &&
            Quantity == reservation.Quantity;
    }

    public override int GetHashCode()
    {
        return HashCode.Combine(At, Email, Name, Quantity);
    }
}
```

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: `Reservation`은 DTO와 달리 (1) 모든 값을 생성자에서 요구해 **비어 있는 상태가 될 수 없고**, (2) `DateTime`을 사용해 **적절한 날짜만 들어가도록 보장**한다. 이 두 조건이 캡슐화의 시작점이다.
:::

`Reservation`이 **값 객체(*Value Object - 식별자 없이 값 자체로 비교되는 불변 객체*)** 처럼 보이는 이유는 여러 이점이 있고, 테스트가 더 쉬워지기 때문이다. 도메인 모델에는 되도록 값 객체를 사용하자.

Equals 오버라이드로 **구조적 동등성(*Structural Equality - 모든 속성 값이 같으면 같다고 판단하는 방식*)** 을 구현했으므로 `Assert.Contains(expected, db)`가 동작한다. 변경 불가한 클래스에서만 구조적 동등성을 안전하게 구현할 수 있다.

### 3.5 가짜 객체 (FakeDatabase)

```csharp
[SuppressMessage(
    "Naming", "CA1710: Identifiers should have correct suffix",
    Justification = "The role of the class is a Test Double.")]
public class FakeDatabase :
    Collection<Reservation>, IReservationsRepository
{
    public Task Create(Reservation reservation)
    {
        Add(reservation);
        return Task.CompletedTask;
    }
}
```

**가짜 객체(*Fake Object - 테스트 더블(Test Double)의 일종. 실제 데이터베이스처럼 동작하지만 인메모리로 동작하는 테스트 전용 구현*)** 는 `IReservationsRepository`를 구현한 일반적인 인메모리 컬렉션이다. `Collection<Reservation>`에서 파생됐으므로 `Add`, `Contains` 등 컬렉션 메서드가 그대로 동작한다. **상태 기반 테스트**에서 잘 작동한다.

저장소 인터페이스는 초기에는 한 메서드만 정의한다.

```csharp
public interface IReservationsRepository
{
    Task Create(Reservation reservation);
}
```

### 3.6 저장소 생성 — 프로덕션 코드 수정

컨트롤러가 저장소를 사용하도록 수정한다.

```csharp
[ApiController, Route("[controller]")]
public class ReservationsController
{
    public ReservationsController(IReservationsRepository repository)
    {
        Repository = repository;
    }

    public IReservationsRepository Repository { get; }

    public async Task Post(ReservationDto dto)
    {
        if (dto is null)
            throw new ArgumentNullException(nameof(dto));

        await Repository
            .Create(
                new Reservation(
                    new DateTime(2023, 11, 24, 19, 0, 0),
                    "juliad@example.net",
                    "Julia Domna",
                    5))
            .ConfigureAwait(false);
    }
}
```

**생성자 주입(*Constructor Injection - 의존성을 생성자 매개변수로 받아 필드에 저장하는 의존성 주입 방식*)** 을 사용한다. 하드코딩된 예약을 만드는 것은 명백히 잘못됐지만, 테스트를 통과시키는 가장 간단한 방법이다. 이 문제는 다음 장에서 다룬다.

### 3.7 의존성 구성

새 테스트는 성공하지만 기존 경계 테스트는 실패한다. `ReservationsController`가 매개변수 없는 생성자를 가지지 않기 때문이다. 일단 **널 객체(*Null Object - 아무 동작도 하지 않는 인터페이스 구현체*)** 로 해결한다.

```csharp
private class NullRepository : IReservationsRepository
{
    public Task Create(Reservation reservation)
    {
        return Task.CompletedTask;
    }
}
```

**의존성 주입 컨테이너(*Dependency Injection Container - 인터페이스와 구현체의 매핑을 관리하고 자동으로 인스턴스를 주입해주는 도구*)** 에 싱글턴으로 등록한다.

```csharp
public static void ConfigureServices(IServiceCollection services)
{
    services.AddControllers();
    services.AddSingleton<IReservationsRepository>(new NullRepository());
}
```

---

## 4. 슬라이스 완성

지금까지는 저장소가 널 객체다. 예약을 **영구 저장소**에 저장하려면 `IReservationsRepository`를 제대로 구현해야 한다.

> **실무 팁**: 자동화된 테스트를 통해 지원할 수 있는 데이터베이스가 있으면 편하다. 하지만 저자는 교육 목적으로 SQL 서버(관계형 DB)를 선택했다. 관계형 DB는 어디서나 쓰이며, 조직 표준이나 운영팀의 지원 계약 때문에 특정 DB를 강제로 써야 할 때가 많기 때문이다.

### 4.1 스키마

```sql
CREATE TABLE [dbo].[Reservations] (
    [Id]       INT             NOT NULL IDENTITY,
    [At]       DATETIME2       NOT NULL,
    [Name]     NVARCHAR(50)    NOT NULL,
    [Email]    NVARCHAR(50)    NOT NULL,
    [Quantity] INT             NOT NULL
    PRIMARY KEY CLUSTERED ([Id] ASC)
)
```

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: DB 스키마는 DB의 기본 언어인 **SQL로 정의**하고 소스 코드가 있는 깃 저장소에 커밋하라. ORM이나 도메인 특화 언어가 좋다면 그것도 괜찮지만, **버전 관리 대상**이라는 사실은 변하지 않는다.
:::

### 4.2 SQL 저장소

```csharp
public class SqlReservationsRepository : IReservationsRepository
{
    public SqlReservationsRepository(string connectionString)
    {
        ConnectionString = connectionString;
    }

    public string ConnectionString { get; }

    public async Task Create(Reservation reservation)
    {
        if (reservation is null)
            throw new ArgumentNullException(nameof(reservation));

        using var conn = new SqlConnection(ConnectionString);
        using var cmd = new SqlCommand(createReservationSql, conn);
        cmd.Parameters.Add(new SqlParameter("@At", reservation.At));
        cmd.Parameters.Add(new SqlParameter("@Name", reservation.Name));
        cmd.Parameters.Add(new SqlParameter("@Email", reservation.Email));
        cmd.Parameters.Add(new SqlParameter("@Quantity", reservation.Quantity));

        await conn.OpenAsync().ConfigureAwait(false);
        await cmd.ExecuteNonQueryAsync().ConfigureAwait(false);
    }

    private const string createReservationSql = @"
        INSERT INTO [dbo].[Reservations] ([At], [Name], [Email], [Quantity])
        VALUES (@At, @Name, @Email, @Quantity)";
}
```

저자는 ORM을 좋아하지 않는다. ADO.NET은 코드가 조금 더 많지만 코드 생산 속도가 중요한 게 아니다.

이 클래스는 TDD로 만들지 않았다. **험블 객체(*Humble Object - 자동 테스트가 어려운 하위 시스템에 의존하는 부분을 최대한 얇게 만들어, 유닛 테스트 커버리지 밖에 두는 패턴*)** 라고 보기 때문이다. 논리 분기가 거의 없고(정적 분석이 추가한 null 체크뿐), 상태를 저장하지 않고 스레드 안전하다. DB 통합 테스트는 나중에 12장에서 다룬다.

### 4.3 데이터베이스 설정

`Startup` 클래스에서 실제 저장소를 등록한다.

```csharp
public IConfiguration Configuration { get; }

public Startup(IConfiguration configuration)
{
    Configuration = configuration;
}

public void ConfigureServices(IServiceCollection services)
{
    services.AddControllers();
    var connStr = Configuration.GetConnectionString("Restaurant");
    services.AddSingleton<IReservationsRepository>(
        new SqlReservationsRepository(connStr));
}
```

연결 문자열은 `appsettings.json` 구조만 커밋하고 실제 값은 커밋하지 않는다 — 비밀 정보가 포함될 수 있다.

```json
{
  "ConnectionStrings": {
    "Restaurant": ""
  }
}
```

### 4.4 스모크 테스트 (Smoke Test)

자동화된 테스트가 좋지만 **수동 테스트도 잊지 말자**. 시스템을 켜서 제대로 동작하는지 확인하는 것을 **스모크 테스트(*Smoke Test - "연기가 나는지" 즉 즉시 눈에 띄는 문제가 있는지 빠르게 확인하는 테스트*)** 라 한다.

```bash
$ curl -v http://localhost:53568/reservations \
    -H "Content-Type: application/json" \
    -d "{ \"at\": \"2022-10-21 19:00\",
         \"email\": \"caravan@example.com\",
         \"name\": \"Cara van Palace\",
         \"quantity\": 3 }"
```

DB를 확인해보면 `Julia Domna`에 대한 예약 행을 볼 수 있다(하드코딩 때문). 시스템은 아직 하드코딩 예약만 저장하지만, **적어도 입력을 넣으면 뭔가 일어난다**는 것은 확인됐다.

### 4.5 가짜 DB를 사용한 경계 테스트

경계 테스트는 여전히 실패한다. `Startup`이 실제 연결 문자열을 요구하기 때문이다. 실제 DB를 자동 테스트에 붙이면 번거롭고 느려지므로, `FakeDatabase`를 주입한다.

```csharp
public class RestaurantApiFactory : WebApplicationFactory<Startup>
{
    protected override void ConfigureWebHost(IWebHostBuilder builder)
    {
        if (builder is null)
            throw new ArgumentNullException(nameof(builder));

        builder.ConfigureServices(services =>
        {
            services.RemoveAll<IReservationsRepository>();
            services.AddSingleton<IReservationsRepository>(
                new FakeDatabase());
        });
    }
}
```

기존 `PostReservation` 헬퍼에서 팩토리 한 줄만 교체하면 된다. 이제 모든 테스트가 다시 통과한다.

---

## 5. 자주 하는 실수

| 안티패턴 | 해결법 |
|---|---|
| DB 스키마 먼저 설계 | 수직 슬라이스로 UI→DB 얇게 관통 |
| 자체 프레임워크·ORM 개발에 몇 달 소비 | 추측성 일반화 금지. 필요한 것만 만들기 |
| 모든 경계 테스트로 엣지 케이스 검증 | 경계는 happy path, 세부는 유닛 테스트 |
| DTO에 캡슐화/검증 로직 넣기 | DTO는 데이터 매핑, 도메인 모델은 별도 |
| 정적 분석 규칙을 그냥 무시 | 억제할 때 반드시 **왜 껐는지 이유** 문서화 |
| DB 스키마를 GUI로만 관리 | SQL로 정의해 깃 저장소에 커밋 |

---

## 6. 결론

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 얇은 수직 슬라이스는 소프트웨어가 실제로 작동할 수 있음을 입증하는 효과적인 방법이다. 지속적 배포와 함께 사용하면 프로덕션 환경으로 작업한 소프트웨어를 빠르게 배치할 수 있다.
:::

첫 번째 수직 슬라이스가 너무 얇아 무의미해 보이는가? 이 장에서는 DB에 예약을 저장하는 방법을 보여줬지만 저장되는 값은 사용자 입력이 아니었다. 이게 무슨 의미가 있을까?

아직은 그렇지 않지만, 배포 파이프라인과 더불어 **동작하는 시스템을 구성하게 되었다**는 점에서 가치가 있다. 이제 개선해 나갈 수 있다. 작은 개선사항을 지속적으로 제공함에 따라 점점 더 쓸모 있는 시스템이 될 것이며, 이해관계자들은 시스템의 유용성을 평가할 좋은 장치들을 갖게 된다.

여러분의 임무는 그들의 평가를 지원하는 것이다. **가능한 한 자주 배포하고, 완료되면 알려주자.**

---

## 요약

- 분석 마비를 피하려면 **그냥 시작**하는 게 낫다. 계획은 필요하지만 너무 많아도 좋지 않다
- **수직 슬라이스**: UI부터 DB까지 얇게 관통하는 최소 기능. 계층 하나만 만드는 "수평" 접근과 대비됨
- 얻는 것: (1) 개발 프로세스 전체에 대한 **빠른 피드백**, (2) **작동하는 소프트웨어**
- 새 코드베이스는 (a) **동작하는 골격** → (b) **특성화 테스트** → (c) **외부 접근 TDD**로 진행. 경계에서 시작해 내부로 파고들기
- **AAA 패턴**: 준비-행동-어설트. 세 단계 크기가 균형을 이루면 좋음. 행동 부분이 중앙에 오도록
- 코드 예약 도메인에서 **DTO**(데이터 매핑용, `ReservationDto`)와 **도메인 모델**(비즈니스 규칙 캡슐화, `Reservation`) 분리
- 도메인 객체는 **값 객체** 스타일로. 불변, 구조적 동등성, 완전한 생성자 초기화
- 자동 테스트를 위한 **가짜 객체(FakeDatabase)**. 인메모리로 실제처럼 동작하는 테스트 더블
- 실제 DB는 **험블 객체** 스타일로 얇게. 유닛 테스트가 어려운 부분에 분기 로직을 넣지 않기
- 정적 분석 규칙을 억제할 때는 **왜 껐는지 이유를 반드시 문서화**
- 얇은 슬라이스는 **가치가 없어 보여도** 배포 파이프라인과 함께 있으면 지속적 개선 인프라가 완성된다
