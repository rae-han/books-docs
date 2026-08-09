# Chapter 9: Organizing Data (데이터 조직화)

## 핵심 질문

한 변수가 여러 역할을 맡으면 왜 위험한가? 필드·게터·세터 이름은 어떻게 안전하게 바꾸는가? 저장해 둔 파생 값을 언제 계산으로 대체하는가? 중첩된 객체를 값으로 다룰지 참조로 다룰지는 무엇이 가르는가? 코드에 흩어진 리터럴은 어떻게 의미를 갖게 하는가?

---

## 0. 이 장에서 다루는 것 · 코드 표기 규약

데이터 구조는 프로그램에서 중요한 역할을 하므로, 데이터에 집중한 리팩터링만 따로 모았다. 하나의 값이 여러 목적으로 쓰이면 혼란과 버그를 낳으니 **변수 쪼개기(9.1)**로 나누고, 이름은 **필드 이름 바꾸기(9.2)**로 다듬으며, 변수 자체를 없애는 게 최선이면 **파생 변수를 질의 함수로 바꾸기(9.3)**를 쓴다. 참조냐 값이냐가 헷갈리면 **참조를 값으로(9.4)**·**값을 참조로(9.5)** 전환하고, 의미를 알기 어려운 리터럴은 **매직 리터럴 바꾸기(9.6)**로 명확히 한다.

> **코드 표기 규약**: 원서 JavaScript를 `<details>`로 접어 두고 **TypeScript**를 병기한다. 각 기법은 **스케치(before→after) · 배경 · 절차** 형식이다.

---

## 1. 변수 쪼개기 (9.1) — Split Variable

> 1판에서의 이름: 매개변수로의 값 대입 제거 / 임시변수 분리

**두 번 이상 대입되며 역할이 둘 이상인 변수**를, 역할 하나당 변수 하나로 나눈다.

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before: temp가 둘레와 넓이 두 역할
let temp = 2 * (height + width);
console.log(temp);
temp = height * width;
console.log(temp);
// after
const perimeter = 2 * (height + width);
console.log(perimeter);
const area = height * width;
console.log(area);
```

</details>

**배경**: 변수는 한 번만 대입해야 한다. 대입이 두 번 이상이면 **여러 역할을 수행한다는 신호**다 — 예외는 없다. 역할이 둘 이상인 변수는 읽는 이에게 큰 혼란을 주므로 쪼갠다. 단, **루프 변수**(`i`)나 **수집 변수**(`i = i + <무언가>` 형태로 총합·문자열 연결·컬렉션 추가 등에 쓰이는 변수)는 예외다.

**절차**:
1. 변수를 선언한 곳과 **첫 대입** 지점에서 변수 이름을 바꾼다.
2. 가능하면 이때 **불변(`const`)**으로 선언한다.
3. **두 번째 대입 전까지**의 모든 참조를 새 이름으로 바꾼다.
4. 두 번째 대입 지점에서 변수를 **원래 이름으로 다시 선언**한다.
5. 테스트한다.
6. 마지막 대입까지 반복한다(매번 새 이름으로 선언하고 다음 대입 전까지의 참조를 바꾼다).

**예시 — 입력 매개변수를 수정할 때**: 매개변수도 변수다. 입력 전달용과 결과 반환용으로 겸용된 매개변수를 쪼갠다(JS 매개변수는 값에 의한 호출이라 수정해도 호출자에 영향 없음).

```typescript
// before: inputValue가 '입력'과 '결과'를 겸함
function discount(inputValue: number, quantity: number): number {
  if (inputValue > 50) {
    inputValue = inputValue - 2;
  }
  if (quantity > 100) {
    inputValue = inputValue - 1;
  }
  return inputValue;
}
```

```typescript
// after: 결과용 변수 result를 분리 (첫 비교는 그대로 inputValue를 참조 — 입력값 기반 누적임을 드러냄)
function discount(inputValue: number, quantity: number): number {
  let result = inputValue;
  if (inputValue > 50) {
    result = result - 2;
  }
  if (quantity > 100) {
    result = result - 1;
  }
  return result;
}
```

---

## 2. 필드 이름 바꾸기 (9.2) — Rename Field

레코드·클래스의 **필드(및 게터·세터) 이름**을 더 잘 드러나게 바꾼다.

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before
class Organization { get name() {...} }
// after
class Organization { get title() {...} }
```

