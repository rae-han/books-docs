# Chapter 12: Compound Patterns (복합 패턴)

## 핵심 질문

- 여러 디자인 패턴을 **함께** 쓰면 어떤 시너지가 나는가?
- "여러 패턴을 섞어 쓰는 것"과 진짜 **복합 패턴**은 무엇이 다른가?
- 복합 패턴의 왕 **MVC(Model-View-Controller)** 는 어떤 패턴들의 조합인가?
- (TS/프런트) React·Vue 같은 현대 프레임워크는 MVC와 어떤 관계인가?

> **복합 패턴 정의**: 반복적으로 생기는 일반적인 문제를 해결하기 위해 **2개 이상의 패턴을 결합**해 사용하는 것. 단순히 여러 패턴을 함께 쓰는 것과는 다르다 — 복합 패턴은 "일반적 문제의 해법"이어야 한다.

---

## 1. 오리 시뮬레이터 재등장 — 6개 패턴 함께 쓰기

1장의 `SimUDuck`을 다시 만들며 요구가 하나씩 늘 때마다 패턴을 적용한다. (이것은 "복합 패턴"이 아니라 **여러 패턴을 함께 쓰는 예시**다.)

```
문제 → 적용한 패턴
─────────────────────────────────────────────
Quackable 인터페이스로 통일               (기반)
거위(Goose)도 오리처럼 → GooseAdapter      어댑터(7장)
꽥 소리 횟수 세기 → QuackCounter           데코레이터(3장)
데코레이터 누락 방지 → CountingDuckFactory  추상 팩토리(4장)
오리 무리 관리 → Flock                     컴포지트(9장) + 반복자(9장)
꽥 소리 실시간 관찰 → Quackologist          옵저버(2장)
```

```typescript
interface Quackable extends QuackObservable {
  quack(): void;
}

// 어댑터: 거위를 오리로
class GooseAdapter implements Quackable {
  constructor(private goose: Goose) {}
  quack(): void { this.goose.honk(); }
}

// 데코레이터: 꽥 횟수 세기
class QuackCounter implements Quackable {
  static numberOfQuacks = 0;
  constructor(private duck: Quackable) {}
  quack(): void {
    this.duck.quack();       // 위임
    QuackCounter.numberOfQuacks++; // 기능 추가
  }
}

// 컴포지트: 오리 무리 (자신도 Quackable)
class Flock implements Quackable {
  private quackers: Quackable[] = [];
  add(quacker: Quackable): void { this.quackers.push(quacker); }
  quack(): void {
    for (const quacker of this.quackers) { // 반복자
      quacker.quack();                     // 잎이든 무리든 동일 호출(재귀)
    }
  }
}
```

<details>
<summary>Java 원본 (Flock)</summary>

```java
public class Flock implements Quackable {
    List<Quackable> quackers = new ArrayList<Quackable>();
    public void add(Quackable quacker) { quackers.add(quacker); }
    public void quack() {
        Iterator<Quackable> iterator = quackers.iterator();
        while (iterator.hasNext()) {
            Quackable quacker = iterator.next();
            quacker.quack();
        }
    }
}
```
</details>

> **무엇이든 물어보세요 (Q&A)**
>
> **Q. 이게 복합 패턴인가요?**
> A. 아니다. 그냥 **여러 패턴을 함께 쓴** 것뿐이다. 게다가 실전에서 이렇게 패턴을 억지로 다 우겨넣지는 않는다(13장에서 다룸). "패턴을 써야지"가 아니라 **문제에 맞을 때만** 써야 한다. 진짜 복합 패턴은 다음의 **MVC**다.

---

## 2. MVC — 복합 패턴의 왕

음악 플레이어(iTunes류)를 생각하자. **모델**은 곡 데이터·재생 로직을, **뷰**는 화면 표시를, **컨트롤러**는 사용자 입력 처리를 맡는다.

```
        [사용자]
           │ ① 조작(버튼 클릭)
           ▼
        ┌──────┐  ② 상태 바꿔줘   ┌───────┐
        │ View │ ───────────────▶ │Controller│
        └──────┘                  └───────┘
           ▲                          │ ③ 모델 조작
     ④ 상태 변경 통지(옵저버)          ▼
           │                      ┌───────┐
           └──────────────────────│ Model │
             ⑤ 상태 요청(getState)  └───────┘
```

