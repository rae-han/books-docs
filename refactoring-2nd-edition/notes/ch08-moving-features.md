# Chapter 8: Moving Features (기능 이동)

## 핵심 질문

요소를 어느 컨텍스트(클래스·모듈)에 둘지는 어떻게 정하는가? 함수·필드를 옮길 때 무엇을 함께 옮겨야 하는가? 문장을 함수 안으로 넣을지 밖으로 뺄지는 무엇이 가르는가? 반복문 하나가 여러 일을 할 때 어떻게 나누고, 언제 파이프라인으로 바꾸는가? 죽은 코드는 왜 미련 없이 지워도 되는가?

---

## 0. 이 장에서 다루는 것 · 코드 표기 규약

앞 장들이 요소를 **생성·제거·개명**했다면, 이 장은 요소를 **다른 컨텍스트로 옮기는** 9가지 기법을 다룬다. 함수·필드를 다른 클래스/모듈로 옮기고(8.1·8.2), 문장을 함수 안팎으로 옮기며(8.3·8.4·8.5), 같은 함수 안에서 슬라이드하고(8.6), 반복문을 쪼개거나(8.7) 파이프라인으로 바꾸고(8.8), 죽은 코드를 제거한다(8.9).

> **코드 표기 규약**: 원서 JavaScript를 `<details>`로 접어 두고 **TypeScript**를 병기한다. 각 기법은 **스케치(before→after) · 배경 · 절차** 형식이다.

---

## 1. 함수 옮기기 (8.1) — Move Function

> 1판에서의 이름: 메서드 이동

어떤 함수가 자신이 속한 모듈보다 **다른 모듈의 요소를 더 많이 참조**한다면, 그 모듈로 옮긴다.

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before
class Account { get overdraftCharge() {...} }
// after
class AccountType { get overdraftCharge() {...} }
```

</details>

**배경**: 좋은 설계의 핵심은 **모듈성(modularity)** — 수정할 때 관련된 작은 일부만 이해해도 되게 하는 능력이다. 이해가 깊어질수록 요소를 더 잘 묶는 방법을 깨닫고, 그러면 요소를 이리저리 옮겨야 한다. 함수가 다른 모듈의 요소를 더 많이 참조하거나, 다른 클래스에 두면 쓰기 편해질 때 옮긴다.

> **핵심 통찰**: 함수의 최적 위치를 정하기 어려울수록 **큰 문제가 아닌 경우가 많다**. 일단 한 곳에 두고 작업하다 잘 안 맞으면 언제든 옮기면 된다.

**절차**:
1. 옮길 함수가 현재 컨텍스트에서 사용하는 모든 요소를 살펴보고, **함께 옮길 게 있는지** 고민한다(호출되는 하위 함수부터, 영향이 적은 것부터).
2. 선택한 함수가 **다형 메서드인지**(슈퍼/서브클래스에 선언됐는지) 확인한다.
3. 함수를 타깃 컨텍스트로 **복사**한다(원본=소스 함수, 사본=타깃 함수). 새 터전에 맞게 다듬는다 — 소스 요소를 쓰면 **매개변수로 넘기거나 소스 컨텍스트 자체를 참조**로 넘긴다.
4. 정적 분석을 수행한다.
5. 소스에서 타깃 함수를 **참조할 방법**을 찾아 반영한다.
6. 소스 함수를 타깃의 **위임 함수**로 만든다.
7. 테스트한다.
8. 소스 함수를 **인라인(6.2)**할지 고민한다(호출처에서 타깃을 직접 호출해도 무리 없으면 중간 단계 제거).

**예시 — 다른 클래스로 옮기기**: 계좌 종류에 따라 초과 인출 이자가 달라지도록, `Account.overdraftCharge`를 `AccountType`으로 옮긴다.

```typescript
// before: Account가 이자 계산을 직접 수행
class Account {
  get bankCharge(): number {
    let result = 4.5;
    if (this._daysOverdrawn > 0) {
      result += this.overdraftCharge;
    }
    return result;
  }
  get overdraftCharge(): number {
    if (this.type.isPremium) {
      const baseCharge = 10;
      if (this.daysOverdrawn <= 7) {
        return baseCharge;
      }
      return baseCharge + (this.daysOverdrawn - 7) * 0.85;
    }
    return this.daysOverdrawn * 1.75;
  }
}
```

```typescript
// after: 계산은 AccountType으로, Account는 위임만
class Account {
  get overdraftCharge(): number {
    // 넘길 데이터가 적으면 값으로, 많아지면 this(계좌 자체)를 넘긴다
    return this.type.overdraftCharge(this.daysOverdrawn);
  }
}
class AccountType {
  overdraftCharge(daysOverdrawn: number): number {
    if (this.isPremium) {
      const baseCharge = 10;
      if (daysOverdrawn <= 7) {
        return baseCharge;
      }
      return baseCharge + (daysOverdrawn - 7) * 0.85;
    }
    return daysOverdrawn * 1.75;
  }
}
```

중첩 함수를 최상위로 옮길 때도 같은 절차다 — 사본에 임시 이름(`top_calculateDistance`)을 붙여 소스와 구별하고, 참조하던 값(`points`)을 매개변수로 넘긴 뒤, 소스를 위임→인라인하고 이름을 정리한다. (중첩 함수는 숨겨진 데이터끼리 얽히기 쉬우니 되도록 만들지 않는다.)

---

## 2. 필드 옮기기 (8.2) — Move Field

한 레코드를 다룰 때 **다른 레코드의 필드까지 함께 갱신·전달**해야 한다면, 그 필드의 위치가 잘못된 것이다.

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before
class Customer { get discountRate() { return this._discountRate; } }
// after: 할인율을 계약(CustomerContract)으로 옮김
class Customer { get discountRate() { return this._contract.discountRate; } }
```

