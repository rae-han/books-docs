# Chapter 09: The Iterator and Composite Patterns (반복자 패턴과 컴포지트 패턴)

## 핵심 질문

- 컬렉션이 **배열이든 리스트든 해시맵이든**, 저장 방식을 노출하지 않고 모든 항목을 순회하려면? (반복자)
- 메뉴·서브메뉴·메뉴 항목이 **트리로 중첩**될 때, 개별 항목과 그룹을 **똑같이** 다루려면? (컴포지트)
- "클래스가 바뀌는 이유는 하나뿐이어야 한다"는 단일 책임 원칙은 왜 중요한가?

> **참고**: 이 장은 **반복자**와 **컴포지트** 두 패턴, 그리고 그 사이에 **단일 책임 원칙**을 다룬다.

---

## 1. 문제 — 서로 다른 컬렉션의 합병

팬케이크 하우스(`ArrayList`)와 객체마을 식당(배열)이 합병했다. `MenuItem`은 합의했지만 **저장 방식이 다르다**. "자바 종업원"이 두 메뉴를 출력하려면 순환문을 **각각** 써야 한다.

```typescript
// ❌ 컬렉션 종류마다 다른 순환문 — 메뉴가 늘면 순환문도 는다
for (let i = 0; i < breakfastItems.length; i++) { /* ArrayList용 */ }
for (let i = 0; i < lunchItems.length; i++) { /* 배열용 */ }
```

> **핵심 통찰**: 여기서 바뀌는 부분은 **"반복하는 방법"** 이다. 컬렉션마다 순회 방식이 다르기 때문이다. 이 반복을 캡슐화하면, 종업원은 컬렉션이 무엇인지 몰라도 된다.

---

## 2. 반복자 패턴

`hasNext()`/`next()`를 가진 `Iterator`로 반복을 캡슐화한다. 각 메뉴는 `createIterator()`로 자신에 맞는 반복자를 만들어 준다.

```typescript
interface Iterator<T> {
  hasNext(): boolean;
  next(): T;
}

/** 배열 기반 메뉴용 반복자. */
class DinerMenuIterator implements Iterator<MenuItem> {
  private position = 0;
  constructor(private items: MenuItem[]) {}

  hasNext(): boolean {
    return this.position < this.items.length && this.items[this.position] != null;
  }
  next(): MenuItem {
    return this.items[this.position++];
  }
}

class DinerMenu implements Menu {
  private menuItems: MenuItem[] = [];
  createIterator(): Iterator<MenuItem> {
    return new DinerMenuIterator(this.menuItems);
  }
  // getMenuItems()는 제거 — 내부 구조를 노출하기 때문
}
```

종업원은 **인터페이스(Iterator)만** 알면 되고, 컬렉션 종류마다 순환문을 따로 쓸 필요가 없다.

```typescript
class Waitress {
  constructor(private menus: Menu[]) {}

  printMenu(): void {
    for (const menu of this.menus) {
      this.printMenuItems(menu.createIterator()); // 컬렉션 종류 무관
    }
  }

  private printMenuItems(iterator: Iterator<MenuItem>): void {
    while (iterator.hasNext()) {
      const item = iterator.next();
      console.log(`${item.getName()}, ${item.getPrice()} -- ${item.getDescription()}`);
    }
  }
}
```

<details>
<summary>Java 원본 (DinerMenuIterator)</summary>

```java
public class DinerMenuIterator implements Iterator<MenuItem> {
    MenuItem[] items;
    int position = 0;
    public DinerMenuIterator(MenuItem[] items) {
        this.items = items;
    }
    public MenuItem next() {
        return items[position++];
    }
    public boolean hasNext() {
        return position < items.length && items[position] != null;
    }
}
```
</details>

> **패턴 정의 — 반복자 패턴 (Iterator Pattern)**<br>컬렉션의 구현 방법을 노출하지 않으면서 집합체(aggregate) 내의 모든 항목에 접근하는 방법을 제공한다.

```
       «interface» Aggregate         «interface» Iterator
        createIterator()              hasNext() / next() / remove()
             △                              △
       ConcreteAggregate  ──생성──▶   ConcreteIterator (현재 위치 관리)
```

> **핵심 통찰**: 반복 책임을 **집합체가 아니라 반복자 객체**가 맡는다. 그래서 집합체는 "컬렉션 관리"라는 본연의 일에 집중할 수 있다(→ 다음 절의 단일 책임 원칙).

---

## 3. TS/JS 관점 — 반복자 프로토콜이 언어에 내장

