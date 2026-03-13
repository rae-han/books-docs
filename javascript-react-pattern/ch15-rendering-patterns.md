# Chapter 15: Rendering Patterns (렌더링 패턴)

## 핵심 질문

> 웹 콘텐츠를 어디서, 언제, 어떻게 렌더링해야 최적의 사용자 경험과 개발 경험을 동시에 달성할 수 있는가?

---

## 1. 렌더링 패턴의 중요성

웹 사이트가 점점 인터랙티브해짐에 따라, 클라이언트에서 처리해야 할 이벤트와 렌더링할 콘텐츠의 양이 크게 늘어났다. 리액트 같은 프레임워크를 사용한 SPA(*Single Page Application — 페이지 전환 없이 하나의 페이지에서 동적으로 콘텐츠를 교체하는 웹 애플리케이션*)가 등장했지만, 모든 페이지에 동일한 렌더링 전략을 적용하는 것은 올바르지 않다. 정적인 블로그 페이지와 동적인 대시보드는 근본적으로 다른 렌더링 요구 사항을 가진다.

올바른 렌더링 패턴을 선택하면 빠른 빌드 속도와 탁월한 로딩 성능을 낮은 비용으로 얻을 수 있다. 반면 잘못된 선택은 훌륭한 비즈니스 아이디어를 실현할 수 있는 애플리케이션을 망칠 수도 있다.

### 1.1 Core Web Vitals (핵심 웹 지표)

뛰어난 사용자 경험을 제공하려면 핵심 웹 지표(*Core Web Vitals, CWV*)를 기준으로 애플리케이션을 최적화해야 한다. CWV를 최적화하면 뛰어난 사용자 경험과 검색 엔진 최적화(*SEO — Search Engine Optimization*)를 동시에 보장할 수 있다.

| 지표 | 정식 명칭 | 설명 |
|------|-----------|------|
| **TTFB** | Time to First Byte | 클라이언트가 페이지 콘텐츠의 **첫 번째 바이트**를 받는 데 걸리는 시간 |
| **FCP** | First Contentful Paint | 브라우저가 콘텐츠의 **첫 부분**을 렌더링하는 데 걸리는 시간 |
| **LCP** | Largest Contentful Paint | 페이지의 **주요 콘텐츠**(가장 큰 요소)를 로드하고 렌더링하는 데 걸리는 시간 |
| **TTI** | Time to Interactive | 페이지 로드 시작부터 사용자 입력에 **빠르게 응답**할 수 있을 때까지 걸리는 시간 |
| **CLS** | Cumulative Layout Shift | 예상치 못한 **레이아웃 변경**을 방지하기 위한 시각적 안정성 측정 |
| **INP** | Interaction to Next Paint | 사용자 상호작용 후 **다음 프레임이 그려지기까지** 걸리는 시간 (FID를 대체) |

### 1.2 개발 경험 vs 사용자 경험

렌더링 패턴을 선택할 때는 사용자 경험뿐 아니라 개발 팀의 경험도 함께 고려해야 한다.

**개발 경험(DX) 최적화 기준:**

| 기준 | 설명 |
|------|------|
| **빠른 빌드 시간** | 빠른 반복 작업과 배포를 위해 프로젝트가 빠르게 빌드되어야 한다 |
| **낮은 서버 비용** | 서버 실행 시간을 제한하고 최적화하여 비용을 절감해야 한다 |
| **동적 콘텐츠** | 동적 콘텐츠를 효율적으로 로드할 수 있어야 한다 |
| **쉬운 롤백** | 이전 빌드 버전으로 빠르게 되돌릴 수 있어야 한다 |
| **확장 가능한 인프라** | 성능 문제 없이 프로젝트를 확장 또는 축소할 수 있어야 한다 |

### 1.3 렌더링 패턴 선택 기준

한 사용 사례에 유익한 패턴이 다른 사용 사례에서는 해로울 수 있다. 동일한 웹 사이트 내에서도 페이지 유형에 따라 다른 렌더링 패턴이 필요할 수 있다. 크롬 팀은 전체 페이지를 하이드레이션하는 방식보다 **정적 렌더링 또는 SSR** 사용을 권장하고 있다.

> **핵심 통찰**: 렌더링 패턴의 핵심은 "하나의 정답"이 아니라 **각 페이지의 특성에 맞는 최적의 전략을 선택하는 능력**에 있다. 정적 콘텐츠에 SSR을 적용하면 불필요한 서버 비용이 발생하고, 동적 콘텐츠에 SSG를 적용하면 오래된 데이터를 보여주게 된다.

---

## 2. 클라이언트 사이드 렌더링 (CSR)

클라이언트 사이드 렌더링(*Client-Side Rendering, CSR*)에서는 대부분의 애플리케이션 로직이 클라이언트에서 실행되며, 데이터를 가져오거나 저장하기 위한 API 호출로 서버와 상호작용한다. 거의 모든 UI가 클라이언트에서 생성되며, 전체 웹 애플리케이션은 첫 요청 시 모두 로드된다.

### 2.1 동작 방식

```
[브라우저 요청]
    ↓
[서버: 빈 HTML + JS 번들 전송]
    ↓
[브라우저: JS 다운로드 & 파싱]
    ↓
[브라우저: JS 실행 → DOM 생성]
    ↓
[브라우저: API 호출 → 데이터 fetching]
    ↓
[브라우저: 데이터로 UI 렌더링 완성]
```

사용자가 링크를 클릭해 페이지를 탐색할 때, 새로운 요청을 서버로 보내지 않는다. 대신 클라이언트에서 코드가 실행되어 뷰나 데이터를 교체한다. 이것이 SPA의 핵심 동작 방식이다.

### 2.2 장단점

