# Chapter 6: General-Purpose Modules are Deeper (범용 모듈이 더 깊다)

## 핵심 질문

모듈을 설계할 때 범용적(general-purpose)으로 만들어야 하는가, 특수 목적(special-purpose)으로 만들어야 하는가? 이 둘의 적절한 균형점은 어디인가?

---

## 1. 범용 vs 특수 목적의 딜레마

새로운 클래스를 설계할 때 흔히 마주치는 질문:

- "현재 필요한 것만 딱 맞게 만들까?" (특수 목적)
- "미래의 사용도 고려해서 넓게 만들까?" (범용)

Ousterhout의 답:

> **"somewhat general-purpose"** — 기능은 현재 필요에 맞추되, **인터페이스는 범용적으로** 설계하라.

---

## 2. Ousterhout의 Sweet Spot

### 2.1 핵심 원칙

- **기능(Implementation)**: 현재 필요한 것만 구현한다. 아직 필요하지 않은 기능을 미리 만들지 않는다 (YAGNI).
- **인터페이스(Interface)**: 현재뿐 아니라 미래의 사용 사례도 자연스럽게 지원하도록 범용적으로 설계한다.

이것이 **"somewhat general-purpose"** 의 의미다. 구현은 현재에 집중하되, 인터페이스는 미래를 고려한다.

### 2.2 예시: 텍스트 에디터 버퍼

GUI 텍스트 에디터를 만든다고 하자. 텍스트를 저장하고 편집하는 버퍼 클래스가 필요하다.

**특수 목적 설계 (나쁜 예)**:

```java
public class TextBuffer {
    // UI 동작에 맞춘 특수 목적 메서드들
    public void backspace() { ... }
    public void deleteSelection(int start, int end) { ... }
    public void typeCharacter(char c) { ... }
    public void insertNewline() { ... }
    public void pasteFromClipboard(String text) { ... }
    public void cutSelection(int start, int end) { ... }
}
```

문제점:
- 메서드 수가 많다 → 인터페이스가 복잡하다
- UI 개념("backspace", "clipboard")이 하위 모듈에 침투했다 (정보 누출)
- 새로운 UI 동작이 추가될 때마다 버퍼에 메서드를 추가해야 한다
- 각 메서드가 얕다 (예: `backspace()`는 그냥 `delete(cursor-1, cursor)`)

**범용 설계 (좋은 예)**:

```java
public class TextBuffer {
    // 범용적인 두 가지 기본 연산만 제공
    public void insert(int position, String text) { ... }
    public void delete(int start, int end) { ... }
    public String getText(int start, int end) { ... }
    public int length() { ... }
}
```

이 인터페이스로 모든 UI 동작을 구현할 수 있다:

```java
// backspace = 커서 앞 한 글자 삭제
buffer.delete(cursor - 1, cursor);

// 선택 영역 삭제
buffer.delete(selectionStart, selectionEnd);

// 문자 입력
buffer.insert(cursor, String.valueOf(c));

// 줄바꿈
buffer.insert(cursor, "\n");

// 붙여넣기
buffer.insert(cursor, clipboardText);
```

### 2.3 범용 설계의 장점

| 비교 항목 | 특수 목적 설계 | 범용 설계 |
|----------|-------------|----------|
| 메서드 수 | 6개 이상 | 3~4개 |
| 인터페이스 복잡성 | 높음 | **낮음** |
| UI 변경 시 버퍼 수정 필요? | 예 | **아니오** |
| 다른 용도로 재사용 가능? | 아니오 | **예** |
| 각 메서드의 깊이 | 얕음 | **깊음** |

---

## 3. 자문해야 할 질문들

모듈의 인터페이스를 설계할 때 다음 질문으로 범용성을 점검한다:

### 3.1 "이 메서드가 사용될 상황은 몇 가지인가?"

