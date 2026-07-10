# Chapter 18: OOP Frontend Applications (객체지향 프런트엔드 응용)

> **참고**: 이 장은 멀티패러다임 노트 7장의 이관본으로, 본문의 `[코드 7-N]` 번호는 원본 기준이다.

## 핵심 질문

현대 프런트엔드 개발에서 객체지향 프로그래밍은 왜 여전히 중요하며, 함수형 프로그래밍과 어떻게 결합하면 더 나은 소프트웨어를 만들 수 있을까? 또한 디자인 패턴과 일급 함수를 함께 활용하면 컴포넌트의 재사용성과 확장성을 어떻게 극대화할 수 있을까?

---

현대의 클라이언트 측 개발에서는 UI 렌더링 갱신을 대신 관리해주는 리액티브한 패러다임의 라이브러리가 널리 활용되고 있다. 이러한 라이브러리에서는 선언적인 방식으로 UI 코드를 작성할 수 있고 DOM이나 브라우저 기술을 직접 다루는 과정을 최소화하며 자바스크립트의 내장 객체만으로도 상당 부분의 UI 프로그래밍이 가능하다. 이러한 특징은 분명히 개발 편의성과 생산성을 높여준다.

하지만 여전히 구글 캘린더, 스프레드시트, 피그마처럼 풍부한 기능과 고품질 사용자 경험(UX)을 제공해야 하는 실시간 편집 툴을 만들려면 객체지향 프로그래밍 능력이 필요하다. 이러한 애플리케이션을 개발할 때는 객체지향 기반의 SDK를 통해 UI 요소를 직접 핸들링하고 시스템 자원이나 플랫폼 기능을 유기적으로 연동하는 구조를 이해하며 코딩하는 능력이 요구된다.

또한 방대한 기능을 모듈화하고 관리하는 데도 객체지향적인 접근이 매우 유용하다. 객체지향 프로그래밍 기술은 캡슐화, 추상화, 상속, 다형성 등 명확한 개념 체계를 갖추고 있고 디자인 패턴이나 수많은 SDK 사례들을 포함해 현업에서 오랜 기간 검증된 유산을 가지고 있다.

이러한 객체지향 프로그래밍 패턴과 설계는 웹 브라우저 환경에 국한되지 않는다. iOS, 안드로이드, macOS, 윈도우 등 다양한 운영체제나 플랫폼의 클라이언트 측 프로그래밍에서도 동일하게 적용된다. 이 같은 기반 기술을 익히면 특정 라이브러리나 프레임워크에 의존하지 않고도 더 근본적인 방식으로 코드를 작성할 수 있으며 프로그래밍 업무 영역을 넓히는 데도 용이하다.

이 장에서는 이러한 배경을 바탕으로 타입스크립트와 WebAPI를 사용해 간단한 애플리케이션을 구현하면서 플랫폼 SDK 기반 프로그래밍과 객체지향 프로그래밍을 직접 경험하고 이해를 다진다. 또한 객체지향 설계와 구현에 멀티패러다임적 접근과 응용을 결합해 본다.

> **참고**: 이 장의 예제에서 사용하는 rune-ts의 `html` 및 `View`는 17장에서 구현한 `html` 함수와 `View` 클래스의 역할을 그대로 수행하면서 WebAPI 기반의 간단한 프런트엔드 애플리케이션 개발을 지원하도록 확장한 객체지향적 설계용 키트다.

---

## 1. Setting 앱 만들기

WebAPI는 웹 브라우저 환경에서 동작하는 소프트웨어를 프로그래밍하기 위한 기초 도구다. DOM 조작, Fetch API 등을 포함하는 WebAPI는 WHATWG의 Standards 문서나 MDN 웹 문서를 통해 자세히 살펴볼 수 있다.

이번 절에서는 WebAPI를 토대로 간단한 애플리케이션(Wi-Fi, Bluetooth 등의 ON/OFF 토글 기능을 가지는 Setting 앱)을 만들어 본다. 우리가 활용할 WebAPI 중 다수는 이미 객체지향적으로 설계되어 있다. 최근에는 ES6 모듈과 발전된 번들링 도구 그리고 타입스크립트를 통한 정적 타이핑의 보편화 덕분에 별도의 라이브러리 없이도 잘 설계된 WebAPI 인터페이스 위에 사용자 정의 클래스를 정의하는 것만으로도 충분히 객체지향적이고 확장 가능한 설계를 구현할 수 있게 되었다.

### 1.1 SwitchView

17장에서 구현한 HTML 템플릿 엔진과 `View` 클래스를 확장한 rune-ts의 `html` 함수와 `View` 클래스를 활용해 보겠다. 간단한 스위치 UI 컴포넌트를 구현한 `SwitchView`를 살펴보자. `SwitchView`는 `View`의 관례를 따르므로 `render()` 메서드를 호출하면 실제 DOM 엘리먼트를 반환한다.

```typescript
// [코드 7-1] SwitchView 렌더링
import { html, View } from "rune-ts";

class SwitchView extends View<{ on: boolean }> {
  override template() {
    return html`
      <button class="${this.data.on ? 'on' : ''}">
        <span class="toggle"></span>
      </button>
    `;
  }
}

export function main() {
  console.log(
    new SwitchView({ on: true }).toHtml()
  );
  // <button class="SwitchView on"><span class="toggle"></span></button>

  document.querySelector('#body')!.append(
    new SwitchView({ on: false }).render()
  );
}
```

`SwitchView`는 `View<{ on: boolean }>`을 상속받으며 `data.on`이 `true`이면 `'on'` 클래스를, 그렇지 않으면 빈 문자열을 `<button>` 엘리먼트에 설정한다. `toHtml()`은 HTML 문자열을, `render()`는 실제 DOM 엘리먼트를 반환한다.

### 1.2 SettingItemView

설정 앱의 각 항목(Wi-Fi, Bluetooth 등)을 표현하는 `SettingItemView`는 라벨 텍스트와 `SwitchView`를 조합한다.

```typescript
// [코드 7-2] SettingItemView
type Setting = {
  title: string;
  on: boolean;
};

class SettingItemView extends View<Setting> {
  switchView = new SwitchView({ on: this.data.on });

  override template() {
    return html`
      <div>
        <span class="title">${this.data.title}</span>
        ${this.switchView}
      </div>
    `;
  }
}
```

`SettingItemView`는 `View<Setting>`을 상속받아 `title`과 `on` 상태를 가진다. 내부에 `SwitchView` 인스턴스를 생성하여 스위치 UI를 표현한다.

### 1.3 SettingListView

`SettingListView`는 `Setting[]` 배열을 받아 각 항목마다 `SettingItemView`를 생성한다.

```typescript
// [코드 7-3] SettingListView
class SettingListView extends View<Setting[]> {
  override template() {
    return html`
      <div>
        ${this.data.map(setting => new SettingItemView(setting))}
      </div>
    `;
  }
}
```

`View`의 `template()` 메서드에서 배열을 반환하면 각 요소가 순서대로 렌더링된다. `SettingListView`는 `Setting[]` 데이터를 받아 `SettingItemView` 인스턴스 배열을 템플릿에 삽입한다.

### 1.4 SettingPage

`SettingPage`는 `SwitchView`(전체 토글)와 `SettingListView`(설정 목록)를 조합하여 완성된 설정 페이지를 구성한다.

```typescript
// [코드 7-4] SettingPage
class SettingPage extends View<Setting[]> {
  private switchView = new SwitchView({ on: false });
  private listView = new SettingListView(this.data);

  override template() {
    return html`
      <div>
        <div class="header">
          <h2>Setting</h2>
          ${this.switchView}
        </div>
        <div class="body">
          ${this.listView}
        </div>
      </div>
    `;
  }
}
```

이제 클릭 이벤트를 등록하여 실제로 동작하는 토글 기능을 구현해야 한다.

### 1.5 커스텀 이벤트

`SwitchView`를 클릭하면 데이터를 변경하고 DOM을 업데이트한 후 커스텀 이벤트를 발생시킨다.

