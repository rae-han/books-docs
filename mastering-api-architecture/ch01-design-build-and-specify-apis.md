# Chapter 1: Design, Build, and Specify APIs (API 설계, 구현, 명세)

## 핵심 질문

같은 참석자 정보를 다루더라도 REST와 gRPC 중 무엇을 골라야 하는가? 그 선택을 무엇으로 정당화하는가? 그리고 API가 살아 있는 동안 계속 바뀔 텐데, 소비자를 깨뜨리지 않으면서 바꾸려면 무엇을 미리 정해둬야 하는가?

## 1. 사례 연구: 참석자 API의 설계

0장에서 레거시 컨퍼런스 시스템을 API 주도 아키텍처로 옮기기로 했고, 첫 단계는 참석자 API를 제공할 참석자 서비스를 새로 구현하는 것이다. API를 효과적으로 설계하려면 **누가 생산자이고 누가 소비자인지**부터 정해야 한다. 생산자는 참석자 팀이며, 이 팀은 성격이 다른 두 관계를 관리한다.

- **참석자 팀(생산자) ↔ 레거시 컨퍼런스 팀(소비자)**: 두 팀은 가깝고 구조 변경을 쉽게 조율할 수 있다. 생산자와 소비자 서비스 사이에 **강한 응집**을 허용할 수 있는 관계다
- **참석자 팀(생산자) ↔ 외부 CFP 시스템(소비자)**: 연관은 있지만 어떤 변경이든 조율이 필요하다. **느슨한 결합**이 필요하고 단절적 변경(*breaking change*)을 주의해서 관리해야 한다

> **핵심 통찰**: 같은 데이터를 노출하더라도 소비자와의 **관계**가 다르면 적절한 API 형식이 달라진다. 이 장의 모든 선택(REST vs gRPC, 표준, 버저닝)은 결국 이 두 관계 중 어느 쪽을 다루는가로 갈린다.

## 2. REST 다시 보기

REST(*REpresentational State Transfer*)는 아키텍처적 제약의 집합이며 대개 HTTP를 전송 프로토콜로 쓴다. 완전한 정의는 로이 필딩(Roy Fielding)의 논문에 있지만, 실용적으로 RESTful하다는 것은 다음을 만족한다는 뜻이다.

- 생산자가 **리소스를 모델링**하고 소비자는 그 리소스와 상호작용하는 형태로 관계를 정의한다
- 요청에 **상태가 없다**. 생산자는 이전 요청의 상세를 캐싱하지 않으며, 소비자가 처리에 필요한 정보를 매번 전달한다
- 요청을 **캐싱할 수 있다**. 생산자는 보통 HTTP 헤더로 힌트를 제공한다
- 소비자에게 **일관된 인터페이스**를 제공한다 (HTTP 동사, 리소스 등)
- **계층형 시스템**이며 시스템의 복잡도를 REST 인터페이스 뒤로 추상화한다. 소비자는 뒤에 데이터베이스가 있는지 다른 서비스가 있는지 몰라야 한다

### HTTP로 보는 예시

아래 예제에서 `---` 위쪽은 요청, 아래쪽은 응답이다.

```http
GET http://mastering-api.com/attendees
Accept: application/json

---

200 OK
Content-Type: application/json
{
  "displayName": "Jim",
  "id": 1
}
```

`GET`은 **메서드(동사)** 로 리소스에 수행할 행위를 설명하고, 여기서 리소스는 `attendees`다. `Accept` 헤더는 소비자가 받고 싶은 콘텐츠 종류를 정의한다. REST는 **본문에 리소스 표현**을, **헤더에 메타데이터**를 담는다. 응답의 상태 코드 `200 OK`는 생산자가 요청을 성공적으로 처리했음을 알린다.

콘텐츠 타입은 여러 가지를 쓸 수 있지만 **소비자가 파싱할 수 있는지**가 관건이다. `application/pdf`를 돌려주는 것도 가능하지만 다른 시스템이 쓰기 좋은 데이터 표현은 아니다.

### 리처드슨 성숙도 모델

레너드 리처드슨(Leonard Richardson)이 2008년 QCon에서 여러 REST API를 리뷰한 경험을 발표하며 제시한 모델이다(마틴 파울러가 블로그로 널리 알렸다). 팀마다 REST를 반영하는 수준이 다르다는 관찰에서 출발한다.

