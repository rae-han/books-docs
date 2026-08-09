# Item 45: 안전하지 않은 타입 단언은 잘 타이핑된 함수 안에 숨기기 (Hide Unsafe Type Assertions in Well-Typed Functions)

## 핵심 질문

깨끗한 구현과 원하는 타입 시그니처 사이에서 골라야 한다면 무엇을 골라야 하는가? 단언은 어디에 두어야 하는가?

이상적인 세계에서 함수는 정확히 원하는 타입 시그니처를 갖고, 구현은 타입 체커를 통과하며, 단언도 any도 다른 건전성 함정(Item 48)도 없다. 다행히 우리가 쓰는 대부분의 함수가 그렇다. 하지만 항상 이상적이지는 않다.

**안전한 무단언 구현과 원하는 타입 시그니처 사이에서 골라야 한다면, 타입 시그니처를 골라라.** 시그니처는 함수의 공개 API로 코드의 나머지와 사용자에게 보인다. 구현은 사용자에게 숨겨진 세부 사항이다 - 단언과 any는 그 안에 감춰진다. 사용자의 삶을 어렵게 만드는 시그니처를 채택하느니, 안전하지 않은(하지만 잘 테스트된) 구현이 훨씬 낫다.

## 1. 시그니처를 양보하면 생기는 일

산봉우리 정보를 가져오는 코드:

```typescript
interface MountainPeak {
  name: string;
  continent: string;
  elevationMeters: number;
  firstAscentYear: number;
}

async function checkedFetchJSON(url: string): Promise<unknown> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Unable to fetch! ${response.statusText}`);
  }
  return response.json();
}

export async function fetchPeak(peakId: string): Promise<MountainPeak> {
  return checkedFetchJSON(`/api/mountain-peaks/${peakId}`);
  // ~~~~~ Type 'unknown' is not assignable to type 'MountainPeak'.
}
```

`checkedFetchJSON`은 fetch 성공 여부를 검사하고, 기본값인 any보다 안전한 `unknown`(Item 46)으로 JSON 응답을 준다. 그런데 unknown은 `MountainPeak`에 할당할 수 없어서 에러다. 구현에서 단언·any를 피하려고 반환 타입을 맞춰 바꾸면:

```typescript
export async function fetchPeak(peakId: string): Promise<unknown> {
  return checkedFetchJSON(`/api/mountain-peaks/${peakId}`);  // OK
}
```

타입 체커를 통과하고 안전하지 않은 단언도 없다(좋다!). 하지만 대가가 크다 - `fetchPeak`이 극도로 쓰기 어려운 함수가 됐다.

```typescript
async function getPeaksByHeight(): Promise<MountainPeak[]> {
  const peaks = await Promise.all(sevenPeaks.map(fetchPeak));
  return peaks.toSorted(
    //   ~~~ Type 'unknown' is not assignable to type 'MountainPeak'.
    (a, b) => b.elevationMeters - a.elevationMeters
    //        ~         ~ 'b' and 'a' are of type 'unknown'
  );
}
```

호출하는 코드마다 타입 단언을 써야 할 판이다 - 중복이고 지루하며, **곳에 따라 다른 타입을 단언할 가능성**까지 생긴다.

## 2. 단언을 구현 안에 숨겨라

타입 체커를 달래려고 반환 타입을 바꾸는 대신, **시그니처를 원래대로 두고 함수 본문에 단언을 넣는다.**

```typescript
export async function fetchPeak(peakId: string): Promise<MountainPeak> {
  return checkedFetchJSON(
    `/api/mountain-peaks/${peakId}`,
  ) as Promise<MountainPeak>;
}
```

단언이 구현 속에 감춰지자, 호출 코드는 우리의 안전하지 않은 비밀을 전혀 모른 채 깨끗하게 써진다.

```typescript
async function getPeaksByContinent(): Promise<MountainPeak[]> {
  const peaks = await Promise.all(sevenPeaks.map(fetchPeak));  // 단언 없음!
  return peaks.toSorted((a, b) => a.continent.localeCompare(b.continent));
}
```

단언을 한곳에 모은 덕에 **안전성을 올리기도 쉬워졌다.** 응답의 형태를 일부라도 검사하는 버전:

```typescript
export async function fetchPeak(peakId: string): Promise<MountainPeak> {
  const maybePeak = checkedFetchJSON(`/api/mountain-peaks/${peakId}`);
  if (
    !maybePeak ||
    typeof maybePeak !== 'object' ||
    !('firstAscentYear' in maybePeak)
  ) {
    throw new Error(`Invalid mountain peak: ${JSON.stringify(maybePeak)}`);
  }
  return checkedFetchJSON(
    `/api/mountain-peaks/${peakId}`,
  ) as Promise<MountainPeak>;
}
```

모든 호출 지점에서 이런 형태 검사를 할 리는 없지만, 단언이 한곳에 있으면 하기 쉽다. (이런 검증 코드를 자주 쓰게 된다면 Item 74의 체계적인 런타임 타입 검증 접근들을 보라 - 전부 잘 타이핑된 함수 안에 타입 단언을 숨긴 것들이다!)

단언을 숨기는 또 다른 방법은 **단일 오버로드**다.

```typescript
export async function fetchPeak(peakId: string): Promise<MountainPeak>;
export async function fetchPeak(peakId: string): Promise<unknown> {
  return checkedFetchJSON(`/api/mountain-peaks/${peakId}`);  // OK
}

