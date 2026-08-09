# Chapter 7: Encapsulation (캡슐화)

## 핵심 질문

데이터 구조(레코드·컬렉션)를 어떻게 캡슐화해 변경을 통제하는가? 기본형을 언제 전용 객체로 승격하는가? 임시 변수를 질의 함수로 바꾸면 무엇이 좋아지는가? 클래스를 언제 추출하고 인라인하는가? 위임을 숨기는 것과 중개자를 제거하는 것 사이의 균형은?

---

## 0. 이 장에서 다루는 것 · 코드 표기 규약

캡슐화는 모듈이 서로에 대해 알아야 할 것을 줄여 결합을 낮춘다. 이 장은 **데이터·클래스·위임을 캡슐화(또는 그 반대)**하는 9가지 기법을 다룬다.

> **코드 표기 규약**: 원서 JavaScript를 `<details>`로 접어 두고 **TypeScript**를 병기한다. 각 기법은 **스케치(before→after) · 배경 · 절차** 형식이다.

---

## 1. 레코드 캡슐화하기 (7.1) — Encapsulate Record

가변 레코드를 **클래스로** 바꿔, 저장 방식을 숨기고 접근을 게터/세터로 통제한다.

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before
organization = { name: "애크미 구스베리", country: "GB" };
// after
class Organization {
  constructor(data) { this._name = data.name; this._country = data.country; }
  get name() { return this._name; }  set name(arg) { this._name = arg; }
  get country() { return this._country; }  set country(arg) { this._country = arg; }
}
```

</details>

```typescript
class Organization {
  private _name: string;
  private _country: string;
  constructor(data: { name: string; country: string }) {
    this._name = data.name;
    this._country = data.country;
  }
  get name(): string { return this._name; }
  set name(arg: string) { this._name = arg; }
  get country(): string { return this._country; }
  set country(arg: string) { this._country = arg; }
}
```

**배경**: 단순 레코드는 "저장된 값 vs 계산된 값"을 구분하기 번거롭다(예: 범위를 `{start,end}`로 저장했는지 `{start,length}`로 저장했는지 사용자가 알아야 함). **가변 데이터는 객체로** 감싸 저장 방식을 숨기면, 세 값을 각각 메서드로 제공하고 이름도 점진적으로 바꿀 수 있다.

**절차**:
1. 레코드를 담은 변수를 **캡슐화(6.6)**한다(검색 쉬운 임시 이름의 게터).
2. 레코드를 감싼 단순 클래스로 교체하고, 원본 레코드를 반환하는 접근자를 둔다.
3. 테스트한다.
4. 새 클래스 타입 객체를 반환하는 함수를 만든다.
5. 예전 함수 사용처를 새 함수로 바꾼다(필드는 접근자로).
6. 임시 접근자와 원본 레코드 반환 함수를 제거한다.
7. 테스트한다. (중첩 구조면 **컬렉션 캡슐화하기(7.2)**와 함께 재귀 적용)

> **핵심 통찰**: 중첩 레코드(JSON 등)는 **쓰기(갱신) 부분에 집중**하라 — 값을 수정하는 곳을 세터로 추출·이동해 한 곳에 모으는 것이 캡슐화의 핵심이다. 읽기는 게터·`rawData()`(깊은 복사)·읽기전용 프락시 등으로 대응한다.

---

## 2. 컬렉션 캡슐화하기 (7.2) — Encapsulate Collection

컬렉션 게터가 **원본을 반환하지 않게** 하고, 추가·제거는 **전용 변경자 메서드**로만 하게 한다.

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before
class Person { get courses() { return this._courses; }  set courses(aList) { this._courses = aList; } }
// after
class Person {
  get courses() { return this._courses.slice(); } // 복제본 반환
  addCourse(aCourse) { ... }
  removeCourse(aCourse) { ... }
}
```

</details>

```typescript
class Person {
  private _courses: Course[] = [];
  // 복제본을 반환해 외부에서 원본을 못 바꾸게 한다
  get courses(): readonly Course[] {
    return this._courses.slice();
  }
  addCourse(aCourse: Course): void {
    this._courses.push(aCourse);
  }
  removeCourse(aCourse: Course): void {
    const index = this._courses.indexOf(aCourse);
    if (index !== -1) {
      this._courses.splice(index, 1);
    }
  }
}
```

