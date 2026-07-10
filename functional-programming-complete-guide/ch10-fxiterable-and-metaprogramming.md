# Chapter 10: FxIterable and Metaprogramming (FxIterable과 메타프로그래밍)

## 핵심 질문

클래스·고차 함수·반복자·타입 시스템을 조합하면 어떻게 "언어를 확장한 듯한" 경험을 만들 수 있는가? LISP의 '코드가 데이터'라는 철학은 멀티패러다임 언어에서 어떤 형태로 실현되는가?

---

7장에서 고차 함수에 타입을 부여했고, 3장과 8장에서 파이프라인의 가독성 문제와 그 해법의 방향(체이닝)을 예고했다. 이 장에서 그 답을 완성한다 — 고차 함수들에 클래스를 결합하고 이터러블 패턴을 적용하여 데이터 스트림을 한층 가독성 높게 처리하는 구조, `FxIterable`을 만든다. 이 패턴은 이미 많은 현대 언어의 표준 라이브러리에서 널리 활용되고 있다.

이 장의 후반부는 이 모든 것의 사상적 뿌리인 LISP로 간다. 메타프로그래밍(*Metaprogramming - 프로그램이 자기 자신이나 다른 프로그램을 데이터처럼 바라보며 분석·변형·생성하거나 실행하는 프로그래밍 기법*)이란 프로그램이 코드를 데이터로 다루면서 동적으로 조작하고 확장하는 방식으로, 전통적인 LISP 계열 언어에서 극대화되었다. 타입스크립트 같은 현대 언어들은 LISP만큼 메타프로그래밍을 직접 지원하지는 않지만, 여러 언어 기능을 전략적으로 결합하면 그 이점을 실용적으로 구현할 수 있다.

> **참고**: 이 장의 `[코드 2-N]` 번호는 원본 멀티패러다임 노트(ch02) 기준이다.

---

## 1. Pipe Operator

잠시 미래에 다녀오자 — 아니, 어쩌면 과거일 수도 있다. 오른쪽 아래에서 왼쪽 위로 읽어야 하는 함수 중첩 코드는 가독성이 떨어질 수 있다. 몇몇 언어는 Pipe Operator를 지원하여 이 문제를 완화한다.

```typescript
// [코드 2-24] Pipe Operator
forEach(printNumber,
  map(n => n * 10,
    filter(n => n % 2 === 1,
      naturals(5))));
// 10
// 30
// 50

// Pipe Operator (Stage 2)
naturals(5)
  |> filter(n => n % 2 === 1, %)
  |> map(n => n * 10, %)
  |> forEach(printNumber, %)
// 10
// 30
// 50
```

지금까지 고차 함수들의 인자 순서를 `map(iterable, f)`가 아닌 **`map(f, iterable)`**로 설계한 이유가 여기서 드러난다. 정통 함수형 언어들의 인자 순서를 따른 것으로, 함수 중첩·Pipe Operator·커링을 지원할 때 가독성을 높인다. 만일 `map(iterable, f)` 순서라면 이렇게 작성해야 한다.

```typescript
// [코드 2-25] 인자 순서가 반대일 때
forEach(map(filter(naturals(5), n => n % 2 === 1), n => n * 10), printNumber);

naturals(5)
  |> filter(%, n => n % 2 === 1)
  |> map(%, n => n * 10)
  |> forEach(%, printNumber)
```

확실히 앞의 코드가 더 읽기 좋다. 다만 Pipe Operator 코드도 고차 함수의 첫 번째 인자 자리에 `%`가 있어 시선을 방해한다 — 그리고 이 연산자는 아직 표준화 논의(Stage 2) 단계다.

## 2. 클래스와 고차 함수, 반복자, 타입 시스템을 조합하기

Pipe Operator를 마냥 기다릴 필요는 없다. 객체지향 패러다임의 클래스와 이터러블, 함수형 함수, 타입 시스템을 결합하여 가독성 문제를 지금 해결해 보자.

### 2.1 제네릭 클래스로 Iterable 확장하기

`Iterable`을 확장한 제네릭 클래스를 만든다.

```typescript
// [코드 2-26] FxIterable<A> 클래스 정의
class FxIterable<A> {
  private iterable: Iterable<A>;
  constructor(iterable: Iterable<A>) {
    this.iterable = iterable;
  }
}
```

접근 제어자를 생성자 매개변수에 직접 명시하면(매개변수 프로퍼티) 필드 정의와 할당 코드를 생략할 수 있다.

