# Chapter 10: The Liskov Substitution Principle (LSP / 리스코프 치환 원칙)

## 핵심 질문

OCP(*Open-Closed Principle - 개방-폐쇄 원칙*)를 가능하게 하는 일차적인 메커니즘은 추상화(*abstraction - 공통점을 추출해 일반화하는 것*)와 다형성(*polymorphism - 같은 인터페이스로 서로 다른 객체를 다루는 능력*)이다. 정적 타입 언어에서 이를 지원하는 핵심 수단은 상속이다. 그렇다면 상속을 어떻게 써야 OCP가 깨지지 않을까? 좋은 상속 계층의 특징은 무엇이고, 함정은 어디에 있는가? "정사각형은 직사각형이다"라는 자연스러워 보이는 IS-A 관계가 왜 코드에서는 깨지는가?

---

## 1. LSP의 정의

> **리스코프 치환 원칙 (Liskov Substitution Principle)**<br>**서브타입(*subtype - 어떤 타입의 하위 분류로 정의된 새로운 타입*)은 그것의 기반 타입(*base type - 상속의 뿌리가 되는 부모 타입*)으로 치환 가능해야 한다.**

이 원칙은 1988년 바버라 리스코프(*Barbara Liskov - MIT 교수, 2008년 튜링상 수상자*)가 처음 작성했다. 그녀의 원문 정의는 다음과 같다.

> 타입 S의 각 객체 O₁과 타입 T의 각 객체 O₂가 있을 때, T로 프로그램 P를 정의했음에도 불구하고 O₂를 O₁로 치환할 때 P의 행위가 변하지 않으면, S는 T의 서브타입이다.

### 1.1 LSP 위반의 결과

이 원칙의 중요성은 **위반했을 때 무엇이 깨지는지**를 보면 분명해진다.

어떤 함수 `f`가 기반 클래스 `B`의 포인터나 참조값을 인자로 받는다고 하자. 그리고 `B`의 파생 클래스 `D`가 `f`에 넘겨질 때 `f`가 잘못 동작한다고 하자. 그러면 `D`는 LSP를 위반한 것이다.

이때 `f`의 작성자는 어떤 유혹에 빠지게 된다 — `f` 안에 `D`를 식별하는 테스트를 추가해서, `D`가 들어와도 제대로 동작하도록 분기를 만드는 것이다.

```
        ┌──────────────────────────────┐
        │  if (instanceof D) {         │   ◀── OCP 위반: f가 D의 존재를
        │     handleD();               │       알아야 한다
        │  } else if (instanceof E) {  │
        │     handleE();               │
        │  } else {                    │
        │     handleB();               │
        │  }                           │
        └──────────────────────────────┘
```

> **핵심 통찰**: 이런 테스트는 `f`가 `B`의 모든 파생 클래스에 대해 닫혀 있지 않게 만들기 때문에 **OCP를 위반**한다. 즉 **LSP 위반은 잠재적인 OCP 위반**이다. 미숙한 개발자나 서두르는 개발자가 LSP 위반에 대응하기 위해 짜는 이런 코드에서는 늘 악취가 난다.

---

## 2. LSP 위반의 간단한 예 — Shape 계층

### 2.1 RTTI를 강제하는 잘못된 설계

LSP 위반은 종종 런타임 타입 정보(*RTTI - Run-Time Type Information, 실행 시점에 객체의 타입을 식별하는 메커니즘*)의 사용으로 이어진다. 어떤 객체의 타입을 결정하는 데 명시적인 `if` 문이나 `if/else` 사슬이 사용되어 그 타입에 맞는 행위를 선택하게 되는 경우다.

<details>
<summary>원문 C++ 코드 (목록 10-1)</summary>

```cpp
struct Point { double x, y; };

struct Shape {
    enum ShapeType { square, circle } itsType;
    Shape(ShapeType t) : itsType(t) {}
};

struct Circle : public Shape {
    Circle() : Shape(circle) {}
    void Draw() const;
    Point itsCenter;
    double itsRadius;
};

struct Square : public Shape {
    Square() : Shape(square) {}
    void Draw() const;
    Point itsTopLeft;
    double itsSide;
};

void DrawShape(const Shape& s) {
    if (s.itsType == Shape::square)
        static_cast<const Square&>(s).Draw();
    else if (s.itsType == Shape::circle)
        static_cast<const Circle&>(s).Draw();
}
```

</details>

```typescript
// TypeScript - OCP 위반을 유발하는 LSP 위반

interface Point {
    x: number;
    y: number;
}

enum ShapeType {
    Square,
    Circle,
}

class Shape {
    constructor(public itsType: ShapeType) {}
}

class Circle extends Shape {
    itsCenter!: Point;
    itsRadius!: number;

    constructor() {
        super(ShapeType.Circle);
    }

    draw(): void {
        // 원을 그린다
    }
}

class Square extends Shape {
    itsTopLeft!: Point;
    itsSide!: number;

    constructor() {
        super(ShapeType.Square);
    }

    draw(): void {
        // 정사각형을 그린다
    }
}

function drawShape(s: Shape): void {
    if (s.itsType === ShapeType.Square) {
        (s as Square).draw();
    } else if (s.itsType === ShapeType.Circle) {
        (s as Circle).draw();
    }
}
```

### 2.2 무엇이 잘못되었나

`drawShape` 함수는 OCP를 위반한다 — `Shape`의 모든 가능한 파생 클래스를 알아야 하고, `Shape`의 새로운 파생 클래스가 생길 때마다 변경되어야 한다.