| 장점 | 단점 |
|------|------|
| 페이지 전환이 빠르고 네이티브 앱과 유사한 경험 제공 | **FCP와 TTI가 길다** — 큰 JS 번들 다운로드 필요 |
| 서버 부하가 적음 (API 호출만 처리) | **SEO 불리** — 크롤러가 빈 HTML을 인덱싱할 수 있음 |
| 풍부한 상호작용 구현 용이 | 초기 로딩 시 빈 화면(흰 화면) 노출 |
| 오프라인 지원이 비교적 용이 | 디바이스 성능에 의존적 |

### 2.3 적합한 사용 사례

CSR은 **SEO가 중요하지 않고 풍부한 상호작용이 필요한 애플리케이션**에 적합하다.

- 관리자 대시보드
- 사내 도구 / 백오피스
- 소셜 미디어 피드 (예: Facebook, Twitter)
- 실시간 협업 도구 (예: Figma)
- SaaS 애플리케이션

```tsx
// 전형적인 CSR: React SPA
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </BrowserRouter>
  );
}

// 클라이언트에서 데이터를 fetching
function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);

  useEffect(() => {
    fetch("/api/dashboard")
      .then((res) => res.json())
      .then(setData);
  }, []);

  if (!data) return <Skeleton />;
  return <DashboardView data={data} />;
}
```

> **Osmani의 조언**: CSR의 과도한 자바스크립트 로딩은 성능을 저하시킬 수 있다. 그러나 정적인 웹 사이트에서도 어느 정도의 상호작용과 자바스크립트는 필요하다. 핵심은 CSR 수준의 상호작용성과 SSR 수준의 SEO 및 성능 이점 사이에서 균형을 찾는 것이다.

---

## 3. 서버 사이드 렌더링 (SSR)

서버 사이드 렌더링(*Server-Side Rendering, SSR*)은 모든 요청마다 서버에서 HTML을 생성한다. 이 방식은 사용자 쿠키 정보나 요청 데이터 기반의 개인 맞춤형 데이터를 포함하는 페이지에 가장 적합하다.

### 3.1 동작 방식

```
[브라우저 요청]
    ↓
[서버: 데이터 fetching + HTML 생성]
    ↓
[서버: 완성된 HTML 전송]
    ↓
[브라우저: HTML 렌더링 (FCP 발생)]
    ↓
[브라우저: JS 다운로드 & 실행]
    ↓
[브라우저: 하이드레이션 (TTI 발생)]
```

SSR에서는 데이터 연결 및 fetching 작업이 서버에서 처리된다. HTML 또한 서버에서 생성되므로, 클라이언트에서 데이터 fetching과 템플릿 처리를 위한 추가 왕복 시간을 줄일 수 있다.

### 3.2 하이드레이션 (Hydration)

하이드레이션(*Hydration — 서버에서 렌더링된 정적 HTML에 자바스크립트 이벤트 핸들러를 연결하여 상호작용 가능하게 만드는 과정*)은 SSR의 핵심 개념이다. 서버가 완성된 HTML을 보내면 브라우저는 즉시 콘텐츠를 표시할 수 있지만, 아직 이벤트 핸들러가 연결되지 않은 상태다. 하이드레이션 과정에서 리액트는 서버에서 보낸 HTML 위에 이벤트 핸들러를 연결하고, 가상 DOM을 재구성하여 UI를 상호작용 가능하게 만든다.

하이드레이션에는 비용이 따르기 때문에, SSR은 항상 하이드레이션 과정을 최적화하려고 한다.

### 3.3 장단점

| 장점 | 단점 |
|------|------|
| **SEO 우수** — 완성된 HTML을 크롤러에 제공 | **TTFB가 길다** — 매 요청마다 서버에서 HTML 생성 |
| FCP가 빠름 — 서버에서 완성된 HTML 즉시 표시 | 서버 부하 증가 — 모든 요청을 서버가 처리 |
| 느린 디바이스에서도 일관된 초기 렌더링 | 하이드레이션 비용 — TTI가 FCP보다 늦음 |
| 민감 데이터를 서버에서 안전하게 처리 | 서버 비용 증가 |

### 3.4 Next.js에서의 SSR

```tsx
// Pages Router 방식
export async function getServerSideProps(context: GetServerSidePropsContext) {
  const { req } = context;
  const session = await getSession(req);
  const userData = await fetchUserData(session.userId);

  return {
    props: { userData },
  };
}

export default function Dashboard({ userData }: { userData: UserData }) {
  return (
    <div>
      <h1>Welcome, {userData.name}</h1>
      <DashboardContent data={userData.dashboardData} />
    </div>
  );
}
```

```tsx
// App Router 방식 (서버 컴포넌트 + 동적 렌더링)
import { cookies } from "next/headers";

export default async function Dashboard() {
  const cookieStore = await cookies();
  const session = cookieStore.get("session");
  const userData = await fetchUserData(session?.value);

  return (
    <div>
      <h1>Welcome, {userData.name}</h1>
      <DashboardContent data={userData.dashboardData} />
    </div>
  );
}
```

> **핵심 통찰**: SSR에서 모든 요청은 독립적으로 처리된다. 연속된 두 요청의 결과가 크게 다르지 않더라도 서버는 처음부터 다시 처리하고 HTML을 생성한다. 이 "중복 처리" 문제를 해결하기 위해 ISR과 캐싱 전략이 등장했다.

---

## 4. 정적 사이트 생성 (SSG)

정적 렌더링(*Static Rendering / Static Site Generation, SSG*)은 전체 페이지의 HTML을 **빌드 시점**에 미리 생성하며, 다음 빌드 때까지 변경되지 않는다. 생성된 정적 HTML 콘텐츠는 CDN(*Content Delivery Network — 전 세계에 분산된 서버 네트워크를 통해 콘텐츠를 빠르게 제공하는 시스템*)이나 엣지 네트워크에 쉽게 캐싱될 수 있다.

