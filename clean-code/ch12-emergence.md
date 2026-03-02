# Chapter 12: Emergence (창발성)

## 핵심 질문

간단한 규칙 네 가지만 따르면 우수한 설계가 '창발'할 수 있는가? 켄트 벡의 단순한 설계 규칙은 무엇이며, 각 규칙을 어떻게 적용해야 깨끗한 코드와 깨끗한 설계를 얻을 수 있는가?

---

## 1. 창발적 설계로 깔끔한 코드를 구현하자

착실하게 따르기만 하면 우수한 설계가 나오는 간단한 규칙 네 가지가 있다면? 네 가지 규칙을 따르면 코드 구조와 설계를 파악하기 쉬워지고, SRP(*SRP — Single Responsibility Principle, 단일 책임 원칙*)나 DIP(*DIP — Dependency Inversion Principle, 의존 관계 역전 원칙*)와 같은 원칙을 적용하기도 쉬워진다.

켄트 벡이 제시한 **단순한 설계 규칙 네 가지** (중요도 순):

| 우선순위 | 규칙 | 핵심 |
|---|---|---|
| 1 | **모든 테스트를 실행한다** | 의도한 대로 돌아가는 시스템을 검증 |
| 2 | **중복을 없앤다** | 추가 작업, 추가 위험, 불필요한 복잡도 제거 |
| 3 | **프로그래머 의도를 표현한다** | 유지보수 개발자가 시스템을 이해하기 쉽게 |
| 4 | **클래스와 메서드 수를 최소로 줄인다** | 실용적 최소화 |

---

## 2. 단순한 설계 규칙 1: 모든 테스트를 실행하라

무엇보다 먼저, 설계는 **의도한 대로 돌아가는 시스템**을 내놓아야 한다. 문서로는 시스템을 완벽하게 설계했지만, 시스템이 의도한 대로 돌아가는지 검증할 간단한 방법이 없다면, 문서 작성을 위해 투자한 노력에 대한 가치는 인정받기 힘들다.

테스트를 철저히 거쳐 모든 테스트 케이스를 항상 통과하는 시스템은 **'테스트가 가능한 시스템'** 이다. 테스트가 불가능한 시스템은 검증도 불가능하고, 검증이 불가능한 시스템은 절대 출시하면 안 된다.

### 테스트가 설계 품질을 높이는 이유

테스트가 가능한 시스템을 만들려고 애쓰면 설계 품질이 **더불어 높아진다**:

| 효과 | 설명 |
|---|---|
| **작은 클래스** | 크기가 작고 목적 하나만 수행하는 클래스가 나온다 |
| **SRP 준수** | SRP를 준수하는 클래스는 테스트가 훨씬 더 쉽다 |
| **낮은 결합도** | 결합도가 높으면 테스트 케이스를 작성하기 어렵다 |
| **DIP 적용** | 테스트 케이스를 많이 작성할수록 의존성 주입, 인터페이스, 추상화를 사용하게 된다 |

> **핵심 통찰**: "테스트 케이스를 만들고 계속 돌려라"라는 간단하고 단순한 규칙을 따르면 시스템은 **낮은 결합도와 높은 응집력**이라는, 객체 지향 방법론이 지향하는 목표를 저절로 달성한다.

---

## 3. 단순한 설계 규칙 2~4: 리팩터링

테스트 케이스를 모두 작성했다면 이제 코드와 클래스를 정리해도 괜찮다. 코드 몇 줄을 추가할 때마다 잠시 멈추고 설계를 조감한다:

1. 새로 추가하는 코드가 설계 품질을 낮추는가?
2. 그렇다면 깔끔히 정리한다
3. 테스트 케이스를 돌려 기존 기능을 깨뜨리지 않았다는 사실을 확인한다

코드를 정리하면서 시스템이 깨질까 걱정할 필요가 없다. **테스트 케이스가 있으니까!**

리팩터링 단계에서 적용해도 괜찮은 기법:
- 응집도를 높이고
- 결합도를 낮추고
- 관심사를 분리하고
- 시스템 관심사를 모듈로 나누고
- 함수와 클래스 크기를 줄이고
- 더 나은 이름을 선택하는 등

---

## 4. 중복을 없애라

우수한 설계에서 중복은 **커다란 적**이다. 중복은 추가 작업, 추가 위험, 불필요한 복잡도를 뜻한다. 중복은 여러 가지 형태로 표출된다:
- **똑같은 코드**는 당연히 중복이다
- 비슷한 코드는 더 비슷하게 고쳐주면 리팩터링이 쉬워진다
- **구현 중복**도 중복의 한 형태다

### 구현 중복 제거

```java
// isEmpty에서 size를 활용해 구현 중복 제거
int size() {}
boolean isEmpty() {
    return 0 == size();
}
```

### 공통 코드 추출

