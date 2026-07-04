# Chapter 10: Augmenting Code (코드를 보강해봅시다)

## 핵심 질문

전문적인 소프트웨어 개발의 대부분은 그린필드가 아니라 기존 코드베이스 위에서 이루어진다. 그렇다면 이미 동작하는 시스템에 새로운 기능을 추가하거나 기존 동작을 개선할 때, 어떻게 하면 지속적 통합의 흐름을 깨뜨리지 않으면서 안전하게 코드를 보강할 수 있을까? 4시간 안에 끝낼 수 없는 큰 변경을 어떻게 조각내서 매일 master 브랜치에 병합할 수 있을까?

---

## 1. 코드를 보강한다는 것

기존 코드베이스에 손을 대는 일은 세 가지 형태로 나눠서 생각할 수 있다.

- **완전히 새로운 기능** 추가
- **기존 동작 개선**
- **버그 수정**

동작을 유지한 채 구조만 바꾸는 **리팩터링(*Refactoring - 외부 동작을 유지하면서 내부 구조를 개선하는 작업*)** 은 이미 여러 자료에서 다루므로, 이 챕터에서는 새로운 동작을 추가하는 앞의 두 가지에 집중한다. 버그 수정은 12장에서 별도로 다룬다.

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 새 기능을 추가할 때 가장 큰 도전은 코드 자체가 아니라 **지속적 통합(*Continuous Integration - 하루 두 번 이상 master 브랜치에 코드를 병합하는 프랙티스, CI*)** 의 리듬을 유지하는 것이다. 4시간 이상 걸리는 기능을 어떻게 하루에 두 번 이상 병합할 것인가?
:::

---

## 2. 기능 플래그 (Feature Flag)

4시간 안에 끝낼 수 없는 기능은 어떻게 병합해야 할까? 대부분의 개발자는 완성되지 않은 기능을 master에 올리는 것을 꺼린다. 특히 **지속적 배포(*Continuous Deployment - master 브랜치의 변경사항이 자동으로 프로덕션에 배포되는 방식, CD*)** 를 하는 팀이라면 이는 불완전한 코드가 프로덕션으로 나간다는 뜻이기 때문이다.

해결책은 **기능 자체와 그것을 구현하는 코드를 분리**하는 것이다. 코드는 병합되어 있되, 사용자에게는 아직 보이지 않게 **기능 플래그(*Feature Flag - 코드는 배포되어 있지만 런타임 스위치로 기능 활성화 여부를 제어하는 기법*)** 뒤에 숨긴다.

### 2.1 캘린더 플래그 예제

레스토랑 예약 시스템에 캘린더 기능을 추가한다고 하자. 월별/일별 좌석 조회, 남은 자리 계산 등 복잡한 작업이라 4시간 안에 끝낼 수 없다. 캘린더 기능을 시작하기 전 `home` 리소스는 예약 링크 하나만 반환하고 있었다.

```csharp
public IActionResult Get()
{
    return Ok(new HomeDto { Links = new[]
    {
        CreateReservationsLink()
    } });
}
```

여기에 기능 플래그를 도입해서 다음과 같이 바꾼다.

```csharp
public IActionResult Get()
{
    var links = new List<LinkDto>();
    links.Add(CreateReservationsLink());
    if (enableCalendar)
    {
        links.Add(CreateYearLink());
        links.Add(CreateMonthLink());
        links.Add(CreateDayLink());
    }
    return Ok(new HomeDto { Links = links.ToArray() });
}
```

`enableCalendar`는 컨트롤러의 생성자를 통해 주입받는 필드다.

```csharp
private readonly bool enableCalendar;

public HomeController(CalendarFlag calendarFlag)
{
    if (calendarFlag is null)
        throw new ArgumentNullException(nameof(calendarFlag));
    enableCalendar = calendarFlag.Enabled;
}
```

`CalendarFlag`는 불리언 값을 감싼 래퍼 클래스인데, ASP.NET의 DI 컨테이너가 값 형식(*value type*)을 의존성으로 취급하지 않기 때문에 필요한 기술적 래퍼일 뿐이다.

구성 파일의 `EnableCalendar` 값이 없으면 `bool` 기본값 `false`가 반환된다. 즉 프로덕션에서는 기본적으로 캘린더 링크가 노출되지 않는다.

