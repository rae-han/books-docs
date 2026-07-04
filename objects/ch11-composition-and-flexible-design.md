# Chapter 11: Composition and Flexible Design (합성과 유연한 설계)

## 핵심 질문

상속의 남용으로 인한 클래스 폭발 문제를 어떻게 해결할 수 있는가? 합성은 상속과 비교하여 코드 재사용과 유연한 설계에서 어떤 장점을 제공하며, 믹스인은 이 둘의 특성을 어떻게 결합하는가?

---

## 1. 상속을 합성으로 변경하기

상속과 합성은 객체지향 프로그래밍에서 가장 널리 사용되는 코드 재사용 기법이다. 상속이 부모 클래스와 자식 클래스를 연결해서 부모 클래스의 코드를 재사용하는 데 비해, 합성은 전체를 표현하는 객체가 부분을 표현하는 객체를 포함해서 부분 객체의 코드를 재사용한다.

| 비교 항목 | 상속 (is-a) | 합성 (has-a) |
|---|---|---|
| **의존 대상** | 부모 클래스의 구현 (화이트박스 재사용) | 포함된 객체의 퍼블릭 인터페이스 (블랙박스 재사용) |
| **의존성 해결 시점** | 컴파일타임 | 런타임 |
| **관계 변경** | 코드 작성 시점에 고정, 실행 중 변경 불가 | 실행 시점에 동적으로 변경 가능 |
| **결합도** | 클래스 사이의 높은 결합도 | 객체 사이의 낮은 결합도 |

> [코드 재사용을 위해서는] 객체 합성이 클래스 상속보다 더 좋은 방법이다[GOF94].

상속은 부모 클래스 안에 구현된 코드 자체를 재사용하지만, 합성은 포함되는 객체의 퍼블릭 인터페이스를 재사용한다. 따라서 상속 대신 합성을 사용하면 **구현에 대한 의존성을 인터페이스에 대한 의존성으로 변경**할 수 있다. 다시 말해서 클래스 사이의 높은 결합도를 객체 사이의 낮은 결합도로 대체할 수 있는 것이다.

> **핵심 통찰**: 설계는 변경과 관련된 것이다. 변경에 유연하게 대처할 수 있는 설계가 대부분의 경우에 정답일 가능성이 높다. 합성은 내부에 포함되는 객체의 구현이 아닌 퍼블릭 인터페이스에 의존하기 때문에, 포함된 객체의 내부 구현이 변경되더라도 영향을 최소화할 수 있다.

10장에서 코드 재사용을 위해 상속을 남용했을 때 직면할 수 있는 세 가지 문제점을 살펴봤다. 합성을 사용하면 이 세 가지 문제를 해결할 수 있다. 상속을 합성으로 바꾸는 방법은 매우 간단한데, 자식 클래스에 선언된 상속 관계를 제거하고 부모 클래스의 인스턴스를 자식 클래스의 인스턴스 변수로 선언하면 된다.

### 1.1 불필요한 인터페이스 상속 문제: Properties와 Stack

`Hashtable`을 상속받던 `Properties` 클래스를 합성 관계로 변경하면, 더 이상 불필요한 `Hashtable`의 오퍼레이션들이 `Properties`의 퍼블릭 인터페이스를 오염시키지 않는다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Properties {
    private Hashtable<String, String> properties = new Hashtable<>();

    public String setProperty(String key, String value) {
        return properties.put(key, value);
    }

    public String getProperty(String key) {
        return properties.get(key);
    }
}
```

</details>

```typescript
// TypeScript
class Properties {
    private properties = new Map<string, string>();

    setProperty(key: string, value: string): string | undefined {
        const old = this.properties.get(key);
        this.properties.set(key, value);
        return old;
    }

    getProperty(key: string): string | undefined {
        return this.properties.get(key);
    }
}
```

클라이언트는 오직 `Properties`에서 정의한 오퍼레이션만 사용할 수 있다. 모든 타입의 키와 값을 저장할 수 있는 `Hashtable`의 오퍼레이션을 사용할 수 없기 때문에, `String` 타입의 키와 값만 허용하는 `Properties`의 규칙을 어길 위험성은 사라진다.

`Vector`를 상속받던 `Stack` 역시 같은 방식으로 합성 관계로 변경할 수 있다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Stack<E> {
    private Vector<E> elements = new Vector<>();

    public E push(E item) {
        elements.addElement(item);
        return item;
    }

    public E pop() {
        if (elements.isEmpty()) {
            throw new EmptyStackException();
        }
        return elements.remove(elements.size() - 1);
    }
}
```

</details>

```typescript
// TypeScript
class Stack<E> {
    private elements: E[] = [];

    push(item: E): E {
        this.elements.push(item);
        return item;
    }

    pop(): E {
        if (this.elements.length === 0) {
            throw new Error("EmptyStackException");
        }
        return this.elements.pop()!;
    }
}
```

이제 `Stack`의 퍼블릭 인터페이스에는 불필요한 `Vector`의 오퍼레이션들이 포함되지 않는다. 클라이언트는 더 이상 임의의 위치에 요소를 추가하거나 삭제할 수 없으며, 마지막 위치에서만 요소를 추가하거나 삭제할 수 있다는 `Stack`의 규칙을 어길 수 없게 된다.

### 1.2 메서드 오버라이딩의 오작용 문제: InstrumentedHashSet

`InstrumentedHashSet`도 같은 방법으로 합성 관계로 변경할 수 있다. `HashSet` 인스턴스를 내부에 포함한 후, `HashSet`의 퍼블릭 인터페이스에서 제공하는 오퍼레이션들을 이용해 필요한 기능을 구현하면 된다.

그러나 `InstrumentedHashSet`의 경우에는 `Properties`나 `Stack`과 다른 점이 한 가지 있다. `Properties`와 `Stack`을 합성으로 변경한 이유는 불필요한 오퍼레이션들이 퍼블릭 인터페이스에 스며드는 것을 방지하기 위해서다. 하지만 `InstrumentedHashSet`의 경우에는 `HashSet`이 제공하는 퍼블릭 인터페이스를 그대로 제공해야 한다.

`HashSet`에 대한 구현 결합도는 제거하면서도 퍼블릭 인터페이스는 그대로 유지할 수 있는 방법은, 자바의 인터페이스를 사용하는 것이다. `InstrumentedHashSet`이 `Set` 인터페이스를 실체화하면서 내부에 `HashSet`의 인스턴스를 합성하면 된다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class InstrumentedHashSet<E> implements Set<E> {
    private int addCount = 0;
    private Set<E> set;

    public InstrumentedHashSet(Set<E> set) {
        this.set = set;
    }

    @Override
    public boolean add(E e) {
        addCount++;
        return set.add(e);
    }

    @Override
    public boolean addAll(Collection<? extends E> c) {
        addCount += c.size();
        return set.addAll(c);
    }

    public int getAddCount() {
        return addCount;
    }

    // Set 인터페이스의 나머지 메서드들은 모두 내부 set에 위임
    @Override public boolean remove(Object o) { return set.remove(o); }
    @Override public void clear() { set.clear(); }
    @Override public boolean contains(Object o) { return set.contains(o); }
    @Override public int size() { return set.size(); }
    @Override public boolean isEmpty() { return set.isEmpty(); }
    @Override public Iterator<E> iterator() { return set.iterator(); }
    // ... 나머지 포워딩 메서드들
}
```

</details>

```typescript
// TypeScript
class InstrumentedSet<E> {
    private addCount = 0;
    private set: Set<E>;

