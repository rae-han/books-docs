# Chapter 8: Make Code Modular (코드를 모듈화하라)

## 핵심 질문

요구사항이 어떻게 바뀔지 모르는 상태에서 어떻게 변경이 쉬운 코드를 작성하는가? 의존성 주입은 왜 코드를 모듈화하는가? 구체적인 클래스가 아니라 인터페이스에 의존하면 무엇이 좋아지는가? 클래스 상속은 왜 위험하며 구성(composition)은 어떻게 그 함정을 피하는가? 반환 유형과 예외로 구현 세부사항이 유출되면 어떤 문제가 생기는가?

---

## 0. 이 장에서 다루는 것 · 코드 표기 규약

- 모듈화된 코드의 이점
- 이상적인 모듈화가 되지 않는 흔한 방식
- 코드를 더 모듈화하기 위한 구체적 기법

모듈화의 핵심 목표는 **요구사항이 어떻게 변경될지 정확히 모르는 상태에서도 변경·재구성이 쉬운 코드**를 작성하는 것이다. 이를 위한 핵심은 각 기능(요구사항)이 코드베이스의 서로 다른 부분에서 구현되어, 하나가 바뀌면 그와 직접 관련된 부분만 수정하면 되도록 하는 것이다. 이 장은 2장의 **간결한 추상화 계층**을 토대로 하며, 하위 문제의 해결책들이 서로 밀접하게 얽히지 않고 독립적이도록 만드는 데 초점을 둔다. 6대 요소 중 **모듈화**를 정면으로 다룬다.

> **코드 표기 규약**: 원서 의사코드를 `<details>`로 접어 두고 아래에 **TypeScript 변환본**을 병기한다. 널 규약(`Type?` → `Type | null`), `final` → `readonly`.

---

## 1. 의존성 주입의 사용을 고려하라 (8.1)

클래스는 보통 다른 클래스에 의존한다. 그런데 하위 문제의 해결책이 **항상 하나뿐인 것은 아니므로**, 의존 대상을 나중에 교체할 수 있게 열어 두는 것이 유용하다. `RoutePlanner`(자동차 여행 플래너)가 생성자에서 직접 `NorthAmericaRoadMap`을 생성하면, 이 클래스는 **북미 여행에만** 쓸 수 있고 다른 지역엔 무용지물이 된다.

<details>
<summary>의사코드 (원서) — 예제 8.1 · 8.3 하드코드된 의존성 (나쁜 예)</summary>

```java
class RoutePlanner {
  private final RoadMap roadMap;

  RoutePlanner() {
    // 특정 구현을 생성자 안에서 직접 생성 — 북미 전용으로 고정됨
    this.roadMap = new NorthAmericaRoadMap(true, false); // 온라인 사용, 계절도로 제외 (임의 결정)
  }
  Route planRoute(LatLong startPoint, LatLong endPoint) { ... }
}

interface RoadMap {
  List<Road> getRoads();
  List<Junction> getJunctions();
}
```

</details>

```typescript
// ❌ 나쁜 예: 특정 구현을 하드코드 — 북미·온라인·계절도로 제외로 고정
class RoutePlanner {
  private readonly roadMap: RoadMap;

  constructor() {
    this.roadMap = new NorthAmericaRoadMap(true, false);
  }
  planRoute(startPoint: LatLong, endPoint: LatLong): Route { /* ... */ }
}
```

**해결책 — 의존성 주입(*dependency injection*)**: 의존 대상을 생성자 매개변수로 **주입**받는다. 이제 어떤 로드맵으로도 설정할 수 있어 모듈화되고 적응성이 높아진다.

<details>
<summary>의사코드 (원서) — 예제 8.4 · 8.5 의존성 주입 + 팩토리 함수 (좋은 예)</summary>

