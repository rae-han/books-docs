# Chapter 14: Successive Refinement (점진적인 개선)

## 핵심 질문

깨끗하고 우아한 프로그램은 처음부터 한 번에 완성되는가? 아니면 지저분한 초안에서 점진적으로 개선해 나가는 것인가? 코드를 개선하면서도 시스템이 항상 동작하도록 보장하는 방법은 무엇인가?

---

## 1. 사례 연구: Args — 명령행 인수 구문분석기

이 장은 명령행 인수 구문분석기 `Args`를 점진적으로 개선하는 사례 연구다. 출발은 좋았으나 확장성이 부족했던 모듈을 소개한 뒤, 모듈을 개선하고 정리하는 과정을 단계별로 보여준다.

### Args의 사용법

`Args`는 형식 문자열(스키마)과 명령행 인수 배열을 받아 인수를 파싱하는 유틸리티다.

```java
public static void main(String[] args) {
    try {
        Args arg = new Args("l,p#,d*", args);
        boolean logging = arg.getBoolean('l');
        int port = arg.getInt('p');
        String directory = arg.getString('d');
        executeApplication(logging, port, directory);
    } catch (ArgsException e) {
        System.out.printf("Argument error: %s\n", e.errorMessage());
    }
}
```

스키마 문자열 `"l,p#,d*"`의 의미:

| 기호 | 의미 | 예시 |
|---|---|---|
| (문자만) | 부울 인수 | `l` → `-l` (true/false) |
| `#` | 정수 인수 | `p#` → `-p 8080` |
| `*` | 문자열 인수 | `d*` → `-d /home/logs` |
| `##` | 실수(double) 인수 | `x##` → `-x 42.3` |
| `[*]` | 문자열 배열 인수 | `f[*]` → `-f a -f b` |

---

## 2. 최종 버전: 깨끗한 Args 구현

최종 버전의 `Args` 클래스는 위에서 아래로 자연스럽게 읽히도록 구성되어 있다.

### Args.java (최종 버전)

```java
public class Args {
    private Map<Character, ArgumentMarshaler> marshalers;
    private Set<Character> argsFound;
    private ListIterator<String> currentArgument;

    public Args(String schema, String[] args) throws ArgsException {
        marshalers = new HashMap<Character, ArgumentMarshaler>();
        argsFound = new HashSet<Character>();
        parseSchema(schema);
        parseArgumentStrings(Arrays.asList(args));
    }

    private void parseSchema(String schema) throws ArgsException {
        for (String element : schema.split(","))
            if (element.length() > 0)
                parseSchemaElement(element.trim());
    }

    private void parseSchemaElement(String element) throws ArgsException {
        char elementId = element.charAt(0);
        String elementTail = element.substring(1);
        validateSchemaElementId(elementId);
        if (elementTail.length() == 0)
            marshalers.put(elementId, new BooleanArgumentMarshaler());
        else if (elementTail.equals("*"))
            marshalers.put(elementId, new StringArgumentMarshaler());
        else if (elementTail.equals("#"))
            marshalers.put(elementId, new IntegerArgumentMarshaler());
        else if (elementTail.equals("##"))
            marshalers.put(elementId, new DoubleArgumentMarshaler());
        else if (elementTail.equals("[*]"))
            marshalers.put(elementId, new StringArrayArgumentMarshaler());
        else
            throw new ArgsException(INVALID_ARGUMENT_FORMAT, elementId, elementTail);
    }
    // ... 이하 parseArgumentStrings, getBoolean, getString, getInt 등
}
```

### ArgumentMarshaler 인터페이스와 파생 클래스

