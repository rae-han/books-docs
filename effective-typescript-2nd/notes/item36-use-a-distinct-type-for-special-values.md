# Item 36: 특수 값에는 구별되는 타입 사용하기 (Use a Distinct Type for Special Values)

## 핵심 질문

`indexOf`의 -1 같은 "도메인 안의 특수 값"은 왜 타입 체커를 무력화하는가? 특수 케이스는 무엇으로 표현해야 하는가?

문자열의 `split`처럼 배열을 특정 값 주위로 쪼개는 함수를 만들어 보자.

```typescript
function splitAround<T>(vals: readonly T[], val: T): [T[], T[]] {
  const index = vals.indexOf(val);
  return [vals.slice(0, index), vals.slice(index+1)];
}

> splitAround([1, 2, 3, 4, 5], 3)
[ [ 1, 2 ], [ 4, 5 ] ]
```

기대대로다. 그런데 리스트에 없는 요소로 쪼개면 아주 뜻밖의 일을 한다.

```typescript
> splitAround([1, 2, 3, 4, 5], 6)
[ [ 1, 2, 3, 4 ], [ 1, 2, 3, 4, 5 ] ]
```

이 경우 함수가 무엇을 해야 하는지는 논쟁의 여지가 있어도, **저것**은 확실히 아니다. 이렇게 단순한 코드가 어떻게 이런 기괴한 동작을 낳았을까?

## 1. 근본 원인 — 특수 값이 일반 값과 같은 타입

`indexOf`는 요소를 못 찾으면 **-1**을 반환한다. 실패를 나타내는 특수 값이지만, -1은 그냥 평범한 숫자다. `slice`에 넘길 수 있고 산술도 된다. `slice`에 음수를 넘기면 배열 끝에서부터 센다는 뜻이 되고, -1에 1을 더하면 0이다. 그래서 위 코드는 이렇게 평가된다.

```typescript
[vals.slice(0, -1), vals.slice(0)]
// 첫 번째: 마지막 요소만 뺀 전부, 두 번째: 배열 전체 복사본
```

버그다. 더 아쉬운 것은 타입스크립트가 이 문제를 찾도록 도와주지 못했다는 점이다. 근본 원인은 `indexOf`가 못 찾았을 때 null 같은 것이 아니라 -1을 반환한다는 것. 왜일까? 1995년 넷스케이프 사무실에 가 보지 않고는 확실히 알 수 없지만 추측은 할 수 있다 — 자바스크립트는 자바의 영향을 짙게 받았고 자바의 `indexOf`도 같은 동작이다. 자바(그리고 C)에서는 함수가 "원시 값 또는 null"을 반환할 수 없다(객체/포인터만 nullable). 자바스크립트에는 없는 기술적 제약에서 온 동작일 것이다.

자바스크립트(그리고 타입스크립트)에서는 `number | null` 반환에 아무 문제가 없다. `indexOf`를 감싸자.

```typescript
function safeIndexOf<T>(vals: readonly T[], val: T): number | null {
  const index = vals.indexOf(val);
  return index === -1 ? null : index;
}
```

이걸 원래의 `splitAround`에 끼우면 **즉시 타입 에러 두 개**가 난다.

```typescript
function splitAround<T>(vals: readonly T[], val: T): [T[], T[]] {
  const index = safeIndexOf(vals, val);
  return [vals.slice(0, index), vals.slice(index+1)];
  //                     ~~~~~             ~~~~~ 'index' is possibly 'null'
}
```

정확히 원하던 것이다! `indexOf`에는 언제나 고려할 케이스가 둘 있다. 내장 버전으로는 타입스크립트가 둘을 구별하지 못했지만 감싼 버전으로는 구별한다 — 그리고 우리가 배열에 값이 있는 경우만 고려했다는 것을 본다. 다른 케이스를 명시적으로 처리하면 된다.

```typescript
function splitAround<T>(vals: readonly T[], val: T): [T[], T[]] {
  const index = safeIndexOf(vals, val);
  if (index === null) {
    return [[...vals], []];
  }
  return [vals.slice(0, index), vals.slice(index+1)];  // OK
}
```

이 동작이 옳은지는 논쟁할 수 있지만, 적어도 타입스크립트가 **그 논쟁을 하도록 강제**했다!

> **핵심 통찰**: 첫 구현의 근본 문제는 `indexOf`에 서로 다른 두 케이스가 있는데 특수 케이스의 반환값(-1)이 일반 케이스의 반환값과 **같은 타입**(number)이었다는 것이다. 타입스크립트 관점에서는 케이스가 하나뿐이었고, -1 체크를 안 했다는 것을 감지할 수 없었다.

## 2. 타입 설계에서 되풀이되는 상황

상품 타입이 있다고 하자.

```typescript
interface Product {
  title: string;
  priceDollars: number;
}
```

그런데 일부 상품의 가격이 미상임을 알게 됐다. 필드를 옵셔널로 바꾸거나 `number | null`로 바꾸면 마이그레이션과 많은 코드 수정이 필요할 것 같아 특수 값을 도입한다.

```typescript
interface Product {
  title: string;
  /** 상품 가격(달러), 가격 미상이면 -1 */
  priceDollars: number;
}
```

프로덕션에 배포한다. 일주일 뒤 상사가 격노해서 **왜 고객 카드에 돈을 입금하고 있는지** 묻는다. 팀이 롤백하는 동안 당신은 포스트모템을 쓰게 된다. 돌이켜 보면 그 타입 에러들을 처리하는 편이 훨씬 쉬웠을 것이다!

-1, 0, `""` 같은 **도메인 안의 특수 값**을 고르는 것은 정신적으로 `strictNullChecks`를 끄는 것과 같다. strictNullChecks가 꺼져 있으면 아무 타입에나 null을 할당할 수 있어서 타입스크립트가 `number`와 `number | null`을 구별하지 못하고 거대한 버그 부류가 통과한다. 켜면 구별할 수 있게 되어 새 문제들을 무더기로 감지한다. 도메인 안의 특수 값을 고르는 것은 사실상 **내 타입 안에 non-strict 구역을 파는 것**이다. 편법으로는 좋지만 최선은 아니다.

## 3. null/undefined도 만능은 아니다

특수 케이스를 표현하는 데 null과 undefined가 항상 옳은 것도 아니다 — 그 정확한 의미가 문맥에 따라 달라질 수 있기 때문이다. 네트워크 요청의 상태를 모델링하는데 null이 에러 상태, undefined가 대기 상태를 뜻하게 한다면 나쁜 생각이다. 그런 특수 상태는 태그된 유니온으로 더 명시적으로 표현하는 것이 낫다(Item 29의 예제 참고).

## 기억해야 할 것들

- 타입의 일반 값에 할당 가능한 특수 값을 피하라. 타입스크립트가 버그를 찾는 능력을 떨어뜨린다.
- 0·-1·`""` 대신 null이나 undefined를 특수 값으로 선호하라.
- null이나 undefined의 의미가 분명하지 않다면 태그된 유니온 사용을 고려하라.
