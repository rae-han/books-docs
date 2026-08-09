# Chapter 1: Multi-Paradigm Extends Modern Languages (멀티패러다임이 현대 언어를 확장하는 방법)

## 핵심 질문

현대 프로그래밍 언어에서 객체지향 디자인 패턴의 반복자 패턴과 함수형 패러다임의 일급 함수는 어떻게 만나 멀티패러다임 언어로의 발전을 이끌었는가? 이터레이션 프로토콜은 왜 상속이 아닌 인터페이스로 설계되었는가?

---

과거에는 함수형 패러다임을 사용하려면 함수형 언어를, 객체지향 패러다임을 사용하려면 객체지향 언어를 선택해야 했다. 그러나 오늘날 대부분의 프로그래밍 언어는 멀티패러다임 언어로 발전했다. 2010년 즈음부터 이러한 변화가 본격적으로 시작되어 특히 2020년 이후에는 현업에서 사용하는 언어가 거의 명령형, 객체지향, 함수형 패러다임을 동시에 지원하게 되었다.

많은 프로그래밍 언어가 처음에는 객체지향 패러다임을 기반으로 시작했지만, 일급 함수를 도입하고 지연성을 적용한 이터레이션 헬퍼 함수나 비동기를 다루는 내장 객체 등을 포함하며 다각도로 발전했다. 그 결과 이제 하나의 언어에서 다양한 패러다임을 성숙한 수준으로 활용할 수 있게 되었다.

모든 프로그래밍 패러다임은 성공적인 소프트웨어 개발을 위한 도구다. 우리는 그동안 어느 하나의 방식이나 개념만 사용하도록 프로젝트와 코드를 구성하고 통합하려 했던 경향이 있다. 하지만 이는 오히려 더 나은 프로그래밍으로 나아갈 기회를 제약할 수 있다. 어떤 문제는 명령형으로 푸는 것이 적합하고, 어떤 문제는 함수형, 또 어떤 문제는 객체지향이 더 효과적일 수 있다. 오늘날은 다양한 패러다임을 효과적으로 조합해 더 나은 코드를 작성할 수 있는 시대다.

이 책에서는 서로 다른 패러다임이 어우러져 탄생하는 아름다운 코드와 문제 해결 방식을 함께 탐구한다. 첫 장에서는 이러한 패러다임들이 조화롭게 만나기 시작한 이야기로 앞으로 이어질 긴 여정을 열어본다.

---

## 1. 객체지향 디자인 패턴의 반복자 패턴과 일급 함수

함수형 프로그래밍을 중심으로 프로그래밍을 하던 어느 날, 요즘의 멀티패러다임 언어에서는 함수형 패러다임을 적용하는 방법으로 반복자(*Iterator*) 패턴을 활용한다는 점을 깊게 생각하게 되었다. 다시 생각해보니 이 반복자 패턴은 십여 년 전에 접했던 GoF의 객체지향 디자인 패턴 중 하나였다.

객체지향 기반 언어들은 반복자 패턴을 통해 지연성 있는 이터레이션 프로토콜을 구현했다. 이후 일급 함수가 추가되면서 이를 바탕으로 `map`, `filter`, `reduce`, `take` 같은 이터레이터 헬퍼 함수들이 구현될 수 있었다. 시간이 흐르며 이러한 함수들은 언어의 핵심 기능으로 자리잡아 빌트인 형태로 제공되기 시작했다.

객체지향 디자인 패턴인 반복자 패턴과 함수형 패러다임의 일급 함수가 만나 함수형 패러다임의 지연 평가와 리스트 프로세싱(*List Processing - 리스트 형태의 데이터를 map, filter, reduce 등의 함수로 처리하는 패러다임*)을 구현해 나간 것이다. 여러 패러다임이 서로 협력하여 함수형 패러다임 지원을 더욱 고도화했으며 결과적으로 더욱 멀티패러다임적인 언어로 발전했다.

### 1.1 GoF의 반복자 패턴

반복자 패턴은 객체지향 디자인 패턴 중 하나로, 컬렉션의 요소를 순차적으로 접근하는 규약을 제시한다. 반복자 패턴은 GoF(*Gang of Four - 에릭 감마, 리처드 헬름, 랄프 존슨, 존 블리시디스를 가리키는 별칭*)가 1994년에 발표한 「GoF의 디자인 패턴」에서 소개되었다.

다음은 반복자의 구조를 타입스크립트의 인터페이스 정의를 사용해 표현한 코드다 [코드 1-1].

```typescript
// [코드 1-1] Iterator 인터페이스
interface IteratorYieldResult<T> { // ①
  done?: false;
  value: T;
}

interface IteratorReturnResult { // ②
  done: true;
  value: undefined;
}

interface Iterator<T> { // ③
  next(): IteratorYieldResult<T> | IteratorReturnResult;
}
```

- ① `IteratorYieldResult<T>`: `done`이 `false`인 경우와 `value`가 `T` 타입인 값을 나타낸다. 반복자가 아직 완료되지 않았음을 의미한다.
- ② `IteratorReturnResult`: `done`이 `true`이고 `value`가 `undefined`인 값을 나타낸다. 반복자가 완료되었음을 의미한다.
- ③ `Iterator<T>`: `next()` 메서드를 가진 인터페이스로 `IteratorYieldResult<T>` 또는 `IteratorReturnResult` 중 하나를 반환한다.

반복자 패턴은 컬렉션의 내부 구조를 노출하는 대신 `next()` 같은 public 메서드로 내부 요소에 접근할 수 있도록 설계되었다. 이는 컬렉션의 실제 구조와 상관없이 다양한 컬렉션 스타일 데이터의 요소를 일관된 방식으로 순회할 수 있게 한다.

> **참고**: [코드 1-1]은 이번 장의 핵심 내용을 간결하게 전달하기 위해 축약된 형태를 사용했다. 타입스크립트에서 공식적으로 제공하는 Iterator 인터페이스는 `lib.es2015.iterable.d.ts` 파일을 참고하면 확인할 수 있다.

### 1.2 ArrayLike로부터 Iterator 생성하기

다음은 `ArrayLike`를 받아서 이를 순회하는 Iterator를 생성하는 클래스를 구현한 코드다 [코드 1-2]. 함수와 객체 리터럴로 더 간결하게 구현할 수도 있지만 이번에는 `class`와 `implements`를 사용하는 좀 더 전통적인 방식을 따랐다.

```typescript
// [코드 1-2] ArrayLike로부터 Iterator를 생성하는 클래스
/* lib.es5.ts
interface ArrayLike<T> {
  readonly length: number;
  readonly [n: number]: T;
}
*/
class ArrayLikeIterator<T> implements Iterator<T> {
  private index = 0;
  constructor(private arrayLike: ArrayLike<T>) {}

  next(): IteratorResult<T> {
    if (this.index < this.arrayLike.length) {
      return {
        value: this.arrayLike[this.index++],
        done: false,
      };
    } else {
      return {
        value: undefined,
        done: true,
      };
    }
  }
}

const arrayLike: ArrayLike<number> = {
  0: 10,
  1: 20,
  2: 30,
  length: 3,
};

const iterator: Iterator<number> = new ArrayLikeIterator(arrayLike);

console.log(iterator.next()); // { value: 10, done: false }
console.log(iterator.next()); // { value: 20, done: false }
console.log(iterator.next()); // { value: 30, done: false }
console.log(iterator.next()); // { value: undefined, done: true }
```

`ArrayLikeIterator`는 GoF의 반복자 패턴을 따르고 있다. 이 클래스가 지원하는 컬렉션 타입은 `ArrayLike`다. `ArrayLike`는 0부터 시작하는 number 키와 `length` 속성을 가진 타입을 의미한다. 자바스크립트에는 이러한 조건을 만족하는 타입의 값이 많다. 예를 들어 `Array`, `arguments`, `NodeList` 등이 있다. 따라서 `ArrayLikeIterator`를 사용하면 꼭 `Array`가 아니더라도 이 조건에 부합하는 다양한 컬렉션을 순회하는 객체를 만들 수 있다.

```typescript
// [코드 1-3] array를 ArrayLikeIterator로 만들어 순회하기
const array: Array<string> = ['a', 'b', 'c'];
const iterator2: Iterator<string> = new ArrayLikeIterator(array);

console.log(iterator2.next()); // { value: 'a', done: false }
console.log(iterator2.next()); // { value: 'b', done: false }
console.log(iterator2.next()); // { value: 'c', done: false }
console.log(iterator2.next()); // { value: undefined, done: true }
```

`iterator.next()`를 실행하여 `arrayLike`와 `array`의 요소를 순회했다. 당연하게도 `next()`를 실행한 만큼만 요소를 순회하고 `next()`를 실행하지 않으면 순회하지 않게 된다. 이터레이터의 바로 이러한 특성을 활용하여 지연 평가를 구현할 수 있다.

### 1.3 ArrayLike를 역순으로 순회하는 이터레이터 만들기

이번에는 배열의 요소를 역순으로 순회하는 이터레이터를 만들어 본다.

#### Array의 reverse() 메서드

`array.reverse()` 메서드는 호출 시점에 원본 배열의 순서를 뒤집는다. [코드 1-4]에서는 인덱스로 배열의 요소에 접근하기 전에 이미 요소들의 순서가 반전되어 있다.

```typescript
// [코드 1-4] 원본 배열의 순서를 뒤집는 array.reverse 메서드
const array = ['A', 'B'];
array.reverse(); // array의 순서를 반대로 미리 모두 변경해둠
console.log(array[0], array[1]); // B A
```

이렇게 미리 변경해두는 동작이 당연하게 여겨질 수 있지만 대규모 데이터 처리나 성능이 중요한 경우에는 불필요한 메모리 이동과 연산을 유발할 수 있다.

