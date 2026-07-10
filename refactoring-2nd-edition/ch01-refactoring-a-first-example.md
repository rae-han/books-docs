# Chapter 1: Refactoring: A First Example (리팩터링: 첫 번째 예시)

## 핵심 질문

잘 작동하는 코드를 왜 굳이 고치는가? 리팩터링은 어디서부터 시작하는가? 긴 함수 하나를 어떤 순서로, 얼마나 잘게 나눠 가며 개선하는가? "계산과 표현의 분리", "조건부 로직을 다형성으로"는 무엇을 얻게 해 주는가? 좋은 코드를 가늠하는 객관적 기준은 무엇인가?

---

## 0. 이 장에서 다루는 것 · 코드 표기 규약

이 장은 원칙을 나열하는 대신, **하나의 지저분한 함수를 처음부터 끝까지 리팩터링하는 과정**을 그대로 보여 준다. 예제는 극단의 **공연료 청구서(`statement`)** 출력 프로그램이다. 파울러는 이 과정을 세 국면으로 진행한다 — (1) 긴 함수를 잘게 **쪼개고**, (2) **계산과 표현(포맷)을 분리**하고, (3) 계산 로직을 **다형성**으로 재구성한다.

> **코드 표기 규약**: 원서는 **JavaScript**로 작성되어 있다. 이 노트는 원서 JS를 `<details>`로 접어 두고(원문 확인용), 그 아래에 **TypeScript 변환본**을 펼쳐 병기한다. TS에서는 도메인 타입을 명시하고, 모든 `if`/`for` 본문에 중괄호를 사용한다.

이 노트 전반에서 다루는 도메인 타입은 다음과 같다(TS).

```typescript
/** 공연할 연극 한 편의 정보. */
interface Play {
  /** 연극 제목 */
  name: string;
  /** 장르 (예: "tragedy", "comedy") */
  type: string;
}

/** playID → Play 조회 맵. */
type Plays = Record<string, Play>;

/** 특정 연극의 1회 공연 (무엇을, 몇 석 규모로). */
interface Performance {
  /** 공연한 연극의 ID */
  playID: string;
  /** 관객 수 */
  audience: number;
}

/** 한 고객에게 보낼 공연료 청구 정보. */
interface Invoice {
  /** 고객명 */
  customer: string;
  /** 청구 대상 공연 목록 */
  performances: Performance[];
}
```

---

## 1. 시작 프로그램: 공연료 청구서 (1.1)

극단은 공연 장르(비극·희극)와 관객 규모로 공연료를 책정하고, 다음 의뢰 때 할인에 쓸 **적립 포인트(volume credits)**도 지급한다. 연극 정보(`plays.json`)와 청구 데이터(`invoices.json`)를 받아 청구 내역 문자열을 출력하는 함수가 다음의 `statement()`다.

<details>
<summary>원서 JavaScript — 시작 시점의 statement()</summary>

```javascript
function statement(invoice, plays) {
  let totalAmount = 0;
  let volumeCredits = 0;
  let result = `청구 내역 (고객명: ${invoice.customer})\n`;
  const format = new Intl.NumberFormat("en-US",
    { style: "currency", currency: "USD", minimumFractionDigits: 2 }).format;

  for (let perf of invoice.performances) {
    const play = plays[perf.playID];
    let thisAmount = 0;
    switch (play.type) {
      case "tragedy": // 비극
        thisAmount = 40000;
        if (perf.audience > 30) {
          thisAmount += 1000 * (perf.audience - 30);
        }
        break;
      case "comedy": // 희극
        thisAmount = 30000;
        if (perf.audience > 20) {
          thisAmount += 10000 + 500 * (perf.audience - 20);
        }
        thisAmount += 300 * perf.audience;
        break;
      default:
        throw new Error(`알 수 없는 장르: ${play.type}`);
    }
    // 포인트를 적립한다.
    volumeCredits += Math.max(perf.audience - 30, 0);
    // 희극 관객 5명마다 추가 포인트를 제공한다.
    if ("comedy" === play.type) volumeCredits += Math.floor(perf.audience / 5);
    // 청구 내역을 출력한다.
    result += `  ${play.name}: ${format(thisAmount / 100)} (${perf.audience}석)\n`;
    totalAmount += thisAmount;
  }
  result += `총액: ${format(totalAmount / 100)}\n`;
  result += `적립 포인트: ${volumeCredits}점\n`;
  return result;
}
```

