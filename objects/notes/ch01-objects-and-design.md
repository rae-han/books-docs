# Chapter 1: Objects and Design (객체, 설계)

## 핵심 질문

소프트웨어 설계에서 이론과 실무 중 무엇이 먼저인가? 좋은 객체지향 설계란 무엇이며, 절차적 프로그래밍의 문제를 어떻게 객체의 자율성과 캡슐화를 통해 해결할 수 있는가?

---

## 1. 이론 vs 실무

로버트 L. 글래스(Robert L. Glass)는 《소프트웨어 크리에이티비티 2.0》[Glass06a]에서 "이론이 먼저일까, 실무가 먼저일까?"라는 질문을 던진다. 대부분의 사람들은 이론이 먼저 정립된 후에 실무가 뒤따른다고 생각하지만, 글래스의 주장은 정반대다.

글래스에 따르면, 어떤 분야를 막론하고 이론을 정립할 수 없는 초기에는 **실무가 먼저 급속한 발전을 이룬다**. 실무가 어느 정도 발전한 다음에야 비로소 실무의 실용성을 입증할 수 있는 이론이 서서히 모습을 갖춰가기 시작하고, 해당 분야가 충분히 성숙해지는 시점에 이르러서야 이론이 실무를 추월하게 된다.

소프트웨어 분야에서 이 관점은 특히 중요하다:

- **소프트웨어 설계**: 훌륭한 설계에 관한 최초의 이론은 1970년대가 돼서야 비로소 등장했다. 대부분의 설계 원칙과 개념은 이론에서 실무로 스며들었다기보다는 실무에서 반복적으로 적용되던 기법들을 이론화한 것들이 대부분이다.
- **소프트웨어 유지보수**: 실무에서는 다양한 규모의 소프트웨어를 성공적으로 유지보수하고 있지만, 이와 관련된 효과적인 이론이 발표된 적은 거의 없다.

> **핵심 통찰**: 소프트웨어 설계와 유지보수에 중점을 두려면 이론이 아닌 실무에 초점을 맞추는 것이 효과적이다. 설계에 관해 설명할 때 가장 유용한 도구는 이론으로 치장된 개념과 용어가 아니라 **코드** 그 자체다.

이 책은 추상적인 개념이나 이론을 앞세우지 않고, 코드를 이용해 객체지향의 다양한 측면을 설명한다. 프로그래밍을 통해 개념과 이론을 배우는 것이 개념과 이론을 통해 프로그래밍을 배우는 것보다 더 훌륭한 학습 방법이다.

---

## 2. 티켓 판매 애플리케이션 구현하기

### 2.1 요구사항

작은 소극장을 경영하고 있다고 상상해 보자. 홍보를 겸해 추첨을 통해 선정된 관람객에게 무료 초대장을 발송하는 이벤트를 기획했다. 공연날이 되면 두 종류의 관람객이 존재한다:

| 관람객 유형 | 입장 방식 |
|---|---|
| 이벤트 당첨자 | 초대장을 티켓으로 교환 후 입장 |
| 일반 관람객 | 티켓을 구매 후 입장 |

### 2.2 초기 구현: 클래스 설계

**Invitation** - 초대장. 공연을 관람할 수 있는 초대일자(`when`)를 인스턴스 변수로 포함하는 간단한 클래스다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Invitation {
    private LocalDateTime when;
}
```

</details>

```typescript
// TypeScript
class Invitation {
    private when: Date;

    constructor(when: Date) {
        this.when = when;
    }
}
```

**Ticket** - 공연을 관람하기 위해 필요한 티켓. 요금(`fee`) 정보를 포함한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Ticket {
    private Long fee;

    public Long getFee() {
        return fee;
    }
}
```

</details>

```typescript
// TypeScript
class Ticket {
    private fee: number;

    constructor(fee: number) {
        this.fee = fee;
    }

    getFee(): number {
        return this.fee;
    }
}
```

**Bag** - 관람객의 소지품을 보관하는 가방. 초대장(`invitation`), 티켓(`ticket`), 현금(`amount`)을 인스턴스 변수로 포함한다. 이벤트 당첨자의 가방에는 현금과 초대장이, 미당첨자의 가방에는 현금만 들어 있다. 생성자를 통해 이 제약을 강제한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Bag {
    private Long amount;
    private Invitation invitation;
    private Ticket ticket;

    public Bag(long amount) {
        this(null, amount);
    }

    public Bag(Invitation invitation, long amount) {
        this.invitation = invitation;
        this.amount = amount;
    }

    public boolean hasInvitation() {
        return invitation != null;
    }

    public boolean hasTicket() {
        return ticket != null;
    }

    public void setTicket(Ticket ticket) {
        this.ticket = ticket;
    }

    public void minusAmount(Long amount) {
        this.amount -= amount;
    }

    public void plusAmount(Long amount) {
        this.amount += amount;
    }
}
```

</details>

```typescript
// TypeScript
class Bag {
    private amount: number;
    private invitation: Invitation | null;
    private ticket: Ticket | null = null;

    constructor(amount: number);
    constructor(invitation: Invitation, amount: number);
    constructor(invitationOrAmount: Invitation | number, amount?: number) {
        if (typeof invitationOrAmount === "number") {
            this.invitation = null;
            this.amount = invitationOrAmount;
        } else {
            this.invitation = invitationOrAmount;
            this.amount = amount!;
        }
    }

    hasInvitation(): boolean {
        return this.invitation !== null;
    }

    hasTicket(): boolean {
        return this.ticket !== null;
    }

    setTicket(ticket: Ticket): void {
        this.ticket = ticket;
    }

    minusAmount(amount: number): void {
        this.amount -= amount;
    }

    plusAmount(amount: number): void {
        this.amount += amount;
    }
}
```

**Audience** - 관람객. 소지품을 보관하기 위해 가방을 소지한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Audience {
    private Bag bag;

    public Audience(Bag bag) {
        this.bag = bag;
    }

    public Bag getBag() {
        return bag;
    }
}
```

