# Chapter 1: Objects and Design (객체, 설계) - 요약

**핵심 질문**: 좋은 객체지향 설계란 무엇이며, 절차적 프로그래밍의 문제를 객체의 자율성과 캡슐화로 어떻게 해결하는가?

## 이론보다 실무가 먼저다

로버트 글래스는 어떤 분야든 이론을 정립할 수 없는 초기에는 **실무가 먼저 급속히 발전**하고, 실무가 어느 정도 쌓인 뒤에야 이론이 모습을 갖춘다고 말한다. 소프트웨어 설계가 그렇다. 훌륭한 설계에 관한 최초의 이론은 1970년대에야 등장했고, 대부분의 설계 원칙은 이론에서 실무로 내려온 것이 아니라 실무에서 반복되던 기법을 이론화한 것이다.

> **핵심 통찰**: 설계를 설명할 때 가장 유용한 도구는 이론으로 치장된 개념과 용어가 아니라 **코드** 그 자체다. 프로그래밍을 통해 개념을 배우는 것이 개념을 통해 프로그래밍을 배우는 것보다 낫다.

## 티켓 판매 시스템: 무엇이 문제인가

소극장에 관람객을 입장시키는 코드에서 출발한다. 이벤트 당첨자는 초대장을 티켓으로 교환하고, 일반 관람객은 티켓을 구매한다.

```typescript
// Before - Theater가 모든 처리를 도맡는다
class Theater {
    enter(audience: Audience): void {
        if (audience.getBag().hasInvitation()) {
            const ticket = this.ticketSeller.getTicketOffice().getTicket();
            audience.getBag().setTicket(ticket);
        } else {
            const ticket = this.ticketSeller.getTicketOffice().getTicket();
            audience.getBag().minusAmount(ticket.getFee());
            this.ticketSeller.getTicketOffice().plusAmount(ticket.getFee());
            audience.getBag().setTicket(ticket);
        }
    }
}
```

로직은 잘 동작한다. 그런데 로버트 마틴이 말한 모듈의 세 가지 목적 - 제대로 동작할 것, 변경이 용이할 것, 읽는 사람과 의사소통할 것 - 중 **첫 번째만** 만족한다.

**의사소통 문제**: 이 코드를 말로 풀면 "소극장이 관람객의 가방을 열어 초대장을 확인하고, 돈을 꺼내 매표소에 넣고, 티켓을 가방에 넣어 준다"가 된다. 현실에서는 관람객이 직접 돈을 꺼내 건네고 판매원이 직접 티켓을 꺼내 준다. 관람객과 판매원이 **소극장의 통제를 받는 수동적 존재**로 전락한 것이다. 게다가 `enter` 하나를 이해하려고 Audience가 Bag을 갖고, Bag 안에 현금과 티켓이 있고, TicketSeller가 TicketOffice에서 판매한다는 사실을 **동시에 기억해야** 한다.

**변경 문제**: 이 코드는 "관람객은 항상 가방을 들고 다닌다", "판매원은 매표소에서만 판매한다"는 가정에 의존한다. 관람객이 신용카드로 결제하거나 판매원이 매표소 밖에서 팔아야 하는 순간 Theater까지 흔들린다. 다른 클래스가 Audience의 내부를 많이 알수록 Audience를 변경하기 어려워진다. 이것이 **의존성**의 문제이고, 의존성이 과한 상태를 **결합도**가 높다고 부른다.

## 해결: 자율적인 객체로 만들기

해결책은 단순하다. 관람객이 스스로 가방을 다루고, 판매원이 스스로 매표소를 다루게 하는 것 - 즉 **자율적인 존재**로 만드는 것이다.

