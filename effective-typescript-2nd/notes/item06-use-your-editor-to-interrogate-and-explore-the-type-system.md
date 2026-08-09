# Item 6: 편집기를 사용하여 타입 시스템 탐색하기 (Use Your Editor to Interrogate and Explore the Type System)

## 핵심 질문

타입스크립트가 내 코드의 타입을 어떻게 이해하고 있는지 어디서 확인하는가? 편집기를 타입 시스템의 실험실로 쓰는 법은?

타입스크립트를 설치하면 실행 파일 두 개가 생긴다.

- **`tsc`**: 타입스크립트 컴파일러 - 직접 실행할 일이 더 많다
- **`tsserver`**: 타입스크립트 단독 서버 - 언어 서비스(*language services - 자동완성·검사·내비게이션·리팩터링 등 편집기 기능의 백엔드*)를 제공한다

컴파일러 못지않게 서버가 중요하다. 자동완성 같은 서비스는 타입스크립트를 쓰는 즐거움의 큰 부분이지만, 편의를 넘어 **편집기는 타입 시스템 지식을 쌓고 검증하는 최고의 장소**다. 타입스크립트가 언제 타입을 추론할 수 있는지에 대한 직관을 길러 주는데, 이것이 간결하고 관용적인 코드의 열쇠다(Item 18).

## 1. 편집기로 추론 타입 확인하기

편집기마다 다르지만 보통 심벌에 마우스를 올리면 타입스크립트가 그 심벌의 타입을 무엇으로 보는지 나온다.

- **변수**: `let num = 10`에 올리면 `number` - 직접 쓰지 않았지만 값에서 알아냈다
- **함수**: 추론된 **반환 타입**을 보여 준다. 기대와 다르면 타입 선언을 추가하고 어긋난 지점을 추적해야 한다(Item 9)
- **조건문 분기**: 분기 바깥에서 `string | null`이던 변수가 분기 안에서 `string`으로 바뀌는 것을 관찰할 수 있다 - 넓히기(Item 20)와 좁히기(Item 22)의 직관을 기르는 데 필수적이고, 타입 시스템에 대한 확신을 쌓는 훌륭한 방법이다
- **객체의 개별 속성**: 큰 객체에서 속성별 추론 결과를 확인할 수 있다. `[10, 20]`이 `number[]`로 추론됐는데 튜플 타입(`[number, number]`)을 의도했다면 타입 구문이 필요하다는 것을 알게 된다
- **메서드 체인 중간**: 체인 중간의 추론된 제네릭 타입은 **메서드 이름**에 마우스를 올려 확인한다. `split`이 `Array<string>`을 만들었다는 것을 타입스크립트가 이해하고 있음을 볼 수 있고, 긴 함수 호출 체인을 작성·디버깅할 때 이 정보가 결정적일 수 있다

## 2. 에러로 타입 시스템의 미묘함 배우기

편집기에 뜨는 타입 에러도 타입 시스템의 뉘앙스를 배우는 훌륭한 통로다. ID로 `HTMLElement`를 얻거나 기본 요소를 반환하려는 함수에서 타입스크립트는 두 가지 에러를 지적한다.

```typescript
function getElement(elOrId: string | HTMLElement | null): HTMLElement {
  if (typeof elOrId === 'object') {
    return elOrId;
    //     ~~~~~~ Type 'HTMLElement | null' is not assignable to type 'HTMLElement'
  } else if (elOrId === null) {
    return document.body;
  }
  elOrId
  // ^? (parameter) elOrId: string
  return document.getElementById(elOrId);
  //     ~~~ Type 'HTMLElement | null' is not assignable to type 'HTMLElement'
}
```

첫 분기의 의도는 객체(`HTMLElement`)만 걸러내는 것이었지만, 자바스크립트에서는 얄궂게도 `typeof null`이 `"object"`라서 그 분기 안에서도 `elOrId`가 여전히 `null`일 수 있다. `null` 체크를 앞으로 옮기면 해결된다. 두 번째 에러는 `document.getElementById`가 `null`을 반환할 수 있기 때문으로, 예외를 던지는 식으로 처리해 준다.

