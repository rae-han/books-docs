# Chapter 2: Meaningful Names (의미 있는 이름)

## 핵심 질문

변수, 함수, 클래스의 이름만으로 코드의 의도를 명확히 전달할 수 있는가? 좋은 이름을 짓기 위한 실용적인 규칙은 무엇인가?

---

## 1. 의도를 분명히 밝혀라

좋은 이름을 지으려면 시간이 걸리지만, 좋은 이름으로 절약하는 시간이 훨씬 더 많다. 변수(혹은 함수나 클래스)의 이름은 다음 질문에 모두 답해야 한다:

- 존재 이유는?
- 수행 기능은?
- 사용 방법은?

**따로 주석이 필요하다면 의도를 분명히 드러내지 못했다는 뜻이다.**

```java
// 나쁜 예
int d; // 경과 시간(단위: 날짜)

// 좋은 예
int elapsedTimeInDays;
int daysSinceCreation;
int daysSinceModification;
int fileAgeInDays;
```

### 지뢰찾기 예제

의도가 드러나는 이름의 위력을 보여주는 예제다. 다음 코드가 무엇을 하는지 짐작할 수 있는가?

```java
// 나쁜 예 — 코드의 함축성이 문제
public List<int[]> getThem() {
    List<int[]> list1 = new ArrayList<int[]>();
    for (int[] x : theList)
        if (x[0] == 4)
            list1.add(x);
    return list1;
}
```

복잡한 문장은 없다. 변수는 세 개, 상수는 두 개뿐이다. 그런데도 코드가 하는 일을 짐작하기 어렵다. 문제는 코드의 단순성이 아니라 **함축성**이다. 독자가 다음 정보를 이미 알고 있다고 가정하기 때문이다:

1. `theList`에 무엇이 들었는가?
2. `theList`에서 0번째 값이 어째서 중요한가?
3. 값 `4`는 무슨 의미인가?
4. 함수가 반환하는 리스트를 어떻게 사용하는가?

지뢰찾기 게임이라면 `theList`는 게임판이다. 각 칸은 배열이고, 0번째 값은 칸 상태, 값 4는 깃발이 꽂힌 상태를 가리킨다:

```java
// 좋은 예 — 이름만 바꿨을 뿐인데 명확해짐
public List<int[]> getFlaggedCells() {
    List<int[]> flaggedCells = new ArrayList<int[]>();
    for (int[] cell : gameBoard)
        if (cell[STATUS_VALUE] == FLAGGED)
            flaggedCells.add(cell);
    return flaggedCells;
}
```

한 걸음 더 나아가, `int` 배열 대신 `Cell` 클래스를 만들면:

```java
// 더 좋은 예 — 클래스로 의미를 캡슐화
public List<Cell> getFlaggedCells() {
    List<Cell> flaggedCells = new ArrayList<Cell>();
    for (Cell cell : gameBoard)
        if (cell.isFlagged())
            flaggedCells.add(cell);
    return flaggedCells;
}
```

> **핵심 통찰**: 단순히 이름만 고쳤는데도 함수가 하는 일을 이해하기 쉬워졌다. 바로 이것이 좋은 이름이 주는 위력이다.

---

## 2. 그릇된 정보를 피하라

프로그래머는 코드에 **그릇된 단서**를 남겨서는 안 된다:

| 나쁜 예 | 이유 | 대안 |
|---|---|---|
| `hp` | 유닉스 플랫폼 이름으로 이미 사용됨 | `hypotenuse` |
| `accountList` | 실제 `List`가 아닌데 List라는 단어 사용 | `accountGroup`, `accounts` |
| `XYZControllerForEfficientHandlingOfStrings` vs `XYZControllerForEfficientStorageOfStrings` | 지나치게 흡사한 이름 | 명확히 구분되는 이름 사용 |
| `int a = l;` / `if (O == l)` | 소문자 `l`은 숫자 `1`, 대문자 `O`는 숫자 `0`과 혼동 | 의미 있는 이름으로 변경 |

유사한 개념은 **유사한 표기법**을 사용한다. 일관성이 떨어지는 표기법은 그 자체가 그릇된 정보다.

---

## 3. 의미 있게 구분하라

컴파일러나 인터프리터만 통과하려는 생각으로 코드를 구현하면 스스로 문제를 일으킨다.

