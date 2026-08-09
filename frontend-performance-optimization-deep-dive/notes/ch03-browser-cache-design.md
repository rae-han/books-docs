# Chapter 3: 브라우저 캐시는 믿는 게 아니라 설계하는 것이다

## 핵심 질문

가장 빠른 네트워크 요청은 요청하지 않는 것이다. 그렇다면 어떤 리소스를 얼마나 오래, 어느 레이어에서 캐싱할 것인가? `no-cache`와 `no-store`는 무엇이 다르며, 1년짜리 캐시를 걸어놓고도 배포 즉시 새 버전을 받게 하려면 어떻게 해야 하는가?

## 1. Cache-Control 헤더 완전 정복

많은 개발자가 캐시를 "그냥 켜두면 되는 기능"으로 생각한다. 하지만 새 버전을 배포했는데 사용자 브라우저가 여전히 구 버전 자바스크립트를 실행하거나, CSS 수정이 반영되지 않아 강제 새로고침 공지를 올린 경험은 누구에게나 있다. **캐시는 믿고 의존할 대상이 아니라 개발자가 세심하게 설계하고 검증해야 하는 시스템이다.**

캐시가 성능에 미치는 영향은 측정 가능하고 즉각적이다. 캐시 히트가 발생하면 네트워크 왕복 지연 100~300ms를 완전히 제거한다. 전체 요청의 80%가 캐시로 처리되면 오리진 부하도 80% 감소한다. 히트율을 5~10% 개선하는 것만으로 대규모 서비스에서는 월 수천 달러의 서버·대역폭 비용을 절감할 수 있다.

### 1.1 캐시 레이어의 이해

요청이 서버에 도달하기까지 여러 캐시 레이어를 거친다.

```
      사용자
        │ 리소스 요청
        ▼
  ┌──────────────────────┐  Cache Hit
  │ 브라우저 캐시         │ ─────────▶ 즉시 반환 (매우 빠름, 네트워크 없음)
  │ (Private Cache)      │
  │ max-age 적용         │
  └──────┬───────────────┘
         │ Cache Miss
         ▼
  ┌──────────────────────┐  Cache Hit
  │ 프락시 캐시(기업/ISP) │ ─────────▶ 프락시 반환 (빠름)
  │ public/private 적용  │
  └──────┬───────────────┘
         │ Cache Miss
         ▼
  ┌──────────────────────┐  Cache Hit
  │ CDN 캐시              │ ─────────▶ CDN 반환 (빠름)
  │ (Shared Cache)       │
  │ s-maxage 적용        │
  └──────┬───────────────┘
         │ Cache Miss
         ▼
  ┌──────────────────────┐
  │ 오리진 서버(원본)     │ ─────────▶ 오리진 응답 (느림)
  └──────────────────────┘
```

**브라우저 캐시(Private Cache)**

사용자의 로컬 디스크나 메모리에 저장되며 해당 사용자만 접근할 수 있다. 가장 큰 장점은 **네트워크를 전혀 거치지 않는다**는 점이다. 유효 기간이 남아 있으면 서버에 요청조차 보내지 않는다.

- **크기 제한**: 크롬은 일반적으로 디스크 공간의 약 10%(보통 수 GB)를 사용하며, 가득 차면 LRU(*Least Recently Used*) 알고리즘으로 오래된 항목부터 삭제한다. 개발자가 크기를 직접 제어할 수는 없지만 중요한 리소스는 서비스 워커로 별도 관리할 수 있다.
- **지속성**: 탭이나 창을 닫아도 유지되며, 사용자가 "인터넷 사용 기록 삭제"로 지우면 사라진다.
- **따르는 지시어**: `max-age`, `no-cache`, `no-store`. `private`과 `public`은 브라우저 캐시 동작을 바꾸지 않는다(브라우저 캐시는 이미 프라이빗 캐시다).

> **참고 — 트리플 키 캐싱(Partitioned Cache)**<br><br>최신 브라우저는 프라이버시 보호를 위해 캐시 키로 URL만 쓰지 않고 **(최상위 사이트, 현재 프레임, 리소스 URL)** 세 값을 조합한다. `site-a.com`과 `site-b.com`이 모두 `cdn.example.com/script.js`를 로드해도 서로 다른 캐시 항목을 쓴다. 캐시가 URL만으로 공유되면 악의적 사이트가 특정 리소스의 로드 시간을 재서 사용자가 은행 사이트를 방문했는지 추론할 수 있는데(타이밍 공격), 트리플 키 캐싱은 이를 원천 차단한다. 개발자가 직접 제어할 수는 없지만 **같은 CDN 리소스라도 사이트마다 별도 캐싱된다는 점**을 CDN 히트율 계산에 반영해야 한다.

**CDN 캐시(Shared Cache)**

여러 사용자가 공유하므로 공유 캐시라고 부른다. 서울 사용자 A가 요청한 리소스가 서울 엣지에 캐싱되면 서울의 다른 사용자 B도 같은 캐시를 쓴다.

CDN은 `s-maxage`를 우선 적용한다. `s-maxage=86400, max-age=3600`이면 브라우저는 1시간, CDN은 1일 캐싱한다. **이렇게 분리하는 이유는 캐시 무효화 전략 때문이다.** 브라우저 캐시는 개발자가 강제로 비울 수 없지만 CDN 캐시는 API로 무효화(Purge)할 수 있다. 따라서 CDN은 길게 캐싱하고 필요시 무효화하며, 브라우저는 짧게 캐싱하는 패턴이 일반적이다.

CDN 캐시가 만료되면 CDN이 오리진에 재검증 요청을 보낸다. 이 재검증은 사용자가 아니라 CDN이 수행하고, CDN↔오리진 백본 네트워크는 매우 빠르므로 오버헤드가 크지 않다.

**프락시 캐시**

엄밀히 말하면 CDN도 프락시 캐시의 일종이지만, 전통적 의미의 프락시 캐시는 기업 네트워크의 스퀴드(Squid)·엔진엑스 같은 포워드 프락시를 말한다. 프런트엔드 개발자가 직접 제어할 수는 없지만 `Cache-Control` 지시어는 프락시에도 적용된다. `private`을 설정하면 민감한 데이터가 기업 프락시에 캐싱되어 다른 직원에게 노출되는 것을 막는다. 모바일 통신사의 투명 프락시(*transparent proxy*)가 이미지를 압축하는 것을 막으려면 `Cache-Control: no-transform`을 설정한다.

> **핵심 통찰**: 각 레이어는 **독립적**이다. 브라우저 캐시가 만료돼도 CDN 캐시는 유효할 수 있고, CDN 캐시가 만료돼도 브라우저 캐시가 유효하면 브라우저는 요청조차 보내지 않는다. 그래서 파일명이 고정된 상태에서 CDN만 무효화하면 사용자 브라우저에는 구 버전이 `max-age`만큼 남는다. **이것이 파일명 해싱이 필수인 이유다.**

### 1.2 지시어의 정확한 의미

**캐시 저장 여부를 제어**

- `no-store`: 가장 강력하다. 브라우저와 모든 중간 캐시가 응답을 디스크에 저장하지 않는다. 메모리에만 임시 보관하며 탭을 닫으면 즉시 사라진다. **다른 모든 지시어를 무시한다.** 은행 거래 내역, 개인 의료 정보처럼 절대 디스크에 남으면 안 되는 데이터에만 쓴다.

**캐시 재검증을 제어**

