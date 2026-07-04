# Chapter 28: The Visitor Pattern (비지터 패턴 패밀리)

## 핵심 질문

이미 안정적으로 동작하는 클래스 계층 구조에 **새로운 메소드/연산을 추가**해야 한다. 그런데 계층 구조를 건드리면 OCP가 깨지고, 기존 코드를 재컴파일·재배포해야 한다. 어떻게 하면 **계층 구조를 수정하지 않고** 새 기능을 추가할 수 있을까? 그리고 이 문제를 해결하는 네 가지 패턴(Visitor, Acyclic Visitor, Decorator, Extension Object)은 각각 언제 써야 하는가?

> 어떤 늦은 방문객이 문 밖에서 들어오기를 청하고 있어. 그것뿐 아무것도 아니야.<br>— 에드거 앨런 포(Edgar Allen Poe), 「갈가마귀(The Raven)」 중

---

## 1. 문제: 계층 구조에 메소드 추가의 고통

`Modem` 객체들의 계층 구조가 있다고 하자. 기반 인터페이스에는 `dial`, `send`, `hangup`, `recv` 같은 모든 모뎀 공통 메소드가 들어 있고, 파생형으로는 `HayesModem`, `ZoomModem`, `ErnieModem`이 있다.

```
        «interface»
         Modem
        ─────────
        + dial()
        + send()
        + hangup()
        + recv()
            ▲
   ┌────────┼─────────┐
   │        │         │
 Hayes    Zoom     Ernie
```

이제 `configureForUnix`라는 새 메소드를 추가하라는 요구가 들어왔다. 환경 설정 방법이 모뎀마다 다르므로, 이 메소드는 파생형마다 다른 일을 해야 한다.

문제는 **운영체제마다 메소드를 추가해야 한다는 점**이다. 윈도우는? 맥OS는? 리눅스는? `Modem` 인터페이스를 변경에 닫지 못하게 되어, 새로운 OS가 등장할 때마다 인터페이스를 수정하고 모든 모뎀 소프트웨어를 재배포해야 한다.

> **핵심 통찰**: 계층 구조의 **변경 축**은 단 하나여야 한다. `Modem`은 "어떤 모뎀이 있는가"라는 축만 변경되어야 하지, "어느 OS용 환경 설정이 추가되는가" 같은 다른 축으로 변경되면 안 된다. 다른 축의 변경은 **다른 곳**에서 처리해야 한다.

이 문제를 해결하기 위해 GoF 디자인 패턴은 **비지터 집합(Visitor Family)**이라는 네 가지 패턴을 제공한다.

| 패턴 | 핵심 메커니즘 | 주된 장점 |
|------|--------------|----------|
| Visitor | 이중 디스패치(dual dispatch) | 빠르고 단순 |
| Acyclic Visitor | 마커 인터페이스 + 형변환 | 의존 관계 순환 제거, 점진적 컴파일 |
| Decorator | 위임(delegation) | 동적 책임 추가 |
| Extension Object | 객체별 확장 객체 맵 | 런타임 인터페이스 확장 |

---

## 2. 비지터 패턴 (Visitor)

### 2.1 구조와 이중 디스패치

비지터 패턴의 핵심은 **이중 디스패치(*dual dispatch - 다형성을 이용해 호출할 메소드 본체를 두 번 결정하는 기법*)**다.

```
   «interface»                «interface»
     Modem                    ModemVisitor
   ───────────                ─────────────
   + dial()                   + visit(Hayes)
   + accept(ModemVisitor)     + visit(Zoom)
        ▲                     + visit(Ernie)
        │                          ▲
   ┌────┼────┐                     │
   │    │    │                  UnixModem
  Hayes Zoom Ernie              Configurator

   public void accept(ModemVisitor v) {
       v.visit(this);  // ← 이중 디스패치
   }
```

이중 디스패치 과정은 두 단계로 이루어진다:

1. **첫 번째 디스패치**: `modem.accept(v)` — 어떤 종류의 `Modem`인지에 따라 해당 파생형의 `accept` 메소드가 호출된다.
2. **두 번째 디스패치**: 그 안에서 `v.visit(this)` — `this`의 정적 타입(예: `HayesModem`)에 따라 오버로드된 `visit(HayesModem)`이 호출된다.

이 두 번의 다형성 호출로 **(모뎀 종류) × (수행할 기능)**의 행렬에서 정확한 함수가 결정된다.

### 2.2 코드 예제

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public interface Modem {
    void dial(String pno);
    void hangup();
    void send(char c);
    char recv();
    void accept(ModemVisitor v);
}

