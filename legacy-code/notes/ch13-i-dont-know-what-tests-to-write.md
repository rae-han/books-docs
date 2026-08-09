# Chapter 13: 변경해야 하는데, 어떤 테스트를 작성해야 할지 모르겠다 (I Need to Make a Change, but I Don't Know What Tests to Write)

## 핵심 질문

레거시 코드를 변경해야 하는데 어떤 테스트를 작성해야 할지 모를 때, 코드의 현재 동작을 안전하게 보존하면서 변경할 수 있는 테스트를 어떻게 작성하는가?

---

## 1. Characterization Test (특성 테스트)

### 1.1 정의

**Characterization Test(특성 테스트)** 는 코드의 **현재 동작(current behavior)** 을 그대로 기록하는 테스트다. "이 코드가 어떻게 동작해야 하는가(should)"가 아니라, "이 코드가 지금 실제로 어떻게 동작하는가(does)"를 문서화한다.

> Characterization test는 코드가 올바른지를 검증하는 것이 아니다. 코드의 현재 동작을 기록하여, 이후 변경 시 기존 동작이 의도치 않게 바뀌었는지를 감지하는 것이다.

### 1.2 왜 Characterization Test인가?

레거시 코드에서 테스트를 작성할 때의 근본적 딜레마:

- **"올바른" 동작이 무엇인지 모른다**: 명세서가 없거나, 있더라도 현재 코드와 일치하지 않을 수 있다
- **코드가 사실상의 명세다**: 시스템이 현재 동작하는 방식이 곧 사용자와 다른 시스템이 의존하는 명세다
- **변경의 목표는 기존 동작을 보존하면서 일부만 변경하는 것이다**: 기존 동작을 정확히 기록해두어야 보존 여부를 확인할 수 있다

### 1.3 기존 단위 테스트와의 차이

| 구분 | 일반 단위 테스트 | Characterization Test |
|------|-----------------|----------------------|
| **작성 시점** | 코드 작성 전/후 (TDD 등) | 기존 레거시 코드에 대해 사후에 작성 |
| **기준** | 명세/요구사항 기반 ("올바른" 동작) | 현재 코드의 실제 동작 기반 |
| **목적** | 코드가 올바르게 동작하는지 검증 | 현재 동작을 기록하여 변경 시 안전망 확보 |
| **실패 의미** | 코드에 버그가 있음 | 코드의 동작이 변경되었음 (의도적이든 아니든) |
| **assertion 값** | 예상되는 올바른 값 | 코드가 실제로 반환하는 값 |

```java
// 일반 단위 테스트: "올바른" 동작을 검증
@Test
public void testCalculateTax_shouldReturn10PercentForIncome() {
    TaxCalculator calc = new TaxCalculator();
    // 명세서에 따르면 10만원 소득에 대해 세금은 1만원이어야 함
    assertEquals(10000, calc.calculateTax(100000), 0.01);
}

// Characterization Test: "현재" 동작을 기록
@Test
public void testCalculateTax_currentBehavior() {
    TaxCalculator calc = new TaxCalculator();
    // 현재 코드가 실제로 반환하는 값을 기록
    // (9500이 "올바른"지는 이 테스트의 관심사가 아님)
    assertEquals(9500, calc.calculateTax(100000), 0.01);
}
```

---

## 2. Characterization Test 작성 절차

Feathers가 제시하는 단계별 절차는 매우 체계적이고 실용적이다.

### 2.1 Step-by-Step 절차

**Step 1: 테스트 하네스에 코드를 넣는다**

테스트에서 대상 코드를 호출할 수 있도록 설정한다. Chapter 9, 10에서 다룬 기법들을 활용하여 인스턴스를 생성하고 메서드를 호출할 수 있게 만든다.

```java
@Test
public void testGenerateReport() {
    // Step 1: 테스트 하네스에서 코드 실행 가능하게 설정
    ReportGenerator generator = new ReportGenerator();
    // 필요한 의존성 설정...
}
```

**Step 2: 의도적으로 틀린 assertion을 작성한다**

관찰하고 싶은 동작에 대한 assertion을 작성하되, **일부러 틀린 값**을 넣는다. 이것이 핵심 트릭이다.

```java
@Test
public void testGenerateReport() {
    ReportGenerator generator = new ReportGenerator();
    String result = generator.generate(testData);

    // Step 2: 의도적으로 틀린 값을 넣음
    assertEquals("WRONG VALUE", result);
}
```

**Step 3: 테스트를 실행하여 실패 메시지에서 실제 값을 확인한다**

