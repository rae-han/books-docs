# Chapter 18: Payroll Case Study — Iteration 1 (급여 관리 사례 연구: 반복의 시작)

## 핵심 질문

간단한 일괄 임금 지급 시스템의 첫 번째 반복에서 우리는 무엇을 설계해야 하는가? 데이터베이스 스키마부터 시작하는 통념적 접근이 왜 잘못되었는가? 유스케이스 분석으로부터 어떻게 객체 모델과 추상화를 도출할 수 있는가? 그리고 — 요구사항에 명시적으로 드러나지 않은 잠재적 추상화는 어떻게 발견하는가?

> 아름다운 것은 모두 그 자체로 아름답고, 그 자체로 완전하며, 찬양할 만한 점이 따로 있는 것은 아니다.<br>— 마르쿠스 아우렐리우스(Marcus Aurelius), A.D. 170년경

---

## 1. 사례 연구의 배경

이 사례 연구는 간단한 일괄 임금 지급 시스템(*Batch Payroll System - 일정 주기로 한 번에 직원들에게 임금을 지급하는 시스템*) 개발 과정의 첫 번째 반복(*Iteration - 애자일에서 일정 단위로 끊어진 짧은 개발 주기*)을 보여준다. 사용자 스토리는 극단적으로 단순화되어 있다 — 예를 들어 세금은 아예 언급되지도 않는다. 이는 초기 반복의 전형적인 모습이다. 고객이 필요로 하는 업무 기능의 아주 작은 부분만 제공한다.

이 장에서 진행할 일은 일반적인 반복을 시작할 때 흔히 갖는 **빠른 분석/설계 회의**와 비슷한 것이다. 고객은 그 반복에 처리할 스토리를 선택했고, 우리는 이제 그것을 어떻게 구현할지 생각해야 한다. 이런 설계 회의는 짧고 대충 지나가는 것이며, 여기서 보게 될 UML 다이어그램은 화이트보드에 급하게 스케치한 것과 다름없다. 실질적인 설계 작업은 단위 테스트와 구현을 다루는 다음 장에서 하게 된다.

> **핵심 통찰**: 반복 시작 시점의 설계 회의는 "확실한 설계를 만들어내는 것"이 목표가 아니다. 개발자들에게 일을 시작해나갈 **공통적인 사고 모델(mental model)**을 제공하는 것이 목표다. 한 시간 안에 끝나며, 그 결과물은 화이트보드에 남겨놓거나 지우는 것이 보통이다.

---

## 2. 명세 (Specification)

첫 반복에 선택된 사용자 스토리에 관해 고객과 나눈 대화에서 메모한 사항은 다음과 같다.

- **시간제 직원(*Hourly Employee*)**: 몇몇 직원은 시간제로 일한다. 직원 레코드의 한 필드인 시급에 따라 임금을 받는다. 매일 날짜와 일한 시간을 기록한 **타임카드(*TimeCard - 출근/근무 시간을 기록한 카드*)**를 제출하는데, 하루에 8시간 이상 일하면 초과근무 시간에 대해서는 1.5배를 받는다. 매주 금요일마다 임금을 받는다.
- **월급 직원(*Salaried Employee*)**: 몇몇 직원은 고정된 월급을 받는다. 매달 마지막 평일에 임금을 받는다. 월급 액수는 직원 레코드의 한 필드가 된다.
- **수수료 직원(*Commissioned Employee*)**: 월급을 받는 직원 중 일부는 별도로 판매량에 기반을 둔 수수료를 받는다. 날짜와 판매량이 기록된 **판매영수증(*SalesReceipt*)**을 제출한다. 수수료율은 직원 레코드의 한 필드가 된다. 격주로 금요일마다 임금을 받는다.
- **지급 방법**: 직원들은 임금을 받는 방법을 선택할 수 있다. 자신이 선택한 우편 주소로 급료 지급 수표를 우송받을 수도 있고, 급여 담당자에게 맡겨놓았다가 찾아갈 수도 있으며, 자신이 선택한 은행 계좌로 직접 입금되게 할 수도 있다.
- **조합 가입**: 몇몇 직원은 조합에 속해 있다. 직원 레코드에는 주당 조합비 비율을 나타내는 필드가 있으며, 이 조합비는 임금에서 공제되어야 한다. 또한 조합은 가끔 조합원 개인에게 **공제액(*Service Charge - 임금에서 별도로 차감되는 추가 부과 금액*)**을 부과할 수도 있다. 이 공제액은 주 단위로 조합에 의해 제출되며, 해당 직원의 다음 달 임금에서 공제되어야 한다.
- **실행 방식**: 급여 관리 애플리케이션은 평일에 한 번씩 실행되고 해당 직원에게 그날 임금을 지급한다. 이 시스템은 직원이 임금을 받을 날짜를 입력받아, 지정된 날짜 전에 마지막으로 임금을 받은 날부터 지정된 날짜까지의 임금을 계산한다.

---

## 3. 데이터베이스부터 시작하지 말 것

