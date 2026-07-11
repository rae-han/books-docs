# Chapter 07: The Adapter and Facade Patterns (어댑터 패턴과 퍼사드 패턴)

## 핵심 질문

- 인터페이스가 **호환되지 않는** 기존 클래스를, 코드를 고치지 않고 어떻게 함께 쓸까? (어댑터)
- 복잡하게 얽힌 **여러 클래스(서브시스템)** 를 어떻게 간단한 하나의 창구로 다룰까? (퍼사드)
- 데코레이터·어댑터·퍼사드는 모두 "객체를 감싸는데" 무엇이 다른가?
- "진짜 절친에게만 이야기하라"는 최소 지식 원칙은 왜 필요한가?

> **참고**: 이 장은 **어댑터**와 **퍼사드** 두 패턴을 다룬다. 둘 다 인터페이스를 바꾸지만 목적이 다르다 — 어댑터는 **변환**, 퍼사드는 **단순화**.

---

## 1. 어댑터 패턴 — 인터페이스 변환

한국 플러그를 영국 소켓에 꽂으려면 **AC 어댑터**가 필요하다. 소프트웨어도 마찬가지: 기존 코드가 기대하는 인터페이스와, 새 업체 클래스의 인터페이스가 다를 때, 그 사이를 **변환**하는 어댑터를 만든다.

### Duck과 Turkey

```typescript
interface Duck {
  quack(): void;
  fly(): void;
}

interface Turkey {
  gobble(): void; // 칠면조는 꽥이 아니라 골골
  fly(): void;    // 짧게 난다
}
```

`Duck`이 필요한 자리에 `Turkey`를 쓰려면, `Turkey`를 `Duck`처럼 보이게 하는 어댑터가 필요하다.

```typescript
/** 칠면조를 오리로 적응시키는 어댑터. 타깃(Duck)을 구현하고 어댑티(Turkey)를 보유한다. */
class TurkeyAdapter implements Duck {
  constructor(private turkey: Turkey) {}

  quack(): void {
    this.turkey.gobble(); // quack 요청 → gobble로 변환
  }

  fly(): void {
    // 칠면조는 짧게 나니, 오리만큼 날도록 5번 호출
    for (let i = 0; i < 5; i++) {
      this.turkey.fly();
    }
  }
}

// 클라이언트는 Turkey인지 모른 채 Duck으로 사용
const turkey: Turkey = new WildTurkey();
const duck: Duck = new TurkeyAdapter(turkey);
duck.quack(); // 골골
```

<details>
<summary>Java 원본</summary>

```java
public class TurkeyAdapter implements Duck {
    Turkey turkey;
    public TurkeyAdapter(Turkey turkey) {
        this.turkey = turkey;
    }
    public void quack() {
        turkey.gobble();
    }
    public void fly() {
        for (int i = 0; i < 5; i++) {
            turkey.fly();
        }
    }
}
```
</details>

> **패턴 정의 — 어댑터 패턴 (Adapter Pattern)**<br>특정 클래스 인터페이스를 클라이언트가 요구하는 다른 인터페이스로 변환한다. 인터페이스가 호환되지 않아 함께 쓸 수 없던 클래스를 사용할 수 있게 해 준다.

```
 Client ──request()──▶ Adapter ──specificRequest()──▶ Adaptee
        (타깃 인터페이스)   (타깃 구현 +               (변환 대상)
                          어댑티 보유)
```

동작: ①클라이언트가 타깃 메서드로 어댑터에 요청 → ②어댑터가 어댑티 메서드 호출로 변환 → ③클라이언트는 어댑터의 존재를 모른다.

### 객체 어댑터 vs 클래스 어댑터

- **객체 어댑터**(위 코드): **구성**으로 어댑티를 보유. 어댑티의 서브클래스에도 쓸 수 있어 유연하다.
- **클래스 어댑터**: 타깃과 어댑티를 **다중 상속**. 자바/TS는 다중 상속이 없어 못 쓴다.

