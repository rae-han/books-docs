# Chapter 16: Singleton and Monostate (싱글톤과 모노스테이트)

## 핵심 질문

단 하나의 인스턴스만 가져야 하는 클래스는 어떻게 그 단일성을 강제할 수 있는가? 싱글톤(*Singleton - 클래스가 단 하나의 인스턴스만 갖도록 강제하는 GoF 패턴*)과 모노스테이트(*Monostate - 모든 변수를 정적으로 만들어 단일성을 행위로만 강제하는 패턴*)는 같은 목적을 달성하면서도 비용·이익의 균형이 왜 그렇게 다른가? 언제 어느 쪽을 선택해야 하는가?

> 존재의 무한한 지복이여! 이것이 있다. 그리고 그 외에는 아무것도 없다.<br>— 에드윈 애벗(Edwin A. Abbott)의 『Flatland(평면세계)』, 중점에 대해

---

## 1. 단일성을 왜 강제하는가

보통 클래스와 인스턴스 사이에는 **일대다 관계**가 있다. 대부분의 클래스에서는 많은 인스턴스를 만들어내며, 인스턴스는 필요할 때 생성되고 이용 가치가 사라졌을 때 버려진다. 인스턴스는 메모리 할당과 해제의 흐름 속에서 들락날락한다.

그러나 **단 하나의 인스턴스만을 가져야 하는 클래스**도 있다. 이런 인스턴스는 프로그램이 시작했을 때 처음 나타나고, 프로그램이 끝날 때 사라져야 한다. 이런 객체는 종종 다음 역할을 맡는다:

| 역할 | 설명 |
|------|------|
| **루트(root)** | 애플리케이션의 진입점. 이 루트에서 시스템에 있는 다른 많은 객체로 가는 경로를 찾을 수 있다 |
| **공장(factory)** | 시스템에 있는 다른 객체를 만들기 위해 사용 |
| **관리자(manager)** | 다른 특정한 객체를 추적하여 그 객체의 보폭(pace)에 맞게 동작시키는 역할 |

### 1.1 둘 이상이 만들어지면

이 객체들이 무엇이든 간에, **둘 이상이 만들어지면 심각한 논리 실패**가 된다:

- **둘 이상의 루트** → 애플리케이션에 있는 객체에 대한 접근이 선택된 루트에 의존하게 된다. 여러 개의 루트가 있다는 사실을 모르는 프로그래머는 자신이 보고 있는 것이 애플리케이션 객체들의 부분집합임을 모르는 채로 그것을 보게 된다.
- **둘 이상의 공장** → 만들어진 객체에 대한 사무적인 통제가 손상된다.
- **둘 이상의 관리자** → 순차적으로 하려고 했던 동작이 동시에 일어나게 된다.

### 1.2 메커니즘이 필요한가?

이런 객체에게 단일성을 강제하기 위한 메커니즘은 지나친 것으로 보일지도 모른다. 애플리케이션을 초기화할 때 그저 이 객체 중 하나를 생성하고 그것으로 끝내면 되는 것이다. 사실, **이것이 보통 최선의 동작 방법**이다. 급하고 심각할 필요가 없는 경우에는 이 메커니즘을 피해야 한다.

> **핵심 통찰**: 그러나 코드를 우리의 의도에 맞게 만들고 싶은 것도 사실이다. 단일성을 강제하는 메커니즘이 단순하다면, **의도와 맞는다는 이익이 메커니즘에 드는 비용보다 클 것**이다. 이번 장에서는 단일성을 강제하는 두 패턴을 다루는데, 이 패턴들은 비용 대 이익의 균형(*trade-off - 한쪽을 얻기 위해 다른 쪽을 포기해야 하는 관계*)이 매우 다르다.

---

## 2. 싱글톤 패턴

싱글톤은 아주 단순한 패턴이다. 다음 테스트 케이스는 이것이 어떻게 동작하는지를 보여준다.

### 2.1 싱글톤 테스트 케이스

첫 번째 테스트 함수는 공용 정적(public static) 메서드인 `Instance`를 통해 `Singleton` 인스턴스에 접근함을 보여준다. 또 `Instance`가 여러 번 호출되면, 똑같은 인스턴스에 대한 참조값이 매번 반환됨을 보여준다. 두 번째 테스트 케이스는 `Singleton` 클래스가 공용 생성자를 갖고 있지 않기 때문에, `Instance` 메서드를 사용하지 않고서는 인스턴스를 생성할 방법이 없음을 보여준다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java - 목록 16-1: Singleton 테스트 케이스
import java.lang.reflect.Constructor;
import junit.framework.TestCase;

