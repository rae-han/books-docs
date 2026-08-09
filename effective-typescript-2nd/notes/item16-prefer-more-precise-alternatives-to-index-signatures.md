# Item 16: 인덱스 시그니처보다 더 정확한 대안 사용하기 (Prefer More Precise Alternatives to Index Signatures)

## 핵심 질문

`{[key: string]: string}` 같은 인덱스 시그니처는 무엇을 포기하게 만드는가? 동적 데이터는 무엇으로 모델링해야 하는가?

자바스크립트 최고의 기능 중 하나는 객체를 만드는 편리한 문법이다. 객체는 string(또는 symbol) 키를 어떤 타입의 값에든 매핑한다. 타입스크립트에서는 인덱스 시그니처(*index signature - 임의 키와 값의 타입을 지정하는 `[key: K]: V` 구문*)로 이런 유연한 매핑을 표현할 수 있다.

```typescript
type Rocket = {[property: string]: string};
const rocket: Rocket = {
  name: 'Falcon 9',
  variant: 'v1.0',
  thrust: '4,940 kN',
};  // OK
```

`[property: string]: string`은 세 가지를 지정한다.

1. **키의 이름**(`property`): 순전히 문서용이다. 타입 체커는 전혀 사용하지 않는다.
2. **키의 타입**: `string | number | symbol`(일명 `PropertyKey`)의 서브타입이어야 한다. 보통 `string`이거나 문자열 리터럴 유니온 같은 `string`의 서브타입이다. `number` 인덱스는 피하는 것이 좋고(Item 17), `symbol`은 애플리케이션 코드에서 드물다.
3. **값의 타입**: 무엇이든 된다.

## 1. 인덱스 시그니처의 문제

위 코드는 타입 체크를 통과하지만 단점이 여럿이다.

- **잘못된 키를 포함해 아무 키나 허용한다**: `name` 대신 `Name`을 썼어도 유효한 `Rocket`이다.
- **특정 키의 존재를 요구하지 않는다**: `{}`도 유효한 `Rocket`이다.
- **키마다 다른 타입을 가질 수 없다**: `thrust`는 string이 아니라 number이고 싶을 수 있다.
- **언어 서비스가 도움을 줄 수 없다**: `name:`을 입력해도 키가 무엇이든 될 수 있으므로 자동완성이 없다.

요컨대 인덱스 시그니처는 정확하지 않으며, 거의 언제나 더 나은 대안이 있다. 이 경우 `Rocket`은 그냥 인터페이스면 된다.

```typescript
interface Rocket {
  name: string;
  variant: string;
  thrust_kN: number;
}
const falconHeavy: Rocket = {
  name: 'Falcon Heavy',
  variant: 'v1',
  thrust_kN: 15200,
};
```

이제 `thrust_kN`은 number이고 타입스크립트가 필수 필드의 존재를 검사하며, 자동완성·정의로 이동·이름 변경 같은 언어 서비스가 전부 살아난다.

## 2. 진짜 동적 데이터 - 그리고 Map이라는 더 나은 답

그럼 인덱스 시그니처는 어디에 쓰나? 역사적으로는 **진짜 동적인 데이터**를 모델링하는 최선의 방법이었다. 예를 들어 CSV 파일 - 헤더 행이 있고 데이터 행을 열 이름→값 객체로 표현하고 싶을 때다.

```typescript
function parseCSV(input: string): {[columnName: string]: string}[] {
  const lines = input.split('\n');
  const [headerLine, ...rows] = lines;
  const headers = headerLine.split(',');
  return rows.map(rowStr => {
    const row: {[columnName: string]: string} = {};
    rowStr.split(',').forEach((cell, i) => {
      row[headers[i]] = cell;
    });
    return row;
  });
}
```

이런 일반적 상황에서는 열 이름을 미리 알 수 없으니 더 정밀한 타입이 불가능하다. 특정 문맥에서 사용자가 열을 더 잘 안다면 단언으로 구체화할 수 있다.

```typescript
interface ProductRow {
  productId: string;
  name: string;
  price: string;
}
declare let csvData: string;
const products = parseCSV(csvData) as unknown[] as ProductRow[];
```

물론 런타임의 열이 기대와 일치한다는 보장은 없다. 값 타입을 `string | undefined`로 바꾸거나 `noUncheckedIndexedAccess` 컴파일러 옵션(Item 48)으로 대비할 수 있다.

하지만 동적 데이터를 모델링하는 **더 나은 방법은 `Map` 타입**(연관 배열)이다.

```typescript
function parseCSVMap(input: string): Map<string, string>[] {
  const lines = input.split('\n');
  const [headerLine, ...rows] = lines;
  const headers = headerLine.split(',');
  return rows.map(rowStr => {
    const row = new Map<string, string>();
    rowStr.split(',').forEach((cell, i) => {
      row.set(headers[i], cell);
    });
    return row;
  });
}
```

