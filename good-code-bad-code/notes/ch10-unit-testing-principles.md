# Chapter 10: Unit Testing Principles (단위 테스트의 원칙)

## 핵심 질문

단위 테스트란 무엇이며 어떤 용어로 구성되는가? 좋은 단위 테스트가 갖춰야 할 특징은 무엇인가? 테스트는 왜 구현 세부사항이 아니라 동작에 집중해야 하는가? 테스트 더블(목·스텁·페이크)은 각각 무엇이고 언제 쓰는가? 목·스텁은 왜 위험하며 페이크가 더 나은 이유는 무엇인가?

---

## 0. 이 장에서 다루는 것 · 코드 표기 규약

- 단위 테스트의 기본 개념과 용어
- 좋은 단위 테스트가 되기 위한 다섯 가지 조건
- 테스트 더블 — 목·스텁·페이크
- 테스트 철학 — TDD·BDD·ATDD

**단위 테스트(*unit test*)**는 코드의 구별되는 단위(보통 클래스·함수)를 상대적으로 격리된 방식으로 테스트한다. 테스트는 코드를 작성한 뒤 얹는 장식이 아니라 **작성의 모든 단계에서** 고려해야 할 사항이며, 심지어 코드보다 먼저 작성하자는 주장(TDD)도 있다. 이 장은 6대 요소 중 **테스트 용이성**의 원칙을 다루고, 11장은 실전 기법을 다룬다.

> **코드 표기 규약**: 원서 의사코드를 `<details>`로 접어 두고 아래에 **TypeScript 변환본**을 병기한다. 테스트 코드는 이해를 돕기 위해 프레임워크 중립적 형태(`assertThat`·`createMock` 등)로 표기한다.

---

## 1. 단위 테스트 기초 (10.1)

단위 테스트를 이해하려면 다음 용어를 알아야 한다.

- **테스트 대상 코드(*code under test*)**: '실제 코드' — 테스트의 대상이 되는 코드.
- **테스트 코드(*test code*)**: 단위 테스트를 구성하는 코드. 보통 실제 코드와 일대일 매핑된다(`GuestList` → `GuestListTest`).
- **테스트 케이스(*test case*)**: 특정 동작·시나리오 하나를 테스트하는 함수. 보통 세 부분으로 나뉜다 — **준비(arrange)**(값·의존성 설정), **실행(act)**(테스트 대상 호출), **단언(assert)**(결과 확인).
- **테스트 러너(*test runner*)**: 테스트를 실제로 실행하고 통과·실패를 출력하는 도구.

<details>
<summary>의사코드 (원서) — 준비·실행·단언 세 부분으로 나뉜 테스트 케이스</summary>

```java
void testGetAllGuests_vipGuestsOnly() {
  // 준비(arrange)
  Guest guest1 = new Guest("Test person 1");
  Guest guest2 = new Guest("Test person 2");
  GuestList guestList = new GuestList();
  guestList.addVipGuest(guest1);
  guestList.addVipGuest(guest2);
  // 실행(act)
  List<Guest> result = guestList.getAllGuests();
  // 단언(assert)
  assertThat(result).containsExactly(guest1, guest2);
}
```

</details>

```typescript
test("getAllGuests — VIP 게스트만", () => {
  // 준비(arrange)
  const guest1 = new Guest("Test person 1");
  const guest2 = new Guest("Test person 2");
  const guestList = new GuestList();
  guestList.addVipGuest(guest1);
  guestList.addVipGuest(guest2);
  // 실행(act)
  const result = guestList.getAllGuests();
  // 단언(assert)
  expect(result).toEqual([guest1, guest2]);
});
```

> **핵심 통찰**: 준비·실행·단언 대신 **주어진(given)·때(when)·그리고 나면(then)**이라는 용어를 선호하는 개발자도 있다. 테스트 철학에 따라 뉘앙스가 다르지만 코드 맥락에서는 같은 의미다.

---

## 2. 좋은 단위 테스트의 다섯 가지 특징 (10.2)

테스트가 있다고 다 좋은 것은 아니다. 좋은 단위 테스트는 다섯 가지 특징을 갖는다.

