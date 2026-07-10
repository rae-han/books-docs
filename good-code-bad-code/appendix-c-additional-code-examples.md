# Appendix C: Additional Code Examples (추가 예제 코드)

## 핵심 질문

본문에서 단순하게 보여 준 예제를, 실무에서 쓰는 여러 기술과 언어 기능을 동원하면 어떻게 더 완전하게 구현할 수 있는가? 특히 **빌더 패턴(*Builder pattern - 여러 선택적 설정을 단계적으로 지정한 뒤 최종 객체를 만드는 생성 패턴*)**을 제대로 구현하면 어떤 요소들을 고려하게 되는가?

---

## 0. 이 부록에서 다루는 것 · 코드 표기 규약

- **7장(오용하기 어려운 코드)**에서 단순하게 다룬 빌더 패턴을, 실무에 가깝게 더 완전히 구현한 예제

> **코드 표기 규약**: 원서 예제는 자바로 작성되어 있다. 이 노트는 원서의 자바 구현을 `<details>`로 접어 두고(원문 확인용), 그 아래에 **TypeScript 변환본**을 펼쳐 둔다. 자바의 `OptionalDouble`·`Optional<Color>`는 TypeScript에서 널 안전성이 있는 유니언 타입(`number | null`·`Color | null`)으로 옮긴다(부록 B 참고).

---

## 1. 빌더 패턴 (C.1)

7장에서는 빌더 패턴을 단순한 형태로만 구현했다. 실제로 개발자들은 빌더 패턴을 구현할 때 많은 기술과 언어 특징을 사용한다. 아래 예제 C.1은 빌더 패턴을 자바로 좀 더 완전하게 구현한 코드다. 이 구현에서 주목해서 살펴봐야 할 사항은 다음과 같다.

1. **`TextOptions` 클래스 생성자는 프라이빗**이다. 다른 개발자가 빌더 패턴을 사용할 수밖에 없도록 강제하기 위함이다.
2. **`TextOptions` 클래스 생성자는 `Builder`의 인스턴스를 매개변수로 받는다.** 이렇게 하면 매우 긴 매개변수·인수 목록을 피할 수 있어 코드의 가독성과 유지보수성이 조금 더 향상된다.
3. **`TextOptions` 클래스는 `toBuilder()` 메서드를 제공한다.** `Builder` 인스턴스를 생성할 때 기존 `TextOptions` 인스턴스의 값으로 미리 채워 넣어 만들 수 있다(일부만 바꿔 새 인스턴스를 만들 때 유용).
4. **`Builder` 클래스는 `TextOptions` 클래스의 내부 클래스(*inner class - 다른 클래스 안에 정의된 클래스*)**인데, 두 가지 목적을 갖는다.
   - `Builder`를 `TextOptions.Builder`로 참조하게 되므로 클래스 명명이 좀 더 명확해진다.
   - 자바에서는 `TextOptions`와 `Builder` 클래스가 서로의 프라이빗 멤버 변수·메서드에 접근할 수 있다.

이 구현은 조슈아 블로크(*Joshua Bloch*)의 《이펙티브 자바 3판》과 구글 구아바(Guava) 라이브러리 같은 여러 코드베이스에서 영감을 받았다.

<details>
<summary>의사코드 (원서, 자바) — 예제 C.1 빌더 패턴 구현</summary>

