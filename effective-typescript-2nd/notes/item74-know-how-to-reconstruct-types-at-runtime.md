# Item 74: 런타임에 타입 재구성하는 법 알기 (Know How to Reconstruct Types at Runtime)

## 핵심 질문

런타임에 지워지는 타입으로 요청 검증을 하려면? 타입과 검증 로직의 단일 진실 공급원은 어떻게 만드는가?

타입스크립트를 배우다 보면 대부분 어느 순간 깨닫는다 - 타입은 "진짜"가 아니라 런타임에 지워진다(Item 3). 타입과 런타임 동작의 독립은 타입스크립트-자바스크립트 관계의 핵심이고 대부분의 경우 아주 잘 동작한다. 하지만 **런타임에 타입스크립트 타입에 접근할 수 있다면 극히 편리할 때**가 분명히 있다.

블로그 댓글 생성 API 엔드포인트를 구현한다고 하자(Item 42에서 본 API다).

```typescript
interface CreateComment {
  postId: string;
  title: string;
  body: string;
}
```

요청 핸들러는 요청을 검증해야 한다. 일부는 애플리케이션 수준(postId가 실재하고 댓글 가능한 포스트인가?)이지만 일부는 **타입 수준**(기대한 속성이 다 있는가, 타입이 맞는가, 잉여 속성은 없는가?)이다.

```typescript
app.post('/comment', (request, response) => {
  const {body} = request;
  if (
    !body ||
    typeof body !== 'object' ||
    Object.keys(body).length !== 3 ||
    !('postId' in body) || typeof body.postId !== 'string' ||
    !('title' in body) || typeof body.title !== 'string' ||
    !('body' in body) || typeof body.body !== 'string'
  ) {
    return response.status(400).send('Invalid request');
  }
  const comment = body as CreateComment;
  // ... 애플리케이션 검증과 로직 ...
  return response.status(200).send('ok');
});
```

속성 셋뿐인데 벌써 검증 코드가 한가득이다. 더 나쁜 것은 **이 체크가 정확하고 타입과 동기화됐음을 보장하는 것이 아무것도 없다**는 점 - 철자를 맞게 썼는지 검사해 주는 것도 없고, 새 속성을 추가하면 체크 추가도 기억해야 한다. 최악의 코드 중복이다. 타입과 검증 로직, 동기화되어야 할 두 가지가 있으니 **단일 진실 공급원**이 필요하다. 인터페이스가 자연스러운 후보 같지만 런타임에 지워진다. 세 가지 해법을 보자.

## 1. 다른 소스에서 타입 생성

API가 GraphQL이나 OpenAPI 스키마 등 다른 형식으로 명세되어 있다면 **그것을 진실 공급원으로 삼아 타입스크립트 타입을 생성**하라. 보통 외부 도구를 돌려 타입과 (경우에 따라) 검증 코드를 생성한다 - OpenAPI는 JSON Schema를 쓰므로 json-schema-to-typescript로 타입을 생성하고 Ajv 같은 JSON Schema 검증기로 요청을 검증할 수 있다.

단점은 복잡성과, API 스키마가 바뀔 때마다 돌려야 하는 빌드 단계다. 하지만 이미 OpenAPI 등으로 API를 명세하고 있다면 **새 진실 공급원을 도입하지 않는다는 거대한 이점**이 있고, 이 접근을 선호해야 한다(생성 예제는 Item 42).

## 2. 런타임 라이브러리로 타입 정의 - Zod

정적 타입에서 런타임 값을 끌어내는 것은 타입스크립트 설계상 불가능하지만, **반대 방향(런타임 값→정적 타입)은 `typeof`로 간단하다.** 그래서 런타임 구문으로 타입을 정의하고 정적 타입을 유도하는 선택지가 있다 - 보통 라이브러리를 쓰고, 현재 가장 인기 있는 것은 Zod다(React의 PropTypes도 한 예).

```typescript
import { z } from 'zod';

// 타입 검증용 런타임 값
const createCommentSchema = z.object({
  postId: z.string(),
  title: z.string(),
  body: z.string(),
});

// 정적 타입
type CreateComment = z.infer<typeof createCommentSchema>;
//   ^? type CreateComment = { postId: string; title: string; body: string; }

app.post('/comment', (request, response) => {
  const {body} = request;
  try {
    const comment = createCommentSchema.parse(body);
    //    ^? const comment: { postId: string; title: string; body: string; }
    // ... 애플리케이션 검증과 로직 ...
    return response.status(200).send('ok');
  } catch (e) {
    return response.status(400).send('Invalid request');
  }
});
```

