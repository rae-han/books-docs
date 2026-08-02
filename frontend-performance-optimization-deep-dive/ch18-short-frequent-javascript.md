# Chapter 18: 자바스크립트는 짧게 자주 실행해야 한다

## 핵심 질문

FCP 0.8초·LCP 1.2초·라이트하우스 90점인데 드롭다운이 펼쳐지는 데 0.5초 — 네트워크 요청도 없는 단순 상태 변경이 왜 느린가? 문제는 자바스크립트가 많아서가 아니라 **한 번에 너무 오래 실행되어서**다. 목표는 "적은 자바스크립트"가 아니라 **"메인 스레드를 50ms 이상 블로킹하지 않는 자바스크립트"** — 100ms 작업 1개보다 10ms 작업 10개가 낫다. 총 시간이 같아도 작업 사이사이에 브라우저가 입력을 처리할 기회가 생기기 때문이다.

## 1. 긴 작업과 메인 스레드 블로킹

### 1.1 긴 작업(Long Task)이란

브라우저는 싱글 스레드다. 메인 스레드가 자바스크립트 실행·DOM 조작·스타일 계산·레이아웃·페인트를 **순차적으로** 전부 처리한다. **긴 작업 = 메인 스레드를 50ms 이상 점유하는 작업.**

> **참고 — 왜 50ms인가**<br><br>HCI 연구(밀러 1968, 닐슨의 "응답 시간 3가지 한계")에서 사용자가 "즉각적"이라고 느끼는 임곗값은 100ms다. 그런데 자바스크립트가 끝나도 스타일 계산·레이아웃·페인트가 남는다. 구글은 100ms의 절반인 50ms를 JS 실행 상한으로 정했다 — JS 50ms + 렌더링 50ms = 100ms 안에 화면 갱신.

**이벤트 루프가 핵심 메커니즘이다.** 브라우저는 태스크 큐에서 작업을 하나씩 꺼내 실행하고, **각 태스크가 끝날 때마다** 렌더링과 입력 처리 기회를 얻는다. 400ms짜리 태스크가 실행 중이면 그동안 클릭 이벤트는 큐에 쌓이기만 한다 — Input Delay 300ms. 같은 작업을 50ms×8청크로 쪼개고 사이마다 양보하면 청크 경계에서 클릭이 처리된다 — Input Delay 47ms.

```
긴 작업:   [########## 400ms ##########]→클릭 처리     ← 100ms 시점 클릭이 400ms까지 대기
작업 분할: [50][50][50]→클릭 처리→[50][50]...          ← 청크 경계마다 이벤트 처리 기회
```

두 가지 오해를 바로잡자.

1. **번들 크기 ≠ 실행 시간**: 10KB 코드도 100만 번 반복하면 100ms가 걸리고, 100KB 코드도 데이터 100개만 순회하면 10ms에 끝난다. 번들 축소는 다운로드·파싱을 개선할 뿐 실행 시간 문제는 남는다.
2. **긴 작업은 누적된다**: 각 30ms인 작업 2개도 연속 실행되면 60ms 긴 작업이다. 사이에 양보를 넣어야 각각 30ms짜리 정상 작업이 된다.

실무 발생 예 — 전자상거래 "가격 낮은 순" 정렬: 5,000개 상품 × (할인율·배송비·재고 계산) 비교 연산 5만+ 회 → 중저사양 모바일에서 600~900ms. 게다가 `setProducts(sorted)` 후 5,000개 카드 리렌더링이 또 긴 작업을 만든다.

### 1.2 INP와 긴 작업의 관계

**INP = Input Delay(입력→핸들러 시작) + Processing Time(핸들러 실행) + Presentation Delay(DOM 업데이트→화면 표시).** 200ms 이하 좋음 / 200~500ms 개선 필요 / 500ms 이상 나쁨.

긴 작업은 **세 구간 전부**를 악화시킨다:

- 다른 작업 실행 중 클릭 → **Input Delay** 증가(600ms 긴 작업 중 클릭 = INP 600ms대).
- 클릭 핸들러 자체가 무거움 → **Processing Time** 증가(Input Delay 0이어도 필터링 150ms + 리렌더 100ms = INP 250ms).
- 무거운 DOM 업데이트 → **Presentation Delay** 증가.

작업 분할 실측: 5,000개 정렬을 1,000개씩 청크 + 양보로 바꾸면 INP 600ms → 71ms, **8배 개선**. 총 실행 시간은 비슷한데 사용자 경험이 달라진다. 검색 자동완성(타이핑마다 10,000개 필터링 → 커서 버벅임)은 디바운스로 해결한다(4절).

