# Chapter 10: 코드 스플리팅은 기능이 아니라 전략이다

## 핵심 질문

`import()`를 넣으면 번들이 쪼개진다는 것은 안다. 하지만 **어디서 쪼개고, 얼마나 쪼개고, 쪼갠 청크를 언제 로드할 것인가?** 전략 없는 코드 스플리팅은 왜 오히려 성능을 해치는가? 그리고 프레임워크가 자동으로 해주는 시대에 왜 여전히 원리를 알아야 하는가?

## 1. 프레임워크가 자동으로 해주는데 왜 알아야 하는가

Next.js·Nuxt·리믹스는 `app/`이나 `pages/`에 파일만 넣으면 라우트별 청크를 자동 생성한다. 그럼에도 원리를 알아야 하는 이유는 세 가지다.

1. **프레임워크 기본 설정이 모든 상황에 최적은 아니다.** 라우트 단위 분할은 자동이지만, **라우트 내부에서 조건부로 쓰이는 무거운 라이브러리**(Chart.js ~68KB gzip)는 정적 import하면 사용 여부와 무관하게 라우트 청크에 포함된다. 더 심각한 것은 공통 레이아웃(`_app.js`, `layout.tsx`)에서 무거운 라이브러리를 import하면 **모든 라우트의 초기 번들**에 들어간다는 점이다.
2. **문제가 생겼을 때 디버깅할 수 있어야 한다.** "왜 이 페이지 청크가 500KB인가", "왜 같은 라이브러리가 여러 청크에 중복 포함됐는가", "왜 페이지 이동마다 깜빡임이 발생하는가"에 답하려면 번들러의 청크 구성 방식을 알아야 한다.
3. **프레임워크의 한계를 넘어선 최적화**(벤더 청크 분리, 조건부 로딩, 공통 모듈 중복 제거)는 수동 설정이 필요하다.

효과적인 코드 스플리팅은 **사용자의 행동 패턴**(첫 화면에 필요한 코드 vs 특정 라우트·조건에서만 필요한 코드)과 **애플리케이션의 구조**(공통 모듈, 의존성 관계, 청크 구성)를 이해하는 데서 시작한다.

## 2. 동적 import()가 번들을 쪼개는 원리

### 2.1 정적 import vs 동적 import()

`import()`는 단순한 지연 로딩 문법이 아니라 **번들러에게 "이 지점에서 번들을 분할하라"는 명령**이다. 핵심 차이는 **의존성이 언제 해결되는가**다.

| 특성 | 정적 import | 동적 import() |
|---|---|---|
| 의존성 해결 시점 | 빌드 타임 | 런타임 |
| 번들 구성 | 하나의 번들에 포함 | 별도 청크로 분리 |
| 로딩 시점 | 페이지 초기 로드 | 코드 실행 시점 |
| 반환 타입 | 모듈 객체 | `Promise<Module>` |
| 트리 셰이킹 | 가능 | 제한적 |
| 파일 위치 | 최상단만 가능 | 코드 어디서나 가능 |

Chart.js(gzip ~68KB) 예제의 실측 결과가 차이를 보여준다.

```
[정적 import]  초기 로드: 298.63KB (gzip 100.06KB)
  → 차트를 안 보는 사용자도 Chart.js 155.31KB(gzip 54.12KB)를 다운로드

[동적 import()] 초기 로드: 144.64KB (gzip 47.35KB)  ← 51.6% 감소
  → '차트 보기' 클릭 시에만 155.31KB(gzip 54.12KB) 추가 로드
```

```tsx
// 동적 import() - 버튼 클릭 시에만 Chart 컴포넌트 로드
function App() {
  const [ChartComponent, setChartComponent] = useState<React.ComponentType | null>(null);
  const [loading, setLoading] = useState(false);

  const loadChart = async () => {
    setLoading(true);
    const module = await import(/* webpackChunkName: 'chart' */ './ChartComponent');
    setChartComponent(() => module.default);
    setLoading(false);
  };

  return (
    <div>
      <button onClick={loadChart} disabled={loading}>
        {loading ? '로딩 중...' : '차트 보기'}
      </button>
      {ChartComponent && <ChartComponent />}
    </div>
  );
}
```

> **핵심 통찰**: 동적 import에도 **비용**이 있다. 클릭한 시점부터 청크 다운로드가 시작되므로 느린 네트워크에서는 사용자가 "로딩 중"을 보며 기다린다. 그래서 코드 스플리팅은 '전략'이다. **사용 빈도**(10%만 쓰는 기능이면 효과적), **사용 시점**(로드 직후 필요하면 쪼개지 않는다), **리소스 크기**(10KB 수준이면 HTTP 오버헤드가 더 클 수 있다), **네트워크 환경**을 종합해 결정한다.

### 2.2 번들러가 청크를 생성하는 방식