</details>

**배경**: 데이터 구조는 프로그램을 이해하는 열쇠이므로 그 필드 이름은 특히 중요하다. 게터·세터는 사용자 입장에서 필드와 다를 바 없으니, 접근자 이름 바꾸기도 필드 이름 바꾸기만큼 중요하다.

> 데이터 테이블 없이 흐름도만 보여줘서는 나는 여전히 혼란스러울 것이다. 하지만 데이터 테이블을 보여준다면 흐름도는 웬만해선 필요조차 없을 것이다 — 테이블만으로 명확하기 때문이다.<br>— 프레드 브룩스(Fred Brooks)

**절차**:
1. 레코드의 **유효 범위가 좁으면** 필드에 접근하는 모든 코드를 직접 수정하고 테스트한다(이후 단계 불필요).
2. 레코드가 캡슐화되지 않았다면 **레코드 캡슐화(7.1)**한다.
3. 캡슐화된 객체 안의 **private 필드명**을 바꾸고 내부 메서드를 맞춘다.
4. 테스트한다.
5. 생성자 매개변수 중 이름이 겹치면 **함수 선언 바꾸기(6.5)**로 바꾼다.
6. 접근자들의 이름도 **바꾼다(6.5)**.

> 널리 참조되는 데이터 구조라면, 캡슐화 후 **생성자가 옛 이름과 새 이름을 모두 받도록**(`data.title ?? data.name`) 한 뒤 호출처를 하나씩 새 이름으로 옮기고, 마지막에 옛 이름 지원 코드를 제거한다 — 모든 변경을 한 번에 하는 대신 작은 단계로 나눠 독립적으로 수행하는 것이다.

---

## 3. 파생 변수를 질의 함수로 바꾸기 (9.3) — Replace Derived Variable with Query

**계산으로 구할 수 있는 값을 저장해 둔 변수**를 없애고, 그 값을 계산하는 질의 함수로 대체한다.

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before: discountedTotal을 저장하고 discount 세터에서 함께 갱신
get discountedTotal() { return this._discountedTotal; }
set discount(aNumber) {
  const old = this._discount;
  this._discount = aNumber;
  this._discountedTotal += old - aNumber;
}
// after: 저장하지 않고 계산
get discountedTotal() { return this._baseTotal - this._discount; }
set discount(aNumber) { this._discount = aNumber; }
```

</details>

**배경**: 가변 데이터는 소프트웨어의 가장 큰 골칫거리다 — 한쪽 수정이 연쇄 효과로 다른 쪽에 원인 찾기 어려운 문제를 만든다. 쉽게 계산할 수 있는 변수를 제거하면 가변 데이터의 유효 범위가 좁아지고, 값을 갱신하며 반영을 깜빡하는 실수도 막는다. **예외**: 피연산자가 불변이면 계산 결과도 일정하므로, 새 데이터 구조를 만드는 **변형 연산**은 그대로 둬도 좋다.

**절차**:
1. 변수 값이 **갱신되는 지점을 모두** 찾는다(필요하면 **변수 쪼개기(9.1)**로 분리).
2. 그 값을 계산하는 함수를 만든다.
3. 변수가 사용되는 곳에 **어서션(10.6)**을 추가해 함수 계산 결과가 변수 값과 같은지 확인한다.
4. 테스트한다.
5. 변수를 읽는 코드를 모두 함수 호출로 대체한다.
6. 테스트하고, 변수를 선언·갱신하던 코드를 **죽은 코드 제거(8.9)**로 없앤다.

**예시**: 조정 값을 누적하며 `_production`까지 갱신하던 코드를, `_adjustments`로부터 계산하도록 바꾼다.

```typescript
// before: 데이터 중복 — production을 매번 갱신
class ProductionPlan {
  get production(): number {
    return this._production;
  }
  applyAdjustment(anAdjustment: Adjustment): void {
    this._adjustments.push(anAdjustment);
    this._production += anAdjustment.amount;
  }
}
```

```typescript
// after: 저장 대신 계산 (어서션으로 안전을 확인한 뒤 필드 제거)
class ProductionPlan {
  get production(): number {
    return this._adjustments.reduce((sum, a) => sum + a.amount, 0);
  }
  applyAdjustment(anAdjustment: Adjustment): void {
    this._adjustments.push(anAdjustment);
  }
}
```

> 소스가 둘 이상이면(초깃값 + 누적값) 먼저 **변수 쪼개기(9.1)**로 `_initialProduction`과 `_productionAccumulator`로 나눈 뒤, 누적값만 계산으로 대체한다(이 경우 계산 함수는 인라인하지 않고 속성으로 남겨 두는 편이 낫다).

---

## 4. 참조를 값으로 바꾸기 (9.4) — Change Reference to Value

중첩된 객체를 **불변 값 객체**로 만들어, 속성 수정 대신 **객체 통째로 교체**하게 한다. (반대: 9.5)

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before: 내부 객체의 속성을 직접 수정
class Product {
  applyDiscount(arg) { this._price.amount -= arg; }
}
// after: 새 값 객체로 통째 교체
class Product {
  applyDiscount(arg) {
    this._price = new Money(this._price.amount - arg, this._price.currency);
  }
}
```

