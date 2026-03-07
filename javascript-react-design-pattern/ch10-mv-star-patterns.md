# Chapter 10: MV* Patterns (MV* 패턴)

## 핵심 질문

> MVC, MVP, MVVM은 각각 어떤 문제를 해결하며, 현대 프론트엔드 프레임워크는 이 패턴들을 어떻게 변형하여 사용하는가?

---

## 1. MV* 패턴의 역사와 배경

### 분리된 프레젠테이션

MV* 패턴의 근원은 **분리된 프레젠테이션**(*Separated Presentation — 도메인 객체와 프레젠테이션 객체를 명확히 구분하는 설계 원칙*)이라는 개념에 있다. 1970년대에는 GUI라는 것이 거의 존재하지 않았다. 실세계의 아이디어(사진, 사람 등)를 모델링하는 **도메인 객체**와 사용자 화면에 렌더링되는 **프레젠테이션 객체** 사이를 명확하게 구분하기 위한 수단으로 이 개념이 등장했다.

### Smalltalk-80에서의 탄생

MVC 패턴은 트뤼그베 린스카우그(*Trygve Reenskaug*)가 **Smalltalk-80**(1979)에서의 작업 중 처음 설계했으며, 당시에는 **Model-View-Controller-Editor**라고 불렸다. Smalltalk-80에서 구현된 MVC는 분리된 프레젠테이션 개념을 한 단계 더 발전시켜 **애플리케이션의 로직과 UI를 분리하는 것**을 목표로 했다.

이 설계의 핵심 아이디어는 애플리케이션의 일부를 분리함으로써 **모델을 다른 인터페이스에서도 재사용할 수 있다**는 점이었다. MVC는 이후 GoF의 「디자인 패턴」(1995)에서 자세히 설명되어 대중화에 크게 기여했다.

### MV*에서 *의 의미

MVC/MVVM 패턴을 사용하는 대부분의 최신 웹 UI 프레임워크에서는 모델과 뷰 계층을 쉽게 구별할 수 있다. 하지만 **세 번째 구성 요소**의 이름과 기능은 프레임워크마다 다를 수 있다. 따라서 **MV\***에서 **\***는 프레임워크에 따라 다양한 형태로 구현되는 세 번째 구성 요소를 의미한다.

> **핵심 통찰**: MV* 패턴의 본질은 "비즈니스 데이터(모델)와 UI(뷰)를 분리하고, 그 둘을 연결하는 중재자를 두는 것"이다. Controller, Presenter, ViewModel은 모두 이 중재자의 변형이다.

---

## 2. MVC 패턴

MVC(*Model-View-Controller*)는 애플리케이션의 구조를 개선하기 위해 **관심사의 분리**(*Separation of Concerns*)를 활용하는 아키텍처 디자인 패턴이다. 비즈니스 데이터(모델)와 UI(뷰)를 분리하고, 세 번째 구성 요소(컨트롤러)가 로직과 사용자 입력을 관리하는 구조이다.

### 2.1 모델 (Model)

모델은 애플리케이션의 **도메인 관련 데이터**를 관리하는 역할을 한다. UI나 프레젠테이션 계층은 담당하지 않고, 애플리케이션에 필요한 **고유 데이터 형식**을 나타낸다.

| 특성 | 설명 |
|------|------|
| **데이터 관리** | 비즈니스 데이터를 저장하고 관리한다 |
| **관찰자 알림** | 데이터가 변경되면 관찰자(Observer)에게 변경 사항을 알린다 |
| **UI 무관** | 데이터가 브라우저에 어떻게 표현될지에 관여하지 않는다 |
| **유효성 검사** | 데이터의 유효성 검사는 모델에서 수행할 수 있다 |
| **다중 뷰 지원** | 하나의 모델을 여러 뷰가 관찰할 수 있다 |
| **컬렉션 그룹화** | MV* 프레임워크에서는 모델을 컬렉션으로 그룹화하여 관리할 수 있다 |

자바스크립트 애플리케이션에서 '상태(*state*)'라는 용어는 전통적 MVC와 다르게 해석된다. SPA(*Single Page Application — 페이지 전환 없이 동작하는 단일 페이지 웹 애플리케이션*)에서의 상태는 사용자의 화면에 특정 시점에 나타나는 데이터를 의미하며, 이 상태를 시뮬레이션할 필요가 있다. 그러나 모델 자체는 **비즈니스 데이터**와 주로 관련이 있다.

### 2.2 뷰 (View)

뷰는 모델에 대한 **시각적인 표현**으로, 현재 상태의 특정 부분만 보여준다. Smalltalk의 뷰가 비트맵을 생성하고 관리하는 역할이라면, 자바스크립트의 뷰는 여러 **DOM 요소의 집합**을 생성하고 정리하는 역할을 한다.

뷰의 핵심 역할:

- **관찰자 패턴**을 사용해 모델이 변경되거나 수정될 때마다 알아차리고 스스로를 업데이트한다
- 디자인 패턴 관련 자료에서 뷰를 종종 **"둔하다(dumb)"**고 하는데, 뷰는 모델이나 컨트롤러에 대한 정보를 제한적으로 갖기 때문이다
- 사용자가 뷰 내의 요소를 클릭하면, 뷰는 그 다음에 무엇을 해야 할지 모른다. 대신 이 **결정을 컨트롤러에 위임**한다
- 화면에 표시되는 각 섹션 또는 요소에는 언제나 **뷰-컨트롤러 쌍**이 존재한다

최신 자바스크립트 템플릿 솔루션은 ES6의 **태그 템플릿 리터럴**(*Tagged Template Literal*)을 사용하여 동적 HTML을 생성한다. 그러나 템플릿 자체가 뷰는 아니라는 점을 명심해야 한다. 뷰는 모델을 관찰하고 시각적 표현(UI)을 최신 상태로 유지하는 **객체**이며, 템플릿은 뷰 객체의 일부 또는 전체를 **선언적으로 지정**하는 방법일 뿐이다.

### 2.3 컨트롤러 (Controller)

컨트롤러는 모델과 뷰 사이의 **중재자** 역할을 하며, 사용자가 뷰를 조작할 때 모델을 업데이트하는 역할을 한다. 키보드 입력이나 클릭 같은 사용자의 상호작용을 처리하고, 뷰에 무엇을 보여줄지, 사용자 입력을 어떻게 처리할지 등을 결정한다.

### 2.4 TypeScript로 구현하는 MVC

