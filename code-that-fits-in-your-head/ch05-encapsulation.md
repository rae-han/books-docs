# Chapter 5: Encapsulation (캡슐화하기)

## 핵심 질문

객체가 합리적으로 작동한다고 어떻게 신뢰할 수 있는가? getter와 setter로 필드를 감싸는 것이 정말 캡슐화인가? 유효한 입력이 무엇이고, 무엇이 유효하지 않은지를 어떻게 결정해야 할까? 왜 **불변** 객체가 캡슐화에 유리한가?

---

## 서두 — 계약이라는 은유

집·땅·회사·자동차 같이 가치가 높은 것을 구입한 적이 있는가? 그렇다면 아마도 계약을 체결했을 것이다. **계약(*Contract - 쌍방의 권리와 의무를 규정하고 형식을 정한 약속*)** 은 판매자의 의무(자산 양도)와 구매자의 의무(대금 지불)를 규정한다. 판매자는 자산 상태에 대해 보증을 제공할 수 있고, 구매자는 거래 후 특정 손해에 대한 책임을 묻지 않기로 약속한다.

계약이란 원래 존재하지 않았을 **일정 수준의 신뢰**를 도입하고 형식을 정하는 일이다. 낯선 사람을 믿는 것은 위험하지만 계약이라는 제도를 통해 조금 더 안전하게 처리할 수 있다.

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 이것이 바로 **캡슐화**다. 객체가 합리적으로 작동한다고 어떻게 신뢰할 수 있는가? **객체가 그렇게 작동하게끔 계약을 맺으면 된다.**
:::

---

## 1. 데이터 저장하기

4장은 사실 제대로 동작하는 것을 확인하지 못한 채 끝났다. `Post` 메서드가 수신한 데이터를 무시하고 미리 하드코딩한 예약을 저장했기 때문이다. 이 결함을 해결하는 김에 캡슐화도 함께 다뤄본다.

### 1.1 변환 우선순위 전제

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 개발 방법론에 입각해 코드를 작성하도록 유도하는 **수단**을 꼭 사용하자. 저자는 팀을 코칭할 때 개발자들에게 끊임없이 이야기한다 — **속도를 늦추라.** 테스트 또는 분석기 같은 수단을 하나씩 도입하고, 이에 대응하면서 프로덕션 코드를 작성한다.
:::

코드를 고친다는 건 코드를 하나의 상태에서 다른 상태로 바꾼다는 의미다. 이런 변환은 **원자적(*Atomic - 도중에 끊길 수 없는*)** 으로 일어나지 않기 때문에 고치는 동안에는 컴파일이 되지 않을 수 있다. 코드가 유효하지 않은 시간을 최대한 짧게 유지해야 두뇌가 추적할 항목의 수를 줄일 수 있다.

2013년 로버트 마틴이 발표한 **변환 우선순위 전제(*Transformation Priority Premise - 코드 변경을 작은 단계로 나누고, 단순한 변환부터 복잡한 변환 순서로 진행하는 지침*)** 목록의 일부는 다음과 같다.

- (∅ → nil): 코드 없음 → nil로 코드 작성하기
- (nil → 상수)
- (상수 → 상수+): 단순 상수 → 조금 더 복잡한 상수
- (상수 → 스칼라 변수): 상수를 변수/매개변수로 바꾸기
- (문장 → 여러 문장): 조건 없는 문장 추가
- (무조건 → 조건): 실행 경로 나누기
- (스칼라 → 배열)
- (배열 → 컨테이너 변수)
- (문장 → 재귀)
- (조건 → 반복)
- (수식 → 함수)
- (변수 → 할당문)

간단한 변환이 위에, 복잡한 변환이 아래에 온다. 엄격한 규칙이 아니라 **생각할 거리**를 주는 지침이다. 현재 `Post`는 상수를 저장하고 있으므로, "상수 → 스칼라 변수" 변환을 적용해 dto의 값을 가져와 저장하도록 바꾸면 된다.

### 1.2 매개변수를 이용하는 테스트

기존 테스트를 조금 바꿔 매개변수를 사용할 수 있게 만든다.

