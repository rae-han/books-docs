# Chapter 16: Refactoring SerialDate (SerialDate 리팩터링)

## 핵심 질문

오픈 소스로 공개된 우수한 코드를 전문가 관점에서 비판적으로 검토하고 개선하려면 어떤 과정을 거치는가? 추상 클래스에 섞여 있는 구현 세부사항을 어떻게 분리하는가?

---

## 1. 코드 리뷰의 자세

이 장에서는 JCommon 라이브러리의 `org.jfree.date.SerialDate` 클래스를 리팩터링한다. `SerialDate`를 구현한 데이비드 길버트(David Gilbert)는 확실히 숙련된 우수한 프로그래머다. `SerialDate`는 분명히 '우수한' 코드다. 그럼에도 이 장에서는 코드를 낱낱이 까발긴다.

저자가 강조하는 코드 리뷰의 자세:

- **악의나 자만이 아니다** — 전문가 입장에서 수행하는 검토, 그 이상도 그 이하도 아니다
- **우리 모두가 편안하게 여겨야 할 활동**이다 — 남이 내게 해줄 때 감사히 반겨야 한다
- **이와 같은 비판이 있어야만 발전도 가능**하다 — 의사, 조종사, 법률가 모두 동료 검토를 한다

> **핵심 통찰**: 코드 리뷰는 공격이 아니라 전문가 활동이다. 우리 프로그래머들도 서로의 코드를 검토하는 방법을 배워야 한다.

---

## 2. SerialDate 개요

`SerialDate`는 날짜를 표현하는 자바 추상 클래스다. `java.util.Date`나 `java.util.Calendar`와 달리, 시간 없이 **순수한 날짜만** 다루기 위해 만들어졌다. 1899년 12월 30일을 기준으로 경과한 날짜 수(일련번호)를 사용하는 구현 방식이다.

주요 클래스 구조:

| 클래스 | 역할 |
|---|---|
| `SerialDate` (추상) | 날짜를 표현하는 추상 인터페이스 |
| `SpreadsheetDate` (구체) | 일련번호 기반의 구체적 구현 |
| `MonthConstants` (인터페이스) | 월을 정의하는 `static final` 상수 모음 |
| `SerialDateTests` | 기존 단위 테스트 |

---

## 3. 첫째, 돌려보자 — 테스트 커버리지 개선

리팩터링 전에 먼저 기존 테스트를 돌려본다.

### 기존 테스트의 문제점

기존 `SerialDateTests` 클래스는 돌려보면 실패하는 테스트 케이스가 없다. 하지만 테스트 케이스를 훑어보면 **모든 경우를 점검하지 않는다**는 사실이 드러난다:

- `MonthCodeToQuarter` 메서드를 전혀 호출하지 않음 [F4]
- 코드 커버리지 분석(Clover) 결과: 실행 가능한 문장 185개 중 **91개만 실행** (약 50%) [T2]

### 독자적 단위 테스트 작성

저자는 독자적으로 단위 테스트를 구현했다. 그 과정에서 **여러 버그를 발견**했다:

#### 버그 1: getFollowingDayOfWeek 경계 조건 오류 [G3] [T1] [T5]

2004년 12월 25일(토요일)의 다음 토요일은 2005년 1월 1일이어야 한다. 하지만 메서드는 12월 25일을 다음 토요일로 반환했다. 전형적인 경계 조건 오류였다.

```java
// 이전 (버그)
if (baseDOW > targetWeekday) {

// 이후 (수정)
if (baseDOW >= targetWeekday) {
```

#### 버그 2: getNearestDayOfWeek 알고리즘 오류 [T5] [T7]

가장 가까운 날짜가 **미래**에 있을 때 실패하는 패턴이 발견되었다. 변수 `adjust`가 항상 음수여서 4 이상이 될 가능성이 없었다 — 알고리즘 자체가 틀렸다.

```java
// 수정된 알고리즘
int delta = targetDOW - base.getDayOfWeek();
int positiveDelta = delta + 7;
int adjust = positiveDelta % 7;
if (adjust > 3)
    adjust -= 7;
return SerialDate.addDays(adjust, base);
```

#### 버그 3: stringToWeekdayCode 대소문자 구분 [G2]

`stringToWeekdayCode` 메서드가 대소문자를 구분하여 "monday"를 인식하지 못했다. `equalsIgnoreCase`로 변경하여 수정했다.

