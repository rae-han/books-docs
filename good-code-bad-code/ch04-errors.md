# Chapter 4: Errors (오류)

## 핵심 질문

시스템이 복구할 수 있는 오류와 복구할 수 없는 오류는 어떻게 구분하는가? "신속한 실패"와 "요란한 실패"는 무엇이며 왜 중요한가? 오류를 호출자에게 전달하는 방법에는 무엇이 있고, 그중 **명시적** 방법과 **암시적** 방법은 어떻게 다른가? 복구 가능한 오류에는 어떤 방법을 써야 하는가?

---

## 0. 이 장에서 다루는 것 · 코드 표기 규약

- 시스템이 복구할 수 있는 오류와 복구할 수 없는 오류의 구분
- 신속하게 실패하고(fail fast) 분명하게 실패하기(fail loudly)
- 오류를 전달하는 다양한 기법과 선택을 위한 고려사항

코드가 실행되는 환경은 불완전하다 — 사용자가 잘못된 입력을 주고, 외부 시스템이 다운되며, 코드에는 버그가 있다. **오류는 불가피하다.** 오류 사례를 신중히 생각하지 않고는 견고하고 신뢰성 높은 코드를 쓸 수 없다. 이 장은 1장의 6대 요소 중 **예측 가능성**과 **오용 방지**에 크게 기여한다. (오류 처리는 소프트웨어 엔지니어와 언어 설계자 사이에서도 의견이 갈리는 첨예한 주제라, 원서에서도 이 장이 가장 길다.)

> **코드 표기 규약**: 원서 의사코드를 `<details>`로 접어 두고 아래에 **TypeScript 변환본**을 펼쳐 병기한다. 널 규약(`Type?` → `Type | null`, `== null` → `=== null`)을 따른다.

---

## 1. 복구 가능성

### 1.1 복구 가능한 오류 vs 복구할 수 없는 오류

- **복구 가능한 오류**: 적절히 처리하면 작동을 계속할 합리적 방법이 있는 오류. 잘못된 사용자 입력(잘못된 전화번호), 네트워크 오류, 중요하지 않은 작업(통계 기록) 오류 등. 일반적으로 **시스템 외부**에서 야기되는 오류는 시스템 전체가 표 나지 않게 적절히 처리하려 노력해야 한다.
- **복구할 수 없는 오류**: 복구할 합리적 방법이 없는 오류. 대개 **프로그래밍 오류**(필요한 리소스 없음, 잘못된 입력 인수로 호출, 상태 미초기화)다. 코드가 할 수 있는 최선은 피해를 최소화하고 개발자가 문제를 발견·수정할 가능성을 최대화하는 것 — 이것이 2절의 신속한 실패·요란한 실패다.

### 1.2 호출하는 쪽에서만 복구 가능 여부를 알 때가 많다

코드는 재사용되고 여러 곳에서 호출되므로, 함수를 작성하는 시점에 그 오류가 복구 가능한지 항상 알 수는 없다. 같은 `PhoneNumber.parse()`라도 호출 맥락에 따라 다르다.

<details>
<summary>의사코드 (원서) — 예제 4.1 전화번호 분석</summary>

```java
class PhoneNumber {
  static PhoneNumber parse(String number) {
    if (!isValidPhoneNumber(number)) {
      // ... 에러를 처리하기 위한 코드 ... 프로그램이 복구할 수 있는가?
    }
    ...
  }
}

// 하드코딩된 잘못된 번호 → 프로그래밍 오류(복구 불가)
PhoneNumber getHeadOfficeNumber() {
  return PhoneNumber.parse("01234typo56789");
}

// 사용자가 입력한 번호 → 복구 가능(UI에 오류 메시지 표시)
PhoneNumber getUserPhoneNumber(UserInput input) {
  return PhoneNumber.parse(input.getPhoneNumber());
}
```

</details>

