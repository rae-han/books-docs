# Chapter 01: Welcome to Design Patterns (디자인 패턴 소개와 전략 패턴)

## 핵심 질문

- 잘 돌아가던 코드가 왜 새 요구사항 하나에 무너질까? 상속만으로는 왜 변화에 유연하게 대응할 수 없을까?
- 애플리케이션에서 "바뀌는 부분"과 "바뀌지 않는 부분"을 어떻게 분리해야 할까?
- 전략 패턴(Strategy Pattern)은 무엇이며, 알고리즘군을 어떻게 캡슐화해서 실행 중에 교체할 수 있게 만드는가?
- 디자인 패턴은 결국 "좋은 객체지향 설계"와 무엇이 다른가?

---

## 1. SimUDuck — 잘 돌아가던 오리 시뮬레이터

조(Joe)는 `SimUDuck`이라는 오리 연못 시뮬레이션 게임을 만드는 회사에 다닌다. 게임에는 헤엄치고 꽥꽥거리는 다양한 오리가 등장한다. 최초 설계자는 표준 객체지향 기법대로 `Duck`이라는 슈퍼클래스를 만들고, 이를 상속해서 여러 종류의 오리를 만들었다.

```
              ┌───────────────────────┐
              │         Duck          │   ← 모든 오리가 공유하는 슈퍼클래스
              ├───────────────────────┤
              │ quack()               │   꽥꽥 소리 (공통 구현)
              │ swim()                │   헤엄 (공통 구현)
              │ display()  «abstract» │   모양은 오리마다 다름 → 추상 메서드
              └───────────────────────┘
                        △
            ┌───────────┴───────────┐
     ┌─────────────┐         ┌──────────────┐
     │ MallardDuck │         │ RedheadDuck  │  ← display()만 각자 구현
     │ display()   │         │ display()    │
     └─────────────┘         └──────────────┘
```

`display()`는 오리마다 모양이 다르므로 추상 메서드로 두고, 각 서브클래스가 구현한다. 여기까지는 상속을 교과서적으로 잘 활용한 설계처럼 보인다.

---

## 2. 재앙: 상속으로 `fly()` 추가하기

경쟁사의 압박에 시달리던 임원진은 "오리가 **날 수 있어야** 한다"고 결정한다. 조는 자신만만하게 생각한다.

> `Duck` 클래스에 `fly()` 메서드만 추가하면 모든 오리가 그걸 상속받겠지. 나의 천재적인 객체지향 능력을 보여 줄 때가 됐어.

그래서 슈퍼클래스에 `fly()`를 추가한다. 그런데 주주총회 데모에서 **화면 위로 고무 오리(RubberDuck)들이 날아다니는** 참사가 벌어진다.

문제의 원인은 명확하다. 슈퍼클래스에 `fly()`를 넣는 순간, **날면 안 되는 서브클래스(고무 오리)에까지 나는 기능이 상속**된 것이다.

> **핵심 통찰**: 코드 재사용을 목적으로 한 상속은, 슈퍼클래스의 한 번 변경이 **의도치 않게 모든 서브클래스로 전파**된다. "일부에만 적합한 행동"을 슈퍼클래스에 두면 그 행동이 부적합한 서브클래스까지 오염된다.

고무 오리의 `quack()`을 "삑삑"으로 오버라이드했던 것처럼, `fly()`도 "아무것도 안 하도록" 오버라이드하면 될까? 나무로 만든 가짜 오리(`DecoyDuck`)가 등장하면 `quack()`과 `fly()`를 **둘 다** 빈 메서드로 오버라이드해야 한다. 오리 종류가 늘 때마다 이 지겨운 오버라이드를 영원히 반복해야 한다.

---

## 3. 인터페이스로 갈아타기 — 이것도 실패

조는 상속이 답이 아님을 깨닫는다. 그래서 `fly()`를 슈퍼클래스에서 빼고, `Flyable`·`Quackable` 인터페이스로 옮긴다. 날 수 있는 오리만 `Flyable`을 구현하고, 꽥꽥거리는 오리만 `Quackable`을 구현하게 하는 것이다.

