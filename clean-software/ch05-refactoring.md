# Chapter 5: Refactoring (리팩토링)

## 핵심 질문

제대로 동작하는 코드의 구조를 왜 굳이 개선해야 하는가? 긁어 부스럼을 만들지 말라는 옛말도 있지 않은가? 리팩토링(*Refactoring - 외부 행위를 바꾸지 않으면서 내부 구조를 개선하는 과정*)이 단순한 "코드 정리"를 넘어서 **소프트웨어 모듈의 본질적 기능**과 어떻게 연결되는가?

> 풍족한 세상에서 점점 더 부족해지고 있는 유일한 것은 사람들의 주의력이다.<br>— 케빈 켈리(Kevin Kelly), 『와이어드(Wired)』

---

## 1. 리팩토링이란 무엇인가

마틴 파울러(Martin Fowler)는 그의 고전적 저서 『리팩토링(Refactoring)』에서 리팩토링을 다음과 같이 정의했다.

> **리팩토링**: 외부 행위를 바꾸지 않으면서 내부 구조를 개선하는 방법으로, 소프트웨어 시스템을 변경하는 프로세스.

이 정의에서 핵심은 **"외부 행위를 바꾸지 않으면서"**라는 부분이다. 즉, 리팩토링 전후로 프로그램이 동일하게 동작해야 한다. 이 안전성은 **자동화된 테스트**가 보장한다. 테스트가 모두 통과하는 상태에서 조금씩 구조를 바꾸고, 매번 테스트로 검증한다.

### 1.1 모듈의 세 가지 기능

모든 소프트웨어 모듈에는 세 가지 기능이 있다.

| # | 기능 | 설명 |
|---|------|------|
| 1 | **실행 중에 동작하는 기능** | 모듈의 존재 이유. 사용자에게 가치를 전달한다 |
| 2 | **변경 기능** | 대부분의 모듈은 생명주기 동안 변경된다. 변경을 쉽게 만드는 것이 개발자의 책임 |
| 3 | **읽는 사람과 의사소통하는 기능** | 모듈은 특별한 훈련 없이도 개발자가 쉽게 읽고 이해할 수 있어야 한다 |

> **핵심 통찰**: 변경하기 어려운 모듈은 **그것이 제대로 동작한다 하더라도 망가진 것이며 수리가 필요하다**. 읽는 사람과 의사소통할 수 없는 모듈 또한 망가진 것이며 수리가 필요하다. 동작은 모듈의 세 가지 책임 중 하나일 뿐이다.

### 1.2 리팩토링은 원칙과 패턴을 넘어선다

읽기 쉽고 변경하기 쉬운 모듈을 만들려면 단순한 원칙과 패턴 이상의 무엇이 필요한데, 바로 **주의력과 훈련**이다. 그리고 미를 창조하기 위한 **열정**이 필요하다.

> **Uncle Bob의 경험**: 이 책의 대부분은 독자들이 유연하고 융통성 있는 모듈을 만들 수 있도록 돕는 원칙과 패턴을 설명하는 데 할애된다. 그러나 원칙과 패턴만으로는 충분하지 않다. 매일 코드에 주의를 기울이고, 작은 단위로 다듬어 가는 훈련이 동반되어야 한다.

---

## 2. 소수 생성기: 리팩토링의 간단한 예

이번 장의 중심 예제는 **소수(prime number)를 생성하는 함수**이다. 알고리즘은 고대의 **에라토스테네스의 체(Sieve of Eratosthenes)** — 2부터 시작하는 정수 배열에서 소수의 배수를 차례로 지워 나가는 방식이다.

원래 코드는 "동작은 하지만 읽기 어려운" 상태이며, 단계적 리팩토링을 통해 이를 "읽기도 쉽고 변경하기도 쉬운" 형태로 변모시키는 과정을 보여준다.

### 2.1 버전 1: 원래 코드 — 거대한 단일 함수

처음 코드는 **단일 문자로 이루어진 많은 변수**(`s`, `f`, `i`, `j`)와 **변수의 의미를 설명하는 주석들**을 포함한 하나의 큰 함수다.

<details>
<summary>원문 Java 코드 (버전 1)</summary>

```java
/**
 * 이 클래스는 사용자가 지정한 최댓값까지의 소수를 생성한다.
 * 사용한 알고리즘은 에라토스테네스의 체(Sieve of Eratosthenes)다.
 * 2부터 시작하는 정수 배열을 받는다.
 * 2의 배수를 모두 지운다.
 * 지워지지 않은 다음 정수를 찾아 그 배수를 모두 지운다.
 * 최댓값의 제곱근 값을 넘을 때까지 이 과정을 계속한다.
 *
 * @author Robert C. Martin
 * @version 9 Dec 1999 rcm
 */
public class GeneratePrimes {
    /**
     * @param maxValue 는 생성 한계값이다.
     */
    public static int[] generatePrimes(int maxValue) {
        if (maxValue >= 2) { // 유효한 경우에만
            // 선언
            int s = maxValue + 1; // 배열 크기
            boolean[] f = new boolean[s];
            int i;
            // 배열을 true 값으로 초기화한다.
            for (i = 0; i < s; i++)
                f[i] = true;
            // 알려진 비소수를 제거한다.
            f[0] = f[1] = false;
            // 체로 걸러내기
            int j;
            for (i = 2; i < Math.sqrt(s) + 1; i++) {
                if (f[i]) { // i가 지워지지 않았으면 그 배수를 지운다.
                    for (j = 2 * i; j < s; j += i)
                        f[j] = false; // 배수는 소수가 아니다.
                }
            }
            // 지워지지 않은 정수가 몇 개인가?
            int count = 0;
            for (i = 0; i < s; i++) {
                if (f[i])
                    count++; // 발견된 개수를 센다.
            }
            int[] primes = new int[count];
            // 소수를 결과 집합에 넣는다.
            for (i = 0, j = 0; i < s; i++) {
                if (f[i]) // 소수이면
                    primes[j++] = i;
            }
            return primes; // 소수를 반환
        } else { // maxValue < 2
            return new int[0]; // 잘못된 입력이 들어왔을 경우 빈 배열을 반환
        }
    }
}
```

