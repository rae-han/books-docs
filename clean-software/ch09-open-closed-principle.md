# Chapter 9: The Open-Closed Principle (OCP / 개방-폐쇄 원칙)

## 핵심 질문

소스 코드를 **변경하지 않고도** 모듈의 행위를 **확장**할 수 있을까? 그렇다면 이 모순처럼 보이는 두 속성("확장 가능"과 "변경 불가")을 동시에 만족시키는 메커니즘은 무엇인가? 그리고 — 모든 변경에 대해 폐쇄할 수 없다면, **어떤** 변경에 대해 폐쇄할 것인가?

> 더치도어(*Dutch Door - 수평으로 둘로 나뉘어 각 부분을 열거나 닫은 상태로 놔둘 수 있는 문*)<br>— *The American Heritage® Dictionary of the English Language* (2000)

> 모든 시스템은 생명 주기 동안에 변화한다. 이것은 개발 중인 시스템이 첫 번째 버전보다 오래 남길 원한다면 반드시 염두에 두어야 할 사실이다.<br>— Ivar Jacobson

---

## 1. OCP의 정의

> **개방-폐쇄 원칙 (Open-Closed Principle)**<br>**소프트웨어 개체(클래스, 모듈, 함수 등)는 확장에 대해서는 열려 있어야 하고, 수정에 대해서는 닫혀 있어야 한다.**

버트런드 마이어(*Bertrand Meyer - 1988년 OCP 개념을 처음 제안한 컴퓨터 과학자*)가 1988년 처음 제안한 원칙으로, 변화를 겪으면서도 안정적이고 첫 번째 버전보다 오래 남는 설계를 위한 가이드라인이다.

### 1.1 경직성의 악취

프로그램 한 군데를 변경한 것이 의존적인 모듈에서 단계적인 변경(*cascade of changes - 한 변경이 줄줄이 다른 변경을 유발하는 현상*)을 불러일으킬 때, 그 설계는 **경직성(rigidity)의 악취**를 풍긴다.

OCP는 시스템을 리팩토링하여 나중에 일어날 같은 종류의 변경이 더 이상의 수정을 유발하지 않도록 하라고 권한다. OCP가 잘 적용되면, **이미 제대로 동작하고 있던 원래 코드를 변경하는 것이 아니라 새로운 코드를 덧붙임으로써** 나중에 그런 변경을 할 수 있게 된다.

### 1.2 OCP를 따르는 모듈의 두 가지 속성

1. **확장에 대해 열려 있다 (Open for Extension)**
   - 모듈의 행위가 확장될 수 있다
   - 애플리케이션의 요구 사항이 변경될 때, 새로운 행위를 추가해 모듈을 확장할 수 있다
   - 즉, 모듈이 **하는 일을 변경**할 수 있다

2. **수정에 대해 닫혀 있다 (Closed for Modification)**
   - 모듈의 행위를 확장하는 것이 그 모듈의 **소스 코드나 바이너리 코드의 변경을 초래하지 않는다**
   - 모듈의 실행 가능한 바이너리 형태(링킹 가능한 라이브러리, DLL, Java의 jar 등)는 고스란히 남아 있다

> **핵심 통찰**: 두 속성은 서로 반대 입장에 있는 것처럼 보인다. 어떤 모듈의 행위를 확장하는 보통의 방법은 그 모듈의 소스 코드를 변경하는 것이기 때문이다. 변경할 수 없는 모듈은 보통 고정된 행위를 한다고 여겨진다. **그런데 소스 코드를 변경하지 않고도 모듈의 행위를 바꾸는 일이 어떻게 가능한가?**

---

## 2. 해결책은 추상화다

C++, Java, 또는 다른 OOPL(*Object-Oriented Programming Language - 객체지향 프로그래밍 언어*)에서는 **고정되어 있지만 제한되지 않은** 가능한 행위의 묶음을 표현하는 **추상화(abstraction)**를 만드는 것이 가능하다. 추상화는 추상 기반 클래스(*abstract base class - 인스턴스화할 수 없고 파생 클래스가 구현을 채워야 하는 부모 클래스*)이자, 모든 가능한 파생 클래스를 대표하는 가능한 행위의 제한되지 않은 묶음이다.

