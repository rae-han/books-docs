# Chapter 11: Unit Testing Practices (단위 테스트의 실제)

## 핵심 질문

왜 함수당 테스트 하나로는 부족하며 무엇을 테스트해야 하는가? 프라이빗 함수를 테스트하려고 퍼블릭으로 바꾸면 왜 안 되는가? 한 테스트 케이스가 여러 동작을 테스트하면 어떤 문제가 생기는가? 테스트 간 상태·설정 공유는 왜 위험한가? 어떤 어서션 확인자가 좋은가? 의존성 주입은 어떻게 테스트를 가능하게 하는가?

---

## 0. 이 장에서 다루는 것 · 코드 표기 규약

- 코드의 모든 동작을 효과적·신뢰성 있게 테스트하기
- 이해하기 쉽고 실패가 잘 설명되는 테스트 코드 작성
- 의존성 주입으로 테스트하기 쉬운 코드 작성

10장의 원칙(정확한 훼손 감지 / 구현 세부 독립 / 잘 설명되는 실패 / 이해 가능한 코드 / 빠른 실행)을 **실전 기법**으로 옮기는 장이다. 이 특징들은 저절로 얻어지지 않으므로, 이를 극대화하는 구체적 방법을 다룬다.

> **코드 표기 규약**: 원서 의사코드를 `<details>`로 접어 두고 아래에 **TypeScript 변환본**을 병기한다. 테스트 코드는 프레임워크 중립적 형태(`assertThat`·`assertThrows` 등)로 표기한다.

---

## 1. 기능뿐만 아니라 동작을 시험하라 (11.1)

개발자가 흔히 저지르는 실수는 **함수 이름만** 테스트 목록에 넣는 것이다(함수 2개 → 테스트 2개). 하지만 한 함수는 여러 동작을 하고, 한 동작이 여러 함수에 걸치기도 한다. `MortgageAssessor.assess()`(주택담보대출 평가)를 테스트 케이스 하나로만 검증하면, "승인" 경로만 보고 "거절" 경로(신용등급 나쁨·기존 대출·금지 고객)를 놓친다 — 금지된 고객에게 대출을 승인하도록 코드를 바꿔도 테스트는 통과한다.

<details>
<summary>의사코드 (원서) — 예제 11.1 MortgageAssessor: 여러 동작을 담은 함수</summary>

```java
class MortgageAssessor {
  MortgageDecision assess(Customer customer) {
    if (!isEligibleForMortgage(customer)) {
      return MortgageDecision.rejected();
    }
    return MortgageDecision.approve(getMaxLoanAmount(customer));
  }
  private static Boolean isEligibleForMortgage(Customer customer) {
    return customer.hasGoodCreditRating() &&
        !customer.hasExistingMortgage() && !customer.isBanned();
  }
  private static MonetaryAmount getMaxLoanAmount(Customer customer) {
    return customer.getIncome().minus(customer.getOutgoings()).multiplyBy(10.0);
  }
}
```

</details>

**해결책 — 함수가 아니라 각 동작을 테스트하라.** `MortgageAssessor`가 보이는 중요한 동작(각 거절 사유, 최대 대출액 계산, 소득<지출 같은 경계값, 오류 시나리오)마다 테스트 케이스를 둔다. 실제 코드 100줄에 테스트 300줄은 흔하며, **테스트 코드가 실제 코드보다 적으면** 동작이 충분히 테스트되지 않았다는 경고다.

<details>
<summary>의사코드 (원서) — 예제 11.4 오류 시나리오도 중요한 동작 (테스트 필수)</summary>

```java
// debit()이 음수에 ArgumentException을 던지는 것은 중요한 동작 → 테스트한다
void testDebit_negativeAmount_throwsArgumentException() {
  MonetaryAmount negativeAmount = new MonetaryAmount(-0.01, Currency.USD);
  BankAccount bankAccount = new BankAccount();
  ArgumentException exception = assertThrows(
      ArgumentException,
      () -> bankAccount.debit(negativeAmount));
  assertThat(exception.getMessage()).isEqualTo("액수는 0보다 적을 수 없음");
}
```

</details>

