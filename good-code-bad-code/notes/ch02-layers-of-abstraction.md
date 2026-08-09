# Chapter 2: Layers of Abstraction (추상화 계층)

## 핵심 질문

복잡한 문제를 어떻게 하위 문제로 세분화하는가? 깔끔한 추상화 계층은 코드 품질의 요소(가독성·모듈화·재사용/일반화·테스트 용이성)를 어떻게 달성하는가? API와 구현 세부사항은 무엇이며, 함수·클래스·인터페이스로 코드를 어떻게 계층으로 나누는가? 계층이 너무 두껍거나 너무 얇으면 어떤 문제가 생기는가?

---

## 0. 이 장에서 다루는 것 · 코드 표기 규약

- 깔끔한 추상화 계층으로 문제를 하위 문제로 세분화하는 방법
- 추상화 계층이 코드 품질 요소를 달성하는 데 어떻게 도움이 되는지
- API 및 구현 세부사항
- 함수·클래스·인터페이스로 코드를 추상화 계층으로 나누는 방법

> **코드 표기 규약**: 원서는 언어 중립적 **의사코드(pseudocode)**를 사용한다. 이 노트는 원서 의사코드를 `<details>`로 접어 두고(원문 확인용), 그 아래에 **TypeScript 변환본**을 펼쳐 둔다. 의사코드의 널 규약도 그대로 옮긴다.

### 널 값 및 널 안전성 규약

이 책의 의사코드는 **널 안전성(null safety)**이 있다고 가정한다. 기본적으로 변수·매개변수·반환 타입은 널을 가질 수 없고, 타입 이름 끝에 `?`가 붙으면 널일 수 있으며 컴파일러가 널 검사를 강제한다. TypeScript에서는 `strictNullChecks` 아래의 유니언 타입(`T | null`)이 이에 대응한다.

<details>
<summary>의사코드 (원서)</summary>

```java
// '?'는 반환값이 널일 수 있음을 나타낸다
Element? getFifthElement(List<Element> elements) {
  if (elements.size() < 5) {
    return null;   // 값을 얻을 수 없으면 널 반환
  }
  return elements[4];
}
```

</details>

```typescript
function getFifthElement(elements: Element[]): Element | null {
  if (elements.length < 5) {
    return null; // 값을 얻을 수 없으면 null 반환
  }
  return elements[4];
}
```

언어가 널 안전성을 지원하지 않으면 널 대신 **옵셔널(Optional)** 타입을 쓰는 것이 좋다(자바·러스트의 `Option`·C++ 등). TypeScript는 유니언 타입으로 널 안전성을 기본 지원하므로 별도 옵셔널이 필요 없다.

---

## 1. 왜 추상화 계층을 만드는가?

코드 작성은 복잡한 문제를 계속해서 더 작은 하위 문제로 세분화하는 작업이다. 예를 들어 "서버에 메시지 보내기"는 단 3줄로 표현되지만(예제 2.1), 그 이면에는 문자열 직렬화, HTTP 프로토콜, TCP 연결, Wi-Fi/셀룰러 확인, 무선 신호 변조, 오류 정정 같은 엄청난 복잡성이 숨어 있다.

<details>
<summary>의사코드 (원서) — 예제 2.1 서버에 메시지 보내기</summary>

```java
HttpConnection connection =
    HttpConnection.connect("http://example.com/server");
connection.send("Hello server");
connection.close();
```

</details>

```typescript
const connection: HttpConnection =
  HttpConnection.connect("http://example.com/server");
connection.send("Hello server");
connection.close();
```

이 코드가 이렇게 간단한 이유는, 다른 개발자들이 하위 문제를 이미 해결했을 뿐 아니라 **그것들을 인식할 필요조차 없게** 만들어 두었기 때문이다. 문제와 하위 문제의 해결책은 일련의 계층을 형성한다. 최상위에서는 HTTP 구현을 몰라도 "서버에 메시지 보내기"에만 신경 쓰면 되고, HttpConnection을 구현한 개발자는 데이터가 무선 신호로 변조되는 방법을 몰라도 됐다. 이것이 **추상화 계층(layers of abstraction)**이다.

