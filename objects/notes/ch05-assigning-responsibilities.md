# Chapter 5: Assigning Responsibilities (책임 할당하기)

## 핵심 질문

객체에게 책임을 할당할 때 어떤 원칙을 따라야 하는가? GRASP 패턴은 어떤 기준으로 책임을 올바른 객체에게 배분하며, 데이터 중심의 설계를 책임 중심의 설계로 전환하려면 어떤 과정을 거쳐야 하는가?

---

## 1. 책임 주도 설계를 향해

4장에서는 데이터 중심의 접근법이 직면하는 다양한 문제점들을 살펴봤다. 데이터 중심의 설계는 행동보다 데이터를 먼저 결정하고, 협력이라는 문맥을 벗어나 고립된 객체의 상태에 초점을 맞추기 때문에 캡슐화를 위반하기 쉽고, 요소들 사이의 결합도가 높아지며, 코드를 변경하기 어려워진다.

데이터 중심 설계로 인해 발생하는 문제점을 해결할 수 있는 가장 기본적인 방법은 **데이터가 아닌 책임에 초점을 맞추는 것**이다. 데이터 중심의 설계에서 책임 중심의 설계로 전환하기 위해서는 다음의 두 가지 원칙을 따라야 한다.

- 데이터보다 행동을 먼저 결정하라
- 협력이라는 문맥 안에서 책임을 결정하라

### 1.1 데이터보다 행동을 먼저 결정하라

객체에게 중요한 것은 데이터가 아니라 외부에 제공하는 행동이다. 클라이언트의 관점에서 객체가 수행하는 행동이란 곧 객체의 책임을 의미한다. 객체는 협력에 참여하기 위해 존재하며 협력 안에서 수행하는 책임이 객체의 존재 가치를 증명한다.

데이터는 객체가 책임을 수행하는 데 필요한 재료를 제공할 뿐이다. 객체지향에 갓 입문한 사람들이 가장 많이 저지르는 실수가 바로 객체의 행동이 아니라 데이터에 초점을 맞추는 것이다. 너무 이른 시기에 데이터에 초점을 맞추면 객체의 캡슐화가 약화되기 때문에 낮은 응집도와 높은 결합도를 가진 객체들로 넘쳐나게 된다.

가장 기본적인 해결 방법은 객체를 설계하기 위한 **질문의 순서를 바꾸는 것**이다.

| 접근 방식 | 첫 번째 질문 | 두 번째 질문 |
|---|---|---|
| **데이터 중심** | "이 객체가 포함해야 하는 데이터가 무엇인가?" | "데이터를 처리하는 데 필요한 오퍼레이션은 무엇인가?" |
| **책임 중심** | "이 객체가 수행해야 하는 책임은 무엇인가?" | "이 책임을 수행하는 데 필요한 데이터는 무엇인가?" |

책임 중심의 설계에서는 객체의 행동, 즉 책임을 먼저 결정한 후에 객체의 상태를 결정한다.

### 1.2 협력이라는 문맥 안에서 책임을 결정하라

객체에게 할당된 책임의 품질은 협력에 적합한 정도로 결정된다. 객체에게 할당된 책임이 협력에 어울리지 않는다면 그 책임은 나쁜 것이다. 객체의 입장에서는 책임이 조금 어색해 보이더라도 협력에 적합하다면 그 책임은 좋은 것이다.

협력을 시작하는 주체는 메시지 전송자이기 때문에 **협력에 적합한 책임이란 메시지 수신자가 아니라 메시지 전송자에게 적합한 책임을 의미한다**. 즉 메시지를 전송하는 클라이언트의 의도에 적합한 책임을 할당해야 한다.

> **핵심 통찰**: 객체를 결정한 후에 메시지를 선택하는 것이 아니라 **메시지를 결정한 후에 객체를 선택해야 한다**. 메시지가 존재하기 때문에 그 메시지를 처리할 객체가 필요한 것이다. 객체가 메시지를 선택하는 것이 아니라 메시지가 객체를 선택하게 해야 한다.

> "이 클래스가 필요하다는 점은 알겠는데 이 클래스는 무엇을 해야 하지?"라고 질문하지 않고 "메시지를 전송해야 하는데 누구에게 전송해야 하지?"라고 질문하는 것. 설계의 핵심 질문을 이렇게 바꾸는 것이 메시지 기반 설계로 향하는 첫걸음이다.
>
> 객체를 가지고 있기 때문에 메시지를 보내는 것이 아니다. 메시지를 전송하기 때문에 객체를 갖게 된 것이다. - Sandi Metz

메시지를 먼저 결정하기 때문에 메시지 송신자는 메시지 수신자에 대한 어떠한 가정도 할 수 없다. 메시지 전송자의 관점에서 메시지 수신자가 깔끔하게 캡슐화되는 것이다. 이처럼 처음부터 데이터에 집중하는 데이터 중심의 설계가 캡슐화에 취약한 반면, 협력이라는 문맥 안에서 메시지에 집중하는 책임 중심의 설계는 캡슐화의 원리를 지키기가 훨씬 쉬워진다.

### 1.3 책임 주도 설계의 흐름

3장에서 설명한 책임 주도 설계의 흐름을 다시 정리하면 다음과 같다.

1. 시스템이 사용자에게 제공해야 하는 기능인 **시스템 책임**을 파악한다.
2. 시스템 책임을 **더 작은 책임으로 분할**한다.
3. 분할된 책임을 수행할 수 있는 적절한 객체 또는 역할을 찾아 **책임을 할당**한다.
4. 객체가 책임을 수행하는 도중 다른 객체의 도움이 필요한 경우 이를 책임질 적절한 객체 또는 역할을 찾는다.
5. 해당 객체 또는 역할에게 **책임을 할당함으로써 두 객체가 협력**하게 한다.

책임 주도 설계의 핵심은 **책임을 결정한 후에 책임을 수행할 객체를 결정하는 것**이다. 그리고 협력에 참여하는 객체들의 책임이 어느 정도 정리될 때까지는 객체의 내부 상태에 대해 관심을 가지지 않는 것이다.

---

## 2. 책임 할당을 위한 GRASP 패턴

GRASP(*General Responsibility Assignment Software Pattern - 일반적인 책임 할당을 위한 소프트웨어 패턴*)은 크레이그 라만(Craig Larman)이 패턴 형식으로 제안한 것으로, 객체에게 책임을 할당할 때 지침으로 삼을 수 있는 원칙들의 집합을 패턴 형식으로 정리한 것이다.

### 2.1 도메인 개념에서 출발하기

설계를 시작하기 전에 도메인에 대한 개략적인 모습을 그려 보는 것이 유용하다. 도메인 안에는 무수히 많은 개념들이 존재하며 이 도메인 개념들을 책임 할당의 대상으로 사용하면 코드에 도메인의 모습을 투영하기가 좀 더 수월해진다. 따라서 어떤 책임을 할당해야 할 때 가장 먼저 고민해야 하는 유력한 후보는 바로 **도메인 개념**이다.

```
┌──────┐ 1    * ┌──────────┐ 1    * ┌──────┐
│ 영화 │────────│  상영    │────────│ 예매 │
└──┬───┘        └──────────┘        └──────┘
   │ 1
   │
   │ *
┌──┴──────────┐
│  할인 조건  │
├─────────────┤
│ 순번 조건   │
│ 기간 조건   │
└─────────────┘

영화의 종류: 금액 할인 영화, 비율 할인 영화
```

설계를 시작하는 단계에서는 개념들의 의미와 관계가 정확하거나 완벽할 필요가 없다. 단지 출발점이 필요할 뿐이다. 중요한 것은 설계를 시작하는 것이지 도메인 개념들을 완벽하게 정리하는 것이 아니다. 도메인 개념을 정리하는 데 너무 많은 시간을 들이지 말고 빠르게 설계와 구현을 진행하라.

> 올바른 도메인 모델이란 존재하지 않는다. 도메인 모델은 도메인을 개념적으로 표현한 것이지만 그 안에 포함된 개념과 관계는 구현의 기반이 돼야 한다. 이것은 도메인 모델이 구현을 염두에 두고 구조화되는 것이 바람직하다는 것을 의미한다. 필요한 것은 도메인을 그대로 투영한 모델이 아니라 **구현에 도움이 되는 모델**이다. 다시 말해서 실용적이면서도 유용한 모델이 답이다.

### 2.2 INFORMATION EXPERT 패턴: 정보 전문가에게 책임을 할당하라

책임 주도 설계 방식의 첫 단계는 애플리케이션이 제공해야 하는 기능을 애플리케이션의 책임으로 생각하는 것이다. 이 책임을 애플리케이션에 대해 전송된 메시지로 간주하고 이 메시지를 책임질 첫 번째 객체를 선택하는 것으로 설계를 시작한다.

사용자에게 제공해야 하는 기능은 "영화를 예매하는 것"이다. 이를 책임으로 간주하면 애플리케이션은 영화를 예매할 책임이 있다고 말할 수 있다.

**첫 번째 질문: 메시지를 전송할 객체는 무엇을 원하는가?**

협력을 시작하는 객체는 미정이지만 이 객체가 원하는 것은 분명하다. 바로 영화를 예매하는 것이다. 따라서 메시지의 이름으로는 `예매하라`가 적절하다.

```
──── 1: 예매하라 ────▶ ?
```

**두 번째 질문: 메시지를 수신할 적합한 객체는 누구인가?**

이 질문에 답하기 위해서는 객체가 상태와 행동을 통합한 캡슐화의 단위라는 사실에 집중해야 한다. 객체는 자신의 상태를 스스로 처리하는 자율적인 존재여야 한다. 따라서 객체에게 책임을 할당하는 첫 번째 원칙은 **책임을 수행할 정보를 알고 있는 객체에게 책임을 할당하는 것**이다. GRASP에서는 이를 **INFORMATION EXPERT(정보 전문가) 패턴**이라고 부른다.

