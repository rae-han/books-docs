# Chapter 04: The Factory Pattern (팩토리 패턴)

## 핵심 질문

- `new`로 구상 클래스의 인스턴스를 만들면 왜 유연성이 떨어지는가? 무엇이 진짜 문제인가?
- 객체 생성 코드를 어떻게 캡슐화해서 클라이언트와 구상 클래스를 분리할까?
- **팩토리 메서드 패턴**과 **추상 팩토리 패턴**은 무엇이 다른가?
- "추상화된 것에 의존하라"는 DIP는 "인터페이스에 맞춰 프로그래밍하라"와 무엇이 다른가?

> **참고**: 이 장은 세 가지 "팩토리"를 다룬다 — **간단한 팩토리**(관용구), **팩토리 메서드 패턴**, **추상 팩토리 패턴**. 셋을 헷갈리기 쉬우니 각각의 차이에 주목하자.

---

## 1. `new`의 무엇이 문제인가

`new`는 죄가 없다. 진짜 말썽꾼은 **변화**다.

```typescript
// 구상 클래스에 의존하는 코드 — 변화에 취약하다
let duck: Duck;
if (picnic) {
  duck = new MallardDuck();
} else if (hunting) {
  duck = new DecoyDuck();
} else if (inBathTub) {
  duck = new RubberDuck();
}
```

구상 클래스를 많이 쓰면, 새 구상 클래스가 추가될 때마다 이 코드를 고쳐야 한다 → **변경에 닫혀 있지 않다**(OCP 위반).

> **핵심 통찰**: 인터페이스(상위 형식)에 맞춰 코딩하면 다형성 덕분에 어떤 변화에도 대응할 수 있다. 반면 구상 클래스에 맞춰 코딩하면 변화에 취약하다. 그러니 **바뀌는 부분(=구상 인스턴스를 만드는 코드)을 찾아내 캡슐화**해야 한다.

---

## 2. 간단한 팩토리 (Simple Factory)

피자 가게의 `orderPizza()`에서 문제가 되는 부분은 **어떤 구상 피자를 만들지 고르는 부분**이다. 이 부분만 뽑아 **팩토리** 클래스에 넣는다.

```typescript
type PizzaType = "cheese" | "pepperoni" | "clam" | "veggie";

class SimplePizzaFactory {
  createPizza(type: PizzaType): Pizza {
    switch (type) {
      case "cheese": return new CheesePizza();
      case "pepperoni": return new PepperoniPizza();
      case "clam": return new ClamPizza();
      case "veggie": return new VeggiePizza();
    }
  }
}

class PizzaStore {
  constructor(private factory: SimplePizzaFactory) {}

  orderPizza(type: PizzaType): Pizza {
    const pizza = this.factory.createPizza(type); // new 대신 팩토리 사용
    pizza.prepare();
    pizza.bake();
    pizza.cut();
    pizza.box();
    return pizza;
  }
}
```

<details>
<summary>Java 원본</summary>

```java
public class SimplePizzaFactory {
    public Pizza createPizza(String type) {
        Pizza pizza = null;
        if (type.equals("cheese")) {
            pizza = new CheesePizza();
        } else if (type.equals("pepperoni")) {
            pizza = new PepperoniPizza();
        } else if (type.equals("clam")) {
            pizza = new ClamPizza();
        } else if (type.equals("veggie")) {
            pizza = new VeggiePizza();
        }
        return pizza;
    }
}

public class PizzaStore {
    SimplePizzaFactory factory;
    public PizzaStore(SimplePizzaFactory factory) {
        this.factory = factory;
    }
    public Pizza orderPizza(String type) {
        Pizza pizza = factory.createPizza(type);
        pizza.prepare();
        pizza.bake();
        pizza.cut();
        pizza.box();
        return pizza;
    }
}
```
</details>

> **핵심 통찰**: 간단한 팩토리는 **엄밀히 말해 디자인 패턴이 아니라 관용구(idiom)** 다. 하지만 객체 생성을 한곳에 모아, 여러 클라이언트가 재사용하고 변경 지점을 하나로 만든다는 이점이 있다. (`'팩토리 패턴'`이라 부르는 사람을 만나면 "정확히는 패턴이 아니야"라고 귀띔해 주자.)