### 연속적 숫자 덧붙이기 — 의도가 전혀 드러나지 않는다

```java
// 나쁜 예
public static void copyChars(char a1[], char a2[]) {
    for (int i = 0; i < a1.length; i++) {
        a2[i] = a1[i];
    }
}

// 좋은 예
public static void copyChars(char source[], char destination[]) {
    for (int i = 0; i < source.length; i++) {
        destination[i] = source[i];
    }
}
```

### 불용어(noise word) 추가 — 아무런 정보도 제공하지 못한다

| 의미 없는 구분 | 문제 |
|---|---|
| `Product` vs `ProductInfo` vs `ProductData` | `Info`, `Data`는 의미가 불분명한 불용어 |
| `NameString` vs `Name` | `Name`이 부동소수가 될 가능성이 있는가? |
| `Customer` vs `CustomerObject` | 차이를 알 수 있는가? |
| `getActiveAccount()` vs `getActiveAccounts()` vs `getActiveAccountInfo()` | 어느 함수를 호출해야 하는가? |
| `moneyAmount` vs `money` | `variable`이라는 단어를 변수 이름에 쓰는 것과 같다 |

> **핵심 통찰**: 읽는 사람이 차이를 알도록 이름을 지어라. 이름이 달라야 한다면 의미도 달라져야 한다.

---

## 4. 발음하기 쉬운 이름을 사용하라

프로그래밍은 **사회 활동**이다. 발음하기 어려운 이름은 토론하기도 어렵다.

```java
// 나쁜 예 — "젠 야 무다 힘즈"?
class DtaRcrd102 {
    private Date genymdhms;
    private Date modymdhms;
    private final String pszqint = "102";
    /* ... */
}

// 좋은 예 — "Generation Timestamp 값이 내일 날짜입니다!"
class Customer {
    private Date generationTimestamp;
    private Date modificationTimestamp;
    private final String recordId = "102";
    /* ... */
}
```

둘째 코드는 지적인 대화가 가능해진다: *"마이키, 이 레코드 좀 보세요. Generation Timestamp 값이 내일 날짜입니다! 어떻게 이렇죠?"*

---

## 5. 검색하기 쉬운 이름을 사용하라

문자 하나를 사용하는 이름과 상수는 텍스트 코드에서 쉽게 눈에 띄지 않는다. `WORK_DAYS_PER_WEEK`는 `grep`으로 쉽게 찾지만, 숫자 `5`는 5가 들어가는 모든 파일과 수식이 검색된다.

```java
// 나쁜 예 — 검색 불가
for (int j = 0; j < 34; j++) {
    s += (t[j] * 4) / 5;
}

// 좋은 예 — 검색 가능, 의미 명확
int realDaysPerIdealDay = 4;
const int WORK_DAYS_PER_WEEK = 5;
int sum = 0;
for (int j = 0; j < NUMBER_OF_TASKS; j++) {
    int realTaskDays = taskEstimate[j] * realDaysPerIdealDay;
    int realTaskWeeks = (realTaskDays / WORK_DAYS_PER_WEEK);
    sum += realTaskWeeks;
}
```

**이름 길이는 범위 크기에 비례해야 한다.** 간단한 메서드에서 로컬 변수만 한 문자를 사용하고, 여러 곳에서 사용하는 변수나 상수는 검색하기 쉬운 이름이 바람직하다.

---

## 6. 인코딩을 피하라

유형이나 범위 정보까지 이름에 인코딩하면 해독하기 어려워진다. 문제 해결에 집중하는 개발자에게 인코딩은 **불필요한 정신적 부담**이다.

### 6.1 헝가리식 표기법

과거 윈도 C API에서는 컴파일러가 타입을 점검하지 않아 프로그래머에게 타입 기억 단서가 필요했다. 하지만 요즘은:
- 프로그래밍 언어가 훨씬 많은 타입을 지원
- 컴파일러가 타입을 기억하고 강제
- 클래스와 함수는 점차 작아지는 추세
- IDE가 코드를 컴파일하지 않고도 타입 오류를 감지

```java
// 헝가리식 표기법의 문제
PhoneNumber phoneString;  // 타입이 바뀌어도 이름은 바뀌지 않는다!
```

