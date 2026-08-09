# Chapter 11: Refactoring APIs (API 리팩터링)

## 핵심 질문

좋은 API는 조회와 갱신을 어떻게 구분하는가? 값만 다른 함수들, 동작 모드만 바꾸는 플래그 인수는 어떻게 정리하는가? 매개변수로 넘길지(호출자 결정) 함수가 알아내게 할지(피호출 함수 결정)의 균형은 무엇이 가르는가? 객체를 언제 불변으로 만들고, 생성자 대신 팩터리를 쓰는가? 함수를 명령 객체로 승격하면 무엇을 얻는가? 오류는 코드로 반환할지 예외로 던질지, 예외는 언제 사전 확인으로 대체하는가?

---

## 0. 이 장에서 다루는 것 · 코드 표기 규약

API는 모듈·함수라는 빌딩 블록을 끼워 맞추는 연결부다. 조회와 갱신이 섞이면 **질의/변경 함수 분리(11.1)**, 값만 다른 함수들은 **함수 매개변수화(11.2)**, 동작 모드용 인수는 **플래그 인수 제거(11.3)**, 필요 이상으로 분해된 데이터는 **객체 통째로 넘기기(11.4)**로 정리한다. 결정 주체의 균형은 **매개변수를 질의로(11.5)**·**질의를 매개변수로(11.6)** 오간다. 불변을 위해 **세터 제거(11.7)**, 생성 유연성을 위해 **생성자를 팩터리로(11.8)**, 복잡한 함수는 **함수를 명령으로(11.9)**·다시 **명령을 함수로(11.10)** 바꾼다. 갱신은 **수정된 값 반환하기(11.11)**로 드러내고, 오류는 **오류 코드를 예외로(11.12)**·과한 예외는 **예외를 사전확인으로(11.13)** 다듬는다.

> **코드 표기 규약**: 원서 JavaScript를 `<details>`로 접어 두고 **TypeScript**를 병기한다. 각 기법은 **스케치(before→after) · 배경 · 절차** 형식이다.

---

## 1. 질의 함수와 변경 함수 분리하기 (11.1) — Separate Query from Modifier

**값을 반환하면서 부수효과도 있는 함수**를, 순수한 질의 함수와 변경 함수로 나눈다.

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before
function getTotalOutstandingAndSendBill() {
  const result = customer.invoices.reduce((total, each) => each.amount + total, 0);
  sendBill();
  return result;
}
// after
function totalOutstanding() {
  return customer.invoices.reduce((total, each) => each.amount + total, 0);
}
function sendBill() { emailGateway.send(formatBill(customer)); }
```

</details>

**배경**: **겉보기 부수효과 없이 값을 반환하는 함수**는 언제든 원하는 만큼 호출해도 되고, 호출 위치를 옮겨도 되며, 테스트하기 쉽다. 이를 위한 규칙이 **명령-질의 분리(CQS)** — "질의(읽기) 함수는 모두 부수효과가 없어야 한다". '**겉보기**'라 한 이유는, 캐싱처럼 객체 밖에서 관찰되지 않는 상태 변경은 허용되기 때문이다.

> **핵심 통찰**: 값을 반환하면서 부수효과도 있는 함수를 발견하면 **무조건** 분리를 시도한다.

**절차**:
1. 함수를 복제하고 **질의 목적**에 맞는 이름을 짓는다(반환하는 변수 이름이 단초).
2. 새 질의 함수에서 **부수효과를 모두 제거**한다.
3. 정적 검사를 수행한다.
4. 원래 함수를 호출하는 곳에서 반환값을 쓰면, **질의 함수 호출로 바꾸고 바로 아래에 원래 함수 호출을 추가**한다(하나씩 테스트).
5. 원래 함수에서 질의 관련 코드를 제거한다.
6. 테스트한다(이후 중복은 변경 함수가 질의 함수를 쓰도록 **알고리즘 교체(7.9)**로 정리).

---

## 2. 함수 매개변수화하기 (11.2) — Parameterize Function

**로직이 같고 리터럴 값만 다른** 함수들을, 그 값을 매개변수로 받는 하나로 합친다.

> 1판에서의 이름: 메서드를 매개변수로 전환

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before
function tenPercentRaise(aPerson) { aPerson.salary = aPerson.salary.multiply(1.1); }
function fivePercentRaise(aPerson) { aPerson.salary = aPerson.salary.multiply(1.05); }
// after
function raise(aPerson, factor) { aPerson.salary = aPerson.salary.multiply(1 + factor); }
```