```typescript
class PhoneNumber {
  static parse(number: string): PhoneNumber {
    if (!isValidPhoneNumber(number)) {
      // ... 이 오류를 프로그램이 복구할 수 있는가? — 호출 맥락에 달렸다
    }
    // ...
  }
}

// 하드코딩된 잘못된 번호 → 프로그래밍 오류(복구 불가)
function getHeadOfficeNumber(): PhoneNumber {
  return PhoneNumber.parse("01234typo56789");
}

// 사용자가 입력한 번호 → 복구 가능(UI에 오류 메시지 표시)
function getUserPhoneNumber(input: UserInput): PhoneNumber {
  return PhoneNumber.parse(input.getPhoneNumber());
}
```

> **핵심 통찰**: 함수가 어디서 호출될지 완전히 알 수 없거나 재사용될 가능성이 있다면, **호출하는 쪽에서 오류를 복구하고자 한다고 가정**해야 한다. 단, 특정 입력이 무효라는 점이 코드 계약으로 명확하고 호출 측이 쉽게 사전 검증할 수 있는 경우(예: 음수 인덱스)는 예외로, 프로그래밍 오류(복구 불가)로 간주할 수 있다.

### 1.3 호출하는 쪽이 오류를 인지하도록 하라

호출자가 오류로부터 복구하기를 원한다고 판단했더라도, **오류가 발생할 수 있다는 것조차 모르면** 제대로 처리하지 못한다. 따라서 함수 작성자는 오류 발생 가능성을 호출 측이 확실히 인지하도록 해야 한다(3절·5절).

---

## 2. 견고성 vs 실패

오류가 발생하면 (1) **실패**시켜 상위 계층이 처리하거나 프로그램을 멈추게 하거나, (2) **오류를 처리하고 계속 진행**할 수 있다. 계속 진행하면 더 견고해 보이지만, 오류가 감지되지 않고 이상한 일이 벌어질 수도 있다.

### 2.1 신속하게 실패하라 (fail fast)

> **비유 — 송로버섯 개**: 송로버섯을 발견하자마자 멈추도록 훈련된 개가, 발견 후 무작위로 10미터 걷다 짖는 개보다 낫다. 코드도 문제의 **실제 발생 지점에 최대한 가까운 곳에서** 오류를 나타내야 한다.

신속한 실패는 잘못된 인수로 함수가 호출되는 **즉시** 오류를 내는 것이다. 그러면 스택 트레이스가 오류의 정확한 위치를 가리켜 디버깅이 쉽고, 잘못된 값으로 계속 실행하다 엉뚱한 곳(예: 데이터베이스에 손상된 데이터 저장)에서 터지는 것을 막는다.

### 2.2 요란하게 실패하라 (fail loudly)

복구할 수 없는 오류(프로그래밍 오류)는 **개발팀이 알아야만 고칠 수 있다.** 요란한 실패는 오류가 발생하는데도 아무도 모르는 상황을 막는 것이다. 가장 명백한 방법은 예외를 발생시켜 프로그램을 중단시키는 것이고, 오류 메시지 로깅도 방법이지만 무시될 위험이 있다.

### 2.3 복구 가능성의 범위

복구 가능/불가능의 범위는 상황에 따라 다르다. 서버에서 한 요청을 처리하다 오류가 나면, **그 요청 범위에서는 복구 불가**여도 **서버 전체로는 복구 가능**하다(전체가 멈추지 않게). 견고성(전체가 안 멈춤)과 요란한 실패(오류를 알림)는 종종 충돌하는데, 해결책은 **프로그래밍 오류를 기록·모니터링**하고 발생률이 높아지면 개발자에게 알리는 것이다. (대부분의 서버 프레임워크가 요청별 오류 격리 기능을 내장하고 있다.)

### 2.4 오류를 숨기지 말라

오류를 숨기면 (복구 가능한 오류는) 호출자가 복구할 기회를 잃고, (복구 불가능한 오류는) 프로그래밍 오류가 감춰진다. 오류를 숨기는 흔한 안티패턴들:

- **기본값 반환**: 오류 시 `0.0`을 반환하면, 잔액 조회 실패와 "잔액이 실제로 0"을 구분할 수 없다(예제 4.3)
- **널 객체 패턴**: 오류 시 빈 리스트를 반환하면 "미지급 송장 없음"으로 오해된다(6장에서 상세)
- **아무것도 하지 않음**: 통화 불일치 시 조용히 `return`하거나(예제 4.5), `catch {}`로 예외를 억제(예제 4.6)

<details>
<summary>의사코드 (원서) — 예제 4.3 기본값 반환 (나쁜 예)</summary>

```java
class AccountManager {
  private final AccountStore accountStore;

  Double getAccountBalanceUsd(Int customerId) {
    AccountResult result = accountStore.lookup(customerId);
    if (!result.success()) {
      return 0.0;   // 오류가 발생하면 기본값 0이 반환된다 → 오류를 숨긴다
    }
    return result.getAccount().getBalanceUsd();
  }
}
```

</details>

```typescript
// ❌ 나쁜 예: 오류를 기본값으로 숨긴다 — "잔액 0"과 구별 불가
class AccountManager {
  constructor(private readonly accountStore: AccountStore) {}

  getAccountBalanceUsd(customerId: number): number {
    const result = this.accountStore.lookup(customerId);
    if (!result.success) {
      return 0.0; // 조회 실패인데 잔액 0으로 보인다 → 사용자가 기겁한다
    }
    return result.getAccount().getBalanceUsd();
  }
}
```

> **참고 — 로그에 담기는 내용에 주의**: 예외를 로깅할 때 예외 객체에 이메일 주소 같은 개인정보가 포함될 수 있고, 이를 로그에 남기면 데이터 처리 정책을 위반할 수 있다.

---

## 3. 오류 전달 방법

오류가 발생하면 보통 더 높은 계층으로 알려야 한다. 방법은 크게 둘로 나뉜다 — 이 구분은 "요란/조용히 실패하느냐"가 아니라 **코드를 쓰는 개발자 관점에서 오류 발생 가능성이 명시적으로 드러나느냐**의 문제다.

- **명시적 방법**: 호출 측이 오류 가능성을 **인지할 수밖에 없다.** 코드 계약의 명확한 부분에 나타난다.
- **암시적 방법**: 호출 측이 오류를 신경 쓰지 않아도 된다. 오류를 알려면 문서·코드를 읽는 적극적 노력이 필요하다(세부 조항이거나 아예 없음).

| 명시적 기법 | 암시적 기법 |
|---|---|
| 검사 예외, 널 반환 타입(널 안전성 시), 옵셔널 반환, 리절트 반환, 아웃컴 반환(확인 필수 시), 스위프트 오류 | 비검사 예외, 매직값 반환(피하라), 프로미스/퓨처, 어서션, 패닉 |

아래에서는 **제곱근 함수 `getSquareRoot()`**(음수 입력 시 오류)를 공통 예로 각 기법을 비교한다.

### 3.1 검사 예외 (명시적)

컴파일러가 호출 측에 예외 처리 또는 시그니처 선언을 **강제**하므로 명시적이다. 자바에서 `Exception`을 확장하면 검사 예외가 된다.

> **핵심 통찰**: **TypeScript/JavaScript에는 검사 예외가 없다.** 모든 `throw`는 비검사(암시적)다. 따라서 자바의 검사 예외에 대응하는 "컴파일러가 강제하는 명시적 오류"를 TS에서 원한다면 **예외 대신 반환 타입(널 가능·리절트·아웃컴)**을 써야 한다.

<details>
<summary>의사코드 (원서) — 예제 4.8 검사 예외 발생</summary>

