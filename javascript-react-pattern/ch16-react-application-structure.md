# Chapter 16: React Application Structure (리액트 애플리케이션 구조)

## 핵심 질문

> 리액트 애플리케이션이 성장함에 따라 코드베이스를 어떻게 구조화해야 유지보수성과 확장성을 확보할 수 있는가?

---

## 1. 프로젝트 구조의 중요성

작은 토이 프로젝트나 새로운 라이브러리를 시험할 때는 체계적인 구조 없이 개발을 시작하는 경우가 많다. CSS, 헬퍼 컴포넌트, 이미지, 페이지 컴포넌트가 모두 한 폴더에 뒤섞여 있어도 당장은 문제가 없다. 하지만 프로젝트가 성장하면 이 방식은 곧 한계에 부딪힌다. 특정 파일을 찾는 데 시간이 걸리고, 관련 코드가 흩어져 있어 변경의 영향 범위를 파악하기 어려워진다.

### 리액트는 구조에 의견이 없다

리액트는 프로젝트 구조에 대한 공식적인 가이드라인을 제공하지 않는 **비의견적**(*Unopinionated*) 라이브러리다. 이는 개발자에게 자유를 주는 동시에, 팀마다 서로 다른 구조를 채택하게 되는 원인이 된다. 리액트 공식 문서에서도 "너무 많은 시간을 고민하지 말라"고 조언하지만, 실무에서는 **초기에 정한 구조가 프로젝트 전체 수명에 영향을 미친다**.

> **Osmani의 조언**: 잘 정의된 패턴을 따르면 다른 팀원들에게 프로젝트 구조를 설명하기 쉽고, 프로젝트가 불필요하게 복잡해지거나 체계가 무너지는 사태를 방지할 수 있다. 구조 설계는 한 번 결정하면 변경 비용이 크므로, 프로젝트 초기에 신중하게 선택해야 한다.

---

## 2. 파일 그룹화 전략

리액트 애플리케이션에서 파일을 그룹화하는 방법은 크게 세 가지로 나뉜다.

### 2.1 기능별 그룹화 (Feature-based Grouping)

기능별 그룹화(*Feature-based Grouping*)는 비즈니스 모델이나 애플리케이션의 흐름을 반영하여 폴더를 구성하는 방식이다. 예를 들어 전자상거래 애플리케이션이라면 `product/`, `checkout/`, `cart/` 등의 도메인 폴더를 만들고, 각 폴더 안에 해당 기능에 필요한 컴포넌트, 스타일, 테스트, 헬퍼 등을 모두 함께 넣는다.

```
common/
  Avatar.tsx
  Avatar.css
  ErrorUtils.ts
  ErrorUtils.test.ts
product/
  index.tsx
  product.css
  price.tsx
  product.test.tsx
checkout/
  index.tsx
  checkout.css
  checkout.test.tsx
```

**장점**: 특정 모듈에 변경이 있을 때 관련 파일이 모두 같은 폴더에 있어 변경 범위가 명확하다.

**단점**: 모듈 간 공통으로 사용되는 컴포넌트나 로직을 주기적으로 파악해야 중복을 피할 수 있다.

### 2.2 파일 유형별 그룹화 (Type-based Grouping)

파일 유형별 그룹화(*Type-based Grouping*)는 CSS, 컴포넌트, 테스트, 라이브러리 등 파일 유형에 따라 서로 다른 폴더를 생성하는 방식이다. 논리적으로 관련된 파일들이 유형에 따라 분산된다.

```
css/
  global.css
  checkout.css
  product.css
lib/
  date.ts
  currency.ts
  gtm.ts
pages/
  product.tsx
  productlist.tsx
  checkout.tsx
```

**장점**:
- 여러 프로젝트에서 동일하게 재사용할 수 있는 표준적 구조를 갖는다
- 애플리케이션 로직에 익숙하지 않은 신규 팀원도 파일을 쉽게 찾을 수 있다
- 공통 컴포넌트나 스타일을 변경하면 애플리케이션 전체에 적용된다

**단점**:
- 특정 모듈을 수정하려면 여러 폴더를 오가며 파일을 찾아야 한다
- 기능이 많아질수록 각 폴더의 파일 수가 급증하여 특정 파일을 찾기 어려워진다

### 2.3 혼합 그룹화 (Hybrid Grouping)

혼합 그룹화(*Hybrid Grouping*)는 기능별 그룹화와 파일 유형별 그룹화의 장점을 결합한 방식이다. 애플리케이션 전체에서 공통으로 사용되는 컴포넌트는 `components/` 폴더에, 특정 기능에 종속된 코드는 `domain/` 폴더에 배치한다.

