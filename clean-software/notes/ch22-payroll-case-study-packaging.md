# Chapter 22: Payroll Case Study Part 2: Packaging (급여 관리 사례 연구 2부: 패키징)

## 핵심 질문

3,280줄의 코드와 50개 클래스를 100개 소스 파일에 흩뿌려놓은 상태에서, 여러 개발자가 동시에 작업할 수 있도록 어떻게 패키지로 분할해야 하는가? 20장에서 배운 패키지 원칙(REP, CCP, CRP, ADP, SDP, SAP)을 실제 시스템에 적용하면 어떤 구조가 나오며, 측정값(A, I, D)으로 그 구조를 어떻게 검증하는가?

> 경험상의 규칙: 어떤 것이 영리하고 정교하다고 생각된다면, 조심해라. 그 생각이 여러분의 방종일 가능성이 크다.<br>— Donald A. Norman, 『The Design of Everyday Things』 (1990)

---

## 1. 패키징의 필요성

18~19장에서 설계한 급여 관리 시스템은 **하나의 디렉토리에 모든 파일이 평평하게 놓인 상태**다. 프로그래머가 한 명일 때는 괜찮지만, 팀이 커지면 다음과 같은 문제가 생긴다:

| 문제 | 결과 |
|------|------|
| **체크아웃 충돌** | 여러 개발자가 동시에 같은 파일을 수정 |
| **릴리즈 단위 부재** | 변경 1줄에도 전체 애플리케이션을 재배포 |
| **변경 영향 분석 불가** | 어떤 변경이 어떤 부분에 영향을 끼치는지 추적 불가 |
| **재사용 단위 부재** | "이 부분만 가져다 쓰고 싶다"가 불가능 |

> **핵심 통찰**: 패키지는 단순히 파일을 묶는 폴더가 아니라 **릴리즈/배포/재사용/변경 격리의 최소 단위**다. 50개 클래스를 어떻게 8개 패키지로 묶느냐에 따라 개발 환경의 안정성이 결정된다.

---

## 2. 첫 번째 시도 — "비슷한 것끼리" 묶기 (안티패턴)

### 2.1 직관적 분류

처음에는 클래스 이름이 비슷한 것끼리 패키지로 묶었다.

```
┌─────────────────────────────────────────────────┐
│            PayrollApplication                   │
│  - PayrollApplication                           │
│  - TransactionSource                            │
│  - TextParserTransactionSource                  │
└──────────────┬──────────────────────────────────┘
               │
               ▼
        ┌──────────────┐
        │ Transactions │
        │  (모든 트랜잭션 클래스 계층)
        └──────┬───────┘
               │
               ▼
   ┌─────────────────────────────────────┐
   │           PayrollDatabase           │
   └──┬────────┬─────────┬──────────┬────┘
      │        │         │          │
      ▼        ▼         ▼          ▼
   Methods Schedules Classifications Affiliations
   (구체적 정책 클래스들)
```

### 2.2 무엇이 잘못되었는가?

`Classifications` 패키지가 변경된다고 가정해 보자.

- `PayrollDatabase` 재컴파일/재테스트 — 합리적
- `Transactions` 재컴파일/재테스트 — **불합리** (왜 모든 트랜잭션을 다시 테스트해야 하는가?)

핵심 문제는 `Transactions` 패키지 내부 클래스들이 **동일한 변경에 동일하게 폐쇄(closed)되어 있지 않다**는 점이다:

| 트랜잭션 클래스 | 민감한 변경 |
|----------------|------------|
| `ServiceChargeTransaction` | `ServiceCharge` 클래스 변경 |
| `TimeCardTransaction` | `TimeCard` 클래스 변경 |
| `ChangeClassificationTransaction` | `Classification` 클래스 변경 |

> **핵심 통찰**: `Transactions` 패키지는 시스템의 거의 모든 변경에 영향을 받으므로 **재릴리즈 횟수가 폭발적**이다. `PayrollApplication`은 더 심각해서 어떤 변경에도 재릴리즈된다. CCP(*Common Closure Principle - 함께 변경되는 클래스끼리 묶는다*)를 위반한 결과다.

---