1. **훼손의 정확한 감지**: 코드가 훼손되면 테스트가 실패하고, **훼손된 경우에만** 실패해야 한다. 코드 변경으로 잘 돌아가던 기능이 깨지는 것을 **회귀(*regression*)**, 이를 탐지하는 테스트를 회귀 테스트라 한다. 코드는 정상인데 무작위성·타이밍·외부 시스템 때문에 때때로 실패하는 테스트를 **플래키(*flaky*)** 테스트라 하는데, '양치기 소년'처럼 결국 아무도 실패를 신뢰하지 않게 만들어 테스트가 없는 것과 같아진다.
2. **구현 세부사항에 독립적**: 구현 세부사항을 바꿔도(리팩터링) 테스트 코드는 그대로여야 한다.
3. **잘 설명되는 실패**: 실패 시 무엇이 왜 잘못됐는지 명확히 알려줘야 한다.
4. **이해할 수 있는 테스트 코드**: 다른 개발자가 무엇을 어떻게 테스트하는지 이해할 수 있어야 한다(테스트는 사용 설명서 역할도 한다).
5. **쉽고 빠른 실행**: 느린 테스트는 개발 속도를 떨어뜨리고 테스트를 기피하게 만든다.

**② 구현 세부사항 독립성**이 왜 중요한지가 이 장의 핵심이다. 리팩터링 전 테스트를 두 방식으로 작성할 수 있다.

- **접근 A**: 동작뿐 아니라 프라이빗 함수·멤버 변수 같은 **구현 세부사항까지** 테스트. → 올바르게 리팩터링해도 테스트가 깨져, 코드가 잘못됐는지 테스트가 낡은 건지 구분하기 어렵다.
- **접근 B**: **동작만** 테스트하고 구현 세부사항은 건드리지 않음. → 올바른 리팩터링이면 테스트는 그대로 통과하고, 실패하면 리팩터링이 동작을 바꿨다는 뜻이다.

> **핵심 통찰**: 성숙한 코드베이스에서는 리팩터링 양이 새 코드보다 많을 수 있다. 테스트가 구현 세부사항에 의존하지 않아야 리팩터링을 안심하고 할 수 있다. 또한 **기능 변경과 리팩터링을 동시에 하지 말라** — 예상된 동작 변화와 실수로 인한 동작 변화를 구분하기 어려워진다. 잘 설명되는 실패를 위해서는 **한 테스트 케이스가 한 가지만** 검사하고 **서술적인 이름**을 붙이는 것이 좋다.

---

## 3. 퍼블릭 API에 집중하되 중요한 동작은 무시하지 말라 (10.3)

구현 세부사항 테스트를 피하려면 **퍼블릭 API만 사용해** 테스트해야 한다. `calculateKineticEnergy(massKg, speedMs)`를 테스트할 때, 내부에서 `Math.pow()`를 호출하는지가 아니라 **주어진 입력에 기대한 값을 반환하는지**만 확인한다(`Math.pow(x,2)`를 `x*x`로 바꿔도 동작은 같으므로).

<details>
<summary>의사코드 (원서) — 퍼블릭 API(반환값)에 집중한 테스트</summary>

```java
Double calculateKineticEnergyJ(Double massKg, Double speedMs) {
  return 0.5 * massKg * Math.pow(speedMs, 2.0);   // Math.pow는 구현 세부사항
}

void testCalculateKineticEnergy_correctValueReturned() {
  // 반환값이 double이므로 정확한 일치 대신 범위로 확인
  assertThat(calculateKineticEnergyJ(3.0, 7.0)).isWithin(1.0e-10).of(73.5);
}
```

</details>

```typescript
function calculateKineticEnergyJ(massKg: number, speedMs: number): number {
  return 0.5 * massKg * Math.pow(speedMs, 2.0); // Math.pow 호출은 구현 세부사항
}

test("운동 에너지 — 올바른 값 반환", () => {
  // 부동소수라 정확한 일치가 아니라 허용 오차로 확인
  expect(calculateKineticEnergyJ(3.0, 7.0)).toBeCloseTo(73.5, 10);
});
```

