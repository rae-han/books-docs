# Chapter 13: Separation of Concerns (관심사의 분리)

## 핵심 질문

데이터베이스 스키마를 바꿨더니 이메일 글꼴 크기가 변했다면 뭔가 크게 잘못된 것이다. 이메일 템플릿이 데이터베이스 스키마에 영향을 받아서는 안 된다. 이런 상황을 피하려면 "관련 없는 것은 분리한다"는 원칙이 필요하다. 그런데 **어떻게 분리해야** 하는가? 7장은 "언제, 왜" 분해해야 하는지를 다뤘지만, 이 챕터는 "어떻게" 분해해서 다시 조합할 수 있는가에 답한다.

---

## 1. 조합과 분해

**분해(*Decomposition - 큰 코드 단위를 작은 단위로 나누는 것*)** 만으로는 부족하다. 분해한 조각들이 다시 조합되어 동작하는 소프트웨어가 되어야 한다. 그러니 조합해서 만들어진 모델이 명확해야 한다.

여기서 저자는 폭탄 발언을 던진다.

> 객체지향 조합에는 문제가 있다.

### 1.1 중첩 조합 (Nested Composition)

객체지향 조합은 부수효과를 함께 구성하는 데 초점을 맞춘다. GoF의 컴포지트 패턴이 대표적이다. 객체 안에 객체가 중첩되고, 부수효과 안에 부수효과가 중첩된다. **읽고 이해하기 쉬운 코드**라는 목표에 정면으로 반한다.

나쁜 코드 예시를 살펴보자. 다음처럼 코드를 작성하지 말라는 반면교사다.

```csharp
public IRestaurantManager Manager { get; }

public async Task<ActionResult> Post(ReservationDto dto)
{
    if (dto is null)
        throw new ArgumentNullException(nameof(dto));
    Reservation? r = dto.Validate();
    if (r is null)
        return new BadRequestResult();
    var isAccepted =
        await Manager.Check(r).ConfigureAwait(false);
    if (!isAccepted)
        return new StatusCodeResult(
            StatusCodes.Status500InternalServerError);
    return new NoContentResult();
}
```

순환 복잡도 4, 코드 17줄. 얼핏 보면 괜찮아 보인다. 문제는 `Manager.Check`가 실제로 무엇을 하는지 이 코드만 봐서는 알 수 없다는 점이다.

```csharp
public interface IRestaurantManager
{
    Task<bool> Check(Reservation reservation);
}
```

이 메서드 이름을 X로 바꾸면 `Task<bool> X(Reservation reservation)`만 남는다. 얼핏 서술자(*predicate*)처럼 보이지만, 구현을 보면 데이터베이스에 예약을 저장한다.

```csharp
public async Task<bool> Check(Reservation reservation)
{
    // ... 유효성 검사 ...
    return await Manager.TrySave(reservation).ConfigureAwait(false);
}
```

**명령 쿼리 분리 원칙(*Command Query Separation - Bertrand Meyer가 제안. 메서드는 부수효과를 일으키는 명령이거나 값을 반환하는 쿼리 중 하나여야 하며, 둘을 섞으면 안 된다는 원칙, CQS*)** 을 위반한다. 쿼리처럼 생겼는데 부수효과가 있다.

로버트 마틴의 추상화 정의를 다시 보자.

> 추상화는 무관한 것을 제거하고, 본질적인 것을 강조하는 것입니다.

쿼리에 부수효과를 숨김으로써 이 코드는 본질적 동작을 **제거해버렸다**. `Post` 메서드 안에는 눈에 보이는 것보다 더 많은 일이 일어난다. 숨겨진 6번째 상호작용이 우리 뇌의 7 슬롯 중 하나를 조용히 갉아먹는다.

### 1.2 순차적 조합 (Sequential Composition)

중첩 조합 대신 **순차적 조합**을 쓸 수 있다. CQS에서 쿼리는 문제를 거의 일으키지 않는다. 쿼리는 다른 쿼리의 입력으로 사용할 수 있는 데이터를 반환하기 때문이다.

레스토랑 예약 코드는 이 원칙을 염두에 두고 작성됐다.