1. 사용자는 **뷰**만 조작한다.
2. 뷰는 사용자 행동을 **컨트롤러**에 넘긴다.
3. 컨트롤러는 입력을 해석해 **모델**의 상태를 바꾼다.
4. 모델은 상태가 바뀌면 **옵저버(뷰)** 에게 통지한다.
5. 뷰는 모델에서 상태를 가져와 화면을 갱신한다.

---

## 3. MVC를 이루는 세 패턴

> **핵심 통찰**: MVC를 이해하는 가장 좋은 방법은 **"여러 패턴이 합쳐진 하나의 디자인"** 으로 보는 것이다. 맨땅에서 MVC를 외우면 어렵지만, 아래 세 패턴으로 분해하면 명확해진다.

| MVC 관계 | 사용된 패턴 | 역할 |
|----------|-----------|------|
| 모델 → 뷰/컨트롤러 | **옵저버**(2장) | 모델이 상태 변화를 옵저버(뷰·컨트롤러)에게 통지. **모델은 뷰·컨트롤러를 모른다**(느슨한 결합). |
| 뷰 ↔ 컨트롤러 | **전략**(1장) | **컨트롤러 = 뷰의 전략 객체**. 컨트롤러를 바꾸면 뷰의 행동이 바뀐다. 뷰는 화면 표시만, 로직은 컨트롤러에 위임. |
| 뷰 내부 | **컴포지트**(9장) | 뷰는 윈도우·패널·버튼의 **중첩 트리**. 최상위에 "갱신"을 요청하면 재귀로 전파. |

> **핵심 통찰**: **옵저버**로 모델을 뷰·컨트롤러에서 독립시켜 **한 모델에 여러 뷰**를 붙일 수 있고, **전략**으로 뷰와 컨트롤러를 분리해 뷰를 재사용할 수 있으며, **컴포지트**로 복잡한 UI를 하나처럼 다룬다.

---

## 4. 구현 — BPM 제어 도구 (DJ 뷰)

### 모델 — 옵저버로 상태를 알린다

```typescript
interface BeatModelInterface {
  on(): void;
  off(): void;
  setBPM(bpm: number): void;
  getBPM(): number;
  registerObserver(o: BPMObserver): void; // 옵저버 등록
  removeObserver(o: BPMObserver): void;
}

class BeatModel implements BeatModelInterface {
  private bpm = 90;
  private bpmObservers: BPMObserver[] = [];

  setBPM(bpm: number): void {
    this.bpm = bpm;
    this.notifyBPMObservers(); // 상태가 바뀌면 옵저버에게 통지
  }
  getBPM(): number { return this.bpm; }

  registerObserver(o: BPMObserver): void { this.bpmObservers.push(o); }
  private notifyBPMObservers(): void {
    for (const o of this.bpmObservers) { o.updateBPM(); }
  }
  // on()/off()/removeObserver() ...
}
```

### 컨트롤러 — 뷰의 전략

```typescript
interface ControllerInterface {
  setBPM(bpm: number): void;
  increaseBPM(): void;
  decreaseBPM(): void;
}

class BeatController implements ControllerInterface {
  constructor(private model: BeatModelInterface, private view: DJView) {}

  increaseBPM(): void {
    // 사용자 입력을 해석해 모델을 조작
    this.model.setBPM(this.model.getBPM() + 1);
  }
  setBPM(bpm: number): void { this.model.setBPM(bpm); }
  // decreaseBPM() ...
}
```

### 뷰 — 모델의 옵저버이자, 컨트롤러에 행동을 위임

