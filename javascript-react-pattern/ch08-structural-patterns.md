# Chapter 08: Structural Patterns (구조 패턴)

## 핵심 질문

> 객체와 클래스를 조합하여 더 큰 구조를 만드는 구조 패턴은 무엇이며, TypeScript/현대 자바스크립트(ES2022+)에서 각 패턴은 어떻게 구현하고 언제 사용해야 하는가?

---

## 구조 패턴에 대하여

구조 패턴(*Structural Pattern*)은 클래스와 객체의 **구성**을 다룬다. 상속의 개념을 통해 인터페이스와 객체를 구성하여 새로운 기능을 추가할 수 있는 것처럼, 구조 패턴은 클래스와 객체를 체계적으로 구성하는 최고의 방법과 사례를 제공한다.

생성 패턴이 "객체를 **어떻게 만들 것인가**"에 집중했다면, 구조 패턴은 "만들어진 객체들을 **어떻게 조합할 것인가**"에 집중한다.

이 장에서 다루는 구조 패턴:

| 패턴 | 의도 |
|------|------|
| **퍼사드** (*Facade*) | 복잡한 하위 시스템에 단순한 인터페이스 제공 |
| **믹스인** (*Mixin*) | 여러 클래스의 기능을 하나로 조합 |
| **데코레이터** (*Decorator*) | 서브클래싱 없이 객체에 동적으로 기능 추가 |
| **플라이웨이트** (*Flyweight*) | 많은 객체 간 데이터를 공유하여 메모리 최적화 |
| **어댑터** (*Adapter*) | 호환되지 않는 인터페이스를 연결 |
| **프록시** (*Proxy*) | 다른 객체에 대한 접근을 제어하는 대리 객체 |
| **컴포지트** (*Composite*) | 객체를 트리 구조로 구성하여 단일/복합 객체를 동일하게 취급 |

> **Osmani의 조언**: 구조 패턴은 클래스의 인터페이스를 단순화하고 코드의 구현 부분과 사용 부분을 분리한다. 이를 통해 하위 시스템에 직접 접근하기보단 간접적으로 상호 작용하여 에러를 줄일 수 있다.

---

## 1. 퍼사드 패턴 (Facade Pattern)

퍼사드(*Facade — "겉모습"이라는 뜻으로, 복잡한 내부를 숨기고 단순한 외부 인터페이스를 제공*)란 실제 모습을 숨기고 꾸며낸 겉모습만을 세상에 드러내는 것을 뜻한다. 퍼사드 패턴은 심층적인 복잡성을 숨기고, 사용하기 편리한 높은 수준의 인터페이스를 제공하는 패턴이다.

### 패턴 카드: Facade

| 항목 | 설명 |
|------|------|
| **의도** | 복잡한 하위 시스템에 단순하고 통합된 인터페이스를 제공한다 |
| **사용 시점** | 복잡한 라이브러리/API의 일부 기능만 사용하거나, 여러 하위 시스템을 조율해야 할 때 |
| **미사용 시점** | 하위 시스템의 세밀한 제어가 필요하거나, 추상화 레이어가 오히려 방해될 때 |
| **장점** | 사용 용이성, 결합도 감소, 코드 가독성 향상 |
| **단점** | 과도한 추상화로 유연성 감소, 퍼사드 자체가 "신 객체"(*God Object*)가 될 위험 |

### 1.1 기본 퍼사드 — jQuery의 사례

퍼사드는 jQuery 같은 자바스크립트 라이브러리에서 흔히 볼 수 있는 구조 패턴이다. `$(el).css()`나 `$(el).animate()` 같은 메서드를 사용할 때마다 퍼사드를 사용하는 것이다. jQuery 코어의 많은 내부 메서드를 직접 찾아 실행하는 대신 쉽게 공개된 인터페이스를 사용한다.

```typescript
// 퍼사드 없이 — 브라우저마다 다른 이벤트 API를 직접 다뤄야 함
function addEventLegacy(
  el: HTMLElement,
  ev: string,
  fn: EventListener,
): void {
  if (el.addEventListener) {
    el.addEventListener(ev, fn, false);
  } else if ((el as any).attachEvent) {
    (el as any).attachEvent(`on${ev}`, fn);
  } else {
    (el as any)[`on${ev}`] = fn;
  }
}

// 퍼사드 적용 — 단일 인터페이스로 통합
class EventFacade {
  static on(el: HTMLElement, event: string, handler: EventListener): void {
    el.addEventListener(event, handler, false);
  }

  static off(el: HTMLElement, event: string, handler: EventListener): void {
    el.removeEventListener(event, handler, false);
  }

  static once(el: HTMLElement, event: string, handler: EventListener): void {
    el.addEventListener(event, handler, { once: true });
  }
}

// 사용자는 내부 구현을 몰라도 됨
const button = document.querySelector("button")!;
EventFacade.on(button, "click", () => console.log("clicked"));
```

### 1.2 모듈 + 퍼사드 조합

퍼사드 패턴을 단독으로 사용해야만 하는 것은 아니다. 모듈 패턴 같은 다른 패턴과도 어울릴 수 있다. 여러 비공개 메서드를 가진 모듈에 대해 퍼사드가 간단한 API를 제공한다:

```typescript
// analyticsInternal.ts — 비공개 모듈
const queue: Array<{ event: string; data: Record<string, unknown> }> = [];
let isInitialized = false;

function initialize(): void {
  // 복잡한 SDK 초기화 로직
  isInitialized = true;
}

function flush(): void {
  if (!isInitialized) initialize();
  // 큐에 쌓인 이벤트를 서버로 전송
  queue.length = 0;
}

function enqueue(event: string, data: Record<string, unknown>): void {
  queue.push({ event, data });
  if (queue.length >= 10) flush();
}

// analyticsFacade.ts — 퍼사드
export const analytics = {
  trackPageView(page: string): void {
    enqueue("page_view", { page, timestamp: Date.now() });
  },

  trackClick(elementId: string): void {
    enqueue("click", { elementId, timestamp: Date.now() });
  },

  trackPurchase(amount: number, currency: string): void {
    enqueue("purchase", { amount, currency, timestamp: Date.now() });
  },
} as const;
```

```typescript
// 사용 — 내부 큐잉, 초기화, 플러시 로직을 전혀 몰라도 됨
import { analytics } from "./analyticsFacade";

analytics.trackPageView("/home");
analytics.trackClick("buy-button");
analytics.trackPurchase(29.99, "USD");
```

### 1.3 TypeScript로 강화된 퍼사드

TypeScript에서는 퍼사드의 공개 인터페이스를 타입으로 명시하여 하위 시스템 변경에 따른 영향을 컴파일 타임에 감지할 수 있다:

```typescript
// 복잡한 하위 시스템들
class AudioEngine {
  loadTrack(url: string): AudioBuffer { /* ... */ return {} as AudioBuffer; }
  setVolume(level: number): void { /* ... */ }
  play(buffer: AudioBuffer): void { /* ... */ }
  stop(): void { /* ... */ }
  crossFade(from: AudioBuffer, to: AudioBuffer, duration: number): void { /* ... */ }
}

class PlaylistManager {
  #tracks: string[] = [];
  #currentIndex = 0;

  add(url: string): void { this.#tracks.push(url); }
  next(): string | undefined { return this.#tracks[++this.#currentIndex]; }
  previous(): string | undefined { return this.#tracks[--this.#currentIndex]; }
  current(): string | undefined { return this.#tracks[this.#currentIndex]; }
}

class EqualizerEngine {
  setBass(level: number): void { /* ... */ }
  setTreble(level: number): void { /* ... */ }
  applyPreset(name: string): void { /* ... */ }
}

// 퍼사드 — 세 하위 시스템을 단일 인터페이스로
interface MusicPlayerFacade {
  play(url?: string): void;
  stop(): void;
  next(): void;
  previous(): void;
  setVolume(level: number): void;
  applyEqualizer(preset: string): void;
}

class MusicPlayer implements MusicPlayerFacade {
  #audio = new AudioEngine();
  #playlist = new PlaylistManager();
  #eq = new EqualizerEngine();
  #currentBuffer: AudioBuffer | null = null;

  play(url?: string): void {
    const track = url ?? this.#playlist.current();
    if (!track) return;
    if (url) this.#playlist.add(url);
    this.#currentBuffer = this.#audio.loadTrack(track);
    this.#audio.play(this.#currentBuffer);
  }

  stop(): void {
    this.#audio.stop();
  }

  next(): void {
    const track = this.#playlist.next();
    if (track) this.play(track);
  }

  previous(): void {
    const track = this.#playlist.previous();
    if (track) this.play(track);
  }

  setVolume(level: number): void {
    this.#audio.setVolume(Math.max(0, Math.min(100, level)));
  }

  applyEqualizer(preset: string): void {
    this.#eq.applyPreset(preset);
  }
}
```

