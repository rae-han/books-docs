# Appendix A: Design by Contract (계약에 의한 설계)

## 핵심 질문

6장에서 명령-쿼리 분리 원칙을 통해 인터페이스를 다듬었지만, 명령의 부수 효과를 명확하게 표현하는 데는 한계가 있었다. 인터페이스만으로는 전달할 수 없는 협력의 제약 조건과 부수 효과를 어떻게 명시적으로 문서화하고, 실행 시점에 검증할 수 있는가? 계약에 의한 설계(DBC)는 리스코프 치환 원칙과 어떤 관계를 가지는가?

---

## 1. 인터페이스의 한계와 계약의 필요성

6장에서 의도를 드러내도록 인터페이스를 다듬고 명령과 쿼리를 분리했다 하더라도, 명령으로 인해 발생하는 부수 효과를 명확하게 표현하는 데는 한계가 있다. 주석으로 부수 효과를 서술하는 것도 가능하겠지만, 파급 효과를 명확하게 전달하기가 쉽지 않을뿐더러 시간이 흐를수록 구현을 정확하게 반영하지 못할 가능성도 높다.

메서드의 구현이 단순하다면 내부를 살펴보는 것만으로도 부수 효과를 쉽게 이해할 수 있다. 하지만 구현이 복잡하고 부수 효과를 가진 다수의 메서드들을 연이어 호출하는 코드를 분석하는 경우에는 실행 결과를 예측하기 어려울 수밖에 없다. 캡슐화의 가치는 사라지고 개발자는 복잡하게 얽히고설킨 로직을 이해하기 위해 코드의 구석구석을 파헤쳐야 하는 운명에 처하고 만다.

> **핵심 통찰**: 인터페이스만으로는 객체의 행동에 관한 다양한 관점을 전달하기 어렵다. 명령의 부수 효과를 쉽고 명확하게 표현할 수 있는 커뮤니케이션 수단이 필요하다. 이 시점이 되면 계약에 의한 설계(*Design By Contract, DBC*)가 주는 혜택으로 눈을 돌릴 때가 된 것이다.

계약에 의한 설계를 사용하면 협력에 필요한 다양한 제약과 부수 효과를 **명시적으로 정의하고 문서화**할 수 있다. 클라이언트 개발자는 오퍼레이션의 구현을 살펴보지 않더라도 객체의 사용법을 쉽게 이해할 수 있다. 계약은 실행 가능하기 때문에 구현에 동기화돼 있는지 여부를 런타임에 검증할 수 있다. 따라서 주석과 다르게 시간의 흐름에 뒤처질 걱정을 할 필요가 없다.

### 1.1 부수 효과를 명시적으로

프로그래밍 언어로 작성된 인터페이스는 객체가 수신할 수 있는 메시지는 정의할 수 있지만, 객체 사이의 의사소통 방식은 명확하게 정의할 수 없다. 메시지의 이름과 파라미터 목록은 시그니처를 통해 전달할 수 있지만, 협력을 위해 필요한 약속과 제약은 인터페이스를 통해 전달할 수 없기 때문에 협력과 관련된 상당한 내용이 암시적인 상태로 남게 된다.

6장의 일정 관리 프로그램을 예로 들어 보자. 명령과 쿼리를 분리했기 때문에 `Event` 클래스의 클라이언트는 먼저 `IsSatisfied` 메서드를 호출해서 `RecurringSchedule`의 조건을 만족시키는지 확인한 후에 `Reschedule` 메서드를 호출해야 한다. 인터페이스만으로는 메서드의 순서와 관련된 제약을 설명하기 쉽지 않지만, 계약에 의한 설계 라이브러리인 CodeContracts를 사용하면 이를 명확하게 표현할 수 있다.

<details>
<summary>원문 C# 코드</summary>

```csharp
// C#
class Event
{
    public bool IsSatisfied(RecurringSchedule schedule) { ... }

    public void Reschedule(RecurringSchedule schedule)
    {
        Contract.Requires(IsSatisfied(schedule));
    }
}
```

</details>

```typescript
// TypeScript
class Event {
    isSatisfied(schedule: RecurringSchedule): boolean { /* ... */ }

    reschedule(schedule: RecurringSchedule): void {
        // 사전조건: isSatisfied가 true일 때만 호출 가능
        if (!this.isSatisfied(schedule)) {
            throw new Error("Contract violation: isSatisfied(schedule) must be true");
        }
        // ... 실제 로직
    }
}
```

이 코드가 `if`문을 사용한 일반적인 파라미터 체크 방식과 크게 다르지 않다고 생각할 수도 있다. 하지만 계약에 의한 설계에는 일반적인 정합성 체크와 구분되는 중요한 차이점이 있다.

| 측면 | 일반 정합성 체크 | 계약에 의한 설계 |
|---|---|---|
| **가시성** | 코드 구현 내부에 숨겨져 있어 분석하지 않으면 파악하기 어렵다 | 전용 표기법으로 제약 조건을 명시적으로 표현한다 |
| **분리도** | 일반 로직과 조건 기술 로직이 섞여 있다 | 계약을 일반 로직과 분리해서 서술한다 |
| **강제력** | 개발자가 직접 체크 로직을 빠짐없이 작성해야 한다 | 메서드의 일부로 자동 실행되어 계약을 강제한다 |
| **문서화** | 코드 변경 시 주석이 뒤처질 수 있다 | 코드로부터 문서를 자동 생성하는 도구를 제공한다 |

---

## 2. 계약에 의한 설계

### 2.1 계약의 비유

현재 살고 있는 집을 리모델링하고 싶다고 가정해 보자. 리모델링할 수 있는 전문적인 지식이 부족하기 때문에 적절한 인테리어 전문가에게 작업을 위탁하고 계약을 체결할 것이다. 이 계약은 일반적으로 다음과 같은 특성을 가진다:

- 각 계약 당사자는 계약으로부터 **이익**(*benefit*)을 기대하고 이익을 얻기 위해 **의무**(*obligation*)를 이행한다.
- 각 계약 당사자의 이익과 의무는 **계약서에 문서화**된다.

여기서 눈여겨볼 부분은 **한쪽의 의무가 반대쪽의 권리가 된다**는 것이다.

| 당사자 | 의무 | 이익 |
|---|---|---|
| **고객** (위탁자) | 인테리어 전문가에게 대금을 지급한다 | 원하는 품질로 리모델링된 집을 얻는다 |
| **인테리어 전문가** (수행자) | 고객이 원하는 품질로 집을 리모델링한다 | 대금을 지급받는다 |

두 계약 당사자 중 어느 한쪽이라도 계약서에 명시된 내용을 위반한다면 계약은 정상적으로 완료되지 않는다. 또한 여러분이 계약상 고용주라고 하더라도 인테리어 전문가가 계약을 이행하는 **구체적인 방식에 대해서는 간섭하지 않는다**. 리모델링 공사를 진행하는 구체적인 방법은 인테리어 전문가가 자유롭게 결정할 수 있다.

이처럼 계약은 협력을 명확하게 정의하고 커뮤니케이션할 수 있는 범용적인 아이디어다. 사람들이 협력을 위해 사용하는 계약이라는 아이디어를 객체들이 협력하는 방식에도 적용할 수 있지 않을까?

