# Appendix B: Null Safety and Optionals (널 안전성과 옵셔널)

## 핵심 질문

널 안전성(*null safety - 값이 널일 수 있는지를 타입에 표시하고 컴파일러가 널 검사를 강제하는 기능*)은 정확히 무엇을 해 주는가? 널 안전성을 지원하는 언어에서는 널을 어떻게 표시하고 확인하는가? 널 안전성을 지원하지 않는 언어에서는 옵셔널(*Optional - 값이 있을 수도, 없을 수도 있음을 감싸서 표현하는 타입*)로 어떻게 같은 안전성을 얻는가? TypeScript는 이 문제를 어떻게 기본적으로 해결하는가?

---

## 0. 이 부록에서 다루는 것 · 코드 표기 규약

- 널 안전성을 지원하는 언어에서 널을 표시(`?`)하고 확인하는 방법 (B.1)
- 널 확인을 간결하게 해 주는 널 조건부 연산자 (B.1.1)
- 널 안전성이 없는 언어에서 옵셔널 타입으로 대응하는 방법 (B.2)
- C++ 표준 라이브러리 옵셔널의 미묘한 제약

이 부록은 **2장에서 소개한 널 안전성 규약**을 자세히 풀어 쓴 것이며, 널 처리는 **4장(오류 전달)**·**6장(예측 벗어나는 코드 피하기)**과도 밀접하다. 널을 제대로 다루지 않으면 시스템이 예측 불가능하게 멈추기 때문이다.

> **코드 표기 규약**: 원서는 언어 중립적 **의사코드(pseudocode)**를 쓴다. 이 노트는 원서 의사코드를 `<details>`로 접어 두고(원문 확인용), 그 아래에 **TypeScript 변환본**을 펼쳐 둔다. 의사코드의 널 규약(`T?` = 널 가능, `== null` = 널 비교)은 TypeScript에서 각각 `T | null`, `=== null`로 옮긴다. TypeScript는 `strictNullChecks` 아래에서 유니언 타입 `T | null`로 널 안전성을 **기본 제공**하므로, 원서가 다른 언어를 위해 설명하는 장치들이 상당 부분 언어 차원에서 이미 해결되어 있다.

---

## 1. 널 안전성 사용 (B.1)

사용하는 언어가 널 안전성을 지원하거나 활성화할 수 있다면, **타입에 애너테이션을 달아 널이 가능함을 표시**하는 방법이 있다. 이때 `?` 기호를 쓰는 경우가 많다. 아래 함수는 리스트에서 다섯 번째 요소를 반환하되, 요소가 5개 미만이면 값을 얻을 수 없으므로 널을 반환한다.

<details>
<summary>의사코드 (원서)</summary>

```java
// Element? 에서 '?' 기호는 반환 유형이 널일 수 있음을 나타낸다
Element? getFifthElement(List<Element> elements) {
  if (elements.size() < 5) {
    return null;
  }
  return elements[4];
}
```

</details>

```typescript
// 반환 타입 'Element | null'이 널 가능성을 타입 수준에서 드러낸다
function getFifthElement(elements: Element[]): Element | null {
  if (elements.length < 5) {
    return null;
  }
  return elements[4];
}
```

이 함수를 호출하는 코드가 **널을 반환하는 경우를 처리하지 않으면 컴파일되지 않는다.** 예를 들어 `displayElement()`는 매개변수 타입이 `Element?`가 아니라 `Element`이므로 널이 아닌 값만 받는데, 여기에 널이 가능한 값을 그대로 넘기면 컴파일러가 오류를 낸다.

<details>
<summary>의사코드 (원서) — 널 확인 없이는 컴파일되지 않는다</summary>

```java
// 매개변수 타입이 Element(널 불가)이므로 널이 아닌 값만 받는다
void displayElement(Element element) { ... }

void displayFifthElement(List<Element> elements) {
  // fifthElement 는 Element? 타입이므로 널이 가능하다
  Element? fifthElement = getFifthElement(elements);
  // displayElement()는 널이 아닌 값을 예상하는데 널이 가능한 값으로 호출되므로
  // 이 라인에서 컴파일러 오류가 발생한다
  displayElement(fifthElement);
}
```

</details>

