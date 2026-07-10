# Chapter 9: Make Code Reusable and Generalizable (코드를 재사용하고 일반화할 수 있도록 하라)

## 핵심 질문

코드에 숨은 가정은 왜 재사용 시 버그가 되는가? 가정이 꼭 필요하면 어떻게 안전하게 강제하는가? 전역 상태는 왜 코드 재사용을 위험하게 만드는가? 기본 반환값은 왜 낮은 계층에서 반환하면 안 되는가? 함수가 필요 이상으로 많은 매개변수를 받으면 무엇이 문제인가? 제네릭은 어떻게 코드를 일반화하는가?

---

## 0. 이 장에서 다루는 것 · 코드 표기 규약

- 안전하게 **재사용(reusable)**할 수 있는 코드 작성법 — 같은 하위 문제를 여러 상황에서 다시 쓰기
- 다양한 문제를 해결하도록 **일반화(generalizable)**된 코드 작성법

같은 하위 문제는 프로젝트마다 반복해서 나타나므로, 재사용 가능하게 코드를 짜 두면 미래의 나와 팀의 시간·노력을 아낀다. 하지만 기존 해결책이 **내 사례에 맞지 않는 가정**을 하거나 **필요 없는 기능과 엮여** 있으면 재사용할 수 없다. 이 장은 2장(간결한 추상화 계층)·8장(모듈화)을 토대로, 재사용·일반화를 해치는 추가 요인들을 다룬다. 6대 요소 중 **재사용·일반화**를 정면으로 다룬다.

> **코드 표기 규약**: 원서 의사코드를 `<details>`로 접어 두고 아래에 **TypeScript 변환본**을 병기한다. 널 규약(`Type?` → `Type | null`), `final` → `readonly`.

---

## 1. 가정을 주의하라 (9.1)

가정은 코드를 단순하거나 효율적으로 만들지만, 그만큼 **취약하게** 만든다. `Article.getAllImages()`가 "이미지를 가진 섹션은 최대 하나"라고 가정하고 첫 이미지 섹션에서 루프를 끝내면, for 루프가 몇 번 덜 도는 미미한 이득을 얻는 대신, 이미지 섹션이 여럿인 기사에서 **일부 이미지를 조용히 누락**한다. `getAllImages`라는 이름을 본 사람은 누구나 '모든' 이미지를 기대하므로, 이 가정은 주석 속에 묻혀 호출자에게 보이지 않는 함정이 된다.

<details>
<summary>의사코드 (원서) — 예제 9.1 → 9.2 (가정 있음 → 가정 제거)</summary>

```java
// ❌ 나쁜 예: "이미지 섹션은 하나뿐"이라는 숨은 가정
List<Image> getAllImages() {
  for (Section section : sections) {
    if (section.containsImages()) {
      // 기사 내에 이미지를 포함하는 섹션은 최대 하나만 있다 (숨은 가정)
      return section.getImages();   // 첫 섹션만 반환 → 나머지 누락
    }
  }
  return [];
}

// ✅ 좋은 예: 가정을 제거 — 모든 섹션의 이미지를 모은다
List<Image> getAllImages() {
  List<Image> images = [];
  for (Section section : sections) {
    images.addAll(section.getImages());
  }
  return images;
}
```

</details>

```typescript
// ❌ 나쁜 예: "이미지 섹션은 하나뿐"이라는 숨은 가정
class Article {
  private readonly sections: Section[] = [];
  getAllImages(): Image[] {
    for (const section of this.sections) {
      if (section.containsImages()) {
        // 숨은 가정: 이미지 섹션은 최대 하나 → 나머지 조용히 누락
        return section.getImages();
      }
    }
    return [];
  }
}

// ✅ 좋은 예: 가정을 제거 — 모든 섹션의 이미지를 모은다
class Article {
  private readonly sections: Section[] = [];
  getAllImages(): Image[] {
    const images: Image[] = [];
    for (const section of this.sections) {
      images.push(...section.getImages());
    }
    return images;
  }
}
```

미미한 성능 이득을 위해 견고함을 희생하는 것은 **섣부른 최적화(*premature optimization*)**다. 수백만 번 실행되어 최적화 효과가 명백할 때만 최적화하고, 그렇지 않으면 가독성·견고함을 우선하라.