</details>

**배경**: 프로그램의 진짜 힘은 **데이터 구조**에서 나온다. 적합한 구조를 쓰면 동작 코드가 단순해지고, 잘못 고르면 아귀 안 맞는 데이터를 다루는 코드로 범벅이 된다. 초기 설계는 늘 틀리므로, 부적절함을 깨달으면 곧바로 고친다. 함수에 항상 함께 건네지는 데이터, 함께 갱신되는 필드는 한 레코드로 모은다. 클래스(캡슐화)를 쓰면 접근자만 고치면 되어 훨씬 수월하다.

**절차**:
1. 소스 필드가 캡슐화되어 있지 않다면 **캡슐화(6.6)**한다.
2. 테스트한다.
3. 타깃 객체에 필드(와 접근자)를 생성한다.
4. 정적 검사를 수행한다.
5. 소스 객체에서 **타깃 객체를 참조**할 수 있는지 확인한다(없으면 타깃을 저장할 필드를 소스에 추가).
6. 접근자들이 타깃 필드를 사용하도록 수정한다. **여러 소스가 타깃을 공유**하면, 먼저 세터가 양쪽을 갱신하게 하고 **어서션(10.6)**으로 불일치를 검출한 뒤 전환한다.
7. 테스트한다.
8. 소스 필드를 제거한다.
9. 테스트한다.

> 세터를 `set discountRate(arg)` 속성이 아니라 `_setDiscountRate(aNumber)` **메서드**로 둘 수 있다 — public 세터를 노출하고 싶지 않을 때다. 생성자에서 필드를 갱신하는 순서 때문에 오류가 나면 **문장 슬라이드하기(8.6)**로 호출 위치를 뒤로 옮긴다.

---

## 3. 문장을 함수로 옮기기 (8.3) — Move Statements into Function

