# Chapter 7: Error Handling (오류 처리)

## 핵심 질문

오류 처리 코드로 인해 프로그램 논리를 이해하기 어려워진다면 깨끗한 코드라 부를 수 있는가? 오류 처리를 프로그램 논리와 분리하면서도 안정성을 높이는 방법은 무엇인가?

---

## 1. 오류 처리와 깨끗한 코드의 관계

깨끗한 코드를 다루는 책에 오류 처리를 논하는 장이 있어 이상하게 여길지도 모르겠다. 하지만 오류 처리는 프로그램에 반드시 필요한 요소 중 하나다. 입력이 이상하거나 디바이스가 실패할지도 모르기 때문이다. 뭔가 잘못될 가능성은 늘 존재하며, 바로 잡을 책임은 바로 우리 프로그래머에게 있다.

상당수 코드 기반은 전적으로 오류 처리 코드에 좌우된다. 여기저기 흩어진 오류 처리 코드 때문에 **실제 코드가 하는 일을 파악하기가 거의 불가능**하다는 의미다.

> **핵심 통찰**: 오류 처리는 중요하다. 하지만 오류 처리 코드로 인해 프로그램 논리를 이해하기 어려워진다면 깨끗한 코드라 부르기 어렵다.

---

## 2. 오류 코드보다 예외를 사용하라

얼마 전까지만 해도 예외를 지원하지 않는 프로그래밍 언어가 많았다. 오류 플래그를 설정하거나 호출자에게 오류 코드를 반환하는 방법이 전부였다.

```java
// 나쁜 예 — 오류 코드 사용: 호출자 코드가 복잡해진다
public class DeviceController {
    ...
    public void sendShutDown() {
        DeviceHandle handle = getHandle(DEV1);
        // 디바이스 상태를 점검한다.
        if (handle != DeviceHandle.INVALID) {
            // 레코드 필드에 디바이스 상태를 저장한다.
            retrieveDeviceRecord(handle);
            // 디바이스가 일시정지 상태가 아니라면 종료한다.
            if (record.getStatus() != DEVICE_SUSPENDED) {
                pauseDevice(handle);
                clearDeviceWorkQueue(handle);
                closeDevice(handle);
            } else {
                logger.log("Device suspended. Unable to shut down");
            }
        } else {
            logger.log("Invalid handle for: " + DEV1.toString());
        }
    }
    ...
}
```

함수를 호출한 즉시 오류를 확인해야 하기 때문에 호출자 코드가 복잡해진다. 불행히도 이 단계는 잊어버리기 쉽다.

```java
// 좋은 예 — 예외 사용: 논리와 오류 처리가 분리된다
public class DeviceController {
    ...
    public void sendShutDown() {
        try {
            tryToShutDown();
        } catch (DeviceShutDownError e) {
            logger.log(e);
        }
    }

    private void tryToShutDown() throws DeviceShutDownError {
        DeviceHandle handle = getHandle(DEV1);
        DeviceRecord record = retrieveDeviceRecord(handle);
        pauseDevice(handle);
        clearDeviceWorkQueue(handle);
        closeDevice(handle);
    }

    private DeviceHandle getHandle(DeviceID id) {
        ...
        throw new DeviceShutDownError("Invalid handle for: " + id.toString());
        ...
    }
    ...
}
```

디바이스를 종료하는 **알고리즘**과 오류를 처리하는 **알고리즘**이 분리되었다. 이제는 각 개념을 독립적으로 살펴보고 이해할 수 있다.

---

## 3. Try-Catch-Finally 문부터 작성하라

`try` 블록은 트랜잭션과 비슷하다. `try` 블록에서 무슨 일이 생기든지 `catch` 블록은 프로그램 상태를 일관성 있게 유지해야 한다. 그러므로 **예외가 발생할 코드를 짤 때는 try-catch-finally 문으로 시작하는 편이 낫다.**

### TDD로 예외 처리 구현하기

**1단계**: 파일이 없으면 예외를 던지는지 알아보는 단위 테스트를 작성한다.

```java
@Test(expected = StorageException.class)
public void retrieveSectionShouldThrowOnInvalidFileName() {
    sectionStore.retrieveSection("invalid - file");
}
```

**2단계**: 단위 테스트에 맞춰 코드를 구현한다.

```java
public List<RecordedGrip> retrieveSection(String sectionName) {
    try {
        FileInputStream stream = new FileInputStream(sectionName);
    } catch (Exception e) {
        throw new StorageException("retrieval error", e);
    }
    return new ArrayList<RecordedGrip>();
}
```

