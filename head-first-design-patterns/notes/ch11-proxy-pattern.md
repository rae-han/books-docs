# Chapter 11: The Proxy Pattern (프록시 패턴)

## 핵심 질문

- 진짜 객체에 대한 **접근을 제어**하는 대리인을 어떻게 세울까?
- 원격에 있는 객체·생성 비용이 큰 객체·권한이 필요한 객체를 클라이언트가 **똑같은 인터페이스로** 다루게 하려면?
- 프록시는 데코레이터·어댑터와 무엇이 다른가?
- (TS/JS) 자바스크립트 내장 `Proxy`는 이 패턴과 어떤 관계인가?

> **참고**: 프록시는 **한 인터페이스**로 여러 변종이 있다 — 원격/가상/보호 프록시. 원서는 자바 RMI·동적 프록시로 구현하지만, 이 노트는 **개념과 JS `Proxy`** 에 초점을 맞춘다.

---

## 1. 프록시 패턴의 정의와 구조

> **패턴 정의 — 프록시 패턴 (Proxy Pattern)**<br>특정 객체로의 접근을 제어하는 대리인(그 객체를 대변하는 객체)을 제공한다.

```
       «interface» Subject
        request()
             △
   ┌─────────┴──────────┐
 RealSubject         Proxy ──subject──▶ RealSubject
  request()          request()  (접근 제어 후 위임)
 (진짜 작업)
```

`Proxy`와 `RealSubject`가 **같은 인터페이스**를 구현하므로, 클라이언트는 진짜 객체 대신 프록시를 놓아도 눈치채지 못한다. 프록시는 그 접근을 여러 방식으로 **제어**한다:

- **원격 프록시(Remote Proxy)**: 원격(다른 JVM/프로세스)에 있는 객체로의 접근 제어
- **가상 프록시(Virtual Proxy)**: 생성 비용이 큰 객체로의 접근 제어(지연 생성)
- **보호 프록시(Protection Proxy)**: 접근 권한에 따른 접근 제어

---

## 2. 원격 프록시 — 원격 객체의 로컬 대변자

뽑기 기계를 CEO가 **원격으로 모니터링**하려 한다. `GumballMonitor`(클라이언트)는 로컬의 **프록시(스텁)** 를 진짜 뽑기 기계로 알고 메서드를 호출하지만, 실제로는 네트워크로 원격 뽑기 기계(스켈레톤)와 통신한다.

```
 [CEO 데스크톱]                        [원격 뽑기 기계]
 GumballMonitor ─▶ 프록시(스텁) ══네트워크══▶ 스켈레톤 ─▶ GumballMachine
                  getState()                          getState()
```

> **핵심 통찰**: 원격 프록시는 "메서드 호출을 받아 네트워크로 전달하고, 결과를 받아 반환"하는 **로컬 대변자**다. 클라이언트는 원격 호출임을 (예외 처리를 빼면) 몰라도 된다. 자바에서는 **RMI**(스텁=클라이언트 보조, 스켈레톤=서비스 보조)가 이 배관을 자동 생성한다.

```typescript
// TS/JS에서 원격 프록시의 정신 — 같은 인터페이스로 네트워크 호출을 감춘다
interface GumballMachineRemote {
  getCount(): Promise<number>;
  getLocation(): Promise<string>;
  getState(): Promise<string>;
}

/** 원격 뽑기 기계의 로컬 프록시 — HTTP 호출을 감춘다. */
class GumballMachineProxy implements GumballMachineRemote {
  constructor(private baseUrl: string) {}
  async getCount(): Promise<number> {
    const res = await fetch(`${this.baseUrl}/count`); // 네트워크로 전달
    return res.json();
  }
  async getLocation(): Promise<string> {
    return (await fetch(`${this.baseUrl}/location`)).json();
  }
  async getState(): Promise<string> {
    return (await fetch(`${this.baseUrl}/state`)).json();
  }
}
```

> RPC 클라이언트, tRPC/gRPC 스텁, GraphQL 클라이언트가 모두 원격 프록시다 — 로컬 메서드 호출처럼 보이지만 네트워크 뒤의 객체를 대변한다.

