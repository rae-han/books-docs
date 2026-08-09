# Item 75: DOM 계층 이해하기 (Understand the DOM Hierarchy)

## 핵심 질문

멀쩡해 보이는 DOM 코드 14줄에서 왜 타입 에러가 11개나 나는가? EventTarget·Node·Element·HTMLElement는 어떻게 다른가?

이 책 대부분의 아이템은 실행 환경(브라우저·서버·폰)에 무관하지만 이것은 다르다. 브라우저에서 자바스크립트를 돌릴 때 DOM 계층은 항상 존재한다. 자바스크립트에서는 분류 체계를 잘 몰라도 원하는 메서드를 부르고 잘되길 빌면 됐지만, **타입스크립트에서는 DOM 요소의 계층이 더 가시화된다.** Node와 Element와 EventTarget을 구별할 줄 알면 타입 에러를 디버깅하고 타입 단언이 적절한 때를 판단하는 데 도움이 된다 - React나 D3 같은 프레임워크를 쓰더라도 많은 API가 DOM에 기반하므로 유효한 이야기다.

## 1. 11개의 에러 - 무엇이 문제인가

사용자가 `<div>` 위에서 마우스를 드래그하는 것을 추적하는, 아무 문제 없어 보이는 자바스크립트에 타입 구문을 붙이면:

```typescript
function handleDrag(eDown: Event) {
  const targetEl = eDown.currentTarget;
  targetEl.classList.add('dragging');
  // ~~~~~ 'targetEl' is possibly 'null'
  //       ~~~~~~~~~ Property 'classList' does not exist on type 'EventTarget'
  const dragStart = [
    eDown.clientX, eDown.clientY
    //    ~~~~~~~        ~~~~~~~ Property '...' does not exist on 'Event'
  ];
  // ... (비슷한 에러들이 계속)
}
const surfaceEl = document.getElementById('surface');
surfaceEl.addEventListener('mousedown', handleDrag);
// ~~~~~~ 'surfaceEl' is possibly 'null'
```

14줄에 에러 11개다. EventTarget이 뭐고, 왜 다 null일 수 있다는 걸까?

## 2. DOM 타입 계층

```html
<p id="quote">and <i>yet</i> it moves</p>
```

브라우저 콘솔에서 이 p 요소를 보면 `HTMLParagraphElement`다. 이것은 `HTMLElement`의 서브타입이고, 그것은 `Element`의, 그것은 `Node`의, 그것은 `EventTarget`의 서브타입이다. **전부 자바스크립트 런타임 값이지 타입스크립트만의 타입이 아니다.**

| 타입 | 예 |
|------|-----|
| EventTarget | window, XMLHttpRequest |
| Node | document, Text, Comment |
| Element | HTMLElement들, SVGElement들 |
| HTMLElement | `<i>`, `<b>` |
| HTMLButtonElement | `<button>` |

- **EventTarget**: 가장 일반적인 DOM 타입. 할 수 있는 것은 이벤트 리스너 추가·제거와 이벤트 디스패치뿐이다. 이제 classList 에러가 이해된다 - 이름대로 Event의 `currentTarget` 속성은 EventTarget이고 null일 수도 있다. 실제로는 HTMLElement겠지만 타입 시스템 관점에서는 window나 XMLHttpRequest가 아니어야 할 이유가 없다. (`currentTarget`은 리스너를 등록한 요소, `target`은 이벤트가 발원한 요소 - 서로 타입이 다를 수 있다.)
- **Node**: Element가 아닌 Node에는 텍스트 조각과 주석이 있다. `p.children`은 자식 **Element**만 담은 HTMLCollection을, `p.childNodes`는 텍스트 조각·주석까지 담은 NodeList(배열 비슷한 Node 모음)를 반환한다. 진짜 배열이 필요하면 스프레드(`[...p.childNodes]`)를 쓴다.
- **Element vs HTMLElement**: HTML이 아닌 Element들이 있다 - SVG 태그의 전체 계층(SVGElement)이 그렇다. `<html>`은 HTMLHtmlElement, `<svg>`는 SVGSVGElement다. SVG나 MathML을 안 쓰면 실질적으로 모든 Element는 HTMLElement다.
- **특화된 Element**: 고유 속성이 있다 - HTMLImageElement의 `src`, HTMLInputElement의 `value`. 이런 속성을 읽으려면 타입이 그만큼 구체적이어야 한다.

