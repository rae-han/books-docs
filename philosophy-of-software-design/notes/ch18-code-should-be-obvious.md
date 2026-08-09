# Chapter 18: Code Should be Obvious (코드는 명확해야 한다)

## 핵심 질문

"명확한 코드"란 무엇인가? 코드를 불명확하게 만드는 요소는 무엇이고, 어떻게 피할 수 있는가?

---

## 1. 명확성의 정의

> **코드가 명확하다는 것은, 독자가 코드를 빠르게 읽었을 때 그 의미와 동작에 대한 첫 번째 추측이 맞는다는 것이다.**

명확한 코드는 Unknown Unknowns(Ch 2)를 최소화한다. 독자가 코드를 읽으면서 "아, 이건 이렇게 동작하겠구나"라고 생각한 것이 실제로 맞다면, 그 코드는 명확하다.

---

## 2. 명확성을 높이는 것들

- **좋은 이름** (Ch 14): 이름만으로 의미가 전달됨
- **일관성** (Ch 17): 익숙한 패턴은 즉시 이해됨
- **적절한 공백과 포매팅**: 코드의 구조가 시각적으로 드러남
- **주석** (Ch 12~13): 코드만으로 불명확한 부분을 보충

---

## 3. 명확성을 해치는 것들

### 3.1 이벤트 기반 프로그래밍

이벤트 기반 코드는 제어 흐름을 추적하기 어렵다:

```javascript
// 이벤트 등록은 여기
button.addEventListener('click', handleClick);

// 핸들러 정의는 저기
function handleClick(event) {
    // 이 함수가 언제, 어디서 호출되는지
    // 코드를 읽는 것만으로는 파악하기 어렵다
}
```

완화 방법: 명확한 이름, 이벤트와 핸들러의 관계를 문서화

### 3.2 제네릭 컨테이너

```java
// 불명확: 첫 번째와 두 번째가 뭔지 모름
Pair<String, Integer> result = lookup(key);
String name = result.getFirst();   // first가 뭔데?
Integer count = result.getSecond(); // second가 뭔데?

// 명확: 의미가 명시적
record LookupResult(String userName, int orderCount) {}
LookupResult result = lookup(key);
String name = result.userName();
int count = result.orderCount();
```

> 🚩 **Red Flag: Nonobvious Code**
>
> "If the meaning and behavior of code cannot be understood with a quick reading, it is a red flag."

### 3.3 선언 타입과 할당 타입의 불일치

```java
// 독자가 두 타입의 관계를 알아야 이해 가능
List<String> items = new ArrayList<>();  // List ≠ ArrayList
Map<String, Object> config = new LinkedHashMap<>();  // 순서 보장이 중요하다면 주석 필요
```

### 3.4 독자의 기대를 위반하는 코드

```python
# 이름은 "get"이지만 실제로는 부수 효과가 있다
def get_user_count():
    # 실은 데이터를 캐시에 저장하고, 로그도 남기고,
    # 오래된 세션도 정리한다!
    clean_expired_sessions()  # 기대하지 않은 부수 효과
    count = db.query("SELECT COUNT(*) FROM users")
    cache.set("user_count", count)
    logger.info(f"User count: {count}")
    return count
```

`get`으로 시작하는 메서드에서 독자는 **부수 효과 없이 값을 반환**할 것으로 기대한다. 이 기대를 위반하면 Unknown Unknowns가 발생한다.

---

## 4. 명확성은 독자의 관점이다

> **자신의 코드가 명확한지 판단하는 가장 좋은 방법은 코드 리뷰다.**

코드 작성자는 너무 많은 맥락을 가지고 있어서 자신의 코드를 객관적으로 평가하기 어렵다. 코드 리뷰어가 "이 부분이 이해가 안 된다"고 말하면, 그것은 명확성이 부족하다는 확실한 신호다.

> "소프트웨어는 읽기 쉽게, 쓰기 쉽게가 아니라 **읽기 쉽게** 설계해야 한다."

---

## 요약

- **명확한 코드**: 독자의 첫 번째 추측이 맞는 코드.
- 명확성을 높이는 요소: 좋은 이름, 일관성, 포매팅, 주석.
- 명확성을 해치는 요소: 이벤트 기반 코드, 제네릭 컨테이너(`Pair`, `Tuple`), 기대 위반 코드.
- 명확성은 **독자의 관점**에서 판단한다. **코드 리뷰**가 가장 좋은 검증 방법이다.

---

## Red Flags

- 🚩 **Nonobvious Code**: 빠르게 읽었을 때 의미와 동작을 이해할 수 없는 코드

---

## 다음 챕터와의 연결

Chapter 19 **"Software Trends (소프트웨어 트렌드)"** 에서는 OOP, 애자일, TDD, 디자인 패턴 등 주요 소프트웨어 트렌드에 대한 Ousterhout의 비판적 평가를 다룬다. 각 트렌드가 복잡성 관리에 도움이 되는지를 기준으로 판단한다.
