# Chapter 5: Assigning Responsibilities (책임 할당하기) - 요약

> 상세 노트: [ch05-assigning-responsibilities.md](../notes/ch05-assigning-responsibilities.md)

**핵심 질문**: 책임을 할당할 때 어떤 원칙을 따라야 하는가? GRASP 패턴은 무엇을 기준으로 책임을 배분하는가?

## 핵심

- **두 가지 전환 원칙**: 데이터보다 행동을 먼저 결정하고("책임이 무엇인가?"를 먼저 묻기), 협력이라는 문맥 안에서 책임을 결정한다. "객체를 가지고 있어서 메시지를 보내는 게 아니라, 메시지를 전송하기 때문에 객체를 갖게 된 것이다"(샌디 메츠).
- **INFORMATION EXPERT**: 책임 수행에 필요한 정보를 가진 객체에게 할당한다. "예매하라"는 Screening, "가격을 계산하라"는 Movie, "할인 여부를 판단하라"는 DiscountCondition. 정보는 데이터와 달라서, 저장하지 않고 계산하거나 다른 객체를 알기만 해도 전문가다.
- **LOW COUPLING / HIGH COHESION**: 설계 대안 사이의 평가 기준. Screening이 DiscountCondition과 직접 협력하는 대안은 새 결합을 추가하고(도메인상 Movie가 이미 조건을 알고 있음) Screening에 다른 변경 이유를 얹으므로 기각된다.
- **CREATOR**: 생성될 객체를 포함/참조/사용하거나 초기화 데이터를 가진 객체에게 생성 책임을 준다. Reservation의 창조자는 Screening이다.
- **낮은 응집도의 세 가지 징후**: 인스턴스 변수 일부만 초기화됨(순번 조건이면 기간 필드가 빈다), 메서드들이 쓰는 속성 그룹이 갈린다, 변경 이유가 둘 이상이다. 초기 DiscountCondition이 셋 다 해당했다.
- **POLYMORPHISM**: 타입에 따라 변하는 로직(if~else, switch)은 타입을 명시적 클래스로 분리하고 다형적으로 책임을 할당한다. 단, Movie가 Sequence/PeriodCondition 클래스 양쪽에 직접 결합하면 역효과이므로 DiscountCondition 인터페이스(역할)를 둔다.
- **PROTECTED VARIATIONS**: 변화가 예상되는 불안정한 지점 주위에 안정된 인터페이스를 형성한다. 캡슐화해야 하는 것은 데이터가 아니라 변경이다. 역할 덕에 새 할인 조건을 추가해도 Movie는 영향받지 않는다.
- **유연성이 더 필요하면 합성**: 실행 중 할인 정책 교체 요구가 생기면 상속 계층(AmountDiscountMovie 등)을 DiscountPolicy 합성으로 바꾼다. 이것이 2장의 최종 구조다.
- **리팩터링이라는 대안**: 처음부터 책임 주도로 못 가도 된다. 몬스터 메서드를 응집도 있는 작은 메서드로 분해한 뒤, 각 메서드를 그것이 사용하는 데이터를 가진 클래스로 옮기면(자율적인 객체) 유사한 설계에 도달한다.

> **핵심 통찰**: GRASP은 정답 목록이 아니라 트레이드오프 판단의 어휘다. 책임 하나를 놓고 결합도와 응집도의 관점에서 설계 대안을 비교하는 습관이 책임 주도 설계의 실체다.