```typescript
class DJView implements BPMObserver {
  constructor(
    private controller: ControllerInterface,
    private model: BeatModelInterface,
  ) {
    this.model.registerObserver(this); // 모델의 옵저버로 등록
  }

  // 모델이 상태 변화를 통지하면 호출됨
  updateBPM(): void {
    const bpm = this.model.getBPM();       // 모델에서 상태를 가져와 갱신
    this.setDisplay(`Current BPM: ${bpm}`);
  }

  // 사용자가 버튼을 누르면 → 컨트롤러에 위임 (직접 모델을 만지지 않음)
  onIncreaseClicked(): void { this.controller.increaseBPM(); }
  onSetClicked(bpm: number): void { this.controller.setBPM(bpm); }

  private setDisplay(text: string): void { /* DOM 갱신 */ }
}
```

<details>
<summary>Java 원본 (DJView 일부)</summary>

```java
public class DJView implements ActionListener, BeatObserver, BPMObserver {
    BeatModelInterface model;
    ControllerInterface controller;

    public DJView(ControllerInterface controller, BeatModelInterface model) {
        this.controller = controller;
        this.model = model;
        model.registerObserver((BPMObserver) this);
    }
    public void updateBPM() {
        int bpm = model.getBPM();
        bpmOutputLabel.setText("Current BPM: " + model.getBPM());
    }
    public void actionPerformed(ActionEvent event) {
        if (event.getSource() == increaseBPMButton) {
            controller.increaseBPM(); // 컨트롤러에 위임
        }
    }
}
```
</details>

> **무엇이든 물어보세요 (Q&A)**
>
> **Q. 컨트롤러는 모델 메서드를 호출만 하는데, 왜 뷰에 그 코드를 안 넣나요?**
> A. (1) 뷰에 제어 로직까지 넣으면 뷰가 **두 역할**(화면 + 로직)로 복잡해진다(단일 책임 위반). (2) 뷰가 모델에 **밀접하게 결합**돼 재사용이 어려워진다. 컨트롤러가 제어 로직을 분리해 뷰와 모델의 결합을 끊는다.

---

## 5. TS/프런트엔드 관점 — MVC의 진화

> **핵심 통찰**: 웹 프런트엔드는 MVC의 후예다. **모델의 옵저버 패턴 = 오늘날의 "반응성(reactivity)/상태 관리"** 다. 프레임워크마다 세 조각의 경계와 데이터 흐름이 다르게 진화했다.

- **웹 MVC (Model 2)**: 서버에서 컨트롤러(요청 핸들러)가 모델을 다루고 뷰(템플릿)를 렌더링. Spring MVC, Rails, Express+템플릿.
- **React**: **단방향 데이터 흐름**. 컴포넌트 트리(**컴포지트**), 상태 변경 시 리렌더(**옵저버**의 변형), Redux/Flux는 "모델(store) → 뷰" 통지를 명시화. 컨트롤러 역할은 이벤트 핸들러·리듀서로 분산.
- **Vue**: **MVVM**(Model-View-ViewModel). `Proxy` 기반 반응성(11장의 프록시 + 옵저버)이 모델↔뷰를 자동 동기화 — MVC의 "옵저버 배관"을 언어/프레임워크가 자동화한 것.

```typescript
// React로 본 MVC의 흔적 — 옵저버(구독)+컴포지트(트리)+이벤트 위임
function BpmControl() {
  const bpm = useBeatStore((s) => s.bpm);         // 모델 구독(옵저버)
  const increaseBpm = useBeatStore((s) => s.increaseBpm); // 컨트롤러 역할

  return ( // 뷰: 컴포지트 트리
    <div>
      <span>Current BPM: {bpm}</span>
      <button onClick={increaseBpm}>▲</button> {/* 행동을 스토어에 위임 */}
    </div>
  );
}
```

> **핵심 통찰**: "모델은 뷰를 모르고, 상태 변화만 통지한다"는 MVC의 원칙은 **Redux·Zustand·MobX·Vue reactivity**에 그대로 살아 있다. 패턴 이름은 바뀌었어도 근본(옵저버로 모델↔뷰 분리)은 같다.

---

## 연습 문제 (해답 예시)

**1. 거위 생성 추상 팩토리** — `createGooseDuck()`을 추상 팩토리에 추가하고, `Goose`를 `GooseAdapter`로 감싸 반환하면 거위도 팩토리로 일관되게 만들 수 있다.