</details>

```typescript
function statement(invoice: Invoice, plays: Plays): string {
  let totalAmount = 0;
  let volumeCredits = 0;
  let result = `청구 내역 (고객명: ${invoice.customer})\n`;
  const format = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
  }).format;

  for (const perf of invoice.performances) {
    const play = plays[perf.playID];
    let thisAmount = 0;
    switch (play.type) {
      case "tragedy": // 비극
        thisAmount = 40000;
        if (perf.audience > 30) {
          thisAmount += 1000 * (perf.audience - 30);
        }
        break;
      case "comedy": // 희극
        thisAmount = 30000;
        if (perf.audience > 20) {
          thisAmount += 10000 + 500 * (perf.audience - 20);
        }
        thisAmount += 300 * perf.audience;
        break;
      default:
        throw new Error(`알 수 없는 장르: ${play.type}`);
    }
    volumeCredits += Math.max(perf.audience - 30, 0);
    // 코드 스타일 규칙: 한 줄 본문에도 중괄호를 사용한다
    if (play.type === "comedy") {
      volumeCredits += Math.floor(perf.audience / 5);
    }
    result += `  ${play.name}: ${format(thisAmount / 100)} (${perf.audience}석)\n`;
    totalAmount += thisAmount;
  }
  result += `총액: ${format(totalAmount / 100)}\n`;
  result += `적립 포인트: ${volumeCredits}점\n`;
  return result;
}
```

실행 결과는 다음과 같은 평범한 텍스트 청구서다.

```
청구 내역 (고객명: BigCo)
  Hamlet: $650.00 (55석)
  As You Like It: $580.00 (35석)
  Othello: $500.00 (40석)
총액: $1,730.00
적립 포인트: 47점
```

---

## 2. 이 코드를 왜 고쳐야 하는가 (1.2)

이 프로그램은 **잘 작동한다.** 그런데도 고쳐야 하는 이유는 **곧 변경이 들이닥치기 때문**이다.

- **청구서를 HTML로도 출력**해 달라는 요구 → `statement()`를 복사해 `htmlStatement()`를 만들면 청구 로직이 바뀔 때마다 두 함수를 일관되게 고쳐야 한다(중복 코드).
- **연극 장르가 늘어난다** → 공연료·포인트 계산법이 바뀌고, 그때마다 이 긴 함수를 파고들어 수정해야 한다.

컴파일러는 코드가 지저분해도 개의치 않지만, **코드를 수정하는 것은 사람**이다. 설계가 나쁘면 고칠 곳을 찾기 어렵고, 그만큼 버그가 생긴다.

> **핵심 통찰**: 프로그램이 새로운 기능을 추가하기에 편한 구조가 아니라면, 먼저 **기능을 추가하기 쉬운 형태로 리팩터링**하고 나서 원하는 기능을 추가하라. 리팩터링과 기능 추가는 뒤섞지 않고 번갈아 진행한다.

---

## 3. 리팩터링의 첫 단계: 자가진단 테스트 (1.3)

리팩터링의 첫 단계는 **항상 똑같다 — 견고한 테스트부터 마련한다.** 리팩터링 기법이 실수를 줄이도록 설계됐다 해도 작업은 사람이 하므로 언제든 틀릴 수 있다. `statement()`는 문자열을 반환하므로, 여러 장르로 구성한 청구서 몇 개의 **정답 문자열**을 준비해 두고 반환값과 비교한다.

핵심은 **자가진단(self-testing)** — 통과/실패를 사람 눈이 아니라 테스트 프레임워크가 초록불/빨간불로 판정하게 한다. 그래야 수시로, 빠르게 돌릴 수 있다.

> **핵심 통찰**: 리팩터링하기 전에 반드시 **자가진단 테스트**를 갖춰라. 테스트는 내 실수로부터 나를 지키는 버그 검출기다 — 소스와 테스트 양쪽에 의도를 적어 두면, 두 번 똑같이 실수하지 않는 한 반드시 걸린다.

