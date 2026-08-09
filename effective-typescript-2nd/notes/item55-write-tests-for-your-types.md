# Item 55: 타입에 대한 테스트 작성하기 (Write Tests for Your Types)

## 핵심 질문

타입 선언의 버그는 어떻게 잡는가? 할당 가능성 테스트는 어디서 실패하고, 어떤 도구를 써야 하는가?

> Write tests until fear is transformed into boredom.<br>두려움이 지루함으로 바뀔 때까지 테스트를 써라.<br>- Phlip (켄트 벡, "테스트 주도 개발"에서 재인용)

테스트 없이 코드를 쓰지 않듯(그러길 바란다!) 타입 선언도 테스트 없이 쓰면 안 된다. 타입스크립트에서 이 필요가 특히 절실한 이유가 둘 있다: ① 타입에 어마어마한 양의 로직을 넣을 수 있다 - 로직이 있는 곳에 버그가 있을 수 있고, 버그가 있을 수 있는 곳에 테스트를 써야 한다. ② 타입을 런타임 구현과 독립적으로 정의할 수 있다 - 즉 둘이 어긋날 수 있다.

유틸리티 라이브러리의 `map` 타입 선언을 테스트한다고 하자.

```typescript
declare function map<U, V>(array: U[], fn: (u: U) => V): V[];
```

## 1. 비효과적인 방법들과 그 교훈

**호출만 하는 테스트** - 무딘 검사다. 반환값을 확인하지 않는 `square(1); square(2);` 스타일의 런타임 테스트와 같다 - 틀린 구현도 통과한다.

```typescript
map(['2017', '2018', '2019'], v => Number(v));
```

**할당 테스트** - 결과를 선언된 타입의 변수에 할당한다.

```typescript
const lengths: number[] = map(['john', 'paul'], name => name.length);
```

Item 18이라면 지우라고 할 불필요한 타입 선언이지만 여기서는 핵심 역할을 한다. 실제로 DefinitelyTyped의 많은 선언이 이 방식으로 테스트한다. 하지만 문제가 있다.

1. **쓰이지 않는 이름 붙은 변수**를 만들어야 한다 - 보일러플레이트에 미사용 변수 린트 룰도 꺼야 한다. 흔한 우회는 헬퍼다: `function assertType<T>(x: T) {}`
2. **동등성이 아니라 할당 가능성을 검사한다.** `assertType<number>(12)`처럼 서브타입이 통과하는 것은 기대대로지만, 객체에서는 뿌예진다.

```typescript
const beatles = ['john', 'paul', 'george', 'ringo'];
assertType<{name: string}[]>(
  map(beatles, name => ({
    name,
    inYellowSubmarine: name === 'ringo'
  }))
);  // OK - 그런데 노란 잠수함은?!
```

반환은 `{name, inYellowSubmarine}` 배열인데 `{name: string}[]`에 할당 가능하니 통과한다. 정말 원한 것은 **타입 동등성** 검사다.

3. **함수 타입에서 특히 이상하다.**

```typescript
const double = (x: number) => 2 * x;
assertType<(a: number, b: number) => number>(double);  // OK!?
```

매개변수 수가 다른데 통과한다. 타입스크립트에서 **함수 타입은 더 적은 매개변수를 받는 함수 타입에 할당 가능**하기 때문이다 - 자바스크립트에서 선언보다 많은 인수로 함수를 호출하는 것이 아무 문제 없다는 사실의 반영이고, 콜백에서 만연한 패턴(`map(array, (element, index, array) => ...)`에서 하나만 쓰는 것)이라 막지 않는다.

## 2. 콜백 내부와 this까지 테스트하기

지금까지의 테스트는 "블랙박스" 스타일이었다. 콜백을 채워서 매개변수와 `this`의 타입을 직접 검증할 수도 있다.