public interface ModemVisitor {
    void visit(HayesModem modem);
    void visit(ZoomModem modem);
    void visit(ErnieModem modem);
}

public class HayesModem implements Modem {
    String configurationString = null;
    public void dial(String pno) {}
    public void hangup() {}
    public void send(char c) {}
    public char recv() { return 0; }
    public void accept(ModemVisitor v) {
        v.visit(this);
    }
}

public class UnixModemConfigurator implements ModemVisitor {
    public void visit(HayesModem m) {
        m.configurationString = "&s1=4&D=3";
    }
    public void visit(ZoomModem m) {
        m.configurationValue = 42;
    }
    public void visit(ErnieModem m) {
        m.internalPattern = "C is too slow";
    }
}
```

</details>

```typescript
// TypeScript
interface Modem {
  dial(pno: string): void;
  hangup(): void;
  send(c: string): void;
  recv(): string;
  accept(v: ModemVisitor): void;
}

interface ModemVisitor {
  visitHayes(m: HayesModem): void;
  visitZoom(m: ZoomModem): void;
  visitErnie(m: ErnieModem): void;
}

class HayesModem implements Modem {
  configurationString: string | null = null;
  dial(pno: string): void {}
  hangup(): void {}
  send(c: string): void {}
  recv(): string {
    return "";
  }
  accept(v: ModemVisitor): void {
    v.visitHayes(this);
  }
}

class ZoomModem implements Modem {
  configurationValue: number = 0;
  dial(pno: string): void {}
  hangup(): void {}
  send(c: string): void {}
  recv(): string {
    return "";
  }
  accept(v: ModemVisitor): void {
    v.visitZoom(this);
  }
}

class ErnieModem implements Modem {
  internalPattern: string | null = null;
  dial(pno: string): void {}
  hangup(): void {}
  send(c: string): void {}
  recv(): string {
    return "";
  }
  accept(v: ModemVisitor): void {
    v.visitErnie(this);
  }
}

class UnixModemConfigurator implements ModemVisitor {
  visitHayes(m: HayesModem): void {
    m.configurationString = "&s1=4&D=3";
  }
  visitZoom(m: ZoomModem): void {
    m.configurationValue = 42;
  }
  visitErnie(m: ErnieModem): void {
    m.internalPattern = "C is too slow";
  }
}
```

> TypeScript는 메소드 오버로드 시 시그니처만 다르고 본체는 하나여야 하므로, Java의 `visit(HayesModem)`/`visit(ZoomModem)` 오버로드를 `visitHayes`/`visitZoom`처럼 이름을 달리하여 표현한다.

### 2.3 사용 예

```typescript
const v = new UnixModemConfigurator();
const h = new HayesModem();
h.accept(v);
// h.configurationString === "&s1=4&D=3"
```

프로그래머는 `UnixModemConfigurator`의 인스턴스를 만든 다음 `Modem`의 `accept`에 전달하기만 하면 된다. 그러면 `Modem` 파생형이 자신의 `accept` 안에서 `v.visit(this)`를 호출해, 적절한 `visit` 메소드가 실행된다.

> **핵심 통찰**: 비지터는 행렬과 같다. 한 축은 방문 대상 타입(모뎀 종류), 다른 축은 수행할 기능(OS별 환경 설정)이다. 각 셀에는 "특정 OS에서 특정 모뎀을 초기화하는 방법"을 설명하는 함수가 들어간다. **새로운 OS가 추가되면 새 비지터를 작성**하기만 하면 되고, `Modem` 계층은 손대지 않는다.

---

## 3. 비순환 비지터 패턴 (Acyclic Visitor)

### 3.1 비지터의 의존 관계 순환 문제

비지터 패턴 구조를 자세히 보면, `Modem` 기반 클래스가 `ModemVisitor`에 의존하고, `ModemVisitor`는 모든 `Modem` 파생형(`HayesModem`, `ZoomModem`, `ErnieModem`)에 의존한다. 결국 **모든 `Modem` 파생형이 의존 관계 순환에 빠진다**.

```
   Modem ─────► ModemVisitor
     ▲                │
     │                ▼
   Hayes ◀──────────── (visit(Hayes))
