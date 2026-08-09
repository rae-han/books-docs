# Chapter 8: API Design (API 설계)

## 핵심 질문

코드 블록이 너무 복잡해질 때 이를 분해(*decompose - 하나의 큰 코드 단위를 더 작은 여러 단위로 쪼개는 것*)해야 한다. 그런데 새로 만들어지는 작은 블록은 어떤 모양이어야 하는가? 잘못된 방법이 올바른 방법보다 훨씬 많은 상황에서, 어떻게 하면 좁은 길을 벗어나지 않고 좋은 API를 설계할 수 있는가? 사람이 이해할 수 있는 코드란 무엇이며, 그것을 만들어내는 휴리스틱은 무엇인가?

---

## 1. API란 무엇인가

**API(*Application Programming Interface - 응용 프로그래밍 인터페이스. 다른 코드가 특정 코드 패키지와 상호작용할 수 있게 제공되는 진입점 집합*)** 는 클라이언트 코드를 작성할 수 있도록 노출된 인터페이스를 의미한다. 프로그래밍 언어의 `interface` 키워드와 헷갈리기 쉽지만, 이 장에서는 그보다 넓은 뜻으로 사용한다.

이 책에서 말하는 인터페이스란 다른 코드와 상호작용하기 위해 사용할 수 있는 메서드·값·함수·객체의 집합이며, 적절한 캡슐화를 통해 관련 객체의 **불변성(*Invariant - 객체가 항상 만족해야 하는 조건*)** 을 보존하는 일련의 작업이다. 즉 인터페이스의 동작은 객체의 상태가 언제나 유효하도록 보장하는 것이라고 할 수 있다.

이 장에서는 코드를 분해할 때 새 블록을 어떻게 설계해야 하는지, 그 휴리스틱을 살펴본다.

---

## 2. 행동 유도성 (Affordance)

### 2.1 도널드 노먼의 어포던스 개념

API를 사용하는 것은 손잡이가 달린 문과 상호작용하는 것과 비슷하다. 손잡이의 모양은 밀어야 할지 당겨야 할지, 돌려야 할지를 알려준다. 도널드 A. 노먼(Donald A. Norman)은 이 관계를 설명하기 위해 **행동 유도성(*Affordance - 물체가 특정 행위를 유도하도록 만드는 속성*)** 이라는 개념을 사용했다.

> 행동 유도성(어포던스, affordance)은 물체나 사람(또는 동물·인간·기계·로봇 등 상호관계하는 모든 중개자) 사이의 관계를 설명하는 것이다. 객체의 속성과 그 객체의 사용 가능성을 결정하는 중개자 관계라고도 이야기할 수 있다. 예컨대 의자는 받침을 제공하기 때문에 앉을 수 있으며, 대부분 한 사람이 옮길 수 있지만, 어떤 의자는 힘이 센 사람이 필요하거나 여러 명이 힘을 합쳐야 들어올릴 수 있는 것도 있다.
> — 도널드 노먼

### 2.2 API에서의 어포던스

API도 마찬가지다. `IReservationsRepository` 같은 API는 특정 날짜의 예약을 확인하고 새 예약을 추가하는 동작을 제공하는데, 반드시 필요한 인자를 넘겨야만 호출할 수 있다. 클라이언트 코드와 API 사이의 관계는 호출자와 (제대로 캡슐화된) 객체 사이의 관계와 같다. 객체는 필수 전제조건을 충족시킨 클라이언트에게만 기능을 제공한다. 즉 `Reservation` 정보 없이는 `Create` 메서드를 호출할 수 없다.

컴파일된 정적 형식(*statically typed - 컴파일 시점에 타입이 결정되고 검증되는 것*) 언어에서는 **형식(type)** 을 통해 행동을 유도한다. IDE에서 객체 뒤에 점(`.`)을 찍으면 사용할 수 있는 메서드 목록이 뜨는데, 이런 개발 방식을 "점(dot) 기반 개발"이라 부르기도 한다.

```csharp
var accepted = maitreD.
// IDE 자동완성:
//   WithTables
//   Schedule
//   WillAccept
//   OpensAt
//   Segment
//   Equals
//   GetHashCode
//   GetType
```

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 형식은 객체가 무엇을 할 수 있는지 알려주는 첫 번째 어포던스다. 정적 타입 언어에서 API 설계란 곧 "이 객체가 어떤 행동을 유도하도록 할 것인가"를 정하는 일이다.
:::

---