```csharp
[Theory]
[InlineData("2023-11-24 19:00", "juliad@example.net", "Julia Domna", 5)]
[InlineData("2024-02-13 18:15", "x@example.com", "Xenia Ng", 9)]
public async Task PostValidReservationWhenDatabaseIsEmpty(
    string at, string email, string name, int quantity)
{
    var db = new FakeDatabase();
    var sut = new ReservationsController(db);
    var dto = new ReservationDto {
        At = at, Email = email, Name = name, Quantity = quantity
    };

    await sut.Post(dto);

    var expected = new Reservation(
        DateTime.Parse(dto.At, CultureInfo.InvariantCulture),
        dto.Email, dto.Name, dto.Quantity);
    Assert.Contains(expected, db);
}
```

`[Fact]` 대신 `[Theory]` 속성과 `[InlineData]`로 여러 테스트 케이스를 제공한다. 어설션이 프로덕션 코드와 비슷해 보이는 게 거슬리지만, "**완벽은 좋은 것의 적**"이다. 이 테스트의 목적은 `Post`가 하드코딩된 값만 저장한다는 사실을 보여주는 것이다.

### 1.3 DTO를 도메인 모델로 복사하기

```csharp
public async Task Post(ReservationDto dto)
{
    if (dto is null)
        throw new ArgumentNullException(nameof(dto));

    var r = new Reservation(
        DateTime.Parse(dto.At!, CultureInfo.InvariantCulture),
        dto.Email!,
        dto.Name!,
        dto.Quantity);
    await Repository.Create(r).ConfigureAwait(false);
}
```

`dto.At!`처럼 느낌표(`!`)가 붙어 있는 이유는 이 코드베이스가 C#의 널 가능 참조 형식을 켜두었기 때문이다. `!` 연산자는 "이건 널이 아니다"라고 컴파일러에 우기는 것으로, 경고를 숨기는 것뿐이다.

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: `!` 연산자는 좋지 않다. 코드가 컴파일되더라도 런타임에 `NullReferenceException`을 발생시킬 가능성이 높다. **컴파일 오류를 런타임 오류로 바꾸는 것**은 좋지 않은 방식이므로 조치를 취해야 한다.
:::

또한 `DateTime.Parse` 호출이 성공한다는 보장이 없다. 이 두 문제 — null 검사 부재와 파싱 실패 가능성 — 를 해결해야 한다.

---

## 2. 검증

`dto.At`가 없는 JSON을 클라이언트가 보내면 어떻게 될까? `NullReferenceException` 대신 `DateTime.Parse`가 `ArgumentNullException`을 발생시킨다. ASP.NET은 처리되지 않은 예외를 `500 Internal Server Error`로 변환한다. 원하는 결과가 아니다. 유효하지 않은 입력은 `400 Bad Request`가 반환되어야 한다.

> `NullReferenceException`보다 `ArgumentNullException`이 더 좋은 이유는 **예외 메시지**다. `NullReferenceException`은 "어떤 객체가 null"이라는 정보만 주지만, `ArgumentNullException`은 **어떤 인자가 null인지** 알려준다. 로그·오류 보고서에서 훨씬 유용하다.

### 2.1 날짜가 잘못 입력된 경우

문제를 재현하는 테스트부터 추가한다.

```csharp
[Theory]
[InlineData(null, "j@example.net", "Jay Xerxes", 1)]
public async Task PostInvalidReservation(
    string at, string email, string name, int quantity)
{
    var response =
        await PostReservation(new { at, email, name, quantity });

    Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);
}
```

왜 `[Theory]`에 하나의 케이스만 넣었는지 의문일 것이다. 시간이 지남에 따라 더 많은 케이스를 추가할 것을 이미 알고 있어서 조금 더 편하게 `[Theory]`에 두었다.

null 가드를 추가한다.