하지만 "퍼블릭 API만 테스트"를 **중요한 동작을 방치하는 핑계**로 쓰면 안 된다. 커피 자판기 비유: 고객 관점의 퍼블릭 API(카드 대기 → 커피 선택 → 커피 제공)만으로는 완전히 테스트할 수 없다. 테스트는 (1) 전원·물·원두 같은 **퍼블릭 API가 아닌 의존성을 설정**해야 하고, (2) "원두가 떨어지면 담당자에게 알림" 같은 **퍼블릭 API 밖의 중요한 부수 효과를 검증**해야 한다. 반면 물을 데우는 방식(열전 차단기 vs 보일러)은 명백한 구현 세부사항이라 테스트하지 않는다.

<details>
<summary>의사코드 (원서) — 예제 10.1 AddressBook: 캐싱은 구현 세부사항이지만 "서버 재호출 안 함"은 중요한 동작</summary>

```java
class AddressBook {
  private final ServerEndPoint server;
  private final Map<Int, String> emailAddressCache;  // 캐싱 = 구현 세부사항

  String? lookupEmailAddress(Int userId) {           // 퍼블릭 API
    String? cachedEmail = emailAddressCache.get(userId);
    if (cachedEmail != null) { return cachedEmail; }
    return fetchAndCacheEmailAddress(userId);
  }
  private String? fetchAndCacheEmailAddress(Int userId) {
    String? fetchedEmail = server.fetchEmailAddress(userId);
    if (fetchedEmail != null) { emailAddressCache.put(userId, fetchedEmail); }
    return fetchedEmail;
  }
}
// 테스트해야 할 중요한 동작: 같은 ID로 반복 호출 시 서버를 다시 호출하지 않는다
// → 이는 퍼블릭 API 밖에 있지만(캐시는 세부사항) 서버 과부하 방지를 위해 반드시 테스트
```

</details>

> **핵심 통찰**: "퍼블릭 API만 테스트하라"·"구현 세부사항을 테스트하지 말라"는 훌륭한 **지침**이지만, 무엇이 퍼블릭 API·구현 세부사항인지는 **주관적·상황 의존적**이다. 궁극적으로 중요한 것은 **모든 중요한 동작을 제대로 테스트**하는 것이며, 다른 대안이 없을 때만 퍼블릭 API 밖으로 나가 테스트한다.

---

## 4. 테스트 더블 (10.4)

의존성을 테스트에서 실제로 쓰는 것이 항상 가능·바람직하지는 않다. 대안이 **테스트 더블(*test double*)** — 의존성을 시뮬레이션하는 객체다. 쓰는 이유는 세 가지다.

1. **테스트 단순화**: 설정이 복잡하거나 하위 의존성이 많은 경우.
2. **외부 세계 보호**: 실제 은행 계좌 인출·실제 DB 쓰기 같은 부수 효과로부터 외부를 보호.
3. **외부로부터 테스트 보호**: 비결정적 값(자주 바뀌는 잔액, 난수)으로부터 테스트를 결정적으로 유지.

테스트 더블에는 세 종류가 있다.

- **목(*mock*)**: 멤버 함수 호출을 **기록**만 한다. 특정 함수가 특정 인수로 호출됐는지 검증할 때 쓴다(부수 효과 시뮬레이션에 유용).
- **스텁(*stub*)**: 함수가 호출되면 **미리 정한 값을 반환**한다. 의존성으로부터 값을 받아야 할 때 쓴다.
- **페이크(*fake*)**: 실제 의존성의 **대체 구현체**. 퍼블릭 API를 정확히 시뮬레이션하되 외부 시스템 대신 내부 멤버 변수에 상태를 저장한다.

<details>
<summary>의사코드 (원서) — 예제 10.4·10.6 목과 스텁</summary>

```java
// 목: debit()이 예상 인수로 호출됐는지 검증
void testSettleInvoice_accountDebited() {
  BankAccount mockAccount = createMock(BankAccount);
  Invoice invoice = new Invoice(new MonetaryAmount(5.0, USD), "test-id");
  new PaymentManager().settleInvoice(mockAccount, invoice);
  verifyThat(mockAccount.debit).wasCalledOnce().withArguments(invoice.getBalance());
}

// 스텁: getBalance()가 미리 정한 값을 반환하도록 설정
void testSettleInvoice_insufficientFunds() {
  BankAccount mockAccount = createMock(BankAccount);
  when(mockAccount.getBalance()).thenReturn(new MonetaryAmount(9.99, USD));
  Invoice invoice = new Invoice(new MonetaryAmount(10.0, USD), "test-id");
  PaymentResult result = new PaymentManager().settleInvoice(mockAccount, invoice);
  assertThat(result.getStatus()).isEqualTo(INSUFFICIENT_FUNDS);
}
```