### 6.2 멤버 변수 접두어

`m_` 접두어는 더 이상 필요 없다. 클래스와 함수는 접두어가 필요 없을 정도로 작아야 한다.

```java
// 나쁜 예
public class Part {
    private String m_dsc;  // 설명 문자열
    void setName(String name) {
        m_dsc = name;
    }
}

// 좋은 예
public class Part {
    String description;
    void setDescription(String description) {
        this.description = description;
    }
}
```

### 6.3 인터페이스 클래스와 구현 클래스

인터페이스 이름에 `I` 접두어를 붙이지 않는 편이 좋다. `I`는 주의를 흐트리고 과도한 정보를 제공한다. 인코딩이 필요하다면 **구현 클래스 이름**을 택한다.

| 나쁜 예 | 좋은 예 |
|---|---|
| `IShapeFactory` + `ShapeFactory` | `ShapeFactory` + `ShapeFactoryImp` |

---

## 7. 자신의 기억력을 자랑하지 마라

독자가 코드를 읽으면서 변수 이름을 자신이 아는 이름으로 변환해야 한다면, 그 변수 이름은 바람직하지 못하다.

- 루프 변수 `i`, `j`, `k`는 전통적으로 괜찮다 (단, `l`은 절대 안 된다!)
- 그 외에는 대부분 적절하지 못하다
- `r`이라는 변수가 호스트와 프로토콜을 제외한 소문자 URL이라는 사실을 항상 기억한다면 확실히 똑똑한 사람이다

> **핵심 통찰**: 똑똑한 프로그래머와 전문가 프로그래머의 차이 — 전문가 프로그래머는 **명료함이 최고**라는 사실을 이해한다. 자신의 능력을 좋은 방향으로 사용해 남들이 이해하는 코드를 내놓는다.

---

## 8. 클래스 이름과 메서드 이름

### 클래스 이름

**명사나 명사구**가 적합하다:

| 좋은 예 | 나쁜 예 |
|---|---|
| `Customer`, `WikiPage`, `Account`, `AddressParser` | `Manager`, `Processor`, `Data`, `Info` |

동사는 사용하지 않는다.

### 메서드 이름

**동사나 동사구**가 적합하다: `postPayment`, `deletePage`, `save`

접근자, 변경자, 조건자는 JavaBean 표준에 따라 `get`, `set`, `is`를 붙인다:

```java
string name = employee.getName();
customer.setName("mike");
if (paycheck.isPosted()) ...
```

생성자를 중복정의(overload)할 때는 **정적 팩토리 메서드**를 사용한다:

```java
// 좋은 예 — 인수를 설명하는 이름
Complex fulcrumPoint = Complex.FromRealNumber(23.0);

// 나쁜 예
Complex fulcrumPoint = new Complex(23.0);
```

---

## 9. 기발한 이름은 피하라

이름이 너무 기발하면 저자와 유머 감각이 비슷한 사람만, 그리고 농담을 기억하는 동안만 이름을 기억한다.

| 기발한 이름 | 명료한 이름 |
|---|---|
| `HolyHandGrenade`(*HolyHandGrenade — 몬티 파이썬에 나오는 가상의 무기(수류탄)*) | `DeleteItems` |
| `whack()` | `kill()` |
| `eatMyShort()` | `abort()` |

**재미난 이름보다 명료한 이름을 선택하라. 의도를 분명하고 솔직하게 표현하라.**

---

## 10. 한 개념에 한 단어를 사용하라

추상적인 개념 하나에 단어 하나를 선택해 이를 고수한다.

| 혼란스러운 사용 | 문제 |
|---|---|
| 클래스마다 `fetch`, `retrieve`, `get` 혼용 | 어느 클래스에서 어느 이름을 썼는지 기억 불가 |
| `controller`, `manager`, `driver` 혼용 | `DeviceManager`와 `ProtocolController`는 근본적으로 어떻게 다른가? |

**일관성 있는 어휘는 코드를 사용할 프로그래머가 반갑게 여길 선물이다.**

---

## 11. 말장난을 하지 마라

한 단어를 두 가지 목적으로 사용하지 마라. "한 개념에 한 단어를 사용하라"는 규칙과 혼동하지 말 것.