**배경**: 컬렉션은 캡슐화 실수가 잦다 — 게터가 컬렉션 **자체**를 반환하면, 소유 클래스 모르게 원소가 바뀐다. `add`/`remove` 변경자만 두고 게터는 **복제본(또는 읽기전용 뷰)**을 반환해 실수를 원천 차단한다.

**절차**:
1. (아직 안 했다면) 컬렉션을 **캡슐화(6.6)**한다.
2. 원소 **추가/제거 메서드**를 추가한다.
3. 정적 검사를 수행한다.
4. 컬렉션을 직접 수정하던 곳을 추가/제거 메서드로 바꾼다.
5. 게터가 **원본이 아닌 복제본/읽기전용 뷰**를 반환하게 한다.
6. 테스트한다.

---

## 3. 기본형을 객체로 바꾸기 (7.3) — Replace Primitive with Object

단순 출력 이상의 동작이 필요해진 기본형 데이터를 **전용 값 클래스**로 승격한다.

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before
orders.filter(o => "high" === o.priority || "rush" === o.priority);
// after
orders.filter(o => o.priority.higherThan(new Priority("normal")));
```

</details>

```typescript
// 우선순위를 문자열이 아니라 전용 값 객체로
class Priority {
  private readonly _value: string;
  constructor(value: string | Priority) {
    if (value instanceof Priority) {
      return value;
    }
    if (!Priority.legalValues().includes(value)) {
      throw new Error(`<${value}>는 유효하지 않은 우선순위입니다.`);
    }
    this._value = value;
  }
  toString(): string { return this._value; }
  private get index(): number {
    return Priority.legalValues().indexOf(this._value);
  }
  static legalValues(): string[] { return ["low", "normal", "high", "rush"]; }
  higherThan(other: Priority): boolean { return this.index > other.index; }
}
// 사용: orders.filter(o => o.priority.higherThan(new Priority("normal")))
```

**배경**: 처음엔 숫자·문자열로 충분하던 정보가 포매팅·검증·비교 같은 동작을 요구하게 된다. 그 순간 **전용 클래스**를 만들면, 처음엔 단순 래퍼지만 동작이 쌓일수록 강력한 도구가 된다("경험 많은 개발자가 가장 유용하게 꼽는 리팩터링").

**절차**:
1. (아직 안 했다면) 변수를 **캡슐화(6.6)**한다.
2. 단순 **값 클래스**를 만든다(값을 받는 생성자 + 게터).
3. 정적 검사를 수행한다.
4. 세터가 값 클래스 인스턴스를 저장하도록 수정한다.
5. 게터가 값 클래스의 게터 결과를 반환하도록 수정한다.
6. 테스트한다.
7. **함수 이름 바꾸기(6.5)**로 접근자 의미를 더 잘 드러낼지 검토한다.

---

## 4. 임시 변수를 질의 함수로 바꾸기 (7.4) — Replace Temp with Query

계산 결과를 담은 임시 변수를 **게터(질의 함수)**로 바꾼다.

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before
const basePrice = this._quantity * this._itemPrice;
if (basePrice > 1000) return basePrice * 0.95;
else return basePrice * 0.98;
// after
get basePrice() { return this._quantity * this._itemPrice; }
if (this.basePrice > 1000) return this.basePrice * 0.95;
else return this.basePrice * 0.98;
```

</details>

```typescript
class Order {
  constructor(private readonly _quantity: number, private readonly _itemPrice: number) {}
  private get basePrice(): number {
    return this._quantity * this._itemPrice;
  }
  get price(): number {
    return this.basePrice > 1000 ? this.basePrice * 0.95 : this.basePrice * 0.98;
  }
}
```

**배경**: 임시 변수를 함수로 만들면 (1) 긴 함수를 추출할 때 변수를 넘길 필요가 없어 경계가 분명해지고, (2) 같은 계산을 다른 함수에서 재사용해 중복이 준다. **클래스 안에서** 가장 효과적이다(메서드들이 공유 컨텍스트를 제공). 단, 값이 한 번만 계산되고 매번 같은 결과를 내는 변수에만 적용한다(스냅숏 변수엔 금지).

**절차**:
1. 변수가 사용 전에 확정되고, 매번 같은 결과를 내는지 확인한다.
2. 읽기전용으로 만들 수 있으면 그렇게 한다.
3. 테스트한다.
4. 변수 대입문을 함수로 **추출**한다(부수효과가 있으면 **질의/변경 함수 분리하기(11.1)** 먼저).

