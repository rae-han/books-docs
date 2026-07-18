# Chapter 3: Code, Objects, Functions, Generators, Iterators, and LISP (코드, 객체, 함수, 제너레이터, 이터레이터, LISP)

## 핵심 질문

명령형 코드로 작성하는 제너레이터와 객체지향적 반복자 패턴의 구현체인 이터레이터, 리스트 프로세싱(LISP의 핵심 개념)은 서로 깊은 관계를 맺고 있다. 이 세 가지가 어떻게 상호 협력하여 고도의 추상화를 가능하게 하며, IP(명령형), OOP(객체지향), FP(함수형) 세 패러다임이 조화를 이루는 코드를 만들 수 있을까? 또한 지연 평가의 실행 순서와 효율성을 이해하면 find, every, some 같은 고차 함수를 어떻게 함수형으로 구현할 수 있을까?

---

1장과 2장에서 다룬 개념들을 Generator: Iterator: LISP = IP: OOP: FP의 관점에서 정리하면 다음과 같다.

- **제너레이터는 명령형 코드로 이터레이터 생성**: 제너레이터 함수는 명령형 코드로 이터레이터를 만들 수 있는 수단이다. `yield` 지점에서 함수 실행을 일시 정지하고 재개할 수 있어 제너레이터의 코드를 리스트 단위로 지연 평가하는 효과를 낸다. 이는 '코드가 리스트이고 리스트가 코드'라는 LISP적 사고와 맞닿아 있다.
- **이터레이터는 반복자 패턴의 구현체**: 이터레이터는 컬렉션 형태의 데이터를 일반화된 패턴으로 순회하는 객체다. 필요할 때마다 값을 평가하는 지연성(*Laziness*)을 가지므로 유한한 컬렉션뿐 아니라 무한 시퀀스도 처리할 수 있다.
- **이터러블 이터레이터는 명령형, 객체지향적, 함수형으로 다룰 수 있음**: 명령형으로는 `next()` 메서드를 실행하며 `while`문으로 순회하거나 `for...of`문이나 전개 연산자(`...`)로 다룰 수 있다. 객체지향적으로는 이터러블 이터레이터를 다루는 클래스를 만들거나 이터레이터 내부에서 다른 이터레이터와 통신하는 이터레이터를 만들 수 있다. 함수형으로는 고차 함수를 통해 이터레이터와 각 요소를 처리할 함수를 전달하는 방식으로 다루며 이터레이션 로직을 함수 조합 형태로 구현하고 지연 평가와 리스트 프로세싱을 극대화한다.
- **이터레이터 생성 방식의 다양화**: 궁극적으로 이터레이터는 다음 세 가지 방식으로 만들 수 있으며 이들은 서로 1:1:1로 대체할 수 있다.
  - **명령형 방식(IP)**: 제너레이터를 통한 이터레이터 생성
  - **객체지향적 방식(OOP)**: 이터레이터 객체 직접 구현
  - **함수형 방식(FP)**: 리스트 프로세싱 함수 조합으로 이터레이터 생성

---

## 1. 코드가 곧 데이터 - 로직이 담긴 리스트

1장과 2장에서는 멀티패러다임 언어에서 함수형 프로그래밍과 리스트 프로세싱, 메타프로그래밍, 함수형 타입 시스템을 적용하는 과정을 다뤘다. 이번 장에서는 실제로 일상에서 마주칠 만한 문제들을 해결하는 로직을 함수형으로 작성하면서 그동안의 이야기를 실질적인 세계로 연결하려 한다. 그 시작은 명령형 코드를 리스트 프로세싱 함수로 대체하는 것이다.

### 1.1 [for, i++, if, break] - 코드를 리스트로 생각하기

코드를 리스트로 바라보는 사고방식은 프로그래밍 패러다임을 확장하는 강력한 도구다. 함수형 프로그래밍에서는 코드가 곧 데이터이고 데이터가 곧 코드인 특성을 이용하여 더 읽기 쉽고 유지보수하기 좋은 코드를 작성할 수 있다.

이번 절에서는 `for`, `i++`, `if`, `break`와 같은 명령형 코드를 함수형 리스트 프로세싱 함수로 변환하면서 코드가 어떻게 리스트로 처리될 수 있는지 탐구해 보겠다.

#### 명령형으로 작성한 n개의 홀수를 제곱하여 모두 더하는 함수

다음은 n개의 홀수를 제곱하여 모두 더하는 함수다. 코드를 실행하면 `list` 배열에서 처음 3개의 홀수(1, 3, 5)를 선택하고 각 홀수의 제곱(1², 3², 5²)을 계산하여 더한다. 최종 결과는 1 + 9 + 25 = 35가 출력된다.

```typescript
// [코드 3-1] n개의 홀수를 제곱하여 모두 더하기
function sumOfSquaresOfOddNumbers(limit: number, list: number[]): number {
  let acc = 0;
  for (const a of list) {
    if (a % 2 === 1) {
      const b = a * a;
      acc += b;
      if (--limit === 0) break;
    }
  }
  return acc;
}

console.log(
  sumOfSquaresOfOddNumbers(3, [1, 2, 3, 4, 5, 6, 7, 8, 9])
);
// 35
```

이 코드가 하는 일을 목록으로 정리하면 다음과 같다.

- **순회**: `for (const a of list)`를 통해 `list` 배열의 각 요소를 순회한다.
- **홀수 검사**: `if (a % 2 === 1)` 조건문을 사용하여 `a`가 홀수인지 검사한다. 홀수인 경우에만 다음 단계를 실행한다.
- **제곱 계산**: `const b = a * a;`를 통해 홀수 `a`의 제곱을 계산하여 `b`에 저장한다.
- **누적 합계 갱신**: `acc += b;`를 통해 누적 합계에 `b`를 더한다.
- **길이 검사 및 종료**: `if (--limit === 0) break;` 조건문을 사용하여 `limit`를 감소시키고 `limit`가 0이 되면 반복문을 종료한다.
- **결과 반환**: `return acc;`를 통해 최종 누적 합계를 반환한다.

#### if를 filter로 대체

`if` 조건문은 `filter` 함수로 대체할 수 있다.

```typescript
// [코드 3-2] if를 filter로 대체한 코드
function sumOfSquaresOfOddNumbers(limit: number, list: number[]): number {
  let acc = 0;
  for (const a of filter(a => a % 2 === 1, list)) {
    const b = a * a;
    acc += b;
    if (--limit === 0) break;
  }
  return acc;
}

console.log(
  sumOfSquaresOfOddNumbers(3, [1, 2, 3, 4, 5, 6, 7, 8, 9])
);
// 35
```

[코드 3-1]의 `list` 부분을 `filter(...)`로 대체하고 `if (a % 2 === 1) {}`의 조건을 `filter`의 보조 함수로 가져와 적용한 다음 `if (a % 2 === 1) {}`를 제거했다. 이제 `filter(a => a % 2 === 1, list)`가 홀수만 남기므로 제곱과 합산을 계산하는 `for`문 내부 코드가 한 단계 간결해졌다.

이 예제에서는 `list`에서 `a`를 꺼내 `if (a % 2 === 1) {}`로 코드의 실행을 제어하는 '코드 문장'을 `filter`가 적용된 '리스트'로 변경했다. `for...of`문의 내부 코드 입장에서는 `a`가 필터링된 결과인지 신경 쓸 필요 없이 그저 요소인 `a`를 제곱하고 합산하는 일만 한다.

다시 한번 정리하면 다음과 같다.

- 곳곳에 있던 코드 문장이 리스트 프로세싱 함수 실행으로 대체되었다.
- `filter(a => a % 2 === 1, list)`는 필터 로직을 수행하는 코드인 동시에 리스트다.
- 내부 로직에서 조건문이 제거되어 코드가 더욱 명확하고 단순해졌다.

#### 값 변화 후 변수 할당을 map으로 대체

이번에는 `map`을 활용하여 값 변화 후 변수 할당을 제거해 보겠다.

```typescript
// [코드 3-3] map으로 대체한 코드
function sumOfSquaresOfOddNumbers(limit: number, list: number[]): number {
  let acc = 0;
  for (const a of map(a => a * a, filter(a => a % 2 === 1, list))) {
    acc += a;
    if (--limit === 0) break;
  }
  return acc;
}

console.log(
  sumOfSquaresOfOddNumbers(3, [1, 2, 3, 4, 5, 6, 7, 8, 9])
);
// 35
```

예제에서 `map`은 변수를 선언하고 제곱한 값을 할당하는 코드 `const b = a * a;`를 대체하는 역할을 한다. 결과적으로 `map(a => a * a, filter(a => a % 2 === 1, list))`는 홀수만 제곱한 리스트를 만드는 지연된 이터레이터가 된다. 이를 `for...of`문을 통해 순회하면서 제곱이 적용된 `a`를 뽑아내고 있다.

역시 코드 문장들이 리스트와 함수들의 조합으로 바뀌고 있다. 이러한 개념을 LISP 문법으로 표현하면 더욱 명확해진다. LISP 문법이 코드를 리스트로 다루는 개념을 더 잘 나타내기 때문이다.

```scheme
; [코드 3-4] Scheme 코드
(define list '(1 2 3 4 5))
(define (square x) (* x x))
(map square (filter odd? list))
; (1 9 25)

; JavaScript
; map(square, filter(isOdd, list))
```

[코드 3-4]를 보면 리스트를 생성하는 `(1 2 3 4 5)`와 같은 문법과 곱하기 연산자(`*`)로 `x`의 제곱을 구하는 `(* x x)`와 같은 문법이 작은 따옴표(`'`)를 빼고는 동일함을 볼 수 있다. 즉 LISP에서는 숫자 배열과 같은 데이터를 정의하는 문법도 리스트로 표현되며, 제곱하는 계산식 또한 리스트로 표현된다. 다시 말해 함수 호출도 리스트로 표기된다. `(* x x)`라는 리스트는 `*` 하나와 `x` 두 개를 요소로 가지며, 리스트인 코드를 평가할 때 `x`의 제곱으로 계산된다.

