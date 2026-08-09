# Chapter 13: 동영상 최적화는 전송량과 로딩 전략이 핵심이다

## 핵심 질문

동영상은 이미지보다 훨씬 무겁고, 최근에는 LCP 요소로도 측정되기 시작했다. "해상도만 줄이면 되지 않나?"를 넘어 — 어떤 코덱으로 인코딩하고, `preload`를 어떻게 설정하고, 언제 로드를 시작하며, 유튜브 임베드의 1.3MB를 어떻게 없앨 것인가?

## 1. 동영상 포맷과 코덱 선택이 용량을 좌우한다

같은 동영상이라도 코덱에 따라 파일 크기가 2배 이상 차이 난다. H.264로 10MB인 동영상이 VP9로는 약 7MB, AV1로는 약 5.4MB가 된다.

### 1.1 H.264 vs VP9 vs AV1

- **H.264(2003, MPEG)**: 가장 오래되고 안정적인 표준. 최대 강점은 **거의 모든 기기의 하드웨어 디코딩 지원** — 저사양 스마트폰과 구형 브라우저에서도 배터리 소모 없이 재생된다. 특허권이 있으나 **최종 사용자에게 무료로 제공되는 인터넷 동영상은 영구 로열티 무료**다(라이선스 비용은 10만 명 이상 유료 구독 서비스 등에만 해당). 지원율 약 95%로 **최종 폴백 필수**.
- **VP9(2013, 구글)**: H.264의 특허 문제와 유튜브 전송량 폭증에 대응해 개발된 **완전 무료 코덱**. H.264 대비 30~50% 효율적이다. 유튜브가 2014년부터 전면 도입. 지원율 약 95%지만 **사파리는 16.0+, iOS 사파리는 17.4+에서 정식 지원**이므로 그 이하는 H.264 폴백이 필요하다. 하드웨어 디코딩 지원이 H.264보다 제한적이다.
- **AV1(2018, AOMedia)**: 구글·넷플릭스·아마존 등이 결성한 연합의 차세대 무료 코덱. **Meta 실측 기준 H.264 대비 46.2%, VP9 대비 34.0% 절감.** 그러나 **인코딩이 VP9의 10배 이상, H.264의 90배 이상 느리다**(libaom 기준, SVT-AV1으로 개선 가능). 디코딩도 무거워 하드웨어 지원 없이는 배터리 소모가 크다. 지원율 약 93%이지만 **사파리는 하드웨어 디코더가 있는 기기(iPhone 15 Pro+, M3 Mac+)에서만 지원**한다.

| 코덱 | 지원율 | 압축 효율(H.264 기준) | 주요 제약 |
|---|---|---|---|
| H.264 | 약 95% | 기준 | Opera Mini 미지원 정도 |
| VP9 | 약 95% | 약 30% 절감 | 사파리 16 미만 미지원 |
| AV1 | 약 93% | 약 46% 절감 | 인코딩 매우 느림, 사파리는 HW 디코더 기기만 |

### 1.2 `<video>` 태그로 점진적 도입

브라우저는 `<source>`를 위에서부터 확인해 재생 가능한 첫 번째를 선택한다.

```html
<video controls width="1920" height="1080" poster="poster.jpg">
  <!-- AV1 지원 브라우저: 가장 작은 파일 (5.4MB) -->
  <source src="video.mp4" type='video/mp4; codecs="av01.0.05M.08"' />
  <!-- VP9 지원 브라우저 (7.2MB) -->
  <source src="video.webm" type='video/webm; codecs="vp09.00.41.08"' />
  <!-- 폴백: 모든 브라우저 (12MB) -->
  <source src="video-h264.mp4" type='video/mp4; codecs="avc1.640028"' />
  <p>Your browser doesn't support HTML video. <a href="video-h264.mp4">Download the video</a>.</p>
</video>
```

