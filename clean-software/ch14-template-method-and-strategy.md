# Chapter 14: Template Method and Strategy: Inheritance and Delegation (템플릿 메소드와 스트래터지: 상속과 위임)

## 핵심 질문

일반적인 알고리즘과 구체적인 구현을 어떻게 분리해야 하는가? 같은 문제를 푸는 **템플릿 메소드(Template Method)**와 **스트래터지(Strategy)** 패턴 중 무엇을 언제 선택해야 하는가? 상속과 위임 — 둘 사이의 trade-off는 무엇인가? 그리고 — 디자인 패턴이 존재한다는 사실 자체가 항상 그 패턴을 사용해야 한다는 뜻인가?

> 인생에서의 최고의 전략은 근면이다.<br>— 중국 속담

---

## 1. 상속에 대한 환상에서 깨어나기

### 1.1 90년대 초반의 상속 열풍

객체지향 프로그래밍 여명기에 우리는 모두 **상속(*inheritance - 기존 클래스의 속성과 동작을 물려받아 새 클래스를 정의하는 메커니즘*)**이라는 개념에 사로잡혀 있었다. 이 관계의 의미는 심오해 보였다:

- **차이에 의한 프로그래밍(*program by difference - 기존 클래스를 상속받아 다른 부분만 수정하여 새 클래스를 만드는 기법*)**이 가능하다
- 유용한 일을 하는 클래스가 이미 있다면, 그 서브클래스를 만들고 마음에 들지 않는 일부분만 수정하면 된다
- 단지 클래스를 상속하는 것만으로 코드를 재사용할 수 있다
- 각 단계가 그 위 단계의 코드를 재사용하는 분류 체계를 만들 수도 있다

### 1.2 비현실적인 몽상이었음이 드러나다

1995년에 이르러 상속이 너무 지나치게 사용되었고, 이런 과도한 사용은 비싼 대가를 치른다는 사실이 명백해졌다. GoF는 다음과 같이 강조했다:

> **클래스 상속보다는 차라리 복합(composition)이 더 낫다.**<br>— Gamma, Helm, Johnson, Vlissides, 『Design Patterns』(1995), p. 20

> **핵심 통찰**: 상속은 너무나 강력하지만, 동시에 너무나 결합도가 높다. 코드를 재사용하기 위해 상속을 사용하는 순간, 파생 클래스의 운명은 영원히 기반 클래스에 묶이게 된다. 같은 재사용 문제를 풀더라도 **위임(*delegation - 객체가 다른 객체에게 일을 시킴*)**을 사용하면 결합도를 훨씬 낮출 수 있다.

### 1.3 두 패턴의 위치

이번 장에서 다루는 두 패턴은 같은 문제 — **일반적인 알고리즘과 구체적인 구현의 분리** — 를 풀지만 방식이 다르다:

| 패턴 | 메커니즘 |
|------|----------|
| **템플릿 메소드 (Template Method)** | 상속을 사용 — 추상 기반 클래스가 알고리즘 골격을 갖고, 서브클래스가 변경 단계를 채움 |
| **스트래터지 (Strategy)** | 위임을 사용 — 알고리즘 객체가 인터페이스를 통해 구체적인 단계 객체에 위임 |

두 패턴 모두 **의존관계 역전 원칙(*DIP - Dependency Inversion Principle*)**을 만족시키려 한다. 일반적인 알고리즘이 구체적 구현에 의존하지 않고, 양쪽 모두 추상화에 의존하도록 만든다.

---

## 2. 템플릿 메소드 패턴

### 2.1 메인 루프 문제

지금까지 작성한 거의 모든 프로그램은 다음과 같은 메인 루프 구조를 가진다:

```
Initialize();
while (!done()) {  // 메인 루프
    Idle();         // 뭔가 유용한 일을 한다
}
Cleanup();
```

이 구조는 너무 평범하므로 `Application`이라는 추상 기반 클래스에 집어넣고 재사용할 수 있다.

### 2.2 시작점 — 초기 버전 ftoc

화씨를 섭씨로 변환하는 단순한 프로그램부터 보자. 표준적인 프로그램의 모든 구성요소(초기화, 메인 루프, 정리)가 들어있다.

<details>
<summary>원문 Java 코드 (목록 14-1)</summary>

```java
// Java - 목록 14-1: ftocRaw.java
import java.io.BufferedReader;
import java.io.InputStreamReader;

public class ftocRaw {
    public static void main(String[] args) throws Exception {
        InputStreamReader isr = new InputStreamReader(System.in);
        BufferedReader br = new BufferedReader(isr);
        boolean done = false;
        while (!done) {
            String fahrString = br.readLine();
            if (fahrString == null || fahrString.length() == 0) {
                done = true;
            } else {
                double fahr = Double.parseDouble(fahrString);
                double celcius = 5.0 / 9.0 * (fahr - 32);
                System.out.println("F=" + fahr + ", C=" + celcius);
            }
        }
        System.out.println("ftoc exit");
    }
}
```