> **핵심 통찰**: 퍼사드의 장점은 사용하기 쉽다는 점과 패턴 구현에 필요한 코드의 양이 적다는 점이다. TypeScript에서는 퍼사드 인터페이스를 명시적으로 정의하여 하위 시스템 변경 시 타입 에러로 빠르게 감지할 수 있다.

### JavaScript vs TypeScript

```javascript
// JavaScript — 퍼사드가 어떤 메서드를 노출하는지 코드를 읽어야 앎
class MusicPlayer {
  constructor() {
    this.audio = new AudioEngine();    // 내부 의존성이 public
    this.playlist = new PlaylistManager();
  }
  play(url) { /* ... */ }
  // audio, playlist에 직접 접근 가능 → 캡슐화 깨짐
}
```

```typescript
// TypeScript — 인터페이스 + #private으로 퍼사드 계약 강제
interface MusicPlayerFacade {
  play(url?: string): void;
  stop(): void;
}

class MusicPlayer implements MusicPlayerFacade {
  #audio = new AudioEngine();     // 런타임 비공개
  #playlist = new PlaylistManager();
  play(url?: string): void { /* ... */ }
  stop(): void { /* ... */ }
  // #audio, #playlist에 외부 접근 불가 → 캡슐화 보장
}
```

---

## 2. 믹스인 패턴 (Mixin Pattern)

C++나 Lisp 같은 전통적인 프로그래밍 언어에서 믹스인(*Mixin — 서브클래스가 쉽게 상속받아 기능을 재사용할 수 있도록 하는 클래스*)은 클래스의 기능을 확장하는 데 사용된다. 자바스크립트의 클래스는 부모 클래스를 하나만 가질 수 있지만, 여러 클래스의 기능을 **섞는 것**으로 문제를 해결할 수 있다.

### 패턴 카드: Mixin

| 항목 | 설명 |
|------|------|
| **의도** | 다중 상속 없이 여러 소스로부터 기능을 조합하여 클래스를 확장한다 |
| **사용 시점** | 여러 클래스에서 공통 기능을 공유해야 하지만 단일 상속 제한이 있을 때 |
| **미사용 시점** | 기능의 출처가 불명확해질 수 있는 대규모 시스템, 리액트 컴포넌트 (Hooks/HOC 사용 권장) |
| **장점** | 코드 재사용성 향상, 함수 중복 감소 |
| **단점** | 프로토타입 오염, 함수 출처 불확실, 이름 충돌 가능성 |

### 2.1 서브클래싱

ES2015+에서 도입된 `extends` 키워드를 통해 기존 부모 클래스를 확장할 수 있다. 부모 클래스를 확장하는 자식 클래스를 서브클래스(*Subclass*)라고 한다:

```typescript
class Person {
  constructor(
    public firstName: string,
    public lastName: string,
    public gender: string = "male",
  ) {}
}

class Superhero extends Person {
  constructor(
    firstName: string,
    lastName: string,
    public powers: string[],
  ) {
    super(firstName, lastName); // 부모 클래스의 생성자 호출 (생성자 체이닝)
  }
}

const superman = new Superhero("Clark", "Kent", ["flight", "heat-vision"]);
console.log(superman.powers); // ["flight", "heat-vision"]
console.log(superman.firstName); // "Clark" — Person에서 상속
```

### 2.2 믹스인 함수

자바스크립트에서 클래스 표현식은 평가될 때마다 새로운 클래스를 반환한다. `extends` 절은 클래스나 생성자를 반환하는 임의의 표현식을 허용할 수 있다. 이러한 특징을 통해 부모 클래스를 받아 새로운 서브클래스를 만들어 내는 믹스인 함수를 정의할 수 있다:

```typescript
// 믹스인 타입 정의
type Constructor<T = {}> = new (...args: any[]) => T;

// 이동 기능 믹스인
function Movable<TBase extends Constructor>(Base: TBase) {
  return class extends Base {
    moveUp(): void {
      console.log("move up");
    }
    moveDown(): void {
      console.log("move down");
    }
    stop(): void {
      console.log("stop! in the name of love!");
    }
  };
}

// 직렬화 기능 믹스인
function Serializable<TBase extends Constructor>(Base: TBase) {
  return class extends Base {
    serialize(): string {
      return JSON.stringify(this);
    }
  };
}

// 기본 클래스
class CarAnimator {
  moveLeft(): void {
    console.log("move left");
  }
}

// 믹스인 적용 — 여러 기능을 합성
class MyAnimator extends Movable(Serializable(CarAnimator)) {}

const myAnimator = new MyAnimator();
myAnimator.moveLeft();  // "move left"  — CarAnimator에서
myAnimator.moveDown();  // "move down"  — Movable에서
myAnimator.stop();      // "stop! in the name of love!" — Movable에서
console.log(myAnimator.serialize()); // JSON 직렬화 — Serializable에서
```

### 2.3 실전 예제 — 자동차 클래스 확장

```typescript
type Constructor<T = {}> = new (...args: any[]) => T;

// 운전 기능 믹스인
function Drivable<TBase extends Constructor>(Base: TBase) {
  return class extends Base {
    driveForward(): void {
      console.log("drive forward");
    }
    driveBackward(): void {
      console.log("drive backward");
    }
    driveSideways(): void {
      console.log("drive sideways");
    }
  };
}

interface CarOptions {
  model?: string;
  color?: string;
}

class Car {
  model: string;
  color: string;

  constructor({ model = "no model provided", color = "no color provided" }: CarOptions = {}) {
    this.model = model;
    this.color = color;
  }
}

class MyCar extends Drivable(Car) {}

const myCar = new MyCar({});
myCar.driveForward();   // "drive forward"
myCar.driveBackward();  // "drive backward"

const mySportsCar = new MyCar({ model: "Porsche", color: "red" });
mySportsCar.driveSideways(); // "drive sideways"
```

### 2.4 장점과 단점

믹스인은 함수의 중복을 줄이고 재사용성을 높인다. 그러나 몇몇 개발자들은 클래스나 객체의 프로토타입에 기능을 주입하는 것을 나쁜 방법이라고 여긴다. 프로토타입 오염과 함수의 출처에 대한 불확실성을 초래하기 때문이다.

**리액트에서의 믹스인**: 리액트에서도 ES6 클래스 도입 이전에는 컴포넌트에 기능을 추가하기 위해 믹스인을 사용하곤 했다. 그러나 리액트 개발팀은 컴포넌트의 유지보수와 재사용을 복잡하게 만든다는 이유로 믹스인을 반대했다. 그 대신 **고차 컴포넌트**(*HOC — Higher-Order Component*)나 **Hooks**의 사용을 장려했다.

### JavaScript vs TypeScript

```javascript
// JavaScript — 믹스인 반환 타입을 알 수 없음
const Movable = (Base) => class extends Base {
  moveUp() { console.log("up"); }
};
// new (Movable(Car))().moveUp(); → IDE가 moveUp()을 인식하지 못함
```

```typescript
// TypeScript — 제네릭 Constructor 타입으로 믹스인 체인 추론
type Constructor<T = {}> = new (...args: any[]) => T;

function Movable<TBase extends Constructor>(Base: TBase) {
  return class extends Base {
    moveUp(): void { console.log("up"); }
  };
}

const MovableCar = Movable(Car);
new MovableCar({}).moveUp();
//                  ^^^^^^ 자동완성 + 타입 체크 작동
```

TypeScript의 `Constructor<T>` 제네릭 타입을 사용하면 믹스인 체인에서도 모든 메서드의 타입 정보가 보존된다.