```typescript
function getElement(elOrId: string | HTMLElement | null): HTMLElement {
  if (elOrId === null) {
    return document.body;
  } else if (typeof elOrId === 'object') {
    return elOrId;
    //     ^? (parameter) elOrId: HTMLElement
  }
  const el = document.getElementById(elOrId);
  //                                 ^? (parameter) elOrId: string
  if (!el) {
    throw new Error(`No such element ${elOrId}`);
  }
  return el;
  // ^? const el: HTMLElement
}
```

## 3. 리팩터링 도구

언어 서비스는 리팩터링 도구도 제공한다. 가장 단순하면서 유용한 것이 **심벌 이름 변경(Rename Symbol)** 이다. 단순 찾기-바꾸기보다 훨씬 정교한데, 같은 이름이 곳곳에서 다른 변수를 가리킬 수 있기 때문이다.

```typescript
let i = 0;
for (let i = 0; i < 10; i++) {
  console.log(i);
  {
    let i = 12;
    console.log(i);
  }
}
console.log(i);
```

여기엔 `i`라는 이름의 **서로 다른 변수 세 개**가 있다. VS Code에서 `for` 루프의 `i`를 클릭하고 F2를 누르면 새 이름을 입력할 수 있고, 적용하면 그 `i`를 참조하는 곳만 바뀐다(루프의 `i` → `x`, 바깥과 블록 안의 `i`는 그대로). 다른 모듈에서 import한 심벌의 이름을 바꾸면 import 문도 함께 갱신된다.

그 밖에도 파일 이름 변경·이동(모든 import 갱신), 심벌을 새 파일로 이동 등 유용한 리팩터링이 많다. 대규모 타입스크립트 프로젝트에서 생산성을 크게 높여 주므로 익숙해져야 한다.

## 4. 타입 선언 파일로 점프하기

언어 서비스는 내 코드는 물론 외부 라이브러리와 타입 선언 사이의 내비게이션도 도와준다. 전역 `fetch` 함수가 궁금하면 **"Go to Definition(정의로 이동)"** 으로 타입스크립트가 DOM용으로 포함하는 타입 선언 `lib.dom.d.ts`로 들어갈 수 있다.

```typescript
declare function fetch(
  input: RequestInfo | URL, init?: RequestInit
): Promise<Response>;
```

`fetch`가 `Promise`를 반환하고 인수 두 개를 받는다는 것이 보인다. `RequestInfo`를 타고 들어가면:

```typescript
type RequestInfo = Request | string;
```

`Request`로 가 보면 타입과 값이 **따로 모델링**되어 있다(Item 8).

```typescript
interface Request extends Body {
  // ...
}
declare var Request: {
  prototype: Request;
  new(input: RequestInfo | URL, init?: RequestInit | undefined): Request;
};
```

`RequestInit`을 열면 `Request` 생성에 쓸 수 있는 모든 옵션(`body`·`cache`·`credentials`·`headers` 등)이 나온다. 타입 선언은 처음에는 읽기 어렵지만, 타입스크립트로 무엇을 할 수 있는지, 쓰고 있는 라이브러리가 어떻게 모델링되어 있는지, 에러를 어떻게 디버깅할지 보는 훌륭한 창이다. 타입 선언은 Chapter 8에서 자세히 다룬다.

> **핵심 통찰**: 타입스크립트 학습의 가장 빠른 피드백 루프는 편집기다. 코드를 조금 바꾸고 추론이 어떻게 변하는지 관찰하는 습관이 타입 시스템에 대한 직관을 만든다.

## 기억해야 할 것들

- 언어 서비스를 지원하는 편집기를 써서 타입스크립트 언어 서비스를 활용하라.
- 편집기로 타입 시스템이 어떻게 동작하고 타입스크립트가 어떻게 타입을 추론하는지에 대한 직관을 길러라.
- 심벌·파일 이름 변경 같은 타입스크립트 리팩터링 도구에 익숙해져라.
- 타입 선언 파일로 점프해서 동작이 어떻게 모델링되어 있는지 보는 법을 알아 두라.
