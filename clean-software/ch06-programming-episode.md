# Chapter 6: A Programming Episode (프로그래밍 에피소드)

## 핵심 질문

테스트 주도 개발(TDD)과 짝 프로그래밍(*pair programming - 두 명의 개발자가 한 컴퓨터에서 함께 코드를 작성하는 실천 방법*)으로 실제 애플리케이션을 만드는 과정은 어떻게 진행되는가? 초기에 세웠던 설계(UML 다이어그램)는 왜 결국 폐기되는가? 그리고 단일 책임 원칙(SRP)을 위반한 코드는 TDD의 작은 단계들 사이에서 어떻게 자연스럽게 분리되는가?

> 설계와 프로그래밍은 사람이 하는 일이다. 그것을 잊어버리면 모든 것을 잃게 된다.<br>— 비야네 스트로스트룹(Bjarne Stroustrup), 1991

---

## 1. 에피소드 개요

이 챕터는 밥 코스(Bob Koss)와 밥 마틴(Bob Martin) 두 사람이 2000년 후반 호텔 방에서 실제로 진행한 짝 프로그래밍 세션을 **대화 형식 그대로** 재현한 것이다. 만든 것은 **볼링 게임 스코어 계산 프로그램**이다.

### 1.1 이 에피소드의 특징

- 완전한 사전 설계가 없다 — 냅킨에 그린 단순한 UML로 시작했지만, 결국 다이어그램의 두 클래스(`Throw`, `Frame`) 모두 코드에는 등장하지 않는다
- TDD로 작은 단계를 반복하며 진행한다 — 테스트 작성 → 컴파일 통과 → 테스트 통과 → 리팩토링
- 많은 실수, 혼란, 오해가 그대로 드러난다
- 그럼에도 불구하고 결과물은 매우 단순하고 깔끔하다

> **핵심 통찰**: 이 프로세스는 사람이 하는 모든 프로세스가 그렇듯 **지저분하다**. 하지만 이런 지저분한 프로세스에서 도출된 결과의 질서 정연함은 놀랍다. **사전 설계의 우아함이 아니라 작은 단계들의 누적이 깔끔한 코드를 만든다.**

### 1.2 볼링 점수 규칙 (요약)

- 한 게임은 10개의 프레임으로 구성
- 각 프레임에 최대 2번의 투구(*throw - 볼을 굴려 핀을 쓰러뜨리는 한 번의 시도*)
- **스트라이크(Strike)**: 첫 투구에 10핀 다 쓰러뜨림 → 프레임 점수 = 10 + 다음 두 공의 점수
- **스페어(Spare)**: 두 투구로 10핀 다 쓰러뜨림 → 프레임 점수 = 10 + 다음 한 공의 점수
- **일반 프레임**: 두 공의 핀 합계
- 10번째 프레임 예외 — 스페어면 1개, 스트라이크면 2개의 공을 더 던질 수 있다

---

## 2. 첫 번째 설계: UML과 후보 클래스

두 사람은 짧은 대화로 후보 객체를 식별했다.

```
┌──────┐    1  ┌───────┐  1..3  ┌───────┐
│ Game │──────▶│ Frame │───────▶│ Throw │
└──────┘   10  └───────┘        └───────┘
```

- `Game` — 10개의 `Frame`을 보유
- `Frame` — 1~3번의 `Throw`를 보유
- `Throw` — 한 번의 투구

**의존성 사슬의 끝부터** 거꾸로 작업하면 테스트가 더 쉬워 보였다. 그래서 `Throw`부터 시작했다.

### 2.1 첫 번째 폐기: Throw 클래스

`Throw`가 어떤 행위를 해야 하는지 자문하자 답이 없었다.

> 밥 코스: "만약 이것이 아무 행위도 하지 않는다면 어떻게 중요한 것이 될 수 있겠는가?"

`Throw`는 단지 `int` 값이라는 결론이 났다. **첫 번째 후보 객체가 코드 한 줄 쓰기 전에 사라졌다.**

---

## 3. TDD 사이클: Frame → Game으로의 점프