</details>

```typescript
// TypeScript 버전 1
/**
 * 이 클래스는 사용자가 지정한 최댓값까지의 소수를 생성한다.
 * 사용한 알고리즘은 에라토스테네스의 체다.
 */
class GeneratePrimes {
  static generatePrimes(maxValue: number): number[] {
    if (maxValue >= 2) {
      // 선언
      const s = maxValue + 1; // 배열 크기
      const f: boolean[] = new Array(s);
      let i: number;
      // 배열을 true 값으로 초기화한다.
      for (i = 0; i < s; i++) {
        f[i] = true;
      }
      // 알려진 비소수를 제거한다.
      f[0] = f[1] = false;
      // 체로 걸러내기
      let j: number;
      for (i = 2; i < Math.sqrt(s) + 1; i++) {
        if (f[i]) {
          for (j = 2 * i; j < s; j += i) {
            f[j] = false;
          }
        }
      }
      // 발견된 개수를 센다.
      let count = 0;
      for (i = 0; i < s; i++) {
        if (f[i]) {
          count++;
        }
      }
      const primes: number[] = new Array(count);
      // 소수를 결과 집합에 넣는다.
      for (i = 0, j = 0; i < s; i++) {
        if (f[i]) {
          primes[j++] = i;
        }
      }
      return primes;
    } else {
      return [];
    }
  }
}
```

### 2.2 안전망: 단위 테스트

리팩토링의 핵심 전제는 **테스트**다. 테스트가 없으면 "동작을 바꾸지 않았다"는 보장이 없다. 다음은 통계적 접근 방식의 단위 테스트다 — 0, 2, 3, 100까지 소수 생성을 확인한다.

<details>
<summary>원문 Java 테스트 (TestGeneratePrimes)</summary>

```java
import junit.framework.TestCase;

public class TestGeneratePrimes extends TestCase {
    public TestGeneratePrimes(String name) {
        super(name);
    }

    public void testPrimes() {
        int[] nullArray = GeneratePrimes.generatePrimes(0);
        assertEquals(nullArray.length, 0);

        int[] minArray = GeneratePrimes.generatePrimes(2);
        assertEquals(minArray.length, 1);
        assertEquals(minArray[0], 2);

        int[] threeArray = GeneratePrimes.generatePrimes(3);
        assertEquals(threeArray.length, 2);
        assertEquals(threeArray[0], 2);
        assertEquals(threeArray[1], 3);

        int[] centArray = GeneratePrimes.generatePrimes(100);
        assertEquals(centArray.length, 25);
        assertEquals(centArray[24], 97);
    }
}
```

</details>

```typescript
// TypeScript (Jest 스타일)
describe('GeneratePrimes', () => {
  it('handles edge cases and produces correct primes up to 100', () => {
    const nullArray = GeneratePrimes.generatePrimes(0);
    expect(nullArray.length).toBe(0);

    const minArray = GeneratePrimes.generatePrimes(2);
    expect(minArray.length).toBe(1);
    expect(minArray[0]).toBe(2);

    const threeArray = GeneratePrimes.generatePrimes(3);
    expect(threeArray.length).toBe(2);
    expect(threeArray[0]).toBe(2);
    expect(threeArray[1]).toBe(3);

    const centArray = GeneratePrimes.generatePrimes(100);
    expect(centArray.length).toBe(25);
    expect(centArray[24]).toBe(97);
  });
});
```

테스트 100까지가 모두 성공으로 끝나면, 이 생성기가 제대로 동작한다고 추정한다. 완벽한 검증은 아니지만 이 테스트를 통과하면서 함수 자체에 결함이 있는 시나리오를 생각해 내기는 힘들다.

> **핵심 통찰**: 리팩토링의 매 단계마다 **"이 상태에서도 테스트는 전부 제대로 동작한다"**를 확인하는 것이 핵심이다. 리팩토링은 한 번에 한 걸음씩, 항상 테스트가 초록색인 상태에서 진행된다.

---

## 3. 리팩토링 단계별 진행

### 3.1 버전 2: 메소드 추출 (Extract Method)

메인 함수가 명백히 **세 가지 일**을 한다는 것을 발견할 수 있다.

