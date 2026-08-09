# Item 31: 문서에 타입 정보를 반복하지 않기 (Don't Repeat Type Information in Documentation)

## 핵심 질문

주석과 변수 이름에 타입 정보를 쓰면 왜 문제가 되는가? 강제되지 않는 약속은 어떻게 되는가?

이 코드는 무엇이 문제인가?

```typescript
/**
 * Returns a string with the foreground color.
 * Takes zero or one arguments. With no arguments, returns the
 * standard foreground color. With one argument, returns the foreground color
 * for a particular page.
 */
function getForegroundColor(page?: string) {
  return page === 'login' ? {r: 127, g: 127, b: 127} : {r: 0, g: 0, b: 0};
}
```

**코드와 주석이 서로 다른 말을 한다!** 문맥 없이는 어느 쪽이 맞는지 알 수 없지만 뭔가 잘못된 것은 분명하다. 저자의 한 교수는 이렇게 말하곤 했다.

> 코드와 주석이 어긋나면, 둘 다 틀린 것이다!

코드가 의도된 동작이라고 가정하면 이 주석의 문제는:

1. 함수가 색을 **string으로** 반환한다고 하는데 실제로는 `{r, g, b}` 객체를 반환한다.
2. 인수를 0개나 1개 받는다고 설명하는데, 타입 시그니처만 봐도 명백하다.
3. 쓸데없이 장황하다 — 주석이 함수 선언과 구현을 합친 것보다 길다!

타입스크립트의 타입 구문 체계는 간결하고 서술적이며 읽기 좋게 설계됐다. 수십 년 경력의 언어 전문가들이 만든 것이니, 함수의 입출력 타입을 표현하기에는 내 산문보다 거의 확실히 낫다. 그리고 **타입 구문은 컴파일러가 검사하므로 구현과 어긋날 수 없다.** `getForegroundColor`가 예전엔 string을 반환하다가 나중에 객체로 바뀌었을지 모른다 — 바꾼 사람이 긴 주석 갱신을 잊었을 뿐.

> **핵심 통찰**: 강제되지 않으면 아무것도 동기화 상태를 유지하지 못한다. 타입 구문에는 타입 체커라는 강제 장치가 있다. 타입 정보를 문서가 아니라 구문에 두면 코드가 진화해도 정보가 옳게 유지된다는 확신이 크게 올라간다.

더 나은 주석:

```typescript
/** Get the foreground color for the application or a specific page. */
function getForegroundColor(page?: string): Color {
  // ...
}
```

특정 매개변수를 설명하고 싶으면 `@param` JSDoc 구문을 쓴다(Item 68).

## 1. "변경하지 않음" 주석도 의심하라

```typescript
/** Sort the strings by numeric value (i.e. "2" < "10"). Does not modify nums. */
function sortNumerically(nums: string[]): string[] {
  return nums.sort((a, b) => Number(a) - Number(b));
}
```

주석은 매개변수를 수정하지 않는다는데, 배열의 `sort`는 제자리에서 동작하므로 **확실히 수정한다**. 주석의 주장은 별 가치가 없다. 대신 매개변수를 `readonly`(Item 14)로 선언하면 타입스크립트가 계약을 강제해 준다.

```typescript
/** Sort the strings by numeric value (i.e. "2" < "10"). */
function sortNumerically(nums: readonly string[]): string[] {
  return nums.sort((a, b) => Number(a) - Number(b));
  //          ~~~~ Property 'sort' does not exist on 'readonly string[]'.
}
```

올바른 구현은 배열을 복사하거나 불변 메서드 `toSorted`를 쓴다.

```typescript
/** Sort the strings by numeric value (i.e. "2" < "10"). */
function sortNumerically(nums: readonly string[]): string[] {
  return nums.toSorted((a, b) => Number(a) - Number(b));  // OK
}
```

## 2. 변수 이름에도 타입을 넣지 마라 — 단위는 예외

주석에 해당하는 이야기는 변수 이름에도 해당한다. 변수를 `ageNum`이라 부르지 말고 `age`라 부르고 **진짜로 number이게 하라**.

예외는 **단위가 있는 숫자**다. 단위가 불분명하면 변수나 속성 이름에 포함하는 것이 좋다 — `time`보다 `timeMs`가, `temperature`보다 `temperatureC`가 훨씬 명확하다. 단위를 더 타입 안전하게 모델링하는 "브랜드" 기법은 Item 64에서 다룬다.

## 기억해야 할 것들

- 주석과 변수 이름에 타입 정보를 반복하지 마라. 좋아 봐야 타입 선언의 중복이고, 나쁘면 상충하는 정보가 된다.
- 매개변수를 변경하지 않는다고 말하는 대신 `readonly`로 선언하라.
- 타입에서 분명하지 않다면 단위를 변수 이름에 포함하는 것을 고려하라(예: `timeMs`, `temperatureC`).
