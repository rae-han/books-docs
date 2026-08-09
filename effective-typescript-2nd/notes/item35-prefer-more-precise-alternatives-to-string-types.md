# Item 35: string 타입보다 더 정밀한 대안 선호하기 (Prefer More Precise Alternatives to String Types)

## 핵심 질문

"stringly typed" 코드는 어떤 버그를 숨기는가? `string`을 리터럴 유니온·`keyof`로 좁히면 무엇이 좋아지는가?

Item 7에서 봤듯 타입의 도메인은 그 타입에 할당 가능한 값의 집합이다. `string`의 도메인은 어마어마하다 - `"x"`와 `"y"`도 들어 있지만 "모비 딕" 전문(약 120만 자)도 들어 있다. `string` 타입 변수를 선언할 때마다 더 좁은 타입이 적절하지 않은지 물어야 한다.

## 1. "stringly typed" 인터페이스의 문제

음악 컬렉션의 앨범 타입을 만든다고 하자.

```typescript
interface Album {
  artist: string;
  title: string;
  releaseDate: string;   // YYYY-MM-DD
  recordingType: string; // 예: "live" 또는 "studio"
}
```

`string`의 만연과 주석 속 타입 정보(Item 31)가 이 인터페이스가 온전치 않다는 강한 신호다.

```typescript
const kindOfBlue: Album = {
  artist: 'Miles Davis',
  title: 'Kind of Blue',
  releaseDate: 'August 17th, 1959',  // 이런!
  recordingType: 'Studio',           // 이런!
};  // OK
```

`releaseDate`는 주석의 형식과 다르고 `'Studio'`는 소문자여야 하는데 대문자다. 하지만 둘 다 string이므로 타입 체커는 조용하다. 넓은 string 타입은 **유효한 Album 객체 사이의 실수**도 감춘다.

```typescript
function recordRelease(title: string, date: string) { /* ... */ }
recordRelease(kindOfBlue.releaseDate, kindOfBlue.title);  // OK - 에러여야 한다
```

인수 순서가 뒤바뀌었는데 둘 다 string이라 통과한다. string 타입이 만연한 이런 코드를 "stringly typed"라고 부르기도 한다(같은 타입의 위치 매개변수 반복 문제는 Item 38).

타입을 좁혀 보자. "모비 딕" 전문이 아티스트 이름이나 앨범 제목일 가능성은 낮아도 아주 없지는 않으니 그 둘은 `string`이 적절하다. `releaseDate`는 `Date` 객체로 형식 문제를 원천 차단하고, `recordingType`은 값 두 개짜리 유니온으로 정의한다(enum도 가능하지만 일반적으로 피하길 권한다 - Item 72).

```typescript
type RecordingType = 'studio' | 'live';

interface Album {
  artist: string;
  title: string;
  releaseDate: Date;
  recordingType: RecordingType;
}

const kindOfBlue: Album = {
  artist: 'Miles Davis',
  title: 'Kind of Blue',
  releaseDate: new Date('1959-08-17'),
  recordingType: 'Studio'
  // ~~~~~~~~~~~~ Type '"Studio"' is not assignable to type 'RecordingType'
};
```

## 2. 좁힌 타입의 부수 이점

엄격한 검사 이상의 장점이 있다.

1. **의미가 이동 중에 사라지지 않는다.** `function getAlbumsOfType(recordingType: string)`의 호출자는 무엇을 넘겨야 하는지 알 길이 없다 - 'studio' 또는 'live'라는 설명은 사용자가 들춰 볼 생각도 못 할 `Album` 정의 안에 숨어 있다. `RecordingType`을 받으면 명확해진다.
2. **타입에 문서를 붙일 수 있다**(Item 68).

```typescript
/** What type of environment was this recording made in? */
type RecordingType = 'live' | 'studio';
```

`getAlbumsOfType`이 `RecordingType`을 받으면 호출자가 클릭해서 문서를 볼 수 있다.

## 3. 함수 매개변수의 string - keyof로

string의 또 다른 흔한 오용이 함수 매개변수다. 배열에서 한 필드의 값만 뽑아내는 함수(Underscore·Ramda의 `pluck`)를 타이핑해 보자.

```typescript
function pluck(records: any[], key: string): any[] {
  return records.map(r => r[key]);
}
```

타입 체크는 되지만 좋지 않다 - 특히 반환값의 `any`(Item 43). 제네릭 타입 매개변수를 도입하면:

```typescript
function pluck<T>(records: T[], key: string): any[] {
  return records.map(r => r[key]);
  //                      ~~~~~~ Element implicitly has an 'any' type
  //                             because type '{}' has no index signature
}
```

이제 타입스크립트가 `key`의 `string`이 너무 넓다고 항의하는데, 옳은 항의다 - `Album` 배열을 넘긴다면 유효한 key는 광대한 문자열 집합이 아니라 네 개뿐이다. 정확히 `keyof Album`이다.

```typescript
type K = keyof Album;
//   ^? type K = keyof Album
//      ("artist" | "title" | "releaseDate" | "recordingType"과 동등)

function pluck<T>(records: T[], key: keyof T) {
  return records.map(r => r[key]);
}
```

통과한다. 추론된 반환 타입은 `T[keyof T][]` - `T[keyof T]`는 T에 있을 수 있는 **모든** 값의 타입이다. 키 하나를 넘기는 경우에는 여전히 너무 넓다.

```typescript
const releaseDates = pluck(albums, 'releaseDate');
//    ^? const releaseDates: (string | Date)[]
```

`Date[]`여야 하는데 `(string | Date)[]`다. 더 좁히려면 `keyof T`의 서브타입(아마 단일 값)인 **두 번째 타입 매개변수**를 도입한다.

```typescript
function pluck<T, K extends keyof T>(records: T[], key: K): T[K][] {
  return records.map(r => r[key]);
}
```

이제 타입 시그니처가 완전히 올바르다.

```typescript
const dates = pluck(albums, 'releaseDate');
//    ^? const dates: Date[]
const artists = pluck(albums, 'artist');
//    ^? const artists: string[]
const types = pluck(albums, 'recordingType');
//    ^? const types: RecordingType[]
const mix = pluck(albums, Math.random() < 0.5 ? 'releaseDate' : 'artist');
//    ^? const mix: (string | Date)[]
const badDates = pluck(albums, 'recordingDate');
//                             ~~~~~~~~~~~~~~~
// Argument of type '"recordingDate"' is not assignable to parameter of type ...
```

언어 서비스가 `Album`의 키를 자동완성해 주는 덤도 있다.

> **핵심 통찰**: `string`은 `any`와 같은 문제를 일부 공유한다 - 부적절하게 쓰면 무효한 값을 허용하고 타입 간의 관계를 감춰서 타입 체커를 무력화하고 진짜 버그를 숨긴다. string의 부분집합을 정의하는 타입스크립트의 능력은 자바스크립트 코드에 타입 안전성을 가져오는 강력한 수단이다.

이 아이템은 유한한 문자열 집합을 다뤘지만, 무한 집합("http:"로 시작하는 모든 문자열 등)도 모델링할 수 있다 - 템플릿 리터럴 타입, Item 54의 주제다.

## 기억해야 할 것들

- "stringly typed" 코드를 피하라. 모든 문자열이 가능한 것이 아니라면 더 적절한 타입을 선호하라.
- 변수의 도메인을 더 정확히 묘사한다면 `string`보다 문자열 리터럴 타입의 유니온을 선호하라. 더 엄격한 타입 체크와 더 나은 개발 경험을 얻는다.
- 객체의 속성이어야 하는 함수 매개변수에는 `string`보다 `keyof T`를 선호하라.