---

## 3. 가상 프록시 — 비싼 객체를 지연 생성

앨범 커버 뷰어: 커버 이미지를 네트워크로 받아오는 동안 UI가 멈추면 안 되고, "불러오는 중…" 메시지를 보여줘야 한다. **`ImageProxy`** 가 진짜 `ImageIcon` 대신 나서서, 이미지가 준비되기 전엔 메시지를, 준비되면 실제 이미지를 그린다.

```typescript
interface Icon {
  getIconWidth(): number;
  getIconHeight(): number;
  paint(ctx: CanvasRenderingContext2D): void;
}

/** 가상 프록시 — 비싼 이미지 로딩을 지연하고, 로딩 중엔 대체 화면을 보여준다. */
class ImageProxy implements Icon {
  private realIcon: ImageIcon | null = null; // 아직 없음
  private loading = false;

  constructor(private url: string) {}

  getIconWidth(): number {
    return this.realIcon ? this.realIcon.getIconWidth() : 800; // 로딩 전 기본값
  }
  getIconHeight(): number {
    return this.realIcon ? this.realIcon.getIconHeight() : 600;
  }

  paint(ctx: CanvasRenderingContext2D): void {
    if (this.realIcon) {
      this.realIcon.paint(ctx); // 준비됐으면 진짜 아이콘에 위임
    } else {
      ctx.fillText("앨범 커버를 불러오는 중입니다. 잠시만 기다려 주세요.", 300, 190);
      if (!this.loading) {
        this.loading = true;
        // 비동기로 로딩 (UI 블로킹 방지)
        loadImage(this.url).then((icon) => {
          this.realIcon = icon;
          requestRepaint();
        });
      }
    }
  }
}
```

<details>
<summary>Java 원본 (ImageProxy.paintIcon 핵심)</summary>

```java
public void paintIcon(final Component c, Graphics g, int x, int y) {
    if (imageIcon != null) {
        imageIcon.paintIcon(c, g, x, y); // 준비됐으면 위임
    } else {
        g.drawString("앨범 커버를 불러오는 중입니다...", x + 300, y + 190);
        if (!retrieving) {
            retrieving = true;
            retrievalThread = new Thread(() -> { // 별도 스레드로 로딩
                setImageIcon(new ImageIcon(imageURL, "Album Cover"));
                c.repaint();
            });
            retrievalThread.start();
        }
    }
}
```
</details>

> **핵심 통찰**: 가상 프록시는 **진짜 객체 생성을 실제로 필요할 때까지 미룬다(lazy)**. 생성 전/중에는 프록시가 대신 응답하고, 생성이 끝나면 진짜 객체에 위임한다. 이미지 지연 로딩, ORM의 지연 로딩(lazy loading), `React.lazy`가 같은 발상이다. **캐싱 프록시(Caching Proxy)** 는 이미 만든 객체를 캐시에 저장해 재사용하는 변종이다.

---

## 4. 보호 프록시 — 권한 기반 접근 제어

데이팅 서비스에서 "자기 정보는 수정 가능하지만 남의 정보는 수정 불가, 선호도 점수는 남만 매길 수 있음" 같은 규칙을 강제한다. **보호 프록시**는 호출자의 권한(역할)에 따라 **일부 메서드 호출만 허용**한다.

자바는 `java.lang.reflect.Proxy`로 **동적 프록시(dynamic proxy)** 를 만든다 — 실행 중에 프록시 클래스를 생성하고, 모든 호출을 `InvocationHandler.invoke()`가 가로채 권한을 검사한다.

```java
// 자바 동적 프록시: InvocationHandler가 호출을 가로챈다
class OwnerInvocationHandler implements InvocationHandler {
    Person person;
    public Object invoke(Object proxy, Method method, Object[] args) throws ... {
        if (method.getName().startsWith("get")) {
            return method.invoke(person, args);       // 조회는 허용
        } else if (method.getName().equals("setGeekRating")) {
            throw new IllegalAccessException();        // 본인은 자기 점수 못 매김
        } else if (method.getName().startsWith("set")) {
            return method.invoke(person, args);        // 본인 정보 수정은 허용
        }
        return null;
    }
}
```