> **핵심 통찰**: 자바스크립트의 단일 상속 제한을 믹스인으로 우회할 수 있지만, 현대 개발에서는 함수 합성(*Composition*)이나 Hooks 패턴이 더 선호된다. 믹스인을 사용한다면 TypeScript의 `Constructor<T>` 타입으로 타입 안전성을 확보해야 한다.

---

## 3. 데코레이터 패턴 (Decorator Pattern)

데코레이터(*Decorator*) 패턴은 코드 재사용을 목표로 하는 구조 패턴이다. 기존 클래스에 **동적으로 기능을 추가**하기 위해 사용되며, 서브클래싱의 대안이라고 생각하면 된다. 데코레이터 자체는 클래스의 기본 기능에 필수적이지 않다 — 필수적이었다면 부모 클래스에 이미 구현되었을 것이다.

### 패턴 카드: Decorator

| 항목 | 설명 |
|------|------|
| **의도** | 서브클래싱 없이 객체에 동적으로 새로운 책임(기능)을 추가한다 |
| **사용 시점** | 기능 조합이 다양하여 서브클래스 폭발(*Class Explosion*)이 발생할 때 |
| **미사용 시점** | 기능 조합이 단순하여 상속으로 충분하거나, 런타임 동적 추가가 불필요한 경우 |
| **장점** | 유연한 기능 확장, Open-Closed 원칙 준수, 서브클래스 폭발 방지 |
| **단점** | 작고 비슷한 객체가 많아지면 구조 파악이 어려움, 디버깅 복잡도 증가 |

### 3.1 기본 데코레이터 — 객체에 직접 속성 추가

자바스크립트 클래스 인스턴스 객체에 새로운 속성이나 메서드를 추가하는 것은 간단하다:

```typescript
class Vehicle {
  vehicleType: string;
  model: string;
  license: string;

  constructor(vehicleType?: string) {
    this.vehicleType = vehicleType ?? "car";
    this.model = "default";
    this.license = "00000-000";
  }
}

const truck = new Vehicle("truck");

// 데코레이터: 인스턴스에 직접 기능 추가
(truck as any).setModel = function (modelName: string) {
  this.model = modelName;
};
(truck as any).setColor = function (color: string) {
  this.color = color;
};

(truck as any).setModel("CAT");
(truck as any).setColor("blue");
// truck: { vehicleType: "truck", model: "CAT", color: "blue", ... }

// 원본 Vehicle은 변경되지 않음
const car = new Vehicle("car");
// car: { vehicleType: "car", model: "default", license: "00000-000" }
```

이러한 단순 구현은 유용하지만 데코레이터의 이점을 모두 보여주기엔 부족하다.

### 3.2 MacBook 데코레이터 — 클래스 기반

맥북 구매 상황을 예로 들어보자. 추가 옵션(메모리, 각인, 보험)의 조합에 따라 서브클래스를 만들면 비실용적이다. 데코레이터 패턴으로 해결한다:

```typescript
// 컴포넌트 인터페이스
interface MacBookComponent {
  getCost(): number;
  getDescription(): string;
}

// 기본 컴포넌트
class MacBook implements MacBookComponent {
  getCost(): number {
    return 997;
  }

  getDescription(): string {
    return 'MacBook 11.6"';
  }
}

// 데코레이터 베이스 — 컴포넌트를 감싸고 같은 인터페이스를 구현
abstract class MacBookDecorator implements MacBookComponent {
  constructor(protected macBook: MacBookComponent) {}

  getCost(): number {
    return this.macBook.getCost();
  }

  getDescription(): string {
    return this.macBook.getDescription();
  }
}

// 구체 데코레이터 1: 메모리 업그레이드
class MemoryUpgrade extends MacBookDecorator {
  getCost(): number {
    return this.macBook.getCost() + 75;
  }

  getDescription(): string {
    return `${this.macBook.getDescription()}, Memory Upgrade`;
  }
}

// 구체 데코레이터 2: 각인
class Engraving extends MacBookDecorator {
  getCost(): number {
    return this.macBook.getCost() + 200;
  }

  getDescription(): string {
    return `${this.macBook.getDescription()}, Engraving`;
  }
}

// 구체 데코레이터 3: 보험
class Insurance extends MacBookDecorator {
  getCost(): number {
    return this.macBook.getCost() + 250;
  }

  getDescription(): string {
    return `${this.macBook.getDescription()}, Insurance`;
  }
}

// 사용 — 데코레이터를 점진적으로 추가
let mb: MacBookComponent = new MacBook();
mb = new MemoryUpgrade(mb);
mb = new Engraving(mb);
mb = new Insurance(mb);

console.log(mb.getCost());        // 1522 (997 + 75 + 200 + 250)
console.log(mb.getDescription()); // 'MacBook 11.6", Memory Upgrade, Engraving, Insurance'
```

모든 조합의 서브클래스를 만드는 대신, 5개의 데코레이터 클래스만으로 수십 가지 조합을 표현할 수 있다.

### 3.3 함수형 데코레이터

TypeScript에서는 함수를 감싸는 방식으로도 데코레이터를 구현할 수 있다:

```typescript
// 함수형 데코레이터 — 로깅
function withLogging<T extends (...args: any[]) => any>(
  fn: T,
  label: string,
): T {
  return function (this: any, ...args: Parameters<T>): ReturnType<T> {
    console.log(`[${label}] 호출: ${fn.name}(${args.join(", ")})`);
    const result = fn.apply(this, args);
    console.log(`[${label}] 결과: ${result}`);
    return result;
  } as T;
}

// 타이밍 데코레이터
function withTiming<T extends (...args: any[]) => any>(
  fn: T,
  label: string,
): T {
  return function (this: any, ...args: Parameters<T>): ReturnType<T> {
    const start = performance.now();
    const result = fn.apply(this, args);
    console.log(`[${label}] ${(performance.now() - start).toFixed(2)}ms`);
    return result;
  } as T;
}

function calculateTotal(prices: number[]): number {
  return prices.reduce((sum, p) => sum + p, 0);
}

const loggedTotal = withLogging(calculateTotal, "CALC");
const timedLoggedTotal = withTiming(loggedTotal, "PERF");

timedLoggedTotal([10, 20, 30]);
// [CALC] 호출: calculateTotal(10,20,30)
// [CALC] 결과: 60
// [PERF] 0.05ms
```

### 3.4 TC39 데코레이터 (Stage 3 → 표준)

TC39 데코레이터(*TC39 Decorator — ECMAScript 표준으로 진행 중인 메타프로그래밍 문법*)는 `@` 구문으로 클래스와 메서드를 장식한다:

```typescript
// TC39 표준 데코레이터 (Stage 3)
// tsconfig.json: "experimentalDecorators": false (새 표준 사용 시)

function log(
  _target: any,
  context: ClassMethodDecoratorContext,
) {
  const methodName = String(context.name);
  return function (this: any, ...args: any[]) {
    console.log(`→ ${methodName}(${args.join(", ")})`);
    const result = (_target as Function).apply(this, args);
    console.log(`← ${methodName}: ${result}`);
    return result;
  };
}

function sealed(constructor: Function, _context: ClassDecoratorContext) {
  Object.seal(constructor);
  Object.seal(constructor.prototype);
}

@sealed
class Calculator {
  @log
  add(a: number, b: number): number {
    return a + b;
  }

  @log
  multiply(a: number, b: number): number {
    return a * b;
  }
}

const calc = new Calculator();
calc.add(2, 3);
// → add(2, 3)
// ← add: 5
```

### JavaScript vs TypeScript

```javascript
// JavaScript — 데코레이터 인터페이스 충족을 보장할 수 없음
class MemoryUpgrade {
  constructor(macBook) {
    this.macBook = macBook;
  }
  getCost() {
    return this.macBook.getCost() + 75; // macBook에 getCost가 없으면 런타임 에러
  }
  // getDescription()을 깜빡해도 아무 경고 없음
}
```

