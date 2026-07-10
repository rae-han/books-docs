# Chapter 12: Dealing with Inheritance (상속 다루기)

## 핵심 질문

기능을 상속 계층의 위·아래로 언제 올리고 내리는가? 타입 코드는 언제 서브클래스로 승격하고, 언제 서브클래스를 걷어내는가? 비슷한 두 클래스에서 공통 슈퍼클래스를 어떻게 뽑아내는가? "상속보다 컴포지션"은 상속을 쓰지 말라는 뜻인가? 상속이 잘못 끼워졌을 때 어떻게 위임으로 갈아타는가?

---

## 0. 이 장에서 다루는 것 · 코드 표기 규약

마지막 장은 객체 지향의 가장 유명한(그리고 오용하기 쉬운) 특성인 **상속**을 다룬다. 기능을 계층 위아래로 옮기는 **메서드/필드 올리기(12.1·12.2)·생성자 본문 올리기(12.3)·메서드/필드 내리기(12.4·12.5)**, 계층에 클래스를 더하거나 빼는 **슈퍼클래스 추출(12.8)·서브클래스 제거(12.7)·계층 합치기(12.9)**, 필드 값에 따라 동작이 달라지면 **타입 코드를 서브클래스로 바꾸기(12.6)**, 상속이 잘못 끼워졌으면 **서브클래스를 위임으로(12.10)·슈퍼클래스를 위임으로(12.11)** 바꾼다.

> **코드 표기 규약**: 원서 JavaScript를 `<details>`로 접어 두고 **TypeScript**를 병기한다. 각 기법은 **스케치(before→after) · 배경 · 절차** 형식이다. (일부 예제는 원서가 Java로 제시한 것을 TS로 각색했다.)

---

## 1. 메서드 올리기 (12.1) — Pull Up Method

여러 서브클래스에 **똑같이 동작하는 메서드**를 슈퍼클래스로 올려 중복을 없앤다. (반대: 12.4)

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before: 두 서브클래스에 같은 name()
class Salesperson extends Employee { get name() {...} }
class Engineer extends Employee { get name() {...} }
// after
class Employee { get name() {...} }
```

</details>

**배경**: 중복된 두 메서드는 한쪽 변경이 다른 쪽에 반영되지 않을 위험을 늘 수반한다. 본문이 똑같으면 그냥 복사해 올리면 되지만, 세상은 그리 만만치 않다 — **차이점을 찾는 방법**이 테스트가 놓친 동작까지 알려 줘 효과가 좋다. 참조하는 필드가 서브클래스에만 있으면 **필드 먼저 올리고(12.2)** 메서드를 올린다. 전체 흐름은 비슷하나 세부가 다르면 **템플릿 메서드**를 고려한다.

**절차**:
1. 메서드들이 똑같이 동작하는지 살핀다(실질은 같고 코드가 다르면 같아질 때까지 리팩터링).
2. 메서드가 호출·참조하는 것을 슈퍼클래스에서도 접근할 수 있는지 확인한다.
3. 시그니처가 다르면 **함수 선언 바꾸기(6.5)**로 통일한다.
4. 슈퍼클래스에 메서드를 만들고 코드를 복사한다.
5. 정적 검사를 수행한다.
6. 서브클래스 하나의 메서드를 제거한다.
7. 테스트한다.
8. 모든 서브클래스의 메서드가 없어질 때까지 반복한다.

> 슈퍼클래스가 구현하지 않은 메서드(예: `monthlyCost`)를 서브클래스가 반드시 구현해야 함을 알리려면 **함정 메서드**를 둔다 — `throw new SubclassResponsibilityError()`(스몰토크에서 유래한 **서브클래스 책임 오류**).

---

## 2. 필드 올리기 (12.2) — Pull Up Field

여러 서브클래스에 **중복된 필드**를 슈퍼클래스로 올린다. (반대: 12.5)

<details>
<summary>원서 Java — 스케치</summary>

```java
// before
class Salesperson extends Employee { private String name; }
class Engineer extends Employee { private String name; }
// after
class Employee { protected String name; }
```

</details>

**배경**: 서브클래스들이 독립적으로 개발되었거나 뒤늦게 하나의 계층으로 묶이면 필드가 중복되기 쉽다. 필드들이 비슷하게 쓰이면 올려서 (1) 데이터 중복 선언을 없애고, (2) 그 필드를 쓰는 동작도 슈퍼클래스로 옮길 수 있다.

**절차**:
1. 후보 필드들이 모두 **똑같은 방식으로 쓰이는지** 살핀다.
2. 이름이 다르면 **필드 이름 바꾸기(9.2)**로 통일한다.
3. 슈퍼클래스에 필드를 만든다(서브클래스가 접근하게 대개 `protected`).
4. 서브클래스의 필드들을 제거한다.
5. 테스트한다.

> 동적 언어(JS)는 필드를 클래스 정의에 두지 않고 **처음 값이 대입될 때** 등장하는 경우가 많으므로, 필드를 올리기 전에 **생성자 본문부터 올려야(12.3)** 한다.

---

## 3. 생성자 본문 올리기 (12.3) — Pull Up Constructor Body

서브클래스 생성자들의 **공통 초기화 코드**를 슈퍼클래스 생성자로 올린다.

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before: 서브클래스마다 this._name = name
class Employee extends Party {
  constructor(name, id, monthlyCost) {
    super();
    this._id = id;
    this._name = name;
    this._monthlyCost = monthlyCost;
  }
}
// after: 이름 대입을 슈퍼클래스로
class Employee extends Party {
  constructor(name, id, monthlyCost) {
    super(name);
    this._id = id;
    this._monthlyCost = monthlyCost;
  }
}
```