**3단계**: 리팩터링 — catch 블록에서 예외 유형을 좁힌다.

```java
public List<RecordedGrip> retrieveSection(String sectionName) {
    try {
        FileInputStream stream = new FileInputStream(sectionName);
        stream.close();
    } catch (FileNotFoundException e) {
        throw new StorageException("retrieval error", e);
    }
    return new ArrayList<RecordedGrip>();
}
```

> **핵심 통찰**: 먼저 강제로 예외를 일으키는 테스트 케이스를 작성한 후 테스트를 통과하게 코드를 작성하는 방법을 권장한다. 그러면 자연스럽게 try 블록의 트랜잭션 범위부터 구현하게 되므로 범위 내에서 트랜잭션 본질을 유지하기 쉬워진다.

---

## 4. 미확인(unchecked) 예외를 사용하라

여러 해 동안 자바 프로그래머들은 확인된(checked) 예외의 장단점을 놓고 논쟁을 벌여왔다. 자바 첫 버전이 확인된 예외를 선보였던 당시는 멋진 아이디어로 여겨졌지만, 지금은 안정적인 소프트웨어를 제작하는 요소로 **반드시 필요하지는 않다**는 사실이 분명해졌다.

C#은 확인된 예외를 지원하지 않는다. C++, 파이썬, 루비도 마찬가지다. 그럼에도 불구하고 안정적인 소프트웨어를 구현하기에 무리가 없다.

### 확인된 예외의 비용

확인된 예외는 **OCP(Open Closed Principle)를 위반**한다:

1. 메서드에서 확인된 예외를 던지면, catch 블록이 세 단계 위에 있더라도 **그 사이 메서드 모두**가 선언부에 해당 예외를 정의해야 한다
2. 하위 단계에서 코드를 변경하면 **상위 단계 메서드 선언부를 전부** 고쳐야 한다
3. 모듈과 관련된 코드가 전혀 바뀌지 않았더라도 모듈을 다시 빌드하고 배포해야 한다
4. `throws` 경로에 위치하는 **모든 함수가 최하위 함수에서 던지는 예외를 알아야** 하므로 캡슐화가 깨진다

| 확인된(checked) 예외 | 미확인(unchecked) 예외 |
|---|---|
| 메서드 선언부에 throws 절 필수 | 선언부 변경 불필요 |
| 연쇄적 수정 (OCP 위반) | 캡슐화 유지 |
| 아주 중요한 라이브러리에서는 유용 | 일반적인 애플리케이션에 적합 |

---

## 5. 예외에 의미를 제공하라

예외를 던질 때는 전후 상황을 충분히 덧붙인다. 그러면 오류가 발생한 **원인과 위치**를 찾기가 쉬워진다.

자바는 모든 예외에 호출 스택을 제공한다. 하지만 실패한 코드의 의도를 파악하려면 호출 스택만으로 부족하다:

- 오류 메시지에 **정보를 담아** 예외와 함께 던진다
- 실패한 연산 **이름**과 실패 **유형**도 언급한다
- 로깅 기능을 사용한다면 catch 블록에서 오류를 기록하도록 **충분한 정보를 넘겨준다**

---

## 6. 호출자를 고려해 예외 클래스를 정의하라

오류를 분류하는 방법은 수없이 많다. 오류가 발생한 위치, 유형(디바이스 실패, 네트워크 실패, 프로그래밍 오류 등) 등으로 분류할 수 있다. 하지만 애플리케이션에서 오류를 정의할 때 프로그래머에게 **가장 중요한 관심사는 오류를 잡아내는 방법**이 되어야 한다.

### 나쁜 예 — 외부 라이브러리의 예외를 그대로 노출

```java
ACMEPort port = new ACMEPort(12);

try {
    port.open();
} catch (DeviceResponseException e) {
    reportPortError(e);
    logger.log("Device response exception", e);
} catch (ATM1212UnlockedException e) {
    reportPortError(e);
    logger.log("Unlock exception", e);
} catch (GMXError e) {
    reportPortError(e);
    logger.log("Device response exception");
} finally {
    ...
}
```

중복이 심하다. 대다수 상황에서 오류를 처리하는 방식은 비교적 일정하다 — 오류를 기록하고, 프로그램을 계속 수행해도 좋은지 확인한다.

### 좋은 예 — 감싸기(wrapper) 클래스로 예외 유형 통합

```java
LocalPort port = new LocalPort(12);

try {
    port.open();
} catch (PortDeviceFailure e) {
    reportError(e);
    logger.log(e.getMessage(), e);
} finally {
    ...
}
```