```
css/
  global.css
components/
  User/
    Profile.tsx
    Profile.test.tsx
    Avatar.tsx
  date.ts
  currency.ts
  errorUtils.ts
domain/
  product/
    product.tsx
    product.css
    product.test.tsx
  checkout/
    checkout.tsx
    checkout.css
    checkout.test.tsx
```

이 방식은 자주 변경되는 관련 파일들을 한곳에 모으면서도, 재사용 가능한 공통 컴포넌트와 스타일을 별도로 관리할 수 있다.

### 그룹화 전략 비교

| 전략 | 적합한 규모 | 파일 탐색 | 변경 범위 격리 | 재사용성 관리 |
|------|------------|----------|--------------|-------------|
| **기능별** | 중~대규모 | 기능 내 우수 | 우수 | 별도 노력 필요 |
| **유형별** | 소~중규모 | 유형 내 우수 | 미흡 | 자연스러움 |
| **혼합** | 중~대규모 | 양쪽 모두 양호 | 양호 | 양호 |

> **핵심 통찰**: 중소 규모(폴더당 50~100개 파일)에서는 어떤 전략이든 큰 차이가 없다. 그러나 대규모 프로젝트에서는 혼합 그룹화가 사실상 유일한 현실적 선택이다. 핵심은 팀 전체가 합의된 하나의 규칙을 일관되게 따르는 것이다.

---

## 3. 확장 가능한 프로젝트 구조

프로젝트 규모에 따라 폴더 구조는 진화해야 한다. 여기서는 소규모부터 대규모까지 단계별로 권장하는 구조를 살펴본다.

### 3.1 소규모 프로젝트 (MVP / 사이드 프로젝트)

파일 수가 적고 팀원이 1~2명인 경우, 평면적(*Flat*)이고 단순한 구조가 적합하다.

```
src/
  components/
    Button.tsx
    Input.tsx
    Modal.tsx
  hooks/
    useAuth.ts
    useLocalStorage.ts
  utils/
    format.ts
    api.ts
  pages/
    Home.tsx
    Login.tsx
    Dashboard.tsx
  App.tsx
  main.tsx
```

이 단계에서는 깊은 중첩 없이 `components/`, `hooks/`, `utils/`, `pages/` 정도의 유형별 그룹화로 충분하다.

### 3.2 중규모 프로젝트 (Feature Sliced Design 참고)

팀원이 3명 이상이고 기능이 10개를 넘어가면, 기능 단위로 코드를 분리하는 것이 효과적이다. Feature Sliced Design(*FSD*)의 계층 개념을 참고하면 좋다.

```
src/
  app/
    providers/
      AuthProvider.tsx
      QueryProvider.tsx
    layout/
      RootLayout.tsx
      Sidebar.tsx
    routes.tsx
    App.tsx
  features/
    auth/
      components/
        LoginForm.tsx
        SignupForm.tsx
      hooks/
        useAuth.ts
      api/
        authApi.ts
      types.ts
      index.ts
    product/
      components/
        ProductCard.tsx
        ProductList.tsx
      hooks/
        useProducts.ts
      api/
        productApi.ts
      types.ts
      index.ts
  shared/
    ui/
      Button.tsx
      Input.tsx
      Modal.tsx
    lib/
      format.ts
      cn.ts
    hooks/
      useDebounce.ts
      useMediaQuery.ts
    types/
      common.ts
```

핵심 원칙은 **상위 계층은 하위 계층을 참조할 수 있지만, 하위 계층은 상위 계층을 참조할 수 없다**는 것이다. 예를 들어 `features/`는 `shared/`를 import할 수 있지만, `shared/`는 `features/`를 import할 수 없다. 각 feature 폴더의 `index.ts`는 공개 API 역할을 하며, 외부에서는 이 진입점만 참조한다.

### 3.3 대규모 프로젝트 (모노레포)

여러 팀이 하나의 프로덕트를 개발하는 대규모 프로젝트에서는 모노레포(*Monorepo*) 구조가 효과적이다. Turborepo, Nx 같은 도구를 사용하여 패키지를 분리한다.

```
apps/
  web/                    # 메인 웹 애플리케이션
    src/
      app/
      features/
      ...
    package.json
  admin/                  # 관리자 대시보드
    src/
    package.json
  mobile/                 # React Native 앱
    src/
    package.json
packages/
  ui/                     # 공유 UI 컴포넌트 라이브러리
    src/
      Button.tsx
      Modal.tsx
    package.json
  utils/                  # 공유 유틸리티
    src/
      format.ts
      validation.ts
    package.json
  config/                 # 공유 설정 (ESLint, TypeScript 등)
    eslint/
    tsconfig/
    package.json
  types/                  # 공유 타입 정의
    src/
      api.ts
      domain.ts
    package.json
turbo.json
package.json
```

