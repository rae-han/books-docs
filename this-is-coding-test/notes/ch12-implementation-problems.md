# Chapter 12: 구현 기출문제

> Ch 04에서 배운 구현(완전 탐색·시뮬레이션) 유형의 기출문제 모음(Q07~Q14). 문제를 **오류 없이 코드로 옮기는 꼼꼼함**과, 회전·조합·순열 같은 보조 도구가 관건이다.

## 핵심 질문

- 좌표·회전·문자열 처리를 정확히 코드로 옮길 수 있는가? (시뮬레이션)
- 조합·순열로 모든 경우를 빠짐없이 시도해야 하는가? (완전 탐색)
- 2차원 배열 회전·슬라이딩 같은 정형 기법을 손에 익혔는가?

---

## Q07 럭키 스트레이트

| 항목 | 값 |
|------|-----|
| 난이도 | ★ 하 |
| 기출 | 핵심 유형 |

### 문제 요약

점수 N(자릿수는 짝수)을 반으로 나눠, **왼쪽 자릿수 합 == 오른쪽 자릿수 합**이면 `LUCKY`, 아니면 `READY`.

예: `123402` → `LUCKY`, `7755` → `READY`

```ts
function luckyStraight(n: string): string {
  const half = n.length / 2;
  let left = 0;
  let right = 0;
  for (let i = 0; i < half; i++) {
    left += Number(n[i]);
  }
  for (let i = half; i < n.length; i++) {
    right += Number(n[i]);
  }
  return left === right ? "LUCKY" : "READY";
}
console.log(luckyStraight("123402")); // LUCKY
```

## Q08 문자열 재정렬

| 항목 | 값 |
|------|-----|
| 난이도 | ★ 하 |
| 기출 | Facebook 인터뷰 |

### 문제 요약

알파벳 대문자와 숫자로 된 문자열에서, **알파벳은 오름차순 정렬**해 출력하고 그 뒤에 **숫자들의 합**을 붙인다.

예: `K1KA5CB7` → `ABCKK13`

```ts
function reorder(s: string): string {
  const letters: string[] = [];
  let sum = 0;
  for (const ch of s) {
    if (ch >= "0" && ch <= "9") {
      sum += Number(ch);
    } else {
      letters.push(ch);
    }
  }
  letters.sort();
  return letters.join("") + (sum > 0 ? String(sum) : "");
}
console.log(reorder("K1KA5CB7")); // ABCKK13
```

## Q09 문자열 압축

| 항목 | 값 |
|------|-----|
| 난이도 | ★★ 중하 |
| 기출 | 2020 카카오 신입공채 |

### 문제 요약

문자열을 **1개 이상 단위로 잘라** 연속 반복을 `횟수+문자열`로 압축한다(1회는 횟수 생략). 가능한 가장 짧은 길이를 구하라.

예: `aabbaccc` → `7`, `ababcdcdababcdcd` → `9`, `abcabcabcabcdededededede` → `14`

### 핵심 아이디어

단위 길이를 1 ~ `len/2`까지 모두 시도하며 압축 길이를 계산해 최솟값을 취한다(완전 탐색).

```ts
function compress(s: string): number {
  let answer = s.length;
  for (let unit = 1; unit <= Math.floor(s.length / 2); unit++) {
    let compressed = "";
    let prev = s.slice(0, unit);
    let count = 1;
    for (let i = unit; i < s.length; i += unit) {
      const piece = s.slice(i, i + unit);
      if (piece === prev) {
        count++;
      } else {
        compressed += (count > 1 ? String(count) : "") + prev;
        prev = piece;
        count = 1;
      }
    }
    compressed += (count > 1 ? String(count) : "") + prev; // 마지막 조각
    answer = Math.min(answer, compressed.length);
  }
  return answer;
}
console.log(compress("ababcdcdababcdcd")); // 9
```

## Q10 자물쇠와 열쇠

| 항목 | 값 |
|------|-----|
| 난이도 | ★★★ 상 |
| 기출 | 2020 카카오 신입공채 |

### 문제 요약

M×M 열쇠(`key`)를 **회전·이동**해 N×N 자물쇠(`lock`)의 모든 홈(0)을 돌기(1)로 채우되 겹치지 않으면 `true`. 1=돌기, 0=홈.