#### 이터레이터의 지연성을 이용한 reverse 함수 만들기

이터레이터를 활용하면 배열을 실제로 뒤집지 않고도 역순으로 순회할 수 있다. 이터레이터는 필요할 때마다 값을 하나씩 꺼내는 지연 평가(*Lazy Evaluation*)를 지원하므로 모든 요소를 미리 뒤집어둘 필요가 없다. 이로써 불필요한 연산과 메모리 사용량을 줄이며 필요한 시점에만 연산이 이루어지도록 개선할 수 있다.

```typescript
// [코드 1-5] Iterator를 반환하는 reverse 함수
function reverse<T>(arrayLike: ArrayLike<T>): Iterator<T> {
  let idx = arrayLike.length;
  return {
    next() {
      if (idx === 0) {
        return { value: undefined, done: true };
      } else {
        return { value: arrayLike[--idx], done: false };
      }
    },
  };
}

const array = ['A', 'B'];
const reversed = reverse(array);

console.log(array); // ['A', 'B'] (원본 배열은 그대로)
console.log(reversed.next().value, reversed.next().value);
// B A
```

[코드 1-5]의 `reverse` 함수는 `ArrayLike` 객체를 인자로 받아 객체를 실제로 뒤집지 않고도 역순으로 순회하는 이터레이터를 반환한다. 물론 원본 배열을 변경하지 않는 것도 의미가 있다. 하지만 여기서 더 중요한 점은 `reverse` 함수를 호출하는 순간에는 아무 일도 일어나지 않고 `reversed.next().value`를 실행할 때마다 배열을 역순으로 하나씩 효율적으로 꺼낸다는 사실이다.

#### 지연 평가의 효율성

[코드 1-4]와 [코드 1-5]만 볼 때는 [코드 1-5]의 방식에 어떤 장점이 있는지 잘 와닿지 않을 수 있다. 하지만 다음 상황을 살펴보면 이 방식의 장점을 느낄 수 있다.

```typescript
// [코드 1-6] 지연 평가가 더 효율적인 상황
const array = ['A', 'B', 'C', 'D', 'E', 'F'];
array.reverse(); // array의 순서를 반대로 미리 모두 변경해둠
console.log(array[0], array[1]); // F E

const array2 = ['A', 'B', 'C', 'D', 'E', 'F'];
const reversed = reverse(array2);
console.log(array2); // ['A', 'B', 'C', 'D', 'E', 'F']
console.log(reversed.next().value, reversed.next().value); // F E
```

`reverse` 함수를 활용한 `array2`에서는 필요한 만큼만 두 번 역방향으로 순회하여 연산과 메모리 사용을 최소화할 수 있다.

```typescript
// [코드 1-7] 만일 원본도 필요하다면?
const array = ['A', 'B', 'C', 'D', 'E', 'F'];
const reversed = [...array].reverse(); // 복사하여 반전해둠
console.log(reversed[0], reversed[1], array[0], array[1]);
// F E A B

const array2 = ['A', 'B', 'C', 'D', 'E', 'F'];
const reversed2 = reverse(array2);
console.log(reversed2.next().value, reversed2.next().value, array2[0], array2[1]);
// F E A B
```

전자는 원본을 지키기 위해 동일한 크기의 배열을 복사한 다음 전체를 반전시켰다. 반면 후자는 원래도 원본을 변경하지 않기 때문에 복사가 필요하지 않다.

### 1.4 지연 평가되는 map 함수

[코드 1-8]의 `map`은 `Iterator<A>`와 A를 B로 변환하는 `transform` 함수를 받아 지연된 `Iterator<B>`를 반환하는 함수다.

#### 일급 함수와 고차 함수

`map` 함수는 `transform` 함수를 인자로 받고 있다. 이렇게 함수를 값처럼 다루어 변수에 담거나 다른 함수의 인자로 전달하거나 함수의 반환값으로 사용할 수 있는 함수를 일급 함수(*First-class Function*)라고 한다. 일급 함수의 이러한 특성을 활용하여 고차 함수를 구현할 수 있다.

고차 함수(*Higher-order Function*)란 하나 이상의 함수를 인자로 받거나 반환하는 함수를 말한다. [코드 1-8]의 `map` 역시 인자로 함수를 받으므로 고차 함수의 전형적인 예시에 해당한다.

이러한 일급 함수와 고차 함수는 함수형 프로그래밍 패러다임의 핵심적인 구성 요소로서 로직을 더욱 쉽게 모듈화하거나 조합할 수 있게 돕는다.

```typescript
// [코드 1-8] Iterator<A>를 받아서 Iterator<B>를 반환하는 map 함수
function map<A, B>(transform: (value: A) => B, iterator: Iterator<A>): Iterator<B> {
  return {
    next(): IteratorResult<B> {
      const { value, done } = iterator.next();
      return done
        ? { value, done }
        : { value: transform(value), done };
    },
  };
}
```

`map` 함수도 `next()`를 실행하기 전까지는 아무런 작업을 하지 않는다. 외부에서 `next()` 메서드를 호출하면 그때 원본 이터레이터의 `next()` 메서드를 호출하여 값을 가져온다. `done`이 `true`이면 변환 없이 그대로 반환하고 `done`이 `false`이면 `transform` 함수를 적용하여 변환된 값을 반환한다. 이처럼 고차 함수는 인자로 받은 함수를 원하는 시점에 실행시킬 수 있는 구조를 갖는다.

```typescript
// [코드 1-9] map(f, reverse(array))
const array = ['A', 'B', 'C', 'D', 'E', 'F'];
const iterator = map((str) => str.toLowerCase(), reverse(array));

console.log(iterator.next().value, iterator.next().value); // f e
```

`reverse(array)`가 배열을 역순으로 순회하는 이터레이터로 만들고 `map` 함수는 각 요소에 `str => str.toLowerCase()`를 적용할 준비가 된 이터레이터를 만든다. [코드 1-9]에서는 `iterator`를 두 번 순회하므로 작업을 두 번만 수행한다. 첫 번째 값을 뽑아 소문자로 변환한 다음 두 번째 값을 뽑아 소문자로 변환하는 것으로 작업을 마치게 된다.

> **핵심 통찰**: 반복자 패턴의 지연성은 지연 평가가 가능한 객체를 생성할 수 있게 해주고, 일급 함수는 고차 함수를 정의할 수 있게 한다. 이 두 가지를 조합하면 `map`, `filter`, `take`, `reduce` 등의 지연 평가를 활용하는 고도화된 리스트 프로세싱 함수를 구현할 수 있다.

### 1.5 멀티패러다임의 교차점: 반복자 패턴과 일급 함수

자바스크립트는 ES6부터 반복자 패턴의 구현체인 Iterator를 중심으로 `Map`, `Set`, `Array`, WebAPI의 `NodeList` 등을 포함한 코어 환경의 모든 컬렉션 타입에 일관된 순회 규약을 도입했다. 이 이터레이션 프로토콜은 `for...of` 문, 전개 연산자(`...`), 구조 분해와 함께 사용되며 `IterableIterator`를 생성할 수 있는 제너레이터 함수도 추가되었다.

이터레이션 프로토콜은 ES6로의 변화에서 큰 축을 이루었으며 이후에도 언어의 발전에 중요한 역할을 하고 있다. `AsyncGenerator`, `Array.fromAsync`, `Iterator Helpers` 등은 이 프로토콜이 현재도 계속 진화하고 있음을 보여준다.

ES6는 또한 `class` 문법을 도입하여 자바스크립트를 객체지향적으로도 크게 발전시켰다. 더 흥미로웠던 점은 정통적인 객체지향 디자인 패턴인 반복자 패턴이 함수형 패러다임의 일급 함수와 만나며 서로의 가치를 더욱 높이고 있다는 사실이다. 여기에 명령형 패러다임으로 작성되는 제너레이터까지 이 조합과 호환된다. 이 세 가지 패러다임이 하나의 언어 안에서 협력하여 객체지향, 함수형, 명령형 패러다임을 함께 고도화하고 언어를 멀티패러다임적으로 발전시키고 있다.

세 가지 프로그래밍 패러다임이 만난 시작점이자 통로가 반복자 패턴과 일급 함수라고 할 수 있다. 특히 「GoF의 디자인 패턴」에 소개된 반복자 패턴은 어느 한 언어에 내장된 기능이나 국한된 개념이 아니다. 일급 객체와 메서드만 지원된다면 어떤 환경에서도 구현 가능한 언어 독립적 방법론이라는 점이 이 이야기를 더욱 매력적으로 만든다. GoF는 다양한 순회 전략을 사용자 정의 Iterator 클래스로 체계화해 보여주었고, 무엇을 순회할지, 어떻게 순회할지, 누가 제어할지를 값(객체)으로 캡슐화해 다루도록 했다. 이렇게 반복 규약을 분리하여 기능을 확장하는 방식은 코드를 데이터처럼 다루며 개발자가 언어 표현력을 스스로 확장해야 한다는 LISP(*LISt Processing - 1950년대 후반 존 매카시가 개발한 고전 함수형 언어로, Scheme, Common Lisp, Clojure 등 파생 언어들이 현대 언어 설계에 큰 영향을 주었다*)의 철학과도 맞닿아 있다.

---

## 2. 명령형 프로그래밍으로 이터레이터를 만드는 제너레이터 함수

앞서 "정통적인 객체지향 디자인 패턴인 반복자 패턴이 함수형 패러다임의 일급 함수와 만나며 서로의 가치를 더욱 높이고 있다", "명령형 패러다임으로 작성되는 제너레이터 역시 이 조합과 호환된다"라고 말했다.

