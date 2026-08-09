# Chapter 25: 차세대 웹 표준으로 성능을 한 단계 더 개선하라

## 핵심 질문

네트워크·번들·렌더링을 다 최적화해도 남는 문제들 - 페이지 전환 깜빡임, 클릭 후 흰 화면, "어딘가 느린데 어디인지 모름" - 을 2023~2024년에 구현된 차세대 표준이 정면으로 푼다: **View Transitions**(부드러운 전환), **Speculation Rules**(클릭 전 프리렌더링), **LoAF**(INP 원인 코드 특정), **공유 압축 사전**(델타 전송). 공통점은 **미지원 브라우저에서 에러 없이 무시된다**는 것 - 점진적 향상의 이상적 대상이다. 판단 기준은 "새롭다"가 아니라 "실제로 UX를 개선하고 안정적으로 운영 가능한가"다.

## 1. View Transitions API - 부드러운 페이지 전환

### 1.1 작동 원리

SPA 프레임워크 없이도 브라우저가 전환 애니메이션을 처리한다. 3단계: ① 현재 페이지의 시각적 **스냅샷 캡처** → ② 콜백에서 DOM 업데이트(렌더링 억제) → ③ 이전/새 스냅샷을 CSS 애니메이션으로 연결(기본 크로스페이드).

```ts
function toggleTheme() {
  if (!document.startViewTransition) { // 기능 감지 필수
    updateTheme();
    return;
  }
  document.startViewTransition(() => {
    updateTheme();
  });
}
```

- **`view-transition-name`**: 같은 이름의 요소끼리 브라우저가 매칭해 크기·위치·투명도를 보간(목록 섬네일 → 상세 큰 이미지 확대 효과). **페이지 내에서 고유해야 한다** - 중복이면 전환 실패.
- 내부적으로 가짜 요소 트리(`::view-transition-group/image-pair/old/new`)가 생성되며 CSS로 커스터마이징 가능(`root` = 이름 없는 요소 전체의 기본 전환 - 슬라이드 등으로 교체 가능).
- 지원(2025-11): 같은 문서(SPA) 크롬 111+·사파리 18+·파이어폭스 144+(**Baseline Newly available**, ~88.7%), 교차 문서(MPA) 크롬 126+·사파리 18.2+(파이어폭스 미지원, ~85%).

### 1.2 MPA - 교차 문서 전환

양쪽 페이지 모두 CSS `@view-transition { navigation: auto }`를 선언하면 일반 링크 이동에 전환이 적용된다(사용자 시작 내비게이션만 - 새로고침·주소창 입력 제외). **같은 출처(same-origin)만** 가능.

목록의 여러 카드가 같은 이름을 가질 수 없는 문제 → 클릭한 카드 정보를 sessionStorage에 저장하고, 새 페이지의 **`pagereveal` 이벤트**(첫 렌더링 직전, `e.viewTransition` 접근 가능)에서 해당 요소에만 동적으로 이름을 부여 → `finished` 후 정리. 이전 페이지 쪽은 **`pageswap`**(마지막 프레임 직전).

### 1.3 SPA - 라우터 통합

라우터 내비게이션을 `startViewTransition`으로 감싼다. **리액트의 함정**: 상태 업데이트가 비동기라 콜백 안에서 DOM이 즉시 바뀌지 않는다 → **`flushSync`로 동기화**(남용 금지, 뷰 트랜지션처럼 꼭 필요한 곳만). Next.js도 `router.push`를 같은 패턴으로. 목록→상세에서는 **클릭한 카드에만** 전환 이름을 부여(상태로 selectedId 관리)한다.

### 1.4 성능 고려와 폴백

- 스냅샷 캡처는 메모리·렌더링 비용 - **전환 범위를 제한**(핵심 요소만 이름 부여, 나머지는 기본 크로스페이드).
- 지속 시간 150~250ms(머티리얼 가이드 데스크톱 150~200ms).
- 폴백 3종 세트: **기능 감지** + **`prefers-reduced-motion` 존중**(접근성) + **데이터 프리페치 후 전환 시작**(전환은 네트워크를 기다려주지 않는다).

> **핵심 통찰**: 뷰 트랜지션의 목적은 "멋진 효과"가 아니라 **사용자에게 방향성과 맥락을 제공해 로딩이 실제보다 짧게 느껴지게** 하는 것이다. 없어도 동작에는 지장이 없다 - 점진적 향상의 교과서.