```typescript
// [코드 7-5] SwitchView에 클릭 이벤트와 커스텀 이벤트 추가
type Toggle = { on: boolean };

class Toggled extends CustomEvent<Toggle> {
  constructor(detail: Toggle) {
    super('toggled', { bubbles: true, detail });
  }
}

class SwitchView extends View<Toggle> {
  override template() {
    return html`
      <button class="${this.data.on ? 'on' : ''}">
        <span class="toggle"></span>
      </button>
    `;
  }

  protected override onRender() {
    this.addEventListener('click', () => this.toggle());
  }

  private toggle() {
    this.setOn(!this.data.on);
    this.dispatchEvent(Toggled, { bubbles: true, detail: this.data });
  }

  setOn(bool: boolean) {
    this.data.on = bool;
    this.element().classList.toggle('on', bool);
  }
}
```

`SwitchView`는 `onRender()` 시점에 클릭 이벤트 리스너를 등록한다. 클릭하면 `toggle()` 메서드가 실행되어 `data.on`을 반전시키고 DOM 클래스를 업데이트한 뒤 `Toggled` 커스텀 이벤트를 발생시킨다. `bubbles: true`로 설정하여 이벤트가 상위 요소로 전파되도록 한다.

### 1.6 이벤트 루프 문제

여기서 중요한 설계 포인트가 있다. `toggle()` 메서드와 `setOn()` 메서드를 분리한 이유는 이벤트 루프(*Event Loop - 자바스크립트 런타임이 비동기 작업을 처리하는 메커니즘*) 문제를 방지하기 위함이다.

만약 `setOn()` 내부에서도 `Toggled` 이벤트를 발생시키면 무한 루프에 빠질 수 있다. 상위 컴포넌트가 `Toggled` 이벤트를 수신한 후 다시 `setOn()`을 호출하면 또 다시 `Toggled` 이벤트가 발생하는 순환이 생기기 때문이다. 따라서 `toggle()`은 사용자의 직접 클릭에 의해서만 호출되고, `setOn()`은 외부에서 프로그래밍적으로 상태를 변경할 때 사용하는 것으로 역할을 분리한다.

### 1.7 ToggleView 추상 클래스

`SwitchView`의 토글 로직을 다른 뷰에서도 재사용할 수 있도록 추상 클래스(*Abstract Class - 직접 인스턴스화할 수 없고 상속받아 구현해야 하는 클래스*)로 추출한다.

```typescript
// [코드 7-8] ToggleView 추상 클래스
abstract class ToggleView extends View<Toggle> {
  constructor(data?: Toggle) {
    super(data ?? { on: false });
  }

  protected override onRender() {
    this.addEventListener('click', () => this.toggle());
  }

  private toggle() {
    this.setOn(!this.data.on);
    this.dispatchEvent(Toggled, { bubbles: true, detail: this.data });
  }

  setOn(bool: boolean) {
    this.data.on = bool;
    this.element().classList.toggle('on', bool);
  }
}
```

이제 `SwitchView`는 `ToggleView`를 상속받아 `template()`만 구현하면 된다.

```typescript
// [코드 7-9] SwitchView가 ToggleView를 상속
class SwitchView extends ToggleView {
  override template() {
    return html`
      <button class="${this.data.on ? 'on' : ''}">
        <span class="toggle"></span>
      </button>
    `;
  }
}
```

### 1.8 Headless UI

Headless UI(*Headless UI - 비주얼 렌더링 없이 로직과 상태 관리만 제공하는 UI 패턴*)란 특정 시각적 형태에 묶이지 않고 상태 관리와 동작 로직만 제공하여 다양한 시각적 형태로 확장할 수 있는 패턴이다.

`ToggleView`는 토글 상태 관리(`data.on`), 클릭 이벤트 처리(`toggle()`), 외부 상태 설정(`setOn()`), 이벤트 발생(`Toggled`)이라는 핵심 로직을 제공하면서도 시각적 표현은 하위 클래스에 위임한다. `SwitchView`는 스위치 형태로, 나중에 만들 `CheckView`는 체크박스 형태로 동일한 토글 로직을 재사용한다.

### 1.9 타입 안전한 이벤트

rune-ts의 `View` 클래스는 `CustomEventWithDetail<T>` 같은 타입 유틸리티를 제공하여 커스텀 이벤트의 타입 안전성을 보장한다.

```typescript
// [코드 7-10] 타입 안전한 커스텀 이벤트
class CustomEventWithDetail<T> extends CustomEvent<T> {
  declare detail: T;
}

class Toggled extends CustomEventWithDetail<Toggle> {}
```

`Toggled` 이벤트의 `detail` 필드는 `Toggle` 타입으로 고정되어 이벤트 핸들러에서 `e.detail.on`에 안전하게 접근할 수 있다.

### 1.10 GoF의 디자인 패턴 관점으로 보기: 옵저버 패턴

Setting 앱의 이벤트 전파 구조는 GoF의 옵저버(*Observer*) 패턴과 유사하다. `Toggled` 이벤트를 발행하는 `ToggleView`가 Subject 역할을 하고, 이를 구독하는 `SettingPage`가 Observer 역할을 한다. DOM의 `addEventListener`와 `dispatchEvent`가 옵저버 패턴의 구현 기반을 제공한다.

---

## 2. Todo 앱 만들기

이번 절에서는 Todo 앱을 단계별로 구현하면서 객체지향 설계의 핵심 기법들을 실습한다.

### 2.1 CheckView

`ToggleView`를 상속받아 체크박스 형태의 `CheckView`를 구현한다.

```typescript
// [코드 7-12] CheckView
class CheckView extends ToggleView {
  override template() {
    return html`
      <button class="${this.data.on ? 'on' : ''}">
        <span class="check">✓</span>
      </button>
    `;
  }
}
```

`CheckView`는 `SwitchView`와 동일한 토글 로직을 공유하면서도 시각적 표현만 다르다. 이것이 `ToggleView` 추상 클래스의 Headless UI 패턴이 주는 이점이다.

### 2.2 TodoItemView

```typescript
// [코드 7-13] TodoItemView
type Todo = {
  title: string;
  completed: boolean;
};

class TodoItemView extends View<Todo> {
  private checkView = new CheckView({ on: this.data.completed });

  override template() {
    return html`
      <div>
        ${this.checkView}
        <span class="title">${this.data.title}</span>
      </div>
    `;
  }

  protected override onRender() {
    this.checkView.addEventListener(Toggled, () => {
      this.data.completed = this.checkView.data.on;
    });
  }

  setCompleted(bool: boolean) {
    this.checkView.setOn(bool);
    this.data.completed = bool;
  }
}
```

`TodoItemView`는 내부에 `CheckView`를 가지며, 체크 상태 변경 시 `data.completed`를 동기화한다. `setCompleted()` 메서드를 통해 외부에서도 완료 상태를 변경할 수 있다.

### 2.3 도메인 이름과 UI 이름 분리

`Todo` 타입에서는 `completed`라는 도메인 이름을 사용하고 `CheckView`에서는 `on`이라는 UI 이름을 사용한다. 이러한 분리는 중요하다. `CheckView`는 범용 UI 컴포넌트로서 다양한 도메인(Todo의 completed, Setting의 on 등)에 재사용되어야 하기 때문이다. `TodoItemView`가 이 두 세계를 연결하는 어댑터 역할을 한다.

### 2.4 TodoListView

```typescript
// [코드 7-15] TodoListView
class TodoListView extends View<Todo[]> {
  itemViews: TodoItemView[];

  override template() {
    return html`
      <div>
        ${this.itemViews = this.data.map(todo => new TodoItemView(todo))}
      </div>
    `;
  }
}
```

`TodoListView`는 `Todo[]`을 받아 각 항목마다 `TodoItemView`를 생성한다. `itemViews` 배열에 참조를 유지하여 나중에 개별 아이템 뷰에 접근할 수 있다.

### 2.5 ListView

`TodoListView`의 패턴을 제네릭하게 추상화한 `ListView`를 만든다.

```typescript
// [코드 7-16] ListView 제네릭 클래스
type ExtractItemView<T> = T extends ListView<infer IV> ? IV : never;

abstract class ListView<IV extends View<object>> extends View<IV['data'][]> {
  abstract ItemView: new (data: IV['data']) => IV;
  itemViews: IV[] = [];

  override template() {
    return html`
      <div>
        ${this.itemViews = this.data.map(item => new this.ItemView(item))}
      </div>
    `;
  }
}
```

`ListView<IV>`는 아이템 뷰의 타입 `IV`를 제네릭으로 받아 데이터 배열로부터 아이템 뷰 인스턴스를 자동으로 생성한다. `ItemView` 프로퍼티에 실제 아이템 뷰 클래스를 지정하면 된다.