</details>

```typescript
// TypeScript - 초기 버전
import * as readline from "readline";

async function ftocRaw(): Promise<void> {
  const rl = readline.createInterface({ input: process.stdin });
  for await (const fahrString of rl) {
    if (!fahrString) {
      break;
    }
    const fahr = Number.parseFloat(fahrString);
    const celcius = (5.0 / 9.0) * (fahr - 32);
    console.log(`F=${fahr}, C=${celcius}`);
  }
  console.log("ftoc exit");
}
```

### 2.3 Application 추상 기반 클래스

템플릿 메소드 패턴을 적용하면 일반적인 알고리즘(메인 루프 구조)을 추상 기반 클래스의 메소드 하나에 집어넣을 수 있다. 구체적인 부분은 모두 추상 메소드에 맡긴다.

<details>
<summary>원문 Java 코드 (목록 14-2)</summary>

```java
// Java - 목록 14-2: Application.java
public abstract class Application {
    private boolean isDone = false;

    protected abstract void init();
    protected abstract void idle();
    protected abstract void cleanup();

    protected void setDone() {
        isDone = true;
    }

    protected boolean done() {
        return isDone;
    }

    public void run() {
        init();
        while (!done()) {
            idle();
        }
        cleanup();
    }
}
```

</details>

```typescript
// TypeScript - Application 추상 기반 클래스
abstract class Application {
  private isDone = false;

  protected abstract init(): void;
  protected abstract idle(): void;
  protected abstract cleanup(): void;

  protected setDone(): void {
    this.isDone = true;
  }

  protected done(): boolean {
    return this.isDone;
  }

  public run(): void {
    this.init();
    while (!this.done()) {
      this.idle();
    }
    this.cleanup();
  }
}
```

`run` 함수가 **템플릿 메소드** — 즉 알고리즘 골격을 담은 메소드 — 다. 모든 구체적인 작업이 추상 메소드 `init`, `idle`, `cleanup`에 맡겨졌다.

### 2.4 파생 클래스로 ftoc 재작성

`Application`을 상속해서 추상 메소드의 내용을 채워 넣는 것만으로 `ftoc`를 다시 작성할 수 있다.

<details>
<summary>원문 Java 코드 (목록 14-3)</summary>

```java
// Java - 목록 14-3: ftocTemplateMethod.java
public class ftocTemplateMethod extends Application {
    private InputStreamReader isr;
    private BufferedReader br;

    public static void main(String[] args) throws Exception {
        (new ftocTemplateMethod()).run();
    }

    protected void init() {
        isr = new InputStreamReader(System.in);
        br = new BufferedReader(isr);
    }

    protected void idle() {
        String fahrString = readLineAndReturnNullIfError();
        if (fahrString == null || fahrString.length() == 0) {
            setDone();
        } else {
            double fahr = Double.parseDouble(fahrString);
            double celcius = 5.0 / 9.0 * (fahr - 32);
            System.out.println("F=" + fahr + ", C=" + celcius);
        }
    }

    protected void cleanup() {
        System.out.println("ftoc exit");
    }

    private String readLineAndReturnNullIfError() {
        try {
            return br.readLine();
        } catch (IOException e) {
            return null;
        }
    }
}
```

</details>

```typescript
// TypeScript - 파생 클래스
class FtocTemplateMethod extends Application {
  private lines: AsyncIterator<string> | null = null;

  protected init(): void {
    const rl = readline.createInterface({ input: process.stdin });
    this.lines = rl[Symbol.asyncIterator]();
  }

  protected idle(): void {
    // 의사 코드 — 실제로는 비동기 처리가 필요하지만, 패턴 구조를 보여주기 위해 간략화
    const fahrString = this.readLineOrNull();
    if (!fahrString) {
      this.setDone();
      return;
    }
    const fahr = Number.parseFloat(fahrString);
    const celcius = (5.0 / 9.0) * (fahr - 32);
    console.log(`F=${fahr}, C=${celcius}`);
  }

  protected cleanup(): void {
    console.log("ftoc exit");
  }

  private readLineOrNull(): string | null {
    // 입력 한 줄 또는 null 반환
    return null;
  }
}
```

### 2.5 패턴 오용 경고