### 테스트 결과

새 단위 테스트는 실행 가능한 문장 185개 중 **170개를 실행** (약 92% 커버리지). 주석 처리된 실패 테스트 케이스를 모두 통과시킨 후 리팩터링을 시작했다.

---

## 4. 둘째, 고쳐보자 — 체계적 리팩터링

### 4.1 변경 이력 삭제 [C1]

라이선스 정보와 저작권은 보존하되, 변경 이력은 삭제했다. 소스 코드 제어 도구가 이력을 관리하므로 소스 코드에 변경 이력을 유지하는 것은 1960년대 방식이다.

### 4.2 import 문 정리 [J1]

장황한 import 문을 `java.text.*`와 `java.util.*`로 줄였다.

### 4.3 Javadoc 주석의 HTML 태그 정리 [G1]

한 소스 코드에 자바, 영어, Javadoc, HTML이라는 **네 가지 언어**를 사용하는 것은 바람직하지 않다. 주석 전부를 `<pre>`로 감싸 소스 코드에 보이는 형식이 Javadoc에 그대로 유지되도록 했다.

### 4.4 클래스 이름 변경: SerialDate → DayDate [N1] [N2]

`SerialDate`라는 이름의 두 가지 문제:

| 문제 | 설명 |
|---|---|
| **서술적이지 않다** [N1] | '일련번호(serial number)'보다 '상대 오프셋(relative offset)'이 더 정확. '서수(ordinal)'가 더 적절 |
| **구현을 암시한다** [N2] | 추상 클래스인데 구현 방식을 이름에 노출. 추상화 수준이 올바르지 못함 |

이름 후보 검토:

| 후보 | 문제 |
|---|---|
| `Date` | 자바 라이브러리에 이미 너무 많이 존재 |
| `Day` | 너무 많이 쓰이는 이름 |
| **`DayDate`** | 최종 선택 |

### 4.5 MonthConstants를 enum으로 변환 [J2]

상수 클래스를 상속하는 방식은 옛날 자바 프로그래머들의 기교였다. `MonthConstants`를 `enum`으로 정의하여:

- 달(月)을 `int`로 받던 메서드가 이제 `Month`로 받으므로 **타입 안전성**이 보장된다
- `isValidMonthCode` 메서드가 불필요해졌다 [G9]
- `monthCodeToQuarter`와 같은 오류 검사 코드도 불필요해졌다 [G5]

```java
public abstract class DayDate implements Comparable, Serializable {
    public static enum Month {
        JANUARY(1), FEBRUARY(2), MARCH(3), APRIL(4),
        MAY(5), JUNE(6), JULY(7), AUGUST(8),
        SEPTEMBER(9), OCTOBER(10), NOVEMBER(11), DECEMBER(12);

        Month(int index) { this.index = index; }

        public static Month make(int monthIndex) {
            for (Month m : Month.values())
                if (m.index == monthIndex) return m;
            throw new IllegalArgumentException("Invalid month index " + monthIndex);
        }

        public final int index;
    }
}
```

### 4.6 serialVersionUID 제거 [G4]

`serialVersionUID`를 선언하지 않으면 컴파일러가 자동으로 생성한다. 저자는 자동 제어가 더 안전하다고 판단했다:

- 깜빡하고 `serialVersionUID`를 변경하지 않아 생기는 **모호한 오류**보다
- `InvalidClassException`이라는 **명확한 오류**를 디버깅하는 편이 낫다

### 4.7 구현 세부사항을 SpreadsheetDate로 이동 [G6]

추상 클래스 `DayDate`에 구체적 구현 정보가 포함되어서는 안 된다.

| 변수/메서드 | 이동 방향 | 이유 |
|---|---|---|
| `EARLIEST_DATE_ORDINAL`, `LATEST_DATE_ORDINAL` | → `SpreadsheetDate` | `SpreadsheetDate`만 사용 |
| `MINIMUM_YEAR_SUPPORTED`, `MAXIMUM_YEAR_SUPPORTED` | → `SpreadsheetDate` (팩토리를 통해 접근) | 구현에 의존하는 정보 |
| `AGGREGATE_DAYS_TO_END_OF_MONTH` | 삭제 | JCommon 어디서도 사용하지 않음 [G9] |
| `AGGREGATE_DAYS_TO_END_OF_PRECEDING_MONTH` | → `SpreadsheetDate` | `SpreadsheetDate`에서만 사용 [G10] |
| `leapYearCount` | → `SpreadsheetDate` | `SpreadsheetDate`의 두 메서드만 호출 |