```typescript
// TypeScript — 인터페이스로 데코레이터 계약 강제
interface MacBookComponent {
  getCost(): number;
  getDescription(): string;
}

class MemoryUpgrade implements MacBookComponent {
  constructor(private macBook: MacBookComponent) {}
  getCost(): number { return this.macBook.getCost() + 75; }
  // getDescription()을 빠뜨리면 → 컴파일 에러!
  getDescription(): string { return `${this.macBook.getDescription()}, Memory`; }
}
```

> **Osmani의 조언**: 데코레이터는 객체를 동적으로 확장할 수 있으므로, 이미 동작하는 시스템의 내용을 변경하기에 매우 적합한 패턴이다. 가끔은 각 객체 타입의 개별 서브클래스를 관리하는 것보다 객체를 감싸는 데코레이터를 만드는 게 더 쉬울 때도 있다.

---

## 4. 플라이웨이트 패턴 (Flyweight Pattern)

플라이웨이트(*Flyweight — 복싱 체급에서 이름을 따왔으며, 메모리 공간의 경량화를 목표로 함*) 패턴은 반복되고 비효율적으로 데이터를 공유하는 코드를 최적화하는 전통적인 구조 패턴이다. 연관된 객체끼리 데이터를 공유하게 하면서 애플리케이션의 메모리를 최소화한다.

### 패턴 카드: Flyweight

| 항목 | 설명 |
|------|------|
| **의도** | 많은 유사 객체 간 공통 상태를 공유하여 메모리 사용을 최소화한다 |
| **사용 시점** | 수천~수만 개의 유사 객체를 생성해야 하고 메모리가 제한될 때 |
| **미사용 시점** | 객체 수가 적거나, 각 객체의 상태가 모두 고유한 경우 |
| **장점** | 메모리 절약, 대량 객체 처리 시 성능 향상 |
| **단점** | 코드 복잡성 증가, 내재적/외재적 상태 분리의 설계 비용 |

### 4.1 내재적 상태 vs 외재적 상태

플라이웨이트 패턴에는 두 가지 핵심 개념이 있다:

| 구분 | 내재적 상태 (*Intrinsic State*) | 외재적 상태 (*Extrinsic State*) |
|------|-------------------------------|-------------------------------|
| **위치** | 플라이웨이트 객체 내부 | 외부 관리자(Manager)에 저장 |
| **공유** | 여러 컨텍스트에서 공유 가능 | 각 컨텍스트마다 고유 |
| **변경** | 불변 | 변경 가능 |
| **예시** | 책의 제목, 저자, ISBN | 대출일, 반납일, 대출자 |

### 4.2 도서관 시스템 — 최적화 전

```typescript
// 최적화 전 — 모든 속성을 각 Book 인스턴스에 저장
class BookUnoptimized {
  constructor(
    public id: string,
    public title: string,
    public author: string,
    public genre: string,
    public pageCount: number,
    public publisherID: string,
    public ISBN: string,
    public checkoutDate: string,
    public checkoutMember: string,
    public dueReturnDate: string,
    public availability: boolean,
  ) {}

  getTitle(): string { return this.title; }
  getAuthor(): string { return this.author; }

  updateCheckoutStatus(
    newStatus: boolean,
    checkoutDate: string,
    member: string,
    returnDate: string,
  ): void {
    this.availability = newStatus;
    this.checkoutDate = checkoutDate;
    this.checkoutMember = member;
    this.dueReturnDate = returnDate;
  }

  isPastDue(): boolean {
    return Date.now() > Date.parse(this.dueReturnDate);
  }
}
```

처음에 책이 조금만 있을 때는 잘 작동하겠지만, 수천 개의 책 객체를 다루면 메모리에 부담이 된다.

### 4.3 도서관 시스템 — 플라이웨이트 적용

내재적 상태(책의 메타데이터)와 외재적 상태(대출 정보)를 분리한다:

```typescript
// 플라이웨이트 객체 — 내재적 상태만 보유 (공유됨)
class Book {
  constructor(
    public readonly title: string,
    public readonly author: string,
    public readonly genre: string,
    public readonly pageCount: number,
    public readonly publisherID: string,
    public readonly ISBN: string,
  ) {}
}

// 플라이웨이트 팩토리 — 같은 ISBN의 Book은 하나만 생성
class BookFactory {
  static #existingBooks = new Map<string, Book>();

  static createBook(
    title: string,
    author: string,
    genre: string,
    pageCount: number,
    publisherID: string,
    ISBN: string,
  ): Book {
    const existing = BookFactory.#existingBooks.get(ISBN);
    if (existing) return existing;

    const book = new Book(title, author, genre, pageCount, publisherID, ISBN);
    BookFactory.#existingBooks.set(ISBN, book);
    return book;
  }

  static getBookCount(): number {
    return BookFactory.#existingBooks.size;
  }
}

// 외재적 상태를 관리하는 레코드
interface BookRecord {
  book: Book;
  checkoutMember: string;
  checkoutDate: string;
  dueReturnDate: string;
  availability: boolean;
}

// 외부 상태 관리자
class BookRecordManager {
  #database = new Map<string, BookRecord>();

  addBookRecord(
    id: string,
    title: string,
    author: string,
    genre: string,
    pageCount: number,
    publisherID: string,
    ISBN: string,
    checkoutDate: string,
    checkoutMember: string,
    dueReturnDate: string,
    availability: boolean,
  ): void {
    const book = BookFactory.createBook(
      title, author, genre, pageCount, publisherID, ISBN,
    );
    this.#database.set(id, {
      book,
      checkoutMember,
      checkoutDate,
      dueReturnDate,
      availability,
    });
  }

  updateCheckoutStatus(
    bookID: string,
    newStatus: boolean,
    checkoutDate: string,
    member: string,
    returnDate: string,
  ): void {
    const record = this.#database.get(bookID);
    if (!record) return;
    record.availability = newStatus;
    record.checkoutDate = checkoutDate;
    record.checkoutMember = member;
    record.dueReturnDate = returnDate;
  }

  extendCheckoutPeriod(bookID: string, newReturnDate: string): void {
    const record = this.#database.get(bookID);
    if (record) record.dueReturnDate = newReturnDate;
  }

  isPastDue(bookID: string): boolean {
    const record = this.#database.get(bookID);
    if (!record) return false;
    return Date.now() > Date.parse(record.dueReturnDate);
  }
}
```

같은 책에 대해 30권의 사본이 있다고 해도 `Book` 객체는 단 한 번만 생성된다. 대출 관련 메서드는 `BookRecordManager`에 위치하여 외재적 데이터를 다룬다.

### 4.4 DOM 이벤트 위임 — 플라이웨이트 적용

플라이웨이트 패턴은 DOM 레이어에도 적용할 수 있다. 각 자식 요소에 이벤트 핸들러를 등록하는 대신, 부모 요소에 하나의 핸들러를 등록하여 이벤트 버블링(*Event Bubbling — 하위 요소에서 발생한 이벤트가 상위 요소로 전파되는 방식*)을 활용한다:

```typescript
// 플라이웨이트 없이 — 각 요소마다 핸들러 등록
document.querySelectorAll(".toggle").forEach((el) => {
  el.addEventListener("click", function () {
    this.querySelector(".info")?.classList.toggle("visible");
  });
});

// 플라이웨이트 적용 — 부모에 하나의 핸들러 (이벤트 위임)
class AccordionManager {
  constructor(containerId: string) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.addEventListener("click", (e) => {
      const toggle = (e.target as HTMLElement).closest(".toggle");
      if (!toggle) return;

      const info = toggle.querySelector(".info");
      if (info) {
        info.classList.toggle("visible");
      }
    });
  }
}

// 수백 개의 .toggle 요소가 있어도 이벤트 핸들러는 하나
const accordion = new AccordionManager("container");
```

> **핵심 통찰**: 플라이웨이트의 핵심은 "같은 내재적 상태를 가진 객체는 공유한다"는 원칙이다. 이벤트 위임은 DOM에서의 플라이웨이트 적용으로, 수백 개의 핸들러를 하나의 부모 핸들러로 대체한다. React의 이벤트 시스템도 내부적으로 이 원리를 사용한다.

---

## 5. 어댑터 패턴 (Adapter Pattern)

