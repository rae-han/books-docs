# Chapter 14: 나를 미치게 하는 라이브러리 의존 관계 (Dependencies on Libraries Are Killing Me)

## 핵심 질문

라이브러리에 대한 의존성이 왜 코드의 테스트 가능성과 유연성을 해치며, 이를 어떻게 관리해야 하는가?

---

## 1. 라이브러리 의존성의 함정

소프트웨어 개발에서 라이브러리는 필수적이다. 직접 모든 것을 구현하는 것은 비현실적이며, 잘 만들어진 라이브러리를 활용하는 것은 당연히 올바른 접근이다. 그러나 **라이브러리를 사용하는 방식**에 따라 코드의 테스트 가능성과 유연성이 크게 달라진다.

### 1.1 라이브러리와 프레임워크의 차이

라이브러리와 프레임워크는 서로 다른 수준의 결합을 요구한다:

| 구분 | 라이브러리 (Library) | 프레임워크 (Framework) |
|------|---------------------|----------------------|
| **제어 흐름** | 내 코드가 라이브러리를 호출한다 | 프레임워크가 내 코드를 호출한다 |
| **결합도** | 상대적으로 느슨할 수 있다 | 본질적으로 강하다 |
| **교체 난이도** | 래핑으로 교체 가능하다 | 교체가 매우 어렵다 |

프레임워크의 경우, 제어의 역전(Inversion of Control) 때문에 코드가 프레임워크의 구조에 깊이 종속된다. 이것은 프레임워크 선택 시 신중해야 하는 이유이기도 하다. 하지만 이 장에서 주로 다루는 것은 **라이브러리 수준의 의존성**이며, 이 수준에서는 적절한 추상화로 문제를 해결할 수 있다.

### 1.2 문제가 되는 의존성 패턴

라이브러리 의존성이 테스트를 어렵게 만드는 대표적인 패턴들이 있다:

**1) Concrete 클래스에 직접 의존**

```java
// 문제: 라이브러리의 구체 클래스를 직접 사용
public class OrderProcessor {
    public void processOrder(Order order) {
        HttpClient client = new HttpClient();  // 직접 생성
        client.post("https://payment.example.com/charge", order.toJson());

        MailSender sender = new MailSender();  // 직접 생성
        sender.send(order.getCustomerEmail(), "주문이 처리되었습니다.");
    }
}
```

이 코드에서 `HttpClient`와 `MailSender`는 라이브러리가 제공하는 구체 클래스다. 테스트 시 실제 HTTP 요청을 보내고, 실제 이메일을 발송하게 된다. 이를 대체할 방법이 없다.

**2) 라이브러리 클래스를 직접 상속**

```java
// 문제: 라이브러리 클래스를 직접 상속
public class CustomList extends ThirdPartyList {
    // ThirdPartyList의 모든 동작에 종속됨
    // ThirdPartyList가 변경되면 이 클래스도 영향을 받음
}
```

라이브러리 클래스를 상속하면, 라이브러리의 내부 구현에 종속된다. 라이브러리가 업그레이드될 때 예기치 않은 문제가 발생할 수 있다.

**3) Final/Sealed 클래스와 Static 메서드**

```java
// 문제: final 클래스는 상속할 수 없다
public final class ThirdPartyService {
    public Result doSomething(Input input) { ... }
}

// 문제: static 메서드는 오버라이드할 수 없다
public class ThirdPartyUtil {
    public static String format(String input) { ... }
}
```