### 4.8 ABSTRACT FACTORY 패턴 적용 [G7]

기반 클래스가 파생 클래스를 직접 참조하는 것은 바람직하지 않다. 기존 `createInstance` 메서드는 `SpreadsheetDate` 인스턴스를 직접 생성했다.

ABSTRACT FACTORY 패턴을 적용해 `DayDateFactory`를 만들었다:

```java
public abstract class DayDateFactory {
    private static DayDateFactory factory = new SpreadsheetDateFactory();

    public static void setInstance(DayDateFactory factory) {
        DayDateFactory.factory = factory;
    }

    protected abstract DayDate _makeDate(int ordinal);
    protected abstract DayDate _makeDate(int day, DayDate.Month month, int year);
    protected abstract DayDate _makeDate(int day, int month, int year);
    protected abstract DayDate _makeDate(java.util.Date date);
    protected abstract int _getMinimumYear();
    protected abstract int _getMaximumYear();

    public static DayDate makeDate(int ordinal) {
        return factory._makeDate(ordinal);
    }
    // ... 나머지 정적 위임 메서드들
}
```

`createInstance` 메서드를 `makeDate`라는 더 서술적인 이름으로 변경했다 [N1]. SINGLETON, DECORATOR, ABSTRACT FACTORY 패턴을 조합해 사용한다.

### 4.9 요일과 상수를 enum으로 변환 [J3]

요일 상수와 기타 상수들을 enum으로 변환했다:

```java
public enum Day {
    MONDAY(Calendar.MONDAY),
    TUESDAY(Calendar.TUESDAY),
    // ...
    SUNDAY(Calendar.SUNDAY);

    public final int index;
    private static DateFormatSymbols dateSymbols = new DateFormatSymbols();

    Day(int day) { index = day; }

    public static Day make(int index) throws IllegalArgumentException {
        for (Day d : Day.values())
            if (d.index == index) return d;
        throw new IllegalArgumentException(
            String.format("Illegal day index: %d.", index));
    }

    public static Day parse(String s) throws IllegalArgumentException {
        String[] shortWeekdayNames = dateSymbols.getShortWeekdays();
        String[] weekDayNames = dateSymbols.getWeekdays();
        s = s.trim();
        for (Day day : Day.values()) {
            if (s.equalsIgnoreCase(shortWeekdayNames[day.index]) ||
                s.equalsIgnoreCase(weekDayNames[day.index]))
                return day;
        }
        throw new IllegalArgumentException(
            String.format("%s is not a valid weekday string", s));
    }

    public String toString() {
        return dateSymbols.getWeekdays()[index];
    }
}
```

범위 끝 날짜 포함 여부를 지정하는 상수도 enum으로 변환했다:

| 원래 상수 | enum | 수학적 명칭 |
|---|---|---|
| `INCLUDE_NONE` | `OPEN` | 개구간 |
| `INCLUDE_FIRST` | `CLOSED_LEFT` | 반개구간 (왼쪽 닫힘) |
| `INCLUDE_SECOND` | `CLOSED_RIGHT` | 반개구간 (오른쪽 닫힘) |
| `INCLUDE_BOTH` | `CLOSED` | 폐구간 |

### 4.10 메서드를 적절한 클래스로 이동 [G13] [G14]

**기능 욕심(Feature Envy)** 이 보이는 메서드를 해당 enum이나 적절한 클래스로 이동했다:

| 메서드 | 이전 위치 | 이후 위치 | 이유 |
|---|---|---|---|
| `stringToWeekdayCode` | `DayDate` | `Day.parse()` | Day의 구문분석 메서드 [G14] |
| `weekdayCodeToString` | `DayDate` | `Day.toString()` | Day의 문자열 변환 [G14] |
| `monthCodeToQuarter` | `DayDate` | `Month.quarter()` | Month의 기능 [G14] |
| `monthCodeToString` | `DayDate` | `Month.toString()`, `Month.toShortString()` | Month의 문자열 변환 [G14] |
| `stringToMonthCode` | `DayDate` | `Month.parse()` | Month의 구문분석 [G14] |

### 4.11 정적 메서드를 인스턴스 메서드로 변환 [G18]

