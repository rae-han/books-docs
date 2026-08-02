# Chapter 11: 서버가 할 수 있는 일은 클라이언트가 하지 않게 하라

## 핵심 질문

SPA 시대에 서버에서 클라이언트로 옮겨온 로직들 — 데이터 가공, 검증, 계산 — 이 정말 브라우저에서 실행돼야 하는가? 클라이언트가 반드시 해야 할 일과 서버에서 처리해도 되는 일을 어떻게 구분하며, 리액트 서버 컴포넌트는 이 문제를 어떻게 근본적으로 해결하는가?

## 1. 클라이언트 중심 개발의 함정

### 1.1 SPA가 가져온 번들 크기 폭발

SPA는 페이지 전환 시 전체 HTML을 다시 받는 대신 자바스크립트로 필요한 부분만 동적으로 렌더링한다. 깜빡임 없는 부드러운 경험이라는 장점 뒤에는 대가가 있다. **라우팅·상태 관리·렌더링 로직을 모두 클라이언트가 담당**해야 하므로 라우터, 상태 관리 라이브러리, 프레임워크 런타임, UI 컴포넌트 라이브러리가 전부 번들에 포함된다.

실제로 많은 SPA의 초기 번들이 500KB를 넘고 대규모 애플리케이션은 1~2MB에 달한다. 문제는 다운로드만이 아니다 — **다운로드한 자바스크립트를 파싱·컴파일·실행하는 동안 메인 스레드가 블로킹된다.** Slow 4G(1.44Mbps) 기준 1MB 압축 자바스크립트 다운로드에 약 5.6초, 중저사양 모바일에서 파싱·실행에 추가로 수 초가 걸린다. HTTP Archive 통계로 모바일 중간값 자바스크립트 크기는 2019년 8월 약 377KB에서 2025년 10월 약 680KB로, **연평균 약 13%씩 증가**하고 있다.

극단적 사례가 지메일이다. 2025년 10월 측정 기준 초기 로딩 시 **약 30MB의 자바스크립트 리소스**(압축 전송 약 4MB)를 다운로드하고, 570개 요청 중 146개가 자바스크립트 관련이며, 전체 로딩 완료까지 32초 이상 걸렸다.

> **핵심 통찰**: 지메일은 코드 스플리팅·지연 로딩·서비스 워커 캐싱 등 고도의 최적화를 적용했고 재방문은 훨씬 빠르다. 그럼에도 이 사례가 보여주는 것은 명확하다. **번들 크기 자체가 크면 아무리 최적화해도 첫 방문 시 한계가 있다.** 고도의 최적화 기법보다 **애초에 서버와 클라이언트의 역할을 적절히 분담해 클라이언트 번들을 줄이는 편**이 훨씬 현실적이고 효과적이다.

### 1.2 클라이언트에서 모든 것을 처리하려는 시도의 문제

"서버는 JSON API만 제공하고 나머지는 클라이언트"라는 구조는 프런트/백 분리라는 장점이 있지만 클라이언트에 과도한 책임을 부여한다. **언뜻 클라이언트 작업 같지만 실제로는 성능 문제를 일으키는** 세 가지 실전 사례를 보자.

**① 검색 자동완성 — 클라이언트 퍼지 검색**

전체 상품 데이터를 내려받아 Fuse.js로 검색하는 구현의 문제: ① 5,000개 상품 데이터 전체 다운로드로 약 2MB 전송, ② Fuse.js 약 20KB가 번들에 포함, ③ 데이터가 많을수록 퍼지 검색 연산이 무거워져 **타이핑마다 UI가 버벅임**, ④ 검색 인덱스를 메모리에 유지해야 함. 서버에서 PostgreSQL 전문 검색이나 엘라스틱서치를 쓰면 클라이언트는 쿼리를 보내고 결과만 표시하면 된다.

**② CSV/엑셀 파일 처리 — SheetJS 클라이언트 파싱**