```java
class RoutePlanner {
  private final RoadMap roadMap;
  RoutePlanner(RoadMap roadMap) {   // RoadMap이 생성자를 통해 주입된다
    this.roadMap = roadMap;
  }
  Route planRoute(LatLong startPoint, LatLong endPoint) { ... }
}

// 생성이 복잡해지는 단점은 팩토리 함수로 보완한다
class RoutePlannerFactory {
  static RoutePlanner createEuropeRoutePlanner() {
    return new RoutePlanner(new EuropeRoadMap());
  }
  static RoutePlanner createDefaultNorthAmericaRoutePlanner() {
    return new RoutePlanner(new NorthAmericaRoadMap(true, false)); // '합리적인' 기본값
  }
}
```

</details>

```typescript
// ✅ 좋은 예: 의존성을 주입 — 어떤 RoadMap으로도 설정 가능
class RoutePlanner {
  constructor(private readonly roadMap: RoadMap) {}
  planRoute(startPoint: LatLong, endPoint: LatLong): Route { /* ... */ }
}

// 생성이 복잡해지는 단점은 팩토리 함수(또는 DI 프레임워크)로 보완
class RoutePlannerFactory {
  static createEuropeRoutePlanner(): RoutePlanner {
    return new RoutePlanner(new EuropeRoadMap());
  }
  static createDefaultNorthAmericaRoutePlanner(): RoutePlanner {
    return new RoutePlanner(new NorthAmericaRoadMap(true, false)); // '합리적인' 기본값
  }
}
```

> **핵심 통찰**: DI를 나중에 쓰고 싶어도 **정적 함수(static function)에 직접 의존하도록** 코드를 짜 두면 주입이 불가능해진다. 정적 함수·변수에 과도하게 의존하는 것을 **정적 매달림(*static cling*)**이라 하며, 특히 단위 테스트에서 테스트 더블로 대체할 수 없어 문제가 된다(10장). 하위 문제의 해결책이 하나뿐인 아주 근본적인 경우가 아니라면, 처음부터 인스턴스화 가능한 클래스(+인터페이스)로 설계해 DI 여지를 남겨 두라.

---

## 2. 인터페이스에 의존하라 (8.2)

DI를 쓰더라도 **구체적인 구현 클래스**에 의존하면 이점의 절반을 잃는다. `RoutePlanner`가 `RoadMap` 인터페이스가 아니라 `NorthAmericaRoadMap` 클래스를 생성자 타입으로 받으면, 여전히 다른 로드맵 구현으로는 쓸 수 없다.

<details>
<summary>의사코드 (원서) — 예제 8.8 → 8.9 구체 클래스 의존(나쁨) → 인터페이스 의존(좋음)</summary>

```java
// ❌ 나쁜 예: 구체 클래스에 의존
class RoutePlanner {
  private final NorthAmericaRoadMap roadMap;   // 북미 구현에 고정
  RoutePlanner(NorthAmericaRoadMap roadMap) { this.roadMap = roadMap; }
}

// ✅ 좋은 예: 인터페이스에 의존
class RoutePlanner {
  private final RoadMap roadMap;               // 어떤 구현이든 주입 가능
  RoutePlanner(RoadMap roadMap) { this.roadMap = roadMap; }
}
```

</details>

```typescript
// ❌ 나쁜 예: 구체 클래스에 의존 — 북미 구현에 고정
class RoutePlanner {
  constructor(private readonly roadMap: NorthAmericaRoadMap) {}
}

// ✅ 좋은 예: 인터페이스에 의존 — 어떤 구현이든 주입 가능
class RoutePlanner {
  constructor(private readonly roadMap: RoadMap) {}
}
```

> **핵심 통찰**: 어떤 클래스가 인터페이스를 구현하고 필요한 기능이 그 인터페이스에 모두 정의되어 있다면, 클래스가 아니라 **인터페이스에 의존**하는 것이 낫다. 추가 노력이 거의 없으면서 코드가 훨씬 모듈화된다. "구체적인 구현보다 추상화에 의존하라"는 것이 **의존성 역전 원리(*Dependency Inversion Principle* — SOLID의 D)**의 핵심이다.

---

## 3. 클래스 상속을 주의하라 (8.3)

두 클래스가 진정한 **is-a 관계**(예: 포드 머스탱 *is a* 자동차)면 상속이 적절할 수 있다. 하지만 상속은 함정이 많아, 상속을 쓸 수 있는 많은 상황에서 **구성(*composition*)**이 더 낫다. "쉼표로 구분된 정수 파일을 읽는" 문제를 예로 보자. `CsvFileHandler`(파일을 열고 문자열을 읽음)를 재사용해 `IntFileReader`를 만들 때, 상속을 쓰면 두 가지 문제가 생긴다.

