# Chapter 6: Triangulation (다각화하기)

## 핵심 질문

새로운 기능을 어떻게 코드에 안전하게 도입하는가? 하나의 테스트만으로는 왜 부족한가? "테스트는 언제 충분한가?"라는 질문에 어떻게 답할 것인가? 그리고 왜 우리는 애초에 코드를 **여러 개의 작은 덩어리**로 나누어야 하는가?

---

## 1. 단기 기억과 장기 기억

몇 년 전 저자는 한 고객사의 레거시 코드베이스를 도와달라는 요청을 받았다. 개발자들과 인터뷰를 진행하면서, 가장 최근에 합류한 팀원에게 "스스로 프로젝트에 기여하고 있다는 느낌이 들 때까지 얼마나 걸렸는지"를 물었다. 대답은 **"3개월이요"** 였다.

코드에 손을 대도 되겠다는 자신감이 생길 때까지 걸린 시간이 3개월이라는 뜻이다. 실제로 그 코드베이스를 살펴보니 하나의 메서드에서 7가지 이상의 일이 동시에 진행되는 것이 흔했고, 어떤 메서드는 70가지가 넘는 일을 처리하고 있었다.

3장에서 인간의 **단기 기억(*Short-term Memory - "작업 기억(working memory)"이라고도 함. 뇌가 동시에 다룰 수 있는 정보 덩어리의 수, 대략 7±2개*)** 은 대략 7개의 덩어리를 다룰 수 있다고 했다. 그렇다면 어떻게 개발자들은 7가지가 넘는 일들을 다루는 코드베이스를 이해할 수 있었을까? 답은 **장기 기억(*Long-term Memory - 단기 기억과 다른 시스템으로, 훨씬 큰 용량을 가지고 오래 유지되는 기억*)** 에 있다.

두뇌를 컴퓨터에 비유하는 것은 조심해야 하지만, 단기 기억과 장기 기억의 관계는 RAM과 하드 드라이브에 비유될 만하다. 단기 기억의 대부분은 범위를 벗어나면 사라지지만, 일부는 장기 기억에 도달해 오랫동안 남는다. 반대로 장기 기억에 있는 정보를 단기 기억으로 불러와서 작업에 쓸 수도 있다.

### 1.1 레거시 코드가 만드는 두 가지 문제

레거시 코드로 작업할 때는 **코드베이스의 구조를 천천히, 그리고 고생스럽게 장기 기억에 저장하는 과정**을 거친다. 이것은 두 가지 심각한 문제를 낳는다.

- **코드베이스를 익히는 데 시간이 걸린다.**
- **한 번 익힌 코드는 바꾸기 어렵다.**

첫 번째 문제만으로도 채용 담당자를 곤란하게 만든다. 새로 들어온 엔지니어가 정상적인 생산성을 낼 때까지 3개월이 걸린다면, 기존 프로그래머는 **대체 불가능한 존재**가 된다. 다소 냉소적으로 말하면 레거시 코드를 만드는 것이 개인의 고용 안정성 확보에는 유리한 셈이다. 다만 그 지식은 다른 곳에서는 쓸모가 없기 때문에 이직에는 도리어 걸림돌이 된다.

두 번째 문제는 더 나쁘다. 장기 기억까지 도달한 정보는 바꾸기가 더 어렵다. 복잡한 시스템을 조금 덜 복잡한 시스템으로 리팩터링하더라도, 여전히 머리에 잘 안 들어올 만큼 복잡하다면 어떻게 될까? 왼쪽(복잡한 원본)은 이미 기억하고 있었던 것인 반면, 오른쪽(리팩터링된 결과)은 새로운 것이므로, 힘들게 얻은 지식은 쓸모없어지고 그 자리를 잘 모르는 것이 차지한다.

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 애초에 레거시 코드를 작성하지 않는 것이 가장 좋은 전략이다. 코드베이스는 처음부터 **머리에 잘 들어오는 크기**로 유지되어야 한다.
:::

---