```typescript
// 매개변수 타입이 Element(널 불가)이므로 널이 아닌 값만 받는다
function displayElement(element: Element): void {
  /* ... */
}

function displayFifthElement(elements: Element[]): void {
  const fifthElement: Element | null = getFifthElement(elements);
  // ❌ 컴파일 오류: 'Element | null' 형식은 'Element' 형식에 할당할 수 없다
  displayElement(fifthElement);
}
```

코드가 컴파일되게 하려면 반환값이 널이 아닌지 먼저 확인한 뒤에 `displayElement()`를 호출해야 한다. 컴파일러는 **값이 널이 아닐 때만 도달할 수 있는 코드 경로를 유추**하므로, 널 확인 이후 지점에서는 그 값을 안전하게 사용할 수 있다고 판단한다. (TypeScript에서는 이를 **제어 흐름 기반 타입 좁히기**라고 부른다.)

<details>
<summary>의사코드 (원서) — 널을 확인하면 컴파일된다</summary>

```java
void displayFifthElement(List<Element> elements) {
  Element? fifthElement = getFifthElement(elements);
  if (fifthElement == null) {
    // 널이면 함수가 조기에 반환된다
    displayMessage("Fifth element doesn't exist");
    return;
  }
  // 컴파일러는 이 라인이 fifthElement가 널이 아닐 때만 도달 가능하다고 유추한다
  displayElement(fifthElement);
}
```

</details>

```typescript
function displayFifthElement(elements: Element[]): void {
  const fifthElement: Element | null = getFifthElement(elements);
  if (fifthElement === null) {
    // 널이면 함수가 조기에 반환된다
    displayMessage("Fifth element doesn't exist");
    return;
  }
  // 이 지점에서 타입이 'Element'로 좁혀지므로 안전하게 사용할 수 있다
  displayElement(fifthElement);
}
```