---

## 4. statement() 함수 쪼개기 (1.4~1.5)

긴 함수는 먼저 **동작을 나눌 수 있는 지점**을 찾는다. 한가운데의 `switch`문이 "공연 하나의 요금 계산"을 하고 있으니, 이를 **함수 추출하기(6.1)**로 `amountFor(perf, play)`로 뽑아낸다. 추출 시 유효범위를 벗어나는 변수를 살핀다 — `perf`·`play`는 값이 안 바뀌니 매개변수로, 값이 바뀌는 `thisAmount`는 반환값으로 처리한다.

이후 **작은 단계마다 컴파일·테스트·커밋**하며 다음을 이어 간다.

- **변수 이름 바꾸기**: 추출한 함수 안의 `thisAmount` → `result`(반환값 관례). 매개변수 `perf` → `aPerformance`.
- **임시 변수를 질의 함수로 바꾸기(7.4)**: 루프 안의 지역변수 `play`, `format`을 각각 `playFor()`, `usd()` 같은 함수 호출로 대체한 뒤 **변수 인라인하기(6.4)** → 이후 리팩터링이 쉬워진다.
- **반복문 쪼개기(8.7)** + **문장 슬라이드하기(8.6)** + **함수 추출하기(6.1)**: 한 루프가 "포인트 적립"과 "총액 합산"을 겸하던 것을 분리해 `totalVolumeCredits()`, `totalAmount()`로 각각 추출한다. 반복문은 **파이프라인으로 바꾸기(8.8)**로 `reduce`로 정리한다.

그 결과 `statement()`는 **여러 중첩 함수로 이뤄진 얇은 골격**만 남는다.

<details>
<summary>원서 JavaScript — 쪼갠 뒤의 statement() 골격</summary>

```javascript
function statement(invoice, plays) {
  let result = `청구 내역 (고객명: ${invoice.customer})\n`;
  for (let perf of invoice.performances) {
    result += `  ${playFor(perf).name}: ${usd(amountFor(perf))} (${perf.audience}석)\n`;
  }
  result += `총액: ${usd(totalAmount())}\n`;
  result += `적립 포인트: ${totalVolumeCredits()}점\n`;
  return result;

  function totalAmount() { /* reduce로 amountFor 합산 */ }
  function totalVolumeCredits() { /* reduce로 volumeCreditsFor 합산 */ }
  function usd(aNumber) { /* Intl.NumberFormat */ }
  function volumeCreditsFor(aPerformance) { /* ... */ }
  function playFor(aPerformance) { return plays[aPerformance.playID]; }
  function amountFor(aPerformance) { /* switch로 요금 계산 */ }
}
```

</details>

```typescript
function statement(invoice: Invoice, plays: Plays): string {
  let result = `청구 내역 (고객명: ${invoice.customer})\n`;
  for (const perf of invoice.performances) {
    result += `  ${playFor(perf).name}: ${usd(amountFor(perf))} (${perf.audience}석)\n`;
  }
  result += `총액: ${usd(totalAmount())}\n`;
  result += `적립 포인트: ${totalVolumeCredits()}점\n`;
  return result;

  // 아래는 statement 안의 중첩 함수 — 바깥 변수(invoice, plays)에 접근한다
  function totalAmount(): number {
    return invoice.performances.reduce((total, p) => total + amountFor(p), 0);
  }
  function totalVolumeCredits(): number {
    return invoice.performances.reduce((total, p) => total + volumeCreditsFor(p), 0);
  }
  function usd(aNumber: number): string {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 2,
    }).format(aNumber / 100);
  }
  function volumeCreditsFor(aPerformance: Performance): number {
    let credits = Math.max(aPerformance.audience - 30, 0);
    if (playFor(aPerformance).type === "comedy") {
      credits += Math.floor(aPerformance.audience / 5);
    }
    return credits;
  }
  function playFor(aPerformance: Performance): Play {
    return plays[aPerformance.playID];
  }
  function amountFor(aPerformance: Performance): number {
    let thisAmount = 0;
    switch (playFor(aPerformance).type) {
      case "tragedy":
        thisAmount = 40000;
        if (aPerformance.audience > 30) {
          thisAmount += 1000 * (aPerformance.audience - 30);
        }
        break;
      case "comedy":
        thisAmount = 30000;
        if (aPerformance.audience > 20) {
          thisAmount += 10000 + 500 * (aPerformance.audience - 20);
        }
        thisAmount += 300 * aPerformance.audience;
        break;
      default:
        throw new Error(`알 수 없는 장르: ${playFor(aPerformance).type}`);
    }
    return thisAmount;
  }
}
```