> TypeScript에서는 `type` 매개변수를 `string` 대신 **유니언 타입/enum**으로 두면, 오타(`"calm"`)를 **컴파일 시점에** 잡을 수 있다(원서 Q&A가 지적한 타입 안전성 문제를 TS가 언어 차원에서 해결).

---

## 3. 팩토리 메서드 패턴 (Factory Method)

지점(뉴욕·시카고)마다 스타일이 다른 피자를 만들되, **주문 절차(준비·굽기·자르기·포장)는 모든 지점이 동일**하게 따르게 하고 싶다. 해법: `createPizza()`를 `PizzaStore`의 **추상 메서드**로 두고, 지점별 서브클래스가 구현한다.

```typescript
/** 피자 가게 — 팩토리 메서드 패턴의 추상 생산자(Creator). */
abstract class PizzaStore {
  // 주문 절차는 고정. 어떤 피자가 오는지는 알지 못한다.
  orderPizza(type: PizzaType): Pizza {
    const pizza = this.createPizza(type); // 팩토리 메서드 호출
    pizza.prepare();
    pizza.bake();
    pizza.cut();
    pizza.box();
    return pizza;
  }

  /** 팩토리 메서드 — 어떤 구상 피자를 만들지는 서브클래스가 결정한다. */
  protected abstract createPizza(type: PizzaType): Pizza;
}

class NYPizzaStore extends PizzaStore {
  protected createPizza(type: PizzaType): Pizza {
    switch (type) {
      case "cheese": return new NYStyleCheesePizza();
      case "veggie": return new NYStyleVeggiePizza();
      case "clam": return new NYStyleClamPizza();
      case "pepperoni": return new NYStylePepperoniPizza();
    }
  }
}
```

<details>
<summary>Java 원본</summary>

```java
public abstract class PizzaStore {
    public Pizza orderPizza(String type) {
        Pizza pizza = createPizza(type);
        pizza.prepare();
        pizza.bake();
        pizza.cut();
        pizza.box();
        return pizza;
    }
    protected abstract Pizza createPizza(String type); // 팩토리 메서드
}

public class NYPizzaStore extends PizzaStore {
    protected Pizza createPizza(String item) {
        if (item.equals("cheese")) {
            return new NYStyleCheesePizza();
        } else if (item.equals("veggie")) {
            return new NYStyleVeggiePizza();
        } // ...
        else return null;
    }
}
```
</details>

> **핵심 통찰**: `orderPizza()`는 추상 클래스에 정의되어 있어, **실제로 어떤 구상 피자가 만들어지는지 전혀 모른다.** "서브클래스가 결정한다"는 말은 실행 중 결정이 아니라, **어떤 서브클래스(`NYPizzaStore` vs `ChicagoPizzaStore`)를 선택했느냐에 따라 만들어지는 제품이 정해진다**는 뜻이다.

**생산자(Creator)와 제품(Product)은 병렬 클래스 계층**을 이룬다.

```
    생산자 계층                     제품 계층
   ┌───────────┐                  ┌──────────┐
   │ PizzaStore│                  │  Pizza   │  (추상)
   │ orderPizza()│                └──────────┘
   │ createPizza() «abstract»        △
   └───────────┘              ┌──────┴─────────┐
        △                 NYStyleCheesePizza  ChicagoStyleCheesePizza ...
  ┌─────┴────────┐
NYPizzaStore  ChicagoPizzaStore
 createPizza()   createPizza()
```

> **패턴 정의 — 팩토리 메서드 패턴 (Factory Method Pattern)**<br>객체를 생성할 때 필요한 인터페이스를 만들되, 어떤 클래스의 인스턴스를 만들지는 서브클래스에서 결정하게 한다. 팩토리 메서드 패턴을 사용하면 클래스 인스턴스를 만드는 일을 서브클래스에 맡길 수 있다.

---

## 4. DIP — 의존성 뒤집기 원칙 (디자인 원칙 6)

팩토리 없이 모든 피자를 직접 `new`하는 `PizzaStore`는 **모든 구상 피자 클래스에 의존**한다(뉴욕 4종 + 시카고 4종 = 8개, 캘리포니아 추가 시 12개). 이 의존을 뒤집는 원칙이 DIP다.

