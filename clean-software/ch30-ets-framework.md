# Chapter 30: The ETS Framework (ETS 프레임워크)

## 핵심 질문

실제 대규모 프로젝트에서 재사용 가능한 프레임워크(*Framework - 애플리케이션의 공통 골격을 제공하고 제어 흐름의 주도권을 가지는 소프트웨어 구조*)는 어떻게 진화하는가? 객체지향과 디자인 패턴은 4년간의 끊임없는 요구사항 변경 속에서도 설계를 견고하게 유지할 수 있게 만드는가? 라이브러리와 프레임워크는 무엇이 다른가 — 왜 "처음 만든 프레임워크는 버려야 한다"고 하는가?

> 로버트 C. 마틴과 제임스 뉴커크 공동 집필.<br>1993년 3월부터 1997년 후반까지 개발한 규모가 큰 소프트웨어 프로젝트에 대해 설명한다. 이 소프트웨어는 교육시험서비스(ETS: Educational Testing Service)로부터 의뢰받아 오브젝트 멘토 사(OMI: Object Mentor, Inc)에서 공동 개발했다.

---

## 1. 프로젝트 배경 — 건축사 면허 시험 자동화

미국과 캐나다에서 건축사 면허를 따려면 **NCARB(*National Council of Architectural Registration Boards - 미국 연방 건축사 등록 위원회*)** 가 주관하고 ETS가 개발한 시험을 통과해야 한다. 시험은 9개 과목으로 구성되며, 그중 **그래픽 과목 3개**는 응시자가 CAD와 유사한 환경에서 직접 도면을 그리는 방식이다.

예를 들어 응시자에게는 다음과 같은 문제가 주어진다.

- 특정 종류의 빌딩 평면도를 설계하시오.
- 이미 존재하는 빌딩에 들어맞는 지붕을 설계하시오.
- 제안된 빌딩을 토지구획에 배치하고 주차장, 도로, 보도 체계를 설계하시오.

과거에는 응시자가 종이에 그린 답안을 베테랑 건축사들이 일일이 채점했다. 1989년 NCARB는 ETS에게 이 과정을 자동화하는 시스템 개발 가능성을 조사하도록 의뢰했고, 1992년 ETS는 **요구사항 변동성이 매우 큰 도메인이므로 객체지향 접근이 적절하다**고 판단했다. 그 결과 OMI가 1993년 봄 첫 계약을 체결했다.

### 1.1 프로그램 구조

- **비네트(*Vignette - 특정 지식 분야 하나를 시험하는 한 묶음의 문제*) 15개**로 그래픽 시험이 구성됨
- 각 비네트는 다시 **수행평가(performance) 프로그램**과 **채점(scoring) 프로그램**으로 나뉨
- 비네트마다 여러 개의 **스크립트(script)** — 같은 비네트라도 도서관/식품점/경찰서 등 구체적 문제가 다름
- 플랫폼: Windows 3.1 → Windows 95/NT, C++ 사용

### 1.2 1994년 팀과 마감

- 로버트 C. 마틴 (아키텍트 겸 수석 설계자, 경력 20년 이상)
- 제임스 W. 뉴커크 (설계자 겸 프로젝트 리더, 경력 15년 이상)
- 바마 라오, 윌리엄 미첼 (설계자 겸 프로그래머)

**1997년 2월 실전 투입**이 절대적인 마감이었다. 응시자는 2월에 시험을 치르고 5월에 채점이 이루어진다.

---

## 2. 프레임워크의 첫 실패 — 1993~1994

초기 1년간 마틴과 뉴커크는 '빌딩 설계' 비네트를 만들면서 동시에 **다른 14개 비네트에서도 재사용 가능한 프레임워크**를 함께 만들고자 했다. 1993년 10월 첫 시연은 성공적이었고, 1993년 후반까지 60,000라인 분량의 C++ 프레임워크가 만들어졌다.

그러나 1993년 12월, 뉴커크가 다른 비네트를 만드는 ETS 공학자와 일주일을 보내면서 이 프레임워크의 실제 재사용 가능성을 검증해보았다. 결과는 충격적이었다.

