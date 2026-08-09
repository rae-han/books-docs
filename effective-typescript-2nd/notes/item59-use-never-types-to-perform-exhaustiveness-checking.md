# Item 59: never 타입으로 소진 체크 수행하기 (Use Never Types to Perform Exhaustiveness Checking)

## 핵심 질문

유니온에 새 케이스를 추가했을 때, 그것을 처리하지 않은 switch 문들을 어떻게 타입 에러로 만드는가?

정적 타입 분석은 하지 말아야 할 일을 한 곳(잘못된 할당, 없는 속성 참조, 잘못된 인수 개수)을 잘 찾아 준다. 하지만 **누락의 오류** — 해야 할 일을 안 한 경우 — 도 있다. 타입스크립트가 늘 스스로 잡아 주지는 않지만, switch나 if의 빠진 케이스를 타입 에러로 바꾸는 인기 있는 트릭이 있다 — 소진 체크(*exhaustiveness checking - 유니온의 모든 케이스가 처리됐는지 확인하는 것*)다.

## 1. 누락의 오류가 생기는 과정

캔버스 드로잉 프로그램의 도형을 태그된 유니온으로 정의하고 그리는 함수가 있다.

```typescript
type Coord = [x: number, y: number];
interface Box {
  type: 'box';
  topLeft: Coord;
  size: Coord;
}
interface Circle {
  type: 'circle';
  center: Coord;
  radius: number;
}
type Shape = Box | Circle;

function drawShape(shape: Shape, context: CanvasRenderingContext2D) {
  switch (shape.type) {
    case 'box':
      context.rect(...shape.topLeft, ...shape.size);
      break;
    case 'circle':
      context.arc(...shape.center, shape.radius, 0, 2 * Math.PI);
      break;
  }
}
```

여기까지 좋다. 이제 셋째 도형 `Line`을 추가하면 — **타입 에러는 없지만 버그가 생겼다.** `drawShape`가 선을 조용히 무시한다.

## 2. never와 assertUnreachable

소진된 switch 뒤의 타입에 단서가 있다.

```typescript
function processShape(shape: Shape) {
  switch (shape.type) {
    case 'box': break;
    case 'circle': break;
    case 'line': break;
    default:
      shape
      // ^? (parameter) shape: never
  }
}
```

`never`는 도메인이 공집합인 바텀 타입이다(Item 7). 모든 케이스를 다뤘다면 남는 것은 never뿐이고, **케이스를 빠뜨렸다면 never가 아닌 무언가**(예: `Line`)가 남는다. 어떤 값도 never에 할당할 수 없으므로 이것으로 누락을 타입 에러로 바꾼다.

```typescript
function assertUnreachable(value: never): never {
  throw new Error(`Missed a case! ${value}`);
}

function drawShape(shape: Shape, context: CanvasRenderingContext2D) {
  switch (shape.type) {
    case 'box':
      context.rect(...shape.topLeft, ...shape.size);
      break;
    case 'circle':
      context.arc(...shape.center, shape.radius, 0, 2 * Math.PI);
      break;
    default:
      assertUnreachable(shape);
      //                ~~~~~
      // ... type 'Line' is not assignable to parameter of type 'never'.
  }
}
```

빠진 케이스를 채우면 에러가 사라진다. **채운 뒤에도 `assertUnreachable` 호출을 남겨 둬야 한다** — 이름대로 도달 불가능하더라도, 나중에 도형을 또 추가할 때의 누락으로부터 지켜 준다.

왜 예외를 던질까? 잘 타이핑된 타입스크립트라면 도달 불가능하겠지만, `drawShape`가 자바스크립트에서 호출되거나 any 등 불건전한 타입(Item 48)으로 호출될 가능성은 언제나 있다. 예외는 타입 체크 시점만이 아니라 **런타임의 뜻밖의 값**으로부터도 보호해 준다.

## 3. 반환 타입 명시도 어느 정도 보호해 준다

`drawShape`는 부수효과만 있는 함수라 소진 체크가 특히 유용했다. 반환값이 있는 함수라면 **반환 타입 명시**가 어느 정도 보호를 준다.

```typescript
function getArea(shape: Shape): number {
  //       ~~~~~~ Function lacks ending return statement and
  //              return type does not include 'undefined'.
  switch (shape.type) {
    case 'box':
      const [width, height] = shape.size;
      return width * height;
    case 'circle':
      return Math.PI * shape.radius ** 2;
    // 'line' 누락!
  }
}
```

