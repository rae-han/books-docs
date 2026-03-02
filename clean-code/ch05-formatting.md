# Chapter 5: Formatting (형식 맞추기)

## 핵심 질문

코드 형식은 왜 중요하며, 원활한 소통을 장려하는 코드 형식 규칙은 무엇인가? 세로와 가로 형식을 어떻게 맞춰야 읽기 좋은 코드가 되는가?

---

## 1. 형식을 맞추는 목적

코드 형식은 **중요하다!** 너무 중요해서 무시하기 어렵다. 너무나도 중요하므로 융통성 없이 맹목적으로 따르면 안 된다. 코드 형식은 **의사소통의 일환**이다. 의사소통은 전문 개발자의 일차적인 의무다.

어쩌면 '돌아가는 코드'가 전문 개발자의 일차적인 의무라 여길지도 모르겠다. 하지만 오늘 구현한 기능이 다음 버전에서 바뀔 확률은 아주 높다. 그런데 오늘 구현한 코드의 **가독성**은 앞으로 바뀔 코드의 품질에 지대한 영향을 미친다.

> **핵심 통찰**: 원래 코드는 사라질지라도 개발자의 스타일과 규율은 사라지지 않는다. 오랜 시간이 지나 원래 코드의 흔적을 더 이상 찾아보기 어려울 정도로 코드가 바뀌어도 맨 처음 잡아놓은 구현 스타일과 가독성 수준은 유지보수 용이성과 확장성에 계속 영향을 미친다.

---

## 2. 적절한 행 길이를 유지하라 (세로 형식)

소스 코드는 얼마나 길어야 적당할까? 프로젝트 7개(JUnit, FitNesse, testNG, Time and Money, JDepend, Ant, Tomcat)를 조사한 결과:

| 프로젝트 | 평균 파일 크기 | 최대 파일 크기 | 특징 |
|---|---|---|---|
| JUnit | ~200줄 미만 | ~500줄 | 작은 파일 |
| FitNesse | ~65줄 | ~400줄 | 50,000줄 시스템을 작은 파일들로 구축 |
| Time and Money | ~200줄 미만 | ~500줄 | 작은 파일 |
| Tomcat | 200줄 초과 다수 | 수천 줄 | 큰 파일 |
| Ant | 200줄 초과 다수 | 수천 줄 | 큰 파일 |

> **핵심 통찰**: **500줄을 넘지 않고 대부분 200줄 정도**인 파일로도 커다란 시스템을 구축할 수 있다. 반드시 지킬 엄격한 규칙은 아니지만 바람직한 규칙으로 삼으면 좋겠다. 일반적으로 큰 파일보다 작은 파일이 이해하기 쉽다.

---

## 3. 신문 기사처럼 작성하라

좋은 신문 기사를 떠올려보라:

| 위치 | 신문 기사 | 소스 파일 |
|---|---|---|
| **최상단** | 표제 — 기사를 몇 마디로 요약 | 이름 — 간단하면서도 설명 가능 |
| **첫 문단** | 전체 내용 요약, 큰 그림 | 고차원 개념과 알고리즘 |
| **중간** | 세세한 사실이 조금씩 드러남 | 의도를 세세하게 묘사 |
| **마지막** | 날짜, 이름, 기타 세부사항 | 가장 저차원 함수와 세부 내역 |

신문이 읽을 만한 이유는 **다양한 기사로 이뤄져** 있기 때문이다. 대다수 기사가 아주 짧다. 신문이 사실, 날짜, 이름 등을 무작위로 뒤섞은 긴 기사 하나만 싣는다면 아무도 읽지 않으리라.

---

## 4. 개념은 빈 행으로 분리하라

각 행은 수식이나 절을 나타내고, 일련의 행 묶음은 완결된 생각 하나를 표현한다. 생각 사이는 빈 행을 넣어 분리해야 마땅하다.

```java
// 좋은 예 — 빈 행으로 개념 분리
package fitnesse.wikitext.widgets;

import java.util.regex.*;

public class BoldWidget extends ParentWidget {
    public static final String REGEXP = "'''.+?'''";
    private static final Pattern pattern = Pattern.compile("'''(.+?)'''",
        Pattern.MULTILINE + Pattern.DOTALL
    );

    public BoldWidget(ParentWidget parent, String text) throws Exception {
        super(parent);
        Matcher match = pattern.matcher(text);
        match.find();
        addChildWidgets(match.group(1));
    }

    public String render() throws Exception {
        StringBuffer html = new StringBuffer("<b>");
        html.append(childHtml()).append("</b>");
        return html.toString();
    }
}
```

