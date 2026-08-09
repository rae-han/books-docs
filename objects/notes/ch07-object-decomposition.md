# Chapter 7: Object Decomposition (객체 분해)

## 핵심 질문

복잡한 소프트웨어 시스템을 어떤 기준으로 분해해야 하는가? 프로시저 추상화에서 데이터 추상화로의 역사적 진화 과정에서 기능 분해, 모듈, 추상 데이터 타입, 클래스는 각각 어떤 문제를 해결하고 어떤 한계를 드러내는가?

---

## 1. 추상화와 분해

### 1.1 인지 과부하와 단기 기억

사람의 기억은 **단기 기억**(*Short-term Memory - 정보에 직접 접근할 수 있지만 용량에 제한이 있는 기억 저장소*)과 **장기 기억**(*Long-term Memory - 수개월에서 평생에 걸쳐 정보를 보관하는 저장소*)으로 분류할 수 있다. 장기 기억은 매우 큰 저장 용량을 가지고 있으며 그 용량은 거의 무한대에 이르는 것으로 알려져 있다. 그러나 장기 기억 안에 보관된 지식은 직접 접근이 불가능하고, 먼저 단기 기억 영역으로 옮긴 후에 처리해야 한다.

단기 기억은 보관된 지식에 직접 접근할 수 있지만, 정보를 보관할 수 있는 속도와 공간 측면 모두에서 제약을 받는다:

- **공간적 제약**: 조지 밀러(George Miller)의 **매직 넘버 7(±2) 규칙**으로 널리 알려져 있다. 사람이 동시에 단기 기억 안에 저장할 수 있는 정보의 개수는 5개에서 많아봐야 9개 정도를 넘지 못한다.
- **시간적 제약**: 허버트 사이먼(Herbert A. Simon)에 따르면 사람이 새로운 정보를 받아들이는 데 약 5초 정도의 시간이 소요된다.

컴퓨터 프로그램을 작성할 때는 시간과 공간의 트레이드오프를 통해 효율을 향상시킬 수 있지만, 사람의 경우에는 트레이드오프의 여지가 전혀 없다. 시간과 공간 모두가 병목 지점으로 작용한다.

핵심은 실제로 문제를 해결하기 위해 사용하는 저장소가 장기 기억이 아니라 **단기 기억**이라는 점이다. 문제 해결에 필요한 요소의 수가 단기 기억의 용량을 초과하는 순간, 문제 해결 능력은 급격하게 떨어진다. 이런 현상을 **인지 과부하**(*Cognitive Overload*)라고 부른다.

### 1.2 추상화

인지 과부하를 방지하는 가장 좋은 방법은 단기 기억 안에 보관할 정보의 양을 조절하는 것이다. 한 번에 다뤄야 하는 정보의 수를 줄이기 위해 본질적인 정보만 남기고 불필요한 세부 사항을 걸러내면 문제를 단순화할 수 있다. 이처럼 불필요한 정보를 제거하고 현재의 문제 해결에 필요한 핵심만 남기는 작업을 **추상화**라고 부른다.

### 1.3 분해

가장 일반적인 추상화 방법은 한 번에 다뤄야 하는 문제의 크기를 줄이는 것이다. 사람들은 한 번에 해결하기 어려운 커다란 문제에 맞닥뜨릴 경우, 해결 가능한 작은 문제로 나누는 경향이 있다. 이처럼 큰 문제를 해결 가능한 작은 문제로 나누는 작업을 **분해**(*Decomposition*)라고 부른다.

분해의 목적은 큰 문제를 인지 과부하의 부담 없이 단기 기억 안에서 한 번에 처리할 수 있는 규모의 문제로 나누는 것이다.

### 1.4 청크와 추상화의 확장

조지 밀러의 매직 넘버 7은 정보의 가장 작은 단위로서의 개별 항목을 의미하는 것이 아니라, 하나의 단위로 취급될 수 있는 논리적인 **청크**(*Chunk*)를 의미한다. 청크는 더 작은 청크를 포함할 수 있으며 연속적으로 분해 가능하다. 예를 들어, 임의로 조합된 11자리 정수 8개를 한꺼번에 기억하는 것은 힘들지만, 11자리 정수를 전화번호라는 개념적 청크로 묶으면 8명에 대한 전화번호(88개의 숫자)를 기억할 수 있도록 인지 능력을 향상시킬 수 있다.

한 번에 단기 기억에 담을 수 있는 추상화의 수에는 한계가 있지만, 추상화를 더 큰 규모의 추상화로 압축시킴으로써 단기 기억의 한계를 초월할 수 있다.

> **핵심 통찰**: 추상화와 분해는 인간이 세계를 인식하고 반응하기 위해 사용하는 가장 기본적인 사고 도구다. 복잡성이 존재하는 곳에 추상화와 분해 역시 함께 존재한다. 인류가 창조한 가장 복잡한 분야인 소프트웨어 개발 영역에서 추상화와 분해가 핵심 도구로 사용되는 것은 당연한 일이다.

---

## 2. 프로시저 추상화와 데이터 추상화

프로그래밍 언어의 발전은 좀 더 효과적인 추상화를 이용해 복잡성을 극복하려는 개발자들의 노력에서 출발했다. 어셈블리어는 기계어에 인간이 이해할 수 있는 상징을 부여하려는 노력의 결과다. 고수준 언어는 기계적인 사고를 강요하는 낮은 수준의 명령어들을 탈피해서 인간의 눈높이에 맞는 추상화를 제공하려는 시도의 결과였다.

현대적인 프로그래밍 언어를 특징짓는 중요한 두 가지 추상화 메커니즘이 있다:

| 추상화 메커니즘 | 대상 | 설명 |
|---|---|---|
| **프로시저 추상화**(*Procedure Abstraction*) | 무엇을 해야 하는지(기능) | 소프트웨어가 수행해야 할 작업을 추상화한다 |
| **데이터 추상화**(*Data Abstraction*) | 무엇을 알아야 하는지(데이터) | 소프트웨어가 처리해야 할 정보를 추상화한다 |

프로그래밍 패러다임은 프로그래밍을 구성하기 위해 사용하는 추상화의 종류와 이 추상화를 이용해 소프트웨어를 분해하는 방법이라는 두 가지 요소로 결정된다. 시스템을 분해하는 방법을 결정하려면 먼저 프로시저 추상화를 중심으로 할 것인지, 데이터 추상화를 중심으로 할 것인지를 결정해야 한다.

```
                    시스템 분해 방법
                         │
            ┌────────────┴────────────┐
            ▼                         ▼
     프로시저 추상화              데이터 추상화
            │                         │
            ▼                    ┌────┴────┐
     기능 분해                   ▼         ▼
  (알고리즘 분해)         타입 추상화    프로시저 추상화
                          (ADT)        (객체지향)
```

- **프로시저 추상화 중심**: 기능 분해(*Functional Decomposition*) 또는 알고리즘 분해(*Algorithmic Decomposition*)의 길로 들어선다.
- **데이터 추상화 중심**: 다시 두 가지 중 하나를 선택해야 한다.
  - 데이터를 중심으로 **타입을 추상화**하는 것: **추상 데이터 타입**(*Abstract Data Type, ADT*)
  - 데이터를 중심으로 **프로시저를 추상화**하는 것: **객체지향**(*Object-Oriented*)

