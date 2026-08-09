# Chapter 5: Make Code Readable (가독성 높은 코드를 작성하라)

## 핵심 질문

코드가 그 자체로 설명되게 하려면 어떻게 해야 하는가? 주석문은 언제 유용하고 언제 유해한가? 코드 줄 수는 정말 적을수록 좋은가? 깊이 중첩된 코드·불명확한 함수 호출·설명되지 않은 값·긴 익명 함수는 어떻게 개선하는가? 언어의 새 기능은 언제 써야 하는가?

---

## 0. 이 장에서 다루는 것 · 코드 표기 규약

- 코드가 그 자체로 설명이 되도록 하는 방법
- 다른 사람에게 코드의 세부 내용을 명확히 하는 방법
- 언어의 기능을 사용할 때 합당한 이유를 갖는 것

여기서부터가 **PART 2(실전)**이다. 2부의 각 장은 6대 요소 중 하나에 초점을 맞추고, 각 절은 "문제가 될 수 있는 방법 → 특정 기법으로 개선"의 패턴을 따른다. 이 장은 **가독성**을 다룬다.

> **핵심 통찰**: 가독성은 본질적으로 주관적이고 정의하기 어렵다. 핵심은 **개발자가 코드의 기능을 빠르고 정확하게 이해하도록** 하는 것이며, 이를 위해 "다른 사람 관점에서 이 코드가 혼란스럽거나 오해될 수 있는가"를 **공감(empathy)**하며 상상해야 한다. 이 장의 기법들은 규칙이 아니라 지침이므로 상식과 판단을 함께 적용해야 한다.

> **코드 표기 규약**: 원서 의사코드를 `<details>`로 접어 두고 아래에 **TypeScript 변환본**을 병기한다. 널 규약(`Type?` → `Type | null`)을 따른다.

---

## 1. 서술형 명칭을 사용하라 (5.1)

이름은 대상을 식별할 뿐 아니라 그것이 무엇인지 **간단한 설명**도 해준다. 토스터를 "객체 A"라고 부르면 무엇인지 기억하기 어렵다. 서술적이지 않은 이름은 코드를 읽기 어렵게 만든다.

<details>
<summary>의사코드 (원서) — 예제 5.1 → 5.3 (나쁜 예 → 좋은 예)</summary>

```java
// ❌ 서술적이지 않은 이름 — 무슨 일을 하는지 알 수 없다
class T {
  Set<String> pns = new Set();
  Int s = 0;
  Boolean f(String n) { return pns.contains(n); }
  Int getS() { return s; }
}
Int? s(List<T> ts, String n) {
  for (T t in ts) {
    if (t.f(n)) { return t.getS(); }
  }
  return null;
}

// ✅ 서술적인 이름 — 자명하다
class Team {
  Set<String> playerNames = new Set();
  Int score = 0;
  Boolean containsPlayer(String playerName) { return playerNames.contains(playerName); }
  Int getScore() { return score; }
}
Int? getTeamScoreForPlayer(List<Team> teams, String playerName) {
  for (Team team in teams) {
    if (team.containsPlayer(playerName)) { return team.getScore(); }
  }
  return null;
}
```

</details>

```typescript
// ❌ 서술적이지 않은 이름
class T {
  pns = new Set<string>();
  s = 0;
  f(n: string): boolean { return this.pns.has(n); }
  getS(): number { return this.s; }
}

// ✅ 서술적인 이름 — Team.containsPlayer(playerName)만 봐도 자명하다
class Team {
  playerNames = new Set<string>();
  score = 0;
  containsPlayer(playerName: string): boolean { return this.playerNames.has(playerName); }
  getScore(): number { return this.score; }
}

function getTeamScoreForPlayer(teams: Team[], playerName: string): number | null {
  for (const team of teams) {
    if (team.containsPlayer(playerName)) { return team.getScore(); }
  }
  return null;
}
```

> **핵심 통찰**: 서술적 이름을 붙이는 대신 **주석문으로 대체하면 안 된다**(5.1.2). 주석은 코드를 더 복잡하게 만들고, 개발자가 `s`가 무엇인지 잊으면 파일 맨 위로 스크롤해 주석을 찾아야 한다. 서술적 이름은 코드를 **떼어놓고 봐도** 의미가 통하게 한다.

---

## 2. 주석문을 적절히 사용하라 (5.2)

