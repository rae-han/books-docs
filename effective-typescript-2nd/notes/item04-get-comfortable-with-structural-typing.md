# Item 4: 구조적 타이핑에 익숙해지기 (Get Comfortable with Structural Typing)

## 핵심 질문

타입 체커가 이해하는 타입이 왜 내 생각보다 넓은가? 타입의 개방성은 언제 독이 되고, 언제 약이 되는가?

자바스크립트는 본질적으로 덕 타이핑(*duck typing - "오리처럼 걷고 오리처럼 말하면 오리다" — 값이 필요한 속성을 다 갖고 있으면 어떻게 만들어졌는지 따지지 않는 방식*) 기반이다. 타입스크립트는 이를 구조적 타입 시스템(*structural type system - 이름이 아니라 구조(속성 구성)로 타입 호환성을 판정하는 시스템*)으로 모델링한다. 그런데 타입 체커가 이해하는 타입이 내 머릿속 타입보다 **넓을** 수 있어서 놀라운 결과가 생기곤 한다. 구조적 타이핑을 제대로 이해하면 에러와 비(非)에러를 해석할 수 있게 되고, 더 견고한 코드를 쓸 수 있다.

## 1. 선언한 적 없는 호환성

물리 라이브러리의 2D 벡터와 길이 계산 함수:

```typescript
interface Vector2D {
  x: number;
  y: number;
}
function calculateLength(v: Vector2D) {
  return Math.sqrt(v.x ** 2 + v.y ** 2);
}

interface NamedVector {
  name: string;
  x: number;
  y: number;
}
const v: NamedVector = { x: 3, y: 4, name: 'Pythagoras' };
calculateLength(v);  // OK — 결과는 5
```

`Vector2D`와 `NamedVector`의 관계를 선언한 적이 없고 `NamedVector`용 구현을 따로 쓰지도 않았는데 호출이 허용된다. 타입스크립트의 타입 시스템은 자바스크립트의 런타임 동작을 모델링하므로(Item 1), `NamedVector`의 **구조**가 `Vector2D`와 호환되면 그대로 통과시킨다. 이것이 "구조적 타이핑"이라는 이름의 유래다.

## 2. 구조적 타이핑이 일으키는 문제

같은 관용이 역효과를 낼 때가 있다. 3D 벡터와 정규화(길이를 1로) 함수를 추가하면:

```typescript
interface Vector3D {
  x: number;
  y: number;
  z: number;
}
function normalize(v: Vector3D) {
  const length = calculateLength(v);  // 2D 함수에 3D 벡터를 전달 — 에러 없음!
  return {
    x: v.x / length,
    y: v.y / length,
    z: v.z / length,
  };
}

normalize({x: 3, y: 4, z: 5});
// { x: 0.6, y: 0.8, z: 1 } — 길이가 1이 아니라 약 1.4
```

`calculateLength`는 2D 벡터용인데 3D 벡터로 호출해도 타입 체커가 잡지 않는다. `{x, y, z}` 객체는 `Vector2D`와 구조적으로 호환되기 때문이다. `z`가 정규화에서 무시되는 버그가 조용히 지나간다. (이것을 에러로 만들고 싶다면 Item 63의 옵셔널 `never` 속성 트릭이나 Item 64의 브랜드 기법이 있다.)

함수를 쓸 때는 매개변수가 선언한 속성만 갖고 있으리라 상상하기 쉽다. 그런 타입을 "닫힌(closed)"·"봉인된(sealed)"·"정확한(precise)" 타입이라 부르는데, **타입스크립트 타입 시스템에서는 표현할 수 없다. 좋든 싫든 타입은 "열려(open)" 있다.**

열린 타입은 이런 놀라움도 만든다.

```typescript
function calculateLengthL1(v: Vector3D) {
  let length = 0;
  for (const axis of Object.keys(v)) {
    const coord = v[axis];
    //            ~~~~~~~ Element implicitly has an 'any' type because ...
    //                    'string' can't be used to index type 'Vector3D'
    length += Math.abs(coord);
  }
  return length;
}
```

`axis`는 `v`의 키니까 `"x" | "y" | "z"`이고 값은 전부 `number` 아닌가? 이 에러는 오탐이 아니다 — 그 논리는 `Vector3D`가 봉인되어 있다고 가정하지만, 실제로는 그렇지 않다.

```typescript
const vec3D = {x: 3, y: 4, z: 1, address: '123 Broadway'};
calculateLengthL1(vec3D);  // OK — NaN을 반환
```