프로그래밍 언어의 관점에서 객체지향이란 데이터를 중심으로 데이터 추상화와 프로시저 추상화를 통합한 객체를 이용해 시스템을 분해하는 방법이다. 대부분의 객체지향 언어는 이런 객체를 구현하기 위해 **클래스**라는 도구를 제공한다.

> 객체지향이 전통적인 기능 분해 방법에 비해 효과적이라고 말하는 이유가 무엇일까? 이 질문의 해답을 찾기 위해서는 전통적인 기능 분해 방법에서 시작해서 객체지향 분해 방법에 이르는 좌절과 극복의 역사를 살펴봐야 한다.

---

## 3. 프로시저 추상화와 기능 분해

### 3.1 메인 함수로서의 시스템

기능과 데이터의 첫 번째 전쟁에서 승리한 것은 기능이었다. 기능은 오랜 시간 동안 시스템을 분해하기 위한 기준으로 사용됐다. 기능 분해의 관점에서 추상화의 단위는 **프로시저**이며 시스템은 프로시저를 단위로 분해된다.

프로시저는 반복적으로 실행되거나 거의 유사하게 실행되는 작업들을 하나의 장소에 모아놓음으로써 로직을 재사용하고 중복을 방지할 수 있는 추상화 방법이다. 프로시저를 추상화라고 부르는 이유는 내부의 상세한 구현 내용을 모르더라도 인터페이스만 알면 프로시저를 사용할 수 있기 때문이다. 따라서 프로시저는 잠재적으로 정보 은닉의 가능성을 제시하지만, 프로시저만으로 효과적인 정보 은닉 체계를 구축하는 데는 한계가 있다.

기능 분해 관점에서 시스템은 입력값을 계산해서 출력값을 반환하는 수학의 함수와 동일하다. 시스템은 필요한 더 작은 작업으로 분해될 수 있는 **하나의 커다란 메인 함수**다.

전통적인 기능 분해 방법은 **하향식 접근법**(*Top-Down Approach*)을 따른다. 하향식 접근법이란 시스템을 구성하는 가장 최상위 기능을 정의하고, 이 최상위 기능을 좀 더 작은 단계의 하위 기능으로 분해해 나가는 방법을 말한다. 분해는 세분화된 마지막 하위 기능이 프로그래밍 언어로 구현 가능한 수준이 될 때까지 계속된다.

### 3.2 급여 관리 시스템: 기능 분해 예제

간단한 급여 관리 시스템을 기능 분해 방법으로 구현해 보자. 연초에 회사는 매달 지급해야 하는 기본급에 대해 직원과 협의하며 이 금액을 12개월 동안 동일하게 직원들에게 지급한다. 회사는 급여 지급 시 소득세율에 따라 일정 금액의 세금을 공제한다.

```
급여 = 기본급 - (기본급 × 소득세율)
```

먼저 급여 관리 시스템에 대한 추상적인 최상위 문장을 기술함으로써 시작한다.

```
직원의 급여를 계산한다
```

이 문장을 좀 더 세부적인 절차로 구체화한다:

```
직원의 급여를 계산한다
    사용자로부터 소득세율을 입력받는다
        "세율을 입력하세요: "라는 문장을 화면에 출력한다
        키보드를 통해 세율을 입력받는다
    직원의 급여를 계산한다
        전역 변수에 저장된 직원의 기본급 정보를 얻는다
        급여를 계산한다
    양식에 맞게 결과를 출력한다
        "이름: {직원명}, 급여: {계산된 금액}" 형식에 따라 출력 문자열을 생성한다
```

기능 분해의 결과는 최상위 기능을 수행하는 데 필요한 절차들을 실행되는 시간 순서에 따라 나열한 것이다.

```
             ┌───────────────┐
             │  직원 정보     │
             └───────┬───────┘
                     ▼
     ┌───────────────────────────────┐
     │     급여 관리 시스템 (main)     │──▶ 급여
     └───────────────────────────────┘
                     ▲
             ┌───────┴───────┐
             │  소득세율      │
             └───────────────┘
```

기능 분해 방법에서는 **기능을 중심으로 필요한 데이터를 결정한다**. 기능 분해라는 무대의 주연은 기능이고 데이터는 기능을 보조하는 조연의 역할에 머무른다.

이제 코드로 구현해 보자. 원서에서는 Ruby를 사용하지만 여기서는 TypeScript로 변환한다.

<details>
<summary>원문 Ruby 코드</summary>

```ruby
# Ruby
$employees = ["직원A", "직원B", "직원C"]
$basePays = [400, 300, 250]

def main(name)
  taxRate = getTaxRate()
  pay = calculatePayFor(name, taxRate)
  puts(describeResult(name, pay))
end

def getTaxRate()
  print("세율을 입력하세요: ")
  return gets().chomp().to_f()
end

def calculatePayFor(name, taxRate)
  index = $employees.index(name)
  basePay = $basePays[index]
  return basePay - (basePay * taxRate)
end

def describeResult(name, pay)
  return "이름: #{name}, 급여: #{pay}"
end

main("직원C")
```

</details>

```typescript
// TypeScript
const employees = ["직원A", "직원B", "직원C"];
const basePays = [400, 300, 250];

function main(name: string): void {
    const taxRate = getTaxRate();
    const pay = calculatePayFor(name, taxRate);
    console.log(describeResult(name, pay));
}

function getTaxRate(): number {
    // 사용자로부터 소득세율을 입력받는다
    return parseFloat(prompt("세율을 입력하세요: ") ?? "0");
}

function calculatePayFor(name: string, taxRate: number): number {
    const index = employees.indexOf(name);
    const basePay = basePays[index];
    return basePay - basePay * taxRate;
}

function describeResult(name: string, pay: number): string {
    return `이름: ${name}, 급여: ${pay}`;
}

main("직원C");
```

하향식 기능 분해 방식으로 설계한 시스템은 메인 함수를 루트로 하는 **트리**로 표현할 수 있다.

```
                main
              ╱  │  ╲
             ╱   │   ╲
            ▼    ▼    ▼
   getTaxRate  calculatePayFor  describeResult
```

### 3.3 하향식 기능 분해의 문제점

하향식 기능 분해 방법은 겉으로는 이상적으로 보이지만 실제로 적용하면 다음과 같은 문제에 직면한다:

1. **시스템은 하나의 메인 함수로 구성돼 있지 않다**
2. **기능 추가나 요구사항 변경으로 인해 메인 함수를 빈번하게 수정해야 한다**
3. **비즈니스 로직이 사용자 인터페이스와 강하게 결합된다**
4. **하향식 분해는 너무 이른 시기에 함수들의 실행 순서를 고정시키기 때문에 유연성과 재사용성이 저하된다**
5. **데이터 형식이 변경될 경우 파급 효과를 예측할 수 없다**

#### 하나의 메인 함수라는 비현실적인 아이디어

어떤 시스템도 최초 릴리스 당시의 모습을 그대로 유지하지는 않는다. 시간이 지나면서 지속적으로 새로운 기능을 추가하게 된다. 대부분의 경우 추가되는 기능은 최초에 배포된 메인 함수의 일부가 아닐 것이다. 결국 처음에는 중요하게 생각됐던 메인 함수는 동등하게 중요한 여러 함수들 중 하나로 전락하고 만다.