- `no-cache`: **"캐시하지 마라"가 아니라 "캐시는 하되 사용 전에 반드시 재검증하라"**는 뜻이다. 응답을 디스크에 저장하되 쓸 때마다 오리진에 재검증 요청을 보낸다. 304면 캐시 사용, 200이면 새 콘텐츠 다운로드.
- `must-revalidate`: `no-cache`보다 덜 엄격하다. 유효 기간 내에는 재검증 없이 쓰고 만료된 후에만 재검증한다. `no-cache`가 "매번 재검증"이라면 `must-revalidate`는 "만료 후 재검증"이다.

**캐시 유효 기간을 제어**

- `max-age=N`: 유효 기간을 초 단위로 지정한다. 브라우저·CDN 모두에 적용되지만 `s-maxage`가 있으면 공유 캐시는 그쪽을 따른다. 시작 시점은 응답을 받은 시각이며, 서버의 `Date` 헤더 + `max-age`가 만료 시각이다.
- `s-maxage=N`: `shared max-age`의 약자로 CDN·프락시 같은 공유 캐시에만 적용된다. 브라우저는 완전히 무시한다.

> **실무 팁**: `max-age=0`은 `no-cache`와 완전히 같지 않다. `max-age=0`만으로는 응답이 곧바로 오래된 상태가 될 뿐이고, `stale-while-revalidate`나 `stale-if-error`가 있거나 오리진 장애 상황에서는 재검증 없이 오래된 응답이 재사용될 수 있다. 매 요청 재검증을 강제하려면 `max-age=0, must-revalidate`를 쓰거나, **의도가 한눈에 드러나는 `no-cache`를 쓰는 것이 권장된다.**

**캐시 공유 범위를 제어**

- `private`: 브라우저만 캐싱할 수 있고 CDN·프락시는 캐싱할 수 없다. 사용자별 개인화 콘텐츠에 필수다.
- `public`: 모든 캐시가 캐싱할 수 있다. 명시하지 않아도 기본적으로 공개 캐싱이 허용되지만, **`Authorization` 헤더가 있는 요청은 예외**다. 기본적으로 인증 요청은 공유 캐시에 저장되지 않는데, `public`을 명시하면 저장하도록 강제할 수 있다.

**우선순위**

가장 제한적인 지시어가 우선한다.

1. `no-store` > 모든 지시어 (캐싱 완전 비활성화)
2. `no-cache` > `max-age` (매번 재검증 강제)
3. `s-maxage` > `max-age` (공유 캐시에서)
4. `private` > `public` (공유 캐시 비활성화)

```http
# 정적 리소스(해시 파일명) — 브라우저·CDN 모두 1년 캐싱
Cache-Control: public, max-age=31536000, immutable

# HTML — 매번 재검증, 변경 없으면 304
Cache-Control: no-cache

# API 응답(짧은 캐싱) — 브라우저만 1분, CDN 캐싱 안 함
Cache-Control: private, max-age=60

# 사용자 대시보드 — 브라우저만 캐싱하되 매번 재검증
Cache-Control: private, no-cache

# 금융 거래 내역 — 아예 캐싱 안 함
Cache-Control: no-store
```

잘못된 조합도 있다.

```http
# ❌ no-store가 우선하여 max-age 무시됨
Cache-Control: no-store, max-age=3600

# ❌ private은 공유 캐시 비활성화, s-maxage는 공유 캐시용 → s-maxage 의미 없음
Cache-Control: private, s-maxage=86400
```

### 1.3 max-age와 s-maxage 분리 전략

가장 널리 쓰이는 패턴은 **CDN 캐시를 길게 설정하고 배포 시 무효화하며, 브라우저 캐시는 짧게 설정하는 것**이다.

```ts
// Next.js Route Handler
export async function GET(): Promise<Response> {
  const products = await db.products.findMany();
  return new Response(JSON.stringify(products), {
    headers: {
      'Content-Type': 'application/json',
      // 브라우저: 5분, CDN: 1시간
      'Cache-Control': 'public, max-age=300, s-maxage=3600',
    },
  });
}
```

이 설정으로 배포 시나리오를 따라가 보자.

```
[배포 전]  CDN: v1.0 (50분 남음) / 브라우저: v1.0 (2분 남음)

[12:00 배포]
  1. 코드 배포
  2. CDN 무효화 실행(클라우드플레어 API, 클라우드프런트 Invalidation 등)
  3. CDN 캐시 즉시 삭제

[12:02 사용자 A 방문]
  브라우저 캐시 만료 → CDN 요청 → CDN 미스 → 오리진 → v1.1
  → CDN이 v1.1 캐싱(1시간), 브라우저가 v1.1 캐싱(5분) ✅

[12:05 사용자 B 첫 방문]
  브라우저 캐시 없음 → CDN에 v1.1 있음(55분 남음) → 즉시 반환 ✅
```

만약 `s-maxage` 없이 `max-age=3600`만 설정했다면, CDN 무효화를 해도 브라우저 캐시는 50분 동안 v1.0을 계속 쓴다. **브라우저 캐시는 강제로 비울 수 없으므로 유효 기간을 짧게 잡아야 한다.**

**주의할 함정**

- **`s-maxage`가 있으면 공유 캐시에서 `max-age`를 완전히 덮어쓴다**: `max-age=86400, s-maxage=3600`이면 CDN은 1시간만 캐싱한다. 브라우저는 여전히 86400초를 따른다.
- **`private`과 `s-maxage`는 충돌한다**: `private, s-maxage=3600`은 의미가 없다. `private`이 우선해 CDN은 캐싱하지 않는다.
- **CDN마다 `s-maxage` 지원이 다를 수 있다**: 최신 CDN(클라우드플레어, AWS 클라우드프런트, 패스틀리)은 표준대로 지원하지만 일부 레거시 프락시나 커스텀 캐시 레이어는 무시하고 `max-age`만 따른다. 프로덕션에서 실제 동작을 테스트해야 한다.

**리소스별 권장 설정**

| 리소스 유형 | 권장 설정 | 의도 |
|---|---|---|
| 정적 리소스(해시 파일명) | `public, max-age=31536000, immutable` | 파일명이 바뀌므로 `s-maxage` 불필요 |
| HTML | `public, max-age=0, s-maxage=3600` | 브라우저는 매번 재검증, CDN은 1시간(배포 시 무효화) |
| API — 준실시간 데이터 | `public, max-age=60, s-maxage=300` | 브라우저 1분, CDN 5분 |
| API — 자주 안 바뀌는 데이터 | `public, max-age=300, s-maxage=3600` | 브라우저 5분, CDN 1시간 |
| 사용자별 데이터 | `private, max-age=300` | 브라우저만 5분, CDN 캐싱 금지 |

### 1.4 no-cache vs no-store: 가장 많이 오해받는 지시어

**`no-cache`: 캐싱하되 매번 재검증**

브라우저는 응답을 디스크에 저장하고, 사용할 때마다 조건부 요청을 보낸다.

```http
# 최초 응답
HTTP/1.1 200 OK
Cache-Control: no-cache
ETag: "abc123"
Content-Type: text/html

# 재방문 시 브라우저의 조건부 요청
GET /index.html HTTP/1.1
If-None-Match: "abc123"

# 변경 없으면 서버 응답 (바디 없음, 약 500B)
HTTP/1.1 304 Not Modified
ETag: "abc123"
Cache-Control: no-cache
```

핵심은 **항상 최신 상태를 보장하면서도 변경되지 않았다면 대역폭을 절약한다**는 점이다. 100KB HTML 파일이라면 304 응답은 약 500B로 200배 작다.