> **핵심 통찰**: 문제를 하위 문제로 계속 나누며 추상화 계층을 만들면, 같은 계층 안에서는 이해하기 쉬운 몇 개의 개념만 다루기 때문에 개별 코드가 복잡해 보이지 않는다. 문제가 아무리 복잡해도 **하위 문제를 식별하고 올바른 추상화 계층을 만들면** 쉽게 다룰 수 있다.

---

## 2. 추상화 계층과 코드 품질

깨끗하고 뚜렷한 추상화 계층은 코드 품질의 네 가지 핵심 요소를 직접 끌어올린다.

- **가독성**: 개발자는 코드베이스의 모든 세부사항을 이해할 수 없지만, 한 번에 한두 계층·몇 개 개념만 다루면 되므로 이해하기 쉽다.
- **모듈화**: 구현 세부사항이 계층 밖으로 새지 않으면, 다른 계층에 영향을 주지 않고 계층 내부 구현만 교체할 수 있다(Wi-Fi 모듈 ↔ 셀룰러 모듈).
- **재사용성·일반화성**: 하위 문제의 해결책이 간결한 계층으로 제시되면 재사용이 쉽고, 여러 상황에 일반화될 가능성이 크다(TCP/IP 처리 코드를 WebSocket에도 활용).
- **테스트 용이성**: 집을 살 때 외관만 보지 않고 기초·벽·구조물을 점검하듯, 각 하위 문제의 해결책이 계층으로 분리되면 완벽하게 테스트하기 쉽다.

---

## 3. 코드의 계층: 함수·클래스·인터페이스

추상화 계층을 만드는 실제 방법은 코드를 단위로 나눠 **의존성 그래프**를 형성하는 것이다. 대부분의 언어가 제공하는 분할 요소는 **함수 / 클래스(및 구조체·믹스인) / 인터페이스 / 패키지·네임스페이스·모듈**이다(패키지 수준은 조직·시스템 설계 영역이라 이 책의 범위 밖).

### 3.1 API와 구현 세부사항

코드를 작성할 때 고려할 두 측면이 있다.

- **호출 시 볼 수 있는 내용**: 퍼블릭 클래스·인터페이스·함수, 이름·입력 매개변수·반환 타입이 표현하는 개념, 올바른 사용에 필요한 추가 정보(예: 호출 순서)
- **호출 시 볼 수 없는 내용**: 구현 세부사항(프라이빗 함수·변수, 함수 내부 코드, 의존 라이브러리)

> **핵심 통찰**: 내가 작성한 코드를 다른 코드가 쓸 수 있도록 **미니 API를 노출**하는 것으로 생각하면 유용하다. API는 호출 측에 공개할 개념만 정의하고 나머지는 모두 구현 세부사항이다. 만약 수정 시 구현 세부정보가 API로 **새어 나간다면** 추상화 계층이 명확하게 구분된 것이 아니다.

### 3.2 함수 — 한 문장으로 읽히게

각 함수에 담긴 코드는 **하나의 잘 쓰인 짧은 문장**처럼 읽히면 이상적이다. 예제 2.2는 너무 많은 일을 하는 함수다 — 소유자의 주소를 찾는 자세한 로직과 편지를 보내는 로직을 한 함수가 다 갖고 있어, "소유자의 주소(차량이 폐기됐으면 폐차장, 아직 안 팔렸으면 전시장, 그 외엔 마지막 구매자의 주소)를 찾아 편지를 보내라"라는 **여러 개념이 뒤섞인 나쁜 문장**이 된다.

<details>
<summary>의사코드 (원서) — 예제 2.2 너무 많은 일을 하는 함수 (나쁜 예)</summary>

