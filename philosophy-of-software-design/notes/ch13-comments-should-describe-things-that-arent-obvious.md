# Chapter 13: Comments Should Describe Things That Aren't Obvious (주석은 명확하지 않은 것을 설명해야 한다)

## 핵심 질문

좋은 주석은 무엇을 담아야 하는가? 주석의 유형별로 어떤 정보를 제공해야 하는가?

---

## 1. 주석 규칙(Convention) 정하기

팀 차원에서 주석 규칙을 정하고 일관되게 따르는 것이 중요하다. 주요 주석 유형:

| 유형 | 위치 | 목적 |
|------|------|------|
| **인터페이스 주석** | 클래스/메서드 선언 앞 | 사용자를 위한 추상화 설명 |
| **데이터 멤버 주석** | 필드/변수 옆 | 변수가 나타내는 것과 제약 조건 |
| **구현 주석** | 메서드 내부 | 비자명한 로직의 이유와 의도 |
| **모듈 간 주석** | 설계 문서/코드 참조 | 모듈 간 의존성과 관계 |

---

## 2. 코드를 반복하지 마라

> 🚩 **Red Flag: Comment Repeats Code**
>
> "If the information in a comment is already obvious from the code beside it, then the comment isn't helpful. One example of this is when the comment uses the same words that make up the name of the thing it is describing."

```java
// 나쁜 주석: 코드를 그대로 반복
int numRetries;  // 재시도 횟수

// 좋은 주석: 코드에 없는 정보를 추가
int numRetries;  // 연결 실패 시 재시도 횟수. 0이면 재시도 안 함.
                 // 각 재시도 사이에 지수 백오프가 적용됨.
```

```python
# 나쁜: 이름이 이미 말하는 것을 반복
def get_user_count():
    """사용자 수를 반환한다."""  # 메서드 이름에서 이미 알 수 있음
    ...

# 좋은: 이름이 전달하지 못하는 정보를 추가
def get_user_count():
    """현재 활성 사용자 수를 반환한다.

    '활성'은 최근 30일 이내에 로그인한 사용자를 의미한다.
    비활성 사용자나 삭제 대기 상태의 사용자는 제외된다.
    결과는 캐싱되며, 캐시는 5분마다 갱신된다.
    """
    ...
```

---

## 3. 하위 수준 주석: 정밀성을 추가하라

구현 수준의 주석은 변수와 코드에 **정밀한 정보**를 추가해야 한다.

### 3.1 변수 주석

```java
// 나쁜: 이름 반복
private int timeout;  // 타임아웃

// 좋은: 단위, 범위, 특수값 명시
/**
 * 서버 응답 대기 시간의 상한 (밀리초 단위).
 * 0이면 무한 대기. 기본값은 5000ms.
 * 음수는 허용되지 않음.
 */
private int timeout;
```

```python
# 나쁜: 타입 정보만 반복
current_index = 0  # int, 현재 인덱스

# 좋은: 의미와 제약 명시
current_index = 0  # items 리스트에서 다음에 처리할 항목의 위치.
                   # 모든 항목이 처리되면 len(items)와 같아진다.
```

### 3.2 구현 주석

```python
# 나쁜: 코드가 하는 일을 설명 (코드를 읽으면 알 수 있음)
# 리스트를 순회하면서 가격이 0보다 큰 항목을 찾는다
result = [item for item in items if item.price > 0]

# 좋은: 코드가 하는 일의 "이유"를 설명
# 무료 샘플 항목은 매출 보고서에서 제외해야 한다 (정책 #234 참고)
result = [item for item in items if item.price > 0]
```

---

## 4. 상위 수준 주석: 직관을 제공하라

인터페이스 수준의 주석은 **전체적인 직관(intuition)** 을 제공해야 한다. 세부 구현이 아니라 "이 모듈이 무엇이고, 어떤 개념으로 동작하는가"를 전달한다.

```java
/**
 * 백그라운드 작업의 스케줄링과 실행을 관리한다.
 *
 * 작업은 우선순위 순서로 실행된다. 같은 우선순위의 작업은
 * 제출된 순서대로 실행된다. 동시에 실행되는 작업의 수는
 * 가용 CPU 코어 수에 의해 자동으로 제한된다.
 *
 * 이 클래스는 스레드 안전하다. 여러 스레드에서 동시에
 * 작업을 제출할 수 있다.
 */
public class TaskScheduler {
    ...
}
```

