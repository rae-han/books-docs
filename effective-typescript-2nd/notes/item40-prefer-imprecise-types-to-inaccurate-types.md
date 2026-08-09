# Item 40: 부정확한 타입보다 덜 정밀한 타입 선호하기 (Prefer Imprecise Types to Inaccurate Types)

## 핵심 질문

타입을 더 정밀하게 만드는 것은 언제 역효과가 되는가? "타입 안전의 불쾌한 골짜기"란 무엇인가?

타입 선언을 쓰다 보면 동작을 더 정밀하게 또는 덜 정밀하게 모델링할 수 있는 상황을 반드시 만난다. 타입의 정밀도는 일반적으로 좋은 것이다 - 사용자가 버그를 잡고 도구의 혜택을 누리게 해 준다. 하지만 정밀도를 올릴 때는 조심하라. **실수하기 쉽고, 틀린 타입은 타입이 없는 것보다 나쁠 수 있다.**

## 1. GeoJSON - 정밀하게 만들려다 부정확해진 사례

GeoJSON 지오메트리는 몇 가지 타입 중 하나이고 좌표 배열의 모양이 서로 다르다.

```typescript
interface Point {
  type: 'Point';
  coordinates: number[];
}
interface LineString {
  type: 'LineString';
  coordinates: number[][];
}
interface Polygon {
  type: 'Polygon';
  coordinates: number[][][];
}
type Geometry = Point | LineString | Polygon;  // 그 외 몇 개 더
```

괜찮지만 좌표의 `number[]`가 좀 덜 정밀하다. 사실 위도·경도니까 튜플이 낫지 않을까?

```typescript
type GeoPosition = [number, number];
interface Point {
  type: 'Point';
  coordinates: GeoPosition;
}
```

더 정밀해진 타입을 세상에 공개하고 찬사가 쏟아지길 기다린다. 불행히도 한 사용자가 새 타입이 모든 것을 망가뜨렸다고 항의한다. **위도·경도만 써 왔더라도, GeoJSON의 position은 세 번째 요소(고도)와 그 이상도 허용한다.** 타입 선언을 더 정밀하게 만들려다 도를 넘어 **부정확**해진 것이다! 사용자는 계속 쓰려면 타입 단언을 도입하거나 `as any`로 타입 체커를 통째로 꺼야 한다.

## 2. 정밀도의 스펙트럼 - Mapbox 표현식

JSON으로 정의된 Lisp풍 언어의 타입 선언을 시도해 보자.

```
12
"red"
["+", 1, 2]                              // 3
["/", 20, 2]                             // 10
["case", [">", 20, 10], "red", "blue"]   // "red"
["rgb", 255, 0, 127]                     // "#FF007F"
```

Mapbox 라이브러리가 이런 시스템으로 지도 피처의 외관을 결정한다. 시도할 수 있는 정밀도의 스펙트럼:

1. 아무거나 허용
2. 문자열·숫자·배열 허용
3. 문자열·숫자·"알려진 함수 이름으로 시작하는 배열" 허용
4. 각 함수의 인수 **개수**까지 검사
5. 각 함수의 인수 **타입**까지 검사

1·2단계는 단순하다.

```typescript
type Expression1 = any;
type Expression2 = number | string | any[];
```

모든 유효한 프로그램을 허용하는 타입 시스템을 "완전(complete)"하다고 한다. 이 둘은 모든 유효한 Mapbox 표현식을 허용한다 - 거짓 양성이 없다. 대신 거짓 음성(잡히지 않는 무효 표현식)이 많다. 즉 정밀하지 않다.

완전성을 잃지 않고 정밀도를 올려 보자. 회귀를 막기 위해 유효/무효 표현식의 테스트 세트를 도입한다(타입 테스트는 Item 55). 3단계 - 튜플 첫 요소를 문자열 리터럴 유니온으로:

```typescript
type FnName = '+' | '-' | '*' | '/' | '>' | '<' | 'case' | 'rgb';
type CallExpression = [FnName, ...any[]];
type Expression3 = number | string | CallExpression;

const invalidExpressions: Expression3[] = [
  true,
  // Error: Type 'boolean' is not assignable to type 'Expression3'
  ["**", 2, 31],
  // ~~ Type '"**"' is not assignable to type 'FnName'
  ["rgb", 255, 0, 127, 0],                          // 잡혀야 하는데 안 잡힘
  ["case", [">", 20, 10], "red", "blue", "green"],  // 잡혀야 하는데 안 잡힘
];
```

새로 잡힌 에러 하나, 회귀 없음. 꽤 좋다! 다만 타입 선언이 Mapbox 버전과 더 밀접해졌다 - Mapbox가 함수를 추가하면 타입도 추가해야 한다. **더 정밀한 타입은 유지 비용도 더 높다.**