### 1.3 Performance 탭에서 긴 작업 찾기

녹화 → 문제 인터랙션 수행 → 정지. 확인 순서:

1. **Main 트랙의 빨간 삼각형** = 50ms 초과 작업. 호버하면 정확한 시간(예: "Long task took 355.22ms").
2. **함수 호출 스택 확대**: 블록 너비 = 실행 시간. `Task → onClick → filterProducts → Array.filter → expensiveCheck(750ms)` 식으로 병목 함수가 특정된다.
3. **Summary 파이 차트**: Scripting(노랑)이 높으면 JS 자체가 느림, Rendering(보라)이 높으면 DOM 조작·스타일이 무거움.

리액트 10,000개 리스트 사례: `loadItems`(배열 생성)는 빠르지만 `setItems` 후 리렌더링이 긴 작업 — 스택 최하단에 `appendChild` 1만 회, Summary는 Rendering 70%+. 이 경우 해법은 코드 분할이 아니라 **가상 스크롤**(화면에 보이는 20~30개만 렌더링, Ch22 상세)이다. 가상 스크롤 적용 후 녹화하면 긴 작업이 사라진다.

> **실무 팁**: 개발 장비는 너무 빠르다. Performance 설정(톱니바퀴)에서 **CPU 4x slowdown**을 켜고 측정하면 중저사양 모바일에서만 드러나는 긴 작업(20ms→80ms)이 보인다.

## 2. 긴 작업 분할과 scheduler.yield()

### 2.1 setTimeout 분할의 두 가지 문제

전통적 분할은 청크 처리 후 `await new Promise((resolve) => setTimeout(resolve, 0))`로 양보하는 것이다. 동작은 하지만:

1. **중첩 타이머 지연(Nested Timer Clamping)**: HTML 표준상 setTimeout이 5회 중첩되면 **최소 4ms 지연이 강제**된다. 청크 16개면 12개×4ms=48ms 낭비, 청크 100개면 384ms 낭비 — 청크가 늘수록 커진다.
2. **낮은 우선순위**: setTimeout 콜백은 태스크 큐 **맨 뒤**에 들어간다. 광고 스크립트가 계속 태스크를 추가하면 내 연속 작업이 그 뒤로 밀려 5초짜리 작업이 10초+ 걸릴 수 있다.

### 2.2 scheduler.yield() — 우선순위가 보장되는 양보

크롬 129+/엣지 129+/파이어폭스 142+에서 지원(사파리 미지원). `await scheduler.yield()` 시점에 함수가 일시 중지되고 메인 스레드가 양보된다. 핵심 차이: **연속 작업(continuation)이 같은 우선순위 큐의 앞쪽에 배치**되어 서드파티 태스크보다 먼저 실행된다(우선순위가 올라가는 게 아니라 큐 앞쪽 삽입).

```ts
async function processItemsWithYield(items: Item[]) {
  const CHUNK_SIZE = 625; // 625개 × 0.08ms ≈ 50ms
  for (let i = 0; i < items.length; i += CHUNK_SIZE) {
    const chunk = items.slice(i, i + CHUNK_SIZE);
    chunk.forEach((item) => { complexCalculation(item); });
    await scheduler.yield(); // 브라우저가 입력·렌더링 처리 후 즉시 복귀
  }
}
```

**대표 사용 사례 — 즉각적인 UI 피드백**: 클릭 핸들러에서 스피너를 먼저 표시하고 `await scheduler.yield()`로 브라우저가 그리게 한 뒤 무거운 작업을 시작한다. yield 없이는 스피너가 그려지기 전에 메인 스레드가 막혀 사용자가 클릭 피드백을 못 본다.

프로덕션에서는 기능 감지 + 폴백이 필수다:

```ts
async function yieldToMain(): Promise<void> {
  if ('scheduler' in window && 'yield' in scheduler) {
    return scheduler.yield();
  }
  return new Promise((resolve) => setTimeout(resolve, 0));
}
```

더 정교한 폴백이 필요하면 `scheduler-polyfill` 패키지(setTimeout + MessageChannel + requestIdleCallback 조합, 단 완전한 우선순위 상속은 불가). 타입스크립트 타입은 `@types/wicg-task-scheduling`.

### 2.3 scheduler.postTask() — 우선순위 지정 스케줄링

Scheduler API의 다른 축. `yield()`가 **분할**이라면 `postTask()`는 **우선순위와 함께 태스크를 예약**한다.