이런 코드는 어떻게 만들어졌을까? 책에서는 "엔지니어 조(Joe)"의 사례를 든다. 조는 객체지향을 공부한 후 **다형성의 부하가 지나치게 크다**는 결론에 도달하고, 가상 함수(*virtual function - 파생 클래스에서 오버라이드 가능한 함수*)를 포함하지 않는 `Shape` 클래스를 정의했다. `Square`와 `Circle`은 `Shape`에서 파생되었지만 `Shape`의 함수를 오버라이드하지 않는다.

> **Uncle Bob의 경험**: 그런대로 빠른 컴퓨터에서는 가상 함수 호출 부하가 메서드 호출당 1ns(나노초) 단위가 되므로, 조의 관점을 이해하기는 어렵다. 그러나 이런 식의 "최적화 직감"이 LSP 위반을 만든다.

`Square`와 `Circle`이 `Shape`를 대체할 수 없으므로 `drawShape`는 인자로 받는 `Shape`를 검사하고, 형을 결정하고, 적절한 `Draw` 함수를 호출해야만 한다. **LSP 위반이 OCP 위반을 유발한 것이다.**

---

## 3. 정사각형과 직사각형 — 좀 더 미묘한 위반

LSP를 위반하는 훨씬 미묘한 경우가 있다. 이 예제는 OOP 교육의 고전이다.

### 3.1 출발 — 단순한 Rectangle

<details>
<summary>원문 C++ 코드 (목록 10-2)</summary>

```cpp
class Rectangle {
public:
    void SetWidth(double w)  { itsWidth = w; }
    void SetHeight(double h) { itsHeight = h; }
    double GetHeight() const { return itsHeight; }
    double GetWidth()  const { return itsWidth; }
private:
    Point itsTopLeft;
    double itsWidth;
    double itsHeight;
};
```

</details>

```typescript
// TypeScript
class Rectangle {
    private itsTopLeft: Point = { x: 0, y: 0 };
    private itsWidth: number = 0;
    private itsHeight: number = 0;

    setWidth(w: number): void {
        this.itsWidth = w;
    }

    setHeight(h: number): void {
        this.itsHeight = h;
    }

    getWidth(): number {
        return this.itsWidth;
    }

    getHeight(): number {
        return this.itsHeight;
    }

    area(): number {
        return this.itsWidth * this.itsHeight;
    }
}
```

### 3.2 요구사항 추가 — Square도 처리해야 한다

이 애플리케이션이 잘 동작하고 많은 곳에 설치되었다. 그러던 어느 날, 사용자가 **직사각형은 물론 정사각형도 조작할 수 있게 해달라**고 요구해왔다.

상속은 흔히 **IS-A 관계**라고 불린다. "모든 정사각형은 직사각형이다"이므로, `Square` 클래스는 `Rectangle` 클래스에서 파생되는 것이 합리적으로 보인다.

```
       ┌──────────────┐
       │  Rectangle   │
       │              │
       │ + setWidth() │
       │ + setHeight()│
       │ + area()     │
       └──────┬───────┘
              △
              │ (inherits)
       ┌──────┴───────┐
       │   Square     │
       └──────────────┘
```

### 3.3 첫 번째 문제 — Square는 두 변수가 필요 없다

뭔가 잘못되었다는 첫 번째 증거는 `Square`가 `itsHeight`와 `itsWidth`를 따로 가질 필요가 없다는 사실이다. 그럼에도 `Rectangle`에서 이를 상속받는다 — 소모적이다.

수십만 개의 `Square` 객체를 생성해야 하는 CAD 프로그램이라면 이 낭비는 심각한 문제가 된다. 그러나 잠시 메모리 효율은 무시하자. 더 본질적인 문제가 있다.

### 3.4 두 번째 문제 — setWidth/setHeight의 의미가 깨진다

`Square`는 `setWidth`와 `setHeight`를 상속받는데, **정사각형의 가로와 세로 길이는 같아야 하므로** 이 함수들은 부적절하다.

이 문제를 비껴가는 방법으로 `Square`에서 두 함수를 오버라이드할 수 있다 — 다만 `setWidth`/`setHeight`를 가상 함수로 만들어줘야 한다.

<details>
<summary>원문 C++ 코드 (목록 10-3, 자체 모순 없는 버전)</summary>

```cpp
class Rectangle {
public:
    virtual void SetWidth(double w)  { itsWidth = w; }
    virtual void SetHeight(double h) { itsHeight = h; }
    double GetHeight() const { return itsHeight; }
    double GetWidth()  const { return itsWidth; }
private:
    Point itsTopLeft;
    double itsHeight;
    double itsWidth;
};

class Square : public Rectangle {
public:
    virtual void SetWidth(double w);
    virtual void SetHeight(double h);
};

void Square::SetWidth(double w) {
    Rectangle::SetWidth(w);
    Rectangle::SetHeight(w);
}

void Square::SetHeight(double h) {
    Rectangle::SetHeight(h);
    Rectangle::SetWidth(h);
}
```

</details>