> **핵심 통찰**: 어댑터는 **객체 구성**을 쓰므로, 어댑티 전체와 그 서브클래스에 두루 적용된다. "상속보다 구성(원칙 3)"의 좋은 예다.

### 실전 — Enumeration ↔ Iterator

자바 구형 컬렉션의 `Enumeration`(`hasMoreElements`/`nextElement`)을 신형 `Iterator`(`hasNext`/`next`/`remove`)로 변환.

```java
public class EnumerationIterator implements Iterator<Object> {
    Enumeration<?> enumeration;
    public EnumerationIterator(Enumeration<?> enumeration) {
        this.enumeration = enumeration;
    }
    public boolean hasNext() { return enumeration.hasMoreElements(); }
    public Object next() { return enumeration.nextElement(); }
    public void remove() {
        throw new UnsupportedOperationException(); // Enumeration엔 없는 기능
    }
}
```

> **핵심 통찰**: 메서드가 **일대일로 대응되지 않을 때**(`Iterator.remove()`)는 완벽한 변환이 불가능하다. `UnsupportedOperationException`을 던지는 것이 차선책이며, 이 제약은 문서로 명시해야 한다.

---

## 2. 퍼사드 패턴 — 인터페이스 단순화

홈시어터로 영화 한 편 보려면 팝콘 기계·조명·스크린·프로젝터·앰프·플레이어 등 **6개 클래스에 걸쳐 13단계**를 호출해야 한다. 끔찍하다. **퍼사드(facade, 겉모양)** 로 이 복잡함을 단순한 메서드 뒤에 감춘다.

```typescript
/** 홈시어터 서브시스템을 단순한 인터페이스로 감싸는 퍼사드. */
class HomeTheaterFacade {
  constructor(
    private amp: Amplifier,
    private player: StreamingPlayer,
    private projector: Projector,
    private screen: Screen,
    private lights: TheaterLights,
    private popper: PopcornPopper,
  ) {}

  /** 영화 볼 준비 — 복잡한 13단계를 하나로. */
  watchMovie(movie: string): void {
    this.popper.on();
    this.popper.pop();
    this.lights.dim(10);
    this.screen.down();
    this.projector.on();
    this.projector.wideScreenMode();
    this.amp.on();
    this.amp.setStreamingPlayer(this.player);
    this.amp.setSurroundSound();
    this.amp.setVolume(5);
    this.player.on();
    this.player.play(movie);
  }

  /** 영화 종료 — 모든 구성 요소를 역순으로 끈다. */
  endMovie(): void {
    this.popper.off();
    this.lights.on();
    this.screen.up();
    this.projector.off();
    this.amp.off();
    this.player.stop();
    this.player.off();
  }
}

// 클라이언트는 이제 두 메서드만 알면 된다
homeTheater.watchMovie("인디아나 존스: 레이더스");
homeTheater.endMovie();
```

<details>
<summary>Java 원본 (watchMovie)</summary>

```java
public void watchMovie(String movie) {
    popper.on();
    popper.pop();
    lights.dim(10);
    screen.down();
    projector.on();
    projector.wideScreenMode();
    amp.on();
    amp.setStreamingPlayer(player);
    amp.setSurroundSound();
    amp.setVolume(5);
    player.on();
    player.play(movie);
}
```
</details>

> **패턴 정의 — 퍼사드 패턴 (Facade Pattern)**<br>서브시스템에 있는 일련의 인터페이스를 통합 인터페이스로 묶어 준다. 고수준 인터페이스도 정의하므로 서브시스템을 더 편리하게 사용할 수 있다.

> **무엇이든 물어보세요 (Q&A)**
>
> **Q. 퍼사드가 서브시스템을 캡슐화(은닉)하나요?**
> A. 아니다. 퍼사드는 **간단한 인터페이스를 추가**할 뿐, 서브시스템 클래스를 숨기지 않는다. 고급 기능이 필요하면 클라이언트는 여전히 서브시스템에 **직접 접근**할 수 있다.
>
> **Q. 퍼사드는 새 기능을 추가하나요?**
> A. 새 행동을 구현하진 않지만, "팝콘을 튀기기 전에 기계를 켠다" 같은 **순서·조합 로직(스마트함)** 은 담는다.