- `user-blocking`: 클릭 핸들러·키 입력 처리 — 최고 우선순위
- `user-visible`(기본): 화면 업데이트·데이터 로딩
- `background`: 분석 전송·캐시 갱신·프리페칭 — 유휴 시간

`postTask()` 안에서 `yield()`를 호출하면 **연속 작업이 그 우선순위를 상속**한다(background로 예약한 루프는 yield 후에도 background 유지 — 우선순위 역전 방지). 단독 `yield()`는 기본 `user-visible`. 그리고 `signal: controller.signal`을 넘기면 **AbortController로 진행 중인 긴 작업을 취소**할 수 있다 — yield 지점에서 Promise가 거부되어 대용량 작업에 "취소" 버튼을 제공할 때 유용하다.

### 2.4 실전: 대량 데이터 렌더링

가상 스크롤을 못 쓰는 상황에서 검색 결과 5,000행 테이블(행당 ~0.2ms 포매팅 = 1,000ms 긴 작업)을 렌더링한다면:

```ts
async function renderSearchResultsOptimized(results: SearchResult[]) {
  const tbody = document.querySelector('#results-table tbody')!;
  tbody.innerHTML = '';
  const CHUNK_SIZE = 250; // 250개 × 0.2ms = 50ms

  for (let i = 0; i < results.length; i += CHUNK_SIZE) {
    const chunk = results.slice(i, i + CHUNK_SIZE);
    const fragment = document.createDocumentFragment(); // 리플로우 최소화
    chunk.forEach((result) => { fragment.appendChild(createResultRow(result)); });
    tbody.appendChild(fragment);
    await scheduler.yield();
  }
}
```

- **청크 크기**: 각 청크가 30~50ms 걸리도록 실측으로 조정. 기기마다 다르므로 **적응형 청킹**도 유효 — 청크 처리 시간을 재서 목표(40ms)보다 길면 20% 줄이고 절반 이하면 20% 늘린다(고성능 데스크톱은 큰 청크, 저사양 모바일은 작은 청크로 자동 수렴).
- **진행률 표시**: 청크마다 프로그레스 바 업데이트 — 양보 덕분에 실제로 그려진다.
- **트레이드오프**: 총 시간은 약간 늘 수 있다(실측 987ms→1,042ms — yield 오버헤드 + 태스크 전환 비용). 대신 작업 중 클릭이 50ms 안에 반응한다.

### 2.5 분할 시 주의사항

- **과도한 yield 금지**: 호출당 0.1~0.5ms 오버헤드. 아이템마다 yield하지 말고 **~50ms 분량(예: 500개)마다** 또는 시간 기반(`performance.now() - lastYield > 50`)으로.
- **`isInputPending()`은 비권장**: 감지가 부정확하고, 입력이 없어도 렌더링을 위해 주기적으로 양보해야 하며, scheduler.yield()가 이미 우선순위 문제를 해결했다. 단순히 일정 간격 yield가 최선이다.
- **동기→비동기 전환 파급**: yield를 넣으면 함수가 async가 되므로 호출부도 `await`로 바꿔야 하고 에러 처리도 달라진다.
- scheduler.yield()는 **웹 워커 안에서도** 사용 가능 — 워커 내부 메시지 처리를 원활하게 한다.

## 3. requestIdleCallback으로 급하지 않은 작업 미루기

### 3.1 동작 원리

`scheduler.yield()`가 작업을 **잠깐 멈추는** 도구라면, `requestIdleCallback()`은 작업 자체를 **브라우저가 한가할 때까지 미루는** 도구다. 60fps 기준 프레임당 16.67ms — 렌더링이 10ms에 끝나면 남은 ~6.67ms의 **유휴 시간**에 콜백이 실행된다.

콜백은 `deadline` 객체를 받는다: `timeRemaining()`(남은 유휴 시간, **최대 50ms** — 입력 지연 방지 안전장치)과 `didTimeout`(타임아웃 강제 실행 여부).

**최대 약점: 실행 보장이 없다.** 애니메이션·스크롤 중에는 유휴 시간이 없어 콜백이 몇 초~몇 분 지연될 수 있다. 그래서 **필수 작업에는 반드시 `timeout` 옵션**을 설정한다:

- 분석 데이터 전송: 2~5초(이탈 전 전송 보장) / 로그: 5~10초 / 캐시 정리: 10~30초 / 프리페칭: 1~2초

