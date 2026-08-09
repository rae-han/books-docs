# Chapter 4: 봉합 모델 (The Seam Model)

## 핵심 질문

코드를 직접 편집하지 않고도 프로그램의 동작을 변경할 수 있는 지점은 어디인가? 그리고 어떤 종류의 seam이 레거시 코드 작업에 가장 유용한가?

---

## 1. Seam(이음새)의 정의

### 1.1 Seam이란 무엇인가

Feathers는 **Seam(이음새)** 을 다음과 같이 정의한다:

> **Seam은 해당 위치의 코드를 편집하지 않고도 프로그램의 동작을 변경할 수 있는 지점이다.**

이 정의에서 핵심은 **"코드를 편집하지 않고도(without editing in that place)"** 라는 부분이다. Seam은 코드 안에 이미 존재하는 "틈새"로, 이 틈새를 통해 프로그램의 동작을 바꿀 수 있다.

### 1.2 왜 Seam이 중요한가

레거시 코드에서 테스트를 작성하려면 의존성을 깨뜨려야 한다. 의존성을 깨뜨린다는 것은 **프로그램의 특정 동작을 다른 동작으로 교체**하는 것이다 (예: 실제 DB 연결 대신 가짜 객체 사용). Seam은 바로 이 **교체가 가능한 지점**이다.

Seam을 이해하면:

- 기존 코드에서 **테스트를 위한 교체 지점**을 찾아낼 수 있다.
- 코드를 최소한만 변경하여 **새로운 교체 지점을 만들 수** 있다.
- 각 상황에 **가장 적절한 의존성 교체 전략**을 선택할 수 있다.

### 1.3 Enabling Point (활성화 지점)

모든 seam에는 **Enabling Point**가 있다. Enabling Point란 **어떤 seam에서 어떤 동작을 사용할지 결정하는 지점**이다.

Seam과 Enabling Point는 항상 쌍으로 존재한다:

```
Seam: 동작을 교체할 수 있는 지점
Enabling Point: 어떤 동작을 사용할지 선택하는 지점
```

각 seam 유형마다 Enabling Point의 위치와 형태가 다르다. 이것이 seam을 분류하는 기준이 된다.

---

## 2. Preprocessing Seam (전처리 Seam)

### 2.1 개념

**Preprocessing Seam**은 C/C++의 전처리기(preprocessor)를 이용한 seam이다. C/C++에서는 컴파일 전에 전처리기가 소스 코드를 변환하는데, 이 단계에서 동작을 교체할 수 있다.

### 2.2 예시: #include를 이용한 Seam

다음과 같은 C 코드가 있다고 하자:

```c
#include "db_connection.h"

void process_order(Order* order) {
    db_connection* conn = db_connect("production_db");
    db_execute(conn, "INSERT INTO orders ...");
    db_close(conn);
}
```

이 코드를 테스트하려면 실제 DB 연결이 필요하다. 하지만 `#include`는 **Preprocessing Seam**이다.

**Enabling Point**: 컴파일러에게 전달하는 include 경로

테스트 시 다른 경로에 `db_connection.h`를 만들어두고, 컴파일러의 include 경로를 변경하면 된다:

```c
// 테스트용 db_connection.h (다른 디렉토리에 위치)
// 실제 DB 대신 메모리에 기록하는 가짜 구현

typedef struct { int dummy; } db_connection;

db_connection* db_connect(const char* db_name) {
    // 아무것도 하지 않고 더미 연결 반환
    static db_connection fake_conn;
    return &fake_conn;
}

void db_execute(db_connection* conn, const char* sql) {
    // SQL을 기록만 하고 실행하지 않음
    record_sql(sql);
}

void db_close(db_connection* conn) {
    // 아무것도 하지 않음
}
```

`process_order` 함수의 코드는 전혀 변경하지 않았지만, include 경로를 바꾸는 것만으로 동작이 교체된다.

### 2.3 매크로를 이용한 Seam

```c
#define REPORT_ERROR(msg) log_to_file(msg)

void process_data(Data* data) {
    if (data == NULL) {
        REPORT_ERROR("Null data received");
        return;
    }
    // ...
}
```

**Seam**: `REPORT_ERROR` 매크로 호출 지점
**Enabling Point**: `#define` 지시문

테스트 시 매크로를 재정의할 수 있다:

```c
// 테스트에서 매크로 재정의
#undef REPORT_ERROR
#define REPORT_ERROR(msg) last_error_message = msg

// 이제 process_data가 에러를 보고할 때
// 파일에 쓰는 대신 변수에 저장한다
```

### 2.4 Preprocessing Seam의 한계

| 장점 | 단점 |
|------|------|
| 소스 코드 변경 불필요 | C/C++에서만 사용 가능 |
| 강력한 교체 능력 | 코드가 혼란스러워질 수 있음 |
| | 전처리기 남용 시 디버깅이 매우 어려움 |
| | 컴파일 설정에 숨겨진 동작이 생김 |

> Feathers는 Preprocessing Seam이 가능한 선택지이긴 하지만, **최후의 수단**으로 사용해야 한다고 조언한다. 전처리기 기반의 seam은 코드의 흐름을 추적하기 어렵게 만든다.

---

## 3. Link Seam (링크 Seam)

### 3.1 개념

**Link Seam**은 프로그램의 링크(link) 단계에서 동작을 교체하는 seam이다. 대부분의 언어에서 코드는 컴파일 후 링크 과정을 거쳐 실행 파일이 된다. 이 과정에서 어떤 구현체를 연결할지 결정되는데, 이 연결을 바꾸면 동작을 교체할 수 있다.

### 3.2 예시: Java의 classpath

Java에서 클래스를 로드할 때 classpath를 참조한다. 같은 이름의 클래스가 여러 경로에 있다면, classpath 순서에 따라 어떤 클래스가 로드되는지 달라진다.

```java
// 프로덕션 코드
package com.example;

public class OrderProcessor {
    public void process(Order order) {
        PaymentGateway gateway = new PaymentGateway();
        gateway.charge(order.getAmount());
    }
}
```

**Seam**: `new PaymentGateway()` 호출 시 어떤 `PaymentGateway` 클래스가 로드되는지
**Enabling Point**: classpath 설정

테스트 시 classpath의 앞쪽에 테스트용 `PaymentGateway` 클래스를 배치하면:

```java
// 테스트용 PaymentGateway (동일한 패키지 이름)
package com.example;

public class PaymentGateway {
    private static double lastChargedAmount = 0;

    public void charge(double amount) {
        // 실제 결제하지 않고 기록만
        lastChargedAmount = amount;
    }

    public static double getLastChargedAmount() {
        return lastChargedAmount;
    }
}
```

`OrderProcessor`의 코드를 전혀 변경하지 않고도, classpath 조작만으로 테스트용 결제 게이트웨이를 사용하게 할 수 있다.

### 3.3 예시: C/C++의 라이브러리 링크

C/C++에서는 링크 단계에서 어떤 라이브러리(.a, .so, .lib, .dll)를 사용하는지 지정한다. 같은 인터페이스의 다른 구현체를 가진 라이브러리를 링크하면 동작이 교체된다.

```makefile
# 프로덕션 빌드
LIBS = -lnetwork -ldatabase

# 테스트 빌드
LIBS = -lfake_network -lfake_database
```

### 3.4 Link Seam의 한계

| 장점 | 단점 |
|------|------|
| 소스 코드 변경 불필요 | 같은 이름의 클래스/함수를 별도로 관리해야 함 |
| 언어/빌드 시스템 수준에서 동작 | 클래스 전체를 교체하므로 세밀한 제어가 어려움 |
| | 빌드 설정이 복잡해질 수 있음 |
| | 어떤 구현이 사용되는지 추적하기 어려움 |

> Link Seam은 Preprocessing Seam보다는 깔끔하지만, 여전히 **코드 밖의 설정에 의존**하므로 추적성(traceability)이 떨어진다.

---

## 4. Object Seam (객체 Seam)

### 4.1 개념

**Object Seam**은 객체지향 언어에서 **다형성(polymorphism)** 을 이용한 seam이다. 호출하는 메서드가 객체의 타입에 따라 다른 구현을 실행하는 특성을 활용한다.

### 4.2 기본 예시

다음 코드를 살펴보자:

```java
public class OrderProcessor {
    private MailSender mailSender;

    public OrderProcessor(MailSender mailSender) {
        this.mailSender = mailSender;
    }

    public void processOrder(Order order) {
        // 주문 처리 로직...
        // ...

        // 확인 메일 발송
        mailSender.send(order.getCustomerEmail(),
                       "주문이 처리되었습니다.");
    }
}
```