## 3. 포카요케 (Poka-yoke)

### 3.1 실수 방지 설계

흔한 실수 중 하나는 API를 **스위스 군용 칼**처럼 설계하는 것이다. 좋은 API는 기능이 많아야 한다고 여기는 개발자가 많은데, 한 API에 온갖 기능을 다 밀어넣기보다는 특정 목적에 특화된 도구를 여러 개 두는 것이 낫다. 이런 설계의 극단적인 안티패턴이 **갓 클래스(*God Class - 너무 많은 책임을 떠안은 거대 클래스*)** 다.

잘 설계된 인터페이스는 무엇이 가능한지뿐 아니라 **무엇이 불가능한지도** 의도적으로 알려준다. API에서 겉으로 보이는 멤버를 통해 제공 기능과 함께 수행해서는 안 되는 기능도 드러내야 한다.

> API는 잘못 사용하기 어렵게 설계해야 한다.

린 소프트웨어 개발(*Lean Software Development - 도요타 생산방식에서 유래한 소프트웨어 개발 철학*)의 중요한 개념 중 하나는 만드는 과정에서부터 품질을 유지하는 것이다. 마지막 단계에서 결점을 잡아내는 것이 아니라, 결과물과 과정 모두를 실수로부터 보호한다. 린 제조에서는 이 개념을 실수 방지를 뜻하는 일본어 **포카요케(*Poka-yoke - ポカヨケ. 실수를 애초에 방지하도록 만드는 설계 원칙*)** 라 부른다.

### 3.2 능동적 vs 수동적 실수 방지

포카요케는 두 가지로 나뉜다.

| 유형 | 설명 | 소프트웨어에서의 예 |
|---|---|---|
| 능동적 실수 방지 | 만든 직후 검사한다 | 테스트 주도 개발, 자동화된 테스트 |
| 수동적 실수 방지 | 애초에 잘못 쓸 수 없게 만든다 | 타입 시스템, 컴파일러 오류 |

일상에서도 예를 쉽게 찾을 수 있다. USB-C나 HDMI는 올바른 방향으로만 꽂히고, 도로의 높이 제한 장벽은 트럭이 통과할 수 있는지 물리적으로 알려준다. 이런 시스템은 별도로 작동시킬 필요가 없다.

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 허용되지 않는 상태가 코드로 표현조차 되지 않도록 API를 설계하는 것이 가장 좋다. 불가능한 기능을 사용하려 하면 **컴파일조차 되지 않게** 만들어야 한다. 컴파일러 오류는 런타임 예외보다 훨씬 빠른 피드백을 준다.
:::

---

## 4. 읽는 사람을 위한 코드

학창 시절 작문 시간에는 문맥·발신인·수신인을 모두 고려해 글을 써야 한다고 배웠을 것이다. 프로그래머가 되었다고 해서 그 원칙에서 벗어나지는 못한다.

> 코드는 작성하는 일보다 읽는 일이 훨씬 더 많다. 미래의 독자를 위해 코드를 작성하라. 그 독자가 여러분 자신이 될 수도 있다.

### 4.1 주석보다는 잘 지은 이름

주석은 코드가 변하면 낡은 내용이 되어버린다. 한때는 맞았더라도 시간이 지나면서 오히려 오해를 부른다. 결국 믿을 수 있는 유일한 산출물은 코드뿐이다.

```csharp
// 나쁜 예: 의도를 주석으로 설명
// 영업시간 외에 들어온 예약은 거부하기
if (candidate.At.TimeOfDay < OpensAt ||
    LastSeating < candidate.At.TimeOfDay)
    return false;
```

같은 로직을 이름 있는 메서드로 뽑아내면 주석 없이도 의도가 드러난다.

```csharp
// 좋은 예: 메서드 이름으로 의도 표현
if (IsOutsideOfOpeningHours(candidate))
    return false;
```

주석을 쓰는 것 자체가 나쁘다는 뜻이 아니라, **주석보다는 메서드 이름을 잘 짓는 편이 더 낫다**는 이야기다.

### 4.2 이름조차 낡을 수 있다 — 형식으로 말하기

메서드 이름도 낡을 수 있다. 구현을 바꾸면서 이름 바꾸는 것을 잊어버리는 경우가 자주 있다. 다행히 정적 형식 언어에서는 형식(type)이 정확히 유지된다. API 계약(*API Contract - API와 클라이언트 사이의 약속*)의 의미를 형식으로 표현할 수 있게 설계하자.