```

이 순환 때문에:
- 새로운 `Modem` 파생형을 추가하면 `ModemVisitor`를 변경해야 하고,
- 그러면 모든 비지터 파생형이 재컴파일된다.
- C++에서는 더 나쁘다 — 새로운 파생형이 추가될 때마다 변경 대상 계층 전체를 재컴파일·재배포해야 한다.

> **핵심 통찰**: 비지터는 **방문 대상 계층이 안정적**이고 새 파생형이 자주 추가되지 않을 때 적합하다. `Hayes`, `Zoom`, `Ernie`가 모든 모뎀 파생형일 가능성이 높다면 비지터로 충분하다. 반대로 파생형이 자주 추가되는 변동성 큰 계층이라면 비순환 비지터가 답이다.

### 3.2 비순환 비지터의 구조

비순환 비지터(*Acyclic Visitor - 의존 관계 순환을 깬 비지터 변종*)는 `ModemVisitor`를 **퇴화 클래스(degenerate class - 메소드가 전혀 없는 마커 인터페이스)**로 만든다. 그리고 파생형마다 별도의 비지터 인터페이스(`HayesVisitor`, `ZoomVisitor`, `ErnieVisitor`)를 둔다.

```
   «interface»          «marker, degenerate»
     Modem ─────────►       ModemVisitor
       ▲
       │                    ┌──────────────┐
   ┌───┼───┐                ▼              ▼
   │   │   │           «interface»    «interface»
  Hayes Z. Ernie       HayesVisitor   ZoomVisitor
                       + visit(Hayes) + visit(Zoom)
                            ▲              ▲
                            └──────┬───────┘
                              UnixModemConfigurator
```

`accept` 함수에서는 비지터를 자신에 해당하는 인터페이스로 **형변환(downcast)**한다. 형변환이 성공하면 `visit`을 호출하고, 실패하면 무시한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public interface ModemVisitor {} // 마커 인터페이스 (메소드 없음)

public interface HayesVisitor extends ModemVisitor {
    void visit(HayesModem m);
}

public interface ZoomVisitor extends ModemVisitor {
    void visit(ZoomModem m);
}

public class HayesModem implements Modem {
    String configurationString = null;
    public void accept(ModemVisitor v) {
        try {
            HayesVisitor hv = (HayesVisitor) v;
            hv.visit(this);
        } catch (ClassCastException e) {
            // 이 비지터는 Hayes에 관심 없음
        }
    }
    // ...
}
```

</details>

```typescript
// TypeScript
interface ModemVisitor {} // 마커 인터페이스

interface HayesVisitor extends ModemVisitor {
  visit(m: HayesModem): void;
}

interface ZoomVisitor extends ModemVisitor {
  visit(m: ZoomModem): void;
}

// 타입 가드로 다운캐스트를 안전하게
function isHayesVisitor(v: ModemVisitor): v is HayesVisitor {
  return typeof (v as HayesVisitor).visit === "function";
}

class HayesModem implements Modem {
  configurationString: string | null = null;
  dial(pno: string): void {}
  hangup(): void {}
  send(c: string): void {}
  recv(): string {
    return "";
  }
  accept(v: ModemVisitor): void {
    if (isHayesVisitor(v)) {
      v.visit(this);
    }
  }
}
```

### 3.3 트레이드오프

비순환 비지터는 다음과 같은 장단을 가진다:

| 측면 | 평가 |
|------|------|
| 의존 관계 순환 | 제거됨 |
| 점진적 컴파일 | 가능 |
| 새 파생형 추가 | 쉬움 (다른 모듈 영향 없음) |
| 복잡도 | 비지터보다 훨씬 복잡 |
| 형변환 비용 | 시간 예측 어려움 (RTTI 의존) |
| 경성 실시간 시스템(*hard real-time system - 결과가 절대적으로 정해진 시간 내에 출력되어야 하는 시스템*) | 부적합 |

> **핵심 통찰**: 비지터가 빽빽한 행렬(dense matrix)이라면, 비순환 비지터는 **희소 행렬(sparse matrix)**이다. 모든 파생형 × 기능 조합을 구현할 필요가 없다. 예를 들어 `Ernie` 모뎀을 유닉스용으로 환경 설정할 수 없다면 `UnixModemConfigurator`는 `ErnieVisitor`를 구현하지 않으면 된다.

---

## 4. 보고서 생성 — 비지터의 대표적 사용처

비지터의 가장 흔한 용도는 **자료 구조를 순회하며 보고서를 생성**하는 일이다. 자료 구조와 보고서 생성 코드를 분리할 수 있기 때문이다.

자재 명세서(BOM: bill-of-material) 구조를 보자. `Part` 인터페이스 아래에 `Assembly`(조립품)와 `PiecePart`(부품)가 있다.

```
   «interface»               «interface»
     Part ◄──────────────── PartVisitor
   ──────────              ──────────────
   + getPartNumber()        + visit(Assembly)
   + getDescription()       + visit(PiecePart)
   + accept(PartVisitor)         ▲
        ▲                        │
   ┌────┴────┐            ┌──────┴───────┐
   │         │            │              │
 Assembly  PiecePart  ExplodedCost   PartCount
  (1..*)    + cost     Visitor       Visitor
```