이렇게 표현했던 이유는 제너레이터가 반복자 패턴인 이터레이터를 명령형 코드로 구현하고 생성할 수 있는 도구이기 때문이다. 실제로 어떤 문제는 명령형 스타일로 해결하는 것이 더 효율적이면서 직관적일 때가 있다. 제너레이터는 객체지향, 함수형 패러다임과 명령형 스타일이 서로 협력할 수 있게 하는 중요한 기반을 제공한다.

### 2.1 제너레이터 기본 문법

제너레이터는 명령형 스타일로 이터레이터를 작성할 수 있게 해주는 문법이다. 제너레이터 함수는 `function*` 키워드로 정의되며 호출 시 곧바로 실행되지 않고 이터레이터 객체를 반환한다. 이 객체를 통해 함수의 실행 흐름을 외부에서 제어할 수 있다.

#### yield와 next

제너레이터 함수가 반환한 이터레이터에 대해 `next()` 메서드를 호출하면 제너레이터 함수의 본문이 `yield` 키워드를 만날 때까지 실행된다. `yield` 키워드를 통해 외부로 값을 반환하고, 이후 `next()`를 다시 호출하면 이전 실행 지점부터 이어서 함수가 재개된다. 이렇게 `yield`와 `next()`를 조합하면 함수 내부 상태를 유지하며 순차적으로 값을 반환하는 구조를 쉽게 구현할 수 있다.

```typescript
// [코드 1-10] 간단한 generator 함수
function* generator() {
  yield 1;
  yield 2;
  yield 3;
}

const iter = generator();

console.log(iter.next()); // { value: 1, done: false }
console.log(iter.next()); // { value: 2, done: false }
console.log(iter.next()); // { value: 3, done: false }
console.log(iter.next()); // { value: undefined, done: true }
```

이 예제에서 `generator` 함수는 호출 즉시 이터레이터 객체를 반환한다. `iter.next()`를 호출할 때마다 `yield` 키워드가 있는 지점까지 실행되며 해당 지점에서 값을 반환하고 함수의 실행을 일시 중지한다. `done` 속성이 `true`가 될 때까지 이 과정을 반복한다.

만일 `yield 1;`과 `yield 2;` 사이에 `console.log('hi');`가 있다면 다음과 같이 동작한다.

```typescript
// [코드 1-10a] 제너레이터의 일시 중지
function* generator() {
  yield 1;
  console.log('hi');
  yield 2;
  yield 3;
}

const iter = generator();

console.log(iter.next());
// { value: 1, done: false }
console.log(iter.next()); // hi ← 이때 console.log('hi');가 실행됨
// { value: 2, done: false }
console.log(iter.next());
// { value: 3, done: false }
console.log(iter.next());
// { value: undefined, done: true }
```

이 경우 `iter.next()`를 처음 호출하면 1이 반환되고 함수는 `console.log('hi');` 이전 지점에서 실행이 일시 중지된다. 두 번째로 `iter.next()`를 호출하면 'hi'가 출력되고 2가 반환된다.

#### 제너레이터와 제어문

제너레이터는 명령형으로 구현하기 때문에 조건문을 사용할 수 있다.

```typescript
// [코드 1-11] 조건문을 사용한 제너레이터
function* generator(condition: boolean) {
  yield 1;
  if (condition) {
    yield 2;
  }
  yield 3;
}

const iter1 = generator(false);

console.log(iter1.next()); // { value: 1, done: false }
console.log(iter1.next()); // { value: 3, done: false }
console.log(iter1.next()); // { value: undefined, done: true }
```

[코드 1-11]에서 `iter1.next()`를 처음 호출할 때 1이 반환되고 함수는 일시 중지된다. 두 번째로 `iter1.next()`를 호출하면 조건이 `false`이므로 두 번째 `yield 2;`는 실행되지 않으며 바로 3이 반환된다.

반면 `true`를 전달하면 두 번째 `yield`가 실행된다.

```typescript
// [코드 1-11a] 조건문을 사용한 제너레이터
const iter2 = generator(true);

console.log(iter2.next()); // { value: 1, done: false }
console.log(iter2.next()); // { value: 2, done: false }
console.log(iter2.next()); // { value: 3, done: false }
console.log(iter2.next()); // { value: undefined, done: true }
```

이처럼 제너레이터 안에서 `if` 문을 사용하여 이터레이터가 리스트를 만드는 로직을 제어할 수 있다.

#### yield* 키워드

`yield*` 키워드는 제너레이터 함수 안에서 이터러블(*Iterable - 반복을 지원하는 객체*)을 순회하며 해당 이터러블이 제공하는 요소들을 순차적으로 반환하도록 해준다. 예를 들어 `[2, 3]`과 같은 배열은 자바스크립트에서 이터러블로 간주되어 `for...of` 문이나 전개 연산자(`...`) 뿐 아니라 `yield*`를 통해서도 순회할 수 있다(이터러블에 대한 자세한 내용은 3절에서 다룬다).

```typescript
// [코드 1-12] yield*를 사용한 제너레이터
function* generator() {
  yield 1;
  yield* [2, 3];
  yield 4;
}

const iter = generator();

console.log(iter.next()); // { value: 1, done: false }  ①
console.log(iter.next()); // { value: 2, done: false }  ②
console.log(iter.next()); // { value: 3, done: false }  ③
console.log(iter.next()); // { value: 4, done: false }  ④
console.log(iter.next()); // { value: undefined, done: true }
```

1. `iter.next()`를 호출하면 `yield 1`이 실행되어 1을 반환하고 함수는 일시 중지된다.
2. 두 번째로 `iter.next()`를 호출하면 `yield* [2, 3]`이 실행되어 배열 `[2, 3]`의 각 요소를 차례로 반환하기 시작하여 `yield 2`를 한 것과 동일하게 동작한다.
3. 세 번째로 `iter.next()`를 호출하면 `yield 3`을 한 것과 동일하게 동작하여 3을 반환한다.
4. 네 번째로 `iter.next()`를 호출하면 `yield 4`가 실행되어 4를 반환한다.

#### naturals 제너레이터 함수

다음은 자연수의 무한 시퀀스를 생성하는 제너레이터 함수다. 이 함수는 `yield` 키워드를 사용하여 1부터 시작하는 자연수를 무한히 생성한다.

```typescript
// [코드 1-13] naturals 제너레이터 함수
function* naturals() {
  let n = 1;
  while (true) {
    yield n++;
  }
}

const iter = naturals();

console.log(iter.next()); // { value: 1, done: false }
console.log(iter.next()); // { value: 2, done: false }
console.log(iter.next()); // { value: 3, done: false }
// 계속해서 호출할 수 있다.
```

예제에서 `naturals` 제너레이터 함수는 무한 루프를 사용하여 자연수를 생성하지만 `iter.next()`를 호출할 때만 `n`을 반환하고 다시 일시 중지하기 때문에 프로세스나 브라우저가 멈추지 않는다. 앞서 이터레이터는 지연적인 특성을 가진다고 했는데 제너레이터 역시 이터레이터를 반환한다. 제너레이터 내부의 코드도 `next()`를 실행한 만큼만 평가되므로 제너레이터 역시 지연 평가를 지원한다고 말할 수 있다. 다르게 말하면 제너레이터는 코드를 지연 실행한다.

### 2.2 제너레이터로 작성한 reverse 함수

다음 예제에서는 [코드 1-5]에서 구현한 Iterator를 반환하는 `reverse` 함수를 제너레이터를 사용하여 다시 작성했다.

```typescript
// [코드 1-14] 제너레이터로 작성한 reverse 함수
function* reverse<T>(arrayLike: ArrayLike<T>): IterableIterator<T> {
  let idx = arrayLike.length;
  while (idx--) {
    yield arrayLike[idx];
  }
}

const array = ['A', 'B', 'C', 'D', 'E', 'F'];
const reversed = reverse(array);

console.log(reversed.next().value); // F
console.log(reversed.next().value); // E
console.log(reversed.next().value); // D
```

위 `reverse` 함수는 `arrayLike`의 길이에서 시작하여 0까지 역순으로 순회하면서 각 요소를 `yield` 키워드를 통해 반환한다. 역시 `next()`를 실행하여 요소를 순회할 수 있고 제너레이터 코드를 진행시킬 수 있다.

[코드 1-5]의 `reverse` 함수와 [코드 1-14]의 `reverse` 함수는 구현은 다르지만 동작은 동일하다. [코드 1-5]에서는 `idx`라는 상태를 바라보는 `next()` 메서드를 가진 객체로 구현했다. 반면 [코드 1-14]에서는 제어문을 활용한 명령형 코드로 작성했다. 그리고 두 코드가 해결한 문제는 동일하다.

이 예제를 통해 현대 프로그래밍 언어에서 동일한 문제를 객체지향 방식이나 명령형 등 여러 패러다임 중 하나를 선택하여 해결할 수 있다는 사실을 생각해볼 수 있다. 이번 장과 이후 이어지는 장들에서 계속해서 이터러블을 다루는 이터레이터를 객체지향으로도, 명령형으로도, 함수형으로도 구현해보며 이들이 서로 1:1:1로 호환되는 측면을 살펴본다.

---

## 3. 자바스크립트에서 반복자 패턴 사례: 이터레이션 프로토콜

이터레이션 프로토콜은 자바스크립트의 규약이다. ES6(ECMAScript 2015)에서 도입된 이터레이션 프로토콜은 어떤 객체가 이터러블인지 여부를 나타내는 규칙과 해당 규칙을 따르는 문법들을 제공하는 언어 전반의 규약이다.

### 3.1 이터레이터와 이터러블

만일 어떤 객체가 이터레이터를 반환하는 `[Symbol.iterator]() { return { next() { ... } }; }` 메서드를 가지고 있다면 이터러블이다. 이터러블 객체는 `for...of`, 전개 연산자, 구조 분해 등 다양한 기능과 함께 사용할 수 있다.