## 2. 용량 — 뇌 크기의 덩어리로 자르기

작업 기억의 용량은 7개 안팎에 불과하다. 그러므로 소프트웨어 공학의 핵심 과제는 **동시에 진행되는 일의 수를 제한**하는 것, 즉 코드를 뇌가 받아들일 수 있는 작은 덩어리로 나누는 것이다.

> 소프트웨어 설계의 목표는 인간의 머리에 잘 들어오는 덩어리 혹은 조각을 만드는 것입니다. 소프트웨어는 계속 커지지만, 인간의 정신은 한계가 있기 때문에 계속 변화를 주려면 다른 방식으로 쪼개고 분리해야 합니다.
> — 켄트 벡(Kent Beck)

이런 분리 방법은 예제를 통해 배우는 것이 가장 좋다. 앞장까지의 예제는 너무 간단해서 나눌 것이 없었다. 이제 조금 더 복잡한 상황 — 레스토랑 예약 시스템의 **초과 예약** 문제를 다룬다.

### 2.1 초과 예약(Overbooking)

지금까지 만든 예약 시스템은 최소한의 입력 유효성 검사만 수행한다. 인원이 양수이기만 하면 미래는 물론 과거 날짜에 대한 예약까지도 허용한다. 실제 레스토랑에는 **물리적인 수용 인원 한계**가 있고, 특정 날짜에는 이미 만석일 수도 있다. 따라서 시스템은 **기존 예약 인원 합계 + 신규 예약 인원**이 수용 인원을 초과하지 않는지 확인해야 한다.

이 기능을 추가하기 전에 테스트를 먼저 작성한다. 5장에서 본 최신 버전의 `Post` 메서드는 성공하면 `204 No Content`를 반환한다. **변환 우선순위 전제(*Transformation Priority Premise - Robert C. Martin이 제안한, "무조건문 → 조건문", "상수 → 스칼라"처럼 코드 변환의 우선순위를 정한 목록, TPP*)** 에 따르면 가장 먼저 시도해야 할 변환은 "**무조건문 → 조건문**"이다. 즉 지금은 항상 성공하는 경로를 조건문으로 갈라, **초과 예약일 때는 오류 상태**를 반환하도록 만들어야 한다.

이 동작을 유도하는 첫 테스트는 예제 6-1과 같다.

```csharp
[Fact]
public async Task OverbookAttempt()
{
    using var service = new RestaurantApiFactory();
    await service.PostReservation(new
    {
        at = "2022-03-18 17:30",
        email = "mars@example.edu",
        name = "Marina Seminova",
        quantity = 6
    });

    var response = await service.PostReservation(new
    {
        at = "2022-03-18 17:30",
        email = "shli@example.org",
        name = "Shanghai Li",
        quantity = 5
    });

    Assert.Equal(
        HttpStatusCode.InternalServerError,
        response.StatusCode);
}
```

같은 시간대(17:30)에 이미 6인이 예약된 상태에서 5인 추가 예약을 시도하면, 총 11인이 되어 레스토랑 용량(예: 10)을 넘는다. 그러므로 두 번째 응답은 성공이 아닌 오류(500 Internal Server Error)여야 한다. 여기서는 레스토랑의 수용 인원을 **암시적으로** 처리했지만, 나중에 이 부분은 명확하게 바꿔야 한다는 점을 유의하자.

### 2.2 악마의 변호인 — 테스트를 통과시키는 가장 뻔뻔한 방법

첫 테스트를 통과시키기 위한 **가장 간단한 구현**은 무엇일까? 저자는 여기서 의도적으로 "악마의 변호인(*Devil's Advocate - 일부러 잘못된, 그러나 테스트를 통과하는 최소 구현을 작성해 테스트의 취약성을 드러내는 사고 실험*)" 태도를 취한다. 즉 "테스트만 통과하면 되는가?"라는 질문에 아주 뻔뻔하게 답한다.