> **핵심 통찰**: 자바스크립트는 **반복자 패턴이 언어 차원에 내장**되어 있다. `Symbol.iterator` 메서드를 구현하면 `for...of`·전개(`...`)·구조분해가 전부 동작한다. `Array`·`Map`·`Set`·`string`이 모두 이 프로토콜을 따른다(자바의 `Iterable`에 해당).

```typescript
class DinerMenu implements Iterable<MenuItem> {
  private items: MenuItem[] = [];

  // 이 하나로 for...of, 전개 연산자 등이 모두 동작한다
  [Symbol.iterator](): Iterator<MenuItem> {
    return this.items[Symbol.iterator]();
  }
}

const menu = new DinerMenu();
for (const item of menu) {          // 저장 방식을 몰라도 순회
  console.log(item.getName());
}
```

**제너레이터**를 쓰면 반복자를 더 간결하게 만들 수 있다(위치 관리를 언어가 대신 해준다).

```typescript
class DinerMenu implements Iterable<MenuItem> {
  private items: MenuItem[] = [];
  *[Symbol.iterator](): Generator<MenuItem> {
    for (const item of this.items) {
      if (item != null) {
        yield item; // yield로 하나씩 내보낸다 — hasNext/next 수동 관리 불필요
      }
    }
  }
}
```

> 자바의 향상된 for(`for (MenuItem m : menu)`)와 JS의 `for...of`는 모두 반복자 프로토콜 위에서 동작한다. **직접 `Iterator` 인터페이스를 만들기보다, 언어가 제공하는 프로토콜을 쓰는 것이 실전**이다(원서도 결국 `java.util.Iterator`로 전환한다).

---

## 4. 단일 책임 원칙 (디자인 원칙 9)

집합체가 "컬렉션 관리"와 "반복" **두 가지**를 다 하면, 바뀔 이유가 두 개가 된다. 그래서 반복을 반복자로 분리한 것이다.

> **디자인 원칙 9 — 단일 책임 원칙 (Single Responsibility Principle)**<br>어떤 클래스가 바뀌는 이유는 하나뿐이어야 한다.

> **핵심 통찰**: 역할(책임)이 둘이면 바뀔 이유가 둘이고, 한 변경이 다른 기능을 망가뜨릴 위험이 커진다. **응집도(cohesion)** — 클래스가 얼마나 한 가지 목적에 집중하는가 — 가 높을수록 관리하기 쉽다.

예: `Game` 클래스가 `login()`·`signup()`·`move()`·`fire()`를 다 가지면 역할이 여럿(세션 관리 + 플레이어 행동)이다 → `GameSession`, `PlayerActions`, `Player`로 쪼갠다.

---

## 5. 컴포지트 패턴

새 요구: 메뉴 안에 **서브메뉴(디저트 메뉴)** 를 넣어야 한다. 이제 "메뉴들의 리스트"만으로는 안 되고, **메뉴·서브메뉴·메뉴 항목이 트리로 중첩**된다. 반복자만으로는 부족하다.

> **패턴 정의 — 컴포지트 패턴 (Composite Pattern)**<br>객체를 트리 구조로 구성해서 부분-전체 계층구조(part-whole hierarchy)를 구현한다. 컴포지트 패턴을 사용하면 클라이언트에서 개별 객체(잎)와 복합 객체(노드)를 **똑같은 방법으로** 다룰 수 있다.

```
           «abstract» MenuComponent
             print() / add() / remove() / getChild() ...
                    △
        ┌───────────┴───────────┐
     MenuItem(잎)            Menu(복합)
      print()               menuComponents: MenuComponent[]
                            print() / add() / remove() / getChild()
```

### 공통 추상 클래스

잎(`MenuItem`)과 복합(`Menu`) 모두 `MenuComponent`를 상속한다. 자기 역할에 안 맞는 메서드는 **기본으로 예외를 던지게** 두고, 필요한 것만 오버라이드한다.

```typescript
abstract class MenuComponent {
  // 복합(Menu)에서만 의미 있는 메서드 — 기본은 예외
  add(_c: MenuComponent): void { throw new Error("지원하지 않음"); }
  remove(_c: MenuComponent): void { throw new Error("지원하지 않음"); }
  getChild(_i: number): MenuComponent { throw new Error("지원하지 않음"); }

  // 잎(MenuItem)에서만 의미 있는 메서드 — 기본은 예외
  getName(): string { throw new Error("지원하지 않음"); }
  getDescription(): string { throw new Error("지원하지 않음"); }
  getPrice(): number { throw new Error("지원하지 않음"); }
  isVegetarian(): boolean { throw new Error("지원하지 않음"); }

  // 둘 다 구현하는 작업 메서드
  print(): void { throw new Error("지원하지 않음"); }
}
```

### 잎 — MenuItem