이 시점에서 자연스럽게 떠오르는 충동은 **데이터베이스 스키마(*schema - DB 테이블/필드 구조*)부터 만드는 것**이다. 명백히 어떤 종류의 관계형 데이터베이스를 사용할 수 있을 것이고, 고객의 요구사항은 테이블과 필드가 어떻게 구성될지에 대한 좋은 정보를 제공한다. 제대로 동작하는 스키마를 설계하고 어떤 질의 구성을 시작하는 것은 쉬운 일이다.

그러나 이런 접근 방식을 택하면 **데이터베이스가 중점적 관심사가 되는 애플리케이션**이 만들어진다.

> **핵심 통찰**: 데이터베이스는 구체적인 구현이다. 데이터베이스에 대한 고려는 가능한 한 뒤로 미루어야 한다. 너무 많은 애플리케이션이 처음부터 데이터베이스를 생각하고 설계되기 때문에 그 데이터베이스에 어쩔 수 없이 묶여버린다. **본질의 확충과 지엽적인 것의 제거**라는 추상화의 정의를 상기하자. 이 단계의 프로젝트에서 데이터베이스는 지엽적인 것으로, 그저 데이터를 저장하고 그것에 접근하는 기법, 그 이상도 이하도 아니다.

| 통념적 접근 | 추천 접근 |
|------------|-----------|
| DB 스키마부터 설계 | 시스템 행위(behavior)부터 분석 |
| 테이블/필드 구조에 갇힘 | 객체 모델이 자유롭게 진화 |
| 데이터 중심 사고 | 책임/협력 중심 사고 |

---

## 4. 유스케이스 분석 (Use Case Analysis)

시스템의 데이터보다는 **시스템의 행위**를 생각하는 것에서 출발하자. 아무튼 우리가 보수를 받고 만들어내야 하는 것은 시스템의 동작이다.

어떤 시스템의 행위를 이해하고 분석하는 방법 중 하나는 **유스케이스(*Use Case - 시스템 사용자가 특정 목표를 달성하기 위해 시스템과 상호작용하는 시나리오*)**를 만들어보는 것이다. 유스케이스는 원래 야콥슨(Jacobson)이 기술한 것으로, XP에서의 사용자 스토리 개념과 아주 비슷하다. 유스케이스는 좀 더 구체적인 내용이 추가되어 상세해진 사용자 스토리라 할 수 있다.

### 4.1 첫 반복의 사용자 스토리

다음 반복을 위해 고객이 선택한 사용자 스토리는 7개다.

1. 새 직원을 추가한다.
2. 직원을 삭제한다.
3. 타임카드를 기록한다.
4. 판매영수증을 기록한다.
5. 조합 공제액을 기록한다.
6. 직원 정보를 변경한다 (예: 시급, 조합비 비율).
7. 당일을 위한 급여 프로그램을 실행한다.

이 사용자 스토리 각각을 상세화된 유스케이스로 변환하자. 지나치게 구체적으로 들어갈 필요는 없다. 각 스토리를 충족시키는 코드 설계를 생각하는 데 도움이 될 정도면 된다.

---

## 5. 유스케이스 1 — 직원 추가

> **유스케이스 1: 새 직원 추가하기**
>
> 새로운 직원은 `AddEmp` 트랜잭션을 받는 것으로 추가된다. 이 트랜잭션은 직원의 이름, 주소, 직원 번호를 포함하는데, 다음과 같은 세 가지 형식이 있다.
>
> ```
> AddEmp <직원번호> "<이름>" "<주소>" H <시급>
> AddEmp <직원번호> "<이름>" "<주소>" S <월급>
> AddEmp <직원번호> "<이름>" "<주소>" C <월급> <수수료율>
> ```
>
> 이 직원의 레코드 필드는 적절히 값이 할당되어 생성된다.
>
> **대안 — 트랜잭션 구조에서의 에러**: 트랜잭션 구조가 부적당하다면, 에러 메시지를 출력하고 아무 동작도 하지 않는다.

### 5.1 커맨드 패턴 적용

`AddEmp` 트랜잭션에는 세 가지 형식이 있지만, 모든 형식에는 `<직원번호>`, `<이름>`, `<주소>` 필드가 공통적으로 있다. **커맨드 패턴(*Command Pattern - 요청을 객체로 캡슐화하여 매개변수화/큐잉/실행취소 등을 가능하게 하는 패턴*)**을 사용해서 3개의 파생 클래스를 갖는 기반 클래스 `AddEmployeeTransaction`을 만들 수 있다.

```
                ┌──────────────────────────┐
                │ AddEmployeeTransaction   │
                ├──────────────────────────┤
                │ - Name                   │
                │ - EmployeeId             │
                │ - Address                │
                └────────────┬─────────────┘
                             △
            ┌────────────────┼────────────────┐
            │                │                │
┌───────────┴────────┐ ┌─────┴───────────┐ ┌──┴────────────────┐
│ AddHourly          │ │ AddSalaried     │ │ AddCommissioned   │
│ EmployeeTransaction│ │ EmployeeTrans.. │ │ EmployeeTrans..   │
└────────────────────┘ └─────────────────┘ └───────────────────┘
                  그림 18-1 AddEmployeeTransaction 클래스 계층 구조
```

<details>
<summary>원문 Java 코드</summary>