> **Uncle Bob의 경험**: 이 예는 패턴의 동작을 보여주기 위해 선택했을 뿐, 실제로 `ftoc`를 이렇게 만들기를 권하지 않는다. 이것은 **패턴 오용**의 좋은 예가 된다. 단순한 애플리케이션에 템플릿 메소드를 강제로 적용하면 프로그램이 복잡해지고 내용만 더 늘어날 뿐이다. 디자인 패턴이 존재한다는 사실 자체가 항상 그 패턴을 사용해야 한다는 뜻은 아니다. 패턴을 적용하는 비용이 결과적인 이익보다 더 클 수 있다.

---

## 3. 더 유용한 예 — 버블 정렬

### 3.1 초기 버전 BubbleSorter

먼저 정수 배열을 정렬하는 단순한 버블 정렬을 보자.

<details>
<summary>원문 Java 코드 (목록 14-4)</summary>

```java
// Java - 목록 14-4: BubbleSorter.java (초기 버전)
public class BubbleSorter {
    static int operations = 0;

    public static int sort(int[] array) {
        operations = 0;
        if (array.length <= 1) {
            return operations;
        }
        for (int nextToLast = array.length - 2; nextToLast >= 0; nextToLast--) {
            for (int index = 0; index <= nextToLast; index++) {
                compareAndSwap(array, index);
            }
        }
        return operations;
    }

    private static void swap(int[] array, int index) {
        int temp = array[index];
        array[index] = array[index + 1];
        array[index + 1] = temp;
    }

    private static void compareAndSwap(int[] array, int index) {
        if (array[index] > array[index + 1]) {
            swap(array, index);
        }
        operations++;
    }
}
```

</details>

```typescript
// TypeScript - 초기 버전
class BubbleSorter {
  static operations = 0;

  static sort(array: number[]): number {
    BubbleSorter.operations = 0;
    if (array.length <= 1) {
      return BubbleSorter.operations;
    }
    for (let nextToLast = array.length - 2; nextToLast >= 0; nextToLast--) {
      for (let index = 0; index <= nextToLast; index++) {
        BubbleSorter.compareAndSwap(array, index);
      }
    }
    return BubbleSorter.operations;
  }

  private static swap(array: number[], index: number): void {
    const temp = array[index];
    array[index] = array[index + 1];
    array[index + 1] = temp;
  }

  private static compareAndSwap(array: number[], index: number): void {
    if (array[index] > array[index + 1]) {
      BubbleSorter.swap(array, index);
    }
    BubbleSorter.operations++;
  }
}
```

`sort` 메소드는 **알고리즘**을 담고 있고, `swap`과 `compareAndSwap`은 **정수와 배열의 구체적인 부분**을 다룬다 — 두 책임이 한 클래스에 결합되어 있다.

### 3.2 템플릿 메소드 적용

버블 정렬 알고리즘만 따로 떼어 추상 기반 클래스에 넣고, 구체적인 부분은 추상 메소드에 맡긴다.

```
       ┌───────────────────┐
       │  BubbleSorter     │  «abstract»
       ├───────────────────┤
       │ + doSort()        │  ◀── 알고리즘 골격
       │ # outOfOrder()    │  ◀── 추상
       │ # swap()          │  ◀── 추상
       └─────────┬─────────┘
                 △
        ┌────────┴────────┐
        │                 │
┌───────────────┐  ┌───────────────────┐
│IntBubbleSorter│  │DoubleBubbleSorter │
└───────────────┘  └───────────────────┘
```

<details>
<summary>원문 Java 코드 (목록 14-5)</summary>

```java
// Java - 목록 14-5: BubbleSorter.java (추상 기반 클래스)
public abstract class BubbleSorter {
    private int operations = 0;
    protected int length = 0;

    protected int doSort() {
        operations = 0;
        if (length <= 1) {
            return operations;
        }
        for (int nextToLast = length - 2; nextToLast >= 0; nextToLast--) {
            for (int index = 0; index <= nextToLast; index++) {
                if (outOfOrder(index)) {
                    swap(index);
                }
                operations++;
            }
        }
        return operations;
    }

    protected abstract void swap(int index);
    protected abstract boolean outOfOrder(int index);
}
```

</details>

```typescript
// TypeScript - 추상 기반 클래스
abstract class BubbleSorter {
  private operations = 0;
  protected length = 0;

  protected doSort(): number {
    this.operations = 0;
    if (this.length <= 1) {
      return this.operations;
    }
    for (let nextToLast = this.length - 2; nextToLast >= 0; nextToLast--) {
      for (let index = 0; index <= nextToLast; index++) {
        if (this.outOfOrder(index)) {
          this.swap(index);
        }
        this.operations++;
      }
    }
    return this.operations;
  }

  protected abstract swap(index: number): void;
  protected abstract outOfOrder(index: number): boolean;
}
```