> **참고 — 컴파일러 경고 vs 오류(C#)**: C#에서는 널이 가능한 값을 잘못 사용해도 컴파일러 **경고**만 보여 주고 오류는 내지 않기 때문에 안전하지 않을 수 있다.<br>C#을 쓰면서 널 안전성을 활성화했다면, 경고가 아니라 **오류**로 처리하도록 설정해 이런 경우가 눈에 띄게 만드는 것이 좋다.

이처럼 널 안전성을 사용하면 컴파일러가 논리적으로 널이 가능한 경로와 그렇지 않은 경로를 추적하여 **널 값이 안전하지 않게 사용되는 일이 없도록** 보장한다. 덕분에 널 포인터 예외(*null pointer exception - 널 값의 멤버에 접근하려다 발생하는 런타임 오류*) 같은 위험 없이 널 값의 유용함만 누릴 수 있다.

---

## 2. 널 확인 — 간결한 구문 (B.1.1)

널 안전성을 지원하는 언어는 값이 널인지 확인하고 **널이 아닐 때만 멤버 함수나 속성에 접근**하도록 하는 간결한 구문을 제공하는 경우가 많다. 이렇게 하면 반복적인 널 확인 구문을 줄일 수 있다. 다만 이런 문법을 제공하지 않는 언어가 더 많으므로, 이 책의 의사코드 규약은 널을 일일이 확인하는 다소 장황한 방식을 따른다.

예를 들어 주소를 조회하되 찾지 못하면 널을 반환하는 `lookupAddress()` 함수가 있고, 호출하는 쪽에서 반환값이 널이 아닐 때만 `getCity()`를 호출하려 한다고 하자. 장황한 방식은 다음과 같다.

<details>
<summary>의사코드 (원서) — 장황한 널 확인</summary>

```java
Address? lookupAddress() {
  ...
  return null; // 주소를 찾지 못하면 널을 반환한다
  ...
}

City? getCity() {
  Address? address = lookupAddress();
  if (address == null) {
    return null;
  }
  return address.getCity();
}
```

</details>

```typescript
function lookupAddress(): Address | null {
  /* ... */
  return null; // 주소를 찾지 못하면 널을 반환한다
}

function getCity(): City | null {
  const address: Address | null = lookupAddress();
  if (address === null) {
    return null;
  }
  return address.getCity();
}
```

그러나 널 안전성을 지원하는 대부분의 언어는 이 코드를 더 간결하게 만들 수 있는 구문을 제공한다. 예를 들어 **널 조건부 연산자(*null conditional operator - 앞 값이 널이면 멤버 접근을 건너뛰고 널을 반환하는 연산자, 보통 `?.`*)**를 쓰면 다음처럼 한 줄로 쓸 수 있다.

<details>
<summary>의사코드 (원서) — 널 조건부 연산자</summary>

```java
City? getCity() {
  return lookupAddress()?.getCity();
}
```

</details>

```typescript
function getCity(): City | null {
  // ?. 은 옵셔널 체이닝(널 조건부 연산자). 앞 값이 널/undefined면 즉시 undefined로 단락된다.
  // 반환 타입을 'City | null'로 맞추기 위해 ?? null 로 undefined를 null로 바꾼다
  return lookupAddress()?.getCity() ?? null;
}
```

> **핵심 통찰**: TypeScript의 옵셔널 체이닝 `?.`은 널 조건부 연산자에 정확히 대응한다. 다만 미묘한 차이가 하나 있다 — 앞 값이 널일 때 `?.`은 `null`이 아니라 **`undefined`로 단락**된다. 따라서 반환 타입을 엄밀히 `T | null`로 유지하려면 `?? null`을 덧붙여야 한다. TypeScript는 `null`과 `undefined`를 구분하므로, 팀 컨벤션으로 둘 중 하나만 "값 없음"의 표현으로 정하면 이런 혼동을 줄일 수 있다.

이처럼 널 안전성을 활용하면 코드의 오류 발생을 줄이면서도, 언어의 다른 기능을 이용해 가독성은 높이고 훨씬 더 간결한 코드를 작성할 수 있다.

---

## 3. 옵셔널 사용 (B.2)

사용 중인 언어가 널 안전성을 제공하지 않거나 어떤 이유로든 쓸 수 없는 경우, 함수가 널을 반환하면 **호출하는 쪽에서 이를 예상하지 못할 수 있다.** 이를 방지하기 위해 `Optional` 같은 타입을 쓰면, 반환값이 없을 수도 있음을 호출하는 쪽에서 **강제로 인지**하게 만들 수 있다. 앞 절의 `getFifthElement()`를 옵셔널로 바꾸면 다음과 같다.

<details>
<summary>의사코드 (원서) — 옵셔널로 반환</summary>

```java
Optional<Element> getFifthElement(List<Element> elements) {
  if (elements.size() < 5) {
    return Optional.empty(); // 값이 없음
  }
  return Optional.of(elements[4]); // 값이 있음
}
```

</details>

```typescript
// TypeScript에서는 별도의 Optional 래퍼가 필요 없다.
// 'Element | null'이 곧 옵셔널 역할을 하며, 컴파일러가 널 처리를 강제한다.
function getFifthElement(elements: Element[]): Element | null {
  if (elements.length < 5) {
    return null;
  }
  return elements[4];
}
```

이 코드를 사용하는 개발자는 옵셔널의 값을 쓰기 전에 **먼저 값이 있는지 확인(`isPresent()`)하고, 값은 `get()`으로 꺼내야** 한다. 즉 옵셔널 타입 자체가 "값이 없을 수도 있으니 확인하라"고 호출자에게 요구하는 셈이다.

<details>
<summary>의사코드 (원서) — 옵셔널 사용</summary>

```java
void displayFifthElement(List<Element> elements) {
  Optional<Element> fifthElement = getFifthElement(elements);
  if (fifthElement.isPresent()) {   // 값이 있는지 먼저 확인
    displayElement(fifthElement.get());   // 값은 get()으로 꺼낸다
  } else {
    displayMessage("Fifth element doesn't exist");
  }
}
```

</details>

```typescript
function displayFifthElement(elements: Element[]): void {
  const fifthElement: Element | null = getFifthElement(elements);
  // Optional의 isPresent()/get() 대신, 컴파일러가 강제하는 널 확인으로 같은 안전성을 얻는다
  if (fifthElement !== null) {
    displayElement(fifthElement); // 타입이 'Element'로 좁혀졌다
  } else {
    displayMessage("Fifth element doesn't exist");
  }
}
```

옵셔널을 쓰는 것이 다소 번거로운 것은 사실이다. 하지만 `Optional` 타입은 대개 다양한 멤버 함수를 제공해, 어떤 상황에서는 훨씬 더 간결한 코드를 쓸 수 있게 해 준다. 예를 들어 자바 9부터 제공되는 `ifPresentOrElse()`를 쓰면 값이 있을 때와 없을 때의 처리를 한 번에 넘길 수 있다.

<details>
<summary>의사코드 (원서) — ifPresentOrElse()</summary>

```java
void displayFifthElement(List<Element> elements) {
  getFifthElement(elements).ifPresentOrElse(
      displayElement,   // Optional에 값이 있으면 그 값을 인수로 displayElement()가 호출된다
      () -> displayMessage("Fifth element doesn't exist"));   // 값이 없으면 displayMessage()가 호출된다
}
```

</details>

```typescript
// TypeScript에는 Optional.ifPresentOrElse()가 없지만, 같은 의도를 작은 헬퍼로 표현할 수 있다.
// 대개는 위의 if/else 나 옵셔널 체이닝만으로 충분하다.
function ifPresentOrElse<T>(
  value: T | null,
  onPresent: (value: T) => void,
  onEmpty: () => void,
): void {
  if (value !== null) {
    onPresent(value);
  } else {
    onEmpty();
  }
}

function displayFifthElement(elements: Element[]): void {
  ifPresentOrElse(
    getFifthElement(elements),
    (element) => {
      displayElement(element);
    },
    () => {
      displayMessage("Fifth element doesn't exist");
    },
  );
}
```

옵셔널 타입을 쓰는 것은 경우에 따라 다소 장황하고 번거로울 수 있다. 그러나 널 처리를 제대로 하지 않으면 그 문제가 코드 곳곳으로 빠르게 확산될 수 있다. 따라서 코드가 늘어나고 번거로워지는 비용을 치르더라도, **코드 견고성 향상과 버그 감소로 얻는 이익이 더 크기 때문에 옵셔널을 사용하는 것이 바람직하다.** (그리고 TypeScript처럼 언어가 널 안전성을 기본 제공한다면, 이 비용의 대부분은 언어가 대신 치러 준다.)

---

## 4. C++의 옵셔널

이 책을 쓰는 현재, C++ 표준 라이브러리의 `optional`은 **참조를 지원하지 않기 때문에** 클래스 같은 객체를 반환하는 데 사용하기 어려울 수 있다. 주목할 만한 대안으로는 참조를 지원하는 **부스트(Boost) 라이브러리**의 옵셔널을 사용하는 것이 있다.

각 접근 방식은 장단점이 있으므로, C++ 코드에서 옵셔널 사용을 고려하고 있다면 이 주제는 읽어 볼 만한 가치가 있다.

- **표준 라이브러리의 Optional**: http://mng.bz/n2pe
- **부스트 라이브러리의 Optional**: http://mng.bz/vem1

---

## 요약

- **널 안전성**을 지원하는 언어는 타입에 `?`를 붙여 널 가능성을 표시하고, 널 확인 없이 값을 쓰면 **컴파일 자체를 막는다.** 컴파일러가 널이 아닌 경로를 유추(타입 좁히기)하므로 널 포인터 예외 위험 없이 널을 다룰 수 있다.
- **널 조건부 연산자(`?.`)** 등의 구문으로 장황한 널 확인을 간결하게 줄일 수 있다.
- 언어가 널 안전성을 제공하지 않으면 **옵셔널 타입**을 써서, 값이 없을 수 있음을 호출자가 강제로 인지하게 만든다. 다소 번거롭지만 견고성·버그 감소의 이익이 더 크다.
- **C#**은 널 안전성 위반을 기본적으로 경고로만 처리하므로, 오류로 승격하도록 설정하는 것이 좋다. **C++**의 표준 `optional`은 참조를 지원하지 않아 부스트 라이브러리가 대안이 된다.
- **TypeScript**는 `strictNullChecks` 아래에서 유니언 타입 `T | null`(또는 `T | undefined`)로 널 안전성을 **기본 제공**한다. 별도의 옵셔널 래퍼 없이도 `Element | null` 반환 타입만으로 컴파일러가 널 처리를 강제하며, 제어 흐름 기반 타입 좁히기로 확인 이후 지점에서 값을 안전하게 쓸 수 있다. 옵셔널 체이닝 `?.`은 널 조건부 연산자에 대응하되 널일 때 `undefined`로 단락된다는 점만 유의하면 된다.