> **핵심 통찰**: 리팩터링은 프로그램 수정을 **아주 작은 단계**로 나눠 진행한다 — 그래서 중간에 실수해도 버그를 쉽게 찾는다. 코드가 늘어난 것처럼 보여도, 각 조각에 **이름**이 붙어 "무엇을 하는지"가 코드 스스로 말하게 된 것이 이득이다.

---

## 5. 계산과 표현(포맷)을 분리하라 — 단계 쪼개기 (1.6~1.7)

이제 원래 목표였던 **HTML 출력**을 준비한다. 핵심 기법은 **단계 쪼개기(6.11)** — 로직을 "① 청구 데이터를 계산하는 단계"와 "② 그 데이터를 문자열로 표현하는 단계"로 나눈다. 계산 결과를 중간 데이터 구조(`statementData`)에 담아 넘기면, 표현 단계는 텍스트든 HTML이든 **같은 데이터로 골라 쓰기만** 하면 된다.

<details>
<summary>원서 JavaScript — 두 단계(두 파일)로 분리</summary>

```javascript
// statement.js
import createStatementData from "./createStatementData.js";

function statement(invoice, plays) {
  return renderPlainText(createStatementData(invoice, plays));
}
function renderPlainText(data) {
  let result = `청구 내역 (고객명: ${data.customer})\n`;
  for (let perf of data.performances) {
    result += `  ${perf.play.name}: ${usd(perf.amount)} (${perf.audience}석)\n`;
  }
  result += `총액: ${usd(data.totalAmount)}\n`;
  result += `적립 포인트: ${data.totalVolumeCredits}점\n`;
  return result;
}
function htmlStatement(invoice, plays) {   // 이제 손쉽게 추가된다
  return renderHtml(createStatementData(invoice, plays));
}
```

</details>

```typescript
// statement.ts — "표현" 단계. 계산은 createStatementData가 이미 끝냈다.
import { createStatementData, StatementData } from "./createStatementData";

function statement(invoice: Invoice, plays: Plays): string {
  return renderPlainText(createStatementData(invoice, plays));
}

function renderPlainText(data: StatementData): string {
  let result = `청구 내역 (고객명: ${data.customer})\n`;
  for (const perf of data.performances) {
    result += `  ${perf.play.name}: ${usd(perf.amount)} (${perf.audience}석)\n`;
  }
  result += `총액: ${usd(data.totalAmount)}\n`;
  result += `적립 포인트: ${data.totalVolumeCredits}점\n`;
  return result;
}

// 계산 단계를 재사용하므로 HTML 버전은 '표현'만 새로 쓰면 된다 — 중복 없음
function htmlStatement(invoice: Invoice, plays: Plays): string {
  return renderHtml(createStatementData(invoice, plays));
}
```

이 분리 덕분에 `htmlStatement()`는 계산 로직을 복사하지 않고 **표현만** 새로 작성하면 된다 — 2절에서 걱정한 중복 문제가 사라졌다.

---

## 6. 조건부 로직을 다형성으로 재구성하라 (1.8~1.9)

두 번째 걱정인 **장르 추가**를 대비할 차례다. `amountFor()`·`volumeCreditsFor()`의 `switch(play.type)`는 장르가 늘 때마다 손대야 한다. **조건부 로직을 다형성으로 바꾸기(10.4)**로, 장르별 계산을 **서브클래스**에 몰아넣는다.

절차: (1) 계산을 담을 `PerformanceCalculator` 클래스를 만들고, (2) 장르별 서브클래스(`TragedyCalculator`·`ComedyCalculator`)를 두고, (3) **팩토리 함수** `createPerformanceCalculator()`가 `type`에 맞는 계산기를 생성하게 한 뒤, (4) `switch`의 각 분기를 해당 서브클래스의 `get amount()`·`get volumeCredits()`로 옮긴다.

