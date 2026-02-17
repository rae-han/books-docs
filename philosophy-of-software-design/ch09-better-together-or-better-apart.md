# Chapter 9: Better Together Or Better Apart? (합치는 게 나은가, 분리하는 게 나은가?)

## 핵심 질문

두 개의 관련된 기능이 있을 때, 하나의 모듈에 합치는 것이 나은가, 별도의 모듈로 분리하는 것이 나은가? 이 결정을 내리는 기준은 무엇인가?

---

## 1. 소프트웨어 설계의 근본적 질문

모듈의 크기와 경계를 결정하는 것은 소프트웨어 설계에서 가장 근본적인 질문 중 하나다. 두 기능을 하나의 모듈에 넣을지, 별도의 모듈로 분리할지에 따라 시스템의 복잡성이 크게 달라진다.

Ousterhout의 기본 원칙:

> **목표는 전체 시스템의 복잡성을 최소화하는 것이다. 합치든 분리하든, 전체 복잡성이 줄어드는 방향을 선택하라.**

---

## 2. 합치는 것이 나은 경우

### 2.1 정보를 공유하는 경우

두 모듈이 같은 정보(데이터 구조, 설계 결정, 도메인 지식)에 의존한다면, 합치는 것이 낫다. 분리하면 **정보 누출(Information Leakage)** 이 발생한다.

```python
# 나쁜 예: 같은 파일 형식 지식이 두 클래스에 분산
class ConfigReader:
    def read(self, path):
        with open(path) as f:
            # JSON 형식임을 알고 있음
            return json.load(f)

class ConfigWriter:
    def write(self, path, data):
        with open(path, 'w') as f:
            # JSON 형식임을 알고 있음
            json.dump(data, f, indent=2)

# 좋은 예: 파일 형식 지식을 하나의 클래스에 캡슐화
class ConfigStore:
    FORMAT = "json"

    def read(self, path):
        with open(path) as f:
            return json.load(f)

    def write(self, path, data):
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    # 형식을 YAML로 바꿔도 이 클래스만 수정하면 됨
```

### 2.2 항상 함께 사용되는 경우

두 기능이 항상 함께 사용된다면, 합쳐서 호출자의 부담을 줄인다.

```java
// 나쁜 예: 항상 함께 호출되는 두 메서드가 별도 클래스에
Validator validator = new Validator();
Sanitizer sanitizer = new Sanitizer();

String input = getUserInput();
validator.validate(input);        // 항상 이 순서로
String clean = sanitizer.sanitize(input);  // 함께 호출됨

// 좋은 예: 하나의 메서드로 합침
InputProcessor processor = new InputProcessor();
String clean = processor.processInput(getUserInput());
// 내부에서 검증과 정제를 모두 처리
```

### 2.3 개념적으로 겹치는 경우

두 기능이 같은 상위 문제를 해결하는 부분들이라면, 하나의 모듈에 있는 것이 자연스럽다.

### 2.4 한쪽을 이해하기 위해 다른 쪽이 필요한 경우

한 모듈의 코드를 이해하려면 다른 모듈도 반드시 읽어야 한다면, 이 둘은 사실상 하나의 모듈이다.

> 🚩 **Red Flag: Conjoined Methods**
>
> "It should be possible to understand each method independently. If you can't understand the implementation of one method without also understanding the implementation of another, that's a red flag. This suggests that the methods should be combined, or that the interface between them needs to be improved."

```java
// 나쁜 예: 두 메서드가 서로의 구현에 의존
class DataProcessor {
    // 이 메서드는 prepareData()가 반환한 형식을 알아야 이해 가능
    void processData(Object[] prepared) {
        // prepared[0]은 헤더, prepared[1]은 바디...
        // prepareData()의 구현을 알아야 이해할 수 있다
    }

    Object[] prepareData(RawData raw) {
        // processData()가 기대하는 형식으로 변환
        return new Object[]{ raw.getHeader(), raw.getBody() };
    }
}

// 좋은 예: 합치거나, 명확한 인터페이스로 분리
class DataProcessor {
    void process(RawData raw) {
        Header header = raw.getHeader();
        Body body = raw.getBody();
        // 하나의 메서드에서 전체 흐름을 처리
    }
}
```