> **실무 팁**: **`codecs` 파라미터를 정확히 명시해야 한다.** `type="video/mp4"`만 쓰면 브라우저가 파일을 내려받아 직접 확인해야 하지만, codecs를 명시하면 다운로드 전에 재생 가능 여부를 판단한다. H.264 1080p는 `avc1.640028`(High Profile Level 4.0), VP9은 `vp09.00.41.08`, AV1은 `av01.0.05M.08` — 실제 인코딩 결과에 맞는 문자열을 쓴다. 컨테이너는 AV1=MP4(호환성)·WebM, VP9=WebM, H.264=MP4가 표준이다.

### 1.3 코덱별 사용 케이스

- **H.264**: ① 최대 호환성(구형 브라우저·스마트 TV·사파리 15 이하), ② 하드웨어 디코딩이 중요한 장시간 동영상(강의·웨비나 — 배터리), ③ **실시간/라이브 스트리밍**(AV1은 인코딩이 느려 실시간 불가).
- **VP9**: ① 무료 코덱이 필요하고 AV1 인코딩 비용은 부담일 때, ② **인코딩 속도와 압축 효율의 균형점**(사용자 업로드 동영상 서버 인코딩), ③ 최신 브라우저 사용자 위주 서비스.
- **AV1**: ① **정적 동영상(빌드 타임 인코딩)** — 마케팅·제품 데모처럼 한 번 인코딩해 반복 재생, ② 4K/8K/HDR 대용량, ③ 최신 기기 타깃.

> **핵심 통찰**: 실전 권장은 **세 코덱 모두 제공**이다. AV1(50% 절감) → VP9(30% 절감) → H.264(폴백) 순서로 `<source>`를 배치하면 브라우저가 자동 선택한다. 빌드 파이프라인에서 세 버전을 자동 생성해 CDN에 배포하면 초기 구축 비용 대비 장기 대역폭 절감이 크다.

## 2. 비트레이트와 해상도 최적화

### 2.1 비트레이트 실전 기준

비트레이트(초당 전송 데이터양, Mbps)가 화질과 파일 크기를 결정한다. **유튜브 공식 권장값**을 따르면 안전하다.

- **1080p**: 8~12Mbps (일반 웹 동영상 8, 액션 많으면 12)
- **720p**: 5~7.5Mbps
- **4K**: 35~45Mbps
- **60fps는 30fps 대비 약 1.5배** 비트레이트 필요 — 일반 웹 동영상은 30fps로 충분하고, 게임·스포츠만 60fps를 고려한다.

너무 낮으면 블로킹·모스키토 노이즈 같은 아티팩트가, 너무 높으면 대역폭 낭비가 발생한다. **1080p를 8Mbps와 20Mbps로 인코딩하면 육안 구분이 어려운데 파일 크기는 2.5배 차이 난다.**

### 2.2 반응형 동영상

모바일에 1080p를 보내는 것은 낭비다. 접근법 3단계:

1. **자바스크립트 화면 감지**: 간단하지만 JS 실행 지연이 있다.
2. **`<source media>` 속성**: `<picture>`처럼 미디어 쿼리로 브라우저가 자동 선택. JS 불필요. 단, 재생 후 창 크기를 바꿔도 전환되지 않고 네트워크 상황은 고려하지 못한다.
3. **적응형 스트리밍(HLS/DASH)**: 네트워크 속도에 따라 실시간 화질 전환(5절).

실무 절충안: **모바일 720p(4~5Mbps) + 데스크톱 1080p(6~8Mbps) + 선택적 4K.**

### 2.3 FFmpeg 핵심 설정

대부분의 웹 동영상은 이 명령 하나로 충분하다.

```bash
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset medium \
  -pix_fmt yuv420p -movflags +faststart -c:a aac -b:a 128k output.mp4
```

