# Item 80: @ts-check와 JSDoc으로 타입스크립트 실험하기 (Use @ts-check and JSDoc to Experiment with TypeScript)

## 핵심 질문

파일을 .ts로 바꾸기 전에, 마이그레이션에서 어떤 문제가 나올지 미리 가늠하는 방법은?

소스 파일을 자바스크립트에서 타입스크립트로 변환하기(Item 81) 전에 타입 체크를 실험해서 어떤 문제가 나올지 초기 감을 잡고 싶을 수 있다. `@ts-check` 지시어가 정확히 그것을 해 준다 - 파일 하나를 분석해 찾은 문제를 보고하게 한다. **극히 느슨한 버전의 타입 체크**(noImplicitAny를 끈 타입스크립트보다도 느슨한)라고 생각하면 된다.

```javascript
// @ts-check
const person = {first: 'Grace', last: 'Hopper'};
2 * person.first
//  ~~~~~~~~~~~~ The right-hand side of an arithmetic operation must be of
//               type 'any', 'number', 'bigint' or an enum type
```

`person.first`가 string으로 추론되어 타입 구문 없이도 에러가 잡혔다. 이런 노골적인 타입 에러나 인수 과다 호출도 잡지만, 실전에서 @ts-check가 주로 드러내는 것은 몇 가지 특정 유형이다.

## 1. 선언되지 않은 전역

내가 정의하는 심벌이면 let/const로 선언하면 된다. 다른 곳(HTML의 `<script>` 태그 등)에서 정의되는 "환경(ambient)" 심벌이면 타입 선언 파일을 만든다.

```javascript
// @ts-check
console.log(user.firstName);
//          ~~~~ Cannot find name 'user'
```

```typescript
// types.d.ts
interface UserData {
  firstName: string;
  lastName: string;
}
declare let user: UserData;
```

타입스크립트가 이 파일을 인지하도록 tsconfig.json 조정이 필요할 수 있다. 이 types.d.ts는 귀중한 산물이다 - **코드가 실행되는 환경을 모델링**하며(Item 76) 프로젝트 타입 선언의 기초가 된다.

## 2. 모르는 라이브러리

서드파티 라이브러리를 쓰면 타입스크립트가 그것을 알아야 한다. jQuery로 요소 크기를 설정한다면:

```javascript
// @ts-check
$('#graph').style({'width': '100px', 'height': '100px'});
// Error: Cannot find name '$'
```

타입 선언 설치가 해법이다.

```
$ npm install --save-dev @types/jquery
```

이제 에러가 jQuery에 특정된 것으로 바뀐다.

```javascript
$('#graph').style({'width': '100px', 'height': '100px'});
//          ~~~~~ Property 'style' does not exist on type 'JQuery<HTMLElement>'
```

실제로 `.style`이 아니라 `.css`여야 한다. **@ts-check 덕에 직접 마이그레이션하지 않고도 인기 라이브러리의 타입스크립트 선언을 활용할 수 있다** - 이것이 @ts-check를 쓸 최고의 이유 중 하나다. 쓰는 라이브러리 버전에 맞는 타입을 설치할 것(버전 불일치는 Item 66).

## 3. DOM 문제

브라우저에서 도는 코드라면 DOM 요소 처리에 관한 문제가 나올 가능성이 높다.

```javascript
// @ts-check
const ageEl = document.getElementById('age');
ageEl.value = '12';
//    ~~~~~ Property 'value' does not exist on type 'HTMLElement'
```

`value`는 HTMLInputElement에만 있는데 getElementById는 더 일반적인 HTMLElement를 반환한다(Item 75). `#age`가 정말 input 요소임을 안다면 타입 단언이 적절한 자리다 - 하지만 아직 JS 파일이라 `as HTMLInputElement`라고 쓸 수 없다. 대신 **JSDoc으로 단언**한다.

```javascript
// @ts-check
const ageEl = /** @type {HTMLInputElement} */(document.getElementById('age'));
ageEl.value = '12';  // OK
```

주석 뒤의 **괄호가 필수**라는 것에 주의하며 입력하라.

## 4. 부정확한 JSDoc

프로젝트에 이미 JSDoc 스타일 주석이 있다면 @ts-check를 켜는 순간 검사가 시작된다. Closure Compiler처럼 주석 기반 타입 체크를 쓰던 프로젝트라면 큰 문제가 없겠지만, 주석이 "희망 사항 JSDoc"에 가까웠다면 놀랄 수 있다.

```javascript
// @ts-check
/**
 * Gets the size (in pixels) of an element.
 * @param {Node} el The element
 * @return {{w: number, h: number}} The size
 */
function getSize(el) {
  const bounds = el.getBoundingClientRect();
  //             ~~~~~~~~~~~~~~~~~~~~~
  // Property 'getBoundingClientRect' does not exist on type 'Node'
  return {width: bounds.width, height: bounds.height};
  //     ~~~~~ Type '{ width: any; height: any; }' is not
  //           assignable to type '{ w: number; h: number; }'
}
```

첫 문제는 DOM 오해다 - `getBoundingClientRect()`는 Node가 아니라 Element에 정의되어 있으니 @param을 고쳐야 한다. 둘째는 @return과 구현의 속성 불일치 - 프로젝트의 나머지가 width·height를 쓰고 있을 테니 @return을 고치거나, 타입스크립트가 반환 타입을 잘 추론하니 아예 지워도 된다.

JSDoc으로 점진적으로 타입 구문을 추가할 수 있다. 사용처에서 분명한 경우 언어 서비스가 타입 추론을 빠른 수정으로 제안해 준다(`function double(val)`의 val 밑에 점선 밑줄 → 클릭 → `@param {number} val` 생성). 하지만 항상 잘 통하지는 않는다 - `data.files.forEach(...)`를 쓰는 함수에서 빠른 수정을 쓰면 `files: { forEach: (arg0: (file: any) => Promise<void>) => void; }` 같은 **구조적 타이핑이 탈선한** 주석이 나온다. 의도는 십중팔구 `{files: string[]}`이었을 텐데.

## 5. 목표를 잊지 말 것

JSDoc과 @ts-check로 자바스크립트 프로젝트에서 타입스크립트 경험의 상당 부분을 얻을 수 있다. 도구 변경이 필요 없어 매력적이지만 **이 방향으로 너무 가지는 마라.** 주석 보일러플레이트에는 실제 비용이 있다 - 로직이 JSDoc의 바다에 빠지기 쉽다. 타입스크립트는 .js가 아니라 .ts 파일과 가장 잘 동작한다. 궁극의 목표는 프로젝트를 타입스크립트로 변환하는 것이지, JSDoc 주석 달린 자바스크립트가 아니다.

> **핵심 통찰**: @ts-check의 진짜 가치는 조직적이다 - 타입을 실험하고, 장애물을 발견하고, 경영진에게 몇 주~몇 달짜리 타입스크립트 전환의 승인을 요청하기 전에 마이그레이션이 얼마나 어려울지 감을 잡는 유용한 방법이다.

## 기억해야 할 것들

- 자바스크립트 파일 맨 위에 `// @ts-check`를 추가하면 타입스크립트로 변환하지 않고도 타입 체크를 켤 수 있다.
- 흔한 에러들을 알아보라. 전역을 선언하는 법과 서드파티 라이브러리의 타입 선언을 추가하는 법을 알아 두라.
- 타입 단언과 더 나은 타입 추론을 위해 JSDoc 구문을 사용하라.
- JSDoc으로 코드를 완벽하게 타이핑하는 데 너무 시간을 쓰지 마라. 목표는 .ts로의 변환임을 기억하라!