함수 호출 앞뒤에서 **늘 똑같이 실행되는 문장**을 피호출 함수 안으로 합쳐 중복을 없앤다. (반대: 8.4)

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before: 호출부마다 제목 출력이 반복됨
result.push(`<p>제목: ${person.photo.title}</p>`);
result.concat(photoData(person.photo));
// after: 제목 출력을 photoData 안으로
result.concat(photoData(person.photo));
function photoData(aPhoto) {
  return [
    `<p>제목: ${aPhoto.title}</p>`,
    `<p>위치: ${aPhoto.location}</p>`,
    `<p>날짜: ${aPhoto.date.toDateString()}</p>`,
  ];
}
```

</details>

**배경**: 중복 제거는 코드를 건강하게 관리하는 가장 효과적인 방법 중 하나다. 특정 함수 호출 앞뒤에 똑같은 코드가 늘 붙는다면, 그 반복 부분을 피호출 함수로 합친다. 단, 그 문장들이 **피호출 함수의 일부라는 확신**이 있어야 한다(한 몸은 아니지만 함께 호출돼야 할 뿐이라면, 문장과 호출을 통째로 새 함수로 **추출(6.1)**한다).

**절차**:
1. 반복 코드가 호출과 멀리 떨어져 있으면 **문장 슬라이드하기(8.6)**로 근처로 옮긴다.
2. 호출자가 **한 곳뿐**이면 코드를 잘라 피호출 함수로 복사하고 테스트한다(끝).
3. 호출자가 **둘 이상**이면 한 호출자에서 '호출 부분 + 옮길 문장'을 함께 **추출(6.1)**하고 임시 이름을 붙인다.
4. 다른 호출자도 이 함수를 쓰도록 하나씩 바꾼다(매번 테스트).
5. 모두 전환되면 원래 함수를 새 함수 안으로 **인라인(6.2)**하고 원래 함수를 제거한다.
6. 새 함수 이름을 원래 이름으로 **바꾼다(6.5)**.

---

## 4. 문장을 호출한 곳으로 옮기기 (8.4) — Move Statements to Callers

함수가 하던 일 중 **일부 호출자에게만 다르게 동작해야 하는 부분**을 호출한 곳으로 꺼낸다. (반대: 8.3)

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before: emitPhotoData가 위치까지 출력
function emitPhotoData(outStream, photo) {
  outStream.write(`<p>제목: ${photo.title}</p>\n`);
  outStream.write(`<p>위치: ${photo.location}</p>\n`);
}
// after: 위치 출력을 호출자로 옮김 (호출자마다 다르게 렌더링 가능)
emitPhotoData(outStream, person.photo);
outStream.write(`<p>위치: ${person.photo.location}</p>\n`);
function emitPhotoData(outStream, photo) {
  outStream.write(`<p>제목: ${photo.title}</p>\n`);
}
```

</details>

**배경**: 함수는 추상화의 기본 빌딩 블록이지만 그 경계를 항상 옳게 긋기는 어렵다. 응집도 높던 함수가 어느새 둘 이상의 일을 하게 되면 — 특히 여러 호출자 중 일부만 다르게 동작해야 하면 — 달라지는 부분을 호출자로 꺼낸다. 먼저 **문장 슬라이드(8.6)**로 달라지는 부분을 함수의 시작/끝으로 몬 뒤 이 리팩터링을 적용한다.

**절차**:
1. 호출자가 한두 개고 함수도 간단하면, 첫(또는 마지막) 줄을 잘라 호출자에 복사하고 테스트한다(끝).
2. 복잡하면 **이동하지 않을** 문장을 함수로 **추출(6.1)**하고 임시 이름을 붙인다(오버라이드된 메서드면 각 서브클래스에서 동일하게 추출 후 서브클래스 메서드 제거).
3. 원래 함수를 **인라인(6.2)**한다 — 호출자마다 하나씩 인라인하며 테스트.
4. 추출한 함수의 이름을 원래 이름으로 되돌린다.

