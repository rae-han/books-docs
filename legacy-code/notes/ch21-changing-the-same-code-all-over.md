# Chapter 21: 반복되는 동일한 수정, 그만할 수는 없을까? (I'm Changing the Same Code All Over the Place)

## 핵심 질문

비슷한 코드가 여러 곳에 산재해 있어서 한 가지를 변경할 때마다 여러 곳을 동시에 수정해야 한다면, 어떻게 하면 중복을 제거하고 변경을 한 곳에서만 할 수 있게 만들 수 있는가?

---

## 1. 코드 중복의 문제

코드 중복은 소프트웨어 시스템에서 가장 흔하면서도 가장 해로운 문제 중 하나다. Feathers는 중복이 시스템에 미치는 구체적인 해악을 다음과 같이 정리한다.

### 1.1 같은 변경을 여러 곳에서 반복해야 함

중복 코드의 가장 직접적인 문제는 변경 비용의 증가다. 하나의 비즈니스 규칙을 변경하려면 그 규칙이 구현된 모든 곳을 찾아서 수정해야 한다.

```java
// 3개의 다른 파일에서 동일한 할인 계산 로직이 반복된다
// OrderService.java
public double calculateDiscount(Order order) {
    if (order.getTotal() > 100) {
        return order.getTotal() * 0.1;
    }
    return 0;
}

// InvoiceGenerator.java
public double getDiscountAmount(Invoice invoice) {
    if (invoice.getSubtotal() > 100) {
        return invoice.getSubtotal() * 0.1;
    }
    return 0;
}

// ShoppingCart.java
public double computeDiscount() {
    double total = calculateTotal();
    if (total > 100) {
        return total * 0.1;
    }
    return 0;
}
```

할인 기준이 100에서 150으로 바뀌면? 3곳을 모두 찾아서 바꿔야 한다.

### 1.2 한 곳을 빠뜨리면 버그 발생

중복 코드에서 한 곳이라도 수정을 빠뜨리면 **일관성이 깨져서 버그**가 된다. 이런 버그는 발견하기 매우 어렵다. 대부분의 경우에는 올바르게 동작하다가, 특정 경로를 통해 실행될 때만 문제가 드러나기 때문이다.

```java
// 변경 후: 할인 기준을 100 → 150으로 변경
// OrderService.java - ✅ 변경 완료
if (order.getTotal() > 150) { ... }

// InvoiceGenerator.java - ✅ 변경 완료
if (invoice.getSubtotal() > 150) { ... }

// ShoppingCart.java - ❌ 변경 누락!
if (total > 100) { ... }  // 여전히 100 → 버그!
```

### 1.3 시스템의 일관성 저해

중복 코드가 시간이 지나면서 **제각각 다르게 진화**하는 현상이 발생한다. 처음에는 완전히 동일했던 코드가 각 위치에서 약간씩 다르게 수정되면서, 같은 개념에 대해 서로 다른 구현이 공존하게 된다.

이렇게 되면:
- **어느 것이 "올바른" 구현인지 알 수 없다**
- **새로운 위치에 같은 로직을 추가할 때 어느 것을 참고해야 하는지 모른다**
- **시스템 전체의 동작을 예측하기 어렵다**

---

## 2. 중복 제거의 원칙

### 2.1 DRY (Don't Repeat Yourself)

**DRY 원칙**은 "모든 지식은 시스템 내에서 단 하나의, 명확한, 권위 있는 표현을 가져야 한다"는 원칙이다.

> **모든 코드 중복은 지식의 중복이다.** 같은 비즈니스 규칙, 같은 알고리즘, 같은 정책이 여러 곳에 표현되어 있다면, 그것은 DRY 위반이다.

DRY는 단순히 "같은 코드를 복사하지 마라"를 넘어선다:

| DRY의 범위 | 예시 |
|-----------|------|
| **코드 중복** | 동일한 로직이 여러 메서드에 반복 |
| **지식 중복** | 같은 비즈니스 규칙이 코드와 설정 파일에 동시에 존재 |
| **의도 중복** | 다르게 생겼지만 같은 목적을 가진 코드 |

### 2.2 Open/Closed Principle과의 관계

