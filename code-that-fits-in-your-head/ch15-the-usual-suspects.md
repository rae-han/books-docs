# Chapter 15: The Usual Suspects (유력한 용의자)

## 핵심 질문

성능, 보안, 알고리즘, 아키텍처 — 소프트웨어 공학이라 하면 곧바로 떠오르는 "유력한 용의자"들에 대해 이 책이 왜 지금까지 침묵했는가? 이 주제들을 어떻게 다뤄야 균형 잡힌 판단을 내릴 수 있는가?

---

## 1. 왜 지금에서야 다루는가

"성능은 왜 안 다루나요? 보안은요? 의존성 분석, 알고리즘, 아키텍처, 컴퓨터과학은요?"

모두 소프트웨어 공학을 이야기할 때 항상 불려나오는 유력한 용의자들이다. 이 책이 지금까지 이 주제들에 침묵한 이유는 **중요하지 않아서가 아니라 이미 잘 다루어진 훌륭한 자료가 많기 때문**이다.

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 저자가 컨설팅에서 성능을 가르쳐야 하는 경우는 거의 없었다. 알고리즘/컴퓨터과학은 저자보다 잘 아는 팀원이 많고, 보안도 마찬가지다. 이 책은 **가르쳐야 할 필요가 있는 프랙티스**를 다룬다.
:::

『클린 코드』, 『코드 컴플리트』 같은 책이 채우지 못한 공백을 이 책이 메꾸는 셈이다. 15장에서는 그동안 다루지 않았던 성능과 보안, 그리고 몇 가지 다른 프랙티스에 대한 접근 방식을 정리한다.

---

## 2. 성능

싫어하는 아이디어를 받아들이지 않기 위해 사람들이 자주 꺼내는 반박이 있다.

> "하지만 성능은 어떻습니까?"

이 질문에는 두 가지 배경이 있다고 저자는 본다: **과거의 유산**과 **명료성 추구**.

### 2.1 과거의 유산

수십 년 동안 컴퓨터는 느렸다. 컴퓨터 과학이라는 학문이 만들어지던 시기에는 비효율적 알고리즘 하나가 프로그램을 쓸모없게 만들 수 있었다. 그래서 **빅오 표기법(*Big O Notation - 알고리즘의 시간/공간 복잡도를 점근적으로 표현하는 방법*)**, 메모리 사용량, 복잡도 계산이 컴퓨터 과학 커리큘럼에 자리잡았다.

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 문제는 이 커리큘럼이 **그대로 굳어졌다**는 점이다. 최신 컴퓨터가 너무 빨라 대부분의 경우 10나노초와 100나노초의 차이는 무의미하다. 데이터베이스 쿼리 옆에서 메서드 호출을 몇 마이크로초 줄이려는 노력은 낭비다.
:::

> 프로그램이 제대로 동작하지 않아도 된다면, 카드 한 장당 1밀리초만 걸리는 프로그램도 쉽게 작성할 수 있죠.
> — 제럴드 와인버그(Gerald Weinberg) 『프로그래밍 심리학』에서

**우선순위**:

1. **정확성** — 일단 동작하게 만든다
2. **보안** — 다음으로 중요할 수 있다
3. **성능** — 측정한 뒤 최적화

성능이 정말 중요하면 **측정하라**. 현대 컴파일러는 메서드 인라이닝, 루프 최적화 등을 수행하기 때문에 생성된 기계어는 상상과 전혀 다를 수 있다. **성능은 추정할 수 없다.**

### 2.2 명료성

사람들이 성능에 집착하는 다른 이유는 명료성(*legibility*)과 관련이 있다. 이 아이디어는 제임스 스콧의 『국가처럼 보기(*Seeing Like a State*)』에서 왔다.

중세 마을은 구전 문화로 운영되었다. 특정 토지에 대한 사용권은 계절과 관습에 따라 유동적이었다. 왕이 세금을 직접 부과할 수 없었고, 지역 귀족에 의존해야 했다. 이 의존성을 없애기 위해 왕은 **지적도(*Cadastral map - 토지 소유권을 기록한 지도*)** 를 도입했다. 지적도는 복잡한 현실을 단순한 소유권으로 환원하여 명료성을 부여했지만, 이 과정에서 많은 것을 잃었다. 지도는 현실을 반영하는 것을 넘어 **현실을 바꾸어 놓았다**.

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 소프트웨어는 형태가 없다. 그래서 **측정 가능한 것**에 집착하게 된다. 관리자는 근무시간, 커밋 수, 성능 수치 같은 간접 지표로 성과를 측정하려 한다. 성능 집착은 형태 없는 소프트웨어 공학을 지적도처럼 명료하게 만들려는 시도일 수 있다.
:::

