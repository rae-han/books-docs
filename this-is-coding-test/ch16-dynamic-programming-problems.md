# Chapter 16: 다이나믹 프로그래밍 기출문제

> Ch 08에서 배운 DP 유형의 기출문제 모음(Q31~Q36). 모든 문제는 **점화식**에서 출발한다. 2차원 격자 DP, LIS, 편집 거리 같은 정형 패턴을 익힌다.

## 핵심 질문

- 격자/경로 문제의 점화식을 "이전 칸들의 max/min + 현재 값"으로 세울 수 있는가?
- 가장 긴 증가/감소 부분 수열(LIS/LDS)을 DP로 어떻게 구하는가?
- 두 문자열의 편집 거리는 왜 2차원 DP인가?

---

## Q31 금광

| 항목 | 값 |
|------|-----|
| 난이도 | ★★ 중하 |
| 기출 | Flipkart 인터뷰 |

### 문제 요약

n×m 금광에서 첫 열의 임의 행에서 출발해 매번 **오른쪽 위·오른쪽·오른쪽 아래**로 이동하며 얻는 금의 최댓값.

예: `[[1,3,3,2],[2,1,4,1],[0,6,4,7]]` → `19`

### 점화식

> `dp[i][j] = gold[i][j] + max(dp[i-1][j-1], dp[i][j-1], dp[i+1][j-1])` (경계 제외)

```ts
function goldMine(n: number, m: number, gold: number[][]): number {
  const dp = gold.map((row) => [...row]);
  for (let j = 1; j < m; j++) {
    for (let i = 0; i < n; i++) {
      const leftUp = i > 0 ? dp[i - 1][j - 1] : 0;
      const left = dp[i][j - 1];
      const leftDown = i < n - 1 ? dp[i + 1][j - 1] : 0;
      dp[i][j] = gold[i][j] + Math.max(leftUp, left, leftDown);
    }
  }
  let result = 0;
  for (let i = 0; i < n; i++) {
    result = Math.max(result, dp[i][m - 1]); // 마지막 열의 최댓값
  }
  return result;
}
```

## Q32 정수 삼각형

| 항목 | 값 |
|------|-----|
| 난이도 | ★★ 중하 |
| 기출 | 백준 1932 |

### 문제 요약

삼각형을 위→아래로 내려오며(대각선 좌/우) 선택한 수의 합 최대.

예: `[[7],[3,8],[8,1,0],[2,7,4,4],[4,5,2,6,5]]` → `30`

### 점화식

> `dp[i][j] = tri[i][j] + max(dp[i-1][j-1], dp[i-1][j])` (경계 처리)

```ts
function triangle(tri: number[][]): number {
  const n = tri.length;
  const dp = tri.map((row) => [...row]);
  for (let i = 1; i < n; i++) {
    for (let j = 0; j <= i; j++) {
      let best = -Infinity;
      if (j > 0) {
        best = Math.max(best, dp[i - 1][j - 1]); // 대각선 왼쪽 위
      }
      if (j < i) {
        best = Math.max(best, dp[i - 1][j]); // 대각선 오른쪽 위
      }
      dp[i][j] = tri[i][j] + best;
    }
  }
  return Math.max(...dp[n - 1]);
}
```

## Q33 퇴사

| 항목 | 값 |
|------|-----|
| 난이도 | ★★★ 중 |
| 기출 | 백준 14501 |

### 문제 요약

N일 동안 각 날의 상담(소요 `T[i]`일, 보수 `P[i]`)을 적절히 골라 **최대 수익**. 상담은 기간 내 끝나야 한다.

예: N=7, `T=[3,5,1,1,2,4,2]`, `P=[10,20,10,20,15,40,200]` → `45`

### 점화식 (뒤에서부터)

> `dp[i] = max(P[i] + dp[i+T[i]], dp[i+1])` (i+T[i] ≤ N일 때만 상담 가능)

```ts
function quitJob(n: number, t: number[], p: number[]): number {
  const dp = new Array(n + 1).fill(0);
  for (let i = n - 1; i >= 0; i--) {
    const end = i + t[i]; // 상담 끝나고 다음 가능한 날
    if (end <= n) {
      dp[i] = Math.max(p[i] + dp[end], dp[i + 1]);
    } else {
      dp[i] = dp[i + 1]; // 기간 초과 → 이 상담 불가
    }
  }
  return dp[0];
}
```

> **핵심 통찰**: "현재 상담을 하면 끝나는 날로 점프, 안 하면 다음 날"이라는 선택을 **뒤에서부터** 누적한다. 미래 값(dp[i+T[i]])이 먼저 계산돼 있어야 하므로 역방향이 자연스럽다.

## Q34 병사 배치하기

| 항목 | 값 |
|------|-----|
| 난이도 | ★★★ 중 |
| 기출 | 백준 18353 |

### 문제 요약