public class TestSimpleSingleton extends TestCase {
    public TestSimpleSingleton(String name) {
        super(name);
    }

    public void testCreateSingleton() {
        Singleton s = Singleton.Instance();
        Singleton s2 = Singleton.Instance();
        assertSame(s, s2);
    }

    public void testNoPublicConstructors() throws Exception {
        Class singleton = Class.forName("Singleton");
        Constructor[] constructors = singleton.getConstructors();
        assertEquals("public constructors.", 0, constructors.length);
    }
}
```

</details>

```typescript
// TypeScript - Singleton 테스트
describe("Singleton", () => {
    test("createSingleton: 여러 번 호출해도 같은 인스턴스 반환", () => {
        const s = Singleton.instance();
        const s2 = Singleton.instance();
        expect(s).toBe(s2);
    });

    test("noPublicConstructors: new로 직접 생성할 수 없음", () => {
        // TypeScript에서는 private 생성자가 컴파일 단계에서 차단됨
        // @ts-expect-error - 'new'는 private 생성자에서 허용되지 않음
        expect(() => new Singleton()).toThrow;
    });
});
```

### 2.2 싱글톤 구현

이 테스트 케이스는 싱글톤 패턴의 구체화이며, 이는 바로 다음 코드로 이어진다. 정적 변수 `Singleton.theInstance`의 유효 범위 안에서는 `Singleton` 클래스의 인스턴스가 2개 이상 있을 수 없음을 분명히 알 수 있다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java - 목록 16-2: Singleton 구현
public class Singleton {
    private static Singleton theInstance = null;

    private Singleton() {
    }

    public static Singleton Instance() {
        if (theInstance == null) {
            theInstance = new Singleton();
        }
        return theInstance;
    }
}
```

</details>

```typescript
// TypeScript - Singleton 구현
class Singleton {
    private static theInstance: Singleton | null = null;

    // private 생성자 - 외부에서 'new Singleton()' 불가
    private constructor() {}

    public static instance(): Singleton {
        if (Singleton.theInstance === null) {
            Singleton.theInstance = new Singleton();
        }
        return Singleton.theInstance;
    }
}
```

> **핵심 통찰**: TypeScript의 `private constructor`는 싱글톤 패턴을 표현할 때 특히 유용하다. 컴파일 단계에서 외부의 `new` 호출을 차단하므로, 자바의 `private` 생성자보다 더 강한 보장을 정적 타입 시스템 안에서 얻을 수 있다.

### 2.3 싱글톤이 주는 이점

- **플랫폼 호환**: 적절한 미들웨어(예: RMI(*Remote Method Invocation - 자바 분산 객체 호출 기술*))를 사용하면, 싱글톤은 많은 JVM과 컴퓨터에서 적용되어 확장될 수 있다.
- **어떤 클래스에도 적용 가능**: 어떤 클래스든 그냥 생성자를 전용(private)으로 만들고 적절한 정적 함수와 변수를 추가하기만 하면 싱글톤 형태로 바꿀 수 있다.
- **파생을 통해 생성 가능**: 주어진 클래스에서 싱글톤인 서브클래스를 만들 수 있다.
- **게으른 처리(*lazy evaluation - 꼭 필요해지기 전까지 처리를 미루는 것*)**: 만약 싱글톤이 사용되지 않는다면, 생성되지도 않는다.

### 2.4 싱글톤의 비용

- **소멸(destruction)이 정의되어 있지 않음**: 싱글톤을 없애거나 사용을 중지하는 좋은 방법은 없다. `theInstance`를 널(null) 처리하는 `decommission` 메서드를 추가한다 해도, 시스템에 있는 다른 모듈은 그 싱글톤 인스턴스에 대한 참조값을 계속 유지하고 있을 수도 있다. 이어서 일어나는 `Instance`에 대한 호출은 다른 인스턴스를 생성하는 결과를 낳고, 2개의 인스턴스가 동시에 존재하게 만든다. 이 문제는 C++에서 특히 두드러진다 — C++에서는 인스턴스가 소멸될 수 있고, 이것은 소멸된 객체에 대한 역참조(dereferencing) 가능성으로 이어진다.
- **상속되지 않음**: 어떤 싱글톤에서 파생된 클래스는 싱글톤이 아니다. 이것이 싱글톤이 되려면 정적 함수와 변수가 추가되어야 한다.
- **효율성**: `Instance`에 대한 각 호출은 `if`문을 실행시킨다. 이 호출 중 대부분의 경우에는 이 `if`문이 쓸모없다.
- **비투명성**: 싱글톤의 사용자는 `Instance` 메서드를 실행해야 하기 때문에 자신이 싱글톤을 사용한다는 사실을 안다.

