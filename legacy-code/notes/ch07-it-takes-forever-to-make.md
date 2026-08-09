# Chapter 7: 코드 하나 바꾸는 데 왜 이리 오래 걸리지? (It Takes Forever to Make a Change)

## 핵심 질문

코드 변경에 시간이 오래 걸리는 근본 원인은 무엇이며, 의존성 구조를 어떻게 개선하면 변경 비용과 빌드 시간을 줄일 수 있는가?

---

## 1. 변경이 오래 걸리는 이유

레거시 코드에서 단순한 변경조차 오래 걸리는 이유는 크게 네 가지이다:

| 원인 | 설명 |
|------|------|
| **코드 이해에 시간이 오래 걸림** | 코드가 복잡하고, 문서가 없으며, 의도가 불명확함 |
| **빌드 시간이 오래 걸림** | 의존성이 많아서 작은 변경에도 대규모 재컴파일 발생 |
| **의존성이 복잡하게 얽혀 있음** | 하나의 변경이 예상치 못한 다른 부분에 영향 |
| **변경의 영향 범위를 파악하기 어려움** | 어디까지 영향을 미치는지 확신할 수 없음 |

이 장에서 Feathers는 특히 **의존성 문제**와 **빌드 시간** 문제에 집중한다. 왜냐하면 이 두 가지가 다른 문제들의 근본 원인인 경우가 많기 때문이다.

### 1.1 코드 이해의 어려움

코드를 이해하는 데 걸리는 시간은 **코드가 얼마나 명확한가**와 **한 번에 살펴봐야 하는 범위가 얼마나 넓은가**에 좌우된다.

- 하나의 클래스가 수천 줄이라면, 변경 지점을 찾는 것 자체가 큰 일이다.
- 하나의 메서드가 다른 20개의 클래스에 의존한다면, 그 메서드의 동작을 이해하려면 20개의 클래스를 모두 파악해야 한다.
- 이름이 모호하거나 책임이 불명확한 클래스/메서드는 코드 탐색 시간을 기하급수적으로 늘린다.

> 좋은 코드는 설명이 필요 없고, 나쁜 코드는 설명으로도 부족하다.

---

## 2. 의존성 문제의 구체적 양상

### 2.1 C++에서의 의존성 문제: 헤더 파일 의존성

C++의 빌드 시스템은 **헤더 파일 의존성**이 빌드 시간에 직접적으로 영향을 미친다.

```cpp
// Scheduler.h
#ifndef SCHEDULER_H
#define SCHEDULER_H

#include "Meeting.h"
#include "MailDaemon.h"
#include "Calendar.h"
#include "TimeZone.h"

class Scheduler {
public:
    void schedule(Meeting& meeting);
    void notify(MailDaemon& daemon);
    // ...
private:
    Calendar calendar;
    TimeZone timezone;
};

#endif
```

이 경우 `Scheduler.h`를 포함하는 모든 파일은 `Meeting.h`, `MailDaemon.h`, `Calendar.h`, `TimeZone.h`도 간접적으로 포함하게 된다. **헤더 파일 하나가 변경되면, 그것을 직접 또는 간접적으로 포함하는 모든 소스 파일이 재컴파일**된다.

대규모 C++ 프로젝트에서 이 문제는 심각하다:

```
Meeting.h 변경
  → Scheduler.h를 포함하는 모든 .cpp 파일 재컴파일
  → Scheduler.h를 포함하는 다른 헤더를 포함하는 모든 .cpp 파일도 재컴파일
  → 연쇄적 재컴파일 → 빌드 시간 수십 분~수 시간
```

### 2.2 Java에서의 의존성 문제: 컴파일 의존성

Java는 C++의 헤더 파일 문제는 없지만, **컴파일 의존성(compile dependency)** 문제는 여전히 존재한다.

```java
public class InvoiceUpdateResponder {
    private InvoiceUpdateServlet servlet;

    public InvoiceUpdateResponder(InvoiceUpdateServlet servlet) {
        this.servlet = servlet;
    }

    public String getContent() {
        Invoice invoice = servlet.getInvoice();
        // invoice 처리 로직...
    }
}
```

`InvoiceUpdateResponder`는 `InvoiceUpdateServlet`에 직접 의존한다. 이것은:
- `InvoiceUpdateServlet`이 변경되면 `InvoiceUpdateResponder`도 재컴파일되어야 한다.
- `InvoiceUpdateResponder`를 **테스트하려면 `InvoiceUpdateServlet` 객체가 필요**하다.
- `InvoiceUpdateServlet`은 서블릿 컨테이너에 의존하므로, 테스트 환경을 구성하기 어렵다.

---

## 3. 의존성을 줄이는 방법

