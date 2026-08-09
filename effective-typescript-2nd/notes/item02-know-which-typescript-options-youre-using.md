# Item 2: 어떤 타입스크립트 설정을 사용하는지 알기 (Know Which TypeScript Options You're Using)

## 핵심 질문

같은 코드가 어떤 프로젝트에서는 통과하고 어떤 프로젝트에서는 에러가 나는 이유는 무엇인가? 어떤 설정이 언어의 성격 자체를 바꾸는가?

다음 코드는 타입 체커를 통과할까?

```typescript
function add(a, b) {
  return a + b;
}
add(10, null);
```

**어떤 설정을 쓰는지 모르면 대답할 수 없다.** 타입스크립트 컴파일러의 설정은 집필 시점 기준 100개가 넘고, 그중 몇 개는 언어 자체의 핵심 성격을 바꾼다. 대부분의 언어가 사용자에게 맡기지 않는 고수준 설계 선택을 타입스크립트는 설정으로 열어 두었기 때문에, 설정에 따라 완전히 다른 언어처럼 느껴질 수 있다.

설정은 커맨드라인(`tsc --noImplicitAny program.ts`)보다 **설정 파일 `tsconfig.json`으로 관리하는 것이 좋다**. 동료와 도구가 프로젝트의 사용 방식을 정확히 알 수 있기 때문이다. `tsc --init`으로 생성한다.

```json
{
  "compilerOptions": {
    "noImplicitAny": true
  }
}
```

언어의 핵심을 통제하는 설정 중 가장 중요한 둘은 `noImplicitAny`와 `strictNullChecks`다.

## 1. noImplicitAny

타입스크립트가 변수의 타입을 알아낼 수 없을 때의 동작을 통제한다. 꺼져 있으면 위 `add`의 매개변수는 암시적 `any`(*implicit any - 직접 `any`라고 쓰지 않았는데도 추론 실패로 부여되는 `any` 타입*)가 된다.

```typescript
function add(a, b) {   // noImplicitAny가 꺼져 있으면 유효
  return a + b;
}
// 편집기 표시: function add(a: any, b: any): any
```

`any` 타입은 해당 코드의 타입 체크를 사실상 꺼 버린다(Item 5). `noImplicitAny`를 켜면 에러가 된다.

```typescript
function add(a, b) {
  //         ~ Parameter 'a' implicitly has an 'any' type
  //            ~ Parameter 'b' implicitly has an 'any' type
  return a + b;
}
```

명시적 타입 선언(`: any` 또는 더 구체적인 타입)으로 해결한다.

```typescript
function add(a: number, b: number) {
  return a + b;
}
```

- **새 프로젝트**: 처음부터 켜고 시작한다. 코드를 쓰면서 타입을 함께 쓰게 되어 문제를 잘 잡고, 가독성과 개발 경험(Item 6)이 좋아진다.
- **끄는 것이 정당한 경우**: 자바스크립트 프로젝트를 타입스크립트로 전환하는 과도기뿐이다(Chapter 10). 그마저도 임시 상태여야 한다. `noImplicitAny` 없는 타입스크립트는 놀랄 만큼 느슨하며, Item 83에서 그 문제를 다룬다.

## 2. strictNullChecks

`null`과 `undefined`가 모든 타입의 값으로 허용되는지를 통제한다.

```typescript
const x: number = null;
// strictNullChecks 꺼짐: OK - null은 유효한 number
// strictNullChecks 켜짐:
// ~ Type 'null' is not assignable to type 'number'
```

`undefined`를 썼어도 같은 에러가 난다. `null`을 허용할 의도라면 명시하면 된다.

```typescript
const x: number | null = null;
```

허용하지 않을 의도라면 `null`이 어디서 왔는지 추적해서 체크나 단언을 추가해야 한다.

```typescript
const statusEl = document.getElementById('status');
statusEl.textContent = 'Ready';
// ~~~~~~~~ 'statusEl' is possibly 'null'.

if (statusEl) {
  statusEl.textContent = 'Ready';  // OK - null이 배제됨
}
statusEl!.textContent = 'Ready';   // OK - null이 아니라고 단언함
```

`if`로 타입에서 `null`을 배제하는 것을 좁히기(*narrowing - 조건문 등으로 타입의 범위를 줄이는 것. refining이라고도 함*)라고 하며 Item 22에서 다룬다. `!`는 널 아님 단언(non-null assertion)인데, 타입 단언은 런타임 예외로 이어질 수 있으므로 Item 9의 기준에 따라 써야 한다.

`strictNullChecks`는 `null`/`undefined` 관련 오류를 잡는 데 대단히 효과적이지만 언어 사용 난도를 높인다. 타입스크립트 경험자가 새 프로젝트를 시작한다면 켜는 것이 맞고, 언어 입문자나 마이그레이션 중이라면 미룰 수 있다 - 단, **`noImplicitAny`를 먼저 켜고 나서** 고려할 것. 끄고 일한다면 "undefined is not an object" 런타임 에러를 볼 때마다 더 엄격한 체크가 필요하다는 신호로 받아들여야 한다. 프로젝트가 커질수록 설정 변경은 어려워지므로 너무 오래 미루지 말 것. 대부분의 타입스크립트 코드는 `strictNullChecks`를 켜고 있으며, 결국 도달해야 할 지점이다.

## 3. 그 외 설정: strict와 그 너머

- **`strict`**: `noImplicitThis`·`strictFunctionTypes` 등 언어 의미에 영향을 주는 나머지 검사까지 한꺼번에 켠다(개별 검사는 `noImplicitAny`·`strictNullChecks`에 비하면 부차적이다). 타입스크립트가 잡을 수 있는 오류를 가장 많이 잡는 상태이며, 궁극적으로 도달해야 할 목표다. `tsc --init`으로 만든 프로젝트는 기본이 `strict` 모드다.
- **"strict보다 엄격한" 설정**: 오류를 더 공격적으로 찾도록 선택적으로 켤 수 있다. 대표적으로 `noUncheckedIndexedAccess`가 객체·배열 인덱스 접근의 오류를 잡아 준다.

```typescript
const tenses = ['past', 'present', 'future'];
tenses[3].toUpperCase();
// --strict: 에러 없음, 런타임 예외 발생
// noUncheckedIndexedAccess 켜짐:
// ~~~~~~~~~ Object is possibly 'undefined'.
```

공짜는 아니다 - `tenses[0].toUpperCase()` 같은 유효한 접근도 `undefined` 가능성으로 지적된다. 쓰는 프로젝트도 있고 안 쓰는 프로젝트도 있지만, 존재는 알아 두어야 한다(Item 48).

> **실무 팁**: 동료가 공유한 타입스크립트 예제의 에러가 내 환경에서 재현되지 않는다면, 가장 먼저 컴파일러 설정이 같은지 확인하라.

## 기억해야 할 것들

- 타입스크립트 컴파일러에는 언어의 핵심 성격에 영향을 주는 설정이 여럿 있다.
- 커맨드라인 옵션보다 `tsconfig.json`으로 설정하라.
- 자바스크립트 프로젝트를 전환하는 중이 아니라면 `noImplicitAny`를 켜라.
- "undefined is not an object" 류의 런타임 에러를 막으려면 `strictNullChecks`를 켜라.
- 타입스크립트가 제공하는 가장 철저한 검사인 `strict` 활성화를 목표로 하라.