```
   Duck            «interface»        «interface»
 (추상)             Flyable            Quackable
                    fly()              quack()
     △                 △                  △
     │        ┌────────┴────┐      ┌───────┴──────┐
 MallardDuck ─┤ implements  │      │ implements   │
             Flyable, Quackable  ...  (오리마다 제각각)
```

이 방식은 "고무 오리가 날아다니는" 문제는 막아준다. 하지만 더 큰 문제를 낳는다.

> **핵심 통찰**: 자바 인터페이스에는 **구현 코드가 없다**. 따라서 나는 방식이 같은 오리가 48종이라도, 나는 행동을 바꾸려면 그 48개 클래스의 `fly()`를 **일일이 찾아 고쳐야** 한다. 코드 재사용은커녕 유지보수 지옥이 열린다.

상속(코드는 재사용되지만 강제 전파)과 인터페이스(전파는 막지만 재사용 불가) 사이에서 진퇴양난이다. 여기서 첫 번째 디자인 원칙이 등장한다.

---

## 4. 디자인 원칙 1: 바뀌는 부분을 분리하라

> **디자인 원칙 1**<br>애플리케이션에서 달라지는 부분을 찾아내고, 달라지지 않는 부분과 분리한다.

다르게 표현하면 이렇다.

> 바뀌는 부분은 따로 뽑아서 캡슐화한다. 그러면 나중에 바뀌지 않는 부분에는 영향을 미치지 않고 그 부분만 고치거나 확장할 수 있다.

이 원칙은 거의 모든 디자인 패턴의 밑바탕을 이룬다. 모든 패턴은 "시스템의 일부분을 다른 부분과 **독립적으로** 변화시키는" 방법을 제공하기 때문이다.

`SimUDuck`에서 바뀌는 부분은 무엇인가? 오리마다, 그리고 시간이 지남에 따라 달라지는 `fly()`와 `quack()`이다. 이 둘을 `Duck` 클래스에서 끄집어내 **별도의 클래스 집합**으로 옮긴다.

```
  ┌──────────┐        뽑아낸다        ┌─────────────────┐
  │   Duck   │ ─────────────────────> │  나는 행동 집합   │
  │  클래스   │                        ├─────────────────┤
  │ (변하지   │                        │  꽥꽥거리는       │
  │  않는 것) │                        │  행동 집합        │
  └──────────┘                        └─────────────────┘
```

---

## 5. 디자인 원칙 2: 구현보다 인터페이스에 맞춰 프로그래밍하라

행동 클래스 집합은 어떻게 설계해야 유연할까? 두 번째 원칙이 답을 준다.

> **디자인 원칙 2**<br>구현보다는 인터페이스에 맞춰서 프로그래밍한다.

여기서 "인터페이스"는 중의적이다. 자바의 `interface` 문법을 뜻할 수도 있고, "상위 형식(supertype)"이라는 **개념**을 뜻할 수도 있다. 이 원칙의 진짜 의미는 후자다.

> **핵심 통찰**: "인터페이스에 맞춰 프로그래밍하라" = "**상위 형식**에 맞춰 프로그래밍하라". 실행 시에 쓰이는 실제 객체 타입이 코드에 박히지 않도록, 변수를 상위 형식으로 선언해서 다형성을 활용하라는 뜻이다.

간단한 예로 비교해 보자. `Animal` 추상 클래스 아래에 `Dog`, `Cat` 구상 클래스가 있다고 하자.

```typescript
// ❌ 구현에 맞춘 프로그래밍 — 타입이 Dog로 고정됨
const d: Dog = new Dog();
d.bark();

// ✅ 상위 형식(인터페이스)에 맞춘 프로그래밍 — 다형성 활용
const animal: Animal = new Dog();
animal.makeSound();

// ✅✅ 더 나은 방법 — 어떤 하위 형식인지조차 몰라도 됨 (런타임에 주입)
const a: Animal = getAnimal();
a.makeSound();
```

<details>
<summary>Java 원본</summary>

```java
// ❌ 구현에 맞춘 프로그래밍
Dog d = new Dog();
d.bark();

// ✅ 상위 형식에 맞춘 프로그래밍
Animal animal = new Dog();
animal.makeSound();

// ✅✅ 런타임에 주입
Animal a = getAnimal();
a.makeSound();
```
</details>

---

## 6. 행동 클래스 구현하기