### 핵심 아이디어

자물쇠를 **3N×3N 보드 중앙**에 놓고, 열쇠를 4방향 회전하며 모든 위치에 슬라이딩해 더한다. 더한 뒤 **중앙 N×N 영역이 모두 1**이면 성공(0=안 채움, 2=겹침이므로 1만 정답).

```ts
function rotate90(matrix: number[][]): number[][] {
  const n = matrix.length;
  const m = matrix[0].length;
  const result = Array.from({ length: m }, () => new Array(n).fill(0));
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < m; j++) {
      result[j][n - 1 - i] = matrix[i][j]; // 시계 90도
    }
  }
  return result;
}

function solutionLock(key: number[][], lock: number[][]): boolean {
  const n = lock.length;
  const m = key.length;
  const board = Array.from({ length: 3 * n }, () => new Array(3 * n).fill(0));
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      board[n + i][n + j] = lock[i][j];
    }
  }

  const check = (): boolean => {
    for (let i = n; i < 2 * n; i++) {
      for (let j = n; j < 2 * n; j++) {
        if (board[i][j] !== 1) {
          return false;
        }
      }
    }
    return true;
  };

  let rotatedKey = key;
  for (let r = 0; r < 4; r++) {
    rotatedKey = rotate90(rotatedKey);
    for (let x = 0; x < 2 * n; x++) {
      for (let y = 0; y < 2 * n; y++) {
        // 열쇠 더하기
        for (let i = 0; i < m; i++) {
          for (let j = 0; j < m; j++) {
            board[x + i][y + j] += rotatedKey[i][j];
          }
        }
        if (check()) {
          return true;
        }
        // 원상복구 (빼기)
        for (let i = 0; i < m; i++) {
          for (let j = 0; j < m; j++) {
            board[x + i][y + j] -= rotatedKey[i][j];
          }
        }
      }
    }
  }
  return false;
}
```

> **핵심 통찰**: 2차원 **회전 함수**(`rotate90`)와 "큰 보드 중앙에 놓고 슬라이딩"은 격자 완전 탐색의 정형 패턴이다. 더한 값이 `1`이면 정확히 채움, `0`은 미충족, `2`는 겹침으로 자연스럽게 판정된다.

## Q11 뱀

| 항목 | 값 |
|------|-----|
| 난이도 | ★★★ 중 |
| 기출 | 삼성전자 SW 역량테스트 |

### 문제 요약

N×N 보드에서 뱀이 매초 머리를 전진(사과 먹으면 길이 +1, 아니면 꼬리 당김). 벽/자기 몸에 부딪히면 종료. 방향 전환(`X`초 후 `L`/`D`) 정보가 주어질 때 **끝나는 시각**을 구하라.

예: 입력1 → `9`

### 핵심 아이디어

머리 좌표 큐(또는 배열)와 점유 집합으로 뱀 몸을 관리한다. 방향은 시계 순서(우→하→좌→상)로 두고, `D`면 +1, `L`이면 −1(mod 4)로 회전한다.

```ts
function snake(input: string): number {
  const lines = input.split("\n");
  let idx = 0;
  const n = Number(lines[idx++]);
  const k = Number(lines[idx++]);
  const apple = new Set<string>();
  for (let i = 0; i < k; i++) {
    const [r, c] = lines[idx++].split(" ").map(Number);
    apple.add(`${r},${c}`);
  }
  const l = Number(lines[idx++]);
  const turns: [number, string][] = [];
  for (let i = 0; i < l; i++) {
    const [x, ch] = lines[idx++].split(" ");
    turns.push([Number(x), ch]);
  }

  const dx = [0, 1, 0, -1]; // 우, 하, 좌, 상
  const dy = [1, 0, -1, 0];
  let direction = 0;
  let x = 1;
  let y = 1;
  const snakeBody: [number, number][] = [[1, 1]];
  const occupied = new Set<string>(["1,1"]);
  let time = 0;
  let turnIdx = 0;

  while (true) {
    time++;
    const nx = x + dx[direction];
    const ny = y + dy[direction];
    // 벽 또는 자기 몸 충돌
    if (nx < 1 || nx > n || ny < 1 || ny > n || occupied.has(`${nx},${ny}`)) {
      break;
    }
    x = nx;
    y = ny;
    snakeBody.push([x, y]);
    occupied.add(`${x},${y}`);
    if (apple.has(`${x},${y}`)) {
      apple.delete(`${x},${y}`); // 사과: 꼬리 유지
    } else {
      const [tx, ty] = snakeBody.shift()!;
      occupied.delete(`${tx},${ty}`); // 꼬리 당김
    }
    // 방향 전환
    if (turnIdx < turns.length && turns[turnIdx][0] === time) {
      direction = turns[turnIdx][1] === "D" ? (direction + 1) % 4 : (direction + 3) % 4;
      turnIdx++;
    }
  }
  return time;
}
```

