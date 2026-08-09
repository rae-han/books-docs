# Chapter 12: Troubleshooting (문제 해결하기)

## 핵심 질문

버그가 발생했을 때 사람들은 대개 "고치는 것"부터 서두른다. 예전에 효과가 있었던 마법 주문(서비스 재시작, 코드 일부 수정, 이상한 루틴 호출)을 이것저것 시도해보고, 문제가 사라진 것 같으면 왜 사라졌는지 이해하지 않은 채 다음 작업으로 넘어간다. 하지만 이런 "우연에 맡기는 프로그래밍"은 문제를 다루는 방식으로 결코 효과적이지 않다. 그렇다면 **문제를 어떻게 이해하고, 어떻게 재현하고, 어떻게 좁혀 들어가야** 할까?

---

## 1. 이해하려고 노력하라

가장 중요한 조언은 하나로 요약된다.

> 무슨 일이 일어나고 있는지 이해하려고 노력하십시오.

**우연에 맡기는 프로그래밍(*Programming by Coincidence - 코드가 왜 동작하는지 이해하지 못한 채 동작하는 것처럼 보이면 다음 작업으로 넘어가는 방식*)** 은 문제 해결의 반대말이다. 왜 동작하는지 이해하지 못하면 실제로는 동작하지 않는다는 사실도 이해하지 못한다.

### 1.1 과학적 방법

문제가 발생하면 즉시 해결 모드로 들어가는 대신 과학적 방법을 변형해서 적용한다.

- **예측**을 한다. 이것이 **가설(*Hypothesis - 관찰된 현상을 설명하는 검증 가능한 예측*)** 이다
- **실험**을 한다
- **결과와 예측을 비교**한다. 이해할 때까지 반복한다

"과학적 방법"이라는 용어에 부담 가질 필요 없다. 실험실 가운을 입거나 이중 맹검 실험을 설계할 필요는 없다. "이 함수를 호출하면 42를 반환할 것이다"처럼 단순한 예측이면 된다.

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 이 방법과 "우연에 맡기는 프로그래밍"의 가장 큰 차이점은 **작업의 목적이 문제를 해결하는 것이 아니라 문제를 이해하는 것**이라는 점이다.
:::

### 1.2 단순화 — 코드를 삭제해서 문제를 해결한다

문제를 대하는 가장 일반적인 반응은 "코드를 더 추가"하는 것이다. 하지만 근본적 구현 오류인 경우가 훨씬 많으며, **코드를 단순하게 만드는 것만으로도 놀랄 만큼 많은 문제가 해결된다**.

행동 편향의 예로 저자가 관찰한 것들이다.

- 객체 그래프를 직접 구성하는 대신 복잡한 DI 컨테이너를 개발
- 순수 함수를 쓰는 대신 복잡한 모의 객체 라이브러리를 개발
- 소스 컨트롤에 의존성을 커밋하는 대신 정교한 패키지 복원 방식을 만듦
- 자주 병합하는 대신 고급 diff 도구를 사용
- SQL을 배우는 대신 복잡한 ORM을 사용

> 단순함을 유지하기 위해서는 똑똑해야 한다. KISS 같은 구호는 방법을 모르면 쓸모없다.

### 1.3 고무 오리 디버깅

막힐 때 도움이 되는 기술이다.

- **시간 관리**: 한 문제에 25분 정도만 붙잡고 있다가, 진척이 없으면 잠시 자리에서 일어난다
- **컴퓨터에서 멀어지기**: 커피를 마시고 걸어다니는 사이 새로운 관점이 떠오른다
- **동료에게 설명하기**: 문제를 설명하다가 "아, 됐어요, 방금 생각났어요!"로 대화가 끊기는 경험이 흔하다
- **고무 오리에게 설명하기(*Rubber Duck Debugging - 무생물 사물에게 문제를 소리 내어 설명하면서 스스로 깨닫는 디버깅 기법*)**: 동료가 없다면 오리에게라도 설명한다
- **Stack Overflow에 질문 초안 쓰기**: 저자는 자주 이 방법을 쓴다. 질문을 완성하기도 전에 답을 깨닫는 경우가 많다

---

## 2. 결함 (Defects)

이상적인 결함의 수는 **0개**다. 린 소프트웨어 개발에서는 이를 **품질의 내재화(*Building Quality In - 결함을 "나중에 잡는" 것이 아니라 처음부터 만들어 넣지 않는 접근*)** 라 한다.

> "나중에 처리"하겠다며 결함을 미뤄두지 마라. 소프트웨어 개발에서 "나중"은 "절대 안 한다"와 같다.

버그가 나타나면 이를 우선순위로 삼고, 하던 일을 멈춰서 결함부터 수정한다.

### 2.1 결함을 테스트로 재현하기

버그를 이해했다면 그것을 재현하는 **실패하는 테스트**를 먼저 작성한다. 이 테스트는 회귀 테스트로 남아 같은 버그의 재발을 막는다.

