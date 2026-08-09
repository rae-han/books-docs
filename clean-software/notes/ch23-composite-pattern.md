# Chapter 23: The Composite Pattern (컴포지트 패턴)

## 핵심 질문

여러 객체를 단일 객체와 똑같이 다룰 수 있다면 어떤 이점이 있는가? 일대다(*one-to-many - 한 객체가 여러 객체를 참조하는 관계*) 관계를 일대일(*one-to-one - 한 객체가 단일 객체만 참조하는 관계*) 관계로 바꿔도 일대다의 행위를 유지할 수 있는가? 그리고 — 모든 일대다 관계를 컴포지트로 바꿔도 되는가?

---

## 1. 컴포지트 패턴이란

컴포지트(*Composite - GoF 디자인 패턴 중 하나로, 객체들의 트리 구조를 단일 객체처럼 다루도록 하는 패턴*) 패턴은 아주 단순하지만 지니고 있는 의미는 크다. 기본 구조는 도형의 계층 구조로 설명할 수 있다.

### 1.1 구조

```
              ┌──────────────────┐
              │  «interface»     │
              │     Shape        │
              ├──────────────────┤
              │ + draw()         │
              └─────────▲────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────┴──────┐ ┌──────┴──────┐ ┌─────┴─────────────┐
│   Circle     │ │   Square    │ │  CompositeShape   │
├──────────────┤ ├─────────────┤ ├───────────────────┤
│ + draw()     │ │ + draw()    │ │ - shapes: Shape[] │
└──────────────┘ └─────────────┘ │ + add(Shape)      │
                                 │ + draw()          │
                                 └────────┬──────────┘
                                          │
                                  «delegates to each»
                                          ▼
                                       Shape[]
```

`Shape` 기반 클래스에는 `Circle`과 `Square`라는 두 개의 파생 도형이 있다. 그리고 세 번째 파생 클래스가 바로 컴포지트인 `CompositeShape`인데, 이 클래스는 여러 `Shape` 인스턴스들의 목록을 갖고 있다.

> **핵심 통찰**: `CompositeShape`의 `draw()`가 호출되면 이 클래스는 자신의 목록에 들어 있는 모든 `Shape` 인스턴스에게 이 메소드 수행을 **위임(delegate)** 한다. 따라서 시스템이 보기에 `CompositeShape`의 인스턴스는 그냥 일반 `Shape` 하나로 보인다. `Shape`를 받는 함수나 객체에게 `CompositeShape`를 전달해도 그 행위는 `Shape`와 똑같아 보인다.

### 1.2 코드 예시

<details>
<summary>원문 Java 코드</summary>

```java
// Java - 목록 23-1: Shape.java
public interface Shape {
    public void draw();
}

// Java - 목록 23-2: CompositeShape.java
import java.util.Vector;

public class CompositeShape implements Shape {
    private Vector itsShapes = new Vector();

    public void add(Shape s) {
        itsShapes.add(s);
    }

    public void draw() {
        for (int i = 0; i < itsShapes.size(); i++) {
            Shape shape = (Shape) itsShapes.elementAt(i);
            shape.draw();
        }
    }
}
```

</details>

```typescript
// TypeScript - Shape 인터페이스
interface Shape {
    draw(): void;
}

// TypeScript - CompositeShape 구현
class CompositeShape implements Shape {
    private shapes: Shape[] = [];

    add(s: Shape): void {
        this.shapes.push(s);
    }

    draw(): void {
        for (const shape of this.shapes) {
            shape.draw();
        }
    }
}
```

`CompositeShape`의 실체는 여러 `Shape` 인스턴스들 집합의 **프록시(*PROXY - 실제 객체를 대신해 동작하는 대리 객체*)** 다. 클라이언트는 단일 `Shape`인지 컴포지트인지 알 필요가 없다.

---

## 2. 예제: 컴포지트 커맨드

13장에서 논의했던 `Sensor`와 `Command` 객체를 다시 한번 생각해 보자. `Sensor`는 무엇을 감지하면 `Command`의 `do()`를 호출한다.

### 2.1 문제 상황: Sensor가 여러 Command를 실행해야 한다

이전 논의에서는 `Sensor`가 `Command`를 하나 이상 실행해야 하는 경우가 종종 있다는 사실을 언급하지 못했다. 예를 들어:

> 종이가 복사기 내부의 특정 지점에 도달하면 광학 센서가 작동된다. 그러면 이 센서는 특정 모터를 정지시키고 다른 모터를 실행한 다음 특정 클러치를 작동시킨다.

따라서 처음에는 모든 `Sensor` 클래스가 `Command` 객체의 목록을 유지해야 한다고 생각할 수 있다.

```
   ┌─────────┐  0..*   ┌──────────┐
   │ Sensor  │────────▶│ Command  │
   └─────────┘         └──────────┘
```

### 2.2 깨달음: 모든 Command가 동일하게 취급된다

하지만 `Sensor`가 `Command`를 하나 이상 실행할 때, 언제나 **모든 `Command` 객체를 동일하게 취급**한다는 사실을 곧 깨닫게 된다. 이 말은, `Sensor`가 그저 목록을 순회하면서 각 `Command`마다 단지 `do()`만 호출한다는 뜻이다. 이런 상황은 컴포지트 패턴을 적용하기에 적합하다.