### 2.2 통합 테스트에서 플래그 켜기

테스트에서는 플래그를 재정의해 새 기능의 동작을 검증한다.

```csharp
services.RemoveAll<CalendarFlag>();
services.AddSingleton(new CalendarFlag(true));
```

로컬에서 탐색적으로 테스트해보고 싶다면 로컬 구성 파일의 `EnableCalendar` 값을 `true`로 만들면 된다.

### 2.3 기능이 완성되면 플래그를 지운다

기능이 프로덕션에 노출될 준비가 되면 `CalendarFlag` 클래스 자체를 삭제한다. 그러면 플래그를 참조하는 모든 코드가 컴파일되지 않으니, 컴파일러 오류를 따라가며 조건부 분기를 제거하면 된다.

> 코드를 삭제하면 유지보수할 코드의 양이 줄어들기 때문에 항상 흐뭇하다.

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 기능 플래그는 "미완성 코드를 감추는 스위치"가 아니라 **"코드 병합과 기능 릴리즈를 분리하는 도구"** 다. 병합은 매일, 릴리즈는 준비되면.
:::

---

## 3. 스트랭글러 패턴 (Strangler Pattern)

새 기능이 아니라 **기존 코드를 바꾸는** 경우는 이야기가 다르다. 저자가 예전에 겪은 실패담이 있다.

> 문제의 클래스를 변경하고 난 뒤 기본적으로 컴파일러의 출력 메시지를 따라가며 이 부분을 호출하는 위치들을 찾아내서 고칠 수 있을 거라고 생각했는데, 실제로는 컴파일 오류가 너무 많이 발생했고 일주일이 지나도록 코드는 여전히 컴파일되지 않았다.

이 실패에서 얻은 경험 법칙이다.

> 중요한 변경사항이 있다면 그 위치에서 바로 바꾸지 말고, 대안을 만들어서 바로 옆에 놓고 같이 적용하세요.

이것이 **스트랭글러 패턴(*Strangler Pattern - 새 구현을 기존 구현 옆에 두고 점진적으로 호출자를 옮긴 뒤 기존 구현을 제거하는 리팩터링 기법*)** 이다. 이름은 숙주 나무를 감아 올라가면서 서서히 대체하는 스트랭글러 무화과나무(strangler fig)에서 왔다. 원래 마틴 파울러가 대규모 레거시 시스템 교체 방법으로 소개했지만, 메서드/클래스 수준에서도 똑같이 유용하다.

### 3.1 메서드 수준의 스트랭글러

캘린더 기능을 구현하려면 기간(range)에 대한 예약을 읽어야 했다. 하지만 기존 인터페이스는 하루짜리만 지원했다.

```csharp
public interface IReservationsRepository
{
    Task Create(Reservation reservation);
    Task<IReadOnlyCollection<Reservation>> ReadReservations(
        DateTime dateTime);
    Task<Reservation?> ReadReservation(Guid id);
    Task Update(Reservation reservation);
    Task Delete(Guid id);
}
```

기존 메서드를 바로 바꾸는 대신, 새 메서드를 옆에 추가한다.

```csharp
public interface IReservationsRepository
{
    Task Create(Reservation reservation);
    Task<IReadOnlyCollection<Reservation>> ReadReservations(
        DateTime dateTime);
    Task<IReadOnlyCollection<Reservation>> ReadReservations(
        DateTime min, DateTime max);
    Task<Reservation?> ReadReservation(Guid id);
    Task Update(Reservation reservation);
    Task Delete(Guid id);
}
```

이제 호출자를 한 명씩 새 메서드로 옮기고, 매 변경마다 git에 커밋한다. 마지막 호출자를 옮긴 뒤 기존 오버로드를 삭제하면 리팩터링이 끝난다.

### 3.2 클래스 수준의 스트랭글러

과도하게 일반화된 `Occurrence<T>` 클래스가 있었다. 이 클래스를 쓰는 코드는 모두 `IEnumerable<Table>`만 값으로 담고 있었기 때문에, 일반화는 불필요한 복잡도만 만들고 있었다. 이런 시그니처가 튀어나온다.

```csharp
public IEnumerable<Occurrence<IEnumerable<Table>>> Schedule(
    IEnumerable<Reservation> reservations)
```

`TimeSlot`이라는 구체 클래스로 대체하면 훨씬 읽기 좋다.