## Q12 기둥과 보 설치

| 항목 | 값 |
|------|-----|
| 난이도 | ★★★ 상 |
| 기출 | 2020 카카오 신입공채 |

### 문제 요약

기둥(0)·보(1)를 설치/삭제하는 명령을 수행한다. 각 작업 후 **모든 구조물이 규칙을 만족**해야 하며, 안 되면 그 작업은 무시. 최종 구조물을 정렬해 반환.

- 기둥: 바닥 위 / 보의 끝 위 / 다른 기둥 위
- 보: 한쪽 끝이 기둥 위 / 양 끝이 보에 연결

### 핵심 아이디어

설치/삭제를 **일단 적용한 뒤, 전체 구조물의 유효성을 다시 검사**한다. 위반이면 되돌린다(시뮬레이션 + 전수 검증).

```ts
function possible(structures: Set<string>): boolean {
  for (const s of structures) {
    const [x, y, a] = s.split(",").map(Number);
    if (a === 0) {
      // 기둥: 바닥 / 보 끝 / 기둥 위
      if (y === 0 || structures.has(`${x},${y - 1},0`) || structures.has(`${x - 1},${y},1`) || structures.has(`${x},${y},1`)) {
        continue;
      }
      return false;
    } else {
      // 보: 한쪽 끝 기둥 위 / 양끝 보 연결
      if (structures.has(`${x},${y - 1},0`) || structures.has(`${x + 1},${y - 1},0`) || (structures.has(`${x - 1},${y},1`) && structures.has(`${x + 1},${y},1`))) {
        continue;
      }
      return false;
    }
  }
  return true;
}

function solutionFrame(n: number, buildFrame: number[][]): number[][] {
  const structures = new Set<string>();
  for (const [x, y, a, b] of buildFrame) {
    const key = `${x},${y},${a}`;
    if (b === 1) {
      structures.add(key);
      if (!possible(structures)) {
        structures.delete(key); // 설치 무효 → 되돌림
      }
    } else {
      structures.delete(key);
      if (!possible(structures)) {
        structures.add(key); // 삭제 무효 → 복구
      }
    }
  }
  const result = [...structures].map((s) => s.split(",").map(Number));
  // x → y → a 오름차순
  result.sort((p, q) => p[0] - q[0] || p[1] - q[1] || p[2] - q[2]);
  return result;
}
```

> **핵심 통찰**: "작업 후 조건을 만족해야 한다"는 문제는 **낙관적 적용 → 전체 검증 → 실패 시 롤백** 패턴이 깔끔하다. 구조물을 `"x,y,a"` 문자열 키의 `Set`으로 두면 존재 검사가 O(1)이다.

## Q13 치킨 배달

| 항목 | 값 |
|------|-----|
| 난이도 | ★★★ 중 |
| 기출 | 삼성전자 SW 역량테스트 |

### 문제 요약

치킨집 중 **최대 M개만 남기고** 폐업시킬 때, 모든 집의 "치킨 거리(가장 가까운 치킨집까지 맨해튼 거리)" 합의 **최솟값**을 구하라.

예: 입력1(5×5, M=3) → `5`

### 핵심 아이디어

치킨집은 최대 13개이므로 **M개를 고르는 조합**을 모두 시도(완전 탐색)하고, 각 조합마다 집들의 치킨 거리 합을 계산해 최소를 취한다.

