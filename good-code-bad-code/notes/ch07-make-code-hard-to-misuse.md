# Chapter 7: Make Code Hard to Misuse (코드를 오용하기 어렵게 만들라)

## 핵심 질문

코드는 어떻게 오용되어 버그를 낳는가? 가변 객체는 왜 위험하며 어떻게 불변으로 만드는가? 깊은 가변성이란 무엇이고 어떻게 막는가? 지나치게 일반적인 데이터 타입·정수로 표현한 시간은 왜 오용을 부르는가? "진실의 원천을 하나만" 두는 것은 왜 중요한가?

---

## 0. 이 장에서 다루는 것 · 코드 표기 규약

- 코드 오·남용으로 버그가 발생하는 방식과 흔한 오용 경로
- 코드를 오용하기 어렵게 만드는 기법

코드가 오용하기 쉽게 작성되면 조만간 오용되고 소프트웨어가 잘못 작동한다. 설명서(세부 조항)는 간과되기 쉬우므로, **코드 자체를 오용하기 어렵게 설계**하는 것이 중요하다. 이 원칙은 제조업의 **포카요케(*poka-yoke*)**·방어적 디자인과 같으며, 소프트웨어에서는 "사용하기 쉽고 오용하기 어렵게(EUHM, easy to use and hard to misuse)"로 표현된다. 이 장은 6대 요소 중 **오용 방지**를 다룬다.

> **코드 표기 규약**: 원서 의사코드를 `<details>`로 접어 두고 아래에 **TypeScript 변환본**을 병기한다. 널 규약(`Type?` → `Type | null`), `final` → `readonly`.

---

## 1. 불변 객체로 만드는 것을 고려하라 (7.1)

객체가 생성 후 상태를 바꿀 수 없으면 **불변(*immutable*)**이다. 가변 객체는 (a) 추론하기 어렵고(누가 언제 바꿨는지 모름 — 봉인 없는 주스 상자), (b) 멀티스레드에서 취약하다.

> **핵심 통찰**: 불변 객체는 "누구도 해제할 수 없는 변질 방지 봉인"과 같다. 기본적으로 불변으로 만들되 꼭 필요한 곳에서만 가변으로 하라. 세터(setter)를 제공하면 그 인스턴스에 접근하는 모든 코드가 상태를 바꿀 수 있어 오용된다(예: `renderTitle()`이 공유된 `TextOptions`의 폰트 크기를 바꿔 `renderMessage()`에 영향).

**해결책 1 — 생성 시에만 값을 할당**하고 멤버를 `final`(TS `readonly`)로 표시한다.

<details>
<summary>의사코드 (원서) — 예제 7.3 불변 TextOptions</summary>

```java
class TextOptions {
  private final Font font;
  private final Double fontSize;
  TextOptions(Font font, Double fontSize) {
    this.font = font;
    this.fontSize = fontSize;
  }
  Font getFont() { return font; }
  Double getFontSize() { return fontSize; }
}
```

</details>

```typescript
class TextOptions {
  constructor(
    private readonly font: Font,
    private readonly fontSize: number,
  ) {}
  getFont(): Font { return this.font; }
  getFontSize(): number { return this.fontSize; }
}
```

**해결책 2 — 불변성 디자인 패턴**: 값 일부가 선택적이면 **빌더 패턴**(가변 빌더 → `build()`로 불변 인스턴스 반환), 생성 후 일부만 바꾼 복사본이 필요하면 **쓰기 시 복사(copy-on-write)** 패턴을 쓴다.

<details>
<summary>의사코드 (원서) — 예제 7.6 쓰기 시 복사 패턴</summary>

```java
class TextOptions {
  private final Font font;
  private final Double? fontSize;

  TextOptions(Font font) { this(font, null); }          // 필수값 공개 생성자
  private TextOptions(Font font, Double? fontSize) {     // 모든 값 프라이빗 생성자
    this.font = font;
    this.fontSize = fontSize;
  }
  Font getFont() { return font; }
  Double? getFontSize() { return fontSize; }

  TextOptions withFont(Font newFont) { return new TextOptions(newFont, fontSize); }
  TextOptions withFontSize(Double newFontSize) { return new TextOptions(font, newFontSize); }
}
```

</details>

