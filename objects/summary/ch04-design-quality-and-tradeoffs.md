# Chapter 4: Design Quality and Tradeoffs (설계 품질과 트레이드오프) - 요약

> 상세 노트: [ch04-design-quality-and-tradeoffs.md](../notes/ch04-design-quality-and-tradeoffs.md)

**핵심 질문**: 왜 데이터 중심 설계는 변경에 취약한 구조를 만드는가? 캡슐화, 응집도, 결합도로 평가하면 무엇이 드러나는가?

## 핵심

- **두 가지 분할 축**: 데이터 중심("이 객체가 저장할 데이터는 무엇인가?")과 책임 중심("이 객체의 책임은 무엇인가?"). 상태는 불안정한 구현에 속하고 책임은 안정적인 인터페이스에 속하므로, 훌륭한 설계는 책임에 초점을 맞춘다.
- **데이터 중심 1차 설계**: Movie가 movieType 열거형과 discountAmount/discountPercent를 함께 갖고(종류 변수 + 배타적 사용 변수 = 전형적 안티패턴), ReservationAgency가 getter로 데이터를 꺼내 모든 제어 로직을 처리한다.
- **평가 기준**: 캡슐화(변경 가능성 높은 부분을 감추는 추상화), 응집도(하나의 변경 이유), 결합도(다른 모듈에 대한 지식의 양). 셋 다 변경의 관점에서 평가하며, 캡슐화가 응집도와 결합도를 결정하므로 캡슐화 먼저다.
- **getter/setter는 캡슐화가 아니다**: private이어도 접근자/수정자로 다 노출하면 public 속성과 같다. 협력을 고려하지 않고 "언젠가 쓰겠지"로 접근자를 늘리는 것이 추측에 의한 설계 전략(앨런 홀럽)이다. 1차 설계는 모든 변경이 ReservationAgency로 모이는 의존성 덩어리가 된다(SRP 위반 - 변경 이유 5가지).
- **2차 설계(스스로 책임지는 데이터 객체)도 부족**: 각 객체에 오퍼레이션을 옮겨도, isDiscountable(dayOfWeek, time) 같은 시그니처가 내부 속성을, calculateAmountDiscountedFee 같은 메서드 이름이 정책의 종류를 노출한다. 구현 변경이 여전히 Movie와 Screening까지 파급된다.
- **캡슐화의 진정한 의미**: 데이터 은닉만이 아니라 변경될 수 있는 어떤 것이라도(속성 타입, 정책의 종류) 감추는 것. "변하는 개념을 캡슐화하라"(GOF).
- **데이터 중심 설계가 실패하는 두 가지 이유**: 너무 이른 시기에 데이터(구현)를 결정하도록 강요하고, 협력이라는 문맥 없이 객체를 고립시켜 오퍼레이션을 결정하기 때문이다.

## 코드 한 컷

```typescript
// Rectangle 예시 - 책임의 위치가 캡슐화를 가른다
// Before: 외부가 getter/setter로 사각형을 조작 (추측에 의한 설계)
rectangle.setRight(rectangle.getRight() * multiple);
rectangle.setBottom(rectangle.getBottom() * multiple);

// After: 사각형이 스스로 커진다 - 내부 표현이 바뀌어도 외부는 무사
rectangle.enlarge(multiple);
```

> **핵심 통찰**: 캡슐화는 설계의 제1원리다. 데이터 중심 설계의 낮은 응집도와 높은 결합도는 전부 캡슐화 위반에서 나온 증상이다.