망치를 든 사람에게는 모든 것이 못처럼 보인다. 측정 가능한 성능은 소프트웨어 공학의 지적도가 된다. 하지만 지적도가 마을의 복잡성을 담지 못하듯, 성능 수치도 소프트웨어의 본질을 담지 못한다.

---

## 3. 보안

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 소프트웨어 보안은 보험과 같다. 정말로 비용을 지불하고 싶지 않지만, 가입하지 않으면 나중에 후회한다. **완벽하게 안전한 시스템은 없다** — 무장 경비를 배치해도 뇌물, 강요, 속임수가 존재한다.
:::

보안에서는 **적절한 균형**을 찾아야 한다.

### 3.1 STRIDE 위협 모델

**STRIDE 위협 모델(*STRIDE Threat Model - Microsoft가 개발한 위협 분류 체계. 여섯 가지 위협 유형의 앞글자를 딴 이름*)** 을 체크리스트처럼 사용하면 보안 전문가가 아니어도 위협을 체계적으로 검토할 수 있다.

| 약자 | 위협 | 설명 |
|---|---|---|
| S | 스푸핑(*Spoofing*) | 다른 사람인 척 위장 |
| T | 변조(*Tampering*) | 데이터 무단 변경 (예: SQL 주입) |
| R | 거부(*Repudiation*) | 정상 작업 수행 사실 부인 |
| I | 정보 노출(*Information Disclosure*) | 읽어선 안 되는 데이터 노출 |
| D | 서비스 거부(*Denial of Service*) | 정상 사용자의 서비스 이용 방해 |
| E | 권한 상승(*Elevation of Privilege*) | 부여된 것 이상의 권한 획득 |

위협 모델링은 프로그래머만의 영역이 아니다. **IT 전문가, 세일즈, 프로덕트 등 이해관계자가 모두 참여**해야 한다. 어떤 문제는 코드로, 어떤 문제는 네트워크 구성으로, 어떤 문제는 그냥 감수해야 한다.

### 3.2 레스토랑 예약 시스템에 STRIDE 적용하기

레스토랑 예약 REST API에 대해 각 위협을 체크해보자.

#### 스푸핑
예약 시 원하는 어떤 이름이나 사용해도 된다. "키아누 리브스"라고 입력해도 시스템이 받아들인다. 문제가 될까? **시스템의 동작이 이름에 따라 바뀌지 않으므로 스푸핑으로는 동작을 바꿀 수 없다.** 레스토랑 주인에게 문제가 될지 확인이 필요하지만, 코드 관점에서는 큰 문제 아님.

#### 변조
- **HTTP를 통한 변조**: URL만 알면 PUT/DELETE로 예약 수정 가능. GUID로 예약 ID를 사용해 추측을 어렵게 했지만, POST 응답의 Location 헤더가 노출될 수 있음 → **HTTPS 필수**. IT 전문가 영역.
- **직접 DB 접근**: 안전한 배포 구성이나 신뢰할 수 있는 클라우드 DB 사용 → IT 전문가 영역.
- **SQL 주입**: 프로그래머의 책임. 이름 있는 매개변수를 사용하여 방어.

```csharp
// Restaurant/e89b0c2/Restaurant.RestApi/SqlReservationsRepository.cs
public async Task Delete(Guid id)
{
    const string deleteSql = @"
        DELETE [dbo].[Reservations]
        WHERE [PublicId] = @id";

    using var conn = new SqlConnection(ConnectionString);
    using var cmd = new SqlCommand(deleteSql, conn);
    cmd.Parameters.AddWithValue("@id", id);
    await conn.OpenAsync().ConfigureAwait(false);
    await cmd.ExecuteNonQueryAsync().ConfigureAwait(false);
}
```

이름 있는 SQL 매개변수 ``@id`` 를 사용하면 ADO.NET이 SQL 주입을 방어한다. **코드 리뷰와 짝 프로그래밍에서 반드시 이 부분을 확인**해야 한다.

#### 거부
사용자가 예약해놓고 나타나지 않는 문제. 병원, 미용실 등 모든 예약 기반 사업의 골칫거리다. 완화 방법:

- 사용자 인증 요구
- 디지털 서명 기반 감사 로그
- 신용카드 선결제

**하지만** 레스토랑 주인은 대개 이런 조치가 고객에게 부담을 주어 아예 오지 않게 만들까 걱정한다. **너무 안전하게 만들면 원래 목적을 달성하지 못한다** — 보안 균형의 대표적 예.

#### 정보 노출
비밀번호는 저장하지 않지만 이메일과 예약 정보가 있다. 지배인이 특정 날짜의 전체 일정을 GET하면 이름과 이메일이 노출된다.