필드는 `get` 메서드로 접근해야 하고, 결과에 항상 `undefined` 가능성이 포함된다.

```typescript
const rockets = parseCSVMap(csvData);
const superHeavy = rockets[2];
const thrust_kN = superHeavy.get('thrust_kN');  // 74,500
//    ^? const thrust_kN: string | undefined
```

Map에서 객체 타입을 뽑아내려면 파싱 코드를 써야 한다.

```typescript
function parseRocket(map: Map<string, string>): Rocket {
  const name = map.get('name');
  const variant = map.get('variant');
  const thrust_kN = Number(map.get('thrust_kN'));
  if (!name || !variant || isNaN(thrust_kN)) {
    throw new Error(`Invalid rocket: ${map}`);
  }
  return {name, variant, thrust_kN};
}
const rockets = parseCSVMap(csvData).map(parseRocket);
//    ^? const rockets: Rocket[]
```

번거롭게 느껴질 수 있지만 데이터가 실제로 기대한 형태인지 보장해 준다 - 에러가 **데이터를 로드하는 시점**에 잡히지, 한참 뒤 사용하는 시점에 터지지 않는다. 넓은 타입(`Map<string, string>`)에 데이터 검증을 수행해 더 구체적인 타입(`Rocket`)을 얻는 이 패턴은 타입스크립트에서 흔하다(체계적인 런타임 타입 검증은 Item 74). 덤으로 Map은 프로토타입 체인과 얽힌 유명한 함정들도 우회한다.

## 3. 필드 집합이 제한적이라면 - 옵셔널 필드, 유니온, Record

가능한 필드의 집합이 제한적이라면 인덱스 시그니처로 모델링하지 마라. 키가 A, B, C, D 중 몇 개인지 모를 뿐이라면:

```typescript
interface Row1 { [column: string]: number }  // 너무 넓다
interface Row2 { a: number; b?: number; c?: number; d?: number }  // 낫다
type Row3 =
  | { a: number; }
  | { a: number; b: number; }
  | { a: number; b: number; c: number; }
  | { a: number; b: number; c: number; d: number };  // 이것도 낫다
```

마지막 형태가 가장 정확하지만 다루기는 덜 편할 수 있다(유효하지 않은 상태를 금지하는 타입 설계는 Item 29).

인덱스 시그니처의 문제가 "`string`이 너무 넓다"는 것이라면 **`Record`** 를 쓸 수 있다. 키 타입에 유연성을 주는 제네릭 타입으로, `string`의 부분집합을 넘길 수 있다.

```typescript
type Vec3D = Record<'x' | 'y' | 'z', number>;
//   ^? type Vec3D = {
//        x: number;
//        y: number;
//        z: number;
//      }
```

`Record`는 매핑된 타입(Item 15)의 내장 래퍼다.

## 4. 잉여 속성 체크 끄기 용도

인덱스 타입으로 잉여 속성 체크(Item 11)를 끌 수도 있다. `ButtonProps`에 알려진 속성 몇 개를 정의하되 다른 속성도 허용하고 싶다면:

```typescript
interface ButtonProps {
  title: string;
  onClick: () => void;
  [otherProps: string]: unknown;
}

renderAButton({
  title: 'Roll the dice',
  onClick: () => alert(1 + Math.floor(20 * Math.random())),
  theme: 'Solarized',  // OK - 인덱스 시그니처가 없었다면 잉여 속성 에러
});
```

중요한 것은 `title`과 `onClick`이 여전히 전과 같은 타입을 유지한다는 점 - `title`에 number를 넘기면 여전히 타입 에러다. 추가 속성이 특정 패턴을 따르도록 제약할 수도 있다 - 예를 들어 `data-`로 시작하는 속성만 허용하는 웹 컴포넌트는 인덱스 시그니처와 템플릿 리터럴 타입으로 모델링한다(Item 54).

> **핵심 통찰**: 데이터 타입에 인덱스 시그니처를 추가하기 전에 두 번 생각하라. 더 정확한 대안은 없는가? 인덱스 없는 인터페이스로 되는가? Map은? 매핑된 타입은? 다 안 되면 최소한 키의 타입이라도 제약할 수 없는가?

## 기억해야 할 것들

- 인덱스 시그니처의 단점을 이해하라: `any`와 매우 비슷하게 타입 안전성을 갉아먹고 언어 서비스의 가치를 떨어뜨린다.
- 가능하면 인덱스 시그니처보다 정확한 타입을 선호하라: 인터페이스, `Map`, `Record`, 매핑된 타입, 또는 키 공간을 제약한 인덱스 시그니처.
