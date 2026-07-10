# Chapter 10: Simplifying Conditional Logic (조건부 로직 간소화)

## 핵심 질문

복잡한 조건문은 '무엇'은 말해도 '왜'는 말하지 못한다 — 어떻게 의도를 드러내는가? 여러 조건이 같은 동작으로 이어질 때, 중첩·나열된 조건을 어떻게 통합하고 평탄하게 만드는가? 타입별 switch가 여러 곳에 흩어져 있을 때 다형성이 왜 강력한가? 널 같은 특이 케이스의 중복 처리는 어떻게 한 곳에 모으는가? 코드의 가정은 어떻게 명시하는가?

---

## 0. 이 장에서 다루는 것 · 코드 표기 규약

조건부 로직은 프로그램의 힘을 키우지만 복잡함의 주요 원흉이기도 하다. 복잡한 조건문은 **분해하기(10.1)**, 논리 조합은 **통합하기(10.2)**, 핵심 로직 앞의 검사는 **보호 구문으로(10.3)**, 타입별 분기(주로 switch)는 **다형성으로(10.4)** 바꾼다. 널 등 특이 케이스의 똑같은 처리는 **특이 케이스 추가하기(10.5)**로 모으고, 코드의 가정은 **어서션 추가하기(10.6)**로 명시하며, 흐름을 바꾸는 플래그는 **제어 플래그를 탈출문으로 바꾸기(10.7)**로 없앤다.

> **코드 표기 규약**: 원서 JavaScript를 `<details>`로 접어 두고 **TypeScript**를 병기한다. 각 기법은 **스케치(before→after) · 배경 · 절차** 형식이다.

---

## 1. 조건문 분해하기 (10.1) — Decompose Conditional

조건식과 각 조건절을 **의도를 드러내는 이름의 함수**로 추출한다.

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before
if (!aDate.isBefore(plan.summerStart) && !aDate.isAfter(plan.summerEnd)) {
  charge = quantity * plan.summerRate;
} else {
  charge = quantity * plan.regularRate + plan.regularServiceCharge;
}
// after
if (summer()) {
  charge = summerCharge();
} else {
  charge = regularCharge();
}
```

</details>

```typescript
// 조건식·조건절을 각각 함수로 — '왜'가 드러난다. 취향껏 3항으로도 정리 가능
const charge = summer() ? summerCharge() : regularCharge();

function summer(): boolean {
  return !aDate.isBefore(plan.summerStart) && !aDate.isAfter(plan.summerEnd);
}
function summerCharge(): number {
  return quantity * plan.summerRate;
}
function regularCharge(): number {
  return quantity * plan.regularRate + plan.regularServiceCharge;
}
```

**배경**: 복잡한 조건부 로직은 코드를 길게 만들고, 조건과 동작을 표현한 코드는 **무슨 일이 일어나는지는 말해도 '왜'인지는 말해 주지 않을 때가 많다**. 조건식과 각 절을 의도를 살린 이름의 함수 호출로 바꾸면, 무엇을 왜 분기하는지가 명백해진다. 이는 **함수 추출(6.1)**의 한 사례지만, 연습용으로 훌륭해 독립된 리팩터링으로 다룬다.

**절차**:
1. 조건식과 그에 딸린 **조건절 각각을 함수로 추출(6.1)**한다.

---

## 2. 조건식 통합하기 (10.2) — Consolidate Conditional Expression

**조건은 다르지만 동작이 같은** 여러 검사를 하나의 조건식으로 합친다.

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before: 결과가 모두 같은 순차 검사
if (anEmployee.seniority < 2) return 0;
if (anEmployee.monthsDisabled > 12) return 0;
if (anEmployee.isPartTime) return 0;
// after
if (isNotEligibleForDisability()) return 0;
function isNotEligibleForDisability() {
  return anEmployee.seniority < 2
    || anEmployee.monthsDisabled > 12
    || anEmployee.isPartTime;
}
```