주석은 (1) 코드가 **무엇을** 하는지, (2) **왜** 하는지, (3) 사용 지침(코드 계약, 3장)을 설명할 수 있다. 클래스 같은 큰 단위의 상위 요약 주석은 유용하지만, 한 줄 한 줄이 무엇을 하는지 설명하는 하위 주석은 가독성에 효과적이지 않다.

- **중복된 주석은 유해**(5.2.1): `// "{이름}.{성}" 형태로 ID 생성` 같은 주석은 코드가 이미 설명하므로 쓸모없고, 유지보수 부담·지저분함만 더한다.
- **주석으로 가독성 높은 코드를 대체할 수 없다**(5.2.2): `data[0]`, `data[1]`을 주석으로 설명하느니 `firstName(data)`, `lastName(data)` 헬퍼 함수를 쓴다.
- **주석은 "왜"를 설명하는 데 유용**(5.2.3): 제품/비즈니스 결정, 이상한 버그 해결책, 의존 코드의 예상 밖 동작 등 **코드만으로 알 수 없는 배경**은 주석이 값지다(예: "v2.0 이전 레거시 유저는 이름으로 ID 부여. #4218 이슈 참고").
- **상위 수준 요약은 유용**(5.2.4): 책의 뒤표지처럼, 클래스가 하는 일을 요약한 주석은 다른 개발자가 유용성을 빠르게 가늠하게 한다("이 클래스는 DB와 동기화되지 않을 수 있다" 등).

> **핵심 통찰**: 코드의 기능을 설명하는 하위 주석을 많이 달아야 한다면, 그것은 **코드 자체의 가독성이 낮다는 신호**다. 주석은 코드가 표현하지 못하는 **"왜"**와 **상위 요약**에 쓰라.

---

## 3. 코드 줄 수에 집착하지 말라 (5.3)

줄 수가 적을수록 좋다는 것은 일반적으로 맞지만, 이는 우리가 진짜 신경 쓰는 것(이해하기 쉬움 / 오해하기 어려움 / 실수로 깨뜨리기 어려움)을 **간접 측정**할 뿐이다. 이해하기 어려운 한 줄은 같은 일을 하는 이해하기 쉬운 10줄보다 품질이 낮다.

<details>
<summary>의사코드 (원서) — 예제 5.9 → 5.10 (간결하지만 난해 → 길지만 명확)</summary>

```java
// ❌ 간결하지만 거의 이해할 수 없다 (패리티 비트 검사)
Boolean isIdValid(UInt16 id) {
  return countSetBits(id & 0x7FFF) % 2 == ((id & 0x8000) >> 15);
}

// ✅ 줄은 많지만 명확하고, 하위 문제를 재사용할 수 있다
Boolean isIdValid(UInt16 id) {
  return extractEncodedParity(id) == calculateParity(getIdValue(id));
}
private const UInt16 PARITY_BIT_INDEX = 15;
private const UInt16 PARITY_BIT_MASK = (1 << PARITY_BIT_INDEX);
private const UInt16 VALUE_BIT_MASK = ~PARITY_BIT_MASK;
private UInt16 getIdValue(UInt16 id) { return id & VALUE_BIT_MASK; }
private UInt16 extractEncodedParity(UInt16 id) { return (id & PARITY_BIT_MASK) >> PARITY_BIT_INDEX; }
private UInt16 calculateParity(UInt16 value) { return countSetBits(value) % 2; }
```

</details>

```typescript
// ❌ 간결하지만 난해 — 유효한 ID 기준을 즉시 알 수 없다
function isIdValid(id: number): boolean {
  return countSetBits(id & 0x7fff) % 2 === ((id & 0x8000) >> 15);
}

// ✅ 명확: 상수·헬퍼로 가정을 드러내고 재사용 가능
const PARITY_BIT_INDEX = 15;
const PARITY_BIT_MASK = 1 << PARITY_BIT_INDEX;
const VALUE_BIT_MASK = ~PARITY_BIT_MASK;

function isIdValid(id: number): boolean {
  return extractEncodedParity(id) === calculateParity(getIdValue(id));
}
function getIdValue(id: number): number { return id & VALUE_BIT_MASK; }
function extractEncodedParity(id: number): number { return (id & PARITY_BIT_MASK) >> PARITY_BIT_INDEX; }
function calculateParity(value: number): number { return countSetBits(value) % 2; }
```

---

## 4. 일관된 코딩 스타일을 고수하라 (5.4)