```java
SendConfirmation? sendOwnerALetter(Vehicle vehicle, Letter letter) {
  Address? ownersAddress = null;
  if (vehicle.hasBeenScraped()) {
    ownersAddress = SCRAPYARD_ADDRESS;
  } else {
    Purchase? mostRecentPurchase = vehicle.getMostRecentPurchase();
    if (mostRecentPurchase == null) {
      ownersAddress = SHOWROOM_ADDRESS;
    } else {
      ownersAddress = mostRecentPurchase.getBuyersAddress();
    }
  }
  if (ownersAddress == null) {
    return null;
  }
  return sendLetter(ownersAddress, letter);
}
```

</details>

```typescript
// ❌ 나쁜 예: 주소 조회 로직과 편지 발송이 한 함수에 뒤섞임
function sendOwnerALetter(
  vehicle: Vehicle,
  letter: Letter,
): SendConfirmation | null {
  let ownersAddress: Address | null = null;
  if (vehicle.hasBeenScraped()) {
    ownersAddress = SCRAPYARD_ADDRESS;
  } else {
    const mostRecentPurchase: Purchase | null = vehicle.getMostRecentPurchase();
    if (mostRecentPurchase === null) {
      ownersAddress = SHOWROOM_ADDRESS;
    } else {
      ownersAddress = mostRecentPurchase.getBuyersAddress();
    }
  }
  if (ownersAddress === null) {
    return null;
  }
  return sendLetter(ownersAddress, letter);
}
```

함수가 하는 일을 **(1) 단일 업무 수행** 또는 **(2) 잘 명명된 다른 함수를 호출해 더 복잡한 동작 구성** 중 하나로 제한하면, 이해하기 쉬운 함수가 된다. 소유자 주소를 찾는 로직을 별도 함수로 빼면 "주소를 찾아보고, 발견되면 편지를 보내라"라는 좋은 문장이 된다.

<details>
<summary>의사코드 (원서) — 예제 2.3 더 작은 함수 (좋은 예)</summary>

```java
SendConfirmation? sendOwnerALetter(Vehicle vehicle, Letter letter) {
  Address? ownersAddress = getOwnersAddress(vehicle);
  if (ownersAddress == null) {
    return null;
  }
  return sendLetter(ownersAddress, letter);
}

// 소유자의 주소를 찾기 위한 함수. 재사용이 쉽다.
private Address? getOwnersAddress(Vehicle vehicle) {
  if (vehicle.hasBeenScraped()) {
    return SCRAPYARD_ADDRESS;
  }
  Purchase? mostRecentPurchase = vehicle.getMostRecentPurchase();
  if (mostRecentPurchase == null) {
    return SHOWROOM_ADDRESS;
  }
  return mostRecentPurchase.getBuyersAddress();
}
```

</details>

```typescript
// ✅ 좋은 예: "주소를 찾아, 있으면 편지를 보낸다"는 한 문장
function sendOwnerALetter(
  vehicle: Vehicle,
  letter: Letter,
): SendConfirmation | null {
  const ownersAddress: Address | null = getOwnersAddress(vehicle);
  if (ownersAddress === null) {
    return null;
  }
  return sendLetter(ownersAddress, letter);
}

// 소유자의 주소를 찾는 로직을 분리 — 재사용이 쉽다
function getOwnersAddress(vehicle: Vehicle): Address | null {
  if (vehicle.hasBeenScraped()) {
    return SCRAPYARD_ADDRESS;
  }
  const mostRecentPurchase: Purchase | null = vehicle.getMostRecentPurchase();
  if (mostRecentPurchase === null) {
    return SHOWROOM_ADDRESS;
  }
  return mostRecentPurchase.getBuyersAddress();
}
```

> **직접 해보기**: 함수를 작성한 뒤 **그 코드를 한 문장으로 말해 보라.** 문장이 어색하거나 "그리고", "또한"이 많이 들어간다면 함수가 너무 길다는 신호이며, 로직 일부를 잘 명명된 헬퍼 함수로 분리하는 것이 좋다.

### 3.3 클래스 — 응집력과 관심사 분리

단일 클래스의 이상적 크기에 대한 여러 경험칙이 있다.

