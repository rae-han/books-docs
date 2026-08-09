# Chapter 21: The Factory Pattern (팩토리 패턴)

## 핵심 질문

`new` 키워드 한 번을 쓰는 것만으로도 의존관계 역전 원칙(DIP)을 어기게 된다는 말은 무엇을 의미하는가? 그렇다면 객체의 인스턴스는 누가, 어떻게 생성해야 하는가? 그리고 팩토리(*Factory - 다른 객체의 인스턴스를 생성하는 책임만을 가진 객체*)가 그렇게 강력한 도구라면, 왜 항상 기본으로 사용하지는 않는가?

> 공장을 짓는 사람은 사원(寺院)을 짓고 있는 셈이다.<br>— 캘빈 쿨리지(Calvin Coolidge), 1872~1933

---

## 1. `new` 키워드와 DIP 위반

11장의 의존관계 역전 원칙(*DIP: Dependency Inversion Principle - 구체 클래스가 아닌 추상 인터페이스에 의존하라는 원칙*)에 따르면, 구체 클래스에 의존하는 것은 피하고 추상 클래스에 의존하는 것을 선호해야 한다. 구체 클래스가 쉽게 변경되는 종류일 경우 특히 그렇다.

따라서 다음과 같은 코드는 DIP를 위반한다.

<details>
<summary>원문 Java 코드</summary>

```java
Circle c = new Circle(origin, 1);
```

</details>

```typescript
// TypeScript
const c = new Circle(origin, 1);
```

`Circle`은 구체 클래스다. 그러므로 `Circle`의 인스턴스를 생성하는 모듈은 DIP를 어기게 된다. **사실 `new` 키워드를 사용하기만 하면 DIP를 어기는 셈이 된다.**

### 1.1 모든 `new` 가 나쁜 것은 아니다

DIP 위반이 거의 해롭지 않은 경우도 있다. 상당히 많은 경우가 여기에 포함된다. 구체 클래스가 변경될 가능성이 크면 클수록, 그 클래스에 의존할 때 문제가 생길 가능성도 커진다. 하지만 구체 클래스가 쉽게 변경되는 종류의 클래스가 아니라면, 그 클래스에 의존하는 것이 그렇게 걱정거리가 되지는 않는다.

| 의존 대상 | 변경 가능성 | DIP 위반 위험도 |
|-----------|-------------|------------------|
| `String` | 매우 낮음 | 무시 가능 |
| 표준 라이브러리의 안정된 타입 | 낮음 | 낮음 |
| 한창 개발 중인 도메인 클래스 | 높음 | 높음 — 팩토리 도입 검토 |

예를 들어, `String`의 인스턴스를 만드는 것 정도는 그렇게 신경 쓸 필요가 없다. `String`이 조만간 변경될 가능성은 거의 없기 때문에 `String`에 의존하는 것은 매우 안전하다. 반면, 애플리케이션을 한창 개발하는 중이라면, 매우 변경되기 쉬운 구체 클래스들이 많이 생긴다. 이 구체 클래스들에 의존하는 것은 문제가 있으며, 대부분의 변경에 영향을 받지 않도록 추상 인터페이스에 의존하는 편이 낫다.

> **핵심 통찰**: 팩토리 패턴을 사용하면 추상 인터페이스에만 의존하면서도 구체적 객체(*concrete object - 실제 동작을 구현한 구상 클래스의 인스턴스*)들의 인스턴스를 만들 수 있다. 한창 개발하느라 생성할 구체 클래스의 변경이 잦을 때 이 패턴이 큰 도움이 된다.

---

## 2. 문제 상황 — `SomeApp` 의 DIP 위반

그림 21-1에서 문제가 되는 시나리오를 볼 수 있다. `Shape` 인터페이스에 의존하는 `SomeApp`이라는 이름의 클래스가 있는데, 이 `SomeApp`은 오직 `Shape` 인터페이스를 통해서만 여러 `Shape` 인스턴스들을 사용한다. 불행하게도, `SomeApp`은 `Square`와 `Circle`의 인스턴스를 직접 생성하기 때문에, 구체 클래스인 `Square`와 `Circle`에게 의존하게 된다.

