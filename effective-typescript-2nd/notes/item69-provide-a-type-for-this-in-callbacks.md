# Item 69: 콜백에서 this가 API의 일부라면 타입 제공하기 (Provide a Type for this in Callbacks if It's Part of Their API)

## 핵심 질문

동적으로 바인딩되는 this는 어떻게 동작하고, 타입스크립트는 그것을 어떻게 모델링하는가?

자바스크립트의 `this`는 언어에서 가장 악명 높게 혼란스러운 부분이다. 렉시컬 스코프인 `let`·`const` 변수와 달리 **`this`는 동적 스코프**다 — 값이 코드의 어디에 나타나는지가 아니라 **어떻게 거기 도달했는지**에 달렸다.

## 1. this 바인딩의 동작

this는 클래스에서 가장 많이 쓰이며 보통 객체의 현재 인스턴스를 가리킨다.

```typescript
class C {
  vals = [1, 2, 3];
  logSquares() {
    for (const val of this.vals) {
      console.log(val ** 2);
    }
  }
}

const c = new C();
c.logSquares();  // 1 4 9
```

그런데 `logSquares`를 변수에 담아 호출하면:

```typescript
const c = new C();
const method = c.logSquares;
method();
// TypeError: Cannot read properties of undefined (reading 'vals')
```

`c.logSquares()`는 사실 두 가지 일을 한다 — `C.prototype.logSquares`를 호출하고, 그 함수 안의 `this`를 `c`에 **바인딩**한다. 참조를 뽑아내면서 이 둘이 분리됐고 this는 undefined가 됐다. 자바스크립트는 this 바인딩의 완전한 통제권을 준다 — `call`로 명시적으로 설정해 고칠 수 있다.

```typescript
const method = c.logSquares;
method.call(c);  // 다시 제곱들이 출력된다
```

this가 C의 인스턴스에 바인딩되어야 할 이유는 없다 — 무엇에든 바인딩될 수 있다. 그래서 라이브러리들은 **this의 값을 API의 일부로** 만들 수 있고 실제로 그렇게 한다. DOM의 이벤트 핸들러도 그렇다.

```typescript
document.querySelector('input')?.addEventListener('change', function(e) {
  console.log(this);  // 이벤트가 발생한 input 요소를 출력
});
```

## 2. 콜백과 this — 고전적 함정과 해법

클래스 안에 onClick 핸들러를 정의한다면:

```typescript
class ResetButton {
  render() {
    return makeButton({text: 'Reset', onClick: this.onClick});
  }
  onClick() {
    alert(`Reset ${this}`);
  }
}
```

버튼을 클릭하면 "Reset undefined"가 뜬다. 이런! 범인은 역시 this 바인딩이다. 흔한 해법은 생성자에서 바인딩된 버전을 만드는 것.

```typescript
class ResetButton {
  constructor() {
    this.onClick = this.onClick.bind(this);
  }
  render() {
    return makeButton({text: 'Reset', onClick: this.onClick});
  }
  onClick() {
    alert(`Reset ${this}`);
  }
}
```

`onClick() { ... }` 정의는 `ResetButton.prototype`의 속성으로 모든 인스턴스가 공유한다. 생성자에서 `this.onClick = ...`로 바인딩하면 **인스턴스에** this가 바인딩된 `onClick` 속성이 생기고, 조회 순서에서 인스턴스 속성이 프로토타입 속성보다 앞서므로 `render()`의 `this.onClick`은 바인딩된 함수를 가리킨다.

극히 편리한 축약이 있다 — 화살표 함수 속성.

```typescript
class ResetButton {
  render() {
    return makeButton({text: 'Reset', onClick: this.onClick});
  }
  onClick = () => {
    alert(`Reset ${this}`);  // "this"는 ResetButton 인스턴스를 가리킨다
  }
}
```

ResetButton이 생성될 때마다 적절한 this가 설정된 새 함수가 정의된다(생성된 자바스크립트를 보면 생성자 안에서 화살표 함수를 할당하는 코드가 된다).

## 3. 타입스크립트에서 — this 매개변수

this 바인딩은 자바스크립트의 일부이므로 타입스크립트가 모델링한다. **콜백의 this 값을 설정하는 라이브러리를 만들거나 타이핑한다면 그것도 모델링해야 한다.** 콜백에 `this` 매개변수를 추가하면 된다.

```typescript
function addKeyListener(
  el: HTMLElement,
  listener: (this: HTMLElement, e: KeyboardEvent) => void
) {
  el.addEventListener('keydown', e => listener.call(el, e));
}
```

`this` 매개변수는 특별하다 — **또 하나의 위치 인수가 아니다.** 두 인수로 호출하려 하면 알 수 있다.

```typescript
el.addEventListener('keydown', e => {
  listener(el, e);
  //           ~ Expected 1 arguments, but got 2
});
```

더 좋은 것은, **올바른 this 컨텍스트로 호출하는지도 강제**한다는 점이다.

```typescript
el.addEventListener('keydown', e => {
  listener(e);
  // ~~~~~~~~ The 'this' context of type 'void' is not assignable
  //          to method's 'this' of type 'HTMLElement'
});
```

이 함수의 사용자는 콜백에서 this를 참조하며 완전한 타입 안전성을 얻는다.

```typescript
declare let el: HTMLElement;
addKeyListener(el, function(e) {
  console.log(this.innerHTML);
  //          ^? this: HTMLElement
});
```

물론 화살표 함수를 쓰면 this의 값을 덮어쓰게 되는데, 타입스크립트가 그 문제도 잡아 준다.

```typescript
class Foo {
  registerHandler(el: HTMLElement) {
    addKeyListener(el, e => {
      console.log(this.innerHTML);
      //               ~~~~~~~~~ Property 'innerHTML' does not exist on 'Foo'
    });
  }
}
```

> **핵심 통찰**: this를 잊지 마라! 콜백에서 this의 값을 설정한다면 그것은 API의 일부이고 타입 선언에 포함해야 한다. 다만 **새 API를 설계한다면 동적 this 바인딩은 쓰지 않는 것이 좋다** — 역사적으로 인기 있었지만 늘 혼란의 원천이었고, 화살표 함수가 만연한 모던 자바스크립트에서 이런 API는 쓰기가 훨씬 어렵다.

## 기억해야 할 것들

- this 바인딩이 어떻게 동작하는지 이해하라.
- 콜백의 this가 API의 일부라면 타입을 제공하라.
- 새 API에서는 동적 this 바인딩을 피하라.