같은 시각으로 `(filter odd? list)`를 보면 `filter`와 `odd?`, `list`가 들어 있는 리스트임을 알 수 있다. 여러 단계로 중첩된 리스트를 풀면 다음과 같다.

```scheme
; [코드 3-4a] Scheme 코드
(map (lambda (x) (* x x)) (filter odd? '(1 2 3 4 5)))
```

LISP에서는 이러한 리스트이자 코드이자 데이터를 평가하는 식으로 프로그램이 실행된다. 즉 리스트는 코드이고, 코드는 리스트이며, 중첩된 리스트는 알고리즘이자 로직이다. LISP의 문법은 이러한 철학을 잘 반영하며 더욱 우아하게 표현해 낸다.

이 책에서 주 언어로 사용하는 타입스크립트는 LISP와 문법만 약간 다를 뿐 이터러블과 이터레이터를 활용한 이터레이션 프로토콜을 기반으로 이러한 패러다임을 그대로 적용할 수 있다.

#### break를 take로 대체

이제 `if (--limit === 0) break;` 부분을 `take`로 대체해 보겠다.

```typescript
// [코드 3-5] take로 대체한 코드
function* take<A>(limit: number, iterable: Iterable<A>): IterableIterator<A> {
  const iterator = iterable[Symbol.iterator]();
  while (true) {
    const { value, done } = iterator.next();
    if (done) break;
    yield value;
    if (--limit === 0) break;
  }
}

function sumOfSquaresOfOddNumbers(limit: number, list: number[]): number {
  let acc = 0;
  for (const a of take(limit, map(a => a * a, filter(a => a % 2 === 1, list)))) {
    acc += a;
  }
  return acc;
}

console.log(
  sumOfSquaresOfOddNumbers(3, [1, 2, 3, 4, 5, 6, 7, 8, 9])
);
// 35
```

`take` 함수는 주어진 이터러블에서 지정된 `limit`만큼의 요소를 반환하는 지연된 리스트인 이터러블 이터레이터를 반환한다. 여기서는 처음 3개의 요소만 반환한다.

`take(limit, map(a => a * a, filter(a => a % 2 === 1, list)))`는 모든 연산이 지연되어 아무런 연산도 이루어지지 않는다. `for...of`문에서 `a`를 처음 뽑을 때 1이 들어오고, 두 번째 뽑을 때 9, 마지막으로 25가 들어오면서 반복문이 종료된다.

이때 코드에서 반복문을 빠져나가는 `break`문을 제거했음에도 시간 복잡도가 동일하다는 사실에 주목해야 한다. `break`는 필요한 만큼만 코드가 반복되도록 제어하여 로직의 효율성을 높이는 키워드다. 여기서는 `take`를 통해 `break`와 같은 제어문마저도 리스트로 사고할 수 있음을 확인했다. 이러한 접근을 가능하게 하는 핵심은 지연 평가다. 지연 평가는 3절에서 더 자세히 알아보겠다.

#### 합산을 reduce로 대체

마지막으로 `reduce` 함수를 사용하여 합산하는 명령형 코드를 대체해 보겠다.

```typescript
// [코드 3-6] reduce로 대체한 코드
const sumOfSquaresOfOddNumbers = (limit: number, list: number[]): number =>
  reduce((a, b) => a + b, 0,      // add(add(1, 9), 25)
    take(limit,                     // [(1), (9), (25)]
      map(a => a * a,               // [(1), (9), (25), (49), (81)]
        filter(a => a % 2 === 1, list)))); // [(1), (3), (5), (7), (9)]

console.log(
  sumOfSquaresOfOddNumbers(3, [1, 2, 3, 4, 5, 6, 7, 8, 9])
);
// 35
```

`reduce`는 지연된 리스트를 평가하면서 요소를 뽑아낸다. 첫 번째 요소 1과 두 번째 요소 9를 더해 누적하고, 마지막으로 세 번째 요소 25를 더해 최종 결과로 35를 만든다.

#### 체이닝으로 변경

`take`는 자주 사용되는 함수이므로 `FxIterable`에 `take` 메서드를 추가하여 읽기 좋은 순서로 표현해 보겠다.

```typescript
// [코드 3-7] 체이닝으로 변경한 코드
class FxIterable<A> {
  constructor(private iterable: Iterable<A>) {}
  // ... 메서드 생략 ...
  take(limit: number): FxIterable<A> {
    return fx(take(limit, this)); // new FxIterable(take(limit, this));
  }
}

// 함수형 코드:
const sumOfSquaresOfOddNumbers = (limit: number, list: number[]): number =>
  fx(list)                        // [1, 2, 3, 4, 5, 6, 7, 8, 9]
    .filter(a => a % 2 === 1)     // [(1), (3), (5), (7), (9)]
    .map(a => a * a)              // [(1), (9), (25), (49), (81)]
    .take(limit)                  // [(1), (9), (25)]
    .reduce((a, b) => a + b, 0);  // add(add(1, 9), 25)

console.log(
  sumOfSquaresOfOddNumbers(3, [1, 2, 3, 4, 5, 6, 7, 8, 9])
);
// 35
```

지금까지 명령형 코드로 구현된 함수를 함수형 프로그래밍 방식으로 변경해 보았다. 코드가 선언적으로 변했고 가독성이 크게 향상되었다. `filter`, `map`, `take`, `reduce`와 같은 선언적인 함수명을 통해 각 코드 부분의 목적을 쉽게 파악할 수 있고, 위에서부터 아래로 읽으면서 어떤 일이 이루어지는지 파악하기 좋아졌다.

결과를 보면 코드의 각 부분을 리스트 프로세싱 함수들로 대체했고, 이는 결국 중첩된 리스트를 만드는 것과 같다.

리스트 프로세싱은 이처럼 (명령형) 코드 라인들을 리스트로 변환한다. 코드를 값(리스트)으로 다루고 함수를 값(일급 함수)으로 다루어 작은 코드들의 목록으로 복잡한 문제를 해결해 나가는 것, 이것이 함수형 프로그래밍과 리스트 프로세싱의 방법이다.

### 1.2 현대 언어에서 리스트 프로세싱

현대 프로그래밍 언어들은 지금까지 살펴본 리스트 프로세싱의 철학을 따르는 함수형 프로그래밍을 지원하고 있다. [코드 3-7]에서 완성한 함수형 코드를 다른 언어들로 구현하면서 이를 확인해 보겠다.

```clojure
;; [코드 3-8] 클로저로 구현
(defn square [x]
  (* x x))

(defn sumOfSquaresOfOddNumbers [limit list]
  (->> list
    (filter odd?)
    (map square)
    (take limit)
    (reduce +)))

(println (sumOfSquaresOfOddNumbers 3 [1 2 3 4 5 6 7 8 9]))
; 35
```

클로저는 함수형 프로그래밍 패러다임에 중점을 둔 언어다. `->>` 는 파이프라인으로 코드를 표현할 수 있게 하는 매크로다. `->>` 는 나중에 리스트를 받을 준비가 된 시퀀스인 `(filter odd?)`, `(map square)` 등의 코드들을 받아 앞에서부터 `list`에 적용하고 그 결과를 연속적으로 함수들에 적용한다. LISP답게 `+` 기호를 `reduce`의 누적 함수로 사용하도록 인자로 전달할 수 있다.

```kotlin
// [코드 3-9] 코틀린으로 구현
fun sumOfSquaresOfOddNumbers(limit: Int, list: List<Int>): Int {
  return list.asSequence()
    .filter { it % 2 == 1 }
    .map { it * it }
    .take(limit)
    .fold(0) { a, b -> a + b }
}

fun main() {
  val result = sumOfSquaresOfOddNumbers(3, listOf(1, 2, 3, 4, 5, 6, 7, 8, 9))
  println(result) // 35
}
```

코틀린은 `Iterable` 인터페이스를 통해 이터레이션을 지원하고 `asSequence()`를 사용해 지연 연산을 시작한다. 코틀린의 표준 라이브러리는 높은 수준의 함수형 프로그래밍을 지원하며 `filter`, `map`, `take`, `reduce`, `fold`와 같은 고차 함수를 제공한다. 또한 간결하고 독특한 람다식을 지원하며 `it` 키워드를 사용해 현재 요소를 나타낼 수 있다.

```swift
// [코드 3-10] 스위프트로 구현
func sumOfSquaresOfOddNumbers(limit: Int, list: [Int]) -> Int {
  return list.lazy
    .filter { $0 % 2 == 1 }
    .map { $0 * $0 }
    .prefix(limit)       // take와 동일한 함수
    .reduce(0, +)        // 스위프트의 reduce는 첫 번째 인자가 초깃값이며 생략할 수 없음
}

print(sumOfSquaresOfOddNumbers(limit: 3, list: [1, 2, 3, 4, 5, 6, 7, 8, 9]))
// 35
```

스위프트에서는 `lazy` 키워드를 사용하여 지연 연산을 시작한다. `reduce` 함수의 누적 함수로 `+` 연산자를 사용할 수 있는 점도 매력적이다.

```scala
// [코드 3-11] 스칼라로 구현
object Main extends App {
  def sumOfSquaresOfOddNumbers(limit: Int, list: List[Int]): Int = {
    list.to(LazyList)
      .filter(_ % 2 == 1)
      .map(a => a * a)
      .take(limit)
      .foldLeft(0)(_ + _)
  }

  println(sumOfSquaresOfOddNumbers(3, List(1, 2, 3, 4, 5, 6, 7, 8, 9))) // 35
}
```

스칼라는 `LazyList`를 통해 지연 평가 방식을 지원한다. 스칼라의 람다식에서는 언더스코어(`_`)를 사용해 현재 요소를 간단히 나타낼 수 있으며, `foldLeft(0)(_ + _)`와 같은 간결한 문법도 지원한다.

