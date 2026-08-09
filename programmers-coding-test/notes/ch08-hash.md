# Chapter 08: Hash (해시)

## 핵심 질문

키를 해시 함수로 변환해 인덱스로 삼아 O(1)에 데이터를 찾는 자료구조는 어떻게 동작하는가? 자바스크립트의 객체와 `Map`은 어떻게 활용하며, 어떤 문제에서 해시를 떠올려야 하는가?

## 1. 해시의 개념

해시(hash)는 **키(key)** 를 **해시 함수**로 변환해 얻은 값을 인덱스로 삼아 키와 값을 저장하는 자료구조다. 키만 알면 값에 **O(1)에 접근**할 수 있다.

### 해시의 특징

1. **단방향 동작**: 키 → 값은 가능하지만, 값 → 키는 불가능.
2. **O(1) 접근**: 인덱스 탐색이 필요 없다.
3. **키를 인덱스로 변환**하는 적절한 변환 과정이 필요하다.

```
키        해시 함수    인덱스    값
"홍길동" → hash() → 3      → 010-1234-5678
"박철수" → hash() → 7      → 010-9876-5432
```

> **핵심 통찰**: "특정 데이터를 빈번히 탐색해야 한다", "키-값 매핑이 필요하다", "중복 체크"가 단서가 보이면 해시를 떠올려라. O(N²) 이중 반복문을 O(N)으로 줄이는 일반적 무기다.

### 해시의 활용 분야

- **비밀번호 관리**: 단방향 특성을 활용해 해싱한 비밀번호만 저장.
- **데이터베이스 인덱싱**: 대량 데이터의 효율적 검색.
- **블록체인**: 각 블록이 이전 블록의 해시값을 포함해 무결성 보장.

## 2. 해시 함수

해시 함수는 두 가지를 만족해야 한다.

1. 변환 결과가 **해시 테이블 크기를 넘지 않아야** 한다 (인덱스로 써야 하므로).
2. **충돌이 최대한 적어야** 한다 (서로 다른 키의 해시값이 같은 경우).

### 나눗셈법 (division method)

가장 간단한 해시 함수.

```
h(x) = x mod k
```

`k`는 **소수**여야 한다. 소수가 아니면 약수가 있어 그 배수에서 충돌이 잦아진다.

> **예**: `k=15`(=3×5)라면 3의 배수 입력에서 해시값이 `3, 6, 9, 12, 0, 3, 6, ...`로 반복.

### 곱셈법 (multiplication method)

황금비를 활용해 큰 소수가 필요 없는 방법.

```
h(x) = floor(((x * A) mod 1) * m)
```

`A`는 황금비(약 0.6180339887), `m`은 해시 테이블 크기.

### 문자열 해싱 (polynomial rolling)

문자열을 다항식 값으로 변환:

```
hash(s) = (s[0] + s[1]*p + s[2]*p² + ... + s[n-1]*p^(n-1)) mod m
```

`p=31`(홀수이자 메르센 소수에 가까움), `m`은 해시 테이블 크기.

오버플로 방지를 위해 **각 항마다 모듈러 연산**을 적용한다:

```
hash(s) = ((s[0]%m) + (s[1]*p % m) + ... + (s[n-1]*p^(n-1) % m)) % m
```

### JavaScript 구현

```javascript
function polynomialHash(str) {
  const p = 31;
  const m = 1_000_000_007; // 큰 소수
  let hashValue = 0;
  for (let i = 0; i < str.length; i++) {
    hashValue = (hashValue * p + str.charCodeAt(i)) % m;
  }
  return hashValue;
}
```

## 3. 충돌 처리

서로 다른 키의 해시값이 같은 경우 = **충돌(collision)**. 충돌 처리는 필수다.

### 체이닝 (chaining)

같은 해시값을 가진 데이터를 **연결 리스트**로 묶는 방식.

- 장점: 구현 간단.
- 단점: 충돌이 많으면 공간 낭비, 검색 성능 저하 (최악 O(N)).

### 개방 주소법 (open addressing)