### 2.2 버트란드 마이어의 계약에 의한 설계

버트란드 마이어(*Bertrand Meyer*)는 Eiffel 언어를 만들면서 사람들 사이의 계약에 착안해 계약에 의한 설계 기법을 고안했다. 그가 제시한 계약의 개념은 사람들 사이의 계약과 유사하다:

- 협력에 참여하는 각 객체는 계약으로부터 **이익을 기대**하고 이익을 얻기 위해 **의무를 이행**한다.
- 협력에 참여하는 각 객체의 이익과 의무는 객체의 **인터페이스 상에 문서화**된다.

계약에 의한 설계 개념은 "인터페이스에 대해 프로그래밍하라"는 원칙을 확장한 것이다. 오퍼레이션의 시그니처를 구성하는 다양한 요소들을 이용해 협력에 참여하는 객체들이 지켜야 하는 제약 조건을 명시할 수 있다.

### 2.3 오퍼레이션의 시그니처가 전달하는 정보

Java로 작성된 `reserve` 메서드의 구성 요소를 살펴보자.

```
가시성    반환 타입    메서드 이름     파라미터
  ↓         ↓           ↓             ↓
public  Reservation  reserve(Customer customer, int audienceCount)
```

이 메서드의 시그니처는 다음과 같은 협력을 위한 정보를 제공한다:

- `public` 가시성을 가지므로 외부에서 호출 가능하다
- `Customer` 타입과 `int` 타입의 인자를 전달해야 한다
- 실행이 성공하면 `Reservation` 인스턴스를 반환한다

6장에서 설명한 의도를 드러내는 인터페이스를 만들면 오퍼레이션의 시그니처만으로도 어느 정도까지는 클라이언트와 서버가 협력을 위해 수행해야 하는 제약 조건을 명시할 수 있다.

### 2.4 계약의 세 가지 요소

계약은 여기서 한 걸음 더 나아간다. `reserve` 메서드를 호출할 때 클라이언트는 `customer`의 값으로 `null`을 전달할 수 있고 `audienceCount`의 값으로 음수를 포함한 어떤 정수도 전달할 수 있다고 가정할지 모른다. 하지만 사실 이 메서드는 한 명 이상의 예약자에 대해 예약 정보를 생성해야 하므로 `customer`는 `null`이어서는 안 되고 `audienceCount`의 값은 1보다 크거나 최소한 같아야 한다.

서버는 자신이 처리할 수 있는 범위의 값들을 클라이언트가 전달할 것이라고 기대한다. 클라이언트는 자신이 원하는 값을 서버가 반환할 것이라고 예상한다. 클라이언트는 메시지 전송 전과 후의 서버의 상태가 정상일 것이라고 기대한다. 이 세 가지 기대가 바로 계약에 의한 설계를 구성하는 세 가지 요소에 대응된다.

| 요소 | 정의 | 책임 |
|---|---|---|
| **사전조건**(*Precondition*) | 메서드가 호출되기 위해 만족돼야 하는 조건. 메서드의 요구사항을 명시한다. 사전조건이 만족되지 않을 경우 메서드가 실행돼서는 안 된다. | **클라이언트**의 의무 |
| **사후조건**(*Postcondition*) | 메서드가 실행된 후에 클라이언트에게 보장해야 하는 조건. 클라이언트가 사전조건을 만족시켰다면 메서드는 사후조건에 명시된 조건을 만족시켜야 한다. 만족시키지 못한 경우에는 클라이언트에게 예외를 던져야 한다. | **서버**의 의무 |
| **불변식**(*Invariant*) | 항상 참이라고 보장되는 서버의 조건. 메서드가 실행되는 도중에는 불변식을 만족시키지 못할 수도 있지만, 메서드를 실행하기 전이나 종료된 후에 불변식은 항상 참이어야 한다. | **서버 클래스** 전체의 의무 |

> **핵심 통찰**: 사전조건, 사후조건, 불변식을 기술할 때는 실행 절차를 기술할 필요 없이 **상태 변경만을 명시**하기 때문에 코드를 이해하고 분석하기 쉬워진다. 클라이언트 개발자가 알아야 하는 모든 것이 사전조건, 사후조건, 불변식에 포함돼 있다.

```
클라이언트                        서버
    │                              │
    │  ① 사전조건 만족시키기        │
    │  (클라이언트의 의무)           │
    │──── 메서드 호출 ────────────▶│
    │                              │  ② 사후조건 만족시키기
    │                              │  (서버의 의무)
    │◀──── 결과 반환 ─────────────│
    │                              │
    │     [불변식: 호출 전/후 항상 참]│
```

---

## 3. 사전조건

사전조건(*Precondition*)이란 메서드가 정상적으로 실행되기 위해 만족해야 하는 조건이다. 사전조건을 만족시키는 것은 메서드를 실행하는 **클라이언트의 의무**다. 사전조건을 만족시키지 못해서 메서드가 실행되지 않을 경우 클라이언트에 버그가 있다는 것을 의미한다. 사전조건이 만족되지 않을 경우 서버는 메서드를 실행할 의무가 없다.

일반적으로 사전조건은 메서드에 전달된 **인자의 정합성을 체크**하기 위해 사용된다. `Reserve` 메서드의 경우 인자로 전달된 `customer`가 `null`이 아니어야 하고 `audienceCount`의 값은 1보다 크거나 같아야 한다.

<details>
<summary>원문 C# 코드</summary>

```csharp
// C#
public Reservation Reserve(Customer customer, int audienceCount)
{
    Contract.Requires(customer != null);
    Contract.Requires(audienceCount >= 1);

    return new Reservation(customer, this, calculateFee(audienceCount), audienceCount);
}
```

</details>

```typescript
// TypeScript
class Screening {
    reserve(customer: Customer, audienceCount: number): Reservation {
        // 사전조건
        console.assert(customer != null, "customer must not be null");
        console.assert(audienceCount >= 1, "audienceCount must be >= 1");

        return new Reservation(customer, this, this.calculateFee(audienceCount), audienceCount);
    }
}
```

사전조건을 만족시킬 책임은 `reserve` 메서드를 호출하는 클라이언트에게 있다. 클라이언트가 사전조건을 만족시키지 못할 경우 메서드는 **최대한 빨리 실패**해서 클라이언트에게 버그가 있다는 사실을 알린다.

---

## 4. 사후조건

사후조건(*Postcondition*)은 메서드의 실행 결과가 올바른지를 검사하고 실행 후에 객체가 유효한 상태로 남아 있는지를 검증한다. 클라이언트가 사전조건을 만족시켰는데도 서버가 사후조건을 만족시키지 못한다면 **서버에 버그**가 있음을 의미한다.

일반적으로 사후조건은 다음과 같은 세 가지 용도로 사용된다:

1. **인스턴스 변수의 상태**가 올바른지를 서술하기 위해
2. **메서드에 전달된 파라미터의 값**이 올바르게 변경됐는지를 서술하기 위해
3. **반환값**이 올바른지를 서술하기 위해

### 4.1 사후조건 정의의 어려움

다음 두 가지 이유로 사전조건보다 사후조건을 정의하는 것이 더 어려울 수 있다:

| 어려움 | 설명 | 해결 방법 |
|---|---|---|
| **여러 return 문** | 한 메서드 안에서 `return` 문이 여러 번 나올 경우 모든 `return` 문마다 반환값이 올바른지 검증하는 코드를 추가해야 한다 | 대부분의 DBC 라이브러리는 반환값에 대한 사후조건을 **한 번만 기술**할 수 있게 해준다 |
| **실행 전/후 값 비교** | 실행 전의 값이 메서드 실행으로 인해 다른 값으로 변경됐을 수 있어 두 값을 비교하기 어렵다 | 대부분의 DBC 라이브러리는 **실행 전의 값에 접근**할 수 있는 간편한 방법을 제공한다 |

### 4.2 반환값 사후조건

`Reserve` 메서드의 사후조건은 반환값인 `Reservation` 인스턴스가 `null`이어서는 안 된다는 것이다.

<details>
<summary>원문 C# 코드</summary>

```csharp
// C#
public Reservation Reserve(Customer customer, int audienceCount)
{
    Contract.Requires(customer != null);
    Contract.Requires(audienceCount >= 1);
    Contract.Ensures(Contract.Result<Reservation>() != null);

    return new Reservation(customer, this, calculateFee(audienceCount), audienceCount);
}
```

</details>

```typescript
// TypeScript
class Screening {
    reserve(customer: Customer, audienceCount: number): Reservation {
        // 사전조건
        console.assert(customer != null);
        console.assert(audienceCount >= 1);

        const result = new Reservation(customer, this, this.calculateFee(audienceCount), audienceCount);

        // 사후조건
        console.assert(result != null, "result must not be null");

        return result;
    }
}
```

### 4.3 여러 return 문에 대한 사후조건

`Buy` 메서드는 초대장이 있을 경우에는 0원을, 없을 경우에는 티켓의 요금을 반환한다. 두 개의 `return` 문이 존재하지만, CodeContracts의 `Contract.Result<T>` 메서드를 사용하면 메서드 실행이 끝난 후 실제로 반환되는 값을 전달하기 때문에 사후조건을 **한 번만 기술**하면 된다.

<details>
<summary>원문 C# 코드</summary>

```csharp
// C#
public decimal Buy(Ticket ticket)
{
    Contract.Requires(ticket != null);
    Contract.Ensures(Contract.Result<decimal>() >= 0);

    if (bag.Invited)
    {
        bag.Ticket = ticket;
        return 0;
    }
    else
    {
        bag.Ticket = ticket;
        bag.MinusAmount(ticket.Fee);
        return ticket.Fee;
    }
}
```

</details>

```typescript
// TypeScript
class Audience {
    buy(ticket: Ticket): number {
        // 사전조건
        console.assert(ticket != null);

        let result: number;
        if (this.bag.invited) {
            this.bag.ticket = ticket;
            result = 0;
        } else {
            this.bag.ticket = ticket;
            this.bag.minusAmount(ticket.fee);
            result = ticket.fee;
        }

        // 사후조건: 한 번만 기술
        console.assert(result >= 0, "result must be >= 0");

        return result;
    }
}
```

### 4.4 실행 전 값에 접근하기

`Contract.OldValue<T>`를 이용하면 메서드 실행 전의 상태에 접근할 수 있다. 아래 코드에서 파라미터 `text`의 값이 메서드 실행 중에 변경되기 때문에 `text`의 값을 이용하는 사후조건이 정상적으로 체크되지 않는 문제가 발생한다.

<details>
<summary>원문 C# 코드</summary>

```csharp
// C# - 문제 버전
public string Middle(string text)
{
    Contract.Requires(text != null && text.Length >= 2);
    // text가 변경되므로 이 사후조건은 정상 동작하지 않음
    Contract.Ensures(Contract.Result<string>().Length < text.Length);

    text = text.Substring(1, text.Length - 2);
    return text.Trim();
}

// C# - 해결 버전
public string Middle(string text)
{
    Contract.Requires(text != null && text.Length >= 2);
    // OldValue로 실행 전 text 값에 접근
    Contract.Ensures(Contract.Result<string>().Length < Contract.OldValue<string>(text).Length);

    text = text.Substring(1, text.Length - 2);
    return text.Trim();
}
```

</details>

```typescript
// TypeScript
class StringProcessor {
    middle(text: string): string {
        // 사전조건
        console.assert(text != null && text.length >= 2);

        // 실행 전 값을 저장 (OldValue에 해당)
        const oldTextLength = text.length;

        text = text.substring(1, text.length - 1);
        const result = text.trim();

        // 사후조건: 실행 전 값과 비교
        console.assert(result.length < oldTextLength, "result must be shorter than original");

        return result;
    }
}
```

---

## 5. 불변식

사전조건과 사후조건은 각 메서드마다 달라지는 데 반해, 불변식(*Invariant*)은 인스턴스 생명주기 전반에 걸쳐 지켜져야 하는 규칙을 명세한다. 일반적으로 불변식은 **객체의 내부 상태**와 관련이 있다.

### 5.1 불변식의 두 가지 특성

1. **생성 후 만족**: 불변식은 클래스의 모든 인스턴스가 생성된 후에 만족돼야 한다. 이것은 클래스에 정의된 모든 생성자가 불변식을 준수해야 한다는 것을 의미한다.
2. **메서드 전후 만족**: 불변식은 클라이언트에 의해 호출 가능한 모든 메서드에 의해 준수돼야 한다. 메서드가 실행되는 중에는 객체의 상태가 불안정한 상태로 빠질 수 있기 때문에 불변식을 만족시킬 필요는 없지만, 메서드 실행 전과 종료 후에는 항상 불변식을 만족하는 상태가 유지돼야 한다.

> **핵심 통찰**: 불변식은 클래스의 모든 메서드의 사전조건과 사후조건에 추가되는 **공통의 조건**으로 생각할 수 있다. 불변식은 메서드가 실행되기 전에 사전조건과 함께 실행되며, 메서드가 실행된 후에 사후조건과 함께 실행된다.

### 5.2 Screening에 불변식 추가하기

`Screening`의 인스턴스가 생성되면 `movie`는 `null`이 아니어야 하고 `sequence`는 1보다 크거나 같아야 하며, `whenScreened`는 현재 시간 이후여야 한다.

<details>
<summary>원문 C# 코드</summary>

```csharp
// C#
public class Screening
{
    private Movie movie;
    private int sequence;
    private DateTime whenScreened;

    [ContractInvariantMethod]
    private void Invariant()
    {
        Contract.Invariant(movie != null);
        Contract.Invariant(sequence >= 1);
        Contract.Invariant(whenScreened > DateTime.Now);
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

        // 불변식 체크 (생성자 종료 시점)
        this.checkInvariant();
    }

    private checkInvariant(): void {
        console.assert(this.movie != null, "movie must not be null");
        console.assert(this.sequence >= 1, "sequence must be >= 1");
        console.assert(this.whenScreened > new Date(), "whenScreened must be in the future");
    }

    reserve(customer: Customer, audienceCount: number): Reservation {
        this.checkInvariant(); // 메서드 실행 전

        // ... 메서드 로직 ...

        this.checkInvariant(); // 메서드 종료 후
        return result;
    }
}
```

