# Chapter 8: 어떻게 기능을 추가할까? (How Do I Add a Feature?)

## 핵심 질문

레거시 코드에 새로운 기능을 추가할 때, TDD를 어떻게 적용할 수 있으며, 기존 코드를 최소한으로 변경하면서 새 동작을 안전하게 추가하는 방법은 무엇인가?

---

## 1. 레거시 코드에서 기능 추가의 어려움

새 기능을 추가하는 것은 소프트웨어 개발에서 가장 기본적인 활동이지만, 레거시 코드에서는 유난히 어렵다. 그 이유는:

1. **기존 코드를 충분히 이해하지 못한 상태**에서 변경해야 한다.
2. 변경이 **기존 동작을 깨뜨리지 않는다는 확신**이 없다.
3. 어디에 새 코드를 **어떤 방식으로 배치해야 하는지** 판단하기 어렵다.

Feathers는 이 장에서 두 가지 핵심 기법을 소개한다:
- **TDD (Test-Driven Development)**: 테스트가 설계를 이끌게 하는 개발 방식
- **Programming by Difference**: 상속을 이용해 기존 코드를 건드리지 않고 새 동작을 추가하는 기법

---

## 2. TDD (Test-Driven Development)

### 2.1 TDD의 기본 사이클

TDD는 **Red-Green-Refactor**라는 세 단계의 반복 사이클로 이루어진다:

```
┌──────────────────────────────────────┐
│  1. Red: 실패하는 테스트를 작성한다    │
│          ↓                           │
│  2. Green: 테스트를 통과시킨다         │
│          ↓                           │
│  3. Refactor: 코드를 정리한다         │
│          ↓                           │
│  (다시 1번으로)                       │
└──────────────────────────────────────┘
```

**1단계 - Red: 실패하는 테스트 작성**

새로 추가할 기능의 동작을 **테스트로 먼저 표현**한다. 이 시점에서 테스트는 당연히 실패한다 (아직 구현이 없으므로).

```java
// 아직 구현이 없는 상태에서 테스트를 먼저 작성
public void testAddSetsReadyIndicator() {
    InvoiceUpdateResponder responder = new InvoiceUpdateResponder(new FakeInvoiceSource());
    responder.add(new Invoice(/* ... */));
    assertTrue(responder.isReady());  // 실패! isReady()가 아직 없음
}
```

**2단계 - Green: 테스트를 통과시키기**

테스트를 통과시키기 위한 **최소한의 코드**를 작성한다. 이 단계에서는 코드의 우아함이나 완결성보다 **테스트 통과**가 최우선이다.

```java
public class InvoiceUpdateResponder {
    private boolean ready = false;

    public void add(Invoice invoice) {
        // 최소한의 구현
        ready = true;
    }

    public boolean isReady() {
        return ready;
    }
}
```

**3단계 - Refactor: 코드 정리**

테스트가 통과하는 상태를 유지하면서, 코드의 **구조를 개선**한다. 중복을 제거하고, 이름을 명확하게 하며, 책임을 적절히 분배한다.

### 2.2 레거시 코드에서의 TDD 적용

그린필드(greenfield) 프로젝트에서의 TDD와 레거시 코드에서의 TDD는 차이가 있다:

| 측면 | 그린필드 TDD | 레거시 코드 TDD |
|------|-------------|----------------|
| **시작점** | 빈 클래스부터 시작 | 기존 코드 사이에 끼워넣기 |
| **테스트 대상** | 새로 만드는 모든 코드 | 새로 추가하는 코드 + 변경하는 코드 |
| **가짜 객체** | 설계부터 테스트를 고려 | 기존 의존성을 끊기 위해 사용 |
| **리팩토링** | 자유롭게 가능 | 기존 테스트 범위 내에서만 안전 |

레거시 코드에서 TDD를 적용할 때는:
1. 먼저 **변경할 부분 주변에 테스트를 추가**한다 (Chapter 13의 characterization test).
2. 새 기능에 대한 **실패하는 테스트를 작성**한다.
3. 테스트를 **통과시키는 코드를 구현**한다.
4. **안전하게 리팩토링**한다.

### 2.3 TDD가 레거시 코드에서 특히 유용한 이유

> TDD는 단순히 테스트를 먼저 작성하는 것이 아니다. 코드의 설계를 테스트가 이끌게 하는 것이다.