```typescript
// [코드 2-27] FxIterable<A> 간결한 클래스 정의
class FxIterable<A> {
  constructor(private iterable: Iterable<A>) {}
}
```

`FxIterable<A>`의 타입 파라미터 `A`는 인스턴스를 생성하는 시점에 전달하는 `iterable` 인자의 타입에 따라 결정된다 — 제네릭 함수의 타입 파라미터가 호출 시점에 정해지는 방식과 유사하다(9장).

### 2.2 map 메서드 추가하기

7장에서 만든 `map` 함수를 활용해 메서드를 구현한다.

```typescript
// [코드 2-28] FxIterable<A>에 map 메서드 추가
class FxIterable<A> {
  constructor(private iterable: Iterable<A>) {}
  map<B>(f: (a: A) => B): FxIterable<B> {
    return new FxIterable(map(a => f(a), this.iterable));
  }
}

const mapped = new FxIterable(['a', 'b'])
  .map(a => a.toUpperCase())
  .map(b => b + b);
// [const mapped: FxIterable<string>]
// [a: string]
// [b: string]
```

`map` 메서드는 `this.iterable`에 `map(f)`를 적용한 이터러블 이터레이터를 만든 후 `FxIterable<B>`를 생성해 반환한다. 인스턴스는 체이닝 방식으로 `map`을 연속 실행할 수 있다 — **코드를 위에서 아래로 읽을 수 있고, 제네릭 덕분에 타입 추론도 원활하다.** 3장에서 예고한 "pipe의 타입 추론 문제에 대한 체이닝의 답"이 이것이다.

인스턴스 생성을 간결하게 하는 헬퍼 함수 `fx`를 추가한다.

```typescript
// [코드 2-29] fx 헬퍼 함수 추가
function fx<A>(iterable: Iterable<A>): FxIterable<A> {
  return new FxIterable(iterable);
}

const mapped2 = fx(['a', 'b'])
  .map(a => a.toUpperCase())
  .map(b => b + b);
// [const mapped2: FxIterable<string>]
```

### 2.3 filter, forEach 메서드 만들기

```typescript
// [코드 2-30a] filter, forEach 메서드 추가 (fx로 간결하게)
class FxIterable<A> {
  constructor(private iterable: Iterable<A>) {}
  map<B>(f: (a: A) => B): FxIterable<B> {
    return fx(map(f, this.iterable));
  }
  filter(f: (a: A) => boolean): FxIterable<A> {
    return fx(filter(f, this.iterable));
  }
  forEach(f: (a: A) => void): void {
    return forEach(f, this.iterable);
  }
}
```

```typescript
// [코드 2-31] map, forEach 사용 예제
fx(['a', 'b'])
  .map(a => a.toUpperCase())
  .map(a => a + a)
  .forEach(a => console.log(a));
// AA
// BB
```

세 가지 표기를 나란히 비교해 보자.

```typescript
// [코드 2-32] naturals, filter, map, forEach
// 함수 중첩
forEach(printNumber,
  map(n => n * 10,
    filter(n => n % 2 === 1,
      naturals(5))));

// 파이프 오퍼레이터
naturals(5)
  |> filter(n => n % 2 === 1, %)
  |> map(n => n * 10, %)
  |> forEach(printNumber, %)

// 체이닝
fx(naturals(5))
  .filter(n => n % 2 === 1)
  .map(n => n * 10)
  .forEach(printNumber);
// 10
// 30
// 50
```

함수 중첩과 파이프 오퍼레이터도 충분히 가독성이 있지만, 체이닝은 현대 언어의 접근 방식(자바스크립트 Array 메서드 체이닝, 자바 스트림 API)과 유사해 익숙하고, 데이터 변환의 각 단계가 명확하게 드러난다. 또한 사용할 수 있는 메서드를 **IDE 힌트**로 제공받을 수 있다는 실용적 장점도 있다.

### 2.4 reduce 메서드 만들기

```typescript
// [코드 2-33] FxIterable<A>에 reduce 메서드 추가
class FxIterable<A> {
  constructor(private iterable: Iterable<A>) {}
  // ... 메서드 생략 ...
  reduce<Acc>(f: (acc: Acc, a: A) => Acc, acc: Acc): Acc {
    return reduce(f, acc, this.iterable);
  }
}
```

reduce는 7장에서처럼 초깃값 생략을 지원해야 하므로 메서드 오버로드를 적용한다(메서드 오버로드는 함수 오버로드와 동일한 방식이다).