```ts
function combinations<T>(arr: T[], k: number): T[][] {
  const result: T[][] = [];
  const pick = (start: number, chosen: T[]) => {
    if (chosen.length === k) {
      result.push([...chosen]);
      return;
    }
    for (let i = start; i < arr.length; i++) {
      chosen.push(arr[i]);
      pick(i + 1, chosen);
      chosen.pop();
    }
  };
  pick(0, []);
  return result;
}

function chicken(input: string): number {
  const lines = input.split("\n");
  const [n, m] = lines[0].split(" ").map(Number);
  const houses: [number, number][] = [];
  const chickens: [number, number][] = [];
  for (let i = 1; i <= n; i++) {
    const row = lines[i].split(" ").map(Number);
    for (let j = 0; j < n; j++) {
      if (row[j] === 1) {
        houses.push([i, j]);
      } else if (row[j] === 2) {
        chickens.push([i, j]);
      }
    }
  }

  let result = Infinity;
  for (const combo of combinations(chickens, m)) {
    let total = 0;
    for (const [hr, hc] of houses) {
      let minDist = Infinity;
      for (const [cr, cc] of combo) {
        minDist = Math.min(minDist, Math.abs(hr - cr) + Math.abs(hc - cc));
      }
      total += minDist;
    }
    result = Math.min(result, total);
  }
  return result;
}
```

## Q14 외벽 점검

| 항목 | 값 |
|------|-----|
| 난이도 | ★★★ 상 |
| 기출 | 2020 카카오 신입공채 1차 |

### 문제 요약

둘레 n인 원형 외벽의 취약 지점(`weak`)을, 이동 거리(`dist`)가 제각각인 친구들로 모두 점검할 때 **최소 친구 수**를 구하라. 불가능하면 -1.

예: n=12, `weak=[1,5,6,10]`, `dist=[1,2,3,4]` → `2`

### 핵심 아이디어

원형이므로 weak를 **선형으로 펼치고**(`weak + (weak+n)`), 각 시작점에서 `dist`의 **모든 순열**로 친구를 배치하며 그리디로 커버한다. 가장 적은 친구 수가 답이다.

```ts
function permutations<T>(arr: T[]): T[][] {
  if (arr.length <= 1) {
    return [arr];
  }
  const result: T[][] = [];
  for (let i = 0; i < arr.length; i++) {
    const rest = [...arr.slice(0, i), ...arr.slice(i + 1)];
    for (const p of permutations(rest)) {
      result.push([arr[i], ...p]);
    }
  }
  return result;
}

function solutionWall(n: number, weak: number[], dist: number[]): number {
  const length = weak.length;
  const extended = [...weak, ...weak.map((w) => w + n)]; // 원형 → 선형
  let answer = dist.length + 1;

  for (let start = 0; start < length; start++) {
    for (const perm of permutations(dist)) {
      let count = 1; // 투입 친구 수
      let position = extended[start] + perm[count - 1]; // 현재 친구가 커버하는 끝
      for (let i = start; i < start + length; i++) {
        if (extended[i] > position) {
          count++;
          if (count > dist.length) {
            break;
          }
          position = extended[i] + perm[count - 1];
        }
      }
      answer = Math.min(answer, count);
    }
  }
  return answer > dist.length ? -1 : answer;
}
console.log(solutionWall(12, [1, 5, 6, 10], [1, 2, 3, 4])); // 2
```

> **핵심 통찰**: 원형 문제는 **배열을 두 배로 펼쳐** 선형으로 다루는 게 정석이다. `dist` 길이가 최대 8이라 순열(8! = 40,320)을 시작점마다 돌려도 충분하다 — 입력 크기가 작으면 완전 탐색이 답이다.

---

## 요약

- **럭키 스트레이트·문자열 재정렬**: 자릿수/문자 분류 — 기본 문자열 처리.
- **문자열 압축**: 단위 길이 1~len/2 완전 탐색.
- **자물쇠와 열쇠**: 2차원 **회전(`rotate90`) + 슬라이딩**, 큰 보드 중앙 배치.
- **뱀·기둥과 보**: 시뮬레이션 — 뱀은 점유 집합, 기둥/보는 **낙관 적용 → 전수 검증 → 롤백**.
- **치킨 배달**: 치킨집 **조합** 완전 탐색 + 맨해튼 거리.
- **외벽 점검**: 원형 **펼치기 + 순열** 그리디.
- 공통 도구: **회전, 조합, 순열** 헬퍼는 구현 기출의 필수 무기다.