어댑터(*Adapter — 호환되지 않는 인터페이스 사이의 변환기 역할*) 패턴은 기존 클래스의 인터페이스를 클라이언트가 기대하는 다른 인터페이스로 변환한다. 서로 호환되지 않는 인터페이스 때문에 함께 동작할 수 없는 클래스들을 연결해준다.

### 패턴 카드: Adapter

| 항목 | 설명 |
|------|------|
| **의도** | 호환되지 않는 인터페이스를 가진 클래스들이 함께 동작할 수 있게 변환한다 |
| **사용 시점** | 기존 코드를 변경하지 않고 새로운 인터페이스에 맞춰야 할 때 (레거시 API 통합, 서드파티 라이브러리 교체) |
| **미사용 시점** | 인터페이스를 직접 수정할 수 있거나, 변환이 불필요하게 복잡해질 때 |
| **장점** | 기존 코드 무변경, 단일 책임 원칙 준수, Open-Closed 원칙 준수 |
| **단점** | 코드 복잡성 증가, 어댑터 레이어의 성능 오버헤드 |

### 5.1 기본 어댑터 — 구 API에서 신 API로

```typescript
// 구 API — 변경 불가능한 레거시 인터페이스
interface OldLogger {
  logMessage(message: string, level: number): void;
  getLogHistory(): string[];
}

class LegacyLogger implements OldLogger {
  #history: string[] = [];

  logMessage(message: string, level: number): void {
    const entry = `[Level ${level}] ${message}`;
    this.#history.push(entry);
    console.log(entry);
  }

  getLogHistory(): string[] {
    return [...this.#history];
  }
}

// 신 API — 애플리케이션이 기대하는 인터페이스
interface NewLogger {
  debug(message: string): void;
  info(message: string): void;
  warn(message: string): void;
  error(message: string): void;
  history(): readonly string[];
}

// 어댑터 — 구 API를 신 API 인터페이스로 변환
class LoggerAdapter implements NewLogger {
  #adaptee: OldLogger;

  constructor(legacyLogger: OldLogger) {
    this.#adaptee = legacyLogger;
  }

  debug(message: string): void {
    this.#adaptee.logMessage(message, 0);
  }

  info(message: string): void {
    this.#adaptee.logMessage(message, 1);
  }

  warn(message: string): void {
    this.#adaptee.logMessage(message, 2);
  }

  error(message: string): void {
    this.#adaptee.logMessage(message, 3);
  }

  history(): readonly string[] {
    return this.#adaptee.getLogHistory();
  }
}

// 사용 — 클라이언트는 NewLogger 인터페이스만 알면 됨
const logger: NewLogger = new LoggerAdapter(new LegacyLogger());
logger.info("Application started");
logger.error("Something went wrong");
console.log(logger.history());
// ["[Level 1] Application started", "[Level 3] Something went wrong"]
```

### 5.2 실전 예제 — HTTP 클라이언트 어댑터

서드파티 HTTP 라이브러리를 교체할 때 어댑터 패턴이 빛난다:

```typescript
// 애플리케이션이 기대하는 HTTP 인터페이스
interface HttpClient {
  get<T>(url: string, options?: RequestOptions): Promise<ApiResponse<T>>;
  post<T>(url: string, body: unknown, options?: RequestOptions): Promise<ApiResponse<T>>;
}

interface RequestOptions {
  headers?: Record<string, string>;
  timeout?: number;
}

interface ApiResponse<T> {
  data: T;
  status: number;
  headers: Record<string, string>;
}

// Axios 어댑터
class AxiosAdapter implements HttpClient {
  #instance: AxiosInstance;

  constructor(baseURL: string) {
    this.#instance = axios.create({ baseURL });
  }

  async get<T>(url: string, options?: RequestOptions): Promise<ApiResponse<T>> {
    const response = await this.#instance.get<T>(url, {
      headers: options?.headers,
      timeout: options?.timeout,
    });
    return {
      data: response.data,
      status: response.status,
      headers: response.headers as Record<string, string>,
    };
  }

  async post<T>(url: string, body: unknown, options?: RequestOptions): Promise<ApiResponse<T>> {
    const response = await this.#instance.post<T>(url, body, {
      headers: options?.headers,
      timeout: options?.timeout,
    });
    return {
      data: response.data,
      status: response.status,
      headers: response.headers as Record<string, string>,
    };
  }
}

// Fetch 어댑터 — 라이브러리 교체 시 어댑터만 변경
class FetchAdapter implements HttpClient {
  #baseURL: string;

  constructor(baseURL: string) {
    this.#baseURL = baseURL;
  }

  async get<T>(url: string, options?: RequestOptions): Promise<ApiResponse<T>> {
    const response = await fetch(`${this.#baseURL}${url}`, {
      headers: options?.headers,
      signal: options?.timeout
        ? AbortSignal.timeout(options.timeout)
        : undefined,
    });
    const data = await response.json() as T;
    return {
      data,
      status: response.status,
      headers: Object.fromEntries(response.headers.entries()),
    };
  }

  async post<T>(url: string, body: unknown, options?: RequestOptions): Promise<ApiResponse<T>> {
    const response = await fetch(`${this.#baseURL}${url}`, {
      method: "POST",
      body: JSON.stringify(body),
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
      signal: options?.timeout
        ? AbortSignal.timeout(options.timeout)
        : undefined,
    });
    const data = await response.json() as T;
    return { data, status: response.status, headers: Object.fromEntries(response.headers.entries()) };
  }
}

// 사용 — 어댑터를 교체해도 비즈니스 로직은 변경 없음
// const http: HttpClient = new AxiosAdapter("https://api.example.com");
const http: HttpClient = new FetchAdapter("https://api.example.com");

interface User {
  id: number;
  name: string;
}

const { data } = await http.get<User[]>("/users");
```

### JavaScript vs TypeScript

```javascript
// JavaScript — 어댑터가 올바른 인터페이스를 구현하는지 보장 없음
class LoggerAdapter {
  constructor(legacy) { this.legacy = legacy; }
  info(msg) { this.legacy.logMessage(msg, 1); }
  // error()를 깜빡해도 런타임까지 에러 없음
}
```

```typescript
// TypeScript — implements로 인터페이스 계약 강제
class LoggerAdapter implements NewLogger {
  constructor(private legacy: OldLogger) {}
  info(message: string): void { this.legacy.logMessage(message, 1); }
  // error()가 없으면 → 컴파일 에러!
  // "Class 'LoggerAdapter' incorrectly implements interface 'NewLogger'"
}
```

> **핵심 통찰**: 어댑터 패턴은 "기존 코드를 변경하지 않고 새로운 인터페이스에 맞추는" 가장 직관적인 방법이다. TypeScript의 `implements` 키워드가 어댑터의 인터페이스 충족을 컴파일 타임에 보장하므로, 라이브러리 교체 시 누락된 메서드를 즉시 발견할 수 있다.

---

## 6. 프록시 패턴 (Proxy Pattern)

프록시(*Proxy — 다른 객체에 대한 접근을 제어하는 대리 객체*) 패턴은 실제 객체 대신 대리 객체를 제공하여 접근을 제어한다. ES6에서 도입된 `Proxy` 내장 객체로 자바스크립트에서 네이티브하게 지원된다.

### 패턴 카드: Proxy

| 항목 | 설명 |
|------|------|
| **의도** | 다른 객체에 대한 접근을 제어하거나 추가 로직을 삽입하는 대리 객체를 제공한다 |
| **사용 시점** | 지연 로딩, 접근 제어, 캐싱, 로깅 등 원본 객체에 부가 기능이 필요할 때 |
| **미사용 시점** | 단순한 객체 접근에 불필요한 간접 참조를 추가하는 경우 |
| **장점** | Open-Closed 원칙 준수, 관심사 분리, 투명한 기능 추가 |
| **단점** | 간접 참조로 인한 성능 오버헤드, 디버깅 복잡도 증가 |

### 6.1 ES6 Proxy — 기본 사용

```typescript
// 기본 Proxy — 속성 접근/설정 가로채기
interface UserData {
  name: string;
  age: number;
  email: string;
  [key: string]: unknown;
}

const user: UserData = { name: "Alice", age: 30, email: "alice@example.com" };