> 대부분의 시스템에서 하나의 메인 기능이란 개념은 존재하지 않는다. 모든 기능들은 규모라는 측면에서 차이가 있을 수는 있겠지만 기능성의 측면에서는 동등하게 독립적이고 완결된 하나의 기능을 표현한다. 버트란드 마이어의 말을 인용하자면 "실제 시스템에 정상(top)이란 존재하지 않는다."

#### 메인 함수의 빈번한 재설계

급여 관리 시스템에 "모든 직원의 기본급 총합을 구하는 기능"을 추가해 달라는 새로운 요구사항이 접수됐다고 가정하자.

<details>
<summary>원문 Ruby 코드</summary>

```ruby
# Ruby
def sumOfBasePays()
  result = 0
  for basePay in $basePays
    result += basePay
  end
  puts(result)
end
```

</details>

```typescript
// TypeScript
function sumOfBasePays(): void {
    let result = 0;
    for (const basePay of basePays) {
        result += basePay;
    }
    console.log(result);
}
```

문제는 기존의 `main` 함수는 개별 직원의 급여를 계산하는 것이 목적이므로, 전체 직원의 기본급 총액을 계산하는 `sumOfBasePays` 함수가 들어설 자리가 마땅치 않다는 것이다. `sumOfBasePays`와 기존의 `main` 로직은 개념적으로 동등한 수준의 작업을 수행한다.

해결 방법은 기존 `main`의 로직을 `calculatePay`라는 함수로 추출한 후, `main` 함수에서 두 함수를 선택적으로 호출하도록 수정하는 것이다:

<details>
<summary>원문 Ruby 코드</summary>

```ruby
# Ruby
def main(operation, args={})
  case operation
  when :pay then calculatePay(args[:name])
  when :basePays then sumOfBasePays()
  end
end

def calculatePay(name)
  taxRate = getTaxRate()
  pay = calculatePayFor(name, taxRate)
  puts(describeResult(name, pay))
end
```

</details>

```typescript
// TypeScript
function main(operation: "pay" | "basePays", args?: { name: string }): void {
    switch (operation) {
        case "pay":
            calculatePay(args!.name);
            break;
        case "basePays":
            sumOfBasePays();
            break;
    }
}

function calculatePay(name: string): void {
    const taxRate = getTaxRate();
    const pay = calculatePayFor(name, taxRate);
    console.log(describeResult(name, pay));
}
```

새로운 정상(top)을 추가할 때마다 기존의 메인 함수를 수정할 수밖에 없다. 기존 코드의 빈번한 수정으로 인한 버그 발생 확률이 높아지고 시스템은 변경에 취약해진다.

#### 비즈니스 로직과 사용자 인터페이스의 결합

하향식 접근법은 비즈니스 로직을 설계하는 초기 단계부터 입력 방법과 출력 양식을 함께 고민하도록 강요한다. "사용자로부터 소득세율을 입력받아 급여를 계산한 후 계산된 결과를 화면에 출력한다"라는 말에는 비즈니스 로직의 관심사와 사용자 인터페이스의 관심사가 한데 섞여 있다.

문제는 비즈니스 로직과 사용자 인터페이스가 변경되는 빈도가 다르다는 것이다. 사용자 인터페이스는 시스템 내에서 가장 자주 변경되는 부분이다. 하향식 접근법은 이 둘을 한데 섞기 때문에 사용자 인터페이스를 변경하는 경우 비즈니스 로직까지 변경에 영향을 받는다. 급여 관리 시스템의 사용자 인터페이스를 GUI 기반으로 변경한다고 하면? 하향식 접근법을 따르는 현재의 설계에서는 전체 구조를 재설계하는 것이 유일한 방법이다.

#### 성급하게 결정된 실행 순서

하향식으로 기능을 분해하는 과정은 하나의 함수를 더 작은 함수로 분해하고, 분해된 함수들의 실행 순서를 결정하는 작업으로 요약할 수 있다. 이것은 설계를 시작하는 시점부터 시스템이 **무엇**(what)을 해야 하는지가 아니라 **어떻게**(how) 동작해야 하는지에 집중하도록 만든다.

기능 분해 방식은 **중앙 집중 제어 스타일**(*Centralized Control Style*)의 형태를 띨 수밖에 없다. 모든 중요한 제어 흐름의 결정이 상위 함수에서 이뤄지고 하위 함수는 상위 함수의 흐름에 따라 적절한 시점에 호출된다. 기능이 추가되거나 변경될 때마다 초기에 결정된 함수들의 제어 구조가 올바르지 않다는 것이 판명된다.

이를 해결할 수 있는 한 가지 방법은 자주 변경되는 시간적인 제약(**시간 제약**, *Temporal Constraint*)에 대한 미련을 버리고 좀 더 안정적인 **논리적 제약**(*Logical Constraint*)을 설계의 기준으로 삼는 것이다. 객체지향은 함수 간의 호출 순서가 아니라 객체 사이의 논리적인 관계를 중심으로 설계를 이끌어 나간다.

하향식 접근법을 통해 분해한 함수들은 **재사용하기도 어렵다**. 모든 함수는 상위 함수를 분해하는 과정에서 필요에 따라 식별되며, 상위 함수가 강요하는 문맥(context) 안에서만 의미를 가지기 때문이다. 하향식 설계와 관련된 모든 문제의 원인은 **결합도**다. 함수는 상위 함수가 강요하는 문맥에 강하게 결합되고, 함께 절차를 구성하는 다른 함수들과 시간적으로 강하게 결합돼 있다.

#### 데이터 변경으로 인한 파급 효과

하향식 기능 분해의 가장 큰 문제점은 어떤 데이터를 어떤 함수가 사용하고 있는지를 추적하기 어렵다는 것이다. 개별 함수의 입장에서 사용하는 데이터를 파악하는 것은 어렵지 않다. 그러나 반대로 어떤 데이터가 어떤 함수에 의존하고 있는지를 파악하는 것은 모든 함수를 열어 데이터를 사용하고 있는지를 모두 확인해봐야 하기 때문에 어렵다.

급여 관리 시스템에 **아르바이트 직원**에 대한 급여 계산 기능을 추가해 보자. 아르바이트 직원은 고정된 급여를 받는 정규직원과 달리 일한 시간에 시급을 곱한 금액만큼을 지급받는다.

<details>
<summary>원문 Ruby 코드</summary>

```ruby
# Ruby
$employees = ["직원A", "직원B", "직원C", "아르바이트D", "아르바이트E", "아르바이트F"]
$basePays = [400, 300, 250, 1, 1, 1.5]
$hourlys = [false, false, false, true, true, true]
$timeCards = [0, 0, 0, 120, 120, 120]

def calculateHourlyPayFor(name, taxRate)
  index = $employees.index(name)
  basePay = $basePays[index] * $timeCards[index]
  return basePay - (basePay * taxRate)
end

def hourly?(name)
  return $hourlys[$employees.index(name)]
end

def calculatePay(name)
  taxRate = getTaxRate()
  if (hourly?(name)) then
    pay = calculateHourlyPayFor(name, taxRate)
  else
    pay = calculatePayFor(name, taxRate)
  end
  puts(describeResult(name, pay))
end
```

</details>