```typescript
// ────────────── Model ──────────────
interface TodoItem {
  id: number;
  text: string;
  completed: boolean;
}

type Subscriber = () => void;

class TodoModel {
  private todos: TodoItem[] = [];
  private subscribers: Subscriber[] = [];
  private nextId = 1;

  subscribe(callback: Subscriber): void {
    this.subscribers.push(callback);
  }

  private notify(): void {
    this.subscribers.forEach((cb) => cb());
  }

  addTodo(text: string): void {
    this.todos.push({ id: this.nextId++, text, completed: false });
    this.notify();
  }

  toggleTodo(id: number): void {
    const todo = this.todos.find((t) => t.id === id);
    if (todo) {
      todo.completed = !todo.completed;
      this.notify();
    }
  }

  removeTodo(id: number): void {
    this.todos = this.todos.filter((t) => t.id !== id);
    this.notify();
  }

  getTodos(): ReadonlyArray<TodoItem> {
    return this.todos;
  }
}

// ────────────── View ──────────────
class TodoView {
  private app: HTMLElement;
  private input: HTMLInputElement;
  private list: HTMLUListElement;

  constructor(rootSelector: string) {
    this.app = document.querySelector(rootSelector)!;
    this.input = document.createElement("input");
    this.input.placeholder = "할 일을 입력하세요";
    this.list = document.createElement("ul");
    this.app.append(this.input, this.list);
  }

  /** 뷰는 컨트롤러에 이벤트 처리를 위임한다 */
  bindAddTodo(handler: (text: string) => void): void {
    this.input.addEventListener("keypress", (e) => {
      if (e.key === "Enter" && this.input.value.trim()) {
        handler(this.input.value.trim());
        this.input.value = "";
      }
    });
  }

  bindToggleTodo(handler: (id: number) => void): void {
    this.list.addEventListener("change", (e) => {
      const target = e.target as HTMLInputElement;
      if (target.type === "checkbox") {
        handler(Number(target.dataset.id));
      }
    });
  }

  bindRemoveTodo(handler: (id: number) => void): void {
    this.list.addEventListener("click", (e) => {
      const target = e.target as HTMLButtonElement;
      if (target.className === "delete") {
        handler(Number(target.dataset.id));
      }
    });
  }

  /** 모델이 변경되면 호출되어 UI를 갱신한다 */
  render(todos: ReadonlyArray<TodoItem>): void {
    this.list.innerHTML = todos
      .map(
        (todo) => `
      <li>
        <input type="checkbox" data-id="${todo.id}"
               ${todo.completed ? "checked" : ""} />
        <span style="${todo.completed ? "text-decoration:line-through" : ""}">
          ${todo.text}
        </span>
        <button class="delete" data-id="${todo.id}">삭제</button>
      </li>`
      )
      .join("");
  }
}

// ────────────── Controller ──────────────
class TodoController {
  constructor(
    private model: TodoModel,
    private view: TodoView
  ) {
    // 뷰의 이벤트를 컨트롤러가 처리하도록 바인딩
    this.view.bindAddTodo((text) => this.model.addTodo(text));
    this.view.bindToggleTodo((id) => this.model.toggleTodo(id));
    this.view.bindRemoveTodo((id) => this.model.removeTodo(id));

    // 모델 변경 시 뷰 업데이트 (Observer 패턴)
    this.model.subscribe(() => {
      this.view.render(this.model.getTodos());
    });
  }
}

// ────────────── 부트스트랩 ──────────────
const model = new TodoModel();
const view = new TodoView("#app");
const controller = new TodoController(model, view);
```

위 예제에서 MVC의 핵심 흐름이 명확하게 드러난다:

1. **사용자 입력** → 뷰가 감지하여 컨트롤러에 위임
2. **컨트롤러** → 모델을 업데이트
3. **모델** → 관찰자(뷰)에게 변경 알림
4. **뷰** → 모델의 최신 데이터로 UI 갱신

### 2.5 MVC를 사용하는 이유

MVC에서의 관심사 분리는 다음과 같은 이점을 제공한다:

- **유지보수 단순화**: 변경 사항이 데이터 중심인지(모델, 컨트롤러) 시각적인지(뷰) 명확하게 구분할 수 있다
- **테스트 용이성**: 비즈니스 로직에 대한 단위 테스트 작성이 훨씬 간편해진다
- **코드 중복 제거**: 하위 수준의 모델 및 컨트롤러 코드 중복이 제거된다
- **동시 개발**: 코어 로직 담당 개발자와 UI 담당 개발자가 동시에 작업할 수 있다

### 2.6 GoF의 관점: MVC = 관찰자 + 전략 + 컴포지트

GoF는 MVC를 독립적인 디자인 패턴이 아닌 **UI를 구축하기 위한 클래스의 집합**으로 간주한다. GoF의 관점에서 MVC는 세 가지 전통적인 디자인 패턴의 변형이다.

| 패턴 | MVC에서의 역할 |
|------|----------------|
| **관찰자(Observer)** | 모델이 변경되면 뷰(관찰자)에게 알림을 보낸다. 일대다(1:N) 관계 정의 |
| **전략(Strategy)** | 뷰가 사용자 입력에 응답할 수 있도록 컨트롤러가 지원한다 |
| **컴포지트(Composite)** | 뷰가 중첩된 하위 뷰로 구성될 수 있다 |

프레임워크에서 MVC가 구현된 방식에 따라 팩토리, 템플릿 패턴도 사용될 수 있다.

> **Osmani의 조언**: 개발자들은 관찰자 패턴(오늘날 대부분 발행자/구독자 패턴으로 변형되어 구현됨)이 수십 년 전에 MVC 아키텍처의 일부로 포함되었다는 사실을 알고 놀라곤 한다. 많은 MVC 관련 글에서 다루지 않는 부분이지만, 모델과 뷰 사이의 관찰자 패턴은 MVC에서 가장 중요한 관계일 것이다.

### 2.7 MVC의 현대적 맥락: 서버 사이드

현대에서 MVC는 **서버 사이드 프레임워크**에서 가장 전통적인 형태로 살아있다.

```typescript
// Express.js에서의 MVC 패턴 예시

// ── Model (Prisma + 도메인 로직) ──
class UserService {
  async findById(id: string): Promise<User | null> {
    return prisma.user.findUnique({ where: { id } });
  }

  async updateProfile(id: string, data: UpdateProfileDto): Promise<User> {
    if (!data.email.includes("@")) {
      throw new ValidationError("유효하지 않은 이메일");
    }
    return prisma.user.update({ where: { id }, data });
  }
}

// ── Controller (라우트 핸들러) ──
class UserController {
  constructor(private userService: UserService) {}

  async getProfile(req: Request, res: Response): Promise<void> {
    const user = await this.userService.findById(req.params.id);
    if (!user) {
      res.status(404).json({ error: "사용자를 찾을 수 없음" });
      return;
    }
    res.json(user); // View: JSON 응답 자체가 뷰 역할
  }
}

// ── NestJS에서의 MVC (더 명확한 계층 분리) ──
@Controller("users")
class NestUserController {
  constructor(private readonly userService: UserService) {}

  @Get(":id")
  async getUser(@Param("id") id: string): Promise<UserResponseDto> {
    return this.userService.findById(id);
  }

  @Put(":id")
  async updateUser(
    @Param("id") id: string,
    @Body() dto: UpdateUserDto
  ): Promise<UserResponseDto> {
    return this.userService.update(id, dto);
  }
}
```