`addDays`, `addMonths`, `addYears` 등의 메서드는 DayDate 변수를 사용하므로 정적 메서드여서는 안 된다.

```java
// 이전: 정적 메서드
public static SerialDate addDays(int days, SerialDate base) {
    int serialDayNumber = base.toSerial() + days;
    return SerialDate.createInstance(serialDayNumber);
}

// 이후: 인스턴스 메서드
public DayDate addDays(int days) {
    return DayDateFactory.makeDate(toOrdinal() + days);
}
```

### 4.12 메서드 이름 개선: date.addDays(5)의 모호함 [N4] [G20]

```java
DayDate date = DateFactory.makeDate(5, Month.DECEMBER, 1952);
date.addDays(7); // date 객체가 변경되는가? 새 인스턴스가 반환되는가?
```

`addDays`는 `date` 객체를 변경한다고 오해할 소지가 있다. 실제로는 새 `DayDate` 인스턴스를 반환한다. `plusDays`로 이름을 변경하면 의도가 명확해진다:

```java
// 명확한 표현: 새 인스턴스 반환
DayDate date = oldDate.plusDays(5);

// 이 코드는 반환값을 사용하지 않으므로 의미 없다는 사실이 분명해짐
date.plusDays(5);  // 결과를 사용하지 않으면 무의미
```

### 4.13 알고리즘 단순화와 임시 변수 설명 [G19] [G21]

복잡한 알고리즘을 임시 변수 설명(Explaining Temporary Variables)을 사용해 읽기 쉽게 고쳤다:

```java
// addMonths 개선
public DayDate addMonths(int months) {
    int thisMonthAsOrdinal = 12 * getYear() + getMonth().index - 1;
    int resultMonthAsOrdinal = thisMonthAsOrdinal + months;
    int resultYear = resultMonthAsOrdinal / 12;
    Month resultMonth = Month.make(resultMonthAsOrdinal % 12 + 1);
    int lastDayOfResultMonth = lastDayOfMonth(resultMonth, resultYear);
    int resultDay = Math.min(getDayOfMonth(), lastDayOfResultMonth);
    return DayDateFactory.makeDate(resultDay, resultMonth, resultYear);
}

// getPreviousDayOfWeek 단순화
public DayDate getPreviousDayOfWeek(Day targetDayOfWeek) {
    int offsetToTarget = targetDayOfWeek.index - getDayOfWeek().index;
    if (offsetToTarget >= 0)
        offsetToTarget -= 7;
    return plusDays(offsetToTarget);
}

// getFollowingDayOfWeek 단순화
public DayDate getFollowingDayOfWeek(Day targetDayOfWeek) {
    int offsetToTarget = targetDayOfWeek.index - getDayOfWeek().index;
    if (offsetToTarget <= 0)
        offsetToTarget += 7;
    return plusDays(offsetToTarget);
}
```

### 4.14 가독성 개선: isLeapYear [G16]

```java
// 이전: 단일 조건문
public static boolean isLeapYear(int year) {
    return ((year % 4 == 0) && (year % 100 != 0)) || (year % 400 == 0);
}

// 이후: 서술적인 표현
public static boolean isLeapYear(int year) {
    boolean fourth = year % 4 == 0;
    boolean hundredth = year % 100 == 0;
    boolean fourHundredth = year % 400 == 0;
    return fourth && (!hundredth || fourHundredth);
}
```

### 4.15 논리적 의존성을 물리적 의존성으로 [G22]

`getDayOfWeek` 메서드는 서수 날짜 시작일의 요일에 **암시적으로** 의존한다. 물리적 의존성은 없지만 논리적 의존성이 존재하므로, 추상 메서드 `getDayOfWeekForOrdinalZero`를 만들어 의존성을 명시했다:

```java
// DayDate에서 구현
public Day getDayOfWeek() {
    Day startingDay = getDayOfWeekForOrdinalZero();
    int startingOffset = startingDay.index - Day.SUNDAY.index;
    return Day.make((getOrdinalDay() + startingOffset) % 7 + 1);
}

// SpreadsheetDate에서 구체화
protected Day getDayOfWeekForOrdinalZero() {
    return Day.SATURDAY;
}
```

> **핵심 통찰**: 뭔가가 구현에 논리적으로 의존한다면 물리적으로도 의존해야 마땅하다.