```java
public interface ArgumentMarshaler {
    void set(Iterator<String> currentArgument) throws ArgsException;
}

public class BooleanArgumentMarshaler implements ArgumentMarshaler {
    private boolean booleanValue = false;

    public void set(Iterator<String> currentArgument) throws ArgsException {
        booleanValue = true;
    }

    public static boolean getValue(ArgumentMarshaler am) {
        if (am != null && am instanceof BooleanArgumentMarshaler)
            return ((BooleanArgumentMarshaler) am).booleanValue;
        else
            return false;
    }
}

public class StringArgumentMarshaler implements ArgumentMarshaler {
    private String stringValue = "";

    public void set(Iterator<String> currentArgument) throws ArgsException {
        try {
            stringValue = currentArgument.next();
        } catch (NoSuchElementException e) {
            throw new ArgsException(MISSING_STRING);
        }
    }
    // getValue 생략
}

public class IntegerArgumentMarshaler implements ArgumentMarshaler {
    private int intValue = 0;

    public void set(Iterator<String> currentArgument) throws ArgsException {
        String parameter = null;
        try {
            parameter = currentArgument.next();
            intValue = Integer.parseInt(parameter);
        } catch (NoSuchElementException e) {
            throw new ArgsException(MISSING_INTEGER);
        } catch (NumberFormatException e) {
            throw new ArgsException(INVALID_INTEGER, parameter);
        }
    }
    // getValue 생략
}
```

> **핵심 통찰**: 새로운 인수 유형을 추가하려면 `ArgumentMarshaler`에서 새 클래스를 파생하고, `parseSchemaElement`에 `case`를 추가하고, `getXXX` 함수를 추가하면 끝이다. 기존 코드를 건드릴 필요가 거의 없다.

---

## 3. 어떻게 짰느냐고?

저자는 위 프로그램을 **처음부터 저렇게 구현하지 않았다**고 밝힌다.

> **핵심 통찰**: 깨끗한 코드를 짜려면 먼저 지저분한 코드를 짠 뒤에 정리해야 한다. 이는 작문에서 초안을 쓰고 고쳐나가는 과정과 같다. 깔끔한 작품을 내놓으려면 단계적으로 개선해야 한다.

대다수 신참 프로그래머는 일단 프로그램이 '돌아가면' 다음 업무로 넘어간다. 경험이 풍부한 전문 프로그래머라면 이런 행동이 **전문가로서 자살 행위**라는 사실을 잘 안다.

---

## 4. Args: 1차 초안 — 코드가 망가지는 과정

### Boolean만 지원하던 초기 버전

Boolean 인수만 지원하는 최초 버전은 나름대로 깔끔했다:

```java
public class Args {
    private String schema;
    private String[] args;
    private boolean valid;
    private Set<Character> unexpectedArguments = new TreeSet<Character>();
    private Map<Character, Boolean> booleanArgs = new HashMap<Character, Boolean>();
    private int numberOfArguments = 0;

    // parseSchema, parseArguments 등 간결한 메서드들
    // ...
}
```

이 코드는 간결하고 단순하며 이해하기 쉬웠다. 하지만 나중에 엉망으로 변해갈 **씨앗**이 보인다.

### String과 Integer 추가 후 — 엉망이 된 버전

인수 유형 **두 개만 더했을 뿐**인데 코드는 엄청나게 지저분해졌다:

```java
public class Args {
    private String schema;
    private String[] args;
    private boolean valid = true;
    private Set<Character> unexpectedArguments = new TreeSet<Character>();
    private Map<Character, Boolean> booleanArgs = new HashMap<Character, Boolean>();
    private Map<Character, String> stringArgs = new HashMap<Character, String>();
    private Map<Character, Integer> intArgs = new HashMap<Character, Integer>();
    private Set<Character> argsFound = new HashSet<Character>();
    private int currentArgument;
    private char errorArgumentId = '\0';
    private String errorParameter = "TILT";
    private ErrorCode errorCode = ErrorCode.OK;
    // ... 200줄 이상의 지저분한 코드
}
```

문제점:
- 인스턴스 변수 개수가 압도적
- `"TILT"`와 같은 의미 불명확한 문자열
- `try-catch-catch` 블록의 남발
- 타입별 `HashMap`의 중복 패턴
- 오류 처리 코드가 여기저기 흩어짐