테스트가 실패하면, 테스트 프레임워크가 실제 값을 알려준다:

```
Expected: "WRONG VALUE"
Actual:   "Report: Sales Summary\nTotal: $15,230.50\nDate: 2024-01-15"
```

이 실패 메시지가 코드의 **실제 현재 동작**을 알려주는 것이다.

**Step 4: 실제 값으로 assertion을 수정한다**

```java
@Test
public void testGenerateReport() {
    ReportGenerator generator = new ReportGenerator();
    String result = generator.generate(testData);

    // Step 4: 실제 값으로 수정
    assertEquals("Report: Sales Summary\nTotal: $15,230.50\nDate: 2024-01-15", result);
}
```

**Step 5: 테스트가 통과하는지 확인한다**

수정된 assertion으로 테스트를 다시 실행하여 통과하는지 확인한다. 통과하면 이 테스트는 현재 동작을 정확히 기록한 Characterization Test가 된다.

### 2.2 전체 흐름 요약

```
틀린 assertion 작성 → 테스트 실행 (실패) → 실제 값 확인 → assertion 수정 → 테스트 실행 (통과)
```

이 과정은 코드의 동작을 **코드를 읽어서 이해하는 것이 아니라, 실행하여 관찰하는 것**이다. 이것이 중요한 이유는:

- 레거시 코드는 읽어서 이해하기 어려운 경우가 많다
- 실행 결과는 거짓말하지 않는다
- 코드의 미묘한 동작(부동소수점 계산, 경계 조건 등)을 정확히 포착할 수 있다

### 2.3 구체적 코드 예시

```java
// 레거시 코드: 무엇을 하는지 한눈에 파악하기 어려움
public class FeeSchedule {
    private List<FeeRule> rules;

    public double calculateFee(double amount, String accountType, int yearsActive) {
        double fee = 0;
        for (FeeRule rule : rules) {
            if (rule.appliesTo(accountType)) {
                fee += rule.calculate(amount);
            }
        }
        if (yearsActive > 5) {
            fee *= 0.85;
        }
        if (amount > 10000) {
            fee = Math.max(fee, 25.0);
        }
        return Math.round(fee * 100.0) / 100.0;
    }
}
```

Characterization Test 작성 과정:

```java
@Test
public void testCalculateFee_standardAccount() {
    FeeSchedule schedule = createScheduleWithStandardRules();

    // Step 2: 의도적으로 틀린 값
    assertEquals(0, schedule.calculateFee(1000, "STANDARD", 3), 0.01);
}
// 실행 → 실패 메시지: Expected: 0.0, Actual: 15.0

@Test
public void testCalculateFee_standardAccount() {
    FeeSchedule schedule = createScheduleWithStandardRules();

    // Step 4: 실제 값으로 수정
    assertEquals(15.0, schedule.calculateFee(1000, "STANDARD", 3), 0.01);
}
// 실행 → 통과!

// 추가 케이스들도 같은 방식으로 작성
@Test
public void testCalculateFee_longTermCustomerDiscount() {
    FeeSchedule schedule = createScheduleWithStandardRules();

    // yearsActive > 5일 때 0.85 곱하는 로직
    assertEquals(12.75, schedule.calculateFee(1000, "STANDARD", 6), 0.01);
}

@Test
public void testCalculateFee_highAmount_minimumFee() {
    FeeSchedule schedule = createScheduleWithStandardRules();

    // amount > 10000일 때 최소 수수료 25.0 적용
    assertEquals(25.0, schedule.calculateFee(15000, "STANDARD", 10), 0.01);
}
```

---

## 3. 경계값과 특수 케이스에 대한 Characterization Test

### 3.1 경계값 탐색

코드의 조건문 경계에서 동작이 바뀌는 지점을 찾아 테스트를 작성한다:

```java
// 위의 FeeSchedule 예시에서 경계값들
@Test
public void testCalculateFee_exactly5YearsActive_noDiscount() {
    // yearsActive > 5 조건이므로, 정확히 5년은 할인 미적용
    assertEquals(15.0, schedule.calculateFee(1000, "STANDARD", 5), 0.01);
}

@Test
public void testCalculateFee_6YearsActive_discountApplied() {
    // 6년부터 할인 적용
    assertEquals(12.75, schedule.calculateFee(1000, "STANDARD", 6), 0.01);
}

@Test
public void testCalculateFee_exactly10000_noMinimumFee() {
    // amount > 10000 조건이므로, 정확히 10000은 최소 수수료 미적용
    assertEquals(15.0, schedule.calculateFee(10000, "STANDARD", 3), 0.01);
}

@Test
public void testCalculateFee_10001_minimumFeeApplied() {
    // 10001부터 최소 수수료 적용
    assertEquals(25.0, schedule.calculateFee(10001, "STANDARD", 3), 0.01);
}
```