**2. 오리 코드에 숨은 패턴 찾기** — `Flock.quack()`이 `iterator`로 순회하므로 컴포지트 안에 **반복자 패턴**이 숨어 있다.

**3. `QuackCounter`에 옵저버 추가** — 데코레이터도 `Quackable`(=`QuackObservable`)이므로, `quack()` 위임 시 감싼 오리의 옵저버 등록/통지를 그대로 전달하면 된다.

**4. MVC의 다른 뷰 만들기** — 같은 `BeatModel`에 "BPM에 따라 색이 바뀌는 조명 뷰"나 "장르 텍스트 뷰"를 옵저버로 추가로 붙일 수 있다(한 모델 → 여러 뷰).

---

## 디자인 원칙 정리 (누적)

이 장에서는 **새 원칙이 추가되지 않는다**. MVC는 기존 패턴·원칙(옵저버·전략·컴포지트, 느슨한 결합·단일 책임)의 **종합 응용**이다.

---

## 요약

- **복합 패턴**은 반복되는 일반적 문제를 풀기 위해 **2개 이상의 패턴을 결합**한 것이다. (단순히 여러 패턴을 함께 쓰는 것과 구별)
- 오리 시뮬레이터는 어댑터·데코레이터·추상 팩토리·컴포지트·반복자·옵저버를 **함께** 쓴 예시일 뿐, 복합 패턴은 아니다.
- **MVC**는 진짜 복합 패턴이다: **옵저버**(모델→뷰/컨트롤러 통지) + **전략**(컨트롤러=뷰의 전략) + **컴포지트**(뷰의 UI 트리).
- 모델은 뷰·컨트롤러를 **모른 채 상태 변화만 통지**하므로, 한 모델에 여러 뷰를 붙이고 뷰·컨트롤러를 재사용할 수 있다.
- React·Vue 등 현대 프런트엔드는 MVC의 후예다 — 옵저버(반응성/상태 관리)·컴포지트(컴포넌트 트리)가 그대로 살아 있다.

---

## 다른 챕터와의 관계

- **2장 옵저버 · 1장 전략 · 9장 컴포지트**: MVC를 이루는 세 기둥. 이 장에서 하나로 합쳐진다.
- **11장 프록시**: Vue 반응성은 `Proxy`(프록시) + 옵저버의 결합이다.
- **13장 실전**: "패턴을 억지로 다 넣지 말라"는 오리 예제의 교훈이 13장으로 이어진다.

---

## 보너스: 원서 복습 요소

### 🎵 MVC 노래 (제임스 뎀시)

"모델, 뷰, 컨트롤러" — MVC를 노래로 만든 곡. "모델은 애플리케이션 존재의 의미, 뷰는 예쁘게 치장하고 나타나며, 컨트롤러는 둘 사이의 중계자"라는 가사로 MVC의 역할 분담을 재치있게 요약한다.

### 🧠 뇌 단련 (Brain Power)

1. 오리/거위가 함께 놀게 하려면? → 어댑터.
2. `Flock`을 관찰(옵저버)하면 그 안의 모든 오리가 관찰되어야 한다 — 복합 객체에 옵저버 등록 시 자식에게도 전파.
3. 같은 `BeatModel`로 만들 수 있는 다른 뷰는? → 조명 뷰, 장르 텍스트 뷰 등(한 모델 다중 뷰).

### 🔗 안전성 vs 투명성 (컴포지트 재론)

`Flock`은 `add()`를 복합 객체(Flock)에만 두어 **안전성**을 택했다(오리 잎에는 `add()`가 없음). 9장 메뉴 컴포지트는 잎에도 `add()`를 두어 **투명성**을 택했다. 상황에 맞게 조절하는 트레이드오프.

### 📝 낱말 퀴즈 (정답 단어 모음)

12장 용어들(정답은 영어): MODEL(모델), VIEW(뷰), CONTROLLER(컨트롤러), OBSERVER(옵저버), STRATEGY(전략), COMPOSITE(컴포지트), ADAPTER(어댑터), DECORATOR(데코레이터), FACTORY(팩토리), ITERATOR(반복자), COMPOUND(복합), QUACKABLE(꽥꽥), FLOCK(무리), BPM.