```typescript
// [코드 2-34] reduce 메서드 오버로드
class FxIterable<A> {
  constructor(private iterable: Iterable<A>) {}
  // ... 메서드 생략 ...
  reduce<Acc>(f: (acc: Acc, a: A) => Acc, acc: Acc): Acc;       // ①
  reduce<Acc>(f: (a: A, b: A) => Acc): Acc;                     // ②
  reduce<Acc>(f: (a: Acc | A, b: A) => Acc, acc?: Acc): Acc {
    return acc === undefined
      ? reduce(f, this.iterable)   // ③
      : reduce(f, acc, this.iterable); // ④
  }
}
```

- ① 초깃값 `acc`를 포함해 호출될 때의 시그니처. `f`는 누적값 `acc`와 요소 `a`를 받아 새로운 누적값을 반환한다.
- ② 초깃값 없이 호출될 때의 시그니처. 이터러블의 첫 번째 요소가 초깃값으로 사용된다.
- ③ `acc`가 `undefined`인 경우 — `reduce(f, this.iterable)`을 호출해 내부에서 첫 요소를 초깃값으로 처리한다.
- ④ `acc`가 있는 경우 — `reduce(f, acc, this.iterable)`을 호출한다.

```typescript
// [코드 2-35] reduce 메서드 사용 예제
// 초깃값이 없을 때
const num = fx(naturals(5))             // FxIterable<number> (1, 2, 3, 4, 5)
  .filter(n => n % 2 === 1)             // FxIterable<number> (1, 3, 5)
  .map(n => n * 10)                     // FxIterable<number> (10, 30, 50)
  .reduce((a, b) => a + b);             // [a: number] [b: number]
console.log(num); // [num: number]
// 90

// 초깃값이 있을 때
const num2 = fx(naturals(5))
  .filter(n => n % 2 === 1)
  .map(n => n * 10)
  .reduce((a, b) => a + b, 10);
console.log(num2);
// 100
```

map·filter·reduce·forEach 메서드로 체이닝을 활용한 가독성 좋고 안전하며 유지보수하기 쉬운 코드를 작성할 수 있게 되었다.

## 3. LISP(클로저)에서 배우기 — 코드가 데이터, 데이터가 코드

잠시 LISP 이야기를 하자. LISP의 가장 큰 특징은 **'코드가 데이터이고 데이터가 코드'**라는 개념이다. 프로그래밍 언어의 구문을 데이터 구조로 표현하고 조작할 수 있어, 프로그램이 동적으로 새로운 코드를 생성하고 실행할 수 있다 — 메타프로그래밍을 비롯한 고급 기법의 기반이다.

여기서는 LISP 계열 언어인 클로저(*Clojure - 리치 히키(Rich Hickey)가 2007년에 개발한 JVM 기반 함수형 언어. 불변성과 일급 함수를 강조하며 코드와 데이터를 동일하게 취급한다*)를 예로 든다.

### 3.1 S-표현식

LISP의 S-표현식은 리스트 형태의 구문 표현이다. `(+ 1 2)`는 숫자 1과 2를 더하는 **코드이자** 동시에 리스트 형태의 **데이터**다.

```clojure
;; [코드 2-36] 실행될 코드가 곧 리스트
(+ 1 2)
```

- 첫 번째 요소: 연산자(함수) `+`
- 나머지 요소: 피연산자 `1`과 `2`

LISP 계열 언어에서 함수 호출은 리스트 구조로 이루어지며, 리스트의 첫 요소가 함수, 뒤 요소들이 인자다. 이를 타입스크립트로 단순화해 표현하면 다음과 같다.

```typescript
// [코드 2-37] 리스트는 값
[add, 1, 2]
```

`[add, 1, 2]` 자체는 배열이고 데이터다. 이 데이터를 평가하는 함수가 있다면 데이터를 코드로 만들어 평가할 수 있다.

```typescript
// [코드 2-37a] 리스트를 평가하는 함수
type Evaluatable<A, B> = [(...args: A[]) => B, ...A[]]; // ①
function evaluation<A, B>(expr: Evaluatable<A, B>) {     // ②
  const [fn, ...args] = expr;
  return fn(...args);
}

const add = (a: number, b: number) => a + b;
const result: number = evaluation([add, 1, 2]);           // ③
console.log(result); // 3
```