**가정이 정말 필요하면 강제하라.** 예를 들어 기사를 렌더링하는 템플릿이 이미지 섹션을 하나만 처리할 수 있어 그 가정이 불가피하다면, (1) 이름으로 가정을 드러내고(`getOnlyImageSection()`), (2) 어서션/오류 전달로 가정이 깨지면 **빠르게 실패**하게 한다.

<details>
<summary>의사코드 (원서) — 예제 9.5 가정의 강제적 확인 (좋은 예)</summary>

```java
class Article {
  private List<Section> sections;

  // 함수 이름이 호출자가 할 가정("이미지 섹션은 하나")을 드러낸다
  Section? getOnlyImageSection() {
    List<Section> imageSections =
        sections.filter(section -> section.containsImages());
    assert(imageSections.size() <= 1, "기사가 여러 개의 이미지 섹션을 갖는다"); // 강제 확인
    return imageSections.first();
  }
}
```

</details>

```typescript
class Article {
  private readonly sections: Section[] = [];

  // 이름이 가정을 드러낸다: 이미지 섹션은 하나뿐
  getOnlyImageSection(): Section | null {
    const imageSections = this.sections.filter((section) =>
      section.containsImages(),
    );
    // 가정이 깨지면 빠르게 실패 (내부 생성 데이터 → 어서션이 적합)
    assert(imageSections.length <= 1, "기사가 여러 개의 이미지 섹션을 갖는다");
    return imageSections[0] ?? null;
  }
}
```

> **핵심 통찰**: 가정의 **비용(취약성 증가) vs 이득(단순화·효율)**을 저울질하라. 이득이 미미하면 가정하지 않는 것이 최선이다. 데이터가 프로그램 내부에서 생성되면 가정이 깨진 것은 프로그래밍 오류이므로 **어서션**이 적합하고, 외부·사용자가 제공하면 **명시적 오류 전달**(4장)이 더 매끄럽다.

---

## 2. 전역 상태를 주의하라 (9.2)

**전역 상태(*global state*)**(정적 변수 등)는 프로그램의 모든 컨텍스트가 공유한다. 전역 상태를 쓰는 것은 "이 코드를 아무도 다른 목적으로 재사용하지 않을 것"이라는 **매우 취약한 암묵적 가정**을 전제한다. 온라인 쇼핑의 `ShoppingBasket`을 정적 변수·정적 함수로 만들면 어디서든 쉽게 접근되지만, "실행 인스턴스당 장바구니는 하나"라고 가정한 셈이다. 이 가정은 (1) 장바구니를 서버에 저장해 여러 사용자를 처리할 때, (2) "나중을 위해 저장" 기능을 추가할 때, (3) 신선식품용 별도 장바구니가 필요할 때 등으로 쉽게 깨진다. 깨지면 서로 다른 코드가 같은 전역 상태를 읽고 써서 **간섭**하며, 최악의 경우 사생활 침해 같은 심각한 버그가 된다.

<details>
<summary>의사코드 (원서) — 예제 9.7 → 9.9·9.10 (전역 상태 → DI)</summary>

```java
// ❌ 나쁜 예: 전역 상태 — static 변수·함수
class ShoppingBasket {
  private static List<Item> items = [];       // 전역 변수
  static void addItem(Item item) { items.add(item); }
  static List<Item> getItems() { return List.copyOf(items); }
}
// 어디서든 ShoppingBasket.addItem(...) 호출 → 모든 코드가 같은 상태를 공유

// ✅ 좋은 예: 인스턴스 상태 + 의존성 주입
class ShoppingBasket {
  private final List<Item> items = [];         // 인스턴스 변수
  void addItem(Item item) { items.add(item); }
  List<Item> getItems() { return List.copyOf(items); }
}
class ViewItemWidget {
  private final ShoppingBasket basket;
  ViewItemWidget(Item item, ShoppingBasket basket) { ... }  // 주입
  void addItemToBasket() { basket.addItem(item); }
}
```

</details>

