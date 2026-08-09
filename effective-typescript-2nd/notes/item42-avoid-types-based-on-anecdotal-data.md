# Item 42: 일화적 데이터에 기반한 타입 피하기 (Avoid Types Based on Anecdotal Data)

## 핵심 질문

"내가 본 데이터"를 보고 손으로 쓴 타입은 무엇을 놓치는가? 명세·스키마에서 타입을 얻는 방법들은?

이 장의 다른 아이템들은 좋은 타입 설계의 이점과 나쁜 설계의 대가를 보여 줬다. 그런데 타입 설계에 이만한 압박이 실린다면, 직접 안 해도 된다면 좋지 않을까?

타입의 적어도 일부는 프로그램 바깥에서 온다: 명세, 파일 형식, API, 데이터베이스 스키마. 이런 타입을 **내가 본 데이터에 근거해서** 직접 쓰고 싶은 유혹이 생긴다 - 테스트 DB의 행이나 특정 API 엔드포인트에서 본 응답 같은 것들. **이 충동을 참아라!** 다른 곳에서 타입을 가져오거나 명세에서 생성하는 것이 훨씬 낫다. 일화적 데이터로 타입을 직접 쓰면 내가 본 예제만 고려하게 되어 프로그램을 깨뜨릴 중요한 엣지 케이스를 놓칠 수 있다.

## 1. GeoJSON - 커뮤니티 타입이 잡아 준 진짜 버그

GeoJSON 피처의 바운딩 박스를 계산하는 함수가 있다.

```typescript
function calculateBoundingBox(f: GeoJSONFeature): BoundingBox | null {
  let box: BoundingBox | null = null;
  const helper = (coords: any[]) => {
    // ...
  };
  const {geometry} = f;
  if (geometry) {
    helper(geometry.coordinates);
  }
  return box;
}
```

`GeoJSONFeature` 타입은 어떻게 정의할까? 저장소의 GeoJSON 몇 개를 보고 인터페이스를 스케치할 수 있다.

```typescript
interface GeoJSONFeature {
  type: 'Feature';
  geometry: GeoJSONGeometry | null;
  properties: unknown;
}
interface GeoJSONGeometry {
  type: 'Point' | 'LineString' | 'Polygon' | 'MultiPolygon';
  coordinates: number[] | number[][] | number[][][] | number[][][][];
}
```

이 정의로 함수는 타입 체크를 통과한다. 하지만 정말 올바를까? **이 검사는 우리가 손으로 만든 타입 선언만큼만 좋다.** 더 나은 접근은 공식 GeoJSON 명세(RFC 7946)를 쓰는 것이고, 다행히 DefinitelyTyped에 이미 타입 선언이 있다.

```
$ npm install --save-dev @types/geojson
```

이 선언으로 바꾸면 타입스크립트가 에러를 지적한다.

```typescript
import {Feature} from 'geojson';

function calculateBoundingBox(f: Feature): BoundingBox | null {
  // ...
  const {geometry} = f;
  if (geometry) {
    helper(geometry.coordinates);
    //              ~~~~~~~~~~~
    // Property 'coordinates' does not exist on type 'Geometry'
    // Property 'coordinates' does not exist on type 'GeometryCollection'
  }
  return box;
}
```

이 코드는 지오메트리에 `coordinates`가 있다고 가정하는데, 점·선·다각형 등 많은 지오메트리에는 참이지만 GeoJSON 지오메트리는 **`GeometryCollection`** - 다른 지오메트리들의 이질적 모음 - 일 수도 있고, 그것에는 `coordinates`가 없다. 그런 피처에 이 함수를 호출하면 "cannot read property 0 of undefined" 에러가 난다. **진짜 버그다!** 커뮤니티에서 타입을 가져온 덕에 잡았다.

수정 방법 하나는 `GeometryCollection`을 명시적으로 거부하는 것 - 체크로 타입이 정제되어 `coordinates` 참조가 허용되고, 사용자에게 더 분명한 에러 메시지라도 준다.

```typescript
if (geometry.type === 'GeometryCollection') {
  throw new Error('GeometryCollections are not supported.');
}
helper(geometry.coordinates);  // OK
```

하지만 더 나은 해법은 지원하는 것이다.

```typescript
const geometryHelper = (g: Geometry) => {
  if (g.type === 'GeometryCollection') {
    g.geometries.forEach(geometryHelper);
  } else {
    helper(g.coordinates);  // OK
  }
}
```

손으로 쓴 GeoJSON 타입은 이 형식에 대한 **내 경험**에만 근거했고, 거기에 GeometryCollection이 없었기에 코드의 정확성에 대한 거짓 안도감을 줬다. 명세에 기반한 커뮤니티 타입은 **내가 우연히 본 값만이 아니라 모든 값**과 동작하리라는 확신을 준다.

## 2. API 타입 - 공식 클라이언트, GraphQL, OpenAPI

API 호출에도 같은 고려가 적용된다. 공식 타입스크립트 클라이언트가 있으면 그것을 써라! 없어도 공식 소스에서 타입을 **생성**할 수 있는 경우가 많다.

- **GraphQL**: 모든 쿼리·뮤테이션·타입을 기술하는 스키마가 포함되어 있고, GraphQL 쿼리에 타입스크립트 타입을 붙여 주는 도구가 많다.
- **REST**: 많은 API가 OpenAPI 스키마를 공개한다 - 모든 엔드포인트, HTTP 동사, 타입을 JSON Schema로 기술한 파일이다.

블로그 댓글 API의 OpenAPI 스키마가 있다면, 스키마를 추출해 json-schema-to-typescript에 돌리는 것이 한 방법이다.

```
$ jq .components.schemas.CreateCommentRequest schema.json > comment.json
$ npx json-schema-to-typescript comment.json > comment.ts
$ cat comment.ts
export interface CreateCommentRequest {
  body: string;
  postId: string;
  title: string;
}
```

깔끔한 인터페이스가 나와서 이 API와 타입 안전하게 상호작용하게 해 준다. 중요한 것은 **타입을 내가 쓰지 않았다는 것** - 신뢰할 수 있는 진실 공급원에서 생성됐다. 필드가 옵셔널이거나 null일 수 있다면 타입스크립트가 알고 그 가능성을 처리하도록 강제한다. 다음 단계는 런타임 검증을 추가하고 타입을 엔드포인트에 직접 연결하는 것인데, Item 74에서 이 예제로 돌아온다. 생성한 타입이 API 스키마와 동기화되도록 유지하는 전략은 Item 58에서 다룬다.

## 3. 명세가 없다면

공식 스키마가 없으면 데이터에서 타입을 생성해야 한다. quicktype 같은 도구가 도와준다. 하지만 **타입이 현실과 다를 수 있다는 것**을 인지하라 - 놓친 엣지 케이스가 있을 수 있다. (예외: 데이터 집합이 유한한 경우 - 예를 들어 JSON 파일 1,000개짜리 디렉터리라면 놓친 것이 없음을 안다!)

의식하지 못해도 우리는 이미 코드 생성의 혜택을 받고 있다. 브라우저 DOM API에 대한 타입스크립트의 타입 선언(Item 75)은 MDN의 API 기술로부터 생성된다. 복잡한 시스템을 올바르게 모델링하고, 내 코드의 오류와 오해를 잡아 준다.

## 기억해야 할 것들

- 내가 본 데이터에 근거해서 손으로 타입을 쓰지 마라. 스키마를 오해하거나 nullability를 틀리기 쉽다.
- 공식 클라이언트나 커뮤니티에서 나온 타입을 선호하라. 없다면 스키마에서 타입스크립트 타입을 생성하라.