---

## 5. TS/JS 관점 — 언어에 내장된 `Proxy`

> **핵심 통찰**: 자바스크립트는 **`Proxy`가 언어에 내장**되어 있다(ES6). `new Proxy(target, handler)` 로 대상 객체의 모든 연산(`get`/`set`/`has`/`apply` 등)을 **트랩(trap)** 으로 가로챌 수 있어, 자바의 동적 프록시와 정확히 같은 일을 훨씬 간단히 한다.

```typescript
interface Person {
  name: string;
  geekRating: number;
  setGeekRating(r: number): void;
}

/** 보호 프록시 — 본인은 자기 점수를 못 매기게 막는다. */
function createOwnerProxy(person: Person): Person {
  return new Proxy(person, {
    get(target, prop, receiver) {
      if (prop === "setGeekRating") {
        // 본인은 자기 점수 조작 불가
        return () => { throw new Error("자신의 괴짜 지수는 매길 수 없습니다."); };
      }
      return Reflect.get(target, prop, receiver);
    },
    set(target, prop, value, receiver) {
      // 본인 정보 수정은 허용
      return Reflect.set(target, prop, value, receiver);
    },
  });
}
```

`Proxy`는 실전에서 **가상 프록시(지연/캐싱)**, **검증/불변 객체**, **관찰(Vue 3의 반응성)**, **음수 인덱스 배열** 등 다양하게 쓰인다.

```typescript
// 가상(지연) 프록시: 처음 접근할 때 비싼 객체를 만든다
function lazy<T extends object>(factory: () => T): T {
  let instance: T | null = null;
  return new Proxy({} as T, {
    get(_t, prop, receiver) {
      if (!instance) { instance = factory(); } // 최초 접근 시 생성
      return Reflect.get(instance, prop, receiver);
    },
  });
}
```

> **핵심 통찰**: 자바에서는 RMI·리플렉션·`InvocationHandler`로 힘겹게 만드는 것을, JS는 **`Proxy` + `Reflect`** 로 선언적으로 해결한다. Vue 3의 반응성 시스템, MobX, immer가 모두 `Proxy` 기반이다.

---

## 6. 프록시 vs 데코레이터 vs 어댑터

> 방구석 토크 — 프록시와 데코레이터의 신경전<br><br>**데코레이터**: 프록시 너, 나랑 똑같이 객체를 감싸잖아. 내 아이디어 훔친 거 아냐?<br>**프록시**: 나는 **접근을 제어**하고 **주제를 대변**해. 원격 프록시는 감쌀 객체가 아예 다른 시스템에 있고, 가상 프록시는 진짜 객체가 **아직 존재하지도 않아**(내가 생성하지). 너는 그냥 **기능을 덧붙일** 뿐이잖아.

| 패턴 | 목적 | 대상 객체 |
|------|------|----------|
| **데코레이터**(3장) | 책임(기능)을 **추가** | 이미 존재하는 객체를 감쌈 |
| **어댑터**(7장) | 인터페이스를 **변환** | 다른 인터페이스의 객체 |
| **프록시**(이 장) | 접근을 **제어**/대변 | 원격·미생성·보호 대상 객체(프록시가 생성하기도) |

> **핵심 통찰**: 셋 다 "감싸기"지만 목적이 다르다 — 데코레이터=기능 추가, 어댑터=인터페이스 변환, 프록시=**접근 제어**(인터페이스는 유지). 프록시는 진짜 객체를 **직접 생성/관리**하기도 한다(가상 프록시).

---

## 연습 문제 (해답 예시)

**1. `ImageProxy`의 2가지 상태를 깔끔하게** — `imageIcon`이 있냐 없냐로 분기하는 조건문이 곳곳에 있다. **상태 패턴(10장)** 으로 "로딩 중 상태"와 "로딩 완료 상태"를 분리하면 조건문을 없앨 수 있다.

