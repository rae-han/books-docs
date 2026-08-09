# Chapter 11: Learning from Haskell (하스켈에서 배우기 — 코드:객체:함수)

## 핵심 질문

Generator : Iterator : LISP = IP : OOP : FP라는 등식은 무엇을 말하는가? 명령형 문장(for·if·break)을 리스트 프로세싱으로 대체하는 사고는 언어를 넘어 어떻게 일반화되며, 하스켈은 커링·부수효과·에러 처리를 언어 차원에서 어떻게 다루는가?

---

1~10장에서 다룬 개념들을 **Generator : Iterator : LISP = IP : OOP : FP**의 관점에서 정리하면 다음과 같다.

- **제너레이터는 명령형 코드로 이터레이터 생성**: 제너레이터 함수는 명령형 코드로 이터레이터를 만들 수 있는 수단이다. `yield` 지점에서 함수 실행을 일시 정지하고 재개할 수 있어 제너레이터의 코드를 리스트 단위로 지연 평가하는 효과를 낸다. 이는 '코드가 리스트이고 리스트가 코드'라는 LISP적 사고와 맞닿아 있다.
- **이터레이터는 반복자 패턴의 구현체**: 이터레이터는 컬렉션 형태의 데이터를 일반화된 패턴으로 순회하는 객체다. 필요할 때마다 값을 평가하는 지연성을 가지므로 유한한 컬렉션뿐 아니라 무한 시퀀스도 처리할 수 있다.
- **이터러블 이터레이터는 명령형·객체지향적·함수형으로 다룰 수 있음**: 명령형으로는 `next()`를 실행하며 `while`문으로 순회하거나 `for...of`문·전개 연산자로 다룰 수 있다. 객체지향적으로는 이터러블 이터레이터를 다루는 클래스를 만들거나 이터레이터 내부에서 다른 이터레이터와 통신하는 이터레이터를 만들 수 있다. 함수형으로는 고차 함수를 통해 이터레이터와 각 요소를 처리할 함수를 전달하는 방식으로 다루며, 이터레이션 로직을 함수 조합 형태로 구현하고 지연 평가와 리스트 프로세싱을 극대화한다.
- **이터레이터 생성 방식의 다양화**: 궁극적으로 이터레이터는 세 가지 방식으로 만들 수 있으며 서로 1:1:1로 대체할 수 있다.
  - **명령형 방식(IP)**: 제너레이터를 통한 이터레이터 생성
  - **객체지향적 방식(OOP)**: 이터레이터 객체 직접 구현
  - **함수형 방식(FP)**: 리스트 프로세싱 함수 조합으로 이터레이터 생성

> **참고**: 이 장의 `[코드 3-N]` 번호는 원본 멀티패러다임 노트(ch03) 기준이다.

---

## 1. 코드가 곧 데이터 — 로직이 담긴 리스트

코드를 리스트로 바라보는 사고방식은 프로그래밍 패러다임을 확장하는 강력한 도구다. 2장에서 예고했던 대응표(if→filter, 변수 할당→map, break→take, 합산→reduce)를 실제 문제로 완성해 보자.

### 1.1 명령형으로 작성한 n개의 홀수를 제곱하여 모두 더하는 함수

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

- **순회**: `for (const a of list)`를 통해 각 요소를 순회한다.
- **홀수 검사**: `if (a % 2 === 1)`로 홀수인지 검사한다.
- **제곱 계산**: `const b = a * a;`로 제곱을 계산해 저장한다.
- **누적 합계 갱신**: `acc += b;`로 누적한다.
- **길이 검사 및 종료**: `if (--limit === 0) break;`로 limit이 0이 되면 종료한다.
- **결과 반환**: `return acc;`

### 1.2 if를 filter로 대체

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
```

`list`를 `filter(...)`로 대체하고 `if`의 조건을 filter의 보조 함수로 옮겼다. `for...of` 내부 코드는 `a`가 필터링된 결과인지 신경 쓸 필요 없이 제곱하고 합산하는 일만 한다. 코드의 실행을 제어하던 '코드 문장'이 filter가 적용된 **'리스트'**로 바뀐 것이다.

### 1.3 값 변화 후 변수 할당을 map으로 대체

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
```

`map`이 `const b = a * a;`(값 변화 후 변수 할당)를 대체했다. `map(a => a * a, filter(...))`는 홀수만 제곱한 리스트를 만드는 **지연된 이터레이터**다. 이 개념을 LISP 문법으로 표현하면 더욱 명확해진다.

