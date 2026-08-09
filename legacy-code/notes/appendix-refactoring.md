# 부록: Refactoring

## 핵심 질문

레거시 코드를 변경할 때 어떤 리팩토링 기법을 적용해야 하며, 각 기법은 어떤 절차로 안전하게 수행할 수 있는가?

---

## Martin Fowler의 "Refactoring"과의 관계

이 부록은 Michael Feathers의 "Working Effectively with Legacy Code" 전체에서 언급되는 주요 리팩토링 기법들의 참조 목록이다. 이 기법들의 대부분은 Martin Fowler의 저서 **"Refactoring: Improving the Design of Existing Code"**(1999)에서 처음 체계적으로 정리된 것이다.

Fowler의 책이 이미 잘 설계된 코드를 더 개선하는 데 초점을 맞추고 있다면, Feathers의 책은 **테스트가 없는 레거시 코드에서 이러한 리팩토링을 안전하게 수행하기 위한 전제 조건**을 만드는 데 집중한다. 즉, Feathers의 접근법은 다음과 같은 순서를 따른다:

1. 의존성 깨기(Dependency Breaking) 기법으로 코드를 테스트 가능한 상태로 만든다
2. 특성화 테스트(Characterization Test)를 작성하여 기존 동작을 포착한다
3. 안전망이 확보된 상태에서 Fowler의 리팩토링 기법을 적용한다

> Fowler의 리팩토링 카탈로그에 나오는 기법들은 이 책 전체에서 핵심 도구로 사용된다. 레거시 코드를 다룰 때 이 기법들을 이해하는 것은 필수적이다.

따라서 이 부록의 리팩토링 기법들을 충분히 이해하면, 본문의 의존성 깨기 기법들과 결합하여 레거시 코드를 체계적으로 개선할 수 있다.

---

## 리팩토링 기법 카탈로그

### 1. Extract Method (메서드 추출)

**설명**: 코드의 한 블록을 별도의 메서드로 추출하는 기법이다. 긴 메서드에서 논리적으로 구분되는 부분을 식별하고, 그 부분을 의미 있는 이름을 가진 새 메서드로 분리한다.

**적용 상황**:
- 메서드가 너무 길어서 이해하기 어려울 때
- 메서드 내에 주석으로 구분된 논리적 블록이 있을 때
- 동일한 코드 조각이 여러 곳에서 반복될 때
- 테스트하기 어려운 긴 메서드를 테스트 가능한 단위로 분해할 때
- Chapter 22(Monster Method)에서 특히 핵심적으로 활용됨

**절차**:
1. 추출하려는 코드 블록을 식별한다
2. 해당 블록에서 사용하는 지역 변수와 매개변수를 파악한다
3. 블록 내에서 수정되는 지역 변수가 있는지 확인한다 (있다면 반환값으로 처리하거나, 여러 개인 경우 추출을 재고한다)
4. 새 메서드를 생성하고, 필요한 변수들을 매개변수로 전달한다
5. 원래 위치의 코드를 새 메서드 호출로 교체한다
6. 컴파일 및 테스트한다

**예시**:

```java
// Before
void printOwing() {
    double outstanding = 0.0;
    // print banner
    System.out.println("**************************");
    System.out.println("***** Customer Owes ******");
    System.out.println("**************************");
    // calculate outstanding
    for (Order order : orders) {
        outstanding += order.getAmount();
    }
    // print details
    System.out.println("name: " + name);
    System.out.println("amount: " + outstanding);
}

// After
void printOwing() {
    printBanner();
    double outstanding = calculateOutstanding();
    printDetails(outstanding);
}

void printBanner() {
    System.out.println("**************************");
    System.out.println("***** Customer Owes ******");
    System.out.println("**************************");
}

double calculateOutstanding() {
    double outstanding = 0.0;
    for (Order order : orders) {
        outstanding += order.getAmount();
    }
    return outstanding;
}

void printDetails(double outstanding) {
    System.out.println("name: " + name);
    System.out.println("amount: " + outstanding);
}
```

