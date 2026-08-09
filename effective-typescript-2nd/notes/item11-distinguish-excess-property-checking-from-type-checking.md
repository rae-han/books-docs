# Item 11: 잉여 속성 체크와 타입 체크 구분하기 (Distinguish Excess Property Checking from Type Checking)

## 핵심 질문

구조적 타이핑에서는 추가 속성이 허용된다면서(Item 4), 왜 객체 리터럴의 추가 속성은 에러가 나는가? 이 검사는 언제 적용되고 언제 사라지는가?

선언된 타입의 변수에 **객체 리터럴**을 할당하면, 타입스크립트는 그 타입의 속성이 있는지 **그리고 "그 외의 속성은 없는지"** 확인한다.

```typescript
interface Room {
  numDoors: number;
  ceilingHeightFt: number;
}
const r: Room = {
  numDoors: 1,
  ceilingHeightFt: 10,
  elephant: 'present',
  // ~~~~~~~ Object literal may only specify known properties,
  //         and 'elephant' does not exist in type 'Room'
};
```

`elephant` 속성이 있는 게 이상하긴 하지만, 구조적 타이핑 관점(Item 4)에서 이 에러는 앞뒤가 맞지 않는다. 중간 변수를 끼우면 실제로 할당이 된다.

```typescript
const obj = {
  numDoors: 1,
  ceilingHeightFt: 10,
  elephant: 'present',
};
const r: Room = obj;  // OK
```

`obj`의 추론 타입은 `{ numDoors: number; ceilingHeightFt: number; elephant: string }`이고, 이 타입의 값 집합은 `Room` 값 집합의 부분집합이므로(Item 7) 할당 가능하다. 두 예제의 차이는 무엇일까? 첫 번째에서는 **잉여 속성 체크**(*excess property checking - 선언된 타입의 문맥에 쓰인 객체 리터럴에서 알려지지 않은 속성을 금지하는 별도 검사*)라는 과정이 발동한 것이다. 이것은 구조적 타입 시스템이 놓칠 중요한 부류의 오류를 잡아 주지만 한계가 있으며, **통상적인 할당 가능성 검사와 뒤섞어 이해하면 구조적 타이핑의 직관을 세우기 어려워진다**. 별개의 과정으로 인식해야 한다.

## 1. 왜 이런 검사가 필요한가 - 타입은 생각보다 훨씬 넓다

Item 1에서 봤듯 타입스크립트는 런타임 예외를 던질 코드만이 아니라 **의도와 다르게 동작하는 코드**도 잡으려 한다.

```typescript
interface Options {
  title: string;
  darkMode?: boolean;
}
function createWindow(options: Options) {
  if (options.darkMode) {
    setDarkMode();
  }
  // ...
}
createWindow({
  title: 'Spider Solitaire',
  darkmode: true
  // ~~~~~~~ Object literal may only specify known properties,
  //         but 'darkmode' does not exist in type 'Options'.
  //         Did you mean to write 'darkMode'?
});
```

이 코드는 런타임에 아무 에러도 던지지 않지만, 타입스크립트가 말한 그대로의 이유로 의도대로 동작하지도 않는다 - `darkmode`가 아니라 `darkMode`(대문자 M)여야 한다.

순수하게 구조적인 타입 체커는 이런 오류를 잡을 수 없다. `Options` 타입이 **어마어마하게 넓기** 때문이다: `title`이 string인 모든 객체가 - `darkMode`에 boolean 아닌 값을 넣지 않는 한 어떤 속성을 더 갖고 있어도 - 전부 `Options`다.

```typescript
const o1: Options = document;                 // OK - title: string이 있다
const o2: Options = new HTMLAnchorElement();  // OK - title: string이 있다
```

## 2. 발동 조건 - "신선한" 객체 리터럴

잉여 속성 체크는 타입 시스템의 구조적 본질을 훼손하지 않으면서 이 넓음을 억제하려는 장치다. **선언된 타입이 있는 문맥에 쓰인 객체 리터럴**에서 알려지지 않은 속성을 금지한다. (그래서 "엄격한 객체 리터럴 체크"라고도 하고, 갓 만들어진 객체에 적용된다는 뜻에서 "신선도(freshness)" 체크라고도 부른다.)

문맥은 선언된 타입의 변수로의 할당, 함수 인수, 선언된 반환 타입이 있는 함수의 반환값 등이다. `document`나 `new HTMLAnchorElement()`는 객체 리터럴이 아니라서 발동하지 않았고, `{title, darkmode}` 객체는 리터럴이라서 발동했다.

