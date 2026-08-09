# Chapter 23: 서드파티 코드는 당신이 통제해야 한다

## 핵심 질문

Performance 탭에서 가장 긴 막대가 내 코드가 아니라 `googletagmanager.com`·`connect.facebook.net`이다 - HTTP Archive 기준 웹사이트 스크립트 실행 시간의 **57%가 서드파티**에서 나오고, 2024년 모바일 중앙값에서 서드파티 JS(375KB)는 퍼스트 파티(168KB)의 2배가 넘는다. 내 코드를 아무리 최적화해도 절반 이상이 통제 밖처럼 보인다. 하지만 서드파티는 제거할 수 없다(전환 추적·A/B 테스트·채팅은 비즈니스 요구다). 답은 **"서드파티라서 어쩔 수 없다"는 생각을 버리고 통제하는 것** - 내 서비스에 박힌 스크립트라면 출처가 어디든 성능 책임은 프런트엔드 개발자에게 있다.

## 1. 서드파티 영향을 정확히 측정하라

### 1.1 크롬 개발자 도구

- **Performance 탭**: Main 트랙의 긴 작업(빨간 삼각형) 클릭 → Summary에서 `Evaluate Script`/`Function Call`의 출처 도메인 확인. **Bottom-Up 탭 + Group by Domain**으로 도메인별 총 실행 시간 정렬 - "googletagmanager.com이 500ms"처럼 정량화된다.
- **Resource Timing API**: `performance.getEntriesByType('resource')`를 도메인별로 집계(요청 수·duration·전송량)해 콘솔 테이블로 - 어떤 외부 서비스가 가장 오래 걸리는지 코드로 파악.
- **Network 탭**: `-domain:내도메인` 필터 또는 More filters의 **3rd-party requests** 옵션. 워터폴에서 서드파티 병목 3패턴을 읽는다: ① **렌더 블로킹**(async/defer 없는 동기 스크립트가 파싱 차단) ② **연쇄 요청**(GTM이 GA·픽셀을 다시 로드하는 계단식) ③ **느린 서드파티 서버**(긴 TTFB - preconnect/dns-prefetch로 완화, 근본적으론 교체).

### 1.2 라이트하우스 Third-party Summary

Diagnostics의 "Reduce the impact of third-party code" - 도메인별 **메인 스레드 차단 시간**과 **전송 크기**. 차단 300ms를 넘으면 INP 직접 악영향이라 최우선 대상이다. CLI(`npx lighthouse --only-audits=third-parties-insight --output=json`)로 CI 파이프라인에 통합할 수 있다.

> **참고 - 파사드 전용 감사 항목은 폐기됨**<br><br>과거의 "Lazy load third-party resources with facades" 감사는 라이트하우스 13부터 제거됐다. 이제는 Third-party Summary에서 전송 크기가 큰 임베드(유튜브·지도·위젯)를 직접 확인하고 파사드 적용 여부를 판단한다.

### 1.3 Performance API로 RUM 모니터링

- **PerformanceObserver**(resource + longtask, `buffered: true`)로 도메인별 통계와 차단 시간(50ms 초과분 누적)을 실시간 수집하는 추적기를 만들어 분석 서비스로 전송.
- **User Timing**: 서드파티는 로드 후 **초기화**에도 시간을 쓴다 - mark/measure로 GA 초기화 시간을 재고 1초 초과 시 경고.
- **Long Animation Frames API**(크롬 123+): 50ms+ 프레임의 `entry.scripts`에서 `sourceURL` 도메인을 확인 - **어떤 서드파티가 어떤 인터랙션을 차단했는지**까지 특정된다(`forcedStyleAndLayoutDuration`으로 강제 레이아웃 유발량도).

## 2. 정말 필요한 스크립트인지 먼저 검토하라

가장 효과적인 최적화는 **아예 로드하지 않는 것**이다. 끝난 A/B 테스트 도구, 종료된 캠페인의 픽셀, 담당자 퇴사로 정체불명이 된 스크립트 - "좀비 스크립트"가 흔하다.

### 2.1 찾고, 분석하고, 점진적으로 제거