### 3.1 Step 1: Frame의 첫 테스트 (Red → Green)

`Frame`의 가장 단순한 테스트부터 시작했다.

<details>
<summary>원문 Java 코드</summary>

```java
// TestFrame.java
public void testScoreNoThrows() {
    Frame f = new Frame();
    assertEquals(0, f.getScore());
}

// Frame.java
public class Frame {
    public int getScore() {
        return 0;
    }
}
```

</details>

```typescript
// TestFrame.ts
test('testScoreNoThrows', () => {
    const f = new Frame();
    expect(f.getScore()).toBe(0);
});

// Frame.ts
class Frame {
    getScore(): number {
        return 0;
    }
}
```

테스트는 통과하지만, **`getScore`는 바보 같은 함수**다.

### 3.2 Step 2: 투구를 더하는 테스트

```typescript
// 다음 테스트
test('testAddOneThrow', () => {
    const f = new Frame();
    f.add(5);
    expect(f.getScore()).toBe(5);
});

// 통과시키기
class Frame {
    private itsScore = 0;
    getScore(): number { return this.itsScore; }
    add(pins: number): void { this.itsScore += pins; }
}
```

### 3.3 막다른 골목: Frame이 스코어를 계산할 수 있는가?

다음 테스트로 스트라이크를 표현하려고 `add(10)`을 호출하면, `getScore()`는 무엇을 반환해야 하나?

- 스트라이크의 점수는 **다음 두 공의 점수**까지 알아야 정해진다
- 그렇다면 `Frame`은 다음 `Frame`을 알아야 한다
- 그러면 `Game`은 `Frame`에 의존하고, `Frame`도 `Game`에 의존한다 (양방향 의존)

> **핵심 통찰**: TDD의 작은 단계를 밟는 동안 **테스트가 작성되지 않으면 설계가 잘못된 신호**다. "스트라이크 테스트의 assertion을 어떻게 써야 할지 모르겠다" — 이 막힘 자체가 객체 책임이 잘못 배치되어 있다는 증거다.

두 사람은 `Frame` 작업을 멈추고 `Game`으로 점프하기로 결정한다.

---

## 4. Game으로 점프: 두 번째 폐기

### 4.1 Game의 간단한 테스트들

```typescript
test('testOneThrow', () => {
    const g = new Game();
    g.add(5);
    expect(g.score()).toBe(5);
});

test('testTwoThrowsNoMark', () => {
    const g = new Game();
    g.add(5);
    g.add(4);
    expect(g.score()).toBe(9);
});
```

`Game`은 처음엔 단순한 누적 합산이었다.

### 4.2 결정적 순간: scoreForFrame이 필요하다

다음 테스트에서 새 요구가 드러났다.

```typescript
test('testFourThrowsNoMark', () => {
    g.add(5); g.add(4); g.add(7); g.add(2);
    expect(g.score()).toBe(18);
    expect(g.scoreForFrame(1)).toBe(9);
    expect(g.scoreForFrame(2)).toBe(18);
});
```

이 시점에서 **Frame 객체는 정말로 필요한가?** `Game` 내부에 `int` 배열을 두고 `scoreForFrame`이 배열을 순회하면 충분하다.

<details>
<summary>원문 Java 코드</summary>

```java
public class Game {
    private int itsScore = 0;
    private int[] itsThrows = new int[21];
    private int itsCurrentThrow = 0;

    public int score() { return itsScore; }
    public void add(int pins) {
        itsThrows[itsCurrentThrow++] = pins;
        itsScore += pins;
    }
    public int scoreForFrame(int theFrame) {
        int ball = 0;
        int score = 0;
        for (int currentFrame = 0; currentFrame < theFrame; currentFrame++) {
            score += itsThrows[ball++] + itsThrows[ball++];
        }
        return score;
    }
}
```

</details>

