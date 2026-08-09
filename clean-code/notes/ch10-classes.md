# Chapter 10: Classes (클래스)

## 핵심 질문

깨끗한 클래스는 어떻게 설계하는가? 클래스 크기의 기준은 무엇이며, 응집도와 결합도를 어떻게 관리해야 변경에 유연한 시스템을 만들 수 있는가?

---

## 1. 클래스 체계

클래스를 정의하는 표준 자바 관례에 따르면, 변수 목록이 가장 먼저 나온다. 순서는 다음과 같다:

| 순서 | 종류 | 설명 |
|---|---|---|
| 1 | `public static` 상수 | 정적 공개 상수가 맨 처음 |
| 2 | `private static` 변수 | 정적 비공개 변수 |
| 3 | `private` 인스턴스 변수 | 비공개 인스턴스 변수 |
| 4 | 공개 함수 | 공개 메서드 |
| 5 | 비공개 함수 | 자신을 호출하는 공개 함수 직후에 배치 |

공개 변수가 필요한 경우는 거의 없다. 이러한 배치를 따르면 추상화 단계가 순차적으로 내려가므로 프로그램이 **신문 기사처럼 읽힌다**.

### 캡슐화

변수와 유틸리티 함수는 가능한 공개하지 않는 편이 낫지만, 반드시 숨겨야 한다는 법칙도 없다. 때로는 테스트 코드의 접근을 위해 `protected`로 선언하기도 한다.

하지만 캡슐화를 풀어주는 결정은 언제나 **최후의 수단**이다. 비공개 상태를 유지할 온갖 방법을 먼저 강구해야 한다.

---

## 2. 클래스는 작아야 한다!

클래스를 만들 때 **첫 번째 규칙도 크기, 두 번째 규칙도 크기**다. 더 작아야 한다. 하지만 함수는 물리적인 행 수로 크기를 측정하는 반면, 클래스는 **맡은 책임(*Responsibility — Rebecca Wirfs-Brock 등의 [RDD]에서 정의한 개념으로, 클래스가 변경되어야 할 이유를 의미한다.*)의 수**로 크기를 측정한다.

다음은 공개 메서드가 약 70개인 `SuperDashboard` 클래스다:

```java
// 나쁜 예 — 너무 많은 책임 (메서드 70개 이상)
public class SuperDashboard extends JFrame implements MetaDataUser {
    public String getCustomizerLanguagePath()
    public void setSystemConfigPath(String systemConfigPath)
    public String getSystemConfigDocument()
    public boolean getGuruState()
    public boolean getNoviceState()
    public void showObject(MetaObject object)
    public void showProgress(String s)
    public Component getLastFocusedComponent()
    public void setLastFocused(Component lastFocused)
    public int getMajorVersionNumber()
    public int getMinorVersionNumber()
    public int getBuildNumber()
    // ... 많은 메서드가 이어진다 ...
}
```

메서드 수를 다섯 개로 줄여도 여전히 문제가 될 수 있다:

```java
// 여전히 나쁜 예 — 메서드 수는 적지만 책임이 둘
public class SuperDashboard extends JFrame implements MetaDataUser {
    public Component getLastFocusedComponent()
    public void setLastFocused(Component lastFocused)
    public int getMajorVersionNumber()
    public int getMinorVersionNumber()
    public int getBuildNumber()
}
```

메서드 다섯 개뿐이지만, 이 클래스에는 **두 가지 책임**이 있다: 스윙 컴포넌트 관리와 소프트웨어 버전 정보 추적.

### 클래스 이름 짓기와 책임 판별법

클래스 이름은 해당 클래스의 책임을 기술해야 한다:

- **간결한 이름이 떠오르지 않는다면** → 클래스 크기가 너무 큰 것이다
- **이름이 모호하다면** → 클래스 책임이 너무 많은 것이다
- 이름에 `Processor`, `Manager`, `Super` 등 **모호한 단어**가 있다면 → 여러 책임을 떠안았다는 증거다