"파일을 읽는 건 당연히 클라이언트 작업 아닌가?"라고 생각하기 쉽지만: ① SheetJS는 압축 후에도 약 180KB, ② 10,000행 이상 대용량 파일 파싱 시 **메인 스레드가 수 초간 블로킹되어 페이지가 완전히 멈춤**, ③ 파싱된 JSON이 메모리에 올라가 사용량 급증, ④ 검증까지 하면 부담이 배가된다. 서버에서 스트리밍 파싱·검증하면 클라이언트는 업로드와 진행 상황 표시만 담당한다.

> **실무 팁**: 민감한 데이터가 포함된 파일은 보안상 서버로 전송할 수 없는 경우도 있다. 이때는 **웹 워커**로 메인 스레드를 블로킹하지 않으면서 클라이언트에서 파싱하는 것이 대안이다.

**③ 마크다운 에디터 실시간 프리뷰**

marked(50KB) + DOMPurify(45KB) + highlight.js(75KB) = **총 170KB**가 번들에 포함되고, 타이핑마다 파싱이 실행되어 긴 문서에서 반응이 느려지며, 정규식 연산과 HTML 생성이 메인 스레드를 블로킹한다. 대안: 서버 변환 API + debounce(타이핑 멈춘 후 0.5초 뒤 요청). 깃허브·노션도 유사한 방식을 쓴다.

### 1.3 서버와 클라이언트의 최적 역할 분담 기준

**클라이언트에서 처리해야 할 것** — 사용자와 직접 상호작용하는 부분:

- **UI 상태 관리**: 모달 열림/닫힘, 탭 전환, 아코디언 확장 같은 순수 UI 상태
- **입력 중 즉각 피드백**: 문자 수 표시, 실시간 자동완성 표시, 기본 형식 검증
- **클라이언트 전용 로직**: 드래그 앤드 드롭, 애니메이션, 캔버스 조작 등 브라우저 API 활용
- **오프라인 기능**: 서비스 워커 오프라인 지원, 로컬 캐싱

**서버에서 처리해야 할 것** — 데이터 처리·비즈니스 로직·보안:

- **데이터 필터링·정렬**: 큰 데이터셋의 검색, 필터링, 정렬, 페이지네이션
- **복잡한 계산**: 할인 계산, 통계 집계, 데이터 분석
- **비즈니스 규칙 검증**: 재고 확인, 쿠폰 유효성, 권한 체크
- **데이터 가공**: 날짜 포매팅, 텍스트 변환, 이미지 리사이징
- **보안 관련 로직**: 인증, 권한 부여, 민감 데이터 처리

**실용적 의사결정 4문**

1. **이 로직이 없어도 사용자가 콘텐츠를 볼 수 있는가?** 콘텐츠 표시에 필수라면 서버에서 처리해 SSR로 제공. 필터·정렬 UI 조작은 클라이언트.
2. **클라이언트에서 처리하면 코드가 얼마나 추가되는가?** 10KB 미만 유틸리티는 클라이언트 OK, **50KB 이상 라이브러리가 필요하면 서버 검토.**
3. **즉각적인 응답이 필요한가?** 타이핑 중 실시간 반응은 클라이언트, 폼 제출 후 검증은 서버.
4. **보안이 중요한가?** 가격 계산·할인·권한은 반드시 서버. **클라이언트 로직은 쉽게 조작된다.**

```ts
// 서버: 필터링·정렬·페이지네이션 + 필요한 필드만 선택
app.get('/api/products', async (req, res) => {
  const { category, sort, page = 1 } = req.query;

  const products = await db.products
    .where('category', category)
    .orderBy(sort, 'asc')
    .paginate(page, 20);

  // 필요한 필드만 선택해 응답 크기 최소화
  const simplified = products.map((p) => ({
    id: p.id,
    name: p.name,
    price: p.price,
    image: p.thumbnail_url,  // 작은 섬네일만 전달
    inStock: p.stock > 0,
  }));

  res.json({ products: simplified, total: products.total, hasMore: products.hasMore });
});
```