- ① `Evaluatable<A, B>`: 첫 요소는 함수 타입, 그 뒤로 함수의 인자에 해당하는 값들이 이어지는 형태를 타입으로 표현했다.
- ② `evaluation` 함수: 구조 분해로 첫 요소를 함수(`fn`), 나머지를 인자 배열(`args`)로 추출하고 `fn(...args)`를 호출한다 — 리스트 형태의 '코드'를 실제 함수 호출로 '평가'하는 과정이다.
- ③ `[add, 1, 2]`는 '`add`를 인자 1, 2로 호출한다'는 의미를 갖는 데이터 구조이고, 평가하면 3이 나온다.

이 타입스크립트 예제는 **런타임 시점에만** 코드 구조를 데이터로 활용한다. 반면 LISP는 **컴파일 타임에도** 코드를 데이터로 다룰 수 있어, 코드 자체를 변환하고 런타임에 실행될 코드를 재구성하는 더 강력한 조작 능력을 갖는다(3.4절의 매크로).

### 3.2 클로저에서 map이 실행될 때

```clojure
;; [코드 2-38] map 사용 예제
(map #(+ % 10) [1 2 3 4])
```

- 첫 번째 요소: 함수 `map`
- 두 번째 요소: 익명 함수 `#(+ % 10)` (현재 요소에 10을 더하는 함수)
- 세 번째 요소: 벡터 `[1 2 3 4]` (클로저에서 `[]`는 벡터, `()`는 리스트)

평가하면 `(11 12 13 14)`라는 **지연 시퀀스**가 된다 — 아직 어디에도 소비되지 않았으므로 실제로 값이 필요할 때 평가가 완료된다. `#(+ % 10)`은 리더 매크로(*Reader Macro - 소스 코드를 읽는 단계에서 특정 기호나 패턴을 다른 코드 형태로 치환하는 기능*)에 의해 `(fn [x] (+ x 10))` 형태의 익명 함수로 확장된다 — 함수 정의 구문 자체가 '코드이자 데이터 구조'다.

```clojure
;; [코드 2-39] let과 구조 분해
(let [[first second] (map #(+ % 10) [1 2 3 4])]
  (println first second))
;; 11 12
```

`let`에서 `[first second]`로 구조를 분해하면 처음 두 요소만 추출하면서 **필요한 부분만 평가**한다. LISP 계열 언어에서 코드는 리스트로 표현되고, 리스트는 평가되기 전까지 단순한 데이터 구조다. 코드와 데이터를 동일한 형태로 다루며 필요할 때 점진적으로 평가하는 것 — 이것이 LISP의 핵심 강점이다.

### 3.3 FxIterable을 LISP의 리스트처럼 만들기

클로저 예제와 동일한 시간 복잡도(지연 평가)와 표현력을 갖도록 `FxIterable`을 확장해 보자. 우선 배열 변환 메서드로 시도해 본다.

```typescript
// [코드 2-40] toArray() 메서드 추가
class FxIterable<A> {
  constructor(private iterable: Iterable<A>) {}
  // ... 메서드 생략 ...
  toArray(): A[] {                                              // ①
    return [...this.iterable];
  }
}

const [first, second] = fx([1, 2, 3, 4]).map(a => a + 10).toArray(); // ②
console.log(first, second); // 11 12                             // ③
```

- ① `toArray()`는 내부 이터러블을 전개 연산자로 배열로 변환해 반환한다.
- ② `map()` 후 `toArray()`로 배열을 얻는다.
- ③ 구조 분해로 첫 두 값을 얻는다.

원하는 결과는 얻었지만 두 가지가 아쉽다 — `.toArray()`라는 추가 코드, 그리고 `toArray()`가 **모든 요소를 평가**해 길이 4의 배열을 만든다는 점. 해결책은 이미 알고 있다. `FxIterable`을 **이터레이션 프로토콜을 따르는 값**으로 만들면 된다.

```typescript
// [코드 2-41] LISP의 리스트 같은 이터러블
class FxIterable<A> {
  constructor(private iterable: Iterable<A>) {}
  [Symbol.iterator]() {
    return this.iterable[Symbol.iterator]();
  }
  // ... 메서드 생략 ...
}

const [first, second] = fx([1, 2, 3, 4]).map(a => a + 10);
console.log(first, second); // 11 12
```

`[Symbol.iterator]()` 메서드 하나로 충분하다. `toArray()` 없이 구조 분해가 되고, **10을 더하는 연산이 단 두 번만 실행된다** — 클로저의 지연 시퀀스와 같은 효율이다.