</details>

**배경**: 다른 값만 매개변수로 받는 하나의 함수로 합치면 중복이 사라지고, 매개변수 값만 바꿔 여러 곳에서 쓸 수 있어 유용성이 커진다.

**절차**:
1. 비슷한 함수 중 하나를 선택한다.
2. **함수 선언 바꾸기(6.5)**로 리터럴을 매개변수로 추가한다.
3. 호출하는 곳 모두에 적절한 리터럴 값을 추가한다.
4. 테스트한다.
5. 매개변수를 사용하도록 본문을 수정한다(하나씩 테스트).
6. 비슷한 다른 함수 호출도 매개변수화된 함수로 전환한다.

**예시 — 범위(band) 로직 통합**: 하한·상한을 매개변수로 받는 `withinBand`로 세 함수를 합친다(중간 대역부터 시작하는 게 요령, 상한은 `Infinity` 활용).

```typescript
// before: bottomBand / middleBand / topBand — 로직이 비슷
// after: 하나로 통합
function baseCharge(usage: number): Money {
  if (usage < 0) {
    return usd(0);
  }
  const amount =
    withinBand(usage, 0, 100) * 0.03 +
    withinBand(usage, 100, 200) * 0.05 +
    withinBand(usage, 200, Infinity) * 0.07;
  return usd(amount);
}
function withinBand(usage: number, bottom: number, top: number): number {
  return usage > bottom ? Math.min(usage, top) - bottom : 0;
}
```

---

## 3. 플래그 인수 제거하기 (11.3) — Remove Flag Argument

호출자가 로직을 고르려고 넘기는 **플래그 인수**를, 각 동작을 하는 **명시적 함수**로 대체한다.

> 1판에서의 이름: 매개변수를 메서드로 전환

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before
bookConcert(aCustomer, true);
function bookConcert(aCustomer, isPremium) {
  if (isPremium) { /* 프리미엄 예약 */ } else { /* 일반 예약 */ }
}
// after
premiumBookConcert(aCustomer);
```

</details>

**배경**: 플래그 인수가 있으면 API의 함수 목록만 봐서는 기능 차이가 드러나지 않고, 넘길 값(`true`가 무슨 뜻?)도 알아내야 한다. 특정 기능 하나만 하는 명시적 함수가 훨씬 깔끔하다.

> **핵심 통찰**: 플래그 인수인지 아닌지는 **리터럴 여부**가 가른다 — 호출자가 **불리언 리터럴**을 건네고 그것으로 **제어 흐름을 결정**할 때만 플래그 인수다. 값이 데이터(`const isRush = determineIfRush(...)`)로 온다면 시그니처에 불만이 없다. 두 쓰임이 혼재하면, 데이터 사용 코드는 두고 명시적 함수를 추가로 제공한다.

**절차**:
1. 매개변수 값마다 대응하는 **명시적 함수**를 만든다(분배 조건문이면 **조건문 분해(10.1)**, 아니면 **래핑 함수**).
2. 원래 함수 호출을 각 리터럴에 대응하는 명시적 함수 호출로 바꾼다.

```typescript
// before: deliveryDate(anOrder, true) — true가 무슨 뜻인지 불명확
// after: 의도가 드러나는 명시적 함수
function deliveryDate(anOrder: Order, isRush: boolean): LocalDate {
  return isRush ? rushDeliveryDate(anOrder) : regularDeliveryDate(anOrder);
}
function rushDeliveryDate(anOrder: Order): LocalDate { /* ... */ }
function regularDeliveryDate(anOrder: Order): LocalDate { /* ... */ }
```

---

## 4. 객체 통째로 넘기기 (11.4) — Preserve Whole Object

레코드에서 **값 두어 개를 꺼내 넘기는** 대신, 레코드를 통째로 넘기고 함수 안에서 꺼내 쓴다.

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before
const low = aRoom.daysTempRange.low;
const high = aRoom.daysTempRange.high;
if (aPlan.withinRange(low, high)) { ... }
// after
if (aPlan.withinRange(aRoom.daysTempRange)) { ... }
```

</details>

**배경**: 레코드를 통째로 넘기면 (1) 함수가 더 다양한 데이터를 써도 매개변수 목록을 고칠 필요가 없고, (2) 목록이 짧아져 이해하기 쉽고, (3) 같은 데이터를 쓰는 함수들의 로직 중복을 없앤다. 단, 함수가 레코드 자체에 의존하길 원치 않으면(특히 다른 모듈) 하지 않는다.

