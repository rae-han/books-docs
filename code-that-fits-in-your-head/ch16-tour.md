# Chapter 16: Tour (여행 — 예제 코드베이스 살펴보기)

## 핵심 질문

자신이 작성하지 않은 코드에서 어떻게 길을 찾을 것인가? 이 책이 제시한 프랙티스들을 모두 적용한 코드베이스는 어떤 모습이며, 어떻게 탐색하고 학습해야 하는가?

---

## 1. 코드베이스 탐색하기

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 코드를 볼 때 어떤 동기를 가지고 있는지에 따라 접근이 달라진다. 유지보수 개발자로서 스택 트레이스를 받았다면 최상위 프레임부터 본다. 감을 익히려 한다면 **프로그램의 진입점**부터 본다.
:::

.NET 코드베이스는 ``Main`` 메서드가 시작점이다. 이 책의 예제 코드베이스에서 ``Main`` 메서드는 예제 2-4 이후로 바뀐 적이 없다.

```csharp
// Restaurant/af31e63/Restaurant.RestApi/Program.cs
public static class Program
{
    public static void Main(string[] args)
    {
        CreateHostBuilder(args).Build().Run();
    }

    public static IHostBuilder CreateHostBuilder(string[] args) =>
        Host.CreateDefaultBuilder(args)
            .ConfigureWebHostDefaults(webBuilder =>
                webBuilder.UseStartup<Startup>());
}
```

이는 ASP.NET Core의 **보일러플레이트 코드(*Boilerplate Code - 프레임워크가 요구하는, 거의 변경되지 않는 정형화된 코드*)** 다. 팀원들이 프레임워크의 기본을 안다고 전제하고, 되도록 놀랍지 않은 코드를 유지하는 것이 최선이다.

### 1.1 큰 그림 보기

IDE로 ``Startup`` 클래스로 이동해보자.

```csharp
// Restaurant/af31e63/Restaurant.RestApi/Startup.cs
public sealed class Startup
{
    public IConfiguration Configuration { get; }

    public Startup(IConfiguration configuration)
    {
        Configuration = configuration;
    }

    public static void Configure(
        IApplicationBuilder app,
        IWebHostEnvironment env)
    {
        if (env.IsDevelopment())
            app.UseDeveloperExceptionPage();

        app.UseAuthentication();
        app.UseRouting();
        app.UseAuthorization();
        app.UseEndpoints(endpoints => { endpoints.MapControllers(); });
    }
}
```

``Configure`` 메서드는 순환 복잡도가 2, 활성화된 객체 3개, 코드 12줄로 이해가 쉽다. 이 코드는 시스템이 인증/라우팅/권한부여를 사용하고 프레임워크의 기본 MVC 패턴을 쓴다는 것을 알려준다.

**육각 꽃 다이어그램(*Hexagonal Flower Diagram - 저자가 제안하는 코드 이해도 시각화. 중심 메서드 주위에 활성화된 객체나 분기를 육각형으로 배치*)** 을 그려보면 코드가 프랙탈 아키텍처에 얼마나 잘 맞는지 확인할 수 있다.

이어서 ``ConfigureServices``:

```csharp
public void ConfigureServices(IServiceCollection services)
{
    var urlSigningKey = Encoding.ASCII.GetBytes(
        Configuration.GetValue<string>("UrlSigningKey"));
    services
        .AddControllers(opts =>
        {
            opts.Filters.Add<LinksFilter>();
            opts.Filters.Add(new UrlIntegrityFilter(urlSigningKey));
        })
        .AddJsonOptions(opts =>
            opts.JsonSerializerOptions.IgnoreNullValues = true);

    ConfigureUrlSigning(services, urlSigningKey);
    ConfigureAuthorization(services);
    ConfigureRepository(services);
    ConfigureRestaurants(services);
    ConfigureClock(services);
    ConfigurePostOffice(services);
}
```

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 이 메서드는 코드베이스의 **목차** 역할을 한다. 인증을 알고 싶으면 ``ConfigureAuthorization`` 으로, 데이터 접근을 조사하려면 ``ConfigureRepository`` 로 이동. 이것이 프랙탈 아키텍처가 동작하는 방식이다.
:::

