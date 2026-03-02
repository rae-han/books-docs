# Chapter 3: Functions (함수)

## 핵심 질문

함수를 어떻게 짜야 읽는 사람이 프로그램 내부를 직관적으로 파악할 수 있는가? 의도를 분명히 표현하는 함수의 속성은 무엇인가?

---

## 1. 작게 만들어라!

함수를 만드는 첫째 규칙은 **'작게!'**다. 함수를 만드는 둘째 규칙은 **'더 작게!'**다.

Robert C. Martin은 지난 40여 년 동안 온갖 크기로 함수를 구현해 본 경험을 바탕으로 작은 함수가 좋다고 확신한다. 다음 예제를 보자.

```java
// 나쁜 예 — 목록 3-1: 너무 길고 추상화 수준이 뒤섞인 함수
public static String testableHtml(
    PageData pageData,
    boolean includeSuiteSetup
) throws Exception {
    WikiPage wikiPage = pageData.getWikiPage();
    StringBuffer buffer = new StringBuffer();
    if (pageData.hasAttribute("Test")) {
        if (includeSuiteSetup) {
            WikiPage suiteSetup =
                PageCrawlerImpl.getInheritedPage(
                    SuiteResponder.SUITE_SETUP_NAME, wikiPage);
            if (suiteSetup != null) {
                WikiPagePath pagePath =
                    suiteSetup.getPageCrawler().getFullPath(suiteSetup);
                String pagePathName = PathParser.render(pagePath);
                buffer.append("!include -setup .")
                    .append(pagePathName)
                    .append("\n");
            }
        }
        // ... (생략) — 비슷한 패턴이 4번 반복
    }
    pageData.setContent(buffer.toString());
    return pageData.getHtml();
}
```

```java
// 좋은 예 — 목록 3-3: 리팩터링 완료
public static String renderPageWithSetupsAndTeardowns(
    PageData pageData, boolean isSuite) throws Exception {
    if (isTestPage(pageData))
        includeSetupAndTeardownPages(pageData, isSuite);
    return pageData.getHtml();
}
```

> **Uncle Bob의 경험**: 1999년 켄트 벡의 집을 방문했을 때, 켄트가 보여준 Sparkle이라는 자바/스윙 프로그램에서 모든 함수가 2줄, 3줄, 4줄 정도였다. 각 함수가 너무도 명백했고, 각 함수가 이야기 하나를 표현했으며, 각 함수가 너무도 멋지게 다음 무대를 준비했다. 바로 이것이 답이다.

### 블록과 들여쓰기

`if` 문/`else` 문/`while` 문 등에 들어가는 블록은 **한 줄**이어야 한다. 대개 거기서 함수를 호출한다. 바깥을 감싸는 함수가 작아질 뿐 아니라, 블록 안에서 호출하는 함수 이름을 적절히 짓는다면 코드를 이해하기도 쉬워진다.

이 말은 중첩 구조가 생길 만큼 함수가 커져서는 안 된다는 뜻이다. 함수에서 **들여쓰기 수준은 1단이나 2단을 넘어서면 안 된다.**

---

## 2. 한 가지만 해라!

> **함수는 한 가지를 해야 한다. 그 한 가지를 잘 해야 한다. 그 한 가지만을 해야 한다.**

이 충고에서 문제는 그 '한 가지'가 무엇인지 알기 어렵다는 점이다. 목록 3-3은 한 가지만 하는가? 세 가지를 한다고 주장할 수도 있다:

1. 페이지가 테스트 페이지인지 판단한다.
2. 그렇다면 설정 페이지와 해제 페이지를 넣는다.
3. 페이지를 HTML로 렌더링한다.

하지만 위 세 단계는 지정된 함수 이름 아래에서 **추상화 수준이 하나**다. 함수는 간단한 **TO 문단**(*TO — LOGO 언어에서 사용하는 키워드로, 루비나 파이썬의 `def`와 같다. '~하려면'이라는 의미.*)으로 기술할 수 있다:

> TO RenderPageWithSetupsAndTeardowns, 페이지가 테스트 페이지인지 확인한 후 테스트 페이지라면 설정 페이지와 해제 페이지를 넣는다. 테스트 페이지든 아니든 페이지를 HTML로 렌더링한다.

