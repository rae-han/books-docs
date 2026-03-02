# Chapter 15: JUnit Internals (JUnit 들여다보기)

## 핵심 질문

이미 잘 짜인 코드라도 개선의 여지가 있는가? 우수한 모듈을 더 깨끗하게 만드는 구체적인 리팩터링 기법은 무엇인가?

---

## 1. JUnit 프레임워크

JUnit은 자바 프레임워크 중에서 가장 유명하다. 일반적인 프레임워크가 그렇듯 개념은 단순하며 정의는 정밀하고 구현은 우아하다. JUnit은 켄트 벡(Kent Beck)과 에릭 감마(Erich Gamma) 두 사람이 아틀란타 행 비행기 안에서 세 시간 동안 만든 프레임워크다.

이 장에서 살펴볼 모듈은 문자열 비교 오류를 파악할 때 유용한 `ComparisonCompactor`라는 클래스다. 이 클래스는 두 문자열을 받아 차이를 반환한다.

예를 들어:
- 입력: `"ABCDE"` vs `"ABXDE"`
- 출력: `<...B[X]D...>`

---

## 2. 테스트 코드: ComparisonCompactorTest

리팩터링에 앞서 테스트 코드부터 살펴본다. 테스트 케이스를 읽으면 모듈에 필요한 기능이 상세히 드러난다.

```java
public class ComparisonCompactorTest extends TestCase {
    public void testMessage() {
        String failure = new ComparisonCompactor(0, "b", "c").compact("a");
        assertTrue("a expected:<[b]> but was:<[c]>".equals(failure));
    }

    public void testStartSame() {
        String failure = new ComparisonCompactor(1, "ba", "bc").compact(null);
        assertEquals("expected:<b[a]> but was:<b[c]>", failure);
    }

    public void testEndSame() {
        String failure = new ComparisonCompactor(1, "ab", "cb").compact(null);
        assertEquals("expected:<[a]b> but was:<[c]b>", failure);
    }

    public void testSame() {
        String failure = new ComparisonCompactor(1, "ab", "ab").compact(null);
        assertEquals("expected:<ab> but was:<ab>", failure);
    }

    public void testNoContextStartAndEndSame() {
        String failure = new ComparisonCompactor(0, "abc", "adc").compact(null);
        assertEquals("expected:<...[b]...> but was:<...[d]...>", failure);
    }

    public void testStartAndEndContext() {
        String failure = new ComparisonCompactor(1, "abc", "adc").compact(null);
        assertEquals("expected:<a[b]c> but was:<a[d]c>", failure);
    }

    public void testStartAndEndContextWithEllipses() {
        String failure = new ComparisonCompactor(1, "abcde", "abfde").compact(null);
        assertEquals("expected:<...b[c]d...> but was:<...b[f]d...>", failure);
    }

    public void testComparisonErrorWithActualNull() {
        String failure = new ComparisonCompactor(0, "a", null).compact(null);
        assertEquals("expected:<a> but was:<null>", failure);
    }

    public void testComparisonErrorWithExpectedNull() {
        String failure = new ComparisonCompactor(0, null, "a").compact(null);
        assertEquals("expected:<null> but was:<a>", failure);
    }

    // ... 더 많은 테스트 케이스 (총 100% 코드 커버리지)
}
```

코드 커버리지 분석 결과 **100%**가 나왔다. 테스트 케이스가 모든 행, 모든 `if` 문, 모든 `for` 문을 실행한다.

---

## 3. 원본 코드: ComparisonCompactor.java

