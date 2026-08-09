# Chapter 21: 애니메이션은 60fps가 기본이다

## 핵심 질문

사용자는 끊기는 애니메이션을 "느리다"가 아니라 **"허술하다"** 고 받아들인다. 60fps = 프레임당 16.67ms인데, 브라우저 자체 렌더링에 약 6ms가 필요하므로 **자바스크립트와 스타일 계산에 쓸 수 있는 시간은 약 10ms뿐**이다(RAIL 모델의 프레임당 10ms 권장과 일치). 같은 시각적 효과라도 `width`를 애니메이션하느냐 `transform: scaleX()`를 쓰느냐에 따라 성능이 10배 이상 갈린다 — 왜 그런가, 그리고 60fps를 보장하는 구현·측정·모니터링은 어떻게 하는가?

## 1. 레이아웃 트리거 최소화 — transform/opacity 우선

### 1.1 렌더링 파이프라인과 단계별 비용

브라우저가 화면을 그리는 5단계: **자바스크립트 실행 → Style 계산 → Layout(리플로우) → Paint → Composite.**

- **Layout이 가장 비싸다**: 요소 하나의 크기가 바뀌면 부모·자식·형제까지 연쇄적으로 위치를 재계산한다. DOM 트리가 클수록 느려진다.
- **Paint**: 레이아웃 결과를 픽셀로 채운다(텍스트·색·그림자). 색상 변경만으로도 트리거된다.
- **Composite**: 여러 레이어를 GPU가 합성 — 상대적으로 매우 빠르다.

> **핵심 통찰**: 애니메이션 최적화의 본질은 **이 파이프라인을 얼마나 건너뛰느냐**다. `width` 애니메이션은 매 프레임 전체 파이프라인(Layout 8ms + Paint 5ms면 이미 13ms — 예산 초과). `opacity`는 Layout 생략, `transform`은 **Layout과 Paint를 모두 생략**하고 Composite만 실행한다. Performance 패널에서 width 애니메이션은 보라색 Layout 바 + 녹색 Paint 바가 프레임마다 반복되지만, transform은 둘 다 사라진다.

`width: 100px → 300px` 대신 `transform: scaleX(3)`(+`transform-origin`)을 쓰면 시각적으로 동일하되 브라우저는 요소를 여전히 100px로 간주하고 GPU에서 3배 확대해 그린다. 단순한 데모에선 둘 다 60fps가 나올 수 있지만 — **Main 스레드 부하 차이**가 복잡한 DOM·동시 다중 애니메이션·모바일에서 프레임 드롭으로 드러난다. (주의: scale은 콘텐츠도 함께 확대된다 — 내용물을 유지하려면 내부 요소에 역 transform.)

### 1.2 CSS 속성 3분류

**Composite만(가장 빠름)** — `transform` 전 함수·`opacity`(항상 GPU 보장), `filter`·`clip-path`(브라우저에 따라 GPU).

> **참고 — filter: blur()는 공짜가 아니다**<br><br>블러는 각 픽셀 주변을 샘플링해 평균 내는 연산이라 **반경의 제곱에 비례**해 비용이 는다(10px ≈ 400샘플, 50px ≈ 10,000샘플). 게다가 블러가 경계 밖으로 번지므로 레이어 크기도 반경만큼 커진다 — 100×100 요소 + 50px 블러 = 200×200 레이어(GPU 메모리 4배). 실무는 3~10px, 모바일 고려 시 20px 이하로 제한한다.

**Paint 트리거(중간)** — `color`, `background-color`, `border-color`, `box-shadow`, `outline`, `visibility`. 60fps는 가능하지만 CPU 부하가 있어 다수 동시 애니메이션엔 불리.

**Layout 트리거(가장 느림 — 애니메이션 금지)** — `width`/`height`(min·max 포함), `padding`, `border-width`, `top/right/bottom/left`, `margin`, flex(`flex-grow` 등)·grid(`grid-template-*`, `gap`), 텍스트(`font-size`, `line-height` 등), `display`·`position`·`float` 전환. 대체: width→`scaleX`, left→`translateX`, top→`translateY`. 속성별 엔진별 트리거는 CSS Triggers 사이트에서 확인.

