# Item 50: 제네릭을 타입 간 함수로 생각하기 (Think of Generics as Functions Between Types)

## 핵심 질문

제네릭 타입은 무엇의 타입 수준 등가물인가? 타입 매개변수의 제약·이름·문서는 어떻게 다뤄야 하는가?

Item 15는 타입 연산(extends·매핑된 타입·인덱싱·keyof)으로 관련 타입 간의 반복을 줄이는 법을 보여 줬다. 값의 세계에서 반복 코드를 뽑아내는 핵심 수단이 함수라면, **타입의 세계에서 함수의 등가물이 제네릭 타입**이다. 제네릭 타입은 하나 이상의 타입 매개변수를 받아 구체적인 비제네릭 타입을 만들어 낸다. 함수를 "호출"하듯 제네릭 타입은 "인스턴스화"한다.

내장 `Partial`을 직접 정의해 보면:

```typescript
type MyPartial<T> = {[K in keyof T]?: T[K]};

interface Person {
  name: string;
  age: number;
}
type MyPartPerson = MyPartial<Person>;
//   ^? type MyPartPerson = { name?: string; age?: number; }
```

다른 타입의 모든 속성을 옵셔널화하는 타입 수준 연산을 캡슐화한 것이다 — 함수가 값 하나를 받아 다른 값을 만드는 로직을 캡슐화하는 것과 정확히 유사하다. `Math.cos`의 구현을 몰라도 코사인을 계산한다는 것을 알듯이.

## 1. 타입 수준의 타입 에러 — 그리고 세 가지 대응

타입 매개변수 여러 개짜리도 쓸 수 있다. 내장 `Pick`의 등가물을 시도해 보자.

```typescript
type MyPick<T, K> = {
  [P in K]: T[P]
  //    ~ Type 'K' is not assignable to type 'string | number | symbol'.
  //        ~~~~ Type 'P' cannot be used to index type 'T'.
};
```

타입 수준에서 프로그래밍할 때도 타입스크립트는 똑같은 정적 분석 도구로 할당 가능성 등을 검사한다. 여기서 찾은 문제 둘: ① `K`가 속성 키로 쓸 수 있는 타입(string·number·symbol)을 담고 있다고 믿을 근거가 없다. ② 유효한 키라 해도 `P`로 `T`를 인덱싱할 수 있다고 믿을 근거가 없다.

**대응 ① — 무시한다.** 놀랍게도 꽤 잘 동작한다!

```typescript
// @ts-expect-error (이렇게 하지 말 것!)
type MyPick<T, K> = { [P in K]: T[P] };
type AgeOnly = MyPick<Person, 'age'>;
//   ^? type AgeOnly = { age: number; }
```

타입 에러가 있어도 자바스크립트를 방출하는 것(Item 3)의 타입 수준 버전이라 생각하면 된다. 물론 타입스크립트의 항의가 옳다 — 이 버전은 오류에 취약하다.

```typescript
type FirstNameOnly = MyPick<Person, 'firstName'>;
//   ^? type FirstNameOnly = { firstName: unknown; }
type Flip = MyPick<'age', Person>;
//   ^? type Flip = {}
```

잘못 써도 타입 에러 대신 **틀린 타입이 그냥 반환된다.** 거의 자바스크립트로 프로그래밍하는 기분이다!

**대응 ② — 기대되는 타입과의 인터섹션.**

```typescript
type MyPick<T, K> = { [P in K & PropertyKey]: T[P & keyof T] };
```

`PropertyKey`는 `string | number | symbol`의 내장 별칭이다. 이런 인터섹션은 **`as any`의 타입 수준 등가물** 같은 것이다 — 구현의 에러는 사라지고 올바른 사용은 그대로지만, 잘못된 사용의 결과가 `never`로 나오는 정도의 개선뿐이다. 값의 세계에서 `as any`가 좀처럼 옳지 않듯, 이런 인터섹션도 대개 최선이 아니다.

**대응 ③ — extends로 타입 매개변수 제약.** 함수의 매개변수 타입을 좁혀서 타입 에러를 푸는 것과 정확히 같은 발상이다.

```typescript
type MyPick<T extends object, K extends keyof T> = {[P in K]: T[P]};

type AgeOnly = MyPick<Person, 'age'>;
//   ^? type AgeOnly = { age: number; }
type FirstNameOnly = MyPick<Person, 'firstName'>;
//                                  ~~~~~~~~~~~
// Type '"firstName"' does not satisfy the constraint 'keyof Person'.
type Flip = MyPick<'age', Person>;
//                 ~~~~~ Type 'string' does not satisfy the constraint 'object'.
```

T를 객체 타입으로, K를 T의 키의 서브타입으로 제약하자 문제 둘이 한꺼번에 풀렸다 — 구현의 타입 에러가 사라졌고, 잘못된 인스턴스화에 타입 에러가 난다.

> **참고**: noImplicitAny는 함수 매개변수에 타입 구문을 요구하지만 타입 매개변수에는 그런 것이 없다. 제약을 지정하지 않으면 기본이 `unknown`이라 사용자가 아무 타입이나 넘길 수 있다. 제네릭을 정의할 때 사용자에게 자유를 조금 덜 주고 안전을 조금 더 줄지 고민하라.

## 2. 이름과 문서 — 타입 수준에도 좋은 습관을