<details>
<summary>의사코드 (원서) — 예제 8.11 · 8.12 상속 (나쁜 예)</summary>

```java
class IntFileReader extends CsvFileHandler {   // CsvFileHandler를 상속(확장)
  IntFileReader(File file) { super(file); }
  Int? getNextInt() {
    String? nextValue = getNextValue();        // 슈퍼클래스의 함수 호출
    if (nextValue == null) { return null; }
    return Int.parse(nextValue, Radix.BASE_10);
  }
}

// 실질적 퍼블릭 API — 원치 않는 함수까지 노출된다
class IntFileReader /* extends CsvFileHandler */ {
  Int? getNextInt() { ... }
  String? getNextValue() { ... }              // ← 유출된 구현 세부사항
  void writeValue(String value) { ... }       // ← 정수 리더인데 쓰기까지 노출!
  void close() { ... }
}
```

</details>

```typescript
// ❌ 나쁜 예: 상속 — 슈퍼클래스의 모든 기능이 원치 않게 노출된다
class IntFileReader extends CsvFileHandler {
  constructor(file: File) {
    super(file);
  }
  getNextInt(): number | null {
    const nextValue: string | null = this.getNextValue(); // 슈퍼클래스 함수
    if (nextValue === null) {
      return null;
    }
    return parseInt(nextValue, 10);
  }
  // 상속으로 getNextValue()·writeValue()·close()까지 전부 퍼블릭 API에 노출됨
}
```

- **문제 1 — 추상화 계층 오염**: 상속하면 슈퍼클래스의 **모든 기능**이 노출된다. 정수를 읽는 클래스가 `getNextValue()`(문자열 읽기)·`writeValue()`(쓰기)까지 제공하는 이상한 API가 되고, 훗날 이 함수들이 코드베이스 곳곳에서 호출되면 변경이 어려워진다.
- **문제 2 — 적응성 저하**: "세미콜론 구분 파일도 읽어야 한다"는 요구가 생기면, `SemicolonFileHandler`가 이미 있어도 `IntFileReader`가 `CsvFileHandler`를 상속하고 있어 갈아끼울 수 없다. 결국 `SemicolonIntFileReader`를 통째로 복제해야 하는데, 이 **코드 중복**은 유지보수 비용과 버그를 키운다.

**해결책 — 구성(composition)**: 클래스를 확장하는 대신, 필요한 인터페이스의 인스턴스를 **멤버로 갖고**(주입받고), 노출할 함수만 직접 골라 **전달(forwarding)**한다.

<details>
<summary>의사코드 (원서) — 예제 8.15 · 8.17 구성 + 팩토리 (좋은 예)</summary>

```java
class IntFileReader {
  private final FileValueReader valueReader;   // 인터페이스 인스턴스를 '가진다'(구성)
  IntFileReader(FileValueReader valueReader) { // DI로 주입
    this.valueReader = valueReader;
  }
  Int? getNextInt() {
    String? nextValue = valueReader.getNextValue();
    if (nextValue == null) { return null; }
    return Int.parse(nextValue, Radix.BASE_10);
  }
  void close() { valueReader.close(); }        // 필요한 함수만 명시적으로 전달(forwarding)
}

class IntFileReaderFactory {
  IntFileReader createCsvIntReader(File file) {
    return new IntFileReader(new CsvFileHandler(file));
  }
  IntFileReader createSemicolonIntReader(File file) {
    return new IntFileReader(new SemicolonFileHandler(file));
  }
}
```

</details>