```java
public class LocalPort {
    private ACMEPort innerPort;

    public LocalPort(int portNumber) {
        innerPort = new ACMEPort(portNumber);
    }

    public void open() {
        try {
            innerPort.open();
        } catch (DeviceResponseException e) {
            throw new PortDeviceFailure(e);
        } catch (ATM1212UnlockedException e) {
            throw new PortDeviceFailure(e);
        } catch (GMXError e) {
            throw new PortDeviceFailure(e);
        }
    }
    ...
}
```

### 외부 API 감싸기의 장점

| 장점 | 설명 |
|---|---|
| **의존성 감소** | 외부 라이브러리와 프로그램 사이의 의존성이 크게 줄어든다 |
| **교체 용이** | 나중에 다른 라이브러리로 갈아타도 비용이 적다 |
| **테스트 용이** | 감싸기 클래스에서 테스트 코드를 넣어주는 방법으로 테스트하기 쉬워진다 |
| **자유로운 API 설계** | 특정 업체의 API 설계 방식에 발목 잡히지 않는다 |

> **핵심 통찰**: 실제로 외부 API를 사용할 때는 **감싸기 기법이 최선**이다. 흔히 예외 클래스가 하나만 있어도 충분한 코드가 많다. 예외 클래스에 포함된 정보로 오류를 구분해도 괜찮은 경우가 그렇다.

---

## 7. 정상 흐름을 정의하라

앞 절의 지침을 충실히 따르면 비즈니스 논리와 오류 처리가 잘 분리된다. 하지만 때로는 **중단이 적합하지 않을 때**도 있다.

```java
// 나쁜 예 — 예외가 논리를 따라가기 어렵게 만든다
try {
    MealExpenses expenses = expenseReportDAO.getMeals(employee.getID());
    m_total += expenses.getTotal();
} catch (MealExpensesNotFound e) {
    m_total += getMealPerDiem();
}
```

식비를 비용으로 청구했다면 직원이 청구한 식비를 총계에 더하고, 청구하지 않았다면 일일 기본 식비를 더한다. 하지만 예외가 논리를 따라가기 어렵게 만든다.

```java
// 좋은 예 — 특수 사례 패턴으로 간결하게
MealExpenses expenses = expenseReportDAO.getMeals(employee.getID());
m_total += expenses.getTotal();
```

`ExpenseReportDAO`를 고쳐 언제나 `MealExpense` 객체를 반환한다. 청구한 식비가 없다면 일일 기본 식비를 반환하는 `MealExpense` 객체를 반환한다:

```java
public class PerDiemMealExpenses implements MealExpenses {
    public int getTotal() {
        // 기본값으로 일일 기본 식비를 반환한다.
    }
}
```

이를 **특수 사례 패턴(Special Case Pattern)**(*Special Case Pattern — Martin Fowler의 『리팩터링』에서 소개된 패턴으로, Null Object 패턴의 일반화된 형태다.*)이라 부른다. 클래스를 만들거나 객체를 조작해 특수 사례를 처리하는 방식이다. 클라이언트 코드가 예외적인 상황을 처리할 필요가 없어진다.

---

## 8. null을 반환하지 마라

흔히 저지르는 실수 중 첫째가 **null을 반환하는 습관**이다.

```java
// 나쁜 예 — null 확인이 누락되기 쉽다
public void registerItem(Item item) {
    if (item != null) {
        ItemRegistry registry = peristentStore.getItemRegistry();
        if (registry != null) {
            Item existing = registry.getItem(item.getID());
            if (existing.getBillingPeriod().hasRetailOwner()) {
                existing.register(item);
            }
        }
    }
}
```

위 코드에서 둘째 행에 null 확인이 빠졌다. `persistentStore`가 null이라면 `NullPointerException`이 발생한다. 문제는 null 확인이 누락된 것이 아니라 **null 확인이 너무 많다**는 점이다.

**해결책**: 메서드에서 null을 반환하고픈 유혹이 든다면 그 대신 **예외를 던지거나 특수 사례 객체를 반환**한다.

```java
// 나쁜 예 — null 반환 후 확인
List<Employee> employees = getEmployees();
if (employees != null) {
    for (Employee e : employees) {
        totalPay += e.getPay();
    }
}
```

```java
// 좋은 예 — 빈 리스트 반환
List<Employee> employees = getEmployees();
for (Employee e : employees) {
    totalPay += e.getPay();
}

public List<Employee> getEmployees() {
    if ( .. 직원이 없다면 .. )
        return Collections.emptyList();
}
```