모듈은 추상화를 조작할 수 있다.
- 모듈은 **고정된 추상화에 의존**하기 때문에 수정에 대해 닫혀 있을 수 있다
- 모듈의 행위는 추상화의 **새 파생 클래스를 만듦으로써 확장**될 수 있다

### 2.1 OCP를 따르지 않는 설계

```
   ┌─────────┐         ┌─────────┐
   │ Client  │────────▶│ Server  │
   └─────────┘         └─────────┘
   (구체 클래스)       (구체 클래스)
```

`Client`와 `Server` 클래스 모두 구체적이다. `Client`가 다른 서버 객체를 사용하게 하려면, `Client` 클래스가 새로운 서버 클래스를 지정하도록 **변경해야 한다**.

### 2.2 OCP를 따르는 설계 — 스트래터지(Strategy) 패턴

```
   ┌─────────┐         ┌───────────────────┐
   │ Client  │────────▶│  «interface»      │
   └─────────┘         │  ClientInterface  │
                       └─────────┬─────────┘
                                 △
                                 │
                          ┌──────┴──────┐
                          │   Server    │
                          └─────────────┘
```

여기서 `ClientInterface`는 추상 멤버 함수를 포함한 추상 클래스다.
- `Client`는 이 추상화를 사용하지만, 실제로는 파생 `Server` 클래스의 객체를 사용한다
- `Client` 객체가 다른 서버 클래스를 사용하게 하려면, `ClientInterface`의 새 파생 클래스를 만들면 된다
- `Client` 클래스는 **변경되지 않은 채로 남는다**

<details>
<summary>원문 C++/Java 스타일 코드</summary>

```java
// Java
interface ClientInterface {
    void serviceFunction();
}

class Server implements ClientInterface {
    @Override
    public void serviceFunction() {
        // 구현
    }
}

class Client {
    private ClientInterface server;

    public Client(ClientInterface server) {
        this.server = server;
    }

    public void doWork() {
        server.serviceFunction();
    }
}
```

</details>

```typescript
// TypeScript — 스트래터지 패턴
interface ClientInterface {
    serviceFunction(): void;
}

class Server implements ClientInterface {
    serviceFunction(): void {
        // 구현
    }
}

class Client {
    constructor(private readonly server: ClientInterface) {}

    doWork(): void {
        this.server.serviceFunction();
    }
}
```

> **Uncle Bob의 경험**: 왜 `AbstractServer` 대신 `ClientInterface`라는 이름을 지었는지 궁금할 수 있다. **추상 클래스는 자신을 구현하는 클래스보다도 클라이언트에 더 밀접하게 관련되어 있기 때문이다.** 인터페이스의 이름은 그것을 사용하는 쪽의 관점에서 짓는다.

### 2.3 템플릿 메소드(Template Method) 패턴

```
   ┌─────────────────────────┐
   │        Policy           │
   ├─────────────────────────┤
   │ + policyFunction()      │  ◀── 구체 함수
   │ # serviceFunction() = 0 │  ◀── 추상 메소드
   └────────────┬────────────┘
                △
                │
   ┌────────────┴────────────┐
   │    Implementation       │
   ├─────────────────────────┤
   │ # serviceFunction()     │
   └─────────────────────────┘
```

이번에는 **추상 인터페이스가 `Policy` 클래스 자체의 한 부분**이다.
- `Policy`의 구체 함수(`policyFunction`)는 추상 메소드(`serviceFunction`)를 통해 작업을 설명한다
- C++에서는 순수 가상 함수(*pure virtual function - 본문 없는 가상 함수*), Java/TypeScript에서는 추상 메소드
- `Policy` 내부의 행위는 **`Policy`의 새 파생 클래스를 생성**함으로써 확장/수정된다

> **핵심 통찰**: 스트래터지와 템플릿 메소드, 이 두 패턴은 OCP를 따르는 **가장 흔한 수단**이다. 둘 모두 일반적 기능을 구체적 구현으로부터 깔끔하게 분리해낸다.

---

## 3. Shape 애플리케이션 — OCP 위반

표준 GUI에서 원과 사각형을 그릴 수 있는 애플리케이션이 있다. 도형은 특정한 순서에 따라 그려져야 한다.

### 3.1 절차적 (OCP 위반) 해결책

<details>
<summary>원문 C 스타일 코드</summary>