```csharp
public interface IReservationsRepository
{
    Task Create(Reservation reservation);
    Task<IReadOnlyCollection<Reservation>> ReadReservations(DateTime dateTime);
    Task<Reservation?> ReadReservation(Guid id);
}
```

세 번째 메서드의 반환 형식이 `Task<Reservation?>`인 것을 보라. C#의 **널 참조 가능 형식(*Nullable reference types - 참조가 null일 수 있음을 타입 수준에서 표현*)** 을 쓰면 "이 값은 null일 수 있다"는 정보를 이름이 아닌 **형식**으로 전달할 수 있다. `GetReservationOrNull` 같은 이름에 이 정보를 담아도 되지만, 나중에 API가 바뀌어 null을 반환하지 않게 되면 이름 바꾸는 것을 잊어버릴 수 있다. 형식으로 표현한 정보는 그런 실수에 강하다.

### 4.3 이름을 X로 바꿔보기 연습

메서드 이름을 `Xxx`로 지우고, 그래도 어떤 동작을 하는지 짐작할 수 있는지 확인해보자.

```csharp
public interface IReservationsRepository
{
    Task Xxx(Reservation reservation);
    Task<IReadOnlyCollection<Reservation>> Xxx(DateTime dateTime);
    Task<Reservation?> Xxx(Guid id);
}
```

- `Task Xxx(Reservation reservation)` — 반환값이 없다. 부수효과(*side effect - 함수 호출로 인해 외부 상태가 바뀌는 것*)가 있을 것이다. `IReservationsRepository`라는 클래스 이름을 고려하면 예약을 저장하는 명령일 가능성이 크다. 다만 새 행을 만드는지 기존 행을 갱신하는지는 이름 없이는 알기 어렵다.
- `Task<IReadOnlyCollection<Reservation>> Xxx(DateTime dateTime)` — 날짜를 입력받아 예약 컬렉션을 반환한다. 날짜 기반 조회 쿼리라는 것은 쉽게 추측된다.
- `Task<Reservation?> Xxx(Guid id)` — ID로 예약 하나를 조회하는 쿼리라는 것이 명백하다.

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 이름에는 형식을 통해 추정할 수 있는 부분까지 반복해서 넣을 필요가 없다. 형식으로 추정하기 어려운 부분만 이름에 넣어 추가 정보를 제공하자.
:::

이 기법은 객체 멤버가 서로 다른 형식을 가질 때만 잘 동작한다. 모든 메서드가 `string`이나 `int`만 반환한다면 형식은 도움이 되지 않는다. 이것이 **문자열 형식 API를 피해야 하는 또 다른 이유**이며, 스위스 군용 칼보다 특화된 API가 나은 이유이기도 하다.

---

## 5. 명령 쿼리 분리 (Command Query Separation)

### 5.1 부수효과란

`void Xxx()` 같은 시그니처는 거의 아무 정보도 주지 않는다. 반환값이 없으므로 존재 이유가 있으려면 부수효과가 있어야 한다는 것 정도만 알 수 있다.

부수효과란 프로시저가 어떤 것의 상태를 바꾸는 것을 의미한다. 지역적인 효과(객체 상태 변경)일 수도 있고, 전역적인 효과(DB 행 삭제, 파일 편집, GUI 다시 그리기, 이메일 보내기)일 수도 있다.

단, **캡슐화 안쪽의 지역 상태 변경**은 관찰 가능한 부수효과가 아니다. 예제 8-4의 헬퍼 메서드를 보자.

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

`availableTables`라는 지역 변수를 수정하지만, 이는 메서드 안에서 생성된 지역 상태다. 호출자 입장에서는 예약 컬렉션을 넣으면 테이블 컬렉션이 돌아올 뿐, 관찰 가능한 부수효과는 없다.

### 5.2 CQS 원칙

이제 규칙을 세울 수 있다.

- 부수효과가 있는 메서드는 데이터를 반환하지 않는다 → 반환 타입은 `void` → **명령(*Command - 상태를 바꾸는 메서드*)**
- 데이터를 반환하는 메서드는 부수효과가 없어야 한다 → **쿼리(*Query - 상태를 조회하는 메서드*)**

이 개념을 버트런드 마이어(Bertrand Meyer)가 정립한 **명령 쿼리 분리 원칙(*Command Query Separation, CQS - 메서드는 명령이거나 쿼리 중 하나여야 하며 둘을 겸해서는 안 된다는 원칙*)** 이라 한다.