> **Uncle Bob의 경험**: 한 주가 끝날 때쯤, 프레임워크를 재사용할 수 있는 유일한 방법은 그 소스 코드의 일부분을 새로운 비네트에 이리저리 복사해 붙여넣는 것뿐이라는 사실이 분명해졌다. 분명히 이것은 좋은 선택 방법이 아니었다.

### 2.1 실패의 두 가지 원인

지나고 나서 보니까, 첫 프레임워크가 작동하지 못한 데에는 두 가지 이유가 있었다.

1. **시야가 좁았다** — 빌딩 설계에만 초점을 맞추고 그 밖의 비네트들을 모두 고려 대상에서 배제하고 있었다.
2. **압박이 심했다** — 몇 달 동안 요구사항의 변동과 일정의 압박에 시달리면서 빌딩 설계에만 한정된 개념들이 프레임워크에 스며들었다.

> **핵심 통찰**: 객체지향 기술의 장점을 너무 당연하게 생각했다. C++를 사용하고 주의 깊게 객체지향 설계를 하면, 재사용 가능한 프레임워크를 만드는 일이 쉬우리라 생각했다. 하지만 생각이 틀렸다. **재사용 가능한 프레임워크를 만드는 일은 힘들다.**

### 2.2 레베카 워프스-브록의 조언

> 적어도 세 번 이상 그 프레임워크를 기반으로 애플리케이션을 구축해봐야(그리고 실패해봐야) 그 도메인에 맞는 올바른 아키텍처를 구축했다는 자신감이 그런대로 생길 수 있다.<br>— 레베카 워프스-브록(Rebecca Wirfs-Brock)

OMI는 이 조언을 뒤늦게 체득했다.

---

## 3. 새로운 전략 — 1994년 3월

1994년 3월 새로운 계약(프레임워크 + 비네트 10개 추가)에 서명한 후, OMI는 전략을 바꾸었다.

### 3.1 채택되지 않은 대안 — 아키텍처 주도 접근

비네트들을 만들기 전에 먼저 프레임워크를 완벽히 재설계하는 방식은 **테스트할 수 없는 프레임워크 코드만 잔뜩 만들 위험**이 있었다. OMI는 "비네트가 프레임워크에서 무엇을 필요로 할지 완벽히 예측할 능력이 우리에게 있다고 믿지 않았다." 추측에 의존하지 않고 즉시 검증하기를 원했다.

### 3.2 채택된 전략 — 비네트 4개 동시 개발 + 점진적 추출

