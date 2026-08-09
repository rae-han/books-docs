# Item 9: 타입 단언보다 타입 선언 사용하기 (Prefer Type Annotations to Type Assertions)

## 핵심 질문

`: Person`과 `as Person`은 무엇이 다른가? 타입 단언이 정당한 경우는 언제이고, 그때 무엇을 함께 남겨야 하는가?

타입스크립트에서 변수에 값을 할당하며 타입을 부여하는 방법은 두 가지처럼 보인다.

```typescript
interface Person { name: string };

const alice: Person = { name: 'Alice' };
//    ^? const alice: Person
const bob = { name: 'Bob' } as Person;
//    ^? const bob: Person
```

결과는 비슷해 보이지만 실제로는 상당히 다르다. 첫 번째(`alice: Person`)는 변수에 **타입 선언**(타입 구문)을 붙여 값이 그 타입에 부합하는지 검사한다. 두 번째(`as Person`)는 **타입 단언**으로, "타입스크립트가 추론한 타입이 뭐든 내가 더 잘 아니 `Person`으로 해 달라"는 뜻이다.

## 1. 선언은 검사하고, 단언은 침묵시킨다

```typescript
const alice: Person = {};
//    ~~~~~ Property 'name' is missing in type '{}'
//          but required in type 'Person'
const bob = {} as Person;  // 에러 없음
```

타입 선언은 값이 인터페이스에 부합하는지 검증한다. 부합하지 않으니 에러다. 타입 단언은 "내가 더 잘 안다"며 이 에러를 침묵시킨다. 잉여 속성을 지정해도 마찬가지다.

```typescript
const alice: Person = {
  name: 'Alice',
  occupation: 'TypeScript developer'
  // ~~~~~~~~~ Object literal may only specify known properties,
  //           and 'occupation' does not exist in type 'Person'
};
const bob = {
  name: 'Bob',
  occupation: 'JavaScript developer'
} as Person;  // 에러 없음
```

선언되지 않은 속성은 구조적 타이핑 관점에서는 유효하지만(Item 4) 실수인 경우가 많다. 타입스크립트에는 선언된 타입의 객체에서 잉여 속성을 잡아 주는 **잉여 속성 체크**(Item 11)라는 도구가 있는데, 단언을 쓰면 이것도 적용되지 않는다. **추가 안전 검사가 있으므로, 단언을 써야 할 특별한 이유가 없다면 선언을 써라.**

> **참고**: `const bob = <Person>{}` 같은 코드를 볼 수도 있다. 단언의 원래 문법으로 `{} as Person`과 동일하지만, `.tsx` 파일(TypeScript + React)에서 `<Person>`이 시작 태그로 해석되기 때문에 지금은 덜 쓰인다.

## 2. 화살표 함수의 반환 타입에 선언 붙이기

화살표 함수에서는 타입 선언을 쓰기가 까다로울 때가 있다. 이 코드에서 `Person` 인터페이스를 쓰고 싶다면?

```typescript
const people = ['alice', 'bob', 'jan'].map(name => ({name}));
// { name: string; }[]… 원하는 것은 Person[]
```

단언이 문제를 푸는 것처럼 보이지만, 단언의 문제를 그대로 물려받는다.

```typescript
const people = ['alice', 'bob', 'jan'].map(name => ({name} as Person));
// Person[] - 하지만…
const people = ['alice', 'bob', 'jan'].map(name => ({} as Person));
// 에러 없음!
```

화살표 함수 안에 변수를 선언하면 검사는 되지만 원래 코드에 비해 잡음이 상당하다. 더 간결한 방법은 **화살표 함수의 반환 타입을 선언**하는 것이다.

```typescript
const people = ['alice', 'bob', 'jan'].map(
  (name): Person => ({name})
);  // 타입은 Person[]
```

앞의 변수 선언 버전과 동일한 검사를 전부 수행한다. **괄호가 중요하다** - `(name): Person`은 `name`의 타입은 추론하게 두고 반환 타입이 `Person`이라고 명시한다. 반면 `(name: Person)`은 `name`의 타입을 `Person`으로 명시하는 것이라 에러가 난다(함수 매개변수의 타입 추론은 Item 24).

이 경우엔 최종 타입을 변수에 선언하고 할당의 유효성을 검사하게 할 수도 있다.

```typescript
const people: Person[] = ['alice', 'bob', 'jan'].map(name => ({name}));  // OK
```

하지만 함수 호출 체인이 길다면 이름 붙은 타입이 체인 앞쪽에 있는 편이 필요하거나 바람직할 수 있다 - 에러가 발생한 지점 가까이에서 잡히게 해 주기 때문이다.

## 3. 단언이 정당한 경우 - 타입 체커보다 내가 더 알 때

타입 단언이 가장 말이 되는 경우는 **타입 체커가 접근할 수 없는 문맥을 통해 내가 타입을 진짜로 더 잘 알 때**다. 대표적으로 DOM:

```typescript
document.querySelector('#myButton')?.addEventListener('click', e => {
  e.currentTarget
  // ^? (property) Event.currentTarget: EventTarget | null
  // currentTarget은 #myButton이고, 그것은 버튼 요소다
  const button = e.currentTarget as HTMLButtonElement;
  //    ^? const button: HTMLButtonElement
});
```