```scheme
; [코드 3-4] Scheme 코드
(define list '(1 2 3 4 5))
(define (square x) (* x x))
(map square (filter odd? list))
; (1 9 25)

; JavaScript
; map(square, filter(isOdd, list))
```

리스트를 생성하는 `'(1 2 3 4 5)`와 제곱 계산식 `(* x x)`의 문법이 작은따옴표를 빼고는 동일하다 — LISP에서는 데이터를 정의하는 문법도, 계산식도, 함수 호출도 모두 **리스트로 표현**된다. `(* x x)`라는 리스트는 `*` 하나와 `x` 두 개를 요소로 가지며, 평가될 때 제곱으로 계산된다.

```scheme
; [코드 3-4a] Scheme 코드
(map (lambda (x) (* x x)) (filter odd? '(1 2 3 4 5)))
```

리스트는 코드이고, 코드는 리스트이며, **중첩된 리스트는 알고리즘이자 로직**이다. 타입스크립트는 LISP와 문법만 다를 뿐 이터레이션 프로토콜을 기반으로 이 패러다임을 그대로 적용할 수 있다.

### 1.4 break를 take로 대체

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
```

`take(limit, map(..., filter(..., list)))`는 모든 연산이 지연되어 있다가, `for...of`에서 처음 뽑을 때 1, 두 번째에 9, 마지막에 25가 들어오면서 종료된다. **`break`문을 제거했음에도 시간 복잡도가 동일하다** — break는 필요한 만큼만 반복되도록 제어하는 키워드인데, take를 통해 그 제어문마저 리스트로 사고할 수 있게 됐다. 이를 가능하게 하는 핵심이 지연 평가다(8장).

### 1.5 합산을 reduce로 대체

```typescript
// [코드 3-6] reduce로 대체한 코드
const sumOfSquaresOfOddNumbers = (limit: number, list: number[]): number =>
  reduce((a, b) => a + b, 0,      // add(add(1, 9), 25)
    take(limit,                     // [(1), (9), (25)]
      map(a => a * a,               // [(1), (9), (25), (49), (81)]
        filter(a => a % 2 === 1, list)))); // [(1), (3), (5), (7), (9)]
```

### 1.6 체이닝으로 변경

`take`는 자주 쓰이므로 `FxIterable`(10장)에 메서드로 추가해 읽기 좋은 순서로 표현한다.

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
```

코드가 선언적으로 변했고 가독성이 크게 향상됐다. filter·map·take·reduce라는 선언적인 함수명으로 각 부분의 목적을 파악할 수 있고, 위에서 아래로 읽힌다.

> **핵심 통찰**: 리스트 프로세싱은 (명령형) 코드 라인들을 리스트로 변환한다. 코드를 값(리스트)으로 다루고 함수를 값(일급 함수)으로 다루어, 작은 코드들의 목록으로 복잡한 문제를 해결해 나가는 것 — 이것이 함수형 프로그래밍과 리스트 프로세싱의 방법이다.

## 2. 현대 언어에서 리스트 프로세싱

같은 함수를 여러 언어로 구현하면, 이 철학이 언어를 넘어 일반화됨을 확인할 수 있다.

**클로저** — `->>` 매크로(10장)로 파이프라인을 표현하고, `+` 기호를 reduce의 누적 함수로 그대로 전달한다.

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

**코틀린** — `asSequence()`로 지연 연산을 시작하며, `it` 키워드로 현재 요소를 나타낸다.

```kotlin
// [코드 3-9] 코틀린으로 구현
fun sumOfSquaresOfOddNumbers(limit: Int, list: List<Int>): Int {
  return list.asSequence()
    .filter { it % 2 == 1 }
    .map { it * it }
    .take(limit)
    .fold(0) { a, b -> a + b }
}
```

**스위프트** — `lazy` 키워드로 지연 연산을 시작하고, `+` 연산자를 reduce의 누적 함수로 쓸 수 있다.

```swift
// [코드 3-10] 스위프트로 구현
func sumOfSquaresOfOddNumbers(limit: Int, list: [Int]) -> Int {
  return list.lazy
    .filter { $0 % 2 == 1 }
    .map { $0 * $0 }
    .prefix(limit)       // take와 동일한 함수
    .reduce(0, +)        // 스위프트의 reduce는 첫 번째 인자가 초깃값이며 생략할 수 없음
}
```

**스칼라** — `LazyList`로 지연 평가를 지원하며, 언더스코어로 요소를 간단히 표현한다.