```
┌─────────────────────────────────────────────────────────────┐
│                    4개 비네트 동시 개발                       │
│                                                              │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │비네트 A │  │비네트 B │  │비네트 C │  │비네트 D │        │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘        │
│       │            │            │            │              │
│       └────────────┴─────┬──────┴────────────┘              │
│                          │                                  │
│                          ▼                                  │
│        ┌──────────────────────────────────┐                │
│        │  유사 부분 추출 → 일반화 → 리팩터링 │                │
│        └──────────────┬───────────────────┘                │
│                       ▼                                     │
│        ┌──────────────────────────────────┐                │
│        │     프레임워크 (75,000라인)        │                │
│        │  최소 4개 비네트에서 재사용 검증됨    │                │
│        └──────────────────────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

규칙은 단순했다.

> **핵심 통찰**: 적어도 4개의 비네트에 성공적으로 재사용되지 않는 것은 하나도 프레임워크에 들어올 수 없다.

### 3.3 프레임워크에 추가된 공통 기능

- UI 화면의 구조 (메시지창, 그림창, 버튼 팔레트 등)
- 그래픽 요소를 만들고, 움직이고, 조정하고, 식별하고, 지우는 기능
- 확대와 스크롤
- 직선, 원, 다각형 같은 단순한 그림 요소를 그리는 기능
- 비네트의 시간 제한과 자동 종료
- 응시자 답안 파일 저장/읽기 (에러 복구 포함)
- 기하 요소의 수학적 모델: 직선, 점, 상자, 원, 호, 삼각형, 다각형 등 — Intersection, Area, IsPointIn, IsPointOn 메소드 포함
- 채점에 사용되는 특징(feature)의 평가와 비중 부여

이 8개월 동안 프레임워크는 C++ 60,000라인 분량으로 발전했고, 최종적으로 75,000라인에 가깝게 성장했다.

---

## 4. 결과 — 6:1 생산성 향상

### 4.1 첫 비네트 4개의 비용

| 항목 | 비용 |
|---|---|
| 첫 4개 비네트 수행 프로그램 개발 | 4 man-year 이상 |
| 비네트당 평균 | 약 1 man-year |

길고 비싼 초기 투자였다.

### 4.2 이후의 폭발적 효율

| 항목 | 비용 |
|---|---|
| 이후 7개 수행 프로그램 (빌딩 설계 재작성 포함) | 18 man-month |
| 비네트당 평균 | 2.6 man-month |
| **첫 5개 대비 이후 비네트들의 생산성 향상** | **약 400% (4배)** |
| 빌딩 설계 처음 작성 → 프레임워크로 재작성 | 1 man-year → 2.5 man-month (**6:1 향상**) |

### 4.3 코드 라인 수 분포

비네트마다 필요한 코드의 **5/6 이상이 프레임워크에 있었다.** 한 애플리케이션에만 고유한 코드는 전체의 1/10에 불과했다.

| 코드 종류 | 라인 수 |
|---|---|
| 프레임워크 (모든 비네트 공통) | 75,000라인 |
| 비네트당 전형적 코드 | 약 4,000라인 |
| 가장 작은 비네트 고유 코드 | 약 500라인 |
| 가장 큰 비네트 고유 코드 | 약 12,000라인 |

### 4.4 빌딩 설계는 결국 버려졌다

> **Uncle Bob의 경험**: 빌딩 설계를 만드는 데 1년 이상의 시간과 인력이 들어갔지만, 우리는 냉혹하게 마음을 먹고 옛날 판을 완전히 버리기로 결정했다. 우리는 빌딩 설계를 프로젝트 주기의 후반부에서 다시 설계하고 구현하기로 했다.

프레임워크가 진화하면서 옛 빌딩 설계는 점점 "아웃사이더"가 되어갔다. 결과적으로 다시 짠 빌딩 설계는 단 2.5 man-month만에 완성되었다.

### 4.5 매주 전달 — 변경에도 무너지지 않은 설계

프로젝트 시작부터 전체 기간 동안 OMI는 매주 ETS에게 중간 판을 전달했다. ETS는 이를 테스트하고 변경 요청 목록을 보냈다. OMI는 변경사항을 추정한 다음 ETS와 함께 한 주의 일정을 잡았다.

> 격렬한 개발 와중의 이런 모든 수정, 사소한 변경, 작은 조정에도 불구하고, "소프트웨어의 설계는 흐트러지지 않았다."<br>— 피트 브리팅햄(Pete Britingham), ETS의 NCARB 프로젝트 관리자

---

## 5. 채점 프레임워크의 설계

### 5.1 도메인 모델 — 초급 수학 시험으로 본 채점 체계

채점 체계를 설명하기 위해 본문은 가상의 "초급 수학 시험" 예제를 사용한다. 시험은 단순히 통과/실패가 아니라, **학생의 강점과 약점을 분석**해야 한다.

```
                       Basic Math
                          │
              ┌───────────┴────────────┐
              ▼                        ▼
            Terms                    Factors
              │                        │
       ┌──────┴──────┐          ┌─────┴──────┐
       ▼             ▼          ▼            ▼
   Addition      Subtraction  Multipl.    Division
       │                        │
   ┌───┴───┐              ┌────┴────┐
   ▼       ▼              ▼         ▼
 Carry  Properties    Partial    Properties
                       Products
