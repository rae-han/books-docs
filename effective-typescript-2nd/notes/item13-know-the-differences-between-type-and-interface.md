# Item 13: type과 interface의 차이 알기 (Know the Differences Between type and interface)

## 핵심 질문

이름 붙은 타입을 정의하는 두 가지 방법 - `type`과 `interface` - 은 무엇이 같고 무엇이 다른가? 새 코드에서는 무엇을 골라야 하는가?

```typescript
type TState = {
  name: string;
  capital: string;
};

interface IState {
  name: string;
  capital: string;
}
```

(클래스도 쓸 수 있지만, 그건 값도 함께 도입하는 자바스크립트 런타임 개념이다 - Item 8.) 두 방법의 경계는 해를 거듭하며 흐려져서 대부분의 상황에서 어느 쪽을 써도 된다. 남아 있는 차이를 알고 상황별로 일관되게 쓰되, **같은 타입을 두 문법 모두로 쓸 줄 알아야** 어느 쪽을 쓴 코드든 편하게 읽을 수 있다.

> **참고**: 이 아이템의 `I`/`T` 접두사는 어느 문법으로 정의했는지 표시하기 위한 것일 뿐이다. **실제 코드에서 이렇게 쓰면 안 된다!** 인터페이스에 `I`를 붙이는 것은 C#의 관례로 타입스크립트 초기에 일부 유입됐지만, 불필요하고 가치가 없으며 표준 라이브러리에서도 일관되게 따르지 않으므로 오늘날에는 나쁜 스타일로 여겨진다.

## 1. 공통점 - 거의 구별되지 않는다

- **잉여 속성 체크**: 추가 속성을 가진 값을 정의하면 두 타입 모두 글자 하나까지 동일한 에러(Item 11)를 낸다.
- **인덱스 시그니처**: 둘 다 쓸 수 있다.

```typescript
type TDict = { [key: string]: string };
interface IDict {
  [key: string]: string;
}
```

- **함수 타입**: 둘 다 표현할 수 있다.

```typescript
type TFn = (x: number) => string;
interface IFn {
  (x: number): string;
}
type TFnAlt = {
  (x: number): string;
};
```

첫 번째 형태(`TFn`)가 함수 타입으로는 더 자연스럽고 간결해서 선호되는 형태이고 타입 선언에서도 가장 흔히 만난다. 뒤의 두 형태는 자바스크립트의 함수가 호출 가능한 객체라는 사실을 반영하며, 오버로드된 함수 시그니처(Item 52)에서 가끔 유용하다.

- **제네릭**: 둘 다 가능하다 (`type TBox<T> = { value: T }`, `interface IBox<T> { value: T }`).
- **상호 확장**: 인터페이스가 타입을 extends 할 수 있고(단서는 아래), 타입이 인터페이스를 확장(`&`)할 수도 있다.

```typescript
interface IStateWithPop extends TState {
  population: number;
}
type TStateWithPop = IState & { population: number; };
```

두 타입은 동일하다. 단서: 인터페이스는 **interface로 정의할 수 있었을 객체 타입만** extends 할 수 있다(유니온 타입은 불가 - 그때는 `type`과 `&`가 필요하다).

- **클래스 implements**: 둘 다 가능하다.
- **재귀 타입**: 둘 다 가능하다(Item 57).

## 2. type만 할 수 있는 것 - 유니온, 그리고 타입 수준 기능

**유니온 타입은 있지만 유니온 인터페이스는 없다.**

```typescript
type AorB = 'a' | 'b';
```

유니온을 확장하는 것이 유용할 때가 있다. `Input`·`Output` 타입과 이름→변수 매핑이 있을 때, 이름이 붙은 변수 타입은 이렇게만 표현된다.

```typescript
type Input = { /* ... */ };
type Output = { /* ... */ };
interface VariableMap {
  [name: string]: Input | Output;
}

type NamedVariable = (Input | Output) & { name: string };
```

이 타입은 `interface`로 표현할 수 없다. **일반적으로 `type`이 `interface`보다 표현력이 세다** - 유니온이 될 수 있고, 매핑된 타입(Item 15)·조건부 타입(Item 52) 같은 고급 타입 수준 기능도 쓸 수 있다. 튜플·배열 타입도 `type`이 자연스럽다.

```typescript
type Pair = [a: number, b: number];
type StringList = string[];
type NamedNums = [string, ...number[]];
```

한편 **`extends`는 `&`보다 에러 체크를 더 해 준다**.

```typescript
interface Person {
  name: string;
  age: string;
}
type TPerson = Person & { age: number; };  // 에러 없음 - 사용 불가능한 타입
interface IPerson extends Person {
  //      ~~~~~~~ Interface 'IPerson' incorrectly extends interface 'Person'.
  //              Types of property 'age' are incompatible.
  age: number;
}
```

서브타입에서 속성 타입을 바꾸는 것은 기반 타입과 호환될 때만 유효하다(Item 7). `&`는 모순되는 교차(`string & number` = `never`)를 조용히 만들지만 `extends`는 즉시 에러를 낸다. 안전 검사는 많을수록 좋으므로 인터페이스의 `extends`를 쓸 좋은 이유다.

## 3. interface만 할 수 있는 것 - 선언 병합

인터페이스는 **보강(augment)** 될 수 있다.

```typescript
interface IState {
  name: string;
  capital: string;
}
interface IState {
  population: number;
}
const wyoming: IState = {
  name: 'Wyoming',
  capital: 'Cheyenne',
  population: 578_000,
};  // OK
```