- **CRF(Constant Rate Factor)**: 화질 제어의 핵심. 낮을수록 고화질·대용량. **CRF 18 = 시각적 무손실, CRF 23 = 기본값(균형점), CRF 28 = 화질 저하 시작.** 값 1 차이가 파일 크기 약 10~15%를 바꾼다. 파일을 더 줄이려면 25~26, 고화질은 20~21. **VP9/AV1은 압축 효율이 좋아 같은 화질에 CRF를 5~7 높인다**(H.264 CRF 23 ≈ VP9/AV1 CRF 30).
- **preset**: 인코딩 속도 vs 압축 효율. `medium`이 기본, 빌드 타임 정적 동영상은 `slow`(5~10% 더 작음, 시간 2배), 실시간 처리는 `fast`.
- **`-movflags +faststart`**: **웹 필수 옵션.** MP4 메타데이터(moov atom)는 기본적으로 파일 끝에 있어 재생 시작이 지연된다. 이 옵션이 메타데이터를 앞으로 옮겨 **다운로드 중에도 즉시 재생**을 가능하게 한다.
- **`-pix_fmt yuv420p`**: 브라우저 호환성 필수. 없으면 일부 입력에서 yuv444p가 유지되어 특정 브라우저·기기에서 재생 불가.

### 2.4 GIF를 비디오로 대체하기

애니메이션 GIF는 웹에서 가장 비효율적인 포맷 중 하나다. 1987년 포맷이라 **프레임 간 압축이 없어** 각 프레임을 독립 저장한다(동영상 코덱은 이전 프레임과의 차이만 저장). web.dev 실측: **3.7MB GIF → MP4 551KB(85% 절감), WebM 341KB(91% 절감).**

```bash
# GIF → MP4 (H.264)
ffmpeg -i animation.gif -b:v 0 -crf 25 -f mp4 -vcodec libx264 -pix_fmt yuv420p animation.mp4

# GIF → WebM (VP9, 더 작은 파일)
ffmpeg -i animation.gif -c:v libvpx-vp9 -b:v 0 -crf 41 animation.webm

# 홀수 해상도 GIF 처리 (인코딩 실패 방지)
ffmpeg -i odd-size.gif -vf "crop=trunc(iw/2)*2:trunc(ih/2)*2" \
  -b:v 0 -crf 25 -f mp4 -vcodec libx264 -pix_fmt yuv420p output.mp4
```

```html
<video autoplay loop muted playsinline>
  <source src="animation.webm" type="video/webm" />  <!-- 작은 파일 우선 -->
  <source src="animation.mp4" type="video/mp4" />
</video>
```

> **실무 팁**: `muted`는 단순 음소거가 아니다 — **브라우저는 소리 있는 자동 재생을 차단하므로 `muted` 없이는 `autoplay`가 작동하지 않는다.** `playsinline`은 iOS 사파리의 인라인 재생에 필수(없으면 전체 화면 전환). `<video>`의 `loading="lazy"`는 표준에 추가됐지만 지원이 매우 낮으므로(크롬 148+ 중심) 실무 폴백은 `preload="none"` + 인터섹션 옵저버다. **100KB 이상의 GIF는 모두 비디오 대체를 검토한다.**

## 3. video 태그 속성 최적화

### 3.1 preload 전략 (none / metadata / auto)

| 값 | 다운로드 | 적합한 경우 |
|---|---|---|
| `none` | 0바이트(단, `poster`는 별도 다운로드 가능) | 페이지 하단, 대부분 안 보는 동영상, 데이터 요금 고려 |
| `metadata` | 재생 시간·해상도·트랙 정보 + 첫 몇 프레임(9MB 동영상 기준 약 919KB) | **대부분의 웹 동영상 — 기본 권장** |
| `auto` | 전체 파일 | 동영상이 페이지의 핵심이고 거의 모든 사용자가 재생하는 경우만 |