체크가 사라지는 경로 두 가지를 기억하자.

**중간 변수** - 두 번째 줄의 우변(`intermediate`)은 객체 리터럴이 아니므로 체크가 적용되지 않는다.

```typescript
const intermediate = { darkmode: true, title: 'Ski Free' };
const o: Options = intermediate;  // OK
```

**타입 단언** - 단언에는 잉여 속성 체크가 없다. 단언보다 선언을 써야 할 또 하나의 이유다(Item 9).

```typescript
const o = { darkmode: true, title: 'MS Hearts' } as Options;  // OK
```

이런 체크를 원하지 않는다면 인덱스 시그니처로 추가 속성을 기대한다고 알릴 수 있다(이것이 데이터 모델링에 적절한지는 Item 16).

```typescript
interface Options {
  darkMode?: boolean;
  [otherOptions: string]: unknown;
}
const o: Options = { darkmode: true };  // OK
```

## 3. 약한 타입 체크 - 옵셔널 속성만 있는 타입

관련된 검사가 옵셔널 속성만 가진 "약한(weak)" 타입에도 일어난다.

```typescript
interface LineChartOptions {
  logscale?: boolean;
  invertedYAxis?: boolean;
  areaChart?: boolean;
}
function setOptions(options: LineChartOptions) { /* ... */ }

const opts = { logScale: true };
setOptions(opts);
//         ~~~~ Type '{ logScale: boolean; }' has no properties in common
//              with type 'LineChartOptions'
```

구조적 관점에서 `LineChartOptions`는 거의 모든 객체를 포함해야 한다. 약한 타입에 대해 타입스크립트는 **값 타입과 선언 타입에 공통 속성이 최소 하나는 있는지** 확인하는 검사를 추가한다. 잉여 속성 체크처럼 오타를 잘 잡고 엄밀히 구조적이지 않지만, **다른 점이 있다** - 약한 타입이 관련된 **모든** 할당 가능성 검사에서 일어난다. 중간 변수로 빼도 이 검사는 우회되지 않는다.

> **참고**: 타입스크립트에서 "약한 타입(weak type)"은 옵셔널 속성만 가진 인터페이스를 가리키는 기술 용어다. 타입의 품질과는 무관하며, 반대말이 "강한 타입"인 것도 아니다 - "강한 타입"은 타입스크립트에도 프로그래밍 언어 일반에도 특정한 의미가 없는 말이다.

## 4. 정리 - 두 검사를 구분하라

잉여 속성 체크는 구조적 타이핑 시스템이 허용했을 속성 이름의 오타와 실수를 잡는 효과적인 수단이며, `Options`처럼 옵셔널 필드를 가진 타입에서 특히 유용하다. 하지만 **적용 범위가 객체 리터럴에 국한**된다는 한계도 뚜렷하다. 이 한계를 인식하고, 잉여 속성 체크와 통상의 할당 가능성 검사를 구분하면 둘 모두의 멘털 모델을 세울 수 있다. 잉여 속성 체크가 버그를 잡고 새로운 설계 가능성을 열어 주는 구체적 사례는 Item 61에서 볼 수 있다.

> **핵심 통찰**: "왜 여기선 추가 속성이 에러인데 저기선 통과하지?"라는 혼란의 답은 언제나 같다 - 잉여 속성 체크는 타입 체크가 아니라, 객체 리터럴에만 적용되는 별도의 오타 방지 장치다. 타입스크립트의 타입은 여전히 닫혀 있지 않다.

## 기억해야 할 것들

- 객체 리터럴을 알려진 타입의 변수에 할당하거나 함수 인수로 넘기면 잉여 속성 체크가 일어난다.
- 잉여 속성 체크는 오류를 찾는 효과적인 방법이지만, 타입스크립트 타입 체커의 통상적인 구조적 할당 가능성 검사와는 별개다. 두 과정을 뒤섞으면 할당 가능성의 멘털 모델을 세우기 어렵다. 타입스크립트의 타입은 "닫혀" 있지 않다(Item 4).
- 잉여 속성 체크의 한계를 알아 두라: 중간 변수를 도입하면 검사가 사라진다.
- "약한 타입"은 옵셔널 속성만 가진 객체 타입이다. 이런 타입은 할당 가능성 검사에서 최소 하나의 공통 속성을 요구한다.