이터러블 객체는 자신이 가진 요소들을 이터레이터를 통해 순회할 수 있도록 하며 앞에서 설명한 반복자 패턴의 특성을 모두 갖추고 있다. 대표적으로 `Array`, `Map`, `Set` 등이 있고 WebAPI도 컬렉션 유형의 값들을 이터러블로 만들어 이터레이션 프로토콜을 따르고 있다.

#### 이터레이터

이번에는 자연수를 생성하는 이터레이터를 반환하는 함수를 제너레이터가 아닌 일반 함수로 만들어 본다. 끝나는 값을 설정할 수 있도록 `end` 인자를 추가하고 인자를 받지 않을 경우 기본값으로 `Infinity`를 설정했다.

```typescript
// [코드 1-15] naturals(): Iterator
function naturals(end = Infinity): Iterator<number> {
  let n = 1;
  return {
    next(): IteratorResult<number> {
      return n <= end
        ? { value: n++, done: false }
        : { value: undefined, done: true };
    },
  };
}

const iterator = naturals(3);

console.log(iterator.next().value); // 1
console.log(iterator.next().value); // 2
console.log(iterator.next().value); // 3
console.log(iterator.next().done);  // true
```

[코드 1-15]의 스펙과 패턴은 제너레이터로 구현한 [코드 1-13]의 `naturals`와 동일하다.

#### for...of 문으로 순회하려면

다음과 같이 작성하면 어떻게 될까? IDE에서 보면 `for (const num of iterator2)`의 `iterator2` 부분이 빨간 줄로 표시되고 에러가 표시된다.

```typescript
// [코드 1-16] 타입 에러
const iterator2 = naturals(3);

// TS2488: Type Iterator<number, any, undefined>
// must have a [Symbol.iterator]() method that returns an iterator.
for (const num of iterator2) {
  console.log(num);
}
```

제대로 동작하게 하려면 `naturals` 함수를 다음과 같이 수정하면 된다.

```typescript
// [코드 1-17] Symbol.iterator 메서드 추가
function naturals(end = Infinity): IterableIterator<number> {
  let n = 1;
  return {
    next(): IteratorResult<number> {
      return n <= end
        ? { value: n++, done: false }
        : { value: undefined, done: true };
    },
    [Symbol.iterator]() {
      return this;
    },
  };
}

const iterator = naturals(3);

for (const num of iterator) {
  console.log(num);
}
// 1
// 2
// 3
```

이제 `for...of` 문을 사용하여 `naturals()` 함수가 생성하는 자연수를 순회할 수 있다. 이터러블 객체의 `[Symbol.iterator]()` 메서드가 호출되어 이터레이터를 반환하고 `for...of` 문이 자동으로 `next()` 메서드를 호출하면서 자연수를 순회한다.

`naturals()` 함수의 반환값에 `[Symbol.iterator]() { return this; }` 메서드가 추가되었고 반환 타입이 `IterableIterator<number>`가 되었다. `IterableIterator<number>`는 이터레이터(Iterator)이면서 동시에 이터러블(Iterable)인 값이다.

다음은 `Iterator<T>`, `Iterable<T>`, `IterableIterator<T>`에 대한 인터페이스 정의다 [코드 1-18].

```typescript
// [코드 1-18] Iterator<T>, Iterable<T>, IterableIterator<T>
interface IteratorYieldResult<T> {
  done?: false;
  value: T;
}

interface IteratorReturnResult {
  done: true;
  value: undefined;
}

interface Iterator<T> {
  next(): IteratorYieldResult<T> | IteratorReturnResult;
}

interface Iterable<T> {
  [Symbol.iterator](): Iterator<T>;
}

interface IterableIterator<T> extends Iterator<T> {
  [Symbol.iterator](): IterableIterator<T>;
}
```

정리하면 다음과 같다:

- **Iterator**: `{ value, done }` 객체를 반환하는 `next()` 메서드를 가진 값
- **Iterable**: 이터레이터를 반환하는 `[Symbol.iterator]()` 메서드를 가진 값
- **IterableIterator**: 이터레이터면서 이터러블인 값
- **이터레이션 프로토콜**: 이터러블을 `for...of` 문, 전개 연산자 등과 함께 동작하도록 한 규약

#### 내장 이터러블

지금까지 이터러블이 되는 조건이 무엇인지 알아보았다. 이번에는 자바스크립트의 내장 이터러블들을 살펴보면서 이터레이션 프로토콜에 대해 좀 더 자세히 알아본다.

```typescript
// [코드 1-19] 이터러블인 Array
const array = [1, 2, 3];
const arrayIterator = array[Symbol.iterator]();

console.log(arrayIterator.next()); // { value: 1, done: false }
console.log(arrayIterator.next()); // { value: 2, done: false }
console.log(arrayIterator.next()); // { value: 3, done: false }
console.log(arrayIterator.next()); // { value: undefined, done: true }

// for...of 문을 사용하여 새로운 이터레이터를 만들어 순회한다.
for (const value of array) {
  console.log(value);
}
// 1
// 2
// 3
```

배열 `array`는 기본적으로 이터러블이다. `Symbol.iterator`를 통해 이터레이터를 생성하고 `next()` 메서드로 요소들을 하나씩 순회할 수 있다. 또한 `for...of` 문을 사용하여 모든 요소를 다시 순회할 수 있다.

```typescript
// [코드 1-20] 이터러블인 Set
const set = new Set([1, 2, 3]);
const setIterator = set[Symbol.iterator]();

console.log(setIterator.next()); // { value: 1, done: false }
console.log(setIterator.next()); // { value: 2, done: false }
console.log(setIterator.next()); // { value: 3, done: false }
console.log(setIterator.next()); // { value: undefined, done: true }

for (const value of set) {
  console.log(value);
}
// 1
// 2
// 3
```

`Set` 객체 역시 이터러블이다. `Symbol.iterator`를 통해 이터레이터를 생성하고 모든 요소를 `next()` 메서드로 순회할 수 있다.

```typescript
// [코드 1-21] 이터러블인 Map
const map = new Map([['a', 1], ['b', 2], ['c', 3]]);
const mapIterator = map[Symbol.iterator]();

console.log(mapIterator.next()); // { value: ['a', 1], done: false }
console.log(mapIterator.next()); // { value: ['b', 2], done: false }
console.log(mapIterator.next()); // { value: ['c', 3], done: false }
console.log(mapIterator.next()); // { value: undefined, done: true }

for (const [key, value] of map) {
  console.log(`${key}: ${value}`);
}
// a: 1
// b: 2
// c: 3
```

`Map` 객체도 이터러블이다. `Symbol.iterator`를 통해 이터레이터를 생성하고 모든 요소를 `next()` 메서드로 순회할 수 있다.

```typescript
// [코드 1-22] Map의 entries() 메서드
const mapEntries = map.entries();

console.log(mapEntries.next()); // { value: ['a', 1], done: false }
console.log(mapEntries.next()); // { value: ['b', 2], done: false }
console.log(mapEntries.next()); // { value: ['c', 3], done: false }
console.log(mapEntries.next()); // { value: undefined, done: true }

for (const entry of map.entries()) {
  console.log(entry);
}
// ['a', 1]
// ['b', 2]
// ['c', 3]
```

`map.entries()` 메서드는 Map 객체의 엔트리를 `IterableIterator`로 반환한다. 모든 엔트리를 `next()` 메서드로 순회한 후 `for...of` 문을 사용하여 모든 엔트리를 다시 순회할 수 있다.

```typescript
// [코드 1-23] Map의 values() 메서드
const mapValues = map.values();

console.log(mapValues.next()); // { value: 1, done: false }

// for...of 문을 사용하여 나머지 값을 순회한다.
for (const value of mapValues) {
  console.log(value);
}
// 2
// 3
```

이번에는 조금 다르게 해본다. `map.values()` 메서드는 Map 객체에 담긴 값들을 `IterableIterator`로 반환한다. 먼저 `next()` 메서드를 사용해 첫 번째 값을 확인한 뒤 `for...of` 문으로 나머지 값을 순회할 수 있다. 이터레이터는 내부적으로 현재 위치를 기억하고 순회가 진행됨에 따라 위치를 갱신한다. 따라서 첫 번째 값을 확인한 상태에서 `for...of` 문을 시작하면 그 다음 값부터 순회가 이어진다는 점을 확인할 수 있다.

```typescript
// [코드 1-24] Map의 keys() 메서드
const mapKeys = map.keys();

console.log(mapKeys.next()); // { value: 'a', done: false }

for (const key of mapKeys) {
  console.log(key);
}
// b
// c
```

`map.keys()` 메서드는 Map 객체의 키들을 `IterableIterator`로 반환한다. 첫 번째 키를 `next()` 메서드로 확인한 후 `for...of` 문으로 나머지 키들을 순회할 수 있다. 이터레이터는 현재 위치를 유지하기 때문에 첫 번째 키를 확인한 이후부터 순회가 이어진다.

### 3.2 언어와 이터러블의 상호작용

자바스크립트와 타입스크립트에서 이터러블은 언어의 다양한 기능과 상호작용하며 동작한다. 다음은 이터러블이 전개 연산자, 구조 분해 등과 함께 사용되는 예제다.

#### 전개 연산자와 이터러블

전개 연산자(`...`)는 이터러블 객체의 모든 요소를 개별 요소로 확장하는 데 사용된다. 전개 연산자를 사용하면 배열이나 객체를 쉽게 복사하거나 병합할 수 있다.

```typescript
// [코드 1-25] array 병합
const array = [1, 2, 3];
const array2 = [...array, 4, 5, 6];

console.log(array2); // [1, 2, 3, 4, 5, 6]
```

이터러블 객체는 전개 연산자를 사용하여 배열로 변환할 수 있다.