그리고 **자바스크립트로 레이아웃 속성을 읽기만 해도**(`offsetWidth`, `getBoundingClientRect()`) 최신 값을 주기 위한 **강제 레이아웃**이 발생한다 — 애니메이션 루프 안 읽기/쓰기 교대는 프레임마다 강제 Layout. 모든 읽기 먼저, 모든 쓰기 나중(Ch16·18과 동일 원칙).

### 1.3 의외의 복병 — CSS 변수 애니메이션

CSS 변수를 경유하면 `opacity`처럼 원래 Composite 속성도 **Paint가 트리거**된다. 더 심각한 건 **상속** — `:root`/`html`에 정의한 변수를 매 프레임 갱신하면 그 변수를 쓰지 않는 요소까지 재평가 대상이 되어 DOM 전체 재계산으로 프레임당 5~8ms+가 사라진다. 데모에선 멀쩡하고 프로덕션에서 재앙이 되는 패턴.

안전 가이드: ① 전역 변수는 애니메이션하지 않는다 — 컴포넌트 최상위로 범위 한정 ② `@property`로 `inherits: false` 등록(상속 차단 — web.dev 벤치마크 848% 개선) ③ transform/opacity에는 변수 대신 `style.transform` 직접 업데이트 ④ 어차피 Paint인 속성(gradient stop 등)에는 써도 손해 없음.

## 2. 컴포지터 레이어와 GPU 가속

### 2.1 레이어 기반 합성의 원리

브라우저는 페이지를 단일 비트맵이 아니라 **여러 레이어**로 나눠 관리한다. 승격된 레이어는 GPU 메모리에 텍스처로 저장되고, 애니메이션 중에는 **픽셀을 다시 그리지 않고** GPU가 위치·크기·투명도·변형만 바꿔 합성한다. 메인 스레드가 아무리 바빠도 GPU는 독립적으로 레이어를 움직인다 — 이것이 60fps 보장의 핵심 메커니즘이다.

`transform`은 텍스처의 좌표계(변환 행렬)만, `opacity`는 알파 값만 갱신한다. 단 **transform과 함께 width를 애니메이션하면 Layout이 되살아나 이점이 사라진다** — 반드시 transform/opacity만.

비용도 있다: 레이어는 GPU 메모리를 먹는다 — **1920×1080 레이어 ≈ 8MB**(RGBA 4bytes/px).

> **실무 팁 — 무한 스크롤 티커(marquee)의 함정**: 로고 50개를 복제해 `translateX`로 무한 스크롤하면 전체 티커가 **하나의 거대 레이어**(96,000×100px ≈ 38MB)가 된다. 모바일 GPU 메모리에서는 브라우저 강제 종료 감이다. 해법: ① 화면 밖 요소를 재활용해 DOM 수를 뷰포트의 2~3배로 제한 ② 레이어 분할 ③ IntersectionObserver로 화면 밖에서 애니메이션 중지.

### 2.2 레이어 승격 조건과 Layers 패널

**명시적 승격**: `will-change: transform/opacity`(가장 현대적·권장), 3D transform(`translateZ(0)` 해크 — 의도가 불명확해 will-change 권장), `video`/`canvas`/`iframe`(항상), `backface-visibility: hidden`, `filter`/`backdrop-filter`.

**암시적 승격**: transform/opacity의 **CSS transition·animation은 자동 승격**된다(단 JS로 직접 스타일을 바꾸는 경우엔 승격이 안 될 수 있어 will-change 명시가 안전). **겹침(overlap)** — 레이어 위에 겹친 요소는 z-order 유지를 위해 함께 승격되는데, 이것이 의도치 않은 레이어 폭증의 원인이다(z-index·DOM 순서 조정으로 해소). `position: fixed`도 대개 승격.

**Layers 패널**(개발자 도구 → More tools → Layers): 레이어 3D 시각화 + 크기·메모리·**Compositing Reasons**("has a will-change hint", "overlaps other composited content" 등)·**Paint count**(애니메이션 중 증가하지 않으면 GPU 가속 정상 작동의 증거).

## 3. will-change의 올바른 사용법과 함정

### 3.1 무엇을 해주나

`will-change: transform`은 "곧 이 속성이 변한다"는 힌트 — 브라우저가 **레이어를 미리 생성**해 둔다. 없으면 첫 호버 순간에 레이어 생성 비용이 들어 첫 프레임이 버벅인다(모바일·저사양에서 두드러짐). 있으면 첫 프레임부터 부드럽다.

