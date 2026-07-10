# fp-ts vs fxts

안녕하세요 현업에서 fp-ts와 fxts두개중 하나의 도입을 고민하고 있습니다. fxts에 대한 장점으로는 woolimpark님 께서 정리해주신 내용으로 참고가 많이 되었는데요. fp-ts와 비교하였을때 fxts의 장점이 무엇이 있을지 알려주실 수 있을까요?

**woolim park**
[https://www.inflearn.com/questions/13513](https://www.inflearn.com/questions/13513)
예전에 유인동님이 답변해주신 lodash 나 ramda 에 비해 얻는 장점에 대한 글도 여기에 공유합니다. (fxjs 지만 fxts 에도 해당하는 이야기라고 생각해서 같이 정리할겸 올려요)

1. 대부분의 라이브러리들이 Promise를 잘 지원하지 못합니다.
2. Promise를 잘 지원하지 못하면 async/await 와 함께 사용하지 못합니다.
3. async/await를 사용하지 못하면 비동기 에러 핸들링이 어려워집니다.
4. fxjs는 ES6 표준 이터러블 프로토콜을 따르고 있어 이터러블/이터레이터/제너레이터와 잘 조합됩니다.
5. fxjs는 Promise를 잘 지원합니다.
6. fxjs는 지연 평가와 Promise가 함께 잘 동작합니다.
7. fxjs는 async/await 와 함께 사용할 수 있으며, 비동기 에러핸들링이 쉽습니다.
8. fxjs는 병렬적 동시 평가를 다루는 많은 함수들이 있습니다. (C.takeAll, C.takeRace, C.race, C.map 등..)
9. fxjs는 함수 하나 하나가 코드가 간결하고 이해하기 쉽게 잘 작성되어있습니다.
10. fxjs는 tree shaking 을 잘 지원합니다.
11. fxjs는 이전 브라우저, 최신 브라우저, CommonJS, ESM 등의 환경을 모두 잘 지원하고 있습니다.
12. fxjs는 슬랙 채널을 운영하고 있습니다.
13. 다른 라이브러리에서 아래와 같은 코드가 동작하는지 테스트해보세요. 대부분의 다른 라이브러리들은 1번 상황에서 이상한 값이 나오고 2번 상황에서는 에러핸들링이 안되고 에러가 터질거에요.

```typescript
// 1
async function f1() {
  const res = await go(
    [1, 2, 3, 4, 5],
    L.map(a => new Promise(resolve => resolve(a * a))),
    L.filter(a => new Promise(resolve => resolve(a % 2))),
    L.take(3),
    reduce((a, b) => a + b));

  return res * 10
}

f1().then(console.log); // 350

// 2
async function f2() {
  try {
    return await go(
      [{ val: 1 }, { val: 2 }, null, { val: 4 }, { val: 5 }],
      L.map(({val}) => new Promise(resolve => resolve(val + 10))),
      L.filter(a => a % 2),
      L.take(3),
      reduce((a, b) => a + b));
  } catch (e) {
    return 0;
  }
}

f2().then(console.log); // 0
```

### 답변
저도 잘 아는 부분은 아니지만.. 두 라이브러리의 컨셉 자체가 차이가 나는 것 같아요.
- fp-ts

```plain text
The goal of fp-ts is to empower developers to write pure FP apps and libraries built atop higher order abstractions. It includes the most popular data types, type classes, and abstractions from languages like Haskell, PureScript, and Scala.
```

fp-ts는 타입 추상화에 더 초점이 맞추어져 있는 것 같습니다.

**이도형**
예전에 동일한 질문을 받은 적이 있어서 답변 공유드립니다.
(스크린샷 첨부: fxts/fp-ts 비교 이미지 — 원본 Notion 참조)