    constructor(set: Set<E>) {
        this.set = set;
    }

    add(e: E): this {
        this.addCount++;
        this.set.add(e);
        return this;
    }

    addAll(c: E[]): this {
        this.addCount += c.length;
        c.forEach(e => this.set.add(e));
        return this;
    }

    getAddCount(): number {
        return this.addCount;
    }

    // 나머지는 내부 set에 포워딩
    delete(e: E): boolean { return this.set.delete(e); }
    has(e: E): boolean { return this.set.has(e); }
    get size(): number { return this.set.size; }
    clear(): void { this.set.clear(); }
}
```

이처럼 `Set`의 오퍼레이션을 오버라이딩한 인스턴스 메서드에서 내부의 `HashSet` 인스턴스에게 동일한 메서드 호출을 그대로 전달하는 것을 **포워딩**(*Forwarding - 동일한 메서드를 호출하기 위해 추가된 메서드를 통해 요청을 전달하는 기법*)이라 부르고, 동일한 메서드를 호출하기 위해 추가된 메서드를 **포워딩 메서드**(*Forwarding Method*)라고 부른다[Bloch08]. 포워딩은 기존 클래스의 인터페이스를 그대로 외부에 제공하면서 구현에 대한 결합 없이 일부 작동 방식을 변경하고 싶은 경우에 사용할 수 있는 유용한 기법이다.

### 1.3 부모 클래스와 자식 클래스의 동시 수정 문제: PersonalPlaylist

안타깝게도 `Playlist`의 경우에는 합성으로 변경하더라도 가수별 노래 목록을 유지하기 위해 `Playlist`와 `PersonalPlaylist`를 함께 수정해야 하는 문제가 해결되지는 않는다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class PersonalPlaylist {
    private Playlist playlist = new Playlist();

    public void append(Song song) {
        playlist.append(song);
    }

    public void remove(Song song) {
        playlist.getTracks().remove(song);
        playlist.getSingers().remove(song.getSinger());
    }
}
```

</details>

```typescript
// TypeScript
class PersonalPlaylist {
    private playlist = new Playlist();

    append(song: Song): void {
        this.playlist.append(song);
    }

    remove(song: Song): void {
        this.playlist.getTracks().delete(song);
        this.playlist.getSingers().delete(song.getSinger());
    }
}
```

그렇다고 하더라도 여전히 상속보다는 합성을 사용하는 게 더 좋은데, 향후에 `Playlist`의 내부 구현을 변경하더라도 파급 효과를 최대한 `PersonalPlaylist` 내부로 캡슐화할 수 있기 때문이다. 대부분의 경우 **구현에 대한 결합보다는 인터페이스에 대한 결합이 더 좋다**는 사실을 기억하라.

> 몽키 패치(*Monkey Patch - 현재 실행 중인 환경에만 영향을 미치도록 지역적으로 코드를 수정하거나 확장하는 것*)란 기법을 통해 소스 코드가 없거나 수정 권한이 없는 클래스에도 메서드를 추가할 수 있다. 루비의 열린 클래스(*Open Class*), C#의 확장 메서드(*Extension Method*), 스칼라의 암시적 변환(*Implicit Conversion*) 역시 몽키 패치의 일종이다. 자바는 언어 차원에서 몽키 패치를 지원하지 않기 때문에 바이트코드를 직접 변환하거나 AOP(*Aspect-Oriented Programming*)를 이용해 구현한다.

이번 장의 시작 부분에서 상속과 비교해서 합성은 **안정성**과 **유연성**이라는 장점을 제공한다고 말했다. 지금까지는 합성을 사용해서 변경에 불안정한 코드를 안정적으로 유지하는 방법을 살펴봤다. 이제 두 번째 장점인 유연성을 살펴보자. 이 경우에도 핵심은 동일하다. **구현이 아니라 인터페이스에 의존하면 설계가 유연해진다**는 것이다.

---

## 2. 상속으로 인한 조합의 폭발적인 증가

상속으로 인해 결합도가 높아지면 코드를 수정하는 데 필요한 작업의 양이 과도하게 늘어나는 경향이 있다. 가장 일반적인 상황은 작은 기능들을 조합해서 더 큰 기능을 수행하는 객체를 만들어야 하는 경우다. 일반적으로 다음과 같은 두 가지 문제점이 발생한다:

- 하나의 기능을 추가하거나 수정하기 위해 불필요하게 많은 수의 클래스를 추가하거나 수정해야 한다.
- 단일 상속만 지원하는 언어에서는 상속으로 인해 오히려 중복 코드의 양이 늘어날 수 있다.

### 2.1 기본 정책과 부가 정책 조합하기

10장에서 소개했던 핸드폰 과금 시스템에 새로운 요구 사항을 추가해 보자. 핸드폰 요금제가 **기본 정책**과 **부가 정책**을 조합해서 구성된다고 가정할 것이다.

| 구분 | 기본 정책 | 부가 정책 |
|---|---|---|
| **종류** | 일반 요금제, 심야 할인 요금제 | 세금 정책, 기본 요금 할인 정책 |
| **기준** | 가입자의 통화 정보(한 달 통화량) 기반 | 통화량과 무관, 기본 정책에 선택적 추가 |

부가 정책은 다음과 같은 특성을 가진다:

1. **기본 정책의 계산 결과에 적용된다**: 세금 정책은 기본 정책의 계산이 끝난 결과에 세금을 부과한다.
2. **선택적으로 적용할 수 있다**: 기본 정책의 계산 결과에 세금 정책을 적용할 수도 있고 적용하지 않을 수도 있다.
3. **조합 가능하다**: 세금 정책만 적용하거나 기본 요금 할인 정책만 적용하거나 둘을 함께 적용할 수 있다.
4. **부가 정책은 임의의 순서로 적용 가능하다**: 세금 정책을 먼저 적용한 후 기본 요금 할인 정책을 적용하거나, 그 반대 순서로도 적용할 수 있다.

조합 가능한 모든 요금 정책을 나열하면 다음과 같다:

```
기본 정책          부가 정책
──────────────    ──────────────────────────────────
일반 요금제    →   (없음)
심야 할인       →   (없음)
일반 요금제    →   세금 정책
심야 할인       →   세금 정책
일반 요금제    →   기본 요금 할인 정책
심야 할인       →   기본 요금 할인 정책
일반 요금제    →   세금 정책 → 기본 요금 할인 정책
심야 할인       →   세금 정책 → 기본 요금 할인 정책
일반 요금제    →   기본 요금 할인 정책 → 세금 정책
심야 할인       →   기본 요금 할인 정책 → 세금 정책
```

이 요구 사항을 구현하는 데 가장 큰 장벽은 기본 정책과 부가 정책의 **조합 가능한 수가 매우 많다**는 것이다. 따라서 설계는 다양한 조합을 수용할 수 있도록 유연해야 한다.

### 2.2 상속을 이용해서 기본 정책 구현하기

기본 정책은 `Phone` 추상 클래스를 루트로 삼는 기존의 상속 계층을 그대로 이용한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public abstract class Phone {
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

public class RegularPhone extends Phone {
    private Money amount;
    private Duration seconds;

    public RegularPhone(Money amount, Duration seconds) {
        this.amount = amount;
        this.seconds = seconds;
    }

    @Override
    protected Money calculateCallFee(Call call) {
        return amount.times(call.getDuration().getSeconds() / seconds.getSeconds());
    }
}

public class NightlyDiscountPhone extends Phone {
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
abstract class Phone {
    private calls: Call[] = [];

    calculateFee(): Money {
        return this.calls.reduce(
            (result, call) => result.plus(this.calculateCallFee(call)),
            Money.ZERO
        );
    }

    protected abstract calculateCallFee(call: Call): Money;
}

class RegularPhone extends Phone {
    constructor(
        private amount: Money,
        private seconds: Duration
    ) { super(); }

    protected calculateCallFee(call: Call): Money {
        return this.amount.times(call.getDuration().getSeconds() / this.seconds.getSeconds());
    }
}

class NightlyDiscountPhone extends Phone {
    private static readonly LATE_NIGHT_HOUR = 22;

    constructor(
        private nightlyAmount: Money,
        private regularAmount: Money,
        private seconds: Duration
    ) { super(); }

    protected calculateCallFee(call: Call): Money {
        if (call.getFrom().getHour() >= NightlyDiscountPhone.LATE_NIGHT_HOUR) {
            return this.nightlyAmount.times(call.getDuration().getSeconds() / this.seconds.getSeconds());
        }
        return this.regularAmount.times(call.getDuration().getSeconds() / this.seconds.getSeconds());
    }
}
```

### 2.3 기본 정책에 세금 정책 조합하기

일반 요금제에 세금 정책을 조합하려면 `RegularPhone`을 상속받은 `TaxableRegularPhone`을 추가한다. 하지만 부모 클래스의 메서드를 재사용하기 위해 `super` 호출을 사용하면 자식 클래스와 부모 클래스 사이의 결합도가 높아진다. 결합도를 낮추는 방법은 부모 클래스에 추상 메서드(또는 훅 메서드)를 제공하는 것이다.

`Phone` 클래스에 새로운 훅 메서드인 `afterCalculated`를 추가하자. 이 메서드는 자식 클래스에게 전체 요금을 계산한 후에 수행할 로직을 추가할 수 있는 기회를 제공한다.

> 추상 메서드와 동일하게 자식 클래스에서 오버라이딩할 의도로 메서드를 추가했지만, 편의를 위해 기본 구현을 제공하는 메서드를 **훅 메서드**(*Hook Method*)라고 부른다. 모든 자식 클래스가 추상 메서드를 동일한 방식으로 구현한다면 상속 계층 전반에 걸쳐 중복 코드가 존재하게 되므로, 기본 구현을 제공하는 훅 메서드가 더 적절하다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public abstract class Phone {
    private List<Call> calls = new ArrayList<>();

    public Money calculateFee() {
        Money result = Money.ZERO;
        for (Call call : calls) {
            result = result.plus(calculateCallFee(call));
        }
        return afterCalculated(result);
    }

    protected abstract Money calculateCallFee(Call call);

    protected Money afterCalculated(Money fee) {  // 훅 메서드
        return fee;
    }
}
```

</details>

```typescript
// TypeScript
abstract class Phone {
    private calls: Call[] = [];

    calculateFee(): Money {
        const result = this.calls.reduce(
            (acc, call) => acc.plus(this.calculateCallFee(call)),
            Money.ZERO
        );
        return this.afterCalculated(result);
    }

    protected abstract calculateCallFee(call: Call): Money;

    protected afterCalculated(fee: Money): Money {  // 훅 메서드
        return fee;
    }
}
```

이제 세금 정책을 구현하는 클래스들은 `afterCalculated` 메서드만 오버라이딩하면 된다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class TaxableRegularPhone extends RegularPhone {
    private double taxRate;

    public TaxableRegularPhone(Money amount, Duration seconds, double taxRate) {
        super(amount, seconds);
        this.taxRate = taxRate;
    }

    @Override
    protected Money afterCalculated(Money fee) {
        return fee.plus(fee.times(taxRate));
    }
}

public class TaxableNightlyDiscountPhone extends NightlyDiscountPhone {
    private double taxRate;

    public TaxableNightlyDiscountPhone(Money nightlyAmount,
            Money regularAmount, Duration seconds, double taxRate) {
        super(nightlyAmount, regularAmount, seconds);
        this.taxRate = taxRate;
    }

    @Override
    protected Money afterCalculated(Money fee) {
        return fee.plus(fee.times(taxRate));
    }
}
```

</details>

```typescript
// TypeScript
class TaxableRegularPhone extends RegularPhone {
    constructor(amount: Money, seconds: Duration, private taxRate: number) {
        super(amount, seconds);
    }

    protected override afterCalculated(fee: Money): Money {
        return fee.plus(fee.times(this.taxRate));
    }
}

class TaxableNightlyDiscountPhone extends NightlyDiscountPhone {
    constructor(nightlyAmount: Money, regularAmount: Money,
                seconds: Duration, private taxRate: number) {
        super(nightlyAmount, regularAmount, seconds);
    }

    protected override afterCalculated(fee: Money): Money {
        return fee.plus(fee.times(this.taxRate));
    }
}
```

문제는 `TaxableNightlyDiscountPhone`과 `TaxableRegularPhone` 사이에 **코드를 중복**했다는 것이다. 두 클래스의 코드를 자세히 살펴보면 부모 클래스의 이름을 제외하면 대부분의 코드가 거의 동일하다. 자바를 비롯한 대부분의 객체지향 언어는 단일 상속만 지원하기 때문에 상속으로 인해 발생하는 중복 코드 문제를 해결하기가 쉽지 않다.

### 2.4 기본 정책에 기본 요금 할인 정책 조합하기

기본 요금 할인 정책이란 매달 청구되는 요금에서 고정된 요금을 차감하는 부가 정책이다. 일반 요금제와 조합하려면 `RateDiscountableRegularPhone`, 심야 할인 요금제와 조합하려면 `RateDiscountableNightlyDiscountPhone`을 추가해야 한다. 이번에도 부가 정책을 구현한 두 클래스 사이에 중복 코드가 발생한다.

### 2.5 중복 코드의 덫에 걸리다

부가 정책은 자유롭게 조합할 수 있어야 하고, 적용되는 순서 역시 임의로 결정할 수 있어야 한다. 상속을 이용한 해결 방법은 **모든 가능한 조합별로 자식 클래스를 하나씩 추가하는 것**이다.

예를 들어 일반 요금제에 세금 정책을 조합한 후 기본 요금 할인 정책을 추가하려면 `TaxableAndRateDiscountableRegularPhone`, 반대 순서라면 `RateDiscountableAndTaxableRegularPhone`을 만들어야 한다. 심야 할인 요금제에 대해서도 동일한 조합이 필요하다.

```
상속으로 모든 조합을 구현한 클래스 계층 (10개 클래스):

                               Phone
                            /        \
                RegularPhone          NightlyDiscountPhone
               /    |    \               /    |    \
  TaxableRP   RateDiscRP  ...    TaxableNDP  RateDiscNDP  ...
     |           |                   |           |
 TaxableAnd  RateDiscAnd        TaxableAnd  RateDiscAnd
 RateDiscRP  TaxableRP          RateDiscNDP TaxableNDP
```

여기서 새로운 기본 정책인 고정 요금제(`FixedRatePhone`)를 추가한다면? 모든 부가 정책 조합에 대응하는 클래스도 함께 추가해야 하므로, 하나의 기본 정책을 추가하기 위해 **5개의 새로운 클래스**가 필요하다. 새로운 부가 정책(예: 약정 할인 정책)을 추가하면 기하급수적으로 더 많은 클래스가 필요해진다.

이처럼 상속의 남용으로 하나의 기능을 추가하기 위해 필요 이상으로 많은 수의 클래스를 추가해야 하는 경우를 가리켜 **클래스 폭발**(*Class Explosion*)[Shalloway01] 또는 **조합의 폭발**(*Combinational Explosion*) 문제라고 부른다. 클래스 폭발 문제는 자식 클래스가 부모 클래스의 구현에 강하게 결합되도록 강요하는 상속의 근본적인 한계 때문에 발생한다. 컴파일타임에 결정된 자식 클래스와 부모 클래스 사이의 관계는 변경될 수 없기 때문에, 다양한 조합이 필요한 상황에서 유일한 해결 방법은 조합의 수만큼 새로운 클래스를 추가하는 것뿐이다.

> **핵심 통찰**: 클래스 폭발 문제는 새로운 기능을 추가할 때뿐만 아니라 기능을 수정할 때도 문제가 된다. 세금 정책을 변경해야 한다면, 세금 정책과 관련된 코드가 여러 클래스 안에 중복돼 있기 때문에 모든 클래스를 찾아 동일한 방식으로 수정해야 한다. 이 클래스 중에서 하나라도 누락한다면 버그가 발생한다. 이 문제를 해결할 수 있는 최선의 방법은 **상속을 포기하는 것**이다.

---

## 3. 합성 관계로 변경하기

상속 관계는 컴파일타임에 결정되고 고정되기 때문에 코드를 실행하는 도중에는 변경할 수 없다. 따라서 여러 기능을 조합해야 하는 설계에 상속을 이용하면 모든 조합 가능한 경우별로 클래스를 추가해야 한다.

합성은 **컴파일타임 관계를 런타임 관계로 변경**함으로써 이 문제를 해결한다. 합성을 사용하면 구현이 아닌 퍼블릭 인터페이스에 대해서만 의존할 수 있기 때문에 런타임에 객체의 관계를 변경할 수 있다. 8장에서 컴파일타임 의존성과 런타임 의존성의 거리가 멀수록 설계가 유연해진다고 했던 것을 기억하라.

상속이 **조합의 결과를 개별 클래스 안으로 밀어 넣는 방법**이라면, 합성은 **조합을 구성하는 요소들을 개별 클래스로 구현한 후 실행 시점에 인스턴스를 조립하는 방법**이다.

> **핵심 통찰**: 컴파일타임 의존성에 속박되지 않고 다양한 방식의 런타임 의존성을 구성할 수 있다는 것이 합성이 제공하는 가장 큰 장점이다. 물론 컴파일타임 의존성과 런타임 의존성의 거리가 멀면 코드를 이해하기 어려워지는 것도 사실이다. 하지만 설계는 변경과 유지보수를 위해 존재한다. 설계는 트레이드오프의 산물이다. 변경에 따르는 고통이 복잡성으로 인한 혼란을 넘어서고 있다면 유연성의 손을 들어 주는 것이 현명한 판단일 확률이 높다.

### 3.1 기본 정책 합성하기

가장 먼저 해야 할 일은 각 정책을 별도의 클래스로 구현하는 것이다. 먼저 기본 정책과 부가 정책을 포괄하는 `RatePolicy` 인터페이스를 추가하자.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public interface RatePolicy {
    Money calculateFee(Phone phone);
}
```

</details>

```typescript
// TypeScript
interface RatePolicy {
    calculateFee(phone: Phone): Money;
}
```

기본 정책을 구성하는 일반 요금제와 심야 할인 요금제는 개별 요금을 계산하는 방식을 제외한 전체 처리 로직이 거의 동일하다. 이 중복 코드를 담을 추상 클래스 `BasicRatePolicy`를 추가하자.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public abstract class BasicRatePolicy implements RatePolicy {
    @Override
    public Money calculateFee(Phone phone) {
        Money result = Money.ZERO;
        for (Call call : phone.getCalls()) {
            result = result.plus(calculateCallFee(call));
        }
        return result;
    }

    protected abstract Money calculateCallFee(Call call);
}
```

</details>

```typescript
// TypeScript
abstract class BasicRatePolicy implements RatePolicy {
    calculateFee(phone: Phone): Money {
        return phone.getCalls().reduce(
            (result, call) => result.plus(this.calculateCallFee(call)),
            Money.ZERO
        );
    }

    protected abstract calculateCallFee(call: Call): Money;
}
```

`BasicRatePolicy`의 자식 클래스는 추상 메서드인 `calculateCallFee`를 오버라이딩해서 `Call`의 요금을 계산하는 자신만의 방식을 구현할 수 있다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class RegularPolicy extends BasicRatePolicy {
    private Money amount;
    private Duration seconds;

    public RegularPolicy(Money amount, Duration seconds) {
        this.amount = amount;
        this.seconds = seconds;
    }

    @Override
    protected Money calculateCallFee(Call call) {
        return amount.times(call.getDuration().getSeconds() / seconds.getSeconds());
    }
}

public class NightlyDiscountPolicy extends BasicRatePolicy {
    private static final int LATE_NIGHT_HOUR = 22;
    private Money nightlyAmount;
    private Money regularAmount;
    private Duration seconds;

    public NightlyDiscountPolicy(Money nightlyAmount, Money regularAmount, Duration seconds) {
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
class RegularPolicy extends BasicRatePolicy {
    constructor(private amount: Money, private seconds: Duration) {
        super();
    }

    protected calculateCallFee(call: Call): Money {
        return this.amount.times(call.getDuration().getSeconds() / this.seconds.getSeconds());
    }
}

class NightlyDiscountPolicy extends BasicRatePolicy {
    private static readonly LATE_NIGHT_HOUR = 22;

    constructor(
        private nightlyAmount: Money,
        private regularAmount: Money,
        private seconds: Duration
    ) { super(); }

    protected calculateCallFee(call: Call): Money {
        if (call.getFrom().getHour() >= NightlyDiscountPolicy.LATE_NIGHT_HOUR) {
            return this.nightlyAmount.times(call.getDuration().getSeconds() / this.seconds.getSeconds());
        }
        return this.regularAmount.times(call.getDuration().getSeconds() / this.seconds.getSeconds());
    }
}
```

이제 기본 정책을 이용해 요금을 계산할 수 있도록 `Phone`을 수정하자.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Phone {
    private RatePolicy ratePolicy;
    private List<Call> calls = new ArrayList<>();

    public Phone(RatePolicy ratePolicy) {
        this.ratePolicy = ratePolicy;
    }

    public List<Call> getCalls() {
        return Collections.unmodifiableList(calls);
    }

    public Money calculateFee() {
        return ratePolicy.calculateFee(this);
    }
}
```

</details>

```typescript
// TypeScript
class Phone {
    private calls: Call[] = [];

    constructor(private ratePolicy: RatePolicy) {}

    getCalls(): readonly Call[] {
        return this.calls;
    }

    calculateFee(): Money {
        return this.ratePolicy.calculateFee(this);
    }
}
```

`Phone` 내부에 `RatePolicy`에 대한 참조자가 포함돼 있다는 것에 주목하라. **이것이 바로 합성이다.** `Phone`이 다양한 요금 정책과 협력할 수 있어야 하므로 요금 정책의 타입이 `RatePolicy`라는 인터페이스로 정의돼 있다. `Phone`은 생성자를 통해 `RatePolicy` 인스턴스에 대한 의존성을 주입받는다.

다양한 종류의 객체와 협력하기 위해 합성 관계를 사용하는 경우에는, 합성하는 객체의 타입을 **인터페이스나 추상 클래스로 선언**하고 **의존성 주입**을 사용해 런타임에 필요한 객체를 설정할 수 있도록 구현하는 것이 일반적이다.

```
합성 관계를 사용한 기본 정책의 전체 구조:

  Phone ──── ratePolicy ────▶ «interface» RatePolicy
                                      │
                              BasicRatePolicy
                               /            \
                    RegularPolicy    NightlyDiscountPolicy
```

일반 요금제 규칙에 따라 통화 요금을 계산하고 싶다면 다음과 같이 `Phone`과 `RegularPolicy`의 인스턴스를 합성하면 된다.

```typescript
const phone = new Phone(new RegularPolicy(Money.wons(10), Duration.ofSeconds(10)));
```

심야 할인 요금제를 사용하고 싶다면 `NightlyDiscountPolicy`를 사용하면 된다.

```typescript
const phone = new Phone(new NightlyDiscountPolicy(Money.wons(5), Money.wons(10), Duration.ofSeconds(10)));
```

### 3.2 부가 정책 적용하기

부가 정책은 기본 정책에 대한 계산이 끝난 후에 적용된다. 부가 정책을 구현할 때는 다음의 두 가지 제약을 따라야 한다:

1. **부가 정책은 기본 정책이나 다른 부가 정책의 인스턴스를 참조할 수 있어야 한다**: 부가 정책의 인스턴스는 어떤 종류의 정책과도 합성될 수 있어야 한다.
2. **Phone의 입장에서는 자신이 기본 정책에게 메시지를 전송하고 있는지, 부가 정책에게 메시지를 전송하고 있는지를 몰라야 한다**: 기본 정책과 부가 정책은 협력 안에서 동일한 '역할'을 수행해야 한다. 이것은 부가 정책이 기본 정책과 동일한 `RatePolicy` 인터페이스를 구현해야 한다는 것을 의미한다.

```
부가 정책 적용 시 인스턴스 관계:

기본 정책만 적용:
  phone:Phone ──calculateFee──▶ RegularPolicy

기본 정책 + 세금 정책:
  phone:Phone ──calculateFee──▶ TaxablePolicy ──calculateFee──▶ RegularPolicy

기본 정책 + 할인 정책 + 세금 정책:
  phone:Phone ──▶ TaxablePolicy ──▶ RateDiscountablePolicy ──▶ RegularPolicy
```

부가 정책을 `AdditionalRatePolicy` 추상 클래스로 구현하자.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public abstract class AdditionalRatePolicy implements RatePolicy {
    private RatePolicy next;

    public AdditionalRatePolicy(RatePolicy next) {
        this.next = next;
    }

    @Override
    public Money calculateFee(Phone phone) {
        Money fee = next.calculateFee(phone);
        return afterCalculated(fee);
    }

    abstract protected Money afterCalculated(Money fee);
}
```

</details>

```typescript
// TypeScript
abstract class AdditionalRatePolicy implements RatePolicy {
    constructor(private next: RatePolicy) {}

    calculateFee(phone: Phone): Money {
        const fee = this.next.calculateFee(phone);
        return this.afterCalculated(fee);
    }

    protected abstract afterCalculated(fee: Money): Money;
}
```

`AdditionalRatePolicy`는 `Phone`의 입장에서 `RatePolicy`의 역할을 수행하기 때문에 `RatePolicy` 인터페이스를 구현한다. 또한 다른 요금 정책과 조합될 수 있도록 `RatePolicy` 타입의 `next`라는 인스턴스 변수를 내부에 포함한다. `calculateFee` 메서드는 먼저 `next`가 참조하고 있는 인스턴스에게 `calculateFee` 메시지를 전송한 후, 반환된 요금에 부가 정책을 적용하기 위해 `afterCalculated` 메서드를 호출한다.

이제 세금 정책과 기본 요금 할인 정책을 구현하자.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class TaxablePolicy extends AdditionalRatePolicy {
    private double taxRatio;

    public TaxablePolicy(double taxRatio, RatePolicy next) {
        super(next);
        this.taxRatio = taxRatio;
    }

    @Override
    protected Money afterCalculated(Money fee) {
        return fee.plus(fee.times(taxRatio));
    }
}

public class RateDiscountablePolicy extends AdditionalRatePolicy {
    private Money discountAmount;

    public RateDiscountablePolicy(Money discountAmount, RatePolicy next) {
        super(next);
        this.discountAmount = discountAmount;
    }

    @Override
    protected Money afterCalculated(Money fee) {
        return fee.minus(discountAmount);
    }
}
```

</details>

```typescript
// TypeScript
class TaxablePolicy extends AdditionalRatePolicy {
    constructor(private taxRatio: number, next: RatePolicy) {
        super(next);
    }

    protected afterCalculated(fee: Money): Money {
        return fee.plus(fee.times(this.taxRatio));
    }
}

class RateDiscountablePolicy extends AdditionalRatePolicy {
    constructor(private discountAmount: Money, next: RatePolicy) {
        super(next);
    }

    protected afterCalculated(fee: Money): Money {
        return fee.minus(this.discountAmount);
    }
}
```

```
기본 정책과 부가 정책을 조합할 수 있는 전체 구조:

                           «interface»
  Phone ── ratePolicy ──▶  RatePolicy  ◀── next
                               │                │
                    ┌──────────┴──────────┐     │
              BasicRatePolicy    AdditionalRatePolicy
              /            \         /              \
   RegularPolicy  NightlyDP  TaxablePolicy  RateDiscountablePolicy
```

### 3.3 기본 정책과 부가 정책 합성하기

이제 다양한 방식으로 정책들을 조합할 수 있는 설계가 준비됐다. 남은 일은 원하는 정책의 인스턴스를 생성한 후 의존성 주입을 통해 다른 정책의 인스턴스에 전달하는 것뿐이다.

**일반 요금제 + 세금 정책:**

```typescript
const phone = new Phone(
    new TaxablePolicy(0.05,
        new RegularPolicy(Money.wons(10), Duration.ofSeconds(10))
    )
);
```

**일반 요금제 + 기본 요금 할인 정책 + 세금 정책:**

```typescript
const phone = new Phone(
    new TaxablePolicy(0.05,
        new RateDiscountablePolicy(Money.wons(1000),
            new RegularPolicy(Money.wons(10), Duration.ofSeconds(10))
        )
    )
);
```

**일반 요금제 + 세금 정책 + 기본 요금 할인 정책** (순서만 변경):

```typescript
const phone = new Phone(
    new RateDiscountablePolicy(Money.wons(1000),
        new TaxablePolicy(0.05,
            new RegularPolicy(Money.wons(10), Duration.ofSeconds(10))
        )
    )
);
```

**심야 할인 요금제에도 동일하게 적용 가능:**

```typescript
const phone = new Phone(
    new RateDiscountablePolicy(Money.wons(1000),
        new TaxablePolicy(0.05,
            new NightlyDiscountPolicy(Money.wons(5), Money.wons(10), Duration.ofSeconds(10))
        )
    )
);
```

> **핵심 통찰**: 합성을 사용한 설계가 처음에는 상속보다 더 복잡하고 객체를 생성하고 조합하는 방식이 어려울 수 있다. 하지만 일단 설계에 익숙해지고 나면, 객체를 조합하고 사용하는 방식이 상속보다 더 예측 가능하고 일관성이 있다는 사실을 알게 될 것이다. 합성의 진가는 새로운 클래스를 추가하거나 수정하는 시점이 돼서야 비로소 알 수 있다.

### 3.4 새로운 정책 추가하기

상속 기반 설계에서는 새로운 기본 정책인 고정 요금제를 추가하면 조합 가능한 부가 정책의 수만큼 새로운 클래스를 함께 추가해야 했다. 합성 기반 설계에서는 고정 요금제가 필요하다면 고정 요금제를 구현한 클래스 **하나만** 추가한 후 원하는 방식으로 조합하면 된다.

새로운 부가 정책인 약정 할인 정책이 필요한가? 역시 클래스 **하나만** 추가하면 된다.

```
기본 정책 추가 시:

  «interface» RatePolicy
      │
  BasicRatePolicy ──────── AdditionalRatePolicy
  /      |        \          /              \
Regular  Nightly  FixedRate  Taxable  RateDiscountable
Policy   DP       Policy     Policy   Policy
```

더 중요한 것은 요구 사항을 변경할 때 **오직 하나의 클래스만 수정해도 된다**는 것이다. 세금 정책을 변경한다면, 세금 정책과 관련된 코드가 상속 계층 여기저기에 중복돼 있던 이전 설계에서는 한 번에 여러 클래스를 수정해야 한다. 합성 기반 설계에서는 오직 `TaxablePolicy` 클래스 하나만 변경하면 된다. 변경 후의 설계는 **단일 책임 원칙**을 준수하고 있는 것이다.

### 3.5 객체 합성이 클래스 상속보다 더 좋은 방법이다

객체지향에서 코드를 재사용하기 위해 가장 널리 사용되는 방법은 상속이다. 하지만 상속은 코드 재사용을 위한 우아한 해결책은 아니다. 상속은 부모 클래스의 세부적인 구현에 자식 클래스를 강하게 결합시키기 때문에 코드의 진화를 방해한다.

코드를 재사용하면서도 건전한 결합도를 유지할 수 있는 더 좋은 방법은 합성을 이용하는 것이다. 상속이 구현을 재사용하는 데 비해 **합성은 객체의 인터페이스를 재사용**한다.

그렇다면 상속은 사용해서는 안 되는 것인가? 이 의문에 대답하기 위해서는 먼저 상속을 **구현 상속**과 **인터페이스 상속**의 두 가지로 나눠야 한다는 사실을 이해해야 한다. 이번 장에서 살펴본 상속에 대한 모든 단점들은 **구현 상속에 국한**된다. 13장에서는 인터페이스 상속이 구현 상속과 어떤 면에서 다른지 살펴볼 것이다.

---

## 4. 믹스인

상속을 사용하면 다른 클래스를 간편하게 재사용하고 점진적으로 확장할 수 있지만, 부모 클래스와 자식 클래스가 강하게 결합되기 때문에 수정과 확장에 취약한 설계를 낳게 된다. 합성이 상속과 같은 문제점을 초래하지 않는 이유는 클래스의 구체적인 구현이 아니라 객체의 추상적인 인터페이스에 의존하기 때문이다.

**믹스인**(*Mixin - 객체를 생성할 때 코드 일부를 클래스 안에 섞어 넣어 재사용하는 기법*)은 합성처럼 유연하면서도 상속처럼 쉽게 코드를 재사용할 수 있는 방법이다. 합성이 실행 시점에 객체를 조합하는 재사용 방법이라면, 믹스인은 **컴파일 시점에 필요한 코드 조각을 조합**하는 재사용 방법이다.

상속과 믹스인은 유사해 보이지만 근본적으로 다르다:

| 비교 항목 | 상속 | 믹스인 |
|---|---|---|
| **목적** | is-a 관계를 만들기 위한 것 | 코드를 다른 코드 안에 섞어 넣기 위한 것 |
| **관계** | 클래스 사이의 관계를 고정시킴 | 유연하게 관계를 재구성할 수 있음 |
| **super 바인딩** | 컴파일 시점에 정적으로 결정 | 실행 시점에 동적으로 결정 |
| **문맥** | 재사용 가능한 문맥을 고정시킴 | 문맥을 확장 가능하도록 열어 놓음 |

### 4.1 스칼라 트레이트로 기본 정책 구현하기

스칼라의 트레이트(*Trait*)를 이용해 믹스인을 구현해 보자. 기본 정책을 구현하는 `BasicRatePolicy`는 추상 클래스로, `RegularPolicy`와 `NightlyDiscountPolicy`는 이를 상속받아 구현한다.

```scala
// Scala
abstract class BasicRatePolicy {
  def calculateFee(phone: Phone): Money =
    phone.calls.map(calculateCallFee(_)).reduce(_ + _)

  protected def calculateCallFee(call: Call): Money
}

class RegularPolicy(val amount: Money, val seconds: Duration) extends BasicRatePolicy {
  override protected def calculateCallFee(call: Call): Money =
    amount * (call.duration.getSeconds / seconds.getSeconds)
}

class NightlyDiscountPolicy(
    val nightlyAmount: Money,
    val regularAmount: Money,
    val seconds: Duration) extends BasicRatePolicy {
  override protected def calculateCallFee(call: Call): Money =
    if (call.from.getHour >= NightlyDiscountPolicy.LateNightHour)
      nightlyAmount * (call.duration.getSeconds / seconds.getSeconds)
    else
      regularAmount * (call.duration.getSeconds / seconds.getSeconds)
}

object NightlyDiscountPolicy {
  val LateNightHour: Integer = 22
}
```

### 4.2 트레이트로 부가 정책 구현하기

부가 정책을 트레이트로 구현한다. `TaxablePolicy` 트레이트가 `BasicRatePolicy`를 확장(extends)한다는 점에 주목하라. 이것은 상속의 개념이 아니라, **`TaxablePolicy`가 `BasicRatePolicy`나 그 자손에 해당하는 경우에만 믹스인될 수 있다**는 것을 의미한다.

```scala
// Scala
trait TaxablePolicy extends BasicRatePolicy {
  def taxRate: Double

  override def calculateFee(phone: Phone): Money = {
    val fee = super.calculateFee(phone)
    fee + fee * taxRate
  }
}

trait RateDiscountablePolicy extends BasicRatePolicy {
  val discountAmount: Money

  override def calculateFee(phone: Phone): Money = {
    val fee = super.calculateFee(phone)
    fee - discountAmount
  }
}
```

트레이트와 상속의 가장 큰 차이점은 다음과 같다. 상속은 부모 클래스와 자식 클래스의 관계를 코드를 작성하는 시점에 고정시키지만, **믹스인은 제약을 둘 뿐 실제로 어떤 코드에 믹스인될 것인지를 결정하지 않는다**. `TaxablePolicy` 트레이트는 어떤 코드에 믹스인될 것인가? 알 수 없다. 실제로 트레이트를 믹스인하는 시점에 가서야 믹스인할 대상을 결정할 수 있다.

또한 `super` 호출에서도 차이가 있다. 상속의 경우 일반적으로 `this` 참조는 동적으로 결정되지만 `super` 참조는 컴파일 시점에 결정된다. 하지만 스칼라의 트레이트에서 **`super` 참조는 동적으로 결정**된다. `TaxablePolicy` 트레이트를 `RegularPolicy`에 믹스인하면 `RegularPolicy`의 `calculateFee`가, `NightlyDiscountPolicy`에 믹스인하면 `NightlyDiscountPolicy`의 `calculateFee`가 호출된다. 이것이 트레이트를 사용한 믹스인이 클래스를 사용한 상속보다 더 유연한 재사용 기법인 이유다.

### 4.3 부가 정책 트레이트 믹스인하기

스칼라는 트레이트를 클래스나 다른 트레이트에 믹스인할 수 있도록 `extends`와 `with` 키워드를 제공한다. 부모 클래스는 `extends`를 이용해 상속받고, 트레이트는 `with`를 이용해 믹스인한다. 이를 **트레이트 조합**(*Trait Composition*)[Odersky11]이라고 부른다.

**일반 요금제 + 세금 정책:**

```scala
// Scala
class TaxableRegularPolicy(
    amount: Money,
    seconds: Duration,
    val taxRate: Double)
  extends RegularPolicy(amount, seconds)
  with TaxablePolicy
```

**심야 할인 요금제 + 기본 요금 할인 정책:**

```scala
// Scala
class RateDiscountableNightlyDiscountPolicy(
    nightlyAmount: Money,
    regularAmount: Money,
    seconds: Duration,
    val discountAmount: Money)
  extends NightlyDiscountPolicy(nightlyAmount, regularAmount, seconds)
  with RateDiscountablePolicy
```

### 4.4 선형화

스칼라는 특정 클래스에 믹스인한 클래스와 트레이트를 **선형화**(*Linearization*)해서 어떤 메서드를 호출할지 결정한다. 클래스의 인스턴스를 생성할 때, 스칼라는 클래스 자신과 조상 클래스, 트레이트를 일렬로 나열해서 순서를 정한다. 실행 중인 메서드 내부에서 `super` 호출을 하면 다음 단계에 위치한 클래스나 트레이트의 메서드가 호출된다.

선형화 규칙: 맨 앞에는 구현한 클래스 자기 자신이 위치하고, 그 다음부터는 오른쪽에 선언된 트레이트를 다음 자리에 위치시키고 왼쪽 방향으로 순서대로 쌓아 올린다.

```
TaxableRegularPolicy의 선형화:

  TaxableRegularPolicy → TaxablePolicy → RegularPolicy → BasicRatePolicy
         (자기 자신)      (with 트레이트)   (extends 클래스)    (조상 클래스)

calculateFee 호출 흐름:
  1. TaxableRegularPolicy에서 메서드 검색 → 없음
  2. TaxablePolicy에서 메서드 발견 → 실행
  3. super 호출 → RegularPolicy에서 검색 → 없음
  4. BasicRatePolicy의 calculateFee 실행 → 일반 요금제 계산
  5. 제어가 TaxablePolicy로 복귀 → 세금 부과 후 반환
```

**세금 정책 + 기본 요금 할인 정책 순서 조합:**

트레이트의 순서만 바꾸면 적용 순서를 변경할 수 있다.

```scala
// Scala - 세금 먼저, 할인 나중
class RateDiscountableAndTaxableRegularPolicy(
    amount: Money,
    seconds: Duration,
    val discountAmount: Money,
    val taxRate: Double)
  extends RegularPolicy(amount, seconds)
  with TaxablePolicy
  with RateDiscountablePolicy

// Scala - 할인 먼저, 세금 나중
class TaxableAndRateDiscountableRegularPolicy(
    amount: Money,
    seconds: Duration,
    val discountAmount: Money,
    val taxRate: Double)
  extends RegularPolicy(amount, seconds)
  with RateDiscountablePolicy
  with TaxablePolicy
```

클래스를 만들어야 하는 것이 불만이라면, 클래스를 만들지 않고 인스턴스를 생성할 때 트레이트를 믹스인할 수도 있다.

```scala
// Scala
new RegularPolicy(Money(100), Duration.ofSeconds(10))
  with RateDiscountablePolicy
  with TaxablePolicy {
  val discountAmount = Money(100)
  val taxRate = 0.02
}
```

### 4.5 쌓을 수 있는 변경

믹스인을 사용하면 특정한 클래스에 대한 변경 또는 확장을 독립적으로 구현한 후, 필요한 시점에 차례대로 추가할 수 있다. 마틴 오더스키(Martin Odersky)는 믹스인의 이러한 특징을 **쌓을 수 있는 변경**(*Stackable Modification*)이라고 부른다.

> 스칼라에서 트레이트는 코드 재사용의 근간을 이루는 단위다. 클래스와 트레이트의 또 다른 차이는 클래스에서는 super 호출을 정적으로 바인딩하지만, 트레이트에서는 동적으로 바인딩한다는 것이다. super가 이렇게 동작하기 때문에 트레이트를 이용해 변경 위에 변경을 쌓아 올리는 '쌓을 수 있는 변경'이 가능해진다[Odersky11].

> **핵심 통찰**: 클래스 폭발 문제의 진짜 단점은 클래스가 늘어난다는 것이 아니라, 클래스가 늘어날수록 **중복 코드도 함께 기하급수적으로 늘어난다**는 점이다. 믹스인에서는 이런 문제가 발생하지 않는다. 각 트레이트는 독립적으로 작성되며, 조합이 필요한 곳에서만 선택적으로 믹스인된다. 따라서 기능을 추가하더라도 중복 코드 없이 하나의 트레이트만 작성하면 된다.

---

## 설계 원칙

| 원칙 | 핵심 내용 | 효과 |
|---|---|---|
| **합성 우선** | 코드 재사용을 위해서는 클래스 상속보다 객체 합성을 사용하라[GOF94] | 구현 의존성을 인터페이스 의존성으로 대체, 낮은 결합도 |
| **인터페이스에 의존하라** | 합성하는 객체의 타입은 인터페이스나 추상 클래스로 선언하라 | 런타임에 동적으로 관계를 변경 가능 |
| **포워딩** | 기존 인터페이스를 유지하면서 구현 결합도를 제거하려면 포워딩 메서드를 사용하라 | 구현 결합 없이 인터페이스 재사용 |
| **단일 책임 원칙** | 하나의 정책 변경이 하나의 클래스 변경만을 요구하도록 설계하라 | 변경의 파급 효과 최소화 |
| **트레이드오프** | 유연성과 복잡성 사이의 균형을 찾아라 | 변경에 따르는 고통 > 복잡성으로 인한 혼란일 때 유연성 선택 |

---

## 요약

- **상속과 합성의 차이**: 상속은 부모 클래스의 구현(코드 자체)을 재사용하고 컴파일타임에 관계가 고정되지만, 합성은 포함된 객체의 퍼블릭 인터페이스를 재사용하고 런타임에 관계를 동적으로 변경할 수 있다.
- **상속의 세 가지 문제를 합성으로 해결**: 불필요한 인터페이스 상속(`Properties`, `Stack`), 메서드 오버라이딩의 오작용(`InstrumentedHashSet`), 부모-자식 동시 수정(`PersonalPlaylist`) 문제를 합성 관계로 전환하여 해결할 수 있다.
- **클래스 폭발 문제**: 상속을 이용해 기능을 조합하면 모든 가능한 조합별로 클래스를 추가해야 하며, 새로운 정책 추가 시 기하급수적으로 클래스가 늘어나고 중복 코드도 함께 증가한다.
- **합성으로 클래스 폭발 해결**: `RatePolicy` 인터페이스를 도입하고 기본 정책(`BasicRatePolicy`)과 부가 정책(`AdditionalRatePolicy`)을 분리하여, 런타임에 인스턴스를 조립하는 방식으로 유연하게 조합할 수 있다. 새로운 정책 추가 시 **클래스 하나만** 추가하면 된다.
- **포워딩**: 기존 클래스의 인터페이스를 그대로 외부에 제공하면서 구현에 대한 결합 없이 일부 작동 방식을 변경하고 싶은 경우에 사용하는 기법이다.
- **구현 상속 vs 인터페이스 상속**: 이 장에서 다룬 상속의 모든 단점은 구현 상속에 국한된다. 인터페이스 상속은 다른 특성을 가진다.
- **믹스인(Mixin)**: 컴파일 시점에 코드 조각을 조합하는 재사용 방법으로, 합성처럼 유연하면서도 상속처럼 쉽게 코드를 재사용할 수 있다. 스칼라의 트레이트가 대표적이다.
- **쌓을 수 있는 변경**: 트레이트의 `super` 참조가 동적으로 바인딩되기 때문에, 변경 위에 변경을 쌓아 올리는 방식으로 기능을 조합할 수 있다.

---

## 다른 챕터와의 관계

- **Chapter 8 (의존성 관리하기)**: 8장에서 다룬 컴파일타임 의존성과 런타임 의존성의 차이가 이 장의 핵심 토대다. 8장에서 "두 의존성의 거리가 멀수록 설계가 유연해진다"고 했던 원칙이 합성을 통해 구체적으로 실현된다. 의존성 주입을 통해 런타임에 객체를 설정하는 기법 역시 8장의 개념과 직접 연결된다.
- **Chapter 9 (유연한 설계)**: 9장에서 설명한 개방-폐쇄 원칙(OCP)이 합성 기반 설계에서 자연스럽게 달성된다. 새로운 정책을 추가할 때 기존 코드를 수정하지 않고 클래스 하나만 추가하면 되는 것은 OCP를 준수하는 대표적인 사례다. 또한 합성 기반 설계가 단일 책임 원칙을 준수한다는 점도 9장의 논의와 연결된다.
- **Chapter 10 (상속과 코드 재사용)**: 10장에서 제시한 상속의 세 가지 문제점(불필요한 인터페이스 상속, 메서드 오버라이딩 오작용, 부모-자식 동시 수정)을 이 장에서 합성으로 해결한다. 10장의 핸드폰 과금 시스템 예제가 이 장에서 합성과 믹스인을 이용한 설계로 재구성된다.
- **Chapter 13 (서브클래싱과 서브타이핑)**: 이 장에서 언급된 구현 상속과 인터페이스 상속의 구분이 13장에서 본격적으로 다뤄진다. 이 장의 모든 단점이 구현 상속에 국한된다는 주장의 근거를 13장에서 확인할 수 있다.