- **줄 수**: "한 클래스는 300줄을 넘지 않아야 한다" 같은 가이드라인. 단, 이는 *"뭔가 잘못됐을지 모른다"는 경고*일 뿐 300줄 이하가 옳다는 보장은 아니다
- **응집력(cohesion)**: 클래스 내 요소들이 얼마나 잘 속해 있는지의 척도. 순차적 응집력(한 요소의 출력이 다음의 입력 — 원두 갈기→커피 추출), 기능적 응집력(여러 요소가 하나의 일을 성취 — 케이크 도구를 한 서랍에) 등
- **관심사의 분리(separation of concerns)**: 시스템을 각각 별개의 문제를 다루는 구성 요소로 분리(게임 콘솔과 TV를 분리하면 각각 독립적으로 업그레이드 가능)

> **핵심 통찰**: "클래스는 응집력이 있어야 한다"에 반대하는 개발자는 거의 없지만, 알면서도 여전히 너무 큰 클래스를 작성한다. 경험칙을 외우기보다 **1장의 핵심 요소(가독성·모듈화·재사용/일반화·테스트 용이)에 비추어** 이 클래스가 저품질인지 판단하는 것이 더 낫다.

예제 2.4의 `TextSummarizer`는 텍스트 요약이라는 "한 가지 일"을 한다고 주장할 수 있지만, 실제로는 (1) 단락 분할, (2) 중요도 점수 계산, (3) 명사·동사·형용사 추출이라는 여러 하위 문제를 한 클래스에 담아 다섯 가지 핵심 요소를 모두 위반한다(가독성↓, 모듈화↓, `splitIntoParagraphs`를 재사용 불가, 입력이 일반 텍스트라 가정해 일반화 불가, 내부 로직을 개별 테스트 불가).

개선책은 각 하위 문제를 **자체 클래스로 분리**하고 생성자 매개변수로 주입하는 것이다. 이 패턴을 **의존성 주입(dependency injection)**이라 하며 8장에서 자세히 다룬다.

<details>
<summary>의사코드 (원서) — 예제 2.5 각 개념에 대한 별도의 클래스 (좋은 예)</summary>

```java
class TextSummarizer {
  private final ParagraphFinder paragraphFinder;
  private final TextImportanceScorer importanceScorer;

  // 생성자를 통해 의존하는 클래스의 인스턴스가 주입된다 (의존성 주입)
  TextSummarizer(
      ParagraphFinder paragraphFinder,
      TextImportanceScorer importanceScorer) {
    this.paragraphFinder = paragraphFinder;
    this.importanceScorer = importanceScorer;
  }

  // 기본 인스턴스를 생성하는 정적 팩토리 함수
  static TextSummarizer createDefault() {
    return new TextSummarizer(
        new ParagraphFinder(), new TextImportanceScorer());
  }

  String summarizeText(String text) {
    return paragraphFinder.find(text)
        .filter(paragraph -> importanceScorer.isImportant(paragraph))
        .join("\n\n");
  }
}

class ParagraphFinder { /* 텍스트를 단락으로 나누는 하위 문제만 담당 */ }
class TextImportanceScorer { /* 중요도 점수 계산 하위 문제만 담당 */ }
```

</details>

```typescript
class TextSummarizer {
  // TS의 매개변수 프로퍼티로 주입과 필드 선언을 한 번에
  constructor(
    private readonly paragraphFinder: ParagraphFinder,
    private readonly importanceScorer: TextImportanceScorer,
  ) {}

  // 기본 인스턴스를 생성하는 정적 팩토리 함수
  static createDefault(): TextSummarizer {
    return new TextSummarizer(
      new ParagraphFinder(),
      new TextImportanceScorer(),
    );
  }

  summarizeText(text: string): string {
    return this.paragraphFinder.find(text)
      .filter((paragraph) => this.importanceScorer.isImportant(paragraph))
      .join("\n\n");
  }
}

class ParagraphFinder { /* 텍스트를 단락으로 나누는 하위 문제만 담당 */ }
class TextImportanceScorer { /* 중요도 점수 계산 하위 문제만 담당 */ }
```