1. 모든 변수를 초기화하고 체를 기본 상태로 설정
2. 체로 걸러내는 동작을 실제로 실행
3. 체로 걸러낸 결과를 정수 배열에 담기

이 세 동작을 각각 별개의 메소드로 추출한다. 또한 클래스 이름을 더 의미 있는 `PrimeGenerator`로 바꾼다. 함수의 일부 지역 변수는 클래스의 `static` 필드로 **승격(promote)**되었다 — 이로써 어떤 변수가 지역이고 어떤 변수가 전역인지 명확해진다.

<details>
<summary>원문 Java 코드 (버전 2)</summary>

```java
public class PrimeGenerator {
    private static int s;
    private static boolean[] f;
    private static int[] primes;

    public static int[] generatePrimes(int maxValue) {
        if (maxValue < 2) {
            return new int[0];
        } else {
            initializeSieve(maxValue);
            sieve();
            loadPrimes();
            return primes;
        }
    }

    private static void initializeSieve(int maxValue) {
        s = maxValue + 1;
        f = new boolean[s];
        for (int i = 0; i < s; i++)
            f[i] = true;
        f[0] = f[1] = false;
    }

    private static void sieve() {
        for (int i = 2; i < Math.sqrt(s) + 1; i++) {
            if (f[i]) {
                for (int j = 2 * i; j < s; j += i)
                    f[j] = false;
            }
        }
    }

    private static void loadPrimes() {
        int count = 0;
        for (int i = 0; i < s; i++) {
            if (f[i])
                count++;
        }
        primes = new int[count];
        for (int i = 0, j = 0; i < s; i++) {
            if (f[i])
                primes[j++] = i;
        }
    }
}
```

</details>

```typescript
// TypeScript 버전 2
class PrimeGenerator {
  private static s: number;
  private static f: boolean[];
  private static primes: number[];

  static generatePrimes(maxValue: number): number[] {
    if (maxValue < 2) {
      return [];
    } else {
      PrimeGenerator.initializeSieve(maxValue);
      PrimeGenerator.sieve();
      PrimeGenerator.loadPrimes();
      return PrimeGenerator.primes;
    }
  }

  private static initializeSieve(maxValue: number): void {
    PrimeGenerator.s = maxValue + 1;
    PrimeGenerator.f = new Array(PrimeGenerator.s);
    for (let i = 0; i < PrimeGenerator.s; i++) {
      PrimeGenerator.f[i] = true;
    }
    PrimeGenerator.f[0] = PrimeGenerator.f[1] = false;
  }

  private static sieve(): void {
    for (let i = 2; i < Math.sqrt(PrimeGenerator.s) + 1; i++) {
      if (PrimeGenerator.f[i]) {
        for (let j = 2 * i; j < PrimeGenerator.s; j += i) {
          PrimeGenerator.f[j] = false;
        }
      }
    }
  }

  private static loadPrimes(): void {
    let count = 0;
    for (let i = 0; i < PrimeGenerator.s; i++) {
      if (PrimeGenerator.f[i]) {
        count++;
      }
    }
    PrimeGenerator.primes = new Array(count);
    for (let i = 0, j = 0; i < PrimeGenerator.s; i++) {
      if (PrimeGenerator.f[i]) {
        PrimeGenerator.primes[j++] = i;
      }
    }
  }
}
```

`generatePrimes`는 이제 세 줄의 단순한 코디네이션 로직만 남았다 — **무엇을 하는 함수인지 한눈에 들어온다**. 테스트는 여전히 모두 통과한다.

### 3.2 버전 3: 변수 정리와 의미 있는 이름

`initializeSieve`는 약간 지저분하다. 다음을 손본다.

- 모든 `s` 변수를 `f.length`로 바꾸어 별도 변수를 없앤다
- 세 함수의 이름을 좀 더 의미 있는 것으로 바꾼다: `initializeSieve` → `initializeArrayOfIntegers`, `sieve` → `crossOutMultiples`, `loadPrimes` → `putUncrossedIntegersIntoResult`
- `primes` 필드 이름을 `result`로 바꾼다
- `initializeArrayOfIntegers`의 내부 구조를 더 읽기 쉽게 재배열한다

<details>
<summary>원문 Java 코드 (버전 3 — 일부)</summary>

```java
public class PrimeGenerator {
    private static boolean[] f;
    private static int[] result;

    public static int[] generatePrimes(int maxValue) {
        if (maxValue < 2)
            return new int[0];
        else {
            initializeArrayOfIntegers(maxValue);
            crossOutMultiples();
            putUncrossedIntegersIntoResult();
            return result;
        }
    }

    private static void initializeArrayOfIntegers(int maxValue) {
        f = new boolean[maxValue + 1];
        f[0] = f[1] = false; // 소수도 아니고 배수도 아니다.
        for (int i = 2; i < f.length; i++)
            f[i] = true;
    }
    // ...
}
```

</details>