**함수가 '한 가지'만 하는지 판단하는 방법**: 의미 있는 이름으로 다른 함수를 추출할 수 있다면 그 함수는 여러 작업을 하는 셈이다.

---

## 3. 함수 당 추상화 수준은 하나로!

함수가 확실히 '한 가지' 작업만 하려면 함수 내 모든 문장의 **추상화 수준이 동일**해야 한다.

| 추상화 수준 | 예시 |
|---|---|
| **높음** | `getHtml()` |
| **중간** | `String pagePathName = PathParser.render(pagePath);` |
| **낮음** | `.append("\n")` |

한 함수 내에 추상화 수준을 섞으면 코드를 읽는 사람이 헷갈린다. 근본 개념과 세부사항을 뒤섞기 시작하면, 깨어진 창문처럼 사람들이 함수에 세부사항을 점점 더 추가한다.

### 위에서 아래로 코드 읽기: 내려가기 규칙

코드는 위에서 아래로 이야기처럼 읽혀야 좋다. 한 함수 다음에는 추상화 수준이 한 단계 낮은 함수가 온다. 일련의 TO 문단을 읽듯이 프로그램이 읽혀야 한다:

```
TO 설정 페이지와 해제 페이지를 포함하려면,
    설정 페이지를 포함하고, 테스트 페이지 내용을 포함하고, 해제 페이지를 포함한다.
  TO 설정 페이지를 포함하려면,
      슈트이면 슈트 설정 페이지를 포함한 후 일반 설정 페이지를 포함한다.
    TO 슈트 설정 페이지를 포함하려면,
        부모 계층에서 "SuiteSetUp" 페이지를 찾아 include 문과 페이지 경로를 추가한다.
```

> **핵심 통찰**: 위에서 아래로 TO 문단을 읽어내려 가듯이 코드를 구현하면 추상화 수준을 일관되게 유지하기가 쉬워진다.

---

## 4. Switch 문

`switch` 문은 작게 만들기 어렵다. 본질적으로 `switch` 문은 N가지를 처리한다. 하지만 각 `switch` 문을 **저차원 클래스에 숨기고 절대로 반복하지 않는 방법**은 있다. **다형성(polymorphism)** 을 이용한다.

```java
// 나쁜 예 — 직원 유형에 따라 다른 값을 계산
public Money calculatePay(Employee e) throws InvalidEmployeeType {
    switch (e.type) {
        case COMMISSIONED:
            return calculateCommissionedPay(e);
        case HOURLY:
            return calculateHourlyPay(e);
        case SALARIED:
            return calculateSalariedPay(e);
        default:
            throw new InvalidEmployeeType(e.type);
    }
}
```

위 함수의 문제점:

| # | 문제 | 설명 |
|---|---|---|
| 1 | 함수가 길다 | 새 직원 유형 추가 시 더 길어짐 |
| 2 | '한 가지' 작업만 수행하지 않는다 | 유형 판별 + 계산 |
| 3 | SRP 위반 | 코드를 변경할 이유가 여럿 |
| 4 | OCP 위반 | 새 직원 유형 추가 시 코드 변경 필요 |
| 5 | 동일 구조 무한 반복 | `isPayday(Employee e)`, `deliverPay(Employee e, Money pay)` 등 |

```java
// 좋은 예 — 추상 팩토리로 switch 문을 숨김
public abstract class Employee {
    public abstract boolean isPayday();
    public abstract Money calculatePay();
    public abstract void deliverPay(Money pay);
}

public interface EmployeeFactory {
    public Employee makeEmployee(EmployeeRecord r) throws InvalidEmployeeType;
}

public class EmployeeFactoryImpl implements EmployeeFactory {
    public Employee makeEmployee(EmployeeRecord r) throws InvalidEmployeeType {
        switch (r.type) {
            case COMMISSIONED:
                return new CommissionedEmployee(r);
            case HOURLY:
                return new HourlyEmployee(r);
            case SALARIED:
                return new SalariedEmployee(r);
            default:
                throw new InvalidEmployeeType(r.type);
        }
    }
}
```

`switch` 문을 **추상 팩토리(ABSTRACT FACTORY)** 에 꽁꽁 숨긴다. 팩토리는 `switch` 문을 사용해 적절한 `Employee` 파생 클래스의 인스턴스를 생성하고, `calculatePay`, `isPayday`, `deliverPay` 등은 `Employee` 인터페이스를 거쳐 호출된다. 다형성으로 인해 실제 파생 클래스의 함수가 실행된다.

