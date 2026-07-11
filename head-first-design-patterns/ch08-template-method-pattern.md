# Chapter 08: The Template Method Pattern (템플릿 메소드 패턴)

## 핵심 질문

- 거의 똑같지만 **일부 단계만 다른** 알고리즘들의 중복을 어떻게 제거할까?
- 알고리즘의 **구조(골격)는 고정**하면서 특정 단계만 서브클래스가 채우게 하려면?
- 후크(hook)는 추상 메서드와 무엇이 다른가?
- "먼저 연락하지 마세요, 저희가 연락 드리겠습니다"는 할리우드 원칙은 무엇인가?

---

## 1. 커피와 홍차 — 거의 같은 제조법

```
커피: ①물 끓이기 ②커피 우려내기 ③컵에 따르기 ④설탕·우유 추가
홍차: ①물 끓이기 ②찻잎 우려내기 ③컵에 따르기 ④레몬 추가
```

`Coffee`와 `Tea` 클래스를 따로 만들면 ①③이 완전히 중복되고, ②④도 "우려내기/첨가물 추가"라는 점에서 사실상 같다.

> **핵심 통찰**: 알고리즘의 **구조가 동일**하다 — ①물 끓이기 → ②우려내기 → ③따르기 → ④첨가물. 다른 것은 ②와 ④의 **구체적 방법**뿐이다. 이 구조를 상위 클래스에 못 박고, 다른 단계만 서브클래스에 맡기면 중복이 사라진다.

---

## 2. 템플릿 메서드로 추상화

`brew()`(우려내기)와 `addCondiments()`(첨가물)로 일반화하고, 알고리즘 골격을 `prepareRecipe()`에 담는다.

```typescript
abstract class CaffeineBeverage {
  /** 템플릿 메서드 — 알고리즘 골격. 서브클래스가 못 바꾸도록 재정의 방지. */
  prepareRecipe(): void {
    this.boilWater();
    this.brew();          // 서브클래스가 구현
    this.pourInCup();
    this.addCondiments(); // 서브클래스가 구현
  }

  /** 우려내는 방법 — 음료마다 다르다. */
  protected abstract brew(): void;
  /** 첨가물 추가 — 음료마다 다르다. */
  protected abstract addCondiments(): void;

  protected boilWater(): void {
    console.log("물 끓이는 중");
  }
  protected pourInCup(): void {
    console.log("컵에 따르는 중");
  }
}

class Coffee extends CaffeineBeverage {
  protected brew(): void {
    console.log("필터로 커피를 우려내는 중");
  }
  protected addCondiments(): void {
    console.log("설탕과 우유를 추가하는 중");
  }
}

class Tea extends CaffeineBeverage {
  protected brew(): void {
    console.log("찻잎을 우려내는 중");
  }
  protected addCondiments(): void {
    console.log("레몬을 추가하는 중");
  }
}
```

<details>
<summary>Java 원본</summary>

```java
public abstract class CaffeineBeverage {
    // final: 서브클래스가 알고리즘 골격을 못 바꾸게 한다
    final void prepareRecipe() {
        boilWater();
        brew();
        pourInCup();
        addCondiments();
    }
    abstract void brew();
    abstract void addCondiments();
    void boilWater() { System.out.println("물 끓이는 중"); }
    void pourInCup() { System.out.println("컵에 따르는 중"); }
}

public class Coffee extends CaffeineBeverage {
    public void brew() { System.out.println("필터로 커피를 우려내는 중"); }
    public void addCondiments() { System.out.println("설탕과 우유를 추가하는 중"); }
}
```
</details>

> **핵심 통찰**: `prepareRecipe()`를 **`final`(재정의 불가)** 로 두는 것이 핵심이다. 알고리즘의 **구조·순서는 상위 클래스가 독점**하고, 서브클래스는 **빈칸(추상 메서드)만** 채운다.

> **패턴 정의 — 템플릿 메서드 패턴 (Template Method Pattern)**<br>알고리즘의 골격을 정의한다. 템플릿 메서드를 사용하면 알고리즘의 일부 단계를 서브클래스에서 구현할 수 있으며, 알고리즘의 구조는 그대로 유지하면서 특정 단계를 서브클래스에서 재정의할 수도 있다.

```
        AbstractClass
        templateMethod() «final»  ← 알고리즘 골격
          → primitiveOperation1()  «abstract»
          → primitiveOperation2()  «abstract»
          → concreteOperation()
          → hook()
              △
        ConcreteClass
          primitiveOperation1() / primitiveOperation2() 구현
```

---

## 3. 후크 (hook)

**후크**는 추상 클래스에 있는, 기본 구현이 비었거나 최소한인 메서드다. 서브클래스가 **선택적으로** 오버라이드해 알고리즘에 끼어들 수 있다.