```typescript
// ✅ 좋은 예: 상태를 인스턴스에 캡슐화하고 의존성 주입으로 공유
class ShoppingBasket {
  private readonly items: Item[] = []; // 정적 아님 — 인스턴스마다 별도 상태
  addItem(item: Item): void {
    this.items.push(item);
  }
  getItems(): readonly Item[] {
    return [...this.items];
  }
}

class ViewItemWidget {
  // 어떤 장바구니를 쓸지 주입으로 제어 — 일반 장바구니와 신선식품 장바구니 분리 가능
  constructor(
    private readonly item: Item,
    private readonly basket: ShoppingBasket,
  ) {}
  addItemToBasket(): void {
    this.basket.addItem(this.item);
  }
}

// 서로 완전히 독립적인 장바구니 — 절대 간섭하지 않음
const normalBasket = new ShoppingBasket();
const freshBasket = new ShoppingBasket();
```

> **핵심 통찰**: 전역성(global)과 가시성(public/private)을 혼동하지 말라 — 전역 여부는 "프로그램 전체가 하나를 공유하는가"의 문제다. 여러 부분이 상태를 공유해야 한다면 전역 변수 대신 **의존성 주입**으로 인스턴스를 넘겨, 무엇을 공유하고 무엇을 분리할지 **통제된 방식**으로 결정하라.

---

## 3. 기본 반환값을 적절하게 사용하라 (9.3)

합리적인 기본값은 소프트웨어를 쓰기 편하게 만들지만, **어느 계층에서 기본값을 정하느냐**가 중요하다. `UserDocumentSettings.getPreferredFont()`가 폰트 미지정 시 `Font.ARIAL`을 반환하면, (1) 사용자가 Arial을 **선택한 것**인지 **미설정 기본값**인지 구분 불가능하고, (2) "회사가 전사 기본 폰트를 지정" 같은 요구가 오면 대응할 수 없다. 낮은 계층은 여러 상위 계층에서 재사용되므로, 낮은 계층에서 기본값을 박으면 **그 위 모든 계층에 가정을 강요**하는 셈이다(사용자 설정 조회와 기본값 정의라는 별개의 하위 문제를 뒤섞음).

**해결책 — 기본값 결정은 상위 계층으로**: 낮은 계층은 미설정 시 `null`을 반환하고, 상위 계층에서 기본값을 처리한다.

<details>
<summary>의사코드 (원서) — 예제 9.13 · 9.15 (null 반환 + 상위에서 기본값)</summary>

```java
// 낮은 계층: 미설정이면 null 반환 (기본값을 강요하지 않음)
class UserDocumentSettings {
  private final Font? font;
  Font? getPreferredFont() { return font; }
}

// 기본값 정의는 별도 하위 문제로 분리
class DefaultDocumentSettings {
  Font getDefaultFont() { return Font.ARIAL; }
}

// 상위 계층: 사용자값과 기본값 사이 선택 (DI로 구성)
class DocumentSettings {
  private final UserDocumentSettings userSettings;
  private final DefaultDocumentSettings defaultSettings;
  Font getFont() {
    Font? userFont = userSettings.getPreferredFont();
    if (userFont != null) { return userFont; }
    return defaultSettings.getFont();
  }
}
```

</details>

```typescript
// 낮은 계층: 미설정이면 null (기본값을 강요하지 않는다)
class UserDocumentSettings {
  private readonly font: Font | null = null;
  getPreferredFont(): Font | null {
    return this.font;
  }
}

// 기본값 정의는 별개의 하위 문제로 분리
class DefaultDocumentSettings {
  getDefaultFont(): Font {
    return Font.ARIAL;
  }
}

// 상위 계층에서 사용자값 vs 기본값을 선택 (DI로 구성 → 재설정 가능)
class DocumentSettings {
  constructor(
    private readonly userSettings: UserDocumentSettings,
    private readonly defaultSettings: DefaultDocumentSettings,
  ) {}
  getFont(): Font {
    // 널 병합 연산자(??): 왼쪽이 null이면 오른쪽 사용
    return this.userSettings.getPreferredFont() ?? this.defaultSettings.getDefaultFont();
  }
}
```