### 코드 악화의 3가지 확장 지점

새 인수 유형을 추가하려면 **세 곳**에 코드를 추가해야 했다:

| 단계 | 설명 |
|---|---|
| **1. 스키마 파싱** | 인수 유형에 해당하는 `HashMap`을 선택하기 위해 스키마 요소의 구문을 분석 |
| **2. 인수 파싱** | 명령행 인수에서 인수 유형을 분석해 진짜 유형으로 변환 |
| **3. 값 반환** | `getXXX` 메서드를 구현해 호출자에게 진짜 유형을 반환 |

인수 유형이 다양하지만 모두가 유사한 메서드를 제공하므로, **클래스 하나가 적합**하다고 판단했다. 이것이 `ArgumentMarshaler`라는 개념의 탄생이다.

---

## 5. 점진적으로 개선하다 — TDD를 활용한 리팩터링

### 원칙: 프로그램을 망치지 말 것

프로그램을 망치는 가장 좋은 방법 중 하나는 **개선이라는 이름 아래 구조를 크게 뒤집는 행위**다. 어떤 프로그램은 그저 그런 '개선'에서 결코 회복하지 못한다.

그래서 저자는 **테스트 주도 개발(TDD)** 기법을 사용했다. TDD는 언제 어느 때라도 시스템이 돌아가야 한다는 원칙을 따른다. 변경을 가한 후에도 시스템이 변경 전과 똑같이 돌아가야 한다.

### 리팩터링의 단계별 과정

리팩터링은 루빅 큐브 맞추기와 비슷하다. 큰 목표 하나를 이루기 위해 자잘한 단계를 수없이 거친다. 각 단계를 거쳐야 다음 단계가 가능하다.

#### 단계 1: ArgumentMarshaler 골격 추가

기존 코드 끝에 `ArgumentMarshaler` 클래스의 골격을 추가했다. 아무 문제도 일으키지 않는 변경이었다.

```java
private class ArgumentMarshaler {
    private boolean booleanValue = false;
    public void setBoolean(boolean value) { booleanValue = value; }
    public boolean getBoolean() { return booleanValue; }
}
private class BooleanArgumentMarshaler extends ArgumentMarshaler {}
private class StringArgumentMarshaler extends ArgumentMarshaler {}
private class IntegerArgumentMarshaler extends ArgumentMarshaler {}
```

#### 단계 2: Boolean HashMap 타입 변경

`HashMap<Character, Boolean>`을 `HashMap<Character, ArgumentMarshaler>`로 변경하고, 관련 코드를 수정했다.

```java
private Map<Character, ArgumentMarshaler> booleanArgs =
    new HashMap<Character, ArgumentMarshaler>();

private void parseBooleanSchemaElement(char elementId) {
    booleanArgs.put(elementId, new BooleanArgumentMarshaler());
}

private void setBooleanArg(char argChar, boolean value) {
    booleanArgs.get(argChar).setBoolean(value);
}
```

NullPointerException 문제가 발생하여 즉시 수정 — null 점검 위치만 바꿔주면 충분했다.

#### 단계 3: String, Integer에도 동일 적용

모든 인수 유형에 대해 같은 패턴으로 변경했다. 한 번에 하나씩 고치면서 테스트를 계속 돌렸다.

#### 단계 4: 파생 클래스로 기능 분산

모든 논리를 `ArgumentMarshaler`로 옮긴 후, 파생 클래스를 만들어 코드를 분리했다.

```java
// set 메서드를 BooleanArgumentMarshaler로 옮김
private class BooleanArgumentMarshaler extends ArgumentMarshaler {
    public void set(String s) { booleanValue = true; }
}

// get 메서드도 파생 클래스로 옮김
public Object get() { return booleanValue; }
```

#### 단계 5: 타입별 HashMap을 단일 marshalers 맵으로 통합

```java
private Map<Character, ArgumentMarshaler> marshalers =
    new HashMap<Character, ArgumentMarshaler>();
```

