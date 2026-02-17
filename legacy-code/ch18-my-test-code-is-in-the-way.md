# Chapter 18: 테스트 코드가 방해를 한다 (My Test Code Is in the Way)

## 핵심 질문

테스트 코드가 프로덕션 코드와 뒤섞여 방해가 될 때, 어떻게 하면 테스트의 이점을 유지하면서도 프로덕션 코드를 깔끔하게 관리할 수 있는가?

---

## 1. 테스트 코드가 "방해"가 되는 상황

레거시 코드에 테스트를 추가하다 보면, 어느 시점에서 테스트 코드 자체가 프로덕션 코드를 어지럽히는 것처럼 느껴지는 상황이 발생한다. 이 장에서는 테스트 코드가 프로덕션 코드에 영향을 미치는 여러 가지 방식을 다루고, 이를 관리하는 전략을 제시한다.

### 1.1 흔히 발생하는 문제들

테스트 코드가 "방해"가 된다고 느끼는 대표적인 상황은 다음과 같다:

| 문제 | 설명 |
|------|------|
| **소스 디렉토리 혼재** | 테스트 파일과 프로덕션 파일이 같은 디렉토리에 뒤섞여 있어 탐색이 어렵다 |
| **배포 크기 증가** | 테스트 코드가 프로덕션 빌드에 포함되어 배포 아티팩트가 불필요하게 커진다 |
| **접근 제어 완화** | 테스트를 위해 `private`을 `protected`나 `public`으로 바꿔야 하는 경우가 생긴다 |
| **테스트 전용 클래스의 존재** | Testing Subclass, Fake 객체 등이 프로덕션 코드 사이에 존재한다 |
| **코드 탐색 혼란** | IDE에서 클래스를 검색할 때 테스트 클래스가 함께 나타나 혼란을 준다 |

이런 문제들은 테스트를 처음 도입하는 팀에서 특히 자주 논의된다. "테스트를 추가하는 것은 좋지만, 이렇게 코드가 지저분해져도 괜찮은가?"라는 의문이 생기는 것이다.

---

## 2. 테스트 코드와 프로덕션 코드의 분리 전략

테스트 코드와 프로덕션 코드를 물리적으로 분리하는 것은 대부분의 현대적 프로젝트에서 표준적인 관행이다. 다양한 분리 전략이 존재하며, 각각의 장단점이 있다.

### 2.1 별도 소스 디렉토리 사용

가장 널리 사용되는 방법은 프로덕션 코드와 테스트 코드를 별도의 소스 디렉토리에 두는 것이다.

```
project/
├── src/
│   └── main/
│       └── com/
│           └── example/
│               ├── Order.java
│               └── OrderProcessor.java
└── src/
    └── test/
        └── com/
            └── example/
                ├── OrderTest.java
                └── OrderProcessorTest.java
```

이 구조의 장점:

- **명확한 물리적 분리**: 프로덕션 코드와 테스트 코드가 완전히 다른 디렉토리 트리에 있다.
- **빌드 시 제외 용이**: 빌드 도구(Maven, Gradle 등)에서 `src/test`를 프로덕션 빌드에서 쉽게 제외할 수 있다.
- **IDE 지원**: 대부분의 IDE가 이 구조를 기본적으로 지원한다.

### 2.2 같은 패키지, 다른 디렉토리

Java와 같은 언어에서 특히 유용한 방법이다. 테스트 클래스를 프로덕션 클래스와 **같은 패키지**에 두되, **물리적으로 다른 디렉토리**에 배치한다.

```
src/main/com/example/   ← 프로덕션 코드
src/test/com/example/   ← 테스트 코드 (같은 패키지)
```

이 방식의 핵심 이점은 **패키지 수준 접근(package-private access)** 을 활용할 수 있다는 것이다. Java에서 접근 제어자를 명시하지 않으면 같은 패키지 내의 클래스만 접근할 수 있다. 테스트 클래스가 같은 패키지에 있으므로, `private`을 `public`으로 바꾸지 않고도 패키지 수준의 메서드나 필드에 접근할 수 있다.

```java
// src/main/com/example/Order.java
package com.example;

public class Order {
    private List<Item> items = new ArrayList<>();

    // package-private: 같은 패키지의 테스트에서 접근 가능
    List<Item> getItems() {
        return Collections.unmodifiableList(items);
    }

    public void addItem(Item item) {
        items.add(item);
    }
}
```