빈 버킷을 찾아 충돌 데이터를 삽입하는 방식.

- **선형 탐사**: `h(k, i) = (h(k) + i) mod m` — 1칸씩 이동. 클러스터 형성 위험.
- **이중 해싱**: 두 번째 해시 함수로 점프 간격을 결정 — `h(k, i) = (h₁(k) + i × h₂(k)) mod m`.

> **합격 조언**: 코딩 테스트에서 해시 함수 자체를 직접 구현하라는 문제는 거의 없다. 자바스크립트의 **객체(`{}`)** 와 **`Map`, `Set`** 으로 풀면 된다. 다만 원리를 이해하면 면접에서 도움이 되고 효율적인 사용이 가능해진다.

## 4. JavaScript에서의 해시

자바스크립트는 **객체**와 **Map**을 통해 해시를 사용한다.

### 객체 (Object)

```javascript
const obj = {};
obj["apple"] = 5;
obj["banana"] = 3;

console.log(obj["apple"]); // 5
console.log("apple" in obj); // true
delete obj["apple"];
```

### Map

```javascript
const map = new Map();
map.set("apple", 5);
map.set("banana", 3);

console.log(map.get("apple")); // 5
console.log(map.has("apple")); // true
map.delete("apple");
console.log(map.size); // 1
```

| 비교 | 객체 | Map |
|------|------|-----|
| 키 타입 | 문자열/심볼 | 모든 타입 |
| 크기 조회 | `Object.keys(obj).length` | `map.size` |
| 순회 | `for...in`, `Object.entries` | `for...of`, 삽입 순서 보장 |
| 성능 | 작은 데이터에 빠름 | 빈번한 추가/삭제에 우수 |

> **합격 조언**: 코딩 테스트에서는 **객체**가 코드가 짧아 자주 쓰인다. 다만 키가 숫자이고 크기가 정해져 있으면 그냥 배열을 쓰는 게 빠르다.

### Set

값만 저장하는 해시 (중복 제거).

```javascript
const set = new Set([1, 2, 3, 3, 2]);
// Set { 1, 2, 3 }

set.add(4);
set.has(2);    // true
set.delete(1);
set.size;      // 3
```

## 5. 핵심 코드 패턴

### 빈도 카운팅

```javascript
const count = {};
for (const x of arr) {
  count[x] = (count[x] || 0) + 1;
}
```

### 키 존재 여부로 분기

```javascript
if (!obj[key]) {
  obj[key] = []; // 초기화
}
obj[key].push(value);
```

### 중복 제거

```javascript
const unique = [...new Set(arr)];
```

### 두 객체의 동등 비교 (얕은 비교)

```javascript
function isShallowEqual(a, b) {
  const keysA = Object.keys(a);
  const keysB = Object.keys(b);
  if (keysA.length !== keysB.length) return false;
  for (const key of keysA) {
    if (a[key] !== b[key]) return false;
  }
  return true;
}
```

### 보수(complement) 패턴 — Two Sum 류

```javascript
const seen = new Set();
for (const x of arr) {
  if (seen.has(target - x)) return true;
  seen.add(x);
}
```

## 6. JavaScript 빌트인 메서드 레퍼런스

### Object

| 메서드 | 동작 |
|--------|------|
| `obj[key]` / `obj.key` | 값 조회 (없으면 `undefined`) |
| `obj[key] = value` | 값 설정 |
| `key in obj` | 키 존재 여부 |
| `delete obj[key]` | 키 삭제 |
| `Object.keys(obj)` | 키 배열 |
| `Object.values(obj)` | 값 배열 |
| `Object.entries(obj)` | `[key, value]` 배열 |

### Map / Set

| 메서드 | 동작 | 비고 |
|--------|------|------|
| `map.set(k, v)` | 추가/갱신 | O(1) |
| `map.get(k)` | 조회 | O(1) |
| `map.has(k)` | 존재 여부 | O(1) |
| `set.add(x)` | 추가 | O(1) |
| `set.has(x)` | 존재 여부 | O(1) |
| `arr.includes(x)` | 배열 포함 여부 | O(N) ⚠️ — Set으로 대체 |