1. **레벨 0 — HTTP/RPC**: HTTP로 API를 구현하고 단일 URI 개념만 있다. 동사를 쓰지 않고 단순 데이터 교환용 엔드포인트를 제공한다. 사실상 HTTP 위에 RPC를 얹은 것이다
2. **레벨 1 — 리소스**: URI로 리소스를 모델링한다. `GET /attendees/1`처럼 특정 참석자를 돌려주는 API를 추가하면 레벨 1이다. 파울러는 이를 객체 지향의 **아이덴티티** 도입에 비유했다
3. **레벨 2 — 동사(메서드)**: 서버 리소스에 미치는 영향에 따라 서로 다른 HTTP 동사로 접근한다. `GET`이 서버 상태를 바꾸지 않음을 보장하고, 같은 URL에 `DELETE /attendees/1`·`PUT /attendees/1` 같은 여러 작업을 표현한다
4. **레벨 3 — 하이퍼미디어 제어**: HATEOAS(*Hypertext As The Engine Of Application State*)로 탐색 가능한 API를 제공한다. `GET /attendees/1` 응답에 그 객체로 할 수 있는 행위(수정·삭제)와 사용법이 함께 담긴다

레벨 3은 REST 설계의 전형이지만 **모던 RESTful HTTP 서비스에서는 드물다**. 탐색은 유연한 UI 스타일 시스템에는 유용해도 서비스 간 API 호출에는 잘 맞지 않고, 생산자를 개발하는 동안 가능한 행위를 미리 다 정의해야 해서 구현 경험이 상당히 불편하다.

> **핵심 통찰**: 실무의 목표점은 **레벨 2**다. 여기까지만 해도 이해하기 쉬운 리소스 모델과 그 모델에 허용되는 행위를 소비자에게 제공할 수 있고, 결합을 느슨하게 하며 뒷단 서비스의 상세를 숨길 수 있다.

## 3. RPC와 gRPC

**RPC**(*Remote Procedure Call - 원격 프로시저 호출*)는 한 프로세스에서 메서드를 호출하되 그 실행은 다른 프로세스에서 이뤄지게 하는 방식이다. REST가 도메인 모델을 투영하고 기반 기술을 추상화한다면, **RPC는 메서드를 그대로 노출**하고 다른 프로세스가 직접 호출한다.

**gRPC**는 고성능 RPC의 오픈 소스 구현이며 리눅스 재단이 관리하고, 대부분의 플랫폼에서 사실상 표준 RPC 프로토콜로 채택되고 있다.

```
┌──────────────────────────────┐              ┌──────────────────────────────┐
│  레거시 컨퍼런스 서비스          │              │      참석자 서비스              │
│  ┌────────────────────────┐  │              │  ┌────────────────────────┐  │
│  │  gRPC 스텁 [라이브러리]   │  │ gRPC/HTTP/2  │  │  gRPC 서버 [라이브러리]  │  │
│  │  원격 호출의 복잡도를 추상화│──┼─────────────▶│  │  특정 포트에서 트래픽 수신│  │
│  └───────────┬────────────┘  │              │  └───────────┬────────────┘  │
│              │ 호출            │             │              │ 호출           │
│  ┌───────────▼────────────┐  │              │  ┌───────────▼────────────┐  │
│  │  레거시 로직 [패키지]      │  │             │  │  참석자 로직 [패키지]     │  │
│  └────────────────────────┘  │              │  └────────────────────────┘  │
└──────────────────────────────┘              └──────────────────────────────┘
```

클라이언트 측은 **스텁**(*stub*)으로 원격 호출의 복잡도를 감추고, 생산자와 소비자 상호작용을 모두 처리할 **스키마**가 필요하다.

REST와 RPC의 중요한 차이는 **상태**다. REST는 상태가 없지만 RPC는 구현에 따라 상태가 존재할 수 있고, 응답을 돌려주는 과정에서 상태를 만들기도 한다. 이렇게 상태를 쌓으면 **신뢰성과 라우팅 복잡성이라는 비용을 치르고 고성능을 얻는다**. RPC 모델은 2차 서비스가 필요로 하는 정확한 기능을 **메서드 수준**으로 전달하는 경향이 있어 생산자-소비자 결합이 더 강해진다. 다만 **성능이 핵심 요구사항인 수평 서비스 사이에서는 그 결합이 꼭 나쁜 것은 아니다**.

### GraphQL은 어디에 놓이는가

RPC는 개별 기능에 대한 접근을 열어주지만 소비자에게 모델이나 추상화를 주지는 않는다. REST는 생산자가 제공하는 단일 API의 리소스 모델을 확장한다. 여러 API를 같은 기반 URL로 제공할 수도 있지만(3장), 그러면 소비자는 클라이언트 쪽에서 상태를 만들기 위해 **순차적으로 쿼리**해야 하고 관련된 모든 서비스의 구조를 이해해야 한다. 응답의 일부만 필요할 때는 낭비다. 화면과 네트워크가 제약된 **모바일**에서 특히 그렇다.

**GraphQL**은 기존 서비스·데이터 스토어·API 위의 기술 계층으로, 여러 소스에 걸친 쿼리 언어를 제공한다. 클라이언트가 **필요한 필드만 정확히** 요청할 수 있고 여러 API에 걸쳐 지정할 수도 있다. GraphQL 스키마 언어로 타입과 조합 방식을 명시하며, 주요 장점 중 하나는 **모든 API에 대해 단일 버전을 제공**해 소비자가 복잡한 버전 관리를 하지 않아도 된다는 점이다.