CodeContracts 덕분에 객체의 생성자나 메서드 실행 전후에 불변식을 직접 호출해야 하는 수고를 덜 수 있다. `ContractInvariantMethod` 어트리뷰트가 지정된 메서드를 불변식을 체크해야 하는 모든 지점에 자동으로 추가한다.

---

## 6. 계약에 의한 설계와 서브타이핑

지금까지 살펴본 것처럼 계약에 의한 설계의 핵심은 클라이언트와 서버 사이의 견고한 협력을 위해 준수해야 하는 규약을 정의하는 것이다. 여기서 핵심 단어는 **'클라이언트'**다. 계약에 의한 설계는 클라이언트가 만족시켜야 하는 사전조건과 클라이언트의 관점에서 서버가 만족시켜야 하는 사후조건을 기술한다.

**계약에 의한 설계와 리스코프 치환 원칙이 만나는 지점**이 바로 이곳이다. 리스코프 치환 원칙은 슈퍼타입의 인스턴스와 협력하는 클라이언트의 관점에서 서브타입의 인스턴스가 슈퍼타입을 대체하더라도 협력에 지장이 없어야 한다는 것을 의미한다. 따라서 다음과 같이 정리할 수 있다:

> 서브타입이 리스코프 치환 원칙을 만족시키기 위해서는 클라이언트와 슈퍼타입 간에 체결된 **계약을 준수**해야 한다.

리스코프 치환 원칙의 규칙을 두 가지 종류로 세분화할 수 있다:

| 규칙 종류 | 설명 | 세부 규칙 |
|---|---|---|
| **계약 규칙**(*Contract Rules*) | 슈퍼타입과 서브타입 사이의 사전조건, 사후조건, 불변식에 관한 제약 규칙 | ① 서브타입에 더 강력한 사전조건을 정의할 수 없다 ② 서브타입에 더 완화된 사후조건을 정의할 수 없다 ③ 슈퍼타입의 불변식은 서브타입에서도 반드시 유지돼야 한다 |
| **가변성 규칙**(*Variance Rules*) | 파라미터와 리턴 타입의 변형과 관련된 규칙 | ① 서브타입의 메서드 파라미터는 반공변성을 가져야 한다 ② 서브타입의 리턴 타입은 공변성을 가져야 한다 ③ 서브타입은 슈퍼타입이 발생시키는 예외와 다른 타입의 예외를 발생시켜서는 안 된다 |

---

## 7. 계약 규칙

11장에서 살펴본 핸드폰 과금 시스템의 합성 버전을 예제로 사용한다. `RatePolicy`는 기본 정책과 부가 정책을 구현하는 모든 객체들이 실체화해야 하는 인터페이스다.

```
              Phone
                │ ratePolicy
                ▼
         «interface»
          RatePolicy ◀──────────────────────┐
       calculateFee(calls)                  │ next
                ▲                           │
        ┌───────┴────────┐          ┌───────┴─────────┐
  BasicRatePolicy    AdditionalRatePolicy
  - calculateFee()   - calculateFee()
  # calculateCallFee()  # afterCalculated()
        ▲                       ▲
   ┌────┴────┐            ┌─────┴──────┐
Regular  Nightly     Taxable   RateDiscount
Policy   Discount    Policy    ablePolicy
         Policy
```

### 7.1 Phone의 publishBill 메서드

요금 청구서를 발행하는 `publishBill` 메서드를 `Phone`에 추가한다. 청구서(`Bill`)는 요금 청구의 대상인 핸드폰(`phone`)과 통화 요금(`fee`)을 인스턴스 변수로 포함한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Bill {
    private Phone phone;
    private Money fee;

    public Bill(Phone phone, Money fee) {
        if (phone == null) {
            throw new IllegalArgumentException();
        }
        if (fee.isLessThan(Money.ZERO)) {
            throw new IllegalArgumentException();
        }
        this.phone = phone;
        this.fee = fee;
    }
}

public class Phone {
    private RatePolicy ratePolicy;
    private List<Call> calls = new ArrayList<>();

    public Phone(RatePolicy ratePolicy) {
        this.ratePolicy = ratePolicy;
    }

    public void call(Call call) {
        calls.add(call);
    }

    public Bill publishBill() {
        return new Bill(this, ratePolicy.calculateFee(calls));
    }
}
```

</details>

```typescript
// TypeScript
class Bill {
    private phone: Phone;
    private fee: Money;

    constructor(phone: Phone, fee: Money) {
        if (phone == null) {
            throw new Error("phone must not be null");
        }
        if (fee.isLessThan(Money.ZERO)) {
            throw new Error("fee must be >= 0");
        }
        this.phone = phone;
        this.fee = fee;
    }
}

class Phone {
    private ratePolicy: RatePolicy;
    private calls: Call[] = [];

    constructor(ratePolicy: RatePolicy) {
        this.ratePolicy = ratePolicy;
    }

    call(call: Call): void {
        this.calls.push(call);
    }

    publishBill(): Bill {
        return new Bill(this, this.ratePolicy.calculateFee(this.calls));
    }
}
```

`publishBill` 메서드에서 `calculateFee`의 반환값을 `Bill`의 생성자에 전달한다는 부분에 주목하라. 청구서의 요금은 최소한 0원보다 크거나 같아야 하므로 `calculateFee`의 반환값은 0원보다 커야 한다.

따라서 `RatePolicy`의 `calculateFee`에 대한 계약은 다음과 같이 정의할 수 있다:

- **사전조건**: `calls != null`
- **사후조건**: `result.isGreaterThanOrEqual(Money.ZERO)`

### 7.2 서브타입에 더 강력한 사전조건을 정의할 수 없다

한 번도 통화가 발생하지 않은 `Phone`에 대한 청구서를 발행하는 시나리오를 고려해 보자.

```typescript
// TypeScript
const phone = new Phone(new RegularPolicy(Money.wons(100), Duration.ofSeconds(10)));
const bill = phone.publishBill();
```

`Phone`의 코드를 보면 내부적으로 통화 목록을 유지하는 인스턴스 변수 `calls`를 선언하는 동시에 빈 리스트로 초기화한다. 따라서 한 번도 `call` 메서드가 호출되지 않은 경우 `calculateFee` 메서드 인자로 **빈 리스트**가 전달될 것이다. `calculateFee`의 사전조건에서는 인자가 `null`인 경우를 제외하고는 모든 값을 허용하기 때문에 위 코드는 사전조건을 위반하지 않는다.

하지만 `BasicRatePolicy`에 `calls`가 빈 리스트여서는 안 된다는 **더 강력한 사전조건**을 추가하면 어떻게 될까?

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public abstract class BasicRatePolicy implements RatePolicy {
    @Override
    public Money calculateFee(List<Call> calls) {
        // 사전조건 (강화!)
        assert calls != null;
        assert !calls.isEmpty(); // 빈 리스트 불허
        // ...
    }
}
```

</details>

```typescript
// TypeScript
abstract class BasicRatePolicy implements RatePolicy {
    calculateFee(calls: Call[]): Money {
        // 사전조건 (강화!)
        console.assert(calls != null);
        console.assert(calls.length > 0); // 빈 배열 불허 — 문제!
        // ...
    }
}
```

클라이언트인 `Phone`은 오직 `RatePolicy` 인터페이스만 알고 있기 때문에 `null`을 제외한 어떤 `calls`라도 받아들인다고 가정한다. 따라서 빈 리스트를 전달하더라도 문제가 발생하지 않는다고 예상할 것이다.

