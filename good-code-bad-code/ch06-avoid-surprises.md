# Chapter 6: Avoid Surprises (예측 가능한 코드를 작성하라)

## 핵심 질문

코드는 어떻게 개발자의 예측(정신 모델)을 벗어나 동작하게 되는가? 매직값·널 객체 패턴·예상치 못한 부수효과·입력 매개변수 변경·오해를 일으키는 함수는 각각 어떤 버그를 낳는가? 미래에 값이 추가될 열거형은 어떻게 안전하게 처리하는가?

---

## 0. 이 장에서 다루는 것 · 코드 표기 규약

- 코드가 어떻게 예측을 벗어나 작동할 수 있는지
- 예측을 벗어나는 코드가 어떻게 버그로 이어지는지
- 코드가 예측을 벗어나지 않도록 보장하는 방법

개발자는 코드 계약·사전 지식·공통 패러다임에 근거해 **정신 모델(mental model)**을 구축한다. 코드가 실제로 하는 일이 이 모델과 어긋나면, 최선의 경우 시간 낭비, 최악의 경우 치명적 버그가 발생한다. 이 장은 6대 요소 중 **예측 가능성**을 다룬다.

> **코드 표기 규약**: 원서 의사코드를 `<details>`로 접어 두고 아래에 **TypeScript 변환본**을 병기한다. 널 규약(`Type?` → `Type | null`)을 따른다.

---

## 1. 매직값을 반환하지 말아야 한다 (6.1)

**매직값(*magic value*)**은 함수의 정상 반환 타입에 들어맞지만 특별한 의미(예: 값 없음·오류를 나타내는 `-1`)를 갖는 값이다. 정상 반환값으로 오인하기 쉬워 예측을 벗어난다.

예: `User.getAge()`가 나이가 없을 때 몰래 `-1`을 반환하면(세부 조항에만 언급), 이를 모르는 `getMeanAge()`가 `-1`을 합산해 **잘못된 평균**을 낸다 — 단위 테스트도 "나이 있는 User"만 쓰면 못 잡는다.

<details>
<summary>의사코드 (원서) — 예제 6.3 → 6.4 (매직값 → 널 반환)</summary>

```java
// ❌ 매직값: 나이 없으면 -1 (세부 조항에만 있음)
class User {
  private final Int? age;
  // 나이가 주어지지 않은 경우에는 -1을 반환한다.
  Int getAge() {
    if (age == null) { return -1; }
    return age;
  }
}

// ✅ 널 반환: 값이 없을 수 있음이 계약의 명백한 부분이 된다
class User {
  private final Int? age;
  Int? getAge() { return age; }
}
```

</details>

```typescript
// ❌ 매직값: 정상 반환값과 섞여 조용히 버그를 만든다
class User {
  constructor(private readonly age: number | null) {}
  getAge(): number {
    if (this.age === null) { return -1; }
    return this.age;
  }
}

// ✅ 널 반환: 호출 측이 널 처리를 강제당한다(getMeanAge는 컴파일 에러로 버그를 드러냄)
class User {
  constructor(private readonly age: number | null) {}
  getAge(): number | null { return this.age; }
}
```

> **핵심 통찰**: 값이 없을 수 있으면 **널(널 안전성 시)·옵셔널·오류 전달**로 그것을 계약의 **명백한 부분**으로 만들라. 매직값은 의도적으로도, `minValue()`가 빈 리스트에 `Int.MAX_VALUE`를 반환하듯 **우연히도** 생긴다 — 언어별로 다른 `Int.MAX_VALUE`가 클라이언트/DB로 흘러가면 큰 혼란을 부른다.

---

## 2. 널 객체 패턴을 적절히 사용하라 (6.2)

**널 객체 패턴(*null object pattern*)**은 널 대신 "유효해 보이는" 값을 반환해 이후 로직이 널 때문에 깨지지 않게 한다. 하지만 오용하면 예측을 벗어난다.