### 4.1 빌드 타임 렌더링

정적 렌더링은 자주 변경되지 않고 누가 요청하든 동일한 데이터를 표시하는 페이지에 가장 적합하다.

```tsx
// Next.js App Router: 순수 정적 페이지
export default function About() {
  return (
    <div>
      <h1>About Us</h1>
      <p>회사 소개 내용...</p>
    </div>
  );
}
// next build 시 about.html로 미리 렌더링됨
```

```tsx
// 데이터를 포함한 정적 생성 (App Router)
export default async function BlogList() {
  // fetch의 기본 캐시 옵션으로 정적 생성
  const posts = await fetch("https://api.example.com/posts", {
    cache: "force-cache",
  }).then((res) => res.json());

  return (
    <ul>
      {posts.map((post: Post) => (
        <li key={post.id}>
          <Link href={`/blog/${post.slug}`}>{post.title}</Link>
        </li>
      ))}
    </ul>
  );
}
```

```tsx
// 동적 경로를 사용한 상세 페이지 정적 생성 (App Router)
export async function generateStaticParams() {
  const posts = await fetch("https://api.example.com/posts").then((res) =>
    res.json()
  );

  return posts.map((post: Post) => ({
    slug: post.slug,
  }));
}

export default async function BlogPost({
  params,
}: {
  params: { slug: string };
}) {
  const post = await fetch(
    `https://api.example.com/posts/${params.slug}`
  ).then((res) => res.json());

  return (
    <article>
      <h1>{post.title}</h1>
      <div dangerouslySetInnerHTML={{ __html: post.content }} />
    </article>
  );
}
```

### 4.2 클라이언트 사이드 데이터 fetching을 결합한 정적 렌더링

항상 최신 목록을 표시해야 하는 동적 리스트 페이지에서는, UI의 뼈대를 정적으로 렌더링하고 동적 데이터를 클라이언트에서 fetching하는 전략을 사용할 수 있다. SWR(*Stale-While-Revalidate — 캐시된 데이터를 먼저 보여주고 백그라운드에서 새 데이터를 가져와 업데이트하는 전략*)과 같은 라이브러리가 이 패턴에 유용하다.

### 4.3 장단점

| 장점 | 단점 |
|------|------|
| **TTFB가 매우 짧음** — CDN에서 캐시된 HTML 즉시 제공 | 빌드 시간이 페이지 수에 비례하여 증가 |
| **SEO 우수** — 완성된 HTML 제공 | **동적 콘텐츠 제한** — 빌드 이후 변경 불가 |
| 서버 부하 최소 — 정적 파일 제공 | 개인화된 콘텐츠 제공 어려움 |
| 캐싱 효율 극대화 | 데이터 업데이트 시 전체 재빌드 필요 |

### 4.4 적합한 사용 사례

- 블로그, 문서 사이트
- 마케팅 랜딩 페이지
- 회사 소개, 문의하기 페이지
- 상품 카탈로그 (변경이 드문 경우)

---

## 5. 점진적 정적 생성 (ISR)

점진적 정적 생성(*Incremental Static Regeneration, ISR*)은 정적 렌더링과 SSR을 결합한 방식으로, SSG의 한계를 극복한다. 특정 정적 페이지만 미리 렌더링하고, 동적 페이지는 사용자 요청 시 온디맨드 방식으로 렌더링한다.

### 5.1 SSG의 한계 극복

SSG는 빌드 이후 콘텐츠를 업데이트하려면 전체 사이트를 다시 빌드해야 한다. 수천 개의 상품 페이지를 가진 이커머스 사이트에서 하나의 가격이 변경될 때마다 전체를 재빌드하는 것은 비현실적이다. ISR은 이 문제를 두 가지 측면에서 해결한다.

**새로운 페이지 추가:**
빌드 후 웹 사이트에 새 페이지를 추가하기 위해 지연 로딩을 사용한다. 새로운 페이지는 첫 요청 시 즉시 생성되며, 생성 중에는 사용자에게 fallback 페이지나 로딩 화면을 보여줄 수 있다.

**기존 페이지 업데이트:**
각 페이지에 적절한 revalidate 타임아웃을 정의하고, 시간이 경과하면 페이지가 다시 유효한지 검증한다. 재검증이 완료될 때까지 사용자는 이전 버전의 페이지를 계속 보게 된다.

### 5.2 revalidate 메커니즘

ISR은 Stale-While-Revalidate 전략을 사용한다. 재검증이 진행되는 동안 사용자는 캐시된(이전) 버전을 보게 되고, 재검증은 백그라운드에서 이루어지며 전체 재빌드가 필요하지 않다.

```tsx
// Next.js App Router: ISR (시간 기반 재검증)
export default async function ProductList() {
  const products = await fetch("https://api.example.com/products", {
    next: { revalidate: 60 }, // 60초마다 재검증
  }).then((res) => res.json());

  return (
    <ul>
      {products.map((product: Product) => (
        <li key={product.id}>
          {product.name} - ${product.price}
        </li>
      ))}
    </ul>
  );
}
```

### 5.3 On-demand ISR

On-demand ISR은 일반 ISR과 달리, 정해진 시간 간격이 아니라 **특정 이벤트 발생 시** 페이지가 재생성된다. 일반 ISR에서는 업데이트된 페이지가 해당 페이지에 대한 사용자 요청을 처리한 엣지 네트워크 노드에만 캐시되지만, On-demand ISR은 엣지 네트워크 전체에 페이지를 다시 생성하고 재분배한다. 이를 통해 전 세계 사용자가 최신 버전의 페이지를 볼 수 있으며, 불필요한 페이지 재생성을 피하여 운영 비용을 절감할 수 있다.

```tsx
// Next.js: On-demand ISR을 위한 Revalidation API Route
import { revalidatePath } from "next/cache";

