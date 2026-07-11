# Chapter 05: The Singleton Pattern (싱글턴 패턴)

## 핵심 질문

- 한 클래스의 인스턴스가 **정확히 하나만** 존재하도록 어떻게 강제할까?
- 전역 변수 대신 싱글턴을 쓰면 무엇이 나은가?
- 멀티스레드 환경에서 싱글턴이 어떻게 깨지고, 어떻게 고치는가?
- (TS/JS 관점) 자바의 복잡한 동기화가 자바스크립트에서는 왜 대부분 불필요한가?

> **참고**: 싱글턴은 클래스 다이어그램에 클래스가 **하나뿐**인 가장 단순한 패턴이지만, "제대로" 구현하기는 의외로 까다롭다.

---

## 1. 싱글턴은 어디에 쓰나

인스턴스가 하나만 있으면 되는(그리고 **둘 이상이면 문제가 생기는**) 객체들이 있다: 스레드 풀, 캐시, 대화상자, 사용자 설정, 레지스트리 설정, 로그 객체, 디바이스 드라이버 등. 이들이 2개 이상이면 동작이 이상해지거나, 자원을 낭비하거나, 결과에 일관성이 없어진다.

> **무엇이든 물어보세요 (Q&A)**
>
> **Q. 그냥 전역 변수를 쓰면 안 되나요?**
> A. 전역 변수는 (1) **게으른 생성(lazy)** 이 안 되고 앱 시작 시 무조건 만들어지며(자원 낭비), (2) 네임스페이스를 어지럽힌다. 싱글턴은 "**하나만 존재**"와 "**전역 접근**"을 모두 제공하면서 게으른 생성도 가능하다.

---

## 2. 고전적인 싱글턴 구현

핵심 재료: **private 생성자** + **정적 변수** + **정적 `getInstance()`**.

- 생성자가 `private`이면 외부에서 `new`로 만들 수 없다(닭이 먼저냐 달걀이 먼저냐 — 인스턴스를 만들려면 인스턴스가 있어야 하는데, `MyClass` 안에서만 생성자를 부를 수 있다).
- 대신 정적 메서드 `getInstance()`로만 인스턴스를 얻는다.

```typescript
class Singleton {
  // 하나뿐인 인스턴스를 저장하는 정적 변수
  private static uniqueInstance: Singleton;

  // private 생성자 — 외부에서 new 불가
  private constructor() {}

  static getInstance(): Singleton {
    // 게으른 생성(lazy instantiation): 필요할 때 처음 만든다
    if (!Singleton.uniqueInstance) {
      Singleton.uniqueInstance = new Singleton();
    }
    return Singleton.uniqueInstance;
  }
}
```

<details>
<summary>Java 원본</summary>

```java
public class Singleton {
    private static Singleton uniqueInstance;

    private Singleton() {}

    public static Singleton getInstance() {
        if (uniqueInstance == null) {          // 게으른 생성
            uniqueInstance = new Singleton();
        }
        return uniqueInstance;
    }
}
```
</details>

> **핵심 통찰**: `getInstance()`가 처음 호출될 때만 인스턴스를 만드는 것을 **게으른 생성(lazy instantiation)** 이라 한다. 자원을 많이 쓰는 객체라면 필요할 때까지 생성을 미룰 수 있어 유용하다.

> **패턴 정의 — 싱글턴 패턴 (Singleton Pattern)**<br>클래스 인스턴스를 하나만 만들고, 그 인스턴스로의 전역 접근을 제공한다.

---

## 3. 초콜릿 보일러 예제와 멀티스레딩 문제

초코홀릭사의 `ChocolateBoiler`는 "빈 보일러에만 재료를 채우고, 다 끓인 것만 배출"하도록 세심하게 만들어졌다. 인스턴스가 2개면 보일러 상태가 어긋나 500갤런의 초콜릿이 넘칠 수 있다. 그래서 싱글턴으로 만들었다.

그런데 **멀티스레드**로 최적화한 뒤 문제가 터졌다.

```
1번 스레드                        2번 스레드                uniqueInstance
getInstance() 진입
if (null) → 참                                             null
                                 getInstance() 진입
                                 if (null) → 참             null   ← 아직 안 만들어짐!
uniqueInstance = new Boiler()                              object1
                                 uniqueInstance = new()     object2 ← 두 번째 인스턴스!
```

두 스레드가 `if (null)`을 **거의 동시에** 통과하면, **인스턴스가 2개** 만들어진다.

> **핵심 통찰**: 이것은 자바처럼 **여러 스레드가 같은 메모리를 공유**하는 언어의 문제다. (뒤에서 보듯 자바스크립트에는 이 문제가 없다.)

---

## 4. 멀티스레딩 해결법 (자바)

### 방법 1 — `getInstance()` 동기화