## 3. CCP 적용 — 변경 폐쇄로 다시 묶기

### 3.1 변경 축에 따른 재패키징

각 트랜잭션을 자기가 다루는 도메인 클래스와 **같은 패키지**에 두면, 변경의 영향이 그 패키지 안에 갇힌다.

```
       ┌─────────────────────┐
       │     TextParser      │  (가장 의존적, 가장 구체적)
       │  TransactionSource  │
       └──────────┬──────────┘
                  ▼
       ┌─────────────────────┐
       │  PayrollApplication │
       └──────────┬──────────┘
                  ▼
   ┌──────────┬──┴──┬───────────┬──────────────┐
   ▼          ▼     ▼           ▼              ▼
Classifications Methods Schedules Affiliations
 + 자기 Transaction 들이 같이 들어감
   │          │     │           │
   └──────────┴─────┴───────────┘
                  │
                  ▼
       ┌─────────────────────┐
       │    PayrollDomain    │  ← 모든 추상화 (Employee, PaymentClassification, ...)
       └─────────────────────┘   (가장 일반적, 아무에게도 의존하지 않음)
                  ▲
                  │
       ┌─────────────────────┐
       │   PayrollDatabase   │
       └─────────────────────┘
```

### 3.2 거꾸로 뒤집힌 구조

이 구조의 핵심은 **DIP(*Dependency Inversion Principle - 추상에 의존, 구체에 의존하지 않는다*)에 의해 의존성이 뒤집혀 있다**는 점이다.

- `PayrollDomain` 패키지는 **시스템의 핵심**이지만 **아무에게도 의존하지 않는다**
- `Classifications` 같은 구체적 패키지는 `PayrollDomain`의 추상에 의존

| 위치 | 패키지 특성 | 변경 영향 |
|------|-------------|----------|
| 아래쪽 (베이스) | **일반적·추상적·독립적·책임 있음** (의존받음) | 변경 시 위쪽 전체에 영향 |
| 위쪽 (상위) | **세부적·구체적·의존적·책임 없음** | 변경이 자기 안에 갇힘 |

> **핵심 통찰**: 객체지향 설계의 특징은 **구조가 거꾸로 뒤집힌다**는 것이다. 절차적 설계에서는 메인이 위에 있고 세부가 아래에 있지만, OOD에서는 추상이 아래에 있고 구체가 위에 있다. **세부적인 것들이 아키텍처적인 결정에 의존**하지, 아키텍처가 세부에 의존하지 않는다. 후자는 SAP(*Stable Abstractions Principle - 안정된 패키지는 추상적이어야 한다*) 위반이다.

---

## 4. REP/CRP 적용 — 재사용 단위 분리

### 4.1 재사용의 최소 단위는 패키지다

> 어떤 패키지에 들어 있는 클래스 하나만 재사용되는 경우는 극히 드물다. 클래스들은 응집력이 있어야 하기 때문에 — 서로 의존하므로 떼어내기 어렵거나, 떼어내는 일이 합리적이지 않다. `Employee` 클래스를 쓰는데 `PaymentMethod`를 쓰지 않는 것은 말이 되지 않는다.

### 4.2 CRP 위반 — `PayrollDomain` 안의 `Transaction`

`PayrollDomain` 패키지에는 `Employee`, `PaymentClassification`, `PaymentMethod`, `PaymentSchedule`, `Affiliation`과 함께 `Transaction`이 들어 있다. 그러나:

- `Employee`만 사용하고 `Transaction`은 쓰지 않는 애플리케이션을 충분히 상상할 수 있다 (예: 직원 데이터베이스 분석 도구)
- 즉 `Transaction`은 `PayrollDomain` 나머지와 **함께 재사용될 이유가 없다** → CRP(*Common Reuse Principle - 함께 재사용되는 클래스끼리 묶는다*) 위반

### 4.3 트랜잭션 추상 레이어 분리

```
        ┌──────────────────────┐
        │ TransactionApplication│  ← Transaction, TransactionSource,
        │                       │     TransactionApplication 의 3개 클래스
        └───────────┬──────────┘
                    │
                    ▼
        ┌──────────────────────┐
        │    PayrollDomain     │  ← Transaction 빠진 순수 도메인
        │  Employee, Payment*, │
        │  Affiliation         │
        └──────────────────────┘
```