> **핵심 통찰**: `??`(널 병합 연산자)로 "사용자값이 있으면 그것, 없으면 기본값"을 간결하게 표현한다. 널 병합이 없는 언어라면 `Map.getOrDefault(key, default)`처럼 **기본값 매개변수**를 받는 방식도 있다. 핵심은 **기본값 가정을 그 가정이 유효한 상위 계층에서** 하는 것이다.

---

## 4. 함수의 매개변수를 주목하라 (9.4)

함수가 데이터 객체 내 **모든** 정보를 쓴다면 그 객체를 통째로 받는 것이 타당하다(8.5). 하지만 **한두 값만** 필요한데 객체 전체를 받으면 재사용성을 해친다. `TextBox.setTextColor(TextOptions options)`가 `TextOptions`에서 색상만 쓰는데도 전체를 받으면, "경고 스타일(빨간색만)"을 적용하려는 호출자가 **무의미한 값들로 채운 `TextOptions`를 억지로 만들어야** 한다.

<details>
<summary>의사코드 (원서) — 예제 9.18 → 9.19·이후 (전체 객체 → 필요한 것만)</summary>

```java
// ❌ 나쁜 예: 색상만 쓰는데 TextOptions 전체를 받는다
void setTextColor(TextOptions options) {
  textContainer.setStyleProperty("color", options.getTextColor().asHexRgb());
}
// 호출자가 관련 없는 값을 억지로 만들어야 함
void styleAsWarning(TextBox textBox) {
  TextOptions style = new TextOptions(Font.ARIAL, 12.0, 14.0, Color.RED); // 앞 3개는 무의미
  textBox.setTextColor(style);
}

// ✅ 좋은 예: 필요한 Color만 받는다
void setTextColor(Color color) {
  textElement.setStyleProperty("color", color.asHexRgb());
}
void styleAsWarning(TextBox textBox) {
  textBox.setTextColor(Color.RED);   // 훨씬 간단
}
```

</details>

```typescript
// ❌ 나쁜 예: 색상만 쓰는데 TextOptions 전체를 받는다
class TextBox {
  setTextColor(options: TextOptions): void {
    this.textContainer.setStyleProperty("color", options.getTextColor().asHexRgb());
  }
}
// 호출자가 관련 없는 값을 억지로 지어내야 한다
function styleAsWarning(textBox: TextBox): void {
  const style = new TextOptions(Font.ARIAL, 12.0, 14.0, Color.RED); // 앞 3개는 무의미
  textBox.setTextColor(style);
}

// ✅ 좋은 예: 함수는 필요한 것(Color)만 받는다
class TextBox {
  setTextColor(color: Color): void {
    this.textElement.setStyleProperty("color", color.asHexRgb());
  }
}
function styleAsWarning(textBox: TextBox): void {
  textBox.setTextColor(Color.RED); // 훨씬 간단하고 오해 없음
}
```

> **핵심 통찰**: 함수는 **필요한 것만** 매개변수로 받으면 재사용성이 높아지고 이해하기 쉬워진다. 단, 10개 항목 중 8개가 필요하다면 객체 전체를 넘기는 편이 낫다 — 8개를 낱개로 넘기면 오히려 모듈성을 해친다(8.5). 정답은 상황마다 다르며, 트레이드오프를 인지하는 것이 중요하다.

---

## 5. 제네릭의 사용을 고려하라 (9.5)

특정 유형에 하드코딩하면 일반화가 제한된다. "단어 맞히기 게임"의 무작위 큐 `RandomizedQueue`가 `List<String>`을 하드코딩하면, 문자열 단어는 저장하지만 "사진 맞히기 게임"에는 재사용할 수 없다 — 하위 문제(무작위 큐)는 사실상 동일한데도.

**해결책 — 제네릭(*generic*)**: 참조하는 유형을 자리표시자 `<T>`로 두면, 사용 시점에 유형을 지정할 수 있어 어떤 유형이든 저장하는 하나의 클래스가 된다.

<details>
<summary>의사코드 (원서) — 예제 9.20 → 9.21 (String 하드코딩 → 제네릭)</summary>

