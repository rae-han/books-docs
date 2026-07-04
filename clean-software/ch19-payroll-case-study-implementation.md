# Chapter 19: Payroll Case Study — Implementation (급여 관리 사례 연구: 구현)

## 핵심 질문

18장에서 도출한 설계를 어떻게 실제로 동작하는 코드로 옮길 것인가? 트랜잭션 패턴을 어떻게 클래스 계층으로 구현하면 새로운 트랜잭션을 추가할 때 기존 코드를 건드리지 않을 수 있는가? 그리고 — 18장의 다이어그램이 완벽해 보였더라도, 실제 코드를 작성하다 보면 왜 설계는 끊임없이 진화하는가?

> 사실 여러분이 보게 될 코드 묶음은 작성하는 사이에 수십 번의 수정과 컴파일 및 테스트로 아주 조금씩 코드를 발전시켰다.<br>— Robert C. Martin

---

## 1. 구현의 출발점: Transaction 인터페이스

18장에서 설계한 **커맨드 패턴(*Command Pattern - 요청을 객체로 캡슐화하여 호출자와 수신자를 분리하는 패턴*)** 을 그대로 코드로 옮기는 것에서 시작한다. 모든 트랜잭션은 `Transaction`이라는 추상 기반 클래스를 상속받고, `Execute()` 메소드를 구현한다.

```
                  «interface»
                  Transaction
                  ───────────
                  + Execute()
                       △
                       │
       ┌───────────────┼───────────────┬─────────────────┐
       │               │               │                 │
AddEmployee     ChangeEmployee   TimeCardTxn      PaydayTransaction
Transaction     Transaction
```

<details>
<summary>원문 C++ 코드 (Transaction.h)</summary>

```cpp
// C++
#ifndef TRANSACTION_H
#define TRANSACTION_H

class Transaction {
public:
    virtual ~Transaction();
    virtual void Execute() = 0;
};
#endif
```

</details>

```typescript
// TypeScript
interface Transaction {
    execute(): void;
}
```

> **핵심 통찰**: 모든 트랜잭션을 `Transaction` 인터페이스 뒤로 숨기는 순간, 메인 프로그램은 트랜잭션 종류와 무관해진다. 파서가 어떤 구체 트랜잭션을 만들든 메인 프로그램은 그저 `Execute()`만 호출한다. 이것이 OCP(*Open-Closed Principle - 확장에는 열려 있고 변경에는 닫혀 있어야 한다는 원칙*)를 실현하는 방식이다.

---

## 2. AddEmployee 트랜잭션 — 템플릿 메소드 패턴

직원을 추가하는 트랜잭션은 세 가지 종류가 있다: 시급제(Hourly), 월급제(Salaried), 수당제(Commissioned). 세 트랜잭션은 공통 골격(직원을 만들고, 분류·일정·지급 방법을 붙이고, DB에 저장)을 공유하지만 어떤 `PaymentClassification`과 `PaymentSchedule`을 만드는지는 다르다.

이때 사용하는 것이 **템플릿 메소드 패턴(*Template Method Pattern - 알고리즘의 골격은 상위 클래스에 두고 일부 단계를 하위 클래스에서 구현하도록 하는 패턴*)** 이다.

### 2.1 정적 모델

```
            «interface»
            Transaction
                △
                │
        AddEmployeeTransaction      ◀── Execute() 구현
        ─────────────────────────
        + Execute()
        # GetClassification() = 0   ◀── 순수 가상 (훅 메소드)
        # GetSchedule() = 0         ◀── 순수 가상 (훅 메소드)
                △
                │
       ┌────────┼────────┐
       │        │        │
  AddSalaried  AddHourly  AddCommissioned
  Employee     Employee   Employee
```

### 2.2 테스트 먼저 작성

평소처럼 테스트를 먼저 작성한다. `AddSalariedEmployee`가 제대로 작동함을 보여주는 테스트다.

<details>
<summary>원문 C++ 코드 (PayrollTest::TestAddSalariedEmployee)</summary>

