# Item 56: 타입이 표시되는 방식에 주의 기울이기 (Pay Attention to How Types Display)

## 핵심 질문

같은 타입도 여러 방식으로 표시될 수 있다면, 사용자에게 보이는 표시는 어떻게 다듬는가? Resolve 트릭은 어떻게 동작하는가?

보통 우리는 타입이 무엇이고 어떤 값이 할당 가능한지에 신경 쓴다. 하지만 타입스크립트 라이브러리를 쓸 때, **라이브러리가 타입을 표시하는 방식**이 사용 경험을 크게 좌우한다. 라이브러리 저자라면 타입의 표시에 주의를 기울여야 한다는 뜻이다.

어느 타입이든 유효한 표시 방법은 여럿이다. 유니온은 보통 나열한 순서로 표시되지만, 앞서 겹치는 유니온을 도입했다면 다르게 표시될 수도 있다.

```typescript
type T21 = '2' | '1';
//   ^? type T21 = "2" | "1"
type T123 = '1' | '2' | '3';
//   ^? type T123 = "2" | "1" | "3"
```

1, 2, 3인가 2, 1, 3인가? 정확히 같은 타입의 똑같이 유효한 두 표현이다. 이 경우엔 가독성이 비슷하지만, 표현에 따라 가독성이 크게 갈릴 때도 있다.

## 1. 구현이 새어 나오는 표시 — PartiallyPartial

객체의 일부 속성만 옵셔널로 만드는 `PartiallyPartial` 제네릭을 구현해 보자.

```typescript
type PartiallyPartial<T, K extends keyof T> =
  Partial<Pick<T, K>> & Omit<T, K>;

interface BlogComment {
  commentId: number;
  title: string;
  content: string;
}
type PartComment = PartiallyPartial<BlogComment, 'title'>;
//   ^? type PartComment =
//        Partial<Pick<BlogComment, "title">> & Omit<BlogComment, "title">
```

구현은 올바르고 이 표시도 완벽히 유효하다. 하지만 사용자 입장에서는 아쉽다 — `title`의 타입은 뭐지? nullable인가? `Omit` 뒤에는 어떤 필드들이 있지? 결과 타입이 **무엇인지**보다 제네릭이 **어떻게 정의됐는지**를 말해 주는, 온통 구현 냄새 나는 표시다.

## 2. Resolve 트릭

타입스크립트에게 제네릭 타입을 좀 더 풀어헤치라고 시키는 널리 퍼진 트릭이 있다.

```typescript
type Resolve<T> = T extends Function ? T : {[K in keyof T]: T[K]};

type PartiallyPartial<T, K extends keyof T> =
  Resolve<Partial<Pick<T, K>> & Omit<T, K>>;

type PartComment = PartiallyPartial<BlogComment, 'title'>;
//   ^? type PartComment = {
//        title?: string | undefined;
//        commentId: number;
//        content: string;
//      }
```

`Resolve`로 감쌌더니 모든 속성이 평평하게 펼쳐졌다. 무슨 타입인지 훨씬 명확하고, 구현의 흔적(Partial·Pick·Omit)이 전부 사라졌다.

어떻게 동작할까? 조건부 타입을 무시하면 객체 타입의 항등처럼 보이는 표현식이 남는다: `{[K in keyof T]: T[K]}`. 실제로 이것이 타입을 "풀어" 준다. 동형 매핑된 타입이라(Item 15) 원시 타입은 수정 없이 통과시킨다(`ObjIdentity<string>`은 string). 하지만 **함수에는 항등이 아니라서**(`{}`가 되어 버린다) `T extends Function ? T : ...` 가드가 필요한 것이다.

이 헬퍼는 제네릭을 많이 쓰는 타입스크립트 코드에 어디에나 있다. `Resolve`는 저자의 이름 선택이고 `Simplify`·`NOP`·`NOOP`·`MergeInsertions`라고도 불린다.

주의할 점들:

- **DeepResolve는 보통 나쁜 생각**이다 — 클래스에 지나치게 공격적이 된다. `Resolve<Date>`는 메서드 42개가 펼쳐진 흉물이 된다. `Date`는 그냥 `Date`로 표시되게 두는 것이 낫다.
- `keyof` 표현식을 인라인하는 데도 쓸 수 있다 — 가독성이 나아진다고 판단되면.

```typescript
interface Color { r: number; g: number; b: number; a: number };
type Chan = keyof Color;
//   ^? type Chan = keyof Color
type ChanInline = Resolve<keyof Color>;
//   ^? type ChanInline = "r" | "g" | "b" | "a"
```

- 다른 기법들 — `Exclude<keyof T, never>`(keyof 인라인), `unknown & T`·`{} & T`(객체 인라인) — 도 보이지만, 같은 효과에 덜 취약한 `Resolve`로 대체할 수 있다.

## 3. 중요한 특수 케이스는 따로 처리

특별히 깨끗하게 표시되길 바라는 케이스가 있을 수 있다. `PartiallyPartial`에서 `K`가 never라면(아무 필드도 옵셔널이 아니라면) 결과는 그냥 `BlogComment`인데, 현재 정의로는 펼쳐진 형태로 나온다. 그 케이스를 검사해서 더 간결한 타입을 줄 수 있다.

```typescript
type PartiallyPartial<T extends object, K extends keyof T> =
  [K] extends [never]
  ? T  // 특수 케이스
  : T extends unknown  // 유니온 분배 보존용 조건
  ? Resolve<Partial<Pick<T, K>> & Omit<T, K>>
  : never;

type FullComment = PartiallyPartial<BlogComment, never>;
//   ^? type FullComment = BlogComment
```

(조건을 튜플로 감싼 것과 `T extends unknown` 절의 이유는 Item 53.) 이 특수 케이스 처리는 `PartiallyPartial`의 **동작을 전혀 바꾸지 않는다** — 한 상황에서 결과가 표시되는 방식만 개선한다.

> **핵심 통찰**: 타입 표시를 바꿀 때 한 경우의 가독성을 위해 다른 경우를 희생하지 않는지 확인하라. 이런 조작은 미묘하고 할당 가능성에 영향이 없어서 회귀가 눈에 안 띄기 쉽고, 새 타입스크립트 버전도 표시를 바꿀 수 있다. 그래서 **타입의 표시를 테스트하는 체계**가 중요하다(Item 55).

## 기억해야 할 것들

- 같은 타입을 표시하는 유효한 방법은 여럿이며, 어떤 것은 다른 것보다 명확하다.
- 타입스크립트는 표시를 통제하는 도구를 준다. 특히 `Resolve` 제네릭 — 타입 표시를 명료하게 하고 구현 세부를 감추는 데 분별 있게 활용하라.
- 제네릭 타입의 중요한 특수 케이스를 처리해 타입 표시를 개선하는 것을 고려하라.
- 회귀를 막기 위해 제네릭 타입과 그 표시에 대한 테스트를 작성하라.