```tsx
// 클라이언트: UI 상태 관리와 렌더링에만 집중
function ProductList() {
  const [category, setCategory] = useState('all');
  const [sortBy, setSortBy] = useState('price');
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery(['products', category, sortBy, page], () =>
    fetch(`/api/products?category=${category}&sort=${sortBy}&page=${page}`).then((r) => r.json()),
  );

  return (
    <div>
      <CategoryFilter value={category} onChange={setCategory} />
      <SortSelect value={sortBy} onChange={setSortBy} />
      {isLoading ? <Spinner /> : <ProductGrid products={data.products} />}
      {data?.hasMore && <button onClick={() => setPage((p) => p + 1)}>더 보기</button>}
    </div>
  );
}
```

> **핵심 통찰**: 역할 분담의 핵심은 **"클라이언트를 가볍게, 서버는 똑똑하게"**다. 클라이언트는 빠르게 로드되고 부드럽게 동작하는 데 집중하고, 무거운 작업은 서버에 맡긴다.

## 2. 클라이언트 로직을 서버로 이동하기

모든 로직을 무조건 서버로 옮기면 오히려 네트워크 왕복이 늘어 UX가 나빠진다. **명확한 이점이 있는 로직 유형**만 옮긴다.

### 2.1 서버로 옮기면 좋은 로직 유형

**① 복잡한 데이터 구조 변환**

여러 데이터 소스 조합(상품+재고+가격+리뷰), 중첩 구조 평탄화, 복잡한 계산이 있는 변환 로직. 클라이언트에서 lodash(약 70KB)로 `useMemo` 연산을 돌리는 대신 서버 API가 이미 UI에 최적화된 형태로 변환해 내려준다. 서버는 DB 쿼리를 `Promise.all`로 병렬 실행할 수 있어 오히려 빠르다.

**② 대용량 데이터 필터링·집계**

수천 건 이상은 반드시 서버에서 처리한다. 수만 건의 판매 데이터를 전부 내려받아 클라이언트에서 월별 합계를 계산하는 대신, DB 집계 쿼리(MongoDB `aggregate`, SQL `GROUP BY`)로 12개월치 요약만 전송한다. **네트워크 전송량이 수 MB → 수 KB로** 줄고 클라이언트 메모리·연산 부담이 사라진다.

**③ 복잡한 비즈니스 로직**

할인·세금·배송비·포인트 규칙은 서버에서 처리한다. 이유는 성능보다 **보안**이다 — 클라이언트 할인 계산은 개발자 도구로 조작 가능하고, 규칙이 바뀔 때마다 클라이언트를 재배포해야 한다.

```ts
// 서버에서 검증된 할인 계산
app.post('/api/cart/calculate', async (req, res) => {
  const { items, userId, coupons } = req.body;
  const user = await db.users.findById(userId);
  const subtotal = items.reduce((sum, item) => sum + item.price * item.quantity, 0);

  const discount = await discountService.calculate({ subtotal, user, coupons, items });

  res.json({ subtotal, discount, total: subtotal - discount, breakdown: discount.breakdown });
});
```

**④ 무거운 라이브러리가 필요한 작업**

마크다운 파싱(marked ~50KB), PDF 생성(jsPDF ~200KB), 이미지 변환 같은 작업은 서버로 옮긴다. 마크다운을 서버에서 HTML로 변환해 전달하면 클라이언트 번들에서 약 95KB(marked+DOMPurify)를 제거하고 파싱 연산도 서버에서 한 번만 수행한다.

### 2.2 API 응답 최적화: BFF와 GraphQL

서버로 로직을 옮기는 것만큼 중요한 것이 **데이터 전송 최적화**다. 화면에 필요한 데이터만 정확히 받으면 페이로드가 줄고 클라이언트 가공 로직도 단순해진다.

**BFF(*Backend for Frontend*): 맞춤형 데이터 제공**

범용 REST API는 여러 클라이언트를 만족시켜야 하므로 특정 화면에는 불필요한 데이터까지 포함된 거대한 응답을 보낸다(**오버 페치**). 프로필 화면에는 이름·아바타만 필요한데 전체 주문 내역·주소·포인트까지 내려오는 식이다.

