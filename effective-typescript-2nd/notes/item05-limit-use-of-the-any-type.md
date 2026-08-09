# Item 5: any 타입 사용 제한하기 (Limit Use of the any Type)

## 핵심 질문

`any`는 무엇을 대가로 편리함을 주는가? 타입 체커를 끄는 스위치가 감추는 여섯 가지 비용은 무엇인가?

타입스크립트의 타입 시스템은 **점진적(gradual)이고 선택적(optional)이다**. 코드에 조금씩 타입을 추가할 수 있어서 점진적이고(`noImplicitAny`와 함께), 언제든 타입 체커를 끌 수 있어서 선택적이다. 이 두 특성의 열쇠가 `any` 타입이다.

```typescript
let ageInYears: number;
ageInYears = '12';
// ~~~~~~~~ Type 'string' is not assignable to type 'number'.
ageInYears = '12' as any;  // OK
```

에러를 이해하지 못했거나, 타입 체커가 틀렸다고 생각하거나, 타입 선언을 쓰기 귀찮을 때 `any`와 `as any`의 유혹이 찾아온다. 경우에 따라 괜찮을 수도 있지만, `any`는 타입스크립트를 쓰는 이점 대부분을 없애 버린다. 쓰기 전에 최소한 그 위험을 알아야 한다.

## 1. any는 타입 안전성을 없앤다

위 코드에서 `ageInYears`는 `number`로 선언됐지만 `any`는 `string` 할당을 허용한다. 타입 체커는 선언대로 `number`라고 믿으므로(그렇게 말했으니까) 혼돈은 잡히지 않는다.

```typescript
ageInYears += 1;  // OK — 런타임에 ageInYears는 "121"
```

## 2. any는 함수 계약을 깨뜨린다

함수 시그니처는 계약이다 — 호출자가 특정 타입의 입력을 주면 특정 타입의 출력을 낸다는 약속. `any`는 이 계약을 깨고 들어간다.

```typescript
function calculateAge(birthDate: Date): number {
  // ...
}

let birthDate: any = '1990-01-19';
calculateAge(birthDate);  // OK
```

`birthDate`는 `Date`여야 하는데 문자열이 통과했다. 자바스크립트는 암시적 타입 변환에 관대해서 이런 값이 어떤 상황에서는 동작하다가 다른 상황에서 터지는 것이 특히 골칫거리다.

## 3. any 타입에는 언어 서비스가 없다

타입이 있는 심벌에는 자동완성과 문맥 도움말이 제공되지만, `any` 심벌은 알아서 해야 한다. 이름 변경(Rename Symbol) 같은 리팩터링 서비스도 마찬가지다.

```typescript
interface Person {
  first: string;
  last: string;
}
const formatName = (p: Person) => `${p.first} ${p.last}`;
const formatNameAny = (p: any) => `${p.first} ${p.last}`;
```

편집기에서 `Person`의 `first`를 선택해 `firstName`으로 이름을 바꾸면 `formatName`은 함께 바뀌지만 `formatNameAny`는 그대로 남는다 — 조용한 런타임 버그가 된다.

타입스크립트의 모토는 "확장 가능한 자바스크립트(JavaScript that scales)"이고, 그 "확장"의 핵심이 언어 서비스다(Item 6). 언어 서비스를 잃으면 나만이 아니라 그 코드를 다루는 모든 동료의 생산성이 떨어진다.

## 4. any는 리팩터링 시 버그를 감춘다

아이템 선택 콜백을 가진 컴포넌트가 있다고 하자. 아이템 타입을 쓰기 귀찮아서 `any`를 두었다.

```typescript
interface ComponentProps {
  onSelectItem: (item: any) => void;
}

function renderSelector(props: ComponentProps) { /* ... */ }

let selectedId: number = 0;
function handleSelectItem(item: any) {
  selectedId = item.id;
}
renderSelector({onSelectItem: handleSelectItem});
```

나중에 아이템 객체 전체 대신 ID만 넘기도록 시그니처를 바꾼다.

```typescript
interface ComponentProps {
  onSelectItem: (id: number) => void;
}
```

컴포넌트를 수정하면 타입 체크는 전부 통과한다. 승리! …일까? `handleSelectItem`은 `any` 매개변수라서 아이템이 오든 ID가 오든 똑같이 받아들이고, ID에는 `id` 속성이 없으므로 런타임 예외가 난다. 구체적인 타입을 썼다면 타입 체커가 잡았을 버그다.

## 5. any는 타입 설계를 감춘다

애플리케이션 상태처럼 복잡한 객체의 타입 정의는 길어질 수밖에 없고, 수십 개 속성의 타입을 쓰는 대신 `any` 하나로 끝내고 싶어진다. 하지만 좋은 타입 설계는 깨끗하고 올바르고 이해 가능한 코드의 필수 조건이며(Chapter 4), `any` 상태는 타입 설계를 **암묵적으로** 만든다. 설계가 좋은지, 심지어 설계가 무엇인지조차 알 수 없게 된다. 동료에게 리뷰를 요청하면 상태를 어떻게 바꿨는지 동료가 재구성해야 한다. 모두가 볼 수 있게 써 두는 편이 낫다.

## 6. any는 타입 시스템의 신뢰를 무너뜨린다

실수를 저지를 때마다 타입 체커가 잡아 주면 타입 시스템에 대한 확신이 쌓인다. 반대로 런타임에서야 드러나는 타입 에러를 만나면 그 확신이 깎인다. 팀에 타입스크립트를 도입하는 중이라면 동료들이 "타입스크립트가 그만한 가치가 있나"를 의심하게 만들고, 그 미검출 에러의 출처는 대개 `any`다.

`any`가 많은 타입스크립트는 타입 없는 자바스크립트보다 나쁠 수 있다 — 타입 에러도 고쳐야 하고 실제 타입은 여전히 머릿속으로 추적해야 하기 때문이다. 타입이 현실과 일치하면 타입 정보를 머리에 담아 둘 부담에서 해방된다. 타입스크립트가 대신 추적해 준다.

> **핵심 통찰**: `any`는 타입 체커와 언어 서비스를 동시에 끄는 스위치다. 부득이 써야 할 때조차 더 나은 방식과 더 나쁜 방식이 있다 — 피해를 줄이는 법은 Chapter 5(Item 43~49)에서 다룬다.

## 기억해야 할 것들

- `any` 타입은 해당 심벌에 대한 대부분의 타입 체크를 꺼 버린다.
- `any`는 타입 안전성을 없애고, 계약을 깨게 하고, 개발자 경험을 해치고, 리팩터링을 위험하게 만들고, 타입 설계를 감추고, 타입 시스템의 신뢰를 무너뜨린다.
- 가능하다면 `any` 사용을 피하라!