**25단어 테스트**: 클래스 설명을 "만일(if)", "그리고(and)", "~(하)며(or)", "하지만(but)"을 사용하지 않고 25단어 내외로 가능해야 한다.

> "SuperDashboard는 마지막으로 포커스를 얻었던 컴포넌트에 접근하는 방법을 제공하**며**, 버전과 빌드 번호를 추적하는 메커니즘을 제공한다."

첫 번째 "~하며"가 바로 **책임이 너무 많다는 증거**다.

---

## 3. 단일 책임 원칙 (SRP)

**단일 책임 원칙(Single Responsibility Principle, SRP)** 은 클래스나 모듈을 **변경할 이유가 하나, 단 하나뿐이어야 한다**는 원칙이다.

`SuperDashboard`에서 버전 정보를 추출하면:

```java
// 좋은 예 — 단일 책임 클래스
public class Version {
    public int getMajorVersionNumber()
    public int getMinorVersionNumber()
    public int getBuildNumber()
}
```

`Version` 클래스는 다른 애플리케이션에서 재사용하기 아주 쉬운 구조다.

### SRP를 무시하는 이유

SRP는 이해하고 지키기 수월한 개념이지만, 클래스 설계자가 **가장 무시하는 규칙** 중 하나다. 이유는 다음과 같다:

1. **'돌아가는 소프트웨어'에만 초점** — 프로그램이 돌아가면 일이 끝났다고 여기고, 다음 관심사인 '깨끗하고 체계적인 소프트웨어'로 전환하지 않는다
2. **큰 그림 우려** — 많은 개발자가 "자잘한 단일 책임 클래스가 많아지면 큰 그림을 이해하기 어려워진다"고 걱정한다

하지만 작은 클래스가 많은 시스템이든 큰 클래스가 몇 개뿐인 시스템이든, **돌아가는 부품 수와 익힐 내용의 양은 비슷하다**.

> **핵심 통찰**: "도구 상자를 어떻게 관리하고 싶은가? 작은 서랍을 많이 두고 기능과 이름이 명확한 컴포넌트를 나눠 넣고 싶은가? 아니면 큰 서랍 몇 개를 두고 모두를 던져 넣고 싶은가?"

**큰 클래스 몇 개가 아니라 작은 클래스 여럿으로 이뤄진 시스템이 더 바람직하다.** 작은 클래스는 각자 맡은 책임이 하나며, 변경할 이유가 하나며, 다른 작은 클래스와 협력해 시스템에 필요한 동작을 수행한다.

---

## 4. 응집도 (Cohesion)

클래스는 인스턴스 변수 수가 작아야 한다. 각 클래스 메서드는 클래스 인스턴스 변수를 **하나 이상** 사용해야 한다. 메서드가 변수를 더 많이 사용할수록 응집도가 더 높다.

```java
// 좋은 예 — 응집도가 아주 높은 클래스
public class Stack {
    private int topOfStack = 0;
    List<Integer> elements = new LinkedList<Integer>();

    public int size() {
        return topOfStack;
    }

    public void push(int element) {
        topOfStack++;
        elements.add(element);
    }

    public int pop() throws PoppedWhenEmpty {
        if (topOfStack == 0)
            throw new PoppedWhenEmpty();
        int element = elements.get(--topOfStack);
        elements.remove(topOfStack);
        return element;
    }
}
```

`size()`를 제외한 두 메서드는 두 변수를 모두 사용한다. 응집도가 아주 높은 클래스다.

### 응집도가 낮아지는 신호

'함수를 작게, 매개변수 목록을 짧게'라는 전략을 따르다 보면 때때로 **몇몇 메서드만이 사용하는 인스턴스 변수가 아주 많아진다**. 이는 십중팔구 **새로운 클래스로 쪼개야 한다는 신호**다.

---

## 5. 응집도를 유지하면 작은 클래스 여럿이 나온다