```cpp
// C++
void PayrollTest::TestAddSalariedEmployee() {
    int empId = 1;
    AddSalariedEmployee t(empId, "Bob", "Home", 1000.00);
    t.Execute();

    Employee* e = GpayrollDatabase.GetEmployee(empId);
    assert("Bob" == e->GetName());

    PaymentClassification* pc = e->GetClassification();
    SalariedClassification* sc =
        dynamic_cast<SalariedClassification*>(pc);
    assert(sc);
    assertEquals(1000.00, sc->GetSalary(), .001);

    PaymentSchedule* ps = e->GetSchedule();
    MonthlySchedule* ms = dynamic_cast<MonthlySchedule*>(ps);
    assert(ms);

    PaymentMethod* pm = e->GetMethod();
    HoldMethod* hm = dynamic_cast<HoldMethod*>(pm);
    assert(hm);
}
```

</details>

```typescript
// TypeScript
test("AddSalariedEmployee 트랜잭션", () => {
    const empId = 1;
    const t = new AddSalariedEmployee(empId, "Bob", "Home", 1000.0);
    t.execute();

    const e = payrollDatabase.getEmployee(empId);
    expect(e.getName()).toBe("Bob");

    const sc = e.getClassification() as SalariedClassification;
    expect(sc).toBeInstanceOf(SalariedClassification);
    expect(sc.getSalary()).toBeCloseTo(1000.0, 3);

    expect(e.getSchedule()).toBeInstanceOf(MonthlySchedule);
    expect(e.getMethod()).toBeInstanceOf(HoldMethod);
});
```

### 2.3 템플릿 메소드 구현

기반 클래스 `AddEmployeeTransaction`은 `Execute()`의 골격을 구현하고, `GetClassification()`과 `GetSchedule()`은 순수 가상 함수로 남겨둔다.

<details>
<summary>원문 C++ 코드 (AddEmployeeTransaction.cpp)</summary>

```cpp
// C++
void AddEmployeeTransaction::Execute() {
    PaymentClassification* pc = GetClassification();
    PaymentSchedule* ps = GetSchedule();
    PaymentMethod* pm = new HoldMethod();
    Employee* e = new Employee(itsEmpid, itsName, itsAddress);
    e->SetClassification(pc);
    e->SetSchedule(ps);
    e->SetMethod(pm);
    GpayrollDatabase.AddEmployee(itsEmpid, e);
}
```

</details>

```typescript
// TypeScript
abstract class AddEmployeeTransaction implements Transaction {
    constructor(
        protected readonly empId: number,
        protected readonly name: string,
        protected readonly address: string,
    ) {}

    protected abstract getClassification(): PaymentClassification;
    protected abstract getSchedule(): PaymentSchedule;

    execute(): void {
        const pc = this.getClassification();
        const ps = this.getSchedule();
        const pm = new HoldMethod();
        const e = new Employee(this.empId, this.name, this.address);
        e.setClassification(pc);
        e.setSchedule(ps);
        e.setMethod(pm);
        payrollDatabase.addEmployee(this.empId, e);
    }
}

class AddSalariedEmployee extends AddEmployeeTransaction {
    constructor(
        empId: number,
        name: string,
        address: string,
        private readonly salary: number,
    ) {
        super(empId, name, address);
    }

    protected getClassification(): PaymentClassification {
        return new SalariedClassification(this.salary);
    }

    protected getSchedule(): PaymentSchedule {
        return new MonthlySchedule();
    }
}
```

> **Uncle Bob의 경험**: 기본 지급 방법은 `HoldMethod` — 급여를 담당자에게 맡겨두는 방식 — 이다. 이 결정은 트랜잭션 안에 묻혀 있지만 핵심 모델은 이를 모른다. 트랜잭션은 "기교(*technique*)"의 영역이고, 모델은 도메인의 영역이다. 두 영역을 섞지 말자.

---

## 3. PayrollDatabase — 퍼사드(*Facade Pattern - 복잡한 서브시스템에 단순한 인터페이스를 제공하는 패턴*)로 영속성 미루기

`PayrollDatabase`는 `empId`를 키로 `Employee` 객체를 보관하는 단순한 사전(Dictionary)이다. 의도적으로 인메모리 구현으로 시작한다.