> **핵심 통찰**: `switch` 문은 단 한 번만 참아준다 — 다형적 객체를 생성하는 코드 안에서. 이렇게 상속 관계로 숨긴 후에는 절대로 다른 코드에 노출하지 않는다.

---

## 5. 서술적인 이름을 사용하라!

좋은 이름이 주는 가치는 아무리 강조해도 지나치지 않다. 워드가 말했던 원칙을 기억하라: *"코드를 읽으면서 짐작했던 기능을 각 루틴이 그대로 수행한다면 깨끗한 코드라 불러도 되겠다."*

서술적인 이름의 원칙:

| 원칙 | 설명 |
|---|---|
| **길어도 괜찮다** | 길고 서술적인 이름 > 짧고 어려운 이름 > 길고 서술적인 주석 |
| **시간을 들여도 괜찮다** | IDE를 사용해 이런저런 이름을 시도한 후 최대한 서술적인 이름을 고른다 |
| **일관성이 있어야 한다** | 모듈 내에서 같은 문구, 명사, 동사를 사용 |

```
// 일관적인 이름의 예
includeSetupAndTeardownPages
includeSetupPages
includeSuiteSetupPage
includeSetupPage
```

> 문체가 비슷하면 "includeTeardownPages, includeSuiteTeardownPage, includeTeardownPage도 있나요?"라는 질문이 자연스럽게 떠오른다. 당연히 있다. **'짐작하는 대로'**다.

---

## 6. 함수 인수

함수에서 이상적인 인수 개수는 **0개(무항)**다. 다음은 1개(단항), 다음은 2개(이항)다. 3개(삼항)는 가능한 피하는 편이 좋다. 4개 이상(다항)은 특별한 이유가 있어도 사용하면 안 된다.

| 인수 개수 | 평가 | 이유 |
|---|---|---|
| **0개 (무항)** | 최선 | 이해하기 가장 쉬움 |
| **1개 (단항)** | 차선 | 질문 또는 변환 |
| **2개 (이항)** | 주의 필요 | 순서 기억 부담, 무시되는 인수 |
| **3개 (삼항)** | 가능한 피함 | 순서/주춤/무시 문제 2배 이상 |
| **4개+ (다항)** | 금지 | 특별한 이유가 있어도 안 됨 |

### 6.1 많이 쓰는 단항 형식

인수 1개를 넘기는 흔한 경우 두 가지:

1. **인수에 질문을 던지는 경우**: `boolean fileExists("MyFile")`
2. **인수를 변환해 결과를 반환하는 경우**: `InputStream fileOpen("MyFile")`

드물지만 유용한 형식으로 **이벤트**가 있다: `passwordAttemptFailedNtimes(int attempts)` — 입력 인수만 있고 출력 인수는 없다.

변환 함수에서 출력 인수를 사용하면 혼란을 일으킨다:

```java
// 나쁜 예 — 변환인데 반환값 없음
void includeSetupPageInto(StringBuffer pageText)

// 좋은 예 — 변환 형태 유지
StringBuffer transform(StringBuffer in)
```

### 6.2 플래그 인수

**플래그 인수는 추하다.** 함수로 부울 값을 넘기는 관례는 정말로 끔찍하다. 함수가 한꺼번에 여러 가지를 처리한다고 대놓고 공표하는 셈이니까!

```java
// 나쁜 예
render(true)

// 좋은 예 — 함수를 나눔
renderForSuite()
renderForSingleTest()
```

### 6.3 이항 함수

인수가 2개인 함수는 1개인 함수보다 이해하기 어렵다. `writeField(name)`은 `writeField(outputStream, name)`보다 쉽게 읽힌다.

이항 함수가 적절한 경우: `Point p = new Point(0, 0)` — 인수 2개가 한 값을 표현하는 두 요소이며, 자연적인 순서가 있다.

이항 함수를 단항 함수로 바꾸는 방법:
- `outputStream.writeField(name)` — 메서드를 클래스 구성원으로
- `outputStream`을 현재 클래스 구성원 변수로 만들어 인수 제거
- `FieldWriter` 새 클래스를 만들어 구성자에서 `outputStream`을 받음

