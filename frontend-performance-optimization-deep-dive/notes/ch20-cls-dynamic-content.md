# Chapter 20: CLS는 동적 콘텐츠를 어떻게 다루느냐의 문제다

## 핵심 질문

읽던 텍스트가 갑자기 밀려나 잘못된 링크를 누르고, 광고가 튀어나와 읽던 문단을 놓친다 — 사용자는 "느리다"가 아니라 **"불안정하다"** 고 느낀다. CLS(0.1 이하 좋음 / 0.25 이상 나쁨, 검색 순위에도 영향)를 흔히 "이미지에 width/height 붙이면 끝"으로 알지만, 실무 CLS의 주범은 **동적으로 삽입되는 콘텐츠** — 광고·서드파티 임베드·쿠키 배너·무한 스크롤이다. 크기를 미리 예약할 것인가, 어디에 배치할 것인가, 실패 시 어떻게 처리할 것인가 — 이 선택이 CLS를 결정한다.

(이미지 크기 예약은 Ch12, 폰트 로딩은 Ch14에서 이미 다뤘다. 이 장은 그 외의 실무 CLS를 다룬다.)

## 1. 광고 — CLS 최대 주범과 대응 전략

### 1.1 발생 메커니즘

광고 슬롯은 0px로 시작한다 → 비동기 스크립트 로드 → 광고 서버 RTB(Real-Time Bidding, 일반적으로 80~300ms 타임아웃) → 낙찰 크리에이티브 다운로드 → **렌더링 순간 슬롯이 300×250으로 확장되며 아래 콘텐츠 전체가 밀린다.**

광고 CLS가 유독 높은 구조적 이유 4가지:

1. **비동기 로딩의 구조적 한계**: 렌더링을 막지 않으려 항상 비동기 — 콘텐츠가 먼저 그려진 후 삽입되므로 필연적으로 시프트.
2. **가변적인 광고 크기**: 같은 슬롯에 300×250·300×600·336×280이 번갈아 오고, 반응형 광고는 뷰포트 따라 달라진다.
3. **다수의 슬롯**: 슬롯 3개가 각각 0.08이면 합계 0.24 — '나쁨' 기준 직전.
4. **예측 불가능한 타이밍**: 네트워크·입찰 경쟁에 따라 200ms~2초.

**측정**: 사후 분석은 `performance.getEntriesByType('layout-shift')`를 필터링(클래스명 'ad' 또는 IFRAME). 실시간 추적은 PerformanceObserver:

```ts
let adCLS = 0;
new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    if (!entry.hadRecentInput) { // 사용자 입력 후 500ms 이내 시프트는 CLS 미포함
      const isAdShift = entry.sources?.some((s) => s.node?.className?.includes('ad'));
      if (isAdShift) {
        adCLS += entry.value;
      }
    }
  }
}).observe({ type: 'layout-shift', buffered: true }); // 등록 전 발생분도 포함
```

### 1.2 크기 예약 — 가장 확실한 해법

광고 슬롯을 감싸는 컨테이너에 CSS로 공간을 미리 잡는다:

```css
.ad-container {
  min-height: 250px; /* 작은 광고가 와도 유지, 큰 광고면 확장 */
  width: 300px;
  background: #f5f5f5; /* 로딩 중 배경 */
}

/* 반응형 광고는 미디어 쿼리로 뷰포트별 예약 */
@media (max-width: 767px) { .ad-responsive { min-height: 250px; width: 300px; } }
@media (min-width: 768px) { .ad-responsive { min-height: 90px; width: 728px; } }
```

여러 크기가 올 수 있으면 **가장 큰 크기로 예약** — 빈 공간이 생겨도 읽던 콘텐츠가 밀리는 것보다 낫다.

### 1.3 SDK가 크기를 미리 알려주지 않을 때 — 4가지 전략

GPT의 `slotRenderEnded` 이벤트도 렌더링 **후**의 크기만 준다. 사전 정보가 없다면:

1. **과거 데이터 기반 예측**(가장 현실적): 프로덕션에서 실제 로드된 크기를 로깅 — 지난 30일간 80%가 300×250이었다면 최빈값 또는 안전하게 최대값으로 예약. 광고 집행 패턴이 바뀌므로 분기별 재검토.
2. **IAB 표준 크기**: 300×250(Medium Rectangle)·728×90(Leaderboard)·300×600(Half Page)·336×280(Large Rectangle)·970×90. 위치별 관례 — 사이드바 300×250/600, 헤더 728×90/970×90, 본문 중간 300×250.
3. **실측 후 다음 방문에 적용**: ResizeObserver로 렌더링된 높이를 측정해 localStorage 저장 → 재방문 시 그 값으로 예약. 첫 방문엔 효과가 없지만 재방문율 높은 사이트에서 유용. (`contentRect`는 레거시 — `contentBoxSize` 권장.)
4. **가장 큰 크기로 예약**: 300×600까지 올 수 있으면 항상 600px. 뉴스·콘텐츠 사이트처럼 읽기 중 시프트가 즉시 이탈로 이어지는 곳에서 특히 합리적.

### 1.4 광고 로딩 실패 시 — 3가지 전략

서버 장애·광고 차단기·입찰 실패로 예약 공간이 빈 채 남을 수 있다.

| 전략 | 방법 | 장단점 |
|---|---|---|
| 공간 유지 | 예약 공간 그대로 + `:empty::after`로 "광고" 표시 | CLS 0 보장 / 빈 공간이 어색, 스크롤 길어짐 |
| 대체 콘텐츠 | `slotRenderEnded`의 `isEmpty` 시 추천 기사·자사 광고로 교체 | 유용한 콘텐츠 제공 / **정확히 같은 크기 필수**(250px 자리에 100px 넣으면 150px CLS) |
| 조건부 축소 | IntersectionObserver로 뷰포트 진입 추적 — 진입 전 실패면 `display: none`, 진입 후면 대체 콘텐츠 | 가장 이상적(CLS는 뷰포트 내에서만 측정) / 구현 복잡, 타이밍 이슈 |

## 2. 서드파티 임베드 콘텐츠의 크기 예약

광고 다음의 CLS 주범. 광고는 표준 크기라도 있지, 임베드는 플랫폼마다 다르고 크기를 미리 알려주지 않는다.

### 2.1 플랫폼별 특성

- **유튜브**: 16:9 고정이라 가장 쉽다. 기본 임베드 코드(고정 560×315)는 CLS는 없지만 반응형이 안 되므로, 컨테이너 + `aspect-ratio`로 감싼다.
- **X(트위터)**: `<blockquote>` → widgets.js가 iframe으로 변환. **높이가 콘텐츠에 따라 달라** 예측 불가(짧은 텍스트 ~200px, 이미지 포함 600px+). `min-height: 400px` 수준의 타협 — 큰 트윗은 여전히 약간의 CLS, 작은 트윗은 빈 공간.
- **인스타그램**: 1:1 기본이지만 4:5·1.91:1도 지원, 캡션·좋아요 영역으로 높이 가변. `min-height: 700px` + `max-width: 540px` 수준으로 예약.

세 플랫폼의 공통점: 스크립트가 비동기로 로드되고 콘텐츠 렌더링 전까지 크기를 알 수 없다 — 완벽한 해법은 없고 **적절한 min-height로 대부분의 CLS를 막는 것**이 실무 답이다.

### 2.2 aspect-ratio 패턴 — 모든 iframe의 범용 기법

```css
/* 최신: aspect-ratio (2021+ 전 브라우저) */
.video-container {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9; /* 너비에 맞춰 높이 자동 계산 */
}
.video-container iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}
```

> **참고 — padding hack에서 aspect-ratio로**<br><br>과거에는 `padding-bottom: 56.25%; height: 0`이라는 padding hack을 썼다 — CSS에서 %패딩은 상하좌우 모두 **부모 너비 기준**이라 너비 비례 높이를 만들 수 있었기 때문(9÷16=56.25%). 동작은 하지만 의도가 드러나지 않는다. 구형 브라우저 지원이 필요하면 padding hack을 기본으로 두고 `@supports (aspect-ratio: 16 / 9)`에서 덮어쓴다. 다양한 비율은 CSS 변수(`aspect-ratio: var(--aspect-ratio)`)로 처리 — 구글 맵·비메오·스포티파이 등 거의 모든 iframe 임베드에 적용 가능하다.