</details>

**배경**: 어차피 같은 일을 한다면 조건 검사도 하나로 합치는 게 낫다. (1) 여러 조각으로 나뉜 조건을 통합하면 하려는 일이 명확해진다(나뉘어 있으면 독립된 검사가 우연히 나열된 것으로 오해된다). (2) 통합한 조건식은 **함수 추출(6.1)**로 이어져 '무엇'이 아닌 '왜'를 말하는 코드가 된다. 단, **진짜로 독립된 검사**라면 이 리팩터링을 하면 안 된다.

**절차**:
1. 조건식들에 **부수효과가 없는지** 확인한다(있으면 **질의/변경 함수 분리(11.1)** 먼저).
2. 두 조건문을 논리 연산자로 결합한다 — **순차(같은 레벨)는 `||`(or)**, **중첩은 `&&`(and)**.
3. 테스트한다.
4. 조건이 하나만 남을 때까지 반복한다.
5. 합쳐진 조건식을 **함수로 추출(6.1)**할지 고려한다.

---

## 3. 중첩 조건문을 보호 구문으로 바꾸기 (10.3) — Replace Nested Conditional with Guard Clauses

**한쪽만 정상인 조건**은 비정상 케이스를 먼저 검사해 빠져나가는 **보호 구문(guard clause)**으로 바꾼다.

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before: 중첩 if-else + result 변수
function getPayAmount() {
  let result;
  if (isDead) { result = deadAmount(); }
  else {
    if (isSeparated) { result = separatedAmount(); }
    else {
      if (isRetired) { result = retiredAmount(); }
      else { result = normalPayAmount(); }
    }
  }
  return result;
}
// after: 보호 구문 나열
function getPayAmount() {
  if (isDead) return deadAmount();
  if (isSeparated) return separatedAmount();
  if (isRetired) return retiredAmount();
  return normalPayAmount();
}
```

</details>

**배경**: 조건문은 두 형태다 — 참·거짓 **양쪽 모두 정상**이거나, **한쪽만 정상**이거나. `if/else`는 양 갈래가 똑같이 중요하다는 뜻을 전한다. 반면 보호 구문은 "이건 이 함수의 핵심이 아니다. 이 일이 일어나면 조치 후 빠져나온다"라고 말한다. 의도가 다르므로 코드에 드러나야 한다.

> **핵심 통찰**: **반환점이 하나여야 한다는 규칙은 유용하지 않다.** 코드에서는 명확함이 핵심이다 — 반환점이 하나일 때 로직이 더 명백하면 그렇게 하고, 아니면 하지 말라. (가변 변수 `result`를 함께 제거하면 자다가도 떡이 생긴다.)

**절차**:
1. 가장 바깥 조건을 보호 구문으로 바꾼다.
2. 테스트한다.
3. 필요한 만큼 반복한다.
4. 모든 보호 구문이 같은 결과를 반환한다면 **조건식을 통합(10.2)**한다.

> **조건 반대로 만들기**(조슈아 케리에프스키 제안): 정상 케이스를 감싼 조건은 **부정(`!`)**을 붙여 보호 구문으로 만든 뒤(`if (x > 0) {...}` → `if (x <= 0) return ...`), `!(a && b)`는 `a <= 0 || b <= 0`처럼 드모르간으로 간소화한다.

---

## 4. 조건부 로직을 다형성으로 바꾸기 (10.4) — Replace Conditional with Polymorphism

**타입에 따라 분기하는 로직**(주로 switch)을, 타입별 클래스와 다형성으로 대체한다.

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before: 여러 함수에 같은 switch(bird.type)가 반복
switch (bird.type) {
  case '유럽 제비': return "보통이다";
  case '아프리카 제비': return (bird.numberOfCoconuts > 2) ? "지쳤다" : "보통이다";
  case '노르웨이 파랑 앵무': return (bird.voltage > 100) ? "그을렸다" : "예쁘다";
  default: return "알 수 없다";
}
// after: 타입별 클래스가 자기 방식으로 처리
class EuropeanSwallow { get plumage() { return "보통이다"; } }
class AfricanSwallow { get plumage() { return this.numberOfCoconuts > 2 ? "지쳤다" : "보통이다"; } }
class NorwegianBlueParrot { get plumage() { return this.voltage > 100 ? "그을렸다" : "예쁘다"; } }
```

