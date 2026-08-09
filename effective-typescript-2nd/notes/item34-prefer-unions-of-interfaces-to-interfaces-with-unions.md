# Item 34: 유니온의 인터페이스보다 인터페이스의 유니온 선호하기 (Prefer Unions of Interfaces to Interfaces with Unions)

## 핵심 질문

속성들이 유니온 타입인 인터페이스는 무엇을 감추는가? 속성 간의 관계를 타입 시스템에 어떻게 알려 주는가?

속성이 유니온 타입인 인터페이스를 만들었다면, **더 정밀한 인터페이스들의 유니온이 더 말이 되지 않는지** 물어야 한다.

## 1. 어긋난 조합을 허용하는 타입

벡터 드로잉 프로그램에서 기하 타입별 레이어 인터페이스를 정의한다고 하자.

```typescript
interface Layer {
  layout: FillLayout | LineLayout | PointLayout;
  paint: FillPaint | LinePaint | PointPaint;
}
```

`layout`은 도형이 그려지는 방식과 위치(모서리 둥글게? 직선?)를, `paint`는 스타일(선이 파란가? 굵은가? 점선인가?)을 통제한다. 의도는 `FillLayout`엔 `FillPaint`, `LineLayout`엔 `LinePaint`가 짝이 되는 것이다. 하지만 이 타입은 **`FillLayout`에 `LinePaint`가 붙는 것도 허용**한다. 라이브러리 사용이 오류에 취약해지고 인터페이스를 다루기 어려워진다.

더 나은 모델링은 레이어 종류마다 별도 인터페이스를 두는 것이다.

```typescript
interface FillLayer {
  layout: FillLayout;
  paint: FillPaint;
}
interface LineLayer {
  layout: LineLayout;
  paint: LinePaint;
}
interface PointLayer {
  layout: PointLayout;
  paint: PointPaint;
}
type Layer = FillLayer | LineLayer | PointLayer;
```

이렇게 정의하면 layout과 paint가 섞이는 가능성이 배제된다 — 유효한 상태만 표현하는 타입을 선호하라는 Item 29의 조언을 따른 것이다.

## 2. 가장 흔한 형태 — 태그된 유니온

이 패턴의 압도적으로 흔한 예가 태그된 유니온이다. 속성 하나가 문자열 리터럴 타입들의 유니온인 경우:

```typescript
interface Layer {
  type: 'fill' | 'line' | 'point';
  layout: FillLayout | LineLayout | PointLayout;
  paint: FillPaint | LinePaint | PointPaint;
}
```

`type: 'fill'`인데 `LineLayout`과 `PointPaint`라니, 말이 안 된다. 인터페이스의 유니온으로 바꿔 이 가능성을 배제하라.

```typescript
interface FillLayer {
  type: 'fill';
  layout: FillLayout;
  paint: FillPaint;
}
interface LineLayer {
  type: 'line';
  layout: LineLayout;
  paint: LinePaint;
}
interface PointLayer {
  type: 'paint';
  layout: PointLayout;
  paint: PointPaint;
}
type Layer = FillLayer | LineLayer | PointLayer;
```

`type` 속성이 "태그"(판별자)다. 런타임에 접근 가능하고, 타입스크립트가 유니온의 어느 구성원을 다루는지 판단하기에 딱 충분한 정보를 준다.

```typescript
function drawLayer(layer: Layer) {
  if (layer.type === 'fill') {
    const {paint} = layer;
    //     ^? const paint: FillPaint
    const {layout} = layer;
    //     ^? const layout: FillLayout
  } else if (layer.type === 'line') {
    const {paint} = layer;
    //     ^? const paint: LinePaint
    const {layout} = layer;
    //     ^? const layout: LineLayout
  } else {
    const {paint} = layer;
    //     ^? const paint: PointPaint
    const {layout} = layer;
    //     ^? const layout: PointLayout
  }
}
```

속성 간의 관계를 올바르게 모델링하면 타입스크립트가 코드의 정확성을 검사하도록 돕는 것이다. 처음의 `Layer` 정의였다면 같은 코드가 타입 단언으로 어지러웠을 것이다.

> **핵심 통찰**: 태그된 유니온은 타입 체커와 워낙 잘 맞아서 타입스크립트 코드 어디에나 있다. 이 패턴을 알아보고, 쓸 수 있을 때 적용하라. 데이터 타입을 태그된 유니온으로 표현할 수 있다면 보통 그렇게 하는 것이 좋다.

## 3. 옵셔널 필드도 유니온이다 — 함께 움직이는 속성 묶기

옵셔널 필드를 "그 타입과 undefined의 유니온"으로 생각하면 이 패턴에 들어맞는다.

```typescript
interface Person {
  name: string;
  // 둘 다 있거나 둘 다 없다
  placeOfBirth?: string;
  dateOfBirth?: Date;
}
```

타입 정보가 담긴 주석은 문제가 있다는 강한 신호다(Item 31). `placeOfBirth`와 `dateOfBirth` 사이의 관계를 타입스크립트에 알리지 않았다. 더 나은 모델링은 두 속성을 한 객체로 옮기는 것이다 — null을 가장자리로 밀어내기(Item 33)와 같은 정신이다.

```typescript
interface Person {
  name: string;
  birth?: {
    place: string;
    date: Date;
  }
}
```

이제 place는 있는데 date가 없는 값에 타입스크립트가 항의한다.

```typescript
const alanT: Person = {
  name: 'Alan Turing',
  birth: {
    // ~~~~ Property 'date' is missing in type
    //      '{ place: string; }' but required in type
    //      '{ place: string; date: Date; }'
    place: 'London'
  }
}
```

그리고 `Person`을 받는 함수는 체크 한 번이면 된다.

```typescript
function eulogize(person: Person) {
  console.log(person.name);
  const {birth} = person;
  if (birth) {
    console.log(`was born on ${birth.date} in ${birth.place}.`);
  }
}
```

타입 구조를 내가 통제할 수 없다면(API에서 오는 것이라면), 이제는 익숙한 인터페이스의 유니온으로 필드 간의 관계를 모델링할 수 있다.

```typescript
interface Name {
  name: string;
}
interface PersonWithBirth extends Name {
  placeOfBirth: string;
  dateOfBirth: Date;
}
type Person = Name | PersonWithBirth;

function eulogize(person: Person) {
  if ('placeOfBirth' in person) {
    person
    // ^? (parameter) person: PersonWithBirth
    const {dateOfBirth} = person;  // OK
    //     ^? const dateOfBirth: Date
  }
}
```

어느 쪽이든 타입 정의가 속성 간의 관계를 더 분명하게 만든다. 옵셔널 속성은 유용할 때가 많지만 인터페이스에 추가하기 전에 두 번 생각하라 — 옵셔널 필드의 단점은 Item 37에서 더 다룬다.

## 기억해야 할 것들

- 유니온 타입 속성을 여럿 가진 인터페이스는 속성 간의 관계를 가리므로 실수인 경우가 많다.
- 인터페이스의 유니온이 더 정밀하며 타입스크립트가 이해할 수 있다.
- 제어 흐름 분석이 잘 되도록 태그된 유니온을 사용하라. 워낙 지원이 좋아서 타입스크립트 코드 어디에나 있는 패턴이다.
- 옵셔널 속성 여러 개를 묶으면 데이터를 더 정확하게 모델링할 수 있는지 고려하라.