</details>

```typescript
// TypeScript
class Audience {
    private bag: Bag;

    constructor(bag: Bag) {
        this.bag = bag;
    }

    getBag(): Bag {
        return this.bag;
    }
}
```

**TicketOffice** - 매표소. 판매하거나 교환해 줄 티켓의 목록(`tickets`)과 판매 금액(`amount`)을 인스턴스 변수로 포함한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class TicketOffice {
    private Long amount;
    private List<Ticket> tickets = new ArrayList<>();

    public TicketOffice(Long amount, Ticket... tickets) {
        this.amount = amount;
        this.tickets.addAll(Arrays.asList(tickets));
    }

    public Ticket getTicket() {
        return tickets.remove(0);
    }

    public void minusAmount(Long amount) {
        this.amount -= amount;
    }

    public void plusAmount(Long amount) {
        this.amount += amount;
    }
}
```

</details>

```typescript
// TypeScript
class TicketOffice {
    private amount: number;
    private tickets: Ticket[];

    constructor(amount: number, ...tickets: Ticket[]) {
        this.amount = amount;
        this.tickets = [...tickets];
    }

    getTicket(): Ticket {
        return this.tickets.shift()!;
    }

    minusAmount(amount: number): void {
        this.amount -= amount;
    }

    plusAmount(amount: number): void {
        this.amount += amount;
    }
}
```

**TicketSeller** - 판매원. 자신이 일하는 매표소(`ticketOffice`)를 알고 있어야 한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class TicketSeller {
    private TicketOffice ticketOffice;

    public TicketSeller(TicketOffice ticketOffice) {
        this.ticketOffice = ticketOffice;
    }

    public TicketOffice getTicketOffice() {
        return ticketOffice;
    }
}
```

</details>

```typescript
// TypeScript
class TicketSeller {
    private ticketOffice: TicketOffice;

    constructor(ticketOffice: TicketOffice) {
        this.ticketOffice = ticketOffice;
    }

    getTicketOffice(): TicketOffice {
        return this.ticketOffice;
    }
}
```

### 2.3 클래스 관계

```
┌──────────┐        ┌───────────┐        ┌────────────┐
│ Audience │───bag──▶│    Bag     │───inv──▶│ Invitation │
│          │        │           │        │   when     │
│ getBag() │        │ amount    │        └────────────┘
└──────────┘        │ hasInv()  │
                    │ hasTkt()  │───tkt──▶┌────────────┐
                    │ setTkt()  │        │   Ticket   │
                    │ minus()   │        │   fee      │
                    │ plus()    │        │  getFee()  │
                    └───────────┘        └────────────┘
                                              ▲
┌──────────────┐     ┌──────────────┐         │
│ TicketSeller │─of─▶│ TicketOffice │─tickets─┘
│              │     │   amount     │
│ getTktOfc()  │     │  getTicket() │
└──────────────┘     │  minus()     │
                     │  plus()      │
                     └──────────────┘
```

### 2.4 Theater의 enter 메서드: 나쁜 설계

이제 이 클래스들을 조합해서 관람객을 소극장에 입장시키는 로직을 작성한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Theater {
    private TicketSeller ticketSeller;

    public Theater(TicketSeller ticketSeller) {
        this.ticketSeller = ticketSeller;
    }

    public void enter(Audience audience) {
        if (audience.getBag().hasInvitation()) {
            Ticket ticket = ticketSeller.getTicketOffice().getTicket();
            audience.getBag().setTicket(ticket);
        } else {
            Ticket ticket = ticketSeller.getTicketOffice().getTicket();
            audience.getBag().minusAmount(ticket.getFee());
            ticketSeller.getTicketOffice().plusAmount(ticket.getFee());
            audience.getBag().setTicket(ticket);
        }
    }
}
```

</details>

```typescript
// TypeScript
class Theater {
    private ticketSeller: TicketSeller;