```typescript
// TypeScript - 자체 모순 없는 Rectangle/Square
class Rectangle {
    protected itsWidth: number = 0;
    protected itsHeight: number = 0;

    setWidth(w: number): void {
        this.itsWidth = w;
    }

    setHeight(h: number): void {
        this.itsHeight = h;
    }

    getWidth(): number {
        return this.itsWidth;
    }

    getHeight(): number {
        return this.itsHeight;
    }

    area(): number {
        return this.itsWidth * this.itsHeight;
    }
}

class Square extends Rectangle {
    setWidth(w: number): void {
        super.setWidth(w);
        super.setHeight(w);
    }

    setHeight(h: number): void {
        super.setHeight(h);
        super.setWidth(h);
    }
}
```

이제 `Square` 객체의 가로를 설정하면 세로도 같이 바뀌고, 세로를 설정하면 가로도 같이 바뀐다. 그러므로 `Square`의 불변식(*invariant - 객체의 상태에 관계없이 항상 참이어야 하는 속성*) — "가로 = 세로" — 은 손상되지 않는다.

```typescript
const s = new Square();
s.setWidth(1);    // 가로와 세로 모두 1
s.setHeight(2);   // 가로와 세로 모두 2 — 좋다
```

> **Uncle Bob의 경험**: 파생 클래스를 만드는 것이 기반 클래스의 변경으로 이어질 때(여기서는 `setWidth`/`setHeight`를 `virtual`로 바꾼 일), 대개는 이 설계에 결점이 있음을 의미한다. "`virtual`로 만드는 것을 잊었던 게 설계의 치명적인 결점이었고, 지금 고쳤을 뿐"이라고 논리적으로 반박할 수도 있을 것이다. 그러나 직사각형의 가로와 세로 길이를 설정하는 것은 대단히 기본적인 일이기에 — `Square`의 존재를 예상하지 않았다면 어떤 근거로 이 함수들을 가상으로 만들 수 있었겠는가?

### 3.5 본질적인 문제 — 합리적 가정의 위반

`Square`와 `Rectangle`은 이제 제대로 동작하는 것처럼 보인다. 자체 모순도 없다. 그러나 다음 함수 `g`를 보자.

```typescript
function g(r: Rectangle): void {
    r.setWidth(5);
    r.setHeight(4);
    if (r.area() !== 20) {
        throw new Error("Area should be 20");
    }
}
```

이 함수는 `Rectangle`이라고 믿는 객체의 가로와 세로를 따로 설정한 후, 면적이 5×4=20일 것이라 단언한다. `Rectangle`에 대해서는 더할 나위 없이 잘 동작한다 — 그러나 `Square`를 넘겨받으면 단언 에러가 발생한다.

```typescript
const sq = new Square();
g(sq);   // assertion error: area()는 16
```

본질적인 문제는 `g`의 작성자가 **"`Rectangle`의 가로 길이를 바꾸는 동작이 세로 길이를 바꾸지는 않을 것"**이라고 가정했다는 데 있다. 이것은 너무도 합리적인 가정이다.

그러나 `Rectangle`로서 넘겨질 수 있는 모든 객체가 이 가정을 만족하는 것은 아니다. 그래서 `g`는 `Square`/`Rectangle` 계층 구조에 대해 취약하다.

> **핵심 통찰**: 흥미롭게도, `Square`의 작성자는 `Square`의 불변식을 위반하지 않았다. `Rectangle`에서 `Square`를 파생시킴으로써 **`Rectangle`의 불변식을 위반**하게 된 것이다. 즉 LSP 위반은 파생 클래스의 잘못이 아니라, "이 객체를 그 기반 클래스의 자리에 둘 수 있다"고 선언한 잘못이다.

---

## 4. 유효성은 본래 갖추어진 것이 아니다

LSP는 아주 중요한 결론을 이끈다.

> **핵심 통찰**: 모델만 별개로 보고 그 모델의 유효성을 충분히 검증할 수 없다. 어떤 모델의 유효성(*validity - 설계가 올바른지 여부*)은 오직 **그 고객(client)의 관점에서만** 표현될 수 있다.

`Square`와 `Rectangle` 클래스의 최종 버전을 각각 별개로 검사하면 자체 모순이 없고 유효하다는 결론을 내릴 것이다. 그러나 기반 클래스에 대해 합리적인 가정을 택한 프로그래머의 관점에서 보면, 이 모델은 깨진다.

### 4.1 누가 합리적 가정을 알 수 있는가?

대부분 이런 가정은 예상하기가 쉽지 않다. 사실 이것들을 모두 예상하려고 시도한다면, 시스템을 **불필요한 복잡성의 악취**로 찌들게 하는 결과를 낳을 것이다.

따라서 다른 모든 원칙과 마찬가지로, **관련된 취약성의 악취를 맡을 때까지** 가장 명백한 LSP 위반을 제외한 나머지의 처리는 **연기하는 게 최선이다**.

> **Uncle Bob의 경험**: 종종 기반 클래스를 위해 작성한 단위 테스트(*unit test - 코드의 작은 단위에 대한 자동화 테스트*)에서 이런 합리적 가정 문제가 나타나는 모습을 확인할 수 있다. 이것이 **테스트 주도 개발(TDD)을 해야 하는 또 하나의 훌륭한 이유**다.

---

## 5. IS-A는 행위(behavior)에 대한 것이다

왜 외관상으로는 합리적인 `Square`/`Rectangle`의 모델이 망가졌는가? 결국 `Square`가 `Rectangle`이지 않은가? IS-A 관계가 유지되지 않는 건가?

답은 **"`g`의 작성자를 생각하지 않는 한 그렇다"**이다.