`Part`에 `getExplodedCost`나 `getPieceCount`를 추가할 수도 있다. 하지만 그러면 **새로운 보고서가 필요할 때마다 `Part` 계층을 바꿔야** 한다. SRP 위반이다.

> **Uncle Bob의 경험**: 새로운 종류의 부품이 필요한 경우라면 `Part` 계층 구조가 바뀌어도 된다. 하지만 새로운 종류의 **보고서**가 필요하다는 이유 때문에 `Part` 계층 구조가 바뀌어선 안 된다. 보고서를 `Part` 계층에서 분리하면 좋다 — 이것이 비지터 구조가 보여주는 방법이다.

### 4.1 코드 예제

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public interface Part {
    String getPartNumber();
    String getDescription();
    void accept(PartVisitor v);
}

public class Assembly implements Part {
    private List itsParts = new LinkedList();
    // ...
    public void accept(PartVisitor v) {
        v.visit(this);
        Iterator i = getParts();
        while (i.hasNext()) {
            Part p = (Part) i.next();
            p.accept(v);  // 트리 순회
        }
    }
    public void add(Part part) {
        itsParts.add(part);
    }
}

public class PiecePart implements Part {
    private double itsCost;
    // ...
    public void accept(PartVisitor v) {
        v.visit(this);
    }
    public double getCost() { return itsCost; }
}

public interface PartVisitor {
    void visit(PiecePart pp);
    void visit(Assembly a);
}

public class ExplodedCostVisitor implements PartVisitor {
    private double cost = 0;
    public double cost() { return cost; }
    public void visit(PiecePart p) { cost += p.getCost(); }
    public void visit(Assembly a) {}
}
```

</details>

```typescript
// TypeScript
interface Part {
  getPartNumber(): string;
  getDescription(): string;
  accept(v: PartVisitor): void;
}

interface PartVisitor {
  visitPiecePart(pp: PiecePart): void;
  visitAssembly(a: Assembly): void;
}

class Assembly implements Part {
  private itsParts: Part[] = [];

  constructor(
    private partNumber: string,
    private description: string,
  ) {}

  getPartNumber(): string {
    return this.partNumber;
  }
  getDescription(): string {
    return this.description;
  }

  add(part: Part): void {
    this.itsParts.push(part);
  }

  accept(v: PartVisitor): void {
    v.visitAssembly(this);
    for (const p of this.itsParts) {
      p.accept(v); // 재귀적으로 자식 노드 순회
    }
  }
}

class PiecePart implements Part {
  constructor(
    private partNumber: string,
    private description: string,
    private cost: number,
  ) {}

  getPartNumber(): string {
    return this.partNumber;
  }
  getDescription(): string {
    return this.description;
  }
  getCost(): number {
    return this.cost;
  }

  accept(v: PartVisitor): void {
    v.visitPiecePart(this);
  }
}

class ExplodedCostVisitor implements PartVisitor {
  private cost = 0;

  getCost(): number {
    return this.cost;
  }

  visitPiecePart(p: PiecePart): void {
    this.cost += p.getCost();
  }

  visitAssembly(a: Assembly): void {
    // 합계만 모은다
  }
}

class PartCountVisitor implements PartVisitor {
  private pieceCount = 0;
  private pieceMap = new Map<string, number>();

  visitPiecePart(p: PiecePart): void {
    this.pieceCount++;
    const pn = p.getPartNumber();
    this.pieceMap.set(pn, (this.pieceMap.get(pn) ?? 0) + 1);
  }

  visitAssembly(a: Assembly): void {}

  getPieceCount(): number {
    return this.pieceCount;
  }
  getPartNumberCount(): number {
    return this.pieceMap.size;
  }
}
```

### 4.2 사용 예

```typescript
const cellphone = new Assembly("CP-7734", "Cell Phone");
const display = new PiecePart("DS-1428", "LCD Display", 14.37);
const speaker = new PiecePart("SP-92", "Speaker", 3.5);
cellphone.add(display);
cellphone.add(speaker);

const costVisitor = new ExplodedCostVisitor();
cellphone.accept(costVisitor);
console.log(costVisitor.getCost()); // 17.87

