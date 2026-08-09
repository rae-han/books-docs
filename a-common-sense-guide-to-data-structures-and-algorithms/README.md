# 누구나 자료 구조와 알고리즘 (A Common-Sense Guide to Data Structures and Algorithms)

> *A Common-Sense Guide to Data Structures and Algorithms* (2nd Edition, Jay Wengrow, Pragmatic Bookshelf, 2020)<br>한국어판: "누구나 자료 구조와 알고리즘 (개정2판)" (심지현 옮김, 길벗, 2021)

수학 공식 없이 **상식적인 직관과 그림**으로 자료 구조와 알고리즘을 이해하는 입문서. "이 코드가 몇 단계 걸리는가?"라는 단 하나의 질문을 축으로 배열부터 그래프까지, 버블 정렬부터 동적 프로그래밍까지를 관통한다. 개정2판에서 각 장 연습 문제(+해답), 일상 코드 빅 오 분석, 동적 프로그래밍 등 새 장이 추가되었다.

## 책 정보

| 항목 | 내용 |
|------|------|
| **저자** | 제이 웬그로우 (Jay Wengrow) |
| **역자** | 심지현 |
| **출판** | 길벗, 2021 (개정2판) |
| **원서** | *A Common-Sense Guide to Data Structures and Algorithms, 2nd Edition* (Pragmatic Bookshelf, 2020) |
| **대상 독자** | 자료 구조·알고리즘을 처음 배우거나, 수학 위주 교재에 좌절한 실무 개발자 |

## 개요

이 책의 포지션은 "CS 비전공자를 위한 자료 구조·알고리즘 첫 책"이다. 대학 교재처럼 증명과 수식으로 접근하는 대신, **단계 수 세기**라는 상식적 도구 하나로 빅 오 표기법을 도출하고, 모든 자료 구조를 읽기·검색·삽입·삭제 4대 연산의 효율로 비교한다. 코드 예제는 Ruby·Python·JavaScript를 장별로 혼용하며, 언어보다 개념 전달에 집중한다.

구성은 크게 세 흐름이다. ① 빅 오라는 렌즈 만들기(Ch1~7) - 배열·집합·정렬 예제로 O(1)부터 O(N²)까지 도출, ② 렌즈로 자료 구조 고르기(Ch8~9, 14~18) - 해시 테이블·스택·큐·연결 리스트·트리·힙·트라이·그래프, ③ 알고리즘 설계 기법(Ch10~13, 19~20) - 재귀, 동적 프로그래밍, 퀵 정렬, 공간 복잡도와 실전 최적화 전략.

코딩 테스트 대비서(this-is-coding-test, programmers-coding-test)를 읽기 전의 **개념 기반 다지기**로 적합하다 - 문제 풀이 요령이 아니라 "왜 이 자료 구조인가"를 설명하는 책이다.