> **INFORMATION EXPERT 패턴**
>
> 책임을 객체에 할당하는 일반적인 원리는 무엇인가? 책임을 **정보 전문가**, 즉 **책임을 수행하는 데 필요한 정보를 가지고 있는 객체에게 할당하라**.

INFORMATION EXPERT 패턴은 객체가 자율적인 존재여야 한다는 사실을 다시 한번 상기시킨다. 정보를 알고 있는 객체만이 책임을 어떻게 수행할지 스스로 결정할 수 있기 때문이다. INFORMATION EXPERT 패턴을 따르면 정보와 행동을 최대한 가까운 곳에 위치시키기 때문에 캡슐화를 유지할 수 있다. 필요한 정보를 가진 객체들로 책임이 분산되기 때문에 더 응집력 있고 이해하기 쉬워진다.

여기서 이야기하는 **정보는 데이터와 다르다**는 사실에 주의하라. 책임을 수행하는 객체가 정보를 알고 있다고 해서 그 정보를 '저장'하고 있을 필요는 없다. 객체는 해당 정보를 제공할 수 있는 다른 객체를 알고 있거나 필요한 정보를 계산해서 제공할 수도 있다.

INFORMATION EXPERT 패턴에 따르면 예매하는 데 필요한 정보를 가장 많이 알고 있는 객체에게 `예매하라` 메시지를 처리할 책임을 할당해야 한다. `상영(Screening)`은 영화에 대한 정보와 상영 시간, 상영 순번처럼 영화 예매에 필요한 다양한 정보를 알고 있다. 따라서 영화 예매를 위한 정보 전문가다.

```
──── 1: 예매하라 ────▶ Screening
```

`예매하라` 메시지를 수신했을 때 Screening이 수행해야 하는 작업의 흐름을 생각해 보자. 예매 가격을 계산하기 위해서는 영화 한 편의 가격을 알아야 한다. 안타깝게도 Screening은 가격을 계산하는 데 필요한 정보를 모르기 때문에 외부의 객체에게 도움을 요청해서 가격을 얻어야 한다. 이 외부에 대한 요청이 새로운 메시지가 된다.

```
──── 1: 예매하라 ────▶ Screening ──── 2: 가격을 계산하라 ────▶ ?
```

영화 가격을 계산하는 데 필요한 정보를 알고 있는 전문가는 `영화(Movie)`다. 따라서 INFORMATION EXPERT 패턴에 따라 메시지를 수신할 적당한 객체는 Movie가 된다. Movie는 영화 가격을 계산할 책임을 지게 된다.

```
──── 1: 예매하라 ────▶ Screening ──── 2: 가격을 계산하라 ────▶ Movie
```

요금을 계산하기 위해서는 먼저 영화가 할인 가능한지를 판단한 후 할인 정책에 따라 할인 요금을 제외한 금액을 계산하면 된다. Movie가 스스로 처리할 수 없는 일이 한 가지 있다. 할인 조건에 따라 영화가 할인 가능한지를 판단하는 것이다. 따라서 Movie는 `할인 여부를 판단하라` 메시지를 전송해서 외부의 도움을 요청해야 한다.

```
──── 1: 예매하라 ────▶ Screening ──── 2: 가격을 계산하라 ────▶ Movie
                                                                 │
                                               3: 할인 여부를 판단하라
                                                                 │
                                                                 ▼
                                                          DiscountCondition
```

DiscountCondition은 자체적으로 할인 여부를 판단하는 데 필요한 모든 정보를 알고 있기 때문에 외부의 도움 없이도 스스로 할인 여부를 판단할 수 있다.

Movie는 DiscountCondition 중에서 할인 가능한 조건이 하나라도 존재하면 할인 정책에 정해진 계산식에 따라 요금을 계산한 후 반환한다. 만약 할인 가능한 조건이 존재하지 않는다면 영화의 기본 금액을 반환한다.

> **핵심 통찰**: INFORMATION EXPERT 패턴은 객체에게 책임을 할당할 때 가장 기본이 되는 책임 할당 원칙이다. 이 패턴은 객체란 상태와 행동을 함께 가지는 단위라는 객체지향의 가장 기본적인 원리를 책임 할당의 관점에서 표현한다. INFORMATION EXPERT 패턴을 따르는 것만으로도 자율성이 높은 객체들로 구성된 협력 공동체를 구축할 가능성이 높아진다.

### 2.3 LOW COUPLING 패턴과 HIGH COHESION 패턴

설계는 트레이드오프 활동이라는 것을 기억하라. 동일한 기능을 구현할 수 있는 무수히 많은 설계가 존재한다. 따라서 실제로 설계를 진행하다 보면 몇 가지 설계 중에서 한 가지를 선택해야 하는 경우가 빈번하게 발생한다.

예를 들어, 할인 요금을 계산하기 위해 Movie가 DiscountCondition에 `할인 여부를 판단하라` 메시지를 전송한다. 그렇다면 이 설계의 대안으로 Movie 대신 **Screening이 직접 DiscountCondition과 협력**하게 하는 것은 어떨까?

```
[대안 설계]
               할인 여부
──── 1: 예매하라 ────▶ Screening ──── 3: 가격을 계산하라 ────▶ Movie
                           │                                   예매 요금
                           │
              2: 할인 여부를 판단하라
                           │
                           ▼
                    DiscountCondition
```

이 설계는 기능적인 측면에서는 원래 설계와 동일하다. 차이점은 DiscountCondition과 협력하는 객체가 Movie가 아니라 Screening이라는 것뿐이다. 그렇다면 왜 Movie가 DiscountCondition과 협력하는 방법을 선택해야 할까?

그 이유는 **응집도와 결합도**에 있다. GRASP에서는 이를 **LOW COUPLING(낮은 결합도) 패턴**과 **HIGH COHESION(높은 응집도) 패턴**이라고 부른다.

#### LOW COUPLING 패턴

> **LOW COUPLING 패턴**
>
> 어떻게 하면 의존성을 낮추고 변화의 영향을 줄이며 재사용성을 증가시킬 수 있을까? **설계의 전체적인 결합도가 낮게 유지되도록 책임을 할당하라.**

도메인 상으로 Movie는 DiscountCondition의 목록을 속성으로 포함하고 있다. Movie와 DiscountCondition은 이미 결합돼 있기 때문에 Movie를 DiscountCondition과 협력하게 하면 **설계 전체적으로 결합도를 추가하지 않고도** 협력을 완성할 수 있다.

하지만 Screening이 DiscountCondition과 협력할 경우에는 Screening과 DiscountCondition 사이에 **새로운 결합도가 추가된다**. 따라서 LOW COUPLING 패턴의 관점에서는 Movie가 DiscountCondition과 협력하는 것이 더 나은 설계 대안이다.

#### HIGH COHESION 패턴

> **HIGH COHESION 패턴**
>
> 어떻게 복잡성을 관리할 수 있는 수준으로 유지할 것인가? **높은 응집도를 유지할 수 있게 책임을 할당하라.**

Screening의 가장 중요한 책임은 예매를 생성하는 것이다. 만약 Screening이 DiscountCondition과 협력해야 한다면 Screening은 영화 요금 계산과 관련된 책임 일부를 떠안아야 할 것이다. 이 경우 Screening은 DiscountCondition이 할인 여부를 판단할 수 있고 Movie가 이 할인 여부를 필요로 한다는 사실 역시 알고 있어야 한다. 다시 말해서 예매 요금을 계산하는 방식이 변경될 경우 Screening도 함께 변경해야 한다. 결과적으로 Screening은 서로 다른 이유로 변경되는 책임을 짊어지게 되므로 **응집도가 낮아질 수밖에 없다**.

반면 Movie의 주된 책임은 영화 요금을 계산하는 것이다. 따라서 영화 요금을 계산하는 데 필요한 할인 조건을 판단하기 위해 Movie가 DiscountCondition과 협력하는 것은 응집도에 아무런 해도 끼치지 않는다.

LOW COUPLING 패턴과 HIGH COHESION 패턴은 설계를 진행하면서 책임과 협력의 품질을 검토하는 데 사용할 수 있는 중요한 **평가 기준**이다. 책임을 할당하고 코드를 작성하는 매 순간마다 LOW COUPLING과 HIGH COHESION의 관점에서 전체적인 설계 품질을 검토하면 단순하면서도 재사용 가능하고 유연한 설계를 얻을 수 있다.

### 2.4 CREATOR 패턴: 창조자에게 객체 생성 책임을 할당하라

영화 예매 협력의 최종 결과물은 Reservation 인스턴스를 생성하는 것이다. 이것은 협력에 참여하는 어떤 객체에게는 Reservation 인스턴스를 생성할 책임을 할당해야 한다는 것을 의미한다. GRASP의 **CREATOR(창조자) 패턴**은 이 같은 경우에 사용할 수 있는 책임 할당 패턴으로서 객체를 생성할 책임을 어떤 객체에게 할당할지에 대한 지침을 제공한다.

> **CREATOR 패턴**
>
> 객체 A를 생성해야 할 때 어떤 객체에게 객체 생성 책임을 할당해야 하는가? 아래 조건을 최대한 많이 만족하는 B에게 객체 생성 책임을 할당하라.
>
> - B가 A 객체를 포함하거나 참조한다.
> - B가 A 객체를 기록한다.
> - B가 A 객체를 긴밀하게 사용한다.
> - B가 A 객체를 초기화하는 데 필요한 데이터를 가지고 있다(이 경우 B는 A에 대한 정보 전문가다).

