# Item 3: 코드 생성과 타입은 독립적임을 이해하기 (Understand That Code Generation Is Independent of Types)

## 핵심 질문

`tsc`의 두 가지 역할(코드 생성·타입 체크)이 서로 독립적이라는 사실은 어떤 함의를 갖는가? 타입이 런타임에 할 수 없는 일은 무엇인가?

크게 보면 `tsc`(타입스크립트 컴파일러)는 두 가지 일을 한다.

1. 최신 타입스크립트/자바스크립트를 브라우저 등에서 동작하는 구버전 자바스크립트로 변환한다 - 트랜스파일(*transpile - translate + compile의 합성어. 고수준 언어를 또 다른 고수준 언어로 변환하는 것*)
2. 코드의 타입 오류를 체크한다

놀라운 점은 **이 둘이 완전히 독립적**이라는 것이다. 코드의 타입은 타입스크립트가 내놓는 자바스크립트에 영향을 줄 수 없고, 실행되는 것은 그 자바스크립트이므로 **타입은 코드의 실행 방식에 영향을 줄 수 없다**. 여기서 여섯 가지 함의가 나온다.

## 1. 런타임에는 타입스크립트 타입을 체크할 수 없다

```typescript
interface Square {
  width: number;
}
interface Rectangle extends Square {
  height: number;
}
type Shape = Square | Rectangle;

function calculateArea(shape: Shape) {
  if (shape instanceof Rectangle) {
    //                 ~~~~~~~~~ 'Rectangle' only refers to a type,
    //                           but is being used as a value here.
    return shape.height * shape.width;
    //           ~~~~~~ Property 'height' does not exist on type 'Shape'.
  } else {
    return shape.width * shape.width;
  }
}
```

`instanceof` 체크는 런타임에 일어나는데 `Rectangle`은 타입이라서 런타임 동작에 관여할 수 없다. 타입스크립트의 타입은 지워질 수 있는(*erasable - 컴파일 과정에서 흔적 없이 제거 가능한*) 것으로, 자바스크립트로 컴파일되면서 인터페이스·타입·타입 구문이 전부 제거된다. 위 코드가 컴파일된 자바스크립트를 보면 문제가 분명해진다.

```javascript
function calculateArea(shape) {
  if (shape instanceof Rectangle) {  // Rectangle이 어디에도 정의되어 있지 않다
    return shape.height * shape.width;
  } else {
    return shape.width * shape.width;
  }
}
```

런타임에 타입을 알려면 **생성된 자바스크립트에서도 말이 되는 방법으로 타입을 재구성**해야 하며, 세 가지 방법이 있다.

**방법 1 - 속성 존재 체크**: 런타임에 존재하는 값만 다루면서도 타입 체커가 타입을 좁히게 해 준다.

```typescript
function calculateArea(shape: Shape) {
  if ('height' in shape) {
    return shape.width * shape.height;
    //     ^? (parameter) shape: Rectangle
  } else {
    return shape.width * shape.width;
  }
}
```

**방법 2 - 태그 도입**: 런타임에 접근 가능한 방식으로 타입 정보를 명시적으로 저장한다.

```typescript
interface Square {
  kind: 'square';
  width: number;
}
interface Rectangle {
  kind: 'rectangle';
  height: number;
  width: number;
}
type Shape = Square | Rectangle;

function calculateArea(shape: Shape) {
  if (shape.kind === 'rectangle') {
    return shape.width * shape.height;
    //     ^? (parameter) shape: Rectangle
  } else {
    return shape.width * shape.width;
    //     ^? (parameter) shape: Square
  }
}
```

여기서 `kind`가 태그이고, 이런 `Shape`를 태그된 유니온(*tagged union - 공통 판별 속성으로 구성원을 구분하는 유니온 타입. discriminated union(판별 유니온)과 같은 말이며 이때 태그를 discriminant(판별자)라 부른다*)이라 한다. 런타임에 타입 정보를 복원하기가 워낙 쉬워서 타입스크립트 어디서나 볼 수 있는 패턴이다.