```java
// Java
public abstract class AddEmployeeTransaction implements Transaction {
    private final int empid;
    private final String name;
    private final String address;

    public AddEmployeeTransaction(int empid, String name, String address) {
        this.empid = empid;
        this.name = name;
        this.address = address;
    }

    protected abstract PaymentClassification makeClassification();
    protected abstract PaymentSchedule makeSchedule();

    public void execute() {
        PaymentClassification pc = makeClassification();
        PaymentSchedule ps = makeSchedule();
        PaymentMethod pm = new HoldMethod();
        Employee e = new Employee(empid, name, address);
        e.setClassification(pc);
        e.setSchedule(ps);
        e.setMethod(pm);
        PayrollDatabase.addEmployee(empid, e);
    }
}

public class AddHourlyEmployee extends AddEmployeeTransaction {
    private final double hourlyRate;

    public AddHourlyEmployee(int empid, String name, String address, double rate) {
        super(empid, name, address);
        this.hourlyRate = rate;
    }

    @Override
    protected PaymentClassification makeClassification() {
        return new HourlyClassification(hourlyRate);
    }

    @Override
    protected PaymentSchedule makeSchedule() {
        return new WeeklySchedule();
    }
}
```

</details>

```typescript
// TypeScript
abstract class AddEmployeeTransaction implements Transaction {
    constructor(
        protected readonly empid: number,
        protected readonly name: string,
        protected readonly address: string,
    ) {}

    protected abstract makeClassification(): PaymentClassification;
    protected abstract makeSchedule(): PaymentSchedule;

    execute(): void {
        const pc = this.makeClassification();
        const ps = this.makeSchedule();
        const pm = new HoldMethod();
        const e = new Employee(this.empid, this.name, this.address);
        e.setClassification(pc);
        e.setSchedule(ps);
        e.setMethod(pm);
        PayrollDatabase.addEmployee(this.empid, e);
    }
}

class AddHourlyEmployee extends AddEmployeeTransaction {
    constructor(empid: number, name: string, address: string, private readonly hourlyRate: number) {
        super(empid, name, address);
    }

    protected makeClassification(): PaymentClassification {
        return new HourlyClassification(this.hourlyRate);
    }

    protected makeSchedule(): PaymentSchedule {
        return new WeeklySchedule();
    }
}
```

### 5.2 SRP 관점에서의 장점

이 구조는 각각의 일을 독자적인 클래스에 나누어 맡김으로써 **단일 책임 원칙(SRP)**을 멋지게 지키고 있다. 그 밖의 대안으로 이 모든 일을 하나의 모듈에 맡길 수도 있다. 이 방법은 시스템에 있는 클래스의 수를 감소시켜 시스템이 더 간단해질 수는 있겠지만, 모든 트랜잭션 처리 코드를 한 곳에 집중시켜 거대하고 잠재적으로 에러가 발생하기 쉬운 모듈을 만들어낸다.

### 5.3 첫 시도의 Employee 계층 구조

유스케이스 1은 특히 직원 레코드를 다루고 있는데, 이 레코드는 어떤 종류의 데이터베이스를 의미한다. 또다시 데이터베이스를 고려하려는 성향이 관계형 데이터베이스 테이블에서의 레코드 레이아웃이나 필드 구조를 생각하도록 유혹하지만, 이 충동에 단호히 저항해야만 한다.

이 유스케이스가 정말 요구하는 것은 **직원을 새로 만드는 것**이다. 어떤 직원의 객체 모델은 무엇인가? 좀 더 나은 질문 형태는 다음과 같을 것이다. 각기 다른 3개의 트랜잭션이 만들어내는 것은 무엇인가? 이 트랜잭션들은 서로 다른 세 가지 종류의 직원 객체를 만들면서, 서로 다른 세 가지 종류의 `AddEmp` 트랜잭션을 흉내내고 있다.

```
                    ┌──────────────┐
                    │   Employee   │
                    └──────┬───────┘
                           △
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────┴────────┐ ┌───────┴────────┐ ┌──────┴────────────┐
│ HourlyEmployee │ │ SalariedEmp.   │ │ CommissionedEmp.  │
└────────────────┘ └────────────────┘ └───────────────────┘
              그림 18-2 가능한 Employee 클래스 계층 구조
```

> 이 다이어그램은 후에 유스케이스 6을 분석하면서 잘못된 설계로 판명된다 — 직원의 종류는 런타임에 바뀔 수 있기 때문이다.

---

## 6. 유스케이스 2 — 직원 삭제

> **유스케이스 2: 직원 삭제하기**
>
> `DelEmp` 트랜잭션을 받으면 직원을 삭제한다.
>
> ```
> DelEmp <직원번호>
> ```
>
> 이 트랜잭션을 받으면 해당하는 직원 레코드가 삭제된다.
>
> **대안 — 유효하지 않거나 알 수 없는 직원번호**: `<직원번호>` 필드가 맞게 구성되어 있지 않거나 유효한 직원 레코드를 가리키지 않으면, 이 트랜잭션은 에러 메시지를 출력하고 아무 동작도 하지 않는다.