```java
class NegativeNumberException extends Exception {  // 검사 예외
  private final Double erroneousNumber;
  NegativeNumberException(Double erroneousNumber) {
    this.erroneousNumber = erroneousNumber;  // 오류를 유발한 값을 캡슐화
  }
  Double getErroneousNumber() { return erroneousNumber; }
}

// 함수는 검사 예외를 발생시킬 수 있음을 선언해야 한다
Double getSquareRoot(Double value) throws NegativeNumberException {
  if (value < 0.0) {
    throw new NegativeNumberException(value);
  }
  return Math.sqrt(value);
}
```

</details>

```typescript
// TS에는 검사 예외가 없다. throw는 모두 비검사(암시적)다.
class NegativeNumberError extends Error {
  constructor(readonly erroneousNumber: number) {
    super(`음수의 제곱근: ${erroneousNumber}`);
  }
}

function getSquareRoot(value: number): number {
  if (value < 0.0) {
    throw new NegativeNumberError(value); // 컴파일러가 처리를 강제하지 않는다
  }
  return Math.sqrt(value);
}
```

호출 측은 `try/catch`로 처리하거나, (자바에서는) 자신의 시그니처에 다시 선언해 상위로 넘긴다. 처리도 선언도 않으면 컴파일되지 않는다 → 명시적.

### 3.2 비검사 예외 (암시적)

`RuntimeException`을 확장하면 비검사 예외다. 호출 측은 예외 발생 사실을 전혀 모를 수 있고, 문서화는 권장이지 강제가 아니다(=세부 조항). 따라서 암시적이다. 대부분의 주요 언어에서 "예외"는 비검사 예외를 의미한다(TS/JS 포함).

### 3.3 널 값이 가능한 반환 타입 (명시적)

값을 얻는 것이 불가능함을 나타내는 간단한 방법. **널 안전성을 지원하면** 호출 측이 널 확인을 강제당하므로 명시적이다. 단, 오류 이유는 전달하지 못한다.

<details>
<summary>의사코드 (원서) — 예제 4.14 널 값 반환</summary>

```java
// 제공되는 값이 음수이면 널을 반환한다.
Double? getSquareRoot(Double value) {
  if (value < 0.0) {
    return null;
  }
  return Math.sqrt(value);
}
```

</details>

```typescript
function getSquareRoot(value: number): number | null {
  if (value < 0.0) {
    return null; // 오류 '이유'는 전달하지 못한다
  }
  return Math.sqrt(value);
}
```

### 3.4 리절트 반환 타입 (명시적)

널·옵셔널과 달리 **오류의 이유까지** 전달할 수 있다. 스위프트·러스트·F#은 리절트 타입을 언어로 지원한다.

> **핵심 통찰**: 원서는 리절트를 `Optional<V>`와 `Optional<E>`를 감싼 클래스로 구현하지만(`hasError()` 확인 후 `getValue()` 호출), **TypeScript에서는 판별 유니언(discriminated union)**이 훨씬 낫다. `ok` 태그로 분기하면, 오류를 확인하지 않고 값에 접근하는 실수를 **타입 시스템이 컴파일 타임에 차단**한다.

<details>
<summary>의사코드 (원서) — 예제 4.16 · 4.17 리절트 유형</summary>

```java
class Result<V, E> {
  private final Optional<V> value;
  private final Optional<E> error;
  private Result(Optional<V> value, Optional<E> error) { ... }
  static Result<V, E> ofValue(V value) { ... }
  static Result<V, E> ofError(E error) { ... }
  Boolean hasError() { return error.isPresent(); }
  V getValue() { return value.get(); }   // hasError() 확인을 잊으면 무용지물
  E getError() { return error.get(); }
}

Result<Double, NegativeNumberError> getSquareRoot(Double value) {
  if (value < 0.0) {
    return Result.ofError(new NegativeNumberError(value));
  }
  return Result.ofValue(Math.sqrt(value));
}
```

</details>