```typescript
// ✅ 좋은 예: 구성 — FileValueReader 인터페이스 인스턴스를 멤버로 갖는다
class IntFileReader {
  constructor(private readonly valueReader: FileValueReader) {} // DI로 주입

  getNextInt(): number | null {
    const nextValue: string | null = this.valueReader.getNextValue();
    if (nextValue === null) {
      return null;
    }
    return parseInt(nextValue, 10);
  }
  close(): void {
    this.valueReader.close(); // 노출할 함수만 명시적으로 전달(forwarding)
  }
  // 퍼블릭 API는 getNextInt()·close()뿐 — 문자열 읽기/쓰기는 숨겨짐
}

class IntFileReaderFactory {
  createCsvIntReader(file: File): IntFileReader {
    return new IntFileReader(new CsvFileHandler(file));
  }
  createSemicolonIntReader(file: File): IntFileReader {
    return new IntFileReader(new SemicolonFileHandler(file));
  }
}
```

이제 API는 `getNextInt()`·`close()`뿐이고, 파일 형식은 주입으로 자유롭게 교체된다. 한 함수만 전달하면 간단하지만 함수가 많으면 지루한데, 코틀린의 기본 위임(`by`)·자바 롬복의 `@Delegate`처럼 **위임(*delegation*)**을 언어 차원에서 지원하기도 한다.

**진정한 is-a 관계라도** 상속은 여전히 주의해야 한다. (1) **취약한 베이스 클래스 문제**(슈퍼클래스 수정이 서브클래스를 깨뜨림), (2) **다이아몬드 문제**(다중 상속 시 어느 슈퍼클래스의 함수를 상속할지 모호), (3) **문제가 있는 계층 구조**(단일 상속만 되는 언어에서 `FlyingCar`가 `Car`·`Aircraft` 둘 다 상속할 수 없음). 계층 구조가 필요하면 **인터페이스로 계층을 정의**하고 **구성으로 코드를 재사용**하는 것이 안전하다.

> **핵심 통찰**: 상속은 강력하지만 그 문제가 치명적일 수 있어 많은 개발자가 가능한 한 피한다. **구성 + 인터페이스**를 쓰면 상속의 단점(추상화 계층 오염, 적응성 저하)은 피하면서 코드 재사용의 이점은 그대로 얻는다.

---

## 4. 클래스는 자신의 기능에만 집중해야 한다 (8.4)

한 개념이 여러 클래스에 흩어지면, 그 개념의 요구사항이 바뀔 때 관련 클래스를 모두 고쳐야 하고 하나라도 빠뜨리면 버그가 된다. `Book` 클래스가 장(chapter)의 단어 수를 직접 세는 `getChapterWordCount()`를 가지면, 이는 `Chapter`의 세부사항(서두·절 구조)을 `Book`에 하드코딩하는 셈이다.

<details>
<summary>의사코드 (원서) — 예제 8.18 → 8.19 (나쁨 → 좋음)</summary>

```java
// ❌ 나쁜 예: Book이 Chapter의 세부사항을 다룬다
class Book {
  private final List<Chapter> chapters;
  Int wordCount() {
    return chapters.map(getChapterWordCount).sum();
  }
  private static Int getChapterWordCount(Chapter chapter) {   // Chapter 세부사항이 Book에!
    return chapter.getPrelude().wordCount() +
        chapter.getSections().map(s -> s.wordCount()).sum();
  }
}

// ✅ 좋은 예: 단어 세는 논리가 Chapter로 이동
class Book {
  private final List<Chapter> chapters;
  Int wordCount() {
    return chapters.map(chapter -> chapter.wordCount()).sum();
  }
}
class Chapter {
  Int wordCount() {
    return getPrelude().wordCount() +
        getSections().map(s -> s.wordCount()).sum();
  }
}
```

</details>

```typescript
// ❌ 나쁜 예: Book이 Chapter의 세부사항(서두·절)을 직접 다룬다
class Book {
  constructor(private readonly chapters: Chapter[]) {}
  wordCount(): number {
    return this.chapters
      .map((chapter) => Book.getChapterWordCount(chapter))
      .reduce((a, b) => a + b, 0);
  }
  private static getChapterWordCount(chapter: Chapter): number {
    return (
      chapter.getPrelude().wordCount() +
      chapter.getSections().map((s) => s.wordCount()).reduce((a, b) => a + b, 0)
    );
  }
}

// ✅ 좋은 예: 단어 세는 논리를 Chapter가 스스로 책임진다
class Book {
  constructor(private readonly chapters: Chapter[]) {}
  wordCount(): number {
    return this.chapters
      .map((chapter) => chapter.wordCount())
      .reduce((a, b) => a + b, 0);
  }
}
class Chapter {
  wordCount(): number {
    return (
      this.getPrelude().wordCount() +
      this.getSections().map((s) => s.wordCount()).reduce((a, b) => a + b, 0)
    );
  }
}
```