---

## 3. 데코레이터 vs 어댑터 vs 퍼사드

셋 다 객체를 감싸지만 **목적**이 다르다.

| 패턴 | 목적 | 인터페이스 |
|------|------|-----------|
| **데코레이터**(3장) | 책임(기능)을 **추가** | **유지** |
| **어댑터**(이 장) | 인터페이스를 **변환** | **바꿈** |
| **퍼사드**(이 장) | 인터페이스를 **단순화/통합** | **간단하게 바꿈** |

> **핵심 통찰**: 어댑터와 퍼사드의 차이는 "감싸는 클래스 개수"가 아니다(둘 다 여러 개 감쌀 수 있다). 차이는 **용도** — 어댑터는 **호환되게 변환**, 퍼사드는 **쓰기 쉽게 단순화**.

---

## 4. 최소 지식 원칙 (디자인 원칙 7)

퍼사드는 새 원칙을 실현한다.

> **디자인 원칙 7 — 최소 지식 원칙 (Principle of Least Knowledge)**<br>진짜 절친에게만 이야기해야 한다. (= 데메테르의 법칙, Law of Demeter)

객체가 상호작용하는 클래스 수와 방식을 줄여, 한 부분의 변경이 여러 곳으로 번지는 것을 막는다.

### 나쁜 예 — 메서드 체이닝(기차 충돌)

```typescript
// ❌ 다른 메서드가 리턴한 객체의 메서드를 또 호출 → 낯선 객체와 친해짐
getTemp(): number {
  return this.station.getThermometer().getTemperature();
}

// ✅ Station이 대신 요청하도록 위임 메서드를 둔다
getTemp(): number {
  return this.station.getTemperature();
}
```

### 메서드를 호출해도 되는 "친구" 4가지

메서드 안에서, 다음 객체의 메서드만 호출한다.

1. **객체 자신**(`this`)
2. **매개변수로 전달된** 객체
3. 메서드 안에서 **직접 생성한** 객체
4. 객체의 **구성 요소**(인스턴스 변수가 참조하는 "A에는 B가 있다" 객체)

```typescript
class Car {
  private engine: Engine;

  start(key: Key): void {
    const doors = new Doors();       // ③ 직접 생성한 객체
    const authorized = key.turns();  // ② 매개변수 객체
    if (authorized) {
      this.engine.start();           // ④ 구성 요소
      this.updateDashboardDisplay(); // ① 자기 자신
      doors.lock();                  // ③ 직접 생성한 객체
    }
  }

  updateDashboardDisplay(): void { /* ... */ }
}
```

> **무엇이든 물어보세요 (Q&A)**
>
> **Q. 최소 지식 원칙의 단점은?**
> A. 원칙을 지키려고 **위임 메서드(래퍼)** 를 많이 만들면 시스템이 복잡해지고 개발 시간·성능에 부담이 될 수 있다. 모든 원칙처럼 상황을 보고 적용한다. (자바의 `System.out.println()`도 엄밀히는 이 원칙 위반이다.)

퍼사드는 클라이언트의 "친구"를 **퍼사드 하나로** 줄여 이 원칙을 실현한다.

---

## 연습 문제 (해답 예시)

**1. `DuckAdapter` (Duck → Turkey)** — `Turkey`를 구현하고 `Duck`을 보유한다. `gobble()`은 `duck.quack()`을 호출. `fly()`는 오리가 더 오래 날므로, `Random`으로 **5번에 1번꼴**로만 `duck.fly()`를 호출해 균형을 맞춘다.

**2. 최소 지식 원칙 위반 판별** — `station.getThermometer().getTemperature()`는 **위반**(리턴 객체의 메서드 호출). 반면 `getThermometer()`로 받은 객체를 **매개변수로 넘겨** `getTempHelper(thermometer)`에서 호출하면 (매개변수 규칙에 따라) 형식상 위반이 아니다 — 다만 "교묘하게 속인" 느낌이라 근본 개선은 아니다.