단 **마법이 아니다** — `will-change: width`를 줘도 width는 여전히 Layout을 트리거한다. 빠른 애니메이션의 답은 여전히 transform/opacity다.

### 3.2 남용의 3중 비용

모든 요소(최악은 `* { will-change: transform }`)에 붙이면: ① **GPU 메모리 급증** — 300×400px 카드 100장 = 레이어당 ~500KB × 100 = 50MB 추가 ② **페이지 로드 지연** — 레이어 생성 + GPU 업로드가 초기 렌더링을 늦춤 ③ **컴포지팅 비용 증가** — 수백 레이어 관리가 오히려 스크롤을 버벅이게 한다. 최적화 도구가 성능 저하의 원인이 되는 역설.

원칙: **실제로 애니메이션하는 요소에만, 수술용 메스처럼.** 다수 요소 동시 애니메이션이면 화면에 보이는 것만(IntersectionObserver) 적용한다.

### 3.3 사용 후 제거 — 동적 관리 패턴

will-change가 남아 있는 한 레이어와 메모리도 남는다. CSS에 정적으로 쓰면 제거가 불가능하므로 **자바스크립트로 추가·제거**한다:

```ts
function openModal() {
  modal.style.willChange = 'transform, opacity'; // ① 레이어 미리 생성
  requestAnimationFrame(() => {                   // ② 다음 프레임에 애니메이션 시작(생성 시간 확보)
    modal.classList.add('open');
  });
  modal.addEventListener('transitionend', () => { // ③ 완료 후 해제 → 메모리 반환
    modal.style.willChange = 'auto';
  }, { once: true });
}
```

- 복수 트랜지션(transform+opacity)은 transitionend 횟수를 세거나, duration+여유의 setTimeout으로.
- CSS animation은 `animationend` 이벤트로.
- 무한 반복 애니메이션(스피너)은 유지하되, 중지 시 즉시 `'auto'`.
- 스크롤 진입 애니메이션은 IntersectionObserver로 진입 시 추가 → 완료 시 제거 + `unobserve` — 메모리와 스크롤 성능을 모두 지킨다.

## 4. requestAnimationFrame으로 프레임 동기화

### 4.1 rAF의 동작 원리

렌더링 사이클: Input events → **rAF 콜백** → Style → Layout → Paint → Composite → Display. rAF 콜백은 렌더링 직전에 실행되므로 여기서의 DOM 변경이 **같은 사이클에 반영**된다 — 타이밍이 완벽하다.

- 브라우저가 준비됐을 때만 실행 → **콜백 쌓임 방지**(메인 스레드가 바쁘면 프레임을 건너뜀).
- **백그라운드 탭에서 자동 중지** → CPU·배터리 절약(setInterval은 1초 간격으로 스로틀될 뿐 계속 돈다).
- 콜백 인자로 고정밀 **타임스탬프** — 경과 시간 기반 진행률(`progress = elapsed / duration`)을 쓰면 프레임 레이트가 30fps로 떨어져도 정확히 같은 시간에 목표에 도달한다.
- 중지는 `cancelAnimationFrame(id)`.

### 4.2 setInterval/setTimeout이 안 되는 이유

- **렌더링 사이클과 비동기**: 타이머는 16ms마다, 렌더링은 16.67ms마다 — 어긋나며 프레임 드롭.
- **백그라운드에서도 실행**: 리소스 낭비.
- **콜백 누적**: 콜백이 16ms보다 오래 걸리면 큐가 쌓인다.

100개 요소 비교 실측: setInterval은 100개의 Timer fired가 프레임 전체에 산발적으로 흩어지고, rAF는 Animation Frame Fired가 규칙적 간격으로 프레임 시작점에 집중된다(한 콜백에서 일괄 처리). CPU 스로틀링이나 요소 증가 시 setInterval이 먼저 무너진다. 마이그레이션 요령: `clearInterval` 대신 재귀 호출을 조건문으로 중단.

### 4.3 실전 패턴 5종

