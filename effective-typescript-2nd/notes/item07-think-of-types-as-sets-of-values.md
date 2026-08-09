# Item 7: 타입을 값들의 집합으로 생각하기 (Think of Types as Sets of Values)

## 핵심 질문

"할당 가능(assignable)"·"extends"·"서브타입"이라는 말은 정확히 무엇을 뜻하는가? 타입 연산(`|`·`&`·`keyof`)의 결과를 어떻게 예측하는가?

런타임에 모든 변수는 자바스크립트 값의 우주에서 뽑은 **하나의 값**을 갖는다(`42`, `null`, `'Canada'`, `/regex/`, `(x, y) => x + y`, …). 하지만 코드가 실행되기 전, 타입스크립트가 에러를 체크하는 시점에 변수는 **타입**을 갖는다. 타입은 **가능한 값들의 집합**으로 생각하는 것이 가장 좋다. 이 집합을 타입의 도메인(*domain - 타입에 속하는 값들의 집합. 이 아이템에서 타입 자체와 구분해 부르기 위한 용어*)이라 부른다. `number` 타입은 모든 숫자 값의 집합이다 - `42`와 `-37.25`는 속하고 `'Canada'`는 속하지 않는다. `strictNullChecks`에 따라 `null`과 `undefined`는 집합에 속할 수도, 아닐 수도 있다.

## 1. 작은 집합부터: never, 리터럴, 유니온

가장 작은 집합은 아무 값도 없는 **공집합**으로, 타입스크립트의 `never` 타입이 이에 해당한다. 도메인이 비어 있으므로 어떤 값도 할당할 수 없다.

```typescript
const x: never = 12;
//    ~ Type 'number' is not assignable to type 'never'.
```

타입 계층의 맨 아래에 있어서 `never`를 바텀 타입(bottom type)이라고도 부른다.

그다음으로 작은 집합은 값 하나짜리 집합, 타입스크립트의 리터럴 타입(*literal type - 값 하나만을 도메인으로 갖는 타입. 다른 언어에서는 unit type이라고도 함*)이다.

```typescript
type A = 'A';
type B = 'B';
type Twelve = 12;
```

값 두세 개짜리 타입은 리터럴 타입을 **유니온**하면 된다. 유니온 타입의 도메인은 구성 타입 도메인들의 합집합이다 - "유니온 타입"의 "유니온"이 가리키는 것이 바로 이것이다.

```typescript
type AB = 'A' | 'B';
type AB12 = 'A' | 'B' | 12;
```

## 2. "할당 가능"의 의미 - 원소이거나, 부분집합이거나

타입스크립트 에러에 수없이 등장하는 "assignable"은 집합의 언어로 두 가지 중 하나다: **원소(∈)** (값↔타입 관계) 또는 **부분집합(⊆)** (타입↔타입 관계).

```typescript
const a: AB = 'A';  // OK - 값 'A'는 집합 {'A', 'B'}의 원소
const c: AB = 'C';
//    ~ Type '"C"' is not assignable to type 'AB'
```

`"C"`는 리터럴 타입으로 도메인이 `"C"` 하나인데, `AB`의 도메인(`"A"`, `"B"`)의 부분집합이 아니므로 에러다. **타입 체커가 하는 일의 상당 부분은 결국 한 집합이 다른 집합의 부분집합인지 검사하는 것이다.**

```typescript
const ab: AB = Math.random() < 0.5 ? 'A' : 'B';  // OK - {"A","B"} ⊆ {"A","B"}
const ab12: AB12 = ab;                           // OK - {"A","B"} ⊆ {"A","B",12}

declare let twelve: AB12;
const back: AB = twelve;
//    ~~~~ Type 'AB12' is not assignable to type 'AB'
//         Type '12' is not assignable to type 'AB'
```

## 3. 무한 집합 다루기 - 인터페이스는 "값의 묘사"다

실무에서 쓰는 타입 대부분은 도메인이 무한하다. 원소를 나열하는 대신 **구성원의 조건을 서술**한다고 생각하면 된다.

```typescript
interface Identified {
  id: string;
}
```

이 인터페이스는 도메인에 속하는 값들의 묘사다: "값이 객체인가? `string`에 할당 가능한 `id` 속성이 있는가? 그렇다면 `Identified`다." **그게 전부다.** Item 4의 구조적 타이핑 규칙대로 값은 다른 속성을 더 가질 수 있고, 심지어 호출 가능할 수도 있다. (이 사실은 잉여 속성 체크 때문에 가려질 때가 있다 - Item 11.)

이 관점은 타입 연산의 결과를 추론하는 데 힘을 발휘한다.

```typescript
interface Person {
  name: string;
}
interface Lifespan {
  birth: Date;
  death?: Date;
}
type PersonSpan = Person & Lifespan;
```