```
                ┌──────────────────┐
                │ PayrollDatabase  │
                │     (Facade)     │
                ├──────────────────┤
                │ GetEmployee()    │
                │ AddEmployee()    │
                │ clear()          │
                └────────┬─────────┘
                         │
              ┌──────────┴───────────┐
              ▼                      ▼
     EmpID → Employee          MemberID → EmpID
        (Dictionary)             (Dictionary)
```

<details>
<summary>원문 C++ 코드 (PayrollDatabase.h/.cpp)</summary>

```cpp
// C++
class PayrollDatabase {
public:
    virtual ~PayrollDatabase();
    Employee* GetEmployee(int empId);
    void AddEmployee(int empid, Employee*);
    void clear() { itsEmployees.clear(); }

private:
    map<int, Employee*> itsEmployees;
};

PayrollDatabase GpayrollDatabase;

Employee* PayrollDatabase::GetEmployee(int empid) {
    return itsEmployees[empid];
}

void PayrollDatabase::AddEmployee(int empid, Employee* e) {
    itsEmployees[empid] = e;
}
```

</details>

```typescript
// TypeScript
class PayrollDatabase {
    private readonly employees = new Map<number, Employee>();

    getEmployee(empId: number): Employee | undefined {
        return this.employees.get(empId);
    }

    addEmployee(empId: number, e: Employee): void {
        this.employees.set(empId, e);
    }

    clear(): void {
        this.employees.clear();
    }
}

export const payrollDatabase = new PayrollDatabase();
```

> **핵심 통찰**: 데이터베이스의 구현은 구체적인 사항이므로 이에 대한 의사결정은 가능한 한 뒤로 미뤄야 한다. RDBMS, 플랫 파일, OODBMS 중 어느 것을 쓸지는 지금 시점에서는 의미가 없다. 지금 당장은 데이터베이스 서비스를 제공할 API를 만드는 데만 관심이 있을 뿐이다. 이 연기를 통해 데이터베이스에 지나치게 많은 기반 구조를 추가하는 문제를 방지하게 된다.

---

## 4. TimeCard, SalesReceipt 트랜잭션 — 데이터를 분류에 추가하기

시급제 직원은 출퇴근 시간을 `TimeCard`로 기록하고, 수당제 직원은 판매 영수증을 `SalesReceipt`로 기록한다. 두 트랜잭션은 닮은꼴이다.

### 4.1 TimeCardTransaction

<details>
<summary>원문 C++ 코드 (TimeCardTransaction.cpp)</summary>

```cpp
// C++
void TimeCardTransaction::Execute() {
    Employee* e = GpayrollDatabase.GetEmployee(itsEmpId);
    if (e != 0) {
        PaymentClassification* pc = e->GetClassification();
        HourlyClassification* hc =
            dynamic_cast<HourlyClassification*>(pc);
        if (hc != 0)
            hc->AddTimeCard(new TimeCard(itsDate, itsHours));
        else
            throw("Tried to add timecard to non-hourly employee");
    } else {
        throw("No such employee.");
    }
}
```

</details>

```typescript
// TypeScript
class TimeCardTransaction implements Transaction {
    constructor(
        private readonly date: number,
        private readonly hours: number,
        private readonly empId: number,
    ) {}

    execute(): void {
        const e = payrollDatabase.getEmployee(this.empId);
        if (!e) {
            throw new Error("No such employee.");
        }
        const pc = e.getClassification();
        if (!(pc instanceof HourlyClassification)) {
            throw new Error("Tried to add timecard to non-hourly employee");
        }
        pc.addTimeCard(new TimeCard(this.date, this.hours));
    }
}
```

`SalesReceiptTransaction`도 같은 구조다. `CommissionedClassification`에 `SalesReceipt`를 추가한다.

| 트랜잭션 | 대상 분류 | 추가 데이터 |
|---|---|---|
| `TimeCardTransaction` | `HourlyClassification` | `TimeCard(date, hours)` |
| `SalesReceiptTransaction` | `CommissionedClassification` | `SalesReceipt(date, amount)` |
| `ServiceChargeTransaction` | (조합원의) `UnionAffiliation` | `ServiceCharge(date, amount)` |