GraphQL은 소비자가 서로 연결된 여러 서비스에 단일 API로 접근해야 할 때 가장 빛난다. 데이터가 여러 서브시스템에 흩어진 시스템에서 내부 복잡도를 추상화하는 데 이상적이고, UI와 보고서·데이터 웨어하우징 스타일 시스템을 함께 모델링할 때도 잘 맞는다. 레거시 위에 **퍼사드**(*facade*)로 얹을 수도 있지만, **잘 설계된 API 위에 얹을수록 퍼사드를 만들고 유지하기 쉽다**. 경쟁 기술이 아니라 보완 기술로 보는 편이 낫다.

## 4. REST API 표준과 구조

REST의 규칙은 아주 기본적이라, 구현과 설계의 대부분은 개발자 경험에 의존하게 된다. 에러는 어떻게 전달하지? 페이징은? 호환성 문제는 어떻게 막지? 여기서 표준과 가이드라인이 필요해진다. 책은 **마이크로소프트 REST API 가이드라인**을 따른다. 내부 가이드라인을 오픈소스로 공개한 것이며, `MUST`·`SHOULD`·`SHOULD NOT`·`MUST NOT`을 정의한 RFC-2119 용어를 써서 요구사항이 필수인지 선택인지 명확하다.

### 리소스 생성과 PII

새 참석자를 만드는 엔드포인트를 설계해보자.

```http
POST http://mastering-api.com/attendees
{
  "displayName": "Jim",
  "givenName": "James",
  "surname": "Gough",
  "email": "jim@mastering-api.com"
}

---

201 CREATED
Location: http://mastering-api.com/attendees/1
```

`Location` 헤더는 새로 생성된 리소스의 위치이며, 여기서 사용자에 대한 고유 ID를 모델링했다. `email`을 고유 ID로 쓸 수도 있지만 가이드라인 7.9절은 **개인 식별 정보(*Personally Identifiable Information - PII*)를 URL의 일부로 쓰지 말라**고 권고한다. 경로나 쿼리 파라미터는 서버 로그나 네트워크 중간 지점에 캐싱되기 때문이다.

API 설계에서 어려운 것 중 하나가 **이름**이다. 이름을 바꾸는 간단한 작업만으로도 호환성이 깨진다. 가이드라인에 표준 이름 몇 가지가 있지만, 팀이 **공통 도메인 데이터 사전**을 만들어 보충해야 한다. 회사가 제공하는 모든 API의 이름이 일관되면 소비자가 응답을 이해하고 이어 붙이기 쉬워진다.

### 컬렉션과 페이징

`GET /attendees`의 응답을 배열 하나로 모델링해도 동작은 한다.

```http
GET http://mastering-api.com/attendees

---

200 OK
[
  { "displayName": "Jim", "givenName": "James", "surname": "Gough",
    "email": "jim@mastering-api.com", "id": 1 }
]
```

그런데 배열을 **객체 안에 중첩**하면 더 큰 컬렉션과 **페이징**을 모델링할 수 있다.

```http
200 OK
{
  "values": [
    { "displayName": "Jim", "givenName": "James", "surname": "Gough",
      "email": "jim@mastering-api.com", "id": 1 }
  ],
  "@nextLink": "{opaqueUrl}"
}
```

> **핵심 통찰**: 지금 참석자가 한 명뿐이어도 응답을 객체로 감싸 두는 이유는, **나중에 페이징을 붙이려고 배열을 객체로 바꾸는 순간 호환성이 깨지기 때문**이다. 표준을 미리 채택하는 값어치가 여기서 나온다.

### 컬렉션 필터링

REST의 필터링 표준은 **OData** 기반의 표현식 언어를 쓰는 것이다.

```http
GET http://mastering-api.com/attendees?$filter=displayName eq 'Jim'
```

처음부터 필터링과 검색을 완벽히 구현할 필요는 없다. 다만 표준을 기준으로 설계해두면 나중에 **호환성 문제 없이** API를 개선할 수 있다. 여러 서비스에 걸친 쿼리·필터링이 필요하다면 GraphQL이 가장 적합하다.

### 에러 처리

에러를 일관되게 다루려면 **에러 표준을 미리 정의해 생산자와 공유**하는 것이 좋다. 가이드라인은 "개발자는 요청 처리가 실패하는 경우 에러를 일관되게 처리할 수 있는 하나의 코드 블록을 작성해야 한다"고 못박는다. 소비자는 **상태 코드**를 기준으로 로직을 짜므로 상황에 맞는 코드를 반드시 줘야 한다.