```

각 말단 노드는 **특징(*Feature - 평가 가능하고 점수를 매길 수 있는 지식의 단위*)** 이다. 점수는 `A(승인, acceptable)`, `U(불승인, unacceptable)`, `I(미정, indeterminate)` 중 하나다.

### 5.2 매트릭스 — 점수 합성 규칙

계층 구조의 각 단계마다 **행렬(matrix)** 이 있어, 하위 특징의 점수에 비중을 곱한 뒤 표를 통해 상위 점수로 합쳐 올린다.

예: Addition 행렬은 Carry의 비중을 2, Properties의 비중을 1로 두고, 비중이 적용된 누적 U와 누적 I를 좌표로 사용해 결과(A/U/I)를 결정한다.

> **핵심 통찰**: 채점 트리 구조와 비중을 텍스트 파일로 외부화함으로써, **ETS의 교육측정평가 전문가들이 실제 코드를 변경하지 않고도 트리의 모양과 비중을 바꿀 수 있게** 했다. 이것이 OCP(개방-폐쇄 원칙)의 실제 구현이다.

### 5.3 정적 구조 — Evaluator 추상 클래스

```
              ┌──────────────────────────────┐
              │       <<abstract>>           │
              │        Evaluator             │
              ├──────────────────────────────┤
              │ + Evaluate(ostream&): Score  │ ◀── Template Method
              │ - DoEval(): Score = 0        │ ◀── Hook (순수 가상)
              └──────────┬───────────────────┘
                         │
              ┌──────────┴───────────────┐
              ▼                          ▼
   ┌──────────────────┐      ┌──────────────────────┐
   │ VignetteFeature  │      │   FeatureGroup       │ ◀── 매트릭스 노드
   │ (말단 노드)        │      ├──────────────────────┤
   │ - DoEval()       │      │ + AddEvaluator(e,r)  │
   └──────────────────┘      │ + AddMatrixElement() │
                              │ - DoEval()           │
                              │ - itsMatrix: Matrix  │
                              │ - itsEvaluators[]    │
                              └──────────────────────┘
```

`Evaluator`는 채점 트리의 **말단(feature) 노드와 매트릭스 노드 모두를 나타내는 추상 클래스**다 — 합성 패턴(Composite Pattern)이다.

<details>
<summary>원문 C++ 코드</summary>

```cpp
// C++ (1994)
class Evaluator {
public:
    enum Score { A, I, U, F, X };
    Evaluator();
    virtual ~Evaluator();
    Score Evaluate(ostream& scoreOutput);
    void SetName(const String& theName) { itsName = theName; }
private:
    const String& GetName() { return itsName; }
    virtual Score DoEval() = 0;
    String itsName;
};

Evaluator::Score Evaluator::Evaluate(ostream& o) {
    static char scoreName[] = { 'A', 'I', 'U', 'F', 'X' };
    Score score = DoEval();
    o << itsName << ":" << scoreName[score] << endl;
    return score;
}
```

</details>

```typescript
// TypeScript
enum Score {
    A,
    I,
    U,
    F,
    X,
}

/** 채점 트리 노드의 공통 추상 클래스. */
abstract class Evaluator {
    private name: string = "";

    setName(name: string): void {
        this.name = name;
    }

    protected getName(): string {
        return this.name;
    }

    /** Template Method — 표준 출력 형식을 제공하고 DoEval을 호출한다. */
    evaluate(output: (line: string) => void): Score {
        const scoreName = ["A", "I", "U", "F", "X"];
        const score = this.doEval();
        output(`${this.name}:${scoreName[score]}`);
        return score;
    }

    /** Hook — 파생 클래스에서 실제 점수 계산을 구현한다. */
    protected abstract doEval(): Score;
}
```

`Evaluate()` 함수는 순수 가상 함수인 `DoEval()`을 호출하고 결과를 표준 형식으로 출력한다. 이것이 **템플릿 메소드 패턴**의 전형이다.

### 5.4 FeatureGroup — 매트릭스 노드

`FeatureGroup`은 자식 `Evaluator`들을 가지면서 매트릭스로 결과를 합성한다.

<details>
<summary>원문 C++ 코드</summary>

```cpp
class FeatureGroup : public Evaluator {
public:
    FeatureGroup(const RWCString& name);
    virtual ~FeatureGroup();
    void AddEvaluator(Evaluator* e, int rank);
    void AddMatrixElement(int i, int u, Score s);
private:
    Evaluator::Score DoEval();
    Matrix itsMatrix;
    vector<pair<Evaluator*, int>> itsEvaluators;
};

