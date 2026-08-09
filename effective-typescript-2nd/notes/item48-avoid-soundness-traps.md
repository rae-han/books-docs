# Item 48: 건전성 함정 피하기 (Avoid Soundness Traps)

## 핵심 질문

any를 다 없애도 정적 타입과 런타임 값이 어긋날 수 있는 지점은 어디인가? 타입스크립트는 왜 건전성을 목표로 하지 않는가?

인터넷에 오래 머물다 보면 타입스크립트가 "건전하지 않다(not sound)"며 나쁜 언어라는 불평을 듣게 된다. 이 아이템은 그 말이 무슨 뜻인지, 그리고 타입스크립트의 흔한 불건전성 원천들을 안내한다. (안심하라, 타입스크립트는 훌륭한 언어다. 그리고 인터넷의 말을 듣는 것은 결코 좋은 생각이 아니다!)

**모든 심벌의 정적 타입이 런타임 값과 호환됨이 보장**될 때 언어가 건전(sound)하다고 한다. Item 7의 용어로, 모든 심벌의 런타임 값이 그 정적 타입의 도메인 안에 남아 있다는 뜻이다.

```typescript
const x = Math.random();
//    ^? const x: number   — 건전하다. 런타임 값이 뭐든 number다
```

더 정밀한 타입은 반개구간 [0, 1)이겠지만 타입스크립트는 표현할 수 없고, number면 충분하다 — **건전성은 정밀도가 아니라 정확도의 문제**다. 불건전의 예:

```typescript
const xs = [0, 1, 2];
//    ^? const xs: number[]
const x = xs[3];
//    ^? const x: number   — 런타임 값은 undefined!
console.log(x.toFixed(1));
// TypeError: Cannot read properties of undefined (reading 'toFixed')
```

건전성에는 트레이드오프가 있다. 표현력이 낮은 타입 시스템일수록 건전성 달성이 쉽다 — 제네릭이 없는 타입스크립트라면 아래 불건전 원천 다수가 사라지겠지만, 자바스크립트 패턴을 모델링하기 어려워지고 잡는 버그도 줄어든다. **표현력·건전성·편의성 사이에 트레이드오프가 있고**, 타입스크립트는 스펙트럼 위의 위치를 어느 정도 선택하게 해 준다(`strictNullChecks`처럼). 전체적으로 타입스크립트는 단연코 건전하지 않으며, 애초에 건전성은 설계 목표가 아니다 — 편의성과 기존 자바스크립트 라이브러리와의 협업을 우선한다. 그래도 불건전성은 크래시·버그·데이터 손상으로 이어질 수 있으니 피할 수 있으면 피해야 한다. 주요 함정들을 보자.

## 1. any

any를 얹으면 무엇이든 통과다. 해법은 단순하다 — any 사용을 제한하거나, 아예 쓰지 마라. 스코프를 좁히고(Item 43), 가능하면 unknown을 쓰고(Item 46), any를 반환하는 `JSON.parse` 같은 내장은 선언 병합으로 고쳐라(Item 71).

```typescript
function logNumber(x: number) {
  console.log(x.toFixed(1));  // x는 런타임에 string!
}
const num: any = 'forty two';
logNumber(num);  // 에러 없음, 런타임 폭발
```

## 2. 타입 단언

any의 조금 덜 불쾌한 사촌. 많은 단언은 조건문으로 대체할 수 있다.

```typescript
const hour = (new Date()).getHours() || null;
//    ^? const hour: number | null
logNumber(hour as number);  // 타입 체크 통과, 런타임에 터질 수 있음

if (hour !== null) {
  logNumber(hour);  // OK — 좁히기로 단언이 불필요해짐
}
```

단언은 입력 검증 맥락에서 자주 나온다. 타입과 런타임 검증 로직을 동기화하는 체계적 접근을 채택하는 것이 좋다(Item 74).

## 3. 객체·배열 조회

strict 모드에서도 타입스크립트는 배열 조회의 **경계 검사를 전혀 하지 않는다.** 인덱스 타입 객체의 속성 참조도 마찬가지다.

```typescript
type IdToName = { [id: string]: string };
const ids: IdToName = {'007': 'James Bond'};
const agent = ids['008'];  // 런타임에 undefined
//    ^? const agent: string
```