- 크롬 64+는 `preload` 속성이 없을 때 기본값을 `metadata`로 본다. 명시적으로 쓰는 것이 의도를 명확히 한다.
- **크롬은 모바일 네트워크(2G~4G)에서 `preload` 값과 무관하게 강제로 `metadata`를 적용**한다 — 모바일 데이터 보호를 위한 자동 최적화다.
- `auto`는 다른 중요 리소스(CSS·JS·LCP 이미지)의 다운로드를 지연시킬 수 있고, 재생하지 않으면 전부 낭비다.

### 3.2 포스터 이미지

`poster`는 동영상 로드 전에 표시할 이미지다. 성능 관점의 핵심은 **동영상이 페이지 최대 요소일 때 첫 프레임 또는 포스터 중 먼저 로드되는 것이 LCP로 측정된다**는 점이다.

- **동영상과 정확히 같은 종횡비**여야 한다. 다르면 동영상 로드 시 리플로우로 CLS가 발생한다. `width`/`height` 또는 `aspect-ratio`로 공간을 예약한다(`object-fit: cover`는 박스 안의 맞춤 방식만 제어할 뿐 CLS를 직접 막지 않는다).
- WebP/AVIF 사용(JPEG 대비 30~50% 절감). 단 `poster` 속성은 단일 URL만 받으므로 포맷 폴백이 필요하면 CDN의 Accept 헤더 자동 변환이나 `<picture>` 플레이스홀더 패턴을 쓴다.
- 포스터가 없으면 브라우저는 동영상 일부를 다운로드해 첫 프레임을 표시한다 — 더 느리고, 첫 프레임이 검은 화면일 수 있다. **항상 제공한다.**

### 3.3 자동 재생의 트레이드오프

autoplay의 세 가지 문제: ① **대역폭 소비**(10초 720p ≈ 3~4MB, 4K는 20MB+) — 관심 확인 없이 소비, ② **페이지 로딩 경쟁** — 중요 리소스와 대역폭을 다툼, ③ **뷰포트 밖에서도 즉시 다운로드**.

써야 한다면: **10초 이내·720p 이하·3~4MB 이내·`muted` 필수·인터섹션 옵저버로 뷰포트 진입 시에만 재생.** 배경 장식용은 포스터 이미지로 즉시 시각 피드백을 주고 동영상은 뷰포트 진입 후 로드한다. **자동 재생은 최후의 수단이다.**

## 4. 동영상 로딩 전략

### 4.1 동영상이 LCP인 경우

`<video>` 요소의 `readyState` 단계가 핵심이다.

| readyState | 이벤트 | 화면 상태 | 재생 가능 |
|---|---|---|---|
| 0 HAVE_NOTHING | loadstart | 검은 화면(포스터 있으면 포스터) | ✗ |
| 1 HAVE_METADATA | loadedmetadata | 검은 화면(포스터 있으면 포스터) | ✗ |
| 2 HAVE_CURRENT_DATA | loadeddata | **첫 프레임 표시(포스터 → 동영상 전환)** | ✗ |
| 3 HAVE_FUTURE_DATA | canplay | 첫 프레임 또는 재생 중 | ✓ |
| 4 HAVE_ENOUGH_DATA | canplaythrough | 재생 중 | ✓ |

첫 프레임 표시에는 readyState 2 이상이 필요하다 — 즉 동영상 파일을 충분히 다운로드해야 한다. **포스터 이미지가 있으면 이 대기가 사라진다.** DebugBear 실측: 포스터 없음 LCP 1.55초 → 포스터 추가 1.23초 → **포스터 `preload` + `fetchpriority` 적용 1.2초.**

```html
<head>
  <!-- 포스터 이미지를 최우선으로 로드 -->
  <link rel="preload" as="image" fetchpriority="high" href="hero-video-poster.webp" />
</head>
<body>
  <video poster="hero-video-poster.webp" preload="metadata" controls style="object-fit: cover;">
    <source src="hero-video.webm" type="video/webm" />
    <source src="hero-video.mp4" type="video/mp4" />
  </video>
</body>
```