- **2xx**: 성공. 그런데 성공 응답 본문에 에러를 담아 돌려주는 API가 의외로 많다 — 하지 말아야 한다
- **3xx**: 리다이렉션. 일부 클라이언트 라이브러리가 적극 활용한다
- **4xx**: 보통 클라이언트 측 에러. 이때 `message` 필드의 내용이 개발자와 최종 사용자에게 매우 유용하다
- **5xx**: 보통 서버 측 실패. 일부 클라이언트 라이브러리는 이 경우 요청을 재시도한다

예상 못 한 실패가 났을 때 서비스에 무슨 일이 벌어지는지 **생각하고 문서화**하는 것도 중요하다. 결제 시스템의 500 에러는 결제가 됐다는 뜻인가, 안 됐다는 뜻인가?

> **참고**: 외부 소비자에게 가는 에러 메시지에 스택 추적이나 민감 정보가 섞이지 않게 해야 한다. 공격자에게 그대로 재료가 된다. 마이크로소프트 가이드라인에는 상세한 스택 추적·이슈 설명을 담는 `InnerError` 개념이 있는데, 디버깅에는 유용하지만 **외부로 나가서는 안 된다**.

### ADR 가이드라인: API 표준의 선택

- **결정사항**: 어떤 API 표준을 채택할 것인가?
- **논의사항**: 회사가 이미 채택한 표준이 있는가? 그 표준을 외부 소비자에게까지 확대할 수 있는가? 이미 표준을 갖춘 소비자에게 노출해야 하는 서드파티 API를 쓰고 있는가? 표준을 채택하지 **않는 것**이 소비자에게 어떤 영향을 주는가?
- **권장사항**: 조직 문화와 이미 보유한 API 형식에 가장 잘 맞는 표준을 고른다. 진화를 염두에 두고 도메인·업계에 필요한 수정은 표준에 덧붙인다. **나중에 호환성 문제를 겪지 않도록 표준은 미리 채택한다.** 기존 API가 소비자에게 이해하기 쉬운지, 아니면 설명에 더 많은 노력이 드는지 주의 깊게 본다

## 5. OpenAPI로 REST API 명세 작성하기

API 개수가 늘수록 **API의 형태와 구조를 소비자와 공유할 메커니즘**이 급해진다. 그래서 생긴 것이 OpenAPI 이니셔티브와 **OpenAPI 명세**(*OpenAPI Specification - OAS*)다. 스와거(Swagger)가 처음 구현했지만 이제는 대부분의 도구가 OpenAPI를 쓴다.

OAS는 JSON 또는 YAML로 API의 구조, 도메인 객체, 요구사항을 서술한다. 구조뿐 아니라 **법적·라이선스 요구사항 같은 메타데이터**와 개발자가 참조할 문서·예제도 담을 수 있다.

### 명세를 공유하면 생기는 것들

**① 코드 생성** — OAS의 가장 유용한 기능이다. 서버·보안·구조 정보를 바탕으로 API를 표현하고 호출하는 모델과 서비스 객체를 만들어낸다. OpenAPI 생성기 프로젝트는 다양한 언어를 지원한다 — 자바는 스프링이나 JAX-RS를, **타입스크립트는 선호하는 프레임워크를 조합해** 고를 수 있다. 심지어 **구현 스텁**까지 생성할 수 있다.

여기서 **명세를 먼저 쓸지, 서버 코드를 먼저 쓸지** 결정해야 한다. 그리고 OAS의 한계를 알아야 한다 — **명세는 API의 형태만 서술할 뿐, 여러 조건에서의 의미(기대 동작)를 완전히 모델링하지는 못한다.** 그래서 2장의 계약 테스트가 필요해진다.

**② 검증** — 요청과 응답이 명세대로인지 확인한다. 코드를 생성했으면 당연히 일치하지 않겠느냐고 생각할 수 있지만, 실제 쓰임새는 **API와 인프라를 보호하는 것**이다. 많은 조직이 구역화 아키텍처(*zonal architecture*)를 쓰고 유입 트래픽으로부터 네트워크를 지키려 DMZ(*demilitarized zone - 비무장지대*)를 둔다. DMZ 안에서 메시지를 검사해 **명세와 맞지 않는 트래픽을 버리는 것**이 유용한 방어다(6장).

아틀라시안(Atlassian)의 오픈소스 `swagger-request-validator`가 그 예다.

<details>
<summary>원서 예제 (Java)</summary>

```java
// 명세의 위치를 지정해 검증기를 생성한다.
// basePathOverride는 검증기가 게이트웨이/프록시 뒤에 있을 때 유용하다.
final OpenApiInteractionValidator validator = OpenApiInteractionValidator
    .createForSpecificationUrl(specUrl)
    .withBasePathOverride(basePathOverride)
    .build();

// 요청과 응답 객체는 빌더를 이용해 변환하거나 생성할 수 있다.
final ValidationReport report = validator.validate(request, response);
if (report.hasErrors()) {
    // 에러를 처리한다.
}
```