```java
package junit.framework;

public class ComparisonCompactor {
    private static final String ELLIPSIS = "...";
    private static final String DELTA_END = "]";
    private static final String DELTA_START = "[";

    private int fContextLength;
    private String fExpected;
    private String fActual;
    private int fPrefix;
    private int fSuffix;

    public ComparisonCompactor(int contextLength, String expected, String actual) {
        fContextLength = contextLength;
        fExpected = expected;
        fActual = actual;
    }

    public String compact(String message) {
        if (fExpected == null || fActual == null || areStringsEqual())
            return Assert.format(message, fExpected, fActual);
        findCommonPrefix();
        findCommonSuffix();
        String expected = compactString(fExpected);
        String actual = compactString(fActual);
        return Assert.format(message, expected, actual);
    }

    private String compactString(String source) {
        String result = DELTA_START +
            source.substring(fPrefix, source.length() - fSuffix + 1) +
            DELTA_END;
        if (fPrefix > 0)
            result = computeCommonPrefix() + result;
        if (fSuffix > 0)
            result = result + computeCommonSuffix();
        return result;
    }

    // findCommonPrefix, findCommonSuffix, computeCommonPrefix,
    // computeCommonSuffix, areStringsEqual 메서드들...
}
```

전반적으로 상당히 훌륭한 모듈이다. 코드는 잘 분리되었고, 표현력이 적절하며, 구조가 단순하다. 하지만 보이스카우트 규칙에 따르면 우리는 처음 왔을 때보다 **더 깨끗하게 해놓고 떠나야** 한다.

### 디팩터링(*defactoring — 리팩터링의 반대 과정. 구조를 의도적으로 어지럽히는 것.*) 버전과의 비교

원본이 얼마나 잘 짜인 코드인지는 **디팩터링**(리팩터링의 반대) 결과를 보면 명확해진다:

```java
// 디팩터링 결과 — 끔찍한 코드
public class ComparisonCompactor {
    private int ctxt;
    private String s1;
    private String s2;
    private int pfx;
    private int sfx;
    // ... 모든 변수명이 축약, 메서드가 하나로 뭉침
}
```

---

## 4. 리팩터링 과정: 단계별 개선

### 4.1 멤버 변수 접두어 제거 [N6]

오늘날 개발 환경에서는 변수 이름에 범위를 명시하는 `f` 접두어가 불필요하다. 중복되는 정보이므로 제거한다.

```java
// 이전
private int fContextLength;
private String fExpected;
private String fActual;
private int fPrefix;
private int fSuffix;

// 이후
private int contextLength;
private String expected;
private String actual;
private int prefix;
private int suffix;
```

### 4.2 조건문 캡슐화 [G28]

`compact` 함수 시작부의 캡슐화되지 않은 조건문을 메서드로 추출해 의도를 명확히 표현한다.

```java
// 이전
if (expected == null || actual == null || areStringsEqual())
    return Assert.format(message, expected, actual);

// 이후
if (shouldNotCompact())
    return Assert.format(message, expected, actual);

private boolean shouldNotCompact() {
    return expected == null || actual == null || areStringsEqual();
}
```

### 4.3 지역 변수 이름 충돌 해소 [N4]

`fExpected`에서 `f`를 빼면 멤버 변수와 지역 변수의 이름이 충돌한다. 서로 다른 의미이므로 명확하게 구분한다.

```java
// 이전: this.expected와 expected 지역변수가 충돌
String expected = compactString(this.expected);
String actual = compactString(this.actual);

// 이후: 명확한 이름
String compactExpected = compactString(expected);
String compactActual = compactString(actual);
```

### 4.4 부정문을 긍정문으로 변환 [G29]

부정문은 긍정문보다 이해하기 약간 더 어렵다. 조건문을 반전시킨다.

```java
// 이전
if (shouldNotCompact())
    return Assert.format(message, expected, actual);

// 이후
public String formatCompactedComparison(String message) {
    if (canBeCompacted()) {
        findCommonPrefix();
        findCommonSuffix();
        String compactExpected = compactString(expected);
        String compactActual = compactString(actual);
        return Assert.format(message, compactExpected, compactActual);
    } else {
        return Assert.format(message, expected, actual);
    }
}
```

### 4.5 함수 이름 개선 [N7]

`compact`라는 이름은 실제 동작을 정확히 표현하지 못한다. `canBeCompacted`가 false이면 압축하지 않고, 반환하는 것은 '형식이 갖춰진 문자열'이다.

```java
// 이전
public String compact(String message)

// 이후: 실제 동작을 서술적으로 표현
public String formatCompactedComparison(String message)
```

### 4.6 함수 분리: 압축과 형식 맞추기 [G30]

압축 기능과 형식 맞추기 기능을 분리한다.