**`no-store`: 아예 캐싱하지 않음**

디스크에 저장하지 않으므로 뒤로가기를 눌러도 서버에 전체 콘텐츠를 다시 요청해야 한다. 조건부 요청도 없다. 매번 200 OK로 전체를 받는다.

**뒤로가기 시나리오 성능 비교**

200KB HTML 페이지를 기준으로 비교하면 다음과 같다.

| 지시어 | 디스크 저장 | 뒤로가기 동작 | 네트워크 |
|---|---|---|---|
| `no-cache` | 저장함 | 서버에 재검증 → 변경 없으면 304(500B) → 캐시된 응답 사용 | 재검증만, 빠름 |
| `no-store` | 저장 안 함 | 서버에 전체 요청 → 200 OK(200KB) 대기 → 다운로드 후 표시 | 전체 다운로드, 느림 |
| `max-age=3600` | 저장함 | 디스크에서 즉시 표시 | 없음, 매우 빠름 |

`no-store`는 뒤로가기 시 500ms 동안 빈 화면이 될 수 있다. 이것이 **HTML에는 `no-cache`를 쓰고 `no-store`는 피해야 하는 이유**다.

**흔한 실수 네 가지**

1. **HTML에 `no-store` 사용**: 뒤로가기가 매우 느려진다. `no-cache`로 바꾼다.
2. **민감한 데이터에 `no-cache` 사용**: `no-cache`는 디스크에 저장한다. 공용 컴퓨터에서 신용카드 API를 호출하면 정보가 브라우저 캐시 폴더에 남는다. 금융·의료·개인 식별 정보에는 반드시 `no-store`를 쓴다.
3. **`no-cache, no-store` 함께 사용**: `no-store`가 우선하므로 `no-cache`는 무시된다. 의도에 따라 하나만 선택한다.
4. **모든 API에 `no-cache` 사용**: 블로그 글 목록처럼 자주 안 바뀌는 데이터에 매번 재검증하면 DB를 매번 조회한다. 적절한 `max-age`(예: 1시간)를 설정하는 편이 서버 부하와 응답 속도 모두 유리하다. 실시간 재고가 중요한 상품 목록은 짧은 캐시(1분)나 `no-cache`가 적절하다.

**지시어별 사용 시나리오**

| 지시어 | 사용 시나리오 |
|---|---|
| `no-store` | 민감한 개인정보(금융·의료·신용카드), 일회용 데이터(OTP·세션 토큰), 법적 규제 대상 |
| `no-cache` | 항상 최신 상태 필요(HTML, `manifest.json`), 뒤로가기 성능 중요, 대역폭 절약(304 활용) |
| `max-age` | 민감하지 않은 데이터, 일정 시간 오래된 데이터 허용 가능, 서버 부하 감소가 중요 |

### 1.5 public과 private의 실전 활용

`private`을 빠뜨리면 **사용자 A의 개인정보가 CDN에 캐싱되어 사용자 B에게 노출되는 심각한 보안 사고**가 발생한다.

```
❌ Cache-Control: max-age=600  (private 누락)
  1. 사용자 A가 /api/dashboard 요청
  2. CDN이 A의 대시보드를 10분간 캐싱
  3. 사용자 B가 /api/dashboard 요청 (같은 URL!)
  4. CDN이 캐싱된 A의 대시보드를 B에게 반환
  5. 사용자 B가 A의 개인정보를 봄 ← 보안 사고

✅ Cache-Control: private, max-age=600
  A의 데이터는 A의 브라우저에만 저장되고 CDN은 저장하지 않음
```

`Cache-Control` 헤더를 아예 설정하지 않은 세션 기반 인증 API가 더 위험하다. 일부 CDN이 기본 캐싱 정책을 적용해 같은 사고가 발생한다.

**URL 구조와 캐싱 전략의 관계**

| 패턴 | 예시 URL | 선택 |
|---|---|---|
| URL에 사용자 식별자 없음 | `/api/me`, `/api/my/cart`, `/api/my/wishlist` | **`private` 필수.** 같은 URL에 사용자마다 다른 응답이므로 CDN이 섞을 위험이 매우 높다 |
| URL에 사용자 ID 포함 + 권한 검증 | `/api/users/12345/avatar` | **`public` 가능.** URL이 다르므로 섞일 위험이 없다. 단 권한 검증은 필수 |
| 같은 사용자라도 공개/비공개 구분 | `/api/users/:id/profile` vs `/api/users/:id/settings` | 공개 프로필은 `public`, 개인 설정은 `private` |

**API 캐싱 전략 의사결정 트리**

```
개인정보가 포함되어 있는가?
  ├ Yes ──▶ private 필수
  └ No
     │
     같은 URL이 사용자마다 다른 응답을 반환하는가?
       ├ Yes ──▶ private 필수
       └ No
          │
          이 데이터가 CDN에 캐싱되어 다른 사용자에게 보여도 괜찮은가?
            ├ No ──▶ private 필수
            └ Yes
               │
               Authorization 헤더가 있는가?
                 ├ No  ──▶ public (명시 없어도 캐싱됨)
                 └ Yes ──▶ public 명시 (CDN 캐싱 활성화)
```

### 1.6 조건부 요청과 재검증 (ETag, Last-Modified)

`no-cache`나 `must-revalidate`는 "캐시를 쓰기 전에 서버에 확인하라"고 지시한다. 서버가 변경 여부를 어떻게 판단하는지가 조건부 요청(*conditional request*)의 역할이다.

**ETag: 콘텐츠 기반 검증**

ETag(*Entity Tag*)는 파일의 '지문'이다. 파일 내용이 바뀌면 ETag도 바뀐다. 서버가 해시값이나 버전 번호를 ETag로 만들어 전달하면, 브라우저는 다음 요청 시 `If-None-Match` 헤더로 되돌려 보낸다.

```ts
// Next.js Route Handler — ETag 직접 구현
import crypto from 'node:crypto';

export async function GET(req: Request): Promise<Response> {
  const post = await db.posts.findById(1);
  const content = JSON.stringify(post);

  // 콘텐츠로 ETag 생성
  const etag = `"${crypto.createHash('md5').update(content).digest('hex')}"`;

  // 클라이언트가 보낸 ETag 확인
  if (req.headers.get('if-none-match') === etag) {
    return new Response(null, {
      status: 304,
      headers: { ETag: etag, 'Cache-Control': 'no-cache' },
    });
  }

  return new Response(content, {
    status: 200,
    headers: {
      'Content-Type': 'application/json',
      ETag: etag,
      'Cache-Control': 'no-cache',
    },
  });
}
```

대부분의 프레임워크는 ETag를 자동 생성한다. Express.js는 `etag` 미들웨어가 기본 활성화돼 있고 Next.js도 기본적으로 생성한다(`generateEtags: false`로 끌 수 있으나 대부분 기본값 유지가 좋다).

**Last-Modified: 시간 기반 검증**

파일의 마지막 수정 시간을 전달하고, 브라우저는 `If-Modified-Since`로 되돌려 보낸다. 더 단순하지만 초 단위 해상도라는 한계가 있다.

**둘의 비교**