레거시 코드에서 TDD를 적용하면:

- 새 기능의 **인터페이스를 먼저 생각**하게 된다 (테스트를 작성하려면 호출 방법을 결정해야 하므로).
- 자연스럽게 **테스트 가능한 설계**가 나온다.
- 새 코드가 **즉시 테스트 범위에 포함**된다.
- 작은 단위로 **피드백을 받으면서** 개발할 수 있다.

---

## 3. Programming by Difference (차이에 의한 프로그래밍)

### 3.1 개념

Programming by Difference는 **상속을 이용해 기존 클래스의 동작을 변경**하는 기법이다. 기존 클래스를 수정하는 대신, **새로운 서브클래스를 만들어 필요한 메서드만 오버라이드**한다.

핵심 아이디어: 기존 코드와 새 코드의 **"차이(difference)"** 만 서브클래스에 표현한다.

### 3.2 예시

온라인 쇼핑몰의 `MailForwarder` 클래스가 있다. 이 클래스는 메일링 리스트에 메일을 전달하는 역할을 한다:

```java
public class MailForwarder {
    private Domain domain;
    private Destination destination;

    public MailForwarder(Domain domain, Destination destination) {
        this.domain = domain;
        this.destination = destination;
    }

    public void forwardMessage(Message message) {
        if (message.getFrom().endsWith(domain.getName())) {
            destination.forward(message);
        }
    }
}
```

새로운 요구사항: **익명 메시지도 전달할 수 있어야 한다.** 익명 메시지는 발신자 정보를 제거한 후 전달한다.

**기존 코드를 직접 수정하는 방식 (위험):**

```java
// 나쁜 예: 기존 메서드에 조건문 추가
public void forwardMessage(Message message) {
    if (anonymous) {
        message.setFrom("anonymous");  // 기존 동작과 새 동작이 뒤섞임
    }
    if (message.getFrom().endsWith(domain.getName())) {
        destination.forward(message);
    }
}
```

**Programming by Difference 방식 (안전):**

```java
// 서브클래스: 차이점만 표현
public class AnonymousMailForwarder extends MailForwarder {

    public AnonymousMailForwarder(Domain domain, Destination destination) {
        super(domain, destination);
    }

    @Override
    public void forwardMessage(Message message) {
        // 차이점: 발신자 정보를 익명으로 변경
        Message anonymousMessage = new Message(message);
        anonymousMessage.setFrom("anonymous");
        super.forwardMessage(anonymousMessage);
    }
}
```

이제 `AnonymousMailForwarder`를 **독립적으로 테스트**할 수 있다:

```java
public void testAnonymousForward() {
    Domain domain = new Domain("example.com");
    TestingDestination destination = new TestingDestination();
    AnonymousMailForwarder forwarder =
        new AnonymousMailForwarder(domain, destination);

    Message message = new Message();
    message.setFrom("user@example.com");
    message.setBody("Hello");

    forwarder.forwardMessage(message);

    assertEquals("anonymous", destination.getLastMessage().getFrom());
    assertEquals("Hello", destination.getLastMessage().getBody());
}
```

### 3.3 Programming by Difference의 장점

1. **기존 코드를 전혀 수정하지 않는다** → 기존 동작 보존이 확실하다.
2. **새 코드만 테스트하면 된다** → 테스트 범위가 명확하다.
3. **차이점이 코드에서 명시적으로 드러난다** → 무엇이 바뀌었는지 한눈에 보인다.
4. **원래 클래스로 쉽게 되돌릴 수 있다** → 서브클래스만 제거하면 된다.

### 3.4 주의: 이것은 최종 설계가 아니다

Feathers는 Programming by Difference가 **임시적인 기법**임을 강조한다:

> Programming by Difference는 기존 코드를 안전하게 변경하기 위한 첫 번째 단계이다. 최종 목적지가 아니라 경유지이다.

상속을 남용하면 다음과 같은 문제가 발생한다:

- **상속 계층이 깊어지면** 코드를 이해하기 어려워진다.
- **서브클래스가 부모 클래스의 내부 구현에 의존**하면, 부모 클래스를 변경하기 어려워진다.
- **is-a 관계가 아닌 곳에 상속을 사용**하면 설계가 혼란스러워진다.