```c
// C — 목록 9-1: 절차적 해결책
enum ShapeType { circle, square };

struct Shape {
    enum ShapeType itsType;
};

struct Circle {
    enum ShapeType itsType;
    double itsRadius;
    Point itsCenter;
};
void DrawCircle(struct Circle*);

struct Square {
    enum ShapeType itsType;
    double itsSide;
    Point itsTopLeft;
};
void DrawSquare(struct Square*);

typedef struct Shape* ShapePointer;

void DrawAllShapes(ShapePointer list[], int n) {
    int i;
    for (i = 0; i < n; i++) {
        struct Shape* s = list[i];
        switch (s->itsType) {
            case square:
                DrawSquare((struct Square*) s);
                break;
            case circle:
                DrawCircle((struct Circle*) s);
                break;
        }
    }
}
```

</details>

```typescript
// TypeScript — 절차적 해결책 (OCP 위반)
enum ShapeType {
    Circle,
    Square,
}

interface Shape {
    itsType: ShapeType;
}

interface Circle extends Shape {
    itsRadius: number;
    itsCenter: Point;
}

interface Square extends Shape {
    itsSide: number;
    itsTopLeft: Point;
}

function drawCircle(c: Circle): void { /* ... */ }
function drawSquare(s: Square): void { /* ... */ }

function drawAllShapes(list: Shape[]): void {
    for (const s of list) {
        switch (s.itsType) {
            case ShapeType.Square: {
                drawSquare(s as Square);
                break;
            }
            case ShapeType.Circle: {
                drawCircle(s as Circle);
                break;
            }
        }
    }
}
```

### 3.2 왜 이 코드가 OCP를 위반하는가?

`drawAllShapes` 함수는 **새로운 도형 종류에 대해 닫혀 있지 않다.** 삼각형을 추가하려면 함수 자체를 수정해야 한다.

| 폐해 | 설명 |
|------|------|
| **경직성** | 삼각형 추가 시 `Shape`, `Square`, `Circle`, `DrawAllShapes` 모두 재컴파일·재배포 |
| **취약성** | switch/case나 if/else 사슬이 애플리케이션 전체에 흩어져 있어, 변경 누락 지점을 찾기 어려움 |
| **부동성** | `DrawAllShapes`를 다른 프로그램에서 재사용하려면 필요 없는 `Square`/`Circle`도 함께 들고 가야 함 |
| **변경의 전염** | `ShapeType` enum 변경이 enum을 저장하는 변수의 **크기 변경**까지 유발 가능 |

> **핵심 통찰**: 실제 현실에서는 이런 switch/case 또는 if/else 사슬이 애플리케이션 전체의 다양한 함수에 흩어져 있다 — 드래그 함수, 늘이기 함수, 옮기는 함수, 지우는 함수 등. **새 도형을 추가하는 일은 이런 패턴을 전부 찾아 각각에 새 도형을 추가하는 것**을 의미한다. 게다가 멋있게 정리된 switch가 아니라, if 조건이 논리 연산자와 결합되거나 case 절이 결합된 어수선한 코드인 경우가 많다.

---

## 4. OCP 따르기 — 다형성 해결책

### 4.1 추상 Shape 클래스

<details>
<summary>원문 C++ 코드</summary>

```cpp
// C++ — 목록 9-2: OOD 해결책
class Shape {
public:
    virtual void Draw() const = 0;
};

class Square : public Shape {
public:
    virtual void Draw() const;
};

class Circle : public Shape {
public:
    virtual void Draw() const;
};

void DrawAllShapes(vector<Shape*>& list) {
    vector<Shape*>::iterator i;
    for (i = list.begin(); i != list.end(); i++) {
        (*i)->Draw();
    }
}
```

</details>

```typescript
// TypeScript — OCP를 따르는 해결책
abstract class Shape {
    abstract draw(): void;
}

class Square extends Shape {
    draw(): void {
        // 사각형 그리기
    }
}

class Circle extends Shape {
    draw(): void {
        // 원 그리기
    }
}

function drawAllShapes(list: Shape[]): void {
    for (const shape of list) {
        shape.draw();
    }
}
```

### 4.2 무엇이 좋아졌는가?