세부 사항으로 들어갈 때는 상위 수준의 맥락이 더 이상 필요하지 않다.

### 1.2 파일 정리

저자가 자주 받는 질문: **"컨트롤러/모델/필터 디렉터리를 나눠야 하나요? 기능별로 나눠야 하나요?"**

저자의 대답: **"그냥 모든 파일을 한 디렉터리에 넣으세요."** — 대부분 좋아하지 않는 답이다.

이유는 파일 시스템의 본질에 있다. **파일 시스템은 트리 구조** — 각 노드는 최대 하나의 부모만 가진다. 어떤 파일을 ``Controllers/`` 에 넣으면 동시에 ``Calendar/`` 에 넣을 수는 없다.

파이어폭스 코드베이스 분석에서는 이렇게 지적한다.

> 시스템 아키텍트들은 시스템을 분할하는 방법이 여러 가지라는 것을 깨달았다. 파이어폭스는 브라우저와 툴킷을 분리함으로써 장소로(*locale*)와 테마도 함께 분리할 수 있게 됐다.

**계층으로 정리하는 순간 다른 정리 방식은 자동으로 배제**된다. C#, Java 같은 단일 상속 언어에서 부모 클래스를 하나 정하면 다른 모든 클래스는 잠재적 부모가 될 수 없는 것과 같다.

> 클래스 상속보다 객체 구성을 선호해야 한다. — GoF

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 상속을 피하듯이 **디렉터리 구조로 코드를 정리하는 것도 피해야 한다**. 샘플 코드베이스 ``Restaurant.RestApi/`` 디렉터리에는 컨트롤러, DTO, 도메인 모델, 필터, SQL, 인터페이스, 어댑터 등 65개 파일이 평면적으로 놓여 있다.
:::

유일한 예외: ``Options/`` 서브디렉터리 — ASP.NET 옵션 시스템에 특화된 4개 파일. **특정 목적으로만 사용되어야 하고 다른 곳에서 참조되면 안 된다는 것을 확실히 알기에** 격리시켰다.

"그럼 파일을 어떻게 찾나요?"

**IDE의 이동(navigation) 기능을 사용하라.**

- Visual Studio의 F12 (Go To Definition)
- 인터페이스 구현으로 이동
- 참조 찾기, 심볼 찾기
- 편집기 탭 사이 단축키 이동

한번은 몹 프로그래밍을 하면서 "테스트 대상 시스템으로 가볼까요?"라고 하자, 개발자가 파일 보기로 가서 스크롤로 파일을 찾아 더블클릭했다. 그 파일은 이미 다른 탭에 열려 있었고 단축키만 누르면 되는 상태였다.

**연습**: IDE의 파일 뷰를 숨기고 코드 통합 편집 기능만으로 이동하는 법을 익혀라.

### 1.3 세부 사항 찾아보기

데이터 접근이 궁금하면 ``ConfigureRepository`` 로 이동.

```csharp
private void ConfigureRepository(IServiceCollection services)
{
    var connStr = Configuration.GetConnectionString("Restaurant");
    services.AddSingleton<IReservationsRepository>(sp =>
    {
        var logger =
            sp.GetService<ILogger<LoggingReservationsRepository>>();
        var postOffice = sp.GetService<IPostOffice>();
        return new EmailingReservationsRepository(
            postOffice,
            new LoggingReservationsRepository(
                logger,
                new SqlReservationsRepository(connStr)));
    });
}
```

이 코드에서 배울 수 있는 것:

- ASP.NET 표준 구성 시스템으로 접속 문자열 관리
- ``IReservationsRepository`` 서비스는 **3단계 깊이의 데코레이터** — 이메일, 로깅, SQL
- 가장 안쪽 구현은 ``SqlReservationsRepository``

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 세부 사항으로 확대해 들어가면 주변 상황은 더 이상 중요하지 않다. 머릿속에서 추적할 것은 ``services`` 파라미터, ``Configuration`` 속성, 이 메서드가 만드는 변수뿐이다. **프랙탈 아키텍처**란 각 수준의 코드를 이해할 때 상위 수준의 내용이 필요하지 않게 만드는 것이다.
:::

---

## 2. 아키텍처

아키텍처 자체는 이 책의 주제가 아니지만, 코드 구성 방식에 영향을 주므로 짚고 넘어간다. 저자는 계층화, 모놀리식, 포트와 어댑터, 수직 슬라이스, 행위자 모델, 마이크로서비스, 함수형 코어/명령 셸 등 다양한 아키텍처를 사용해왔다.

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 모든 것에 적용되는 아키텍처는 없다. 여기서 설명하는 것은 현재 예제에 적합한 하나의 선택일 뿐이다.
:::

### 2.1 모놀리식

샘플 코드베이스는 당황스러울 정도로 하나의 큰 덩어리, 즉 **모놀리식(*Monolithic - 하나의 실행 단위로 배포되는 단일 코드베이스 구조*)** 이다. 프로덕션 패키지 하나 + 유닛 테스트 + 통합 테스트 = 세 패키지.

전체 프로덕션 코드는 하나의 실행 파일로 컴파일된다. 여기에는 DB 접근, HTTP, 도메인 모델, 로깅, 이메일, 인증 및 권한 부여가 모두 들어 있다. 모놀리식이라고 부를 수 있다.

배포 관점에서는 이 코드를 다른 컴퓨터에서 작동시키기 위해 분리할 수 없다. 저자는 이 부분이 이 샘플 애플리케이션의 **비즈니스 목표가 아니라고 판단**했다. 재사용 관점에서도 마찬가지 — 도메인 모델만 떼어 배치 작업에 재사용하려 하면 HTTP와 이메일까지 딸려 온다.

**한 개의 패키지가 네 개의 패키지보다 간단**하다. 그리고 내부적으로는 **함수형 코어/명령 셸** 아키텍처를 적용했고, 이는 대체로 **포트-어댑터 스타일**로 이어진다.

### 2.2 순환 구조

모놀리식이 평판이 나쁜 이유는 의도치 않게 **스파게티 코드**가 되기 쉽기 때문이다. 하나의 패키지 안에서 모든 코드를 쉽게 호출할 수 있다.

전형적 예: 객체-관계 매퍼(ORM)에 의해 정의된 매개변수 객체를 주고받는 데이터 접근 인터페이스.

```
   [도메인 모델]                     [데이터 접근]
   ┌─────────────┐                 ┌────────────────┐
   │ IRepository │  ─── Row ───▶   │ OrmRepository  │
   │  Create(Row)│                 │      ROW       │
   └─────────────┘  ◀── impl ───   └────────────────┘
        ▲                                  │
        └──────────────────────────────────┘
              순환 구조 (cyclic)
```

인터페이스가 도메인 모델에 정의되면서 매개변수로 ORM의 ``Row`` 클래스를 사용하니, 도메인 모델이 데이터 접근에 의존한다. 반대로 ``OrmRepository`` 는 인터페이스를 구현하므로 도메인 모델에 의존한다. **순환**이다. 이는 의존성 역전 원칙 위반이기도 하다.

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 주류 언어는 코드의 순환 구조를 허용하지만, **패키지의 순환 의존성은 금지**할 수 있다. IDE에서 A→B, B→A 참조를 시도하면 비순환 의존성 원칙(ADP) 위반으로 거부한다. 이것이 코드베이스를 여러 패키지로 분리하는 강력한 동기다.
:::

이는 아키텍처에 **포카요케(*Poka-yoke - "실수 방지"를 뜻하는 일본 제조업 용어. 잘못된 동작 자체를 불가능하게 만드는 설계*)** 를 적용하는 것과 같다.