```scala
// [코드 3-11] 스칼라로 구현
def sumOfSquaresOfOddNumbers(limit: Int, list: List[Int]): Int = {
  list.to(LazyList)
    .filter(_ % 2 == 1)
    .map(a => a * a)
    .take(limit)
    .foldLeft(0)(_ + _)
}
```

**C#** — LINQ(*Language Integrated Query - 프로그래밍 언어에 데이터 질의 기능을 통합한 기술*)의 Where/Select/Take/Aggregate가 각각 filter/map/take/reduce에 해당하며, SQL 스타일 문법도 지원한다. C#은 2007년 LINQ를 도입한 선도적 멀티패러다임 언어다.

```csharp
// [코드 3-12] C#으로 구현
static int SumOfSquaresOfOddNumbers(int limit, List<int> list)
{
  return list.Where(a => a % 2 == 1)
    .Select(a => a * a)
    .Take(limit)
    .Aggregate(0, (a, b) => a + b);
}
```

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

**자바** — Stream API의 filter/map/limit/reduce를 사용한다.

```java
// [코드 3-14] 자바로 구현
public static int sumOfSquaresOfOddNumbers(int limit, List<Integer> list) {
  return list.stream()
    .filter(a -> a % 2 == 1)
    .map(a -> a * a)
    .limit(limit)          // take와 동일
    .reduce(0, Integer::sum);
}
```

> **참고**: 각 언어에서 `reduce`가 초깃값을 처리하는 방식에는 약간의 차이가 있다. 빈 컬렉션을 런타임에 만났을 때 발생할 수 있는 에러에 대해 언어가 개발자에게 처리 방법을 제안하도록 설계됐기 때문이다(7장의 reduce 에러 관리). 타입스크립트·자바스크립트의 reduce는 초깃값 없이 빈 이터러블을 만나면 에러를 전파한다.

결국 객체지향·명령형·함수형 패러다임을 결합한 멀티패러다임적 사고와 문제 해결 능력은 **특정 언어에 국한되지 않는다**. 강력한 타입 시스템과 타입 추론을 지원하는 이 언어들 모두에서 클래스와 인터페이스, 이터레이션 프로토콜, 함수형 고차 함수를 활용할 수 있다.

## 3. 하스켈로부터 배우기

하스켈(*Haskell - 순수 함수형 프로그래밍 언어*)은 순수 함수와 함수 합성을 강조하고, 커링이 기본이며, 지연 평가를 지원하고, 부수효과를 특별하게 관리한다. 강력한 타입 시스템과 타입 추론, 대수적 데이터 타입, 타입 클래스 등 함수형에 특화된 기능을 제공한다 — 8장의 `Maybe`, 13장의 모나드적 사고가 모두 하스켈의 어휘에서 왔다.

### 3.1 함수와 함수 시그니처

```haskell
-- [코드 3-15] 하스켈의 square 함수
square :: Int -> Int
square x = x * x
```

`square :: Int -> Int`는 `square`가 `Int`를 받아 `Int`를 반환함을 의미한다. `::`는 타입 선언, `=`는 함수 정의와 오른쪽 식의 결과 반환을 뜻한다. 타입스크립트로는 이렇다.

```typescript
// [코드 3-16] 타입스크립트의 square 함수
function square(x: number): number {
  return x * x;
}

// [코드 3-17] 타입스크립트로 함수 타입 정의
type Square = (x: number) => number;
const square: Square = x => x * x;
```

### 3.2 언어 차원에서 지원하는 커링

하스켈은 언어 차원에서 커링을 지원한다 — 3장에서 `_curry`를 직접 만들어야 했던 것과 달리, 모든 함수 호출에 커링이 기본 적용된다.

```haskell
-- [코드 3-18] add 함수
add :: Int -> Int -> Int
add x y = x + y

-- [코드 3-19] add 5 부분 적용
addFive :: Int -> Int
addFive = add 5
```

`addFive`는 `add`에 5를 부분 적용(*Partial Application*)한 결과로, `Int -> Int` 타입의 함수다.

```haskell
-- [코드 3-20] add 실행 완료
main :: IO ()
main = do
  print (addFive 10)  -- 출력: 15
  print (add 3 7)     -- 출력: 10
  print (3 `add` 7)   -- 출력: 10
```