</details>

**배경**: 생성자는 일반 메서드와 달리 **할 수 있는 일과 호출 순서에 제약**이 있어 다르게 접근해야 한다. 이 리팩터링이 간단히 끝날 것 같지 않으면 **생성자를 팩터리 함수로 바꾸기(11.8)**를 고려한다.

**절차**:
1. 슈퍼클래스에 생성자가 없으면 만들고, 서브클래스 생성자가 이를 호출하는지 확인한다.
2. **문장 슬라이드하기(8.6)**로 공통 문장을 `super()` 호출 직후로 옮긴다.
3. 공통 코드를 슈퍼클래스에 추가하고 서브클래스에서 제거한다(참조 값은 `super()`로 전달).
4. 테스트한다.
5. 생성자 시작부로 옮길 수 없는 공통 코드는 **함수 추출(6.1)** 후 **메서드 올리기(12.1)**.

> 공통 작업이 **뒤에 와야 할 때**(예: 서브클래스만 값을 넣는 필드에 의존하는 `if (this.isPrivileged) this.assignCar()`)는, 그 부분을 `finishConstruction()`으로 추출한 뒤 슈퍼클래스로 올린다.

---

## 4. 메서드 내리기 (12.4) — Push Down Method

**특정 서브클래스에서만 쓰는 메서드**를 슈퍼클래스에서 내린다. (반대: 12.1)

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before
class Employee { get quota() {...} }
// after: Salesperson만 사용
class Salesperson extends Employee { get quota() {...} }
```

</details>

**배경**: 특정 서브클래스 하나(혹은 소수)와만 관련된 메서드는 그 서브클래스로 내리는 편이 깔끔하다. 단, **호출자가 어느 서브클래스인지 알 때만** 적용한다 — 그렇지 못하면 **조건부 로직을 다형성으로 바꿔야(10.4)** 한다.

**절차**:
1. 대상 메서드를 모든 서브클래스에 복사한다.
2. 슈퍼클래스에서 제거한다.
3. 테스트한다.
4. 사용하지 않는 서브클래스에서 제거한다.
5. 테스트한다.

---

## 5. 필드 내리기 (12.5) — Push Down Field

**특정 서브클래스에서만 쓰는 필드**를 슈퍼클래스에서 내린다. (반대: 12.2)

<details>
<summary>원서 Java — 스케치</summary>

```java
// before
class Employee { private String quota; }
// after
class Salesperson extends Employee { protected String quota; }
```

</details>

**배경**: 서브클래스 하나(혹은 소수)에서만 사용하는 필드는 해당 서브클래스로 옮긴다.

**절차**:
1. 대상 필드를 모든 서브클래스에 정의한다.
2. 슈퍼클래스에서 제거한다.
3. 테스트한다.
4. 사용하지 않는 서브클래스에서 제거한다.
5. 테스트한다.

---

## 6. 타입 코드를 서브클래스로 바꾸기 (12.6) — Replace Type Code with Subclasses

동작을 가르는 **타입 코드 필드**를, 그 타입별 **서브클래스**로 바꾼다. (반대: 12.7)

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before
function createEmployee(name, type) { return new Employee(name, type); }
// after: 팩터리가 타입별 서브클래스를 반환
function createEmployee(name, type) {
  switch (type) {
    case "engineer": return new Engineer(name);
    case "salesperson": return new Salesperson(name);
    case "manager": return new Manager(name);
  }
}
```