### 3.2 특수 케이스 탐색

```java
// null 입력
@Test
public void testCalculateFee_nullAccountType() {
    // 의도적으로 틀린 값 → 실행하여 실제 동작 확인
    // NullPointerException이 발생할 수도, 기본값이 적용될 수도 있음
    assertEquals(0.0, schedule.calculateFee(1000, null, 3), 0.01);
}

// 음수 입력
@Test
public void testCalculateFee_negativeAmount() {
    assertEquals(-15.0, schedule.calculateFee(-1000, "STANDARD", 3), 0.01);
}

// 빈 리스트
@Test
public void testCalculateFee_noRules() {
    FeeSchedule emptySchedule = new FeeSchedule(Collections.emptyList());
    assertEquals(0.0, emptySchedule.calculateFee(1000, "STANDARD", 3), 0.01);
}
```

> 경계값과 특수 케이스를 테스트하면, 코드의 미묘한 동작을 발견할 수 있다. 이러한 테스트는 나중에 코드를 변경할 때 예상치 못한 동작 변경을 감지하는 데 특히 유용하다.

---

## 4. 버그를 발견했을 때의 대응

### 4.1 Characterization Test와 버그의 관계

Characterization test를 작성하다 보면 코드에서 **버그처럼 보이는 동작**을 발견할 수 있다. 이때 중요한 원칙:

> Characterization test는 현재 동작을 기록하는 것이므로, **버그도 그대로 기록한다.** 버그 수정은 Characterization test 작성과 별도의 작업으로 분리해야 한다.

### 4.2 왜 버그를 그대로 기록하는가?

```java
// 버그가 있는 것처럼 보이는 코드
public double calculateDiscount(double price, int quantity) {
    if (quantity > 100) {
        return price * 0.2;  // 20% 할인
    }
    if (quantity > 50) {
        return price * 0.1;  // 10% 할인
    }
    if (quantity > 10) {
        return price * 0.05; // 5% 할인
    }
    return 0;
    // 버그?: quantity가 정확히 10일 때 할인이 0이다.
    // 의도적일 수도, 버그일 수도 있다.
}
```

버그를 그대로 기록하는 이유:

1. **다른 코드가 이 버그에 의존할 수 있다**: 할인이 0인 것을 전제로 동작하는 코드가 있을 수 있다
2. **현재 시스템이 이 동작으로 운영 중이다**: 사용자가 이 동작에 익숙해져 있을 수 있다
3. **지금의 목표는 안전하게 변경하는 것이다**: 버그 수정은 별도의 의식적인 결정이어야 한다

### 4.3 버그 발견 시 워크플로우

```
Characterization test 작성 중 버그 발견
  ↓
버그를 현재 동작 그대로 기록 (Characterization test에 반영)
  ↓
버그를 별도로 기록 (이슈 트래커, TODO 등)
  ↓
현재 변경 작업 완료
  ↓
별도 작업으로 버그 수정 (이때는 Characterization test의 assertion을 올바른 값으로 변경)
```

```java
// 버그를 현재 동작 그대로 기록
@Test
public void testCalculateDiscount_exactlyTen_noDiscount() {
    // NOTE: quantity가 정확히 10일 때 할인이 0인 것은 버그일 수 있음
    // 별도 이슈로 기록: ISSUE-1234
    assertEquals(0, calculator.calculateDiscount(100, 10), 0.01);
}
```

나중에 버그를 수정할 때:

```java
// 버그 수정 후 Characterization test를 의도적으로 업데이트
@Test
public void testCalculateDiscount_exactlyTen_fivePercentDiscount() {
    // ISSUE-1234: quantity >= 10일 때도 5% 할인 적용하도록 수정
    assertEquals(5.0, calculator.calculateDiscount(100, 10), 0.01);
}
```

---

## 5. 탐색적(Exploratory) 테스트를 통한 코드 이해

### 5.1 탐색적 테스트란?

Characterization test 작성은 단순히 테스트를 만드는 것이 아니라, **코드를 이해하는 과정**이기도 하다. 다양한 입력을 넣어보면서 코드의 동작을 탐색하는 것을 **탐색적(exploratory) 테스트**라 한다.

### 5.2 탐색적 테스트 활용법