```typescript
// [코드 1-26] Set 객체 배열로 변환
const set = new Set([1, 2, 3]);
const array = [...set];

console.log(array); // [1, 2, 3]
```

`Set` 객체의 요소들이 전개 연산자를 통해 배열로 변환된다. 이 방식은 `Array.from(set)`과 동일한 결과를 제공한다.

또한 전개 연산자는 함수 호출 시 이터러블 객체의 요소들을 개별 인자로 전달할 때도 유용하다.

```typescript
// [코드 1-27] 전개 연산자로 인자를 펼쳐서 전달
const numbers = [1, 2, 3];

function sum(...nums: number[]): number {
  return nums.reduce((a, b) => a + b, 0);
}

console.log(sum(...numbers)); // 6
```

전개 연산자는 이처럼 인자가 가변적인 함수를 만들고 사용할 때 편리하다.

#### 구조 분해 할당과 이터러블

구조 분해 할당은 이터러블 객체의 요소들을 개별 변수에 할당하는 방법이다. 이를 활용하면 원하는 특정 요소를 쉽게 추출할 수 있다.

```typescript
// [코드 1-28] 구조 분해 할당
const array = [1, 2, 3];
const [first, second] = array;

console.log(first);  // 1
console.log(second); // 2
```

다음은 이터러블의 첫 번째 요소와 나머지 요소들을 추출하는 간결한 코드다.

```typescript
// [코드 1-29] head와 tail 추출
const array = [1, 2, 3, 4];
const [head, ...tail] = array;

console.log(head); // 1
console.log(tail); // [2, 3, 4]
```

`head`에는 배열의 첫 번째 요소가 할당되고 `tail`에는 나머지 요소들이 배열로 할당된다.

```typescript
// [코드 1-30] Map과 for...of 그리고 구조 분해 할당
const map = new Map();
map.set('a', 1);
map.set('b', 2);
map.set('c', 3);

for (const [key, value] of map.entries()) {
  console.log(`${key}: ${value}`);
}
// a: 1
// b: 2
// c: 3
```

#### 사용자 정의 이터러블과 전개 연산자

마지막으로 사용자 정의 이터러블을 반환하는 `naturals()` 함수도 전개 연산자와 함께 사용해 본다.

```typescript
// [코드 1-31] naturals 전개
const array = [0, ...naturals(3)];

console.log(array); // [0, 1, 2, 3]
```

이와 같이 전개 연산자와 구조 분해 할당은 이터러블 프로토콜을 활용하여 자바스크립트와 타입스크립트에서 데이터와 코드를 더욱 효과적으로 다루는 방법을 제공한다. 또한 [코드 1-31]처럼 사용자 정의 객체도 이터러블로 만들 수 있다. 따라서 언어를 사용하는 개발자도 이터레이션 프로토콜을 통해 언어의 다양한 기능과 협업할 수 있다. 이런 규약을 만들 수 있는 바탕에는 1절에서 설명했던 반복자 패턴의 특징이 있다.

### 3.3 제너레이터로 만든 이터레이터도 이터러블

이번에는 앞서 만들었던 [코드 1-8]의 `map` 함수를 제너레이터를 사용하여 다시 구현해 본다.

#### 제너레이터로 만든 map 함수

`map` 함수를 제너레이터로 구현했으며 제너레이터는 항상 `IterableIterator`를 반환한다.

```typescript
// [코드 1-32] map 함수
function* map<A, B>(
  f: (value: A) => B, iterable: Iterable<A>
): IterableIterator<B> {
  for (const value of iterable) {
    yield f(value);
  }
}
```

`map` 함수는 `f` 함수와 이터러블 객체를 인자로 받아 이터러블 객체의 각 요소에 `f` 함수를 적용한 결과를 `yield` 키워드로 반환한다.

```typescript
// [코드 1-33] 제너레이터로 만든 map 함수 사용 예제
const array = [1, 2, 3, 4];
const mapped: IterableIterator<number> = map((x) => x * 2, array); // ①
const iterator = mapped[Symbol.iterator]();

console.log(mapped.next().value);   // ② 2
console.log(iterator.next().value); // ③ 4
console.log([...iterator]);         // ④ [6, 8]
```

- ① `map((x) => x * 2, array)`: `array`의 각 요소에 2배 연산을 적용한 `IterableIterator<number>`를 반환한다.
- ② `mapped.next()`와 `iterator.next()`: 같은 이터레이터를 참조하므로 이미 소비된 요소는 다시 나오지 않는다.
- ④ 전개 연산자(`...iterator`): 남은 요소만을 배열로 만들어 `[6, 8]`을 얻는다.

#### 제너레이터로 만든 이터레이터와 for...of 문

제너레이터로 만든 이터레이터도 이터러블이므로 `for...of` 문을 통해 순회할 수 있다. 이번에는 `naturals()`와 함께 사용해 본다. `naturals()`의 반환값도 이터레이터인 동시에 이터러블이기 때문에 `map` 함수와 조합할 수 있다.

```typescript
// [코드 1-34] map((x) => x * 2, naturals(4))
let acc = 0;
for (const num of map((x) => x * 2, naturals(4))) {
  acc += num;
}

console.log(acc); // 20
```

[코드 1-34]에서는 `map` 함수에 배열이 아닌 지연 평가되는 이터레이터를 전달했다. 실행 과정에서 배열을 만들지 않고도 `acc`에 모든 값을 더했다.

지금까지 여러 예제를 통해 제너레이터, 이터레이터, 이터러블, 전개 연산자, 구조 분해, `for...of` 등을 서로 조합하여 중첩해서 사용할 수 있음을 확인했다. 일반 함수로 이터레이터를 만들 수 있고, 제너레이터로 이터레이터를 생성할 수도 있으며, 일반 함수로 만든 이터레이터를 제너레이터 함수에 전달하거나 반대로 제너레이터에서 생성한 이터레이터를 일반 함수에 전달하여 `for...of`나 `next()`로 순회하며 `yield`를 수행할 수 있다. 타입스크립트에서는 이처럼 이터레이션 프로토콜을 통해 다양한 프로그래밍 패러다임으로 전환하고 조합할 수 있는 유연성을 제공한다.

---

## 4. 이터러블을 다루는 함수형 프로그래밍

이 절에서는 `forEach`, `map`, `filter` 세 가지 함수를 다양한 방식으로 구현해 본다. 이를 통해 반복자 패턴을 활용하고 이터레이션 프로토콜을 준수하는 함수를 구현하는 방법에 익숙해질 수 있다.

이번에는 이터러블과 이터레이터를 직접 다루며 인자로 받은 함수를 각 요소에 적절히 적용하는 패턴에 집중한다. 따라서 타입 정의 없이 자바스크립트 코드로만 구현한다. 이후 2장(함수형 프로그래밍과 타입 시스템 그리고 LISP)에서 여기서 만든 함수들에 타입을 적용하고 발전시키는 과정을 다룰 예정이다.

### 4.1 forEach 함수

`forEach` 함수는 함수와 이터러블을 받아 이터러블을 순회하면서 각 요소에 인자로 받은 함수를 적용하는 고차 함수다.

```javascript
// [코드 1-35] function forEach(f, iterable) { for...of }
function forEach(f, iterable) {
  for (const value of iterable) {
    f(value);
  }
}

const array = [1, 2, 3];
forEach(console.log, array);
// 1
// 2
// 3
```

예제에서 `forEach` 함수는 `for...of` 문을 사용하여 이터러블의 각 요소를 순회한다. 그리고 인자로 받은 함수 `f`를 실행하며 `value`를 전달한다.

```javascript
// [코드 1-36] function forEach(f, iterable) { while }
function forEach(f, iterable) {
  const iterator = iterable[Symbol.iterator]();
  let result = iterator.next();
  while (!result.done) {
    f(result.value);
    result = iterator.next();
  }
}

const set = new Set([4, 5, 6]);
forEach(console.log, set);
// 4
// 5
// 6
```

예제에서 `forEach` 함수는 `while` 루프를 사용하여 이터레이터를 직접 조작한다. 이터레이터의 `next()` 메서드를 사용하여 각 요소를 순회한다. `result.done`이 `true`일 때 루프를 멈춘다. `Set`도 이터러블이기 때문에 `forEach` 함수를 사용할 수 있다.

> **참고**: [코드 1-35]의 `forEach`와 [코드 1-36]의 `forEach` 모두 동일하게 동작하며 실제로 언어 내부에서 하는 일도 거의 동일하다. 참고로 자바스크립트의 `for` 문 내부에는 비정상종료 등 여러 예외 상황을 처리하기 위한 로직이 포함되어 있다. 다만, 대부분 실제로 활용되는 일은 드물며 이 장의 흐름상 중요한 부분은 아니다.

#### `for...of`의 이터레이터 종료 처리

`for...of`와 수동 `while` 루프의 가장 큰 차이는 **이터레이터 종료 처리**(*IteratorClose*)다. ECMAScript 명세에 따르면, `for...of` 루프가 `break`, `return`, 또는 예외(`throw`)로 인해 중간에 빠져나올 때, 엔진은 자동으로 이터레이터의 `return()` 메서드를 호출한다. 이는 이터레이터가 보유한 리소스를 정리할 기회를 주기 위함이다.