```
                    ┌──────────────┐
                    │   SomeApp    │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │ «creates»  │  «uses»    │ «creates»
              ▼            ▼            ▼
        ┌─────────┐  ┌───────────┐  ┌─────────┐
        │ Square  │─▶│ «interface»│◀─│ Circle  │
        └─────────┘  │   Shape    │  └─────────┘
                     └────────────┘
```

**그림 21-1** 구체 클래스를 생성하기 때문에 DIP를 위반하는 애플리케이션

이 상황의 문제점은 다음과 같다:

- `SomeApp`은 `Shape` 인터페이스에는 잘 의존하고 있지만,
- `new Square()`, `new Circle()` 호출 때문에 구체 클래스에 컴파일/링크 의존성이 생긴다
- `Square`, `Circle`이 변경되면 `SomeApp`도 재컴파일/재배포해야 한다

---

## 3. 팩토리 패턴의 적용

`SomeApp`에 그림 21-2처럼 팩토리 패턴을 적용하면 이 문제점을 고칠 수 있다. 여기 `ShapeFactory` 인터페이스가 등장하는데, 이 인터페이스에는 `makeSquare`와 `makeCircle` 두 메소드가 있다. `makeSquare` 메소드는 `Square`의 인스턴스를 생성하고, `makeCircle`은 `Circle`의 인스턴스를 생성한다. 하지만 두 메소드가 생성한 인스턴스를 반환할 때는 모두 `Shape` 타입으로 해서 반환한다.

```
        ┌──────────────┐
        │   SomeApp    │
        └──────┬───┬───┘
               │   │
       «uses»  │   │  «uses»
               ▼   ▼
   ┌────────────────────┐      ┌────────────┐
   │    «interface»     │      │ «interface»│
   │   ShapeFactory     │      │   Shape    │
   ├────────────────────┤      └────────────┘
   │ + makeSquare()     │            ▲
   │ + makeCircle()     │            │
   └─────────┬──────────┘            │
             │                       │
             ▼                       │
   ┌────────────────────┐            │
   │   ShapeFactory     │            │
   │  Implementation    │            │
   └────────┬───────────┘            │
            │                        │
   «creates»│                        │
            ▼                        │
       ┌─────────┐  ┌─────────┐      │
       │ Square  │  │ Circle  │──────┘
       └─────────┘  └─────────┘
```

**그림 21-2** Shape 팩토리

### 3.1 ShapeFactory 인터페이스

목록 21-1에 `ShapeFactory`의 한 예가 나와 있다.

<details>
<summary>원문 Java 코드 — 목록 21-1 ShapeFactory.java</summary>

```java
public interface ShapeFactory {
    public Shape makeCircle();
    public Shape makeSquare();
}
```

</details>

```typescript
// TypeScript
interface ShapeFactory {
  makeCircle(): Shape;
  makeSquare(): Shape;
}
```

### 3.2 ShapeFactoryImplementation 구현

목록 21-2에 `ShapeFactoryImplementation`의 예가 나와 있다.

<details>
<summary>원문 Java 코드 — 목록 21-2 ShapeFactoryImplementation.java</summary>

```java
public class ShapeFactoryImplementation implements ShapeFactory {
    public Shape makeCircle() {
        return new Circle();
    }

    public Shape makeSquare() {
        return new Square();
    }
}
```

</details>

```typescript
// TypeScript
class ShapeFactoryImplementation implements ShapeFactory {
  makeCircle(): Shape {
    return new Circle();
  }

  makeSquare(): Shape {
    return new Square();
  }
}
```

이렇게 하면 구체 클래스에 의존하는 문제점이 완전하게 해결됨을 알 수 있다. 애플리케이션 코드는 더 이상 `Circle`이나 `Square`에 의존하지 않으면서도 이 두 클래스의 인스턴스는 계속 생성할 수 있다. 애플리케이션은 이 인스턴스들을 `Shape` 인터페이스를 통해서만 사용하며, `Square`나 `Circle` 한 곳에만 있는 메소드는 전혀 호출하지 않는다.

따라서 이제 구체 클래스에 의존하는 문제점은 사라진다. 그래도 누군가 한 사람은 `ShapeFactoryImplementation`을 구현해야 하겠지만, 나머지 사람들은 이제 더 이상 `Square`나 `Circle`을 생성할 필요가 없다. **`ShapeFactoryImplementation` 자체는 아마 `main` 함수에서 생성되거나 `main` 함수에 딸린 초기화 함수에서 생성될 것이다.**