```typescript
// 오류 시나리오도 중요한 동작이므로 반드시 테스트한다
test("debit — 음수 금액이면 예외를 던진다", () => {
  const negativeAmount = new MonetaryAmount(-0.01, Currency.USD);
  const bankAccount = new BankAccount();
  expect(() => bankAccount.debit(negativeAmount)).toThrow("액수는 0보다 적을 수 없음");
});
```

> **핵심 통찰**: 모든 동작이 테스트되는지 확인하는 좋은 질문 — "이 코드 줄을 지워도(또는 `if`를 반대로, `&&`를 `||`로, 상수를 바꿔도) 테스트가 통과하는가?" **예**라면 그 동작은 테스트되지 않는 것이다. 이를 자동화한 것이 **돌연변이 테스트(*mutation test*)**다(코드를 약간 변형해 테스트가 여전히 통과하면 경고). 단, 방어적 어서션은 예외 — 깨뜨려야만 테스트할 수 있어 테스트가 불가능할 수 있다.

---

## 2. 테스트만을 위해 퍼블릭으로 만들지 말라 (11.2)

프라이빗 함수는 구현 세부사항이다. 이를 테스트하려고 `isEligibleForMortgage()`를 퍼블릭으로 바꾸는 것("테스트를 위해서만 공개" 주석과 함께)은 나쁜 생각이다.

<details>
<summary>의사코드 (원서) — 예제 11.7 프라이빗 함수를 직접 테스트 (나쁜 예)</summary>

```java
// ❌ 나쁜 예: 프라이빗이어야 할 함수를 퍼블릭으로 만들어 직접 테스트
testIsEligibleForMortgage_badCreditRating_ineligible() {
  Customer customer = new Customer(..., hasGoodCreditRating: false, ...);
  assertThat(MortgageAssessor.isEligibleForMortgage(customer)).isFalse();
}
```

</details>

이 방식의 문제는 세 가지다. (1) **실제로 신경 쓰는 동작을 테스트하지 않는다** — "신용등급이 나쁘면 대출이 거절된다"가 아니라 "함수가 false를 반환한다"만 확인하므로, `assess()`가 그 함수를 잘못 호출해도 통과한다. (2) **구현 세부사항과 결합** — 함수 이름 변경·헬퍼 클래스 이동 같은 리팩터링에 테스트가 깨진다. (3) **퍼블릭 API를 넓힌다** — "테스트용" 주석은 간과되기 쉬워 다른 코드가 의존하게 된다.

**해결책 1 — 퍼블릭 API로 테스트하라.** 실제로 중요한 동작("신용등급 나쁨 → 거절")을 `assess()`를 통해 검증한다.

<details>
<summary>의사코드 (원서) — 예제 11.8 퍼블릭 API를 통한 테스트 (좋은 예)</summary>

```java
// ✅ 좋은 예: 퍼블릭 API(assess)를 통해 실제 중요한 동작을 테스트
testAssess_badCreditRating_mortgageRejected() {
  Customer customer = new Customer(..., hasGoodCreditRating: false, ...);
  MortgageDecision decision = new MortgageAssessor().assess(customer);
  assertThat(decision.isApproved()).isFalse();
}
```

</details>

**해결책 2 — 코드를 더 작은 단위로 분할하라.** 프라이빗 함수가 복잡해(예: 외부 `CreditScoreService` 호출·오류 처리) 퍼블릭 API로 테스트하기 어렵다면, 그 진짜 원인은 **클래스가 너무 많은 일을 한다**는 것이다. 신용등급 판정 로직을 `CreditRatingChecker` 클래스로 분리하면, 각 클래스를 **자신의 퍼블릭 API로** 쉽게 테스트할 수 있다.

<details>
<summary>의사코드 (원서) — 예제 11.10 두 클래스로 분할 (좋은 예)</summary>

```java
// 신용등급 판정을 별도 클래스로 분리 → 각자의 퍼블릭 API로 테스트 가능
class CreditRatingChecker {
  private final CreditScoreService creditScoreService;
  Result<Boolean, Error> isCreditRatingGood(Int customerId) {
    CreditScoreResponse response = creditScoreService.query(customerId);
    if (response.errorOccurred()) { return Result.ofError(response.getError()); }
    return Result.ofValue(response.getCreditScore() >= GOOD_CREDIT_SCORE_THRESHOLD);
  }
}
class MortgageAssessor {
  private final CreditRatingChecker creditRatingChecker;   // 의존성 주입
  // ... assess()는 훨씬 단순해진다
}
```