> 8.3과 8.4는 **반대 짝**이다. 경계를 완전히 다시 그어야 할 만큼 큰 변경이라면, **함수 인라인(6.2)** 후 슬라이드·추출로 새 경계를 설정한다.

---

## 5. 인라인 코드를 함수 호출로 바꾸기 (8.5) — Replace Inline Code with Function Call

이미 있는 함수와 **똑같은 일을 하는 인라인 코드**를 그 함수 호출로 대체한다.

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before
let appliesToMass = false;
for (const s of states) {
  if (s === "MA") appliesToMass = true;
}
// after
const appliesToMass = states.includes("MA");
```

</details>

```typescript
// 라이브러리/표준 함수로 대체할 수 있다면 본문을 짤 필요조차 없다
const appliesToMass = states.includes("MA");
```

**배경**: 함수는 코드의 **목적**(어떻게가 아니라 무엇)을 이름으로 말해 이해를 돕고 중복을 없앤다. 이미 있는 함수와 같은 일을 하는 인라인 코드는 호출로 바꾸는 게 보통이다 — 예외는 순전히 우연히 비슷할 뿐이라 그 함수를 고쳐도 이 코드는 바뀌면 안 되는 경우다. **함수 이름을 넣어도 말이 되는지**가 판단 힌트다.

**절차**:
1. 인라인 코드를 함수 호출로 대체한다.
2. 테스트한다.

> **함수 추출하기(6.1)와의 차이**: 대체할 함수가 아직 **없어서 새로 만들면** 함수 추출, **이미 존재하면** 인라인 코드를 함수 호출로 바꾸기다. 표준 라이브러리·플랫폼 API를 잘 알수록 이 리팩터링의 활용 빈도가 높아진다.

---

## 6. 문장 슬라이드하기 (8.6) — Slide Statements

> 1판에서의 이름: 조건문의 공통 실행 코드 빼내기

관련된 문장들을 **한데 모아** 이해하기 쉽게 한다(주로 다른 리팩터링의 준비 단계).

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before: 선언이 사용처와 떨어져 있음
const pricingPlan = retrievePricingPlan();
const order = retrieveOrder();
let charge;
const chargePerUnit = pricingPlan.unit;
// after: pricingPlan을 쓰는 선언을 붙여 모음
const pricingPlan = retrievePricingPlan();
const chargePerUnit = pricingPlan.unit;
const order = retrieveOrder();
let charge;
```

</details>

**배경**: 관련된 코드가 가까이 모여 있으면 이해하기 쉽다. 특히 변수는 **처음 사용하는 곳에서 선언**하는 스타일을 선호한다. 관련 코드끼리 모으는 것은 **함수 추출(6.1)**의 준비 단계로 자주 쓰인다 — 흩어져 있으면 추출 자체가 불가능하다.

**절차**:
1. 목표 위치를 찾고, 원래 위치와 목표 위치 사이 코드를 훑어 **간섭**이 있는지 살핀다. 다음이면 포기한다: 참조하는 요소의 선언 앞으로는 못 감 / 자신을 참조하는 요소의 뒤로는 못 감 / 참조 요소를 수정하는 문장을 건너뛸 수 없음 / 자신이 수정하는 요소를 참조하는 문장을 건너뛸 수 없음.
2. 코드 조각을 잘라내어 목표 위치에 붙인다.
3. 테스트한다(실패하면 더 작게 나눠 슬라이드).

> **핵심 통찰**: **부수효과가 없는 코드끼리는 자유롭게 재배치**할 수 있다. 명령-질의 분리(Command-Query Separation) 원칙을 지켜 값을 반환하는 함수를 부수효과 없이 짜면, 슬라이드 가능 여부를 훨씬 쉽게 판단할 수 있다.

**예시 — 조건문 밖으로 슬라이드**: 두 분기에 똑같은 문장이 있으면 조건문 밖으로 꺼내며 한 문장으로 합쳐진다(중복 제거). 반대로 조건문 안으로 넣으면 모든 분기에 복제된다.