```csharp
// [코드 3-12] C#으로 구현
using System;
using System.Collections.Generic;
using System.Linq;

public class ListTest
{
  public static void Main()
  {
    List<int> list = new List<int> { 1, 2, 3, 4, 5, 6, 7, 8, 9 };
    int result = SumOfSquaresOfOddNumbers(3, list);
    Console.WriteLine(result); // 35
  }

  static int SumOfSquaresOfOddNumbers(int limit, List<int> list)
  {
    return list.Where(a => a % 2 == 1)
      .Select(a => a * a)
      .Take(limit)
      .Aggregate(0, (a, b) => a + b);
  }
}
```

C#은 LINQ(*Language Integrated Query - 프로그래밍 언어에 데이터 질의 기능을 통합한 기술*)를 통해 높은 수준의 함수형 프로그래밍을 지원한다. `Where`, `Select`, `Take`, `Aggregate`와 같은 고차 함수들은 각각 함수형 프로그래밍의 `filter`, `map`, `take`, `reduce`에 해당한다.

특히 LINQ는 일부 기능을 SQL과 유사한 구문으로 작성할 수 있도록 지원한다.

```csharp
// [코드 3-13] C# SQL 스타일 문법
static int SumOfSquaresOfOddNumbers(int limit, List<int> list)
{
  var query = from num in list
              where num % 2 == 1
              select num * num;
  return query.Take(limit).Aggregate(0, (acc, a) => acc + a);
}
```

C#은 2007년 11월 LINQ를 도입했다. C#은 오래전부터 함수형 패러다임을 통합한 선도적인 멀티패러다임 언어다.

```java
// [코드 3-14] 자바로 구현
import java.util.Arrays;
import java.util.List;

public class Main {
  public static void main(String[] args) {
    List<Integer> list = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9);
    int result = sumOfSquaresOfOddNumbers(3, list);
    System.out.println(result); // 35
  }

  public static int sumOfSquaresOfOddNumbers(int limit, List<Integer> list) {
    return list.stream()
      .filter(a -> a % 2 == 1)
      .map(a -> a * a)
      .limit(limit)          // take와 동일
      .reduce(0, Integer::sum);
  }
}
```

자바는 Stream API를 통해 함수형 프로그래밍을 지원한다. `filter`, `map`, `limit`, `reduce`와 같은 스트림 메서드를 사용하여 컬렉션을 변환하고 처리할 수 있다.

> **참고**: 각 언어에서 `reduce`가 초깃값을 처리하는 방식에는 약간의 차이가 있다. 이는 개발자가 예상하지 못한 상황을 최대한 예방하거나 조기에 감지할 수 있도록 언어가 설계되었기 때문이다. 빈 배열, 빈 스트림, 빈 이터러블 등 비어 있는 컬렉션을 런타임에서 만났을 때 발생할 수 있는 에러에 대해 언어가 개발자에게 처리 방법을 제안하는 것이다. 타입스크립트와 자바스크립트의 `reduce`에서는 초깃값이 없을 때 빈 배열이나 빈 이터러블을 만나면 에러를 전파한다.

### 1.3 언어를 넘어 적용 가능한 개념, 패러다임

앞에서 살펴본 다양한 언어들은 각기 고유한 이터레이션 프로토콜이나 유사한 메커니즘을 바탕으로 지연 평가를 지원한다. 이를 통해 함수형 프로그래밍의 원칙을 언어 차원에서 구현함으로써 코드 가독성과 유지보수성을 높이고 데이터 처리 효율을 극대화할 수 있다.

결국 객체지향, 명령형, 함수형 패러다임을 결합한 멀티패러다임적 사고와 문제 해결 능력은 특정 언어에 국한되지 않는다. 타입스크립트, 코틀린, 스위프트, 스칼라, C#, 자바 등 강력한 타입 시스템과 타입 추론을 지원하는 이들 언어에서는 클래스와 인터페이스, 이터레이션 프로토콜, 함수형 고차 함수를 모두 활용할 수 있다. 이 책에서 다루는 개념과 원칙 역시 이러한 언어 전반에 적용할 수 있으며, 다양한 환경에서 더욱 안전하고 효율적인 코드를 구현하는 데 기여할 것이다.

---

## 2. 하스켈로부터 배우기

하스켈(*Haskell - 순수 함수형 프로그래밍 언어*)은 순수 함수형 프로그래밍 언어로 평가되며 함수형 패러다임을 잘 반영하도록 설계된 문법을 가지고 있다. 하스켈은 순수 함수와 함수 합성을 강조하고 커링이 기본이며 지연 평가를 지원하고 부수 효과를 특별하게 관리한다. 또한 강력한 타입 시스템과 타입 추론, 대수적 데이터 타입, 높은 다형성을 지원하는 타입 클래스 등 함수형 프로그래밍에 특화되고 차별화된 많은 기능을 제공한다.

> **참고**: 3.4절에서 타입스크립트의 `find` 함수와 옵셔널 값 처리를 다룰 때, 좀 더 폭넓은 시각을 제공하고자 하스켈 예제와 관련 내용을 포함했다. 이를 효과적으로 이해하려면 하스켈의 문법과 특징을 먼저 알아야 해서 이번 절을 하스켈 내용으로 준비했다.

### 2.1 하스켈의 함수와 함수 시그니처

하스켈에서 함수 시그니처는 함수형 프로그래밍의 기본 개념을 이해하는 데 중요한 단서를 제공한다.

```haskell
-- [코드 3-15] 하스켈의 square 함수
square :: Int -> Int
square x = x * x
```

여기서 `square :: Int -> Int`는 `square` 함수가 `Int` 타입의 인자를 받아 `Int` 타입을 반환함을 의미한다. `::`는 타입 선언을 나타내며, `square x = x * x`에서 `square`는 함수명, `x`는 매개변수, `=`는 함수 정의와 오른쪽 식의 결과 반환을 뜻한다.

이 코드를 타입스크립트로 표현하면 다음과 같다.

```typescript
// [코드 3-16] 타입스크립트의 square 함수
function square(x: number): number {
  return x * x;
}

// [코드 3-17] 타입스크립트로 함수 타입 정의
type Square = (x: number) => number;
const square: Square = x => x * x;
```

하스켈과 타입스크립트 모두 함수 시그니처를 명시함으로써 함수의 입출력 타입을 분명히 할 수 있다.

### 2.2 언어 차원에서 지원하는 커링

하스켈은 언어 차원에서 커링(*Currying - 여러 인자를 받는 함수를 인자 하나씩 받는 함수들의 연쇄로 표현하는 기법*)을 지원하므로 여러 인자를 받는 함수를 자연스럽게 커링된 형태로 다룰 수 있다.

```haskell
-- [코드 3-18] add 함수
add :: Int -> Int -> Int
add x y = x + y

-- [코드 3-19] add 5 부분 적용
addFive :: Int -> Int
addFive = add 5
```

`addFive`는 `add` 함수에 5를 부분 적용(*Partial Application*)한 결과다. 이로써 `addFive`는 `Int -> Int` 타입의 함수이며 새로운 인자 하나를 받으면 그에 따른 결과를 반환하는 함수가 된다.

```haskell
-- [코드 3-20] add 실행 완료
main :: IO ()
main = do
  print (addFive 10)  -- 출력: 15
  print (add 3 7)     -- 출력: 10
  print (3 `add` 7)   -- 출력: 10
```

`addFive 10`은 `add` 함수에 5를 먼저 부분 적용하여 `(add 5)` 형태의 함수를 만든 뒤 여기에 10을 전달해 15를 결과로 얻는다. 또한 하스켈에서는 함수 호출을 중위(*Infix*) 연산자로 표현할 수 있어 `` 3 `add` 7 ``과 `add 3 7`은 동일한 결과를 만든다.

하스켈은 모든 함수 호출에 커링을 기본 적용한다. 예를 들어 `add :: Int -> Int -> Int`는 사실상 `add :: Int -> (Int -> Int)`와 동일한 의미다. 즉 `add`는 `Int` 하나를 받아 `(Int -> Int)` 형태의 새로운 함수를 반환한다.

### 2.3 main 함수와 IO

하스켈에서는 모든 프로그램이 `main` 함수로 시작한다. `main` 함수는 `IO` 타입을 반환해야 한다. `IO` 타입은 입출력 작업을 수행할 수 있도록 설계된 특별한 타입이다.

- `main :: IO ()`는 함수의 타입 시그니처이며, `main` 함수가 `IO ()` 타입을 반환한다는 의미다. `IO`는 입출력 작업을 나타내는 타입이고 `()`는 `main` 함수가 특별히 반환할 값이 없다는 의미다.
- `main =`는 함수 정의의 시작 부분으로 인자가 없다는 의미다.
- `do` 구문을 사용하면 여러 개의 IO 액션을 순차적으로 실행할 수 있다.

`IO`는 하스켈에서 입출력 작업을 나타내는 타입이다. 순수 함수형 언어인 하스켈에서는 입출력과 같은 부수 효과를 관리하기 위해 `IO` 타입을 사용한다. 하스켈에서 어떤 함수가 `IO`를 반환한다면 이는 해당 함수가 내부적으로 입출력 등의 부수 효과를 일으킬 수 있음을 타입 차원에서 명시하는 것이다. 이로써 '순수 함수(`a -> b`)'와 'IO 함수(`a -> IO b`)'를 명확히 구분할 수 있고, 부수 효과로 인한 예측 불가능성을 최소화할 수 있다.

정리하자면 `IO`는 하스켈에서 '이 함수는 입출력, 상태 변경 등 순수하지 않은 일을 할 수 있다'는 것을 선언하는 타입이다. 이를 통해 순수 함수와 부수 효과 함수를 엄격히 구분하고 프로그램의 예측 가능성과 안전성을 높인다.

#### Unit 타입 ()와 타입스크립트의 void

하스켈에서 `()`는 유일한 값을 갖는 Unit 타입으로 '의미 없는 값'을 나타내며 함수가 유의미한 결과를 반환하지 않을 때 사용한다. 타입스크립트에서는 함수의 반환 타입으로 `void`를 사용하여 비슷한 의도를 드러낼 수 있다. 비록 하스켈의 `()`와 타입스크립트의 `void`는 구현 방식이나 정적 분석 수준에서 차이가 있지만, 둘 다 '의미 있는 결과를 반환하지 않는 함수'를 표현할 때 사용된다는 점에서 개념적으로 유사한 역할을 한다.

