# Chapter 6: A First Set of Refactorings (기본적인 리팩터링)

## 핵심 질문

가장 자주 쓰는 기본 리팩터링은 무엇인가? 코드를 언제 함수로 **추출**하고 언제 다시 **인라인**하는가? 복잡한 표현식/변수에 이름을 붙이는 두 방법(변수 vs 함수)은 어떻게 고르는가? 저수준 함수들을 어떻게 다시 **클래스·변환 함수·단계**로 조직하는가? 각 리팩터링의 **절차(mechanics)**는 어떤 작은 단계로 이뤄지는가?

---

## 0. 이 장에서 다루는 것 · 카탈로그 표기 규약

6~12장은 **리팩터링 카탈로그**다. 각 기법은 일정한 틀로 서술된다.

- **기법명 (영문명)** + 한 줄 정의 + **반대/관련 리팩터링**
- **스케치**: before → after의 한눈에 보이는 축약 예
- **배경(Motivation)**: 언제·왜 하는가
- **절차(Mechanics)**: 번호가 매겨진 작은 단계

이 장은 가장 기본적이고 많이 쓰는 리팩터링이다. 추출/인라인(함수·변수)으로 **이름을 짓고**, 함수 선언 바꾸기·캡슐화·이름 바꾸기로 **연결부를 다듬고**, 매개변수 객체·클래스로 묶기·변환 함수로 묶기·단계 쪼개기로 **저수준 함수를 고수준 구조로 조직**한다.

> **코드 표기 규약**: 원서 JavaScript를 `<details>`로 접어 두고 **TypeScript**를 병기한다. 모든 `if`/`for` 본문에 중괄호를 쓴다.

---

## 1. 함수 추출하기 (6.1) — Extract Function

코드 조각을 **목적을 드러내는 이름의 함수**로 뽑아낸다. (반대: 함수 인라인하기 6.2)

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before
function printOwing(invoice) {
  printBanner();
  let outstanding = calculateOutstanding();
  // 세부 사항 출력
  console.log(`고객명: ${invoice.customer}`);
  console.log(`채무액: ${outstanding}`);
}
// after
function printOwing(invoice) {
  printBanner();
  let outstanding = calculateOutstanding();
  printDetails(outstanding);
  function printDetails(outstanding) {
    console.log(`고객명: ${invoice.customer}`);
    console.log(`채무액: ${outstanding}`);
  }
}
```

</details>

```typescript
// before — "세부 사항 출력"이 주석으로만 표시돼 있다
function printOwing(invoice: Invoice): void {
  printBanner();
  const outstanding = calculateOutstanding();
  // 세부 사항 출력
  console.log(`고객명: ${invoice.customer}`);
  console.log(`채무액: ${outstanding}`);
}
// after — 목적을 이름(printDetails)으로 승격 (중첩 함수라 invoice에 접근 가능)
function printOwing(invoice: Invoice): void {
  printBanner();
  const outstanding = calculateOutstanding();
  printDetails(outstanding);
  function printDetails(outstanding: number): void {
    console.log(`고객명: ${invoice.customer}`);
    console.log(`채무액: ${outstanding}`);
  }
}
```

**배경**: 파울러가 가장 많이 쓰는 리팩터링. 기준은 길이·재사용성이 아니라 **"목적과 구현의 분리"**다 — 파악에 시간이 걸리는 코드를 빼서 **'무엇을' 하는지**로 이름 짓는다. 이름이 구현보다 길어도 좋다(강조=`highlight()`가 반전=`reverse()`만 호출하듯).

**절차**:
1. 함수를 새로 만들고 **'무엇을'** 하는지 드러나는 이름을 붙인다.
2. 추출할 코드를 새 함수로 복사한다.
3. **유효범위 밖 변수**를 매개변수로 전달한다(값이 바뀌는 변수가 하나면 반환값으로; 너무 많으면 `변수 쪼개기`·`임시 변수를 질의 함수로 바꾸기(7.4)` 후 재시도).
4. 컴파일한다.
5. 원본의 해당 코드를 **함수 호출문**으로 교체한다.
6. 테스트한다.
7. 다른 곳의 **중복 코드**도 이 함수를 호출하도록 검토한다.

> **핵심 통찰**: 좋은 이름이 떠오르지 않으면 **추출하지 말라는 신호**일 수 있다. 일단 뽑아 보고 효과가 없으면 인라인해 되돌려도 된다.

---

## 2. 함수 인라인하기 (6.2) — Inline Function

함수 호출을 **본문으로 대체**하고 그 함수를 제거한다. (반대: 함수 추출하기 6.1)

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before
function getRating(driver) {
  return moreThanFiveLateDeliveries(driver) ? 2 : 1;
}
function moreThanFiveLateDeliveries(driver) {
  return driver.numberOfLateDeliveries > 5;
}
// after
function getRating(driver) {
  return driver.numberOfLateDeliveries > 5 ? 2 : 1;
}
```

