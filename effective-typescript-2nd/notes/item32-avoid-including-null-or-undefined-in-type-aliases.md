# Item 32: 타입 별칭에 null이나 undefined 포함하지 않기 (Avoid Including null or undefined in Type Aliases)

## 핵심 질문

`User`라는 이름의 타입이 null일 수도 있다면 코드 독자에게 무슨 일이 생기는가?

이 코드에서 옵셔널 체인(`?.`)은 필요한가? `user`가 null일 수 있나?

```typescript
function getCommentsForUser(comments: readonly Comment[], user: User) {
  return comments.filter(comment => comment.userId === user?.id);
}
```

`strictNullChecks`를 가정해도 **`User`의 정의를 보기 전에는 대답할 수 없다.** null이나 undefined를 허용하는 타입 별칭이라면 옵셔널 체인이 필요하다.

```typescript
type User = { id: string; name: string; } | null;
```

단순한 객체 타입이라면 필요 없다.

```typescript
interface User {
  id: string;
  name: string;
}
```

일반 규칙: **null이나 undefined 값을 허용하는 타입 별칭은 피하는 것이 좋다.** 이 규칙을 어겨도 타입 체커는 혼동하지 않지만 **사람 독자가 혼동한다**. `User`라는 타입 이름을 읽으면 우리는 그것이 사용자를 표현한다고 가정하지, "사용자일 수도 있는 것"을 표현한다고 가정하지 않는다.

어떤 이유로 타입 별칭에 null을 꼭 넣어야 한다면, 독자를 위해 모호하지 않은 이름이라도 써라.

```typescript
type NullableUser = { id: string; name: string; } | null;
```

하지만 `User | null`이 더 간결하고 누구나 알아보는 문법인데 굳이 그럴 이유가 있을까?

```typescript
function getCommentsForUser(comments: readonly Comment[], user: User | null) {
  return comments.filter(comment => comment.userId === user?.id);
}
```

## 적용 범위 — 별칭의 최상위 수준

이 규칙은 타입 별칭의 **최상위 수준**에 관한 것이다. 더 큰 객체 안의 null·undefined(또는 옵셔널) 속성과는 무관하다.

```typescript
// 괜찮다
type BirthdayMap = {
  [name: string]: Date | undefined;
};

// 이렇게는 하지 말 것
type BirthdayMap = {
  [name: string]: Date | undefined;
} | null;
```

객체 타입 안의 null 값과 옵셔널 필드를 피할 이유도 따로 있지만 그것은 Item 33과 37의 주제다. 지금은 코드 독자를 혼란스럽게 할 타입 별칭을 피하는 것 — **무언가를 표현하는 타입 별칭을 선호하라. "무언가 또는 null 또는 undefined"를 표현하는 별칭이 아니라.**

## 기억해야 할 것들

- null이나 undefined를 포함하는 타입 별칭을 정의하지 마라.