이 유스케이스는 설계에 관해 지금은 아무 영감도 주지 않는다. 그러므로 다음으로 넘어가자.

---

## 7. 유스케이스 3 — 타임카드 기록

> **유스케이스 3: 타임카드 기록하기**
>
> `TimeCard` 트랜잭션을 받으면 시스템은 타임카드 레코드를 하나 생성하고, 이것을 해당하는 직원 레코드에 연결한다.
>
> ```
> TimeCard <직원번호> <날짜> <시간>
> ```
>
> **대안 1 — 선택된 직원이 시간제로 일하지 않는 경우**: 시스템은 적절한 에러 메시지를 출력하고 더 이상의 동작은 취하지 않는다.
> **대안 2 — 트랜잭션 구조에서의 에러**: 시스템은 적절한 에러 메시지를 출력하고 더 이상의 동작은 취하지 않는다.

이 유스케이스는 **어떤 트랜잭션은 특정한 부류의 직원에 대해서만 쓸 수 있음**을 나타낸다. 이는 서로 다른 것은 서로 다른 클래스에 의해 표현되어야 한다는 아이디어를 강화하는 것이다. 여기서 타임카드와 시간제 직원 사이에는 어떤 관계가 있다.

```
    ┌────────────────┐  1     0..*  ┌────────────┐
    │ HourlyEmployee │◇────────────▷│  TimeCard  │
    └────────────────┘               └────────────┘
        그림 18-3 HourlyEmployee와 TimeCard 사이의 관계
```

---

## 8. 유스케이스 4 — 판매영수증 기록

> **유스케이스 4: 판매영수증 기록하기**
>
> `SalesReceipt` 트랜잭션을 받으면 시스템은 새로운 판매영수증 레코드를 하나 생성하고, 이것을 해당하는 직원에게 연결한다.
>
> ```
> SalesReceipt <직원번호> <날짜> <액수>
> ```
>
> **대안 1**: 선택된 직원이 판매수수료를 따로 받는 직원이 아닌 경우, 에러 메시지를 출력하고 더 이상의 동작은 취하지 않는다.
> **대안 2**: 트랜잭션 구조에서의 에러 — 에러 메시지를 출력하고 더 이상의 동작은 취하지 않는다.

이 유스케이스는 유스케이스 3과 아주 비슷한 의미를 갖는다.

```
    ┌──────────────────────┐ 1   0..* ┌──────────────┐
    │ CommissionedEmployee │◇────────▷│ SalesReceipt │
    └──────────────────────┘          └──────────────┘
        그림 18-4 판매수수료를 받는 직원과 판매영수증
```

---

## 9. 유스케이스 5 — 조합 공제액 기록

> **유스케이스 5: 조합 공제액 기록하기**
>
> 이 트랜잭션을 받으면 시스템은 공제액 레코드 하나를 생성하고, 이것을 해당하는 조합원 레코드에 연결한다.
>
> ```
> ServiceCharge <조합원번호> <액수>
> ```
>
> **대안 — 형식을 지키지 않은 트랜잭션**: 트랜잭션이 형식을 지키지 않았거나 `<직원번호>`가 실제로 존재하는 조합원을 가리키지 않으면, 적절한 에러 메시지와 함께 출력된다.

이 유스케이스는 **직원번호로 조합원에게 접근하는 것이 아님**을 보여준다. 조합은 조합원들을 위한 고유의 식별번호 체계를 갖고 있다. 따라서 시스템은 조합원과 직원을 연결할 수 있어야 한다.

> **핵심 통찰**: 이와 같은 연결을 가능하게 하는 여러 가지 방법이 있으므로, 임의로 결정하는 상황을 피하기 위해 이 결정은 뒤로 미루도록 하자. 아마 시스템의 다른 부분의 제약이 어느 한쪽으로 이끌어줄 것이다. **결정의 지연(*Deferred Decision*)**은 잘못된 추측으로 설계를 망가뜨리는 일을 막아준다.

```
    ┌───────────────┐ 1     0..*  ┌────────────────┐
    │ UnionMember   │◇───────────▷│ ServiceCharge  │
    └───────────────┘              └────────────────┘
            그림 18-5 조합원과 공제액
```

---

## 10. 유스케이스 6 — 직원 정보 변경

> **유스케이스 6: 직원 정보 변경하기**
>
> 이 트랜잭션을 받으면 시스템은 해당하는 직원 레코드의 정보 중 하나를 변경한다. 다양한 변형이 있다.
>
> ```
> ChgEmp <직원번호> Name <이름>                      직원의 이름을 변경
> ChgEmp <직원번호> Address <주소>                   직원의 주소를 변경
> ChgEmp <직원번호> Hourly <시급>                    시급제로 변경
> ChgEmp <직원번호> Salaried <월급>                  월급제로 변경
> ChgEmp <직원번호> Commissioned <월급> <비율>       수수료제로 변경
> ChgEmp <직원번호> Hold                             급여담당자에게 맡김
> ChgEmp <직원번호> Direct <은행> <계좌>             직접 입금
> ChgEmp <직원번호> Mail <주소>                      우편 수령
> ChgEmp <직원번호> Member <조합원번호> Dues <비율>  조합 가입
> ChgEmp <직원번호> NoMember                         조합 탈퇴
> ```