<details>
<summary>원서 JavaScript — 다형성 계산기 계층</summary>

```javascript
function createPerformanceCalculator(aPerformance, aPlay) {
  switch (aPlay.type) {
    case "tragedy": return new TragedyCalculator(aPerformance, aPlay);
    case "comedy":  return new ComedyCalculator(aPerformance, aPlay);
    default: throw new Error(`알 수 없는 장르: ${aPlay.type}`);
  }
}

class PerformanceCalculator {
  constructor(aPerformance, aPlay) {
    this.performance = aPerformance;
    this.play = aPlay;
  }
  get amount() { throw new Error("서브클래스에서 처리하도록 설계되었습니다."); }
  get volumeCredits() { return Math.max(this.performance.audience - 30, 0); }
}

class TragedyCalculator extends PerformanceCalculator {
  get amount() {
    let result = 40000;
    if (this.performance.audience > 30) {
      result += 1000 * (this.performance.audience - 30);
    }
    return result;
  }
}

class ComedyCalculator extends PerformanceCalculator {
  get amount() {
    let result = 30000;
    if (this.performance.audience > 20) {
      result += 10000 + 500 * (this.performance.audience - 20);
    }
    result += 300 * this.performance.audience;
    return result;
  }
  get volumeCredits() {
    return super.volumeCredits + Math.floor(this.performance.audience / 5);
  }
}
```

</details>

```typescript
// 계산기 계층 — 장르별 계산을 각자의 서브클래스가 책임진다
abstract class PerformanceCalculator {
  constructor(
    protected readonly performance: Performance,
    protected readonly play: Play,
  ) {}
  /** 이 공연의 요금(센트 단위). 서브클래스가 구현한다. */
  abstract get amount(): number;
  /** 이 공연으로 적립되는 포인트. 기본은 관객 30 초과분. */
  get volumeCredits(): number {
    return Math.max(this.performance.audience - 30, 0);
  }
}

class TragedyCalculator extends PerformanceCalculator {
  get amount(): number {
    let result = 40000;
    if (this.performance.audience > 30) {
      result += 1000 * (this.performance.audience - 30);
    }
    return result;
  }
}

class ComedyCalculator extends PerformanceCalculator {
  get amount(): number {
    let result = 30000;
    if (this.performance.audience > 20) {
      result += 10000 + 500 * (this.performance.audience - 20);
    }
    result += 300 * this.performance.audience;
    return result;
  }
  // 희극만 다른 부분(관객 5명당 추가)만 오버라이드 — 공통은 슈퍼클래스에 남긴다
  get volumeCredits(): number {
    return super.volumeCredits + Math.floor(this.performance.audience / 5);
  }
}

// type에 맞는 계산기를 생성하는 팩토리 (조건 분기는 여기 한 곳으로 모인다)
function createPerformanceCalculator(
  aPerformance: Performance,
  aPlay: Play,
): PerformanceCalculator {
  switch (aPlay.type) {
    case "tragedy":
      return new TragedyCalculator(aPerformance, aPlay);
    case "comedy":
      return new ComedyCalculator(aPerformance, aPlay);
    default:
      throw new Error(`알 수 없는 장르: ${aPlay.type}`);
  }
}
```

이제 **새 장르 추가 = 서브클래스 하나 작성 + 팩토리에 한 줄 추가**로 끝난다. 장르별 계산이 한 곳에 모여 있어 어디를 고칠지도 분명하다.

> **핵심 통찰**: 다형성은 **같은 타입 분기를 여러 함수가 반복**할 때 특히 유리하다 — `amount`와 `volumeCredits` 두 곳의 `switch`가 팩토리 하나로 합쳐졌다. "공통은 슈퍼클래스, 예외만 서브클래스에서 오버라이드"가 장르 확장을 값싸게 만든다.

---

## 7. 좋은 코드의 기준과 리팩터링의 리듬 (1.10)