### 2.3 해결: CompositeCommand 도입

`Sensor` 클래스는 그대로 놓아두고 `CompositeCommand` 클래스를 만든다.

```
   ┌─────────┐  0..1   ┌──────────────────┐
   │ Sensor  │────────▶│   «interface»    │
   └─────────┘         │     Command      │
                       ├──────────────────┤
                       │ + do()           │
                       └────────▲─────────┘
                                │
                       ┌────────┴─────────┐
                       │ CompositeCommand │
                       ├──────────────────┤
                       │ + add(Command)   │
                       │ + do()           │
                       └──────────────────┘
```

<details>
<summary>원문 Java 코드</summary>

```java
// Java - Command 인터페이스
public interface Command {
    void do_();
}

// Java - CompositeCommand
import java.util.Vector;

public class CompositeCommand implements Command {
    private Vector itsCommands = new Vector();

    public void add(Command c) {
        itsCommands.add(c);
    }

    public void do_() {
        for (int i = 0; i < itsCommands.size(); i++) {
            Command c = (Command) itsCommands.elementAt(i);
            c.do_();
        }
    }
}
```

</details>

```typescript
// TypeScript - Command 인터페이스
interface Command {
    do(): void;
}

// TypeScript - CompositeCommand
class CompositeCommand implements Command {
    private commands: Command[] = [];

    add(c: Command): void {
        this.commands.push(c);
    }

    do(): void {
        for (const c of this.commands) {
            c.do();
        }
    }
}
```

> **핵심 통찰**: 이렇게 해서 `Sensor`나 `Command`를 변경할 필요가 없어졌다. 우리는 두 클래스 모두 **하나도 변경하지 않고도** `Command`에 복수성(multiplicity)이라는 개념을 추가할 수 있었다. 이것은 **OCP(*Open-Closed Principle - 개방 폐쇄 원칙. 확장에는 열려 있고 변경에는 닫혀 있어야 한다*)** 적용의 한 예다.

---

## 3. 다수성이냐 아니냐

여기에서 흥미로운 논제가 하나 생긴다. 우리는 `Sensor`는 하나도 변경하지 않고도 `Sensor`가 마치 여러 `Command`를 갖고 있는 것처럼 동작하게 만드는 데는 성공했다.

### 3.1 일대일 vs 일대다

> **Uncle Bob의 경험**: `Sensor`와 `Command`의 연관은 일대일이었는데, 이것을 일대다로 바꾸는 것에 잠시 마음이 끌렸다. 하지만 그러는 대신, 일대다 관계 없이도 일대다의 행위를 할 수 있는 방법을 찾아냈다. **일대일 관계가 일대다 관계보다 훨씬 이해하기도 쉽고 코딩 및 유지보수하기도 쉬우므로**, 분명 올바른 설계상의 균형(*tradeoff - 한쪽을 얻는 대신 다른 쪽을 양보하는 선택*)처럼 보인다.

| 항목 | 일대다 (List/Vector) | 일대일 + 컴포지트 |
|------|---------------------|------------------|
| 클라이언트 코드 | 목록 관리, 순회 코드 필요 | 단일 객체처럼 호출 |
| 가독성 | 컬렉션 다루는 로직이 섞임 | 단순함 |
| 유지보수 | 목록 관리 코드가 여러 곳에 분산 | 컴포지트 한 곳에만 |
| 확장 | 새 사용처마다 순회 로직 작성 | 변경 없이 컴포지트 주입 |

### 3.2 일반화 — 다른 일대다도 컴포지트로?

> 일반적인 소프트웨어 설계에서도 이와 비슷한 상황들이 많을 것이다. 즉, 객체의 벡터나 목록을 만드는 대신 컴포지트를 쓸 수 있는 경우가 있을 것이다.

여러분이 지금 하고 있는 프로젝트에서 컴포지트를 사용했다면 얼마나 많은 일대다 관계를 일대일 관계로 바꿀 수 있었을까?

### 3.3 컴포지트로 바꿀 수 없는 경우

물론, 컴포지트를 사용한다고 **모든** 일대다 관계를 일대일 관계로 되돌릴 수 있는 것은 아니다. **목록에 들어 있는 모든 객체가 동일하게 취급받을 때만** 이것이 가능하다.

예를 들어:

> 직원 목록을 유지하면서 월급날이 오늘인 직원을 찾기 위해 그 목록을 검색한다면 아마 컴포지트 패턴을 사용해서는 안 될 것이다. 그런 상황에서는 여러분이 모든 직원을 동일하게 취급하지 않을 것이기 때문이다.

> **핵심 통찰**: 컴포지트 패턴이 적용 가능한 조건은 **"모든 원소를 동일하게 취급한다"** 는 것이다. 원소마다 다른 분기, 다른 검색 조건, 다른 처리 흐름이 필요하다면 컴포지트는 맞지 않는다. 단순 위임(delegate)만으로 충분한 균질한 컬렉션에서만 컴포지트의 장점이 빛난다.