`v`는 어떤 속성이든 가질 수 있으므로 `axis`의 타입은 `string`이고, `v[axis]`가 `number`라고 믿을 근거가 없다. (여기서 `vec3D`를 변수로 거친 것은 잉여 속성 체크를 피하기 위해서다 — Item 11.) 객체 순회의 올바른 타이핑은 Item 60에서 다루며, 이 경우에는 루프 없는 구현이 낫다.

```typescript
function calculateLengthL1(v: Vector3D) {
  return Math.abs(v.x) + Math.abs(v.y) + Math.abs(v.z);
}
```

## 3. 클래스도 구조적으로 비교된다

할당 가능성 판정에서는 클래스도 구조적으로 비교된다.

```typescript
class SmallNumContainer {
  num: number;
  constructor(num: number) {
    if (num < 0 || num >= 10) {
      throw new Error(`You gave me ${num} but I want something 0-9.`);
    }
    this.num = num;
  }
}

const a = new SmallNumContainer(5);
const b: SmallNumContainer = { num: 2024 };  // OK!
```

`b`는 `num: number` 속성을 갖고 있으므로 구조가 맞아서 할당된다. 생성자의 검증 로직이 실행됐다고 가정하는 함수가 있다면 문제가 된다. 속성과 메서드가 많은 클래스에서는 우연히 일어나기 어렵지만, C++이나 자바와는 분명히 다르다 — 그 언어들에서는 `SmallNumContainer` 타입 매개변수 선언이 "그 클래스 또는 서브클래스의 인스턴스이며 생성자가 실행됐음"을 보장한다.

## 4. 구조적 타이핑은 테스트에 유리하다

DB 쿼리를 실행해 결과를 가공하는 함수가 있다고 하자.

```typescript
interface Author {
  first: string;
  last: string;
}
function getAuthors(database: PostgresDB): Author[] {
  const authorRows = database.runQuery(`SELECT first, last FROM authors`);
  return authorRows.map(row => ({first: row[0], last: row[1]}));
}
```

`PostgresDB`를 모킹할 수도 있지만, 구조적 타이핑을 이용해 **더 좁은 인터페이스를 정의하는 편이 간단하다**.

```typescript
interface DB {
  runQuery: (sql: string) => any[];
}
function getAuthors(database: DB): Author[] {
  const authorRows = database.runQuery(`SELECT first, last FROM authors`);
  return authorRows.map(row => ({first: row[0], last: row[1]}));
}
```

프로덕션에서는 여전히 `PostgresDB`를 넘길 수 있다 — `runQuery` 메서드가 있으니 구조적으로 호환되고, `implements DB`라고 선언할 필요도 없다. 테스트에서는 더 단순한 객체를 넘기면 된다.

```typescript
test('getAuthors', () => {
  const authors = getAuthors({
    runQuery(sql: string) {
      return [['Toni', 'Morrison'], ['Maya', 'Angelou']];
    }
  });
  expect(authors).toEqual([
    {first: 'Toni', last: 'Morrison'},
    {first: 'Maya', last: 'Angelou'}
  ]);
});
```

타입스크립트가 테스트용 DB가 인터페이스에 부합하는지 검증해 준다. 테스트가 프로덕션 DB에 대해 아무것도 몰라도 되고 모킹 라이브러리도 필요 없다. 추상화(`DB`)를 도입해 로직과 테스트를 특정 구현(`PostgresDB`)의 세부 사항에서 해방시킨 것이다. 구조적 타이핑은 라이브러리 간 의존성을 깔끔하게 끊는 데에도 쓰인다(Item 70).

> **핵심 통찰**: 구조적 타이핑은 양날의 검이다. 선언 없는 호환성 덕에 유연한 코드(테스트 더블, 의존성 절단)가 가능하지만, 타입이 "봉인"되어 있다고 가정하는 순간 버그가 스며든다. 타입 체커의 이해가 내 상상보다 넓다는 사실을 항상 기억하라.

## 기억해야 할 것들

- 자바스크립트는 덕 타이핑 기반이고 타입스크립트는 이를 구조적 타이핑으로 모델링한다. 인터페이스에 할당 가능한 값은 타입 선언에 명시된 것 외의 속성을 가질 수 있다. 타입은 "봉인"되어 있지 않다.
- 클래스 역시 구조적 타이핑 규칙을 따른다. 기대한 클래스의 인스턴스가 아닐 수 있다!
- 구조적 타이핑을 유닛 테스트에 활용하라.