---

## 3. MVP 패턴

MVP(*Model-View-Presenter*)는 **프레젠테이션 로직의 개선**에 초점을 맞춘 MVC의 파생 패턴이다. 1990년대 초반, Taligent(*IBM이 인수한 C++ 프레임워크 회사*)라는 회사가 C++ CommonPoint용 모델을 작업하던 중에 처음 등장했다.

### 3.1 프리젠터 vs 컨트롤러

MVP에서 P는 **프리젠터**(*Presenter*)를 의미한다. 프리젠터는 뷰에 대한 **UI 비즈니스 로직**을 담당하는 구성 요소이다. MVC와의 핵심 차이점은 다음과 같다:

| 관점 | MVC의 Controller | MVP의 Presenter |
|------|-------------------|-----------------|
| **뷰와의 관계** | 뷰가 컨트롤러를 알고 있음 | 프리젠터가 뷰의 인터페이스를 통해 통신 |
| **모델 접근** | 뷰가 모델에 직접 접근 가능 | 뷰는 모델에 직접 접근하지 않음 |
| **데이터 흐름** | 뷰 → 컨트롤러 → 모델 → 뷰(관찰) | 뷰 ↔ 프리젠터 ↔ 모델 |
| **테스트** | 뷰와 컨트롤러가 강하게 결합 | 인터페이스 기반으로 뷰 모킹(*mocking*) 용이 |

### 3.2 수동형 뷰 (Passive View)

MVP에서 가장 널리 사용되는 구현 방식은 **수동형 뷰**(*Passive View*)이다. 수동형 뷰는 로직을 거의 가지고 있지 않으며, 단순히 화면을 출력할 뿐 사용자의 입력 처리를 프리젠터에 완전히 위임한다. 직접적인 데이터 바인딩의 개념이 없고, 대신 뷰는 프리젠터가 데이터를 설정하는 데 사용할 수 있는 **세터(setter)**를 제공한다.

```typescript
// ────────────── View 인터페이스 ──────────────
interface ITodoListView {
  setItems(items: ReadonlyArray<TodoItem>): void;
  getNewItemText(): string;
  clearInput(): void;
  onAddItem(handler: () => void): void;
  onToggleItem(handler: (id: number) => void): void;
  onDeleteItem(handler: (id: number) => void): void;
}

// ────────────── Presenter ──────────────
class TodoListPresenter {
  constructor(
    private view: ITodoListView,
    private model: TodoModel
  ) {
    // 뷰 이벤트 구독
    this.view.onAddItem(() => this.handleAddItem());
    this.view.onToggleItem((id) => this.handleToggleItem(id));
    this.view.onDeleteItem((id) => this.handleDeleteItem(id));

    // 모델 이벤트 구독
    this.model.subscribe(() => this.updateView());
  }

  private handleAddItem(): void {
    const text = this.view.getNewItemText();
    if (text.trim().length > 0) {
      this.model.addTodo(text.trim());
      this.view.clearInput();
    }
  }

  private handleToggleItem(id: number): void {
    this.model.toggleTodo(id);
  }

  private handleDeleteItem(id: number): void {
    this.model.removeTodo(id);
  }

  /** 프리젠터가 뷰를 능동적으로 업데이트한다 */
  private updateView(): void {
    this.view.setItems(this.model.getTodos());
  }
}

// ────────────── 구체적인 View 구현 ──────────────
class TodoListDomView implements ITodoListView {
  private input: HTMLInputElement;
  private list: HTMLUListElement;

  constructor(rootSelector: string) {
    const root = document.querySelector(rootSelector)!;
    this.input = document.createElement("input");
    this.list = document.createElement("ul");
    root.append(this.input, this.list);
  }

  setItems(items: ReadonlyArray<TodoItem>): void {
    this.list.innerHTML = items
      .map(
        (item) =>
          `<li>
            <input type="checkbox" data-id="${item.id}"
                   ${item.completed ? "checked" : ""} />
            ${item.text}
            <button data-id="${item.id}">삭제</button>
          </li>`
      )
      .join("");
  }

  getNewItemText(): string {
    return this.input.value;
  }

  clearInput(): void {
    this.input.value = "";
  }

  onAddItem(handler: () => void): void {
    this.input.addEventListener("keypress", (e) => {
      if (e.key === "Enter") handler();
    });
  }

  onToggleItem(handler: (id: number) => void): void {
    this.list.addEventListener("change", (e) => {
      const target = e.target as HTMLInputElement;
      handler(Number(target.dataset.id));
    });
  }

  onDeleteItem(handler: (id: number) => void): void {
    this.list.addEventListener("click", (e) => {
      const target = e.target as HTMLButtonElement;
      if (target.tagName === "BUTTON") {
        handler(Number(target.dataset.id));
      }
    });
  }
}
```

핵심은 **뷰가 인터페이스(`ITodoListView`)를 구현**한다는 점이다. 테스트 시에는 이 인터페이스를 모킹하여 프리젠터의 로직을 DOM 없이도 완전히 테스트할 수 있다.

### 3.3 감독 컨트롤러 (Supervising Controller)

MVP의 변형인 **감독 컨트롤러**(*Supervising Controller*) 패턴은 마틴 파울러(*Martin Fowler*)가 정리한 것으로, 모델의 데이터를 바로 뷰에 바인딩할 수 있도록 해준다는 점에서 MVC와 MVVM에 더 가깝다:

- **단순한 데이터 표시**: 모델 → 뷰 직접 바인딩
- **복잡한 프레젠테이션 로직**: 프리젠터가 중재

이렇게 두 가지 방식을 혼합하여 사용한다.

### 3.4 MVP의 테스트 이점

MVP 패턴은 **Android 개발**에서 한때 사실상의 표준 아키텍처였다(Google이 MVVM 기반의 Architecture Components를 발표하기 전까지). MVP가 특히 테스트에 유리한 이유는 프리젠터를 **UI의 완전한 모킹**으로 사용하여 다른 구성 요소와 독립적으로 단위 테스트를 할 수 있기 때문이다.

```typescript
// MVP의 테스트 이점 — 프리젠터를 DOM 없이 테스트
class MockTodoView implements ITodoListView {
  public displayedItems: ReadonlyArray<TodoItem> = [];
  public inputText = "테스트 할 일";
  public inputCleared = false;
  private addHandler?: () => void;

  setItems(items: ReadonlyArray<TodoItem>): void {
    this.displayedItems = items;
  }
  getNewItemText(): string {
    return this.inputText;
  }
  clearInput(): void {
    this.inputCleared = true;
  }
  onAddItem(handler: () => void): void {
    this.addHandler = handler;
  }
  onToggleItem(_handler: (id: number) => void): void {}
  onDeleteItem(_handler: (id: number) => void): void {}

  // 테스트에서 직접 호출
  simulateAdd(): void {
    this.addHandler?.();
  }
}

// 테스트
const mockView = new MockTodoView();
const testModel = new TodoModel();
const presenter = new TodoListPresenter(mockView, testModel);

mockView.simulateAdd();
console.assert(mockView.displayedItems.length === 1);
console.assert(mockView.inputCleared === true);
```