- **새 도형 추가 = `Shape`의 새 파생 클래스 생성만**으로 끝난다
- `drawAllShapes`는 변경할 필요가 없다 → **OCP를 따른다**
- `Triangle` 클래스 추가는 여기 보인 어떤 모듈에도 영향을 주지 않는다
- 재빌드되어야 하는 바이너리 모듈은 **`Shape`의 새 파생 클래스의 인스턴스를 실제로 생성하는 모듈** 하나뿐이다 (보통 `main` 또는 팩토리)
- `DrawAllShapes`는 `Square`/`Circle`의 편승 없이 재사용 가능 → **부동성 없음**

---

## 5. "그래, 거짓말했다" — 완벽한 폐쇄는 없다

이전 예제는 사실 **터무니없는 소리**였다. 다음 상황을 보자.

> 모든 `Circle`이 모든 `Square` 앞에 그려지도록 정책이 바뀐다면?

`drawAllShapes`는 이런 변경에 대해 **닫혀 있지 않다**. 이를 구현하려면 함수에 들어가 `Circle`을 먼저 검색하고, 그다음 `Square`를 검색해야 한다.

### 5.1 자연스러운 모델은 없다

이전 추상화(`Shape` → `Square`/`Circle`)는 **이 종류의 변경에는 도움이 되기보다 장애가 됐다.** 놀랍게 들릴 수 있다 — 그밖에 어떤 것이 `Shape` 기반 클래스보다 더 자연스러울 수 있겠는가?

답은 이렇다 — **순서가 도형 종류보다 더 중요한 시스템에서는 이 모델이 자연스럽지 않다.**

> **핵심 통찰**: 일반적으로, 모듈이 얼마나 닫혀 있든 간에 **닫혀 있지 않은 것에 대한 변경은 항상 존재한다**. 모든 상황에서 자연스러운 모델은 없다. 폐쇄는 완벽할 수 없기 때문에 **전략적**이어야 한다.

### 5.2 전략적 폐쇄 (Strategic Closure)

설계자는 자신의 설계에서 **닫혀 있을 변경의 종류를 선택**해야 한다.

1. 가장 그럴법한 종류의 변경을 추측한다
2. 그 변경에 대해 보호할 수 있는 추상화를 작성한다

경험으로 얻은 통찰력이 필요하다. 옳은 추측을 하면 이기고, 잘못된 추측을 하면 진다. 그리고 **분명히 많은 부분을 잘못 추측하게 될 것이다**.

또한 OCP를 따르는 데에는 비용이 든다:
- 적절한 추상화를 만드는 데 개발 시간과 노력
- 추상화는 소프트웨어 설계의 **복잡성을 높임**
- 개발자가 감당할 수 있는 추상화 정도에 한계가 있음

따라서 OCP의 응용은 **있을 법한 변경 정도로 제한**해야 한다.

---

## 6. "올가미" 놓기 — 휴리스틱

### 6.1 과거의 격언 vs 현재의 휴리스틱

| 시대 | 접근 방식 | 결과 |
|------|-----------|------|
| **이전 세기** | 일어날 수 있다고 생각되는 모든 변경에 대해 미리 "올가미"를 놓는다 | 종종 틀린 추측 + 사용되지 않는데 유지보수되는 **불필요한 복잡성의 악취** |
| **현재** | 추상화가 **실제로 필요할 때까지** 기다렸다가 올가미를 놓는다 | 첫 번째 총알은 맞되, 같은 총에서 쏘는 다른 총알에는 확실히 보호 |

### 6.2 "Fool me once" 휴리스틱

> 한 번 속지 두 번 속냐 (*Fool me once, shame on you; fool me twice, shame on me.*)

이것이 소프트웨어 설계에서의 효과적인 태도다.
- **처음에는** 코드가 변경되지 않을 것이라 생각하고 작성한다
- **변경이 일어나면**, 나중에 일어날 그런 종류의 변경으로부터 보호하는 추상화를 구현한다
- 즉, **첫 번째 총알은 그냥 맞고**, 그 종에서 쏘는 다른 총알에 대해서는 확실히 보호한다

> **Uncle Bob의 경험**: 우리가 놓은 올가미는 종종 틀렸다. 그것이 사용되지 않음에도 유지보수되어야 하는 **불필요한 복잡성의 악취**를 풍겼다. 지나치고 불필요한 추상화로 설계에 부하를 주지 않으려면, 추상화가 실제로 필요할 때까지 기다렸다가 올가미를 놓는 편이 차라리 낫다.

