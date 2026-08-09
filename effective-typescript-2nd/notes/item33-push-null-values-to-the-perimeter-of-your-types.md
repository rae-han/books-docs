# Item 33: null 값을 타입의 가장자리로 밀어내기 (Push Null Values to the Perimeter of Your Types)

## 핵심 질문

"A가 null이 아니면 B도 null이 아니다" 같은 암묵적 관계는 왜 위험한가? null을 어디에 배치해야 코드가 단순해지는가?

`strictNullChecks`를 처음 켜면 코드 전체에 null·undefined 체크 if 문을 수십 개 추가해야 할 것처럼 보인다. 그 원인은 대개 **null 값과 non-null 값 사이의 관계가 암묵적**이기 때문이다 - 변수 A가 null이 아니면 B도 null이 아니라는 것을 나는 알지만, 사람 독자에게도 타입 체커에게도 이 암묵적 관계는 혼란스럽다.

**값은 완전히 null이거나 완전히 non-null일 때 다루기 쉽다.** 섞여 있으면 어렵다. null 값을 구조의 가장자리(perimeter)로 밀어내서 이를 모델링할 수 있다.

## 1. extent 예제 - 함께 태어나는 두 값

숫자 목록의 최솟값·최댓값("범위")을 계산하는 시도:

```typescript
// @strictNullChecks: false
function extent(nums: Iterable<number>) {
  let min, max;
  for (const num of nums) {
    if (!min) {
      min = num;
      max = num;
    } else {
      min = Math.min(min, num);
      max = Math.max(max, num);
    }
  }
  return [min, max];
}
```

strictNullChecks 없이는 타입 체크를 통과하고 추론 반환 타입도 `number[]`로 그럴듯하다. 하지만 버그와 설계 결함이 있다.

1. **min이나 max가 0이면 덮어쓰일 수 있다**: `extent([0, 1, 2])`는 `[0, 2]`가 아니라 `[1, 2]`를 반환한다 (`!min`이 0에서도 참이므로).
2. **배열이 비어 있으면 `[undefined, undefined]`를 반환한다.**

undefined가 여럿 든 객체는 클라이언트가 다루기 어렵고, 정확히 이 아이템이 말리는 종류의 타입이다. 소스를 읽으면 min과 max가 **둘 다 undefined거나 둘 다 아니거나**임을 알 수 있지만, 이 정보는 타입 시스템에 표현되어 있지 않다.

`strictNullChecks`를 켜면 문제가 드러난다.

```typescript
function extent(nums: Iterable<number>) {
  let min, max;
  for (const num of nums) {
    if (!min) {
      min = num;
      max = num;
    } else {
      min = Math.min(min, num);
      max = Math.max(max, num);
      //             ~~~ Argument of type 'number | undefined' is not
      //                 assignable to parameter of type 'number'
    }
  }
  return [min, max];
}
```

반환 타입이 `(number | undefined)[]`로 추론되어 설계 결함이 더 뚜렷해졌고, `extent`를 호출하는 곳마다 타입 에러로 나타난다.

```typescript
const [min, max] = extent([0, 1, 2]);
const span = max - min;
//           ~~~   ~~~ Object is possibly 'undefined'
```

구현의 에러는 `min`에서만 undefined를 배제하고 `max`에서는 안 했기 때문이다. 둘은 함께 초기화되지만 그 정보가 타입 시스템에 없다. max 체크를 추가해서 없앨 수도 있지만 그건 버그를 배가시키는 짓이다.

**더 나은 해법: min과 max를 한 객체에 넣고, 그 객체가 완전히 null이거나 완전히 non-null이게 하라.**

```typescript
function extent(nums: Iterable<number>) {
  let minMax: [number, number] | null = null;
  for (const num of nums) {
    if (!minMax) {
      minMax = [num, num];
    } else {
      const [oldMin, oldMax] = minMax;
      minMax = [Math.min(num, oldMin), Math.max(num, oldMax)];
    }
  }
  return minMax;
}
```

반환 타입이 `[number, number] | null`이 되어 클라이언트가 다루기 쉽다. 널 아님 단언이나 체크 한 번으로 꺼내 쓸 수 있다.

```typescript
const [min, max] = extent([0, 1, 2])!;
const span = max - min;  // OK

// 또는
const range = extent([0, 1, 2]);
if (range) {
  const [min, max] = range;
  const span = max - min;  // OK
}
```

객체 하나로 범위를 추적하면서 설계가 좋아졌고, 타입스크립트가 null 값들의 관계를 이해하게 됐고, 버그도 고쳐졌다 - 이제 `if (!minMax)` 체크는 문제가 없다(0이어도 [0, 0]은 truthy). 다음 단계로 빈 리스트를 아예 못 넘기게 하면 null 반환 가능성 자체를 없앨 수 있다 - 비어 있지 않은 리스트의 타입 표현은 Item 64에서.

## 2. 클래스에서 - 부분적으로 로드된 상태를 없애라

null과 non-null의 혼합은 클래스에서도 문제를 만든다. 사용자와 그의 포럼 게시물을 함께 표현하는 클래스:

```typescript
class UserPosts {
  user: UserInfo | null;
  posts: Post[] | null;

  constructor() {
    this.user = null;
    this.posts = null;
  }

  async init(userId: string) {
    return Promise.all([
      async () => this.user = await fetchUser(userId),
      async () => this.posts = await fetchPostsForUser(userId)
    ]);
  }

  getUserName() {
    // ...?
  }
}
```

두 네트워크 요청이 로딩되는 동안 `user`와 `posts`는 null이다. 어느 시점이든 둘 다 null이거나, 하나만 null이거나, 둘 다 non-null일 수 있다 - **네 가지 가능성**. 이 복잡성이 클래스의 모든 메서드로 스며든다. 혼란, null 체크의 증식, 버그가 거의 확정이다.

더 나은 설계는 **클래스가 쓰는 데이터가 전부 준비될 때까지 기다리는 것**이다.

```typescript
class UserPosts {
  user: UserInfo;
  posts: Post[];

  constructor(user: UserInfo, posts: Post[]) {
    this.user = user;
    this.posts = posts;
  }

  static async init(userId: string): Promise<UserPosts> {
    const [user, posts] = await Promise.all([
      fetchUser(userId),
      fetchPostsForUser(userId)
    ]);
    return new UserPosts(user, posts);
  }

  getUserName() {
    return this.user.name;
  }
}
```

이제 `UserPosts`는 완전히 non-null이고 올바른 메서드를 쓰기 쉽다. 물론 데이터가 부분적으로 로드된 동안 작업해야 한다면 null·non-null 상태의 다중성을 다뤄야 한다.

> **실무 팁**: nullable 속성을 프로미스로 대체하고 싶은 유혹을 참아라. 코드가 더 혼란스러워지고 모든 메서드가 async가 되어야 한다. 프로미스는 데이터를 **로드하는** 코드는 명료하게 하지만, 그 데이터를 **사용하는** 클래스에는 반대 효과를 내는 경향이 있다.

## 기억해야 할 것들

- 한 값의 null 여부가 다른 값의 null 여부와 암묵적으로 얽히는 설계를 피하라.
- 더 큰 객체가 null이거나 완전히 non-null이게 만들어 null 값을 API의 가장자리로 밀어내라. 사람 독자에게도 타입 체커에게도 코드가 명확해진다.
- 완전히 non-null인 클래스를 만들고 모든 값이 준비됐을 때 생성하는 것을 고려하라.