```csharp
public async Task<ActionResult> Post(ReservationDto dto)
{
    if (dto is null)
        throw new ArgumentNullException(nameof(dto));
    if (dto.At is null)
        return new BadRequestResult();

    var r = new Reservation(
        DateTime.Parse(dto.At, CultureInfo.InvariantCulture),
        dto.Email!, dto.Name!, dto.Quantity);
    await Repository.Create(r).ConfigureAwait(false);
    return new NoContentResult();
}
```

컴파일러가 널 검사를 감지하므로 `dto.At` 뒤의 `!`도 제거된다. 두 개의 테스트 케이스를 더 추가해서 이메일 누락과 잘못된 날짜 형식도 검증한다.

```csharp
[InlineData("not a date", "w@example.edu", "Wk Hd", 8)]
[InlineData("2023-11-30 20:01", null, "Thora", 19)]
```

`DateTime.Parse`를 `DateTime.TryParse`로 바꾸고 이메일 null 체크도 추가한다.

```csharp
public async Task<ActionResult> Post(ReservationDto dto)
{
    if (dto is null)
        throw new ArgumentNullException(nameof(dto));
    if (dto.At is null)
        return new BadRequestResult();
    if (!DateTime.TryParse(dto.At, out var d))
        return new BadRequestResult();
    if (dto.Email is null)
        return new BadRequestResult();

    var r = new Reservation(d, dto.Email, dto.Name!, dto.Quantity);
    await Repository.Create(r).ConfigureAwait(false);
    return new NoContentResult();
}
```

### 2.2 빨강-초록-리팩터

지금까지 예제에서는 **빨강-초록(Red-Green)** 만 반복했다. 이제 세 번째 단계 리팩터를 추가할 때다.

- **빨강(Red)**: 실패하는 테스트를 작성한다
- **초록(Green)**: 최대한 조금만 바꿔서 모든 테스트를 통과시킨다
- **리팩터(Refactor)**: 동작을 바꾸지 않고 코드를 개선한다

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 빨강-초록-리팩터 과정은 컴퓨터 공학에서 가장 과학적인 방법론 중 하나다. 과학적 방법은 (1) 예측 가능한 결과를 가진 가설을 세우고, (2) 실험을 하고 결과를 측정하고, (3) 실제 결과와 예측을 비교한다. 빨강 단계는 "이 테스트는 실패할 것"이라는 **가설**을, 초록 단계는 "이제는 통과할 것"이라는 **가설**을 실험으로 검증한다.
:::

일관성 있게 빨강-초록-리팩터를 진행하다 보면, 이 과정에서 **빨강 단계에서 테스트가 예상외로 통과하는 경우**를 자주 만난다. 뇌가 얼마나 성급하게 결론을 내리는지를 떠올려보라 — 의도치 않게 거의 같은 어설션을 중복 작성했을 수 있고, 그러면 **위양성(*False Positive - 결함이 없는데 있다고 판정하거나, 잘못된 것을 옳다고 판정하는 결과*)** 이 나타나지만 실험을 하지 않으면 발견하지 못한다.

리팩터 단계에서 확인해보자. `dto.At`의 null 체크가 중복되어 있다. `DateTime.TryParse`는 이미 null을 체크하고 false를 반환한다.

```csharp
public async Task<ActionResult> Post(ReservationDto dto)
{
    if (dto is null)
        throw new ArgumentNullException(nameof(dto));
    if (!DateTime.TryParse(dto.At, out var d))
        return new BadRequestResult();
    if (dto.Email is null)
        return new BadRequestResult();

    var r = new Reservation(d, dto.Email, dto.Name!, dto.Quantity);
    await Repository.Create(r).ConfigureAwait(false);
    return new NoContentResult();
}
```

여전히 모든 테스트가 통과한다. 이 리팩터링을 생각해낼 수 있었던 건 `DateTime.TryParse`의 동작을 알고 있었기 때문이다. 소프트웨어 공학의 예술인 **"끊임없이 흘러내리는 모래 같은 개인 경험"** 의 또 다른 예다.

### 2.3 자연수

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 캡슐화는 null 검사를 넘어서, **객체와 호출자 간의 유효한 상호작용을 나타내는 계약**이다. 유효성을 지정하는 방법 중 하나는 유효하지 않다고 간주되는 것을 명시하는 것. 그 외의 것들은 암시적으로 모두 유효하다.