</details>

```typescript
import * as OpenApiValidator from 'express-openapi-validator';

// 명세를 기준으로 요청·응답을 검증하는 미들웨어를 붙인다.
app.use(
  OpenApiValidator.middleware({
    apiSpec: specUrl,
    validateRequests: true,
    validateResponses: true, // 응답까지 명세와 대조한다
  }),
);

// 검증 실패는 에러 핸들러로 모인다.
app.use((err: any, _req: Request, res: Response, _next: NextFunction) => {
  if (err.status === 400) {
    res.status(400).json({ message: err.message, errors: err.errors });
    return;
  }
  res.status(500).json({ message: 'internal error' });
});
```

`basePathOverride`에 해당하는 고민은 TS 쪽에서도 같다. 게이트웨이가 경로를 바꿔 전달하면 명세의 `basePath`와 실제 경로가 어긋나므로, 프록시 뒤에 배포할 때는 기준 경로를 맞춰줘야 한다.

**③ 예제와 모의 데이터** — OAS에는 예제 응답을 담을 수 있다. 문서로도 유용하지만, 예제를 그대로 **모의 서비스**로 띄워 소비자가 쿼리해보게 하는 도구도 있다. 개발자 포털을 만들 때 특히 좋고, **구현을 시작하기 전에 생산자와 소비자가 데이터를 공유**할 수 있다는 점이 결정적이다. **API를 직접 호출해보는 경험이 명세 문서를 리뷰하는 것보다 훨씬 낫다.** 다만 명세에 넣는 예제는 기본적으로 문자열이라 명세와 어긋날 수 있어서, `openapi-examples-validator` 같은 도구로 예제가 해당 요청/응답 컴포넌트와 일치하는지 검증한다.

**④ 변경 탐지** — 명세는 API 변경을 탐지하는 데도 쓰이며 데브옵스 파이프라인에서 특히 유용하다. 이것이 버저닝으로 이어진다.

## 6. API 버저닝

코드 라이브러리라면 변경이 새 버전으로 패키징되고, 재컴파일하고 테스트하기 전까지 프로덕션에 아무 영향이 없다. 그런데 **API는 실행 중인 서비스**라 변경이 즉시 반영된다. 업그레이드 옵션은 셋이다.

1. **새 버전을 새 위치에 배포한다** — 기존 버전은 계속 서비스되고, 소비자는 새 기능이 필요할 때만 옮겨오면 된다. 대신 **API 소유자가 여러 버전을 유지 관리**하고 패치·버그 수정도 각각 지원해야 한다
2. **하위호환되는 새 버전을 릴리스한다** — 기존 사용자에게 영향이 없다. 소비자는 아무것도 안 바꿔도 되지만, 생산자는 다운타임이나 업그레이드 중 두 버전의 가용성을 함께 고려해야 한다. **잘못된 필드 이름을 고치는 소소한 수정도 호환성을 깰 수 있다**
3. **호환성을 버리고 모든 소비자가 업그레이드하게 한다** — 나쁜 생각처럼 보이지만 호환을 유지할 수 없는 상황이 실제로 있다. 전체 시스템의 일괄 변경을 유발하므로 **다운타임 조율이 필요**하다

현실적으로는 이 셋을 조합해서 지원해야 하고, 그러려면 **버저닝 규칙**과 **버전을 소비자에게 노출하는 방법**을 정해야 한다.

### 시맨틱 버저닝

시맨틱 버저닝(*semantic versioning*)은 릴리스를 `메이저.마이너.패치`로 표현하며, 기존 버전 대비 **바뀐 동작**을 기준으로 숫자를 올린다.

- **메이저**: 기존 API와 **호환되지 않는** 변경. 새 메이저로 올릴지는 소비자가 결정하며, 마이그레이션 가이드와 추적 수단이 함께 제공되는 것이 보통이다
- **마이너**: **하위호환되는** 변경. 소비자는 클라이언트를 고치지 않고도 새 마이너를 쓸 수 있다
- **패치**: 기능 변화 없이 기존 `메이저.마이너`의 **버그를 고친** 경우

`1.5.1`이면 메이저 1, 마이너 5, 패치 1이다. 5장에서 이 버저닝을 API 수명주기·릴리스와 연결한다.

### 명세로 단절적 변경 잡아내기

`openapi-diff` 같은 도구로 두 명세를 비교할 수 있다. 먼저 `givenName` 필드 이름을 `firstName`으로 바꾼 경우 — 소비자는 `givenName`을 쓰고 있으므로 **단절적 변경**이다.