**레거시 코드에서의 주의점**: 테스트가 없는 상태에서 Extract Method를 수행할 때는 **Sprout Method**(Chapter 6)나 **Wrap Method**(Chapter 6) 패턴과 결합하여 사용하는 것이 안전하다. 또한, IDE의 자동 리팩토링 기능을 사용하면 수동 실수를 크게 줄일 수 있다.

---

### 2. Rename Method / Rename Variable (메서드/변수 이름 변경)

**설명**: 메서드나 변수의 이름을 현재의 역할과 의미를 더 잘 전달하도록 변경하는 기법이다. 코드의 의도를 명확히 드러내는 가장 간단하면서도 효과적인 리팩토링 중 하나이다.

**적용 상황**:
- 메서드 이름이 실제 수행하는 동작을 정확히 설명하지 않을 때
- 변수 이름이 그 값의 의미를 충분히 전달하지 않을 때
- 코드를 읽는 사람이 이름만으로 의도를 파악할 수 없을 때
- Chapter 16(코드를 충분히 이해하지 못할 때)에서 코드 이해도를 높이는 수단으로 활용됨

**절차**:
1. 메서드/변수의 현재 역할을 정확히 파악한다
2. 역할을 잘 설명하는 새로운 이름을 결정한다
3. 해당 메서드/변수의 모든 참조 지점을 찾는다
4. 이름을 변경한다 (IDE의 Rename 기능을 사용하면 안전하다)
5. 컴파일 및 테스트한다

**예시**:

```java
// Before
double calc(int q, double p) {
    return q * p * 0.9;
}

// After
double calculateDiscountedTotal(int quantity, double unitPrice) {
    return quantity * unitPrice * 0.9;
}
```

**레거시 코드에서의 주의점**: 공개(public) 메서드의 이름을 변경하면 외부 호출자에게 영향을 줄 수 있다. 레거시 시스템에서는 모든 호출 지점을 파악하기 어려울 수 있으므로, IDE의 검색 기능을 활용하여 모든 참조를 확인해야 한다. 리플렉션(reflection)이나 문자열 기반 호출이 있는 경우 특히 주의가 필요하다.

---

### 3. Extract Class (클래스 추출)

**설명**: 하나의 클래스가 너무 많은 책임을 가지고 있을 때, 관련된 필드와 메서드를 묶어 새로운 클래스로 분리하는 기법이다. 단일 책임 원칙(Single Responsibility Principle)을 적용하는 대표적인 방법이다.

**적용 상황**:
- 클래스가 두 가지 이상의 명확히 구분되는 책임을 가질 때
- 클래스의 필드 일부가 항상 함께 사용될 때
- 클래스의 메서드 일부가 특정 필드만 사용할 때
- Chapter 20(클래스가 너무 클 때)에서 핵심적으로 다루어짐

**절차**:
1. 클래스에서 분리할 책임을 식별한다
2. 새 클래스를 생성한다
3. 원래 클래스에서 새 클래스로의 링크(필드)를 만든다
4. 관련 필드를 하나씩 새 클래스로 이동한다 (Move Field)
5. 관련 메서드를 하나씩 새 클래스로 이동한다 (Move Method)
6. 각 이동 후 컴파일 및 테스트한다
7. 양쪽 클래스의 인터페이스를 검토하고 정리한다

**예시**:

```java
// Before
class Employee {
    private String name;
    private String officeAreaCode;
    private String officeNumber;

    String getName() { return name; }
    String getOfficeAreaCode() { return officeAreaCode; }
    String getOfficeNumber() { return officeNumber; }
    String getFullPhoneNumber() {
        return "(" + officeAreaCode + ") " + officeNumber;
    }
}

// After
class Employee {
    private String name;
    private TelephoneNumber officeTelephone;

    String getName() { return name; }
    TelephoneNumber getOfficeTelephone() { return officeTelephone; }
}

class TelephoneNumber {
    private String areaCode;
    private String number;

    String getAreaCode() { return areaCode; }
    String getNumber() { return number; }
    String getFullNumber() {
        return "(" + areaCode + ") " + number;
    }
}
```