```typescript
const beatles = ['john', 'paul', 'george', 'ringo'];
assertType<number[]>(map(
  beatles,
  function(name, i, array) {
    // ~~~ Argument of type '(name: any, i: any, array: any) => any' is
    //     not assignable to parameter of type '(u: string) => any'
    assertType<string>(name);
    assertType<number>(i);
    assertType<string[]>(array);
    assertType<string[]>(this);
    // ~~~~ 'this' implicitly has type 'any'
    return name.length;
  }
));
```

우리의 `map` 선언 문제가 드러났다 - 콜백이 매개변수 하나만 받고 `this`의 타입도 없다. (`this`를 테스트하려고 화살표 함수 대신 함수 표현식을 쓴 것에 주목.) 통과하는 선언:

```typescript
declare function map<U, V>(
  array: U[],
  fn: (this: U[], u: U, i: number, array: U[]) => V
): V[];
```

**그러나 결정적 문제가 남는다.** 가장 엄격한 테스트도 통과하면서 쓸모없는 것보다 나쁜 선언 파일이 있다.

```typescript
declare module 'your-amazing-module';
```

모듈 전체가 any다. 단언은 전부 통과하지만 타입 안전성은 없고, 모듈의 모든 함수 호출이 조용히 any를 낳아 코드 전체의 타입 안전성을 전염적으로 파괴한다. 대응 하나는 **실패해야 하는 "부정" 테스트**다.

```typescript
// @ts-expect-error 매개변수는 두 개만
map([1, 2, 3], x => x * x, 'third parameter');
```

에러가 **없으면** 컴파일 에러가 난다. any에 대한 보호가 어느 정도 되지만 `@ts-expect-error`는 아주 무딘 도구다 - 어느 에러를 기대하는지 지정할 수 없다. 위 코드는 map이 any여도 통과한다(함수 매개변수에 암시적 any 에러가 나므로). 여러 줄로 쪼개 지시어의 범위를 좁히는 것이 한 우회책이다.

## 3. 표준 도구 ① - 타입 시스템 안에서: expect-type

직접 테스트 시스템을 만들지 말고 라이브러리를 쓰자. 타입 시스템 안에서 동작하는 인기 선택지가 expect-type이다(vitest에도 번들되어 있다).

```typescript
import {expectTypeOf} from 'expect-type';

const beatles = ['john', 'paul', 'george', 'ringo'];
expectTypeOf(map(
  beatles,
  function(name, i, array) {
    expectTypeOf(name).toEqualTypeOf<string>();
    expectTypeOf(i).toEqualTypeOf<number>();
    expectTypeOf(array).toEqualTypeOf<string[]>();
    expectTypeOf(this).toEqualTypeOf<string[]>();
    return name.length;
  }
)).toEqualTypeOf<number[]>();
```

any 타입, 다른 함수 타입, readonly 같은 미묘한 차이까지 잡는다. 장점: 추가 도구가 필요 없고(tsc로 끝), 구조적으로 테스트하므로 `1|2` vs `2|1` 같은 무의미한 차이에 안 걸리며, 언어 서비스의 리팩터링(이름 변경 등)이 단언에도 적용되고, prettier 같은 포매터의 혜택도 받는다. 단점: 불일치 에러 메시지(`'MISMATCH'`)가 어디가 어떻게 다른지 알려 주지 않고, 구조를 테스트하므로 **타입이 어떻게 표시되는지**의 문제는 감지할 수 없다(표시는 Item 56).

Type Challenges 저장소가 유행시킨 접근도 이 계열이다.

```typescript
export type Equals<X, Y> =
  (<T>() => T extends X ? 1 : 2) extends
  (<T>() => T extends Y ? 1 : 2) ? true : false;
export type Expect<T extends true> = T;

const double = (x: number) => 2 * x;
type Test1 = Expect<Equals<typeof double, (x: number) => number>>;
type Test2 = Expect<Equals<typeof double, (x: string) => number>>;
//   ~~~~~ Type 'false' does not satisfy the constraint 'true'.
```