이제 "장 끝에 요약을 추가"하는 요구가 와도 `Chapter`만 고치면 된다. 이는 **디미터의 법칙(*Law of Demeter* - 한 객체는 직접 관련된 객체하고만 상호작용하고 다른 객체의 내부 구조를 가정하지 말라)**과 통한다. 나쁜 예의 `chapter.getPrelude().wordCount()`처럼 이웃의 이웃까지 파고드는 호출이 위반 신호다.

---

## 5. 관련 있는 데이터는 함께 캡슐화하라 (8.5)

서로 밀접해 **항상 함께 움직이는** 데이터는 하나의 객체로 묶는 것이 낫다. `TextBox.renderText()`가 `font`·`fontSize`·`lineHeight`·`textColor`를 개별 매개변수로 받으면, 이 값들을 넘겨야 하는 상위 함수(`displayMessage()`)까지 스타일의 세부사항을 알아야 한다. 스타일에 항목(예: 기울임꼴)이 하나 추가되면, 실제로는 스타일과 무관한 `displayMessage()`까지 수정해야 한다.

<details>
<summary>의사코드 (원서) — 예제 8.20~8.23 (나쁨 → 좋음)</summary>

```java
// ❌ 나쁜 예: 스타일 값이 개별 매개변수로 흩어져 있다
void renderText(String text, Font font, Double fontSize,
    Double lineHeight, Color textColor) { ... }

void displayMessage(String message) {   // 스타일 세부사항을 낱낱이 알아야 한다
  messageBox.renderText(message, uiSettings.getFont(), uiSettings.getFontSize(),
      uiSettings.getLineHeight(), uiSettings.getTextColor());
}

// ✅ 좋은 예: 관련 데이터를 TextOptions로 캡슐화
class TextOptions {
  private final Font font;
  private final Double fontSize;
  private final Double lineHeight;
  private final Color textColor;
  // 생성자 + 게터 ...
}
void renderText(String text, TextOptions textStyle) { ... }
void displayMessage(String message) {   // 상자 안 내용은 몰라도 되는 택배기사
  messageBox.renderText(message, uiSettings.getTextStyle());
}
```

</details>

```typescript
// ✅ 좋은 예: 함께 움직이는 스타일 값을 하나의 객체로 캡슐화
class TextOptions {
  constructor(
    private readonly font: Font,
    private readonly fontSize: number,
    private readonly lineHeight: number,
    private readonly textColor: Color,
  ) {}
  getFont(): Font { return this.font; }
  getFontSize(): number { return this.fontSize; }
  getLineHeight(): number { return this.lineHeight; }
  getTextColor(): Color { return this.textColor; }
}

class UserInterface {
  constructor(
    private readonly messageBox: TextBox,
    private readonly uiSettings: UiSettings,
  ) {}
  // displayMessage는 텍스트 스타일의 세부사항을 갖지 않는다
  displayMessage(message: string): void {
    this.messageBox.renderText(message, this.uiSettings.getTextStyle());
  }
}
```

> **핵심 통찰**: `displayMessage()`는 상자 안에 무엇이 든지 모른 채 소포를 배달하는 **택배기사**와 같아야 한다. 단, 캡슐화는 신중히 — 데이터가 따로 떨어지면 의미가 없을 만큼 밀접하거나, 일부만 골라 쓰는 경우가 아닐 때 캡슐화한다(2장의 "너무 많은 것을 한 클래스에 담지 말라"와 균형).

---

## 6. 반환 유형에 구현 세부정보가 유출되지 않도록 주의하라 (8.6)