### 4.16 if 문 연쇄를 enum 다형성으로 제거 [G23]

`isInRange` 메서드의 `if` 문 연쇄를 `DateInterval` enum으로 옮겼다:

```java
public enum DateInterval {
    OPEN {
        public boolean isIn(int d, int left, int right) {
            return d > left && d < right;
        }
    },
    CLOSED_LEFT {
        public boolean isIn(int d, int left, int right) {
            return d >= left && d < right;
        }
    },
    CLOSED_RIGHT {
        public boolean isIn(int d, int left, int right) {
            return d > left && d <= right;
        }
    },
    CLOSED {
        public boolean isIn(int d, int left, int right) {
            return d >= left && d <= right;
        }
    };
    public abstract boolean isIn(int d, int left, int right);
}

public boolean isInRange(DayDate d1, DayDate d2, DateInterval interval) {
    int left = Math.min(d1.getOrdinalDay(), d2.getOrdinalDay());
    int right = Math.max(d1.getOrdinalDay(), d2.getOrdinalDay());
    return interval.isIn(getOrdinalDay(), left, right);
}
```

### 4.17 final 키워드 제거 [G12]

인수와 변수 선언에서 `final` 키워드를 모두 없앴다. 실질적인 가치는 없으면서 코드만 복잡하게 만든다고 판단했기 때문이다. 단위 테스트가 `final` 키워드로 잡아낼 오류를 모두 잡아낸다.

---

## 5. 리팩터링 최종 정리

마지막으로 전체 작업을 정리하면 다음과 같다:

| # | 작업 | 적용 원칙 |
|---|---|---|
| 1 | 주석 정리: 변경 이력 삭제, 불필요한 주석 제거 | [C1] [C2] |
| 2 | enum 분리: `Month`, `Day`, `WeekInMonth`, `DateInterval`, `WeekdayRange`를 독자적 소스 파일로 | [G12] [G13] |
| 3 | 정적 변수/메서드를 `DateUtil` 클래스로 이동 | [G6] |
| 4 | 추상 메서드를 `DayDate` 클래스로 끌어올림 | [G24] |
| 5 | `Month.make` → `Month.fromInt`로 이름 변경, `toInt()` 접근자 추가, `index` 필드를 `private`로 | [N1] |
| 6 | `plusYears`와 `plusMonths`의 중복을 `correctLastDayOfMonth` 메서드로 제거 | [G5] |
| 7 | 매직 넘버 `1`을 `Month.JANUARY.toInt()` 또는 `Day.SUNDAY.toInt()`로 교체 | [G25] |

### 최종 코드 커버리지

리팩터링 후 DayDate 코드 커버리지는 **84.9%**로 나타났다. 커버리지가 감소한 것은 테스트 코드가 줄어서가 아니라 **클래스 크기가 작아지는 바람에** 테스트하지 않는 코드의 비중이 커졌기 때문이다. 테스트 케이스는 DayDate 53개 실행 문 중 45개를 테스트한다. 테스트하지 않는 코드는 너무 사소해 테스트할 필요도 없다.

---

## 6. 리팩터링 과정에서 참조한 코드 냄새 모음

이 장의 리팩터링 과정에서 참조된 코드 냄새와 휴리스틱을 분류별로 정리한다:

### 주석 (C)

| 번호 | 규칙 | 적용 예시 |
|---|---|---|
| C1 | 부적절한 정보 | 변경 이력 삭제, 일련번호 관련 주석 정리 |
| C2 | 쓸모 없는 주석 | 오래된 주석 제거, 중복 주석 삭제 |
| C3 | 중복된 주석 | 코드만으로 의미가 분명한 곳의 주석 삭제 |

### 자바 (J)

| 번호 | 규칙 | 적용 예시 |
|---|---|---|
| J1 | 긴 import 문을 와일드카드로 | `java.text.*`, `java.util.*` |
| J2 | 상수 상속 대신 enum | `MonthConstants` → `Month` enum |
| J3 | 상수 대신 enum | 요일, 주차, 날짜 범위 등 |

### 이름 (N)

| 번호 | 규칙 | 적용 예시 |
|---|---|---|
| N1 | 서술적인 이름 | `SerialDate` → `DayDate`, `toSerial` → `getOrdinalDay`, `createInstance` → `makeDate` |
| N2 | 추상화 수준에 맞는 이름 | `SerialDate`는 구현을 암시하므로 부적절 |
| N3 | 표준 명명법을 따르라 | `INCLUDE_BOTH` → `CLOSED` (수학적 명칭) |
| N4 | 명확한 이름 | `addDays` → `plusDays` (부수효과 없음을 명시) |