</details>

**배경**: 타입을 기준으로 분기하는 switch가 **여러 함수에 반복**된다면, case별 클래스를 만들어 중복을 없앨 수 있다("책·음악·음식은 다르게 처리한다 — 왜? 타입이 다르니까"). 또 다른 쓰임은 **기본 동작 + 변형 동작**: 기본 로직을 슈퍼클래스에 두고, 변형을 서브클래스로 표현한다(서브클래스는 슈퍼클래스와의 **차이만** 담는다).

> **핵심 통찰**: 다형성은 강력하지만 **남용하기 쉽다**. "모든 조건부 로직을 다형성으로 바꿔야 한다"는 주장에는 동의하지 않는다 — 대부분의 조건부 로직은 평범한 `if/else`·`switch`로 충분하다. 다형성은 그렇게 **개선할 수 있는 복잡한 조건부 로직**을 만났을 때 꺼내는 도구다.

**절차**:
1. 다형적 클래스들이 없으면 만들고, 적합한 인스턴스를 반환하는 **팩터리 함수**도 만든다.
2. 호출 코드가 팩터리 함수를 쓰게 한다.
3. 조건부 로직 함수를 **슈퍼클래스로 옮긴다**(온전한 함수가 아니면 먼저 추출).
4. 서브클래스에서 슈퍼클래스 메서드를 **오버라이드**하고, 해당 조건절을 복사·수정한다.
5. 각 조건절을 해당 서브클래스 메서드로 구현한다.
6. 슈퍼클래스에는 **기본 동작만** 남긴다(추상이어야 하면 추상 선언 또는 에러 던지기).

```typescript
// 팩터리가 타입에 맞는 서브클래스를 반환 — 이후 switch가 사라진다
function createBird(bird: BirdData): Bird {
  switch (bird.type) {
    case "유럽 제비":
      return new EuropeanSwallow(bird);
    case "아프리카 제비":
      return new AfricanSwallow(bird);
    case "노르웨이 파랑 앵무":
      return new NorwegianBlueParrot(bird);
    default:
      return new Bird(bird); // 기본 동작
  }
}
class Bird {
  constructor(birdObject: BirdData) { Object.assign(this, birdObject); }
  get plumage(): string { return "알 수 없다"; }
  get airSpeedVelocity(): number | null { return null; }
}
class AfricanSwallow extends Bird {
  get plumage(): string { return this.numberOfCoconuts > 2 ? "지쳤다" : "보통이다"; }
  get airSpeedVelocity(): number { return 40 - 2 * this.numberOfCoconuts; }
}
```

> 자바스크립트는 타입 계층 없이도 **덕 타이핑**으로 다형성을 표현할 수 있으나, 슈퍼클래스가 관계를 잘 설명하면 그대로 둔다. **기본-변형 동작** 예(항해 투자 등급 A/B)에서는 서브클래스가 `super.method()`를 호출해 차이(예: `super.voyageProfitFactor + 3`)만 더하는 식으로 변형을 표현한다.

---

## 5. 특이 케이스 추가하기 (10.5) — Introduce Special Case

특정 값(주로 널)에 **똑같이 반응하는 중복 코드**를, 그 공통 동작을 담은 **특이 케이스 객체**로 모은다. (널 객체 패턴)