하스켈에서 함수 호출을 중위(*Infix*) 연산자로 표현할 수도 있어 `` 3 `add` 7 ``과 `add 3 7`은 같다. `add :: Int -> Int -> Int`는 사실상 `add :: Int -> (Int -> Int)`와 동일한 의미다 — `add`는 `Int` 하나를 받아 `(Int -> Int)` 형태의 새로운 함수를 반환한다.

### 3.3 main 함수와 IO

하스켈의 모든 프로그램은 `main` 함수로 시작하고, `main`은 `IO` 타입을 반환해야 한다.

- `main :: IO ()`는 `main`이 `IO ()` 타입을 반환한다는 시그니처다. `IO`는 입출력 작업을 나타내는 타입이고 `()`는 특별히 반환할 값이 없다는 의미다.
- `do` 구문으로 여러 IO 액션을 순차 실행할 수 있다.

순수 함수형 언어인 하스켈은 입출력 같은 부수효과를 관리하기 위해 `IO` 타입을 사용한다. 어떤 함수가 `IO`를 반환한다면 **부수효과를 일으킬 수 있음을 타입 차원에서 명시**하는 것이다. 이로써 '순수 함수(`a -> b`)'와 'IO 함수(`a -> IO b`)'를 명확히 구분하고, 부수효과로 인한 예측 불가능성을 최소화한다 — 1장의 "순수하지 못한 작업의 격리"를 언어가 강제하는 형태다.

**Unit 타입 ()와 타입스크립트의 void**: 하스켈의 `()`는 유일한 값을 갖는 Unit 타입으로 '의미 없는 값'을 나타내며, 타입스크립트의 `void`와 개념적으로 유사한 역할을 한다 — 둘 다 '의미 있는 결과를 반환하지 않는 함수'를 표현한다.

### 3.4 head, map, filter, foldl 함수 시그니처

```haskell
-- [코드 3-21] head 함수
head :: [a] -> a

-- [코드 3-22] map 함수
map :: (a -> b) -> [a] -> [b]

-- [코드 3-23] filter 함수
filter :: (a -> Bool) -> [a] -> [a]

-- [코드 3-24] foldl 함수
foldl :: (b -> a -> b) -> b -> [a] -> b
```

`head`는 리스트의 첫 요소를 반환한다(`a`는 제네릭). `map`은 `[a]`의 각 요소에 `(a -> b)`를 적용해 `[b]`를 반환하고, `filter`는 `(a -> Bool)` 조건을 만족하는 요소만 남기며, `foldl`의 `(b -> a -> b)`는 누적 함수의 시그니처다. 타입스크립트로 `head`를 표현하면 다음과 같다.

```typescript
// [코드 3-21a] 타입스크립트 head 함수
type Head = <A>(arr: A[]) => A;
// 또는
type Head = <A>(iterable: Iterable<A>) => A;
```

하스켈은 제네릭 타입 변수로 `a`, `b` 같은 단일 문자를 사용한다. 이 단순하고 일관된 표기 덕분에 고차 함수를 매우 간결하게 표현할 수 있다 — 7장에서 `map<A, B>`의 타입을 읽던 방식이 바로 이 표기법의 타입스크립트 판이다.

### 3.5 함수 합성 — . 연산자와 $ 연산자

`.` 연산자는 함수를 합성한다. `f . g . h`는 `(\x -> f (g (h x)))`와 동일하다 — 자바스크립트로 `(x) => f(g(h(x)))`. `$` 연산자는 함수 적용 연산자로 우선순위를 조정해 괄호를 줄인다. `f $ g $ h x`는 `f (g (h x))`와 같다.

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

### 3.6 하스켈판 sumOfSquaresOfOddNumbers

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

`foldl (+) 0 . take limit . map square . filter odd $ list`는 오른쪽에서 왼쪽으로 읽는다.

1. `$ list`에 의해 `list`를 왼쪽에 합성된 함수들에게 전달한다.
2. `filter odd`가 홀수만 남긴다.
3. `map square`가 제곱한다.
4. `take limit`가 limit 개수만큼 선택한다.
5. `foldl (+) 0`이 합을 계산한다.

### 3.7 파이프라인 스타일 — &

