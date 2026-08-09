# Item 23: 별칭을 일관되게 사용하기 (Be Consistent in Your Use of Aliases)

## 핵심 질문

중복을 줄이려고 만든 중간 변수가 왜 타입 에러를 낳는가? 별칭과 제어 흐름 분석은 어떻게 상호작용하는가?

값에 새 이름을 도입하면 별칭(*alias - 같은 기저 객체를 가리키는 또 하나의 변수*)이 생긴다.

```typescript
const place = {name: 'New York', latLng: [41.6868, -74.2692]};
const loc = place.latLng;

> loc[0] = 0;
> place.latLng
[ 0, -74.2692 ]
```

별칭의 속성을 바꾸면 원래 값에서도 보인다 — 포인터·참조 타입이 있는 언어를 써 봤다면 같은 개념이다. **별칭은 모든 언어에서 컴파일러 작성자의 골칫거리다** — 제어 흐름 분석을 어렵게 만들기 때문이다. 별칭을 신중하게 쓰면 타입스크립트가 코드를 더 잘 이해하고 더 많은 진짜 오류를 찾아 준다.

## 1. 별칭이 좁히기를 방해하는 예

다각형 자료 구조가 있다. `bbox`는 있을 수도 없을 수도 있는 최적화 속성이다.

```typescript
interface Coordinate {
  x: number;
  y: number;
}
interface BoundingBox {
  x: [number, number];
  y: [number, number];
}
interface Polygon {
  exterior: Coordinate[];
  holes: Coordinate[][];
  bbox?: BoundingBox;
}

function isPointInPolygon(polygon: Polygon, pt: Coordinate) {
  if (polygon.bbox) {
    if (pt.x < polygon.bbox.x[0] || pt.x > polygon.bbox.x[1] ||
        pt.y < polygon.bbox.y[0] || pt.y > polygon.bbox.y[1]) {
      return false;
    }
  }
  // ... 더 복잡한 검사
}
```

동작하고 타입 체크도 되지만 세 줄에 `polygon.bbox`가 다섯 번 나온다. 중복을 줄이려 중간 변수를 뽑으면:

```typescript
function isPointInPolygon(polygon: Polygon, pt: Coordinate) {
  const box = polygon.bbox;
  if (polygon.bbox) {
    if (pt.x < box.x[0] || pt.x > box.x[1] ||
        //     ~~~         ~~~ 'box' is possibly 'undefined'
        pt.y < box.y[0] || pt.y > box.y[1]) {
        //     ~~~         ~~~ 'box' is possibly 'undefined'
      return false;
    }
  }
  // ...
}
```

코드는 여전히 동작하는데 왜 에러일까? `box`라는 **별칭을 만들면서** 첫 예제에서 조용히 작동하던 제어 흐름 분석이 무력화됐다. 타입을 확인해 보면:

```typescript
polygon.bbox
// ^? (property) Polygon.bbox?: BoundingBox | undefined
const box = polygon.bbox;
// ^? const box: BoundingBox | undefined
if (polygon.bbox) {
  console.log(polygon.bbox);
  //          ^? (property) Polygon.bbox?: BoundingBox
  console.log(box);
  //          ^? const box: BoundingBox | undefined
}
```

속성 체크가 `polygon.bbox`의 타입은 정제했지만 `box`는 아니다. 여기서 별칭의 황금률이 나온다.

> **핵심 통찰**: **별칭을 도입했으면 일관되게 써라.** 체크도 별칭으로, 사용도 별칭으로.

```typescript
function isPointInPolygon(polygon: Polygon, pt: Coordinate) {
  const box = polygon.bbox;
  if (box) {
    if (pt.x < box.x[0] || pt.x > box.x[1] ||
        pt.y < box.y[0] || pt.y > box.y[1]) {  // OK
      return false;
    }
  }
  // ...
}
```

## 2. 구조 분해 — 일관된 이름에 주는 보상

타입 체커는 만족했지만 사람 독자에게 문제가 남았다 — 같은 것에 두 이름(`box`와 `bbox`)을 쓰고 있다. 차이 없는 구별이다(Item 41). **객체 구조 분해**는 일관된 이름을 쓰게 하면서 코드도 간결하게 해 준다. 배열과 중첩 구조에도 쓸 수 있다.

```typescript
function isPointInPolygon(polygon: Polygon, pt: Coordinate) {
  const {bbox} = polygon;
  if (bbox) {
    const {x, y} = bbox;
    if (pt.x < x[0] || pt.x > x[1] || pt.y < y[0] || pt.y > y[1]) {
      return false;
    }
  }
  // ...
}
```

곁들일 점 두 가지:

1. `bbox` 전체가 아니라 `x`·`y` 속성이 옵셔널이었다면 속성 체크가 더 필요했을 것이다. **null 값을 타입의 가장자리로 밀어내라**는 Item 33의 조언 덕을 본 것이다.
2. `bbox`에는 옵셔널이 적절했지만 `holes`에는 아니었을 것이다 — `holes`가 옵셔널이면 "없음"과 "빈 배열"이 공존하는 차이 없는 구별이 된다. 구멍이 없다는 것은 빈 배열로 충분히 표현된다.

## 3. 런타임에서도 혼란을 부른다

별칭은 타입 체커만이 아니라 **런타임에서도** 혼란을 만들 수 있다.

```typescript
const {bbox} = polygon;
if (!bbox) {
  calculatePolygonBbox(polygon);  // polygon.bbox를 채운다
  // 이제 polygon.bbox와 bbox는 서로 다른 값을 가리킨다!
}
```

## 4. 함수 호출은 속성의 정제를 무효화할 수 있다

타입스크립트의 제어 흐름 분석은 지역 변수에는 꽤 정확하다. 하지만 **속성**은 경계해야 한다.

```typescript
function expandABit(p: Polygon) { /* ... */ }

polygon.bbox
// ^? (property) Polygon.bbox?: BoundingBox | undefined
if (polygon.bbox) {
  polygon.bbox
  // ^? (property) Polygon.bbox?: BoundingBox
  expandABit(polygon);
  polygon.bbox
  // ^? (property) Polygon.bbox?: BoundingBox  — 여전히!
}
```

`expandABit(polygon)`이 `polygon.bbox`를 지워 버릴 수도 있으므로 타입이 `BoundingBox | undefined`로 되돌아가는 것이 더 안전하다. 하지만 그러면 함수를 부를 때마다 속성 체크를 반복해야 해서 짜증이 날 것이다. 그래서 타입스크립트는 **함수가 타입 정제를 무효화하지 않는다고 가정하는 실용적 선택**을 한다(안전을 편의와 맞바꾸는 다른 사례들은 Item 48).

지역 변수 `bbox`를 뽑아냈다면 타입은 정확하게 유지되지만 `polygon.bbox`와 같은 값이 아니게 될 수 있다. 이런 부수효과가 걱정된다면 최선은 함수에 **읽기 전용 버전을 넘기는 것**(Item 14)이다 — 변경을 막으면 타입 안전성도 좋아진다. 이것은 가변인 객체 타입(배열 포함)의 문제다. 원시 값은 이미 불변이다.

## 기억해야 할 것들

- 별칭은 타입스크립트의 타입 좁히기를 막을 수 있다. 변수에 별칭을 만들었으면 일관되게 사용하라.
- 함수 호출이 속성의 타입 정제를 무효화할 수 있음을 알아 두라. 속성보다 지역 변수의 정제를 더 신뢰하라.
