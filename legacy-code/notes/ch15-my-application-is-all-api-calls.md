# Chapter 15: 애플리케이션에 API 호출이 너무 많다 (My Application Is All API Calls)

## 핵심 질문

애플리케이션이 API 호출로만 구성되어 있고 자체적인 도메인 모델이 없을 때, 어떻게 테스트 가능하고 유지보수 가능한 구조로 전환할 수 있는가?

---

## 1. API 호출로만 구성된 애플리케이션의 문제

많은 시스템, 특히 오래된 시스템에서 볼 수 있는 패턴이 있다. 코드가 거의 전적으로 라이브러리나 플랫폼 API 호출의 나열로 이루어져 있는 것이다. 이런 코드에는 자체적인 도메인 모델이 없고, 비즈니스 로직이 API 호출 사이사이에 흩어져 있다.

### 1.1 전형적인 문제 코드

Feathers는 메일링 리스트 서버를 예로 든다. 다음은 이 패턴의 전형적인 모습이다:

```java
// 전형적인 "API 호출로만 구성된" 코드
public class MailingListServer {
    public void processMessage(Socket socket) {
        InputStreamReader isr = new InputStreamReader(socket.getInputStream());
        BufferedReader reader = new BufferedReader(isr);

        String message = "";
        String line;
        while ((line = reader.readLine()) != null) {
            message += line;
        }

        // 비즈니스 로직이 API 호출 사이에 흩어져 있다
        if (message.indexOf("SUBSCRIBE") != -1) {
            String address = message.substring(message.indexOf(":") + 1);
            // DB API 호출
            Connection conn = DriverManager.getConnection(dbUrl);
            PreparedStatement stmt = conn.prepareStatement(
                "INSERT INTO subscribers (address) VALUES (?)"
            );
            stmt.setString(1, address);
            stmt.executeUpdate();
            stmt.close();
            conn.close();

            // 메일 API 호출
            SMTPMessage response = new SMTPMessage();
            response.setFrom("list@example.com");
            response.setTo(address);
            response.setSubject("구독 확인");
            response.setBody("메일링 리스트에 구독되었습니다.");
            response.send();
        } else if (message.indexOf("UNSUBSCRIBE") != -1) {
            // 비슷한 패턴이 반복...
            String address = message.substring(message.indexOf(":") + 1);
            Connection conn = DriverManager.getConnection(dbUrl);
            PreparedStatement stmt = conn.prepareStatement(
                "DELETE FROM subscribers WHERE address = ?"
            );
            stmt.setString(1, address);
            stmt.executeUpdate();
            stmt.close();
            conn.close();
        }
        socket.close();
    }
}
```

### 1.2 이 코드의 문제점

이 코드의 문제를 분석하면 다음과 같다:

| 문제 | 설명 |
|------|------|
| **테스트 불가능** | Socket, DB, SMTP 등 외부 시스템에 직접 의존하여 단위 테스트 작성이 불가능하다 |
| **비즈니스 로직의 분산** | "구독 처리"라는 비즈니스 로직이 소켓 읽기, 문자열 파싱, DB 쿼리, 메일 전송 등 저수준 API 호출 사이에 흩어져 있다 |
| **도메인 모델 부재** | Subscriber, MailingList, Message 같은 도메인 개념이 코드에 표현되지 않는다 |
| **중복** | 구독/구독 해제 로직에서 DB 연결, 리소스 정리 등의 코드가 반복된다 |
| **변경의 어려움** | DB를 변경하거나, 메일 전송 방식을 바꾸거나, 새로운 명령어를 추가할 때 기존 코드 전체를 수정해야 한다 |

> **핵심 문제**: 이런 코드에는 "나의 코드"가 없다. 모든 것이 다른 사람의 API 호출이다. 코드를 읽어도 비즈니스 의도를 파악하기 어렵고, 테스트할 "나의 로직"이 분리되어 있지 않다.

---

## 2. 해결 전략 1: Skin and Wrap the API