따라서 Programming by Difference로 기능을 추가한 후, 테스트가 갖춰지면 **리팩토링을 통해 더 나은 설계로 개선**해야 한다:

```
1단계: 기존 코드에 대한 테스트 확보
2단계: Programming by Difference로 새 기능 추가
3단계: 새 기능에 대한 테스트 확보
4단계: 리팩토링 (상속 → 조합, 전략 패턴 등으로 전환)
```

예를 들어, `AnonymousMailForwarder`를 나중에 **전략 패턴**으로 리팩토링할 수 있다:

```java
// 리팩토링 후: 전략 패턴
public interface MessageProcessor {
    Message process(Message message);
}

public class AnonymizingProcessor implements MessageProcessor {
    public Message process(Message message) {
        Message result = new Message(message);
        result.setFrom("anonymous");
        return result;
    }
}

public class MailForwarder {
    private MessageProcessor processor;

    public MailForwarder(Domain domain, Destination destination,
                         MessageProcessor processor) {
        this.domain = domain;
        this.destination = destination;
        this.processor = processor;
    }

    public void forwardMessage(Message message) {
        Message processed = processor.process(message);
        if (processed.getFrom().endsWith(domain.getName())) {
            destination.forward(processed);
        }
    }
}
```

---

## 4. Liskov Substitution Principle (LSP)

### 4.1 원칙의 정의

Programming by Difference를 적용할 때 반드시 지켜야 하는 원칙이 **리스코프 치환 원칙(LSP)** 이다:

> 서브타입(subtype)은 그것의 기반 타입(base type)을 대체할 수 있어야 한다. 즉, 부모 클래스를 사용하는 모든 곳에서 서브클래스를 넣어도 프로그램의 정확성이 깨져서는 안 된다.

### 4.2 LSP 위반 예시

```java
public class Rectangle {
    protected int width;
    protected int height;

    public void setWidth(int w) { width = w; }
    public void setHeight(int h) { height = h; }
    public int getArea() { return width * height; }
}

public class Square extends Rectangle {
    @Override
    public void setWidth(int w) {
        width = w;
        height = w;  // 정사각형이므로 높이도 함께 변경
    }

    @Override
    public void setHeight(int h) {
        width = h;  // 정사각형이므로 너비도 함께 변경
        height = h;
    }
}
```

이 코드는 LSP를 위반한다:

```java
// Rectangle을 기대하는 코드
public void testArea(Rectangle rect) {
    rect.setWidth(5);
    rect.setHeight(4);
    assertEquals(20, rect.getArea());  // Square를 넣으면 실패! (4*4 = 16)
}
```

`Square`를 `Rectangle` 자리에 넣으면 프로그램의 정확성이 깨진다. 이것이 LSP 위반이다.

### 4.3 Programming by Difference와 LSP

Programming by Difference로 서브클래스를 만들 때, LSP를 위반하지 않도록 주의해야 한다:

**안전한 경우:**
- 서브클래스가 **새로운 기능을 추가**만 하는 경우
- 서브클래스가 부모의 메서드를 호출한 후 **추가 동작을 수행**하는 경우 (앞의 `AnonymousMailForwarder` 예시처럼)

**위험한 경우:**
- 서브클래스가 부모의 메서드를 **완전히 다른 동작으로 대체**하는 경우
- 서브클래스가 부모의 **불변식(invariant)을 깨뜨리는** 경우
- 서브클래스가 부모의 **사전조건을 강화하거나 사후조건을 약화**하는 경우

---

## 5. 정규화된 상속 계층 (Normalized Hierarchy)

### 5.1 개념

Feathers는 **정규화된 상속 계층(Normalized Hierarchy)** 이라는 개념을 제시한다:

> 정규화된 상속 계층에서는, 어떤 비추상(concrete) 메서드도 그 계층 내에서 오버라이드되지 않는다.

즉, 메서드가 구체적인 구현을 가지고 있다면(비추상), 서브클래스에서 그것을 다시 오버라이드하지 않는다. 오버라이드가 필요한 동작은 **추상 메서드**로 선언한다.

### 5.2 왜 정규화된 계층이 좋은가