### 3.3 파생 클래스 — IntBubbleSorter, DoubleBubbleSorter

<details>
<summary>원문 Java 코드 (목록 14-6, 14-7)</summary>

```java
// Java - 목록 14-6: IntBubbleSorter.java
public class IntBubbleSorter extends BubbleSorter {
    private int[] array = null;

    public int sort(int[] theArray) {
        array = theArray;
        length = array.length;
        return doSort();
    }

    protected void swap(int index) {
        int temp = array[index];
        array[index] = array[index + 1];
        array[index + 1] = temp;
    }

    protected boolean outOfOrder(int index) {
        return (array[index] > array[index + 1]);
    }
}

// Java - 목록 14-7: DoubleBubbleSorter.java
public class DoubleBubbleSorter extends BubbleSorter {
    private double[] array = null;

    public int sort(double[] theArray) {
        array = theArray;
        length = array.length;
        return doSort();
    }

    protected void swap(int index) {
        double temp = array[index];
        array[index] = array[index + 1];
        array[index + 1] = temp;
    }

    protected boolean outOfOrder(int index) {
        return (array[index] > array[index + 1]);
    }
}
```

</details>

```typescript
// TypeScript - 파생 클래스들
class IntBubbleSorter extends BubbleSorter {
  private array: number[] = [];

  sort(theArray: number[]): number {
    this.array = theArray;
    this.length = theArray.length;
    return this.doSort();
  }

  protected swap(index: number): void {
    const temp = this.array[index];
    this.array[index] = this.array[index + 1];
    this.array[index + 1] = temp;
  }

  protected outOfOrder(index: number): boolean {
    return this.array[index] > this.array[index + 1];
  }
}

class DoubleBubbleSorter extends BubbleSorter {
  private array: number[] = [];  // TypeScript는 double 구분 없음

  sort(theArray: number[]): number {
    this.array = theArray;
    this.length = theArray.length;
    return this.doSort();
  }

  protected swap(index: number): void {
    const temp = this.array[index];
    this.array[index] = this.array[index + 1];
    this.array[index + 1] = temp;
  }

  protected outOfOrder(index: number): boolean {
    return this.array[index] > this.array[index + 1];
  }
}
```

### 3.4 템플릿 메소드의 한계 — 결합도

템플릿 메소드 패턴은 객체지향에서 고전적인 재사용 형태를 보여준다. 일반적인 알고리즘은 기반 클래스에 있고, 다른 구체적인 내용에서 상속된다. **그러나 이 기법은 비용을 수반한다.**

> **핵심 통찰**: 상속은 아주 강한 관계여서, 파생 클래스는 필연적으로 기반 클래스에 묶이게 된다. `IntBubbleSorter`의 `outOfOrder`와 `swap` 함수는 다른 종류의 정렬 알고리즘에서도 필요로 하지만, **재사용할 방법이 없다.** `BubbleSorter`를 상속함으로써, `IntBubbleSorter`의 운명이 영원히 `BubbleSorter`와 묶이게끔 결정해버린 것이다.

---

## 4. 스트래터지 패턴

### 4.1 위임으로 같은 문제 풀기

스트래터지 패턴은 같은 문제를 완전히 다른 방식으로 풀어낸다. 일반적인 알고리즘을 추상 기반 클래스에 넣는 대신, **`ApplicationRunner`라는 구체 클래스**에 넣는다. 그리고 일반적 알고리즘이 호출해야 할 추상 메소드를 **`Application`이라는 인터페이스**로 정의한다.

```
   ┌────────────────────┐         ┌──────────────────────┐
   │ ApplicationRunner  │────────▶│  «interface»         │
   ├────────────────────┤  uses   │  Application         │
   │ + run()            │         ├──────────────────────┤
   └────────────────────┘         │ + init()             │
                                  │ + idle()             │
                                  │ + cleanup()          │
                                  │ + done(): boolean    │
                                  └──────────┬───────────┘
                                             △
                                             │
                                  ┌──────────┴───────────┐
                                  │   ftocStrategy       │
                                  └──────────────────────┘
```

### 4.2 ApplicationRunner와 Application 인터페이스

<details>
<summary>원문 Java 코드 (목록 14-8, 14-9)</summary>

```java
// Java - 목록 14-8: ApplicationRunner.java
public class ApplicationRunner {
    private Application itsApplication = null;

    public ApplicationRunner(Application app) {
        itsApplication = app;
    }

    public void run() {
        itsApplication.init();
        while (!itsApplication.done()) {
            itsApplication.idle();
        }
        itsApplication.cleanup();
    }
}

// Java - 목록 14-9: Application.java (인터페이스)
public interface Application {
    public void init();
    public void idle();
    public void cleanup();
    public boolean done();
}
```