타입스크립트의 DOM 타입 선언은 리터럴 타입을 아낌없이 써서 가장 구체적인 타입을 주려 한다.

```typescript
const p = document.getElementsByTagName('p')[0];
//    ^? const p: HTMLParagraphElement
const button = document.createElement('button');
//    ^? const button: HTMLButtonElement
const div = document.querySelector('div');
//    ^? const div: HTMLDivElement | null
```

하지만 항상 가능하지는 않다 - 특히 `document.getElementById`.

```typescript
const div = document.getElementById('my-div');
//    ^? const div: HTMLElement | null
```

단언은 일반적으로 눈총받지만(Item 9), 이것은 **내가 타입스크립트보다 더 아는 경우**라 적절하다 - `#my-div`가 div인 것을 안다면 `as HTMLDivElement`에 아무 문제가 없다. 모르면 런타임 체크가 해 준다.

```typescript
const div = document.getElementById('my-div');
if (div instanceof HTMLDivElement) {
  console.log(div);
  //          ^? const div: HTMLDivElement
}
```

(HTMLElement의 더 정밀한 타입을 얻는 또 다른 방법은 Item 54.) `strictNullChecks`에서는 getElementById의 null 케이스를 고려해야 한다 - 실제로 일어날 수 있는지에 따라 if 문 또는 널 아님 단언(`!`)을 쓴다. 참고로 이 타입들은 타입스크립트 전용이 아니라 **DOM의 공식 명세에서 생성**된 것이다 - 가능하면 명세에서 타입을 생성하라는 Item 42의 조언의 사례다.

## 3. Event 계층

clientX·clientY 에러는? Node·Element 계층에 더해 **Event의 계층**도 있다. `lib.dom.d.ts`에는 Event의 서브타입이 무려 54개 정의되어 있다. 평범한 `Event`가 가장 일반적이고, 더 구체적으로:

- **UIEvent**: 모든 종류의 사용자 인터페이스 이벤트
- **MouseEvent**: 클릭 등 마우스가 발생시킨 이벤트
- **TouchEvent**: 모바일 기기의 터치 이벤트
- **KeyboardEvent**: 키 입력

`handleDrag`의 문제는 이벤트를 `Event`로 선언했는데 `clientX`·`clientY`는 더 구체적인 `MouseEvent`에만 있다는 것이다.

## 4. 고치기 - 문맥 주기

Item 24에서 봤듯 타입스크립트는 문맥으로 더 정밀한 타입을 추론하며 DOM 선언이 이를 광범위하게 활용한다. **mousedown 핸들러를 인라인**하면 문맥이 생겨 에러 대부분이 사라진다. 매개변수 타입을 Event 대신 MouseEvent로 선언할 수도 있다. 타입 체커를 통과하는 완성본:

```typescript
function addDragHandler(el: HTMLElement) {
  el.addEventListener('mousedown', eDown => {
    const dragStart = [eDown.clientX, eDown.clientY];
    const handleUp = (eUp: MouseEvent) => {
      el.classList.remove('dragging');
      el.removeEventListener('mouseup', handleUp);
      const dragEnd = [eUp.clientX, eUp.clientY];
      console.log('dx, dy = ', [0, 1].map(i => dragEnd[i] - dragStart[i]));
    }
    el.addEventListener('mouseup', handleUp);
  });
}

const surfaceEl = document.getElementById('surface');
if (surfaceEl) {
  addDragHandler(surfaceEl);
}
```

끝의 if 문은 `#surface` 요소가 없을 가능성을 처리한다(존재를 확신하면 `surfaceEl!`). `addDragHandler`는 non-null HTMLElement를 요구한다 - null을 가장자리로 밀어내라는 Item 33의 조언을 따른 것이다.

## 기억해야 할 것들

- DOM에는 자바스크립트를 쓸 때는 대개 무시할 수 있는 타입 계층이 있다. 타입스크립트에서는 이 타입들이 더 중요해지며, 이해하면 브라우저용 타입스크립트 작성에 도움이 된다.
- Node·Element·HTMLElement·EventTarget의 차이, 그리고 Event와 MouseEvent의 차이를 알아 두라.
- 코드의 DOM 요소와 이벤트에 충분히 구체적인 타입을 쓰거나, 타입스크립트가 추론할 수 있는 문맥을 제공하라.