**레거시 코드에서의 주의점**: 거대한 클래스에서 책임을 분리할 때는 **기능 스케치(Feature Sketch)**와 **영향 스케치(Effect Sketch)**(Chapter 20)를 그려보면 어떤 필드와 메서드가 함께 묶이는지 시각적으로 파악할 수 있다. 한 번에 모든 것을 분리하려 하지 말고, 점진적으로 진행한다.

---

### 4. Move Method (메서드 이동)

**설명**: 메서드가 자신이 속한 클래스보다 다른 클래스의 기능을 더 많이 사용할 때, 해당 메서드를 더 적절한 클래스로 이동하는 기법이다.

**적용 상황**:
- 메서드가 자신의 클래스 필드보다 다른 클래스의 필드를 더 많이 참조할 때
- 기능 편향(Feature Envy) 코드 스멜이 감지될 때
- 클래스 간의 결합도를 줄이고 응집도를 높이고 싶을 때
- Extract Class를 수행하는 과정의 일부로 활용될 때

**절차**:
1. 이동할 메서드가 사용하는 모든 기능(필드, 메서드)을 확인한다
2. 소스 클래스의 하위 클래스나 상위 클래스에서 해당 메서드를 재정의하고 있는지 확인한다
3. 대상 클래스에 메서드를 선언한다
4. 소스 메서드의 본문을 대상 메서드로 복사하고, 대상 클래스에서 동작하도록 조정한다
5. 소스 메서드를 대상 메서드에 대한 위임(delegation)으로 변경한다
6. 컴파일 및 테스트한다
7. 소스 메서드를 완전히 제거할지, 위임으로 남겨둘지 결정한다

**예시**:

```java
// Before
class Account {
    private AccountType type;
    private int daysOverdrawn;

    double overdraftCharge() {
        if (type.isPremium()) {
            double result = 10;
            if (daysOverdrawn > 7) {
                result += (daysOverdrawn - 7) * 0.85;
            }
            return result;
        } else {
            return daysOverdrawn * 1.75;
        }
    }
}

// After
class AccountType {
    double overdraftCharge(int daysOverdrawn) {
        if (isPremium()) {
            double result = 10;
            if (daysOverdrawn > 7) {
                result += (daysOverdrawn - 7) * 0.85;
            }
            return result;
        } else {
            return daysOverdrawn * 1.75;
        }
    }
}

class Account {
    private AccountType type;
    private int daysOverdrawn;

    double overdraftCharge() {
        return type.overdraftCharge(daysOverdrawn);
    }
}
```

**레거시 코드에서의 주의점**: 메서드를 이동하기 전에 원본 메서드에 대한 테스트가 있는지 확인한다. 테스트가 없다면 먼저 특성화 테스트를 작성한 후 이동을 진행한다. 이동 후에도 원본 위치에 위임 메서드를 남겨두면 기존 호출자에 대한 호환성을 유지할 수 있다.

---

### 5. Extract Interface (인터페이스 추출)

**설명**: 클래스의 메서드 중 일부를 인터페이스로 추출하여, 해당 클래스의 특정 역할만을 표현하는 인터페이스를 정의하는 기법이다. 이 책에서 가장 빈번하게 사용되는 의존성 깨기 기법 중 하나이다.

**적용 상황**:
- 클래스의 특정 하위 집합만 사용하는 클라이언트가 있을 때
- 테스트에서 가짜 객체(Fake Object)를 만들기 위해 인터페이스가 필요할 때
- 두 개 이상의 클래스가 동일한 프로토콜의 일부를 공유할 때
- Chapter 9(클래스를 테스트 하네스에 넣기), Chapter 25(의존성 깨기 기법)에서 핵심적으로 활용됨