하지만 `BasicRatePolicy`는 사전조건에 새로운 조건을 추가함으로써 `Phone`과 `RatePolicy` 사이에 맺은 **계약을 위반**한다. 클라이언트의 관점에서 `BasicRatePolicy`는 `RatePolicy`를 대체할 수 없기 때문에 **리스코프 치환 원칙을 위반**한다.

> **핵심 통찰**: 계약서에 명시된 의무보다 더 많은 의무를 짊어져야 한다는 사실을 순순히 납득하는 클라이언트는 없다. 사전조건을 강화한 서브타입은 클라이언트의 입장에서 수용이 불가능하기 때문에 슈퍼타입을 대체할 수 없게 된다.

반대로 사전조건을 **완화**시키는 경우는 어떨까? `calls`가 `null`인 인자를 전달해도 예외가 발생하지 않도록 수정한다면, 이미 클라이언트는 `null`이 아닌 값을 전달하도록 보장하고 있으므로 `null` 여부를 체크하는 조건문은 무시된다. 결과적으로 사전조건을 완화시키는 것은 리스코프 치환 원칙을 **위반하지 않는다**.

### 7.3 서브타입에 더 완화된 사후조건을 정의할 수 없다

10초당 100원을 부과하는 일반 요금제(`RegularPolicy`)에 1000원을 할인해 주는 기본 요금 할인 정책(`RateDiscountablePolicy`)을 적용하는 시나리오를 살펴보자.

```typescript
// TypeScript
const phone = new Phone(
    new RateDiscountablePolicy(
        Money.wons(1000),
        new RegularPolicy(Money.wons(100), Duration.ofSeconds(10))
    )
);
phone.call(new Call(
    new Date(2017, 0, 1, 10, 10),
    new Date(2017, 0, 1, 10, 11)
));
const bill = phone.publishBill();
```

통화 시간은 1분이므로 통화 요금은 600원이다. 문제는 1000원의 기본 요금 할인 정책이 추가돼 있다는 것이다. 할인 금액을 반영한 최종 청구 금액은 600원에서 1000원을 뺀 **-400원**이 될 것이다.

`calculateFee` 오퍼레이션은 반환값이 0원보다 커야 한다는 사후조건을 정의하고 있다. 사후조건을 만족시킬 책임은 서버에 있다. 서버인 `RateDiscountablePolicy`는 계약을 만족시킬 수 없다는 사실을 안 즉시 **예외를 발생**시키기 때문에 `calculateFee` 오퍼레이션은 정상적으로 실행되지 않고 종료된다.

이제 `AdditionalRatePolicy`에서 사후조건을 완화시켜 마이너스 요금이 반환되더라도 예외가 발생하지 않도록 수정한다고 가정해 보자.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public abstract class AdditionalRatePolicy implements RatePolicy {
    @Override
    public Money calculateFee(List<Call> calls) {
        assert calls != null;
        Money fee = next.calculateFee(calls);
        Money result = afterCalculated(fee);

        // 사후조건 (완화! — 주석 처리)
        // assert result.isGreaterThanOrEqual(Money.ZERO);

        return result;
    }
}
```

</details>

```typescript
// TypeScript
abstract class AdditionalRatePolicy implements RatePolicy {
    calculateFee(calls: Call[]): Money {
        console.assert(calls != null);
        const fee = this.next.calculateFee(calls);
        const result = this.afterCalculated(fee);

        // 사후조건 (완화! — 주석 처리)
        // console.assert(result.isGreaterThanOrEqual(Money.ZERO));

        return result;
    }
}
```

이제 `AdditionalRatePolicy`는 마이너스 금액도 반환할 수 있기 때문에 `Phone`과의 협력을 문제없이 처리할 수 있다. 하지만 엉뚱하게도 `Bill`의 생성자에서 예외가 발생한다. `Bill`의 생성자에서는 인자로 전달된 `fee`가 마이너스 금액일 경우 예외를 던지도록 구현돼 있기 때문이다.

문제는 `Bill`이 아니다. `Bill`의 입장에서 요금이 0원보다 크거나 같다고 가정하는 것은 자연스럽다. 문제는 `AdditionalRatePolicy`가 **사후조건을 완화**함으로써 기존에 `Phone`과 `RatePolicy` 사이에 체결된 계약을 위반했기 때문에 발생한 것이다.

> 계약서에 명시된 이익보다 더 적은 이익을 받게 된다는 사실을 납득할 수 있는 클라이언트가 있을까? 사후조건을 완화시키는 서버는 클라이언트의 관점에서 수용할 수 없기 때문에 슈퍼타입을 대체할 수 없다. **사후조건 완화는 리스코프 치환 원칙 위반이다.**

반대로 사후조건을 **강화**하는 경우는 어떨까? `calculateFee` 메서드가 100원보다 크거나 같은 금액을 반환하도록 사후조건을 강화해도, `Phone`은 반환된 요금이 0원보다 크기만 하다면 아무런 불만도 가지지 않기 때문에 클라이언트에게 영향을 미치지 않는다. 요금이 100원보다 크다고 하더라도 어차피 그 금액은 0원보다는 큰 것이다. 따라서 사후조건 강화는 계약에 영향을 미치지 않는다.

### 7.4 일찍 실패하기 (Fail Fast)

> 처음에는 의아하게 생각될 수도 있지만 마이너스 금액을 그대로 사용하는 것보다 처리를 종료하는 것이 올바른 선택이다. 클라이언트인 `Phone`은 서버가 계약에 명시된 사후조건을 만족시킬 것이라고 가정하기 때문에 반환값을 체크할 필요가 없다. 따라서 `Phone`은 항상 플러스 금액을 반환할 것이라고 가정하고 별도의 확인 없이 반환값을 그대로 `Bill`의 생성자에게 전달한다. 그 결과, **원인에서 멀리 떨어진 엉뚱한 곳에서 경보음이 울리게 되는 것이다.**

> 가능한 한 빨리 문제를 발견하게 되면 좀 더 일찍 시스템을 멈출 수 있다는 이득이 있다. 게다가 프로그램을 멈추는 것이 할 수 있는 최선일 때가 많다. 방금 불가능한 뭔가가 발생했다는 것을 코드가 발견한다면 프로그램은 더 이상 유효하지 않다고 할 수 있다. 일반적으로, **죽은 프로그램이 입히는 피해는 절름발이 프로그램이 끼치는 것보다 훨씬 덜한 법이다.** — [Hunt99]

### 7.5 슈퍼타입의 불변식은 서브타입에서도 반드시 유지돼야 한다

불변식은 메서드가 실행되기 전과 후에 반드시 만족시켜야 하는 조건이다. `AdditionalRatePolicy`에서 다음 요금제를 가리키는 `next`는 `null`이어서는 안 된다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public abstract class AdditionalRatePolicy implements RatePolicy {
    protected RatePolicy next;

    public AdditionalRatePolicy(RatePolicy next) {
        this.next = next;
        // 불변식
        assert next != null;
    }

    @Override
    public Money calculateFee(List<Call> calls) {
        // 불변식
        assert next != null;
        // 사전조건
        assert calls != null;

        Money fee = next.calculateFee(calls);
        Money result = afterCalculated(fee);

        // 사후조건
        assert result.isGreaterThanOrEqual(Money.ZERO);
        // 불변식
        assert next != null;

        return result;
    }
}
```