- **Coverage 탭**: 서드파티 스크립트의 미사용 코드가 50% 이상이면 제거·교체 후보.
- **제거 전 영향도 분석 3단계**: ① 스크립트가 window에 추가하는 전역 변수를 로드 전후 비교로 파악 → 코드베이스에서 사용처 검색 ② Network 탭 우클릭 **Block request domain**으로 차단 후 페이지 동작 테스트 ③ 스테이징에서 제거 후 QA(분석·광고는 무해하지만 결제·인증 SDK는 치명적).
- **점진적 제거**: 트래픽 5~10% A/B 테스트로 에러율·전환율 모니터링 → 확대. 경로별 조건부 로딩(블로그에만 댓글 위젯, 결제 페이지에만 결제 SDK - 경로 정규식/조건 함수로 등록하는 로더).

### 2.2 중복 기능 통합

- **분석 도구 중복**(GA+믹스패널+앰플리튜드...): 하나로 통합하거나 GTM으로 단일 컨테이너 관리. 어댑터 패턴의 `UnifiedAnalytics`(track/pageview/identify를 등록된 모든 제공자에 전파, 각 어댑터는 미로드 시 무시)로 직접 구현하거나 - 이 패턴을 상품화한 것이 **CDP**(Segment·RudderStack·Jitsu)다. 도구가 2~3개면 직접 구현이 합리적, 많으면 CDP.
- **소셜 SDK 제거**: 공유 버튼에 각 플랫폼 SDK(수십 KB + 초기화 차단)는 불필요 - **Web Share API**(`navigator.share`, 모바일 우선, 사용자 제스처에서만 호출 가능) + **공유 Intent URL** 폴백(`x.com/intent/tweet?url=...`, `facebook.com/sharer/sharer.php?u=...` 팝업)으로 SDK 없이 동일 기능.

## 3. 지연 로딩으로 초기 로드를 줄여라

지연 로딩은 `defer` 한 줄이 아니라 **"언제 로드할지"의 전략적 결정**이다. 기능을 제거하는 게 아니라 타이밍만 조정한다.

### 3.1 시점별 전략

| 시점 | 대상 | 구현 |
|---|---|---|
| `load` 이벤트 후 | 분석·마케팅 픽셀(렌더링 무관) | `window.addEventListener('load', ...)` + 타임아웃·에러 처리 |
| `DOMContentLoaded` | DOM을 조작하는 A/B 테스트 도구 | 파싱 완료 직후 |
| load + setTimeout(3초) | 중요도 최하(광고 픽셀) | 추가 지연 |
| **유휴 시간** | 중요도 낮은 도구 | `requestIdleCallback`(timeout 3~5초, 사파리 폴백 setTimeout) 큐 처리 |
| **인터랙션 시** | 채팅 위젯·플레이어 | 첫 클릭에 로드(로딩 중 대기·중복 방지), 이후 클릭은 즉시. 마우스 오버 200ms 프리로드로 클릭 시 지연 제거 |
| **뷰포트 진입 시** | 하단 위젯·광고·댓글 | IntersectionObserver + rootMargin 200~300px 선로딩, `data-lazy-script` 속성으로 자동화 + 로드 완료 커스텀 이벤트로 초기화 분리 |

실무에서는 이들을 **통합 로더**(afterLoad/idle/interaction/viewport 4전략 + 우선순위 + 의존성 + 에러 격리)로 조합한다: 핵심 분석은 load 후 즉시, 히트맵은 유휴 시간, 채팅은 클릭, 댓글은 뷰포트.

### 3.2 의도 기반 조건부 로딩 - 한 단계 더

모든 방문자가 채팅을 쓰지 않는다. **사용자 행동 신호를 점수화**해 임곗값을 넘긴 "진지한 사용자"에게만 로드한다:

- 신호 예: 가격/문의/데모 페이지 방문(가중치 2), 30초+ 체류(1), 75%+ 스크롤(1), 세션당 3페이지+(1), 7일 내 재방문(1)
- 점수가 임곗값(예: 3~4)에 도달하면 자동 로드 + **수동 트리거 병행**(버튼 클릭 시 즉시 로드) - 대다수 방문자의 성능은 보호하고 필요한 사용자에게는 기능 제공.

## 4. 파사드 패턴으로 체감 성능을 높여라

지연 로딩의 남은 문제: 클릭 후 로드가 끝날 때까지 **아무 일도 안 일어나는 것처럼 보인다.** 파사드의 핵심은 "지연(delay)"이 아니라 **"착각(illusion)"** - 진짜처럼 보이는 가벼운 껍데기(HTML/CSS)를 먼저 보여주고, 클릭하면 로딩 상태를 표시하며 백그라운드에서 진짜를 로드해 교체한다.