```csharp
public IEnumerable<TimeSlot> Schedule(
    IEnumerable<Reservation> reservations)
```

절차는 다음과 같다.

1. `TimeSlot` 클래스를 추가하고 커밋한다. 아직 호출자는 없다.
2. `Occurrence<IEnumerable<Table>>`을 `TimeSlot`으로 바꾸는 확장 메서드를 임시로 만든다.
3. 반환 유형이 다른 두 개의 `Schedule` 메서드를 공존시키기 위해, 기존 메서드 이름을 `ScheduleOcc`로 리네임하고 새 `Schedule` 메서드를 추가한다 (C#은 반환형만 다른 오버로드를 허용하지 않는다).
4. 호출자를 하나씩 새 `Schedule`로 옮기고, 각각 커밋한다.
5. 모든 호출자를 옮기면 `ScheduleOcc`와 `Occurrence<T>`, 그리고 임시 변환 메서드를 삭제한다.

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 스트랭글러 패턴의 진짜 이점은 **모든 커밋이 통합·배포 가능한 상태**를 유지한다는 것이다. 5분마다 커밋해도 시스템은 항상 컴파일되고 테스트를 통과한다.
:::

---

## 4. 버전 관리하기

메서드나 클래스가 외부로 공개된 API의 일부라면 삭제 자체가 문제다. 그래서 **유의적 버전(*Semantic Versioning - MAJOR.MINOR.PATCH 형식으로, 호환성 파괴는 MAJOR, 기능 추가는 MINOR, 버그 수정은 PATCH를 올리는 관례*)** 을 고민해야 한다.

- MAJOR: 호환성이 깨지는 변경
- MINOR: 새로운 기능 추가
- PATCH: 버그 수정

호환성이 깨지지 않는 한 가능한 오래 하나의 MAJOR에 머무는 것이 좋다. 저자가 관리한 오픈소스 라이브러리는 4년 넘게 MAJOR 3에 머물렀고, 그 사이 51개의 새 기능이 추가되어 마지막 릴리즈가 3.51.0이었다.

### 4.1 미리 경고하기

호환성을 깰 수밖에 없다면 미리 알린다. 언어가 지원한다면 어노테이션을 활용한다: .NET은 `[Obsolete]`, 자바는 `@Deprecated`.

```csharp
[Obsolete("Use Get method with restaurant ID.")]
[HttpGet("calendar/{year}/{month}")]
public Task<ActionResult> LegacyGet(int year, int month)
```

이 어노테이션은 컴파일러가 해당 메서드 호출자에게 경고를 표시하도록 만든다.

호환성 파괴 변경이 여러 개라면 하나의 MAJOR 릴리즈로 묶는 편이 낫다. 클라이언트 개발자가 매번 대응할 필요 없이 한 번에 처리할 수 있기 때문이다.

> 결국 소프트웨어 공학이란 것은 판단력을 발휘해야 하는 기술(art)이다.

---

## 요약

- 기존 코드베이스에서 작업할 때는 **조금씩 점진적으로** 진행한다. 오래 걸리는 기능을 위한 별도 브랜치는 병합 지옥으로 이어지기 쉽다
- **완전히 새로운 기능**은 기능 플래그 뒤에 숨기고 자주 통합한다. 코드 병합과 기능 릴리즈를 분리하라
- 기능 플래그는 완성 후 삭제한다. 컴파일러 오류를 따라가며 의존 코드를 정리한다
- **기존 기능 개선**은 스트랭글러 패턴으로 접근한다: 새 대안을 옆에 두고, 호출자를 하나씩 옮기고, 마지막에 이전 것을 지운다
- 메서드 수준 스트랭글러: 새 메서드/오버로드 추가 → 호출자 이전 → 이전 메서드 삭제
- 클래스 수준 스트랭글러: 새 클래스 추가 → 임시 변환 도우미 → 호출자 이전 → 이전 클래스 삭제
- 각 단계에서 **모든 커밋이 master에 병합 가능한 상태**여야 한다
- 외부에 공개된 API라면 유의적 버전을 도입한다. 호환성이 깨지지 않는 한 하나의 MAJOR에 오래 머무는 것이 이상적
- 호환성 파괴는 신중하게 결정하고 미리 경고한다 (``[Obsolete]``, ``@Deprecated``)