```java
// src/test/com/example/OrderTest.java
package com.example;  // 같은 패키지!

public class OrderTest {
    @Test
    public void addItemIncreasesItemCount() {
        Order order = new Order();
        order.addItem(new Item("Widget"));

        // package-private 메서드에 접근 가능
        assertEquals(1, order.getItems().size());
    }
}
```

### 2.3 빌드 시 테스트 코드 제외

어떤 분리 전략을 사용하든, 프로덕션 빌드에서 테스트 코드를 제외하는 것이 중요하다. 이를 위한 방법들:

- **빌드 스크립트에서 제외**: Maven, Gradle, Ant 등의 빌드 도구에서 테스트 소스를 프로덕션 빌드 타겟에서 제외한다.
- **조건부 컴파일**: C/C++에서는 전처리기 지시문을 사용하여 테스트 코드를 조건부로 포함/제외할 수 있다.
- **별도 프로젝트/모듈**: 테스트를 완전히 별도의 프로젝트나 모듈로 분리한다.

```xml
<!-- Maven의 경우, 기본적으로 src/test는 프로덕션 JAR에 포함되지 않음 -->
<build>
    <sourceDirectory>src/main/java</sourceDirectory>
    <testSourceDirectory>src/test/java</testSourceDirectory>
</build>
```

> **핵심 통찰**: 테스트 코드의 물리적 분리는 중요하지만, 이것이 테스트 작성을 막는 장벽이 되어서는 안 된다. 분리 구조가 아직 갖추어지지 않았더라도, 일단 테스트를 작성하고 나중에 분리하는 것이 테스트 없이 남겨두는 것보다 훨씬 낫다.

---

## 3. 테스트 서브클래스(Testing Subclass)의 영향

Testing Subclass는 이 책에서 반복적으로 등장하는 핵심 기법이다. 테스트하기 어려운 클래스의 문제적 의존성을 오버라이드하기 위해 서브클래스를 만드는 방법이다. 하지만 이 테스트용 서브클래스가 프로덕션 코드에 영향을 줄 수 있다.

### 3.1 Testing Subclass란

```java
// 프로덕션 코드
public class PaymentProcessor {
    public void processPayment(Payment payment) {
        // 복잡한 비즈니스 로직
        validatePayment(payment);
        ChargeResult result = chargeCard(payment);
        sendReceipt(result);
    }

    // 외부 신용카드 시스템에 의존
    protected ChargeResult chargeCard(Payment payment) {
        return creditCardGateway.charge(payment);
    }

    // 이메일 시스템에 의존
    protected void sendReceipt(ChargeResult result) {
        emailService.send(result.getReceipt());
    }
}
```

```java
// 테스트 전용 서브클래스
public class TestingPaymentProcessor extends PaymentProcessor {
    public ChargeResult chargeResult = new ChargeResult(true);
    public boolean receiptSent = false;

    @Override
    protected ChargeResult chargeCard(Payment payment) {
        // 실제 신용카드 게이트웨이를 호출하지 않음
        return chargeResult;
    }

    @Override
    protected void sendReceipt(ChargeResult result) {
        // 실제 이메일을 보내지 않음
        receiptSent = true;
    }
}
```

### 3.2 프로덕션 코드에 미치는 영향

Testing Subclass를 사용하면 프로덕션 코드에 다음과 같은 변경이 필요할 수 있다:

| 변경 사항 | 이유 |
|-----------|------|
| `private` → `protected` | 서브클래스에서 오버라이드하려면 `protected` 이상이어야 한다 |
| 메서드 추출 | 의존성이 있는 부분을 별도 메서드로 분리하여 오버라이드 가능하게 만든다 |
| `final` 키워드 제거 | `final` 클래스나 메서드는 서브클래싱/오버라이드할 수 없다 |

이런 변경은 프로덕션 코드의 캡슐화를 약간 약화시킨다. 이 트레이드오프에 대해서는 다음 섹션에서 자세히 다룬다.

### 3.3 Testing Subclass의 배치

Testing Subclass를 어디에 둘 것인가도 중요한 문제다:

- **테스트 디렉토리에 배치** (권장): 프로덕션 빌드에 포함되지 않으며, 테스트 코드임이 명확하다.
- **프로덕션 코드와 같은 디렉토리에 배치** (비권장): 배포 시 불필요한 코드가 포함될 수 있다.

---

## 4. 테스트를 위해 접근성을 완화하는 것에 대한 논의

이 장에서 가장 중요하고 논쟁적인 주제다. 테스트를 작성하기 위해 캡슐화를 깨는 것이 정당한가?