```typescript
class Game {
    private itsScore = 0;
    private itsThrows: number[] = new Array(21).fill(0);
    private itsCurrentThrow = 0;

    score(): number {
        return this.itsScore;
    }

    add(pins: number): void {
        this.itsThrows[this.itsCurrentThrow++] = pins;
        this.itsScore += pins;
    }

    scoreForFrame(theFrame: number): number {
        let ball = 0;
        let score = 0;
        for (let currentFrame = 0; currentFrame < theFrame; currentFrame++) {
            const firstThrow = this.itsThrows[ball++];
            const secondThrow = this.itsThrows[ball++];
            score += firstThrow + secondThrow;
        }
        return score;
    }
}
```

> **Uncle Bob의 경험**: 매직 넘버 21이 등장한 순간이다. 21은 한 게임의 가능한 최대 투구 횟수다. 매직 넘버를 두는 것이 늘 나쁘지는 않다 — 단, **그 의미를 이해하기 쉬워야 한다**. 여기서는 게임 도메인이 작아서 21이라는 숫자가 곧 식별된다.

### 4.3 두 번째 폐기: Frame 클래스

이 시점에서 **두 번째 후보 객체인 `Frame`도 사라졌다.** 처음의 UML 다이어그램에 있던 두 클래스가 모두 코드에 등장하지 않는다.

> **핵심 통찰**: 사전 설계가 그릇되었다는 뜻은 아니다. **설계는 코드를 작성하면서 자연스럽게 발전한다**. UML은 아이디어 탐색의 도구이며, 만들었다고 해서 그것을 따라야 한다고 가정해서는 안 된다.

---

## 5. 스페어와 스트라이크: 복잡성의 등장

### 5.1 스페어 처리

```typescript
test('testSimpleSpare', () => {
    g.add(3); g.add(7);  // 첫 프레임 스페어
    g.add(3);            // 다음 공
    expect(g.scoreForFrame(1)).toBe(13);  // 10 + 3
});
```

스페어 처리를 위해 `scoreForFrame`은 각 프레임에서 스페어인지를 검사하고, 그렇다면 다음 공 한 개를 더 더해야 한다.

```typescript
scoreForFrame(theFrame: number): number {
    let ball = 0;
    let score = 0;
    for (let currentFrame = 0; currentFrame < theFrame; currentFrame++) {
        if (this.itsThrows[ball] + this.itsThrows[ball + 1] === 10) {  // 스페어
            score += 10 + this.itsThrows[ball + 2];
            ball += 2;
        } else {
            score += this.itsThrows[ball] + this.itsThrows[ball + 1];
            ball += 2;
        }
    }
    return score;
}
```

### 5.2 스트라이크 처리

```typescript
test('testSimpleStrike', () => {
    g.add(10);            // 스트라이크
    g.add(3); g.add(6);   // 다음 프레임
    expect(g.scoreForFrame(1)).toBe(19);  // 10 + 3 + 6
    expect(g.score()).toBe(28);
});
```

스트라이크는 한 공으로 프레임이 끝나므로 `ball`을 1만 증가시킨다.

```typescript
if (this.itsThrows[ball] === 10) {  // 스트라이크
    score += 10 + this.itsThrows[ball + 1] + this.itsThrows[ball + 2];
    ball += 1;
} else if (...) { ... }
```

---

## 6. SRP의 압박: Game의 책임이 갈라진다

이 시점에서 `Game` 클래스는 두 가지 일을 하고 있다.

| 책임 | 코드 |
|------|------|
| **투구 받기 / 프레임 진행 추적** | `add()`, `itsCurrentFrame`, `firstThrowInFrame` |
| **점수 계산** | `scoreForFrame()`, `itsThrows[]` |

> 밥 코스: "Game이 단일 책임 원칙을 위반하고 있는 것 같네. 이건 투구를 받고, 각 프레임의 스코어를 기록하는 방법을 알고 있지. **Scorer 객체에 대해 어떻게 생각하나?**"

처음엔 밥 마틴이 미루었다 — "지금 내 관심거리는 스코어를 기록하는 것이 제대로 동작하게 하는 것이네. 일단 모든 게 잘 자리잡게 하고 난 다음에야 SRP의 가치 문제를 논할 수 있을 걸세."