---

## 3. 동작에 있어서의 싱글톤 — UserDatabase 예제

사용자가 어떤 웹 서버의 보안 영역에 로그인할 수 있게 해주는 웹 기반의 시스템이 있다고 가정해보자. 이런 시스템은 사용자의 이름, 패스워드, 그 밖의 사용자 속성을 포함하는 데이터베이스를 갖는다. 더 나아가 이 데이터베이스에 서드파티(*third-party - 외부 공급자가 제공한*) API를 통해 접근한다고 가정하자.

### 3.1 나쁜 접근: API 직접 사용 확산

어떤 사용자를 읽고 쓰기 위해 필요한 모든 모듈에서 이 데이터베이스에 직접 접근할 수 있다. 그러나 이것은 코드 전체에서 서드파티 API 사용을 확산시키게 되고, 이는 접근이나 구조에 대한 규정을 강제할 수 있는 여지가 없게 만든다.

```
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│Module A│ │Module B│ │Module C│ │Module D│   ← 모든 모듈이 직접 의존
└───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘
    │          │          │          │
    └──────────┴──────────┴──────────┘
                     ▼
              3rd-party API
```

### 3.2 좋은 접근: 퍼사드 + 싱글톤

더 나은 해결책은 퍼사드(*Facade - 복잡한 서브시스템에 대한 단순한 인터페이스를 제공하는 패턴*) 패턴을 사용하여 `User` 객체를 읽고 쓰는 메서드들을 제공하는 `UserDatabase` 클래스를 만드는 것이다. 이 메서드들은 데이터베이스의 서드파티 API에 접근하여, `User` 객체와 데이터베이스의 테이블과 행 사이에 변환 작업을 한다.

`UserDatabase` 내에서는 구조와 접근의 규정을 강제할 수 있다. 예를 들어:

- 어떤 `User` 레코드도 그것이 내용이 있는 `username`(사용자 이름)을 갖고 있지 않다면 쓰기 작업을 하지 못하도록 보장할 수 있다.
- 또는 `User` 레코드에 대한 접근을 직렬화하여, 두 모듈이 동시에 이것을 읽고 쓰지 않도록 보장할 수 있다.

```
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│Module A│ │Module B│ │Module C│ │Module D│
└───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘
    └──────────┴──────────┴──────────┘
                     ▼
            «interface» UserDatabase
                     ▲
                     │ (implements)
            UserDatabaseSource  ← Singleton
                     │
                     ▼
              3rd-party API
```

### 3.3 코드 구현

정적 `instance()` 메서드가 중복 생성을 막기 위한 전통적인 `if`문을 갖고 있지 않다는 점을 주목하자. 그 대신, 자바의 **초기화 기능 요소**(static field 초기화)를 이용한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java - 목록 16-3: UserDatabase 인터페이스
public interface UserDatabase {
    User readUser(String userName);
    void writeUser(User user);
}

// Java - 목록 16-4: UserDatabaseSource 싱글톤
public class UserDatabaseSource implements UserDatabase {
    private static UserDatabase theInstance = new UserDatabaseSource();

    public static UserDatabase instance() {
        return theInstance;
    }

    private UserDatabaseSource() {
    }

    public User readUser(String userName) {
        // 구현 부분
        return null;
    }

    public void writeUser(User user) {
        // 구현 부분
    }
}
```

</details>

```typescript
// TypeScript - UserDatabase 인터페이스
interface UserDatabase {
    readUser(userName: string): User;
    writeUser(user: User): void;
}

// TypeScript - UserDatabaseSource 싱글톤
class UserDatabaseSource implements UserDatabase {
    // 클래스 로딩 시점에 즉시 생성 (eager initialization)
    private static readonly theInstance: UserDatabase = new UserDatabaseSource();

    public static instance(): UserDatabase {
        return UserDatabaseSource.theInstance;
    }

    private constructor() {}

    public readUser(userName: string): User {
        // 구현 부분
        return {} as User;
    }