```typescript
// TypeScript
const employees = ["직원A", "직원B", "직원C", "아르바이트D", "아르바이트E", "아르바이트F"];
const basePays = [400, 300, 250, 1, 1, 1.5];
const hourlys = [false, false, false, true, true, true];
const timeCards = [0, 0, 0, 120, 120, 120];

function hourly(name: string): boolean {
    return hourlys[employees.indexOf(name)];
}

function calculateHourlyPayFor(name: string, taxRate: number): number {
    const index = employees.indexOf(name);
    const basePay = basePays[index] * timeCards[index];
    return basePay - basePay * taxRate;
}

function calculatePay(name: string): void {
    const taxRate = getTaxRate();
    const pay = hourly(name)
        ? calculateHourlyPayFor(name, taxRate)
        : calculatePayFor(name, taxRate);
    console.log(describeResult(name, pay));
}
```

모든 코드의 수정이 완료됐을까? 안타깝게도 시스템 배포 후 사용자들로부터 `sumOfBasePays` 함수의 결과가 이상하다는 리포트가 전달되기 시작했다. 오랜 디버깅 끝에, `basePays`와 `employees`에 아르바이트 직원에 대한 정보를 추가했기 때문이라는 사실을 알아낼 수 있었다. `sumOfBasePays` 함수도 함께 수정해야 했던 것이다.

<details>
<summary>원문 Ruby 코드</summary>

```ruby
# Ruby (수정된 버전)
def sumOfBasePays()
  result = 0
  for name in $employees
    if (not hourly?(name)) then
      result += $basePays[$employees.index(name)]
    end
  end
  puts(result)
end
```

</details>

```typescript
// TypeScript (수정된 버전)
function sumOfBasePays(): void {
    let result = 0;
    for (const name of employees) {
        if (!hourly(name)) {
            result += basePays[employees.indexOf(name)];
        }
    }
    console.log(result);
}
```

누가 전역 변수를 추가했다고 해서 기존의 `sumOfBasePays` 함수가 수정될 것이라는 것을 예상할 수 있을 것인가? `sumOfBasePays` 함수는 에러도 발생하지 않았고 `basePays`에 저장된 값을 정상적으로 반환했다. 문제는 그 값이 잘못된 값이라는 것이다.

> **핵심 통찰**: 데이터 변경으로 인한 영향을 최소화하려면 데이터와 함께 변경되는 부분과 그렇지 않은 부분을 명확하게 분리해야 한다. 이를 위해 데이터와 함께 변경되는 부분을 하나의 구현 단위로 묶고, 외부에서는 제공되는 함수만 이용해 데이터에 접근해야 한다. 즉, 잘 정의된 퍼블릭 인터페이스를 통해 데이터에 대한 접근을 통제해야 한다.

### 3.4 언제 하향식 분해가 유용한가?

하향식 아이디어가 매력적인 이유는 설계가 어느 정도 안정화된 후에는 설계의 다양한 측면을 논리적으로 설명하고 문서화하기에 용이하기 때문이다. 그러나 설계를 문서화하는 데 적절한 방법이 좋은 구조를 설계할 수 있는 방법과 동일한 것은 아니다.

> 하향식은 이미 완전히 이해된 사실을 서술하기에 적합한 방법이다. 그러나 하향식은 새로운 것을 개발하고, 설계하고, 발견하는 데는 적합한 방법이 아니다. - Michael Jackson

하향식 분해는 작은 프로그램과 개별 알고리즘을 위해서는 유용한 패러다임으로 남아 있다. 특히 프로그래밍 과정에서 이미 해결된 알고리즘을 문서화하고 서술하는 데는 훌륭한 기법이다. 그러나 실제로 동작하는 커다란 소프트웨어를 설계하는 데 적합한 방법은 아니다.

---

## 4. 모듈

### 4.1 정보 은닉과 모듈

시스템의 변경을 관리하는 기본적인 전략은 함께 변경되는 부분을 하나의 구현 단위로 묶고 퍼블릭 인터페이스를 통해서만 접근하도록 만드는 것이다. 즉, **기능을 기반으로 시스템을 분해하는 것이 아니라 변경의 방향에 맞춰 시스템을 분해**하는 것이다.

데이비드 파나스(David Parnas)는 1972년에 발표한 논문 "On the Criteria To Be Used in Decomposing Systems Into Modules"에서 **정보 은닉**(*Information Hiding*)의 개념을 소개했다. 정보 은닉은 시스템을 모듈 단위로 분해하기 위한 기본 원리로, 시스템에서 자주 변경되는 부분을 상대적으로 덜 변경되는 안정적인 인터페이스 뒤로 감춰야 한다는 것이 핵심이다.

> 모듈은 서브프로그램이라기보다는 책임의 할당이다. 분할된 모듈은 다른 모듈에 대해 감춰야 하는 설계 결정에 따라 특징지어진다. 어려운 설계 결정이나 변화할 것 같은 설계 결정들의 목록을 사용해 설계를 시작할 것을 권장한다. - David Parnas

정보 은닉은 외부에 감춰야 하는 비밀에 따라 시스템을 분할하는 모듈 분할 원리다. 모듈은 변경될 가능성이 있는 비밀을 내부로 감추고, 잘 정의되고 쉽게 변경되지 않을 퍼블릭 인터페이스를 외부에 제공해서 내부의 비밀에 함부로 접근하지 못하게 한다.

모듈은 다음과 같은 **두 가지 비밀**을 감춰야 한다:

| 비밀의 종류 | 설명 | 목적 |
|---|---|---|
| **복잡성** | 모듈이 너무 복잡한 경우 이해하고 사용하기가 어렵다 | 간단한 인터페이스를 제공해서 모듈의 복잡도를 낮춘다 |
| **변경 가능성** | 변경 가능한 설계 결정이 외부에 노출될 경우 파급 효과가 커진다 | 변경 시 하나의 모듈만 수정하면 되도록 감춘다 |

### 4.2 급여 관리 시스템에 모듈 적용

직원 정보와 관련된 데이터를 `Employees` 모듈 내부로 숨겨 보자.

<details>
<summary>원문 Ruby 코드</summary>

```ruby
# Ruby
module Employees
  $employees = ["직원A", "직원B", "직원C", "아르바이트D", "아르바이트E", "아르바이트F"]
  $basePays = [400, 300, 250, 1, 1, 1.5]
  $hourlys = [false, false, false, true, true, true]
  $timeCards = [0, 0, 0, 120, 120, 120]

  def Employees.calculatePay(name, taxRate)
    if (Employees.hourly?(name)) then
      pay = Employees.calculateHourlyPayFor(name, taxRate)
    else
      pay = Employees.calculatePayFor(name, taxRate)
    end
  end

  def Employees.hourly?(name)
    return $hourlys[$employees.index(name)]
  end

  def Employees.calculateHourlyPayFor(name, taxRate)
    index = $employees.index(name)
    basePay = $basePays[index] * $timeCards[index]
    return basePay - (basePay * taxRate)
  end

  def Employees.calculatePayFor(name, taxRate)
    index = $employees.index(name)
    basePay = $basePays[index]
    return basePay - (basePay * taxRate)
  end

  def Employees.sumOfBasePays()
    result = 0
    for name in $employees
      if (not Employees.hourly?(name)) then
        result += $basePays[$employees.index(name)]
      end
    end
    return result
  end
end
```