</details>

> **핵심 통찰**: 테스트를 위해 프라이빗 함수를 퍼블릭으로 만드는 것은 **경고 신호**다 — 실제 중요한 동작을 테스트하지 않거나 클래스가 너무 크다는 뜻이다. 실용성도 잊지 말라: 퍼블릭 API의 정의는 해석의 여지가 있고, 일부 중요한 동작(부수 효과)은 그 밖에 있을 수 있다(10.3). 중요한 동작이면 퍼블릭 API 여부와 무관하게 테스트한다.

---

## 3. 한 번에 하나의 동작만 테스트하라 (11.3)

여러 동작을 한 테스트 케이스에 몰아넣을 수 있어도 그래선 안 된다. `getValidCoupons()`(유효 쿠폰 필터링)의 모든 동작(사용됨·만료·타인 발행 제외, 내림차순 정렬)을 `testGetValidCoupons_allBehaviors` 하나로 테스트하면, (1) 테스트 코드가 길고 이해하기 어렵고, (2) 실패 시 **어떤 동작이 깨졌는지** 알 수 없다.

<details>
<summary>의사코드 (원서) — 예제 11.13 각 동작을 개별 테스트 케이스로 (좋은 예)</summary>

```java
// ✅ 좋은 예: 각 동작을 서술적 이름의 개별 테스트 케이스로 분리
void testGetValidCoupons_validCoupon_included() {
  Customer customer = new Customer("test customer");
  Coupon valid = new Coupon(alreadyRedeemed: false, hasExpired: false,
      issuedTo: customer, value: 100);
  assertThat(getValidCoupons([valid], customer)).containsExactly(valid);
}
void testGetValidCoupons_alreadyRedeemed_excluded() {
  Customer customer = new Customer("test customer");
  Coupon redeemed = new Coupon(alreadyRedeemed: true, hasExpired: false,
      issuedTo: customer, value: 100);
  assertThat(getValidCoupons([redeemed], customer)).isEmpty();
}
// testGetValidCoupons_expired_excluded(), ..._returnedInDescendingValueOrder() ...
```

</details>

```typescript
// ✅ 좋은 예: 동작마다 별도 테스트 케이스 — 실패 시 이름만 봐도 무엇이 깨졌는지 안다
test("getValidCoupons — 유효한 쿠폰은 포함된다", () => {
  const customer = new Customer("test customer");
  const valid = new Coupon({ alreadyRedeemed: false, hasExpired: false, issuedTo: customer, value: 100 });
  expect(getValidCoupons([valid], customer)).toEqual([valid]);
});
test("getValidCoupons — 이미 사용된 쿠폰은 제외된다", () => {
  const customer = new Customer("test customer");
  const redeemed = new Coupon({ alreadyRedeemed: true, hasExpired: false, issuedTo: customer, value: 100 });
  expect(getValidCoupons([redeemed], customer)).toEqual([]);
});
```

동작마다 케이스를 나누면 코드 중복이 늘 수 있는데, **매개변수화된 테스트(parameterized test)**로 줄일 수 있다. 하나의 테스트 함수에 여러 입력 세트를 주되, 각 세트에 이름을 붙여 실패 메시지가 잘 설명되게 한다.

<details>
<summary>의사코드 (원서) — 예제 11.14 매개변수화된 테스트</summary>

```java
[TestCase(true, false, TestName = "이미 사용함")]
[TestCase(false, true, TestName = "유효기간 만료")]
void testGetValidCoupons_excludesInvalidCoupons(Boolean alreadyRedeemed, Boolean hasExpired) {
  Customer customer = new Customer("test customer");
  Coupon coupon = new Coupon(alreadyRedeemed: alreadyRedeemed,
      hasExpired: hasExpired, issuedTo: customer, value: 100);
  assertThat(getValidCoupons([coupon], customer)).isEmpty();
}
```

</details>

