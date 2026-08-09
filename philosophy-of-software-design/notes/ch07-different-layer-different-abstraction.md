# Chapter 7: Different Layer, Different Abstraction (계층이 다르면 추상화도 달라야 한다)

## 핵심 질문

소프트웨어 시스템의 인접한 계층이 유사한 추상화를 가지고 있다면, 이것은 어떤 설계 문제를 나타내는가?

---

## 1. 소프트웨어 시스템은 계층으로 이루어진다

### 1.1 계층 구조의 본질

잘 설계된 소프트웨어 시스템은 **계층(layer)** 으로 구성된다. 상위 계층은 하위 계층이 제공하는 기능을 사용하며, 각 계층은 서로 다른 수준의 추상화를 제공한다.

대표적인 예시: 네트워크 스택

```
┌─────────────────────────┐
│  Application Layer       │  HTTP, FTP, SMTP...
├─────────────────────────┤
│  Transport Layer         │  TCP, UDP
├─────────────────────────┤
│  Network Layer           │  IP
├─────────────────────────┤
│  Data Link Layer         │  Ethernet, Wi-Fi
├─────────────────────────┤
│  Physical Layer          │  전기 신호, 광 신호
└─────────────────────────┘
```

각 계층은 완전히 다른 추상화를 제공한다. Application Layer는 "HTTP 요청/응답"이라는 개념으로 동작하고, Transport Layer는 "바이트 스트림의 신뢰성 있는 전달"이라는 개념으로 동작한다. 이 둘은 전혀 다른 수준의 추상화다.

### 1.2 핵심 원칙

> **인접한 계층이 유사한 추상화를 가지고 있다면, 이는 설계 문제의 신호다.**

좋은 계층 구조에서는 각 계층이 이전 계층과는 다른 추상화를 제공한다. 만약 두 인접 계층의 추상화가 비슷하다면, 계층 분리가 올바르게 이루어지지 않았을 가능성이 높다.

---

## 2. Pass-Through Method (통과 메서드)

### 2.1 정의

**Pass-Through Method(통과 메서드)** 는 거의 아무 일도 하지 않고, 인자를 그대로 다른 메서드에 전달하기만 하는 메서드다. 통과 메서드의 시그니처는 호출하는 메서드의 시그니처와 유사하거나 동일하다.

```java
// 나쁜 예: 통과 메서드
public class TextDocument {
    private TextArea textArea;

    // 이 메서드는 아무 가치도 추가하지 않는다
    public void insert(Position pos, String text) {
        textArea.insert(pos, text);
    }

    public void delete(Position start, Position end) {
        textArea.delete(start, end);
    }

    public String getText() {
        return textArea.getText();
    }
}
```

이 `TextDocument` 클래스의 메서드들은 `TextArea`의 메서드를 그대로 호출할 뿐이다. 두 클래스의 인터페이스가 거의 동일하므로, 같은 추상화가 두 번 반복되고 있다.

### 2.2 왜 문제인가

> 🚩 **Red Flag: Pass-Through Method**
>
> "A pass-through method is one that does nothing except pass its arguments to another method, usually with the same API as the pass-through method. This typically indicates that there is not a clean division of responsibility between the classes."

통과 메서드가 문제인 이유:

| 문제 | 설명 |
|------|------|
| **얕은 모듈** | 통과 메서드는 인터페이스만 있고 기능이 없는 전형적인 얕은 모듈이다 |
| **불필요한 복잡성** | 호출자가 두 계층의 인터페이스를 모두 알아야 할 수 있다 |
| **혼란** | 어떤 클래스가 실제 작업을 담당하는지 불명확하다 |
| **변경 증폭** | 하위 메서드의 시그니처가 바뀌면 통과 메서드도 바꿔야 한다 |

### 2.3 해결 방법

통과 메서드를 발견했을 때의 대응 전략:

**방법 1: 클래스 합치기**

두 클래스의 추상화가 동일하다면, 하나로 합치는 것이 나을 수 있다.

```java
// TextDocument와 TextArea가 같은 추상화 → 합치기
public class TextDocument {
    private List<String> lines;

    public void insert(Position pos, String text) {
        // 직접 구현
        // ...
    }
}
```

**방법 2: 책임 재분배**

통과 메서드가 존재하는 이유가 클래스 간 책임 분배가 잘못되었기 때문이라면, 책임을 재분배한다.

```java
// 방법: TextDocument에 고유한 책임 부여
public class TextDocument {
    private TextArea textArea;
    private UndoHistory undoHistory;

    public void insert(Position pos, String text) {
        undoHistory.record(new InsertAction(pos, text));
        textArea.insert(pos, text);
        notifyListeners();  // 고유한 기능 추가
    }
}
```