export async function POST(request: Request) {
  const { path, secret } = await request.json();

  if (secret !== process.env.REVALIDATION_SECRET) {
    return Response.json({ message: "Invalid secret" }, { status: 401 });
  }

  revalidatePath(path);
  return Response.json({ revalidated: true });
}
```

### 5.4 정적 렌더링 방식 비교

| 방식 | 적합한 사용 사례 |
|------|-----------------|
| **순수 정적 렌더링** | 동적 데이터가 없는 페이지 |
| **클라이언트 사이드 fetching + 정적 렌더링** | 매 로드 시 데이터가 새로고침되어야 하는 페이지 |
| **ISR (시간 기반)** | 특정 간격마다 재생성되어야 하는 페이지 |
| **On-demand ISR** | 특정 이벤트 발생 시 재생성되어야 하는 페이지 |

---

## 6. 스트리밍 SSR

스트리밍 SSR(*Streaming Server-Side Rendering*)은 서버에서 렌더링된 콘텐츠를 하나의 큰 HTML 파일로 한 번에 전송하는 대신, **작은 조각(청크)으로 나누어 전송**하는 방식이다. 이를 통해 FCP와 TTI를 더욱 단축할 수 있다.

### 6.1 React 18 Suspense + Streaming

Node.js의 스트림 기능을 사용하면 응답 객체에 데이터를 스트리밍할 수 있다. 클라이언트는 데이터 조각을 받는 즉시 콘텐츠 렌더링을 시작할 수 있어, 매우 빠른 초기 로딩 경험을 제공한다.

```tsx
// React 18+ Suspense를 활용한 스트리밍
import { Suspense } from "react";

export default function ProductPage() {
  return (
    <div>
      {/* 정적 콘텐츠는 즉시 스트리밍 */}
      <Header />
      <ProductInfo />

      {/* 동적 콘텐츠는 준비되면 스트리밍 */}
      <Suspense fallback={<ReviewsSkeleton />}>
        <ProductReviews />
      </Suspense>

      <Suspense fallback={<RecommendationsSkeleton />}>
        <Recommendations />
      </Suspense>

      <Footer />
    </div>
  );
}

// 비동기 서버 컴포넌트 — 데이터 준비되면 스트리밍
async function ProductReviews() {
  const reviews = await fetchReviews(); // 느린 API 호출
  return (
    <ul>
      {reviews.map((review: Review) => (
        <li key={review.id}>{review.text}</li>
      ))}
    </ul>
  );
}
```

스트리밍은 네트워크 정체에도 효과적이다. 네트워크가 혼잡한 경우 렌더러는 네트워크가 해소될 때까지 스트리밍을 중단한다. 서버는 메모리를 덜 사용하고, 여러 요청을 동시에 처리할 수 있으며, 무거운 요청이 가벼운 요청을 장시간 차단하는 것을 방지한다.

### 6.2 Selective Hydration

React 18의 Selective Hydration(*선택적 하이드레이션*)은 스트리밍 SSR과 결합하여 더욱 강력한 성능을 제공한다. 페이지의 모든 부분이 로드될 때까지 기다리지 않고, 준비된 부분부터 개별적으로 하이드레이션한다. 사용자가 아직 하이드레이션되지 않은 영역을 클릭하면, 리액트는 해당 영역의 하이드레이션을 우선적으로 처리한다.

### 6.3 장단점

| 장점 | 단점 |
|------|------|
| **FCP 매우 빠름** — 첫 청크 도착 즉시 렌더링 | 구현 복잡도 증가 |
| 네트워크 정체에 강함 | 클라이언트에서 점진적 렌더링 처리 필요 |
| 서버 메모리 효율적 | 일부 SEO 크롤러의 스트리밍 지원 제한 |
| TTI 개선 — 선택적 하이드레이션과 결합 | 상태 관리 복잡도 증가 |

---

## 7. React Server Components (RSC)

리액트 서버 컴포넌트(*React Server Components, RSC*)는 서버에서 실행되도록 설계된 상태를 가지지 않는 리액트 컴포넌트로, 서버 주도 방식으로 현대적인 사용자 경험을 제공하는 것을 목표로 한다.

### 7.1 서버 컴포넌트 vs 클라이언트 컴포넌트

RSC는 컴포넌트를 **서버 컴포넌트**와 **클라이언트 컴포넌트**로 명확히 구분한다.

| 특성 | 서버 컴포넌트 | 클라이언트 컴포넌트 |
|------|-------------|-------------------|
| **실행 위치** | 서버에서만 실행 | 서버(SSR) + 클라이언트 |
| **상태 관리** | `useState`, `useEffect` 사용 불가 | 모든 Hook 사용 가능 |
| **이벤트 핸들러** | `onClick` 등 사용 불가 | 자유롭게 사용 |
| **데이터 fetching** | `async/await`로 직접 fetch | `useEffect` 또는 라이브러리 사용 |
| **JS 번들 포함** | **포함되지 않음** (제로 번들) | 클라이언트 번들에 포함 |
| **서버 리소스 접근** | DB, 파일 시스템 직접 접근 가능 | API를 통해서만 접근 |

### 7.2 `"use client"` / `"use server"` 지시어

```tsx
// 서버 컴포넌트 (기본값 — 별도 지시어 불필요)
async function BlogPost({ slug }: { slug: string }) {
  // 서버에서 직접 데이터베이스 쿼리 가능
  const post = await db.post.findUnique({ where: { slug } });
  const comments = await db.comment.findMany({
    where: { postId: post.id },
  });

  return (
    <article>
      <h1>{post.title}</h1>
      <div>{post.content}</div>
      {/* 클라이언트 컴포넌트를 서버 컴포넌트 안에서 사용 */}
      <CommentSection initialComments={comments} postId={post.id} />
    </article>
  );
}
```

```tsx
"use client"; // 클라이언트 컴포넌트 선언