```console
$ docker run --rm -t \
    -v $(pwd):/specs:ro \
    openapitools/openapi-diff:latest /specs/original.json /specs/first-name.json

- GET /attendees
  Return Type:
  - Changed 200 OK
    Media types:
    - Changed */*
      Schema: Broken compatibility
        Missing property: [n].givenName (string)

-- Result --
API changes broke backward compatibility
```

반대로 `age` 필드를 **추가**하는 것은 기존 동작을 해치지 않는다.

```console
$ docker run --rm -t \
    -v $(pwd):/specs:ro \
    openapitools/openapi-diff:latest --info /specs/original.json /specs/age.json

- GET /attendees
  Return Type:
  - Changed 200 OK
      Schema: Backward compatible

-- Result --
API changes are backward compatible
```

> **실무 팁**: 이런 비교 도구를 API 파이프라인에 넣어두면 소비자가 의도치 않은 호환성 문제를 겪는 일을 막을 수 있다. 단, 도구는 OpenAPI 버전에 민감하므로 **쓰는 명세 버전을 그 도구가 지원하는지** 확인해야 한다. 실제로 책의 예제에서도 예전 버전 명세를 썼을 때는 단절적 변경이 감지되지 않았다.

## 7. gRPC로 RPC 구현하기

참석자 서비스 같은 **수평 서비스**는 트래픽이 높은 편이고 아키텍처 전반에서 쓰이는 마이크로서비스로 구현되곤 한다. 이런 자리에는 더 작은 데이터 전달과 높은 속도를 지원하는 gRPC가 REST보다 잘 어울린다. 물론 **성능과 관련된 결정은 언제나 측정으로 확인해야 한다**.

아래 `attendees.proto`는 OpenAPI 예제와 같은 `attendee` 객체를 모델링한다.

```protobuf
syntax = "proto3";
option java_multiple_files = true;
package com.masteringapi.attendees.grpc.server;

message AttendeesRequest {
}

message Attendee {
  int32 id = 1;
  string givenName = 2;
  string surname = 3;
  string email = 4;
}

message AttendeeResponse {
  repeated Attendee attendees = 1;
}

service AttendeesService {
  rpc getAttendees(AttendeesRequest) returns (AttendeeResponse);
}
```

프로토콜이 **바이너리 표현**을 쓰므로 메시지 레이아웃을 결정하는 **필드의 번호와 순서가 절대적으로 중요하다.**

- 새 서비스나 새 메서드 추가, 메시지에 새 필드 추가는 하위호환적이다. 단 **새 필드는 반드시 선택적**이어야 한다
- 필드를 **제거하거나 이름을 바꾸면** 데이터 타입 해석이 어긋나 호환성이 깨진다. 필드 **개수**도 전달 필드 인식에 쓰이므로 문제를 만든다

REST/OpenAPI에서는 명세가 가이드 역할이라 너그럽다 — 필드를 추가하거나 순서를 바꿔도 문제가 없다. **gRPC에서는 버저닝과 호환성을 훨씬 더 엄격하게 다뤄야 한다.**

<details>
<summary>원서 예제 (Java, Spring Boot Starter)</summary>

```java
@GrpcService
public class AttendeesServiceImpl extends
        AttendeesServiceGrpc.AttendeesServiceImplBase {

    @Override
    public void getAttendees(AttendeesRequest request,
                             StreamObserver<AttendeeResponse> responseObserver) {
        AttendeeResponse.Builder responseBuilder = AttendeeResponse.newBuilder();
        // 응답을 생성
        responseObserver.onNext(responseBuilder.build());
        responseObserver.onCompleted();
    }
}
```

</details>

```typescript
import * as grpc from '@grpc/grpc-js';
import * as protoLoader from '@grpc/proto-loader';

const packageDefinition = protoLoader.loadSync('attendees.proto');
const proto = grpc.loadPackageDefinition(packageDefinition) as any;

/** getAttendees RPC 구현 — 참석자 목록을 담아 콜백으로 응답한다. */
const getAttendees: grpc.handleUnaryCall<AttendeesRequest, AttendeeResponse> = (
  _call,
  callback,
) => {
  const attendees: Attendee[] = [
    { id: 1, givenName: 'Jim', surname: 'Gough', email: 'gough@mail.com' },
  ];
  callback(null, { attendees });
};

const server = new grpc.Server();
server.addService(proto.com.masteringapi.attendees.grpc.server.AttendeesService.service, {
  getAttendees,
});
server.bindAsync('0.0.0.0:9090', grpc.ServerCredentials.createInsecure(), () => {
  server.start();
});
```

gRPC는 라이브러리 없이 브라우저에서 바로 쿼리할 수 없어서 테스트에는 gRPC UI 플러그인이나 `grpcurl` 명령줄 도구를 쓴다.

```console
$ grpcurl -plaintext localhost:9090 \
    com.masteringapi.attendees.grpc.server.AttendeesService/getAttendees
{
  "attendees": [
    { "id": 1, "givenName": "Jim", "surname": "Gough", "email": "gough@mail.com" }
  ]
}
```