    constructor(ticketSeller: TicketSeller) {
        this.ticketSeller = ticketSeller;
    }

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

로직 자체는 간단하고 예상대로 동작한다. 소극장은 먼저 관람객의 가방 안에 초대장이 들어 있는지 확인한다. 초대장이 있으면 매표소에서 티켓을 꺼내 가방에 넣어 준다. 초대장이 없으면 가방에서 티켓 금액만큼 현금을 차감하고, 매표소에 금액을 적립한 후 티켓을 가방에 넣어 준다.

하지만 이 작은 프로그램에는 몇 가지 심각한 문제가 있다.

---

## 3. 무엇이 문제인가

로버트 마틴(Robert C. Martin)은 《클린 소프트웨어: 애자일 원칙과 패턴, 그리고 실천 방법》[Martin02a]에서 소프트웨어 모듈(*Module - 클래스, 패키지, 라이브러리 등 프로그램을 구성하는 임의의 요소*)이 가져야 하는 세 가지 목적을 제시한다:

| 모듈의 목적 | 설명 |
|---|---|
| **1. 제대로 동작해야 한다** | 모듈의 존재 이유. 실행 중에 올바르게 동작해야 한다 |
| **2. 변경을 위해 존재한다** | 대부분의 모듈은 생명주기 동안 변경되므로 간단한 작업만으로도 변경이 가능해야 한다 |
| **3. 읽는 사람과 의사소통해야 한다** | 특별한 훈련 없이도 개발자가 쉽게 읽고 이해할 수 있어야 한다 |

앞의 프로그램은 첫 번째 목적(제대로 동작한다)은 만족시키지만, 나머지 두 가지 목적은 만족시키지 못한다.

### 3.1 예상을 빗나가는 코드

Theater의 `enter` 메서드가 수행하는 일을 말로 풀어 보자:

> 소극장은 관람객의 가방을 열어 그 안에 초대장이 들어 있는지 살펴본다. 가방 안에 초대장이 들어 있으면 판매원은 매표소에 보관돼 있는 티켓을 관람객의 가방 안으로 옮긴다. 가방 안에 초대장이 들어 있지 않다면 관람객의 가방에서 티켓 금액만큼의 현금을 꺼내 매표소에 적립한 후에 매표소에 보관돼 있는 티켓을 관람객의 가방 안으로 옮긴다.

문제는 **관람객과 판매원이 소극장의 통제를 받는 수동적인 존재**라는 점이다.

- **관람객 입장**: 소극장이라는 제3자가 허락 없이 가방을 열어 보고, 돈을 가져가고, 티켓을 넣어 준다.
- **판매원 입장**: 소극장이 허락 없이 매표소에 보관 중인 티켓과 현금에 접근한다. 판매원은 매표소 안에 가만히 앉아 티켓이 사라지고 돈이 쌓이는 광경을 두 손 놓고 쳐다볼 수밖에 없다.

이해 가능한 코드란 그 동작이 우리의 예상에서 크게 벗어나지 않는 코드다. 현실에서는 관람객이 직접 가방에서 초대장이나 돈을 꺼내 판매원에게 건네고, 판매원은 매표소에서 직접 티켓을 꺼내 건넨다. 하지만 이 코드의 관람객과 판매원은 그렇게 하지 않는다.

코드를 이해하기 어렵게 만드는 또 다른 이유는, `enter` 메서드를 이해하기 위해 **너무 많은 세부사항을 한꺼번에 기억해야 한다**는 점이다. Audience가 Bag을 가지고 있고, Bag 안에는 현금과 티켓이 들어 있으며, TicketSeller가 TicketOffice에서 티켓을 판매하고, TicketOffice 안에 돈과 티켓이 보관돼 있다는 모든 사실을 동시에 기억하고 있어야 한다.

### 3.2 변경에 취약한 코드

가장 심각한 문제는 Audience와 TicketSeller를 변경할 경우 Theater도 함께 변경해야 한다는 점이다. 이 코드는 다음과 같은 가정에 의존한다:

- 관람객이 현금과 초대장을 보관하기 위해 **항상 가방을 들고 다닌다**
- 판매원이 **매표소에서만** 티켓을 판매한다

관람객이 가방을 들고 있지 않다면? 신용카드로 결제한다면? 판매원이 매표소 밖에서 티켓을 판매해야 한다면? 이런 가정이 깨지는 순간 모든 코드가 일시에 흔들리게 된다.

이것은 객체 사이의 **의존성**(*Dependency - 한 객체가 변경될 때 그 객체에 의존하는 다른 객체도 함께 변경될 수 있음을 암시하는 관계*)과 관련된 문제다. 의존성은 변경에 대한 영향을 암시한다. 다른 클래스가 Audience의 내부에 대해 더 많이 알면 알수록 Audience를 변경하기 어려워진다.

```
┌──────────┐
│ Theater  │──────────────┐
│ enter()  │──┐           │
└──────────┘  │           │
    │         │           ▼
    │         │    ┌──────────────┐
    │         │    │ TicketOffice │
    │         │    └──────────────┘
    │         ▼           ▲
    │    ┌──────────────┐ │
    │    │ TicketSeller │─┘
    │    └──────────────┘
    ▼
┌──────────┐     ┌───────┐
│ Audience │────▶│  Bag  │
└──────────┘     └───────┘
  Theater가 Audience, Bag, TicketSeller,
  TicketOffice 모두에 의존하고 있다
```

그렇다고 객체 사이의 의존성을 완전히 없애는 것이 정답은 아니다. 객체지향 설계는 서로 의존하면서 협력하는 객체들의 공동체를 구축하는 것이다. 목표는 **애플리케이션의 기능을 구현하는 데 필요한 최소한의 의존성만 유지하고 불필요한 의존성을 제거하는 것**이다.

객체 사이의 의존성이 과한 경우를 **결합도**(*Coupling - 객체 간 의존성의 정도*)가 높다고 말한다. 설계의 목표는 객체 사이의 결합도를 낮춰 변경이 용이한 설계를 만드는 것이다.

---

## 4. 설계 개선하기

코드를 이해하기 어려운 이유는 Theater가 관람객의 가방과 판매원의 매표소에 직접 접근하기 때문이다. 해결 방법은 간단하다: 관람객이 스스로 가방 안의 현금과 초대장을 처리하고, 판매원이 스스로 매표소의 티켓과 판매 요금을 다루게 만드는 것이다.

다시 말해서 **관람객과 판매원을 자율적인 존재로 만들면 된다**.

### 4.1 1단계: TicketSeller의 자율성 높이기

Theater의 enter 메서드에서 TicketOffice에 접근하는 모든 코드를 TicketSeller 내부로 숨긴다. TicketSeller에 `sellTo` 메서드를 추가하고 Theater에 있던 로직을 이 메서드로 옮긴다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class TicketSeller {
    private TicketOffice ticketOffice;

    public TicketSeller(TicketOffice ticketOffice) {
        this.ticketOffice = ticketOffice;
    }

    public void sellTo(Audience audience) {
        if (audience.getBag().hasInvitation()) {
            Ticket ticket = ticketOffice.getTicket();
            audience.getBag().setTicket(ticket);
        } else {
            Ticket ticket = ticketOffice.getTicket();
            audience.getBag().minusAmount(ticket.getFee());
            ticketOffice.plusAmount(ticket.getFee());
            audience.getBag().setTicket(ticket);
        }
    }
}
```

</details>

```typescript
// TypeScript
class TicketSeller {
    private ticketOffice: TicketOffice;

    constructor(ticketOffice: TicketOffice) {
        this.ticketOffice = ticketOffice;
    }