**방법 3 - 클래스 사용**: `class`는 **타입과 값을 동시에 도입**하는 구문이라 `instanceof`가 동작한다.

```typescript
class Square {
  width: number;
  constructor(width: number) {
    this.width = width;
  }
}
class Rectangle extends Square {
  height: number;
  constructor(width: number, height: number) {
    super(width);
    this.height = height;
  }
}
type Shape = Square | Rectangle;

function calculateArea(shape: Shape) {
  if (shape instanceof Rectangle) {
    return shape.width * shape.height;
    //     ^? (parameter) shape: Rectangle
  } else {
    return shape.width * shape.width;
    //     ^? (parameter) shape: Square
  }
}
```

`type Shape = Square | Rectangle`의 `Rectangle`은 **타입**을, `shape instanceof Rectangle`의 `Rectangle`은 **값**(생성자 함수)을 가리킨다. 이 구분은 중요하지만 미묘한데, Item 8에서 구별법을 다룬다.

## 2. 타입 오류가 있는 코드도 출력을 만들 수 있다

```
$ cat test.ts
let x = 'hello';
x = 1234;
$ tsc test.ts
test.ts:2:1 - error TS2322: Type '1234' is not assignable to type 'string'

$ cat test.js
var x = 'hello';
x = 1234;
```

코드 출력이 타입 체크와 독립적이므로 타입 오류가 있어도 컴파일은 된다. C나 자바 사용자에게는 놀랍겠지만, 타입스크립트의 에러는 그 언어들의 **경고(warning)** 와 비슷하다고 생각하면 된다 - 문제일 가능성이 높으니 살펴볼 가치가 있지만 빌드를 멈추지는 않는다.

> **참고**: "타입스크립트가 컴파일이 안 된다"는 흔한 표현은 엄밀히 틀렸다. 컴파일은 코드 생성 쪽 일이고, 타입스크립트가 유효한 자바스크립트인 한(때로는 아니어도) 출력은 만들어진다. "코드에 에러가 있다" 또는 "타입 체크가 안 된다"고 말하는 편이 정확하다.

에러가 있어도 출력이 나오는 것은 실전에서 유용하다 - 웹 앱의 한 부분에 문제가 있음을 알아도 나머지 부분을 먼저 테스트할 수 있다. 다만 커밋 시점에는 에러 0개를 목표로 해야 한다. 그러지 않으면 어떤 에러가 예상된 것이고 아닌지를 기억해야 하는 함정에 빠진다. 에러 시 출력을 끄고 싶다면 `tsconfig.json`의 `noEmitOnError`(또는 빌드 도구의 대응 옵션)를 쓴다.

## 3. 타입 연산은 런타임 값에 영향을 줄 수 없다

`string | number` 값을 항상 `number`로 정규화하려는 잘못된 시도:

```typescript
function asNumber(val: number | string): number {
  return val as number;
}
```

생성된 자바스크립트를 보면 이 함수의 실체가 드러난다.

```javascript
function asNumber(val) {
  return val;
}
```

변환은 전혀 일어나지 않는다. `as number`는 타입 연산이므로 런타임 동작에 관여할 수 없다. 값을 정규화하려면 자바스크립트 구문으로 런타임 타입을 체크하고 변환해야 한다.

```typescript
function asNumber(val: number | string): number {
  return Number(val);
}
```

`as number`는 타입 단언(*type assertion - 타입 체커의 추론을 개발자의 판단으로 덮어쓰는 구문. "캐스트(cast)"라고 부르기도 하지만 실제 변환이 없으므로 부정확한 명칭*)이다. 언제 써도 되는지는 Item 9에서 다룬다.

## 4. 런타임 타입은 선언된 타입과 다를 수 있다

다음 함수가 마지막 `console.log`에 도달할 수 있을까?

```typescript
function setLightSwitch(value: boolean) {
  switch (value) {
    case true:
      turnLightOn();
      break;
    case false:
      turnLightOff();
      break;
    default:
      console.log(`I'm afraid I can't do that.`);
  }
}
```