반환 타입을 생략했다면 에러 대신 `number | undefined`로 추론됐을 것이고, 에러는 `getArea`를 호출하는 다른 어딘가에서 났을 것이다 — 실수한 곳 가까이에서 에러가 나는 편이 낫다(Item 18의 다중 return 함수에 반환 타입을 달라는 조언). 이 에러는 `strictNullChecks`가 켜져 있을 때만 난다 — strictNullChecks를 쓸 훌륭한 이유다! 다만 undefined가 정당한 반환값이라면 이 검사는 보호가 안 되므로, 반환값이 있는 함수라도 소진 체크가 좋을 수 있다.

`assertUnreachable`의 반환 타입이 `never`인 것도 그래서다 — never는 모든 타입에 할당 가능하므로 함수의 반환 타입이 무엇이든 안전하게 `return assertUnreachable(shape)` 할 수 있다.

패턴의 변형들도 만나게 된다 — never로의 직접 할당(`const exhaustiveCheck: never = shape`)이나 `satisfies` 연산자(`shape satisfies never`). 전부 같은 방식으로 동작하니 마음에 드는 것을 쓰면 된다.

## 4. 두 타입의 조합(교차곱)까지 — 템플릿 리터럴 타입 결합

머리를 조금 쓰면 두 타입의 **모든 쌍**을 처리했는지도 확인할 수 있다. 가위바위보:

```typescript
type Play = 'rock' | 'paper' | 'scissors';

function shoot(a: Play, b: Play) {
  if (a === b) {
    console.log('draw');
  } else if (
    (a === 'rock' && b === 'scissors') ||
    (a === 'paper' && b === 'rock')
  ) {
    console.log('A wins');
  } else {
    console.log('B wins');
  }
}
```

케이스 하나를 놓쳤다 — A가 가위, B가 보면 A의 승리인데 B가 이겼다고 나온다. 템플릿 리터럴 타입(Item 54)과 소진 체크를 결합해 모든 경우를 명시적으로 다루도록 강제하자.

```typescript
function shoot(a: Play, b: Play) {
  const pair = `${a},${b}` as `${Play},${Play}`;  // 또는 as const
  //    ^? const pair: "rock,rock" | "rock,paper" | "rock,scissors" |
  //       "paper,rock" | "paper,paper" | "paper,scissors" |
  //       "scissors,rock" | "scissors,paper" | "scissors,scissors"
  switch (pair) {
    case 'rock,rock':
    case 'paper,paper':
    case 'scissors,scissors':
      console.log('draw');
      break;
    case 'rock,scissors':
    case 'paper,rock':
      console.log('A wins');
      break;
    case 'rock,paper':
    case 'paper,scissors':
    case 'scissors,rock':
      console.log('B wins');
      break;
    default:
      assertUnreachable(pair);
      //                ~~~~ Argument of type "scissors,paper" is not
      //                     assignable to parameter of type 'never'.
  }
}
```

기본이라면 `` `${a},${b}` ``의 타입은 string이지만, `` `${Play},${Play}` ``는 아홉 가지 쌍으로 이뤄진 string의 서브타입이다. 아홉을 다 다뤘는지 소진 체크를 적용하니 빠뜨린 하나가 타입 에러로 잡혔고, **에러에 빠뜨린 조합까지 나와 있다!** 자주는 아니지만 상태 간 전이를 모델링할 때 가끔 도움이 되는 기법이다.

> **실무 팁**: typescript-eslint의 `switch-exhaustiveness-check` 룰로도 소진 체크를 할 수 있다. `assertUnreachable`이 옵트인이라면 린터 룰은 옵트아웃이다 — 켜 보면 소진을 의도하지 않았던 switch나 타입 시스템으로 담기 어려운 이유로 소진인 switch가 드러날 수도 있지만, 버그도 찾게 될 테니 시도해 볼 가치가 있다.

## 기억해야 할 것들

- never 타입으로의 할당을 이용해 타입의 모든 가능한 값이 처리됐는지 확인하라("소진 체크").
- 여러 분기에서 반환하는 함수에는 반환 타입 구문을 추가하라. 그래도 명시적 소진 체크가 필요할 수 있다.
- 둘 이상의 타입의 모든 조합이 처리됐는지 확인하려면 템플릿 리터럴 타입 사용을 고려하라.