</details>

```typescript
// TypeScript
abstract class AdditionalRatePolicy implements RatePolicy {
    protected next: RatePolicy; // protected — 문제의 원인!

    constructor(next: RatePolicy) {
        this.next = next;
        console.assert(this.next != null); // 불변식
    }

    calculateFee(calls: Call[]): Money {
        console.assert(this.next != null); // 불변식
        console.assert(calls != null);     // 사전조건

        const fee = this.next.calculateFee(calls);
        const result = this.afterCalculated(fee);

        console.assert(result.isGreaterThanOrEqual(Money.ZERO)); // 사후조건
        console.assert(this.next != null);                        // 불변식

        return result;
    }

    protected abstract afterCalculated(fee: Money): Money;
}
```

하지만 위 코드에는 불변식을 위반할 수 있는 취약점이 존재한다. 인스턴스 변수 `next`가 `private`이 아니라 **`protected`** 변수라는 사실에 주목하라. 자식 클래스는 부모 클래스 몰래 `next`의 값을 수정하는 것이 가능하다.

```typescript
// TypeScript
class RateDiscountablePolicy extends AdditionalRatePolicy {
    changeNext(next: RatePolicy | null): void {
        this.next = next!; // 부모의 protected 필드를 직접 변경
    }
}

// 불변식 위반!
const policy = new RateDiscountablePolicy(
    Money.wons(1000),
    new RegularPolicy(Money.wons(100), Duration.ofSeconds(10))
);
policy.changeNext(null); // next가 null이 됨 — 불변식 위반
```

> **핵심 통찰**: 계약의 관점에서 캡슐화의 중요성을 잘 보여준다. 자식 클래스가 계약을 위반할 수 있는 코드를 작성하는 것을 막을 수 있는 유일한 방법은 인스턴스 변수의 가시성을 `protected`가 아니라 **`private`**으로 만드는 것뿐이다. `protected` 인스턴스 변수를 가진 부모 클래스의 불변성은 자식 클래스에 의해 언제라도 쉽게 무너질 수 있다.

해결책은 인스턴스 변수를 `private`으로 제한하고, 자식 클래스에서 상태를 변경해야 할 경우 **`protected` 메서드**를 통해 불변식을 체크하는 것이다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public abstract class AdditionalRatePolicy implements RatePolicy {
    private RatePolicy next;

    public AdditionalRatePolicy(RatePolicy next) {
        changeNext(next);
    }

    protected void changeNext(RatePolicy next) {
        this.next = next;
        // 불변식
        assert next != null;
    }
}
```

</details>

```typescript
// TypeScript
abstract class AdditionalRatePolicy implements RatePolicy {
    private next: RatePolicy; // private으로 변경

    constructor(next: RatePolicy) {
        this.changeNext(next);
    }

    protected changeNext(next: RatePolicy): void {
        this.next = next;
        // 불변식 체크
        console.assert(this.next != null, "next must not be null");
    }
}
```

---

## 8. 가변성 규칙

### 8.1 서브타입은 슈퍼타입이 발생시키는 예외와 다른 타입의 예외를 발생시켜서는 안 된다

`RatePolicy`의 `calculateFee` 오퍼레이션이 인자로 빈 리스트를 전달받았을 때 `EmptyCallException` 예외를 던지도록 계약을 수정해 보자.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class EmptyCallException extends RuntimeException { ... }

public interface RatePolicy {
    Money calculateFee(List<Call> calls) throws EmptyCallException;
}

public abstract class BasicRatePolicy implements RatePolicy {
    @Override
    public Money calculateFee(List<Call> calls) {
        if (calls == null || calls.isEmpty()) {
            throw new EmptyCallException();
        }
        // ...
    }
}
```

</details>

```typescript
// TypeScript
class EmptyCallException extends Error {
    constructor() { super("Empty call list"); }
}

interface RatePolicy {
    calculateFee(calls: Call[]): Money; // throws EmptyCallException
}

abstract class BasicRatePolicy implements RatePolicy {
    calculateFee(calls: Call[]): Money {
        if (calls == null || calls.length === 0) {
            throw new EmptyCallException();
        }
        // ...
    }
}
```

`RatePolicy`와 협력하는 메서드가 `EmptyCallException` 예외를 캐치한 후 0원을 반환한다고 가정하자.

```typescript
// TypeScript
function calculate(policy: RatePolicy, calls: Call[]): Money {
    try {
        return policy.calculateFee(calls);
    } catch (ex) {
        if (ex instanceof EmptyCallException) {
            return Money.ZERO;
        }
        throw ex;
    }
}
```

하지만 `AdditionalRatePolicy`가 `EmptyCallException`이 아닌 `NoneElementException`을 던진다면 어떻게 될까?

만약 `NoneElementException`이 `EmptyCallException`의 **자식 클래스**라면 `catch` 블록에서 잡히기 때문에 대체 가능하다:

```
RuntimeException
    └── EmptyCallException
            └── NoneElementException  ← 잡힘 (대체 가능)
```

하지만 **상속 계층이 다르다면** 하나의 `catch`문으로 두 예외 모두를 처리할 수 없기 때문에 대체 불가능하다:

```
RuntimeException
    ├── EmptyCallException      ← catch가 잡는 예외
    └── NoneElementException    ← 잡히지 않음 (대체 불가!)
```

### 8.2 Penguin 문제: 예외와 퇴화 메서드

이 규칙의 변형으로 13장에서 소개한 `Bird`를 상속받는 `Penguin`의 예가 있다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Bird {
    public void fly() { ... }
}

// 방법 1: 예외를 던지는 경우
public class Penguin extends Bird {
    @Override
    public void fly() {
        throw new UnsupportedOperationException();
    }
}

// 방법 2: 아무것도 하지 않는 경우
public class Penguin extends Bird {
    @Override
    public void fly() {
        // 아무것도 하지 않음
    }
}
```

</details>

```typescript
// TypeScript
class Bird {
    fly(): void { /* 날기 구현 */ }
}

// 방법 1: 예외를 던지는 경우
class Penguin extends Bird {
    override fly(): void {
        throw new Error("UnsupportedOperation: Penguins can't fly");
    }
}