### 2.4 head, map, filter, foldl 함수 시그니처

하스켈에서 `head`, `map`, `filter`, `foldl`과 같은 함수의 시그니처를 어떻게 표현하는지 확인해 보자.

#### head 함수 시그니처

`head` 함수는 리스트의 첫 번째 요소를 반환한다. 여기서 `a`는 제네릭 타입으로 어떤 타입이든 받아들일 수 있음을 의미한다.

```haskell
-- [코드 3-21] head 함수
head :: [a] -> a
```

타입스크립트에서는 다음과 같이 제네릭 타입 파라미터 `<A>`를 사용하여 동일한 역할을 수행할 수 있다.

```typescript
// [코드 3-21a] 타입스크립트 head 함수
type Head = <A>(arr: A[]) => A;
// 또는
type Head = <A>(iterable: Iterable<A>) => A;
```

#### map, filter, foldl 함수 시그니처

```haskell
-- [코드 3-22] map 함수
map :: (a -> b) -> [a] -> [b]

-- [코드 3-23] filter 함수
filter :: (a -> Bool) -> [a] -> [a]

-- [코드 3-24] foldl 함수
foldl :: (b -> a -> b) -> b -> [a] -> b
```

`map`은 리스트 `[a]`의 각 요소에 주어진 함수 `(a -> b)`를 적용하여 새로운 리스트 `[b]`를 반환한다. `filter`는 리스트의 각 요소에 대해 주어진 조건 `(a -> Bool)`을 검사하여 조건을 만족하는 요소만을 포함하는 새로운 리스트를 반환한다. `foldl`에서 `(b -> a -> b)`는 누적 함수(*Accumulator Function*)의 타입 시그니처를 의미하며, 이 함수는 현재 누적 값(`b`)과 리스트의 현재 요소(`a`)를 받아 새로운 누적 값(`b`)을 반환하는 형태다.

하스켈에서는 제네릭 타입 변수로 `a`, `b`와 같은 단일 문자 이름을 주로 사용한다. 이러한 단순하고 일관된 표기법 덕분에 `foldl`, `map`과 같은 고차 함수를 매우 간결하게 표현할 수 있다.

### 2.5 함수 합성 - . 연산자와 $ 연산자

`.` 연산자는 함수를 합성하는 데 사용한다. 예를 들어 `f . g . h`는 세 개의 함수를 합성하여 `(\x -> f (g (h x)))`와 동일하게 동작한다. 즉 `h`를 먼저 실행하고 그 결과를 `g`에 전달하며, 마지막으로 `f`에 전달하는 것을 의미한다. 자바스크립트로 표현하면 `(x) => f(g(h(x)))`와 같다.

`$` 연산자는 함수 적용을 위한 연산자로서 우선순위를 조정하고 인자를 전달하여 함수를 즉시 평가한다. `f $ g $ h x`는 `f (g (h x))`와 동일하다. `$` 연산자는 괄호를 줄이는 역할을 한다.

`.`과 `$`를 함께 사용하면 `f . g . h $ x`와 같이 표현할 수 있다.

```haskell
-- [코드 3-25] . 연산자와 $ 연산자
f :: Int -> Int
f x = x + 1

g :: Int -> Int
g x = x * 2

h :: Int -> Int
h x = x - 3

main :: IO ()
main = do
  let result = f . g . h $ 5
  print result  -- 출력: 5
```

이 예제의 실행을 자바스크립트로 표현하면 `f(g(h(5)))`와 같다.

### 2.6 sumOfSquaresOfOddNumbers 함수

하스켈에서는 `sumOfSquaresOfOddNumbers` 함수를 다음과 같이 작성할 수 있다.

```haskell
-- [코드 3-26] 하스켈의 sumOfSquaresOfOddNumbers 함수
square :: Int -> Int
square x = x * x

sumOfSquaresOfOddNumbers :: Int -> [Int] -> Int
sumOfSquaresOfOddNumbers limit list =
  foldl (+) 0 . take limit . map square . filter odd $ list

main :: IO ()
main = print (sumOfSquaresOfOddNumbers 3 [1, 2, 3, 4, 5, 6, 7, 8, 9])
-- 출력: 35
```

코드에서 `foldl (+) 0 . take limit . map square . filter odd $ list` 부분은 함수 합성과 적용으로 이루어져 있다. 이 코드는 오른쪽에서 왼쪽으로 읽으면 이해할 수 있다.

1. `$ list`에 의해 `list`를 왼쪽에 합성된 함수들에게 전달한다.
2. `filter odd`는 리스트에서 홀수만 남긴다.
3. `map square`는 남은 홀수를 제곱한다.
4. `take limit`는 주어진 `limit` 개수만큼의 제곱된 값을 선택한다.
5. `foldl (+) 0`은 선택된 값들의 합을 계산한다.

### 2.7 파이프라인 스타일 - &

하스켈에서는 파이프라인 스타일로 함수 합성을 표현할 때 함수 합성 연산자(`.`) 대신 정방향 함수 적용 연산자(`&`)를 사용할 수 있다.

```haskell
-- [코드 3-27] & 연산자
import Data.Function ((&))

square :: Int -> Int
square x = x * x

sumOfSquaresOfOddNumbers :: Int -> [Int] -> Int
sumOfSquaresOfOddNumbers limit list =
  list
    & filter odd
    & map square
    & take limit
    & foldl (+) 0

main :: IO ()
main = print (sumOfSquaresOfOddNumbers 3 [1, 2, 3, 4, 5, 6, 7, 8, 9])
-- 출력: 35
```

`&` 연산자를 사용하면 위에서 아래로 읽을 수 있는 파이프라인 스타일로 코드를 작성할 수 있다. 이는 타입스크립트의 체이닝 스타일과 유사한 가독성을 제공한다.

### 2.8 Either를 통한 에러 처리

하스켈은 순수 함수형 언어로서 예외를 전통적인 방식(예: `try-catch`)으로 처리하기보다는 타입을 통해 에러 상황을 명시적으로 표현하는 방식을 선호한다. 대표적인 타입 중 하나가 `Either`다. `Either` 타입은 성공(`Right`)과 실패(`Left`)를 구분하여 함수의 결과를 명확히 표현함으로써 컴파일 타임에 에러 처리가 필요함을 인지시킨다.

```haskell
-- [코드 3-28] 0으로 나누기 예제
main :: IO ()
main = do
  print (div 10 2)  -- 출력: 5
  print (div 10 0)  -- 예외 발생: divide by zero
```

기본 라이브러리의 `div` 함수는 0으로 나누려 할 때 예외를 발생시킨다. 이제 `Either` 타입을 사용하여 안전하게 처리할 수 있다.

```haskell
-- [코드 3-29] 패턴 매칭과 Left, Right
safeDiv :: Int -> Int -> Either String Int
safeDiv _ 0 = Left "0으로 나눌 수 없습니다."
safeDiv x y = Right (div x y)
```

`safeDiv` 함수는 두 번째 인자가 0일 경우 `Left "0으로 나눌 수 없습니다."`를 반환한다. 이를 통해 런타임 예외 발생 대신 명시적으로 에러 상황을 표현할 수 있다.

```haskell
-- [코드 3-30] safeDiv 함수 사용 예제
main :: IO ()
main = do
  print (safeDiv 10 2)  -- 출력: Right 5
  print (safeDiv 10 0)  -- 출력: Left "0으로 나눌 수 없습니다."
```

결과가 `Right 5`, `Left "..."` 형태의 `Either` 값 그대로 출력되는 것을 볼 수 있다.

### 2.9 패턴 매칭

`safeDiv` 함수는 하스켈의 패턴 매칭 문법을 사용하여 인자 패턴에 따라 함수 실행을 분기한다. `safeDiv _ 0`에서 `_`는 와일드카드 패턴으로 어떤 값이든 상관없음을 의미하고, `0`은 두 번째 인자가 0일 때를 나타낸다.

이처럼 하스켈의 패턴 매칭 문법은 간결하고 직관적인 코드를 작성하도록 돕는다. 타입스크립트와 비교하자면 함수 오버로드, `if`문, 타입 가드, 타입 좁히기, 매개변수 구조분해 등의 역할을 모두 패턴 매칭 한 번으로 해결할 수 있다.

```haskell
-- [코드 3-31] 패턴 매칭으로 Either 값 처리하기
processResult :: Either String Int -> String
processResult (Left errMsg) = "에러: " ++ errMsg
processResult (Right value) = "결과: " ++ show value

main :: IO ()
main = do
  let result1 = safeDiv 10 2
  let result2 = safeDiv 10 0
  putStrLn (processResult result1)  -- 출력: 결과: 5
  putStrLn (processResult result2)  -- 출력: 에러: 0으로 나눌 수 없습니다.
```

`processResult` 함수는 `Either String Int` 값을 인자로 받아 `Left`일 경우 에러 메시지를, `Right`일 경우 정상 결과를 각각 다른 문자열로 반환한다. 이처럼 `Either` 타입을 사용하면 함수의 성공 또는 실패 상태를 명시적으로 구분할 수 있어 에러를 런타임 예외 대신 타입을 통해 안전하게 처리할 수 있다. 또한 하스켈에는 `Maybe`라는 타입으로 값이 없을 수도 있는 상황을 안전하게 처리할 수 있다.

---

## 3. 지연 평가 자세히 살펴보기

이번 절에서는 지연 평가를 지원하는 자료구조인 이터레이터의 실제 실행 순서를 면밀히 살펴본다.

### 3.1 중첩된 이터레이터의 실행 순서 - 제너레이터로 확인하기

각 함수의 `while` 루프 내부에서 로그를 남김으로써 `take`, `map`, `filter` 함수를 조합해 만든 중첩 이터레이터가 어떤 순서로 실행되는지 추적할 수 있다.

