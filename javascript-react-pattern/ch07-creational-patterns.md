# Chapter 07: Creational Patterns (생성 패턴)

## 핵심 질문

> 객체를 생성하는 다양한 패턴은 무엇이며, TypeScript/현대 자바스크립트(ES2022+)에서 각 패턴은 어떻게 구현하고 언제 사용해야 하는가?

---

## 패턴 선택에 대하여

어느 프로젝트에나 어울리는 "최고의 패턴"이란 존재하지 않는다. 각 코드와 애플리케이션마다 요구하는 부분이 다를 수 있기 때문이다. 패턴이 **실질적인 구현에 도움이 되는지**를 기준으로 선택해야 한다.

> **Osmani의 조언**: 디자인 패턴에 대해 정확히 알고 사용할 때를 잘 파악하게 된다면, 애플리케이션 아키텍처에 올바른 디자인 패턴을 적용하기 수월해진다.

---

## 1. 생성 패턴 개요

생성 패턴(*Creational Pattern*)은 **객체를 생성하는 방법**을 다룬다. 기본적인 객체 생성 방식이 프로젝트의 복잡성을 증가시킬 수 있으므로, 생성 패턴은 이 과정을 제어하여 문제를 해결하는 것을 목표로 한다.

이 장에서 다루는 생성 패턴:

| 패턴 | 의도 |
|------|------|
| **생성자** (*Constructor*) | 새 객체를 초기화하는 특별한 메서드 |
| **모듈** (*Module*) | 공개/비공개 캡슐화를 통한 코드 구조화 |
| **노출 모듈** (*Revealing Module*) | 모듈 패턴의 가독성 개선 변형 |
| **싱글톤** (*Singleton*) | 클래스의 인스턴스를 하나만 허용 |
| **프로토타입** (*Prototype*) | 기존 객체를 복제하여 새 객체 생성 |
| **팩토리** (*Factory*) | 생성자 없이 객체를 생성하는 인터페이스 |
| **추상 팩토리** (*Abstract Factory*) | 관련 팩토리들을 하나의 그룹으로 캡슐화 |
| **빌더** (*Builder*) | 객체 생성과 표현을 분리하여 단계적으로 구성 |

---

## 2. 생성자 패턴 (Constructor Pattern)

생성자(*Constructor*)는 객체가 새로 만들어진 뒤 **초기화하는 데 사용되는 특별한 메서드**다. ES2015 이후로 `constructor`를 가진 클래스를 만들 수 있으며, `new` 키워드를 통해 인스턴스 객체를 생성한다.

### 패턴 카드: Constructor

| 항목 | 설명 |
|------|------|
| **의도** | 새로 생성된 객체를 초기화하고, 멤버 변수와 메서드를 할당한다 |
| **사용 시점** | 동일한 구조를 가진 객체를 여러 개 생성해야 할 때 |
| **미사용 시점** | 객체 생성 로직이 단순하여 클래스가 불필요할 때 |
| **장점** | 직관적, `instanceof`로 타입 확인 가능 |
| **단점** | 상속이 복잡해질 수 있고, 메서드가 인스턴스마다 재정의될 수 있다 |

### 2.1 객체 생성의 기본

TypeScript에서 새로운 객체를 만드는 방법:

```typescript
// 방법 1: 리터럴 표기법 (가장 일반적)
const obj1: Record<string, unknown> = {};

// 방법 2: Object.create()
const obj2 = Object.create(Object.prototype) as Record<string, unknown>;

// 방법 3: 타입 안전한 객체 생성 (권장)
interface Config {
  apiUrl: string;
  timeout: number;
}

const obj3: Config = { apiUrl: "https://api.example.com", timeout: 5000 };
```

속성 할당 — TypeScript에서는 인터페이스를 정의하여 타입 안전하게 속성을 관리한다:

```typescript
// Object.defineProperty — 세밀한 제어가 필요할 때
Object.defineProperty(obj1, "someKey", {
  value: "Hello World",
  writable: true,
  enumerable: true,
  configurable: true,
});
```

### 2.2 기본 생성자

```javascript
// JavaScript
class Car {
  constructor(model, year, miles) {
    this.model = model;  // 매번 수동 할당 필요
    this.year = year;
    this.miles = miles;
  }

  toString() {
    return `${this.model} has done ${this.miles} miles`;
  }
}
```

```typescript
// TypeScript — 매개변수 프로퍼티로 간결하게
class Car {
  constructor(
    public model: string,
    public year: number,
    public miles: number,
  ) {}
  // constructor 본문이 비어있다!
  // public/private/protected/readonly를 매개변수 앞에 붙이면
  // 선언 + 할당이 자동으로 이루어진다.

  toString(): string {
    return `${this.model} has done ${this.miles} miles`;
  }
}
```

```typescript
const civic = new Car("Honda Civic", 2009, 20000);
console.log(civic.toString()); // "Honda Civic has done 20000 miles"
```

TypeScript의 **매개변수 프로퍼티**(*Parameter Property*)는 접근 제한자를 매개변수 앞에 붙이는 것만으로 `this.x = x` 할당을 자동화한다. 프로퍼티가 많을수록 보일러플레이트 차이가 커진다.

### 2.3 프로토타입을 가진 생성자

ES2015+ 클래스에서는 메서드를 클래스 본문에 정의하면 자동으로 프로토타입에 할당되므로, 모든 인스턴스가 **같은 메서드를 공유**한다:

```typescript
class Car {
  constructor(
    public readonly model: string,
    public readonly year: number,
    private _miles: number,
  ) {}

  get miles(): number {
    return this._miles;
  }

  addTrip(distance: number): void {
    this._miles += distance;
  }

  // 프로토타입에 자동 할당 — 모든 인스턴스가 공유
  toString(): string {
    return `${this.model} has done ${this._miles} miles`;
  }
}

const civic = new Car("Honda Civic", 2009, 20000);
const mondeo = new Car("Ford Mondeo", 2010, 5000);

console.log(civic.toString());  // "Honda Civic has done 20000 miles"
console.log(mondeo.toString()); // "Ford Mondeo has done 5000 miles"
```

> **핵심 통찰**: TypeScript의 `readonly` 수정자와 `private`/`protected` 접근 제한자를 활용하면 생성자 패턴의 캡슐화를 컴파일 타임에 강제할 수 있다. 이는 JavaScript의 런타임 `#private` 필드와 상호보완적이다.

### 전통 vs 현대

```typescript
// 전통: 함수 생성자 + 프로토타입 (TypeScript에서는 권장하지 않음)
function OldCar(this: any, model: string) {
  this.model = model;
}
OldCar.prototype.toString = function () {
  return `Model: ${this.model}`;
};

// 현대: TypeScript 클래스 (매개변수 프로퍼티 + 접근 제한자)
class ModernCar {
  constructor(
    public readonly model: string,
    public readonly year: number,
    private _miles: number,
  ) {}

  toString(): string {
    return `${this.model} has done ${this._miles} miles`;
  }
}
```

---

## 3. 모듈 패턴 (Module Pattern)

모듈(*Module*)은 애플리케이션 아키텍처의 핵심 구성 요소이며, 코드 단위를 체계적으로 분리 및 관리하는 데 활용된다. 모듈 패턴은 클로저(*Closure — 함수가 선언된 렉시컬 스코프를 기억하는 기능*)를 활용해 **공개(public)와 비공개(private) 멤버를 구분**한다.

### 패턴 카드: Module

| 항목 | 설명 |
|------|------|
| **의도** | 공개/비공개 캡슐화를 통해 전역 스코프 오염을 방지한다 |
| **사용 시점** | 관련 기능을 하나의 단위로 묶고, 내부 구현을 숨기고 싶을 때 |
| **미사용 시점** | 단순한 유틸리티 함수 모음처럼 캡슐화가 불필요한 경우 |
| **장점** | 캡슐화, 네임스페이스 관리, 의존성 분리 |
| **단점** | 비공개 멤버에 대한 단위 테스트 어려움, 공개/비공개 전환 시 각각 수정 필요 |

### 3.1 객체 리터럴 기반

```typescript
interface ModuleConfig {
  useCaching: boolean;
  language: string;
}

interface MyModule {
  myProperty: string;
  myConfig: ModuleConfig;
  saySomething(): void;
  reportMyConfig(): void;
  updateMyConfig(newConfig: ModuleConfig): void;
}

const myModule: MyModule = {
  myProperty: "someValue",

  myConfig: {
    useCaching: true,
    language: "en",
  },

  saySomething() {
    console.log("Where is Paul Irish debugging today?");
  },

  reportMyConfig() {
    console.log(
      `Caching is: ${this.myConfig.useCaching ? "enabled" : "disabled"}`,
    );
  },

  updateMyConfig(newConfig: ModuleConfig) {
    this.myConfig = newConfig;
    console.log(this.myConfig.language);
  },
};
```

### 3.2 ES Modules를 활용한 모듈 패턴

ES Modules에서 파일 스코프에 정의된 변수는 `export`하지 않으면 외부에서 접근할 수 없다. TypeScript는 여기에 타입 정보를 추가하여 더 안전한 모듈 인터페이스를 제공한다.

```typescript
// counterModule.ts
let counter = 0; // 비공개 — 외부에서 접근 불가

export const testModule = {
  incrementCounter(): number {
    return counter++;
  },

  resetCounter(): void {
    console.log(`counter value prior to reset: ${counter}`);
    counter = 0;
  },
} as const;
```

```typescript
// main.ts
import { testModule } from "./counterModule";

testModule.incrementCounter();
testModule.resetCounter(); // "counter value prior to reset: 1"

// counter 변수에 직접 접근 불가 — 모듈 스코프 내부에서 보호
```

### 3.3 장바구니 예제 — 실용적 모듈 패턴

```typescript
// basketModule.ts
interface BasketItem {
  item: string;
  price: number;
}

const basket: BasketItem[] = []; // 비공개

export const basketModule = {
  addItem(values: BasketItem): void {
    basket.push(values);
  },

  getItemCount(): number {
    return basket.length;
  },

  getTotal(): number {
    return basket.reduce(
      (currentSum, item) => item.price + currentSum,
      0,
    );
  },
};
```

```typescript
// 사용
import { basketModule } from "./basketModule";

basketModule.addItem({ item: "bread", price: 0.5 });
basketModule.addItem({ item: "butter", price: 0.3 });

console.log(basketModule.getItemCount()); // 2
console.log(basketModule.getTotal());     // 0.8
// (basketModule as any).basket → 타입 에러! 비공개 접근 불가
```

### 3.4 클래스 기반 모듈 패턴 — `#private` 필드

ES2022의 `#private` 필드를 TypeScript와 함께 사용하면 **런타임에서도 진정한 비공개**가 보장된다:

```typescript
class CounterModule {
  #counter = 0;

  incrementCounter(): number {
    return ++this.#counter;
  }

  resetCounter(): void {
    console.log(`counter value prior to reset: ${this.#counter}`);
    this.#counter = 0;
  }
}

const testModule = new CounterModule();
testModule.incrementCounter();
testModule.resetCounter(); // "counter value prior to reset: 1"

// testModule.#counter; // SyntaxError: 런타임에서도 접근 불가
```

### 전통 vs 현대

```typescript
// 전통: IIFE + 클로저 (TypeScript에서는 거의 사용하지 않음)
const myModule = (() => {
  let privateVar = 0;
  return {
    increment(): number { return ++privateVar; },
    getCount(): number { return privateVar; },
  };
})();

// 현대: ES Modules (파일 자체가 모듈 스코프)
// counterModule.ts
let privateVar = 0;
export const increment = (): number => ++privateVar;
export const getCount = (): number => privateVar;

// 최신: TypeScript + #private 필드 (런타임 비공개 보장)
class CounterModule {
  #counter = 0;

  increment(): number { return ++this.#counter; }
  getCount(): number { return this.#counter; }
}
```

> **핵심 통찰**: TypeScript에서는 세 가지 수준의 비공개가 있다: (1) ES Modules 스코프 (파일 내부 변수), (2) TypeScript `private` (컴파일 타임 체크), (3) `#private` (런타임 비공개). 실무에서는 TypeScript `private`만으로 충분한 경우가 많지만, 라이브러리 개발 시에는 `#private`을 사용하는 것이 안전하다.

---

## 4. 노출 모듈 패턴 (Revealing Module Pattern)

크리스티안 하일만(*Christian Heilmann*)이 고안한 노출 모듈 패턴은 모듈 패턴의 개선 버전이다. 모든 함수와 변수를 비공개 스코프에 정의하고, **공개하고 싶은 부분만 포인터를 통해 노출하는 객체를 반환**한다.

### 패턴 카드: Revealing Module

| 항목 | 설명 |
|------|------|
| **의도** | 모듈의 공개 API를 한눈에 파악할 수 있게 한다 |
| **사용 시점** | 공개 인터페이스를 명확히 정의하고 싶을 때 |
| **미사용 시점** | 공개 함수를 외부에서 재정의해야 할 때 (패치 불가능) |
| **장점** | 코드 일관성, 모듈 하단에서 공개 API를 한눈에 파악 |
| **단점** | 비공개 함수 참조가 고정되어 수정 불가 |

```typescript
// revealingModule.ts
let privateVar = "Rob Dodson";
const publicVar = "Hey there!";

const privateFunction = (): void => {
  console.log(`Name: ${privateVar}`);
};

const publicSetName = (strName: string): void => {
  privateVar = strName;
};

const publicGetName = (): void => {
  privateFunction();
};

// 비공개 함수와 속성에 접근하는 공개 포인터
export const myRevealingModule = {
  setName: publicSetName,
  greeting: publicVar,
  getName: publicGetName,
} as const;
```

```typescript
import { myRevealingModule } from "./revealingModule";

myRevealingModule.setName("Matt Gaunt");
myRevealingModule.getName(); // "Name: Matt Gaunt"
```

**TypeScript에서의 노출 모듈 패턴**: ES Modules의 named export가 본질적으로 노출 모듈 패턴과 동일한 역할을 한다. 파일 스코프의 비공개 구현과 `export`된 공개 API가 명확히 구분되기 때문이다.

> **Osmani의 조언**: 노출 모듈 패턴으로 만들어진 모듈은 기존 모듈 패턴보다 취약할 수 있으므로 사용에 주의해야 한다. TypeScript + ES Modules 환경에서는 named export를 활용하면 노출 모듈 패턴의 장점을 자연스럽게 얻을 수 있다.

---

## 5. 싱글톤 패턴 (Singleton Pattern)

싱글톤(*Singleton*)은 클래스의 인스턴스(*instance — 클래스를 기반으로 생성된 실제 객체*)가 **오직 하나만 존재하도록 제한**하는 패턴이다. 전역에서 접근 및 공유해야 하는 단 하나의 객체가 필요할 때 유용하다.

### 패턴 카드: Singleton

| 항목 | 설명 |
|------|------|
| **의도** | 클래스의 인스턴스를 하나만 생성하고 전역 접근점을 제공한다 |
| **사용 시점** | 전역 설정, 캐시, 로깅 등 단일 인스턴스가 필요할 때 |
| **미사용 시점** | 테스트가 중요한 코드, 여러 인스턴스가 필요할 수 있는 경우 |
| **장점** | 전역 접근, 지연 초기화 가능, 리소스 절약 |
| **단점** | 테스트 어려움, 숨겨진 의존성, 전역 상태 문제 |

### 5.1 싱글톤 구현 — JS vs TS 비교

```javascript
// JavaScript — 런타임에서만 단일 인스턴스 보장
let instance;

class MySingleton {
  constructor() {
    if (instance) return instance; // 런타임 검사로 방어
    this.publicProperty = "I am public";
    this.#randomNumber = Math.random();
    instance = this;
  }

  #randomNumber;

  getRandomNumber() {
    return this.#randomNumber;
  }
}

// new를 여러 번 호출해도 같은 인스턴스를 반환하지만,
// 개발자가 이 클래스가 싱글톤인지 코드를 읽기 전까지는 알 수 없다.
```

```typescript
// TypeScript — private constructor로 컴파일 타임에 new 차단
class MySingleton {
  static #instance: MySingleton | null = null;

  readonly publicProperty = "I am public";
  #randomNumber: number;

  private constructor() { // ← private으로 외부 new 원천 차단
    this.#randomNumber = Math.random();
  }

  static getInstance(): MySingleton {
    if (!MySingleton.#instance) {
      MySingleton.#instance = new MySingleton();
    }
    return MySingleton.#instance;
  }

  getRandomNumber(): number {
    return this.#randomNumber;
  }
}

// new MySingleton();
// ^^^^^^^^^^^^^ Error: Constructor of class 'MySingleton' is private

const singleA = MySingleton.getInstance();
const singleB = MySingleton.getInstance();
console.log(singleA === singleB); // true
```

TypeScript의 `private constructor`는 싱글톤의 핵심 제약("외부에서 인스턴스 생성 불가")을 **컴파일 타임에 강제**한다. JavaScript에서는 런타임 검사(`if (instance) return instance`)로만 방어할 수 있어, 코드를 읽기 전까지는 해당 클래스가 싱글톤인지 알기 어렵다.

### 5.2 제네릭 싱글톤 — 지연 초기화

```typescript
interface SingletonOptions {
  pointX?: number;
  pointY?: number;
}

class Singleton {
  readonly name = "SingletonTester";
  readonly pointX: number;
  readonly pointY: number;

  private constructor(options: SingletonOptions = {}) {
    this.pointX = options.pointX ?? 6;
    this.pointY = options.pointY ?? 10;
  }

  private static instance: Singleton | undefined;

  static getInstance(options?: SingletonOptions): Singleton {
    if (!Singleton.instance) {
      Singleton.instance = new Singleton(options);
    }
    return Singleton.instance;
  }

  // 테스트 환경에서 싱글톤 리셋을 허용 (선택사항)
  static resetInstance(): void {
    Singleton.instance = undefined;
  }
}

const test = Singleton.getInstance({ pointX: 5 });
console.log(test.pointX); // 5
```

### 5.3 자바스크립트에서 싱글톤의 함정

GoF는 싱글톤의 적합성을 다음과 같이 정의했다:
- 클래스의 인스턴스는 정확히 하나만 있어야 하며, 접근이 용이해야 한다
- 싱글톤의 인스턴스는 서브클래싱을 통해 확장할 수 있어야 한다

그러나 자바스크립트/TypeScript에서 싱글톤에는 여러 단점이 있다:

| 단점 | 설명 |
|------|------|
| **파악 어려움** | 큰 모듈을 가져올 때 어떤 클래스가 싱글톤인지 알아내기 어렵다 |
| **테스트 어려움** | 숨겨진 의존성, 여러 인스턴스 생성 불가, 의존성 대체 곤란 |
| **조정 필요** | 데이터 유효성 이후에만 사용 가능하도록 올바른 실행 순서 구현이 필수적이다 |

> **핵심 통찰**: 자바스크립트는 객체를 직접 생성할 수 있으므로, 싱글톤 클래스 대신 **ES 모듈의 export**를 활용하면 자연스러운 싱글톤이 된다. ES 모듈은 한 번만 평가(evaluate)되므로, 모듈 스코프의 변수는 본질적으로 싱글톤이다.

### 전통 vs 현대

```typescript
// 전통: 클래스 기반 싱글톤
class LegacySingleton {
  private static instance: LegacySingleton;
  private constructor() {}
  static getInstance(): LegacySingleton {
    if (!LegacySingleton.instance) {
      LegacySingleton.instance = new LegacySingleton();
    }
    return LegacySingleton.instance;
  }
}

// 현대: ES 모듈 자체가 싱글톤 (권장)
// config.ts
interface AppConfig {
  apiUrl: string;
  timeout: number;
}

const config: AppConfig = {
  apiUrl: "https://api.example.com",
  timeout: 5000,
};

export default config;
// → 어디서 import하든 같은 객체 참조

// 최신: 리액트에서는 Zustand / Jotai 사용
import { create } from "zustand";

interface CounterStore {
  count: number;
  increment: () => void;
}

const useStore = create<CounterStore>((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
}));
```

### 5.4 리액트의 상태 관리와 싱글톤

리액트에서는 싱글톤 대신 **Context API**나 **전역 상태 관리 도구**(Redux, Zustand, Jotai)를 사용한다. 이들은 싱글톤과 달리 **변경 불가능한 읽기 전용 상태**를 제공하며, 컴포넌트가 전역 상태를 직접 변경하는 것을 방지한다.

---

## 6. 프로토타입 패턴 (Prototype Pattern)

GoF는 프로토타입(*Prototype*) 패턴을 **이미 존재하는 객체를 복제해 만든 템플릿을 기반으로 새 객체를 생성하는 패턴**이라고 정의했다. 자바스크립트는 프로토타입 기반 언어이므로, 이 패턴은 자바스크립트의 **고유한 방식으로 작업할 수 있다**는 장점이 있다.

### 패턴 카드: Prototype

| 항목 | 설명 |
|------|------|
| **의도** | 기존 객체를 복제하여 새 객체를 생성한다 |
| **사용 시점** | 비용이 큰 객체 생성을 피하고 기존 객체를 템플릿으로 사용하고 싶을 때 |
| **미사용 시점** | 매번 완전히 다른 초기화가 필요한 경우 |
| **장점** | 프로토타입 상속으로 메서드 공유, 성능 이점 |
| **단점** | 프로토타입 체인의 속성 열거 시 주의 필요 |

### 6.1 인터페이스 기반 Cloneable 패턴

TypeScript에서는 `Cloneable` 인터페이스를 정의하여 프로토타입 패턴을 타입 안전하게 구현할 수 있다:

```typescript
interface Cloneable<T> {
  clone(): T;
}

class Vehicle implements Cloneable<Vehicle> {
  constructor(
    public readonly model: string,
    public readonly year: number,
    private _mileage: number = 0,
  ) {}

  get mileage(): number {
    return this._mileage;
  }

  drive(distance: number): void {
    this._mileage += distance;
  }

  getInfo(): string {
    return `${this.model} (${this.year}) — ${this._mileage} miles`;
  }

  clone(): Vehicle {
    return new Vehicle(this.model, this.year, this._mileage);
  }
}

const car = new Vehicle("Ford Escort", 2020, 5000);
const car2 = car.clone();

car2.drive(100);
console.log(car.getInfo());  // "Ford Escort (2020) — 5000 miles"
console.log(car2.getInfo()); // "Ford Escort (2020) — 5100 miles" (독립적)
```

### 6.2 structuredClone을 활용한 깊은 복사

```typescript
interface AppState {
  user: { name: string; preferences: { theme: string; lang: string } };
  items: Array<{ id: number; label: string }>;
}

const originalState: AppState = {
  user: { name: "Alice", preferences: { theme: "dark", lang: "ko" } },
  items: [{ id: 1, label: "Item 1" }],
};

// ES2022 structuredClone — 깊은 복사
const clonedState = structuredClone(originalState);
clonedState.user.preferences.theme = "light";

console.log(originalState.user.preferences.theme); // "dark" (원본 유지)
console.log(clonedState.user.preferences.theme);   // "light"
```

### 전통 vs 현대

```typescript
// 전통: Object.create + 프로토타입 체인
const proto = {
  greet(this: { name: string }): string {
    return `Hello, ${this.name}`;
  },
};
const obj = Object.create(proto) as typeof proto & { name: string };
obj.name = "World";

// 현대: 클래스 + Cloneable 인터페이스
class ConfigTemplate implements Cloneable<ConfigTemplate> {
  constructor(
    public readonly apiUrl: string,
    public timeout: number,
    public retryCount: number,
  ) {}

  clone(): ConfigTemplate {
    return new ConfigTemplate(this.apiUrl, this.timeout, this.retryCount);
  }
}

// 현대: structuredClone (데이터 전용 깊은 복사, 메서드 제외)
const original = { nested: { value: 42 }, date: new Date() };
const clone = structuredClone(original);
```

> **핵심 통찰**: TypeScript에서 프로토타입 패턴은 `Cloneable<T>` 인터페이스로 타입 안전하게 구현한다. 데이터만 복사할 때는 `structuredClone()`을, 메서드까지 포함한 완전한 복제가 필요할 때는 `clone()` 메서드를 구현한다.

---

## 7. 팩토리 패턴 (Factory Pattern)

팩토리(*Factory*) 패턴은 **생성자를 직접 호출하지 않고 객체를 생성하는 인터페이스를 제공**하는 패턴이다. `new` 연산자 대신 팩토리 객체에 어떤 타입의 객체가 필요한지 알려주면, 적절한 인스턴스를 생성하여 반환한다.

### 패턴 카드: Factory

| 항목 | 설명 |
|------|------|
| **의도** | 객체 생성 로직을 캡슐화하고 호출부와 분리한다 |
| **사용 시점** | 생성 과정이 복잡하거나, 타입에 따라 다른 객체를 생성해야 할 때 |
| **미사용 시점** | 생성이 단순하여 추가 추상화가 오히려 복잡성을 높일 때 |
| **장점** | 생성 로직 중앙화, Open-Closed 원칙 준수, 디커플링 |
| **단점** | 간단한 경우 불필요한 복잡성 추가, 테스트 복잡도 증가 가능 |

### 7.1 팩토리 구현 — JS vs TS 비교

```javascript
// JavaScript — 반환 타입을 알 수 없고, 잘못된 vehicleType도 런타임까지 잡히지 않음
class VehicleFactory {
  createVehicle(options) {
    const { vehicleType, ...rest } = options;
    switch (vehicleType) {
      case "car":    return new Car(rest);
      case "truck":  return new Truck(rest);
      default:       return new Car(rest); // 기본값 — 실수해도 모름
    }
  }
}

const factory = new VehicleFactory();
const v = factory.createVehicle({ vehicleType: "car", color: "yellow" });
// v의 타입? → 알 수 없음. v.doors가 있는지도 IDE가 모름.
```

TypeScript의 **판별 유니언**(*Discriminated Union*) + **함수 오버로드**를 사용하면 팩토리의 반환 타입이 입력에 따라 **자동으로 좁혀진다**:

```typescript
// TypeScript — 입력 타입에 따라 반환 타입이 자동 결정
interface CarOptions {
  vehicleType: "car";
  doors?: number;
  state?: string;
  color?: string;
}

interface TruckOptions {
  vehicleType: "truck";
  state?: string;
  wheelSize?: string;
  color?: string;
}

type VehicleOptions = CarOptions | TruckOptions;

class Car {
  readonly doors: number;
  readonly state: string;
  readonly color: string;

  constructor({ doors = 4, state = "brand new", color = "silver" }: Omit<CarOptions, "vehicleType"> = {}) {
    this.doors = doors;
    this.state = state;
    this.color = color;
  }
}

class Truck {
  readonly state: string;
  readonly wheelSize: string;
  readonly color: string;

  constructor({ state = "used", wheelSize = "large", color = "blue" }: Omit<TruckOptions, "vehicleType"> = {}) {
    this.state = state;
    this.wheelSize = wheelSize;
    this.color = color;
  }
}

// 함수 오버로드 — 입력에 따라 반환 타입이 달라짐
function createVehicle(options: CarOptions): Car;
function createVehicle(options: TruckOptions): Truck;
function createVehicle(options: VehicleOptions): Car | Truck {
  switch (options.vehicleType) {
    case "car": {
      const { vehicleType, ...rest } = options;
      return new Car(rest);
    }
    case "truck": {
      const { vehicleType, ...rest } = options;
      return new Truck(rest);
    }
  }
}

const car = createVehicle({ vehicleType: "car", color: "yellow", doors: 6 });
//    ^? const car: Car — 자동 추론!

const truck = createVehicle({ vehicleType: "truck", wheelSize: "small" });
//    ^? const truck: Truck — 자동 추론!

// createVehicle({ vehicleType: "boat" });
// ^^^^^^^^^^^^^^^^^^^^^^^^ Error: '"boat"'은 할당할 수 없습니다.
```

JavaScript 팩토리에서는 반환값의 타입을 알 수 없어 `car.doors`에 접근해도 IDE 지원이 없다. TypeScript에서는 `vehicleType: "car"`를 넘기는 순간 반환 타입이 `Car`로 좁혀져, 해당 타입의 프로퍼티에 자동완성과 타입 체크가 적용된다.

### 7.2 Map 기반 레지스트리 팩토리

```typescript
interface Vehicle {
  describe(): string;
}

type VehicleConstructor = new (options: Record<string, unknown>) => Vehicle;

class VehicleFactory {
  #registry = new Map<string, VehicleConstructor>();

  register(type: string, VehicleClass: VehicleConstructor): this {
    this.#registry.set(type, VehicleClass);
    return this;
  }

  create(type: string, options: Record<string, unknown> = {}): Vehicle {
    const VehicleClass = this.#registry.get(type);
    if (!VehicleClass) {
      throw new Error(`Unknown vehicle type: ${type}`);
    }
    return new VehicleClass(options);
  }

  getRegisteredTypes(): string[] {
    return [...this.#registry.keys()];
  }
}

const factory = new VehicleFactory();
factory.register("car", Car).register("truck", Truck);

const car = factory.create("car", { color: "red" });
console.log(car.describe());
```

### 7.3 팩토리 패턴의 사용 가이드

**사용하면 좋은 상황**:
- 객체나 컴포넌트의 생성 과정이 높은 복잡성을 가지고 있을 때
- 상황에 맞춰 다양한 객체 인스턴스를 편리하게 생성해야 할 때
- 같은 인터페이스를 공유하는 여러 구현체를 다뤄야 할 때
- 디커플링(*decoupling — 호출부가 구체적인 클래스를 몰라도 되도록 분리*)이 필요한 경우

**사용하면 안 되는 상황**:
- 객체 생성이 단순한 경우 — 불필요한 복잡성이 추가된다
- 객체 생성 인터페이스 제공이 라이브러리 설계 목표가 아닌 경우

---

## 8. 추상 팩토리 패턴 (Abstract Factory Pattern)

추상 팩토리(*Abstract Factory*) 패턴은 **같은 목표를 가진 팩토리들을 하나의 그룹으로 캡슐화**하는 패턴이다. 객체가 어떻게 생성되는지에 대한 세부 사항을 알 필요 없이 객체를 사용할 수 있게 한다.

### 패턴 카드: Abstract Factory

| 항목 | 설명 |
|------|------|
| **의도** | 관련 객체들의 팩토리를 그룹화하여 일관된 생성 인터페이스를 제공한다 |
| **사용 시점** | 여러 타입의 관련 객체를 생성해야 하고, 생성 과정에 영향받지 않아야 할 때 |
| **미사용 시점** | 관련 객체 그룹이 하나뿐이거나 타입이 고정된 경우 |
| **장점** | 일관된 인터페이스, 구체적 생성 로직 은닉 |
| **단점** | 새로운 타입 추가 시 수정 범위 증가 |

```javascript
// JavaScript — 런타임에 프로토타입 메서드 존재 여부를 검사해야 함
class AbstractVehicleFactory {
  #types = {};

  registerVehicle(type, Vehicle) {
    const proto = Vehicle.prototype;
    // 인터페이스 충족 여부를 런타임에 수동 검증 — 실수하기 쉬움
    if (proto.drive && proto.breakDown) {
      this.#types[type] = Vehicle;
    }
    return this;
  }

  getVehicle(type, customizations = {}) {
    const Vehicle = this.#types[type];
    return Vehicle ? new Vehicle(customizations) : null;
  }
}
```

```typescript
// TypeScript — implements로 컴파일 타임에 인터페이스 충족을 강제
interface Vehicle {
  drive(): void;
  breakDown(): void;
}

interface VehicleCustomizations {
  color?: string;
  state?: string;
  [key: string]: unknown;
}

type VehicleClass = new (options: VehicleCustomizations) => Vehicle;

class AbstractVehicleFactory {
  #types = new Map<string, VehicleClass>();

  getVehicle(type: string, customizations: VehicleCustomizations = {}): Vehicle {
    const VehicleConstructor = this.#types.get(type);
    if (!VehicleConstructor) {
      throw new Error(`Vehicle type "${type}" is not registered`);
    }
    return new VehicleConstructor(customizations);
  }

  // VehicleClass 타입이 Vehicle 인터페이스 구현을 강제하므로
  // 런타임 proto 검사가 불필요
  registerVehicle(type: string, VehicleConstructor: VehicleClass): this {
    this.#types.set(type, VehicleConstructor);
    return this;
  }
}

// implements Vehicle이 없거나 메서드가 빠지면 컴파일 에러!
class SportsCar implements Vehicle {
  constructor(private options: VehicleCustomizations) {}
  drive(): void { console.log("Vroom! Fast driving!"); }
  breakDown(): void { console.log("Engine overheated..."); }
}

class ElectricTruck implements Vehicle {
  constructor(private options: VehicleCustomizations) {}
  drive(): void { console.log("Silent and powerful driving"); }
  breakDown(): void { console.log("Battery depleted..."); }
}

// 사용
const factory = new AbstractVehicleFactory();
factory
  .registerVehicle("sports", SportsCar)
  .registerVehicle("electric-truck", ElectricTruck);

const car = factory.getVehicle("sports", { color: "lime green" });
car.drive(); // "Vroom! Fast driving!"
```

> **핵심 통찰**: JavaScript에서는 `proto.drive && proto.breakDown`으로 **런타임에** 인터페이스 충족 여부를 검사해야 했다. TypeScript에서는 `implements Vehicle`과 `VehicleClass` 타입이 **컴파일 타임에** 이를 보장하므로, 런타임 검증 코드가 사라진다. 이것이 TypeScript와 디자인 패턴의 시너지다.

---

## 9. 빌더 패턴 (Builder Pattern)

원서에서는 빌더 패턴을 간략히 언급하지만, GoF 분류에서 중요한 생성 패턴이므로 보충한다. 빌더(*Builder*) 패턴은 **객체 생성과 표현을 분리하여 동일한 생성 과정에서 서로 다른 표현을 만들 수 있게** 한다.

### 패턴 카드: Builder

| 항목 | 설명 |
|------|------|
| **의도** | 복잡한 객체를 단계적으로 구성하되, 생성 과정과 표현을 분리한다 |
| **사용 시점** | 생성자에 많은 매개변수가 필요하거나 선택적 속성이 많을 때 |
| **미사용 시점** | 객체 생성이 단순하여 단계적 구성이 불필요한 경우 |
| **장점** | 가독성, 선택적 매개변수 처리, 불변 객체 생성에 유리 |
| **단점** | 코드 양 증가, 단순 객체에는 과도한 추상화 |

### TypeScript 빌더 — 타입 안전한 메서드 체이닝

```typescript
class QueryBuilder {
  #table = "";
  #conditions: string[] = [];
  #orderBy = "";
  #limit = 0;

  from(table: string): this {
    this.#table = table;
    return this;
  }

  where(condition: string): this {
    this.#conditions.push(condition);
    return this;
  }

  orderBy(column: string): this {
    this.#orderBy = column;
    return this;
  }

  limit(n: number): this {
    this.#limit = n;
    return this;
  }

  build(): string {
    let query = `SELECT * FROM ${this.#table}`;
    if (this.#conditions.length) {
      query += ` WHERE ${this.#conditions.join(" AND ")}`;
    }
    if (this.#orderBy) query += ` ORDER BY ${this.#orderBy}`;
    if (this.#limit) query += ` LIMIT ${this.#limit}`;
    return query;
  }
}

const query = new QueryBuilder()
  .from("users")
  .where("age > 18")
  .where("active = true")
  .orderBy("name")
  .limit(10)
  .build();

// "SELECT * FROM users WHERE age > 18 AND active = true ORDER BY name LIMIT 10"
```

### 옵션 객체 패턴 — TypeScript에서 빌더의 대안

TypeScript에서는 인터페이스의 선택적 속성(`?`)과 `Readonly`, `Partial` 유틸리티 타입이 빌더 패턴의 많은 사용 사례를 대체한다:

```typescript
interface UserOptions {
  name: string;
  email: string;
  age: number;
  role?: "user" | "admin" | "moderator";
  active?: boolean;
}

type User = Readonly<Required<UserOptions>>;

function createUser(options: UserOptions): User {
  return Object.freeze({
    role: "user",
    active: true,
    ...options,
  }) as User;
}

const user = createUser({ name: "Alice", email: "a@b.com", age: 30 });
// user.role = "admin"; // Error: Cannot assign to 'role' because it is a read-only property
```

> **핵심 통찰**: TypeScript에서는 **인터페이스의 선택적 속성 + `Partial<T>` / `Required<T>` 유틸리티 타입**이 빌더 패턴의 많은 사용 사례를 대체한다. 그러나 쿼리 빌더, HTTP 클라이언트 설정 등 **단계적 구성이 가독성을 높이는 경우**에는 여전히 빌더 패턴이 유용하다.

---

## 최신 업데이트 (2026)

### ES2022+ 비공개 필드 (#private) + TypeScript

TypeScript의 `private`과 ES2022 `#private`의 차이:

```typescript
class Example {
  private tsPrivate = "compile-time only"; // TypeScript private
  #jsPrivate = "runtime enforced";         // ES2022 #private

  // TypeScript private: 컴파일 에러지만, JS로 변환 후에는 접근 가능
  // #private: JS 런타임에서도 접근 불가 (SyntaxError)
}

// 실무 권장: 일반 앱은 TypeScript private, 라이브러리는 #private
```

### Explicit Resource Management (`using`)

ES2024에 도입된 `using` 키워드 — TypeScript 5.2+에서 지원:

```typescript
class DatabaseConnection implements Disposable {
  #connection: Connection;

  constructor(url: string) {
    this.#connection = connect(url);
  }

  query(sql: string): ResultSet {
    return this.#connection.execute(sql);
  }

  [Symbol.dispose](): void {
    this.#connection.close();
    console.log("Connection closed");
  }
}

// using 키워드로 스코프 종료 시 자동 정리
function fetchUsers(): User[] {
  using db = new DatabaseConnection("postgres://localhost/mydb");
  return db.query("SELECT * FROM users");
} // 함수 종료 시 자동으로 db[Symbol.dispose]() 호출
```

### Proxy 기반 팩토리

```typescript
interface VehicleMap {
  car: Car;
  truck: Truck;
}

type VehicleFactory = {
  [K in keyof VehicleMap]: (options?: Record<string, unknown>) => VehicleMap[K];
};

const vehicleFactory = new Proxy({} as VehicleFactory, {
  get(_target, type: string) {
    const classes: Record<string, new (opts: any) => Vehicle> = {
      car: Car,
      truck: Truck,
    };

    return (options: Record<string, unknown> = {}) => {
      const VehicleClass = classes[type];
      if (!VehicleClass) throw new Error(`Unknown: ${type}`);
      return new VehicleClass(options);
    };
  },
});

const car = vehicleFactory.car({ color: "red" });
const truck = vehicleFactory.truck({ wheelSize: "large" });
```

---

## 실무 적용 가이드

### 패턴 선택 체크리스트

| 상황 | 권장 패턴 |
|------|-----------|
| 동일 구조의 객체를 여러 개 생성 | **생성자 패턴** (TypeScript 매개변수 프로퍼티) |
| 관련 기능을 캡슐화하고 비공개 보호 | **모듈 패턴** (ES Modules + `private`/`#private`) |
| 전역에서 하나의 인스턴스만 필요 | **싱글톤** (ES Module export 또는 `private constructor`) |
| 타입에 따라 다른 객체를 생성 | **팩토리 패턴** (판별 유니언 + 함수 오버로드) |
| 관련 팩토리들의 그룹 관리 | **추상 팩토리 패턴** (인터페이스 + Map 레지스트리) |
| 복잡한 객체의 단계적 구성 | **빌더 패턴** (또는 `Partial<T>` + 옵션 객체) |
| 기존 객체를 복제하여 새 객체 생성 | **프로토타입 패턴** (`Cloneable<T>` + `structuredClone`) |

### TypeScript가 디자인 패턴에 미치는 영향

| JavaScript 방식 | TypeScript 대안 |
|-----------------|-----------------|
| 런타임 인터페이스 검증 (`proto.method`) | `implements` 키워드 (컴파일 타임) |
| WeakMap으로 비공개 흉내 | `private` / `#private` |
| 팩토리 switch 문 | 판별 유니언 + 함수 오버로드 |
| 빌더 패턴 (필수) | `Partial<T>` + `Required<T>` (선택적 대안) |
| 프로토타입 체인 검증 | 제네릭 `Cloneable<T>` 인터페이스 |
| JSDoc 타입 힌트 | 타입 시스템 내장 |

---

## 요약

- **생성자 패턴**: TypeScript 매개변수 프로퍼티로 간결하게 구현. `readonly`/`private`으로 캡슐화 강제
- **모듈 패턴**: ES Modules + TypeScript `private` / `#private`으로 3단계 비공개 수준 제공
- **노출 모듈 패턴**: TypeScript ES Modules의 named export가 자연스러운 대체제
- **싱글톤 패턴**: `private constructor` + `static getInstance()`가 TypeScript 표준 구현. ES Module export가 더 간단한 대안
- **프로토타입 패턴**: `Cloneable<T>` 인터페이스로 타입 안전한 복제. `structuredClone()`은 데이터 전용
- **팩토리 패턴**: 판별 유니언 + 함수 오버로드로 타입이 자동 좁혀지는 팩토리 구현 가능
- **추상 팩토리 패턴**: `implements` 키워드가 런타임 인터페이스 검증을 컴파일 타임으로 대체
- **빌더 패턴**: `Partial<T>`/`Required<T>` 유틸리티 타입이 일부 대체하지만, 체이닝 빌더는 여전히 유용

---

## 다른 챕터와의 관계

- **← Ch05 (최신 JS 문법)**: 클래스, 모듈, `#private` 필드 등 생성 패턴의 기반 문법을 다룬다
- **← Ch06 (패턴 카테고리)**: 생성/구조/행위 분류 체계와 GoF 패턴 분류표를 제공한다
- **→ Ch08 (구조 패턴)**: 생성된 객체들을 조합하고 구성하는 패턴(Facade, Decorator, Flyweight 등)으로 이어진다
- **→ Ch09 (행위 패턴)**: 객체 간 커뮤니케이션과 책임 분배 패턴(Observer, Mediator, Command 등)으로 이어진다
- **→ Ch14 (리액트 디자인 패턴)**: 싱글톤의 리액트 대안(Context API, Zustand), 팩토리의 컴포넌트 적용 등을 다룬다
