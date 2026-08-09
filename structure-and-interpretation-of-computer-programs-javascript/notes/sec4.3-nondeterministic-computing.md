# Section 4.3: Nondeterministic Computing (비결정적 컴퓨팅)

## 핵심 질문

프로그래밍 언어가 **"여러 가능성 중에서 선택"** 을 기본 연산으로 지원한다면, 탐색 문제를 어떻게 우아하게 표현할 수 있는가?

---

## 핵심 개념

| 개념 | 정의 |
|------|------|
| **amb 연산** | 여러 선택지 중 하나를 비결정적으로 선택하는 특수 형식 |
| **자동 탐색(Automatic search)** | 언어가 가능한 선택을 자동으로 탐색하여 조건을 만족하는 것을 찾음 |
| **백트래킹(Backtracking)** | 선택이 실패하면 이전 선택 지점으로 돌아가 다른 선택을 시도 |
| **연속(Continuation)** | "다음에 해야 할 일"을 함수로 포착한 것 |

---

## 1. amb 연산

### 1.1 기본 사용

```javascript
amb(1, 2, 3);  // 1, 2, 3 중 하나를 "마법처럼" 선택

// 선택지가 없으면 실패:
amb();  // 실패 — 백트래킹 발생
```

### 1.2 제약 조건 프로그래밍

```javascript
function require(p) {
    if (!p) { amb(); }  // 조건 불만족 시 실패 → 백트래킹
}

function an_integer_between(low, high) {
    require(low <= high);
    return amb(low, an_integer_between(low + 1, high));
}

// 피타고라스 삼중수 찾기:
function a_pythagorean_triple_between(low, high) {
    const i = an_integer_between(low, high);
    const j = an_integer_between(i, high);
    const k = an_integer_between(j, high);
    require(i * i + j * j === k * k);
    return list(i, j, k);
}
```

`require`가 실패하면 `amb`가 자동으로 다른 선택을 시도한다. 프로그래머는 **무엇을 찾는지**만 기술하고, **어떻게 찾는지**는 언어가 처리한다.

> **핵심 통찰**: 비결정적 프로그래밍은 **선언적 프로그래밍**의 한 형태다. Section 1.1에서 언급한 "무엇(what) vs 어떻게(how)"의 대비에서 "무엇" 쪽에 가깝다. 프로그래머는 해의 성질을 기술하고, 시스템이 탐색을 수행한다. Section 4.4의 논리 프로그래밍이 이 아이디어를 더 밀고 나간다.

---

## 2. amb 평가기의 구현

### 2.1 연속 기반 구현

`evaluate`가 세 개의 인수를 받도록 수정한다:

```javascript
function evaluate(component, env, succeed, fail)
```

- `succeed`: 평가 성공 시 호출할 함수 (값과 다른-실패-연속을 받음)
- `fail`: 평가 실패 시 호출할 함수 (백트래킹)

`amb(a, b, c)`의 평가:
1. `a`를 시도
2. 이후 실패하면 `b`를 시도
3. 그것도 실패하면 `c`를 시도
4. 모두 실패하면 자신의 `fail`을 호출 (상위로 백트래킹)

### 2.2 유명한 예제: 논리 퍼즐

```javascript
// Baker, Cooper, Fletcher, Miller, Smith가 5층 아파트에 살 때:
// - Baker는 5층에 살지 않는다
// - Cooper는 1층에 살지 않는다
// - Fletcher는 1층이나 5층에 살지 않는다
// - Miller는 Cooper보다 위층에 산다
// - Smith와 Fletcher는 인접 층에 살지 않는다
// - Fletcher와 Cooper는 인접 층에 살지 않는다

function multiple_dwelling() {
    const baker = amb(1, 2, 3, 4, 5);
    const cooper = amb(1, 2, 3, 4, 5);
    const fletcher = amb(1, 2, 3, 4, 5);
    const miller = amb(1, 2, 3, 4, 5);
    const smith = amb(1, 2, 3, 4, 5);
    require(distinct(list(baker, cooper, fletcher, miller, smith)));
    require(baker !== 5);
    require(cooper !== 1);
    require(fletcher !== 1);
    require(fletcher !== 5);
    require(miller > cooper);
    require(math_abs(smith - fletcher) !== 1);
    require(math_abs(fletcher - cooper) !== 1);
    return list(list("baker", baker), list("cooper", cooper),
                list("fletcher", fletcher), list("miller", miller),
                list("smith", smith));
}
```

---

## 요약

- **amb**는 여러 선택지 중 하나를 비결정적으로 선택하며, 실패 시 **백트래킹**으로 다른 선택을 시도한다.
- 비결정적 프로그래밍은 탐색 문제를 **선언적**으로 기술할 수 있게 한다.
- amb 평가기는 **연속 전달 스타일(CPS)** 로 구현되며, 성공 연속과 실패 연속을 관리한다.
- 논리 퍼즐, 파싱, 조합 탐색 등에 자연스럽게 적용된다.

---

## 다른 섹션과의 관계

- **Section 4.1 (Metacircular Evaluator)**: amb 평가기는 메타순환 평가기의 확장이다. `evaluate`의 인터페이스만 변경.
- **Section 4.4 (Logic Programming)**: 비결정적 탐색을 논리적 추론으로 더 발전시킨다.
- **Section 1.1 (The Elements of Programming)**: 선언적 지식 vs 명령적 지식의 대비가 여기서 실현된다.