이 장은 리팩터링을 **세 국면**으로 진행했다 — ① 원본 함수를 중첩 함수로 **쪼개기**, ② **단계 쪼개기**로 계산과 표현을 분리, ③ 계산 로직을 **다형성**으로 표현. 각 국면마다 구조가 보강됐고, 그럴 때마다 코드가 하는 일이 더 분명해졌다.

> **핵심 통찰**: 좋은 코드를 가늠하는 확실한 방법은 **"얼마나 수정하기 쉬운가"**다. 미적 취향은 사람마다 다르지만, "고칠 곳을 쉽게 찾고 오류 없이 빠르게 바꿀 수 있는가"는 취향을 넘어서는 기준이다.

> **핵심 통찰**: 이 예시에서 배울 가장 중요한 것은 **리팩터링의 리듬**이다 — 단계를 잘게 나눌수록 오히려 더 빠르고, 코드는 절대 깨지지 않으며, 작은 단계들이 모여 큰 변화를 이룬다. (파울러가 20년 전 디트로이트 호텔에서 켄트 벡의 작업을 처음 보고 놀란 지점이 바로 이것이다.)

---

## 8. 이 장에서 사용한 리팩터링 기법 (→ 카탈로그)

이 장에 등장한 기법들은 6~12장 카탈로그에서 정식으로 다룬다. 이름 옆 번호는 카탈로그 절이다.

| 리팩터링 기법 | 이 장에서 한 일 | 카탈로그 |
|---|---|---|
| 함수 추출하기 (Extract Function) | `switch`를 `amountFor()`로, 포인트/총액 계산을 별도 함수로 | 6.1 |
| 변수 인라인하기 (Inline Variable) | `play`·`format` 지역변수를 질의 함수 호출로 대체 후 제거 | 6.4 |
| 함수 선언 바꾸기 (Change Function Declaration) | `amountFor`의 매개변수 정리, 이름 개선 | 6.5 |
| 변수 캡슐화하기 (Encapsulate Variable) | 렌더링이 참조하는 데이터 접근을 함수로 감쌈 | 6.6 |
| 단계 쪼개기 (Split Phase) | 계산(`createStatementData`) ↔ 표현(`renderPlainText`) 분리 | 6.11 |
| 임시 변수를 질의 함수로 바꾸기 (Replace Temp with Query) | `thisAmount` 등 임시변수를 함수 호출로 | 7.4 |
| 문장 슬라이드하기 (Slide Statements) | 관련 코드를 가까이 모아 추출 준비 | 8.6 |
| 반복문 쪼개기 (Split Loop) | 포인트 적립과 총액 합산을 각각의 루프로 | 8.7 |
| 반복문을 파이프라인으로 바꾸기 (Replace Loop with Pipeline) | 합산 루프를 `reduce`로 | 8.8 |
| 조건부 로직을 다형성으로 바꾸기 (Replace Conditional with Polymorphism) | 장르 `switch` → 계산기 서브클래스 | 10.4 |

> **핵심 통찰**: 리팩터링은 대부분 **코드가 하는 일을 파악하는 데서 시작**한다 — 읽고, 개선점을 찾고, 그 개선을 코드에 반영하면 코드가 더 명확해지고, 그러면 또 다른 개선점이 보이는 **선순환**이 생긴다.

---

## 요약

- 리팩터링은 **동작을 바꾸지 않고 내부 구조만 개선**하는 작업이다. 잘 작동하는 코드라도 **곧 변경이 온다면** 먼저 고칠 가치가 있다.
- 순서: **① 자가진단 테스트 마련 → ② 작은 단계로 수정하며 매번 테스트·커밋**. 기능 추가와 리팩터링은 섞지 않는다.
- 이 장의 세 국면: **함수 쪼개기(중첩 함수) → 단계 쪼개기(계산/표현 분리) → 다형성(조건부 로직 제거)**.
  - 계산/표현 분리로 **HTML 출력 중복** 문제가, 다형성으로 **장르 추가** 문제가 해결됐다.
- 구조를 보강하면 코드량은 다소 늘지만, 각 조각에 **이름**이 생겨 의도가 드러나고 수정이 쉬워진다.
- **좋은 코드의 기준 = 수정하기 쉬운 정도.** 그리고 그 비결은 **잘게 나눠 절대 깨지지 않게 나아가는 리듬**이다.