```typescript
// [코드 7-17] TodoListView가 ListView를 상속
class TodoListView extends ListView<TodoItemView> {
  ItemView = TodoItemView;
}
```

`ListView`를 상속받으면 `template()` 구현 없이도 리스트 렌더링이 가능해진다.

### 2.6 TodoPage

```typescript
// [코드 7-18] TodoPage
class TodoPage extends View<Todo[]> {
  private switchView = new SwitchView({ on: false });
  private listView = new TodoListView(this.data);

  override template() {
    return html`
      <div>
        <div class="header">
          ${this.switchView}
          <input type="text">
        </div>
        <div class="body">
          ${this.listView}
        </div>
      </div>
    `;
  }
}
```

### 2.7 TodoPage에 toggle 기능 추가

전체 선택/해제 기능을 `TodoPage`에 직접 구현한다.

```typescript
// [코드 7-19] TodoPage에 toggle 기능 추가
class TodoPage extends View<Todo[]> {
  private switchView = new SwitchView({ on: false });
  private listView = new TodoListView(this.data);

  override template() {
    return html`
      <div>
        <div class="header">
          ${this.switchView}
          <input type="text">
        </div>
        <div class="body">
          ${this.listView}
        </div>
      </div>
    `;
  }

  protected override onRender() {
    this.switchView.data.on = this.isAllOn();
    this.switchView.addEventListener(Toggled, (e) => this.toggleAll(e.detail.on));
    this.listView.addEventListener(Toggled, () => this.syncToggleAllView());
  }

  private toggleAll(on: boolean) {
    this.listView.itemViews
      .filter(itemView => itemView.data.completed !== on)
      .forEach(itemView => itemView.setCompleted(on));
  }

  private syncToggleAllView() {
    this.switchView.setOn(this.isAllOn());
  }

  private isAllOn() {
    return this.listView.itemViews.every(
      itemView => itemView.data.completed
    );
  }
}
```

`toggleAll()`은 현재 상태와 다른 아이템만 변경하고, `syncToggleAllView()`는 모든 아이템이 완료되었는지 확인하여 전체 토글 상태를 동기화한다.

### 2.8 TogglePageController

`SettingPage`에도 동일한 toggle 기능이 필요하다. 중복을 제거하기 위해 `TogglePageController`를 추출한다.

```typescript
// [코드 7-22] TogglePageController
interface TogglePage<LV extends ListView<ExtractItemView<LV>>> {
  toggleAllView: ToggleView;
  listView: LV;
  getItemViewOn(itemView: ExtractItemView<LV>): boolean;
  setItemViewOn(itemView: ExtractItemView<LV>, bool: boolean): void;
}

class TogglePageController<LV extends ListView<ExtractItemView<LV>>> {
  constructor(private togglePage: TogglePage<LV>) {
    const { toggleAllView, listView } = togglePage;
    toggleAllView.data.on = this.isAllOn();
    toggleAllView.addEventListener(Toggled, (e) => this.toggleAll(e.detail.on));
    listView.addEventListener(Toggled, () => this.syncToggleAllView());
  }

  toggleAll(on: boolean) {
    const { listView, getItemViewOn, setItemViewOn } = this.togglePage;
    listView.itemViews
      .filter(itemView => getItemViewOn(itemView) !== on)
      .forEach(itemView => setItemViewOn(itemView, on));
  }

  syncToggleAllView() {
    this.togglePage.toggleAllView.setOn(this.isAllOn());
  }

  isAllOn() {
    return this.togglePage.listView.itemViews.every(
      this.togglePage.getItemViewOn
    );
  }
}
```

`TogglePage` 인터페이스는 toggle 기능에 필요한 최소한의 규약을 정의한다. `TogglePageController`는 이 인터페이스를 통해서만 체크 로직을 수행하므로 구체적인 아이템 뷰나 데이터 모델이 어떻게 동작하는지 전혀 알 필요가 없다.

### 2.9 인터페이스를 활용한 추상화

`TodoPage`와 `SettingPage`가 각각 `TogglePage`를 구현하여 토글 기능을 공유한다.

```typescript
// [코드 7-26] TodoPage가 TogglePage<TodoListView>가 되도록 구현
class TodoPage extends View<Todo[]> implements TogglePage<TodoListView> {
  toggleAllView = new CheckView();
  listView = new TodoListView(this.data);

  getItemViewOn(itemView: TodoItemView): boolean {
    return itemView.data.completed;
  }

  setItemViewOn(itemView: TodoItemView, bool: boolean): void {
    itemView.setCompleted(bool);
  }

  private togglePageController = new TogglePageController(this);

  override template() {
    return html`
      <div>
        <div class="header">
          ${this.toggleAllView}
          <input type="text">
        </div>
        <div class="body">
          ${this.listView}
        </div>
      </div>
    `;
  }
}
```

```typescript
// [코드 7-27] SettingPage가 TogglePage<SettingListView>가 되도록 구현
class SettingPage extends View<Setting[]> implements TogglePage<SettingListView> {
  toggleAllView = new SwitchView();
  listView = new SettingListView(this.data);

  getItemViewOn(itemView: SettingItemView): boolean {
    return itemView.data.on;
  }

  setItemViewOn(itemView: SettingItemView, bool: boolean): void {
    itemView.switchView.setOn(bool);
  }

  private togglePageController = new TogglePageController(this);

  override template() {
    return html`
      <div>
        <div class="header">
          <h2>Setting</h2>
          ${this.toggleAllView}
        </div>
        <div class="body">
          ${this.listView}
        </div>
      </div>
    `;
  }
}
```

이로써 `TogglePageController`는 구체적인 아이템 뷰나 데이터 모델에 의존하지 않으므로 여러 페이지에서 동일한 컨트롤러를 재사용할 수 있다. 각 페이지는 '어느 필드를 체크로 쓸지'만 정하면 된다.

### 2.10 GoF의 디자인 패턴 관점으로 보기: 전략 패턴

`TodoPage`와 `TogglePageController`의 구조는 GoF의 전략(*Strategy*) 패턴과 유사하다. `TogglePageController`가 '문맥(Context)' 역할을 하여 체크 로직을 실행하기 위한 메서드(`toggleAll`, `syncToggleAllView`, `isAllOn`)를 제공한다. 그리고 실제 '체크 상태 확인/설정' 로직은 `TogglePage`를 구현한 다양한 페이지(전략)들이 담당한다.

- **문맥(TogglePageController)**: '체크 로직을 수행할 메서드'를 가지고 있으나 구체적인 '체크 상태를 어떻게 읽고 쓸지'는 외부에 위임한다.
- **전략(TogglePage)**: '체크 상태를 읽고 쓰는' 구체적인 로직을 페이지별로 다르게 구현한다.

### 2.11 일급 함수를 활용한 객체 간 통신: 콜백 인젝션 패턴

GoF가 제시했던 전통적 객체지향 패턴들은 대부분 '클래스 상속' 혹은 '인터페이스 구현'을 통해 확장하고 교체할 수 있도록 설계되었다. 그러나 함수형 프로그래밍 요소가 보편화된 현대 언어에서는 '한두 개의 람다(콜백 함수)'를 인자로 주고받는 것만으로도 원하는 로직의 교체나 확장을 훨씬 간단하게 구현할 수 있다.

```typescript
// [코드 7-28] ToggleListController
export class ToggleListController<
  TV extends ToggleView,
  LV extends ListView<ExtractItemView<LV>>
> {
  constructor(
    public toggleAllView: TV,
    public listView: LV,
    private getItemViewOn: (itemView: ExtractItemView<LV>) => boolean,
    private setItemViewOn: (itemView: ExtractItemView<LV>, bool: boolean) => void
  ) {
    this.toggleAllView.data.on = this.isAllOn();
    this.toggleAllView.addEventListener(Toggled, (e) => this.toggleAll(e.detail.on));
    this.listView.addEventListener(Toggled, () => this.syncToggleAllView());
  }

  toggleAll(bool: boolean) {
    this.listView.itemViews
      .filter(itemView => this.getItemViewOn(itemView) !== bool)
      .forEach(itemView => this.setItemViewOn(itemView, bool));
  }

  syncToggleAllView() {
    this.toggleAllView.setOn(this.isAllOn());
  }

  isAllOn() {
    return this.listView.itemViews.every(this.getItemViewOn);
  }
}
```