```java
// ❌ 나쁜 예: String에 하드코딩 — 다른 유형에 재사용 불가
class RandomizedQueue {
  private final List<String> values = [];
  void add(String value) { values.add(value); }
  String? getNext() { ... }
}

// ✅ 좋은 예: 제네릭 — T는 유형 자리표시자
class RandomizedQueue<T> {
  private final List<T> values = [];
  void add(T value) { values.add(value); }
  T? getNext() {
    if (values.isEmpty()) { return null; }
    Int randomIndex = Math.randomInt(0, values.size());
    values.swap(randomIndex, values.size() - 1);
    return values.removeLast();
  }
}
```

</details>

```typescript
// ✅ 좋은 예: 제네릭 <T> — 어떤 유형이든 저장 가능
class RandomizedQueue<T> {
  private readonly values: T[] = [];

  add(value: T): void {
    this.values.push(value);
  }

  /** 큐에서 무작위 항목을 제거하고 반환한다(비어 있으면 null). */
  getNext(): T | null {
    if (this.values.length === 0) {
      return null;
    }
    const randomIndex = Math.floor(Math.random() * this.values.length);
    const last = this.values.length - 1;
    [this.values[randomIndex], this.values[last]] = [this.values[last], this.values[randomIndex]];
    return this.values.pop() ?? null;
  }
}

// 사용처마다 유형을 지정 — 하나의 클래스로 재사용
const words = new RandomizedQueue<string>();
const pictures = new RandomizedQueue<Picture>();
```

> **핵심 통찰**: 다른 클래스를 참조하되 **그 클래스가 무엇인지 신경 쓰지 않는다면** 제네릭을 고려하라. 아주 적은 추가 작업으로 일반화와 재사용성을 크게 높인다. (TS의 `getNext()`가 `null`로 "비어 있음"을 나타내므로, `null`을 저장할 수 있는 큐라면 `hasNext()`를 따로 두어 "비어 있음"과 "null 값"을 구분해야 한다.)

---

## 6. 코드 품질 6대 요소 연결

이 장의 기법은 모두 **재사용성·일반화성**을 끌어올린다. 그 바탕에는 "가정을 줄이고, 하위 문제를 올바른 계층으로 분리한다"는 공통 원리가 있다.

| 기법 | 재사용·일반화에 기여하는 방식 |
|---|---|
| 불필요한 가정 제거 (9.1) | 다른 사용 사례에서도 버그 없이 재사용 |
| 전역 상태 회피 (9.2) | 여러 컨텍스트에서 간섭 없이 재사용 |
| 기본값을 상위 계층에서 (9.3) | 낮은 계층이 여러 상위 계층에 재사용 가능 |
| 필요한 매개변수만 (9.4) | 함수를 조금 다른 상황에 재사용 가능 |
| 제네릭 (9.5) | 유형에 무관하게 같은 로직을 일반화 |

> **핵심 통찰**: 재사용·일반화의 토대는 8장의 **모듈화**와 2장의 **간결한 추상화 계층**이다. 하위 문제가 느슨하게 결합될수록, 그 해결책을 다른 상위 문제에 가져다 쓰기 쉽고 안전해진다. 이 장의 기법들은 그 위에 "가정을 줄이고 결합을 더 끊는" 한 겹을 더한다.

---

## 요약

- 같은 하위 문제는 자주 반복되므로, **근본적인 하위 문제를 식별해 재사용 가능하게** 코드를 구성하면 미래의 시간·노력을 아낀다.
- **가정을 주의하라**: 가정은 취약성 비용을 수반한다. 이득이 미미하면 하지 말고, 꼭 필요하면 이름·어서션·오류 전달로 **강제**하라.
- **전역 상태를 주의하라**: 전역 상태는 재사용을 안전하지 않게 만든다. 공유가 필요하면 **의존성 주입**으로.
- **기본 반환값**: 낮은 계층에서 기본값을 반환하지 말고 `null`을 반환한 뒤 **상위 계층에서** 기본값을 정하라(`??`).
- **함수 매개변수**: 함수는 **필요한 것만** 받는다(단, 대부분을 쓴다면 객체 전체가 낫다).
- **제네릭**: 참조 유형에 무관한 로직은 제네릭 `<T>`로 일반화한다.