Evaluator::Score FeatureGroup::DoEval() {
    int sumU = 0, sumI = 0;
    for (auto ei = itsEvaluators.begin(); ei != itsEvaluators.end(); ++ei) {
        Evaluator* e = ei->first;
        int rank = ei->second;
        Score s = e->Evaluate(outputStream);
        switch (s) {
            case I: sumI += rank; break;
            case U: sumU += rank; break;
        }
    }
    return itsMatrix.GetScore(sumI, sumU);
}
```

</details>

```typescript
// TypeScript
class FeatureGroup extends Evaluator {
    private matrix: Matrix = new Matrix();
    private evaluators: Array<{ evaluator: Evaluator; rank: number }> = [];

    addEvaluator(evaluator: Evaluator, rank: number): void {
        this.evaluators.push({ evaluator, rank });
    }

    addMatrixElement(i: number, u: number, score: Score): void {
        this.matrix.setScore(i, u, score);
    }

    protected doEval(): Score {
        let sumU = 0;
        let sumI = 0;
        for (const { evaluator, rank } of this.evaluators) {
            const s = evaluator.evaluate(this.output);
            if (s === Score.I) {
                sumI += rank;
            } else if (s === Score.U) {
                sumU += rank;
            }
        }
        return this.matrix.getScore(sumI, sumU);
    }
}
```

> **핵심 통찰**: 채점 트리 자체는 `VignetteScoringApp` 클래스가 **외부 텍스트 파일을 읽어 동적으로 구성한다.** 채점 애플리케이션은 자신의 `FeatureDictionary`(이름 → Evaluator 매핑)만 제공하면 된다. 트리 구조 자체와 평가 알고리즘은 프레임워크가 수행한다.

---

## 6. 템플릿 메소드의 사례 — "반복문을 단 한 번만 작성하기"

### 6.1 문제 — 같은 자료구조를 순회하는 수십 개의 특징

평면도 비네트는 그림 30-4와 같은 자료구조(Building → Floor → Space → Portal → ...)에서 점수를 매긴다. **각 특징이 모두 동일한 자료구조를 순회**해야 하므로 수십 개의 클래스 사이에서 코드 중복이 폭발적으로 늘었다.

### 6.2 해결 — Template Method로 반복문 한 번만 작성

```
              ┌─────────────────────────┐
              │   SolutionSpaceFeature  │ ◀── 기반 클래스
              │   (Evaluator 상속)       │
              ├─────────────────────────┤
              │ + DoEval()              │ ◀── 반복문이 여기에만 있음
              │ # NewSolutionSpace() = 0│ ◀── Hook
              │ # GetScore() = 0        │ ◀── Hook
              └────────────┬────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
  AreaFeature      AspectRatioFeature   ElevatorStacking
                                            Feature
```

이때(1993~1994)는 GoF 책이 나오기 전이었고, OMI는 자신들의 기법을 "**반복문을 단 한 번만 작성하기**"라고 불렀다.

<details>
<summary>원문 C++ 코드 (1994)</summary>

```cpp
// solspcft.h — 1994/04/11
class SolutionSpaceFeature : public Evaluator {
public:
    SolutionSpaceFeature(Query<SolutionSpace*>&);
    virtual ~SolutionSpaceFeature();
    virtual Evaluator::Score DoEval();
    virtual void NewSolutionSpace(const SolutionSpace&) = 0;
    virtual Evaluator::Score GetScore() = 0;
private:
    Query<SolutionSpace*>& itsSolutionSpaceQuery;
};

// solspcft.cpp
Evaluator::Score SolutionSpaceFeature::DoEval() {
    Set<SolutionSpace*>& theSet = GscoreFilter->GetSolutionSpaces();
    SelectiveIterator<SolutionSpace*> ai(theSet, itsSolutionSpaceQuery);
    for (; ai; ai++) {
        SolutionSpace& as = **ai;
        NewSolutionSpace(as);
    }
    return GetScore();
}
```

</details>

```typescript
// TypeScript
abstract class SolutionSpaceFeature extends Evaluator {
    constructor(private readonly query: Query<SolutionSpace>) {
        super();
    }

    protected doEval(): Score {
        const spaces = scoreFilter.getSolutionSpaces();
        for (const space of spaces.filter(this.query)) {
            this.newSolutionSpace(space);
        }
        return this.getScore();
    }

    /** Hook — 파생 클래스가 공간별 채점 로직을 구현한다. */
    protected abstract newSolutionSpace(space: SolutionSpace): void;