**절차**:
1. 추출할 메서드들의 집합을 결정한다 (클라이언트가 실제로 사용하는 메서드)
2. 인터페이스 이름을 결정한다 (클라이언트 관점에서 역할을 표현하는 이름)
3. 인터페이스를 선언하고, 결정한 메서드들을 인터페이스에 추가한다
4. 원래 클래스가 이 인터페이스를 구현하도록 선언한다
5. 클라이언트 코드에서 클래스 타입 대신 인터페이스 타입을 사용하도록 변경한다
6. 컴파일 및 테스트한다

**예시**:

```java
// Before - 테스트에서 MailService를 직접 사용해야 함
class OrderProcessor {
    private MailService mailService;

    void processOrder(Order order) {
        // ... 주문 처리 로직 ...
        mailService.send(order.getCustomerEmail(), "Order confirmed");
    }
}

// After - 인터페이스를 통해 테스트에서 가짜 객체 사용 가능
interface MessageSender {
    void send(String to, String body);
}

class MailService implements MessageSender {
    public void send(String to, String body) {
        // 실제 메일 전송 로직
    }
}

class FakeMessageSender implements MessageSender {
    private List<String> sentMessages = new ArrayList<>();

    public void send(String to, String body) {
        sentMessages.add(to + ": " + body);
    }

    List<String> getSentMessages() { return sentMessages; }
}

class OrderProcessor {
    private MessageSender messageSender;

    OrderProcessor(MessageSender messageSender) {
        this.messageSender = messageSender;
    }

    void processOrder(Order order) {
        // ... 주문 처리 로직 ...
        messageSender.send(order.getCustomerEmail(), "Order confirmed");
    }
}
```

**레거시 코드에서의 주의점**: Feathers는 Extract Interface를 테스트 시 의존성을 깨는 가장 중요한 기법 중 하나로 강조한다. 레거시 코드에서는 종종 구체 클래스에 직접 의존하는 경우가 많은데, 인터페이스를 추출하면 테스트 더블(Test Double)을 주입할 수 있게 된다. 인터페이스 이름은 구현이 아닌 **역할(role)**을 표현해야 한다.

---

### 6. Inline Method (메서드 인라인)

**설명**: 메서드의 본문이 메서드 이름만큼이나 명확할 때, 또는 간접(indirection)이 과도할 때, 메서드 호출을 메서드 본문으로 교체하는 기법이다. Extract Method의 역방향 리팩토링이다.

**적용 상황**:
- 메서드 본문이 이름만큼 명확할 때
- 과도한 위임(delegation)으로 인해 코드 흐름을 따라가기 어려울 때
- 여러 메서드를 재구성하기 전에 먼저 인라인하여 하나로 합친 후, 더 나은 방식으로 다시 Extract Method를 적용하고 싶을 때
- 간접 호출이 불필요하게 많을 때

**절차**:
1. 메서드가 다형적(polymorphic)이지 않은지 확인한다 (하위 클래스에서 재정의하지 않는지)
2. 메서드의 모든 호출 지점을 찾는다
3. 각 호출 지점을 메서드 본문으로 교체한다
4. 컴파일 및 테스트한다
5. 메서드 정의를 제거한다

**예시**:

```java
// Before
int getRating() {
    return moreThanFiveLateDeliveries() ? 2 : 1;
}

boolean moreThanFiveLateDeliveries() {
    return numberOfLateDeliveries > 5;
}

// After
int getRating() {
    return (numberOfLateDeliveries > 5) ? 2 : 1;
}
```

**레거시 코드에서의 주의점**: 레거시 코드에서 Inline Method를 사용하는 주요 시나리오는, 기존의 잘못 분리된 메서드 구조를 재구성하기 위한 중간 단계이다. 먼저 인라인하여 전체 코드를 한곳에 모은 후, 더 의미 있는 단위로 다시 Extract Method를 적용한다. 이때 반드시 테스트가 있는 상태에서 진행해야 한다.