`ToggleListController`는 인터페이스 구현이나 메서드 오버라이드 없이 함수 하나로 이 문제를 해결한다. 클래스 내부 로직에서 어떤 필드를 체크 상태로 삼을지, 체크 상태를 어떻게 변경할지 전혀 모르고 오직 콜백으로 받아온 함수를 통해서만 이를 수행한다.

```typescript
// [코드 7-29] TodoPage & ToggleListController
class TodoPage extends View<Todo[]> {
  private toggleListController = new ToggleListController(
    new CheckView(),
    new TodoListView(this.data),
    (itemView) => itemView.data.completed,       // getItemViewOn
    (itemView, bool) => itemView.setCompleted(bool) // setItemViewOn
  );

  override template() {
    return html`
      <div>
        <div class="header">
          ${this.toggleListController.toggleAllView}
          <input type="text">
        </div>
        <div class="body">
          ${this.toggleListController.listView}
        </div>
      </div>
    `;
  }
}
```

`TodoPage`에서는 더 이상 토글 로직에 관한 메서드를 구현할 필요가 없어졌다. 필요한 부분(아이템의 체크 여부 읽기/쓰기)은 `ToggleListController`가 주입받은 두 개의 람다 함수를 통해 처리된다.

```typescript
// [코드 7-29a] SettingPage & ToggleListController
class SettingPage extends View<Setting[]> {
  private toggleAllView = new SwitchView();
  private listView = new SettingListView(this.data);
  private toggleListController = new ToggleListController(
    this.toggleAllView,
    this.listView,
    (itemView) => itemView.data.on,                    // getItemViewOn
    (itemView, bool) => itemView.switchView.setOn(bool) // setItemViewOn
  );

  override template() {
    return html`
      <div>
        <div class="header">
          ${this.toggleAllView}
          <input type="text">
        </div>
        <div class="body">
          ${this.listView}
        </div>
      </div>
    `;
  }
}
```

`TogglePageController`에서는 `SettingPage`의 `toggleAllView`와 `listView`를 반드시 `public`으로 설정해야 했던 것과 달리, `ToggleListController`에서는 이 두 속성을 `private`으로 선언할 수도 있다.

### 2.12 멀티패러다임적인 코드 설계

GoF가 1994년에 발표한 『GoF의 디자인 패턴』은 그 시기 주로 사용하던 C++와 Smalltalk 환경을 전제로 작성되었다. 자바가 공식 출시된 것은 1996년이며 일급 함수를 도입한 시점(2014년 자바 8)은 그보다 훨씬 뒤였기 때문에 당시에는 현대적인 함수형 기법(람다 등)을 결합하기가 어려웠다.

이제 현대 프로그래밍 언어는 객체지향만 지원하지 않고 동시에 함수형 프로그래밍 언어 역할도 수행한다. 객체지향 기반으로 문제를 푼다고 해서 함수형 기법을 배제할 이유가 없고, 함수형을 우선하는 문제에서 클래스를 사용하지 않을 이유도 없다.

그렇기에 현대 언어로는 GoF의 디자인 패턴 일부도 함수를 인자로 넘기는 방식으로 훨씬 단순화할 수 있다. 예컨대 Command나 Strategy는 굳이 객체로 명령/전략을 캡슐화하지 않아도 간단히 람다 하나로 대체할 수 있다. Observer나 Template Method 또한 함수형 스타일로 재정의하면 더 짧고 직관적인 코드로 표현할 수 있다.

핵심은 '책임 분리와 부수 효과 최소화'라는 공통 원칙을 어떻게 녹여내느냐이며, 양쪽 모두 불필요한 복잡도와 부수 효과를 줄이기 위해 같은 방향을 지향한다.

---

## 3. Todo 앱 만들기 2

이제 Todo 앱을 완성하기 위해 남은 기능들을 구현한다.

- 새로운 Todo 항목 등록
- 완료 처리 / 한 번에 모든 항목을 완료로 처리
- 미완료 항목만 또는 완료 항목만 필터링하여 보기

### 3.1 데코레이터로 코드를 간결하게

앞서 `ToggleView`에서는 클릭 이벤트 등록을 `onRender()` 메서드에서 직접 처리했다. 데코레이터(*Decorator - 클래스, 메서드, 접근자, 속성 등에 부가 기능이나 메타데이터를 주입하기 위한 문법 요소*)를 이용하면 이벤트 등록 로직을 훨씬 간단하게 만들 수 있다.

```typescript
// [코드 7-30] 데코레이터 적용 전 ToggleView
abstract class ToggleView extends View<Toggle> {
  constructor(data?: Toggle) {
    super(data ?? { on: false });
  }

  // 아래 부분을 @on('click') 데코레이터로 대체할 수 있다.
  protected override onRender() {
    this.addEventListener('click', () => this.toggle());
  }

  private toggle() {
    this.setOn(!this.data.on);
    this.dispatchEvent(Toggled, { bubbles: true, detail: this.data });
  }

  setOn(bool: boolean) {
    this.data.on = bool;
    this.element().classList.toggle('on', bool);
  }
}
```

```typescript
// [코드 7-31] 데코레이터 적용 후 간결해진 ToggleView
abstract class ToggleView extends View<Toggle> {
  constructor(data?: Toggle) {
    super(data ?? { on: false });
  }

  @on('click')
  private toggle() {
    this.setOn(!this.data.on);
    this.dispatchEvent(Toggled, { bubbles: true, detail: this.data });
  }

  setOn(bool: boolean) {
    this.data.on = bool;
    this.element().classList.toggle('on', bool);
  }
}
```

`onRender()`에 직접 이벤트를 등록하는 로직이 사라지고 데코레이터 `@on('click')`을 통해 `toggle()` 메서드가 클릭 이벤트와 연결됨을 명시한다. '어떤 메서드가 어떤 이벤트를 처리하는지'를 메서드 정의 부분에서 바로 확인할 수 있어 코드 구조가 훨씬 깔끔해진다.

```typescript
// [코드 7-32] @on 데코레이터 구현
function on(eventType) {
  return function(viewPrototype, propertyKey, descriptor) {
    const method = descriptor.value; // 데코레이터가 붙은 실제 메서드 (예: toggle())
    const originalOnRender = viewPrototype.onRender; // 기존 onRender를 임시로 저장
    viewPrototype.onRender = function() { // onRender를 새로 재정의
      this.addEventListener(eventType, method); // 데코레이터 대상 메서드를 이벤트 핸들러로 등록
      originalOnRender.call(this); // 원래 onRender 로직을 이어서 수행
    };
  };
}
```

`@on` 데코레이터는 `onRender`를 오버라이드하여 '이벤트 핸들러 등록 → 원본 onRender 호출' 순서로 실행되도록 한다. 이를 통해 `onRender()` 등에서 이벤트를 일일이 등록하던 과정이 사라지므로 코드가 한층 간결해지고 유지보수도 편리해진다.

데코레이터에 타입 정보를 명시하면 코드의 안전성과 유지보수성을 높일 수 있다.

```typescript
// [코드 7-34] @on 데코레이터에 타입 추가
// @on('click')용 시그니처
function on<K extends keyof HTMLElementEventMap>(
  eventType: K
): <T extends (event: HTMLElementEventMap[K]) => void>(
  target: View,
  propertyKey: string,
  descriptor: TypedPropertyDescriptor<T>
) => void;

// @on(Toggled)용 시그니처
function on<E extends new (...args: any[]) => Event>(
  EventClass: E
): <T extends (event: InstanceType<E>) => void>(
  view: View,
  propertyKey: string,
  descriptor: TypedPropertyDescriptor<T>
) => void;

function on(eventType: any) {
  return function<T extends (e: any) => void>(
    viewPrototype: any,
    propertyKey: string,
    descriptor: TypedPropertyDescriptor<T>
  ) {
    const method: T = descriptor.value!;
    const onRender: () => void = viewPrototype.onRender;
    viewPrototype.onRender = function() {
      this.addEventListener(eventType, method);
      onRender.call(this);
    };
  };
}
```

이렇게 하면 `'click'` 이벤트에는 `MouseEvent`, `Toggled` 이벤트에는 `Toggled` 클래스를 자동 매핑하여 메서드 시그니처가 올바르지 않을 경우 컴파일 타임에 에러를 발생시킨다.