이제 `TextSummarizer`를 보면 몇 초 만에 "단락을 찾고 → 중요하지 않은 것을 걸러내고 → 남은 단락을 연결한다"는 상위 알고리즘을 파악할 수 있고, `ParagraphFinder`는 다른 문제에서도 재사용할 수 있다.

### 3.4 인터페이스 — 구현 교체

하나의 추상화 계층을 **두 가지 이상의 방식으로 구현**하거나 향후 다르게 구현할 것으로 예상되면 **인터페이스**를 정의하는 것이 좋다. 상위 계층은 인터페이스에만 의존하고 구체적인 구현 클래스에는 의존하지 않는다. 예를 들어 중요도 점수 계산을 단어 기반(`WordBasedScorer`)과 머신러닝 기반(`ModelBasedScorer`) 둘 중 하나로 교체하고 싶다면:

<details>
<summary>의사코드 (원서) — 예제 2.6 인터페이스 및 구현 클래스</summary>

```java
interface TextImportanceScorer {
  Boolean isImportant(String text);
}

class WordBasedScorer implements TextImportanceScorer {
  override Boolean isImportant(String text) {
    return calculateImportance(text) >= IMPORTANCE_THRESHOLD;
  }
  private Double calculateImportance(String text) { ... }
}

class ModelBasedScorer implements TextImportanceScorer {
  private final TextPredictionModel model;

  static ModelBasedScorer create() {
    return new ModelBasedScorer(TextPredictionModel.load(MODEL_FILE));
  }
  override Boolean isImportant(String text) {
    return model.predict(text) >= MODEL_THRESHOLD;
  }
}
```

</details>

```typescript
/** 단락이 요약에 포함될 만큼 중요한지 판정하는 채점기. */
interface TextImportanceScorer {
  /** 주어진 텍스트(단락)가 중요한지 여부 */
  isImportant(text: string): boolean;
}

class WordBasedScorer implements TextImportanceScorer {
  isImportant(text: string): boolean {
    return this.calculateImportance(text) >= IMPORTANCE_THRESHOLD;
  }
  private calculateImportance(text: string): number {
    /* ... 복잡한 수식 ... */
  }
}

class ModelBasedScorer implements TextImportanceScorer {
  private constructor(private readonly model: TextPredictionModel) {}

  static create(): ModelBasedScorer {
    return new ModelBasedScorer(TextPredictionModel.load(MODEL_FILE));
  }
  isImportant(text: string): boolean {
    return this.model.predict(text) >= MODEL_THRESHOLD;
  }
}
```

`TextSummarizer`는 어떤 채점기를 쓸지 **팩토리 함수**로 구성한다(예제 2.7: `createWordBasedSummarizer()`, `createModelBasedSummarizer()`).

**구현이 하나뿐이어도 인터페이스를 둘 것인가?**(예제 2.8) — 팀이 결정할 사안이다. 장점: 퍼블릭 API가 매우 명확해지고, "구현이 하나뿐"이라는 추측이 틀린 것으로 판명될 때 대비가 되며, 테스트 시 목(mock)·페이크로 교체하기 쉽다. 단점: 코드가 더 필요하고, 로직 탐색이 복잡해진다.

> **핵심 통찰**: 저자의 경험상 **모든 클래스에 인터페이스를 붙이는 극단**은 통제 불가능하고 불필요하게 복잡해진다. 인터페이스의 장점이 확실한 상황에서만 쓰되, **인터페이스만을 위한 인터페이스는 만들지 말라.** 다만 인터페이스가 없더라도 어떤 함수를 퍼블릭으로 노출할지는 신중히 정해야 한다.

### 3.5 층이 너무 얇아질 때

계층을 나누면 장점이 많지만 비용도 있다 — 보일러플레이트 코드로 코드량이 늘고, 로직을 따라가는 데 노력이 더 들며, 인터페이스 뒤에 숨기면 어떤 구현이 쓰이는지 파악하기 어려워진다. 예제 2.9는 `ParagraphFinder`를 `ParagraphStartOffsetDetector`와 `ParagraphEndOffsetDetector`로 쪼개고 공통 인터페이스 뒤에 두는데, 이 둘은 서로 밀접하게 연관되어 따로 쓰일 일이 없으므로 **계층이 너무 얇아진** 경우다(분할을 위한 분할).

