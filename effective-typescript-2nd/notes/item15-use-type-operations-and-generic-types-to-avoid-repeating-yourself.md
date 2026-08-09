# Item 15: 타입 연산과 제네릭 타입으로 반복 줄이기 (Use Type Operations and Generic Types to Avoid Repeating Yourself)

## 핵심 질문

코드의 DRY 원칙을 타입에는 어떻게 적용하는가? "헬퍼 함수 뽑아내기"의 타입 시스템 버전은 무엇인가?

원기둥 몇 개의 치수·표면적·부피를 출력하는 스크립트가 있다.

```typescript
console.log('Cylinder r=1 × h=1',
  'Surface area:', 6.283185 * 1 * 1 + 6.283185 * 1 * 1,
  'Volume:', 3.14159 * 1 * 1 * 1);
console.log('Cylinder r=1 × h=2',
  'Surface area:', 6.283185 * 1 * 1 + 6.283185 * 2 * 1,
  'Volume:', 3.14159 * 1 * 2 * 1);
console.log('Cylinder r=2 × h=1',
  'Surface area:', 6.283185 * 2 * 1 + 6.283185 * 2 * 1,
  'Volume:', 3.14159 * 2 * 2 * 1);
```

보기 불편해야 정상이다. 같은 줄을 복사-붙여넣기해서 수정한 듯 극도로 반복적이고, 값과 상수를 되풀이하다 보니 오류까지 스며들었다(마지막 예의 표면적에 `r*r` 대신 `r*h`가 들어갔다). 함수·상수·루프로 정리하면 버그도 사라진다.

```typescript
type CylinderFn = (r: number, h: number) => number;
const surfaceArea: CylinderFn = (r, h) => 2 * Math.PI * r * (r + h);
const volume: CylinderFn = (r, h) => Math.PI * r * r * h;

for (const [r, h] of [[1, 1], [1, 2], [2, 1]]) {
  console.log(`Cylinder r=${r} × h=${h}`,
    `Surface area: ${surfaceArea(r, h)}`,
    `Volume: ${volume(r, h)}`);
}
```