### 2.3 파사드 패턴 — 성능과 CLS를 동시에

유튜브 iframe 하나가 **약 1.3MB의 자바스크립트**와 수십 개의 요청을 발생시킨다 — 대부분의 사용자는 재생하지도 않는데. 파사드(facade)는 섬네일+재생 버튼만 먼저 보여주고 클릭 시 실제 iframe으로 교체한다. CLS 관점의 핵심은 **플레이스홀더에 `aspect-ratio: 16/9`를 고정**하는 것 — 크기가 이미 확정되어 있어 교체 순간에도 레이아웃이 변하지 않는다. (구현 상세·lite-youtube-embed·채팅 위젯 적용은 Ch23.)

## 3. 동적 UI 요소를 CLS 없이 삽입하는 방법

원칙은 둘 중 하나다: **레이아웃 흐름에서 벗어나거나(fixed), 미리 공간을 확보하거나.**

### 3.1 쿠키 동의 배너

- **`position: fixed`로 레이아웃 밖 배치**(가장 널리 사용): 흐름에 영향을 주지 않아 언제 나타나든 CLS 0. 단점은 콘텐츠 가림 — 모바일에서 화면을 크게 차지하지 않도록 높이·닫기 버튼 배치에 신경 쓴다.
- **공간 예약**: 배너 자리를 HTML에 미리 확보(min-height). 콘텐츠를 가리지 않지만 이미 동의한 사용자에게도 빈 공간이 보인다 — SSR에서 쿠키를 읽어 **동의 안 한 사용자에게만 조건부 렌더링**하면 해결.

### 3.2 알림·토스트의 안전한 삽입 위치

`document.body.insertBefore(notification, body.firstChild)` — 상단 삽입은 최악이다. 헤더·내비·콘텐츠 전체가 밀린다.

1. **fixed + transform 애니메이션**(가장 안전): 우측 상단/하단에 고정하고 `transform: translateX()`로 슬라이드 인. **`left`/`top` 애니메이션은 레이아웃 재계산을 유발하지만 `transform`은 컴포지터 레이어에서 처리**되어 CLS 무관.
2. **페이지 하단 배치**: 사용자가 아직 보지 않은 영역(뷰포트 밖)의 시프트는 CLS에 반영되지 않는다.
3. **전용 컨테이너**: 헤더 아래 `#notification-container`를 두고 `:not(:empty) { min-height: 50px }` — 0→50px 확장의 CLS는 남지만 전체가 밀리는 것보다 작다. 결제 오류 같은 중요 알림은 이 방식으로 최대한 빨리 표시해 스크롤 전에 안정화한다.

### 3.3 무한 스크롤과 페이지네이션

**CLS 발생 구현**: 이미지 높이 예약 없이 append → 이미지 로드마다 0px→실제 크기 확장 → 스크롤 중 계속 덜컹.

**올바른 구현 3요소**:

1. **스켈레톤 UI**: 로딩 전에 실제 콘텐츠와 같은 크기의 회색 박스를 먼저 표시 — 교체돼도 레이아웃 불변.
2. **이미지 `aspect-ratio` 예약**: `<div class="post-image" style="aspect-ratio: 16/9">` + 내부 img `absolute` + `object-fit: cover` + `loading="lazy"`.
3. **IntersectionObserver**: scroll 이벤트 대신 sentinel 요소 관찰 + `rootMargin: '100px'`로 뷰포트 진입 전 선로딩.

**페이지네이션**: 전환 시 현재 컨테이너 높이를 `minHeight`로 고정 → 스켈레톤 표시 → 새 콘텐츠 로드 후 해제 + `scrollIntoView({ behavior: 'smooth' })`. 높이 유지 덕분에 교체 순간 시프트가 없다.

## 4. CSS contain으로 레이아웃 범위 제한하기

### 4.1 contain 속성

`contain`은 브라우저에 **"이 요소 내부의 변경은 외부에 영향을 주지 않는다"**고 알려 불필요한 레이아웃 재계산을 건너뛰게 한다.