```java
// "이 메서드가 뭘 하는지 모르겠다" → 다양한 입력으로 탐색

@Test
public void explore_whatDoesProcessDo() {
    DataProcessor processor = new DataProcessor();

    // 빈 입력
    System.out.println("Empty: " + processor.process(""));

    // 일반 입력
    System.out.println("Hello: " + processor.process("Hello"));

    // 특수문자
    System.out.println("Special: " + processor.process("Hello, World!"));

    // 긴 입력
    System.out.println("Long: " + processor.process("A".repeat(1000)));

    // null
    try {
        System.out.println("Null: " + processor.process(null));
    } catch (Exception e) {
        System.out.println("Null throws: " + e.getClass().getSimpleName());
    }
}
```

이 탐색 과정에서 코드의 동작 패턴을 파악하면, 이를 기반으로 Characterization test를 작성한다:

```java
// 탐색 결과를 Characterization test로 변환
@Test
public void testProcess_emptyString_returnsEmpty() {
    assertEquals("", processor.process(""));
}

@Test
public void testProcess_normalString_convertsToUppercase() {
    assertEquals("HELLO", processor.process("Hello"));
}

@Test
public void testProcess_specialChars_stripsNonAlpha() {
    assertEquals("HELLO WORLD", processor.process("Hello, World!"));
}

@Test
public void testProcess_null_throwsIllegalArgument() {
    assertThrows(IllegalArgumentException.class, () -> processor.process(null));
}
```

### 5.3 탐색 시 유용한 질문들

코드를 탐색할 때 스스로에게 던질 질문들:

- 이 메서드에 null을 전달하면 어떻게 되는가?
- 빈 컬렉션이나 빈 문자열을 전달하면?
- 극단적으로 큰 값이나 극단적으로 작은 값을 전달하면?
- 음수를 전달하면?
- 같은 메서드를 두 번 연속 호출하면?
- 메서드 호출 순서를 바꾸면?
- 조건문의 경계값에서는?

---

## 6. Heuristic: 어디까지 테스트를 작성할 것인가

### 6.1 무한한 테스트의 유혹

이론적으로는 모든 입력 조합에 대해 테스트를 작성해야 하지만, 이는 현실적으로 불가능하다. Feathers는 **실용적인 기준(heuristic)** 을 제시한다.

### 6.2 Heuristic 1: 변경 영역에 집중

변경하려는 코드에 가장 가까운 부분에 테스트를 집중한다:

```
변경 지점에서의 거리        테스트 밀도
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
직접 변경하는 메서드          높음 (반드시 테스트)
변경 메서드가 호출하는 메서드   중간 (가능하면 테스트)
간접적으로 영향받는 코드       낮음 (Pinch Point에서 커버)
영향이 미미한 코드            불필요
```

### 6.3 Heuristic 2: 조건문의 분기마다 테스트

변경 대상 메서드에 조건문이 있다면, **각 분기에 대해 최소 하나의 테스트**를 작성한다:

```java
public double applyPolicy(double amount, String type) {
    if (type.equals("PREMIUM")) {       // ← 분기 1
        if (amount > 5000) {            // ← 분기 1-1
            return amount * 0.95;
        }
        return amount * 0.97;           // ← 분기 1-2
    } else if (type.equals("BASIC")) {  // ← 분기 2
        return amount;
    } else {                            // ← 분기 3
        return amount * 1.02;
    }
}

// 각 분기에 대한 Characterization test
@Test public void testApplyPolicy_premium_highAmount() { /* 분기 1-1 */ }
@Test public void testApplyPolicy_premium_lowAmount() { /* 분기 1-2 */ }
@Test public void testApplyPolicy_basic() { /* 분기 2 */ }
@Test public void testApplyPolicy_other() { /* 분기 3 */ }
```

### 6.4 Heuristic 3: 데이터 변환 지점에 테스트

데이터가 변환되는 지점(입력 → 처리 → 출력)에서 테스트를 작성한다:

```java
public class ReportFormatter {
    public String format(List<Sale> sales) {
        double total = calculateTotal(sales);   // 변환 1: 리스트 → 합계
        String formatted = formatCurrency(total); // 변환 2: 숫자 → 문자열
        return buildReport(formatted, sales.size()); // 변환 3: 조합
    }
}

// 각 변환 지점에 테스트
@Test public void testCalculateTotal() { /* 변환 1 */ }
@Test public void testFormatCurrency() { /* 변환 2 */ }
@Test public void testBuildReport() { /* 변환 3 */ }
@Test public void testFormat_endToEnd() { /* 전체 흐름 */ }
```

### 6.5 Heuristic 4: "충분히 안전하다고 느낄 때까지"