```typescript
// [코드 7-35] 이벤트명으로 인자 타입 추론
class DeleteView extends View<object> {
  @on('click')
  private remove(e: MouseEvent) { // OK
    // ...
  }
}

class MovableView extends View<object> {
  @on('click') // 타입 에러!
  private move(e: KeyboardEvent) {
    // ...
  }
}
// Type '(e: KeyboardEvent) => void' is not assignable to type '(event: MouseEvent) => void'
```

데코레이터는 2.3절에서 살펴본 LISP의 메타프로그래밍에 속하는 기법이다. 타입스크립트에서는 주로 클래스 같은 객체지향 요소의 표현력을 높이는 용도로 데코레이터를 활용한다. 반면 구현 자체는 일급 함수와 고차 함수를 사용하는 함수형 기법에 기반을 두어 멀티패러다임적이라고 할 수 있다.

`TodoItemView`에도 `@on(Toggled)` 데코레이터를 적용하면 코드가 더 간결해진다.

```typescript
// [코드 7-33] TodoItemView에 @on(Toggled) 적용
class TodoItemView extends View<Todo> {
  private checkView = new CheckView({ on: this.data.completed });

  override template() {
    return html`
      <div>
        ${this.checkView}
        <span class="title">${this.data.title}</span>
      </div>
    `;
  }

  @on(Toggled)
  private syncCompleted() {
    this.data.completed = this.checkView.data.on;
  }

  setCompleted(bool: boolean) {
    this.checkView.setOn(bool);
    this.syncCompleted();
  }
}
```

### 3.2 TextSubmitView

텍스트를 입력받은 뒤 [Enter] 키를 누르면 `TextSubmitted` 이벤트를 발생시키는 컴포넌트다.

```typescript
// [코드 7-37] TextSubmitView
class TextSubmitted extends CustomEventWithDetail<string> {}

class TextSubmitView extends View<{ value?: string }> {
  override template() {
    return html`<input type="text" value="${this.data.value ?? ''}">`;
  }

  @on('keypress')
  private keypress(e: KeyboardEvent) {
    if (e.code === 'Enter') {
      const input = e.target as HTMLInputElement;
      const detail = input.value.trim();
      if (detail) {
        this.dispatchEvent(TextSubmitted, { detail, bubbles: true });
        input.value = '';
      }
    }
  }
}
```

`TextSubmitView`는 사용자가 텍스트를 입력한 뒤 [Enter] 키를 누르면 입력 내용을 담은 `TextSubmitted` 커스텀 이벤트를 발생시킨다. 이벤트에 전달되는 `detail`에는 사용자가 입력한 텍스트가 들어가며, 이후 입력 필드 값을 비워 사용자가 다음 텍스트를 입력할 수 있도록 한다.

### 3.3 ListView에 헬퍼 메서드 추가하기

`ListView`에 `ItemView`를 생성하고 DOM에도 추가하는 `append(item)` 메서드를 추가한다.

```typescript
// [코드 7-38] ListView에 append 추가
abstract class ListView<IV extends View<object>> extends View<IV['data'][]> {
  // ... 생략 ...
  append(item: IV['data']): this {
    const itemView = new this.ItemView(item);
    this.data.push(item);
    this.itemViews.push(itemView);
    this.element().append(itemView.render());
    return this;
  }
}
```

`append()` 메서드는 새로운 아이템 데이터를 받아 `ItemView` 인스턴스를 생성한 뒤 내부 상태를 갱신하고 DOM에 추가한다. `return this;`로 메서드 체이닝을 지원한다.

### 3.4 새로운 Todo 생성하기

`TextSubmitView`와 `ListView`의 `append` 메서드를 활용하면 새 Todo 아이템을 쉽게 추가할 수 있다.

```typescript
// [코드 7-39] TodoPage
class TodoPage extends View<Todo[]> {
  private listView = new TodoListView(this.data);
  private toggleListController = new ToggleListController(
    new CheckView(),
    this.listView,
    (itemView) => itemView.data.completed,
    (itemView, bool) => itemView.setCompleted(bool)
  );

  override template() {
    return html`
      <div>
        <div class="header">
          ${this.toggleListController.toggleAllView}
          ${new TextSubmitView({})}
        </div>
        <div class="body">
          ${this.listView}
        </div>
      </div>
    `;
  }

  @on(TextSubmitted)
  private append({ detail: title }: TextSubmitted) {
    const todo: Todo = { title, completed: false };
    this.listView.append(todo);
    this.toggleListController.syncToggleAllView();
  }
}
```

`@on(TextSubmitted)` 데코레이터로 `append`를 이벤트 핸들러로 등록한다. `TextSubmitView`에서 [Enter] 키를 누르면 `TextSubmitted` 이벤트가 발생하며 새 `Todo` 객체를 생성하여 `listView`에 추가한다. 만약 모든 Todo가 이미 완료 상태였다면 새로 생성된 Todo는 아직 완료되지 않은 상태이므로 `syncToggleAllView()`를 호출하여 헤더의 체크 상태를 off로 전환한다.

### 3.5 SegmentControlView

`SegmentControlView`는 여러 필터 옵션을 관리하는 리스트 뷰 형태의 컴포넌트다. All/Active/Completed 같은 필터 옵션을 배열로 전달받아 각 세그먼트를 렌더링하고 현재 선택된 세그먼트를 추적한다.

```typescript
// [코드 7-40] SegmentControlView
type Segment = {
  title: string;
  value?: string;
  selected?: boolean;
};

class SegmentSelected<T extends Segment = Segment> extends CustomEventWithDetail<T> {}

class SegmentItemView<T extends Segment> extends View<T> {
  override template({ selected, title }: T) {
    return html`
      <button class="${selected ? 'selected' : ''}">${title}</button>
    `;
  }
}

class SegmentControlView<T extends Segment> extends ListView<SegmentItemView<T>> {
  ItemView = SegmentItemView;
  selectedIndex: number;

  selectedSegment() {
    return this.data[this.selectedIndex];
  }
  // ... 생략 ...
}
```

`SegmentControlView` 생성자의 첫 번째 인자는 `Segment[]`이며 두 번째 인자는 기본으로 선택되어 있어야 할 옵션의 인덱스(`selectedIndex`)다.

```typescript
// SegmentControlView 사용 예시
const filterView = new SegmentControlView([
  { title: 'All', value: 'all' },
  { title: 'Active', value: 'active' },
  { title: 'Completed', value: 'completed' }
], 1); // 두 번째 옵션(Active)을 기본 선택 상태로

const segment: Segment = filterView.selectedSegment();
console.log(segment);
// { title: 'Active', value: 'active', selected: true }
```

`SegmentControlView`를 `TodoPage`에 적용하면 필터링 기능을 추가할 수 있다.

```typescript
// [코드 7-41] TodoPage에 필터 추가
class TodoPage extends View<Todo[]> {
  private listView = new TodoListView([...this.data]); // 배열 복사로 원본 데이터와 분리
  private toggleListController = new ToggleListController(
    new CheckView(),
    this.listView,
    (itemView) => itemView.data.completed,
    (itemView, bool) => itemView.setCompleted(bool)
  );

  private filterView = new SegmentControlView([
    { title: 'All', value: 'all' },
    { title: 'Active', value: 'active' },
    { title: 'Completed', value: 'completed' }
  ]);

  private get filterState() {
    return this.filterView.selectedSegment();
  }

  override template() {
    return html`
      <div>
        <div class="header">
          ${this.toggleListController.toggleAllView}
          ${new TextSubmitView({})}
        </div>
        <div class="body">
          ${this.listView}
          <div class="filter">${this.filterView}</div>
        </div>
      </div>
    `;
  }

  @on(TextSubmitted)
  private append({ detail: title }: TextSubmitted) {
    const todo: Todo = { title, completed: false };
    this.data.push(todo); // 전체 Todo[]용 data에 새 Todo 추가
    // 현재 필터가 'completed'로 선택된 경우 화면에 추가하지 않음
    if (this.filterState.value !== 'completed') {
      this.listView.append(todo);
      this.toggleListController.syncToggleAllView();
    }
  }

  @on(Toggled)
  @on(SegmentSelected)
  private refresh() {
    const todos = this.data.filter(todo =>
      this.filterState.value === 'all'
        ? true
        : this.filterState.value === 'completed'
          ? todo.completed
          : !todo.completed,
    );
    this.listView.set(todos);
    this.toggleListController.syncToggleAllView();
  }
}
```