정사각형은 직사각형일 수 있지만, **`g`의 관점에서 볼 때 `Square` 객체는 절대로 `Rectangle` 객체가 아니다.** 왜인가? `Square` 객체의 행위가 `g`가 기대하는 `Rectangle` 객체의 행위와 일치하지 않기 때문이다.

> **핵심 통찰**: 행위 측면에서 볼 때 `Square`는 `Rectangle`이 아니다. 그리고 **행위야말로 소프트웨어의 모든 것이다.** LSP는 OOD에서 IS-A 관계가 합리적으로 가정할 수 있고 클라이언트가 의존하는 **행위와 관련이 있다**는 점을 분명히 한다.

---

## 6. 계약에 의한 설계 (Design by Contract)

많은 개발자가 "합리적 가정"이라는 개념에 불편함을 느낀다 — 고객이 정말로 기대하는 것을 어떻게 알 수 있는가?

이 합리적인 추정을 명시적으로 만들어 LSP를 강제하는 테크닉이 있다. **계약에 의한 설계(*DBC - Design by Contract*)**이며, 버트런드 마이어(*Bertrand Meyer - Eiffel 언어 창시자*)가 자세히 설명했다.

### 6.1 사전조건과 사후조건

DBC를 사용하면 어떤 클래스의 작성자는 그 클래스의 **계약 사항을 명시적으로** 정한다. 각 메서드는 다음을 가진다:

- **사전조건(*precondition - 메서드 실행 전에 참이어야 하는 조건*)**: 메서드를 실행하기 위해 만족되어야 하는 조건
- **사후조건(*postcondition - 메서드 실행 후에 보장되는 조건*)**: 메서드가 완료되고 나서 반드시 참이 되는 조건

예를 들어, `Rectangle.setWidth(w)`의 사후조건은 다음과 같다.

```typescript
// (itsWidth === w) && (itsHeight === old.itsHeight)
// — setWidth 호출 후 itsWidth는 인자값과 같고,
//   itsHeight는 호출 전 값과 같아야 한다
```

### 6.2 마이어의 파생 규칙

> 루틴 재선언(파생 클래스에서)은 오직 **원래 사전조건과 같거나 더 약한 수준**에서 그것을 대체할 수 있고, **원래 사후조건과 같거나 더 강한 수준**에서 그것을 대체할 수 있다.

|  | 기반 클래스 | 파생 클래스 |
|------|-------------|-------------|
| **사전조건** | P_base | P_derived: P_base와 같거나 **더 약함** |
| **사후조건** | Q_base | Q_derived: Q_base와 같거나 **더 강함** |

다시 말해, 기반 클래스의 인터페이스를 통해 객체를 사용할 때 사용자는 그 기반 클래스의 사전조건과 사후조건만 안다. 따라서:

- 파생된 객체는 **기반 클래스가 요구하는 것보다 더 강한 사전조건**을 따를 것이라고 기대할 수 없다 — 즉 파생 객체는 기반 클래스가 받아들이는 것은 모두 받아들여야 한다
- 파생 클래스는 **기반 클래스의 모든 사후조건**을 따라야 한다 — 그 행위와 출력은 기반 클래스의 제약을 위반해서는 안 된다

### 6.3 Square/Rectangle에 적용

`Square.setWidth(w)`의 사후조건은 `Rectangle.setWidth(w)`의 사후조건보다 약하다. `(itsHeight === old.itsHeight)`라는 제약을 **강제하지 않기 때문이다**. 따라서 `Square`의 `setWidth` 메서드는 기반 클래스의 계약을 위반한다.

> "더 약하다"의 의미: 만약 X가 Y의 모든 제약을 강제하지 않는다면 X는 Y보다 약하다. 이것은 X가 강제하는 새로운 제약이 몇 개인지와는 관계가 없다.

### 6.4 언어 차원 지원과 단위 테스트

Eiffel 같은 언어는 사전조건과 사후조건을 직접적으로 지원한다. 그러나 TypeScript, Java, C++에는 이런 기능이 없다. 따라서 이런 언어에서는:

1. 각 메서드의 사전·사후조건을 **수동으로 처리**해야 하고
2. 마이어의 규칙이 위반되지는 않는지 **수동으로 검증**해야 한다
3. **각 메서드의 주석에 사전·사후조건을 문서화**해두면 유용하다
4. **단위 테스트**가 계약을 구체화한다 — 테스트는 클래스의 행위를 분명하게 만들어주며, 클라이언트는 테스트를 보고 "합리적 추정"이 무엇인지 알 수 있다

---

## 7. 실제 예 — PersistentSet

정사각형/직사각형은 인위적인 예처럼 보일 수 있다. Uncle Bob이 실제 프로젝트에서 겪은 사례를 보자.

### 7.1 출발 — Set 추상 인터페이스

1990년대 초, Uncle Bob은 Smalltalk의 `Bag`/`Set`과 유사한 서드파티 컨테이너 라이브러리를 구매했다. 두 종류가 있었다:

| 종류 | 기반 | 특성 |
|------|------|------|
| **BoundedSet** | 배열 | 최대 원소 수 명시. 빠름. 메모리 미리 할당 → 할당 실패 위험 없음. 그러나 메모리 낭비 가능 |
| **UnboundedSet** | 연결 리스트 | 한도 없음. 유연하고 경제적. 그러나 느리고 힙 공간 고갈 위험 |

이 서드파티 클래스들의 인터페이스가 불편하고 나중에 교체할 수도 있기에, Uncle Bob은 자신의 추상 `Set` 인터페이스로 포장(어댑터 패턴)했다.