타입스크립트는 페이지의 DOM에 접근할 수 없으므로 `#myButton`이 버튼 요소인지, 이벤트의 `currentTarget`이 그 버튼인지 알 길이 없다. 타입스크립트가 모르는 정보를 내가 갖고 있으므로 단언이 합리적이다(DOM 타입은 Item 75).

> **실무 팁**: 타입 단언을 쓸 때는 **왜 유효한지 설명하는 주석**을 함께 남겨라. 사람 독자에게 빠진 정보를 제공하고, 나중에 그 단언이 여전히 정당한지 판단하는 데 도움이 된다.

## 4. 널 아님 단언(!)과 옵셔널 체이닝(?.)

변수 타입에 `null`이 포함되어 있는데 문맥상 불가능하다는 것을 안다면 단언으로 `null`을 제거할 수 있다.

```typescript
const elNull = document.getElementById('foo');
//    ^? const elNull: HTMLElement | null
const el = document.getElementById('foo') as HTMLElement;
//    ^? const el: HTMLElement
```

이런 단언은 워낙 흔해서 전용 문법이 있다 - 널 아님 단언(non-null assertion):

```typescript
const el = document.getElementById('foo')!;
//    ^? const el: HTMLElement
```

접두사 `!`는 논리 NOT이지만, **접미사 `!`는 값이 null이 아니라는 타입 단언**이다. `as`보다 나은 점은 타입의 널 아닌 부분을 건드리지 않고 통과시킨다는 것. 그래도 `!`는 다른 단언과 똑같이 신중히 다뤄야 한다 - 컴파일 시 지워지므로, 타입 체커가 모르는 정보로 값이 null이 아님을 **보장할 수 있을 때만** 쓰고, 아니면 조건문으로 null 케이스를 체크해야 한다.

null일 수 있는 객체의 속성·메서드에 접근할 때는 옵셔널 체이닝 `?.`이 편리하다.

```typescript
document.getElementById('foo')?.addEventListener('click', () => {
  alert('Hi there!');
});
```

`!.`와 겉모습이 비슷하지만 전혀 다르다 - `a?.b`는 **런타임에** 객체가 null(또는 undefined)인지 확인하고 진행하는 자바스크립트 구문이고, `a!.b`는 그냥 `a.b`로 컴파일되는 **타입 수준** 구문이라 런타임에 null이면 예외를 던진다. `a?.b`가 더 안전하지만 남용하지는 말 것 - 이벤트 리스너 등록이 앱에 필수적이라면 실패했을 때 알아야 하지 않겠는가!

## 5. 단언의 한계 - "겹치는" 타입 사이에서만

단언으로 임의의 타입 사이를 오갈 수는 없다. 일반 규칙: A와 B가 서로 "비교 가능(comparable)"해야 한다. Item 7의 집합 용어로는 **교집합이 비어 있지 않아야** 한다. 특히 서브타입 관계면 허용된다 - `HTMLElement`는 `HTMLElement | null`의 서브타입, `HTMLButtonElement`는 `EventTarget`의 서브타입, `Person`은 `{}`의 서브타입이라 앞의 단언들은 모두 OK였다.

```typescript
interface Person { name: string; }
const body = document.body;
const el = body as Person;
//         ~~~~~~~~~~~~~~
// Conversion of type 'HTMLElement' to type 'Person' may be a mistake because
// neither type sufficiently overlaps with the other. If this was intentional,
// convert the expression to 'unknown' first.
```

에러 메시지가 탈출구를 알려 준다 - `unknown`(Item 46)을 거치는 것. 모든 타입은 `unknown`의 서브타입이므로 `unknown`이 낀 단언은 항상 허용된다. 임의 타입 간 변환이 가능해지지만, 적어도 **수상한 짓을 하고 있다는 것이 명시**된다.

```typescript
const el = document.body as unknown as Person;  // OK
```

몇 가지 관련 사항:

- **모든 단언이 `as`는 아니다**: Item 22의 사용자 정의 타입 가드(`is`)는 단언에 검증 로직을 결합한 것이다. 제네릭 타입 추론으로 단언하는 것("반환 전용 제네릭")도 가능하지만, 타입스크립트가 검사해 주고 있다고 착각하기 쉬워 나쁜 방법이다(Item 51).
- **"캐스트"라는 말은 피하라**: C 같은 언어의 캐스트는 런타임에 값을 바꿀 수 있지만(int→float), 타입 단언은 런타임에 지워지는 타입 수준 구문이라 값을 바꾸지 못한다. 값에 대해 이미 참인 무언가를 "단언"할 뿐이다.
- **`as const`는 단언이 아니다**: 생김새는 비슷하지만 "const 문맥"이라 부르는 것이 정확하다. `as T`는 의심해야 하지만 `as const`는 타입을 **더 정밀하게** 만들며 완전히 안전하다(Item 24).

## 기억해야 할 것들

- 타입 단언(`as Type`)보다 타입 선언(`: Type`)을 사용하라.
- 화살표 함수의 반환 타입에 선언을 붙이는 법을 알아 두라.
- 타입스크립트가 모르는 것을 내가 알 때만 타입 단언과 널 아님 단언을 사용하라.
- 타입 단언을 쓸 때는 왜 유효한지 설명하는 주석을 남겨라.