그리고 **콜백 자체가 긴 작업이 되면 본말전도**다 — `timeRemaining()`을 확인하며 작업 큐를 하나씩 처리하고, 남으면 재예약하는 패턴을 쓴다:

```ts
function processTasksInIdle() {
  requestIdleCallback(
    (deadline) => {
      while (deadline.timeRemaining() > 0 && tasksQueue.length > 0) {
        const task = tasksQueue.shift()!;
        task();
      }
      if (tasksQueue.length > 0) {
        processTasksInIdle(); // 남은 작업은 다음 유휴 시간에
      }
    },
    { timeout: 5000 },
  );
}
```

### 3.2 실전 활용

**분석 데이터 전송** — 이벤트 발생과 전송을 분리한다. 클릭 핸들러는 큐에 push만 하고 즉시 반환, 유휴 시간에 10개씩 배치로 `navigator.sendBeacon('/analytics', ...)` 전송. sendBeacon은 페이지 종료 시에도 브라우저가 백그라운드 전송을 보장한다(일반 fetch는 취소될 수 있음).

**로그 수집** — 큐가 100개 차면 즉시 flush, 아니면 유휴 시간에(timeout 5초). `fetch(..., { keepalive: true })`로 언로드 후에도 전송 시도. 실패 로그는 재시도하지 않는다(무한 루프 방지).

**프리페칭** — 링크 `mouseenter` 시 유휴 시간에 `<link rel="prefetch">`를 동적 추가(timeout 1초). 클릭 전에 리소스가 캐시된다.

공통 원칙: **급한 작업(입력 피드백)과 급하지 않은 작업(분석·로그·프리페치)을 구분**하고, 후자를 유휴 시간으로 밀어 메인 스레드를 비운다.

### 3.3 사파리 미지원 대응

사파리(점유율 ~17%)는 requestIdleCallback을 기본 비활성 실험 기능으로만 제공한다. 프로덕션에는 기능 감지 + 폴백이 필수다.

- **간단한 폴백**: `setTimeout`으로 예약하고 deadline 객체를 흉내(`timeRemaining()`이 잔여 ~50ms 반환). 유휴 시간 활용은 못 하지만 코드는 동작한다.
- **정교한 폴백**: `requestAnimationFrame`으로 프레임 시작 시각을 얻고(`frameDeadline = rafTime + 16.67`), rAF 콜백에서 직접 일하지 않고 `setTimeout(fn, 0)`으로 **렌더링(스타일·레이아웃·페인트) 이후 시점**에 실행을 예약한다. 그 시점의 `frameDeadline - performance.now()`가 유휴 시간 추정치다. 프레임 드롭·백그라운드 탭에서는 정확도가 떨어지므로 검증된 폴리필 패키지 사용도 고려한다.

프로덕션 체크 4가지: ① 필수 작업엔 timeout ② 콜백도 짧게(timeRemaining 확인) ③ 사파리 폴백이 오히려 INP를 해치지 않는지 테스트 ④ Performance 탭 Idle 구간으로 실제 유휴 시간 확인(애니메이션 많은 페이지는 유휴가 없어 효과도 없다).

## 4. 이벤트 리스너 최적화

스크롤은 초당 60~120회, touchmove·wheel은 초당 수백 회 발생한다. 핸들러가 5ms만 걸려도 긴 작업이 된다. 세 가지 기법: **디바운스**(빈도를 "마지막 1회"로), **스로틀**(빈도를 "간격당 1회"로), **패시브 리스너**(스크롤 차단 자체를 제거).

### 4.1 디바운스 vs 스로틀

- **디바운스**: 마지막 이벤트 후 delay가 지나면 **1번만** 실행. 이벤트가 계속 발생하는 동안은 실행되지 않는다. → "행동이 **끝난 후** 반응": 검색 입력, 폼 검증, 윈도우 리사이즈, 자동 저장.
- **스로틀**: 아무리 이벤트가 와도 **delay 간격당 최대 1번** 실행. → "행동이 **진행되는 동안** 일정 간격 반응": 스크롤 위치 추적, 무한 스크롤, 마우스 이동, 게임 입력.

```ts
function debounce<T extends unknown[]>(func: (...args: T) => void, delay: number) {
  let timeoutId: ReturnType<typeof setTimeout>;
  return function (this: unknown, ...args: T) {
    clearTimeout(timeoutId);              // 새 이벤트가 오면 이전 타이머 취소
    timeoutId = setTimeout(() => { func.apply(this, args); }, delay);
  };
}

function throttle<T extends unknown[]>(func: (...args: T) => void, delay: number) {
  let lastCall = 0;
  return function (this: unknown, ...args: T) {
    const now = Date.now();
    if (now - lastCall >= delay) {        // 충분한 시간이 지났을 때만 실행
      lastCall = now;
      func.apply(this, args);
    }
  };
}
```