### 10.1 그림 18-2가 유효하지 않음을 깨달음

이 유스케이스는 변경되어야 하는 직원의 모든 면을 말해주기 때문에 그 의미가 아주 크다. **어떤 직원을 시간제 직원에서 월급을 받는 직원으로 변경할 수 있다는 사실**은 그림 18-2의 다이어그램(직원 종류별 상속)이 분명 유효하지 않음을 의미한다. 객체의 클래스는 런타임에 바뀔 수 없기 때문이다.

오히려 임금을 계산하는 데 **스트래터지 패턴(*Strategy Pattern - 알고리즘 종류를 캡슐화하고 런타임에 교체할 수 있게 하는 패턴*)**을 사용하는 편이 더 정확할 것이다.

### 10.2 핵심 모델 — 스트래터지 패턴 3중 적용

```
    «interface»                                «interface»
   ┌─────────────┐                           ┌─────────────┐
   │ Payment     │                           │ Affiliation │
   │ Method      │                           └──────△──────┘
   └──────△──────┘                                  │
          │           ┌──────────┐         ┌────────┴────────┐
   ┌──────┼──────┐    │ Employee │◇───────▷│ NoAffiliation   │
   │      │      │    └─────┬────┘         │ UnionAffiliation│
   │      │      │          │              │   - Dues        │
┌──┴──┐ ┌─┴──┐ ┌─┴──┐       │              └────────┬────────┘
│Hold │ │Dir.│ │Mail│       │                       │ 0..*
└─────┘ └────┘ └────┘       │              ┌────────┴────────┐
                            │              │ ServiceCharge   │
                            │              └─────────────────┘
                            ▽
                  «interface»
                ┌────────────────┐
                │ Payment        │
                │ Classification │
                └────────△───────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
  ┌─────┴──────┐  ┌──────┴───────┐  ┌─────┴──────────┐
  │ Salaried   │  │ Hourly       │  │ Commissioned   │
  │ Classif.   │  │ Classif.     │  │ Classif.       │
  │ - Salary   │  │ - HourlyRate │  │ - Salary       │
  └────────────┘  └───────┬──────┘  │ - CommissionR. │
                          │ 0..*    └────────┬───────┘
                  ┌───────┴────┐             │ 0..*
                  │ TimeCard   │     ┌───────┴──────┐
                  └────────────┘     │ SalesReceipt │
                                     └──────────────┘
        그림 18-6 급여 관리의 수정된 클래스 다이어그램 (핵심 모델)
```

<details>
<summary>원문 Java 코드 — Employee 핵심 모델</summary>

```java
// Java
public class Employee {
    private int empid;
    private String name;
    private String address;
    private PaymentClassification classification;
    private PaymentSchedule schedule;
    private PaymentMethod method;
    private List<Affiliation> affiliations = new ArrayList<>();

    public void setClassification(PaymentClassification c) { this.classification = c; }
    public void setSchedule(PaymentSchedule s) { this.schedule = s; }
    public void setMethod(PaymentMethod m) { this.method = m; }
    public void addAffiliation(Affiliation a) { affiliations.add(a); }

    public boolean isPayDate(Date date) {
        return schedule.isPayDate(date);
    }

    public double calculatePay(Paycheck pc) {
        double grossPay = classification.calculatePay(pc);
        double deductions = 0.0;
        for (Affiliation a : affiliations) {
            deductions += a.calculateDeductions(pc);
        }
        return grossPay - deductions;
    }
}

public interface PaymentClassification {
    double calculatePay(Paycheck pc);
}

public interface PaymentSchedule {
    boolean isPayDate(Date date);
}

public interface PaymentMethod {
    void pay(Paycheck pc);
}

public interface Affiliation {
    double calculateDeductions(Paycheck pc);
}
```

</details>

```typescript
// TypeScript
class Employee {
    private classification!: PaymentClassification;
    private schedule!: PaymentSchedule;
    private method!: PaymentMethod;
    private affiliations: Affiliation[] = [];

    constructor(
        private readonly empid: number,
        private name: string,
        private address: string,
    ) {}

    setClassification(c: PaymentClassification): void {
        this.classification = c;
    }
    setSchedule(s: PaymentSchedule): void {
        this.schedule = s;
    }
    setMethod(m: PaymentMethod): void {
        this.method = m;
    }
    addAffiliation(a: Affiliation): void {
        this.affiliations.push(a);
    }

    isPayDate(date: Date): boolean {
        return this.schedule.isPayDate(date);
    }

    calculatePay(pc: Paycheck): number {
        const grossPay = this.classification.calculatePay(pc);
        let deductions = 0;
        for (const a of this.affiliations) {
            deductions += a.calculateDeductions(pc);
        }
        return grossPay - deductions;
    }
}

interface PaymentClassification {
    calculatePay(pc: Paycheck): number;
}

interface PaymentSchedule {
    isPayDate(date: Date): boolean;
}

interface PaymentMethod {
    pay(pc: Paycheck): void;
}

interface Affiliation {
    calculateDeductions(pc: Paycheck): number;
}
```