## 7. 몸풀기 문제

### 문제 18: 두 개의 수로 특정 값 만들기

> 양의 정수 배열 `arr`와 정수 `target`이 주어질 때, 두 수의 합이 `target`인 쌍이 있는지 판별.
> 권장 시간 복잡도: O(N + K)

**접근 아이디어**: O(N²) 이중 반복문 대신 해시 테이블에 원소 존재 여부를 저장하고, 각 원소 `x`에 대해 `target - x`가 있는지 O(1)에 검사.

```javascript
function solution(arr, target) {
  const set = new Set(arr);
  for (const num of arr) {
    const complement = target - num;
    if (complement !== num && set.has(complement)) {
      return true;
    }
  }
  return false;
}
```

> **함정**: `complement !== num` 체크가 필요하다. `target = 2 * num`일 때 같은 원소를 두 번 사용하면 안 되기 때문이다 (문제에서 "서로 다른 인덱스"라는 제약).

**시간 복잡도**: O(N)

### 문제 19: 문자열 해싱을 이용한 검색 함수 만들기

> `stringList`의 각 문자열을 해시 테이블에 저장하고, `queryList`의 각 문자열이 있는지 boolean 배열로 반환. **다항 해싱(polynomial rolling)** 으로 직접 구현.
> 권장 시간 복잡도: O(N + K)

```javascript
function polynomialHash(str) {
  const p = 31;
  const m = 1_000_000_007;
  let hashValue = 0;
  for (let i = 0; i < str.length; i++) {
    hashValue = (hashValue * p + str.charCodeAt(i)) % m;
  }
  return hashValue;
}

function solution(stringList, queryList) {
  const hashSet = new Set(stringList.map(polynomialHash));
  return queryList.map((query) => hashSet.has(polynomialHash(query)));
}
```

> **핵심 통찰**: `hashValue = hashValue * p + char` 형태(호너의 방법)로 작성하면 모듈러 연산을 한 번씩만 적용하면서도 다항식 값을 정확히 계산한다. `s[0] + s[1]*p + s[2]*p² + ...`를 매번 거듭제곱 계산하는 것보다 O(N)에 효율적.

**시간 복잡도**: O(N + K)

## 8. 합격자가 되는 모의테스트

### 문제 20: 완주하지 못한 선수 — 프로그래머스