---

### 7. Pull Up Method (메서드 올리기)

**설명**: 하위 클래스들에 동일하거나 매우 유사한 메서드가 있을 때, 이를 상위 클래스로 이동하여 코드 중복을 제거하는 기법이다.

**적용 상황**:
- 여러 하위 클래스에 동일한 메서드가 존재할 때
- 하위 클래스들의 메서드가 약간의 차이만 있고 대부분 동일할 때 (Template Method 패턴으로 전환 가능)
- 공통 행위를 상위 클래스에 정의하여 중복을 제거하고 싶을 때

**절차**:
1. 대상 메서드들이 동일한지 확인한다. 동일하지 않다면, 동일한 본문을 갖도록 먼저 수정한다
2. 메서드의 시그니처가 동일한지 확인한다. 다르다면 동일하게 맞춘다
3. 상위 클래스에 메서드를 생성하고, 하위 클래스의 메서드 본문을 복사한다
4. 하위 클래스의 메서드를 삭제한다
5. 컴파일 및 테스트한다
6. 해당 메서드를 사용하지 않는 다른 하위 클래스가 있다면 상위 클래스의 메서드가 적절한지 검토한다

**예시**:

```java
// Before
class RegularEmployee extends Employee {
    String getId() {
        return "EMP-" + employeeNumber;
    }
}

class ContractEmployee extends Employee {
    String getId() {
        return "EMP-" + employeeNumber;
    }
}

// After
class Employee {
    String getId() {
        return "EMP-" + employeeNumber;
    }
}
```

**레거시 코드에서의 주의점**: 메서드를 올리기 전에, 모든 하위 클래스에서 해당 메서드의 동작이 정확히 동일한지 반드시 확인해야 한다. 레거시 코드에서는 겉보기에 동일해 보이는 메서드가 미묘한 차이를 가지고 있는 경우가 많다. 특성화 테스트를 작성하여 각 하위 클래스의 동작을 먼저 문서화한다.

---

### 8. Push Down Method (메서드 내리기)

**설명**: 상위 클래스의 메서드가 특정 하위 클래스에서만 의미가 있을 때, 해당 메서드를 관련 하위 클래스로 이동하는 기법이다. Pull Up Method의 역방향 리팩토링이다.

**적용 상황**:
- 상위 클래스의 메서드가 일부 하위 클래스에서만 사용될 때
- 상위 클래스가 너무 많은 기능을 가지고 있어 특정 하위 클래스에만 해당하는 기능을 분리하고 싶을 때
- 클래스 계층 구조를 정리할 때

**절차**:
1. 해당 메서드를 사용하는 하위 클래스를 모두 식별한다
2. 관련 하위 클래스 각각에 메서드를 복사한다
3. 상위 클래스에서 메서드를 제거한다
4. 컴파일 및 테스트한다
5. 메서드를 사용하지 않는 하위 클래스에서도 제거한다

**예시**:

```java
// Before
class Employee {
    double calculateCommission() {
        return salesAmount * commissionRate;
    }
}

class SalesEmployee extends Employee { }
class Engineer extends Employee { }  // 커미션과 무관

// After
class Employee { }

class SalesEmployee extends Employee {
    double calculateCommission() {
        return salesAmount * commissionRate;
    }
}

class Engineer extends Employee { }
```

**레거시 코드에서의 주의점**: 상위 클래스에서 메서드를 제거하면 해당 메서드를 상위 클래스 타입으로 호출하는 코드가 깨진다. 레거시 코드에서는 이런 호출 지점을 빠짐없이 찾는 것이 어려울 수 있으므로, 컴파일러의 도움을 받아 모든 참조를 확인한다. 정적 타입 언어에서는 컴파일 에러로 누락을 잡을 수 있지만, 동적 타입 언어에서는 더 주의가 필요하다.