이 원칙에 따라 나는 행동과 꽥꽥거리는 행동을 각각 인터페이스로 정의하고, 구체적인 행동을 구현 클래스로 만든다.

```typescript
/** 나는 행동을 표현하는 전략 인터페이스. */
interface FlyBehavior {
  /** 구체적인 나는 방법을 수행한다. */
  fly(): void;
}

/** 날개로 나는 행동 (진짜 날 수 있는 오리용). */
class FlyWithWings implements FlyBehavior {
  fly(): void {
    console.log("날고 있어요!!");
  }
}

/** 날지 못하는 행동 (고무 오리·가짜 오리용). */
class FlyNoWay implements FlyBehavior {
  fly(): void {
    console.log("저는 못 날아요");
  }
}
```

```typescript
/** 꽥꽥거리는 행동을 표현하는 전략 인터페이스. */
interface QuackBehavior {
  /** 구체적인 꽥꽥거리는 방법을 수행한다. */
  quack(): void;
}

/** 진짜 꽥꽥 소리. */
class Quack implements QuackBehavior {
  quack(): void {
    console.log("꽥");
  }
}

/** 고무 오리의 삑삑 소리. */
class Squeak implements QuackBehavior {
  quack(): void {
    console.log("삑");
  }
}

/** 소리를 못 내는 행동. */
class MuteQuack implements QuackBehavior {
  quack(): void {
    console.log("<< 조용~ >>");
  }
}
```

<details>
<summary>Java 원본</summary>

```java
public interface FlyBehavior {
    void fly();
}

public class FlyWithWings implements FlyBehavior {
    public void fly() {
        System.out.println("날고 있어요!!");
    }
}

public class FlyNoWay implements FlyBehavior {
    public void fly() {
        System.out.println("저는 못 날아요");
    }
}

public interface QuackBehavior {
    void quack();
}

public class Quack implements QuackBehavior {
    public void quack() {
        System.out.println("꽥");
    }
}

public class Squeak implements QuackBehavior {
    public void quack() {
        System.out.println("삑");
    }
}

public class MuteQuack implements QuackBehavior {
    public void quack() {
        System.out.println("<< 조용~ >>");
    }
}
```
</details>

이렇게 하면 나는 행동·꽥꽥거리는 행동을 **다른 형식의 객체에서도 재사용**할 수 있고, 기존 오리 클래스를 건드리지 않고 **새 행동을 추가**할 수도 있다.

---

## 7. 오리 행동 통합 — 위임(delegation)

핵심은 나는 행동과 꽥꽥거리는 행동을 `Duck`에서 직접 구현하지 않고 **다른 클래스에 위임**한다는 것이다.

1. `Duck`에 인터페이스 형식의 인스턴스 변수 `flyBehavior`, `quackBehavior`를 둔다(구상 클래스 형식이 아니다).
2. `Duck`에서 `fly()`·`quack()`을 제거하고, 대신 `performFly()`·`performQuack()`을 넣는다.
3. `performQuack()`은 스스로 처리하지 않고 `quackBehavior`가 참조하는 객체에 **위임**한다.

```typescript
abstract class Duck {
  /** 나는 행동 — 실행 시점에 구체 전략이 주입된다. */
  protected flyBehavior!: FlyBehavior;
  /** 꽥꽥거리는 행동 — 실행 시점에 구체 전략이 주입된다. */
  protected quackBehavior!: QuackBehavior;

  /** 나는 행동을 flyBehavior 객체에 위임한다. */
  performFly(): void {
    this.flyBehavior.fly();
  }

  /** 꽥꽥거리는 행동을 quackBehavior 객체에 위임한다. */
  performQuack(): void {
    this.quackBehavior.quack();
  }

  swim(): void {
    console.log("모든 오리는 물에 뜹니다. 가짜 오리도 뜨죠");
  }

  abstract display(): void;
}
```

`MallardDuck`은 생성자에서 자신에게 맞는 구체 행동을 대입한다.

```typescript
class MallardDuck extends Duck {
  constructor() {
    super();
    // 물오리는 진짜 꽥꽥거리고, 날개로 난다.
    this.quackBehavior = new Quack();
    this.flyBehavior = new FlyWithWings();
  }

  display(): void {
    console.log("저는 물오리입니다");
  }
}
```