CREATOR 패턴의 의도는 어떤 방식으로든 생성되는 객체와 연결되거나 관련될 필요가 있는 객체에 해당 객체를 생성할 책임을 맡기는 것이다. 이미 결합돼 있는 객체에게 생성 책임을 할당하는 것은 설계의 전체적인 결합도에 영향을 미치지 않는다. 결과적으로 CREATOR 패턴은 이미 존재하는 객체 사이의 관계를 이용하기 때문에 설계가 낮은 결합도를 유지할 수 있게 한다.

Reservation을 잘 알고 있거나, 긴밀하게 사용하거나, 초기화에 필요한 데이터를 가지고 있는 객체는 바로 **Screening**이다. Screening은 예매 정보를 생성하는 데 필요한 영화, 상영 시간, 상영 순번 등의 정보에 대한 전문가이며, 예매 요금을 계산하는 데 필수적인 Movie도 알고 있다.

```
──── 1: 예매하라 ────▶ Screening ──── 2: 가격을 계산하라 ────▶ Movie
                           │                                     │
                    «creates»                       3: 할인 여부를 판단하라
                           │                                     │
                           ▼                                     ▼
                      Reservation                         DiscountCondition
```

대략적으로나마 영화 예매에 필요한 책임을 객체들에게 할당했다. 현재까지의 책임 분배는 설계를 시작하기 위한 대략적인 스케치에 불과하다. **실제 설계는 코드를 작성하는 동안 이뤄진다**. 그리고 협력과 책임이 제대로 동작하는지 확인할 수 있는 유일한 방법은 코드를 작성하고 실행해 보는 것뿐이다.

---

## 3. 구현을 통한 검증

### 3.1 Screening 구현

Screening을 구현하는 것으로 시작하자. Screening은 영화를 예매할 책임을 맡으며 그 결과로 Reservation 인스턴스를 생성할 책임을 수행해야 한다. 다시 말해 Screening은 예매에 대한 정보 전문가인 동시에 Reservation의 창조자다.

협력의 관점에서 Screening은 `예매하라` 메시지에 응답할 수 있어야 한다. 또한 가격을 계산하기 위해 Movie에 `가격을 계산하라` 메시지를 전송해야 하기 때문에 영화(movie)에 대한 참조도 포함해야 한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Screening {
    private Movie movie;
    private int sequence;
    private LocalDateTime whenScreened;

    public Reservation reserve(Customer customer, int audienceCount) {
        return new Reservation(customer, this, calculateFee(audienceCount), audienceCount);
    }

    private Money calculateFee(int audienceCount) {
        return movie.calculateMovieFee(this).times(audienceCount);
    }
}
```

</details>

```typescript
// TypeScript
class Screening {
    private movie: Movie;
    private sequence: number;
    private whenScreened: Date;

    constructor(movie: Movie, sequence: number, whenScreened: Date) {
        this.movie = movie;
        this.sequence = sequence;
        this.whenScreened = whenScreened;
    }

    reserve(customer: Customer, audienceCount: number): Reservation {
        return new Reservation(customer, this, this.calculateFee(audienceCount), audienceCount);
    }

    private calculateFee(audienceCount: number): Money {
        return this.movie.calculateMovieFee(this).times(audienceCount);
    }

    getWhenScreened(): Date {
        return this.whenScreened;
    }

    getSequence(): number {
        return this.sequence;
    }
}
```

Screening을 구현하는 과정에서 Movie에 전송하는 메시지의 시그니처를 `calculateMovieFee(screening: Screening)`으로 선언했다는 사실에 주목하라. 이 메시지는 수신자인 Movie가 아니라 **송신자인 Screening의 의도를 표현한다**. 여기서 중요한 것은 Screening이 Movie의 내부 구현에 대한 어떤 지식도 없이 전송할 메시지를 결정했다는 것이다. 이처럼 Movie의 구현을 고려하지 않고 필요한 메시지를 결정하면 Movie의 내부 구현을 깔끔하게 캡슐화할 수 있다.

### 3.2 Movie 구현

Movie는 `calculateMovieFee` 메시지에 응답하기 위해 요금을 계산하는 메서드를 구현해야 한다. 현재의 설계에서 할인 정책을 Movie의 일부로 구현하고 있기 때문에 할인 금액(discountAmount)과 할인 비율(discountPercent)을 Movie의 인스턴스 변수로 선언했다. 그리고 현재의 Movie가 어떤 할인 정책이 적용된 영화인지를 나타내기 위한 영화 종류(movieType)를 인스턴스 변수로 포함한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public enum MovieType {
    AMOUNT_DISCOUNT,    // 금액 할인 정책
    PERCENT_DISCOUNT,   // 비율 할인 정책
    NONE_DISCOUNT       // 미적용
}

public class Movie {
    private String title;
    private Duration runningTime;
    private Money fee;
    private List<DiscountCondition> discountConditions;

    private MovieType movieType;
    private Money discountAmount;
    private double discountPercent;

    public Money calculateMovieFee(Screening screening) {
        if (isDiscountable(screening)) {
            return fee.minus(calculateDiscountAmount());
        }
        return fee;
    }

    private boolean isDiscountable(Screening screening) {
        return discountConditions.stream()
                .anyMatch(condition -> condition.isSatisfiedBy(screening));
    }

    private Money calculateDiscountAmount() {
        switch (movieType) {
            case AMOUNT_DISCOUNT:
                return calculateAmountDiscountAmount();
            case PERCENT_DISCOUNT:
                return calculatePercentDiscountAmount();
            case NONE_DISCOUNT:
                return calculateNoneDiscountAmount();
        }
        throw new IllegalStateException();
    }

    private Money calculateAmountDiscountAmount() {
        return discountAmount;
    }

    private Money calculatePercentDiscountAmount() {
        return fee.times(discountPercent);
    }

    private Money calculateNoneDiscountAmount() {
        return Money.ZERO;
    }
}
```

</details>

```typescript
// TypeScript
enum MovieType {
    AMOUNT_DISCOUNT = "AMOUNT_DISCOUNT",     // 금액 할인 정책
    PERCENT_DISCOUNT = "PERCENT_DISCOUNT",   // 비율 할인 정책
    NONE_DISCOUNT = "NONE_DISCOUNT",         // 미적용
}

class Movie {
    private title: string;
    private runningTime: number;
    private fee: Money;
    private discountConditions: DiscountCondition[];

    private movieType: MovieType;
    private discountAmount: Money;
    private discountPercent: number;

    constructor(
        title: string,
        runningTime: number,
        fee: Money,
        movieType: MovieType,
        discountConditions: DiscountCondition[],
        discountAmount: Money = Money.ZERO,
        discountPercent: number = 0,
    ) {
        this.title = title;
        this.runningTime = runningTime;
        this.fee = fee;
        this.movieType = movieType;
        this.discountConditions = discountConditions;
        this.discountAmount = discountAmount;
        this.discountPercent = discountPercent;
    }

    calculateMovieFee(screening: Screening): Money {
        if (this.isDiscountable(screening)) {
            return this.fee.minus(this.calculateDiscountAmount());
        }
        return this.fee;
    }

    private isDiscountable(screening: Screening): boolean {
        return this.discountConditions.some((condition) => condition.isSatisfiedBy(screening));
    }

    private calculateDiscountAmount(): Money {
        switch (this.movieType) {
            case MovieType.AMOUNT_DISCOUNT:
                return this.discountAmount;
            case MovieType.PERCENT_DISCOUNT:
                return this.fee.times(this.discountPercent);
            case MovieType.NONE_DISCOUNT:
                return Money.ZERO;
        }
    }
}
```

### 3.3 DiscountCondition 구현

Movie는 각 DiscountCondition에 `할인 여부를 판단하라` 메시지를 전송한다. DiscountCondition은 이 메시지를 처리하기 위해 `isSatisfiedBy` 메서드를 구현해야 한다.

DiscountCondition은 기간 조건을 위한 요일(dayOfWeek), 시작 시간(startTime), 종료 시간(endTime)과 순번 조건을 위한 상영 순번(sequence)을 인스턴스 변수로 포함한다. 추가적으로 할인 조건의 종류(type)를 인스턴스 변수로 포함한다. `isSatisfiedBy` 메서드는 type의 값에 따라 적절한 메서드를 호출한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public enum DiscountConditionType {
    SEQUENCE,   // 순번 조건
    PERIOD      // 기간 조건
}

public class DiscountCondition {
    private DiscountConditionType type;
    private int sequence;
    private DayOfWeek dayOfWeek;
    private LocalTime startTime;
    private LocalTime endTime;

    public boolean isSatisfiedBy(Screening screening) {
        if (type == DiscountConditionType.PERIOD) {
            return isSatisfiedByPeriod(screening);
        }
        return isSatisfiedBySequence(screening);
    }

    private boolean isSatisfiedByPeriod(Screening screening) {
        return dayOfWeek.equals(screening.getWhenScreened().getDayOfWeek()) &&
                startTime.compareTo(screening.getWhenScreened().toLocalTime()) <= 0 &&
                endTime.compareTo(screening.getWhenScreened().toLocalTime()) >= 0;
    }

    private boolean isSatisfiedBySequence(Screening screening) {
        return sequence == screening.getSequence();
    }
}
```

</details>

```typescript
// TypeScript
enum DiscountConditionType {
    SEQUENCE = "SEQUENCE", // 순번 조건
    PERIOD = "PERIOD",     // 기간 조건
}

class DiscountCondition {
    private type: DiscountConditionType;
    private sequence: number;
    private dayOfWeek: number;
    private startTime: number; // 분 단위 (예: 600 = 10:00)
    private endTime: number;

    constructor(type: DiscountConditionType, sequence: number, dayOfWeek: number, startTime: number, endTime: number) {
        this.type = type;
        this.sequence = sequence;
        this.dayOfWeek = dayOfWeek;
        this.startTime = startTime;
        this.endTime = endTime;
    }

