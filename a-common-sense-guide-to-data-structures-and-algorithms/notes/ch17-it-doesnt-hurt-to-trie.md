# Chapter 17: It Doesn't Hurt to Trie (트라이(trie)해 보는 것도 나쁘지 않다)

## 핵심 질문

스마트폰의 자동 완성은 어떻게 "catn"만 치면 "catnip"·"catnap"을 즉시 찾아내는가? 사전이 아무리 커져도 검색 속도가 변하지 않는 자료 구조는 어떻게 생겼는가?

---

## 1. 자동 완성 문제

자동 완성을 위해 사전 전체를 어디에 저장할까?

- **정렬 안 된 배열**: "catn"으로 시작하는 단어를 찾으려면 전부 검사 - O(N) (N = 사전 단어 수, 매우 큼)
- **해시 테이블**: 단어 전체를 해싱해 위치를 정하므로 "catn"으로는 "catnip"의 위치를 알 수 없음
- **정렬된 배열 + 이진 검색**: O(log N) - 나쁘지 않지만 더 빨라질 수 있다

**트라이(*trie - 문자 단위로 노드를 이어 단어를 저장하는 트리. retrieval에서 유래했지만 tree와의 혼동을 피해 "트라이"로 발음. 프리픽스 트리·디지털 트리라고도 함*)**가 그 답이다. 자동 완성·자동 수정 같은 텍스트 기능 외에 IP 주소·전화번호 처리에도 쓰인다. (트라이는 교재마다 구현이 조금씩 다르다 - 이 책은 가장 이해하기 쉬운 구현을 택했다.)

## 2. 트라이의 구조

트라이는 이진 트리가 아니다 - **자식 수에 제한이 없다**. 이 구현에서 각 노드는 **해시 테이블**을 가지며, 키는 알파벳 문자, 값은 자식 트라이 노드다.

```typescript
class TrieNode {
  children: Record<string, TrieNode | null> = {};
}

class Trie {
  root = new TrieNode();
}
```

**단어 저장 방식**: "ace"는 루트 → "a" 키 → "c" 키 → "e" 키의 노드 사슬로 저장된다. "act"를 추가하면 기존 "a"→"c"는 **공유**하고 "t"만 새로 단다 - 접두사를 공유하는 단어들이 경로를 공유하는 것이 트라이의 본질이다.

**별표(`*`) 키의 필요성**: 각 단어의 마지막 문자 노드에는 `"*"` 키(값은 null)를 추가해 "여기서 단어가 끝난다"를 표시한다. "bat"과 "batter"처럼 **한 단어가 다른 단어의 접두사**일 때 필수적이다 - 첫 "t" 노드가 `{"*", "t"}` 두 키를 가져 "bat 자체도 단어이고, 이어지는 단어도 있다"를 동시에 표현한다.

## 3. 트라이 검색 - O(K)

접두사 검색(완전한 단어 검색을 포함하는 더 일반적인 연산):

1. `currentNode` = 루트
2. 검색 문자열의 각 문자에 대해: currentNode의 자식에 그 문자 키가 있으면 따라가고, 없으면 None 반환(트라이에 없음)
3. 문자열을 끝까지 순회하면 찾은 것

```typescript
search(word: string): TrieNode | null {
  let currentNode = this.root;
  for (const char of word) {
    if (currentNode.children[char]) {
      currentNode = currentNode.children[char]!;
    } else {
      return null;  // 접두사가 트라이에 없다
    }
  }
  return currentNode;  // (true 대신 노드를 반환 - 자동 완성에 쓰기 위해)
}
```

> **핵심 통찰**: 각 문자마다 해시 테이블 룩업 1번(O(1))이므로 단계 수 = **검색 문자열의 문자 수**. 이를 **O(K)**(K = 검색 문자열 길이)라 표기한다. O(K)는 상수는 아니지만 결정적인 미덕이 있다 - **트라이(데이터)가 아무리 커져도 검색 속도가 변하지 않는다.** 속도를 좌우하는 건 전체 데이터가 아니라 입력의 크기뿐이다. "cat"은 사전이 백만 단어여도 3단계다.

## 4. 트라이 삽입 - O(K)

검색과 거의 같다. 문자를 따라가다 **자식이 없으면 새 노드를 만들어** 잇고, 끝나면 `"*"`를 단다:

```typescript
insert(word: string): void {
  let currentNode = this.root;
  for (const char of word) {
    if (currentNode.children[char]) {
      currentNode = currentNode.children[char]!;
    } else {
      const newNode = new TrieNode();   // 없는 문자는 새 노드로
      currentNode.children[char] = newNode;
      currentNode = newNode;
    }
  }
  currentNode.children["*"] = null;     // 단어의 끝 표시
}
```

정확히는 K+1단계지만 상수를 버려 **O(K)**다.

## 5. 자동 완성 개발

### 5.1 단어 수집 - collectAllWords

어떤 노드에서 시작해 그 아래의 모든 완전한 단어를 배열로 모으는 재귀 메서드:

```typescript
collectAllWords(
  node: TrieNode | null = null,
  word = "",
  words: string[] = [],
): string[] {
  const currentNode = node ?? this.root;
  for (const [key, childNode] of Object.entries(currentNode.children)) {
    if (key === "*") {
      words.push(word);         // 기저 조건: 완전한 단어 발견
    } else {
      // 문자를 이어 붙이며 자식으로 재귀
      this.collectAllWords(childNode!, word + key, words);
    }
  }
  return words;
}
```

재귀 포인트 두 가지 (Ch12의 메모이제이션과 같은 원리):

- **배열(words)은 메모리에서 같은 객체**라 호출 스택 위아래로 전달되며 계속 누적된다
- **문자열(word)은 수정 시 새 객체**가 생기므로, 호출 스택을 되감아 올라가면 이전 호출의 원래 문자열("ca")이 그대로 남아 있다 - 그래서 "can"을 수집한 뒤 "cat" 분기를 탐색할 수 있다

### 5.2 autocomplete = search + collectAllWords

```typescript
autocomplete(prefix: string): string[] | null {
  const currentNode = this.search(prefix);   // 접두사의 마지막 노드 찾기
  if (!currentNode) {
    return null;
  }
  return this.collectAllWords(currentNode, prefix);  // 그 아래 모든 단어 수집
}
```

search가 true가 아니라 **노드를 반환하도록 설계한 이유**가 여기 있다 - 접두사의 끝 노드에서 수집을 시작해, 접두사에 이어 붙는 모든 완전한 단어를 돌려준다.

## 6. 값을 포함하는 트라이 - 자동 완성 업그레이드

후보 16개를 다 보여주는 것은 과하다 - **많이 쓰이는 단어**만 추리는 게 낫다. `"*"` 키의 값을 null 대신 **단어 인기도**(예: 1~10)로 쓰면 된다: `{"*": 10}`(ball), `{"*": 9}`(balance), `{"*": 1}`(balter). 단어를 수집할 때 점수를 함께 모아 인기도순으로 정렬해 상위만 표시한다 - 트라이를 아주 조금만 수정해 얻는 기능이다.

---

## 요약

- 트라이 = **문자 하나가 노드 하나**인 트리. 각 노드는 해시 테이블(문자 → 자식)이고 자식 수 제한이 없다
- 접두사를 공유하는 단어들이 **경로를 공유**하고, `"*"` 키가 단어의 끝을 표시한다 (bat ⊂ batter 문제 해결)
- 검색·삽입 모두 **O(K)** (K = 문자열 길이) - 데이터가 커져도 속도가 불변이라는 점에서 사실상 상수처럼 동작
- **자동 완성 = search(접두사 끝 노드 찾기) + collectAllWords(그 아래 단어 재귀 수집)**
- `"*"`의 값에 인기도를 저장하면 인기순 추천으로 업그레이드된다
- 재귀 수집에서 배열은 공유되고 문자열은 호출별로 보존된다 - 호출 스택을 통한 상태 전달의 좋은 사례

## 연습 문제 (해답 예시)

1. **그림의 트라이에 저장된 단어 나열** - 경로를 따라 `"*"`를 만날 때마다 단어가 완성된다: tag, tan, tank, tap, today, total, we, well, went, wend, wet.
2. **"get", "go", "got", "gotten", "hall", "ham", "hammer", "hill", "zebra" 트라이 그리기** - 루트에 g, h, z 세 자식. g 아래 e-t(*)와 o(* - "go"도 단어) → o 아래 t(* - "got") → t 아래 t-e-n(*) ("gotten"). h 아래 a와 i: a 아래 l-l(*)과 m(*) → m 아래 m-e-r(*) ("hammer"), i 아래 l-l(*). z 아래 e-b-r-a(*).
3. **모든 키를 출력하는 순회 함수** - collectAllWords와 같은 골격으로, 각 자식의 key를 출력하고 자식 노드에 재귀한다:

   ```typescript
   traverse(node: TrieNode = this.root): void {
     for (const [key, childNode] of Object.entries(node.children)) {
       console.log(key);
       if (key !== "*") {
         this.traverse(childNode!);
       }
     }
   }
   ```

4. **autocorrect(가장 긴 공유 접두사의 단어 반환)** - 사용자 문자열의 문자를 따라가며 **갈 수 있는 데까지** 전진하고(경로 = 최장 공유 접두사), 막힌 지점부터는 collectAllWords로 아무 단어나 하나 완성해 `접두사 + 나머지`를 반환한다. 사용자 문자열이 트라이에 그대로 있으면(중간에 안 막히면) 입력을 그대로 반환한다.

## 다른 챕터와의 관계

- **Ch8 (해시 테이블)**: 트라이의 각 노드가 해시 테이블 - O(1) 자식 룩업이 O(K)의 기반이다
- **Ch15 (BST)·Ch16 (힙)**: 트리 3부작의 완결 - 검색 전문(BST), 최댓값 전문(힙), 접두사 전문(트라이)로 각자 특화가 다르다
- **Ch10~11 (재귀)**: collectAllWords는 "임의 깊이 순회 + 호출 스택으로 상태 전달"의 종합 연습이다
- **Ch18 (그래프)**: 자식 수 제한이 없는 노드 연결 구조가 그래프로 일반화된다