> **핵심 통찰**: 한 번에 여러 동작을 테스트하면 "무언가 변경됐다"만 알려주고 "무엇이 변경됐는지"는 알려주지 않는다. 동작마다 **서술적 이름의 개별 케이스**로 나누면 실패가 잘 설명되고, 한 동작을 의도적으로 바꿀 때 무관한 동작이 영향받지 않았는지 확인하기 쉽다.

---

## 4. 공유 설정을 적절하게 사용하라 (11.4)

많은 테스트 프레임워크는 설정을 공유하는 훅을 제공한다 — **BeforeAll/AfterAll**(전체 전후 1회), **BeforeEach/AfterEach**(각 케이스 전후 매번). 이를 잘못 쓰면 테스트가 무력해진다.

**① 가변 상태 공유는 위험하다.** `Database` 인스턴스를 `BeforeAll`에서 만들어 공유하면, 앞 테스트가 DB에 남긴 상태 때문에 **뒤 테스트가 버그를 놓친다**(코드가 지연 표시에 실패해도, 앞 테스트가 이미 DELAYED로 저장해 통과). **해결책**: 상태를 공유하지 않거나(케이스마다 새 인스턴스, 페이크 사용), 불가피하면 `AfterEach`에서 **초기화**한다.

<details>
<summary>의사코드 (원서) — 예제 11.17 AfterEach로 테스트 간 상태 초기화</summary>

```java
class OrderManagerTest {
  private Database database;
  @BeforeAll void oneTimeSetUp() { database = Database.createInstance(); database.waitForReady(); }
  @AfterEach void tearDown() { database.reset(); }   // 각 케이스 후 초기화 → 서로 영향 없음
  void testProcessOrder_outOfStockItem_orderDelayed() { ... }
  void testProcessOrder_paymentNotComplete_orderDelayed() { ... }
}
```

</details>

**② 중요한 설정 공유도 위험하다.** `BeforeEach`에서 "항목 3개짜리 주문"을 만들어 공유하면, 나중에 누군가 "위험물 테스트"를 위해 그 공유 주문에 4번째 항목을 추가하는 순간, "정확히 3개일 때 대형 박스" 테스트가 **의도와 다른 4개를 테스트**하게 된다. **해결책**: 테스트 결과에 **직접 영향을 주는 설정은 각 케이스 안에서** 정의한다(중복은 헬퍼 함수로 줄인다).

<details>
<summary>의사코드 (원서) — 예제 11.22 중요한 설정은 케이스 안에서 (헬퍼 함수 활용)</summary>

```java
// ✅ 좋은 예: 결과에 영향을 주는 항목은 각 케이스 안에서 명시적으로 설정
class OrderPostageManagerTest {
  void testGetPostageLabel_threeItems_largePackage() {
    Order order = createOrderWithItems([  // 이 케이스가 의존하는 "3개"가 눈앞에 있음
        new Item("Test item 1"), new Item("Test item 2"), new Item("Test item 3")]);
    PostageLabel label = new PostageManager().getPostageLabel(order);
    assertThat(label.isLargePackage()).isTrue();
  }
  // 중복을 줄이는 헬퍼 (결과에 영향 없는 부분만 채운다)
  private static Order createOrderWithItems(List<Item> items) {
    return new Order(customer: new Customer(address: new Address("Test address")), items: items);
  }
}
```

</details>

**③ 공유가 적절한 경우도 있다.** 인스턴스 생성에 **반드시 필요하지만 테스트 결과와 무관한** 설정(예: `OrderMetadata`)은 공유 상수로 한 번만 정의하는 것이 타당하다.

> **핵심 통찰**: 공유 설정은 양날의 검이다 — 반복·비용을 줄이지만 테스트를 무력화·불투명하게 만들 수 있다. 판단 기준은 "**이 설정이 테스트 결과에 직접 영향을 주는가**"다. 그렇다면 케이스 안에서, 아니라면 공유해도 된다. 공유 상수는 반드시 **불변 타입**으로(가변 상태 공유는 ①의 문제).

---

## 5. 적절한 어서션 확인자를 사용하라 (11.5)

**어서션 확인자(*assertion matcher*)**는 테스트 통과 여부를 결정하는 코드다. `getClassNames()`(순서 없는 CSS 클래스 목록 반환)가 "사용자 지정 클래스를 포함하는지"를 테스트할 때, 확인자 선택이 중요하다.

