# Chapter 19: 메모리 누수는 코드가 아니라 생명주기의 문제다

## 핵심 질문

"새로고침하면 빨라져요" - 처음 5분은 50ms에 반응하던 앱이 30분 후 300ms, 1시간 후엔 스크롤까지 버벅인다. Performance Monitor의 JS Heap Size는 50MB에서 250MB로 우상향한다. 코드는 정확하게 동작하는데 왜 메모리가 쌓이는가? 답은 **생명주기** - 등록한 리스너·타이머·구독을 컴포넌트가 사라질 때 해제하지 않았기 때문이다. 목표는 "메모리를 덜 쓰는 것"이 아니라 **"쓴 메모리를 제때 해제하는 것"**, 즉 "처음 1분만 빠른 앱"이 아니라 **"1시간 후에도 빠른 앱"**이다.

> **핵심 통찰**: 메모리 누수는 INP를 직접 악화시킨다. 메모리가 증가하면 가비지 컬렉터가 더 자주·더 오래 실행되고(Major GC 수십~수백 ms), 각 실행이 메인 스레드를 블로킹한다. 힙 250MB에서 GC 50~100ms가 도는 순간 클릭하면 INP는 즉시 100ms를 넘는다. Ch18의 긴 작업 분할이 **순간의 반응성**이라면, 메모리 관리는 **장시간의 안정성** - 런타임 성능의 양대 축이다.

이 장의 패턴은 프레임워크 무관이다 - 리액트 `useEffect` 정리 함수, 뷰 `onUnmounted`, 스벨트 `onDestroy`, 앵귤러 `ngOnDestroy`, 솔리드 `onCleanup`은 문법만 다를 뿐 "컴포넌트가 사라질 때 리소스를 정리하라"는 같은 역할이다. 그리고 **SPA에서 특히 치명적**이다 - MPA는 페이지 이동마다 전체 새로고침으로 자동 정리되지만, SPA는 클라이언트 라우팅이라 명시적으로 정리하지 않으면 10개 페이지를 이동하면 10개 페이지의 리소스가 전부 쌓인다.

## 1. 메모리 누수가 발생하는 전형적인 5가지 패턴

### 1.1 이벤트 리스너 미제거 - 가장 흔한 패턴

전역 객체(`window`·`document`)에 등록한 리스너는 컴포넌트가 언마운트되어도 남는다. 모달을 10번 열고 닫으면 10개의 리스너가 누적된다.

```tsx
useEffect(() => {
  function handleEscape(e: KeyboardEvent) {
    if (e.key === 'Escape') {
      onClose();
    }
  }
  window.addEventListener('keydown', handleEscape);
  return () => {
    window.removeEventListener('keydown', handleEscape); // 이 한 줄이 없으면 누수
  };
}, [onClose]);
```

연쇄 효과가 더 무섭다 - `handleEscape`는 클로저로 `onClose`를 참조하고, `onClose`는 외부 컴포넌트의 상태를 참조한다. **리스너 하나가 수십 MB를 붙잡을 수 있다.** 힙 스냅샷의 Retainer 경로로 보면 `window → EventTarget → handleEscape → onClose`로 이어진다.

> **참고 - 익명 함수는 제거할 수 없다**<br><br>`removeEventListener`에 전달하는 함수는 `addEventListener`에 전달한 것과 **정확히 같은 참조**여야 한다. 등록과 해제에 각각 익명 함수를 쓰면 내용이 같아도 다른 객체라서 아무것도 제거되지 않는다 - 정리 함수가 있어 보여도 누수는 그대로다.

### 1.2 타이머와 인터벌 미정리

`setTimeout` 콜백은 만료까지, `setInterval`은 **영원히** 메모리에 남는다. 콜백이 캡처한 클로저도 함께 유지된다. 컴포넌트 언마운트 후 실행된 콜백의 setState는 리액트 18+에서 무시되지만(17까지는 경고 출력, 18부터 거짓 양성 문제로 제거) **타이머와 클로저 참조는 계속 누수를 만든다.** `LiveTimer`를 10번 마운트하면 10개의 인터벌이 동시에 돈다.

해법: `clearTimeout` / `clearInterval` / `cancelAnimationFrame` - 설정과 취소의 쌍(3절 상세).

### 1.3 Detached DOM 노드

