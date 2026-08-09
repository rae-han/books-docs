# Chapter 12: Polymorphism (다형성)

## 핵심 질문

다형성이란 무엇이며 어떤 종류가 있는가? 객체지향 시스템은 런타임에 어떻게 적절한 메서드를 선택하는가? self 참조와 super 참조는 메서드 탐색 과정에서 어떤 역할을 하며, 상속은 본질적으로 위임과 어떤 관계인가?

---

## 1. 다형성의 분류

**다형성**(*Polymorphism - 그리스어 poly(많은) + morph(형태)의 합성어로, 하나의 추상 인터페이스에 서로 다른 구현을 연결할 수 있는 능력*)이라는 단어는 '많은 형태를 가질 수 있는 능력'을 의미한다. 컴퓨터 과학에서 다형성은 하나의 추상 인터페이스에 대해 코드를 작성하고 이 추상 인터페이스에 대해 서로 다른 구현을 연결할 수 있는 능력으로 정의한다. 간단히 말해서 다형성은 **여러 타입을 대상으로 동작할 수 있는 코드를 작성할 수 있는 방법**이다.

객체지향 프로그래밍에서 사용되는 다형성은 크게 **유니버설 다형성**과 **임시 다형성**으로 분류할 수 있다.

```
                          다형성
                       (Polymorphism)
                     ┌───────┴───────┐
                유니버설                임시
               (Universal)           (Ad Hoc)
              ┌────┴────┐         ┌────┴────┐
           매개변수     포함     오버로딩     강제
         (Parametric) (Inclusion) (Overloading) (Coercion)
```

### 1.1 오버로딩 다형성

하나의 클래스 안에 **동일한 이름의 메서드가 존재**하는 경우를 오버로딩 다형성이라고 부른다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Money {
    public Money plus(Money amount) { ... }
    public Money plus(BigDecimal amount) { ... }
    public Money plus(long amount) { ... }
}
```

</details>

```typescript
// TypeScript — 오버로딩 시그니처
class Money {
    plus(amount: Money): Money;
    plus(amount: bigint): Money;
    plus(amount: number): Money;
    plus(amount: Money | bigint | number): Money {
        // 구현
    }
}
```

메서드 오버로딩을 사용하면 `plusMoney`, `plusBigDecimal`, `plusLong`이라는 이름을 모두 기억할 필요 없이 `plus`라는 하나의 이름만 기억하면 된다. 유사한 작업을 수행하는 메서드의 이름을 통일할 수 있기 때문에 기억해야 하는 이름의 수를 극적으로 줄일 수 있다.

### 1.2 강제 다형성

**강제 다형성**(*Coercion Polymorphism*)은 언어가 지원하는 자동적인 타입 변환이나 사용자가 직접 구현한 타입 변환을 이용해 동일한 연산자를 다양한 타입에 사용할 수 있는 방식을 가리킨다.

예를 들어 자바에서 이항 연산자인 `+`는 피연산자가 모두 정수일 경우에는 **정수에 대한 덧셈 연산자**로 동작하지만, 하나는 정수형이고 다른 하나는 문자열인 경우에는 **연결 연산자**로 동작한다. 이때 정수형 피연산자는 문자열 타입으로 강제 형변환된다.

일반적으로 오버로딩 다형성과 강제 다형성을 함께 사용하면 모호해질 수 있는데, 실제로 어떤 메서드가 호출될지를 판단하기가 어려워지기 때문이다.

### 1.3 매개변수 다형성

**매개변수 다형성**(*Parametric Polymorphism*)은 제네릭 프로그래밍과 관련이 높은데, 클래스의 인스턴스 변수나 메서드의 매개변수 타입을 **임의의 타입으로 선언**한 후 사용하는 시점에 구체적인 타입으로 지정하는 방식을 가리킨다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
List<String> names = new ArrayList<>();      // T를 String으로 지정
List<Integer> scores = new ArrayList<>();    // T를 Integer로 지정
```

</details>

```typescript
// TypeScript — 제네릭
const names: Array<string> = [];     // T를 string으로 지정
const scores: Array<number> = [];    // T를 number로 지정
```

자바의 `List` 인터페이스는 컬렉션에 보관할 요소의 타입을 임의의 타입 `T`로 지정하고 있으며, 실제 인스턴스를 생성하는 시점에 `T`를 구체적인 타입으로 지정할 수 있게 한다. 따라서 `List` 인터페이스는 다양한 타입의 요소를 다루기 위해 동일한 오퍼레이션을 사용할 수 있다.

### 1.4 포함 다형성

**포함 다형성**(*Inclusion Polymorphism*)은 메시지가 동일하더라도 **수신한 객체의 타입에 따라 실제로 수행되는 행동이 달라지는** 능력을 의미한다. 포함 다형성은 **서브타입 다형성**(*Subtype Polymorphism*)이라고도 부른다. 특별한 언급 없이 '다형성'이라고 할 때는 포함 다형성을 의미하는 것이 일반적이다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Movie {
    private DiscountPolicy discountPolicy;

    public Money calculateMovieFee(Screening screening) {
        return fee.minus(discountPolicy.calculateDiscountAmount(screening));
    }
}
```

</details>

```typescript
// TypeScript
class Movie {
    private discountPolicy: DiscountPolicy;

    calculateMovieFee(screening: Screening): Money {
        return this.fee.minus(
            this.discountPolicy.calculateDiscountAmount(screening)
        );
    }
}
```

`Movie` 클래스는 `discountPolicy`에게 `calculateDiscountAmount` 메시지를 전송하지만, 실제로 실행되는 메서드는 메시지를 수신한 객체의 타입에 따라 달라진다.

포함 다형성을 구현하는 가장 일반적인 방법은 상속을 사용하는 것이다. 두 클래스를 상속 관계로 연결하고 자식 클래스에서 부모 클래스의 메서드를 오버라이딩한 후 클라이언트는 부모 클래스만 참조하면 포함 다형성을 구현할 수 있다.

> **핵심 통찰**: 상속의 진정한 목적은 코드 재사용이 아니라 **다형성을 위한 서브타입 계층을 구축하는 것**이다. 상속을 사용하려는 목적이 단순히 코드를 재사용하기 위해서인지, 아니면 클라이언트 관점에서 인스턴스들을 동일하게 행동하는 그룹으로 묶기 위해서인지 자문해 보라. 전자라면 상속을 사용하지 말아야 한다.

이 장에서는 다형성의 다양한 측면 중에서 **포함 다형성**에 관해 중점적으로 다룬다. 이 장의 목표는 포함 다형성의 관점에서 런타임에 상속 계층 안에서 적절한 메서드를 선택하는 방법을 이해하는 것이다.

---

## 2. 상속의 양면성

객체지향 패러다임의 근간을 이루는 아이디어는 데이터와 행동을 객체라고 불리는 하나의 실행 단위 안으로 통합하는 것이다. 상속 역시 데이터와 행동이라는 두 가지 관점에서 이해해야 한다.

상속의 메커니즘을 이해하는 데 필요한 개념:

- **업캐스팅**
- **동적 메서드 탐색**
  - 동적 바인딩
  - self 참조
  - super 참조

### 2.1 상속을 사용한 강의 평가: Lecture 클래스

수강생들의 성적을 계산하는 간단한 예제로 시작한다. 프로그램은 다음과 같은 형식으로 전체 수강생들의 성적 통계를 출력한다.

```
Pass:3 Fail:2, A:1 B:1 C:1 D:0 F:2
```

출력은 두 부분으로 구성된다. 앞부분의 `Pass:3 Fail:2`는 강의를 이수한 학생의 수와 낙제한 학생의 수를 나타내고, 뒷부분의 `A:1 B:1 C:1 D:0 F:2`는 등급별 학생 분포 현황을 나타낸다.

프로젝트에는 이수/낙제 통계를 출력하는 `Lecture` 클래스가 이미 존재한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Lecture {
    private int pass;
    private String title;
    private List<Integer> scores = new ArrayList<>();

    public Lecture(String title, int pass, List<Integer> scores) {
        this.title = title;
        this.pass = pass;
        this.scores = scores;
    }

    public double average() {
        return scores.stream()
                .mapToInt(Integer::intValue)
                .average().orElse(0);
    }

    public List<Integer> getScores() {
        return Collections.unmodifiableList(scores);
    }

    public String evaluate() {
        return String.format("Pass:%d Fail:%d", passCount(), failCount());
    }

    private long passCount() {
        return scores.stream().filter(score -> score >= pass).count();
    }

    private long failCount() {
        return scores.size() - passCount();
    }
}
```