const userProxy = new Proxy(user, {
  get(target, property: string, receiver) {
    console.log(`속성 읽기: ${property}`);
    return Reflect.get(target, property, receiver);
  },

  set(target, property: string, value, receiver) {
    console.log(`속성 쓰기: ${property} = ${value}`);

    // 유효성 검사
    if (property === "age" && (typeof value !== "number" || value < 0)) {
      throw new TypeError("age는 0 이상의 숫자여야 합니다");
    }

    return Reflect.set(target, property, value, receiver);
  },
});

userProxy.name;         // 속성 읽기: name → "Alice"
userProxy.age = 31;     // 속성 쓰기: age = 31
// userProxy.age = -5;  // TypeError: age는 0 이상의 숫자여야 합니다
```

### 6.2 가상 프록시 (Virtual Proxy) — 지연 로딩

무거운 객체를 필요한 시점까지 생성을 지연한다:

```typescript
interface Image {
  display(): void;
  getSize(): { width: number; height: number };
}

// 실제 객체 — 생성 비용이 높음
class HighResImage implements Image {
  #data: Uint8Array;
  #width: number;
  #height: number;

  constructor(private url: string) {
    console.log(`고해상도 이미지 로딩 중: ${url}`);
    // 무거운 초기화 (네트워크 요청, 디코딩 등)
    this.#data = new Uint8Array(1024 * 1024 * 10); // 10MB
    this.#width = 3840;
    this.#height = 2160;
  }

  display(): void {
    console.log(`이미지 표시: ${this.url} (${this.#width}x${this.#height})`);
  }

  getSize(): { width: number; height: number } {
    return { width: this.#width, height: this.#height };
  }
}

// 가상 프록시 — 실제 사용 시점까지 생성 지연
class ImageProxy implements Image {
  #realImage: HighResImage | null = null;

  constructor(private url: string) {
    console.log(`이미지 프록시 생성 (아직 로딩 안 함): ${url}`);
  }

  #loadImage(): HighResImage {
    if (!this.#realImage) {
      this.#realImage = new HighResImage(this.url);
    }
    return this.#realImage;
  }

  display(): void {
    this.#loadImage().display();
  }

  getSize(): { width: number; height: number } {
    return this.#loadImage().getSize();
  }
}

// 100개의 이미지를 생성해도 실제 로딩은 display() 호출 시에만 발생
const images: Image[] = Array.from(
  { length: 100 },
  (_, i) => new ImageProxy(`https://cdn.example.com/img/${i}.jpg`),
);
// "이미지 프록시 생성 (아직 로딩 안 함)" × 100

images[0].display();
// "고해상도 이미지 로딩 중: .../0.jpg" — 이 시점에 실제 로딩
// "이미지 표시: .../0.jpg (3840x2160)"
```

### 6.3 보호 프록시 (Protection Proxy) — 접근 제어

```typescript
interface AdminPanel {
  deleteUser(userId: string): void;
  viewLogs(): string[];
  modifySettings(key: string, value: unknown): void;
}

type UserRole = "admin" | "moderator" | "user";

class RealAdminPanel implements AdminPanel {
  deleteUser(userId: string): void {
    console.log(`사용자 ${userId} 삭제됨`);
  }

  viewLogs(): string[] {
    return ["[2026-01-01] Login", "[2026-01-02] Error"];
  }

  modifySettings(key: string, value: unknown): void {
    console.log(`설정 변경: ${key} = ${value}`);
  }
}

// 역할 기반 접근 제어 정의
const permissions: Record<UserRole, Set<keyof AdminPanel>> = {
  admin: new Set(["deleteUser", "viewLogs", "modifySettings"]),
  moderator: new Set(["viewLogs"]),
  user: new Set([]),
};

// 보호 프록시 팩토리
function createProtectedPanel(
  panel: AdminPanel,
  role: UserRole,
): AdminPanel {
  return new Proxy(panel, {
    get(target, property: string, receiver) {
      const allowed = permissions[role];

      if (typeof target[property as keyof AdminPanel] === "function") {
        if (!allowed.has(property as keyof AdminPanel)) {
          return () => {
            throw new Error(
              `권한 부족: ${role}은(는) ${property}에 접근할 수 없습니다`,
            );
          };
        }
      }

      return Reflect.get(target, property, receiver);
    },
  });
}

// 사용
const panel = new RealAdminPanel();
const moderatorPanel = createProtectedPanel(panel, "moderator");

moderatorPanel.viewLogs();      // ["[2026-01-01] Login", ...]
// moderatorPanel.deleteUser("123");
// → Error: 권한 부족: moderator은(는) deleteUser에 접근할 수 없습니다
```

### 6.4 캐싱 프록시 (Caching Proxy)

```typescript
interface DataService {
  fetchData(key: string): Promise<unknown>;
}

class ApiService implements DataService {
  async fetchData(key: string): Promise<unknown> {
    console.log(`API 호출: ${key}`);
    // 실제로는 네트워크 요청
    return { key, data: Math.random(), fetchedAt: Date.now() };
  }
}

// 캐싱 프록시
class CachingProxy implements DataService {
  #cache = new Map<string, { data: unknown; expiry: number }>();
  #ttl: number;

  constructor(
    private service: DataService,
    ttlMs: number = 60_000, // 기본 1분 TTL
  ) {
    this.#ttl = ttlMs;
  }

  async fetchData(key: string): Promise<unknown> {
    const cached = this.#cache.get(key);

    if (cached && cached.expiry > Date.now()) {
      console.log(`캐시 히트: ${key}`);
      return cached.data;
    }

    console.log(`캐시 미스: ${key}`);
    const data = await this.service.fetchData(key);
    this.#cache.set(key, { data, expiry: Date.now() + this.#ttl });
    return data;
  }

  clearCache(): void {
    this.#cache.clear();
  }
}

// 사용
const api = new CachingProxy(new ApiService(), 30_000);

await api.fetchData("users");  // 캐시 미스 → API 호출
await api.fetchData("users");  // 캐시 히트 → 네트워크 요청 없음
```

### JavaScript vs TypeScript

```javascript
// JavaScript — Proxy 핸들러의 타입 안전성 없음
const proxy = new Proxy(target, {
  get(target, prop) {
    // prop이 string | symbol이지만 IDE가 target의 실제 속성을 모름
    return target[prop]; // 오타가 있어도 런타임까지 발견 불가
  }
});
```

```typescript
// TypeScript — ProxyHandler<T>로 타입 체크
const proxy = new Proxy<UserData>(target, {
  get(target, property: keyof UserData, receiver) {
    return Reflect.get(target, property, receiver);
    // target의 속성 타입이 자동 추론됨
  },
  set(target, property: keyof UserData, value) {
    // value의 타입이 UserData[typeof property]와 호환되는지 검증 가능
    return Reflect.set(target, property, value);
  },
});
```

> **Osmani의 조언**: ES6 Proxy는 자바스크립트에서 메타프로그래밍의 문을 열었다. 반응형 시스템(Vue 3, MobX)의 핵심에 Proxy가 있으며, 유효성 검사, 접근 제어, 캐싱 등 횡단 관심사를 투명하게 처리할 수 있다.

---

## 7. 컴포지트 패턴 (Composite Pattern)

컴포지트(*Composite — 객체를 트리 구조로 구성하여 부분-전체 계층을 표현*) 패턴은 객체들을 트리 구조로 구성하여 **단일 객체와 복합 객체를 동일하게 취급**할 수 있게 한다. 클라이언트는 개별 객체인지 그룹인지 구분하지 않고 동일한 인터페이스로 다룬다.

### 패턴 카드: Composite

| 항목 | 설명 |
|------|------|
| **의도** | 객체를 트리 구조로 구성하여 부분-전체 계층을 표현하고, 단일/복합 객체를 동일하게 취급한다 |
| **사용 시점** | 재귀적 트리 구조 (파일 시스템, UI 컴포넌트 트리, 메뉴 구조) |
| **미사용 시점** | 트리 구조가 아닌 평면적인 데이터를 다룰 때 |
| **장점** | 단일/복합 객체의 통일된 인터페이스, 새로운 요소 추가 용이 |
| **단점** | 지나친 일반화로 타입 안전성 감소, 리프와 컴포지트의 차이를 숨길 수 있음 |

### 7.1 파일 시스템 예제

```typescript
// 컴포넌트 인터페이스
interface FileSystemNode {
  readonly name: string;
  getSize(): number;
  print(indent?: string): void;
}