```java
// 나쁜 예 — 중복 코드
public void scaleToOneDimension(float desiredDimension, float imageDimension) {
    if (Math.abs(desiredDimension - imageDimension) < errorThreshold)
        return;
    float scalingFactor = desiredDimension / imageDimension;
    scalingFactor = (float)(Math.floor(scalingFactor * 100) * 0.01f);
    RenderedOp newImage = ImageUtilities.getScaledImage(image, scalingFactor, scalingFactor);
    image.dispose();
    System.gc();
    image = newImage;
}

public synchronized void rotate(int degrees) {
    RenderedOp newImage = ImageUtilities.getRotatedImage(image, degrees);
    image.dispose();
    System.gc();
    image = newImage;
}
```

`scaleToOneDimension`과 `rotate`에서 일부 코드가 동일하다. 공통 코드를 새 메서드로 추출한다:

```java
// 좋은 예 — 중복 제거
public void scaleToOneDimension(float desiredDimension, float imageDimension) {
    if (Math.abs(desiredDimension - imageDimension) < errorThreshold)
        return;
    float scalingFactor = desiredDimension / imageDimension;
    scalingFactor = (float)(Math.floor(scalingFactor * 100) * 0.01f);
    replaceImage(ImageUtilities.getScaledImage(image, scalingFactor, scalingFactor));
}

public synchronized void rotate(int degrees) {
    replaceImage(ImageUtilities.getRotatedImage(image, degrees));
}

private void replaceImage(RenderedOp newImage) {
    image.dispose();
    System.gc();
    image = newImage;
}
```

아주 적은 양이지만 공통적인 코드를 새 메서드로 뽑고 보니 클래스가 **SRP를 위반**한다. 새로 만든 `replaceImage` 메서드를 다른 클래스로 옮기면 가시성이 높아지고, 다른 팀원이 좀 더 추상화해 다른 맥락에서 재사용할 기회를 포착할 수 있다.

> **핵심 통찰**: 이런 '소규모 재사용'은 시스템 복잡도를 극적으로 줄여준다. 소규모 재사용을 제대로 익혀야 대규모 재사용이 가능하다.

### TEMPLATE METHOD 패턴으로 고차원 중복 제거

```java
// 나쁜 예 — 고차원 중복
public class VacationPolicy {
    public void accrueUSDivisionVacation() {
        // 지금까지 근무한 시간을 바탕으로 휴가 일수를 계산하는 코드
        // ...
        // 휴가 일수가 미국 최소 법정 일수를 만족하는지 확인하는 코드
        // ...
        // 휴가 일수를 급여 대장에 적용하는 코드
        // ...
    }

    public void accrueEUDivisionVacation() {
        // 지금까지 근무한 시간을 바탕으로 휴가 일수를 계산하는 코드
        // ...
        // 휴가 일수가 유럽연합 최소 법정 일수를 만족하는지 확인하는 코드
        // ...
        // 휴가 일수를 급여 대장에 적용하는 코드
        // ...
    }
}
```

최소 법정 일수를 계산하는 코드만 제외하면 두 메서드는 거의 동일하다. TEMPLATE METHOD 패턴을 적용한다:

```java
// 좋은 예 — TEMPLATE METHOD 패턴으로 중복 제거
abstract public class VacationPolicy {
    public void accrueVacation() {
        calculateBaseVacationHours();
        alterForLegalMinimums();
        applyToPayroll();
    }

    private void calculateBaseVacationHours() { /* ... */ }
    abstract protected void alterForLegalMinimums();
    private void applyToPayroll() { /* ... */ }
}

public class USVacationPolicy extends VacationPolicy {
    @Override protected void alterForLegalMinimums() {
        // 미국 최소 법정 일수를 사용한다.
    }
}

public class EUVacationPolicy extends VacationPolicy {
    @Override protected void alterForLegalMinimums() {
        // 유럽연합 최소 법정 일수를 사용한다.
    }
}
```

하위 클래스는 중복되지 않는 정보만 제공해 `accrueVacation` 알고리즘에서 빠진 '구멍'을 메운다.

---

## 5. 표현하라

자신이 이해하는 코드를 짜기는 쉽다. 하지만 나중에 코드를 유지보수할 사람이 코드를 짜는 사람만큼이나 문제를 깊이 이해할 가능성은 **희박**하다.

소프트웨어 프로젝트 비용 중 대다수는 **장기적인 유지보수**에 들어간다. 코드를 변경하면서 버그의 싹을 심지 않으려면 유지보수 개발자가 시스템을 제대로 이해해야 한다. 시스템이 복잡해질수록 이해하느라 보내는 시간은 늘어나고 코드를 오해할 가능성도 커진다.

### 표현력을 높이는 네 가지 방법