</details>

**목·스텁은 두 가지 문제가 있다.**

- **비현실적 테스트**: 목·스텁을 실제 의존성과 다르게 동작하도록 설정하면, 테스트는 통과하지만 코드는 실제로 버그가 있을 수 있다. 예: `debit()`은 음수 금액에 `ArgumentException`을 던지는데, 목은 그냥 호출만 기록하므로 "음수 송장 잔액" 버그가 테스트를 **통과**해버린다(사실상 동어반복 테스트).
- **구현 세부사항과 결합**: "`debit()`이 호출됐는지"를 검증하는 테스트는, `debit()`+`credit()`을 `transfer()` 하나로 리팩터링하면 동작이 같은데도 실패한다.

**해결책 — 가능하면 페이크를 써라.** 페이크는 코드 계약이 실제와 동일하므로(음수면 예외를 던지고, 잔액을 10 단위로 반내림하는 등) **버그를 잡아내고**, 최종 상태(계좌 잔액)를 검증하므로 **구현 세부사항과 분리**된다.

<details>
<summary>의사코드 (원서) — 예제 10.8·10.9 페이크와 그것을 쓰는 테스트</summary>

```java
class FakeBankAccount implements BankAccount {   // 실제 구현 대신 사용 가능
  private MonetaryAmount balance;                // 외부 대신 멤버 변수에 상태 저장
  FakeBankAccount(MonetaryAmount startingBalance) { this.balance = startingBalance; }

  override void debit(MonetaryAmount amount) {
    if (amount.isNegative()) { throw new ArgumentException("액수는 0보다 적을 수 없음"); } // 계약 강제
    balance = balance.subtract(amount);
  }
  override void credit(MonetaryAmount amount) {
    if (amount.isNegative()) { throw new ArgumentException("액수는 0보다 적을 수 없음"); }
    balance = balance.add(amount);
  }
  override MonetaryAmount getBalance() { return roundDownToNearest10(balance); } // 실제와 같은 동작
  MonetaryAmount getActualBalance() { return balance; }  // 테스트용 정확한 잔액 확인 함수
}

// 페이크를 쓰면 음수 송장 버그가 드러난다(예외 발생 → 테스트 실패)
void testSettleInvoice_negativeInvoiceBalance() {
  FakeBankAccount fakeAccount = new FakeBankAccount(new MonetaryAmount(100.0, USD));
  Invoice invoice = new Invoice(new MonetaryAmount(-5.0, USD), "test-id");
  new PaymentManager().settleInvoice(fakeAccount, invoice);
  assertThat(fakeAccount.getActualBalance()).isEqualTo(new MonetaryAmount(105.0, USD));
}
```

</details>

```typescript
// 페이크: 실제 BankAccount를 대체하되 코드 계약(음수 금지·반내림)을 그대로 지킨다
class FakeBankAccount implements BankAccount {
  constructor(private balance: MonetaryAmount) {}

  debit(amount: MonetaryAmount): void {
    if (amount.isNegative()) {
      throw new ArgumentError("액수는 0보다 적을 수 없음"); // 계약 강제 → 버그를 잡아냄
    }
    this.balance = this.balance.subtract(amount);
  }
  credit(amount: MonetaryAmount): void {
    if (amount.isNegative()) {
      throw new ArgumentError("액수는 0보다 적을 수 없음");
    }
    this.balance = this.balance.add(amount);
  }
  getBalance(): MonetaryAmount {
    return roundDownToNearest10(this.balance); // 실제 구현과 같은 동작
  }
  getActualBalance(): MonetaryAmount {
    return this.balance; // 테스트가 정확한 잔액을 확인할 수 있는 추가 함수
  }
}
```