첫 번째 전략은 **API를 감싸고(Wrap) 그 위에 추상화 계층을 구축(Skin)** 하는 것이다.

### 2.1 기본 개념

이 전략은 다음 단계로 진행된다:

1. 사용하는 API에 대한 **얇은 래퍼(thin wrapper)** 를 만든다.
2. 래퍼를 인터페이스 뒤에 숨긴다.
3. 비즈니스 코드가 래퍼 인터페이스에만 의존하도록 한다.
4. 테스트에서는 가짜 구현을 주입한다.

### 2.2 적용 과정

**1단계: API 래핑 - 각 API에 대한 인터페이스와 래퍼 정의**

```java
// 메일 수신을 위한 인터페이스
public interface MessageReceiver {
    Message receive();
}

// 소켓 기반의 실제 구현
public class SocketMessageReceiver implements MessageReceiver {
    private Socket socket;

    public SocketMessageReceiver(Socket socket) {
        this.socket = socket;
    }

    public Message receive() {
        InputStreamReader isr = new InputStreamReader(socket.getInputStream());
        BufferedReader reader = new BufferedReader(isr);
        StringBuilder message = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            message.append(line);
        }
        return new Message(message.toString());
    }
}
```

```java
// 구독자 저장소를 위한 인터페이스
public interface SubscriberRepository {
    void addSubscriber(String address);
    void removeSubscriber(String address);
    List<String> getAllSubscribers();
}

// DB 기반의 실제 구현
public class DatabaseSubscriberRepository implements SubscriberRepository {
    private String dbUrl;

    public void addSubscriber(String address) {
        Connection conn = DriverManager.getConnection(dbUrl);
        PreparedStatement stmt = conn.prepareStatement(
            "INSERT INTO subscribers (address) VALUES (?)"
        );
        stmt.setString(1, address);
        stmt.executeUpdate();
        stmt.close();
        conn.close();
    }

    // ... 나머지 메서드
}
```

```java
// 메일 전송을 위한 인터페이스
public interface MailSender {
    void send(String to, String subject, String body);
}

// SMTP 기반의 실제 구현
public class SmtpMailSender implements MailSender {
    public void send(String to, String subject, String body) {
        SMTPMessage message = new SMTPMessage();
        message.setFrom("list@example.com");
        message.setTo(to);
        message.setSubject(subject);
        message.setBody(body);
        message.send();
    }
}
```

**2단계: 비즈니스 코드를 래퍼 인터페이스에 의존하도록 재구성**

```java
public class MailingListServer {
    private MessageReceiver receiver;
    private SubscriberRepository subscribers;
    private MailSender mailSender;

    public MailingListServer(
            MessageReceiver receiver,
            SubscriberRepository subscribers,
            MailSender mailSender) {
        this.receiver = receiver;
        this.subscribers = subscribers;
        this.mailSender = mailSender;
    }

    public void processMessage() {
        Message message = receiver.receive();

        if (message.isSubscribeRequest()) {
            String address = message.extractAddress();
            subscribers.addSubscriber(address);
            mailSender.send(address, "구독 확인", "메일링 리스트에 구독되었습니다.");
        } else if (message.isUnsubscribeRequest()) {
            String address = message.extractAddress();
            subscribers.removeSubscriber(address);
        }
    }
}
```

### 2.3 테스트 작성

이제 각 의존성에 가짜 구현을 주입하여 테스트할 수 있다:

```java
public class FakeSubscriberRepository implements SubscriberRepository {
    private List<String> subscribers = new ArrayList<>();

    public void addSubscriber(String address) {
        subscribers.add(address);
    }

    public void removeSubscriber(String address) {
        subscribers.remove(address);
    }

    public List<String> getAllSubscribers() {
        return new ArrayList<>(subscribers);
    }
}

public class FakeMailSender implements MailSender {
    private List<SentMail> sentMails = new ArrayList<>();

    public void send(String to, String subject, String body) {
        sentMails.add(new SentMail(to, subject, body));
    }

    public List<SentMail> getSentMails() { return sentMails; }
}

@Test
public void subscribe_addsSubscriberAndSendsConfirmation() {
    FakeSubscriberRepository subscribers = new FakeSubscriberRepository();
    FakeMailSender mailSender = new FakeMailSender();
    MessageReceiver receiver = new StubMessageReceiver("SUBSCRIBE:user@test.com");

    MailingListServer server = new MailingListServer(
        receiver, subscribers, mailSender
    );

    server.processMessage();

    assertEquals(1, subscribers.getAllSubscribers().size());
    assertEquals("user@test.com", subscribers.getAllSubscribers().get(0));
    assertEquals(1, mailSender.getSentMails().size());
    assertEquals("user@test.com", mailSender.getSentMails().get(0).getTo());
}
```

---

## 3. 해결 전략 2: Responsibility-Based Extraction

두 번째 전략은 **책임 단위로 코드를 클래스로 추출(Responsibility-Based Extraction)** 하는 것이다.

### 3.1 기본 개념

Skin and Wrap the API가 "API를 감싸는 것"에 초점을 맞춘다면, Responsibility-Based Extraction은 "비즈니스 책임을 식별하고 분리하는 것"에 초점을 맞춘다.

코드를 읽으면서 다음 질문을 던진다:

- **이 코드가 수행하는 책임(responsibility)은 무엇인가?**
- **이 책임들을 각각 독립된 클래스로 추출할 수 있는가?**

### 3.2 메일링 리스트 서버에서의 책임 식별

원래 코드에서 다음과 같은 책임들을 식별할 수 있다:

```
[원래 processMessage 메서드의 책임들]

1. 메시지 수신 (소켓에서 데이터 읽기)
2. 메시지 파싱 (명령어와 주소 추출)
3. 구독 처리 (구독자 추가 + 확인 메일 발송)
4. 구독 해제 처리 (구독자 제거)
5. 메일 전송 (SMTP를 통한 메일 발송)
6. 구독자 데이터 관리 (DB에 구독자 추가/삭제)
```

### 3.3 책임별 클래스 추출

각 책임을 별도의 클래스로 추출한다:

```java
// 책임 1: 메시지 파싱
public class MailingListMessage {
    private String rawContent;

    public MailingListMessage(String rawContent) {
        this.rawContent = rawContent;
    }

    public boolean isSubscribeRequest() {
        return rawContent.contains("SUBSCRIBE");
    }

    public boolean isUnsubscribeRequest() {
        return rawContent.contains("UNSUBSCRIBE");
    }

    public String extractAddress() {
        return rawContent.substring(rawContent.indexOf(":") + 1).trim();
    }
}
```

```java
// 책임 2: 구독 처리 로직
public class SubscriptionManager {
    private SubscriberRepository subscribers;
    private MailSender mailSender;

    public SubscriptionManager(
            SubscriberRepository subscribers, MailSender mailSender) {
        this.subscribers = subscribers;
        this.mailSender = mailSender;
    }

    public void subscribe(String address) {
        subscribers.addSubscriber(address);
        mailSender.send(address, "구독 확인", "메일링 리스트에 구독되었습니다.");
    }

    public void unsubscribe(String address) {
        subscribers.removeSubscriber(address);
    }
}
```

```java
// 책임 3: 메시지 디스패칭 (어떤 명령어를 어떤 처리기로 보낼지)
public class MessageDispatcher {
    private SubscriptionManager subscriptionManager;

    public MessageDispatcher(SubscriptionManager subscriptionManager) {
        this.subscriptionManager = subscriptionManager;
    }

    public void dispatch(MailingListMessage message) {
        if (message.isSubscribeRequest()) {
            subscriptionManager.subscribe(message.extractAddress());
        } else if (message.isUnsubscribeRequest()) {
            subscriptionManager.unsubscribe(message.extractAddress());
        }
    }
}
```

### 3.4 추출된 구조의 이점

추출 후 각 클래스를 독립적으로 테스트할 수 있다:

```java
// MailingListMessage는 외부 의존성이 전혀 없다 - 순수 단위 테스트
@Test
public void extractAddress_fromSubscribeMessage() {
    MailingListMessage msg = new MailingListMessage("SUBSCRIBE:user@test.com");
    assertEquals("user@test.com", msg.extractAddress());
}

@Test
public void isSubscribeRequest_trueForSubscribeMessage() {
    MailingListMessage msg = new MailingListMessage("SUBSCRIBE:user@test.com");
    assertTrue(msg.isSubscribeRequest());
    assertFalse(msg.isUnsubscribeRequest());
}

// SubscriptionManager는 가짜 의존성으로 테스트
@Test
public void subscribe_addsAndSendsConfirmation() {
    FakeSubscriberRepository repo = new FakeSubscriberRepository();
    FakeMailSender sender = new FakeMailSender();
    SubscriptionManager manager = new SubscriptionManager(repo, sender);

    manager.subscribe("user@test.com");

    assertTrue(repo.getAllSubscribers().contains("user@test.com"));
    assertEquals(1, sender.getSentMails().size());
}
```

---

## 4. 두 전략의 비교

### 4.1 Skin and Wrap the API vs Responsibility-Based Extraction

| 비교 항목 | Skin and Wrap the API | Responsibility-Based Extraction |
|-----------|----------------------|-------------------------------|
| **초점** | API 경계에서 의존성 끊기 | 비즈니스 책임을 식별하고 분리 |
| **시작점** | 외부 API 호출을 찾아 래핑 | 코드가 수행하는 책임을 분석 |
| **결과** | API 래퍼 + 기존 코드가 래퍼 사용 | 도메인 객체와 서비스 클래스 |
| **장점** | 기계적으로 적용 가능, 실수 위험 적음 | 더 나은 도메인 모델 탄생 |
| **단점** | 도메인 모델이 명시적으로 드러나지 않을 수 있음 | 더 많은 설계 판단이 필요 |
| **적합한 경우** | API 의존성이 명확히 분리되어 있을 때 | 비즈니스 로직이 복잡하게 얽혀 있을 때 |

### 4.2 두 전략의 조합

실제로는 두 전략을 함께 사용하는 것이 가장 효과적이다:

```
1단계: Skin and Wrap the API
  - 외부 API를 인터페이스로 감싼다
  - 이것만으로도 테스트가 가능해진다

2단계: Responsibility-Based Extraction
  - API 래퍼를 사용하는 코드에서 비즈니스 책임을 식별한다
  - 각 책임을 별도 클래스로 추출한다
  - 도메인 모델이 점점 드러난다
```

---

## 5. 얇은 래퍼(Thin Wrapper) 전략의 심화

### 5.1 래퍼를 얇게 유지하는 이유

래퍼의 핵심 목적은 **의존성 차단**이지, 로직 구현이 아니다. 래퍼를 얇게 유지해야 하는 이유:

1. **래퍼 자체는 단위 테스트하기 어렵다**: 래퍼는 실제 외부 시스템과 통신하므로, 통합 테스트로만 검증할 수 있다.
2. **래퍼에 로직이 있으면 테스트 사각지대가 생긴다**: 단위 테스트로 검증할 수 없는 곳에 로직이 숨어 있게 된다.
3. **래퍼가 두꺼워지면 원래 문제가 재발한다**: 비즈니스 로직이 다시 API 호출과 섞이게 된다.

### 5.2 얇은 래퍼의 원칙

```java
// 원칙: 래퍼는 타입 변환과 위임만 수행한다

public class SmtpMailSender implements MailSender {

    // 좋은 예: 도메인 타입을 라이브러리 타입으로 변환하고 위임
    public void send(String to, String subject, String body) {
        SMTPMessage msg = new SMTPMessage();
        msg.setTo(to);
        msg.setSubject(subject);
        msg.setBody(body);
        msg.send();  // 위임
    }

    // 나쁜 예: 래퍼에 비즈니스 로직이 들어감
    public void sendWelcomeEmail(User user) {
        String body = "안녕하세요, " + user.getName() + "님. "
            + "가입을 환영합니다!";
        if (user.isPremium()) {
            body += "\n프리미엄 혜택 안내: ...";
        }
        SMTPMessage msg = new SMTPMessage();
        msg.setTo(user.getEmail());
        msg.setSubject("환영합니다!");
        msg.setBody(body);
        msg.send();
    }
}
```