### 3.4 코로케이션 원칙

코로케이션(*Colocation*)은 **관련 파일을 가능한 한 가까이 배치**하는 원칙이다. 컴포넌트, 해당 컴포넌트의 스타일, 테스트, 타입 정의를 같은 디렉토리에 놓으면 파일 탐색 시간이 줄어들고, 코드의 응집도(*Cohesion*)가 높아진다.

```
features/
  product/
    components/
      ProductCard/
        ProductCard.tsx        # 컴포넌트
        ProductCard.test.tsx   # 테스트
        ProductCard.stories.tsx # 스토리북
        ProductCard.module.css # 스타일
        index.ts               # 배럴 export
```

> **핵심 통찰**: 코로케이션의 핵심은 "함께 변경되는 것은 함께 둔다"는 원칙이다. 테스트를 별도의 `__tests__/` 디렉토리에 두면 컴포넌트를 수정할 때마다 다른 디렉토리로 이동해야 한다. 반면 `.test.tsx`를 컴포넌트 옆에 두면, 컴포넌트와 테스트를 하나의 단위로 다룰 수 있다.

---

## 4. Next.js App Router 구조

Next.js는 파일 시스템 기반 라우팅을 제공하므로, 폴더 구조가 곧 URL 구조가 된다. App Router(*Next.js 13+에서 도입된 라우팅 방식*)는 `app/` 디렉토리를 사용한다.

### 4.1 app/ 디렉토리 기본 구조

```
app/
  layout.tsx              # 루트 레이아웃
  page.tsx                # / (홈)
  loading.tsx             # 로딩 UI
  error.tsx               # 에러 UI
  not-found.tsx           # 404 UI
  products/
    page.tsx              # /products
    [id]/
      page.tsx            # /products/:id
      loading.tsx
  checkout/
    page.tsx              # /checkout
  api/
    products/
      route.ts            # API 라우트
```

`page.tsx` 파일이 있는 폴더만 라우트로 인식되므로, **라우트 폴더 안에 컴포넌트나 유틸리티 파일을 함께 놓아도 URL에 노출되지 않는다**. 이를 활용하면 코로케이션과 라우팅을 자연스럽게 결합할 수 있다.

```
app/
  products/
    page.tsx              # 라우트 (공개)
    ProductList.tsx        # 컴포넌트 (비공개, URL 미생성)
    useProducts.ts         # 훅 (비공개)
```

### 4.2 라우트 그룹 (Route Groups)

라우트 그룹(*Route Group*)은 괄호 `()`로 폴더 이름을 감싸서 URL 경로에 영향을 주지 않으면서 라우트를 논리적으로 그룹화하는 기능이다.

```
app/
  (marketing)/
    about/
      page.tsx            # /about
    blog/
      page.tsx            # /blog
    layout.tsx            # 마케팅 페이지 전용 레이아웃
  (shop)/
    products/
      page.tsx            # /products
    cart/
      page.tsx            # /cart
    layout.tsx            # 쇼핑 페이지 전용 레이아웃
  (auth)/
    login/
      page.tsx            # /login
    signup/
      page.tsx            # /signup
    layout.tsx            # 인증 페이지 전용 레이아웃
```

`(marketing)`, `(shop)`, `(auth)`는 URL에 포함되지 않지만, 각 그룹마다 별도의 `layout.tsx`를 적용할 수 있어 레이아웃 분리에 유용하다.

### 4.3 병렬 라우트 (Parallel Routes)

병렬 라우트(*Parallel Routes*)는 `@` 접두사를 사용하여 동일한 레이아웃 내에서 여러 페이지를 동시에 렌더링하는 기능이다. 대시보드처럼 여러 독립적인 영역을 가진 페이지에 적합하다.

```
app/
  dashboard/
    layout.tsx
    page.tsx
    @analytics/
      page.tsx            # 분석 패널
      loading.tsx
    @activity/
      page.tsx            # 활동 피드
      loading.tsx
    @notifications/
      page.tsx            # 알림 패널
      loading.tsx
```