### 6.4 인수 객체

인수가 2~3개 필요하다면 일부를 **독자적인 클래스 변수**로 선언할 가능성을 짚어본다:

```java
// 인수 3개
Circle makeCircle(double x, double y, double radius);

// 인수 2개 — 개념을 표현하는 객체 사용
Circle makeCircle(Point center, double radius);
```

### 6.5 동사와 키워드

단항 함수는 함수와 인수가 **동사/명사 쌍**을 이뤄야 한다:

```java
write(name)            // 이해 가능하지만...
writeField(name)       // 더 좋다 — name이 field라는 사실이 드러남

assertEquals(expected, actual)              // 인수 순서 기억 필요
assertExpectedEqualsActual(expected, actual) // 인수 순서가 이름에 포함
```

---

## 7. 부수 효과를 일으키지 마라!

부수 효과는 거짓말이다. 함수에서 한 가지를 하겠다고 약속하고선 남몰래 다른 짓도 하니까.

```java
// 나쁜 예 — 숨겨진 부수 효과
public class UserValidator {
    private Cryptographer cryptographer;

    public boolean checkPassword(String userName, String password) {
        User user = UserGateway.findByName(userName);
        if (user != User.NULL) {
            String codedPhrase = user.getPhraseEncodedByPassword();
            String phrase = cryptographer.decrypt(codedPhrase, password);
            if ("Valid Password".equals(phrase)) {
                Session.initialize();  // ← 부수 효과!
                return true;
            }
        }
        return false;
    }
}
```

`checkPassword` 함수는 이름 그대로 암호를 확인한다. 이름만 봐서는 세션을 초기화한다는 사실이 드러나지 않는다. 이런 부수 효과는 **시간적인 결합(temporal coupling)** 을 초래한다 — `checkPassword`는 세션을 초기화해도 괜찮은 경우에만 호출이 가능하다.

만약 시간적인 결합이 필요하다면 함수 이름에 분명히 명시한다: `checkPasswordAndInitializeSession` (물론 '한 가지'만 한다는 규칙을 위반하지만).

### 출력 인수

일반적으로 출력 인수는 피해야 한다:

```java
// 혼란스러운 코드 — s는 입력인가 출력인가?
appendFooter(s);

// 좋은 예 — this를 출력 인수로 사용
report.appendFooter()
```

> **핵심 통찰**: 함수에서 상태를 변경해야 한다면 함수가 속한 객체 상태를 변경하는 방식을 택한다.

---

## 8. 명령과 조회를 분리하라!

함수는 뭔가를 **수행하거나** 뭔가에 **답하거나** 둘 중 하나만 해야 한다. 둘 다 하면 혼란을 초래한다.

```java
// 나쁜 예 — 명령과 조회가 혼합됨
public boolean set(String attribute, String value);

// 호출 시 혼란
if (set("username", "unclebob"))...
// "username"이 "unclebob"으로 설정되어 있는지 확인? 설정하는 코드?
```

```java
// 좋은 예 — 명령과 조회 분리
if (attributeExists("username")) {
    setAttribute("username", "unclebob");
    ...
}
```

---

## 9. 오류 코드보다 예외를 사용하라!

명령 함수에서 오류 코드를 반환하면 여러 단계로 중첩되는 코드를 야기한다:

```java
// 나쁜 예 — 오류 코드 반환 → 중첩된 if 문
if (deletePage(page) == E_OK) {
    if (registry.deleteReference(page.name) == E_OK) {
        if (configKeys.deleteKey(page.name.makeKey()) == E_OK) {
            logger.log("page deleted");
        } else {
            logger.log("configKey not deleted");
        }
    } else {
        logger.log("deleteReference from registry failed");
    }
} else {
    logger.log("delete failed");
    return E_ERROR;
}
```

```java
// 좋은 예 — 예외 사용 → 깔끔한 코드
try {
    deletePage(page);
    registry.deleteReference(page.name);
    configKeys.deleteKey(page.name.makeKey());
}
catch (Exception e) {
    logger.log(e.getMessage());
}
```

### Try/Catch 블록 뽑아내기

`try/catch` 블록은 코드 구조에 혼란을 일으키므로 별도 함수로 뽑아내는 편이 좋다:

```java
// 정상 동작과 오류 처리 분리
public void delete(Page page) {
    try {
        deletePageAndAllReferences(page);
    }
    catch (Exception e) {
        logError(e);
    }
}

private void deletePageAndAllReferences(Page page) throws Exception {
    deletePage(page);
    registry.deleteReference(page.name);
    configKeys.deleteKey(page.name.makeKey());
}

private void logError(Exception e) {
    logger.log(e.getMessage());
}
```

### 오류 처리도 한 가지 작업이다

함수에 키워드 `try`가 있다면 함수는 `try` 문으로 시작해 `catch`/`finally` 문으로 끝나야 한다.

### Error.java 의존성 자석

```java
// 오류 코드를 열거형으로 정의하면 의존성 자석이 됨
public enum Error {
    OK, INVALID, NO_SUCH, LOCKED, OUT_OF_RESOURCES, WAITING_FOR_EVENT;
}
```

위 클래스는 **의존성 자석(magnet)**이다. `Error` enum이 변하면 사용하는 클래스 전부를 재컴파일/재배치해야 한다. 오류 코드 대신 **예외를 사용하면** 새 예외는 `Exception` 클래스에서 파생되므로 재컴파일/재배치 없이도 새 예외 클래스를 추가할 수 있다(OCP).

---

## 10. 반복하지 마라! (DRY)

중복은 소프트웨어에서 **모든 악의 근원**이다. 많은 원칙과 기법이 중복을 없애거나 제어할 목적으로 나왔다:

| 분야 | 중복 제거 전략 |
|---|---|
| 관계형 데이터베이스 | 정규 형식 (E.F. Codd) |
| 객체 지향 프로그래밍 | 부모 클래스로 코드를 몰아 중복 제거 |
| 구조적 프로그래밍 | 하위 루틴 |
| AOP | 횡단 관심사의 중복 제거 |
| COP | 컴포넌트 기반 중복 제거 |

> **핵심 통찰**: 하위 루틴을 발명한 이래로 소프트웨어 개발에서 일어난 혁신은 소스 코드에서 중복을 제거하려는 지속적인 노력으로 보인다.

---

## 11. 구조적 프로그래밍

데이크스트라의 구조적 프로그래밍 원칙에 따르면, 모든 함수와 함수 내 모든 블록에 입구와 출구가 하나만 존재해야 한다 — 함수는 `return` 문이 하나여야 하며, 루프 안에서 `break`나 `continue`를 사용해선 안 되고, `goto`는 절대로 안 된다.

하지만 **함수가 작다면** 위 규칙은 별 이익을 제공하지 못한다. 함수를 작게 만든다면 간혹 `return`, `break`, `continue`를 여러 차례 사용해도 괜찮다. 오히려 때로는 단일 입/출구 규칙보다 의도를 표현하기 쉬워진다. 반면, `goto` 문은 큰 함수에서만 의미가 있으므로 작은 함수에서는 피해야 한다.

---

## 12. 함수를 어떻게 짜죠?

소프트웨어를 짜는 행위는 여느 글짓기와 비슷하다:

1. **초안 작성**: 처음에는 길고 복잡하다. 들여쓰기 단계도 많고, 중복된 루프도 많고, 인수 목록도 길고, 이름은 즉흥적이고 코드는 중복된다.
2. **테스트 케이스 작성**: 그 서투른 코드를 빠짐없이 테스트하는 단위 테스트 케이스를 만든다.
3. **리팩터링**: 코드를 다듬고, 함수를 만들고, 이름을 바꾸고, 중복을 제거하고, 메서드를 줄이고 순서를 바꾼다. 때로는 전체 클래스를 쪼개기도 한다.
4. **테스트 통과 확인**: 이 와중에도 코드는 항상 단위 테스트를 통과한다.

> **Uncle Bob의 경험**: 처음부터 이 장에서 설명한 규칙을 따르는 함수를 탁 짜내지 않는다. 그게 가능한 사람은 없으리라.

---

## 13. 결론: 함수는 언어다

모든 시스템은 프로그래머가 설계한 **도메인 특화 언어(DSL)** 로 만들어진다. 함수는 그 언어에서 **동사**며, 클래스는 **명사**다.

