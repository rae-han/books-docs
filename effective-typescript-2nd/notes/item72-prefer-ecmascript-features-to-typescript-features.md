# Item 72: 타입스크립트 기능보다 ECMAScript 기능 선호하기 (Prefer ECMAScript Features to TypeScript Features)

## 핵심 질문

"타입을 지우면 자바스크립트"라는 규칙의 역사적 예외들 - enum, 매개변수 프로퍼티, 네임스페이스, 데코레이터, private - 은 왜 피해야 하는가?

타입스크립트와 자바스크립트의 관계는 변해 왔다. 2010년 마이크로소프트가 타입스크립트를 시작할 때는 자바스크립트가 "고쳐야 할 문제적 언어"라는 인식이 지배적이라 클래스·데코레이터·모듈 시스템 같은 빠진 기능을 얹는 것이 흔했고 타입스크립트도 그랬다. 시간이 지나 TC39(자바스크립트 표준화 기구)가 같은 기능들을 언어 코어에 추가했는데, 타입스크립트에 있던 버전과 호환되지 않았다. 타입스크립트는 대체로 표준을 채택하는 쪽을 택했고, 결국 현재의 지배 원칙을 세웠다: **TC39가 런타임을 정의하고, 타입스크립트는 타입 공간에서만 혁신한다.**

그 결정 이전의 기능 몇 개가 남아 있다. 언어의 나머지 패턴에 맞지 않으므로 알아보고 이해하는 것이 중요하며, 일반적으로 **피하기를 권한다** - 타입스크립트와 자바스크립트의 관계를 최대한 명료하게 유지하고, 대안 컴파일러와의 호환성과 미래의 표준 정렬에 대비하기 위해서다. 이 조언을 따르면 타입스크립트를 "타입 있는 자바스크립트"로 생각할 수 있다.

## 1. Enum → 리터럴 타입의 유니온

```typescript
enum Flavor {
  Vanilla = 0,
  Chocolate = 1,
  Strawberry = 2,
}
```

enum의 명분은 맨 숫자보다 안전하고 투명하다는 것이지만, 타입스크립트의 enum에는 기벽이 있다. 미묘하게 다른 변종이 여럿이다.

- **숫자 값 enum**: `number` 타입이 할당 가능해서 별로 안전하지 않다(비트 플래그 구조를 위해 그렇게 설계됐다).
- **문자열 값 enum**: 타입 안전성과 유의미한 런타임 값을 주지만, **타입스크립트의 다른 모든 타입과 달리 명목적으로 타이핑된다.**
- **const enum**: 런타임에 완전히 사라진다 - 컴파일러가 `Flavor.Chocolate`을 `1`로 다시 쓴다. 컴파일러 동작에 대한 기대를 깨뜨린다.
- **preserveConstEnums 플래그가 켜진 const enum**: 일반 enum처럼 런타임 코드를 방출한다.

문자열 enum의 명목적 타이핑은 특히 놀랍고, 라이브러리를 공개할 때 문제가 된다.

```typescript
enum Flavor {
  Vanilla = 'vanilla',
  Chocolate = 'chocolate',
  Strawberry = 'strawberry',
}
function scoop(flavor: Flavor) { /* ... */ }

scoop('vanilla');  // 자바스크립트에서는 OK - 런타임엔 그냥 문자열이니까

// 타입스크립트 사용자는:
scoop('vanilla');
//    ~~~~~~~~~ '"vanilla"' is not assignable to parameter of type 'Flavor'
import {Flavor} from 'ice-cream';
scoop(Flavor.Vanilla);  // OK
```

자바스크립트 사용자와 타입스크립트 사용자의 경험이 갈린다 - 문자열 enum을 피할 이유다. 타입스크립트에는 다른 언어에서 덜 흔한 대안이 있다: **리터럴 타입의 유니온**.

```typescript
type Flavor = 'vanilla' | 'chocolate' | 'strawberry';

let favoriteFlavor: Flavor = 'chocolate';  // OK
favoriteFlavor = 'americone dream';
// ~~~~~~~~~~~ Type '"americone dream"' is not assignable to type 'Flavor'
```

enum만큼 안전하면서 자바스크립트로 더 직접적으로 번역되고 편집기 자동완성도 된다(Item 35). 숫자 enum이라면? 선택할 수 있다면 값에 문자열을 강력히 고려하라 - 디버거나 네트워크 요청에서 `{"flavor": 1}`과 `{"flavor": "chocolate"}` 중 무엇을 보고 싶은가?

## 2. 매개변수 프로퍼티

생성자 매개변수를 속성에 할당하는 축약 문법:

```typescript
class Person {
  constructor(public name: string) {}
}
```

첫 형태(명시적 할당)와 동등하지만 문제들이 있다.

1. 컴파일 시 **코드를 생성하는** 몇 안 되는 구문 중 하나다(enum도 그렇다). 일반적으로 컴파일은 타입을 지우는 것뿐인데.
2. 매개변수가 생성된 코드에서만 쓰이므로 소스만 보면 미사용 매개변수처럼 보인다.
3. 매개변수 프로퍼티와 일반 프로퍼티가 섞이면 **클래스의 설계가 가려진다.**

```typescript
class Person {
  first: string;
  last: string;
  constructor(public name: string) {
    [this.first, this.last] = name.split(' ');
  }
}
```