> **핵심 통찰**: 트랜잭션이 `dynamic_cast`로 분류를 확인하는 것은 일종의 LSP(*Liskov Substitution Principle*) 위반의 냄새다. 하지만 이 케이스에서는 정당하다 — 시급 직원이 아닌 사람에게 타임카드를 추가하라는 요청은 **의미적으로 잘못된 요청**이므로 런타임에 거부해야 한다.

---

## 5. ChangeEmployee 트랜잭션 — 다양한 변경의 추상화

직원의 무엇이든 바꿀 수 있어야 한다: 이름, 주소, 분류(시급→월급), 일정, 지급 방법, 조합 가입/탈퇴. 이를 모두 별개 트랜잭션으로 만들면 수가 폭발한다. 이때 **추상화 계층**을 한 단계 더 둔다.

### 5.1 ChangeEmployee 계층

```
             AbstractTransaction
                      △
                      │
              ChangeEmployeeTransaction      ◀── empId만 받음
                      △
        ┌─────────────┼──────────────────┐
        │             │                  │
ChangeName      ChangeAddress      ChangeClassification    ChangeMethod
Transaction     Transaction        Transaction             Transaction
                                          △                      △
                                          │                      │
                              ┌───────────┼────────┐    ┌────────┼───────┐
                              │           │        │    │        │       │
                          ChangeHourly  ChangeSalaried ... ChangeMail  ChangeDirect ChangeHold
```

`ChangeEmployeeTransaction`은 `Execute()`에서 직원을 찾고, 추상 메소드 `Change(Employee&)`를 호출한다. 하위 클래스는 `Change`만 구현하면 된다.

<details>
<summary>원문 C++ 코드 (ChangeEmployeeTransaction)</summary>

```cpp
// C++
void ChangeEmployeeTransaction::Execute() {
    Employee* e = GpayrollDatabase.GetEmployee(itsEmpId);
    if (e != 0)
        Change(*e);
    else
        throw("No such employee.");
}
```

</details>

```typescript
// TypeScript
abstract class ChangeEmployeeTransaction implements Transaction {
    constructor(protected readonly empId: number) {}

    protected abstract change(e: Employee): void;

    execute(): void {
        const e = payrollDatabase.getEmployee(this.empId);
        if (!e) {
            throw new Error("No such employee.");
        }
        this.change(e);
    }
}

class ChangeNameTransaction extends ChangeEmployeeTransaction {
    constructor(empId: number, private readonly newName: string) {
        super(empId);
    }
    protected change(e: Employee): void {
        e.setName(this.newName);
    }
}

class ChangeAddressTransaction extends ChangeEmployeeTransaction {
    constructor(empId: number, private readonly newAddress: string) {
        super(empId);
    }
    protected change(e: Employee): void {
        e.setAddress(this.newAddress);
    }
}
```

### 5.2 ChangeClassification — 또 한 단계의 템플릿 메소드

분류 변경(시급→월급 등)은 분류뿐 아니라 **일정(Schedule)** 도 함께 바꿔야 한다. 그래서 한 단계 더 추상화한다.

<details>
<summary>원문 C++ 코드 (ChangeClassificationTransaction)</summary>

```cpp
// C++
void ChangeClassificationTransaction::Change(Employee& e) {
    e.SetClassification(GetClassification());
    e.SetSchedule(GetSchedule());
}
```

</details>

```typescript
// TypeScript
abstract class ChangeClassificationTransaction extends ChangeEmployeeTransaction {
    protected abstract getClassification(): PaymentClassification;
    protected abstract getSchedule(): PaymentSchedule;

    protected change(e: Employee): void {
        e.setClassification(this.getClassification());
        e.setSchedule(this.getSchedule());
    }
}

class ChangeHourlyTransaction extends ChangeClassificationTransaction {
    constructor(empId: number, private readonly hourlyRate: number) {
        super(empId);
    }
    protected getClassification(): PaymentClassification {
        return new HourlyClassification(this.hourlyRate);
    }
    protected getSchedule(): PaymentSchedule {
        return new WeeklySchedule();
    }
}
```

### 5.3 ChangeAffiliation — 조합 가입/탈퇴

조합 관련 변경도 같은 패턴이다. `ChangeAffiliationTransaction`을 추상 기반으로 두고, `ChangeMember`(가입), `ChangeUnaffiliated`(탈퇴)가 이를 구현한다.