비트(프로덕션은 내부적으로 롤업 사용)의 빌드 과정: ① 진입점 분석(`index.html`의 `<script type="module">`) → ② 의존성 그래프 생성 → ③ **동적 `import()`마다 분할 지점 표시** → ④ 청크 생성 → ⑤ 트리 셰이킹 → ⑥ 내용 기반 해시로 청크 이름 지정.

`manualChunks`로 벤더 청크를 직접 제어한다.

```ts
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor-react': ['react', 'react-dom'],   // 리액트를 별도 청크로
        },
      },
    },
  },
});
```

```
dist/assets/
├── index-DNNgL9FK.js          (3.77KB)   ← 애플리케이션 메인 코드
├── vendor-react-nf7bT_Uh.js   (140.87KB) ← React + ReactDOM
└── ChartComponent-BLNUy8Dt.js (155.31KB) ← Chart.js (동적 로드)
```

파일명의 해시는 **내용 기반**이다. Chart.js를 수정하면 그 청크의 해시만 바뀌고, 리액트 청크는 캐시에서 그대로 쓰인다. 함수 형태의 `manualChunks`로 공통 모듈도 추출할 수 있다.

```ts
manualChunks(id) {
  if (id.includes('node_modules')) {
    return 'vendor';
  }
  if (id.includes('/src/utils/')) {
    return 'common';   // 여러 동적 청크가 공유하는 유틸을 한 번만 다운로드
  }
},
```

빌드 시 상대 경로(`./ChartComponent`)는 해시가 붙은 절대 경로(`/assets/ChartComponent-BLNUy8Dt.js`)로 재작성되고, 브라우저는 네이티브 `import()`로 청크를 로드한다. 개발 환경에서 비트는 번들링 없이 브라우저 ESM을 직접 쓰고, 프로덕션에서만 롤업으로 최적화한다.

### 2.3 React.lazy()와 서스펜스의 동작 원리

`React.lazy()`는 동적 `import()`를 감싸는 래퍼다. 사용자가 지연 컴포넌트를 렌더링하려는 순간의 흐름:

1. 리액트가 lazy 컴포넌트 렌더링 시도
2. 아직 로드되지 않았다면 **Promise를 throw**
3. 가장 가까운 `Suspense` 경계가 이를 잡아 `fallback` 렌더링
4. Promise가 리졸브되면 실제 컴포넌트 렌더링

```tsx
// React.lazy()의 단순화된 구현
function lazy(loadComponent) {
  let status = 'pending';
  let result;
  const promise = loadComponent().then(
    (module) => { status = 'success'; result = module.default; },
    (error) => { status = 'error'; result = error; },
  );

  return function LazyComponent(props) {
    if (status === 'pending') { throw promise; }  // ← 핵심: Promise를 throw
    if (status === 'error')   { throw result; }
    const Component = result;
    return <Component {...props} />;
  };
}
```

> **참고**: 실제 리액트 서스펜스는 사용자 코드의 `componentDidCatch`로 Promise를 잡는 방식이 아니다. 렌더링 중 thenable이 발생하면 **리액트 렌더러가** 가장 가까운 서스펜스 경계를 찾아 폴백을 표시하고, 완료되면 다시 렌더링한다. **로딩 상태는 서스펜스가, 로딩 실패 같은 실제 에러는 에러 바운더리가 처리한다.**

이 메커니즘에서 세 가지 제약이 나온다.

1. **default export여야 한다.** 명명 엑스포트는 변환이 필요하다: `lazy(() => import('./Dashboard').then((m) => ({ default: m.Dashboard })))`
2. **반드시 서스펜스 경계 안에 있어야 한다.** 없으면 Promise를 잡을 곳이 없어 에러가 난다.
3. **하나의 서스펜스에 여러 lazy 컴포넌트를 넣으면 어느 하나라도 로딩 중이면 전체가 폴백**이 된다. 독립적으로 로딩하려면 각각 별도 서스펜스로 감싼다.

**서스펜스 배치 패턴 비교**

- **패턴 1 - 단일 서스펜스**: 코드가 간단하고 일관된 로딩 경험. 단점은 작은 컴포넌트 로딩에도 전체 영역이 폴백으로 바뀌어 깜빡임이 느껴진다.
- **패턴 2 - 독립적 서스펜스**: 각 영역이 독립적으로 로딩 상태를 관리해 UX가 세밀하다. 단점은 코드 복잡도와 경계 배치 고민.
- **패턴 3 - ErrorBoundary와 함께**: 청크 로딩 실패(네트워크 오류·404)를 우아하게 처리. CDN 장애나 배포 중 문제에 대응한다.

실제 프로덕션에서는 셋을 조합한다. 페이지 레벨에 ErrorBoundary, 중요한 위젯은 독립적 서스펜스, 작은 모달·드롭다운은 단일 서스펜스.