---

## 5. 클래스 추출하기 (7.5) — Extract Class

한 클래스가 하는 일이 많아지면 **일부 데이터·메서드를 새 클래스로** 분리한다. (반대: 7.6)

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before: Person이 전화번호까지 다룸
class Person {
  get officeAreaCode() { return this._officeAreaCode; }
  get officeNumber() { return this._officeNumber; }
}
// after: TelephoneNumber로 분리
class Person {
  get officeAreaCode() { return this._telephoneNumber.areaCode; }
  get officeNumber() { return this._telephoneNumber.number; }
}
class TelephoneNumber {
  get areaCode() { return this._areaCode; }
  get number() { return this._number; }
}
```

</details>

```typescript
class TelephoneNumber {
  areaCode = "";
  number = "";
  toString(): string { return `(${this.areaCode}) ${this.number}`; }
}
class Person {
  private readonly _telephoneNumber = new TelephoneNumber();
  get officeAreaCode(): string { return this._telephoneNumber.areaCode; }
  set officeAreaCode(arg: string) { this._telephoneNumber.areaCode = arg; }
  get telephoneNumber(): string { return this._telephoneNumber.toString(); }
}
```

**배경**: 클래스는 명확한 추상화와 소수의 역할만 맡아야 하는데, 기능이 쌓이며 비대해진다. **함께 변경되거나 서로 의존하는 데이터·메서드**가 따로 묶인다면 분리 신호다(판단법: 일부 데이터/메서드를 제거해도 나머지가 논리적으로 말이 되는가?).

**절차**:
1. 클래스 역할을 분리할 방법을 정한다.
2. 새 클래스를 만든다(원래 클래스 이름도 필요시 조정).
3. 원래 생성자에서 새 클래스 인스턴스를 만들어 필드에 저장한다.
4. 필드를 새 클래스로 **옮긴다(8.2)**(하나씩 테스트).
5. 메서드를 새 클래스로 **옮긴다(8.1)**(저수준부터).
6. 인터페이스를 정리하고 이름을 새 환경에 맞게 바꾼다.
7. 새 클래스를 노출할지 정한다(**참조를 값으로 바꾸기(9.4)** 검토).

---

## 6. 클래스 인라인하기 (7.6) — Inline Class

제 역할을 못 하는 클래스를 **가장 많이 쓰는 클래스로 흡수**한다. (반대: 7.5)

```typescript
// before: TrackingInformation이 거의 빈 껍데기
// after: Shipment로 흡수 (필드·메서드를 옮기고 TrackingInformation 삭제)
class Shipment {
  shippingCompany = "";
  trackingNumber = "";
  get trackingInfo(): string {
    return `${this.shippingCompany}: ${this.trackingNumber}`;
  }
}
```

**배경**: 역할을 옮기다 보니 특정 클래스에 남은 게 거의 없을 때 흡수한다. 또는 **두 클래스의 기능을 재배분**하고 싶을 때, 일단 인라인해 하나로 합친 뒤 다시 **추출(7.5)**하는 것이 쉬울 수 있다.

**절차**:
1. 소스 클래스의 public 메서드에 대응하는 (위임하는) 메서드를 타깃 클래스에 만든다.
2. 소스 메서드 사용처를 타깃의 위임 메서드로 바꾼다(하나씩 테스트).
3. 소스의 메서드·필드를 모두 타깃으로 옮긴다.
4. 소스 클래스를 삭제한다.

---

## 7. 위임 숨기기 (7.7) — Hide Delegate

`서버.위임객체.메서드()`를 `서버.메서드()`로 감싸 **위임 객체의 존재를 숨긴다**. (반대: 7.8)

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before
manager = aPerson.department.manager;
// after
manager = aPerson.manager;
class Person { get manager() { return this._department.manager; } }
```

</details>

```typescript
class Person {
  constructor(private readonly _department: Department) {}
  // department의 존재를 숨긴다 — 클라이언트는 aPerson.manager만 안다
  get manager(): Person {
    return this._department.manager;
  }
}
```

**배경**: 캡슐화의 핵심은 모듈이 서로에 대해 알아야 할 것을 줄이는 것. 클라이언트가 `department`를 거쳐 `manager`를 얻으면 **부서 클래스의 구조에 종속**된다. 서버에 위임 메서드를 두면 위임 객체가 바뀌어도 서버만 고치면 된다.