### 3.5 MVP vs MVC 선택 기준

MVP는 일반적으로 **프레젠테이션 로직을 최대한 재사용해야 하는 엔터프라이즈 수준의 애플리케이션**에서 사용된다. 뷰가 매우 복잡하고 사용자와의 상호작용이 많은 애플리케이션에서는 MVC가 적합하지 않을 수 있다. 이런 문제를 MVC로 해결하려면 여러 컨트롤러에 크게 의존해야 할 수 있기 때문이다. MVP에서는 이 모든 복잡한 로직을 프리젠터 안에 **캡슐화**할 수 있어 유지보수가 훨씬 간단해진다.

MVP의 뷰는 인터페이스를 통해 정의되므로, 디자이너가 애플리케이션의 레이아웃과 그래픽을 완성하기를 기다리지 않고도 **프레젠테이션 로직을 먼저 작성**할 수 있다.

MVC와 MVP 간의 차이점이 대부분 의미론적인 수준이므로, MVC에 존재하는 근본적인 문제점들은 MVP에도 동일하게 존재할 가능성이 크다. 하지만 모델, 뷰, 컨트롤러(또는 프리젠터)로 관심사를 명확히 분리하기만 한다면, 어떤 패턴을 선택하든 대부분 동일한 장점을 얻을 수 있다.

> **Osmani의 조언**: 전통적인 형태의 MVC나 MVP 패턴을 구현하는 자바스크립트 아키텍처 프레임워크는 거의 없다. 많은 자바스크립트 개발자는 MVC와 MVP를 상호 배타적인 것으로 보지 않는다. 애플리케이션에 프리젠터/뷰 로직을 추가하더라도 여전히 MVC 패턴의 한 종류로 여길 수 있기 때문이다.

---

## 4. MVVM 패턴

MVVM(*Model-View-ViewModel*)은 MVC와 MVP를 기반으로 하는 아키텍처 패턴으로, 애플리케이션의 **UI 개발 부분과 비즈니스 로직, 동작 부분을 명확하게 분리**한다. 많은 MVVM 구현 방식은 **선언적 데이터 바인딩**을 활용하여 뷰에 대한 작업을 다른 계층과 분리할 수 있도록 한다.

### 4.1 역사

MVVM은 마이크로소프트에 의해 **WPF**(*Windows Presentation Foundation*)와 **Silverlight** 용도로 발명되었으며, 2005년에 **존 고스만**(*John Gossman*)의 블로그 글에서 공식적으로 발표되었다.

마이크로소프트가 MVVM이라는 명칭을 채택하기 전에, 커뮤니티 내에서는 MVP에서 **MVPM**(*Model-View-PresentationModel*)으로 발전하려는 움직임이 있었다. 마틴 파울러가 2004년에 쓴 프레젠테이션 모델(*Presentation Model*)에 대한 글이 이 개념의 대중화에 크게 기여했으며, MVVM과 Presentation Model은 사실상 같은 개념에 약간의 차이가 있는 것으로 인식된다.

자바스크립트에서는 초기에 KnockoutJS, Kendo MVVM, Knockback.js 같은 프레임워크로 구현되었고, 이후 **Angular**와 **Vue.js**가 이 패턴을 현대적으로 계승했다.

### 4.2 뷰모델 (ViewModel)

뷰모델(*ViewModel*)은 **데이터 변환기** 역할을 하는 특수한 컨트롤러로 볼 수 있다:

- 모델의 정보를 **뷰가 사용할 수 있는 형태로 변환**한다
- 뷰에서 발생한 **명령(사용자의 조작이나 이벤트)을 모델로 전달**한다
- **뷰의 상태를 유지**하고 뷰에 이벤트를 발생시킨다

예를 들어, UNIX 포맷의 날짜(1333832407)를 가진 모델이 있다면, 모델은 원시 포맷을 그대로 유지하고, 뷰모델이 "2012년 4월 7일 오후 5:00" 형태로 변환하여 뷰에 제공한다. 뷰모델은 뷰라기보다는 **모델에 더 가깝지만**, 동시에 뷰의 **디스플레이 로직 대부분을 처리**한다.

뷰모델은 뷰를 참조할 필요가 없다. 뷰는 뷰모델의 속성을 **바인딩**하여 모델에 포함된 데이터를 뷰에 표현할 수 있다. 이것이 MVP의 프리젠터와의 근본적 차이다.

### 4.3 데이터 바인딩

MVVM의 핵심 메커니즘은 **데이터 바인딩**(*Data Binding*)이다.

| 바인딩 유형 | 방향 | 설명 | 예시 |
|-------------|------|------|------|
| **단방향**(*One-way*) | Model → View | 모델 변경이 뷰에 자동 반영 | React의 상태 → JSX |
| **양방향**(*Two-way*) | Model ↔ View | 뷰의 변경도 모델에 자동 반영 | Angular의 `[(ngModel)]`, Vue의 `v-model` |

뷰와 뷰모델은 데이터 바인딩과 이벤트를 통해 소통한다. 모델과 뷰모델의 속성은 양방향 데이터 바인딩을 통해 동기화되고 업데이트된다.