```typescript
abstract class CaffeineBeverageWithHook {
  prepareRecipe(): void {
    this.boilWater();
    this.brew();
    this.pourInCup();
    if (this.customerWantsCondiments()) { // 후크로 흐름 제어
      this.addCondiments();
    }
  }

  protected abstract brew(): void;
  protected abstract addCondiments(): void;

  /** 후크 — 기본은 true. 서브클래스가 필요하면 오버라이드. */
  protected customerWantsCondiments(): boolean {
    return true;
  }
  // boilWater / pourInCup ...
}

class CoffeeWithHook extends CaffeineBeverageWithHook {
  protected brew(): void { console.log("필터로 커피를 우려내는 중"); }
  protected addCondiments(): void { console.log("우유와 설탕을 추가하는 중"); }

  // 후크를 오버라이드해 사용자에게 물어본다
  protected customerWantsCondiments(): boolean {
    const answer = this.getUserInput();
    return answer.toLowerCase().startsWith("y");
  }
  // getUserInput() ...
}
```

> **무엇이든 물어보세요 (Q&A)**
>
> **Q. 추상 메서드와 후크는 언제 각각 쓰나요?**
> A. 서브클래스가 **반드시 제공해야 하는** 단계는 **추상 메서드**. **선택적**인 단계(끼어들 기회, 흐름 제어)는 **후크**. 후크는 오버라이드해도, 안 해도 된다.

---

## 4. 할리우드 원칙 (디자인 원칙 8)

> **디자인 원칙 8 — 할리우드 원칙 (Hollywood Principle)**<br>먼저 연락하지 마세요. 저희가 연락 드리겠습니다. (Don't call us, we'll call you.)

**고수준 구성 요소가 저수준을 언제·어떻게 호출할지 결정**하고, 저수준은 고수준을 직접 호출하지 않는다. 이로써 의존성이 뒤엉키는 **의존성 부패(dependency rot)** 를 막는다.

템플릿 메서드가 바로 이것이다: `CaffeineBeverage`(고수준)가 `prepareRecipe()`에서 알고리즘을 쥐고, 필요할 때 `Coffee`/`Tea`(저수준)의 `brew()`·`addCondiments()`를 **불러낸다**. 서브클래스는 "호출당하기 전까지" 아무것도 하지 않는다.

> **무엇이든 물어보세요 (Q&A)**
>
> **Q. 할리우드 원칙과 DIP(원칙 6)의 관계는?**
> A. 둘 다 "객체 분리"가 목표다. DIP는 **추상화에 의존하라**는 더 일반적·강한 원칙이고, 할리우드 원칙은 **저수준이 고수준에 얽히지 않도록 프레임워크를 구성하는 기법**이다.

---

## 5. 실전 — 자바 API 속 템플릿 메서드

교과서적 형태가 아니어도 템플릿 메서드는 프레임워크 곳곳에 있다.

- **`Arrays.sort()` + `Comparable.compareTo()`**: `sort()`가 정렬 알고리즘(골격)을 쥐고, 비교 단계만 `compareTo()`에 위임한다. (상속 대신 정적 메서드 + 인터페이스로 구현한 **변형**)
- **`JFrame.paint()`**: `paint()`는 기본은 아무 일도 안 하는 **후크**. 오버라이드해 그래픽을 그린다.
- **`AbstractList.subList()`**: `get()`/`size()` 추상 메서드에 의존하는 템플릿 메서드. 상속해 두 메서드만 구현하면 리스트가 완성된다.

```typescript
// Arrays.sort의 정신을 TS로: 정렬(골격) + compare 단계 위임
class Duck {
  constructor(public name: string, public weight: number) {}
}

const ducks = [new Duck("Daffy", 8), new Duck("Dewey", 2), new Duck("Louie", 2)];
// sort가 알고리즘을 쥐고, 비교(compareTo에 해당) 단계만 우리가 제공
ducks.sort((a, b) => a.weight - b.weight);
```

> **핵심 통찰**: `Arrays.sort()`는 서브클래싱을 쓰지 않는(자바 배열은 서브클래싱 불가) **변형된** 템플릿 메서드다. "실전 패턴은 교과서와 똑같이 생기지 않는다" — 상황과 제약에 맞게 변형된다.

---

## 6. 템플릿 메서드 vs 전략 vs 팩토리 메서드

> 방구석 토크 — 템플릿 메서드와 전략의 대화<br><br>**전략**: 저는 **알고리즘 전체를 캡슐화**하고 **객체 구성**으로 통째로 갈아 끼워요. 실행 중에도 바꿀 수 있죠.<br>**템플릿 메서드**: 저는 **알고리즘 골격을 쥐고** 일부 단계만 서브클래스에 맡겨요. **상속**을 쓰니 객체가 적고 코드 중복도 적죠. 대신 유연성은 당신이 낫네요.

| 패턴 | 캡슐화 대상 | 방식 | 요지 |
|------|-----------|------|------|
| **전략**(1장) | 알고리즘 **전체**(교체 가능) | **구성** | 어떤 알고리즘을 쓸지 갈아 끼운다 |
| **템플릿 메서드**(이 장) | 알고리즘 **골격**(일부 단계) | **상속** | 구조는 고정, 단계만 채운다 |
| **팩토리 메서드**(4장) | **객체 생성** 단계 | **상속** | 템플릿 메서드의 특수형 |