> **디자인 원칙 6 — DIP (Dependency Inversion Principle)**<br>추상화된 것에 의존하게 만들고, 구상 클래스에 의존하지 않게 만든다.

- **고수준 구성 요소**(`PizzaStore`): 다른 저수준 구성 요소에 의해 행동이 정의되는 것.
- **저수준 구성 요소**(각 피자): 실제 구현.

팩토리 메서드를 적용하면 **고수준(`PizzaStore`)과 저수준(구상 피자)이 모두 추상 클래스 `Pizza`에 의존**하게 된다. 원래 위→아래로만 흐르던 의존이 **뒤집혀**, 저수준도 추상화를 바라보게 된다.

> **핵심 통찰**: DIP는 "인터페이스에 맞춰 프로그래밍하라"(원칙 2)와 비슷하지만 **추상화를 더 강하게 강조**한다. 핵심은 "**고수준 모듈도, 저수준 모듈도 모두 추상화에 의존**해야 한다"는 것이다.

DIP를 지키기 위한 가이드라인(항상 지킬 규칙이 아니라 지향점):
1. 변수에 **구상 클래스의 레퍼런스를 저장하지 말라**(→ 팩토리 사용).
2. 구상 클래스에서 **유도된(파생) 클래스를 만들지 말라**(→ 추상 타입에서 파생).
3. 베이스 클래스에 이미 구현된 메서드를 **오버라이드하지 말라**(→ 공유 가능한 것만 베이스에 정의).

> `String`처럼 절대 바뀌지 않는 클래스는 `new`로 만들어도 문제없다. **바뀔 수 있는 클래스**에만 팩토리를 적용한다.

---

## 5. 추상 팩토리 패턴 (Abstract Factory)

새 문제: 지점들이 몰래 싸구려 **원재료**로 바꿔치기한다. 지역별로 정해진 **원재료군(family)**(반죽·소스·치즈·야채·고기)을 공급해야 한다. 지역마다 재료의 구체적 종류는 다르다(뉴욕=마리나라+레지아노+신선한 조개, 시카고=플럼토마토+모차렐라+냉동 조개).

원재료군 전체를 생산하는 **팩토리 인터페이스**를 만든다.

```typescript
/** 피자 원재료군을 생산하는 추상 팩토리. */
interface PizzaIngredientFactory {
  /** 반죽을 만든다. */
  createDough(): Dough;
  /** 소스를 만든다. */
  createSauce(): Sauce;
  /** 치즈를 만든다. */
  createCheese(): Cheese;
  /** 야채군을 만든다. */
  createVeggies(): Veggies[];
  /** 페퍼로니를 만든다. */
  createPepperoni(): Pepperoni;
  /** 조개를 만든다. */
  createClam(): Clams;
}

/** 뉴욕 지역 원재료 팩토리 — 뉴욕식 재료를 생산한다. */
class NYPizzaIngredientFactory implements PizzaIngredientFactory {
  createDough(): Dough {
    return new ThinCrustDough();
  }
  createSauce(): Sauce {
    return new MarinaraSauce();
  }
  createCheese(): Cheese {
    return new ReggianoCheese();
  }
  createVeggies(): Veggies[] {
    return [new Garlic(), new Onion(), new Mushroom(), new RedPepper()];
  }
  createPepperoni(): Pepperoni {
    return new SlicedPepperoni();
  }
  createClam(): Clams {
    return new FreshClams(); // 뉴욕은 바닷가 → 신선한 조개
  }
}
```

피자는 자신을 만들 **원재료 팩토리를 주입받아**, 재료가 필요할 때마다 팩토리에 요청한다.

```typescript
class CheesePizza extends Pizza {
  constructor(private ingredientFactory: PizzaIngredientFactory) {
    super();
  }

  prepare(): void {
    console.log(`준비 중: ${this.name}`);
    this.dough = this.ingredientFactory.createDough();   // 팩토리가 지역 재료 공급
    this.sauce = this.ingredientFactory.createSauce();
    this.cheese = this.ingredientFactory.createCheese();
  }
}
```

`NYPizzaStore`의 `createPizza()`는 뉴욕 원재료 팩토리를 만들어 피자에 넘긴다.