문법이 허용하는 것과 별개로, 잘 읽히는 스타일 지침이 있다. `SaaS`를 `SAAS`로 쓰면 다른 것으로 오해되듯, 코드 스타일이 어긋나면 혼란과 버그를 부른다.

> **비유 — connectionManager 버그**: 클래스는 파스칼케이스, 변수는 캐멀케이스라는 관례를 따를 때, `connectionManager.terminateAll()`을 보면 "인스턴스 변수"라고 가정한다. 그런데 `connectionManager`가 실은 **클래스**(정적 함수 `terminateAll()`)라면, 해당 채팅만이 아니라 **서버의 모든 채팅 연결을 종료**하는 심각한 버그가 된다. `ConnectionManager`로 명명했다면 이 버그는 드러났을 것이다.

팀·조직의 스타일 가이드를 따르는 것은 모두가 같은 언어를 유창하게 말하는 것과 같다. **린터(*linter - 스타일 위반이나 알려진 나쁜 관행을 찾아 알려주는 도구*)**는 처음부터 좋은 코드를 쓰는 것을 대체하진 못하지만 빠르고 쉬운 개선 수단이다.

---

## 5. 깊이 중첩된 코드를 피하라 (5.5)

제어 흐름(if/for)은 서로 중첩된 블록을 만든다. 인간의 눈은 각 줄의 중첩 수준을 추적하는 데 약하므로, 깊은 중첩은 "이 줄이 언제 실행되는가"를 파악하기 어렵게 한다.

<details>
<summary>의사코드 (원서) — 예제 5.14 → 5.15 (중첩 if → 일찍 반환)</summary>

```java
// ❌ 깊이 중첩된 if — 언제 어떤 값이 반환되는지 따라가기 어렵다
Address? getOwnersAddress(Vehicle vehicle) {
  if (vehicle.hasBeenScraped()) {
    return SCRAPYARD_ADDRESS;
  } else {
    Purchase? mostRecentPurchase = vehicle.getMostRecentPurchase();
    if (mostRecentPurchase == null) {
      return SHOWROOM_ADDRESS;
    } else {
      Buyer? buyer = mostRecentPurchase.getBuyer();
      if (buyer != null) {
        return buyer.getAddress();
      }
    }
  }
  return null;
}

// ✅ 일찍 반환(early return)으로 중첩 제거
Address? getOwnersAddress(Vehicle vehicle) {
  if (vehicle.hasBeenScraped()) {
    return SCRAPYARD_ADDRESS;
  }
  Purchase? mostRecentPurchase = vehicle.getMostRecentPurchase();
  if (mostRecentPurchase == null) {
    return SHOWROOM_ADDRESS;
  }
  Buyer? buyer = mostRecentPurchase.getBuyer();
  if (buyer != null) {
    return buyer.getAddress();
  }
  return null;
}
```

</details>

```typescript
// ✅ 일찍 반환으로 중첩 제거 (나쁜 예는 중첩된 if/else 형태)
function getOwnersAddress(vehicle: Vehicle): Address | null {
  if (vehicle.hasBeenScraped()) {
    return SCRAPYARD_ADDRESS;
  }
  const mostRecentPurchase: Purchase | null = vehicle.getMostRecentPurchase();
  if (mostRecentPurchase === null) {
    return SHOWROOM_ADDRESS;
  }
  const buyer: Buyer | null = mostRecentPurchase.getBuyer();
  if (buyer !== null) {
    return buyer.getAddress();
  }
  return null;
}
```

> **핵심 통찰**: 중첩된 모든 블록에 반환문이 있으면 일찍 반환으로 쉽게 펼 수 있다. 하지만 **중첩된 블록에 반환문이 없다면, 그건 대개 함수가 너무 많은 일을 한다는 신호**다(5.5.3). 이럴 땐 주소를 찾는 로직을 별도 함수로 분리한 뒤 중첩을 제거한다(5.5.4) — 2장의 "함수는 한 문장처럼"과 이어진다.

---

## 6. 함수 호출도 가독성이 있어야 한다 (5.6)

함수 이름이 좋아도 인수가 무엇을 뜻하는지 불명확하면 호출이 이해되지 않는다. `sendMessage("hello", 1, true)`에서 `1`과 `true`가 무엇인지 알려면 함수 정의를 봐야 한다.