**절차**:
1. 위임 객체의 각 메서드에 대응하는 **위임 메서드를 서버에** 만든다.
2. 클라이언트가 위임 객체 대신 서버를 호출하도록 바꾼다(하나씩 테스트).
3. 위임 객체를 얻는 접근자를 제거한다.
4. 테스트한다.

---

## 8. 중개자 제거하기 (7.8) — Remove Middle Man

단순 위임만 하는 메서드가 많아지면 **위임 객체를 직접 호출**하게 한다. (반대: 7.7)

```typescript
// before: Person.manager 등 위임 메서드가 너무 많음
// after: 부서를 노출해 클라이언트가 직접
class Person {
  constructor(private readonly _department: Department) {}
  get department(): Department {
    return this._department;
  }
}
// 클라이언트: manager = aPerson.department.manager;
```

**배경**: 위임 숨기기(7.7)의 이점은 공짜가 아니다 — 클라이언트가 위임 객체의 새 기능을 쓸 때마다 서버에 위임 메서드를 추가해야 한다. 그렇게 서버가 **중개자로 전락**하면 차라리 직접 호출이 낫다. (디미터 법칙을 지나치게 신봉할 때 잘 생긴다 — "이따금 유용한 디미터의 제안"으로 여기는 편이 낫다.)

**절차**:
1. 위임 객체를 얻는 게터를 만든다.
2. 위임 메서드를 쓰는 클라이언트가 이 게터를 거치게 바꾼다(하나씩 테스트).
3. 위임 메서드를 삭제한다.

> **핵심 통찰**: 7.7과 7.8은 **반대 방향의 짝**이다. "어느 정도 숨길지"의 적절함은 시스템이 바뀌면 함께 바뀐다 — 자주 쓰는 위임은 숨기고, 성가신 위임은 제거하며 **언제든 균형점을 옮긴다**.

---

## 9. 알고리즘 교체하기 (7.9) — Substitute Algorithm

복잡한 알고리즘을 **더 간명한 알고리즘으로 통째로 교체**한다.

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before: 긴 if 반복
function foundPerson(people) {
  for (let i = 0; i < people.length; i++) {
    if (people[i] === "Don") { return "Don"; }
    if (people[i] === "John") { return "John"; }
    if (people[i] === "Kent") { return "Kent"; }
  }
  return "";
}
// after
function foundPerson(people) {
  const candidates = ["Don", "John", "Kent"];
  return people.find(p => candidates.includes(p)) || "";
}
```

</details>

```typescript
function foundPerson(people: string[]): string {
  const candidates = ["Don", "John", "Kent"];
  return people.find((p) => candidates.includes(p)) ?? "";
}
```

**배경**: 더 간명한 방법(또는 같은 일을 하는 라이브러리)을 찾으면 기존 알고리즘을 걷어내고 교체한다. 알고리즘을 살짝 바꾸고 싶을 때도, 다루기 쉬운 알고리즘으로 먼저 바꾼 뒤 처리하면 편하다. **먼저 메서드를 잘게 나눠** 두어야 교체가 쉽다.

**절차**:
1. 교체할 코드를 함수 하나에 모은다.
2. 이 함수를 검증하는 테스트를 마련한다.
3. 대체 알고리즘을 준비한다.
4. 정적 검사를 수행한다.
5. 기존·새 알고리즘의 결과를 비교 테스트한다(같으면 완료).

---

## 요약

- **레코드 캡슐화(7.1)**·**컬렉션 캡슐화(7.2)**: 가변 데이터를 클래스/변경자로 감싸 변경을 통제(컬렉션 게터는 복제본 반환).
- **기본형을 객체로(7.3)**: 동작이 필요해진 기본형을 전용 값 클래스로 승격.
- **임시 변수를 질의로(7.4)**: 계산 변수를 게터로 — 추출을 쉽게 하고 중복을 줄인다.
- **클래스 추출(7.5) ↔ 인라인(7.6)**: 비대한 클래스를 쪼개거나, 빈 껍데기를 흡수한다(재구성 시 합쳤다 다시 추출).
- **위임 숨기기(7.7) ↔ 중개자 제거(7.8)**: 위임을 감출지 드러낼지의 반대 짝 — 상황에 따라 균형점을 옮긴다.
- **알고리즘 교체(7.9)**: 더 간명한 알고리즘으로 통째 교체(먼저 잘게 나누고, 결과를 비교 테스트).