```tsx
// app/dashboard/layout.tsx
export default function DashboardLayout({
  children,
  analytics,
  activity,
  notifications,
}: {
  children: React.ReactNode;
  analytics: React.ReactNode;
  activity: React.ReactNode;
  notifications: React.ReactNode;
}) {
  return (
    <div className="grid grid-cols-3 gap-4">
      <main className="col-span-2">{children}</main>
      <aside className="space-y-4">
        {analytics}
        {activity}
        {notifications}
      </aside>
    </div>
  );
}
```

각 슬롯은 독립적으로 로딩 상태와 에러 상태를 가질 수 있어, 하나의 슬롯이 느려도 다른 슬롯은 즉시 렌더링된다.

### 4.4 인터셉팅 라우트 (Intercepting Routes)

인터셉팅 라우트(*Intercepting Routes*)는 현재 레이아웃 내에서 다른 라우트를 가로채 표시하는 기능이다. 모달 패턴에서 특히 유용하다. `(.)`, `(..)`, `(..)(..)`, `(...)` 접두사를 사용한다.

```
app/
  products/
    page.tsx              # /products (상품 목록)
    [id]/
      page.tsx            # /products/:id (상품 상세 - 직접 접근 시)
    (.)  [id]/
      page.tsx            # /products/:id (인터셉트 - 목록에서 클릭 시 모달)
```

| 접두사 | 의미 | 설명 |
|--------|------|------|
| `(.)` | 같은 수준 | 동일 디렉토리의 라우트를 인터셉트 |
| `(..)` | 한 수준 위 | 부모 디렉토리의 라우트를 인터셉트 |
| `(..)(..)` | 두 수준 위 | 조부모 디렉토리의 라우트를 인터셉트 |
| `(...)` | 루트 | 앱 루트 기준으로 인터셉트 |

인스타그램 스타일의 사진 피드가 대표적 사례다. 피드에서 사진을 클릭하면 모달로 보여주고, URL은 `/photo/123`으로 변경된다. 이 URL을 직접 방문하면 전체 페이지로 렌더링된다.

### 4.5 Server/Client 컴포넌트 배치 전략

Next.js App Router에서는 기본적으로 모든 컴포넌트가 서버 컴포넌트(*Server Component*)다. 클라이언트 상호작용(이벤트 핸들러, 훅 사용 등)이 필요한 컴포넌트만 `'use client'` 지시어를 추가한다.

```
app/
  products/
    page.tsx              # Server Component (데이터 페칭)
    ProductList.tsx        # Server Component (목록 렌더링)
    ProductFilter.tsx      # 'use client' (필터 상호작용)
    AddToCartButton.tsx    # 'use client' (장바구니 추가 버튼)
```

**배치 원칙**:
- `'use client'` 경계를 가능한 한 **트리의 하단**에 배치한다
- 서버 컴포넌트에서 데이터를 페칭하고, 클라이언트 컴포넌트에 props로 전달한다
- 클라이언트 컴포넌트 안에 서버 컴포넌트를 **직접** import할 수 없다. 대신 서버 컴포넌트를 `children` prop으로 전달하는 컴포지션 패턴을 사용한다

```tsx
// 잘못된 방식: 클라이언트 컴포넌트에서 서버 컴포넌트 직접 import
'use client';
import ServerComponent from './ServerComponent'; // 서버 컴포넌트가 클라이언트로 변환됨

// 올바른 방식: 컴포지션 패턴
'use client';
export function ClientWrapper({ children }: { children: React.ReactNode }) {
  const [isOpen, setIsOpen] = useState(false);
  return (
    <div>
      <button onClick={() => setIsOpen(!isOpen)}>토글</button>
      {isOpen && children} {/* children은 서버 컴포넌트로 유지 */}
    </div>
  );
}
```

---

## 5. 상태 관리 아키텍처

### 5.1 상태 에스컬레이션 전략

상태 관리는 가장 단순한 방법부터 시작해서, 필요에 따라 점진적으로 복잡한 도구로 이동하는 에스컬레이션(*Escalation*) 전략을 따르는 것이 좋다.

```
로컬 상태 (useState)
    ↓ 형제 컴포넌트 간 공유 필요
상태 끌어올리기 (Lifting State Up)
    ↓ 깊은 트리에서 프롭 드릴링 발생
Context API (useContext)
    ↓ 잦은 업데이트로 리렌더링 성능 문제
외부 상태 관리 라이브러리 (Zustand, Jotai, Redux 등)
```

모든 상태를 전역으로 관리하려는 유혹을 피해야 한다. **대부분의 상태는 로컬 상태로 충분**하며, 전역 상태는 정말 여러 곳에서 공유되어야 하는 데이터(인증, 테마, 언어 설정 등)에만 사용한다.

### 5.2 Zustand: 간단한 전역 상태