```typescript
// TS: 판별 유니언 — 오류 확인 없이 value 접근 시 컴파일 에러
type Result<V, E> =
  | { readonly ok: true; readonly value: V }
  | { readonly ok: false; readonly error: E };

function getSquareRoot(value: number): Result<number, NegativeNumberError> {
  if (value < 0.0) {
    return { ok: false, error: new NegativeNumberError(value) };
  }
  return { ok: true, value: Math.sqrt(value) };
}

// 호출 측: ok로 좁히기 전에는 value에 접근할 수 없다
const result = getSquareRoot(input);
if (!result.ok) {
  ui.setError(`음수의 제곱근: ${result.error.erroneousNumber}`);
} else {
  ui.setOutput(`제곱근: ${result.value}`);
}
```

### 3.5 아웃컴 반환 타입 (명시적)

값을 반환하지 않고 동작만 하는 함수는, 수행 결과를 나타내는 값(불리언·열거형)을 반환할 수 있다. 결과가 셋 이상이거나 참/거짓이 모호하면 열거형이 낫다.

<details>
<summary>의사코드 (원서) — 예제 4.19 아웃컴 반환</summary>

```java
Boolean sendMessage(Channel channel, String message) {
  if (channel.isOpen()) {
    channel.send(message);
    return true;   // 전송되면 참
  }
  return false;    // 오류면 거짓
}
```

</details>

```typescript
function sendMessage(channel: Channel, message: string): boolean {
  if (channel.isOpen()) {
    channel.send(message);
    return true;
  }
  return false;
}
```

> **핵심 통찰**: 아웃컴의 약점은 호출 측이 **반환값을 무시**할 수 있다는 것이다(예제 4.21). 자바 `@CheckReturnValue`, C# `MustUseReturnValue`, C++ `[[nodiscard]]`처럼 반환값 무시 시 경고를 내게 하면 명시적이 된다. TS에는 표준 기능이 없어, 무시하면 안 되는 경우 리절트 타입으로 강제하는 편이 낫다.

### 3.6 프로미스/퓨처 (암시적)

비동기 함수는 프로미스/퓨처를 반환한다. 오류 처리(`catch`)가 강제되지 않고 세부 조항을 읽어야 알 수 있어 **암시적**이다. `Promise<Result<V, E>>`를 반환하면 명시적으로 만들 수 있지만 타입이 복잡해진다.

### 3.7 매직값 반환 (암시적, 피하라)

정상 반환 타입에 속하지만 특별한 의미를 부여하는 값(예: 음수 입력 시 `-1` 반환). 문서·코드를 읽어야 알 수 있어 암시적이며, 예상 이탈·버그를 부른다(6장에서 상세).

> **핵심 통찰**: **매직값은 오류를 알리는 좋은 방법이 아니다.** `-1` 같은 값은 정상 결과와 섞여 조용히 버그를 만든다.

---

## 4. 복구할 수 없는 오류의 전달

현실적으로 복구 불가능한 오류는 **신속하고 요란하게** 실패하는 것이 최선이다. 방법: (1) **비검사 예외** 발생, (2) 프로그램을 **패닉**(지원 언어), (3) **체크·어서션**(3장). 이 경우 프로그램(또는 복구 불가 범위)이 종료되어 개발자가 문제를 알아차리고, 스택 트레이스로 위치를 파악한다. 복구할 방법이 없으므로 **암시적 기법**이 합리적이다 — 중간 호출자들이 처리 코드를 작성할 필요가 없기 때문이다.

---

## 5. 복구 가능한 오류의 전달: 명시적 vs 암시적 논쟁

호출자가 복구하기를 원할 수 있는 오류에 대해, 비검사 예외를 쓸지 명시적 기법(검사 예외·널·옵셔널·리절트)을 쓸지는 엔지니어·언어 설계자 사이에 합의가 없다.

**비검사 예외를 쓰자는 주장**
- **코드 구조 개선**: 오류 처리가 대개 상위 몇 계층에서만 이뤄지므로, 중간 코드는 오류를 신경 쓸 필요가 없어진다.
- **실용성**: 명시적 오류 전달이 너무 많으면 개발자가 결국 잘못된 일(예외를 잡고 무시, 널 확인 없이 캐스팅)을 한다.