예를 들어, 기존 `add` 메서드가 모두 두 값을 더하거나 이어서 새로운 값을 만든다고 가정하자. 새로 작성하는 메서드가 집합에 값 하나를 추가한다면?

- **나쁜 선택**: `add` — 기존 `add`와 맥락이 다르므로 말장난
- **좋은 선택**: `insert` 또는 `append`

> **핵심 통찰**: 프로그래머는 코드를 최대한 이해하기 쉽게 짜야 한다. 의미를 해독할 책임이 독자에게 있는 '논문 모델'이 아니라, 의도를 밝힐 책임이 저자에게 있는 **'잡지 모델'** 이 바람직하다.

---

## 12. 해법 영역과 문제 영역에서 이름 가져오기

### 해법 영역(Solution Domain)에서 가져온 이름

코드를 읽을 사람도 프로그래머라는 사실을 명심한다. 전산 용어, 알고리즘 이름, 패턴 이름, 수학 용어 등을 사용해도 괜찮다.

- `AccountVisitor` — VISITOR 패턴에 친숙한 프로그래머는 금방 이해
- `JobQueue` — 모르는 프로그래머가 있을까?

### 문제 영역(Problem Domain)에서 가져온 이름

적절한 프로그래머 용어가 없다면 문제 영역에서 이름을 가져온다. 코드를 보수하는 프로그래머가 분야 전문가에게 의미를 물어 파악할 수 있다.

우수한 프로그래머와 설계자라면 **해법 영역과 문제 영역을 구분할 줄 알아야 한다.**

---

## 13. 의미 있는 맥락을 추가하라

대다수 이름은 스스로 의미가 분명하지 않다. 클래스, 함수, 이름 공간에 넣어 맥락을 부여한다. 모든 방법이 실패하면 마지막 수단으로 접두어를 붙인다.

예: `firstName`, `lastName`, `street`, `state`, `zipcode` — 변수를 훑어보면 주소라는 사실을 알아챈다. 하지만 `state` 변수 하나만 사용한다면?

**해결 방법의 단계:**
1. 접두어 추가: `addrFirstName`, `addrLastName`, `addrState`
2. 클래스 생성: `Address` 클래스에 변수를 넣는다 (더 좋음)

### 맥락 개선 예제

```java
// 나쁜 예 — 맥락이 불분명한 변수
private void printGuessStatistics(char candidate, int count) {
    String number;
    String verb;
    String pluralModifier;
    if (count == 0) {
        number = "no";
        verb = "are";
        pluralModifier = "s";
    } else if (count == 1) {
        number = "1";
        verb = "is";
        pluralModifier = "";
    } else {
        number = Integer.toString(count);
        verb = "are";
        pluralModifier = "s";
    }
    String guessMessage = String.format(
        "There %s %s %s%s", verb, number, candidate, pluralModifier
    );
    print(guessMessage);
}
```

함수가 길고, 세 변수의 맥락이 함수 전반에 흩어져 있다. `GuessStatisticsMessage` 클래스를 만들면:

```java
// 좋은 예 — 맥락이 분명한 변수
public class GuessStatisticsMessage {
    private String number;
    private String verb;
    private String pluralModifier;

    public String make(char candidate, int count) {
        createPluralDependentMessageParts(count);
        return String.format(
            "There %s %s %s%s",
            verb, number, candidate, pluralModifier);
    }

    private void createPluralDependentMessageParts(int count) {
        if (count == 0) {
            thereAreNoLetters();
        } else if (count == 1) {
            thereIsOneLetter();
        } else {
            thereAreManyLetters(count);
        }
    }

    private void thereAreManyLetters(int count) {
        number = Integer.toString(count);
        verb = "are";
        pluralModifier = "s";
    }

    private void thereIsOneLetter() {
        number = "1";
        verb = "is";
        pluralModifier = "";
    }

    private void thereAreNoLetters() {
        number = "no";
        verb = "are";
        pluralModifier = "s";
    }
}
```

세 변수는 확실하게 `GuessStatisticsMessage`에 속한다. 맥락을 개선하면 함수를 쪼개기가 쉬워지므로 알고리즘도 더 명확해진다.

---

## 14. 불필요한 맥락을 없애라