BFF는 프런트엔드와 백엔드 사이의 중간 레이어로, 클라이언트 요구에 딱 맞는 형태로 데이터를 가공해 내려준다.

```ts
// BFF — 백엔드 마이크로서비스 호출 후 필요한 데이터만 조합
app.get('/bff/user-profile', async (req, res) => {
  const userId = req.user.id;

  const user = await userService.getUser(userId);
  const orders = await orderService.getRecentOrders(userId);

  res.json({
    name: user.name,
    avatarUrl: user.profileImage,
    lastOrderDate: orders.length > 0 ? orders[0].date : null,
    totalOrderCount: user.orderCount,
  });
});
```

클라이언트는 가공·필터링 없이 데이터를 그대로 UI에 바인딩한다. **Next.js API Routes를 쓰면 별도 서버 구축 없이 BFF 패턴을 구현할 수 있다.**

**GraphQL: 필요한 데이터만 골라 받기**

REST는 엔드포인트가 고정돼 있어 화면이 바뀌면 API를 수정하거나 여러 API를 조합해야 한다(**언더 페치**). GraphQL은 클라이언트가 필요한 데이터 구조를 쿼리로 명시하면 서버가 정확히 그 구조로 반환해 오버 페치와 언더 페치를 동시에 해결한다. 여러 리소스를 한 번의 요청으로 가져와 HTTP 요청 횟수도 줄고, 데이터 조회·조합 로직이 서버 리졸버로 이동한다.

**도입 시 고려사항**

- **BFF**: 추가 서버 레이어로 운영 복잡도 증가, 플랫폼별 BFF는 유지보수 비용 증가, BFF 자체가 SPOF(단일 장애 지점)가 될 수 있음, 백엔드 API 변경 시 함께 수정 필요.
- **GraphQL**: 학습 곡선, N+1 쿼리 방지를 위한 DataLoader 배칭 필요, 복잡한 쿼리의 서버 부하(쿼리 깊이 제한·복잡도 분석 필요), REST보다 복잡한 캐싱, 기존 모니터링 도구와의 차이.

> **실무 팁**: 점진적으로 도입한다. BFF는 Next.js API Routes나 리믹스 loader처럼 **프레임워크 내장 기능부터**, GraphQL은 **새 기능이나 성능 문제가 있는 특정 화면부터** 적용해 효과를 검증한 후 확대한다.

## 3. 리액트 서버 컴포넌트

### 3.1 기존 SSR의 한계와 서버 컴포넌트가 필요한 이유

`getServerSideProps` 같은 전통적 SSR은 초기 로딩을 개선하지만 근본적 한계가 있다.

1. **서버에서 HTML을 만들어도 하이드레이션을 위해 모든 컴포넌트의 자바스크립트가 클라이언트 번들에 포함돼야 한다.** 같은 코드를 서버와 클라이언트에서 두 번 실행하는 셈이다.
2. **페이지 레벨에서만 작동한다.** 개별 컴포넌트가 필요한 데이터를 독립적으로 가져올 수 없어, 모든 데이터 페칭이 페이지 파일에 집중된다. `PostList`가 어떤 데이터를 쓰는지 알려면 페이지 파일을 봐야 하고, 순차 페칭 시 워터폴이 발생한다.
3. **하이드레이션 오버헤드.** 번들을 100KB로 줄여도 하이드레이션 과정에서 컴포넌트 트리 재생성, 가상 DOM 생성, 실제 DOM 비교가 필요하다(근본 해법인 스트리밍 SSR·부분 하이드레이션·Resumability는 Ch16).

**리액트 서버 컴포넌트(RSC)는 번들 크기 문제를 해결한다.** 서버 컴포넌트는 서버에서만 실행되므로 **해당 컴포넌트 코드와 의존성이 클라이언트 번들에 포함되지 않는다.**

### 3.2 서버 컴포넌트의 기본 개념