</details>

**배경**: 타입 코드(열거형·문자열·숫자)를 서브클래스로 바꾸면 두 가지가 좋다. (1) **다형성** — 타입에 따라 동작이 달라지는 함수가 여럿이면 **조건부 로직을 다형성으로(10.4)** 적용할 수 있다. (2) **특정 타입에만 의미 있는 필드**(예: '판매 목표'는 영업자만)를 서브클래스로 내려(12.5) 관계를 명확히 한다. **직접 상속**(`Employee`를 직접 서브클래싱)은 간단하지만 유형을 다른 용도로 못 쓰고 유형이 불변일 때 곤란하다. 이럴 땐 **간접 상속** — 타입 코드에 **기본형을 객체로 바꾸기(7.3)**를 먼저 적용해 `EmployeeType` 클래스를 만들고 그것을 서브클래싱한다.

**절차**:
1. 타입 코드 필드를 **자가 캡슐화**한다.
2. 타입 코드 값 하나를 골라 **서브클래스**를 만들고, 타입 게터를 오버라이드해 그 값을 반환하게 한다.
3. 타입 코드와 서브클래스를 잇는 **선택 로직**을 만든다(직접=팩터리(11.8), 간접=생성자).
4. 테스트한다.
5. 남은 타입 값마다 반복한다(하나 완성할 때마다 테스트).
6. 타입 코드 필드를 제거한다.
7. 테스트한다.
8. 타입 게터를 쓰는 메서드에 **메서드 내리기(12.4)**와 **조건부 로직을 다형성으로(10.4)**를 적용한다.

```typescript
// 직접 상속: 게터 오버라이드만으로 간단히
class Engineer extends Employee {
  get type(): string { return "engineer"; }
}
// 검증 로직은 팩터리의 switch가 대신한다
function createEmployee(name: string, type: string): Employee {
  switch (type) {
    case "engineer": return new Engineer(name);
    case "salesperson": return new Salesperson(name);
    case "manager": return new Manager(name);
    default: throw new Error(`${type}라는 직원 유형은 없습니다.`);
  }
}
```

> 간접 상속에서 만든 `EmployeeType` 계층은 이 책 1판의 **'분류 부호를 상태/전략 패턴으로 전환'**과 본질적으로 같다(2판에서 통합됐다).

---

## 7. 서브클래스 제거하기 (12.7) — Remove Subclass

**가치를 잃은 서브클래스**를 슈퍼클래스의 필드로 대체해 없앤다. (반대: 12.6)