**해결책 1 — 명명된 매개변수**: 지원 언어에서는 `sendMessage(message: "hello", priority: 1, allowRetry: true)`. TS/JS는 명명된 매개변수가 없지만 **객체 구조분해(object destructuring)**로 같은 효과를 낸다(원서도 TS로 이 기법을 보여준다).

<details>
<summary>의사코드 (원서) — 예제 5.18 TypeScript 객체 구조분해</summary>

```typescript
interface SendMessageParams {
  message: string,
  priority: number,
  allowRetry: boolean,
}

async function sendMessage(
  {message, priority, allowRetry}: SendMessageParams) {
  const outcome = await XhrWrapper.send(END_POINT, message, priority);
  if (outcome.failed() && allowRetry) { ... }
}
```

</details>

```typescript
/** sendMessage 호출 시 전달하는 매개변수. */
interface SendMessageParams {
  /** 보낼 메시지 본문 */
  message: string;
  /** 메시지 우선순위 */
  priority: number;
  /** 전송 실패 시 재시도 허용 여부 */
  allowRetry: boolean;
}

async function sendMessage(
  { message, priority, allowRetry }: SendMessageParams,
): Promise<void> {
  const outcome = await XhrWrapper.send(END_POINT, message, priority);
  if (outcome.failed() && allowRetry) {
    // ...
  }
}

// 호출 측: 각 값이 이름과 연결되어 명명된 매개변수처럼 읽힌다
sendMessage({ message: "hello", priority: 1, allowRetry: true });
```

**해결책 2 — 서술적 유형 사용**: `Int`·`Boolean` 대신 `MessagePriority` 클래스, `RetryPolicy` **열거형**(`ALLOW_RETRY`/`DISALLOW_RETRY`)을 쓰면 호출이 자명해진다.

> **핵심 통찰**: `BoundingBox(10, 50, 20, 5)`처럼 **훌륭한 해결책이 없을 때도 있다**(5.6.4). 이때는 인라인 주석(`/* top= */ 10`)이 차선책이지만 최신 유지 부담이 있다. **IDE가 매개변수 이름을 보여주는 기능(5.6.5)에 의존하지 말라** — 코드 리뷰·병합 도구는 IDE 도움 없이 코드만 보기 때문이다.

---

## 7. 설명되지 않은 값을 사용하지 말라 (5.7)

하드코딩된 값에는 두 정보가 있다 — **값이 무엇인지**(컴퓨터가 알아야 함)와 **값이 무엇을 의미하는지**(개발자가 알아야 함). 후자를 빠뜨리기 쉽다. 예: `getKineticEnergy()`의 `907.1847`(미국톤→kg)과 `0.44704`(mph→m/s)는 의미가 불명확해, 누군가 `getMassUsTon()`을 `getMassKg()`로 바꿔도 `907.1847`을 지워야 하는지 몰라 **버그**가 난다.

- **해결책 A — 잘 명명된 상수**: `const KILOGRAMS_PER_US_TON = 907.1847;`
- **해결책 B — 공급자 함수**: `kilogramsPerUsTon()`이 값을 반환
- **해결책 C — 헬퍼 함수**: `usTonsToKilograms(value)`가 변환을 하위 문제로 처리(계수는 구현 세부사항으로 숨김)

<details>
<summary>의사코드 (원서) — 예제 5.22 잘 명명된 상수</summary>

```java
class Vehicle {
  private const Double KILOGRAMS_PER_US_TON = 907.1847;
  private const Double METERS_PER_SECOND_PER_MPH = 0.44704;

  Double getKineticEnergy() {
    return 0.5 *
      getMassUsTon() * KILOGRAMS_PER_US_TON *
      Math.pow(getSpeedMph() * METERS_PER_SECOND_PER_MPH, 2);
  }
}
```

</details>

```typescript
class Vehicle {
  private static readonly KILOGRAMS_PER_US_TON = 907.1847;
  private static readonly METERS_PER_SECOND_PER_MPH = 0.44704;

  getKineticEnergy(): number {
    return 0.5 *
      this.getMassUsTon() * Vehicle.KILOGRAMS_PER_US_TON *
      Math.pow(this.getSpeedMph() * Vehicle.METERS_PER_SECOND_PER_MPH, 2);
  }
}
```

---

## 8. 익명 함수를 적절하게 사용하라 (5.8)

익명 함수(anonymous function)는 이름 없는 함수로, 필요한 지점에 인라인으로 정의된다. **간단하고 자명한 로직에는 좋다**(예: `filter(feedback => !feedback.getComment().isEmpty())`). 하지만 문제가 있다.