    sellTo(audience: Audience): void {
        if (audience.getBag().hasInvitation()) {
            const ticket = this.ticketOffice.getTicket();
            audience.getBag().setTicket(ticket);
        } else {
            const ticket = this.ticketOffice.getTicket();
            audience.getBag().minusAmount(ticket.getFee());
            this.ticketOffice.plusAmount(ticket.getFee());
            audience.getBag().setTicket(ticket);
        }
    }
}
```

핵심 변경점: `getTicketOffice` 메서드가 제거됐다. `ticketOffice`의 가시성이 `private`이고 접근 가능한 public 메서드가 더 이상 존재하지 않기 때문에, 외부에서는 `ticketOffice`에 직접 접근할 수 없다. `ticketOffice`에 대한 접근은 오직 TicketSeller 안에만 존재하게 된다.

이처럼 개념적이나 물리적으로 객체 내부의 세부적인 사항을 감추는 것을 **캡슐화**(*Encapsulation - 객체 내부의 세부사항을 감추고 외부 접근을 제한하는 것*)라고 부른다. 캡슐화의 목적은 변경하기 쉬운 객체를 만드는 것이다.

이제 Theater의 enter 메서드는 간단한 코드로 바뀐다:

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Theater {
    private TicketSeller ticketSeller;

    public Theater(TicketSeller ticketSeller) {
        this.ticketSeller = ticketSeller;
    }

    public void enter(Audience audience) {
        ticketSeller.sellTo(audience);
    }
}
```

</details>

```typescript
// TypeScript
class Theater {
    private ticketSeller: TicketSeller;

    constructor(ticketSeller: TicketSeller) {
        this.ticketSeller = ticketSeller;
    }

    enter(audience: Audience): void {
        this.ticketSeller.sellTo(audience);
    }
}
```

Theater는 `ticketOffice`가 TicketSeller 내부에 존재한다는 사실을 알지 못한다. Theater는 단지 TicketSeller가 `sellTo` 메시지를 이해하고 응답할 수 있다는 사실만 알고 있을 뿐이다. Theater는 오직 TicketSeller의 **인터페이스**(*Interface - 객체가 외부에 공개하는 메시지의 집합*)에만 의존한다. TicketSeller가 내부에 TicketOffice 인스턴스를 포함하고 있다는 사실은 **구현**(*Implementation - 인터페이스 뒤에 감춰진 객체 내부의 세부사항*)의 영역에 속한다.

> **핵심 통찰**: 객체를 인터페이스와 구현으로 나누고 인터페이스만을 공개하는 것은 객체 사이의 결합도를 낮추고 변경하기 쉬운 코드를 작성하기 위해 따라야 하는 가장 기본적인 설계 원칙이다.

### 4.2 2단계: Audience의 자율성 높이기

TicketSeller는 여전히 Audience의 `getBag` 메서드를 호출해서 Audience 내부의 Bag 인스턴스에 직접 접근한다. Bag에 접근하는 객체가 Theater에서 TicketSeller로 바뀌었을 뿐, Audience는 여전히 자율적인 존재가 아니다.

Audience에 `buy` 메서드를 추가하고, TicketSeller의 `sellTo` 메서드에서 `getBag` 메서드에 접근하는 부분을 `buy` 메서드로 옮긴다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Audience {
    private Bag bag;

    public Audience(Bag bag) {
        this.bag = bag;
    }

    public Long buy(Ticket ticket) {
        if (bag.hasInvitation()) {
            bag.setTicket(ticket);
            return 0L;
        } else {
            bag.setTicket(ticket);
            bag.minusAmount(ticket.getFee());
            return ticket.getFee();
        }
    }
}
```

</details>

```typescript
// TypeScript
class Audience {
    private bag: Bag;

    constructor(bag: Bag) {
        this.bag = bag;
    }