    /** Hook — 최종 점수를 반환한다. */
    protected abstract getScore(): Score;
}
```

### 6.3 왜 Strategy가 아니라 Template Method였는가

Strategy 패턴을 쓰면 결합도가 훨씬 낮아진다. 그렇다면 왜 Template Method를 선택했을까?

| 측면 | Template Method | Strategy |
|---|---|---|
| 결합도 | 상속으로 강하게 결합 | 위임으로 약하게 결합 |
| DIP 준수 | 상대적으로 약함 | 더 잘 지킴 |
| 자료구조 변경 시 영향 | SpaceFeature, PortalFeature → 모든 특징 재컴파일 | Driver 클래스 2개만 변경 |
| 클래스 수 | 적음 | Driver 추가로 2개 더 |
| 단순함 | **더 단순** | 추가 추상화 필요 |

> **Uncle Bob의 경험**: 그렇다면 우리는 왜 템플릿 메소드를 선택했을까? **더 단순하기 때문이다.** 그리고 자료구조가 그렇게 자주 바뀌는 것이 아니고, 모든 특징을 재컴파일하는 데 불과 몇 분밖에 안 걸리기 때문이기도 하다. (...) 결과적으로 봤을 때 이런 이점들이 Strategy를 구현하기 위해 추가로 필요한 클래스 2개의 비용보다 크지 않았다.

> **핵심 통찰**: "더 좋은" 원칙(DIP)을 지키는 설계가 항상 옳은 것은 아니다. **변경 빈도와 비용을 함께 고려**해야 한다. 자료구조가 안정적이라면 더 단순한 설계가 이긴다.

---

## 7. 수행평가 프레임워크의 설계

### 7.1 공통된 화면 구조

모든 비네트가 **명령창(Command Window)** + **작업창(Task Window)** 구조를 공유했다.

```
┌──────────────────────────────────────────────────┐
│  Command Window   │      Task Window              │
│  ┌─────────────┐  │  ┌─────────────────────────┐ │
│  │ 항목 배치    │  │  │                          │ │
│  │ 삭제         │  │  │      (스크롤/확대 가능)   │ │
│  │ 이동/조정    │  │  │   사용자가 그리는 영역      │ │
│  │ 확대         │  │  │                          │ │
│  │ 완료         │  │  │                          │ │
│  └─────────────┘  │  └─────────────────────────┘ │
└──────────────────────────────────────────────────┘
```

명령창의 버튼을 누르면 작업창의 내용이 바뀐다. 비네트마다 차이는 있지만, **유사성이 많다는 말은 재사용 기회가 굉장히 많다는 뜻**이었다.

### 7.2 이벤트 모델 — State 패턴의 활용

이벤트 처리에는 두 가지 종류가 있었다.

1. **표준 이벤트** — 모든 비네트 공통 (Erase, Measure, Sketch 등)
2. **비네트 전용 이벤트** — 특정 비네트만의 행동

프레임워크는 표준 이벤트의 기본 처리를 제공하면서도, 각 비네트가 **재정의(override)** 할 수 있게 해야 했다.

```
              ┌──────────────────────┐
              │   CommandWindow      │ ◀── 프레임워크
              │   (표준 행동 구현)     │
              └──────────┬───────────┘
                         │
              ┌──────────┴────────────┐
              │ StandardCommandWindow │ ◀── 프레임워크
              │  (표준 이벤트 → FSM)   │
              └──────────┬────────────┘
                         │
              ┌──────────┴─────────────┐
              │ VignetteCommandWindow  │ ◀── 비네트 전용
              │ (전용 행동 + 재정의)     │
              └────────────────────────┘