`&`는 두 타입의 **교집합**을 계산한다. `Person`과 `Lifespan`은 공통 속성이 없으니 `PersonSpan`이 공집합(`never`)일 것 같지만, **타입 연산은 인터페이스의 속성이 아니라 값의 집합(도메인)에 적용된다**. 추가 속성을 가진 값도 여전히 타입에 속하므로, `Person`의 속성과 `Lifespan`의 속성을 **모두** 가진 값이 교집합에 속한다.

```typescript
const ps: PersonSpan = {
  name: 'Alan Turing',
  birth: new Date('1912/06/23'),
  death: new Date('1954/06/07'),
};  // OK
```

일반 규칙: **인터섹션 타입의 값은 구성 타입 각각의 속성의 합집합을 가진다.** "속성이 교차한다"는 직관은 인터섹션이 아니라 두 인터페이스의 **유니온**에 들어맞는다.

```typescript
type K = keyof (Person | Lifespan);
//   ^? type K = never
```

유니온 타입의 값에 반드시 존재한다고 확신할 수 있는 키는 없으므로 유니온의 `keyof`는 공집합이다. 형식으로 쓰면 (타입스크립트 코드가 아니라 관계식이다):

```
keyof (A&B) = (keyof A) | (keyof B)
keyof (A|B) = (keyof A) & (keyof B)
```

이 등식이 왜 성립하는지 직관을 세울 수 있다면 타입스크립트의 타입 시스템 이해에 큰 진전을 이룬 것이다.

## 4. extends = 부분집합

`PersonSpan`을 더 관용적으로 쓰면 `extends`다.

```typescript
interface Person {
  name: string;
}
interface PersonSpan extends Person {
  birth: Date;
  death?: Date;
}
```

집합의 관점에서 `extends`는 "할당 가능"과 마찬가지로 **"~의 부분집합"** 으로 읽으면 된다. `PersonSpan`의 모든 값은 `name`을 갖고 `birth`도 가져야 하므로 진부분집합이다.

`extends`는 보통 필드 추가에 쓰이지만, 기반 타입 값의 부분집합이기만 하면 무엇이든 된다 - 속성 타입을 **좁히는** 것도 가능하다.

```typescript
interface NullyStudent {
  name: string;
  ageYears: number | null;
}
interface Student extends NullyStudent {
  ageYears: number;   // OK - number ⊆ number | null
}
interface StringyStudent extends NullyStudent {
  //      ~~~~~~~~~~~~~~ Interface 'StringyStudent' incorrectly
  //                     extends interface 'NullyStudent'
  ageYears: number | string;  // 넓히는 것은 불가
}
```

"서브타입"이라는 용어도 한 타입의 도메인이 다른 타입의 도메인의 부분집합이라는 말의 다른 표현일 뿐이다. `Vector3D`는 `Vector2D`의 서브타입이고, `Vector2D`는 `Vector1D`의 서브타입이다. 이 관계는 보통 계층도로 그리지만 값의 집합으로 보면 **벤 다이어그램이 더 적절**하며, `extends` 없이 속성을 풀어 써도 집합은 그대로이므로 관계도 변하지 않는다.

```typescript
interface Vector1D { x: number; }
interface Vector2D { x: number; y: number; }
interface Vector3D { x: number; y: number; z: number; }
// Vector3D ⊂ Vector2D ⊂ Vector1D - extends로 썼을 때와 동일
```

제네릭 타입의 제약(constraint)으로 나오는 `extends`도 같은 뜻이다(Item 15).

```typescript
function getKey<K extends string>(val: any, key: K) {
  // ...
}

getKey({}, 'x');                                  // OK - 'x' ⊆ string
getKey({}, Math.random() < 0.5 ? 'a' : 'b');      // OK - 'a'|'b' ⊆ string
getKey({}, document.title);                       // OK - string ⊆ string
getKey({}, 12);
//         ~~ Type 'number' is not assignable to parameter of type 'string'
```

"`string`을 상속한다"를 객체 상속으로 해석하려 하면 난감하지만, 집합으로 보면 자명하다 - 도메인이 `string`의 부분집합인 타입(문자열 리터럴, 리터럴 유니온, 템플릿 리터럴 타입(Item 54), `string` 자신)이면 된다. 마지막 에러에서 "extends"가 "assignable"로 바뀌었지만 둘 다 "부분집합"으로 읽으면 흔들릴 일이 없다.

## 5. 엄격한 계층이 아니라 겹치는 집합

집합 해석은 **계층으로 표현되지 않는 타입 관계**에서 더 빛난다. `string | number`와 `string | Date`의 관계는? 교집합(`string`)이 비어 있지 않지만 어느 쪽도 서로의 서브타입이 아니다. 엄격한 계층에는 안 들어가도 도메인 간의 관계는 명확하다.

배열과 튜플의 관계도 명쾌해진다.