DOM에서 제거됐지만 자바스크립트 변수가 여전히 참조하는 노드. 전역 변수에 `modalRef.current`를 저장하면 모달이 닫혀도 GC되지 않는다 - 10번 여닫으면 10개의 Detached DOM 트리.

- 전역 상태에 DOM 노드를 꼭 저장해야 한다면 정리 함수에서 `null` 할당.
- 이벤트 핸들러에서 `e.target`(DOM 노드)을 상태 배열에 저장하는 패턴도 같은 문제 - 리렌더링 후 이전 노드들이 Detached로 쌓인다.

> **핵심 통찰**: **DOM 노드를 저장하지 말고 노드에서 필요한 데이터만 추출해 저장하라.** 이미지면 `src`만, 버튼이면 `textContent`만. DOM 노드 자체는 프레임워크가 관리하게 두고 개발자는 데이터만 다룬다.

### 1.4 클로저에 의한 누수

함수가 외부 스코프의 변수를 참조하면 그 변수는 함수가 살아있는 동안 유지된다. 10MB `rawData`를 가져온 뒤 `setInterval` 콜백에서 `rawData.length`를 로깅하면 - 실제 필요한 건 길이 하나인데 **전체 10MB 배열이 캡처**된다. 페이지 10번 방문 = 100MB.

해법: **필요한 값만 별도 상태로 추출**(`dataLength`)하고 콜백은 그것만 참조. 그리고 오래된 클로저(stale closure) 문제 - 의존성 빈 배열의 핸들러가 마운트 시점 `count`를 캡처하는 버그 - 는 **함수형 업데이트**(`setCount((prev) => prev + 1)`)로 해결한다. 최신 상태를 인자로 받으므로 클로저가 낡은 값을 붙잡지 않고, 의존성 재등록도 불필요하다.

### 1.5 무한히 증가하는 캐시와 전역 상태

캐싱은 성능 최적화의 핵심이지만 만료 정책이 없으면 누수다. 이미지 100개 × 1MB를 전역 `Map`에 영원히 저장하면 100MB.

- **LRU 캐시로 크기 제한**: Map의 삽입 순서 보장을 활용 - `get()` 시 삭제 후 재삽입으로 "최근 사용" 갱신, 가득 차면 `keys().next().value`(가장 오래된 키) 제거. 실무에서는 `lru-cache` 패키지(max 개수 + maxSize 바이트 + TTL 지원).
- **전역 상태도 상한선**: 알림 배열은 최대 50개 유지, 넘치면 오래된 것부터 `shift()`.

다섯 패턴의 공통 원칙은 하나다 - **생성과 해제의 쌍.** 등록했으면 제거, 설정했으면 취소, 시작했으면 해제, 추가했으면 만료.

## 2. useEffect 정리 함수의 올바른 사용

### 2.1 정리 함수는 두 시점에 실행된다

흔한 오해: "정리 함수 = 언마운트 때만". 실제로는 ① 언마운트 시 + ② **의존성이 변경되어 이펙트가 재실행되기 직전**. 두 번째를 놓치면 `userId`가 1→2→3으로 바뀔 때 구독 3개가 전부 활성화된다. 정리 함수가 있으면 리액트는 "이전 구독 해제 → 새 구독 생성"을 반복해 **항상 하나의 구독만** 유지한다.

### 2.2 비동기 작업과 경쟁 상태

'react'를 검색하고 응답 전에 'vue'로 바꾸면 두 요청이 동시에 진행되고 응답 순서가 보장되지 않는다 - 'vue' 응답 후 'react' 응답이 도착하면 잘못된 결과가 화면을 덮는다.

```tsx
useEffect(() => {
  const controller = new AbortController();

  async function fetchResults() {
    try {
      const data = await fetch(`/api/search?q=${query}`, { signal: controller.signal });
      setResults(await data.json());
    } catch (error) {
      if ((error as Error).name === 'AbortError') {
        return; // 의도적 취소는 무시
      }
      throw error;
    }
  }
  fetchResults();

  return () => {
    controller.abort(); // 진행 중인 요청 자체를 취소
  };
}, [query]);
```

간단한 대안은 `let cancelled = false` 플래그 + `if (!cancelled) setResults(...)`이지만, AbortController는 **네트워크 요청 자체를 취소**해 대역폭·서버 리소스까지 아낀다.

### 2.3 커스텀 훅과 의존성 배열