이제 `insert` 메서드는 단순 통과가 아니라 실질적인 가치(undo 기록, 리스너 알림)를 추가한다.

**방법 3: 호출자가 하위 객체를 직접 사용**

상위 클래스가 단순히 중계만 한다면, 호출자가 하위 객체를 직접 사용하도록 바꾼다.

---

## 3. 인터페이스 중복이 허용되는 경우

### 3.1 디스패처(Dispatcher) 패턴

디스패처는 인자를 기반으로 적절한 핸들러를 선택하여 호출한다. 인터페이스가 비슷해 보이지만, 각 핸들러는 서로 다른 구현을 제공한다.

```python
# 디스패처: 인터페이스 중복이 허용되는 경우
class WebServer:
    def handle_request(self, request):
        if request.path == "/users":
            return self.user_handler.handle(request)
        elif request.path == "/orders":
            return self.order_handler.handle(request)
        elif request.path == "/products":
            return self.product_handler.handle(request)
```

이것은 통과 메서드가 아니다. 디스패처는 **라우팅**이라는 고유한 역할을 수행하고 있으며, 각 핸들러는 완전히 다른 동작을 한다.

### 3.2 같은 시그니처, 다른 구현

인터페이스(interface)를 구현하는 여러 클래스는 동일한 메서드 시그니처를 가지지만, 각각 다른 구현을 제공한다. 이것은 다형성의 핵심이며 설계 문제가 아니다.

```java
interface Storage {
    void save(String key, byte[] data);
    byte[] load(String key);
}

class FileStorage implements Storage { /* 파일 시스템에 저장 */ }
class S3Storage implements Storage { /* AWS S3에 저장 */ }
class MemoryStorage implements Storage { /* 메모리에 저장 */ }
```

---

## 4. 데코레이터 (Decorator)

### 4.1 데코레이터의 문제

**데코레이터(Decorator)** 는 기존 객체를 감싸면서 동일한 인터페이스를 노출하고, 약간의 기능을 추가하는 패턴이다. 데코레이터는 통과 메서드의 온상이 되기 쉽다.

Java I/O는 데코레이터의 대표적 사례이자 문제점을 보여주는 예시다:

```java
// Java I/O: 데코레이터의 남용
FileInputStream fileStream = new FileInputStream("data.txt");
BufferedInputStream bufferedStream = new BufferedInputStream(fileStream);
ObjectInputStream objectStream = new ObjectInputStream(bufferedStream);

Object obj = objectStream.readObject();
```

`BufferedInputStream`은 `FileInputStream`을 감싸면서 버퍼링만 추가한다. 나머지 메서드들은 모두 통과 메서드다. 사용자는 세 개의 클래스를 조합해야 기본적인 파일 읽기를 할 수 있다.

### 4.2 데코레이터 대안

데코레이터를 만들기 전에 다음을 고려한다:

| 대안 | 설명 |
|------|------|
| **기존 클래스에 기능 추가** | 버퍼링을 FileInputStream에 직접 내장 (가장 간단) |
| **기존 데코레이터에 합치기** | 이미 데코레이터가 있다면 거기에 기능 추가 |
| **독립 클래스로 구현** | 감싸는 대신 별도의 독립 모듈로 설계 |

> **핵심 통찰**: 데코레이터가 많다는 것은 기본 클래스가 충분히 깊지 않다는 신호다. 깊은 모듈은 대부분의 기능을 내부에 포함하므로, 외부에서 감싸서 기능을 추가할 필요가 줄어든다.

---

## 5. Pass-Through Variable (통과 변수)

### 5.1 정의

**통과 변수(Pass-Through Variable)** 는 긴 메서드 호출 체인을 따라 전달되지만, 중간 메서드들은 이 변수를 사용하지 않는 경우를 말한다.

```java
// 통과 변수 문제
public class Application {
    public void start(Config config) {
        ServiceManager manager = new ServiceManager(config);  // config 전달
        manager.initialize();
    }
}

public class ServiceManager {
    private Config config;  // 자신은 사용하지 않음

    public ServiceManager(Config config) {
        this.config = config;
    }

    public void initialize() {
        DatabaseService db = new DatabaseService(config);  // 그냥 전달만
        db.connect();
    }
}

public class DatabaseService {
    public DatabaseService(Config config) {
        String url = config.getDatabaseUrl();  // 여기서 비로소 사용
        // ...
    }
}
```

`ServiceManager`는 `Config`를 사용하지 않지만 `DatabaseService`에 전달하기 위해 들고 있어야 한다.

### 5.2 왜 문제인가