```csharp
internal bool Overlaps(Reservation other)
{
    var otherSeating = new Seating(SeatingDuration, other);
    return Start < otherSeating.End && otherSeating.Start < End;
}
```

`Overlaps`는 부수효과가 없고 데이터를 반환하는 쿼리다. LINQ의 내장 `Where`도 쿼리, `Overlaps`도 쿼리, `Allocate`도 쿼리, `Fits`도 쿼리다.

```csharp
private IEnumerable<Table> Allocate(
    IEnumerable<Reservation> reservations)
{
    List<Table> availableTables = Tables.ToList();
    foreach (var r in reservations)
    {
        var table = availableTables.Find(t => t.Fits(r.Quantity));
        if (table is { })
        {
            availableTables.Remove(table);
            if (table.IsCommunal)
                availableTables.Add(table.Reserve(r.Quantity));
        }
    }
    return availableTables;
}
```

`Where`의 출력이 `Allocate`의 입력이 되고, `Allocate`의 출력이 `Any`의 입력이 된다. 이 파이프라인 안에 부수효과는 없다. 결과가 어떻게 도출되었는지 코드만 보고 따라갈 수 있다.

### 1.3 참조 투명성 (Referential Transparency)

CQS는 쿼리의 결정론(*determinism*)까지는 강제하지 않는다. 같은 입력으로 호출해도 매번 다른 값이 반환되면 여전히 놀랄 수 있다 (예: 데이터베이스나 시간에 의존하는 쿼리).

여기에 한 가지 규칙을 더 추가해보자: **쿼리 결과는 결정론적이어야 한다**.

부수효과가 없고 출력이 입력에 의해서만 결정되는 함수를 **참조 투명(*Referential Transparency - 함수 호출을 그 결과값으로 대체해도 프로그램 동작이 변하지 않는 성질*)** 하다고 하며, 이를 **순수 함수(*Pure Function - 부수효과가 없고 결정론적인 함수*)** 라 부른다.

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 순수 함수 호출은 그 결과값으로 **치환**할 수 있다. 함수의 복잡도가 어떻든 뇌는 결과 하나만 추적하면 된다. 이것이야말로 "관련 없는 것을 제거하고 본질적인 것을 강조"한 것이다.
:::

`WillAccept` 메서드는 사실 단순한 쿼리가 아니라 순수 함수다. 확대해서 보면 주변 상태에 의존하지 않고 입력 인자와 불변 필드만 사용한다. 축소해서 보면 그 결과값 하나로 축약된다. 프랙탈 아키텍처에서 각 층이 뇌에 담기는 이유가 여기에 있다.

### 1.4 함수형 코어, 명령 셸

그런데 부수효과는 소프트웨어의 존재 이유이기도 하다 — 데이터베이스에 저장하고, 이메일을 보내고, 로그를 남긴다. 이걸 어떻게 다뤄야 할까?

답은 이렇다: **부수효과와 비결정성을 시스템의 가장자리로 밀어낸다**. `Main` 메서드, 컨트롤러, 메시지 핸들러 같은 얇은 껍질이 그 역할을 맡는다.

앞서 나쁜 코드 예제(예제 13-1)를 순차적 조합으로 고친 것이 다음이다.

```csharp
[HttpPost]
public async Task<ActionResult> Post(ReservationDto dto)
{
    if (dto is null)
        throw new ArgumentNullException(nameof(dto));
    var id = dto.ParseId() ?? Guid.NewGuid();
    Reservation? r = dto.Validate(id);
    if (r is null)
        return new BadRequestResult();
    var reservations = await Repository
        .ReadReservations(r.At)
        .ConfigureAwait(false);
    if (!MaitreD.WillAccept(DateTime.Now, reservations, r))
        return NoTables500InternalServerError();
    await Repository.Create(r).ConfigureAwait(false);
    return Reservation201Created(r);
}
```