서버 컴포넌트는 서버에서만 실행되고 렌더링 결과만 직렬화되어 클라이언트에 전달된다. 초기 로드 시 SSR로 HTML도 함께 전송돼 즉시 표시된다.

```tsx
// app/products/page.tsx (서버 컴포넌트, 앱 라우터 기본값)
import { db } from '@/lib/db';
import ProductCard from '@/components/ProductCard'; // 클라이언트 컴포넌트

// 서버에서만 실행됨 — 클라이언트 번들에 포함되지 않음
export default async function ProductsPage() {
  // 서버에서 직접 DB 접근 가능
  const products = await db.products.findMany({
    where: { published: true },
    orderBy: { createdAt: 'desc' },
    take: 20,
  });

  // 서버에서 데이터 가공 — Intl도 서버 실행이라 폴리필·번들 증가 없음
  const formattedProducts = products.map((product) => ({
    id: product.id,
    name: product.name,
    price: new Intl.NumberFormat('ko-KR', { style: 'currency', currency: 'KRW' }).format(product.price),
    image: product.images[0]?.url,
    inStock: product.stock > 0,
  }));

  return (
    <div className="grid">
      {formattedProducts.map((product) => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
}
```

DB 쿼리, 데이터 가공, 가격 포매팅이 모두 서버에서 실행되고 클라이언트 번들에는 `ProductCard`만 포함된다.

**무거운 라이브러리를 서버 컴포넌트에서 사용**

```tsx
// app/blog/[slug]/page.tsx (서버 컴포넌트)
import { marked } from 'marked';          // 서버에서만 사용 → 번들 미포함
import { readFile } from 'fs/promises';   // 파일 시스템 직접 접근
import path from 'node:path';
import sanitizeHtml from 'sanitize-html';

export default async function BlogPost({ params }: { params: { slug: string } }) {
  const content = await readFile(path.join(process.cwd(), 'content', `${params.slug}.md`), 'utf-8');
  const html = sanitizeHtml(marked(content));

  return <article dangerouslySetInnerHTML={{ __html: html }} />;
}
```

별도 API 엔드포인트 없이 파일을 직접 읽고, marked(~50KB)는 번들 크기에 영향을 주지 않는다.

### 3.3 서버 컴포넌트와 클라이언트 컴포넌트 조합

실무 패턴은 **데이터 페칭·무거운 연산은 서버 컴포넌트, 상호작용이 필요한 부분만 `'use client'` 클라이언트 컴포넌트**다.

```tsx
// app/dashboard/page.tsx (서버 컴포넌트)
export default async function Dashboard() {
  const session = await getServerSession();

  // 서버에서 복잡한 집계 쿼리 실행
  const stats = await db.analytics.aggregate({
    where: { userId: session.user.id },
    _sum: { revenue: true, visits: true },
    _avg: { conversionRate: true },
  });

  const monthlyData = await db.analytics.groupBy({
    by: ['month'],
    where: { userId: session.user.id, year: new Date().getFullYear() },
    _sum: { revenue: true },
  });

  return (
    <div>
      <StatCard title="총 매출" value={stats._sum.revenue} />
      {/* 클라이언트 컴포넌트에는 이미 가공된 데이터만 전달 */}
      <InteractiveChart data={monthlyData} />
    </div>
  );
}
```

```tsx
// components/InteractiveChart.tsx (클라이언트 컴포넌트)
'use client';

import { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip } from 'recharts';

export default function InteractiveChart({ data }) {
  const [showDetails, setShowDetails] = useState(false);

  return (
    <div>
      <button onClick={() => setShowDetails(!showDetails)}>
        {showDetails ? '간단히 보기' : '자세히 보기'}
      </button>
      <LineChart width={600} height={300} data={data}>
        <XAxis dataKey="month" />
        <YAxis />
        {showDetails && <Tooltip />}
        <Line type="monotone" dataKey="revenue" stroke="#8884d8" />
      </LineChart>
    </div>
  );
}
```