### 10.3 PaymentClassification의 세 변형

`PaymentClassification` 객체에는 세 가지 변형이 있다.

| 클래스 | 보유 데이터 |
|--------|-------------|
| `HourlyClassification` | 시급 액수, `TimeCard` 객체의 리스트 |
| `SalariedClassification` | 월급 액수 |
| `CommissionedClassification` | 월급, 수수료율, `SalesReceipt` 객체의 리스트 |

직원을 삭제할 때 `TimeCard`와 `SalesReceipt`도 같이 소멸되어야 한다고 생각했기 때문에 각 객체에서 **합성(*composition - 강한 소유 관계로, 전체가 사라지면 부분도 사라지는 관계*)**을 사용했다.

### 10.4 PaymentMethod 변형

- `MailMethod` — 우편 수령. 수표를 보낼 주소를 저장
- `DirectMethod` — 직접 입금. 은행 계좌 저장
- `HoldMethod` — 급여 담당자에게 맡김

### 10.5 Affiliation에 널 오브젝트 패턴 적용

각 `Employee` 객체는 두 가지 형식이 있는 `Affiliation` 객체를 포함한다.

- `NoAffiliation` — 자신 외의 조직에 의해 임금이 조정되지 않는다 (**널 오브젝트 패턴(*Null Object Pattern - 빈 동작을 수행하는 객체로 null 체크를 제거하는 패턴*)**)
- `UnionAffiliation` — 조합비와 공제액을 지불한다

### 10.6 OCP를 만족시킴

> **핵심 통찰**: 이와 같은 패턴 사용은 시스템이 **개방-폐쇄 원칙(OCP)**을 잘 따르게 한다. `Employee` 클래스는 급여 지급 방법, 급여 종류, 조합 종류의 변경에 대해 닫혀 있다. `Employee`에 아무 영향을 주지 않고 새로운 방법과 종류, 조합의 종류를 추가할 수 있다.

그림 18-6은 핵심 모델이자 아키텍처가 된다. 이 구조는 급여 시스템이 하는 모든 일의 핵심에 있다. 급여 관리 애플리케이션에는 다른 많은 클래스와 설계가 있겠지만, 이것들은 모두 이 기본 구조에 비하면 부차적인 것이다.

---

## 11. 유스케이스 7 — 임금 지급일

> **유스케이스 7: 당일을 위한 급여 프로그램 실행하기**
>
> `Payday` 트랜잭션을 받으면, 시스템은 지정된 날짜에 임금을 받아야 할 직원을 모두 가려낸다. 이들이 얼마의 액수를 받아야 하는지 결정하고, 이들이 선택한 지급 방식으로 임금을 지급한다.
>
> ```
> Payday <날짜>
> ```

### 11.1 임금 계산의 위임 — 협동 다이어그램

먼저, `Employee` 객체는 어떻게 자신의 임금을 계산하는 방법을 알 수 있는가? 직원이 시간제 직원이라면 시스템은 그의 타임카드 기록의 총합을 계산해서 시급을 곱해야 할 것이다. 수수료를 받는다면 판매영수증 금액의 총합을 계산해서 수수료율을 곱하고, 기본 월급을 더해야 할 것이다.

이상적인 장소는 `PaymentClassification` 파생 클래스인 것처럼 보인다. 이 객체는 임금을 계산하는 데 필요한 레코드를 갖기 때문이다.

```
   ┌────────────────────┐  1: Pay(Date)   ┌──────────┐
   │ PaydayTransaction  │ ───────────────▶│ Employee │
   └────────────────────┘                 └─────┬────┘
                                                │ 1.1: CalculatePay(Date)
                                                ▽
                                       ┌────────────────────┐
                                       │ PaymentClassif.    │
                                       └────────────────────┘
                  그림 18-7 어떤 직원의 임금 계산
```

`Employee` 객체는 임금을 계산하라는 요청을 받으면, 이 요청을 `PaymentClassification` 객체에 맡긴다. 실제로 사용되는 알고리즘은 `Employee` 객체가 포함하는 `PaymentClassification`의 형에 좌우된다.

### 11.2 시간제/수수료/월급 직원별 임금 계산

```
시간제 직원의 임금 계산 (그림 18-8)
┌─────────────────────┐               ┌──────────┐
│ HourlyClassif.      │── GetHours ──▶│ TimeCard │
│ CalculatePay(Date)  │◀── hours ─────│          │
│                     │── GetDate ───▶│          │
│                     │◀── date ──────│          │
└─────────────────────┘ (각 타임카드별 반복)
```

```
수수료 직원의 임금 계산 (그림 18-9)
┌─────────────────────┐                  ┌──────────────┐
│ Commissioned        │── GetAmount ────▶│ SalesReceipt │
│ Classification      │◀── amount ───────│              │
│ CalculatePay(Date)  │── GetDate ──────▶│              │
│                     │◀── date ─────────│              │
└─────────────────────┘ (각 판매영수증별 반복)
```

```
월급 직원의 임금 계산 (그림 18-10)
┌────────────────┐
│ Salaried       │
│ Classification │── 월급 반환
│ CalculatePay   │
└────────────────┘
```