- **자명하지 않으면 가독성이 떨어진다**(5.8.2): 패리티 비트 검사 같은 로직을 익명 함수로 넣으면 무엇을 하는지 알 수 없다 → **명명 함수 `isParityBitCorrect`로 추출**(5.8.3). 이름이 설명을 제공하고 재사용도 쉬워진다.
- **길면 문제가 된다**(5.8.4): 중첩된 긴 익명 함수(`buildFeedbackListItems`)는 UI에 무엇이 표시되는지 파악하기 어렵다 → **여러 명명 함수로 분리**(`buildTitle`, `buildCommentText`, `buildCategory`)(5.8.5).

> **핵심 통찰**: 함수형 스타일(*functional programming - 상태 변경 명령문 대신 함수 호출·참조로 로직을 표현*)을 채택하는 것과 인라인 익명 함수를 쓰는 것은 별개다. **명명 함수로도 함수형 스타일 코드를 쓸 수 있다.** 익명 함수가 두세 줄을 넘으면 명명 함수로 나누는 것이 가독성에 좋다.

---

## 9. 프로그래밍 언어의 새로운 기능을 적절하게 사용하라 (5.9)

언어 설계자는 신중하게 기능을 추가하므로 새 기능이 가독성·견고성을 높이는 경우가 많다(예: 자바 8 스트림으로 리스트 필터링이 간결해짐). 하지만:

- **불분명한 기능은 혼동을 일으킨다**(5.9.2): 팀이 자바 스트림에 익숙하지 않다면, 스트림이 주는 개선이 그 혼란보다 작을 수 있다.
- **작업에 가장 적합한 도구를 쓰라**(5.9.3): 맵에서 값 찾기는 `map.get(key)`가 정답이지, 스트림으로 전체를 필터링하는 것은 가독성·효율 모두 나쁘다.

> **핵심 통찰**: 새 기능을 **단지 새로워서가 아니라 작업에 적합해서** 쓴다는 점을 분명히 하라.

---

## 10. 코드 품질 6대 요소 연결

이 장은 6대 요소 중 **읽기 쉬움(가독성)**을 정면으로 다룬다. 동시에 여러 기법이 다른 요소에도 기여한다.

| 6대 요소 | 이 장이 기여하는가? | 근거 |
|---|---|---|
| 읽기 쉬움 | ✅ (직접) | 서술적 이름·일관 스타일·중첩 최소화 등 전 절 |
| 예측 가능 | (부수) | 일관된 스타일이 오해(connectionManager)를 막는다 |
| 오용 어렵게 | (부수) | 서술적 유형(열거형)은 잘못된 인수를 막는다 |
| 모듈화 | (부수) | 함수 분리(5.5·5.8)는 모듈화로 이어진다 |
| 재사용·일반화 | (부수) | 상수·명명 함수·헬퍼 추출은 재사용을 돕는다 |

> **핵심 통찰**: 가독성 기법의 상당수(중첩 제거·긴 함수 분리·설명되지 않은 값을 헬퍼로)는 결국 **"함수를 작게, 하위 문제로 나누기"**(2장)로 수렴한다. 가독성과 모듈화는 같은 뿌리를 공유한다.

---

## 요약

- 가독성이 떨어지면 이해에 시간이 낭비되고, 오해로 버그가 생기며, 수정 시 코드가 깨진다.
- 가독성을 높이려면 코드가 더 장황해질 수 있는데, 이는 대개 가치 있는 절충이다.
- **서술적 이름**을 쓰고(주석으로 대체 금지), 주석은 **"왜"와 상위 요약**에 쓴다.
- **코드 줄 수에 집착하지 말고**, 일관된 스타일을 지키며, **깊은 중첩은 일찍 반환·함수 분리**로 편다.
- **함수 호출도 읽히게** — 명명된 매개변수(TS는 객체 구조분해)·서술적 유형(열거형)을 쓴다.
- **설명되지 않은 값을 쓰지 말라** — 상수·공급자·헬퍼 함수로 의미를 드러낸다.
- **익명 함수는 간단할 때만**, 복잡·긴 로직은 명명 함수로 분리한다.
- 언어의 새 기능은 **작업에 적합할 때만** 쓴다.
- 무엇보다 다른 개발자의 입장을 **공감**하고 상식과 판단을 적용해야 한다.