> **핵심 통찰 — 서버 컴포넌트의 제약**: ① `useState`·`useEffect` 같은 훅을 사용할 수 없다 — 상태·이벤트 핸들러가 필요하면 클라이언트 컴포넌트로. ② 서버 → 클라이언트 컴포넌트로 전달하는 **프롭은 직렬화 가능해야 한다.** 함수나 클래스 인스턴스는 전달할 수 없고 순수 데이터(객체·배열·문자열·숫자)만 가능하다.

### 3.4 다른 프레임워크의 접근 방식

클라이언트 번들 문제는 리액트만의 것이 아니다.

- **넉스트 3(뷰)**: 아일랜드 아키텍처를 도입했다. `.server.vue` 확장자를 쓰면 해당 컴포넌트는 서버에서만 렌더링되어 클라이언트 번들에 포함되지 않는다(아일랜드의 하이드레이션 제거 효과는 Ch16).
- **SvelteKit(스벨트 5)**: 컴포넌트가 아닌 **리소스 레벨**에서 해결한다. `+page.server.js`의 `load` 함수는 서버에서만 실행되고, 결과가 HTML에 자동 인라인되어 하이드레이션 시 추가 네트워크 요청 없이 데이터를 쓴다. 무거운 라이브러리는 서버 파일에서만 사용한다.

```ts
// +page.server.ts — 서버에서만 실행
export async function load() {
  const products = await db.query('SELECT * FROM products');
  const processed = products.map((p) => ({
    ...p,
    formattedPrice: formatPrice(p.price), // 무거운 라이브러리 사용 가능
  }));
  return { products: processed }; // HTML에 인라인되어 클라이언트로 전달
}
```

> **핵심 통찰**: 각 프레임워크가 해결하려는 문제는 동일하다 — **"서버에서 할 수 있는 일은 서버에서 하고, 클라이언트 번들을 최소화하자."** 리액트는 컴포넌트를 서버/클라이언트로 구분하고, 뷰/넉스트는 서버 전용 컴포넌트를 지원하며, 스벨트는 데이터 페칭 경계로 관리한다. 프레임워크와 무관하게 이 원칙을 이해하면 적용할 수 있다.

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|---|---|---|
| 전체 데이터를 내려받아 클라이언트 퍼지 검색 | 수 MB 전송 + 라이브러리 20KB + 타이핑마다 무거운 연산 | 서버 전문 검색(PostgreSQL·엘라스틱서치)으로 쿼리만 전송 |
| SheetJS로 클라이언트에서 대용량 엑셀 파싱 | 번들 +180KB, 메인 스레드 수 초 블로킹 | 서버 스트리밍 파싱(민감 데이터는 웹 워커 대안) |
| 마크다운 파싱 라이브러리 3종을 번들에 포함 | 170KB 추가 + 타이핑마다 파싱으로 반응 저하 | 서버 변환 API + debounce |
| 할인·가격 계산을 클라이언트에서 수행 | 개발자 도구로 조작 가능 + 규칙 변경 시 재배포 필요 | 서버에서 계산하고 결과만 전달 |
| 수만 건 데이터를 받아 클라이언트에서 집계 | 네트워크·메모리 낭비, 집계 중 UI 멈춤 | DB 집계 쿼리로 요약 데이터만 전송 |
| 모든 로직을 무조건 서버로 이동 | 네트워크 왕복 증가로 인터랙션이 느려짐 | UI 상태·즉각 피드백은 클라이언트에 유지 |
| 범용 API가 화면에 불필요한 데이터까지 반환 | 오버 페치로 페이로드 낭비 + 클라이언트 필터링 로직 필요 | BFF 또는 GraphQL로 필요한 데이터만 |
| 서버 컴포넌트에서 `useState`·`useEffect` 사용 | 서버 컴포넌트는 훅 사용 불가 | 상호작용 부분만 `'use client'`로 분리 |
| 서버 → 클라이언트 컴포넌트로 함수 프롭 전달 | 직렬화 불가능해 에러 발생 | 순수 데이터만 전달 |
| 무거운 라이브러리를 클라이언트 컴포넌트에서 import | 서버 컴포넌트의 번들 절감 효과가 사라짐 | 서버 컴포넌트에서만 import |
| 폼 검증을 클라이언트에만 구현 | 조작 가능 — 보안 구멍 | 클라이언트(UX) + 서버(보안) 이중 검증, Zod/Yup으로 스키마 공유 |