병사들을 **전투력 내림차순**으로 만들기 위해 열외시킬 **최소 인원**. 순서는 유지.

예: `[15,11,4,8,5,2,4]` → `2`

### 핵심 아이디어

"가장 긴 감소 부분 수열(LDS)"을 남기면 열외가 최소다. 답 = `N − LDS 길이`. LDS는 LIS의 DP를 부등호만 바꿔 구한다(O(N²), N ≤ 2000).

```ts
function soldier(power: number[]): number {
  const n = power.length;
  const dp = new Array(n).fill(1); // dp[i] = i로 끝나는 가장 긴 감소 수열 길이
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < i; j++) {
      if (power[j] > power[i]) {
        dp[i] = Math.max(dp[i], dp[j] + 1);
      }
    }
  }
  return n - Math.max(...dp);
}
console.log(soldier([15, 11, 4, 8, 5, 2, 4])); // 2  (15,11,8,5,4 유지)
```

## Q35 못생긴 수

| 항목 | 값 |
|------|-----|
| 난이도 | ★★ 중하 |
| 기출 | Google 인터뷰 |

### 문제 요약

2, 3, 5만 소인수로 갖는 수(1 포함)를 순서대로 셀 때 **n번째 수**.

예: n=10 → `12`, n=4 → `4`

### 핵심 아이디어

이미 구한 못생긴 수에 2·3·5를 곱해 다음 수를 만든다. **세 개의 포인터**로 각 배수의 다음 후보를 추적하며 최솟값을 채택한다.

```ts
function uglyNumber(n: number): number {
  const dp = new Array(n);
  dp[0] = 1;
  let i2 = 0;
  let i3 = 0;
  let i5 = 0;
  let next2 = 2;
  let next3 = 3;
  let next5 = 5;
  for (let i = 1; i < n; i++) {
    dp[i] = Math.min(next2, next3, next5);
    if (dp[i] === next2) {
      next2 = dp[++i2] * 2;
    }
    if (dp[i] === next3) {
      next3 = dp[++i3] * 3;
    }
    if (dp[i] === next5) {
      next5 = dp[++i5] * 5;
    }
  }
  return dp[n - 1];
}
console.log(uglyNumber(10)); // 12
```

> **함정**: `dp[i] === next2`, `next3`, `next5`를 **각각 독립 `if`로** 검사한다(`else if` 아님). 같은 값이 여러 배수에서 동시에 나올 수 있어(예: 6 = 2×3) 모든 해당 포인터를 전진시켜야 중복이 안 생긴다.

## Q36 편집 거리

| 항목 | 값 |
|------|-----|
| 난이도 | ★★★ 중 |
| 기출 | Goldman Sachs 인터뷰 |

### 문제 요약

문자열 A를 삽입·삭제·교체로 B로 만드는 **최소 연산 수**(Levenshtein 거리).

예: `cat` → `cut` = `1`, `sunday` → `saturday` = `3`

### 점화식

> 같으면 `dp[i][j] = dp[i-1][j-1]`, 다르면 `dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])` (삭제·삽입·교체)

```ts
function editDistance(a: string, b: string): number {
  const m = a.length;
  const n = b.length;
  const dp = Array.from({ length: m + 1 }, () => new Array(n + 1).fill(0));
  // 빈 문자열로/에서 만드는 비용 = 길이
  for (let i = 0; i <= m; i++) {
    dp[i][0] = i;
  }
  for (let j = 0; j <= n; j++) {
    dp[0][j] = j;
  }
  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      if (a[i - 1] === b[j - 1]) {
        dp[i][j] = dp[i - 1][j - 1]; // 같으면 그대로
      } else {
        dp[i][j] = 1 + Math.min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]);
      }
    }
  }
  return dp[m][n];
}
console.log(editDistance("sunday", "saturday")); // 3
```

> **핵심 통찰**: 2차원 DP에서 `dp[i][j]`는 "A의 앞 i글자를 B의 앞 j글자로" 만드는 비용이다. 세 연산이 각각 `dp[i-1][j]`(삭제), `dp[i][j-1]`(삽입), `dp[i-1][j-1]`(교체)에 대응한다.

---

## 요약

- **금광·정수 삼각형**: 격자 경로 DP — `현재 값 + 이전 칸들의 max`.
- **퇴사**: 뒤에서부터 `dp[i] = max(P[i] + dp[i+T[i]], dp[i+1])`.
- **병사 배치하기**: LDS(가장 긴 감소 부분 수열), 답 = `N − LDS`.
- **못생긴 수**: 2·3·5 포인터로 다음 후보 추적, 동시 갱신 주의.
- **편집 거리**: 2차원 DP, 삽입·삭제·교체 = `dp[i][j-1]`·`dp[i-1][j]`·`dp[i-1][j-1]`.
- 모든 DP는 **점화식이 절반**이다(Ch 08). 격자·문자열·수열별 정형 점화식을 외워 두면 빠르다.