null 참조를 금지하면 null이 아닌 모든 객체를 암시적으로 허용하는 것이다. 제약 조건을 더 추가하지 않는 한.
:::

`ReservationDto.Quantity`는 `?`가 없으므로 null이 될 수 없다. 하지만 모든 정수가 예약에 적절한 숫자일까? 2? 0? -3?

- **2**: 합리적. 두 명이 예약
- **-3**: 아니다. 인원이 음수일 수 없음
- **0**: 아무도 오지 않는데 예약할 이유가 없음

예약할 때 인원 수는 **자연수(*Natural Number - 양의 정수. 0을 포함하는지에 대해서는 학문마다 합의가 없음*)** 로 보는 것이 가장 합리적이다. 저자의 경험에 따르면 도메인 모델을 발전시킬 때 이런 가정을 하는 경우가 자주 있다. 모델은 현실 세계를 나타내려는 시도이며, 현실 세계는 대부분 자연수를 사용하기 때문이다.

새 테스트 케이스를 추가한다.

```csharp
[InlineData("2022-01-02 12:10", "3@example.org", "3 Beard", 0)]
[InlineData("2045-12-31 11:45", "git@example.com", "Gil Tan", -1)]
```

새 가드가 필요하다.

```csharp
if (dto.Quantity < 1)
    return new BadRequestResult();
```

부호 없는 정수(unsigned int)를 쓰면 되지 않을까 싶지만, 부호 없는 정수는 0을 허용하므로 여전히 가드가 필요하다.

### 2.4 포스텔의 법칙

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: **계약 기반 설계(*Design by Contract - 버트런드 메이어(Bertrand Meyer)가 Eiffel 언어에서 명시적으로 만든 접근. 사전조건과 사후조건을 통해 객체 간 상호작용을 규정*)** 는 (1) 구현을 리팩터링할 수 있게 하고, (2) 객체를 **추상화**해서 생각할 수 있게 한다.
:::

객체의 본질은 계약에서 온다. 계약이 구현보다 간단하기 때문에 우리 두뇌가 더 잘 받아들일 수 있다. 로버트 마틴의 정의처럼 **추상화란 무관한 것을 제거하고 본질적인 것을 강조하는 것**이다.