- **커스텀 훅에도 정리 함수 필수**: `useWindowSize`가 resize 리스너를 정리하지 않으면 훅을 쓰는 모든 컴포넌트가 누수를 상속한다. 훅에서 정리하면 사용자는 신경 쓸 필요가 없다 - 캡슐화의 힘.
- **의존성에는 원시 값만**: 부모가 렌더링마다 `user={{ id: 123, ... }}` 새 객체를 만들면 참조 비교로 이펙트가 매번 재실행 - 채팅 연결이 계속 끊겼다 붙는다. `userId` 같은 원시 값을 프롭으로 받거나, 이펙트 밖에서 `const userId = user.id`로 추출해 의존성에 넣는다(또는 부모에서 `useMemo`).
- **정리 함수에서 하지 말 것**: 상태 업데이트·새 부수 효과. 리스너 제거·타이머 취소·연결 종료 같은 **정리 작업만** 단순하게. 복잡한 로직이 필요하다면 이펙트 설계 자체를 재검토하라는 신호다.

## 3. 타이머와 인터벌 관리

### 3.1 setTimeout - ID 저장 후 clearTimeout

query 변경마다 이전 타이머를 취소하고 새로 설정하면 마지막 입력에 대한 요청만 실행된다. 이것이 디바운스 훅의 정체다:

```tsx
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);
    return () => {
      clearTimeout(timeoutId);
    };
  }, [value, delay]);

  return debouncedValue;
}
```

### 3.2 setInterval의 위험 - 재귀 setTimeout이 더 안전

`setInterval`은 **이전 콜백이 끝나지 않아도 다음 콜백을 실행**한다. API 호출처럼 오래 걸리는 작업은 겹칠 수 있다. 재귀 setTimeout은 이전 작업 완료 후에야 다음을 예약한다:

```tsx
// 폴링 훅 - 이전 요청 완료 후 다음 폴링
function usePolling<T>(fetchFn: () => Promise<T>, interval: number) {
  const [data, setData] = useState<T | null>(null);

  useEffect(() => {
    let timeoutId: ReturnType<typeof setTimeout>;

    async function poll() {
      try {
        setData(await fetchFn());
      } catch (error) {
        console.error('Polling error:', error);
      }
      timeoutId = setTimeout(poll, interval); // 완료 후 다음 예약
    }
    poll();

    return () => {
      clearTimeout(timeoutId);
    };
  }, [fetchFn, interval]);

  return data;
}
```

### 3.3 requestAnimationFrame과 복수 타이머

- rAF 재귀 루프(카운트업 애니메이션·스크롤 애니메이션)는 매 프레임 `rafId`를 갱신 저장하고 정리 함수에서 `cancelAnimationFrame(rafId)`. 정리하지 않으면 `target` 변경 시 이전 애니메이션과 새 애니메이션이 **동시에** 돌아 값이 비정상 증가한다.
- 한 컴포넌트의 여러 타이머(자동 닫기 timeout + 진행 바 interval)는 **전부** 정리해야 한다 - 일부만 정리하는 실수가 흔하다. 타이머가 많으면 배열로 모아 `timers.forEach(clearTimeout)`.
- `useTimeout` 커스텀 훅으로 추상화하면 실수를 원천 차단한다. 이때 `callbackRef` 패턴(콜백을 ref에 보관)을 쓰면 콜백이 변경되어도 타이머가 재설정되지 않는다.

## 4. 구독과 이벤트 리스너의 생명주기 관리

모든 구독 메커니즘은 "등록과 해제의 쌍"을 따른다. 해제 API만 다르다.

| 구독 유형 | 등록 | 해제 |
|---|---|---|
| DOM 이벤트 | `addEventListener` | `removeEventListener`(같은 참조) |
| WebSocket | `new WebSocket()` | `close()`(readyState 확인) |
| SSE | `new EventSource()` | `close()`(상태 확인 불필요) |
| RxJS | `subscribe()` | `unsubscribe()` 또는 `takeUntil` |
| EventEmitter | `on()` | `off()` / `removeListener()`(같은 참조) |

