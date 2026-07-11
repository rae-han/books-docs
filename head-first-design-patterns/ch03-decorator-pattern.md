# Chapter 03: The Decorator Pattern (데코레이터 패턴)

## 핵심 질문

- 기존 클래스 코드를 **전혀 건드리지 않고** 객체에 새 기능(임무)을 추가하려면?
- "확장에는 열려 있고 변경에는 닫혀 있다"는 모순처럼 보이는 원칙(OCP)을 어떻게 동시에 만족하는가?
- 상속으로 기능을 조합하면 왜 "클래스 폭발"이 일어나고, 데코레이터는 이를 어떻게 피하는가?
- 왜 데코레이터는 상속을 쓰면서도 "상속 대신 구성"이라고 말하는가?

---

## 1. 스타버즈 커피 주문 시스템

`Beverage`(음료) 추상 클래스가 있고, `getDescription()`과 추상 메서드 `cost()`를 가진다. `HouseBlend`, `DarkRoast`, `Decaf`, `Espresso`가 이를 상속한다. 문제는 고객이 **우유·두유·모카·휘핑크림** 같은 첨가물을 조합해서 주문하고, 조합마다 가격이 달라진다는 것이다.

---

## 2. 첫 번째 나쁜 예 — 클래스 폭발

첨가물 조합마다 서브클래스를 만들면 이렇게 된다.

```
DarkRoastWithSteamedMilkAndMocha, HouseBlendWithSteamedMilkAndCaramel,
EspressoWithWhipAndMocha, DecafWithSoyAndMocha, ... (수십 개!)
```

> **핵심 통찰**: "커피 종류 × 첨가물 조합"의 수만큼 클래스가 폭발한다. 첨가물 가격이 바뀌거나 새 첨가물이 생기면 수많은 클래스를 고쳐야 한다. **관리 불가능하다.**

---

## 3. 두 번째 나쁜 예 — 슈퍼클래스에 boolean 필드

그럼 `Beverage`에 `milk`, `soy`, `mocha`, `whip` boolean 필드와 게터/세터를 두고, 슈퍼클래스 `cost()`가 첨가물 비용을 계산하면 어떨까?

```typescript
// ❌ 나쁜 예
abstract class Beverage {
  milk = false;
  soy = false;
  mocha = false;
  whip = false;
  // hasMilk()/setMilk() ... 게터·세터

  cost(): number {
    let condimentCost = 0;
    if (this.hasMilk()) { condimentCost += 0.10; }
    if (this.hasSoy()) { condimentCost += 0.15; }
    if (this.hasMocha()) { condimentCost += 0.20; }
    if (this.hasWhip()) { condimentCost += 0.10; }
    return condimentCost;
  }
}
```

클래스는 5개로 줄었지만 문제가 산적한다.

- 첨가물 **가격이 바뀌면** 기존 코드를 수정해야 한다.
- **새 첨가물**이 생기면 새 메서드를 추가하고 슈퍼클래스 `cost()`도 고쳐야 한다.
- 특정 첨가물이 맞지 않는 음료(예: 아이스티에 `hasWhip()`)도 모든 메서드를 상속한다.
- **더블 모카** 같은 중복 첨가는 표현하기 어렵다.

---

## 4. OCP (디자인 원칙 5)

> 스승: 코드는 밤의 연꽃처럼 **변경에는 닫혀 있고**, 아침의 연꽃처럼 **확장에는 활짝 열려 있어야** 합니다.

> **디자인 원칙 5 — OCP (Open-Closed Principle)**<br>클래스는 확장에는 열려 있어야 하지만, 변경에는 닫혀 있어야 한다.

> **무엇이든 물어보세요 (Q&A)**
>
> **Q. 확장에는 열고 변경에는 닫는다? 모순 아닌가요?**
> A. 처음엔 모순처럼 보인다. 하지만 코드를 **변경하지 않고도** 확장하게 해 주는 객체지향 기법이 많다. 2장 옵저버 패턴을 떠올려 보라 — 옵저버를 새로 추가해도 주제 코드는 안 바뀐다. 핵심은 "새 행동은 **새 코드**로 추가하고, 기존 코드는 건드리지 않는다"는 것이다.
>
> **Q. 모든 곳에 OCP를 적용해야 하나요?**
> A. 아니다. OCP를 지키려면 추상화가 늘어 코드가 복잡해진다. **가장 바뀔 가능성이 높은 부분**에 집중해서 적용하는 것이 현명하다. 무분별한 OCP 적용은 시간 낭비이자 과도한 복잡성을 낳는다.