큰 함수를 작은 함수 여럿으로 나누기만 해도 클래스 수가 많아진다:

1. 큰 함수 일부를 작은 함수로 빼내려 하는데, 빼내려는 코드가 변수 네 개를 사용한다
2. 네 변수를 새 함수에 인수로 넘기는 대신, **클래스 인스턴스 변수로 승격**하면 함수를 쪼개기 쉬워진다
3. 그러면 몇몇 함수만 사용하는 인스턴스 변수가 늘어나 **응집력이 낮아진다**
4. 응집력을 잃는다면 **쪼개라!** — 몇몇 함수가 몇몇 변수만 사용한다면 독자적인 클래스로 분리

### PrintPrimes 리팩터링 예제

커누스 교수의 `PrintPrimes` 프로그램을 리팩터링한 사례를 보자.

```java
// 나쁜 예 — 하나의 거대한 함수
public class PrintPrimes {
    public static void main(String[] args) {
        final int M = 1000;
        final int RR = 50;
        final int CC = 4;
        final int WW = 10;
        final int ORDMAX = 30;
        int P[] = new int[M + 1];
        int PAGENUMBER;
        int PAGEOFFSET;
        // ... 엉망진창인 코드가 이어진다
    }
}
```

리팩터링 후에는 **세 가지 책임**으로 분리된다:

```java
// 좋은 예 — 책임 1: 실행 환경
public class PrimePrinter {
    public static void main(String[] args) {
        final int NUMBER_OF_PRIMES = 1000;
        int[] primes = PrimeGenerator.generate(NUMBER_OF_PRIMES);
        final int ROWS_PER_PAGE = 50;
        final int COLUMNS_PER_PAGE = 4;
        RowColumnPagePrinter tablePrinter =
            new RowColumnPagePrinter(ROWS_PER_PAGE,
                COLUMNS_PER_PAGE,
                "The First " + NUMBER_OF_PRIMES + " Prime Numbers");
        tablePrinter.print(primes);
    }
}

// 좋은 예 — 책임 2: 출력 형식
public class RowColumnPagePrinter {
    private int rowsPerPage;
    private int columnsPerPage;
    private int numbersPerPage;
    private String pageHeader;
    private PrintStream printStream;
    // ... 출력 관련 메서드
}

// 좋은 예 — 책임 3: 소수 생성 알고리즘
public class PrimeGenerator {
    private static int[] primes;
    private static ArrayList<Integer> multiplesOfPrimeFactors;

    protected static int[] generate(int n) {
        primes = new int[n];
        multiplesOfPrimeFactors = new ArrayList<Integer>();
        set2AsFirstPrime();
        checkOddNumbersForSubsequentPrimes();
        return primes;
    }
    // ... 소수 생성 관련 메서드
}
```

| 클래스 | 책임 | 변경 시점 |
|---|---|---|
| `PrimePrinter` | 실행 환경 (main) | 호출 방식이 달라질 때 (예: SOAP 서비스) |
| `RowColumnPagePrinter` | 출력 형식 | 출력 모양새를 바꿀 때 |
| `PrimeGenerator` | 소수 생성 알고리즘 | 소수 계산 알고리즘이 바뀔 때 |

> **핵심 통찰**: 리팩터링 과정에서 가장 먼저 **원래 프로그램의 정확한 동작을 검증하는 테스트 슈트를 작성**했다. 그런 다음, 한 번에 하나씩 수차례에 걸쳐 조금씩 코드를 변경하면서 매번 테스트를 수행해 동일하게 동작하는지 확인했다. 재구현이 아니라 **점진적 개선**이다.

---

## 6. 변경하기 쉬운 클래스

대다수 시스템은 지속적인 변경이 가해진다. 뭔가 변경할 때마다 시스템이 의도대로 동작하지 않을 **위험**이 따른다. 깨끗한 시스템은 클래스를 체계적으로 정리해 변경에 수반하는 위험을 낮춘다.