1. **중앙 애니메이션 루프**: 애니메이션마다 rAF를 따로 돌리지 말고 하나의 루프에서 배열로 관리 — 배열이 비면 루프 자동 중지.
2. **이징 함수**: `progress`(0~1)에 `easeOutQuad = t * (2 - t)` 등을 적용해 자연스러운 가속/감속.
3. **Promise 기반**: 완료 시 resolve → `await animatePromise(...)`로 순차 애니메이션을 평문처럼.
4. **AnimationManager**: 각 항목의 `update(timestamp)`가 계속 여부를 반환 — 완료 항목 자동 제거, 전부 끝나면 루프 종료.
5. **스크롤 디바운싱**: `ticking` 플래그로 스크롤 이벤트가 아무리 와도 **프레임당 한 번만** rAF 예약(패럴랙스 등).

```ts
let ticking = false;
window.addEventListener('scroll', () => {
  if (!ticking) {
    requestAnimationFrame(() => {
      updateParallax();
      ticking = false;
    });
    ticking = true;
  }
});
```

## 5. CSS가 기본이고 JS는 필요할 때만

### 5.1 세 가지 방식의 성격

**CSS transition/animation** — 선언적·간결, 그리고 **컴포지터 스레드에서 독립 실행**(transform/opacity 한정): 메인 스레드가 바빠도 60fps 유지, 레이어 자동 승격. keyframes로 다단계 시퀀스·무한 반복(스피너·스켈레톤 shimmer)도 간단. **한계**: 중간 정지·속도 변경·역재생이 어렵고, 조건부 로직·현재 값 접근 불가, 다수 요소 순차 실행은 `nth-child` delay 수동 나열.

**Web Animations API(WAAPI)** — `element.animate(keyframes, options)`. CSS와 **동일한 컴포지터 최적화** + 자바스크립트 제어력. 2024년 기준 전 브라우저 지원.

- 동적 값: `translateX(${distance}px)` — CSS로 불가능한 런타임 계산.
- 제어: `pause()`/`play()`/`reverse()`/`playbackRate`/`currentTime`/`cancel()`/`finish()`.
- **`animation.finished` Promise** → `await`로 순차 애니메이션이 깔끔해진다.
- 다단계는 keyframe 객체의 `offset`(0~1, CSS %와 동일).

**requestAnimationFrame** — 제어력 최대, 메인 스레드 의존. 실시간 계산이 필수인 경우만.

### 5.2 선택 기준

| 상황 | 권장 | 이유 |
|---|---|---|
| 버튼 호버·체크박스 토글·탭 전환 | CSS | 상태 전환만 — 선언적·간결 |
| 페이드 인/아웃·로딩 스피너·스켈레톤 | CSS | 단순 전환·무한 반복, 메인 스레드 독립 |
| 모달 열기/닫기 | CSS/WAAPI | CSS로 충분, 완료 이벤트 필요 시 WAAPI |
| 진행 바(동적 제어)·순차 애니메이션 | WAAPI | pause/재생·Promise 체이닝 |
| 드래그 앤드 드롭·스크롤 패럴랙스 | rAF | 실시간 입력 추적 |
| 물리 시뮬레이션·게임·차트 | rAF(차트는 WAAPI도) | 프레임마다 상태 계산 |

- **하이브리드**가 실무적이다: 드래그 중에는 rAF로 실시간 추적, 드롭 후 제자리 복귀는 WAAPI로.
- 성능 우선순위는 CSS > WAAPI > rAF지만, **셋 다 transform/opacity만 쓰면 모두 컴포지터에서 실행되어 차이가 미미**하다 — 선택은 코드 복잡도와 제어 필요성으로.
- 실무 비율 감각: **CSS 80% / WAAPI 15% / rAF 5%.** 복잡도 낮은 방법부터 시작하고 필요할 때만 올라간다.

## 6. 애니메이션 성능 측정과 디버깅

### 6.1 Performance 탭 워크플로

1. **FPS 미터**(Cmd+Shift+P → "Show frames per second") — 실시간 FPS, 60 아래로 떨어지는지 확인.
2. **녹화 3~5초** → FPS 그래프의 **빨간 막대** = 드롭 구간 → 드래그 확대.
3. 색으로 원인 분류: **노랑(자바스크립트)** 크면 JS 실행 과다, **보라(Recalculate Style/Layout)** 크면 레이아웃·스타일 재계산.
4. **Bottom-Up 탭 → Self Time 정렬** — 가장 오래 걸린 함수가 최적화 대상.
5. 수정 → 같은 조건으로 재측정. **"추측하지 말고 측정한다."**