- **성능 근거**: 진짜 위젯은 수백 KB + 초기화 시 메인 스레드 수백 ms 차단. 파사드는 섬네일(20~50KB) + 초기화 0 → **LCP·TBT 직접 개선**. 클릭하지 않는 대다수 사용자에게는 비용이 아예 발생하지 않는다.
- **유튜브**: `lite-youtube-embed`(폴 아이리시) - 웹 컴포넌트(`<lite-youtube videoid="...">`)로 5KB 미만, 표준 임베드 대비 **~224배 빠른** 초기화. 섬네일 자동 + 재생 버튼, **호버 시 youtube.com·googlevideo.com에 preconnect**해 클릭 시 시작도 빠르다. 비메오는 `lite-vimeo-embed`. 부적합한 곳: 동영상이 주 콘텐츠라 재생 확률이 높은 페이지(클릭 한 번 추가가 오히려 손해).
- **소셜 공유**: Intent URL(2절)이 곧 파사드다. **채팅 위젯**: 표준 라이브러리가 없어 직접 구현 - 진짜와 똑같은 플로팅 버튼을 CSS로 만들고 클릭 시 `widget.intercom.io/...` 로드 + `Intercom('boot')`/`('show')`.
- CLS 관점(Ch20): 플레이스홀더에 aspect-ratio를 고정해 교체 시 시프트 방지.

## 5. 웹 워커로 메인 스레드를 보호하라 - 파티타운

지연 로딩·파사드를 써도 **로드된 후에는 결국 메인 스레드에서 실행**된다. 파티타운(Partytown)은 `type="text/partytown"` 스크립트를 **웹 워커에서 실행**해 메인 스레드 차단을 거의 0으로 만든다.

### 5.1 작동 원리와 설정

핵심은 **DOM 프락시**: 워커의 스크립트가 `document.querySelector()` 등을 호출하면 메인 스레드에 메시지를 보내 실제 작업을 수행하고 결과를 받아온다 - 스크립트는 자신이 메인 스레드에 있다고 착각한다.

```html
<script>
  partytown = {
    forward: ['dataLayer.push', 'gtag'], /* 메인 스레드 호출을 워커로 전달 */
    lib: '/~partytown/',
  };
</script>
<!-- 파티타운 인라인 스니펫 -->
<script type="text/partytown" async src="https://www.googletagmanager.com/gtag/js?id=G-XXXX"></script>
```

- 설치: `@qwik.dev/partytown` + 정적 파일을 `public/~partytown/`에 복사(빌드 도구별 플러그인).
- **forward가 핵심**: `dataLayer.push`·`gtag`·`fbq`·`ttq`·`clarity` 등 메인 스레드에서 불리는 전역 함수를 워커로 중계 - 다른 스크립트가 메인에서 호출해도 정상 작동.
- GTM을 옮기면 컨테이너 안의 모든 태그(GA·픽셀 등)가 함께 워커에서 실행된다.
- 리액트: `@qwik.dev/partytown/react`의 `<Partytown forward={[...]} />`(Next.js는 _document에).
- 디버그: `debug: true` + logCalls/logGetters 등으로 워커↔메인 통신 로그 확인.

**효과 실측**: 적용 전 서드파티 Evaluate Script가 메인 스레드를 ~153ms 차단(긴 작업 경고) → 적용 후 Main 트랙이 깨끗해지고 "Worker: Partytown" 트랙에서 실행. 워커 내 실행 시간 자체는 프락시 오버헤드로 오히려 길어질 수 있지만 **메인 스레드 차단은 0ms** - 사용자는 실행 중에도 자유롭게 인터랙션한다. TBT가 크게 개선된다.

### 5.2 파티타운을 쓰면 안 되는 경우

1. **동기적 DOM 조작이 필요한 스크립트**: A/B 테스트·개인화 도구는 렌더링 전에 요소를 숨기고 바꿔야 한다 - 워커 통신은 비동기라 깜빡임(flicker) 발생. 메인 스레드에 남긴다.
2. **실시간 인터랙션 추적**: 채팅 위젯·히트맵(Hotjar 등)은 클릭·스크롤을 즉시 캡처해야 하는데 워커는 이벤트 리스너를 프락시로 등록해 오버헤드가 크다 - 파사드/지연 로딩이 낫다.
3. **워커 불가 API 의존**: `alert()`·`confirm()`·`document.write()`를 쓰는 레거시 스크립트 - 적용 전 반드시 테스트.
4. **통신 오버헤드 > 이득**: 실행이 50ms 미만인데 DOM 호출이 수백 번이면 프락시 왕복이 더 비싸다 - 그냥 async/defer.