</details>

```typescript
// TypeScript
namespace Employees {
    const employees = ["직원A", "직원B", "직원C", "아르바이트D", "아르바이트E", "아르바이트F"];
    const basePays = [400, 300, 250, 1, 1, 1.5];
    const hourlys = [false, false, false, true, true, true];
    const timeCards = [0, 0, 0, 120, 120, 120];

    function isHourly(name: string): boolean {
        return hourlys[employees.indexOf(name)];
    }

    function calculateHourlyPayFor(name: string, taxRate: number): number {
        const index = employees.indexOf(name);
        const basePay = basePays[index] * timeCards[index];
        return basePay - basePay * taxRate;
    }

    function calculatePayFor(name: string, taxRate: number): number {
        const index = employees.indexOf(name);
        const basePay = basePays[index];
        return basePay - basePay * taxRate;
    }

    export function calculatePay(name: string, taxRate: number): number {
        if (isHourly(name)) {
            return calculateHourlyPayFor(name, taxRate);
        }
        return calculatePayFor(name, taxRate);
    }

    export function sumOfBasePays(): number {
        let result = 0;
        for (const name of employees) {
            if (!isHourly(name)) {
                result += basePays[employees.indexOf(name)];
            }
        }
        return result;
    }
}
```

전역 변수였던 `employees`, `basePays`, `hourlys`, `timeCards`가 `Employees`라는 모듈 내부로 숨겨져 있다는 것에 주목하라. 외부에서는 직원 정보를 관리하는 데이터에 직접 접근할 수 없다. 외부에서는 `Employees` 모듈이 제공하는 퍼블릭 인터페이스(`calculatePay`, `sumOfBasePays`)를 통해서만 내부 변수를 조작할 수 있다.

이제 `main` 함수가 `Employees` 모듈의 기능을 사용하도록 코드를 수정한다:

```typescript
// TypeScript
function calculatePay(name: string): void {
    const taxRate = getTaxRate();
    const pay = Employees.calculatePay(name, taxRate);
    console.log(describeResult(name, pay));
}

function sumOfBasePays(): void {
    console.log(Employees.sumOfBasePays());
}
```

### 4.3 모듈의 장점과 한계

**장점**:

1. **모듈 내부의 변수가 변경되더라도 모듈 내부에만 영향을 미친다**: 어떤 데이터가 변경됐을 때 영향을 받는 함수를 찾기 위해 해당 데이터를 정의한 모듈만 검색하면 된다. 모듈은 데이터 변경으로 인한 파급 효과를 제어할 수 있다.
2. **비즈니스 로직과 사용자 인터페이스에 대한 관심사를 분리한다**: `Employees` 모듈은 비즈니스 로직의 관심사만 담당하며, 사용자 인터페이스 관련 관심사는 모듈을 사용하는 `main` 함수 쪽에 위치한다. GUI 같은 다른 형식의 사용자 인터페이스를 추가하더라도 비즈니스 로직은 변경되지 않는다.
3. **전역 변수와 전역 함수를 제거함으로써 네임스페이스 오염을 방지한다**: 변수와 함수를 모듈 내부에 포함시키기 때문에 다른 모듈에서도 동일한 이름을 사용할 수 있다.

모듈은 기능이 아니라 **변경의 정도에 따라 시스템을 분해**하게 한다. 각 모듈은 외부에 감춰야 하는 비밀과 관련성 높은 데이터와 함수의 집합이다. 모듈 내부는 높은 응집도를 유지하고, 모듈과 모듈 사이에는 퍼블릭 인터페이스를 통해서만 통신하므로 낮은 결합도를 유지한다.

**한계**: 모듈의 가장 큰 단점은 **인스턴스의 개념을 제공하지 않는다**는 점이다. `Employees` 모듈은 단지 회사에 속한 모든 직원 정보를 가지고 있는 모듈일 뿐이다. 좀 더 높은 수준의 추상화를 위해서는 직원 전체가 아니라 **개별 직원을 독립적인 단위**로 다룰 수 있어야 한다. 다수의 직원 인스턴스가 존재하는 추상화 메커니즘이 필요한 것이다. 이를 만족시키기 위해 등장한 개념이 바로 **추상 데이터 타입**이다.

---

## 5. 데이터 추상화와 추상 데이터 타입

### 5.1 추상 데이터 타입의 탄생

프로그래밍 언어에서 **타입**(*Type*)이란 변수에 저장할 수 있는 내용물의 종류와 변수에 적용될 수 있는 연산의 가짓수를 의미한다. 정수 타입의 변수는 덧셈 연산을 이용해 값을 더할 수 있고, 문자열 타입의 변수는 연결 연산을 이용해 두 문자열을 하나로 합칠 수 있다. 타입은 저장된 값에 대해 수행될 수 있는 연산의 집합을 결정하기 때문에, 변수의 값이 어떻게 행동할 것이라는 것을 예측할 수 있게 한다.

기능 분해의 시대에 사용되던 절차형 언어들은 적은 수의 **내장 타입**(*Built-in Type*)만을 제공했으며, 새로운 타입을 추가하는 것이 불가능하거나 제한적이었다.

바바라 리스코프(Barbara Liskov)는 프로시저 추상화의 한계를 인지하고 대안을 탐색한 선각자 중 한 명이다. 리스코프는 논문 "Programming with Abstract Data Types"(1974)에서 프로시저 추상화를 보완하기 위해 **데이터 추상화**의 개념을 제안했다.

> 추상 데이터 타입은 추상 객체의 클래스를 정의한 것으로, 추상 객체에 사용할 수 있는 오퍼레이션을 이용해 규정된다. 추상 데이터 객체를 사용할 때 프로그래머는 오직 객체가 외부에 제공하는 행위에만 관심을 가지며, 행위가 구현되는 세부적인 사항에 대해서는 무시한다. - Barbara Liskov

리스코프의 업적은 소프트웨어를 이용해 표현할 수 있는 추상화의 수준을 한 단계 높였다는 점이다. 사람들은 '직원의 급여를 계산한다'라는 하나의 커다란 절차를 이용해 사고하기보다는 '직원'과 '급여'라는 추상적인 개념들을 머릿속에 떠올린 후 이들을 이용해 '계산'에 필요한 절차를 생각하는 데 익숙하다.

추상 데이터 타입을 구현하려면 다음과 같은 특성을 위한 프로그래밍 언어의 지원이 필요하다:

1. **타입 정의를 선언**할 수 있어야 한다
2. 타입의 인스턴스를 다루기 위해 사용할 수 있는 **오퍼레이션의 집합을 정의**할 수 있어야 한다
3. 제공된 오퍼레이션을 통해서만 조작할 수 있도록 **데이터를 외부로부터 보호**할 수 있어야 한다
4. 타입에 대해 **여러 개의 인스턴스를 생성**할 수 있어야 한다

### 5.2 급여 관리 시스템에 추상 데이터 타입 적용

추상 데이터 타입으로 급여 관리 시스템을 개선해 보자. 원서에서는 Ruby의 `Struct`를 사용한다.

<details>
<summary>원문 Ruby 코드</summary>