레스토랑 예약 시스템에서 예약을 갱신했더니 이메일과 이름이 뒤바뀌어 저장되는 결함이 발견되었다. 원인 코드는 이렇다.

```csharp
return new Reservation(
    id,
    (DateTime)rdr["At"],
    (string)rdr["Name"],
    (string)rdr["Email"],
    (int)rdr["Quantity"]);
```

`Reservation` 생성자가 사실은 `(id, at, email, name, quantity)` 순서를 받는데, 여기서는 name과 email의 위치가 뒤바뀌어 전달되고 있었다. **두 매개변수 모두 `string`이므로 컴파일러가 잡아주지 못한다** — 문자열 원시 형식을 남용하지 말아야 할 또 다른 예시다.

수정 자체는 간단하지만, 같은 실수가 다시 일어나지 않도록 먼저 실패하는 통합 테스트를 작성한다.

```csharp
[Theory]
[InlineData("2032-01-01 01:12", "z@example.net", "z", "Zet", 4)]
[InlineData("2084-04-21 23:21", "q@example.gov", "q", "Quu", 9)]
public async Task PutAndReadRoundTrip(
    string date, string email, string name, string newName, int quantity)
{
    var r = new Reservation(
        Guid.NewGuid(),
        DateTime.Parse(date, CultureInfo.InvariantCulture),
        new Email(email),
        new Name(name),
        quantity);
    var sut = new SqlReservationsRepository(ConnectionStrings.Reservations);
    await sut.Create(r);
    var expected = r.WithName(new Name(newName));
    await sut.Update(expected);
    var actual = await sut.ReadReservation(expected.Id);
    Assert.Equal(expected, actual);
}
```

### 2.2 느린 테스트

데이터베이스를 포함하는 통합 테스트는 필연적으로 느리다. 테스트 스위트가 30분이 걸리면 리팩터링의 안전망으로 못 쓴다. TDD의 빨강-초록-리팩터 사이클에서도 5분이 넘으면 부담이 된다.

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 테스트 스위트에 걸리는 최대 시간은 **10초**여야 한다. 그보다 오래 걸리면 집중력을 잃고 이메일이나 소셜 미디어를 보고 싶어진다.
:::

해결책은 **테스트를 두 단계로 나누는 것**이다.

- 1단계: 유닛 테스트만 (`Restaurant.sln`) — 매 리팩터링/커밋마다 실행
- 2단계: 유닛 테스트 + 통합 테스트 (`Build.sln`) — 빌드 스크립트/CI에서 실행

```bash
#!/usr/bin/env bash
dotnet test Build.sln --configuration Release
```

각 통합 테스트는 새 데이터베이스를 생성하고 DDL 스크립트를 실행한 뒤 실행하고, 끝나면 데이터베이스를 분리한다. 느릴 수밖에 없다.

### 2.3 비결정적 결함 (Race Conditions)

레스토랑 예약 시스템에서 가끔 초과 예약이 발생하고 있었다. 로그를 자세히 살펴보니 **경쟁 상태(*Race Condition - 두 개 이상의 실행 흐름이 공유 자원에 접근하는 순서에 따라 결과가 달라지는 현상*)** 였다.

```csharp
[HttpPost]
public async Task<ActionResult> Post(ReservationDto dto)
{
    // ...
    var reservations = await Repository
        .ReadReservations(r.At)
        .ConfigureAwait(false);
    if (!MaitreD.WillAccept(DateTime.Now, reservations, r))
        return NoTables500InternalServerError();
    await Repository.Create(r).ConfigureAwait(false);
    // ...
}
```

두 요청이 동시에 들어오면 두 스레드가 같은 `reservations` 스냅숏을 읽고 둘 다 예약을 저장해버린다.

이 결함은 **자동화된 테스트로 재현**해야 하지만, 조건이 정확히 결정되어 있지 않다는 것이 문제다. 이럴 때는 **비결정적 테스트**를 감수한다.

```csharp
[Fact]
public async Task NoOverbookingRace()
{
    var start = DateTimeOffset.UtcNow;
    var timeOut = TimeSpan.FromSeconds(30);
    var i = 0;
    while (DateTimeOffset.UtcNow - start < timeOut)
    {
        await PostTwoConcurrentLiminalReservations(
            start.DateTime.AddDays(++i));
    }
}
```

30초 동안 두 개의 동시 예약을 반복해서 시도한다. 이 테스트에는 두 가지 실패 모드가 있다.

- **위양성(*False Positive - 실제로는 문제 없는데 실패로 판정되는 것*)** — 잡음이 커져 신호 대 잡음비가 떨어진다
- **위음성(*False Negative - 실제로는 문제 있는데 성공으로 판정되는 것*)** — 신뢰도가 떨어지지만 잡음은 없다

해결책은 `TransactionScope`로 임계 구간을 감싸 읽기/쓰기를 직렬화하는 것이었다.