<details>
<summary>Java 원본</summary>

```java
public abstract class Duck {
    FlyBehavior flyBehavior;
    QuackBehavior quackBehavior;

    public Duck() { }

    public abstract void display();

    public void performFly() {
        flyBehavior.fly();      // 행동 클래스에 위임
    }

    public void performQuack() {
        quackBehavior.quack();  // 행동 클래스에 위임
    }

    public void swim() {
        System.out.println("모든 오리는 물에 뜹니다. 가짜 오리도 뜨죠");
    }
}

public class MallardDuck extends Duck {
    public MallardDuck() {
        quackBehavior = new Quack();
        flyBehavior = new FlyWithWings();
    }

    public void display() {
        System.out.println("저는 물오리입니다");
    }
}
```
</details>

> **무엇이든 물어보세요 (Q&A)**
>
> **Q. 생성자에서 `new Quack()`을 호출하잖아요. 구현에 맞춰 프로그래밍하지 말라면서요?**
> A. 맞는 지적이다. 지금은 1장이라 이렇게 두었다. 뒤에서 배울 팩토리 패턴(4장)이 바로 이 "구상 클래스 인스턴스 생성" 문제를 해결해 준다. 지금 단계에서도 `setter`로 실행 중에 행동을 바꿀 수 있으므로 충분히 유연하다.

---

## 8. 코드 테스트

```typescript
const mallard = new MallardDuck();
mallard.performQuack(); // 꽥
mallard.performFly();   // 날고 있어요!!
```

`performQuack()`은 `MallardDuck`이 `Duck`에서 상속받은 메서드다. 이 메서드는 자신의 `quackBehavior`(여기서는 `Quack`)에 실제 작업을 위임한다.

---

## 9. 동적으로 행동 지정하기

기껏 유연하게 만들었으니, **실행 중에** 행동을 바꿀 수 있게 해 보자. `Duck`에 세터 메서드를 추가한다.

```typescript
abstract class Duck {
  // ...앞의 코드 생략...

  /** 실행 중 나는 행동을 교체한다. */
  setFlyBehavior(fb: FlyBehavior): void {
    this.flyBehavior = fb;
  }

  /** 실행 중 꽥꽥거리는 행동을 교체한다. */
  setQuackBehavior(qb: QuackBehavior): void {
    this.quackBehavior = qb;
  }
}
```

바닥에서 시작해 날지 못하는 모형 오리 `ModelDuck`과, 로켓 추진 나는 행동 `FlyRocketPowered`를 만들어 실행 중에 능력을 부여해 보자.

```typescript
class ModelDuck extends Duck {
  constructor() {
    super();
    this.flyBehavior = new FlyNoWay(); // 처음엔 못 난다
    this.quackBehavior = new Quack();
  }

  display(): void {
    console.log("저는 모형 오리입니다");
  }
}

/** 로켓 추진으로 나는 행동. */
class FlyRocketPowered implements FlyBehavior {
  fly(): void {
    console.log("로켓 추진으로 날아갑니다!");
  }
}

const model = new ModelDuck();
model.performFly();                           // 저는 못 날아요
model.setFlyBehavior(new FlyRocketPowered()); // 실행 중 행동 교체!
model.performFly();                           // 로켓 추진으로 날아갑니다!
```

<details>
<summary>Java 원본</summary>

```java
// Duck 클래스에 추가
public void setFlyBehavior(FlyBehavior fb) {
    flyBehavior = fb;
}
public void setQuackBehavior(QuackBehavior qb) {
    quackBehavior = qb;
}

public class ModelDuck extends Duck {
    public ModelDuck() {
        flyBehavior = new FlyNoWay();
        quackBehavior = new Quack();
    }
    public void display() {
        System.out.println("저는 모형 오리입니다");
    }
}

public class FlyRocketPowered implements FlyBehavior {
    public void fly() {
        System.out.println("로켓 추진으로 날아갑니다!");
    }
}

// 테스트
Duck model = new ModelDuck();
model.performFly();                            // 저는 못 날아요
model.setFlyBehavior(new FlyRocketPowered());
model.performFly();                            // 로켓 추진으로 날아갑니다!
```
</details>

