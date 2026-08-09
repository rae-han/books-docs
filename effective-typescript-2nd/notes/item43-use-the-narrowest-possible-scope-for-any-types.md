# Item 43: any 타입은 가능한 한 좁은 스코프로 사용하기 (Use the Narrowest Possible Scope for any Types)

## 핵심 질문

any를 꼭 써야 한다면, 피해를 최소화하는 위치는 어디인가? any는 어떻게 코드베이스로 퍼져 나가는가?

```typescript
declare function getPizza(): Pizza;
function eatSalad(salad: Salad) { /* ... */ }

function eatDinner() {
  const pizza = getPizza();
  eatSalad(pizza);
  //       ~~~~~
  // Argument of type 'Pizza' is not assignable to parameter of type 'Salad'
  pizza.slice();
}
```

이 `eatSalad` 호출이 어째서인지 괜찮다는 것을 안다면, 최선은 타입스크립트도 이해하도록 타입을 조정하는 것이다(파르메산과 레몬을 얹은 루꼴라 피자는 샐러드 비슷하니까!). 그럴 수 없다면 any로 강제할 수 있는데, 방법이 두 가지다.

```typescript
function eatDinner1() {
  const pizza: any = getPizza();  // 이렇게 하지 말 것
  eatSalad(pizza);                // OK
  pizza.slice();                  // 이 호출은 검사되지 않는다!
}

function eatDinner2() {
  const pizza = getPizza();
  eatSalad(pizza as any);         // 이쪽이 낫다
  pizza.slice();                  // 안전하다
}
```

두 번째가 압도적으로 낫다. **any의 스코프가 함수 인수의 표현식 하나로 국한**되어 그 인수·그 줄 밖에는 아무 영향이 없기 때문이다. `eatSalad` 호출 뒤에 `pizza`를 참조하는 코드에서 타입은 여전히 `Pizza`이고 타입 에러도 낼 수 있다. 반면 첫 번째에서는 함수가 끝날 때까지 `pizza`의 타입이 내내 any라서 `pizza.slice()` 호출이 완전히 무검사다 - 오타나 잘못된 매개변수가 통과했다가 런타임에 터진다.

`eatSalad`가 any를 받게 만드는 것도 나빴을 것이다 - `eatDinner` 안에서 `pizza`는 `Pizza`로 남겠지만, 프로그램의 **모든** `eatSalad` 호출에서 이 매개변수의 타입 체크가 사라진다.

## 1. any 반환은 전염된다

`pizza`를 반환하면 판돈이 훨씬 커진다.

```typescript
function eatDinner1() {
  const pizza: any = getPizza();
  eatSalad(pizza);
  pizza.slice();
  return pizza;  // 위험한 피자!
}

function spiceItUp() {
  const pizza = eatDinner1();
  //    ^? const pizza: any
  pizza.addRedPepperFlakes();  // 이 호출도 무검사!
}
```

**any 반환 타입은 "전염성"이 있어서 코드베이스 전체로 퍼질 수 있다.** `eatDinner1`을 고친 결과 `spiceItUp`에 any가 조용히 나타났다. 좁은 스코프의 any를 쓴 `eatDinner2`에서는 일어나지 않았을 일이다.

이것이 반환 타입이 추론 가능해도 **명시적 반환 타입 구문을 고려할 좋은 이유**다 - any 타입이 무심코 "탈출"하는 것을 막아 준다(반환 타입 명시의 장단은 Item 18). 표준 라이브러리에도 any를 반환하는 함수가 몇 있는데, 특히 `JSON.parse`가 그렇다. 상당히 위험하다! 방어법은 Item 71에서.

## 2. @ts-ignore와 @ts-expect-error

틀렸다고 믿는 에러를 억누르는 다른 방법으로 지시어가 있다.

```typescript
function eatDinner2() {
  const pizza = getPizza();
  // @ts-expect-error
  eatSalad(pizza);
  pizza.slice();
}
```

다음 줄의 에러를 침묵시키되 `pizza`의 타입은 바꾸지 않는다. 두 형태 중 **`@ts-expect-error`가 낫다** - 나중에 에러가 사라지면(예: `eatSalad`의 시그니처가 바뀌어서) 타입스크립트가 알려 주므로 지시어를 제거할 수 있다.

한 줄에 명시적으로 국한되므로 이 지시어들은 any처럼 전염되지 않는다. 그래도 너무 기대지는 말 것 - 타입 체커의 항의에는 보통 그럴 만한 이유가 있고, 그다음 줄의 에러가 더 문제적인 것으로 바뀌어도 알 수 없게 되며, 같은 줄에 두 번째 에러가 생기면 영영 모르게 된다.

## 3. 공간적으로 좁히기 - 객체의 속성 하나에만

큰 객체의 속성 하나에서만 타입 에러가 나는 경우도 있다.

```typescript
const config: Config = {
  a: 1,
  b: 2,
  c: {
    key: value
    //   ~~~ Property ... missing in type 'Bar' but required in type 'Foo'
  }
};
```

객체 전체에 `as any`를 두르면 조용해지지만 **다른 속성(a와 b)의 타입 체크까지 꺼진다.** 더 좁은 any가 피해를 제한한다.

```typescript
const config: Config = {
  a: 1,
  b: 2,           // 이 속성들은 여전히 검사된다
  c: {
    key: value as any
  }
};
```

첫 예제가 any의 스코프를 **시간적으로** 제한한 것이라면 이것은 **공간적으로** 제한한 것이다. 목표는 같다 - any를 써야 한다면 부수 피해를 피하도록 스코프를 최대한 줄여라.

> **실무 팁**: typescript-eslint의 recommended-type-checked 프리셋을 채택하면 `no-unsafe-assignment`·`no-unsafe-return` 같은 룰이 any 타입의 확산을 드러내 준다.

## 기억해야 할 것들

- 코드의 다른 곳에서 원치 않게 타입 안전성을 잃지 않도록 any의 사용을 최대한 좁은 스코프로 만들어라.
- 함수에서 any 타입을 절대 반환하지 마라. 그 함수를 호출하는 코드의 타입 안전성이 소리 없이 사라진다.
- 객체 전체 대신 큰 객체의 개별 속성에 `as any`를 사용하라.