```
              ┌────────────┐
              │   «abstract»│
              │     Set     │
              │ + add()     │
              │ + delete()  │
              │ + isMember()│
              └──────┬──────┘
                     △
          ┌──────────┴──────────┐
          │                     │
  ┌───────┴───────┐    ┌────────┴───────┐
  │  BoundedSet   │    │  UnboundedSet  │
  └───────┬───────┘    └────────┬───────┘
          │ delegates           │ delegates
          ▼                     ▼
  ┌───────────────┐    ┌────────────────┐
  │ ThirdParty    │    │ ThirdParty     │
  │ BoundedSet    │    │ UnboundedSet   │
  └───────────────┘    └────────────────┘
```

<details>
<summary>원문 C++ 코드 (목록 10-4, 10-5)</summary>

```cpp
template <class T> class Set {
public:
    virtual void Add(const T&)        = 0;
    virtual void Delete(const T&)     = 0;
    virtual bool IsMember(const T&) const = 0;
};

template <class T>
void PrintSet(const Set<T>& s) {
    for (Iterator<T> i(s); i; i++)
        cout << (*i) << endl;
}
```

</details>

```typescript
// TypeScript - 추상 Set 인터페이스
interface Set<T> {
    add(item: T): void;
    delete(item: T): void;
    isMember(item: T): boolean;
    iterator(): Iterator<T>;
}

function printSet<T>(s: Set<T>): void {
    const iter = s.iterator();
    let result = iter.next();
    while (!result.done) {
        console.log(result.value);
        result = iter.next();
    }
}
```

클라이언트는 `Set<T>` 인자만 받으면 되고, 안의 구현이 `BoundedSet`이든 `UnboundedSet`이든 신경 쓰지 않는다. **다형성의 모범적인 사용**이다.

### 7.2 문제 — PersistentSet의 등장

이 계층에 `PersistentSet`(*영속 집합 - 스트림에 쓰이고 다른 애플리케이션에서 다시 읽힐 수 있는 집합*)을 추가하려 한다. 그런데 사용 가능한 서드파티 영속 컨테이너는 **템플릿 클래스가 아니었다**. 대신 추상 기반 클래스 `PersistentObject`에서 파생된 객체만 받아들였다.

```
                       ┌────────────┐
                       │   Set      │
                       └──────┬─────┘
                              △
                              │
                       ┌──────┴─────────┐
                       │ PersistentSet  │
                       └────────┬───────┘
                                │ delegates
                                ▼
                       ┌────────────────────┐
                       │ ThirdParty         │
                       │ PersistentSet      │
                       │ (PersistentObject만│
                       │  받음)             │
                       └────────────────────┘
```

`PersistentSet.add()`는 다음과 같은 구현이 된다.

<details>
<summary>원문 C++ 코드 (목록 10-6)</summary>

```cpp
template <typename T>
void PersistentSet::Add(const T& t) {
    PersistentObject& p = dynamic_cast<PersistentObject&>(t);
    itsThirdPartyPersistentSet.Add(p);
}
```

</details>

```typescript
// TypeScript - LSP 위반의 PersistentSet
class PersistentSet<T> implements Set<T> {
    private thirdParty: ThirdPartyPersistentSet;

    add(item: T): void {
        // PersistentObject가 아니면 런타임 에러!
        if (!(item instanceof PersistentObject)) {
            throw new Error("Item must derive from PersistentObject");
        }
        this.thirdParty.add(item as unknown as PersistentObject);
    }

    delete(item: T): void { /* ... */ }
    isMember(item: T): boolean { /* ... */ }
    iterator(): Iterator<T> { /* ... */ throw new Error(); }
}
```

### 7.3 무엇이 깨졌나

- 추상 `Set<T>`의 클라이언트 중 어느 것도 `add`에서 예외가 발생할 것이라 기대하지 않는다
- 그러나 `PersistentSet`은 `PersistentObject`에서 파생되지 않은 원소가 들어오면 런타임 에러를 던진다
- `Set<T>`의 사전조건이 강해진 것이다 → **LSP 위반**

이 위반의 가장 큰 문제는 **디버깅의 어려움**이다. 실제 논리적 결점은 (1) `PersistentSet`을 어떤 함수에 넘겨주는 의사결정이거나 (2) 비영속 객체를 `PersistentSet`에 추가하는 의사결정인데, 런타임 에러는 그로부터 **수백만 기계 명령어나 떨어진 곳**에서 발생한다.

### 7.4 LSP를 따르지 않은 첫 번째 해결책 — 규정으로 처리

Uncle Bob의 첫 시도는 코드가 아닌 **규정(convention)**이었다.

> **Uncle Bob의 경험**: 나는 `PersistentSet`과 `PersistentObject`가 애플리케이션 전체에 알려지지 않게 한다는 규정을 세웠다. 이들은 단 하나의 모듈에만 알려졌다 — 영속 저장소에서 모든 컨테이너를 읽고 쓰는 책임을 진 모듈이다. 컨테이너를 영속화할 때 그 내용은 `PersistentObject` 파생 객체에 복사되어 `PersistentSet`에 추가되고, 읽을 때는 그 반대로 진행된다.

이 해결책은 효과가 있었을까? **그렇지 않았다.** 규정의 필요성을 이해하지 못한 개발자들이 애플리케이션 일부에서 이를 위반했다. **이것이 바로 규정 기반 해결의 문제다** — 끊임없이 알려야 하고, 동의하지 않거나 모르는 개발자가 위반하면 전체 구조가 손상된다.