```java
public final class TextOptions {
  private final Font font;
  private final OptionalDouble fontSize;
  private final Optional<Color> color;

  // 생성자는 프라이빗이고 Builder 인스턴스를 매개변수로 받는다
  private TextOptions(Builder builder) {
    font = builder.font;
    fontSize = builder.fontSize;
    color = builder.color;
  }

  public Font getFont() {
    return font;
  }

  public OptionalDouble getFontSize() {
    return fontSize;
  }

  public Optional<Color> getColor() {
    return color;
  }

  // TextOptions 인스턴스로 미리 채워진 Builder 인스턴스를 생성한다
  public Builder toBuilder() {
    return new Builder(this);
  }

  // Builder 클래스는 TextOptions 클래스의 내부 클래스다
  public static final class Builder {
    private Font font;
    private OptionalDouble fontSize = OptionalDouble.empty();
    private Optional<Color> color = Optional.empty();

    public Builder(Font font) {
      this.font = font;
    }

    // TextOptions 인스턴스로부터 값을 복사하기 위한 Builder의 프라이빗 생성자
    private Builder(TextOptions options) {
      font = options.font;
      fontSize = options.fontSize;
      color = options.color;
    }

    public Builder setFont(Font font) {
      this.font = font;
      return this;
    }

    public Builder setFontSize(double fontSize) {
      this.fontSize = OptionalDouble.of(fontSize);
      return this;
    }

    public Builder clearFontSize() {
      fontSize = OptionalDouble.empty();
      return this;
    }

    public Builder setColor(Color color) {
      this.color = Optional.of(color);
      return this;
    }

    public Builder clearColor() {
      color = Optional.empty();
      return this;
    }

    public TextOptions build() {
      return new TextOptions(this);
    }
  }
}
```

</details>

```typescript
/** 텍스트 렌더링 옵션(불변 값 객체). 반드시 TextOptionsBuilder로 생성한다. */
class TextOptions {
  constructor(
    // TS의 readonly 공개 필드가 자바의 private 필드 + getter 역할을 대신한다
    readonly font: Font,
    // 자바의 OptionalDouble / Optional<Color> 대신 널 안전성이 있는 유니언 타입을 쓴다
    readonly fontSize: number | null,
    readonly color: Color | null,
  ) {}

  /** 현재 값으로 미리 채워진 빌더를 반환한다 (일부만 바꿔 새 인스턴스를 만들 때 유용) */
  toBuilder(): TextOptionsBuilder {
    const builder = new TextOptionsBuilder(this.font);
    if (this.fontSize !== null) {
      builder.setFontSize(this.fontSize);
    }
    if (this.color !== null) {
      builder.setColor(this.color);
    }
    return builder;
  }
}

class TextOptionsBuilder {
  private font: Font;
  private fontSize: number | null = null;
  private color: Color | null = null;

  constructor(font: Font) {
    this.font = font;
  }

  // 반환 타입 this 로 메서드 체이닝(플루언트 인터페이스)을 지원한다
  setFont(font: Font): this {
    this.font = font;
    return this;
  }

  setFontSize(fontSize: number): this {
    this.fontSize = fontSize;
    return this;
  }

  clearFontSize(): this {
    this.fontSize = null;
    return this;
  }

  setColor(color: Color): this {
    this.color = color;
    return this;
  }

  clearColor(): this {
    this.color = null;
    return this;
  }

  build(): TextOptions {
    return new TextOptions(this.font, this.fontSize, this.color);
  }
}
```

이 코드가 사용되는 몇 가지 예는 다음과 같다.

<details>
<summary>의사코드 (원서, 자바) — 사용 예</summary>

```java
TextOptions options1 = new TextOptions.Builder(Font.ARIAL)
    .setFontSize(12.0)
    .build();

TextOptions options2 = options1.toBuilder()
    .setColor(Color.BLUE)
    .clearFontSize()
    .build();

TextOptions options3 = options2.toBuilder()
    .setFont(Font.VERDANA)
    .setColor(Color.RED)
    .build();
```

</details>

```typescript
const options1 = new TextOptionsBuilder(Font.ARIAL)
  .setFontSize(12.0)
  .build();

// toBuilder()로 options1을 복제해 일부만 바꾼다
const options2 = options1.toBuilder()
  .setColor(Color.BLUE)
  .clearFontSize()
  .build();

const options3 = options2.toBuilder()
  .setFont(Font.VERDANA)
  .setColor(Color.RED)
  .build();
```