import { useState, useOptimistic } from "react";

function CommentSection({
  initialComments,
  postId,
}: {
  initialComments: Comment[];
  postId: string;
}) {
  const [comments, setComments] = useState(initialComments);
  const [newComment, setNewComment] = useState("");

  async function handleSubmit() {
    const response = await fetch(`/api/comments`, {
      method: "POST",
      body: JSON.stringify({ postId, text: newComment }),
    });
    const comment = await response.json();
    setComments([...comments, comment]);
    setNewComment("");
  }

  return (
    <div>
      <ul>
        {comments.map((c) => (
          <li key={c.id}>{c.text}</li>
        ))}
      </ul>
      <input value={newComment} onChange={(e) => setNewComment(e.target.value)} />
      <button onClick={handleSubmit}>댓글 작성</button>
    </div>
  );
}
```

```tsx
// Server Actions ("use server" 지시어)
async function addComment(formData: FormData) {
  "use server";

  const postId = formData.get("postId") as string;
  const text = formData.get("text") as string;

  await db.comment.create({
    data: { postId, text },
  });

  revalidatePath(`/blog/${postId}`);
}

// 서버 컴포넌트에서 Server Action 사용
function CommentForm({ postId }: { postId: string }) {
  return (
    <form action={addComment}>
      <input type="hidden" name="postId" value={postId} />
      <textarea name="text" placeholder="댓글을 입력하세요" />
      <button type="submit">작성</button>
    </form>
  );
}
```

### 7.3 제로 번들 서버 컴포넌트

서버 컴포넌트의 가장 큰 이점은 **클라이언트 번들에 포함되지 않는다**는 것이다. 서버 컴포넌트에서 사용하는 라이브러리(예: 마크다운 파서, 날짜 포매터, 구문 강조기 등)도 클라이언트로 전송되지 않아 번들 크기를 크게 줄일 수 있다.

```tsx
// 서버 컴포넌트: 이 import는 클라이언트 번들에 포함되지 않음
import { marked } from "marked";         // 25KB
import hljs from "highlight.js";         // 180KB
import { format } from "date-fns";       // 30KB

async function BlogPost({ slug }: { slug: string }) {
  const post = await db.post.findUnique({ where: { slug } });
  const htmlContent = marked(post.content, {
    highlight: (code, lang) => hljs.highlight(code, { language: lang }).value,
  });

  return (
    <article>
      <time>{format(post.createdAt, "yyyy-MM-dd")}</time>
      <div dangerouslySetInnerHTML={{ __html: htmlContent }} />
    </article>
  );
}
// 클라이언트로 전송되는 JS: 0 KB (서버에서만 실행)
```

### 7.4 RSC와 SSR의 차이

RSC는 SSR을 **대체하지 않는다**. 오히려 함께 사용할 때 최적의 결과를 제공한다.

| 구분 | SSR | RSC |
|------|-----|-----|
| **목적** | 초기 HTML을 빠르게 전달 | 클라이언트 번들 크기 감소 |
| **출력** | HTML 문자열 | 직렬화된 컴포넌트 트리 (RSC Payload) |
| **실행 시점** | 매 요청 또는 빌드 시 | 서버에서 컴포넌트 렌더링 시 |
| **하이드레이션** | 전체 페이지 하이드레이션 필요 | 서버 컴포넌트는 하이드레이션 불필요 |
| **상태 보존** | 페이지 전환 시 상태 초기화 | 클라이언트 상태를 유지하며 서버 트리 갱신 가능 |

RSC와 SSR을 함께 사용하면, 서버 컴포넌트 렌더링 결과를 SSR 인프라를 통해 HTML로 변환하여 초기 렌더링 속도를 빠르게 유지할 수 있다.

### 7.5 Next.js App Router에서의 구현

Next.js 13부터 도입된 App Router는 RSC를 기본으로 지원한다. `app` 디렉토리 내의 컴포넌트는 기본적으로 서버 컴포넌트로 설정되며, 자동으로 서버에서 렌더링되어 성능이 향상된다.

```
app/
├── layout.tsx          ← 서버 컴포넌트 (기본)
├── page.tsx            ← 서버 컴포넌트 (기본)
├── loading.tsx         ← Suspense fallback (스트리밍용)
├── error.tsx           ← "use client" (에러 바운더리)
├── blog/
│   ├── page.tsx        ← 서버 컴포넌트
│   └── [slug]/
│       └── page.tsx    ← 서버 컴포넌트
└── components/
    ├── Header.tsx      ← 서버 컴포넌트 (정적 네비게이션)
    ├── SearchBar.tsx   ← "use client" (상호작용 필요)
    └── ThemeToggle.tsx ← "use client" (상태 필요)
