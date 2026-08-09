# Item 18: 추론 가능한 타입으로 코드를 어지럽히지 않기 (Avoid Cluttering Your Code with Inferable Types)

## 핵심 질문

타입 구문은 어디에 쓰고 어디에서 생략해야 하는가? 추론 가능한데도 명시하는 것이 오히려 좋은 경우는 언제인가?

자바스크립트 코드베이스를 전환할 때 신참 타입스크립트 개발자가 처음 하는 일이 타입 구문으로 도배하는 것이다 - 어쨌든 타입스크립트는 타입에 관한 거니까! 하지만 많은 구문이 불필요하다. 모든 변수에 타입을 선언하는 것은 비생산적이며 나쁜 스타일로 여겨진다.

```typescript
let x: number = 12;   // 이렇게 쓰지 말고
let x = 12;           // 이렇게 쓰라
```

편집기에서 `x`에 마우스를 올리면 `number`로 추론된 것이 보인다. 명시적 타입 구문은 중복이고 잡음만 더한다. 타입이 확실치 않으면 편집기에서 확인하면 된다.

## 1. 추론에 맡겨도 되는 곳

복잡한 객체도 문제없이 추론된다.

```typescript
const person = {
  name: 'Sojourner Truth',
  born: {
    where: 'Swartekill, NY',
    when: 'c.1797',
  },
  died: {
    where: 'Battle Creek, MI',
    when: 'Nov. 26, 1883',
  }
};  // 전체 타입 구문을 붙인 버전과 타입이 정확히 같다
```

배열과 함수 반환도 마찬가지다.

```typescript
function square(nums: number[]) {
  return nums.map(x => x * x);
}
const squares = square([1, 2, 3, 4]);
//    ^? const squares: number[]
```

타입스크립트는 기대보다 **더 정밀하게** 추론하기도 하는데, 대체로 좋은 일이다.

```typescript
const axis1: string = 'x';
//    ^? const axis1: string
const axis2 = 'y';
//    ^? const axis2: "y"
```

`"y"`가 `axis2`에 더 정확한 타입이다. `axis1`의 명시적 `string`은 잡음이면서 타입 안전성도 떨어뜨린다.

추론에 맡기면 **리팩터링도 쉬워진다**. `Product`의 `id`가 `number`에서 `string`으로 바뀌었을 때, 함수 본문의 지역 변수마다 명시적 구문이 붙어 있으면 전부 에러가 난다.

```typescript
function logProduct(product: Product) {
  const id: number = product.id;
  //    ~~ Type 'string' is not assignable to type 'number'
  const name: string = product.name;
  const price: number = product.price;
  console.log(id, name, price);
}
```

구문을 안 붙였다면 수정 없이 통과했을 것이다(런타임에도 정상 동작). 더 나은 구현은 구조 분해 할당으로 모든 지역 변수의 타입을 추론에 맡기는 것이다.

```typescript
function logProduct(product: Product) {
  const {id, name, price} = product;
  console.log(id, name, price);
}
```

구조 분해 안에 타입 구문을 직접 넣을 수 없다는 것도 기억하자 - Item 8에서 봤듯 값 공간의 이름 바꾸기 지시어로 해석된다. 구조 분해는 코드를 간결하게 하고 일관된 네이밍을 장려하며 추론 타입과 훨씬 잘 어울린다.

## 2. 구문이 필요한 곳 - 함수 매개변수 (예외 있음)

타입스크립트가 스스로 타입을 결정할 문맥이 부족한 곳에서는 명시적 구문이 여전히 필요하다. 대표가 **함수 매개변수**다. 사용처를 보고 매개변수 타입을 추론하는 언어도 있지만 타입스크립트는 그러지 않는다 - 변수의 타입은 일반적으로 **처음 도입될 때** 결정된다(중요한 예외는 Item 25).

> **핵심 통찰**: 이상적인 타입스크립트 코드는 함수/메서드 **시그니처에는** 타입 구문을 쓰고, 본문의 **지역 변수에는** 쓰지 않는다. 잡음을 최소화하고 독자가 구현 로직에 집중하게 한다.

매개변수 구문도 생략 가능한 경우가 있다.

- **기본값이 있을 때**: `function parseNumber(str: string, base=10)` - `base`는 기본값 10에서 `number`로 추론된다.
- **타입 선언이 있는 라이브러리의 콜백일 때**: 문맥으로 추론된다(Item 24).

```typescript
// 이렇게 하지 말고:
app.get('/health', (request: express.Request, response: express.Response) => {
  response.send('OK');
});

// 이렇게:
app.get('/health', (request, response) => {
  //                ^? (parameter) request: Request<...>
  response.send('OK');
  // ^? (parameter) response: Response<...>
});
```

## 3. 추론 가능해도 명시하고 싶은 곳 ① - 객체 리터럴