---

## 3. 분리하는 것이 나은 경우

### 3.1 각각 독립적으로 이해 가능한 경우

두 기능이 서로에 대해 알 필요 없이 독립적으로 이해되고 사용될 수 있다면, 분리가 낫다.

### 3.2 서로 다른 목적을 가진 경우

개념적 겹침이 없고 완전히 다른 문제를 해결한다면 분리한다.

### 3.3 합치면 너무 커지는 경우

합치는 것이 논리적으로 맞더라도, 결과 모듈이 지나치게 커서 이해하기 어렵다면 분리를 고려한다. 하지만 이 경우에도 분리의 기준은 크기가 아니라 **추상화의 깔끔함**이어야 한다.

---

## 4. 과도한 분리의 문제

### 4.1 "클래스는 작아야 한다"의 함정

"클래스는 작아야 한다", "메서드는 짧아야 한다"는 조언은 극단적으로 적용하면 오히려 해가 된다.

```java
// 과도한 분리: 각 메서드가 너무 작아서 의미가 없음
class OrderProcessor {
    void process(Order order) {
        validateOrder(order);
        calculateTotal(order);
        applyDiscount(order);
        calculateTax(order);
        finalizeOrder(order);
    }

    private void validateOrder(Order order) {
        // 3줄짜리 검증 로직
    }

    private void calculateTotal(Order order) {
        // 2줄짜리 합산 로직
    }

    // ... 각 메서드가 2-3줄
}
```

이렇게 분리하면:
- 메서드를 이해하려면 5개의 메서드를 오가며 읽어야 한다
- 메서드 간의 실행 순서 의존성이 보이지 않는다
- 각 메서드가 너무 얕아서 추상화의 가치가 없다

```java
// 차라리 하나의 메서드에 전체 흐름을 담는 게 낫다
class OrderProcessor {
    void process(Order order) {
        // 검증
        if (order.getItems().isEmpty()) throw new InvalidOrderException();

        // 합산
        double total = order.getItems().stream()
            .mapToDouble(Item::getPrice).sum();

        // 할인 적용
        total *= (1 - order.getDiscountRate());

        // 세금
        total *= (1 + TAX_RATE);

        order.setFinalTotal(total);
    }
}
```

### 4.2 메서드 분리가 적절한 경우

메서드를 분리하는 것이 적절한 경우는 추출된 메서드가 **독립적인 범용 기능(subtask)** 을 제공할 때다.

```java
// 좋은 분리: 범용 유틸리티 추출
class OrderProcessor {
    void process(Order order) {
        // ... 주문 처리 로직 ...
        String formattedTotal = formatCurrency(total, order.getCurrency());
        // ...
    }

    // 이 메서드는 독립적이고 범용적이다
    // 다른 곳에서도 사용할 수 있다
    private String formatCurrency(double amount, Currency currency) {
        return currency.getSymbol() + String.format("%.2f", amount);
    }
}
```

---

## 5. Special-General Mixture

> 🚩 **Red Flag: Special-General Mixture**
>
> "This red flag occurs when a general-purpose mechanism also contains code specialized for a particular use of that mechanism. This makes the mechanism more complicated and creates information leakage between the mechanism and the specific use case."

범용 메커니즘에 특수 목적 코드가 섞이면 문제가 된다:

```python
# 나쁜 예: 범용 캐시에 특수 로직이 섞임
class Cache:
    def get(self, key):
        value = self._store.get(key)
        if value is None:
            return None

        # 특수 로직: 사용자 세션 만료 처리
        if key.startswith("session:"):
            if value.is_expired():
                self.delete(key)
                return None

        return value

# 좋은 예: 범용 캐시는 범용으로, 특수 로직은 상위 계층에
class Cache:
    def get(self, key):
        return self._store.get(key)

    def get_with_ttl(self, key):
        """TTL을 고려한 조회 (범용)"""
        value = self._store.get(key)
        if value and value.is_expired():
            self.delete(key)
            return None
        return value

class SessionManager:
    def get_session(self, session_id):
        """세션 조회 (특수)"""
        return self.cache.get_with_ttl(f"session:{session_id}")
```