- **빈 컬렉션 반환은 좋다**(6.2.1): `getClassNames()`가 널 대신 빈 집합을 반환하면 호출 측이 널 확인을 안 해도 되고 간결해진다.
- **빈 문자열은 상황에 따라 문제**(6.2.2): 문자열이 단순 문자 모음이면 빈 문자열 OK. 하지만 **ID처럼 의미를 가지면**(예: `cardTransactionId`가 널=카드 거래 아님), 빈 문자열 반환은 "항상 카드 거래"라는 오해를 낳는다 → 널 반환이 낫다.
- **복잡한 널 객체는 예측을 벗어난다**(6.2.3): 재고가 없을 때 `getRandomMug()`가 크기 0인 머그잔을 반환하면(빈 상자를 파는 것과 같다), 통계 보고서가 조용히 오염된다 → 널 반환이 낫다.
- **널 객체 구현(NullCoffeeMug)**(6.2.4)도 같은 문제를 겪는다.

> **핵심 통찰**: 널 안전성·옵셔널이 보편화되면서 "값 없음"을 쉽고 안전하게 표현할 수 있게 되어, 널 객체 패턴을 지지하던 옛 논거(NullPointerException 회피)는 대부분 설득력을 잃었다. 널 객체 패턴을 쓸 때는 "빈 상자를 받고 호출 측이 놀랄 것인가"를 자문하라.

---

## 3. 예상치 못한 부수효과를 피하라 (6.3)

**부수효과(*side effect*)**는 함수 호출이 함수 외부에 초래한 상태 변화(출력·저장·네트워크·캐시)다. 부수효과 자체는 불가피하지만, **예상되지 않은** 부수효과가 문제다.

- **분명하고 의도적인 부수효과는 괜찮다**(6.3.1): `UserDisplay.displayErrorMessage()`가 캔버스를 그리는 것은 이름으로 명백하다.
- **예상치 못한 부수효과는 문제**(6.3.2): `getPixel()`이 값을 읽기 전에 `canvas.redraw()`를 호출하면 — (a) **비용**(28만 픽셀 스크린샷에 47분 멈춤·깜빡임), (b) **호출자 가정 위반**(개인정보 편집 스크린샷이 redraw로 되살아나 유출), (c) **멀티스레드 버그**(다른 스레드가 redraw 중 읽어 깨진 데이터)를 낳는다.

> **핵심 통찰**: 정보를 얻는 함수는 부수효과가 없다는 것이 자연스러운 정신 모델이다. **해결책은 (a) 애초에 부수효과를 없애거나, (b) 이름으로 분명히 하는 것**이다 — `getPixel()` → `redrawAndGetPixel()`. 이름 하나로 세 문제 모두 완화된다. (불변 객체로 만드는 것도 부수효과를 줄이는 좋은 방법 — 7장.)

---

## 4. 입력 매개변수를 수정하는 것에 주의하라 (6.4)

입력 매개변수를 함수 내에서 변경하는 것은 특수한 부수효과다.

> **비유 — 빌린 책**: 친구에게 빌린 책의 페이지를 찢고 여백에 낙서하면 나쁜 친구다. 객체를 함수에 넘기는 것은 책을 빌려주는 것과 같아서, 호출자는 "빌려준다"고 생각한다. 함수가 그것을 변경하면 버그가 난다.

예: `getBillableInvoices()`가 입력 맵 `userInvoices`에서 무료 체험 사용자를 **삭제**하면, `processOrders()`가 나중에 그 맵을 재사용할 때 무료 체험 사용자가 서비스를 못 쓰게 된다.

<details>
<summary>의사코드 (원서) — 예제 6.24 입력 매개변수를 변경하지 않음 (좋은 예)</summary>