**Open/Closed Principle (OCP)**: 소프트웨어 엔티티는 확장에는 열려 있고, 수정에는 닫혀 있어야 한다.

중복 제거와 OCP는 밀접하게 관련된다:

- **중복이 있으면** → 변경 시 여러 곳을 수정해야 한다 → 코드가 "수정에 닫혀 있지 않다"
- **중복을 제거하면** → 변경이 한 곳에서만 이루어진다 → 코드가 "수정에 닫혀 있다"
- **공통 로직을 추상화하면** → 새로운 변형을 추가할 때 기존 코드를 수정하지 않아도 된다 → "확장에 열려 있다"

```java
// 중복이 있는 상태: OCP 위반
// 새로운 할인 유형을 추가하려면 여러 곳을 수정해야 한다

// 중복을 제거한 상태: OCP 준수
public interface DiscountPolicy {
    double calculateDiscount(double total);
}

// 새로운 할인 유형은 새 클래스를 추가하면 된다 (확장에 열림)
// 기존 코드는 수정할 필요 없다 (수정에 닫힘)
```

중복 제거는 OCP를 달성하기 위한 첫 번째 단계다. 중복을 제거하는 과정에서 자연스럽게 추상화가 만들어지고, 이 추상화가 확장 지점(extension point)이 된다.

---

## 3. 중복 제거 기법들

### 3.1 Extract Method: 중복 코드를 메서드로 추출

가장 기본적이고 빈번하게 사용되는 기법이다. 두 곳 이상에서 반복되는 코드를 별도 메서드로 추출한다.

#### Before

```java
public class OrderService {
    public void processOnlineOrder(Order order) {
        // 주소 유효성 검사 (중복!)
        if (order.getAddress() == null || order.getAddress().isEmpty()) {
            throw new InvalidOrderException("Address is required");
        }
        if (order.getAddress().getZipCode() == null) {
            throw new InvalidOrderException("Zip code is required");
        }
        if (!isValidZipCode(order.getAddress().getZipCode())) {
            throw new InvalidOrderException("Invalid zip code");
        }

        // 온라인 주문 처리 로직
        // ...
    }

    public void processPhoneOrder(Order order) {
        // 주소 유효성 검사 (중복!)
        if (order.getAddress() == null || order.getAddress().isEmpty()) {
            throw new InvalidOrderException("Address is required");
        }
        if (order.getAddress().getZipCode() == null) {
            throw new InvalidOrderException("Zip code is required");
        }
        if (!isValidZipCode(order.getAddress().getZipCode())) {
            throw new InvalidOrderException("Invalid zip code");
        }

        // 전화 주문 처리 로직
        // ...
    }
}
```

#### After

```java
public class OrderService {
    public void processOnlineOrder(Order order) {
        validateAddress(order);
        // 온라인 주문 처리 로직
        // ...
    }

    public void processPhoneOrder(Order order) {
        validateAddress(order);
        // 전화 주문 처리 로직
        // ...
    }

    private void validateAddress(Order order) {
        if (order.getAddress() == null || order.getAddress().isEmpty()) {
            throw new InvalidOrderException("Address is required");
        }
        if (order.getAddress().getZipCode() == null) {
            throw new InvalidOrderException("Zip code is required");
        }
        if (!isValidZipCode(order.getAddress().getZipCode())) {
            throw new InvalidOrderException("Invalid zip code");
        }
    }
}
```

주소 유효성 검사 규칙이 변경되면 `validateAddress()` 한 곳만 수정하면 된다.

### 3.2 Extract Class: 관련된 중복 코드를 클래스로 추출

여러 클래스에 걸쳐 중복되는 코드가 있다면, 중복 코드를 별도 클래스로 추출하고 각 클래스에서 이를 사용한다.

#### Before

```java
// OrderService.java
public class OrderService {
    public String formatCurrency(double amount) {
        return String.format("$%,.2f", amount);
    }

    public String formatDate(Date date) {
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");
        return sdf.format(date);
    }

    public void printOrderSummary(Order order) {
        System.out.println("Total: " + formatCurrency(order.getTotal()));
        System.out.println("Date: " + formatDate(order.getDate()));
    }
}

// InvoiceService.java
public class InvoiceService {
    public String formatCurrency(double amount) {
        return String.format("$%,.2f", amount);
    }

    public String formatDate(Date date) {
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");
        return sdf.format(date);
    }

    public void printInvoice(Invoice invoice) {
        System.out.println("Amount: " + formatCurrency(invoice.getAmount()));
        System.out.println("Due: " + formatDate(invoice.getDueDate()));
    }
}
```