### 6.1 책임 분리: Scorer 추출

기능이 모두 동작한 뒤, 마침내 `Scorer` 클래스를 추출한다.

<details>
<summary>원문 Java 코드 - 최종 Game</summary>

```java
public class Game {
    private int itsCurrentFrame = 0;
    private boolean firstThrowInFrame = true;
    private Scorer itsScorer = new Scorer();

    public int score() {
        return scoreForFrame(itsCurrentFrame);
    }

    public void add(int pins) {
        itsScorer.addThrow(pins);
        adjustCurrentFrame(pins);
    }

    private void adjustCurrentFrame(int pins) {
        if (lastBallInFrame(pins))
            advanceFrame();
        else
            firstThrowInFrame = false;
    }

    private boolean lastBallInFrame(int pins) {
        return strike(pins) || !firstThrowInFrame;
    }

    private boolean strike(int pins) {
        return (firstThrowInFrame && pins == 10);
    }

    private void advanceFrame() {
        itsCurrentFrame = Math.min(10, itsCurrentFrame + 1);
    }

    public int scoreForFrame(int theFrame) {
        return itsScorer.scoreForFrame(theFrame);
    }
}
```

</details>

```typescript
// Game.ts - 책임: 프레임 진행 추적
class Game {
    private itsCurrentFrame = 0;
    private firstThrowInFrame = true;
    private itsScorer = new Scorer();

    score(): number {
        return this.scoreForFrame(this.itsCurrentFrame);
    }

    add(pins: number): void {
        this.itsScorer.addThrow(pins);
        this.adjustCurrentFrame(pins);
    }

    private adjustCurrentFrame(pins: number): void {
        if (this.lastBallInFrame(pins)) {
            this.advanceFrame();
        } else {
            this.firstThrowInFrame = false;
        }
    }

    private lastBallInFrame(pins: number): boolean {
        return this.strike(pins) || !this.firstThrowInFrame;
    }

    private strike(pins: number): boolean {
        return this.firstThrowInFrame && pins === 10;
    }

    private advanceFrame(): void {
        this.itsCurrentFrame = Math.min(10, this.itsCurrentFrame + 1);
    }

    scoreForFrame(theFrame: number): number {
        return this.itsScorer.scoreForFrame(theFrame);
    }
}
```

<details>
<summary>원문 Java 코드 - 최종 Scorer</summary>

```java
public class Scorer {
    private int ball;
    private int[] itsThrows = new int[21];
    private int itsCurrentThrow = 0;

    public void addThrow(int pins) {
        itsThrows[itsCurrentThrow++] = pins;
    }

    public int scoreForFrame(int theFrame) {
        ball = 0;
        int score = 0;
        for (int currentFrame = 0; currentFrame < theFrame; currentFrame++) {
            if (strike()) {
                score += 10 + nextTwoBallsForStrike();
                ball++;
            } else if (spare()) {
                score += 10 + nextBallForSpare();
                ball += 2;
            } else {
                score += twoBallsInFrame();
                ball += 2;
            }
        }
        return score;
    }

    private boolean strike() { return itsThrows[ball] == 10; }
    private boolean spare() { return (itsThrows[ball] + itsThrows[ball + 1]) == 10; }
    private int nextTwoBallsForStrike() { return itsThrows[ball + 1] + itsThrows[ball + 2]; }
    private int nextBallForSpare() { return itsThrows[ball + 2]; }
    private int twoBallsInFrame() { return itsThrows[ball] + itsThrows[ball + 1]; }
}
```

</details>

