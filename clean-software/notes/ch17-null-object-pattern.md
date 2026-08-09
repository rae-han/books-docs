# Chapter 17: The Null Object Pattern (널 오브젝트 패턴)

## 핵심 질문

`null`을 반환하는 함수의 호출자는 왜 매번 `null` 검사를 반복해야 하는가? 그리고 — 검사를 잊었을 때 발생하는 NullPointerException(또는 segfault)을 어떻게 근본적으로 제거할 수 있는가? `null` 대신 "아무 일도 하지 않는 객체"를 반환하면 어떤 일이 일어나는가?

> 너무 흠이 없어 흠이 되고, 시릴 정도로 정확하며, 화려하게 비어 있는, 죽어 있는 완벽함, 그 이상은 없다.<br>— 알프레드 테니슨(Alfred Tennyson), 1809~1892

---

## 1. 문제 — `null` 검사의 관용적 표현

다음과 같은 코드를 보자.

<details>
<summary>원문 Java 코드</summary>

```java
// Java - null 검사의 전형적인 형태
Employee e = DB.getEmployee("Bob");
if (e != null && e.isTimeToPay(today)) {
    e.pay();
}
```

</details>

```typescript
// TypeScript - null 검사의 전형적인 형태
const e: Employee | null = DB.getEmployee("Bob");
if (e !== null && e.isTimeToPay(today)) {
    e.pay();
}
```

이 코드는 데이터베이스에서 "Bob"이라는 이름의 `Employee` 객체를 요청한다. `DB` 객체는 그런 객체가 존재하지 않는 경우 `null`을 반환하고, 존재하는 경우에는 `Employee`의 인스턴스를 반환한다. 이 직원이 존재하고, 그에게 임금을 지급할 시간이라면 `pay` 메서드를 실행한다.

### 1.1 관용적 표현의 문제

C 기반 언어에서는 `&&`의 첫 번째 수식이 먼저 평가되고, 두 번째 수식은 첫 번째가 `true`인 경우에만 평가되므로(*short-circuit evaluation - 논리 연산자가 결과가 결정되면 나머지 피연산자를 평가하지 않는 방식*) 이런 관용적 표현(*idiom - 특정 언어 사용자가 흔히 쓰는 정형화된 표현*)이 흔히 등장한다. 그러나 이 표현은 다음과 같은 문제를 안고 있다.

| 문제 | 결과 |
|------|------|
| **보기 싫음** | 모든 호출 지점마다 `null` 검사 코드가 반복된다 |
| **에러 발생 용이성** | 검사를 잊으면 NullPointerException 또는 segfault 발생 |
| **호출자의 부담** | 호출자가 매번 "이 함수는 `null`을 반환할 수 있다"는 사실을 기억해야 한다 |

> **핵심 통찰**: 우리 중 대부분은 `null` 테스트를 잊어버려서 호되게 당해본 적이 있다. 이런 관용적 표현이 흔하긴 할지라도, **이것은 보기 싫고 에러가 발생하기 쉽다.**

### 1.2 예외(exception)로 대체하는 대안 — 그리고 그 한계

`DB.getEmployee`가 `null`을 반환하는 대신 예외를 발생시키게 하면 에러가 발생할 위험을 감소시킬 수 있다. 그러나:

- `try/catch` 블록은 `null` 검사보다 **더 보기 싫을 수 있다**
- 예외 사용은 `throws` 절(*throws clause - Java에서 메서드가 던질 수 있는 검사 예외를 선언하는 부분*)에 이를 선언하도록 만들어서, **기존 애플리케이션에 예외를 끼워 넣기 어렵다**

---

## 2. 널 오브젝트 패턴 — 우드워드(Woolf)의 해법

널 오브젝트(*Null Object - "아무 일도 하지 않는" 객체로 부재를 표현하는 객체*) 패턴을 사용하면 이런 문제를 해결할 수 있다. 이 패턴은 보비 우드워드(Bobby Woolf)가 *Pattern Languages of Program Design 3* 에서 소개한 것으로, 종종 `null` 검사의 필요를 제거하고 코드를 단순화하는 데 도움이 된다.

