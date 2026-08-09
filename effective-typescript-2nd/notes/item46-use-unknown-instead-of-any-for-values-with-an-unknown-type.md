# Item 46: 타입을 모르는 값에는 any 대신 unknown 사용하기 (Use unknown Instead of any for Values with an Unknown Type)

## 핵심 질문

any는 타입 시스템의 어디가 고장 나 있는가? unknown은 어떻게 같은 역할을 타입 안전하게 해내는가?

YAML 파서를 쓴다고 하자(YAML은 JSON과 같은 값 집합을 표현하지만 문법은 JSON의 상위집합이다). `parseYAML`의 반환 타입은? `JSON.parse`처럼 any로 하고 싶어진다.

```typescript
function parseYAML(yaml: string): any {
  // ...
}
```

하지만 이는 "전염되는" any를 피하라는 — 특히 함수에서 반환하지 말라는 — Item 43의 조언에 정면으로 반한다. (`JSON.parse`가 any를 반환하지 않게 "고치는" 법은 Item 71.) 이상적으로는 사용자가 결과를 즉시 다른 타입에 할당하길 바라지만, 타입 구문이 없으면 `book` 변수는 조용히 any가 되어 쓰이는 곳마다 타입 체크를 무력화한다.

```typescript
const book = parseYAML(`
  name: Jane Eyre
  author: Charlotte Brontë
`);
console.log(book.title);  // 에러 없음 — 런타임에 "undefined" 출력
book('read');             // 에러 없음 — 런타임에 "book is not a function" 예외
```

더 안전한 대안은 `unknown`을 반환하는 것이다.

```typescript
function safeParseYAML(yaml: string): unknown {
  return parseYAML(yaml);
}

const book = safeParseYAML(`
  name: The Tenant of Wildfell Hall
  author: Anne Brontë
`);
console.log(book.title);
//          ~~~~ 'book' is of type 'unknown'
book("read");
// Error: 'book' is of type 'unknown'
```

## 1. any는 왜 고장인가 — 할당 가능성의 관점

any의 힘과 위험은 두 성질에서 온다.

1. **모든 타입이 any에 할당 가능하다.**
2. **any가 모든 타입에 할당 가능하다.**

"타입 = 값의 집합"(Item 7)으로 보면 첫 성질은 any가 모든 타입의 **슈퍼타입**, 둘째는 **서브타입**이라는 뜻이다. 이상하다! 한 집합이 다른 모든 집합의 부분집합이면서 동시에 상위집합일 수는 없으므로, **any는 타입 시스템에 들어맞지 않는다.** 그것이 any의 힘의 원천이자 문제의 이유다 — 타입 체커는 집합 기반이라 any를 쓰면 사실상 꺼진다.

`unknown`은 타입 시스템에 들어맞는 any의 대안이다. 첫 성질(어떤 타입이든 unknown에 할당 가능)은 갖되 둘째 성질은 없다(unknown은 unknown과, 물론 any에만 할당 가능). 계층 꼭대기에 있어 **탑 타입**이라 부른다. `never`는 정반대다 — 둘째 성질(어느 타입에나 할당 가능)은 갖되 첫째는 없다(어떤 타입도 never에 할당 불가). **바텀 타입**이다.

unknown 값에 속성 접근을 하거나 호출하거나 산술을 하면 에러다. unknown으로는 거의 아무것도 할 수 없는데, **바로 그게 요점이다.** unknown 에러들은 더 구체적인 타입을 고르라고 종용한다.

```typescript
const book = safeParseYAML(`
  name: Villette
  author: Charlotte Brontë
`) as Book;
console.log(book.title);
//               ~~~~~ Property 'title' does not exist on type 'Book'
book('read');
// Error: This expression is not callable
```

이 에러들이 훨씬 말이 된다. unknown은 다른 타입에 할당할 수 없으니 타입 단언이 필요한데, 이것은 **적절한** 단언이기도 하다 — 결과 객체의 타입에 대해 우리가 타입스크립트보다 정말로 더 알고 있으니까.

## 2. unknown이 어울리는 자리

**값이 있다는 것은 알지만 타입은 모르거나 신경 쓰지 않을 때** unknown이 적절하다.

```typescript
// GeoJSON 명세에서 feature의 properties는 JSON 직렬화 가능한 아무것이나
interface Feature {
  id?: string | number;
  geometry: Geometry;
  properties: unknown;
}

// 요소 타입은 아무래도 좋은 함수
function isSmallArray(arr: readonly unknown[]): boolean {
  return arr.length < 10;
}
```

## 3. unknown에서 구체적 타입으로

타입 단언만이 길은 아니다. `instanceof` 체크로도 된다.

```typescript
function processValue(value: unknown) {
  if (value instanceof Date) {
    value
    // ^? (parameter) value: Date
  }
}
```

사용자 정의 타입 가드로도:

```typescript
function isBook(value: unknown): value is Book {
  return (
    typeof(value) === 'object' && value !== null &&
    'name' in value && 'author' in value
  );
}

function processValue(value: unknown) {
  if (isBook(value)) {
    value;
    // ^? (parameter) value: Book
  }
}
```

unknown을 좁히는 데 타입스크립트는 꽤 많은 증명을 요구한다 — `in` 체크의 에러를 피하려면 먼저 값이 객체 타입이고 null이 아님을 보여야 한다(`typeof null === 'object'`이므로). 여느 타입 가드처럼 이것도 타입 단언보다 안전하지는 않다는 것을 기억하라 — 가드를 올바르게 구현했는지, 타입과 동기화됐는지 검사해 주는 것은 없다(해결책은 Item 74).

## 4. 유사품들 — 반환 전용 제네릭, 이중 단언, {}·object

**반환 전용 타입 매개변수**를 unknown 대신 쓰는 코드를 볼 수 있다.

```typescript
function safeParseYAML<T>(yaml: string): T {
  return parseYAML(yaml);
}
```

일반적으로 나쁜 스타일로 여겨진다. 타입 단언과 달라 보이지만 안전하지도 않고 기능적으로 같다. 그냥 unknown을 반환해서 사용자가 단언하거나 좁히도록 강제하는 것이 낫다(불필요한 제네릭은 Item 51의 주제).

**이중 단언**에서도 any 대신 unknown을 쓸 수 있다.

```typescript
declare const foo: Foo;
let barAny = foo as any as Bar;
let barUnk = foo as unknown as Bar;
```

기능적으로 동등하지만 unknown 버전은 `as any`를 봤을 때의 본능적 거부감을 일으키지 않는다.

**{}·Object·object**를 unknown 비슷하게 쓰는 코드도 있다. 넓은 타입들이지만 unknown보다 약간 좁다.

- `{}` 타입: null과 undefined를 **제외한** 모든 값
- `Object` 타입(대문자 O): `{}`와 거의 같다. 문자열·숫자·불리언 등 원시 값도 할당 가능
- `object` 타입(소문자 o): 모든 **비원시** 타입. true·12·"foo"는 안 되고 객체·배열·함수는 된다

"null과 undefined만 빼고 다 허용"을 정말로 원하는 경우는 드물므로, 일반적으로 `{}`·`Object`보다 unknown이 낫다.

## 기억해야 할 것들

- unknown은 any의 타입 안전한 대안이다. 값이 있다는 것은 알지만 타입을 모르거나 신경 쓰지 않을 때 사용하라.
- 사용자가 타입 단언이나 다른 형태의 좁히기를 쓰도록 강제하려면 unknown을 사용하라.
- 거짓 안도감을 만드는 반환 전용 타입 매개변수를 피하라.
- `{}`·`object`·`unknown`의 차이를 이해하라.