// 방법 2: 아무것도 하지 않는 경우
class Penguin extends Bird {
    override fly(): void {
        // 아무것도 하지 않음
    }
}
```

클라이언트는 협력하는 모든 `Bird`가 날 수 있다고 생각할 것이다. 예외를 던지든 아무것도 하지 않든, 클라이언트의 관점에서 자식 클래스가 부모 클래스가 하는 일보다 **더 적은 일을 수행한다**는 공통점이 있다. **부모 클래스보다 못한 자식 클래스는 서브타입이 아니다.**

---

## 9. 공변성, 반공변성, 무공변성

### 9.1 개념 정의

S가 T의 서브타입이라고 할 때, 프로그램의 어떤 위치에서 두 타입 사이의 치환 가능성을 다음과 같이 나눠볼 수 있다:

| 개념 | 정의 | 설명 |
|---|---|---|
| **공변성**(*Covariance*) | S와 T 사이의 서브타입 관계가 **그대로 유지**된다 | 서브타입인 S가 슈퍼타입인 T 대신 사용될 수 있다. 흔히 이야기하는 리스코프 치환 원칙은 공변성과 관련된 원칙이다. |
| **반공변성**(*Contravariance*) | S와 T 사이의 서브타입 관계가 **역전**된다 | 슈퍼타입인 T가 서브타입인 S 대신 사용될 수 있다. |
| **무공변성**(*Invariance*) | S와 T 사이에는 **아무런 관계도 존재하지 않는다** | S 대신 T를 사용하거나 T 대신 S를 사용할 수 없다. |

### 9.2 리턴 타입 공변성

이해를 돕기 위해 세 개의 상속 계층을 살펴보자.

```
   Book          Publisher        BookStall
     ▲               ▲               ▲
     │               │               │
  Magazine    IndependentPublisher  MagazineStore
```

`BookStall`의 `sell` 메서드는 `Book`의 인스턴스를 리턴하고, `MagazineStore`의 `sell` 메서드는 `Magazine`의 인스턴스를 리턴한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class BookStall {
    public Book sell(IndependentPublisher publisher) {
        return new Book(publisher);
    }
}

public class MagazineStore extends BookStall {
    @Override
    public Magazine sell(IndependentPublisher publisher) {
        return new Magazine(publisher);
    }
}

public class Customer {
    private Book book;

    public void order(BookStall bookStall) {
        this.book = bookStall.sell(new IndependentPublisher());
    }
}
```

</details>

```typescript
// TypeScript
class BookStall {
    sell(publisher: IndependentPublisher): Book {
        return new Book(publisher);
    }
}

class MagazineStore extends BookStall {
    override sell(publisher: IndependentPublisher): Magazine {
        return new Magazine(publisher);
    }
}

class Customer {
    private book: Book;

    order(bookStall: BookStall): void {
        this.book = bookStall.sell(new IndependentPublisher());
    }
}
```

`Customer`가 `BookStall` 대신 `MagazineStore`와 협력하면, `sell` 메서드는 `Magazine` 인스턴스를 반환한다. 업캐스팅에 의해 `Magazine` 역시 `Book`이기 때문에 `Customer`의 입장에서는 둘 사이의 차이를 알지 못한다.

```
메서드 정의 계층       리턴 타입 계층
  BookStall              Book
      ▲                    ▲         ← 같은 방향!
      │                    │
  MagazineStore          Magazine
```

이처럼 부모 클래스에서 구현된 메서드를 자식 클래스에서 오버라이딩할 때 부모 클래스에서 선언한 반환 타입의 **서브타입**으로 지정할 수 있는 특성을 **리턴 타입 공변성**(*Return Type Covariance*)이라고 부른다. 메서드를 구현한 클래스의 타입 계층 방향과 리턴 타입의 타입 계층 방향이 **동일한 경우**를 가리킨다.

슈퍼타입 대신 서브타입을 반환하는 것은 더 강력한 사후조건을 정의하는 것과 같다. 따라서 리턴 타입 공변성은 계약에 의한 설계 관점에서 **계약을 위반하지 않는다**.

> 한 가지 기억해야 하는 사항은 공변성과 반공변성의 지원 여부는 **언어에 따라 다르다**는 것이다. Java는 리턴 타입 공변성을 지원하지만, C#은 리턴 타입 공변성을 지원하지 않는다(무공변적이다). TypeScript는 리턴 타입에 대해 공변적이다.

### 9.3 파라미터 타입 반공변성

`BookStall`의 자식 클래스인 `MagazineStore`에서 `sell` 메서드의 파라미터를 `IndependentPublisher`의 **슈퍼타입**인 `Publisher`로 변경할 수 있다면 어떨까?

```
메서드 정의 계층        파라미터 타입 계층
  BookStall           IndependentPublisher
      ▲                    │           ← 반대 방향!
      │                    ▼
  MagazineStore          Publisher
```

`Customer`의 `order` 메서드는 `BookStall`의 `sell` 메서드에 `IndependentPublisher` 인스턴스를 전달한다. `BookStall` 대신 `MagazineStore` 인스턴스와 협력한다면 `IndependentPublisher` 인스턴스가 `MagazineStore`의 `sell` 메서드의 파라미터로 전달될 것이다. 파라미터 타입이 슈퍼타입인 `Publisher` 타입으로 선언돼 있기 때문에 `IndependentPublisher` 인스턴스가 전달되더라도 문제가 없다.

이처럼 부모 클래스에서 구현된 메서드를 자식 클래스에서 오버라이딩할 때 파라미터 타입을 부모 클래스에서 사용한 파라미터의 **슈퍼타입**으로 지정할 수 있는 특성을 **파라미터 타입 반공변성**(*Parameter Type Contravariance*)이라고 부른다. 메서드를 정의한 클래스의 타입 계층과 파라미터의 타입 계층의 방향이 **반대인 경우** 서브타입 관계를 만족한다.

서브타입 대신 슈퍼타입을 파라미터로 받는 것은 더 약한 사전조건을 정의하는 것과 같다. 따라서 파라미터 타입 반공변성은 계약에 의한 설계 관점에서 **계약을 위반하지 않는다**.

> 현재 Java 언어에서는 파라미터 반공변성을 허용하지 않는다. `@Override` 어노테이션을 제거하면 Java 컴파일러는 오버라이딩이 아니라 이름만 같고 실제로는 서로 다른 메서드인 **오버로딩**으로 판단한다.

### 9.4 사전조건/사후조건과의 관계 정리

리턴 타입 공변성과 파라미터 타입 반공변성을 사전조건과 사후조건의 관점에서 정리할 수 있다:

| 항목 | 계약 규칙 | 가변성 규칙 |
|---|---|---|
| **사전조건 (파라미터)** | 서브타입은 사전조건을 완화할 수 있다 | 좀 더 완화된 슈퍼타입을 파라미터로 받을 수 있다 (반공변성) |
| **사후조건 (리턴 타입)** | 서브타입은 사후조건을 강화할 수 있다 | 좀 더 강화된 서브타입 인스턴스를 반환할 수 있다 (공변성) |

---

## 10. 함수 타입과 서브타이핑

최근의 객체지향 언어들은 이름 없는 메서드를 정의할 수 있게 허용한다. 이들은 익명 함수(*anonymous function*), 함수 리터럴(*function literal*), 람다 표현식(*lambda expression*) 등의 다양한 이름으로 불린다.

이름 없이 메서드를 정의하는 것을 허용하는 언어들은 객체의 타입뿐만 아니라 **메서드의 타입**을 정의할 수 있게 허용한다. 그리고 타입에서 정의한 시그니처를 준수하는 메서드들을 이 타입의 인스턴스로 간주한다.

```typescript
// TypeScript - 함수 타입 정의
type SellFunction = (publisher: IndependentPublisher) => Book;

class Customer {
    private book: Book | null = null;

    order(store: SellFunction): void {
        this.book = store(new IndependentPublisher());
    }
}

// BookStall의 sell 메서드를 함수 리터럴로 전달
new Customer().order((publisher: IndependentPublisher) => new Book(publisher));
```