> **핵심 통찰**: **크롬은 동영상 파일 자체의 프리로드(`<link rel="preload" as="video">`)를 지원하지 않는다.** 그래서 포스터 이미지 최적화가 동영상 LCP 개선의 사실상 유일한 실질적 해법이다. `fetchpriority="high"`는 LCP가 포스터인 경우에만 — 하단의 부가 동영상에 쓰면 오히려 중요 리소스와 경쟁해 LCP를 지연시킨다.

### 4.2 지연 로딩과 인터섹션 옵저버

**일반 동영상(재생 버튼 필요)**: `preload="none"`으로 미디어 사전 다운로드를 막는다. UX를 높이려면 hover 시 메타데이터를 미리 로드한다.

```html
<video controls preload="none" poster="placeholder.jpg"
       onmouseenter="this.setAttribute('preload', 'metadata')">
  <source src="video.webm" type="video/webm" />
  <source src="video.mp4" type="video/mp4" />
</video>
```

**자동 재생 동영상(GIF 대체용)**: `autoplay`가 있으면 `src`가 있는 순간 다운로드가 시작되므로, `data-src`에 URL을 담아두고 뷰포트 진입 시 복사한다.

```html
<video class="lazy" autoplay muted loop playsinline width="610" height="254" poster="placeholder.jpg">
  <source data-src="video.webm" type="video/webm" />
  <source data-src="video.mp4" type="video/mp4" />
</video>
```

```ts
document.addEventListener('DOMContentLoaded', () => {
  const lazyVideos = document.querySelectorAll<HTMLVideoElement>('video.lazy');

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const video = entry.target as HTMLVideoElement;
        // data-src를 src로 복사
        for (const source of Array.from(video.children)) {
          if (source.tagName === 'SOURCE') {
            (source as HTMLSourceElement).src = (source as HTMLElement).dataset.src ?? '';
          }
        }
        video.load();              // 동영상 로드 시작
        observer.unobserve(video); // 관찰 중지
      }
    });
  });

  lazyVideos.forEach((video) => observer.observe(video));
});
```

인터섹션 옵저버는 지원율 97.9%로 폴백 없이 써도 대부분 문제없다. 직접 구현이 번거로우면 vanilla-lazyload·lozad.js·yall.js 같은 라이브러리를 쓴다.

### 4.3 파사드 패턴으로 임베드 최적화

**유튜브 임베드 하나가 1.3MB 리소스 + 32개 네트워크 요청**을 발생시키고, 임베드끼리 리소스를 공유하지 않아 2개면 2.4MB, 3개면 3.6MB로 선형 증가한다. 대부분의 사용자는 재생하지 않고 지나간다.

파사드(Facade) 패턴은 섬네일 + 재생 버튼만 있는 가벼운 정적 플레이스홀더를 표시하고, **클릭 시에만 실제 임베드를 로드**한다. `lite-youtube-embed`(표준 대비 약 13배 작은 100KB) 같은 라이브러리로 쉽게 구현한다. 상세 구현은 Ch23에서 다룬다.

## 5. 적응형 스트리밍과 고급 최적화

### 5.1 HLS와 DASH

**적응형 비트레이트 스트리밍**은 동영상을 여러 화질(360p/720p/1080p)로 인코딩하고 각각을 2~10초 세그먼트로 분할한 뒤, 매니페스트 파일로 목록을 제공한다. 클라이언트는 낮은 화질로 빠르게 재생을 시작하고 네트워크 속도를 측정하며 화질을 전환한다 — 유튜브·넷플릭스·트위치의 방식이다. **버퍼링 대신 "약간 낮은 화질"을 택하는 것이 대부분 더 나은 경험**이다.