```
GET /restaurants/2112/schedule/2021/2/23 HTTP/1.1
Authorization: Bearer eyJhbGci0iJIUZI1NiIsInCI6IkpXVCJ9.eyJ...

HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
{
  "name": "Nono",
  ...
  "reservations": [{
    "id": "2c7ace4bbee94553950afd60a86c530c",
    "at": "2021-02-23T19:45:00.0000000",
    "email": "anarchi@example.net",
    "name": "Ann Archie",
    "quantity": 2
  }]
}
```

완화책: **JSON 웹 토큰(*JWT - 서명된 클레임을 JSON으로 표현하는 토큰 형식*)** 으로 인증. 지배인 역할이 없으면 403 Forbidden.

```csharp
[Theory]
[InlineData(1, "Hipgnosta")]
[InlineData(2112, "Nono")]
[InlineData(90125, "The Vatican Cellar")]
public async Task GetScheduleWithoutRequiredRole(
    int restaurantId,
    string name)
{
    using var api = new SelfHostedApi();
    var token =
        new JwtTokenGenerator(new[] { restaurantId }, "Foo", "Bar")
            .GenerateJwtToken();
    var client = api.CreateClient().Authorize(token);

    var actual = await client.GetSchedule(name, 2021, 12, 6);

    Assert.Equal(HttpStatusCode.Forbidden, actual.StatusCode);
}
```

민감 정보를 포함하는 리소스에만 인증을 요구하고, 일반 예약 리소스는 인증 없이 유지 → 거부 방지와의 균형.

#### 서비스 거부
- 저수준 크래시: C#, Java, JavaScript 같은 **관리형 코드(*Managed Code - 런타임이 메모리를 관리하는 코드로, 버퍼 오버플로 등의 저수준 취약점을 원천 차단*)** 는 버퍼 오버플로 방어. 발생 시 플랫폼 결함 → 최신 상태 유지가 유일한 방어.
- 분산 서비스 거부(DDoS): IT 전문가와 상의.
- 트래픽 급증: 필요하다면 **CQRS 아키텍처(*Command Query Responsibility Segregation - 명령과 조회를 분리하고 구체화 뷰와 내구성 큐를 활용하는 아키텍처*)** 로 대응. 다만 복잡도가 크게 오르므로 필요성 판단이 중요.

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 위협 모델링에서 위협을 인식한 뒤 **해결하지 않기로 결정해도 괜찮다**. 궁극적으로 사업상의 결정이기 때문이다. 다만 다른 조직 구성원에게 위협을 인지시키는 것이 중요하다.
:::

#### 권한 상승
SQL 주입이 여기서도 문제. DB 실행 계정의 권한을 최소화(**최소 권한 원칙**)하고, DB를 관리자 권한으로 실행하지 말 것.

---

## 4. 다른 기법들

성능과 보안 외에도 카나리아 배포, A/B 테스팅, 내결함성, 의존성 분석, 리더십, 분산 시스템 알고리즘, 유한 상태 기계, 디자인 패턴, 지속적 배포, SOLID 원칙 등 다뤄야 할 프랙티스는 방대하다. 여기서는 두 가지만 간단히 언급한다.

### 4.1 속성 기반 테스트

자동화된 테스트를 처음 접하는 프로그래머는 **테스트할 값**을 고르는 데 어려움을 겪는다. 아래 테스트를 보자.

```csharp
[Theory]
[InlineData(0)]
[InlineData(-1)]
public void QuantityMustBePositive(int invalidQuantity)
{
    Assert.Throws<ArgumentOutOfRangeException>(() =>
        new Reservation(
            Guid.NewGuid(),
            new DateTime(2024, 8, 19, 11, 30, 0),
            new Email("vandal@example.com"),
            new Name("Ann da Lucia"),
            invalidQuantity));
}
```

0은 경계값이라 포함해야 하지만, -1은 왜 -1이어야 하는가? -42여도 된다. 어떤 음수라도 좋다면, **임의의 음수를 생성하는 프레임워크**를 쓰는 게 낫다. 이것이 **속성 기반 테스트(*Property-based Testing - 무작위 값을 생성해 시스템의 일반적인 속성을 검증하는 테스트 기법*)** 의 발상이다.

F#의 **FsCheck**를 사용하면 아래처럼 리팩터링된다.

```csharp
[Property]
public void QuantityMustBePositive(NonNegativeInt i)
{
    var invalidQuantity = -i?.Item ?? 0;
    Assert.Throws<ArgumentOutOfRangeException>(() =>
        new Reservation(
            Guid.NewGuid(),
            new DateTime(2024, 8, 19, 11, 30, 0),
            new Email("vandal@example.com"),
            new Name("Ann da Lucia"),
            invalidQuantity));
}
```