```javascript
// 리소스를 보유하는 이터러블 예시
function createResourceIterable() {
  console.log('리소스 획득');
  return {
    [Symbol.iterator]() {
      let i = 0;
      return {
        next() {
          return i < 5
            ? { value: i++, done: false }
            : { value: undefined, done: true };
        },
        return() {
          console.log('리소스 해제'); // 정리 로직
          return { value: undefined, done: true };
        },
      };
    },
  };
}

// for...of: break 시 return()이 자동 호출된다
for (const value of createResourceIterable()) {
  if (value === 2) break;
  console.log(value);
}
// 리소스 획득
// 0
// 1
// 리소스 해제 ← 엔진이 자동으로 iterator.return()을 호출

// while: break 시 return()이 호출되지 않는다
const iterable = createResourceIterable();
const iterator = iterable[Symbol.iterator]();
let result = iterator.next();
while (!result.done) {
  if (result.value === 2) break;
  console.log(result.value);
  result = iterator.next();
}
// 리소스 획득
// 0
// 1
// (리소스 해제가 호출되지 않음 — 리소스 누수 가능)
```

제너레이터 함수로 만든 이터레이터도 동일한 혜택을 받는다. 제너레이터는 `return()` 메서드가 자동으로 존재하며, 호출 시 제너레이터 내부의 `finally` 블록이 실행된다.

```javascript
function* numbersWithCleanup() {
  try {
    yield 1;
    yield 2;
    yield 3;
  } finally {
    console.log('제너레이터 정리 완료');
  }
}

for (const n of numbersWithCleanup()) {
  if (n === 2) break;
  console.log(n);
}
// 1
// 제너레이터 정리 완료 ← finally 블록이 실행됨
```

실무에서 이 차이가 두드러지는 대표적인 예는 파일 읽기, 데이터베이스 커서, 네트워크 스트림 등 외부 리소스를 순회하는 경우다. `for...of`를 사용하면 루프가 어떤 이유로 중단되더라도 리소스가 안전하게 해제된다. 이 장에서 다루는 배열, `Set`, `Map` 등의 인메모리 컬렉션은 별도의 정리가 필요 없기에 두 방식의 차이가 드러나지 않는다.

### 4.2 map 함수

[코드 1-37]의 `map` 함수는 제너레이터를 사용하여 구현했다. `for...of` 문을 사용하여 이터러블의 각 요소인 `value`에 대해 인자로 받은 함수 `f`를 적용한 결과를 `yield` 키워드로 반환한다.

```javascript
// [코드 1-37] function* map(f, iterable) { for...of }
function* map(f, iterable) {
  for (const value of iterable) {
    yield f(value);
  }
}

const array = [1, 2, 3];
const mapped = map((x) => x * 2, array);
console.log([...mapped]); // [2, 4, 6]

const mapped2 = map((x) => x * 3, naturals(3));
forEach(console.log, mapped2);
// 3
// 6
// 9
```

`map` 함수는 이터러블을 인자로 받아 이터레이터를 결과로 반환한다. 반환 결과는 동시에 이터러블이기 때문에 전개 연산자를 이용하거나 `for...of` 문으로 순회할 수 있다. 그렇기에 `map` 함수는 `IterableIterator`를 반환하는 `naturals`나 이터러블을 인자로 받는 `forEach`와도 함께 사용할 수 있다.

```javascript
// [코드 1-38] function* map(f, iterable) { while }
function* map(f, iterable) {
  const iterator = iterable[Symbol.iterator]();
  while (true) {                                // ①
    const { value, done } = iterator.next();    // ②
    if (done) break;                            // ③
    yield f(value);                             // ④
  }
}

const mapped = map(
  ([k, v]) => `${k}: ${v}`,
  new Map([['a', 1], ['b', 2]]),
);
forEach(console.log, mapped);
// a: 1
// b: 2
```

역시 제너레이터를 사용하여 구현했지만 앞선 `forEach`의 구현과는 약간 다른 패턴이다.

- ① 무한 루프를 만든다.
- ② `next()`의 결과를 구조 분해한다.
- ③ `done`이 `true`인 경우 `break;`를 수행한다.
- ④ `value`에 인자로 받은 함수 `f`를 적용한 결과를 `yield` 키워드로 반환한다.

이번에는 역시 이터러블인 `Map`을 전달했다. `Map`의 요소인 엔트리 역시 이터러블이기에 구조 분해를 이용할 수 있으며 `forEach`와 조합하여 동작하게 했다.

```javascript
// [코드 1-39] function map(f, iterable) { return { next, ... } }
function map(f, iterable) {
  const iterator = iterable[Symbol.iterator]();
  return {                                         // ①
    next() {
      const { done, value } = iterator.next();
      return done
        ? { done, value }
        : { done, value: f(value) };               // ②
    },
    [Symbol.iterator]() {                          // ③
      return this;
    },
  };
}

const iterator = (function* () {                   // ④
  yield 1;
  yield 2;
  yield 3;
})();

const mapped = map((x) => x * 10, iterator);      // ⑤

console.log([...mapped]); // [10, 20, 30]
```

- ① 이 `map` 함수는 `IterableIterator` 객체를 직접 만들어 반환한다.
- ② `next` 메서드를 직접 구현하여 각 요소인 `value`에 대해 함수 `f`를 적용한 결과를 반환한다.
- ③ 이터러블 프로토콜을 따르도록 `[Symbol.iterator]` 메서드를 추가한다.
- ④ 익명 제너레이터 함수를 사용하여 1, 2, 3을 순차적으로 생성하는 이터레이터를 만든 후, `map` 함수에 전달한다.
- ⑤ `map` 함수는 각 요소에 대해 `x * 10`을 적용할 준비를 해둔 이터레이터를 만든다.

결과적으로 `mapped`는 전개 연산자로 모든 값을 평가할 경우 `[10, 20, 30]`을 만들 준비가 된 이터레이터다.

### 4.3 filter 함수

`filter` 함수는 주어진 이터러블의 각 요소에 대해 조건을 확인하여 해당 조건을 만족하는 요소들만 반환하는 고차 함수다.

```javascript
// [코드 1-40] function* filter(f, iterable) { for...of }
function* filter(f, iterable) {
  for (const value of iterable) {
    if (f(value)) {
      yield value;
    }
  }
}

const array = [1, 2, 3, 4, 5];
const filtered = filter((x) => x % 2 === 0, array);
console.log([...filtered]); // [2, 4]
```

[코드 1-40]의 `filter` 함수는 제너레이터를 사용하여 구현했다. `for...of` 문을 사용하여 이터러블의 각 요소에 대해 조건 함수 `f`의 식을 만족하는 요소만 `yield` 키워드로 반환한다.

```javascript
// [코드 1-41] function* filter(f, iterable) { while }
function* filter(f, iterable) {
  const iterator = iterable[Symbol.iterator]();
  while (true) {
    const { value, done } = iterator.next();
    if (done) break;       // 여기까지 동일
    if (f(value)) {
      yield value;
    }
  }
}

const array = [1, 2, 3, 4, 5];
const filtered = filter((x) => x % 2 === 0, array);
console.log([...filtered]); // [2, 4]
```

`map`과 `filter` 함수의 구현에서 `for...of` 방식과 `while` 방식을 비교해보면, `for...of`의 역할을 하는 `while` 루프의 바깥 부분과 `done`으로 종료하는 곳까지는 동일하고 내부 구현 부분만 다른 것을 볼 수 있다. 이러한 패턴이 익숙해지도록 연습하면 함수형 프로그래밍의 고차 함수들을 쉽게 구현할 수 있다.

```javascript
// [코드 1-42] function filter(f, iterable) { return { next, ... } }
function filter(f, iterable) {
  const iterator = iterable[Symbol.iterator]();
  return {
    next() {
      const { done, value } = iterator.next();
      if (done) return { done, value };       // ③
      if (f(value)) return { done, value };   // ①
      return this.next();                     // ② 재귀 호출
    },
    [Symbol.iterator]() {
      return this;
    },
  };
}

console.log(...filter((x) => x % 2 === 1, [1, 2, 3, 4, 5])); // 1 3 5
```

- ① `next()` 메서드를 구현하여 각 요소에 대해 주어진 조건 함수 `f`를 만족할 때 `{ done, value }`를 그대로 반환한다. 이때 `done`은 `false`고 `value`에는 값이 있다.
- ② 주어진 조건 함수 `f`를 만족하지 않는다면 재귀적으로 `this.next()`를 다시 실행하여 순회를 계속한다.
- ③ 인자로 받은 `iterable`로 만든 `iterator`의 모든 순회를 마쳐 `done`이 `true`가 되면 `{ done, value }`를 그대로 반환하여 이터레이터를 종료한다.

[코드 1-42]의 `next()` 메서드는 `while` 문이나 `for` 문 같은 반복문 없이 자신의 메서드를 재귀 호출하는 방식으로 객체지향적인 코드로만 순회를 구현하여 매우 간결하다. 또한 이 코드는 꼬리 호출 최적화(*Tail Call Optimization, TCO*)가 가능하다. 꼬리 호출 최적화를 적용할 수 있는 조건은 함수가 반환될 때 마지막으로 호출되는 함수가 재귀 호출이어야 한다. 이 코드에서는 ②의 `this.next()` 호출이 함수의 마지막 동작이며 이 결과가 직접 반환되기 때문에 꼬리 호출 최적화가 적용될 수 있는 구조다. 그러나 아쉽게도 ES6 스펙에 포함된 꼬리 호출 최적화를 V8 엔진에서는 지원하지 않아 스택 오버플로의 위험이 있다.

이러한 문제를 해결하기 위해 다음과 같이 변경할 수 있다.

```javascript
// [코드 1-42a] do...while, while로 변경
function filter(f, iterable) {
  const iterator = iterable[Symbol.iterator]();
  return {
    next() {
      do {
        const { done, value } = iterator.next();
        if (done) return { done, value };
        if (f(value)) return { done, value };
      } while (true); // 재귀 호출과 동일한 위치이며 거의 동일한 표현
    },
    [Symbol.iterator]() {
      return this;
    },
  };
}

// while만 사용하면 좀 더 간결하다.
function filter(f, iterable) {
  const iterator = iterable[Symbol.iterator]();
  return {
    next() {
      while (true) {
        const { done, value } = iterator.next();
        if (done) return { done, value };
        if (f(value)) return { value };
      }
    },
    [Symbol.iterator]() {
      return this;
    },
  };
}
```