</details>

```typescript
// before — 본문이 이름만큼 명확해 간접 호출이 군더더기
function getRating(driver: Driver): number {
  return moreThanFiveLateDeliveries(driver) ? 2 : 1;
}
function moreThanFiveLateDeliveries(driver: Driver): boolean {
  return driver.numberOfLateDeliveries > 5;
}
// after
function getRating(driver: Driver): number {
  return driver.numberOfLateDeliveries > 5 ? 2 : 1;
}
```

**배경**: 짧은 함수를 권하지만 **본문이 이름만큼 명확**하면 간접 호출은 군더더기다. 리팩터링 중 **잘못 추출된 함수**를 되돌리거나, 위임만 하는 함수가 얽힌 **과한 간접 호출**을 정리할 때 쓴다.

**절차**:
1. **다형 메서드가 아닌지** 확인한다(오버라이드되면 인라인 금지).
2. 모든 **호출처**를 찾는다.
3. 각 호출문을 함수 **본문으로 교체**한다.
4. 하나씩 교체할 때마다 테스트한다.
5. 함수 정의를 삭제한다.

> **핵심 통찰**: 재귀·다중 반환문으로 복잡해지면 **애초에 인라인하면 안 된다는 신호**다. 복잡하면 `문장을 호출한 곳으로 옮기기(8.4)`로 한 문장씩 나눠 처리한다.

---

## 3. 변수 추출하기 (6.3) — Extract Variable

복잡한 표현식의 일부에 **이름 붙인 지역 변수**를 도입한다. (반대: 변수 인라인하기 6.4)

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before
return order.quantity * order.itemPrice
  - Math.max(0, order.quantity - 500) * order.itemPrice * 0.05
  + Math.min(order.quantity * order.itemPrice * 0.1, 100);