`this.data`는 `TodoPage`의 전체 Todo 목록을 담당하는 배열이다. `[...this.data]` 구문으로 배열을 복사해 `TodoListView`에 새로운 배열을 전달하는 이유는 필터 로직을 일관되게 관리하기 위함이다. `refresh()` 메서드는 `@on(Toggled)`와 `@on(SegmentSelected)` 데코레이터에 의해 토글 이벤트와 필터 변경 이벤트 모두에 반응한다.

### 3.6 휴리스틱 기반 Diff로 DOM 업데이트 최적화

기존에 `ListView`의 `set`은 '항상 전체를 삭제 후 다시 그리는' 로직이었다. 이 방식은 구현이 단순하지만 많은 항목을 재사용할 수 있음에도 매번 DOM 전체를 갈아치우기 때문에 비효율적일 수 있다.

여기서는 간단한 휴리스틱(*Heuristic - 정확한 최적 해를 보장하기보다는 경험적 방법을 통해 '충분히 괜찮은' 해답을 빠르게 찾아내려는 접근 방식*) 로직을 도입한다. 새 목록(`items`)과 이전 목록(`this.data`)을 앞에서부터 비교하여 동일 레퍼런스인 항목은 그대로 두어 재사용하고, 필요 없는 항목만 제거하거나 새 항목만 삽입하는 방식이다.

```typescript
// [코드 7-44] 일부 항목만 업데이트하는 set
abstract class ListView<IV extends View<object>> extends View<IV['data'][]> {
  // ... 생략 ...
  set(items: IV['data'][]): this {
    let i = 0, j = 0;
    // ① 기존 항목들을 빠르게 조회하기 위한 맵
    const oldItemsMap = new Map(
      this.data.map(item => [item, true])
    );
    // ② 앞에서부터 비교
    while (i < this.data.length && j < items.length) {
      const oldItem = this.data[i];
      const newItem = items[j];
      if (oldItem === newItem) {
        // 같은 레퍼런스면 그대로 두고 진행
        i++;
        j++;
        continue;
      }
      // ③ 새 항목(newItem)이 기존에도 있으면(재사용 가능) → 현재 oldItem 제거
      if (oldItemsMap.has(newItem)) {
        this.itemViews[i].element().remove();
        this.itemViews.splice(i, 1);
        this.data.splice(i, 1);
      } else {
        // ④ 기존 항목에 없는 경우 → 새 항목을 삽입
        const oldItemView = this.itemViews[i];
        const newItemView = new this.ItemView(newItem);
        oldItemView.element().before(newItemView.render());
        this.itemViews.splice(i, 0, newItemView);
        this.data.splice(i, 0, newItem);
        i++;
        j++;
      }
    }
    // ⑤ 남은 기존 항목이 있으면 전부 제거
    while (i < this.data.length) {
      this.itemViews[i].element().remove();
      this.itemViews.splice(i, 1);
      this.data.splice(i, 1);
    }
    // ⑥ 남은 새 항목이 있으면 전부 삽입
    while (j < items.length) {
      const newItem = items[j];
      const newItemView = new this.ItemView(newItem);
      this.itemViews.push(newItemView);
      this.element().append(newItemView.render());
      this.data.push(newItem);
      j++;
    }
    return this;
  }
}
```

이 예제는 객체지향 스타일의 상태 관리(`data`, `itemViews`)와 멀티패러다임적 접근법(함수형 코드, 객체지향 클래스, 명령형 코드)을 혼합한 방식이다. `i++`, `j++` 포인터 증가로 배열을 순차 비교하고 필요한 시점에 배열과 DOM을 직접 수정한다.

순수 함수형 접근 방식은 이 같은 상황에서 더 번거로울 수 있다. 배열 인덱싱에는 명령형 스타일이 더 단순할 수 있다. 어떤 문제는 객체지향이 우세하고, 어떤 문제는 함수형이 우세하며, 어떤 문제는 명령형이 우세하고, 또 어떤 문제는 여러 패러다임이 협력하는 것이 우세할 수 있다. 이러한 멀티패러다임적 연습은 개발자에게 뛰어난 문제 해결 능력을 제공한다.

---

## 4. Todo 앱 만들기 3

이번에는 Todo 앱에 상태 패턴(*State Pattern - 객체가 내부 상태에 따라 다른 행동을 보이도록 설계하는 기법*)을 적용하면서 프로그램을 더욱 확장성 있고 유연하게 만드는 방법을 소개한다.

### 4.1 상태 패턴으로 유연하게 만들기

이전에는 `'all'`, `'active'`, `'completed'` 같은 고정된 문자열을 이용해 필터를 분기 처리했다면, 이제는 `FilterState`라는 별도의 상태 객체를 도입한다.

```typescript
// [코드 7-45] 상태 패턴 적용
interface FilterState {
  title: string;
  predicate: (todo: Todo) => boolean;
}

class TodoPage extends View<Todo[]> {
  private listView = new TodoListView([...this.data]);
  private toggleListController = new ToggleListController(
    new CheckView(),
    this.listView,
    (itemView) => itemView.data.completed,
    (itemView, bool) => itemView.setCompleted(bool)
  );

  // ① SegmentControlView 생성자에 filterState[] 전달
  private filterView = new SegmentControlView(
    [
      { title: 'All', predicate: () => true },
      { title: 'Active', predicate: todo => !todo.completed },
      { title: 'Completed', predicate: todo => todo.completed }
    ] as FilterState[]
  );

  // ② addFilterState 메서드 추가
  addFilterState(filterState: FilterState) {
    this.filterView.append(filterState);
  }

  // ③ this.filterView.selectedSegment()의 결과 타입을 자동으로 FilterState로 추론
  private get filterState(): FilterState {
    return this.filterView.selectedSegment();
  }

  override template() {
    return html`
      <div>
        <div class="header">
          ${this.toggleListController.toggleAllView}
          ${new TextSubmitView({})}
        </div>
        <div class="body">
          ${this.listView}
          <div class="filter">${this.filterView}</div>
        </div>
      </div>
    `;
  }

  @on(TextSubmitted)
  private append({ detail: title }: TextSubmitted) {
    const todo: Todo = { title, completed: false };
    this.data.push(todo);
    // ④ if(this.filterState.value !== 'completed')를 아래처럼 변경
    if (this.filterState.predicate(todo)) {
      this.listView.append(todo);
      this.toggleListController.syncToggleAllView();
    }
  }

  @on(Toggled)
  @on(SegmentSelected)
  private refresh() {
    // ⑤ 복잡한 분기 로직을 한 줄로 변경
    const todos = this.data.filter(this.filterState.predicate);
    this.listView.set(todos);
    this.toggleListController.syncToggleAllView();
  }
}
```

핵심 변경 사항:
- `predicate` 함수로 필터 로직을 캡슐화하여 필터 상태가 어떤 텍스트를 가지고 있든 상관없이 실제 동작은 `predicate`가 결정한다.
- `this.data.filter(this.filterState.predicate)` 한 줄로 현재 필터를 반영하므로 필터 개수가 늘어나도 코드가 복잡해지지 않는다.

### 4.2 상태 패턴 적용의 이점

이러한 코드 구조에서는 '필터 상태'를 하나의 객체로 표현하고 해당 객체에 특정 로직(`predicate`)을 담도록 했다.

- **조건 분기 최소화**: 필터 이름을 직접 비교하는 대신 `predicate` 함수로 추상화하여 조건문이 단순해진다.
- **유연한 기획 변경**: 완전히 다른 필터 구성을 적용하거나 특정 필터가 없는 상황으로 수정할 때도 필터 상태 객체를 다르게 구성하기만 하면 된다.
- **코드 확장성**: 필터 로직이 상태 객체 안에 캡슐화되어 있으므로 여러 조건을 추가하거나 다른 필터를 도입해도 코드 충돌이 적고 유지보수가 쉽다.

### 4.3 런타임에서도 변경 가능한 코드와 소프트웨어 동작

상태 패턴을 적용하면 런타임에서도 프로그램의 기능과 동작을 확장할 수 있다.