```

> **핵심 통찰**: RSC의 핵심 가치는 **"서버에서 할 수 있는 일은 서버에서 하라"**는 원칙이다. 데이터 fetching, 무거운 라이브러리 의존성, 민감 정보 처리를 서버에 두고, 상호작용이 필요한 최소한의 코드만 클라이언트로 전송한다. 이를 통해 클라이언트 번들 크기를 극적으로 줄이면서도 풍부한 사용자 경험을 유지할 수 있다.

---

## 8. 아일랜드 아키텍처 (Islands Architecture)

아일랜드 아키텍처(*Islands Architecture — 정적 HTML 바다 위에 독립적으로 하이드레이션되는 동적 컴포넌트 섬들을 배치하는 아키텍처*)는 케이티 사일러 밀러(*Katie Sylor-Miller*)와 제이슨 밀러(*Jason Miller*)가 대중화한 개념이다. 정적인 HTML 위에 독립적으로 전달될 수 있는 **상호작용 아일랜드**를 통해 자바스크립트 전송량을 줄이는 패러다임이다.

### 8.1 정적 바다 + 동적 섬

대부분의 웹 페이지는 정적 콘텐츠와 동적 콘텐츠가 결합된 형태다. 정적 콘텐츠 위에 상호작용 영역이 구분 가능하게 흩어져 있는 형태로 구성된다.

```
┌─────────────────────────────────────────────┐
│ [Header — 정적 HTML]                         │
├─────────────────────────────────────────────┤
│                                             │
│  정적 텍스트 콘텐츠 (HTML만, JS 없음)          │
│                                             │
│  ┌─────────────┐   정적 이미지와 텍스트       │
│  │ 🏝️ 검색 바  │                            │
│  │ (동적 아일랜드)│                            │
│  └─────────────┘                            │
│                                             │
│  더 많은 정적 콘텐츠...                        │
│                                             │
│  ┌──────────────────┐                       │
│  │ 🏝️ 이미지 캐러셀  │                       │
│  │ (동적 아일랜드)    │                       │
│  └──────────────────┘                       │
│                                             │
│  정적 푸터 (HTML만, JS 없음)                   │
└─────────────────────────────────────────────┘
```

- **정적 부분(바다)**: 순수한 비상호작용 HTML이며 하이드레이션이 필요하지 않다.
- **동적 부분(섬)**: HTML과 자바스크립트가 결합되어 렌더링 후 스스로 하이드레이션할 수 있다.

### 8.2 아일랜드 아키텍처 구현 프레임워크

**Astro:**
리액트, 스벨트, Preact, Vue.js 등 다양한 프레임워크의 UI 컴포넌트를 사용하여 가벼운 정적 HTML 페이지를 생성하는 정적 사이트 빌더다. 클라이언트 사이드 자바스크립트가 필요한 컴포넌트만 의존성과 함께 개별적으로 로드하여 기본적으로 부분 하이드레이션을 제공한다.

```astro
---
// Astro 컴포넌트: 정적 HTML + 선택적 아일랜드
import Header from "../components/Header.astro";  // 정적 (JS 없음)
import SearchBar from "../components/SearchBar";   // React 컴포넌트
import Footer from "../components/Footer.astro";   // 정적 (JS 없음)
---

<Header />
<main>
  <h1>블로그</h1>
  <p>정적 콘텐츠입니다. JS가 전혀 필요하지 않습니다.</p>

  <!-- client:visible — 뷰포트에 진입할 때만 하이드레이션 -->
  <SearchBar client:visible />

  <article>
    <p>더 많은 정적 콘텐츠...</p>
  </article>