두 번째 메서드에서 이메일 본문을 구성하는 로직은 비즈니스 로직이다. 이 로직은 래퍼가 아닌 별도의 서비스 클래스에 있어야 하며, 래퍼는 단순히 `send(to, subject, body)`만 수행해야 한다.

---

## 6. 리팩토링 과정의 실전 팁

### 6.1 점진적 접근

API 호출로 가득한 코드를 한 번에 완벽하게 리팩토링하려고 하면 안 된다. 점진적으로 접근해야 한다:

```
[점진적 리팩토링 순서]

1. 가장 테스트하고 싶은 부분을 선택한다
2. 그 부분이 사용하는 API를 래핑한다
3. 래퍼를 사용하도록 코드를 변경한다
4. 테스트를 작성한다
5. 비즈니스 로직을 추출한다
6. 다음 부분을 선택하여 반복한다
```

### 6.2 변경 전후의 코드 구조 비교

```
[변경 전]
MailingListServer
  └── processMessage()
        ├── Socket API 호출 (읽기)
        ├── String 파싱 (비즈니스 로직)
        ├── JDBC API 호출 (DB)
        ├── 조건 분기 (비즈니스 로직)
        └── SMTP API 호출 (메일 전송)

[변경 후]
MailingListServer
  ├── MessageReceiver (인터페이스)
  │     └── SocketMessageReceiver (래퍼)
  ├── MailingListMessage (도메인 객체, 순수 로직)
  ├── SubscriptionManager (비즈니스 서비스)
  │     ├── SubscriberRepository (인터페이스)
  │     │     └── DatabaseSubscriberRepository (래퍼)
  │     └── MailSender (인터페이스)
  │           └── SmtpMailSender (래퍼)
  └── MessageDispatcher (조정 역할)
```

변경 후에는 각 클래스가 명확한 하나의 책임을 가지며, 외부 의존성은 인터페이스 뒤에 숨겨져 있다. 비즈니스 로직(`MailingListMessage`, `SubscriptionManager`)은 외부 의존성 없이 순수하게 테스트할 수 있다.

---

## 요약

- API 호출로만 구성된 코드는 **자체적인 도메인 모델이 없고**, 비즈니스 로직이 API 호출 사이에 흩어져 있어 **테스트가 거의 불가능**하다.
- **Skin and Wrap the API**: API를 인터페이스로 감싸고, 비즈니스 코드가 인터페이스에만 의존하게 하여 테스트 가능성을 확보한다.
- **Responsibility-Based Extraction**: 코드의 책임을 식별하고, 각 책임을 별도 클래스로 추출하여 도메인 모델을 드러낸다.
- 두 전략은 함께 사용할 때 가장 효과적이다: 먼저 API를 감싸고, 그 다음 책임을 추출한다.
- 래퍼는 **얇게(thin)** 유지해야 한다: 타입 변환과 위임만 수행하고, 비즈니스 로직은 넣지 않는다.
- 리팩토링은 **점진적으로** 진행한다: 한 번에 모든 것을 바꾸려 하지 말고, 가장 테스트가 필요한 부분부터 시작한다.

---

## 다음 챕터와의 연결

Chapter 16 "변경이 가능할 만큼 코드를 이해하지 못하는 경우 (I Don't Understand the Code Well Enough to Change It)"에서는 코드를 변경하기 전에 먼저 이해해야 하는 상황을 다룬다. 레거시 코드를 이해하기 위한 실용적 기법들 — 메모와 스케치, 리스팅 마크업, 임시 리팩토링, 미사용 코드 삭제 — 을 살펴보며, 코드의 구조와 의도를 파악하는 방법을 소개한다.