#### After

```java
// Formatter.java - 중복 코드를 별도 클래스로 추출
public class Formatter {
    public String formatCurrency(double amount) {
        return String.format("$%,.2f", amount);
    }

    public String formatDate(Date date) {
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");
        return sdf.format(date);
    }
}

// OrderService.java
public class OrderService {
    private Formatter formatter = new Formatter();

    public void printOrderSummary(Order order) {
        System.out.println("Total: " + formatter.formatCurrency(order.getTotal()));
        System.out.println("Date: " + formatter.formatDate(order.getDate()));
    }
}

// InvoiceService.java
public class InvoiceService {
    private Formatter formatter = new Formatter();

    public void printInvoice(Invoice invoice) {
        System.out.println("Amount: " + formatter.formatCurrency(invoice.getAmount()));
        System.out.println("Due: " + formatter.formatDate(invoice.getDueDate()));
    }
}
```

### 3.3 Template Method Pattern: 공통 알고리즘 구조를 상위 클래스에

**Template Method Pattern**은 알고리즘의 전체 구조는 상위 클래스에 정의하고, 변하는 부분만 하위 클래스에서 구현하게 하는 패턴이다. 여러 클래스에서 **알고리즘의 골격은 같지만 세부 단계가 다른** 경우에 특히 유용하다.

#### Before

```java
// CsvReportGenerator.java
public class CsvReportGenerator {
    public void generateReport(List<Record> records) {
        // 1. 헤더 출력 (다름)
        System.out.println("Name,Amount,Date");

        // 2. 데이터 필터링 (같음)
        List<Record> filtered = records.stream()
            .filter(r -> r.getAmount() > 0)
            .collect(Collectors.toList());

        // 3. 데이터 정렬 (같음)
        filtered.sort(Comparator.comparing(Record::getDate));

        // 4. 각 레코드 출력 (다름)
        for (Record r : filtered) {
            System.out.println(r.getName() + "," + r.getAmount() + "," + r.getDate());
        }

        // 5. 요약 출력 (같음)
        double total = filtered.stream().mapToDouble(Record::getAmount).sum();
        System.out.println("Total: " + total);
    }
}

// HtmlReportGenerator.java
public class HtmlReportGenerator {
    public void generateReport(List<Record> records) {
        // 1. 헤더 출력 (다름)
        System.out.println("<table><tr><th>Name</th><th>Amount</th><th>Date</th></tr>");

        // 2. 데이터 필터링 (같음)
        List<Record> filtered = records.stream()
            .filter(r -> r.getAmount() > 0)
            .collect(Collectors.toList());

        // 3. 데이터 정렬 (같음)
        filtered.sort(Comparator.comparing(Record::getDate));

        // 4. 각 레코드 출력 (다름)
        for (Record r : filtered) {
            System.out.println("<tr><td>" + r.getName() + "</td><td>"
                + r.getAmount() + "</td><td>" + r.getDate() + "</td></tr>");
        }

        // 5. 요약 출력 (같음)
        double total = filtered.stream().mapToDouble(Record::getAmount).sum();
        System.out.println("<tr><td colspan='3'>Total: " + total + "</td></tr></table>");
    }
}
```

필터링 로직, 정렬 로직, 요약 계산 로직이 두 클래스에서 완전히 동일하게 반복된다.

#### After