### 2.1 구조

```
                ┌─────────────────────────┐
                │     «interface»         │
                │       Employee          │
                ├─────────────────────────┤
                │ + isTimeToPay(d): bool  │
                │ + pay()                 │
                └────────┬────────────────┘
                         ▲
              ┌──────────┴──────────────┐
              │                         │
   ┌──────────┴────────────┐  ┌─────────┴──────────────┐
   │ EmployeeImplementation│  │     NullEmployee       │
   ├───────────────────────┤  ├────────────────────────┤
   │ (일반 구현)           │  │ isTimeToPay → false    │
   │                       │  │ pay() → no-op          │
   └───────────────────────┘  └────────────────────────┘
              ▲                         ▲
              │ «creates»               │ «creates»
              └────────────┬────────────┘
                           │
                       ┌───┴───┐
                       │  DB   │
                       └───────┘
```

`Employee`는 2개의 구현을 가진 인터페이스가 된다.

- `EmployeeImplementation` — 일반적인 구현. `Employee` 객체가 가질 것으로 기대하는 모든 메서드와 변수를 포함한다. `DB.getEmployee`가 데이터베이스에서 어떤 직원을 찾으면 이 클래스의 인스턴스를 반환한다.
- `NullEmployee` — `DB.getEmployee`가 그 직원을 찾지 못했을 경우에만 반환된다. `Employee`의 모든 메서드가 **아무 일도 하지 않도록** 구현한다. "아무 일"이라는 것은 메서드에 달려 있다 — 예를 들어, `isTimeToPay`는 `false`를 반환하게 구현할 수 있다(`NullEmployee`에게 임금을 지급할 시기는 있을 수 없으므로).

### 2.2 적용 후 코드

이 패턴을 적용하면 원래 코드를 다음과 같이 단순화할 수 있다.

<details>
<summary>원문 Java 코드</summary>

```java
// Java - Null Object 적용 후
Employee e = DB.getEmployee("Bob");
if (e.isTimeToPay(today)) {
    e.pay();
}
```

</details>

```typescript
// TypeScript - Null Object 적용 후
const e: Employee = DB.getEmployee("Bob");
if (e.isTimeToPay(today)) {
    e.pay();
}
```

| 변화 | 효과 |
|------|------|
| `null` 검사 제거 | 코드가 단순하고 깨끗해짐 |
| `DB.getEmployee`는 **항상** `Employee` 인스턴스 반환 | 호출자가 "없을 수도 있다"를 기억할 필요 없음 |
| 직원 부재 시 동작은 `NullEmployee`가 책임짐 | 부재 처리 로직이 한 곳에 모임 |

> **핵심 통찰**: 이 코드는 에러가 발생하기 쉬운 것도 아니고 보기 싫지도 않다. 여기에는 멋진 일관성이 있다. `DB.getEmployee`는 항상 `Employee`의 인스턴스를 반환하며, **이 인스턴스는 그 직원을 찾았든 못 찾았든 상관없이 올바른 동작을 하도록 보장된다.**

---

## 3. 부재를 식별해야 할 때 — `Employee.NULL` 정적 변수

물론 `DB.getEmployee`가 어떤 직원을 찾는 데 실패했는지 알고 싶은 경우도 많다. 이 경우 `NullEmployee`의 **유일한 인스턴스**를 저장하는 `Employee`의 정적(`static final`) 변수를 만들 수 있다.

### 3.1 테스트 케이스

<details>
<summary>원문 Java 코드</summary>

```java
// Java - 목록 17-1 TestEmployee.java (일부분)
public void testNull() throws Exception {
    Employee e = DB.getEmployee("Bob");
    if (e.isTimeToPay(new Date())) {
        fail();
    }
    assertEquals(Employee.NULL, e);
}
```

</details>

```typescript
// TypeScript - 테스트 케이스
test("getEmployee returns Employee.NULL when not found", () => {
    const e: Employee = DB.getEmployee("Bob");
    if (e.isTimeToPay(new Date())) {
        fail();
    }
    expect(e).toBe(Employee.NULL);
});
```