**2. `ImageProxy`가 데코레이터 아닌가?** — 겉보기엔 감싸기지만, 목적이 **`ImageIcon`으로의 접근 제어**다(로딩 완료 전까지 대체 화면을 보여주며 분리). 데코레이터는 기능 추가가 목적이다.

**3. 클라이언트가 프록시를 쓰게 만드는 법** — **팩토리**가 진짜 객체를 프록시로 감싸서 반환하면, 클라이언트는 프록시인지 진짜인지 모른 채 사용한다.

**4. 캐싱 프록시** — 이미 로딩한 이미지를 캐시에 저장했다가 재요청 시 캐시본을 반환하는 가상 프록시의 변종.

---

## 디자인 원칙 정리 (누적)

이 장에서는 **새 원칙이 추가되지 않는다**. 1~9번 원칙(캡슐화·인터페이스·구성·느슨한 결합·OCP·DIP·최소 지식·할리우드·단일 책임)이 그대로 적용된다. 프록시는 특히 클라이언트와 진짜 객체를 **분리**(느슨한 결합)한다.

---

## 요약

- **프록시 패턴**은 진짜 객체(RealSubject)와 **같은 인터페이스**로 그 객체로의 **접근을 제어**하는 대리인을 제공한다.
- **원격 프록시**(다른 프로세스의 객체 대변, RMI/RPC), **가상 프록시**(비싼 객체 지연 생성/캐싱), **보호 프록시**(권한 기반 접근 제어)가 대표 변종이다.
- 자바는 원격 프록시에 **RMI**, 보호 프록시에 **동적 프록시(`InvocationHandler`)** 를 쓴다.
- **자바스크립트는 `Proxy`를 내장**해, `get`/`set` 등 연산을 트랩으로 가로채 보호·가상·관찰 프록시를 간단히 만든다(Vue 반응성, MobX, immer의 기반).
- 데코레이터(기능 추가)·어댑터(인터페이스 변환)와 달리 프록시는 **접근 제어**가 목적이다.

---

## 다른 챕터와의 관계

- **3장 데코레이터 · 7장 어댑터**: 셋 다 감싸기 패턴 — 목적으로 구분(위 비교표).
- **10장 상태**: `ImageProxy`의 로딩 상태 분기를 상태 패턴으로 정리할 수 있다.
- **4장 팩토리**: 팩토리로 진짜 객체를 프록시로 감싸 반환하는 것이 흔한 조합이다.

---

## 보너스: 원서 복습 요소

### 🎬 5분 드라마 — 보호 프록시(매니저)

닷컴 시절, 개발자(주제)에게 스카우트 전화가 오면 **매니저**가 먼저 받아 "조건이 어떻게 되죠?"라며 접근을 제어한다 — 매니저가 곧 보호 프록시.

### 🎙️ 방구석 토크 — 프록시 vs 데코레이터

- 데코레이터: 객체를 감싸 **기능 추가**, 진짜 객체는 이미 존재.
- 프록시: **접근 제어/대변**. 원격은 다른 시스템, 가상은 진짜 객체가 아직 없음(프록시가 생성).

### 🐾 프록시 동물원 (변종 카탈로그)

원격·가상·보호 외에도: **캐싱 프록시**(결과 캐시), **방화벽 프록시**(네트워크 접근 제어), **스마트 레퍼런스 프록시**(참조 수 관리 등 부가 작업), **동기화 프록시**(멀티스레드 안전 접근), **복잡도 숨김 프록시**(퍼사드 프록시), **지연 복사 프록시**(copy-on-write) 등.

### 📝 낱말 퀴즈 (정답 단어 모음)

11장 용어들(정답은 영어): PROXY(프록시), REMOTE(원격), VIRTUAL(가상), PROTECTION(보호), SUBJECT(주제), REALSUBJECT(진짜 주제), STUB(스텁), SKELETON(스켈레톤), RMI, INVOCATIONHANDLER(호출 핸들러), SERIALIZABLE(직렬화 가능), DYNAMICPROXY(동적 프록시), CACHING(캐싱), GUMBALL(뽑기).