    public writeUser(user: User): void {
        // 구현 부분
    }
}
```

이것은 싱글톤 패턴의 아주 흔한 사용 형태로서, 모든 데이터베이스 접근이 `UserDatabaseSource`의 단일 인스턴스를 통해 이루어짐을 보장해준다. 이것은 검사(check), 카운터(counter), 락(lock)을 `UserDatabaseSource`에 넣어 먼저 언급된 접근과 구조에 대한 규정을 강제하기 쉽게 해준다.

---

## 4. 모노스테이트 패턴

모노스테이트 패턴은 단일성을 이루기 위한 또 다른 방법으로, 이 패턴은 **완전히 다른 메커니즘**으로 동작한다.

### 4.1 모노스테이트 테스트 케이스

첫 번째 테스트 함수는 단순히 자신의 `x` 변수가 설정되거나 검색될 수 있는 어떤 객체를 나타낸다. 그러나 두 번째 테스트 케이스는 **같은 클래스의 두 인스턴스가 하나인 것처럼 동작**하는 모습을 보여준다. 한 인스턴스의 `x` 변수를 특정 값으로 설정하면, 다른 인스턴스의 `x` 변수를 확인하는 것으로 그 값을 검색할 수 있다. 이는 2개의 인스턴스가 같은 객체의 서로 다른 이름을 갖고 있는 것이다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java - 목록 16-5: Monostate 테스트 케이스
import junit.framework.TestCase;

public class TestMonostate extends TestCase {
    public TestMonostate(String name) {
        super(name);
    }

    public void testInstance() {
        Monostate m = new Monostate();
        for (int x = 0; x < 10; x++) {
            m.setX(x);
            assertEquals(x, m.getX());
        }
    }

    public void testInstancesBehaveAsOne() {
        Monostate m1 = new Monostate();
        Monostate m2 = new Monostate();
        for (int x = 0; x < 10; x++) {
            m1.setX(x);
            assertEquals(x, m2.getX());
        }
    }
}
```

</details>

```typescript
// TypeScript - Monostate 테스트
describe("Monostate", () => {
    test("instance: 단일 인스턴스에서 set/get 동작", () => {
        const m = new Monostate();
        for (let x = 0; x < 10; x++) {
            m.setX(x);
            expect(m.getX()).toBe(x);
        }
    });

    test("instancesBehaveAsOne: 두 인스턴스가 같은 객체처럼 동작", () => {
        const m1 = new Monostate();
        const m2 = new Monostate(); // 새로운 'new'를 막지 않음
        for (let x = 0; x < 10; x++) {
            m1.setX(x);
            expect(m2.getX()).toBe(x); // 다른 인스턴스가 같은 값 공유
        }
    });
});
```

> **핵심 통찰**: `Singleton` 클래스를 이 테스트 케이스에 접목하고 모든 `new Monostate` 부분을 `Singleton.Instance`에 대한 호출로 바꿨더라도, 이 테스트 케이스를 통과한다. 따라서 이 테스트 케이스는 **단일 인스턴스라는 제약을 강제하지 않은 `Singleton`의 행위**를 나타낸다. 두 패턴의 차이는 행위가 아니라 **메커니즘**에 있다.

### 4.2 모노스테이트 구현

어떻게 2개의 인스턴스가 하나의 객체인 것처럼 동작할 수 있을까? 아주 당연하게도, 이것은 2개의 객체가 같은 변수를 공유함을 의미한다. 이는 **모든 변수를 정적으로 만듦으로써** 쉽게 이룰 수 있다.

`itsX` 변수가 정적 변수임을 주목하자. 또, **어떤 메서드도 정적이 아니라는 점**에 주목하자. 나중에 살펴보겠지만 이것은 아주 중요하다(파생 클래스에서 메서드를 오버라이드할 수 있게 해주기 때문이다).

<details>
<summary>원문 Java 코드</summary>

```java
// Java - 목록 16-6: Monostate 구현
public class Monostate {
    private static int itsX = 0;

    public Monostate() {
    }

    public void setX(int x) {
        itsX = x;
    }

    public int getX() {
        return itsX;
    }
}
```

</details>

```typescript
// TypeScript - Monostate 구현
class Monostate {
    private static itsX: number = 0;

    constructor() {}

    public setX(x: number): void {
        Monostate.itsX = x;
    }

    public getX(): number {
        return Monostate.itsX;
    }
}
```

> **Uncle Bob의 경험**: 나는 이것이 아주 특이하게 꼬인 패턴이라는 사실을 알았다. `Monostate`의 인스턴스를 몇 개 만들든지 간에, 이들은 모두 단일 객체인 것처럼 동작한다. 심지어 **데이터를 잃지 않고도 현재 있는 모든 인스턴스를 없애거나 사용을 중지**할 수도 있다.

### 4.3 행위 vs 구조

이 두 패턴의 차이점은 **행위 대 구조의 차이** 중 하나임을 명심하자.

| 패턴 | 단일성을 강제하는 방식 |
|------|-------------------------|
| **Singleton** | **구조적 단일성**을 강제한다. 둘 이상의 인스턴스가 생성되는 것을 막는다 |
| **Monostate** | **구조적 제약을 부여하지 않고도** 단일성이 있는 행위를 강제한다 |