## 목차

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 1 | [Why Data Structures Matter (자료 구조가 중요한 까닭)](notes/ch01-why-data-structures-matter.md) | 자료 구조, 배열, 집합, 4대 연산 | 같은 코드도 자료 구조에 따라 효율이 달라진다 - 읽기·검색·삽입·삭제로 배열 분석 |
| 2 | [Why Algorithms Matter (알고리즘이 중요한 까닭)](notes/ch02-why-algorithms-matter.md) | 알고리즘, 선형 검색, 이진 검색, 정렬된 배열 | 같은 문제도 알고리즘에 따라 속도가 달라진다 - 정렬된 배열과 이진 검색 |
| 3 | [O Yes! Big O Notation (빅 오 표기법)](notes/ch03-big-o-notation.md) | 빅 오 표기법, O(1), O(N), O(log N) | 단계 수를 데이터 크기 N의 함수로 - 효율을 말하는 공통 언어 |
| 4 | [Speeding Up Your Code with Big O (빅 오로 코드 속도 올리기)](notes/ch04-speeding-up-your-code-with-big-o.md) | 버블 정렬, O(N²), 중첩 루프 | 버블 정렬로 배우는 O(N²) - 빅 오가 리팩터링의 나침반이 된다 |
| 5 | [Optimizing Code with and Without Big O (빅 오를 사용하거나 사용하지 않는 코드 최적화)](notes/ch05-optimizing-code-with-and-without-big-o.md) | 선택 정렬, 상수 무시, 빅 오의 한계 | 같은 O(N²)라도 2배 빠를 수 있다 - 상수를 무시하는 빅 오 너머 보기 |
| 6 | [Optimizing for Optimistic Scenarios (긍정적인 시나리오 최적화)](notes/ch06-optimizing-for-optimistic-scenarios.md) | 삽입 정렬, 최악/평균/최선 시나리오 | 최악의 경우만 보지 마라 - 평균 시나리오가 실질 성능을 좌우한다 |
| 7 | [Big O in Everyday Code (일상적인 코드 속 빅 오)](notes/ch07-big-o-in-everyday-code.md) | 빅 오 분석, 일상 코드 판별 | 실무에서 마주치는 함수들의 빅 오를 직접 판별하는 훈련 |
| 8 | [Blazing Fast Lookup with Hash Tables (해시 테이블로 매우 빠른 룩업)](notes/ch08-blazing-fast-lookup-with-hash-tables.md) | 해시 테이블, 해시 함수, 충돌, O(1) 룩업 | 키→값 O(1) 룩업의 마법 - 충돌 처리와 실전 활용 패턴 |
| 9 | [Crafting Elegant Code with Stacks and Queues (스택과 큐로 간결한 코드 생성)](notes/ch09-crafting-elegant-code-with-stacks-and-queues.md) | 스택, 큐, LIFO/FIFO, 제약 자료 구조 | 제약이 만드는 우아함 - 스택(LIFO)과 큐(FIFO)의 활용처 |
| 10 | [Recursively Recurse with Recursion (재귀를 사용한 재귀적 반복)](notes/ch10-recursively-recurse-with-recursion.md) | 재귀, 기저 조건, 호출 스택 | 루프 대신 자신을 호출한다 - 기저 조건과 호출 스택으로 재귀 읽기 |
| 11 | [Learning to Write in Recursive (재귀적으로 작성하는 법)](notes/ch11-learning-to-write-in-recursive.md) | 재귀적 사고, 하위 문제, 하향식 사고 | "하위 문제에 떠넘기기" - 재귀 코드를 직접 작성하는 요령 |
| 12 | [Dynamic Programming (동적 프로그래밍)](notes/ch12-dynamic-programming.md) | 동적 프로그래밍, 메모이제이션, 상향식, 중복 하위 문제 | 중복 재귀 호출 제거 - 메모이제이션과 상향식으로 O(2^N)을 O(N)으로 |
| 13 | [Recursive Algorithms for Speed (속도를 높이는 재귀 알고리즘)](notes/ch13-recursive-algorithms-for-speed.md) | 퀵 정렬, 분할, 퀵 셀렉트, O(N log N) | 분할 기반 퀵 정렬과 퀵 셀렉트 - 평균 O(N log N) 대표 재귀 알고리즘 |
| 14 | [Node-Based Data Structures (노드 기반 자료 구조)](notes/ch14-node-based-data-structures.md) | 연결 리스트, 노드, 이중 연결 리스트 | 메모리에 흩어진 노드를 링크로 잇는다 - 삽입/삭제에 강한 연결 리스트 |
| 15 | [Speeding Up All the Things with Binary Search Trees (이진 탐색 트리로 속도 향상)](notes/ch15-speeding-up-all-the-things-with-binary-search-trees.md) | 이진 탐색 트리, O(log N), 트리 순회 | 정렬 유지와 빠른 검색/삽입/삭제를 동시에 - BST와 중위 순회 |
| 16 | [Keeping Your Priorities Straight with Heaps (힙으로 우선순위 유지하기)](notes/ch16-keeping-your-priorities-straight-with-heaps.md) | 힙, 우선순위 큐, 완전 트리 | 항상 최댓값(최솟값)이 루트 - 힙으로 구현하는 우선순위 큐 |
| 17 | [It Doesn't Hurt to Trie (트라이(trie)해 보는 것도 나쁘지 않다)](notes/ch17-it-doesnt-hurt-to-trie.md) | 트라이, 접두사 검색, 자동 완성 | 문자 단위 트리로 만드는 자동 완성 - 단어 길이에만 비례하는 검색 |
| 18 | [Connecting Everything with Graphs (그래프로 뭐든지 연결하기)](notes/ch18-connecting-everything-with-graphs.md) | 그래프, 깊이 우선 탐색, 너비 우선 탐색, 데이크스트라 알고리즘 | 관계를 표현하는 자료 구조 - DFS/BFS와 가중 그래프 최단 경로 |
| 19 | [Dealing with Space Constraints (공간 제약 다루기)](notes/ch19-dealing-with-space-constraints.md) | 공간 복잡도, 시간-공간 트레이드오프 | 빅 오로 메모리 사용량도 잰다 - 시간 vs 공간 트레이드오프 |
| 20 | [Techniques for Code Optimization (코드 최적화 기법)](notes/ch20-techniques-for-code-optimization.md) | 최적화 전략, 마법의 룩업, 탐욕 알고리즘 | 가능한 최선의 빅 오를 먼저 상상하라 - 마법의 룩업·탐욕 등 실전 기법 |

## 학습 가이드

**순서대로 읽는 것을 권장** - Ch1~7이 만든 "빅 오 렌즈"를 이후 모든 장이 사용한다. 특히 Ch3(빅 오 도출)과 Ch6(시나리오 구분)은 뒤 장들의 전제다.

주제별로 골라 읽는다면:

- **빅 오·복잡도 분석**: Ch1 → Ch2 → Ch3 → Ch5 → Ch6 → Ch7 → Ch19
- **정렬 알고리즘**: Ch4(버블) → Ch5(선택) → Ch6(삽입) → Ch13(퀵)
- **자료 구조 선택**: Ch8(해시) → Ch9(스택·큐) → Ch14(연결 리스트) → Ch15(BST) → Ch16(힙) → Ch17(트라이) → Ch18(그래프)
- **재귀와 알고리즘 설계**: Ch10 → Ch11 → Ch12(DP) → Ch13(퀵 정렬)
- **실전 최적화**: Ch19 → Ch20 (책 전체의 총정리 - 마지막에 읽기)

## Notion DB 구조

- **위치**: Raehan's Must reads > Dev DB > [누구나 자료 구조와 알고리즘](https://app.notion.com/p/3aede4986fe381768c5cc820a683ac65) 페이지 안의 DB "[챕터](https://app.notion.com/p/ccd92c7072284ff5aa20b69d8096f003)" (`collection://19e3783f-19b0-46d7-8efc-a7e071d5ba7b`)
- **속성**: ① `Done`(checkbox - 읽음 표시, 값은 사용자가 직접 체크) ② `Name`(title, `ChNN. 영문 제목 (한국어판 제목)` 형식) ③ `Chapter`(number 1~20) ④ `주제`(select 색상 딱지) ⑤ `핵심 단어`(multi-select, README 목차 표 소스) ⑥ `핵심 요약`(text, README 목차 표 소스)
- **주제 딱지 매핑** (파트 없는 책이라 파트 대신 주제 분류 사용): 빅 오 렌즈(Ch1~7, 파랑) / 자료 구조(Ch8~9·14~18, 초록) / 알고리즘 설계(Ch10~13, 주황) / 실전 최적화(Ch19~20, 보라)
- **정렬**: `Name`의 `ChNN.` 두 자리 접두어로 이름 오름차순 정렬(또는 `Chapter` 오름차순). 업로드는 역순(Ch20→Ch1)으로 생성해 기본 뷰에서도 Ch1이 맨 위
- **본문 변환 규칙**: `> **핵심 통찰**:` → `::: callout {icon="💡" color="gray_bg"}` 콜아웃, 마크다운 표 → `<table header-row="true">`(td 별도 줄), H1 제거(제목은 Name 속성). 레이블 없는 인용문은 quote 블록 유지
- ⚠️ **업로드 시 한글은 반드시 리터럴로**: 도구 입력에 `\uXXXX` 유니코드 이스케이프를 쓰면 받침이 깨진다(실제 발생: 돈다→돌다, 잰다→잴다, 옮겨야→옆겨야, 썼다면→쎜다면, 뺀→뻐, 붓는다→부는다, 숟가락→숨가락). 20개 챕터 전량을 한글 리터럴로 재업로드해 교정했으며, 재업로드 시에도 같은 원칙을 지킬 것

## 핵심 개념 맵

- 모든 분석의 축은 **4대 연산**(읽기·검색·삽입·삭제)의 **단계 수 세기** - 여기서 빅 오가 자연스럽게 도출된다
- **빅 오 표기법**은 "N개 데이터일 때 몇 단계인가"의 함수 표현 - 상수를 버리므로(Ch5) 같은 빅 오 안에서의 우열은 시나리오 분석(Ch6)으로 가린다
- **자료 구조 선택 = 연산별 트레이드오프**: 해시 테이블(검색 O(1), 순서 없음) vs BST(정렬 유지, O(log N)) vs 연결 리스트(삽입/삭제 강함, 읽기 약함)
- **제약이 곧 설계**: 스택·큐는 배열에서 기능을 뺀 구조 - 제약이 의도를 드러내고 버그를 막는다
- **재귀는 설계 기법의 뿌리**: 재귀(Ch10~11) → 중복 제거하면 동적 프로그래밍(Ch12) → 분할에 적용하면 퀵 정렬(Ch13)
- **최적화의 제1질문**은 "가능한 최선의 빅 오는 무엇인가?"를 먼저 상상하고, 마법의 룩업(해시 테이블 끼워 넣기)·탐욕 접근을 시도하는 것(Ch20)
- 시간이 전부가 아니다 - **공간 복잡도**(Ch19)까지 재야 트레이드오프가 완성된다

## 인용문

전 책 통합 모음은 [루트 QUOTES.md](../QUOTES.md) 참조.

> 이 책에서 오직 한 가지만 배워야 한다면 이것이다 - 연산이 얼마나 "빠른가"는 **시간이 아니라 단계(step) 수**로 측정한다.<br>- 제이 웬그로우 (위치: Ch2)

> 빅 오 표기법은 단 하나의 **핵심 질문**에 대한 답이다 - **"데이터 원소가 N개일 때, 알고리즘에 몇 단계가 필요할까?"**<br>- 제이 웬그로우 (위치: Ch3)

> 빅 오의 본질은 단계 수 자체가 아니라 **"데이터가 늘어날 때 알고리즘의 단계 수가 어떻게 증가하는가"**다.<br>- 제이 웬그로우 (위치: Ch3)

> "정렬 유지"라는 제약(삽입이 느려지는 비용)이 이진 검색이라는 강력한 알고리즘(검색이 빨라지는 이득)을 사준다 - **자료 구조의 제약과 알고리즘의 능력은 거래 관계다.**<br>- 제이 웬그로우 (위치: Ch2)

> **배열 크기를 두 배로 늘릴 때마다 이진 검색은 딱 한 단계만 늘어난다.** 확인할 때마다 남은 원소의 절반이 제거되기 때문이다.<br>- 제이 웬그로우 (위치: Ch2)

> **중첩 루프가 보이면 머릿속에 O(N²) 경보가 울려야 한다.** 마주치면 시간을 들여 더 빠른 대안을 깊이 고민해 볼 신호다.<br>- 제이 웬그로우 (위치: Ch4)

> 빅 오에서 내 알고리즘이 "느린" 카테고리에 속한다면, 한 발짝 물러나 **더 빠른 빅 오 카테고리로 들어갈 수 있는지** 고민해 보라. 불가능하다고 결론 내리기 전에 꼭 생각해 볼 가치가 있다.<br>- 제이 웬그로우 (위치: Ch4)

> **정의상 가장 자주 일어나는 경우가 평균 시나리오다.** 임의의 배열이 완벽한 오름차순/내림차순일 확률이 얼마나 되겠는가.<br>- 제이 웬그로우 (위치: Ch6)
