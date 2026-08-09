# Item 58: 복잡한 타입의 대안으로 코드 생성 고려하기 (Consider Codegen as an Alternative to Complex Types)

## 핵심 질문

타입 수준 프로그래밍이 "튜링 타르 구덩이"에 빠졌다는 신호는 무엇이고, 그때 대안은 무엇인가?

> Beware of the Turing tar-pit in which everything is possible but nothing of interest is easy.<br>모든 것이 가능하지만 흥미로운 어떤 것도 쉽지 않은 튜링 타르 구덩이를 조심하라.<br>— 앨런 펄리스(Alan Perlis)

이 장에서 타입 수준 프로그래밍을 탐구했다 — 타입에 작용하는 로직과 함수를 구현하고(Item 50), 테스트를 쓰고(Item 55), 성능을 생각하는(Item 57) 일이다. 특히 템플릿 리터럴 타입(Item 54)까지 있으면 타입 수준 프로그램은 정말 인상적인 일을 할 수 있다. 타입스크립트의 타입 시스템은 튜링 완전이라 이론상 어떤 계산도 표현할 수 있다. 하지만 인용문의 경고대로 — **가능하다고 쉬운 것도, 현명한 것도 아니다.**

## 1. SQL 쿼리 타이핑 — 타르 구덩이로 가는 길

프로그램이 DB와 상호작용하며 SQL을 담고 있다고 하자.

```typescript
async function getBooks(db: Database) {
  const result = await db.query(
    `SELECT title, author, year, publisher FROM books`
  );
  return result.rows;
}
```

머리를 짜내면 템플릿 리터럴 타입과 조건부 타입으로 저 쿼리를 타입 시스템에서 파싱할 수 있을지 모른다. DB 스키마를 표현하는 타입과 결합하면 쿼리 SQL 자체에서 결과 타입을 추론할 수도 있다. 인상적인 성취고 더 정밀한 타입도 얻는다. 그런데 프로그램에 이 쿼리도 있다면?

```typescript
async function getLatestBookByAuthor(db: Database, publisher: string) {
  const result = await db.query(
    `SELECT author, MAX(year) FROM books GROUP BY author WHERE publisher=$1`,
    [publisher]
  );
  return result.rows;
}
```

이 쿼리의 올바른 타입을 얻기는 훨씬 어렵다. GROUP BY 절, MAX 표현식을 이해해야 하고, `$1` 플레이스홀더가 문자열 하나가 든 배열을 둘째 인수로 넘기라는 뜻임도 알아야 한다. 첫 쿼리의 파서를 만들 수 있었더라도 이 쿼리는 코드를 "튜링 타르 구덩이"로 밀어 넣을 것이다. 부정확한 타입보다 덜 정밀한 타입을 선호하라(Item 40)는 조언을 지키고 있는지 확신하기도 점점 어려워진다 — 복잡한 프로그램일수록 실수하기 쉽다.

## 2. 대안 — 코드 생성

상당히 더 단순한 대안이 있다: 코드 생성(*codegen - 코드에 작용해 다른 코드를 생성하는 프로그램. 진정한 의미의 메타프로그래밍*)이다. 코드 생성의 아름다움은 **타입 조작을 원하는 어떤 언어로든 쓸 수 있다**는 것이다. 타입스크립트의 타입 시스템이 강력하긴 해도 일을 해치우는 데 첫손에 꼽을 언어는 아니다. 코드 생성이라면 평범한 타입스크립트로 쓸 수 있다. 파이썬이나 러스트도 되고, 셸 스크립트로 충분할 수도 있다.

SQL 쿼리에는 PgTyped 라이브러리가 한 선택지다. 타입스크립트 안에서 적절히 태그된 SQL 쿼리를 찾아 **실제 데이터베이스에 대조**하고, 입력·출력 타입을 담은 타입 선언 파일을 써 준다.

```typescript
// books-queries.ts
import { sql } from '@pgtyped/runtime';

const selectLatest = sql`
  SELECT author, MAX(year)
  FROM books
  GROUP BY author
  WHERE publisher=$publisher
`;
```

`npx pgtyped -c pgtyped.config.json`을 실행하면(설정 파일은 DB 접속 방법을 알려 준다) 타입이 담긴 새 파일이 생긴다.

```typescript
// books-queries.types.ts
/** 'selectLatest' parameters type */
export interface selectLatestParams {
  publisher: string;
}
/** 'selectLatest' return type */
export interface selectLatestResult {
  author: string;
  year: number;
}
/** 'selectLatest' query type */
export interface selectLatestQuery {
  params: selectLatestParams;
  result: selectLatestResult;
}
```

그리고 원본 파일에 타입 매개변수가 끼워진다.

```typescript
export const selectLatestBookByAuthor = sql<selectLatestQuery>`
  SELECT author, MAX(year)
  FROM books
  GROUP BY author
  WHERE publisher=$publisher
`;

async function getLatestBookByAuthor(db: Database, publisher: string) {
  const result = await selectLatestBookByAuthor.run({publisher}, db);
  //    ^? const result: selectLatestResult[]
  return result;
}
```

쿼리가 올바르게 타이핑됐다! PgTyped가 단순한 프로그램은 아니지만, 타입스크립트로 작성됐고 표준 DB·테스트 라이브러리를 쓰며, 같은 능력의 도구를 타입 시스템 안에서 만드는 것보다 확실히 덜 고통스럽다.

코드 생성 접근의 추가 이점:

- **타입 표시의 완전한 통제**: 생성된 타입에는 Item 56의 트릭이 필요 없다. 원하는 모양 그대로 만들 수 있다 — snake_case 타입 이름이 싫으면 sed에 통과시키면 그만이다.
- **컴파일러 부담 감소**: 생성된 타입은 손수 만든 SQL 파서보다 타입스크립트 컴파일러와 언어 서비스에 훨씬 덜 부담을 준다.

## 3. 비용 — 동기화 유지

코드 생성의 주목할 비용 하나는 **정기적으로 실행해야 하는 빌드 단계가 하나 더 생긴다**는 것이다. SQL의 경우 쿼리가 바뀌거나 DB 스키마가 바뀔 때마다 pgtyped를 다시 돌려야 한다. 흔한 강제 방법은 **CI에서 codegen을 돌리고 `git diff`로 아무것도 안 바뀌었는지 확인**하는 것이다. pre-push 체크로 추가할 수도 있다.

> **핵심 통찰**: 소프트웨어 공학은 복잡성과의 끝없는 전투이고, 타입 수준 타입스크립트는 인상적인 도구지만 이 전투의 최고 무기는 아니다. 화려한 타입 수준 코드를 쓰다가 튜링 타르 구덩이를 헤매는 기분이 든다면, 타입을 생성하고 코드는 더 평범한 언어로 쓸 수 없는지 생각해 보라.

(codegen으로 타입 안전성을 높이고 유지 비용을 줄이는 다른 방법들은 Item 42와 74에서.)

## 기억해야 할 것들

- 타입 수준 타입스크립트는 인상적으로 강력한 도구지만 항상 최선의 도구는 아니다.
- 복잡한 타입 조작에는 타입 수준 코드 대신 코드와 타입을 생성하는 것을 고려하라. 코드 생성 도구는 평범한 타입스크립트나 다른 어떤 언어로도 쓸 수 있다.
- CI에서 codegen과 git diff를 돌려 생성된 코드가 동기화 상태를 유지하는지 확인하라.