다른 프레임워크도 원리는 같다. 뷰는 `defineAsyncComponent`(loadingComponent·errorComponent·delay·timeout 옵션 제공), 스벨트는 래퍼 없이 동적 `import()`를 직접 사용한다. **동적 import로 청크를 분리하고, Promise로 로딩 상태를 관리하고, 사용자에게 적절한 피드백을 준다.**

## 3. 전략적 분할 지점 찾기

### 3.1 라우트 기반 코드 스플리팅

가장 효과적이고 직관적인 전략이다. **사용자 행동과 코드 경계가 일치**하기 때문이다 - 페이지를 이동하는 시점은 명확하고, 그때의 짧은 로딩은 사용자가 기대하는 예상 가능한 경험이다.

```tsx
import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

const Home = lazy(() => import('./pages/Home'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Settings = lazy(() => import('./pages/Settings'));

function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<div>페이지 로딩 중...</div>}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
```

- **Next.js**: 파일 시스템 라우팅으로 자동 분할. 페이지 **내부** 컴포넌트는 자동 분할되지 않으므로 `next/dynamic`을 쓴다(`ssr: false` 옵션 등). 단, 앱 라우터의 서버 컴포넌트에서 `ssr: false`를 쓰면 빌드 에러 - 반드시 `'use client'` 파일 안에서 선언한다.
- **Vue Router**: `component: () => import('./views/Home.vue')` 화살표 함수가 핵심이다.

**세 가지 주의점**

1. **내비게이션 바·사이드바 같은 공통 컴포넌트는 분할하지 않는다.** 각 라우트 청크에 중복 포함되면 총 다운로드가 오히려 증가한다.
2. **첫 페이지(랜딩)는 최대한 가볍게.** 첫 페이지 로드 성능이 전체 경험에 가장 큰 영향을 준다.
3. **중첩 라우트는 부모-자식 관계를 고려한다.** 공통 레이아웃은 부모 라우트에, 실제 콘텐츠만 자식 라우트로 분리한다.

### 3.2 컴포넌트 레벨 지연 로딩

라우트 분할이 거시 전략이라면 컴포넌트 레벨은 페이지 내부의 미시 최적화다. 좋은 후보들:

- **모달·다이얼로그**: 버튼 클릭 전까지 화면에 없다. 이미지 에디터가 200KB라면 대부분의 사용자는 그것을 다운로드하지 않는다.
- **탭·아코디언**: 첫 탭만 보고 떠나는 사용자에게 나머지 탭 코드는 불필요하다.
- **조건부 기능·권한 기반**: `user.isAdmin && <AdminPanel />` - 일반 사용자 90%는 관리자 패널 코드를 받지 않는다.
- **무거운 라이브러리를 포함한 컴포넌트**: Chart.js(~280KB), Monaco Editor(~1.5MB), PDF.js(~500KB). **Next.js 기준으로 160KB 이상의 서드파티는 별도 청크 분리가 효과적**이며, 이 기준을 적용해 Barnebys 23%, SumUp 30%, HashiCorp 71%의 번들 감소를 달성했다.
- **뷰포트 기반**: 페이지 하단의 무거운 컴포넌트는 인터섹션 옵저버 + `rootMargin: '100px'`로 뷰포트 진입 직전에 로드한다.

```tsx
const HeavyFooter = lazy(() => import('./components/HeavyFooter'));

function HomePage() {
  const [showFooter, setShowFooter] = useState(false);
  const footerTrigger = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          setShowFooter(true);
          observer.disconnect();
        }
      },
      { rootMargin: '100px' }, // 뷰포트 100px 전에 미리 로드
    );
    if (footerTrigger.current) {
      observer.observe(footerTrigger.current);
    }
    return () => observer.disconnect();
  }, []);

  return (
    <div>
      <main>...</main>
      <div ref={footerTrigger} />
      {showFooter && (
        <Suspense fallback={<div>Footer 로딩 중...</div>}>
          <HeavyFooter />
        </Suspense>
      )}
    </div>
  );
}
```

> **핵심 통찰**: 모든 무거운 라이브러리를 무조건 지연 로딩하는 것은 아니다. **차트가 대시보드의 핵심 콘텐츠이고 대부분의 사용자가 첫 화면에서 봐야 한다면 지연 로딩하지 않는 편이 낫다.** 버튼 클릭 후 로딩을 기다리는 것보다 페이지 로드 시 바로 보이는 것이 더 나은 경험이다. 기준은 **사용 빈도 + 사용자 기대**다.

### 3.3 잘못된 분할 지점과 안티패턴

**① 너무 작은 청크 남발**: 2~4KB 컴포넌트를 각각 분할하면 청크 로드 오버헤드(번들러 런타임·파싱 비용)가 코드 크기보다 커진다. 구글 연구 기준 HTTP/2에서도 **초기 요청 25개**까지는 FCP가 유지되지만 그 이상은 저하된다. **최소 20~30KB 이상만 별도 청크로** - 웹팩 기본값 20KB, Next.js·개츠비가 채택한 실무 가이드라인이다.