---

## 12. 잠재적인 추상화를 찾아서

지금까지 간단한 유스케이스 분석이 시스템 설계에 풍부한 정보와 영감을 제공해준다는 사실을 배웠다. 그러나 OCP를 효과적으로 사용하기 위해서는, 애플리케이션 내에 **잠재하는 추상화**를 샅샅이 뒤져 찾아야 한다. 이런 추상화는 애플리케이션의 요구사항에 명확히 드러나기는커녕 심지어 암시조차 없는 경우도 많다.

### 12.1 첫 번째 — 임금 분류 추상화

요구사항을 다시 살펴보자. "몇몇 직원은 시간제로 일한다", "몇몇 직원은 고정된 월급을 받는다", "몇몇 직원은 수수료를 받는다"와 같은 문장을 볼 수 있다. 이는 다음과 같은 일반화에 대한 힌트를 준다.

> **모든 직원은 임금을 받는다. 하지만 서로 다른 체계에 따라 받는다.**

여기서의 추상화는 `PaymentClassification`이며, 이미 그림 18-6에서 사용되었다. 이 추상화는 아주 간단한 유스케이스 분석에 의해 이미 사용자 스토리 속에서 발견된 것이다.

### 12.2 두 번째 — 지급 주기(Schedule) 추상화 — 가장 까다로움

다른 추상화를 찾아보면 "이들은 매주 금요일마다 임금을 받는다", "이들은 그 달의 마지막 평일에 임금을 받는다", "이들은 격주로 금요일마다 임금을 받는다"를 찾을 수 있다. 이것들은 또 다른 일반성을 이끌어낸다.

> **모든 직원은 어떤 지급 주기에 따라 임금을 받는다.**

여기서의 추상화는 **지급 주기(*schedule*)** 라는 개념이다. 어떤 `Employee` 객체에 특정 날짜가 그 직원이 임금을 받는 날인지 물어볼 수 있어야 한다.

요구사항은 어떤 직원의 지급 주기를 그의 임금 분류와 연계시킨다. 구체적으로:

| 임금 분류 | 지급 주기 |
|-----------|-----------|
| 시간제 직원 | 주당 임금 |
| 월급 직원 | 달마다 임금 |
| 수수료 직원 | 2주마다 임금 |

#### 12.2.1 이런 연계가 본질적인 것인가?

> **Uncle Bob의 경험**: 어느 날 정책이 바뀌어서 직원이 특정한 지급 주기를 선택할 수 있게 되거나, 직원이 서로 다른 지급 주기를 갖는 부서나 부에 소속되지는 않을까? 지급 주기 정책이 임금 지급 정책과는 독립적으로 바뀔 수도 있지 않을까? 물론, 그럴 법하다.

요구사항이 내포하는 것처럼 만약 지급 주기 문제를 `PaymentClassification` 클래스에 위임한다면, 우리의 클래스는 지급 주기 변경에 대해 닫혀 있을 수 없게 된다. 지급 정책을 변경하면 지급 주기도 테스트해야 할 것이다. 지급 주기를 변경하면 지급 정책도 테스트해야 할 것이다. **OCP와 SRP를 모두 위반하게 된다.**

> **핵심 통찰**: 지급 주기와 지급 정책의 연계는 특정 지급 정책 변경이 어떤 직원의 지급 주기를 망가뜨리는 버그를 유발할 수 있다. 이런 버그는 프로그래머에게는 당연한 것이지만, 관리자와 사용자에게는 심장이 얼어붙을 정도로 두려운 것이다. **변경의 영향을 예측할 수 없다면, 신뢰성은 사라지고 그 프로그램은 관리자와 사용자가 내심 "위험하고 불안정한" 상태에 있다고 생각하는 것이 된다.**

#### 12.2.2 PaymentSchedule 추상화

지급 주기 추상화의 본질에도 불구하고, 유스케이스 분석은 그 존재 여부에 대해 어떤 직접적 근거를 보이는 데 실패했다. 이를 보이는 데는 **주의 깊은 요구사항 고려와 사용자 커뮤니티의 속임수에 대한 통찰력**이 필요했다. 도구와 절차에 지나치게 의존하고 부족한 지성과 경험에 의지하면 재앙을 불러온다.

```
        ┌─────────────┐ itsSchedule  ┌──────────────────┐
        │  Employee   │◇────────────▷│ PaymentSchedule  │
        └─────────────┘               └────────△─────────┘
                                                │
                          ┌─────────────────────┼───────────────────┐
                          │                     │                   │
                  ┌───────┴────────┐    ┌───────┴───────┐    ┌──────┴──────────┐
                  │ WeeklySchedule │    │ MonthlySchedule│   │ BiweeklySchedule│
                  └────────────────┘    └────────────────┘   └─────────────────┘
                          그림 18-11 지급 주기 추상화의 정적 모델
```

```
   ┌──────────┐  isPayDate(date)  ┌──────────────────┐
   │ Employee │ ─────────────────▶│ PaymentSchedule  │
   └──────────┘                   │  isPayDate(date) │
                                   └──────────────────┘
                그림 18-12 지급 주기 추상화의 동적 모델
```