```java
List<Invoice> getBillableInvoices(
    Map<User, Invoice> userInvoices,
    Set<User> usersWithFreeTrial) {
  return userInvoices
      .entries()
      .filter(entry -> !usersWithFreeTrial.contains(entry.getKey()))
      .map(entry -> entry.getValue());   // 원본을 변경하지 않고 새 리스트를 만든다
}
```

</details>

```typescript
function getBillableInvoices(
  userInvoices: Map<User, Invoice>,
  usersWithFreeTrial: Set<User>,
): Invoice[] {
  // 원본 맵을 변경하지 않고 필터링해 새 리스트로 복사
  return [...userInvoices.entries()]
    .filter(([user]) => !usersWithFreeTrial.has(user))
    .map(([, invoice]) => invoice);
}
```

> **핵심 통찰**: 변경이 필요하면 **변경 전에 복사**하라. 성능이 정말 중요해 불가피하게 변경해야 한다면(대량 정렬 등) 이름·문서로 분명히 하라. 반대로 **자신의 객체가 남에 의해 변경되는 것을 막는 것**은 7장의 불변성(immutability)으로 다룬다.

---

## 5. 오해를 일으키는 함수는 작성하지 말라 (6.5)

계약의 명백한 부분(이름)이 **오해의 소지**가 있으면 더 나쁘다. 예: `displayLegalDisclaimer(legalText)`가 `legalText`가 널이면 **아무것도 안 하고 반환**하면, `ensureLegalCompliance()`를 읽는 개발자는 "고지 사항이 항상 표시된다"고 결론짓지만 실제로는 번역이 없을 때 표시되지 않아 **법을 위반**할 수 있다.

> **핵심 통찰**: 매개변수 없이는 함수가 제 일을 못 하는 **중요한 매개변수는 널을 허용하지 말고 필수로 만들라**(6.5.2). 그러면 호출 측이 "번역이 없는 경우"를 처리할 수밖에 없다. 호출 측 코드가 몇 줄 길어지지만(널 확인), 오해로 인한 치명적 버그를 막는 값진 절충이다(5장의 "줄 수에 집착 말라"와 이어진다).

---

## 6. 미래를 대비한 열거형 처리 (6.6)

우리가 **의존하는** 코드(예: 남의 열거형)에 대해 부실한 가정을 하면 우리 코드가 예측을 벗어난다. 열거형은 **나중에 값이 추가될 수 있다**는 점을 기억해야 한다.

예: `PredictedOutcome`이 `COMPANY_WILL_GO_BUST`/`COMPANY_WILL_MAKE_A_PROFIT` 둘뿐일 때, `isOutcomeSafe()`가 "GO_BUST면 false, 나머지는 암묵적으로 true"로 처리하면 — 나중에 `WORLD_WILL_END`가 추가됐는데 함수가 수정되지 않으면 **세계 종말을 "안전"으로 판정**한다.

**해결책: 모든 경우를 명시적으로 처리하고, 처리 안 된 새 값이 오면 컴파일/테스트가 실패하게 한다.**

<details>
<summary>의사코드 (원서) — 예제 6.31 · 6.32 모든 경우를 처리하는 스위치문 + 단위 테스트</summary>

```java
Boolean isOutcomeSafe(PredictedOutcome prediction) {
  switch (prediction) {
    case COMPANY_WILL_GO_BUST:
      return false;
    case COMPANY_WILL_MAKE_A_PROFIT:
      return true;
  }
  // 처리되지 않은 값 → 프로그래밍 오류이므로 비검사 예외로 요란하게 실패
  throw new UncheckedException("Unhandled prediction: " + prediction);
}

// 모든 열것값을 순회하는 테스트 — 처리 안 된 값이 있으면 예외로 실패
testIsOutcomeSafe_allPredictedOutcomeValues() {
  for (PredictedOutcome prediction in PredictedOutcome.values()) {
    isOutcomeSafe(prediction);
  }
}
```

</details>