> **핵심 통찰**: 어떤 객체에서 값 몇 개를 꺼내 그것만으로 뭔가 하는 로직은, **그 로직을 객체 안으로 넣으라는 악취**다. 또, 다른 객체의 메서드에 자신의 데이터 여러 개를 건넨다면 `this`만 넘기면 된다.

**절차**:
1. 원하는 매개변수를 받는 빈 함수를 만든다(검색 쉬운 임시 이름).
2. 새 함수 본문에서 원래 함수를 호출하며 매개변수를 매핑한다.
3. 정적 검사를 수행한다.
4. 모든 호출자를 새 함수로 전환한다(하나씩 테스트, **죽은 코드 제거(8.9)** 병행).
5. 원래 함수를 **인라인(6.2)**한다.
6. 새 함수의 이름을 정리하고 반영한다.

---

## 5. 매개변수를 질의 함수로 바꾸기 (11.5) — Replace Parameter with Query

피호출 함수가 **스스로 쉽게 알아낼 수 있는 값**을 넘기는 매개변수를 제거한다. (반대: 11.6)

> 1판에서의 이름: 매개변수 세트를 메서드로 전환

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before
availableVacation(anEmployee, anEmployee.grade);
function availableVacation(anEmployee, grade) { /* 휴가 계산 */ }
// after
availableVacation(anEmployee);
function availableVacation(anEmployee) {
  const grade = anEmployee.grade;
  // 휴가 계산
}
```

</details>

**배경**: 매개변수 목록은 짧을수록 이해하기 쉽고, 중복은 피해야 한다. 피호출 함수가 쉽게 결정할 수 있는 값을 넘기는 건 의미 없이 호출자만 복잡하게 한다. 다른 매개변수로부터 얻을 수 있는 값이라면 안심하고 바꾼다. 단, **제거하면 원치 않는 의존성이 생기거나** 참조 투명성을 잃는다면(가변 전역 변수 사용 등) 하지 않는다.

**절차**:
1. 필요하면 매개변수 값을 계산하는 코드를 함수로 **추출(6.1)**한다.
2. 본문의 매개변수 참조를 그 값을 만드는 표현식으로 바꾼다(하나씩 테스트).
3. **함수 선언 바꾸기(6.5)**로 매개변수를 없앤다.

---

## 6. 질의 함수를 매개변수로 바꾸기 (11.6) — Replace Query with Parameter

함수 안의 **거북한 참조**(전역 변수 등)를 매개변수로 바꿔, 참조를 푸는 책임을 호출자로 옮긴다. (반대: 11.5)

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before: 전역 thermostat에 의존
function targetTemperature(aPlan) {
  const currentTemperature = thermostat.currentTemperature;
  // ...
}
// after: 매개변수로 받아 의존성을 끊음
function targetTemperature(aPlan, currentTemperature) { /* ... */ }
```

</details>

**배경**: 함수가 전역 변수나 제거하고 싶은 원소를 참조하면, 그 참조를 매개변수로 바꿔 의존성을 끊는다. 그러면 **참조 투명성**(같은 입력 → 항상 같은 결과)을 얻어 테스트·이해가 쉬워진다.

> **핵심 통찰**: 이 리팩터링은 균형의 문제다 — 모든 것을 매개변수로 바꾸면 목록이 길고 반복적이 되고, 다 공유하면 결합이 커진다. 호출자가 복잡해지는 단점이 있지만, **모듈을 참조 투명하게(순수 함수로)** 만드는 이득이 대체로 크다. JS는 불변을 강제하지 못하지만, **불변으로 설계했음을 알리고 그렇게 쓰라고 제안하는 것만으로도** 값어치를 한다.

**절차**:
1. **변수 추출(6.3)**로 질의 코드를 나머지와 분리한다.
2. 질의를 호출하지 않는 코드를 함수로 **추출(6.1)**한다(검색 쉬운 이름).
3. 추출에 쓴 변수를 **인라인(6.4)**한다.
4. 원래 함수를 **인라인(6.2)**한다.
5. 새 함수의 이름을 원래 이름으로 바꾼다.

---

## 7. 세터 제거하기 (11.7) — Remove Setting Method

