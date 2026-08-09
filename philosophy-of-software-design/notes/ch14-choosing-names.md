# Chapter 14: Choosing Names (이름 짓기)

## 핵심 질문

좋은 이름은 어떤 특성을 가지는가? 이름이 소프트웨어 복잡성에 어떤 영향을 미치는가?

---

## 1. 이름이 중요한 이유

좋은 이름은 일종의 **문서화**다. 주석 없이도 코드의 의미를 전달할 수 있다. 반대로 나쁜 이름은 **모호성(obscurity)** 을 유발하여 복잡성을 높인다.

> "If a variable or method name requires a comment to explain it, the name is probably not good enough."

---

## 2. 이미지를 만들어라 (Create an Image)

좋은 이름은 독자의 머릿속에 **명확한 이미지**를 만든다.

```python
# 나쁜 이름: 이미지가 불명확
count = get_count()
data = fetch_data()
result = process(data)

# 좋은 이름: 구체적인 이미지
active_user_count = get_active_user_count()
pending_orders = fetch_pending_orders()
validated_orders = validate_orders(pending_orders)
```

---

## 3. 정확한 이름을 사용하라 (Be Precise)

> 🚩 **Red Flag: Vague Name**
>
> "If a variable or method name is broad enough to refer to many different things, then it doesn't convey much information to the developer and the underlying entity is more likely to be misused."

### 3.1 모호한 이름 피하기

| 모호한 이름 | 문제 | 더 나은 이름 |
|------------|------|-------------|
| `data` | 무슨 데이터? | `userProfile`, `rawResponse` |
| `result` | 무슨 결과? | `matchingUsers`, `validationErrors` |
| `tmp` | 임시 뭐? | `swapBuffer`, `previousValue` |
| `info` | 무슨 정보? | `connectionStatus`, `errorDetails` |
| `count` | 무엇의 개수? | `activeSessionCount`, `failedAttempts` |
| `handle()` | 어떻게 처리? | `retryFailedRequest()`, `routeToHandler()` |
| `process()` | 무슨 처리? | `validateAndSave()`, `parseAndTransform()` |
| `get()` | 뭘 가져옴? | `fetchFromCache()`, `loadFromDatabase()` |

### 3.2 예시

```java
// 모호: "compute"가 무엇을 계산하는가?
double compute(List<Item> items) { ... }

// 명확: 이름만으로 동작을 알 수 있다
double calculateTotalPrice(List<Item> items) { ... }
```

```python
# 모호: buf는 무엇을 버퍼링하는가?
buf = []
for line in file:
    buf.append(line)

# 명확
unprocessed_lines = []
for line in file:
    unprocessed_lines.append(line)
```

---

## 4. 일관되게 사용하라 (Be Consistent)

같은 것은 항상 같은 이름으로 부른다. 다른 것은 다른 이름으로 부른다.

```java
// 나쁜: 같은 개념에 다른 이름
class OrderService {
    int getCount() { ... }       // "count" 사용
}
class UserService {
    int getNum() { ... }         // "num" 사용
}
class ProductService {
    int getTotal() { ... }       // "total" 사용
}

// 좋은: 같은 개념에 같은 이름
class OrderService {
    int getCount() { ... }
}
class UserService {
    int getCount() { ... }
}
class ProductService {
    int getCount() { ... }
}
```

---

## 5. 불필요한 단어를 추가하지 마라

이름을 길게 만든다고 좋은 것은 아니다. 의미 없는 단어를 추가하면 오히려 가독성이 떨어진다.

```java
// 불필요한 접미사
String fileNameString;  // "String"은 타입에서 이미 알 수 있음 → fileName
List<User> userList;    // "List"는 불필요 → users
Map<String, Config> configMap;  // "Map"은 불필요 → configs 또는 configByName
```

하지만 **정확성을 위해 필요한 단어는 추가**해야 한다:

```java
// 필요한 단어
int elapsedTimeMs;      // "Ms"가 단위를 명확히 함
int maxRetryCount;      // "max"가 의미를 명확히 함
String rawJsonResponse; // "raw"와 "Json"이 처리 상태를 명확히 함
```

---

## 6. 이름 짓기가 어렵다면, 설계를 의심하라

> 🚩 **Red Flag: Hard to Pick Name**
>
> "If it's hard to find a simple name for a variable or method that creates a clear image of the underlying object, that's a hint that the underlying object may not have a clean design."

```java
// 이름 짓기가 어려운 경우 = 설계 문제의 신호
class UserOrderNotificationProcessor { ... }
// 이 클래스의 이름이 이렇게 긴 이유:
// - User, Order, Notification, Processing 네 가지 관심사가 섞여 있음
// - 분리가 필요하다는 신호

// 더 나은 설계:
class NotificationSender { ... }      // 알림 전송
class OrderEventListener { ... }       // 주문 이벤트 감지
```

이름이 길어지거나 모호해진다면, 그 엔티티의 책임이 불명확하거나 너무 많다는 뜻이다.

---

## 7. 범위에 따른 이름 길이

- **넓은 범위(전역, 클래스 멤버)**: 더 구체적이고 긴 이름이 필요하다. 많은 곳에서 사용되므로 맥락 없이도 이해 가능해야 한다.
- **좁은 범위(짧은 루프, 람다)**: 짧은 이름도 괜찮다. 맥락이 가까이 있으므로.

```python
# 좁은 범위: 짧은 이름 OK
for i, item in enumerate(items):
    ...

# 넓은 범위: 구체적인 이름 필요
class PaymentProcessor:
    max_daily_transaction_count = 100  # 멤버 변수는 구체적으로
```

---

## 요약

- 좋은 이름은 **문서화의 일종**이다. 주석 없이도 의미를 전달할 수 있어야 한다.
- 이름은 독자의 머릿속에 **명확한 이미지**를 만들어야 한다.
- **모호한 이름**(`data`, `result`, `tmp`, `handle`)은 피하라.
- **같은 것에는 같은 이름**, 다른 것에는 다른 이름을 일관되게 사용하라.
- 불필요한 단어를 추가하지 말되, **정확성에 필요한 단어는 유지**하라.
- 이름 짓기가 어려우면 **설계를 의심**하라. 책임이 불명확하거나 과도하다는 신호다.

---

## Red Flags

- 🚩 **Vague Name**: 이름이 너무 넓어서 여러 의미로 해석 가능함
- 🚩 **Hard to Pick Name**: 간단하고 명확한 이름을 찾기 어려움 → 설계 문제의 신호

---

## 다음 챕터와의 연결

Chapter 15 **"Write The Comments First (주석을 먼저 작성하라)"** 에서는 주석을 코드보다 먼저 작성하는 습관이 어떻게 설계 품질을 높이는지, 그리고 주석이 단순한 문서화가 아니라 **설계 도구**로서 기능하는 메커니즘을 다룬다.