| 변경 종류 | 구체 클래스 | 조작 대상 |
|---|---|---|
| 이름 | `ChangeNameTransaction` | `Employee.name` |
| 주소 | `ChangeAddressTransaction` | `Employee.address` |
| 시급제로 | `ChangeHourlyTransaction` | classification + schedule |
| 월급제로 | `ChangeSalariedTransaction` | classification + schedule |
| 수당제로 | `ChangeCommissionedTransaction` | classification + schedule |
| 보류 지급 | `ChangeHoldTransaction` | method |
| 직접 입금 | `ChangeDirectTransaction` | method |
| 우편 지급 | `ChangeMailTransaction` | method |
| 조합 가입 | `ChangeMemberTransaction` | affiliation = `UnionAffiliation` |
| 조합 탈퇴 | `ChangeUnaffiliatedTransaction` | affiliation = `NoAffiliation` |

> **핵심 통찰**: 트랜잭션 종류가 늘어날 때마다 계층의 깊이가 한 단계씩 추가될 수 있다. 이는 **변경의 축**(축이 같은 것끼리 묶기)을 식별하는 작업이다. SRP(*Single Responsibility Principle*)와 OCP가 동시에 작동하는 모습이다.

---

## 6. PaydayTransaction — 가장 복잡한 로직

매일 실행되는 `PaydayTransaction`은 다음을 수행한다:

1. 모든 직원을 순회한다.
2. 직원이 **오늘 지급일인지** 확인한다 (`PaymentSchedule.IsPayDate()`).
3. 지급일이라면 `Paycheck`을 만들고, 직원의 `Payday()`를 호출한다.

### 6.1 동적 흐름

```
PaydayTransaction          Employee              Classification    Affiliation
       │                       │                       │                │
       │ for each employee     │                       │                │
       ├──IsPayDate(date)─────▶│                       │                │
       │◀──true/false──────────┤                       │                │
       │                       │                       │                │
       │ if pay day:           │                       │                │
       ├──Payday(paycheck)────▶│                       │                │
       │                       │──CalculatePay()──────▶│                │
       │                       │◀──gross pay───────────│                │
       │                       │──CalculateDeductions─────────────────▶ │
       │                       │◀──deductions──────────────────────────┤
       │                       │ (netPay = gross - deductions)         │
       │                       │ (Method.Pay(paycheck))                │
```

### 6.2 Employee::Payday 구현

<details>
<summary>원문 C++ 코드 (Employee::Payday, PaydayTransaction::Execute)</summary>

```cpp
// C++
void PaydayTransaction::Execute() {
    list<int> empIds;
    GpayrollDatabase.GetAllEmployeeIds(empIds);
    list<int>::iterator i = empIds.begin();
    for (; i != empIds.end(); i++) {
        Employee* e = GpayrollDatabase.GetEmployee(*i);
        if (e->IsPayDate(itsPayDate)) {
            Paycheck pc(e->GetPayPeriodStartDate(itsPayDate), itsPayDate);
            itsPaychecks[*i] = pc;
            e->Payday(pc);
        }
    }
}

void Employee::Payday(Paycheck& pc) {
    double grossPay = itsClassification->CalculatePay(pc);
    double deductions = itsAffiliation->CalculateDeductions(pc);
    double netPay = grossPay - deductions;
    pc.SetGrossPay(grossPay);
    pc.SetDeductions(deductions);
    pc.SetNetPay(netPay);
    itsPaymentMethod->Pay(pc);
}
```

</details>

```typescript
// TypeScript
class PaydayTransaction implements Transaction {
    private readonly paychecks = new Map<number, Paycheck>();

    constructor(private readonly payDate: Date) {}

    execute(): void {
        const empIds = payrollDatabase.getAllEmployeeIds();
        for (const id of empIds) {
            const e = payrollDatabase.getEmployee(id);
            if (!e) {
                continue;
            }
            if (e.isPayDate(this.payDate)) {
                const pc = new Paycheck(
                    e.getPayPeriodStartDate(this.payDate),
                    this.payDate,
                );
                this.paychecks.set(id, pc);
                e.payday(pc);
            }
        }
    }

    getPaycheck(empId: number): Paycheck | undefined {
        return this.paychecks.get(empId);
    }
}

class Employee {
    // ... 생성자, 필드 생략

    payday(pc: Paycheck): void {
        const grossPay = this.classification.calculatePay(pc);
        const deductions = this.affiliation.calculateDeductions(pc);
        const netPay = grossPay - deductions;
        pc.setGrossPay(grossPay);
        pc.setDeductions(deductions);
        pc.setNetPay(netPay);
        this.paymentMethod.pay(pc);
    }
}
```