> **핵심 통찰**: 팩토리를 도입하면 "구체 클래스를 누군가는 생성해야 한다"는 책임을 시스템의 한 지점(보통 `main`)으로 격리할 수 있다. 애플리케이션의 나머지 모든 부분은 추상에만 의존하는 깨끗한 상태가 된다.

---

## 4. 의존관계 순환 문제

눈치 빠른 독자는 이 형태의 팩토리 패턴에 문제가 있음을 알아챘을 것이다. `ShapeFactory` 클래스는 `Shape`의 파생형마다 메소드가 하나씩 있다. 그런데 이렇게 할 경우 `Shape`에 새로운 파생형을 추가하는 일을 매우 어렵게 만들지도 모르는 의존관계 순환이 생길 수 있다.

새로운 `Shape` 파생형을 추가할 때마다 `ShapeFactory`에 새로운 메소드를 추가해야 하는데, 대부분의 경우 이것은 모든 `ShapeFactory` 사용자의 `ShapeFactory` 클래스를 재컴파일하고 재배포해야 한다는 의미가 되어버린다.

### 4.1 해결책 — 문자열 인자를 받는 `make` 메소드

타입 안정성을 조금 희생하면 이 의존관계 순환을 막을 수 있다. `ShapeFactory`에 `Shape` 파생형마다 메소드를 하나씩 만드는 대신, `String`을 받는 `make` 함수 하나만 만들면 된다. 이 기법을 사용하려면 `ShapeFactoryImplementation`이 들어오는 인자를 가지고 어떤 `Shape` 파생형을 인스턴스화해야 할지 결정하기 위해 연쇄적으로 `if/else` 문을 사용해야 한다.

<details>
<summary>원문 Java 코드 — 목록 21-3 원을 생성하는 코드 조각</summary>

```java
public void testCreateCircle() throws Exception {
    Shape s = factory.make("Circle");
    assert(s instanceof Circle);
}
```

</details>

```typescript
// TypeScript
test("createCircle", () => {
  const s = factory.make("Circle");
  expect(s).toBeInstanceOf(Circle);
});
```

<details>
<summary>원문 Java 코드 — 목록 21-4 ShapeFactory.java</summary>

```java
public interface ShapeFactory {
    public Shape make(String shapeName) throws Exception;
}
```

</details>

```typescript
// TypeScript
interface ShapeFactory {
  make(shapeName: string): Shape;
}
```

<details>
<summary>원문 Java 코드 — 목록 21-5 ShapeFactoryImplementation.java</summary>

```java
public class ShapeFactoryImplementation implements ShapeFactory {
    public Shape make(String shapeName) throws Exception {
        if (shapeName.equals("Circle"))
            return new Circle();
        else if (shapeName.equals("Square"))
            return new Square();
        else
            throw new Exception("ShapeFactory cannot create " + shapeName);
    }
}
```

</details>

```typescript
// TypeScript
class ShapeFactoryImplementation implements ShapeFactory {
  make(shapeName: string): Shape {
    if (shapeName === "Circle") {
      return new Circle();
    } else if (shapeName === "Square") {
      return new Square();
    } else {
      throw new Error(`ShapeFactory cannot create ${shapeName}`);
    }
  }
}
```

### 4.2 런타임 에러는 어떻게 막을까?

`Shape` 파생형의 이름을 잘못 쓴 호출자가 컴파일 에러 대신 런타임 에러를 받게 되기 때문에, 이렇게 하면 위험하다고 주장하는 사람이 있을지도 모른다. 틀린 말은 아니다.

> **Uncle Bob의 경험**: 하지만 적절한 수의 단위 테스트가 있고 테스트 주도적 개발(TDD)을 적용한다면 런타임 에러가 문제가 되기 전에 미리 잡을 수 있을 것이다. 컴파일러의 타입 검사를 잃은 대신, 단위 테스트라는 더 강력한 검증 수단으로 대체하는 것이다.

| 방식 | 타입 안정성 | 의존관계 순환 |
|------|-------------|----------------|
| 파생형마다 메소드 (`makeCircle`, `makeSquare`) | 강함 (컴파일 타임 보장) | **있음** — 새 파생형 추가 시 재컴파일 |
| 문자열 인자 받는 `make(name)` | 약함 (런타임 검증) | **없음** — 인터페이스 변경 없음 |