생성 후 **변경되면 안 되는 필드**의 세터를 없애 불변임을 명확히 한다.

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before
class Person { get name() {...} set name(aString) {...} }
// after: name을 불변으로 (세터 제거)
class Person { get name() {...} }
```

</details>

**배경**: 세터가 있다는 건 필드가 수정될 수 있다는 뜻이다. 생성 후 불변이길 원하면 세터를 없애 의도를 분명히 한다. 필요한 상황은 둘 — (1) 무조건 접근자로만 필드를 다루려다 **생성자에서만 호출하는 세터**가 생겼을 때, (2) 생성자 호출 후 세터로 완성하는 **생성 스크립트**를 쓸 때.

**절차**:
1. 값을 생성자에서 받지 않으면 **함수 선언 바꾸기(6.5)**로 생성자 매개변수를 추가하고, 생성자 안에서 세터를 호출한다.
2. 생성자 밖의 세터 호출을 제거하고 새 생성자를 쓰게 한다(하나씩 테스트). 공유 참조 객체라 새 객체 생성으로 대체할 수 없으면 이 리팩터링을 취소한다.
3. 세터를 **인라인(6.2)**하고 가능하면 필드를 불변으로 만든다.
4. 테스트한다.

---

## 8. 생성자를 팩터리 함수로 바꾸기 (11.8) — Replace Constructor with Factory Function

생성자의 제약을 벗어나기 위해 **팩터리 함수**로 객체 생성을 감싼다.

> 1판에서의 이름: 생성자를 팩토리 메서드로 전환

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before
leadEngineer = new Employee(document.leadEngineer, 'E');
// after
leadEngineer = createEngineer(document.leadEngineer);
function createEngineer(name) { return new Employee(name, 'E'); }
```

</details>

**배경**: 생성자에는 제약이 있다 — 정의한 클래스의 인스턴스만 반환(서브클래스·프락시 불가), 이름 고정, `new` 연산자 필요. 팩터리 함수에는 이런 제약이 없어, 서브클래스를 반환하거나 더 나은 이름을 쓸 수 있다.

**절차**:
1. 팩터리 함수를 만들고 본문에서 원래 생성자를 호출한다.
2. 생성자 호출을 팩터리 함수 호출로 바꾼다(하나씩 테스트).
3. 생성자의 가시 범위를 최소로 제한한다.

> 문자열 리터럴을 함수에 건네는 것(`createEmployee(name, 'E')`)은 악취다 — 유형을 **팩터리 함수 이름에 녹여**(`createEngineer(name)`) 의도를 드러낸다.

---

## 9. 함수를 명령으로 바꾸기 (11.9) — Replace Function with Command

함수를 **그 함수만을 위한 객체(명령 객체)**로 캡슐화한다. (반대: 11.10)

> 1판에서의 이름: 메서드를 메서드 객체로 전환

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before
function score(candidate, medicalExam, scoringGuide) { /* 긴 코드 */ }
// after
class Scorer {
  constructor(candidate, medicalExam, scoringGuide) { /* 필드 저장 */ }
  execute() { /* 긴 코드 */ }
}
```

</details>

**배경**: 함수를 객체로 캡슐화한 **명령 객체**는 평범한 함수보다 유연하다 — `undo` 같은 보조 연산, 수명주기 제어, 상속·훅으로 맞춤화, 그리고 **복잡한 함수를 필드와 메서드로 잘게 쪼개기**가 가능하다.

> **핵심 통찰**: 유연성은 복잡성을 키우고 얻는 대가다. **일급 함수와 명령 중 고른다면 95%는 일급 함수**를 택한다 — 명령은 더 간단한 방식으로 얻을 수 없는 기능이 필요할 때만 쓴다.

**절차**:
1. 대상 함수의 기능을 옮길 빈 클래스를 만든다(이름은 함수 기반).
2. 함수를 그 클래스로 **옮긴다(8.1)**(실행 메서드는 `execute`·`call` 등, 원래 함수는 전달 함수로 남김).
3. 함수의 인수 각각을 명령의 **필드로 만들어 생성자에서 설정**할지 고민한다.

> 인수를 생성자로 옮겨 `execute()`가 매개변수를 안 받게 하면, 매개변수가 다른 여러 명령을 하나의 **실행 대기열**로 전달할 수 있다. 이후 **지역 변수를 필드로** 바꾸면 유효 범위에 구애받지 않고 **함수 추출(6.1)**로 복잡한 로직을 쪼갤 수 있다(서브함수를 테스트·디버깅에 활용).

---

## 10. 명령을 함수로 바꾸기 (11.10) — Replace Command with Function

로직이 복잡하지 않은 **명령 객체**를 평범한 함수로 되돌린다. (반대: 11.9)

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before
class ChargeCalculator {
  constructor(customer, usage) { this._customer = customer; this._usage = usage; }
  execute() { return this._customer.rate * this._usage; }
}
// after
function charge(customer, usage) { return customer.rate * usage; }
```

