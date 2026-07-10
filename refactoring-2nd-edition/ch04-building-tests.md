# Chapter 4: Building Tests (테스트 구축하기)

## 핵심 질문

리팩터링의 전제인 **자가 테스트 코드**는 왜 그렇게 중요한가? 테스트는 무엇을 기준으로(모든 메서드? 위험 요인?) 작성하는가? 픽스처(fixture)를 어떻게 구성하며, 왜 **매번 새로** 만드는가? 경계 조건은 어떻게 테스트하고, "충분한 테스트"는 어느 정도인가?

---

## 0. 이 장에서 다루는 것 · 코드 표기 규약

리팩터링의 첫 단계는 **견고한 자가 테스트 코드**를 갖추는 것이다(1장·2장). 이 장은 "생산 계획"을 다루는 작은 예제(`Province`·`Producer`)로 **테스트 스위트를 밑바닥부터 구축**하는 과정을 보여 준다.

> **코드 표기 규약**: 원서 JavaScript(테스트는 **Mocha + Chai**)를 `<details>`로 접어 두고 **TypeScript**를 병기한다. 테스트 코드는 `describe`/`it`/`expect` 형태를 유지한다(jest 등에서도 유사).

---

## 1. 자가 테스트 코드의 가치 (4.1)

코드가 하는 일을 스스로 검증하는 **자가 테스트(self-testing)** 코드는 리팩터링의 안전망이자, 그 자체로 개발 속도를 높인다. 핵심은 **성공/실패를 사람이 아니라 프레임워크가 판정**하고, 실패 시 **최근 통과 지점과의 차이**로 버그를 좁힐 수 있다는 것이다.

> **핵심 통찰**: 테스트를 작성하기 가장 좋은 시점은 **프로그래밍을 시작하기 전**이다. 기능을 추가할 때는 "그 기능이 동작하려면 무엇이 필요한지"를 먼저 테스트로 적고, 통과시키는 데 집중한다. 테스트에 쏟는 시간은 디버깅·수동 확인 시간을 줄여 **전체적으로는 시간을 번다**.

---

## 2. 테스트할 샘플 코드 (4.2)

"지역(`Province`)"은 수요(demand)·가격(price)과 여러 생산자(`Producer`)로 구성된다. 생산 부족분(`shortfall` = 수요 − 총생산량)과 총수익(`profit`)을 계산한다. UI·영속성은 제쳐 두고 **비즈니스 로직 두 클래스**만 테스트한다(코드를 성격별로 분리해 둔 덕분에 가능).

<details>
<summary>원서 JavaScript — Province/Producer (핵심 부분)</summary>

```javascript
class Province {
  constructor(doc) {
    this._name = doc.name;
    this._producers = [];
    this._totalProduction = 0;
    this._demand = doc.demand;
    this._price = doc.price;
    doc.producers.forEach(d => this.addProducer(new Producer(this, d)));
  }
  get shortfall() { return this._demand - this.totalProduction; }
  get profit() { return this.demandValue - this.demandCost; }
  get satisfiedDemand() { return Math.min(this._demand, this.totalProduction); }
  get demandValue() { return this.satisfiedDemand * this.price; }
  get demandCost() {
    let remainingDemand = this.demand;
    let result = 0;
    this.producers.sort((a, b) => a.cost - b.cost).forEach(p => {
      const contribution = Math.min(remainingDemand, p.production);
      remainingDemand -= contribution;
      result += contribution * p.cost;
    });
    return result;
  }
}
function sampleProvinceData() {
  return { name: "Asia", price: 20, demand: 30, producers: [
    { name: "Byzantium", cost: 10, production: 9 },
    { name: "Attalia", cost: 12, production: 10 },
    { name: "Sinope", cost: 10, production: 6 },
  ]};
}
```

</details>

```typescript
/** Province 생성자에 넘기는 원시 데이터(JSON에서 파싱). */
interface ProvinceData {
  /** 지역명 */
  name: string;
  /** 수요량 */
  demand: number;
  /** 단가 */
  price: number;
  /** 생산자 목록 */
  producers: ProducerData[];
}

/** Producer 원시 데이터. */
interface ProducerData {
  /** 생산자명 */
  name: string;
  /** 단위 생산 비용 */
  cost: number;
  /** 생산량 */
  production: number;
}

class Province {
  private readonly producers: Producer[] = [];
  private totalProductionValue = 0;
  private demandValue_: number;
  private priceValue: number;

  constructor(doc: ProvinceData) {
    this.demandValue_ = doc.demand;
    this.priceValue = doc.price;
    doc.producers.forEach((d) => this.addProducer(new Producer(this, d)));
  }
  get shortfall(): number {
    return this.demandValue_ - this.totalProductionValue;
  }
  get profit(): number {
    return this.demandValue - this.demandCost;
  }
  // demandValue / demandCost / satisfiedDemand 게터 ... (원서와 동일)
}
```