</details>

```typescript
// TypeScript - ApplicationRunner와 Application 인터페이스
interface Application {
  init(): void;
  idle(): void;
  cleanup(): void;
  done(): boolean;
}

class ApplicationRunner {
  constructor(private readonly itsApplication: Application) {}

  run(): void {
    this.itsApplication.init();
    while (!this.itsApplication.done()) {
      this.itsApplication.idle();
    }
    this.itsApplication.cleanup();
  }
}
```

### 4.3 ftocStrategy 구현

<details>
<summary>원문 Java 코드 (목록 14-10)</summary>

```java
// Java - 목록 14-10: ftocStrategy.java
public class ftocStrategy implements Application {
    private InputStreamReader isr;
    private BufferedReader br;
    private boolean isDone = false;

    public static void main(String[] args) throws Exception {
        (new ApplicationRunner(new ftocStrategy())).run();
    }

    public void init() {
        isr = new InputStreamReader(System.in);
        br = new BufferedReader(isr);
    }

    public void idle() {
        String fahrString = readLineAndReturnNullIfError();
        if (fahrString == null || fahrString.length() == 0) {
            isDone = true;
        } else {
            double fahr = Double.parseDouble(fahrString);
            double celcius = 5.0 / 9.0 * (fahr - 32);
            System.out.println("F=" + fahr + ", C=" + celcius);
        }
    }

    public void cleanup() {
        System.out.println("ftoc exit");
    }

    public boolean done() {
        return isDone;
    }

    private String readLineAndReturnNullIfError() {
        try {
            return br.readLine();
        } catch (IOException e) {
            return null;
        }
    }
}
```

</details>

```typescript
// TypeScript - ftocStrategy 구현
class FtocStrategy implements Application {
  private isDone = false;

  init(): void {
    // 입력 스트림 초기화
  }

  idle(): void {
    const fahrString = this.readLineOrNull();
    if (!fahrString) {
      this.isDone = true;
      return;
    }
    const fahr = Number.parseFloat(fahrString);
    const celcius = (5.0 / 9.0) * (fahr - 32);
    console.log(`F=${fahr}, C=${celcius}`);
  }

  cleanup(): void {
    console.log("ftoc exit");
  }

  done(): boolean {
    return this.isDone;
  }

  private readLineOrNull(): string | null {
    return null;
  }
}

// 실행
new ApplicationRunner(new FtocStrategy()).run();
```

### 4.4 스트래터지의 trade-off

> **핵심 통찰**: 스트래터지에는 템플릿 메소드보다 **더 많은 전체 클래스 개수**와 **더 많은 간접 지정(*indirection - 직접 호출 대신 중간 객체/포인터를 거치는 것*)**이 있다. 위임 포인터는 실행 시간과 데이터 공간 면에서 상속의 경우보다 좀 더 많은 비용을 초래한다. 그러나 그 대신, `ApplicationRunner` 인스턴스를 재사용해 다양한 `Application` 구현에 넘겨줄 수 있다 — 즉 **결합도가 훨씬 낮아진다.**

---

## 5. 스트래터지로 다시 정렬하기

### 5.1 BubbleSorter를 위임 기반으로 재구성

이번에는 `BubbleSorter`가 **구체 클래스**가 되고, 정렬 대상의 비교/교환은 `SortHandle` 인터페이스에 위임한다.

```
   ┌────────────────────┐         ┌──────────────────────┐
   │   BubbleSorter     │────────▶│  «interface»         │
   ├────────────────────┤         │  SortHandle          │
   │ + sort(array)      │         ├──────────────────────┤
   └────────────────────┘         │ + swap(index)        │
                                  │ + outOfOrder(index)  │
                                  │ + length()           │
                                  │ + setArray(array)    │
                                  └──────────┬───────────┘
                                             △
                                             │
                                  ┌──────────┴───────────┐
                                  │   IntSortHandle      │
                                  └──────────────────────┘
```

<details>
<summary>원문 Java 코드 (목록 14-11, 14-12, 14-13)</summary>