- `PayrollDomain`은 이제 `Transaction` 없이 재사용 가능
- `TransactionApplication`은 **어떤 종류의 트랜잭션이든 받아 실행하는 일반 프레임워크**로 재사용 가능

### 4.4 트레이드오프

이 변경은 **패키지 수를 늘리고 의존성 아키텍처를 복잡하게** 만든다.

| 상황 | 권장 |
|------|------|
| 애플리케이션이 안정적이고 재사용 클라이언트가 적음 | **현재 구조 유지** — 과도한 분리 |
| 재사용 클라이언트가 많고 잦은 변경이 예상됨 | **새 구조 채택** |

> **Uncle Bob의 경험**: 처음에는 간단하게 시작하고 필요에 따라 패키지 구조를 발전시키는 것이 가장 좋다. 패키지 구조는 필요하다면 언제든지 더욱 정교하게 만들 수 있기 때문이다. 추측보다는 **자료에 바탕을 두고** 결정해야 한다.

---

## 5. 결합과 캡슐화 — 패키지 전용 클래스

### 5.1 일부 클래스 숨기기

`Classifications` 패키지 안에는 `HourlyClassification`, `CommissionedClassification`, `SalariedClassification`(공용)과 `TimeCard`, `SalesReceipt`(전용)이 들어 있다.

```
┌────────────────────────────────────────┐
│         Classifications                │
│  ┌──────────────────────────────────┐  │
│  │ + HourlyClassification (export)  │  │
│  │ + CommissionedClassification     │  │
│  │ + SalariedClassification         │  │
│  │ - TimeCard       (private)       │  │
│  │ - SalesReceipt   (private)       │  │
│  └──────────────────────────────────┘  │
└────────────────────────────────────────┘
```

### 5.2 왜 숨기는가?

`TimeCard`와 `SalesReceipt`는 **직원 월급 계산 메커니즘의 세부 구현**이다. 이 세부를 자유롭게 고치려면 외부에서 의존하지 못하게 해야 한다.

> **핵심 통찰**: 패키지 내부 클래스 숨기기는 **들어오는 결합(Ca)을 제한**하기 위한 도구다. 클래스 수준의 `private`처럼, 패키지 수준에서도 캡슐화 경계를 그려서 변경의 자유를 확보한다.

---

## 6. 측정법 — 패키지 품질 정량화

> **Uncle Bob의 경험**: 톰 드마르코의 말을 빌리면 "측정하지 못한다면 통제할 수도 없다." 측정값을 자동 계산해 주는 도구도 여러 개 있으며, 손으로 직접 계산하기도 그렇게 어렵지 않다. 1994년부터 여러 프로젝트에 성공적으로 적용된 측정법이다.

### 6.1 핵심 측정값 6개

| 측정값 | 약자 | 공식 | 의미 |
|--------|------|------|------|
| **관계 응집도** | H | (R + 1) / N | 패키지 내부 클래스 간 관계 밀도 |
| **들어오는 결합** | Ca | (count) | 이 패키지에 의존하는 외부 클래스 수 |
| **나가는 결합** | Ce | (count) | 이 패키지가 의존하는 외부 클래스 수 |
| **추상도** | A | 추상 클래스 / 전체 클래스 | 0(구체) ~ 1(추상) |
| **불안정도** | I | Ce / (Ca + Ce) | 0(안정) ~ 1(불안정) |
| **주계열로부터의 거리** | D' | \|A + I − 1\| | 0(이상) ~ 1(최악) |

- R = 패키지 내부로 한정된 클래스 관계 수
- N = 패키지 내 클래스 수
- N=1일 때 H=0이 되는 것을 막기 위해 +1

### 6.2 주계열(Main Sequence)

```
     A
     1 ┤●──── 주계열: A + I = 1
       │ ●●
       │   ●●
       │     ●●●  ← 이상적인 패키지가 놓이는 직선
       │       ●●●
       │         ●●●
       │           ●●●
     0 ┤─────────────●
       0           1   I

         좋은 위치       나쁜 위치
   안정+추상 (A=1,I=0)  안정+구체 (A=0,I=0) — 경직
   불안정+구체 (A=0,I=1) 불안정+추상 (A=1,I=1) — 무용
```