- `isEqualTo([전체 목록])` — **과도하게 제한적**. 표준 클래스까지 테스트하고, 순서가 바뀌면(순서 무관인데도) 실패한다.
- `contains(...).isTrue()` — **실패 설명이 부실**. "true를 기대했지만 false"만 나온다.
- `containsAtLeast(...)` — **적절**. 순서와 무관하게 지정 항목 포함만 확인하고, 실패 시 "빠진 항목: custom_class_1"처럼 명확히 설명한다.

<details>
<summary>의사코드 (원서) — 예제 11.27 적절한 확인자 사용 (좋은 예)</summary>

```java
// ✅ 좋은 예: containsAtLeast — 의도한 것만 테스트하고, 실패가 잘 설명된다
testGetClassNames_containsCustomClassNames() {
  TextWidget textWidget = new TextWidget(["custom_class_1", "custom_class_2"]);
  assertThat(textWidget.getClassNames())
      .containsAtLeast("custom_class_1", "custom_class_2");
}
```

</details>

```typescript
// ✅ 좋은 예: 순서 무관하게 "포함"만 확인 (jest의 arrayContaining 등)
test("getClassNames — 사용자 지정 클래스를 포함한다", () => {
  const textWidget = new TextWidget(["custom_class_1", "custom_class_2"]);
  expect(textWidget.getClassNames()).toEqual(
    expect.arrayContaining(["custom_class_1", "custom_class_2"]),
  );
});
```

> **핵심 통찰**: `assertThat(list).contains(x)`가 `assertThat(list.contains(x)).isTrue()`보다 자연스러운 문장에 가깝고, 실패 메시지도 훨씬 낫다. "코드가 잘못되면 실패해야 한다"뿐 아니라 "**어떻게 실패할지**"까지 고려해 확인자를 고르라.

---

## 6. 테스트 용이성을 위해 의존성 주입을 사용하라 (11.6)

하드코드된 의존성은 테스트를 아예 불가능하게 만든다. `InvoiceReminder`가 생성자에서 `DataStore.getAddressBook()`과 `new EmailSenderImpl()`을 직접 생성하면, 테스트가 실제 DB에 접근하고 실제 이메일을 보내게 되어 테스트 더블로 대체할 수 없다.

<details>
<summary>의사코드 (원서) — 예제 11.28 → 11.29 (하드코드 의존성 → DI)</summary>

```java
// ❌ 나쁜 예: 생성자에서 의존성을 직접 생성 → 테스트 더블로 교체 불가
class InvoiceReminder {
  private final AddressBook addressBook;
  private final EmailSender emailSender;
  InvoiceReminder() {
    this.addressBook = DataStore.getAddressBook();   // 실제 DB
    this.emailSender = new EmailSenderImpl();         // 실제 이메일 발송!
  }
}

// ✅ 좋은 예: 의존성 주입 + 정적 팩토리 함수
class InvoiceReminder {
  private final AddressBook addressBook;
  private final EmailSender emailSender;
  InvoiceReminder(AddressBook addressBook, EmailSender emailSender) {  // 주입
    this.addressBook = addressBook;
    this.emailSender = emailSender;
  }
  static InvoiceReminder create() {   // 실사용자는 의존성 걱정 없이 생성
    return new InvoiceReminder(DataStore.getAddressBook(), new EmailSenderImpl());
  }
}
```

</details>

```typescript
// ✅ 좋은 예: 의존성 주입 → 테스트에서 페이크로 교체 가능
class InvoiceReminder {
  constructor(
    private readonly addressBook: AddressBook,
    private readonly emailSender: EmailSender,
  ) {}

  static create(): InvoiceReminder {
    // 실사용자는 의존성 걱정 없이 생성
    return new InvoiceReminder(DataStore.getAddressBook(), new EmailSenderImpl());
  }

  sendReminder(invoice: Invoice): boolean {
    const address = this.addressBook.lookupEmailAddress(invoice.getCustomerId());
    if (address === null) {
      return false;
    }
    return this.emailSender.send(address, InvoiceReminderTemplate.generate(invoice));
  }
}

// 테스트: 페이크를 주입해 실제 DB·이메일 없이 모든 동작을 테스트
const addressBook = new FakeAddressBook();
addressBook.addEntry(123456, "test@example.com");
const emailSender = new FakeEmailSender();
const invoiceReminder = new InvoiceReminder(addressBook, emailSender);
```