```typescript
// [코드 7-46] 브라우저 콘솔에서 런타임에 필터 추가
todoPage.addFilterState({
  title: 'ASAP',
  predicate: todo => todo.title.includes('ASAP') && !todo.completed
});
```

브라우저 콘솔에서 이 코드를 입력하면 곧바로 'ASAP' 필터가 `SegmentControlView`에 추가된다. 새로운 필터를 상태 객체(`FilterState`)로 추가하는 것만으로 프로그램 코드를 전혀 수정하지 않고도 기획을 바꾸거나 기능을 늘릴 수 있다.

### 4.4 상태 객체로 더 확장하기

`FilterState`가 기존에는 어떤 조건으로 필터링할지를 결정하는 역할만 맡았다면, 이제는 필터를 포함한 전처리 전체를 담당하도록 확장한다.

```typescript
// [코드 7-47] FilterState 역할 확장
interface FilterState {
  title: string;
  predicate: (todo: Todo) => boolean;
  filter(todos: Todo[]): Todo[];
}

class FilterState {
  constructor(
    public title: string,
    public predicate: (todo: Todo) => boolean
  ) {}

  filter(todos: Todo[]) {
    return todos.filter(this.predicate);
  }
}

const shuffleFilterState: FilterState = {
  title: 'Shuffle',
  predicate: (todo) => !todo.completed,
  filter(todos: Todo[]) {
    return shuffle(todos.filter(this.predicate));
  }
};

function shuffle<T>(array: T[]): T[] {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
}
```

`interface FilterState`는 타입 선언 목적으로 특정 객체가 `title`, `predicate`, `filter`를 가져야 한다는 명세를 나타낸다. `class FilterState`는 실제 구현체다. 이로써 'FilterState를 만족하는 다양한 형태의 객체'를 정의할 수 있게 된다. `shuffleFilterState`는 완료되지 않은 Todo를 무작위로 섞어서 보여주는 특별한 필터다. 이 앱의 사용자는 앱에게 '어떤 일을 먼저 해야 할지 정해 달라'고 요청할 수 있게 된다.

```typescript
// [코드 7-48] 변경된 FilterState 적용
class TodoPage extends View<Todo[]> {
  // ... 생략 ...

  // ① FilterState 생성 방식 변경
  private filterView = new SegmentControlView(
    [
      new FilterState('All', () => true),
      new FilterState('Active', todo => !todo.completed),
      shuffleFilterState, // ② shuffle 기능을 가진 shuffleFilterState
      new FilterState('Completed', todo => todo.completed),
    ] as FilterState[]
  );

  // ... 생략 ...

  @on(TextSubmitted)
  private append({ detail: title }: TextSubmitted) {
    const todo: Todo = { title, completed: false };
    this.data.push(todo);
    // ③ if 문 대신 filter 활용
    this.filterState.filter([todo]).forEach(todo => {
      this.listView.append(todo);
      this.toggleListController.syncToggleAllView();
    });
  }

  @on(Toggled)
  @on(SegmentSelected)
  private refresh() {
    // ④ this.filterState의 filter()를 실행하므로 간결성과 확장성 높임
    const todos = this.filterState.filter(this.data);
    this.listView.set(todos);
    this.toggleListController.syncToggleAllView();
  }
}
```

최종 완성된 `TodoPage`의 코드를 보면 매우 간결하면서도 직관적인 방법으로 Todo 앱을 완성하고 동작시키는 모습을 확인할 수 있다. 각 컴포넌트가 자기 역할에 충실하며 유기적으로 동작한다.

- **TextSubmitView**: 입력창에 할 일을 입력하고 [Enter] 키를 누르면 이벤트를 발생시킨다.
- **SegmentControlView**: 현재 어떤 필터가 선택되었는지를 관리하며 필터를 전환하면 이벤트를 발생시킨다.
- **FilterState**: 어떤 항목을 필터링할지 그리고 어떻게 전처리할지(정렬, 셔플 등) 책임진다.
- **ToggleListController, CheckView**: TodoItemView의 토글, 전체 선택 등 Todo의 완료 여부에 관한 UI 로직을 처리한다.
- **ListView**: TodoListView와 SegmentControlView에서 `append`, `set` 등의 리스트 렌더링에 관한 공통 로직을 처리한다.
- **TodoPage**: 이러한 컴포넌트들을 조립하고 템플릿에 뷰를 배치하며 이벤트 시점에 적절한 메서드를 호출하여 컴포넌트 간 통신을 연결해준다.

이러한 코드 구조는 객체지향 설계의 이점을 잘 살린 예다. 각 클래스는 자기 역할과 책임이 명확하여 수정이나 확장이 필요한 경우 해당 부분만 교체하거나 확장하면 된다.

---

## 5. 비동기와 뷰, Promise와 Class

4.1절에서 Promise를 값으로 다루면서 UI 렌더링 로직을 제어하는 간단한 사례를 살펴봤다. 이번 절에서는 Promise를 UI 컴포넌트 간의 통신에 활용하는 사례를 다룬다.

### 5.1 Promise로 만드는 alert, confirm

다음은 경고 대화 상자(`alert`)를 직접 구현한 예다. 내장 `alert()`는 UI/UX 제약과 확장성 측면에서 한계가 있다. 이를 보완하기 위해 커스텀 `AlertView`를 만든다.

```typescript
// [코드 7-50] alert와 AlertView (Promise 적용 전)
class AlertView extends View<{ message: string }> {
  override template() {
    return html`
      <div>
        <div class="message">${this.data.message}</div>
        <button>확인</button>
      </div>
    `;
  }

  @on('click', 'button')
  private close() {
    this.element().remove();
  }

  static open(message: string) {
    const alertView = new AlertView({ message });
    document.body.append(alertView.render());
  }
}
```

내장 `alert()`는 '사용자가 대화 상자를 닫을 때까지' 스레드를 멈추는 블로킹 동작을 한다. 반면 `AlertView.open`은 사용자가 확인 버튼을 누르기도 전에 이미 이후 코드가 실행된다. Promise를 활용하면 이 문제를 해결할 수 있다.

```typescript
// [코드 7-51] AlertView에 Promise 적용
class AlertView extends View<{ message: string }> {
  private resolve!: () => void;
  readonly promise = new Promise<void>(res => this.resolve = res);

  override template() {
    return html`
      <div>
        <div class="message">${this.data.message}</div>
        <button>확인</button>
      </div>
    `;
  }

  @on('click', 'button')
  private close() {
    this.element().remove();
    this.resolve();
  }

  static open(message: string) {
    const view = new AlertView({ message });
    document.body.append(view.render());
    return view.promise;
  }
}

async function test() {
  alert('완료되었습니다.'); // 확인 버튼을 누를 때까지 아래로 내려가지 않음
  console.log('alert');

  await AlertView.open('완료되었습니다.'); // 확인 버튼을 누를 때까지 아래로 내려가지 않음
  console.log('AlertView');
}
```

`AlertView`는 내부에 `Promise`를 생성하고 `resolve` 함수를 저장해둔다. 사용자가 '확인' 버튼을 클릭하면 `this.resolve()`가 호출되어 Promise가 해결되고, `await` 이후의 코드가 실행된다. 6.2절에서 Promise의 실행 시점을 제어하기 위해 `TaskRunner` 클래스를 만들었던 것처럼, `AlertView` 클래스는 Promise와 `resolve` 함수를 값으로 다루며 UI 렌더링 로직을 제어한다.

### 5.2 값으로서의 Promise, 컴포넌트 간 통신 매개

다음은 확인/취소 버튼이 있는 `confirm()`을 모사한 예다.

```typescript
// [코드 7-52] ConfirmView
class ConfirmView extends View<{ message: string }> {
  private resolve!: (bool: boolean) => void;
  readonly promise = new Promise<boolean>(res => this.resolve = res);

  override template() {
    return html`
      <div>
        <div class="message">${this.data.message}</div>
        <button class="cancel">취소</button>
        <button class="confirm">확인</button>
      </div>
    `;
  }

  @on('click', 'button')
  private close(e: MouseEvent) {
    const button = e.currentTarget as HTMLButtonElement;
    this.element().remove();
    this.resolve(button.matches('.confirm'));
  }

  static open(message: string) {
    const view = new ConfirmView({ message });
    document.body.append(view.render());
    return view.promise;
  }
}

async function test2() {
  if (await ConfirmView.open('삭제하시겠습니까?')) {
    console.log('삭제');
  } else {
    console.log('취소');
  }
}
```