## 2. Speculation Rules API - 프리렌더링 제어

### 2.1 기존 방식의 한계와 실전 성과

`<link rel="prefetch">`는 리소스 다운로드만(파싱·실행·렌더링 X), `<link rel="prerender">`는 브라우저 지원이 불일치(크롬은 NoState Prefetch로 축소)하고 제어가 불가능했다. Speculation Rules는 **JSON 선언으로 무엇을·언제** 프리페치/프리렌더링할지 제어한다.

- 실측: 구글 검색이 2024년 적용해 FCP 7.6ms·LCP 9.5ms(중앙값) 개선. **쇼피파이**(2025-06 전체 플랫폼), **워드프레스 6.8**(2025-03 코어 통합) - 사이트 코드 수정 없이 자동 적용.
- 지원: 크롬 109+(문서 규칙·eagerness는 121+)·엣지(~81%). 사파리·파이어폭스는 미지원이지만 **script 태그를 조용히 무시** - 우아한 성능 저하.

### 2.2 문법

```html
<script type="speculationrules">
{
  "prefetch": [{ "urls": ["/blog", "/about"] }],
  "prerender": [
    {
      "where": {
        "and": [
          { "href_matches": "/products/*" },
          { "not": { "href_matches": "*logout*" } }
        ]
      },
      "eagerness": "moderate"
    }
  ]
}
</script>
```

- **prefetch**: 다음 문서의 HTML만 미리(하위 리소스 X). **prerender**: 완전 렌더링(파싱·CSS·JS·이미지) - 클릭 시 즉시 활성화, **FCP·LCP가 거의 0**.
- **URL 리스트** 방식(아는 URL 나열) + **문서 규칙**(`where`: `href_matches` glob 패턴 / `selector_matches` CSS 선택자 / `and`·`or`·`not` 조합). **same-origin만.**

### 2.3 eagerness - 이동 확률에 맞춘 시점 제어

| 레벨 | 시점 | 적합 상황 |
|---|---|---|
| `immediate` | 발견 즉시(urls 리스트) | 이동 확률 90%+(장바구니→결제, 단계별 가입) |
| `eager` | 즉시(문서 규칙 링크) | 메인 내비게이션·헤더 - 범위는 좁게 |
| `moderate` | 200ms 호버/터치 | 상품 목록·블로그 목록 - **대부분의 최선** |
| `conservative` | mousedown/터치 시작 | 검색 결과·무한 스크롤(선택지 수십 개) - 클릭~로드 사이 50~100ms 활용 |

### 2.4 조건부 전략

1. **행동 데이터 기반**: 80%가 이동하는 페이지는 eager/immediate.
2. **리소스 제약 체크 후 동적 삽입**: 배터리 20% 미만(비충전)·2G/saveData·저메모리면 규칙을 추가하지 않는다.
3. **제외 패턴 필수**: logout·delete·checkout/complete 등 **부작용 있는 URL은 절대 프리렌더링 금지**(백그라운드 렌더링이 의도치 않은 동작 실행). `rel="nofollow"`·외부 링크도 제외.
4. **계층적 조합**: 결제 immediate > 내비 eager > 상품 moderate > 블로그 conservative prefetch.

### 2.5 측정과 디버깅

- `document.prerendering`(현재 프리렌더링 중인지), `prerenderingchange` 이벤트(활성화 시점). 프리렌더링 중엔 일부 API(Web Audio·Notification 등)가 활성화까지 지연된다.
- **`activationStart > 0`** 이면 프리렌더링된 페이지 - LCP는 `startTime - activationStart`로 사용자 기준 보정(대개 <50ms).
- DevTools Application 탭 → Speculative loads에서 규칙·상태 확인.
- **A/B 테스트**로 검증: 실험군/대조군의 FCP·LCP·바운스·전환율 비교. 잘못 쓰면 대역폭·서버 부하만 늘린다.

## 3. Long Animation Frames API - INP 디버깅

### 3.1 Long Tasks의 한계를 넘는 프레임 단위 측정

Long Tasks API는 "50ms+ 작업"만 알려준다 - 40ms(핸들러)+30ms(렌더링)+25ms(레이아웃)가 연속돼 **사용자는 95ms 블로킹을 겪어도 감지하지 못하고**, 어떤 함수가 원인인지도 모른다. LoAF(크롬 123+, 2024-03 정식, ~75.9%)는 **프레임 단위**로 50ms+ 프레임의 완전한 타임라인을 준다.