왜 허용하나? 극도로 흔한 코드인 데다 특정 인덱스/배열 접근의 유효성을 증명하기가 몹시 어렵기 때문이다. 시도하게 하고 싶다면 `noUncheckedIndexedAccess` 옵션이 있다 — 위 에러를 잡아 주지만 완벽히 유효한 코드에도 에러를 낸다. 건전성-편의성 스펙트럼의 다른 지점으로 옮기는 것이다. 이 옵션은 그래도 흔한 배열 구문(for-of, map)은 이해할 만큼 똑똑하다.

특정 배열·객체의 접근만 걱정된다면 값 타입에 명시적으로 `undefined`를 더할 수 있다 — 옵션보다 범위(그리고 거짓 양성)를 제한할 수 있지만 옵션의 똑똑함이 없고(for-of에서도 에러) 배열에 undefined를 push할 가능성도 생긴다. 마지막으로, 이런 조회 자체를 줄이도록 코드를 고칠 수도 있다 — 인덱스나 키를 함수에 넘기지 말고 그것이 가리키는 객체를 직접 다뤄라.

## 4. 부정확한 타입 정의

자바스크립트 라이브러리의 타입 선언은 **거대한 타입 단언**과 같다 — 라이브러리의 런타임 동작을 정적으로 모델링한다고 주장하지만 보장하는 것은 없다. 유명한 역사적 사례가 `@types/react`의 `React.FC` 정의였다(논리적으로 말이 안 되는데도 UI 컴포넌트가 children을 받게 만들었다). 최선의 대응은 버그를 고치는 것 — DefinitelyTyped의 처리 시간은 보통 일주일 이내다. 안 되면 보강이나 최악의 경우 단언으로 우회한다.

정적으로 모델링하기가 정말 어려운 함수들도 있다. `String.prototype.replace`의 콜백 매개변수를 보라 — `offset` 매개변수의 위치가 정규식의 캡처 그룹 수에 따라 달라지는데, 정규식 리터럴 타입 개념이 없으니 콜백 매개변수는 any가 된다. `Object.assign`처럼 역사적 이유로 잘못 타이핑된 함수도 있다(수정은 Item 71).

## 5. 클래스 계층의 이변성(bivariance)

함수 타입의 할당 가능성은 반환 타입과 매개변수 타입에서 다르게 동작한다.

- **반환 타입은 공변(covariant)**: number를 기대하는데 string도 반환할 수 있는 함수를 할당하면 안 된다.
- **매개변수 타입은 반변(contravariant)**: `number|string`을 기대하는 함수에 boolean까지 받는 타입은 할당 가능하지만, 그 역은 안 된다.

그런데 클래스에 적용하면:

```typescript
class Parent {
  foo(x: number | string) {}
  bar(x: number) {}
}
class Child extends Parent {
  foo(x: number) {}           // OK?! (반변이라면 에러여야 함)
  bar(x: number | string) {}  // OK
}
```

타입스크립트는 클래스의 **메서드**를 이변(bivariant)으로 모델링한다 — 부모와 자식 중 어느 쪽이든 서로 할당 가능하면 유효로 친다. 이를 악용하면 감지되지 않는 예외를 만들 수 있다.

```typescript
class FooChild extends Parent {
  foo(x: number) {
    console.log(x.toFixed());
  }
}
const p: Parent = new FooChild();
p.foo('string');  // 타입 에러 없음, 런타임 크래시
```

역사적으로 모든 함수 할당이 이렇게 모델링됐지만, 2017년의 `strictFunctionTypes` 이후 독립 함수 타입은 더 정확하게 처리된다. 실무적 교훈: **클래스를 상속할 때 메서드 시그니처를 정확히 맞춰라.** 보통 자식은 부모와 정확히 같은 메서드 시그니처를 가져야 한다. 부모의 시그니처를 바꾸면 자식 구현들에서 타입 에러가 날 거라 기대하지 마라 — 계층의 메서드 시그니처를 바꿀 때는 부모·자식 클래스의 같은 메서드를 확인하라.

## 6. 객체·배열 가변성(variance)의 부정확한 모델

온라인에서 널리 논의된 문제다. 표준 예제:

```typescript
function addFoxOrHen(animals: Animal[]) {
  animals.push(Math.random() > 0.5 ? new Fox() : new Hen());
}
const henhouse: Hen[] = [new Hen()];
addFoxOrHen(henhouse);  // 이런, 닭장에 여우가!
```

`Hen[]`을 `Animal[]`에 할당하는 것은 **배열을 수정하지 않을 때만** 안전하다 — 즉 `readonly Hen[]`만 `readonly Animal[]`에 할당 가능해야 한다. 하지만 readonly가 없던 초기에 이런 코드를 허용하기로 했다. 대응: **함수 매개변수를 변경하지 말고, readonly 구문으로 강제하라**(Item 14).