타입스크립트는 보통 죽은 코드를 지적하지만 `strict`에서도 이 `default`는 지적하지 않는다. 핵심은 `boolean`이 **선언된** 타입이라는 것 - 런타임에는 사라진다. 자바스크립트 코드가 `"ON"` 같은 값으로 호출할 수도 있고, 순수 타입스크립트에서도 일어난다.

```typescript
interface LightApiResponse {
  lightSwitchValue: boolean;
}
async function setLight() {
  const response = await fetch('/light');
  const result: LightApiResponse = await response.json();
  setLightSwitch(result.lightSwitchValue);
}
```

`/light` 응답이 `LightApiResponse`라고 **선언**했지만 그것을 강제하는 것은 아무것도 없다. API를 잘못 이해했거나 배포 후 API가 바뀌었다면 런타임에 `string`이 넘어온다. 런타임 타입과 선언된 타입이 어긋나면 타입스크립트는 몹시 혼란스러워지므로 이런 "불건전한" 타입은 최대한 피해야 한다(Item 48).

## 5. 타입스크립트 타입으로는 함수를 오버로드할 수 없다

C++처럼 매개변수 타입만 다른 함수를 여러 벌 정의하는 것(함수 오버로딩)은 불가능하다 - 런타임 동작이 타입과 독립적이기 때문이다.

```typescript
function add(a: number, b: number) { return a + b; }
//       ~~~ Duplicate function implementation
function add(a: string, b: string) { return a + b; }
//       ~~~ Duplicate function implementation
```

타입스크립트의 오버로딩은 **온전히 타입 수준에서만** 동작한다. 타입 시그니처는 여러 개 쓸 수 있지만 구현은 하나뿐이다.

```typescript
function add(a: number, b: number): number;
function add(a: string, b: string): string;
function add(a: any, b: any) {
  return a + b;
}

const three = add(1, 2);
//    ^? const three: number
const twelve = add('1', '2');
//    ^? const twelve: string
```

앞의 두 시그니처는 타입 정보만 제공하며 자바스크립트 출력에서는 제거된다. 구현부의 `any`는 바람직하지 않은데, 처리법과 오버로드의 미묘한 점들은 Item 52에서 다룬다.

## 6. 타입스크립트 타입은 런타임 성능에 영향을 주지 않는다

타입과 타입 연산은 자바스크립트 생성 시점에 지워지므로 런타임 성능에 영향을 줄 수 없다. **타입스크립트의 정적 타입은 진짜로 제로 코스트다.** 다음에 누군가 런타임 오버헤드를 이유로 타입스크립트를 반대하면, 그 주장을 얼마나 잘 검증했는지 알 수 있을 것이다. 다만 두 가지 단서가 있다.

- 런타임 오버헤드 대신 **빌드 타임 오버헤드**가 있다. 컴파일은 대체로 빠르고(특히 증분 빌드), 심각해지면 빌드 도구의 "transpile only" 옵션으로 타입 체크를 건너뛸 수 있다(Item 78).
- 구형 런타임을 지원하기 위해 내놓는 코드(예: ES5 타깃의 제너레이터 헬퍼)는 네이티브 구현 대비 오버헤드가 있을 수 있다. 하지만 이것은 어떤 트랜스파일러든 마찬가지이며, 방출 타깃/언어 레벨의 문제일 뿐 타입과는 여전히 무관하다.

## 기억해야 할 것들

- 코드 생성은 타입 시스템과 독립적이다. 타입스크립트 타입은 코드의 런타임 동작에 영향을 줄 수 없다.
- 타입 오류가 있는 프로그램도 코드를 생성("컴파일")할 수 있다.
- 타입스크립트 타입은 런타임에 존재하지 않는다. 런타임에 타입을 조회하려면 재구성할 방법이 필요하며, 태그된 유니온과 속성 체크가 흔한 방법이다.
- `class`처럼 타입스크립트 타입과 런타임에 존재하는 값을 동시에 도입하는 구문도 있다.
- 컴파일 시 지워지기 때문에, 타입스크립트 타입은 런타임 성능에 영향을 줄 수 없다.