```java
// ReportGenerator.java - 공통 알고리즘 구조 (Template Method)
public abstract class ReportGenerator {

    // Template Method: 알고리즘의 골격을 정의
    public final void generateReport(List<Record> records) {
        printHeader();

        List<Record> filtered = filterRecords(records);     // 공통
        List<Record> sorted = sortRecords(filtered);        // 공통

        for (Record r : sorted) {
            printRecord(r);                                 // 변하는 부분
        }

        double total = calculateTotal(sorted);              // 공통
        printSummary(total);                                // 변하는 부분
    }

    // 공통 로직: 상위 클래스에서 구현
    protected List<Record> filterRecords(List<Record> records) {
        return records.stream()
            .filter(r -> r.getAmount() > 0)
            .collect(Collectors.toList());
    }

    protected List<Record> sortRecords(List<Record> records) {
        List<Record> sorted = new ArrayList<>(records);
        sorted.sort(Comparator.comparing(Record::getDate));
        return sorted;
    }

    protected double calculateTotal(List<Record> records) {
        return records.stream().mapToDouble(Record::getAmount).sum();
    }

    // 변하는 부분: 하위 클래스에서 구현
    protected abstract void printHeader();
    protected abstract void printRecord(Record record);
    protected abstract void printSummary(double total);
}

// CsvReportGenerator.java
public class CsvReportGenerator extends ReportGenerator {
    @Override
    protected void printHeader() {
        System.out.println("Name,Amount,Date");
    }

    @Override
    protected void printRecord(Record record) {
        System.out.println(record.getName() + "," + record.getAmount()
            + "," + record.getDate());
    }

    @Override
    protected void printSummary(double total) {
        System.out.println("Total: " + total);
    }
}

// HtmlReportGenerator.java
public class HtmlReportGenerator extends ReportGenerator {
    @Override
    protected void printHeader() {
        System.out.println("<table><tr><th>Name</th><th>Amount</th><th>Date</th></tr>");
    }

    @Override
    protected void printRecord(Record record) {
        System.out.println("<tr><td>" + record.getName() + "</td><td>"
            + record.getAmount() + "</td><td>" + record.getDate() + "</td></tr>");
    }

    @Override
    protected void printSummary(double total) {
        System.out.println("<tr><td colspan='3'>Total: " + total + "</td></tr></table>");
    }
}
```

이제 필터링 규칙을 변경하려면 `ReportGenerator.filterRecords()` 한 곳만 수정하면 된다. 새로운 보고서 형식(예: JSON)을 추가하려면 `ReportGenerator`를 상속하는 새 클래스를 만들면 된다.

### 3.4 Pull Up Method: 중복된 메서드를 상위 클래스로 이동

이미 상속 관계에 있는 여러 하위 클래스에 동일한 메서드가 존재할 때, 이를 상위 클래스로 올리는 기법이다.

#### Before

```java
public abstract class Shape {
    protected double x, y;
}

public class Circle extends Shape {
    private double radius;

    // 중복!
    public double distanceTo(Shape other) {
        double dx = this.x - other.x;
        double dy = this.y - other.y;
        return Math.sqrt(dx * dx + dy * dy);
    }
}

public class Rectangle extends Shape {
    private double width, height;

    // 중복!
    public double distanceTo(Shape other) {
        double dx = this.x - other.x;
        double dy = this.y - other.y;
        return Math.sqrt(dx * dx + dy * dy);
    }
}
```

#### After

```java
public abstract class Shape {
    protected double x, y;

    // 상위 클래스로 Pull Up
    public double distanceTo(Shape other) {
        double dx = this.x - other.x;
        double dy = this.y - other.y;
        return Math.sqrt(dx * dx + dy * dy);
    }
}

public class Circle extends Shape {
    private double radius;
    // distanceTo() 메서드가 제거됨
}

public class Rectangle extends Shape {
    private double width, height;
    // distanceTo() 메서드가 제거됨
}
```

Pull Up Method를 적용할 때의 주의점:

- **완전히 동일한 코드인지 확인한다**: 미세한 차이가 있을 수 있다. 차이가 있다면 먼저 코드를 통일하거나, Template Method Pattern을 고려한다.
- **상위 클래스의 필드에 접근 가능한지 확인한다**: 메서드가 사용하는 필드가 상위 클래스에 존재하거나, 함께 올려야 할 수 있다.
- **테스트를 먼저 확보한다**: Pull Up 후 동작이 달라지지 않았는지 확인할 수 있어야 한다.

---

## 4. 중복 코드를 찾는 방법

### 4.1 물리적으로 동일한 코드

가장 발견하기 쉬운 중복이다. 문자 그대로 동일한 코드 블록이 여러 곳에 존재한다.