const countVisitor = new PartCountVisitor();
cellphone.accept(countVisitor);
console.log(countVisitor.getPieceCount()); // 2
```

> **핵심 통찰**: 비지터를 사용하면 방문 대상인 자료 구조 자체와 그 자료 구조가 사용되는 용도가 **독립적**이게 된다. 자료 구조를 재컴파일하거나 재배치하지 않고도 새로운 비지터를 만들어 배치하거나 기존 비지터를 변경한 다음 재배치할 수 있다 — 이것이 비지터의 힘이다.

### 4.3 비지터의 다른 용도

자료 구조를 여러 가지 방법으로 해석할 필요가 있는 애플리케이션이라면 언제나 비지터 패턴을 사용할 수 있다:

- **컴파일러**: 중간 단계 AST 자료 구조를 다양한 프로세서/최적화 계획에 맞춰 컴파일하기 위한 비지터
- **상호참조 생성**: AST를 소스코드 cross-reference나 UML 다이어그램으로 변환하는 비지터
- **환경 설정**: 서브시스템마다 자신만의 비지터를 사용해 환경 설정 데이터를 방문하면서 스스로를 초기화

---

## 5. 데코레이터 패턴 (Decorator)

### 5.1 동기 — 동적 책임 추가

비지터가 새로운 **메소드**를 추가하는 패턴이라면, 데코레이터는 새로운 **책임**을 객체에 추가한다.

다시 `Modem` 계층 구조를 보자. 어떤 사용자는 모뎀이 다이얼하는 소리를 듣고 싶어 하고, 어떤 사용자는 듣고 싶어 하지 않는다.

```typescript
// ❌ 나쁜 방법 1: 호출하는 곳마다 분기
const m = user.getModem();
if (user.wantsLoudDial()) {
  m.setVolume(11);
}
m.dial("...");
```

이 코드 조각이 애플리케이션 코드 몇 백 군데에 중복되는 광경을 상상해보자. 끔찍하다.

```java
// ❌ 나쁜 방법 2: Modem 안에 플래그
public class HayesModem implements Modem {
    private boolean wantsLoudDial = false;
    public void dial(...) {
        if (wantsLoudDial) {
            setVolume(11);
        }
        // ...
    }
}
```

이전보다는 낫지만, `Modem`의 **모든 파생형마다 코드가 중복**된다. 게다가 왜 `Modem`이 사용자의 일시적인 기분에 영향받아야 하는가? CCP와 SRP를 위반한다.

### 5.2 데코레이터의 구조

데코레이터는 `LoudDialModem`이라는 완전히 새로운 클래스를 만든다. 이 클래스는 `Modem`을 구현하면서, 내부적으로는 다른 `Modem` 인스턴스에게 **위임**한다.

```
   «interface»
     Modem ◄────────────────────┐
   ──────────                    │
   + dial()                      │  «delegates»
   + setVolume()              itsModem
        ▲                        │
   ┌────┼────────┬──────────────┐│
   │    │        │              │
  Hayes Zoom   Ernie       LoudDialModem
                            (decorator)
                            dial() {
                              itsModem.setVolume(11);
                              itsModem.dial(...);
                            }
```

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class LoudDialModem implements Modem {
    private Modem itsModem;

    public LoudDialModem(Modem m) {
        itsModem = m;
    }
    public void dial(String pno) {
        itsModem.setSpeakerVolume(10);
        itsModem.dial(pno);
    }
    public void setSpeakerVolume(int volume) {
        itsModem.setSpeakerVolume(volume);
    }
    public String getPhoneNumber() {
        return itsModem.getPhoneNumber();
    }
    public int getSpeakerVolume() {
        return itsModem.getSpeakerVolume();
    }
}
```

</details>

```typescript
// TypeScript
class LoudDialModem implements Modem {
  constructor(private itsModem: Modem) {}

  dial(pno: string): void {
    this.itsModem.setSpeakerVolume(10);
    this.itsModem.dial(pno);
  }

  setSpeakerVolume(volume: number): void {
    this.itsModem.setSpeakerVolume(volume);
  }

  getPhoneNumber(): string {
    return this.itsModem.getPhoneNumber();
  }

  getSpeakerVolume(): number {
    return this.itsModem.getSpeakerVolume();
  }

  // Modem 인터페이스의 다른 메소드도 모두 위임
  hangup(): void {
    this.itsModem.hangup();
  }
  send(c: string): void {
    this.itsModem.send(c);
  }
  recv(): string {
    return this.itsModem.recv();
  }
}
```

이제 다이얼할 때 큰 소리를 낼 것인지에 대한 결정은 **단 한 장소**에서 일어난다. 사용자가 큰 소리가 필요하면 `LoudDialModem`을 생성하고 사용자의 모뎀을 여기에 전달하면 된다.

```typescript
const userModem: Modem = new HayesModem();
const m: Modem = user.wantsLoudDial()
  ? new LoudDialModem(userModem)
  : userModem;
m.dial("5551212"); // 사용자 환경에 따라 자동 처리
```