```java
public static synchronized Singleton getInstance() {
    if (uniqueInstance == null) {
        uniqueInstance = new Singleton();
    }
    return uniqueInstance;
}
```

가장 간단하지만, 매 호출마다 동기화 비용이 든다(성능 최대 100배 저하). 사실 동기화가 필요한 건 **최초 생성 순간뿐**인데도 그렇다. `getInstance()`가 병목이 아니면 그냥 써도 된다.

### 방법 2 — 이른 생성 (eager instantiation)

```java
public class Singleton {
    private static Singleton uniqueInstance = new Singleton(); // 클래스 로딩 시 생성
    private Singleton() {}
    public static Singleton getInstance() {
        return uniqueInstance; // 이미 있으니 반환만
    }
}
```

인스턴스를 어차피 항상 쓴다면, 클래스 로딩 시점에 JVM이 하나만 만들어 주므로 스레드 안전하다.

### 방법 3 — DCL (Double-Checked Locking)

```java
public class Singleton {
    private volatile static Singleton uniqueInstance;
    private Singleton() {}
    public static Singleton getInstance() {
        if (uniqueInstance == null) {              // 1차 확인(동기화 없음)
            synchronized (Singleton.class) {
                if (uniqueInstance == null) {      // 2차 확인(동기화 안에서)
                    uniqueInstance = new Singleton();
                }
            }
        }
        return uniqueInstance;
    }
}
```

최초 생성 때만 동기화하고 이후엔 안 한다. `volatile`이 필수(자바 5+에서만 올바로 동작).

### 가장 좋은 방법 — enum

> **무엇이든 물어보세요 (Q&A)**
>
> **Q. enum으로 싱글턴을 만들 수 있지 않나요?**
> A. 그렇다. 동기화·클래스 로더·리플렉션·직렬화 문제를 **enum이 한 번에 해결**한다. 자바에서 싱글턴이 필요하면 그냥 enum을 쓰면 된다.

```java
public enum Singleton {
    UNIQUE_INSTANCE;
    // 기타 필드/메서드
}
// 사용: Singleton.UNIQUE_INSTANCE
```

---

## 5. TS/JS 관점 — 훨씬 단순하다

> **핵심 통찰**: **자바스크립트는 단일 스레드(이벤트 루프)** 다. 여러 스레드가 `getInstance()`에 동시에 진입하는 일이 없으므로, 4장의 동기화(`synchronized`·DCL·`volatile`)가 **전부 불필요**하다. §2의 게으른 생성 코드만으로 완전히 안전하다.

게다가 **ES 모듈은 최초 import 시 한 번만 평가**되고 그 결과가 캐시된다. 즉 **모듈 스코프의 값 자체가 이미 싱글턴**이다.

```typescript
// chocolateBoiler.ts
class ChocolateBoiler {
  private empty = true;
  private boiled = false;
  fill(): void {
    if (this.empty) {
      this.empty = false;
      this.boiled = false;
    }
  }
  // ...
}

// 모듈은 한 번만 평가되므로, 이 인스턴스는 앱 전체에서 유일하다
export const chocolateBoiler = new ChocolateBoiler();
```

```typescript
// 어디서 import하든 항상 같은 인스턴스
import { chocolateBoiler } from "./chocolateBoiler";
```

> **핵심 통찰**: 프런트엔드에서 "싱글턴"이 필요할 때(예: 전역 스토어, API 클라이언트, 설정 캐시) 보통 **모듈 export**로 충분하다. 클래스 + `getInstance()`는 "게으른 생성이 꼭 필요하거나, 인터페이스로 다뤄야 할 때"만 쓴다.

---

## 6. 싱글턴의 그늘 (남용 주의)

> 패턴 집중 인터뷰 — 싱글턴의 고백<br><br>"저는 진짜 유일한 존재예요. public 생성자가 없거든요. 연결 풀·스레드 풀 관리에 자주 불려 다니죠. 다만... 개발자들이 저를 **남용**하는 게 걱정이에요."

Q&A가 짚는 싱글턴의 약점들:
- **느슨한 결합 위반(원칙 4)**: 싱글턴에 의존하는 객체들이 전부 그 하나의 구상 객체에 **단단히 결합**된다. 싱글턴을 바꾸면 연결된 모두가 영향받는다.
- **단일 책임 위반**: 싱글턴은 "인스턴스 관리"와 "본래 기능" **두 가지**를 책임진다.
- **테스트 어려움**: 전역 상태라 테스트 간 격리가 어렵다(모의 객체 주입이 힘들다).
- **서브클래싱 곤란**: private 생성자 때문에 확장이 어렵다.

> **핵심 통찰**: 싱글턴을 **많이** 쓰고 있다면 설계를 재검토하라. 싱글턴은 특수한 상황의 제한된 도구다. 현대적으로는 **의존성 주입(DI)** 으로 "인스턴스를 하나만 만들되, 그것을 주입"하는 방식이 결합 문제를 피하면서 같은 목적을 달성한다.