**Seam**: `mailSender.send()` 호출 지점. `mailSender`의 실제 타입에 따라 다른 `send` 구현이 실행된다.

**Enabling Point**: `OrderProcessor`의 생성자에서 어떤 `MailSender` 구현체를 전달하는지.

```java
// 프로덕션 코드
OrderProcessor processor = new OrderProcessor(new SmtpMailSender());

// 테스트 코드
FakeMailSender fakeSender = new FakeMailSender();
OrderProcessor processor = new OrderProcessor(fakeSender);
processor.processOrder(testOrder);

// 감지(Sensing): 메일이 올바르게 발송되었는지 확인
assertEquals("customer@test.com", fakeSender.getLastRecipient());
assertEquals("주문이 처리되었습니다.", fakeSender.getLastMessage());
```

### 4.3 상속과 오버라이드를 통한 Object Seam

때로는 인터페이스를 추출하지 않고도 **상속과 오버라이드**로 Object Seam을 만들 수 있다. 이것은 레거시 코드에서 특히 자주 사용되는 기법이다.

```java
public class ReportGenerator {
    public void generate(Data data) {
        // 데이터 처리...
        String report = formatReport(data);

        // 이 부분을 테스트에서 교체하고 싶다
        sendToServer(report);
    }

    protected void sendToServer(String report) {
        // 실제 서버에 전송하는 복잡한 코드
        HttpClient client = new HttpClient();
        client.post("https://reports.example.com", report);
    }
}
```

테스트에서는 하위 클래스를 만들어 `sendToServer`를 오버라이드한다:

```java
// 테스트 전용 하위 클래스
public class TestingReportGenerator extends ReportGenerator {
    private String lastSentReport = null;

    @Override
    protected void sendToServer(String report) {
        // 서버에 전송하지 않고 기록만
        lastSentReport = report;
    }

    public String getLastSentReport() {
        return lastSentReport;
    }
}
```

```java
// 테스트 코드
TestingReportGenerator generator = new TestingReportGenerator();
generator.generate(testData);

// 리포트 내용 확인 (Sensing)
assertNotNull(generator.getLastSentReport());
assertTrue(generator.getLastSentReport().contains("expected content"));
```

**Seam**: `sendToServer` 메서드 호출 지점
**Enabling Point**: 어떤 클래스의 인스턴스를 생성하는지 (테스트에서는 `TestingReportGenerator`를 생성)

### 4.4 Object Seam의 Enabling Point 정리

Object Seam에서 Enabling Point는 여러 형태를 가질 수 있다:

| Enabling Point 형태 | 설명 | 예시 |
|---------------------|------|------|
| **생성자 파라미터** | 의존 객체를 생성자로 주입 | `new Processor(fakeDb)` |
| **메서드 파라미터** | 의존 객체를 메서드 인자로 전달 | `process(data, fakeLogger)` |
| **Setter 메서드** | 의존 객체를 setter로 교체 | `processor.setDb(fakeDb)` |
| **인스턴스 생성** | 하위 클래스 인스턴스 사용 | `new TestProcessor()` |
| **팩토리 메서드 오버라이드** | 객체 생성 메서드를 오버라이드 | `createConnection()` 오버라이드 |

---

## 5. 왜 Object Seam이 가장 선호되는가

Feathers는 세 가지 seam 유형 중 **Object Seam이 가장 유용하고 가장 자주 사용된다**고 명확히 밝힌다. 그 이유는 다음과 같다:

### 5.1 세 가지 Seam 유형 비교

| 특성 | Preprocessing Seam | Link Seam | Object Seam |
|------|-------------------|-----------|-------------|
| **언어 지원** | C/C++만 | 대부분 언어 | 모든 OOP 언어 |
| **교체 단위** | 매크로, include 파일 | 클래스/모듈 전체 | 메서드 단위 |
| **Enabling Point 위치** | 전처리기 지시문, 빌드 설정 | classpath, 링크 설정 | **소스 코드 내부** |
| **추적성** | 매우 낮음 | 낮음 | **높음** |
| **세밀한 제어** | 가능하지만 혼란 | 제한적 | **매우 세밀** |
| **코드 가독성 영향** | 악화 | 무관 | **개선 가능** |
| **설계 개선 효과** | 없음 | 없음 | **있음** |