---

### 9. Replace Type Code with Subclasses (타입 코드를 서브클래스로 교체)

**설명**: 클래스의 동작에 영향을 미치는 타입 코드(type code)가 있을 때, 이를 서브클래스로 교체하는 기법이다. 이 기법은 보통 Replace Conditional with Polymorphism의 전 단계로 수행된다.

**적용 상황**:
- 타입 코드에 따라 동작이 달라지는 조건문이 있을 때
- `switch`문이나 `if-else` 체인이 타입 코드를 기반으로 분기할 때
- 타입별 동작을 다형성으로 처리하고 싶을 때
- Chapter 21(같은 코드를 여러 곳에서 변경할 때)에서 활용됨

**절차**:
1. 타입 코드에 Self-Encapsulate Field를 적용하여 접근자 메서드를 만든다
2. 각 타입 코드 값에 대한 서브클래스를 생성한다
3. 각 서브클래스에서 타입 코드 접근자를 재정의하여 해당 값을 반환하도록 한다
4. 상위 클래스의 타입 코드 필드를 제거한다
5. 팩토리 메서드를 도입하여 적절한 서브클래스의 인스턴스를 생성하도록 한다
6. 컴파일 및 테스트한다

**예시**:

```java
// Before
class Employee {
    static final int ENGINEER = 0;
    static final int SALESPERSON = 1;
    static final int MANAGER = 2;

    private int type;

    Employee(int type) {
        this.type = type;
    }

    double calculatePay() {
        switch (type) {
            case ENGINEER:
                return baseSalary;
            case SALESPERSON:
                return baseSalary + commission;
            case MANAGER:
                return baseSalary + bonus;
            default:
                throw new IllegalArgumentException("Unknown type");
        }
    }
}

// After
abstract class Employee {
    static Employee create(int type) {
        switch (type) {
            case 0: return new Engineer();
            case 1: return new Salesperson();
            case 2: return new Manager();
            default: throw new IllegalArgumentException("Unknown type");
        }
    }

    abstract double calculatePay();
}

class Engineer extends Employee {
    double calculatePay() { return baseSalary; }
}

class Salesperson extends Employee {
    double calculatePay() { return baseSalary + commission; }
}

class Manager extends Employee {
    double calculatePay() { return baseSalary + bonus; }
}
```

**레거시 코드에서의 주의점**: 타입 코드가 여러 곳에서 사용되는 경우, 한 번에 모두 변환하기보다 점진적으로 진행한다. 먼저 팩토리 메서드를 도입하고, 타입 코드 기반 조건문을 하나씩 다형성으로 교체한다. 레거시 코드에서는 타입 코드가 직렬화, 데이터베이스 매핑 등 여러 목적으로 사용될 수 있으므로, 이러한 외부 의존성도 고려해야 한다.

---

### 10. Replace Conditional with Polymorphism (조건문을 다형성으로 교체)

**설명**: 객체의 타입에 따라 다른 동작을 수행하는 조건문이 있을 때, 조건문의 각 분기를 서브클래스의 재정의 메서드로 옮기는 기법이다. 객체지향 프로그래밍의 핵심 원리를 활용한 리팩토링이다.

**적용 상황**:
- 동일한 조건 구조가 여러 메서드에 반복적으로 나타날 때
- 타입 코드나 타입 확인(`instanceof`)에 기반한 조건문이 있을 때
- 새로운 타입 추가 시 여러 곳의 조건문을 수정해야 할 때
- Chapter 21(같은 코드를 여러 곳에서 변경할 때)에서 핵심적으로 다루어짐

**절차**:
1. 조건문이 타입 코드에 기반한다면 먼저 Replace Type Code with Subclasses를 적용한다
2. 조건문이 포함된 메서드를 식별한다
3. 해당 메서드를 상위 클래스에서 재정의할 수 있도록 설정한다 (필요하다면 Extract Method 수행)
4. 각 서브클래스에서 메서드를 재정의하여 해당 조건 분기의 코드를 넣는다
5. 상위 클래스의 메서드를 추상으로 만들거나 기본 구현을 남긴다
6. 컴파일 및 테스트한다