---

## 5. 대체할 수 있는 팩토리

팩토리를 사용해서 생기는 큰 장점 중 하나는, **어떤 팩토리의 구현을 다른 구현으로 대체할 수 있다는 점이다.** 그럼으로써 애플리케이션 안에 있는 객체들의 집합 하나를 다른 집합으로 통째로 대체할 수 있다.

### 5.1 예제 — 다양한 DB 백엔드 지원

다양한 데이터베이스 구현에 모두 잘 적응해야 하는 애플리케이션을 하나 예로 들어 보자. 사용자가 일반 파일을 사용할 수도 있고, Oracle™ 어댑터를 구매할 수도 있다고 가정해 보자. 프록시(*Proxy - 다른 객체에 대한 접근을 제어하기 위해 그 객체를 대리하는 객체. 26장에서 다룸*) 패턴을 써서 애플리케이션과 데이터베이스 구현을 분리할 수도 있을 것이다. 그리고 이 프록시들을 인스턴스화하기 위해 팩토리들을 사용할 수도 있을 것이다.

```
        ┌─────────────────┐
        │   Application   │
        └────────┬────────┘
                 │
                 ▼
       ┌──────────────────────┐         ┌──────────────┐
       │     «interface»      │         │ «interface»  │
       │   EmployeeFactory    │         │   Employee   │
       ├──────────────────────┤         └──────────────┘
       │ + makeEmp()          │                ▲
       │ + makeTimeCard()     │                │
       └──────────┬───────────┘                │
                  │                            │
        ┌─────────┴──────────┐                 │
        ▼                    ▼                 │
   ┌──────────┐         ┌──────────┐           │
   │  Oracle  │         │ FlatFile │           │
   │ Factory  │         │ Factory  │           │
   └────┬─────┘         └─────┬────┘           │
        │ «creates»           │ «creates»      │
        ▼                     ▼                │
   ┌──────────┐         ┌──────────┐           │
   │  Oracle  │         │ FlatFile │           │
   │ Employee │         │ Employee │───────────┘
   │  Proxy   │         │  Proxy   │
   └──────────┘         └──────────┘
```

**그림 21-3** 대체할 수 있는 팩토리

`EmployeeFactory`에 두 가지 구현이 있음을 주목하자. 하나는 일반 파일을 대상으로 작업하는 프록시들을 만들고, 다른 하나는 Oracle™을 대상으로 작업하는 프록시들을 만든다. **애플리케이션 자체는 어떤 것이 사용되는지 모르거나, 알더라도 상관하지 않는다는 점**에도 주목하자.

> **핵심 통찰**: 팩토리의 구현을 교체하는 것은 곧 "객체들의 집합 하나를 완전히 다른 집합으로 교체"하는 것이다. 이것은 단일 객체 단위의 다형성을 넘어 **객체 가족 단위의 다형성**을 제공한다. GoF의 *Abstract Factory* 패턴이 바로 이 개념이다.

---

## 6. 테스트 픽스처를 위해 팩토리 사용하기

단위 테스트를 작성할 때, 어떤 모듈의 행위를 그 모듈이 사용하는 다른 모듈들과 분리된 상태에서 테스트하고 싶은 경우가 종종 있다. 예를 들어, 데이터베이스를 사용하는 `Payroll` 애플리케이션이 있다고 생각해 보자. 여기서 데이터베이스를 전혀 사용하지 않고 `Payroll` 모듈의 기능을 테스트해 보고 싶을 수 있다.

```
   ┌──────────┐           ┌──────────┐
   │ Payroll  │──────────▶│ Database │
   └──────────┘           └──────────┘
```

**그림 21-4** Payroll이 Database를 사용한다.

### 6.1 Database 인터페이스 추출

이것은 데이터베이스의 추상 인터페이스를 사용해서 이룰 수 있다. 추상 인터페이스의 구현 하나는 실제 데이터베이스를 사용하고, 다른 하나는 데이터베이스의 행위를 흉내 낸다. 그리고 데이터베이스로 들어오는 호출이 올바른지 검사하기 위해 테스트 코드를 작성하면 된다.