```typescript
// [코드 3-32] 지연 평가의 실행 순서
function* filter<A>(f: (a: A) => boolean, iterable: Iterable<A>): IterableIterator<A> {
  const iterator = iterable[Symbol.iterator]();
  while (true) {
    console.log('filter');
    const { value, done } = iterator.next();
    if (done) break;
    if (f(value)) yield value;
  }
}

function* map<A, B>(f: (a: A) => B, iterable: Iterable<A>): IterableIterator<B> {
  const iterator = iterable[Symbol.iterator]();
  while (true) {
    console.log('map');
    const { value, done } = iterator.next();
    if (done) break;
    yield f(value);
  }
}

function* take<A>(limit: number, iterable: Iterable<A>): IterableIterator<A> {
  const iterator = iterable[Symbol.iterator]();
  while (true) {
    console.log('take limit:', limit);
    const { value, done } = iterator.next();
    if (done) break;
    yield value;
    if (--limit === 0) break;
  }
}

const iterable = fx([1, 2, 3, 4, 5])
  .filter(a => a % 2 === 1)
  .map(a => a * a)
  .take(2);

for (const a of iterable) {
  console.log('result:', a);
}
// ??
```

이 코드는 어떤 순서로 로그를 출력할까? 아마 (1) filter가 모두 실행된 다음 map이 모두 실행되거나, (2) filter → map → take 순으로 하나씩 실행될 것이라고 예상할 수 있다. 하지만 실제 결과는 다르다.

```
// 실제 출력 결과
// take limit: 2
// map
// filter
// filter value f(value): 1 true
// map value f(value): 1 1
// take value: 1
// result: 1
// -
// take limit: 1
// map
// filter
// filter value f(value): 2 false
// filter
// filter value f(value): 3 true
// map value f(value): 3 9
// take value: 9
// result: 9
// -
```

결과를 보면 반대로 `take limit: 2`가 먼저 출력되고 이어서 `map`, `filter` 순으로 출력되고 있다. 이는 `take` 함수까지 실행한 결과로 만들어진 이터레이터의 `next()`를 `for...of`문을 통해 처음 호출할 때 `take` 함수의 `while` 루프부터 실행되기 때문이다. 루프 내부에서 `take limit: 2`를 출력하고, 바로 다음 줄에서 `take` 함수는 자신이 인자로 받은 이터레이터의 `next()` 메서드를 호출한다. 여기서 이 이터레이터는 `map`까지 실행한 이터레이터이므로 역시 `map`의 `while` 루프 내부가 먼저 실행되어 `map`이 출력되고, 그 다음으로 `filter`가 출력된다.

### 3.2 이터레이터로 직접 살펴보기

왜 이러한 순서를 따라 실행되는지 확인하기 위해 `map`과 `take` 함수의 반환값을 객체지향 방식으로 이터레이터를 직접 구현하여 살펴보겠다.

```javascript
// [코드 3-35] map, take 함수 (순수 자바스크립트)
function map(f, iterable) {
  const iterator = iterable[Symbol.iterator]();
  return {
    next() {
      const { done, value } = iterator.next();
      return done
        ? { done, value }
        : { done, value: f(value) };
    },
    [Symbol.iterator]() {
      return this;
    }
  };
}

function take(limit, iterable) {
  const iterator = iterable[Symbol.iterator]();
  return {
    next() {
      if (limit === 0) return { done: true };
      const { done, value } = iterator.next();
      if (done) return { done, value };
      limit--;
      return { done, value };
    },
    [Symbol.iterator]() {
      return this;
    }
  };
}

const mapped = map(a => a * a, [10, 20, 30]);
const taked = take(2, mapped);

console.log(taked.next());
// take limit: 2 → map → map value f(value): 10 100 → take value: 100
// { done: false, value: 100 }

console.log(taked.next());
// take limit: 1 → map → map value f(value): 20 400 → take value: 400
// { done: false, value: 400 }

console.log(taked.next());
// { done: true }
```

첫 번째 `taked.next()`를 호출하면 `take` 함수에서 반환한 이터레이터의 `next` 메서드가 호출되고, 내부에서 `iterator.next()`로 `mapped`의 `next` 메서드를 호출한다. `mapped`는 다시 원본 배열의 이터레이터를 호출하여 10을 받고, `f(value)`로 100으로 변환하여 반환한다. 최종적으로 `take`는 `{ done: false, value: 100 }`을 반환한다.

### 3.3 단순화해서 살펴보기

이러한 시각을 가지고 핵심 부분을 코드로 표현해 보면 다음과 같다.

```javascript
// [코드 3-36] 중첩 이터레이터의 내부 실행을 단순화하여 표현
const filtered = {
  next() {
    return iterator.next();
  }
}

const mapped = {
  next() {
    return filtered.next();
  }
}

const taked = {
  next() {
    return mapped.next();
  }
}

taked.next();
```

`taked.next()`를 실행하면 take → map → filter 순으로 진행하여 결과를 반환하면서 다시 filter → map → take 방향으로 돌아온다. 이 코드는 지연된 중첩 이터레이터가 어떻게 평가되는지 잘 나타낸다. `take` 함수가 반환하는 이터레이터의 구현부를 보면 `{ next() {} }` 안에서 다시 `next()`를 실행하는 것을 볼 수 있다. 말 그대로 이터레이터가 중첩되어 있다.

---

## 4. Generator: Iterator: LISP - 지연 평가와 안전한 합성

이번 절에서는 `find`, `every`, `some`과 같은 고차 함수를 리스트 프로세싱 함수의 조합만으로 구현하면서 Generator: Iterator: LISP가 서로 완전히 대체될 수 있다는 관점을 확장하고자 한다. 또한 함수 합성과 안전한 값 접근, 값이 없는 예외를 어떻게 다루는지 알아본다.

### 4.1 find 함수 시그니처

`map`이나 `filter`가 연산을 지연한 이터레이터를 만든 후 계속 리스트 프로세싱을 이어갈 수 있도록 하는 유형의 함수라면, `find`는 '지연된 이터레이터를 평가하여 결과를 만드는 유형의 함수'다. `find`는 이터러블을 순회하면서 요소마다 `f`로 조건을 검사하여 참으로 평가되는 첫 번째 요소를 반환하고, 만족하는 값이 하나도 없을 때는 `undefined`를 반환한다.

```typescript
// [코드 3-38] 타입스크립트의 find 함수 시그니처
type Find = <A>(f: (a: A) => boolean, iterable: Iterable<A>) => A | undefined;
```

이 시그니처는 `find` 함수가 `(a: A) => boolean` 타입의 함수와 `Iterable<A>` 타입의 이터러블을 인자로 받아, 이터러블의 요소 중 하나인 `A` 타입의 값 또는 `undefined`를 반환함을 나타낸다.

하스켈의 `find` 함수 시그니처도 살펴보자.

```haskell
-- [코드 3-39] 하스켈의 find 함수 시그니처
find :: (a -> Bool) -> [a] -> Maybe a
```

이 시그니처는 `find`가 `(a -> Bool)` 타입의 함수와 `[a]` 타입의 리스트를 받아 `Maybe a` 타입의 값을 반환함을 나타낸다.

최종 반환값인 `Maybe a`는 찾는 조건을 만족하는 첫 번째 요소가 있을 경우 `Just a`를, 없을 경우 `Nothing`을 반환하는 타입이다. 하스켈에서는 안전한 함수 합성을 위해 `A | undefined`와 같은 상황을 `Maybe` 타입의 값으로 다룬다.

### 4.2 하스켈에서 find 함수와 안전한 합성

```haskell
-- [코드 3-40] 하스켈에서 find 함수 사용 예제
import Data.Maybe (fromMaybe)
import Data.List (find)

main :: IO ()
main = do
  let result = fromMaybe 0 (find even [1, 3, 5])
  print result  -- 출력: 0
```

이 예제는 `find` 함수와 `Maybe` 타입으로 리스트에서 조건을 만족하는 요소를 찾고 이를 안전하게 처리하는 방법을 보여 준다.

프로그래밍 언어들은 `reduce`의 빈 컬렉션 처리나 `find`처럼 값이 없을 수 있는 (옵셔널한) 상황에 대해 각기 다른 해법을 제안한다. 하스켈은 선언적인 타입과 값으로 이런 상황을 명확히 표현하고, 타입스크립트는 `?.`, `!`, `??`와 같은 연산자를 통해 개발자에게 해결 방법을 제시한다.

### 4.3 find 함수로 생각하는 지연 평가와 리스트 프로세싱

다시 타입스크립트로 돌아와 이터러블 프로토콜을 따르는 `find` 함수를 만들겠다. 먼저 명령형 방식이다.

```typescript
// [코드 3-41] 명령형 코드로 작성한 find 함수
function find<A>(f: (a: A) => boolean, iterable: Iterable<A>): A | undefined {
  const iterator = iterable[Symbol.iterator]();
  while (true) {
    const { value, done } = iterator.next();
    if (done) break;
    if (f(value)) return value;
  }
  return undefined;
}

const result = find(a => a > 2, [1, 2, 3, 4]);
console.log(result);
// 3
```

동작은 단순하다 — ① 이터레이터를 생성해 순회를 준비하고, ② `while (true)` 안에서 `next()`로 `done`과 `value`를 꺼내고, ③ `done`이면 종료, ④ `f(value)`가 참이면 그 값을 `return`(반복문과 함수가 동시에 종료), ⑤ 끝까지 찾지 못하면 `undefined`를 반환한다.

이제 `find`를 함수형 방식으로 구현해 보겠다. 기존에 작성했던 `map`, `filter`, `take` 등은 제너레이터를 활용한 명령형 코드이거나, 이터레이터 객체가 다른 이터레이터 객체의 메서드를 호출하는 객체지향적 구조를 따랐다. `map`·`filter`·`take`는 오히려 그런 명령형 코드가 더 이해하기 쉬운 결과물을 만든다. 그에 반해 `find`, `every`, `some`은 이미 `map`, `filter`, `take`, `reduce` 같은 함수들이 마련되어 있다면 이들을 조합해 함수형 패러다임으로 구현할 수 있으며, 이런 접근은 코드 이해도와 표현력을 높이는 데도 유리하다.

