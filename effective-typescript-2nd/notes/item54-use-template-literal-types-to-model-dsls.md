# Item 54: 템플릿 리터럴 타입으로 DSL과 문자열 간 관계 모델링하기 (Use Template Literal Types to Model DSLs and Relationships Between Strings)

## 핵심 질문

유한한 리터럴 유니온과 무한한 string 사이 - "특정 패턴을 따르는 문자열의 집합"은 어떻게 표현하는가?

Item 35는 내 코드에서 string 대신 더 정밀한 대안을 권했다. 하지만 세상에는 문자열이 넘쳐나서 완전히 피하기는 어렵다. 그럴 때 타입스크립트만의 도구가 있다 - 템플릿 리터럴 타입(*template literal type - 자바스크립트 템플릿 리터럴을 닮은 문법으로 문자열의 패턴과 관계를 표현하는 타입*)이다.

문자열 리터럴 타입의 유니온으로는 **유한한** 문자열 집합을, `string`으로는 **무한한 전체** 집합을 모델링할 수 있다. 템플릿 리터럴 타입은 그 사이 - 예를 들어 "pseudo로 시작하는 모든 문자열" - 를 모델링한다.

```typescript
type PseudoString = `pseudo${string}`;

const science: PseudoString = 'pseudoscience';  // OK
const alias: PseudoString = 'pseudonym';        // OK
const physics: PseudoString = 'physics';
//    ~~~~~~~ Type '"physics"' is not assignable to type '`pseudo${string}`'.
```

`string`처럼 도메인이 무한하지만(Item 7), 값들에 구조가 있다 - 전부 pseudo로 시작한다.

## 1. 구조화된 문자열 키 - data-* 속성

알려진 속성 집합은 요구하되 `data-`로 시작하는 다른 속성도 허용하고 싶다면? (DOM에서 흔한 패턴이다.)

```typescript
interface Checkbox {
  id: string;
  checked: boolean;
  [key: `data-${string}`]: unknown;
}

const check1: Checkbox = {
  id: 'subscribe',
  checked: true,
  value: 'yes',
  // ~~~~ Object literal may only specify known properties,
  //      and 'value' does not exist in type 'Checkbox'.
  'data-listIds': 'all-the-lists',  // OK
};
```

인덱스 타입을 그냥 `string`으로 했다면 잉여 속성 체크(Item 11)의 이점을 잃고, `data-` 접두사 없는 속성도 잘못 허용했을 것이다.

## 2. 제네릭·추론과의 결합 - querySelector 정밀화

템플릿 리터럴 타입의 진짜 힘은 **제네릭·타입 추론과 결합해 타입 간 관계를 포착**할 때 나온다. DOM의 `querySelector`는 태그로 조회하면 이미 똑똑하게 구체적 타입을 준다.

```typescript
const img = document.querySelector('img');
//    ^? const img: HTMLImageElement | null
```

하지만 특정 ID까지 붙이면 그냥 `Element`다.

```typescript
const img = document.querySelector('img#spectacular-sunset');
//    ^? const img: Element | null
img?.src
//   ~~~ Property 'src' does not exist on type 'Element'.
```

`lib.dom.d.ts`에는 태그 이름→타입 매핑 `HTMLElementTagNameMap`이 있다. 템플릿 리터럴 타입으로 `tag#id` 케이스의 오버로드를 추가할 수 있다.

```typescript
type HTMLTag = keyof HTMLElementTagNameMap;
declare global {
  interface ParentNode {
    querySelector<
      TagName extends HTMLTag
    >(
      selector: `${TagName}#${string}`
    ): HTMLElementTagNameMap[TagName] | null;
  }
}

const img = document.querySelector('img#spectacular-sunset');
//    ^? const img: HTMLImageElement | null
img?.src  // OK
```

그런데 과녁을 살짝 빗나갔다.

```typescript
const img = document.querySelector('div#container img');
//    ^? const img: HTMLDivElement | null   - 실제로는 img인데!
```

CSS 셀렉터의 공백은 "자손"을 뜻한다. 우리의 `${TagName}#${string}`이 "div" + "#" + "container img"로 매칭된 것 - 정밀을 노리다 Item 40의 조언(부정확보다 덜 정밀)을 어겼다. 템플릿 리터럴 타입으로 CSS 셀렉터 파서 전체를 만들 수도 있겠지만, 덜 야심 찬 처리는 **특수 의미 문자를 막는 오버로드**를 하나 더 두는 것이다.