구현 코드가 `Duck` 안에 들어 있었다면 이런 **런타임 교체**는 불가능했을 것이다.

---

## 10. 디자인 원칙 3: 상속보다는 구성을 활용하라

각 오리는 `FlyBehavior`와 `QuackBehavior`를 **가지고 있다(HAS-A)**. 나는 행동과 꽥꽥거리는 행동을 이 객체들에 위임받는다. 이렇게 두 클래스를 합치는 것을 **구성(composition)**이라 부른다.

> **디자인 원칙 3**<br>상속보다는 구성을 활용한다.

> **핵심 통찰**: "A는 B이다(IS-A)"(상속)보다 "A에는 B가 있다(HAS-A)"(구성)가 나을 때가 많다. 구성을 쓰면 알고리즘군을 별도 클래스 집합으로 캡슐화할 수 있고, 구성 요소가 올바른 인터페이스만 구현한다면 **실행 중에 행동을 바꿀 수도** 있다.

---

## 11. 전략 패턴 (Strategy Pattern)

축하한다. 방금 첫 번째 디자인 패턴인 **전략 패턴**을 적용했다.

> **패턴 정의 — 전략 패턴 (Strategy Pattern)**<br>알고리즘군을 정의하고 각각을 캡슐화하여 교체해서 쓸 수 있게 만든다. 전략 패턴을 사용하면 알고리즘을 사용하는 클라이언트와 독립적으로 알고리즘을 변경할 수 있다.

`SimUDuck`을 전략 패턴에 대응시키면 이렇다.

| 전략 패턴의 구성 요소 | SimUDuck에서의 대응 |
|----------------------|---------------------|
| 알고리즘군을 캡슐화한 전략 인터페이스 | `FlyBehavior`, `QuackBehavior` |
| 교체 가능한 구체 전략들 | `FlyWithWings`·`FlyNoWay`·`FlyRocketPowered` / `Quack`·`Squeak`·`MuteQuack` |
| 전략을 사용하는 컨텍스트(클라이언트) | `Duck` (행동을 위임) |
| 실행 중 전략 교체 | `setFlyBehavior()`·`setQuackBehavior()` |

최종 클래스 구조는 다음과 같다.

```
                    ┌───────────────────────────┐      「나는 행동」 캡슐화
                    │           Duck            │      ┌────────────────────┐
                    ├───────────────────────────┤◇────>│   «interface»      │
   HAS-A (구성) ───▶│ flyBehavior: FlyBehavior  │      │   FlyBehavior      │
                    │ quackBehavior:QuackBehavior│◇──┐  │   fly()            │
                    │ performFly()              │   │  └────────────────────┘
                    │ performQuack()            │   │       △        △
                    │ setFlyBehavior()          │   │  FlyWithWings  FlyNoWay
                    │ setQuackBehavior()        │   │
                    │ swim() / display()«abstr» │   │  「꽥꽥거리는 행동」 캡슐화
                    └───────────────────────────┘   │  ┌────────────────────┐
                           △                        └─>│   «interface»      │
              ┌────────────┼──────────┬────────┐       │   QuackBehavior    │
        MallardDuck  RedheadDuck  RubberDuck DecoyDuck │   quack()          │
                                                        └────────────────────┘
                                                          △      △      △
                                                        Quack Squeak MuteQuack
```

행동 집합을 "일련의 행동"이 아니라 **알고리즘군**으로 바라보는 관점이 중요하다. 여기서는 오리의 행동이지만, 지역별로 다른 세금 계산 방식 같은 것에도 똑같이 적용된다.

---

## 12. 패턴은 개발자의 공유 어휘다

식당에서 손님이 "BLT 주세요"라고 하면 주방장은 긴 설명 없이 무엇을 만들지 안다. **전문 용어**가 소통을 압축하기 때문이다. 디자인 패턴도 마찬가지다.

> **핵심 통찰**: "오리들의 행동을 전략 패턴으로 구현했습니다"라는 한마디에는 "행동들이 쉽게 확장·변경 가능한 클래스 집합으로 캡슐화되어 있고, 실행 중에도 바꿀 수 있다"는 모든 함의가 담긴다. 패턴은 **구현 세부사항이 아니라 디자인 수준에서** 대화하게 해 준다.