`Post` 자체는 순수 함수가 아니다. GUID를 만들고 (비결정), DB에 쿼리하고 (비결정), 현재 시간을 가져오고 (비결정), 조건부로 DB에 저장한다 (부수효과). 하지만 **핵심 판단인 `WillAccept`는 순수 함수**다. 데이터를 모두 수집한 뒤 이 순수 함수에게 결정을 위임하고, 반환값에 따라 부수효과를 수행한다.

이 아키텍처를 **함수형 코어, 명령 셸(*Functional Core, Imperative Shell - Gary Bernhardt가 대중화. 순수 함수 코어를 부수효과 있는 얇은 껍질이 감싸는 아키텍처*)** 이라 부른다.

---

## 2. 횡단 관심사 (Cross-Cutting Concerns)

시스템의 여러 부문에 걸쳐 반복해서 고려해야 하는 기능들이 있다.

- 로그 남기기 (logging)
- 성능 모니터링
- 감사 (auditing)
- 계량 (metering)
- 계측 (instrumentation)
- 캐싱
- 내결함성 (회로 차단기 등)
- 보안

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 횡단 관심사에는 공통점이 있다. 바로 **데코레이터 패턴으로 구현하는 것이 가장 좋다**는 것이다.
:::

### 2.1 로그 남기기의 원칙

- 처리되지 않은 예외는 최소한 자동으로 로그에 기록되게 만든다
- 로그에 나타나는 예외 수의 이상적인 값은 **0**이다. 예외가 나오면 결함으로 처리
- 일부 결함은 예외를 던지지 않고 **잘못 동작**한다. 이런 경우를 파악하려면 예외 이상의 로그가 필요

### 2.2 데코레이터 (Decorator)

**데코레이터 패턴(*Decorator Pattern - 다형성을 이용해 같은 인터페이스를 구현하는 객체가 다른 객체를 감싸 기능을 추가하는 GoF 디자인 패턴. 러시아 마트료시카 인형에 비유됨*)** 은 다형성 객체를 안쪽으로 중첩시켜 원래 구현을 건드리지 않고 기능을 추가한다.

`SqlReservationsRepository`에 로깅을 추가한다고 하자. 그 클래스 자체를 편집하는 대신 데코레이터를 만든다.

```csharp
public sealed class LoggingReservationsRepository : IReservationsRepository
{
    public LoggingReservationsRepository(
        ILogger<LoggingReservationsRepository> logger,
        IReservationsRepository inner)
    {
        Logger = logger;
        Inner = inner;
    }
    public ILogger<LoggingReservationsRepository> Logger { get; }
    public IReservationsRepository Inner { get; }
}
```

각 메서드는 `Inner`의 같은 메서드를 호출하는 사이에 로깅을 끼워 넣는다.

```csharp
public async Task<Reservation?> ReadReservation(Guid id)
{
    var output = await Inner.ReadReservation(id).ConfigureAwait(false);
    Logger.LogInformation(
        "{method}({id}) => {output}",
        nameof(ReadReservation),
        id,
        JsonSerializer.Serialize(output?.ToDto()));
    return output;
}
```

DI 컨테이너에서는 람다 팩토리로 데코레이터를 감싸 등록한다.

```csharp
var connStr = Configuration.GetConnectionString("Restaurant");
services.AddSingleton<IReservationsRepository>(sp =>
{
    var logger =
        sp.GetService<ILogger<LoggingReservationsRepository>>();
    return new LoggingReservationsRepository(
        logger,
        new SqlReservationsRepository(connStr));
});
```

캐싱 데코레이터라면 캐시를 먼저 조회하고, 없으면 `Inner`를 호출하고 결과를 캐시에 담아 반환한다. 이를 **연속 읽기 캐시(*Read-Through Cache - 캐시 미스 시 캐시가 스스로 원본에서 읽어와 캐시를 채우는 패턴*)** 라 한다.

### 2.3 무엇을 로그로 남길까 — 금쪽같은 로그

너무 많이 남기는 것보다는 낫지만, **딱 필요한 만큼만** 남기는 것이 이상적이다. 이를 저자는 **금쪽같은 로그(*Goldilogs - 골디락스에서 따온 저자의 조어. 너무 적지도 너무 많지도 않은 딱 적당한 로그*)** 라 부른다.

