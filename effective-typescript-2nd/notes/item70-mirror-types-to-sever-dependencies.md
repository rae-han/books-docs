# Item 70: 타입을 미러링해 의존성 끊기 (Mirror Types to Sever Dependencies)

## 핵심 질문

내 라이브러리의 타입이 @types/node 같은 거대한 타입 패키지에 의존한다면, 그것을 사용자에게 강요하지 않는 방법은?

CSV 파일을 파싱하는 라이브러리를 만들었다고 하자. Node.js 사용자의 편의를 위해 내용물로 string 또는 Node.js `Buffer`를 받는다.

```typescript
// parse-csv.ts
import {Buffer} from 'node:buffer';

function parseCSV(contents: string | Buffer): {[column: string]: string}[] {
  if (typeof contents === 'object') {
    // Buffer다
    return parseCSV(contents.toString('utf8'));
  }
  // ...
}
```

`Buffer`의 타입 정의는 Node.js 타입 선언(`@types/node`)에서 오고, Item 65의 조언대로 devDependency로 설치했다. 라이브러리를 공개하면서 `--declaration`으로 타입 선언을 생성해 번들하면:

```typescript
// parse-csv.d.ts
import { Buffer } from 'node:buffer';
export declare function parseCSV(contents: string | Buffer): {
  [column: string]: string;
}[];
```

자바스크립트 사용자는 행복하겠지만 **타입스크립트 웹 개발자는 아니다** - 이런 에러 항의가 들어온다.

```
Cannot find module 'node:buffer' or its corresponding type declarations.
```

`@types/node`가 devDependency라서 패키지와 함께 설치되지 않는데, 패키지의 일부인 타입은 그것에 의존하기 때문이다. 그럼 `@types/node`를 prod 의존성으로? 에러는 사라지지만 다른 항의들이 온다.

1. 자바스크립트 개발자: 내가 의존하게 된 이 @types 모듈들은 뭔가?
2. 타입스크립트 웹 개발자: 내가 왜 Node.js에 의존하나?
3. 다른 버전의 Node.js를 쓰는 타입스크립트 개발자: 타입 정의가 왜 중복되나?

합리적인 항의들이다. Buffer 지원은 필수가 아니라 이미 Node.js를 쓰는 사용자에게만 유의미하고, `@types/node`의 선언은 그중에서도 타입스크립트를 쓰는 사용자에게만 유의미하다. `@types/node`는 작지 않고(약 10만 줄) 우리는 그 극히 일부만 쓴다.

## 1. 구조적 타이핑으로 탈출 - 필요한 만큼만 미러링

타입스크립트의 구조적 타이핑(Item 4)이 궁지에서 꺼내 준다. `@types/node`의 Buffer 선언 대신 **필요한 메서드와 속성만 담은 나만의 타입**을 쓰면 된다. 이 경우 인코딩을 받는 `toString` 하나면 된다.

```typescript
export interface CsvBuffer {
  toString(encoding?: string): string;
}
export function parseCSV(
  contents: string | CsvBuffer
): {[column: string]: string}[] {
  // ...
}
```

완전한 인터페이스보다 극적으로 짧지만 Buffer에게서 필요한 (단순한) 것을 다 담았다. Node.js 프로젝트에서 진짜 Buffer로 호출하는 것도 여전히 OK다 - 타입이 호환되니까.

```typescript
parseCSV(new Buffer("column1,column2\nval1,val2", "utf-8"));  // OK
```

`CsvBuffer`를 다시 보면 CSV에 특정된 것이 없다. 더 "구조적인" 이름이 그 점을 강조해 준다.

```typescript
/** 인코딩을 받아 문자열로 변환 가능한 것. 예: Node의 Buffer. */
export interface StringEncodable {
  toString(encoding?: string): string;
}
```

Node의 Buffer가 `StringEncodable`에 할당 가능하다는 것이 중요하므로(주석도 그렇게 말한다!) **그것을 검증하는 유닛 테스트를 써야 한다.**

```typescript
import {Buffer} from 'node:buffer';
import {parseCSV} from './parse-csv';

test('parse CSV in a buffer', () => {
  expect(
    parseCSV(new Buffer("column1,column2\nval1,val2", "utf-8"))
  ).toEqual(
    [{column1: 'val1', column2: 'val2'}]
  );
});
```

이 테스트는 코드의 런타임 동작과 **Buffer의 StringEncodable 할당 가능성을 동시에** 검증한다. 테스트가 `node:buffer`를 import하지만 괜찮다 - `@types/node`는 라이브러리 사용자에게 영향을 주지 않는 devDependency로 남을 수 있다.

## 2. 트레이드오프

코드가 Buffer의 메서드를 더 쓰기 시작하면 내 인터페이스에도 추가해야 한다. 중복처럼 느껴질 수 있지만, Go 언어 커뮤니티에는 이런 말이 있다.

> A little copying is better than a little dependency.<br>약간의 복사가 약간의 의존성보다 낫다.

다른 라이브러리의 타입 상당 부분에 의존한다면 벤더링(vendoring)으로 이 복사를 공식화할 수도 있다.

어느 쪽이든 @types 의존성을 끊음으로써 자바스크립트 사용자와 모든 부류의 타입스크립트 개발자에게 좋은 경험을 준다. 그 @types 의존성에 자체 의존성이 또 있었다면 **의존성 트리 전체를 끊어낸** 것이라 컴파일러 성능에도 큰 이득이 될 수 있다(Item 78). 이 기법은 유닛 테스트와 프로덕션 시스템 사이의 의존성 절단에도 유용하다 - Item 4의 `getAuthors` 예제가 그것이다.

## 기억해야 할 것들

- 공개하는 npm 모듈에서 이행적 타입 의존성을 피하라.
- 구조적 타이핑으로 필수가 아닌 의존성을 끊어라.
- 자바스크립트 사용자에게 @types 의존을, 웹 개발자에게 Node.js 의존을 강요하지 마라.
