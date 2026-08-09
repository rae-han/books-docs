# Chapter 4: Comments (주석)

## 핵심 질문

주석은 언제 필요하고 언제 해로운가? 코드로 의도를 표현하지 못해 사용하는 주석이라는 도구를 어떻게 최소화할 수 있는가?

---

## 1. 주석은 실패를 의미한다

> *"나쁜 코드에 주석을 달지 마라. 새로 짜라."* — 브라이언 W. 커니핸, P. J. 플라우거

주석은 기껏해야 **필요악**이다. 프로그래밍 언어 자체가 표현력이 풍부하다면, 의도를 표현할 능력이 있다면, 주석은 거의 필요하지 않다. 주석은 코드로 의도를 표현하지 못해 — 실패를 만회하기 위해 — 사용하는 것이다.

주석을 무시해야 하는 이유: **거짓말을 하니까.** 항상도 아니고 고의도 아니지만 너무 자주 거짓말을 한다. 주석은 오래될수록 코드에서 멀어지고, 오래될수록 완전히 그릇될 가능성도 커진다. 프로그래머들이 주석을 유지하고 보수하기란 현실적으로 불가능하니까.

```java
MockRequest request;
private final String HTTP_DATE_REGEXP =
    "[SMTWF][a-z]{2}\\,\\s[0-9]{2}\\s[JFMASOND][a-z]{2}\\s"+
    "[0-9]{4}\\s[0-9]{2}\\:[0-9]{2}\\:[0-9]{2}\\sGMT";
private Response response;
private FitNesseContext context;
private FileResponder responder;
private Locale saveLocale;
// Example: "Tue, 02 Apr 2003 22:18:49 GMT"
```

`HTTP_DATE_REGEXP` 상수와 주석 사이에 다른 인스턴스 변수가 추가되면서, 주석이 코드에서 분리되어 부정확한 고아로 변해버렸다.

> **핵심 통찰**: 진실은 한곳에만 존재한다. 바로 코드다. 코드만이 자기가 하는 일을 진실되게 말한다. 코드만이 정확한 정보를 제공하는 유일한 출처다.

---

## 2. 주석은 나쁜 코드를 보완하지 못한다

코드에 주석을 추가하는 일반적인 이유는 코드 품질이 나쁘기 때문이다. "이런! 주석을 달아야겠다!" 아니다! **코드를 정리해야 한다!**

표현력이 풍부하고 깔끔하며 주석이 거의 없는 코드가, 복잡하고 어수선하며 주석이 많이 달린 코드보다 **훨씬** 좋다.

---

## 3. 코드로 의도를 표현하라!

많은 경우 주석으로 달려는 설명을 **함수로 만들어** 표현해도 충분하다:

```java
// 나쁜 예 — 주석이 필요한 코드
// 직원에게 복지 혜택을 받을 자격이 있는지 검사한다.
if ((employee.flags & HOURLY_FLAG) &&
    (employee.age > 65))

// 좋은 예 — 주석이 필요 없는 코드
if (employee.isEligibleForFullBenefits())
```

> **핵심 통찰**: 몇 초만 더 생각하면 코드로 대다수 의도를 표현할 수 있다.

---

## 4. 좋은 주석

어떤 주석은 필요하거나 유익하다. 하지만 명심하라 — **정말로 좋은 주석은, 주석을 달지 않을 방법을 찾아낸 주석이다!**

### 4.1 법적인 주석

회사가 정립한 구현 표준에 맞춰 법적인 이유로 특정 주석을 넣으라고 명시하는 경우다:

```java
// Copyright (C) 2003,2004,2005 by Object Mentor, Inc. All rights reserved.
// GNU General Public License 버전 2 이상을 따르는 조건으로 배포한다.
```

모든 조항과 조건을 열거하는 대신, 가능하다면 표준 라이선스나 외부 문서를 참조해도 된다.

### 4.2 정보를 제공하는 주석

기본적인 정보를 주석으로 제공하면 편리한 경우가 있다:

```java
// kk:mm:ss EEE, MMM dd, yyyy 형식이다.
Pattern timeMatcher = Pattern.compile(
    "\\d*:\\d*:\\d* \\w*, \\w* \\d*, \\d*");
```

위 주석은 정규표현식이 시각과 날짜를 뜻한다고 설명한다. 이왕이면 시각과 날짜를 변환하는 클래스를 만들어 코드를 옮겨주면 더 좋다 — 그러면 주석이 필요 없어진다.

### 4.3 의도를 설명하는 주석

때때로 주석은 구현을 이해하게 도와주는 선을 넘어 **결정에 깔린 의도**까지 설명한다:

```java
public int compareTo(Object o) {
    if (o instanceof WikiPagePath) {
        // ... 비교 로직
    }
    return 1; // 오른쪽 유형이므로 정렬 순위가 더 높다.
}
```

```java
// 스레드를 대량 생성하는 방법으로 어떻게든 경쟁 조건을 만들려 시도한다.
for (int i = 0; i < 25000; i++) {
    WidgetBuilderThread widgetBuilderThread =
        new WidgetBuilderThread(widgetBuilder, text, parent, failFlag);
    Thread thread = new Thread(widgetBuilderThread);
    thread.start();
}
```

### 4.4 의미를 명료하게 밝히는 주석

모호한 인수나 반환값이 표준 라이브러리나 변경하지 못하는 코드에 속한다면 의미를 명료하게 밝히는 주석이 유용하다:

```java
assertTrue(a.compareTo(a) == 0);    // a == a
assertTrue(a.compareTo(b) != 0);    // a != b
assertTrue(a.compareTo(b) == -1);   // a < b
assertTrue(b.compareTo(a) == 1);    // b > a
```

하지만 그릇된 주석을 달아놓을 위험이 상당히 높다. 주석이 올바른지 검증하기 쉽지 않기 때문이다. 더 나은 방법이 없는지 고민하고 정확히 달도록 각별히 주의해야 한다.

### 4.5 결과를 경고하는 주석

다른 프로그래머에게 결과를 경고할 목적으로 주석을 사용한다:

```java
public static SimpleDateFormat makeStandardHttpDateFormat() {
    // SimpleDateFormat은 스레드에 안전하지 못하다.
    // 따라서 각 인스턴스를 독립적으로 생성해야 한다.
    SimpleDateFormat df = new SimpleDateFormat("EEE, dd MMM yyyy HH:mm:ss z");
    df.setTimeZone(TimeZone.getTimeZone("GMT"));
    return df;
}
```

정적 초기화 함수를 사용하려던 열성적인 프로그래머가 주석 덕분에 실수를 면한다.

### 4.6 TODO 주석

'앞으로 할 일'을 `// TODO` 주석으로 남겨두면 편하다:

```java
// TODO-MdM 현재 필요하지 않다.
// 체크아웃 모델을 도입하면 함수가 필요 없다.
protected VersionInfo makeVersion() throws Exception {
    return null;
}
```

하지만 어떤 용도로 사용하든 시스템에 나쁜 코드를 남겨 놓는 핑계가 되어서는 안 된다. 주기적으로 TODO 주석을 점검해 없애도 괜찮은 주석은 없애라.

### 4.7 중요성을 강조하는 주석

자칫 대수롭지 않다고 여겨질 뭔가의 중요성을 강조하기 위해 사용한다:

```java
String listItemContent = match.group(3).trim();
// 여기서 trim은 정말 중요하다. trim 함수는 문자열에서 시작 공백을 제거한다.
// 문자열에 시작 공백이 있으면 다른 문자열로 인식되기 때문이다.
new ListItemWidget(this, listItemContent, this.level + 1);
```

### 4.8 공개 API에서 Javadocs

공개 API를 구현한다면 반드시 훌륭한 Javadocs를 작성한다. 하지만 여느 주석과 마찬가지로 Javadocs 역시 독자를 오도하거나, 잘못 위치하거나, 그릇된 정보를 전달할 가능성이 존재한다.

### 좋은 주석 종합