### 4.1 private에서 protected로 변경하기

테스트를 위해 `private` 메서드를 `protected`로 바꾸는 것은 레거시 코드 작업에서 매우 흔한 일이다. 이에 대해 두 가지 상반된 시각이 존재한다.

**반대 의견: 캡슐화 위반**

```java
// 원래 코드: 내부 구현이 완전히 숨겨져 있음
public class Account {
    private double balance;

    private void applyInterest() {
        balance *= 1.05;
    }

    public void monthlyUpdate() {
        applyInterest();
        // ... 기타 월간 처리
    }
}
```

`applyInterest()`를 `protected`로 바꾸면:
- 서브클래스에서 이 메서드를 오버라이드할 수 있게 된다.
- 내부 구현의 세부사항이 상속 계층에 노출된다.
- 향후 다른 개발자가 실수로 이 메서드를 오버라이드하여 예상치 못한 동작을 만들 수 있다.

**찬성 의견: 실용적 트레이드오프**

Feathers는 이에 대해 매우 실용적인 입장을 취한다:

> **테스트가 없는 것보다 캡슐화를 약간 깨는 것이 낫다.**

이 말은 단순한 타협이 아니다. 다음과 같은 논리가 뒷받침한다:

1. **캡슐화의 목적**: 캡슐화의 궁극적 목적은 코드를 안전하게 변경할 수 있게 만드는 것이다. 그런데 테스트가 없으면 어떤 변경도 안전하지 않다.
2. **실질적 위험 비교**: `private`을 `protected`로 바꾸는 것의 위험(누군가 잘못 오버라이드할 수 있음)과 테스트가 없는 것의 위험(어떤 변경이든 기존 동작을 깨뜨릴 수 있음)을 비교하면, 후자가 압도적으로 크다.
3. **점진적 개선**: 테스트를 추가한 후, 더 나은 설계로 리팩토링하여 캡슐화를 복원할 수 있다. 하지만 테스트가 없으면 리팩토링조차 안전하게 할 수 없다.

### 4.2 캡슐화를 깨는 것에 대한 트레이드오프

Feathers는 캡슐화에 대해 더 넓은 관점을 제시한다:

| 관점 | 테스트 없는 캡슐화 | 캡슐화를 약간 깬 + 테스트 |
|------|-------------------|------------------------|
| **변경 안전성** | 매우 낮음 | 높음 |
| **코드 이해** | 표면적으로 깔끔해 보임 | 테스트가 동작을 문서화함 |
| **리팩토링 가능성** | 위험해서 시도 불가 | 안전하게 리팩토링 가능 |
| **장기적 코드 품질** | 계속 악화 | 점진적 개선 가능 |

> 캡슐화는 중요하다. 하지만 캡슐화라는 이름 뒤에 숨어서 테스트를 작성하지 않는 것은, 미래의 자신과 동료에게 더 큰 부담을 지우는 것이다.

### 4.3 접근성 완화의 구체적 기법들

상황에 따라 선택할 수 있는 여러 기법이 있다:

**기법 1: protected 메서드로 추출**

```java
// Before: 테스트하기 어려운 코드
public class ReportGenerator {
    public Report generate() {
        // ... 로직 ...
        Connection conn = DriverManager.getConnection(DB_URL);
        ResultSet rs = conn.executeQuery(sql);
        // ... 결과 처리 ...
    }
}

// After: DB 접근 부분을 protected 메서드로 추출
public class ReportGenerator {
    public Report generate() {
        // ... 로직 ...
        ResultSet rs = executeQuery(sql);
        // ... 결과 처리 ...
    }

    protected ResultSet executeQuery(String sql) {
        Connection conn = DriverManager.getConnection(DB_URL);
        return conn.executeQuery(sql);
    }
}
```

**기법 2: 언어별 접근 제어 활용**

- **Java**: 패키지-프라이빗(default) 접근 제어자를 사용하면 같은 패키지의 테스트에서 접근 가능하면서도 다른 패키지에서의 접근은 차단된다.
- **C#**: `internal` 접근 제어자와 `InternalsVisibleTo` 어트리뷰트를 사용하면 특정 테스트 어셈블리에만 접근을 허용할 수 있다.
- **C++**: `friend` 선언을 사용하여 테스트 클래스에 접근 권한을 부여할 수 있다.