</details>

```typescript
// TypeScript
class Lecture {
    private pass: number;
    private title: string;
    private scores: number[];

    constructor(title: string, pass: number, scores: number[]) {
        this.title = title;
        this.pass = pass;
        this.scores = [...scores];
    }

    average(): number {
        if (this.scores.length === 0) return 0;
        const sum = this.scores.reduce((a, b) => a + b, 0);
        return sum / this.scores.length;
    }

    getScores(): readonly number[] {
        return Object.freeze([...this.scores]);
    }

    evaluate(): string {
        return `Pass:${this.passCount()} Fail:${this.failCount()}`;
    }

    private passCount(): number {
        return this.scores.filter(score => score >= this.pass).length;
    }

    private failCount(): number {
        return this.scores.length - this.passCount();
    }
}
```

이수 기준이 70점인 객체지향 프로그래밍 과목의 수강생 5명에 대한 성적 통계는 다음과 같이 구한다.

```typescript
const lecture = new Lecture("객체지향 프로그래밍", 70, [81, 95, 75, 50, 45]);
lecture.evaluate(); // "Pass:3 Fail:2"
```

### 2.2 상속을 이용한 Lecture 클래스 재사용: GradeLecture

`Lecture` 클래스를 상속받아 등급별 통계를 추가하는 `GradeLecture` 클래스를 만든다. `Grade` 클래스는 등급의 이름과 각 등급 범위를 정의하는 최소/최대 성적을 인스턴스 변수로 포함한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Grade {
    private String name;
    private int upper, lower;

    private Grade(String name, int upper, int lower) {
        this.name = name;
        this.upper = upper;
        this.lower = lower;
    }

    public String getName() { return name; }

    public boolean isName(String name) {
        return this.name.equals(name);
    }

    public boolean include(int score) {
        return score >= lower && score <= upper;
    }
}

public class GradeLecture extends Lecture {
    private List<Grade> grades;

    public GradeLecture(String name, int pass, List<Grade> grades,
                        List<Integer> scores) {
        super(name, pass, scores);
        this.grades = grades;
    }

    @Override
    public String evaluate() {
        return super.evaluate() + ", " + gradesStatistics();
    }

    private String gradesStatistics() {
        return grades.stream()
                .map(grade -> format(grade))
                .collect(joining(" "));
    }

    private String format(Grade grade) {
        return String.format("%s:%d", grade.getName(), gradeCount(grade));
    }

    private long gradeCount(Grade grade) {
        return getScores().stream()
                .filter(grade::include)
                .count();
    }

    public double average(String gradeName) {
        return grades.stream()
                .filter(each -> each.isName(gradeName))
                .findFirst()
                .map(this::gradeAverage)
                .orElse(0d);
    }

    private double gradeAverage(Grade grade) {
        return getScores().stream()
                .filter(grade::include)
                .mapToInt(Integer::intValue)
                .average()
                .orElse(0);
    }
}
```

</details>

```typescript
// TypeScript
class Grade {
    constructor(
        private name: string,
        private upper: number,
        private lower: number
    ) {}

    getName(): string { return this.name; }

    isName(name: string): boolean {
        return this.name === name;
    }

    include(score: number): boolean {
        return score >= this.lower && score <= this.upper;
    }
}

class GradeLecture extends Lecture {
    private grades: Grade[];

    constructor(name: string, pass: number, grades: Grade[],
                scores: number[]) {
        super(name, pass, scores);
        this.grades = grades;
    }

    // 메서드 오버라이딩: Lecture의 evaluate를 재정의
    evaluate(): string {
        return `${super.evaluate()}, ${this.gradesStatistics()}`;
    }

    private gradesStatistics(): string {
        return this.grades
            .map(grade => this.format(grade))
            .join(" ");
    }

    private format(grade: Grade): string {
        return `${grade.getName()}:${this.gradeCount(grade)}`;
    }

    private gradeCount(grade: Grade): number {
        return this.getScores()
            .filter(score => grade.include(score)).length;
    }

    // 메서드 오버로딩: Lecture의 average()와 이름만 같고 시그니처가 다름
    averageByGrade(gradeName: string): number {
        const grade = this.grades.find(g => g.isName(gradeName));
        if (!grade) return 0;
        return this.gradeAverage(grade);
    }

    private gradeAverage(grade: Grade): number {
        const filtered = this.getScores()
            .filter(score => grade.include(score));
        if (filtered.length === 0) return 0;
        return filtered.reduce((a, b) => a + b, 0) / filtered.length;
    }
}
```

`GradeLecture`의 `evaluate` 메서드에서는 예약어 `super`를 이용해 `Lecture` 클래스의 `evaluate` 메서드를 먼저 실행한다는 점에 주목하라.

여기서 주목할 부분은 **메서드 오버라이딩**과 **메서드 오버로딩**의 차이다.

| 구분 | 메서드 오버라이딩 | 메서드 오버로딩 |
|---|---|---|
| **시그니처** | 부모와 자식이 **동일** | 이름만 같고 **시그니처가 다름** |
| **관계** | 자식이 부모를 **감춤** (대체) | 부모와 자식이 **공존** |
| **예시** | `GradeLecture.evaluate()`가 `Lecture.evaluate()`를 감춤 | `GradeLecture.average(gradeName)`과 `Lecture.average()`가 공존 |

```typescript
const lecture = new GradeLecture(
    "객체지향 프로그래밍", 70,
    [new Grade("A", 100, 95), new Grade("B", 94, 80),
     new Grade("C", 79, 70), new Grade("D", 69, 50),
     new Grade("F", 49, 0)],
    [81, 95, 75, 50, 45]
);
lecture.evaluate(); // "Pass:3 Fail:2, A:1 B:1 C:1 D:1 F:1"
```

### 2.3 데이터 관점의 상속

`Lecture`의 인스턴스를 생성하면 시스템은 인스턴스 변수 `title`, `pass`, `scores`를 저장할 수 있는 메모리 공간을 할당한다.

```
lecture ──▶ ┌─────────────────────────────────────┐
            │ Lecture                              │
            │   title  = "객체지향 프로그래밍"       │
            │   pass   = 70                        │
            │   scores = [81, 95, 75, 50, 45]      │
            └─────────────────────────────────────┘