- **HLS**(애플, 2009, `.m3u8`): 사파리·iOS 네이티브 재생, 다른 브라우저는 hls.js + MSE로 재생. 스마트 TV·콘솔까지 거의 모든 환경 지원. **Low-Latency HLS로 지연도 개선.**
- **DASH**(MPEG, 2012, `.mpd`): 국제 표준이지만 **사파리 네이티브 미지원, iOS 제약이 크다.** dash.js·Shaka Player로 MSE 브라우저에서 재생.

> **핵심 통찰**: 실무 권장은 **HLS 기본**이다. 애플 생태계의 점유율 때문에 DASH만 제공하면 많은 사용자를 잃는다. 직접 구현(다중 인코딩 + 세그먼트 분할 + 매니페스트 생성)은 복잡하므로 대부분 동영상 CDN에 맡기는 것이 효율적이다.

### 5.2 동영상 CDN (Cloudinary, Mux)

- **Cloudinary**: 이미지+동영상 통합 관리. URL 파라미터(`q_auto`, `f_auto`)로 즉시 변환, HLS/DASH 지원. 크레딧 기반 과금(무료 플랜 월 25 크레딧).
- **Mux**: 동영상 스트리밍 특화. **Just-in-Time 인코딩** — 사용자가 실제 시청하는 화질만 인코딩해 비용 절감. 시청 데이터 분석(이탈 지점·화질·버퍼링) 기본 포함. 분 단위 과금.

선택 기준: ① 이미지도 함께 쓰면 Cloudinary, ② 동영상이 핵심 콘텐츠면 Mux, ③ 트래픽 규모에 따라 과금 방식 비교. **5분 이상 긴 동영상이나 라이브 스트리밍이면 CDN 도입을 검토하고, 1~2분짜리 데모·마케팅 영상은 직접 인코딩한 MP4/WebM + 일반 CDN으로 충분하다.**

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|---|---|---|
| `type="video/mp4"`만 쓰고 codecs 생략 | 브라우저가 파일을 받아봐야 재생 가능 여부를 알 수 있음 | `codecs="av01…"` 등 정확히 명시 |
| 모든 동영상을 AV1로 실시간 인코딩 | 인코딩이 H.264의 90배 느려 실시간 불가 | 정적 동영상만 AV1, 실시간은 H.264/VP9 |
| 사파리 폴백 없이 VP9/AV1만 제공 | 사파리 16 미만·HW 디코더 없는 기기에서 재생 불가 | H.264 `<source>`를 마지막에 필수 배치 |
| `-movflags +faststart` 누락 | 메타데이터가 파일 끝에 있어 재생 시작 지연 | 웹용 MP4에 항상 적용 |
| `-pix_fmt yuv420p` 누락 | 일부 브라우저·기기에서 재생 불가 | MP4 인코딩 시 항상 지정 |
| 비트레이트 과다(1080p 20Mbps) | 육안 차이 없이 파일만 2.5배 | 유튜브 권장값(1080p 8~12Mbps) 준수 |
| 애니메이션을 GIF로 유지 | 프레임 간 압축이 없어 비디오 대비 80~90% 낭비 | MP4/WebM `<video autoplay loop muted playsinline>` |
| `muted` 없이 `autoplay` | 브라우저가 자동 재생을 차단해 아예 재생 안 됨 | `muted` + `playsinline` 필수 |
| 모든 동영상에 `preload="auto"` | 수십 MB를 미리 받아 중요 리소스 로딩 지연 | 기본 `metadata`, 하단 동영상은 `none` |
| LCP 동영상에 포스터 미제공 | readyState 2까지 검은 화면 → LCP 지연 | WebP 포스터 + `preload` + `fetchpriority="high"` |
| `<link rel="preload" as="video">` 시도 | 크롬이 동영상 프리로드를 지원하지 않음 | 포스터 이미지 프리로드로 대체 |
| 포스터와 동영상의 종횡비 불일치 | 동영상 로드 시 리플로우 → CLS 발생 | 동일 비율 + `width`/`height` 예약 |
| 유튜브 임베드를 그대로 여러 개 배치 | 1.3MB × 개수만큼 선형 증가 | 파사드 패턴(lite-youtube-embed) |
| autoplay 동영상에 `src` 직접 지정 | 뷰포트 밖에서도 즉시 다운로드 | `data-src` + 인터섹션 옵저버 |