```typescript
const list = [1, 2];
//    ^? const list: number[]
const tuple: [number, number] = list;
//    ~~~~~ Type 'number[]' is not assignable to type '[number, number]'
//          Target requires 2 element(s) but source may have fewer
```

숫자 쌍이 아닌 숫자 리스트(빈 리스트, `[1]`)가 존재하므로 `number[]`는 `[number, number]`의 부분집합이 아니다(역방향 할당은 된다). 그럼 트리플은 페어에 할당될까? 구조적 타이핑으로 생각하면 될 것 같지만 답은 "안 된다"다.

```typescript
const triple: [number, number, number] = [1, 2, 3];
const double: [number, number] = triple;
//    ~~~~~~ '[number, number, number]' is not assignable to '[number, number]'
//           Source has 3 element(s) but target allows only 2.
```

타입스크립트가 숫자 쌍을 `{0: number, 1: number}`가 아니라 `{0: number, 1: number, length: 2}`로 모델링하기 때문이다. 튜플의 길이를 체크할 수 있으니 합리적이고, 이 할당을 막아 주니 다행이기도 하다.

타입스크립트는 할당 가능성(부분집합/서브타입 관계)은 끊임없이 검사하지만 **타입의 동등성은 거의 검사하지 않는다**. 이 때문에 타입에 대한 테스트를 쓰기가 까다로운데, Item 55의 주제다. 타입이 값의 집합이라면 같은 집합을 갖는 두 타입은 같은 타입이다 - 실제로 그렇다(아래 단서 하나 제외). 의미가 다른데 우연히 도메인이 같은 경우가 아니라면 같은 타입을 두 번 정의할 이유가 없다.

## 6. 스펙트럼의 반대편, 그리고 대응표

`never`(공집합)의 정반대 극단에 `unknown`이 있다. 도메인이 **자바스크립트의 모든 값**이라 모든 타입이 `unknown`에 할당 가능하고, 계층 꼭대기에 있어 탑 타입(top type)이라 부른다(활용법은 Item 46).

모든 값의 집합이 타입스크립트 타입에 대응하는 것은 아니라는 점도 알아 두자. "모든 정수"의 타입이나 "x와 y만 갖고 다른 속성은 없는 객체"의 타입은 없다. `Exclude`로 타입을 빼는 것도 결과가 올바른 타입스크립트 타입일 때만 동작한다.

```typescript
type T = Exclude<string | Date, string | number>;
//   ^? type T = Date
type NonZeroNums = Exclude<number, 0>;
//   ^? type NonZeroNums = number   (0을 뺀 number라는 타입은 표현 불가)
```

타입스크립트 용어와 집합 용어의 대응:

| 타입스크립트 용어 | 집합 용어 |
|------------------|-----------|
| `never` | ∅ (공집합) |
| 리터럴 타입 | 원소 하나짜리 집합 |
| 값이 T에 할당 가능 | 값 ∈ T (원소) |
| T1이 T2에 할당 가능 | T1 ⊆ T2 (부분집합) |
| T1 extends T2 | T1 ⊆ T2 (부분집합) |
| T1 \| T2 | T1 ∪ T2 (합집합) |
| T1 & T2 | T1 ∩ T2 (교집합) |
| `unknown` | 전체 집합 |

**중요한 단서**: 이 해석은 값을 **불변으로 볼 때** 가장 잘 맞는다. `Lockbox { code: number }`와 `ReadonlyLockbox { readonly code: number }`는 도메인이 정확히 같지만 관찰 가능하게 다르다 - 후자는 `code` 재할당이 에러다. 그래서 이 아이템 제목의 변주로 "타입은 값들의 집합, **그리고 그 값으로 할 수 있는 일들**"이라는 말도 있다. `readonly`는 Item 14에서 다루며, 일반 규칙으로 불변 값으로 일할 때 타입 체커가 더 효과적이다.

> **핵심 통찰**: "assignable" · "extends" · "subtype"은 전부 "부분집합"의 동의어다. 에러 메시지가 어렵게 느껴질 때마다 두 타입의 도메인을 그려 보라 - 타입 체커가 하는 일은 결국 집합의 포함 관계 검사다.

## 기억해야 할 것들

- 타입을 값들의 집합(타입의 도메인)으로 생각하라. 집합은 유한할 수도(`boolean`, 리터럴 타입), 무한할 수도(`number`, `string`) 있다.
- 타입스크립트의 타입은 엄격한 계층이 아니라 겹치는 집합(벤 다이어그램)을 이룬다. 어느 쪽도 서브타입이 아니면서 겹치는 두 타입이 있을 수 있다.
- 타입 선언에 없는 추가 속성을 가진 객체도 그 타입에 속할 수 있음을 기억하라.
- 타입 연산은 집합의 도메인에 적용된다. `A | B`의 도메인은 A와 B 도메인의 합집합이다.
- "extends" · "할당 가능" · "서브타입"을 "부분집합"의 동의어로 생각하라.
