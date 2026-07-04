# 이것이 취업을 위한 코딩 테스트다 (나동빈) — 학습 노트

> 원서는 **Python** 기반이지만, 이 노트는 모든 코드 예제를 **TypeScript**로 옮겨 정리했다. 프론트엔드/Node.js 개발자가 코딩 테스트를 준비할 때 바로 활용할 수 있도록, Python 특유의 도구(`heapq`, `bisect`, `deque`, 슬라이싱 등)를 TS 관용구로 대체하는 변환 포인트를 함께 담았다.

## 이 노트의 특징

- **언어**: TypeScript(`.ts`) 주력. 도입 예제 일부만 Python 원본을 병기.
- **검증**: 각 챕터의 핵심 알고리즘 코드를 `node`로 실제 실행해 정답 예제와 대조했다(청소년·어른 상어 시뮬레이션 제외 — 본문 참고).
- **TS 변환 포인트**: `Array.prototype.sort()`의 사전순 함정, 우선순위 큐(MinHeap) 직접 구현, 중간점 비트 시프트 오버플로, `Math.trunc` vs `Math.floor`, 큐의 `shift()` O(n) 함정 등 TS 고유의 주의점을 콜아웃으로 강조.

## 구성

### Part 1 — 준비 (참고)

- `ch00-javascript-basics-for-coding-test.md` — 코딩 테스트용 JavaScript/TypeScript 기본 문법 (원서 **부록 A**의 JS/TS 변환판: 자료형, 자료구조, 복잡도, 표준 기능)

> 원서 Ch01(코딩 테스트 개요·복잡도)·Ch02(연도별 유형 분석)는 ch00의 빅오 정리와 중복되거나 노트 가치가 낮아 생략.

### Part 2 — 주요 알고리즘 이론

| 챕터 | 주제 | 핵심 |
|------|------|------|
| `ch03-greedy.md` | 그리디 | 국소 최적 선택 + 정당성 검증 |
| `ch04-implementation.md` | 구현 | 방향 벡터(dx/dy), 완전 탐색·시뮬레이션 |
| `ch05-dfs-bfs.md` | DFS/BFS | 스택·큐·재귀, 격자 그래프 모델링, **큐 O(1) 구현** |
| `ch06-sorting.md` | 정렬 | 선택·삽입·퀵·계수 정렬, **sort() 비교 함수 필수** |
| `ch07-binary-search.md` | 이진 탐색 | lower/upper bound, **파라메트릭 서치** |
| `ch08-dynamic-programming.md` | DP | 점화식, 탑다운 vs 바텀업 |
| `ch09-shortest-path.md` | 최단 경로 | 다익스트라(**MinHeap 직접 구현**), 플로이드 워셜 |
| `ch10-graph-theory.md` | 그래프 이론 | Union-Find, 크루스칼 MST, 위상 정렬 |

### Part 3 — 알고리즘 유형별 기출문제

| 챕터 | 유형 | 문제 |
|------|------|------|
| `ch11-greedy-problems.md` | 그리디 | 모험가 길드, 곱하기 혹은 더하기, 문자열 뒤집기, 만들 수 없는 금액, 볼링공 고르기, 무지의 먹방 |
| `ch12-implementation-problems.md` | 구현 | 럭키 스트레이트, 문자열 재정렬·압축, 자물쇠와 열쇠, 뱀, 기둥과 보, 치킨 배달, 외벽 점검 |
| `ch13-dfs-bfs-problems.md` | DFS/BFS | 특정 거리의 도시, 연구소, 경쟁적 전염, 괄호 변환, 연산자 끼워 넣기, 감시 피하기, 인구 이동, 블록 이동하기 |
| `ch14-sorting-problems.md` | 정렬 | 국영수, 안테나, 실패율, 카드 정렬하기 |
| `ch15-binary-search-problems.md` | 이진 탐색 | 특정 수의 개수, 고정점, 공유기 설치, 가사 검색 |
| `ch16-dynamic-programming-problems.md` | DP | 금광, 정수 삼각형, 퇴사, 병사 배치하기, 못생긴 수, 편집 거리 |
| `ch17-shortest-path-problems.md` | 최단 경로 | 플로이드, 정확한 순위, 화성 탐사, 숨바꼭질 |
| `ch18-graph-theory-problems.md` | 그래프 이론 | 여행 계획, 탑승구, 어두운 길, 행성 터널, 최종 순위 |
| `ch19-samsung-2020.md` | 삼성 기출 | 아기 상어, 청소년 상어, 어른 상어 |

> 원서 **부록 B**(기타 알고리즘)·**부록 C**(개발형 코딩 테스트)·**부록 D**(기출 풀이)는 이 노트의 범위에 포함하지 않았다. 기출 문제의 풀이는 각 챕터 내에 직접 TS로 작성·검증했다.

## 학습 순서

1. **ch00**으로 TS 코딩 테스트 기본기를 다진다(특히 `Map`/`Set`, 정렬 비교 함수, 큐 구현).
2. **Part 2(ch03~10)**로 알고리즘 유형을 익힌다 — 각 챕터의 `## 핵심 질문`과 점화식/패턴을 먼저 본다.
3. **Part 3(ch11~19)**에서 같은 유형의 기출을 풀며 이론을 적용한다. 이론 챕터에서 만든 도구(MinHeap, Union-Find, 조합·순열 헬퍼)가 그대로 재사용된다.

## 파일

- `origin.md` — PDF에서 추출한 원본 (작업 소스, 학습 노트 아님)
- `db-design.md` — 학습 진도 추적용 Notion DB 설계 명세 (노트 아님)