가상의 분해 예시 — 하나의 프로덕션 패키지를 4개로 나누면 총 7개 패키지가 된다.

```
┌─── 테스트 ────────┐     ┌─── 프로덕션 ─────┐
│                  │     │                │
│  통합 테스트     │────▶│  데이터 접근    │
│  도메인 테스트   │────▶│  도메인 모델    │
│  HTTP 테스트     │────▶│  HTTP 모델      │
│                  │     │                │
│                  │     │  APP 호스트    │
│                  │     │  (조합)         │
└──────────────────┘     └────────────────┘
```

3개 테스트 패키지가 3개 프로덕션 패키지를 대상으로 하고, **APP 호스트** 패키지가 최상위 조합(*composition root*)을 담당한다.

F#은 앞에서 정의되지 않은 코드는 사용할 수 없어 언어 차원에서 순환을 막는 것으로 유명하다. 하스켈은 상위 수준에서 부수 효과를 명시적으로 처리하도록 강제하여 궁극적으로 포트-어댑터 스타일로 유도한다. 저자는 이런 언어에 익숙해서 모놀리식으로도 잘 분리된 코드를 유지할 수 있지만, **경험이 없다면 패키지 분리를 권장**한다.

---

## 3. 사용법

익숙하지 않은 코드베이스를 살펴볼 때는 실제로 어떻게 동작하는지 확인하고 싶어진다. REST API는 UI가 없어 버튼을 클릭할 수 없다.

브라우저로 홈 리소스를 열고 링크를 따라갈 수는 있지만 GET만 가능하다. 새 예약을 하려면 POST가 필요하다.

### 3.1 테스트를 통해서 배우기

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 코드베이스에 포괄적인 테스트 스위트가 있다면 **테스트가 API 사용법을 알려주는 최고의 문서**가 된다.
:::

```csharp
// Restaurant/af31e63/Restaurant.RestApi.Tests/ReservationsTests.cs
[Fact]
public async Task ReserveTableAtNono()
{
    using var api = new SelfHostedApi();
    var client = api.CreateClient();

    var dto = Some.Reservation.ToDto();
    dto.Quantity = 6;
    var response = await client.PostReservation("Nono", dto);

    var at = Some.Reservation.At;
    await AssertRemainingCapacity(client, at, "Nono", 4);
    await AssertRemainingCapacity(client, at, "Hipgnosta", 10);
}
```

순환 복잡도 1, 활성화된 객체 6개, 14줄. 늘 그렇듯 읽기 쉽다. 추상화 수준이 높아 어설션이나 ``PostReservation`` 의 세부 구현은 여기서 알려주지 않는다. 궁금하면 확대해서 들어간다.

```csharp
internal static async Task<HttpResponseMessage> PostReservation(
    this HttpClient client,
    string name,
    object reservation)
{
    string json = JsonSerializer.Serialize(reservation);
    using var content = new StringContent(json);
    content.Headers.ContentType.MediaType = "application/json";
    var resp = await client.GetRestaurant(name);
    resp.EnsureSuccessStatusCode();
    var rest = await resp.ParseJsonContent<RestaurantDto>();
    var address = rest.Links.FindAddress("urn:reservations");
    return await client.PostAsync(address, content);
}
```

이 도우미 메서드는 reservation을 JSON으로 직렬화하고, POST 요청을 위한 적절한 주소를 찾아낸다. 이제 궁금증이 어느 정도 해소됐을 것이다. **프랙탈 아키텍처**가 동작하는 또 다른 예다.

### 3.2 테스트에 귀를 기울이자

『테스트 주도 개발로 배우는 객체지향 설계와 실천』의 모토는 **테스트에 귀를 기울이자(*Listen to the tests*)** 이다. 좋은 테스트는 시스템과의 상호작용 방법 이상을 알려준다.

**테스트 코드 역시 코드**다. 테스트 코드가 썩기 시작하면 프로덕션 코드처럼 리팩터링해야 한다. 그 과정에서 **테스트 유틸리티 메서드(*Test Utility Method - 여러 테스트에서 공용으로 사용되는 도우미 메서드*)** 가 자연스럽게 도입된다.