```

`GradeLecture`의 인스턴스를 생성하면, 자식 클래스의 인스턴스 안에 부모 클래스의 인스턴스가 **개념적으로 포함**된다.

```
lecture ──▶ ┌─────────────────────────────────────┐
            │ GradeLecture                        │
            │   grades = ["A","B","C","D","F"]     │
            │ ┌─────────────────────────────────┐ │
            │ │ Lecture                          │ │
            │ │   title  = "객체지향 프로그래밍"   │ │
            │ │   pass   = 70                    │ │
            │ │   scores = [81, 95, 75, 50, 45]  │ │
            │ └─────────────────────────────────┘ │
            └─────────────────────────────────────┘
```

> 데이터 관점에서 상속은 자식 클래스의 인스턴스 안에 부모 클래스의 인스턴스를 포함하는 것으로 볼 수 있다. 자식 클래스의 인스턴스는 자동으로 부모 클래스에서 정의한 모든 인스턴스 변수를 내부에 포함하게 되는 것이다.

### 2.4 행동 관점의 상속

행동 관점의 상속은 부모 클래스가 정의한 일부 메서드를 자식 클래스의 메서드로 포함시키는 것을 의미한다. 부모 클래스의 모든 퍼블릭 메서드는 자식 클래스의 퍼블릭 인터페이스에 포함된다. 따라서 외부의 객체가 부모 클래스의 인스턴스에게 전송할 수 있는 모든 메시지는 자식 클래스의 인스턴스에게도 전송할 수 있다.

실제로 클래스의 코드를 합치거나 복사하는 작업이 수행되는 것은 아니다. 런타임에 시스템이 자식 클래스에 정의되지 않은 메서드가 있을 경우, 이 메서드를 부모 클래스 안에서 탐색하기 때문에 가능한 것이다.

각 인스턴스는 자신의 클래스를 가리키는 `class` 포인터를 가지며, 각 클래스는 부모 클래스를 가리키는 `parent` 포인터를 가진다.

```
                              ┌───────────┐
                              │  Object   │
                              └─────▲─────┘
                                    │ parent
  oop ──▶ ┌──────────────┐    ┌─────┴─────────────────────┐
          │ :Lecture      │    │  Lecture                   │
          │ title="OOP"  ├──▶ │  average() getScores()    │
          │ pass=70      │class│  evaluate()               │
          └──────────────┘    └─────▲─────────────────────┘
                                    │ parent
  fp ──▶  ┌──────────────┐    ┌─────┴─────────────────────┐
          │ :GradeLecture├──▶ │  GradeLecture              │
          │ grades=[...]  │class│  average(gradeName)       │
          └──────────────┘    │  evaluate()                │
                              └────────────────────────────┘
```

메시지를 수신한 객체는 `class` 포인터로 연결된 자신의 클래스에서 적절한 메서드가 존재하는지를 찾는다. 만약 메서드가 존재하지 않으면 클래스의 `parent` 포인터를 따라 부모 클래스를 차례대로 훑어가면서 적절한 메서드가 존재하는지를 검색한다.

---

## 3. 업캐스팅과 동적 바인딩

### 3.1 같은 메시지, 다른 메서드

코드 안에서 선언된 참조 타입과 무관하게 **실제로 메시지를 수신하는 객체의 타입에 따라 실행되는 메서드가 달라질 수 있는** 것은 업캐스팅과 동적 바인딩이라는 메커니즘이 작용하기 때문이다.

교수별로 강의에 대한 성적 통계를 계산하는 `Professor` 클래스를 추가한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Professor {
    private String name;
    private Lecture lecture;

    public Professor(String name, Lecture lecture) {
        this.name = name;
        this.lecture = lecture;
    }

    public String compileStatistics() {
        return String.format("[%s] %s - Avg: %.1f",
                name, lecture.evaluate(), lecture.average());
    }
}
```

</details>

```typescript
// TypeScript
class Professor {
    constructor(
        private name: string,
        private lecture: Lecture   // Lecture 타입으로 선언
    ) {}

    compileStatistics(): string {
        return `[${this.name}] ${this.lecture.evaluate()} - Avg: ${this.lecture.average().toFixed(1)}`;
    }
}
```

`Lecture` 인스턴스를 전달하면:

```typescript
const professor = new Professor("다익스트라",
    new Lecture("알고리즘", 70, [81, 95, 75, 50, 45]));
professor.compileStatistics();
// "[다익스트라] Pass:3 Fail:2 - Avg: 69.2"
```

`GradeLecture` 인스턴스를 전달하면:

```typescript
const professor = new Professor("다익스트라",
    new GradeLecture("알고리즘", 70,
        [new Grade("A", 100, 95), new Grade("B", 94, 80),
         new Grade("C", 79, 70), new Grade("D", 69, 50),
         new Grade("F", 49, 0)],
        [81, 95, 75, 50, 45]));
professor.compileStatistics();
// "[다익스트라] Pass:3 Fail:2, A:1 B:1 C:1 D:1 F:1 - Avg: 69.2"
```

동일한 `compileStatistics` 코드가 서로 다른 `evaluate` 메서드를 실행하고 있다. 이것이 가능한 이유:

| 메커니즘 | 역할 |
|---|---|
| **업캐스팅** | 서로 다른 클래스의 인스턴스를 동일한 타입에 할당하는 것을 가능하게 해준다 |
| **동적 바인딩** | 부모 클래스의 타입에 대해 메시지를 전송하더라도 실행 시에는 실제 클래스를 기반으로 메서드가 선택되게 해준다 |

> 개방-폐쇄 원칙과의 관계: 업캐스팅과 동적 메서드 탐색은 코드를 변경하지 않고도 기능을 추가할 수 있게 해주며, 이것은 개방-폐쇄 원칙의 의도와도 일치한다. **개방-폐쇄 원칙이 목적이라면 업캐스팅과 동적 메서드 탐색은 목적에 이르는 방법이다.**

### 3.2 업캐스팅

상속을 이용하면 부모 클래스의 퍼블릭 인터페이스가 자식 클래스의 퍼블릭 인터페이스에 합쳐지기 때문에, 부모 클래스의 인스턴스 대신 자식 클래스의 인스턴스를 사용하더라도 메시지를 처리하는 데는 아무런 문제가 없다. 컴파일러는 명시적인 타입 변환 없이도 자식 클래스가 부모 클래스를 대체할 수 있게 허용한다.

업캐스팅을 활용할 수 있는 대표적인 두 가지: **대입문**과 **메서드의 파라미터 타입**이다.

```typescript
// 대입문에서의 업캐스팅
const lecture: Lecture = new GradeLecture(/* ... */);

// 메서드 파라미터에서의 업캐스팅
const professor = new Professor("다익스트라", new GradeLecture(/* ... */));
```