객체 리터럴 정의에 타입을 명시하면 **잉여 속성 체크**(Item 11)가 활성화되어 특히 옵셔널 필드가 있는 타입의 오류를 잘 잡는다. 그리고 **에러가 올바른 위치에 보고될 확률**이 올라간다. 구문이 없으면 객체 정의의 실수가 정의 지점이 아니라 **사용 지점**에서 에러가 된다.

```typescript
const furby = {
  name: 'Furby',
  id: 630509430963,
  price: 35,
};
logProduct(furby);
//         ~~~~~ Argument ... is not assignable to parameter of type 'Product'
//               Types of property 'id' are incompatible
//               Type 'number' is not assignable to type 'string'
```

큰 코드베이스에서는 이 에러가 객체 정의와 아무 연관이 안 보이는 다른 파일에서 나타날 수 있다. 구문을 붙이면 실수한 바로 그 자리에서 더 간결한 에러가 난다.

```typescript
const furby: Product = {
  name: 'Furby',
  id: 630509430963,
  //  ~~ Type 'number' is not assignable to type 'string'
  price: 35,
};
```

## 4. 추론 가능해도 명시하고 싶은 곳 ② - 함수 반환 타입

반환 타입도 추론 가능하지만, **구현의 오류가 함수 사용처로 새어 나가지 않게** 명시하고 싶을 수 있다. 공개 API의 export 함수라면 특히 그렇다.

주가를 조회하는 함수에 캐시를 추가했다고 하자.

```typescript
const cache: {[ticker: string]: number} = {};
function getQuote(ticker: string) {
  if (ticker in cache) {
    return cache[ticker];
  }
  return fetch(`https://quotes.example.com/?q=${ticker}`)
    .then(response => response.json())
    .then(quote => {
      cache[ticker] = quote;
      return quote as number;
    });
}

getQuote;
// ^? function getQuote(ticker: string): number | Promise<number>
```

실수가 있다 - 캐시 히트 시 `Promise.resolve(cache[ticker])`를 반환해서 항상 `Promise`가 되게 해야 한다. 이 실수는 에러를 내겠지만 `getQuote` 자신이 아니라 **호출하는 코드**에서 난다.

```typescript
getQuote('MSFT').then(considerBuying);
//               ~~~~ Property 'then' does not exist on type
//                    'number | Promise<number>'
```

의도한 반환 타입(`Promise<number>`)을 명시했다면 에러가 올바른 자리에서 보고된다.

```typescript
function getQuote(ticker: string): Promise<number> {
  if (ticker in cache) {
    return cache[ticker];
    //     ~~~ Type 'number' is not assignable to type 'Promise<number>'
  }
  // ...
}
```

(async 함수가 이 특정 실수를 효과적으로 방지하는 방법은 Item 27.)

반환 타입을 명시할 이유는 그 밖에도:

1. **여러 return 문이 있는 함수**: 모든 return이 같은 타입인지 검사받으려면 의도를 알려야 한다.
2. **함수에 대해 더 명확하게 생각하게 된다**: 구현 전에 입출력 타입을 알아야 한다. 구현은 흔들려도 함수의 계약(타입 시그니처)은 대체로 흔들리면 안 된다 - 테스트를 먼저 쓰는 TDD와 같은 정신이다. 전체 시그니처를 먼저 쓰면 구현이 만들기 편한 함수가 아니라 원하는 함수를 얻게 된다.
3. **이름 붙은 타입으로 보여 주고 싶을 때**: `add(a: Vector2D, b: Vector2D)`의 추론 반환 타입은 `{ x: number; y: number; }`다. `Vector2D`와 호환되지만, 입력은 `Vector2D`인데 출력은 아닌 것이 사용자에게 의아해 보일 수 있다. 명시하면 표현이 곧아지고, 타입에 단 문서(Item 68)도 반환값에 연결된다.
4. **컴파일러 성능**: 명시하면 타입스크립트가 알아낼 일이 줄어든다. 큰 코드베이스에서는 영향이 있다(Item 78).

정리하면 - 코드를 줄이고 리팩터링을 쉽게 하려면 기본 답은 "명시하지 않는다"지만, "명시한다"로 기울 계기는 많지 않아도 된다: 다중 return, 공개 API, 이름 붙은 반환 타입.

> **실무 팁**: typescript-eslint의 `no-inferrable-types` 룰(철자 주의 - rr)이 모든 타입 구문이 정말 필요한 것인지 확인해 준다.

## 기억해야 할 것들

- 타입스크립트가 같은 타입을 추론할 수 있다면 타입 구문을 쓰지 마라.
- 이상적인 타입스크립트 코드는 함수/메서드 시그니처에는 타입 구문이 있고 본문의 지역 변수에는 없다.
- 객체 리터럴에는 명시적 구문을 고려하라 - 잉여 속성 체크가 활성화되고 에러가 발생 지점 가까이에서 보고된다.
- 함수 반환 타입은 다중 return이거나 공개 API이거나 이름 붙은 반환 타입을 원하는 경우가 아니면 명시하지 마라.