**목에 대한 두 의견**: **목 찬성론자(mockist, 런던 학파)**는 의존성을 목으로 대체하는 것을 선호하고, **고전주의자(classicist, 디트로이트 학파)**는 실제 의존성 사용을 우선하고 불가능하면 페이크, 목·스텁은 최후의 수단으로 본다. 목 접근법은 "코드가 **어떻게** 하는가"(상호작용)를, 고전주의는 "**최종 결과**가 무엇인가"(결과 상태)를 검증한다.

> **핵심 통찰**: 저자(고전주의자)는 **① 실제 의존성 → ② 페이크 → ③ 목·스텁(최후의 수단)** 순으로 선호한다. 목·스텁으로라도 테스트하는 것이 아예 안 하는 것보다는 낫지만, 비현실적 테스트와 구현 세부사항 결합의 위험을 안는다. 자기 팀이 관리하는 의존성이라면 **페이크를 직접 구현**해 두는 것이 자신과 다른 팀 모두에게 이롭다.

---

## 5. 테스트 철학으로부터 신중하게 선택하라 (10.5)

테스트 철학은 '전부 아니면 전무'가 아니다. 여러 철학에서 옳다고 생각하는 것을 **취사선택**할 자유가 있다.

- **테스트 주도 개발(TDD)**: 실제 코드보다 **테스트를 먼저** 작성하고, 통과할 최소 코드를 짠 뒤 리팩터링한다(켄트 벡).
- **행동 주도 개발(BDD)**: 사용자·고객·비즈니스 관점의 **동작(기능)**을 식별하는 데 집중하고, 테스트가 그 동작을 반영하게 한다.
- **인수 테스트 주도 개발(ATDD)**: 고객 관점의 동작을 자동화된 **인수 테스트**로 만들어, 전체 소프트웨어가 필요를 충족하는지 검증한다.

> **핵심 통찰**: 방법론은 효과적이라고 여겨지는 작업 방식을 문서화한 것일 뿐, **궁극적으로 달성하려는 목표**(고품질 테스트와 소프트웨어)가 방법론 자체보다 중요하다. 어떤 철학을 문자 그대로 따를 때 가장 효과적이라면 그렇게 하고, 아니라면 자기 방식대로 해도 좋다.

---

## 6. 코드 품질 6대 요소 연결

이 장은 6대 요소 중 **테스트 용이성**의 원칙 자체를 다룬다. 그리고 좋은 테스트는 다른 요소들과 서로를 강화한다.

| 이 장의 원칙 | 다른 요소와의 관계 |
|---|---|
| 구현 세부사항 독립 테스트 (10.2) | **모듈화**(2·8장)가 잘 될수록 동작 단위로 테스트하기 쉬움 |
| 퍼블릭 API 중심 (10.3) | 2장의 API/구현 세부사항 경계가 테스트 경계와 일치 |
| 테스트 더블·페이크 (10.4) | **의존성 주입**(8장)이 되어 있어야 더블로 교체 가능 |

> **핵심 통찰**: 테스트 용이성은 **모듈화의 부산물**이다. DI로 의존성을 주입받게 설계되어 있으면 테스트에서 페이크로 교체할 수 있고, 추상화 계층이 깔끔하면 동작 단위로 테스트가 갈린다. 반대로 정적 매달림(8.1)이 있으면 테스트 더블을 끼울 수 없다.

---

## 요약

- 제출되는 거의 모든 실제 코드에는 단위 테스트가 동반되어야 하고, 코드가 보이는 **모든 동작**에 테스트 케이스가 있어야 한다. 테스트 케이스는 보통 **준비·실행·단언** 세 부분으로 나뉜다.
- 좋은 단위 테스트의 다섯 특징: **훼손의 정확한 감지 / 구현 세부 독립 / 잘 설명되는 실패 / 이해 가능한 코드 / 쉽고 빠른 실행**.
- **퍼블릭 API에 집중**하되, 퍼블릭 API 밖에 있어도 **중요한 동작은 반드시 테스트**하라.
- **테스트 더블**(목·스텁·페이크)은 실제 의존성을 쓸 수 없을 때 사용한다. 목·스텁은 비현실적이거나 구현 세부사항과 결합될 수 있어, **가능하면 실제 의존성 → 페이크 → 목·스텁** 순으로 선호한다.
- 테스트 철학(TDD·BDD·ATDD)은 취사선택하라 — **목표가 방법론보다 중요**하다.