구현 세부정보를 유출하는 흔한 형태가 **그 세부사항과 밀접히 엮인 유형을 반환**하는 것이다. `ProfilePictureService`가 내부적으로 `HttpFetcher`를 쓴다는 사실은 구현 세부사항인데, `getProfilePicture()`가 `HttpResponse.Status`(HTTP 상태 코드)와 `HttpResponse.Payload`를 반환하면 그 사실이 반환 유형을 통해 새어 나간다.

- 사용자는 50개가 넘는 HTTP 상태 코드를 알아야 하고, "성공=200, 없음=404"를 스스로 추측해야 한다.
- HTTP 대신 WebSocket으로 바꾸는 순간, `HttpResponse` 유형에 의존하던 **모든 코드**를 고쳐야 한다.

**해결책 — 추상화 계층에 맞는 유형을 반환하라**: 사용자가 실제로 신경 써야 할 개념만 담은 **전용 열거형**과 **바이트 리스트**를 반환한다.

<details>
<summary>의사코드 (원서) — 예제 8.24 → 8.25 (나쁨 → 좋음)</summary>

```java
// ❌ 나쁜 예: HTTP 세부사항이 반환 유형으로 유출
class ProfilePictureResult {
  HttpResponse.Status getStatus() { ... }        // HTTP 상태 코드 노출
  HttpResponse.Payload? getImageData() { ... }   // HTTP 페이로드 노출
}

// ✅ 좋은 예: 추상화 계층에 맞는 전용 유형
class ProfilePictureResult {
  enum Status { SUCCESS, USER_DOES_NOT_EXIST, OTHER_ERROR; } // 필요한 상태만
  Status getStatus() { ... }
  List<Byte>? getImageData() { ... }             // 그냥 바이트 리스트
}
```

</details>

```typescript
// ✅ 좋은 예: 사용자가 신경 쓸 개념만 담은 전용 유형 반환
class ProfilePictureResult {
  getStatus(): ProfilePictureStatus { /* ... */ }
  getImageData(): ReadonlyArray<number> | null { /* 바이트 리스트 */ }
}

/** 프로필 사진 조회 결과 상태. HTTP 세부사항을 노출하지 않는다. */
enum ProfilePictureStatus {
  /** 조회 성공 */
  SUCCESS,
  /** 해당 사용자가 존재하지 않음 */
  USER_DOES_NOT_EXIST,
  /** 서버 연결 실패 등 일시적 오류 */
  OTHER_ERROR,
}
```

---

## 7. 예외 처리 시 구현 세부사항이 유출되지 않도록 주의하라 (8.7)

같은 유출이 **예외**에서도 일어난다. `TextSummarizer`가 `TextImportanceScorer` 인터페이스에 의존하는데, 그 구현체인 `ModelBasedScorer`가 `PredictionModelException`(비검사 예외)을 던지면, `TextSummarizer` 사용자는 이 예외를 처리하려다 "내부적으로 모델 기반 예측을 쓴다"는 구현 세부사항을 알게 된다. 게다가 다른 구현체는 전혀 다른 예외를 던질 수 있어 처리 코드가 신뢰할 수 없게 된다.

**해결책 — 계층에 맞는 예외로 감싸라(wrap)**: 각 계층이 자신의 추상화에 맞는 예외 유형만 드러내도록, 하위 계층 오류를 현재 계층의 예외로 감싼다(원래 오류 정보는 `cause`로 보존).

<details>
<summary>의사코드 (원서) — 예제 8.28 · 8.29 계층에 적합한 예외 (좋은 예)</summary>

```java
class TextImportanceScorerException extends Exception {
  TextImportanceScorerException(Throwable cause) { ... }  // 원래 예외를 감싼다
}
interface TextImportanceScorer {
  Boolean isImportant(String text) throws TextImportanceScorerException; // 계층이 노출하는 오류 정의
}
class ModelBasedScorer implements TextImportanceScorer {
  override Boolean isImportant(String text) throws TextImportanceScorerException {
    try {
      return model.predict(text) >= MODEL_THRESHOLD;
    } catch (PredictionModelException e) {
      throw new TextImportanceScorerException(e);          // 구현 예외를 감싸 다시 던진다
    }
  }
}

// 사용하는 쪽은 단 하나의 예외 유형만 처리하면 된다
void updateTextSummary(UserInterface ui) {
  try {
    String summary = textSummarizer.summarizeText(ui.getUserText());
    ui.getSummaryField().setValue(summary);
  } catch (TextSummarizerException e) {
    ui.getSummaryField().setError("Unable to summarize text");
  }
}
```