    buy(ticket: Ticket): number {
        if (this.bag.hasInvitation()) {
            this.bag.setTicket(ticket);
            return 0;
        } else {
            this.bag.setTicket(ticket);
            this.bag.minusAmount(ticket.getFee());
            return ticket.getFee();
        }
    }
}
```

변경된 코드에서 Audience는 자신의 가방 안에 초대장이 들어 있는지를 **스스로 확인**한다. 외부의 제3자가 자신의 가방을 열어 보도록 허용하지 않는다. Audience가 Bag을 직접 처리하기 때문에 외부에서는 더 이상 Audience가 Bag을 소유하고 있다는 사실을 알 필요가 없다. `getBag` 메서드를 제거할 수 있고, 결과적으로 Bag의 존재를 내부로 캡슐화할 수 있게 됐다.

이제 TicketSeller가 Audience의 인터페이스에만 의존하도록 수정한다:

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class TicketSeller {
    private TicketOffice ticketOffice;

    public TicketSeller(TicketOffice ticketOffice) {
        this.ticketOffice = ticketOffice;
    }

    public void sellTo(Audience audience) {
        ticketOffice.plusAmount(audience.buy(ticketOffice.getTicket()));
    }
}
```

</details>

```typescript
// TypeScript
class TicketSeller {
    private ticketOffice: TicketOffice;

    constructor(ticketOffice: TicketOffice) {
        this.ticketOffice = ticketOffice;
    }

    sellTo(audience: Audience): void {
        this.ticketOffice.plusAmount(audience.buy(this.ticketOffice.getTicket()));
    }
}
```

TicketSeller와 Audience 사이의 결합도가 낮아졌다. 내부 구현이 캡슐화됐으므로 Audience의 구현을 수정하더라도 TicketSeller에는 영향을 미치지 않는다.

### 4.3 개선 결과: 자율적인 객체

```
┌──────────┐  sellTo  ┌──────────────┐  buy   ┌──────────┐
│ Theater  │────────▶│ TicketSeller │──────▶│ Audience │
│ enter()  │        │  sellTo()    │       │  buy()   │
└──────────┘        │              │       │          │
                    │  [private]   │       │ [private]│
                    │  ticketOfc ──┤       │  bag ────┤
                    └──────────────┘       └──────────┘
                           │                     │
                           ▼                     ▼
                    ┌──────────────┐        ┌─────────┐
                    │ TicketOffice │        │   Bag   │
                    └──────────────┘        └─────────┘

  Theater → TicketSeller → Audience 순서로만 의존.
  TicketOffice, Bag은 각각의 소유자만 접근 가능.
```

가장 크게 달라진 점은 Audience와 TicketSeller가 내부 구현을 외부에 노출하지 않고 **자신의 문제를 스스로 책임지고 해결한다**는 것이다.

---

## 5. 무엇이 개선됐는가

### 5.1 의사소통 관점

수정된 Audience와 TicketSeller는 자신이 가지고 있는 소지품을 스스로 관리한다. 이것은 우리의 예상과도 정확하게 일치한다. 코드를 읽는 사람과의 의사소통 관점에서 확실히 개선됐다.

### 5.2 변경 용이성 관점

Audience나 TicketSeller의 내부 구현을 변경하더라도 Theater를 함께 변경할 필요가 없어졌다.

- Audience가 가방이 아니라 작은 지갑을 소지하도록 변경하고 싶은가? **Audience 내부만 변경하면 된다.**
- TicketSeller가 매표소가 아니라 은행에 돈을 보관하도록 만들고 싶은가? **TicketSeller 내부만 변경하면 된다.**

### 5.3 캡슐화와 응집도

핵심은 **객체 내부의 상태를 캡슐화하고 객체 간에 오직 메시지를 통해서만 상호작용하도록 만드는 것**이다.

- Theater는 TicketSeller의 내부에 대해 전혀 알지 못한다. 단지 TicketSeller가 `sellTo` 메시지를 이해하고 응답할 수 있다는 사실만 알고 있을 뿐이다.
- TicketSeller 역시 Audience의 내부에 대해 전혀 알지 못한다. 단지 Audience가 `buy` 메시지에 응답할 수 있고 자신이 원하는 결과를 반환할 것이라는 사실만 알고 있을 뿐이다.

밀접하게 연관된 작업만을 수행하고 연관성 없는 작업은 다른 객체에게 위임하는 객체를 가리켜 **응집도**(*Cohesion - 객체가 자신과 밀접하게 연관된 작업만 수행하는 정도*)가 높다고 말한다. 자신의 데이터를 스스로 처리하는 자율적인 객체를 만들면 결합도를 낮출 수 있을뿐더러 응집도를 높일 수 있다.

> **핵심 통찰**: 외부의 간섭을 최대한 배제하고 메시지를 통해서만 협력하는 자율적인 객체들의 공동체를 만드는 것이 훌륭한 객체지향 설계를 얻을 수 있는 지름길이다.

---

## 6. 절차지향 vs 객체지향

### 6.1 절차적 프로그래밍

수정 전 코드에서는 Theater의 `enter` 메서드 안에서 모든 처리가 이뤄졌다. Audience, TicketSeller, Bag, TicketOffice는 정보를 제공하는 데이터에 불과했고, 모든 처리는 Theater의 `enter` 메서드 안에 존재했다.

이 관점에서 Theater의 `enter` 메서드는 **프로세스**(*Process - 데이터를 사용하여 기능을 처리하는 절차*)이며, Audience, TicketSeller, Bag, TicketOffice는 **데이터**(*Data - 프로세스에 의해 사용되는 수동적인 정보*)다. 이처럼 프로세스와 데이터를 별도의 모듈에 위치시키는 방식을 **절차적 프로그래밍**(*Procedural Programming*)이라고 부른다.

절차적 프로그래밍의 문제:

1. **우리의 직관에 위배된다**: 관람객과 판매원이 자신의 일을 스스로 처리할 것이라고 예상하지만, 절차적 프로그래밍에서는 수동적인 존재일 뿐이다.
2. **데이터의 변경으로 인한 영향을 지역적으로 고립시키기 어렵다**: Audience와 TicketSeller의 내부 구현을 변경하려면 Theater의 `enter` 메서드를 함께 변경해야 한다.
3. **프로세스가 필요한 모든 데이터에 의존해야 한다는 근본적 문제**: 변경에 취약할 수밖에 없다.

```
        [절차적 프로그래밍: 책임이 중앙 집중]

                    Theater
                   ╱  │  ╲  ╲
                  ╱   │   ╲   ╲
                 ▼    ▼    ▼    ▼
          TicketSeller  TicketOffice  Audience  Bag
          (데이터)      (데이터)      (데이터)   (데이터)

    → 모든 책임이 Theater에 집중
    → Theater가 모든 객체에 의존
```

### 6.2 객체지향 프로그래밍

데이터를 사용하는 프로세스를 데이터를 소유하고 있는 Audience와 TicketSeller 내부로 옮기면, 데이터와 프로세스가 동일한 모듈 내부에 위치하게 된다. 이처럼 데이터와 프로세스가 동일한 모듈 내부에 위치하도록 프로그래밍하는 방식을 **객체지향 프로그래밍**(*Object-Oriented Programming*)이라고 부른다.

```
        [객체지향 프로그래밍: 책임이 분산]

    Theater ──▶ TicketSeller ──▶ Audience
    (입장)      (판매)           (구매)
                    │
                    ▼
               TicketOffice

    → 각 객체가 자신의 책임을 스스로 수행
    → 의존성이 적절히 통제됨
```

> **핵심 통찰**: 훌륭한 객체지향 설계의 핵심은 캡슐화를 이용해 의존성을 적절히 관리함으로써 객체 사이의 결합도를 낮추는 것이다. 객체지향 코드는 자신의 문제를 스스로 처리해야 한다는 우리의 예상을 만족시켜주기 때문에 이해하기 쉽고, 객체 내부의 변경이 외부에 파급되지 않도록 제어할 수 있기 때문에 변경하기가 수월하다.

---

## 7. 책임의 이동

두 방식 사이에 근본적인 차이를 만드는 것은 **책임의 이동**(*Shift of Responsibility*)[Shalloway01]이다. 여기서 '책임'은 기능을 가리키는 객체지향 세계의 용어로 생각해도 무방하다.

| | 절차적 프로그래밍 | 객체지향 프로그래밍 |
|---|---|---|
| **책임 분배** | Theater에 집중 | 각 객체에 분산 |
| **작업 흐름** | Theater가 모든 작업을 도맡아 처리 | 각 객체가 자신의 일을 스스로 처리 |
| **의존성** | Theater가 모든 데이터에 의존 | 최소한의 의존성만 유지 |
| **변경 영향** | 하나의 변경이 여러 클래스에 파급 | 변경이 해당 객체 내부로 제한 |

객체지향 설계에서는 독재자가 존재하지 않고 각 객체에 책임이 적절하게 분배된다. 객체지향 애플리케이션은 스스로 책임을 수행하는 자율적인 객체들의 공동체를 구성함으로써 완성된다.

> 설계를 어렵게 만드는 것은 의존성이다. 해결 방법은 불필요한 의존성을 제거함으로써 객체 사이의 결합도를 낮추는 것이다. 결합도를 낮추기 위해 선택한 방법은 Theater가 몰라도 되는 세부사항을 Audience와 TicketSeller 내부로 감춰 캡슐화하는 것이다.

사실 객체지향 설계의 핵심은 **적절한 객체에 적절한 책임을 할당하는 것**이다. 객체가 어떤 데이터를 가지느냐보다는 객체에 어떤 책임을 할당할 것이냐에 초점을 맞춰야 한다.

---

## 8. 더 개선할 수 있다

현재 설계는 이전보다 분명히 좋아졌지만 아직도 개선의 여지가 있다.

### 8.1 Bag의 자율성 개선

Audience의 `buy` 메서드를 보면, Audience는 자율적인 존재지만 **Bag은 여전히 수동적인 존재**다. Bag은 과거의 Audience처럼 Audience에 의해 끌려 다니는 존재다.

Bag을 자율적인 존재로 바꿔 보자. Bag의 내부 상태에 접근하는 모든 로직을 Bag 안으로 캡슐화해서 결합도를 낮추면 된다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Bag {
    private Long amount;
    private Ticket ticket;
    private Invitation invitation;

    public Long hold(Ticket ticket) {
        if (hasInvitation()) {
            setTicket(ticket);
            return 0L;
        } else {
            setTicket(ticket);
            minusAmount(ticket.getFee());
            return ticket.getFee();
        }
    }

    private void setTicket(Ticket ticket) {
        this.ticket = ticket;
    }

    private boolean hasInvitation() {
        return invitation != null;
    }

    private void minusAmount(Long amount) {
        this.amount -= amount;
    }
}
```

</details>

```typescript
// TypeScript
class Bag {
    private amount: number;
    private ticket: Ticket | null = null;
    private invitation: Invitation | null;