| 구분 | 명령 (Command) | 쿼리 (Query) |
|---|---|---|
| 반환 타입 | `void` (또는 `Task`) | 값을 반환 |
| 부수효과 | 있음 | 없음 |
| 예 | `Create(reservation)` | `ReadReservation(id)` |
| 추론 난이도 | 이름에 크게 의존 | 형식에서 많이 추정 가능 |

명령보다는 쿼리를 추론하는 것이 훨씬 쉽다. 데이터를 반환하면서 부수효과도 있는 메서드는 기술적으로 문제없이 동작하지만 CQS에 어긋난다. 컴파일러가 이 규칙을 강제하지 못하므로 스스로 지켜야 한다.

---

## 6. 정보 전달의 계층 (Communication Hierarchy)

주석이 낡을 수 있듯 메서드 이름도 낡을 수 있다. 그렇다면 일반화된 규칙은 무엇인가?

> 메서드 이름을 통해 알려줄 수 있는 것은 주석에 쓰지 않는다.
> 형식을 통해 알려줄 수 있는 것은 메서드 이름에 적지 않는다.

중요한 순서대로 정리하면 다음과 같다.

| 순위 | 수단 | 특성 |
|---|---|---|
| 1 | **API 고유의 데이터 형식** | 컴파일 시점 검증 — 잘못되면 컴파일이 안 된다 |
| 2 | **유용한 메서드 이름** | 매일 들여다보는 코드의 일부 |
| 3 | **좋은 주석** | 왜(why)를 설명 — 낡을 위험 있음 |
| 4 | **자동화된 테스트** | API 사용 예제 역할 |
| 5 | **깃 커밋 메시지** | 특정 변경의 배경을 설명 |
| 6 | **문서 (README 등)** | 높은 수준의 질문 답변 |

데이터 형식은 컴파일 과정에서 확인되기에 다른 어떤 수단도 이 품질을 제공하지 못한다. 반면 문서·주석·이름은 쉽게 정체되어 낡아버린다. 코드만이 늘 최신 상태를 유지하는 유일한 산출물이다.

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 정보를 전달할 때는 가장 위쪽 계층을 먼저 소진하고, 그 계층으로 표현할 수 없을 때만 아래 계층으로 내려가라. 형식으로 말할 수 있는 것을 이름에 반복하지 말고, 이름으로 말할 수 있는 것을 주석에 반복하지 말자.
:::

---

## 7. API 설계 예제 — 지배인(MaitreD)

### 7.1 요구사항의 확장

지금까지의 `ReservationsController`는 매우 단순했다. 좌석은 10개로 하드코딩되어 있었고, 예약 수락 규칙은 "테이블에 자리만 있으면 받는다"였다. 즉 주방이 보이는 바 테이블 하나짜리 레스토랑에나 맞는 로직이다.

이제 요구사항을 늘려보자.

- 테이블이 여러 개이고, 한 좌석은 하루에 여러 번 예약 가능(식사 시간만큼 점유)
- 영업시간 반영(개점 전·마감 후 예약 거부)
- 과거 시간 예약 거부
- 위 모든 설정은 변경 가능해야 함

동시에 제약 조건은 그대로다. 순환 복잡도 7 이내, 메서드가 너무 크거나 변수가 많지 않아야 한다.

### 7.2 유비쿼터스 언어로 이름 짓기

새 클래스에 뭐라고 이름을 붙일까? 도메인 전문가들이 사용하는 **유비쿼터스 언어(*Ubiquitous Language - 도메인 전문가와 개발자가 공유하는 공통 용어. 도메인 주도 설계의 핵심 개념*)** 를 채택하면 자연스러운 이름을 찾을 수 있다. 정식 레스토랑에서 주방을 관리하는 사람이 셰프(chef de cuisine)라면, 접객 구역을 총괄하는 수석 웨이터는 **지배인(*Maître d' - maître d'hôtel의 줄임말. 레스토랑 홀 총괄자*)** 이다. 예약을 받고 테이블을 배정하는 것 역시 지배인의 책임이다. 그래서 `MaitreD` 클래스를 도입한다.

### 7.3 MaitreD 생성자 — 형식으로 요구사항 표현

```csharp
public MaitreD(
    TimeOfDay opensAt,
    TimeOfDay lastSeating,
    TimeSpan seatingDuration,
    IEnumerable<Table> tables)
```