### 7.5 LSP를 따르는 해결책 — 계층 분리

Uncle Bob이 지금이라면 어떻게 풀까? **`PersistentSet`이 `Set`과 IS-A 관계가 아니라는 사실을 인정**한다.

그러나 두 클래스가 공통으로 가진 기능 — 멤버 여부 테스트, 순환 등 — 은 있다. LSP 관점에서 문제가 되는 것은 `add` 메서드뿐이다. 그러므로 **상위에 공통 추상 인터페이스를 두고, `Set`과 `PersistentSet`을 형제 관계로** 만든다.

```
                       ┌───────────────┐
                       │   «abstract»  │
                       │   Container   │
                       │ + remove(T)   │
                       │ + isIn(T)     │
                       └───────┬───────┘
                               △
                ┌──────────────┴──────────────┐
                │                             │
        ┌───────┴────────┐           ┌────────┴────────┐
        │      Set       │           │ PersistentSet   │
        │ + add(T)       │           │ + add(T:        │
        │                │           │     Persistent  │
        │                │           │     Object)     │
        └────────────────┘           └─────────────────┘
                                              │ delegates
                                              ▼
                                     ┌─────────────────┐
                                     │ ThirdParty      │
                                     │ PersistentSet   │
                                     └─────────────────┘
```

```typescript
// TypeScript - LSP를 따르는 해결책
interface Container<T> {
    remove(item: T): void;
    isIn(item: T): boolean;
    iterator(): Iterator<T>;
}

interface Set<T> extends Container<T> {
    add(item: T): void;
}

interface PersistentSet extends Container<PersistentObject> {
    add(item: PersistentObject): void;
}
```

이 구조는 `PersistentSet` 객체를 순환 검색할 수 있고 멤버 여부를 테스트할 수 있게 해준다. 그러나 **`PersistentObject`에서 파생되지 않은 객체를 `PersistentSet`에 추가할 수 있는 방법은 (타입 시스템 차원에서) 제공하지 않는다.**

> **핵심 통찰**: LSP 문제의 해결은 종종 **잘못된 IS-A를 끊는 것**으로 시작한다. "당연히 이것은 저것이다"라는 직관이 코드 사용자의 합리적 가정을 깬다면, IS-A는 거짓이다. 형제 관계로 만들거나 공통 인자를 추출하는 것이 정공법이다.

---

## 8. 파생 대신 공통 인자 추출하기 — Line/LineSegment

또 하나의 미묘한 예. `Line`(직선)과 `LineSegment`(선분).

### 8.1 자연스러워 보이는 상속

처음 보면 `LineSegment`는 `Line`의 자연스러운 상속 후보다. 모든 멤버 변수와 멤버 함수를 그대로 가진다. 그저 `getLength`라는 메서드가 추가되고 `isOn`만 오버라이드하면 될 것처럼 보인다.

<details>
<summary>원문 C++ 코드 (목록 10-7, 10-8)</summary>

```cpp
class Line {
public:
    Line(const Point& p1, const Point& p2);
    double GetSlope() const;
    double GetIntercept() const;  // Y절편
    Point GetP1() const { return itsP1; }
    Point GetP2() const { return itsP2; }
    virtual bool IsOn(const Point&) const;
private:
    Point itsP1;
    Point itsP2;
};

class LineSegment : public Line {
public:
    LineSegment(const Point& p1, const Point& p2);
    double GetLength() const;
    virtual bool IsOn(const Point&) const;
};
```

</details>

### 8.2 미묘한 위반

`Line`의 사용자는 직선상에 있는 **모든 점**이 `isOn`에 포함되기를 기대한다. 예를 들어 `getIntercept` 함수가 반환하는 Y절편은 이 직선 위의 점이므로, 사용자는 `line.isOn(line.getIntercept()) === true`라 기대한다.

그러나 `LineSegment`의 많은 인스턴스에서 이 판정은 **실패**한다 — 선분은 무한히 뻗어 있지 않으므로, Y절편이 선분 바깥에 있을 수 있다.

### 8.3 판단의 문제

이 미묘한 결점을 그냥 놔두면 어떨까?

> **핵심 통찰**: 설계를 고쳐서 완벽하게 LSP에 맞는 설계를 만들기보다, 다형적 행위에서 미묘한 결점은 놔두는 것이 좀 더 적절한 대응인 경우도 드물게 있다. 완벽 대신 타협을 받아들이는 것은 **공학적 균형(trade-off)**이다. 그러나 LSP를 가볍게 포기해서는 안 된다 — 기반 클래스가 사용되는 곳에서 서브클래스가 항상 제대로 동작함을 보장하는 것은 복잡성을 다루는 강력한 방법이다.

### 8.4 공통 인자 추출 (Factoring Out Commonality)

`Line`과 `LineSegment` 두 클래스 모두에 접근할 수 있다면, **두 클래스의 공통 원소를 추출하여 추상 기반 클래스**로 만들 수 있다.

```
                ┌────────────────────┐
                │ «abstract»         │
                │ LinearObject       │
                │ + getSlope()       │
                │ + getIntercept()   │
                │ + getP1(), getP2() │
                │ + isOn(): abstract │
                └────────┬───────────┘
                         △
              ┌──────────┼──────────┐
              │          │          │
        ┌─────┴────┐ ┌───┴────┐ ┌───┴───┐
        │   Line   │ │LineSeg │ │  Ray  │
        └──────────┘ └────────┘ └───────┘
```