**발견 방법:**
- **텍스트 검색**: 특정 코드 패턴이나 문자열을 검색한다.
- **복사-붙여넣기 감지 도구(CPD, Clone Detector 등)**: 코드베이스 전체에서 중복된 코드 블록을 자동으로 찾아준다.
- **코드 리뷰 시 주의**: 새로운 코드가 기존 코드와 유사한지 의식적으로 확인한다.

```java
// 완전히 동일한 코드 - 발견하기 쉬움
// 파일 A
if (user.getAge() >= 18 && user.hasConsent()) {
    // ...
}

// 파일 B
if (user.getAge() >= 18 && user.hasConsent()) {
    // ...
}
```

### 4.2 의미적으로 동일한 코드 (다르게 생겼지만 같은 일을 하는 코드)

더 발견하기 어렵지만 더 흔한 형태의 중복이다. 코드의 **표현**은 다르지만 **의미**가 같다.

```java
// 의미적으로 동일한 코드 - 다르게 생겼지만 같은 일을 함

// 파일 A: 배열을 사용
public boolean isWeekend(int dayOfWeek) {
    int[] weekendDays = {Calendar.SATURDAY, Calendar.SUNDAY};
    for (int day : weekendDays) {
        if (dayOfWeek == day) return true;
    }
    return false;
}

// 파일 B: 조건문을 사용
public boolean checkIfWeekend(int day) {
    return day == Calendar.SATURDAY || day == Calendar.SUNDAY;
}

// 파일 C: 범위 검사를 사용
public boolean isNonWorkingDay(int d) {
    return d >= Calendar.SATURDAY;  // SATURDAY=7, SUNDAY=1 이면 버그 가능!
}
```

세 메서드 모두 "주말인지 확인"이라는 같은 의미를 가지지만, 표현이 다르다. 심지어 파일 C는 표현이 다른 만큼 버그를 포함할 가능성도 있다.

**의미적 중복을 발견하는 방법:**
- **변경 이력 분석**: 같은 종류의 변경이 여러 파일에 동시에 발생하는 패턴을 관찰한다.
- **도메인 지식 활용**: "이 비즈니스 규칙이 다른 곳에도 구현되어 있지 않을까?" 라고 의식적으로 질문한다.
- **네이밍 유사성**: 비슷한 이름의 메서드나 변수가 여러 클래스에 있다면 의미적 중복일 가능성이 높다.

---

## 5. Abbreviation (축약): 중복 제거가 가져오는 구조적 통찰

Feathers는 중복 제거의 부수적이지만 매우 중요한 효과를 강조한다.

### 5.1 코드가 간결해지면 전체 구조가 보이기 시작한다

중복을 제거하면 코드가 짧아진다. 코드가 짧아지면:

1. **한눈에 더 많은 코드를 볼 수 있다**: 스크롤 없이 클래스의 전체 구조를 파악할 수 있다.
2. **패턴이 드러난다**: 중복이 제거되면 각 메서드가 고유한 역할만 남게 되고, 클래스의 책임 구조가 명확해진다.
3. **추가 리팩토링 기회가 보인다**: 중복이 있을 때는 코드 양 때문에 보이지 않던 구조적 문제가 드러난다.

```java
// Before: 중복으로 인해 300줄 → 구조가 안 보임
public class ReportService {
    // 매출 보고서 생성 (100줄)
    //   - DB 조회 (20줄)
    //   - 데이터 가공 (30줄)
    //   - 포맷팅 (30줄)
    //   - 출력 (20줄)

    // 재고 보고서 생성 (100줄)
    //   - DB 조회 (20줄)      ← 중복
    //   - 데이터 가공 (30줄)   ← 유사
    //   - 포맷팅 (30줄)       ← 중복
    //   - 출력 (20줄)         ← 중복

    // 인사 보고서 생성 (100줄)
    //   - DB 조회 (20줄)      ← 중복
    //   - 데이터 가공 (30줄)   ← 유사
    //   - 포맷팅 (30줄)       ← 중복
    //   - 출력 (20줄)         ← 중복
}
```