`Producer`의 `production` 세터는 지역의 총생산량을 갱신하는 **복잡한 동작**을 하므로 테스트 가치가 있다(단순 접근자는 제외).

---

## 3. 첫 번째 테스트 (4.3)

Mocha는 `describe` 블록에 스위트를, `it` 블록에 테스트를 담는다. 테스트는 **① 픽스처 설정 → ② 검증** 두 단계다.

```typescript
describe("province", () => {
  it("shortfall", () => {
    const asia = new Province(sampleProvinceData()); // ① 픽스처
    expect(asia.shortfall).equal(5); // ② 검증
  });
});
```

> **핵심 통찰**: **실패해야 할 상황에서 반드시 실패하는지** 확인하라. 파울러는 새 테스트가 진짜 코드를 검사하는지 의심스러워, 일시적으로 코드에 **오류를 주입**(`shortfall`에 `* 2`)해 테스트가 빨간불이 되는지 본 뒤 되돌린다. "기댓값 자리에 임의 값 → 실제 값으로 대체 → 오류 주입 후 확인 → 원복"이 기존 코드에 테스트를 붙일 때의 상투적 패턴이다.

---

## 4. 테스트 추가하기 (4.4)

클래스의 기능마다 **오류가 생길 조건**을 테스트한다. 여기서 원칙이 나온다.

> **핵심 통찰**: 테스트는 **모든 public 메서드가 아니라 위험 요인을 중심으로** 작성한다. 단순히 필드를 읽고 쓰는 접근자는 버그 가능성이 낮아 테스트하지 않는다. 테스트를 너무 많이 만들면 오히려 중요한 것을 놓치기 쉽다 — "완벽하게 만드느라 실행 못 하느니, **불완전한 테스트라도 작성해 실행하는 게 낫다**."

`shortfall`·`profit` 테스트가 같은 픽스처를 중복 설정하므로 공유하고 싶어진다. 하지만 **바깥 범위의 공유 픽스처**(`const asia = ...`)는 **최악의 함정** — 한 테스트가 그 객체를 바꾸면 다른 테스트가 실행 순서에 따라 실패한다. 해법은 **`beforeEach`로 매번 새 픽스처**를 만드는 것이다.

<details>
<summary>원서 JavaScript — beforeEach로 픽스처를 매번 새로</summary>

```javascript
describe("province", function() {
  let asia;
  beforeEach(function() { asia = new Province(sampleProvinceData()); });
  it("shortfall", function() { expect(asia.shortfall).equal(5); });
  it("profit", function() { expect(asia.profit).equal(230); });
});
```

</details>

```typescript
describe("province", () => {
  let asia: Province;
  // 각 테스트 직전에 실행 → 모든 테스트가 자신만의 새 픽스처를 쓴다
  beforeEach(() => {
    asia = new Province(sampleProvinceData());
  });
  it("shortfall", () => {
    expect(asia.shortfall).equal(5);
  });
  it("profit", () => {
    expect(asia.profit).equal(230);
  });
});
```

> **핵심 통찰**: 매번 새 픽스처를 만들어도 눈에 띄게 느려지는 일은 거의 없다. 정말 문제될 때만 (불변이 확실한) 픽스처를 공유한다. `beforeEach`의 등장은 "이 스위트의 모든 테스트가 **같은 표준 픽스처**에서 시작한다"는 신호이기도 하다.

---

## 5. 픽스처 수정과 준비-수행-단언 (4.5)

사용자가 값을 바꾸는 상황을 테스트하려면 픽스처를 **수정**한 뒤 결과를 검증한다.

```typescript
it("change production", () => {
  asia.producers[0].production = 20; // 수정
  expect(asia.shortfall).equal(-6);
  expect(asia.profit).equal(292);
});
```

이 패턴을 **준비(arrange)-수행(act)-단언(assert)**(또는 setup-exercise-verify, given-when-then)이라 부른다. 네 번째 단계인 **해체(teardown)**는 픽스처를 정리해 테스트 간 간섭을 막는데, `beforeEach` 설정이면 프레임워크가 알아서 해체하므로 대개 생략한다(생성 비용이 큰 공유 픽스처일 때만 명시).