<details>
<summary>원문 C++ 코드 (목록 10-9, 10-10, 10-11)</summary>

```cpp
class LinearObject {
public:
    LinearObject(const Point& p1, const Point& p2);
    double GetSlope() const;
    double GetIntercept() const;
    Point GetP1() const { return itsP1; }
    Point GetP2() const { return itsP2; }
    virtual bool IsOn(const Point&) const = 0;  // 추상
private:
    Point itsP1;
    Point itsP2;
};

class Line : public LinearObject {
public:
    Line(const Point& p1, const Point& p2);
    virtual bool IsOn(const Point&) const;
};

class LineSegment : public LinearObject {
public:
    LineSegment(const Point& p1, const Point& p2);
    double GetLength() const;
    virtual bool IsOn(const Point&) const;
};
```

</details>

```typescript
// TypeScript - 공통 인자 추출
abstract class LinearObject {
    constructor(
        protected itsP1: Point,
        protected itsP2: Point,
    ) {}

    getSlope(): number {
        return (this.itsP2.y - this.itsP1.y) / (this.itsP2.x - this.itsP1.x);
    }

    getIntercept(): Point {
        // Y절편 계산
        return { x: 0, y: 0 };
    }

    getP1(): Point {
        return this.itsP1;
    }

    getP2(): Point {
        return this.itsP2;
    }

    abstract isOn(p: Point): boolean;
}

class Line extends LinearObject {
    isOn(p: Point): boolean {
        // 무한 직선 위의 점인지 판정
        return true;
    }
}

class LineSegment extends LinearObject {
    getLength(): number {
        return 0;
    }

    isOn(p: Point): boolean {
        // 선분 안에 있는 점인지 판정
        return true;
    }
}

class Ray extends LinearObject {
    isOn(p: Point): boolean {
        // 반직선 위의 점인지 판정
        return true;
    }
}
```

`LinearObject`의 사용자는 자신이 사용하는 객체의 범위(무한 직선/선분/반직선)를 안다고 가정할 수 없다. 그러므로 **아무 문제 없이** `Line`이든 `LineSegment`든 `Ray`든 받아들일 수 있다. 새로운 `Ray` 같은 클래스가 나중에 추가되어도 자연스럽게 어울린다.

> **핵심 통찰**: 워프스-브록(Wirfs-Brock)의 인용 — "어떤 클래스 집합이 모두 같은 책임을 진다면 공통 슈퍼클래스에서 그 책임을 상속받아야 한다. 공통 슈퍼클래스가 아직 존재하지 않는다면 하나 만들어서 공통 책임을 넘겨라. 그러면 언젠가 이 클래스는 분명히 쓸모가 있다."

공통 인자 추출은 많은 양의 코드가 작성되지 않았을 때 가장 적용하기 편한 설계 수단이다. 코드가 많아진 뒤에는 어렵다 — 그래서 **테스트 주도로 점진적으로 키우면서 일찍 발견**하는 것이 중요하다.

---

## 9. 휴리스틱과 규정

LSP 위반의 단서를 보여주는 간단한 휴리스틱(*heuristic - 경험적 규칙*)이 있다.

### 9.1 파생 클래스에서의 퇴화 함수

**기반 클래스에서 어떻게든 기능성을 제거한 파생 클래스**는 보통 그 기반 클래스와 치환이 불가능하다.

<details>
<summary>원문 Java 코드 (목록 10-13)</summary>

```java
public class Base {
    public void f() { /* 일부 코드 */ }
}

public class Derived extends Base {
    public void f() { }  // 퇴화 — 아무것도 하지 않음
}
```

</details>

```typescript
// TypeScript - 파생 클래스에서의 퇴화 함수
class Base {
    f(): void {
        // 일부 코드
    }
}

class Derived extends Base {
    f(): void {
        // 비어 있음 — 퇴화
    }
}
```

`Derived`의 작성자는 `f`가 `Derived`에서는 쓸모없다고 생각했을 것이다. 유감스럽게도 `Base`의 사용자는 `f`를 호출하면 안 된다는 사실을 모르기 때문에, 치환 위반이 생긴다.

> 퇴화 함수가 존재한다고 해서 무조건 LSP 위반은 아니다. 하지만 이것이 일어났을 때 **위반 여부를 살펴볼 만한 가치는 있다**.

### 9.2 파생 클래스에서의 예외 발생

기반 클래스가 발생시키지 않는 예외를 파생 클래스가 발생시키는 것 또한 위반이다.

```typescript
// LSP 위반 — Base는 던지지 않는데 Derived는 던진다
class FileBase {
    write(data: string): void {
        // 정상 동작
    }
}

class ReadOnlyFile extends FileBase {
    write(data: string): void {
        throw new Error("Read-only");  // ← 사용자가 예상하지 않은 예외
    }
}
```

기반 클래스의 사용자가 예외를 기대하지 않는다면, 파생 클래스의 메서드에 예외를 추가했을 때 이들은 치환 가능하지 않다. **사용자의 기대가 변하든지, 아니면 파생 클래스가 그 예외를 발생시키지 않아야 한다.**

---

## 10. 자주 하는 실수