**② 첫 화면 필수 컴포넌트 지연 로딩**: Header·MainContent를 lazy로 만들면 사용자가 페이지를 열자마자 로딩 인디케이터를 본다. 첫 화면 컴포넌트는 정적 import, 스크롤해야 보이는 Footer만 지연 로딩한다.

**③ 공통 모듈을 여러 청크에 중복 포함**: 세 페이지가 각각 `api.js` 10KB를 포함하면 총 30KB를 다운로드한다. `manualChunks`로 공통 청크로 추출한다.

**④ 모든 라우트를 무분별하게 분할**: 2~5KB짜리 정보성 페이지(About·Contact·Terms·Privacy)는 하나의 청크로 묶는다.

```tsx
// 작은 페이지들을 하나의 청크로 - Promise 재사용으로 네 라우트가 같은 청크 공유
const loadInfoPages = () => import('./pages/InfoPages');

const About = lazy(() => loadInfoPages().then((m) => ({ default: m.About })));
const Contact = lazy(() => loadInfoPages().then((m) => ({ default: m.Contact })));
const Terms = lazy(() => loadInfoPages().then((m) => ({ default: m.Terms })));
const Privacy = lazy(() => loadInfoPages().then((m) => ({ default: m.Privacy })));
```

**⑤ 사용자 인터랙션에 필수적인 컴포넌트 지연 로딩**: 결제·로그인·폼 제출을 버튼 클릭 후 로드하면 전환율이 떨어진다. 결제 페이지 진입 시 정적 import하거나 `useEffect`에서 미리 프리로드한다.

```tsx
function CheckoutPage() {
  useEffect(() => {
    // 페이지 로드 후 결제 모듈 미리 로드
    import('./PaymentForm');
  }, []);
  // ...
}
```

## 4. 청크 최적화와 공통 모듈 추출

청크 최적화는 세 목표의 균형이다. **① 중복 제거**(공통 모듈은 한 번만 다운로드), **② 캐싱 효율**(변경 빈도가 다른 코드를 분리 - 앱 코드가 바뀌어도 벤더 청크는 캐시 유지), **③ 청크 크기와 개수의 균형**.

### 4.1 벤더 청크 분리 전략

비트는 기본적으로 벤더를 자동 분리하지 않으며 500KB 이상 청크에 경고만 표시한다. 청크 크기가 중요한 이유는 다운로드만이 아니다 - **자바스크립트는 파싱·컴파일 시간이 파일 크기에 비례**하고, V8 팀 연구 기준 중급 모바일(Moto G4)은 고급 기기보다 3~4배, 저급 기기는 6배 이상 느리다. 같은 1MB도 500KB 두 개로 나누면 두 코어에서 병렬 파싱되어 더 빠르다.

```ts
// vite.config.ts - 벤더 청크 세분화
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // 핵심 프레임워크 (거의 변경 없음, 모든 페이지에서 사용)
          'vendor-react': ['react', 'react-dom', 'react-router-dom'],
          // 무거운 라이브러리 중 특정 페이지에서만 사용
          'vendor-charts': ['chart.js', 'react-chartjs-2'],
          // 공통 유틸리티 (여러 페이지에서 사용, 거의 변경 없음)
          'vendor-utils': ['lodash-es', 'date-fns', 'classnames'],
          // 자주 업데이트되는 내부 라이브러리는 별도로
          'company-design-system': ['@company/design-system'],
        },
      },
    },
  },
});
```

세분화 전후 실측: Dashboard 청크 155.31KB → **8.91KB**, Settings 70.45KB → **6.73KB**. Chart.js와 lodash가 벤더 청크로 빠졌기 때문이다. 캐싱 시나리오가 진짜 이득이다 - Dashboard 코드를 수정 배포해도 `vendor-charts`의 해시는 그대로이므로 사용자는 **8.91KB만 새로 다운로드**한다(포함했다면 155KB 전체 재다운로드).

**벤더 청크 안티패턴**

- **모든 라이브러리를 개별 청크로**: 20개 이상의 벤더 청크는 HTTP 요청 급증. 초기 요청 25개를 넘으면 성능이 저하된다.
- **특정 페이지 전용 라이브러리를 공통 vendor에**: 관리자만 쓰는 xlsx(300KB)를 공통 벤더에 넣으면 일반 사용자 90%가 불필요하게 다운로드한다.
- **자주 변경되는 라이브러리를 vendor에**: 주 1회 업데이트되는 내부 디자인 시스템이 vendor에 있으면 리액트까지 매번 재다운로드된다.

**분리 기준 4가지**: ① 크기(최소 20~30KB 이상), ② 사용 빈도(대부분의 페이지에서 사용), ③ 업데이트 빈도(거의 안 바뀌는 것만 vendor로, 자주 바뀌는 것은 별도), ④ 관련성(함께 쓰는 라이브러리는 한 청크로).