</main>
<Footer />
```

**Marko:**
eBay에서 개발 및 유지보수하는 오픈 소스 프레임워크로, 스트리밍 렌더링과 자동 부분 하이드레이션을 결합하여 아일랜드 아키텍처를 지원한다. 브라우저에서 상태를 변경할 수 있는 상호작용 컴포넌트에 대해서만 하이드레이션 코드가 전송된다.

### 8.3 Partial Hydration과의 관계

아일랜드 아키텍처는 점진적 하이드레이션(*Progressive Hydration*)과 혼동될 수 있지만 뚜렷한 차이가 있다.

| 구분 | 점진적 하이드레이션 | 아일랜드 아키텍처 |
|------|-------------------|-----------------|
| **하이드레이션 제어** | 페이지가 하향식(top-down)으로 제어 | 각 컴포넌트가 자체적으로 하이드레이션 |
| **스크립트 의존성** | 페이지 전체의 스크립트 그래프에 의존 | 각 아일랜드가 독립적 스크립트 보유 |
| **성능 격리** | 특정 컴포넌트 문제가 전체에 영향 | 특정 아일랜드의 문제가 다른 아일랜드에 영향 없음 |

### 8.4 장단점

| 장점 | 단점 |
|------|------|
| **JS 전송량 최소화** — 상호작용 컴포넌트만 | 아직 제한된 프레임워크 선택지 |
| **SEO 우수** — 서버 렌더링 정적 콘텐츠 | 기존 SPA 코드베이스 마이그레이션 비용 |
| 핵심 콘텐츠 즉시 표시 | 상호작용 위주 애플리케이션에 부적합 |
| 컴포넌트 기반 아키텍처의 재사용성 | 아일랜드 간 상태 공유 복잡 |

> **Osmani의 조언**: 아일랜드 아키텍처는 수천 개의 아일랜드가 필요한 소셜 미디어 애플리케이션에는 적합하지 않다. 정적 콘텐츠가 대부분이고 동적 영역이 제한적인 사이트에서 가장 빛을 발한다.

---

## 9. 렌더링 패턴 비교

### 9.1 주요 지표별 비교

| 패턴 | TTFB | FCP | TTI | SEO | 서버 비용 | 복잡도 |
|------|------|-----|-----|-----|----------|--------|
| **CSR** | 짧음 | 느림 | 매우 느림 | 낮음 | 낮음 | 낮음 |
| **SSR** | 김 | 빠름 | 느림 (하이드레이션) | 높음 | 높음 | 중간 |
| **SSG** | 매우 짧음 | 매우 빠름 | 빠름 | 높음 | 매우 낮음 | 낮음 |
| **ISR** | 매우 짧음 | 매우 빠름 | 빠름 | 높음 | 낮음 | 중간 |
| **스트리밍 SSR** | 짧음~중간 | 매우 빠름 | 중간 | 높음 | 중간 | 높음 |
| **RSC** | 짧음~중간 | 빠름 | 빠름 | 높음 | 중간 | 높음 |
| **아일랜드** | 매우 짧음 | 매우 빠름 | 빠름 | 높음 | 매우 낮음 | 중간 |

### 9.2 사용 사례별 추천 패턴

| 애플리케이션 유형 | 예시 | 추천 패턴 | 이유 |
|-----------------|------|----------|------|
| **개인 블로그** | 포트폴리오, 기술 블로그 | SSG / 아일랜드 | 정적 콘텐츠 위주, CDN 캐싱 극대화 |
| **콘텐츠 중심 사이트** | CNN, 뉴스 매거진 | SSG + ISR | 정적 생성 + 주기적 업데이트 |
| **이커머스** | 아마존, 쇼핑몰 | SSR + 스트리밍 | 개인화 + 빠른 초기 로딩 |
| **SNS** | 소셜 네트워크 | CSR / RSC + SSR | 실시간 상호작용 + 동시성 |
| **몰입형 앱** | Figma, Google Docs | CSR | 극도의 상호작용, SEO 불필요 |
| **대시보드** | 관리자 패널, 분석 도구 | CSR / RSC | 인증 기반, SEO 불필요 |
| **문서 사이트** | API 문서, 가이드 | SSG + 아일랜드 | 정적 콘텐츠 + 검색/네비게이션 아일랜드 |

### 9.3 애플리케이션 유형별 프레임워크 추천

| 유형 | 상호작용 | 중요 가치 | 렌더링 | 추천 프레임워크 |
|------|---------|----------|--------|-------------|
| 포트폴리오 | 최소 | 단순함 | 정적 | 11ty, Astro |
| 콘텐츠 중심 | 링크된 기사 | 도달 가능성 | 정적, SSR | Astro, Elder |
| 쇼핑몰 | 구매 동선 | 성능 | 정적, SSR | Marko, Qwik, Hydrogen |
| SNS | 실시간 | 역동성 | SSR | Next.js, Remix |
| 몰입형 앱 | 모든 요소 | 몰입감 | CSR | Create React App, Vite |

---

## 10. 하이브리드 렌더링과 미래

### 10.1 페이지별 다른 렌더링 전략

하이브리드 렌더링(*Hybrid Rendering*)은 여러 렌더링 방식을 결합하여 각 상황에 최적의 결과를 제공한다. 이는 클라이언트 중심의 관점에서 벗어나 **더욱 다재다능한 렌더링 전략의 조합**으로 나아가는 근본적인 변화를 의미한다.

웹 애플리케이션은 더 이상 SPA 또는 MPA(*Multi-Page Application*)로 분류될 필요가 없다. 정적으로 제공될 수 있는 페이지는 미리 렌더링되고, 다른 페이지에는 ISR, SSR, CSR, 스트리밍 등 동적인 전략을 페이지별로 선택할 수 있다.

```
웹 애플리케이션
├── /                → SSG (정적 랜딩 페이지)
├── /blog            → SSG + ISR (블로그 목록)
├── /blog/[slug]     → SSG (개별 포스트)
├── /dashboard       → SSR + RSC (인증된 동적 페이지)
├── /search          → 스트리밍 SSR (검색 결과)
├── /settings        → CSR (클라이언트 전용)
└── /docs            → SSG + 아일랜드 (문서 + 검색)
```

하이브리드 렌더링을 지원하는 대표적인 프레임워크:

- **Next.js**: RSC와 App Router를 결합한 하이브리드 렌더링
- **Astro**: SSG와 SSR의 장점을 동시에 활용
- **Nuxt 3**: 하이브리드 렌더링을 위한 라우팅 규칙 설정 지원
- **Angular**: 네이티브 하이브리드 렌더링 지원

### 10.2 Partial Prerendering (Next.js 15)

Partial Prerendering(*PPR — 부분 사전 렌더링*)은 Next.js 15에서 도입된 실험적 기능으로, **하나의 페이지 내에서 정적 부분과 동적 부분을 분리**하여 렌더링한다. 기존에는 페이지 단위로 정적/동적을 결정했지만, PPR은 컴포넌트 단위로 이를 결정한다.

```tsx
// Next.js 15 PPR: 하나의 페이지에서 정적 + 동적 결합
export default function ProductPage({ params }: { params: { id: string } }) {
  return (
    <div>
      {/* 정적 셸: 빌드 타임에 사전 렌더링 → CDN 캐싱 */}
      <Header />
      <ProductInfo id={params.id} />

      {/* 동적 부분: 요청 시 서버에서 스트리밍 */}
      <Suspense fallback={<PriceSkeleton />}>
        <DynamicPrice id={params.id} />
      </Suspense>

      <Suspense fallback={<ReviewsSkeleton />}>
        <PersonalizedReviews id={params.id} />
      </Suspense>

      <Footer />
    </div>
  );
}
```

PPR의 동작 방식:
1. **빌드 시**: 정적 셸(Header, Footer, 레이아웃)을 사전 렌더링하여 CDN에 배포
2. **요청 시**: 정적 셸을 즉시 전송하고, 동적 부분은 Suspense 경계에서 스트리밍
3. **결과**: SSG 수준의 TTFB + SSR 수준의 동적 콘텐츠

### 10.3 View Transitions API

View Transitions API는 페이지 전환 시 네이티브 수준의 부드러운 애니메이션을 제공하는 브라우저 API다. MPA에서도 SPA와 같은 매끄러운 전환 경험을 구현할 수 있게 해주며, 하이브리드 렌더링의 사용자 경험을 한 단계 끌어올린다.

```tsx
// Next.js에서 View Transitions 활용
"use client";