- **DOM 이벤트**: `useOnlineStatus`(online/offline), `useClickOutside`(document mousedown+touchstart로 드롭다운 바깥 클릭 감지) 같은 훅에서 등록한 모든 리스너를 정리 함수에서 제거.
- **WebSocket**: 정리 함수에서 `readyState`가 `OPEN` 또는 `CONNECTING`일 때만 `close()`. **자동 재연결 훅에서는 정리 시 `ws.onclose = null`을 먼저** - onclose 핸들러가 재연결을 트리거하므로, 이를 제거하지 않으면 언마운트 후에도 재연결이 계속된다. 재연결 타이머(`reconnectTimeout`)도 함께 정리.
- **SSE(EventSource)**: 연결이 끊기면 자동 재연결이 기본 동작이고, `close()`를 호출하면 재연결도 멈춘다.
- **RxJS**: `subscription.unsubscribe()`. 구독이 여러 개면 `takeUntil(destroy$)` 패턴 - 정리 함수에서 `destroy$.next(); destroy$.complete()` 한 번으로 모든 구독이 동시 해제된다.

## 5. 크롬 개발자 도구로 메모리 누수 디버깅

메모리 누수는 코드만 봐서는 안 보인다 - 도구 기반의 체계적 디버깅이 필수다. Memory 패널의 세 기능: **Heap snapshot**(시점 상태 비교), **Allocation instrumentation on timeline**(실시간 할당 추적), **Allocation sampling**(저오버헤드 샘플링).

### 5.1 힙 스냅샷 비교 워크플로

1. 앱 로드 직후 **Snapshot 1**(기준) 촬영.
2. 의심 동작을 **10번 반복**(모달 여닫기, 마운트/언마운트, 페이지 내비게이션) - 반복이 많을수록 패턴이 명확해진다.
3. **Snapshot 2** 촬영 → Comparison 뷰에서 Snapshot 1과 비교.
4. **# Delta 기준 정렬** - 양수가 큰 객체가 용의자다. 주목 대상: `HTMLElement`(Detached 여부), `EventListener`(리스너 누적), `Closure`(큰 객체 캡처), 배열/객체(캐시 무한 증가).

### 5.2 Detached DOM과 Retainers

- 스냅샷 검색창에 **"Detached"** 를 입력하면 Detached DOM 노드가 필터링된다.
- 노드를 클릭하면 하단 **Retainers 패널**이 참조 체인을 보여준다 - 체인을 역추적하면 어떤 변수·클로저가 노드를 붙잡는지 나온다.

실전 시나리오(검색 모달을 여닫을수록 느려짐): 스냅샷 비교 → EventListener 델타 +10 → Retainers에서 `Window → listeners → keydown → handleKeyDown → onClose → 클로저 스코프` 확인 → `removeEventListener` 정리 함수 추가 → 재측정으로 델타 0±1 검증. **수정 후 같은 테스트로 재검증까지가 한 사이클이다.**

### 5.3 Allocation instrumentation과 Performance Monitor

- **Allocation timeline**: 녹화 중 의심 동작 수행 → 파란 막대(할당)가 시간이 지나도 사라지지 않으면 누수. 구간을 드래그하면 그 시점에 할당된 객체만 필터링 - 이벤트 기반 누수(클릭마다 큰 배열 캡처)를 찾는 데 유용.
- **Performance Monitor**(Cmd+Shift+P → "Show Performance Monitor"): JS heap size·DOM Nodes·JS event listeners를 실시간 그래프로. **정상 앱은 톱니 모양**(증가→GC로 감소 반복), **누수 앱은 계단식 상승**. 장시간 실행 테스트에 적합하다.

## 6. 메모리 누수 방지를 위한 코드 패턴

디버깅보다 예방이 낫다. 세 가지 패턴을 코드베이스 전체에 일관 적용한다.

### 6.1 AbortController - 하나의 시그널로 일괄 취소

```tsx
useEffect(() => {
  const controller = new AbortController();
  const { signal } = controller;

  // 여러 fetch를 하나의 signal로
  Promise.all([
    fetch('/api/search?q=react', { signal }),
    fetch('/api/popular', { signal }),
    fetch('/api/recommendations', { signal }),
  ]).then(/* ... */);

  // addEventListener도 signal 지원 - abort() 시 자동 제거!
  window.addEventListener('resize', updateSize, { signal });
  window.addEventListener('orientationchange', updateSize, { signal });

  return () => {
    controller.abort(); // fetch + 리스너 전부 한 번에
  };
}, []);
```