### 4.2 청크 개수와 크기의 균형

web.dev의 세분화된 청크 분리(granular chunking) 연구 기준:

- **초기 요청 수: 최대 25개 이내** - 이 범위에서 FCP·로드 시간이 일관되게 유지, 100개 이상은 눈에 띄게 느려짐
- **초기 번들 크기: gzip 기준 170KB 이하** - critical-path 리소스 전체
- **최소 청크 크기: 20KB 이상** - 더 작으면 HTTP 오버헤드가 이득보다 큼
- **대형 서드파티 모듈: 160KB 이상은 별도 청크로 분리**

**최적화 5단계 절차**

1. **현재 청크 구성 분석**: 빌드 출력에서 큰 파일 식별
2. **rollup-plugin-visualizer로 청크 내용 분석**: 트리맵으로 어떤 모듈이 청크를 무겁게 만드는지 확인
3. **분리 전략 수립**: 무거운 라이브러리 분리(160KB+) → 공통 모듈 추출 → 저빈도 코드 지연 로딩. 실측 예시로 index.js 298.34KB → 45.23KB, 초기 로드 36% 개선 + 코드 한 줄 수정 시 재다운로드가 298KB → 16KB로 감소
4. **실제 성능 측정**: 라이트하우스로 FCP·LCP·TBT·리소스 수 확인. 청크 30개 이상으로 FCP가 느리면 병합, 초기 번들 200KB 이상으로 LCP가 느리면 더 분할
5. **캐시 효율 확인**: 코드 수정 후 재배포 시 수정한 페이지 청크만 해시가 변경돼야 정상. 벤더 청크 해시가 자주 바뀌면 구성을 재검토

> **핵심 통찰**: 이 수치들은 Next.js·개츠비에서 검증된 좋은 출발점이지만 절대 기준이 아니다. **라이트하우스와 RUM으로 프로젝트마다 최적 균형점을 직접 찾는다.**

## 5. 지연 로딩의 UX 최적화

코드 스플리팅으로 초기 로딩은 빨라졌지만 새로운 UX 문제가 생긴다. 청크 다운로드 중 빈 화면, 네트워크 오류로 인한 청크 로딩 실패다.

### 5.1 서스펜스 폴백 전략과 로딩 상태 디자인

`<Suspense fallback={<div>로딩 중...</div>}>`의 세 가지 문제: ① 단순 텍스트는 무엇이 로딩되는지 알 수 없고, ② 앱 전체를 하나로 감싸면 어느 부분이 로딩 중인지 불분명하며, ③ 즉시 표시되는 폴백은 빠른 로드(200ms)에서 깜빡임을 만든다.

**① 세분화된 서스펜스 경계**: 페이지·기능 단위로 나눈다. Dashboard로 이동할 때 Header·Sidebar는 유지되고 메인 영역만 스켈레톤으로 바뀐다.

**② 스켈레톤 스크린 vs 스피너**: 스피너는 간단하지만 정보가 없다. 스켈레톤은 실제 콘텐츠의 윤곽을 미리 보여준다. **스켈레톤은 실제 컴포넌트와 같은 높이·레이아웃을 유지해야 한다** - 스켈레톤은 카드 3개인데 실제는 5개라면 CLS가 발생한다.

**③ 지연된 폴백 표시**: 청크가 200ms 이하로 빠르게 로드되면 폴백을 아예 안 보여주는 것이 낫다.

```tsx
function useDeferredFallback(delay = 200): boolean {
  const [showFallback, setShowFallback] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setShowFallback(true), delay);
    return () => clearTimeout(timer);
  }, [delay]);

  return showFallback;
}

function DeferredFallback({ children, fallback, delay = 200 }) {
  const showFallback = useDeferredFallback(delay);
  return (
    <Suspense fallback={showFallback ? <div className="fallback-container">{fallback}</div> : null}>
      {children}
    </Suspense>
  );
}
```

```css
.fallback-container {
  animation: fadeIn 300ms ease-in;
  min-height: 200px; /* 레이아웃 시프트 방지 */
}
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
```

200ms 안에 로드되면 폴백이 표시되지 않고, 그보다 늦으면 페이드 인으로 자연스럽게 나타난다. `min-height`로 폴백↔콘텐츠 높이 차이로 인한 CLS도 방지한다.

**④ 중첩된 서스펜스로 점진적 렌더링**: 페이지 자체는 빠르게 표시하고, 무거운 차트·테이블은 각자의 속도로 로드한다. 사용자는 제목과 통계 카드를 먼저 보고 차트·테이블이 순차적으로 나타나는 것을 본다.

**⑤ Transition API**: 리액트 18의 `useTransition`으로 `navigate`를 감싸면 새 화면이 준비되는 동안 기존 화면을 유지하는 전환을 만들 수 있다. 단, `startTransition`이 청크 다운로드를 미리 시작하거나 이전 화면 유지를 **항상 보장하는 것은 아니며**, 라우터의 데이터/코드 로딩 방식과 서스펜스 경계 위치에 따라 폴백 표시 여부가 달라진다.