### 일반 (G)

| 번호 | 규칙 | 적용 예시 |
|---|---|---|
| G1 | 한 소스에 여러 언어 | Javadoc에서 HTML 태그 사용 줄임 |
| G2 | 당연한 동작을 구현하지 않음 | 대소문자 구분 없이 요일 파싱 |
| G3 | 경계를 올바로 처리 | `getFollowingDayOfWeek` 경계 버그 |
| G4 | 안전 절차 무시 | `serialVersionUID` 자동 제어 |
| G5 | 중복 | `plusYears`/`plusMonths` 중복 제거 |
| G6 | 추상화 수준이 올바르지 않다 | 구현 정보를 `SpreadsheetDate`로 이동 |
| G7 | 기반 클래스가 파생 클래스에 의존 | `ABSTRACT FACTORY` 패턴 적용 |
| G9 | 죽은 코드 | 사용하지 않는 배열, 메서드 삭제 |
| G10 | 수직 분리 | 변수를 사용하는 위치 가까이로 이동 |
| G12 | 잡동사니 | 불필요한 `final`, 기본 생성자 제거 |
| G13 | 인위적 결합 | `Day` enum을 독자적 파일로 분리 |
| G14 | 기능 욕심 | 메서드를 해당 데이터가 있는 클래스로 이동 |
| G18 | 부적절한 static | `addDays` 등을 인스턴스 메서드로 변경 |
| G22 | 논리적 의존성은 물리적으로 드러내라 | `getDayOfWeekForOrdinalZero` 추상 메서드 추가 |
| G25 | 매직 넘버 대신 명명된 상수 | `1` → `Month.JANUARY.toInt()` |

---

## 요약

- **코드 리뷰는 전문가 활동**이다 — 악의나 자만이 아니라 동료 간 성장을 위한 필수 과정이다
- **돌려보기가 먼저**다 — 리팩터링 전에 테스트 커버리지를 높이고 버그를 먼저 잡는다
- **추상 클래스에 구현 세부사항을 넣지 마라** — 구현 정보는 파생 클래스로, 팩토리 패턴으로 생성을 위임한다
- **int 상수보다 enum** — 타입 안전성이 보장되고, 유효성 검사 코드가 불필요해진다
- **정적 메서드를 의심하라** — 인스턴스 데이터를 사용하는 메서드는 인스턴스 메서드여야 한다
- **이름이 의도를 드러내야 한다** — `addDays` vs `plusDays`, `SerialDate` vs `DayDate`
- **논리적 의존성은 물리적으로 드러내라** — 암시적 의존은 버그의 온상이다
- **보이스카우트 규칙**: 체크아웃한 코드보다 좀 더 깨끗한 코드를 체크인하라

---

## 다른 챕터와의 관계

- **← Chapter 2 (의미 있는 이름)**: `SerialDate` → `DayDate`, `addDays` → `plusDays` 등 서술적 이름의 중요성을 대규모로 적용
- **← Chapter 6 (객체와 자료 구조)**: 추상 클래스와 구체 클래스의 책임 분리, ABSTRACT FACTORY 패턴 적용이 객체 지향 설계의 실전 사례
- **← Chapter 9 (단위 테스트)**: 테스트 커버리지 50% → 92%로 높이는 과정, 경계 조건 테스트의 중요성
- **← Chapter 10 (클래스)**: SRP 적용으로 DayDate에서 구현 세부사항을 분리하고, 관련 메서드를 적절한 enum으로 이동
- **← Chapter 14 (점진적인 개선)**: 코드를 고칠 때마다 테스트를 실행하는 TDD 방식의 리팩터링
- **← Chapter 15 (JUnit 들여다보기)**: 15장과 동일한 보이스카우트 규칙 적용이지만, 규모가 훨씬 크고 구조적 변경(팩토리 패턴, enum 도입)까지 포함
- **→ Chapter 17 (냄새와 휴리스틱)**: 이 장에서 사용된 [C1]-[C3], [G1]-[G25], [J1]-[J3], [N1]-[N4] 등의 체계적인 정의와 설명이 17장에 있다