```java
private String compactExpected;
private String compactActual;

public String formatCompactedComparison(String message) {
    if (canBeCompacted()) {
        compactExpectedAndActual();
        return Assert.format(message, compactExpected, compactActual);
    } else {
        return Assert.format(message, expected, actual);
    }
}

private void compactExpectedAndActual() {
    findCommonPrefix();
    findCommonSuffix();
    compactExpected = compactString(expected);
    compactActual = compactString(actual);
}
```

### 4.7 함수 사용 방식의 일관성 확보 [G11]

`compactExpectedAndActual`에서 처음 두 줄은 반환값이 없고, 마지막 두 줄은 변수를 반환한다. 일관성을 위해 `findCommonPrefix`와 `findCommonSuffix`도 값을 반환하도록 변경한다.

```java
private void compactExpectedAndActual() {
    prefixIndex = findCommonPrefix();
    suffixIndex = findCommonSuffix();
    compactExpected = compactString(expected);
    compactActual = compactString(actual);
}
```

### 4.8 숨겨진 시간적 결합 노출 [G31]

`findCommonSuffix`는 `findCommonPrefix`가 `prefixIndex`를 먼저 계산해야 한다는 **숨겨진 시간적 결합(hidden temporal coupling)** 이 존재한다. 잘못된 순서로 호출하면 밤샘 디버깅이 필요해진다.

시간 결합을 노출하기 위해 `findCommonPrefixAndSuffix`라는 함수를 만들었다:

```java
private void findCommonPrefixAndSuffix() {
    findCommonPrefix();
    int suffixLength = 1;
    for (; !suffixOverlapsPrefix(suffixLength); suffixLength++) {
        if (charFromEnd(expected, suffixLength) !=
            charFromEnd(actual, suffixLength))
            break;
    }
    suffixIndex = suffixLength;
}

private char charFromEnd(String s, int i) {
    return s.charAt(s.length() - i);
}

private boolean suffixOverlapsPrefix(int suffixLength) {
    return actual.length() - suffixLength < prefixLength ||
           expected.length() - suffixLength < prefixLength;
}
```

### 4.9 변수 이름 개선: index vs length [N1] [G33]

`suffixIndex`가 실제로는 **접미어 길이**라는 사실이 드러났다. 하지만 0이 아니라 1에서 시작하므로 진정한 길이가 아니었다. 이것이 `computeCommonSuffix`에 `+1`이 곳곳에 등장하는 이유였다.

`suffixIndex`를 `suffixLength`로 변경하고, 0에서 시작하도록 고쳐 `+1`을 모두 제거했다:

```java
private int suffixLength;

private void findCommonPrefixAndSuffix() {
    findCommonPrefix();
    suffixLength = 0;
    for (; !suffixOverlapsPrefix(suffixLength); suffixLength++) {
        if (charFromEnd(expected, suffixLength) !=
            charFromEnd(actual, suffixLength))
            break;
    }
}

private char charFromEnd(String s, int i) {
    return s.charAt(s.length() - i - 1);  // -1 추가
}
```

### 4.10 숨겨진 버그 발견

`+1`을 제거하는 과정에서 `compactString`의 다음 코드를 발견했다:

```java
if (suffixLength > 0)
```

원래 `suffixIndex`가 1 이상이었으므로 이 `if` 문은 **사실상 항상 참**이었다. 즉, `if` 문 자체가 있으나마나였다. 테스트를 돌려보니 `if` 문 두 개를 모두 주석 처리해도 **테스트를 통과**했다. 불필요한 `if` 문을 제거하고 `compactString`을 단순화했다:

```java
// 이전: 불필요한 if 문 포함
private String compactString(String source) {
    String result = DELTA_START +
        source.substring(prefixLength, source.length() - suffixLength) +
        DELTA_END;
    if (prefixLength > 0)
        result = computeCommonPrefix() + result;
    if (suffixLength > 0)
        result = result + computeCommonSuffix();
    return result;
}

// 이후: 단순한 문자열 조합
private String compactString(String source) {
    return computeCommonPrefix() +
        DELTA_START +
        source.substring(prefixLength, source.length() - suffixLength) +
        DELTA_END +
        computeCommonSuffix();
}
```

