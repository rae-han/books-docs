# Item 61: Record 타입으로 값들을 동기화하기 (Use Record Types to Keep Values in Sync)

## 핵심 질문

인터페이스에 속성이 추가될 때 관련 코드의 갱신을 어떻게 강제하는가? "fail open"과 "fail closed"의 딜레마에서 세 번째 길은?

산점도를 그리는 UI 컴포넌트가 있다. 표시와 동작을 통제하는 여러 종류의 속성이 있다.

```typescript
interface ScatterProps {
  // 데이터
  xs: number[];
  ys: number[];
  // 표시
  xRange: [number, number];
  yRange: [number, number];
  color: string;
  // 이벤트
  onClick?: (x: number, y: number, index: number) => void;
}
```

불필요한 작업을 피하려고 필요할 때만 다시 그리고 싶다 — 데이터나 표시 속성이 바뀌면 다시 그려야 하지만 이벤트 핸들러가 바뀌면 그럴 필요 없다.

## 1. fail open vs fail closed

**보수적("fail open") 접근**:

```typescript
function shouldUpdate(
  oldProps: ScatterProps,
  newProps: ScatterProps
) {
  for (const kStr in oldProps) {
    const k = kStr as keyof ScatterProps;
    if (oldProps[k] !== newProps[k]) {
      if (k !== 'onClick') return true;
    }
  }
  return false;
}
```

(루프의 keyof 단언은 Item 60 참고 — 값의 타입이 아니라 동등성만 보므로 안전하다.) 새 속성이 추가되면 그것이 바뀔 때마다 다시 그린다. 장점은 차트가 항상 올바르게 보인다는 것, 단점은 너무 자주 그릴 수 있다는 것.

**"fail closed" 접근**:

```typescript
function shouldUpdate(
  oldProps: ScatterProps,
  newProps: ScatterProps
) {
  return (
    oldProps.xs !== newProps.xs ||
    oldProps.ys !== newProps.ys ||
    oldProps.xRange !== newProps.xRange ||
    oldProps.yRange !== newProps.yRange ||
    oldProps.color !== newProps.color
    // (onClick 체크 없음)
  );
}
```

불필요한 다시 그리기는 없지만 **필요한 그리기가 누락**될 수 있다. 최적화의 중요한 원칙 — "먼저, 해를 끼치지 마라(first, do no harm)". 성능을 위해 올바른 동작을 희생하면 안 된다.

어느 쪽도 이상적이지 않다. 정말 원하는 것은 **새 속성을 추가하는 동료(또는 미래의 나)가 결정을 내리도록 강제하는 것**이다. 주석을 달아 볼 수도 있다.

```typescript
interface ScatterProps {
  // ...
  // 주의: 여기에 속성을 추가하면 shouldUpdate를 갱신할 것!
}
```

정말 이게 통하리라 기대하는가? 타입 체커가 강제해 주는 편이 낫다.

## 2. 세 번째 길 — Record로 "그냥 fail"

올바르게 설정하면 가능하다. 열쇠는 **올바른 키 집합을 가진 Record 타입**이다.

```typescript
const REQUIRES_UPDATE: Record<keyof ScatterProps, boolean> = {
  xs: true,
  ys: true,
  xRange: true,
  yRange: true,
  color: true,
  onClick: false,
};

function shouldUpdate(
  oldProps: ScatterProps,
  newProps: ScatterProps
) {
  for (const kStr in oldProps) {
    const k = kStr as keyof ScatterProps;
    if (oldProps[k] !== newProps[k] && REQUIRES_UPDATE[k]) {
      return true;
    }
  }
  return false;
}
```

`keyof ScatterProps` 구문이 `REQUIRES_UPDATE`가 `ScatterProps`와 정확히 같은 속성을 가져야 한다고 타입 체커에 알린다. 결정적으로 **전부 필수 속성**이다. 이제 미래에 새 속성을 추가하면:

```typescript
interface ScatterProps {
  // ...
  onDoubleClick?: () => void;
}

const REQUIRES_UPDATE: Record<keyof ScatterProps, boolean> = {
  //  ~~~~~~~~~~~~~~~ Property 'onDoubleClick' is missing in type ...
  // ...
};
```

확실히 문제를 들이민다! 속성을 지우거나 이름을 바꿔도 비슷한 에러가 난다. 잉여 속성 체크(Item 11)가 작동해서 객체가 **정확히** 원하는 속성 집합을 — 더도 덜도 아니게 — 갖도록 강제해 준다. 타입스크립트가 고전적인 fail open/fail closed 딜레마에 세 번째 선택지를 준 것이다: **"그냥 fail"** — 컴파일 타임에.

**boolean 값의 객체를 쓴 것이 중요하다.** 배열을 썼다면:

```typescript
const PROPS_REQUIRING_UPDATE: (keyof ScatterProps)[] = [
  'xs',
  'ys',
  // ...
];
```

같은 fail open/fail closed 선택으로 다시 내몰렸을 것이다(새 키를 빠뜨려도 에러가 안 나므로).

> **핵심 통찰**: Record와 매핑된 타입은 한 객체가 다른 객체와 정확히 같은 속성을 갖길 원할 때 이상적이다. 여기서는 fail open/fail closed 딜레마를 피하는 데 썼지만 응용은 많다 — 예를 들어 앱 상태의 모든 속성에 대응하는 URL 매개변수가 있도록 요구하기.

## 기억해야 할 것들

- fail open vs fail closed 딜레마를 인식하라.
- Record 타입으로 관련된 값과 타입을 동기화하라.
- 인터페이스에 새 속성이 추가될 때 선택을 강제하기 위해 Record 타입 사용을 고려하라.