우선 명령형으로 구현했던 `filter` 함수와 [코드 3-41]의 `find`를 비교해 보자.

```typescript
// [코드 3-42] 지연 평가를 지원하는 filter 함수
function* filter<A>(f: (a: A) => boolean, iterable: Iterable<A>): IterableIterator<A> {
  const iterator = iterable[Symbol.iterator]();
  while (true) {
    const { value, done } = iterator.next();
    if (done) break;
    if (f(value)) yield value;
  }
}
```

두 함수는 딱 두 군데만 다르다. 바로 `*`와 `yield`다.

1. `filter`는 `*`가 붙은 제너레이터로, `f(value)`가 참일 때 `yield`로 결과를 반환하며 인자로 받은 이터레이터가 종료될 때까지 계속 순회할 수 있다.
2. `find`는 일반 함수로, `f(value)`가 참일 때 `return`으로 결과를 반환하며 동시에 반복문과 함수를 종료한다.

`Array.prototype.filter`처럼 지연 평가를 지원하지 않는 filter는 배열의 모든 요소를 순회하여 참으로 평가되는 모든 요소를 담은 배열을 반환한다. 하지만 지연 평가를 지원하는 `filter`는 그 결과인 이터레이터를 사용하는 쪽에서 원하는 만큼만 실행시킬 수 있다. 즉 `filter`로 만들어진 이터레이터의 `next()`를 한 번만 평가한다면 이는 `find`와 동일한 로직과 효율을 가지게 된다. 한 번만 평가한다면 `yield`는 사실상 `return`과 같기 때문이다.

다음은 이 성질을 이용해 `find` 함수를 함수형 방식으로 구현한 세 가지 코드다.

```typescript
// [코드 3-43] 함수형 코드로 작성한 find (1)
function find<A>(f: (a: A) => boolean, iterable: Iterable<A>): A | undefined {
  return filter(f, iterable).next().value;
  // 아래와 같이 구현할 수도 있다.
  // const [head] = filter(f, iterable);
  // return head;
}

const result = find(a => a > 2, [1, 2, 3, 4]); // [const result: number | undefined]
console.log(result);
// 3

const isOdd = (a: number) => a % 2 === 1;
const result2 = find(isOdd, [2, 4, 6]); // [const result2: number | undefined]
console.log(result2);
// undefined
```

첫 번째 방식은 `filter`로 조건을 만족하는 요소들을 필터링할 준비만 해 두고, 반환된 이터레이터의 `next()`를 한 번만 실행하여 첫 번째로 조건을 만족하는 요소를 찾는 즉시 `filter`의 반복문과 함수를 종료한다. 주석의 구현처럼 구조 분해 할당(`const [head] = ...`)을 사용해도 이터러블 프로토콜에 기반해 `next()`가 한 번만 실행되므로, [코드 3-41] 명령형 코드로 작성한 `find`와 동일하게 효율적인 로직으로 동작한다.

```typescript
// [코드 3-44] 함수형 코드로 작성한 find (2)
const head = <A>(
  iterable: Iterable<A>
): A | undefined => iterable[Symbol.iterator]().next().value;
// 아래와 같이 구현할 수도 있다.
// const head = <A>([a]: Iterable<A>): A | undefined => a;

const find = <A>(
  f: (a: A) => boolean,
  iterable: Iterable<A>
): A | undefined => head(filter(f, iterable));
```

두 번째 방식은 주어진 이터러블의 첫 번째 요소를 반환하는 `head` 헬퍼 함수를 별도로 정의하고, `find`는 `filter`로 필터링할 준비를 한 후 `head`로 첫 번째 요소를 반환한다. 첫 번째 방식과 로직은 유사하지만 `head`를 분리해 코드의 모듈성과 재사용성을 높이고 함수의 역할을 분명하게 나눈 점이 특징이다.

세 번째 방식은 `FxIterable` 클래스를 사용하여 체이닝 방식으로 구현한다. 그 전에 `FxIterable`의 `to` 메서드를 다시 확인해 두자.

```typescript
// [코드 3-45] FxIterable 다시 보기
class FxIterable<A> {
  constructor(private iterable: Iterable<A>) {}

  // ... 메서드 생략 ...

  filter(f: (a: A) => boolean): FxIterable<A> {
    return fx(filter(f, this));
  }

  to<R>(converter: (iterable: Iterable<A>) => R): R {
    return converter(this.iterable);
  }
}
```

```typescript
// [코드 3-46] 함수형 코드로 작성한 find (3)
const find = <A>(f: (a: A) => boolean, iterable: Iterable<A>): A | undefined =>
  fx(iterable)
    .filter(f)
    .to(head);
```

`fx` 함수로 `FxIterable` 인스턴스를 생성하고, `filter` 메서드로 필터링을 준비한 후 `to` 메서드에 `head`를 전달하여 첫 번째 요소를 반환한다.

위의 세 가지 방식 모두 [코드 3-41] 명령형 코드로 작성한 `find` 함수와 동일한 효율을 제공하면서도 코드가 간결하다. 명령형 코드와 비교해 보면 이들 세 가지 방식은 테스트해 볼 필요도 없을 정도로 간결하고, 잘 동작할 것이라는 확신을 빠르게 가질 수 있는 코드다.

3장을 시작하면서 이터레이터를 구현하는 다음 세 가지 방식이 서로 1:1:1로 대체 가능하다고 이야기했다.

- **명령형 방식(IP)**: 제너레이터를 통한 이터레이터 생성
- **객체지향적 방식(OOP)**: 이터레이터 객체 직접 구현
- **함수형 방식(FP)**: 리스트 프로세싱 함수 조합으로 이터레이터 생성

`find` 같은 고차 함수도 명령형 접근 대신 리스트 프로세싱 함수들의 조합으로 동일한 동작을 구현할 수 있고, 이렇게 함수형으로 구현한 코드도 명령형 코드와 동일한 시간 복잡도를 가질 수 있음을 확인했다. 각 패러다임으로 작성한 코드는 서로를 완전히 대체할 수 있으며 필요하다면 섞어서 사용할 수도 있다. 멀티패러다임 언어를 사용하는 우리는 언제든지, 심지어 하나의 함수 안에서도 상황에 따라 가장 알맞은 패러다임을 선택하거나 조합하여 활용할 수 있다.

### 4.4 타입스크립트에서의 안전한 합성

```typescript
// [코드 3-47] 안전한 합성을 위한 연산자 ?. ?? !
const desserts = [
  { name: 'Chocolate', price: 5000 },
  { name: 'Latte', price: 3500 },
  { name: 'Coffee', price: 3000 }
];

// ① 옵셔널 체이닝 연산자(?.)를 통해 name 프로퍼티에 안전하게 접근
const dessert = find(({ price }) => price < 2000, desserts);
console.log(dessert?.name ?? 'TAT');
// TAT

// ② Non-null 단언 연산자(!)를 통해 무조건 찾을 상황을 의도하고 있다고 언어와 소통
const dessert2 = find(({ price }) => price < Infinity, desserts)!;
console.log(dessert2.name);
// Chocolate
```

**① 옵셔널 체이닝 연산자(`?.`)를 통해 name 프로퍼티에 안전하게 접근** — 이 코드는 `dessert` 객체가 존재하지 않을 경우(`find`가 `undefined`를 반환할 경우) 안전하게 접근하며 `'TAT'`를 출력한다. 옵셔널 체이닝 연산자(`?.`)와 Nullish 병합 연산자(`??`)를 사용하여 안전하게 값에 접근하고 기본값을 제공하는 방법이다.

- `dessert?.name`은 `dessert`가 `undefined`일 경우 `undefined`를 반환하고, 그렇지 않으면 `dessert.name`을 반환한다.
- 최종적으로 `dessert?.name`이 `undefined`일 경우 기본값 `'TAT'`를 반환하고, 그렇지 않으면 `dessert?.name`의 값을 반환한다.

`dessert?.name`과 같은 코드는 `dessert`를 찾지 못하는 상황이 있을 수 있음을 알고 있으며, `undefined`일 경우 `'TAT'`로 대체하는 것이 의도한 동작이라는 것을 표현한다. 그렇다면 Non-null 단언 연산자로 소통하는 것은 어떤 의미일까?

**② Non-null 단언 연산자(`!`)를 통해 무조건 찾을 상황을 의도하고 있다고 언어와 소통** — `dessert2.name`에서 만일 `dessert2`가 없는 상황이 생긴다면, 이는 개발자가 프로그램 안에서 이런 상황이 연출되는 것을 의도한 바가 아니기 때문에 에러가 숨지 않고 전파되어야 한다고 언어와 소통한 것이다. 즉 `dessert2`가 존재하지 않는 상황을 에러로 간주하고 이를 탐지하기 위해 Non-null 단언 연산자 `!`를 사용하는 방법이다.

①번 방식(옵셔널 체이닝)은 값이 실제로 없을 때도 런타임 에러 없이 `undefined` 처리된다. 반면 ②번 방식(Non-null 단언)은 값이 없는데도 존재한다고 단언하므로 실제로 값이 `null`이나 `undefined`라면 런타임 에러가 발생할 수 있다. 그렇다면 ②번 방식은 피해야 하는 방법일까? 또는 그저 컴파일을 통과하기 위해 사용하는 기법인 것일까?

②번 방식은 개발자가 '이 로직에서는 값이 반드시 존재하도록 설계했다'는 의도를 언어에 전달하는 수단이다. 즉 '이곳에서는 `null`이나 `undefined`가 나타나지 않는 상황이며, 만약 실제로 값이 없다면 그것은 설계가 어긋난 상황이므로 런타임 에러가 발생해야만 한다'는 의도를 표현하며 구현한 것이다. 따라서 에러가 발생한다면 개발자는 `!`를 없애는 것이 아니라 런타임에서 값을 찾지 못하는 이유를 찾아 해결해야 한다(예: API의 문제인지, DB에 값이 잘못 저장되는지, 어떤 경우에 DOM에 해당 엘리먼트가 없는 상황이 있는지 등).