```csharp
public async Task<ActionResult> Post(ReservationDto dto)
{
    if (dto is null)
        throw new ArgumentNullException(nameof(dto));
    if (!DateTime.TryParse(dto.At, out var d))
        return new BadRequestResult();
    if (dto.Email is null)
        return new BadRequestResult();
    if (dto.Quantity < 1)
        return new BadRequestResult();

    if (dto.Email == "shli@example.org")
        return new StatusCodeResult(
            StatusCodes.Status500InternalServerError);

    var r = new Reservation(d, dto.Email, dto.Name ?? "", dto.Quantity);
    await Repository.Create(r).ConfigureAwait(false);
    return new NoContentResult();
}
```

`dto.Email == "shli@example.org"`이면 500을 반환한다. **모든 테스트가 통과한다.** 그러나 이 코드는 명백히 잘못됐다. 프로덕션에서 초과 예약 방지에는 아무 쓸모가 없다.

이 뻔뻔한 구현이 던지는 메시지는 명확하다. **테스트 하나로는 원하는 동작을 제대로 기술하지 못한다.** 로버트 마틴은 이를 다음과 같이 정리한다.

> 테스트가 더 구체적일수록 코드는 더 포괄적이 됩니다.
> — Robert C. Martin

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 악마의 변호인은 "이 테스트만 있으면 이 잘못된 코드도 살아남을 수 있는가?"를 스스로에게 묻는 렌즈다. 이 질문에 "예"라고 답할 수 있다면 테스트가 부족한 것이다.
:::

### 2.3 다각화(Triangulation) — 두 번째 측정 지점 추가하기

악마의 변호인을 반박하려면 **두 번째 테스트**가 필요하다. 어디에 추가해야 할까?

새 테스트를 **`OverbookAttempt`에 붙이면 안 된다.** 그 테스트는 이미 자기 역할을 다했다. 대신, 유효한 예약이 데이터베이스에 저장되는 경로를 검증하던 기존 파라미터화 테스트 `PostValidReservationWhenDatabaseIsEmpty`에 `[InlineData]` 행 하나를 더 추가한다.

```csharp
[Theory]
[InlineData("2023-11-24 19:00", "juliad@example.net", "Julia Domna", 5)]
[InlineData("2024-02-13 18:15", "x@example.com", "Xenia Ng", 9)]
[InlineData("2023-08-23 16:55", "kite@example.edu", null, 2)]
[InlineData("2022-03-18 17:30", "shli@example.org", "Shanghai Li", 5)]
public async Task PostValidReservationWhenDatabaseIsEmpty(
    string at, string email, string name, int quantity)
{
    var db = new FakeDatabase();
    var sut = new ReservationsController(db);
    var dto = new ReservationDto { At = at, Email = email, Name = name, Quantity = quantity };

    await sut.Post(dto);

    var expected = new Reservation(
        DateTime.Parse(dto.At, CultureInfo.InvariantCulture),
        dto.Email, dto.Name ?? "", dto.Quantity);
    Assert.Contains(expected, db);
}
```

4번째 `[InlineData]` 행은 악마가 하드코딩했던 바로 그 값(`shli@example.org`, `2022-03-18 17:30`, 5명)을 사용한다. 다만 이번에는 **데이터베이스가 비어 있는 상황**에서 호출한다. 이 경우에는 초과 예약이 아니므로 정상적으로 저장되어야 한다.

그러나 악마의 구현은 `Email == "shli@example.org"`이면 무조건 500을 반환하므로, 이 테스트에서는 실패한다. `Assert.Contains(expected, db)`가 실패하는 것이다. 이제 이메일 문자열 하드코딩으로는 두 테스트를 동시에 통과시킬 수 없다. 개발자는 억지로 만든 조건문을 지우고 **진짜 로직**을 작성할 수밖에 없다.