| 유형 | 용도 | 주의사항 |
|---|---|---|
| 법적인 주석 | 저작권, 라이선스 정보 | 외부 문서 참조 권장 |
| 정보 제공 주석 | 정규표현식 등 기술적 설명 | 함수 이름이나 클래스로 대체 가능하면 대체 |
| 의도 설명 주석 | 결정에 깔린 의도 | — |
| 의미 명료화 주석 | 변경 불가 코드의 반환값 설명 | 그릇된 주석 위험 높음 |
| 경고 주석 | 결과 경고 (스레드 안전성 등) | — |
| TODO 주석 | 앞으로 할 일 | 주기적 점검 필요, 핑계 금지 |
| 중요성 강조 주석 | 대수롭지 않아 보이는 것의 중요성 | — |
| 공개 API Javadocs | API 문서 | 오도 가능성 주의 |

---

## 5. 나쁜 주석

대다수 주석이 이 범주에 속한다. 일반적으로 대다수 주석은 허술한 코드를 지탱하거나, 엉성한 코드를 변명하거나, 미숙한 결정을 합리화하는 등 프로그래머가 주절거리는 독백에서 크게 벗어나지 못한다.

### 5.1 주절거리는 주석

특별한 이유 없이 의무감으로 혹은 프로세스에서 하라니까 마지못해 주석을 단다면 전적으로 시간낭비다:

```java
public void loadProperties() {
    try {
        String propertiesPath = propertiesLocation + "/" + PROPERTIES_FILE;
        FileInputStream propertiesStream = new FileInputStream(propertiesPath);
        loadedProperties.load(propertiesStream);
    }
    catch (IOException e) {
        // 속성 파일이 없다면 기본값을 모두 메모리로 읽어 들였다는 의미다.
    }
}
```

`catch` 블록의 주석은 무슨 뜻인가? 누가 기본값을 읽어 들이는가? `loadProperties.load`를 호출하기 전인가 후인가? 이해가 안 되어 다른 모듈까지 뒤져야 하는 주석은 독자와 제대로 소통하지 못하는 주석이다.

### 5.2 같은 이야기를 중복하는 주석

```java
// 나쁜 예 — 코드 내용을 그대로 중복
// this.closed가 true일 때 반환되는 유틸리티 메서드다.
// 타임아웃에 도달하면 예외를 던진다.
public synchronized void waitForClose(final long timeoutMillis)
    throws Exception {
    if (!closed) {
        wait(timeoutMillis);
        if (!closed)
            throw new Exception("MockResponseSender could not be closed");
    }
}
```

주석이 코드보다 더 많은 정보를 제공하지 못한다. 코드를 정당화하는 주석도 아니고, 의도나 근거를 설명하는 주석도 아니다. 코드보다 읽기가 쉽지도 않다.

톰캣의 `ContainerBase.java`에서 가져온 예시도 마찬가지다:

```java
/** 이 컴포넌트의 프로세서 지연값 */
protected int backgroundProcessorDelay = -1;

/** 이 컴포넌트를 지원하기 위한 생명주기 이벤트 */
protected LifecycleSupport lifecycle = new LifecycleSupport(this);

/** 컨테이너와 관련된 Logger 구현 */
protected Log logger = null;
```

코드만 지저분하고 정신없게 만들 뿐, 기록이라는 목적에 전혀 기여하지 못한다.

### 5.3 오해할 여지가 있는 주석

위 `waitForClose` 예제의 주석을 다시 보자. `this.closed`가 `true`로 변하는 순간에 메서드가 반환되지 않는다 — `this.closed`가 `true`**여야** 메서드는 반환된다. 아니면 무조건 타임아웃을 기다렸다 `this.closed`가 그래도 `true`가 아니면 예외를 던진다. '살짝 잘못된 정보' 때문에 어느 프로그래머가 경솔하게 함수를 호출할 수 있다.

### 5.4 의무적으로 다는 주석

모든 함수에 Javadocs를 달거나 모든 변수에 주석을 달아야 한다는 규칙은 어리석기 그지없다:

```java
// 나쁜 예 — 아무 가치도 없는 의무적 주석
/**
 * @param title CD 제목
 * @param author CD 저자
 * @param tracks CD 트랙 숫자
 * @param durationInMinutes CD 길이(단위: 분)
 */
public void addCD(String title, String author,
    int tracks, int durationInMinutes) {
    CD cd = new CD();
    cd.title = title;
    cd.author = author;
    cd.tracks = tracks;
    cd.duration = durationInMinutes;
    cdList.add(cd);
}
```

### 5.5 이력을 기록하는 주석

모듈 첫머리에 변경 이력을 기록하는 관례는 예전에는 바람직했다 — 소스 코드 관리 시스템이 없었으니까. 하지만 이제는 혼란만 가중할 뿐이다. 완전히 제거하는 편이 좋다.

### 5.6 있으나 마나 한 주석

너무 당연한 사실을 언급하며 새로운 정보를 제공하지 못하는 주석:

```java
/** 기본 생성자 */
protected AnnualDateRule() { }

/** 월 중 일자 */
private int dayOfMonth;

/**
 * 월 중 일자를 반환한다.
 * @return 월 중 일자
 */
public int getDayOfMonth() {
    return dayOfMonth;
}
```

이런 주석에 익숙해지면 개발자가 **주석을 무시하는 습관**에 빠진다. 결국은 코드가 바뀌면서 주석은 거짓말로 변한다.

> **핵심 통찰**: 있으나 마나 한 주석을 달려는 유혹에서 벗어나 코드를 정리하라. 더 낫고, 행복한 프로그래머가 되는 지름길이다.

### 5.7 무서운 잡음

```java
/** The name. */
private String name;

/** The version. */
private String version;

/** The licenceName. */
private String licenceName;

/** The version. */   // ← 잘라서 붙여넣기 오류!
private String info;
```

주석을 작성한 저자가 주의를 기울이지 않았다면 독자가 여기서 무슨 이익을 얻겠는가?

### 5.8 함수나 변수로 표현할 수 있다면 주석을 달지 마라

```java
// 나쁜 예 — 주석으로 설명
// 전역 목록 <smodule>에 속하는 모듈이 우리가 속한 하위 시스템에 의존하는가?
if (smodule.getDependSubsystems().contains(subSysMod.getSubSystem()))

// 좋은 예 — 코드로 표현
ArrayList moduleDependees = smodule.getDependSubsystems();
String ourSubSystem = subSysMod.getSubSystem();
if (moduleDependees.contains(ourSubSystem))
```

### 5.9 위치를 표시하는 주석

```java
// Actions ///////////////////////////
```

너무 자주 사용하지 않는다면 눈에 띄며 주의를 환기할 수 있다. 하지만 남용하면 독자가 흔한 잡음으로 여겨 무시한다. 반드시 필요할 때만, 아주 드물게 사용한다.

### 5.10 닫는 괄호에 다는 주석

```java
// 나쁜 예 — 닫는 괄호 주석
try {
    while ((line = in.readLine()) != null) {
        lineCount++;
        charCount += line.length();
        String words[] = line.split("\\W");
        wordCount += words.length;
    } //while
    System.out.println("wordCount = " + wordCount);
} //try
catch (IOException e) {
    System.err.println("Error:" + e.getMessage());
} //catch
```

닫는 괄호에 주석을 달아야겠다는 생각이 든다면 대신에 **함수를 줄이려 시도하자.**

### 5.11 공로를 돌리거나 저자를 표시하는 주석

```java
/* 릭이 추가함 */
```

소스 코드 관리 시스템이 누가 언제 무엇을 추가했는지 귀신처럼 기억한다. 저자 이름으로 코드를 오염시킬 필요가 없다.

### 5.12 주석으로 처리한 코드

```java
InputStreamResponse response = new InputStreamResponse();
response.setBody(formatter.getResultStream(), formatter.getByteCount());
// InputStream resultsStream = formatter.getResultStream();
// StreamReader reader = new StreamReader(resultsStream);
// response.setContent(reader.read(formatter.getByteCount()));
```

