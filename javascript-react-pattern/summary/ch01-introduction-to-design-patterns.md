# Chapter 01: Introduction to Design Patterns (디자인 패턴 소개) - 요약

**핵심 질문**: 디자인 패턴이란 무엇이며, 왜 현대 자바스크립트 개발에서 여전히 중요한가?

## 패턴의 기원: 건축에서 GoF까지

디자인 패턴은 소프트웨어가 아니라 **건축학**에서 시작됐다. 건축가 크리스토퍼 알렉산더는 건물과 도시 설계에서 반복적으로 나타나는 문제의 해결 경험을 문서화하며, 특정 디자인 구조를 반복 사용하면 최적의 효과를 얻는다는 사실을 발견했고, 동료들과 함께 **패턴 언어**(1977)를 만들었다.

1990년 무렵 소프트웨어 엔지니어들이 알렉산더의 원칙을 받아들이기 시작했고, 1995년 에리히 감마, 리차드 헬름, 랄프 존슨, 존 블리시드 - 이른바 **GoF(Gang of Four)** - 의 "GoF의 디자인 패턴"이 **23가지 핵심 객체 지향 디자인 패턴**을 체계화했다. 이 책(오스마니)의 6장에서 분류하고 7~9장에서 자바스크립트로 구현하는 것이 바로 그 패턴들이다.

## 패턴이란 무엇인가

패턴은 소프트웨어 설계에서 **반복되는 문제에 적용할 수 있는 재사용 가능한 템플릿**이다. 세 가지 핵심 특성이 있다:

- **검증됨**: 앞서간 개발자들의 경험과 통찰의 산물로, 오랜 시간 검증된 접근 방식이다
- **재사용 가능**: 독창적인 솔루션을 사용자의 요구에 맞춰 적용할 수 있다
- **알아보기 쉬움**: 정해진 구조와 공통 어휘를 사용한다

부가 이점도 뚜렷하다. 정해진 패턴을 쓰면 코드 구조가 잘못될 염려를 덜어 사소한 실수로 인한 큰 문제를 방지하고, 일반화된 함수로 코드 양을 줄이며(DRY), 팀과 커뮤니티가 공통 어휘로 소통하게 하고, 패턴 자체가 커뮤니티에서 개선되는 선순환을 만든다.

> **Osmani의 조언**: 패턴은 완벽한 해결책이 아니다. 체계화된 방법을 제시할 뿐 설계의 모든 문제를 해결해 주지 않는다. 좋은 패턴을 선택하려면 여전히 좋은 설계자가 필요하다.

## 일상 속 패턴: 공급자 패턴 (Provider Pattern)

리액트를 써봤다면 이미 패턴을 쓰고 있다. 컴포넌트 트리에서 사용자 정보 같은 데이터를 공유할 때, 계층을 따라 prop을 끝까지 내려보내는 **프롭 드릴링**이 생긴다.

```tsx
// 문제 - 프롭 드릴링: 중간 컴포넌트들이 쓰지도 않는 user를 나른다
function App() {
  const [user, setUser] = useState<User | null>(null);
  return <Dashboard user={user} />;
}
function Dashboard({ user }: { user: User | null }) {
  return <Settings user={user} />;
}
function Settings({ user }: { user: User | null }) {
  return <Profile user={user} />;
}

// 해결 - 공급자 패턴: Context Provider가 여러 컴포넌트에 한 번에 공급
const UserContext = createContext<User | null>(null);

function App() {
  const [user, setUser] = useState<User | null>(null);
  return (
    <UserContext.Provider value={user}>
      <Dashboard />
    </UserContext.Provider>
  );
}
function Profile() {
  const user = useContext(UserContext);
  return <span>{user?.name}</span>;
}
```

무의식적으로 쓰던 구조에 이름이 있다는 것, 그것이 패턴 학습의 실체다.

## 현대 자바스크립트에서 패턴의 위치

자바스크립트는 모듈, 클래스, 화살표 함수, 템플릿 리터럴 등 언어 차원의 발전과 리액트/Vue/앵귤러 생태계의 성장을 거쳤다. 패턴은 언어와 프레임워크에 독립적이지만, 적합한 상황이라고 반드시 적용해야 하는 것은 아니다 - 프레임워크가 이미 잘 설계돼 있어 불필요할 수도, 반대로 특정 패턴을 사실상 강제할 수도 있다.

원서(2023) 이후의 변화도 패턴 이해에 영향을 준다: React 19(use() Hook, Server Actions, React Compiler), Next.js 15(App Router 안정화), ECMAScript(Decorators 표준화, `using`), 경량 상태 관리(Zustand, Jotai)와 React Server Components 안정화 등. 이 책의 노트는 원서 내용에 이 2026년 변화를 보충해 반영한다.

> **핵심 통찰**: 패턴의 가치는 외워서 적용하는 데 있지 않고, 무의식적으로 작성하던 코드 구조에 이름을 붙이고 그 특징을 명확히 이해하는 데 있다. "이 패턴을 썼습니다" 한마디가 코드의 가독성과 유지보수 의도를 간결하게 전달한다.