> **핵심 통찰**: 계층 규모에 대한 단 하나의 규칙은 없다. 다만 일반적으로 **너무 많은 일을 하는 계층이 너무 적은 일을 하는 계층보다 더 문제**가 된다. 따라서 확실하지 않다면, 남용의 위험이 있더라도 **계층을 여러 개로 나누는 것이 한 계층에 다 넣는 것보다 낫다.**

---

## 4. 마이크로서비스는 어떤가?

마이크로서비스 아키텍처에서는 개별 문제의 해결책이 독립적으로 실행되는 서비스로 배포된다. "마이크로서비스 자체가 간결한 추상화 계층을 제공하므로 내부 코드 구조는 중요하지 않다"는 주장을 듣기도 하지만, 마이크로서비스는 대개 **크기와 범위**를 기준으로 나뉘므로 그 내부에서도 여전히 적절한 추상화 계층이 유용하다. 재고 관리 마이크로서비스도 "재고 수준 관리"라는 한 가지 일을 위해 창고 위치 결정·DB 질의·데이터 해석 같은 여러 하위 문제를 해결해야 하며, 다른 팀이 그 일부(예: DB 데이터 해석 로직)를 재사용하고 싶어 할 수 있다.

---

## 5. 코드 품질 6대 요소 연결

이 장의 핵심 기법인 **추상화 계층**은 6대 요소 중 다음 넷을 직접 끌어올린다.

| 6대 요소 | 추상화 계층이 개선하는가? | 근거 |
|---|---|---|
| 읽기 쉬움 | ✅ | 한 번에 한두 계층·몇 개 개념만 다룸 |
| 모듈화 | ✅ | 구현 세부사항이 계층 밖으로 새지 않아 내부만 교체 가능 |
| 재사용·일반화 | ✅ | 하위 문제 해결책을 독립적으로 재사용·일반화 |
| 테스트 용이 | ✅ | 각 하위 문제 해결책을 개별적으로 완벽히 테스트 |
| 예측 가능 | (간접) | 3·4·6장에서 다룸 |
| 오용 어렵게 | (간접) | 3·7장에서 다룸 |

> **핵심 통찰**: 추상화 계층은 **API/구현 세부사항의 경계를 명확히 긋는 것**이 본질이다. 함수(3.2)는 가장 작은 계층 단위, 클래스(3.3)는 하위 문제를 묶는 단위, 인터페이스(3.4)는 계층을 명시적으로 표현하고 구현을 교체 가능하게 하는 단위다.

---

## 요약

- 코드를 깨끗하고 뚜렷한 추상화 계층으로 세분화하면 가독성·모듈화·재사용·일반화·테스트 용이성이 향상된다.
- 함수·클래스·인터페이스(및 언어별 기능)를 사용해 코드를 추상화 계층으로 나눈다.
  - **함수**: 하나의 잘 쓰인 문장처럼 읽히게 — 단일 업무 또는 잘 명명된 함수들의 조합.
  - **클래스**: 응집력·관심사 분리를 고려하되, 경험칙보다 4대 핵심 요소로 판단. 하위 문제를 별도 클래스로 분리하고 **의존성 주입**으로 조립.
  - **인터페이스**: 구현이 둘 이상이거나 교체가 예상될 때 정의. "인터페이스만을 위한 인터페이스"는 금물.
- 계층을 나누는 방법은 해결 중인 실제 문제에 대한 판단과 지식을 사용해야 한다.
- **너무 비대한 계층의 문제가 너무 얇은 계층의 문제보다 더 심각하다.** 확실하지 않으면 얇게 나누는 쪽이 낫다.
- 마이크로서비스 내부에서도 올바른 추상화 계층은 여전히 중요하다.