반대로 부모 클래스의 인스턴스를 자식 클래스 타입으로 변환하기 위해서는 명시적인 타입 캐스팅이 필요한데, 이를 **다운캐스팅**(*Downcasting*)이라고 부른다.

```
              ┌───────────┐
              │  Object   │
              └─────▲─────┘
                    │
              ┌─────┴─────┐
              │  Lecture   │
              │ average()  │
              │ evaluate() │
              └─────▲─────┘
           ▲        │        │
     업캐스팅│        │        │다운캐스팅
           │  ┌─────┴──────┐ ▼
              │GradeLecture│
              │ evaluate() │
              │ average(gn)│
              └────────────┘
```

컴파일러 관점에서 자식 클래스는 아무런 제약 없이 부모 클래스를 대체할 수 있기 때문에, 부모 클래스와 협력하는 클라이언트는 **현재 상속 계층에 존재하는 자식 클래스뿐만 아니라 앞으로 추가될 미래의 자식 클래스들과도 협력**할 수 있다. 따라서 이 설계는 유연하며 확장이 용이하다.

### 3.3 동적 바인딩

전통적인 언어에서 함수를 실행하는 방법은 함수를 **호출**하는 것이다. 객체지향 언어에서 메서드를 실행하는 방법은 메시지를 **전송**하는 것이다. 함수 호출과 메시지 전송 사이의 차이는 프로그램 안에 작성된 함수 호출 구문과 실제로 실행되는 코드를 연결하는 언어적인 메커니즘이 완전히 다르기 때문이다.

| 바인딩 방식 | 결정 시점 | 특징 |
|---|---|---|
| **정적 바인딩** (*Static Binding / Early Binding / Compile-time Binding*) | 컴파일타임 | 코드 작성 시점에 호출될 코드가 결정된다. 전통적 언어의 함수 호출 방식 |
| **동적 바인딩** (*Dynamic Binding / Late Binding*) | 런타임 | 메시지를 수신했을 때 실행될 메서드가 런타임에 결정된다. 객체지향 언어의 메시지 전송 방식 |

`foo.bar()`라는 코드를 읽는 것만으로는 실행되는 `bar`가 어떤 클래스의 어떤 메서드인지를 판단하기 어렵다. `foo`가 가리키는 객체가 실제로 어떤 클래스의 인스턴스인지를 알아야 하고, `bar` 메서드가 해당 클래스의 상속 계층의 어디에 위치하는지를 알아야 한다.

---

## 4. 동적 메서드 탐색과 다형성

객체지향 시스템은 다음 규칙에 따라 실행할 메서드를 선택한다.

1. 메시지를 수신한 객체는 먼저 **자신을 생성한 클래스**에 적합한 메서드가 존재하는지 검사한다. 존재하면 메서드를 실행하고 탐색을 종료한다.
2. 메서드를 찾지 못했다면 **부모 클래스**에서 메서드 탐색을 계속한다. 이 과정은 적합한 메서드를 찾을 때까지 상속 계층을 따라 올라가며 계속된다.
3. 상속 계층의 **가장 최상위 클래스**에 이르렀지만 메서드를 발견하지 못한 경우 예외를 발생시키며 탐색을 중단한다.

### 4.1 self 참조

메시지 탐색과 관련해서 이해해야 하는 중요한 변수가 하나 있다. **self 참조**(*Self Reference*)가 바로 그것이다. 객체가 메시지를 수신하면 컴파일러는 `self` 참조라는 임시 변수를 자동으로 생성한 후 메시지를 수신한 객체를 가리키도록 설정한다.

동적 메서드 탐색은 `self`가 가리키는 객체의 클래스에서 시작해서 상속 계층의 역방향으로 이뤄지며, 메서드 탐색이 종료되는 순간 `self` 참조는 자동으로 소멸된다.

> 정적 타입 언어인 C++, 자바, C#에서는 self 참조를 `this`라고 부른다. 동적 타입 언어인 스몰토크, 루비에서는 `self`라는 키워드를 사용한다. 파이썬에서는 self 참조의 이름을 임의로 정할 수 있지만 대부분의 개발자들은 전통을 존중해서 `self`라는 이름을 사용한다.

동적 메서드 탐색은 **두 가지 원리**로 구성된다.

| 원리 | 설명 |
|---|---|
| **자동적인 메시지 위임** | 자식 클래스는 자신이 이해할 수 없는 메시지를 전송받은 경우 상속 계층을 따라 부모 클래스에게 처리를 위임한다. 프로그래머의 개입 없이 자동으로 이뤄진다 |
| **동적인 문맥 사용** | 메시지를 수신했을 때 실제로 어떤 메서드를 실행할지를 결정하는 것은 실행 시점에 이뤄지며, 메서드를 탐색하는 경로는 self 참조를 이용해서 결정한다 |

### 4.2 메서드 오버라이딩의 탐색 과정

**Case 1: Lecture 인스턴스에 evaluate 메시지 전송**

```
self ──▶ :Lecture                      ┌───────────┐
                          class ──────▶│  Lecture   │
                                       │ evaluate() │ ◀── 여기서 발견! 실행
                                       └─────▲─────┘
                                             │ parent
                                       ┌─────┴─────┐
                                       │  Object   │
                                       └───────────┘
```

메서드 탐색은 self 참조가 가리키는 객체의 클래스인 `Lecture`에서 시작한다. `Lecture` 클래스 안에 `evaluate` 메서드가 존재하기 때문에 시스템은 메서드를 실행한 후 탐색을 종료한다.

**Case 2: GradeLecture 인스턴스에 evaluate 메시지 전송**

```
self ──▶ :GradeLecture                 ┌───────────┐
                          class ──────▶│GradeLecture│
                                       │ evaluate() │ ◀── 여기서 발견! 실행
                                       └─────▲─────┘
                                             │ parent
                                       ┌─────┴─────┐
                                       │  Lecture   │
                                       │ evaluate() │ ◀── 감춰짐 (오버라이딩)
                                       └───────────┘
```

동적 메서드 탐색은 self 참조가 가리키는 객체의 클래스인 `GradeLecture`에서 시작되고, `GradeLecture` 클래스 안에 `evaluate` 메서드가 구현되어 있기 때문에 먼저 발견된 메서드가 실행된다. 자식 클래스의 메서드가 부모 클래스의 메서드를 **감추게** 된다.

### 4.3 메서드 오버로딩의 탐색 과정

**Case 3: GradeLecture 인스턴스에 average("A") 메시지 전송**

```
self ──▶ :GradeLecture                 ┌────────────────┐
                          class ──────▶│ GradeLecture    │
                                       │ average(grade)  │ ◀── 여기서 발견! 실행
                                       └──────▲─────────┘
                                              │ parent
                                       ┌──────┴─────────┐
                                       │ Lecture         │
                                       │ average()      │
                                       └────────────────┘
```

**Case 4: GradeLecture 인스턴스에 average() 메시지 전송**

```
self ──▶ :GradeLecture                 ┌────────────────┐
                          class ──────▶│ GradeLecture    │
                                       │ average(grade)  │    시그니처 불일치, 패스
                                       └──────▲─────────┘
                                              │ parent
                                       ┌──────┴─────────┐
                                       │ Lecture         │
                                       │ average()      │ ◀── 여기서 발견! 실행
                                       └────────────────┘
```