코드가 깔끔해질 뿐더러 `NullPointerException`이 발생할 가능성도 줄어든다.

---

## 9. null을 전달하지 마라

메서드에서 null을 반환하는 방식도 나쁘지만 메서드로 **null을 전달하는 방식은 더 나쁘다.**

```java
public class MetricsCalculator {
    public double xProjection(Point p1, Point p2) {
        return (p2.x - p1.x) * 1.5;
    }
}
```

누군가 `calculator.xProjection(null, new Point(12, 13))`을 호출하면 `NullPointerException`이 발생한다.

### 대안 1 — 새로운 예외 유형

```java
public double xProjection(Point p1, Point p2) {
    if (p1 == null || p2 == null) {
        throw InvalidArgumentException(
            "Invalid argument for MetricsCalculator.xProjection");
    }
    return (p2.x - p1.x) * 1.5;
}
```

`NullPointerException`보다는 조금 나을지도 모르겠다. 하지만 `InvalidArgumentException`을 잡아내는 처리기가 필요하다.

### 대안 2 — assert 문

```java
public double xProjection(Point p1, Point p2) {
    assert p1 != null : "p1 should not be null";
    assert p2 != null : "p2 should not be null";
    return (p2.x - p1.x) * 1.5;
}
```

문서화가 잘 되어 코드 읽기는 편하지만 문제를 해결하지는 못한다.

> **핵심 통찰**: 대다수 프로그래밍 언어는 호출자가 실수로 넘기는 null을 적절히 처리하는 방법이 없다. 그렇다면 **애초에 null을 넘기지 못하도록 금지하는 정책이 합리적**이다.

---

## 오류 처리 기법 종합

| # | 기법 | 핵심 |
|---|---|---|
| 1 | 오류 코드보다 예외 사용 | 논리와 오류 처리를 분리 |
| 2 | try-catch-finally 먼저 작성 | 트랜잭션 범위 정의 |
| 3 | 미확인 예외 사용 | OCP 위반 방지, 캡슐화 유지 |
| 4 | 예외에 의미 제공 | 원인과 위치 추적 용이 |
| 5 | 호출자 고려해 예외 클래스 정의 | 감싸기(wrapper) 클래스 활용 |
| 6 | 정상 흐름 정의 | 특수 사례 패턴(Special Case Pattern) |
| 7 | null 반환 금지 | 예외 또는 특수 사례 객체 반환 |
| 8 | null 전달 금지 | 정책으로 금지 |

---

## 요약

- **오류 처리를 프로그램 논리와 분리**하면 튼튼하고 깨끗한 코드를 작성할 수 있다
- **오류 코드 대신 예외**를 사용하라 — 비즈니스 로직과 오류 처리 로직이 뒤섞이지 않는다
- **try-catch-finally 문부터 작성**하라 — TDD 방식으로 예외 처리를 구현하면 트랜잭션 본질을 유지하기 쉽다
- **미확인(unchecked) 예외를 사용**하라 — 확인된 예외는 OCP를 위반하고 캡슐화를 깨뜨린다
- **외부 API는 감싸기(wrapper) 클래스**로 처리하라 — 의존성 감소, 테스트 용이, API 설계 자유
- **특수 사례 패턴**으로 정상 흐름을 정의하라 — 예외적 상황을 클래스가 캡슐화한다
- **null을 반환하지도, 전달하지도 마라** — 빈 컬렉션이나 특수 사례 객체를 반환하라
- 깨끗한 코드는 읽기도 좋아야 하지만 **안정성도 높아야 한다** — 이 둘은 상충하는 목표가 아니다

---

## 다른 챕터와의 관계

- **← Chapter 3 (함수)**: "한 가지를 하라" 원칙이 try-catch 블록의 분리 전략과 직접 연결된다 — try 블록 안의 함수는 하나의 작업만 수행해야 한다
- **← Chapter 6 (객체와 자료 구조)**: 감싸기(wrapper) 클래스로 외부 API의 예외를 캡슐화하는 기법은 자료 추상화 원칙의 확장이다
- **→ Chapter 8 (경계)**: 외부 API 감싸기 기법이 경계에서의 코드 관리 전략으로 확장된다
- **→ Chapter 9 (단위 테스트)**: try-catch-finally 문을 TDD로 구현하는 방식이 단위 테스트 작성의 기본 패턴이다
- **→ Chapter 17 (냄새와 휴리스틱)**: null 반환, 오류 코드 사용 등이 구체적인 코드 냄새로 체계화된다