> 1판에서의 이름: 하위클래스를 필드로 전환

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before: 하는 일이 genderCode 뿐인 서브클래스
class Male extends Person { get genderCode() { return "M"; } }
class Female extends Person { get genderCode() { return "F"; } }
// after
class Person { get genderCode() { return this._genderCode; } }
```

</details>

**배경**: 서브클래스는 '다름'을 프로그래밍하는 멋진 수단이지만, 시스템이 자라며 변종이 사라지거나 거의 안 쓰이면 가치가 바랜다. 더는 쓰이지 않는 서브클래스는 이해하느라 에너지만 낭비시키므로, **슈퍼클래스의 필드로 대체**해 제거하는 게 최선이다.

**절차**:
1. 서브클래스의 생성자를 **팩터리 함수로 바꾼다(11.8)**(생성 결정 로직을 팩터리에).
2. 서브클래스 타입을 검사하는 코드는 **함수 추출(6.1)** 후 **함수 옮기기(8.1)**로 슈퍼클래스로 옮긴다.
3. 서브클래스 타입을 나타내는 **필드**를 슈퍼클래스에 만든다.
4. 서브클래스를 참조하던 메서드가 그 타입 필드를 쓰게 한다.
5. 서브클래스를 지운다.
6. 테스트한다.

---

## 8. 슈퍼클래스 추출하기 (12.8) — Extract Superclass

**비슷한 두 클래스**의 공통 요소를 새 슈퍼클래스로 뽑아낸다.

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before: Employee와 Department에 name·연간비용 개념이 중복
// after: 공통을 Party 슈퍼클래스로
class Party { get name() {...} get annualCost() {...} }
class Employee extends Party { get annualCost() {...} get id() {...} }
class Department extends Party { get annualCost() {...} get headCount() {...} }
```

</details>

**배경**: 비슷한 일을 하는 두 클래스의 공통 부분을 슈퍼클래스로 옮긴다(데이터는 **필드 올리기(12.2)**, 동작은 **메서드 올리기(12.1)**).

> **핵심 통찰**: 상속 구조를 사전에 '현실 세계 분류 체계'로 신중히 설계해야 한다는 견해가 많지만, 경험상 상속은 **프로그램이 자라며 공통 요소를 발견했을 때** 뽑아내는 경우가 잦다. 대안인 **클래스 추출(7.5, 위임)**과의 선택은 중복을 상속으로 풀지 위임으로 풀지의 문제다 — 슈퍼클래스 추출이 대개 더 간단하니 먼저 시도하고, 나중에 필요하면 **슈퍼클래스를 위임으로 바꾸기(12.11)**는 어렵지 않다.

**절차**:
1. 빈 슈퍼클래스를 만들고 원래 클래스들이 상속하게 한다.
2. 테스트한다.
3. **생성자 본문 올리기(12.3)·메서드 올리기(12.1)·필드 올리기(12.2)**로 공통 원소를 옮긴다.
4. 서브클래스에 남은 메서드 중 공통되는 부분은 **함수 추출(6.1)** 후 **메서드 올리기(12.1)**.
5. 원래 클래스 사용처가 슈퍼클래스 인터페이스를 쓰게 할지 검토한다.

---

## 9. 계층 합치기 (12.9) — Collapse Hierarchy