전형적 발견: 루프 안에서 `offsetWidth` 읽기+쓰기 교대 → 보라색 Layout 바 반복(강제 동기 레이아웃) → 읽기 일괄 후 쓰기 일괄로 Layout 1회화.

### 6.2 Rendering 탭 — 어디서 낭비가 일어나는지

- **Paint Flashing**: 페인트 발생 영역이 녹색으로 깜빡인다. width 호버는 깜빡 / transform 호버는 안 깜빡. **box-shadow 호버 애니메이션**이 카드 전체를 깜빡이게 한다면 → 의사 요소 `::after`에 그림자를 미리 그려두고 `opacity`만 전환하는 패턴으로 해결.
- **Layer Borders**: 오렌지 테두리 = 컴포지터 레이어. 100개가 보이면 메모리 낭비 — `animating` 클래스로 애니메이션 중에만 will-change를 주고 끝나면 제거해, 테두리가 생겼다 사라지는지 확인.
- **Layers 패널**: Compositing Reasons에서 "overlaps other composited content"는 **의도치 않은 승격** — z-index·레이아웃 조정으로 겹침 해소.
- **Frame Rendering Stats**: 실시간 FPS + GPU 메모리. **GPU 메모리가 계속 증가하면 레이어 누수**(will-change 미제거 등).

### 6.3 프로덕션 프레임 드롭 모니터링

개발자의 고사양 장비에서 60fps여도 사용자의 저사양 폰에서는 30fps일 수 있다 — 실사용자 데이터가 필요하다.

- **rAF 타임스탬프 델타**: 프레임 간격이 16.67×1.5 = 25ms를 넘으면 드롭으로 판정, 드롭율을 집계해 전송.
- **구간 측정 트래커**: 모달 열기 같은 핵심 애니메이션의 start~transitionend 사이 프레임을 기록해 평균 FPS·드롭 횟수·드롭율 산출.
- **Long Animation Frames API**(크롬 123+ 정식): 50ms 이상 걸린 애니메이션 프레임을 자동 감지하고, `entry.scripts`로 **어떤 스크립트가 원인인지**까지 알려준다.
- **디바이스 정보 동봉**: `deviceMemory`·`hardwareConcurrency`·`connection.effectiveType` — 디바이스별 분석으로 저사양 최적화 우선순위 결정.
- **샘플링**: 10% 사용자만, 또는 드롭율 10% 이상만 전송(sendBeacon) — 오버헤드와 서버 부하 절감.

전략의 핵심은 **선택과 집중**: 모든 애니메이션이 아니라 핵심 애니메이션(페이지 전환·모달·드로어)을, 모든 사용자가 아니라 샘플을.

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|---|---|---|
| width/height/top/left 애니메이션 | 매 프레임 Layout+Paint — 전체 파이프라인 실행 | transform(scale/translate)·opacity로 대체 |
| transform과 함께 레이아웃 속성 병행 | Layout이 되살아나 GPU 가속 이점 소멸 | transform/opacity만 단독으로 |
| box-shadow 직접 전환 | 카드 전체 Paint 반복(Paint Flashing 깜빡) | ::after에 그림자 + opacity 전환 |
| 전역 CSS 변수를 매 프레임 갱신 | 상속 때문에 DOM 전체 재평가(5~8ms+) | 범위 한정 / @property inherits:false / 직접 style 업데이트 |
| 큰 filter: blur() 애니메이션 | 반경 제곱 비례 연산 + 레이어 확장 | 3~10px, 모바일 20px 이하 |
| `* { will-change: ... }` | 수천 레이어 = GPU 메모리 폭증 + 로드 지연 + 컴포지팅 병목 | 실제 애니메이션 요소에만 |
| will-change 영구 방치 | 레이어·메모리 계속 점유(GPU 메모리 우상향) | 시작 직전 추가 → transitionend에서 'auto' |
| 애니메이션 루프에서 offsetWidth 읽기+쓰기 교대 | 프레임마다 강제 동기 레이아웃 | 읽기 일괄 → 쓰기 일괄 |
| setInterval(16ms) 애니메이션 | 렌더링과 비동기·백그라운드 실행·콜백 누적 | requestAnimationFrame + 타임스탬프 |
| 애니메이션마다 독립 rAF 루프 | 프레임당 rAF 다중 호출 오버헤드 | 중앙 루프에서 일괄 관리 |
| 프레임 수 기반 진행(position += 2) | 프레임 레이트 변하면 속도가 변함 | 타임스탬프 기반 progress 계산 |
| 스크롤 이벤트마다 즉시 DOM 갱신 | 프레임당 수십 회 중복 작업 | ticking 플래그 + rAF 디바운싱 |
| 복제 요소로 만든 거대 티커 레이어 | 96,000px 레이어 ≈ 38MB — 모바일 크래시 위험 | 요소 재활용 + 화면 밖 애니메이션 중지 |
| 단순 호버까지 JS로 구현 | 불필요한 복잡도 + 메인 스레드 의존 | CSS 기본, WAAPI·rAF는 필요할 때만 |
| 고사양 장비에서만 확인 | 실사용자 저사양 폰에서 30fps | CPU 스로틀링 테스트 + 프로덕션 RUM |