### 6.3 각 분류의 CalculatePay 구현

다형성(*polymorphism - 같은 메시지에 객체마다 다르게 반응하는 능력*)이 빛을 발하는 지점이다.

<details>
<summary>원문 C++ 코드 (각 Classification의 CalculatePay)</summary>

```cpp
// C++
double SalariedClassification::CalculatePay(Paycheck& pc) const {
    return itsSalary;
}

double HourlyClassification::CalculatePay(Paycheck& pc) {
    double totalPay = 0.0;
    list<TimeCard*>::iterator i = itsTimeCards.begin();
    for (; i != itsTimeCards.end(); i++) {
        TimeCard* tc = *i;
        if (pc.IsInPayPeriod(tc->GetDate()))
            totalPay += CalculatePayForTimeCard(tc);
    }
    return totalPay;
}

double CommissionedClassification::CalculatePay(Paycheck& pc) {
    double totalPay = itsSalary;
    list<SalesReceipt*>::iterator i = itsSalesReceipts.begin();
    for (; i != itsSalesReceipts.end(); i++) {
        SalesReceipt* sr = *i;
        if (pc.IsInPayPeriod(sr->GetDate()))
            totalPay += itsCommissionRate * sr->GetAmount();
    }
    return totalPay;
}
```

</details>

```typescript
// TypeScript
class SalariedClassification implements PaymentClassification {
    constructor(private readonly salary: number) {}

    calculatePay(_pc: Paycheck): number {
        return this.salary;
    }
}

class HourlyClassification implements PaymentClassification {
    private readonly timeCards: TimeCard[] = [];

    constructor(private readonly hourlyRate: number) {}

    calculatePay(pc: Paycheck): number {
        let totalPay = 0.0;
        for (const tc of this.timeCards) {
            if (pc.isInPayPeriod(tc.getDate())) {
                totalPay += this.calculatePayForTimeCard(tc);
            }
        }
        return totalPay;
    }

    private calculatePayForTimeCard(tc: TimeCard): number {
        const hours = tc.getHours();
        const overtime = Math.max(0, hours - 8.0);
        const straightTime = hours - overtime;
        return straightTime * this.hourlyRate + overtime * this.hourlyRate * 1.5;
    }

    addTimeCard(tc: TimeCard): void {
        this.timeCards.push(tc);
    }
}

class CommissionedClassification implements PaymentClassification {
    private readonly salesReceipts: SalesReceipt[] = [];

    constructor(
        private readonly baseSalary: number,
        private readonly commissionRate: number,
    ) {}

    calculatePay(pc: Paycheck): number {
        let totalPay = this.baseSalary;
        for (const sr of this.salesReceipts) {
            if (pc.isInPayPeriod(sr.getDate())) {
                totalPay += this.commissionRate * sr.getAmount();
            }
        }
        return totalPay;
    }
}
```

### 6.4 Affiliation — 공제 계산

조합비 차감은 `UnionAffiliation`의 책임이다.

```typescript
// TypeScript
interface Affiliation {
    calculateDeductions(pc: Paycheck): number;
}

class NoAffiliation implements Affiliation {
    calculateDeductions(_pc: Paycheck): number {
        return 0;
    }
}

class UnionAffiliation implements Affiliation {
    private readonly serviceCharges: ServiceCharge[] = [];

    constructor(
        private readonly memberId: number,
        private readonly dues: number,
    ) {}

    calculateDeductions(pc: Paycheck): number {
        let total = 0;
        // 주당 조합비 × pay period 내 금요일 수
        total += this.dues * this.numberOfFridaysInPayPeriod(pc);
        // pay period 내 service charge 합계
        for (const sc of this.serviceCharges) {
            if (pc.isInPayPeriod(sc.getDate())) {
                total += sc.getAmount();
            }
        }
        return total;
    }

    private numberOfFridaysInPayPeriod(pc: Paycheck): number {
        // ... 구현 생략
        return 0;
    }
}
```