### 5.2 Object Seam의 핵심 장점

1. **Enabling Point가 소스 코드 안에 있다**: Preprocessing Seam과 Link Seam의 Enabling Point는 빌드 설정이나 전처리기 지시문에 숨어 있다. 반면 Object Seam의 Enabling Point는 소스 코드의 생성자, 메서드 파라미터, 팩토리 등에 명시적으로 드러난다. 코드를 읽는 사람이 "이 지점에서 동작이 교체될 수 있구나"라고 즉시 인식할 수 있다.

2. **설계를 개선한다**: Object Seam을 만드는 과정에서 자연스럽게 인터페이스 추출, 의존성 주입 등이 이루어진다. 이는 코드의 결합도를 낮추고 응집도를 높이는 좋은 설계 원칙과 정확히 일치한다. 테스트를 위한 작업이 곧 설계 개선 작업이 되는 것이다.

3. **언어 수준에서 지원된다**: 특별한 빌드 도구나 전처리기 없이, 언어의 기본 기능(상속, 인터페이스, 다형성)만으로 구현할 수 있다.

> **핵심 통찰**: Object Seam은 테스트 가능성과 좋은 설계를 동시에 달성한다. 테스트를 위해 Object Seam을 만들면, 그 코드는 더 유연하고 이해하기 쉬운 코드가 된다.

---

## 6. Seam을 찾고 활용하는 실무 가이드

### 6.1 기존 코드에서 Seam 찾기

레거시 코드를 테스트하려 할 때, 다음 순서로 seam을 찾아본다:

1. **Object Seam이 이미 존재하는가?**
   - 의존 객체가 파라미터로 전달되는가?
   - 가상(virtual) 메서드를 오버라이드할 수 있는가?
   - 인터페이스를 통해 접근하고 있는가?

2. **Object Seam을 만들 수 있는가?**
   - 인터페이스를 추출할 수 있는가?
   - 메서드를 오버라이드 가능하게 만들 수 있는가?
   - 의존 객체를 외부에서 주입받도록 변경할 수 있는가?

3. **다른 seam을 고려해야 하는가?**
   - Object Seam을 만들기가 너무 위험한 경우에만 Link Seam이나 Preprocessing Seam을 고려한다.

### 6.2 Seam 활용 시 주의사항

- **프로덕션 코드에서 seam을 악용하지 말라**: Seam은 테스트에서 동작을 교체하기 위한 것이지, 프로덕션 코드에서 "편법"으로 사용하기 위한 것이 아니다.
- **Enabling Point를 명확히 하라**: 어디서 동작이 결정되는지 모호하면, 코드를 이해하기 어려워진다.
- **가능한 한 Object Seam을 사용하라**: 다른 유형의 seam은 추적성이 떨어지고 유지보수가 어렵다.

---

## 요약

- **Seam(이음새)** 은 해당 위치의 코드를 편집하지 않고도 프로그램의 동작을 변경할 수 있는 지점이다.
- 모든 seam에는 어떤 동작을 사용할지 결정하는 **Enabling Point**가 있다.
- Seam은 세 가지 유형이 있다:
  - **Preprocessing Seam**: C/C++ 전처리기(`#include`, `#define`, 매크로)를 이용. Enabling Point는 전처리기 지시문이나 빌드 설정.
  - **Link Seam**: 링크 단계에서 다른 구현체로 교체(classpath, 라이브러리 경로 조작). Enabling Point는 빌드/링크 설정.
  - **Object Seam**: 객체지향의 다형성을 이용. Enabling Point는 소스 코드 내부(생성자, 메서드 파라미터 등).
- **Object Seam이 가장 선호**되는 이유: Enabling Point가 코드에 명시적으로 드러나고, 설계를 개선하며, 언어의 기본 기능만으로 구현 가능하다.
- 레거시 코드에서는 먼저 Object Seam을 찾거나 만들고, 불가능한 경우에만 다른 seam을 고려한다.

---

## 다음 챕터와의 연결

Chapter 5 **"도구 (Tools)"** 에서는 레거시 코드 작업을 돕는 자동화된 리팩토링 도구, Mock 객체 프레임워크, 단위 테스트 하네스(xUnit 계열), 통합 테스트 프레임워크(FIT, Fitnesse) 등 실무에서 사용하는 구체적인 도구들을 소개한다.
