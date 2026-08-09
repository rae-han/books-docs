# Item 51: 불필요한 타입 매개변수 피하기 (Avoid Unnecessary Type Parameters)

## 핵심 질문

"타입 매개변수는 두 번 나타나야 한다"는 제네릭의 황금률은 무엇을 걸러내는가? 한 번만 나타나는 타입 매개변수는 어떻게 고치는가?

공식 타입스크립트 핸드북의 말:

> Writing generic functions is fun, and it can be easy to get carried away with type parameters. Having too many type parameters or using constraints where they aren't needed can make inference less successful, frustrating callers of your function.<br>제네릭 함수 작성은 재미있어서 타입 매개변수에 도취되기 쉽다. 타입 매개변수가 너무 많거나 불필요한 제약을 쓰면 추론이 잘 안 되어 함수 호출자를 좌절시킨다.

핸드북은 "제네릭의 황금률(Golden Rule of Generics)"이라 불리는 조언도 준다.

> **타입 매개변수는 두 번 나타나야 한다.** 타입 매개변수는 여러 값의 타입을 **관련짓기** 위한 것이다. 함수 시그니처에 한 번만 나타난다면 아무것도 관련짓고 있지 않다.<br>규칙: 타입 매개변수가 한 곳에만 나타난다면, 정말 필요한지 강하게 재고하라.

## 1. 좋은 예와 나쁜 예

**항등 함수 — 통과.** 선언부를 빼고 `T`가 두 곳에 나타난다. 입력 매개변수의 타입과 반환 타입이 같다고 **관련짓고** 있다.

```typescript
function identity<T>(arg: T): T {
  //           (선언)    1   2
  return arg;
}
```

**세 번째 인수 반환 — A·B 탈락.**

```typescript
function third<A, B, C>(a: A, b: B, c: C): C {
  return c;
}
// C는 두 번이라 괜찮지만 A·B는 한 번씩 — unknown으로 대체
function third<C>(a: unknown, b: unknown, c: C): C {
  return c;
}
```

**반환 전용 제네릭 — 탈락이자 위험.**

```typescript
declare function parseYAML<T>(input: string): T;
```

`T`가 한 번만 나타나니 나쁘다. 이런 "반환 전용 제네릭"은 **`as`라는 단어 없는 타입 단언과 동등**해서 위험하다.

```typescript
interface Weight {
  pounds: number;
  ounces: number;
}
const w: Weight = parseYAML('');
```

단언도 any도 없어 보이지만 착시다 — `Weight`를 어떤 타입으로 바꿔도 타입 체크를 통과한다. 타입 매개변수에 기본값을 줘도 마찬가지다. `unknown`을 반환하게 하는 것이 낫다(Item 46).

```typescript
declare function parseYAML(input: string): unknown;
const w = parseYAML('') as Weight;
```

사용자가 결과에 타입 단언을 하도록 강제되는데, 이것은 오히려 좋은 일이다 — **안전하지 않은 단언을 명시적으로** 하게 만드니까. 타입 안전의 착시가 없다!

**printProperty vs getProperty — 겉은 닮았지만 판정이 다르다.**

```typescript
function printProperty<T, K extends keyof T>(obj: T, key: K) {
  console.log(obj[key]);
}
```

`K`가 한 번만 나타나니 나쁜 사용이다(`T`는 매개변수 타입과 K의 제약 두 곳이라 괜찮다). `keyof T`를 매개변수 타입으로 옮기고 K를 없앤다.

```typescript
function printProperty<T>(obj: T, key: keyof T) {
  console.log(obj[key]);
}
```

반면 이것은:

```typescript
function getProperty<T, K extends keyof T>(obj: T, key: K) {
  return obj[key];
}
```

**좋은 사용이다.** 편집기에서 확인하면 추론된 반환 타입이 `T[K]`다 — 즉 시그니처가 사실상 `(obj: T, key: K): T[K]`이고, **K는 두 번 나타난다**(추론된 타입 속에!). K는 T와 관련되고 반환 타입은 둘 다와 관련된다.

## 2. 클래스에서

```typescript
class ClassyArray<T> {
  arr: T[];
  constructor(arr: T[]) { this.arr = arr; }
  get(): T[] { return this.arr; }
  add(item: T) { this.arr.push(item); }
  remove(item: T) {
    this.arr = this.arr.filter(el => el !== item)
  }
}
```

`T`가 여러 번(5번) 나타나므로 괜찮다. 인스턴스화 시 타입 매개변수가 바인딩되어 클래스의 모든 속성·메서드의 타입을 관련짓는다(추론 지점 만들기에도 유용 — Item 28).

반면 이 클래스는 탈락이다.

```typescript
class Joiner<T extends string | number> {
  join(els: T[]) {
    return els.map(el => String(el)).join(',');
  }
}
```

우선 `T`가 `join`에만 관련되니 클래스가 아니라 메서드로 내린다 — 선언을 사용처 가까이 옮기면 T의 추론이 가능해지고, 일반적으로 그게 바람직하다. 그런데 이 경우 T는 한 번만 나타나므로 **비제네릭으로** 만들어야 한다. 그리고 애초에 왜 클래스여야 하나? 이런 래퍼 클래스는 (독립 함수가 없는) 자바에서 흔하지만 자바스크립트에는 불필요하다. 독립 함수로 만들자.

```typescript
function join(els: (string|number)[]) {
  return els.map(el => String(el)).join(',');
}
```

**length를 가진 값 — 제약만으로 충분한 경우.**

```typescript
interface Lengthy {
  length: number;
}
function getLength<T extends Lengthy>(x: T) {
  return x.length;
}
```

T가 한 번뿐이므로 나쁜 사용. 이렇게들 쓸 수 있다.

```typescript
function getLength(x: Lengthy) { return x.length; }
function getLength(x: {length: number}) { return x.length; }
function getLength(x: ArrayLike<unknown>) { return x.length; }
```

## 3. 예외 — 드물지만 있다

모든 규칙에 예외가 있다. 남는 타입 매개변수가 **구현을 올바르게 만드는 데** 도움이 되는 드문 경우가 있다.

```typescript
declare function processUnrelatedTypes<A, B>(a: A, b: B): void;  // 둘 다 나쁨
declare function processUnrelatedTypes(a: unknown, b: unknown): void;  // 수정
```

그런데 구현에는 영향이 있다 — 첫 선언에서는 함수 본문에서 `a`와 `b`가 서로 할당 불가능했지만, 고친 시그니처에서는 둘 다 unknown이라 서로 할당된다. 우회법은 단일 오버로드로 호출자용과 구현용 시그니처를 분리하는 것이다(Item 52). 하지만 일반적으로 이런 상황은 드물며, 한 번만 나타나는 제네릭 타입 매개변수는 피해야 한다.

> **핵심 통찰**: 제네릭 함수를 읽고 쓸 때마다 황금률을 따르는지 생각하라. 함수나 클래스가 제네릭일 필요가 없다면, 제네릭이 아닌 편이 이해하고 유지하기 쉽다. 달리 말해 — **제네릭의 첫 번째 규칙은 "쓰지 마라"다.**

## 기억해야 할 것들

- 필요 없는 함수·클래스에 타입 매개변수를 추가하지 마라.
- 타입 매개변수는 타입들을 관련짓는 것이므로, 모든 타입 매개변수는 두 번 이상 나타나 관계를 형성해야 한다.
- 타입 매개변수가 추론된 타입 안에 나타날 수도 있음을 기억하라.
- "반환 전용 제네릭"을 피하라.
- 불필요한 타입 매개변수는 대개 unknown 타입으로 대체할 수 있다.