**3. `IteratorEnumeration` (Iterator → Enumeration)** — `Enumeration`을 구현하고 `Iterator`를 보유. `hasMoreElements()`→`iterator.hasNext()`, `nextElement()`→`iterator.next()`.

**4. 패턴-용도 연결** — 데코레이터=인터페이스 유지 + 책임 추가 / 어댑터=인터페이스 변환 / 퍼사드=인터페이스 단순화.

---

## 디자인 원칙 정리 (누적)

1. 바뀌는 부분을 캡슐화한다.
2. 구현보다는 인터페이스에 맞춰 프로그래밍한다.
3. 상속보다는 구성을 활용한다.
4. 느슨한 결합을 사용한다.
5. 확장에는 열려 있고 변경에는 닫혀 있어야 한다 (OCP).
6. 추상화에 의존하고 구상 클래스에 의존하지 않는다 (DIP).
7. **진짜 절친에게만 이야기한다 (최소 지식 원칙).** ← 이번 장

---

## 요약

- **어댑터 패턴**: 호환되지 않는 인터페이스를 클라이언트가 원하는 인터페이스로 **변환**한다. 객체 구성으로 어댑티를 감싼다.
- **퍼사드 패턴**: 복잡한 서브시스템을 **단순한 통합 인터페이스**로 감싸, 클라이언트를 서브시스템과 분리한다. 서브시스템에 직접 접근하는 길은 열려 있다.
- 데코레이터(기능 추가)·어댑터(변환)·퍼사드(단순화)는 목적이 다르다.
- **최소 지식 원칙**: 낯선 객체와 친해지지 말고, 위임을 통해 상호작용 대상을 줄여 결합을 낮춘다.

---

## 다른 챕터와의 관계

- **3장 데코레이터**: 셋 다 "감싸기"지만 목적이 다르다(위 비교표).
- **9장 반복자**: 이 장의 `Enumeration`↔`Iterator` 어댑터는 반복자 패턴과 이어진다.
- **11장 프록시**: 프록시도 객체를 감싸지만, 목적은 **접근 제어**다(또 다른 감싸기 패턴).

---

## 보너스: 원서 복습 요소

### 🎙️ 방구석 토크 — 객체 어댑터 vs 클래스 어댑터

- **객체 어댑터**(구성): 어댑티와 그 서브클래스 모두에 적용 가능 → 유연.
- **클래스 어댑터**(다중 상속): 어댑티 객체 없이 어댑터 하나로 끝, 메서드 오버라이드 가능 → 효율적이지만 다중 상속 필요(자바/TS 불가).

### 🧠 뇌 단련 (Brain Power)

1. AC 어댑터에 서지 프로텍션·지시등 같은 기능을 더하려면? → **데코레이터**(어댑터를 감싸 기능 추가).
2. `station.getThermometer().getTemperature()`는 몇 개 클래스와 결합? → 3개(House, Station, Thermometer). 위임으로 줄인다.

### ❓ 누가 무엇을 할까요

데코레이터=책임 추가 / 어댑터=인터페이스 변환 / 퍼사드=인터페이스 단순화.

### 📝 낱말 퀴즈 (정답 단어 모음)

7장 용어들(정답은 영어): ADAPTER 관련 — CONVERTS(변환), TARGET(타깃), TWOWAY(다중 어댑터), WRAP(감싸는), WRAPPERS(래퍼), ACADAPTER(AC어댑터), TURKEY(칠면조), FLY(날기), DECORATOR(데코레이터), SIMPLEPASSTHROUGH(그냥 통과), FACADE(퍼사드), HOMETHEATER(홈시어터), POPCORN(팝콘), DECOUPLING(분리), ALLOWS(허용), LEASTKNOWLEDGE(최소 지식 원칙), PRINTLN(println), FALSE(거짓), RAIDERSOFTHELOSTARK(인디아나 존스: 레이더스).