위 두 가지 방식 모두 함수 전체를 무한 루프로 감싸므로 재귀 호출과 거의 유사한 구조를 유지하면서도 안전하게 최적화되었다. 현대 언어 중 스칼라와 코틀린은 모두 꼬리 재귀 함수를 반복문 형태로 변환해 스택 오버플로를 방지하는 꼬리 재귀 최적화를 지원한다. 특히 스칼라는 `@tailrec` 애노테이션을 통해 더 다양한 꼬리 재귀 패턴에 최적화를 적용할 수 있어 보다 전면적인 꼬리 호출 최적화에 가까운 접근을 보여준다. 반면 코틀린은 `tailrec` 키워드를 통해 특정 형태의 꼬리 재귀 함수에 한해서만 최적화를 제공한다.

### 4.4 고차 함수 조합하기

지금까지 작성한 여러 함수를 함께 활용하여 약간 더 복잡한 문제를 해결해 본다.

```javascript
// [코드 1-43] 고차 함수 조합
forEach(console.log,         // ④
  map(x => x * 10,           // ③
    filter(x => x % 2 === 1, // ②
      naturals(5))));         // ①
// 10
// 30
// 50
```

함수가 많이 중첩되어 코드를 읽기 약간 불편할 수도 있다. 하지만 이는 LISP 계열 언어들에서 흔히 사용하는 컨벤션이다. 오른쪽 아래에서 왼쪽 위로 올라가며 읽는다고 생각하면 더 쉽게 이해할 수 있다.

- ① `naturals(5)` 결과를
- ② `x % 2 === 1` 조건으로 필터링하고
- ③ `x * 10`으로 변환한 다음
- ④ 모두 콘솔에 출력하라

이 코드에서는 `naturals(5)` 함수로 1부터 5까지 자연수를 순차적으로 생성하는 이터레이터를 만든다. 만든 이터레이터를 `filter` 함수에 전달하여 홀수만 걸러내는 이터레이터를 생성한다. 반복해서 말하지만 이터레이터는 평가가 지연된 객체다.

이제 홀수만 걸러낸 이터레이터가 `map` 함수에 전달된다. `map` 함수는 각 요소에 대해 `x * 10`을 적용한 값을 생성한다. `map` 제너레이터는 입력된 이터레이터의 각 요소에 함수 `f`를 적용하여 변환된 값을 `yield`한다. 이로써 최종적으로 10, 30, 50의 값을 순차적으로 생성하는 이터레이터를 반환한다.

이렇게 생성된 이터레이터는 `forEach` 함수에 전달된다. `forEach` 함수는 주어진 이터러블의 각 요소에 대해 지정된 함수를 실행한다. 여기서는 `console.log` 함수를 지정하여 각 값을 출력한다.

### 4.5 재미난 filter

```javascript
// [코드 1-44] function* filter(f, iterable) { [].filter() }
function* filter(f, iterable) {
  for (const value of iterable) {
    yield* [value].filter(f);
  }
}

const array = [1, 2, 3, 4, 5];
const filtered = filter((x) => x % 2 === 0, array);
console.log([...filtered]); // [2, 4]
```

이 코드의 재미 포인트는 **`if`문 없이 필터링을 구현했다**는 것이다. 일반적인 제너레이터 기반 `filter`는 `if (f(value)) yield value;`로 조건 분기를 하지만, 이 버전은 `if`를 전혀 사용하지 않고 같은 동작을 만들어낸다.

1. `[value].filter(f)` → 조건을 통과하면 `[value]`, 실패하면 `[]`을 반환한다.
2. `yield* [value]` → `value`를 yield한다.
3. `yield* []` → 빈 이터러블이므로 아무것도 yield하지 않고 다음 반복으로 넘어간다.

즉, 배열의 "있거나 없거나"라는 성질과 `yield*`가 빈 이터러블에 대해 아무것도 하지 않는 성질을 조합해서 `if`문의 역할을 대체한 것이다. 조건 분기를 데이터 구조의 존재 여부로 치환한 셈이다.

이 방식도 지연 평가를 지원하며 기존 방식과 시간 복잡도는 본질적으로 동일하다. 이터러블의 각 요소를 한 번씩 순회하므로 요소의 개수가 n일 때 시간 복잡도는 O(n)이다. 물론 단일 요소 배열을 생성하고 `Array.prototype.filter`를 호출하는 추가적인 오버헤드가 존재하지만 이는 매우 작아 실제 실행 시간에 큰 영향을 미치지 않는다.

이 기법을 너무 진지하게 볼 필요는 없지만 이터레이션 프로토콜을 특수하게 조합한 독특한 접근 방식으로, 이터러블을 다루는 프로그래밍 아이디어를 확장해주는 부분이 있다.

---

## 5. 이터러블 프로토콜이 상속이 아닌 인터페이스로 설계된 이유

객체지향 프로그래밍에서 우리가 익숙하게 알고 있는 개념 중 하나는 상속(*Inheritance*)이다. 상속은 코드를 추상화해 기능을 공유하는 좋은 도구이며 실제 개발 현장에서도 자주 사용한다.

그런데 반복자 패턴과 이터레이터를 지원하는 헬퍼 함수들은 상속이 아닌 인터페이스로 설계되어 있다. 이유는 무엇일까? 이 절에서는 현대 언어가 언어 레벨 설계에서 왜 상속을 자제하고 인터페이스(혹은 프로토콜, 트레이트 등)를 적극적으로 활용하는지 살펴본다.

> **참고**: 이 절에서 '상속'과 '인터페이스'가 가리키는 것<br>- **상속(inheritance)**: 타입스크립트 코드 레벨에서 `class A extends B {}`처럼 기존 클래스의 구성과 구현 모두를 물려받는 '클래스 상속'을 의미한다.<br>- **인터페이스(interface)**: 시그니처(메서드/프로퍼티의 타입 정의)만을 정의하는 것을 의미하며 `class X implements Y {}` 형식으로 클래스가 해당 시그니처를 구현할 수 있다. 타입스크립트의 경우 인터페이스는 구현(메서드 코드) 자체가 없고 시그니처만 지정한다.

### 5.1 WebAPI의 NodeList도 이터러블

자바스크립트에서 DOM을 다루다 보면 `NodeList` 객체를 접하게 된다. `NodeList`는 문서 내의 노드들을 컬렉션 형태로 나타내며 이터러블 프로토콜을 따른다. 따라서 `NodeList`를 `for...of` 문이나 전개 연산자와 같이 다양한 이터러블 프로토콜을 사용하는 기능들과 함께 활용할 수 있다.

```html
<!-- [코드 1-45] NodeList와 for...of 문 -->
<ul>
  <li>1</li>
  <li>2</li>
  <li>3</li>
  <li>4</li>
  <li>5</li>
</ul>
<script>
  // 모든 li 요소들을 선택
  const nodeList = document.querySelectorAll('li');

  // for...of 문을 사용하여 NodeList 순회
  for (const node of nodeList) {
    console.log(node.textContent);
    // 1
    // 2
    // 3
    // 4
    // 5
  }
</script>
```

그리고 당연하게도 앞에서 우리가 만든 이터러블을 다루는 함수들과도 함께 사용할 수 있다.

```javascript
// [코드 1-46] 앞에서 만든 함수와 함께 활용
forEach(console.log,
  filter(x => x % 2 === 1,
    map(node => parseInt(node.textContent),
      document.querySelectorAll('li'))));
// 1
// 3
// 5

forEach(element => element.remove(),
  filter(node => parseInt(node.textContent) % 2 === 0,
    document.querySelectorAll('li')));
// removed: <li>2</li>
// removed: <li>4</li>
```

첫 번째 코드는 홀수인 1, 3, 5를 출력하고 두 번째 코드는 짝수 텍스트를 가진 `li` 요소 `<li>2</li>`와 `<li>4</li>`를 화면에서 제거한다.

### 5.2 상속이 아닌 인터페이스로 해결해야 하는 이유

#### 이터러블을 사용하는 이유

왜 이터러블을 사용해야 할까? `Array`의 `map`, `filter`를 쓰면 되지 않을까?

```typescript
// [코드 1-47] NodeList에서 Array.prototype.map을 시도하는 예제
const nodes: NodeList = document.querySelectorAll('li');

console.log(nodes[0], nodes[1], nodes.length);
// <li>1</li> <li>3</li> 3
// nodes는 Array처럼 보인다.

nodes.map(node => node.textContent);
// Uncaught TypeError: nodes.map is not a function
```

[코드 1-47]을 실행하면 에러가 발생한다. `NodeList`는 `Array`가 아닐 뿐더러 다음과 같이 정의되어 있기 때문에 `Array`의 메서드를 사용할 수 없다.

```typescript
// [코드 1-48] NodeList 인터페이스
interface NodeList {
  readonly length: number;
  item(index: number): Node | null;
  forEach(callbackfn: (value: Node, key: number, parent: NodeList) => void, thisArg?: any): void;
  [index: number]: Node;
}
```

반면에 [코드 1-46] 예제에서는 이터레이션 프로토콜에 기반하여 `NodeList`에 `filter`, `map`, `forEach`를 바로 적용할 수 있었다.

#### 순회가 필요한 자료구조들인데 왜 Array를 상속받도록 만들지 않았을까?

자바스크립트나 타입스크립트의 표준 라이브러리에서 `Array`를 상속받은 내장 클래스는 없다. `Map`, `Set`, `NodeList`는 `Array`와 동일한 기능이 일부 필요하다고 해도 `Array`를 상속받지 않았다.