### 6.3 변경 촉진하기

첫 번째 총알을 맞기로 결정했다면, **총알이 빨리 그리고 자주 날아올수록 유리하다**. 변경 종류를 빨리 알수록 적절한 추상화를 만들기 쉽다.

촉진 방법(2장에서 논한 애자일 실천 방법):

- **테스트를 먼저 작성한다 (TDD)**: 테스트는 시스템을 사용하는 한 가지 방법이다. 테스트가 자연스럽게 많은 추상화를 미리 끌어낸다
- **아주 짧은 주기로 개발한다** — 주(week)보다는 일(day) 단위
- **기반 구조보다 기능 요소를 먼저 개발**하고, 자주 이해당사자(*stakeholder - 시스템에 이해관계를 가진 고객/사용자/관리자 등*)에게 보여준다
- **가장 중요한 기능 요소를 먼저** 개발한다
- **빨리, 그리고 자주 릴리즈**한다 — 가능한 한 자주 고객 앞에서 시연

---

## 7. 명시적인 폐쇄를 위한 추상화 — Shape 순서 결정

첫 번째 총알을 맞았다고 하자: 사용자가 모든 `Circle`이 `Square` 앞에 그려지도록 요청했다. 이제 이 종류의 변경으로부터 보호하기를 원한다.

### 7.1 자기 자신을 폐쇄하기 — `Precedes` 메소드

폐쇄는 추상화에 기반을 둔다. 그러므로 `drawAllShapes`를 순서에 대해 닫으려면 **순서 추상화(ordering abstraction)**가 필요하다.

순서 정책은 "2개의 객체가 주어졌을 때 어느 것을 먼저 그려야 하는지"를 포함한다. `Shape`에 추상 메소드 `precedes`를 정의한다.

<details>
<summary>원문 C++ 코드</summary>

```cpp
// C++ — 목록 9-3: 순서 메소드를 포함한 Shape 클래스
class Shape {
public:
    virtual void Draw() const = 0;
    virtual bool Precedes(const Shape&) const = 0;
    bool operator<(const Shape& s) {
        return Precedes(s);
    }
};

// 목록 9-4: 순서 결정을 포함한 DrawAllShapes
template <typename P>
class Lessp {
public:
    bool operator()(const P p, const P q) {
        return (*p) < (*q);
    }
};

void DrawAllShapes(vector<Shape*>& list) {
    vector<Shape*> orderedList = list;
    sort(orderedList.begin(), orderedList.end(), Lessp<Shape*>());
    vector<Shape*>::const_iterator i;
    for (i = orderedList.begin(); i != orderedList.end(); i++) {
        (*i)->Draw();
    }
}

// 목록 9-5: Circle의 순서 결정
bool Circle::Precedes(const Shape& s) const {
    if (dynamic_cast<const Square*>(&s)) {
        return true;
    } else {
        return false;
    }
}
```

</details>

```typescript
// TypeScript — Shape가 자기 자신을 순서에 대해 폐쇄
abstract class Shape {
    abstract draw(): void;
    abstract precedes(other: Shape): boolean;
}

class Circle extends Shape {
    draw(): void { /* ... */ }

    precedes(other: Shape): boolean {
        if (other instanceof Square) {
            return true;
        } else {
            return false;
        }
    }
}

class Square extends Shape {
    draw(): void { /* ... */ }

    precedes(other: Shape): boolean {
        return false;
    }
}

function drawAllShapes(list: Shape[]): void {
    const ordered = [...list].sort((a, b) => {
        if (a.precedes(b)) {
            return -1;
        } else if (b.precedes(a)) {
            return 1;
        } else {
            return 0;
        }
    });
    for (const shape of ordered) {
        shape.draw();
    }
}
```

### 7.2 이 해결책의 새로운 OCP 위반

`Circle::precedes`와 `Shape`의 다른 파생 클래스에 있는 모든 형제(*sibling - 같은 부모를 공유하는 클래스*) 함수는 **OCP를 따르지 않는다.**

- `Shape`의 새로운 파생 클래스에 대해 닫혀 있을 방법이 없다
- 새 파생 클래스가 생성될 때마다 모든 `precedes()` 함수가 변경되어야 함