가장 주관적이지만 실용적인 기준이다:

> 코드를 변경했을 때, 테스트가 잘못된 변경을 감지할 것이라는 **합리적인 확신**이 들 때까지 Characterization test를 작성하라.

이 확신의 수준은 상황에 따라 다르다:

| 상황 | 필요한 확신 수준 | 테스트 양 |
|------|-----------------|----------|
| 핵심 비즈니스 로직 변경 | 높음 | 많은 경계값 + 분기 커버리지 |
| 단순 리팩토링 | 중간 | 주요 경로 커버리지 |
| UI 텍스트 변경 | 낮음 | 기본적인 동작 확인 |
| 설정값 변경 | 낮음 | 관련 동작만 확인 |

### 6.6 Heuristic 5: 너무 많은 테스트보다는 올바른 위치의 테스트

테스트의 수보다 **위치**가 중요하다. Chapter 11에서 배운 Effect Reasoning을 활용하여:

- 변경 영향이 모이는 **Pinch Point**에 테스트를 배치
- 조건 분기가 있는 곳에 경계값 테스트를 배치
- 외부 의존성과의 접점에 테스트를 배치

---

## 7. Characterization Test 작성 시 주의사항

### 7.1 비결정적(Non-deterministic) 동작

시간, 난수, 시스템 상태 등에 따라 결과가 달라지는 코드는 Characterization test 작성이 까다롭다:

```java
// 현재 시간에 의존하는 코드
public String getGreeting() {
    int hour = LocalTime.now().getHour();
    if (hour < 12) return "Good morning";
    if (hour < 18) return "Good afternoon";
    return "Good evening";
}
```

이런 경우 시간 의존성을 분리하거나(Extract and Override), 시간을 매개변수로 받도록 변경한다:

```java
// 시간을 매개변수로 받도록 변경
public String getGreeting(int hour) {
    if (hour < 12) return "Good morning";
    if (hour < 18) return "Good afternoon";
    return "Good evening";
}

// Characterization test
@Test
public void testGreeting_morning() {
    assertEquals("Good morning", service.getGreeting(9));
}
```

### 7.2 대량 출력을 다루는 테스트

메서드가 복잡한 문자열이나 큰 데이터 구조를 반환하는 경우:

```java
// 전체를 비교하기보다 핵심 부분만 검증
@Test
public void testGenerateReport_containsTotal() {
    String report = generator.generate(testData);
    assertTrue(report.contains("Total: $15,230.50"));
}

@Test
public void testGenerateReport_containsHeader() {
    String report = generator.generate(testData);
    assertTrue(report.startsWith("Report: Sales Summary"));
}
```

### 7.3 부수효과가 있는 메서드의 Characterization Test

값을 반환하지 않고 상태를 변경하는 메서드의 경우, 상태 변경을 검증한다:

```java
@Test
public void testProcessOrder_updatesStatus() {
    Order order = createTestOrder();
    processor.processOrder(order);

    // 부수효과(상태 변경)를 검증
    assertEquals("PROCESSED", order.getStatus());
    assertNotNull(order.getProcessedDate());
}
```

---

## 요약

- **Characterization Test(특성 테스트)** 는 코드의 "올바른" 동작이 아닌 **"현재" 동작을 기록**하는 테스트다.
- 작성 절차: **틀린 assertion 작성 → 실행하여 실패 → 실제 값 확인 → 수정 → 통과 확인**의 단계를 따른다.
- **경계값과 특수 케이스**에 대한 Characterization test를 작성하면 코드의 미묘한 동작을 포착할 수 있다.
- **버그를 발견해도 현재 동작 그대로 기록**하고, 버그 수정은 별도 작업으로 분리한다.
- **탐색적(exploratory) 테스트**를 통해 코드의 동작을 이해하고, 그 결과를 Characterization test로 변환한다.
- 테스트 작성 범위는 **실용적 heuristic**을 따른다: 변경 영역에 집중, 조건 분기마다 테스트, 데이터 변환 지점에 테스트, 충분한 확신이 들 때까지 작성.
- Characterization test는 레거시 코드를 변경하기 위한 **안전망을 구축하는 가장 실용적인 방법**이다.

---

## 다음 챕터와의 연결

Chapter 14 "나를 미치게 하는 라이브러리 의존 관계 (Dependencies on Libraries Are Killing Me)"에서는 라이브러리에 대한 의존성이 테스트와 변경을 어떻게 어렵게 만드는지, 그리고 라이브러리 의존성을 관리하여 코드의 유연성을 유지하는 방법을 다룬다.