**너무 비슷해진 클래스와 그 부모**를 하나로 합친다.

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before
class Employee {...}
class Salesperson extends Employee {...}
// after: 독립할 이유가 사라져 합침
class Employee {...}
```

</details>

**배경**: 계층을 리팩터링하다 보면 어떤 클래스와 그 부모가 너무 비슷해져 **독립적으로 존재할 이유가 사라지는** 때가 온다. 그때 둘을 합친다.

**절차**:
1. 두 클래스 중 제거할 것을 고른다(더 적합한 이름을 남긴다).
2. **필드/메서드 올리기(12.2·12.1)** 또는 **내리기(12.5·12.4)**로 모든 요소를 한 클래스로 모은다.
3. 제거할 클래스를 참조하던 코드가 남길 클래스를 참조하게 한다.
4. 빈 클래스를 제거한다.
5. 테스트한다.

---

## 10. 서브클래스를 위임으로 바꾸기 (12.10) — Replace Subclass with Delegate

상속으로 표현하던 변종을 **위임 객체**로 바꾼다.

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before: PriorityOrder extends Order
// after: Order가 위임을 두고 분배
class Order {
  get daysToShip() {
    return this._priorityDelegate
      ? this._priorityDelegate.daysToShip
      : this._warehouse.daysToShip;
  }
}
class PriorityOrderDelegate {
  get daysToShip() { return this._priorityPlan.daysToShip; }
}
```

</details>

**배경**: 상속에는 두 단점이 있다. (1) **한 번만 쓸 수 있는 카드** — 달라져야 하는 이유가 여럿이어도 상속은 하나만 기준 삼을 수 있다(나이대 *또는* 소득 수준, 둘 다는 안 됨). (2) **긴밀한 결합** — 부모 수정이 자식을 망가뜨리기 쉽다. **위임**은 서로 다른 이유로 여러 클래스에 위임할 수 있고 결합도도 약해 두 문제를 모두 푼다(디자인 패턴의 **상태·전략 패턴**과 구조가 같다).

> **핵심 통찰**: "(클래스) 상속보다 (객체) 컴포지션을 사용하라"는 상속을 **쓰지 말라는 게 아니라 과용에 대한 반작용**이다. 파울러의 조언은 실용적이다 — 처음엔 상속으로 접근하고, **문제가 생기기 시작하면 위임으로 갈아탄다**(그래서 상속을 부담 없이 쓴다).

**절차**(핵심):
1. 생성자 호출이 많으면 **생성자를 팩터리로 바꾼다(11.8)**.
2. 위임 빈 클래스를 만든다(서브클래스 특화 데이터 + 슈퍼클래스로의 **역참조(back-reference)**).
3. 슈퍼클래스에 위임 필드를 추가한다.
4. 서브클래스 생성 코드가 위임 인스턴스를 만들어 초기화하게 한다.
5. 옮길 메서드를 골라 **함수 옮기기(8.1)**로 위임에 옮긴다(원래 메서드의 위임 코드는 유지).
6. 외부에서 원래 메서드를 호출하면 위임 검사 **보호 코드**로 감싼 분배 로직을 슈퍼클래스에 두고, 없으면 **죽은 코드 제거(8.9)**.
7. 모든 메서드가 옮겨질 때까지 반복하고, 서브클래스 생성자 호출을 슈퍼클래스로 바꾼 뒤 서브클래스를 삭제한다.

```typescript
// super 호출이 있던 오버라이드는 무한 재귀를 피해 '확장' 형태로 재호출한다
class Booking {
  get basePrice(): number {
    let result = this._show.price;
    if (this.isPeakDay) {
      result += Math.round(result * 0.15);
    }
    return this._premiumDelegate ? this._premiumDelegate.extendBasePrice(result) : result;
  }
}
class PremiumBookingDelegate {
  extendBasePrice(base: number): number {
    return Math.round(base + this._extras.premiumFee);
  }
}
```

> 서브클래스가 여럿이라 중복이 생기면 위임에서 **슈퍼클래스를 추출(12.8)**해 위임 계층을 만든다 — 이러면 위임 슈퍼클래스가 기본 동작을 맡아 보호 코드가 필요 없어진다.

---

## 11. 슈퍼클래스를 위임으로 바꾸기 (12.11) — Replace Superclass with Delegate

**서브클래스에 어울리지 않는 슈퍼클래스**를, 상속 대신 위임(필드)으로 이용한다.