---

## 7. PaymentSchedule, PaymentMethod 다형성

`PaymentSchedule`은 지급일을 판정하고, `PaymentMethod`는 지급 채널을 결정한다. 각각의 구현은 자신의 책임만 안다.

| 인터페이스 | 구현 | 역할 |
|---|---|---|
| `PaymentSchedule` | `MonthlySchedule` | 월 마지막 영업일이 지급일 |
| `PaymentSchedule` | `WeeklySchedule` | 매주 금요일이 지급일 |
| `PaymentSchedule` | `BiweeklySchedule` | 격주 금요일이 지급일 |
| `PaymentMethod` | `HoldMethod` | 급여 담당자에게 보류 |
| `PaymentMethod` | `DirectMethod` | 은행 계좌 직접 입금 |
| `PaymentMethod` | `MailMethod` | 우편 발송 |

```typescript
// TypeScript
interface PaymentSchedule {
    isPayDate(date: Date): boolean;
    getPayPeriodStartDate(payDate: Date): Date;
}

class MonthlySchedule implements PaymentSchedule {
    isPayDate(date: Date): boolean {
        return this.isLastDayOfMonth(date);
    }
    getPayPeriodStartDate(payDate: Date): Date {
        return new Date(payDate.getFullYear(), payDate.getMonth(), 1);
    }
    private isLastDayOfMonth(date: Date): boolean {
        const next = new Date(date);
        next.setDate(next.getDate() + 1);
        return next.getMonth() !== date.getMonth();
    }
}

interface PaymentMethod {
    pay(pc: Paycheck): void;
}

class HoldMethod implements PaymentMethod {
    pay(pc: Paycheck): void {
        // 급여 담당자가 들고 있도록 표시만 한다
    }
}
```

---

## 8. 메인 프로그램 — 모든 조각을 잇다

메인 프로그램은 작다. 입력에서 트랜잭션 문자열을 읽고, 파서에게 `Transaction` 객체를 만들어 달라고 한 뒤, `Execute()`를 호출한다.

```typescript
// TypeScript
class TransactionApplication {
    constructor(
        private readonly source: TransactionSource,
        private readonly factory: TransactionFactory,
    ) {}

    run(): void {
        let line: string | null;
        while ((line = this.source.readNext()) !== null) {
            const transaction = this.factory.parse(line);
            transaction.execute();
        }
    }
}
```

> **핵심 통찰**: 메인은 트랜잭션의 구체 종류를 전혀 모른다. 파서가 `Transaction` 인터페이스 뒤로 다양성을 숨기기 때문이다. 새 트랜잭션을 추가해도 메인은 손대지 않는다 — 이것이 OCP의 약속이다.

전체 구조를 한눈에 보면:

```
   ┌─────────────────────────────────────────────────────┐
   │                  Main Program                       │
   │  while (line = source.read()):                      │
   │    factory.parse(line).execute()                    │
   └─────────────────────────────────────────────────────┘
                          │
                          ▼
   ┌─────────────────────────────────────────────────────┐
   │                Transaction (interface)              │
   └─────────────────────────────────────────────────────┘
              △               △                △
   ┌──────────┴──┐  ┌─────────┴──┐  ┌──────────┴────────┐
   │ AddEmployee │  │TimeCard /  │  │ChangeEmployee /   │
   │ Transaction │  │SalesReceipt│  │PaydayTransaction  │
   └──────┬──────┘  └──────┬─────┘  └──────────┬────────┘
          │                │                   │
          ▼                ▼                   ▼
   ┌────────────────────────────────────────────────────┐
   │                    Employee                        │
   │  - classification: PaymentClassification           │
   │  - schedule:       PaymentSchedule                 │
   │  - method:         PaymentMethod                   │
   │  - affiliation:    Affiliation                     │
   └────────────────────────────────────────────────────┘
          │                │                  │
          ▼                ▼                  ▼
     [Salaried,       [Monthly,           [Hold,
      Hourly,          Weekly,             Direct,
      Commissioned]    Biweekly]           Mail]
```

