# Item 62: 나머지 매개변수와 튜플 타입으로 가변 인수 함수 모델링하기 (Use Rest Parameters and Tuple Types to Model Variadic Functions)

## 핵심 질문

타입에 따라 인수 개수가 달라지는 함수는 어떻게 타이핑하는가?

웹 앱의 라우트별 쿼리 매개변수를 기술하는 인터페이스가 있다.

```typescript
interface RouteQueryParams {
  '/': null,
  '/search': { query: string; language?: string; }
  // ...
}
```

루트 페이지(`/`)는 쿼리 매개변수를 받지 않고, `/search`는 `query`와 옵셔널 `language`를 받는다. 라우트의 URL을 만드는 함수:

```typescript
function buildURL(route: keyof RouteQueryParams, params?: any) {
  return route + (params ? `?${new URLSearchParams(params)}` : '');
}
```

기대하는 URL은 만들어지지만 둘째 매개변수의 `any` 때문에 전혀 안전하지 않다 — 아무 라우트에나 아무 검색 매개변수를 붙일 수 있다.

```typescript
buildURL('/', {query: 'recursion'});  // 에러여야 함 (루트에는 매개변수 없음)
buildURL('/search');                  // 에러여야 함 (매개변수 누락)
```

더 안전한 버전 — 라우트를 제네릭으로 만들고(보통 추론된다) 매개변수 타입이 라우트에 의존하게 한다.

```typescript
function buildURL<Path extends keyof RouteQueryParams>(
  route: Path,
  params: RouteQueryParams[Path]
) {
  return route + (params ? `?${new URLSearchParams(params)}` : '');
}
```

`/search` 라우트에는 완벽하다.

```typescript
buildURL('/search', {query: 'do a barrel roll'})                  // OK
buildURL('/search', {query: 'do a barrel roll', language: 'en'})  // OK
buildURL('/search', {})
//                  ~~ Property 'query' is missing in type '{}'
```

그런데 루트 페이지에는 `null`을 추가로 넘겨야 한다.

```typescript
buildURL('/', {query: 'recursion'});  // 에러 — 좋다!
buildURL('/', null);                  // OK
buildURL('/');                        // 이것이 허용되길 원한다
//        ~~~~~ Expected 2 arguments, but got 1.
```

`null` 하나 더 쓰는 게 큰일은 아니지만 성가시고, 옵셔널 매개변수였던 옛 API가 더 보기 좋았다. 둘째 매개변수를 옵셔널로 만들되 **라우트가 검색 매개변수를 받지 않을 때만** 허용하고 싶다. 즉, **추론된 타입에 따라 인수 개수가 달라지는 함수**를 원한다.

## 1. 트릭 — 조건부 타입 + 나머지 매개변수

```typescript
function buildURL<Path extends keyof RouteQueryParams>(
  route: Path,
  ...args: (
    RouteQueryParams[Path] extends null
      ? []
      : [params: RouteQueryParams[Path]]
  )
) {
  const params = args ? args[0] : null;
  return route + (params ? `?${new URLSearchParams(params)}` : '');
}
```

쿼리 매개변수 타입이 null을 extends 하면 시그니처가 `(route: Path, ...args: [])` — **1개 매개변수 함수**처럼 보인다. 아니면 `(route: Path, ...args: [params: ...])` — **2개 매개변수 함수**다. 정확히 바라던 대로 동작한다.

```typescript
buildURL('/search', {query: 'do a barrel roll'})   // OK
buildURL('/search', {})
//                  ~~ Property 'query' is missing in type '{}'
buildURL('/', {query: 'recursion'});
//            ~~~~~~~~~~~~~~~~~~~~ Expected 1 arguments, but got 2.
buildURL('/', null);
//            ~~~~ Expected 1 arguments, but got 2.
buildURL('/');  // OK
```

호출 지점을 들여다보면 정말 라우트에 따라 두 개의 다른 함수가 있는 것처럼 보인다. 나머지 매개변수는 사용자에게 감춰진 구현 세부 사항이다. 타입스크립트가 **튜플 요소의 레이블에서 둘째 매개변수의 이름(`params`)까지 집어 온** 것에 주목하라.

```typescript
buildURL('/');
// ^? function buildURL<"/">(route: "/"): string
buildURL('/search', {query: 'do a barrel roll'})
// ^? function buildURL<"/search">(
//      route: "/search", params: { query: string; language?: string; }
//    ): string
```

레이블을 안 붙이면 사용자에게 `args_0` 같은 밋밋한 매개변수 이름이 보인다.

## 2. 오버로드와의 비교

가변 인수 함수를 모델링하는 가장 일반적인 기법이 이것이다. 오버로드 시그니처로 비슷한 효과를 낼 수도 있지만 코드 중복이 생기고, Item 52에서 봤듯 조건부 타입이 오버로드보다 유니온을 자연스럽게 처리한다.

> **핵심 통찰**: 함수의 매개변수 개수나 타입이 타입스크립트 타입에 의존할 때가 있다. 그럴 때는 튜플 타입의 나머지 매개변수로 모델링하라.

## 기억해야 할 것들

- 시그니처가 인수의 타입에 의존하는 함수는 나머지 매개변수와 튜플 타입으로 모델링하라.
- 한 매개변수의 타입과 나머지 매개변수들의 개수·타입 사이의 관계는 조건부 타입으로 모델링하라.
- 호출 지점에서 의미 있는 매개변수 이름이 보이도록 튜플 타입의 요소에 레이블을 붙이는 것을 잊지 마라.