이것이 **다각화(triangulation)** 다. 기하학에서 두 개의 측정 지점만 있으면 목표 지점의 위치를 특정할 수 있듯이, 두 개의 테스트가 서로 다른 각도에서 SUT(*System Under Test - 테스트 대상 시스템*)를 겨냥하면, 개발자가 취할 수 있는 자유도가 좁아진다.

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 왜 새 테스트를 `OverbookAttempt`가 아니라 `PostValidReservationWhenDatabaseIsEmpty`에 추가했는가? 변환 우선순위 전제 때문이다. 지금 필요한 변환은 "**상수 → 변수**" — 즉 이메일이라는 특정 상수 값에 대한 분기를, "예약 수량 합계"라는 변수에 대한 분기로 옮기는 것이다. 각 테스트는 자기 관심사를 지켜야 한다.
:::

### 2.4 기존 예약 다루기 — 리포지토리에 새로운 능력 추가

이제 진짜 로직을 쓰기 위해서는 **해당 날짜의 기존 예약**을 읽어와야 한다. 그래서 `IReservationsRepository`에 다음 메서드를 추가한다.

```csharp
Task<IReadOnlyCollection<Reservation>> ReadReservations(DateTime dateTime);
```

`FakeDatabase`는 LINQ를 이용해서 이 메서드를 구현한다.

```csharp
public Task<IReadOnlyCollection<Reservation>> ReadReservations(DateTime dateTime)
{
    var min = dateTime.Date;
    var max = min.AddDays(1).AddTicks(-1);
    return Task.FromResult<IReadOnlyCollection<Reservation>>(
        this.Where(r => min <= r.At && r.At <= max).ToList());
}
```

여기서 `Where` 조건식에 주목하자. `min <= r.At && r.At <= max` — 이 식은 **수직선의 순서**대로 읽힌다. 왼쪽에서 오른쪽으로 읽으면 "min 이하 이하 r.At 이하 이하 max"가 되어, 값 세 개가 수직선 위에서 어떤 순서로 배치되는지가 그대로 문장이 된다.

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰 — 숫자 표현은 수직선 순서로**: 범위 비교에서는 항상 `<`와 `<=`만 사용하고, `>`와 `>=`는 쓰지 않는다. `r.At >= min && r.At <= max`는 같은 뜻이지만 읽는 사람의 머릿속에서 방향이 두 번 반전되어야 한다. 반면 `min <= r.At && r.At <= max`는 **수학 교과서의 부등식 표기 그대로**이므로, 두뇌의 단기 기억 자원을 낭비하지 않는다.
:::

이것은 사소해 보이지만 강력한 휴리스틱이다. 코드 한 줄을 이해하는 데 드는 인지 비용을 줄이는 것이 곧 **머리에 잘 들어오는 코드**를 만드는 길이다.

### 2.5 악마의 변호인 vs 빨강-초록-리팩터

`ReadReservations`를 사용해서 `Post`를 다시 쓴다. 하지만 여기서도 악마의 변호인은 여전히 뻔뻔하다. 다음처럼 쓰면 어떨까?

```csharp
var reservations = await Repository.ReadReservations(d).ConfigureAwait(false);
int reservedSeats = reservations.Select(r => r.Quantity).SingleOrDefault();
if (10 < reservedSeats + dto.Quantity)
    return new StatusCodeResult(
        StatusCodes.Status500InternalServerError);
```

`SingleOrDefault`는 컬렉션에 원소가 0개면 기본값(0)을, 1개면 그 값을 반환하고, 2개 이상이면 예외를 던진다. 현재 테스트 시나리오에서 예약은 항상 0개 또는 1개이므로 **이 코드로도 모든 테스트가 통과한다**. 그러나 실제로 같은 시간대에 예약이 2개 이상 있으면 예외가 터진다. 명백히 잘못된 코드다.

여기서 저자는 **테스트를 하나 더 추가하는 대신, 리팩터링으로 대응**한다. `SingleOrDefault` 대신 `Sum`을 쓰면 예약이 몇 개든 상관없이 인원의 합계가 나온다. 이것이 "빨강-초록-리팩터" 사이클의 **리팩터** 단계다.