Zustand는 보일러플레이트가 거의 없는 경량 상태 관리 라이브러리다. Provider 없이 어디서든 스토어에 접근할 수 있다.

```tsx
import { create } from 'zustand';

interface CartStore {
  items: CartItem[];
  addItem: (item: CartItem) => void;
  removeItem: (id: string) => void;
  clearCart: () => void;
  totalPrice: () => number;
}

const useCartStore = create<CartStore>((set, get) => ({
  items: [],
  addItem: (item) =>
    set((state) => ({ items: [...state.items, item] })),
  removeItem: (id) =>
    set((state) => ({ items: state.items.filter((i) => i.id !== id) })),
  clearCart: () => set({ items: [] }),
  totalPrice: () =>
    get().items.reduce((sum, item) => sum + item.price * item.quantity, 0),
}));

// 컴포넌트에서 사용
function CartBadge() {
  const itemCount = useCartStore((state) => state.items.length);
  return <span className="badge">{itemCount}</span>;
}
```

**적합한 경우**: UI 상태(사이드바 열림/닫힘), 장바구니, 사용자 설정 등 중간 복잡도의 전역 상태.

### 5.3 Jotai: 원자적(Atomic) 상태

Jotai는 원자(*Atom*) 단위로 상태를 관리하는 바텀업 방식의 라이브러리다. React의 `useState`와 유사한 인터페이스를 제공하면서도 전역 공유가 가능하다.

```tsx
import { atom, useAtom, useAtomValue } from 'jotai';

// 원자(atom) 정의
const themeAtom = atom<'light' | 'dark'>('light');
const fontSizeAtom = atom<number>(16);

// 파생 원자 (derived atom)
const themeConfigAtom = atom((get) => ({
  theme: get(themeAtom),
  fontSize: get(fontSizeAtom),
  isDark: get(themeAtom) === 'dark',
}));

// 컴포넌트에서 사용
function ThemeToggle() {
  const [theme, setTheme] = useAtom(themeAtom);
  return (
    <button onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>
      현재: {theme}
    </button>
  );
}

function FontSize() {
  const config = useAtomValue(themeConfigAtom);
  return <p style={{ fontSize: config.fontSize }}>샘플 텍스트</p>;
}
```

**적합한 경우**: 독립적인 소규모 상태 조각이 많고, 컴포넌트 간 자유롭게 공유해야 할 때. 파생 상태가 많은 경우에 특히 효과적이다.

### 5.4 Redux Toolkit: 복잡한 비즈니스 로직

Redux Toolkit(*RTK*)은 Redux의 공식 도구 모음으로, 보일러플레이트를 대폭 줄이면서도 Redux의 예측 가능한 상태 관리 철학을 유지한다. 리덕스 공식 문서에서는 기능별 슬라이스(*Slice*) 파일에 리듀서와 액션을 함께 배치하는 덕스(*Ducks*) 패턴을 권장한다.

```tsx
// features/todos/todosSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface Todo {
  id: string;
  text: string;
  completed: boolean;
}

interface TodosState {
  items: Todo[];
  filter: 'all' | 'active' | 'completed';
}

const todosSlice = createSlice({
  name: 'todos',
  initialState: { items: [], filter: 'all' } as TodosState,
  reducers: {
    addTodo: (state, action: PayloadAction<string>) => {
      state.items.push({
        id: crypto.randomUUID(),
        text: action.payload,
        completed: false,
      });
    },
    toggleTodo: (state, action: PayloadAction<string>) => {
      const todo = state.items.find((t) => t.id === action.payload);
      if (todo) todo.completed = !todo.completed;
    },
    setFilter: (state, action: PayloadAction<TodosState['filter']>) => {
      state.filter = action.payload;
    },
  },
});

export const { addTodo, toggleTodo, setFilter } = todosSlice.actions;
export default todosSlice.reducer;
```

Redux의 프로젝트 구조는 기능 폴더 안에 슬라이스 파일을 배치하는 형태다:

```
src/
  app/
    store.ts
    rootReducer.ts
    App.tsx
  features/
    todos/
      todosSlice.ts
      Todos.tsx
    auth/
      authSlice.ts
      Auth.tsx
  common/
    hooks/
    components/
```

**적합한 경우**: 복잡한 비즈니스 로직, 상태 변화의 추적이 중요한 경우(DevTools), 대규모 팀에서 예측 가능한 패턴이 필요할 때.

### 5.5 React Query / TanStack Query: 서버 상태