```typescript
// before
let result: Resource;
if (availableResources.length === 0) {
  result = createResource();
  allocatedResources.push(result);
} else {
  result = availableResources.pop()!;
  allocatedResources.push(result);
}
return result;
```

```typescript
// after: push를 조건문 밖으로 슬라이드 → 중복 제거
let result: Resource;
if (availableResources.length === 0) {
  result = createResource();
} else {
  result = availableResources.pop()!;
}
allocatedResources.push(result);
return result;
```

---

## 7. 반복문 쪼개기 (8.7) — Split Loop

한 반복문에서 **두 가지 일**을 하고 있다면, 각각의 반복문으로 나눈다.

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before: 나이 합과 급여 합을 한 반복문에서
let averageAge = 0, totalSalary = 0;
for (const p of people) {
  averageAge += p.age;
  totalSalary += p.salary;
}
averageAge = averageAge / people.length;
// after: 두 반복문으로 분리
let totalSalary = 0;
for (const p of people) { totalSalary += p.salary; }
let averageAge = 0;
for (const p of people) { averageAge += p.age; }
averageAge = averageAge / people.length;
```

</details>

**배경**: 한 반복문이 두 일을 하면 수정할 때마다 둘 다 이해해야 한다. 나누면 하나만 이해하면 되고, 각각 값을 곧바로 반환할 수 있어 **사용하기도 쉬워진다**. 반복문 쪼개기는 **함수 추출(6.1)**로 이어지는 경우가 잦다.

> **핵심 통찰**: "반복문을 두 번 돈다"는 이유로 꺼리지 말라 — **리팩터링과 최적화는 구분**한다. 정리 후 병목으로 밝혀지면 그때 합치면 된다(대개 병목이 아니다). 오히려 쪼개기가 더 강력한 최적화의 길을 연다.

**절차**:
1. 반복문을 **복제**해 둘로 만든다.
2. 중복 때문에 생기는 **부수효과를 제거**한다(부수효과 없는 코드는 양쪽에 둬도 무방).
3. 테스트한다.
4. 완료됐으면 각 반복문을 **함수로 추출(6.1)**할지 고민한다(추출 후 8.8·7.9로 더 다듬을 수 있다).

---

## 8. 반복문을 파이프라인으로 바꾸기 (8.8) — Replace Loop with Pipeline

반복문을 **컬렉션 파이프라인**(map·filter 등)으로 바꿔, 객체가 흐르며 처리되는 과정을 읽히게 한다.

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before
const names = [];
for (const i of input) {
  if (i.job === "programmer") names.push(i.name);
}
// after
const names = input
  .filter(i => i.job === "programmer")
  .map(i => i.name);
```

</details>

**배경**: 컬렉션 파이프라인은 처리 과정을 **일련의 연산**으로 표현한다. 각 연산은 컬렉션을 입력받아 다른 컬렉션을 내뱉는다(`map`은 원소를 변환, `filter`는 부분집합을 만듦). 논리를 파이프라인으로 표현하면 객체가 어떻게 처리되는지 위에서 아래로 읽을 수 있어 이해하기 쉽다.

**절차**:
1. 반복문이 사용하는 컬렉션을 가리키는 **루프 변수**를 하나 만든다.
2. 반복문의 각 단위 행위를 적절한 **파이프라인 연산으로 하나씩 대체**하며, 매번 테스트한다.
3. 모든 동작을 대체했으면 반복문을 지운다(누적 변수에는 파이프라인 결과를 대입).

**예시 — CSV에서 인도 사무실 뽑기**: 첫 줄 건너뛰기→빈 줄 제거→필드 분리→인도 필터→결과 매핑을 파이프라인으로 옮긴다.