### 3.4 컴포지트로 바꿀 수 있는 경우의 이점

그래도, 충분히 컴포지트로 바꿀 수 있는 일대다 관계도 많이 있다. 그리고 그렇게 바꿨을 때 얻을 수 있는 이점은 상당하다.

> 컴포지트를 사용하면 우리 클래스의 클라이언트마다 목록 관리와 순환 코드가 중복해서 등장하는 대신, 그 코드가 **컴포지트 클래스에서만 단 한 번** 나타나면 된다.

---

## 4. 컴포지트 패턴의 핵심 정리

### 4.1 구조적 특징

| 요소 | 역할 |
|------|------|
| **Component** (`Shape`, `Command`) | 단일 객체와 컴포지트 모두가 구현하는 공통 인터페이스 |
| **Leaf** (`Circle`, `Square`, 개별 `Command`) | 더 이상 분해되지 않는 단일 객체 |
| **Composite** (`CompositeShape`, `CompositeCommand`) | 자식 Component들을 보관하고 메소드 호출을 위임 |
| **Client** (`Sensor`, 그리기 함수 등) | Component 인터페이스만 알면 됨 — Leaf와 Composite를 구분하지 않음 |

### 4.2 프록시 패턴과의 구조적 유사성

컴포지트는 PROXY 패턴과 구조적으로 유사하다. 둘 다:

- Component 인터페이스를 구현
- 실제 작업은 다른 객체(들)에 위임
- 클라이언트는 차이를 알 필요가 없음

차이점은:

| 항목 | PROXY | COMPOSITE |
|------|-------|-----------|
| 위임 대상 수 | 1개 | 여러 개 (0..n) |
| 목적 | 접근 제어, 지연 로딩, 원격 호출 등 | 다수 객체를 단일 객체처럼 다루기 |

---

## 5. 자주 하는 실수

| 안티패턴 | 문제 | 해결 |
|----------|------|------|
| **원소마다 다른 처리** | 컴포지트 안에 분기/타입 체크가 들어감 | 컴포지트 부적합 — 일반 컬렉션 + 전략 패턴 등 사용 |
| **컴포지트 = 만능** | 모든 일대다를 컴포지트로 강제 변환 | 균질 처리되는 경우에만 적용 |
| **클라이언트가 Composite 타입을 직접 의존** | 다형성 이점 상실 | 클라이언트는 Component 인터페이스만 의존 |
| **컴포지트 내부 노출** | `getChildren()` 등으로 내부 컬렉션 외부 노출 | 위임 메소드만 노출, 컬렉션은 캡슐화 |

---

## 6. 설계 원칙

| 원칙 | 설명 |
|------|------|
| **단일 객체와 집합을 동일하게 다루라** | 클라이언트는 Leaf와 Composite의 차이를 알 필요가 없다 |
| **일대다 → 일대일 + 컴포지트** | 균질 처리되는 경우, 관계를 단순화하라 |
| **OCP를 만족시킨다** | Sensor와 Command 둘 다 변경하지 않고 복수성 추가 |
| **목록 관리 코드는 한 곳에만** | 클라이언트마다 순회 코드를 중복하지 말라 |

---

## 7. 결론

컴포지트 패턴은 단순하지만 강력하다. **하나의 객체를 받는 인터페이스로 여러 객체를 다룰 수 있게** 만들어 주며, 그 결과 클라이언트 코드를 변경 없이도 일대다 행위로 확장할 수 있다.

> **핵심 통찰**: 컴포지트의 진정한 가치는 **"관계의 다수성을 인터페이스 뒤로 숨기는 것"** 에 있다. 일대일 관계가 코드상으로는 일대다처럼 행동한다. 이는 단순성을 유지하면서 유연성을 얻는 드문 패턴 중 하나다.

---

## 요약

- **컴포지트 패턴**: 단일 객체와 객체의 집합을 동일한 인터페이스로 다루게 하는 패턴
- **구조**: Component 인터페이스를 Leaf(개별 객체)와 Composite(집합 객체)가 모두 구현
- **CompositeShape 예제**: `Shape` 인터페이스를 구현하면서 `Shape` 목록을 보유, `draw()` 호출 시 모든 원소에 위임
- **CompositeCommand 예제**: `Sensor`와 `Command` 둘 다 변경 없이 다수 실행 기능 추가 — **OCP 적용 사례**
- **일대일 → 일대다 행위**: 컴포지트를 쓰면 관계는 일대일이지만 행위는 일대다 — 가독성과 유지보수성 ↑
- **적용 조건**: 컬렉션의 **모든 원소가 동일하게 취급될 때**만 적용 가능
- **부적합 사례**: 원소별로 다른 처리가 필요한 경우 (예: 직원 목록 검색)
- **이점**: 목록 관리/순회 코드가 컴포지트 클래스 한 곳에만 존재 — 클라이언트 코드 중복 제거
- **PROXY 패턴과의 유사성**: 둘 다 인터페이스 뒤로 실제 작업을 숨김. 다만 PROXY는 1개, COMPOSITE는 다수에 위임