```ruby
# Ruby
Employee = Struct.new(:name, :basePay, :hourly, :timeCard) do
  def calculatePay(taxRate)
    if (hourly) then
      return calculateHourlyPay(taxRate)
    end
    return calculateSalariedPay(taxRate)
  end

  def monthlyBasePay()
    if (hourly) then return 0 end
    return basePay
  end

  private
  def calculateHourlyPay(taxRate)
    return (basePay * timeCard) - (basePay * timeCard) * taxRate
  end

  def calculateSalariedPay(taxRate)
    return basePay - (basePay * taxRate)
  end
end
```

</details>

```typescript
// TypeScript
class Employee {
    constructor(
        public readonly name: string,
        private readonly basePay: number,
        private readonly hourly: boolean,
        private readonly timeCard: number
    ) {}

    calculatePay(taxRate: number): number {
        if (this.hourly) {
            return this.calculateHourlyPay(taxRate);
        }
        return this.calculateSalariedPay(taxRate);
    }

    monthlyBasePay(): number {
        if (this.hourly) return 0;
        return this.basePay;
    }

    private calculateHourlyPay(taxRate: number): number {
        const pay = this.basePay * this.timeCard;
        return pay - pay * taxRate;
    }

    private calculateSalariedPay(taxRate: number): number {
        return this.basePay - this.basePay * taxRate;
    }
}
```

외부에서 인자로 전달받던 직원의 이름은 이제 `Employee` 타입의 내부에 포함돼 있으므로 `calculatePay` 오퍼레이션의 인자로 받을 필요가 없다. 따라서 직원을 지정해야 했던 모듈 방식보다 추상 데이터 타입에 정의된 오퍼레이션의 시그니처가 더 간단하다.

클라이언트 코드는 다음과 같이 작성한다:

```typescript
// TypeScript
const employees: Employee[] = [
    new Employee("직원A", 400, false, 0),
    new Employee("직원B", 300, false, 0),
    new Employee("직원C", 250, false, 0),
    new Employee("아르바이트D", 1, true, 120),
    new Employee("아르바이트E", 1, true, 120),
    new Employee("아르바이트F", 1.5, true, 120),
];

function calculatePay(name: string): void {
    const taxRate = getTaxRate();
    const employee = employees.find((e) => e.name === name)!;
    const pay = employee.calculatePay(taxRate);
    console.log(describeResult(name, pay));
}

function sumOfBasePays(): void {
    const result = employees.reduce((sum, e) => sum + e.monthlyBasePay(), 0);
    console.log(result);
}
```

추상 데이터 타입은 사람들이 세상을 바라보는 방식에 좀 더 근접하도록 추상화 수준을 향상시킨다. 일상생활에서 Employee라고 말할 때는 상태와 행위를 가지는 독립적인 객체라는 의미가 담겨 있다. 따라서 개별 직원의 인스턴스를 생성할 수 있는 `Employee` 추상 데이터 타입은 전체 직원을 캡슐화하는 `Employees` 모듈보다 사람들의 사고방식에 가깝다.

> **핵심 통찰**: 비록 추상 데이터 타입 정의를 기반으로 객체를 생성하는 것은 가능하지만, 여전히 데이터와 기능을 분리해서 바라본다는 점에 주의하라. 추상 데이터 타입은 데이터에 대한 관점을 설계의 표면으로 끌어올리기는 하지만, 여전히 데이터와 기능을 분리하는 절차적인 설계의 틀에 갇혀 있다.

---

## 6. 클래스

### 6.1 클래스는 추상 데이터 타입인가?

대부분의 프로그래밍 서적은 클래스를 추상 데이터 타입으로 설명한다. 클래스와 추상 데이터 타입 모두 데이터 추상화를 기반으로 시스템을 분해하기 때문에 이런 설명이 꼭 틀린 것만은 아니다. 두 메커니즘 모두 외부에서는 객체의 내부 속성에 직접 접근할 수 없으며 오직 퍼블릭 인터페이스를 통해서만 외부와 의사소통할 수 있다.

그러나 명확한 의미에서 추상 데이터 타입과 클래스는 **동일하지 않다**. 가장 핵심적인 차이는 클래스는 **상속과 다형성**을 지원하는 데 비해 추상 데이터 타입은 지원하지 못한다는 점이다. 상속과 다형성을 지원하는 **객체지향 프로그래밍**과 구분하기 위해, 상속과 다형성을 지원하지 않는 추상 데이터 타입 기반의 프로그래밍 패러다임을 **객체 기반 프로그래밍**(*Object-Based Programming*)이라고 부르기도 한다.

윌리엄 쿡(William Cook)은 논문 "Object-Oriented Programming Versus Abstract Data Types"(1990)에서 객체지향과 추상 데이터 타입 간의 차이를 다음과 같이 정의했다:

| | 추상 데이터 타입 | 클래스 (객체지향) |
|---|---|---|
| **추상화 방식** | **타입 추상화**: 오퍼레이션을 기준으로 타입을 묶는다 | **절차 추상화**: 타입을 기준으로 절차(오퍼레이션)를 묶는다 |
| **타입 표현** | 하나의 타입 안에 여러 개념적 타입이 암묵적으로 공존 | 각 개념적 타입이 독립적인 클래스로 명시적 표현 |
| **타입 구분** | 인스턴스 변수를 이용한 조건문으로 타입 구분 | 다형성으로 타입 구분 |

### 6.2 타입 추상화 vs 절차 추상화

추상 데이터 타입으로 구현된 `Employee`의 `calculatePay`와 `monthlyBasePay` 오퍼레이션을 살펴보자. `Employee` 타입은 물리적으로는 하나의 타입이지만 개념적으로는 **정규직원과 아르바이트 직원**이라는 두 개의 개별적인 개념을 포괄하는 복합 개념이다.

```
    ┌─────────────────────────────────────────────────────┐
    │                  Employee Type (ADT)                 │
    ├─────────────────┬───────────────┬───────────────────┤
    │  오퍼레이션       │  정규직원       │  아르바이트 직원    │
    ├─────────────────┼───────────────┼───────────────────┤
    │ calculatePay()  │ basePay -     │ (basePay×timeCard) │
    │                 │ basePay×tax   │ - ...×tax          │
    ├─────────────────┼───────────────┼───────────────────┤
    │ monthlyBasePay()│ basePay       │ 0                  │
    └─────────────────┴───────────────┴───────────────────┘
    → 오퍼레이션을 기준으로 타입을 통합 (타입 추상화)
```

추상 데이터 타입은 하나의 대표적인 타입이 다수의 세부적인 타입을 감추기 때문에 이를 **타입 추상화**라고 부른다. 개별 오퍼레이션이 모든 개념적인 타입에 대한 구현을 포괄하도록 함으로써, 하나의 물리적인 타입 안에 전체 타입을 감춘다.

객체지향은 이와 반대로 **타입을 기준으로 오퍼레이션을 묶는다**. 정규직원과 아르바이트 직원이라는 두 개의 타입을 명시적으로 정의하고, 두 직원 유형과 관련된 오퍼레이션의 실행 절차를 두 타입에 분배한다.