```typescript
function addFoxOrHen(animals: readonly Animal[]) {
  animals.push(Math.random() > 0.5 ? new Fox() : new Hen());
  //      ~~~~ Property 'push' does not exist on type 'readonly Animal[]'.
}
```

배열에 추가하는 대신 반환하도록 고치면 문제를 통째로 피할 수 있다.

```typescript
function foxOrHen(): Animal {
  return Math.random() > 0.5 ? new Fox() : new Hen();
}
const henhouse: Hen[] = [new Hen(), foxOrHen()];
//                                  ~~~~~~~~~~ 에러, 만세! 닭들이 안전하다.
```

## 7. 함수 호출은 정제를 무효화하지 않는다

```typescript
interface FunFact {
  fact: string;
  author?: string;
}
function processFact(fact: FunFact, processor: (fact: FunFact) => void) {
  if (fact.author) {
    processor(fact);
    console.log(fact.author.blink());  // OK로 통과하지만…
  }
}

processFact(
  {fact: 'Peanuts are not actually nuts', author: 'Botanists'},
  f => delete f.author
);
// 타입 체크 통과, 런타임: Cannot read property 'blink' of undefined
```

`if (fact.author)`는 타입을 `string`으로 정제한다 — 건전하다. 하지만 `processor(fact)` 호출이 이 정제를 무효화**해야** 한다. 콜백이 무슨 짓을 할지 타입스크립트가 알 수 없으니까. 그런데도 허용하는 이유는 대부분의 함수가 매개변수를 변경하지 않고 이런 패턴이 자바스크립트에서 흔하기 때문이다(Item 23에서도 봤다). 대응은 역시 — **함수 매개변수를 변경하지 마라.** 콜백에 `Readonly` 버전을 넘겨 강제할 수 있다(Item 14).

## 8. 할당 가능성과 옵셔널 속성

타입스크립트의 객체 타입은 "봉인"되어 있지 않다(Item 4). 옵셔널 속성과 결합하면 불건전으로 이어질 수 있다.

```typescript
interface Person {
  name: string;
}
interface PossiblyAgedPerson extends Person {
  age?: number;
}
const p1 = { name: "Serena", age: "42 years" };
const p2: Person = p1;               // OK — 추가 속성은 구조적으로 허용
const p3: PossiblyAgedPerson = p2;   // OK?! — 여기서 건전성을 잃는다
console.log(`${p3.name} is ${p3.age?.toFixed(1)} years old.`);
// 런타임 크래시 — age는 string인데 number?로 보인다
```

p1→p2 할당은 잉여 속성 체크를 우회하며(중간 변수, Item 11), 구조적으로 건전하다. p2→p3에서 문제가 생긴다 — 타입이 봉인되어 있다면 `Person`에 age가 없을 테니 괜찮겠지만, 실제로는 옵셔널 속성의 타입과 **호환되지 않는 추가 속성**이 있을 수 있다. 이 문제를 만난다면 지나치게 일반적인 속성 이름(예: `type`)의 충돌 때문일 가능성이 있다 — 더 구체적인 이름을 골라라(`ageInYears`·`ageFormatted`였다면 예방됐을 것이다). 옵셔널 속성을 신중히 쓸 또 하나의 이유다(Item 37).

> **핵심 통찰**: 불건전성은 언어의 결함이 아니라 편의성·표현력·안전성 스펙트럼에서 타입스크립트가 선 위치의 반영이다. 다른 지점으로 가고 싶다면 손잡이가 있고(`strictNullChecks`, `noUncheckedIndexedAccess`), 아니라면 불건전으로 이어지는 흔한 패턴을 알고 피하라.

## 기억해야 할 것들

- "불건전성"은 심벌의 런타임 값이 정적 타입에서 벗어나는 것이다. 타입 에러 없이 크래시 등 나쁜 동작으로 이어질 수 있다.
- 불건전성이 생기는 흔한 경로를 알아 두라: any 타입, 타입 단언(as·is), 객체·배열 조회, 부정확한 타입 정의.
- 함수 매개변수의 변경은 불건전으로 이어질 수 있으니 피하라. 변경할 의도가 없다면 읽기 전용으로 표시하라.
- 자식 클래스가 부모의 메서드 선언과 일치하게 하라.
- 옵셔널 속성이 불건전한 타입으로 이어질 수 있음을 알아 두라.