이 클래스에는 속성이 셋(first·last·name)인데 생성자 앞에는 둘만 나열되어 있어 읽어 내기 어렵다. 클래스가 매개변수 프로퍼티로만 이뤄져 있고 메서드가 없다면 인터페이스 + 객체 리터럴을 고려하라(구조적 타이핑 덕에 서로 할당 가능하다 - Item 4). 의견이 갈리는 기능이다 - 타자 절약을 좋아하는 사람도 있다. 다만 타입스크립트의 나머지 패턴에 맞지 않고 새 개발자에게 그 패턴을 가릴 수 있음을 인지하고, 매개변수/일반 프로퍼티 혼용 뒤에 클래스 설계를 숨기지 마라.

## 3. 네임스페이스와 삼중 슬래시 import

ES2015 이전 자바스크립트에는 공식 모듈 시스템이 없었고(Node는 require, 브라우저는 AMD), 타입스크립트도 `module` 키워드와 삼중 슬래시 import로 그 공백을 메웠다. ES2015가 공식 모듈을 추가한 뒤 혼동을 피하려 `namespace`를 동의어로 추가했다.

```typescript
// other.ts
namespace foo {
  export function bar() {}
}
// index.ts
/// <reference path="other.ts"/>
foo.bar();
```

타입 선언 파일 밖에서 삼중 슬래시 import와 module 키워드는 역사적 골동품일 뿐이다. **내 코드에서는 ES2015 스타일 모듈(import/export)을 써라.**

## 4. experimentalDecorators

데코레이터는 클래스·메서드·속성에 주석을 달거나 수정한다(`@` 접두사). 2015년 타입스크립트는 Angular 지원을 위해 데코레이터 **초안**을 `--experimentalDecorators` 플래그 뒤에 추가했다. 8년 뒤인 2023년, 매우 다른 형태의 제안이 stage 3에 도달했고, **표준 데코레이터는 플래그 없이 쓸 수 있다.**

```typescript
class Greeter {
  greeting: string;
  constructor(message: string) {
    this.greeting = message;
  }
  @logged  // <-- 데코레이터
  greet() {
    return `Hello, ${this.greeting}`;
  }
}

function logged(originalFn: any, context: ClassMethodDecoratorContext) {
  return function(this: any, ...args: any[]) {
    console.log(`Calling ${String(context.name)}`);
    return originalFn.call(this, ...args);
  };
}
```

tsconfig.json의 `experimentalDecorators`가 켜져 있다면 비표준 데코레이터를 쓰고 있는 것이다. **끌 수 있으면 꺼라!** 라이브러리·프레임워크 때문에 유지해야 한다면 최소한 직접 비표준 데코레이터를 새로 쓰면서 구덩이를 더 파지는 마라 - 결국 표준으로 마이그레이션해야 한다. 플래그가 없다면 마음껏 쓰되, 데코레이터가 모든 문제의 최선은 아니며 코드를 따라가기 어렵게 만들 수 있음을 기억하라 - 메서드의 타입 시그니처를 바꾸는 데코레이터는 피하라.

## 5. 멤버 가시성 한정자 (private·protected·public) → #private

타입스크립트의 `private`은 강제처럼 보이지만:

```typescript
class Diary {
  private secret = 'cheated on my English test';
}
const diary = new Diary();
diary.secret
//    ~~~~~~ Property 'secret' is private and only accessible within ...
```

private은 **타입 시스템의 기능**이고, 타입 시스템의 기능은 런타임에 사라진다(Item 3). 컴파일된 자바스크립트에는 private 표시가 없고 비밀은 노출된다. 타입스크립트 안에서조차 단언이나 순회로 접근할 수 있다.

```typescript
(diary as any).secret            // OK
console.log(Object.entries(diary));  // [["secret", "cheated on ..."]]
```

**ES2022가 진짜 private 필드를 공식 추가했다.** 타입스크립트의 private과 달리 타입 체크와 런타임 양쪽에서 강제된다. 클래스 속성에 `#` 접두사를 쓴다.

```typescript
class PasswordChecker {
  #passwordHash: number;
  constructor(passwordHash: number) {
    this.#passwordHash = passwordHash;
  }
  checkPassword(password: string) {
    return hash(password) === this.#passwordHash;
  }
}

const checker = new PasswordChecker(hash('s3cret'));
checker.#passwordHash
//      ~~~~~~~~~~~~~ Property '#passwordHash' is not accessible outside class
//                    'PasswordChecker' because it has a private identifier.
```

`#passwordHash`는 클래스 밖에서 접근 불가하고 열거되지 않는다. private 필드를 네이티브 지원하지 않는 타깃(ES2021 이하)에도 데이터를 비공개로 유지하는 폴백 구현이 있다. **표준이고, 널리 지원되고, 타입스크립트의 private보다 안전하다. 이것을 써라.**

`public`은? 자바스크립트(그리고 타입스크립트)의 기본 가시성이라 명시할 필요가 없다. `protected`는? private이 캡슐화를 함의한다면 protected는 상속을 함의하는데, OOP의 일반 규칙이 상속보다 합성이므로 실용적 쓰임은 드물다. 필드 한정자 `readonly`는 타입 수준 구문이라 써도 좋고(Item 14), 필드는 `#private`이면서 readonly일 수 있다.

## 기억해야 할 것들

- 대체로 코드에서 모든 타입을 지우면 타입스크립트를 자바스크립트로 변환할 수 있다.
- enum, 매개변수 프로퍼티, 삼중 슬래시 import, 실험적 데코레이터, 멤버 가시성 한정자는 이 규칙의 역사적 예외다.
- 코드베이스에서 타입스크립트의 역할을 최대한 명료하게 유지하고 미래의 호환성 문제를 피하려면 비표준 기능을 피하라.
