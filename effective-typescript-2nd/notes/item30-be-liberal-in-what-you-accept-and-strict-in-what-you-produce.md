# Item 30: 받을 때는 너그럽게, 내놓을 때는 엄격하게 (Be Liberal in What You Accept and Strict in What You Produce)

## 핵심 질문

함수의 매개변수 타입과 반환 타입은 왜 다르게 설계해야 하는가? 반환 타입이 넓으면 무슨 문제가 생기는가?

이 아이디어는 견고성 원칙(robustness principle) 또는 포스텔의 법칙(Postel's Law)으로 알려져 있다. TCP 네트워킹 프로토콜 맥락에서 존 포스텔이 쓴 문장에서 왔다.

> TCP implementations should follow a general principle of robustness: be conservative in what you do, be liberal in what you accept from others.<br>TCP 구현은 일반적 견고성 원칙을 따라야 한다: 자신이 하는 일에는 보수적으로, 남에게서 받는 것에는 너그럽게.<br>— 존 포스텔(Jon Postel)

함수의 계약에도 비슷한 규칙이 적용된다. **입력으로 받는 것은 넓어도 괜찮지만, 출력으로 내놓는 것은 대개 더 구체적이어야 한다.**

## 1. 너그러운 반환 타입이 만드는 고통

3D 지도 API가 카메라 위치 설정과 바운딩 박스의 뷰포트 계산을 제공한다.

```typescript
declare function setCamera(camera: CameraOptions): void;
declare function viewportForBounds(bounds: LngLatBounds): CameraOptions;
```

`viewportForBounds`의 결과를 바로 `setCamera`에 넘길 수 있으니 편리하다. 타입 정의를 보자.

```typescript
interface CameraOptions {
  center?: LngLat;
  zoom?: number;
  bearing?: number;
  pitch?: number;
}
type LngLat =
  { lng: number; lat: number; } |
  { lon: number; lat: number; } |
  [number, number];
```

`CameraOptions`의 필드가 전부 옵셔널인 것은 center나 zoom만 바꾸고 싶을 수 있어서고, `LngLat` 덕에 `setCamera`는 받는 것에 너그럽다 — `{lng, lat}`, `{lon, lat}`, 순서에 자신 있다면 `[lng, lat]` 쌍까지. 이런 배려가 함수를 호출하기 쉽게 만든다. `viewportForBounds`의 입력도 너그럽다.

```typescript
type LngLatBounds =
  {northeast: LngLat, southwest: LngLat} |
  [LngLat, LngLat] |
  [number, number, number, number];
```

`LngLat`이 이미 세 가지 형태이므로 `LngLatBounds`의 가능한 형태는 무려 19가지(3×3 + 3×3 + 1)다. 참 너그럽다!

이제 GeoJSON 피처에 뷰포트를 맞추고 새 뷰포트를 URL에 저장하는 함수를 쓰면:

```typescript
function focusOnFeature(f: Feature) {
  const bounds = calculateBoundingBox(f);  // 헬퍼 함수
  const camera = viewportForBounds(bounds);
  setCamera(camera);
  const {center: {lat, lng}, zoom} = camera;
  //             ~~~ Property 'lat' does not exist on type ...
  //                  ~~~ Property 'lng' does not exist on type ...
  zoom;
  // ^? const zoom: number | undefined
  window.location.search = `?v=@${lat},${lng}z${zoom}`;
}
```

이런! `zoom`만 존재하는데 그마저 `number | undefined`다. 문제는 `viewportForBounds`의 타입 선언이 **받는 것만이 아니라 내놓는 것에도 너그럽다**는 것이다. camera 결과를 타입 안전하게 쓰는 유일한 방법은 유니온 타입의 구성원마다 코드 분기를 만드는 것뿐이다. 옵셔널 속성과 유니온이 가득한 반환 타입은 함수를 쓰기 어렵게 만든다. **넓은 매개변수 타입은 편리하지만 넓은 반환 타입은 불편하다.**

## 2. 해법 — 정준 형태와 느슨한 형태의 구분

한 가지 방법은 좌표의 정준(canonical) 형태를 구별하는 것이다. 자바스크립트가 "배열"과 "배열 비슷한 것(array-like)"을 구별하듯(Item 17), `LngLat`과 `LngLatLike`를 구별한다. 또 완전히 정의된 `Camera` 타입과 `setCamera`가 받는 부분 버전도 구별한다.

```typescript
interface LngLat { lng: number; lat: number; };
type LngLatLike = LngLat | { lon: number; lat: number; } | [number, number];

interface Camera {
  center: LngLat;
  zoom: number;
  bearing: number;
  pitch: number;
}
interface CameraOptions extends Omit<Partial<Camera>, 'center'> {
  center?: LngLatLike;
}
type LngLatBounds =
  {northeast: LngLatLike, southwest: LngLatLike} |
  [LngLatLike, LngLatLike] |
  [number, number, number, number];

declare function setCamera(camera: CameraOptions): void;
declare function viewportForBounds(bounds: LngLatBounds): Camera;
```

느슨한 `CameraOptions`가 엄격한 `Camera`를 각색한 것이다. `setCamera`의 매개변수로 `Partial<Camera>`를 그냥 쓸 수는 없다 — `center`에 `LngLatLike` 객체를 허용하고 싶기 때문이다. `CameraOptions extends Partial<Camera>`라고 쓸 수도 없다 — `LngLatLike`는 `LngLat`의 서브타입이 아니라 **슈퍼타입**이다(거꾸로 느껴진다면 Item 7). 너무 복잡하게 느껴지면 반복을 감수하고 풀어 써도 된다.

```typescript
interface CameraOptions {
  center?: LngLatLike;
  zoom?: number;
  bearing?: number;
  pitch?: number;
}
```

어느 쪽이든 이제 `focusOnFeature`가 타입 체크를 통과하고 `zoom`의 타입도 `number`다. `viewportForBounds`는 훨씬 쓰기 쉬워졌다.

19가지 바운딩 박스 형태를 허용하는 것이 좋은 설계냐고? 아마 아닐 것이다. 하지만 그렇게 동작하는 라이브러리의 타입 선언을 쓴다면 그 동작을 모델링해야 한다 — **다만 반환 타입을 19가지로 만들지는 마라!**

## 3. 흔한 적용 — 배열 매개변수에는 Iterable

이 패턴의 가장 흔한 적용처가 배열을 매개변수로 받는 함수다.

```typescript
function sum(xs: number[]): number {
  let sum = 0;
  for (const x of xs) {
    sum += x;
  }
  return sum;
}
```

반환 타입 `number`는 아주 엄격하다. 좋다! 그런데 매개변수 `number[]`는? 배열의 능력을 거의 안 쓰고 있으니 더 느슨해도 된다 — `ArrayLike<number>`(Item 17)도, `readonly number[]`(Item 14)도 잘 맞는다. **순회만 필요하다면 가장 넓은 타입은 `Iterable`이다.**

```typescript
function sum(xs: Iterable<number>): number {
  let sum = 0;
  for (const x of xs) {
    sum += x;
  }
  return sum;
}

const six = sum([1, 2, 3]);
//    ^? const six: number
```

`Array`·`ArrayLike` 대신 `Iterable`을 쓰는 장점은 **제너레이터 표현식도 허용**된다는 것이다.

```typescript
function* range(limit: number) {
  for (let i = 0; i < limit; i++) {
    yield i;
  }
}
const zeroToNine = range(10);
//    ^? const zeroToNine: Generator<number, void, unknown>
const fortyFive = sum(zeroToNine);  // OK — 결과는 45
```

for-of 루프를 쓰고 있었다면 코드는 한 줄도 바꿀 필요 없다.

## 기억해야 할 것들

- 입력 타입은 출력 타입보다 넓은 경향이 있다. 옵셔널 속성과 유니온 타입은 반환 타입보다 매개변수 타입에서 더 흔하다.
- 넓은 반환 타입은 클라이언트가 쓰기 불편하므로 피하라.
- 매개변수와 반환 타입 사이에 타입을 재사용하려면 정준 형태(반환용)와 느슨한 형태(매개변수용)를 도입하라.
- 함수 매개변수를 순회만 한다면 `T[]` 대신 `Iterable<T>`를 사용하라.