> **핵심 통찰**: **안정될수록 추상적이어야 하고, 구체적일수록 불안정해야 한다.** 안정된 구체 패키지(`A=0, I=0`)는 변경이 불가능하면서 변경 요구만 많은 "경직 지대"고, 불안정 추상 패키지(`A=1, I=1`)는 추상화해 놓고 아무도 안 쓰는 "무용 지대"다.

---

## 7. 측정값 분석 — 첫 시도의 문제 진단

CCP/CRP를 적용한 두 번째 패키지 구조에 측정값을 적용해 봤더니, 다음과 같은 결과가 나왔다.

| 패키지 | A | I | D' | 평가 |
|--------|---|---|------|------|
| `PayrollDomain` | .80 | .14 | .20 | 양호 (추상+안정) |
| `PayrollApplication` | 0 | 1 | 0 | 양호 (구체+불안정) |
| `PayrollDatabase` | 1 | .06 | .08 | 양호 |
| `Classifications` | 0 | .51 | .73 | **나쁨** — 주계열에서 매우 멀다 |
| `Methods` | 0 | .57 | .80 | **나쁨** |
| `Schedules` | 0 | .67 | .86 | **나쁨** |

`Classifications`, `Methods`, `Schedules`는 **구체적인데 들어오는 결합도 많아서** 변경에 민감한 상황이 된다.

### 7.1 진단

- `ClassificationTransactions` 같은 구체 패키지가 `Classifications` 같은 다른 구체 패키지에 의존
- 구체 클래스는 변경 가능성이 큰데, 변경되면 의존 패키지가 모두 재릴리즈됨
- → 의존성 사슬 전체가 흔들린다

---

## 8. 객체 팩토리로 의존성 끊기

### 8.1 원인 — 인스턴스화가 의존을 만든다

`TextParserTransactionSource`가 `AddHourlyEmployeeTransaction` 객체를 직접 `new`로 생성해야 하기 때문에, `TextParser` 패키지는 모든 구체 트랜잭션 패키지에 의존하게 된다.

> 하지만 일단 생성된 후 이 객체들은 **거의 대부분 추상 인터페이스를 통해서만 사용된다**. 그러므로 객체를 만들어야 할 필요만 없다면 들어오는 결합은 사라질 것이다.

### 8.2 FACTORY 패턴 적용

```
┌─────────────────────────────────────┐
│      TransactionFactory  (추상)     │
│  + makeAddHourlyTransaction(): ...  │
│  + makeAddSalariedTransaction(): ...│
│  + makeTimecardTransaction(): ...   │
│  ... (모든 트랜잭션 생성 함수)       │
└─────────────────▲───────────────────┘
                  │ implements
                  │
┌─────────────────┴─────────────────────┐
│  TransactionFactoryImplementation     │
│  (Transaction Implementation 패키지)  │
└───────────────────────────────────────┘
```

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public interface TransactionFactory {
    Transaction makeAddHourlyTransaction(int empId, String name, double rate);
    Transaction makeTimecardTransaction(int empId, Date date, double hours);
    Transaction makePaydayTransaction(Date date);
    // ...

    static TransactionFactory transactionFactory;  // 메인에서 주입
}

public class TransactionFactoryImplementation implements TransactionFactory {
    @Override
    public Transaction makeAddHourlyTransaction(int empId, String name, double rate) {
        return new AddHourlyEmployeeTransaction(empId, name, rate);
    }
    // ...
}
```

</details>

```typescript
// TypeScript
interface TransactionFactory {
    makeAddHourlyTransaction(empId: number, name: string, rate: number): Transaction;
    makeTimecardTransaction(empId: number, date: Date, hours: number): Transaction;
    makePaydayTransaction(date: Date): Transaction;
    // ...
}

namespace TransactionFactory {
    // 메인에서 주입되는 전역 팩토리 인스턴스
    export let instance: TransactionFactory;
}