---

## 9. 자주 하는 실수

| 안티패턴 | 문제 | 해결 |
|---|---|---|
| 트랜잭션 안에 비즈니스 규칙을 넣는다 | 같은 규칙이 여러 트랜잭션에 중복된다 | 규칙은 모델(`Employee`, `Classification` 등)에 두고, 트랜잭션은 메시지만 보낸다 |
| 분류 변경에서 일정 변경을 잊는다 | 시급제로 바꿨는데 월급 일정 그대로 → 지급 못 받음 | `ChangeClassificationTransaction`이 항상 둘을 같이 바꾸도록 묶는다 |
| 데이터베이스 의사결정을 일찍 한다 | RDBMS 스키마에 도메인이 끌려간다 | 인메모리 퍼사드로 시작하고, 실제 영속성은 마지막에 결정한다 |
| 트랜잭션마다 if/else로 분류 분기 | 분류 추가 시 모든 트랜잭션 수정 | 다형성으로 위임 (`pc.calculatePay()`) |
| Affiliation을 직원 필드들로 흩뜨려 둠 | 조합 미가입 직원도 조합 관련 필드를 가지게 됨 | `Affiliation`을 객체로, 기본은 `NoAffiliation` |

---

## 10. TDD가 설계를 어떻게 진화시켰는가

이 장의 코드는 18장에서 그린 다이어그램을 그대로 옮긴 것이 아니다. 각 트랜잭션의 테스트를 먼저 작성하고, 통과시키고, 리팩토링하는 사이클을 수십 번 거쳤다. 그 과정에서 다음이 일어났다:

- `ChangeClassificationTransaction`이라는 중간 계층은 처음엔 없었다. `ChangeHourly`, `ChangeSalaried`를 각각 만들다 보니 중복이 보였고, 추출했다.
- `Affiliation`의 분리는 처음부터 명확하지 않았다. 조합비 공제 테스트를 작성하면서 `Employee` 안에 두려다, `Employee`의 변경 이유가 두 개가 됨을 발견하고 분리했다 (SRP).
- `Paycheck` 객체는 처음엔 단순한 숫자였다. pay period 정보를 들고 다녀야 한다는 것을 `IsInPayPeriod` 호출이 여기저기 등장하면서 알게 되었다.

> **Uncle Bob의 경험**: 완전한 형태의 코드를 본다고 해서 내가 처음부터 그런 형태의 코드를 작성했다고 오해하지 않기를 바란다. 사실 여러분이 보게 될 코드 묶음은 작성하는 사이에 수십 번의 수정과 컴파일 및 테스트로 아주 조금씩 코드를 발전시켰다. UML 다이어그램은 결과를 보여줄 뿐, 발견의 여정을 보여주지 않는다.

---

## 요약

- **Transaction 인터페이스 + 커맨드 패턴**: 모든 트랜잭션을 `Execute()` 하나로 통일하여 메인 프로그램을 OCP 준수 상태로 유지한다.
- **AddEmployee — 템플릿 메소드 패턴**: 공통 골격은 기반 클래스에, 분류/일정 생성은 하위 클래스에 위임한다.
- **ChangeEmployee — 다단계 추상화**: `ChangeEmployee` → `ChangeClassification` → 구체 변경의 계층은 변경 축을 따라 자라난다.
- **PayrollDatabase — 퍼사드로 영속성 미루기**: 인메모리로 시작하여 데이터베이스 결정을 끝까지 미룬다.
- **PaydayTransaction — 다형성의 종합**: 분류, 일정, 지급 방법, 가입 정보 모두 다형성으로 변경에 닫혀 있다.
- **TDD가 설계를 만든다**: 18장의 다이어그램은 출발점일 뿐, 테스트 사이클이 실제 구조를 발견하고 다듬는다.
- **자주 하는 실수**: 비즈니스 규칙을 트랜잭션에, 분류 변경에서 일정 변경 누락, 영속성 결정의 조기 확정, 분류 분기를 if/else로 처리 등은 SOLID 원칙으로 모두 회피 가능하다.