서버 상태(*Server State*)는 클라이언트 상태와 근본적으로 다르다. 서버 상태는 원격 서버에 존재하며, 캐싱, 백그라운드 리페칭, 페이지네이션, 낙관적 업데이트 등의 고유한 문제를 가진다.

```tsx
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

// 데이터 페칭
function ProductList() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['products'],
    queryFn: () => fetch('/api/products').then((res) => res.json()),
    staleTime: 5 * 60 * 1000, // 5분간 캐시 유효
  });

  if (isLoading) return <Skeleton />;
  if (error) return <ErrorBanner error={error} />;

  return (
    <ul>
      {data.map((product: Product) => (
        <ProductCard key={product.id} product={product} />
      ))}
    </ul>
  );
}

// 뮤테이션 (데이터 변경)
function AddProductForm() {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: (newProduct: NewProduct) =>
      fetch('/api/products', {
        method: 'POST',
        body: JSON.stringify(newProduct),
      }),
    onSuccess: () => {
      // 캐시 무효화 → 자동 리페칭
      queryClient.invalidateQueries({ queryKey: ['products'] });
    },
  });

  return <form onSubmit={(e) => { /* ... */ mutation.mutate(formData); }}>...</form>;
}
```

### 상태 관리 도구 선택 가이드

```
상태의 성격은?
  ├── 서버 데이터 (API 응답) → TanStack Query / SWR
  └── 클라이언트 데이터
       ├── 단일 컴포넌트에서만 사용 → useState / useReducer
       ├── 가까운 하위 트리에서 공유 → Context API
       └── 전역적으로 공유
            ├── 단순한 상태 → Zustand
            ├── 원자적/파생 상태가 많음 → Jotai
            └── 복잡한 비즈니스 로직 + DevTools 필요 → Redux Toolkit
```

> **Osmani의 조언**: 상태 관리 라이브러리를 선택할 때 가장 흔한 실수는 "모든 것을 하나의 도구로 해결하려는 것"이다. 서버 상태와 클라이언트 상태는 근본적으로 다른 문제이므로, TanStack Query + Zustand처럼 역할에 따라 도구를 조합하는 것이 현실적이다.

---

## 6. 데이터 페칭 패턴

### 6.1 Server Components에서의 데이터 페칭

React Server Components에서는 컴포넌트 자체가 서버에서 실행되므로, `async/await`를 직접 사용하여 데이터를 페칭할 수 있다. 클라이언트에 자바스크립트 번들을 보내지 않아 성능상 이점이 크다.

```tsx
// app/products/page.tsx (Server Component)
async function ProductsPage() {
  const products = await fetch('https://api.example.com/products', {
    next: { revalidate: 3600 }, // 1시간마다 재검증 (ISR)
  }).then((res) => res.json());

  return (
    <div>
      <h1>상품 목록</h1>
      <ProductList products={products} />
      <ProductFilter /> {/* 'use client' 컴포넌트 */}
    </div>
  );
}
```

### 6.2 Server Actions (폼 뮤테이션)

Server Actions(*서버 액션*)는 서버에서 실행되는 비동기 함수로, 폼 제출이나 데이터 변경에 사용된다. `'use server'` 지시어로 선언한다.

```tsx
// app/products/actions.ts
'use server';

import { revalidatePath } from 'next/cache';

export async function createProduct(formData: FormData) {
  const name = formData.get('name') as string;
  const price = Number(formData.get('price'));

  await db.product.create({
    data: { name, price },
  });

  revalidatePath('/products');
}

export async function deleteProduct(id: string) {
  await db.product.delete({ where: { id } });
  revalidatePath('/products');
}
```

```tsx
// app/products/CreateProductForm.tsx
'use client';

import { useActionState } from 'react';
import { createProduct } from './actions';

export function CreateProductForm() {
  const [state, formAction, isPending] = useActionState(createProduct, null);

  return (
    <form action={formAction}>
      <input name="name" placeholder="상품명" required />
      <input name="price" type="number" placeholder="가격" required />
      <button type="submit" disabled={isPending}>
        {isPending ? '추가 중...' : '상품 추가'}
      </button>
    </form>
  );
}
```

### 6.3 클라이언트 데이터 페칭 (React Query / SWR)

서버 컴포넌트를 사용할 수 없는 경우(실시간 데이터, 사용자 상호작용 기반 페칭 등)에는 클라이언트에서 TanStack Query나 SWR을 사용한다.

```tsx
'use client';

import { useQuery } from '@tanstack/react-query';

function SearchResults({ query }: { query: string }) {
  const { data, isLoading } = useQuery({
    queryKey: ['search', query],
    queryFn: () =>
      fetch(`/api/search?q=${encodeURIComponent(query)}`).then((r) => r.json()),
    enabled: query.length > 2, // 3글자 이상일 때만 페칭
  });

  if (isLoading) return <Spinner />;
  return <ResultList results={data} />;
}
```