### 자바 구현을 TypeScript로 옮길 때의 차이

- **옵셔널 래퍼가 불필요하다**: 자바는 값의 유무를 `OptionalDouble`·`Optional<Color>`로 감쌌지만, TypeScript는 널 안전성이 있으므로 `number | null`·`Color | null`이면 충분하다. "값 없음"은 그냥 `null`이고, 컴파일러가 사용 전 널 확인을 강제한다.
- **getter가 불필요하다**: 자바는 필드를 `private final`로 두고 `getFont()`·`getFontSize()`·`getColor()` getter를 노출했지만, TypeScript는 `readonly` 공개 필드로 같은 불변성·읽기 전용성을 얻으므로 별도 getter가 필요 없다.
- **"빌더로만 생성" 강제 방식이 다르다**: 자바는 `private` 생성자 + 내부 클래스로 (1) 직접 생성을 막고 (2) 두 클래스가 서로의 프라이빗 멤버에 접근하게 했다. TypeScript의 `private`은 **클래스 단위**라 다른 클래스가 프라이빗 생성자에 접근할 수 없다. 직접 생성을 정말로 막아야 한다면 **모듈 전용 심벌 토큰**으로 생성을 제한할 수 있다.

<details>
<summary>참고 — TypeScript에서 "빌더로만 생성"을 강제하는 토큰 기법</summary>

```typescript
// 이 심벌은 모듈 밖으로 export하지 않으므로, 외부 코드는 TextOptions를 직접 생성할 수 없다
const BUILDER_ONLY: unique symbol = Symbol();

class TextOptions {
  constructor(
    token: typeof BUILDER_ONLY,
    readonly font: Font,
    readonly fontSize: number | null,
    readonly color: Color | null,
  ) {
    if (token !== BUILDER_ONLY) {
      throw new Error("TextOptions는 TextOptionsBuilder로만 생성할 수 있다.");
    }
  }
}

// 같은 모듈 안의 빌더만 토큰을 넘길 수 있다
// build() { return new TextOptions(BUILDER_ONLY, this.font, this.fontSize, this.color); }
```

</details>

> **핵심 통찰**: 빌더 패턴의 본질은 **긴 생성자 인수 목록을 이름 있는 단계로 바꾸고, 선택적 설정을 유연하게 지정**하게 하는 것이다(7장). 예제 C.1은 여기에 `toBuilder()`로 기존 값을 복제해 일부만 바꾸는 기능, `clearXxx()`로 설정을 해제하는 기능, 그리고 "빌더로만 생성"을 강제하는 프라이빗 생성자까지 더한 완전한 형태다. 언어마다 이를 구현하는 관용구는 다르지만(자바의 내부 클래스·`Optional` vs TypeScript의 `readonly` 필드·`T | null`), 목표인 **가독성·오용 방지·불변성**은 동일하다.

---

## 요약

- 본문에서 단순하게 소개한 빌더 패턴(7장)을 실무에 가깝게 구현하면, **프라이빗 생성자**(빌더 사용 강제), **`Builder` 인스턴스를 받는 생성자**(긴 인수 목록 회피), **`toBuilder()`**(기존 값 복제 후 일부 수정), **내부 클래스**(명명 개선 + 상호 프라이빗 접근) 같은 요소가 더해진다.
- 자바에서는 값의 유무를 `Optional`로 감싸고, 내부 클래스 + `private` 생성자로 생성을 통제한다.
- TypeScript로 옮기면 **옵셔널 래퍼와 getter가 불필요**해지고(`readonly` 필드 + `T | null`), 메서드 체이닝은 반환 타입 `this`로 표현하며, "빌더로만 생성"을 강제해야 할 때는 **모듈 전용 심벌 토큰**을 쓴다.
- 구현 관용구는 언어마다 달라도, 빌더 패턴이 추구하는 **가독성·오용 방지·불변성**이라는 목표는 동일하다.