const denali = fetchPeak('denali');
//    ^? const denali: Promise<MountainPeak>
```

오버로드가 호출자에게는 구현과 다른 타입 시그니처를 보여 준다. 타입스크립트가 두 시그니처의 호환성은 검사해 주니 약간의 안전은 있지만, 근본적으로 타입 단언과 다르지 않다 - 여전히 데이터 검증을 곁들이는 것이 좋다.

## 3. 타입 체커가 못 따라올 때 - any도 숨겨라

타입 체커가 코드를 따라오지 못해 단언에 내몰릴 때도 있다. 두 객체의 얕은 동등성을 검사하는 함수:

```typescript
function shallowObjectEqual(a: object, b: object): boolean {
  for (const [k, aVal] of Object.entries(a)) {
    if (!(k in b) || aVal !== b[k]) {
      //                      ~~~~ Element implicitly has an 'any' type
      //                           because type '{}' has no index signature
      return false;
    }
  }
  return Object.keys(a).length === Object.keys(b).length;
}
```

방금 `k in b`를 확인했는데도 `b[k]` 접근에 항의하는 것이 놀랍지만, 그런다. `@ts-expect-error`나 any에 의지해야 한다. **잘못된 수정**은 `b`의 타입을 any로 바꾸는 것 - 런타임에 터질 코드를 허용하게 된다.

```typescript
shallowObjectEqualBad({x: 1}, null);  // OK - 런타임에 예외
```

any를 함수 구현 **안에** 숨기는 것이 낫다.

```typescript
function shallowObjectEqualGood(a: object, b: object): boolean {
  for (const [k, aVal] of Object.entries(a)) {
    if (!(k in b) || aVal !== (b as any)[k]) {
      // `(b as any)[k]`는 방금 `k in b`를 확인했으므로 OK
      return false;
    }
  }
  return Object.keys(a).length === Object.keys(b).length;
}
```

이 any는 좁게 스코프되어 있고(Item 43), 함수의 타입 시그니처에 영향을 주지 않으며, 왜 유효한지 설명하는 주석까지 있다. any와 타입 단언의 훌륭한 사용이다 - 코드는 올바르고, 시그니처는 명확하고, 사용자는 아무것도 모른다.

> **실무 팁**: 모든 코드에 유닛 테스트를 써야 하지만, 타입 단언을 쓰는 코드라면 더더욱이다. 타입스크립트에게 "날 믿어"라고 말한 이상, 그것이 사실임을 증명할 책임은 나에게 있다. 단언이 유효한 이유를 설명하는 주석도 좋지만, 철저한 테스트가 더 나은 정당성 입증이다.

## 기억해야 할 것들

- 때로는 안전하지 않은 타입 단언과 any가 필요하거나 편리하다. 써야 한다면 올바른 시그니처를 가진 함수 안에 숨겨라.
- 구현의 타입 에러를 고치겠다고 함수의 타입 시그니처를 망가뜨리지 마라.
- 타입 단언이 왜 유효한지 설명하고, 코드를 철저히 유닛 테스트하라.