**예시**:

```java
// Before
class Shape {
    private String type;

    double area() {
        if (type.equals("circle")) {
            return Math.PI * radius * radius;
        } else if (type.equals("rectangle")) {
            return width * height;
        } else if (type.equals("triangle")) {
            return 0.5 * base * height;
        }
        throw new IllegalStateException("Unknown shape type");
    }
}

// After
abstract class Shape {
    abstract double area();
}

class Circle extends Shape {
    private double radius;
    double area() { return Math.PI * radius * radius; }
}

class Rectangle extends Shape {
    private double width, height;
    double area() { return width * height; }
}

class Triangle extends Shape {
    private double base, height;
    double area() { return 0.5 * base * height; }
}
```

**레거시 코드에서의 주의점**: 이 리팩토링은 규모가 크고 여러 단계로 나뉘므로, 반드시 충분한 테스트가 갖춰진 상태에서 수행해야 한다. 레거시 코드에서 이 기법을 적용하려면 보통 다음 순서를 따른다:

1. 특성화 테스트로 현재 동작을 포착한다
2. Replace Type Code with Subclasses를 먼저 적용한다
3. 조건문을 하나씩 다형성 메서드로 이동한다
4. 각 단계마다 테스트를 실행하여 동작이 변하지 않았음을 확인한다

---

## 리팩토링 기법 빠른 참조

| 기법 | 주요 목적 | 관련 챕터 |
|------|-----------|-----------|
| Extract Method | 긴 메서드를 작은 단위로 분해 | Ch.6, Ch.22 |
| Rename Method/Variable | 코드의 의도 명확화 | Ch.16 |
| Extract Class | 과도한 책임을 가진 클래스 분리 | Ch.20 |
| Move Method | 메서드를 적절한 클래스로 이동 | Ch.20 |
| Extract Interface | 테스트 가능성 확보, 의존성 분리 | Ch.9, Ch.25 |
| Inline Method | 불필요한 간접 호출 제거 | Ch.22 |
| Pull Up Method | 하위 클래스 간 중복 제거 | Ch.20 |
| Push Down Method | 특정 하위 클래스에만 해당하는 기능 분리 | Ch.20 |
| Replace Type Code with Subclasses | 타입 코드 기반 구조를 상속 구조로 전환 | Ch.21 |
| Replace Conditional with Polymorphism | 조건문을 다형성으로 교체 | Ch.21 |

---

## 요약

이 부록에서 다룬 리팩토링 기법들은 Martin Fowler의 "Refactoring"에서 체계화된 것들로, "Working Effectively with Legacy Code" 전반에 걸쳐 핵심 도구로 사용된다. 레거시 코드에서 이 기법들을 적용할 때의 핵심 원칙은 다음과 같다:

1. **안전망 우선**: 리팩토링 전에 반드시 테스트를 확보한다. 테스트가 없다면 특성화 테스트를 먼저 작성한다.
2. **작은 단계**: 한 번에 하나의 리팩토링만 수행하고, 매 단계마다 테스트를 실행한다.
3. **도구 활용**: IDE의 자동 리팩토링 기능은 수동 실수를 줄여주므로 적극 활용한다.
4. **의존성 깨기와 결합**: 이 부록의 리팩토링 기법들은 Chapter 25의 의존성 깨기 기법들과 결합하여 사용될 때 가장 효과적이다. 의존성 깨기로 코드를 테스트 가능한 상태로 만든 후, 리팩토링으로 설계를 개선한다.

> 리팩토링은 한 번에 완성하는 것이 아니라, 코드를 변경할 때마다 조금씩 개선해 나가는 지속적인 활동이다. 레거시 코드에서도 이 원칙은 동일하게 적용된다.