---

## 5. 데코레이터 패턴 — 객체를 래퍼로 감싸기

발상을 바꾼다. **특정 음료에서 시작해 첨가물로 장식(decorate)** 하는 것이다. "모카·휘핑크림을 추가한 다크 로스트"는 이렇게 만든다.

1. `DarkRoast` 객체를 만든다.
2. `Mocha` 객체로 감싼다(장식).
3. `Whip` 객체로 감싼다.
4. 가장 바깥의 `cost()`를 호출한다 → 첨가물 비용 계산은 **감싸고 있는 객체에 위임**된다.

```
   cost()          cost()          cost()
 ┌────────┐      ┌────────┐      ┌──────────┐
 │  Whip  │─────▶│ Mocha  │─────▶│ DarkRoast│
 └────────┘      └────────┘      └──────────┘
  +0.10 후         +0.20 후          0.99 반환
  최종 반환         반환
```

`cost()` 호출은 바깥에서 안으로 위임되고, 각 데코레이터가 자기 값을 더해 반환한다: `0.99 → (모카)1.19 → (휘핑)1.29`.

핵심 성질:
- 데코레이터의 슈퍼클래스(타입)는 **자신이 감싸는 객체의 슈퍼클래스와 같다.**
- 한 객체를 **여러 데코레이터로** 감쌀 수 있다.
- 데코레이터는 감싼 객체와 같은 타입이므로, **원래 객체 자리에 데코레이터를 넣어도 된다**(다형성).
- 객체는 **실행 중에** 언제든 감쌀 수 있다.

---

## 6. 데코레이터 패턴의 정의

> **패턴 정의 — 데코레이터 패턴 (Decorator Pattern)**<br>객체에 추가 요소를 동적으로 더할 수 있게 한다. 데코레이터를 사용하면 서브클래스를 만드는 것보다 훨씬 유연하게 기능을 확장할 수 있다.

```
                Component
              ┌──────────────┐
              │ methodA()    │◀──────────────┐ (Decorator가 Component를 감싼다)
              │ methodB()    │               │
              └──────────────┘               │
                    △                        │
        ┌───────────┴──────────┐             │
  ConcreteComponent          Decorator ──────┘
    methodA()          ┌──────────────────┐
    methodB()          │ wrappedObj: Component │
                       └──────────────────┘
                              △
                   ┌──────────┴──────────┐
            ConcreteDecoratorA    ConcreteDecoratorB
              methodA()             methodA()
              newBehavior()         newBehavior()
```

> 사무실 옆자리에서 — 메리와 수의 대화<br><br>**메리**: `CondimentDecorator`가 `Beverage`를 상속하잖아. 데코레이터는 "상속 대신 구성"이라며?<br>**수**: 여기서 상속은 **행동을 물려받으려는 게 아니라 "형식(타입)을 맞추려는" 것**이야. 데코레이터가 감싼 객체와 같은 타입이어야, 원래 객체 자리에 들어갈 수 있으니까. **행동은 감싼 객체를 구성(인스턴스 변수로 보유)해서 실행 중에 얻어.** 상속으로 얻는 게 아니고.

> **핵심 통찰**: 데코레이터가 `Beverage`를 상속하는 이유는 **타입을 맞추기 위해서**다. 실제 기능 확장은 **구성**(감싼 객체 참조)으로 이루어진다. 그래서 "상속 대신 구성"이라는 원칙과 어긋나지 않는다.

---

## 7. 구현

### 추상 구성 요소와 추상 데코레이터