> **핵심 통찰**: 이름을 바로잡는 과정에서 기존 코드에 숨어 있던 구조적 문제(불필요한 if 문, 경계 조건 오류)가 드러났다. 좋은 이름은 단순히 가독성을 높이는 것이 아니라 **버그를 발견하는 도구**이기도 하다.

---

## 5. 최종 버전: ComparisonCompactor.java

```java
package junit.framework;

public class ComparisonCompactor {
    private static final String ELLIPSIS = "...";
    private static final String DELTA_END = "]";
    private static final String DELTA_START = "[";

    private int contextLength;
    private String expected;
    private String actual;
    private int prefixLength;
    private int suffixLength;

    public ComparisonCompactor(
        int contextLength, String expected, String actual
    ) {
        this.contextLength = contextLength;
        this.expected = expected;
        this.actual = actual;
    }

    public String formatCompactedComparison(String message) {
        String compactExpected = expected;
        String compactActual = actual;
        if (shouldBeCompacted()) {
            findCommonPrefixAndSuffix();
            compactExpected = compact(expected);
            compactActual = compact(actual);
        }
        return Assert.format(message, compactExpected, compactActual);
    }

    private boolean shouldBeCompacted() {
        return !shouldNotBeCompacted();
    }

    private boolean shouldNotBeCompacted() {
        return expected == null || actual == null || expected.equals(actual);
    }

    private void findCommonPrefixAndSuffix() {
        findCommonPrefix();
        suffixLength = 0;
        for (; !suffixOverlapsPrefix(); suffixLength++) {
            if (charFromEnd(expected, suffixLength) !=
                charFromEnd(actual, suffixLength))
                break;
        }
    }

    private char charFromEnd(String s, int i) {
        return s.charAt(s.length() - i - 1);
    }

    private boolean suffixOverlapsPrefix() {
        return actual.length() - suffixLength <= prefixLength ||
               expected.length() - suffixLength <= prefixLength;
    }

    private void findCommonPrefix() {
        prefixLength = 0;
        int end = Math.min(expected.length(), actual.length());
        for (; prefixLength < end; prefixLength++)
            if (expected.charAt(prefixLength) != actual.charAt(prefixLength))
                break;
    }

    private String compact(String s) {
        return new StringBuilder()
            .append(startingEllipsis())
            .append(startingContext())
            .append(DELTA_START)
            .append(delta(s))
            .append(DELTA_END)
            .append(endingContext())
            .append(endingEllipsis())
            .toString();
    }

    private String startingEllipsis() {
        return prefixLength > contextLength ? ELLIPSIS : "";
    }

    private String startingContext() {
        int contextStart = Math.max(0, prefixLength - contextLength);
        int contextEnd = prefixLength;
        return expected.substring(contextStart, contextEnd);
    }

    private String delta(String s) {
        int deltaStart = prefixLength;
        int deltaEnd = s.length() - suffixLength;
        return s.substring(deltaStart, deltaEnd);
    }

    private String endingContext() {
        int contextStart = expected.length() - suffixLength;
        int contextEnd = Math.min(contextStart + contextLength, expected.length());
        return expected.substring(contextStart, contextEnd);
    }

    private String endingEllipsis() {
        return suffixLength > contextLength ? ELLIPSIS : "";
    }
}
```

최종 코드의 구조적 특징:
- 모듈은 **일련의 분석 함수**와 **일련의 조합 함수**로 나뉜다
- 전체 함수는 **위상적으로 정렬**되어 각 함수가 사용된 직후에 정의된다
- `compact` 메서드는 `StringBuilder`를 사용해 **문자열 조합 순서를 명확히** 보여준다

---

## 6. 리팩터링 과정에서 적용된 원칙 요약