> 이 문제는 28장에서 다룰 **비순환 비지터(ACYCLIC VISITOR) 패턴**으로 풀 수 있다.

`Shape`의 새 파생 클래스가 앞으로 전혀 생성되지 않는다면 문제 없지만, 자주 생성된다면 이 설계는 **상당한 스래싱(*thrashing - 비효율적인 반복 작업으로 시스템이 마비되는 현상*)**을 유발한다. 다시 한번 첫 번째 총알을 맞게 된 셈이다.

---

## 8. 데이터 주도적 접근 — 테이블로 폐쇄하기

`Shape`의 파생 클래스가 서로에 대해 아는 것을 막는다면, **테이블 주도적 접근(table-driven approach)**을 사용할 수 있다.

<details>
<summary>원문 C++ 코드</summary>

```cpp
// C++ — 목록 9-6: 테이블 주도적 도형 순서 결정 메커니즘
class Shape {
public:
    virtual void Draw() const = 0;
    bool Precedes(const Shape&) const;
    bool operator<(const Shape& s) const {
        return Precedes(s);
    }
private:
    static const char* typeOrderTable[];
};

const char* Shape::typeOrderTable[] = {
    typeid(Circle).name(),
    typeid(Square).name(),
    0
};

bool Shape::Precedes(const Shape& s) const {
    const char* thisType = typeid(*this).name();
    const char* argType = typeid(s).name();
    // typeOrderTable에서 두 타입의 위치를 찾아 비교
    // ...
}
```

</details>

```typescript
// TypeScript — 테이블 주도적 순서 결정
abstract class Shape {
    abstract draw(): void;

    // 그릴 순서를 정의하는 테이블 (외부 모듈에서 주입 가능)
    private static typeOrderTable: string[] = ['Circle', 'Square'];

    precedes(other: Shape): boolean {
        const thisOrd = Shape.typeOrderTable.indexOf(this.constructor.name);
        const argOrd = Shape.typeOrderTable.indexOf(other.constructor.name);
        // 발견되지 않은 도형은 언제나 발견된 도형에 우선
        if (thisOrd === -1) {
            return false;
        }
        if (argOrd === -1) {
            return true;
        }
        return thisOrd < argOrd;
    }
}
```

### 8.1 무엇을 얻었는가

- `drawAllShapes`를 **일반적 순서 문제에 대해 성공적으로 닫음**
- `Shape`의 파생 클래스 각각을 **새 파생 클래스 생성**에 대해 닫음
- `Shape` 객체를 형태에 따라 **다시 정렬하는 정책 변화**에 대해서도 닫음

다양한 `Shape`의 순서에 대해 닫히지 않은 유일한 항목은 **테이블 자체뿐**이다. 이 테이블은 다른 모든 모듈에서 분리되어 고유한 모듈에 위치할 수 있으므로, 테이블 변경은 다른 모듈에 아무런 영향을 주지 않는다.

> **핵심 통찰**: 닫힘은 변경의 종류를 옮기는 행위다. 테이블 주도적 접근에서는 "도형 종류"와 "순서 정책"이라는 **서로 다른 두 변경의 축**을 분리했다 — 한 축은 새로운 파생 클래스 (확장으로 폐쇄), 다른 축은 테이블 변경 (데이터 변경으로 격리).

---

## 9. 자주 하는 실수

| 안티패턴 | 문제 | 해결 |
|----------|------|------|
| **switch/type-tag** — `switch (shape.type)`로 분기 | 새 종류 추가 시 모든 switch 위치를 찾아 수정해야 함 | 다형성으로 전환 — 추상 메소드 호출 |
| **이른 추상화 (preemptive abstraction)** — 사용되지 않을 변경에 미리 올가미를 놓음 | 불필요한 복잡성의 악취. 추상화 자체가 유지보수 부담 | 첫 변경이 실제로 일어날 때 추상화 추가 |
| **모든 곳에 추상화** — 애플리케이션 전체에 마구 추상화 적용 | 추상화 폭증으로 설계 이해 불가 | 자주 변경되는 부분에만 추상화 적용 |
| **잘못된 변경 축 선택** — Shape 종류로 폐쇄했으나 순서가 변함 | "자연스러운" 모델이 실제 변경의 축과 어긋남 | 변경이 일어났을 때 다시 추상화 — 첫 총알은 맞아야 함 |
| **형제 의존 (sibling coupling)** — 한 파생 클래스가 다른 파생 클래스를 알아봄 (`instanceof`/`dynamic_cast`) | 새 파생 클래스 추가 시 모든 형제 클래스 수정 필요 | 데이터 주도적 접근 또는 비순환 비지터 패턴 |
| **추상화 부재** — 구체 클래스가 구체 클래스를 직접 사용 | 의존 클래스도 변경 전염을 받음 | 추상 인터페이스를 사이에 끼움 (스트래터지 패턴) |