`{ signal }` 옵션 덕분에 `removeEventListener`를 직접 호출할 필요도, 함수 참조를 보관할 필요도 없다. 단 **타이머는 signal을 지원하지 않으므로 여전히 `clearInterval` 수동 정리** + 콜백에서 `signal.aborted` 체크로 취소 후 실행을 막는다.

### 6.2 Disposable 패턴 - 생명주기를 타입으로 강제

리소스 생성 시 정리 방법을 함께 캡슐화한다. `dispose()`(또는 TS 5.2+ `[Symbol.dispose]()` + `using` 키워드 - 스코프 이탈 시 자동 호출).

```ts
/** 정리 가능한 리소스. */
interface Disposable {
  /** 보유한 리소스를 해제한다 */
  dispose(): void;
}

class EventListenerDisposable implements Disposable {
  constructor(
    private target: EventTarget,
    private event: string,
    private handler: EventListener,
    private options?: AddEventListenerOptions,
  ) {
    target.addEventListener(event, handler, options);
  }
  dispose() {
    this.target.removeEventListener(this.event, this.handler, this.options);
  }
}
```

`IntervalDisposable`·`TimeoutDisposable`도 같은 꼴이고, `CompositeDisposable`은 여러 Disposable을 모아 **생성의 역순으로** 정리한다(나중에 생성된 리소스가 먼저 것에 의존할 수 있으므로). 정리 함수는 `disposables.dispose()` 한 줄이 된다. WebSocket처럼 인터페이스가 없는 리소스도 `{ dispose: () => ws.close() }`로 감싸 추가할 수 있다.

### 6.3 WeakMap / WeakSet - 약한 참조로 자동 회수

일반 Map에 객체를 저장하면 컬렉션이 참조를 유지해 GC를 막는다. `WeakMap`/`WeakSet`은 **약한 참조** - 저장된 객체가 다른 곳에서 참조되지 않으면 자동으로 GC되고 컬렉션에서도 사라진다. `delete()` 호출을 잊어도 누수가 없다.

- **DOM 노드 메타데이터**: `nodeData.set(element, data)` - 노드가 제거·GC되면 데이터도 자동 정리.
- **리스너 레지스트리**: 요소별 등록 리스너 목록을 WeakMap으로 추적.
- **객체 키 캐시**: `apiCache.set(user, data)` - user 객체가 사라지면 캐시 엔트리도 함께.
- **처리 여부 추적**: `processedElements`(WeakSet)로 중복 처리 방지.

제약: ① 키는 객체(또는 non-registered 심벌)만 - 문자열·숫자 불가 ② 순회 불가(keys/values/forEach 없음 - GC 타이밍이 비결정적이라) ③ `.size` 없음. 순회가 필요하거나 원시값이 키면 일반 Map/Set + 수동 정리를 쓴다.

### 6.4 상황별 패턴 선택

| 상황 | 권장 패턴 |
|---|---|
| 여러 페치 요청을 한 번에 취소 | AbortController |
| 이벤트 리스너 자동 제거 | AbortController + `{ signal }` |
| 여러 종류 리소스 일괄 관리 | Disposable + CompositeDisposable |
| 타입 레벨에서 정리 강제 | Disposable 인터페이스(TS 5.2+ `using`) |
| DOM 노드에 메타데이터 저장 | WeakMap |
| 객체 처리 여부 추적 | WeakSet |
| 캐시 자동 정리(객체 키) | WeakMap |
| 순회 필요·원시값 키 | 일반 Map/Set + 수동 정리(LRU) |