> **참고 - 제이콥 닐슨의 응답 시간 연구**<br><br>**100ms 이하**: 즉각적으로 느껴짐 → 폴백 불필요. **100ms~1초**: 딜레이를 인지하지만 흐름 유지 → 간단한 인디케이터나 스켈레톤. **1초 이상**: 생각 흐름이 끊김 → 스켈레톤 + 진행률 표시. 이 기준은 인간의 인지 능력에 기반하므로 기술 발전과 무관하게 유지된다. 실무에서는 보통 **100~300ms 사이에 폴백 표시를 시작**하고, 한 번 표시된 폴백은 **최소 300~500ms 유지**해 깜빡임을 방지한다.

### 5.2 에러 바운더리로 청크 로딩 실패 처리

청크 로딩 실패의 가장 흔한 원인은 **새 배포**다. 사용자가 앱을 열어둔 상태에서 새 버전이 배포되면 이전 HTML이 더 이상 존재하지 않는 청크를 참조해 `ChunkLoadError: Loading chunk 3 failed`가 발생한다. 처리하지 않으면 컴포넌트 트리 전체가 언마운트되어 빈 화면만 남는다.

**청크 에러 감지 + 자동 재시도 에러 바운더리**

```tsx
class ChunkErrorBoundary extends React.Component {
  state = { hasError: false, error: null, retryCount: 0 };

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error) {
    const isChunkError =
      error.name === 'ChunkLoadError' ||
      /Loading chunk [\d]+ failed/.test(error.message) ||
      /Failed to fetch/.test(error.message);

    if (isChunkError && this.state.retryCount < 3) {
      // 1초 후 자동 재시도 (최대 3번)
      setTimeout(() => {
        this.setState((state) => ({
          hasError: false,
          error: null,
          retryCount: state.retryCount + 1,
        }));
      }, 1000);
    }
  }

  render() {
    if (this.state.hasError && this.state.retryCount >= 3) {
      return (
        <div className="error-container">
          <h2>페이지를 불러올 수 없습니다</h2>
          <p>새 버전이 배포되었을 수 있습니다.</p>
          <button onClick={() => window.location.reload()}>새로고침</button>
        </div>
      );
    }
    if (this.state.hasError) {
      return this.props.fallback ?? <div>오류가 발생했습니다</div>;
    }
    return this.props.children;
  }
}
```

**동적 import 자체에 재시도 로직**을 추가하면 더 견고하다. 임포트 단계에서 3번 재시도하고, 그래도 실패하면 에러 바운더리가 잡는다.

```ts
function retryImport<T>(importFn: () => Promise<T>, retries = 3, delay = 1000): Promise<T> {
  return new Promise((resolve, reject) => {
    importFn()
      .then(resolve)
      .catch((error) => {
        if (retries === 0) {
          reject(error);
          return;
        }
        setTimeout(() => {
          retryImport(importFn, retries - 1, delay).then(resolve, reject);
        }, delay);
      });
  });
}

const Dashboard = lazy(() => retryImport(() => import('./Dashboard')));
```

**배포로 인한 버전 불일치**에는 자동 새로고침 + `sessionStorage`로 무한 리로드를 방지하는 패턴을 쓴다.

```ts
componentDidCatch(error) {
  const isChunkError = error.name === 'ChunkLoadError'
    || /Loading chunk [\d]+ failed/.test(error.message);

  if (isChunkError) {
    const reloadCount = parseInt(sessionStorage.getItem('chunkErrorReloadCount') ?? '0');
    if (reloadCount < 1) {
      sessionStorage.setItem('chunkErrorReloadCount', String(reloadCount + 1));
      window.location.reload();     // 자동 새로고침 1회
    } else {
      sessionStorage.removeItem('chunkErrorReloadCount');
      // 이미 한 번 리로드했으면 에러 UI 표시 → 수동 새로고침 안내
    }
  }
}
```

**페이지 단위로 에러 바운더리를 배치**해 에러의 영향 범위를 제한한다. Dashboard 청크 로딩이 실패해도 Header·Sidebar는 정상 작동하므로 사용자는 다른 페이지로 이동할 수 있다.