패턴 어휘를 공유하면 (1) 적은 단어로 많은 것을 전달하고, (2) 디자인에 더 오래 집중하며, (3) 팀의 오해가 줄고, (4) 신입 개발자에게 학습 동기를 준다.

> **무엇이든 물어보세요 (Q&A)**
>
> **Q. 디자인 패턴이 그렇게 좋으면 왜 "디자인 패턴 라이브러리"는 없나요?**
> A. 디자인 패턴은 라이브러리보다 **더 높은 추상 단계**에 있다. 라이브러리·프레임워크는 특정 구현(코드)을 제공하지만, 패턴은 "클래스와 객체를 어떻게 구성해 문제를 풀지"에 대한 **설계**를 제공한다. 그 설계를 특정 애플리케이션에 적용하는 일은 개발자의 몫이다. (다만 라이브러리·프레임워크가 내부적으로 패턴을 사용하기는 한다.)
>
> **Q. 결국 캡슐화·상속·다형성만 잘 알면 패턴은 필요 없는 것 아닌가요?**
> A. 흔한 오해다. 객체지향 기초를 안다고 해서 유연하고 재사용·유지보수하기 좋은 시스템이 저절로 만들어지지는 않는다. 그런 시스템을 만드는 **검증된 방법**을 모아 놓은 것이 디자인 패턴이다. 패턴은 발명되는 것이 아니라 **발견**되는 것이다.

---

## 연습 문제 (해답 예시)

**1. 상속의 단점 고르기** — "`Duck`의 행동을 상속할 때 단점이 될 수 있는 요소를 모두 고르시오."
- ✅ A. 서브클래스에서 코드가 중복된다.
- ✅ B. 실행 시에 행동을 바꾸기 힘들다.
- ✅ D. 모든 오리의 행동을 파악하기 힘들다.
- ✅ F. 코드를 변경하면 다른 오리들에게 원치 않은 영향을 끼칠 수 있다.
- (C·E는 이 설계 맥락의 단점이 아니다.)

**2. 로켓 추진 나는 행동 추가하기** — `FlyBehavior` 인터페이스를 구현하는 `FlyRocketPowered` 클래스를 만들면 된다(§9에서 실제로 구현). 기존 `Duck`이나 다른 행동 클래스는 전혀 건드리지 않는다.

**3. `Quack`을 오리가 아닌 곳에서 재사용하기** — 사냥꾼이 쓰는 **오리 호출기(duck call)** 를 만들 때 `Quack` 행동을 재사용할 수 있다. 행동이 `Duck`에 묶여 있지 않고 독립 클래스로 캡슐화되어 있으므로 가능하다.

**4. "구현에 맞춘 코드" vs "인터페이스에 맞춘 코드"** — §5 참고. 변수를 상위 형식으로 선언하고 런타임에 구체 객체를 주입하면, 변수를 선언한 코드가 실제 객체 타입을 몰라도 된다.

---

## 디자인 원칙 정리 (누적)

이 책은 장이 진행되며 디자인 원칙이 도구상자에 하나씩 쌓인다. 1장까지의 도구는 다음과 같다.

1. **바뀌는 부분을 찾아내 캡슐화하고, 바뀌지 않는 부분과 분리한다.**
2. **구현보다는 인터페이스(상위 형식)에 맞춰 프로그래밍한다.**
3. **상속보다는 구성을 활용한다.**

---

## 요약

- 잘 돌아가던 코드도 **변화**(새 요구사항) 앞에서 무너질 수 있다. 소프트웨어 개발에서 변하지 않는 유일한 진리는 "변한다"는 것이다.
- 코드 재사용을 위한 **상속**은 슈퍼클래스 변경이 서브클래스로 강제 전파되는 문제가 있고, 구현 없는 **인터페이스**는 코드 재사용이 안 되는 문제가 있다.
- 해법은 **바뀌는 부분(알고리즘군)을 별도 클래스로 캡슐화**하고, 이를 인터페이스 형식으로 참조하여 **위임**하는 것이다.
- 이렇게 하면 (1) 행동을 다른 객체에서 재사용하고, (2) 기존 코드를 건드리지 않고 새 행동을 추가하며, (3) **실행 중에 행동을 교체**할 수 있다.
- 이 설계가 바로 **전략 패턴**이다: 알고리즘군을 캡슐화해 교체 가능하게 만들고, 클라이언트와 독립적으로 알고리즘을 변경한다.
- 디자인 패턴은 좋은 객체지향 설계를 만드는 **검증된 방법의 집합**이자, 개발자 사이의 **공유 어휘**다.