> 1판에서의 이름: 상속을 위임으로 전환

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before: 자바 Stack extends List의 실수 — 리스트 연산이 스택에 다 노출됨
class Stack extends List {...}
// after: 리스트를 필드에 두고 필요한 기능만 위임
class Stack {
  constructor() { this._storage = new List(); }
}
```

</details>

**배경**: 슈퍼클래스의 기능 중 서브클래스에 맞지 않는 게 많다면(자바 `Stack extends List`처럼 스택에 없는 리스트 연산이 노출), 그것을 상속으로 이용하면 안 된다는 신호다.

> **핵심 통찰**: **제대로 된 상속**이라면 서브클래스가 슈퍼클래스의 **모든** 기능을 사용하고, 서브클래스 인스턴스를 슈퍼클래스 인스턴스로도 취급할 수 있어야 한다(리스코프 치환). 자동차 '모델'(타입)에 식별번호·제조일자를 더해 물리적 '자동차'(인스턴스)를 표현하려는 것은 **타입-인스턴스 동형이의어**라는 흔한 모델링 실수다. "상속은 절대 쓰지 말라"에는 동의하지 않는다 — 의미상 적합하면 상속은 간단·효과적이고, **아니게 되면 그때 위임으로 바꾸면 된다**(위임의 대가는 지루한 전달 함수 작성뿐이다).

**절차**:
1. 서브클래스에 슈퍼클래스 객체를 참조하는 필드(**위임 참조**)를 만들고 새 슈퍼클래스 인스턴스로 초기화한다.
2. 슈퍼클래스의 동작마다 대응하는 **전달 함수**를 서브클래스에 만든다(관련 함수끼리 그룹으로, 그룹마다 테스트).
3. 슈퍼클래스 동작이 모두 전달 함수로 덮이면 **상속 관계를 끊는다**.

```typescript
// Scroll이 CatalogItem을 상속하던 것을 위임으로
class Scroll {
  private _catalogItem: CatalogItem;
  constructor(id: string, title: string, tags: string[], dateLastCleaned: LocalDate) {
    this._catalogItem = new CatalogItem(id, title, tags);
    this._lastCleaned = dateLastCleaned;
  }
  get id(): string { return this._catalogItem.id; }
  get title(): string { return this._catalogItem.title; }
  hasTag(aString: string): boolean { return this._catalogItem.hasTag(aString); }
}
```

> 이후 사본 스크롤 여럿이 하나의 카탈로그 아이템을 공유하게 하려면 **값을 참조로 바꾸기(9.5)**로 저장소를 통해 공유 인스턴스를 참조하게 다듬을 수 있다. 두 위임 리팩터링(12.10·12.11)의 교훈은 **"상속과 컴포지션을 적절히 혼용하라"**이다.

---

## 요약

- **메서드/필드 올리기(12.1·12.2)·생성자 본문 올리기(12.3)**: 서브클래스의 공통 요소를 슈퍼클래스로 올려 중복 제거(생성자는 제약이 많아 슬라이드 후 `super()`로).
- **메서드/필드 내리기(12.4·12.5)**: 특정 서브클래스만 쓰는 요소를 내린다 — 호출자가 타입을 알 때만.
- **타입 코드를 서브클래스로(12.6) ↔ 서브클래스 제거(12.7)**: 타입별 동작이 여럿이면 서브클래스로 승격(다형성), 서브클래스가 가치를 잃으면 필드로 되돌린다.
- **슈퍼클래스 추출(12.8)·계층 합치기(12.9)**: 비슷한 두 클래스에서 공통 슈퍼클래스를 뽑거나, 너무 비슷해진 부모·자식을 합친다.
- **서브클래스를 위임으로(12.10) ↔ 슈퍼클래스를 위임으로(12.11)**: 상속의 '한 번만 쓰는 카드'·긴밀한 결합·부적합(LSP 위반) 문제를 위임으로 푼다 — 상속을 먼저 쓰되, 문제가 생기면 갈아탄다.