class TransactionFactoryImplementation implements TransactionFactory {
    makeAddHourlyTransaction(empId: number, name: string, rate: number): Transaction {
        return new AddHourlyEmployeeTransaction(empId, name, rate);
    }
    // ...
}
```

### 8.3 팩토리 초기화 — 메인의 역할

```
       main()
         │
         │ new TransactionFactoryImplementation()
         │ new PayrollFactoryImplementation()
         │
         ▼
   TransactionFactory.instance ← 주입
   PayrollFactory.instance     ← 주입
```

> **Uncle Bob의 경험**: 메인 프로그램이 모든 구체 패키지에 의존하게 되므로, 모든 구체 패키지에는 메인으로부터 들어오는 결합이 하나씩 생긴다. 이 때문에 구체 패키지가 주계열에서 약간 멀어지지만 어쩔 수 없다. 실용적인 해결책으로, 나는 보통 메인 프로그램으로부터 오는 결합은 무시하곤 한다.

---

## 9. 최종 패키지 구조

### 9.1 응집도 경계 재고

처음 분리했던 `Classifications`, `Methods`, `Schedules`, `Affiliations` 4개 구체 패키지는 패키지 다이어그램을 너무 엉키게 만들었다. **트랜잭션을 다른 것과 갈라놓는 것이 기능별로 갈라놓는 것보다 더 중요**하므로 다음과 같이 통합한다:

- 4개 구체 도메인 패키지 → **`PayrollImplementation`** 하나로 통합
- 모든 트랜잭션 → **`TransactionImplementation`** 하나로 통합

### 9.2 최종 구조

```
                  ┌────────────────────────┐
                  │  PayrollApplication    │  ← main (모든 팩토리에 의존)
                  └──┬──────────┬──────────┘
                     │          │
        ┌────────────┘          └────────────┐
        ▼                                    ▼
┌───────────────┐                    ┌───────────────┐
│  TextParser   │                    │ PayrollFactory│
│  Transaction  │                    │     Impl      │
│   Source      │                    └───────┬───────┘
└───────┬───────┘                            │
        │                                    ▼
        ▼                            ┌───────────────┐
┌───────────────┐                    │   Payroll     │
│  Transaction  │                    │Implementation │
│   Factory     │                    └───────┬───────┘
│Implementation │                            │
└───────┬───────┘                            │
        ▼                                    │
┌───────────────┐                            │
│  Transaction  │                            │
│Implementation │                            │
└───────┬───────┘                            │
        ▼                                    │
┌───────────────┐    ┌───────────────┐      │
│  Transaction  │    │   Payroll     │      │
│   Factory     │    │   Factory     │      │
└───────┬───────┘    └───────┬───────┘      │
        ▼                    ▼              │
┌───────────────┐    ┌──────────────────────┴────┐
│   Abstract    │    │      PayrollDomain        │ ◀── 핵심 추상
│ Transactions  │    └──────────────┬────────────┘
└───────┬───────┘                   │
        ▼                           ▼
┌───────────────┐         ┌──────────────────┐
│ Transaction   │         │  PayrollDatabase │
│ Application   │         └────────┬─────────┘
└───────────────┘                  ▼
                         ┌──────────────────────┐
                         │ PayrollDatabase Impl │
                         └──────────────────────┘