```typescript
// TypeScript 버전 3 (일부)
class PrimeGenerator {
  private static f: boolean[];
  private static result: number[];

  static generatePrimes(maxValue: number): number[] {
    if (maxValue < 2) {
      return [];
    } else {
      PrimeGenerator.initializeArrayOfIntegers(maxValue);
      PrimeGenerator.crossOutMultiples();
      PrimeGenerator.putUncrossedIntegersIntoResult();
      return PrimeGenerator.result;
    }
  }

  private static initializeArrayOfIntegers(maxValue: number): void {
    PrimeGenerator.f = new Array(maxValue + 1);
    PrimeGenerator.f[0] = PrimeGenerator.f[1] = false;
    for (let i = 2; i < PrimeGenerator.f.length; i++) {
      PrimeGenerator.f[i] = true;
    }
  }
  // ...
}
```

테스트는 여전히 모두 통과한다.

### 3.3 버전 4: 의미 있는 변수명과 이중 부정 제거

`crossOutMultiples`를 본다. 함수 내부에 `if (f[i] == true)` 형태의 수행문이 많은데, 이는 **"i가 아직 안 지워졌는지"** 확인하는 것이다. 따라서 `f`의 이름을 `unCrossed`로 바꾸려 했다 — 그러나 그러면 `unCrossed[1] = false`처럼 **이중 부정으로 인한 혼란**이 생긴다.

> **핵심 통찰**: 이름을 짓다가 **이중 부정으로 인한 혼란**이 생기면, 그 이름은 잘못된 것이다. 의미가 더 자연스럽게 흘러가는 이름을 찾을 때까지 시도해 본다.

해결책: 배열 이름을 `isCrossed`로 바꾸고 **모든 불리언 값의 의미를 반전**시킨다. 이제 `true`는 "지워졌다", `false`는 "아직 안 지워졌다"를 뜻한다.

추가로 다음을 정리한다.

- `isCrossed[0]`, `isCrossed[1]`을 `true`로 설정하는 초기화를 없애고, 함수의 어떤 부분도 2보다 작은 인덱스를 사용하지 않게 만든다
- `crossOutMultiples`의 내부 루프를 별도 메소드 `crossOutMultiplesOf(i)`로 추출
- `if (isCrossed[i] == false)`도 혼란을 부추긴다고 보고 `notCrossed(i)` 함수를 만들어 `if (notCrossed(i))`로 변경
- 배열 크기의 제곱근값까지만 루프를 도는 이유를 설명하다가 그 계산을 `calcMaxPrimeFactor` 함수로 추출

<details>
<summary>원문 Java 코드 (버전 4 — 일부)</summary>

```java
public class PrimeGenerator {
    private static boolean[] isCrossed;
    private static int[] result;

    public static int[] generatePrimes(int maxValue) {
        if (maxValue < 2)
            return new int[0];
        else {
            initializeArrayOfIntegers(maxValue);
            crossOutMultiples();
            putUncrossedIntegersIntoResult();
            return result;
        }
    }

    private static void initializeArrayOfIntegers(int maxValue) {
        isCrossed = new boolean[maxValue + 1];
        for (int i = 2; i < isCrossed.length; i++)
            isCrossed[i] = false;
    }

    private static void crossOutMultiples() {
        int maxPrimeFactor = calcMaxPrimeFactor();
        for (int i = 2; i <= maxPrimeFactor; i++)
            if (notCrossed(i))
                crossOutMultiplesOf(i);
    }

    private static int calcMaxPrimeFactor() {
        // p가 소수일 때, p의 모든 배수를 지운다.
        // 따라서 지워지는 모든 배수는 인수로 p와 q를 갖는다.
        // p > 배열 크기의 sqrt(제곱근)일 경우, q는 1보다 클 수 없다.
        // 따라서 p는 이 배열의 가장 큰 소인수이고, 루프 횟수의 한계값이기도 하다.
        double maxPrimeFactor = Math.sqrt(isCrossed.length) + 1;
        return (int) maxPrimeFactor;
    }

    private static void crossOutMultiplesOf(int i) {
        for (int multiple = 2 * i; multiple < isCrossed.length; multiple += i)
            isCrossed[multiple] = true;
    }

    private static boolean notCrossed(int i) {
        return isCrossed[i] == false;
    }
    // ...
}
```

</details>

```typescript
// TypeScript 버전 4 (일부)
class PrimeGenerator {
  private static isCrossed: boolean[];
  private static result: number[];

  static generatePrimes(maxValue: number): number[] {
    if (maxValue < 2) {
      return [];
    } else {
      PrimeGenerator.initializeArrayOfIntegers(maxValue);
      PrimeGenerator.crossOutMultiples();
      PrimeGenerator.putUncrossedIntegersIntoResult();
      return PrimeGenerator.result;
    }
  }

  private static initializeArrayOfIntegers(maxValue: number): void {
    PrimeGenerator.isCrossed = new Array(maxValue + 1);
    for (let i = 2; i < PrimeGenerator.isCrossed.length; i++) {
      PrimeGenerator.isCrossed[i] = false;
    }
  }

  private static crossOutMultiples(): void {
    const maxPrimeFactor = PrimeGenerator.calcMaxPrimeFactor();
    for (let i = 2; i <= maxPrimeFactor; i++) {
      if (PrimeGenerator.notCrossed(i)) {
        PrimeGenerator.crossOutMultiplesOf(i);
      }
    }
  }

  private static calcMaxPrimeFactor(): number {
    const maxPrimeFactor = Math.sqrt(PrimeGenerator.isCrossed.length) + 1;
    return Math.floor(maxPrimeFactor);
  }

  private static crossOutMultiplesOf(i: number): void {
    for (let multiple = 2 * i; multiple < PrimeGenerator.isCrossed.length; multiple += i) {
      PrimeGenerator.isCrossed[multiple] = true;
    }
  }

  private static notCrossed(i: number): boolean {
    return PrimeGenerator.isCrossed[i] === false;
  }
  // ...
}
```