### SQL 클래스 리팩터링

```java
// 나쁜 예 — 변경이 필요해 '손대야' 하는 클래스
public class Sql {
    public Sql(String table, Column[] columns)
    public String create()
    public String insert(Object[] fields)
    public String selectAll()
    public String findByKey(String keyColumn, String keyValue)
    public String select(Column column, String pattern)
    public String select(Criteria criteria)
    public String preparedInsert()
    private String columnList(Column[] columns)
    private String valuesList(Object[] fields, final Column[] columns)
    private String selectWithCriteria(String criteria)
    private String placeholderList(Column[] columns)
}
```

이 클래스는 **SRP를 위반**한다:
- 새로운 SQL 문을 지원하려면 반드시 `Sql` 클래스에 손대야 한다
- 기존 SQL 문 하나를 수정할 때도 반드시 `Sql` 클래스에 손대야 한다
- `selectWithCriteria`라는 비공개 메서드는 `select` 문을 처리할 때만 사용한다 — **클래스 일부에서만 사용되는 비공개 메서드는 코드 개선의 잠재적 여지를 시사**한다

```java
// 좋은 예 — 닫힌 클래스 집합
abstract public class Sql {
    public Sql(String table, Column[] columns)
    abstract public String generate();
}

public class CreateSql extends Sql {
    public CreateSql(String table, Column[] columns)
    @Override public String generate()
}

public class SelectSql extends Sql {
    public SelectSql(String table, Column[] columns)
    @Override public String generate()
}

public class InsertSql extends Sql {
    public InsertSql(String table, Column[] columns, Object[] fields)
    @Override public String generate()
    private String valuesList(Object[] fields, final Column[] columns)
}

public class SelectWithCriteriaSql extends Sql {
    public SelectWithCriteriaSql(String table, Column[] columns, Criteria criteria)
    @Override public String generate()
}

public class FindByKeySql extends Sql {
    public FindByKeySql(String table, Column[] columns, String keyColumn, String keyValue)
    @Override public String generate()
}

public class PreparedInsertSql extends Sql {
    public PreparedInsertSql(String table, Column[] columns)
    @Override public String generate()
    private String placeholderList(Column[] columns)
}

public class Where {
    public Where(String criteria)
    public String generate()
}

public class ColumnList {
    public ColumnList(Column[] columns)
    public String generate()
}
```

이 구조의 장점:

| 장점 | 설명 |
|---|---|
| **극도로 단순** | 각 클래스가 순식간에 이해됨 |
| **변경 격리** | 함수 하나를 수정해도 다른 함수가 망가질 위험이 사실상 사라짐 |
| **테스트 용이** | 모든 논리를 구석구석 증명하기 쉬워짐 |
| **확장 용이** | `update` 문을 추가할 때 기존 클래스를 변경할 필요 없음 |

`update` 문을 만드는 논리는 `Sql` 클래스에서 새 클래스 `UpdateSql`을 상속받아 넣으면 그만이다. 다른 코드가 망가질 염려는 전혀 없다.

이 구조는 **SRP**뿐 아니라 **OCP(개방-폐쇄 원칙)** 도 지원한다. OCP란 클래스는 **확장에 개방적이고 수정에 폐쇄적**이어야 한다는 원칙이다. 파생 클래스를 생성하는 방식으로 새 기능에 개방적인 동시에, 다른 클래스를 닫아놓는 방식으로 수정에 폐쇄적이다.

> **핵심 통찰**: 새 기능을 수정하거나 기존 기능을 변경할 때 건드릴 코드가 최소인 시스템 구조가 바람직하다. 이상적인 시스템이라면 새 기능을 추가할 때 시스템을 확장할 뿐 기존 코드를 변경하지는 않는다.

---

## 7. 변경으로부터 격리