`new MaitreD(` 까지만 입력해도 IDE가 필요한 인자를 알려준다. 모든 인자가 필수이며 null이 될 수 없다. `TimeOfDay`라는 커스텀 형식을 만들었기 때문에 아무 시간 값이나 넣을 수 없고, `Table`이라는 형식도 마찬가지다. 문자열이나 정수 대신 도메인 형식을 쓴 덕분에 잘못된 값을 애초에 컴파일 시점에서 차단한다 — 포카요케다.

### 7.4 WillAccept 메서드 — 쿼리로 설계

```csharp
public bool WillAccept(
    DateTime now,
    IEnumerable<Reservation> existingReservations,
    Reservation candidate)
```

이 메서드는 값을 반환하므로 쿼리다. CQS에 따르면 부수효과가 없어야 하고, 실제로도 없다. 부담 없이 호출할 수 있으며, 하는 일은 CPU 사이클을 소모해 bool 값을 반환하는 것뿐이다. `Post` 메서드에서는 두 줄로 처리되던 비즈니스 로직을 한 줄로 대체할 수 있다.

```csharp
if (!MaitreD.WillAccept(DateTime.Now, reservations, r))
    return new StatusCodeResult(StatusCodes.Status500InternalServerError);
```

### 7.5 의존성으로 MaitreD 주입하기

`MaitreD`는 어디서 오는가? `ReservationsController` 생성자로 주입된다.

```csharp
public ReservationsController(
    IReservationsRepository repository,
    MaitreD maitreD)
{
    Repository = repository;
    MaitreD = maitreD;
}
public IReservationsRepository Repository { get; }
public MaitreD MaitreD { get; }
```

`MaitreD`는 다형성 의존성이 아니라 구체 클래스 의존성이다. 왜 이런 식으로 했을까? 대안으로 `MaitreD` 생성자의 인자들을 모두 컨트롤러 생성자로 밀어 넣을 수도 있다.

```csharp
// 대안 — 좋아 보이지 않는다
public ReservationsController(
    IReservationsRepository repository,
    TimeOfDay opensAt,
    TimeOfDay lastSeating,
    TimeSpan seatingDuration,
    IEnumerable<Table> tables)
{
    Repository = repository;
    MaitreD = new MaitreD(opensAt, lastSeating, seatingDuration, tables);
}
```

이 대안은 `MaitreD`에 대한 공개 의존성이 없어 보이지만, 여전히 존재한다. `MaitreD` 생성자를 바꾸면 컨트롤러 생성자도 바꿔야 한다. 원래 형태(`MaitreD`를 그대로 주입)를 유지하면, `MaitreD` 생성자를 바꿀 때 주입 지점만 손보면 된다. 유지보수 부담이 줄어든다.

`MaitreD`는 불변 클래스이므로 한 번 만들어지면 바뀌지 않는다. 상태 없는(*stateless*) 서비스는 스레드에 안전하므로 싱글턴 수명으로 등록해도 된다.

```csharp
// Startup.ConfigureServices
var settings = new Settings.RestaurantSettings();
Configuration.Bind("Restaurant", settings);
services.AddSingleton(settings.ToMaitreD());
```

### 7.6 캡슐화된 객체와의 상호작용

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 잘 설계된 API는 세부 구현을 몰라도 상호작용할 수 있어야 한다. 예제 8-6·8-7에서 우리는 공개된 API 표면(생성자와 `WillAccept` 시그니처)만 보고도 `MaitreD` 객체를 어떻게 만들고 사용할지 추론할 수 있었다.
:::

`opensAt`, `lastSeating`, `seatingDuration`, `tables` — 각 인자의 형식과 이름만으로 무엇을 넣어야 할지 알 수 있다. 이것이 캡슐화의 핵심이다. API를 통해 이야기해야 한다는 것이 아니라, **API에 대해 추론할 수 있는 근거를 제공해야 한다는 것**이다.

---

## 8. WillAccept 구현 살펴보기

가끔은 세부 구현을 봐야 할 때도 있다. 그럴 때는 프랙탈 아키텍처에서 한 단계 더 들어가면 된다. `WillAccept`의 구현은 다음과 같다. 순환 복잡도 5, 20줄, 80자 이내, 객체 7개 — 사람이 이해할 만한 규모다.