이것을 선언 병합(*declaration merging - 같은 이름의 인터페이스 선언들이 하나로 합쳐지는 것*)이라 하며, 처음 보면 꽤 놀랍다. 주로 타입 선언 파일(Chapter 8)에서 쓰이고, 선언 파일을 쓴다면 관례를 따라 `interface`를 써서 병합을 지원해야 한다 - 타입 선언에 사용자가 채워야 할 빈틈이 있을 수 있고, 이것이 그 채우는 방법이기 때문이다(Item 71).

이 특이한 기능의 쓸모는 타입스크립트 자신이 **자바스크립트 표준 라이브러리의 버전별 차이를 모델링하는 방식**에서 잘 드러난다. `Array` 인터페이스는 `lib.es5.d.ts`에 정의되어 있는데, `target: ES2015`로 설정하면 `lib.es2015.core.d.ts`가 추가로 포함되고, 여기에 ES2015에서 추가된 4개 메서드(`find`·`findIndex`·`fill`·`copyWithin`)만 담은 또 하나의 `Array` 선언이 있다. 선언 병합으로 이것들이 ES5 `Array`에 합쳐져서, **타기팅하는 자바스크립트 버전에 딱 맞는 메서드를 가진 단일 `Array` 타입**이 만들어진다.

이름대로 선언 병합은 선언 파일에서 가장 말이 되며, 사용자 코드에서는 두 인터페이스가 **같은 모듈(같은 .ts 파일)** 에 있을 때만 일어난다 - `Location`·`FormData`처럼 흔한 이름의 전역 인터페이스와 우연히 충돌하는 것을 막기 위해서다.

## 4. 이름 유지 vs 인라인 - 표시와 .d.ts에 미치는 영향

또 하나의 차이: 타입스크립트는 **인터페이스는 항상 이름으로 지칭**하려 하지만, **타입 별칭은 기저 정의로 마음껏 대체**한다. 에러 메시지와 타입 표시(Item 56)에서 종종 보이고, `declaration: true` 설정 시 생성되는 `.d.ts` 파일 같은 구체적 산출물에도 영향을 준다.

함수 스코프 안의 타입 별칭으로 반환값을 타이핑한 함수:

```typescript
export function getHummer() {
  type Hummingbird = { name: string; weightGrams: number; };
  const ruby: Hummingbird = { name: 'Ruby-throated', weightGrams: 3.4 };
  return ruby;
};

const rubyThroat = getHummer();
//    ^? const rubyThroat: Hummingbird
```

스코프 밖의 타입 이름으로 표시된다는 것도 흥미롭지만, `.d.ts`를 생성하면 더 흥미롭다 - 타입 별칭을 정의할 함수 본문이 없으므로 타입스크립트는 별칭을 **인라인**한다.

```typescript
// get-hummer.d.ts
export declare function getHummer(): {
  name: string;
  weightGrams: number;
};
```

이름은 사라지고 구조만 남는다. 타입 시스템이 구조적이라(Item 4) 할당 가능한 값에는 영향이 없지만, 표시와 생성 파일에는 영향이 있고, 극단적인 경우 타입 중복이 컴파일러 성능에까지 영향을 줄 수 있다(Item 78). 같은 코드를 `interface`로 쓰면 타입스크립트가 이름으로 지칭하려 하는데 선언 파일에서 그 이름을 쓸 수 없으므로 에러가 난다(`Return type of exported function has or is using private name 'Hummingbird'`). 더 나은 해법은 인터페이스를 유지하되 최상위 export로 만드는 것이다 - Item 67이 설명하듯 타입은 어차피 export하는 것이 좋다.

## 5. 그래서 무엇을 쓸까

- **복잡한 타입**(유니온·매핑·조건부): 선택의 여지 없이 `type`
- **함수·튜플·배열 타입**: `type` 문법이 더 간결하고 자연스럽다
- **둘 다 가능한 단순 객체 타입**: 기존 스타일이 있는 코드베이스라면 그것을 따르라. 스타일이 없는 새 프로젝트라면 **`interface`를 선호**하라 - 에러 메시지와 타입 표시에 이름이 더 일관되게 나타나고, 다른 인터페이스를 올바르게 확장하는지 검사도 더 받는다

공식 타입스크립트 핸드북의 표현:

> For the most part, you can choose based on personal preference, and TypeScript will tell you if it needs something to be the other kind of declaration. If you would like a heuristic, use interface until you need to use features from type.<br>대부분은 개인 취향으로 골라도 되고, 다른 종류의 선언이 필요하면 타입스크립트가 알려 줄 것이다. 휴리스틱을 원한다면, type의 기능이 필요해질 때까지는 interface를 써라.

즉 **가능하면 `interface`, 필요하거나 더 편하면 `type`** - 어느 쪽이든 너무 고민하지는 말 것.

> **실무 팁**: typescript-eslint의 `consistent-type-definitions` 룰(stylistic 프리셋 포함, 기본값 interface 선호)로 일관성을 강제할 수 있다.

## 기억해야 할 것들

- `type`과 `interface`의 차이점과 공통점을 이해하라.
- 같은 타입을 두 문법 모두로 쓸 줄 알아야 한다.
- `interface`의 선언 병합과 `type`의 인라인 동작을 알아 두라.
- 정해진 스타일이 없는 프로젝트라면 객체 타입에는 `type`보다 `interface`를 선호하라.