타입스크립트는 이러한 연산자들과 함께 `try...catch` 구문을 통해 안전한 합성, 에러 전파, 정확한 에러 처리를 지원한다. 또한 IDE는 타입 시스템을 바탕으로 '옵셔널 체이닝으로 안전하게 접근해야 하는지' 아니면 'Non-null 단언이 필요한 상황인지'를 파악하도록 돕는다. 이런 기능들을 적절히 활용하면 런타임 에러가 될 수 있는 부분을 코드 작성 단계에서 미리 감지하고, 개발자가 원하는 상황(안전한 합성 또는 예외 발생)에 맞춰 명확히 표현할 수 있다.

### 4.5 every 함수

`every` 함수는 주어진 함수 `f`가 모든 요소에 대해 `true`를 반환하면 최종 결과로 `true`를, 그렇지 않으면 `false`를 반환해야 한다. 먼저 `every`의 함수 시그니처는 다음과 같다. 위쪽 주석은 같은 동작을 하는 하스켈의 `all` 함수 시그니처다.

```typescript
// [코드 3-48] every 함수 시그니처
// all :: (a -> Bool) -> [a] -> Bool
function every<A>(f: (a: A) => boolean, iterable: Iterable<A>): boolean {}
```

이번에도 명령형 코드 대신 함수형 방식으로, 리스트 프로세싱 관점에서 문제를 해결해 보겠다. 함수형 프로그래밍에서는 리스트를 단계별로 변환하며 최종 결과를 도출하는 방식으로 사고한다. 다양한 방법이 있지만 여기서는 다음과 같은 전략을 세웠다. 먼저 리스트의 모든 요소를 `boolean` 값으로 변환한 뒤 이들을 `&&` 연산자로 모두 연결하면 원하는 결과를 쉽게 얻을 수 있다.

```typescript
// [코드 3-49] every 함수 구현 전략
// 1. [1, 3, 5]
// 2. [isOdd(1), isOdd(3), isOdd(5)]
// 3. (true && true && true)
```

`every`를 구현하는 방법은 여러 가지가 있지만 이 방식은 거의 모든 언어에 적용할 수 있는 로직이라는 점이 매력적이다. 특정 언어나 자료구조에 특화된 메서드나 문법에 의존하지 않고, 대부분의 언어에서 지원하는 AND 연산자(`&&`)만 활용하므로 언어에 종속되지 않으면서도 간결하고 이해하기 쉽다. [코드 3-50]을 보면 [코드 3-49]의 계획이 정말 그대로 옮겨진 것을 확인할 수 있다.

```typescript
// [코드 3-50] every 함수 구현
function every<A>(f: (a: A) => boolean, iterable: Iterable<A>): boolean {
  return fx(iterable)
    .map(f)
    .reduce((a, b) => a && b, true);
}

const isOdd = (a: number) => a % 2 === 1;
console.log(every(isOdd, [1, 3, 5]));
// true
console.log(every(isOdd, [1, 2, 5]));
// false
```

`every`는 `map(f)`와 `reduce((a, b) => a && b, true)`를 체이닝으로 합성하여 만들었다. 첫 번째 `map`에는 `every`가 받은 `f`를 그대로 전달하고, `reduce`에서는 누적 함수 `a && b`를 통해 `(boolean && boolean && boolean)`과 같은 효과를 낸다.

참고로 "한 번의 `reduce`에서 `f(b)`와 같이 구현하지 않고 왜 `map`과 `reduce`로 나누어 순회하는 거지?"라는 의문이 생길 수도 있다. 하지만 두 코드의 시간 복잡도는 동일하다. `fx(list).reduce((a, b) => a && f(b), true)`는 각 요소를 순회하며 `f(b)`를 바로 평가하므로 한 번의 순회로 O(n)이 걸린다. 한편 `fx(list).map(f).reduce((a, b) => a && b, true)`는 표면적으로는 'map 후 reduce'로 보이지만, 지연 이터레이터의 특성상 각 요소가 `map`을 통과한 직후 즉시 `reduce`에 소비되므로 실제로는 한 번만 순회하면서 O(n)이 걸린다.

연관된 다른 케이스로, 지연 이터레이터가 아닌 일반 배열의 `array.map(f).reduce(...)`는 전부 `map`을 수행해 새 배열을 생성한 뒤 다시 `reduce`를 수행하므로 배열을 두 번 순회한다. 그래도 각각 O(n)씩 두 번이므로 최종 복잡도는 여전히 O(n)이지만, 중간 배열을 만들지 않는 지연 이터레이터 방식이 메모리 면에서 더 효율적이다. 함수형 프로그래밍에서는 이와 같이 합성하는 방법으로 간결성과 가독성을 높일 수 있고 비동기 프로그래밍에서도 이점을 발휘할 수 있으므로 이러한 방법을 추천한다.

### 4.6 some 함수

`some` 함수도 비슷한 방식으로 구현해 보겠다. `some`은 주어진 함수 `f`가 하나라도 `true`를 반환하면 최종 결과로 `true`를, 모든 요소가 `false`를 반환하면 `false`를 반환해야 한다. `some`의 함수 시그니처는 다음과 같다. 위쪽 주석은 같은 동작을 하는 하스켈의 `any` 함수 시그니처다.

```typescript
// [코드 3-51] some 함수 시그니처
// any :: (a -> Bool) -> [a] -> Bool
function some<A>(f: (a: A) => boolean, iterable: Iterable<A>): boolean {}
```

`some`도 `every`와 동일한 방식으로 계획한다. 모든 값을 `boolean`으로 만든 후 `||` 연산자로 묶으면 원하는 결과를 얻을 수 있다.

```typescript
// [코드 3-52] some 함수 구현 전략
// 1. [2, 3, 4]
// 2. [isOdd(2), isOdd(3), isOdd(4)]
// 3. (false || true || false)
```

앞서 이야기한 것처럼 `some`이나 `every`를 구현하는 방법은 많으며 더 간결한 방법도 있다. 예를 들어 조건과 일치하는 값의 index를 구하여 -1과 비교하거나, 길이가 하나인 배열을 만들어 length가 0인지 비교하는 방법도 있다. 그런데 이런 방법은 고차 함수를 사용하더라도 약간 명령형 느낌이 남아 있다. 언어의 문법이나 표준 라이브러리에 의존적이기도 하고, `length === 0` 같은 코드는 선언적이기보다는 '어떻게' 동작할 것인가를 구체적으로 작성하는 명령형 느낌의 코드다.

반면 [코드 3-50]과 [코드 3-53] 같은 방법은 '모든(어떤) 요소가 이 조건에 맞는지 검사한 후 만족하는지 확인'한다는 의미가 코드의 전체 문맥에 그대로 표현된다. '어떻게' 할 것인지보다 '무엇'을 하고 있는지를 표현한 코드가 읽기도 좋고 의미도 잘 담아내며 나중에 다시 읽어도 쉽게 이해할 수 있다.

```typescript
// [코드 3-53] some 함수 구현
function some<A>(f: (a: A) => boolean, iterable: Iterable<A>): boolean {
  return fx(iterable)
    .map(f)
    .reduce((a, b) => a || b, false);
}

console.log(some(isOdd, [2, 5, 6]));
// true
console.log(some(isOdd, [2, 4, 6]));
// false
```

`reduce`의 누적 함수로 `a || b`를 전달하여 `(boolean || boolean || boolean)`과 동일한 효과를 냈다.

### 4.7 지연 평가에 기반한 break 로직 끼워 넣기

사실 `some`과 `every` 두 함수 모두 결과를 만들기 위해 반드시 모든 요소를 순회할 필요는 없다. `some`은 `true`를 하나라도 만나면 순회를 종료할 수 있고, `every`는 `false`를 하나라도 만나면 종료할 수 있다.

```typescript
// [코드 3-54] 효율 높인 some 함수
function some<A>(f: (a: A) => boolean, iterable: Iterable<A>): boolean {
  return fx(iterable)
    .map(f)
    .filter(a => a)
    .take(1)
    .reduce((a, b) => a || b, false);
}
```

앞서 구현한 `some`에 `.filter(a => a).take(1)`을 추가하여 최적화했다. 이제 이 코드는 `.filter(a => a).take(1)`을 통해 `true`를 하나라도 만나면 더 이상 순회하지 않고, 요소가 최대 하나인 이터레이터를 만들어 `reduce`에 전달한다. 만일 `true`가 하나도 없다면 요소가 없는 이터레이터가 `reduce`에 전달된다. `reduce`는 요소가 없으면 기본값으로 받은 `false`를 반환하고, 요소가 있으면 `false || true`로 한 번 누적하여 `true`를 반환한다.

이제 `some`은 반복문을 `if () break;`로 종료한 것처럼 효율이 좋아졌다. `every`도 이와 같은 방법으로 최적화할 수 있다.

```typescript
// [코드 3-55] 효율 높인 every 함수
function every<A>(f: (a: A) => boolean, iterable: Iterable<A>): boolean {
  return fx(iterable)
    .map(f)
    .filter(a => !a)
    .take(1)
    .reduce((a, b) => a && b, true);
}
```

이번에는 `every`에 `.filter(a => !a).take(1)`을 추가하여 최적화했다. 이 코드는 `false`를 하나라도 만나면 더 이상 순회하지 않고 요소가 최대 하나인 이터레이터를 만들어 `reduce`에 전달한다. 만일 `false`가 하나도 없다면 요소가 없는 이터레이터가 `reduce`에 전달되고, `reduce`는 요소가 없으면 기본값으로 받은 `true`를 반환하며 요소가 있으면 `true && false`로 한 번 누적하여 `false`를 반환한다.

이로써 `find`처럼 `every`와 `some` 같은 함수도 명령형이 아닌 리스트 프로세싱 함수만을 합성하여 만들 수 있다는 것을 확인했다.

### 4.8 every와 some 함수의 공통 로직을 함수형으로 추상화하기