### 3.1 인터페이스 추출 (Extract Interface)

인터페이스 추출은 **구체 클래스에 대한 의존성을 인터페이스에 대한 의존성으로 바꾸는** 기법이다.

**변경 전: 구체 클래스에 직접 의존**

```java
public class InvoiceUpdateResponder {
    private InvoiceUpdateServlet servlet;

    public InvoiceUpdateResponder(InvoiceUpdateServlet servlet) {
        this.servlet = servlet;
    }
}
```

**변경 후: 인터페이스에 의존**

```java
// 인터페이스 추출
public interface InvoiceUpdateSource {
    Invoice getInvoice();
}

// 기존 클래스가 인터페이스를 구현
public class InvoiceUpdateServlet implements InvoiceUpdateSource {
    public Invoice getInvoice() {
        // 실제 구현...
    }
}

// 인터페이스에 의존하도록 변경
public class InvoiceUpdateResponder {
    private InvoiceUpdateSource source;

    public InvoiceUpdateResponder(InvoiceUpdateSource source) {
        this.source = source;
    }

    public String getContent() {
        Invoice invoice = source.getInvoice();
        // invoice 처리 로직...
    }
}
```

이제 테스트에서는 **가짜 구현**을 주입할 수 있다:

```java
// 테스트용 가짜 구현
public class FakeInvoiceUpdateSource implements InvoiceUpdateSource {
    private Invoice invoice;

    public FakeInvoiceUpdateSource(Invoice invoice) {
        this.invoice = invoice;
    }

    public Invoice getInvoice() {
        return invoice;
    }
}

// 테스트 코드
public void testGetContent() {
    Invoice testInvoice = new Invoice(/* 테스트 데이터 */);
    InvoiceUpdateSource source = new FakeInvoiceUpdateSource(testInvoice);
    InvoiceUpdateResponder responder = new InvoiceUpdateResponder(source);

    String content = responder.getContent();
    assertEquals("expected content", content);
}
```

**인터페이스 추출의 효과:**

```
변경 전:
  InvoiceUpdateResponder → InvoiceUpdateServlet → (서블릿 컨테이너, HTTP 등)

변경 후:
  InvoiceUpdateResponder → InvoiceUpdateSource (인터페이스)
                                ↑
  InvoiceUpdateServlet ─────────┘  (구현)
  FakeInvoiceUpdateSource ──────┘  (테스트용)
```

### 3.2 구현체 추출 (Extract Implementer)

구현체 추출은 인터페이스 추출과 **반대 방향**으로 작동한다. 기존 클래스를 인터페이스로 바꾸고, 기존 구현을 새 클래스로 이동시킨다.

**절차:**

1. 기존 클래스의 **모든 메서드 시그니처를 인터페이스로 복사**한다.
2. 기존 클래스의 이름을 변경하고 (예: `Scheduler` → `ProductionScheduler`), 인터페이스에 원래 이름을 부여한다 (예: `Scheduler`).
3. 새로 이름이 바뀐 클래스가 **인터페이스를 구현(implements)** 하도록 선언한다.

```java
// 변경 전
public class Scheduler {
    public void schedule(Meeting meeting) { /* 실제 구현 */ }
    public void cancel(Meeting meeting) { /* 실제 구현 */ }
}
```

```java
// 변경 후
// 원래 이름을 인터페이스가 차지
public interface Scheduler {
    void schedule(Meeting meeting);
    void cancel(Meeting meeting);
}

// 기존 구현은 새 이름으로 이동
public class ProductionScheduler implements Scheduler {
    public void schedule(Meeting meeting) { /* 기존 구현 그대로 */ }
    public void cancel(Meeting meeting) { /* 기존 구현 그대로 */ }
}
```

**인터페이스 추출 vs 구현체 추출:**

| 기준 | 인터페이스 추출 | 구현체 추출 |
|------|----------------|-------------|
| **인터페이스 이름** | 새 이름 (예: `InvoiceUpdateSource`) | 기존 클래스 이름 유지 (예: `Scheduler`) |
| **기존 클래스 이름** | 변경 없음 | 새 이름 (예: `ProductionScheduler`) |
| **호출 코드 변경** | 타입 선언만 변경 | 객체 생성 코드만 변경 |
| **적합한 경우** | 기존 클래스 이름이 이미 충분히 구체적일 때 | 기존 클래스 이름이 추상적이어서 인터페이스 이름으로 적합할 때 |

### 3.3 C++에서의 의존성 줄이기

C++에서는 인터페이스 추출이 빌드 시간에 **극적인 효과**를 가져올 수 있다.

