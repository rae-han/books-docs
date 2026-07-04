# Chapter 10: Inheritance and Code Reuse (상속과 코드 재사용)

## 핵심 질문

객체지향에서 코드 재사용을 위해 상속을 사용하면 어떤 문제가 발생하는가? 중복 코드는 왜 위험하며, 취약한 기반 클래스 문제란 무엇인가? 상속의 피해를 최소화하면서도 코드를 재사용할 수 있는 올바른 방법은 무엇인가?

---

## 1. 상속과 중복 코드

객체지향 프로그래밍의 장점 중 하나는 코드를 재사용하기가 용이하다는 것이다. 전통적인 패러다임에서 코드를 재사용하는 방법은 코드를 복사한 후 수정하는 것이다. 객체지향에서는 조금 다른 방법을 취한다. 코드를 재사용하기 위해 '새로운' 코드를 추가한다. 객체지향에서 코드는 일반적으로 클래스 안에 작성되기 때문에, 클래스를 재사용하는 전통적인 방법은 새로운 클래스를 추가하는 것이다.

이번 장에서는 가장 대표적인 재사용 기법인 **상속**에 관해 살펴본다. 재사용 관점에서 상속이란 클래스 안에 정의된 인스턴스 변수와 메서드를 자동으로 새로운 클래스에 추가하는 구현 기법이다.

> 객체지향에서는 상속 외에도 코드를 효과적으로 재사용할 수 있는 방법이 한 가지 더 있다. 새로운 클래스의 인스턴스 안에 기존 클래스의 인스턴스를 포함시키는 방법으로, 흔히 합성이라고 부른다. 이어지는 11장에서 합성에 관해 자세히 살펴보고 상속과 합성의 장단점을 비교할 것이다.

코드를 재사용하려는 강력한 동기 이면에는 **중복된 코드를 제거하려는 욕망**이 숨어 있다. 따라서 상속에 대해 살펴보기 전에 중복 코드가 초래하는 문제점을 먼저 살펴보자.

### 1.1 DRY 원칙

중복 코드는 변경을 방해한다. 이것이 중복 코드를 제거해야 하는 가장 큰 이유다. 프로그램의 본질은 비즈니스와 관련된 지식을 코드로 변환하는 것이다. 안타깝게도 이 지식은 항상 변한다. 그에 맞춰 지식을 표현하는 코드 역시 변경해야 한다. 일단 새로운 코드를 추가하고 나면 언젠가는 변경될 것이라고 생각하는 것이 현명하다.

중복 코드가 가지는 가장 큰 문제는 코드를 수정하는 데 필요한 노력을 몇 배로 증가시킨다는 것이다:

1. 어떤 코드가 중복인지를 찾아야 한다
2. 찾아낸 모든 코드를 일관되게 수정해야 한다
3. 모든 중복 코드를 개별적으로 테스트해서 동일한 결과를 내놓는지 확인해야 한다

중복 여부를 판단하는 기준은 **변경**이다. 요구사항이 변경됐을 때 두 코드를 함께 수정해야 한다면 이 코드는 중복이다. 함께 수정할 필요가 없다면 중복이 아니다. 중복 코드를 결정하는 기준은 코드의 모양이 아니다. 모양이 유사하다는 것은 단지 중복의 징후일 뿐이다. 중복 여부를 결정하는 기준은 **코드가 변경에 반응하는 방식**이다.

> **핵심 통찰**: 신뢰할 수 있고 수정하기 쉬운 소프트웨어를 만드는 효과적인 방법 중 하나는 중복을 제거하는 것이다. 앤드류 헌트와 데이비드 토마스의 말을 인용하자면 프로그래머들은 DRY 원칙을 따라야 한다.