</details>

**배경**: 참조로 다루면 내부 객체는 그대로 둔 채 속성만 갱신하고, 값으로 다루면 새 객체로 통째 대체한다. 값 객체는 **불변**이라 다루기 쉽다 — 외부로 건네도 몰래 바뀔 염려가 없고, 복제해 써도 참조를 관리할 필요가 없어 **분산·동시성 시스템에 특히 유용**하다. 단, 객체를 **여러 곳에서 공유하며 변경을 전파**해야 한다면 참조로 다뤄야 하므로 이 리팩터링을 적용하면 안 된다.

**절차**:
1. 후보 클래스가 **불변인지, 불변이 될 수 있는지** 확인한다.
2. 각 세터를 하나씩 **제거(11.7)**한다(세터로 설정하던 필드를 생성자에서 받도록).
3. 값 기반 **동치성 비교 메서드**를 만든다(대개 해시코드 생성 메서드도 함께 오버라이드).

**예시**: `Person`에서 추출된 `TelephoneNumber`를 값 객체로 만든다. JS는 값 기반 동치성을 언어 차원에서 지원하지 않으므로 `equals`를 직접 작성한다.

```typescript
class TelephoneNumber {
  constructor(
    private readonly _areaCode: string,
    private readonly _number: string,
  ) {}
  get areaCode(): string { return this._areaCode; }
  get number(): string { return this._number; }
  // 값 기반 동치성 — 독립 생성한 두 객체가 같은 값이면 true
  equals(other: unknown): boolean {
    if (!(other instanceof TelephoneNumber)) {
      return false;
    }
    return this.areaCode === other.areaCode && this.number === other.number;
  }
}
```

```typescript
// Person의 세터는 전화번호를 매번 새로 대입한다 (불변 값이므로)
class Person {
  set officeAreaCode(arg: string) {
    this._telephoneNumber = new TelephoneNumber(arg, this.officeNumber);
  }
  set officeNumber(arg: string) {
    this._telephoneNumber = new TelephoneNumber(this.officeAreaCode, arg);
  }
}
```

---

## 5. 값을 참조로 바꾸기 (9.5) — Change Value to Reference