```csharp
public bool WillAccept(
    DateTime now,
    IEnumerable<Reservation> existingReservations,
    Reservation candidate)
{
    if (existingReservations is null)
        throw new ArgumentNullException(nameof(existingReservations));
    if (candidate is null)
        throw new ArgumentNullException(nameof(candidate));

    if (candidate.At < now)
        return false;
    if (IsOutsideOfOpeningHours(candidate))
        return false;

    var seating = new Seating(SeatingDuration, candidate);
    var relevantReservations =
        existingReservations.Where(seating.Overlaps);
    var availableTables = Allocate(relevantReservations);
    return availableTables.Any(t => t.Fits(candidate.Quantity));
}
```

메서드는 여러 원칙을 지키고 있다.

- **가드 절(*Guard clause - 메서드 초입에서 잘못된 입력을 조기에 걸러내는 조건문*)** 로 null을 즉시 거부 — 페일 패스트(*fail-fast - 잘못된 상태를 최대한 빨리 드러내는 원칙*)
- 과거 예약, 영업시간 외 예약을 조기 return
- 나머지 로직은 `Seating`, `Allocate`, `Fits` 등 다른 객체로 위임

만약 테이블 할당 방식을 바꾸려면 `Allocate`를 봐야 하고, 좌석 중복 감지 버그가 있다면 `Seating.Overlaps`를 봐야 한다. `Fits`를 보고 싶으면 다음처럼 딱 두 줄이다.

```csharp
internal bool Fits(int quantity)
{
    return quantity <= Seats;
}
```

`Seats`와 `quantity`, 이 두 덩어리만 따라가면 된다. `Fits`를 호출하는 코드는 신경 쓸 필요가 없다 — **눈에 보이는 것이 전부**라는 원칙에 따라, 알아야 할 모든 것이 이 안에 있다. 이 코드도 여러분의 머리에 잘 들어온다.

---

## 9. 결론

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 코드를 읽는 사람을 위한 코드를 작성하라. 컴퓨터가 인식 가능한 코드는 바보도 작성할 수 있지만, 인간이 이해할 수 있는 코드는 실력 있는 프로그래머만 작성할 수 있다. — 마틴 파울러(Martin Fowler)
:::

동작하는 소프트웨어를 만드는 것은 당연하다. 그것만 따지면 기준이 너무 낮다. 그건 파울러가 말한 "컴퓨터가 이해할 수 있는 코드"에 불과하다. 코드가 지속 가능하려면 **사람이 이해할 수 있게** 작성해야 한다.

캡슐화는 이 노력의 중요한 부분이며, 구현의 세부 내용을 몰라도 되도록 API를 설계하는 작업도 그중 하나다. 로버트 마틴의 추상화 정의를 기억하자.

> 추상화는 무관한 것을 제거하고, 본질적인 것을 강조하는 것이다.
> — 로버트 C. 마틴(Robert C. Martin)

구현의 세부는 그것을 바꿔야 할 때까지 몰라도 되어야 한다. 그러니 API의 동작을 외부에서 추론할 수 있도록 설계해야 한다.

---

## 요약

- API는 클라이언트가 상호작용하는 표면이며, **캡슐화된 불변성을 보존하는 작업의 집합**이다
- **행동 유도성(어포던스)**: API는 형식·이름·자동완성 등을 통해 "무엇을 할 수 있는지"를 스스로 드러내야 한다
- **포카요케**: 잘못 사용하기 어렵게, 잘못된 상태가 컴파일조차 되지 않게 설계하라. 컴파일러 오류가 런타임 예외보다 훨씬 빠른 피드백을 준다
- **정보 전달 계층**: 형식 > 이름 > 주석 > 테스트 > 커밋 메시지 > 문서. 위 계층으로 표현할 수 있는 것을 아래 계층에 반복하지 말라
- **명령 쿼리 분리(CQS)**: 명령은 부수효과만 있고 반환하지 않는다. 쿼리는 반환만 하고 부수효과가 없다. 두 역할을 겸하는 메서드를 만들지 말라
- **커스텀 도메인 형식**을 만들어 문자열·정수 같은 원시 타입 대신 사용하면, 형식 자체가 유효성을 강제한다
- **유비쿼터스 언어**를 채택해 도메인 개념에 어울리는 이름(예: `MaitreD`, `Seating`, `Table`)을 붙여라
- `MaitreD` 예제는 생성자에서 불변식을 확립하고, `WillAccept`를 쿼리로 만들어 부담 없이 호출 가능하게 하며, 세부 구현은 다른 객체로 위임해 프랙탈 구조를 이룬다
- **읽는 사람을 위해 써라** — 컴퓨터가 이해하는 코드보다 사람이 이해하는 코드가 훨씬 어렵고, 훨씬 가치 있다
