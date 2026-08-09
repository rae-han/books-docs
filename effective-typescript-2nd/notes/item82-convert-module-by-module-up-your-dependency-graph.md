# Item 82: 의존성 그래프를 따라 모듈 단위로 위로 변환하기 (Convert Module by Module Up Your Dependency Graph)

## 핵심 질문

수백 개 모듈을 어떤 순서로 변환해야 같은 모듈을 두 번 손대지 않는가? 변환 중 만나는 흔한 에러들은?

모던 자바스크립트를 채택했고(Item 79), 타입스크립트를 빌드 체인에 통합해 테스트가 전부 통과한다(Item 81). 이제 재미있는 부분 - 자바스크립트를 타입스크립트로 변환하기다. 그런데 어디서 시작할까?

모듈에 타입을 추가하면 그것을 import하는 다른 모든 모듈에서 새 타입 에러가 드러나기 쉽다. 이상적으로는 각 모듈을 **한 번만** 변환하고 끝내고 싶다. 즉 **의존성 그래프를 따라 위로** 변환해야 한다 - 잎(아무것도 import하지 않는 모듈)에서 시작해 뿌리로. (나무의 뿌리가 위에 있다고 생각하는 것은 프로그래머뿐이다!)

## 1. 가장 먼저 - 서드파티와 외부 API

**맨 처음 마이그레이션할 모듈은 서드파티 의존성**이다 - 정의상 내가 그것들을 import하지 그 반대가 아니니까. 보통 @types 모듈 설치를 뜻한다.

```
npm install --save-dev @types/lodash
```

이 타입 선언들이 타입이 코드를 타고 흐르게 하고 라이브러리 사용의 문제를 드러낸다. 패키지 버전을 맞출 것(Item 66). 라이브러리가 타입을 번들한다면 이 단계는 건너뛴다.

**외부 API를 호출한다면 그 타입 선언도 이른 시기에** 추가하는 것이 좋다. 호출이 코드 어디에나 있을 수 있지만, API에 내가 의존하지 API가 내게 의존하지 않으므로 여전히 그래프를 따라 올라가는 정신에 맞다. API 호출에서 많은 타입이 흘러나오는데 문맥에서 추론하기는 대체로 어렵다.

```typescript
interface TabularData {
  columns: string[];
  rows: number[][];
}
async function fetchTable(): Promise<TabularData> {
  const response = await fetch('/data');
  if (!response.ok) throw new Error('Failed to fetch!');
  return response.json();
}
```

이제 모든 `fetchTable` 호출에서 타입이 흐른다. Item 42에서 봤듯 명세나 DB 스키마 같은 기존 진실 공급원이 있다면 처음부터 직접 쓰지 않는 것이 낫다.

## 2. 내 모듈들 - 그래프 시각화와 위상 정렬

내 모듈을 마이그레이션할 때는 **의존성 그래프의 시각화**가 도움이 된다(훌륭한 madge 도구 등). 그래프 맨 아래에는 흔히 유틸리티 모듈이 있다 - dygraphs(중간 규모 JS 프로젝트)에서는 utils.js와 tickers.js의 순환 의존이 바닥이었고, 많은 모듈이 그 둘을 import하지만 그 둘은 서로만 import했다. 대부분의 프로젝트에 이런 패턴이 있다.

순서의 추측을 없애고 싶으면 의존성 그래프에 **위상 정렬**을 돌리면 된다. 스프레드시트에 파일별 코드 줄 수와 함께 넣어 두면 얼마나 왔고 얼마나 남았는지 감이 잘 잡힌다.

> **핵심 통찰**: 마이그레이션 중에는 **리팩터링이 아니라 타입 추가에 집중하라.** 오래된 프로젝트라면 이상한 것들이 눈에 띄고 고치고 싶어질 것이다. 그 충동을 참아라! 당면 목표는 타입스크립트로의 변환이지 설계 개선이 아니다. 무관한 리팩터링은 속도를 늦추고 코드 리뷰를 어렵게 하고 버그를 심을 위험을 키운다. 코드 냄새는 기록해서 미래의 리팩터링 목록에 추가하라 - 버그는 지금 접수하고, 수정은 나중에. any나 @ts-expect-error를 쓰게 되더라도 괜찮다.