```cpp
// 변경 전: Scheduler.h - 많은 헤더를 포함
#include "Meeting.h"
#include "MailDaemon.h"
#include "Calendar.h"
#include "TimeZone.h"

class Scheduler {
    Calendar calendar;
    TimeZone timezone;
public:
    void schedule(Meeting& meeting);
    void notify(MailDaemon& daemon);
};
```

```cpp
// 변경 후: Scheduler.h - 순수 가상 클래스 (인터페이스)
class Meeting;   // 전방 선언만으로 충분
class MailDaemon;

class Scheduler {
public:
    virtual ~Scheduler() {}
    virtual void schedule(Meeting& meeting) = 0;
    virtual void notify(MailDaemon& daemon) = 0;
};
```

```cpp
// ProductionScheduler.h - 실제 구현
#include "Scheduler.h"
#include "Meeting.h"
#include "MailDaemon.h"
#include "Calendar.h"
#include "TimeZone.h"

class ProductionScheduler : public Scheduler {
    Calendar calendar;
    TimeZone timezone;
public:
    void schedule(Meeting& meeting) override;
    void notify(MailDaemon& daemon) override;
};
```

이제 `Scheduler.h`를 포함하는 파일들은 더 이상 `Calendar.h`나 `TimeZone.h`를 간접 포함하지 않는다. **헤더 의존성 체인이 끊긴다.**

---

## 4. 의존성 역전 (Dependency Inversion)

### 4.1 의존성 역전 원칙 (Dependency Inversion Principle, DIP)

> A. 고수준 모듈은 저수준 모듈에 의존해서는 안 된다. 둘 다 추상화에 의존해야 한다.
> B. 추상화는 세부 사항에 의존해서는 안 된다. 세부 사항이 추상화에 의존해야 한다.

이것은 Robert C. Martin이 정의한 SOLID 원칙의 D에 해당하며, Feathers가 이 장에서 의존성 문제의 근본적인 해결 방향으로 제시하는 원칙이다.

### 4.2 의존성 역전 전후 비교

**역전 전: 고수준이 저수준에 의존**

```
[비즈니스 로직] → [데이터 접근 계층] → [데이터베이스]
```

- `OrderProcessor`가 `MySQLDatabase`를 직접 참조한다.
- 데이터베이스를 바꾸려면 비즈니스 로직도 수정해야 한다.
- 비즈니스 로직을 단독으로 테스트할 수 없다.

```java
// 나쁜 예: 고수준이 저수준에 직접 의존
public class OrderProcessor {
    private MySQLDatabase database;

    public OrderProcessor() {
        this.database = new MySQLDatabase("connection-string");
    }

    public void processOrder(Order order) {
        database.executeQuery("INSERT INTO orders ...");
    }
}
```

**역전 후: 둘 다 추상화에 의존**

```
[비즈니스 로직] → [인터페이스] ← [데이터 접근 계층]
```

- `OrderProcessor`가 `Database` 인터페이스에 의존한다.
- `MySQLDatabase`도 `Database` 인터페이스를 구현한다.
- **의존성의 방향이 역전**되었다: 저수준 모듈이 고수준 모듈이 정의한 인터페이스에 의존한다.

```java
// 좋은 예: 추상화에 의존
public interface Database {
    void save(Order order);
}

public class MySQLDatabase implements Database {
    public void save(Order order) {
        // MySQL 구현
    }
}

public class OrderProcessor {
    private Database database;

    public OrderProcessor(Database database) {
        this.database = database;
    }

    public void processOrder(Order order) {
        database.save(order);
    }
}
```

### 4.3 빌드 의존성에 미치는 영향

의존성 역전은 **빌드 의존성의 방향도 역전**시킨다.

```
역전 전:
  OrderProcessor.java 컴파일 시 → MySQLDatabase.class 필요
  MySQLDatabase 변경 → OrderProcessor 재컴파일

역전 후:
  OrderProcessor.java 컴파일 시 → Database.class (인터페이스) 만 필요
  MySQLDatabase 변경 → OrderProcessor 재컴파일 불필요
```

대규모 프로젝트에서 이런 의존성 역전을 전체적으로 적용하면, 하나의 모듈을 변경할 때 **재컴파일해야 하는 범위가 획기적으로 줄어든다**.

---

## 5. 빌드 의존성과 물리적 구조의 중요성

### 5.1 패키지/모듈 구조

코드의 **물리적 구조** (파일과 디렉토리의 배치)가 의존성 관리에 중요한 역할을 한다. Feathers는 다음과 같은 구조적 원칙을 제안한다:

**나쁜 구조: 모든 것이 하나의 패키지에**

```
src/
  └── com/company/
        ├── OrderProcessor.java
        ├── MySQLDatabase.java
        ├── InvoiceServlet.java
        ├── EmailSender.java
        └── ... (수십~수백 개 파일)
```