> 참가자 명단 `participant`와 완주자 명단 `completion`이 주어진다. 둘의 차이는 한 명. 완주하지 못한 선수의 이름을 반환. 동명이인 가능.
> 제약: 길이 ≤ 100,000 → O(N) 필수
> [프로그래머스 #42576](https://programmers.co.kr/learn/courses/30/lessons/42576)

**접근 아이디어**: 객체에 `이름 → 인원수`를 저장. participant로 +1, completion으로 -1. 마지막에 값이 0이 아닌 키가 답.

```javascript
function solution(participant, completion) {
  const obj = {};

  for (const p of participant) {
    obj[p] = (obj[p] || 0) + 1;
  }

  for (const c of completion) {
    obj[c] -= 1;
  }

  for (const key in obj) {
    if (obj[key] > 0) return key;
  }
}
```

> **핵심 통찰**: 동명이인을 처리할 때 "이름 → 카운트" 매핑이 자연스럽게 해결한다. 단순 `Set` 사용은 동명이인을 놓친다.

**시간 복잡도**: O(N)

### 문제 21: 할인 행사 — 프로그래머스

> `want[i]`와 `number[i]`로 표현된 원하는 품목과 수량이 있다. `discount`(14일치 할인 품목)에서 10일 연속으로 원하는 품목과 수량이 일치하는 시작일의 개수를 반환.
> 제약: discount 길이 ≤ 100,000
> [프로그래머스 #131127](https://school.programmers.co.kr/learn/courses/30/lessons/131127)

**접근 아이디어**:
1. `want`/`number`를 객체로 변환 — `wantObj = { banana: 3, apple: 2, ... }`.
2. 각 시작일 `i`에 대해 `discount[i..i+9]` 10일 윈도우에서 빈도 객체를 만들고 `wantObj`와 비교.
3. 일치하면 카운트 증가.

```javascript
function isShallowEqual(a, b) {
  const keysA = Object.keys(a);
  const keysB = Object.keys(b);
  if (keysA.length !== keysB.length) return false;
  for (const key of keysA) {
    if (a[key] !== b[key]) return false;
  }
  return true;
}

function solution(want, number, discount) {
  const wantObj = {};
  for (let i = 0; i < want.length; i++) {
    wantObj[want[i]] = number[i];
  }

  let answer = 0;
  for (let i = 0; i <= discount.length - 10; i++) {
    const window = {};
    for (let j = i; j < i + 10; j++) {
      if (wantObj[discount[j]]) {
        window[discount[j]] = (window[discount[j]] || 0) + 1;
      }
    }
    if (isShallowEqual(window, wantObj)) {
      answer += 1;
    }
  }

  return answer;
}
```

> **함정**: 자바스크립트는 두 객체의 동등 비교를 기본 제공하지 않는다(`==`은 참조 비교). `isShallowEqual` 같은 헬퍼를 직접 작성해야 한다.

> **함정**: 윈도우를 구성할 때 `wantObj[discount[j]]`로 필터링해야 불필요한 품목이 끼어들지 않는다. 그래야 `isShallowEqual`이 정확히 일치하는 케이스만 잡는다.

**시간 복잡도**: O(N) — 윈도우 크기 10이 상수.

### 문제 22: 오픈 채팅방 — 2019 KAKAO BLIND

> `record`에 `Enter uid nick`, `Leave uid`, `Change uid newNick` 명령이 들어온다. 모든 명령 처리 후 최종 닉네임으로 표시되는 메시지 배열을 반환.
> 제약: 길이 ≤ 100,000
> [프로그래머스 #42888](https://programmers.co.kr/learn/courses/30/lessons/42888)

**접근 아이디어**: 닉네임 변경 시마다 기존 메시지를 모두 수정하면 O(N²). 대신 **2-pass** 전략:
- **1차 순회**: `uid → 최종 닉네임` 매핑을 완성 (Enter/Change에서만 갱신).
- **2차 순회**: 메시지 출력 시 `uid`로 최종 닉네임을 조회.

```javascript
function solution(record) {
  const uid = {};

  // 1차: 최종 닉네임 결정
  for (const line of record) {
    const cmd = line.split(" ");
    if (cmd[0] !== "Leave") {
      uid[cmd[1]] = cmd[2];
    }
  }

  // 2차: 출력 메시지 생성
  const answer = [];
  for (const line of record) {
    const cmd = line.split(" ");
    if (cmd[0] === "Enter") {
      answer.push(`${uid[cmd[1]]}님이 들어왔습니다.`);
    } else if (cmd[0] === "Leave") {
      answer.push(`${uid[cmd[1]]}님이 나갔습니다.`);
    }
  }

  return answer;
}
```

> **핵심 통찰**: "최종 상태"만 필요하다면 메시지를 매번 갱신할 필요가 없다. **불변 항목(uid)** 을 키로, **가변 항목(닉네임)** 을 값으로 두면 자연스럽게 풀린다. 코딩 테스트에서는 "최종 답에 정말 필요한 정보가 무엇인가?"를 자주 자문해야 한다.

**시간 복잡도**: O(N)

### 문제 23: 베스트 앨범 — 프로그래머스

> 노래의 장르 배열 `genres`와 재생 횟수 배열 `plays`. 다음 기준으로 베스트 앨범에 들어갈 노래의 고유번호를 반환.
> 1. 총 재생 횟수가 많은 장르 우선.
> 2. 장르 내에서 재생 횟수가 많은 곡 우선.
> 3. 재생 횟수가 같으면 고유번호가 낮은 곡 우선.
> 4. 장르당 최대 2곡.
> [프로그래머스 #42579](https://programmers.co.kr/learn/courses/30/lessons/42579)

**접근 아이디어**: 두 객체를 만든다.
- `playObj[genre]`: 장르별 총 재생 횟수.
- `genresObj[genre]`: 장르별 `[index, plays]` 배열.

장르를 총 재생 횟수로 정렬 → 각 장르 내에서 재생 횟수(내림차순), 동률시 인덱스(오름차순) 정렬 → 상위 2곡 선택.

```javascript
function solution(genres, plays) {
  const genresObj = {};
  const playObj = {};

  for (let i = 0; i < genres.length; i++) {
    const genre = genres[i];
    const play = plays[i];
    if (!(genre in genresObj)) {
      genresObj[genre] = [];
      playObj[genre] = 0;
    }
    genresObj[genre].push([i, play]);
    playObj[genre] += play;
  }

  // 총 재생 횟수 내림차순 장르 정렬
  const sortedGenres = Object.keys(playObj).sort(
    (a, b) => playObj[b] - playObj[a]
  );

  const answer = [];
  for (const genre of sortedGenres) {
    const sortedSongs = genresObj[genre].sort((a, b) => {
      return a[1] === b[1] ? a[0] - b[0] : b[1] - a[1];
    });
    answer.push(...sortedSongs.slice(0, 2).map((song) => song[0]));
  }

  return answer;
}
```

> **함정**: 장르 내 정렬에서 **재생 횟수 같으면 인덱스 오름차순** 조건을 빠뜨리기 쉽다. 입출력 예에 명시되지 않아도 제약 조건은 반드시 따라야 한다.

**시간 복잡도**: O(N log N)

### 문제 24: 신고 결과 받기 — 2022 KAKAO BLIND

> 유저 신고 시스템. K번 이상 신고된 유저는 정지되고, 그를 신고한 모든 유저에게 알림이 간다. `id_list` 순서대로 각 유저가 받은 알림 횟수를 반환.
> 제약: id_list ≤ 1,000, report ≤ 200,000
> [프로그래머스 #92334](https://programmers.co.kr/learn/courses/30/lessons/92334)

**접근 아이디어**:
1. `reportedUser[신고당한자] = Set(신고한자들)` — `Set`이 동일인의 중복 신고를 자동 처리.
2. 신고당한자별로 신고한자 수가 K 이상이면, 그를 신고한 모든 유저의 카운트 +1.

```javascript
function solution(id_list, report, k) {
  const reportedUser = {};
  const count = {};

  // ① 신고 기록 정리
  for (const r of report) {
    const [userId, reportedId] = r.split(" ");
    if (reportedUser[reportedId] === undefined) {
      reportedUser[reportedId] = new Set();
    }
    reportedUser[reportedId].add(userId); // Set이 중복 자동 처리
  }

  // ② 정지 기준에 부합하는 유저 처리
  for (const reportedId of Object.keys(reportedUser)) {
    if (reportedUser[reportedId].size >= k) {
      for (const uid of reportedUser[reportedId]) {
        count[uid] = (count[uid] || 0) + 1;
      }
    }
  }

  // ③ id_list 순서대로 결과 정리
  return id_list.map((id) => count[id] || 0);
}
```

> **핵심 통찰**: "한 유저를 여러 번 신고해도 1회로 처리"는 `Set`의 자연스러운 특성이다. 직접 중복 검사 로직을 짜지 말고 `Set`을 쓸 것.

**시간 복잡도**: O(N + M)

### 문제 25: 메뉴 리뉴얼 — 2021 KAKAO BLIND

> 손님들이 주문한 단품 메뉴 조합 `orders`와 코스 크기 배열 `course`. 각 코스 크기에 대해 가장 많이 함께 주문된 메뉴 조합(2명 이상)을 반환.
> [프로그래머스 #72411](https://programmers.co.kr/learn/courses/30/lessons/72411)

**접근 아이디어**:
1. 각 주문을 정렬(`"BCA"` → `"ABC"`) — 같은 메뉴 집합을 같은 키로 만들기 위해.
2. 각 코스 크기 `c`에 대해 모든 주문에서 `c`개 조합을 추출.
3. 빈도 카운팅 후 최댓값(>=2)을 가진 조합 반환.

```javascript
function combinations(arr, n) {
  if (n === 1) return arr.map((v) => [v]);
  const result = [];
  arr.forEach((fixed, idx, original) => {
    const rest = original.slice(idx + 1);
    const combis = combinations(rest, n - 1);
    const combine = combis.map((v) => [fixed, ...v]);
    result.push(...combine);
  });
  return result;
}

function solution(orders, course) {
  const answer = [];

  for (const c of course) {
    const menu = [];
    for (const order of orders) {
      const orderArr = order.split("").sort(); // 정렬 필수
      const comb = combinations(orderArr, c);
      menu.push(...comb);
    }

    // 빈도 카운팅
    const counter = {};
    for (const m of menu) {
      const key = m.join("");
      counter[key] = (counter[key] || 0) + 1;
    }

    const max = Math.max(...Object.values(counter));
    if (max > 1) {
      for (const [key, value] of Object.entries(counter)) {
        if (value === max) {
          answer.push(key);
        }
      }
    }
  }

  return answer.sort();
}
```

> **함정**: `combinations`는 입력 순서를 보존한다. `["B", "C", "A"]`와 `["A", "B", "C"]`는 다른 결과를 낸다. 그래서 각 주문을 **정렬 후** 조합을 뽑아야 같은 집합을 같은 키로 매핑할 수 있다.

> **함정**: "2명 이상이 주문한 조합만 후보"라는 조건. `max > 1` 체크를 빠뜨리면 1번만 주문된 조합도 들어간다.

**시간 복잡도**: O(N × 2^M) — N=주문 수, M=주문당 메뉴 수.

## 9. 함정/실수 노트

| 함정 | 설명 |
|------|------|
| 객체 동등 비교 | `obj1 === obj2`는 참조 비교 — 직접 키-값 순회 비교 |
| `Set`에 객체 저장 | 객체는 참조 비교라 중복 체크 안 됨 — 문자열로 직렬화 |
| `combinations` 결과의 순서 | 입력 순서 보존 — 같은 집합 같은 키로 매핑하려면 정렬 후 조합 |
| 동명이인 처리 | 단순 `Set`이 아니라 `이름 → 카운트` 매핑 |
| `Object.entries`의 키 타입 | 키는 항상 문자열 — 숫자 비교 시 `Number()` 변환 필요 |
| 보수 패턴의 자기 자신 매칭 | `target = 2x`일 때 같은 원소가 두 번 쓰이지 않도록 체크 |
| 중첩 객체 초기화 | `obj[key].push(...)` 전에 `obj[key] = []` 보장 |
| 모든 주문 매번 갱신 | "최종 상태"만 필요하면 2-pass(매핑 → 출력) 패턴이 효율적 |

## 10. 요약

- **해시는 키-값 매핑을 O(1)에 처리**하는 자료구조다. 해시 함수가 키를 인덱스로 변환한다.
- **자바스크립트는 객체와 `Map`/`Set`** 으로 해시를 사용한다. 코딩 테스트에서는 직접 해시 함수를 구현할 일이 거의 없다.
- **충돌 처리**는 체이닝과 개방 주소법이 있다. 면접용 지식.
- **빈도 카운팅, 보수 매칭, 동명이인 처리, 2-pass 매핑**이 해시의 4대 활용 패턴.
- **두 객체 동등 비교는 직접 구현**해야 한다.
- **`combinations`/`permutations` + 정렬**으로 같은 집합을 같은 키로 매핑하는 트릭이 자주 쓰인다.

## 리마인드 (저자)

1. 해시는 키와 값의 쌍으로 이루어진 자료구조다. 해시 함수로 키를 인덱스로 변환해 값에 빠르게 접근한다.
2. 해시 함수에는 나눗셈법, 곱셈법이 있다.
3. 충돌 처리에는 체이닝, 개방 주소법이 있다.
4. 실제 코딩 테스트에서 해시 관련 문제는 자바스크립트의 객체를 활용한다.