```typescript
// before
function acquireData(input: string) {
  const lines = input.split("\n");
  let firstLine = true;
  const result: { city: string; phone: string }[] = [];
  for (const line of lines) {
    if (firstLine) {
      firstLine = false;
      continue;
    }
    if (line.trim() === "") {
      continue;
    }
    const record = line.split(",");
    if (record[1].trim() === "India") {
      result.push({ city: record[0].trim(), phone: record[2].trim() });
    }
  }
  return result;
}
```

```typescript
// after: 제어 변수(firstLine)·누적 변수(result)가 모두 사라진다
function acquireData(input: string) {
  const lines = input.split("\n");
  return lines
    .slice(1) // 헤더 줄 건너뛰기
    .filter((line) => line.trim() !== "")
    .map((line) => line.split(","))
    .filter((fields) => fields[1].trim() === "India")
    .map((fields) => ({ city: fields[0].trim(), phone: fields[2].trim() }));
}
```

> `slice(1)`로 첫 줄을 건너뛰는 순간 **제어용 변수 `firstLine`을 지울 수 있다** — 제어 변수를 없애는 건 언제나 즐거운 일이다. `lines`는 인라인할 수도 있었지만, 남겨 두는 편이 코드가 하는 일을 더 잘 설명하므로 그대로 뒀다.

---

## 9. 죽은 코드 제거하기 (8.9) — Remove Dead Code

더 이상 사용되지 않는 코드를 **지운다**.

<details>
<summary>원서 JavaScript — 스케치</summary>

```javascript
// before
if (false) {
  doSomethingThatUsedToMatter();
}
// after: 삭제
```

</details>

**배경**: 코드의 양에는 비용이 없지만, 쓰이지 않는 코드는 소프트웨어의 동작을 이해하는 데 **커다란 걸림돌**이 된다. "이건 절대 호출되지 않으니 무시해도 된다"는 신호를 주지 않기 때문에, 다른 사람이 그 동작을 파악하느라 시간을 허비한다.

> **핵심 통찰**: "다시 필요해지면?"을 걱정할 필요 없다 — 우리에겐 **버전 관리 시스템**이 있다. 그런 날이 오면 되살리면 된다(필요하면 삭제 리비전을 커밋 메시지에 남긴다). 죽은 코드를 **주석 처리**하던 관행은 버전 관리가 보편화된 지금 더 이상 필요치 않다.

**절차**:
1. 죽은 코드를 외부에서 참조할 수 있는 경우라면(예: 함수 하나가 통째로 죽음) 호출하는 곳이 정말 없는지 확인한다.
2. 없으면 죽은 코드를 제거한다.
3. 테스트한다.

---

## 요약

- **함수 옮기기(8.1)·필드 옮기기(8.2)**: 다른 모듈 요소를 더 많이 참조하거나 함께 갱신되는 요소를 그쪽으로 옮긴다 — 소스는 위임→인라인, 공유 필드는 어서션으로 안전하게 전환.
- **문장을 함수로(8.3) ↔ 호출한 곳으로(8.4)**: 반대 짝. 늘 함께 실행되면 안으로 합치고(중복 제거), 일부 호출자만 달라지면 밖으로 뺀다.
- **인라인 코드를 함수 호출로(8.5)**: 이미 있는 함수(특히 라이브러리)로 대체 — "이름을 넣어도 말이 되는가"로 판단.
- **문장 슬라이드하기(8.6)**: 관련 코드를 모아 추출을 준비 — 부수효과 없는 코드끼리는 자유롭게 재배치.
- **반복문 쪼개기(8.7)**: 한 반복문 두 일을 분리 — 리팩터링과 최적화를 구분하라.
- **반복문을 파이프라인으로(8.8)**: map·filter 연쇄로 제어·누적 변수를 없애고 흐름을 읽히게.
- **죽은 코드 제거하기(8.9)**: 미련 없이 지운다 — 버전 관리가 되살려 준다.