```typescript
class TextOptions {
  // 필수값만 받는 공개 진입점 + 모든 값을 받는 private 생성자
  static create(font: Font): TextOptions {
    return new TextOptions(font, null);
  }
  private constructor(
    private readonly font: Font,
    private readonly fontSize: number | null,
  ) {}

  getFont(): Font { return this.font; }
  getFontSize(): number | null { return this.fontSize; }

  // 원본을 바꾸지 않고 값 하나만 바뀐 새 인스턴스를 반환
  withFont(newFont: Font): TextOptions { return new TextOptions(newFont, this.fontSize); }
  withFontSize(newFontSize: number): TextOptions { return new TextOptions(this.font, newFontSize); }
}
```

---

## 2. 객체를 깊은 수준까지 불변적으로 만드는 것을 고려하라 (7.2)

멤버 변수 자체가 가변 타입(리스트 등)이고 외부가 그 참조를 가지면 **깊은 가변성(*deep mutability*)**이 생긴다. `fontFamily`가 `List<Font>`일 때 — (시나리오 A) 생성자에 넘긴 리스트를 호출자가 나중에 변경하거나, (시나리오 B) `getFontFamily()`로 받은 참조로 내용을 수정하면, `TextOptions`가 몰래 바뀐다.

- **해결책 A — 방어적 복사**: 생성자와 게터에서 리스트를 복사한다. 단, 복사 비용이 크고, 클래스 **내부**의 변경(`final`이어도 `list.add()` 가능)은 못 막는다.
- **해결책 B — 불변 자료구조 사용**(더 강력): `ImmutableList`(Guava), `System.Collections.Immutable`(C#), Immutable.js/Immer(JS). 방어적 복사가 필요 없고 내부 변경도 막는다.

<details>
<summary>의사코드 (원서) — 예제 7.11 ImmutableList 사용</summary>

```java
class TextOptions {
  private final ImmutableList<Font> fontFamily;   // 클래스 내에서도 변경 불가
  private final Double fontSize;
  TextOptions(ImmutableList<Font> fontFamily, Double fontSize) {
    this.fontFamily = fontFamily;
    this.fontSize = fontSize;
  }
  ImmutableList<Font> getFontFamily() { return fontFamily; }   // 방어적 복사 불필요
  Double getFontSize() { return fontSize; }
}
```

</details>

```typescript
class TextOptions {
  // TS: ReadonlyArray<Font>(= readonly Font[])는 push/splice 등 변경 메서드를 타입에서 제거
  constructor(
    private readonly fontFamily: ReadonlyArray<Font>,
    private readonly fontSize: number,
  ) {}
  getFontFamily(): ReadonlyArray<Font> { return this.fontFamily; }
  getFontSize(): number { return this.fontSize; }
}
```

> **핵심 통찰**: TypeScript는 `readonly T[]`(`ReadonlyArray<T>`)·`Readonly<T>`·`ReadonlyMap`/`ReadonlySet`으로 **컴파일 타임에** 깊은 불변성을 강제할 수 있다 — 방어적 복사의 런타임 비용 없이 변경 메서드 자체가 타입에서 사라진다. (자바 `final`은 참조만 불변이지 참조 대상은 불변이 아님을 유의.)

---

## 3. 지나치게 일반적인 데이터 타입을 피하라 (7.3)

정수·문자열·리스트는 일반적이고 다재다능하지만, 그만큼 **스스로 아무것도 설명하지 못하고** 허용 범위가 넓어 오용을 부른다. 지도 위치를 `List<List<Double>>`로 표현하면 — (a) 타입 자체가 무의미하고(문서 필요), (b) 위도·경도 순서를 혼동하기 쉽고, (c) 타입 안전성이 없다(요소 개수가 잘못돼도 컴파일됨). `Pair<Double, Double>`로 바꿔도 순서 혼동·의미 불명은 남는다.

**해결책 — 전용 타입**: 위도·경도를 담는 `LatLong` 클래스를 정의한다(몇 분이면 된다).

<details>
<summary>의사코드 (원서) — 예제 7.16 · 7.17 LatLong 전용 클래스</summary>

```java
class LatLong {
  private final Double latitude;
  private final Double longitude;
  LatLong(Double latitude, Double longitude) {
    this.latitude = latitude;
    this.longitude = longitude;
  }
  Double getLatitude() { return latitude; }
  Double getLongitude() { return longitude; }
}

void markLocationsOnMap(List<LatLong> locations) {
  for (LatLong location in locations) {
    map.markLocation(location.getLatitude(), location.getLongitude());
  }
}
```

</details>

```typescript
/** 지도상의 위치(위도·경도, 각도). */
class LatLong {
  constructor(
    private readonly latitude: number,
    private readonly longitude: number,
  ) {}
  getLatitude(): number { return this.latitude; }
  getLongitude(): number { return this.longitude; }
}

function markLocationsOnMap(locations: LatLong[]): void {
  for (const location of locations) {
    map.markLocation(location.getLatitude(), location.getLongitude());
  }
}
```

> **핵심 통찰**: 지름길(일반적 타입)은 **패러다임이 전염**된다 — `List<Double>`을 쓰면 상호작용하는 다른 코드도 따라 쓰게 되고, 위치 표현이 두 곳에 문서화되어 "진실의 원천"이 둘이 된다(7.6). TS에서는 데이터 전용 객체를 `interface`/`type`으로 정의해 컴파일 타임 안전성을 줄 수도 있다(데이터-동작 결합이 약할 때).

---

## 4. 시간 처리 (7.4)

시간은 (a) 절대 순간 vs 상대적 양, (b) 다양한 단위, (c) 시간대·일광절약·윤년/윤초 때문에 복잡하다. **정수로 시간을 표현하면** 세 가지 오용이 생긴다.

1. **순간인가 양인가**: `sendMessage(message, Int64 deadline)`의 `deadline`이 유닉스 타임스탬프인지 타이머 초인지 모호하다.
2. **단위 불일치**: `getMessageTimeout()`이 초를 반환하는데 `showMessage(..., timeoutMs)`가 밀리초를 받으면, 5초가 5밀리초로 표시된다.
3. **시간대 오류**: 날짜를 로컬 시간대로 해석해 타임스탬프로 저장하면, 다른 시간대 사용자에게 다른 날짜가 보인다.

**해결책 — 적절한 자료구조**: `Instant`(순간)와 `Duration`(양)을 구분하는 라이브러리를 쓴다(java.time, Noda Time, js-joda, C++ chrono). 단위가 타입에 캡슐화되어 혼동·오용이 불가능해진다. 날짜만 필요하면 `LocalDateTime`을 쓴다.

<details>
<summary>의사코드 (원서) — 예제 7.20 Duration 유형 사용</summary>

```java
// deadline이 '시간의 양'임이 타입으로 명백하다
Boolean sendMessage(String message, Duration deadline) { ... }

Duration duration1 = Duration.ofSeconds(5);
Duration duration2 = Duration.ofMinutes(2);
// 어떤 단위로 만들든 toMillis() 등으로 안전하게 읽는다 — 단위 불일치 위험 없음
```

</details>

```typescript
// TS(예: js-joda 또는 유사 라이브러리)
function sendMessage(message: string, deadline: Duration): boolean {
  // deadline이 '순간(Instant)'이 아니라 '양(Duration)'임이 타입으로 드러난다
  // ...
}

const d1 = Duration.ofSeconds(5);
const d2 = Duration.ofMinutes(2);
```

---

## 5. 데이터에 대한 진실의 원천을 하나만 가져라 (7.5)

데이터는 **기본 데이터(primary)**(코드에 제공해야 하는 데이터)와 **파생 데이터(derived)**(기본 데이터로 계산 가능한 데이터)로 나뉜다. 예: 대변·차변은 기본 데이터, 잔액은 파생 데이터. 잔액을 **별도 필드로 저장**하면 "대변 5·차변 2인데 잔액 10" 같은 **논리적으로 불가능한 상태**를 만들 수 있다(둘째 진실의 원천).

**해결책 — 기본 데이터를 유일한 진실의 원천으로**: 잔액을 저장하지 않고 `getBalance()`에서 `credit - debit`으로 계산한다.

<details>
<summary>의사코드 (원서) — 예제 7.23 요청 시 잔액 계산</summary>

```java
class UserAccount {
  private final Double credit;
  private final Double debit;
  UserAccount(Double credit, Double debit) {
    this.credit = credit;
    this.debit = debit;
  }
  Double getCredit() { return credit; }
  Double getDebit() { return debit; }
  Double getBalance() { return credit - debit; }   // 저장하지 않고 계산
}
```

</details>

```typescript
class UserAccount {
  constructor(
    private readonly credit: number,
    private readonly debit: number,
  ) {}
  getCredit(): number { return this.credit; }
  getDebit(): number { return this.debit; }
  getBalance(): number { return this.credit - this.debit; } // 파생값은 계산
}
```

> **핵심 통찰**: 계산 비용이 크면(예: 트랜잭션 목록 합산) **지연 계산(lazy) + 캐싱**을 쓴다. 이때 캐시는 사실상 둘째 진실의 원천이지만, **클래스와 데이터가 불변이면** 캐시가 절대 어긋나지 않아 안전하다 — 또 하나의 불변성 지지 논거다.

---

## 6. 논리에 대한 진실의 원천을 하나만 가져라 (7.6)

진실의 원천은 데이터뿐 아니라 **논리**에도 적용된다. `DataLogger`가 정수 목록을 "10진수 문자열을 쉼표로 연결"해 저장하고, `DataLoader`가 그 역과정을 각자 **독립적으로** 구현하면 — 한쪽만 형식을 바꾸면(예: 16진수로, 줄바꿈 구분자로) 깨진다.

**해결책 — 직렬화/역직렬화를 하나의 재사용 클래스로**: `IntListFormat`에 `serialize()`/`deserialize()`를 두고 구분자·진법도 상수로 한 번만 지정한다.

<details>
<summary>의사코드 (원서) — 예제 7.27 IntListFormat 클래스</summary>

```java
class IntListFormat {
  private const String DELIMITER = ",";
  private const Radix RADIX = Radix.BASE_10;   // 형식이 한 곳에만 존재
  String serialize(List<Int> values) {
    return values.map(value -> value.toString(RADIX)).join(DELIMITER);
  }
  List<Int> deserialize(String serialized) {
    return serialized.split(DELIMITER).map(str -> Int.parse(str, RADIX));
  }
}
```

</details>

```typescript
class IntListFormat {
  private static readonly DELIMITER = ",";
  private static readonly RADIX = 10; // 진법·구분자가 한 곳에만 존재 = 유일한 진실의 원천

  serialize(values: number[]): string {
    return values.map((value) => value.toString(IntListFormat.RADIX)).join(IntListFormat.DELIMITER);
  }
  deserialize(serialized: string): number[] {
    return serialized.split(IntListFormat.DELIMITER).map((str) => parseInt(str, IntListFormat.RADIX));
  }
}
```

> **핵심 통찰**: 직렬화 형식은 `DataLogger`·`DataLoader`가 공유하는 **하위 문제**다(2장). 하위 문제의 해결책을 재사용 가능한 한 계층으로 뽑으면 진실의 원천이 하나가 되어 견고해진다.

---

## 7. 코드 품질 6대 요소 연결

이 장은 6대 요소 중 **오용 방지**를 정면으로 다룬다.

| 기법 | 오용을 어떻게 막는가 |
|---|---|
| 불변 객체 (7.1·7.2) | 공유 객체를 몰래 바꾸는 것을 원천 차단 |
| 전용 타입 (7.3) | 잘못된 값·순서를 컴파일 타임에 막음 |
| Instant/Duration (7.4) | 순간/양·단위 혼동을 타입으로 방지 |
| 단일 진실의 원천 (7.5·7.6) | 논리적으로 불가능한 상태·불일치를 방지 |

> **핵심 통찰**: 이 장의 기법들은 3장(코드 계약)의 확장이다 — **세부 조항(문서)에 의존하지 않고, 타입과 구조로 잘못된 사용을 아예 불가능하게** 만든다. TS에서는 `readonly`·`private constructor`·전용 클래스·판별 유니언이 이를 컴파일 타임에 강제하는 핵심 도구다.

---

## 요약

- **불변 객체로 만드는 것을 고려하라** — 세터를 없애고 생성 시에만 값을 할당(빌더·쓰기 시 복사 패턴 활용).
- **깊은 수준까지 불변으로** — 방어적 복사보다 **불변 자료구조**(TS `readonly T[]`)가 낫다.
- **지나치게 일반적인 데이터 타입을 피하라** — 구체적인 것에는 **전용 타입**을 정의한다.
- **시간은 적절한 자료구조로** — `Instant`(순간)·`Duration`(양)·`LocalDateTime`(날짜)로 정수 표현의 오용을 막는다.
- **데이터·논리 모두 진실의 원천을 하나만** — 파생 데이터는 계산(또는 불변 캐싱), 공유 논리는 하나의 재사용 클래스로.
- 이 모든 것은 **세부 조항이 아니라 타입·구조로 오용을 불가능하게** 만드는 것이 핵심이다.