| 방법 | 설명 |
|---|---|
| **좋은 이름 선택** | 이름과 기능이 딴판인 클래스나 함수로 유지보수 담당자를 놀라게 해서는 안 된다 |
| **함수와 클래스 크기 축소** | 작은 클래스와 작은 함수는 이름 짓기도, 구현하기도, 이해하기도 쉽다 |
| **표준 명칭 사용** | COMMAND나 VISITOR와 같은 표준 패턴을 사용한다면 클래스 이름에 패턴 이름을 넣어준다 |
| **단위 테스트 케이스 꼼꼼히 작성** | 테스트 케이스는 '예제로 보여주는 문서'다 — 잘 만든 테스트를 읽으면 클래스 기능이 한눈에 들어온다 |

하지만 표현력을 높이는 **가장 중요한 방법은 노력**이다. 코드만 돌린 후 다음 문제로 직행하지 말고, 나중에 읽을 사람을 고려해 **조금이라도 읽기 쉽게 만들려는 충분한 고민**이 필요하다.

> **핵심 통찰**: 나중에 코드를 읽을 사람은 바로 자신일 가능성이 높다. 자신의 작품을 조금 더 자랑하자. 더 나은 이름을 선택하고, 큰 함수를 작은 함수 여럿으로 나누고, 자신의 작품에 조금만 더 주의를 기울이자. **주의는 대단한 재능이다.**

---

## 6. 클래스와 메서드 수를 최소로 줄여라

중복을 제거하고, 의도를 표현하고, SRP를 준수한다는 기본적인 개념도 **극단으로 치달으면 득보다 실이 많아진다**:

- 클래스와 메서드 크기를 줄이자고 조그만 클래스와 메서드를 수없이 만드는 사례
- 클래스마다 무조건 인터페이스를 생성하라고 요구하는 구현 표준
- 자료 클래스와 동작 클래스는 무조건 분리해야 한다고 주장하는 개발자

이런 **독단적인 견해는 멀리하고 실용적인 방식**을 택해야 한다.

목표는 함수와 클래스 크기를 작게 유지하면서 **동시에** 시스템 크기도 작게 유지하는 것이다. 하지만 이 규칙은 네 가지 규칙 중 **우선순위가 가장 낮다**. 테스트 케이스를 만들고 중복을 제거하고 의도를 표현하는 작업이 더 중요하다.

---

## 단순한 설계 규칙의 관계

```
규칙 1: 모든 테스트를 실행한다
    │
    ↓ (안전망 확보)
규칙 2~4: 리팩터링
    │
    ├── 규칙 2: 중복을 없앤다
    │       → 소규모 재사용 → 대규모 재사용
    │       → SRP 위반 발견 → 클래스 분리
    │       → TEMPLATE METHOD 등 패턴 적용
    │
    ├── 규칙 3: 프로그래머 의도를 표현한다
    │       → 좋은 이름, 작은 클래스/함수
    │       → 표준 명칭, 단위 테스트
    │       → 노력과 주의
    │
    └── 규칙 4: 클래스와 메서드 수를 최소로 줄인다
            → 극단을 피하고 실용적으로
            → 우선순위 가장 낮음
```

---

## 요약

- **켄트 벡의 단순한 설계 규칙 네 가지**를 따르면 우수한 설계가 창발한다
- **규칙 1 (테스트)**: 모든 테스트를 실행하라 — 이것만으로도 낮은 결합도와 높은 응집력을 달성한다
- **규칙 2 (중복 제거)**: 똑같은 코드, 비슷한 코드, 구현 중복 모두 제거하라 — 소규모 재사용이 대규모 재사용의 기반이다
- **규칙 3 (표현)**: 좋은 이름, 작은 함수/클래스, 표준 명칭, 단위 테스트로 의도를 표현하라 — **주의는 대단한 재능이다**
- **규칙 4 (최소화)**: 극단을 피하고 실용적으로 클래스와 메서드 수를 줄여라 — 단, 우선순위는 가장 낮다
- 테스트 케이스가 있으므로 **리팩터링 중 시스템이 깨질 걱정 없이** 코드를 정리할 수 있다

---

## 다른 챕터와의 관계

- **← Chapter 1 (깨끗한 코드)**: 론 제프리스의 "단순한 코드 규칙"(모든 테스트 통과, 중복 없음, 표현력, 최소화)이 이 장의 네 가지 규칙과 정확히 일치한다
- **← Chapter 9 (단위 테스트)**: "모든 테스트를 실행하라"는 첫 번째 규칙의 구체적 실천법이 Chapter 9에서 다루어진다
- **← Chapter 10 (클래스)**: 응집도를 유지하고 SRP를 준수해 클래스를 쪼개는 방법이 이 장의 중복 제거와 직결된다
- **→ Chapter 17 (냄새와 휴리스틱)**: 이 장의 네 가지 규칙이 코드 냄새와 휴리스틱 목록으로 구체화된다
- **← Chapter 2 (의미 있는 이름)**: "표현하라" 규칙의 첫 번째 도구가 좋은 이름 선택이며, 이는 Chapter 2의 규칙을 따른다
- **← Chapter 3 (함수)**: "표현하라" 규칙에서 함수와 클래스 크기를 줄이라는 권고는 Chapter 3의 함수 설계 원칙과 이어진다