메서드 오버라이딩은 메서드를 감추지만, 메서드 오버로딩은 **사이좋게 공존**한다. 클라이언트의 관점에서 오버로딩된 모든 메서드를 호출할 수 있다.

> 대부분의 사람들은 하나의 클래스 안에서 같은 이름을 가진 메서드들을 정의하는 것은 메서드 오버로딩으로 생각하고, 상속 계층 사이에서 같은 이름을 가진 메서드를 정의하는 것은 메서드 오버로딩으로 생각하지 않는 경향이 있다. 이것은 C++처럼 상속 계층 사이의 메서드 오버로딩을 지원하지 않는 언어가 있기 때문이다. C++에서는 부모 클래스에 선언된 이름이 동일한 메서드 전체를 숨겨서 클라이언트가 호출하지 못하도록 막는데, 이를 **이름 숨기기**(*Name Hiding*)라고 부른다. 자바는 상속 계층 사이의 메서드 오버로딩을 허용한다.

### 4.4 동적인 문맥과 self 전송

`lecture.evaluate()`라는 메시지 전송 코드만으로는 어떤 클래스의 어떤 메서드가 실행될지를 알 수 없다. 메시지를 수신한 객체가 무엇이냐에 따라 메서드 탐색을 위한 문맥이 **동적으로** 바뀐다. 이 동적인 문맥을 결정하는 것이 바로 **self 참조**다.

self 참조가 동적 문맥을 결정한다는 사실은 종종 어떤 메서드가 실행될지를 예상하기 어렵게 만든다. 대표적인 경우가 자신에게 다시 메시지를 전송하는 **self 전송**(*Self Send*)이다.

`Lecture`와 `GradeLecture` 클래스에 평가 기준에 대한 정보를 반환하는 `stats` 메서드를 추가한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class Lecture {
    public String stats() {
        return String.format("Title: %s, Evaluation Method: %s",
                title, getEvaluationMethod());
    }

    public String getEvaluationMethod() {
        return "Pass or Fail";
    }
}

public class GradeLecture extends Lecture {
    @Override
    public String getEvaluationMethod() {
        return "Grade";
    }
}
```

</details>

```typescript
// TypeScript
class Lecture {
    stats(): string {
        return `Title: ${this.title}, Evaluation Method: ${this.getEvaluationMethod()}`;
    }

    getEvaluationMethod(): string {
        return "Pass or Fail";
    }
}

class GradeLecture extends Lecture {
    getEvaluationMethod(): string {
        return "Grade";
    }
}
```

`Lecture` 클래스의 `stats` 메서드 안에서 `getEvaluationMethod()`라는 구문은 **현재 클래스의 메서드를 호출하는 것이 아니라 현재 객체에게 `getEvaluationMethod` 메시지를 전송하는 것**이다. 현재 객체란 바로 self 참조가 가리키는 객체다.

**Lecture 인스턴스의 self 전송:**

```
                                  ┌────────────────────┐
                                  │  Object            │
                                  └────────▲───────────┘
                                           │ parent
         ① stats() 메시지                  │
self ──▶ :Lecture ──class──▶ ┌─────────────┴───────────────┐
                              │  Lecture                    │
                              │  stats()                   │
                              │  getEvaluationMethod() ◀───┤
                              └────────────────────────────┘
                                   │                  ▲
                                   │ ② self 전송      │
                                   └──────────────────┘
```

self 참조가 `Lecture` 인스턴스를 가리키므로, `getEvaluationMethod` 메시지 탐색은 `Lecture` 클래스에서 시작되고 `Lecture`의 `getEvaluationMethod` 메서드가 실행된다.

**GradeLecture 인스턴스의 self 전송:**

```
         ① stats() 메시지            ┌───────────────────────────┐
self ──▶ :GradeLecture ──class──▶   │  GradeLecture              │
                                     │  getEvaluationMethod()    │ ◀── ④ 여기서 발견!
                                     └───────────▲──────────────┘
                                                  │ parent
                                     ┌────────────┴──────────────┐
                                     │  Lecture                   │
                                     │  stats()  ◀── ② 여기서 발견│
                                     │  getEvaluationMethod()     │
                                     └────────────────────────────┘
                                          │                  ▲
                                          │ ③ self 전송      │
                                          └─── self 참조가 가리키는
                                               GradeLecture로 되돌아감
```

`GradeLecture`에 `stats` 메시지를 전송하면, self 참조는 `GradeLecture`의 인스턴스를 가리키도록 설정되고 메서드 탐색은 `GradeLecture` 클래스에서부터 시작된다. `GradeLecture` 클래스에는 `stats` 메시지를 처리할 수 있는 메서드가 없기 때문에 부모 클래스인 `Lecture`에서 메서드 탐색을 계속하고 `Lecture` 클래스의 `stats` 메서드를 발견하여 실행한다.

`Lecture` 클래스의 `stats` 메서드를 실행하는 중에 self 참조가 가리키는 객체에게 `getEvaluationMethod` 메시지를 전송하는 구문과 마주치게 된다. 여기서 self 참조가 가리키는 객체는 바로 `GradeLecture`의 인스턴스다. 따라서 메시지 탐색은 **`Lecture` 클래스를 벗어나 self 참조가 가리키는 `GradeLecture`에서부터 다시 시작**된다.

시스템은 `GradeLecture` 클래스에서 `getEvaluationMethod` 메서드를 발견하고 실행한 후 동적 메서드 탐색을 종료한다. 그 결과 `Lecture` 클래스의 `stats` 메서드와 `GradeLecture` 클래스의 `getEvaluationMethod` 메서드의 실행 결과를 조합한 문자열이 반환된다.

> **핵심 통찰**: self 전송은 자식 클래스에서 부모 클래스 방향으로 진행되는 동적 메서드 탐색 경로를 다시 **self 참조가 가리키는 원래의 자식 클래스로 이동시킨다**. 이로 인해 최악의 경우에는 실제로 실행될 메서드를 이해하기 위해 상속 계층 전체를 훑어가며 코드를 이해해야 하는 상황이 발생할 수도 있다. self 전송이 깊은 상속 계층과 계층 중간중간에 함정처럼 숨겨져 있는 메서드 오버라이딩과 만나면 극단적으로 이해하기 어려운 코드가 만들어진다.

### 4.5 이해할 수 없는 메시지

상속 계층의 최상위 클래스에 이르렀지만 메서드를 발견하지 못했다면, 그 처리 방식은 프로그래밍 언어가 정적 타입 언어인지 동적 타입 언어인지에 따라 달라진다.

| 언어 유형 | 처리 방식 | 특징 |
|---|---|---|
| **정적 타입 언어** (Java, C++, C#, TypeScript) | 컴파일타임에 상속 계층 전체를 탐색한 후 메서드를 발견하지 못하면 **컴파일 에러** 발생 | 실행 전에 오류를 잡아냄, 안정적 |
| **동적 타입 언어** (Smalltalk, Ruby, Python) | 런타임에 최상위 클래스까지 탐색한 후에도 메서드를 찾지 못하면 self 참조에게 "이해할 수 없는 메시지" 메시지를 전송 | `doesNotUnderstand` (Smalltalk), `method_missing` (Ruby) |

```
         ① unknownMessage()
