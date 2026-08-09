# Item 28: 클래스와 커링으로 새 추론 지점 만들기 (Use Classes and Currying to Create New Inference Sites)

## 핵심 질문

제네릭 타입 매개변수 중 일부만 명시하고 나머지는 추론하게 하고 싶다면 어떻게 해야 하는가?

타입스크립트 인터페이스로 API를 정의했다고 하자.

```typescript
export interface SeedAPI {
  '/seeds': Seed[];
  '/seed/apple': Seed;
  '/seed/strawberry': Seed;
  // ...
}
```

이 API의 엔드포인트로 요청을 보내는 함수를 만들고 싶다 — 엔드포인트가 존재하는지 검사하고 올바른 타입의 데이터를 반환하는 함수. 원하는 동작은:

```typescript
// 올바른 사용:
const berry = await fetchAPI<SeedAPI>('/seed/strawberry');  // OK, Seed 반환
// 잘못된 사용 — 에러여야 한다:
fetchAPI<SeedAPI>('/seed/chicken');                    // 없는 엔드포인트
const seed: Seed = await fetchAPI<SeedAPI>('/seeds');  // 잘못된 반환 타입
```

타입만 생각하면 이렇게 선언할 수 있을 것 같다.

```typescript
declare function fetchAPI<
  API, Path extends keyof API
>(path: Path): Promise<API[Path]>;

fetchAPI<SeedAPI>('/seed/strawberry');
//       ~~~~~~~ Expected 2 type arguments, but got 1.
```

문제는 **타입스크립트의 타입 추론이 전부 아니면 전무**라는 것이다. 모든 타입 매개변수를 사용처에서 추론하게 하거나, 모두 명시적으로 지정하거나 — 중간이 없다. (타입 매개변수에 기본값을 줄 수는 있지만 다른 타입 매개변수만 참조할 수 있고 사용처에서 추론되지는 않는다.)

`API`는 어떤 API와도 동작해야 하니 추론이 불가능하고 명시해야만 한다. 그렇다고 `Path`까지 명시하면 짜증스럽게 반복적이다.

```typescript
const berry = fetchAPI<SeedAPI, '/seed/strawberry'>('/seed/strawberry');  // OK지만…
```

필요한 것은 **`API`를 명시하는 자리와 `Path`를 추론하는 자리를 분리**하는 것이다. 표준 방법이 두 가지 있다: 클래스와 커링.

## 1. 클래스

클래스는 상태 조각을 붙잡아 두는 데 능하다 — 관련 함수들(메서드)에 같은 상태를 반복해 넘기지 않게 해 준다. 타입스크립트에서 클래스는 **타입을 붙잡아 두는 데에도** 능하다.

```typescript
declare class ApiFetcher<API> {
  fetch<Path extends keyof API>(path: Path): Promise<API[Path]>;
}

const fetcher = new ApiFetcher<SeedAPI>();
const berry = await fetcher.fetch('/seed/strawberry');  // OK
//    ^? const berry: Seed

fetcher.fetch('/seed/chicken');
//            ~~~~~~~~~~~~~~~
// Argument of type '"/seed/chicken"' is not assignable to type 'keyof SeedAPI'

const seed: Seed = await fetcher.fetch('/seeds');
//    ~~~~ Seed[] is not assignable to Seed
```

정확히 원하던 에러들이다. 타입 매개변수 두 개짜리 함수가, **명시적으로 지정하는 제네릭 매개변수 하나를 가진 클래스** + **추론되는 제네릭 매개변수 하나를 가진 메서드**로 바뀌었다. 생성자 호출(`new ApiFetcher<SeedAPI>()`)에서 `API`를 바인딩하고 `fetch` 호출에서 `Path`를 추론하는 것을 타입스크립트는 아무 문제 없이 허용한다. 같은 타입 매개변수를 요구하는 **메서드가 여러 개**일 때 클래스로 바인딩 지점을 만드는 것이 특히 효과적이다.

## 2. 커링

재미있는 사실: 프로그래밍 언어에 매개변수 여러 개짜리 함수는 사실 필요 없다. 함수를 반환하는 함수로 대체할 수 있다.

```typescript
declare function getDate(mon: string, day: number): Date;
getDate('dec', 25);

// 커링 버전:
declare function getDate(mon: string): (day: number) => Date;
getDate('dec')(25);
```

이 기법이 커링(*currying - 다인수 함수를 함수를 반환하는 단인수 함수들의 연쇄로 바꾸는 것. 논리학자 하스켈 커리의 이름에서 왔는데, 정작 본인은 자기가 고안했다는 것을 늘 부인했다*)이다. 커링은 **원하는 만큼 추론 지점을 도입할 유연성**을 준다 — 함수 호출마다 새 타입 매개변수를 추론할 수 있다.

```typescript
declare function fetchAPI<API>():
  <Path extends keyof API>(path: Path) => Promise<API[Path]>;

const berry = await fetchAPI<SeedAPI>()('/seed/strawberry');  // OK
//    ^? const berry: Seed

fetchAPI<SeedAPI>()('/seed/chicken');
//                  ~~~~~~~~~~~~~~~
// Argument of type '"/seed/chicken"' is not assignable to type 'keyof SeedAPI'
```

중간 변수로 두 호출을 분리하면 반복이 줄어든다.

```typescript
const fetchSeedAPI = fetchAPI<SeedAPI>();
const berry = await fetchSeedAPI('/seed/strawberry');
//    ^? const berry: Seed
```

커링 접근은 보기보다 클래스 접근과 다르지 않다. 이름을 바꾸고 함수 대신 객체 타입을 반환하면 거의 똑같아진다 — 사용상 유일한 차이는 `new` 키워드뿐이다.

```typescript
declare function apiFetcher<API>(): {
  fetch<Path extends keyof API>(path: Path): Promise<API[Path]>;
}
const fetcher = apiFetcher<SeedAPI>();
fetcher.fetch('/seed/strawberry');  // OK
```

## 3. 무엇을 고를까 — 커링의 한 가지 이점

일부 제네릭 매개변수는 명시하고 나머지는 추론하게 하려면 클래스와 커링이 두 선택지다. 어느 쪽이든 편하고 편리한 API가 나오는 쪽으로 고르면 된다. 다만 타입스크립트 맥락에서 커링에는 한 가지 이점이 있다 — **지역 타입 별칭을 정의할 스코프가 생긴다.**

```typescript
function fetchAPI<API>() {
  type Routes = keyof API & string;  // 지역 타입 별칭
  return <Path extends Routes>(
    path: Path
  ): Promise<API[Path]> => fetch(path).then(r => r.json());
}
```

선언만으로는 안 되고 **구현만이 새 스코프를 도입**한다. `Routes` 같은 지역 별칭은 복잡한 타입 표현식의 반복을 줄여 준다. 클래스에는 이에 해당하는 것이 없다.

## 기억해야 할 것들

- 타입 매개변수가 여럿인 함수에서 추론은 전부 아니면 전무다: 모든 타입 매개변수가 추론되거나, 모두 명시되어야 한다.
- 부분 추론이 필요하면 클래스나 커링으로 새 추론 지점을 만들어라.
- 지역 타입 별칭을 만들고 싶다면 커링 접근을 선호하라.