**명시적 기법을 쓰자는 주장**
- **매끄러운 오류 처리**: 오류 시나리오를 호출 측이 알아야 사용자 친화적으로 처리한다.
- **실수로 무시할 수 없다**: 비검사 예외는 "기본적으로 잘못된 일(처리 안 함)"이 일어나기 쉽다. 명시적 기법에서 오류를 무시하려면 **적극적·노골적 위반**이 필요해 코드 리뷰에서 드러난다.

> **핵심 통찰 — 저자의 의견**: 호출자가 복구하기를 원할 수 있는 오류에는 **명시적 기법을 쓰라.** 비검사 예외는 코드베이스 전반에 걸쳐 문서화되는 경우가 드물어, 어떤 오류가 나고 어떻게 처리할지 알기가 거의 불가능하다. 다만 **무엇보다 중요한 것은 팀이 하나의 철학에 합의하는 것**이다 — 팀의 절반은 이 방식, 나머지는 저 방식이면 코드 상호작용이 악몽이 된다.

---

## 6. 컴파일러 경고를 무시하지 말라

컴파일러 경고는 코드가 의심스러우면 표시하는 **버그의 조기 경고**일 수 있다. 예를 들어 `getDisplayName()`이 실수로 `realName`을 반환하면(예제 4.32), 컴파일러는 "`displayName`이 읽히지 않는다"고 경고한다 — 이를 무시하면 개인정보 침해 버그를 놓친다. 경고를 오류로 취급해 컴파일을 막도록 설정하는 것이 유용하며, 정당한 이유가 있으면 `@Suppress("unused")` 같은 것으로 **명시적으로 억제**하되 설명을 남긴다.

---

## 7. 코드 품질 6대 요소 연결

| 6대 요소 | 이 장이 기여하는가? | 근거 |
|---|---|---|
| 예측 가능 | ✅ (핵심) | 오류를 숨기지 않고 명시적으로 전달해 놀라움을 없앤다 |
| 오용 어렵게 | ✅ (핵심) | 명시적 기법은 오류 무시를 컴파일/리뷰 단계에서 드러낸다 |
| 멈추지 않음 | ✅ | 신속·요란한 실패로 버그를 조기에 잡는다 |
| 읽기 쉬움 | (간접) | 리절트/아웃컴 타입은 오류 흐름을 코드에 드러낸다 |
| 테스트 용이 | (간접) | 명시적 오류 타입은 오류 경로를 테스트하기 쉽게 한다 |

> **핵심 통찰**: 오류 전달 기법은 **명시성의 스펙트럼**이다. TS에서는 검사 예외가 없으므로, 호출자가 복구하기를 원할 오류에는 **판별 유니언 리절트 타입**이 가장 명시적이고 타입 안전한 선택이 된다.

---

## 요약

- 오류는 크게 **복구 가능한 오류**와 **복구할 수 없는 오류**로 나뉜다.
- 코드가 낸 오류를 복구할 수 있는지는 **호출하는 쪽만 아는 경우가 많다.**
- 오류가 발생하면 **신속하게 실패**하고, 복구할 수 없으면 **요란하게 실패**하는 것이 좋다.
- **오류를 숨기지 말라** — 기본값 반환·널 객체·예외 억제는 대개 안티패턴이다.
- 오류 전달 기법은 **명시적**(코드 계약의 명확한 부분, 호출 측이 인지)과 **암시적**(세부 조항 또는 없음)으로 나뉜다.
- **복구할 수 없는 오류**에는 암시적 기법(비검사 예외·패닉)을 쓴다.
- **복구 가능한 오류**에는 명시적/암시적 중 합의가 없지만, 저자는 **명시적 기법**을 권한다(TS라면 판별 유니언 리절트). 무엇보다 **팀의 합의**가 중요하다.
- **컴파일러 경고**는 버그의 조기 신호이므로 무시하지 말라.