50ms 간격 이벤트 6번에 대해: 디바운스(300ms)는 마지막 이벤트 후 300ms 뒤 **1회**, 스로틀(100ms)은 100ms마다 총 **3회** 실행된다.

### 4.2 검색 입력 최적화(디바운스)

"javascript performance" 22글자 = input 이벤트 22번 = API 22회. 디바운스 300ms로 타이핑이 멈춘 후 1회만 호출한다. 최소 2글자 미만은 검색하지 않고, 로딩 인디케이터로 피드백을 준다.

남는 문제는 **응답 순서 역전**이다 — 'java' 검색 후 'javascript'를 이어 치면 두 요청이 나가고, 먼저 요청의 응답이 늦게 도착하면 잘못된 결과가 덮는다. **AbortController로 이전 요청을 취소**한다:

```ts
let currentController: AbortController | null = null;

const debouncedSearch = debounce(async (query: string) => {
  if (currentController) {
    currentController.abort(); // 이전 요청 취소
  }
  currentController = new AbortController();
  try {
    const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`, {
      signal: currentController.signal,
    });
    if (!currentController.signal.aborted) {
      displayResults((await response.json()).results);
    }
  } catch (error) {
    if ((error as Error).name !== 'AbortError') { // 의도적 취소는 무시
      displayError('검색에 실패했습니다');
    }
  }
}, 300);
```

추가 고려: 같은 검색어 재입력에 대비한 **메모리 캐시**(Map + 크기 제한), 지연 시간 조정(빠른 응답 200ms ↔ 서버 부하 절감 500ms).

### 4.3 스크롤 이벤트 최적화(스로틀)

- **무한 스크롤**: 100ms 스로틀로 하단 200px 도달을 확인 → `isLoading` 플래그로 중복 로드 방지 → 마지막 페이지 도달 시 **리스너 제거**. 실패 시 페이지 번호 롤백.
- **"맨 위로" 버튼 표시/숨김, 현재 섹션 하이라이트**: 100ms마다 스크롤 위치를 읽어 클래스 토글.
- 간격 선택: 100ms(초당 10회)가 기본, 50ms는 더 부드럽지만 부담 증가, 200ms는 끊겨 보일 수 있다 — 실기기에서 조정.

### 4.4 패시브 이벤트 리스너

디바운스·스로틀이 실행 **빈도**를 줄인다면, 패시브 리스너는 **스크롤 차단 대기 자체**를 없앤다. 브라우저는 터치/휠 핸들러가 `preventDefault()`를 호출할지 알 수 없어 **핸들러 실행이 끝날 때까지 스크롤을 지연**시킨다 — 핸들러가 100ms면 스크롤이 100ms 밀린다.

`{ passive: true }`는 "이 핸들러는 preventDefault를 호출하지 않는다"는 약속이다. 브라우저는 기다리지 않고 즉시 스크롤을 시작하고 핸들러는 병행 실행된다.

```ts
// ✅ 터치 스와이프 갤러리 — 모든 터치 이벤트에 passive
gallery.addEventListener('touchmove', (e) => {
  currentX = e.touches[0].clientX;
  gallery.style.transform = `translateX(${currentX - startX}px)`;
}, { passive: true });
```

- 적용 대상: `touchstart`·`touchmove`·`touchend`·`wheel`. (`scroll` 이벤트는 원래 preventDefault로 막을 수 없어 이미 passive처럼 동작 — 명시 불필요.)
- 크롬은 passive 없는 터치 리스너에 `[Violation] Added non-passive event listener...` 콘솔 경고를 낸다.
- **패시브 리스너 안의 preventDefault()는 무시**되고 경고가 뜬다. 스크롤 방향 제한, 드래그 앤드 드롭, 커스텀 스크롤처럼 조건부 preventDefault가 필요하면 passive를 쓰지 않는다.
- 저사양 모바일에서 특히 효과가 크다 — 옵션 하나로 얻는 가장 값싼 개선.

## 5. 웹 워커로 메인 스레드 부담 줄이기

### 5.1 동작 원리

앞의 기법들은 전부 **여전히 메인 스레드에서** 실행된다. 1만 행 CSV 파싱, 4K 이미지 필터, SHA-256 해싱은 아무리 쪼개도 메인 스레드를 쓴다. 웹 워커는 **별도 스레드**에서 자바스크립트를 실행해 메인 스레드를 완전히 비운다 — 워커가 3초 계산하는 동안 메인 스레드는 클릭에 즉시 응답한다.

- 통신은 `postMessage`/`onmessage`. 워커는 `window`·`document`·DOM API 접근 불가, 대신 `console`·`fetch`·`setTimeout`·IndexedDB는 사용 가능.
- 별도 파일 대신 **Blob URL 인라인 워커** + **Promise 래퍼**(execute/terminate)로 감싸면 일반 비동기 함수처럼 쓸 수 있다.

```ts
// Promise 기반 워커 래퍼의 사용 모습
const result = await myWorker.execute('parse-csv', { csvText });
```

### 5.2 워커로 옮기기 좋은 작업 vs 나쁜 작업

| 적합 | 예시·근거 |
|---|---|
| 대용량 데이터 파싱·처리 | 10MB+ JSON/CSV, 수천 건 필터·정렬(1만 행 CSV 파싱 200ms → 메인 스레드 0ms) |
| 이미지·비디오 처리 | 4K = 800만 픽셀 필터(grayscale·blur), 리사이징 — 쉽게 100ms+ |
| 암호화·해싱 | SHA-256 10MB 해싱 100~200ms |
| 복잡한 계산 | 통계(백분위수), 경로 찾기(A*), 물리 시뮬레이션 |

| 부적합 | 이유 |
|---|---|
| DOM 조작 필요 | 워커는 document 접근 불가 — 읽기는 메인에서, 결과 반영도 메인에서 |
| 작고 빠른 작업(<10ms) | 워커 생성(5~10ms) + 직렬화 오버헤드가 작업보다 큼 |
| 빈번한 통신 | 프레임마다 postMessage = 초당 60회 직렬화 누적 |
| 즉시 결과 필요 | 워커는 비동기 — 동기적 결과가 필요하면 메인에서 |

판단 기준: **Performance 탭에서 50ms 이상 긴 작업으로 나타나면 워커 후보.** 50ms 미만이라도 자주 반복되면 고려할 만하다.

### 5.3 실전과 주의사항

**CSV 파싱 워커**: 파일 업로드 → `file.text()` → 워커에서 파싱 → 메인 스레드는 로딩 인디케이터를 부드럽게 돌리며 클릭에 응답.

**이미지 그레이스케일 워커 + 전송 가능 객체(Transferable Objects)**: `postMessage(data, [imageData.data.buffer])` — 두 번째 인자로 버퍼를 넘기면 **복사 대신 소유권만 이전**한다. 4K 픽셀 데이터 ~30MB를 구조화된 복제로 복사하면 그 자체가 50ms+ 작업이지만, Transferable은 비용이 거의 0이다. `ArrayBuffer`·`MessagePort`·`ImageBitmap`·`OffscreenCanvas`가 해당하며, **전송 후 원본은 사용 불가**(`buffer.byteLength === 0`)가 된다.

주의사항 정리:

1. **직렬화 오버헤드**: 큰 일반 객체의 postMessage는 구조화된 복제로 느리다 — 큰 데이터는 반드시 Transferable.
2. **디버깅**: 워커는 별도 스레드 — 개발자 도구 Sources에서 워커 파일을 따로 열어야 콘솔·중단점 확인.
3. **호환성**: 기본 전용 워커(Dedicated Worker)는 2010년부터 사실상 전 브라우저 지원(IE 10+) — 걱정 불필요.
4. **워커 생성 비용(5~10ms)**: 작업마다 생성·종료하지 말고 **하나의 워커를 재사용**한다. 워커 풀은 대부분 과잉 — 복잡성만 늘린다.

사용 조건 4가지를 모두 만족할 때 워커를 쓴다: ① CPU 집약 50ms+ ② DOM 불필요 ③ 데이터가 작거나 Transferable 가능 ④ 워커 재사용 가능. 아니면 scheduler.yield()·requestIdleCallback을 먼저 고려한다.

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|---|---|---|
| 번들만 줄이고 실행 최적화 생략 | 번들 크기 ≠ 실행 시간 — 10KB도 100만 루프면 100ms | Performance 탭으로 긴 작업 측정 후 분할 |
| 대량 데이터를 한 번에 정렬·필터·렌더링 | 400~1,000ms 긴 작업 — 클릭·스크롤 전부 무시됨 | 30~50ms 청크 + scheduler.yield() (또는 가상 스크롤) |
| setTimeout(0)으로만 작업 분할 | 5회 중첩부터 4ms 강제 지연 누적 + 서드파티 태스크에 밀림 | scheduler.yield() 우선 + 기능 감지 폴백 |
| 무거운 작업 전에 UI 피드백 양보 없음 | 스피너 표시 코드가 있어도 그려지기 전에 블로킹 | 피드백 표시 → `await scheduler.yield()` → 작업 시작 |
| 아이템마다 yield 호출 | 호출당 0.1~0.5ms 오버헤드만 누적 | ~50ms 분량(수백 개)마다 또는 시간 기반 yield |
| isInputPending()으로 조건부 양보 | 감지 부정확 + 렌더링 기회도 필요 | 일정 간격 무조건 yield |
| rIC에 timeout 없이 필수 작업 예약 | 바쁜 페이지에서 몇 분간 미실행 — 분석 데이터 유실 | 필수 작업엔 timeout 2~5초 |
| rIC 콜백에서 무제한 작업 | 유휴 시간(최대 50ms) 초과 — 콜백 자체가 긴 작업 | timeRemaining() 확인 + 남은 작업 재예약 |
| 타이핑마다 API 호출 | 22글자 = 22요청 + 응답 순서 역전 | 디바운스 300ms + AbortController 취소 |
| 스크롤 핸들러 매 이벤트 실행 | 초당 수십 회 × 무거운 계산 = 메인 스레드 포화 | 스로틀 100ms (또는 IntersectionObserver) |
| 터치/휠 리스너에 passive 누락 | 핸들러 종료까지 스크롤 지연 — 버벅임 | `{ passive: true }` (preventDefault 필요 시 제외) |
| 패시브 리스너에서 preventDefault() | 무시됨 + 콘솔 경고 — 의도한 동작 안 함 | 조건부 취소가 필요하면 passive 제거 |
| 작은 작업까지 워커로 이동 | 생성 5~10ms + 직렬화 비용 > 작업 시간 | 50ms+ CPU 집약 작업만 워커로 |
| 워커에 큰 객체를 일반 postMessage | 구조화된 복제 자체가 50ms+ | Transferable(ArrayBuffer 등)로 소유권 이전 |
| 작업마다 워커 생성·종료 | 생성 비용 반복 | 워커 재사용 |

## 측정과 검증

- **Performance 탭**: Main 트랙 빨간 삼각형(50ms+) → 함수 스택으로 병목 특정 → Summary(Scripting vs Rendering)로 원인 분류. **CPU 4x slowdown** 필수.
- **INP 분해**: Input Delay / Processing Time / Presentation Delay 중 어디가 큰지 확인 — 각각 다른 처방(분할 / 핸들러 경량화·디바운스 / 렌더링 최적화).
- **최적화 전후 재측정**: 총 실행 시간이 아니라 **긴 작업 유무와 INP**로 판단한다(분할하면 총 시간은 오히려 약간 는다).
- **리액트 Profiler**: 리렌더링이 병목일 때 컴포넌트 단위 시간 확인.
- **콘솔 Violation 경고**: non-passive listener 경고 확인.
- **RUM**: web-vitals `onINP`로 실사용자 INP 분포 — 필드에서 200ms 이하 확인.
- **지속 모니터링**: 성능 예산 + 라이트하우스 CI로 INP·TBT 회귀 감시 — 새 기능마다 긴 작업은 다시 생긴다.

## 체크리스트

**긴 작업 분석 및 제거**

- [ ] Performance 탭에서 긴 작업 확인(CPU 4x 스로틀링 포함)
- [ ] 50ms 이상 걸리는 작업 분할
- [ ] scheduler.yield()(폴백: setTimeout)로 메인 스레드 양보
- [ ] 무거운 작업 전 UI 피드백 표시 후 yield

**작업 우선순위 관리**

- [ ] 급한 작업(UI 업데이트·사용자 피드백)은 즉시 실행
- [ ] 급하지 않은 작업(분석·로깅·프리페치)은 requestIdleCallback으로 미루기
- [ ] 필수 작업에는 timeout 설정(분석 2~5초)
- [ ] scheduler.postTask() 우선순위(user-blocking/user-visible/background) 활용

**이벤트 최적화**

- [ ] 검색 입력에 디바운스 적용(300ms) + AbortController로 이전 요청 취소
- [ ] 스크롤 이벤트에 스로틀 적용(100ms) 또는 IntersectionObserver 사용
- [ ] 터치·휠 이벤트에 `{ passive: true }` 적용
- [ ] 조건부 preventDefault가 필요한 곳은 passive 제외 확인

**웹 워커 활용**

- [ ] CPU 집약 작업(50ms+)을 워커로 이동(파싱·암호화·이미지 처리)
- [ ] 대용량 데이터는 Transferable Objects로 전송
- [ ] 워커 재사용(작업마다 생성 금지)
- [ ] DOM 의존 작업은 워커 대상에서 제외

**검증**

- [ ] 최적화 전후 Performance 녹화 비교(긴 작업 유무)
- [ ] INP 200ms 이하 확인(랩 + 필드)
- [ ] 라이트하우스 CI로 INP·TBT 지속 모니터링

## 요약

- 문제의 본질: 브라우저는 싱글 스레드이고, **50ms 이상의 긴 작업**은 그동안의 모든 입력을 무시하게 만든다(100ms 즉각 반응 임곗값의 절반 = JS 몫). 번들 크기와 실행 시간은 별개이고, 짧은 작업도 연속 실행되면 긴 작업으로 누적된다.
- **INP = Input Delay + Processing Time + Presentation Delay** — 긴 작업은 세 구간을 모두 악화시킨다. 작업 분할만으로 INP 600ms → 71ms(8배)가 실측된다. 총 시간이 아니라 "브라우저가 끼어들 기회"가 체감을 결정한다.
- 진단은 Performance 탭: 빨간 삼각형 → 함수 스택(너비 = 시간) → Summary(Scripting/Rendering 비율). CPU 4x 스로틀링으로 중저사양을 재현한다.
- **다섯 가지 도구**: ① `scheduler.yield()` — 청크 사이 양보, continuation이 큐 앞쪽 배치라 setTimeout(4ms 중첩 지연 + 맨 뒤 배치)보다 우수. 사파리 미지원이라 폴백 필수. ② `requestIdleCallback` — 급하지 않은 작업(분석·로그·프리페치)을 유휴 시간으로, 필수 작업엔 timeout. sendBeacon/keepalive로 이탈 시 전송 보장. ③ **디바운스** — 행동이 끝난 후 1회(검색·검증·리사이즈), AbortController와 조합. ④ **스로틀** — 진행 중 간격당 1회(스크롤·무한 스크롤). ⑤ **패시브 리스너** — preventDefault 안 한다는 약속으로 스크롤 차단 제거.
- **웹 워커**는 근본 해법 — CPU 집약 작업을 별도 스레드로. 단 조건부: 50ms+ / DOM 불필요 / Transferable 가능 / 재사용. 큰 데이터는 소유권 이전(Transferable)으로 직렬화 비용을 0으로.
- 기법들은 조합이 정답이다: 검색 자동완성 = 디바운스(입력) + 워커(10,000개 필터링) + yield 청크 렌더링(결과 표시) — 전 단계에서 메인 스레드가 자유롭다.
- 전부 표준 브라우저 API다 — 라이브러리 불필요. 측정 → 적용 → 재측정, 그리고 성능 예산 + CI로 지속 감시한다.

## 다른 챕터와의 관계

- **Ch16(하이드레이션)**: 하이드레이션도 결국 긴 작업이다 — Ch16의 강제 동기 레이아웃·긴 작업 신호가 이 장의 일반론으로 확장된다. TTI 이후의 인터랙션 성능을 이 장이 담당한다.
- **Ch17(데이터 캐싱)**: 낙관적 업데이트로 네트워크 대기를 없애도 메인 스레드가 막히면 INP는 나쁘다 — 두 장이 INP의 네트워크 축과 실행 축을 나눠 맡는다. 디바운스+AbortController는 Ch17의 경쟁 조건 해법과 동일 패턴이다.
- **Ch19(메모리 누수)**: 실행이 짧아도 메모리가 쌓이면 GC가 메인 스레드를 멈춘다 — 실행 최적화의 다음 짝.
- **Ch20(CLS)·Ch21(애니메이션)**: Presentation Delay와 프레임 예산(16.67ms)의 세계 — 렌더링 파이프라인 관점을 이어받는다.
- **Ch22(컴포넌트 최적화)**: 리액트 리렌더링이 만드는 긴 작업(10,000개 리스트)의 프레임워크 레벨 해법(가상 스크롤·메모이제이션)을 다룬다.
- **Ch23(서드파티)**: setTimeout 분할이 서드파티 태스크에 밀리는 문제의식이 서드파티 통제 전략으로 이어진다.