## 6. iframe 샌드박싱으로 격리하라

통제조차 못 믿을 코드(사용자 제공 콘텐츠, 미지의 광고 네트워크, 레거시 위젯)는 **격리**가 답이다.

### 6.1 iframe 격리의 원리

iframe은 별도의 **브라우징 컨텍스트** - 크로스 오리진이면 동일 출처 정책으로 DOM·쿠키·스토리지가 **양방향 자동 격리**된다. iframe 안의 스크립트는 메인 페이지의 인증 토큰에 접근할 수 없다.

- **성능 격리**: 크로미움의 Site Isolation으로 크로스 사이트 iframe이 별도 프로세스로 렌더링될 수 있다 - iframe 안의 500ms 긴 작업이 **메인 페이지의 메인 스레드를 직접 차단하지 않는다**(광고 네트워크가 iframe을 선호하는 이유). 단 CPU/GPU/네트워크 대역폭 경쟁, 크기 변경으로 인한 레이아웃 재계산 같은 **간접 영향은 남는다.**
- **통신은 postMessage**: 구조화된 복제로 데이터를 복사 전달(참조 누수 없음), 수신 측은 **`event.origin` 검증 필수**.

### 6.2 sandbox 속성 - 권한 화이트리스트

속성값 없는 `sandbox`는 거의 전부 차단(스크립트·폼·팝업·플러그인 + **고유 오리진** 취급 - 같은 도메인이라도 격리). 필요한 것만 플래그로 허용한다: `allow-scripts`, `allow-same-origin`, `allow-forms`, `allow-popups`, `allow-top-navigation` 등.

> **핵심 통찰 - allow-scripts + allow-same-origin의 함정**: 부모와 **동일 출처인 iframe**에 두 플래그를 함께 주면, iframe 스크립트가 `parent.document...removeAttribute('sandbox')`로 **자기 샌드박스를 벗어버릴 수 있다.** 신뢰할 수 없는 콘텐츠에는 둘 중 하나만 주거나 둘 다 주지 않는다.

**사용자 생성 콘텐츠 렌더링**: `iframe.srcdoc = html` + `sandbox="allow-scripts"`(same-origin 없이) - 사용자가 스크립트를 심어도 고유 오리진에 갇혀 메인 페이지 쿠키·XSS로부터 안전하다.

### 6.3 CSP와 SRI - 마지막 방어선

- **CSP**(Content-Security-Policy 헤더): `script-src 'self' https://허용도메인` - 허용 목록에 없는 스크립트는 브라우저가 차단. 인라인 스크립트는 기본 차단 + 필요 시 **nonce**(요청마다 랜덤 생성, 일치하는 태그만 실행 - XSS 주입 스크립트는 논스를 모른다). 서드파티가 쓰는 도메인을 script-src/img-src/connect-src에 전부 등록해야 한다(하나라도 빠지면 미작동 - 콘솔 에러로 확인).
- **SRI**(Subresource Integrity): `<script src integrity="sha384-..." crossorigin="anonymous">` - 다운로드한 파일의 해시가 다르면 실행 거부. CDN 해킹·중간자 변조 방어. 메이저 CDN은 해시를 제공하고, 직접 계산은 `openssl dgst -sha384 -binary | openssl base64 -A`.

### 6.4 보안 리스크 관리 원칙