이 테스트 케이스에서 "Bob"은 데이터베이스에 존재하지 않는다. 다음 두 가지를 기대한다.

1. `isTimeToPay`가 `false`를 반환
2. `DB.getEmployee`가 반환한 직원이 **`Employee.NULL`과 동일**

### 3.2 DB 구현

<details>
<summary>원문 Java 코드</summary>

```java
// Java - 목록 17-2 DB.java
public class DB {
    public static Employee getEmployee(String name) {
        return Employee.NULL;
    }
}
```

</details>

```typescript
// TypeScript - DB 클래스 (테스트용 스텁)
class DB {
    static getEmployee(name: string): Employee {
        return Employee.NULL;
    }
}
```

테스트의 목적을 위해 `getEmployee` 메서드는 그냥 `Employee.NULL`을 반환한다.

### 3.3 Employee 인터페이스와 익명 구현

<details>
<summary>원문 Java 코드</summary>

```java
// Java - 목록 17-3 Employee.java
import java.util.Date;

public interface Employee {
    public boolean isTimeToPay(Date payDate);
    public void pay();

    public static final Employee NULL = new Employee() {
        public boolean isTimeToPay(Date payDate) {
            return false;
        }
        public void pay() {
        }
    };
}
```

</details>

```typescript
// TypeScript - Employee 인터페이스 + 싱글톤 NULL
interface Employee {
    isTimeToPay(payDate: Date): boolean;
    pay(): void;
}

namespace Employee {
    // 유일한 NullEmployee 인스턴스
    export const NULL: Employee = {
        isTimeToPay(_payDate: Date): boolean {
            return false;
        },
        pay(): void {
            // no-op
        },
    };
}
```

`Employee` 인터페이스가 `NULL`이라는 이름의 정적 변수를 갖고 있음에 주목하자. 이 익명 구현은 "없는 직원"의 유일한 인스턴스다. 구현에서 `isTimeToPay`는 `false`를 반환하고, `pay`는 아무 임금도 지급하지 않는다.

### 3.4 익명 내부 클래스로 만드는 이유 — 싱글톤 보장

없는 직원을 익명 내부 클래스(*anonymous inner class - 이름이 없고 정의 시점에 단 한 번만 인스턴스화되는 클래스*)로 만드는 것은 **이것의 인스턴스가 오직 하나임을 보장하는 방법**이다. 본질적으로 `NullEmployee` 클래스는 외부에서 보면 존재하지 않는 것이다 — 다른 어떤 누구도 "없는 직원"의 다른 인스턴스를 생성할 수 없다.

이는 다음과 같이 표현할 수 있기를 원하기 때문에 바람직한 일이다.

```typescript
if (e === Employee.NULL) {
    // 직원을 찾지 못한 경우의 처리
}
```

> **핵심 통찰**: "없는 직원"의 인스턴스를 여러 개 생성하는 일이 가능하다면 위 표현은 신뢰할 수 없게 된다. **싱글톤성 보장이 부재 식별의 정확성을 받쳐주는 것이다.**

---

## 4. LSP와의 연결 — 다형성으로 부재 다루기

널 오브젝트 패턴이 작동하는 근본 원리는 **리스코프 치환 원칙(LSP)** 이다.

```
┌─────────────────────────────────────────────────────────┐
│ 호출자 코드                                              │
│   const e: Employee = DB.getEmployee("Bob");            │
│   if (e.isTimeToPay(today)) { e.pay(); }                │
└────────────────────┬────────────────────────────────────┘
                     │ Employee 인터페이스에만 의존
                     ▼
        ┌────────────────────────────┐
        │ EmployeeImplementation     │ ← 일반적인 동작
        │ NullEmployee               │ ← "아무 일도 하지 않는" 동작
        └────────────────────────────┘
```

호출자는 **반환된 객체가 어떤 구체 타입인지 알 필요가 없다.** 두 구현 모두 `Employee` 인터페이스의 계약(*contract - 인터페이스가 구현체에 요구하는 동작 명세*)을 만족하므로, 호출자는 어느 쪽이든 동일한 코드로 처리할 수 있다.