| 기준 | ETag | Last-Modified |
|---|---|---|
| 정확도 | 콘텐츠 기반이라 더 정확 | 시간 기반이라 1초 단위 제한 |
| 성능 | 해시 계산 비용 있음 | 시간 비교만, 매우 빠름 |
| 사용 사례 | API 응답, 동적 HTML | 정적 파일, 이미지 |
| 1초 내 여러 번 변경 | 감지 가능 | 감지 불가 |
| 서버 부하 | 높음(매번 해시 계산) | 낮음(DB 타임스탬프만) |
| DB 구조 | 별도 필드 불필요 | `updated_at` 필드 필요 |

브라우저가 두 헤더를 모두 받으면 **ETag를 우선**한다. 대부분의 경우 ETag 하나로 충분하다.

**Strong ETag vs Weak ETag**

- **Strong ETag** (`ETag: "abc123"`): 바이트 단위로 완전히 동일해야 한다. 1바이트라도 다르면 다른 ETag다. 실무에서 대부분 이것을 쓴다.
- **Weak ETag** (`ETag: W/"abc123"`): 의미적으로 동일하면 같은 ETag를 가진다. HTML에 공백이나 주석이 추가돼도 렌더링 결과가 같다면 유지할 수 있다. 대용량 파일 압축이나 정규화된 HTML 비교 같은 특수한 경우에만 쓴다.

**주의사항**

- **ETag 계산 비용**: 요청마다 대용량 파일의 해시를 계산하면 서버 부하가 크다. DB의 `updated_at` 타임스탬프를 ETag로 활용하면 훨씬 효율적이다.
- **로드 밸런서 환경의 ETag 불일치**: 서버별 ETag 생성 방식이 다르면 같은 파일도 다른 ETag를 가져 304를 받지 못한다. 아파치 2.4의 기본 `FileETag`는 `MTime Size`지만 구버전이나 별도 설정에서는 `INode MTime Size`일 수 있다. 엔진엑스는 기본 ETag에 inode를 포함하지 않는다. 해결책은 세 가지다. ① 아파치에서 `FileETag MTime Size`(또는 `None`)로 조정, ② 엔진엑스 `etag off` 후 애플리케이션에서 직접 생성, ③ **CDN을 앞에 두어 오리진이 여러 대여도 CDN이 ETag를 일관되게 관리하도록 한다(프로덕션 권장).**

### 1.7 Vary 헤더로 캐시 키 관리하기

`Cache-Control`이 캐시의 **유효 기간**을 제어한다면, `Vary`는 **무엇을 캐시 키로 쓸지**를 제어한다.

```http
GET /app.js HTTP/1.1
Accept-Encoding: gzip, br

HTTP/1.1 200 OK
Content-Encoding: gzip
Cache-Control: public, max-age=31536000
Vary: Accept-Encoding
```

CDN은 캐시를 이렇게 분리한다.

```
캐시 키 1: URL=/app.js + Accept-Encoding=gzip     → Gzip 압축 파일
캐시 키 2: URL=/app.js + Accept-Encoding=br       → 브로틀리 압축 파일
캐시 키 3: URL=/app.js + Accept-Encoding=identity → 비압축 파일
```

`Vary: Accept-Encoding`이 없으면 첫 사용자가 Gzip으로 요청했을 때 이후 모든 사용자가 Gzip 버전을 받는다. 반대로 첫 사용자가 비압축을 요청했다면 모든 사용자가 비압축 파일을 받아 대역폭이 낭비된다.

**위험한 패턴: 쿠키 폭발**

`Vary: Cookie`는 가장 위험하다. 쿠키 값마다 별도 캐시 항목이 생성되므로 사용자가 1,000명이면 캐시 항목도 1,000개다. **캐시 히트율이 거의 0%가 되고 CDN의 의미가 사라진다.** 더 큰 문제는 구글 애널리틱스나 광고 추적 쿠키처럼 캐싱과 무관한 쿠키도 캐시 키에 포함된다는 점이다.

해결책은 명확하다. 사용자별 개인화 콘텐츠라면 `Cache-Control: private`으로 CDN 캐싱을 막는다. 쿠키의 특정 값에만 의존한다면 엣지 컴퓨팅으로 필요한 부분만 추출해 캐시 키를 만든다.

```ts
// 클라우드플레어 워커 예시
export default {
  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);
    const cookies = request.headers.get('Cookie');

    // 특정 쿠키만 추출
    const region = cookies?.match(/region=([^;]+)/)?.[1] ?? 'us';

    // 캐시 키에 region만 포함
    const cacheKey = new Request(`${url.toString()}?region=${region}`, request);
    const cache = caches.default;

    let response = await cache.match(cacheKey);
    if (!response) {
      response = await fetch(request);
      await cache.put(cacheKey, response.clone());
    }
    return response;
  },
};
```

**위험한 패턴: User-Agent**

`Vary: User-Agent`도 매우 위험하다. User-Agent 문자열은 브라우저 종류·버전·OS·기기 정보를 모두 포함하므로 크롬이 자동 업데이트되기만 해도 캐시 키가 바뀐다. 실제로는 수백 가지 조합이 존재해 캐시가 극도로 파편화된다. 해결책은 URL 자체를 분리하는 것이다(`m.example.com` / `www.example.com` 또는 `/mobile/` / `/desktop/`).

**실전 권장 사항**

- ✅ `Vary: Accept-Encoding` — 값이 3~4가지뿐이라 안전하며 **모든 정적 리소스에 필수**
- ⚠️ `Vary: Accept` — 사용 시 값의 가짓수가 많지 않은지 확인
- ❌ `Vary: Cookie` — 절대 사용 금지
- ❌ `Vary: User-Agent` — 절대 사용 금지

> **핵심 통찰**: `Vary`는 강력하지만 위험한 도구다. **가능하면 URL 구조로 문제를 해결하고**, `Vary`는 압축처럼 값의 가짓수가 명확히 제한된 경우에만 쓴다. `Vary` 추가 후 CDN 히트율이 급락했다면 값이 너무 다양하다는 신호다.

## 2. 파일명 해싱으로 안전한 장기 캐싱

캐시 설정에서 마주치는 가장 큰 딜레마는 **"1년 동안 캐싱하되, 배포할 때는 즉시 새 버전을 받게 하라"**는 요구다. 파일명 해싱이 이 모순을 우아하게 해결한다.

```html
<!-- 첫 배포 -->
<script src="/js/app.abc123.js"></script>
<link rel="stylesheet" href="/css/style.def456.css" />

<!-- 코드 수정 후 재배포 -->
<script src="/js/app.xyz789.js"></script>   <!-- 해시가 바뀌어 완전히 다른 파일 -->
<link rel="stylesheet" href="/css/style.def456.css" />  <!-- CSS는 안 바뀌어 해시 동일 -->
```

브라우저는 `app.abc123.js`와 `app.xyz789.js`를 완전히 다른 파일로 인식한다. 따라서 1년짜리 캐시를 설정해도 안전하다.

**핵심은 HTML과 정적 파일의 캐시 전략을 분리하는 것이다.**

```
HTML (index.html)
  → Cache-Control: no-cache
  → 매번 서버에 확인(ETag로 304 가능)
  → 항상 최신 파일명 해시를 참조

정적 파일 (app.[hash].js, style.[hash].css)
  → Cache-Control: public, max-age=31536000
  → 1년간 캐싱 (파일명이 바뀌면 새 파일로 인식)
```

배포 시나리오로 따라가 보자.