> **핵심 통찰**: 중요한 것은 에러를 조용히 무시하는 것이 아니라 **적절히 복구하거나 사용자에게 투명하게 알리는 것**이다. 사용자는 에러 자체보다 "에러에 대해 무엇을 해야 하는지 모르는 상황"을 더 불편해한다.

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|---|---|---|
| 2~5KB 컴포넌트도 전부 lazy 분할 | 청크 로드 오버헤드가 코드 크기보다 큼, 요청 25개 초과 시 성능 저하 | 최소 20~30KB 이상만 별도 청크 |
| 첫 화면 필수 컴포넌트 지연 로딩 | 페이지를 열자마자 로딩 인디케이터가 보임 | 첫 화면은 정적 import, 폴드 아래만 lazy |
| 결제·로그인 등 핵심 플로를 클릭 후 로드 | 버튼 클릭 후 대기 발생 → 전환율 하락 | 페이지 진입 시 정적 import 또는 프리로드 |
| 공통 모듈이 여러 청크에 중복 | 같은 코드를 페이지마다 반복 다운로드 | `manualChunks`로 공통 청크 추출 |
| 공통 레이아웃에서 무거운 라이브러리 import | 모든 라우트의 초기 번들에 포함됨 | 사용하는 컴포넌트로 import 위치 이동 + 동적 분리 |
| 관리자 전용 라이브러리를 공통 vendor에 | 일반 사용자 90%가 불필요한 300KB 다운로드 | 해당 페이지 청크에만 포함하거나 지연 로딩 |
| 자주 바뀌는 내부 패키지를 vendor 청크에 | 리액트까지 매번 재다운로드(캐시 무효화) | 변경 빈도별로 청크 분리 |
| 명명 엑스포트를 `lazy()`에 그대로 전달 | `lazy`는 default export만 렌더링 가능 | `.then((m) => ({ default: m.X }))` 변환 |
| 서스펜스 없이 lazy 컴포넌트 사용 | Promise를 잡을 곳이 없어 에러 발생 | 반드시 서스펜스 경계 안에 배치 |
| 앱 전체를 하나의 서스펜스/에러 바운더리로 | 한 부분의 로딩·에러가 전체 화면을 대체 | 페이지·기능 단위로 경계 세분화 |
| 스켈레톤과 실제 콘텐츠의 레이아웃 불일치 | 전환 시 CLS 발생 | 같은 높이·구조 유지, `min-height` 설정 |
| 청크 로딩 실패 미처리 | 배포 직후 사용자가 빈 화면(`ChunkLoadError`) | 재시도 + 자동 새로고침(무한 루프 방지) + 에러 UI |

## 측정과 검증

- **번들 분석**: `webpack-bundle-analyzer` 또는 `rollup-plugin-visualizer`(`gzipSize: true`)로 청크별 모듈 구성을 트리맵으로 확인한다.
- **라이트하우스**: FCP·LCP·TBT와 초기 리소스 수를 확인한다. 청크가 많아 FCP가 느리면 병합, 초기 번들이 커서 LCP가 느리면 분할.
- **Network 탭**: 초기 로드 청크 수(25개 이내), 라우트 이동 시 추가 로드 청크, 캐시 히트 여부(해시 동일성)를 확인한다.
- **캐시 효율 검증**: 코드 수정 → 재빌드 → `git diff dist/assets/`로 수정한 청크만 해시가 바뀌는지 확인한다.
- **실패 시나리오 테스트**: 개발자 도구에서 청크 요청을 차단해 에러 바운더리·재시도가 작동하는지, 이전 버전에서 새 버전 배포 시나리오가 처리되는지 테스트한다.
- **RUM**: 청크 로딩 실패율을 에러 추적 도구로 모니터링한다.

## 체크리스트

**분할 전략 수립**

- [ ] 번들 분석 도구로 현재 청크 구성 확인
- [ ] 라우트 기반 스플리팅 적용(페이지별 청크 분리)
- [ ] 대형 라이브러리(160KB 이상) 식별 및 지연 로딩 검토
- [ ] 조건부 렌더링되는 무거운 컴포넌트 분리(모달·차트·에디터)
- [ ] 사용 빈도가 낮은 기능 분리(어드민 페이지·고급 설정)

**청크 최적화**

- [ ] 벤더 청크 분리 설정(리액트·라우터 등 프레임워크)
- [ ] 대형 서드파티 모듈(160KB 이상) 별도 청크로 분리
- [ ] 중복 모듈 확인 및 공통 청크로 추출
- [ ] 트리 셰이킹 가능한 라이브러리 사용(lodash → lodash-es, moment → date-fns)
- [ ] 초기 요청 수 확인(25개 이내 권장)
- [ ] 초기 번들 크기 확인(gzip 기준 170KB 이하 권장)
- [ ] 최소 청크 크기 확인(20KB 이상 권장)

**UX 최적화**

- [ ] 각 라우트에 서스펜스 추가 및 폴백 UI 구현
- [ ] 스켈레톤 스크린 디자인(실제 레이아웃과 일치)
- [ ] 지연된 폴백 표시 구현(100~300ms delay)
- [ ] CSS 트랜지션으로 부드러운 전환(300ms fadeIn)
- [ ] 중첩된 서스펜스로 점진적 렌더링
- [ ] `useTransition`으로 페이지 전환 개선(선택)

**에러 처리**