```typescript
class NYPizzaStore extends PizzaStore {
  protected createPizza(item: PizzaType): Pizza {
    const ingredientFactory = new NYPizzaIngredientFactory();
    let pizza: Pizza;
    switch (item) {
      case "cheese":
        pizza = new CheesePizza(ingredientFactory);
        pizza.setName("뉴욕 스타일 치즈 피자");
        break;
      // ...
    }
    return pizza;
  }
}
```

<details>
<summary>Java 원본 (NYPizzaIngredientFactory)</summary>

```java
public class NYPizzaIngredientFactory implements PizzaIngredientFactory {
    public Dough createDough() { return new ThinCrustDough(); }
    public Sauce createSauce() { return new MarinaraSauce(); }
    public Cheese createCheese() { return new ReggianoCheese(); }
    public Veggies[] createVeggies() {
        return new Veggies[] { new Garlic(), new Onion(), new Mushroom(), new RedPepper() };
    }
    public Pepperoni createPepperoni() { return new SlicedPepperoni(); }
    public Clams createClam() { return new FreshClams(); }
}
```
</details>

> **패턴 정의 — 추상 팩토리 패턴 (Abstract Factory Pattern)**<br>구상 클래스에 의존하지 않고, 서로 연관되거나 의존적인 객체로 이루어진 **제품군**을 생성하는 인터페이스를 제공한다. 구상 클래스는 서브클래스에서 만든다.

---

## 6. 팩토리 메서드 vs 추상 팩토리

> 패턴 집중 인터뷰 — 두 팩토리의 신경전<br><br>**팩토리 메서드**: 저는 **상속**으로 객체를 만들어요. 클래스를 확장하고 팩토리 메서드를 오버라이드하죠. 제품은 딱 하나만 만들면 되고요.<br>**추상 팩토리**: 저는 **구성(composition)** 으로 만들어요. 제품군 전체를 만드는 인터페이스를 제공하죠. 대신 제품군에 새 제품을 추가하려면 **인터페이스를 바꿔야** 하는 게 아프네요.<br>**팩토리 메서드**: <큭큭> 인터페이스를 바꾸면 모든 서브클래스를 고쳐야 하잖아요!<br>**추상 팩토리**: 대신 구상 팩토리를 구현할 때 종종 **당신(팩토리 메서드)** 을 쓰죠.

| 구분 | 팩토리 메서드 | 추상 팩토리 |
|------|--------------|-------------|
| 객체 생성 방식 | **상속** (서브클래스가 팩토리 메서드 오버라이드) | **구성** (팩토리 인스턴스를 주입받아 사용) |
| 만드는 것 | **한 종류**의 제품 | 서로 연관된 **제품군(family)** |
| 확장 시 | 서브클래스만 추가 | 제품 추가 시 **인터페이스 변경** 필요(단점) |
| 관계 | — | 구상 팩토리 내부를 **팩토리 메서드로 구현**하는 경우가 많다 |

> **핵심 통찰**: 두 패턴 모두 **객체 생성을 캡슐화**하여 클라이언트와 구상 클래스를 분리한다. 차이는 "**상속 vs 구성**"과 "**단일 제품 vs 제품군**"이다.

---

## 연습 문제 (해답 예시)

**1. 심하게 의존적인 `PizzaStore`의 구상 클래스 의존 개수** — 뉴욕 4종 + 시카고 4종 = **8개**. 캘리포니아 4종을 추가하면 **12개**로 늘어난다. 이것이 DIP가 해결하려는 문제다.

**2. `ChicagoPizzaStore`·`CaliforniaPizzaStore` 만들기** — `PizzaStore`를 확장하고 `createPizza()`에서 각각 시카고/캘리포니아 스타일 피자를 반환하면 된다. 주문 절차(`orderPizza()`)는 상속받아 그대로 쓴다.

**3. `ChicagoPizzaIngredientFactory` 만들기** — `PizzaIngredientFactory`를 구현하고, `createDough()`→`ThickCrustDough`, `createSauce()`→`PlumTomatoSauce`, `createCheese()`→`MozzarellaCheese`, `createClam()`→`FrozenClams`(내륙이라 냉동)를 반환한다.

**4. 팩토리 메서드가 추상 팩토리 안에 숨어 있나?** — 그렇다. 추상 팩토리의 각 메서드(`createDough()` 등)는 **팩토리 메서드로 구현되는 경우가 많다**. 두 패턴은 대립이 아니라 종종 함께 쓰인다.