핵심을 말하자면 이들은 모두 서로 다른 자료구조를 나타내며 각각 고유한 특성과 동작을 갖도록 설계되었기 때문이다. 만약 이들을 상속으로 연결하여 의존성을 생기게 하면 불필요한 복잡성이 생기고 최적화된 동작을 보장할 수 없게 된다. 또한 각각의 자료구조를 발전시킬 때 서로에게 미칠 영향을 고려해야 하므로 어려움이 생길 수 있다.

- **Array**: 인덱스를 기반으로 요소에 접근하고 조작하는 데 최적화되어 있다.
- **Map**: 키-값 쌍을 저장하며 각 키는 유일하다. 키를 통해 값을 빠르게 검색할 수 있다.
- **Set**: 유일한 값을 저장하며 중복을 허용하지 않는다. 값의 존재 여부를 빠르게 확인할 수 있다.

이와 같이 구조적 차이가 있는 자료구조들을 `Array`의 특성과 동작 방식에 맞추기 위해 상속하는 것은 부자연스럽고 비효율적이다.

#### (가상의 이야기) 한 사람의 결정이 가져온 혼란

여기 언어와 브라우저의 표준을 정의하고 구현하는 한 사람이 있다고 생각해보자. 어느 날 그는 `NodeList`에 새로운 기능을 추가하면서 `NodeList`의 구조가 `Array`와 비슷하며 `Array`와 같이 기능했으면 좋겠다고 생각한다. 그래서 `NodeList`가 `Array`를 상속받도록 변경하고 배포까지 마쳤다고 상상해보자.

그런데 배포하고 한 달 뒤 `Array`를 고치고 싶어졌다. 하지만 `Array`를 상속받고 있는 객체가 있어 이를 항상 함께 고려해야 해서 관리가 어려워졌음을 느낀다. `NodeList`에 어떤 문제가 발견되어 다시 `Array`를 상속받지 않도록 변경하고 싶은 상황도 생겼다. 그런데 한 달 사이에 `NodeList`가 `Array`로부터 상속받은 기능을 활용한 코드가 웹에 많이 배포됐다. 이제 둘 간의 상속 관계를 제거하려고 해도 하위 호환성을 지키려면 `NodeList`가 가진 `Array`의 모든 기능을 `NodeList`에 포함시켜야 한다.

이러한 이유로 특히 언어 레벨의 설계일수록 상속을 보수적으로 사용함을 알 수 있다.

#### 공통 로직을 공유할 수 있는 방법

앞서 우리는 인터페이스를 기반으로 하는 이터레이션 프로토콜과 이를 활용하는 고차 함수를 통해 다양한 자료구조를 일관되게 다루며 공통 로직을 공유하는 방법을 살펴보았다.

이터레이션 프로토콜을 활용하면 상속 없이도 다양한 자료구조를 일관성 있게 다룰 수 있다. 구체적으로 자료구조가 `Array`, `NodeList`, `Map`, 제너레이터의 반환값 또는 어떤 사용자 정의 이터러블이더라도 이터레이션 프로토콜은 '외부 구조의 다형성'을 해결한다. 동시에 그 안에 담긴 '내부 요소의 다형성'은 주로 고차 함수에 전달되는 함수를 통해 처리하는 구조를 형성한다.

여기서 한 가지 더 흥미로운 부분은 `Array`, `Map`, `Set`은 자바스크립트의 표준 라이브러리지만 `NodeList`는 브라우저 구현 객체라는 점이다. 이처럼 인터페이스에 기반한 규약은 언어나 환경에 따라 달라지는 다양한 구조를 포용할 수 있는 유연한 확장성을 제공한다.

> **핵심 통찰**: 이터레이션 프로토콜은 객체지향 디자인 패턴 중 하나인 반복자 패턴에 기반한다. 반복자 패턴처럼 공통의 인터페이스를 만들어 패턴화함으로써 다양한 자료구조에 사용할 공통 로직을 분리할 수 있다. 이러한 방법은 코드의 유지보수성을 높이고 다양한 자료구조에 동일한 패턴을 적용할 수 있는 더 나은 설계 방식을 제공한다.

### 5.3 인터페이스와 클래스 상속

인터페이스는 클래스나 객체가 따라야 할 규약을 정의하며 이를 통해 다양한 클래스가 동일한 방식으로 상호작용할 수 있도록 한다. 이러한 규약을 통해 공통된 행동을 강제하고 서로 다른 클래스들이 동일한 메서드를 구현하게 함으로써 다형성을 지원하고 코드의 유연성을 높일 수 있다.

한편 상속은 기존 클래스의 속성과 메서드를 물려받아 새로운 클래스를 만드는 과정이다. 이를 통해 코드 재사용성을 높이고 확장성을 확보할 수 있다. 상속을 활용하면 공통 로직을 직접 구현한 뒤 이를 필요에 따라 확장하거나 변경할 수 있다. 그러나 상속을 남용할 경우 코드의 결합도가 높아져 유지보수가 어려워질 수 있으므로 주의가 필요하다.

이 절에서 인터페이스의 장점을 강조하다 보니 자칫 인터페이스가 상속보다 우수한 방법으로 비칠 수 있으나 사실 두 기법은 목적과 용도가 다르다. 인터페이스는 규약을 제시하여 다양한 클래스가 동일한 형식의 동작을 구현하도록 유도한다. 반면 상속은 공통 기능을 직접 구현한 뒤 이를 적절히 확장하는 데 초점을 둔다.

| 구분 | 인터페이스 | 상속 |
|------|-----------|------|
| **목적** | 규약 제시, 다형성 지원 | 코드 재사용, 기능 확장 |
| **주요 사용처** | 언어/표준 라이브러리 설계 | SDK/애플리케이션 레벨 |
| **결합도** | 느슨한 결합 | 강한 결합 |
| **예시** | 이터레이션 프로토콜 | GUI 프레임워크의 커스텀 윈도우 |

인터페이스는 언어나 표준 라이브러리 설계 단계에서 자주 사용되고, 상속은 주로 SDK나 애플리케이션 레벨에서 사용된다. 예를 들어 GUI 프레임워크에서는 기본 윈도우 클래스를 상속받아 새로운 기능을 갖춘 커스텀 윈도우를 만드는 경우가 있다. 이 책의 후반부에서는 상속이 적합한 사례와 관련 코드를 다룰 예정이다. 결국 목적과 상황에 맞게 인터페이스와 상속을 적절히 선택하는 것이 좋은 코드로 나아가는 첫걸음이라 할 수 있다.

---

## 요약

- **멀티패러다임의 시대**: 오늘날 대부분의 프로그래밍 언어는 멀티패러다임 언어로 발전했다. 하나의 언어에서 명령형, 객체지향, 함수형 패러다임을 모두 활용할 수 있다.
- **반복자 패턴과 일급 함수**: 객체지향 디자인 패턴 중 하나인 반복자 패턴은 컬렉션 요소를 순차적으로 접근하는 규약을 제시한다. 함수형 프로그래밍의 핵심 요소인 일급 함수는 함수를 값처럼 취급해 다른 함수의 인자로 전달하거나 반환값으로 사용할 수 있다. 이 두 개념을 결합하면 지연 평가와 리스트 프로세싱을 효율적으로 구현할 수 있다.
- **지연 평가와 고차 함수**: 지연 평가는 필요한 시점까지 계산을 미루어 메모리 사용량과 연산 비용을 줄여 성능을 향상하는 기법이다. `map`, `filter`, `reduce`와 같은 고차 함수들은 지연 평가와 고차 함수 기법을 활용해 더 나은 성능과 가독성을 제공한다.
- **제너레이터 함수**: 제너레이터 함수는 이터레이터를 생성하는 문법적 장치로서 명령형 스타일로도 이터레이션 로직을 구현할 수 있게 한다. `function*` 키워드와 `yield` 키워드를 사용해 값을 하나씩 반환함으로써 지연 평가가 필요한 로직을 간결하고 명확하게 표현할 수 있다.
- **이터레이션 프로토콜**: 이터러블 객체는 이터레이터를 통해 순회 가능한 구조를 갖추고 있다. 이를 `for...of` 문, 전개 연산자, 구조 분해 할당 등과 함께 활용하면 더욱 유연한 코드 작성이 가능하다. 타입스크립트는 이터레이션 프로토콜에 대해 정교한 타입 시스템을 제공하여 각 요소의 타입을 명확히 정의하고 코드 안전성을 강화한다.
- **사용자 정의 이터러블**: 개발자는 직접 만든 객체에 이터레이션 프로토콜을 구현하여 사용자 정의 이터러블을 만들 수 있다. 이를 통해 언어의 기본 기능과 긴밀히 협업하고 다양한 문제 해결 방식을 시도하거나 언어 자체를 확장하는 것도 가능하다.
- **상속 대신 인터페이스**: 상속은 객체지향 프로그래밍에서 중요한 개념이지만, 다양한 자료구조를 일관성 있게 처리하려면 인터페이스와 이터레이션 프로토콜을 활용하는 편이 더 효율적일 수 있다. `NodeList`, `Map`, `Set` 등은 서로 다른 특성과 동작 방식을 지니지만, 상속 대신 인터페이스를 통해 공통 로직을 공유하고 반복자 패턴에 기반한 이터레이션 프로토콜을 활용하면 다양한 자료구조를 유연하게 다룰 수 있다.
- **멀티패러다임의 교차점**: 반복자 패턴과 일급 함수는 멀티패러다임 언어에서 함수형 프로그래밍 구현의 중요한 시발점이자 교차점이다. 이를 통해 고도화된 리스트 프로세싱을 구현하고 더 나은 성능과 가독성을 얻을 수 있으며, 멀티패러다임 언어의 강력한 기능을 최대한 활용할 수 있다.