테스트는 여전히 모두 통과한다.

### 3.4 버전 5: putUncrossedIntegersIntoResult 분리

`putUncrossedIntegersIntoResult`는 두 부분으로 되어 있다.

1. 배열에서 지워지지 않은 숫자의 수를 세고, 그 크기대로 결과 배열을 만드는 부분
2. 지워지지 않은 정수를 결과 배열에 넣는 부분

첫 번째 부분을 `numberOfUncrossedIntegers`라는 별도 함수로 추출한다.

<details>
<summary>원문 Java 코드 (버전 5 — 일부)</summary>

```java
private static void putUncrossedIntegersIntoResult() {
    result = new int[numberOfUncrossedIntegers()];
    for (int j = 0, i = 2; i < isCrossed.length; i++)
        if (notCrossed(i))
            result[j++] = i;
}

private static int numberOfUncrossedIntegers() {
    int count = 0;
    for (int i = 2; i < isCrossed.length; i++)
        if (notCrossed(i))
            count++;
    return count;
}
```

</details>

```typescript
// TypeScript 버전 5 (일부)
private static putUncrossedIntegersIntoResult(): void {
  PrimeGenerator.result = new Array(PrimeGenerator.numberOfUncrossedIntegers());
  for (let j = 0, i = 2; i < PrimeGenerator.isCrossed.length; i++) {
    if (PrimeGenerator.notCrossed(i)) {
      PrimeGenerator.result[j++] = i;
    }
  }
}

private static numberOfUncrossedIntegers(): number {
  let count = 0;
  for (let i = 2; i < PrimeGenerator.isCrossed.length; i++) {
    if (PrimeGenerator.notCrossed(i)) {
      count++;
    }
  }
  return count;
}
```

테스트는 여전히 모두 통과한다.

---

## 4. 최종 점검 — 전체를 읽어보기

지금까지는 **부분**만을 리팩토링해 왔다. 이제 모든 프로그램이 **읽을 수 있는 총체로서 제대로 결합되어 있는지** 확인할 차례다. Uncle Bob은 이를 "기하학 증명을 처음부터 끝까지 읽는 것"에 비유한다.

### 4.1 발견된 문제와 수정

전체를 읽는 동안 다음 문제들을 발견했다.

| 문제 | 원래 | 변경 후 | 이유 |
|------|------|---------|------|
| 이름이 부정확 | `initializeArrayOfIntegers` | `uncrossIntegersUpTo` | 사실 초기화하는 건 정수 배열이 아닌 불리언 배열. 실제 동작은 "지워지지 않은 상태로 만드는 것" |
| 이름이 부정확 | `isCrossed` | `crossedOut` | "체크되었나"보다 "지워졌다"가 도메인 의미에 가깝다 |
| 주석이 틀림 | `calcMaxPrimeFactor` | `determineIterationLimit` | 배열 크기의 제곱근값이 꼭 소수라는 보장은 없다. 이 메소드는 **가장 큰 소인수를 계산하지 않는다** — 단지 **루프 횟수의 한계값**을 계산한다 |
| 불필요한 `+1` | `Math.sqrt(...) + 1` | `Math.sqrt(...)` | 편집증적으로 추가했던 안전 마진. 실제 한계값은 배열 크기의 제곱근보다 작거나 같은 가장 큰 소수이므로 `+1`은 불필요 |

> **Uncle Bob의 경험**: 내가 이런 사소한 이름 변경에 너무 신경을 쓰고 있다고 생각하는 독자도 있을 것이다. 그러나 **리팩토링 브라우저를 사용하면 이런 미세 조정에 거의 아무 수고도 들지 않는다**. 리팩토링 브라우저가 없더라도 단순한 '찾기 바꾸기'는 그다지 힘든 일도 아니다. 이름 변경 중에 실수로 망가뜨릴 가능성은 테스트가 상당히 줄여 준다.

### 4.2 의심이 들면 테스트를 추가하라

`+1`을 제거한 마지막 변경은 Uncle Bob을 상당히 불안하게 만들었다. 제곱근값에 숨어 있는 이론적 근거를 알지만, **아직 고려하지 않은 예외 경우(*corner case - 일반적이지 않은 경계 조건의 입력*)**가 있을 것 같다는 의심이 자꾸 들었다.

그래서 2부터 500까지의 소수 목록에 어떤 배수도 없음을 검증하는 또 다른 테스트(`testExhaustive`)를 작성했다. 새 테스트는 성공했고, 걱정은 누그러졌다.

> **핵심 통찰**: 리팩토링 중 불안감이 들면 그 직감을 무시하지 말고 **추가 테스트로 검증**한다. 추가된 테스트는 향후의 리팩토링에도 안전망으로 남는다.