    // ... 생성자 생략 ...

    hold(ticket: Ticket): number {
        if (this.hasInvitation()) {
            this.setTicket(ticket);
            return 0;
        } else {
            this.setTicket(ticket);
            this.minusAmount(ticket.getFee());
            return ticket.getFee();
        }
    }

    private setTicket(ticket: Ticket): void {
        this.ticket = ticket;
    }

    private hasInvitation(): boolean {
        return this.invitation !== null;
    }

    private minusAmount(amount: number): void {
        this.amount -= amount;
    }
}
```

public이었던 `hasInvitation`, `minusAmount`, `setTicket` 메서드들은 더 이상 외부에서 사용되지 않고 내부에서만 사용되기 때문에 가시성을 `private`으로 변경했다. 이제 Bag은 관련된 상태와 행위를 함께 가지는 응집도 높은 클래스가 됐다.

Audience의 `buy` 메서드는 다음과 같이 단순해진다:

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Audience {
    public Long buy(Ticket ticket) {
        return bag.hold(ticket);
    }
}
```

</details>

```typescript
// TypeScript
class Audience {
    buy(ticket: Ticket): number {
        return this.bag.hold(ticket);
    }
}
```

### 8.2 TicketOffice의 자율성 개선

TicketSeller 역시 TicketOffice의 자율권을 침해하고 있다. TicketSeller는 TicketOffice에 있는 Ticket을 마음대로 꺼내 Audience에게 팔고, Audience에게 받은 돈을 마음대로 TicketOffice에 넣는다.

TicketOffice에 `sellTicketTo` 메서드를 추가하고 TicketSeller의 `sellTo` 메서드의 내부 코드를 이 메서드로 옮긴다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class TicketOffice {
    public void sellTicketTo(Audience audience) {
        plusAmount(audience.buy(getTicket()));
    }

    private Ticket getTicket() {
        return tickets.remove(0);
    }

    private void plusAmount(Long amount) {
        this.amount += amount;
    }
}
```

</details>

```typescript
// TypeScript
class TicketOffice {
    sellTicketTo(audience: Audience): void {
        this.plusAmount(audience.buy(this.getTicket()));
    }

    private getTicket(): Ticket {
        return this.tickets.shift()!;
    }