## 측정과 검증

- **Network 탭**: 동영상 다운로드 크기와 시점을 모니터링한다. `preload` 설정별 초기 전송량(none=0, metadata≈파일의 10%)을 확인한다.
- **LCP 확인**: 동영상이 LCP 요소인지 Performance 패널에서 식별하고, 포스터 적용 전후의 LCP(목표 2.5초 이내)를 비교한다.
- **라이트하우스**: 자동 재생 동영상 관련 경고 확인.
- **모바일 네트워크 테스트**: Slow 4G/Regular 4G에서 버퍼링 없이 재생되는지 확인한다.
- **CLS**: 포스터 종횡비 불일치로 인한 시프트가 없는지 확인(목표 0.1 이하).
- **동영상 CDN 분석**(Mux 등): 시청 이탈 지점, 실제 시청 화질 분포, 버퍼링 발생률로 인코딩 프로필을 조정한다.

## 체크리스트

**포맷과 코덱 최적화**

- [ ] 브라우저 지원율 확인 후 코덱 선택(H.264 ~95%, VP9 ~95%, AV1 ~93%)
- [ ] H.264 폴백 + VP9/AV1 추가 제공(`<video>`에 여러 `<source>`, codecs 명시)
- [ ] 정적 동영상은 빌드 타임 AV1 인코딩으로 최대 절감
- [ ] 라이브·사용자 업로드는 H.264/VP9 사용
- [ ] 사파리 구형 버전 지원 필요 시 H.264 우선

**비트레이트와 해상도 관리**

- [ ] 유튜브 권장 비트레이트 준수(1080p 8~12Mbps, 720p 5~7.5Mbps, 4K 35~45Mbps)
- [ ] FFmpeg CRF 23 기본(감량 25~26, 고화질 20~21)
- [ ] `-movflags +faststart` 적용
- [ ] preset: 기본 medium, 정적 파일은 slow
- [ ] 일반 동영상 30fps(60fps는 게임·스포츠만)
- [ ] 모바일 우선이면 720p 기본 + 1080p 선택

**GIF 대체**

- [ ] 100KB 이상 애니메이션 GIF를 동영상으로 대체 검토(80~90% 절감)
- [ ] MP4 + WebM 두 버전 생성, WebM을 첫 번째 `<source>`로
- [ ] `-pix_fmt yuv420p` + 홀수 해상도는 crop 필터 처리
- [ ] `<video autoplay loop muted playsinline>`으로 GIF처럼 동작

**로딩 전략과 UX**

- [ ] LCP 동영상은 WebP/AVIF 포스터 + `<link rel="preload" as="image" fetchpriority="high">`
- [ ] 일반 동영상 `preload="none"`, 재생 가능성 높으면 `metadata`
- [ ] 자동 재생은 10초·3~4MB 이내 + `muted` + 인터섹션 옵저버
- [ ] 포스터는 동영상과 동일 종횡비(CLS 방지)
- [ ] 유튜브/비메오 임베드는 파사드 패턴으로 교체

**고급 최적화**

- [ ] 5분 이상·라이브 스트리밍은 HLS/DASH 검토(애플 지원은 HLS 우선)
- [ ] 동영상이 주요 콘텐츠면 Mux/Cloudinary 검토
- [ ] Just-in-Time 인코딩·시청 분석 활용
- [ ] 무료 플랜으로 테스트 후 도입 결정

**성능 측정과 검증**