```typescript
// TS: never를 이용한 '완전성 검사' — 새 값 추가 시 컴파일 에러로 강제
enum PredictedOutcome {
  COMPANY_WILL_GO_BUST,
  COMPANY_WILL_MAKE_A_PROFIT,
}

function isOutcomeSafe(prediction: PredictedOutcome): boolean {
  switch (prediction) {
    case PredictedOutcome.COMPANY_WILL_GO_BUST:
      return false;
    case PredictedOutcome.COMPANY_WILL_MAKE_A_PROFIT:
      return true;
    default: {
      // 모든 case를 처리했다면 prediction은 never 타입.
      // 새 열것값이 추가되면 이 할당에서 컴파일 에러가 난다.
      const exhaustive: never = prediction;
      throw new Error(`Unhandled prediction: ${exhaustive}`);
    }
  }
}
```

> **핵심 통찰**: 원서(자바/C++)는 스위치문 **밖**에 예외를 두고 단위 테스트로 방어한다. **TypeScript에서는 `default`에서 `const _: never = prediction` 할당으로 컴파일 타임에 강제**하는 것이 훨씬 강력하다 — 새 열것값이 추가되는 순간 빌드가 깨진다. 단, **기본(default) 케이스로 새 값을 암묵 처리하지 말라**(6.6.3) — `default: return false`는 새 값을 조용히 "안전 아님"으로 처리해 버그를 부른다(never 검사용 default는 예외).

---

## 7. 이 모든 것을 테스트로 해결할 수는 없는가? (6.7)

테스트는 중요하지만, 예측을 벗어나는 코드를 방어하는 완전한 수단은 아니다. 테스트 작성자 역시 "코드가 무엇을 하는지"에 대한 (틀릴 수 있는) 가정을 갖고 테스트를 쓰기 때문이다(getMeanAge 예처럼 "나이는 항상 있다"고 가정하면 그 버그를 테스트하지 않는다). 예측 가능한 코드를 **먼저** 작성하는 것이 테스트보다 근본적이다.

---

## 8. 코드 품질 6대 요소 연결

이 장은 6대 요소 중 **예측 가능성**을 정면으로 다룬다.

| 6대 요소 | 이 장이 기여하는가? | 근거 |
|---|---|---|
| 예측 가능 | ✅ (직접) | 매직값·부수효과·오해 유발 함수 제거 |
| 오용 어렵게 | (부수) | 중요 매개변수 필수화·enum 완전성 검사 |
| 멈추지 않음 | (부수) | 열거형 새 값에 요란하게 실패 |
| 읽기 쉬움 | (부수) | 부수효과를 이름으로 드러냄(`redrawAndGetPixel`) |

> **핵심 통찰**: 예측 가능성의 핵심은 **코드가 하는 일을 계약의 "명백한 부분"으로 드러내는 것**이다. 매직값 대신 널/리절트(4장), 부수효과는 이름으로, 열거형은 완전성 검사로 — 모두 "정신 모델과 실제 동작을 일치"시키는 기법이다.

---

## 요약

- **매직값을 반환하지 말라** — 널·옵셔널·오류로 "값 없음"을 명시적으로 드러낸다.
- **널 객체 패턴은 신중히** — 빈 컬렉션은 대개 좋지만, 의미 있는 문자열·복잡한 객체는 예측을 벗어날 수 있다.
- **예상치 못한 부수효과를 피하라** — 없애거나, 피할 수 없으면 이름으로 분명히 한다.
- **입력 매개변수를 변경하지 말라** — 변경 전에 복사한다.
- **오해를 일으키는 함수를 쓰지 말라** — 중요한 매개변수는 필수로 만든다.
- **미래를 대비해 열거형을 처리하라** — 모든 값을 명시적으로 처리하고, 새 값이 오면 실패하게 한다(TS는 `never` 완전성 검사). 기본 케이스로 암묵 처리하지 말라.
- 테스트만으로는 부족하다 — 예측 가능한 코드를 먼저 작성하는 것이 근본이다.