이 차이를 분명히 보려면 — **모노스테이트 테스트 케이스는 `Singleton` 클래스에 대해서도 유효**하지만, **싱글톤 테스트 케이스는 `Monostate` 클래스에 대해 유효하지 않다.**

### 4.4 모노스테이트가 주는 이점

- **투명성**: 모노스테이트의 사용자는 일반 객체의 사용자와 다르게 행동하지 않는다. 사용자는 이 객체가 모노스테이트임을 알 필요가 없다.
- **파생 가능성**: 모노스테이트의 파생 클래스는 모노스테이트다. 사실, 어떤 모노스테이트의 모든 파생 클래스는 같은 모노스테이트의 일부가 된다. 이들은 모두 같은 정적 변수를 공유한다.
- **다형성**: 모노스테이트의 메서드는 정적이 아니기 때문에, 파생 클래스에서 오버라이드될 수 있다. 따라서 서로 다른 파생 클래스는 같은 정적 변수의 집합에 대해 서로 다른 행위를 제공할 수 있다.
- **잘 정의된 생성과 소멸**: 정적인 모노스테이트의 변수는 생성과 소멸 시기가 잘 정의되어 있다.

### 4.5 모노스테이트의 비용

- **변환 불가**: 보통 클래스는 파생을 통해 모노스테이트로 변환될 수 없다.
- **효율성**: 하나의 모노스테이트는 실제 객체이기 때문에 많은 생성과 소멸을 겪을 수 있다. 이 작업은 종종 비용이 꽤 든다.
- **실재함**: 모노스테이트의 변수는 이 모노스테이트가 사용되지 않는다 하더라도 공간을 차지한다.
- **플랫폼 한정**: 한 모노스테이트가 여러 개의 JVM 인스턴스나 여러 개의 플랫폼에서 동작하게 만들 수 없다.

---

## 5. 두 패턴의 비교

| 비교 항목 | Singleton | Monostate |
|-----------|-----------|-----------|
| **단일성 강제 방식** | 구조적 (인스턴스 생성 제한) | 행위적 (변수 공유) |
| **인스턴스 개수** | 0개 또는 1개 (lazy) | 여러 개 가능, 단 모두 같은 상태 |
| **생성자** | private | public (보통 클래스처럼) |
| **변수** | 인스턴스 변수 가능 | **모든 변수가 static** |
| **메서드** | 정적 또는 비정적 | **모든 메서드가 비정적** |
| **사용자에게 투명한가** | 비투명 (`Instance()` 호출 필요) | **투명** (보통 객체처럼 사용) |
| **상속 가능한가** | 파생 클래스는 싱글톤 아님 | **파생 클래스도 모노스테이트** |
| **다형성** | 어려움 | **자연스럽게 지원** |
| **lazy evaluation** | 가능 | 어려움 (정적 변수는 항상 공간 차지) |
| **기존 클래스 변환** | 어떤 클래스도 가능 | 거의 불가 |
| **분산/멀티 JVM** | 미들웨어로 확장 가능 | 플랫폼 한정 |
| **소멸/리셋** | 어려움 (참조 유지 문제) | 잘 정의됨 |

---

## 6. 동작에 있어서의 모노스테이트 — 지하철 개찰구 예제

다음은 지하철 개찰구를 위한 간단한 유한 상태 기계(*finite state machine - 입력에 따라 정해진 상태 간 전이를 수행하는 계산 모델*)를 구현하는 작업이다.

### 6.1 상태 기계 다이어그램

이 개찰구는 `Locked` 상태에서 생명 주기를 시작한다. 다음과 같이 동작한다:

```
            Coin / Unlock, AlarmOff, Deposit
        ┌───────────────────────────────────────────┐
        │                                           ▼
   ┌─────────┐                              ┌────────────┐
   │ Locked  │                              │  Unlocked  │
   └─────────┘                              └────────────┘
        │     ▲                                  │    │
  Pass  │     │ Pass / Lock              Coin /  │    │
  /Alarm│     └──────────────────────────Refund  │    │
        ▼                                        ▼    │
       (alarm)                              (refund)  │
                                                      │
                                  (Unlocked 유지)─────┘
```

| 상태 | 이벤트 | 액션 | 다음 상태 |
|------|--------|------|-----------|
| Locked | Coin | Unlock, AlarmOff, Deposit | Unlocked |
| Locked | Pass | Alarm (무단통과 경보) | Locked |
| Unlocked | Pass | Lock | Locked |
| Unlocked | Coin | Refund (이미 열려있으므로 환불) | Unlocked |