```
[첫 방문 2024-01-01]
  GET /index.html          → 200 (no-cache), <script src="app.v1.js">
  GET /app.v1.js           → 200 (max-age=31536000)  → 1년간 캐시

[재방문 2024-01-02]
  GET /index.html (If-None-Match) → 304 Not Modified
  app.v1.js는 캐시에서 사용 (서버 요청 없음)

[새 버전 배포 2024-01-03] app.js 수정 → app.v2.js로 변경

[배포 후 첫 방문]
  GET /index.html (If-None-Match) → 200 OK, <script src="app.v2.js">
  GET /app.v2.js           → 200  → 새로 다운로드
  app.v1.js는 더 이상 참조되지 않음
```

### 2.1 빌드 도구별 설정

**웹팩**

```js
// webpack.config.js
module.exports = {
  output: {
    filename: '[name].[contenthash].js',
    chunkFilename: '[name].[contenthash].chunk.js',
    assetModuleFilename: 'assets/[name].[contenthash][ext]',
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: '[name].[contenthash].css',
    }),
  ],
};
```

> **실무 팁**: `[contenthash]`와 `[hash]`는 다르다. `[contenthash]`는 **파일 내용의 해시**라서 바뀐 파일만 새 이름을 얻지만, `[hash]`는 **전체 빌드의 해시**라 한 파일만 바뀌어도 모든 파일명이 바뀐다. 캐시 재사용을 위해 반드시 `[contenthash]`를 쓴다.

**비트**

비트는 기본적으로 파일명 해싱이 활성화돼 있다. 경로를 커스터마이징하려면 다음과 같이 설정한다.

```ts
// vite.config.ts
import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        entryFileNames: 'js/[name].[hash].js',
        chunkFileNames: 'js/[name].[hash].js',
        assetFileNames: 'assets/[name].[hash].[ext]',
      },
    },
  },
});
```

**Next.js**

자동으로 처리한다. `/_next/static/` 경로의 해시 포함 파일에 `Cache-Control: public, max-age=31536000`을 자동 설정하므로 별도 설정이 필요 없다.

**엔진엑스로 직접 서빙하는 경우**

```nginx
server {
    # 해시가 포함된 정적 파일 — 1년 캐싱
    location ~* \.[0-9a-f]{8,}\.(js|css|png|jpg|jpeg|gif|svg|woff|woff2)$ {
        add_header Cache-Control "public, max-age=31536000";
    }

    # 해시가 없는 정적 파일 — 1시간
    location ~* \.(js|css|png|jpg|jpeg|gif|svg|woff|woff2)$ {
        add_header Cache-Control "public, max-age=3600";
    }

    # HTML은 항상 재검증
    location ~* \.html$ {
        add_header Cache-Control "no-cache";
    }
}
```

### 2.2 파일명 해싱이 주는 네 가지 이득

1. **안전한 장기 캐싱**: 1년짜리 `max-age`를 설정해도 안전하다.
2. **자동 캐시 무효화**: 수동으로 `?v=2` 쿼리 파라미터를 붙일 필요가 없다.
3. **선택적 갱신**: 바뀐 파일만 새로 받고, 안 바뀐 라이브러리 번들은 캐시에서 재사용한다.
4. **배포 안정성**: 배포 중간에 일부 사용자가 옛 HTML을, 일부가 새 HTML을 받아도 충돌하지 않는다.

마지막 항목이 특히 중요하다. 파일명이 고정돼 있으면 **옛 HTML을 캐시한 사용자가 `app.js`를 참조하는데 서버의 `app.js`는 이미 새 버전으로 교체돼 있어**, HTML이 기대하는 함수가 없어 에러가 난다. 파일명 해싱은 옛 파일이 서버에 남아 있으므로 이 문제가 없다.

## 3. Stale-While-Revalidate로 최신성과 성능 모두 잡기

`no-cache`로 매번 재검증하면 최신성은 보장되지만 느리고, `max-age`로 장기 캐싱하면 빠르지만 오래된 데이터를 보여줄 수 있다. SWR(*stale-while-revalidate*) 패턴은 이 딜레마를 해결한다.

> **참고**: 버셀의 리액트 데이터 페칭 라이브러리 SWR과 혼동하지 않아야 한다. 이 절의 SWR은 **HTTP 캐시 전략**인 `stale-while-revalidate`를 가리킨다. 버셀의 라이브러리는 이 캐시 전략에서 영감을 받아 이름 붙였으며 같은 원리를 클라이언트 사이드에 적용한 것이다.

### 3.1 작동 원리

```http
Cache-Control: max-age=60, stale-while-revalidate=86400
```

이 설정은 캐시를 세 가지 상태로 나눈다.

- **신선(fresh)**: 0~60초. 서버에 요청하지 않고 캐시만 사용한다.
- **오래됨(stale)**: 60~86,460초. 캐시를 **즉시 반환하면서 동시에** 백그라운드에서 새 데이터를 요청한다.
- **썩음(rotten)**: 86,460초 이후. 캐시를 완전히 버리고 서버에서 새로 받는다.

```
[0초]   /api/posts 요청 → 200 OK, 캐시 저장(60초간 신선)
[30초]  /api/posts 요청 → 캐시 신선 → 캐시 반환 (서버 요청 없음)
[70초]  /api/posts 요청 → 캐시 오래됨(SWR 이내)
                        → 오래된 캐시 즉시 반환 ✅
                        → 동시에 백그라운드 재검증 시작 → 200 OK → 캐시 업데이트
[80초]  /api/posts 요청 → 업데이트된 신선한 캐시 → 최신 데이터 반환
```

세 전략을 비교하면 차이가 명확하다.

| 전략 | 첫 요청 | 30초 후 | 70초 후 | 특성 |
|---|---|---|---|---|
| `no-cache` | 느림 | 느림(304 왕복) | 느림(왕복) | 항상 최신, 항상 느림 |
| `max-age=86400` | 느림 | 빠름 | 빠름 | 빠르지만 24시간 동안 오래된 데이터 |
| `max-age=60, swr=86400` | 느림 | 빠름 | 빠름(+백그라운드 갱신) | 빠르고, 최대 한 번만 오래된 데이터 |

SWR의 총 유효 기간은 `max-age + stale-while-revalidate`다. 위 예시는 60 + 86,400 = 86,460초(약 24시간)다.

**서버 부하 관점**의 이득도 크다. `max-age=60`이면 60초 이내 반복 요청은 서버에 전혀 도달하지 않는다. 매초 100명이 접속해도 서버는 1분에 1~2번만 요청을 받는다.

### 3.2 데이터 특성별 설정

```ts
// 자주 변경되는 API — 1분 신선, 1시간 오래됨 허용
'Cache-Control': 'max-age=60, stale-while-revalidate=3600'

// RSS 피드(적당히 변경) — 1시간 신선, 24시간 오래됨 허용
'Cache-Control': 'max-age=3600, stale-while-revalidate=86400'

// 정적 JSON(i18n 번역 파일 등) — 1시간 신선, 1주일 오래됨 허용
'Cache-Control': 'public, max-age=3600, stale-while-revalidate=604800'
```

### 3.3 stale-if-error로 장애 대응

`stale-if-error`는 서버가 오류를 반환할 때 오래된 캐시를 사용하는 지시어다.

```http
Cache-Control: max-age=60, stale-while-revalidate=3600, stale-if-error=86400
```

- 60초 동안 신선
- 60초 이후 1시간 동안은 오래된 캐시 반환 + 백그라운드 재검증
- 서버가 5xx를 반환하면 **24시간 동안 오래된 캐시를 계속 사용**