많은 라이브러리 클래스가 `final`(Java) 또는 `sealed`(C#)로 선언되어 있어 상속을 통한 테스트 대체가 불가능하다. Static 메서드도 마찬가지로 오버라이드할 수 없어 테스트 시 대체할 방법이 없다.

---

## 2. 핵심 원칙: 한 단계 감싸라 (Wrap)

Feathers가 제시하는 핵심 해결 원칙은 명쾌하다:

> **라이브러리를 코드에 직접 뿌리지 말라. 한 단계 감싸서 사용하라.**

이것은 단순하지만 매우 강력한 원칙이다. 라이브러리와 애플리케이션 코드 사이에 얇은 추상화 계층을 두면, 라이브러리에 대한 직접적인 의존성을 제거할 수 있다.

### 2.1 래핑의 기본 구조

```java
// 1단계: 인터페이스 정의 (내가 소유하는 추상화)
public interface PaymentGateway {
    PaymentResult charge(String customerId, Money amount);
}

// 2단계: 라이브러리를 감싸는 구현체
public class StripePaymentGateway implements PaymentGateway {
    private StripeClient stripeClient;  // 라이브러리 클래스

    public PaymentResult charge(String customerId, Money amount) {
        // Stripe 라이브러리의 API를 호출
        StripeCharge charge = stripeClient.charges().create(
            new ChargeParams(customerId, amount.toCents())
        );
        return new PaymentResult(charge.getId(), charge.getStatus());
    }
}

// 3단계: 비즈니스 코드는 인터페이스에만 의존
public class OrderProcessor {
    private PaymentGateway paymentGateway;  // 인터페이스에 의존

    public OrderProcessor(PaymentGateway paymentGateway) {
        this.paymentGateway = paymentGateway;
    }

    public void processOrder(Order order) {
        PaymentResult result = paymentGateway.charge(
            order.getCustomerId(), order.getTotal()
        );
        // ...
    }
}
```

### 2.2 테스트에서의 활용

래핑 후에는 테스트에서 가짜 구현을 쉽게 주입할 수 있다:

```java
// 테스트용 가짜 구현
public class FakePaymentGateway implements PaymentGateway {
    private boolean shouldSucceed = true;
    private List<ChargeRecord> charges = new ArrayList<>();

    public PaymentResult charge(String customerId, Money amount) {
        charges.add(new ChargeRecord(customerId, amount));
        if (shouldSucceed) {
            return new PaymentResult("fake-id", "SUCCESS");
        }
        return new PaymentResult(null, "FAILED");
    }

    // 테스트 검증용 메서드
    public List<ChargeRecord> getCharges() { return charges; }
    public void setShouldSucceed(boolean value) { shouldSucceed = value; }
}

// 테스트 코드
@Test
public void processOrder_chargesCorrectAmount() {
    FakePaymentGateway gateway = new FakePaymentGateway();
    OrderProcessor processor = new OrderProcessor(gateway);

    Order order = new Order("customer-1", Money.of(100));
    processor.processOrder(order);

    assertEquals(1, gateway.getCharges().size());
    assertEquals(Money.of(100), gateway.getCharges().get(0).getAmount());
}
```

---

## 3. 라이브러리 추상화 전략

### 3.1 어떤 라이브러리를 감싸야 하는가?

모든 라이브러리를 무조건 감쌀 필요는 없다. 감싸야 할 라이브러리를 판단하는 기준:

| 기준 | 감싸야 하는 경우 | 감싸지 않아도 되는 경우 |
|------|----------------|---------------------|
| **변경 가능성** | 라이브러리를 교체할 가능성이 있음 | 언어의 표준 라이브러리처럼 안정적 |
| **테스트 영향** | 라이브러리 호출이 테스트를 느리게 하거나 불가능하게 함 | 순수 계산 라이브러리 (예: 수학 라이브러리) |
| **사용 범위** | 코드베이스 전반에 걸쳐 광범위하게 사용됨 | 한두 곳에서만 사용됨 |
| **부수 효과** | I/O, 네트워크, DB 등 부수 효과가 있음 | 부수 효과 없이 값만 반환함 |

> **실용적 지침**: 외부 세계와 통신하는 라이브러리(HTTP, DB, 파일시스템, 메시지 큐 등)는 반드시 감싸라. 순수 유틸리티 라이브러리(문자열 처리, 수학 연산 등)는 직접 사용해도 무방하다.

### 3.2 얇은 래퍼(Thin Wrapper) 전략

래퍼는 가능한 한 **얇아야(thin)** 한다. 래퍼에 비즈니스 로직을 넣으면 안 된다:

```java
// 좋은 예: 얇은 래퍼 - 단순히 위임만 한다
public class EmailService implements Mailer {
    private SendGridClient client;

    public void send(String to, String subject, String body) {
        SendGridMessage msg = new SendGridMessage();
        msg.setTo(to);
        msg.setSubject(subject);
        msg.setBody(body);
        client.send(msg);
    }
}

// 나쁜 예: 두꺼운 래퍼 - 비즈니스 로직이 섞여 있다
public class EmailService implements Mailer {
    private SendGridClient client;

    public void send(String to, String subject, String body) {
        // 비즈니스 로직이 래퍼에 들어가면 안 된다!
        if (isBusinessHours()) {
            SendGridMessage msg = new SendGridMessage();
            msg.setTo(to);
            msg.setSubject("[긴급] " + subject);
            msg.setBody(addFooter(body));
            client.send(msg);
        } else {
            queueForLater(to, subject, body);
        }
    }
}
```

래퍼가 두꺼워지면 래퍼 자체를 테스트해야 하는 문제가 생기고, 라이브러리와 비즈니스 로직이 다시 결합된다.

### 3.3 내 용어로 된 인터페이스 (Interface in My Terms)

래핑할 때 중요한 점은, 인터페이스를 **라이브러리의 용어가 아닌 내 애플리케이션의 용어**로 정의하는 것이다:

```java
// 나쁜 예: 라이브러리의 용어를 그대로 사용
public interface AwsS3Wrapper {
    void putObject(String bucket, String key, InputStream stream);
    S3Object getObject(String bucket, String key);
}

// 좋은 예: 내 도메인의 용어로 정의
public interface DocumentStorage {
    void store(DocumentId id, Document document);
    Document retrieve(DocumentId id);
}
```

이렇게 하면 인터페이스가 특정 라이브러리에 종속되지 않으며, 나중에 S3에서 GCS로, 또는 로컬 파일시스템으로 교체할 때 인터페이스 자체는 변경할 필요가 없다.

---

## 4. "소유하지 않은 코드를 Mock하지 말라" 원칙과의 연관

이 장의 내용은 "Don't Mock What You Don't Own"이라는 널리 알려진 테스트 원칙과 직접적으로 연결된다.

### 4.1 왜 소유하지 않은 코드를 직접 Mock하면 안 되는가?

```java
// 나쁜 예: 라이브러리 클래스를 직접 Mock
@Test
public void testOrderProcessing() {
    // 라이브러리의 내부 API에 직접 의존하는 Mock
    HttpClient mockClient = mock(HttpClient.class);
    when(mockClient.post(any(), any()))
        .thenReturn(new HttpResponse(200, "{\"status\":\"ok\"}"));

    // 이 테스트는 라이브러리의 API가 변경되면 깨진다
    // 실제 HTTP 동작과 Mock의 동작이 다를 수 있다
}
```

소유하지 않은 코드를 직접 Mock하면 다음과 같은 문제가 발생한다:

1. **라이브러리의 API 변경에 취약하다**: 라이브러리가 업그레이드되면 Mock의 설정도 함께 변경해야 한다.
2. **라이브러리의 실제 동작을 정확히 모방하기 어렵다**: Mock은 우리가 예상하는 동작만 흉내 내지만, 실제 라이브러리는 더 복잡한 동작(에러 처리, 재시도, 커넥션 풀링 등)을 수행한다.
3. **테스트가 구현 세부사항에 결합된다**: 라이브러리의 어떤 메서드가 어떤 순서로 호출되는지를 검증하게 되면, 코드의 동작이 아닌 구현을 테스트하는 것이 된다.

### 4.2 래핑이 이 문제를 해결하는 방법

래퍼를 도입하면 이 원칙을 자연스럽게 따를 수 있다:

```
[직접 Mock - 나쁜 방식]
비즈니스 코드 → Mock(라이브러리 클래스)
                ↑ 소유하지 않은 코드를 Mock

[래핑 후 Mock - 좋은 방식]
비즈니스 코드 → Mock(내 인터페이스) ← 내가 소유하는 추상화
실제 구현    → 래퍼 → 라이브러리 클래스
```

내가 정의한 인터페이스를 Mock하는 것은 안전하다. 인터페이스의 계약(contract)을 내가 정의했으므로, 내가 완전히 이해하고 통제할 수 있기 때문이다.

---

## 5. 실전 적용 시 고려사항

### 5.1 기존 코드에 래퍼를 도입하는 순서

레거시 코드에 이미 라이브러리가 직접 사용되고 있는 경우, 다음 순서로 래퍼를 도입한다:

1. **인터페이스를 정의**한다 (내 도메인 용어로).
2. 라이브러리를 감싸는 **구현 클래스를 작성**한다.
3. 기존 코드에서 라이브러리를 직접 사용하는 부분을 찾아 **인터페이스를 사용하도록 변경**한다.
4. 생성자나 세터를 통해 **의존성을 주입**받도록 한다.
5. 테스트에서 **가짜 구현을 주입**하여 테스트를 작성한다.

### 5.2 라이브러리 업그레이드에 대한 방어

래핑의 부수적인 이점으로, 라이브러리 업그레이드가 훨씬 안전해진다:

```
[래퍼 없이 라이브러리 업그레이드]
라이브러리 v1 → v2로 변경 시:
  - 코드베이스 전체에서 변경된 API를 사용하는 모든 곳을 수정해야 함
  - 변경 범위가 광범위하여 위험도가 높음

[래퍼가 있을 때 라이브러리 업그레이드]
라이브러리 v1 → v2로 변경 시:
  - 래퍼 클래스 하나만 수정하면 됨
  - 인터페이스는 변경하지 않으므로 비즈니스 코드는 영향 없음
  - 변경 범위가 좁아 위험도가 낮음
```

---

## 요약

- 라이브러리는 필수적이지만, **직접적으로 결합하면** 테스트 가능성과 유연성이 크게 떨어진다.
- Concrete 클래스에 직접 의존, 라이브러리 클래스 상속, final/sealed 클래스, static 메서드 등이 대표적인 문제 패턴이다.
- 핵심 해결 원칙: **라이브러리를 직접 사용하지 말고 한 단계 감싸라 (Wrap)**.
- 래퍼는 **얇게(thin)** 유지하고, **내 도메인의 용어**로 인터페이스를 정의해야 한다.
- 이 원칙은 **"소유하지 않은 코드를 Mock하지 말라"** 는 테스트 원칙과 직접 연결된다.
- 래핑은 테스트 가능성뿐 아니라, 라이브러리 **교체와 업그레이드**에 대한 방어력도 제공한다.
- 모든 라이브러리를 무조건 감쌀 필요는 없다. 외부 세계와 통신하거나, 부수 효과가 있는 라이브러리를 우선적으로 감싸라.

---

## 다음 챕터와의 연결

Chapter 15 "애플리케이션에 API 호출이 너무 많다 (My Application Is All API Calls)"에서는 라이브러리 의존성 문제의 극단적인 형태를 다룬다. 애플리케이션 전체가 API 호출로만 구성되어 있고, 자체적인 도메인 모델이 없는 경우에 어떻게 책임 기반 설계로 전환하여 테스트 가능한 구조를 만들 수 있는지를 구체적인 예시와 함께 살펴본다.