이것이 DRY(*Don't Repeat Yourself - 반복하지 말라*) 원칙 - 소프트웨어 개발에서 보편적 조언에 가장 가까운 것이다. 그런데 코드의 반복은 성실하게 피하는 개발자들이 **타입의 반복**에는 무심하다.

```typescript
interface Person {
  firstName: string;
  lastName: string;
}
interface PersonWithBirthDate {
  firstName: string;
  lastName: string;
  birth: Date;
}
```

타입 중복은 코드 중복과 같은 문제를 대부분 공유한다 - `Person`에 옵셔널 `middleName`을 추가하면 두 타입은 어긋나기 시작한다. 타입에서 중복이 더 흔한 이유는 공유 패턴을 뽑아내는 메커니즘이 코드보다 덜 익숙하기 때문이다. **타입 간 매핑**을 배우면 타입 정의에도 DRY의 혜택을 가져올 수 있다.

## 1. 기본기 - 이름 붙이기와 extends

가장 단순한 반복 제거는 **타입에 이름 붙이기**다.

```typescript
// 반복
function distance(a: {x: number, y: number}, b: {x: number, y: number}) {
  return Math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2);
}

// 이름 붙이기 - 상수를 뽑아내는 것의 타입 버전
interface Point2D {
  x: number;
  y: number;
}
function distance(a: Point2D, b: Point2D) { /* ... */ }
```

중복 타입은 문법에 가려 안 보일 때도 있다. 여러 함수가 같은 시그니처를 공유한다면 Item 12의 조언대로 이름 붙은 함수 타입을 뽑아낸다.

```typescript
type HTTPFunction = (url: string, opts: Options) => Promise<Response>;
const get: HTTPFunction = (url, opts) => { /* ... */ };
const post: HTTPFunction = (url, opts) => { /* ... */ };
```

`Person`/`PersonWithBirthDate`는 **extends**로 해결한다 - 추가 필드만 쓰면 된다.

```typescript
interface PersonWithBirthDate extends Person {
  birth: Date;
}
```

두 인터페이스가 필드의 부분집합을 공유한다면 공통 필드만 가진 기반 인터페이스를 뽑아낼 수 있다(`Bird`·`Mammal`에서 `Vertebrate`를 뽑아내듯). 기반 속성을 바꾸거나 TSDoc(Item 68)을 달면 양쪽에 반영된다. 코드 중복의 비유로는 `3.141593`과 `6.283185` 대신 `PI`와 `2*PI`를 쓰는 것과 같다. 인터섹션 연산자 `&`로 확장할 수도 있는데(`type PersonWithBirthDate = Person & { birth: Date }`), extends 할 수 없는 **유니온 타입에 속성을 추가**할 때 가장 유용하다(Item 13).

## 2. 반대 방향 - 인덱싱과 매핑된 타입

전체 앱 상태 `State`와 그 일부인 `TopNavState`가 있다면, `TopNavState`를 확장해 `State`를 만들기보다 **`State`의 부분집합으로 `TopNavState`를 정의**하고 싶다. 그래야 전체 상태를 정의하는 인터페이스가 하나로 유지된다.

```typescript
interface State {
  userId: string;
  pageTitle: string;
  recentFiles: string[];
  pageContents: string;
}
```

1단계 - **인덱싱**으로 속성 타입의 중복을 없앤다. `State.pageTitle`의 타입이 바뀌면 반영되지만, 여전히 반복적이다.

```typescript
interface TopNavState {
  userId: State['userId'];
  pageTitle: State['pageTitle'];
  recentFiles: State['recentFiles'];
};
```

2단계 - 매핑된 타입(*mapped type - 키의 유니온을 순회하며 각 키의 값 타입을 조회해 새 타입을 만드는 구문*)이 더 낫다.

```typescript
type TopNavState = {
  [K in 'userId' | 'pageTitle' | 'recentFiles']: State[K]
};
```

마우스를 올려 보면 앞의 정의와 정확히 같다. 매핑된 타입은 **배열 필드를 순회하는 루프의 타입 시스템 버전**이다. 이 패턴은 워낙 흔해서 표준 라이브러리에 `Pick`으로 들어 있다.

```typescript
type Pick<T, K> = { [k in K]: T[k] };  // 완전한 정의는 아님 - Item 50에서 다시
type TopNavState = Pick<State, 'userId' | 'pageTitle' | 'recentFiles'>;
```

`Pick`은 **제네릭 타입**의 예다. 코드 중복 제거의 비유를 이어가면 `Pick`을 쓰는 것은 **함수 호출**에 해당한다 - 함수가 값 두 개를 받아 셋째 값을 반환하듯, `Pick`은 타입 `T`·`K`를 받아 셋째 타입을 반환한다(타입 수준 프로그래밍은 Chapter 6, "타입 간 함수"는 Item 50).

태그된 유니온에서 **태그만의 타입**이 필요할 때도 인덱싱이 답이다.

```typescript
interface SaveAction { type: 'save'; /* ... */ }
interface LoadAction { type: 'load'; /* ... */ }
type Action = SaveAction | LoadAction;

type ActionType = Action['type'];
//   ^? type ActionType = "save" | "load"
```

`Action` 유니온에 타입을 추가하면 `ActionType`이 자동으로 반영한다. `Pick`을 썼다면 결과가 다르다는 것에 주의 - `Pick<Action, 'type'>`은 `{ type: "save" | "load" }`라는 **인터페이스**를 준다.

## 3. keyof, Partial - 옵셔널 버전 만들기

생성 후 갱신이 가능한 클래스에서 `update` 메서드의 매개변수 타입은 생성자 매개변수의 옵셔널 버전이기 십상이다.

```typescript
interface Options {
  width: number;
  height: number;
  color: string;
  label: string;
}
```

`keyof`는 타입을 받아 **키 타입들의 유니온**을 준다.

```typescript
type OptionsKeys = keyof Options;
//   ^? type OptionsKeys = keyof Options
//      ("width" | "height" | "color" | "label"과 동등)
```

매핑된 타입이 이를 순회하며 `?`로 각 속성을 옵셔널로 만든다.

```typescript
type OptionsUpdate = {[k in keyof Options]?: Options[k]};
```

이 패턴도 매우 흔해서 표준 라이브러리에 `Partial`로 들어 있다.

```typescript
class UIWidget {
  constructor(init: Options) { /* ... */ }
  update(options: Partial<Options>) { /* ... */ }
}
```

매핑된 타입의 기교 몇 가지:

- **`as` 절로 키 이름 바꾸기**: 매핑의 키와 값을 뒤집는 데 쓸 수 있다. 템플릿 리터럴 타입(Item 54)과 특히 잘 어울린다.

```typescript
interface ShortToLong {
  q: 'search';
  n: 'numberOfResults';
}
type LongToShort = { [k in keyof ShortToLong as ShortToLong[k]]: k };
//   ^? type LongToShort = { search: "q"; numberOfResults: "n"; }
```

- **동형(homomorphic) 매핑된 타입**: 인덱스 절이 `K in keyof T`(또는 그 변형) 형태면 타입스크립트가 "동형" 매핑으로 취급해서 **한정자(`readonly`·`?`)와 문서 주석이 새 타입으로 전달**된다.

```typescript
interface Customer {
  /** How the customer would like to be addressed. */
  title?: string;
  /** Complete name as entered in the system. */
  readonly name: string;
}

type PickTitle = Pick<Customer, 'title'>;
//   ^? type PickTitle = { title?: string; }
type PickName = Pick<Customer, 'name'>;
//   ^? type PickName = { readonly name: string; }
type ManualName = { [K in 'name']: Customer[K]; };
//   ^? type ManualName = { name: string; }
```

`Pick`은 동형이라 옵셔널·readonly 한정자를 보존하지만, `keyof` 표현식을 쓰지 않은 `ManualName`은 동형이 아니라 한정자를 전달하지 않는다. 동형 매핑의 또 다른 신기한 동작으로, 원시(비객체) 타입은 수정 없이 통과시킨다(`Partial<number>`는 그냥 `number`) - 이상해 보이지만 제네릭 타입을 직접 만들 때 편리하다(Item 56). 매핑된 타입을 정의할 때는 동형인지, 동형이길 원하는지 생각해 보라.

## 4. 값에서 타입 뽑기 - typeof와 ReturnType

값의 형태와 일치하는 타입이 필요하다면 `typeof`를 쓴다.

```typescript
const INIT_OPTIONS = {
  width: 640,
  height: 480,
  color: '#00FF00',
  label: 'VGA',
};
type Options = typeof INIT_OPTIONS;
```

자바스크립트의 런타임 `typeof`를 의도적으로 닮았지만 타입스크립트 타입 수준에서 동작하며 훨씬 정밀하다(Item 8). 다만 **값에서 타입을 끌어내는 것은 신중해야 한다** - 보통은 타입을 먼저 정의하고 값이 그에 할당 가능하다고 선언하는 것이 낫다. 타입이 더 명시적이 되고 넓히기(Item 20)의 변덕에 덜 휘둘린다. `typeof`의 정석 용례는 **어떤 값 하나가 타입의 진실 공급원(source of truth)일 때**다(스키마나 API 명세 같은).

함수·메서드의 추론된 반환값에 이름 붙은 타입을 만들고 싶을 때는 표준 라이브러리의 `ReturnType` 제네릭이 있다.

```typescript
function getUserInfo(userId: string) {
  // ...
  return { userId, name, age, height, weight, favoriteColor };
}

type UserInfo = ReturnType<typeof getUserInfo>;
```

`ReturnType`은 함수의 **값**(`getUserInfo`)이 아니라 함수의 **타입**(`typeof getUserInfo`)에 작용한다는 점에 주의. 이 기법도 진실 공급원이 무엇인지 헷갈리지 않게 분별 있게 쓸 것.

## 5. DRY의 과용 경계 - 우연한 중복은 중복이 아니다

타입의 반복을 걷어내되 도를 넘지는 말 것. 소스 코드에서 같은 글자를 공유한다고 같은 것은 아니다.

```typescript
interface Product {
  id: number;
  name: string;
  priceDollars: number;
}
interface Customer {
  id: number;
  name: string;
  address: string;
}

// 이렇게 하지 말 것!
interface NamedAndIdentified {
  id: number;
  name: string;
}
```

`id`와 `name`이 우연히 같은 이름·타입일 뿐 **같은 것을 가리키지 않는다**. 나중에 한쪽 `id`만 string으로 바꾸거나, 고객의 `name`만 `firstName`/`lastName`으로 쪼갤 수 있다. 공통 기반 인터페이스를 뽑아내는 것은 섣부른 추상화이며 두 타입이 독립적으로 진화하기 어렵게 만든다.

경험칙: **타입(또는 함수)의 이름을 짓기 어렵다면 유용한 추상화가 아닐 수 있다.** `NamedAndIdentified`는 타입이 무엇인지가 아니라 구조만 묘사한다. 반면 앞의 `Vertebrate`는 그 자체로 의미가 있다.

> 중복은 잘못된 추상화보다 훨씬 싸다.<br>- 샌디 메츠(Sandi Metz)

## 기억해야 할 것들

- DRY 원칙은 로직에 적용되는 만큼 타입에도 적용된다.
- 타입을 반복하지 말고 이름을 붙여라. 인터페이스의 필드 반복은 `extends`로 피하라.
- 타입 간 매핑을 위해 타입스크립트가 제공하는 도구를 이해하라: `keyof`, `typeof`, 인덱싱, 매핑된 타입.
- 제네릭 타입은 타입을 위한 함수다. 타입 수준 연산을 반복하는 대신 제네릭으로 타입 간 매핑을 하라.
- `Pick`·`Partial`·`ReturnType` 같은 표준 라이브러리의 제네릭 타입에 익숙해져라.
- DRY의 과용을 피하라: 공유하는 속성과 타입이 정말 같은 것인지 확인하라.