```java
// Java - 목록 14-11: BubbleSorter.java (스트래터지 버전)
public class BubbleSorter {
    private int operations = 0;
    private int length = 0;
    private SortHandle itsSortHandle = null;

    public BubbleSorter(SortHandle handle) {
        itsSortHandle = handle;
    }

    public int sort(Object array) {
        itsSortHandle.setArray(array);
        length = itsSortHandle.length();
        operations = 0;
        if (length <= 1) {
            return operations;
        }
        for (int nextToLast = length - 2; nextToLast >= 0; nextToLast--) {
            for (int index = 0; index <= nextToLast; index++) {
                if (itsSortHandle.outOfOrder(index)) {
                    itsSortHandle.swap(index);
                }
                operations++;
            }
        }
        return operations;
    }
}

// Java - 목록 14-12: SortHandle.java
public interface SortHandle {
    public void swap(int index);
    public boolean outOfOrder(int index);
    public int length();
    public void setArray(Object array);
}

// Java - 목록 14-13: IntSortHandle.java
public class IntSortHandle implements SortHandle {
    private int[] array = null;

    public void swap(int index) {
        int temp = array[index];
        array[index] = array[index + 1];
        array[index + 1] = temp;
    }

    public void setArray(Object array) {
        this.array = (int[]) array;
    }

    public int length() {
        return array.length;
    }

    public boolean outOfOrder(int index) {
        return (array[index] > array[index + 1]);
    }
}
```

</details>

```typescript
// TypeScript - 스트래터지 버전
interface SortHandle {
  swap(index: number): void;
  outOfOrder(index: number): boolean;
  length(): number;
  setArray(array: unknown): void;
}

class BubbleSorter {
  private operations = 0;
  private len = 0;

  constructor(private readonly itsSortHandle: SortHandle) {}

  sort(array: unknown): number {
    this.itsSortHandle.setArray(array);
    this.len = this.itsSortHandle.length();
    this.operations = 0;
    if (this.len <= 1) {
      return this.operations;
    }
    for (let nextToLast = this.len - 2; nextToLast >= 0; nextToLast--) {
      for (let index = 0; index <= nextToLast; index++) {
        if (this.itsSortHandle.outOfOrder(index)) {
          this.itsSortHandle.swap(index);
        }
        this.operations++;
      }
    }
    return this.operations;
  }
}

class IntSortHandle implements SortHandle {
  private array: number[] = [];

  setArray(array: unknown): void {
    this.array = array as number[];
  }

  length(): number {
    return this.array.length;
  }

  outOfOrder(index: number): boolean {
    return this.array[index] > this.array[index + 1];
  }

  swap(index: number): void {
    const temp = this.array[index];
    this.array[index] = this.array[index + 1];
    this.array[index + 1] = temp;
  }
}
```

### 5.2 핵심 — IntSortHandle은 BubbleSorter를 모른다

> **핵심 통찰**: `IntSortHandle` 클래스가 `BubbleSorter`에 대해 **아무것도 모른다**는 점에 주목하자. 이 클래스는 버블 정렬 구현에 어떤 의존성도 갖고 있지 않다 — **이것은 템플릿 메소드에서는 없었던 일이다.** 템플릿 메소드를 사용한 접근에서는 `IntBubbleSorter`가 직접적으로 `BubbleSorter`(버블 정렬 알고리즘을 포함한 클래스)에 의존했다. 그래서 부분적으로 DIP를 위반했다. 스트래터지를 사용한 접근은 이런 의존성이 없으므로 `IntSortHandle`은 **다른 어떤 정렬 알고리즘과도 함께 사용할 수 있다.**

### 5.3 QuickBubbleSorter — 다른 알고리즘에 재사용

예를 들어, 배열을 한 번 훑었을 때 순서가 제대로 되어 있으면 일찍 종료해버리는 버블 정렬의 변형을 만들 수 있다. 이 `QuickBubbleSorter`는 `IntSortHandle`이나 `SortHandle`에서 파생된 다른 클래스도 그대로 사용할 수 있다.

<details>
<summary>원문 Java 코드 (목록 14-14)</summary>

```java
// Java - 목록 14-14: QuickBubbleSorter.java
public class QuickBubbleSorter {
    private int operations = 0;
    private int length = 0;
    private SortHandle itsSortHandle = null;

    public QuickBubbleSorter(SortHandle handle) {
        itsSortHandle = handle;
    }

    public int sort(Object array) {
        itsSortHandle.setArray(array);
        length = itsSortHandle.length();
        operations = 0;
        if (length <= 1) {
            return operations;
        }
        boolean thisPassInOrder = false;
        for (int nextToLast = length - 2;
             nextToLast >= 0 && !thisPassInOrder;
             nextToLast--) {
            thisPassInOrder = true;  // 잠재적으로
            for (int index = 0; index <= nextToLast; index++) {
                if (itsSortHandle.outOfOrder(index)) {
                    itsSortHandle.swap(index);
                    thisPassInOrder = false;
                }
                operations++;
            }
        }
        return operations;
    }
}
```

</details>