## 8. 교환 방식과 API 형식의 선택

0장의 트래픽 패턴이 여기서 판단 기준이 된다. 마이크로서비스 안에서 서비스와 교환 방식을 **완전히 제어할 수 있다면** 외부 소비자와는 불가능한 타협점을 찾을 수 있다.

수직 서비스 간 교환은 대개 인터넷 구간을 지나므로 **레이턴시가 높고**, 마이크로서비스 아키텍처라면 하나의 수직 요청이 **여러 개의 수평 교환**을 유발한다. 그러니 수평 트래픽은 그 누적 지연이 소비자에게 드러나지 않을 만큼 효율적이어야 한다.

- **트래픽이 높은 서비스**: 참석자 서비스는 중심 서비스라 여러 컴포넌트가 `attendeeId`를 추적하게 된다. 교환율이 높아지면 페이로드 크기와 프로토콜 제약 탓에 **네트워크 전송 비용**이 늘어난다. 여기서 비용은 금전일 수도 있고 메시지가 도착하기까지의 총 시간일 수도 있다
- **대용량 데이터 페이로드**: JSON은 사람이 읽을 수 있지만 바이너리보다 길어서 페이로드가 커지고 전송 성능 저하에 취약하다. 또 본문을 언어 수준 도메인 모델로 **해석하는 시간**도 무시할 수 없으며, 전통적인 서버 측 언어 상당수는 바이너리보다 JSON 처리에 더 애를 먹는다
- **HTTP/2의 성능 이점**: **바이너리 프레임 계층**이 메시지를 잘게 쪼개 압축하고, 한 연결에서 전체 요청·응답의 **멀티플렉싱**을 허용한다. 참석자 20명을 조회할 때 HTTP/1이면 TCP 연결 20개가 필요하지만 HTTP/2는 하나로 처리한다. **gRPC는 기본적으로 HTTP/2를 쓰고 바이너리 프로토콜로 데이터 크기를 줄인다**
- **구형 형식들**: 모든 서비스가 현대적 설계인 것은 아니다. 구형 컴포넌트를 도입할 때는 전체 성능 영향도를 이해해야 하며, 격리하고 개선하는 방법은 8장에서 다룬다

> **참고**: "JSON은 사람이 읽을 수 있다"는 근거는 자주 오용된다. 요즘 추적 도구는 개발자가 메시지를 직접 읽는 횟수를 크게 줄였고, 대용량 JSON을 처음부터 끝까지 읽는 일도 드물다. 가독성 논쟁을 잠재우는 더 나은 답은 **로깅을 강화하고 에러를 잘 처리하는 것**이다.

> **참고**: HTTP/3는 UDP 기반 전송 프로토콜인 QUIC을 사용한다. 이 흐름은 10장에서 다시 다룬다.

### ADR 가이드라인: 교환 데이터의 모델링

소비자가 레거시 컨퍼런스 팀이면 보통 **수평** 교환이고, CFP 팀이면 **수직** 교환이다. 결합도와 성능 요구가 서로 다르니 모델링도 달라야 한다.

- **결정사항**: 서비스의 API 모델링에 어떤 형식을 쓸 것인가?
- **논의사항**: 데이터 교환이 수직인가 수평인가? 소비자 코드를 제어할 수 있는가? 여러 서비스에 걸친 강력한 비즈니스 도메인이 있는가, 아니면 소비자가 직접 쿼리를 구성하게 해야 하는가? 어떤 버저닝 정책을 도입할 것인가? 기반 데이터 모델의 배포·변경 빈도는? 대역폭이나 성능이 걱정될 만큼 트래픽이 높은가?
- **권장사항**: **외부 사용자**가 쓴다면 REST가 진입 장벽이 낮고 강력한 도메인 모델도 제공한다(외부 사용이란 대개 낮은 결합도와 낮은 의존성이 필요하다는 뜻이다). **생산자가 완전히 관리하는 두 서비스** 사이이거나 트래픽이 높다면 gRPC를 고려한다

## 9. 다중 명세 — 다 제공할 수 있을까

RESTful 표현·gRPC 서비스·GraphQL 스키마를 모두 갖춘 API를 제공하는 것은 **가능하다**. 다만 쉬운 일이 아니고, 올바른 선택이 아닐 수도 있다.

참석자를 정의하는 proto와 OAS는 얼핏 크게 다르지 않다. 그래서 `openapi2proto` 같은 도구로 OAS에서 proto를 생성할 수 있는지 묻게 된다. 실행해보면 필드가 **알파벳순으로 정렬된** proto가 나온다. 하위호환 필드를 추가할 때는 괜찮지만, 그렇지 않으면 **모든 필드 번호가 밀려서** 호환성이 깨진다.