### 5.3 다중 데코레이터

동일한 계층에 데코레이터가 둘 이상 있는 경우, 위임 코드의 중복을 피하기 위해 `ModemDecorator`라는 공통 추상 데코레이터를 만들 수 있다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class ModemDecorator implements Modem {
    private Modem itsModem;

    public ModemDecorator(Modem m) {
        itsModem = m;
    }
    public void dial(String pno) {
        itsModem.dial(pno);
    }
    public void setSpeakerVolume(int volume) {
        itsModem.setSpeakerVolume(volume);
    }
    public String getPhoneNumber() {
        return itsModem.getPhoneNumber();
    }
    public int getSpeakerVolume() {
        return itsModem.getSpeakerVolume();
    }
    protected Modem getModem() {
        return itsModem;
    }
}

public class LoudDialModem extends ModemDecorator {
    public LoudDialModem(Modem m) {
        super(m);
    }
    @Override
    public void dial(String pno) {
        getModem().setSpeakerVolume(10);
        getModem().dial(pno);
    }
}
```

</details>

```typescript
// TypeScript
class ModemDecorator implements Modem {
  constructor(protected itsModem: Modem) {}

  dial(pno: string): void {
    this.itsModem.dial(pno);
  }
  setSpeakerVolume(volume: number): void {
    this.itsModem.setSpeakerVolume(volume);
  }
  getPhoneNumber(): string {
    return this.itsModem.getPhoneNumber();
  }
  getSpeakerVolume(): number {
    return this.itsModem.getSpeakerVolume();
  }
  hangup(): void {
    this.itsModem.hangup();
  }
  send(c: string): void {
    this.itsModem.send(c);
  }
  recv(): string {
    return this.itsModem.recv();
  }
}

class LoudDialModem extends ModemDecorator {
  constructor(m: Modem) {
    super(m);
  }
  dial(pno: string): void {
    this.itsModem.setSpeakerVolume(10);
    this.itsModem.dial(pno);
  }
}

class LogoutExitModem extends ModemDecorator {
  constructor(m: Modem) {
    super(m);
  }
  hangup(): void {
    this.itsModem.send("e");
    this.itsModem.send("x");
    this.itsModem.send("i");
    this.itsModem.send("t");
    this.itsModem.hangup();
  }
}
```

데코레이터는 **여러 개를 합성**할 수 있다는 점이 강력하다:

```typescript
const m: Modem = new LogoutExitModem(new LoudDialModem(new HayesModem()));
// 다이얼 시 시끄럽게, hangup 시 exit 전송
```

> **핵심 통찰**: 데코레이터는 CCP와 SRP를 함께 만족시킨다. "다이얼 소리 크기" 같은 책임은 `Modem` 본연의 책임이 아니다. 변경 이유가 다른 코드는 분리되어야 하고, 데코레이터는 그 분리를 **객체 합성**으로 우아하게 실현한다.

---

## 6. 확장 객체 패턴 (Extension Object)

### 6.1 동기

계층 구조를 변경하지 않고도 기능을 추가하는 또 다른 방법이 **확장 객체(Extension Object)** 패턴이다. 다른 방법보다 복잡하지만, 훨씬 더 강력하고 유연하다.

핵심 아이디어:
- 계층 구조에 들어 있는 객체마다 **특별한 확장 객체의 맵**을 유지한다.
- 확장 객체를 **이름으로 찾을 수 있도록** 메소드를 제공한다.
- 확장 객체는 원래 객체를 조작할 수 있는 메소드를 제공한다.

자재 명세서 시스템에서 `Part`마다 자신의 XML 표현을 만들 수 있게 하고, 또 CSV 표현도 만들 수 있게 하려면 어떻게 할까?

- `Part`에 `toXML`을 추가? SRP 위반.
- 비지터 사용? 모든 BOM 클래스의 XML 생성 코드가 동일한 비지터 객체에 들어가야 함 — BOM 종류마다 XML 생성 클래스를 따로 두고 싶다면 부적합.

확장 객체는 **객체 종류마다 자신의 확장 클래스를 가지면서도** 계층 구조에 영향을 주지 않는 방법을 제공한다.

### 6.2 구조

```
              Part (abstract)
             ───────────────
             + getExtension(String)
             + addExtension(String, PartExtension)
             - HashMap<String, PartExtension>
                    ▲
             ┌──────┴───────┐
          Assembly      PiecePart

   «marker»
   PartExtension ◄── BadPartExtension
        ▲
        ├── «interface» XMLPartExtension
        │       + getXMLElement()
        │           ▲
        │           ├── XMLAssemblyExtension
        │           └── XMLPiecePartExtension
        │
        └── «interface» CSVPartExtension
                + getCSV()
                    ▲
                    ├── CSVAssemblyExtension
                    └── CSVPiecePartExtension