```java
// 나쁜 예 — 빈 행이 없는 코드 (암호처럼 보인다)
package fitnesse.wikitext.widgets;
import java.util.regex.*;
public class BoldWidget extends ParentWidget {
public static final String REGEXP = "'''.+?'''";
private static final Pattern pattern = Pattern.compile("'''(.+?)'''",
Pattern.MULTILINE + Pattern.DOTALL);
public BoldWidget(ParentWidget parent, String text) throws Exception {
super(parent);
Matcher match = pattern.matcher(text);
match.find();
addChildWidgets(match.group(1));}
public String render() throws Exception {
StringBuffer html = new StringBuffer("<b>");
html.append(childHtml()).append("</b>");
return html.toString();
}
}
```

빈 행은 새로운 개념을 시작한다는 **시각적 단서**다. 단지 줄바꿈만 다를 뿐인데 가독성 차이가 극적이다.

---

## 5. 세로 밀집도

줄바꿈이 개념을 분리한다면 **세로 밀집도는 연관성**을 의미한다. 서로 밀접한 코드 행은 세로로 가까이 놓여야 한다:

```java
// 나쁜 예 — 의미 없는 주석이 관련 코드를 떨어뜨려 놓음
public class ReporterConfig {
    /**
     * 리포터 리스너의 클래스 이름
     */
    private String m_className;

    /**
     * 리포터 리스너의 속성
     */
    private List<Property> m_properties = new ArrayList<Property>();

    public void addProperty(Property property) {
        m_properties.add(property);
    }
```

```java
// 좋은 예 — 한눈에 들어옴
public class ReporterConfig {
    private String m_className;
    private List<Property> m_properties = new ArrayList<Property>();

    public void addProperty(Property property) {
        m_properties.add(property);
    }
}
```

척 보면 변수 2개에 메서드가 1개인 클래스라는 사실이 드러난다.

---

## 6. 수직 거리

서로 밀접한 개념은 세로로 가까이 둬야 한다. 타당한 근거가 없다면 서로 밀접한 개념은 한 파일에 속해야 마땅하다. 이게 바로 `protected` 변수를 피해야 하는 이유 중 하나다.

같은 파일에 속할 정도로 밀접한 두 개념은 **세로 거리**로 연관성을 표현한다. 연관성이란 한 개념을 이해하는 데 다른 개념이 중요한 정도다.

### 6.1 변수 선언

변수는 사용하는 위치에 **최대한 가까이** 선언한다. 함수가 매우 짧으므로 지역 변수는 각 함수 맨 처음에 선언한다:

```java
private static void readPreferences() {
    InputStream is = null;  // ← 사용 위치에 가까이
    try {
        is = new FileInputStream(getPreferencesFile());
        setPreferences(new Properties(getPreferences()));
        getPreferences().load(is);
    } catch (IOException e) {
        // ...
    }
}
```

루프를 제어하는 변수는 흔히 **루프 문 내부**에 선언한다:

```java
public int countTestCases() {
    int count = 0;
    for (Test each : tests)
        count += each.countTestCases();
    return count;
}
```

### 6.2 인스턴스 변수

인스턴스 변수는 **클래스 맨 처음에** 선언한다. 변수 간에 세로로 거리를 두지 않는다. 잘 설계한 클래스는 많은 클래스 메서드가 인스턴스 변수를 사용하기 때문이다.

C++에서는 클래스 마지막에 선언하는 가위 규칙(scissors rule)을 적용하고, 자바에서는 보통 클래스 맨 처음에 선언한다. 어느 쪽이든 핵심은 **잘 알려진 위치에 인스턴스 변수를 모은다**는 것이다.

```java
// 나쁜 예 — 인스턴스 변수가 클래스 중간에 숨어 있음
public class TestSuite implements Test {
    static public Test createTest(Class<? extends TestCase> theClass, String name) { ... }
    public static Constructor<? extends TestCase> getTestConstructor(...) { ... }
    public static Test warning(final String message) { ... }
    private static String exceptionToString(Throwable t) { ... }

    private String fName;                          // ← 중간에 숨김!
    private Vector<Test> fTests = new Vector<Test>(10);

    public TestSuite() { }
    // ...
}
```

### 6.3 종속 함수

한 함수가 다른 함수를 호출한다면 두 함수는 세로로 가까이 배치한다. 또한 가능하다면 **호출하는 함수를 호출되는 함수보다 먼저** 배치한다:

```java
// 좋은 예 — 호출 순서에 따라 배치
public class WikiPageResponder implements SecureResponder {
    protected WikiPage page;
    protected PageData pageData;
    protected String pageTitle;
    protected Request request;
    protected PageCrawler crawler;

    public Response makeResponse(FitNesseContext context, Request request)
        throws Exception {
        String pageName = getPageNameOrDefault(request, "FrontPage");
        loadPage(pageName, context);
        if (page == null)
            return notFoundResponse(context, request);
        else
            return makePageResponse(context);
    }

    private String getPageNameOrDefault(Request request, String defaultPageName) {
        String pageName = request.getResource();
        if (StringUtil.isBlank(pageName))
            pageName = defaultPageName;
        return pageName;
    }

    protected void loadPage(String resource, FitNesseContext context)
        throws Exception {
        WikiPagePath path = PathParser.parse(resource);
        crawler = context.root.getPageCrawler();
        crawler.setDeadEndStrategy(new VirtualEnabledPageCrawler());
        page = crawler.getPage(context.root, path);
        if (page != null)
            pageData = page.getData();
    }

    // ... 나머지 함수들도 호출 순서대로 배치
}
```

규칙을 일관적으로 적용하면 독자는 방금 호출한 함수가 **잠시 후에 정의되리라는 사실을 예측**한다.

### 6.4 개념적 유사성

비슷한 동작을 수행하는 일군의 함수는 **개념적 친화도**가 높으므로 가까이 배치한다:

```java
public class Assert {
    static public void assertTrue(String message, boolean condition) {
        if (!condition)
            fail(message);
    }

    static public void assertTrue(boolean condition) {
        assertTrue(null, condition);
    }

    static public void assertFalse(String message, boolean condition) {
        assertTrue(message, !condition);
    }

    static public void assertFalse(boolean condition) {
        assertFalse(null, condition);
    }
    // ...
}
```

명명법이 똑같고 기본 기능이 유사하고 간단하다. 서로가 서로를 호출하는 관계는 부차적인 요인이다. **종속적인 관계가 없더라도 가까이 배치할 함수들이다.**

친화도를 높이는 요인:

| 요인 | 예시 |
|---|---|
| 직접적인 종속성 | 한 함수가 다른 함수를 호출 |
| 변수 사용 관계 | 변수와 그 변수를 사용하는 함수 |
| 비슷한 동작 수행 | `assertTrue`, `assertFalse` 등 |

---

## 7. 세로 순서

함수 호출 종속성은 **아래 방향**으로 유지한다. 호출되는 함수를 호출하는 함수보다 나중에 배치한다.(*파스칼, C, C++에서는 함수를 호출하려면 먼저 정의해야 하므로 정확히 반대다.*) 소스 코드 모듈이 고차원에서 저차원으로 자연스럽게 내려간다.

신문 기사와 마찬가지로 가장 중요한 개념을 가장 먼저 표현한다. 가장 중요한 개념을 표현할 때는 세세한 사항을 최대한 배제한다. 그러면 독자가 소스 파일에서 **첫 함수 몇 개만 읽어도** 개념을 파악하기 쉬워진다.

---

## 8. 가로 형식 맞추기

한 행은 가로로 얼마나 길어야 적당할까? 프로젝트 7개를 조사한 결과, 프로그래머는 명백하게 **짧은 행을 선호**한다:

- 20자~60자 사이인 행이 총 행 수의 약 40%
- 80자 이후부터 행 수는 급격하게 감소

**100자나 120자까지는 나쁘지 않다.** 하지만 그 이상은 솔직히 주의부족이다. 개인적으로 Robert C. Martin은 **120자** 정도로 행 길이를 제한한다.

---

## 9. 가로 공백과 밀집도

가로로는 공백을 사용해 **밀접한 개념과 느슨한 개념**을 표현한다:

```java
private void measureLine(String line) {
    lineCount++;
    int lineSize = line.length();
    totalChars += lineSize;
    lineWidthHistogram.addLine(lineSize, lineCount);
    recordWidestLine(lineSize);
}
```

| 위치 | 공백 | 이유 |
|---|---|---|
| 할당 연산자 앞뒤 | **있음** | 왼쪽/오른쪽 요소가 분명히 나뉜다 |
| 함수 이름과 괄호 사이 | **없음** | 함수와 인수는 밀접하다 |
| 괄호 안 인수 쉼표 뒤 | **있음** | 인수가 별개라는 사실을 보여준다 |

### 연산자 우선순위 강조

```java
public class Quadratic {
    public static double root1(double a, double b, double c) {
        double determinant = determinant(a, b, c);
        return (-b + Math.sqrt(determinant)) / (2*a);
    }

    private static double determinant(double a, double b, double c) {
        return b*b - 4*a*c;
    }
}
```