이것이 단순한 "if-else"보다 우월한 이유다 — **조건 분기가 객체 다형성으로 대체된다**(*Replace Conditional with Polymorphism - 리팩토링 기법 중 하나*).

---

## 5. 자주 하는 실수와 한계

### 5.1 안티패턴

| 안티패턴 | 문제 | 해결 |
|----------|------|------|
| **NullObject가 silent failure를 감춘다** | 진짜로 에러가 발생했는데 "아무 일도 안 함"으로 처리되어 디버깅이 어려움 | 부재가 정상 흐름인 경우에만 적용. 진짜 에러는 예외로 |
| **NullObject 인스턴스를 여러 개 생성** | `e === Employee.NULL` 비교가 실패 | 싱글톤으로 만들어 유일한 인스턴스 보장 |
| **NullObject가 도메인을 모름** | "아무 일도 안 함"이 도메인에서 잘못된 동작인 경우 | 메서드별로 적절한 "기본값" 결정 (`isTimeToPay → false`처럼) |
| **모든 곳에 무차별 적용** | 어떤 코드는 부재를 명시적으로 알아야 함 | 호출자가 부재를 알아야 할 때는 `Employee.NULL`로 식별 가능하게 노출 |

### 5.2 언제 NULL 대신 예외가 더 좋은가?

> **핵심 통찰**: 부재가 **정상 흐름**(예: 검색 결과 없음, 빈 컬렉션)이면 널 오브젝트가 좋다. 부재가 **계약 위반이나 시스템 오류**(예: 인증 실패, DB 연결 끊김)이면 명시적 예외가 좋다. 모든 실패를 "조용한 객체"로 감싸면 진짜 버그를 숨길 수 있다.

---

## 6. 설계 원칙

| 원칙 | 설명 |
|------|------|
| **null 반환 대신 항상 유효한 객체 반환** | 호출자가 `null` 검사를 잊을 수 없도록 |
| **부재도 객체로 표현하라** | 부재 처리 로직이 NullObject 한 곳에 응집됨 |
| **NullObject는 싱글톤** | 동등성 비교로 부재를 식별할 수 있게 됨 |
| **LSP를 통한 다형성으로 분기 제거** | 조건문이 객체 호출로 대체됨 |
| **silent failure를 감추지 마라** | 정상 흐름의 부재만 NullObject로. 진짜 오류는 예외로 |

---

## 7. 결론

C 기반 언어를 오래 사용해 온 사람들은 어떤 종류의 실패에 대해 `null`이나 `0`을 반환하는 함수에 익숙해서, 이런 함수의 반환값은 검사할 필요가 있다고 생각한다.

> **핵심 통찰**: 널 오브젝트 패턴은 이 생각을 바꾼다. 이 패턴을 사용하면 **함수가 실패한 경우에도 항상 유효한 객체를 반환함을 보장**할 수 있다. 실패를 나타내는 객체들은 아무 일도 하지 않는다.

### 참고 문헌

- Martin, Robert, Dirk Riehle, and Frank Buschmann. *Pattern Languages of Program Design 3*. Reading, MA: Addison-Wesley, 1998.

---

## 요약

- **문제**: `null` 반환 함수는 호출자에게 매번 `null` 검사를 강요하고, 잊으면 NullPointerException으로 이어진다
- **해법**: 인터페이스에 두 구현을 둔다 — 일반 구현(`EmployeeImplementation`)과 "아무 일도 하지 않는" 구현(`NullEmployee`)
- **결과**: 함수는 항상 유효한 객체를 반환하고, 호출자는 `null` 검사 없이 단순한 코드를 작성한다
- **부재 식별**: `Employee.NULL` 정적 변수 + 익명 내부 클래스로 싱글톤 보장 → `e === Employee.NULL` 비교 가능
- **근본 원리**: LSP — NullObject가 정상 객체와 같은 인터페이스를 만족하므로 호출자는 분기 없이 동일하게 처리
- **한계**: 부재가 정상 흐름이면 NullObject, 진짜 시스템 오류면 예외. **silent failure를 감추지 말 것**
- 우드워드(Bobby Woolf)가 *Pattern Languages of Program Design 3*에서 소개한 패턴