```typescript
// After - 메시지로만 협력하는 자율적 객체
class Theater {
    enter(audience: Audience): void {
        this.ticketSeller.sellTo(audience);   // 판매는 판매원이 알아서
    }
}

class TicketSeller {
    private ticketOffice: TicketOffice;       // getTicketOffice() 제거됨

    sellTo(audience: Audience): void {
        this.ticketOffice.plusAmount(audience.buy(this.ticketOffice.getTicket()));
    }
}

class Audience {
    private bag: Bag;                         // getBag() 제거됨

    buy(ticket: Ticket): number {
        return this.bag.hold(ticket);         // 가방도 스스로 처리한다
    }
}
```

여기서 일어난 일이 **캡슐화**다. `getTicketOffice()`와 `getBag()`이 사라지면서 내부 요소에 접근할 public 경로가 없어졌고, Theater는 TicketSeller가 `sellTo` 메시지를 이해한다는 사실만 안다. 즉 **인터페이스**(공개하는 메시지의 집합)에만 의존하고 **구현**(그 뒤에 감춰진 세부사항)은 모른다.

효과는 두 방향이다. 결합도가 낮아져서 Audience가 가방 대신 지갑을 쓰도록 바꿔도 Theater는 그대로고, 응집도가 높아져서 각 객체가 자신과 밀접한 작업만 수행한다.

## 책임의 이동과 트레이드오프

절차적 프로그래밍과 객체지향의 근본적 차이를 만드는 것은 **책임의 이동**이다.

| | 절차적 프로그래밍 | 객체지향 프로그래밍 |
|---|---|---|
| **책임 분배** | Theater에 집중 | 각 객체에 분산 |
| **작업 흐름** | Theater가 모든 작업을 도맡아 처리 | 각 객체가 자신의 일을 스스로 처리 |
| **의존성** | Theater가 모든 데이터에 의존 | 최소한의 의존성만 유지 |
| **변경 영향** | 하나의 변경이 여러 클래스에 파급 | 변경이 해당 객체 내부로 제한 |

Before 코드에서 Theater의 `enter`는 **프로세스**였고 나머지는 전부 수동적인 **데이터**였다. 데이터와 프로세스를 별도 모듈에 두는 것이 절차적 프로그래밍이고, 데이터를 소유한 객체가 그 데이터를 처리하게 하는 것이 객체지향이다.

다만 자율성을 끝까지 밀어붙이는 것이 항상 옳지는 않다. TicketOffice에 `sellTicketTo`를 추가해 자율성을 높이자 TicketOffice가 Audience를 알아야 하는 **새로운 의존성**이 생겼다. 저자는 TicketOffice의 자율성보다 Audience에 대한 결합도를 낮추는 것이 중요하다고 판단해 이 변경을 롤백한다.

> **핵심 통찰**: 동일한 기능을 한 가지 이상의 방법으로 설계할 수 있으므로 **설계는 트레이드오프의 산물**이다. 모든 사람을 만족시키는 설계는 없다. 설계는 균형의 예술이다.

## 의인화와 좋은 설계

Theater, Bag, TicketOffice는 실세계에서 자율적 존재가 아니다. 가방이 스스로 돈을 꺼내지는 않는다. 그럼에도 우리는 이들을 생물처럼 다뤘다. 레베카 워프스브록은 이렇게 무생물을 능동적 에이전트로 설계하는 원칙을 **의인화**라고 부른다.

> 객체는 무생물이거나 실세계의 개념적 개체로 모델링될 수도 있지만, 그들은 자신의 시스템 안에서 능동적이고 자율적인 에이전트로 행동한다.<br>- 레베카 워프스브록

좋은 설계란 오늘 요구하는 기능을 온전히 수행하면서 **내일의 변경을 매끄럽게 수용**하는 설계다. 요구사항은 항상 변하고, 코드를 변경할 때마다 버그 가능성이 높아지며, 버그에 대한 두려움이 다시 변경 의지를 꺾기 때문이다.

> **핵심 통찰**: 훌륭한 객체지향 설계란 **협력하는 객체 사이의 의존성을 적절하게 관리하는 설계**다. 데이터와 프로세스를 한 덩어리로 모으는 것은 첫걸음일 뿐이다.