| 안티패턴 | 문제 | 해결 |
|----------|------|------|
| **IS-A 직관에만 의존한 상속** — "정사각형은 직사각형이다" 같은 자연어 IS-A | 코드 사용자의 합리적 가정을 깨면 LSP 위반 | 행위 측면의 IS-A로 다시 검증. 깨지면 형제 관계나 공통 인자 추출 |
| **`instanceof` / RTTI 분기로 LSP 위반 우회** | LSP 위반이 OCP 위반으로 번짐 | 분기를 만들기 전에 계층 자체를 재설계 |
| **사전조건 강화** — 파생 클래스가 기반보다 까다로운 입력만 받음 | 기반 클래스 시그너처에 전달된 객체에 거부됨 | 사전조건은 같거나 더 약하게 |
| **사후조건 약화** — 파생 클래스가 기반의 보장을 지키지 않음 | 클라이언트의 합리적 가정 위반 | 사후조건은 같거나 더 강하게 |
| **퇴화 함수** — 파생에서 메서드를 빈 구현으로 오버라이드 | "이건 부르지 마라"는 암묵 규약은 클라이언트에 전달되지 않음 | 그 메서드가 안 어울리는 게 아닌가? 계층 재설계 검토 |
| **예외 새로 던지기** — 기반은 안 던지는데 파생만 던짐 | 클라이언트가 예외 처리를 준비하지 않음 | 계약을 명시화하든가, 파생이 던지지 않게 만들든가 |
| **규정(convention)으로 위반 봉합** — "이 클래스는 여기서만 쓴다고 약속하자" | 새 개발자가 들어오면 깨짐. 컴파일러가 강제하지 않음 | 타입 시스템·계층 구조로 강제 |
| **이른 LSP 적용** — 모든 합리적 가정을 예측하려 시도 | 시스템에 불필요한 복잡성 | 위반의 악취가 날 때까지 가장 명백한 것만 처리하고 나머지는 미룸 |

---

## 11. 설계 원칙

| 원칙 | 설명 |
|------|------|
| **서브타입은 기반 타입으로 치환 가능해야 한다** | 단순한 한 줄이지만 모든 OOD의 핵심 |
| **IS-A는 행위에 대한 것이다** | "당연히 X는 Y이다"라는 자연어 IS-A에 속지 말 것. 행위가 일치해야 진짜 IS-A |
| **유효성은 클라이언트의 관점에서 정의된다** | 클래스 자체가 모순 없어도, 클라이언트의 합리적 가정을 깨면 잘못된 설계 |
| **사전조건은 약하게, 사후조건은 강하게 (마이어 규칙)** | 파생 클래스가 기반 클래스의 계약을 더 까다롭게 만들지 않도록 |
| **LSP 위반은 OCP 위반을 부른다** | LSP가 깨지면 클라이언트는 `if (instanceof)`를 짜기 시작한다 |
| **명백한 위반만 먼저 처리하고 나머지는 연기하라** | 모든 가정을 미리 예상하면 시스템이 복잡성에 잠긴다 |
| **공통 인자 추출 > 잘못된 파생** | IS-A가 깨지면 형제 관계로 만들고 공통 슈퍼클래스로 추출 |
| **계약은 단위 테스트로 구체화한다** | 언어가 지원하지 않으면 테스트가 사전·사후조건을 표현한다 |

---

## 요약

- **LSP의 정의**: 서브타입은 그것의 기반 타입으로 치환 가능해야 한다 (Barbara Liskov, 1988)
- **LSP 위반은 잠재적인 OCP 위반**이다 — 위반은 `instanceof`/RTTI 분기로 번지면서 클라이언트가 모든 파생을 알아야 하게 만든다
- **간단한 예 (Shape)**: 파생 클래스가 기반의 가상 메서드를 구현하지 않아 `drawShape`가 타입 분기를 강요당한다
- **미묘한 예 (Square/Rectangle)**: 수학적 IS-A는 옳지만 **행위 측면 IS-A는 거짓** — `setWidth`가 세로를 안 바꾼다는 합리적 가정을 `Square`가 깬다
- **유효성은 클라이언트 관점에서만 표현된다** — 클래스 단독으로 모순이 없어도 클라이언트의 가정을 깨면 무효
- **IS-A는 행위에 대한 것이다** — 그리고 **행위야말로 소프트웨어의 모든 것이다**
- **계약에 의한 설계 (DBC, Bertrand Meyer)**: 사전조건과 사후조건으로 계약을 명시화
  - 마이어 규칙: 파생의 사전조건은 같거나 **더 약하게**, 사후조건은 같거나 **더 강하게**
- **언어가 DBC를 지원하지 않으면 단위 테스트가 그 역할**을 한다 — TDD가 LSP를 자연스럽게 강제
- **실제 사례 (PersistentSet)**: 잘못된 IS-A를 끊고 **형제 관계 + 공통 슈퍼클래스**로 재구성
- **공통 인자 추출 (Line/LineSegment → LinearObject)**: IS-A가 어색하면 두 클래스의 공통 부분을 추상 슈퍼클래스로 추출
- **위반 단서 휴리스틱**: (1) 파생 클래스의 퇴화 함수 (2) 파생 클래스가 새로 던지는 예외
- **균형이 필요하다** — 모든 합리적 가정을 미리 예상하려 하면 불필요한 복잡성의 악취가 난다. 명백한 위반만 처리하고 나머지는 위반의 악취가 날 때까지 연기하라
- **서브타입의 진짜 정의는 IS-A가 아니라 "치환 가능성"** — 그리고 치환 가능성은 명시적·암묵적 계약에 의해 정의된다