```csharp
internal static async Task<HttpResponseMessage> GetRestaurant(
    this HttpClient client,
    string name)
{
    var homeResponse =
        await client.GetAsync(new Uri("", UriKind.Relative));
    homeResponse.EnsureSuccessStatusCode();
    var homeRepresentation =
        await homeResponse.ParseJsonContent<HomeDto>();
    var restaurant =
        homeRepresentation.Restaurants.First(r => r.Name == name);
    var address = restaurant.Links.FindAddress("urn:restaurant");
    return await client.GetAsync(address);
}
```

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 자세히 보면 이 메서드에는 **테스트에 특화된 것이 하나도 없다**. 프로덕션 코드로도 유용하다면 옮기면 된다. 테스트가 자연스럽게 공식 클라이언트 SDK로 진화하는 순간이다.
:::

이런 발견은 언제나 행복하다. 이런 일이 벌어진다면 코드를 옮겨라. 모두에게 이득이다.

---

## 4. 결론

'진짜' 공학이란 **결정론적 과정과 인간의 판단이 혼합**된 것이다. 다리 하나를 세우려면 내하중 강도 계산도 필요하지만, 어떤 교통을 얼마나 지원할지, 온도 범위는 어디까지 감당할지, 지하도는 어떻게 할지 같은 무수한 판단이 필요하다.

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 공학이 완벽히 결정론적이라면 사람이 필요 없을 것이다. 로봇이면 충분하다. 미래에 그 지점에 도달하는 분야도 있겠지만, **그렇게 된다면 그것은 더 이상 공학이 아니라 제조업**이다. 소프트웨어 공학의 기술은 바로 이 결정론과 인간 판단이 만나는 지점에 존재한다.
:::

이 책이 소개한 것은 **지금 당장 채택할 수 있는** 여러 기술이다. 너무 진보적이라고 생각할 수 있지만, 모두 충분히 가능하다.

> 미래는 이미 여기 와 있다. 다만 고르게 퍼져 있지 않을 뿐이다.
> — 윌리엄 깁슨(William Gibson)

이 책에서 설명한 기술들은 그림의 떡이 아니다. 일부 조직에서는 이미 사용 중이다. **여러분도 할 수 있다.**

---

## 요약

- 코드베이스 탐색은 목적에 따라 다르다. 감을 익히려면 **진입점(Main → Startup → Configure)** 부터
- ``ConfigureServices`` 는 **목차** 역할 — 인증/DB/이메일 각 모듈로 확대 이동
- **파일 정리**: 디렉터리로 계층화하지 말고 평면에 두어라. IDE의 이동 기능을 활용
- 파일 시스템 트리는 **하나의 정리 축만 허용** — 다른 정리 축을 미리 배제하는 손실
- 프랙탈 아키텍처: 각 수준의 코드가 상위 맥락 없이 이해 가능. 세부로 들어가면 주변 잊어도 됨
- 샘플은 **모놀리식** — 함수형 코어/명령 셸 스타일로 잘 분리되어 있지만, 경험 없는 팀은 패키지 분리를 권장
- **순환 의존성**은 언어 차원(코드)이 아닌 **패키지 차원에서 차단**하는 것이 포카요케
- F#/하스켈은 언어 자체가 순환을 막고 포트-어댑터로 유도
- **테스트가 최고의 API 문서** — 프랙탈 구조라 원하는 만큼 확대해가며 학습
- 테스트 코드도 코드 — 리팩터링하다 프로덕션에 쓸 만한 코드를 발견하면 옮겨라(공식 SDK로 진화)
- 공학은 결정론과 인간 판단의 혼합. 완전 자동화되면 그것은 제조업. **소프트웨어 공학의 기술은 이 사이에 있다**
- 미래는 이미 여기 있다 — 다만 고르게 퍼져 있지 않을 뿐. **선택은 우리의 몫**