self ──▶ :GradeLecture ──class──▶ GradeLecture ─── 없음
                                     │ parent
                                  Lecture ────── 없음
                                     │ parent
         ⑥ self.method_missing()  Object ─────── 없음 → ④ method_missing 전송
         ⑦ → NoMethodError        ▲
                                  │ ⑤ method_missing 탐색
                                  └──────────────
```

동적 타입 언어에서는 `doesNotUnderstand`/`method_missing` 메시지에 응답할 수 있는 메서드를 구현하면, 객체는 자신의 인터페이스에 정의되지 않은 메시지를 처리하는 것이 가능해진다. 이를 통해 메타프로그래밍 영역에서 강력한 도메인-특화 언어(*Domain-Specific Language, DSL*)를 개발할 수 있으며, 마틴 파울러는 이러한 특징을 이용해 도메인-특화 언어를 개발하는 방식을 **동적 리셉션**(*Dynamic Reception*)이라고 부른다.

> 동적 타입 언어는 이해할 수 없는 메시지를 처리할 수 있는 능력을 가짐으로써 메시지가 선언된 인터페이스와 메서드가 정의된 구현을 분리할 수 있다. 이것은 메시지를 기반으로 협력하는 자율적인 객체라는 순수한 객체지향의 이상에 좀 더 가까운 것이다. 그러나 이러한 동적인 특성과 유연성은 코드를 이해하고 수정하기 어렵게 만들 뿐만 아니라 디버깅 과정을 복잡하게 만들기도 한다.

---

## 5. self 참조와 super 참조

### 5.1 self 참조의 특성

self 참조의 가장 큰 특징은 **동적**이라는 점이다. self 참조는 메시지를 수신한 객체의 클래스에 따라 메서드 탐색을 위한 문맥을 실행 시점에 결정한다.

- self 참조가 `Lecture`의 인스턴스를 가리키면 → 메서드 탐색 문맥은 `Lecture` → `Object`
- self 참조가 `GradeLecture`의 인스턴스를 가리키면 → 메서드 탐색 문맥은 `GradeLecture` → `Lecture` → `Object`

동일한 코드라고 하더라도 self 참조가 가리키는 객체가 무엇인지에 따라 메서드 탐색을 위한 상속 계층의 범위가 **동적으로** 변한다.

### 5.2 super 참조

자식 클래스에서 부모 클래스의 구현을 재사용해야 하는 경우 **super 참조**(*Super Reference*)를 사용한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class GradeLecture extends Lecture {
    @Override
    public String evaluate() {
        return super.evaluate() + ", " + gradesStatistics();
    }
}
```

</details>

```typescript
// TypeScript
class GradeLecture extends Lecture {
    evaluate(): string {
        return `${super.evaluate()}, ${this.gradesStatistics()}`;
    }
}
```

대부분의 사람들은 `super.evaluate()`라는 문장이 단순히 부모 클래스의 `evaluate` 메서드를 호출한다고 생각할 것이다. 하지만 `super.evaluate()`에 의해 호출되는 메서드는 **부모 클래스의 메서드가 아니라 더 상위에 위치한 조상 클래스의 메서드일 수도 있다**.

이해를 돕기 위해 `GradeLecture`의 자식 클래스인 `FormattedGradeLecture` 클래스에 `super.average()` 문장을 추가한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public class FormattedGradeLecture extends GradeLecture {
    public FormattedGradeLecture(String name, int pass,
            List<Grade> grades, List<Integer> scores) {
        super(name, pass, grades, scores);
    }

    public String formatAverage() {
        return String.format("Avg: %1.1f", super.average());
    }
}
```

</details>

```typescript
// TypeScript
class FormattedGradeLecture extends GradeLecture {
    formatAverage(): string {
        return `Avg: ${super.average().toFixed(1)}`;
    }
}
```

super가 부모 클래스의 메서드를 호출하는 것이라면, `super.average()`는 정상적으로 실행될 수 없을 것이다. 부모 클래스인 `GradeLecture`에는 파라미터 없는 `average` 메서드가 정의되어 있지 않기 때문이다. 하지만 이 코드는 정상적으로 실행되며, `super.average()`에 의해 실행되는 메서드는 `GradeLecture`의 부모 클래스인 `Lecture`의 `average` 메서드다.

```
              ┌─────────────┐
              │   Object    │
              └──────▲──────┘
                     │ parent
              ┌──────┴───────────────────┐
              │   Lecture                 │
     super ──▶│   average()  ◀── 여기서 발견! │
              │   evaluate()             │
              └──────▲───────────────────┘
                     │ parent
              ┌──────┴───────────────────┐
              │   GradeLecture           │
              │   average(gradeName)     │   ← 시그니처 불일치, 패스
              │   evaluate()             │
              └──────▲───────────────────┘
                     │ parent
              ┌──────┴───────────────────┐
self ────────▶│ FormattedGradeLecture    │
              │   formatAverage()        │   super.average() 호출
              └──────────────────────────┘
```

> **핵심 통찰**: super 참조의 정확한 의도는 "부모 클래스의 메서드를 호출하라"가 아니라 **"지금 이 클래스의 부모 클래스에서부터 메서드 탐색을 시작하세요"**다. 만약 부모 클래스에서 원하는 메서드를 찾지 못한다면 더 상위의 부모 클래스로 이동하면서 메서드가 존재하는지 검사한다. 부모 클래스의 메서드를 호출하는 것과 부모 클래스에서 메서드 탐색을 시작하는 것은 의미가 매우 다르다.

이처럼 super 참조를 통해 메시지를 전송하는 것은 마치 부모 클래스의 인스턴스에게 메시지를 전송하는 것처럼 보이기 때문에 이를 **super 전송**(*Super Send*)이라고 부른다.

### 5.3 self 전송 vs super 전송

| 구분 | self 전송 | super 전송 |
|---|---|---|
| **탐색 시작 위치** | self 참조가 가리키는 객체의 클래스 (동적) | 메시지를 전송하는 클래스의 **부모 클래스** (정적) |
| **결정 시점** | **런타임** — 어떤 클래스에서 탐색이 시작될지 알 수 없음 | **컴파일타임** — 항상 해당 클래스의 부모 클래스에서 시작됨 |
| **예측 가능성** | 낮음: `Lecture`일 수도, `GradeLecture`일 수도, 미래의 자식 클래스일 수도 있음 | 높음: 항상 미리 정해진 클래스에서 시작 |

> super 전송과 동적 바인딩: 상속에서 super가 컴파일 시점에 미리 결정된다고 설명했지만 super를 런타임에 결정하는 경우도 있다. 11장에서 믹스인을 설명하면서 예로 들었던 스칼라의 트레이트는 super의 대상을 믹스인되는 순서에 따라 동적으로 결정한다. 대부분의 객체지향 언어에서 상속을 사용하는 경우에는 super가 컴파일타임에 결정된다.

동적 바인딩, self 참조, super 참조는 상속을 이용해 **다형성을 구현하고 코드를 재사용하기 위한 가장 핵심적인 재료**다. 동적 바인딩과 self 참조는 동일한 메시지를 수신하더라도 객체의 타입에 따라 적합한 메서드를 동적으로 선택할 수 있게 한다. super 참조는 부모 클래스의 코드에 접근할 수 있게 함으로써 중복 코드를 제거할 수 있게 한다.

---

## 6. 상속 대 위임

### 6.1 위임과 self 참조

다형성은 self 참조가 가리키는 현재 객체에게 메시지를 전달하는 특성을 기반으로 한다. 자식 클래스의 인스턴스를 생성할 경우, 개념적으로 자식 클래스의 인스턴스 안에 부모 클래스의 인스턴스를 포함하는 것으로 표현할 수 있다.

핵심적인 질문: GradeLecture 인스턴스에 포함된 Lecture 인스턴스의 입장에서 self 참조는 무엇을 가리킬까?

**GradeLecture의 인스턴스다.** self 참조는 항상 메시지를 수신한 객체를 가리키기 때문이다. 따라서 메서드 탐색 중에는 자식 클래스의 인스턴스와 부모 클래스의 인스턴스가 **동일한 self 참조를 공유**하는 것으로 봐도 무방하다.

```
       ┌────────────────────────────────────────────┐
       │                                            │
       │  self ──▶ :GradeLecture                    │
       │              │                              │
       │              │ @parent (링크)                │
       │              ▼                              │
       │          self ──▶ :Lecture  ◀── 동일한 self  │
       │                                            │
       └────────────────────────────────────────────┘