## 4. LISP의 확장성 — 매크로와 메타프로그래밍

아직 평가되지 않은 리스트가 있다면 여기에 동적으로 다른 코드를 추가할 수 있다. 개발자가 요소를 제거하는 함수를 만들어 리스트의 첫 요소로 두면, 그 리스트는 **새로운 연산자와 함수로 구성된 코드**처럼 동작한다 — 개발자가 스스로 언어를 확장하는 것이다.

```clojure
;; [코드 2-42] reject 함수 적용
(defn reject [pred coll]                                        ;; ①
  (filter (complement pred) coll))

(let [[first second] (reject odd? (map #(+ % 10) [1 2 3 4 5 6]))] ;; ②
  (println first second))                                         ;; ③
;; 12 14                                                          ;; ④
```

1. `reject`는 `pred` 조건을 만족하지 않는 요소만 남기기 위해 `filter`와 `complement`를 사용한다.
2. `(map #(+ % 10) [1 2 3 4 5 6])`이 `(11 12 13 14 15 16)`을 만들고, `reject odd?`가 홀수를 제거해 `(12 14 16)`을 반환하며, 구조 분해로 처음 두 요소를 바인딩한다.
3. 출력 결과는 ④ `12 14`다.

> **참고**: 이 `reject`는 4장에서 es5로 만든 `_reject = _filter + _negate`와 같은 함수다. 클로저의 `complement`가 `_negate`에 해당한다 — 같은 조합적 아이디어가 언어를 건너 반복된다.

### 4.1 매크로

LISP 계열 언어에서 매크로는 단순한 텍스트 치환이 아니라 **코드(리스트)를 입력받아 코드(리스트)를 반환하는 함수**다. 컴파일 타임에 작동하여 코드가 아직 '구문' 상태일 때 원하는 형태로 재구성한다. 유명한 예제인 `unless` 매크로를 보자.

```clojure
;; [코드 2-43] unless 매크로
(defmacro unless [test body]
  `(if (not ~test) ~body nil))
```

함수 호출에서는 인자들이 먼저 평가된 뒤 전달되지만, 매크로에서는 인자들이 **평가되지 않은 '원본 코드 형태'**로 주어진다.

```clojure
;; [코드 2-44] unless 매크로 사용 예제
(unless false
  (println "조건이 거짓이므로 이 문장은 실행됩니다."))
```

`false`는 `test`로, `(println ...)`은 `body`로 — 평가되지 않은 코드 조각(리스트) 그대로 매크로에 넘어간다. `unless` 매크로는 이 코드 조각들로 컴파일 타임에 새로운 코드를 생성한다.

```clojure
;; [코드 2-45] unless 매크로 변환 후 실제로 실행될 코드
(if (not false)
  (println "조건이 거짓이므로 이 문장은 실행됩니다.")
  nil)