```typescript
// ────────────── 반응형 ViewModel (MVVM 스타일) ──────────────

type Listener = () => void;

/** 간단한 반응형 상태 — 뷰모델의 속성으로 사용 */
class Observable<T> {
  private listeners: Listener[] = [];

  constructor(private _value: T) {}

  get value(): T {
    return this._value;
  }

  set value(newValue: T) {
    if (this._value !== newValue) {
      this._value = newValue;
      this.listeners.forEach((fn) => fn());
    }
  }

  subscribe(fn: Listener): () => void {
    this.listeners.push(fn);
    return () => {
      this.listeners = this.listeners.filter((l) => l !== fn);
    };
  }
}

// ────────────── Model ──────────────
interface UserProfile {
  firstName: string;
  lastName: string;
  birthTimestamp: number;
}

// ────────────── ViewModel ──────────────
class UserProfileViewModel {
  readonly displayName: Observable<string>;
  readonly formattedBirthDate: Observable<string>;
  readonly email: Observable<string>;
  readonly isValid: Observable<boolean>;

  constructor(private model: UserProfile) {
    this.displayName = new Observable(
      `${model.firstName} ${model.lastName}`
    );
    this.formattedBirthDate = new Observable(
      this.formatDate(model.birthTimestamp)
    );
    this.email = new Observable("");
    this.isValid = new Observable(false);

    // 이메일이 바뀔 때마다 유효성 검사 (양방향 바인딩 효과)
    this.email.subscribe(() => {
      this.isValid.value = this.email.value.includes("@");
    });
  }

  /** 뷰에서 호출하는 커맨드(Command) */
  saveProfile(): void {
    if (this.isValid.value) {
      this.model.firstName = this.displayName.value.split(" ")[0];
      console.log("프로필 저장됨:", this.model);
    }
  }

  private formatDate(timestamp: number): string {
    return new Date(timestamp * 1000).toLocaleDateString("ko-KR");
  }
}

// ────────────── View (선언적 바인딩 시뮬레이션) ──────────────
function bindToDOM(vm: UserProfileViewModel): void {
  const nameEl = document.querySelector("#name")!;
  const emailInput = document.querySelector("#email") as HTMLInputElement;
  const saveBtn = document.querySelector("#save") as HTMLButtonElement;
  const statusEl = document.querySelector("#status")!;

  // 단방향 바인딩: ViewModel → View
  vm.displayName.subscribe(() => {
    nameEl.textContent = vm.displayName.value;
  });
  vm.isValid.subscribe(() => {
    saveBtn.disabled = !vm.isValid.value;
    statusEl.textContent = vm.isValid.value ? "유효" : "이메일을 확인하세요";
  });

  // 양방향 바인딩: View ↔ ViewModel
  emailInput.addEventListener("input", () => {
    vm.email.value = emailInput.value; // View → ViewModel
  });
  vm.email.subscribe(() => {
    emailInput.value = vm.email.value; // ViewModel → View
  });

  // 커맨드 바인딩
  saveBtn.addEventListener("click", () => vm.saveProfile());
}
```

### 4.4 MVVM과 주요 프레임워크

#### Angular: 가장 MVVM에 충실

Angular는 공식적으로 MVVM에 가장 가까운 구조를 제공한다. Component 클래스가 ViewModel, Template이 View, Service가 Model 역할을 한다.

```typescript
// Angular의 MVVM 구조

// ── Model (서비스) ──
@Injectable({ providedIn: "root" })
class UserService {
  private readonly apiUrl = "/api/users";

  getUser(id: string): Observable<User> {
    return this.http.get<User>(`${this.apiUrl}/${id}`);
  }

  updateUser(user: User): Observable<User> {
    return this.http.put<User>(`${this.apiUrl}/${user.id}`, user);
  }

  constructor(private http: HttpClient) {}
}

// ── ViewModel (컴포넌트 클래스) + View (템플릿) ──
@Component({
  selector: "app-user-profile",
  template: `
    <!-- View — 양방향 바인딩 -->
    <input [(ngModel)]="userName" />
    <p>안녕하세요, {{ userName }}님!</p>
    <button (click)="save()" [disabled]="!isValid">저장</button>
  `,
})
class UserProfileComponent implements OnInit {
  userName = "";
  isValid = false;

  constructor(private userService: UserService) {}

  ngOnInit(): void {
    this.userService.getUser("1").subscribe((user) => {
      this.userName = user.name;
    });
  }

  save(): void {
    this.userService
      .updateUser({ id: "1", name: this.userName })
      .subscribe();
  }
}
```

#### Vue.js: MVVM-like

Vue.js는 공식적으로 **뷰모델을 사용하는 MVVM 패턴**이라고 주장한다. Vue 인스턴스/컴포넌트가 뷰모델 역할을 한다. Composition API의 도입으로 구조가 더욱 유연해졌다:

```typescript
// Vue 3 Composition API — ViewModel 역할의 composable
import { ref, computed, watch } from "vue";

function useUserProfile(userId: string) {
  // 반응형 상태 = ViewModel의 Observable 속성
  const firstName = ref("");
  const lastName = ref("");
  const email = ref("");

  // 계산된 속성 = ViewModel의 변환 로직
  const displayName = computed(() => `${firstName.value} ${lastName.value}`);
  const isEmailValid = computed(() => email.value.includes("@"));

  // 부수 효과 감시
  watch(email, (newEmail) => {
    console.log("이메일 변경됨:", newEmail);
  });

  // 커맨드
  async function save(): Promise<void> {
    if (isEmailValid.value) {
      await fetch(`/api/users/${userId}`, {
        method: "PUT",
        body: JSON.stringify({
          firstName: firstName.value,
          lastName: lastName.value,
          email: email.value,
        }),
      });
    }
  }

  return { firstName, lastName, email, displayName, isEmailValid, save };
}
```

```html
<!-- Vue 템플릿 = View — v-model로 양방향 바인딩 -->
<template>
  <input v-model="firstName" />
  <input v-model="lastName" />
  <input v-model="email" />
  <p>{{ displayName }}</p>
  <button @click="save" :disabled="!isEmailValid">저장</button>
</template>
```

| Vue 버전 | 패턴 | 접근 방식 |
|----------|------|-----------|
| **Options API** | 전통 MVVM | `data`, `computed`, `methods`가 ViewModel 역할 |
| **Composition API** | ViewModel-like Hooks | `ref`, `computed`, `watch`로 로직을 composable로 추출 |

#### React: 순수 MVVM은 아니지만 ViewModel-like Hooks

리액트는 **MVC 프레임워크가 아니다**. 리액트는 UI 구축을 위한 자바스크립트 라이브러리이며, 컨트롤러나 라우터 기능이 내장되어 있지 않다. 리액트는 **선언형 프로그래밍** 방식을 따르며, 서버가 브라우저에 '뷰'를 직접 제공하지 않고 '데이터'를 제공한다. 리액트는 이 데이터를 브라우저에서 구문 분석하여 실제 뷰를 생성한다.

다른 관점에서 보면 리액트는 MVC를 기술에 따라 수평적으로 나누는 대신, **관심사에 따라 수직적으로 나눈다**. 리액트의 컴포넌트는 상태(모델), 렌더링(뷰), 제어 흐름 로직(소규모 컨트롤러)을 담고 있는 **작은 수직 분할형 MVC**로 시작했다고 볼 수 있다.

최근에는 많은 컴포넌트 로직이 **커스텀 Hooks**로 추출됨에 따라, Hooks가 ViewModel과 유사한 역할을 수행한다:

```typescript
// React 커스텀 Hook = ViewModel-like 역할
function useUserProfile(userId: string) {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  // 계산된 값 (ViewModel의 변환 로직)
  const displayName = useMemo(
    () => `${firstName} ${lastName}`,
    [firstName, lastName]
  );
  const isEmailValid = useMemo(() => email.includes("@"), [email]);

  // 데이터 페칭 (Model과의 상호작용)
  useEffect(() => {
    fetch(`/api/users/${userId}`)
      .then((res) => res.json())
      .then((user: UserProfile) => {
        setFirstName(user.firstName);
        setLastName(user.lastName);
        setEmail(user.email);
      });
  }, [userId]);

  // 커맨드
  const save = useCallback(async () => {
    if (!isEmailValid) return;
    setIsSaving(true);
    await fetch(`/api/users/${userId}`, {
      method: "PUT",
      body: JSON.stringify({ firstName, lastName, email }),
    });
    setIsSaving(false);
  }, [userId, firstName, lastName, email, isEmailValid]);

  return {
    firstName, setFirstName,
    lastName, setLastName,
    email, setEmail,
    displayName, isEmailValid, isSaving, save,
  };
}

// 컴포넌트 = 순수 View
function UserProfileView({ userId }: { userId: string }) {
  const {
    firstName, setFirstName,
    lastName, setLastName,
    email, setEmail,
    displayName, isEmailValid, isSaving, save,
  } = useUserProfile(userId);

  return (
    <div>
      <input value={firstName} onChange={(e) => setFirstName(e.target.value)} />
      <input value={lastName} onChange={(e) => setLastName(e.target.value)} />
      <input value={email} onChange={(e) => setEmail(e.target.value)} />
      <p>{displayName}</p>
      <button onClick={save} disabled={!isEmailValid || isSaving}>
        {isSaving ? "저장 중..." : "저장"}
      </button>
    </div>
  );
}
```

이 패턴에서 `useUserProfile`은 ViewModel의 역할을 수행한다. 다만 리액트의 데이터 흐름은 MVVM의 양방향 바인딩이 아닌 **단방향 데이터 흐름**(*Unidirectional Data Flow*)을 따른다.

> **Osmani의 조언**: '모델 = 비동기 데이터, 뷰 = 컴포넌트, 컨트롤러 = Hook'으로 이해하는 것도 도움이 될 수 있지만, 단순히 개념 파악을 위한 비유일 뿐 엄밀한 뜻은 아니다.

### 4.5 MVVM의 장단점

**장점:**

- MVVM은 뷰와 이를 구동하는 요소를 **동시에 개발**할 수 있도록 한다
- 뷰를 추상화하여 비즈니스 로직(또는 연결 코드)의 양을 줄인다
- 뷰모델은 이벤트 중심 코드에 비해 **단위 테스트가 더 쉽다**
- 뷰모델은 UI 자동화나 상호작용에 대한 고려 없이도 테스트가 가능하다

**단점:**

- 단순한 UI의 경우 MVVM은 **과도한 구현**(*overkill*)이 될 수 있다
- 데이터 바인딩은 선언적이고 편리하지만, 명령형 코드에 비해 **디버깅이 더 어려울** 수 있다
- 복잡한 애플리케이션에서 데이터 바인딩이 **상당한 관리 부담**을 만들어낼 수 있다
- 대규모 애플리케이션에서 필요한 일반화를 제공하기 위해 뷰모델을 **미리 설계하는 것이 어려울** 수 있다

---

## 5. MV* 패턴 비교 테이블

MVP와 MVVM은 모두 MVC에서 파생된 패턴이다. 핵심 차이점은 각 계층이 다른 계층에 대해 갖는 **의존성**과 서로 얼마나 강하게 연결되어 있는지에 있다.

| 관점 | MVC | MVP | MVVM |
|------|-----|-----|------|
| **세 번째 구성 요소** | Controller | Presenter | ViewModel |
| **데이터 흐름** | 뷰 → 컨트롤러 → 모델 → 뷰(Observer) | 뷰 ↔ 프리젠터 ↔ 모델 | 뷰 ↔ 뷰모델 ↔ 모델 (바인딩) |
| **뷰의 성격** | 모델을 직접 관찰 | 수동적(Passive), 인터페이스 구현 | 능동적, 바인딩 표현식 포함 |
| **뷰-모델 결합** | 뷰가 모델에 직접 접근 가능 | 프리젠터를 통해서만 접근 | 바인딩을 통해 간접 접근 |
| **데이터 바인딩** | 없음 | 없음 (수동 세터) | 선언적 양방향 바인딩 |
| **테스트 용이성** | 보통 | 높음 (인터페이스 모킹) | 높음 (ViewModel 독립 테스트) |
| **복잡도** | 낮음 | 중간 (보일러플레이트 많음) | 중간~높음 (바인딩 인프라 필요) |
| **1:N 관계** | 1 Model : N Views | 1 Presenter : 1 View | 1 ViewModel : 1 View |
| **적합한 프레임워크** | Express, NestJS (서버) | Android (역사적), GWT | Angular, Vue.js, KnockoutJS |

MVC에서는 뷰가 아키텍처의 최상단에 위치하고 그 옆에 컨트롤러가 있다. 모델은 컨트롤러 아래에 있기 때문에, 뷰는 컨트롤러에 대해 알고 있고 컨트롤러는 모델에 대해 알고 있다. 이 구조에서 뷰는 모델에 직접 접근할 수 있지만, 전체 모델을 뷰에 노출하는 것은 보안 및 성능에 문제를 일으킬 수 있다.

MVP에서는 컨트롤러의 역할이 프리젠터로 대체된다. 프리젠터는 뷰와 동일한 계층에 존재하며, 뷰와 모델 양쪽에서 발생하는 이벤트를 수신하고 이들 간의 동작을 조정한다.

MVVM을 사용하면 상태와 로직 정보를 포함할 수 있는 뷰와 관련된 모델 일부를 생성할 수 있다. 이를 통해 **전체 모델을 뷰에 노출하는 것을 피할 수 있다**. 그러나 뷰와 뷰모델 분리의 단점은 둘 사이에 일정 수준의 변환이 필요해 **성능에 영향**을 줄 수 있다는 점이다.

> **핵심 통찰**: MVVM에서 뷰가 추상화되기 때문에 뷰에 필요한 로직의 양이 줄어든다. 그러나 MVC에서는 모델 전체에 바로 접근할 수 있어 변환 조작이 필요하지 않으므로, MVVM 같은 성능 문제가 발생하지 않는다. 각 패턴은 트레이드오프를 가진다.

---

## 6. 현대 프론트엔드에서의 MV*

Backbone, KnockoutJS와 같이 초기 MVC와 MVVM을 구현하는 데 사용되었던 프레임워크들은 더 이상 인기가 없거나 업데이트되지 않는다. 이제는 리액트, Vue.js, 앵귤러, 솔리드(*Solid*) 등이 주로 사용된다.

### 6.1 React: "V in MVC"? 실제로는 단방향 흐름

분명히 말하자면, **리액트는 MVC 프레임워크가 아니다**. 리액트는 서버가 브라우저에 '뷰'를 직접 제공하지 않고 '데이터'를 제공하며, 리액트는 이 데이터를 브라우저에서 구문 분석하여 실제 뷰를 생성한다. Flux 아키텍처에서 영감받은 **단방향 데이터 흐름**이 핵심이다.

```
MVC:   View ←→ Controller ←→ Model (양방향 가능)
Flux:  Action → Dispatcher → Store → View → Action (단방향 순환)
React: State → Render → User Event → setState → Re-render
```

리액트의 컴포넌트를 MV* 관점에서 비유하면:

| 전통적 MVC | 리액트 대응 | 설명 |
|-----------|------------|------|
| **Model** | `useState`, 외부 스토어 | 비동기 데이터, 애플리케이션 상태 |
| **View** | JSX, 컴포넌트의 render | 선언적 UI 표현 |
| **Controller** | Hooks (`useEffect`, 커스텀 Hook) | 사용자 입력 처리, 상태 변경 로직 |

### 6.2 Angular: MVVM-like

Angular는 MV* 패턴 중 MVVM에 가장 가까운 구조를 공식적으로 제공한다:

- **Component 클래스** = ViewModel (상태, 로직, 커맨드)
- **Template** = View (HTML + 바인딩 표현식)
- **Service** = Model (비즈니스 데이터, API 통신)
- **양방향 바인딩** = `[(ngModel)]`

Angular의 Change Detection(*변경 감지 — 컴포넌트 트리를 순회하며 바인딩된 값의 변경을 감지하는 메커니즘*)이 MVVM의 데이터 바인딩 역할을 수행한다.

### 6.3 Vue.js: MVVM에서 Composition으로

Vue.js는 초기부터 MVVM을 공식 표방했으며, Vue 인스턴스가 ViewModel 역할을 담당했다. Vue의 반응형 시스템이 뷰모델 역할을 하며, 템플릿(뷰)과 데이터(모델) 사이의 양방향 데이터 바인딩을 자동으로 처리한다.

Composition API에서 `composable` 함수는 리액트의 커스텀 Hooks와 유사하게 ViewModel 역할을 수행하며, 전통적인 MVVM보다 더 유연한 구조를 제공한다.

### 6.4 Svelte/SolidJS: 컴파일러 기반, 전통 MV* 초월

Svelte와 SolidJS는 **컴파일러 기반 접근 방식**으로 전통적인 MV* 패턴의 경계를 허물었다:

```typescript
// SolidJS — 세밀한 반응성(Fine-grained Reactivity)
import { createSignal, createMemo } from "solid-js";

function UserProfile() {
  const [firstName, setFirstName] = createSignal("홍");
  const [lastName, setLastName] = createSignal("길동");
  const displayName = createMemo(() => `${firstName()} ${lastName()}`);

  return (
    <>
      <input
        value={firstName()}
        onInput={(e) => setFirstName(e.currentTarget.value)}
      />
      <p>{displayName()}</p>
    </>
  );
}
```

이 프레임워크들에서는 MVC/MVP/MVVM이라는 분류 자체가 의미를 잃는다. **컴파일러가 바인딩 인프라를 생성**하고, **세밀한 반응성이 런타임에서 최적의 업데이트**를 수행하므로 별도의 ViewModel이나 Controller 계층이 필요 없다.

### 6.5 Server Components: 서버/클라이언트 경계의 붕괴

React Server Components(RSC)와 Next.js의 App Router는 MV* 패턴의 전제 자체를 흔든다. Next.js가 백엔드 역할을 수행하여 데이터베이스와 상호작용하고 뷰를 사전 렌더링하면, 이후부터는 리액트의 반응형 기능을 통해 뷰를 동적으로 업데이트함으로써 전통적인 MVC 형태로 동작한다.

```typescript
// Server Component — 서버에서 실행, 클라이언트로 HTML 전송
// MVC의 "서버가 뷰를 직접 제공"하는 전통으로 회귀
async function UserProfile({ userId }: { userId: string }) {
  // Model: 서버에서 직접 DB 접근 (API 계층 불필요)
  const user = await db.user.findUnique({ where: { id: userId } });

  return (
    // View: 서버에서 렌더링된 HTML
    <div>
      <h1>{user.name}</h1>
      <p>{user.email}</p>
      {/* 인터랙티브한 부분만 클라이언트 컴포넌트로 분리 */}
      <EditProfileButton userId={userId} />
    </div>
  );
}

// Client Component — 브라우저에서 실행
"use client";
function EditProfileButton({ userId }: { userId: string }) {
  const [isEditing, setIsEditing] = useState(false);
  // ... 인터랙티브 로직
}
```

Server Components에서의 MV* 구조:

- **Model** = 데이터베이스 직접 접근 (서버 컴포넌트 내)
- **View** = 서버에서 렌더링된 HTML + 클라이언트 컴포넌트
- **Controller** = Server Actions (폼 처리, 뮤테이션)

> **핵심 통찰**: Server Components는 전통적인 서버 사이드 MVC(Express, Rails)의 "서버가 뷰를 렌더링"하는 모델과 리액트의 컴포넌트 기반 선언형 모델이 합쳐진 하이브리드 형태이다.

---

## 최신 업데이트 (2026)

원서 출판(2023) 이후 MV* 패턴 관점에서 주목할 만한 변화가 있다.

| 변화 | MV* 관점에서의 의미 |
|------|---------------------|
| **React Server Components 안정화** | 서버/클라이언트 경계가 붕괴되면서 전통적 MVC의 "서버가 뷰를 제공" 모델로 부분 회귀. Model 접근이 서버 컴포넌트 내에서 직접 이루어지므로 별도의 API 계층(Controller)이 불필요해지는 경우가 늘어남 |
| **Signals 확산** | SolidJS, Angular(v16+), Preact, Svelte 5(runes)가 Signals 기반 반응성을 채택. ViewModel의 Observable 속성이 프레임워크 원시 요소로 흡수되어 별도 ViewModel 클래스가 불필요해짐 |
| **Server Actions (React 19)** | `"use server"` 지시어로 서버 함수를 클라이언트에서 직접 호출. MVC의 Controller 역할이 서버 함수로 이동하여 클라이언트 측 Controller/Presenter 계층이 축소됨 |
| **Server-First Architecture** | Astro, Fresh, Remix의 서버 우선 접근법이 확산. SSR/SSG가 기본이 되면서 클라이언트 MV* 패턴의 필요성이 감소하는 추세 |
| **React Compiler** | 자동 메모이제이션으로 `useMemo`, `useCallback` 등 수동 최적화 코드가 불필요해지면서, ViewModel-like Hook의 보일러플레이트가 감소 |
| **HTMX** | 서버 렌더링 MVC로의 회귀. 서버가 HTML 조각을 반환하고 클라이언트가 DOM에 삽입하는 방식으로, 전통적인 MVC에 가장 충실한 현대적 접근 |

> **핵심 통찰**: 2026년 현재, 프론트엔드 아키텍처는 "MV* 패턴을 선택한다"는 프레임보다는 **"서버와 클라이언트의 경계를 어디에 둘 것인가"**라는 프레임으로 이동하고 있다. Signals, Server Components, Server Actions는 전통적인 MV* 계층 분리를 프레임워크 수준에서 자동화하거나 불필요하게 만드는 방향으로 발전하고 있다.

---

## 실무 적용 가이드

### 어떤 패턴을 언제 선택하는가