- `layout`: 내부 레이아웃 변경이 외부(부모·형제)에 영향 없음
- `paint`: 자식이 요소 경계 밖에 그려지지 않음
- `size`: 요소 크기가 자식에 의해 결정되지 않음(명시적 크기 필요)
- `style`: 카운터 등 스타일 효과가 밖으로 전파되지 않음
- 단축: **`content` = layout+paint+style**(크기는 자동 — 실무에서 가장 유용), `strict` = content+size

> **핵심 통찰**: `contain: layout`은 **내부→외부 전파**를 차단할 뿐, **요소 자체의 크기 변화**로 생기는 CLS는 막지 못한다. 댓글 내용이 로드되며 늘어나는 높이는 여전히 아래 요소를 민다 — 그래서 항상 **min-height 크기 예약(또는 스켈레톤)과 병행**해야 한다. `contain`은 격리 담당, 크기 예약은 시프트 방지 담당.

실무 적용 예: 카드 그리드 `.card { contain: content; min-height: 300px; }`, 사이드바 위젯 `contain: layout; min-height: 250px;`, 접히고 펼쳐지는 댓글 스레드 `contain: layout`.

### 4.2 content-visibility — 렌더링 자체를 건너뛰기

`content-visibility: auto`는 뷰포트 밖 요소의 렌더링을 아예 생략하고 진입 시에만 렌더링한다 — 긴 페이지 초기 렌더링이 **최대 7배** 빨라진 크롬 팀 테스트가 있다. (`hidden`은 공간은 유지하며 렌더링만 생략.)

함정: 브라우저는 미렌더링 콘텐츠의 높이를 **0으로 추정**한다 — 스크롤 시 갑자기 렌더링되며 아래 콘텐츠가 밀리고 스크롤바가 계속 움직인다. 해법은 `contain-intrinsic-size`:

```css
.article-section {
  content-visibility: auto;
  contain-intrinsic-size: auto 600px; /* auto: 한 번 렌더링한 실제 크기를 기억, 600px는 첫 폴백 */
}
```

주의 3가지: ① 앵커 링크 이동 시 대상 섹션이 미렌더링이면 스크롤 위치가 어긋날 수 있다(intrinsic-size 정확도 중요) ② 구형 크롤러가 미렌더링 콘텐츠를 인덱싱 못할 수 있어 핵심 콘텐츠에는 회피 ③ 2021+ 지원, 미지원 브라우저에선 무시(점진적 향상 OK). **적합**: 긴 문서·무한 스크롤·랜딩 페이지. **부적합**: 앵커 많은 페이지, 짧은 페이지(오버헤드만).

### 4.3 CLS 측정의 세션 윈도우 방식

2021년 6월부터 CLS 계산이 바뀌었다. 이전엔 페이지 전체 수명 동안 모든 시프트를 누적해 **오래 열어둔 SPA·무한 스크롤에서 점수가 무한히 증가**하는 문제가 있었다. 현재는 **세션 윈도우** 방식:

- 세션 = 첫 시프트부터 **최대 5초**, 시프트 간 간격이 **1초 초과**면 새 세션 시작
- **가장 큰 세션의 합**이 CLS 점수