```typescript
class MenuItem extends MenuComponent {
  constructor(
    private name: string,
    private description: string,
    private vegetarian: boolean,
    private price: number,
  ) { super(); }

  getName(): string { return this.name; }
  getDescription(): string { return this.description; }
  getPrice(): number { return this.price; }
  isVegetarian(): boolean { return this.vegetarian; }

  print(): void {
    console.log(`  ${this.getName()}${this.isVegetarian() ? "(v)" : ""}, ${this.getPrice()}`);
    console.log(`     -- ${this.getDescription()}`);
  }
}
```

### 복합 — Menu (재귀 print)

```typescript
class Menu extends MenuComponent {
  private menuComponents: MenuComponent[] = []; // 잎과 복합을 모두 담는다

  constructor(private name: string, private description: string) { super(); }

  add(c: MenuComponent): void { this.menuComponents.push(c); }
  remove(c: MenuComponent): void {
    const i = this.menuComponents.indexOf(c);
    if (i >= 0) { this.menuComponents.splice(i, 1); }
  }
  getChild(i: number): MenuComponent { return this.menuComponents[i]; }

  getName(): string { return this.name; }
  getDescription(): string { return this.description; }

  print(): void {
    console.log(`\n${this.getName()}, ${this.getDescription()}`);
    console.log("---------------------");
    // 핵심: 자식들에게 print()를 재귀 위임 (자식이 잎이든 복합이든 동일)
    for (const component of this.menuComponents) {
      component.print();
    }
  }
}
```

<details>
<summary>Java 원본 (Menu.print)</summary>

```java
public void print() {
    System.out.print("\n" + getName());
    System.out.println(", " + getDescription());
    System.out.println("---------------------");
    for (MenuComponent menuComponent : menuComponents) {
        menuComponent.print(); // 재귀
    }
}
```
</details>

### 종업원 — 최상위 하나만 알면 끝

```typescript
class Waitress {
  constructor(private allMenus: MenuComponent) {}
  printMenu(): void {
    this.allMenus.print(); // 최상위 print() 한 번 → 전체 트리 재귀 출력
  }
}

// 조립
const allMenus = new Menu("전체 메뉴", "전체 메뉴");
allMenus.add(pancakeHouseMenu);
allMenus.add(dinerMenu);
dinerMenu.add(dessertMenu);       // 메뉴 안에 메뉴(서브메뉴)
dessertMenu.add(new MenuItem("애플 파이", "...", true, 1.59));
```

> **핵심 통찰**: `Menu.print()`가 자식들의 `print()`를 **재귀 호출**하므로, 최상위 `print()` 한 번으로 트리 전체가 출력된다. 클라이언트(종업원)는 **잎인지 복합인지 구분할 필요가 없다** — 이것이 컴포지트의 핵심이다.

---

## 6. 투명성 vs 안전성 — 원칙은 상황에 맞게

> **무엇이든 물어보세요 (Q&A)**
>
> **Q. `MenuComponent`가 "자식 관리"와 "잎 작업" 두 역할을 다 갖잖아요. 단일 책임 원칙 위반 아닌가요?**
> A. 맞다. 컴포지트는 **단일 책임을 희생하고 투명성(transparency)을 얻는** 패턴이다. `add()`·`getChild()`(관리)와 `getPrice()`(잎)를 한 인터페이스에 다 넣어, 클라이언트가 잎과 복합을 **똑같이** 다루게 한다. 대신 잎에 `add()`를 호출하는 등 부적절한 호출이 런타임에야 걸리는 **안전성 저하**가 생긴다.
>
> 역할을 별도 인터페이스로 분리하면 안전해지지만, 클라이언트가 `instanceof`로 타입을 확인해야 해 **투명성이 떨어진다**. 어느 쪽을 택할지는 **디자인 결정**이다 — 원칙은 상황에 맞게 적용한다.

> 패턴 집중 인터뷰 — 컴포지트의 고백<br><br>"저는 GUI(프레임 안에 패널, 패널 안에 버튼…)처럼 **부분-전체 계층**을 다룹니다. 복합 객체에 명령하면 그 안의 모든 자식에게 재귀로 전달되죠. 제 가장 큰 장점은 **클라이언트를 단순하게** 만드는 것 — `if`문 없이 메서드 하나로 전체 구조를 처리합니다. 다만 자식 순서·부모 포인터·캐싱 등 구현 시 고려할 게 많아요."

---

## 연습 문제 (해답 예시)

**1. `printMenu()`의 문제점** — 구상 클래스에 맞춰 코딩(A), 캡슐화 위반(D, 종업원이 저장 방식을 앎), 코드 중복(E, 메뉴마다 순환문). → 반복자로 해결.