---

## 연습 문제 (해답 예시)

**1. `ChocolateBoiler`를 싱글턴으로** — 정적 변수 `uniqueInstance`, private 생성자, 정적 `getInstance()`를 추가한다(§2와 동일 구조).

**2. 인스턴스가 2개면 무슨 문제?** — 두 보일러가 서로의 상태(empty/boiled)를 모른 채 독립 동작해, 한쪽이 "비었다"고 판단해 채우는 사이 다른 쪽이 끓이는 등 **상태 불일치**로 초콜릿이 넘친다.

**3. 세 해결법 중 초콜릿 보일러에 적합한 것** — 보일러는 속도가 중요치 않고 인스턴스를 항상 쓰므로, **동기화(방법 1)** 나 **이른 생성(방법 2)** 이면 충분하다. DCL(방법 3)까지 갈 필요는 없다. (자바 한정 논의 — JS라면 §5로 애초에 문제 없음.)

**4. enum으로 초콜릿 보일러 만들기** — `enum ChocolateBoiler { UNIQUE_INSTANCE; ... }`로 필드와 메서드를 넣으면 가장 간단하고 안전하다.

---

## 디자인 원칙 정리 (누적)

이 장에서는 **새 원칙이 추가되지 않는다**(싱글턴은 원칙보다 구현 기법에 가깝다). 지금까지의 6가지는 다음과 같다.

1. 바뀌는 부분을 캡슐화한다.
2. 구현보다는 인터페이스에 맞춰 프로그래밍한다.
3. 상속보다는 구성을 활용한다.
4. 느슨한 결합을 사용한다. ← 싱글턴이 **위반하기 쉬운** 원칙
5. 확장에는 열려 있고 변경에는 닫혀 있어야 한다 (OCP).
6. 추상화에 의존하고 구상 클래스에 의존하지 않는다 (DIP).

---

## 요약

- **싱글턴 패턴**: 클래스 인스턴스를 하나만 만들고, 그 인스턴스로의 전역 접근을 제공한다.
- 구현 재료: **private 생성자 + 정적 변수 + 정적 `getInstance()`**. 필요 시 **게으른 생성**.
- **자바 멀티스레드**에서는 인스턴스가 2개 생길 수 있어, ①동기화 ②이른 생성 ③DCL, 그리고 가장 깔끔한 **enum**으로 해결한다.
- **자바스크립트는 단일 스레드**라 동기화가 불필요하고, **ES 모듈 export** 자체가 싱글턴 역할을 한다.
- 싱글턴은 **느슨한 결합·단일 책임을 위반**하기 쉽고 테스트를 어렵게 하므로 남용을 피하고, 현대적으로는 **DI**를 고려한다.

---

## 다른 챕터와의 관계

- **4장 팩토리**: 팩토리 객체를 싱글턴으로 두는 경우가 많다(생성 로직의 단일 창구).
- **6장 커맨드 이후**: 여러 패턴에서 관리자/호출자 객체가 하나만 필요할 때 싱글턴이 쓰인다.
- **원칙 4(느슨한 결합)**: 싱글턴은 이 원칙과 **긴장 관계**에 있다 — 편리하지만 결합을 높인다.

---

## 보너스: 원서 복습 요소

### 🧠 뇌 단련 (Brain Power)

1. `ChocolateBoiler` 인스턴스가 2개면 어떤 나쁜 일이? (→ 상태 불일치, 초콜릿 범람)
2. enum으로 초코홀릭 코드를 고쳐 보라. (→ `enum ChocolateBoiler`)

### 🎤 패턴 집중 인터뷰 — 싱글턴의 정체

- public 생성자가 없고, `getInstance()`로만 인스턴스를 얻는다.
- 연결 풀·스레드 풀 관리에 유용하지만 남용은 금물.

### 🍫 리틀 싱글턴 문답 (요지)

- `private` 생성자 → 외부에서 `new` 불가.
- 정적 `getInstance()`는 클래스 이름으로 호출(`Singleton.getInstance()`).
- 둘을 합치면: 클래스 내부에서만 인스턴스를 만들고, 정적 메서드로 그 하나를 나눠 준다.

### 📝 낱말 퀴즈 (정답 단어 모음)

5장 용어들(정답은 영어): INSTANCE(인스턴스), CONSTRUCTOR(생성자), PRIVATE(private), STATICALLY(정적으로), LAZY(게으른), CLASS(클래스), CLASSLOADER(클래스 로더), DOUBLECHECKED(DCL), MULTITHREADING(멀티스레딩), ENUM(enum), GLOBALACCESSPOINT(전역 접근), ITSELF(자신), BOILER(보일러), MILK(우유), HERSHEY(허쉬), CHOC-O-HOLIC(초코홀릭), CAR(자동차).