핵심 필드: `duration`(프레임 전체), **`blockingDuration`**(50ms 초과분 누적 - 실제 블로킹), `renderStart`·`styleAndLayoutStart`, **`firstUIEventTimestamp`**(>0이면 사용자 입력이 있던 프레임 = INP 관련).

**`scripts[]`가 백미**: `invoker`("BUTTON#search.onclick"), `sourceURL`·`sourceFunctionName`·`sourceCharPosition`(코드 위치), `duration`, **`forcedStyleAndLayoutDuration`**(강제 리플로우 시간!), `pauseDuration`(alert·동기 XHR).

### 3.2 수집과 INP 연결

```ts
const observer = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    if (entry.firstUIEventTimestamp > 0 && entry.blockingDuration > 100) {
      // 느린 인터랙션 프레임 - scripts에서 원인 특정
    }
  }
});
observer.observe({ type: 'long-animation-frame', buffered: true });
```

- `PerformanceObserver.supportedEntryTypes.includes('long-animation-frame')`으로 기능 감지.
- blockingDuration 상위 10개를 유지하다 `pagehide`에서 sendBeacon 전송.
- **web-vitals v4부터 `onINP`의 `attribution.longAnimationFrameEntries`에 자동 포함** - INP와 LoAF 연결이 공짜. 직접 연결은 `firstUIEventTimestamp ≈ event.startTime`(10ms 오차) 매칭.

### 3.3 실전 워크플로

INP 600ms 사례: LoAF 분석 → `handleSearch` 450ms(그중 강제 리플로우 120ms) + 리액트 렌더링 95ms → 처방: 레이아웃 속성 접근 제거 + `scheduler.yield()` 분할 + 렌더링 최적화 → 180ms.

6단계: ① 문제 확인(INP 측정) → ② LoAF 수집(개발은 콘솔, 프로덕션은 전송) → ③ DevTools Performance(CPU 4x)로 프레임 확인 → ④ scripts 정렬로 병목 함수 특정 → ⑤ 수정(yield 분할/리플로우 제거/메모이제이션/워커) → ⑥ 재측정.

프로덕션 주의: 샘플링(10~20%), blockingDuration 200ms+만 추적. 크롬 사용자 데이터로 찾은 느린 코드를 고치면 **모든 브라우저가 혜택**을 받는다.

## 4. 공유 압축 사전 - 델타 전송으로 압축률 극대화

### 4.1 문제와 원리

리액트 18.2.0→18.3.0 업데이트 - 코드 90%+가 동일한데 브라우저는 완전히 새 파일로 취급해 전체를 다시 받는다. 브로틀리·Gzip·Zstandard는 **파일 내부의 반복 패턴만** 활용하고, 파일 간 유사성은 모른다.

공유 압축 사전(Compression Dictionary Transport, 크롬 130+ 2024-10, 파이어폭스·사파리 미지원)은 **이전 파일을 사전으로 지정해 새 파일은 차이(delta)만 전송**한다.

흐름 3단계:

1. **사전 지정**: 응답에 `Use-As-Dictionary: match="/app.*.js"`(URLPattern) - 브라우저가 SHA-256 해시와 함께 별도 저장.
2. **사전 알림**: 재방문 시 요청에 `Available-Dictionary: :해시:` + `Accept-Encoding: br, dcb, zstd, dcz`(dcb = Dictionary-Compressed Brotli).
3. **델타 전송**: 서버가 사전 기반 압축 응답 - `Content-Encoding: dcb` + **`Vary: Accept-Encoding, Available-Dictionary`**(중간 캐시 오염 방지). 브라우저가 사전과 결합해 원본 복원.

두 유형: **정적 사전**(이전 버전 파일 그대로 - 라이브러리 업데이트용, 구현 간단) / **동적 사전**(여러 페이지의 공통 템플릿을 별도 파일로 - `Link: <...>; rel="compression-dictionary"`, 뉴스 사이트의 헤더·푸터). 델타 파일은 빌드 단계에서 생성(`brotli --dictionary=v1.js`, 레벨 5+ 권장).

### 4.2 실측 효과