```
[정상] 캐시 만료 → 오래된 캐시 즉시 반환 → 백그라운드 재검증 → 200 OK → 캐시 업데이트
[장애] 캐시 만료 → 오래된 캐시 즉시 반환 → 백그라운드 재검증 → 500 Error
                 → stale-if-error 이내면 캐시 유지(버리지 않음)
                 → 사용자는 정상적으로 데이터를 받음 (장애를 인지 못함)
[복구] 백그라운드 재검증 → 200 OK → 캐시 업데이트 성공
```

배포 중 서버가 재시작되거나 외부 API가 다운돼도 사용자는 서비스 중단을 인지하지 못한다.

### 3.4 SWR 사용 시 주의사항

- **빠르게 변경되는 데이터에는 부적합**: 실시간 주식 가격이나 경매 입찰가처럼 초 단위로 바뀌는 데이터는 사용자가 오래된 값을 보는 것 자체가 문제다. `no-cache`를 쓴다.
- **보안이 중요한 데이터**: 권한이 변경된 사용자가 오래된 캐시로 접근 불가능한 데이터를 보는 상황을 막아야 한다. 권한 데이터는 짧은 캐싱(`private, max-age=30`)이나 재검증을 쓴다.
- **CDN과 브라우저의 이중 SWR**: 같은 헤더를 CDN과 브라우저가 모두 적용하면 오래된 데이터가 **두 번 누적**된다. `max-age=60, swr=3600`을 양쪽이 적용하면 최악의 경우 120분 오래된 데이터를 볼 수 있다. `s-maxage`로 CDN과 브라우저를 분리하고 SWR 시간을 줄여야 한다.

  ```http
  # CDN은 짧게, 브라우저는 길게, SWR도 조절
  Cache-Control: public, max-age=300, s-maxage=60, stale-while-revalidate=600
  # CDN: 1분 신선 + 10분 오래됨 = 최대 11분
  # 브라우저: 5분 신선 + 10분 오래됨 = 최대 15분
  # → 최악 26분 (원래 120분보다 크게 개선)
  ```

- **백그라운드 업데이트 실패**: 재검증이 실패하면 다음 요청도 여전히 오래된 캐시를 쓴다. `stale-if-error`를 함께 설정한다.

브라우저가 `stale-while-revalidate`를 지원하지 않으면 이 지시어를 무시하고 `max-age`만 사용하므로 안전하게 폴백된다. 클라우드플레어·AWS 클라우드프런트·패스틀리·버셀 등 주요 CDN도 이를 지원하므로 CDN 레이어에서도 SWR이 작동해 오리진 부하를 크게 줄인다.

## 4. BFCache로 뒤로가기를 즉시 복원하기

HTTP 캐시가 리소스 파일을 저장한다면, **BFCache(*Back/Forward Cache*)는 페이지 전체를 메모리에 동결**한다. 뒤로가기를 누르면 HTML 파싱·자바스크립트 실행·렌더링을 다시 하지 않고 메모리에서 페이지 인스턴스를 즉시 복원한다. DOM 상태, 자바스크립트 변수, 스크롤 위치까지 그대로 살아 있다.

구글 연구에 따르면 크롬 데스크톱에서 전체 탐색의 약 10%, 모바일에서 약 20%가 뒤로가기 또는 앞으로가기다. DebugBear 연구 기준 BFCache의 효과는 극적이다.

- **TTFB**: 146ms → 16ms (약 89% 단축)
- **LCP**: 427ms → 100ms (약 77% 단축)

BFCache는 모든 주요 브라우저가 지원한다(크롬은 96 버전, 2021년 11월부터 데스크톱 지원). **하지만 특정 코드 패턴에 의해 쉽게 비활성화된다.** 이것이 많은 사이트가 BFCache를 활용하지 못하는 이유다.

### 4.1 작동 방식

```
1. 사용자가 페이지 A에서 링크 클릭 → 페이지 B로 이동
2. 브라우저가 페이지 A를 BFCache에 저장(메모리에 동결)
   • DOM 상태, 자바스크립트 변수, 스크롤 위치 모두 보존
   • setTimeout, setInterval 일시 정지
   • fetch, WebSocket 등 네트워크 요청 중단
3. 페이지 B 로드
4. 사용자가 뒤로가기 클릭
5. 브라우저가 페이지 A를 BFCache에서 즉시 복원 (0ms)
   • HTML 파싱 없음 / 자바스크립트 재실행 없음
   • CSS 재계산 없음 / 네트워크 요청 없음
```

HTTP 캐시와의 차이는 명확하다. HTTP 캐시는 리소스 파일만 저장하므로 HTML을 캐싱해도 브라우저는 파싱·실행·DOM 구성을 다시 한다. BFCache는 이 모든 과정을 건너뛴다.

### 4.2 BFCache를 막는 코드 패턴

가장 흔한 원인은 **`unload` 이벤트 리스너**다. `unload`는 페이지가 완전히 언로드됐다고 가정하는데 BFCache는 페이지를 메모리에 유지한다. 이 모순 때문에 브라우저는 `unload` 리스너가 있으면 BFCache를 비활성화한다.

```ts
// ❌ BFCache 비활성화됨
window.addEventListener('unload', () => {
  sendAnalytics();
});

// ✅ pagehide + persisted 플래그
window.addEventListener('pagehide', (event) => {
  if (event.persisted) {
    // BFCache에 저장될 예정
    console.log('페이지가 BFCache에 저장됩니다');
  } else {
    // 완전히 언로드됨
    sendAnalytics();
  }
});
```

크롬은 `unload` 이벤트를 단계적으로 폐기할 계획이며 개발자 도구에서 이미 경고를 표시한다.

**그 밖의 주요 차단 원인**

- 페이지 HTML 자체에 `Cache-Control: no-store`가 설정된 경우
- 완료되지 않은 `fetch` 요청 (실무에서 가장 자주 문제가 된다)
- 열린 IndexedDB 트랜잭션
- 열린 WebSocket 연결
- `beforeunload` 이벤트(일부 브라우저)

```ts
// 진행 중인 fetch 중단
const controller = new AbortController();

async function fetchData(): Promise<unknown> {
  try {
    const response = await fetch('/api/data', { signal: controller.signal });
    return await response.json();
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      console.log('요청이 중단되었습니다');
    }
  }
}

window.addEventListener('pagehide', () => {
  controller.abort();
});
```

```ts
// WebSocket 정리
const ws = new WebSocket('wss://example.com');
window.addEventListener('pagehide', () => {
  ws.close();
});
```

> **실무 팁**: 대규모 코드베이스에서 서드파티 스크립트가 `unload`를 쓰는지 일일이 확인하기 어렵다면 `Permissions-Policy: unload=()` 헤더로 `unload` 이벤트 등록 자체를 차단할 수 있다.

### 4.3 작동 여부 확인

**크롬 개발자 도구**

1. 개발자 도구 열기(F12)
2. Application 탭 → Back/forward cache 메뉴
3. 테스트할 페이지로 이동
4. 다른 페이지로 이동 후 뒤로가기
5. Back/forward cache 패널에서 결과 확인

비활성화된 경우 "Unload event listener in window"처럼 **구체적으로 어떤 API가 문제인지** 알려준다.

**자바스크립트로 확인**

```ts
window.addEventListener('pageshow', (event) => {
  if (event.persisted) {
    console.log('BFCache에서 복원됨');
    refreshRealtimeData(); // 실시간 데이터 다시 가져오기
  } else {
    console.log('일반 페이지 로드');
  }
});
```

**실사용자 환경 모니터링**