## 측정과 검증

- **번들 분석**: `webpack-bundle-analyzer` / `@next/bundle-analyzer`로 50KB 이상 라이브러리 목록을 뽑고, 서버로 옮길 수 있는 것을 식별한다.
- **Coverage**: 클라이언트에서만 쓰이는 무거운 라이브러리(marked·lodash·xlsx 등)의 실사용 비율을 확인한다.
- **네트워크 페이로드**: API 응답 크기를 측정한다. 화면에 안 쓰이는 필드가 내려오고 있다면 BFF/필드 선택 최적화 후보다.
- **서버 이동 전후 비교**: 초기 번들 크기(압축 전/후), LCP·TTI 변화를 측정한다.
- **서버 비용 모니터링**: 로직 이동 후 서버 CPU·메모리 사용량 증가를 추적하고 캐싱·수평 확장·CDN으로 보완한다.

## 체크리스트

**번들 크기 진단**

- [ ] 프로덕션 빌드의 자바스크립트 번들 크기 측정(압축 전/후)
- [ ] `webpack-bundle-analyzer` 또는 `@next/bundle-analyzer`로 번들 분석
- [ ] 50KB 이상의 라이브러리 목록 확인
- [ ] 클라이언트에서만 사용되는 무거운 라이브러리 식별(marked·lodash·xlsx 등)
- [ ] Coverage 탭으로 사용되지 않는 코드 비율 확인

**서버 이동 후보 식별**

- [ ] 데이터 가공 로직이 클라이언트에 있는지 확인(필터링·정렬·집계)
- [ ] 비즈니스 로직 노출 점검(할인·가격 계산)
- [ ] 복잡한 데이터 변환 로직 식별(여러 소스 조합, 중첩 구조 평탄화)
- [ ] 마크다운·PDF·엑셀 같은 무거운 파싱 라이브러리 사용 여부 확인
- [ ] 대용량 데이터(1,000개 이상)를 클라이언트로 전송하는 API 확인

**API 최적화**

- [ ] 모든 데이터를 반환하는 API 엔드포인트 제거 또는 개선
- [ ] 필요한 필드만 선택해 응답 크기 최소화
- [ ] 서버에서 필터링·정렬·페이지네이션 구현
- [ ] DB 쿼리 병렬 실행(`Promise.all`)
- [ ] 집계 쿼리는 DB에서 직접 수행(MongoDB aggregate, SQL GROUP BY)

**서버 컴포넌트 도입(리액트/Next.js)**

- [ ] Next.js 13+ 앱 라우터 사용 여부 확인
- [ ] 페이지 컴포넌트를 서버 컴포넌트로 기본 설정
- [ ] 데이터 페칭 로직을 서버 컴포넌트로 이동
- [ ] 무거운 라이브러리는 서버 컴포넌트에서만 import
- [ ] 상호작용 필요 부분만 `'use client'`로 분리
- [ ] 서버 → 클라이언트 프롭 직렬화 가능 여부 확인

**다른 프레임워크**

- [ ] 넉스트 3: 인터랙션 불필요 컴포넌트를 `.server.vue`로 전환, `<NuxtIsland>`로 서버 전용 영역 래핑
- [ ] SvelteKit: 서버 로직을 `+page.server.js`의 `load` 함수로 분리, 무거운 라이브러리는 서버 파일에서만 사용

**역할 분담 검증**

- [ ] 보안 중요 로직(결제·권한)은 서버에서만 처리하는지 확인
- [ ] UI 상태(모달·탭)는 클라이언트에서 관리하는지 확인
- [ ] 검색/필터는 데이터 크기에 따라 분담했는지 확인(100개 미만: 클라이언트 / 1,000개 이상: 서버)
- [ ] 폼 검증을 클라이언트(UX)와 서버(보안) 양쪽에서 구현했는지 확인
- [ ] Zod·Yup 같은 스키마 라이브러리로 검증 로직 공유 여부 확인