```

이벤트 처리는 **유한 상태 기계(FSM: Finite State Machine)** 가 담당한다. 표준 FSM은 `StandardFSM` + `VignetteFSMContext`(인터페이스만 추가)로 나뉘고, 실제 구현은 `VignetteFSM`과 `VignetteFSMState`에서 일어난다.

### 7.3 SMC — 상태 기계 컴파일러

OMI는 **SMC(*State Machine Compiler - 상태 전이 텍스트를 받아 C++ 클래스를 자동 생성하는 도구*)** 를 사용해 상태 기계 코드를 자동 생성했다.

SMC 입력 예 (Idle 상태):

```
Idle {
    Measure Measuring     MeasureTask
    Erase   Erasing       StartEraseTask
    Sketch  Idle          GetSketchChoice
}
```

이 단순한 텍스트가 Idle 상태에서 일어나는 모든 전이를 기술한다. `{}` 안의 세 줄이 각각 (이벤트, 전이할 상태, 수행할 행동)을 명시한다.

> **실무 팁**: 상태 기계가 복잡할수록 직접 작성하는 코드는 오류가 잦다. **DSL(*Domain-Specific Language - 특정 도메인 전용으로 설계된 언어*)을 만들고 코드 생성기에 맡기는 것**이 훨씬 안전하다. SMC는 현재도 cleancoders.com에서 무료로 구할 수 있다.

---

## 8. 작업 감독자 아키텍처

이벤트가 행동으로 변환된 후, 그 행동을 처리하는 작업(Task) 자체도 **내부에 또 다른 상태 기계**를 가진다.

### 8.1 MeasureTask 예제

거리를 재는 작업의 FSM:

```
       Init
        │
        ▼
   ┌──────────────┐     GetPoint/RecordStartPt    ┌────────────────┐
   │ GetFirstPoint├──────────────────────────────▶│ GetSecondPoint │
   └──────────────┘                                └────────┬───────┘
        ▲                                                   │
        │  GetPoint/RecordEndPt                            │
        └───────────────────────────────────────────────────┤
                                                            │
                                            MovePoint/DragLine
                                                  (self-loop)
```

사용자가 두 점을 찍으면 그 사이의 거리가 메시지 창에 표시된다. `MovePoint`는 마우스 움직임마다 발생하므로 매우 빈번하다.

### 8.2 Task 계층 구조

```
                    <<interface>>
                       Task
                ├ MouseDown()
                ├ MouseMove()
                ├ GotPoint()
                ├ MouseUp()
                         │
        ┌────────────────┼───────────────────┐
        ▼                                    ▼
   MeasureTask                          TwoPointBox
   ├ RecordStartPt                      ├ RecordPoint1
   ├ RecordEndPt                        ├ RecordPoint2
   ├ DragLine                           ├ CheckComplete
        │                                    │
        ▼                                    ▼
  MeasureTaskFSM                       TwoPointBoxFSM
  (SMC 자동 생성)                       (SMC 자동 생성)
        │                                    │
        ▼                                    ▼
  MeasureTaskImpl                  TwoPointBoxImpl
  (Vignette 전용 파생)              (Vignette 전용 파생)