- 중간 계층의 메서드 시그니처에 불필요한 파라미터가 추가된다
- 새로운 변수가 필요하면 체인의 모든 메서드를 수정해야 한다 (변경 증폭)
- 코드를 읽는 사람이 "왜 이 파라미터가 여기 있지?"라고 혼란스러워한다

### 5.3 해결 방법

**방법 1: 공유 컨텍스트 객체**

여러 계층이 공유하는 컨텍스트 객체를 만들어, 각 계층이 필요한 정보를 직접 꺼내 쓴다.

```java
// 공유 컨텍스트 객체
public class ApplicationContext {
    private Config config;
    private Logger logger;
    // 각종 공유 자원...

    public String getDatabaseUrl() {
        return config.getDatabaseUrl();
    }
}

// 각 클래스가 컨텍스트를 직접 참조
public class DatabaseService {
    private ApplicationContext context;

    public void connect() {
        String url = context.getDatabaseUrl();
    }
}
```

**방법 2: 전역/싱글턴 (주의해서 사용)**

정말 시스템 전체에서 사용되는 값이라면 전역 접근을 허용할 수 있다. 하지만 전역 상태는 모호성을 유발하므로 신중하게 사용해야 한다.

> **핵심 통찰**: 통과 변수는 계층 간 추상화가 제대로 분리되지 않았다는 신호다. 각 계층은 자신의 역할에 필요한 정보만 알아야 한다.

---

## 6. 계층별 추상화 수준 맞추기

### 6.1 좋은 계층 구조의 특징

```
┌──────────────────────┐
│  UI Layer             │  "사용자가 주문 버튼을 클릭했다"
├──────────────────────┤
│  Application Layer    │  "주문을 생성하고 결제를 처리한다"
├──────────────────────┤
│  Domain Layer         │  "주문 객체, 결제 규칙, 재고 관리"
├──────────────────────┤
│  Infrastructure Layer │  "SQL 쿼리 실행, HTTP 요청 전송"
└──────────────────────┘
```

각 계층의 추상화가 완전히 다르다:
- UI Layer는 "버튼", "폼", "화면"을 다룬다
- Application Layer는 "주문 생성", "결제 처리" 같은 유스케이스를 다룬다
- Domain Layer는 "주문", "결제 규칙" 같은 비즈니스 개념을 다룬다
- Infrastructure Layer는 "SQL", "HTTP" 같은 기술적 메커니즘을 다룬다

### 6.2 나쁜 계층 구조의 특징

인접한 계층의 추상화가 비슷하면 문제다:

```
// 나쁜 예: 두 계층이 같은 추상화
class OrderController {
    void createOrder(OrderRequest req) {
        orderService.createOrder(req);  // 통과!
    }
}

class OrderService {
    void createOrder(OrderRequest req) {
        orderRepository.save(new Order(req));  // 실제 로직
    }
}
```

`OrderController`와 `OrderService`의 인터페이스가 동일하다. `OrderController`는 통과 메서드만 가지고 있는 얕은 모듈이다.

---

## 요약

- 잘 설계된 시스템에서 **인접한 계층은 서로 다른 추상화**를 제공한다.
- **통과 메서드(Pass-Through Method)** 는 아무 기능도 추가하지 않고 인자를 그대로 전달하는 메서드로, 클래스 간 책임 분배가 잘못되었음을 나타낸다.
- **데코레이터(Decorator)** 는 통과 메서드의 온상이 되기 쉽다. 데코레이터를 만들기 전에 기존 클래스에 기능을 추가하는 것을 먼저 고려하라.
- **통과 변수(Pass-Through Variable)** 는 중간 계층을 불필요하게 복잡하게 만든다. 공유 컨텍스트 객체로 해결할 수 있다.
- 인터페이스 중복이 허용되는 경우: **디스패처 패턴**과 **다형성**(같은 인터페이스, 다른 구현).

---

## Red Flags

- 🚩 **Pass-Through Method**: 인자를 그대로 전달하기만 하고 고유한 기능이 없는 메서드
- 🚩 **Adjacent Layers with Similar Abstractions**: 인접한 두 계층의 인터페이스가 유사함
- 🚩 **Decorator Proliferation**: 데코레이터가 많다는 것은 기본 클래스가 충분히 깊지 않다는 신호

---

## 다음 챕터와의 연결

Chapter 8 **"Pull Complexity Downwards (복잡성을 아래로 끌어내려라)"** 에서는 복잡성이 어딘가에 존재해야 한다면 **상위 계층(인터페이스)보다 하위 계층(구현)에 두는 것이 낫다**는 원칙을 다룬다. 이는 "깊은 모듈"과 "계층별 다른 추상화" 원칙의 자연스러운 연장이다.