### 4.3 효율성과 가독성 사이의 작은 갈등

> **Uncle Bob의 경험**: 켄트 벡과 짐 뉴커크가 이 프로그램을 리팩토링했을 때, 그들은 제곱근값과 관련된 부분을 **모두 제거**했다. 켄트의 의견은 "제곱근값이 이해하기 어렵고, 배열 크기까지 루프를 도는 프로그램이라 해도 실패하는 테스트는 없다"는 것이었다. 그러나 나는 효율성을 포기할 수 없었다. 이것이 내가 어셈블리 언어 사용자로 살아온 배경을 보여주는 것이라 생각한다.

같은 코드를 리팩토링해도 **개발자의 배경과 가치관에 따라 결과가 달라질 수 있다**. 가독성을 우선시한다면 제곱근 최적화를 제거하고, 효율성을 중시한다면 남겨둘 수 있다 — 어느 쪽이든 테스트가 통과한다면 올바른 선택이다.

---

## 5. 최종 코드

<details>
<summary>원문 Java 코드 (최종 — PrimeGenerator.java)</summary>

```java
/**
 * 이 클래스는 사용자가 지정한 최댓값까지의 소수를 생성한다.
 * 사용한 알고리즘은 에라토스테네스의 체다.
 * 2부터 시작하는 정수 배열을 받는다.
 * 지워지지 않은 첫 번째 정수를 찾아 그 배수를 모두 지운다.
 * 이것을 배열에 더 이상의 배수가 없을 때까지 계속한다.
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

    private static void uncrossIntegersUpTo(int maxValue) {
        crossedOut = new boolean[maxValue + 1];
        for (int i = 2; i < crossedOut.length; i++)
            crossedOut[i] = false;
    }

    private static void crossOutMultiples() {
        int limit = determineIterationLimit();
        for (int i = 2; i <= limit; i++)
            if (notCrossed(i))
                crossOutMultiplesOf(i);
    }

    private static int determineIterationLimit() {
        // 배열에 있는 모든 배수는 배열 크기의 제곱근보다 작거나 같은 소인수를 갖는다.
        // 그러므로 소인수보다 큰 숫자의 배수는 지울 필요가 없다.
        double iterationLimit = Math.sqrt(crossedOut.length);
        return (int) iterationLimit;
    }

    private static void crossOutMultiplesOf(int i) {
        for (int multiple = 2 * i; multiple < crossedOut.length; multiple += i)
            crossedOut[multiple] = true;
    }

    private static boolean notCrossed(int i) {
        return crossedOut[i] == false;
    }

    private static void putUncrossedIntegersIntoResult() {
        result = new int[numberOfUncrossedIntegers()];
        for (int j = 0, i = 2; i < crossedOut.length; i++)
            if (notCrossed(i))
                result[j++] = i;
    }

    private static int numberOfUncrossedIntegers() {
        int count = 0;
        for (int i = 2; i < crossedOut.length; i++)
            if (notCrossed(i))
                count++;
        return count;
    }
}
```

</details>

```typescript
// TypeScript 최종 버전
/**
 * 이 클래스는 사용자가 지정한 최댓값까지의 소수를 생성한다.
 * 사용한 알고리즘은 에라토스테네스의 체다.
 */
class PrimeGenerator {
  private static crossedOut: boolean[];
  private static result: number[];

  static generatePrimes(maxValue: number): number[] {
    if (maxValue < 2) {
      return [];
    } else {
      PrimeGenerator.uncrossIntegersUpTo(maxValue);
      PrimeGenerator.crossOutMultiples();
      PrimeGenerator.putUncrossedIntegersIntoResult();
      return PrimeGenerator.result;
    }
  }

  private static uncrossIntegersUpTo(maxValue: number): void {
    PrimeGenerator.crossedOut = new Array(maxValue + 1);
    for (let i = 2; i < PrimeGenerator.crossedOut.length; i++) {
      PrimeGenerator.crossedOut[i] = false;
    }
  }

  private static crossOutMultiples(): void {
    const limit = PrimeGenerator.determineIterationLimit();
    for (let i = 2; i <= limit; i++) {
      if (PrimeGenerator.notCrossed(i)) {
        PrimeGenerator.crossOutMultiplesOf(i);
      }
    }
  }

  private static determineIterationLimit(): number {
    // 배열에 있는 모든 배수는 배열 크기의 제곱근보다 작거나 같은 소인수를 갖는다.
    // 그러므로 소인수보다 큰 숫자의 배수는 지울 필요가 없다.
    const iterationLimit = Math.sqrt(PrimeGenerator.crossedOut.length);
    return Math.floor(iterationLimit);
  }

  private static crossOutMultiplesOf(i: number): void {
    for (let multiple = 2 * i; multiple < PrimeGenerator.crossedOut.length; multiple += i) {
      PrimeGenerator.crossedOut[multiple] = true;
    }
  }

  private static notCrossed(i: number): boolean {
    return PrimeGenerator.crossedOut[i] === false;
  }

  private static putUncrossedIntegersIntoResult(): void {
    PrimeGenerator.result = new Array(PrimeGenerator.numberOfUncrossedIntegers());
    for (let j = 0, i = 2; i < PrimeGenerator.crossedOut.length; i++) {
      if (PrimeGenerator.notCrossed(i)) {
        PrimeGenerator.result[j++] = i;
      }
    }
  }

  private static numberOfUncrossedIntegers(): number {
    let count = 0;
    for (let i = 2; i < PrimeGenerator.crossedOut.length; i++) {
      if (PrimeGenerator.notCrossed(i)) {
        count++;
      }
    }
    return count;
  }
}
```