- 승수 사이 `b*b`, `4*a*c`: 공백 없음 — 곱셈이 우선순위가 가장 높으므로
- 항 사이 `-`: 공백 있음 — 덧셈/뺄셈은 곱셈보다 우선순위가 낮으므로

> 불행히도 코드 형식을 자동으로 맞춰주는 도구는 대다수가 연산자 우선순위를 고려하지 못하므로, 위와 같이 공백을 넣어줘도 나중에 도구에서 없애는 경우가 흔하다.

---

## 10. 가로 정렬

```java
// 나쁜 예 — 가로 정렬
private   Socket          socket;
private   InputStream     input;
private   OutputStream    output;
private   Request         request;
private   Response        response;
private   FitNesseContext  context;
protected long            requestParsingTimeLimit;
```

위와 같은 정렬은 별로 유용하지 못하다. 코드가 엉뚱한 부분을 강조해 진짜 의도가 가려지기 때문이다 — 선언부를 읽다 보면 **변수 유형은 무시하고 변수 이름부터** 읽게 된다.

```java
// 좋은 예 — 정렬하지 않음
private Socket socket;
private InputStream input;
private OutputStream output;
private Request request;
private Response response;
private FitNesseContext context;
protected long requestParsingTimeLimit;
```

정렬하지 않으면 오히려 **중대한 결함을 찾기 쉽다.** 정렬이 필요할 정도로 목록이 길다면 문제는 목록 길이지 정렬 부족이 아니다. 클래스를 쪼개야 한다는 의미다.

---

## 11. 들여쓰기

소스 파일은 **윤곽도(outline)** 와 계층이 비슷하다:

| 수준 | 범위 | 들여쓰기 |
|---|---|---|
| 파일 | 파일 전체에 적용되는 정보 | 없음 |
| 클래스 | 개별 클래스에 적용되는 정보 | 1단 |
| 메서드 | 각 메서드에 적용되는 정보 | 2단 |
| 블록 | 블록 내 정보 | 3단+ |

```java
// 나쁜 예 — 들여쓰기 없음 (거의 불가해)
public class FitNesseServer implements SocketServer { private FitNesseContext
context; public FitNesseServer(FitNesseContext context) { this.context =
context; } public void serve(Socket s) { serve(s, 10000); } public void
serve(Socket s, long requestTimeout) { try { FitNesseExpediter sender = new
FitNesseExpediter(s, context);
sender.setRequestParsingTimeLimit(requestTimeout); sender.start(); }
catch(Exception e) { e.printStackTrace(); } } }
```

```java
// 좋은 예 — 들여쓰기한 코드 (구조가 한눈에 들어옴)
public class FitNesseServer implements SocketServer {
    private FitNesseContext context;

    public FitNesseServer(FitNesseContext context) {
        this.context = context;
    }

    public void serve(Socket s) {
        serve(s, 10000);
    }

    public void serve(Socket s, long requestTimeout) {
        try {
            FitNesseExpediter sender = new FitNesseExpediter(s, context);
            sender.setRequestParsingTimeLimit(requestTimeout);
            sender.start();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

들여쓰기한 파일은 구조가 한눈에 들어온다. 변수, 생성자 함수, 접근자 함수, 메서드가 금방 보인다. **들여쓰기가 없다면 인간이 코드를 읽기란 거의 불가능하리라.**

### 들여쓰기 무시하기

간단한 `if` 문, 짧은 `while` 문, 짧은 함수에서 들여쓰기 규칙을 무시하고픈 유혹이 생긴다:

```java
// 나쁜 예 — 한 행에 뭉뚱그린 코드
public CommentWidget(ParentWidget parent, String text){super(parent, text);}
public String render() throws Exception {return ""; }
```

```java
// 좋은 예 — 들여쓰기로 범위를 표현
public CommentWidget(ParentWidget parent, String text) {
    super(parent, text);
}

public String render() throws Exception {
    return "";
}
```

---

## 12. 가짜 범위

빈 `while` 문이나 `for` 문은 가능한 한 피한다. 피하지 못할 때는 빈 블록을 올바로 들여쓰고 괄호로 감싼다. 세미콜론(`;`)은 **새 행에다 제대로 들여써서** 넣어준다:

```java
while (dis.read(buf, 0, readBufferSize) != -1)
    ;
