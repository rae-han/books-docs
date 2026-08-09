# Item 38: 같은 타입의 매개변수 반복 피하기 (Avoid Repeated Parameters of the Same Type)

## 핵심 질문

`drawRect(25, 50, 75, 100, 1)` — 이 호출이 무엇을 하는지 왜 알 수 없는가? 타입 체커가 도와줄 수 있게 하려면?

이 함수 호출은 무엇을 하는가?

```typescript
drawRect(25, 50, 75, 100, 1);
```

매개변수 목록을 보지 않고는 알 수 없다. 가능성 몇 가지:

- (25, 50)을 왼쪽 위 꼭짓점으로 75×100 사각형을 불투명도 1.0으로 그린다.
- 꼭짓점이 (25, 50)과 (75, 100)인 50×50 사각형을 선 굵기 1픽셀로 그린다.

문맥이 없으면 이 함수가 올바르게 호출되고 있는지 알기 어렵다. 그리고 **매개변수가 전부 같은 타입(number)이라서, 순서를 섞거나 두 번째 좌표 대신 너비·높이를 넘겨도 타입 체커가 도와줄 수 없다.**

```typescript
function drawRect(x: number, y: number, w: number, h: number, opacity: number) {
  // ...
}
```

같은 타입의 매개변수를 연속으로 받는 함수는 잘못된 호출을 타입 체커가 잡을 수 없으므로 오류에 취약하다.

## 1. 해법 ① — 구별되는 타입 도입

```typescript
interface Point {
  x: number;
  y: number;
}
interface Dimension {
  width: number;
  height: number;
}
function drawRect(topLeft: Point, size: Dimension, opacity: number) {
  // ...
}

drawRect({x: 25, y: 50}, {x: 75, y: 100}, 1.0);
//                       ~
// Argument ... is not assignable to parameter of type 'Dimension'.
```

세 매개변수가 세 가지 다른 타입이 되자 타입 체커가 구별할 수 있고, 점 두 개를 넘기는 잘못된 호출이 에러가 된다.

## 2. 해법 ② — 단일 객체 매개변수

```typescript
interface DrawRectParams extends Point, Dimension {
  opacity: number;
}
function drawRect(params: DrawRectParams) { /* ... */ }

drawRect({x: 25, y: 50, width: 75, height: 100, opacity: 1.0});
```

위치 매개변수 대신 객체를 받도록 리팩터링하면 사람 독자에게 명확해지고, 각 숫자에 이름이 붙으므로 타입 체커도 잘못된 호출을 잡을 수 있게 된다.

## 3. 매개변수 개수와 예외

코드가 진화하면 함수는 점점 더 많은 매개변수를 받게 된다. 처음엔 위치 매개변수로 충분했어도 언젠가 문제가 된다. 속담처럼 — "매개변수가 10개인 함수가 있다면, 아마 몇 개를 빠뜨렸을 것이다." 매개변수가 서너 개를 넘으면 더 적게 받도록 리팩터링해야 한다(typescript-eslint의 `max-params` 룰로 강제 가능). **타입이 같은 매개변수라면 더욱 경계해야 한다 — 두 개만 되어도 문제일 수 있다.**

이 규칙의 예외:

1. **인수가 교환 가능한 경우**(순서가 무관): `max(a, b)`, `isEqual(a, b)`는 모호하지 않다.
2. **"자연스러운" 순서가 있는 경우**: `array.slice(start, stop)`은 stop, start보다 말이 된다. 단 조심할 것 — 무엇이 "자연스러운" 순서인지 개발자들이 늘 동의하는 것은 아니다. (연·월·일? 월·일·년? 일·월·년?)

> Make interfaces easy to use correctly and hard to use incorrectly.<br>인터페이스는 올바르게 쓰기는 쉽고 잘못 쓰기는 어렵게 만들어라.<br>— 스콧 마이어스(Scott Meyers), "Effective C++"

반박하기 어려운 말이다!

## 기억해야 할 것들

- 같은 타입스크립트 타입의 매개변수를 연속으로 받는 함수를 쓰지 마라.
- 매개변수가 많은 함수는 구별되는 타입의 더 적은 매개변수 또는 단일 객체 매개변수를 받도록 리팩터링하라.