    isSatisfiedBy(screening: Screening): boolean {
        if (this.type === DiscountConditionType.PERIOD) {
            return this.isSatisfiedByPeriod(screening);
        }
        return this.isSatisfiedBySequence(screening);
    }

    private isSatisfiedByPeriod(screening: Screening): boolean {
        const whenScreened = screening.getWhenScreened();
        return whenScreened.getDay() === this.dayOfWeek &&
            this.startTime <= this.toMinutes(whenScreened) &&
            this.endTime >= this.toMinutes(whenScreened);
    }

    private isSatisfiedBySequence(screening: Screening): boolean {
        return this.sequence === screening.getSequence();
    }

    private toMinutes(date: Date): number {
        return date.getHours() * 60 + date.getMinutes();
    }
}
```

이제 구현이 완료됐다. 코드가 만족스러운가? 안타깝게도 방금 작성한 코드 안에는 마음을 불편하게 만드는 몇 가지 문제점이 숨어 있다.

---

## 4. DiscountCondition 개선하기

### 4.1 변경에 취약한 클래스의 징후

가장 큰 문제점은 **변경에 취약한 클래스**를 포함하고 있다는 것이다. 변경에 취약한 클래스란 코드를 수정해야 하는 이유를 하나 이상 가지는 클래스다. DiscountCondition은 다음과 같이 서로 다른 세 가지 이유로 변경될 수 있다.

| 변경 이유 | 수정 내용 |
|---|---|
| **새로운 할인 조건 추가** | `isSatisfiedBy` 메서드의 if~else 수정 + 새 속성 추가 가능 |
| **순번 조건 판단 로직 변경** | `isSatisfiedBySequence` 내부 구현 수정 + `sequence` 속성 변경 가능 |
| **기간 조건 판단 로직 변경** | `isSatisfiedByPeriod` 내부 구현 수정 + `dayOfWeek`, `startTime`, `endTime` 속성 변경 가능 |

DiscountCondition은 하나 이상의 변경 이유를 가지기 때문에 응집도가 낮다. 응집도가 낮다는 것은 서로 연관성이 없는 기능이나 데이터가 하나의 클래스 안에 뭉쳐져 있다는 것을 의미한다.

### 4.2 낮은 응집도를 판단하는 세 가지 징후

코드를 통해 변경의 이유를 파악할 수 있는 방법은 다음과 같다.

**첫 번째: 인스턴스 변수가 초기화되는 시점을 살펴보라.**

응집도가 높은 클래스는 인스턴스를 생성할 때 **모든 속성을 함께 초기화**한다. 반면 응집도가 낮은 클래스는 객체의 속성 중 일부만 초기화하고 일부는 초기화되지 않은 상태로 남겨진다.

DiscountCondition이 순번 조건을 표현하는 경우 sequence는 초기화되지만 dayOfWeek, startTime, endTime은 초기화되지 않는다. 반대로 기간 조건을 표현하는 경우에는 dayOfWeek, startTime, endTime은 초기화되지만 sequence는 초기화되지 않는다. 클래스의 속성이 서로 다른 시점에 초기화되거나 일부만 초기화된다는 것은 응집도가 낮다는 증거다.

**두 번째: 메서드들이 인스턴스 변수를 사용하는 방식을 살펴보라.**

모든 메서드가 객체의 모든 속성을 사용한다면 클래스의 응집도는 높다고 볼 수 있다. 반면 메서드들이 사용하는 속성에 따라 그룹이 나뉜다면 클래스의 응집도가 낮다고 볼 수 있다.

`isSatisfiedBySequence` 메서드는 sequence만 사용하고, `isSatisfiedByPeriod` 메서드는 dayOfWeek, startTime, endTime만 사용한다. 속성 그룹과 해당 그룹에 접근하는 메서드 그룹을 기준으로 코드를 분리해야 한다.

**세 번째: 클래스가 하나 이상의 이유로 변경돼야 한다면 응집도가 낮은 것이다.**

일반적으로 응집도가 낮은 클래스는 이 세 가지 문제를 동시에 가지는 경우가 대부분이다. DiscountCondition 클래스에는 낮은 응집도를 암시하는 세 가지 징후가 모두 들어 있다.

### 4.3 타입 분리하기

DiscountCondition의 가장 큰 문제는 순번 조건과 기간 조건이라는 두 개의 독립적인 타입이 하나의 클래스 안에 공존하고 있다는 점이다. 가장 먼저 떠오르는 해결 방법은 두 타입을 `SequenceCondition`과 `PeriodCondition`이라는 두 개의 클래스로 분리하는 것이다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class PeriodCondition {
    private DayOfWeek dayOfWeek;
    private LocalTime startTime;
    private LocalTime endTime;

    public PeriodCondition(DayOfWeek dayOfWeek, LocalTime startTime, LocalTime endTime) {
        this.dayOfWeek = dayOfWeek;
        this.startTime = startTime;
        this.endTime = endTime;
    }

    public boolean isSatisfiedBy(Screening screening) {
        return dayOfWeek.equals(screening.getWhenScreened().getDayOfWeek()) &&
                startTime.compareTo(screening.getWhenScreened().toLocalTime()) <= 0 &&
                endTime.compareTo(screening.getWhenScreened().toLocalTime()) >= 0;
    }
}

public class SequenceCondition {
    private int sequence;

    public SequenceCondition(int sequence) {
        this.sequence = sequence;
    }

    public boolean isSatisfiedBy(Screening screening) {
        return sequence == screening.getSequence();
    }
}
```

</details>

```typescript
// TypeScript
class PeriodCondition {
    private dayOfWeek: number;
    private startTime: number;
    private endTime: number;

    constructor(dayOfWeek: number, startTime: number, endTime: number) {
        this.dayOfWeek = dayOfWeek;
        this.startTime = startTime;
        this.endTime = endTime;
    }

    isSatisfiedBy(screening: Screening): boolean {
        const whenScreened = screening.getWhenScreened();
        return whenScreened.getDay() === this.dayOfWeek &&
            this.startTime <= this.toMinutes(whenScreened) &&
            this.endTime >= this.toMinutes(whenScreened);
    }

    private toMinutes(date: Date): number {
        return date.getHours() * 60 + date.getMinutes();
    }
}

class SequenceCondition {
    private sequence: number;

    constructor(sequence: number) {
        this.sequence = sequence;
    }

    isSatisfiedBy(screening: Screening): boolean {
        return this.sequence === screening.getSequence();
    }
}
```

클래스를 분리하면 앞에서 언급했던 문제점들이 모두 해결된다. 각 클래스는 자신의 모든 인스턴스 변수를 함께 초기화할 수 있다. 모든 메서드는 동일한 인스턴스 변수 그룹을 사용한다. 결과적으로 개별 클래스들의 응집도가 향상됐다.

### 4.4 새로운 문제: 두 클래스와의 협력

하지만 안타깝게도 클래스를 분리한 후에 새로운 문제가 나타났다. 수정 전에는 Movie와 협력하는 클래스는 DiscountCondition 하나뿐이었다. 그러나 수정 후에 Movie의 인스턴스는 SequenceCondition과 PeriodCondition이라는 두 개의 서로 다른 클래스의 인스턴스 모두와 협력할 수 있어야 한다.

### 나쁜 설계

첫 번째 방법은 Movie 클래스 안에서 두 목록을 따로 유지하는 것이다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Movie {
    private List<PeriodCondition> periodConditions;
    private List<SequenceCondition> sequenceConditions;

    private boolean isDiscountable(Screening screening) {
        return checkPeriodConditions(screening) || checkSequenceConditions(screening);
    }

    private boolean checkPeriodConditions(Screening screening) {
        return periodConditions.stream()
                .anyMatch(condition -> condition.isSatisfiedBy(screening));
    }

    private boolean checkSequenceConditions(Screening screening) {
        return sequenceConditions.stream()
                .anyMatch(condition -> condition.isSatisfiedBy(screening));
    }
}
```

</details>

```typescript
// TypeScript
class Movie {
    private periodConditions: PeriodCondition[];
    private sequenceConditions: SequenceCondition[];

    private isDiscountable(screening: Screening): boolean {
        return this.checkPeriodConditions(screening) || this.checkSequenceConditions(screening);
    }

    private checkPeriodConditions(screening: Screening): boolean {
        return this.periodConditions.some((condition) => condition.isSatisfiedBy(screening));
    }

    private checkSequenceConditions(screening: Screening): boolean {
        return this.sequenceConditions.some((condition) => condition.isSatisfiedBy(screening));
    }
}
```

하지만 이 방법은 새로운 문제를 야기한다.

1. **결합도 상승**: Movie 클래스가 PeriodCondition과 SequenceCondition 클래스 양쪽 모두에게 결합된다. 수정 전에는 DiscountCondition이라는 하나의 클래스에만 결합돼 있었다.
2. **확장 어려움**: 새로운 할인 조건을 추가하려면 새로운 List를 Movie의 인스턴스 변수로 추가하고, 이 List를 이용해 할인 조건 만족 여부를 판단하는 메서드도 추가하고, isDiscountable 메서드도 수정해야 한다.

클래스를 분리하기 전에는 DiscountCondition의 내부 구현만 수정하면 Movie에는 아무런 영향도 미치지 않았다. 하지만 수정 후에는 할인 조건을 추가하려면 Movie도 함께 수정해야 한다. DiscountCondition의 입장에서 보면 응집도가 높아졌지만, 변경과 캡슐화라는 관점에서 보면 전체적으로 설계의 품질이 나빠지고 만 것이다.

### 좋은 설계

### 4.5 다형성을 통해 분리하기 - POLYMORPHISM 패턴

사실 Movie의 입장에서 보면 SequenceCondition과 PeriodCondition은 아무 차이도 없다. 둘 모두 할인 여부를 판단하는 **동일한 책임**을 수행하고 있을 뿐이다. 할인 가능 여부를 반환해 주기만 하면 Movie는 객체가 SequenceCondition의 인스턴스인지, PeriodCondition의 인스턴스인지는 상관하지 않는다.

이 시점이 되면 자연스럽게 **역할**의 개념이 등장한다. Movie의 입장에서 SequenceCondition과 PeriodCondition이 동일한 책임을 수행한다는 것은 동일한 역할을 수행한다는 것을 의미한다. 역할은 협력 안에서 대체 가능성을 의미하기 때문에 역할의 개념을 적용하면 Movie가 구체적인 클래스는 알지 못한 채 오직 역할에 대해서만 결합되도록 의존성을 제한할 수 있다.

역할을 사용하면 객체의 구체적인 타입을 추상화할 수 있다. 자바에서는 일반적으로 역할을 구현하기 위해 추상 클래스나 인터페이스를 사용한다. 역할을 대체할 클래스들 사이에서 구현을 공유해야 할 필요가 있다면 추상 클래스를 사용하면 된다. 구현을 공유할 필요 없이 역할을 대체하는 객체들의 책임만 정의하고 싶다면 인터페이스를 사용하면 된다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public interface DiscountCondition {
    boolean isSatisfiedBy(Screening screening);
}

public class PeriodCondition implements DiscountCondition { ... }
public class SequenceCondition implements DiscountCondition { ... }
```