```typescript
// TypeScript - QuickBubbleSorter
class QuickBubbleSorter {
  private operations = 0;
  private len = 0;

  constructor(private readonly itsSortHandle: SortHandle) {}

  sort(array: unknown): number {
    this.itsSortHandle.setArray(array);
    this.len = this.itsSortHandle.length();
    this.operations = 0;
    if (this.len <= 1) {
      return this.operations;
    }
    let thisPassInOrder = false;
    for (
      let nextToLast = this.len - 2;
      nextToLast >= 0 && !thisPassInOrder;
      nextToLast--
    ) {
      thisPassInOrder = true;
      for (let index = 0; index <= nextToLast; index++) {
        if (this.itsSortHandle.outOfOrder(index)) {
          this.itsSortHandle.swap(index);
          thisPassInOrder = false;
        }
        this.operations++;
      }
    }
    return this.operations;
  }
}

// 같은 IntSortHandle을 다른 알고리즘에 재사용
const handle = new IntSortHandle();
new BubbleSorter(handle).sort([3, 1, 4, 1, 5, 9, 2, 6]);
new QuickBubbleSorter(handle).sort([3, 1, 4, 1, 5, 9, 2, 6]);
```

### 5.4 스트래터지의 특별한 이점

> **핵심 통찰**: 템플릿 메소드 패턴이 **하나의 일반적인 알고리즘으로 많은 구체적인 구현을 조작**할 수 있게 해주는 반면, **DIP를 완전히 따르는 스트래터지 패턴은 각각의 구체적인 구현이 다른 많은 일반적인 알고리즘에 의해 조작될 수 있게 해준다.** 의존성이 양쪽 모두 추상화(`SortHandle`)를 향하기 때문이다.

---

## 6. 두 패턴 비교

### 6.1 메커니즘 비교

| 측면 | 템플릿 메소드 | 스트래터지 |
|------|----------------|-------------|
| **관계 메커니즘** | 상속 (is-a) | 위임/복합 (has-a) |
| **알고리즘 위치** | 추상 기반 클래스 | 구체 클래스 |
| **구체 단계 위치** | 파생 클래스 (오버라이드) | 별도 인터페이스 구현체 |
| **결합도** | 강함 — 구체 단계가 알고리즘 클래스에 묶임 | 약함 — 구체 단계가 알고리즘을 모름 |
| **클래스 개수** | 적음 | 많음 (인터페이스 + Runner + Strategy) |
| **런타임 비용** | 적음 (가상 호출만) | 약간 많음 (위임 포인터 +α) |
| **DIP 준수** | 부분적 — 구체 단계가 알고리즘에 의존 | 완전 — 양쪽 모두 추상화에 의존 |
| **재사용 방향** | 알고리즘이 여러 구현을 조작 | 구현이 여러 알고리즘에 의해 조작됨 (양방향) |

### 6.2 언제 무엇을 쓸까

| 상황 | 권장 |
|------|------|
| 알고리즘이 안정적이고 구체 단계만 자주 바뀜 | **템플릿 메소드** — 단순함 |
| 같은 구체 단계를 여러 알고리즘에서 재사용하고 싶음 | **스트래터지** — 양방향 재사용 |
| 런타임에 알고리즘을 교체하고 싶음 | **스트래터지** — 상속은 컴파일 타임 결정 |
| 클래스 폭증을 피하고 싶은 단순한 경우 | **템플릿 메소드** |
| 테스트 시 구체 단계를 mock으로 갈아 끼우고 싶음 | **스트래터지** — DI가 자연스러움 |

### 6.3 의존성 방향 다이어그램

**템플릿 메소드 — 부분적 DIP 준수:**

```
       ┌──────────────────┐
       │  BubbleSorter    │  «abstract»  ◀── 알고리즘
       └────────┬─────────┘
                △
                │  extends (의존)
       ┌────────┴─────────┐
       │ IntBubbleSorter  │              ◀── 구체 단계
       └──────────────────┘
                  ↑
        IntBubbleSorter는 BubbleSorter에 의존한다
        (다른 알고리즘에서 swap/outOfOrder 재사용 불가)
```

**스트래터지 — 완전한 DIP 준수:**

```
   ┌────────────────┐         ┌─────────────────┐
   │ BubbleSorter   │────────▶│  «interface»    │◀────────┐
   └────────────────┘         │   SortHandle    │         │
                              └────────┬────────┘         │
   ┌────────────────┐                  △                  │
   │QuickBubbleSort │──────────────────┘                  │
   └────────────────┘                  │                  │
                              ┌────────┴────────┐         │
                              │  IntSortHandle  │─────────┘
                              └─────────────────┘
        IntSortHandle은 어떤 정렬 알고리즘에도 의존하지 않는다
        (양쪽 모두 SortHandle 추상화에 의존)
```