```typescript
/** 음료 — 데코레이터 패턴의 추상 구성 요소(Component). */
abstract class Beverage {
  /** 음료 설명. 서브클래스에서 설정한다. */
  protected description = "제목 없음";

  /** 음료 설명을 반환한다. */
  getDescription(): string {
    return this.description;
  }

  /** 음료(+첨가물) 가격을 반환한다. */
  abstract cost(): number;
}

/** 첨가물 데코레이터의 공통 추상 클래스(Decorator). */
abstract class CondimentDecorator extends Beverage {
  /** 감싸고 있는 음료. 어떤 음료든 감쌀 수 있도록 상위 타입으로 보유한다. */
  protected beverage!: Beverage;

  // 모든 첨가물이 설명을 새로 구성하도록 강제한다
  abstract getDescription(): string;
}
```

> **핵심 통찰**: `beverage` 필드를 **구상 타입이 아니라 상위 타입 `Beverage`로** 선언한 것이 핵심이다. 그래야 데코레이터가 "어떤 음료든, 그리고 다른 데코레이터로 감싸인 음료든" 감쌀 수 있다.

<details>
<summary>Java 원본</summary>

```java
public abstract class Beverage {
    String description = "제목 없음";

    public String getDescription() {
        return description;
    }

    public abstract double cost();
}

public abstract class CondimentDecorator extends Beverage {
    Beverage beverage;
    public abstract String getDescription();
}
```
</details>

### 구상 음료

```typescript
class Espresso extends Beverage {
  constructor() {
    super();
    this.description = "에스프레소";
  }
  cost(): number {
    return 1.99;
  }
}

class HouseBlend extends Beverage {
  constructor() {
    super();
    this.description = "하우스 블렌드 커피";
  }
  cost(): number {
    return 0.89;
  }
}

class DarkRoast extends Beverage {
  constructor() {
    super();
    this.description = "다크 로스트 커피";
  }
  cost(): number {
    return 0.99;
  }
}
```

### 구상 데코레이터 (첨가물)

```typescript
class Mocha extends CondimentDecorator {
  constructor(beverage: Beverage) {
    super();
    this.beverage = beverage;
  }
  getDescription(): string {
    return `${this.beverage.getDescription()}, 모카`;
  }
  cost(): number {
    // 감싼 음료에 위임 후 모카 값을 더한다
    return this.beverage.cost() + 0.20;
  }
}

class Soy extends CondimentDecorator {
  constructor(beverage: Beverage) {
    super();
    this.beverage = beverage;
  }
  getDescription(): string {
    return `${this.beverage.getDescription()}, 두유`;
  }
  cost(): number {
    return this.beverage.cost() + 0.15;
  }
}

class Whip extends CondimentDecorator {
  constructor(beverage: Beverage) {
    super();
    this.beverage = beverage;
  }
  getDescription(): string {
    return `${this.beverage.getDescription()}, 휘핑크림`;
  }
  cost(): number {
    return this.beverage.cost() + 0.10;
  }
}
```

<details>
<summary>Java 원본 (Mocha)</summary>

```java
public class Mocha extends CondimentDecorator {
    public Mocha(Beverage beverage) {
        this.beverage = beverage;
    }
    public String getDescription() {
        return beverage.getDescription() + ", 모카";
    }
    public double cost() {
        return beverage.cost() + 0.20; // 위임 후 모카 값 추가
    }
}
```
</details>

---

## 8. 테스트

```typescript
// 아무것도 안 넣은 에스프레소
let beverage: Beverage = new Espresso();
console.log(`${beverage.getDescription()} $${beverage.cost()}`);
// 에스프레소 $1.99

// 다크 로스트 + 모카 2번 + 휘핑크림
let beverage2: Beverage = new DarkRoast();
beverage2 = new Mocha(beverage2);
beverage2 = new Mocha(beverage2);
beverage2 = new Whip(beverage2);
console.log(`${beverage2.getDescription()} $${beverage2.cost()}`);
// 다크 로스트 커피, 모카, 모카, 휘핑크림 $1.49

// 하우스 블렌드 + 두유 + 모카 + 휘핑크림
let beverage3: Beverage = new HouseBlend();
beverage3 = new Soy(beverage3);
beverage3 = new Mocha(beverage3);
beverage3 = new Whip(beverage3);
console.log(`${beverage3.getDescription()} $${beverage3.cost()}`);
// 하우스 블렌드 커피, 두유, 모카, 휘핑크림 $1.34
```

`new Whip(new Mocha(new Mocha(new DarkRoast())))`처럼 **양파 껍질을 겹겹이 두르듯** 감싼다.