`PerformanceNavigationTiming.notRestoredReasons`로 부적격 이유를 프로그래밍 방식으로 수집할 수 있다.

```ts
window.addEventListener('pageshow', (event) => {
  if (!event.persisted) {
    const navEntry = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
    if (navEntry.notRestoredReasons) {
      sendAnalytics({
        event: 'bfcache_blocked',
        reasons: navEntry.notRestoredReasons.reasons,
        url: location.href,
      });
    }
  }
});
```

### 4.4 pageshow / pagehide 실전 활용

**복원 시 데이터 갱신**

BFCache 복원의 가장 큰 문제는 데이터가 최신이 아닐 수 있다는 점이다. 뉴스 목록 페이지로 뒤로가기 했을 때 그 사이 새 기사가 올라왔을 수 있다.

```ts
let lastFetchTime = Date.now();

window.addEventListener('pageshow', (event) => {
  if (event.persisted) {
    const elapsed = Date.now() - lastFetchTime;
    // 5분 이상 지났으면 갱신
    if (elapsed > 5 * 60 * 1000) {
      refreshArticles();
    }
  }
});

async function refreshArticles(): Promise<void> {
  const response = await fetch('/api/articles');
  const articles = await response.json();
  renderArticles(articles);
  lastFetchTime = Date.now();
}
```

**실시간 연결 재개**

채팅 앱이나 대시보드는 동결 중 멈춘 연결을 복원 시 재개해야 한다.

```ts
let socket: WebSocket | undefined;

function connectWebSocket(): void {
  socket = new WebSocket('wss://example.com/chat');
  socket.addEventListener('message', (event) => {
    displayMessage(JSON.parse(event.data));
  });
}

connectWebSocket();

window.addEventListener('pagehide', (event) => {
  if (event.persisted && socket) {
    socket.close();
  }
});

window.addEventListener('pageshow', (event) => {
  if (event.persisted) {
    connectWebSocket();
  }
});
```

**분석 데이터 전송**

`unload` 대신 `pagehide`와 `navigator.sendBeacon()`을 쓴다. `fetch()`나 `XMLHttpRequest`는 페이지가 사라지면 취소될 수 있지만 `sendBeacon()`은 브라우저가 백그라운드에서 전송을 완료한다.

```ts
window.addEventListener('pagehide', (event) => {
  const analyticsData = {
    url: location.href,
    duration: Date.now() - pageLoadTime,
    fromBfcache: event.persisted,
  };
  navigator.sendBeacon('/api/analytics', JSON.stringify(analyticsData));
});
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|---|---|---|
| HTML에 `no-store` 설정 | 뒤로가기마다 전체를 다시 받아 수백 ms 지연. BFCache도 비활성화됨 | `no-cache` 사용 |
| 민감한 데이터에 `no-cache` 사용 | 디스크에 저장되므로 공용 PC에서 캐시 폴더를 탐색하면 노출 | 금융·의료·개인 식별 정보는 `no-store` |
| 사용자별 API에 `private` 누락 | CDN이 사용자 A의 응답을 B에게 반환하는 개인정보 유출 사고 | 같은 URL에 사용자마다 다른 응답이면 무조건 `private` |
| `Cache-Control` 헤더 자체를 생략 | 일부 CDN이 기본 캐싱 정책을 적용해 인증 API가 캐싱됨 | 모든 응답에 명시적으로 설정 |
| `Vary: Cookie` 또는 `Vary: User-Agent` | 캐시가 사용자 수만큼 파편화되어 히트율이 0%에 수렴 | `private`으로 CDN 캐싱 차단하거나 URL 자체를 분리 |
| `no-store, max-age=3600` 조합 | `no-store`가 우선하므로 `max-age`는 무시됨 | 의도에 따라 하나만 선택 |
| `private, s-maxage=3600` 조합 | `private`이 공유 캐시를 막으므로 `s-maxage`는 무의미 | `public, max-age, s-maxage` 조합 사용 |
| 웹팩에서 `[hash]` 사용 | 전체 빌드 해시라 한 파일만 바뀌어도 전 파일명이 바뀌어 캐시가 전부 무효화됨 | `[contenthash]` 사용 |
| 파일명 고정 상태로 CDN만 무효화 | 브라우저 캐시는 `max-age`가 끝날 때까지 구 버전을 사용 | 파일명 해싱 적용 |
| 로드밸런서 뒤 여러 오리진에서 ETag 불일치 | 같은 파일인데 304를 못 받고 매번 전체 전송 | 아파치 `FileETag MTime Size`, 또는 CDN을 앞에 둠 |
| 페이지 이탈 시 `fetch` 미중단 | 진행 중 요청 때문에 BFCache가 비활성화됨 | `pagehide`에서 `AbortController.abort()` |
| 실시간 데이터에 SWR 적용 | 사용자가 오래된 주가·재고를 보게 됨 | `no-cache` 또는 매우 짧은 `max-age` |
| CDN·브라우저 양쪽에 같은 SWR 헤더 | 오래됨 기간이 누적되어 최악 2배로 늘어남 | `s-maxage`로 분리하고 SWR 시간 축소 |

## 측정과 검증

**CDN 캐시 상태 헤더**

CDN은 일반적으로 다음 상태를 제공한다.

- **HIT**: CDN 캐시에서 반환됨(가장 이상적)
- **MISS**: 캐시에 없어 오리진에서 새로 가져옴
- **EXPIRED**: 캐시가 만료되어 오리진에 재검증 요청
- **STALE**: 만료된 캐시지만 `stale-while-revalidate` 등으로 제공됨
- **BYPASS**: `private` 또는 `no-store`로 캐싱 우회
- **REVALIDATED**: 재검증 후 304로 기존 캐시 재사용

헤더 이름은 CDN마다 다르다(`x-cache`, `cf-cache-status`, `x-vercel-cache` 등). 표준 헤더인 `Age`는 CDN에 캐싱된 시간(초)을 나타낸다.

```http
HTTP/1.1 200 OK
Date: Mon, 10 Nov 2025 12:00:00 GMT
Cache-Control: public, max-age=3600
Age: 1200
```

`Date`(오리진 응답 생성 12:00) + `max-age=3600`(1시간 유효) + `Age: 1200`(20분 전 캐싱) → 남은 유효 시간은 2,400초(40분)다.

**커맨드라인 확인**

```bash
# 단일 리소스
curl -I https://example.com/app.js | grep -i cache
# cache-control: public, max-age=31536000, immutable
# x-cache: HIT
# age: 3600

# 여러 리소스를 한 번에
for url in \
  https://example.com/app.js \
  https://example.com/styles.css \
  https://example.com/logo.png
do
  echo "=== $url ==="
  curl -sI "$url" | grep -iE '(cache-control|x-cache|age):'
  echo ""