### 6.2 모노스테이트 테스트 케이스

이 테스트 메서드들은 `Turnstile`이 모노스테이트라고 전제한다는 사실에 주목하자. 이 클래스는 **이벤트를 보내고 서로 다른 인스턴스들로부터 질의를 받을 수 있으리라 기대**된다. 이것은 `Turnstile`의 인스턴스가 둘 이상 생기지 않는다면 말이 되는 이야기다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java - 목록 16-7: TestTurnstile (일부)
import junit.framework.TestCase;

public class TestTurnstile extends TestCase {
    public void setup() {
        Turnstile t = new Turnstile();
        t.reset();
    }

    public void testInit() {
        Turnstile t = new Turnstile();
        assertTrue(t.locked());
        assertTrue(!t.alarm());
    }

    public void testCoin() {
        Turnstile t = new Turnstile();
        t.coin();
        Turnstile t1 = new Turnstile();   // 다른 인스턴스에서 상태 조회
        assertTrue(!t1.locked());
        assertTrue(!t1.alarm());
        assertEquals(1, t1.coins());
    }

    public void testCoinAndPass() {
        Turnstile t = new Turnstile();
        t.coin();
        t.pass();
        Turnstile t1 = new Turnstile();
        assertTrue(t1.locked());
        assertEquals("coins", 1, t1.coins());
    }

    public void testTwoCoins() {
        Turnstile t = new Turnstile();
        t.coin();
        t.coin();                          // 두 번째 코인 → 환불
        Turnstile t1 = new Turnstile();
        assertTrue("unlocked", !t1.locked());
        assertEquals("coins", 1, t1.coins());
        assertEquals("refunds", 1, t1.refunds());
    }
}
```

</details>

```typescript
// TypeScript - TestTurnstile
describe("Turnstile (Monostate)", () => {
    beforeEach(() => {
        const t = new Turnstile();
        t.reset();
    });

    test("init: 초기에 locked", () => {
        const t = new Turnstile();
        expect(t.locked()).toBe(true);
        expect(t.alarm()).toBe(false);
    });

    test("coin: 동전 투입 후 다른 인스턴스에서 unlocked 확인", () => {
        const t = new Turnstile();
        t.coin();
        const t1 = new Turnstile();
        expect(t1.locked()).toBe(false);
        expect(t1.coins()).toBe(1);
    });

    test("coinAndPass: 동전 후 통과 시 다시 locked", () => {
        const t = new Turnstile();
        t.coin();
        t.pass();
        const t1 = new Turnstile();
        expect(t1.locked()).toBe(true);
        expect(t1.coins()).toBe(1);
    });

    test("twoCoins: 두 번째 동전은 환불", () => {
        const t = new Turnstile();
        t.coin();
        t.coin();
        const t1 = new Turnstile();
        expect(t1.locked()).toBe(false);
        expect(t1.coins()).toBe(1);
        expect(t1.refunds()).toBe(1);
    });
});
```

### 6.3 Turnstile 구현 — 모노스테이트와 상속의 결합

`Turnstile`의 구현은 다음과 같다. 기반 `Turnstile` 클래스는 2개의 이벤트 함수(`coin`과 `pass`)를 유한 상태 기계의 상태를 표현하는 `Turnstile`의 두 파생 클래스(`Locked`와 `Unlocked`)에 위임한다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java - 목록 16-8: Turnstile
public class Turnstile {
    private static boolean isLocked = true;
    private static boolean isAlarming = false;
    private static int itsCoins = 0;
    private static int itsRefunds = 0;
    protected final static Turnstile LOCKED = new Locked();
    protected final static Turnstile UNLOCKED = new Unlocked();
    protected static Turnstile itsState = LOCKED;

    public void reset() {
        lock(true);
        alarm(false);
        itsCoins = 0;
        itsRefunds = 0;
        itsState = LOCKED;
    }

    public boolean locked()  { return isLocked; }
    public boolean alarm()   { return isAlarming; }
    public int coins()       { return itsCoins; }
    public int refunds()     { return itsRefunds; }

    public void coin()       { itsState.coin(); }
    public void pass()       { itsState.pass(); }

    protected void lock(boolean shouldLock) {
        isLocked = shouldLock;
    }
    protected void alarm(boolean shouldAlarm) {
        isAlarming = shouldAlarm;
    }
    public void deposit() { itsCoins++; }
    public void refund()  { itsRefunds++; }
}

class Locked extends Turnstile {
    public void coin() {
        itsState = UNLOCKED;
        lock(false);
        alarm(false);
        deposit();
    }
    public void pass() {
        alarm(true);
    }
}

class Unlocked extends Turnstile {
    public void coin() {
        refund();
    }
    public void pass() {
        lock(true);
        itsState = LOCKED;
    }
}
```