</details>

```typescript
// TypeScript
interface DiscountCondition {
    isSatisfiedBy(screening: Screening): boolean;
}

class PeriodCondition implements DiscountCondition { /* ... */ }
class SequenceCondition implements DiscountCondition { /* ... */ }
```

이제 Movie는 협력하는 객체의 구체적인 타입을 몰라도 상관없다. 협력하는 객체가 DiscountCondition 역할을 수행할 수 있고 `isSatisfiedBy` 메시지를 이해할 수 있다는 사실만 알고 있어도 충분하다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Movie {
    private List<DiscountCondition> discountConditions;

    public Money calculateMovieFee(Screening screening) {
        if (isDiscountable(screening)) {
            return fee.minus(calculateDiscountAmount());
        }
        return fee;
    }

    private boolean isDiscountable(Screening screening) {
        return discountConditions.stream()
                .anyMatch(condition -> condition.isSatisfiedBy(screening));
    }
}
```

</details>

```typescript
// TypeScript
class Movie {
    private discountConditions: DiscountCondition[];

    calculateMovieFee(screening: Screening): Money {
        if (this.isDiscountable(screening)) {
            return this.fee.minus(this.calculateDiscountAmount());
        }
        return this.fee;
    }

    private isDiscountable(screening: Screening): boolean {
        return this.discountConditions.some((condition) => condition.isSatisfiedBy(screening));
    }
}
```

Movie가 전송한 메시지를 수신한 객체의 구체적인 클래스가 무엇인가에 따라 적절한 메서드가 실행된다. 즉, Movie와 DiscountCondition 사이의 협력은 **다형적**이다.

```
┌───────────┐       ┌───────────────────┐       ┌──────────────────────┐
│ Screening │──────▶│       Movie       │──────▶│ «interface»          │
│ reserve() │ movie │calculateMovieFee()│       │ DiscountCondition    │
└───────────┘       └───────────────────┘       │ isSatisfiedBy()      │
                                                └──────────┬───────────┘
                                                           │
                                              ┌────────────┴────────────┐
                                              │                         │
                                    ┌─────────┴──────────┐  ┌──────────┴─────────┐
                                    │ SequenceCondition   │  │ PeriodCondition    │
                                    │ isSatisfiedBy()     │  │ isSatisfiedBy()    │
                                    └────────────────────┘  └────────────────────┘
```

객체의 암시적인 타입에 따라 행동을 분기해야 한다면 암시적인 타입을 명시적인 클래스로 정의하고 행동을 나눔으로써 응집도 문제를 해결할 수 있다. 다시 말해 **객체의 타입에 따라 변하는 행동이 있다면 타입을 분리하고 변화하는 행동을 각 타입의 책임으로 할당하라**는 것이다. GRASP에서는 이를 **POLYMORPHISM(다형성) 패턴**이라고 부른다.

> **POLYMORPHISM 패턴**
>
> 객체의 타입에 따라 변하는 로직이 있을 때 변하는 로직을 담당할 책임을 어떻게 할당해야 하는가? **타입을 명시적으로 정의하고 각 타입에 다형적으로 행동하는 책임을 할당하라.**
>
> if~else 또는 switch~case 등의 조건 논리를 사용해서 설계한다면 새로운 변화가 일어난 경우 조건 논리를 수정해야 한다. 이것은 프로그램을 수정하기 어렵고 변경에 취약하게 만든다. POLYMORPHISM 패턴은 다형성을 이용해 새로운 변화를 다루기 쉽게 확장하라고 권고한다.

### 4.6 변경으로부터 보호하기 - PROTECTED VARIATIONS 패턴

SequenceCondition은 순번 조건의 구현 방법이 변경될 경우에만 수정된다. PeriodCondition은 기간 조건의 구현 방법이 변경될 경우에만 수정된다. 두 개의 서로 다른 변경이 두 개의 서로 다른 클래스 안으로 캡슐화된다.

새로운 할인 조건을 추가하는 경우에는 어떻게 될까? DiscountCondition이라는 역할이 Movie로부터 PeriodCondition과 SequenceCondition의 존재를 감춘다는 사실에 주목하라. DiscountCondition이라는 추상화가 구체적인 타입을 캡슐화한다. Movie의 관점에서 DiscountCondition의 타입이 캡슐화된다는 것은 **새로운 DiscountCondition 타입을 추가하더라도 Movie가 영향을 받지 않는다**는 것을 의미한다. 오직 DiscountCondition 인터페이스를 구현하는 클래스를 추가하는 것으로 할인 조건의 종류를 확장할 수 있다.

이처럼 변경을 캡슐화하도록 책임을 할당하는 것을 GRASP에서는 **PROTECTED VARIATIONS(변경 보호) 패턴**이라고 부른다.

> **PROTECTED VARIATIONS 패턴**
>
> 객체, 서브시스템, 그리고 시스템을 어떻게 설계해야 변화와 불안정성이 다른 요소에 나쁜 영향을 미치지 않도록 방지할 수 있을까? **변화가 예상되는 불안정한 지점들을 식별하고 그 주위에 안정된 인터페이스를 형성하도록 책임을 할당하라.**

PROTECTED VARIATIONS 패턴은 책임 할당의 관점에서 캡슐화를 설명한 것이다. "설계에서 변하는 것이 무엇인지 고려하고 변하는 개념을 캡슐화하라[GOF94]"라는 객체지향의 오랜 격언은 PROTECTED VARIATIONS 패턴의 본질을 잘 설명해 준다. **우리가 캡슐화해야 하는 것은 변경이다. 변경이 될 가능성이 높은가? 그렇다면 캡슐화하라.**

하나의 클래스가 여러 타입의 행동을 구현하고 있는 것처럼 보인다면 클래스를 분해하고 POLYMORPHISM 패턴에 따라 책임을 분산시켜라. 예측 가능한 변경으로 인해 여러 클래스들이 불안정해진다면 PROTECTED VARIATIONS 패턴에 따라 안정적인 인터페이스 뒤로 변경을 캡슐화하라.

---

## 5. Movie 클래스 개선하기

### 5.1 Movie의 문제점

안타깝게도 Movie 역시 DiscountCondition과 동일한 문제로 몸살을 앓고 있다. 금액 할인 정책 영화와 비율 할인 정책 영화라는 **두 가지 타입을 하나의 클래스 안에 구현하고 있기 때문에** 하나 이상의 이유로 변경될 수 있다. 한마디로 말해서 응집도가 낮다.

### 5.2 POLYMORPHISM 패턴 적용: 추상 클래스 활용

해결 방법 역시 DiscountCondition과 동일하다. 역할의 개념을 도입해서 협력을 다형적으로 만들면 된다. POLYMORPHISM 패턴을 사용해 서로 다른 행동을 타입별로 분리하면 다형성의 혜택을 누릴 수 있다.

DiscountCondition의 경우에는 역할을 수행할 클래스들 사이에 구현을 공유할 필요가 없었기 때문에 인터페이스를 이용해 구현했다. Movie의 경우에는 **구현을 공유할 필요가 있다**. 따라서 추상 클래스를 이용해 역할을 구현하자.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public abstract class Movie {
    private String title;
    private Duration runningTime;
    private Money fee;
    private List<DiscountCondition> discountConditions;

    public Movie(String title, Duration runningTime, Money fee,
                 DiscountCondition... discountConditions) {
        this.title = title;
        this.runningTime = runningTime;
        this.fee = fee;
        this.discountConditions = Arrays.asList(discountConditions);
    }

    public Money calculateMovieFee(Screening screening) {
        if (isDiscountable(screening)) {
            return fee.minus(calculateDiscountAmount());
        }
        return fee;
    }

    private boolean isDiscountable(Screening screening) {
        return discountConditions.stream()
                .anyMatch(condition -> condition.isSatisfiedBy(screening));
    }

    abstract protected Money calculateDiscountAmount();

    protected Money getFee() {
        return fee;
    }
}
```

</details>

```typescript
// TypeScript
abstract class Movie {
    private title: string;
    private runningTime: number;
    protected fee: Money;
    private discountConditions: DiscountCondition[];

    constructor(
        title: string,
        runningTime: number,
        fee: Money,
        ...discountConditions: DiscountCondition[]
    ) {
        this.title = title;
        this.runningTime = runningTime;
        this.fee = fee;
        this.discountConditions = discountConditions;
    }

    calculateMovieFee(screening: Screening): Money {
        if (this.isDiscountable(screening)) {
            return this.fee.minus(this.calculateDiscountAmount());
        }
        return this.fee;
    }

    private isDiscountable(screening: Screening): boolean {
        return this.discountConditions.some((condition) => condition.isSatisfiedBy(screening));
    }

    protected abstract calculateDiscountAmount(): Money;
}
```