```

`unless`는 코드를 입력받아 최종적으로 실행될 새로운 코드 조각을 반환하는 **코드 변환기**다. 이로써 개발자는 언어가 제공하지 않는 새로운 구문이나 기능을 마음껏 만들 수 있다.

### 4.2 ->> 매크로 — 파이프라인

클로저에서는 파이프라인 형태의 코드를 `->>` 매크로로 표현한다.

```clojure
;; [코드 2-46] 파이프라인으로 표현
(let [[first second] (->> [1 2 3 4 5 6]          ;; ①, ②
                          (map #(+ % 10))         ;; ③
                          (reject odd?))]         ;; ④
  (println first second))                         ;; ⑤
;; 12 14                                          ;; ⑥
```

`->>` 매크로는 첫 인자를 그다음 함수의 마지막 인자로 전달해 나간다. `unless`나 `->>` 같은 매크로를 개발자가 직접 정의할 수 있고 특수문자·기호를 활용한 표현도 가능하다 — 프로그램의 구문을 데이터 구조로 표현하고 지연된 값처럼 다룰 수 있는 LISP의 특성 덕분이다. 3장에서 만든 `_pipe`/`go`, 1절의 Pipe Operator가 모두 이 아이디어의 후예다.

### 4.3 reject 메서드를 FxIterable에 추가하기

클로저의 `reject`와 동일하게 동작하는 메서드를 추가한다.

```typescript
// [코드 2-47] FxIterable 클래스에 reject 메서드 추가
class FxIterable<A> {
  constructor(private iterable: Iterable<A>) {}
  [Symbol.iterator]() {
    return this.iterable[Symbol.iterator]();
  }
  // ... 메서드 생략 ...
  reject(f: (a: A) => boolean): FxIterable<A> {
    return this.filter(a => !f(a));
  }
}

const isOdd = (a: number) => a % 2 === 1;
```

```typescript
// [코드 2-48] FxIterable 체이닝과 구조 분해 할당
const [first, second] = fx([1, 2, 3, 4, 5, 6])
  .map(a => a + 10)
  .reject(isOdd);

console.log(first, second);
// 12 14
```

클로저 판과 나란히 놓고 보면, 두 예제는 같은 프로그래밍 패러다임과 철학을 공유하며 본질적으로 동일한 의미와 가치를 구현하고 있다.

### 4.4 코드, 객체, 함수가 협력하여 구현한 언어의 확장

```typescript
// [코드 2-48a] FxIterable 체이닝과 구조 분해 할당
const [first, second] = fx([1, 2, 3, 4, 5, 6])
  .map(a => a + 10)
  .reject(isOdd);
```

이 코드를 분류하면 각 패러다임의 역할이 보인다.

- **구조 분해 할당(명령형 문법)**: `const [first, second]`
- **객체지향 메서드 체이닝 패턴**: `fx().map().reject()`
- **함수형 고차 함수와 LISP**: `map = (f: (a: A) => B, iterable: Iterable<A>) => Iterable<B>`

이 외에도 제너레이터(명령형), 이터레이터(객체지향 패턴), 일급 함수, 클래스, 제네릭과 타입 추론이 상호작용하고 있다. 이 코드는 특정 도메인의 구현체가 아니라 어디서나 쓰일 수 있는 **범용적인 언어의 면모**를 보여준다 — 기존 언어의 설계와 철학에서 벗어나지 않았기 때문에 컴파일 타임 타입 처리·런타임 에러 처리와 잘 맞물리고, 앞으로 나올 언어의 신규 기능들과도 상호작용할 것이다.

> **핵심 통찰**: 이터레이션 프로토콜을 매개로 명령형 문법·객체지향 패턴·함수형 고차 함수가 협력하면, 언어 스펙이나 컴파일러를 변경하지 않고도 "언어를 확장한 것 같은" 수준의 추상화와 유연성을 얻는다.

## 5. 런타임에서 동적으로 기능 확장하기

### 5.1 to — 다른 타입으로 변환하며 체이닝 이어가기

`FxIterable`은 이터러블이므로 전개 연산자로 `Array`로 변환할 수 있지만, `toArray()`를 쓰면 **체이닝을 이어갈 수 있다**는 특징이 있다.

```typescript
// [코드 2-49] toArray() 체이닝
const sorted = fx([5, 2, 3, 1, 4, 5, 3])
  .filter(n => n % 2 === 1)
  .map(n => n * 10)
  .toArray()                  // Array<number>로 변환
  .sort((a, b) => a - b);    // Array.prototype.sort로 오름차순으로 정렬
console.log(sorted);
// [10, 30, 30, 50, 50]

const sorted2 = [...fx([5, 2, 3, 1, 4, 5, 3])
  .filter(n => n % 2 === 1)
  .map(n => n * 10)
]
  .sort((a, b) => a - b);
console.log(sorted2);
// [10, 30, 30, 50, 50]
```

`sorted2`는 대괄호와 괄호가 중첩되며 시선이 map까지 갔다가 전개 연산자 시작으로 올라가고 다시 내려온다. 메서드 체이닝은 순차적으로 읽히므로 가독성이 더 좋다.

`toArray`처럼 다른 타입으로 만드는 메서드를 개발자가 **동적으로 확장**할 수 있도록 `to` 메서드를 제공한다.

```typescript
// [코드 2-50] 동적으로 컨버터 생성을 가능하게 하는 to 메서드
class FxIterable<A> {
  constructor(private iterable: Iterable<A>) {}
  [Symbol.iterator](): Iterator<A> {
    return this.iterable[Symbol.iterator]();
  }
  // ... 메서드 생략 ...
  to<R>(converter: (iterable: Iterable<A>) => R): R {
    return converter(this.iterable);
  }
}

const sorted = fx([5, 2, 3, 1, 4, 5, 3])
  .filter(n => n % 2 === 1)
  .map(n => n * 10)
  .to(iterable => [...iterable])        // iterable을 받아 전개 연산자로 배열로 변환
  .sort((a, b) => a - b);
console.log(sorted); // [10, 30, 30, 50, 50]
// const sorted: number[]
```

`Array`로 변환되며 타입도 `Array`로 추론되어, `sort`의 `compareFn` 인자 타입까지 `number`로 잘 추론된다. 사실 `FxIterable` 자체가 이터러블이므로 `this`만 넘기도록 구현해도 동일하게 동작한다.

```typescript
// [코드 2-51] this로 변경
class FxIterable<A> {
  constructor(private iterable: Iterable<A>) {}
  [Symbol.iterator](): Iterator<A> {
    return this.iterable[Symbol.iterator]();
  }
  // ... 메서드 생략 ...
  filter(f: (a: A) => boolean) {
    return fx(filter(f, this));            // <- return fx(filter(f, this.iterable));
  }
  toArray() {
    return [...this];                      // <- return [...this.iterable];
  }
  to<R>(converter: (iterable: this) => R): R {
    return converter(this);                // <- return converter(this.iterable);
  }
}
```

`to`를 이용하면 배열이 아닌 값으로도 변환하여 체이닝을 이어갈 수 있다.

```typescript
// [코드 2-52] Set으로 변환
const set = fx([5, 2, 3, 1, 4, 5, 3])
  .filter(n => n % 2 === 1)
  .map(n => n * 10)                              // [50, 30, 10, 50, 30]
  .to(iterable => new Set(iterable));             // Set으로 만들어지면서 중복된 요소 제거
console.log(set);
// Set(3) {50, 30, 10}

const size = fx([5, 2, 3, 1, 4, 5, 3])
  .filter(n => n % 2 === 1)
  .map(n => n * 10)
  .to(iterable => new Set(iterable))
  .add(10)
  .add(20)
  .size;
console.log(size);
// 4
```

`Set`으로 변환한 뒤 `add`·`size` 같은 **객체지향적인 객체의 메서드**로 자연스럽게 이어진다. 자바스크립트의 `Set`은 집합 메서드들도 지원하므로 이렇게 멀티패러다임적으로 활용할 수 있다.

```typescript
// [코드 2-53] Set.prototype.difference
const set = fx([5, 2, 3, 1, 4, 5, 3])
  .filter(n => n % 2 === 1)
  .map(n => n * 10)
  .to(iterable => new Set(iterable))          // Set으로 변환, 중복 요소 제거: Set {50, 30, 10}
  .difference(new Set([10, 20]));              // Set에서 [10, 20]과의 차집합: Set {50, 30}
console.log([...set]);
// [50, 30]
```

### 5.2 chain — 이터러블을 반환하는 함수로 확장하기

`to`와 유사하지만, 이터러블을 반환하는 함수를 받아 그 결과를 **다시 `FxIterable`로 이어가는** `chain` 메서드를 추가한다.

```typescript
// [코드 2-54] FxIterable 클래스에 chain 메서드 추가
class FxIterable<A> {
  constructor(private iterable: Iterable<A>) {}
  [Symbol.iterator](): Iterator<A> {
    return this.iterable[Symbol.iterator]();
  }
  // ... 메서드 생략 ...
  chain<B>(f: (iterable: this) => Iterable<B>): FxIterable<B> {
    return fx(f(this)); // new FxIterable(f(this));
  }
}
```

```typescript
// [코드 2-55] chain + Set
const result = fx([5, 2, 3, 1, 4, 5, 3])
  .filter(n => n % 2 === 1)
  .map(n => n * 10)                              // [50, 30, 10, 50, 30]
  .chain(iterable => new Set(iterable))           // Set으로 중복 제거, Set도 이터러블
  .reduce((a, b) => a + b);
console.log(result);
// 90

const result2 = fx([5, 2, 3, 1, 4, 5, 3])
  .filter(n => n % 2 === 1)
  .map(n => n * 10)
  .chain(iterable => new Set(iterable))
  .map(n => n - 10)
  .reduce((a, b) => `${a}, ${b}`);
console.log(result2);
// 40, 20, 0
```

`chain`으로 이터러블을 반환하는 어떤 함수든 동적으로 만들어 `FxIterable`을 **런타임에 확장**할 수 있다. 타입 추론이 원활하게 이뤄지도록 설계했기 때문에 별도의 타입 명시 없이도 안전하게 값 변환과 체이닝을 이어갈 수 있다.

## 6. 언어를 확장하는 즐거움

개발자가 언어를 즉시 확장할 수 있다는 점 — 이것이 메타프로그래밍의 가장 매력적인 특징이다. 객체지향 기반 언어가 LISP 계열의 메타프로그래밍 수준에 한 걸음 다가갈 수 있었던 전환점은 **일급 함수의 도입**이었다. 과거에도 인터페이스와 반복자 패턴은 있었지만, 반복자 내부에서 외부 함수를 받아 실행할 수 있는 일급 함수가 없었다면 함수형 패러다임의 다양한 함수를 구현할 수 없었을 것이다.

일급 함수의 도입은 비교적 최근 일이다. 2013년 전후 모바일 앱 개발의 두 축이던 Objective-C와 자바 모두 일급 함수를 지원하지 않았다(Objective-C의 블록(Block)은 람다와 거리가 있었고, 변수 캡처 문법이 복잡하며 메모리를 직접 관리해야 했다).

- 자바는 2014년 자바 8에서 일급 함수와 스트림 API를 도입했다.
- 스위프트는 2014년 첫 출시부터 `Sequence`·`Iterator` 프로토콜과 일급 함수를 지원했다.
- 자바스크립트와 타입스크립트는 2015년 ES6부터 이터레이터와 제너레이터를 포함시켰다.
- 코틀린은 2016년 초기 릴리즈부터 일급 함수와 `Iterable` 기반 이터레이션을 제공했다.
- C#은 초기부터 `IEnumerable`/`IEnumerator`를 제공했으며 2007년 LINQ로 다양한 헬퍼를 지원하기 시작했다.

정리하면 — 클래스 기반 반복자 패턴에 일급 함수가 결합되면서 다양한 언어들이 멀티패러다임 언어로 진화했고, 이터레이션 프로토콜 덕분에 일관되고 표준화된 방식으로 언어 기능을 확장할 수 있게 되었다. 현대 언어들이 LISP의 메타프로그래밍과 동일한 범위를 제공하지는 않지만, 충분히 풍부한 추상화를 구현할 수 있으며 강력한 타입 시스템과 객체지향 지원까지 더해 주류 언어로 자리잡았다.

## 요약

- 고차 함수의 인자 순서(`map(f, iterable)`)는 중첩·Pipe Operator·커링의 가독성을 위한 설계다 — Pipe Operator(`|>`)는 아직 Stage 2이므로, **클래스 체이닝**이 현재의 실용 해법이다.
- **FxIterable<A>**: 제네릭 클래스 + 매개변수 프로퍼티 + 7장의 고차 함수를 메서드로 감싸 체이닝을 만들고, 메서드 오버로드로 reduce의 초깃값 생략을 지원한다 — 타입 추론이 체인 끝까지 흐른다.
- `[Symbol.iterator]()` 하나를 구현하면 FxIterable은 **LISP의 리스트처럼** 동작한다 — 구조 분해가 필요한 만큼만 평가하는 지연 시퀀스가 된다.
- LISP의 **S-표현식**은 코드가 곧 데이터라는 철학의 구현이며, **매크로**는 코드를 받아 코드를 반환하는 컴파일 타임 코드 변환기다(`unless`, `->>`).
- **to**(다른 타입으로 변환해 체이닝 지속)와 **chain**(이터러블 반환 함수로 확장)으로 FxIterable을 런타임에 동적으로 확장하고, Set 같은 객체지향적 객체와도 호흡한다.
- 반복자 패턴 + 일급 함수 + 이터레이션 프로토콜의 결합이 언어를 컴파일러 수정 없이 확장하는 길을 열었다 — 멀티패러다임 언어 진화의 핵심 동력.

## 다른 챕터와의 관계

- **3장**: pipe의 TS 타입 추론 한계에 대한 답(체이닝)이 이 장에서 완성됐다.
- **4장**: es5 `_reject`(`_filter + _negate`)가 클로저의 `reject`(`filter + complement`)와 FxIterable의 `reject` 메서드로 세 번 반복됐다 — 같은 조합적 아이디어의 언어별 구현.
- **5·7장**: 이터레이션 프로토콜과 고차 함수가 FxIterable의 재료다.
- **8장**: `fx(...)` 표기의 구현이 이 장이며, `.to(head)` 같은 조합이 find에 쓰였다.
- **14장**: FxIterable이 FxAsyncIterable과 짝을 이뤄 동기·비동기 통합 체이닝으로 확장됐다.
- **16장**: 이 장의 수제 FxIterable에 해당하는 실전 라이브러리(FXTS)를 사용한다.