| 사례 | 일반 브로틀리 | 사전 기반 | 효과 |
|---|---|---|---|
| 앵귤러 1.7.9→1.8.3 | ~53KiB | **~4KiB** | 98%+ 압축(4G에서 200ms→30ms) |
| 부트스트랩 5.2.3→5.3.3(q11) | 22.7KB | 6.1KB | 추가 73% 감소 |
| 리액트+비트 앱 v1→v2(실측) | 52.7KB | 8.4KB | 추가 84% 감소 |
| 구글 검색 HTML(동적 사전) | - | 평균 23%↓(107→60KiB 사례) | LCP 평균 1.7%, 고지연 9% 개선 |

### 4.3 제약과 적합성

- **same-origin만**(CORS 명시 없이는), **HTTPS 필수**, 사전 크기 ~1MB 제한, 캐시 파티셔닝(사이트 간 추적 방지), **사전에 민감 데이터 금지**(전송·캐싱되므로).
- 적합: 정기 업데이트 서비스·장기 캐시·유사 템플릿 페이지(뉴스·커머스)·저대역폭 시장. 부적합: 정적 사이트·매번 다른 콘텐츠·일회성 방문자.
- 클라이언트 기능 감지 불필요 - 미지원 브라우저는 Available-Dictionary를 안 보내므로 서버가 일반 압축을 제공. 완벽한 점진적 향상.

## 5. 새로운 표준 도입 시 판단 기준

### 5.1 정보 소스 3종 조합

- **Can I use**: 브라우저 버전별 지원 + 전 세계 사용자 비율. 감각: **80%+ 지원이면 점진적 향상으로 도입 고려, 50% 이하면 폴리필/대안**. Notes(플래그 필요 등)를 꼭 읽는다.
- **Baseline**(web.dev): "지금 프로덕션에 도입해도 되는가"에 답한다 - **Newly available** = 크롬·파이어폭스·사파리 모두 지원 시작(점진적 향상 전제로 도입 가능), **Widely available** = +30개월 경과(폴백 최소화하고 기본 사용 가능).
- **MDN**: 속성·옵션 단위의 가장 상세한 호환성 + Baseline 배지 연동. 세부 검토용.

실전 순서: Can I use로 범위 파악 → Baseline으로 도입 시점 판단 → MDN으로 세부(예: 뷰 트랜지션 - 같은 문서만 우선 도입, 교차 문서는 크롬 126+ 확인).

### 5.2 폴리필 vs 점진적 향상

| | 폴리필 | 점진적 향상 |
|---|---|---|
| 적합 | **필수 기능**, 작음(10KB↓), 신뢰 가능한 공식 구현, 완전 재현 가능 | **개선 기능**(성능·UX), 폴백이 자연스러움, 감지 간단, 확산 중 |
| 예 | Promise, fetch, Object.assign | 뷰 트랜지션, 추측 규칙, 압축 사전 |
| 비용 | 번들 증가(core-js 전체 ~150KB), JS 실행 오버헤드, **렌더링 엔진 기능은 재현 불가** | 사용자 간 경험 차이, 두 경로 테스트, 감지 로직 복잡화 가능 |

**하이브리드**: 기능 감지 후 필요한 브라우저에만 동적 import로 폴리필 로드(`if (!('IntersectionObserver' in window)) await import('intersection-observer')`) - 최신 브라우저는 비용 0, 구형은 동작 보장.

### 5.3 오리진 트라이얼 - 실험 기능의 안전한 테스트

크롬의 실험 프로그램: 도메인별 토큰(meta 태그/HTTP `Origin-Trial` 헤더/JS 동적 - 헤더가 가장 안정적)으로 특정 오리진에서만 실험 기능 활성화. 특징: 기간 제한(6~12개월), **사용량 0.5% 초과 시 전체 자동 비활성화**(생태계 의존 방지), API 변경 가능. 유형: 일반/서드파티/폐기(Deprecation - 제거 예정 기능의 마이그레이션 유예).

주의: **핵심 기능을 의존시키지 말 것**(언제든 중단 가능 - 폴백 필수), 토큰 만료 관리, 대규모 트래픽은 A/B로 일부만, 피드백 제공(표준에 영향).

### 5.4 표준화 단계와 도입 타이밍

W3C: **WD**(Working Draft - 초기, 사양 급변 가능, 프로덕션 위험) → **CR**(Candidate - 구현 수집 단계, Baseline Newly면 점진적 향상 가능) → **PR**(Proposed - 사실상 표준) → **Recommendation**(안정, 장기 지원). WHATWG는 **Living Standard**(버전 없음) - "안정" 판단은 브라우저 구현 + Baseline으로, 참조는 Review Draft로.