**좋은 구조: 의존성 방향을 반영하는 패키지 분리**

```
src/
  └── com/company/
        ├── domain/              ← 고수준: 비즈니스 로직
        │     ├── OrderProcessor.java
        │     └── Database.java  ← 인터페이스
        ├── infrastructure/      ← 저수준: 구현 세부사항
        │     ├── MySQLDatabase.java
        │     └── EmailSender.java
        └── web/                 ← 프레젠테이션 계층
              └── InvoiceServlet.java
```

이렇게 구조화하면:
- `domain` 패키지는 **어디에도 의존하지 않는다** (인터페이스만 정의).
- `infrastructure`와 `web`은 `domain`에 의존한다.
- `domain`을 변경해도 **직접 영향받는 범위가 명확**하다.

### 5.2 빌드 시간 줄이기의 실전적 효과

Feathers는 다음과 같은 경험적 사실을 공유한다:

> 프로젝트의 평균 빌드 시간이 10초 이내로 줄어들면, 개발자의 작업 방식이 근본적으로 달라진다.

빌드가 빠르면:
- **더 자주 빌드하고 테스트**한다 → 오류를 빨리 발견한다.
- **더 작은 단위로 변경**한다 → 각 변경의 위험이 줄어든다.
- **실험을 두려워하지 않는다** → 더 나은 설계를 시도할 수 있다.

반대로, 빌드가 30분 이상 걸리면:
- 개발자는 **변경을 모아서 한꺼번에** 빌드한다 → 오류 원인 파악이 어렵다.
- **빌드 실패 시 되돌리기**가 힘들다.
- **리팩토링을 포기**한다 → 코드 품질 악화.

### 5.3 의존성 줄이기가 코드 이해에 미치는 효과

의존성을 줄이면 빌드 시간뿐 아니라 **코드 이해 시간도 줄어든다**:

- 인터페이스에 의존하면, 해당 클래스의 동작을 이해하기 위해 **구현 세부사항을 볼 필요가 없다**.
- 패키지가 잘 분리되어 있으면, **탐색 범위가 좁아진다**.
- 의존성이 적은 클래스는 **독립적으로 이해할 수 있다**.

---

## 6. 레거시 코드에서의 점진적 적용

한꺼번에 모든 의존성을 정리하는 것은 현실적이지 않다. Feathers는 **점진적 접근**을 권장한다:

1. **변경이 필요한 부분부터** 의존성을 끊는다.
2. 해당 부분에 **인터페이스를 추출**하고, 테스트를 작성한다.
3. 시간이 지나면 **자주 변경되는 부분에 자연스럽게 인터페이스가 모인다**.
4. 이 인터페이스들이 **시스템의 핵심 추상화 계층**을 형성한다.

```
시간 →
코드베이스:  [■■■■■■■■■■]  모든 것이 직접 의존
         →  [■■■■□□■■■■]  일부 인터페이스 추출
         →  [■■□□□□□■■■]  점점 더 많은 추상화
         →  [□□□□□□□□□□]  잘 구조화된 의존성 (이상적)

■ = 직접 의존  □ = 인터페이스를 통한 의존
```

---

## 요약

- 변경이 오래 걸리는 주요 원인은 **코드 이해의 어려움**, **빌드 시간**, **복잡한 의존성**, **영향 범위 파악 난이도**이다.
- C++에서는 **헤더 파일 의존성**이, Java에서는 **컴파일 의존성**이 빌드 시간과 변경 비용을 증가시킨다.
- **인터페이스 추출(Extract Interface)** 은 구체 클래스 의존성을 인터페이스 의존성으로 바꿔 의존성을 끊는다.
- **구현체 추출(Extract Implementer)** 은 기존 클래스를 인터페이스로 승격시키고, 구현을 새 클래스로 옮긴다.
- **의존성 역전 원칙(DIP)** 은 고수준 모듈이 저수준 모듈에 의존하지 않고, 둘 다 추상화에 의존하게 만든다.
- 물리적 패키지/모듈 구조가 빌드 의존성과 코드 이해 용이성에 직접적인 영향을 미친다.
- **빌드 시간을 줄이면 개발 방식 자체가 바뀐다**: 더 자주 테스트하고, 더 작은 단위로 변경하며, 리팩토링을 두려워하지 않게 된다.

---

## 다음 챕터와의 연결

Chapter 8 **"어떻게 기능을 추가할까? (How Do I Add a Feature?)"** 에서는 레거시 코드에서 TDD(Test-Driven Development)를 어떻게 적용하는지, 그리고 **Programming by Difference(차이에 의한 프로그래밍)** 를 활용해 기존 코드를 건드리지 않으면서 새 기능을 추가하는 방법을 소개한다.