> 1판에서의 이름: Null 검사를 널 객체에 위임

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before: 곳곳에서 "미확인 고객"을 검사해 같은 기본값을 씀
if (aCustomer === "미확인 고객") customerName = "거주자";
// after: 특이 케이스 객체가 기본 동작을 캡슐화
class UnknownCustomer {
  get name() { return "거주자"; }
}
```

</details>

**배경**: 데이터의 특정 값을 확인해 똑같은 동작을 하는 코드가 곳곳에 있다면(흔한 중복), 그 반응들을 한 요소에 모으는 게 효율적이다 — 이것이 **특이 케이스 패턴(Special Case Pattern)**이다. 읽기만 하면 리터럴 객체로, 동작이 필요하면 메서드를 담은 객체로 표현한다. 널이 특이 케이스일 때가 많아 **널 객체 패턴(Null Object Pattern)**이라고도 한다(널 객체는 특이 케이스의 특수한 예다).

**절차**:
1. 컨테이너(속성을 담은 데이터 구조)에 **특이 케이스인지 검사하는 속성**을 추가하고 `false`를 반환하게 한다.
2. 그 속성만 담고 `true`를 반환하는 **특이 케이스 객체**를 만든다.
3. 클라이언트의 특이 케이스 검사 코드를 **함수로 추출(6.1)**해 모든 클라이언트가 그 함수를 쓰게 한다.
4. 특이 케이스일 때 그 객체를 반환하도록 한다(반환값 또는 변환 함수로).
5. 검사 함수가 **특이 케이스 객체의 속성**을 쓰도록 수정한다.
6. 테스트한다.
7. **여러 함수를 클래스로 묶기(6.9)**나 **변환 함수로 묶기(6.10)**로 공통 동작을 특이 케이스로 옮긴다.

```typescript
// 특이 케이스 객체 — 공통 기본값을 캡슐화 (값 객체이므로 불변)
class UnknownCustomer {
  get isUnknown(): boolean { return true; }
  get name(): string { return "거주자"; }
  get billingPlan(): BillingPlan { return registry.billingPlans.basic; }
  set billingPlan(arg: BillingPlan) { /* 무시한다 */ }
  get paymentHistory(): PaymentHistory { return new NullPaymentHistory(); }
}
class Site {
  get customer(): Customer | UnknownCustomer {
    return this._customer === "미확인 고객" ? new UnknownCustomer() : this._customer;
  }
}
// 클라이언트: 조건 검사가 사라진다
const customerName = aCustomer.name; // 미확인이면 "거주자"
```

> 특이 케이스가 또 다른 객체를 반환해야 하면(예: `paymentHistory`) 그 객체도 특이 케이스로 만든다(`NullPaymentHistory`). 대부분의 클라이언트가 공통 동작을 원해도 **튀는 클라이언트**가 있으면 `aCustomer.isUnknown` 검사를 남긴다. 갱신이 없다면 클래스 대신 **불변 리터럴 객체**(`Object.freeze`)나 **변환 함수**(`enrichSite`로 깊은 복사 후 특이 케이스 주입)로도 같은 아이디어를 적용할 수 있다.

---

## 6. 어서션 추가하기 (10.6) — Introduce Assertion

코드가 **항상 참이라고 가정하는 조건**을 어서션으로 명시한다.

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before: 할인율이 양수라는 가정이 암묵적
if (this.discountRate) {
  base = base - (this.discountRate * base);
}
// after: 가정을 명시
assert(this.discountRate >= 0);
if (this.discountRate) {
  base = base - (this.discountRate * base);
}
```

</details>

**배경**: 특정 조건이 참일 때만 동작하는 코드가 있다(제곱근은 입력이 양수일 때만). 이런 가정은 코드에 명시되어 있지 않아 알고리즘에서 연역해야 할 때가 많다. **어서션은 항상 참이라고 가정하는 조건부 문장**으로, 실패는 "프로그래머가 잘못했다"는 뜻이다. 시스템의 다른 부분은 어서션을 검사하지 않아야 하고, 어서션의 유무가 **정상 동작에 영향을 주면 안 된다**.