```

프레임워크는 수십 종류의 Task를 미리 제공한다.

- `SinglePointPlacementTask` — 클릭 한 번으로 객체를 배치
- `TwoPointBoxTask` — 두 클릭으로 상자를 그림
- `PolyLineTask` — 다각형 기반 객체
- `MeasureTask` — 거리 측정

> **핵심 통찰**: 개발자는 추상 Task 클래스에서 파생해 `CheckComplete()` 같은 비네트 전용 훅(hook)만 구현하면 된다. **할리우드 원칙(Hollywood Principle, "Don't call us, we'll call you")** 그대로 — 프레임워크가 개발자 코드를 호출한다.

---

## 9. 적용된 디자인 패턴 총정리

ETS 프레임워크에서 사용된 패턴들을 정리하면 다음과 같다.

| 패턴 | 용도 | 적용 예 |
|---|---|---|
| **Template Method** | 알고리즘 골격은 고정, 세부 단계만 가변 | `Evaluator::Evaluate()`, `SolutionSpaceFeature::DoEval()` |
| **Composite** | 트리 노드를 단일 인터페이스로 다룸 | `Evaluator` ← `VignetteFeature` / `FeatureGroup` |
| **State** | 상태별 행동을 분리 | 이벤트 처리 FSM, Task 내부 FSM |
| **Strategy** (검토만) | 알고리즘 교체 가능 | 사용하지 않음 — Template Method가 더 단순했기 때문 |
| **Hollywood Principle** | 프레임워크가 사용자 코드를 호출 | Task, CommandWindow, Evaluator 등 전반 |
| **외부 설정 파일** | 트리 구조와 비중을 코드 외부에서 관리 | 채점 트리 정의 텍스트 파일 |
| **코드 생성 (DSL)** | 반복적/오류 잦은 코드를 자동 생성 | SMC로 상태 기계 생성 |

---

## 10. 결론 — 프레임워크 구축에서 얻은 교훈

> **Uncle Bob의 경험**: 1997년 2월이 되자, 건축사 응시자들이 면허 시험을 보기 위해 수행평가 프로그램을 사용하기 시작했다. 1997년 5월이 되자, 이들의 결과가 채점되기 시작했다. 시스템은 그때부터 지금까지 계속 돌아가고 있으며, 아주 잘 작동하고 있다. 현재 북미 대륙의 모든 건축사 응시자들은 이 소프트웨어를 사용해서 시험을 치른다.

### 10.1 핵심 교훈

1. **프레임워크는 한 번에 안 만들어진다** — 최소 3번 이상 실패하고, 최소 4개의 애플리케이션에 적용해보고 나서야 검증된다.
2. **사용해보지 않고 추측하지 마라** — 아키텍처는 실제로 돌아가는 클라이언트에서 검증해야 한다. "아키텍처 주도 접근"은 실측 없는 추측을 양산한다.
3. **첫 시도는 버려야 한다** — OMI도 60,000라인의 초기 프레임워크를 버렸고, 1 man-year짜리 빌딩 설계도 버렸다.
4. **DIP > Template Method가 항상 옳은 것은 아니다** — 변경 빈도와 비용을 함께 따져야 한다.
5. **외부 설정과 코드 생성을 적극 활용하라** — 채점 트리는 텍스트 파일로, FSM은 SMC로 자동 생성했다.
6. **할리우드 원칙이 프레임워크와 라이브러리를 구분한다** — 라이브러리는 사용자가 호출하지만, 프레임워크는 사용자 코드를 호출한다.

### 10.2 6:1 생산성의 원천

빌딩 설계 첫 작성에는 1 man-year, 프레임워크 위에서 재작성에는 2.5 man-month. 이 차이는 단순히 "재사용" 때문이 아니라, **검증된 추상화 + 견고한 변경 흡수 구조 + 외부 설정 가능성**이 함께 만들어낸 결과다.

> **핵심 통찰**: 4년간 끊임없이 들어온 요구사항 변경에도 "소프트웨어의 설계는 흐트러지지 않았다." 이것이 SRP, OCP, LSP, DIP, ISP를 실제 프로젝트에 일관되게 적용한 결과다. 원칙은 학문이 아니라 **수만 라인의 코드가 4년간 진화하는 동안에도 무너지지 않게 받쳐주는 뼈대**다.

---

## 요약

- ETS 프레임워크는 1993~1997년 NCARB 건축사 면허 시험 자동화 프로젝트의 산물 — 현재도 북미 전역에서 사용 중
- 첫 1년간 빌딩 설계만 보고 만든 60,000라인 프레임워크는 **재사용 불가능**으로 판명되어 폐기
- 전략 변경: **4개 비네트 동시 개발 → 공통 부분을 점진적으로 추출/일반화**
- 최소 4개 비네트에서 검증되지 않은 것은 프레임워크에 들어올 수 없다는 규칙
- 결과: 75,000라인 프레임워크, 비네트당 코드의 5/6이 프레임워크에 위치, **6:1 생산성 향상**
- 채점 프레임워크: `Evaluator` 추상 클래스 + Composite + Template Method + 외부 텍스트 파일로 트리 구성
- 수행평가 프레임워크: 표준 CommandWindow + Vignette 재정의 가능, 이벤트는 State 패턴 FSM이 처리, FSM은 SMC가 자동 생성
- 작업 감독자 아키텍처: Task마다 내부에 FSM, 추상 Task에서 비네트가 훅만 구현 (Hollywood Principle)
- Strategy 대신 Template Method를 선택 — DIP보다 단순함이 더 큰 이득이었기 때문
- 매주 ETS에 중간 판 전달, 끊임없는 변경에도 설계는 무너지지 않음 — 객체지향 원칙이 실전에서 입증된 사례