- [ ] LCP 2.5초 이내 확인(동영상 또는 포스터)
- [ ] Network 탭에서 동영상 다운로드 크기 모니터링
- [ ] 라이트하우스 자동 재생 경고 확인
- [ ] 모바일 네트워크에서 버퍼링 테스트
- [ ] CLS 0.1 이하 확인

## 요약

- 동영상 최적화의 본질은 압축이 아니라 **"언제 무엇을 어떻게 로드하는가"**다. 코덱 전환(H.264→VP9 30%, →AV1 46% 절감), preload 전략, 포스터, 파사드가 각각 큰 폭의 개선을 만든다.
- 코덱 3종 전략: **AV1(정적·최신 기기) → VP9(균형) → H.264(폴백 필수).** codecs 파라미터 명시가 다운로드 전 판단을 가능하게 한다. AV1의 인코딩 비용(90배)은 빌드 타임에만 감당 가능하다.
- 비트레이트는 유튜브 권장값이 기준선이다. CRF 23 + `-movflags +faststart` + `-pix_fmt yuv420p`가 웹 MP4의 표준 레시피이며, VP9/AV1은 CRF를 5~7 높인다.
- **GIF는 프레임 간 압축이 없는 1987년 포맷이다.** 비디오 전환으로 80~91% 절감되며, `autoplay loop muted playsinline` 4종 세트로 GIF처럼 동작한다.
- `preload`는 **`metadata`가 기본 권장**이다(9MB 중 약 919KB). `auto`는 핵심 콘텐츠에만, `none`은 하단 동영상에. 크롬은 모바일에서 강제 `metadata`를 적용한다.
- 동영상 LCP의 열쇠는 **포스터 이미지**다. readyState 2까지의 검은 화면을 없애고, 크롬이 동영상 프리로드를 지원하지 않으므로 포스터 프리로드가 유일한 실질 해법이다(실측 1.55s → 1.2s).
- 자동 재생 동영상은 `data-src` + 인터섹션 옵저버로 뷰포트 진입 시에만 로드한다. `<video loading="lazy">`는 아직 지원이 좁아 실무 폴백이 필요하다.
- **유튜브 임베드 1개 = 1.3MB + 32 요청, 공유 없이 선형 증가.** 파사드 패턴으로 약 100KB까지 줄인다.
- 긴 동영상·라이브는 적응형 스트리밍(HLS 기본 — 애플 생태계 때문)이 버퍼링 대신 화질 전환으로 경험을 지킨다. 직접 구현보다 동영상 CDN(Cloudinary·Mux)이 현실적이다.
- 우선순위: **히어로 자동 재생·LCP 동영상 → 임베드 파사드 교체 → 긴 동영상 스트리밍 검토.** 그리고 FFmpeg 스크립트·빌드 파이프라인·CDN으로 자동화해야 성능이 유지된다.

## 다른 챕터와의 관계

- **Ch12(이미지 최적화)**: GIF→비디오 전환의 출발점이 이미지 장이었고, 포스터 이미지 최적화(WebP/AVIF·프리로드·`fetchpriority`)는 이미지 장의 기법을 그대로 쓴다.
- **Ch4(리소스 우선순위)**: 포스터 프리로드와 `fetchpriority="high"`의 원리, "남발 금지" 원칙이 여기서 왔다.
- **Ch5(프리로드 스캐너)**: `data-src` 패턴이 프리로드 스캐너를 우회한다는 점 — 동영상에서는 그것이 의도된 동작(지연 로딩)이라는 대비가 흥미로운 지점이다.
- **Ch20(CLS)**: 포스터·동영상 종횡비 일치와 공간 예약이 CLS 장의 "크기 예약" 원칙과 직결된다.
- **Ch23(서드파티 코드)**: 파사드 패턴의 상세 구현(유튜브·비메오·채팅 위젯)을 전면적으로 다룬다.
- **Ch1(네트워크 최적화)**: 적응형 스트리밍의 세그먼트 전송이 CDN·HTTP 프로토콜 최적화 위에서 동작한다.