논리적으로 같은 엔티티의 **여러 복제본**을, 저장소를 통해 얻는 **단일 참조**로 바꾼다. (반대: 9.4)

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before: 주문마다 고객 객체를 새로 생성 (복제본)
let customer = new Customer(customerData);
// after: 저장소에서 공유 객체를 얻음
let customer = customerRepository.get(customerData.id);
```

</details>

**배경**: 같은 데이터를 물리적으로 복제해 쓰다가 **그 데이터를 갱신해야 할 때** 가장 크게 문제된다 — 모든 복제본을 빠짐없이 갱신해야 하고, 하나라도 놓치면 일관성이 깨진다. 값을 참조로 바꾸면 **엔티티 하나당 객체도 하나**가 되어, 갱신이 관련된 모든 곳에 곧바로 반영된다. 이때 보통 객체들을 모아 접근을 관리하는 **저장소(repository)**가 필요해진다.

**절차**:
1. 같은 부류의 객체들을 보관할 **저장소**를 만든다(이미 있으면 생략).
2. 생성자에서 **특정 객체를 정확히 찾아내는 방법**이 있는지 확인한다.
3. 호스트 객체의 생성자가 저장소에서 객체를 찾도록 수정한다(하나씩 테스트).

**예시**: 주문마다 `new Customer(id)`로 만들던 고객을, ID당 하나만 보장하는 저장소에서 얻게 한다.

```typescript
// 저장소: ID 하나당 고객 객체 하나만 생성됨을 보장
const customers = new Map<string, Customer>();
export function registerCustomer(id: string): Customer {
  if (!customers.has(id)) {
    customers.set(id, new Customer(id));
  }
  return customers.get(id)!;
}
```

```typescript
class Order {
  constructor(data: OrderData) {
    this._number = data.number;
    // new Customer(...) 대신 저장소에서 공유 객체를 얻는다
    this._customer = registerCustomer(data.customer);
  }
  get customer(): Customer { return this._customer; }
}
```

> **핵심 통찰**: 이 예시는 생성자가 **전역 저장소와 결합**되는 문제가 있다. 전역 객체는 독한 약과 같아, 소량은 이롭지만 과용하면 독이 된다. 염려되면 저장소를 **생성자 매개변수로 주입**(의존성 주입)한다.

---

## 6. 매직 리터럴 바꾸기 (9.6) — Replace Magic Literal

의미를 알기 어려운 리터럴을 **이름 있는 상수**로 바꾼다.

> 1판에서의 이름: 마법 숫자를 기호 상수로 전환

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before
function potentialEnergy(mass, height) {
  return mass * 9.81 * height;
}
// after
const STANDARD_GRAVITY = 9.81;
function potentialEnergy(mass, height) {
  return mass * STANDARD_GRAVITY * height;
}
```

</details>

**배경**: 매직 리터럴이란 소스 코드에 등장하는, 그 자체로는 의미를 명확히 알려주지 못하는 리터럴 값이다(`9.81`이 표준중력임을 코드가 말해 주지 않는다). 숫자가 많지만 문자열·날짜도 특별한 의미를 지닐 수 있다(`"M"`=남성, `"서울"`=본사). 값이 쓰이는 모든 곳을 적절한 이름의 상수로 바꾸는 게 일반적이다.

> **핵심 통찰**: 비교 로직에 주로 쓰이는 값이라면 상수보다 **함수 호출**이 낫다 — `aValue === MALE_GENDER`보다 `isMale(aValue)`를 선호한다. 반대로 `const ONE = 1` 같은 상수는 의미 전달에 도움이 안 되니(값이 달라질 리도 없다) **과용을 피한다**. 함수 하나에서만 쓰이고 맥락이 충분하면 상수로 얻는 이득이 줄어든다.

**절차**:
1. 상수를 선언하고 매직 리터럴을 대입한다.
2. 그 리터럴이 사용되는 곳을 모두 찾는다.
3. 각 사용처에서 **같은 의미로 쓰였는지 확인**하여, 같으면 상수로 대체하고 테스트한다.

> **테스트 팁**: 상수의 **값을 일부러 바꿔 보고**, 관련 테스트 모두가 바뀐 값에 해당하는 결과를 내는지 확인하면 대체가 제대로 됐는지 검증할 수 있다.

---

## 요약

- **변수 쪼개기(9.1)**: 두 번 이상 대입되며 역할이 둘인 변수를 나눈다(역할 하나당 변수 하나). 루프·수집 변수는 예외.
- **필드 이름 바꾸기(9.2)**: 데이터 구조는 이해의 열쇠 — 필드·접근자 이름을 캡슐화 후 작은 단계로 바꾼다.
- **파생 변수를 질의 함수로(9.3)**: 계산 가능한 값의 저장을 없애 가변 데이터를 줄인다 — 어서션으로 안전을 확인하고 전환.
- **참조를 값으로(9.4) ↔ 값을 참조로(9.5)**: 반대 짝. 불변 값 객체로 통째 교체할지(공유·전파 불필요), 저장소로 단일 참조를 공유할지(갱신 전파 필요)를 상황이 가른다.
- **매직 리터럴 바꾸기(9.6)**: 의미 없는 리터럴을 이름 있는 상수로 — 비교용이면 함수가 낫고, 과용은 피한다.