포스텔의 법칙(Postel's Law)은 다음과 같다.

> 보내는 부분은 보수적으로, 받는 부분은 더 자유롭게 만드세요.

존 포스텔(Jon Postel)은 원래 이 지침을 TCP 사양의 일부로 넣었지만, API 설계에도 유용하다. **제공자가 더 강력한 보증을 제공하고, 상대방의 보증은 덜 요구할수록 더 매력적인 계약**이 된다.

API 설계 관점에서 포스텔의 법칙은 다음과 같이 해석할 수 있다.

- **의미 있게 처리할 수 있는 만큼은 입력을 자유롭게 받아들인다**
- **그 이상은 허용하지 않는다**
- **유효하지 않은 입력은 빠르게 실패하고 거부**

이메일 검증을 예로 보자. 이메일 주소는 검증하기 어렵기로 악명이 높다. SMTP 사양을 완벽히 구현해도 대응이 안 된다. 가짜 이메일을 만드는 것도 쉽다. 유일한 실제 검증 방법은 이메일 주소로 확인 메시지를 보내는 것이지만, 이건 오래 걸리는 비동기 프로세스이므로 예약 차단 메서드에서 실행할 수 없다. 결론: **이메일이 null이 아닌지만 확인**하는 것이 실용적이다.

이름은 어떨까? 이름은 편의를 위한 것이다. 예약 시 이름을 말하지 않으면 이메일로 확인할 수 있다. 따라서 **이름이 null이면 거부 대신 빈 문자열로 변환**할 수 있다.

새 테스트 케이스.

```csharp
[InlineData("2023-08-23 16:55", "kite@example.edu", null, 2)]
```

어설션에서는 이렇게 처리한다.

```csharp
var expected = new Reservation(
    DateTime.Parse(dto.At, CultureInfo.InvariantCulture),
    dto.Email,
    dto.Name ?? "",  // ← null이면 빈 문자열
    dto.Quantity);
```

프로덕션 코드에도 **널 병합 연산자(*Null-Coalescing Operator - C#의 ??. 좌변이 null이면 우변 반환*)** 를 쓴다.

```csharp
var r = new Reservation(
    d, dto.Email, dto.Name ?? "", dto.Quantity);
```

`??`는 `!`와 달리 컴파일러 널 검사를 우회하지 않기 때문에 좋은 절충안이다.

---

## 3. 변하지 않는 값 보호하기

예제 5-11의 `Post` 메서드에 문제가 있을까? 복잡도 관점에서는 나쁘지 않다. 순환 복잡도는 6이다. 저자는 순환 복잡도가 **7을 넘으면** 줄이는 방법을 찾아야 한다고 본다.

하지만 전체 시스템을 보면 더 많은 일이 진행된다. 유지보수 담당 프로그래머가 `SqlReservationsRepository.Create`를 처음 본다면 이런 의문이 생긴다.

> `At`은 적절한 날짜인가? `Email`은 null이 아닌가? `Quantity`는 자연수인가?

`Reservation` 클래스 자체를 보면 `Email`과 `At`은 non-nullable 형식으로 보장할 수 있다. 하지만 **`Quantity`가 음수 또는 0이 아니라고 어떻게 확신할 수 있을까?**

현재는 각 형식을 확인하는 방법밖에 없다. 그런데 `Create`를 여러 곳에서 호출한다면 머릿속으로 추적할 것이 너무 많아진다. **객체가 이미 검증되었음을 보장할 수 있는 방법**이 있다면 더 간편할 것이다.

### 3.1 항상 유효한 상태

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 캡슐화의 본질은 **객체가 유효하지 않은 상태로 갈 수 없다는 것을 보장하는 것**이다. 이를 위해 "유효"와 "상태" 두 차원을 다뤄야 한다.
:::

객체의 상태는 속성들의 조합이며, 이 조합은 **항상 유효**해야 한다. 상태를 변경하는 동작이 있는 경우 각각의 동작이 유효하지 않은 상태로 바꾸지 않도록 해야 한다.

**불변(*Immutable - 생성 후 상태가 변경되지 않는*)** 객체의 매력적인 특징은 **유효성을 한 군데, 즉 생성자에서만 고려**하면 된다는 것이다. 초기화가 성공하고 나면 객체는 유효한 상태로 남는다.

현재의 `Reservation` 클래스는 이 조건을 완전히 만족하지 못한다. **고객의 수가 음수인 상태로 `Reservation`을 생성할 수 없어야 한다.** 매개변수 테스트로 이를 강제한다.

```csharp
[Theory]
[InlineData(0)]
[InlineData(-1)]
public void QuantityMustBePositive(int invalidQantity)
{
    Assert.Throws<ArgumentOutOfRangeException>(
        () => new Reservation(
            new DateTime(2024, 8, 19, 11, 30, 0),
            "mail@example.com",
            "Marie Ilsøe",
            invalidQantity));
}
```

0을 매개변수로 뽑은 이유는 **0이 자연수에 포함되는지에 대해 명확한 합의가 없기** 때문이다. 어쨌든 이 테스트에서는 0이 유효하지 않다는 것이 분명하다.

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 예외 메시지에 대한 어설션은 만들지 않았다. **예외 메시지 자체는 객체 동작의 일부가 아니다.** 나중에 메시지를 변경하려는 경우 테스트도 함께 바꿔야 하므로, 필요 이상으로 세부 구현을 테스트와 연결시키지 말자.
:::

생성자에 가드 절을 추가한다.

```csharp
public Reservation(
    DateTime at,
    string email,
    string name,
    int quantity)
{
    if (quantity < 1)
        throw new ArgumentOutOfRangeException(
            nameof(quantity),
            "The value must be a positive (non-zero) number.");

    At = at;
    Email = email;
    Name = name;
    Quantity = quantity;
}
```

`Reservation`은 불변이므로 **한 번 생성되면 유효하지 않은 상태로 바뀌지 않는다는 것이 보장**된다. 즉 코드에서 `Reservation`을 사용할 때 항상 방어적으로 코딩할 필요가 없다.

---

## 4. 자주 하는 실수

| 안티패턴 | 해결법 |
|---|---|
| `!` 연산자로 컴파일러 널 경고 회피 | 실제 널 체크·`??` 널 병합·가드 절 |
| 유효성 검증을 여러 곳에서 반복 | 생성자에서 한 번 검증, 불변 객체로 보장 |
| 예외 메시지까지 어설션 | 동작만 검증, 메시지는 구현 세부사항 |
| 이메일/이름을 과도하게 검증 | 실용적 수준의 검증(포스텔의 법칙) |
| getter/setter로 필드 감싸는 것을 캡슐화라 착각 | 캡슐화는 **불변 상태 보장 계약** |
| 리팩터 단계를 생략 | 빨강-초록만 반복 말고 리팩터까지 마무리 |

---

## 5. 결론

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 캡슐화는 객체지향 프로그래밍에서 잘못 이해하기 쉬운 개념이다. 많은 프로그래머가 클래스 필드를 getter·setter 뒤에 숨겨야 한다고 생각한다. 하지만 이는 캡슐화와 거의 관련이 없다.

가장 중요한 개념은 **객체가 잘못된 상태가 되지 않음을 완벽하게 보장**해줘야 한다는 점이며, 이 부분은 호출하는 쪽의 책임이 아니다. 객체는 '유효'하다는 의미와 이를 어떻게 보장해야 하는지 가장 잘 알고 있다.
:::

객체와 호출 함수 간의 상호작용은 계약을 준수해야 한다. 계약이란 **사전 및 사후 조건**의 집합이다.

- **사전 조건**: 호출 코드의 책임
- **사후 조건**: 호출 코드가 의무를 이행했을 때 객체가 제공하는 보장

사전 및 사후 조건을 함께 사용하면 **불변(*Invariant - 객체의 수명 동안 항상 참이어야 하는 조건*)** 이 된다. 포스텔의 법칙을 사용해 조금 더 유용한 계약을 설계할 수 있다.

- **호출자에게 덜 요구할수록** 호출자는 객체와 더 쉽게 상호작용할 수 있다
- **더 나은 보장을 제공할수록** 호출자가 작성해야 하는 방어 코드가 줄어든다

---

## 요약

- 캡슐화는 필드를 숨기는 게 아니라 **객체가 유효하지 않은 상태로 갈 수 없다는 계약**이다
- **변환 우선순위 전제**: 코드를 하나의 상태에서 다른 상태로 바꿀 때, 단순한 변환부터. 유효하지 않은 시간을 최소화
- 매개변수 테스트(`[Theory] + [InlineData]`)로 여러 케이스를 하나의 테스트 메서드로 표현
- **널 처리**: `!` 연산자는 컴파일 오류를 런타임 오류로 미루기 때문에 좋지 않다. 실제 널 체크나 `??` 연산자 사용
- **빨강-초록-리팩터** 주기: 실패 → 최소 통과 → 개선. 리팩터 단계를 생략하지 말 것. 이 과정은 가장 과학적인 방법론
- **자연수 제약**: 인원 수는 1 이상. 부호 없는 정수만으로는 부족하므로 가드 절 필수
- **포스텔의 법칙**: 보수적으로 보내고, 자유롭게 받자. 이메일은 null만 체크, 이름은 null이면 빈 문자열
- **불변 객체 + 생성자 가드**: 한 번 만들면 유효 상태가 영원히 유지되어, 호출 코드가 방어적으로 코딩할 필요가 없다
- **예외 메시지는 동작의 일부가 아니다** — 테스트에서 어설션 대상으로 잡지 말 것
- **계약 기반 설계**: 사전조건 + 사후조건 = 불변. 호출자에게 덜 요구할수록, 보장을 많이 할수록 더 나은 계약