```

각 `Part`는 `getExtension("XML")`이나 `getExtension("CSV")`로 자신의 확장 객체를 가져온다.

### 6.3 코드 예제

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public abstract class Part {
    HashMap itsExtensions = new HashMap();
    public abstract String getPartNumber();
    public abstract String getDescription();

    public void addExtension(String type, PartExtension extension) {
        itsExtensions.put(type, extension);
    }
    public PartExtension getExtension(String type) {
        PartExtension pe = (PartExtension) itsExtensions.get(type);
        if (pe == null) pe = new BadPartExtension();
        return pe;
    }
}

public interface PartExtension {} // 마커
public class BadPartExtension implements PartExtension {}

public interface XMLPartExtension extends PartExtension {
    Element getXMLElement();
}

public class PiecePart extends Part {
    public PiecePart(String pn, String desc, double cost) {
        // ...
        addExtension("CSV", new CSVPiecePartExtension(this));
        addExtension("XML", new XMLPiecePartExtension(this));
    }
}

public class XMLPiecePartExtension implements XMLPartExtension {
    private PiecePart itsPiecePart;
    public XMLPiecePartExtension(PiecePart part) {
        itsPiecePart = part;
    }
    public Element getXMLElement() {
        Element e = new Element("PiecePart");
        e.addContent(new Element("PartNumber").setText(itsPiecePart.getPartNumber()));
        // ...
        return e;
    }
}
```

</details>

```typescript
// TypeScript
interface PartExtension {} // 마커 인터페이스
class BadPartExtension implements PartExtension {}

interface XMLPartExtension extends PartExtension {
  getXMLElement(): XMLElement;
}

interface CSVPartExtension extends PartExtension {
  getCSV(): string;
}

abstract class Part {
  private itsExtensions = new Map<string, PartExtension>();

  abstract getPartNumber(): string;
  abstract getDescription(): string;

  addExtension(type: string, extension: PartExtension): void {
    this.itsExtensions.set(type, extension);
  }

  getExtension(type: string): PartExtension {
    return this.itsExtensions.get(type) ?? new BadPartExtension();
  }
}

class PiecePart extends Part {
  constructor(
    private partNumber: string,
    private description: string,
    private cost: number,
  ) {
    super();
    this.addExtension("CSV", new CSVPiecePartExtension(this));
    this.addExtension("XML", new XMLPiecePartExtension(this));
  }

  getPartNumber(): string {
    return this.partNumber;
  }
  getDescription(): string {
    return this.description;
  }
  getCost(): number {
    return this.cost;
  }
}

class XMLPiecePartExtension implements XMLPartExtension {
  constructor(private itsPiecePart: PiecePart) {}

  getXMLElement(): XMLElement {
    const e = new XMLElement("PiecePart");
    e.addChild(new XMLElement("PartNumber").setText(this.itsPiecePart.getPartNumber()));
    e.addChild(new XMLElement("Description").setText(this.itsPiecePart.getDescription()));
    e.addChild(new XMLElement("Cost").setText(String(this.itsPiecePart.getCost())));
    return e;
  }
}

class CSVPiecePartExtension implements CSVPartExtension {
  constructor(private itsPiecePart: PiecePart) {}

  getCSV(): string {
    return [
      "PiecePart",
      this.itsPiecePart.getPartNumber(),
      this.itsPiecePart.getDescription(),
      this.itsPiecePart.getCost(),
    ].join(",");
  }
}
```

### 6.4 사용 예

```typescript
const p1 = new PiecePart("997624", "MyPart", 3.2);

// 타입 가드로 안전하게 다운캐스트
const xe = p1.getExtension("XML") as XMLPartExtension;
const xml = xe.getXMLElement();
// xml.getName() === "PiecePart"

const ce = p1.getExtension("CSV") as CSVPartExtension;
console.log(ce.getCSV()); // "PiecePart,997624,MyPart,3.2"

// 존재하지 않는 확장
const bad = p1.getExtension("Foo");
console.log(bad instanceof BadPartExtension); // true
```

> **Uncle Bob의 경험**: 나는 이 코드를 백지상태에서 작성하지 않았다. 테스트 케이스를 통해 진화시켰다. 모든 테스트 케이스는 그 케이스를 통과할 코드를 작성하기 전에 먼저 작성되었고, 코드는 절대로 이미 존재하는 테스트 케이스를 통과하기 위해 필요한 정도 이상으로 복잡하게 작성되지 않았다. 그리고 나는 내가 확장 객체 패턴을 만들려고 한다는 사실을 알고 있었으므로, 코드를 진화시킬 때 이 사실을 지침으로 삼았다.