// 리프 (Leaf) — 자식이 없는 개별 객체
class File implements FileSystemNode {
  constructor(
    public readonly name: string,
    private sizeInBytes: number,
  ) {}

  getSize(): number {
    return this.sizeInBytes;
  }

  print(indent = ""): void {
    console.log(`${indent}📄 ${this.name} (${this.sizeInBytes} bytes)`);
  }
}

// 컴포지트 (Composite) — 자식을 가질 수 있는 복합 객체
class Directory implements FileSystemNode {
  #children: FileSystemNode[] = [];

  constructor(public readonly name: string) {}

  add(node: FileSystemNode): this {
    this.#children.push(node);
    return this;
  }

  remove(name: string): boolean {
    const index = this.#children.findIndex((c) => c.name === name);
    if (index === -1) return false;
    this.#children.splice(index, 1);
    return true;
  }

  // 핵심: 리프의 getSize()와 동일한 인터페이스
  getSize(): number {
    return this.#children.reduce((sum, child) => sum + child.getSize(), 0);
  }

  print(indent = ""): void {
    console.log(`${indent}📁 ${this.name} (${this.getSize()} bytes)`);
    for (const child of this.#children) {
      child.print(indent + "  ");
    }
  }
}

// 사용 — 단일 File과 복합 Directory를 동일하게 다룸
const src = new Directory("src");
src
  .add(new File("index.ts", 1500))
  .add(new File("app.ts", 3200));

const components = new Directory("components");
components
  .add(new File("Button.tsx", 800))
  .add(new File("Modal.tsx", 1200));

src.add(components);

const root = new Directory("project");
root
  .add(src)
  .add(new File("package.json", 500))
  .add(new File("tsconfig.json", 300));

root.print();
// 📁 project (7500 bytes)
//   📁 src (6700 bytes)
//     📄 index.ts (1500 bytes)
//     📄 app.ts (3200 bytes)
//     📁 components (2000 bytes)
//       📄 Button.tsx (800 bytes)
//       📄 Modal.tsx (1200 bytes)
//   📄 package.json (500 bytes)
//   📄 tsconfig.json (300 bytes)

// getSize()는 File이든 Directory든 동일하게 호출
console.log(root.getSize());       // 7500
console.log(components.getSize()); // 2000
```

### 7.2 React 컴포넌트 트리 — 실세계의 컴포지트

React의 컴포넌트 트리는 본질적으로 컴포지트 패턴이다. 단일 컴포넌트(`<Button>`)와 복합 컴포넌트(`<Form>`)를 동일하게 `ReactNode`로 취급한다:

```typescript
// React 컴포넌트 트리 = 컴포지트 패턴
// 리프 컴포넌트
interface ButtonProps {
  label: string;
  onClick: () => void;
}

const Button = ({ label, onClick }: ButtonProps) => (
  <button onClick={onClick}>{label}</button>
);

// 컴포지트 컴포넌트 — children을 통해 자식을 포함
interface CardProps {
  title: string;
  children: React.ReactNode; // 단일 또는 복합 자식
}

const Card = ({ title, children }: CardProps) => (
  <div className="card">
    <h2>{title}</h2>
    <div className="card-body">{children}</div>
  </div>
);

// 사용 — 트리 구조로 합성
const App = () => (
  <Card title="Dashboard">
    <Card title="Statistics">
      <Button label="Refresh" onClick={() => {}} />
    </Card>
    <Button label="Settings" onClick={() => {}} />
  </Card>
);
// Card > [Card > Button, Button] — 컴포지트 트리
```

### 7.3 제네릭 컴포지트 — 재사용 가능한 트리

```typescript
// 제네릭 컴포지트 클래스
class TreeNode<T> {
  #children: TreeNode<T>[] = [];

  constructor(public readonly value: T) {}

  add(...children: TreeNode<T>[]): this {
    this.#children.push(...children);
    return this;
  }

  // 재귀적 순회
  traverse(callback: (value: T, depth: number) => void, depth = 0): void {
    callback(this.value, depth);
    for (const child of this.#children) {
      child.traverse(callback, depth + 1);
    }
  }

  // 재귀적 검색
  find(predicate: (value: T) => boolean): TreeNode<T> | undefined {
    if (predicate(this.value)) return this;
    for (const child of this.#children) {
      const found = child.find(predicate);
      if (found) return found;
    }
    return undefined;
  }

  // 재귀적 집계
  reduce<R>(fn: (acc: R, value: T) => R, initial: R): R {
    let result = fn(initial, this.value);
    for (const child of this.#children) {
      result = child.reduce(fn, result);
    }
    return result;
  }
}

// 사용 — 조직도
interface Employee {
  name: string;
  role: string;
  salary: number;
}

const ceo = new TreeNode<Employee>({ name: "Alice", role: "CEO", salary: 200000 });
const cto = new TreeNode<Employee>({ name: "Bob", role: "CTO", salary: 150000 });
const dev1 = new TreeNode<Employee>({ name: "Charlie", role: "Dev", salary: 90000 });
const dev2 = new TreeNode<Employee>({ name: "Diana", role: "Dev", salary: 95000 });

ceo.add(cto.add(dev1, dev2));

// 전체 급여 합계
const totalSalary = ceo.reduce((sum, emp) => sum + emp.salary, 0);
console.log(totalSalary); // 535000

// 특정 직원 검색
const found = ceo.find((emp) => emp.name === "Diana");
console.log(found?.value.role); // "Dev"
```

> **핵심 통찰**: 컴포지트 패턴의 강점은 "부분과 전체를 동일하게 다룰 수 있다"는 점이다. React의 `children` prop, 파일 시스템의 재귀적 탐색, DOM 트리의 `querySelectorAll` 등 현대 프론트엔드의 핵심 추상화가 모두 컴포지트 패턴에 기반한다.

---

## 최신 업데이트 (2026)

### ES6 Proxy와 반응형 시스템

Vue 3와 MobX는 ES6 Proxy를 핵심으로 사용하여 반응형 시스템을 구축한다. 속성 접근/설정을 가로채어 의존성 추적과 자동 리렌더링을 구현한다:

```typescript
// Vue 3 반응형의 핵심 원리 (간략화)
type EffectFn = () => void;

const targetMap = new WeakMap<object, Map<string, Set<EffectFn>>>();
let activeEffect: EffectFn | null = null;

function track(target: object, key: string): void {
  if (!activeEffect) return;
  let depsMap = targetMap.get(target);
  if (!depsMap) targetMap.set(target, (depsMap = new Map()));
  let deps = depsMap.get(key);
  if (!deps) depsMap.set(key, (deps = new Set()));
  deps.add(activeEffect);
}

function trigger(target: object, key: string): void {
  const deps = targetMap.get(target)?.get(key);
  if (deps) deps.forEach((fn) => fn());
}

function reactive<T extends object>(target: T): T {
  return new Proxy(target, {
    get(target, key: string, receiver) {
      track(target, key);
      return Reflect.get(target, key, receiver);
    },
    set(target, key: string, value, receiver) {
      const result = Reflect.set(target, key, value, receiver);
      trigger(target, key);
      return result;
    },
  });
}

// 사용
const state = reactive({ count: 0, name: "Vue" });

activeEffect = () => console.log(`count = ${state.count}`);
state.count; // 의존성 등록 (track)
activeEffect = null;