구체적인(concrete) 클래스는 상세한 구현(코드)을 포함하고, 추상(abstract) 클래스는 개념만 포함한다. **상세한 구현에 의존하는 클라이언트 클래스는 구현이 바뀌면 위험에 빠진다.** 그래서 인터페이스와 추상 클래스를 사용해 구현이 미치는 영향을 격리한다.

### Portfolio 예제

`Portfolio` 클래스가 외부 `TokyoStockExchange` API를 직접 사용해 포트폴리오 값을 계산한다면, 5분마다 값이 달라지는 API로 테스트 코드를 짜기란 쉽지 않다.

```java
// 좋은 예 — 인터페이스로 격리
public interface StockExchange {
    Money currentPrice(String symbol);
}

public class Portfolio {
    private StockExchange exchange;

    public Portfolio(StockExchange exchange) {
        this.exchange = exchange;
    }
    // ...
}
```

이제 테스트용 클래스를 만들 수 있다:

```java
// 테스트 코드 — 고정된 주가를 반환하는 Stub
public class PortfolioTest {
    private FixedStockExchangeStub exchange;
    private Portfolio portfolio;

    @Before
    protected void setUp() throws Exception {
        exchange = new FixedStockExchangeStub();
        exchange.fix("MSFT", 100);
        portfolio = new Portfolio(exchange);
    }

    @Test
    public void GivenFiveMSFTTotalShouldBe500() throws Exception {
        portfolio.add(5, "MSFT");
        Assert.assertEquals(500, portfolio.value());
    }
}
```

결합도가 낮으면 **유연성과 재사용성**이 높아진다. 각 시스템 요소가 다른 요소로부터 그리고 변경으로부터 잘 격리되어 있으면 각 요소를 이해하기도 더 쉬워진다.

이렇게 결합도를 최소로 줄이면 자연스럽게 **DIP(의존성 역전 원칙)** 를 따르는 클래스가 나온다. DIP는 클래스가 **상세한 구현이 아니라 추상화에 의존**해야 한다는 원칙이다.

---

## 요약

- **클래스는 작아야 한다** — 크기의 척도는 행 수가 아니라 **맡은 책임의 수**다
- **SRP(단일 책임 원칙)**: 클래스를 변경할 이유는 단 하나여야 한다 — 25단어 테스트로 확인하라
- **응집도**: 메서드가 인스턴스 변수를 많이 사용할수록 응집도가 높다 — 응집도가 낮아지면 클래스를 쪼개라
- **큰 함수를 작은 함수로 나누다 보면** 자연스럽게 **작은 클래스 여럿으로 쪼갤 기회**가 생긴다
- **변경하기 쉬운 클래스**: OCP를 따라 확장에 개방적이고 수정에 폐쇄적인 구조를 만들어라
- **변경으로부터 격리**: 인터페이스와 추상 클래스를 사용해 결합도를 낮추고 DIP를 따르라
- **작은 서랍을 많이 두는 도구 상자**가 큰 서랍 몇 개의 도구 상자보다 낫다

---

## 다른 챕터와의 관계

- **← Chapter 3 (함수)**: "함수는 작게, 매개변수 목록은 짧게"라는 전략이 클래스의 응집도 유지와 분리의 출발점이 된다
- **← Chapter 5 (형식 맞추기)**: 신문 기사처럼 읽히는 클래스 체계(상수 → 변수 → 공개 함수 → 비공개 함수)는 형식 맞추기의 연장선이다
- **→ Chapter 11 (시스템)**: 클래스 수준의 관심사 분리가 시스템 수준의 아키텍처 설계로 확장된다
- **→ Chapter 12 (창발성)**: 켄트 벡의 단순한 설계 규칙 중 "중복을 없앤다"와 "프로그래머 의도를 표현한다"가 클래스 리팩터링의 지침이 된다
- **← Chapter 1 (깨끗한 코드)**: 론 제프리스가 강조한 "단순한 코드 규칙"과 PPP에서 소개된 SRP, OCP, DIP가 이 장의 이론적 기반이다