> **핵심 통찰**: **팩토리 메서드는 템플릿 메서드의 특수한 경우**다 — "생성"이라는 한 단계를 서브클래스가 결정하게 한 것.

---

## 연습 문제 (해답 예시)

**1. `Coffee`·`Tea` 중복 제거 다이어그램** — `CaffeineBeverage`(추상)에 `prepareRecipe()`(템플릿)·`boilWater()`·`pourInCup()`을 두고, `Coffee`/`Tea`가 `brew()`·`addCondiments()`만 구현하도록 그린다.

**2. 오리 정렬 (`compareTo`)** — `Duck`이 `Comparable`을 구현하고 `compareTo(other)`에서 무게를 비교(작으면 -1, 같으면 0, 크면 1)한다. `Arrays.sort(ducks)`가 나머지(알고리즘)를 처리한다.

**3. 추상 메서드 vs 후크 판단** — 필수 단계면 추상, 선택 단계면 후크(§3 Q&A).

**4. 할리우드 원칙을 쓰는 다른 패턴** — **팩토리 메서드**(생산자가 서브클래스를 불러냄), **옵저버**(주제가 옵저버를 불러냄) 등.

---

## 디자인 원칙 정리 (누적)

1. 바뀌는 부분을 캡슐화한다.
2. 구현보다는 인터페이스에 맞춰 프로그래밍한다.
3. 상속보다는 구성을 활용한다.
4. 느슨한 결합을 사용한다.
5. OCP.
6. 추상화에 의존한다 (DIP).
7. 진짜 절친에게만 이야기한다 (최소 지식).
8. **먼저 연락하지 마세요, 저희가 연락 드리겠습니다 (할리우드 원칙).** ← 이번 장

---

## 요약

- **템플릿 메서드 패턴**은 알고리즘의 **골격을 상위 클래스에 고정**하고, 일부 단계만 **서브클래스**가 구현하게 한다.
- 템플릿 메서드는 보통 **`final`(재정의 불가)** 로 두어 알고리즘 구조를 보호한다.
- 추상 클래스는 **추상 메서드**(필수 단계)·**구상 메서드**·**후크**(선택 단계)를 가질 수 있다.
- **할리우드 원칙**: 고수준이 저수준을 불러내고, 저수준은 고수준을 직접 호출하지 않는다.
- 전략(구성, 알고리즘 전체 교체)과 달리 템플릿 메서드는 **상속**으로 골격을 재사용하며, **팩토리 메서드는 그 특수형**이다.
- 실전에서는 `Arrays.sort`·`JFrame.paint`·`AbstractList`처럼 **변형된** 형태로 나타난다.

---

## 다른 챕터와의 관계

- **1장 전략**: 둘 다 알고리즘 캡슐화 — 전략은 구성, 템플릿 메서드는 상속(위 비교표).
- **4장 팩토리 메서드**: 팩토리 메서드는 "생성 단계"에 특화된 템플릿 메서드.
- **6장 할리우드 원칙 실현체들**: 옵저버·팩토리 메서드도 "우리가 부를게" 구조를 공유한다.

---

## 보너스: 원서 복습 요소

### 🎙️ 방구석 토크 — 템플릿 메서드 vs 전략

- **템플릿 메서드**: 상속, 알고리즘을 꽉 쥠, 코드 중복 최소, 객체 적음(효율적).
- **전략**: 구성, 실행 중 알고리즘 교체 가능(유연), 위임 모형으로 약간 더 복잡.

### 🧠 뇌 단련 (Brain Power)

1. `Arrays.sort`가 상속 대신 정적 메서드 + `Comparable`을 쓴 것은 더 나은가? (배열을 서브클래싱할 수 없다는 자바 제약을 우회한 유연한 선택)
2. "기본 단계에서 객체를 생성·반환하는" 특화된 템플릿 메서드는? → **팩토리 메서드**.

### ❓ 누가 무엇을 할까요

- 템플릿 메서드 = 알고리즘의 어떤 단계 구현을 서브클래스가 결정.
- 전략 = 바꿔 쓸 수 있는 행동을 캡슐화, 서브클래스에 맡김.
- 팩토리 메서드 = 구상 클래스 인스턴스 생성을 서브클래스가 결정.

### 📝 낱말 퀴즈 (정답 단어 모음)

8장 용어들(정답은 영어): TEMPLATE 관련 — ALGORITHM(알고리즘), ABSTRACT(추상), HOOK(후크), OPTIONAL(필수적이지 않은), INHERITANCE(상속), COMPOSITION(구성), STRATEGY(전략 패턴), HOLLYWOOD(할리우드), SPECIALIZATION(특화), PAINT(paint), STATIC(정적), MERGESORT(mergesort), ABSTRACTLIST(AbstractList), CAFFEINE(카페인), STARBUZZ(스타버즈), TEA(홍차).