---

## 6. 반복(Repetition)

> 🚩 **Red Flag: Repetition**
>
> 같은 코드 패턴이 여러 곳에서 반복된다면, 아직 발견되지 않은 추상화가 존재한다는 신호다.

```python
# 나쁜 예: 에러 처리 패턴이 반복
def create_user(data):
    try:
        result = db.execute("INSERT INTO users ...")
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        metrics.increment("db_errors")
        raise ServiceError("Failed to create user")

def update_user(user_id, data):
    try:
        result = db.execute("UPDATE users ...")
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        metrics.increment("db_errors")
        raise ServiceError("Failed to update user")

# 좋은 예: 반복 패턴을 추상화
def execute_db_operation(operation_name, query, *args):
    try:
        return db.execute(query, *args)
    except DatabaseError as e:
        logger.error(f"Database error in {operation_name}: {e}")
        metrics.increment("db_errors")
        raise ServiceError(f"Failed to {operation_name}")

def create_user(data):
    execute_db_operation("create user", "INSERT INTO users ...", data)

def update_user(user_id, data):
    execute_db_operation("update user", "UPDATE users ...", user_id, data)
```

---

## 7. 판단 기준 정리

두 기능을 합칠지 분리할지 결정하는 체크리스트:

| 질문 | "예"이면 |
|------|---------|
| 같은 정보/지식을 공유하는가? | 합치기 |
| 항상 함께 사용되는가? | 합치기 |
| 개념적으로 겹치는가? | 합치기 |
| 한쪽 없이 다른 쪽을 이해하기 어려운가? | 합치기 |
| 각각 독립적으로 이해 가능한가? | 분리하기 |
| 서로 다른 목적인가? | 분리하기 |
| 합치면 너무 커지는가? | 분리하기 (단, 추상화 기준으로) |

> **핵심 통찰**: "합치기 vs 분리하기"의 판단 기준은 **코드의 줄 수**가 아니라 **복잡성의 총량**이다. 합쳤을 때 전체 복잡성이 줄어들면 합치고, 분리했을 때 줄어들면 분리한다.

---

## 요약

- 합치기와 분리하기의 판단 기준은 **전체 시스템의 복잡성 최소화**다.
- **합치는 것이 나은 경우**: 정보 공유, 항상 함께 사용, 개념적 겹침, 상호 의존성.
- **분리하는 것이 나은 경우**: 독립적 이해 가능, 다른 목적, 합치면 너무 큼.
- **과도한 분리 주의**: "작은 클래스/메서드"를 맹목적으로 추구하면 얕은 모듈이 양산된다.
- 메서드를 분리하려면 추출된 메서드가 **독립적인 범용 기능**을 제공해야 한다.
- 범용 메커니즘에 특수 목적 코드를 섞지 마라 (**Special-General Mixture**).
- 같은 코드 패턴의 반복은 **누락된 추상화**의 신호다.

---

## Red Flags

- 🚩 **Conjoined Methods**: 한 메서드를 이해하려면 다른 메서드의 구현도 읽어야 함
- 🚩 **Special-General Mixture**: 범용 메커니즘에 특수 목적 코드가 섞여 있음
- 🚩 **Repetition**: 같은 코드 패턴이 여러 곳에서 반복됨

---

## 다음 챕터와의 연결

Chapter 10 **"Define Errors Out Of Existence (에러를 정의 밖으로 내보내라)"** 에서는 예외 처리가 복잡성의 주요 원인이 되는 메커니즘과, 에러 조건 자체를 재정의하여 예외를 없애는 설계 기법을 다룬다. 이 장에서 다룬 "합치기"의 한 형태로, 에러 처리를 모듈 내부로 흡수하여 인터페이스를 단순화하는 전략이다.
