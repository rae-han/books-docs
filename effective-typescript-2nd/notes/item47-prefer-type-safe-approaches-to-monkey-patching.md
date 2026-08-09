# Item 47: 몽키 패치에는 타입 안전한 접근 선호하기 (Prefer Type-Safe Approaches to Monkey Patching)

## 핵심 질문

window나 DOM에 데이터를 붙여야만 한다면, `(document as any)`보다 나은 방법은 무엇인가?

자바스크립트의 유명한 특징 하나는 객체와 클래스가 "열려" 있어서 임의의 속성을 추가할 수 있다는 것이다. `window`나 `document`에 할당해 전역 변수를 만들거나, DOM 요소에 데이터를 붙이는 데 종종 쓰인다.

```javascript
window.monkey = 'Tamarin';
document.monkey = 'Howler';

const el = document.getElementById('colobus');
el.home = 'tree';
```

런타임에 내장 객체에 속성을 추가하는 것을 몽키 패치(*monkey patching - 내장 객체·클래스·프로토타입을 런타임에 수정하는 것*)라 하며, jQuery나 D3를 쓰는 코드에서 특히 흔하다. 내장 타입의 프로토타입에도 붙일 수 있고 결과는 때로 놀랍다.

```javascript
> RegExp.prototype.monkey = 'Capuchin'
> /123/.monkey
'Capuchin'
```

일반적으로 좋은 설계가 아니다. window나 DOM 노드에 데이터를 붙이는 것은 본질적으로 **전역 변수**를 만드는 것 - 멀리 떨어진 부분들 사이에 무심코 의존성을 만들고, 함수를 호출할 때마다 부수효과를 생각해야 하게 만든다.

타입스크립트를 더하면 문제가 하나 더 생긴다. 타입 체커는 `Document`·`HTMLElement`의 내장 속성은 알지만 내가 추가한 것은 모른다.

```typescript
document.monkey = 'Tamarin';
//       ~~~~~~ Property 'monkey' does not exist on type 'Document'
```

가장 손쉬운 수정은 any 단언이지만, 타입 안전성과 언어 서비스를 잃는다.

```typescript
(document as any).monkey = 'Tamarin';  // OK
(document as any).monky = 'Tamarin';   // 이것도 OK - 오타인데
(document as any).monkey = /Tamarin/;  // 이것도 OK - 타입이 틀렸는데
```

**최선의 해법은 데이터를 window·document·DOM 밖으로 옮기는 것**이다. 하지만 그럴 수 없다면(그것을 요구하는 라이브러리를 쓰거나 마이그레이션 중이라면) 몽키 패치는 내 환경의 일부이므로(Item 76) 타입스크립트로 모델링해야 한다. 완벽한 방법은 없지만 `as any`보다는 훨씬 잘할 수 있다.

## 1. 방법 ① - 인터페이스 보강 (declare global)

로그인한 사용자 정보를 페이지 로드 시 가져와 전역 변수로 저장하는 웹 앱:

```typescript
interface User {
  name: string;
}

document.addEventListener("DOMContentLoaded", async () => {
  const response = await fetch('/api/users/current-user');
  const user = (await response.json()) as User;
  window.user = user;
  //     ~~~~ Property 'user' does not exist
  //          on type 'Window & typeof globalThis'.
});

export function greetUser() {
  alert(`Hello ${window.user.name}!`);
  //             ~~~~ Property 'user' does not exist on type Window...
}
```

`(window as any)` 대신 인터페이스의 특수 능력인 **보강(augmentation)**(Item 13)을 쓸 수 있다.

```typescript
declare global {
  interface Window {
    /** 현재 로그인한 사용자 */
    user: User;
  }
}
```

내장 DOM 타입이 몰랐던 속성이 `Window`에 있다고 알리는 것이다. any보다 나은 점:

1. **타입 안전성** - 오타나 잘못된 타입의 할당을 잡는다.
2. 속성에 **문서**를 붙일 수 있다(Item 68).
3. **자동완성** 등 언어 서비스가 동작한다.
4. 몽키 패치가 정확히 무엇인지 **기록**이 남는다.

보강의 문제도 있다. `user`처럼 앱 실행 중에 설정되는 전역의 경우, **설정된 이후에만 보강을 적용할 방법이 없다.** 이것이 코드의 경쟁 조건을 가린다 - `window.user`가 설정되기 전에 `greetUser()`를 부르면? 이런 문제를 피하려면 전역에 `undefined` 가능성을 포함시켜서 접근하는 곳마다 없을 가능성을 처리하도록 강제할 수 있다.

```typescript
declare global {
  interface Window {
    /** 현재 로그인한 사용자 */
    user: User | undefined;
  }
}

export function greetUser() {
  alert(`Hello ${window.user.name}!`);
  //             ~~~~~~~~~~~ 'window.user' is possibly 'undefined'.
}
```

정확성과 편의 사이의 트레이드오프다. 서빙 인프라가 허락한다면 이 특정 상황의 또 다른 해법은 `user` 변수를 페이지 HTML에 인라인하는 것이다 - 어떤 코드보다 먼저 무조건 설정되므로 경쟁 조건이 사라지고 undefined 가능성을 안전하게 지울 수 있다.

```html
<script type="text/javascript">
window.user = { name: 'Bill Withers' };
</script>
<script src="your-code.js"></script>
```

보강의 또 다른 문제는 `declare global`이라는 이름대로 **전역으로 적용된다**는 것이다. 코드의 다른 부분이나 라이브러리로부터 감출 수 없다. 앱이 여러 페이지로 되어 있고 `user`가 일부 페이지에만 있다면, 전역 보강으로는 정확히 모델링할 수 없다.

## 2. 방법 ② - 더 좁은 타입 단언 (커스텀 타입)

전역 스코프를 오염시키지 않는 대안은 추가 속성을 가진 별도 타입을 정의하고 단언하는 것이다.

```typescript
type MyWindow = (typeof window) & {
  /** 현재 로그인한 사용자 */
  user: User | undefined;
}

document.addEventListener("DOMContentLoaded", async () => {
  const response = await fetch('/api/users/current-user');
  const user = (await response.json()) as User;
  (window as MyWindow).user = user;  // OK
});

export function greetUser() {
  alert(`Hello ${(window as MyWindow).user.name}!`);
  //             ~~~~~~~~~~~~~~~~~~~~~~~~~ Object is possibly 'undefined'.
}
```

`Window`와 `MyWindow`가 속성을 공유하므로 타입스크립트가 이 단언을 허용하고(Item 9), 할당에 타입 안전성도 생긴다. 스코프 문제도 다루기 쉬워진다 - `Window` 타입의 전역 수정 없이 새 타입 하나를 도입했을 뿐이고, import한 곳에서만 스코프에 들어온다.

단점은 몽키 패치된 속성을 참조할 때마다 단언(또는 새 변수)을 써야 한다는 것, 그리고 누군가 `(window as any)`를 슬쩍 끼워 넣지 못하게 (아마 린터 룰로) 단속해야 한다는 것이다. 하지만 이 모든 것을 **더 구조적인 코드로 리팩터링하라는 격려**로 받아들여도 좋다 - 몽키 패치가 너무 쉬우면 안 되니까!

## 기억해야 할 것들

- 전역이나 DOM에 데이터를 저장하기보다 구조화된 코드를 선호하라.
- 내장 타입에 데이터를 저장해야 한다면 타입 안전한 접근(보강 또는 커스텀 인터페이스 단언) 중 하나를 사용하라.
- 보강의 스코프 문제를 이해하라. 런타임에 가능성이 있다면 undefined를 포함시켜라.