**DRY**(*Don't Repeat Yourself - 반복하지 마라*)는 간단히 말해 **동일한 지식을 중복하지 말라**는 것이다.

> "모든 지식은 시스템 내에서 단일하고, 애매하지 않고, 정말로 믿을 만한 표현 양식을 가져야 한다." [Hunt99]

DRY 원칙은 한 번, 단 한 번(*Once and Only Once*) 원칙[Beck96] 또는 단일 지점 제어(*Single-Point Control*) 원칙[Glass06b]이라고도 부른다. 원칙의 이름이 무엇이건 핵심은 코드 안에 중복이 존재해서는 안 된다는 것이다.

### 1.2 중복 코드 살펴보기: 전화 요금 계산 시스템

중복 코드의 문제점을 이해하기 위해 한 달에 한 번씩 가입자별로 전화 요금을 계산하는 간단한 애플리케이션을 개발해 보자. 전화 요금을 계산하는 규칙은 간단한데, 통화 시간을 단위 시간당 요금으로 나눠주면 된다. 10초당 5원의 통화료를 부과하는 요금제에 가입돼 있는 가입자가 100초 동안 통화를 했다면 요금으로 `100 / 10 * 5 = 50`원이 부과된다.

먼저 개별 통화 기간을 저장하는 `Call` 클래스가 필요하다. `Call`은 통화 시작 시간(`from`)과 통화 종료 시간(`to`)을 인스턴스 변수로 포함한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Call {
    private LocalDateTime from;
    private LocalDateTime to;

    public Call(LocalDateTime from, LocalDateTime to) {
        this.from = from;
        this.to = to;
    }

    public Duration getDuration() {
        return Duration.between(from, to);
    }

    public LocalDateTime getFrom() {
        return from;
    }
}
```

</details>

```typescript
// TypeScript
class Call {
    constructor(
        private readonly from: Date,
        private readonly to: Date,
    ) {}

    getDuration(): number {
        return (this.to.getTime() - this.from.getTime()) / 1000; // 초 단위
    }

    getFrom(): Date {
        return this.from;
    }
}
```

이제 통화 요금을 계산할 객체가 필요하다. 전체 통화 목록에 대해 알고 있는 정보 전문가에게 요금을 계산할 책임을 할당해야 한다. 일반적으로 통화 목록은 전화기 안에 보관된다. 따라서 `Call`의 목록을 관리할 정보 전문가는 `Phone`이다.

`Phone` 인스턴스는 요금 계산에 필요한 세 가지 인스턴스 변수를 포함한다:

| 인스턴스 변수 | 설명 | 예시 (10초당 5원) |
|---|---|---|
| `amount` | 단위 요금 | 5원 |
| `seconds` | 단위 시간 | 10초 |
| `calls` | 전체 통화 목록 | Call의 리스트 |

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Phone {
    private Money amount;
    private Duration seconds;
    private List<Call> calls = new ArrayList<>();

    public Phone(Money amount, Duration seconds) {
        this.amount = amount;
        this.seconds = seconds;
    }

    public void call(Call call) {
        calls.add(call);
    }

    public List<Call> getCalls() {
        return calls;
    }

    public Money getAmount() {
        return amount;
    }

    public Duration getSeconds() {
        return seconds;
    }

    public Money calculateFee() {
        Money result = Money.ZERO;
        for (Call call : calls) {
            result = result.plus(
                amount.times(call.getDuration().getSeconds() / seconds.getSeconds())
            );
        }
        return result;
    }
}
```

</details>

```typescript
// TypeScript
class Phone {
    private calls: Call[] = [];

    constructor(
        private readonly amount: number,
        private readonly seconds: number,
    ) {}

    call(call: Call): void {
        this.calls.push(call);
    }

    getCalls(): Call[] {
        return this.calls;
    }

    getAmount(): number {
        return this.amount;
    }

    getSeconds(): number {
        return this.seconds;
    }

    calculateFee(): number {
        let result = 0;
        for (const call of this.calls) {
            result += this.amount * (call.getDuration() / this.seconds);
        }
        return result;
    }
}
```

다음은 `Phone`을 이용해 '10초당 5원'씩 부과되는 요금제에 가입한 사용자가 각각 1분 동안 두 번 통화를 한 경우의 통화 요금을 계산하는 코드다.

```typescript
const phone = new Phone(5, 10); // 10초당 5원
phone.call(new Call(new Date(2018, 0, 1, 12, 10, 0), new Date(2018, 0, 1, 12, 11, 0)));
phone.call(new Call(new Date(2018, 0, 2, 12, 10, 0), new Date(2018, 0, 2, 12, 11, 0)));
phone.calculateFee(); //=> 60
```

### 1.3 심야 할인 요금제: 중복 코드의 탄생

여기부터가 재미있는 부분이다. 요구사항은 항상 변한다. 애플리케이션이 성공적으로 출시되고 시간이 흘러 '심야 할인 요금제'라는 새로운 요금 방식을 추가해야 한다는 요구사항이 접수됐다. 심야 할인 요금제는 밤 10시 이후의 통화에 대해 요금을 할인해주는 방식이다.

이 요구사항을 해결할 수 있는 쉽고도 가장 빠른 방법은 `Phone`의 코드를 복사해서 `NightlyDiscountPhone`이라는 새로운 클래스를 만든 후 수정하는 것이다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class NightlyDiscountPhone {
    private static final int LATE_NIGHT_HOUR = 22;
    private Money nightlyAmount;
    private Money regularAmount;
    private Duration seconds;
    private List<Call> calls = new ArrayList<>();

    public NightlyDiscountPhone(Money nightlyAmount, Money regularAmount, Duration seconds) {
        this.nightlyAmount = nightlyAmount;
        this.regularAmount = regularAmount;
        this.seconds = seconds;
    }

    public Money calculateFee() {
        Money result = Money.ZERO;
        for (Call call : calls) {
            if (call.getFrom().getHour() >= LATE_NIGHT_HOUR) {
                result = result.plus(
                    nightlyAmount.times(call.getDuration().getSeconds() / seconds.getSeconds()));
            } else {
                result = result.plus(
                    regularAmount.times(call.getDuration().getSeconds() / seconds.getSeconds()));
            }
        }
        return result;
    }
}
```

</details>

```typescript
// TypeScript
class NightlyDiscountPhone {
    private static readonly LATE_NIGHT_HOUR = 22;
    private calls: Call[] = [];

    constructor(
        private readonly nightlyAmount: number, // 심야 요금
        private readonly regularAmount: number,  // 일반 요금
        private readonly seconds: number,
    ) {}

    calculateFee(): number {
        let result = 0;
        for (const call of this.calls) {
            if (call.getFrom().getHours() >= NightlyDiscountPhone.LATE_NIGHT_HOUR) {
                result += this.nightlyAmount * (call.getDuration() / this.seconds);
            } else {
                result += this.regularAmount * (call.getDuration() / this.seconds);
            }
        }
        return result;
    }
}
```

`NightlyDiscountPhone`은 밤 10시를 기준으로 `regularAmount`와 `nightlyAmount` 중에서 기준 요금을 결정한다는 점을 제외하고는 `Phone`과 거의 유사하다. `Phone`의 코드를 복사해서 `NightlyDiscountPhone`을 추가하는 방법은 심야 할인 요구사항을 아주 짧은 시간 안에 구현할 수 있게 해준다.

하지만 구현 시간을 절약한 대가로 지불해야 하는 비용은 예상보다 크다. `Phone`과 `NightlyDiscountPhone` 사이에는 중복 코드가 존재하기 때문에 언제 터질지 모르는 시한폭탄을 안고 있는 것과 같다.

### 1.4 중복 코드 수정의 위험성

중복 코드가 코드 수정에 미치는 영향을 살펴보기 위해 새로운 요구사항을 추가해 보자. 통화 요금에 부과할 세금을 계산하는 기능이다. 부과되는 세율은 가입자의 핸드폰마다 다르다고 가정한다.

현재 통화 요금을 계산하는 로직은 `Phone`과 `NightlyDiscountPhone` 양쪽 모두에 구현돼 있기 때문에 세금을 추가하기 위해서는 **두 클래스를 함께 수정**해야 한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java - Phone에 세금 추가
public class Phone {
    // ...
    private double taxRate;

    public Phone(Money amount, Duration seconds, double taxRate) {
        // ...
        this.taxRate = taxRate;
    }

    public Money calculateFee() {
        Money result = Money.ZERO;
        for (Call call : calls) {
            result = result.plus(
                amount.times(call.getDuration().getSeconds() / seconds.getSeconds()));
        }
        return result.plus(result.times(taxRate));
    }
}

// Java - NightlyDiscountPhone에 세금 추가
public class NightlyDiscountPhone {
    // ...
    private double taxRate;

    public NightlyDiscountPhone(Money nightlyAmount, Money regularAmount,
                                 Duration seconds, double taxRate) {
        // ...
        this.taxRate = taxRate;
    }

    public Money calculateFee() {
        Money result = Money.ZERO;
        for (Call call : calls) {
            if (call.getFrom().getHour() >= LATE_NIGHT_HOUR) {
                result = result.plus(
                    nightlyAmount.times(call.getDuration().getSeconds() / seconds.getSeconds()));
            } else {
                result = result.plus(
                    regularAmount.times(call.getDuration().getSeconds() / seconds.getSeconds()));
            }
        }
        return result.minus(result.times(taxRate)); // 버그! plus여야 하는데 minus를 사용
    }
}
```

</details>

```typescript
// TypeScript - Phone에 세금 추가
class Phone {
    private calls: Call[] = [];

    constructor(
        private readonly amount: number,
        private readonly seconds: number,
        private readonly taxRate: number,
    ) {}

    calculateFee(): number {
        let result = 0;
        for (const call of this.calls) {
            result += this.amount * (call.getDuration() / this.seconds);
        }
        return result + result * this.taxRate; // 세금 부과
    }
}

// TypeScript - NightlyDiscountPhone에 세금 추가
class NightlyDiscountPhone {
    // ...
    constructor(
        private readonly nightlyAmount: number,
        private readonly regularAmount: number,
        private readonly seconds: number,
        private readonly taxRate: number,
    ) {}

    calculateFee(): number {
        let result = 0;
        for (const call of this.calls) {
            // ... 요금 계산 로직 ...
        }
        return result - result * this.taxRate; // 버그! +여야 하는데 -를 사용
    }
}
```

이 예제는 중복 코드가 가지는 단점을 잘 보여준다. `Phone`의 `calculateFee` 메서드에서는 반환 시에 `result`에 세금을 **더했**지만, `NightlyDiscountPhone`의 `calculateFee` 메서드에서는 세금을 **뺐다**. 두 코드를 동일하게 수정해야 하는데 서로 다르게 수정하기가 너무 쉬운 것이다.

> **핵심 통찰**: 중복 코드는 새로운 중복 코드를 부른다. 중복 코드를 제거하지 않은 상태에서 코드를 수정할 수 있는 유일한 방법은 새로운 중복 코드를 추가하는 것뿐이다. 새로운 중복 코드를 추가하는 과정에서 코드의 일관성이 무너질 위험이 항상 도사리고 있다.

### 1.5 타입 코드로 합치기: 또 다른 나쁜 선택

두 클래스 사이의 중복 코드를 제거하는 한 가지 방법은 클래스를 하나로 합치는 것이다. 요금제를 구분하는 타입 코드를 추가하고 타입 코드의 값에 따라 로직을 분기시켜 `Phone`과 `NightlyDiscountPhone`을 하나로 합칠 수 있다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Phone {
    private static final int LATE_NIGHT_HOUR = 22;
    enum PhoneType { REGULAR, NIGHTLY }

    private PhoneType type;
    private Money amount;
    private Money regularAmount;
    private Money nightlyAmount;
    private Duration seconds;
    private List<Call> calls = new ArrayList<>();

    public Phone(Money amount, Duration seconds) {
        this(PhoneType.REGULAR, amount, Money.ZERO, Money.ZERO, seconds);
    }

    public Phone(Money nightlyAmount, Money regularAmount, Duration seconds) {
        this(PhoneType.NIGHTLY, Money.ZERO, nightlyAmount, regularAmount, seconds);
    }

    public Phone(PhoneType type, Money amount, Money nightlyAmount,
                 Money regularAmount, Duration seconds) {
        this.type = type;
        this.amount = amount;
        this.regularAmount = regularAmount;
        this.nightlyAmount = nightlyAmount;
        this.seconds = seconds;
    }

    public Money calculateFee() {
        Money result = Money.ZERO;
        for (Call call : calls) {
            if (type == PhoneType.REGULAR) {
                result = result.plus(
                    amount.times(call.getDuration().getSeconds() / seconds.getSeconds()));
            } else {
                if (call.getFrom().getHour() >= LATE_NIGHT_HOUR) {
                    result = result.plus(
                        nightlyAmount.times(call.getDuration().getSeconds() / seconds.getSeconds()));
                } else {
                    result = result.plus(
                        regularAmount.times(call.getDuration().getSeconds() / seconds.getSeconds()));
                }
            }
        }
        return result;
    }
}
```

</details>

```typescript
// TypeScript
type PhoneType = "REGULAR" | "NIGHTLY";

class Phone {
    private static readonly LATE_NIGHT_HOUR = 22;
    private type: PhoneType;
    private amount: number;
    private regularAmount: number;
    private nightlyAmount: number;
    private seconds: number;
    private calls: Call[] = [];

    constructor(amount: number, seconds: number);
    constructor(nightlyAmount: number, regularAmount: number, seconds: number);
    constructor(...args: number[]) {
        if (args.length === 2) {
            this.type = "REGULAR";
            this.amount = args[0];
            this.seconds = args[1];
            this.regularAmount = 0;
            this.nightlyAmount = 0;
        } else {
            this.type = "NIGHTLY";
            this.amount = 0;
            this.nightlyAmount = args[0];
            this.regularAmount = args[1];
            this.seconds = args[2];
        }
    }

    calculateFee(): number {
        let result = 0;
        for (const call of this.calls) {
            if (this.type === "REGULAR") {
                result += this.amount * (call.getDuration() / this.seconds);
            } else {
                if (call.getFrom().getHours() >= Phone.LATE_NIGHT_HOUR) {
                    result += this.nightlyAmount * (call.getDuration() / this.seconds);
                } else {
                    result += this.regularAmount * (call.getDuration() / this.seconds);
                }
            }
        }
        return result;
    }
}
```

하지만 타입 코드를 사용하는 클래스는 **낮은 응집도**와 **높은 결합도**라는 문제에 시달리게 된다. 객체지향 프로그래밍 언어는 타입 코드를 사용하지 않고도 중복 코드를 관리할 수 있는 효과적인 방법을 제공한다. **상속**이 바로 그것이다.

### 1.6 상속을 이용해서 중복 코드 제거하기

상속의 기본 아이디어는 매우 간단하다. 이미 존재하는 클래스와 유사한 클래스가 필요하다면 코드를 복사하지 말고 상속을 이용해 코드를 재사용하라는 것이다.

`NightlyDiscountPhone` 클래스가 `Phone` 클래스를 상속받게 만들면 코드를 중복시키지 않고도 `Phone` 클래스의 코드 대부분을 재사용할 수 있다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class NightlyDiscountPhone extends Phone {
    private static final int LATE_NIGHT_HOUR = 22;
    private Money nightlyAmount;

    public NightlyDiscountPhone(Money nightlyAmount, Money regularAmount, Duration seconds) {
        super(regularAmount, seconds);
        this.nightlyAmount = nightlyAmount;
    }

    @Override
    public Money calculateFee() {
        // 부모 클래스의 calculateFee 호출
        Money result = super.calculateFee();

        Money nightlyFee = Money.ZERO;
        for (Call call : getCalls()) {
            if (call.getFrom().getHour() >= LATE_NIGHT_HOUR) {
                nightlyFee = nightlyFee.plus(
                    getAmount().minus(nightlyAmount).times(
                        call.getDuration().getSeconds() / getSeconds().getSeconds()));
            }
        }
        return result.minus(nightlyFee);
    }
}
```

</details>

```typescript
// TypeScript
class NightlyDiscountPhone extends Phone {
    private static readonly LATE_NIGHT_HOUR = 22;

    constructor(
        private readonly nightlyAmount: number,
        regularAmount: number,
        seconds: number,
    ) {
        super(regularAmount, seconds);
    }

    override calculateFee(): number {
        // 부모 클래스의 calculateFee 호출 — 모든 통화를 일반 요금으로 계산
        const result = super.calculateFee();

        let nightlyFee = 0;
        for (const call of this.getCalls()) {
            if (call.getFrom().getHours() >= NightlyDiscountPhone.LATE_NIGHT_HOUR) {
                // 일반 요금과 심야 요금의 차액을 계산
                nightlyFee += (this.getAmount() - this.nightlyAmount)
                    * (call.getDuration() / this.getSeconds());
            }
        }
        return result - nightlyFee; // 전체 요금에서 차액을 빼서 최종 요금 산출
    }
}
```

이 `calculateFee` 메서드의 로직은 직관에 어긋난다. `super` 참조를 통해 부모 클래스인 `Phone`의 `calculateFee` 메서드를 호출해서 일반 요금제에 따라 통화 요금을 계산한 후, 이 값에서 통화 시작 시간이 10시 이후인 통화의 요금 차액을 빼주는 것이다.

이 로직을 이해하기 위해서는 개발자가 `Phone`의 코드를 재사용하기 위해 세운 **가정**을 이해하는 것이 중요하다. 심야 할인 요금제의 규칙이 다음과 같다고 해보자:

- 밤 10시 이전: 10초당 5원 (`regularAmount = 5원`, `seconds = 10초`)
- 밤 10시 이후: 10초당 2원 (`nightlyAmount = 2원`, `seconds = 10초`)

어떤 가입자가 두 번 통화했고 각 통화 시간은 40초와 50초라고 가정하자. 처음 40초 동안은 10시 이전에, 나머지 50초 동안은 10시 이후에 이뤄졌다면 통화 요금은 다음과 같다:

```
직관적인 계산 방식:
  (40초 / 10초 × 5원) + (50초 / 10초 × 2원) = 20 + 10 = 30원

코드의 계산 방식:
  전체를 일반 요금으로 계산:     (40초 / 10초 × 5원) + (50초 / 10초 × 5원) = 45원
  10시 이후 통화의 차액 계산:    50초 / 10초 × (5원 - 2원) = 15원
  최종 요금:                   45원 - 15원 = 30원
```

우리가 기대한 것은 10시 이전의 요금과 10시 이후의 요금을 **더하는** 것이다. 하지만 코드는 전체를 일반 요금으로 계산한 후 차액을 **빼는** 방식으로 구현되어 있다. 요구사항과 구현 사이의 차이가 크면 클수록 코드를 이해하기 어려워진다. 잘못 사용된 상속은 이 차이를 더 크게 벌린다.

> 이 예제가 비현실적이라고 생각되는가? 그렇다. 비현실적이다. 이 코드가 비현실적인 이유는 지나치게 깔끔하고 그나마 이해하기 쉽기 때문이다. 실제 프로젝트에서 마주치게 될 코드는 여기서 설명한 예보다 훨씬 더 엉망일 확률이 높다.

이 예를 통해 알 수 있는 것처럼 **상속을 염두에 두고 설계되지 않은 클래스를 상속을 이용해 재사용하는 것은 생각처럼 쉽지 않다**. 상속을 이용해 코드를 재사용하기 위해서는 부모 클래스의 개발자가 세웠던 가정이나 추론 과정을 정확하게 이해해야 한다. 이것은 자식 클래스의 작성자가 부모 클래스의 구현 방법에 대한 정확한 지식을 가져야 한다는 것을 의미한다. 따라서 **상속은 결합도를 높인다**.

### 1.7 강하게 결합된 Phone과 NightlyDiscountPhone

부모 클래스와 자식 클래스 사이의 결합이 문제인 이유를 살펴보자. 앞서 설명했던 세금을 부과하는 요구사항이 추가된다면 어떻게 될까?

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Phone {
    private double taxRate;

    public Phone(Money amount, Duration seconds, double taxRate) {
        // ...
        this.taxRate = taxRate;
    }

    public Money calculateFee() {
        // ...
        return result.plus(result.times(taxRate));
    }

    public double getTaxRate() {
        return taxRate;
    }
}

public class NightlyDiscountPhone extends Phone {
    public NightlyDiscountPhone(Money nightlyAmount, Money regularAmount,
                                 Duration seconds, double taxRate) {
        super(regularAmount, seconds, taxRate);
        // ...
    }

    @Override
    public Money calculateFee() {
        // ...
        return result.minus(nightlyFee.plus(nightlyFee.times(getTaxRate())));
    }
}
```

</details>

```typescript
// TypeScript
class Phone {
    private calls: Call[] = [];

    constructor(
        private readonly amount: number,
        private readonly seconds: number,
        private readonly taxRate: number,
    ) {}

    calculateFee(): number {
        let result = 0;
        for (const call of this.calls) {
            result += this.amount * (call.getDuration() / this.seconds);
        }
        return result + result * this.taxRate; // 세금 부과
    }
}

class NightlyDiscountPhone extends Phone {
    constructor(
        private readonly nightlyAmount: number,
        regularAmount: number,
        seconds: number,
        taxRate: number,
    ) {
        super(regularAmount, seconds, taxRate);
    }

    override calculateFee(): number {
        const result = super.calculateFee();
        // ... nightlyFee 계산 ...
        // 차감액에도 세금을 적용해야 하므로 부모의 taxRate를 알아야 한다
        return result - (nightlyFee + nightlyFee * this.getTaxRate());
    }
}
```

코드 중복을 제거하기 위해 상속을 사용했음에도 세금을 계산하는 로직을 추가하기 위해 **새로운 중복 코드를 만들어야 하는** 것이다. `NightlyDiscountPhone`이 `Phone`의 구현에 너무 강하게 결합돼 있기 때문에 발생하는 문제다.

> **상속을 위한 경고 1**: 자식 클래스의 메서드 안에서 `super` 참조를 이용해 부모 클래스의 메서드를 직접 호출할 경우 두 클래스는 강하게 결합된다. `super` 호출을 제거할 수 있는 방법을 찾아 결합도를 제거하라.

상속 관계로 연결된 자식 클래스가 부모 클래스의 변경에 취약해지는 현상을 가리켜 **취약한 기반 클래스 문제**(*Fragile Base Class Problem*)라고 부른다.

---

## 2. 취약한 기반 클래스 문제

상속은 자식 클래스와 부모 클래스의 결합도를 높인다. 이 강한 결합도로 인해 자식 클래스는 부모 클래스의 불필요한 세부사항에 엮이게 된다. 부모 클래스의 작은 변경에도 자식 클래스는 컴파일 오류와 실행 에러라는 고통에 시달려야 할 수도 있다.

부모 클래스의 변경에 의해 자식 클래스가 영향을 받는 현상을 **취약한 기반 클래스 문제**(*Fragile Base Class Problem, Brittle Base Class Problem*)[Holub04]라고 부른다. 이 문제는 상속을 사용한다면 피할 수 없는 객체지향 프로그래밍의 근본적인 취약성이다.

> "겉으로 보기에는 안전한 방식으로 기반 클래스를 수정한 것처럼 보이더라도 이 새로운 행동이 파생 클래스에게 상속될 경우 파생 클래스의 잘못된 동작을 초래할 수 있기 때문에 기반 클래스는 '취약하다'. 단순히 기반 클래스의 메서드들만을 조사하는 것만으로는 기반 클래스를 변경하는 것이 안전하다고 확신할 수 없다. 모든 파생 클래스들을 살펴봐야(그리고 테스트까지 해야) 한다." [Holub04]

취약한 기반 클래스 문제는 **캡슐화를 약화**시키고 **결합도를 높인다**. 상속은 자식 클래스가 부모 클래스의 구현 세부사항에 의존하도록 만들기 때문에 캡슐화를 약화시킨다[Snyder86]. 이것이 상속이 위험한 이유인 동시에 우리가 상속을 피해야 하는 첫 번째 이유다.

객체를 사용하는 이유는 구현과 관련된 세부사항을 퍼블릭 인터페이스 뒤로 캡슐화할 수 있기 때문이다. 캡슐화는 변경에 의한 파급효과를 제어할 수 있기 때문에 가치가 있다. 안타깝게도 상속을 사용하면 부모 클래스의 퍼블릭 인터페이스가 아닌 **구현을 변경하더라도** 자식 클래스가 영향을 받기 쉬워진다.

> **핵심 통찰**: 객체지향의 기반은 캡슐화를 통한 변경의 통제다. 상속은 코드의 재사용을 위해 캡슐화의 장점을 희석시키고 구현에 대한 결합도를 높임으로써 객체지향이 가진 강력함을 반감시킨다.

### 2.1 불필요한 인터페이스 상속 문제

자바의 초기 버전에서 상속을 잘못 사용한 대표적인 사례는 `java.util.Properties`와 `java.util.Stack`이다. 두 클래스의 공통점은 부모 클래스에서 상속받은 메서드를 사용할 경우 자식 클래스의 규칙이 위반될 수 있다는 것이다.

**Stack과 Vector**

`Stack`은 가장 나중에 추가된 요소가 가장 먼저 추출되는 LIFO(*Last In First Out*) 자료 구조를 구현한 클래스다. `Vector`는 임의의 위치에서 요소를 추출하고 삽입할 수 있는 리스트 자료 구조의 구현체다. 자바의 초기 컬렉션 프레임워크 개발자들은 요소의 추가, 삭제 오퍼레이션을 제공하는 `Vector`를 재사용하기 위해 `Stack`을 `Vector`의 자식 클래스로 구현했다.

```
┌──────────────────────────┐
│         Vector           │
├──────────────────────────┤
│ get(index)               │
│ add(index, element)      │
│ remove(index)            │
└────────────▲─────────────┘
             │ extends
┌────────────┴─────────────┐
│         Stack            │
├──────────────────────────┤
│ push(item)               │
│ pop()                    │
└──────────────────────────┘
```

안타깝게도 `Stack`이 `Vector`를 상속받기 때문에 `Stack`의 퍼블릭 인터페이스에 `Vector`의 퍼블릭 인터페이스가 합쳐진다. `Stack`에게 상속된 `Vector`의 퍼블릭 인터페이스를 이용하면 임의의 위치에서 요소를 추가하거나 삭제할 수 있다. LIFO를 보장해야 하는 `Stack`의 규칙을 쉽게 위반할 수 있다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
Stack<String> stack = new Stack<>();
stack.push("1st");
stack.push("2nd");
stack.push("3rd");

stack.add(0, "4th"); // Vector의 메서드로 스택 맨 앞에 삽입

assertEquals("4th", stack.pop()); // 에러! 실제 반환값은 "3rd"
```

</details>

```typescript
// TypeScript — Stack이 Array를 상속받았다고 가정
class Stack<T> extends Array<T> {
    push(...items: T[]): number { return super.push(...items); }
    pop(): T | undefined { return super.pop(); }
}

const stack = new Stack<string>();
stack.push("1st");
stack.push("2nd");
stack.push("3rd");

stack.splice(0, 0, "4th"); // Array의 메서드로 스택 맨 앞에 삽입

stack.pop(); // "3rd" — "4th"가 아니다!
```

문제의 원인은 `Stack`이 규칙을 무너뜨릴 여지가 있는 위험한 `Vector`의 퍼블릭 인터페이스까지도 함께 상속받았기 때문이다.

> "인터페이스 설계는 제대로 쓰기엔 쉽게, 엉터리로 쓰기엔 어렵게 만들어야 한다." [Meyers05]

**Properties와 Hashtable**

`Properties` 클래스는 키와 값의 쌍을 보관한다는 점에서는 `Map`과 유사하지만, 다양한 타입을 저장할 수 있는 `Map`과 달리 키와 값의 타입으로 오직 `String`만 가질 수 있다. 이 클래스는 `Map`의 조상인 `Hashtable`을 상속받는데, 자바에 제네릭이 도입되기 이전에 만들어졌기 때문에 컴파일러가 키와 값의 타입이 `String`인지 여부를 체크할 수 있는 방법이 없었다.

```
┌──────────────────────────────────────────┐
│              Hashtable                   │
├──────────────────────────────────────────┤
│ get(key: Object): Object                │
│ put(key: Object, value: Object)         │
└────────────────────▲─────────────────────┘
                     │ extends
┌────────────────────┴─────────────────────┐
│              Properties                  │
├──────────────────────────────────────────┤
│ getProperty(key: String): String         │
│ setProperty(key: String, value: String)  │
└──────────────────────────────────────────┘
```

<details>
<summary>원문 Java 코드</summary>

```java
// Java
Properties properties = new Properties();
properties.setProperty("Bjarne Stroustrup", "C++");
properties.setProperty("James Gosling", "Java");

properties.put("Dennis Ritchie", 67); // Hashtable의 메서드로 int 값 저장 성공

assertEquals("C", properties.getProperty("Dennis Ritchie")); // 에러! null 반환
```

</details>

분명히 "Dennis Ritchie"라는 키의 값으로 67을 넣는 데 성공했는데도 `getProperty` 메서드는 `null`을 반환한다. 반환할 값의 타입이 `String`이 아닐 경우 `null`을 반환하도록 구현돼 있기 때문이다.

`Stack`과 `Properties`의 예는 퍼블릭 인터페이스에 대한 고려 없이 단순히 코드 재사용을 위해 상속을 이용하는 것이 얼마나 위험한지를 잘 보여준다.

> **상속을 위한 경고 2**: 상속받은 부모 클래스의 메서드가 자식 클래스의 내부 구조에 대한 규칙을 깨트릴 수 있다.

### 2.2 메서드 오버라이딩의 오작용 문제

조슈아 블로치(Joshua Bloch)는 《이펙티브 자바》[Bloch08]에서 `HashSet`의 구현에 강하게 결합된 `InstrumentedHashSet` 클래스를 소개한다. `InstrumentedHashSet`은 `HashSet`의 내부에 저장된 요소의 수를 셀 수 있는 기능을 추가한 클래스다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class InstrumentedHashSet<E> extends HashSet<E> {
    private int addCount = 0;

    @Override
    public boolean add(E e) {
        addCount++;
        return super.add(e);
    }

    @Override
    public boolean addAll(Collection<? extends E> c) {
        addCount += c.size();
        return super.addAll(c);
    }
}
```

</details>

```typescript
// TypeScript
class InstrumentedSet<T> extends Set<T> {
    private addCount = 0;

    override add(value: T): this {
        this.addCount++;
        return super.add(value);
    }

    addAll(values: T[]): void {
        this.addCount += values.length;
        for (const value of values) {
            super.add(value); // 주의: 여기서 super.add를 호출
        }
    }
}
```

`InstrumentedHashSet`의 구현에는 아무런 문제가 없어 보인다. 적어도 다음과 같은 코드를 실행하기 전까지는:

```java
InstrumentedHashSet<String> languages = new InstrumentedHashSet<>();
languages.addAll(Arrays.asList("Java", "Ruby", "Scala"));
```

대부분의 사람들은 위 코드를 실행한 후에 `addCount`의 값이 3이 될 거라고 예상할 것이다. 하지만 실제로 실행한 후의 `addCount` 값은 **6**이다. 그 이유는 부모 클래스인 `HashSet`의 `addAll` 메서드 안에서 `add` 메서드를 호출하기 때문이다.

```
호출 흐름:
1. InstrumentedHashSet.addAll() 호출 → addCount += 3 (addCount = 3)
2. super.addAll() → HashSet.addAll() 호출
3. HashSet.addAll() 내부에서 각 요소에 대해 add() 호출
4. 다형성에 의해 InstrumentedHashSet.add()가 3번 호출 → addCount += 3 (addCount = 6)
```

이 문제를 해결하는 방법들과 그 한계:

| 해결 방법 | 설명 | 문제점 |
|---|---|---|
| `addAll` 오버라이딩 제거 | `HashSet.addAll`이 내부적으로 `add`를 호출하는 것에 의존 | 미래에 `addAll`이 `add`를 호출하지 않도록 변경되면 카운트 누락 |
| `addAll`에서 직접 반복하며 `add` 호출 | 미래 변경에 안전 | 부모 클래스의 코드를 중복. 소스 코드 접근 권한이 없거나 `private` 멤버 사용 시 불가능 |

> **상속을 위한 경고 3**: 자식 클래스가 부모 클래스의 메서드를 오버라이딩할 경우 부모 클래스가 자신의 메서드를 사용하는 방법에 자식 클래스가 결합될 수 있다.

조슈아 블로치는 클래스가 상속되기를 원한다면 **상속을 위해 클래스를 설계하고 문서화해야 하며**, 그렇지 않은 경우에는 **상속을 금지시켜야 한다**고 주장한다.

> "오버라이딩 가능한 메서드들의 자체 사용(self-use), 즉 그 메서드들이 같은 클래스의 다른 메서드를 호출하는지에 대해 반드시 문서화해야 한다. 잘 된 API 문서는 메서드가 무슨 일(what)을 하는지를 기술해야 하고, 어떻게 하는지(how)를 설명해서는 안 된다는 통념을 어기는 것은 아닐까? 그렇다, 어기는 것이다! 이것은 결국 상속이 캡슐화를 위반함으로써 초래된 불행인 것이다." [Bloch08]

설계는 트레이드오프 활동이다. **상속은 코드 재사용을 위해 캡슐화를 희생한다**. 완벽한 캡슐화를 원한다면 코드 재사용을 포기하거나 상속 이외의 다른 방법을 사용해야 한다.

### 2.3 부모 클래스와 자식 클래스의 동시 수정 문제

음악 목록을 추가할 수 있는 플레이리스트를 구현한다고 가정하자.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Song {
    private String singer;
    private String title;

    public Song(String singer, String title) {
        this.singer = singer;
        this.title = title;
    }

    public String getSinger() { return singer; }
    public String getTitle() { return title; }
}

public class Playlist {
    private List<Song> tracks = new ArrayList<>();

    public void append(Song song) {
        getTracks().add(song);
    }

    public List<Song> getTracks() {
        return tracks;
    }
}

public class PersonalPlaylist extends Playlist {
    public void remove(Song song) {
        getTracks().remove(song);
    }
}
```

</details>

```typescript
// TypeScript
class Song {
    constructor(
        private readonly singer: string,
        private readonly title: string,
    ) {}

    getSinger(): string { return this.singer; }
    getTitle(): string { return this.title; }
}

class Playlist {
    private tracks: Song[] = [];

    append(song: Song): void {
        this.tracks.push(song);
    }

    getTracks(): Song[] {
        return this.tracks;
    }
}

class PersonalPlaylist extends Playlist {
    remove(song: Song): void {
        const index = this.getTracks().indexOf(song);
        if (index !== -1) this.getTracks().splice(index, 1);
    }
}
```

요구사항이 변경돼서 `Playlist`에서 노래의 목록뿐만 아니라 **가수별 노래의 제목**도 함께 관리해야 한다고 가정하자.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Playlist {
    private List<Song> tracks = new ArrayList<>();
    private Map<String, String> singers = new HashMap<>(); // 추가

    public void append(Song song) {
        tracks.add(song);
        singers.put(song.getSinger(), song.getTitle()); // 추가
    }

    public List<Song> getTracks() { return tracks; }
    public Map<String, String> getSingers() { return singers; } // 추가
}

// PersonalPlaylist도 함께 수정해야 한다!
public class PersonalPlaylist extends Playlist {
    public void remove(Song song) {
        getTracks().remove(song);
        getSingers().remove(song.getSinger()); // 추가하지 않으면 버그!
    }
}
```

</details>

```typescript
// TypeScript
class Playlist {
    private tracks: Song[] = [];
    private singers = new Map<string, string>(); // 추가

    append(song: Song): void {
        this.tracks.push(song);
        this.singers.set(song.getSinger(), song.getTitle()); // 추가
    }

    getTracks(): Song[] { return this.tracks; }
    getSingers(): Map<string, string> { return this.singers; } // 추가
}

// PersonalPlaylist도 함께 수정해야 한다!
class PersonalPlaylist extends Playlist {
    remove(song: Song): void {
        const index = this.getTracks().indexOf(song);
        if (index !== -1) this.getTracks().splice(index, 1);
        this.getSingers().delete(song.getSinger()); // 추가하지 않으면 버그!
    }
}
```

이 예는 자식 클래스가 부모 클래스의 메서드를 오버라이딩하거나 불필요한 인터페이스를 상속받지 않았음에도, 부모 클래스를 수정할 때 자식 클래스를 함께 수정해야 할 수 있다는 사실을 잘 보여준다.

> "서브클래스는 올바른 기능을 위해 슈퍼클래스의 세부적인 구현에 의존한다. 슈퍼클래스의 구현은 릴리스를 거치면서 변경될 수 있고, 그에 따라 슈퍼클래스의 작성자가 확장될 목적으로 특별히 그 클래스를 설계하지 않았다면 서브클래스는 슈퍼클래스와 보조를 맞춰서 진화해야 한다." [Bloch08]

> **상속을 위한 경고 4**: 클래스를 상속하면 결합도로 인해 자식 클래스와 부모 클래스의 구현을 영원히 변경하지 않거나, 자식 클래스와 부모 클래스를 동시에 변경하거나 둘 중 하나를 선택할 수밖에 없다.

---

## 3. Phone 다시 살펴보기: 추상화로 문제 해결

지금까지 상속으로 인해 발생하는 취약한 기반 클래스 문제의 다양한 예를 살펴봤다. 이제 다시 `Phone`과 `NightlyDiscountPhone`의 문제로 돌아와 상속으로 인한 피해를 최소화할 수 있는 방법을 찾아보자. 취약한 기반 클래스 문제를 완전히 없앨 수는 없지만 어느 정도까지 위험을 완화시키는 것은 가능하다. 문제 해결의 열쇠는 바로 **추상화**다.

### 3.1 추상화에 의존하자

`NightlyDiscountPhone`의 가장 큰 문제점은 `Phone`에 강하게 결합돼 있기 때문에 `Phone`이 변경될 경우 함께 변경될 가능성이 높다는 것이다. 이 문제를 해결하는 가장 일반적인 방법은 자식 클래스가 부모 클래스의 **구현이 아닌 추상화에 의존**하도록 만드는 것이다.

코드 중복을 제거하기 위해 상속을 도입할 때 따르는 두 가지 원칙이 있다:

1. **두 메서드가 유사하게 보인다면 차이점을 메서드로 추출하라.** 메서드 추출을 통해 두 메서드를 동일한 형태로 보이도록 만들 수 있다[Feathers04].
2. **부모 클래스의 코드를 하위로 내리지 말고 자식 클래스의 코드를 상위로 올려라.** 부모 클래스의 구체적인 메서드를 자식 클래스로 내리는 것보다 자식 클래스의 추상적인 메서드를 부모 클래스로 올리는 것이 재사용성과 응집도 측면에서 더 뛰어난 결과를 얻을 수 있다[Metz12].

### 3.2 1단계: 차이를 메서드로 추출하라

가장 먼저 할 일은 중복 코드 안에서 **차이점을 별도의 메서드로 추출**하는 것이다. 이것은 "변하는 것으로부터 변하지 않는 것을 분리하라" 또는 "변하는 부분을 찾고 이를 캡슐화하라"라는 조언을 메서드 수준에서 적용한 것이다.

`Phone`과 `NightlyDiscountPhone`의 `calculateFee` 메서드에서 for 문 안에 구현된 요금 계산 로직이 서로 다르다. 이 부분을 동일한 이름을 가진 메서드 `calculateCallFee`로 추출하자.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
// Phone에서 메서드 추출
public class Phone {
    public Money calculateFee() {
        Money result = Money.ZERO;
        for (Call call : calls) {
            result = result.plus(calculateCallFee(call));
        }
        return result;
    }

    private Money calculateCallFee(Call call) {
        return amount.times(call.getDuration().getSeconds() / seconds.getSeconds());
    }
}

// NightlyDiscountPhone에서도 동일한 방식으로 메서드 추출
public class NightlyDiscountPhone {
    public Money calculateFee() {
        Money result = Money.ZERO;
        for (Call call : calls) {
            result = result.plus(calculateCallFee(call));
        }
        return result;
    }

    private Money calculateCallFee(Call call) {
        if (call.getFrom().getHour() >= LATE_NIGHT_HOUR) {
            return nightlyAmount.times(call.getDuration().getSeconds() / seconds.getSeconds());
        }
        return regularAmount.times(call.getDuration().getSeconds() / seconds.getSeconds());
    }
}
```

</details>

```typescript
// TypeScript
// Phone에서 메서드 추출
class Phone {
    calculateFee(): number {
        let result = 0;
        for (const call of this.calls) {
            result += this.calculateCallFee(call);  // 추출된 메서드 호출
        }
        return result;
    }

    private calculateCallFee(call: Call): number {
        return this.amount * (call.getDuration() / this.seconds);
    }
}

// NightlyDiscountPhone에서도 동일한 방식으로 메서드 추출
class NightlyDiscountPhone {
    calculateFee(): number {
        let result = 0;
        for (const call of this.calls) {
            result += this.calculateCallFee(call);  // 동일한 구조!
        }
        return result;
    }

    private calculateCallFee(call: Call): number {
        if (call.getFrom().getHours() >= NightlyDiscountPhone.LATE_NIGHT_HOUR) {
            return this.nightlyAmount * (call.getDuration() / this.seconds);
        }
        return this.regularAmount * (call.getDuration() / this.seconds);
    }
}
```

두 클래스의 `calculateFee` 메서드가 **완전히 동일**해졌다. 추출한 `calculateCallFee` 메서드 안에 서로 다른 부분을 격리시켜 놓았다. 이제 같은 코드를 부모 클래스로 올리는 일만 남았다.

### 3.3 2단계: 중복 코드를 부모 클래스로 올려라

부모 클래스를 추가하자. 목표는 모든 클래스들이 추상화에 의존하도록 만드는 것이기 때문에 이 클래스는 **추상 클래스**로 구현하는 것이 적합하다. 새로운 부모 클래스의 이름은 `AbstractPhone`으로 하고, `Phone`과 `NightlyDiscountPhone`이 `AbstractPhone`을 상속받도록 수정하자.

공통 코드를 옮길 때 **인스턴스 변수보다 메서드를 먼저 이동**시키는 게 편하다. 메서드를 옮기고 나면 그 메서드에 필요한 인스턴스 변수가 무엇인지를 컴파일 에러를 통해 자동으로 알 수 있기 때문이다.

단계별로 살펴보자:

1. `calculateFee` 메서드를 `AbstractPhone`으로 이동 → `calls`가 존재하지 않는다는 에러 발생
2. `calls` 인스턴스 변수를 `AbstractPhone`으로 이동 → `calculateCallFee` 메서드를 찾을 수 없다는 에러 발생
3. `calculateCallFee`는 시그니처는 동일하지만 내부 구현이 다름 → **추상 메서드**로 선언

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public abstract class AbstractPhone {
    private List<Call> calls = new ArrayList<>();

    public Money calculateFee() {
        Money result = Money.ZERO;
        for (Call call : calls) {
            result = result.plus(calculateCallFee(call));
        }
        return result;
    }

    abstract protected Money calculateCallFee(Call call);
}

public class Phone extends AbstractPhone {
    private Money amount;
    private Duration seconds;

    public Phone(Money amount, Duration seconds) {
        this.amount = amount;
        this.seconds = seconds;
    }

    @Override
    protected Money calculateCallFee(Call call) {
        return amount.times(call.getDuration().getSeconds() / seconds.getSeconds());
    }
}

public class NightlyDiscountPhone extends AbstractPhone {
    private static final int LATE_NIGHT_HOUR = 22;
    private Money nightlyAmount;
    private Money regularAmount;
    private Duration seconds;

    public NightlyDiscountPhone(Money nightlyAmount, Money regularAmount, Duration seconds) {
        this.nightlyAmount = nightlyAmount;
        this.regularAmount = regularAmount;
        this.seconds = seconds;
    }

    @Override
    protected Money calculateCallFee(Call call) {
        if (call.getFrom().getHour() >= LATE_NIGHT_HOUR) {
            return nightlyAmount.times(call.getDuration().getSeconds() / seconds.getSeconds());
        }
        return regularAmount.times(call.getDuration().getSeconds() / seconds.getSeconds());
    }
}
```

</details>

```typescript
// TypeScript
abstract class AbstractPhone {
    private calls: Call[] = [];

    calculateFee(): number {
        let result = 0;
        for (const call of this.calls) {
            result += this.calculateCallFee(call);
        }
        return result;
    }

    protected abstract calculateCallFee(call: Call): number;
}

class Phone extends AbstractPhone {
    constructor(
        private readonly amount: number,
        private readonly seconds: number,
    ) {
        super();
    }

    protected calculateCallFee(call: Call): number {
        return this.amount * (call.getDuration() / this.seconds);
    }
}

class NightlyDiscountPhone extends AbstractPhone {
    private static readonly LATE_NIGHT_HOUR = 22;

    constructor(
        private readonly nightlyAmount: number,
        private readonly regularAmount: number,
        private readonly seconds: number,
    ) {
        super();
    }

    protected calculateCallFee(call: Call): number {
        if (call.getFrom().getHours() >= NightlyDiscountPhone.LATE_NIGHT_HOUR) {
            return this.nightlyAmount * (call.getDuration() / this.seconds);
        }
        return this.regularAmount * (call.getDuration() / this.seconds);
    }
}
```

리팩터링 후의 상속 계층:

```
┌──────────────────────────────┐
│      AbstractPhone           │
├──────────────────────────────┤
│ + calculateFee()             │
│ # calculateCallFee(call) {A} │ ← 추상 메서드
└──────────▲───────────────────┘
           │
     ┌─────┴──────┐
     │            │
┌────┴────┐  ┌───┴──────────────────┐
│  Phone  │  │ NightlyDiscountPhone │
├─────────┤  ├──────────────────────┤
│ # calculateCallFee(call) │  │ # calculateCallFee(call)  │
└─────────┘  └──────────────────────┘
```

> **핵심 통찰**: '위로 올리기' 전략은 실패했더라도 수정하기 쉬운 문제를 발생시킨다. 추상화하지 않고 빼먹은 코드가 있더라도 하위 클래스가 해당 행동을 필요로 할 때가 오면 이 문제는 바로 눈에 띈다. 반대로 구체적인 구현을 아래로 내리는 방식은 작은 실수 한 번으로도 구체적인 행동을 상위 클래스에 남겨놓게 된다[Metz12].

### 3.4 추상화가 핵심이다

공통 코드를 이동시킨 후에 각 클래스는 서로 다른 변경의 이유를 가진다:

| 클래스 | 변경 이유 |
|---|---|
| `AbstractPhone` | 전체 통화 목록을 계산하는 방법이 바뀔 경우 |
| `Phone` | 일반 요금제의 통화 한 건을 계산하는 방식이 바뀔 경우 |
| `NightlyDiscountPhone` | 심야 할인 요금제의 통화 한 건을 계산하는 방식이 바뀔 경우 |

세 클래스는 각각 하나의 변경 이유만을 가진다. 이 클래스들은 **단일 책임 원칙**을 준수하기 때문에 응집도가 높다.

자식 클래스인 `Phone`과 `NightlyDiscountPhone`은 부모 클래스인 `AbstractPhone`의 구체적인 구현에 의존하지 않는다. 오직 추상 메서드인 `calculateCallFee`에만 의존한다. 이 설계는 **낮은 결합도**를 유지하고 있다.

부모 클래스 역시 자신의 내부에 구현된 추상 메서드를 호출하기 때문에 추상화에 의존한다고 말할 수 있다. **의존성 역전 원칙**도 준수한다. 요금 계산과 관련된 상위 수준의 정책을 구현하는 `AbstractPhone`이 세부적인 요금 계산 로직을 구현하는 `Phone`과 `NightlyDiscountPhone`에 의존하지 않고, 그 반대로 구체 클래스들이 추상화인 `AbstractPhone`에 의존하기 때문이다.

새로운 요금제를 추가하기도 쉽다. `AbstractPhone`을 상속받는 새로운 클래스를 추가한 후 `calculateCallFee` 메서드만 오버라이딩하면 된다. 다른 클래스를 수정할 필요가 없다. 현재의 설계는 확장에는 열려 있고 수정에는 닫혀 있기 때문에 **개방-폐쇄 원칙** 역시 준수한다.

### 3.5 의도를 드러내는 이름 선택하기

한 가지 아쉬운 점이 있다. `NightlyDiscountPhone`이라는 이름은 심야 할인 요금제와 관련된 내용을 구현한다는 사실을 명확하게 전달한다. 그에 반해 `Phone`은 일반 요금제와 관련된 내용을 구현한다는 사실을 명시적으로 전달하지 못한다. `AbstractPhone`이라는 이름 역시 전화기를 포괄한다는 의미를 명확하게 전달하지 못한다.

따라서 이름을 다음과 같이 변경하는 것이 적절하다:

| 변경 전 | 변경 후 | 이유 |
|---|---|---|
| `AbstractPhone` | `Phone` | 전화기를 포괄하는 추상 개념 |
| `Phone` | `RegularPhone` | 일반 요금제를 명시적으로 표현 |
| `NightlyDiscountPhone` | `NightlyDiscountPhone` (유지) | 이미 명확 |

```
┌─────────────────────────────┐
│        Phone {abstract}     │
├─────────────────────────────┤
│ + calculateFee()            │
│ # calculateCallFee(call) {A}│
└─────────────▲───────────────┘
              │
    ┌─────────┴──────────┐
    │                    │
┌───┴──────────┐  ┌──────┴──────────────┐
│ RegularPhone │  │ NightlyDiscountPhone│
├──────────────┤  ├─────────────────────┤
│ # calculateCallFee(call) │  │ # calculateCallFee(call) │
└──────────────┘  └─────────────────────┘
```

### 3.6 세금 추가하기: 추상화의 효과 검증

수정된 코드는 이전 코드보다 더 쉽게 변경할 수 있을까? 통화 요금에 세금을 부과하는 요구사항을 반영해 보자.

세금은 모든 요금제에 공통으로 적용돼야 하는 요구사항이다. 따라서 공통 코드를 담고 있는 추상 클래스인 `Phone`을 수정하면 모든 자식 클래스 간에 수정 사항을 공유할 수 있다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public abstract class Phone {
    private double taxRate;
    private List<Call> calls = new ArrayList<>();

    public Phone(double taxRate) {
        this.taxRate = taxRate;
    }

    public Money calculateFee() {
        Money result = Money.ZERO;
        for (Call call : calls) {
            result = result.plus(calculateCallFee(call));
        }
        return result.plus(result.times(taxRate));
    }

    protected abstract Money calculateCallFee(Call call);
}

public class RegularPhone extends Phone {
    public RegularPhone(Money amount, Duration seconds, double taxRate) {
        super(taxRate);
        this.amount = amount;
        this.seconds = seconds;
    }
    // ...
}

public class NightlyDiscountPhone extends Phone {
    public NightlyDiscountPhone(Money nightlyAmount, Money regularAmount,
                                 Duration seconds, double taxRate) {
        super(taxRate);
        this.nightlyAmount = nightlyAmount;
        this.regularAmount = regularAmount;
        this.seconds = seconds;
    }
    // ...
}
```

</details>

```typescript
// TypeScript
abstract class Phone {
    private calls: Call[] = [];

    constructor(private readonly taxRate: number) {}

    calculateFee(): number {
        let result = 0;
        for (const call of this.calls) {
            result += this.calculateCallFee(call);
        }
        return result + result * this.taxRate; // 세금 한 번만 추가하면 끝!
    }

    protected abstract calculateCallFee(call: Call): number;
}

class RegularPhone extends Phone {
    constructor(
        private readonly amount: number,
        private readonly seconds: number,
        taxRate: number,
    ) {
        super(taxRate);
    }

    protected calculateCallFee(call: Call): number {
        return this.amount * (call.getDuration() / this.seconds);
    }
}

class NightlyDiscountPhone extends Phone {
    private static readonly LATE_NIGHT_HOUR = 22;

    constructor(
        private readonly nightlyAmount: number,
        private readonly regularAmount: number,
        private readonly seconds: number,
        taxRate: number,
    ) {
        super(taxRate);
    }

    protected calculateCallFee(call: Call): number {
        if (call.getFrom().getHours() >= NightlyDiscountPhone.LATE_NIGHT_HOUR) {
            return this.nightlyAmount * (call.getDuration() / this.seconds);
        }
        return this.regularAmount * (call.getDuration() / this.seconds);
    }
}
```

안타깝게도 이것으로 모든 것이 끝난 것은 아니다. `Phone`에 인스턴스 변수인 `taxRate`를 추가했고 생성자를 추가했다. 이로 인해 `RegularPhone`과 `NightlyDiscountPhone`의 **생성자 역시 수정**해야 한다.

클래스라는 도구는 메서드뿐만 아니라 인스턴스 변수도 함께 포함한다. 따라서 클래스 사이의 상속은 자식 클래스가 부모 클래스가 구현한 행동뿐만 아니라 **인스턴스 변수에 대해서도 결합**되게 만든다.

인스턴스 변수의 목록이 변하지 않는 상황에서 객체의 행동만 변경된다면 상속 계층에 속한 각 클래스들을 독립적으로 진화시킬 수 있다. 하지만 인스턴스 변수가 추가되는 경우는 다르다. 자식 클래스는 자신의 인스턴스를 생성할 때 부모 클래스에 정의된 인스턴스 변수를 초기화해야 하기 때문에, 부모 클래스에 추가된 인스턴스 변수는 자식 클래스의 초기화 로직에 영향을 미치게 된다.

> **핵심 통찰**: 인스턴스 초기화 로직을 변경하는 것이 두 클래스에 동일한 세금 계산 코드를 중복시키는 것보다는 현명한 선택이다. 객체 생성 로직에 대한 변경을 막기보다는 **핵심 로직의 중복을 막아라**. 핵심 로직은 한 곳에 모아 놓고 조심스럽게 캡슐화해야 한다.

---

## 4. 차이에 의한 프로그래밍

상속을 사용하면 이미 존재하는 클래스의 코드를 기반으로 다른 부분을 구현함으로써 새로운 기능을 쉽고 빠르게 추가할 수 있다. 상속이 강력한 이유는 익숙한 개념을 이용해서 새로운 개념을 쉽고 빠르게 추가할 수 있기 때문이다.

이처럼 기존 코드와 다른 부분만을 추가함으로써 애플리케이션의 기능을 확장하는 방법을 **차이에 의한 프로그래밍**(*Programming by Difference*)[Feathers04]이라고 부른다. 상속을 이용하면 이미 존재하는 클래스의 코드를 쉽게 재사용할 수 있기 때문에 애플리케이션의 점진적인 정의(*Incremental Definition*)가 가능해진다[Taivalsaari96].

```
차이에 의한 프로그래밍:

┌───────────────────────────────┐
│   기존 클래스 (재사용 코드)     │   상속을 이용하면
│   ┌───────────────────────┐   │   기존 코드를 재사용하면서
│   │ 공통 코드 A           │   │   차이점만 새로 구현할 수 있다.
│   │ 공통 코드 B           │   │
│   │ 공통 코드 C           │   │
│   └───────────────────────┘   │
└───────────────▲───────────────┘
                │ extends
┌───────────────┴───────────────┐
│   새 클래스 (차이점만 구현)     │
│   ┌───────────────────────┐   │
│   │ 차이 코드 D           │   │ ← 이 부분만 직접 구현
│   └───────────────────────┘   │
└───────────────────────────────┘
```

차이에 의한 프로그래밍의 목표는 **중복 코드를 제거**하고 **코드를 재사용**하는 것이다. 사실 중복 코드 제거와 코드 재사용은 동일한 행동을 가리키는 서로 다른 단어다. 코드를 재사용하는 것은 단순히 문자를 타이핑하는 수고를 덜어주는 수준의 문제가 아니다. 재사용 가능한 코드란 심각한 버그가 존재하지 않는 코드다. 따라서 코드를 재사용하면 코드의 품질은 유지하면서도 코드를 작성하는 노력과 테스트는 줄일 수 있다.

하지만 시간이 흐르고 객체지향에 대한 이해가 깊어지면서 사람들은 코드를 재사용하기 위해 맹목적으로 상속을 사용하는 것이 위험하다는 사실을 깨닫기 시작했다. 상속이 코드 재사용이라는 측면에서 매우 강력한 도구인 것은 사실이지만, 강력한 만큼 잘못 사용할 경우에 돌아오는 피해 역시 크다. 상속의 오용과 남용은 애플리케이션을 이해하고 확장하기 어렵게 만든다. **정말로 필요한 경우에만 상속을 사용하라.**

> **핵심 통찰**: 상속은 코드 재사용과 관련된 대부분의 경우에 우아한 해결 방법이 아니다. 객체지향에 능숙한 개발자들은 상속의 단점을 피하면서도 코드를 재사용할 수 있는 더 좋은 방법이 있다는 사실을 알고 있다. 바로 **합성**이다.

---

## 설계 원칙

| 원칙 | 설명 | 예제에서의 적용 |
|---|---|---|
| **DRY 원칙** | 동일한 지식을 시스템 내에서 중복하지 마라 | Phone과 NightlyDiscountPhone의 중복 코드를 AbstractPhone으로 통합 |
| **추상화에 의존하라** | 부모 클래스와 자식 클래스 모두 구현이 아닌 추상화에 의존해야 한다 | 추상 메서드 `calculateCallFee`를 통해 결합도 감소 |
| **차이를 메서드로 추출하라** | 두 메서드가 유사하다면 차이점을 별도의 메서드로 분리하라 | `calculateFee`에서 `calculateCallFee`를 추출 |
| **자식 클래스의 코드를 상위로 올려라** | 구체적 코드를 내리지 말고 공통 코드를 올려서 추상화하라 | `calculateFee`를 부모 클래스로, `calculateCallFee`를 추상 메서드로 |
| **의도를 드러내는 이름** | 클래스의 역할이 이름에서 명확히 드러나야 한다 | `AbstractPhone` → `Phone`, `Phone` → `RegularPhone` |
| **개방-폐쇄 원칙** | 확장에는 열려 있고 수정에는 닫혀 있어야 한다 | 새 요금제 추가 시 `calculateCallFee`만 오버라이딩, 기존 클래스 수정 불필요 |

---

## 요약

- **중복 코드**는 변경을 방해하는 가장 큰 적이다. 중복 여부를 판단하는 기준은 코드의 모양이 아니라 **변경에 반응하는 방식**이다.
- **DRY 원칙**(Don't Repeat Yourself)은 동일한 지식을 시스템 내에서 중복하지 말라는 원칙이다.
- 코드를 복사해서 새 클래스를 만드는 방식은 구현은 빠르지만, 중복 코드는 새로운 중복 코드를 부르고 일관성이 무너질 위험이 있다.
- **타입 코드**를 사용해 클래스를 합치는 것은 낮은 응집도와 높은 결합도를 초래하므로 좋은 해결책이 아니다.
- **상속**을 이용하면 코드를 재사용할 수 있지만, `super` 참조를 통해 부모 클래스를 직접 호출하면 두 클래스가 강하게 결합된다.
- **취약한 기반 클래스 문제**는 상속이라는 문맥 안에서 결합도가 초래하는 문제점이다. (1) 불필요한 인터페이스 상속, (2) 메서드 오버라이딩의 오작용, (3) 부모-자식 동시 수정이 대표적 사례다.
- 상속의 피해를 줄이려면 **추상화에 의존**해야 한다. 차이점을 메서드로 추출하고, 공통 코드를 추상 클래스로 올려라.
- 인스턴스 변수가 추가되면 상속 계층 전반에 걸쳐 생성자 변경이 전파될 수 있지만, 핵심 로직의 중복보다는 훨씬 나은 선택이다.
- **차이에 의한 프로그래밍**은 기존 코드와 다른 부분만 추가하여 기능을 확장하는 방법이다. 상속은 이를 가능하게 하지만, 맹목적 사용은 위험하다.
- 상속의 단점을 피하면서 코드를 재사용할 수 있는 더 좋은 방법은 **합성**이다 (11장).

---

## 다른 챕터와의 관계

- **Chapter 4 (설계 품질과 트레이드오프)**: 4장에서 정의한 결합도 개념(하나의 모듈이 다른 모듈에 대해 얼마나 많은 지식을 갖고 있는지의 정도)이 상속 맥락에서 구체화된다. 상속은 자식 클래스가 부모 클래스의 구현 세부사항에 의존하도록 강제하여 결합도를 높인다.
- **Chapter 8 (의존성 관리하기)**: 8장에서 다룬 의존성 역전 원칙(DIP)이 상속 계층의 설계에 적용된다. 추상 클래스 `Phone`이 구체 클래스에 의존하지 않고, 구체 클래스들이 추상화에 의존하는 구조가 DIP를 실현한다.
- **Chapter 9 (유연한 설계)**: 9장에서 다룬 개방-폐쇄 원칙(OCP)이 리팩터링 후의 설계에서 달성된다. 새 요금제 추가 시 기존 클래스 수정 없이 `calculateCallFee`만 오버라이딩하면 된다.
- **Chapter 11 (합성과 유연한 설계)**: 이번 장에서 드러난 상속의 한계(취약한 기반 클래스 문제, 강한 결합도)를 합성을 통해 극복하는 방법을 다룬다. 상속은 코드 재사용의 관점에서 강력하지만, 합성이 더 유연한 대안이 될 수 있다.