주석으로 처리된 코드는 다른 사람들이 지우기를 주저한다 — 이유가 있어 남겨놓았으리라고 생각하기 때문이다. 우수한 소스 코드 관리 시스템이 코드를 기억해준다. **그냥 코드를 삭제하라.** 잃어버릴 염려는 없다.

### 5.13 HTML 주석

소스 코드에서 HTML 주석은 **혐오 그 자체**다. 편집기/IDE에서조차 읽기가 어렵다. 도구로 주석을 뽑아 웹 페이지에 올릴 작정이라면 HTML 태그를 삽입해야 하는 책임은 프로그래머가 아니라 도구가 져야 한다.

### 5.14 전역 정보

주석을 달아야 한다면 **근처에 있는 코드만** 기술하라. 코드 일부에 주석을 달면서 시스템의 전반적인 정보를 기술하지 마라:

```java
/**
 * 적합성 테스트가 동작하는 포트: 기본값은 8082.
 * @param fitnessePort
 */
public void setFitnessePort(int fitnessePort) {
    this.fitnessePort = fitnessePort;
}
```

포트 기본값을 설정하는 코드가 변해도 이 주석이 변하리라는 보장은 전혀 없다.

### 5.15 너무 많은 정보

주석에다 흥미로운 역사나 관련 없는 정보를 장황하게 늘어놓지 마라.

### 5.16 모호한 관계

주석과 주석이 설명하는 코드는 둘 사이 관계가 명백해야 한다:

```java
/*
 * 모든 픽셀을 담을 만큼 충분한 배열로 시작한다(여기에 필터 바이트를 더한다).
 * 그리고 헤더 정보를 위해 200바이트를 더한다.
 */
this.pngBytes = new byte[((this.width + 1) * this.height * 3) + 200];
```

필터 바이트란 무엇일까? `+1`과 관련이 있을까? `*3`과 관련이 있을까? **주석 자체가 다시 설명을 요구하면 안 된다.**

### 5.17 함수 헤더

짧은 함수는 긴 설명이 필요 없다. 짧고 한 가지만 수행하며 이름을 잘 붙인 함수가 주석으로 헤더를 추가한 함수보다 훨씬 좋다.

### 5.18 비공개 코드에서 Javadocs

공개하지 않을 코드라면 Javadocs는 쓸모가 없다. 유용하지 않을 뿐만 아니라 형식으로 인해 코드만 보기 싫고 산만해질 뿐이다.

### 나쁜 주석 종합

| 유형 | 핵심 문제 |
|---|---|
| 주절거리는 주석 | 의무감으로 다는 주석, 뜻을 알 수 없음 |
| 같은 이야기 중복 | 코드보다 부정확해지기 쉬움 |
| 오해할 여지 있는 주석 | 살짝 잘못된 정보 → 경솔한 호출 유발 |
| 의무적 주석 | Javadocs 강제는 어리석음 |
| 이력 기록 | 소스 코드 관리 시스템이 대체 |
| 있으나 마나 한 주석 | 당연한 사실 → 주석 무시 습관 유발 |
| 무서운 잡음 | 복사-붙여넣기 오류 |
| 함수/변수로 표현 가능 | 주석 대신 코드 개선 |
| 위치 표시 주석 | 남용 시 무시됨 |
| 닫는 괄호 주석 | 함수가 길다는 증거 |
| 저자 표시 | 소스 관리 시스템이 대체 |
| 주석 처리된 코드 | 삭제해도 잃어버릴 염려 없음 |
| HTML 주석 | 편집기에서 읽기 어려움 |
| 전역 정보 | 근처 코드만 기술해야 |
| 너무 많은 정보 | 관련 없는 정보 장황하게 기술 |
| 모호한 관계 | 주석이 다시 설명을 요구 |
| 함수 헤더 | 좋은 이름 > 주석 |
| 비공개 Javadocs | 공개 API 아니면 불필요 |

---

## 6. 예제: 나쁜 주석에서 좋은 코드로

목록 4-7 `GeneratePrimes.java`는 주석이 가득하지만 엉성한 코드다:

```java
// 나쁜 예 — 주석으로 뒤덮인 코드
/**
 * 이 클래스는 사용자가 지정한 최대 값까지 소수를 생성한다.
 * 사용된 알고리즘은 에라스토테네스의 체다.
 * 에라스토테네스: 기원전 276년에 리비아 키레네에서 출생 ...
 */
public class GeneratePrimes {
    public static int[] generatePrimes(int maxValue) {
        if (maxValue >= 2) {
            // 선언
            int s = maxValue + 1; // 배열 크기
            boolean[] f = new boolean[s];
            int i;
            // 배열을 참으로 초기화
            for (i = 0; i < s; i++) f[i] = true;
            // 소수가 아닌 알려진 숫자를 제거
            f[0] = f[1] = false;
            // 체
            // ... (주석이 코드를 설명하는 대신 코드 구조가 엉망)
        }
    }
}
```

```java
// 좋은 예 — 리팩터링 후 주석이 2개로 줄어듦
/**
 * 이 클래스는 사용자가 지정한 최대 값까지 소수를 구한다.
 * 알고리즘은 에라스토테네스의 체다.
 * 2에서 시작하는 정수 배열을 대상으로 작업한다.
 * 처음으로 남아 있는 정수를 찾아 배수를 모두 제거한다.
 * 배열에 더 이상 배수가 없을 때까지 반복한다.
 */
public class PrimeGenerator {
    private static boolean[] crossedOut;
    private static int[] result;

    public static int[] generatePrimes(int maxValue) {
        if (maxValue < 2)
            return new int[0];
        else {
            uncrossIntegersUpTo(maxValue);
            crossOutMultiples();
            putUncrossedIntegersIntoResult();
            return result;
        }
    }

    private static int determineIterationLimit() {
        // 배열에 있는 모든 배수는 배열 크기의 제곱근보다 작은 소수의 인수다.
        // 따라서 이 제곱근보다 더 큰 숫자의 배수는 제거할 필요가 없다.
        double iterationLimit = Math.sqrt(crossedOut.length);
        return (int) iterationLimit;
    }
    // ... 함수 이름이 코드를 설명
}
```

리팩터링 후 전체 모듈에서 주석은 **두 개뿐**이다. 알고리즘 설명 주석과 제곱근 사용 이유 주석 — 둘 다 코드만으로는 설명하기 어려운 부분이다.

---

## 요약

- **주석은 실패를 의미한다** — 코드로 의도를 표현하지 못해 사용하는 보완 수단
- **주석은 거짓말을 한다** — 코드는 변하지만 주석은 따라가지 못한다
- **주석은 나쁜 코드를 보완하지 못한다** — 주석을 달 시간에 코드를 정리하라
- **좋은 주석의 조건**: 법적 주석, 의도 설명, 경고, TODO, 중요성 강조, 공개 API 문서
- **나쁜 주석의 조건**: 주절거림, 중복, 오해 유발, 의무적, 이력 기록, 있으나 마나, HTML, 전역 정보
- **주석 처리된 코드는 삭제하라** — 소스 코드 관리 시스템이 기억해준다
- **함수나 변수로 표현할 수 있다면 주석을 달지 마라** — 코드 개선이 먼저다
- **부정확한 주석은 아예 없는 주석보다 훨씬 더 나쁘다**

---

## 다른 챕터와의 관계

- **← Chapter 2 (의미 있는 이름)**: "함수나 변수로 표현할 수 있다면 주석을 달지 마라" — 좋은 이름은 주석의 필요성을 줄인다
- **← Chapter 3 (함수)**: 함수를 작고 명확하게 만들면 주석이 필요 없어진다. 짧은 함수는 긴 설명이 필요 없다
- **→ Chapter 5 (형식 맞추기)**: 코드 형식과 주석은 가독성이라는 같은 목표를 추구한다. 잘 정리된 코드는 주석을 대체한다
- **→ Chapter 9 (단위 테스트)**: 테스트 코드가 의도와 사용법을 설명하므로 주석의 역할을 대체한다
- **→ Chapter 17 (냄새와 휴리스틱)**: [C1]~[C5] 주석 관련 냄새가 이 장의 규칙을 코드 리뷰 체크리스트로 정리한 것이다