| 판단 | 조건 | 예 |
|---|---|---|
| 즉시 도입 | Rec/PR + Widely available + 2년+ 지원 | Promise, fetch, IntersectionObserver |
| 점진적 향상 | CR + Newly available + 2개+ 브라우저 | 뷰 트랜지션, Popover, Intl.DurationFormat |
| 제한적 테스트 | WD / 오리진 트라이얼 | 새 추측 규칙 옵션, 실험적 CSS |
| 보류 | Editor's Draft / 단일 브라우저 | 제안 단계 API |

> **핵심 통찰**: 표준화 단계는 **사양의 안정성**, 브라우저 지원은 **실사용 가능성** - 별개의 지표라 둘 다 확인해야 한다. 그리고 판단 질문 4가지: 필수인가? 폴백 가능한가? 유지보수 리소스가 있는가? UX 영향이 실제로 있는가?

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|---|---|---|
| startViewTransition 기능 감지 생략 | 미지원 브라우저에서 에러 | 감지 후 폴백(콜백 직접 실행) |
| 여러 요소에 같은 view-transition-name | 전환 실패 | 클릭 요소에만 동적 부여(+pagereveal) |
| 리액트에서 flushSync 없이 전환 | 비동기 업데이트로 스냅샷 타이밍 어긋남 | startViewTransition 안에서 flushSync |
| prefers-reduced-motion 무시 | 접근성 위반 - 어지럼증 유발 가능 | 미디어 쿼리 확인 후 스킵 |
| 전체 페이지에 무거운 전환 | 스냅샷 메모리 + 저사양 버벅임 | 핵심 요소만 이름 부여, 150~250ms |
| logout/delete URL 프리렌더링 | 백그라운드에서 부작용 실행 | 제외 패턴 필수(not href_matches) |
| 모든 링크 immediate 프리렌더링 | 대역폭·서버 부하 낭비(10개 중 1개만 클릭) | eagerness를 이동 확률에 맞춤(대부분 moderate) |
| 저사양·데이터 절약 무시한 추측 규칙 | 배터리·요금 낭비 | 배터리/2G/saveData 체크 후 동적 삽입 |
| 프리렌더 페이지의 LCP 그대로 해석 | activationStart 보정 없이는 과대평가 | startTime - activationStart |
| Long Tasks만으로 INP 디버깅 | 연속 짧은 작업(95ms 블로킹) 미감지, 원인 함수 불명 | LoAF의 blockingDuration + scripts |
| LoAF 전수 수집 | 측정 자체가 성능 영향 + 데이터 폭증 | 샘플링 10~20% + 200ms+만 |
| 압축 사전에 민감 데이터 포함 | 전송·캐싱되어 유출 위험 | 공통 템플릿·라이브러리 코드만 |
| Vary 헤더 없이 델타 응답 | 중간 캐시(CDN)가 잘못된 버전 제공 | Vary: Accept-Encoding, Available-Dictionary |
| 오리진 트라이얼 기능에 핵심 의존 | 기간 만료·0.5% 초과 시 갑자기 중단 | 항상 폴백 + 실험으로 취급 |
| "새로워서" 도입 | 유지보수 비용 > 개선 효과 | Can I use+Baseline+MDN 종합 판단 + 측정 |

## 측정과 검증

- **뷰 트랜지션**: 저사양에서 프레임 드롭 확인(Performance 탭), 애니메이션 오버헤드 측정, 전환 유/무 A/B로 체감·전환율 비교.
- **추측 규칙**: DevTools Speculative loads 패널, `activationStart`로 프리렌더 적중률, A/B로 FCP·LCP·바운스·전환율 + 서버 부하·대역폭 모니터링.
- **LoAF**: 개선 전후 blockingDuration 비교(예: 562ms→130ms), INP 재측정. web-vitals v4 attribution 활용.
- **압축 사전**: 델타 파일 크기 vs 일반 압축, Content-Encoding: dcb 응답 확인, 캐시 히트율.
- **도입 후 상시**: 브라우저 지원 확대 모니터링(Baseline 변화) - Newly → Widely가 되면 폴백 단순화 검토.

## 체크리스트

**뷰 트랜지션**

- [ ] Can I use로 지원 범위 확인
- [ ] startViewTransition 기능 감지 + 폴백
- [ ] SPA/MPA 방식 선택(교차 문서는 same-origin·크롬 126+)
- [ ] 전환 이름 고유성(클릭 요소만 동적 부여)
- [ ] prefers-reduced-motion 존중 + 성능 영향 측정