---

## 다른 챕터와의 관계

- **4장 팩토리 패턴**: 이 장의 `new Quack()`처럼 생성자에서 구상 클래스를 직접 만드는 문제를 해결한다.
- **6장 커맨드 패턴**: 요청(행동)을 객체로 캡슐화한다는 점에서 "행동의 캡슐화"라는 이 장의 아이디어를 확장한다.
- **12장 복합 패턴 / MVC**: 여러 패턴을 함께 쓰는 예로 `SimUDuck`이 다시 등장한다.
- 이 장에서 세운 3가지 디자인 원칙은 이후 모든 장의 밑바탕이 된다.

---

## 보너스: 원서 복습 요소

> 아래는 원서의 재미·복습용 요소(뇌 단련·디자인 퍼즐·낱말 퀴즈)를 학습 흐름과 분리해 모아 둔 것이다.

### 🧠 뇌 단련 (Brain Power)

1. **사냥꾼용 오리 호출기(duck call)** 를 `Duck` 클래스를 상속받지 **않고** 구현하려면? → 힌트: 오리 호출기는 오리가 아니다(IS-A 관계가 성립하지 않는다). 하지만 "꽥꽥거리는 행동은 가지고 있다(HAS-A)". `QuackBehavior`를 구현/구성하면 오리 계층과 무관하게 소리 기능을 재사용할 수 있다.
2. 객체지향·요리 말고 여러분이 아는 **전문 용어**(자동차 정비, 목공, 항공 관제 등)는? 그 용어는 어떤 내용을 압축해 전달하는가? '전략 패턴'이라는 이름이 전달하는 설계 내용은 무엇인가?

### 🧩 디자인 퍼즐 — 액션 어드벤처 게임

흩어진 클래스·인터페이스를 정돈해 게임 캐릭터와 무기 행동을 설계하는 문제. 각 캐릭터는 한 번에 한 무기만 쓰지만 게임 중에 무기를 바꿀 수 있다(→ 전형적인 전략 패턴).

- `Character`: 모든 캐릭터(`King`·`Queen`·`Knight`·`Troll`)가 공유하는 **추상 클래스**. `WeaponBehavior weapon` 필드와 `fight()`, `setWeapon()`을 가진다.
- `WeaponBehavior`: 모든 무기가 구현하는 **인터페이스**. `useWeapon()` 하나.
- 구체 무기: `SwordBehavior`(검)·`BowAndArrowBehavior`(활)·`KnifeBehavior`(칼)·`AxeBehavior`(도끼).
- 무기 교체는 `setWeapon(WeaponBehavior w)` 호출로, 싸움은 현재 무기의 `useWeapon()` 호출로 이뤄진다.

```
        ┌────────────────────────┐        «interface»
        │      Character         │◇──────> WeaponBehavior
        │ (추상)                  │  HAS-A  useWeapon()
        │ weapon: WeaponBehavior │            △
        │ fight() «abstract»     │   ┌────────┼────────┬─────────┐
        │ setWeapon(w)           │ Sword  BowAndArrow Knife    Axe
        └────────────────────────┘ Behavior Behavior  Behavior Behavior
              △
   ┌──────┬───┴───┬───────┐
  King  Queen  Knight   Troll
```

### 📝 낱말 퀴즈 (정답 단어 모음)

1장에 등장한 핵심 용어들(정답은 모두 영어): OBSERVER(옵저버), INTERFACE(인터페이스), FRAMEWORKS(프레임워크), SQUEAK(삑삑 소리), STRATEGY(전략), DECOYDUCK(가짜 오리), EXPERIENCE(경험), ENCAPSULATE(캡슐화), VOCABULARY(용어), COMPOSITION(구성), REUSED(재사용), FLEXIBLE(유연한), CHANGE(변화), PRINCIPLES(원칙), MAUI(마우이 — 주주총회가 열린 곳).