### 6.5 트레이드오프

- **유연성**: 시스템 상태에 따라 특정 확장 객체를 런타임에 추가/삭제할 수 있다.
- **남용 위험**: 이 유연성은 남용되기 쉽다. 대개의 경우 이 정도까지 필요하지는 않다.
- **잔존 의존**: BOM 객체의 생성자에서 확장 객체를 만들어 추가하므로, BOM 객체가 아직 XML/CSV 클래스에 어느 정도 의존한다. 이 의존마저 깨야 한다면 팩토리(*Factory - 객체 생성 책임을 별도로 분리한 패턴*)를 도입할 수 있다.

---

## 7. 네 패턴 비교

| 패턴 | 추가하는 것 | 메커니즘 | 트레이드오프 |
|------|-----------|---------|-------------|
| Visitor | 새 메소드(연산) | 이중 디스패치 | 단순·빠름. 단, 방문 대상 계층 변경 시 모든 비지터 수정 필요 |
| Acyclic Visitor | 새 메소드(연산) | 마커 인터페이스 + 다운캐스트 | 의존 순환 제거, 점진적 컴파일 가능. 복잡, 실시간 시스템 부적합 |
| Decorator | 새 책임(행위) | 위임 + 합성 | 런타임 합성 가능. 인터페이스가 큰 경우 위임 코드 많음 |
| Extension Object | 새 인터페이스 | 확장 객체 맵 + 다운캐스트 | 객체별로 별도 확장 가능, 런타임 동적 추가. 가장 복잡 |

### 7.1 언제 어느 것을 쓸까

- **Visitor** — 방문 대상 계층이 안정적이고 새 연산만 추가될 때
- **Acyclic Visitor** — 방문 대상 계층이 자주 변하거나 점진적 컴파일·배포가 중요할 때
- **Decorator** — 객체에 동적으로 책임을 덧붙이고 싶을 때 (특히 SRP에 따라 본 책임과 분리할 때)
- **Extension Object** — 객체마다 종류별 확장 코드를 따로 두고, 런타임에 인터페이스를 확장하고 싶을 때

---

## 8. 객체지향 원칙과의 연결

비지터 패턴 집합은 다음 원칙들을 직접적으로 지원한다:

| 원칙 | 적용 방식 |
|------|---------|
| OCP (개방-폐쇄) | 기존 계층 구조를 수정하지 않고도 새 행위를 추가 |
| SRP (단일 책임) | 자료 구조 본연의 책임과 그 위에서 동작하는 다양한 연산을 분리 |
| CCP (공통 폐쇄) | 변경 이유가 같은 코드는 같은 비지터/데코레이터에 모이고, 다른 코드는 분리 |
| LSP (리스코프 치환) | 비지터/데코레이터 파생형이 기반 인터페이스를 완전히 대체 가능 |
| DIP (의존 역전) | 방문 대상도 비지터도 모두 추상에 의존 |

---

## 요약

- 비지터 패턴 집합은 **클래스 계층 구조를 수정하지 않고** 행위를 변경하기 위한 네 가지 방법을 제공한다.
- **Visitor**는 이중 디스패치로 (객체 종류) × (연산) 행렬을 구현한다. 빠르고 단순하지만 방문 대상 계층이 변하면 모든 비지터를 손봐야 한다.
- **Acyclic Visitor**는 마커 인터페이스와 다운캐스트로 의존 관계 순환을 깨고 희소 행렬을 만든다. 복잡도와 실시간 부적합이 단점.
- **Decorator**는 위임과 합성으로 객체에 새 책임을 동적으로 추가한다. SRP에 따른 책임 분리를 우아하게 실현하고 여러 데코레이터를 자유롭게 합성할 수 있다.
- **Extension Object**는 객체마다 확장 객체 맵을 두어, 객체 종류별로 별도의 확장 클래스를 두면서도 런타임 인터페이스 확장을 가능하게 한다. 가장 강력하지만 가장 복잡하다.
- 네 패턴 모두 **OCP·SRP·CCP·LSP·DIP**를 자연스럽게 만족시킨다.
- 비지터 패턴들은 유혹적이라 남용하기 쉽다. **도움이 된다면 사용하되, 필요성에 대해 합리적인 회의주의적 태도를 유지**해야 한다. 비지터로도 해결할 수 있지만 더 간단하게 해결할 수 있는 경우가 많다.