- [ ] 에러 바운더리 구현(청크 로딩 실패 포착)
- [ ] 청크 로딩 에러 감지 로직(`ChunkLoadError`, `Failed to fetch`)
- [ ] 자동 재시도 메커니즘(최대 3번, 1초 간격)
- [ ] 동적 임포트에 `retryImport` 래퍼 적용
- [ ] 배포 시 자동 새로고침(`sessionStorage`로 무한 루프 방지)
- [ ] 페이지 단위 에러 바운더리 배치(에러 격리)

**모니터링 및 배포 전 확인**

- [ ] 번들 분석을 CI/CD 파이프라인에 통합
- [ ] 성능 예산 설정(청크 크기·초기 번들 크기)
- [ ] 청크 로딩 실패율 모니터링(RUM·에러 추적)
- [ ] 캐시 효율 확인(벤더 청크 해시 변경 빈도)
- [ ] 네트워크 스로틀링(Slow 4G)으로 느린 환경 테스트
- [ ] 청크 로딩 실패 시나리오 테스트(요청 차단)
- [ ] 이전 버전 → 새 버전 배포 시나리오 테스트
- [ ] 분기별 청크 구성 리뷰

## 요약

- 코드 스플리팅은 문법이 아니라 전략이다. **어디서 분할할지, 청크를 어떻게 구성할지, 로딩 실패를 어떻게 처리할지**의 종합 설계가 필요하다.
- 동적 `import()`는 번들러에게 "이 지점에서 분할하라"는 명령이다. 정적 import는 빌드 타임, 동적은 런타임에 의존성이 해결되며 이 차이가 번들 구성·로딩·캐싱 전반을 바꾼다.
- `React.lazy()`의 핵심 메커니즘은 **Promise를 throw**하고 서스펜스가 이를 받아 폴백을 렌더링하는 것이다. default export 필수, 서스펜스 경계 필수라는 제약이 여기서 나온다.
- 분할 지점의 황금 기준: **라우트 기반이 1순위**(사용자 행동과 코드 경계 일치), 그다음 모달·탭·권한 기반·뷰포트 기반 컴포넌트 레벨. **첫 화면 필수 요소와 핵심 인터랙션(결제 등)은 절대 지연 로딩하지 않는다.**
- 안티패턴 5종: 너무 작은 청크 남발, 첫 화면 지연 로딩, 공통 모듈 중복, 무분별한 라우트 분할, 핵심 플로 지연 로딩.
- 벤더 청크는 **변경 빈도**로 나눈다. 거의 안 바뀌는 프레임워크는 오래 캐시되고, 앱 코드 수정 시 재다운로드가 298KB → 16KB로 줄어든다.
- 균형 기준: **초기 요청 25개 이내, 초기 번들 gzip 170KB 이하, 최소 청크 20KB, 160KB 이상 서드파티는 분리.** 단, 절대 기준이 아니라 출발점이며 측정으로 조정한다.
- UX: 세분화된 서스펜스 경계 + 실제 레이아웃과 일치하는 스켈레톤 + **지연된 폴백(100~300ms 후 표시, 표시되면 300~500ms 유지)** + 중첩 서스펜스 점진 렌더링.
- 에러 처리: `ChunkLoadError` 감지 → 임포트 레벨 재시도(3회) → 배포 불일치 시 자동 새로고침 1회(`sessionStorage` 가드) → 최종적으로 명확한 안내 UI. **페이지 단위 격리**로 한 페이지의 실패가 앱 전체를 무너뜨리지 않게 한다.

## 다른 챕터와의 관계

- **Ch5(프리로드 스캐너)**: 동적으로 로드되는 청크는 프리로드 스캐너가 발견하지 못한다. 웹팩 매직 코멘트(`webpackPrefetch`/`webpackPreload`)가 그 보완책이었다.
- **Ch4(리소스 우선순위)**: 방문 확률 높은 라우트 청크의 `prefetch`·`modulepreload` 전략이 이 장의 분할 전략과 결합된다.
- **Ch3(브라우저 캐시)**: 내용 기반 해시 + 장기 캐싱이 벤더 청크 분리 전략의 전제다. 동적 청크에도 해시가 적용돼야 안전하다.
- **Ch9(불필요한 리소스 제거)**: Coverage로 찾은 "초기 로드 미사용 코드"가 이 장의 분할 후보 목록이 된다. 순서는 제거가 먼저, 분할이 나중이다.
- **Ch16(하이드레이션)**: 스트리밍 SSR과 서스펜스의 결합이 이 장의 서스펜스 개념을 서버 렌더링으로 확장한다.
- **Ch20(CLS)**: 스켈레톤과 실제 콘텐츠의 레이아웃 일치, `min-height` 확보가 CLS 방지 기법과 직결된다.
- **Ch24(다국어)**: 언어별 코드 스플리팅과 번역 파일 지연 로딩이 이 장의 전략을 다국어 도메인에 적용한 사례다.