```

### 9.3 최종 측정값

| 패키지 | A | I | D' | 평가 |
|--------|---|---|------|------|
| `PayrollDomain` | .80 | .14 | .20 | 우수 |
| `PayrollFactory` | 1 | .25 | .25 | 우수 (안정+추상) |
| `TransactionFactory` | 1 | .25 | .25 | 우수 |
| `AbstractTransactions` | 1 | .20 | .05 | 우수 |
| `TransactionApplication` | 1.33→1 | .07 | .07 | 우수 |
| `Application` | 1 | 0 | 0 | 주계열 위 |
| `PayrollDatabase` | 1 | 0 | 0 | 주계열 위 |
| `PayrollImplementation` | 0 | .83 | .17 | 우수 (구체+불안정) |
| `TransactionImplementation` | 0 | .93 | .07 | 우수 |
| `TextParserTransactionSource` | 0 | .75 | .25 | 양호 |
| `PayrollApplication` | 0 | 1 | 0 | 주계열 위 (main) |

> **핵심 통찰**: 모든 패키지가 주계열 근처에 위치하고 관계 응집도(H)도 높다. **추상 패키지들은 폐쇄·재사용 가능·의존받지만 자기는 의존 안 함**, **구체 패키지들은 재사용 단위로 분리·추상에 의존·의존받지 않음** — 건전한 개발 환경의 모습이다.

---

## 10. 자주 하는 실수

| 안티패턴 | 문제 | 해결 |
|----------|------|------|
| **"비슷한 이름"으로 묶기** | 한 변경이 패키지 전체 재릴리즈 유발 | CCP로 다시 — "함께 변경되는 것"으로 묶기 |
| **추상도 0인 패키지에 강하게 의존** | 구체 변경이 의존 사슬 전체로 전염 | DIP로 추상을 분리, FACTORY로 의존 끊기 |
| **재사용 단위에 불필요한 짐 동반** | 일부만 쓰고 싶은데 전체를 끌고 와야 함 | CRP로 분리 (`Transaction`을 `PayrollDomain`에서 분리) |
| **패키지 다이어그램이 엉킴** | 수작업 릴리즈 관리 불가 | 응집도 경계를 더 굵게 재설정 (`PayrollImplementation` 통합) |
| **메인의 결합을 측정값에 포함** | 메인은 어차피 늘 재릴리즈 → 측정 노이즈 | 메인의 결합은 실용적으로 무시 |

---

## 11. 패키지 설계 원칙 요약 (적용된 모습)

| 원칙 | 적용된 곳 |
|------|----------|
| **REP** (재사용-릴리즈 등가) | `PayrollDomain`에서 `Transaction` 분리 → 도메인만 재사용 가능 |
| **CCP** (공통 폐쇄) | 트랜잭션을 자기가 다루는 도메인 클래스와 같은 패키지로 묶음 |
| **CRP** (공통 재사용) | 함께 재사용되지 않는 것을 분리 (`Transaction` ↔ `Employee`) |
| **ADP** (비순환 의존성) | DAG 구조 유지 — 모든 의존성이 한 방향으로 흐름 |
| **SDP** (안정 의존성) | 구체 → 추상 방향 — `PayrollImplementation` → `PayrollDomain` |
| **SAP** (안정 추상화) | 안정 패키지(`PayrollDomain`)는 추상도가 높음 (A=.80) |

---

## 요약

- **패키지는 릴리즈/배포/재사용/변경 격리의 단위**다. 50개 클래스를 어떻게 묶느냐에 따라 개발 환경 품질이 결정된다
- **첫 시도 — "비슷한 것끼리"**: 직관적이지만 CCP 위반 → 작은 변경이 큰 재릴리즈를 부른다
- **두 번째 — CCP 적용**: 트랜잭션을 자기 도메인과 같이 묶음 → 변경 영향이 패키지에 갇힘
- **세 번째 — CRP/REP 적용**: `Transaction`을 `PayrollDomain`에서 분리 → 재사용 단위 정제
- **객체 팩토리**: 인스턴스화 의존성을 끊어서 구체 패키지로 들어오는 결합 제거
- **측정값(A, I, D')**: 패키지 품질을 정량화 — 주계열 근처가 이상적
- **거꾸로 뒤집힌 구조**: 추상이 아래, 구체가 위 — OOD의 특징
- **메인은 결합의 종점**: 메인이 모든 팩토리에 의존하지만 어차피 매번 재릴리즈되므로 실용적으로 무시
- **단순함 우선**: 패키지 다이어그램이 엉키면 응집도 경계를 더 굵게 다시 그어라 — `PayrollImplementation`/`TransactionImplementation` 통합

> **Uncle Bob의 경험**: 패키지 구조를 관리할 필요성의 정도는 프로그램의 크기와 개발 팀 규모의 함수다. 아무리 팀이 작더라도 서로 방해되지 않도록 소스 코드를 분할할 필요가 있다. 규모가 큰 프로그램은 어떤 종류이든 소스 코드를 분할할 수 있는 구조가 없다면 이해하기 힘든 소스 파일 더미가 되어버릴 것이다.