## 요약

- SPA 시대의 "로직의 이동"으로 번들이 폭발했다. 모바일 중간값 자바스크립트는 연평균 13% 증가 중이고, 지메일은 첫 방문에 30MB 리소스를 받는다. **번들 자체가 크면 어떤 최적화로도 첫 방문 한계를 못 넘는다.**
- 함정 사례 3종: 클라이언트 퍼지 검색(전체 데이터 다운로드), 클라이언트 엑셀 파싱(메인 스레드 블로킹), 마크다운 실시간 프리뷰(라이브러리 170KB). 모두 "당연히 클라이언트 작업"처럼 보이지만 서버가 낫다.
- 분담 기준: **클라이언트 = UI 상태·즉각 피드백·브라우저 API·오프라인 / 서버 = 필터링·집계·비즈니스 규칙·데이터 가공·보안.** 판단이 어려우면 4문 — 콘텐츠 표시에 필수인가, 50KB 이상 라이브러리가 필요한가, 즉각 응답이 필요한가, 보안이 중요한가.
- 서버로 옮기면 좋은 로직 4유형: 복잡한 데이터 변환, 대용량 필터링·집계(수 MB → 수 KB), 비즈니스 로직(보안), 무거운 라이브러리 작업.
- **BFF**는 화면 맞춤 데이터로 오버 페치를, **GraphQL**은 클라이언트가 명시한 구조로 오버·언더 페치를 해결한다. 둘 다 "복잡한 가공·조합"을 서버로 옮기는 도구이며, 프레임워크 내장 기능부터 점진 도입한다.
- 전통적 SSR의 한계: HTML을 만들어도 하이드레이션용 자바스크립트가 전부 번들에 포함되고, 페이지 레벨 데이터 페칭만 가능하다.
- **리액트 서버 컴포넌트는 컴포넌트 코드와 의존성을 클라이언트 번들에서 아예 제거한다.** DB 직접 접근, 무거운 라이브러리 사용이 자유롭고, 상호작용 부분만 `'use client'`로 분리한다. 제약은 훅 사용 불가와 프롭 직렬화다.
- 넉스트는 `.server.vue`, SvelteKit은 `+page.server.js` load 함수로 같은 원칙을 구현한다.
- 서버 이동은 서버 비용·복잡도 증가라는 트레이드오프가 있다. 캐싱·수평 확장·CDN으로 보완하고, **번들 분석 → 가장 큰 라이브러리부터 하나씩 측정 가능한 개선**으로 점진 적용한다.

## 다른 챕터와의 관계

- **Ch9(불필요한 리소스 제거)**: 번들 분석으로 찾은 무거운 라이브러리의 다음 단계 질문이 "이걸 서버로 옮길 수 없나?"다. 네이티브 API 대체(Ch9) → 서버 이동(이 장) 순으로 검토한다.
- **Ch10(코드 스플리팅)**: 분할해도 결국 클라이언트가 다운로드한다. 서버 이동은 다운로드 자체를 없애는 더 근본적인 해법이다.
- **Ch16(하이드레이션)**: 이 장이 남겨둔 하이드레이션 오버헤드 문제(스트리밍 SSR·부분 하이드레이션·Resumability·아일랜드)를 정면으로 다룬다.
- **Ch17(데이터 캐싱)**: 서버 상태와 클라이언트 상태의 구분이 이 장의 역할 분담 원칙과 이어진다.
- **Ch1(네트워크 최적화)**: CDN 엣지 컴퓨팅으로 언급된 "사용자 가까이에서 로직 실행"이 이 장의 서버 이동 전략과 결합된다.
- **Ch23(서드파티 코드)**: 자사 코드가 아닌 서드파티의 부담을 서버(프락시)나 웹 워커로 옮기는 전략으로 확장된다.
