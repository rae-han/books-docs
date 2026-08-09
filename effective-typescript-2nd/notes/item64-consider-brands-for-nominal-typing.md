# Item 64: 명목적 타이핑을 위한 브랜드 고려하기 (Consider Brands for Nominal Typing)

## 핵심 질문

구조가 같아도 의미가 다른 값들 - 절대 경로, 단위 있는 숫자, 정렬된 리스트 - 을 타입으로 구별하려면?

Item 4에서 봤듯 구조적 타이핑은 가끔 놀라운 결과를 낳는다.

```typescript
interface Vector2D {
  x: number;
  y: number;
}
function calculateNorm(p: Vector2D) {
  return Math.sqrt(p.x ** 2 + p.y ** 2);
}

calculateNorm({x: 3, y: 4});  // OK - 결과 5
const vec3D = {x: 3, y: 4, z: 1};
calculateNorm(vec3D);          // OK! 결과 역시 5
```

`calculateNorm`이 3D 벡터를 거부하게 하고 싶다면? 구조적 타이핑 모델에는 반하지만 수학적으로는 확실히 더 옳다. Item 63의 옵셔널 never는 순수 타입 수준 해법이었다. 런타임에 값에 "태그"를 붙여 할당을 막을 수도 있다(`type: '2d'` - 태그된 유니온, Item 34). 하지만 태그에는 단점이 있다 - 런타임 오버헤드가 생기고, **명시적 태그는 객체 타입에만 붙일 수 있다.**

흥미롭게도 **타입 시스템 안에서만 움직이면서** 명시적 태그의 이점 다수를 얻을 수 있다. 이 맥락의 태그를 브랜드(*brand - 낙인. 코카콜라가 아니라 소에 찍는 쪽을 생각하라*)라 부른다. 타입 전용 접근이라 런타임 오버헤드가 없고, 속성을 붙일 수 없는 `string`·`number` 같은 내장 타입에도 브랜드를 찍을 수 있다. 이것이 명목적 타이핑(*nominal typing - 값이 올바른 형태라서가 아니라 그 타입이라고 말했기 때문에 그 타입인 방식*)이다.

## 1. 절대 경로 - string 브랜딩

파일시스템에서 (상대가 아닌) 절대 경로를 요구하는 함수가 있다면? 런타임 체크는 쉽지만("/"로 시작하나?) 타입 시스템에서는 쉽지 않다. 브랜드 접근:

```typescript
type AbsolutePath = string & {_brand: 'abs'};

function listAbsolutePath(path: AbsolutePath) {
  // ...
}
function isAbsolutePath(path: string): path is AbsolutePath {
  return path.startsWith('/');
}
```

string이면서 `_brand` 속성을 가진 객체는 만들 수 없다 - 순전히 타입 시스템과의 게임이다(string에 속성을 붙일 수 있다고 생각한다면 Item 10을 보라). 절대일 수도 상대일 수도 있는 경로는 타입 가드로 체크하면 타입이 정제된다.

```typescript
function f(path: string) {
  if (isAbsolutePath(path)) {
    listAbsolutePath(path);
  }
  listAbsolutePath(path);
  //               ~~~~ Argument of type 'string' is not assignable to
  //                    parameter of type 'AbsolutePath'
}
```

어떤 함수가 절대/상대 경로를 기대하는지, 각 변수가 어떤 경로를 담는지에 대한 유용한 문서가 된다. 철통같은 보장은 아니다 - `path as AbsolutePath`는 어떤 string에나 성공한다. 하지만 그런 단언을 피한다면 `AbsolutePath`를 얻는 길은 **받거나, 검사하거나**뿐이다. 정확히 원하는 것이다.

## 2. 단위 있는 숫자 - number 브랜딩

```typescript
type Meters = number & {_brand: 'meters'};
type Seconds = number & {_brand: 'seconds'};

const meters = (m: number) => m as Meters;
const seconds = (s: number) => s as Seconds;

const oneKm = meters(1000);
//    ^? const oneKm: Meters
const oneMin = seconds(60);
//    ^? const oneMin: Seconds
```

실전에서는 어색할 수 있다 - **산술 연산이 브랜드를 잊게 만든다.**

```typescript
const tenKm = oneKm * 10;
//    ^? const tenKm: number
const v = oneKm / oneMin;
//    ^? const v: number
```

그래도 단위가 섞인 숫자가 많은 코드라면 숫자 매개변수의 기대 타입을 문서화하는 매력적인 접근일 수 있다.

## 3. 브랜딩 기법들

- **객체 타입의 속성**: 위에서 본 `& {_brand: '...'}`
- **문자열 기반 enum과의 인터섹션**: 문자열 enum은 명목적으로 타이핑된다(Item 72)
- **private 필드**: 클래스 브랜딩에 쓰인다
- **unique symbol**: 흔한 기법 하나.

```typescript
declare const brand: unique symbol;
export type Meters = number & {[brand]: 'meters'};
```

brand 심벌이 export되지 않으므로 사용자는 `Meters` 값을 얻으려면 타입 단언이나 헬퍼 함수를 써야 한다 - 브랜드를 직접 쓰거나 호환되는 다른 타입을 만들 수 없다.

## 4. 타입 시스템으로 표현할 수 없는 성질 - SortedList

브랜드는 타입 시스템 안에서 표현할 수 없는 많은 성질을 모델링할 수 있다. 이진 탐색을 보자.

```typescript
function binarySearch<T>(xs: T[], x: T): boolean {
  let low = 0, high = xs.length - 1;
  while (high >= low) {
    const mid = low + Math.floor((high - low) / 2);
    const v = xs[mid];
    if (v === x) return true;
    [low, high] = x > v ? [mid + 1, high] : [low, mid - 1];
  }
  return false;
}
```

리스트가 정렬되어 있으면 동작하지만 아니면 거짓 음성이 나온다. "정렬된 리스트"는 타입 시스템으로 표현할 수 없다 - 하지만 브랜드는 만들 수 있다.

```typescript
type SortedList<T> = T[] & {_brand: 'sorted'};

function isSorted<T>(xs: T[]): xs is SortedList<T> {
  for (let i = 0; i < xs.length - 1; i++) {
    if (xs[i] > xs[i + 1]) {
      return false;
    }
  }
  return true;
}

function binarySearch<T>(xs: SortedList<T>, x: T): boolean {
  // ...
}
```

이 `binarySearch`를 호출하려면 `SortedList`를 **받거나**(정렬됐다는 증명을 갖고 있거나) `isSorted`로 **직접 증명**해야 한다. 선형 스캔이 근사하진 않지만 최소한 안전하다!

> **핵심 통찰**: 이것은 타입 체커 일반에 대한 유용한 관점이다. 객체의 메서드를 호출하려면 non-null 객체를 받거나 조건문으로 non-null임을 직접 증명해야 한다 - SortedList를 얻는 두 가지 길과 정확히 유사하다. **받거나, 증명하거나.**

## 기억해야 할 것들

- 명목적 타이핑에서 값은 그 타입이라고 말했기 때문에 그 타입이지, 같은 형태라서가 아니다.
- 의미적으로 구별되지만 구조적으로 동일한 원시·객체 타입을 구별하려면 브랜드를 붙이는 것을 고려하라.
- 다양한 브랜딩 기법에 익숙해져라: 객체 타입의 속성, 문자열 기반 enum, private 필드, unique symbol.