```

### 6.2 상속 없이 위임 구현하기 (루비 예제)

개념을 좀 더 쉽게 설명하기 위해 `GradeLecture`에서 `Lecture`로 self 참조가 공유되는 과정을 상속을 사용하지 않고 직접 코드로 구현해 본다.

```ruby
# Ruby — Lecture
class Lecture
  def initialize(name, scores)
    @name = name
    @scores = scores
  end

  def stats(this)   # self 참조를 인자로 전달받음
    "Name: #{@name}, Evaluation Method: #{this.getEvaluationMethod()}"
  end

  def getEvaluationMethod()
    "Pass or Fail"
  end
end
```

```ruby
# Ruby — GradeLecture (상속 없이 위임으로 구현)
class GradeLecture
  def initialize(name, canceled, scores)
    @parent = Lecture.new(name, scores)   # 부모 인스턴스를 링크로 보관
    @canceled = canceled
  end

  def stats(this)
    @parent.stats(this)   # self 참조를 그대로 전달 (위임)
  end

  def getEvaluationMethod()
    "Grade"
  end
end
```

이 코드에서 중요한 네 가지 포인트:

1. **@parent 링크**: `GradeLecture`는 인스턴스 변수 `@parent`에 `Lecture`의 인스턴스를 생성해서 저장한다. 이 링크를 통해 동적 메서드 탐색 메커니즘을 직접 구현한다.
2. **요청 전달**: `GradeLecture`의 `stats` 메서드는 `@parent`에게 요청을 그대로 전달한다. 자식 클래스에 메서드가 존재하지 않을 경우 부모 클래스에서 메서드 탐색을 계속하는 과정을 흉내 낸 것이다.
3. **메서드 오버라이딩**: `GradeLecture`의 `getEvaluationMethod`는 `@parent`에 전달하지 않고 자신만의 방법으로 구현하고 있다. 상속에서의 메서드 오버라이딩과 동일하다.
4. **self 참조 전달**: `GradeLecture`의 `stats` 메서드는 인자로 전달된 `this`를 그대로 `Lecture`의 `stats` 메서드에 전달한다. `Lecture`의 `stats` 메서드는 인자로 전달된 `this`에게 `getEvaluationMethod` 메시지를 전송하기 때문에, `Lecture`의 `getEvaluationMethod` 메서드가 아니라 `GradeLecture`의 `getEvaluationMethod` 메서드가 실행된다.

```ruby
grade_lecture = GradeLecture.new("OOP", false, [1, 2, 3])
grade_lecture.stats(grade_lecture)  # self 참조를 명시적으로 전달
```

자신이 수신한 메시지를 다른 객체에게 동일하게 전달해서 처리를 요청하는 것을 **위임**(*Delegation*)이라고 부른다. 위임은 본질적으로 자신이 정의하지 않거나 처리할 수 없는 속성 또는 메서드의 탐색 과정을 다른 객체로 이동시키기 위해 사용한다. 이를 위해 위임은 항상 **현재의 실행 문맥을 가리키는 self 참조를 인자로 전달**한다.

> self 참조를 전달하지 않는 포워딩과 위임의 차이에 주의하라. **포워딩**(*Forwarding*)은 요청을 전달받은 최초의 객체에 다시 메시지를 전송할 필요 없이 단순히 코드를 재사용하고 싶은 경우다. 처리를 요청할 때 self 참조를 전달하지 않는다. **위임**은 self 참조를 전달하여 다형성을 구현하는 것이다. 위임의 정확한 용도는 클래스를 이용한 상속 관계를 **객체 사이의 합성 관계로 대체**해서 다형성을 구현하는 것이다.

상속이 매력적인 이유는 이런 번잡한 과정을 자동으로 처리해 준다는 점이다. 간단히 `GradeLecture`를 `Lecture`의 자식 클래스로 선언하면, 실행 시에 인스턴스들 사이에서 self 참조가 자동으로 전달된다. 이 self 참조의 전달은 결과적으로 자식 클래스의 인스턴스와 부모 클래스의 인스턴스 사이에 동일한 실행 문맥을 공유할 수 있게 해준다. 따라서 상속 관계로 연결된 클래스 사이에는 **자동적인 메시지 위임**이 일어난다고 말하는 것이다.

### 6.3 프로토타입 기반의 객체지향 언어

클래스가 존재하지 않고 오직 객체만 존재하는 **프로토타입 기반의 객체지향 언어**에서 상속을 구현하는 유일한 방법은 **객체 사이의 위임**을 이용하는 것이다. 클래스 기반의 언어들이 상속을 이용해 클래스 사이에 self 참조를 자동으로 전달하는 것처럼, 프로토타입 기반의 언어들 역시 위임을 이용해 객체 사이에 self 참조를 자동으로 전달한다.

자바스크립트에서는 모든 객체들이 다른 객체를 가리키는 `prototype`이라는 이름의 링크를 가진다. 인스턴스는 메시지를 수신하면 먼저 메시지를 수신한 객체의 `prototype` 안에서 적절한 메서드가 존재하는지 검사한다. 메서드가 존재하지 않는다면 `prototype`이 가리키는 객체를 따라 메시지 처리를 자동적으로 위임한다.

```javascript
// JavaScript (고전적 방식)
function Lecture(name, scores) {
    this.name = name;
    this.scores = scores;
}

Lecture.prototype.stats = function() {
    return "Name: " + this.name +
           ", Evaluation Method: " + this.getEvaluationMethod();
};

Lecture.prototype.getEvaluationMethod = function() {
    return "Pass or Fail";
};

function GradeLecture(name, canceled, scores) {
    Lecture.call(this, name, scores);
    this.canceled = canceled;
}

GradeLecture.prototype = new Lecture();
GradeLecture.prototype.constructor = GradeLecture;