// after
const basePrice = order.quantity * order.itemPrice;
const quantityDiscount = Math.max(0, order.quantity - 500) * order.itemPrice * 0.05;
const shipping = Math.min(basePrice * 0.1, 100);
return basePrice - quantityDiscount + shipping;
```

</details>

```typescript
// before — 기본가·수량할인·배송비가 한 표현식에 뭉쳐 의미가 안 보인다
function price(order: Order): number {
  return (
    order.quantity * order.itemPrice -
    Math.max(0, order.quantity - 500) * order.itemPrice * 0.05 +
    Math.min(order.quantity * order.itemPrice * 0.1, 100)
  );
}
// after — 각 단계에 이름을 붙여 "기본가 - 수량할인 + 배송비"가 드러난다
function price(order: Order): number {
  const basePrice = order.quantity * order.itemPrice;
  const quantityDiscount = Math.max(0, order.quantity - 500) * order.itemPrice * 0.05;
  const shipping = Math.min(basePrice * 0.1, 100);
  return basePrice - quantityDiscount + shipping;
}
```

**배경**: 복잡한 표현식을 지역 변수로 쪼개 **단계마다 이름**을 붙여 목적을 드러낸다(디버깅 중단점·로그에도 유용). 단, 이름이 **함수 범위를 넘어 의미**가 있다면 변수가 아니라 **함수로 추출**해야 재사용된다.

**절차**:
1. 추출할 표현식에 **부작용이 없는지** 확인한다.
2. **불변 변수**를 선언하고 표현식의 복제본을 대입한다.
3. 원본 표현식을 새 변수로 교체한다.
4. 테스트한다(여러 곳이면 각각 교체하며 매번 테스트).

> **핵심 통찰**: 클래스 안이라면 같은 추출을 **게터 메서드**로 하는 편이 낫다 — `get basePrice()` 등으로 만들면 클래스 전체에서 쓸 수 있다. 객체는 "로직·데이터를 공유할 적당한 문맥"을 제공한다.

---

## 4. 변수 인라인하기 (6.4) — Inline Variable

이름이 표현식만큼 명확한 변수를 없애고 **표현식으로 되돌린다**. (반대: 변수 추출하기 6.3)

```typescript
// before — baseprice는 anOrder.basePrice와 다를 바 없다
const basePrice = anOrder.basePrice;
return basePrice > 1000;
// after
return anOrder.basePrice > 1000;
```

**배경**: 변수 이름이 원래 표현식과 다를 바 없거나, 그 변수가 **주변 리팩터링을 방해**할 때 인라인한다.

**절차**:
1. 대입문 우변(표현식)에 **부작용이 없는지** 확인한다.
2. 변수가 불변이 아니면 불변으로 만든 뒤 테스트한다(값이 한 번만 대입되는지 확인).
3. 변수를 처음 사용하는 곳을 대입문 우변으로 바꾸고 테스트한다.
4. 모든 사용처를 교체할 때까지 반복한다.
5. 변수 선언·대입문을 지우고 테스트한다.

---

## 5. 함수 선언 바꾸기 (6.5) — Change Function Declaration

함수의 **이름·매개변수**를 바꾼다("함수 이름 바꾸기", "시그니처 바꾸기"로도 불림).

```typescript
// before → after: 이름 개선
function circum(radius: number): number { return 2 * Math.PI * radius; }
function circumference(radius: number): number { return 2 * Math.PI * radius; }
```

**배경**: 함수 선언은 시스템 구성 요소를 잇는 **연결부**다. 그중 가장 중요한 것이 **이름** — 좋으면 구현을 안 봐도 호출문만으로 목적을 안다. **매개변수**는 함수의 활용 문맥을 정한다(전화번호 포매터가 '사람'이 아니라 '전화번호'를 받으면 결합이 줄고 재사용 범위가 넓어진다). 잘못된 이름을 보면 **더 나은 이름이 떠오르는 즉시 바꾸라**는 명령으로 받아들여라.

**절차 — 간단한 절차** (호출처를 단번에 고칠 수 있을 때):
1. (매개변수 제거 시) 본문에서 그 매개변수를 참조하는 곳이 없는지 확인한다.
2. 선언을 원하는 형태로 바꾼다.
3. 기존 선언을 참조하는 곳을 모두 찾아 수정한다.
4. 테스트한다. (이름 변경 + 매개변수 추가는 각각 독립적으로 처리)

**절차 — 마이그레이션 절차** (호출처가 많거나 복잡·다형·공개 API일 때, 점진적 수정):
1. (필요시) 본문을 미리 리팩터링한다.
2. 본문을 **새 함수로 추출**한다(이름이 겹치면 임시 이름).
3. 추출한 함수에 매개변수를 추가한다(간단한 절차).
4. 테스트한다.
5. 기존 함수를 **인라인**해 호출들이 새 함수를 쓰게 한다(하나씩).
6. 임시 이름이었다면 다시 원래 이름으로 바꾼다.
7. 테스트한다.

> **핵심 통찰**: 함수 선언 바꾸기는 **직접 못 고치는 공개 API**에도 좋다 — 새 함수를 추가하고 기존 함수를 **폐기 대상(deprecated)**으로 표시한 뒤, 모든 클라이언트가 이전하면 삭제한다.

---

## 6. 변수 캡슐화하기 (6.6) — Encapsulate Variable

접근 범위가 넓은 데이터로의 접근을 **게터·세터 함수**로 감싼다.

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before
let defaultOwner = { firstName: "마틴", lastName: "파울러" };
// after
let defaultOwnerData = { firstName: "마틴", lastName: "파울러" };
export function defaultOwner() { return defaultOwnerData; }
export function setDefaultOwner(arg) { defaultOwnerData = arg; }
```

</details>

```typescript
// after — 데이터 접근을 함수로 독점 (파일 밖에는 접근자만 노출)
let defaultOwnerData = { firstName: "마틴", lastName: "파울러" };
export function defaultOwner(): Person {
  return defaultOwnerData;
}
export function setDefaultOwner(arg: Person): void {
  defaultOwnerData = arg;
}
```

**배경**: 함수는 다루기 쉽지만(전달 함수로 우회 가능) **데이터는 참조하는 모든 곳을 한 번에 바꿔야** 해서 까다롭다. 특히 유효범위가 넓은 데이터(전역 데이터)가 골칫거리다. 접근을 **함수로 독점**하면 "데이터 재구성"이라는 어려운 작업을 "함수 재구성"이라는 쉬운 작업으로 바꾸고, 검증·로깅을 끼울 통로도 생긴다. **유효범위가 함수보다 넓은 가변 데이터는 모두 캡슐화**하라(불변 데이터는 캡슐화 이유가 적다 — "불변성은 강력한 방부제").

**절차**:
1. 변수의 접근·갱신을 전담하는 캡슐화 함수를 만든다.
2. 정적 검사를 수행한다.
3. 직접 참조를 모두 캡슐화 함수 호출로 바꾼다(하나씩 테스트).
4. 변수의 접근 범위를 제한한다.
5. 테스트한다.
6. (값이 레코드라면) `레코드 캡슐화하기(7.1)`를 고려한다.