대가 프로그래머는 시스템을 (구현할) 프로그램이 아니라 **(풀어갈) 이야기**로 여긴다. 프로그래밍 언어라는 수단을 사용해 좀 더 풍부하고 좀 더 표현력이 강한 언어를 만들어 이야기를 풀어간다.

이 장의 규칙을 따르면 길이가 짧고, 이름이 좋고, 체계가 잡힌 함수가 나온다. 하지만 진짜 목표는 **시스템이라는 이야기를 풀어가는 데** 있다는 사실을 명심해야 한다.

---

## 함수 규칙 종합

| # | 규칙 | 핵심 |
|---|---|---|
| 1 | 작게 만들어라 | 함수는 20줄도 길다. 2~4줄이 이상적 |
| 2 | 한 가지만 해라 | 의미 있는 이름으로 다른 함수를 추출 가능하면 여러 작업 중 |
| 3 | 추상화 수준은 하나로 | 내려가기 규칙: 위→아래로 추상화 수준 하강 |
| 4 | switch 문은 다형성으로 숨겨라 | 추상 팩토리 안에 단 한 번만 허용 |
| 5 | 서술적인 이름 | 길고 서술적인 이름 > 짧고 어려운 이름 |
| 6 | 인수는 적게 | 0개 > 1개 > 2개, 3개 이상은 피함 |
| 7 | 부수 효과 금지 | 시간적 결합 초래, 이름에 드러나지 않는 동작 |
| 8 | 명령/조회 분리 | 수행하거나 답하거나 둘 중 하나 |
| 9 | 예외 사용 | 오류 코드 대신 예외, try/catch는 별도 함수로 |
| 10 | DRY | 중복은 모든 악의 근원 |
| 11 | 구조적 프로그래밍 | 작은 함수에서는 return/break/continue 괜찮음 |

---

## 요약

- **함수는 작아야 한다** — 20줄도 길다. 들여쓰기는 1~2단까지만
- **함수는 한 가지만 해야 한다** — 추상화 수준이 하나인 단계만 수행
- **위에서 아래로 읽혀야 한다** — 내려가기 규칙을 따라 추상화 수준을 순차적으로 낮춤
- **switch 문은 다형성 뒤에 숨겨라** — 추상 팩토리에 단 한 번만 허용
- **서술적인 이름을 사용하라** — 길고 서술적인 이름이 짧고 어려운 이름보다 좋다
- **인수는 가능한 줄여라** — 0개가 최선, 플래그 인수는 금지
- **부수 효과를 일으키지 마라** — 이름에 드러나지 않는 동작은 거짓말
- **명령과 조회를 분리하라** — 뭔가를 수행하거나 답하거나 둘 중 하나
- **오류 코드 대신 예외를 사용하라** — try/catch 블록은 별도 함수로 분리
- **중복을 없애라** — DRY 원칙은 소프트웨어 발전의 원동력
- **처음부터 완벽한 함수를 짜는 사람은 없다** — 초안을 쓰고, 테스트하고, 다듬어라

---

## 다른 챕터와의 관계

- **← Chapter 1 (깨끗한 코드)**: 비야네 스트롭스트룹이 강조한 "한 가지를 제대로 한다"는 원칙이 이 장의 핵심 규칙이다
- **← Chapter 2 (의미 있는 이름)**: 서술적인 이름, 동사와 키워드 형식 등 2장의 이름 짓기 규칙이 함수에 직접 적용된다
- **→ Chapter 4 (주석)**: 함수를 작고 명확하게 만들면 주석이 불필요해진다. "함수나 변수로 표현할 수 있다면 주석을 달지 마라"
- **→ Chapter 6 (객체와 자료 구조)**: 출력 인수를 `this`로 대체하는 패턴, 객체 지향 설계와 함수 설계의 관계를 다룬다
- **→ Chapter 7 (오류 처리)**: 이 장에서 소개한 "오류 코드보다 예외를 사용하라"가 7장에서 본격적으로 다뤄진다
- **→ Chapter 10 (클래스)**: 함수를 작게 유지하면 자연스럽게 클래스로 분리되며, 클래스 설계 원칙(SRP)과 연결된다
- **→ Chapter 17 (냄새와 휴리스틱)**: [G30] 함수는 한 가지만 해야 한다, [F1]~[F4] 함수 관련 냄새가 이 장의 규칙을 체크리스트로 정리한 것이다