## 측정과 검증

- **FPS 미터 + Performance 녹화**: 빨간 구간 → 확대 → 노랑(JS)/보라(Layout) 분류 → Bottom-Up Self Time으로 병목 함수 특정 → 수정 → 재측정.
- **Paint Flashing**: 애니메이션 중 녹색 깜빡임이 없어야 정상(컴포지터 처리 확인).
- **Layer Borders + Layers 패널**: 레이어 수 적정성, Compositing Reasons에서 의도치 않은 승격(overlap) 점검, Paint count 불변 확인.
- **Frame Rendering Stats**: GPU 메모리 추이 — 우상향이면 레이어 누수.
- **CPU 스로틀링(4x~6x)**: 저사양 환경 재현.
- **프로덕션**: Long Animation Frames API(50ms+ 프레임 + 원인 스크립트) + 디바이스 정보 + 샘플링 수집 → 디바이스별·페이지별 드롭율 대시보드.
- **접근성**: `prefers-reduced-motion` 미디어 쿼리 지원 확인.

## 체크리스트

**레이아웃 트리거 최소화**

- [ ] 애니메이션에 transform·opacity만 사용
- [ ] width·height·top·left 등 레이아웃 속성 애니메이션 금지
- [ ] 확대/축소는 transform: scale(), 이동은 translate()
- [ ] CSS 변수 애니메이션은 범위 한정(전역 금지)

**will-change 관리**

- [ ] 애니메이션 시작 직전에만 추가
- [ ] 종료 후 제거('auto')
- [ ] 와일드카드·전역 적용 금지
- [ ] Layer Borders로 불필요한 레이어 확인
- [ ] GPU 메모리 사용량 모니터링

**레이아웃 스래싱 방지**

- [ ] 레이아웃 읽기(getBoundingClientRect 등)를 루프 밖·프레임 시작에 일괄
- [ ] 읽기 → 쓰기 순서 분리
- [ ] Performance 탭에서 Forced reflow 경고 확인

**requestAnimationFrame**

- [ ] setTimeout/setInterval 대신 rAF 사용
- [ ] 타임스탬프 기반 진행률로 프레임 레이트 독립성 확보
- [ ] 종료 시 cancelAnimationFrame 정리
- [ ] 스크롤 연동은 ticking 플래그 디바운싱

**CSS vs JS 선택**

- [ ] 단순 호버·토글·페이드는 CSS
- [ ] 동적 제어·완료 이벤트·순차 실행은 WAAPI
- [ ] 실시간 인터랙션(드래그·스크롤 동기화)만 rAF
- [ ] 하이브리드 패턴 활용(드래그 rAF + 복귀 WAAPI)

**측정·모니터링**

- [ ] 프레임당 16.67ms 이내 확인(FPS 미터·Performance)
- [ ] Paint Flashing으로 불필요한 페인트 확인
- [ ] CPU 스로틀링으로 저사양 테스트
- [ ] 핵심 애니메이션에 성능 추적 코드
- [ ] Long Animation Frames API로 50ms+ 프레임 감지
- [ ] 디바이스별 드롭 데이터 샘플링 수집