**추측 규칙**

- [ ] prefetch vs prerender 선택
- [ ] eagerness를 이동 확률에 맞춤
- [ ] 부작용 URL 제외 패턴(logout·delete 등)
- [ ] 리소스 제약 시 규칙 미삽입(배터리·2G·saveData)
- [ ] DevTools Speculations 확인 + A/B 검증

**LoAF**

- [ ] supportedEntryTypes 기능 감지
- [ ] INP 높은 페이지에서 LoAF 수집(buffered)
- [ ] scripts 배열로 병목 함수·강제 리플로우 특정
- [ ] 개선 후 INP·blockingDuration 재측정
- [ ] 프로덕션 샘플링 + 임곗값 필터

**공유 압축 사전**

- [ ] Use-As-Dictionary(match 패턴) 헤더 설정
- [ ] 빌드에서 델타 파일 생성(brotli --dictionary)
- [ ] Available-Dictionary 해시 검증 + dcb 응답
- [ ] Vary 헤더 필수 + HTTPS + 민감 데이터 배제

**도입 판단**

- [ ] Can I use + Baseline + MDN 종합 확인
- [ ] 폴리필 vs 점진적 향상 결정(필수성·크기·재현 가능성)
- [ ] 필요 시 오리진 트라이얼(폴백 전제)
- [ ] W3C 단계 확인(WD/CR/PR/Rec)
- [ ] 도입 후 지원 확대 지속 모니터링

## 요약

- 차세대 4종의 역할: **뷰 트랜지션** = 스냅샷 기반 전환(SPA·MPA, view-transition-name 매칭, Baseline Newly) / **추측 규칙** = JSON 선언 프리페치·프리렌더링(eagerness 4단계, FCP·LCP ~0) / **LoAF** = 프레임 단위 INP 디버깅(blockingDuration + scripts로 원인 함수·강제 리플로우 특정) / **압축 사전** = 이전 파일을 사전으로 델타만 전송(업데이트 98% 압축, 구글 검색 HTML 23%↓).
- 넷 모두 **미지원 브라우저에서 조용히 무시**된다 - 기능 감지 + 폴백이면 안전. 크롬 전용 API(추측 규칙·LoAF·사전)도 개선 효과는 전 브라우저에 미친다(LoAF로 찾은 느린 코드 수정은 사파리에서도 빨라짐).
- 함정들: 전환 이름 중복·flushSync 누락·reduced-motion 무시(뷰 트랜지션), 부작용 URL 프리렌더링·무차별 immediate(추측 규칙), 전수 수집(LoAF), 민감 데이터·Vary 누락(사전).
- **도입 판단 프레임**: Can I use(지원율 80%+?) → Baseline(Newly = 점진적 향상 / Widely = 기본 사용) → MDN(세부) + W3C 단계(WD 위험 ~ Rec 안정). 폴리필은 필수·소형·재현 가능할 때, 점진적 향상은 개선 기능일 때, 실험은 오리진 트라이얼로(핵심 의존 금지).
- 이 판단 기준 자체가 이 장의 진짜 유산이다 - 앞으로 등장할 어떤 API에도 적용된다. **최신 기술을 따르는 것이 아니라, 안정성과 개선 사이에서 합리적으로 선택하는 것**이 실력이다.

## 다른 챕터와의 관계

- **Ch4(리소스 우선순위)**: prefetch/preload의 한계에서 출발한 추측 규칙 - 리소스 힌트의 완성형이다.
- **Ch16(하이드레이션)·Ch22(컴포넌트)**: SPA 라우터와 뷰 트랜지션의 통합, flushSync 같은 프레임워크 결합 지점.
- **Ch18(자바스크립트 실행)·Ch21(애니메이션)**: LoAF는 Ch18의 긴 작업·Ch21의 프레임 예산 논의의 관측 도구 완성판 - scheduler.yield()·리플로우 제거가 처방으로 재등장한다.
- **Ch2(압축)·Ch3(캐시)**: Gzip/브로틀리/Zstandard와 Vary 헤더의 기초 위에 압축 사전이 선다 - "마지막 10%"의 최적화.
- **Ch8(폴리필)**: 조건부 폴리필 로딩 전략이 이 장의 폴리필 vs 점진적 향상 판단과 연결된다.
- **Ch26(마치며)**: 측정→판단→점진 도입이라는 이 장의 태도가 책 전체의 결론으로 이어진다.