- **선택 기준**: 평판·CVE 이력, SRI 지원, 정기 업데이트(1년+ 방치는 위험), 최소 권한 요구.
- **데이터 최소화**: `thirdParty.init({ user: currentUser })` 금지 - **ID만** 전달. 인증 쿠키는 HttpOnly·Secure·SameSite. 백엔드 직접 호출 대신 **프락시 경유**(검증·필터링·레이트 리밋, API 키는 서버에서).
- **정기 감사(분기별)**: 좀비 스크립트 제거, 버전·취약점 확인, 더 가벼운 대안 검토, **서드파티 인벤토리 문서화**(이름/용도/소유자/추가일/최근 검토일/대안) - 담당자가 바뀌어도 관리가 이어진다.

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|---|---|---|
| 측정 없이 "서드파티 탓" | 어떤 스크립트가 얼마나 차단하는지 모름 - 우선순위 불가 | Bottom-Up Group by Domain + Third-party Summary |
| 좀비 스크립트 방치 | 끝난 실험·캠페인 코드가 성능+보안 비용만 발생 | Coverage 확인 + 분기별 감사 + 인벤토리 |
| 무작정 제거 | 결제·인증 SDK 제거로 서비스 중단 | 전역 변수 사용처 검색 → 도메인 차단 테스트 → 스테이징 QA → 점진 제거 |
| 유사 도구 중복 로드(GA+믹스패널+…) | 같은 데이터를 위해 수백 KB 중복 | 통합·GTM·CDP 또는 어댑터 패턴 |
| 공유 버튼마다 공식 SDK | 플랫폼당 수십 KB + 초기화 차단 | Web Share API + Intent URL |
| 모든 서드파티를 페이지 로드 즉시 실행 | LCP 이미지·핵심 JS와 대역폭·스레드 경쟁 | 시점별 지연 로딩(load 후/유휴/인터랙션/뷰포트) |
| 지연 로딩만 하고 피드백 없음 | 클릭 후 수 초간 무반응 - "고장났나?" | 파사드(즉각 플레이스홀더 + 로딩 표시) |
| 유튜브 iframe 직접 임베드 | 재생 안 하는 사용자에게도 수백 KB | lite-youtube-embed(재생 확률 높은 페이지 제외) |
| A/B 테스트 도구를 파티타운으로 | 비동기 프락시로 타이밍 어긋남 - 깜빡임 | 동기 DOM 조작 스크립트는 메인 스레드에 |
| 실행 짧고 DOM 호출 많은 스크립트를 워커로 | 프락시 통신 오버헤드가 이득 초과 | async/defer 또는 지연 로딩으로 충분 |
| 동일 출처 iframe에 allow-scripts+allow-same-origin | 샌드박스 자가 해제 가능 | 신뢰 불가 콘텐츠엔 동시 부여 금지 |
| postMessage 수신 시 origin 미검증 | 악의적 페이지의 메시지 수용 | `event.origin` 화이트리스트 검증 |
| 서드파티에 전체 사용자 객체 전달 | 불필요한 개인정보 노출 | 필요한 최소(ID)만 |
| CDN 스크립트를 SRI 없이 로드 | CDN 해킹·변조 시 무방비 | integrity + crossorigin |

## 측정과 검증

- **도입 전**: 라이트하우스 Third-party Summary로 예상 영향, 스테이징에서 전후 비교.
- **최적화 후**: Performance 탭에서 메인 스레드 차단 감소(파티타운은 Worker 트랙 확인), TBT·LCP·INP 개선 확인.
- **RUM**: PerformanceObserver 추적기 + Long Animation Frames API로 실사용자 환경의 서드파티 차단 지속 수집.
- **CI**: 라이트하우스 CLI(third-parties-insight)를 파이프라인에 - 새 스크립트 추가 시 회귀 감지.
- **비즈니스 검증**: "이 위젯이 전환율을 얼마나 올리는가?" - 성능 5% 희생 대비 전환 10% 상승이면 가치 있는 트레이드오프. **측정하고, 비교하고, 결정하라.**

## 체크리스트

**측정**

- [ ] Performance 탭에서 서드파티 메인 스레드 차단 시간 확인(Bottom-Up + Group by Domain)
- [ ] 라이트하우스 Third-party Summary로 영향도 측정
- [ ] Network 탭 도메인별 전송 크기·요청 횟수 분석
- [ ] Performance API로 초기화 시간·RUM 모니터링

**제거·대체**

- [ ] Coverage 탭으로 미사용 서드파티 코드 확인
- [ ] 끝난 실험·캠페인 스크립트 제거
- [ ] 네이티브 API 대체 검토(Web Share, IntersectionObserver, Intl 등)
- [ ] 서드파티 인벤토리 문서화(용도·소유자·추가일)

**지연 로딩**

- [ ] 분석 도구는 load 후/유휴 시간 로드
- [ ] 채팅·공유 버튼은 인터랙션 시 로드(+호버 프리로드)
- [ ] 하단 위젯은 IntersectionObserver로 뷰포트 진입 시
- [ ] 의도 기반 조건부 로딩 검토(신호 점수화)

**파사드**

- [ ] 유튜브·비메오는 lite-*-embed
- [ ] 소셜 임베드·공유는 Intent URL 파사드
- [ ] 채팅 위젯은 CSS 버튼 + 클릭 로드
- [ ] 플레이스홀더 크기 고정(CLS 방지)

**웹 워커(파티타운)**