> **핵심 통찰**: 게터가 **데이터 값 자체의 변경**까지 막지는 못한다 — 필요하면 게터가 **복제본**을 반환하거나, 값을 불변 클래스(`레코드 캡슐화하기`)로 감싼다.

---

## 7. 변수 이름 바꾸기 (6.7) — Rename Variable

변수 이름을 **의미가 드러나게** 바꾼다.

```typescript
// before → after
let a = height * width;
let area = height * width;
```

**배경**: 명확한 프로그래밍의 핵심은 이름짓기다. 이름의 중요성은 **사용 범위**에 비례한다 — 한 줄 람다의 변수는 한 글자여도 되지만, 값이 오래 지속되는 **필드**일수록 신중해야 한다.

**절차**:
1. (폭넓게 쓰이면) `변수 캡슐화하기(6.6)`를 먼저 고려한다.
2. 변수를 참조하는 곳을 모두 찾아 하나씩 이름을 바꾼다.
3. 테스트한다.

---

## 8. 매개변수 객체 만들기 (6.8) — Introduce Parameter Object

함께 몰려다니는 인수들을 **객체 하나로 묶는다**.

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before
function amountInvoiced(startDate, endDate) {...}
function amountReceived(startDate, endDate) {...}
// after
function amountInvoiced(aDateRange) {...}
function amountReceived(aDateRange) {...}
```

</details>

```typescript
// 온도 범위(min/max)가 여러 함수에 쌍으로 다니면 클래스로 묶는다
class NumberRange {
  constructor(
    private readonly _min: number,
    private readonly _max: number,
  ) {}
  get min(): number { return this._min; }
  get max(): number { return this._max; }
  // 이 리팩터링의 진짜 힘: 관련 동작을 이 클래스로 옮길 수 있다
  contains(arg: number): boolean {
    return arg >= this.min && arg <= this.max;
  }
}
// before: readingsOutsideRange(station, min, max)
// after:
function readingsOutsideRange(station: Station, range: NumberRange): Reading[] {
  return station.readings.filter((r) => !range.contains(r.temp));
}
```

**배경**: 데이터 뭉치를 구조로 묶으면 (1) 관계가 명확해지고, (2) 매개변수 수가 줄고, (3) 이름이 일관돼진다. 진짜 힘은 그 다음 — 데이터에 공통으로 적용되는 **동작을 이 구조(클래스)로 옮겨** 새로운 추상 개념(예: `Range`)으로 격상시키는 것이다.

**절차**:
1. 적당한 데이터 구조가 없으면 만든다(주로 **값 객체** 클래스).
2. 테스트한다.
3. `함수 선언 바꾸기(6.5)`로 새 구조를 매개변수로 추가한다.
4. 테스트한다.
5. 호출 시 새 구조 인스턴스를 넘기도록 하나씩 수정한다.
6. 기존 매개변수를 쓰던 코드를 새 구조의 원소를 쓰도록 바꾼다.
7. 기존 매개변수를 제거하고 테스트한다.

> **핵심 통찰**: 이 리팩터링은 대개 더 큰 작업의 **첫 단계**다 — 매개변수 그룹을 객체로 바꾼 뒤 동작을 옮기고, 값 기반 동치성까지 더하면 **진정한 값 객체**로 거듭난다.

---

## 9. 여러 함수를 클래스로 묶기 (6.9) — Combine Functions into Class

공통 데이터에 작용하는 함수들을 **하나의 클래스**로 묶는다. (대안: 6.10)

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before
function base(aReading) {...}
function taxableCharge(aReading) {...}
function calculateBaseCharge(aReading) {...}
// after
class Reading {
  base() {...}
  taxableCharge() {...}
  calculateBaseCharge() {...}
}
```

</details>

```typescript
// 공통 데이터(reading)에 작용하던 함수들을 Reading 클래스로 응집
class Reading {
  constructor(private readonly data: ReadingData) {}
  get baseCharge(): number { /* 공통 데이터 사용 */ }
  get taxableCharge(): number {
    return Math.max(0, this.baseCharge - taxThreshold(this.year));
  }
}
```

**배경**: 클래스는 **데이터와 함수를 하나의 공유 환경으로 묶는** 기본 빌딩 블록이다. 여러 함수가 같은 데이터를 인수로 물고 다니면, 그 데이터를 중심으로 클래스로 응집하는 편이 낫다.