done
```

**브라우저에서 확인**

Network 탭 → 리소스 클릭 → Headers 탭 → Response Headers에서 `cf-cache-status`, `x-cache`, `age` 확인. Size 칼럼에 `(disk cache)` 또는 `(memory cache)`가 표시되면 브라우저 캐시에서 온 것이며 이 경우 CDN 상태 헤더는 보이지 않는다(네트워크 요청 자체가 없었기 때문). 정확한 CDN 동작을 보려면 Network 탭의 "Disable cache"를 체크한 뒤 테스트한다.

**캐시 히트율 모니터링**

정적 리소스가 많은 사이트는 **80% 이상**을 목표로 한다. 50% 미만이면 다음을 점검한다.

- `Cache-Control` 헤더가 제대로 설정돼 있는가?
- 쿼리스트링이나 쿠키로 캐시 키가 불필요하게 분리되고 있지 않은가?
- 사용자별 개인화 콘텐츠를 CDN에서 캐싱하려 하고 있지 않은가?

**BFCache 검증**

크롬 개발자 도구의 Application → Back/forward cache 패널에서 활성화 여부와 차단 사유를 확인하고, `notRestoredReasons`를 RUM으로 수집해 실사용자 환경을 모니터링한다.

## 체크리스트

**Cache-Control 헤더 설정**

- [ ] HTML 파일: `Cache-Control: no-cache`로 매번 재검증되는지 확인
- [ ] 정적 리소스(JS, CSS, 이미지): 파일명 해시가 있으면 `public, max-age=31536000` 적용
- [ ] API 응답: 데이터 특성에 맞는 `max-age` 설정(자주 안 바뀌면 300초 이상 고려)
- [ ] CDN 사용 시: `s-maxage`를 추가해 CDN과 브라우저 캐시를 분리(예: `max-age=60, s-maxage=3600`)
- [ ] 사용자별 데이터: `private` 지시어로 CDN·공유 프락시 캐싱 차단
- [ ] `Vary` 헤더: `Accept-Encoding`(압축), `Accept`(콘텐츠 협상) 등 응답이 달라지는 요청 헤더 추가
- [ ] ETag 활성화: 웹 서버나 프레임워크에서 자동 생성되는지 확인
- [ ] `stale-while-revalidate` 적용: 자주 안 바뀌는 API에 추가해 백그라운드 업데이트 활성화
- [ ] `stale-if-error` 적용: 장애 대응이 중요한 서비스에 `stale-if-error=86400` 고려

**파일명 해싱**

- [ ] 빌드 도구 설정: 웹팩·비트·Next.js에서 `[contenthash]`가 파일명에 포함되는지 확인
- [ ] 해시 길이: 최소 8자 이상 사용해 충돌 가능성 낮춤(예: `app.a1b2c3d4.js`)
- [ ] 모든 정적 리소스: JS·CSS뿐 아니라 이미지·폰트에도 해싱 적용
- [ ] CDN 캐시 무효화: 파일명 해싱이 제대로 돼 있으면 배포 시 무효화가 불필요한지 확인
- [ ] HTML 내 참조: 빌드 도구가 해시 파일명을 자동으로 주입하는지 검증
- [ ] 동적 임포트: 코드 스플리팅 청크 파일에도 해시가 적용되는지 확인

**BFCache 최적화**

- [ ] `unload` 이벤트 제거: `window.addEventListener('unload', ...)`를 `pagehide`로 변경
- [ ] `Permissions-Policy: unload=()` 헤더 고려(서드파티의 `unload` 사용 차단)
- [ ] `beforeunload` 최소화: 꼭 필요한 경우(폼 작성 중 등)만 유지
- [ ] 페치 요청 중단: 페이지를 떠날 때 `AbortController`로 진행 중인 요청 명시적 중단
- [ ] 웹소켓 정리: `pagehide`에서 닫고 `pageshow`에서 재연결
- [ ] IndexedDB 트랜잭션 관리: 제때 커밋하거나 중단해 열린 상태로 남지 않게 함
- [ ] 페이지 HTML 자체에 `Cache-Control: no-store`가 설정돼 있지 않은지 확인
- [ ] BFCache 테스트: Application → Back/forward cache 패널에서 활성화 확인
- [ ] `notRestoredReasons` 모니터링으로 실사용자 환경의 부적격 이유 수집
- [ ] `pageshow`의 `event.persisted`를 확인해 복원 시 필요한 데이터 갱신
- [ ] 세션 종료 분석은 `visibilitychange`(hidden)에서 `navigator.sendBeacon()`으로 전송하고 `pagehide`는 보조 폴백으로 사용

## 요약

- 캐시는 켜고 끄는 스위치가 아니라 **빌드 파이프라인·배포 프로세스와 함께 설계해야 하는 시스템**이다.
- 캐시는 브라우저(프라이빗) → 프락시 → CDN(공유) → 오리진의 **독립적인 레이어**로 구성된다. 각 레이어가 서로 다른 지시어를 따르므로 레이어 구조를 알아야 지시어가 이해된다.
- `no-cache`는 "캐시하지 마라"가 아니라 **"캐시하되 매번 재검증하라"**다. `no-store`만이 실제로 저장을 막는다.
- `max-age`는 모든 캐시, `s-maxage`는 공유 캐시 전용이다. **CDN은 길게(무효화 가능) + 브라우저는 짧게(무효화 불가)**가 실전 패턴이다.
- `private` 누락은 CDN이 사용자 A의 응답을 B에게 반환하는 **보안 사고**로 직결된다. 같은 URL에 사용자마다 다른 응답을 준다면 무조건 `private`이다.
- ETag는 콘텐츠 기반이라 정확하지만 해시 계산 비용이 있고, `Last-Modified`는 빠르지만 1초 해상도 한계가 있다. 브라우저는 ETag를 우선한다.
- `Vary`는 캐시 키를 제어한다. `Accept-Encoding`은 안전하지만 `Cookie`·`User-Agent`는 캐시를 파편화시켜 CDN을 무력화한다. **가능하면 URL 구조로 해결한다.**
- 파일명 해싱은 "1년 캐싱 + 배포 즉시 반영"이라는 모순을 해결한다. **HTML은 `no-cache`, 해시 파일은 `max-age=31536000`**이 핵심 조합이다. 웹팩은 `[hash]`가 아니라 `[contenthash]`를 써야 한다.
- SWR(`stale-while-revalidate`)은 오래된 캐시를 즉시 반환하면서 백그라운드에서 갱신한다. `stale-if-error`를 함께 쓰면 서버 장애 중에도 서비스가 이어진다. 단 실시간·보안 데이터에는 부적합하다.
- BFCache는 페이지 전체를 메모리에 동결해 뒤로가기를 0ms로 만든다(TTFB 89%, LCP 77% 단축). HTTP 캐시와 달리 **헤더가 아니라 코드 패턴**으로 제어하며, `unload` 리스너·미완료 `fetch`·열린 WebSocket이 주요 차단 원인이다.

## 다른 챕터와의 관계

- **Ch1(네트워크 최적화)**: `Cache-Control` 지시어를 간단히 소개했고, 파일명 해싱 + 긴 `max-age`라는 CDN 설정 3단계를 제시했다. 이 장은 그 각각을 깊이 파고든다.
- **Ch2(네트워크 압축)**: 압축한 응답의 캐시 키를 `Vary: Accept-Encoding`으로 분리하는 이유가 이 장의 1.7절에서 완결된다.
- **Ch10(코드 스플리팅)**: 동적 임포트로 생성된 청크에도 해시가 적용돼야 안전한 장기 캐싱이 성립한다.
- **Ch11(서버로 로직 이동)**: 이 장의 엣지 워커 캐시 키 조작 예시가 서버·엣지 역할 분담 논의로 이어진다.
- **Ch17(데이터 캐싱과 낙관적 업데이트)**: HTTP 레벨 SWR을 클라이언트 사이드로 확장한 것이 SWR·리액트 쿼리 라이브러리다. 서버 상태와 클라이언트 상태의 구분을 다룬다.
- **Ch25(차세대 웹 표준)**: Speculation Rules API로 프리렌더링을 제어하는 기법은 BFCache와 함께 "탐색을 즉시 만드는" 전략의 양 축이다.