- [ ] GA·픽셀·GTM을 type="text/partytown"으로 이동
- [ ] forward 설정(dataLayer.push, gtag, fbq 등)
- [ ] Performance 탭에서 메인 스레드 차단 감소 확인
- [ ] 비호환 스크립트(동기 DOM·실시간 추적·alert류) 제외

**격리·보안**

- [ ] 신뢰 불가 콘텐츠는 iframe + sandbox(최소 플래그)
- [ ] allow-scripts+allow-same-origin 동시 부여 금지(동일 출처)
- [ ] CSP 허용 목록 + nonce
- [ ] SRI(integrity + crossorigin)로 CDN 무결성 검증
- [ ] 서드파티에 최소 데이터만 전달, API는 프락시 경유

**정기 감사**

- [ ] 분기마다 서드파티 목록 검토·제거
- [ ] 버전·취약점 업데이트 확인
- [ ] 더 가볍고 안전한 대안 검토
- [ ] RUM으로 서드파티 성능 지속 모니터링

## 요약

- 서드파티는 스크립트 실행 시간의 절반 이상을 차지하며 메인 스레드 차단·대역폭 경쟁·예측 불가 DOM 조작·외부 배포 변경 리스크를 갖는다. 제거가 아니라 **통제**가 목표다 - 6단계 전략: **측정 → 제거 → 지연 로딩 → 파사드 → 웹 워커 → 격리.**
- **측정**: Bottom-Up(Group by Domain)·Third-party Summary·Resource Timing 집계·Long Animation Frames API(원인 스크립트 특정). 측정 없이는 우선순위도 없다.
- **제거가 최고의 최적화**: Coverage로 좀비 스크립트 색출, 영향도 분석(전역 변수→차단 테스트→스테이징) 후 점진 제거. 중복 분석 도구는 통합(어댑터/GTM/CDP), 소셜 SDK는 Web Share API + Intent URL로 대체.
- **지연 로딩 = 타이밍의 전략**: load 후(분석)/유휴(저중요)/인터랙션(채팅)/뷰포트(하단 위젯)/의도 점수(진지한 사용자만). 기능은 그대로, 초기 비용만 제거.
- **파사드 = 착각의 기술**: 가벼운 껍데기 즉시 표시 → 클릭 시 로딩 피드백 + 백그라운드 로드. lite-youtube-embed는 표준 임베드보다 ~224배 빠르고, 클릭 없는 사용자에겐 비용이 0이다.
- **파티타운**: DOM 프락시로 서드파티를 웹 워커에서 실행 - 메인 스레드 차단 0ms, TBT 급감. 단 동기 DOM 조작(A/B 테스트)·실시간 추적·워커 불가 API·짧은 실행+많은 DOM 호출에는 부적합.
- **격리**: iframe(양방향 오리진 격리 + 프로세스 분리 가능) + sandbox 최소 권한(동일 출처에서 allow-scripts+allow-same-origin 동시 부여 금지) + postMessage origin 검증 + CSP(허용 목록·nonce) + SRI(무결성). 데이터는 최소만, API는 프락시로.
- 서드파티 관리는 일회성이 아니다 - 분기별 감사와 인벤토리 문서화, 그리고 궁극적으로는 **비즈니스 결정**("이 도구의 가치가 성능 비용을 넘는가?")이다.

## 다른 챕터와의 관계

- **Ch4(리소스 우선순위)·Ch6(async/defer)**: 렌더 블로킹 스크립트와 preconnect의 기초가 서드파티 워터폴 분석에 그대로 쓰인다.
- **Ch18(자바스크립트 실행)**: 긴 작업·Long Animation Frames·웹 워커의 일반론이 서드파티라는 최대 실전 사례에 적용된다. 파티타운의 부적합 판단(통신 오버헤드 vs 이득)도 Ch18의 워커 판단 기준과 같다.
- **Ch20(CLS)**: 파사드 플레이스홀더의 크기 고정, 광고 슬롯 예약이 서드파티 CLS 통제의 짝이다.
- **Ch22(컴포넌트 최적화)**: 내 코드(Ch22)를 다 최적화한 뒤 남는 절반이 이 장이다.
- **Ch9(불필요한 리소스 제거)**: Coverage 기반 제거 방법론이 퍼스트 파티에서 서드파티로 확장된다.
- **Ch24(다국어)**: "필요한 사용자에게 필요한 것만"의 원칙이 언어 리소스로 이어진다.