함수형 프로그래밍은 리스트, 코드, 함수를 값으로 다루므로 공통 로직을 분리하여 추상화하기 편리하다.

```typescript
// [코드 3-56] accumulateWith 함수
function accumulateWith<A>(
  accumulator: (a: boolean, b: boolean) => boolean,
  acc: boolean,
  taking: (a: boolean) => boolean,
  f: (a: A) => boolean,
  iterable: Iterable<A>
): boolean {
  return fx(iterable)
    .map(f)
    .filter(taking)
    .take(1)
    .reduce(accumulator, acc);
}

function every<A>(f: (a: A) => boolean, iterable: Iterable<A>): boolean {
  return accumulateWith((a, b) => a && b, true, a => !a, f, iterable);
}

function some<A>(f: (a: A) => boolean, iterable: Iterable<A>): boolean {
  return accumulateWith((a, b) => a || b, false, a => a, f, iterable);
}
```

`accumulateWith` 함수를 사용하여 `every`와 `some` 함수의 공통 로직을 추상화했다. 서로 다른 로직을 인자로 전달하는데, 특히 논리가 담긴 코드를 함수로 전달하여 조립하는 면이 특별하다.

`every`와 `some`의 본문은 `fx(iterable).map(f).filter(...).take(1).reduce(...)`처럼 이미 함수들을 전달하는 형태로 되어 있었다. 따라서 코드를 그대로 가져와 아주 간단한 수정만으로 추상화 작업을 마칠 수 있다 — 중복 제거 과정에 대해 특별히 설명하지 않아도 될 만큼 쉽게 완료했다. 이처럼 함수형 프로그래밍은 리팩터링하기도 좋으며 유지보수성이 뛰어나다.

### 4.9 concat으로 더하기

배열 메서드 `concat`은 여러 배열을 하나로 결합하는 데 사용된다. 하지만 `concat` 메서드는 모든 배열 요소를 즉시 평가하고 결합하여 새로운 배열을 생성하기 때문에 매우 큰 배열을 결합할 때 메모리 사용량이 증가할 수 있다. 반면 제너레이터를 사용해 `concat`을 구현하면 지연 평가를 통해 요소를 필요할 때마다 처리할 수 있다.

```typescript
// [코드 3-57] concat 함수
function* concat<T>(...iterables: Iterable<T>[]): IterableIterator<T> {
  for (const iterable of iterables) yield* iterable;
}

const arr = [1, 2, 3, 4];
const iter = concat(arr, [5]);
console.log([...iter]);
// [1, 2, 3, 4, 5]
```

`concat` 함수는 여러 이터러블을 인자로 받아 각 이터러블의 요소를 순차적으로 생성한다. 이때 배열 전체를 한 번에 결합하는 대신 필요한 요소를 하나씩 순회하며 생성한다. 즉 실제로 배열을 합치는 것이 아니라 순회를 이어서 수행하도록 한다.

#### 배열 메서드 concat과 제너레이터 concat의 차이

다음은 배열 메서드 `concat`과 제너레이터 `concat`을 비교한 코드다.

```typescript
// [코드 3-58] concat 비교 코드
const arr = [1, 2, 3, 4, 5];

// 배열 concat을 사용한 예제
const arr2 = arr.concat([6, 7, 8, 9, 10]);
console.log(arr2); // [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
let acc = 0;
for (const a of take(7, arr2)) {
  acc += a;
}
console.log(acc); // 28

// 제너레이터 concat을 사용한 예제
const iter = concat(arr, [6, 7, 8, 9, 10]);
console.log(iter); // concat {<suspended>} (아무 일도 일어나지 않음)
let acc2 = 0;
for (const a of take(7, iter)) {
  acc2 += a;
}
console.log(acc2); // 28
```

`arr.concat([6, 7, 8, 9, 10])`은 `[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]`이라는 새로운 배열을 생성한다. 반면 제너레이터 `concat`은 새로운 배열을 만들지 않고 결합된 요소를 하나씩 생성하여 처리한다.

배열의 `concat` 메서드로 큰 배열이 복사되면 메모리 사용량이 증가한다. 새로 만들어진 배열이 모든 요소를 담을 커다란 인덱스 테이블을 생성하고 그 슬롯들을 전부 재할당해야 하기 때문이다. [코드 3-58]에서 배열 `concat`을 사용한 예제는 `acc` 값을 구하는 데만 목적이 있음에도 불구하고 `arr2`라는 새 배열을 만들게 된다. 반면 제너레이터 `concat`을 사용한 예제에서는 배열이 복사되지 않고 필요한 연산만 수행하여 `acc2`를 계산한다.

#### push·unshift 대신 concat을 사용하며 생각해 보기

`push`(뒤에 추가)와 `unshift`(앞에 추가)는 원본 배열을 변경하는 메서드다. 원서는 [코드 3-59]~[코드 3-60a]에서 이 둘을 제너레이터 `concat`으로 대체해 보는데, 요지는 다음과 같다.

- **`push` 대신 `concat(arr, [6, 7])`**: 원본이 변경되지 않으므로, `push`로 추가했다가 `pop`으로 되돌리는 복원 작업 없이 같은 원본으로 여러 조합을 만들 수 있다.
- **`unshift` 대신 `concat(['1'], arr)`**: `unshift`는 기존 모든 요소의 인덱스를 하나씩 뒤로 이동시키므로(요소가 100개면 100개 모두 이동) 큰 배열일수록 비용이 커진다. `concat`은 인덱스 이동 없이 앞에 연결해 순차적으로 생성한다.

물론 모든 상황에서 제너레이터 `concat`을 사용해야 하는 것은 아니며 `push`가 더 적합한 경우도 있다. 상황에 맞게 적절한 방법을 선택하는 것이 중요하다.

#### take와 함께 사용하기

`unshift`/`push` 대신 `concat`을 사용하고 `take`로 필요한 개수만 가져온다면, 전체 배열을 조작할 필요 없이 필요한 요소만 처리할 수 있다.

```typescript
// [코드 3-61] take와 concat
const arr1 = [1, 2, 3, 4, 5];
const arr2 = [6, 7, 8, 9, 10];
const iter = take(3, concat(arr1, arr2));
console.log([...iter]); // [1, 2, 3]
// arr2는 순회하지도 않고 종료
```

이 방법을 사용하면 필요한 요소만 처리할 수 있어 효율적이다. 위 상황에서는 `arr2`는 순회하지도 않고 종료되므로 `concat`을 하지 않은 것이나 다름없다.

#### some과 함께 사용하기

`concat`과 `some`을 함께 사용하면 필요한 만큼만 요소를 생성하고 처리할 수 있어 효율적이다. `some` 함수는 조건을 만족하는 첫 번째 요소를 찾은 후 즉시 순회를 중지하므로 불필요한 계산을 하지 않는다.

```typescript
// [코드 3-62] some과 concat
const arr = [3, 4, 5];
console.log(some(n => n < 3, arr));
// false
const iter2 = concat([1, 2], arr);
console.log(some(n => n < 3, iter2));
// true
```

지금까지 지연 평가를 활용한 `concat`의 여러 사례를 살펴보았다. 특히 값 변화를 직접적으로 적용하는 대신 지연 평가를 통해 리스트를 처리하는 방법을 확인할 수 있었다. 이러한 접근 방식으로 프로세싱을 효율적이고 유연하게 할 수 있으며 다양한 아이디어를 떠올릴 수 있다.

---

## 요약

- **코드: 객체: 함수 = Generator: Iterator: LISP = IP: OOP: FP**: 코드, 객체, 함수는 각각 제너레이터, 이터레이터, LISP와 유사한 관계를 가진다. 이터레이터는 반복자 패턴의 구현체로 컬렉션의 값을 일반화된 패턴으로 순회하는 객체이며, 지연성을 가져 평가한 만큼만 실행하고 일시 정지하는 특성이 있다. 이를 통해 명령형, 객체지향적, 함수형 접근 방식 모두를 통합하는 강력한 프로그래밍 모델을 만들 수 있다.
- **코드가 곧 데이터 - 로직이 담긴 리스트**: LISP의 철학은 코드와 데이터의 경계가 없는 프로그래밍 언어의 특징을 반영한다. `for`, `if`, `break` 같은 명령형 코드 문장을 `filter`, `map`, `take`, `reduce` 같은 리스트 프로세싱 함수로 대체하면 코드가 선언적으로 변하고 가독성이 크게 향상된다. 이러한 개념은 타입스크립트, 코틀린, 스위프트, 스칼라, C#, 자바 등 현대 멀티패러다임 언어 전반에 적용할 수 있다.
- **하스켈에서 배우기**: 하스켈은 순수 함수형 프로그래밍 언어로 순수 함수와 함수 합성, 커링, 지연 평가, 강력한 타입 시스템 등의 개념을 제공한다. 하스켈의 함수 시그니처, 패턴 매칭, `Either`/`Maybe` 타입을 통한 안전한 에러 처리는 현대 프로그래밍 언어에 적용되는 다양한 기능을 더 깊이 이해하는 데 도움을 준다.
- **지연 평가 자세히 살펴보기**: 지연 평가는 필요한 시점까지 계산을 미루는 전략으로 프로그램의 성능을 최적화할 수 있다. 중첩된 이터레이터는 take → map → filter 순으로(가장 바깥에서 안쪽으로) 실행되며, 이를 이해하면 효율적인 함수 합성이 가능하다.
- **Generator: Iterator: LISP - 지연 평가와 안전한 합성**: 리스트 프로세싱 함수의 조합만으로도 `find`, `every`, `some`과 같은 고차 함수를 구현할 수 있다. 타입스크립트에서는 옵셔널 체이닝 연산자(`?.`)와 Non-null 단언 연산자(`!`)를 사용하여 안전하게 값을 합성하고 언어와 소통할 수 있다. 또한 리스트 프로세싱으로 구현한 함수는 지연 평가로 효율적으로 동작할 수 있으며, 쉽게 공통 로직을 추상화하여 중복을 제거할 수 있다.