> **무엇이든 물어보세요 (Q&A)**
>
> **Q. 데코레이터로 감싸고 나면 그게 하우스 블렌드인지 다크 로스트인지 알 수 없잖아요?**
> A. 맞다. **구상 구성 요소의 타입에 의존하는 코드**(예: "다크 로스트만 할인")에 데코레이터를 적용하면 제대로 동작하지 않는다. 데코레이터는 **추상 타입에 의존하는 코드**에서만 온전히 동작한다.
>
> **Q. 데코레이터를 조립하는 코드가 복잡해지지 않나요?**
> A. 그렇다. 그래서 실전에서는 **팩토리(4장)나 빌더(14장) 패턴**으로 데코레이터 조립을 캡슐화한다.

---

## 9. 실전 — 자바 I/O는 데코레이터 패턴이다

`java.io`의 수많은 스트림 클래스가 데코레이터 패턴으로 설계되어 있다.

- `InputStream` — 추상 구성 요소
- `FileInputStream`, `ByteArrayInputStream` 등 — 구상 구성 요소(바이트를 읽음)
- `FilterInputStream` — 추상 데코레이터
- `BufferedInputStream`(버퍼링 추가), `ZipInputStream`(압축 해제 추가) 등 — 구상 데코레이터

```java
// 파일 스트림을 버퍼링 데코레이터로 감싼다
InputStream in = new BufferedInputStream(new FileInputStream("test.txt"));
```

직접 데코레이터를 만들 수도 있다. 입력 스트림의 대문자를 소문자로 바꾸는 데코레이터:

```java
public class LowerCaseInputStream extends FilterInputStream {
    public LowerCaseInputStream(InputStream in) {
        super(in);
    }
    public int read() throws IOException {
        int c = in.read();
        return (c == -1 ? c : Character.toLowerCase((char) c));
    }
}

// 사용: 세 겹으로 감싼다
InputStream in = new LowerCaseInputStream(
                   new BufferedInputStream(
                     new FileInputStream("test.txt")));
```

> TypeScript/Node.js에서도 동일한 발상이 스트림 파이프라인에 쓰인다: `fs.createReadStream(path).pipe(gunzip).pipe(lowerCaseTransform)` — 각 변환이 이전 스트림을 감싸는 데코레이터다.

> 패턴 집중 인터뷰 — 데코레이터 패턴의 고백<br><br>"저는 디자인을 유연하게 만드는 재주가 뛰어나지만, **자잘한 클래스가 엄청나게 늘어나** 남들이 이해하기 힘든 디자인이 되곤 해요(자바 I/O를 보세요). 또 **특정 구상 타입에 의존하는 코드**에 저를 잘못 적용하면 모든 게 엉망이 되고, **조립 코드가 복잡해지는** 단점도 있죠. 그래도 OCP를 지키며 유연한 디자인을 만든다는 건 변함없는 장점이에요."

---

## 연습 문제 (해답 예시)

**1. 첫 나쁜 예에서 위반한 원칙** — (1) *바뀌는 부분을 캡슐화하라*(첨가물이라는 변화가 캡슐화되지 않음), (2) *상속보다 구성*(모든 조합을 상속으로 표현). 힌트가 말한 "2가지 중요한 원칙"이 이것이다.

**2. `cost()`·`getDescription()` 구현** — §7 참고. 구상 음료는 자기 값만 반환하고, 데코레이터는 `beverage.cost() + 첨가물값`으로 **위임 후 가산**한다. 설명도 `beverage.getDescription() + ", 첨가물"`로 이어 붙인다.

**3. 사이즈(톨·그란데·벤티) 추가** — `Beverage`에 `Size` enum과 `getSize()`/`setSize()`를 추가하고, `CondimentDecorator`가 `getSize()`를 **감싼 음료에 위임**하도록 오버라이드한다. 그러면 사이즈가 가장 안쪽 구상 음료까지 전파되어, 각 데코레이터가 사이즈별 첨가물 가격을 계산할 수 있다.