이 주석을 읽은 사용자는 구현을 읽지 않고도 `TaskScheduler`를 올바르게 사용할 수 있다.

---

## 5. 인터페이스 주석 vs 구현 주석

### 5.1 인터페이스 주석 (WHAT, not HOW)

사용자 관점에서 작성한다. 구현 세부사항을 포함하지 않는다.

포함할 내용:
- 메서드가 무엇을 하는가 (호출자 관점)
- 각 파라미터의 의미와 제약
- 반환값의 의미
- 발생 가능한 예외와 의미
- 부수 효과 (side effects)

```java
/**
 * 지정된 사용자의 최근 주문 목록을 반환한다.
 *
 * @param userId 사용자 고유 ID. null이면 NullPointerException.
 * @param limit 반환할 최대 주문 수. 0이면 전체 반환.
 * @return 최근 주문부터 시간 역순으로 정렬된 목록.
 *         주문이 없으면 빈 리스트 (null이 아님).
 * @throws UserNotFoundException 해당 userId의 사용자가 없는 경우
 */
public List<Order> getRecentOrders(String userId, int limit)
```

### 5.2 구현 주석 (HOW and WHY)

개발자 관점에서 작성한다. 비자명한 부분의 이유와 방법을 설명한다.

```java
public List<Order> getRecentOrders(String userId, int limit) {
    // 먼저 캐시를 확인한다. 캐시 적중률이 85% 이상이므로
    // 대부분의 경우 DB 쿼리를 피할 수 있다.
    List<Order> cached = cache.get(userId);
    if (cached != null) {
        return limit > 0 ? cached.subList(0, Math.min(limit, cached.size()))
                         : cached;
    }

    // 캐시 미스 시 DB에서 조회.
    // 최근 100개만 조회하는 이유: 그 이상 필요한 경우가 0.1% 미만이며,
    // 전체 조회는 대형 사용자에서 수 초가 걸릴 수 있다.
    List<Order> orders = db.query(
        "SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC LIMIT 100",
        userId);

    cache.put(userId, orders);
    return limit > 0 ? orders.subList(0, Math.min(limit, orders.size()))
                     : orders;
}
```

---

## 6. 모듈 간 주석 (Cross-Module Comments)

가장 작성하기 어렵지만 가장 중요한 유형의 주석이다.

```java
/**
 * 이 메서드의 호출 순서는 Protocol.java의 sendMessage()에서
 * 정의한 프로토콜 순서와 일치해야 한다.
 * 순서가 맞지 않으면 상대방이 메시지를 파싱할 수 없다.
 *
 * @see Protocol#sendMessage
 */
public void writeField(String name, String value) { ... }
```

Ousterhout는 모듈 간 의존성을 설명하는 중앙 설계 문서를 권장하며, 코드에서 이 문서를 참조하는 방식을 제안한다.

---

## 요약

- 주석은 **코드에서 명확하지 않은 정보**를 전달해야 한다.
- **코드를 반복하는 주석은 쓸모없다**. 코드에 없는 정보(이유, 제약, 성능 특성)를 추가하라.
- **하위 수준 주석**은 정밀성을 추가한다: 변수의 단위, 범위, 특수값 등.
- **상위 수준 주석**은 직관을 제공한다: 모듈의 역할과 동작 모델.
- **인터페이스 주석**은 WHAT을, **구현 주석**은 HOW와 WHY를 설명한다.
- **모듈 간 주석**은 모듈 간 의존성을 명시한다.

---

## Red Flags

- 🚩 **Comment Repeats Code**: 주석이 코드를 그대로 반복함

---

## 다음 챕터와의 연결

Chapter 14 **"Choosing Names (이름 짓기)"** 에서는 주석과 함께 코드의 가독성을 결정하는 또 다른 핵심 요소인 이름 짓기를 다룬다. 좋은 이름은 주석의 필요성을 줄이고, 나쁜 이름은 복잡성을 높인다.