### 12.3 세 번째 — 지급 방법 추상화

요구사항에서 만들어낼 수 있는 또 다른 일반화는 "모든 직원은 어떤 방법에 의해 임금을 받을 수 있다"이다. 여기서의 추상화는 `PaymentMethod` 클래스다. 흥미롭게도 이 추상화는 그림 18-6에 이미 표현되어 있다.

### 12.4 네 번째 — 조합/단체 가입 추상화

요구사항은 조합에 가입한 직원이 있을 수 있음을 나타낸다. 그러나 **직원의 임금에 청구분을 가진 단체가 조합만은 아닐 수도 있다.** 직원은 어떤 자선단체에 자동납부 형식으로 기부하고 싶을 수도 있고, 전문직 협회의 회비를 자동납부 형식으로 내고 싶을 수도 있다.

> **직원은 그 직원의 임금에서 자동으로 돈을 지급받는 많은 단체에 가입되어 있을 수 있다.**

대응하는 추상화는 `Affiliation` 클래스다.

```
        ┌─────────────┐  0..*  ┌──────────────┐
        │  Employee   │◇──────▷│ Affiliation  │
        └─────────────┘         └──────△───────┘
                                       │
                              ┌────────┴───────┐
                              │ UnionAffiliation│
                              │   - Dues        │
                              └────────┬───────┘
                                       │ 0..*
                              ┌────────┴───────┐
                              │ ServiceCharge   │
                              │   - Date        │
                              │   - Amount      │
                              └─────────────────┘
                그림 18-13 Affiliation 추상화의 정적 모델
```

```
   ┌──────────┐  pay = CalculatePay(date)   ┌──────────────────┐
   │ Employee │ ───────────────────────────▶│ PaymentClassif.  │
   └────┬─────┘                              └──────────────────┘
        │ [foreach affiliation] fee = GetFee(date)
        ▽
   ┌─────────────┐
   │ Affiliation │
   └─────────────┘
              그림 18-14 Affiliation 추상화의 동적 모델
```

> **핵심 통찰**: `Affiliation` 객체의 리스트는 아무 단체에도 소속되지 않은 직원을 위해 **널 오브젝트 패턴을 사용할 필요성을 미연에 제거했다.** 이제 직원이 아무 단체에도 소속되어 있지 않다면, 그 직원의 `Affiliation` 리스트는 그냥 비어 있을 것이다. 추상화를 발견하면서 동시에 더 단순한 구조가 도출된 것이다.

---

## 13. 결론

한 반복이 시작될 때는 화이트보드 앞에 팀이 모여 그 반복에 선택된 사용자 스토리의 설계를 놓고 논의하는 모습을 흔하게 볼 수 있다. 이런 빠른 설계 회의는 보통 한 시간이 가기 전에 끝난다. 결과로 나온 UML 다이어그램이 있다면 화이트보드에 남겨놓거나 지운다. 보통 이것은 종이에 적어두지 않는다.

> **핵심 통찰**: 이 회의의 목적은 **사고 과정을 시작**하고, 개발자들에게 일을 시작해나갈 **공통적인 사고 모델(mental model)**을 주는 데 있다. **확실한 설계를 만들어내는 것이 목표가 아니다.**

이 장은 이런 빠른 설계 회의와 동등한 텍스트 형태로서의 역할을 했다. 실질적인 설계 작업은 단위 테스트와 구현을 다루는 다음 장에서 이루어진다.

---

## 요약

- **데이터베이스부터 시작하지 말 것**: 데이터베이스는 구체적인 구현이며 지엽적이다. 시스템의 행위부터 분석하자
- **유스케이스 분석**: 사용자 스토리에 구체적인 트랜잭션 구조와 대안 흐름을 추가해 상세화한다
- **커맨드 패턴**: `AddEmp`, `DelEmp`, `TimeCard`, `Payday` 등 트랜잭션을 객체로 캡슐화하여 SRP를 만족시킨다
- **스트래터지 패턴 3중 적용**: `Employee`는 `PaymentClassification`, `PaymentSchedule`, `PaymentMethod`를 포함하여 임금 분류/지급 주기/지급 방법을 런타임에 교체 가능하게 한다
- **런타임 종류 변경**: 직원의 종류(시간제/월급/수수료)가 런타임에 변경 가능하므로 상속이 아닌 위임(스트래터지)으로 풀어야 한다
- **널 오브젝트 패턴 → 리스트로 대체**: `NoAffiliation` 대신 빈 리스트를 사용하여 추상화가 더 단순해졌다
- **잠재적 추상화 발견**: 요구사항에 명시되지 않은 추상화(지급 주기와 임금 분류의 분리)는 OCP를 효과적으로 적용하기 위해 통찰력과 경험으로 찾아내야 한다
- **OCP 만족**: `Employee`는 임금 분류/지급 방법/지급 주기/단체 가입의 변경에 대해 닫혀 있고 확장에는 열려 있다
- **설계 회의의 목적**: 확실한 설계가 아니라 팀의 공통 사고 모델 형성. 결과 다이어그램은 화이트보드에 남기거나 지운다