```java
// 정규화되지 않은 계층 (나쁜 예)
public class Animal {
    public String makeSound() {
        return "...";  // 구체적 구현이 있지만, 서브클래스에서 오버라이드됨
    }
}

public class Dog extends Animal {
    @Override
    public String makeSound() {
        return "Woof";  // 부모의 구현을 완전히 무시
    }
}

public class Cat extends Animal {
    @Override
    public String makeSound() {
        return "Meow";  // 부모의 구현을 완전히 무시
    }
}
```

```java
// 정규화된 계층 (좋은 예)
public abstract class Animal {
    public abstract String makeSound();  // 추상 메서드: 오버라이드가 명시적
}

public class Dog extends Animal {
    @Override
    public String makeSound() {
        return "Woof";
    }
}

public class Cat extends Animal {
    @Override
    public String makeSound() {
        return "Meow";
    }
}
```

정규화된 계층의 장점:

1. **메서드의 역할이 명확**하다: 추상 메서드 = "서브클래스마다 다를 수 있음", 구체 메서드 = "모든 서브클래스에서 동일함".
2. **어떤 메서드를 봐야 하는지 쉽게 판단**할 수 있다: 구체 메서드는 부모 클래스에서 한 번만 보면 된다.
3. **LSP 위반의 가능성이 줄어든다**: 구체 메서드를 오버라이드하면서 의미를 바꾸는 실수를 방지한다.

### 5.3 Programming by Difference에서 정규화로의 여정

Programming by Difference로 시작하면 처음에는 **정규화되지 않은 계층**이 만들어질 수 있다. 하지만 테스트가 갖춰진 후 리팩토링을 통해 점진적으로 **정규화된 계층**으로 발전시킬 수 있다:

```
1. Programming by Difference → 구체 메서드를 오버라이드하는 서브클래스 생성
2. 테스트 확보
3. 리팩토링: 오버라이드되는 메서드를 추상 메서드로 전환
4. 기존 부모 클래스의 구현을 별도 서브클래스로 이동
5. 정규화된 상속 계층 완성
```

---

## 6. TDD와 Programming by Difference의 결합

실제 작업에서는 TDD와 Programming by Difference를 **함께 사용**하는 경우가 많다:

```
1. 기존 클래스의 동작을 확인하는 특성화 테스트(characterization test) 작성
2. 새 기능에 대한 실패하는 테스트 작성 (Red)
3. Programming by Difference로 서브클래스를 만들어 테스트 통과 (Green)
4. 코드 정리 및 설계 개선 (Refactor)
5. 필요하다면 상속을 조합(composition)으로 전환
```

이 접근의 핵심 가치:
- **매 단계마다 테스트가 보호막 역할**을 한다.
- 기존 코드는 **안전하게 보존**된다.
- 새 코드는 **처음부터 테스트와 함께** 작성된다.
- 설계 개선은 **테스트가 뒷받침하는 상태에서** 진행된다.

---

## 요약

- **TDD (Test-Driven Development)** 는 Red-Green-Refactor 사이클로, 테스트가 설계를 이끄는 개발 방식이다.
- 레거시 코드에서도 TDD를 적용할 수 있으며, 새로 추가하는 코드에 대해 특히 효과적이다.
- **Programming by Difference**는 상속을 이용해 기존 클래스를 수정하지 않고, 서브클래스에서 차이점만 표현하여 새 기능을 추가하는 기법이다.
- Programming by Difference는 **임시적 기법**이며, 테스트가 갖춰진 후 리팩토링으로 더 나은 설계로 개선해야 한다.
- **Liskov Substitution Principle (LSP)** 을 지켜야 서브클래스가 부모 클래스를 안전하게 대체할 수 있다.
- **정규화된 상속 계층**에서는 비추상 메서드가 오버라이드되지 않아, 코드 이해와 유지보수가 쉬워진다.
- TDD와 Programming by Difference를 결합하면, 기존 코드를 보존하면서 안전하게 새 기능을 추가할 수 있다.

---

## 다음 챕터와의 연결

Chapter 9 **"뚝딱! 테스트 하네스에 클래스 제대로 넣기 (I Can't Get This Class into a Test Harness)"** 에서는 생성자가 복잡하거나, 숨겨진 의존성이 있거나, 싱글톤에 의존하는 등 클래스를 테스트 환경에서 인스턴스화하기 어려운 구체적인 문제들과 그 해결 기법을 상세히 소개한다.