```csharp
public async Task<ActionResult> Post(ReservationDto dto)
{
    if (dto is null)
        throw new ArgumentNullException(nameof(dto));
    if (!DateTime.TryParse(dto.At, out var d))
        return new BadRequestResult();
    if (dto.Email is null)
        return new BadRequestResult();
    if (dto.Quantity < 1)
        return new BadRequestResult();

    var reservations =
        await Repository.ReadReservations(d).ConfigureAwait(false);
    int reservedSeats = reservations.Sum(r => r.Quantity);
    if (10 < reservedSeats + dto.Quantity)
        return new StatusCodeResult(
            StatusCodes.Status500InternalServerError);

    var r = new Reservation(d, dto.Email, dto.Name ?? "", dto.Quantity);
    await Repository.Create(r).ConfigureAwait(false);
    return new NoContentResult();
}
```

여기서도 여전히 `10`이라는 숫자가 하드코딩되어 있다는 점에 주목하자. 레스토랑의 수용 인원은 실제로는 설정값이어야 한다. 그러나 지금 시점에서 이는 불완전한 상태로 남겨둔다. 한 번에 하나씩 진행하기 위함이다.

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 악마의 변호인이 반박당하는 방법은 두 가지다. (1) 다각화 — 새 테스트로 잘못된 구현을 무너뜨리기. (2) 리팩터링 — 이미 있는 코드를 더 일반적인 형태로 다시 쓰기. 어느 쪽이 더 나은지는 상황이 정한다. 테스트를 더 늘리면 **테스트 유지 비용**이 커지고, 리팩터링을 선택하면 **개발자의 판단**에 의존한다.
:::

### 2.6 테스트는 언제 충분한가

TDD를 배우는 사람이 늘 부딪히는 질문이 있다.

> **"테스트를 얼마나 더 써야 하죠?"**

이 질문에 대한 저자의 답은 표준적인 위험 평가 프레임이다.

> 코드가 더 나빠지는 **퇴행(regression)** 이 일어날 가능성은 얼마나 될까? 그리고 그 퇴행의 영향은 얼마나 클까?

- **가능성이 낮고 영향도 작다** → 지금 있는 테스트로 충분하다.
- **가능성이 낮지만 영향이 크다** → 안전을 위한 테스트를 하나 더 쓴다.
- **가능성이 높다** → 반드시 테스트를 추가한다.

특히 프로덕션에서 이미 발생한 퇴행이라면, **자동화된 테스트로 반드시 재현**해야 한다. 재현하지 않으면 같은 버그가 다시 등장한다.

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: "테스트를 얼마나 써야 하는가?"의 답은 **커버리지 숫자**가 아니라 **위험 감수 태도**다. 악마의 변호인은 여기서 유용한 심리적 장치다 — "만약 내가 악의를 가지고 최소한만 구현한다면 이 테스트들이 나를 잡을 수 있는가?"라고 스스로에게 묻는 것이다.
:::

---

## 3. 결론 — 다각측량이라는 은유

기하학의 **삼각측량(triangulation)** 은 두 지점의 관측만으로 미지의 목표 지점 위치를 결정한다. 흥미로운 점은, 기하학에서는 목표 지점이 이미 **존재**한다는 것이다. 다만 그 위치가 알려지지 않았을 뿐이다.

TDD의 다각화는 다르다. 여기서는 **SUT가 아직 존재하지 않는다.** 존재하는 것은 오직 **측정 지점들(테스트들)** 뿐이다. 각 테스트는 아직 태어나지 않은 SUT의 특정 각도에서의 프로필을 기술한다. 테스트가 많을수록 SUT의 형태가 더 정밀하게 결정된다.

이 장에서 본 상호작용을 정리하면 다음과 같다.