함수 합성 연산자(`.`) 대신 정방향 함수 적용 연산자(`&`)를 쓰면 위에서 아래로 읽는 파이프라인이 된다.

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
```

타입스크립트의 체이닝 스타일과 유사한 가독성이다 — 3장의 `go`, 10장의 `fx` 체이닝, 클로저의 `->>`, 하스켈의 `&`는 모두 같은 요구(위에서 아래로 읽히는 합성)에 대한 각 언어의 답이다.

### 3.8 Either를 통한 에러 처리

하스켈은 예외를 try-catch 방식보다 **타입으로 에러 상황을 명시적으로 표현**하는 방식을 선호한다. 대표적인 것이 `Either`다 — 성공(`Right`)과 실패(`Left`)를 구분하여 함수의 결과를 명확히 표현함으로써, 컴파일 타임에 에러 처리가 필요함을 인지시킨다.

```haskell
-- [코드 3-28] 0으로 나누기 예제
main :: IO ()
main = do
  print (div 10 2)  -- 출력: 5
  print (div 10 0)  -- 예외 발생: divide by zero
```

기본 `div`는 0으로 나눌 때 예외를 발생시키지만, `Either`로 안전하게 만들 수 있다.

```haskell
-- [코드 3-29] 패턴 매칭과 Left, Right
safeDiv :: Int -> Int -> Either String Int
safeDiv _ 0 = Left "0으로 나눌 수 없습니다."
safeDiv x y = Right (div x y)
```

두 번째 인자가 0이면 `Left "..."`를 반환한다 — 런타임 예외 대신 **에러를 값으로** 표현한 것이다(13장의 Kleisli, 19장의 Result 타입과 같은 구도).

### 3.9 패턴 매칭

`safeDiv`는 하스켈의 패턴 매칭 문법으로 인자 패턴에 따라 함수 실행을 분기한다. `safeDiv _ 0`에서 `_`는 와일드카드(어떤 값이든 상관없음), `0`은 두 번째 인자가 0일 때를 나타낸다. 타입스크립트와 비교하면 — 함수 오버로드, if문, 타입 가드, 타입 좁히기, 매개변수 구조 분해의 역할을 **패턴 매칭 한 번**으로 해결한다.

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

`processResult`는 `Either String Int` 값을 받아 `Left`면 에러 메시지를, `Right`면 정상 결과를 반환한다. `Either`로 성공/실패 상태를 명시적으로 구분하면 에러를 런타임 예외 대신 타입으로 안전하게 처리할 수 있다. 하스켈에는 값이 없을 수도 있는 상황을 안전하게 처리하는 `Maybe` 타입도 있다(8장의 find에서 이미 만났다).

## 요약

- **Generator : Iterator : LISP = IP : OOP : FP** — 이터레이터는 제너레이터(명령형)로도, 객체 직접 구현(객체지향)으로도, 리스트 프로세싱 함수 조합(함수형)으로도 만들 수 있으며 서로 1:1:1로 대체된다.
- **for·if·break·변수 할당·합산은 각각 이터러블·filter·take·map·reduce로 대체**된다 — 코드 문장이 중첩된 리스트(코드이자 데이터)로 바뀌고, 지연 평가 덕분에 시간 복잡도는 동일하다.
- 이 철학은 클로저(`->>`), 코틀린(`asSequence`), 스위프트(`lazy`), 스칼라(`LazyList`), C#(LINQ), 자바(Stream)에서 같은 모양으로 반복된다 — **패러다임은 언어를 넘는다.**
- 하스켈은 **커링이 언어 기본값**이고(`Int -> Int -> Int` = `Int -> (Int -> Int)`), 함수 합성(`.`·`$`)과 파이프라인(`&`)을 연산자로 제공한다.
- 하스켈의 **IO 타입**은 부수효과를 타입 차원에서 격리하고, **Either·Maybe**는 실패와 부재를 예외가 아닌 값으로 표현하며, **패턴 매칭**은 분기·구조 분해·타입 좁히기를 한 문법으로 통합한다.

## 다른 챕터와의 관계

- **2장**: 명령형→함수형 대응표(9절)가 이 장의 `sumOfSquaresOfOddNumbers` 변환으로 완성됐다.
- **3장**: 직접 만들던 커링·파이프라인이 하스켈에서는 언어 기본 기능임을 확인했다.
- **8장**: find의 `Maybe`·`fromMaybe`가 이 장의 Either·패턴 매칭과 같은 계보다.
- **10장**: LISP의 코드=데이터 철학과 `->>` 매크로가 이 장의 다언어 비교로 이어졌다.
- **13장**: Either가 Kleisli 합성(실패를 값으로)의 타입 시스템 구현임이 드러난다.
- **16장**: 이 장의 리스트 프로세싱 사고가 실전 데이터와 패턴 9종으로 확장된다. **19장**: 패턴 매칭의 자바스크립트 도입 논의(TC39)와 Result 타입이 이어진다.