> **핵심 통찰**: 테스트 용이성은 **모듈화와 밀접**하다(1장). 코드가 느슨하게 결합되고 재설정 가능하면 테스트가 쉬워진다. **의존성 주입**(8장)은 코드를 모듈화하는 기술이자, 동시에 테스트 용이성을 높이는 핵심 기술이다.

---

## 7. 테스트에 대한 몇 가지 결론 (11.7)

단위 테스트는 빙산의 일각이다. 알아 둘 다른 **수준**과 **유형**은 다음과 같다.

- **통합 테스트(*integration test*)**: 여러 구성 요소·모듈을 연결(통합)한 것이 제대로 작동하는지 확인.
- **종단 간 테스트(*end-to-end test*, E2E)**: 처음부터 끝까지 전체 시스템을 통과하는 여정을 테스트(예: 브라우저를 구동해 구매 완료까지).
- **회귀 테스트**: 동작·기능이 나쁘게 변하지 않았는지 정기적으로 확인.
- **골든 테스트(*golden/characterization test*)**: 입력에 대한 출력 스냅숏을 저장해 비교(변경 없음 확인엔 유용하나 취약·설명 부족).
- **퍼즈 테스트(*fuzz test*)**: 무작위·흥미로운 값으로 호출해 아무것도 코드를 멈추지 않는지 점검(3장).

> **핵심 통찰**: 단위 테스트가 가장 흔하지만 그것만으로 모든 테스트 요구를 충족할 수 없다. 높은 품질의 소프트웨어를 유지하려면 여러 테스트 수준·유형을 **혼용**해야 한다.

---

## 8. 코드 품질 6대 요소 연결

이 장의 기법은 **테스트 용이성**을 실현하며, 그 실현은 다시 모듈화·가독성과 맞물린다.

| 기법 | 관련 원칙·요소 |
|---|---|
| 동작 중심 테스트 (11.1) | 정확한 훼손 감지 (10.2) |
| 프라이빗 노출 금지 (11.2) | 구현 세부 독립 + 모듈화(작은 단위로 분할) |
| 하나씩·매개변수화 (11.3) | 잘 설명되는 실패 + 이해 가능한 코드 |
| 공유 설정 신중히 (11.4) | 정확한 훼손 감지 + 이해 가능한 코드 |
| 적절한 확인자 (11.5) | 잘 설명되는 실패 |
| DI로 테스트 (11.6) | **모듈화**가 곧 테스트 용이성 |

> **핵심 통찰**: 이 장의 밑바탕은 두 가지다 — **"결과적으로 중요한 동작을 테스트하라"**(구현 세부사항이 아니라)와 **"모듈화가 테스트 용이성을 만든다"**. 프라이빗을 못 테스트해서 답답하거나 설정이 복잡해 괴롭다면, 그것은 테스트의 문제가 아니라 **설계(모듈화)의 신호**다.

---

## 요약

- **함수가 아니라 동작을 테스트하라** — 함수당 테스트 하나로는 부족하다. 오류 시나리오도 중요한 동작이다.
- **테스트를 위해 프라이빗을 퍼블릭으로 만들지 말라** — 퍼블릭 API로 테스트하거나, 어려우면 클래스를 더 작은 단위로 분할하라.
- **한 번에 하나의 동작만** 테스트하라 — 서술적 이름의 개별 케이스(중복은 매개변수화로 축소).
- **공유 설정은 신중히** — 결과에 직접 영향을 주는 설정은 케이스 안에서, 무관한 설정만 공유한다. 가변 상태 공유는 피하거나 초기화하라.
- **적절한 어서션 확인자**를 골라 실패가 잘 설명되게 하라(`containsAtLeast` 등).
- **의존성 주입**으로 테스트 용이성을 확보하라 — 테스트 용이성은 모듈화의 부산물이다.
- 단위 테스트 외에 통합·E2E·회귀·골든·퍼즈 테스트를 **혼용**하라.