변경 전의 Movie 클래스와 비교해서 discountAmount, discountPercent와 이 인스턴스 변수들을 사용하는 메서드들이 삭제됐다. 이 인스턴스 변수들과 메서드들을 Movie 역할을 수행하는 적절한 자식 클래스로 옮길 것이다.

할인 정책의 종류에 따라 할인 금액을 계산하는 로직이 달라져야 한다. 이를 위해 `calculateDiscountAmount` 메서드를 추상 메서드로 선언함으로써 서브클래스들이 할인 금액을 계산하는 방식을 원하는 대로 오버라이딩할 수 있게 했다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class AmountDiscountMovie extends Movie {
    private Money discountAmount;

    public AmountDiscountMovie(String title, Duration runningTime,
            Money fee, Money discountAmount, DiscountCondition... discountConditions) {
        super(title, runningTime, fee, discountConditions);
        this.discountAmount = discountAmount;
    }

    @Override
    protected Money calculateDiscountAmount() {
        return discountAmount;
    }
}

public class PercentDiscountMovie extends Movie {
    private double percent;

    public PercentDiscountMovie(String title, Duration runningTime,
            Money fee, double percent, DiscountCondition... discountConditions) {
        super(title, runningTime, fee, discountConditions);
        this.percent = percent;
    }

    @Override
    protected Money calculateDiscountAmount() {
        return getFee().times(percent);
    }
}

public class NoneDiscountMovie extends Movie {
    public NoneDiscountMovie(String title, Duration runningTime, Money fee) {
        super(title, runningTime, fee);
    }

    @Override
    protected Money calculateDiscountAmount() {
        return Money.ZERO;
    }
}
```

</details>

```typescript
// TypeScript
class AmountDiscountMovie extends Movie {
    private discountAmount: Money;

    constructor(
        title: string,
        runningTime: number,
        fee: Money,
        discountAmount: Money,
        ...discountConditions: DiscountCondition[]
    ) {
        super(title, runningTime, fee, ...discountConditions);
        this.discountAmount = discountAmount;
    }

    protected calculateDiscountAmount(): Money {
        return this.discountAmount;
    }
}

class PercentDiscountMovie extends Movie {
    private percent: number;

    constructor(
        title: string,
        runningTime: number,
        fee: Money,
        percent: number,
        ...discountConditions: DiscountCondition[]
    ) {
        super(title, runningTime, fee, ...discountConditions);
        this.percent = percent;
    }

    protected calculateDiscountAmount(): Money {
        return this.fee.times(this.percent);
    }
}

class NoneDiscountMovie extends Movie {
    constructor(title: string, runningTime: number, fee: Money) {
        super(title, runningTime, fee);
    }

    protected calculateDiscountAmount(): Money {
        return Money.ZERO;
    }
}
```

### 5.3 최종 설계 구조

```
┌───────────┐ movie ┌──────────────────────────────┐         ┌────────────────────┐
│ Screening │──────▶│     «abstract» Movie         │────────▶│ «interface»        │
│ reserve() │       │ calculateMovieFee()           │         │ DiscountCondition  │
└───────────┘       │ # calculateDiscountAmount()   │         │ isSatisfiedBy()    │
                    └──────────────┬────────────────┘         └─────────┬──────────┘
                                   │                                    │
                    ┌──────────────┼──────────────┐         ┌──────────┴──────────┐
                    │              │              │         │                     │
            ┌───────┴──────┐ ┌────┴─────┐ ┌──────┴───┐ ┌───┴──────────┐ ┌───────┴─────┐
            │ Amount       │ │ Percent  │ │ None     │ │ Sequence     │ │ Period      │
            │ Discount     │ │ Discount │ │ Discount │ │ Condition    │ │ Condition   │
            │ Movie        │ │ Movie    │ │ Movie    │ └──────────────┘ └─────────────┘
            └──────────────┘ └──────────┘ └──────────┘
```

모든 클래스의 내부 구현은 캡슐화돼 있고 모든 클래스는 변경의 이유를 오직 하나씩만 가진다. 각 클래스는 응집도가 높고 다른 클래스와 최대한 느슨하게 결합돼 있다. 클래스는 작고 오직 한 가지 일만 수행한다. 책임은 적절하게 분배돼 있다. 이것이 **책임을 중심으로 협력을 설계할 때 얻을 수 있는 혜택**이다.

> 도메인 모델은 단순히 설계에 필요한 용어를 제공하는 것을 넘어 코드의 구조에도 영향을 미친다. 여기서 강조하고 싶은 것은 변경 역시 도메인 모델의 일부라는 것이다. 도메인 모델에는 도메인 안에서 변하는 개념과 이들 사이의 관계가 투영돼 있어야 한다. 구현을 가이드할 수 있는 도메인 모델을 선택하라. 객체지향은 도메인의 개념과 구조를 반영한 코드를 가능하게 만들기 때문에 도메인의 구조가 코드의 구조를 이끌어 내는 것은 자연스러울 뿐만 아니라 바람직한 것이다.

---

## 6. 변경과 유연성

설계를 주도하는 것은 변경이다. 개발자로서 변경에 대비할 수 있는 두 가지 방법이 있다.

| 접근 방식 | 전략 | 적합한 상황 |
|---|---|---|
| **단순한 설계** | 코드를 이해하고 수정하기 쉽도록 최대한 단순하게 설계 | 대부분의 경우 (기본 전략) |
| **유연한 설계** | 코드를 수정하지 않고도 변경을 수용할 수 있도록 유연하게 설계 | 유사한 변경이 반복적으로 발생하는 경우 |

예를 들어, 영화에 설정된 할인 정책을 **실행 중에 변경할 수 있어야 한다**는 요구사항이 추가됐다고 가정해 보자. 현재의 설계에서는 할인 정책을 구현하기 위해 상속을 이용하고 있기 때문에 실행 중에 영화의 할인 정책을 변경하기 위해서는 새로운 인스턴스를 생성한 후 필요한 정보를 복사해야 한다. 또한 변경 전후의 인스턴스가 개념적으로는 동일한 객체를 가리키지만 물리적으로 서로 다른 객체이기 때문에 식별자의 관점에서 혼란스러울 수 있다.

해결 방법은 **상속 대신 합성을 사용하는 것**이다. Movie의 상속 계층 안에 구현된 할인 정책을 독립적인 DiscountPolicy로 분리한 후 Movie에 합성시키면 유연한 설계가 완성된다. 이것이 바로 2장에서 살펴본 영화 예매 시스템의 전체 구조다.

```
┌───────────┐ movie  ┌────────────┐ discountPolicy ┌────────────────────────┐
│ Screening │───────▶│   Movie    │───────────────▶│ «abstract»             │
│ reserve() │        │ calculate  │                │ DiscountPolicy         │
└───────────┘        │ MovieFee() │                │ calculateDiscountAmount │
                     └────────────┘                │ # getDiscountAmount()  │
                                                   └───────────┬────────────┘
                                                               │
                                              ┌────────────────┼────────────────┐
                                              │                │                │
                                    ┌─────────┴──────┐ ┌──────┴───────┐ ┌──────┴──────┐
                                    │ Amount         │ │ Percent      │ │ None        │
                                    │ DiscountPolicy │ │ DiscountPolicy│ │ DiscountPolicy│
                                    └────────────────┘ └──────────────┘ └─────────────┘
```

이제 금액 할인 정책이 적용된 영화를 비율 할인 정책으로 바꾸는 일은 Movie에 연결된 DiscountPolicy의 인스턴스를 교체하는 단순한 작업으로 바뀐다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
Movie movie = new Movie("타이타닉",
        Duration.ofMinutes(120),
        Money.wons(10000),
        new AmountDiscountPolicy(...));

movie.changeDiscountPolicy(new PercentDiscountPolicy(...));
```

</details>

```typescript
// TypeScript
const movie = new Movie(
    "타이타닉",
    120,
    Money.wons(10000),
    new AmountDiscountPolicy(/* ... */),
);

movie.changeDiscountPolicy(new PercentDiscountPolicy(/* ... */));
```

합성을 사용한 예제의 경우 새로운 할인 정책이 추가되더라도 할인 정책을 변경하는 데 필요한 추가적인 코드를 작성할 필요가 없다. 새로운 클래스를 추가하고 클래스의 인스턴스를 Movie의 `changeDiscountPolicy` 메서드에 전달하면 된다.

> **핵심 통찰**: 유연성은 의존성 관리의 문제다. 요소들 사이의 의존성의 정도가 유연성의 정도를 결정한다. 유연성의 정도를 조절할 수 있는 능력은 객체지향 개발자가 갖춰야 하는 중요한 기술 중 하나다.

> 코드의 구조가 바뀌면 도메인에 대한 관점도 함께 바뀐다. 도메인 모델은 단순히 도메인의 개념과 관계를 모아 놓은 것이 아니다. 도메인 모델은 구현과 밀접한 관계를 맺어야 한다. 도메인 모델은 코드에 대한 가이드를 제공할 수 있어야 하며 코드의 변화에 발맞춰 함께 변화해야 한다.

---

## 7. 책임 주도 설계의 대안

책임 주도 설계에 익숙해지기 위해서는 부단한 노력과 시간이 필요하다. 어느 정도 경험을 쌓은 숙련된 설계자조차도 적절한 책임과 객체를 선택하는 일에 어려움을 느끼곤 한다.