import { useRouter } from "next/navigation";

function NavigationLink({ href, children }: { href: string; children: React.ReactNode }) {
  const router = useRouter();

  function handleClick(e: React.MouseEvent) {
    e.preventDefault();

    // View Transitions API 사용
    if (document.startViewTransition) {
      document.startViewTransition(() => {
        router.push(href);
      });
    } else {
      router.push(href);
    }
  }

  return <a href={href} onClick={handleClick}>{children}</a>;
}
```

---

## 최신 업데이트 (2026)

원서(2023) 이후 렌더링 패턴 생태계에 중요한 변화가 있었다.

| 영역 | 변화 |
|------|------|
| **React 19 RSC** | RSC 안정화, `use()` Hook으로 서버 데이터 소비 간소화, Server Actions 공식 지원, React Compiler를 통한 자동 최적화 |
| **Next.js 15** | Partial Prerendering(PPR) 실험적 도입, `after()` API로 응답 후 작업 실행, 캐싱 기본 동작 변경 (fetch 기본 no-store) |
| **View Transitions** | Chrome에서 MPA View Transitions 지원, Next.js/Astro 등 프레임워크 통합 진행 중 |
| **Astro 5** | Server Islands, Content Layer API, 성능 개선 |
| **아일랜드 확산** | Fresh (Deno), Qwik (Resumability), Solid Start 등 아일랜드/부분 하이드레이션 접근 확대 |
| **엣지 렌더링** | Vercel Edge Runtime, Cloudflare Workers 등에서 서버 컴포넌트 실행 가능, 글로벌 저지연 SSR 실현 |
| **INP 대체** | Google이 FID를 INP(Interaction to Next Paint)로 공식 대체, 전체 상호작용 응답성 측정으로 전환 |

---

## 실무 적용 가이드

### 패턴 선택 의사결정 트리

```
페이지에 동적 데이터가 필요한가?
├── 아니오 → SSG (정적 사이트 생성)
│            └── 검색/필터 등 상호작용이 필요한가?
│                 ├── 아니오 → 순수 SSG
│                 └── 예 → 아일랜드 아키텍처 (Astro)
└── 예 → 데이터가 사용자별로 다른가?
         ├── 아니오 → ISR (주기적 재생성)
         │            └── 실시간성이 중요한가?
         │                 ├── 아니오 → 시간 기반 ISR
         │                 └── 예 → On-demand ISR
         └── 예 → 초기 로딩 속도가 중요한가?
                  ├── 예 → SSR + 스트리밍 / RSC
                  │         └── 부분 정적+동적이 혼합?
                  │              └── 예 → PPR (Next.js 15)
                  └── 아니오 → CSR (SPA)
```

### 하이브리드 전략 실무 예시

실제 이커머스 사이트를 예로 들면:

| 페이지 | 패턴 | 이유 |
|--------|------|------|
| 홈 | SSG + ISR | 프로모션 배너는 주기적 업데이트 |
| 상품 목록 | ISR (60초) | 재고/가격 주기적 갱신 |
| 상품 상세 | PPR | 정적 셸 + 동적 가격/재고 |
| 장바구니 | CSR | 완전히 사용자별 상태 |
| 결제 | SSR | 보안 + 인증 필수 |
| 고객센터 FAQ | SSG | 순수 정적 콘텐츠 |
| 블로그 | SSG + 아일랜드 | 정적 콘텐츠 + 댓글 위젯 |

---

## 요약

- 렌더링 패턴의 선택은 **Core Web Vitals(TTFB, FCP, LCP, TTI, CLS, INP)**과 **개발 경험(DX)**을 기준으로 이루어져야 한다
- **CSR**은 풍부한 상호작용에 강하지만 초기 로딩과 SEO에 약하다
- **SSR**은 SEO와 초기 콘텐츠 표시에 강하지만 서버 부하와 TTFB가 과제다
- **SSG**는 성능과 비용 면에서 최적이지만 동적 콘텐츠 제공이 제한적이다
- **ISR**은 SSG의 한계를 극복하여 정적 생성과 동적 업데이트를 결합한다
- **스트리밍 SSR**은 React Suspense와 결합하여 FCP를 극적으로 단축하고 선택적 하이드레이션을 가능하게 한다
- **RSC**는 서버 컴포넌트와 클라이언트 컴포넌트를 분리하여 번들 크기를 최소화하며, SSR을 대체하지 않고 보완한다
- **아일랜드 아키텍처**는 정적 HTML 위에 독립적인 동적 섬을 배치하여 자바스크립트 전송량을 최소화한다
- **하이브리드 렌더링**은 페이지별로 다른 전략을 적용하는 현대 웹의 방향이며, PPR은 이를 컴포넌트 단위로 확장한다
- 하나의 정답은 없다. **각 페이지의 특성에 맞는 최적의 전략을 선택하는 것**이 핵심이다

---

## 다른 챕터와의 관계

- **← Ch12 (리액트 패턴)**: HOC, Hooks, Compound 패턴 등 리액트의 구성 패턴이 렌더링 패턴과 어떻게 결합되는지 이해할 수 있다
- **← Ch13 (리액트 렌더링 최적화)**: `React.memo`, `useMemo`, 코드 스플리팅 등의 성능 최적화 기법이 렌더링 패턴 내에서 어떻게 작동하는지 다룬다
- **← Ch14 (리액트 애플리케이션 구조)**: 프로젝트 구조와 아키텍처가 렌더링 전략 선택에 미치는 영향을 다룬다
- **← Ch01 (디자인 패턴 소개)**: 디자인 패턴의 본질인 "반복되는 문제에 대한 검증된 해결책"이라는 원칙이 렌더링 패턴에도 동일하게 적용된다