> **핵심 통찰**: 이 패턴들을 일관되게 적용하면 메모리 누수는 **코드 리뷰 단계에서** 대부분 발견된다. "이 리소스를 언제 정리하나요?"라는 질문에 명확히 답할 수 있는 코드가 안전한 코드다.

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|---|---|---|
| useEffect에 정리 함수 없음 | 리스너·타이머·구독이 언마운트 후에도 잔존 | 등록·설정·구독마다 해제를 쌍으로 반환 |
| 익명 함수로 removeEventListener | 다른 참조라서 아무것도 제거 안 됨 - 정리 함수가 있어도 누수 | 이름 있는 함수를 등록·해제에 동일 참조로 |
| 정리 함수 = 언마운트 전용으로 오해 | 의존성 변경 시 이전 이펙트가 정리 안 돼 구독 누적 | 재실행 직전에도 호출됨을 전제로 설계 |
| 비동기 응답을 무조건 setState | 언마운트 후/이전 검색어 응답이 화면을 덮음(경쟁 상태) | AbortController(또는 cancelled 플래그) |
| 객체 프롭을 의존성 배열에 | 렌더링마다 새 참조 → 이펙트 재실행 → 재연결 반복 | 원시 값만 의존성에(추출 또는 useMemo) |
| setInterval로 API 폴링 | 이전 요청이 안 끝나도 다음 실행 - 겹침 | 재귀 setTimeout(완료 후 다음 예약) |
| 여러 타이머 중 일부만 정리 | 남은 타이머의 클로저가 계속 잔존 | 배열 관리 + 전부 정리, 또는 커스텀 훅 |
| rAF 루프 미취소 | target 변경 시 이전 애니메이션과 중복 실행 | rafId 저장 + cancelAnimationFrame |
| 재연결 WebSocket을 그냥 close() | onclose 핸들러가 재연결을 트리거 - 좀비 연결 | 정리 시 `onclose = null` 먼저 + 재연결 타이머 정리 |
| 전역 변수·상태에 DOM 노드 저장 | Detached DOM으로 트리 전체가 잔존 | 필요한 데이터만 추출 저장, 불가피하면 null 할당 |
| 콜백이 큰 객체를 통째로 캡처 | 길이만 필요한데 10MB 배열이 클로저에 유지 | 필요한 값만 별도 상태로 추출해 참조 |
| 캐시·알림 배열 무한 증가 | 만료 없는 캐싱 = 누수 | LRU(크기 제한) + TTL, 상태 상한선 |
| 정리 함수에서 setState | 언마운트 시점 무의미 + 문제 유발 | 정리 함수는 해제 작업만 |
| 코드만 보고 누수 찾기 | 한 줄 누락은 눈에 안 보임 | 힙 스냅샷 비교(동작 10회 반복) + Retainers 추적 |

## 측정과 검증

- **힙 스냅샷 비교**: 기준 → 의심 동작 10회 → 재촬영 → Comparison # Delta 정렬. 수정 후 같은 절차로 델타 0±1 확인.
- **Detached 필터 + Retainers**: 어떤 변수/클로저가 노드를 붙잡는지 참조 체인 역추적.
- **Allocation timeline**: 할당 막대가 유지되면 누수 - 구간 선택으로 시점별 객체 확인.
- **Performance Monitor**: JS heap size·event listeners 실시간 - 톱니(정상) vs 계단식 상승(누수). 실제 사용 패턴으로 30분+ 관찰.
- **Performance 탭**: Major GC가 긴 작업으로 잡히는지 - 메모리 누수의 INP 영향 직접 확인.
- **예방 자동화**: ESLint `react-hooks/exhaustive-deps` 활성화, 코드 리뷰에서 "이 리소스 언제 정리?" 질문 상시화.

## 체크리스트

**생명주기 관리**

- [ ] 리액트 useEffect에 정리 함수 작성(리스너·타이머·구독 해제)
- [ ] 뷰 onUnmounted 등 프레임워크별 정리 훅에서 리소스 정리
- [ ] 컴포넌트 언마운트 시 진행 중인 비동기 작업 취소

**이벤트 리스너**

- [ ] addEventListener 후 반드시 removeEventListener 호출
- [ ] 동일한 함수 참조 사용(익명 함수는 제거 불가)
- [ ] 전역 이벤트 리스너(window·document) 특히 주의

**타이머 관리**

- [ ] setTimeout → clearTimeout
- [ ] setInterval → clearInterval(폴링은 재귀 setTimeout 우선)
- [ ] requestAnimationFrame → cancelAnimationFrame

**구독 관리**

- [ ] RxJS 구독 후 unsubscribe()(복수는 takeUntil)
- [ ] EventEmitter 리스너는 off()/removeListener()
- [ ] WebSocket close()(재연결 로직은 onclose 해제 먼저)
- [ ] EventSource close()

**DOM 참조**

- [ ] 제거된 DOM 노드 참조를 null로 설정
- [ ] 큰 DOM 트리를 참조하는 변수 정리
- [ ] 이벤트 핸들러에서 DOM 노드 직접 저장 회피(데이터만 추출)

**측정 및 디버깅**