Zod가 중복을 완전히 없앴다 - `createCommentSchema` 값이 진실 공급원이고, 정적 타입도 스키마 검증도 그것에서 유도된다.

**단점**:

1. 타입을 정의하는 방법이 둘이 된다 - Zod의 문법(`z.object`)과 타입스크립트의 문법(`interface`). 비슷하지만 똑같지 않고, 팀 전원이 Zod도 배워야 한다.
2. **런타임 타입 시스템은 전염되는 경향이 있다** - `createCommentSchema`가 다른 타입을 참조해야 하면 그 타입도 런타임 타입으로 재작업해야 한다. 외부 라이브러리의 타입을 참조하거나 DB에서 타입을 생성(Item 58)하는 등 다른 타입 소스와의 상호운용이 어려워질 수 있다.

**장점**:

1. Zod류 라이브러리는 타입스크립트 타입으로 담기 어려운 제약("유효한 이메일 주소", "정수")을 표현할 수 있다 - 안 쓰면 그런 검증을 직접 써야 한다.
2. **추가 빌드 단계가 없다.** 전부 타입스크립트 안에서 이뤄진다. 스키마가 자주 바뀐다면 실패 모드 하나가 사라지고 반복 주기가 조여진다.

## 3. 타입에서 런타임 값 생성 - typescript-json-schema

새 도구와 빌드 단계를 감수한다면 앞 절의 반대도 가능하다 - **타입스크립트 타입에서 런타임 값을 생성**한다. JSON Schema가 인기 타깃이다.

```typescript
// api.ts
export interface CreateComment {
  postId: string;
  title: string;
  body: string;
}
```

```
$ npx typescript-json-schema api.ts '*' > api.schema.json
```

생성된 api.schema.json을 런타임에 로드하고(`resolveJsonModule` 옵션이면 평범한 import로 된다) 아무 JSON Schema 검증 라이브러리로 검증한다.

```typescript
import Ajv from 'ajv';
import apiSchema from './api.schema.json';
import {CreateComment} from './api';

const ajv = new Ajv();

app.post('/comment', (request, response) => {
  const {body} = request;
  if (!ajv.validate(apiSchema.definitions.CreateComment, body)) {
    return response.status(400).send('Invalid request');
  }
  const comment = body as CreateComment;
  // ... 애플리케이션 검증과 로직 ...
  return response.status(200).send('ok');
});
```

이 접근의 큰 강점은 **알고 사랑하는 타입스크립트 도구를 계속 쓸 수 있다**는 것 - JSON Schema는 구현 세부일 뿐이라 타입 정의법을 하나 더 배울 필요가 없고, API 타입이 @types 등 다른 소스의 타입을 참조해도 된다(그냥 타입스크립트 타입이니까). 단점은 새 도구와 빌드 단계 - api.ts가 바뀔 때마다 api.schema.json을 재생성해야 하며, 실무에서는 CI로 동기화를 강제해야 한다.

## 4. 무엇을 고를까

완벽한 답은 없고 각각이 트레이드오프다.

1. **타입이 이미 다른 형식(OpenAPI 스키마 등)으로 표현되어 있다면** 그것을 타입과 검증 로직 모두의 진실 공급원으로 써라. 도구·프로세스 오버헤드가 있어도 단일 진실 공급원의 가치가 있다.
2. 아니라면 더 까다롭다 - **빌드 단계와 제2의 타입 정의 방식 중 무엇을 도입할 것인가?** 타입스크립트 타입으로만 정의된 타입(라이브러리에서 오거나 생성된)을 참조해야 한다면 타입스크립트 타입에서 JSON Schema를 생성하는 것이 최선이다. 그 외라면, 독을 골라라!

## 기억해야 할 것들

- 타입스크립트 타입은 코드 실행 전에 지워진다. 추가 도구 없이는 런타임에 접근할 수 없다.
- 런타임 타입의 선택지를 알아 두라: 별도 런타임 타입 시스템(Zod 등), 값에서 타입스크립트 타입 생성(json-schema-to-typescript), 타입스크립트 타입에서 값 생성(typescript-json-schema).
- 타입의 다른 명세(스키마 등)가 있다면 그것을 진실 공급원으로 사용하라.
- 외부 타입스크립트 타입을 참조해야 한다면 typescript-json-schema 또는 그 등가물을 사용하라.
- 그 외에는 빌드 단계 추가와 타입 명세 방식 추가 중 무엇을 선호하는지 저울질하라.