FsCheck는 ``PositiveInt``, ``NonNegativeInt``, ``NegativeInt`` 같은 래퍼 형식을 내장한다. 각 속성은 기본 100번 실행되며, 매번 다른 임의 값이 재생성된다. 여기서 더 확장하면 ID, 날짜, 이메일, 이름까지 모두 FsCheck가 생성하게 만들 수 있다.

```csharp
[Property]
public void QuantityMustBePositive(
    Guid id,
    DateTime at,
    Email email,
    Name name,
    NonNegativeInt i)
{
    var invalidQuantity = -i?.Item ?? 0;
    Assert.Throws<ArgumentOutOfRangeException>(() =>
        new Reservation(id, at, email, name, invalidQuantity));
}
```

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 테스트 대상 시스템의 일반적인 속성을 설명하는 것이 **구체적인 테스트 케이스를 만드는 것보다 더 어렵다**. 하지만 지배인의 하루 일정처럼 복잡한 로직에서는 속성 기반이 훨씬 강력하다.
:::

### 4.2 행위 기반 코드 분석

이 책이 다룬 것은 대부분 코드의 **정적 관점**이다. 하지만 **버전 관리 시스템**을 분석하면 시간에 따른 관점을 얻을 수 있다.

- 가장 자주 변경되는 파일은?
- 어떤 파일들이 같이 변경되는가?
- 어떤 개발자가 어떤 파일만 담당하는가?

이 분야를 **행위 기반 코드 분석(*Behavioral Code Analysis - 커밋 이력에서 패턴을 추출해 코드 품질을 분석하는 기법*)** 이라 부르며, 아담 톤힐(Adam Tornhill)의 두 책(『Your Code as a Crime Scene』, 『Software Design X-Rays』)이 실무 적용을 다룬다.

두 가지 대표 시각화:

| 시각화 | 의미 |
|---|---|
| **변경 결합도 지도(*Change Coupling Map*)** | 함께 변경되는 파일들을 선으로 연결 — 정적 의존성 분석으로 찾기 어려운 결합 발견 |
| **핫스팟 포함 관계도(*Hotspot Enclosure Diagram*)** | 원 크기 = 파일 복잡도, 색 진하기 = 변경 빈도 — 개선 우선순위 파악 |

지식 지도로 확장하여 팀의 **버스 지수(*Bus Factor - 몇 명이 사라지면 프로젝트가 멈추는지 나타내는 지표*)** 도 측정할 수 있다.

---

## 5. 결론

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 소프트웨어에서 가장 중요한 속성은 **성능이 아니라 정확성**이다. 제대로 동작하는 소프트웨어를 만든 뒤에야 성능을 논할 수 있다. 그리고 궁극적으로는 성능·보안·유지보수성 사이의 우선순위가 **비즈니스 결정**이라는 것을 잊지 말아야 한다.
:::

성능, 보안, 코드 리뷰, 복잡도 분석, 공식 프로세스 — 이 모든 것이 소프트웨어 공학이다. 이 책이 이야기한 프랙티스와 휴리스틱은 **그 위에서 함께 작동**해야 한다. 무엇이 가장 중요한지는 프로그래머 혼자 결정할 문제가 아니다.

---

## 요약

- 성능/보안/알고리즘/아키텍처는 유력한 용의자 — 이미 좋은 자료가 많아 이 책이 침묵했을 뿐
- **성능 집착**은 (1) 과거 컴퓨터가 느렸던 시대의 유산, (2) 명료성 없는 소프트웨어에 명료성을 부여하려는 시도
- 정확성 → 보안 → 성능 순의 우선순위. **성능은 추정 불가, 반드시 측정**
- **STRIDE 위협 모델**: 스푸핑/변조/거부/정보 노출/서비스 거부/권한 상승 — 체크리스트처럼 활용
- 위협 완화는 코드/네트워크/사업 결정이 섞인 문제 — IT/세일즈/프로덕트가 모두 참여
- SQL 주입은 프로그래머 책임 → 이름 있는 매개변수 사용, 코드 리뷰에서 확인
- 정보 노출은 JWT 등 인증으로 방어, 다만 인증 요구가 사업 목적을 훼손하지 않는 균형이 필요
- **속성 기반 테스트**(FsCheck)로 테스트 값 선택 문제를 해결, 100번 실행으로 커버리지 확장
- **행위 기반 코드 분석**으로 정적 관점 넘어 커밋 이력에서 인사이트 추출 — 변경 결합도, 핫스팟, 버스 지수
- 우선순위(성능/보안/유지보수) 결정은 궁극적으로 이해관계자와 함께 내려야 하는 **비즈니스 판단**