```java
// 딱 한 가지 상황에서만 사용 → 너무 특수적
public void handleBackspaceKeyPress() { ... }

// 다양한 상황에서 사용 가능 → 적절히 범용적
public void delete(int start, int end) { ... }
```

메서드가 딱 한 가지 상황에서만 사용된다면, 너무 특수적일 가능성이 높다.

### 3.2 "현재 필요를 충족하는 가장 단순한 인터페이스는 무엇인가?"

```python
# 불필요하게 복잡한 인터페이스
def save_user(user, format="json", compress=False,
              encrypt=False, backup=True):
    ...

# 현재 필요에 충분한 단순한 인터페이스
def save_user(user):
    ...
```

범용적이라고 해서 인터페이스가 복잡해져야 하는 것은 아니다. 오히려 **범용적인 인터페이스가 더 단순한 경우가 많다**.

### 3.3 "이 API는 현재 필요에 사용하기 쉬운가?"

범용적 설계가 현재 사용을 불편하게 만든다면 너무 나간 것이다. 범용성과 사용 편의성은 양립해야 한다.

---

## 4. 특수화를 상위 계층으로 밀어 올려라

> **핵심 통찰**: 범용 코드는 하위 계층에, 특수 목적 코드는 상위 계층에 두어라.

```
┌──────────────────────────────────┐
│  UI Layer (특수 목적)              │
│  - backspace = delete(cur-1, cur) │
│  - paste = insert(cur, clipboard) │
├──────────────────────────────────┤
│  TextBuffer (범용)                │
│  - insert(position, text)         │
│  - delete(start, end)             │
└──────────────────────────────────┘
```

하위 모듈(TextBuffer)은 UI 개념을 모른다. 상위 모듈(UI Layer)이 범용 연산을 조합하여 특수한 동작을 구현한다. 이렇게 하면:

- 하위 모듈이 깊어진다 (범용적 → 적은 메서드, 많은 기능)
- 하위 모듈이 변경에 강해진다 (UI가 바뀌어도 버퍼는 그대로)
- 하위 모듈이 재사용 가능해진다

---

## 5. 주의사항: 과도한 범용성

범용성을 너무 추구하면 오히려 문제가 된다:

- **사용하지 않을 기능을 미리 구현**: YAGNI 위반. 기능은 현재 필요에 맞추어라.
- **인터페이스가 오히려 복잡해짐**: 범용적이라고 파라미터를 잔뜩 추가하면 역효과.
- **현재 사용이 불편해짐**: 범용성을 위해 현재의 일반적 사용 사례가 복잡해지면 안 된다.

적절한 균형:
- **인터페이스**: 범용적으로 (미래의 변경에 안정적)
- **구현**: 현재 필요에 맞게 (불필요한 기능을 미리 만들지 않기)

---

## 요약

- 모듈 설계 시 **"somewhat general-purpose"** 접근을 취하라: 기능은 현재에, 인터페이스는 미래에 맞춘다.
- 범용 모듈이 더 **깊다**: 적은 수의 강력한 메서드로 다양한 사용을 지원한다.
- 특수 목적 메서드는 **얕다**: UI 동작 하나에 메서드 하나를 만들면 인터페이스만 복잡해진다.
- 범용 코드는 **하위 계층**에, 특수 목적 코드는 **상위 계층**에 둔다.
- 자문: "이 메서드는 몇 가지 상황에서 사용되는가?" — 하나뿐이면 너무 특수적이다.
- 과도한 범용성도 해롭다. 인터페이스는 단순하게 유지하면서 범용적이어야 한다.

---

## 다음 챕터와의 연결

Chapter 7 **"Different Layer, Different Abstraction (계층이 다르면 추상화도 달라야 한다)"** 에서는 소프트웨어 계층 간의 관계를 다룬다. 인접한 계층이 비슷한 추상화를 가지면 설계 문제의 신호이며, 대표적인 예가 **통과 메서드(Pass-Through Method)** 와 **데코레이터** 남용이다.