함수를 쓸 때 서술적인 매개변수 이름과 TSDoc을 쓰듯 제네릭 타입에도 그래야 한다. 타입 매개변수를 한 글자로 쓰는 관례가 있지만, 한 글자 변수 이름을 경계하듯 경계해야 한다. 네이밍의 일반 원칙: **이름의 길이는 스코프에 비례해야 한다.** `MyPick`처럼 짧은 제네릭에는 T·K로 충분하지만, 타입 매개변수의 스코프가 넓은 긴 정의(제네릭 클래스 등)에는 더 길고 의미 있는 이름이 명료함을 높인다.

제네릭 타입에도 TSDoc을 쓸 수 있고 언어 서비스가 적절한 자리에서 보여 준다. `@param`의 타입 수준 등가물은 `@template`이다.

```typescript
/**
 * Construct a new object type using a subset of the properties of another one
 * (same as the built-in `Pick` type).
 * @template T The original object type
 * @template K The keys to pick, typically a union of string literal types.
 */
type MyPick<T extends object, K extends keyof T> = {
  [P in K]: T[P]
};
```

타입스크립트의 타입은 값의 집합이므로(Item 7) **제네릭 타입은 본질적으로 집합에 작용한다.** 호출 시 매개변수마다 단일 값이 오는 자바스크립트 함수와 크게 다른 점이다 — 제네릭이 **유니온 타입과 어떻게 동작할지 항상 생각해야** 한다(방법은 Item 53). 그리고 값 수준 코드에 테스트를 쓰듯 **타입 수준 코드에도 테스트를 써야 한다**(Item 55).

## 3. 제네릭 함수와 클래스 — 추론까지 얹은 제네릭 타입

함수와 클래스 같은 값 수준 구문에도 타입 매개변수를 붙일 수 있다. `Pick` 제네릭 타입에 대응하는 `pick` 함수:

```typescript
function pick<T extends object, K extends keyof T>(
  obj: T, ...keys: K[]
): Pick<T, K> {
  const picked: Partial<Pick<T, K>> = {};
  for (const k of keys) {
    picked[k] = obj[k];
  }
  return picked as Pick<T, K>;
}

const p: Person = { name: 'Matilda', age: 5.5 };
const age = pick(p, 'age');
//    ^? const age: Pick<Person, "age">
console.log(age);  // { age: 5.5 } 출력
```

괄호 사이를 무시하고 타입만 보면 앞의 `MyPick` 정의와 매우 닮았다. **제네릭 함수는 개념적으로 연관된 제네릭 타입을 정의한다**고 생각할 수 있다. 제네릭 함수의 아름다움은 호출 시 **값으로부터 타입 매개변수가 추론**되는 경우가 많다는 것 — `pick(p, 'age')`라고만 쓰면 되고, 이는 타입을 명시한 것과 정확히 같은 결과를 훨씬 간결하게 낸다. 사용자는 제네릭이나 타입 수준 연산을 쓰고 있다는 것조차 몰라도 되고, 그저 정확하고 정밀한 타입을 누리면 된다(타입 표시를 감추는 법은 Item 56).

클래스도 타입 매개변수를 받고 사용처에서 추론된다.

```typescript
class Box<T> {
  value: T;
  constructor(value: T) {
    this.value = value;
  }
}
const dateBox = new Box(new Date());
//    ^? const dateBox: Box<Date>
```

클래스는 타입과 값을 함께 도입하는 몇 안 되는 구문이다(Item 8). 클래스가 관련 상태를 붙잡아 두는 데 능하듯 **제네릭 클래스는 타입을 붙잡아 두는 좋은 방법**이다 — 타입 매개변수가 생성 시 설정되어 메서드 호출마다 넘길 필요가 없다(추론 지점의 세밀한 통제는 Item 28).

## 4. 고차 함수는? — 고차 종류 타입의 부재

값의 세계에는 함수를 매개변수로 받는 map·filter·reduce 같은 "고차 함수"가 있다. 타입 수준의 등가물은? 집필 시점 기준 **없다.** "타입에 대한 함수에 대한 함수", 이른바 고차 종류 타입(higher-kinded types)이다.

```typescript
type MapValues<T extends object, F> = {
  [K in keyof T]: F<T[K]>;
  //              ~~~~~~~ Type 'F' is not generic.
};
```

좋은 소식은 이것이 제네릭으로 **할 수 있는 일**을 제한하지는 않는다는 것이다 — 표현하는 방식만 제한한다. 이 경우엔 `MapValues` 대신 매핑된 타입을 그 자리에 쓰면 된다. 익명 제네릭 타입 같은 것도 없다.

> **핵심 통찰**: 제네릭 타입은 타입 간 함수로 생각하는 것이 최선이다. 타입 수준은 새롭고 신나지만 여전히 코딩이다 — 값 수준 코드에서 배운 모범 사례(제약 = 매개변수 타입, 서술적 이름, 문서, 테스트)가 전부 그대로 적용된다.

## 기억해야 할 것들

- 제네릭 타입을 타입 간 함수로 생각하라.
- 함수 매개변수를 타입 구문으로 제약하듯, `extends`로 타입 매개변수의 도메인을 제약하라.
- 코드의 가독성을 높이는 타입 매개변수 이름을 고르고 TSDoc을 써라.
- 제네릭 함수와 클래스는 타입 추론이 잘 되는 제네릭 타입을 개념적으로 정의하는 것으로 생각하라.