---

## 디자인 원칙 정리 (누적)

1. 바뀌는 부분을 찾아내 캡슐화하고, 바뀌지 않는 부분과 분리한다.
2. 구현보다는 인터페이스(상위 형식)에 맞춰 프로그래밍한다.
3. 상속보다는 구성을 활용한다.
4. 상호작용하는 객체 사이에서는 가능하면 느슨한 결합을 사용한다.
5. 클래스는 확장에는 열려 있고 변경에는 닫혀 있어야 한다 (OCP).
6. **추상화된 것에 의존하게 만들고, 구상 클래스에 의존하지 않게 만든다 (DIP).** ← 이번 장

---

## 요약

- `new`로 구상 클래스를 직접 만들면 그 클래스에 의존하게 되어 변화에 취약하다. **객체 생성을 캡슐화**해야 한다.
- **간단한 팩토리**: 생성 코드를 한 클래스로 뽑아낸 관용구(패턴은 아님).
- **팩토리 메서드 패턴**: 생성을 **추상 메서드**로 두고 **서브클래스가 상속으로** 결정. 생산자·제품이 병렬 계층을 이룬다.
- **추상 팩토리 패턴**: 서로 연관된 **제품군**을 만드는 인터페이스를 제공하고, **구성**으로 팩토리를 주입한다.
- **DIP**: 고수준·저수준 모듈이 **모두 추상화에 의존**하게 하여, 의존 방향을 뒤집는다.
- 모든 팩토리 패턴은 구상 클래스 의존을 줄여 **느슨한 결합**을 돕는다.

---

## 다른 챕터와의 관계

- **1장 전략 · 3장 데코레이터**: 이 장의 팩토리는 데코레이터 조립처럼 "객체를 만드는 복잡함"을 캡슐화한다(3장에서 예고된 바로 그 패턴).
- **5장 싱글턴**: 팩토리 객체 자체를 싱글턴으로 두는 경우가 많다.
- **추상 팩토리 vs 빌더(14장)**: 둘 다 생성 패턴이지만, 빌더는 복잡한 객체를 **단계적으로** 조립한다.

---

## 보너스: 원서 복습 요소

### 🧠 뇌 단련 (Brain Power)

1. 애플리케이션에서 구상 클래스 인스턴스 생성 부분을 어떻게 전부 찾아 캡슐화할까? (→ 팩토리)
2. `PizzaStore`에서도 구성을 활용해 실행 중에 행동(만드는 피자 스타일)을 바꿀 수 있을까? (→ 다른 팩토리 주입)
3. 추상 팩토리(원재료)의 `createPizza()`와 팩토리 메서드 버전을 비교해 보라.

### 🧩 디자인 퍼즐 — 캘리포니아 지점

`PizzaStore`를 확장한 `CaliforniaPizzaStore`와, `Pizza`를 확장한 `CaliforniaStyle***Pizza` 4종을 추가하면 된다. (재미있는 토핑 예시: 구운 마늘 으깬 감자, 바베큐 소스, 미나리, 초콜릿, 땅콩 — 마음대로!)

### 🎤 패턴 집중 인터뷰 정리

- **팩토리 메서드** = 상속 기반, 단일 제품, 서브클래스가 결정.
- **추상 팩토리** = 구성 기반, 제품군, 제품 추가 시 인터페이스 변경이 단점.
- 둘은 자주 함께 쓰인다(추상 팩토리 내부가 팩토리 메서드).

### 📝 낱말 퀴즈 (정답 단어 모음)

4장 용어들(정답은 영어): CREATOR(생산자), CONCRETECREATOR(구상 생산자), CONCRETEFACTORY(구상 팩토리), FACTORYMETHOD(팩토리 메서드), SIMPLEFACTORY(간단한 팩토리), OBJECTCOMPOSITION(객체 구성), SUBCLASS(서브클래스), IMPLEMENTATION(구현), DEPENDENT(의존), ENCAPSULATE(캡슐화), FAMILY(군), PIZZA(피자), REGGIANO(레지아노), NYSTYLE(뉴욕 스타일), CHICAGOSTYLE(시카고 스타일).