`isBooleanArg`, `isStringArg`, `isIntArg` 메서드를 `instanceof` 검사로 대체한 후 인라인화했다.

#### 단계 6: args 배열을 List + Iterator로 변환

set 함수를 파생 클래스로 내리기 위해, `args` 배열을 `List`로 변환한 후 `Iterator`를 `set` 함수로 전달했다. 이 변경은 10단계에 걸쳐 이뤄졌으며, 단계마다 코드는 테스트를 통과했다.

```java
private Iterator<String> currentArgument;

public void set(Iterator<String> currentArgument) throws ArgsException {
    try {
        stringValue = currentArgument.next();
    } catch (NoSuchElementException e) {
        throw new ArgsException(MISSING_STRING);
    }
}
```

#### 단계 7: if-else 연쇄 제거

마침내 유형을 일일이 확인하던 코드를 제거할 수 있게 되었다:

```java
// 이전: if-else 연쇄
if (m instanceof BooleanArgumentMarshaler)
    m.set(currentArgument);
else if (m instanceof StringArgumentMarshaler)
    m.set(currentArgument);
else if (m instanceof IntegerArgumentMarshaler)
    m.set(currentArgument);

// 이후: 다형성으로 단순화
m.set(currentArgument);
```

#### 단계 8: ArgumentMarshaler를 인터페이스로 변환

```java
private interface ArgumentMarshaler {
    void set(Iterator<String> currentArgument) throws ArgsException;
    Object get();
}
```

#### 단계 9: 새 인수 유형 추가 (double) — 확장성 검증

double 인수 유형을 추가하는 데 필요한 변경은 아주 적었다:

1. `DoubleArgumentMarshaler` 클래스 작성
2. `parseSchemaElement`에 `"##"` 감지 코드 추가
3. `getDouble` 함수 추가
4. `ErrorCode`에 `MISSING_DOUBLE`, `INVALID_DOUBLE` 추가

#### 단계 10: 오류 처리를 ArgsException으로 분리

`ArgsException`을 독자적인 모듈로 만들어 오류 코드, 오류 메시지 형식 등 잡다한 오류 지원 코드를 옮겼다. 이 작업은 대략 **30차례**로 나눠 조금씩 코드를 바꿨으며, 매 단계마다 코드는 테스트를 통과했다.

---

## 6. 변환 과정 요약

전체 리팩터링 과정을 요약하면 다음과 같다:

| 단계 | 변경 내용 | 핵심 원칙 |
|---|---|---|
| 1 | `ArgumentMarshaler` 골격 추가 | 기존 코드를 건드리지 않는 안전한 시작 |
| 2 | 타입별 HashMap을 `ArgumentMarshaler` 맵으로 변경 | 하나씩, 테스트 통과 확인하며 |
| 3 | `set`/`get` 기능을 파생 클래스로 이동 | 추상 메서드 활용 |
| 4 | 타입별 맵 세 개를 단일 `marshalers` 맵으로 통합 | `instanceof` 검사 활용 |
| 5 | `args[]` 배열을 `List` + `Iterator`로 변환 | 인수 전달 단순화 |
| 6 | `if-else` 연쇄를 다형성 호출로 대체 | OCP 실현 |
| 7 | `ArgumentMarshaler`를 인터페이스로 변환 | 추상화 완성 |
| 8 | 오류 처리를 `ArgsException`으로 분리 | SRP 적용 |

> **핵심 통찰**: 리팩터링을 하다 보면 코드를 넣었다 뺐다 하는 사례가 아주 흔하다. 단계적으로 조금씩 변경하며 매번 테스트를 돌려야 하므로 코드를 여기저기 옮길 일이 많아진다.

---

## 7. 소프트웨어 설계의 핵심 원리: 분할

소프트웨어 설계는 **분할만 잘해도 품질이 크게 높아진다**. 적절한 장소를 만들어 코드만 분리해도 설계가 좋아진다. 관심사를 분리하면 코드를 이해하고 보수하기 훨씬 더 쉬워진다.