**절차**:
1. 함수들이 공유하는 **공통 데이터 레코드를 캡슐화**한다(`레코드 캡슐화하기`).
2. 공통 레코드를 쓰는 각 함수를 새 클래스로 **옮긴다**(`함수 옮기기(8.1)`). 공통 인수는 호출에서 뺀다.
3. 데이터를 조작하는 로직은 함수로 **추출**해 클래스로 옮긴다.

---

## 10. 여러 함수를 변환 함수로 묶기 (6.10) — Combine Functions into Transform

파생 데이터 계산 함수들을 **하나의 변환 함수**로 모은다(읽기전용 데이터에 적합). (대안: 6.9)

```typescript
// 입력 레코드를 받아 파생 필드를 추가한 '사본'을 반환하는 변환 함수
function enrichReading(original: ReadingData): EnrichedReading {
  const result = structuredClone(original) as EnrichedReading;
  result.baseCharge = calculateBaseCharge(result);
  result.taxableCharge = Math.max(0, result.baseCharge - taxThreshold(result.year));
  return result;
}
```

**배경**: 6.9와 목적은 같다(파생 계산 로직을 한데 모아 중복·산재를 막음). 다만 **원본 데이터가 코드 전반에서 갱신되면** 클래스가 낫고, **읽기전용**이면 변환 함수가 깔끔하다.

**절차**:
1. 변환할 레코드를 입력받아 **같은 값을 반환**하는 변환 함수를 만든다(대개 깊은 복사).
2. 묶을 계산 로직 하나를 골라 본문을 변환 함수로 옮기고, 결과를 레코드의 **필드로 저장**한다. 클라이언트가 그 필드를 쓰게 고친다.
3. 테스트한다.
4. 나머지 계산 함수도 같은 식으로 처리한다.

---

## 11. 단계 쪼개기 (6.11) — Split Phase

서로 다른 두 대상을 다루는 코드를 **순차적인 두 단계**로 분리한다. (Ch1에서 사용)

```typescript
// before: 하나의 함수가 (1) 계산과 (2) 표현을 뒤섞어 처리
// after: 중간 데이터 구조를 사이에 두고 두 단계로 분리
function statement(invoice: Invoice, plays: Plays): string {
  return renderPlainText(createStatementData(invoice, plays)); // 계산 → 표현
}
```

**배경**: 한 코드가 **성격이 다른 두 가지 일**(예: 계산 vs 표현, 파싱 vs 처리)을 하면, 중간 데이터 구조를 경계로 두 단계로 나눈다. 그러면 각 단계를 독립적으로 이해·수정할 수 있고, 다른 표현(HTML 등)을 값싸게 추가할 수 있다(Ch1의 핵심 국면 중 하나).

**절차**:
1. 두 번째 단계 코드를 **독립 함수로 추출**한다.
2. 테스트한다.
3. **중간 데이터 구조**를 만들어 추출한 함수의 인수로 추가한다.
4. 테스트한다.
5. 추출한 두 번째 단계 함수의 매개변수를 검토해, 첫 단계에서 쓰이면 중간 데이터 구조로 옮긴다(매번 테스트).
6. 첫 단계 코드를 함수로 추출하면서 **중간 데이터 구조를 반환**하게 한다.

> **핵심 통찰**: 6.9·6.10·6.11은 저수준 함수를 다시 **고수준 구조**로 조직하는 세 방법이다 — 갱신되는 데이터는 클래스(6.9), 읽기전용은 변환 함수(6.10), 성격이 다른 두 작업은 단계(6.11)로.

---

## 요약

- 6~12장은 리팩터링 카탈로그로, 각 기법을 **스케치·배경·절차** 틀로 서술한다. 모든 리팩터링의 공통 리듬은 **작은 절차 단계 + 매번 테스트**다.
- **추출/인라인**: 함수 추출(6.1)의 기준은 '목적과 구현의 분리'. 본문이 이름만큼 명확하면 인라인(6.2)한다. 변수도 마찬가지로 추출(6.3)/인라인(6.4)한다.
- **연결부 다듬기**: 함수 선언 바꾸기(6.5)로 이름·매개변수를 개선(공개 API는 마이그레이션 절차). 넓은 범위 데이터는 캡슐화(6.6), 변수는 의미 있게 이름 바꾸기(6.7).
- **고수준으로 조직**: 몰려다니는 인수는 매개변수 객체(6.8)로. 공통 데이터에 작용하는 함수는 클래스(6.9) 또는 변환 함수(6.10)로 묶고, 성격이 다른 두 작업은 단계 쪼개기(6.11)로 분리한다.