PerformanceObserver로 직접 구현하려면 세션 조건(첫 엔트리로부터 5초 이내 && 직전 엔트리로부터 1초 이내)을 확인하며 `sessionValue`를 누적하고 `clsValue = Math.max(clsValue, sessionValue)`로 갱신한다. `hadRecentInput` 엔트리는 제외한다.

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|---|---|---|
| 광고 슬롯을 0px로 시작 | 렌더링 순간 250px+ 확장 — 읽던 콘텐츠 밀림 | 컨테이너 min-height로 IAB 표준 크기 예약 |
| 여러 크기 광고 슬롯을 최빈 크기로만 예약 | 큰 광고가 오면 그만큼 CLS | 가장 큰 크기 예약(빈 공간 감수) 또는 과거 데이터 기반 |
| 광고 실패 시 대체 콘텐츠 크기 불일치 | 250px 자리에 100px → 150px CLS | 대체 콘텐츠도 정확히 같은 크기 |
| 실패 광고 슬롯을 무조건 display:none | 뷰포트 안에서 접으면 그 자체가 CLS | 뷰포트 진입 전에만 축소(IntersectionObserver) |
| 유튜브 기본 임베드 코드 그대로 | 고정 크기라 모바일에서 깨지거나, 컨테이너 없이 재조정 시 시프트 | aspect-ratio 16/9 컨테이너 + absolute iframe |
| X·인스타 임베드에 크기 예약 없음 | widgets.js 변환 시점에 높이 급변 | min-height 타협값 설정(완벽하진 않음을 인지) |
| 알림을 body 최상단에 insertBefore | 페이지 전체가 아래로 밀림 — 최대급 CLS | fixed + transform 애니메이션, 또는 전용 컨테이너 |
| 토스트 애니메이션에 left/top 사용 | 레이아웃 재계산 유발 | transform(컴포지터 처리)으로 이동 |
| 무한 스크롤에서 이미지 크기 미예약 | 로드마다 0→실제 크기 확장 — 연쇄 시프트 | 스켈레톤 + aspect-ratio + IntersectionObserver |
| contain: layout만 믿고 크기 예약 생략 | 요소 자체 크기 변화는 못 막음 | min-height/스켈레톤 병행 |
| content-visibility: auto 단독 사용 | 미렌더링 높이 0 추정 — 스크롤 시 시프트·스크롤바 요동 | contain-intrinsic-size(auto 폴백값) 필수 병행 |
| 첫 화면·앵커 대상에 content-visibility | 핵심 콘텐츠 렌더링 지연, 앵커 위치 어긋남 | 뷰포트 밖 긴 섹션에만 적용 |
| 데스크톱에서만 CLS 확인 | 모바일이 화면이 작아 시프트가 더 크고 눈에 띔 | 모바일 우선 테스트 + RUM |

## 측정과 검증

- **PerformanceObserver(layout-shift)**: `hadRecentInput` 제외 + `buffered: true`. 세션 윈도우 로직으로 실제 CLS 산출. sources로 원인 요소 특정(광고/iframe 필터).
- **Performance 패널**: Layout Shift 타임라인으로 어느 시점·어느 요소가 시프트를 만드는지 시각 확인.
- **라이트하우스**: CLS 점수 정기 측정, CI 통합으로 회귀 방지.
- **RUM**: 실사용자 CLS 추적 — 모바일이 데스크톱보다 높은 경향이므로 세그먼트 분리.
- **우선순위 접근**: 슬롯 4개 × 0.05 = 0.20이면 가장 큰 상단 광고부터 — 데이터 기반으로 개선 효과를 정량 확인.
- **목표**: 0.1 이하(좋음). 0.1~0.25면 개선 계획, 0.25+면 즉시 착수.

## 체크리스트

**광고 CLS 방지**

- [ ] 모든 광고 슬롯에 min-height 크기 예약
- [ ] IAB 표준 크기(300×250·728×90·300×600 등) 기준 설정
- [ ] 반응형 광고는 미디어 쿼리로 뷰포트별 예약
- [ ] 여러 크기 가능 슬롯은 가장 큰 크기로 예약
- [ ] 로딩 실패 시 같은 크기의 대체 콘텐츠 표시
- [ ] Performance Observer로 광고별 CLS 측정
- [ ] SDK 크기 정보 API(slotRenderEnded 등) 활용

**서드파티 임베드**

- [ ] 유튜브·비메오에 aspect-ratio 16/9 적용
- [ ] X·인스타그램에 min-height 설정
- [ ] 모든 iframe이 크기 예약된 컨테이너로 감싸져 있음
- [ ] 파사드 패턴으로 임베드 지연 로딩(Ch23)
- [ ] 서드파티 스크립트 async/defer 로드
- [ ] 사용하지 않는 임베드 제거

**동적 UI 요소**

- [ ] 쿠키 배너는 position: fixed로 레이아웃 밖 배치
- [ ] 알림·토스트는 우측 상단/하단 fixed
- [ ] 애니메이션은 transform 사용(left/top 회피)
- [ ] 페이지 상단에 동적 요소 삽입 금지
- [ ] 삽입이 필요하면 전용 컨테이너 사용

**무한 스크롤·페이지네이션**

- [ ] 스켈레톤 UI 선표시
- [ ] 이미지에 aspect-ratio 또는 명시적 크기
- [ ] IntersectionObserver + rootMargin 선로딩
- [ ] 페이지 전환 시 컨테이너 높이 유지
- [ ] 이미지 loading="lazy"