```java
// After: 중복 제거 후 120줄 → 구조가 명확
public class ReportService {
    private DataFetcher fetcher;      // DB 조회 담당
    private ReportFormatter formatter; // 포맷팅 담당
    private ReportPrinter printer;     // 출력 담당

    public void generateSalesReport() {
        Data data = fetcher.fetchSalesData();
        Data processed = processSalesData(data);   // 각 보고서별 고유 로직만 남음
        printer.print(formatter.format(processed));
    }

    public void generateInventoryReport() {
        Data data = fetcher.fetchInventoryData();
        Data processed = processInventoryData(data); // 각 보고서별 고유 로직만 남음
        printer.print(formatter.format(processed));
    }

    // 이제 "보고서 생성의 골격은 같고, 데이터 가공만 다르다"는
    // 패턴이 명확히 보인다 → Template Method 적용 가능!
}
```

### 5.2 중복 제거가 설계 개선의 시작점

> 중복 제거는 단순한 코드 정리가 아니다. 중복을 제거하는 과정에서 추상화가 만들어지고, 추상화가 만들어지면 설계가 개선된다.

Feathers가 강조하는 순서:

```
중복 발견 → 중복 제거 → 코드 축약 → 구조 가시화 → 추가 리팩토링 기회 발견 → 설계 개선
```

이것은 일회성 과정이 아니라 **반복적인 사이클**이다. 한 번의 중복 제거가 다음 개선의 문을 열어준다.

### 5.3 중복 제거의 실천적 조언

1. **작은 중복부터 시작한다**: 2~3줄의 중복이라도 제거한다. 작은 제거가 축적되면 큰 구조적 개선으로 이어진다.
2. **중복을 발견하면 즉시 제거한다**: "나중에 정리하겠다"는 거의 실행되지 않는다.
3. **새로운 기능을 추가하기 전에 중복을 먼저 제거한다**: 중복이 있는 상태에서 기능을 추가하면 중복이 더 늘어난다.
4. **완벽한 추상화를 추구하지 않는다**: 처음에는 단순한 Extract Method로 충분하다. 더 나은 추상화는 패턴이 보일 때 자연스럽게 만들어진다.

> 많은 개발자들이 리팩토링을 "있으면 좋지만 시간이 없어서 못하는 것"으로 생각한다. 하지만 중복 제거는 오히려 시간을 절약한다. 중복이 있으면 모든 변경이 여러 곳에서 이루어져야 하므로, 중복 제거에 투자한 시간은 미래의 변경에서 바로 회수된다.

---

## 요약

- **코드 중복**은 변경 비용을 높이고, 버그를 유발하며, 시스템의 일관성을 해친다.
- **DRY 원칙**: 모든 지식은 시스템 내에서 단 하나의 표현만 가져야 한다.
- 중복 제거는 **Open/Closed Principle**을 달성하는 첫 번째 단계다.
- 주요 중복 제거 기법:
  1. **Extract Method**: 중복 코드를 메서드로 추출
  2. **Extract Class**: 여러 클래스에 걸친 중복을 별도 클래스로 추출
  3. **Template Method Pattern**: 공통 알고리즘 구조는 상위 클래스에, 변하는 부분만 하위 클래스에서 구현
  4. **Pull Up Method**: 하위 클래스의 동일한 메서드를 상위 클래스로 이동
- 중복에는 **물리적 중복**(동일한 코드)과 **의미적 중복**(다르게 보이지만 같은 일을 하는 코드) 두 가지가 있다.
- 중복을 제거하면 코드가 **축약(abbreviation)** 되어 전체 구조가 보이기 시작하고, 추가 리팩토링 기회가 드러난다.
- **중복 제거는 설계 개선의 시작점**이다. 중복 제거 → 코드 축약 → 구조 가시화 → 설계 개선의 선순환이 만들어진다.

---

## 다음 챕터와의 연결

Chapter 22 **"'괴물 메소드'를 변경해야 하는데 테스트 코드를 작성하지 못하겠다 (I Need to Change a Monster Method and I Can't Write Tests for It)"** 에서는 수백 줄에 달하는 거대한 메서드에서 테스트 없이 안전하게 변경하는 기법들을 소개한다. Sensing Variable, Extract Method 등을 활용하여 거대 메서드를 점진적으로 테스트 가능한 구조로 만드는 방법을 배운다.