**2. `PancakeHouseMenuIterator`** — `ArrayList`는 이미 `iterator()`가 있으므로, `createIterator()`에서 `menuItems.iterator()`를 반환하면 된다(직접 구현 불필요).

**3. 카페 메뉴(HashMap) 추가** — `Menu` 구현, `createIterator()`에서 `menuItems.values().iterator()` 반환(값 컬렉션의 반복자). HashMap은 반복자를 **간접** 지원.

**4. `remove()`를 막고 싶을 때** — `java.util.Iterator`의 `remove()`는 필수 구현이지만, `UnsupportedOperationException`을 던져 비활성화할 수 있다(7장 어댑터의 `Enumeration`과 동일 기법).

---

## 디자인 원칙 정리 (누적)

1. 바뀌는 부분을 캡슐화한다. 2. 인터페이스에 맞춰 프로그래밍한다. 3. 상속보다 구성. 4. 느슨한 결합. 5. OCP. 6. DIP. 7. 최소 지식. 8. 할리우드 원칙.
9. **어떤 클래스가 바뀌는 이유는 하나뿐이어야 한다 (단일 책임 원칙).** ← 이번 장

---

## 요약

- **반복자 패턴**: 컬렉션의 내부 구조를 노출하지 않고 모든 항목을 순회하는 방법을 제공한다. 반복 책임을 **반복자 객체**가 맡아 집합체를 단순하게 만든다.
- TS/JS는 **`Symbol.iterator` 프로토콜과 제너레이터**로 반복자 패턴을 언어 차원에서 지원한다(`for...of`).
- **단일 책임 원칙**: 클래스는 한 가지 역할만 맡아야 하며, 바뀔 이유가 하나여야 한다(높은 응집도).
- **컴포지트 패턴**: 객체를 트리로 구성해 **개별 객체와 복합 객체를 똑같이** 다룬다. 복합 객체는 자식에게 작업을 **재귀 위임**한다.
- 컴포지트는 **투명성을 위해 단일 책임을 희생**한다 — 원칙은 상황에 맞게 적용하는 것이다.

---

## 다른 챕터와의 관계

- **7장 어댑터**: `Enumeration`↔`Iterator` 변환, `remove()` 미지원 처리 등이 이 장과 이어진다.
- **12장 복합 패턴(MVC)**: 컴포지트는 MVC의 뷰(중첩 UI 구성 요소)에서 다시 쓰인다.
- **단일 책임 vs 컴포지트**: 이 장 안에서 원칙(9)과 그 원칙을 의도적으로 어기는 패턴(컴포지트)이 함께 나온다 — "원칙은 규칙이 아니라 지침"의 좋은 예.

---

## 보너스: 원서 복습 요소

### 🧠 뇌 단련 (Brain Power)

1. 반복자 패턴의 클래스 다이어그램은 어떤 패턴과 닮았나? → **팩토리 메서드**(`createIterator()`가 반복자 생성을 서브클래스에 맡김).
2. `Game`·`Person`·`GumballMachine` 중 여러 역할을 맡은 클래스는? → 여러 책임이 섞인 클래스를 찾아 분리 연습.
3. `HashMap`의 `values().iterator()`는 최소 지식 원칙 위반인가? (게터 체이닝 관점에서 논의)

### 🧲 코드 자석 — 요일별 교차 메뉴 반복자

`AlternatingDinerMenuIterator`: `position`을 요일(`Calendar.DAY_OF_WEEK % 2`)로 초기화하고 `position += 2`로 건너뛰어, 홀/짝 요일에 다른 메뉴 항목만 순회한다.

### 🎤 패턴 집중 인터뷰 — 컴포지트 정리

- 부분-전체 계층을 트리로 다루고, 잎/복합을 동일 인터페이스로 처리(투명성).
- 무의미한 메서드는 예외/기본값으로 처리. 자식 순서·부모 포인터·캐싱은 구현 시 고려사항.
- 최대 장점: 클라이언트 단순화(`if`문 없이 전체 구조 처리).

### 📝 낱말 퀴즈 (정답 단어 모음)

9장 용어들(정답은 영어): ITERATOR(반복자), ITERATION(반복 작업), COLLECTION(컬렉션), COMPOSITE(컴포지트), COMPONENTS(구성 요소), LEAF(잎 객체), SINGLERESPONSIBILITY(단일 역할), FACTORYMETHOD(팩토리 메서드), JAVA.UTIL(java.util), HASHMAP(HashMap), ARRAYLIST(ArrayList), WAITRESS(종업원), PANCAKEHOUSE(팬케이크 하우스), CAFE(객체마을 카페), DESSERT(디저트), CHANGE(바뀌는), IMPLEMENTATION(구현).