```typescript
type CSSSpecialChars = ' ' | '>' | '+' | '~' | '||' | ',';
type HTMLTag = keyof HTMLElementTagNameMap;

declare global {
  interface ParentNode {
    // 탈출구
    querySelector(
      selector: `${HTMLTag}#${string}${CSSSpecialChars}${string}`
    ): Element | null;

    // 이전과 동일
    querySelector<
      TagName extends HTMLTag
    >(
      selector: `${TagName}#${string}`
    ): HTMLElementTagNameMap[TagName] | null;
  }
}

const img = document.querySelector('img#spectacular-sunset');
//    ^? const img: HTMLImageElement | null
const img2 = document.querySelector('div#container img');
//    ^? const img2: Element | null   - 부정확 대신 덜 정밀
```

## 3. infer와 재귀 - snake_case → camelCase

템플릿 리터럴 타입은 조건부 타입과 결합해 CSS 셀렉터 같은 DSL(*Domain-Specific Language - 특정 영역 전용 미니 언어*)의 파서를 구현하는 데 자주 쓰인다. snake_case 객체의 키를 camelCase로 바꾸는 `objectToCamel`의 정밀한 타입을 만들어 보자.

```typescript
// 예: foo_bar -> fooBar
function camelCase(term: string) {
  return term.replace(/_([a-z])/g, m => m[1].toUpperCase());
}

function objectToCamel<T extends object>(obj: T) {
  const out: any = {};
  for (const [k, v] of Object.entries(obj)) {
    out[camelCase(k)] = v;
  }
  return out;
}
```

1단계 - 타입 수준 헬퍼. 조건부 타입 안의 `infer` 키워드로 밑줄 앞뒤 부분을 추출한다.

```typescript
type ToCamelOnce<S extends string> =
  S extends `${infer Head}_${infer Tail}`
    ? `${Head}${Capitalize<Tail>}`
    : S;

type T = ToCamelOnce<'foo_bar'>;  // 타입은 "fooBar"
```

S가 `"foo_bar"`면 `Head`는 `"foo"`, `Tail`은 `"bar"`가 되고, 매칭되면 밑줄 없이 Tail의 첫 글자를 대문자화(내장 헬퍼 `Capitalize`)한 새 문자열을 만든다. `"foo_bar_baz"`처럼 밑줄이 여러 개인 문자열은 **재귀**로 처리한다.

```typescript
type ToCamel<S extends string> =
  S extends `${infer Head}_${infer Tail}`
    ? `${Head}${Capitalize<ToCamel<Tail>>}`
    : S;

type T0 = ToCamel<'foo'>;          // "foo"
type T1 = ToCamel<'foo_bar'>;      // "fooBar"
type T2 = ToCamel<'foo_bar_baz'>;  // "fooBarBaz"
```

2단계 - 매핑된 타입(Item 15)의 `as` 절로 키를 다시 쓴다.

```typescript
type ObjectToCamel<T extends object> = {
  [K in keyof T as ToCamel<K & string>]: T[K]
};

function objectToCamel<T extends object>(obj: T): ObjectToCamel<T> {
  // ... 이전과 동일 ...
}

const snake = {foo_bar: 12};
//    ^? const snake: { foo_bar: number; }
const camel = objectToCamel(snake);
//    ^? const camel: ObjectToCamel<{ foo_bar: number; }>
//       ({ fooBar: number; }와 동등)
const val = camel.fooBar;
//    ^? const val: number
const val2 = camel.foo_bar;
//                 ~~~~~~~ Property 'foo_bar' does not exist on type
//                         '{ fooBar: number; }'. Did you mean 'fooBar'?
```

> **핵심 통찰**: 이 정밀한 `objectToCamel` 타입은 "화려한" 타입스크립트 기능이 개발자를 이롭게 하는 훌륭한 예다. 사용자는 템플릿 리터럴·조건부·매핑된 타입을 하나도 몰라도 더 정밀한 타입의 혜택을 누린다 - 타입스크립트가 이 코드를 이해한다는 경험만 남는다.

(camel 타입의 표시가 이상적이지 않은 문제는 Item 56에서 개선한다.)

## 기억해야 할 것들

- 템플릿 리터럴 타입으로 string 타입의 구조화된 부분집합과 DSL을 모델링하라.
- 템플릿 리터럴 타입을 매핑된 타입·조건부 타입과 결합해 타입 간의 미묘한 관계를 포착하라.
- 부정확한 타입의 선을 넘지 않도록 주의하라. 화려한 언어 기능의 지식을 요구하지 않으면서 개발자 경험을 개선하는 사용을 추구하라.