<details>
<summary>원문 Java 코드 (최종 테스트 — TestGeneratePrimes.java)</summary>

```java
import junit.framework.TestCase;

public class TestGeneratePrimes extends TestCase {
    public TestGeneratePrimes(String name) {
        super(name);
    }

    public void testPrimes() {
        int[] nullArray = PrimeGenerator.generatePrimes(0);
        assertEquals(nullArray.length, 0);

        int[] minArray = PrimeGenerator.generatePrimes(2);
        assertEquals(minArray.length, 1);
        assertEquals(minArray[0], 2);

        int[] threeArray = PrimeGenerator.generatePrimes(3);
        assertEquals(threeArray.length, 2);
        assertEquals(threeArray[0], 2);
        assertEquals(threeArray[1], 3);

        int[] centArray = PrimeGenerator.generatePrimes(100);
        assertEquals(centArray.length, 25);
        assertEquals(centArray[24], 97);
    }

    public void testExhaustive() {
        for (int i = 2; i < 500; i++)
            verifyPrimeList(PrimeGenerator.generatePrimes(i));
    }

    private void verifyPrimeList(int[] list) {
        for (int i = 0; i < list.length; i++)
            verifyPrime(list[i]);
    }

    private void verifyPrime(int n) {
        for (int factor = 2; factor < n; factor++)
            assertTrue(n % factor != 0);
    }
}
```

</details>

```typescript
// TypeScript (Jest 스타일) 최종 테스트
describe('PrimeGenerator', () => {
  it('testPrimes - basic cases', () => {
    expect(PrimeGenerator.generatePrimes(0).length).toBe(0);

    const minArray = PrimeGenerator.generatePrimes(2);
    expect(minArray.length).toBe(1);
    expect(minArray[0]).toBe(2);

    const threeArray = PrimeGenerator.generatePrimes(3);
    expect(threeArray.length).toBe(2);
    expect(threeArray[0]).toBe(2);
    expect(threeArray[1]).toBe(3);

    const centArray = PrimeGenerator.generatePrimes(100);
    expect(centArray.length).toBe(25);
    expect(centArray[24]).toBe(97);
  });

  it('testExhaustive - 2부터 500까지의 모든 소수 검증', () => {
    for (let i = 2; i < 500; i++) {
      verifyPrimeList(PrimeGenerator.generatePrimes(i));
    }
  });
});

function verifyPrimeList(list: number[]): void {
  for (let i = 0; i < list.length; i++) {
    verifyPrime(list[i]);
  }
}

function verifyPrime(n: number): void {
  for (let factor = 2; factor < n; factor++) {
    expect(n % factor !== 0).toBe(true);
  }
}
```

---

## 6. 리팩토링의 진짜 비용과 가치

### 6.1 함수 추출의 성능 비용

한 번만 호출되는 함수를 추출해 낼 경우 **성능에 부정적인 영향을 주는 건 아닌지** 걱정하는 사람도 있을 것이다.

> **Uncle Bob의 경험**: 대부분의 경우 나는 향상된 가독성이 **몇 나노초 단위의 가치**가 있다고 생각한다. 그러나 이 몇 나노초가 문제가 되는 깊은 내부 루프도 있을 수 있다. 성능의 손해는 무시할 수 있다고 가정하고, **그것이 틀렸다는 것이 증명될 때까지 기다려 보라**고 조언하고 싶다.

### 6.2 "처음부터 동작하는데 왜?"

이번 장에서 다룬 내용에 시간을 투자할 만큼의 가치가 있는 것일까? 무엇보다도, **처음부터 이 함수는 제대로 동작하고 있었다**.

> **핵심 통찰**: 여러분이 작성한 모든 모듈과 유지보수하는 모든 모듈에 대해 항상 이런 리팩토링 과정을 적용하라. 여기에 투자하는 시간은 가까운 미래에 여러분과 다른 사람들이 들여야 할 수고에 비하면 극히 적은 것이다.

### 6.3 부엌 청소 비유

> **Uncle Bob의 경험**: 리팩토링은 저녁 식사 후에 부엌을 청소하는 것과 비슷하다. 처음으로 생략하고 넘어갔을 때는 저녁 식사를 좀 더 빨리 끝마칠 수 있다. 하지만 깨끗한 접시와 깨끗한 작업공간의 부족 때문에 다음 날 저녁 준비는 훨씬 오래 걸릴 것이다. 그래서 다시 한 번 청소를 안 하고 넘어가게 된다. 실제로, 청소를 안 하고 넘어가면 오늘 저녁 식사는 항상 빨리 끝낼 수 있다. 하지만 문제는 계속해서 쌓인다. 결국에는 원하는 주방기구를 찾고, 딱딱하게 마른 음식을 접시에서 파내고, 북북 문질러 닦아 요리할 수 있는 환경을 만드는 데 과도한 시간을 쓰게 될 것이다. 그리고 저녁 식사는 영원히 끝나지 않는다.
>
> 크게 보면 청소를 생략한다고 해서 저녁 식사를 빨리 끝낼 수 있게 되는 것은 아니다.