```
                ┌──────────┐
                │ Payroll  │
                └────┬─────┘
                     │
                     ▼
              ┌──────────────┐
              │ «interface»  │
              │   Database   │
              └──────┬───────┘
                     ▲
       ┌─────────────┴─────────────┐
       │                           │
  ┌────────────┐            ┌──────────────┐
  │ PayrollTest│            │   Database   │
  │            │            │Implementation│
  └────────────┘            └──────────────┘
```

**그림 21-5** PayrollTest 가 Database 를 스푸핑(*spoofing - 위장, 어떤 객체인 척 행세하여 호출을 가로채는 기법*)한다.

`PayrollTest` 모듈은 `Payroll` 모듈에게 호출을 보냄으로써 이 모듈을 테스트한다. 그리고 `PayrollTest`는 `Payroll`이 데이터베이스에 보내는 호출을 잡기 위해 `Database` 인터페이스도 구현하는데, 이러면 `Payroll`이 올바로 동작하는지 `PayrollTest`가 보증할 수 있게 된다. 그리고 이렇게 하면 다른 방법으로는 생성하기 어려운 여러 종류의 데이터베이스 에러나 문제도 `PayrollTest`가 흉내 내볼 수 있다.

### 6.2 누가 `Database` 구현을 주입하는가?

하지만 `Payroll`은 어떻게 자기가 `Database`로서 사용할 `PayrollTest`의 인스턴스를 받을 수 있을까? 분명히 `Payroll`이 `PayrollTest`를 직접 생성하지는 않을 것이다. 하지만 역시 마찬가지로 분명히, `Payroll`은 어떻게든 자신이 사용할 `Database` 구현에 대한 참조를 받아야만 한다.

| 주입 방식 | 설명 |
|-----------|------|
| **생성자/메소드 인자 전달** | 가장 자연스러운 경우. `PayrollTest`가 `Database` 참조를 `Payroll`에게 직접 넘겨준다 |
| **전역 변수 설정** | `PayrollTest`가 `Database`를 참조하는 전역 변수를 미리 설정 |
| **팩토리를 통한 생성** | `Payroll`이 `Database` 인스턴스를 꼭 스스로 생성해야 하는 경우, 팩토리를 가로채서 테스트 버전을 만들도록 한다 |

마지막 경우라면, `Payroll`에게 다른 팩토리를 넘겨주는 방법으로 `Payroll`을 속여서 `Database`의 테스트 버전을 생성하도록 팩토리를 사용할 수 있다.

### 6.3 팩토리 스푸핑 구조

```
           «global» gDatabaseFactory
                    │
                    ▼
            ┌──────────────────┐
            │  «interface»     │
            │ DatabaseFactory  │
            └──────────────────┘
                    ▲
       ┌────────────┘
       │
   ┌───────────┐        ┌──────────┐
   │PayrollTest│        │ Payroll  │
   └─────┬─────┘        └────┬─────┘
         │                   │
         │«creates»          ▼
         │             ┌──────────────┐
         │             │  «interface» │
         │             │   Database   │
         │             └──────────────┘
         │                   ▲
         ▼                   │
   ┌──────────────┐          │
   │   Database   │──────────┘
   │Implementation│
   └──────────────┘
```

**그림 21-6** 팩토리 스푸핑

`Payroll` 모듈은 `gDatabaseFactory`라는 이름의 전역 변수(또는 전역 클래스의 정적 변수)를 통해 팩토리를 얻는다. `PayrollTest` 모듈은 `DatabaseFactory`를 구현하고 자기 자신의 참조를 `gDatabaseFactory`에 넣는다. `Payroll`이 `Database`를 생성하기 위해 팩토리를 사용한다면, `PayrollTest`가 이 호출을 받아서 자기 자신의 참조를 반환한다.

이렇게 하면 자기가 `Database`를 생성했다고 `Payroll`이 믿게 만들면서도, **`PayrollTest` 모듈이 `Payroll` 모듈을 완전하게 스푸핑해서 모든 데이터베이스 호출을 가로챌 수 있다.**

---

## 7. 팩토리 사용이 얼마나 중요한가?