```
    ┌─────────────────────────────────────────────────────┐
    │               Employee (클래스 계층)                  │
    ├─────────────────────────────────────────────────────┤
    │  정규직원 (SalariedEmployee)                          │
    │    calculatePay(): basePay - basePay×tax             │
    │    monthlyBasePay(): basePay                         │
    ├─────────────────────────────────────────────────────┤
    │  아르바이트 직원 (HourlyEmployee)                     │
    │    calculatePay(): (basePay×timeCard) - ...×tax      │
    │    monthlyBasePay(): 0                               │
    └─────────────────────────────────────────────────────┘
    → 타입을 기준으로 오퍼레이션을 분배 (절차 추상화)
```

### 6.3 추상 데이터 타입에서 클래스로 변경하기

클래스를 이용해 급여 관리 시스템을 구현해 보자. 추상 데이터 타입에서는 `Employee`라는 하나의 타입 안에 두 가지 직원 타입을 캡슐화했다. 클래스를 이용하는 객체지향 버전에서는 각 직원 타입을 독립적인 클래스로 구현함으로써 두 개의 타입이 존재한다는 사실을 명시적으로 표현한다.

<details>
<summary>원문 Ruby 코드</summary>

```ruby
# Ruby
class Employee
  attr_reader :name, :basePay

  def initialize(name, basePay)
    @name = name
    @basePay = basePay
  end

  def calculatePay(taxRate)
    raise NotImplementedError
  end

  def monthlyBasePay()
    raise NotImplementedError
  end
end

class SalariedEmployee < Employee
  def initialize(name, basePay)
    super(name, basePay)
  end

  def calculatePay(taxRate)
    return basePay - (basePay * taxRate)
  end

  def monthlyBasePay()
    return basePay
  end
end

class HourlyEmployee < Employee
  attr_reader :timeCard

  def initialize(name, basePay, timeCard)
    super(name, basePay)
    @timeCard = timeCard
  end

  def calculatePay(taxRate)
    return (basePay * timeCard) - (basePay * timeCard) * taxRate
  end

  def monthlyBasePay()
    return 0
  end
end
```

</details>

```typescript
// TypeScript
abstract class Employee {
    constructor(
        public readonly name: string,
        protected readonly basePay: number
    ) {}

    abstract calculatePay(taxRate: number): number;
    abstract monthlyBasePay(): number;
}

class SalariedEmployee extends Employee {
    constructor(name: string, basePay: number) {
        super(name, basePay);
    }

    calculatePay(taxRate: number): number {
        return this.basePay - this.basePay * taxRate;
    }

    monthlyBasePay(): number {
        return this.basePay;
    }
}

class HourlyEmployee extends Employee {
    constructor(
        name: string,
        basePay: number,
        private readonly timeCard: number
    ) {
        super(name, basePay);
    }

    calculatePay(taxRate: number): number {
        const pay = this.basePay * this.timeCard;
        return pay - pay * taxRate;
    }

    monthlyBasePay(): number {
        return 0;
    }
}
```

모든 직원 타입에 대해 `Employee`의 인스턴스를 생성해야 했던 추상 데이터 타입과 달리, 클래스를 이용한 구현에서는 원하는 직원 타입에 해당하는 클래스의 인스턴스를 명시적으로 지정할 수 있다:

```typescript
// TypeScript
const employees: Employee[] = [
    new SalariedEmployee("직원A", 400),
    new SalariedEmployee("직원B", 300),
    new SalariedEmployee("직원C", 250),
    new HourlyEmployee("아르바이트D", 1, 120),
    new HourlyEmployee("아르바이트E", 1, 120),
    new HourlyEmployee("아르바이트F", 1.5, 120),
];
```

하지만 일단 객체를 생성하고 나면 객체의 클래스가 무엇인지는 중요하지 않다. 클라이언트의 입장에서는 `SalariedEmployee`와 `HourlyEmployee`의 인스턴스를 모두 부모 클래스인 `Employee`의 인스턴스인 것처럼 다룰 수 있다.

```typescript
// TypeScript
function sumOfBasePays(): void {
    const result = employees.reduce((sum, each) => sum + each.monthlyBasePay(), 0);
    console.log(result);
}
```

`sumOfBasePays` 함수가 `employees`에 포함된 객체가 어떤 타입인지를 고민하지 않고 `monthlyBasePay` 메시지를 전송한다는 것에 주목하라. 메시지를 수신한 객체는 자신의 클래스에 구현된 메서드를 이용해 적절하게 반응할 수 있다. 이것이 바로 **다형성**이다.

### 6.4 변경을 기준으로 선택하라

단순히 클래스를 구현 단위로 사용한다는 것이 객체지향 프로그래밍을 한다는 것을 의미하지는 않는다. **타입을 기준으로 절차를 추상화하지 않았다면 그것은 객체지향 분해가 아니다.** 비록 클래스를 사용하고 있더라도 말이다.

클래스가 추상 데이터 타입의 개념을 따르는지를 확인할 수 있는 가장 간단한 방법은 **클래스 내부에 인스턴스의 타입을 표현하는 변수가 있는지를 살펴보는 것**이다. 추상 데이터 타입으로 구현된 `Employee` 클래스를 살펴보면 `hourly`라는 인스턴스 변수에 직원의 유형을 저장한다. 이처럼 인스턴스 변수에 저장된 값을 기반으로 메서드 내에서 타입을 명시적으로 구분하는 방식은 **객체지향을 위반하는 것으로 간주된다**.

```
     [추상 데이터 타입]                    [객체지향]

   ┌──────────────┐              ┌──────────────┐
   │   Employee   │              │   Employee   │
   │              │              │ (abstract)   │
   │ if (hourly)  │              │ calculatePay │
   │   ...hourly  │              │ monthlyBase  │
   │ else         │              └──────┬───────┘
   │   ...salary  │                 ┌───┴───┐
   └──────────────┘                 ▼       ▼
                            ┌─────────┐ ┌──────────┐
   조건문으로 타입 구분       │Salaried │ │  Hourly  │
                            │Employee │ │ Employee │
                            └─────────┘ └──────────┘
                            다형성으로 타입 구분
```

객체지향에서는 타입 변수를 이용한 조건문을 **다형성으로 대체**한다. 클라이언트가 객체의 타입을 확인한 후 적절한 메서드를 호출하는 것이 아니라, 객체가 메시지를 처리할 적절한 메서드를 선택한다.

추상 데이터 타입을 기반으로 한 `Employee`에 새로운 직원 타입을 추가하려면 `hourly`의 값을 체크하는 클라이언트의 조건문을 하나씩 찾아 수정해야 한다. 이에 반해 객체지향은 새로운 직원 유형을 구현하는 클래스를 `Employee` 상속 계층에 추가하고 필요한 메서드를 오버라이딩하면 된다. 새로 추가된 클래스의 메서드를 실행하기 위한 어떤 코드도 추가할 필요가 없다.

이처럼 기존 코드에 아무런 영향도 미치지 않고 새로운 객체 유형과 행위를 추가할 수 있는 객체지향의 특성을 **개방-폐쇄 원칙**(*Open-Closed Principle, OCP*)이라고 부른다. 이것이 객체지향 설계가 전통적인 방식에 비해 변경하고 확장하기 쉬운 구조를 설계할 수 있는 이유다.

### 6.5 ADT vs 클래스: 언제 무엇을 선택할 것인가

설계의 유용성은 변경의 방향성과 발생 빈도에 따라 결정된다. 추상 데이터 타입과 객체지향 설계의 유용성은 설계에 요구되는 변경의 압력이 **타입 추가**에 관한 것인지, **오퍼레이션 추가**에 관한 것인지에 따라 달라진다.