```protobuf
message Attendee {
  string a_new_field = 1;   // 알파벳순 정렬 탓에 맨 앞으로 삽입되면서
  string email = 2;         // 이하 모든 필드 번호가 바뀌고
  string givenName = 3;     // 바이너리 형식이 달라져 호환성이 깨진다
  int32 id = 4;
  string surname = 5;
}
```

다른 방향으로, `grpc-gateway`는 gRPC 서비스 앞에 **REST 퍼사드 리버스 프록시**를 만들어준다. 프록시는 빌드 타임에 `.proto`로부터 생성되며, proto의 확장 기능으로 RPC 메서드를 OAS 표현에 연결한다.

```protobuf
import "google/api/annotations.proto";
// ...
service AttendeesService {
  rpc getAttendees(AttendeesRequest) returns (AttendeeResponse) {
    option (google.api.http) = {
      get: "/attendees"
    };
  }
}
```

이러면 REST와 gRPC를 모두 제공할 수 있다. 대신 여러 명령과 Go 언어·빌드 환경 경험이 필요한 셋업을 감수해야 한다.

한 걸음 물러나 **지금 무엇을 하고 있는지** 보자. OpenAPI의 RESTful 표현을 gRPC 호출로 바꾼다는 것은 **확장된 하이퍼미디어 도메인 모델을 저수준 함수 대 함수 호출로 변환**하는 일이다. RPC와 API의 차이를 억지로 융합하려는 시도이며 호환성과 씨름하게 될 가능성이 높다. 반대 방향(gRPC → OpenAPI)도 마찬가지로 서비스를 개선할 때 어려운 이슈들이 드러난다. 게다가 두 명세는 **각자의 호환성 요구사항**을 갖고 있어서, 하나에서 다른 하나를 생성하는 순간 버저닝이 걸림돌이 된다.

> **핵심 통찰**: 수직 트래픽을 처리하면서 수평 교환용 RPC를 자동 생성하기보다, **두 API를 독립적으로 설계해 각자 자유롭게 진화시키는 편**이 더 납득할 만하다. 컨퍼런스 사례도 이 방식을 택하고 그 결정을 ADR에 남긴다.

## 요약

- REST와 RPC 기반 API를 **구현하는** 진입 장벽은 낮다. 정작 중요한 것은 설계와 구조를 신중히 고려하는 아키텍처 의사결정이다
- REST냐 RPC냐는 리처드슨 성숙도 모델과 **생산자-소비자 결합도**로 판단한다. 실무 목표점은 레벨 2다
- REST는 느슨한 표준이므로 API 표준(예: 마이크로소프트 가이드라인)을 채택해 일관성과 예측 가능성을 확보한다. PII를 URL에 넣지 않기, 컬렉션을 객체로 감싸기처럼 **나중의 호환성 사고를 미리 막는 결정**이 표준에 들어 있다
- OpenAPI 명세는 구조 공유와 자동화(코드 생성·검증·모의 데이터·변경 탐지)의 축이다. 다만 명세는 **형태**를 서술할 뿐 **의미**를 완전히 모델링하지 못한다
- 버저닝은 생산자에게 복잡도를 더하지만 소비자에게는 필수다. 시맨틱 버저닝과 명세 비교 도구를 파이프라인에 넣어 단절적 변경을 사전에 잡는다
- gRPC는 대역폭이 중요한 **수평 교환**에 이상적이고 HTTP/2 기반이라 성능 이점이 크다. 대신 필드 번호·순서에 묶인 **엄격한 호환성 규칙**을 진다
- 다중 명세는 가능하지만 한 명세에서 다른 명세를 생성하는 순간 두 개의 호환성 요구사항이 충돌한다. **REST와 RPC는 독립적으로 설계하는 편이 낫다**

## 다른 챕터와의 관계

- **0장**: 여기서 정의한 수직/수평 트래픽 구분이 이 장의 형식 선택 기준(REST vs gRPC)으로 그대로 쓰인다. ADR-001의 "설계·버저닝" 결론을 이 장이 이어받는다
- **2장**: OAS가 형태만 서술하고 의미는 담지 못한다는 한계가 **계약 테스트**의 출발점이다
- **3장**: API 게이트웨이로 여러 API를 같은 기반 URL에 노출하는 이야기, 그리고 명세 검증을 인프라 층에 두는 이야기가 이어진다
- **5장**: 시맨틱 버저닝을 API 수명주기·릴리스 전략과 연결한다
- **6장**: OpenAPI 검증을 DMZ에서 방어 수단으로 쓰는 맥락이 위협 모델링으로 확장된다
- **8장**: 구형 컴포넌트를 격리하고 개선하는 방법을 다룬다
- **10장**: HTTP/3와 비동기 통신 등 형식 선택의 다음 국면을 다룬다