기준은 **재현성**이다. 문제가 발생했을 때 재현할 수 있으면 해결할 수 있다.

```csharp
int z = x + y;
```

이 문장에 로그를 남겨야 할까? `x`와 `y`가 사용자 입력이나 웹 서비스 결과라면 남기는 것이 합리적이다.

```csharp
Log.Debug($"Adding {x} and {y}.");
int z = x + y;
```

그럼 결과 `z`는? **아니다**. 덧셈은 순수 함수이므로 결정론적이다. 입력을 알면 결과는 재계산할 수 있다. 2 + 2는 항상 4다.

| 로그 대상 여부 | 예시 |
|---|---|
| 반드시 로그 | 현재 날짜/시간, 난수 생성, GUID 생성, 파일/DB 읽기, 외부 호출 결과 |
| 반드시 로그 | 부수효과가 있는 모든 것 (DB 쓰기, 이메일 전송 등) |
| 로그 불필요 | 순수 함수의 결과 |
| 로그 불필요 | 입력만 알면 재현 가능한 모든 것 |

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 코드에 순수 함수가 많을수록 로깅해야 할 부분이 줄어든다. **참조 투명성이 왜 바람직한지에 대한 또 다른 이유이자, 함수형 코어·명령 셸 아키텍처를 선택해야 하는 이유**다.
:::

물론 코드베이스에서 순수/비순수를 분리하지 않았다면 모든 것을 기록해야 한다. 그것이 "과도한 로깅"의 진짜 원인이다.

---

## 3. 결론

관련 없는 관심사들은 분리한다. 하지만 분해는 재조합할 수 있을 때만 의미가 있다.

객체지향 조합은 원래 약속과 달리 이 문제에 잘 맞지 않았다. 대부분의 개발자는 어떻게 분해할지 모르는 채 객체를 **중첩**시키는 방식으로 조합한다. 이는 중요한 동작을 숨겨 코드를 읽고 이해하기 어렵게 만든다.

순수 함수의 반환값이 다른 순수 함수의 입력으로 이어지는 **순차적 조합**이 더 좋은 대안이다. 회사의 객체지향 코드베이스를 하루아침에 Haskell로 갈아치우자는 것은 아니다. 대신 **함수형 코어, 명령 셸** 방향으로 나아가는 것을 권한다.

그렇게 하면 순수 함수로 구현할 수 없는 부분이 자연스럽게 분리되고, 그 부분이야말로 데코레이터로 횡단 관심사를 얹기에 알맞은 자리다.

---

## 요약

- 관심사의 분리 = 다른 속도로 변하는 것은 분리하고, 같은 속도로 변하는 것은 함께 둔다 (켄트 벡)
- 분해는 재조합할 수 있어야 의미가 있다. **어떻게 조합할 것인가**가 핵심 질문
- **중첩 조합**(객체 안에 객체)은 부수효과를 숨겨 코드를 이해하기 어렵게 만든다. CQS 위반의 흔한 형태
- **순차적 조합**(한 쿼리의 출력이 다음 쿼리의 입력)이 훨씬 이해하기 쉽다. 부수효과가 개입하지 않아 뇌가 추적할 상태가 적다
- **참조 투명성**(순수 함수)은 함수 호출을 결과값으로 치환할 수 있게 해준다. 복잡도가 하나의 값으로 축약된다
- **함수형 코어, 명령 셸** 아키텍처: 순수 함수를 시스템의 핵심에 두고 부수효과·비결정성은 얇은 껍질(컨트롤러, `Main`)로 밀어낸다
- **횡단 관심사**(로깅, 캐싱, 회로 차단기, 보안 등)는 **데코레이터 패턴**으로 처리한다. 원 구현을 건드리지 않고 감싸는 방식
- **로그의 원칙**: 재현할 수 없는 것(외부 입력, 시간, 난수, DB 읽기 결과, 부수효과)은 남긴다. 순수 함수의 결과는 남기지 않는다
- 함수형 코어를 늘릴수록 로그 대상이 줄어든다. **참조 투명성이 로깅 부담을 줄여준다**