4단계(인수 개수 검사)는 타입이 재귀적이어야 해서 더 까다롭다. "짝수 길이의 배열"이어야 하는 `CaseCall`을 인터페이스로 정의하는 트릭까지 동원하면 가능은 하다.

```typescript
type Expression4 = number | string | CallExpression;
type CallExpression = MathCall | CaseCall | RGBCall;

type MathCall = [
  '+' | '-' | '/' | '*' | '>' | '<',
  Expression4,
  Expression4,
];

interface CaseCall {
  0: 'case';
  [n: number]: Expression4;
  length: 4 | 6 | 8 | 10 | 12 | 14 | 16;  // 등등
}

type RGBCall = ['rgb', Expression4, Expression4, Expression4];
```

이제 무효 표현식이 전부 에러가 된다. "짝수 길이 배열"을 인터페이스로 표현할 수 있다는 것도 흥미롭다. 하지만 에러 메시지 일부가 상당히 헷갈린다 - 특히 `Type '5' is not assignable to type '4 | 6 | 8 | 10 | 12 | 14 | 16'` 같은 것.

이것이 덜 정밀한 타입보다 개선일까? 잘못된 사용을 더 많이 잡는 것은 분명 승리지만, **헷갈리는 에러 메시지는 타입을 다루기 어렵게 만든다.** Item 6에서 봤듯 언어 서비스는 타입 체크만큼이나 타입스크립트 경험의 일부다 - 타입 선언이 만들어 내는 에러 메시지를 살펴보고, 동작해야 할 자리에서 자동완성을 시험해 보라. 더 정밀해졌는데 자동완성이 깨진다면 개발 경험은 나빠진 것이다.

복잡해진 타입 선언은 **버그가 스밀 확률**도 올렸다. `Expression4`는 모든 수학 연산자가 인수 2개를 받는다고 요구하지만, Mapbox 명세는 `+`·`*`가 더 받을 수 있고 `-`는 1개만 받아 부호 반전에 쓸 수도 있다고 말한다. `Expression4`는 이 모든 유효한 표현식에 잘못 에러를 낸다.

```typescript
const moreOkExpressions: Expression4[] = [
  ['-', 12],
  // ~~~~~~~ Type '["-", number]' is not assignable to type 'MathCall'
  //         Source has 2 element(s) but target requires 3.
  ['+', 1, 2, 3],
  //          ~ Type 'number' is not assignable to type 'undefined'.
  ['*', 2, 3, 4],
  //          ~ Type 'number' is not assignable to type 'undefined'.
];
```

또 정밀을 노리다 과녁을 지나쳐 부정확해졌다. 고칠 수는 있지만, 다른 것을 놓치지 않았다고 확신하려면 테스트 세트를 넓혀야 한다. **복잡한 코드가 더 많은 테스트를 요구하듯 타입도 마찬가지다.**

## 3. 불쾌한 골짜기

타입을 다듬을 때 "불쾌한 골짜기(uncanny valley)" 은유가 도움이 된다. 만화 같은 그림이 실물에 가까워질수록 더 사실적으로 느껴지지만, 어느 지점까지만이다 - 지나치게 사실적이면 남은 몇 안 되는 부정확함에 오히려 시선이 쏠린다.

같은 원리로, `any`처럼 매우 덜 정밀한 타입을 다듬는 것은 거의 항상 도움이 된다. 하지만 타입이 정밀해질수록 **정확할 것이라는 기대도 함께 커진다.** 타입이 대부분의 에러를 잡아 줄 것이라 신뢰하기 시작하면 부정확함이 더 도드라진다. 타입 에러를 몇 시간 추적했는데 결국 타입이 틀린 것이었다면, 타입 선언에 대한 - 어쩌면 타입스크립트 자체에 대한 - 신뢰가 무너진다.

> **핵심 통찰**: 정확하게 모델링할 수 없다면 부정확하게 모델링하지 마라. `any`나 `unknown`으로 빈틈을 인정하라. 복잡한데 부정확한 타입은 단순하고 덜 정밀한 타입보다 나쁜 경우가 많다.

## 기억해야 할 것들

- 타입 안전의 불쾌한 골짜기를 피하라: 복잡하지만 부정확한 타입은 더 단순하고 덜 정밀한 타입보다 나쁜 경우가 많다. 정확히 모델링할 수 없다면 부정확하게 모델링하지 말고 `any`나 `unknown`으로 빈틈을 인정하라.
- 타이핑을 점점 정밀하게 만들면서 에러 메시지와 자동완성에 주의를 기울여라. 정확성만이 아니라 개발자 경험도 중요하다.
- 타입이 복잡해질수록 타입 테스트 스위트도 확장되어야 한다.