> 객체 디자인에서 가장 기본이 되는 것 중의 하나는 책임을 어디에 둘지를 결정하는 것이다. 나는 십년 이상 객체를 가지고 일했지만 처음 시작할 때는 여전히 적당한 위치를 찾지 못한다. 늘 이런 점이 나를 괴롭혔지만, 이제는 이런 경우에 리팩터링을 사용하면 된다는 것을 알게 되었다. - Martin Fowler

책임과 객체 사이에서 방황할 때 돌파구를 찾기 위해 선택하는 방법은 **최대한 빠르게 목적한 기능을 수행하는 코드를 작성하는 것**이다. 일단 실행되는 코드를 얻고 난 후에 코드 상에 명확하게 드러나는 책임들을 올바른 위치로 이동시키는 것이다.

주의할 점은 코드를 수정한 후에 겉으로 드러나는 동작이 바뀌어서는 안 된다는 것이다. 캡슐화를 향상시키고, 응집도를 높이고, 결합도를 낮춰야 하지만 동작은 그대로 유지해야 한다. 이처럼 이해하기 쉽고 수정하기 쉬운 소프트웨어로 개선하기 위해 겉으로 보이는 동작은 바꾸지 않은 채 내부 구조를 변경하는 것을 **리팩터링**(*Refactoring*)이라고 부른다.

### 7.1 메서드 응집도

데이터 중심으로 설계된 영화 예매 시스템에서 모든 절차는 ReservationAgency에 집중돼 있었다. 이 클래스의 reserve 메서드는 길이가 너무 길고 이해하기도 어렵다.

긴 메서드는 다양한 측면에서 코드의 유지보수에 부정적인 영향을 미친다.

- 어떤 일을 수행하는지 한눈에 파악하기 어렵기 때문에 코드를 전체적으로 이해하는 데 너무 많은 시간이 걸린다.
- 하나의 메서드 안에서 너무 많은 작업을 처리하기 때문에 변경이 필요할 때 수정해야 할 부분을 찾기 어렵다.
- 메서드 내부의 일부 로직만 수정하더라도 메서드의 나머지 부분에서 버그가 발생할 확률이 높다.
- 로직의 일부만 재사용하는 것이 불가능하다.
- 코드를 재사용하는 유일한 방법은 원하는 코드를 복사해서 붙여넣는 것뿐이므로 코드 중복을 초래하기 쉽다.

한마디로 말해서 긴 메서드는 응집도가 낮기 때문에 이해하기도 어렵고 재사용하기도 어려우며 변경하기도 어렵다. 마이클 페더스(Michael Feathers)는 이런 메서드를 **몬스터 메서드**(*Monster Method*)라고 부른다.

응집도가 낮은 메서드는 로직의 흐름을 이해하기 위해 주석이 필요한 경우가 대부분이다. **주석을 추가하는 대신 메서드를 작게 분해해서 각 메서드의 응집도를 높여라.**

객체로 책임을 분배할 때 가장 먼저 할 일은 메서드를 응집도 있는 수준으로 분해하는 것이다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class ReservationAgency {
    public Reservation reserve(Screening screening, Customer customer, int audienceCount) {
        boolean discountable = checkDiscountable(screening);
        Money fee = calculateFee(screening, discountable, audienceCount);
        return createReservation(screening, customer, audienceCount, fee);
    }

    private boolean checkDiscountable(Screening screening) {
        return screening.getMovie().getDiscountConditions().stream()
                .anyMatch(condition -> isDiscountable(condition, screening));
    }

    private boolean isDiscountable(DiscountCondition condition, Screening screening) {
        if (condition.getType() == DiscountConditionType.PERIOD) {
            return isSatisfiedByPeriod(condition, screening);
        }
        return isSatisfiedBySequence(condition, screening);
    }

    private boolean isSatisfiedByPeriod(DiscountCondition condition, Screening screening) {
        return screening.getWhenScreened().getDayOfWeek().equals(condition.getDayOfWeek()) &&
                condition.getStartTime().compareTo(screening.getWhenScreened().toLocalTime()) <= 0 &&
                condition.getEndTime().compareTo(screening.getWhenScreened().toLocalTime()) >= 0;
    }

    private boolean isSatisfiedBySequence(DiscountCondition condition, Screening screening) {
        return condition.getSequence() == screening.getSequence();
    }

    private Money calculateFee(Screening screening, boolean discountable, int audienceCount) {
        if (discountable) {
            return screening.getMovie().getFee()
                    .minus(calculateDiscountedFee(screening.getMovie()))
                    .times(audienceCount);
        }
        return screening.getMovie().getFee().times(audienceCount);
    }

    private Money calculateDiscountedFee(Movie movie) {
        switch (movie.getMovieType()) {
            case AMOUNT_DISCOUNT:
                return movie.getDiscountAmount();
            case PERCENT_DISCOUNT:
                return movie.getFee().times(movie.getDiscountPercent());
            case NONE_DISCOUNT:
                return Money.ZERO;
        }
        throw new IllegalArgumentException();
    }

    private Reservation createReservation(Screening screening,
            Customer customer, int audienceCount, Money fee) {
        return new Reservation(customer, screening, fee, audienceCount);
    }
}
```

</details>

```typescript
// TypeScript
class ReservationAgency {
    reserve(screening: Screening, customer: Customer, audienceCount: number): Reservation {
        const discountable = this.checkDiscountable(screening);
        const fee = this.calculateFee(screening, discountable, audienceCount);
        return this.createReservation(screening, customer, audienceCount, fee);
    }

    private checkDiscountable(screening: Screening): boolean {
        return screening.getMovie().getDiscountConditions()
            .some((condition) => this.isDiscountable(condition, screening));
    }

    private isDiscountable(condition: DiscountCondition, screening: Screening): boolean {
        if (condition.getType() === DiscountConditionType.PERIOD) {
            return this.isSatisfiedByPeriod(condition, screening);
        }
        return this.isSatisfiedBySequence(condition, screening);
    }

    private isSatisfiedByPeriod(condition: DiscountCondition, screening: Screening): boolean {
        const whenScreened = screening.getWhenScreened();
        return whenScreened.getDay() === condition.getDayOfWeek() &&
            condition.getStartTime() <= this.toMinutes(whenScreened) &&
            condition.getEndTime() >= this.toMinutes(whenScreened);
    }

    private isSatisfiedBySequence(condition: DiscountCondition, screening: Screening): boolean {
        return condition.getSequence() === screening.getSequence();
    }

    private calculateFee(screening: Screening, discountable: boolean, audienceCount: number): Money {
        if (discountable) {
            return screening.getMovie().getFee()
                .minus(this.calculateDiscountedFee(screening.getMovie()))
                .times(audienceCount);
        }
        return screening.getMovie().getFee().times(audienceCount);
    }

    private calculateDiscountedFee(movie: Movie): Money {
        switch (movie.getMovieType()) {
            case MovieType.AMOUNT_DISCOUNT:
                return movie.getDiscountAmount();
            case MovieType.PERCENT_DISCOUNT:
                return movie.getFee().times(movie.getDiscountPercent());
            case MovieType.NONE_DISCOUNT:
                return Money.ZERO;
        }
    }

    private createReservation(
        screening: Screening, customer: Customer, audienceCount: number, fee: Money,
    ): Reservation {
        return new Reservation(customer, screening, fee, audienceCount);
    }

    private toMinutes(date: Date): number {
        return date.getHours() * 60 + date.getMinutes();
    }
}
```

이제 ReservationAgency 클래스는 오직 하나의 작업만 수행하고, 하나의 변경 이유만 가지는 작고, 명확하고, 응집도가 높은 메서드들로 구성돼 있다. 비록 클래스의 길이는 더 길어졌지만 일반적으로 **명확성의 가치가 클래스의 길이보다 더 중요하다**.

일단 메서드를 분리하고 나면 public 메서드는 상위 수준의 명세를 읽는 것 같은 느낌이 든다.

```typescript
reserve(screening: Screening, customer: Customer, audienceCount: number): Reservation {
    const discountable = this.checkDiscountable(screening);
    const fee = this.calculateFee(screening, discountable, audienceCount);
    return this.createReservation(screening, customer, audienceCount, fee);
}
```

> 나는 다음과 같은 이유로 짧고 이해하기 쉬운 이름으로 된 메서드를 좋아한다. 첫째, 메서드가 잘게 나눠져 있을 때 다른 메서드에서 사용될 확률이 높아진다. 둘째, 고수준의 메서드를 볼 때 일련의 주석을 읽는 것 같은 느낌이 들게 할 수 있다. 또한 메서드가 잘게 나눠져 있을 때 오버라이딩하는 것도 훨씬 쉽다. 작은 메서드는 실제로 이름을 잘 지었을 때만 그 진가가 드러나므로, 이름을 지을 때 주의해야 한다.
>
> 중요한 것은 메서드의 이름과 메서드 몸체의 의미적 차이다. 뽑아내는 것이 코드를 더욱 명확하게 하면 새로 만든 메서드의 이름이 원래 코드의 길이보다 길어져도 뽑아낸다. - Martin Fowler

### 7.2 객체를 자율적으로 만들자

메서드들의 응집도 자체는 높아졌지만 이 메서드들을 담고 있는 ReservationAgency의 응집도는 여전히 낮다. ReservationAgency의 응집도를 높이기 위해서는 변경의 이유가 다른 메서드들을 적절한 위치로 분배해야 한다. 적절한 위치란 바로 **각 메서드가 사용하는 데이터를 정의하고 있는 클래스**를 의미한다.

어떤 메서드를 어떤 클래스로 이동시켜야 할까? 자신이 소유하고 있는 데이터를 자기 스스로 처리하도록 만드는 것이 자율적인 객체를 만드는 지름길이다. 따라서 **메서드가 사용하는 데이터를 저장하고 있는 클래스로 메서드를 이동시키면 된다**.

어떤 데이터를 사용하는지를 가장 쉽게 알 수 있는 방법은 메서드 안에서 어떤 클래스의 접근자 메서드를 사용하는지 파악하는 것이다. 예를 들어 `isDiscountable`, `isSatisfiedByPeriod`, `isSatisfiedBySequence` 메서드는 DiscountCondition의 접근자 메서드를 주로 이용한다. 따라서 이 메서드들을 DiscountCondition으로 이동하고 ReservationAgency에서 삭제하자.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class DiscountCondition {
    private DiscountConditionType type;
    private int sequence;
    private DayOfWeek dayOfWeek;
    private LocalTime startTime;
    private LocalTime endTime;

    public boolean isDiscountable(Screening screening) {
        if (type == DiscountConditionType.PERIOD) {
            return isSatisfiedByPeriod(screening);
        }
        return isSatisfiedBySequence(screening);
    }

    private boolean isSatisfiedByPeriod(Screening screening) {
        return screening.getWhenScreened().getDayOfWeek().equals(dayOfWeek) &&
                startTime.compareTo(screening.getWhenScreened().toLocalTime()) <= 0 &&
                endTime.compareTo(screening.getWhenScreened().toLocalTime()) >= 0;
    }

    private boolean isSatisfiedBySequence(Screening screening) {
        return sequence == screening.getSequence();
    }
}
```