`ConfirmView`는 `test2` 함수와 데이터를 주고받는 예를 보여준다. 사용자가 선택한 버튼(확인/취소)에 따라 비동기적으로 결과를 반환할 수 있고, 이를 통해 두 컴포넌트가 Promise를 매개로 정보(선택 결과)를 교환하는 패턴을 활용한다.

### 5.3 그룹 채팅에 참여할 친구 선택하기

뷰 컴포넌트가 Promise를 통해 상호 간 데이터를 주고받는 패턴은 여러 상황에서 유용하게 활용할 수 있다. 다음은 이 장에서 만든 `ListView`, `CheckView`, `ToggleListController`, `AlertView`, `ConfirmView` 등을 활용해 '그룹 채팅 생성' 화면과 동작을 구현한 예제다.

```typescript
// [코드 7-53] 그룹 채팅 생성
type User = {
  id: number;
  name: string;
};

type Chat = {
  users: User[];
};

class UserItemView extends View<User> {
  override template() {
    return html`<div>${this.data.name}</div>`;
  }
}

class UserListView extends ListView<UserItemView> {
  ItemView = UserItemView;
}

class CheckUserItemView extends View<User> {
  checkView = new CheckView();

  override template() {
    return html`
      <div>
        ${this.checkView}
        ${new UserItemView(this.data)}
      </div>
    `;
  }
}

class CheckUserListView extends ListView<CheckUserItemView> {
  ItemView = CheckUserItemView;
}

class UserPickerView extends View<User[]> {
  private resolve!: (users: User[]) => void;
  readonly promise = new Promise<User[]>(res => this.resolve = res);
  private toggleListController = new ToggleListController(
    new CheckView(),
    new CheckUserListView(this.data),
    (itemView) => itemView.checkView.data.on,
    (itemView, bool) => itemView.checkView.setOn(bool)
  );

  override template() {
    return html`
      <div>
        <div class="header">
          ${this.toggleListController.toggleAllView}
          <h2>친구 선택하기</h2>
          <button class="done">확인</button>
        </div>
        <div class="body">
          ${this.toggleListController.listView}
        </div>
      </div>
    `;
  }

  @on('click', 'button.done')
  private done() {
    this.element().remove();
    this.resolve(
      this.toggleListController
        .listView
        .itemViews
        .filter(({ checkView }) => checkView.data.on)
        .map(({ data }) => data)
    );
  }

  static open() {
    const users: User[] = [
      { id: 1, name: 'Luka' },
      { id: 2, name: 'Stephen' },
      { id: 3, name: 'Nikola' },
      { id: 4, name: 'Kevin' },
    ];
    const view = new UserPickerView(users);
    document.body.append(view.render());
    return view.promise;
  }
}

class ChatCreationView extends View<Chat> {
  private userListView = new UserListView(this.data.users);

  override template() {
    return html`
      <div>
        <button class="pick">대화 상대 선택</button>
        ${this.userListView}
        <button class="create">채팅 시작하기</button>
      </div>
    `;
  }

  @on('click', 'button.pick')
  private async pickUsers() {
    const users = await UserPickerView.open();
    this.userListView.set(users);
  }

  @on('click', 'button.create')
  private async create() {
    if (this.isEmpty()) {
      await AlertView.open('친구들을 선택해주세요.');
    } else {
      if (await ConfirmView.open(this.startMessage)) {
        alert('즐거운 채팅 시작!');
        // new ChatView(this.data)...
      } else {
        this.userListView.set([]);
      }
    }
  }

  isEmpty() {
    return this.data.users.length === 0;
  }

  get startMessage() {
    const names = this.data.users.map(({ name }) => name);
    return `${names.join(', ')} 친구들과 채팅을 시작하겠습니까?`;
  }
}

export function main() {
  document.body.append(
    new ChatCreationView({ users: [] }).render()
  );
}
```

이 간단한 앱은 여러 컴포넌트가 유기적으로 협력한다.

- `UserPickerView`를 통해 사용자(친구)들을 체크박스로 다중 선택할 수 있으며 결과를 Promise로 비동기 반환한다.
- `ChatCreationView`는 선택된 사용자 목록을 실시간으로 업데이트한다.
- 채팅을 시작하기 전에 `AlertView`나 `ConfirmView`를 통해 사용자의 의사를 최종 확인한다.

이러한 로직 전반은 컴포넌트들이 서로 주고받는 비동기 데이터 흐름을 잘 보여준다. UI를 구성하는 여러 개로 분리된 뷰 컴포넌트들과 컨트롤러가 협력하고 Promise를 매개로 통신하는 구조다. 클래스들의 조합, Promise를 통한 비동기 제어, 리스트뷰와 체크박스 컨트롤러가 매끄럽게 어우러져 직관적인 그룹 채팅 생성 화면과 로직을 완성한다.

---

## 요약

- **객체지향 프런트엔드 개발의 가치**: 구글 캘린더, 피그마 같은 고품질 UX 애플리케이션을 만들려면 객체지향 프로그래밍이 필수다. WebAPI는 이미 객체지향적으로 설계되어 있어 이를 활용한 SDK 기반 프로그래밍은 플랫폼에 구애받지 않는 기반 기술이 된다.
- **Headless UI와 추상 클래스**: `ToggleView` 추상 클래스는 토글 상태 관리 로직을 제공하면서 시각적 표현은 하위 클래스에 위임하는 Headless UI 패턴을 보여준다. `SwitchView`와 `CheckView`가 동일한 로직을 공유하면서 서로 다른 UI를 제공한다.
- **커스텀 이벤트와 옵저버 패턴**: DOM의 `addEventListener`/`dispatchEvent`를 활용한 커스텀 이벤트는 컴포넌트 간 느슨한 결합을 실현한다. 이는 GoF의 옵저버 패턴과 자연스럽게 대응된다.
- **제네릭 ListView**: `ListView<IV>` 제네릭 클래스로 리스트 렌더링 로직을 추상화하여 `TodoListView`, `SettingListView`, `SegmentControlView` 등 다양한 리스트 뷰에 재사용할 수 있다.
- **전략 패턴과 콜백 인젝션**: `TogglePageController`는 인터페이스를 통한 전략 패턴을, `ToggleListController`는 콜백 함수를 통한 함수형 접근을 보여준다. 현대 언어에서는 람다 하나로 GoF 패턴을 대체할 수 있다.
- **데코레이터**: `@on('click')`, `@on(Toggled)` 데코레이터는 이벤트 등록 로직을 메서드 선언부 가까이에 두어 가독성을 높인다. 타입 정보를 명시하면 컴파일 타임에 이벤트-핸들러 타입 불일치를 잡아낼 수 있다.
- **상태 패턴**: `FilterState` 객체에 `predicate` 함수를 캡슐화하여 조건 분기를 최소화하고 런타임에도 필터를 동적으로 추가할 수 있는 확장성을 제공한다.
- **Promise를 활용한 컴포넌트 간 통신**: `AlertView`와 `ConfirmView`는 Promise를 값으로 다루며 UI 컴포넌트 간 비동기 데이터 흐름을 구현한다. 내장 `alert()`/`confirm()`의 블로킹 동작을 `await`으로 재현하면서도 UI 확장성을 유지한다.
- **멀티패러다임적 설계**: 객체지향(클래스, 상속, 인터페이스), 함수형(일급 함수, 콜백, 리스트 프로세싱), 명령형(포인터, 직접 DOM 조작)을 상황에 맞게 혼합하면 성능과 생산성을 동시에 확보하며 유지보수와 확장이 한결 쉬워진다.

## 다른 챕터와의 관계

- **5장**: 인터페이스 vs 상속(언어 설계 vs 애플리케이션 레벨)의 논의가 View 상속·ListView 제네릭 추상화로 실현됐다.
- **12장**: "Promise를 값으로"가 AlertView·ConfirmView의 컴포넌트 간 통신 패턴으로 응용됐다.
- **17장**: 이 장의 rune-ts `html`·`View`는 17장에서 만든 템플릿 엔진·View 클래스의 확장판이다.
- **19장**: 상태 패턴의 predicate 캡슐화가 "조건을 값으로 다루기"의 객체지향 판이며, 19장의 패턴 매칭·Result와 대비된다.