```csharp
using var scope = new TransactionScope(
    TransactionScopeAsyncFlowOption.Enabled);
var reservations = await Repository
    .ReadReservations(r.At)
    .ConfigureAwait(false);
if (!MaitreD.WillAccept(DateTime.Now, reservations, r))
    return NoTables500InternalServerError();
await Repository.Create(r).ConfigureAwait(false);
await PostOffice.EmailReservationCreated(r).ConfigureAwait(false);
scope.Complete();
```

비결정적 테스트는 2단계 테스트로 미뤄둔다.

---

## 3. 이분법 (Bisection)

어떤 결함은 코드를 아무리 오래 쳐다봐도 원인을 알 수 없다. 이럴 때는 **이분법**을 쓴다.

1. 문제를 감지하거나 재현할 방법을 찾는다
2. 코드의 절반을 제거한다
3. 문제가 계속되면 2단계부터 반복. 문제가 사라지면 제거했던 코드를 복원하고 나머지 절반을 제거하고 2단계부터
4. 문제 원인을 이해할 수 있을 만큼 코드가 작아질 때까지 반복

Stack Overflow에 최소 재현 예제(*Minimal Working Example*)를 만드는 과정도 사실상 이분법이다.

### 3.1 git bisect

git에도 이분법이 내장되어 있다. 저자는 배포된 API에서 갑자기 보안 기능이 동작하지 않게 되었는데, 잘 동작하던 버전과 지금 사이에 약 130개의 커밋이 있었다.

```bash
$ git bisect start
$ git bisect bad                # 현재 커밋에 결함 있음
$ git bisect good 58fc950       # 이 커밋에서는 잘 됨
```

git은 자동으로 중간 커밋을 체크아웃한다. 그 커밋에서 결함을 확인하고 `good` 또는 `bad`를 알려준다.

```
$ git bisect good
Bisecting: 37 revisions left to test after this (roughly 5 steps)
```

약 8단계 만에 결함을 도입한 정확한 커밋을 찾아냈다.

```
2563131c2d06af8e48f1df2dccbf85e9fc8ddafc is the first bad commit
```

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 이분법은 오류의 원인을 찾아내고 분리해내는 매우 강력한 기법이다. **최소한의 작동 예제를 만들 수 있다는 것은 소프트웨어 문제 해결에서 초능력**이다.
:::

---

## 4. 문화권 문제 (Culture Bug 사례)

한 개발자의 컴퓨터에서는 실패하는 테스트가 다른 개발자의 노트북에서는 성공한 적이 있다. 같은 코드, 같은 커밋인데도. 두 개발자가 30분간 문제를 축소하자 본질적으로 **문자열 비교** 문제로 귀결되었다.

한 컴퓨터에서는 `"aa" < "bb"`인데, 다른 컴퓨터에서는 `"aa" > "bb"`였다. 원인은 **기본 문화권(*Default Culture - .NET에서 문자열 정렬·서식 규칙을 담고 있는 환경 정보*)** 이었다. 덴마크어 문화권은 `Aa`를 `Å`로 취급하는데, `Å`는 알파벳의 마지막 글자이므로 `aa > bb`가 된다.

디버깅에 대한 두 가지 시사점이 있다.

- 이 챕터가 "**디버깅**"이라는 단어를 거의 쓰지 않은 이유가 있다. 너무 많은 사람이 문제 해결을 위해 디버거에만 의존한다
- 프로덕션 환경에는 디버거를 붙일 수 없다. 과학적 방법, 자동화된 테스트, 이분법 같은 **보편적 방법**을 익혀야 한다

---

## 요약

- 결함을 마주하면 **고치기 전에 이해**한다. "우연에 맡기는 프로그래밍"은 마법 주문을 시도하고 문제가 사라진 것 같으면 끝내지만, 이는 문제를 해결하지 못한다
- **과학적 방법**을 적용하라: 가설 → 실험 → 예측과 결과 비교. 목적은 해결이 아니라 이해
- **단순화**를 항상 고려한다. 문제 해결을 위해 코드를 추가하기보다 삭제해서 해결되는 경우가 많다
- 막히면 **고무 오리 디버깅**: 시간을 정하고, 컴퓨터에서 멀어지고, 동료 또는 오리에게 설명한다
- **이상적인 결함 수는 0**. 결함이 나타나면 하던 일을 멈추고 우선 처리한다
- 결함은 **실패하는 테스트로 재현**한다. 이 테스트가 회귀 방지 안전망이 된다
- 테스트 스위트는 **10초 이내**로 유지한다. 느린 테스트는 2단계로 분리해 CI에서만 실행
- **경쟁 상태**처럼 결정적으로 재현하기 어려운 결함은 **비결정적 테스트**로라도 재현한다. 위양성/위음성 트레이드오프를 인지하고 2단계 테스트로 배치
- 원인을 못 찾겠다면 **이분법**: 코드/커밋을 반으로 갈라 문제 영역을 좁힌다. ``git bisect``는 이를 자동화해준다
- 문제 해결은 **디버거보다 보편적**이다. 프로덕션에는 디버거를 붙일 수 없다