**일반 원칙**

- [ ] prefers-reduced-motion 지원
- [ ] 애니메이션 없이도 기능 정상 작동(점진적 향상)

## 요약

- 60fps = 16.67ms/프레임, 그중 JS+스타일 몫은 **~10ms**. 예산 안에 들어오는 방법은 파이프라인 단계를 건너뛰는 것 — **transform·opacity는 Layout·Paint를 생략하고 GPU 컴포지터에서만 처리**된다. width→scaleX, left→translateX로 바꾸는 것이 최적화의 절반이다.
- 속성 3분류: Composite만(transform·opacity·조건부 filter — blur는 반경 제곱 비용) / Paint(색·그림자·visibility) / Layout(크기·위치·박스·텍스트 — 애니메이션 금지). **CSS 변수 경유는 Paint로 강등 + 전역 변수는 상속 폭발** — @property inherits:false 또는 직접 업데이트.
- **컴포지터 레이어**: 승격된 요소는 GPU 텍스처가 되어 픽셀 재그리기 없이 변환·합성된다. 메인 스레드와 독립 — 이것이 60fps 보장의 정체. 대가는 메모리(풀HD ≈ 8MB/레이어) — 거대 티커 레이어, 겹침으로 인한 의도치 않은 승격을 경계한다.
- **will-change**는 레이어를 미리 만들어 첫 프레임 버벅임을 없애는 힌트일 뿐 — 느린 속성을 빠르게 해주지 않는다. 실제 애니메이션 요소에만, **시작 직전 추가 → 종료 후 제거**(JS 동적 관리 + transitionend). 남용은 메모리·로드·컴포지팅 3중 비용.
- **rAF**는 렌더링 사이클과 동기화된 유일한 타이밍 API — 백그라운드 자동 중지, 콜백 쌓임 방지, 타임스탬프 기반 진행률로 프레임 레이트 독립. 중앙 루프·이징·Promise·매니저·ticking 디바운싱 패턴으로 확장한다.
- 선택 기준: **CSS 80%**(상태 전환·반복 — 컴포지터 독립 실행) / **WAAPI 15%**(동적 값·pause/reverse·finished Promise) / **rAF 5%**(실시간 입력·물리). 셋 다 transform/opacity만 쓰면 성능은 비슷하다 — 복잡도로 선택한다.
- 디버깅 루프: FPS 미터 → 녹화 → 빨간 구간(노랑=JS, 보라=Layout) → Bottom-Up → 수정 → 재측정. Rendering 탭(Paint Flashing·Layer Borders)으로 낭비 시각화. 프로덕션은 Long Animation Frames API + 디바이스 정보 + 샘플링 — **데이터 없으면 추측, 데이터 있으면 확신.**

## 다른 챕터와의 관계

- **Ch18(자바스크립트 실행)**: 프레임 예산(16.67ms)과 긴 작업(50ms)은 같은 메인 스레드 자원의 두 관점 — rAF vs setTimeout 논의, 읽기/쓰기 분리가 양쪽에서 반복된다. Long Animation Frames API는 Ch18의 Long Tasks 관측의 애니메이션 버전이다.
- **Ch19(메모리 누수)**: rAF 루프의 취소(cancelAnimationFrame), will-change 제거는 Ch19의 "생성과 해제의 쌍" 원칙 그대로다. GPU 메모리 우상향 = 레이어 누수.
- **Ch20(CLS)**: transform이 레이아웃을 건드리지 않는다는 원리가 CLS 방지(토스트 애니메이션)와 60fps의 공통 기반이다.
- **Ch16(하이드레이션)**: 강제 동기 레이아웃 패턴(읽기/쓰기 분리)이 하이드레이션 진단에서 애니메이션 루프로 확장됐다.
- **Ch22(컴포넌트 최적화)**: 리액트 리렌더링과 애니메이션이 만나는 지점 — 상태 갱신 대신 ref + 직접 스타일 업데이트 같은 프레임워크 레벨 기법으로 이어진다.
- **Ch12(이미지)·Ch23(서드파티)**: GPU 메모리 관리 감각(레이어 크기)과 화면 밖 작업 중지(IntersectionObserver)가 리소스 관리 전반으로 연결된다.
