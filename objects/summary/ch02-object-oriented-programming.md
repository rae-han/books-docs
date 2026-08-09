# Chapter 2: Object-Oriented Programming (객체지향 프로그래밍) - 요약

> 상세 노트: [ch02-object-oriented-programming.md](../notes/ch02-object-oriented-programming.md)

**핵심 질문**: 상속, 다형성, 추상화는 어떻게 유연하고 확장 가능한 설계를 가능하게 하며, 왜 코드 재사용에는 상속보다 합성이 나은가?

## 핵심

- **클래스가 아니라 객체에 초점**: 어떤 클래스가 필요한지보다 어떤 객체들이 어떤 상태와 행동을 가지고 협력하는지를 먼저 고민한다. 훌륭한 협력이 훌륭한 객체를, 훌륭한 객체가 훌륭한 클래스를 낳는다.
- **도메인 구조를 따르는 프로그램 구조**: 영화 예매 도메인의 개념(Movie, Screening, DiscountPolicy, DiscountCondition, Reservation)이 클래스로 매끄럽게 이어진다. 요구사항부터 구현까지 객체라는 동일한 추상화를 쓰는 것이 객체지향의 힘이다.
- **의미를 표현하는 객체**: 금액을 Long이 아닌 Money 객체로 구현한다. 인스턴스 변수가 하나뿐이어도 개념을 명시적으로 표현하는 것이 설계 명확성의 첫걸음이다.
- **메시지와 메서드의 구분**: Screening은 Movie에 calculateMovieFee 메시지를 전송할 뿐, 어떤 메서드가 실행될지는 수신자가 자율적으로 결정한다. 이 구분에서 다형성이 출발한다.
- **컴파일 의존성과 실행 의존성의 분리**: Movie는 코드상 추상 클래스 DiscountPolicy에만 의존하지만, 실행 시점에는 Amount/PercentDiscountPolicy 인스턴스와 협력한다. 이 간극이 클수록 설계는 유연해지지만 코드 이해는 어려워진다(트레이드오프).
- **추상화의 힘**: "예매 요금은 하나의 할인 정책과 다수의 할인 조건으로 계산한다"는 상위 정책만으로 협력을 서술할 수 있고, NoneDiscountPolicy처럼 기존 코드를 수정하지 않고 새 클래스 추가만으로 기능을 확장할 수 있다. 할인 없음을 Movie 안의 null 검사로 처리하면 협력의 일관성이 무너진다.
- **상속보다 합성**: 상속은 부모의 내부 구현을 알아야 해서 캡슐화를 위반하고, 관계가 컴파일 시점에 고정돼 유연하지 않다. 합성은 인터페이스를 통한 약한 결합이라 실행 중 정책 교체(changeDiscountPolicy)가 가능하다. 단, 다형성을 위한 인터페이스 상속은 합성과 함께 쓴다.

## 코드 한 컷

```typescript
// Movie는 구체적 할인 정책을 모른다 - 추상화에만 의존
calculateMovieFee(screening: Screening): Money {
    return this.fee.minus(this.discountPolicy.calculateDiscountAmount(screening));
}
// 확장 = 수정이 아니라 추가: 할인 없음도 정책의 하나로
class NoneDiscountPolicy extends DiscountPolicy {
    protected getDiscountAmount(screening: Screening): Money {
        return Money.ZERO;
    }
}
```

> **핵심 통찰**: 유연성이 필요한 곳에 추상화를 사용하라. 추상화는 설계가 구체적인 상황에 결합되는 것을 막아, 수정 없이 추가만으로 확장할 수 있게 한다.