첫 조건부 타입이 둘째에 확실히 할당 가능하려면 X와 Y가 같아야만 한다 - 타입스크립트 자신에게 타입 동등성을 비교시키는 드문 경우다. expect-type보다 약간 견고하지만 장단점은 비슷하고, 타입 동등성이라는 개념 자체가 타입스크립트에서 워낙 드물어 의미가 좀 흐릿하다(`Equals<{x: 1} & {y: 2}, {x: 1, y: 2}>`가 false로 나오는 등).

## 4. 표준 도구 ② - 외부 도구: dtslint, eslint-plugin-expect-type

**dtslint**는 DefinitelyTyped의 타입 선언 테스트용으로 만들어졌고 특수 형식의 주석으로 동작한다.

```typescript
map(beatles, function(
  name,   // $ExpectType string
  i,      // $ExpectType number
  array   // $ExpectType string[]
) {
  this;   // $ExpectType string[]
  return name.length;
});  // $ExpectType number[]
```

할당 가능성이 아니라 각 심벌의 타입을 **텍스트로 비교**한다 - 편집기에서 수동으로 확인하는 과정을 자동화한 것이다. 근본적으로 같은 타입인 `number|string`과 `string|number`가 텍스트상 다르다는 단점이 있지만, `string`과 `any`도 (서로 할당 가능함에도) 다르다는 것이 사실 요점이다.

**eslint-plugin-expect-type**은 같은 방식의 ESLint 플러그인으로, DefinitelyTyped가 아닌 내 코드의 타입 테스트에 더 편하다. `$ExpectType` 주석에 더해 Twoslash 스타일 주석도 검사한다.

```typescript
const spiceGirls = ['scary', 'sporty', 'baby', 'ginger', 'posh'];
//    ^? const spiceGirls: string[]
```

익숙할 것이다 - 이 책의 코드 예제(그리고 이 노트!)에 쓰이는 바로 그 문법이다. 외부 도구의 장점: 편집기에서 타입과 상호작용하는 방식과 일치하고, 타입의 문자열 표현을 테스트하므로 **표시 문제를 잡을 수 있으며**(Item 56), ESLint 플러그인의 자동 수정으로 테스트 갱신이 쉽다. 단점: 도구를 하나 더 설정해야 하고, 지나치게 예민할 수 있으며(`1|2` ≠ `2|1`), 타입이 주석 안에 있어 포매팅·리팩터링에서 소외된다.

tsd처럼 타입 시스템 안에서 동작하면서 외부 도구로 더 엄격한 검사를 보태는 하이브리드도 있다. 마지막으로 어느 도구도 못 돕는 것도 있다 - `type Game = 'wordle' | 'crossword' | (string & {})` 같은 "자동완성은 주되 아무 문자열이나 허용" 트릭이 기대대로 동작하는지는 두 접근 모두 테스트할 수 없다.

> **핵심 통찰**: 타입 선언 테스트는 까다롭지만 해야 한다. 직접 타입 테스트 시스템을 굴리지 마라 - DefinitelyTyped에는 dtslint(그곳의 표준), 내 코드에는 vitest·expect-type·tsd 또는 Type Challenges 접근, 타입의 표시까지 테스트하려면 eslint-plugin-expect-type.

## 기억해야 할 것들

- 타입을 테스트할 때 동등성과 할당 가능성의 차이를 인지하라. 특히 함수 타입에서.
- 콜백을 쓰는 함수는 콜백 매개변수의 추론 타입을 테스트하라. API의 일부라면 `this`의 타입도 잊지 말 것.
- 타입 테스트 코드를 직접 만들지 말고 표준 도구를 사용하라.
- DefinitelyTyped 코드에는 dtslint를, 내 코드에는 vitest·expect-type·Type Challenges 접근을, 타입 표시까지 테스트하려면 eslint-plugin-expect-type을 사용하라.
