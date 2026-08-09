# Item 57: 꼬리 재귀 제네릭 타입 선호하기 (Prefer Tail-Recursive Generic Types)

## 핵심 질문

재귀 제네릭 타입은 왜 "Type instantiation is excessively deep" 에러를 내는가? 누산기는 이것을 어떻게 해결하는가?

컴퓨팅의 역사는 우연한 프로그래밍 언어들로 가득하다. 시스템에 커스터마이징을 조금 넣고, 사용자가 좋아해서 더 넣고, 계속 통제권을 주다 보면 누군가 튜링 완전이라고 지적하는 것이다! 유명한 예로 엑셀, C 전처리기, C++ 템플릿, 그리고 **타입스크립트의 제네릭 타입**이 있다.

이런 우연한 언어들은 대개 순수 함수형이다 - 최소의 개념으로 최대의 통제를 주기 때문이다. 필요한 것은 함수 합성과 분기뿐이다. 타입스크립트 타입 시스템에서 함수 합성은 제네릭 타입의 인스턴스화이고, 분기는 객체 타입의 키 조회나 조건부 타입이다. 순수 함수형 언어는 보통 **재귀**로 루프를 구현한다. Item 54에서 봤듯 문자열 타입 처리에 큰 효과를 내지만, 재귀 호출마다 스택에 새 항목이 필요하다는 현실적 단점이 있다.

## 1. 값의 세계에서 - 꼬리 호출 최적화

숫자 리스트를 합산하는 재귀 함수:

```typescript
function sum(nums: readonly number[]): number {
  if (nums.length === 0) {
    return 0;
  }
  return nums[0] + sum(nums.slice(1));
}
```

리스트의 숫자마다 스택 공간을 쓰는 재귀 호출이 하나씩 생겨 결국 넘친다(Node.js에서 대략 7,000~8,000개 요소에서 `RangeError: Maximum call stack size exceeded`).

함수형 프로그래머들의 영리한 해법: **함수가 마지막으로 하는 일이 자신을 재귀 호출하고 그 값을 반환하는 것뿐이라면, 스택 자리를 내놓을 수 있다** - 할 일이 끝났으니 더는 필요 없다. 이것이 꼬리 호출 최적화(*Tail Call Optimization, TCO*)이고, 이런 형태의 함수를 꼬리 재귀(tail recursive)라 한다. 누산기를 쓴 꼬리 재귀 버전:

```typescript
function sum(nums: readonly number[], acc=0): number {
  if (nums.length === 0) {
    return acc;
  }
  return sum(nums.slice(1), nums[0] + acc);
}
```

스택 오버플로 없이 빠르게 올바른 결과를 낸다.

## 2. 타입의 세계에서도 똑같다

같은 고려가 재귀 타입 별칭에 적용된다. 타입스크립트는 무한 루프와 타입 체커의 굼뜸을 막으려고 타입 별칭의 재귀 인스턴스화 횟수를 제한하는데, **꼬리 호출 최적화를 지원해서 꼬리 재귀 타입 별칭에는 훨씬 큰 깊이 한도**를 준다. 더 효율적이고 더 유능하므로 재귀 타입 별칭은 가능하면 꼬리 재귀로 만들어야 한다.

문자열 리터럴 타입을 한 글자씩 처리하는 제네릭에서 특히 중요하다. 문자열을 글자들의 유니온으로 바꾸는 제네릭:

```typescript
type GetChars<S extends string> =
  S extends `${infer FirstChar}${infer RestOfString}`
    ? FirstChar | GetChars<RestOfString>
    : never;

type ABC = GetChars<"abc">;
//   ^? type ABC = "a" | "b" | "c"
```

재귀 호출 **뒤에** 연산(FirstChar와의 유니온)을 수행하므로 꼬리 재귀가 아니다. 약 50자를 넘는 문자열 리터럴 타입에서 넘친다.

```typescript
type Long = GetChars<"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWX">;
//   ~~~~ Type instantiation is excessively deep and possibly infinite.
```

## 3. 현실적인 예 - ToSnake

Item 54의 `objectToCamel`의 반대 방향, camelCase→snake_case를 구현하자. 이번엔 구분자("_")가 없으므로 글자 단위로 처리한다.

```typescript
type ToSnake<T extends string> =
  string extends T
  ? string  // ToSnake<string> = string이길 원함
  : T extends `${infer First}${infer Rest}`
  ? (First extends Uppercase<First>  // First가 대문자인가?
     ? `_${Lowercase<First>}${ToSnake<Rest>}`  // 예: "B" -> "_b"
     : `${First}${ToSnake<Rest>}`)
  : T;

type S = ToSnake<'fooBarBaz'>;
//   ^? type S = "foo_bar_baz"
type Two = ToSnake<'className' | 'tagName'>;
//   ^? type Two = "class_name" | "tag_name"
```

첫 글자가 대문자인지에 따라 재귀 호출이 두 갈래다. 유니온 위로도 올바르게 분배된다(Item 53). 그런데 이 타입 별칭은 조건부의 두 분기 모두에서 재귀 호출 **뒤에** 일(문자열 연결·소문자화)을 하므로 꼬리 재귀가 아니고, 예상대로 스택이 쉽게 넘친다.

```typescript
type Long = ToSnake<'reallyDescriptiveNamePropThatsALittleTooLoquacious'>;
//   ~~~~ Type instantiation is excessively deep and possibly infinite.
```

긴 키를 가진 객체를 snake_case하려는 순간 타입이 터진다. 속성 이름에 50자면 충분해 보이지만 훨씬 긴 속성의 예는 많다 - 특히 자바 세계에는.

**누산기로 리팩터링**하면 긴 문자열 리터럴 타입의 제한이 풀리고 모든 인스턴스화의 타입 체크도 빨라진다.

```typescript
type ToSnake<T extends string, Acc extends string = ""> =
  string extends T
  ? string  // ToSnake<string> = string이길 원함
  : T extends `${infer First}${infer Rest}`
  ? ToSnake<
      Rest,
      First extends Uppercase<First>
        ? `${Acc}_${Lowercase<First>}`
        : `${Acc}${First}`
    >
  : Acc;

type S = ToSnake<'fooBarBaz'>;
//   ^? type S = "foo_bar_baz"
type Long = ToSnake<'reallyDescriptiveNamePropThatsALittleTooLoquacious'>;
//   ^? type Long = "really_descriptive_name_prop_thats_a_little_too_loquacious"
```

꼬리 재귀 `sum`처럼 **지금까지의 작업을 추적하는 누산기**를 추가해 재귀 인스턴스화를 꼬리 위치로 옮긴 것이다. 자바 동료들이 어떤 장황한 속성 이름을 던져도 snake_case할 수 있게 됐다!

## 기억해야 할 것들

- 재귀 제네릭 타입은 꼬리 재귀로 만드는 것을 목표로 하라. 더 효율적이고 깊이 한도가 더 크다.
- 재귀 타입 별칭은 누산기를 쓰도록 고쳐서 꼬리 재귀로 만들 수 있는 경우가 많다.