### 6.4 캐싱 전략 (Next.js 캐싱 계층)

Next.js는 여러 층의 캐싱을 제공한다.

| 캐싱 계층 | 위치 | 설명 | 제어 방법 |
|-----------|------|------|----------|
| **요청 메모이제이션** | 서버 (요청 중) | 동일 요청 내 같은 fetch 중복 제거 | React `cache()` |
| **데이터 캐시** | 서버 (요청 간) | fetch 결과를 영구적으로 캐싱 | `fetch()` 옵션, `revalidatePath/Tag` |
| **전체 라우트 캐시** | 서버 | 빌드 타임에 정적으로 렌더링된 라우트 | 동적 함수 사용 시 자동 비활성화 |
| **라우터 캐시** | 클라이언트 | 방문한 라우트의 RSC 페이로드 캐싱 | `router.refresh()` |

```tsx
// 캐싱 전략 예시
// 1. 정적 데이터 — 빌드 타임에 한 번만 페칭
const staticData = await fetch('https://api.example.com/config');

// 2. ISR — 주기적 재검증
const isrData = await fetch('https://api.example.com/products', {
  next: { revalidate: 3600 }, // 1시간
});

// 3. 동적 데이터 — 매 요청마다 페칭
const dynamicData = await fetch('https://api.example.com/user', {
  cache: 'no-store',
});

// 4. 태그 기반 재검증
const taggedData = await fetch('https://api.example.com/posts', {
  next: { tags: ['posts'] },
});
// 서버 액션에서: revalidateTag('posts')
```

---

## 7. 테스트 전략과 구조

### 7.1 컴포넌트 테스트 파일 배치

테스트 파일 배치에는 두 가지 주요 방식이 있다.

**코로케이션 방식 (권장)**:
```
components/
  Button/
    Button.tsx
    Button.test.tsx
    Button.stories.tsx
```

**`__tests__` 디렉토리 방식**:
```
components/
  Button/
    Button.tsx
__tests__/
  components/
    Button.test.tsx
```

코로케이션 방식이 현대 리액트 프로젝트에서 더 선호된다. 컴포넌트를 삭제하면 테스트도 함께 삭제되므로 죽은 테스트가 남지 않으며, 코드 리뷰 시 컴포넌트와 테스트를 함께 확인할 수 있다.

### 7.2 테스트 유형별 배치

```
src/
  features/
    product/
      ProductCard.tsx
      ProductCard.test.tsx          # 유닛 테스트 (컴포넌트 단위)
      ProductCard.integration.test.tsx  # 통합 테스트 (API 포함)
  __e2e__/                          # E2E 테스트 (프로젝트 루트)
    products.spec.ts
    checkout.spec.ts
  __mocks__/                        # 공통 모킹
    handlers.ts                     # MSW 핸들러
    server.ts
```

### 7.3 테스트 비율

| 테스트 유형 | 비율 | 도구 | 설명 |
|------------|------|------|------|
| **유닛 테스트** | ~20% | Vitest, Jest | 순수 함수, 유틸리티, 훅 |
| **통합 테스트** | ~60% | Testing Library, MSW | 컴포넌트 상호작용, API 연동 |
| **E2E 테스트** | ~20% | Playwright, Cypress | 사용자 시나리오 전체 흐름 |

> **Osmani의 조언**: 테스트 피라미드보다 "테스트 트로피"를 따르라. 통합 테스트에 가장 많은 비중을 두면, 유닛 테스트만으로는 잡지 못하는 컴포넌트 간 상호작용 버그를 효과적으로 발견할 수 있다.

---

## 최신 업데이트 (2026)

원서 출판(2023) 이후 리액트 애플리케이션 구조와 관련하여 몇 가지 중요한 변화가 있었다.

| 영역 | 변화 |
|------|------|
| **Next.js 15 App Router** | App Router 완전 안정화, `dynamicIO` 플래그로 동적/정적 렌더링 경계 명확화 |
| **Server Actions** | `useActionState` 도입 (React 19), 점진적 향상(*Progressive Enhancement*) 기본 지원 |
| **Turbopack** | 개발 서버 기본 번들러로 채택, 대규모 프로젝트에서 웹팩 대비 10배 빠른 HMR |
| **React Compiler** | 수동 `useMemo`/`useCallback` 대부분 불필요, 자동 메모이제이션 |
| **Partial Prerendering (PPR)** | 정적 셸 + 동적 홀로 한 페이지에서 정적/동적 렌더링을 결합 |
| **Feature Sliced Design** | 러시아 커뮤니티에서 시작해 글로벌 확산, 계층적 아키텍처의 표준으로 자리잡는 추세 |
| **Biome** | ESLint + Prettier를 대체하는 올인원 도구, 프로젝트 설정 파일 간소화 |