state.count = 1; // 자동으로 effect 실행 (trigger) → "count = 1"
```

### TC39 Decorators — 레거시에서 표준으로

TypeScript의 레거시 데코레이터(`"experimentalDecorators": true`)가 TC39 Stage 3 데코레이터로 대체되고 있다:

| 구분 | 레거시 TS 데코레이터 | TC39 표준 데코레이터 |
|------|---------------------|---------------------|
| **설정** | `"experimentalDecorators": true` | `"experimentalDecorators": false` (기본값) |
| **대상** | 클래스, 메서드, 접근자, 속성, 매개변수 | 클래스, 메서드, 접근자, 필드, auto-accessor |
| **메타데이터** | `reflect-metadata` 의존 | `context.metadata` 내장 |
| **실행 시점** | 런타임 | 런타임 |
| **호환성** | TypeScript 전용 | ECMAScript 표준 (브라우저/Node.js 네이티브) |

```typescript
// TC39 표준 auto-accessor 데코레이터
function observable(
  _target: ClassAccessorDecoratorTarget<unknown, unknown>,
  context: ClassAccessorDecoratorContext,
) {
  return {
    set(this: any, value: unknown) {
      const oldValue = context.access.get(this);
      context.access.set(this, value);
      console.log(`${String(context.name)}: ${oldValue} → ${value}`);
    },
  } satisfies ClassAccessorDecoratorResult<unknown, unknown>;
}

class Settings {
  @observable accessor theme = "light";
  @observable accessor fontSize = 14;
}

const settings = new Settings();
settings.theme = "dark";    // "theme: light → dark"
settings.fontSize = 16;     // "fontSize: 14 → 16"
```

### React Server Components — 현대적 퍼사드

React Server Components(RSC)는 서버 측 데이터 페칭과 클라이언트 렌더링의 복잡성을 퍼사드 패턴으로 추상화한다. 컴포넌트 작성자는 `async/await`만으로 서버 데이터에 접근하고, RSC 프레임워크가 직렬화, 스트리밍, 하이드레이션을 내부적으로 처리한다:

```typescript
// React Server Component — 서버 데이터 접근의 퍼사드
// 내부적으로 직렬화, 스트리밍, 캐싱을 처리하지만
// 개발자는 일반 async 함수처럼 작성
async function UserProfile({ userId }: { userId: string }) {
  const user = await db.user.findUnique({ where: { id: userId } });
  const posts = await db.post.findMany({ where: { authorId: userId } });

  return (
    <div>
      <h1>{user.name}</h1>
      <PostList posts={posts} /> {/* Client Component */}
    </div>
  );
}
```

### Flyweight와 가상 리스트 라이브러리

`react-window`, `@tanstack/virtual` 같은 가상 리스트 라이브러리는 플라이웨이트 패턴의 현대적 적용이다. 수만 개의 행이 있어도 **뷰포트에 보이는 행만** 실제 DOM으로 렌더링한다:

```typescript
// @tanstack/react-virtual을 활용한 플라이웨이트
import { useVirtualizer } from "@tanstack/react-virtual";

function VirtualList({ items }: { items: string[] }) {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: items.length,    // 10만 행이라도
    getScrollElement: () => parentRef.current,
    estimateSize: () => 35, // 각 행의 예상 높이
    overscan: 5,            // 뷰포트 밖 5행 추가 렌더링
  });

  return (
    <div ref={parentRef} style={{ height: 400, overflow: "auto" }}>
      <div style={{ height: virtualizer.getTotalSize() }}>
        {virtualizer.getVirtualItems().map((virtualRow) => (
          <div
            key={virtualRow.key}
            style={{
              position: "absolute",
              top: virtualRow.start,
              height: virtualRow.size,
            }}
          >
            {items[virtualRow.index]}
          </div>
        ))}
        {/* 10만 행 중 ~15개만 실제 DOM에 존재 — 플라이웨이트 */}
      </div>
    </div>
  );
}
```

---

## 실무 적용 가이드

### 패턴 선택 체크리스트

| 상황 | 권장 패턴 |
|------|-----------|
| 복잡한 하위 시스템을 단순하게 노출 | **퍼사드** (단일 인터페이스로 통합) |
| 여러 클래스에 공통 기능 추가 | **믹스인** (또는 함수 합성 / Hooks) |
| 서브클래싱 없이 동적 기능 확장 | **데코레이터** (TC39 표준 데코레이터 사용) |
| 대량의 유사 객체로 메모리 문제 | **플라이웨이트** (내재적/외재적 상태 분리) |
| 기존 인터페이스를 새 인터페이스에 맞춤 | **어댑터** (레거시 코드 통합에 필수) |
| 접근 제어, 캐싱, 지연 로딩 | **프록시** (ES6 Proxy 활용) |
| 트리 구조의 부분-전체 계층 표현 | **컴포지트** (React 컴포넌트 트리, 파일 시스템) |

### 패턴 간 관계

```
┌─────────────┐     감싸기      ┌──────────────┐
│  Decorator   │ ←─────────────→ │    Proxy      │
│ (기능 추가)  │                 │ (접근 제어)   │
└─────────────┘                 └──────────────┘
       │                               │
       │ 둘 다 "감싸기"이지만 의도가 다름  │
       │                               │
┌─────────────┐     단순화      ┌──────────────┐
│   Facade     │ ←─────────────→ │   Adapter     │
│ (복잡도 숨김) │                │ (인터페이스 변환) │
└─────────────┘                 └──────────────┘
       │
       │ 내부에서 사용
       │
┌─────────────┐                 ┌──────────────┐
│  Flyweight   │                │  Composite    │
│ (메모리 공유) │                │ (트리 구조)   │
└─────────────┘                 └──────────────┘
```

### TypeScript가 구조 패턴에 미치는 영향

| JavaScript 방식 | TypeScript 대안 |
|-----------------|-----------------|
| 런타임 인터페이스 검증 (`Interface.ensureImplements`) | `implements` 키워드 (컴파일 타임) |
| 덕 타이핑 기반 어댑터 | 명시적 인터페이스 + 제네릭 |
| 인스턴스에 메서드 동적 추가 | TC39 데코레이터 + `abstract class` |
| 수동 프록시 래퍼 | `Proxy<T>` + `ProxyHandler<T>` |
| 프로토타입 기반 믹스인 | `Constructor<T>` 제네릭 믹스인 |
| 런타임 타입 체크 | 판별 유니언 + 타입 가드 |

---

## 요약

- **퍼사드 패턴**: 복잡한 하위 시스템에 단순한 인터페이스를 제공한다. jQuery, React Server Components가 대표적 사례. TypeScript에서는 인터페이스로 퍼사드 계약을 강제한다
- **믹스인 패턴**: `extends`를 활용한 함수로 다중 상속을 시뮬레이션한다. 리액트에서는 Hooks/HOC로 대체되었으며, TypeScript `Constructor<T>` 제네릭으로 타입 안전성을 확보한다
- **데코레이터 패턴**: 서브클래싱 없이 객체에 동적 기능을 추가한다. TC39 표준 데코레이터(`@`)가 레거시 TypeScript 데코레이터를 대체하고 있다
- **플라이웨이트 패턴**: 내재적/외재적 상태를 분리하여 메모리를 최적화한다. 이벤트 위임과 가상 리스트(`@tanstack/virtual`)가 현대적 적용 사례다
- **어댑터 패턴**: 호환되지 않는 인터페이스를 변환한다. `implements` 키워드로 어댑터의 인터페이스 충족을 컴파일 타임에 보장한다
- **프록시 패턴**: ES6 `Proxy`로 접근 제어, 캐싱, 지연 로딩을 구현한다. Vue 3와 MobX의 반응형 시스템의 핵심이다
- **컴포지트 패턴**: 트리 구조에서 단일/복합 객체를 동일하게 취급한다. React 컴포넌트 트리, 파일 시스템 탐색이 대표적 사례다

---

## 다른 챕터와의 관계

- **← Ch05 (최신 JS 문법)**: `class`, `Proxy`, `#private` 필드, `extends` 등 구조 패턴의 기반 문법을 다룬다
- **← Ch06 (패턴 카테고리)**: 생성/구조/행위 분류 체계와 GoF 패턴 분류표를 제공한다
- **← Ch07 (생성 패턴)**: 구조 패턴이 다루는 객체들은 생성 패턴을 통해 만들어진다. 팩토리 + 플라이웨이트, 싱글톤 + 퍼사드 등 조합이 자주 사용된다
- **→ Ch09 (행위 패턴)**: 구조화된 객체들 간의 커뮤니케이션과 책임 분배 패턴(Observer, Mediator, Command 등)으로 이어진다
- **→ Ch14 (리액트 디자인 패턴)**: 컴포지트(컴포넌트 트리), 프록시(반응형 상태), 데코레이터(HOC)의 리액트 적용을 다룬다