> **핵심 통찰**: 일반적으로 **`it` 하나당 검증도 하나**가 좋다 — 앞 검증이 실패하면 뒤 검증은 실행조차 안 돼 정보를 놓친다. 위 예처럼 두 속성이 아주 밀접하면 묶어도 되지만, 원하면 언제든 나눈다.

---

## 6. 경계 조건 검사하기 (4.6)

"꽃길(happy path)"만이 아니라 **경계 지점**을 테스트한다 — 컬렉션이 빌 때, 숫자가 0·음수일 때, 빈 문자열·잘못된 타입일 때.

```typescript
// 생산자가 없을 때
describe("no producers", () => {
  let noProducers: Province;
  beforeEach(() => {
    noProducers = new Province({ name: "No producers", producers: [], demand: 30, price: 20 });
  });
  it("shortfall", () => {
    expect(noProducers.shortfall).equal(30);
  });
});

// 0 / 음수 / 빈 문자열
it("zero demand", () => {
  asia.demand = 0;
  expect(asia.shortfall).equal(-25);
});
it("negative demand", () => {
  asia.demand = -1;
  expect(asia.profit).equal(-10); // ← "음수 수익이 말이 되나?"라는 설계 고민을 유발
});
it("empty string demand", () => {
  asia.demand = "";
  expect(asia.shortfall).NaN;
});
```

경계 테스트는 두 가지를 준다. (1) **실패(failure)** vs **에러(error)** 구분 — 실패는 검증 단계에서 값이 어긋난 것, 에러는 그 전(설정 등)에서 터진 예외(예: `producers`에 문자열을 넣으면 `forEach is not a function`). (2) **설계 고민** — "수요가 음수면 어떻게?"처럼, 경계를 짚다 보면 특이 상황 처리 방식을 다시 생각하게 된다.

> **핵심 통찰**: **위험한 부분에 집중**하라. 테스트에도 **수확 체감 법칙**이 적용되고, 너무 많이 짜려다 지쳐 아예 안 짜게 될 위험도 있다. "모든 버그를 잡을 수 없으니 안 짠다"는 대다수 버그를 잡을 기회를 버리는 것이다. (외부 입력은 검증 테스트를 쓰되, 신뢰할 수 있는 내부 입력에 중복 유효성 검사는 오히려 문제다. 리팩터링 전이라면 겉보기 동작이 아닌 이런 오류는 신경 쓰지 않아도 된다.)

---

## 7. 끝나지 않은 여정 (4.7)

이 장의 테스트는 **단위 테스트(unit test)** — 작은 영역을 빠르게 검사한다. 자가 테스트의 핵심이다.

> **핵심 통찰**: 테스트도 코드처럼 **반복적으로 보강**한다. 그리고 **버그 리포트를 받으면 가장 먼저 그 버그를 드러내는 단위 테스트부터 작성**하라 — 재발을 막고, 그 버그를 계기로 테스트 스위트의 다른 구멍도 살핀다.

"얼마나 테스트해야 충분한가?"에 명확한 기준은 없다. **테스트 커버리지**는 "**테스트되지 않은 코드를 찾는** 용도"이지 목표 수치가 아니다 — 커버리지 100%가 버그 없음을 뜻하지 않는다. 좋은 척도는 "누군가 결함을 넣었을 때 **테스트가 실패한다고 자신하는가**"이다.

---

## 요약

- 리팩터링의 토대는 **자가 테스트 코드** — 성공/실패를 프레임워크가 판정하고, 실패는 최근 통과 지점과의 차이로 좁힌다.
- 테스트는 **위험 요인 중심**으로 작성한다(모든 메서드가 아니라 버그 가능성 높은 곳). 단순 접근자는 제외.
- **실패해야 할 때 실패하는지** 오류 주입으로 확인하라.
- **픽스처는 `beforeEach`로 매번 새로** 만든다 — 공유 픽스처는 테스트 간 간섭이라는 최악의 함정.
- 테스트는 **준비-수행-단언** 구조. 꽃길뿐 아니라 **경계 조건**(빈 컬렉션·0·음수·잘못된 타입)을 검사하며, 이 과정에서 설계 고민이 따라온다.
- 커버리지는 목표가 아니라 **빈 곳을 찾는 도구**다. **버그를 만나면 그 버그를 드러내는 테스트부터** 작성하라.
