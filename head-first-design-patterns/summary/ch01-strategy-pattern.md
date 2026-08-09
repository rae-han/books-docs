# Chapter 01: Welcome to Design Patterns (디자인 패턴 소개와 전략 패턴) - 요약

**핵심 질문**: 잘 돌아가던 코드가 왜 새 요구사항 하나에 무너지는가? 바뀌는 부분을 어떻게 분리하고 캡슐화하는가?

## 상속의 배신 - SimUDuck 이야기

오리 시뮬레이터 SimUDuck은 `Duck` 슈퍼클래스를 상속받아 여러 오리를 만든 교과서적 설계였다. 그런데 "오리가 날 수 있어야 한다"는 요구사항에 슈퍼클래스에 `fly()`를 추가하자, 주주총회 데모에서 **고무 오리가 화면을 날아다니는 참사**가 벌어졌다.

코드 재사용용 상속의 문제가 그대로 드러난 것이다. 슈퍼클래스의 변경 하나가 부적합한 서브클래스에까지 강제 전파되고, 고무 오리는 `fly()`를, 가짜 나무 오리는 `fly()`와 `quack()`을 빈 메서드로 오버라이드해야 하며, 오리 종류가 늘 때마다 이 지겨운 오버라이드가 영원히 반복된다.

`Flyable`, `Quackable` 인터페이스로 갈아타면 전파는 막을 수 있지만 더 큰 문제가 생긴다. 인터페이스에는 구현 코드가 없으므로 나는 방식이 같은 오리가 48종이면 **48개 클래스의 `fly()`를 일일이 고쳐야** 한다. 상속(재사용되지만 강제 전파)과 인터페이스(전파는 막지만 재사용 불가)의 진퇴양난이다.

## 해법: 바뀌는 부분을 캡슐화하고 위임하기

SimUDuck에서 바뀌는 부분은 오리마다, 시간이 지나며 달라지는 `fly()`와 `quack()`이다. 이 둘을 Duck에서 끄집어내 **행동 인터페이스와 구현 클래스 집합**으로 옮기고, Duck은 행동을 직접 구현하지 않고 **위임**한다.

```typescript
/** 나는 행동을 표현하는 전략 인터페이스. */
interface FlyBehavior {
  fly(): void;
}
class FlyWithWings implements FlyBehavior {
  fly(): void { console.log("날고 있어요!!"); }
}
class FlyNoWay implements FlyBehavior {
  fly(): void { console.log("저는 못 날아요"); }
}

abstract class Duck {
  /** 실행 시점에 구체 전략이 주입된다 - 구상 클래스 형식이 아니다. */
  protected flyBehavior!: FlyBehavior;
  protected quackBehavior!: QuackBehavior;

  performFly(): void {
    this.flyBehavior.fly();   // 행동 객체에 위임
  }
  setFlyBehavior(fb: FlyBehavior): void {
    this.flyBehavior = fb;    // 실행 중 행동 교체
  }
  abstract display(): void;
}

class MallardDuck extends Duck {
  constructor() {
    super();
    this.quackBehavior = new Quack();
    this.flyBehavior = new FlyWithWings();
  }
  display(): void { console.log("저는 물오리입니다"); }
}

// 날지 못하던 모형 오리에게 실행 중에 로켓 추진 능력 부여
model.setFlyBehavior(new FlyRocketPowered());
```

이렇게 하면 행동을 다른 형식의 객체(사냥꾼용 오리 호출기 등)에서도 재사용할 수 있고, 기존 오리 클래스를 건드리지 않고 새 행동을 추가할 수 있으며, setter로 **실행 중에 행동을 교체**할 수 있다. 구현이 Duck 안에 있었다면 런타임 교체는 불가능했다.

## 전략 패턴

> **패턴 정의 - 전략 패턴 (Strategy Pattern)**<br>알고리즘군을 정의하고 각각을 캡슐화하여 교체해서 쓸 수 있게 만든다. 전략 패턴을 사용하면 알고리즘을 사용하는 클라이언트와 독립적으로 알고리즘을 변경할 수 있다.

| 전략 패턴의 구성 요소 | SimUDuck에서의 대응 |
|----------------------|---------------------|
| 전략 인터페이스 | FlyBehavior, QuackBehavior |
| 교체 가능한 구체 전략들 | FlyWithWings, FlyNoWay, FlyRocketPowered / Quack, Squeak, MuteQuack |
| 전략을 사용하는 컨텍스트 | Duck (행동을 위임) |
| 실행 중 전략 교체 | setFlyBehavior(), setQuackBehavior() |

오리는 행동을 상속받는 것(IS-A)이 아니라 가진다(HAS-A). 이것이 **구성(composition)**이며, 구성 요소가 올바른 인터페이스만 구현하면 런타임에 행동을 바꿀 수 있다. 오리의 행동뿐 아니라 지역별로 다른 세금 계산 방식처럼, 행동 집합을 **알고리즘군**으로 바라보는 관점이 핵심이다.

## 패턴은 개발자의 공유 어휘다

식당에서 "BLT 주세요" 한마디면 주방장이 무엇을 만들지 알 듯, "오리 행동을 전략 패턴으로 구현했습니다"라는 말에는 "행동들이 확장/교체 가능한 클래스 집합으로 캡슐화돼 있고 실행 중에도 바꿀 수 있다"는 함의가 다 담긴다. 패턴 어휘는 구현 세부사항이 아니라 **디자인 수준에서** 대화하게 해 준다.

패턴은 라이브러리보다 높은 추상 단계에 있다. 라이브러리는 특정 구현(코드)을 제공하지만, 패턴은 클래스와 객체를 어떻게 구성해 문제를 풀지에 대한 **설계**를 제공하며, 그것을 애플리케이션에 적용하는 일은 개발자의 몫이다. 객체지향 기초(캡슐화, 상속, 다형성)를 안다고 유연한 시스템이 저절로 나오지 않는다. 그 검증된 방법을 모은 것이 패턴이고, 패턴은 발명되는 것이 아니라 **발견**되는 것이다.

## 디자인 원칙 정리 (누적: 1~3)

1. **바뀌는 부분을 찾아내 캡슐화하고, 바뀌지 않는 부분과 분리한다.**
2. **구현보다는 인터페이스(상위 형식)에 맞춰 프로그래밍한다.** - 변수를 상위 형식으로 선언하고 런타임에 구체 객체를 주입
3. **상속보다는 구성을 활용한다.**

> **핵심 통찰**: 소프트웨어에서 변하지 않는 유일한 진리는 "변한다"는 것이다. 거의 모든 디자인 패턴은 시스템의 일부를 나머지와 독립적으로 변화시키는 방법이다.