리팩토링의 목표는 **매일 코드를 청소하는 것**이다. 문제가 쌓이고 쌓여서 오랜 시간 동안 축적된 것을 파내고 문질러 닦아야 하는 상황을 원하지 않는다. **최소한의 노력으로 시스템을 확장하고 수정할 수 있기를 바란다**. 이를 위한 가장 중요한 요소는 **코드의 깔끔함**이다.

> **핵심 통찰**: 이 책에서 소개하는 모든 원칙과 패턴도 그것이 적용된 코드가 엉터리라면 무의미하다. 원칙과 패턴에 신경 쓰기 전에, **간결하고 분명한 코드**를 만드는 데 신경을 써야 한다.

---

## 7. 리팩토링의 핵심 원리 정리

### 7.1 리팩토링의 안전한 사이클

```
┌─────────────────────────────────────────────────┐
│  1. 작은 변경 한 가지를 한다                      │
│       ↓                                          │
│  2. 테스트를 실행한다                             │
│       ↓                                          │
│  3. 모두 통과 → 다음 변경으로                    │
│     실패 → 즉시 되돌리고 더 작게 쪼개기          │
│       ↓                                          │
│  반복: "이 상태에서도 테스트는 전부 동작한다"     │
└─────────────────────────────────────────────────┘
```

### 7.2 이 장에서 사용한 리팩토링 기법

| 기법 | 무엇을 하는가 | 사용 예 |
|------|---------------|---------|
| **메소드 추출(Extract Method)** | 큰 함수를 의미 단위로 작은 함수로 쪼개기 | `generatePrimes` → 3개의 단계 메소드 |
| **변수 이름 변경(Rename Variable)** | 단일 문자/모호한 이름을 의미 있는 이름으로 | `s` → `f.length`, `f` → `isCrossed` → `crossedOut` |
| **메소드 이름 변경(Rename Method)** | 함수가 실제로 하는 일을 반영하는 이름으로 | `initializeSieve` → `uncrossIntegersUpTo` |
| **불리언 의미 반전** | 이중 부정을 없애기 위해 의미 자체를 뒤집기 | `unCrossed`(이중 부정 발생) → `isCrossed`(반전) |
| **임시 함수 도입** | `==`/`!=` 같은 비교를 의미 있는 함수로 감싸기 | `isCrossed[i] == false` → `notCrossed(i)` |
| **주석을 함수로 승격** | 설명이 필요한 코드 블록을 의도가 드러나는 함수명으로 | 제곱근 계산 → `determineIterationLimit` |
| **불필요한 코드 제거** | 편집증으로 추가했던 안전 마진 등 정리 | `Math.sqrt(...) + 1` → `Math.sqrt(...)` |

---

## 요약

- **리팩토링은 외부 행위를 바꾸지 않으면서 내부 구조를 개선하는 과정**이다(마틴 파울러)
- 모든 모듈에는 세 가지 기능이 있다 — **동작 / 변경 가능성 / 의사소통**. 변경하기 어렵거나 읽을 수 없는 모듈은 동작하더라도 망가진 것이다
- 리팩토링의 안전망은 **자동화된 테스트**다. "이 상태에서도 테스트는 전부 동작한다"를 매 단계마다 확인한다
- 소수 생성기 예제는 거대한 단일 함수를 다음 단계로 변모시킨다:
  - 버전 1: 단일 문자 변수와 주석으로 가득한 큰 함수
  - 버전 2: 3개의 의미 단위 메소드로 추출 (`initializeSieve`/`sieve`/`loadPrimes`)
  - 버전 3: 의미 있는 함수명으로 변경 (`crossOutMultiples` 등), 불필요한 변수 제거
  - 버전 4: 이중 부정 제거, 비교를 `notCrossed` 함수로 감싸기, 제곱근 계산을 별도 함수로
  - 버전 5: `putUncrossedIntegersIntoResult` 내부에서 `numberOfUncrossedIntegers` 추출
  - 최종: 부정확한 이름 `initializeArrayOfIntegers`→`uncrossIntegersUpTo`, `isCrossed`→`crossedOut`, `calcMaxPrimeFactor`→`determineIterationLimit`
- 작은 단계마다 테스트로 검증한다. **의심이 들면 새로운 테스트를 추가**해서 그 영역을 안전망으로 덮는다
- 함수 추출의 **성능 비용**은 무시할 수 있다고 가정하라 — 틀렸다는 것이 증명될 때까지
- 리팩토링은 **부엌 청소**와 같다. 매일 청소하지 않으면 결국 저녁 식사는 영원히 끝나지 않는다
- 원칙과 패턴에 신경 쓰기 전에 **간결하고 분명한 코드**를 만드는 데 먼저 신경을 써야 한다

---

## 참고문헌

1. Fowler, Martin. *Refactoring: Improving the Design of Existing Code*. Reading, MA: Addison-Wesley, 1999.