| 단계 | 변경 내용 | 적용 원칙 | 참조 |
|---|---|---|---|
| 접두어 제거 | `f` 접두어 삭제 | 인코딩을 피하라 | [N6] |
| 조건문 캡슐화 | `shouldNotCompact()` 추출 | 조건을 캡슐화하라 | [G28] |
| 이름 충돌 해소 | `compactExpected/compactActual` | 명확한 이름 | [N4] |
| 부정→긍정 | `canBeCompacted()` | 긍정 표현이 읽기 쉽다 | [G29] |
| 함수명 개선 | `formatCompactedComparison` | 서술적 이름 | [N7] |
| 함수 분리 | 압축과 형식 맞추기 | 함수는 한 가지만 | [G30] |
| 일관성 확보 | `find` 함수들의 반환 패턴 통일 | 일관성을 유지하라 | [G11] |
| 시간 결합 노출 | `findCommonPrefixAndSuffix` | 시간적 결합을 명시하라 | [G31] |
| 변수명 개선 | `suffixIndex` → `suffixLength` | 서술적 이름 | [N1] |
| 경계 조건 | `+1` 제거, 0-based 인덱스 | 경계 조건을 캡슐화하라 | [G33] |
| 불필요한 if 제거 | `compactString` 단순화 | 죽은 코드를 제거하라 | [G9] |

---

## 7. 리팩터링에서 되돌림은 흔한 일

코드를 주의 깊게 살피면 저자가 이 장 초반에서 내렸던 결정 일부를 번복했다는 사실을 눈치챌 수 있다:

- 처음에 추출했던 메서드 몇 개를 `formatCompactedComparison`에 도로 집어넣었다
- `shouldNotBeCompacted` 조건도 원래대로 되돌렸다

> **핵심 통찰**: 리팩터링은 코드가 어느 수준에 이를 때까지 수많은 시행착오를 반복하는 작업이다. 이전에 했던 변경을 되돌리는 것은 흔한 일이며, 이를 두려워할 필요가 없다.

---

## 요약

- **세상에 개선이 불필요한 모듈은 없다** — 원래 깨끗한 코드라도 더 깨끗하게 만들 여지가 있다
- **보이스카우트 규칙**을 따르라 — 코드를 처음보다 조금 더 깨끗하게 만드는 책임은 우리 모두에게 있다
- **접두어 `f`는 불필요**하다 — 현대 IDE에서 변수 범위를 이름에 인코딩할 필요 없다
- **조건문을 캡슐화**하라 — 의도를 명확히 표현하는 이름의 메서드로 추출한다
- **부정문보다 긍정문**이 읽기 쉽다 — `shouldNotCompact()`보다 `canBeCompacted()`가 낫다
- **숨겨진 시간적 결합을 노출**하라 — 함수 호출 순서에 의존하는 코드는 그 의존성을 명시해야 한다
- **이름을 바로잡으면 버그가 보인다** — `suffixIndex`를 `suffixLength`로 변경하는 과정에서 숨겨진 `+1` 오류가 드러났다
- **리팩터링 과정의 되돌림은 자연스러운 일**이다 — 시행착오를 거쳐 최적의 구조에 도달한다

---

## 다른 챕터와의 관계

- **← Chapter 1 (깨끗한 코드)**: 보이스카우트 규칙 — "처음 왔을 때보다 더 깨끗하게 해놓고 떠나라"의 실전 적용
- **← Chapter 2 (의미 있는 이름)**: 멤버 변수 접두어 제거[N6], 서술적 이름 선택[N1], 변수 이름 충돌 해소[N4] 등 이름 규칙의 실전 적용
- **← Chapter 3 (함수)**: 함수를 작게, 한 가지 일만 하도록 분리하는 원칙이 `compactExpectedAndActual`, `findCommonPrefixAndSuffix` 등의 추출로 적용됨
- **← Chapter 14 (점진적인 개선)**: 14장의 Args 사례와 동일한 "점진적 개선" 방법론을 JUnit 코드에 적용한 사례
- **→ Chapter 16 (SerialDate 리팩터링)**: 15장보다 더 큰 규모의 리팩터링을 다루며, 추상 클래스 설계와 팩토리 패턴 적용까지 확장한다
- **→ Chapter 17 (냄새와 휴리스틱)**: 리팩터링 중 참조한 코드 냄새([N6], [G28], [G29], [G31], [G33] 등)가 체계적으로 정리되어 있다