    private plusAmount(amount: number): void {
        this.amount += amount;
    }
}
```

TicketSeller는 TicketOffice의 `sellTicketTo` 메서드를 호출하는 것으로 단순해진다:

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class TicketSeller {
    public void sellTo(Audience audience) {
        ticketOffice.sellTicketTo(audience);
    }
}
```

</details>

```typescript
// TypeScript
class TicketSeller {
    sellTo(audience: Audience): void {
        this.ticketOffice.sellTicketTo(audience);
    }
}
```

### 8.3 트레이드오프: 자율성 vs 결합도

안타깝게도 이 변경은 처음에 생각했던 것만큼 만족스럽지 않다. **TicketOffice와 Audience 사이에 의존성이 추가됐기 때문이다.** 변경 전에는 TicketOffice가 Audience에 대해 알지 못했다. 변경 후에는 TicketOffice가 Audience에게 직접 티켓을 판매하기 때문에 Audience에 관해 알고 있어야 한다.

```
  [변경 전]                       [변경 후]
  TicketSeller                    TicketSeller
       │                              │
       ▼                              ▼
  TicketOffice   Audience         TicketOffice ──▶ Audience
  (서로 모름)                     (새로운 의존성 추가!)
```

TicketOffice의 자율성은 높였지만 전체 설계의 관점에서는 결합도가 상승했다. 현재로서는 Audience에 대한 결합도와 TicketOffice의 자율성 모두를 만족시키는 방법이 잘 떠오르지 않는다.

트레이드오프의 시점이 왔다. 토론 끝에 **TicketOffice의 자율성보다는 Audience에 대한 결합도를 낮추는 것이 더 중요하다**는 결론에 도달했다.

> **핵심 통찰**: 어떤 기능을 설계하는 방법은 한 가지 이상일 수 있다. 동일한 기능을 한 가지 이상의 방법으로 설계할 수 있기 때문에 결국 **설계는 트레이드오프의 산물**이다. 어떤 경우에도 모든 사람들을 만족시킬 수 있는 설계를 만들 수는 없다. 설계는 균형의 예술이다.

---

## 9. 의인화

앞에서 실생활의 관람객과 판매자가 스스로 자신의 일을 처리하기 때문에 코드에서의 Audience와 TicketSeller 역시 스스로 자신을 책임져야 한다고 설명했다. 이것은 우리가 세상을 바라보는 직관과도 일치한다.

그러나 Theater, Bag, TicketOffice는 실세계에서 자율적인 존재가 아니다. 소극장에 관람객이 입장하기 위해서는 누군가가 문을 열고 허가해 줘야 한다. 가방에서 돈을 꺼내는 것은 관람객이지 가방이 아니다. 판매원이 매표소에 없는데도 티켓이 저절로 전달되지는 않는다.

그럼에도 우리는 이들을 마치 생물처럼 다뤘다. 무생물 역시 스스로 행동하고 자기 자신을 책임지는 자율적인 존재로 취급한 것이다.

레베카 워프스브록(Rebecca Wirfs-Brock)은 이처럼 능동적이고 자율적인 존재로 소프트웨어 객체를 설계하는 원칙을 **의인화**(*Anthropomorphism - 무생물이나 추상적 개념을 마치 생명체처럼 자율적으로 행동하게 설계하는 원칙*)라고 부른다.

> 객체는 무생물이거나 심지어는 실세계의 개념적인 개체로 모델링될 수도 있지만, 그들은 마치 우리가 현실 세계에서 에이전트로 행동하는 것처럼 그들의 시스템 안에서 에이전트처럼 행동한다. 일상적인 체계에서는 어떤 사건이 일어나기 위해 반드시 인간 에이전트가 필요한 반면, 객체들은 그들 자신의 체계 안에서 능동적이고 자율적인 에이전트다.
>
> 의인화의 관점에서 소프트웨어를 생물로 생각하자. 모든 생물처럼 소프트웨어는 태어나고, 삶을 영위하고, 그리고 죽는다. - Rebecca Wirfs-Brock[Wirfs-Brock90]

훌륭한 객체지향 설계란 소프트웨어를 구성하는 모든 객체들이 자율적으로 행동하는 설계를 가리킨다. 그 대상이 비록 실세계에서는 생명이 없는 수동적인 존재라고 하더라도, 객체지향의 세계로 넘어오는 순간 그들은 생명과 지능을 가진 싱싱한 존재로 다시 태어난다.

이해하기 쉽고 변경하기 쉬운 코드를 작성하고 싶다면 차라리 한 편의 애니메이션을 만든다고 생각하라. 다른 사람의 코드를 읽고 이해하는 동안에는 애니메이션을 보고 있다고 여러분의 뇌를 속여라. 그렇게 하면 코드 안에서 웃고, 떠들고, 화내는 가방 객체를 만나더라도 당황하지 않을 것이다.

---

## 10. 객체지향 설계

### 10.1 설계가 왜 필요한가

> 설계란 코드를 배치하는 것이다. - Sandi Metz[Metz12]

설계를 구현과 떨어트려서 이야기하는 것은 불가능하다. 설계는 코드를 작성하는 매 순간 코드를 어떻게 배치할 것인지를 결정하는 과정에서 나온다.

좋은 설계란 두 가지 요구사항을 만족시키는 것이다:

1. **오늘 요구하는 기능을 온전히 수행한다**
2. **내일의 변경을 매끄럽게 수용할 수 있다**

변경을 수용할 수 있는 설계가 중요한 이유:

- **요구사항은 항상 변경되기 때문이다**: 개발 시작 시점에 모든 요구사항을 수집하는 것은 불가능에 가깝고, 수집할 수 있다 해도 개발 중에 바뀔 수밖에 없다.
- **코드를 변경할 때 버그가 추가될 가능성이 높기 때문이다**: 요구사항 변경은 코드 수정을 초래하고, 코드 수정은 버그 가능성을 높이며, 버그에 대한 두려움은 코드 변경 의지를 꺾는다.

### 10.2 객체지향 설계란

객체지향 프로그래밍은 의존성을 효율적으로 통제할 수 있는 다양한 방법을 제공함으로써 요구사항 변경에 좀 더 수월하게 대응할 수 있는 가능성을 높여준다.

객체지향 패러다임은 세상을 바라보는 방식대로 코드를 작성할 수 있게 돕는다. 세상에 존재하는 모든 자율적인 존재처럼 객체 역시 자신의 데이터를 스스로 책임지는 자율적인 존재다. 객체지향은 객체가 예상하는 방식대로 행동하리라는 것을 보장함으로써 코드를 좀 더 쉽게 이해할 수 있게 한다.

그러나 단순히 데이터와 프로세스를 객체라는 덩어리 안으로 밀어 넣었다고 해서 변경하기 쉬운 설계를 얻을 수 있는 것은 아니다. 애플리케이션의 기능은 객체들 간의 상호작용을 통해 구현되며, 이 과정에서 객체들은 다른 객체에 의존하게 된다.

> **핵심 통찰**: 훌륭한 객체지향 설계란 **협력하는 객체 사이의 의존성을 적절하게 관리하는 설계**다. 데이터와 프로세스를 하나의 덩어리로 모으는 것은 훌륭한 객체지향 설계로 가는 첫걸음일 뿐이다. 진정한 객체지향 설계로 나아가는 길은 협력하는 객체들 사이의 의존성을 적절하게 조절함으로써 변경에 용이한 설계를 만드는 것이다.

---

## 리팩터링 과정

| 단계 | 변경 내용 | 핵심 효과 |
|---|---|---|
| **0단계** (원본) | Theater의 `enter`가 모든 로직을 처리 | 동작하지만 이해하기 어렵고 변경에 취약 |
| **1단계** | TicketSeller에 `sellTo` 추가, `getTicketOffice` 제거 | Theater → TicketOffice 의존성 제거, TicketOffice 캡슐화 |
| **2단계** | Audience에 `buy` 추가, `getBag` 제거 | TicketSeller → Bag 의존성 제거, Bag 캡슐화 |
| **3단계** | Bag에 `hold` 추가, 내부 메서드 `private`으로 변경 | Audience → Bag 내부 메서드 의존성 제거, Bag 자율화 |
| **4단계** (시도) | TicketOffice에 `sellTicketTo` 추가 | TicketOffice → Audience 새 의존성 발생, 트레이드오프로 **롤백** |

---

## 설계 원칙

| 원칙 | 설명 | 예제에서의 적용 |
|---|---|---|
| **캡슐화** | 객체 내부의 세부사항을 감추고 외부 접근을 제한한다 | TicketSeller에서 `getTicketOffice` 제거, Audience에서 `getBag` 제거 |
| **낮은 결합도** | 객체 사이의 불필요한 의존성을 최소화한다 | Theater가 TicketSeller의 인터페이스에만 의존 |
| **높은 응집도** | 객체가 자신과 밀접하게 연관된 작업만 수행한다 | Audience가 자신의 Bag을 직접 관리 |
| **책임의 이동** | 데이터를 소유한 객체에게 해당 데이터를 처리하는 책임을 부여한다 | Theater에 몰려 있던 로직이 TicketSeller, Audience로 분산 |
| **인터페이스와 구현의 분리** | 객체의 공개 메시지(인터페이스)와 내부 구현을 분리하고 인터페이스만 공개한다 | Theater는 `sellTo`만, TicketSeller는 `buy`만 알면 된다 |
| **의인화** | 무생물이나 추상적 개념도 자율적인 존재로 설계한다 | Bag, TicketOffice도 자율적으로 행동 |
| **트레이드오프** | 설계는 균형의 예술이다. 모든 것을 만족시키는 설계는 없다 | TicketOffice의 자율성보다 결합도 감소를 우선 |

---

## 요약

- **이론보다 실무가 먼저다**: 소프트웨어 설계와 유지보수에서는 추상적 이론보다 코드를 통한 학습이 효과적이다.
- **소프트웨어 모듈의 세 가지 목적**: 제대로 동작할 것, 변경이 용이할 것, 읽는 사람과 의사소통할 것.
- **절차적 프로그래밍의 문제**: 프로세스와 데이터를 분리하면 직관에 위배되고, 변경에 취약하며, 높은 결합도를 초래한다.
- **객체지향 프로그래밍의 핵심**: 데이터와 프로세스를 동일한 객체 안에 배치하여 각 객체가 자율적으로 자신의 데이터를 처리하게 한다.
- **캡슐화**: 객체 내부의 세부사항을 감추면 결합도를 낮추고 변경에 유연한 설계를 얻을 수 있다.
- **책임의 이동**: 절차적 코드에서는 하나의 객체에 책임이 집중되지만, 객체지향 코드에서는 각 객체에 적절히 분산된다.
- **설계는 트레이드오프의 산물**: 모든 것을 만족시키는 완벽한 설계는 없다. 적절한 균형을 찾는 것이 핵심이다.
- **의인화**: 무생물이나 추상적 개념도 능동적이고 자율적인 존재로 설계한다.
- **좋은 설계**: 오늘의 기능을 수행하면서도 내일의 변경을 매끄럽게 수용할 수 있는 설계다.
- **객체지향 설계의 본질**: 협력하는 객체 사이의 의존성을 적절하게 관리하는 것이다.

---

## 다른 챕터와의 관계

- **Chapter 2 (객체지향 프로그래밍)**: 이 장에서 직관적으로 도입한 캡슐화, 의존성 관리, 인터페이스와 구현의 분리 등의 개념을 이론적 기반 위에서 체계적으로 설명한다. 특히 상속, 다형성, 추상화 등 객체지향의 핵심 메커니즘을 통해 유연한 설계를 달성하는 방법을 다룬다.
- **Chapter 3 (역할, 책임, 협력)**: 이 장에서 "책임의 이동"으로 표현한 핵심 아이디어를 역할, 책임, 협력이라는 관점에서 심화한다. 적절한 책임 할당이 좋은 설계의 출발점이라는 이 장의 주장을 구체적인 가이드라인으로 발전시킨다.
- **Chapter 4 (설계 품질과 트레이드오프)**: TicketOffice의 자율성 vs Audience에 대한 결합도라는 트레이드오프 문제를 더 정교한 기준(캡슐화, 응집도, 결합도)으로 분석하는 방법을 제시한다.