```

그렇게 하지 않으면 눈에 띄지 않는다.

---

## 13. 팀 규칙

프로그래머라면 각자 선호하는 규칙이 있다. 하지만 **팀에 속한다면** 자신이 선호해야 할 규칙은 바로 **팀 규칙**이다.

팀은 한 가지 규칙에 합의해야 한다. 모든 팀원은 그 규칙을 따라야 한다. 그래야 소프트웨어가 일관적인 스타일을 보인다.

> **Uncle Bob의 경험**: 2002년 FitNesse 프로젝트를 처음 시작했을 때 팀과 마주 앉아 구현 스타일을 논의했다. 대략 10분이 걸렸다. 어디에 괄호를 넣을지, 들여쓰기는 몇 자로 할지, 클래스와 변수와 메서드 이름은 어떻게 지을지 등을 결정했다. 그리고는 정한 규칙으로 IDE 코드 형식기를 설정한 후 지금까지 사용했다. 내가 선호하는 규칙은 아니지만 팀이 정한 규칙이었다.

좋은 소프트웨어 시스템은 읽기 쉬운 문서로 이뤄진다. 스타일은 **일관적이고 매끄러워야** 한다. 한 소스 파일에서 봤던 형식이 다른 소스 파일에도 쓰이리라는 **신뢰감**을 독자에게 줘야 한다.

---

## 세로/가로 형식 규칙 종합

| # | 규칙 | 핵심 |
|---|---|---|
| 1 | 형식은 의사소통이다 | 코드 형식은 전문 개발자의 일차적 의무 |
| 2 | 적절한 행 길이 | 대부분 200줄, 최대 500줄 |
| 3 | 신문 기사처럼 | 위→아래로 추상화 수준 하강 |
| 4 | 빈 행으로 개념 분리 | 생각 사이에 빈 행 |
| 5 | 세로 밀집도 | 연관된 코드는 세로로 가까이 |
| 6 | 수직 거리 | 변수는 사용 위치 근처, 인스턴스 변수는 맨 처음, 종속 함수는 가까이 |
| 7 | 세로 순서 | 호출하는 함수 먼저, 호출되는 함수 나중 |
| 8 | 가로 길이 | 120자 이내 권장 |
| 9 | 가로 공백 | 밀접한 개념은 붙이고, 느슨한 개념은 떼어놓기 |
| 10 | 가로 정렬 | 하지 않는 편이 좋다 — 목록이 길면 클래스를 쪼개야 |
| 11 | 들여쓰기 | 범위 계층을 시각적으로 표현, 무시하지 말 것 |
| 12 | 가짜 범위 | 빈 루프의 세미콜론은 새 행에 |
| 13 | 팀 규칙 | 개인 선호보다 팀 합의가 우선 |

---

## 요약

- **코드 형식은 의사소통이다** — 전문 개발자의 일차적인 의무이며, 원래 코드가 사라져도 스타일과 규율은 남는다
- **파일은 작게 유지하라** — 대부분 200줄, 최대 500줄이면 커다란 시스템도 구축 가능
- **신문 기사처럼 작성하라** — 위에서 아래로 추상화 수준이 내려가도록
- **빈 행으로 개념을 분리하라** — 빈 행은 새로운 개념의 시각적 단서
- **밀접한 코드는 세로로 가까이** — 변수 선언은 사용 위치 근처, 인스턴스 변수는 클래스 맨 처음
- **호출하는 함수를 먼저 배치하라** — 소스 코드가 고차원에서 저차원으로 자연스럽게 내려감
- **행 길이는 120자 이내** — 짧은 행을 선호하되 융통성 있게
- **가로 공백으로 밀접도를 표현하라** — 할당 연산자 앞뒤에 공백, 함수와 괄호 사이에 없음
- **들여쓰기를 무시하지 마라** — 짧은 함수라도 들여쓰기로 범위를 표현
- **팀 규칙이 최우선이다** — 일관적인 스타일이 소프트웨어 품질의 기반

---

## 다른 챕터와의 관계

- **← Chapter 2 (의미 있는 이름)**: 소스 파일 이름이 간단하면서도 설명 가능해야 한다는 원칙은 "신문 기사의 표제"와 같은 역할을 한다
- **← Chapter 3 (함수)**: 함수를 작게 만들면 자연스럽게 파일도 짧아지고, 내려가기 규칙이 세로 순서와 일치한다
- **← Chapter 4 (주석)**: 의미 없는 주석이 세로 밀집도를 깨뜨리고, 빈 행의 역할을 방해한다
- **→ Chapter 10 (클래스)**: 파일 크기와 클래스 크기는 밀접하며, 클래스가 작아야 파일도 작아진다
- **→ Chapter 17 (냄새와 휴리스틱)**: [F1] 지나친 인수, [G10] 수직 분리, [G11] 일관성 부족, [G30] 함수는 한 가지만 등의 냄새가 이 장의 형식 규칙과 직접 연결된다