</details>

```typescript
// TypeScript - Turnstile (Monostate)
class Turnstile {
    private static isLocked: boolean = true;
    private static isAlarming: boolean = false;
    private static itsCoins: number = 0;
    private static itsRefunds: number = 0;

    // forward declaration을 피하기 위해 lazy 초기화
    protected static LOCKED: Turnstile;
    protected static UNLOCKED: Turnstile;
    protected static itsState: Turnstile;

    public reset(): void {
        this.lock(true);
        this.alarm_(false);
        Turnstile.itsCoins = 0;
        Turnstile.itsRefunds = 0;
        Turnstile.itsState = Turnstile.LOCKED;
    }

    public locked():  boolean { return Turnstile.isLocked; }
    public alarm():   boolean { return Turnstile.isAlarming; }
    public coins():   number  { return Turnstile.itsCoins; }
    public refunds(): number  { return Turnstile.itsRefunds; }

    public coin(): void { Turnstile.itsState.coin(); }
    public pass(): void { Turnstile.itsState.pass(); }

    protected lock(shouldLock: boolean): void {
        Turnstile.isLocked = shouldLock;
    }
    protected alarm_(shouldAlarm: boolean): void {
        Turnstile.isAlarming = shouldAlarm;
    }
    public deposit(): void { Turnstile.itsCoins++; }
    public refund():  void { Turnstile.itsRefunds++; }
}

class Locked extends Turnstile {
    public coin(): void {
        Turnstile.itsState = Turnstile.UNLOCKED;
        this.lock(false);
        this.alarm_(false);
        this.deposit();
    }
    public pass(): void {
        this.alarm_(true);
    }
}

class Unlocked extends Turnstile {
    public coin(): void {
        this.refund();
    }
    public pass(): void {
        this.lock(true);
        Turnstile.itsState = Turnstile.LOCKED;
    }
}

// 정적 초기화
Turnstile.LOCKED = new Locked();
Turnstile.UNLOCKED = new Unlocked();
Turnstile.itsState = Turnstile.LOCKED;
```

### 6.4 관습을 따르지 않는 상속

이 예에서 **관습을 따르지 않은 상속 사용**에 신경이 쓰일 것이다. `Unlocked`와 `Locked`가 `Turnstile`로부터 파생되게 하는 것은 일반적인 OO 원칙 위반처럼 보인다.

> **핵심 통찰**: 그러나 `Turnstile`은 모노스테이트이기 때문에, **별도의 인스턴스는 존재하지 않는다**. 따라서 `Unlocked`와 `Locked`는 실제로 별도의 객체가 아니라 **`Turnstile` 추상화의 일부**다. 이들은 `Turnstile`이 접근 권한을 가진 변수와 메서드에 대해 동일한 접근 권한을 갖는다.

이 예는 모노스테이트 패턴의 유용한 기능 몇 가지를 보여준다:
- 모노스테이트 파생 클래스가 **다형적**이 된다는 점
- 이 모노스테이트 파생 클래스 자신들도 **모노스테이트가 된다**는 사실

또 이 예는 때로 **어떤 모노스테이트를 일반 클래스로 바꾸는 일이 얼마나 어려운지**를 보여준다. 이 프로그램의 구조는 `Turnstile`의 모노스테이트적 본질에 강하게 의존하고 있다. 이 유한 상태 기계로 2개 이상의 개찰구를 제어하고자 한다면, 이 코드에는 **많은 리팩토링이 필요**할 것이다.

---

## 7. 자주 하는 실수

| 안티패턴 | 문제 | 해결 |
|----------|------|------|
| **남용된 Singleton** | 단일성이 필요하지 않은데도 전역 접근 편의를 위해 사용 → 전역 변수와 같은 의존성 문제 | 의존성 주입으로 대체. 메인 함수에서 1개 생성하여 전달 |
| **테스트하기 어려운 Singleton** | 상태가 테스트 간에 새어나가서 테스트가 서로 영향을 줌 | `reset()` 메서드 추가 또는 모노스테이트로 전환 |
| **Singleton 상속** | 싱글톤을 상속하면 파생 클래스는 더 이상 싱글톤이 아님 | 정적 함수와 변수를 파생 클래스에도 다시 정의하거나, 모노스테이트로 전환 |
| **C++ Singleton의 dangling pointer** | 소멸된 후 다른 모듈이 참조 유지 → 새 인스턴스 생성 시 두 인스턴스 공존 | 명시적 소멸 금지. 프로그램 수명과 함께 살게 둠 |
| **멀티스레드 race condition** | lazy 초기화의 `if` 검사가 동시 호출에 안전하지 않음 | eager 초기화(static 필드) 또는 동기화 처리 |
| **Monostate를 일반 클래스로 착각** | 사용자가 자신의 인스턴스가 독립적이라고 가정 | 클래스 이름이나 문서로 모노스테이트임을 알리거나, 그냥 사용자에게 투명한 채로 둠 |
| **Monostate로 다중 인스턴스 제어 시도** | "2개 이상의 개찰구"가 필요해지면 모노스테이트는 적합하지 않음 | 처음부터 모노스테이트인지 신중히 판단 |