> **핵심 통찰**: 어서션의 진짜 가치는 오류 찾기를 넘어, **프로그램이 어떤 상태를 가정하는지 다른 개발자에게 알려주는 소통 도구**라는 데 있다. 단, **남발은 금물** — '반드시 참이어야 하는' 것만 검사한다. **프로그래머가 일으킬 오류**에만 쓰고, **외부에서 읽어 온 데이터 검사는 가정이 아니라 예외 처리로 대응**할 프로그램 로직이다.

**절차**:
1. 참이라고 가정하는 조건이 보이면 그 조건을 명시하는 **어서션을 추가**한다.

> 3항식에는 어서션 넣을 자리가 없으니 먼저 `if-then`으로 재구성한다. 어서션은 **세터**에 두는 편이 나을 때가 많다 — 사용 시점(`applyDiscount`)에 실패하면 "언제 처음 잘못됐나"를 다시 추적해야 하기 때문이다.

---

## 7. 제어 플래그를 탈출문으로 바꾸기 (10.7) — Replace Control Flag with Break

흐름을 제어하는 **플래그 변수**를, `break`·`continue`·`return`으로 바꿔 없앤다.

> 1판에서의 이름: 제어 플래그 제거

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before: found 플래그로 흐름 제어
for (const p of people) {
  if (!found) {
    if (p === "조커") {
      sendAlert();
      found = true;
    }
  }
}
// after: break로 탈출
for (const p of people) {
  if (p === "조커") {
    sendAlert();
    break;
  }
}
```

</details>

**배경**: 제어 플래그란 코드 동작을 바꾸는 변수로, 한 곳에서 설정하고 다른 곳 조건문에서 검사하는 형태다. 이런 코드는 **항상 악취**다 — `break`·`continue`에 익숙하지 않거나, `return`을 하나로 유지하려는 사람이 심어 놓는다. **함수에서 할 일을 다 마쳤다면 `return`으로 명확히 알리는 편이 낫다.**

**절차**:
1. 제어 플래그를 쓰는 코드를 **함수로 추출(6.1)**할지 고려한다(관련 코드만 떼어 보기 위해).
2. 플래그를 갱신하는 코드를 각각 적절한 **제어문(`return`·`break`·`continue`)**으로 바꾼다(하나씩 테스트).
3. 모두 수정했으면 **제어 플래그를 제거**한다.

```typescript
// 정리 후: 결국 컬렉션 파이프라인으로 (8.8) 더 간명해진다
function checkForMiscreants(people: string[]): void {
  if (people.some((p) => ["조커", "사루만"].includes(p))) {
    sendAlert();
  }
}
```

---

## 요약

- **조건문 분해하기(10.1)**: 조건식·조건절을 의도가 드러나는 함수로 — '무엇'이 아닌 '왜'를 말하게.
- **조건식 통합하기(10.2)**: 동작이 같은 검사들을 `||`(순차)·`&&`(중첩)로 합쳐 함수 추출로 잇는다(진짜 독립 검사는 제외).
- **중첩 조건문을 보호 구문으로(10.3)**: 한쪽만 정상인 조건은 먼저 빠져나가게 — 반환점 하나 규칙에 얽매이지 말라.
- **조건부 로직을 다형성으로(10.4)**: 타입별 분기를 클래스 + 다형성으로(기본은 슈퍼, 변형은 서브의 차이만) — 강력하되 남용 주의.
- **특이 케이스 추가하기(10.5)**: 특정 값(널)의 똑같은 처리를 특이 케이스 객체로 모은다 — 널 객체 패턴.
- **어서션 추가하기(10.6)**: 코드의 가정을 명시하는 소통 도구 — 프로그래머 오류에만, 남발 금지.
- **제어 플래그를 탈출문으로(10.7)**: 흐름 제어 플래그는 악취 — `return`·`break`·`continue`로 없앤다.