특별히 눈여겨볼 코드는 `ArgsException`의 `errorMessage` 메서드다. 이 메서드는 원래 `Args` 클래스에 속했는데, 이는 명백히 **SRP(단일 책임 원칙)** 위반이었다:

- `Args` 클래스: 인수를 처리하는 클래스
- `ArgsException` 클래스: 오류 메시지 형식을 처리하는 클래스

두 책임을 분리함으로써 `Args` 모듈이 깨끗해졌고 차후 확장도 쉬워졌다.

---

## 8. 결론: 코드는 언제나 깨끗하게

저자가 이 장에서 전달하는 가장 중요한 교훈:

**그저 돌아가는 코드만으로는 부족하다.** 단순히 돌아가는 코드에 만족하는 프로그래머는 전문가 정신이 부족하다.

나쁜 코드의 파괴력:
- 나쁜 **일정**은 다시 짜면 된다
- 나쁜 **요구사항**은 다시 정의하면 된다
- 나쁜 **팀 역학**은 복구하면 된다
- 하지만 나쁜 **코드**는 **썩어 문드러진다** — 점점 무게가 늘어나 팀의 발목을 잡는다

코드 정리의 시간 비용:
- 오래된 의존성을 찾아내 깨려면 **상당한 시간과 인내심**이 필요하다
- 반면, 처음부터 코드를 깨끗하게 유지하기란 **상대적으로 쉽다**
- 5분 전에 엉망으로 만든 코드는 **지금 당장** 정리하기 아주 쉽다

> **핵심 통찰**: 코드는 언제나 최대한 깔끔하고 단순하게 정리하자. 절대로 썩어가게 방치하면 안 된다.

---

## 요약

- **깨끗한 코드는 한 번에 나오지 않는다** — 먼저 지저분한 초안을 짠 뒤 단계적으로 개선해야 한다
- **TDD가 점진적 개선의 핵심**이다 — 자동화된 테스트 슈트가 있어야 변경 전후에 시스템이 동일하게 동작함을 보장할 수 있다
- **한 번에 하나씩만 변경**하라 — 코드를 변경할 때마다 테스트를 돌리고, 실패하면 다음으로 넘어가기 전에 수정한다
- **구조를 크게 뒤집지 마라** — '개선'이라는 이름 아래 대규모 변경을 가하면 프로그램이 회복 불능 상태에 빠질 수 있다
- **분할이 곧 설계**다 — 적절한 장소를 만들어 코드를 분리하면 설계가 좋아진다 (SRP, OCP)
- **돌아가는 코드에 만족하지 마라** — 나쁜 코드는 썩어 문드러져 팀의 발목을 잡는다. 5분 전에 만든 나쁜 코드는 지금 당장 정리하라

---

## 다른 챕터와의 관계

- **← Chapter 1 (깨끗한 코드)**: "캠프장은 처음 왔을 때보다 더 깨끗하게 해놓고 떠나라"는 보이스카우트 규칙의 실전 적용 사례다
- **← Chapter 3 (함수)**: 함수를 작고 한 가지 일만 하도록 쪼개는 원칙이 리팩터링 과정에서 반복적으로 적용된다
- **← Chapter 9 (단위 테스트)**: TDD와 자동화된 테스트 슈트가 점진적 개선의 안전망으로 작동하는 실전 사례다
- **← Chapter 10 (클래스)**: SRP(단일 책임 원칙)를 적용해 `Args`에서 `ArgsException`으로 오류 처리를 분리하는 과정이 핵심이다
- **→ Chapter 15 (JUnit 들여다보기)**: 15장에서도 동일한 "보이스카우트 규칙"과 점진적 개선 방식으로 JUnit 코드를 리팩터링한다
- **→ Chapter 17 (냄새와 휴리스틱)**: 리팩터링 과정에서 참조하는 코드 냄새 번호([G23], [N5], [F1] 등)가 17장의 체계적인 목록으로 정리되어 있다