DIP를 엄격하게 적용하면, 시스템에 들어있는 쉽게 변경되는 종류의 모든 클래스마다 팩토리를 사용해야 한다. 그뿐만 아니라 팩토리 패턴이 지닌 힘은 마음을 끌리게 한다. 이런 두 가지 요인은 때때로 개발자가 기본적으로 팩토리를 사용하도록 부추길 수 있다. **하지만 이것은 너무 극단적이기 때문에 그다지 권장하지 않는다.**

> **Uncle Bob의 경험**: 나는 보통 팩토리를 사용하지 않고 시작하며, 팩토리의 필요성이 충분히 커지면 그제야 시스템에 팩토리를 도입한다. 예를 들어보자. 프록시 패턴을 사용해야만 하게 된다면, 영속적인 객체들을 생성하기 위해 팩토리도 사용해야만 할 것이다. 다른 예도 들어보자. 다른 객체를 생성하는 어떤 객체가 있다고 할 때, 단위 테스트를 하는 동안 이 객체를 스푸핑해야만 하는 상황도 종종 만나게 된다. 그러면 그때 아마 팩토리를 쓰게 될 것이다. 아무튼 어떤 경우라도 팩토리가 당연히 필요할 것이라고 가정하고 시작하지는 않는다.

### 7.1 팩토리 도입의 비용

팩토리는 피하려면 피할 수 있는 복잡함이다. 특히 지금 진화하고 있는 설계의 초기 단계일 경우라면 더욱 그러하다. 언제나 팩토리를 기본으로 사용한다면 **설계를 확장하기가 급격히 어려워진다.**

팩토리를 사용해서 새로운 클래스를 하나 만들려면 다음 4가지를 새로 만들어야 한다:

| # | 만들어야 할 것 |
|---|----------------|
| 1 | 새로 만들 클래스 (예: `NewShape`) |
| 2 | 그 클래스가 구현할 인터페이스 (예: `Shape`) |
| 3 | 팩토리의 인터페이스 클래스 (예: `ShapeFactory`) |
| 4 | 팩토리의 구체 구현 클래스 (예: `ShapeFactoryImplementation`) |

### 7.2 팩토리 도입 트리거

다음 신호 중 하나가 나타날 때 팩토리 도입을 고려한다:

- **프록시 패턴 도입**: 영속성을 위한 프록시가 등장하면 그 프록시를 만들 팩토리도 필요해진다
- **테스트에서의 스푸핑 필요**: 객체를 생성하는 객체가 등장하고 그 의존을 단위 테스트에서 격리해야 할 때
- **다중 백엔드 지원**: 같은 추상에 대해 객체 가족 단위로 구현을 교체해야 할 때
- **구체 클래스의 변동성이 명확히 커진 시점**: 그 클래스에 의존하는 모듈들의 재컴파일/재배포 부담이 실제로 발생하기 시작한 시점

---

## 요약

- 모든 `new` 키워드 사용은 잠재적으로 DIP를 위반한다. 다만 안정된 라이브러리 타입(`String` 등)에 대한 의존은 무해하고, 한창 개발 중인 변동성 큰 구체 클래스에 대한 의존이 문제가 된다.
- **팩토리 패턴**은 추상 인터페이스에만 의존하면서도 구체 객체를 생성할 수 있게 하여 DIP를 지키게 도와준다.
- 파생형마다 메소드를 두는 방식은 타입 안정성이 강하지만 의존관계 순환을 만든다. 문자열 인자 하나로 받는 `make` 방식은 타입 안정성을 단위 테스트로 대체한다.
- 팩토리의 구현을 교체하면 **객체 가족 단위로** 시스템 동작을 통째로 바꿀 수 있다 (Abstract Factory).
- **테스트 픽스처**에서 팩토리는 강력한 도구다. 팩토리를 스푸핑하면 `Payroll`이 자기가 생성했다고 믿는 `Database` 인스턴스를 테스트가 가로챌 수 있다.
- **하지만 팩토리는 피할 수 있는 복잡함이다.** 클래스 하나를 추가하기 위해 4개의 새 클래스를 만들어야 한다.
- 기본으로 팩토리를 사용하는 것이 최선인 경우는 드물다. **팩토리 없이 시작하고, 필요성이 충분히 커진 시점에 도입한다.**

---

## 참고문헌

1. Gamma, et al. *Design Patterns*. Reading, MA: Addison-Wesley, 1995.