</details>

**배경**: 명령 객체의 능력은 공짜가 아니다. 명령이 그저 함수 하나 호출 용도로 쓰이고 로직이 크게 복잡하지 않다면, 장점보다 단점이 크니 평범한 함수로 바꾸는 게 낫다.

**절차**:
1. 명령을 생성하는 코드와 실행 메서드 호출을 함께 함수로 **추출(6.1)**한다.
2. 실행 함수가 호출하는 보조 메서드들을 **인라인(6.2)**한다(값을 반환하면 **변수 추출(6.3)** 먼저).
3. **함수 선언 바꾸기(6.5)**로 생성자 매개변수를 실행 메서드로 옮긴다.
4. 필드 참조 대신 대응하는 매개변수를 쓰게 한다(하나씩 테스트).
5. 생성자 호출과 실행 메서드 호출을 대체 함수 안으로 인라인한다.
6. 테스트한다.
7. **죽은 코드 제거(8.9)**로 명령 클래스를 없앤다.

---

## 11. 수정된 값 반환하기 (11.11) — Return Modified Value

변수를 **갱신하는 함수**가 수정된 값을 반환하게 해, 호출자가 변수에 담게 한다.

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before: 외부 변수를 몰래 갱신
let totalAscent = 0;
calculateAscent();
function calculateAscent() {
  for (let i = 1; i < points.length; i++) {
    const verticalChange = points[i].elevation - points[i - 1].elevation;
    totalAscent += verticalChange > 0 ? verticalChange : 0;
  }
}
// after: 값을 반환해 갱신을 드러냄
const totalAscent = calculateAscent();
function calculateAscent() {
  let result = 0;
  for (let i = 1; i < points.length; i++) {
    const verticalChange = points[i].elevation - points[i - 1].elevation;
    result += verticalChange > 0 ? verticalChange : 0;
  }
  return result;
}
```

</details>

**배경**: 데이터가 어떻게 수정되는지 추적하기는 코드에서 가장 어려운 일 중 하나다. 갱신하는 함수가 **수정된 값을 반환**하면, 호출자 코드만 읽어도 변수가 갱신됨을 분명히 알 수 있다. **값 하나를 계산하는 함수**에 효과적이고(여러 값 갱신에는 부적합), **함수 옮기기(8.1)**의 준비 작업으로 좋다.

**절차**:
1. 함수가 수정된 값을 반환하게 해 호출자가 변수에 저장하게 한다.
2. 테스트한다.
3. 피호출 함수 안에 반환값을 담을 새 변수(`result`)를 선언한다(호출자 초깃값을 바꿔 무시되는지 검사 가능).
4. 테스트한다.
5. 선언과 계산을 통합하고(`const`), 가능하면 불변으로 만든다.
6. 변수 이름을 새 역할에 맞게 바꾼다.

---

## 12. 오류 코드를 예외로 바꾸기 (11.12) — Replace Error Code with Exception

오류를 나타내는 **반환 코드**를, 독립적인 흐름을 갖는 **예외**로 바꾼다.

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before
if (data) return new ShippingRules(data);
else return -23;
// after
if (data) return new ShippingRules(data);
else throw new OrderProcessingError(-23);
```

</details>

**배경**: 예외는 독립적인 오류 처리 메커니즘으로, 오류 코드를 일일이 검사·전파하는 코드를 없애 준다. 단, **정확히 예상 밖의 동작**(정상 동작 범주에 들지 않는 오류)에만 써야 한다.

> **핵심 통찰**: 좋은 경험 법칙 — 예외를 던지는 코드를 **프로그램 종료 코드로 바꿔도 여전히 정상 동작할지** 따져 본다. 정상 동작하지 않을 것 같다면 예외를 쓰지 말라는 신호다(오류를 검출해 정상 흐름으로 되돌려야 한다).