---

## 실무 적용 가이드

### 신규 프로젝트 시작 시 체크리스트

1. **프레임워크 선택**: Next.js App Router를 기본으로 고려한다. SSR/SSG/ISR이 불필요하고 SPA만 필요하면 Vite + React Router를 사용한다.
2. **폴더 구조 결정**: 팀 규모와 예상 프로젝트 규모에 맞는 구조를 초기에 선택한다.
3. **상태 관리 도구**: 처음에는 로컬 상태 + Context API로 시작하고, 필요할 때 도구를 추가한다.
4. **데이터 페칭**: Server Components를 우선 사용하고, 클라이언트 페칭이 필요하면 TanStack Query를 도입한다.
5. **테스트 전략**: 코로케이션 방식으로 테스트 파일을 배치하고, Vitest + Testing Library 조합을 기본으로 한다.

### 기존 프로젝트 마이그레이션 전략

기존 프로젝트의 구조를 한꺼번에 변경하는 것은 위험하다. 대신 **점진적 마이그레이션**을 권장한다:

1. 새로운 기능을 추가할 때 새로운 구조를 적용한다
2. 기존 코드를 수정할 때 해당 부분을 새 구조로 이전한다
3. 별도의 "구조 리팩터링" 스프린트를 잡지 않는다. 일상적인 개발 흐름 안에서 자연스럽게 전환한다

### import 경로 관리

깊은 중첩 구조에서 상대 경로(`../../../shared/ui/Button`)는 가독성을 해친다. TypeScript의 `paths` 설정이나 번들러의 alias 기능을 사용하여 절대 경로를 설정한다.

```json
// tsconfig.json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@features/*": ["./src/features/*"],
      "@shared/*": ["./src/shared/*"]
    }
  }
}
```

```tsx
// 상대 경로 (읽기 어려움)
import { Button } from '../../../shared/ui/Button';

// 절대 경로 (명확함)
import { Button } from '@shared/ui/Button';
```

---

## 요약

- 리액트는 프로젝트 구조에 대해 의견을 제시하지 않으므로, **팀이 합의한 규칙을 일관되게 따르는 것**이 가장 중요하다
- 파일 그룹화 전략은 **기능별**, **유형별**, **혼합** 세 가지가 있으며, 대부분의 실무 프로젝트에서는 혼합 그룹화가 적합하다
- 프로젝트 규모에 따라 구조를 진화시킨다: 소규모(유형별 평면) → 중규모(Feature Sliced) → 대규모(모노레포)
- **코로케이션 원칙** — 함께 변경되는 파일은 함께 둔다
- Next.js App Router는 **라우트 그룹**, **병렬 라우트**, **인터셉팅 라우트** 등 강력한 라우팅 기능을 제공한다
- 상태 관리는 **에스컬레이션 전략**을 따른다: useState → Context → Zustand/Jotai/Redux
- **서버 상태와 클라이언트 상태를 구분**하여 적합한 도구를 선택한다 (TanStack Query vs Zustand)
- Server Components에서 데이터를 페칭하고, `'use client'` 경계는 트리 하단에 배치한다
- 테스트 파일은 컴포넌트 옆에 코로케이션하고, **통합 테스트에 가장 높은 비중**을 둔다

---

## 다른 챕터와의 관계

- **← Ch07 (생성 패턴)**: 팩토리 패턴이나 싱글턴 패턴은 프로젝트 구조 내에서 서비스 인스턴스를 관리하는 데 활용된다
- **← Ch08 (구조 패턴)**: 데코레이터, 파사드 패턴이 API 래퍼나 공통 컴포넌트 설계에 반영된다
- **← Ch10 (MV* 패턴)**: MVC, MVVM 등 아키텍처 패턴이 feature 폴더 내부의 관심사 분리에 영향을 준다
- **← Ch14 (리액트 디자인 패턴)**: HOC, 렌더 프롭, 훅 패턴 등 리액트 고유 패턴이 이 장의 구조 안에서 어디에 배치되는지 이해할 수 있다
- **← Ch15 (렌더링 패턴)**: SSR, SSG, ISR 등 렌더링 패턴이 Next.js App Router 구조의 기반이 된다