| 도구 | 역할 |
|---|---|
| **변환 우선순위 전제(TPP)** | 다음에 어떤 변환을 시도할지 순서를 정한다 (무조건문 → 조건문 → 상수 → 변수 → …) |
| **악마의 변호인** | 현재 테스트들이 얼마나 뻔뻔한 구현까지 허용하는지 드러내는 렌즈 |
| **다각화** | 잘못된 구현을 무너뜨리기 위해 **다른 관심사**의 테스트에 새 시나리오를 추가 |
| **빨강-초록-리팩터** | 새 테스트를 추가하지 않고, 코드를 더 일반적인 형태로 재작성 |
| **위험 평가** | "언제 충분한가"를 커버리지가 아니라 **퇴행 위험**으로 결정 |

이 다섯 가지 도구는 서로 겹치기보다 서로를 보완한다. TPP는 다음 걸음의 방향을 정하고, 악마의 변호인은 지금까지의 걸음이 충분히 정교했는지 검사하며, 다각화와 리팩터링은 걸음의 두 가지 응답 방식이다. 그리고 위험 평가는 언제 걸음을 멈출지를 알려준다.

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 이 도구들의 상호작용은 결과적으로 **중복 없는 포괄적 커버리지**를 만든다. 각 테스트는 자기만의 관심사를 갖고, 서로 다른 각도에서 SUT를 겨냥한다. 이것이 코드베이스가 자라도 테스트가 유지 가능한 이유다.
:::

궁극적으로 이 장의 메시지는 하나다. **소프트웨어는 사람의 머리에 잘 들어와야 한다.** 그러기 위해서는 코드를 작은 덩어리로 분리하고, 각 덩어리가 정말 원하는 동작만 하도록 좁혀야 한다. 테스트는 그 좁힘의 도구다.

---

## 요약

- 인간의 뇌에는 **단기 기억(7±2 덩어리)** 과 **장기 기억**이 있다. 레거시 코드는 장기 기억에 억지로 저장되므로 (1) 익히는 데 오래 걸리고, (2) 바꾸기가 어렵다
- 소프트웨어 설계의 목표는 켄트 벡의 말처럼 **"인간의 머리에 잘 들어오는 덩어리"** 를 만드는 것 — 동시에 진행되는 일의 수를 제한한다
- **변환 우선순위 전제(TPP)** 에 따르면 첫 변환은 "무조건문 → 조건문"이다. 초과 예약 테스트는 항상 성공하던 경로에 오류 분기를 추가하는 첫걸음
- **악마의 변호인**은 "테스트만 통과시키는 뻔뻔한 최소 구현"을 상상하는 사고 실험이다. 이 렌즈로 보면 테스트가 충분한지 알 수 있다
- 로버트 마틴: **"테스트가 더 구체적일수록 코드는 더 포괄적이 된다."** 다각화(triangulation)로 두 번째 측정 지점을 추가하면 잘못된 구현이 살아남을 수 없다
- 새 테스트는 **자기 관심사의 테스트에 붙인다** — 데이터베이스가 비어있을 때 저장되는지를 보는 테스트에는 정상 저장 시나리오를, 초과 예약 방지 테스트에는 초과 시나리오를
- **범위 비교는 수직선 순서로 쓴다**: `min <= r.At && r.At <= max`. `>`/`>=`를 쓰지 않는 이유는 인지 비용을 줄이기 위함
- 악마의 변호인에 대응하는 두 가지 방법: (1) **다각화**로 새 테스트 추가, (2) **리팩터링**으로 더 일반적인 코드로 재작성. `SingleOrDefault` → `Sum`이 후자의 예
- **"테스트는 언제 충분한가?"**의 답은 커버리지가 아니라 **퇴행 위험 평가**다. 프로덕션 버그는 반드시 자동화 테스트로 재현
- 기하학의 삼각측량과 달리 TDD에서는 **SUT가 아직 없다**. 존재하는 것은 측정 지점(테스트)뿐이며, 여러 테스트가 SUT의 형태를 결정한다
- TPP + 악마의 변호인 + 빨강-초록-리팩터 + 위험 평가는 겹치지 않고 서로를 보완하며, 결과적으로 **중복 없는 포괄적 커버리지**를 만든다