| 상황 | 권장 접근법 | 이유 |
|------|-------------|------|
| **서버 사이드 API** | MVC (Express, NestJS) | 라우트 → 컨트롤러 → 서비스(모델) 구조가 자연스럽다 |
| **Angular 프로젝트** | MVVM | 프레임워크가 양방향 바인딩과 DI를 기본 제공 |
| **React 프로젝트** | 커스텀 Hooks + 단방향 흐름 | MV* 패턴을 억지로 적용하기보다 Hooks로 관심사를 분리 |
| **Vue.js 프로젝트** | Composition API (MVVM 변형) | composable로 ViewModel 역할을 추출 |
| **복잡한 폼/엔터프라이즈 UI** | MVP (테스트 중시 시) | 인터페이스 기반 뷰 모킹으로 프레젠테이션 로직 테스트 용이 |
| **Next.js App Router** | Server Components + Server Actions | 전통적 MV*보다 서버/클라이언트 경계 기반 설계 |
| **Svelte/SolidJS** | 컴파일러/Signals에 위임 | 별도의 MV* 계층 없이 프레임워크가 반응성 관리 |

### 현대 프레임워크와 MV* 패턴 매핑

| 프레임워크 | 패턴 | Model | View | Controller/* |
|-----------|------|-------|------|--------------|
| **React** | 수직 MVC | `useState`, Zustand, Jotai | JSX 컴포넌트 | Hooks, 이벤트 핸들러 |
| **Vue.js** | MVVM | `reactive()`, Pinia | `<template>` | Vue 인스턴스 (ViewModel) |
| **Angular** | MVVM + DI | Service 클래스 | Component 템플릿 | Component 클래스 + Signals |
| **Next.js** | 서버 MVC | DB/API 레이어 | Client Components | Server Components + Actions |
| **Svelte** | 반응형 | `$state`, 스토어 | 컴포넌트 마크업 | 이벤트 핸들러, `$effect` |
| **HTMX** | 전통 MVC | 서버 DB/ORM | 서버 렌더링 HTML | 서버 라우트 핸들러 |

### 아키텍처 비교: 수평 분리 vs 수직 분리

```
전통 MVC (수평 분리):
┌─────────┐  ┌─────────┐  ┌─────────┐
│  Model   │  │  View   │  │Controller│
│(데이터)  │  │  (UI)   │  │ (로직)  │
└─────────┘  └─────────┘  └─────────┘

React (수직 분리 — 컴포넌트 단위):
┌──────────────────────────────────────┐
│ Component A    Component B           │
│ ┌──────────┐  ┌──────────┐          │
│ │ Hook(VM) │  │ Hook(VM) │          │
│ │ JSX(V)   │  │ JSX(V)   │          │
│ │ State(M) │  │ State(M) │          │
│ └──────────┘  └──────────┘          │
└──────────────────────────────────────┘

Server Components (경계 기반 분리):
┌─── Server ───┐  ┌── Client ──┐
│ DB 접근(M)    │  │ 인터랙션  │
│ HTML 렌더(V)  │  │ 상태 관리  │
│ Actions(C)    │  │ 이벤트    │
└──────────────┘  └────────────┘
```

> **Osmani의 조언**: 새로운 자바스크립트 MV*/프레임워크를 검토할 때는, 한 걸음 물러서서 프레임워크의 아키텍처 접근 방식을 살펴보라. 특히 모델, 뷰, 컨트롤러 등 기타 요소들을 구현하는 방식을 중점적으로 본다면, 프레임워크를 가장 효과적으로 사용하는 방법을 더 잘 이해할 수 있을 것이다.

---

## 요약

- **MV* 패턴**은 비즈니스 데이터(모델)와 UI(뷰)를 분리하고, 이 둘을 연결하는 중재자(\*)를 두는 아키텍처 패턴 계열이다
- **MVC**는 Smalltalk-80에서 탄생하여 관찰자 패턴 기반으로 모델 변경을 뷰에 알리며, GoF는 이를 관찰자 + 전략 + 컴포지트의 조합으로 본다. 현대에서는 주로 서버 사이드(Express, NestJS)에서 전통적 형태로 사용된다
- **MVP**는 프리젠터가 뷰와 모델 사이의 모든 통신을 중재하며, 인터페이스 기반 뷰 모킹을 통한 **테스트 용이성**이 핵심 장점이다. 엔터프라이즈 수준의 복잡한 UI에 적합하다
- **MVVM**은 선언적 데이터 바인딩을 통해 뷰와 뷰모델을 자동으로 동기화하며, Angular와 Vue.js가 이 패턴을 현대적으로 계승했다. 단순 UI에는 과도할 수 있다
- **리액트**는 순수 MVC도 MVVM도 아니며, 단방향 데이터 흐름과 수직 분할(컴포넌트) 기반의 독자적 구조를 따른다. 커스텀 Hooks가 ViewModel과 유사한 역할을 수행하지만 양방향 바인딩이 아닌 명시적 상태 업데이트를 사용한다
- **Svelte/SolidJS**는 컴파일러 기반으로 MV* 분류 자체가 의미를 잃으며, Signals가 ViewModel의 Observable 속성을 프레임워크 원시 요소로 대체한다
- **2026년 현재**, Server Components와 Server Actions로 인해 전통적 MV* 패턴의 경계가 흐려지고 있으며, 아키텍처 논의의 축이 "서버/클라이언트 경계"로 이동하고 있다

---

## 다른 챕터와의 관계

- **← Ch07 (자바스크립트 디자인 패턴)**: MVC의 내부에서 관찰자(Observer), 전략(Strategy), 컴포지트(Composite) 패턴이 사용되며, GoF는 MVC를 이 세 패턴의 조합으로 간주한다
- **← Ch01 (디자인 패턴 소개)**: 공급자 패턴(Provider Pattern)은 MV* 아키텍처에서 모델(상태)을 여러 뷰(컴포넌트)에 전달하는 메커니즘으로 활용된다
- **→ Ch09 (비동기 프로그래밍 패턴)**: 모델의 데이터 페칭, 뷰모델의 비동기 커맨드 처리 등 MV* 패턴의 실제 구현에서 비동기 패턴이 필수적이다
- **→ Ch11 (모듈 패턴)**: MV* 패턴의 각 계층(Model, View, Controller/Presenter/ViewModel)은 모듈로 캡슐화되며, 모듈 시스템이 MV* 구조의 물리적 분리를 지원한다
- **→ Ch12 (리액트 디자인 패턴)**: 리액트에서 MV* 패턴이 어떻게 변형되어 적용되는지, 특히 커스텀 Hooks를 통한 관심사 분리와 컴포넌트 패턴을 구체적으로 다룬다
- **→ Ch15 (렌더링 패턴)**: SSR, SSG, ISR 등 렌더링 패턴은 MV* 아키텍처에서 뷰가 생성되는 위치와 시점을 결정하는 문제와 직결된다