</details>

```typescript
// TypeScript
class DiscountCondition {
    private type: DiscountConditionType;
    private sequence: number;
    private dayOfWeek: number;
    private startTime: number;
    private endTime: number;

    isDiscountable(screening: Screening): boolean {
        if (this.type === DiscountConditionType.PERIOD) {
            return this.isSatisfiedByPeriod(screening);
        }
        return this.isSatisfiedBySequence(screening);
    }

    private isSatisfiedByPeriod(screening: Screening): boolean {
        const whenScreened = screening.getWhenScreened();
        return whenScreened.getDay() === this.dayOfWeek &&
            this.startTime <= this.toMinutes(whenScreened) &&
            this.endTime >= this.toMinutes(whenScreened);
    }

    private isSatisfiedBySequence(screening: Screening): boolean {
        return this.sequence === screening.getSequence();
    }

    private toMinutes(date: Date): number {
        return date.getHours() * 60 + date.getMinutes();
    }
}
```

DiscountCondition의 `isDiscountable` 메서드는 외부에서 호출 가능해야 하므로 가시성을 private에서 public으로 변경했다. 기존의 isDiscountable 메서드는 DiscountCondition의 인스턴스를 인자로 받아야 했지만 이제 DiscountCondition의 일부가 됐기 때문에 인자로 전달받을 필요가 없어졌다. 이처럼 **메서드를 다른 클래스로 이동시킬 때는 인자에 정의된 클래스 중 하나로 이동하는 경우가 일반적**이다.

이제 DiscountCondition 내부에서만 DiscountCondition의 인스턴스 변수에 접근한다. 따라서 DiscountCondition에서 모든 접근자 메서드를 제거할 수 있다. 이를 통해 DiscountCondition의 내부 구현을 캡슐화할 수 있다. 또한 할인 조건을 계산하는 데 필요한 모든 로직이 DiscountCondition에 모여 있기 때문에 응집도 역시 높아졌다.

변경 후의 코드는 책임 주도 설계 방법을 적용해서 구현했던 DiscountCondition 클래스의 초기 모습과 유사해졌다. 여기에 POLYMORPHISM 패턴과 PROTECTED VARIATIONS 패턴을 차례대로 적용하면 최종 설계와 유사한 모습의 코드를 얻게 될 것이다.

> **핵심 통찰**: 책임 주도 설계 방법에 익숙하지 않다면 일단 데이터 중심으로 구현한 후 이를 리팩터링하더라도 유사한 결과를 얻을 수 있다. 처음부터 책임 주도 설계 방법을 따르는 것보다 동작하는 코드를 작성한 후에 리팩터링하는 것이 더 훌륭한 결과물을 낳을 수도 있다. 캡슐화, 결합도, 응집도를 이해하고 훌륭한 객체지향 원칙을 적용하기 위해 노력한다면 책임 주도 설계 방법을 단계적으로 따르지 않더라도 유연하고 깔끔한 코드를 얻을 수 있을 것이다.

---

## 리팩터링 과정

| 단계 | 변경 내용 | 핵심 효과 |
|---|---|---|
| **1단계** (GRASP 적용) | INFORMATION EXPERT에 따라 Screening, Movie, DiscountCondition에 책임 할당 | 메시지 기반 협력 구조 수립 |
| **2단계** (초기 구현) | 구현을 통해 검증. Movie에 movieType + switch, DiscountCondition에 type + if~else | 동작하지만 응집도 낮음 |
| **3단계** (DiscountCondition 개선) | 순번 조건/기간 조건을 별도 클래스로 분리 + DiscountCondition 인터페이스 도입 | POLYMORPHISM + PROTECTED VARIATIONS 적용 |
| **4단계** (Movie 개선) | Movie를 추상 클래스로, AmountDiscountMovie/PercentDiscountMovie/NoneDiscountMovie로 분리 | 할인 정책별 책임 분산 |
| **5단계** (유연성 확보) | 상속 대신 합성 사용. DiscountPolicy를 독립 객체로 분리하여 Movie에 합성 | 실행 중 할인 정책 변경 가능 |

---

## 설계 원칙

| 패턴/원칙 | 핵심 질문 | 지침 |
|---|---|---|
| **INFORMATION EXPERT** | 책임을 누구에게 할당할 것인가? | 필요한 정보를 가진 객체에게 할당하라 |
| **LOW COUPLING** | 어떻게 의존성을 낮출 것인가? | 전체적인 결합도가 낮게 유지되도록 책임을 할당하라 |
| **HIGH COHESION** | 어떻게 복잡성을 관리할 것인가? | 높은 응집도를 유지할 수 있게 책임을 할당하라 |
| **CREATOR** | 객체 생성 책임을 누구에게 할당할 것인가? | 생성할 객체와 가장 밀접한 관계의 객체에게 할당하라 |
| **POLYMORPHISM** | 타입에 따른 행동 변화를 어떻게 처리할 것인가? | 타입을 명시적으로 정의하고 다형적으로 책임을 할당하라 |
| **PROTECTED VARIATIONS** | 변경으로부터 어떻게 보호할 것인가? | 변화가 예상되는 지점에 안정된 인터페이스를 형성하라 |

---

## 요약

- **데이터가 아닌 책임에 초점을 맞춰라**: 객체를 설계할 때 "이 객체가 포함해야 하는 데이터가 무엇인가?"가 아니라 "이 객체가 수행해야 하는 책임은 무엇인가?"를 먼저 물어라.
- **메시지가 객체를 선택한다**: 객체를 결정한 후에 메시지를 선택하는 것이 아니라 메시지를 결정한 후에 메시지를 처리할 객체를 선택하라.
- **GRASP 패턴은 책임 할당의 지침이다**: INFORMATION EXPERT, CREATOR, LOW COUPLING, HIGH COHESION, POLYMORPHISM, PROTECTED VARIATIONS 등의 패턴은 객체에게 책임을 할당할 때 따라야 하는 원칙들이다.
- **응집도가 낮은 클래스의 징후**: 하나 이상의 변경 이유, 부분적 인스턴스 변수 초기화, 메서드-속성 그룹의 분리.
- **다형성으로 조건 논리를 대체하라**: if~else나 switch~case로 타입을 분기하는 대신 다형성을 이용해 각 타입에 책임을 할당하라.
- **변경을 캡슐화하라**: 변화가 예상되는 지점을 식별하고 안정된 인터페이스 뒤로 숨겨라.
- **유연성이 필요하면 합성을 사용하라**: 상속은 정적이지만 합성은 실행 중에 객체의 행동을 변경할 수 있다.
- **리팩터링은 유효한 대안이다**: 처음부터 완벽한 책임 주도 설계를 하지 못하더라도, 일단 동작하는 코드를 작성한 후 리팩터링을 통해 책임을 올바른 위치로 이동시킬 수 있다.

---

## 다른 챕터와의 관계

- **Chapter 2 (객체지향 프로그래밍)**: 이 장에서 GRASP 패턴을 적용해 도달한 최종 설계(추상 클래스 Movie + DiscountCondition 인터페이스)가 바로 2장에서 이미 소개한 영화 예매 시스템의 구조다. 2장에서 직관적으로 보여준 코드가 어떤 설계 원칙에 의해 그런 형태가 되었는지를 이 장에서 역추적한다.
- **Chapter 3 (역할, 책임, 협력)**: 이 장의 GRASP 패턴들은 3장에서 설명한 역할, 책임, 협력의 개념을 구체적인 설계 지침으로 형식화한 것이다. 특히 INFORMATION EXPERT 패턴은 "책임을 수행할 정보를 가진 객체에게 할당하라"는 3장의 원칙을 패턴화한 것이며, POLYMORPHISM 패턴은 역할의 대체 가능성을 구현 수준에서 실현하는 방법이다.
- **Chapter 4 (설계 품질과 트레이드오프)**: 4장에서 데이터 중심 설계의 문제점으로 지적한 낮은 응집도, 높은 결합도, 캡슐화 위반을 이 장에서 GRASP 패턴을 적용해 해결한다. 특히 7절의 "책임 주도 설계의 대안"에서 4장의 데이터 중심 코드를 리팩터링하여 책임 중심 코드로 전환하는 과정을 직접 보여준다.
- **Chapter 8 (의존성 관리하기)**: 이 장에서 강조하는 LOW COUPLING, HIGH COHESION 패턴은 8장의 의존성 관리 원칙과 직결된다. 특히 "유연성은 의존성 관리의 문제"라는 이 장의 결론이 8장에서 본격적으로 다뤄진다.