```typescript
// Scorer.ts - 책임: 점수 계산
class Scorer {
    private ball = 0;
    private itsThrows: number[] = new Array(21).fill(0);
    private itsCurrentThrow = 0;

    addThrow(pins: number): void {
        this.itsThrows[this.itsCurrentThrow++] = pins;
    }

    scoreForFrame(theFrame: number): number {
        this.ball = 0;
        let score = 0;
        for (let currentFrame = 0; currentFrame < theFrame; currentFrame++) {
            if (this.strike()) {
                score += 10 + this.nextTwoBallsForStrike();
                this.ball++;
            } else if (this.spare()) {
                score += 10 + this.nextBallForSpare();
                this.ball += 2;
            } else {
                score += this.twoBallsInFrame();
                this.ball += 2;
            }
        }
        return score;
    }

    private strike(): boolean {
        return this.itsThrows[this.ball] === 10;
    }

    private spare(): boolean {
        return this.itsThrows[this.ball] + this.itsThrows[this.ball + 1] === 10;
    }

    private nextTwoBallsForStrike(): number {
        return this.itsThrows[this.ball + 1] + this.itsThrows[this.ball + 2];
    }

    private nextBallForSpare(): number {
        return this.itsThrows[this.ball + 2];
    }

    private twoBallsInFrame(): number {
        return this.itsThrows[this.ball] + this.itsThrows[this.ball + 1];
    }
}
```

### 6.2 책임 분리 결과

```
┌──────────────────────────────┐         ┌──────────────────────────────┐
│           Game               │────────▶│           Scorer             │
├──────────────────────────────┤         ├──────────────────────────────┤
│ + score()                    │         │ + addThrow(pins)             │
│ + add(pins)                  │         │ + scoreForFrame(theFrame)    │
│ + scoreForFrame(theFrame)    │         ├──────────────────────────────┤
├──────────────────────────────┤         │ - strike() / spare() / ...   │
│ - adjustCurrentFrame(pins)   │         └──────────────────────────────┘
│ - lastBallInFrame / strike   │
│ - advanceFrame()             │
└──────────────────────────────┘
   책임: 프레임 진행 추적            책임: 점수 계산
```

이 분리는 **8장 SRP**에서 자세히 다뤄진다. 두 책임은 변경의 이유가 다르다 — 프레임 진행 규칙이 바뀌는 것과 점수 계산 규칙이 바뀌는 것은 별개다.

---

## 7. 최종 테스트 스위트

완성된 코드의 견고함은 테스트 스위트가 증명한다.

```typescript
describe('Game', () => {
    let g: Game;
    beforeEach(() => { g = new Game(); });

    test('두 투구, 마크 없음', () => {
        g.add(5); g.add(4);
        expect(g.score()).toBe(9);
    });

    test('스페어 처리', () => {
        g.add(3); g.add(7); g.add(3);
        expect(g.scoreForFrame(1)).toBe(13);
    });

    test('스트라이크 처리', () => {
        g.add(10); g.add(3); g.add(6);
        expect(g.scoreForFrame(1)).toBe(19);
        expect(g.score()).toBe(28);
    });

    test('퍼펙트 게임 = 300', () => {
        for (let i = 0; i < 12; i++) {
            g.add(10);
        }
        expect(g.score()).toBe(300);
    });

    test('아슬아슬 (299)', () => {
        for (let i = 0; i < 11; i++) {
            g.add(10);
        }
        g.add(9);
        expect(g.score()).toBe(299);
    });

    test('10번째 프레임 스페어', () => {
        for (let i = 0; i < 9; i++) {
            g.add(10);
        }
        g.add(9); g.add(1); g.add(1);
        expect(g.score()).toBe(270);
    });
});
```

---

## 8. 결론: 다이어그램은 언제 불필요한가

Uncle Bob이 이 에피소드를 공개한 후 받은 반응 중 흥미로운 것들이 있었다.

| 비판 | Uncle Bob의 응답 |
|------|------------------|
| "객체지향 설계가 거의 없다" | 모든 프로그램이 객체지향 설계를 필요로 하지는 않는다. 이 문제는 단순한 분할로 충분했다 |
| "Frame 클래스가 있어야 한다" | 시도해본 사람도 있었다. 그 결과 훨씬 크고 복잡한 프로그램이 되었다 |
| "UML이 부정확했다" | 그렇다. 사전에 완전한 설계를 하지 않았다. 시퀀스 다이어그램을 추가했어도 결론은 같았을 것이다 |