**contain·content-visibility**

- [ ] 독립 컴포넌트(카드·댓글·위젯)에 contain: content
- [ ] 광고 슬롯·사이드바에 contain: layout
- [ ] 긴 페이지 섹션에 content-visibility: auto
- [ ] contain-intrinsic-size 함께 설정
- [ ] 첫 화면 콘텐츠에는 content-visibility 회피

**측정·모니터링**

- [ ] Performance Observer 실시간 CLS 추적(hadRecentInput 제외)
- [ ] Performance 패널로 발생 지점 확인
- [ ] 라이트하우스 정기 측정 + CI 회귀 방지
- [ ] RUM으로 실사용자 CLS(모바일 우선)
- [ ] CLS 0.1 이하 목표 달성 확인

## 요약

- CLS는 "불안정함"의 지표다 — 로딩이 빨라도 화면이 흔들리면 사용자는 사이트를 신뢰하지 않는다. 실무 주범은 이미지가 아니라 **동적 삽입 콘텐츠**(광고·임베드·배너·무한 스크롤).
- 해법의 본질은 3가지뿐: **① 공간을 미리 확보하거나(크기 예약·스켈레톤) ② 레이아웃 흐름에서 벗어나거나(fixed + transform) ③ 변경 범위를 제한하거나(contain).**
- **광고**: RTB 구조상 비동기 확장이 필연 — min-height 예약(IAB 표준·과거 데이터·실측 저장·최대 크기)으로 막고, 실패 시엔 같은 크기 대체 콘텐츠 또는 뷰포트 밖 조건부 축소.
- **임베드**: 유튜브는 aspect-ratio 16/9로 완결, X·인스타는 min-height 타협. padding hack은 aspect-ratio로 대체됐다. 파사드 패턴은 1.3MB 유튜브 JS를 클릭 시점으로 미루면서 플레이스홀더 크기 고정으로 CLS도 잡는다.
- **동적 UI**: 배너·토스트는 fixed + transform(컴포지터 처리, left/top 금지). 무한 스크롤은 스켈레톤 + aspect-ratio + IntersectionObserver, 페이지네이션은 높이 유지 후 교체.
- **contain: content**는 컴포넌트 내부 변경의 외부 전파를 차단하지만 자체 크기 변화는 못 막는다 — 크기 예약과 역할 분담. **content-visibility: auto**는 초기 렌더링을 극적으로 줄이지만 반드시 `contain-intrinsic-size`와 함께(높이 0 추정 함정).
- CLS 계산은 **세션 윈도우**(최대 5초, 간격 1초, 최대 세션값) — SPA 장시간 사용에도 공정해졌다.
- 개선은 데이터 기반 우선순위로(가장 큰 시프트부터), 유지는 라이트하우스 CI + RUM으로. 그리고 기술 밖의 답도 있다 — 광고를 하나 줄이거나 배너를 작게 만드는 **디자인·비즈니스 균형**이 최선일 때도 있다.

## 다른 챕터와의 관계

- **Ch12(이미지)·Ch14(폰트)**: CLS 3대 정적 원인(이미지 크기·폰트 스왑)은 그쪽에서 완결 — 이 장은 동적 콘텐츠 편이다. 폰트 메트릭 오버라이드와 이미지 aspect-ratio가 이 장의 기법과 합쳐져 CLS 전체 그림이 된다.
- **Ch15(CSS)·Ch16(하이드레이션)**: Runtime CSS-in-JS의 하이드레이션 중 스타일 교체가 만드는 CLS, 스트리밍 SSR의 스켈레톤→콘텐츠 교체가 이 장의 크기 예약 원칙과 연결된다.
- **Ch18(자바스크립트 실행)**: IntersectionObserver로 scroll 이벤트를 대체하는 패턴이 재등장 — 성능과 CLS를 동시에 잡는다.
- **Ch21(애니메이션)**: transform이 컴포지터에서 처리되어 레이아웃을 건드리지 않는다는 원리가 다음 장의 핵심 주제로 확장된다.
- **Ch23(서드파티)**: 파사드 패턴의 상세 구현, 광고·임베드 스크립트 통제 전략이 이어진다.