---

## 10. 설계 원칙

| 원칙 | 설명 |
|------|------|
| **확장은 새 코드 추가로** | 기존 코드를 변경하지 않고 새 모듈을 덧붙임으로써 행위를 확장한다 |
| **추상화에 의존하라** | 모듈은 고정된 추상화에 의존하기 때문에 수정에 대해 닫힐 수 있다 |
| **폐쇄는 전략적이어야 한다** | 모든 변경에 대한 폐쇄는 불가능하다. **어떤** 변경에 폐쇄할지 선택하라 |
| **첫 총알은 맞는다** | 추측으로 올가미를 놓지 말고, 첫 변경이 일어났을 때 같은 종류의 다음 변경을 막는 추상화를 만든다 |
| **변경을 촉진하라** | TDD, 짧은 주기, 잦은 릴리즈로 변경의 종류를 빨리 알아낸다 |
| **인터페이스는 사용자 관점에서 명명한다** | `AbstractServer`가 아니라 `ClientInterface` — 추상화는 그것을 사용하는 클라이언트에 더 가깝다 |
| **자주 변경되는 부분에만 추상화** | 어설픈 추상화를 피하는 일은 추상화 자체만큼이나 중요하다 |

---

## 11. 결론

> **핵심 통찰**: 많은 면에서 OCP는 **객체지향 설계의 심장**이라 할 수 있다. 이 원칙을 따르면 객체지향 기술에서 당연하게 요구되는 최상의 효용(유연성, 재사용성, 유지보수성)을 낳는다. 그러나 객체지향 프로그래밍 언어를 사용한다는 것만으로 OCP를 따르는 것은 아니다.

또한 애플리케이션의 **모든 부분에 마구 추상화를 적용하는 것도 좋은 생각이 아니다.** 프로그램에서 자주 변경되는 부분에만 추상화를 적용하기 위한 개발자의 헌신이 필요하다. **어설픈 추상화를 피하는 일은 추상화 자체만큼이나 중요하다.**

---

## 요약

- **OCP 정의**: 소프트웨어 개체는 **확장에 대해 열려 있고, 수정에 대해 닫혀** 있어야 한다
- **메커니즘**: 추상화 — 고정된 추상 인터페이스에 의존하고, 행위는 새 파생 클래스로 확장
- **두 가지 핵심 패턴**:
  - **스트래터지(Strategy)** — 클라이언트가 추상 인터페이스에 의존
  - **템플릿 메소드(Template Method)** — 기반 클래스가 자신의 추상 메소드를 호출
- **Shape 예제의 교훈**:
  - 절차적 switch/case → 다형성으로 전환 (OCP 따름)
  - 그러나 "도형 종류"로 폐쇄해도 "순서 정책" 변경에는 열려 있음 → 자연스러운 모델은 없다
- **전략적 폐쇄**: 모든 변경에 폐쇄할 수는 없다. 가장 그럴법한 변경의 종류를 선택해 폐쇄한다
- **"Fool me once" 휴리스틱**: 미리 추측해 올가미를 놓지 말 것. **첫 변경이 발생하면 그때 같은 종류의 다음 변경을 막는 추상화**를 만든다
- **변경 촉진**: TDD, 짧은 주기, 잦은 릴리즈 — 변경의 종류를 빨리 알아야 좋은 추상화를 만들 수 있다
- **데이터 주도적 접근**: 변경의 축을 코드 밖(테이블)으로 옮겨 격리할 수 있다
- **어설픈 추상화 피하기**: 모든 곳에 추상화 = 불필요한 복잡성의 악취. 자주 변경되는 곳에만 적용
- **OCP는 객체지향 설계의 심장** — 하지만 OOP 언어를 쓴다고 자동으로 따라지지는 않는다