## 3. 변환 중 만나는 흔한 에러

**① 선언되지 않은 클래스 멤버** - 자바스크립트 클래스는 멤버 선언이 필요 없지만 타입스크립트 클래스는 필요하다. .js를 .ts로 바꾸면 참조하는 모든 속성에 에러가 난다.

```typescript
class Greeting {
  constructor(name) {
    this.greeting = 'Hello';
    //   ~~~~~~~~ Property 'greeting' does not exist on type 'Greeting'
    this.name = name;
    //   ~~~~ Property 'name' does not exist on type 'Greeting'
  }
}
```

유용한 빠른 수정("Add all missing members")이 있으니 활용하라 - 사용에 근거해 누락 멤버의 선언을 추가해 준다.

```typescript
class Greeting {
  greeting: string;
  name: any;
  // ...
}
```

`greeting`은 맞게 잡았지만 `name`은 any다. 적용 후 속성 목록을 훑으며 any들을 고쳐라. 클래스의 전체 속성 목록을 처음 보는 것이라면 충격받을 수도 있다 - 저자가 dygraph.js의 메인 클래스를 변환했을 때 멤버 변수가 무려 45개였다. **타입스크립트 마이그레이션은 이전까지 암묵적이던 나쁜 설계를 드러내는 힘이 있다.** 봐야만 하는 나쁜 설계는 정당화하기 어렵다. 하지만 역시, 지금 리팩터링하려는 충동은 참아라.

**② 타입이 바뀌는 값** - Item 21에서 다룬 주제다.

```typescript
const state = {};
state.name = 'New York';
//    ~~~~ Property 'name' does not exist on type '{}'
state.capital = 'Albany';
//    ~~~~~~~ Property 'capital' does not exist on type '{}'
```

수정이 사소하면 객체를 한 번에 만들면 되고, 아니면 지금이 타입 단언을 쓸 적기다.

```typescript
interface State {
  name: string;
  capital: string;
}
const state = {} as State;
state.name = 'New York';   // OK
state.capital = 'Albany';  // OK
```

단언은 문제적이고 피하는 것이 좋으니(Item 9) 결국 리팩터링해야 하지만, 지금은 편법이 마이그레이션을 계속 굴러가게 해 준다. TODO 주석이나 버그를 남겨 둬라.

**③ JSDoc에서 타입 안전성 유실** - @ts-check와 JSDoc(Item 80)을 쓰고 있었다면 **변환하면서 오히려 타입 안전성을 잃을 수 있다.** .ts가 되는 순간 @ts-check와 JSDoc이 강제되기를 멈춰서, `@param {number} num`이 있어도 num은 암시적 any가 되고 `double('trouble')`이 통과한다. 다행히 **JSDoc 타입을 타입스크립트 타입으로 옮기는 빠른 수정**이 있으니 있으면 써라. 옮긴 뒤에는 중복을 피해 JSDoc에서 타입을 제거하라(Item 31). noImplicitAny를 켜면 잡힐 문제지만 지금 타입을 넣어 두는 편이 낫다.

## 4. 테스트는 마지막에

테스트를 마지막에 마이그레이션하라. 의존성 그래프의 꼭대기에 있을 것이고(프로덕션 코드가 테스트를 import하지 않으니까), **테스트를 전혀 바꾸지 않았는데도 마이그레이션 내내 계속 통과한다는 사실이 극도로 안심된다.** 타입스크립트 마이그레이션은 순수 리팩터링이다 - 코드나 테스트의 런타임 동작을 바꾸면 안 된다.

## 기억해야 할 것들

- 마이그레이션은 서드파티 모듈과 외부 API 호출의 @types 추가로 시작하라.
- 내 모듈은 의존성 그래프의 바닥에서 위로 마이그레이션하라. 첫 모듈은 보통 유틸리티 코드다. 진행 추적을 위해 그래프 시각화를 고려하라.
- 이상한 설계를 발견해도 리팩터링하려는 충동을 참아라. 미래의 리팩터링 아이디어 목록을 관리하되 타입스크립트 변환에 집중하라.
- 변환 중 나오는 흔한 에러들을 알아 두라. 타입 안전성을 잃지 않으려면 필요시 JSDoc 타입을 타입스크립트 타입 구문으로 옮겨라.