메서드에 대한 타입을 정의할 수 있다면 함수 타입의 서브타입도 정의할 수 있을까? 그리고 서브타입 메서드가 슈퍼타입 메서드를 대체할 수 있을까? 대답은 **'그렇다'**이다.

파라미터 타입이 반공변성을 가지고 리턴 타입이 공변성을 가질 경우 메서드가 오버라이드 가능하다고 했던 것을 기억하라. 메서드가 오버라이드 가능하다는 것은 메서드가 대체 가능하며, 따라서 두 메서드 사이에 서브타이핑 관계가 존재한다는 것을 의미한다.

```typescript
// TypeScript - 파라미터 반공변 + 리턴 타입 공변 = 서브타입 함수
type SuperSell = (publisher: IndependentPublisher) => Book;

// Publisher(슈퍼타입)를 받고 Magazine(서브타입)을 반환
// → 파라미터 반공변, 리턴 타입 공변 → 서브타입 함수!
const subSell = (publisher: Publisher): Magazine => new Magazine(publisher);

new Customer().order(subSell); // 정상 동작
```

```
파라미터 타입       함수 타입                     리턴 타입
Independent      IndependentPublisher => Book       Book
  Publisher                ▲                          ▲
      │                   │ (서브타입)                 │
      ▼                   │                          │
  Publisher        Publisher => Magazine           Magazine
```

> 서브타입 관계를 구현하는 방식은 언어에 따라 다르다. 따라서 여러분이 사용하는 언어가 함수 타입에 관한 서브타입 관계를 준수하는지 확인하기 바란다. TypeScript는 `strictFunctionTypes` 옵션을 통해 함수 파라미터에 대한 반공변성 체크를 지원한다.

---

## 설계 원칙

| 원칙 | 설명 | 예제에서의 적용 |
|---|---|---|
| **사전조건** | 메서드 호출 전 클라이언트가 만족시켜야 하는 조건 | `customer != null`, `audienceCount >= 1` |
| **사후조건** | 메서드 실행 후 서버가 보장해야 하는 조건 | `result != null`, `result >= Money.ZERO` |
| **불변식** | 인스턴스 생명주기 전반에 걸쳐 유지돼야 하는 조건 | `movie != null`, `sequence >= 1`, `next != null` |
| **사전조건 완화 허용** | 서브타입은 슈퍼타입보다 더 약한 사전조건을 정의할 수 있다 | `null` 체크를 제거해도 기존 클라이언트에 영향 없음 |
| **사전조건 강화 금지** | 서브타입은 슈퍼타입보다 더 강력한 사전조건을 정의할 수 없다 | 빈 리스트 불허 조건 추가 시 LSP 위반 |
| **사후조건 강화 허용** | 서브타입은 슈퍼타입보다 더 강력한 사후조건을 정의할 수 있다 | 반환값 100원 이상 보장해도 기존 클라이언트에 영향 없음 |
| **사후조건 완화 금지** | 서브타입은 슈퍼타입보다 더 완화된 사후조건을 정의할 수 없다 | 마이너스 금액 허용 시 LSP 위반 |
| **불변식 유지** | 슈퍼타입의 불변식은 서브타입에서도 반드시 유지돼야 한다 | `protected` 필드를 통한 불변식 파괴 방지를 위해 `private` + `protected` 메서드 사용 |
| **일찍 실패하기** | 문제 발생 시 원인 지점에서 즉시 실패시키는 것이 뒤늦은 실패보다 낫다 | 사후조건 위반 즉시 예외 발생 |
| **리턴 타입 공변성** | 서브타입 메서드는 슈퍼타입 메서드의 리턴 타입의 서브타입을 반환할 수 있다 | `MagazineStore.sell`이 `Magazine` 반환 |
| **파라미터 반공변성** | 서브타입 메서드는 슈퍼타입 메서드의 파라미터 타입의 슈퍼타입을 파라미터로 받을 수 있다 | `MagazineStore.sell`이 `Publisher` 수용 |

---

## 요약

- **인터페이스의 한계**: 인터페이스만으로는 객체 사이의 협력에 필요한 약속과 제약, 부수 효과를 명확하게 전달하기 어렵다. 계약에 의한 설계는 이 한계를 극복한다.
- **계약에 의한 설계**: 버트란드 마이어가 Eiffel 언어와 함께 고안한 기법으로, 사전조건, 사후조건, 불변식이라는 세 가지 요소로 객체 사이의 협력을 명시적으로 문서화하고 검증한다.
- **사전조건은 클라이언트의 의무**: 메서드 호출 전에 클라이언트가 만족시켜야 하는 조건이다. 위반 시 클라이언트에 버그가 있다.
- **사후조건은 서버의 의무**: 메서드 실행 후에 서버가 보장해야 하는 조건이다. 위반 시 서버에 버그가 있다.
- **불변식은 클래스 전체의 규약**: 인스턴스 생명주기 전반에 걸쳐 항상 참이어야 하는 조건이다. `private` 가시성으로 캡슐화를 강화해야 보호할 수 있다.
- **리스코프 치환 원칙과의 관계**: 서브타입이 슈퍼타입을 대체할 수 있으려면 클라이언트와 슈퍼타입 간에 체결된 계약을 준수해야 한다.
- **계약 규칙**: 서브타입은 사전조건을 강화할 수 없고, 사후조건을 완화할 수 없으며, 슈퍼타입의 불변식을 유지해야 한다.
- **가변성 규칙**: 리턴 타입은 공변적이어야 하고, 파라미터 타입은 반공변적이어야 하며, 슈퍼타입이 발생시키는 예외와 다른 타입의 예외를 발생시켜서는 안 된다.
- **일찍 실패하기**: 사후조건 위반 시 원인 지점에서 즉시 실패시키는 것이 문제의 원인에서 멀리 떨어진 곳에서 뒤늦게 실패하는 것보다 훨씬 낫다.
- **함수 타입의 서브타이핑**: 파라미터 타입이 반공변적이고 리턴 타입이 공변적일 때 함수 타입 간의 서브타입 관계가 성립한다.
- **계약에 의한 설계는 설계 원칙이지 구현 메커니즘이 아니다**: 특정 라이브러리나 언어의 지원 여부와 상관없이 적용할 수 있는 보편적인 설계 방법이다.

---

## 다른 챕터와의 관계

- **Chapter 6 (메시지와 인터페이스)**: 이 장에서 설명한 명령-쿼리 분리 원칙과 의도를 드러내는 인터페이스 개념이 계약에 의한 설계의 출발점이다. 인터페이스만으로는 전달할 수 없는 제약 조건과 부수 효과를 계약이 보완한다.
- **Chapter 11 (합성과 유연한 설계)**: 핸드폰 과금 시스템의 합성 버전(RatePolicy 인터페이스와 BasicRatePolicy, AdditionalRatePolicy 계층)을 계약 규칙 설명의 예제로 활용한다. 합성 구조에서도 계약이 올바르게 유지돼야 서브타입 관계가 성립한다.
- **Chapter 13 (서브클래싱과 서브타이핑)**: 리스코프 치환 원칙의 정의와 서브타이핑 개념을 계약 규칙과 가변성 규칙으로 구체화한다. Bird-Penguin 예제에서 보여준 LSP 위반이 예외 규칙의 관점에서도 설명된다.