GradeLecture.prototype.getEvaluationMethod = function() {
    return "Grade";
};
```

```javascript
var gradeLecture = new GradeLecture("OOP", false, [1, 2, 3]);
gradeLecture.stats();
// "Name: OOP, Evaluation Method: Grade"
```

메시지를 수신한 인스턴스는 먼저 `GradeLecture`에 `stats` 메서드가 존재하는지 검사한다. 존재하지 않기 때문에 `prototype`을 따라 `Lecture`의 인스턴스에 접근한 후 `stats` 메서드를 발견하고 실행한다. 실행 도중 `this.getEvaluationMethod()` 문장을 발견하면, self 참조가 가리키는 현재 객체에서부터 다시 메서드 탐색을 시작한다. `GradeLecture`의 `getEvaluationMethod`를 발견하고 실행한다.

```
                   this.getEvaluationMethod()
                          │
                  ┌───────┘
                  ▼
prototype ──▶ ┌──────────────────────────────────┐
              │  Lecture (prototype 객체)          │
              │    stats = function() { ... }     │
              │    getEvaluationMethod = func...  │
              └──────────────────▲────────────────┘
                                │ prototype
              ┌─────────────────┴────────────────┐
              │  GradeLecture (prototype 객체)     │
              │    getEvaluationMethod = func...  │ ◀── 여기서 발견!
              └──────────────────▲────────────────┘
                                │ prototype
              ┌─────────────────┴────────────────┐
self ────────▶│  인스턴스                          │
              │    name = "OOP"                   │
              │    canceled = false               │
              │    scores = [1, 2, 3]             │
              └──────────────────────────────────┘
```

클래스 기반 언어에서의 상속과 동일하게, 객체 사이에 self 참조가 전달된다. `Lecture`의 `stats` 메서드 안의 `this`는 `Lecture`의 인스턴스가 아니라 **메시지를 수신한 현재 객체**를 가리킨다.

> **핵심 통찰**: 자바스크립트의 `prototype` 체인은 객체지향 패러다임에서 **클래스가 필수 요소가 아니라는 점**을 잘 보여준다. 또한 상속 이외의 방법(위임)으로도 다형성을 구현할 수 있다는 사실 역시 잘 보여준다. 클래스 기반 언어에서의 상속은 결국 self 참조를 자동으로 전달하는 위임의 특수한 형태인 것이다.

---

## 설계 원칙

| 원칙 | 설명 |
|---|---|
| **상속의 목적은 서브타입 계층 구축** | 상속은 코드 재사용이 아니라 다형성을 위한 타입 계층을 구조화하기 위해 사용해야 한다 |
| **업캐스팅을 통한 확장성** | 부모 클래스 타입으로 선언된 변수에 자식 클래스의 인스턴스를 할당할 수 있어, 미래의 자식 클래스와도 협력할 수 있다 |
| **동적 바인딩을 통한 유연성** | 컴파일타임이 아닌 런타임에 메서드가 결정되므로 코드를 변경하지 않고도 행동을 변경할 수 있다 |
| **self 참조의 동적 문맥** | self 참조가 가리키는 객체에 따라 메서드 탐색 경로가 동적으로 변하며, 이것이 다형성의 기반이다 |
| **super 참조의 정적 문맥** | super 전송은 항상 해당 클래스의 부모 클래스에서부터 탐색을 시작하므로, 코드 재사용을 위한 안정적인 메커니즘을 제공한다 |
| **상속은 자동적인 위임** | 상속 관계에서 self 참조가 자동으로 전달되는 것은 객체 사이의 위임을 자동화한 것이다 |

---

## 요약

- **다형성의 분류**: 다형성은 유니버설(매개변수, 포함)과 임시(오버로딩, 강제)로 분류된다. 특별한 언급 없이 '다형성'이라고 하면 포함(서브타입) 다형성을 의미한다.
- **상속의 양면성**: 상속은 데이터 관점(자식 인스턴스 안에 부모 인스턴스 포함)과 행동 관점(부모의 퍼블릭 메서드가 자식의 인터페이스에 합쳐짐) 두 가지로 이해해야 한다.
- **업캐스팅**: 부모 클래스 타입의 변수에 자식 클래스의 인스턴스를 할당하는 것으로, 명시적 타입 변환이 필요 없다.
- **동적 바인딩**: 메시지를 수신했을 때 실행될 메서드가 컴파일타임이 아닌 런타임에 결정되는 것이다.
- **동적 메서드 탐색**: self 참조가 가리키는 객체의 클래스에서 시작하여 상속 계층을 따라 부모 클래스 방향으로 메서드를 탐색한다.
- **self 참조**: 메시지를 수신한 객체를 가리키는 임시 변수로, 메서드 탐색의 동적 문맥을 결정한다. self 전송은 탐색 경로를 다시 원래의 자식 클래스로 되돌린다.
- **super 참조**: "부모 클래스에서부터 메서드 탐색을 시작하라"는 의미다. 부모 클래스의 메서드를 호출하는 것과는 다르며, 조상 클래스 어딘가에 메서드가 있기만 하면 실행할 수 있다.
- **메서드 오버라이딩 vs 오버로딩**: 오버라이딩은 동일한 시그니처의 메서드를 감추고, 오버로딩은 시그니처가 다른 메서드들이 공존하게 한다.
- **상속과 위임**: 상속은 self 참조를 자동으로 전달하는 자동적인 위임이다. 프로토타입 기반 언어에서는 객체 사이의 위임을 통해 상속을 구현한다.
- **클래스는 필수가 아니다**: 자바스크립트의 prototype 체인이 보여주듯, 클래스 없이 객체 사이의 위임만으로도 다형성을 구현할 수 있다.

---

## 다른 챕터와의 관계

- **Chapter 10 (상속과 코드 재사용)**: 코드 재사용을 위한 상속의 문제점을 다룬 10장과 달리, 이 장에서는 상속의 진정한 목적이 코드 재사용이 아니라 **다형성을 위한 타입 계층 구축**에 있음을 메커니즘 차원에서 규명한다.
- **Chapter 11 (합성과 유연한 설계)**: 합성을 통한 코드 재사용을 다룬 11장의 믹스인 개념이 이 장의 자동적인 메시지 위임, super 참조의 동적 결정과 직접 연결된다. 상속과 합성의 관계를 위임의 관점에서 통합적으로 이해할 수 있다.
- **Chapter 9 (유연한 설계)**: 개방-폐쇄 원칙의 기술적 기반이 업캐스팅과 동적 바인딩임을 이 장에서 명시적으로 밝히고 있다. 9장에서 원칙의 관점에서 설명한 것을 이 장에서는 내부 메커니즘으로 보완한다.
- **Chapter 13 (서브클래싱과 서브타이핑)**: 이 장에서 도입한 포함 다형성과 서브타입 계층의 개념을 이어받아, 올바른 타입 계층을 구성하기 위한 규칙과 원칙(리스코프 치환 원칙 등)을 다룬다.
- **Chapter 1 (객체, 설계)**: 1장에서 직관적으로 보여준 "동일한 메시지, 다른 행동" 패턴의 기술적 기반이 이 장에서 설명하는 동적 메서드 탐색과 다형성 메커니즘이다.