---

## 8. 설계 원칙

| 원칙 | 설명 |
|------|------|
| **단일성이 진짜 필요한지 의심하라** | `main`에서 하나 만들고 끝내는 것이 보통 최선이다. 메커니즘은 필요할 때만 적용 |
| **구조적 강제 vs 행위적 강제를 구분하라** | 인스턴스 생성을 막아야 한다면 Singleton, 행위만 일관되면 된다면 Monostate |
| **사용자에게 투명한가를 고려하라** | 사용자가 단일성을 알아야 하면 Singleton, 몰라도 되면 Monostate |
| **상속과 다형성이 필요하면 Monostate** | Singleton 상속은 어색하다. 다형적 단일 객체는 Monostate가 자연스럽다 |
| **기존 클래스를 단일성으로 바꿔야 한다면 Singleton** | 어떤 클래스도 private 생성자만 추가하면 Singleton이 된다. Monostate로의 변환은 거의 불가능 |
| **lazy 평가가 필요하면 Singleton** | Monostate의 정적 변수는 사용되지 않아도 공간을 차지한다 |
| **분산 시스템 / 멀티 플랫폼이라면 Singleton** | Monostate는 한 프로세스/JVM 안에서만 동작한다 |

---

## 9. 결론

특정 객체는 단일 인스턴스만 생성해야 한다는 제약을 강제해야 할 때가 종종 있다. 이 장에서는 매우 다른 기법 2개를 소개했다:

- **Singleton**은 인스턴스 생성을 제어하고 제한하기 위해 전용(private) 생성자, 1개의 정적 변수, 1개의 정적 함수를 사용한다.
- **Monostate**는 그저 객체의 모든 변수를 정적으로 만든다.

> **핵심 통찰**: **Singleton**은 파생을 통해 제어하고 싶은 이미 존재하는 클래스가 있을 때, 그리고 접근 권한을 얻기 위해서라면 모두가 `instance()` 메서드를 호출해야 하는 것도 상관없을 때 최선의 선택이다. **Monostate**는 클래스의 본질적 단일성이 사용자에게 투과적이 되도록 하고 싶을 때, 또는 단일 객체의 파생 객체가 다형적이 되게 하고 싶을 때 최선의 선택이다.

---

## 요약

- 단일성이 필요한 객체는 **루트 / 공장 / 관리자** 같은 역할을 한다. 둘 이상이 만들어지면 심각한 논리 실패가 일어난다
- 메커니즘 없이 `main`에서 하나만 만드는 것이 보통 최선 — 메커니즘은 의도를 코드로 표현할 가치가 있을 때만 도입
- **Singleton**: private 생성자 + static 인스턴스 + `instance()` 메서드. **구조적**으로 단일성 강제
- **Monostate**: 모든 필드를 static으로. **행위적**으로 단일성 강제. 사용자는 자신이 모노스테이트를 쓰는지 모름
- Singleton의 이점: 어떤 클래스에도 적용 가능, lazy 평가, 미들웨어로 분산 가능
- Singleton의 비용: 소멸 정의 불가, 상속되지 않음, `if` 검사 오버헤드, 비투명성
- Monostate의 이점: 투명성, 파생 가능성, 다형성, 잘 정의된 생성/소멸
- Monostate의 비용: 일반 클래스를 변환 불가, 정적 변수는 항상 공간 차지, 플랫폼 한정
- **차이는 행위가 아니라 메커니즘** — 모노스테이트 테스트는 싱글톤에서도 통과하지만, 싱글톤 테스트는 모노스테이트에서 실패
- TypeScript의 `private constructor`는 싱글톤 표현에 특히 적합 — 컴파일 단계에서 외부 `new`를 차단
- 단일성이 진짜 필요한지 먼저 의심하라 — 남용된 싱글톤은 위장된 전역 변수다