```csharp
// C#에서 InternalsVisibleTo 사용
[assembly: InternalsVisibleTo("MyProject.Tests")]

public class OrderProcessor {
    // internal: 프로덕션 코드에서는 접근 불가, 테스트에서만 접근 가능
    internal void ValidateOrder(Order order) {
        // ...
    }
}
```

### 4.4 판단 기준

접근성을 완화할지 결정할 때 다음을 고려한다:

1. **테스트 가능성이 절대적으로 우선한다**: 테스트를 작성할 수 없는 상태가 가장 위험하다.
2. **가능한 최소한으로 완화한다**: `private` → `protected`가 가능하면 `public`까지 갈 필요 없다.
3. **언어의 접근 제어 기능을 최대한 활용한다**: Java의 패키지 접근, C#의 `InternalsVisibleTo` 등.
4. **나중에 다시 조일 수 있다**: 테스트가 확보되면 더 나은 설계로 리팩토링하여 캡슐화를 복원할 수 있다.

---

## 5. 클래스 네이밍 규칙과 테스트 코드 조직

테스트 코드를 체계적으로 관리하려면 일관된 네이밍 규칙이 필요하다.

### 5.1 테스트 클래스 네이밍

일반적인 규칙은 프로덕션 클래스 이름에 접미사나 접두사를 붙이는 것이다:

| 패턴 | 예시 | 비고 |
|------|------|------|
| `클래스명Test` | `OrderTest` | 가장 일반적 |
| `클래스명Tests` | `OrderTests` | 복수형 사용 |
| `Test클래스명` | `TestOrder` | 접두사 방식 |

### 5.2 Testing Subclass 네이밍

Testing Subclass의 경우, 이것이 테스트 전용 클래스임을 명확히 나타내는 이름을 사용해야 한다:

| 패턴 | 예시 | 비고 |
|------|------|------|
| `Testing클래스명` | `TestingPaymentProcessor` | 테스트 전용임이 명확 |
| `Fake클래스명` | `FakePaymentProcessor` | Fake 객체임을 명시 |

### 5.3 테스트 코드 조직 원칙

- **프로덕션 클래스와 1:1 매핑**: 각 프로덕션 클래스에 대응하는 테스트 클래스를 하나 만든다.
- **같은 패키지 구조 유지**: 테스트 디렉토리에서도 프로덕션 코드와 동일한 패키지 구조를 사용한다.
- **테스트 유틸리티 클래스는 별도 관리**: Fake 객체, Testing Subclass, 테스트 헬퍼 등은 테스트 디렉토리 내에서 별도로 관리한다.

```
src/test/
├── com/example/
│   ├── OrderTest.java                    ← Order에 대한 테스트
│   ├── OrderProcessorTest.java           ← OrderProcessor에 대한 테스트
│   └── testutil/
│       ├── TestingPaymentProcessor.java  ← Testing Subclass
│       └── FakeEmailService.java         ← Fake 객체
```

---

## 요약

- 테스트 코드가 프로덕션 코드와 뒤섞이면 탐색, 빌드, 배포 등에서 문제가 발생할 수 있다.
- **별도 소스 디렉토리**(src/main, src/test)를 사용하는 것이 가장 효과적인 분리 전략이다.
- **같은 패키지, 다른 디렉토리** 구조를 사용하면 패키지 수준 접근을 활용하여 캡슐화를 최소한으로 깨면서 테스트를 작성할 수 있다.
- Testing Subclass는 유용한 기법이지만, `private` → `protected` 같은 접근성 변경이 필요할 수 있다.
- **"테스트가 없는 것보다 캡슐화를 약간 깨는 것이 낫다"** 는 것이 Feathers의 핵심 메시지다.
- 테스트 가능성과 캡슐화 사이의 트레이드오프에서, 테스트가 없는 상태가 가장 위험하다.
- 일관된 네이밍 규칙과 디렉토리 구조로 테스트 코드를 체계적으로 관리해야 한다.
- 캡슐화를 깨더라도 테스트를 확보한 후, 나중에 더 나은 설계로 리팩토링하여 캡슐화를 복원할 수 있다.

---

## 다음 챕터와의 연결

Chapter 19 **"내 프로젝트는 객체 지향이 아니다 (My Project Is Not Object Oriented)"** 에서는 C, COBOL 같은 절차적 언어로 작성된 코드에서도 Seam을 찾고 의존성을 끊어 테스트를 작성할 수 있는 기법들을 소개한다. Link Seam, Preprocessing Seam 등 절차적 코드만의 고유한 접근법을 살펴본다.