**절차**:
1. 콜스택 상위에 예외 핸들러를 둔다(처음엔 모든 예외를 다시 던짐).
2. 테스트한다.
3. 이 예외를 다른 예외와 구분할 식별 방법을 찾는다(대개 `Error` 서브클래스).
4. 정적 검사를 수행한다.
5. `catch`절이 이 예외는 처리하고 나머지는 다시 던지게 한다.
6. 테스트한다.
7. 오류 코드를 반환하던 곳에서 예외를 던지게 한다(하나씩 테스트).
8. 오류 코드를 전파하던 코드를 제거한다 — 먼저 **함정(throw)**으로 바꿔 걸리지 않는지 확인한 뒤 **죽은 코드 제거(8.9)**.

```typescript
class OrderProcessingError extends Error {
  code: number;
  constructor(errorCode: number) {
    super(`주문 처리 오류: ${errorCode}`);
    this.code = errorCode;
  }
  get name(): string { return "OrderProcessingError"; }
}
function localShippingRules(country: string): ShippingRules {
  const data = countryData.shippingRules[country];
  if (data) {
    return new ShippingRules(data);
  }
  throw new OrderProcessingError(-23);
}
```

---

## 13. 예외를 사전확인으로 바꾸기 (11.13) — Replace Exception with Precheck

호출 전에 검사할 수 있는 조건이면, **예외를 던지는 대신 사전 확인**한다.

> 1판에서의 이름: 예외 처리를 테스트로 교체

<details>
<summary>원서 JavaScript/Java — 스케치</summary>

```java
// before
double getValueForPeriod(int periodNumber) {
  try { return values[periodNumber]; }
  catch (ArrayIndexOutOfBoundsException e) { return 0; }
}
// after
double getValueForPeriod(int periodNumber) {
  return (periodNumber >= values.length) ? 0 : values[periodNumber];
}
```

</details>

**배경**: 예외는 오류 코드 전파를 없앤 큰 진보지만, **과용되곤 한다**. 예외는 '뜻밖의 오류'라는 예외적 동작에만 써야 한다.

> **핵심 통찰**: 함수 수행 시 문제가 될 조건을 **함수 호출 전에 검사할 수 있다면**, 예외를 던지는 대신 호출하는 곳에서 조건을 검사하게 하라. (자원 풀이 고갈되는 것은 '예상치 못한 조건'이 아니므로 예외가 아니라 사전 확인 대상이다.)

**절차**:
1. 예외를 유발하는 상황을 검사하는 조건문을 추가한다 — `catch` 블록 코드를 한 조건절로, 남은 `try` 블록 코드를 다른 조건절로 옮긴다.
2. `catch` 블록에 **어서션(10.6)**을 추가하고 테스트한다(더는 도달하지 않음을 확인).
3. `try`/`catch`를 제거한다.
4. 테스트한다.

```typescript
// after: 예외 대신 사전 확인 (이후 문장 슬라이드·3항 정리로 더 깔끔해진다)
get(): Resource {
  const result = this.available.length === 0 ? Resource.create() : this.available.pop()!;
  this.allocated.push(result);
  return result;
}
```

---

## 요약

- **질의/변경 분리(11.1)**: 값 반환 + 부수효과면 무조건 나눈다(CQS).
- **함수 매개변수화(11.2)**: 리터럴만 다른 함수들을 매개변수 하나로 합친다.
- **플래그 인수 제거(11.3)**: 리터럴 불리언으로 로직을 고르는 인수를 명시적 함수로 — 데이터로 오면 두어도 된다.
- **객체 통째로 넘기기(11.4)**: 값 몇 개 대신 레코드를 통째로 — 값으로 뭔가 하는 로직은 객체 안으로.
- **매개변수를 질의로(11.5) ↔ 질의를 매개변수로(11.6)**: 결정 주체(호출자 vs 피호출 함수)의 균형 — 후자는 참조 투명성을 얻는다.
- **세터 제거(11.7)·생성자를 팩터리로(11.8)**: 불변을 명확히 하고, 생성자의 제약을 팩터리로 우회.
- **함수를 명령으로(11.9) ↔ 명령을 함수로(11.10)**: 유연성이 필요하면 명령 객체로, 과하면 함수로 — 기본은 일급 함수.
- **수정된 값 반환하기(11.11)**: 갱신을 반환값으로 드러내 데이터 흐름을 읽히게.
- **오류 코드를 예외로(11.12) ↔ 예외를 사전확인으로(11.13)**: 예상 밖 오류는 예외로, 호출 전 검사 가능한 조건은 사전 확인으로 — 예외 남용을 막는다.