```typescript
enum Size { TALL, GRANDE, VENTI }

abstract class Beverage {
  protected size: Size = Size.TALL;
  setSize(size: Size): void { this.size = size; }
  getSize(): Size { return this.size; }
  // ...
}

// CondimentDecorator: 감싼 음료에 사이즈를 위임
abstract class CondimentDecorator extends Beverage {
  protected beverage!: Beverage;
  getSize(): Size {
    return this.beverage.getSize();
  }
}
```

---

## 디자인 원칙 정리 (누적)

1. 바뀌는 부분을 찾아내 캡슐화하고, 바뀌지 않는 부분과 분리한다.
2. 구현보다는 인터페이스(상위 형식)에 맞춰 프로그래밍한다.
3. 상속보다는 구성을 활용한다.
4. 상호작용하는 객체 사이에서는 가능하면 느슨한 결합을 사용한다.
5. **클래스는 확장에는 열려 있고 변경에는 닫혀 있어야 한다 (OCP).** ← 이번 장

---

## 요약

- 상속으로 기능을 조합하면 **클래스 폭발** 또는 **부적합한 기능 상속** 문제가 생긴다.
- **데코레이터 패턴**은 객체를 같은 타입의 데코레이터로 **감싸(wrap)**, 실행 중에 기능을 동적으로 추가한다.
- 데코레이터는 상속을 **타입(형식)을 맞추는 용도**로만 쓰고, 실제 기능은 **구성(감싼 객체 참조)** 으로 얻는다.
- 데코레이터는 감싼 객체에 작업을 **위임**한 뒤, 그 결과에 자기 몫을 더해(또는 앞뒤로 작업을 얹어) 반환한다.
- 이 패턴은 **OCP**를 만족한다 — 기존 코드를 고치지 않고 새 데코레이터를 추가해 기능을 확장한다.
- 단점: 자잘한 클래스가 많아지고, 조립 코드가 복잡해지며, 구상 타입 의존 코드에는 부적합하다. `java.io`가 대표적 실전 예다.

---

## 다른 챕터와의 관계

- **1·2장의 원칙 위에**: "인터페이스에 맞춰 프로그래밍 + 상속보다 구성"이 데코레이터의 토대다.
- **4장 팩토리 · 14장 빌더**: 데코레이터 조립의 복잡함을 이 패턴들로 캡슐화한다(본문에서 예고).
- **7장 어댑터/퍼사드**: 어댑터는 인터페이스를 **바꾸고**, 데코레이터는 인터페이스를 **유지한 채 책임을 더한다**(비교 포인트).
- **11장 프록시**: 프록시도 객체를 감싸지만, 목적은 **접근 제어**이지 기능 추가가 아니다.

---

## 보너스: 원서 복습 요소

### 🧠 뇌 단련 (Brain Power)

1. 첫 나쁜 예(클래스 폭발)에서 우유 가격이 오르거나 캐러멜이 추가되면? → 수많은 클래스를 고쳐야 한다. 어떤 디자인 원칙 2가지를 어긴 것인가? (→ 바뀌는 부분 캡슐화, 상속보다 구성)
2. 커피와 각 첨가물의 `cost()`·`getDescription()`을 어떻게 구현할지 스스로 그려 보라. (→ 위임 후 가산)

### 🎤 패턴 집중 인터뷰 — 데코레이터의 단점 정리

- 자잘한 클래스가 폭증해 이해하기 어렵다(자바 I/O).
- 구상 타입에 의존하는 클라이언트 코드에 잘못 적용하면 깨진다.
- 구성 요소 초기화(조립) 코드가 복잡해진다 → 팩토리/빌더로 보완.

### 📝 핵심 정리 (Bullet Points)

- 유연성 면에서 상속 확장은 좋은 선택이 아니며, 기존 코드 수정 없이 행동을 확장해야 할 때가 있다.
- 구성과 위임으로 실행 중에 새 행동을 추가할 수 있다.
- 데코레이터는 구상 구성 요소를 감싸며, 감싼 클래스와 **같은 타입**을 가진다.
- 데코레이터는 감싼 구성 요소의 메서드 호출 결과에 기능을 더해 행동을 확장한다.
- 감싸는 데코레이터 개수에는 제한이 없고, 클라이언트는 (구상 타입에 의존하지 않는 한) 데코레이터의 존재를 모른다.
- 남용하면 자잘한 객체가 너무 많아져 코드가 복잡해진다.