'고급 휘발유 충전소(Gas Station Deluxe)' 애플리케이션의 모든 클래스 이름을 `GSD`로 시작하겠다는 생각은 바람직하지 못하다. IDE에서 `G`를 입력하고 자동 완성을 누르면 모든 클래스가 열거된다.

| 나쁜 예 | 좋은 예 |
|---|---|
| `GSDAccountAddress` | `Address` (클래스 이름으로 적합) |
| 17자 중 10자가 중복이거나 부적절 | 포트 주소, MAC 주소, 웹 주소 구분 필요 시: `PostalAddress`, `MAC`, `URI` |

일반적으로 **짧은 이름이 긴 이름보다 좋다** — 단, 의미가 분명한 경우에 한해서. 이름에 불필요한 맥락을 추가하지 않도록 주의한다.

---

## 이름 짓기 규칙 종합

| # | 규칙 | 핵심 |
|---|---|---|
| 1 | 의도를 분명히 밝혀라 | 주석 없이도 존재 이유/기능/사용법이 드러나야 |
| 2 | 그릇된 정보를 피하라 | 이미 의미가 있는 단어, 흡사한 이름 주의 |
| 3 | 의미 있게 구분하라 | 숫자 덧붙이기(`a1`, `a2`)와 불용어(`Info`, `Data`) 금지 |
| 4 | 발음하기 쉬운 이름 | 프로그래밍은 사회 활동, 토론 가능해야 |
| 5 | 검색하기 쉬운 이름 | 이름 길이는 범위 크기에 비례 |
| 6 | 인코딩을 피하라 | 헝가리식 표기법, `m_` 접두어, `I` 접두어 불필요 |
| 7 | 기억력을 자랑하지 마라 | 명료함이 최고, 전문가는 남들이 이해하는 코드를 작성 |
| 8 | 클래스=명사, 메서드=동사 | 생성자 오버로드 시 정적 팩토리 메서드 |
| 9 | 기발한 이름은 피하라 | 재미보다 명료함 |
| 10 | 한 개념에 한 단어 | `fetch`/`retrieve`/`get` 혼용 금지 |
| 11 | 말장난 하지 마라 | 맥락이 다르면 다른 단어 사용 |
| 12 | 해법/문제 영역 구분 | 기술 용어 OK, 없으면 도메인에서 가져오기 |
| 13 | 의미 있는 맥락 추가 | 클래스로 감싸기 > 접두어 |
| 14 | 불필요한 맥락 없애기 | 짧은 이름이 긴 이름보다 좋다 (의미 분명하면) |

---

## 요약

- **이름 하나 잘 짓는 것이 주석 열 줄보다 낫다** — 의도를 분명히, 그릇된 정보 없이, 의미 있게 구분하라
- **발음과 검색이 쉬운 이름**을 사용하라 — 프로그래밍은 사회 활동이다
- **인코딩을 피하라** — 헝가리식 표기법과 멤버 변수 접두어는 현대 IDE에서 불필요하다
- **클래스는 명사, 메서드는 동사** — 생성자 오버로드 시 정적 팩토리 메서드가 좋다
- **한 개념에 한 단어, 말장난 금지** — 일관성과 명확성 사이의 균형
- **맥락은 클래스로 부여**하되, 불필요한 맥락은 제거하라
- 좋은 이름을 선택하는 능력은 기술 문제가 아니라 **교육 문제**다 — 이름을 바꾸는 것을 두려워하지 마라

---

## 다른 챕터와의 관계

- **← Chapter 1 (깨끗한 코드)**: 워드 커닝햄이 말한 "짐작한 대로 동작하는 코드"의 첫 번째 조건이 좋은 이름이다
- **→ Chapter 3 (함수)**: 함수 이름 짓기(서술적인 이름, 동사와 키워드)가 이 장의 규칙을 함수에 적용한 것이다
- **→ Chapter 4 (주석)**: "함수나 변수로 표현할 수 있다면 주석을 달지 마라" — 좋은 이름은 주석의 필요성을 줄인다
- **→ Chapter 6 (객체와 자료 구조)**: 추상화 수준에 맞는 이름 선택이 자료 추상화의 핵심이다
- **→ Chapter 17 (냄새와 휴리스틱)**: [N1]~[N7] 이름 관련 냄새 항목이 이 장의 규칙을 코드 리뷰 체크리스트로 정리한 것이다