---

## 7. 자주 하는 실수

| 안티패턴 | 문제 | 해결 |
|----------|------|------|
| **패턴 강제 적용** — 단순한 ftoc에 Application 추상 클래스 도입 | 비용 > 이익. 복잡성만 증가 | 변경 축이 실제로 드러날 때만 적용 |
| **상속을 코드 재사용 도구로만 사용** — 단지 swap 같은 헬퍼를 재사용하려고 상속 | 파생 클래스 운명이 기반 클래스에 영원히 묶임 | 헬퍼를 별도 클래스/인터페이스로 추출 (위임) |
| **템플릿 메소드의 구체 단계를 다른 곳에서 재사용** | 구체 단계가 알고리즘 클래스에 의존해 불가능 | 스트래터지로 전환 |
| **추상 단계를 너무 많이 노출** — 모든 메소드를 abstract로 | 서브클래스가 채워야 할 부담 폭증 | 진짜 가변 단계만 추상으로 |
| **알고리즘이 한 종류만 필요한데 스트래터지 도입** | 인터페이스, Runner, Strategy 등 클래스 폭증 | 템플릿 메소드 또는 단순 함수로 |

---

## 8. 설계 원칙

| 원칙 | 설명 |
|------|------|
| **알고리즘과 구체 단계를 분리하라** | 둘 다 같은 추상화에 의존하게 — DIP |
| **상속보다 복합을 우선하라** | 결합도 차이가 크다. 같은 일을 위임으로 풀 수 있다면 위임을 선택 |
| **재사용 방향을 고려하라** | 알고리즘 → 구현 한 방향이면 템플릿 메소드. 양방향이면 스트래터지 |
| **패턴 적용은 비용/이익 분석 후에** | 패턴이 존재한다는 사실이 적용 이유가 아니다. 변경의 축이 실제로 드러날 때 적용 |
| **인터페이스로 의존성 방향을 설계하라** | 구체 클래스가 인터페이스를 향해 의존하도록 — 양쪽 모두 |

---

## 9. 결론

템플릿 메소드와 스트래터지 패턴 모두 **상위 단계의 알고리즘을 하위 단계의 구체적인 부분으로부터 분리해주는 역할**을 한다. 둘 다 상위 단계의 알고리즘이 구체적인 부분과 독립적으로 재사용될 수 있게 해준다.

> **핵심 통찰**: 약간의 복잡성과 메모리, 실행 시간을 더 감내하면, **스트래터지는 구체적인 부분이 상위 단계 알고리즘으로부터 독립적으로 재사용될 수 있게까지 해준다.** 즉, 두 패턴 모두 "알고리즘 → 구체"의 재사용을 가능하게 하지만, 스트래터지는 추가로 "구체 → 다른 알고리즘"의 재사용까지 열어준다. 이것이 DIP 완전 준수의 직접적인 결과다.

---

## 요약

- **두 패턴의 공통점**: 일반적인 알고리즘을 구체적인 구현으로부터 분리 — DIP를 적용
- **메커니즘 차이**:
  - **템플릿 메소드** — 상속 기반. 추상 기반 클래스의 `run`/`doSort` 같은 골격 메소드가 추상 단계 메소드를 호출
  - **스트래터지** — 위임 기반. 구체 알고리즘 클래스가 인터페이스를 통해 구체 단계 객체에 위임
- **결합도**:
  - 템플릿 메소드는 파생 클래스가 기반 클래스에 강하게 묶임 — 구체 단계를 다른 알고리즘에 재사용 불가
  - 스트래터지는 구체 단계가 알고리즘을 전혀 모름 — 양방향 재사용 가능
- **trade-off**:
  - 템플릿 메소드는 단순하지만 결합도가 높다
  - 스트래터지는 클래스 수 / 간접 지정 / 메모리 비용이 늘지만 결합도가 낮다
- **패턴 오용 경고**: 디자인 패턴이 존재한다는 사실이 항상 적용 이유가 되지 않는다. `ftoc` 같은 단순한 예에 `Application` 추상화를 강제하면 비용이 이익을 초과한다 — **변경의 축이 실제로 드러날 때 적용**한다
- **스트래터지의 특별한 이점**: 템플릿 메소드는 하나의 알고리즘이 여러 구현을 조작할 수 있게 하지만, 스트래터지는 **하나의 구현이 여러 알고리즘에 의해 조작될 수 있게** 해준다 — 진정한 양방향 재사용
- **선택 기준**: 알고리즘이 안정적이고 단순한 경우 템플릿 메소드. 구체 단계를 재사용하거나 런타임에 알고리즘을 교체해야 하면 스트래터지