| 변경의 압력 | 유리한 방식 | 이유 |
|---|---|---|
| **새로운 타입을 빈번하게 추가** | 객체지향 (클래스) | 새로운 클래스를 상속 계층에 추가하기만 하면 된다. 클라이언트 코드 수정 불필요 |
| **새로운 오퍼레이션을 빈번하게 추가** | 추상 데이터 타입 | 전체 타입에 대한 구현이 하나의 구현체 내에 포함돼 있어 오퍼레이션 추가가 간단하다 |

> **핵심 통찰**: 변경의 축을 찾아라. 객체지향적인 접근법이 모든 경우에 올바른 해결 방법인 것은 아니다. 새로운 타입을 빈번하게 추가해야 한다면 객체지향의 클래스 구조가 더 유용하다. 새로운 오퍼레이션을 빈번하게 추가해야 한다면 추상 데이터 타입을 선택하는 것이 현명한 판단이다.

### 6.6 협력이 중요하다

마지막으로 한 가지만 더 이야기하겠다. 단순하게 오퍼레이션과 타입을 표에 적어놓고 클래스 계층에 오퍼레이션의 구현 방법을 분배한다고 해서 객체지향적인 애플리케이션을 설계하는 것은 아니다. 객체지향에서 중요한 것은 **역할, 책임, 협력**이다.

객체지향은 기능을 수행하기 위해 **객체들이 협력하는 방식**에 집중한다. 협력이라는 문맥을 고려하지 않고 객체를 고립시킨 채 오퍼레이션의 구현 방식을 타입별로 분배하는 것은 올바른 접근법이 아니다.

> 객체가 참여할 협력을 결정하고 협력에 필요한 책임을 수행하기 위해 어떤 객체가 필요한지에 관해 고민하라. 그 책임을 다양한 방식으로 수행해야 할 때만 타입 계층 안에 각 절차를 추상화하라. 타입 계층과 다형성은 협력이라는 문맥 안에서 책임을 수행하는 방법에 관해 고민한 결과물이어야 하며 그 자체가 목적이 되어서는 안 된다.

---

## 설계 원칙

| 원칙 | 설명 | 예제에서의 적용 |
|---|---|---|
| **추상화** | 불필요한 세부사항을 제거하고 핵심만 남겨 인지 과부하를 방지한다 | 급여 관리 시스템을 프로시저/모듈/ADT/클래스 단위로 추상화 |
| **분해** | 큰 문제를 단기 기억으로 처리 가능한 작은 문제로 나눈다 | 최상위 기능을 하위 기능으로 단계적 분해 |
| **정보 은닉** | 자주 변경되는 비밀을 안정적인 인터페이스 뒤로 감춘다 | Employees 모듈이 직원 데이터를 내부로 감춤 |
| **데이터 추상화** | 데이터와 오퍼레이션을 하나의 단위로 묶어 추상화 수준을 높인다 | Employee ADT가 개별 직원을 독립적 인스턴스로 표현 |
| **다형성** | 타입 변수를 이용한 조건문 대신 객체가 스스로 적절한 메서드를 선택한다 | SalariedEmployee/HourlyEmployee가 각자의 calculatePay 구현 |
| **개방-폐쇄 원칙** | 기존 코드를 수정하지 않고 새로운 타입과 행위를 추가할 수 있다 | 새 직원 유형은 Employee 상속 계층에 클래스 추가만으로 가능 |
| **관심사의 분리** | 비즈니스 로직과 사용자 인터페이스를 분리한다 | 모듈은 비즈니스 로직만 담당, UI 로직은 외부에 배치 |

---

## 요약

- **인지 과부하와 분해**: 사람의 단기 기억은 7±2개의 정보만 처리할 수 있다. 복잡한 시스템을 다루려면 추상화와 분해를 통해 한 번에 처리해야 할 정보의 양을 줄여야 한다.
- **프로시저 추상화 vs 데이터 추상화**: 프로그래밍 패러다임은 추상화의 종류(프로시저/데이터)와 이를 이용한 분해 방법으로 결정된다.
- **기능 분해(하향식 접근법)의 한계**: 하나의 메인 함수라는 비현실적 가정, 메인 함수의 빈번한 재설계, 비즈니스 로직과 UI의 결합, 성급한 실행 순서 결정, 데이터 변경의 파급 효과 등 다양한 문제를 야기한다.
- **모듈**: 정보 은닉을 기반으로 변경의 방향에 맞춰 시스템을 분해한다. 데이터 변경의 파급 효과를 제어하고 관심사를 분리하지만, 인스턴스의 개념을 제공하지 못한다는 한계가 있다.
- **추상 데이터 타입**: 타입 정의, 오퍼레이션 집합, 데이터 보호, 인스턴스 생성을 지원한다. 개별 객체를 독립적 단위로 다룰 수 있지만, 여전히 데이터와 기능을 분리하는 절차적 설계의 틀에 갇혀 있다.
- **클래스(객체지향)**: 상속과 다형성을 통해 타입 변수를 이용한 조건문을 제거하고, 새로운 타입 추가 시 기존 코드를 수정할 필요가 없는 개방-폐쇄 원칙을 달성한다.
- **ADT는 타입 추상화, 클래스는 절차 추상화**: 추상 데이터 타입은 오퍼레이션을 기준으로 타입을 묶고, 클래스는 타입을 기준으로 오퍼레이션을 묶는다.
- **변경의 축에 따른 선택**: 새로운 타입 추가가 빈번하면 객체지향(클래스)이, 새로운 오퍼레이션 추가가 빈번하면 추상 데이터 타입이 유리하다.
- **협력이 핵심이다**: 타입 계층과 다형성은 협력이라는 문맥 안에서 책임을 수행하는 방법에 관해 고민한 결과물이어야 하며, 그 자체가 목적이 되어서는 안 된다.

---

## 다른 챕터와의 관계

- **Chapter 1 (객체, 설계)**: 이 장에서 절차적 프로그래밍의 문제를 객체의 자율성과 캡슐화를 통해 해결했다면, 7장은 그 역사적 배경을 기능 분해 → 모듈 → ADT → 클래스라는 진화 과정을 통해 설명한다.
- **Chapter 4 (설계 품질과 트레이드오프)**: 4장에서 강조한 캡슐화, 응집도, 결합도의 원칙이 7장의 각 분해 방식에서 어떻게 달성되거나 위반되는지를 구체적인 코드로 확인할 수 있다.
- **Chapter 5 (책임 할당)**: 7장에서 "협력이 중요하다"고 강조한 것처럼, 5장의 책임 주도 설계가 타입 계층과 다형성을 설계하는 올바른 방법이다.
- **Chapter 6 (메시지와 인터페이스)**: 7장에서 보여준 ADT의 오퍼레이션 기준 통합 vs 클래스의 다형적 메시지 전송이 6장에서 설명한 메시지 중심 설계의 이론적 근거가 된다.
- **Chapter 8 (의존성 관리)**: 7장에서 기능 분해의 "데이터 변경으로 인한 파급 효과"와 "강한 결합도" 문제를 다뤘다면, 8장에서는 의존성을 관리하는 구체적인 기법을 학습한다.