- [ ] Memory 탭 힙 스냅샷 비교(의심 동작 반복 후)
- [ ] Detached DOM nodes 확인 + Retainers 추적
- [ ] Performance Monitor로 JS Heap Size 추적(톱니 vs 계단)
- [ ] Allocation Timeline으로 증가 패턴 분석

**예방 패턴**

- [ ] ESLint react-hooks/exhaustive-deps 규칙 활성화
- [ ] AbortController로 비동기 작업·리스너 일괄 취소
- [ ] WeakMap·WeakSet으로 약한 참조 활용
- [ ] 커스텀 훅/Disposable로 리소스 생명주기 캡슐화

## 요약

- 메모리 누수는 **생명주기 관리의 문제**다 - 코드는 정확한데 "생성했으면 해제한다"를 잊은 것. 한 번에 앱을 죽이지 않고 서서히 성능을 갉아먹어 "오래 쓰면 느려져요"가 된다. SPA는 새로고침이 없어 실수가 그대로 누적된다.
- 성능 영향의 경로: 힙 증가 → GC 빈도·시간 증가 → 메인 스레드 블로킹(Major GC 수십~수백 ms) → **INP 악화**. Ch18의 실행 최적화와 이 장의 메모리 관리가 런타임 성능의 양대 축이다.
- **전형적 5패턴**: ① 전역 리스너 미제거(클로저 연쇄로 수십 MB) ② 타이머 미정리(setInterval은 영원히) ③ Detached DOM(노드 대신 데이터만 저장) ④ 클로저의 큰 객체 캡처(필요 값만 추출 + 함수형 업데이트) ⑤ 무한 캐시(LRU + TTL + 상한선).
- **useEffect 정리 함수는 두 시점** - 언마운트 + 의존성 변경 재실행 직전. 비동기는 AbortController로 경쟁 상태까지 해결, 의존성엔 원시 값만, 정리 함수는 해제 작업만.
- 타이머는 설정·취소의 쌍. **폴링은 setInterval 대신 재귀 setTimeout**(겹침 방지). rAF도 취소 필수. 복수 타이머는 배열/커스텀 훅으로.
- 구독은 유형별 해제 API를 정확히: removeEventListener(같은 참조)·close()(WS는 readyState 확인 + 재연결 훅은 onclose 해제 먼저)·unsubscribe()/takeUntil·off().
- 디버깅은 도구로: **힙 스냅샷 비교(# Delta) → Detached 필터 → Retainers 역추적 → 수정 → 재검증.** Performance Monitor의 톱니(정상) vs 계단(누수) 패턴.
- 예방 3종: **AbortController**(fetch + `{ signal }` 리스너 일괄 취소), **Disposable**(dispose 캡슐화 + CompositeDisposable 역순 정리 + TS `using`), **WeakMap/WeakSet**(약한 참조로 자동 회수 - 객체 키·순회 불가 제약).
- 원칙 한 줄: **"이 리소스를 언제 정리하나요?"에 답할 수 있는 코드가 안전한 코드다.**

## 다른 챕터와의 관계

- **Ch18(자바스크립트 실행)**: 실행 최적화(순간 반응성)와 메모리 관리(장시간 안정성)는 함께 가야 완성된다 - 아무리 작업을 쪼개도 GC가 100ms씩 멈추면 무용지물. 디바운스 훅·AbortController 패턴이 두 장에 걸쳐 재등장한다.
- **Ch17(데이터 캐싱)**: 리액트 쿼리의 gcTime이 바로 이 장의 "캐시 만료 정책"이다 - 라이브러리가 LRU/TTL을 대신 관리해 준다. 직접 캐시를 만들 때만 이 장의 상한선 원칙이 필요하다.
- **Ch16(하이드레이션)**: SPA의 클라이언트 라우팅이 누수를 누적시키는 무대다 - 페이지 전환이 새로고침이 아니라는 점이 두 장의 공통 전제.
- **Ch21(애니메이션)**: rAF 루프의 취소 규율이 애니메이션 장의 기본기가 된다.
- **Ch22(컴포넌트 최적화)**: 클로저 캡처·의존성 배열 설계가 리액트 리렌더링 최적화(useCallback·useMemo)와 만난다.
- **Ch23(서드파티)**: 서드파티 스크립트가 만드는 리스너·타이머는 통제 밖의 누수원 - 서드파티 관리 전략으로 이어진다.