> **Uncle Bob의 경험**: 다이어그램은 때로는 불필요할 수 있다. 언제 불필요한가? **확인할 코드 없이 다이어그램을 만들고, 그것을 따르려고 할 때**다. 아이디어를 탐색하기 위해 다이어그램을 그리는 일은 문제될 게 없다. 하지만 다이어그램을 만들었다고 해서 그것이 그 과업에 가장 최적의 설계라고 가정해서는 안 된다.

### 8.1 핵심 메시지

> **핵심 통찰**: 테스트를 먼저 작성하여 **작은 단계를 밟아 나가면서** 최적 설계가 개선될 수 있다는 사실을 알게 될 것이다. 사전 설계의 우아함을 추구하기보다 **변화하는 이해에 코드를 맞춰가는 능력**이 더 가치 있다.

---

## 9. 자주 하는 실수

| 안티패턴 | 문제 | 해결 |
|----------|------|------|
| **사전 설계 맹신** — UML/다이어그램을 코드 없이 만들고 그대로 따름 | 실제로 필요한 책임 배치와 다를 수 있음 | 다이어그램은 탐색 도구로만, 코드가 진실의 원천 |
| **TDD 막힘을 무시** — 테스트 작성이 막혔는데 코드부터 작성 | 설계 결함을 놓침 | "테스트가 잘 안 써진다 = 책임이 잘못 배치되었다"는 신호로 인식 |
| **SRP 위반 무한 방치** — Game처럼 모든 책임이 한 클래스에 쌓임 | 결국 한 부분 변경이 다른 부분을 깨뜨림 | 기능이 안정된 후 리팩토링으로 분리 (Scorer 추출) |
| **불필요한 후보 객체 보존** — UML에 있다고 Frame, Throw를 억지로 클래스로 만듦 | 코드가 부풀고 복잡해짐 | 행위가 없는 객체는 폐기. 데이터만 있으면 원시 타입으로 |
| **매직 넘버 회피의 과잉** — 21을 무조건 상수로 추출 | 작은 도메인에선 오히려 가독성 저하 | 의미가 명확하면 그대로 두어도 됨 |

---

## 10. TDD가 가르쳐준 것

이 에피소드에서 TDD가 한 일을 정리해본다.

| TDD가 한 일 | 어떻게? |
|-------------|---------|
| **불필요한 후보 객체 제거** | `Throw`, `Frame`이 행위 없음을 테스트 작성 단계에서 드러냄 |
| **막다른 골목 조기 발견** | "스트라이크 assertion을 못 쓰겠다"가 양방향 의존 신호가 됨 |
| **점진적 책임 식별** | 처음엔 누적 합산 → `scoreForFrame` → 스페어 → 스트라이크 → Scorer 분리 |
| **자신감 있는 리팩토링** | 30여 개 테스트가 안전망이 되어 Scorer 추출이 안전 |
| **이해의 진화 수용** | UML과 다르게 가도, 테스트가 통과하면 OK |

---

## 요약

- **짝 프로그래밍 + TDD**로 볼링 점수 계산 프로그램을 만드는 실제 과정을 재현한 챕터
- 초기 UML 다이어그램의 후보 객체 `Throw`와 `Frame`은 **모두 폐기**되었다 — 행위가 없는 객체는 객체일 필요가 없다
- TDD의 막힘은 **설계 결함의 신호**다 — 테스트가 잘 안 써진다면 책임 배치를 의심하라
- `Game` 클래스는 한동안 SRP를 위반했지만, 기능이 안정된 후 `Game`(프레임 진행 추적) + `Scorer`(점수 계산)로 분리되었다
- **사전 설계의 우아함이 아니라 작은 단계들의 누적**이 깔끔한 코드를 만든다
- 다이어그램은 **아이디어 탐색**의 도구일 뿐, 코드 없이 만든 다이어그램을 따라야 한다고 가정해서는 안 된다
- 마틴의 결론: **테스트를 먼저 작성하여 작은 단계를 밟아 나가면, 최적 설계는 자연스럽게 개선된다**