</details>

```typescript
/** 텍스트 점수 계산과 관련된 오류. 구현체가 무엇이든 이 유형으로 전달된다. */
class TextImportanceScorerError extends Error {
  constructor(readonly cause: unknown) {
    super("text importance scoring failed");
  }
}

interface TextImportanceScorer {
  /** @throws TextImportanceScorerError 점수 계산 실패 시 */
  isImportant(text: string): boolean;
}

class ModelBasedScorer implements TextImportanceScorer {
  isImportant(text: string): boolean {
    try {
      return this.model.predict(text) >= MODEL_THRESHOLD;
    } catch (e) {
      // 구현 세부 예외(PredictionModelError)를 계층에 맞는 예외로 감싼다
      throw new TextImportanceScorerError(e);
    }
  }
}
```

> **핵심 통찰**: 감싸기는 코드 줄이 늘지만, 사용자는 이제 **한 가지 유형의 오류만** 처리하면 되고 그 처리는 구현이 바뀌어도 계속 작동한다. 다만 호출 측이 그 오류로부터 복구하지 않을 것이 확실하다면(상위에서 처리하지 않음) 유출은 큰 문제가 아니다 — 복구 대상 오류일 때만 계층 적합성을 꼭 챙기면 된다.

---

## 8. 코드 품질 6대 요소 연결

이 장의 모든 기법은 **모듈화**를 끌어올리고, 그 결과 **적응성(변경 용이)**·**재사용성**·**테스트 용이성**을 함께 높인다.

| 기법 | 모듈화에 기여하는 방식 |
|---|---|
| 의존성 주입 (8.1) | 의존 대상을 교체 가능하게 만들어 재구성이 쉬워짐 |
| 인터페이스 의존 (8.2) | 구체 구현과 분리 → 간결한 추상화 계층 |
| 구성 vs 상속 (8.3) | 추상화 계층 오염·적응성 저하를 피하며 재사용 |
| 자신의 기능에 집중 (8.4) | 요구사항 변경이 한 클래스에만 영향 |
| 데이터 캡슐화 (8.5) | 중간 계층이 세부사항을 몰라도 됨 |
| 반환·예외 유출 방지 (8.6·8.7) | 구현 세부사항이 계층 밖으로 새지 않음 |

> **핵심 통찰**: 모듈화의 단일 목표는 **"요구사항 변경이 그 요구사항과 직접 관련된 코드에만 영향을 미치게" 하는 것**이다. 이 장의 기법들은 결국 2장의 **간결한 추상화 계층**을 지키는 방법이며, DI·인터페이스·구성은 그 계층의 경계를 교체 가능하게 만드는 세 축이다.

---

## 요약

- 모듈화된 코드는 변경된 요구사항을 적용하기 쉽다. 핵심 목표는 **요구사항 변경이 직접 관련된 코드에만 영향을 미치게** 하는 것이다.
- **의존성 주입**: 의존 대상을 생성자로 주입받아 교체 가능하게 한다. 정적 매달림을 피하도록 설계하라.
- **인터페이스에 의존**: 구체 클래스가 아닌 인터페이스에 의존한다(의존성 역전 원리).
- **상속보다 구성**: 상속은 추상화 계층을 오염시키고 적응성을 낮춘다. 구성 + 인터페이스 + 위임으로 대체하라. 진정한 is-a 관계라도 신중히.
- **자신의 기능에만 집중**: 한 개념의 논리는 그 개념을 담당하는 클래스에 둔다(디미터의 법칙).
- **관련 데이터 캡슐화**: 항상 함께 움직이는 데이터는 하나의 객체로 묶는다.
- **반환 유형·예외로 구현 세부사항을 유출하지 말라**: 추상화 계층에 맞는 전용 유형·예외를 정의하고, 하위 오류는 감싸서 다시 던진다.
