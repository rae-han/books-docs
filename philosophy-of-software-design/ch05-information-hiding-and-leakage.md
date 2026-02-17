# Chapter 5: Information Hiding and Leakage (정보 은닉과 정보 누출)

## 핵심 질문

깊은 모듈을 만드는 가장 중요한 기법은 무엇인가? 그리고 이 기법이 실패하는 흔한 형태는 무엇인가?

---

## 1. 정보 은닉 (Information Hiding)

### 1.1 정의와 역사

**정보 은닉(Information Hiding)** 은 1971년 David Parnas가 제안한 개념으로, 소프트웨어 설계에서 가장 중요한 기법 중 하나다.

> 각 모듈은 설계 결정(design decision)을 자신의 내부에 캡슐화해야 한다. 이 결정은 모듈의 인터페이스에 드러나지 않아야 하며, 다른 모듈은 이 결정에 대해 알 필요가 없어야 한다.

### 1.2 무엇을 숨기는가

"정보"란 단순히 데이터만을 의미하지 않는다. 모듈이 숨길 수 있는 정보의 종류:

| 숨길 수 있는 정보 | 예시 |
|-----------------|------|
| **데이터 구조** | 내부적으로 B-tree를 사용하는지, 해시맵을 사용하는지 |
| **알고리즘** | 정렬에 quicksort를 사용하는지, mergesort를 사용하는지 |
| **하위 수준 메커니즘** | 네트워크 프로토콜의 세부 사항, 파일 형식 |
| **설계 결정** | 왜 이 방식을 선택했는지, 어떤 트레이드오프가 있었는지 |

### 1.3 정보 은닉이 깊은 모듈을 만든다

정보 은닉과 깊은 모듈(Chapter 4)의 관계는 직접적이다:

```
숨기는 정보가 많을수록
  → 인터페이스가 단순해지고
    → 모듈이 깊어지고
      → 복잡성이 줄어든다
```

```python
# 깊은 모듈: 많은 정보를 숨김
class Database:
    """데이터베이스 접근을 제공한다."""

    def query(self, sql: str) -> list[dict]:
        """SQL 쿼리를 실행하고 결과를 반환한다."""
        # 숨겨진 정보:
        # - 커넥션 풀링 방식
        # - 쿼리 캐싱 전략
        # - 타임아웃 및 재시도 로직
        # - 결과 직렬화/역직렬화 방식
        # - 데이터베이스 드라이버 종류
        ...
```

호출자는 `query(sql)`만 알면 된다. 커넥션 풀링, 캐싱, 재시도 등의 복잡성은 모두 모듈 내부에 숨겨져 있다.

### 1.4 private ≠ 정보 은닉

정보 은닉은 단순히 필드를 `private`으로 선언하는 것이 아니다:

```java
// private이지만 정보가 은닉되지 않은 경우
public class UserProfile {
    private String firstName;  // private이지만...
    private String lastName;

    // getter/setter가 모든 내부 구조를 노출한다
    public String getFirstName() { return firstName; }
    public void setFirstName(String name) { this.firstName = name; }
    public String getLastName() { return lastName; }
    public void setLastName(String name) { this.lastName = name; }
}
// 호출자는 내부에 firstName, lastName이 별도 필드로 존재한다는 것을 알고 있다
// 이것은 정보 은닉이 아니다
```

진정한 정보 은닉:

```java
// 진정한 정보 은닉
public class UserProfile {
    // 내부 표현은 완전히 숨겨져 있음
    // Map일 수도, 단일 문자열일 수도, DB 레코드 참조일 수도 있음

    public String getDisplayName() {
        // 호출자는 이름이 내부적으로 어떻게 저장되는지 모른다
        // first+last일 수도, 단일 필드일 수도, 지역에 따라 다를 수도
        ...
    }
}
```

---

## 2. 정보 누출 (Information Leakage)

### 2.1 정의

> 🚩 **Red Flag: Information Leakage**
>
> **정보 누출(Information Leakage)은 같은 설계 결정이 여러 모듈에 반영되어 있는 상황이다.** 이 설계 결정이 변경되면 관련된 모든 모듈을 수정해야 하므로, 모듈 간 의존성이 생긴다.

### 2.2 예시: 파일 형식의 누출

```python
# 나쁜 설계: JSON 형식 지식이 두 클래스에 분산
class ConfigReader:
    def read(self, path):
        with open(path) as f:
            data = json.load(f)  # JSON임을 알고 있음
        # JSON 특정 키 구조도 알고 있음
        return {
            "host": data["server"]["host"],
            "port": data["server"]["port"],
        }

class ConfigWriter:
    def write(self, path, config):
        data = {
            "server": {  # 같은 키 구조를 알고 있음
                "host": config["host"],
                "port": config["port"],
            }
        }
        with open(path, 'w') as f:
            json.dump(data, f)  # JSON임을 알고 있음
```

문제: JSON을 YAML로 바꾸면 **두 클래스 모두** 수정해야 한다. 키 구조가 바뀌어도 **두 클래스 모두** 수정해야 한다.

```python
# 좋은 설계: 파일 형식 지식을 하나의 클래스에 캡슐화
class ConfigStore:
    """설정 파일의 읽기/쓰기를 담당한다.
    파일 형식(현재 JSON)은 이 클래스 내부에 캡슐화되어 있다."""

    def read(self, path) -> dict:
        with open(path) as f:
            data = json.load(f)
        return self._parse(data)

    def write(self, path, config: dict):
        data = self._serialize(config)
        with open(path, 'w') as f:
            json.dump(data, f)

    def _parse(self, raw_data):
        # 파일 구조 → 앱 구조 변환 (한 곳에서만 관리)
        return {
            "host": raw_data["server"]["host"],
            "port": raw_data["server"]["port"],
        }

    def _serialize(self, config):
        # 앱 구조 → 파일 구조 변환 (한 곳에서만 관리)
        return {"server": {"host": config["host"], "port": config["port"]}}
```

이제 파일 형식을 변경하더라도 `ConfigStore` 한 곳만 수정하면 된다.

---

## 3. 시간적 분해 (Temporal Decomposition)

> 🚩 **Red Flag: Temporal Decomposition**
>
> **시간적 분해는 실행 순서를 기준으로 모듈을 나누는 것이다.** "먼저 읽고, 그 다음 처리하고, 마지막에 쓴다"는 순서에 따라 읽기 모듈, 처리 모듈, 쓰기 모듈을 만들면, 데이터 형식에 대한 지식이 읽기 모듈과 쓰기 모듈에 분산된다.

### 3.1 예시: HTTP 요청 처리

나쁜 설계 (시간적 분해):

```java
// 1단계: 바이트를 읽는 클래스
class HttpRequestReader {
    byte[] readRawBytes(Socket socket) { ... }
}

// 2단계: 헤더를 파싱하는 클래스
class HttpHeaderParser {
    Map<String, String> parseHeaders(byte[] raw) { ... }
}

// 3단계: 바디를 읽는 클래스
class HttpBodyReader {
    byte[] readBody(Socket socket, Map<String, String> headers) { ... }
}
```

문제: HTTP 프로토콜에 대한 지식(헤더 형식, Content-Length 처리, 청크 인코딩 등)이 세 클래스에 분산되어 있다.

좋은 설계:

```java
// HTTP 프로토콜 지식을 하나의 클래스에 캡슐화
class HttpRequest {
    private String method;
    private String path;
    private Map<String, String> headers;
    private byte[] body;

    public static HttpRequest parse(Socket socket) {
        // HTTP 프로토콜의 모든 세부사항을 여기서 처리
        // - 바이트 읽기
        // - 헤더 파싱
        // - Content-Length 기반 바디 읽기
        // - 청크 인코딩 처리
        // 모든 HTTP 프로토콜 지식이 이 한 클래스에 있다
        ...
    }

    public String getMethod() { return method; }
    public String getPath() { return path; }
    public String getHeader(String name) { return headers.get(name); }
    public byte[] getBody() { return body; }
}
```

### 3.2 핵심 원칙

> **모듈을 나누는 기준은 "언제 실행되는가"가 아니라 "어떤 정보를 캡슐화하는가"여야 한다.**

---

## 4. 과도한 노출 (Overexposure)

> 🚩 **Red Flag: Overexposure**
>
> **흔히 사용되는 기능의 API가 드물게 사용되는 기능에 대한 지식을 요구한다면, 이는 불필요하게 인지 부하를 높인다.**

```java
// 나쁜 예: 단순한 파일 읽기에 버퍼 크기를 지정해야 함
InputStream stream = new FileInputStream("data.txt");
BufferedInputStream buffered = new BufferedInputStream(stream, 8192);
// 대부분의 사용자는 8192가 적절한지 알 수 없다

// 좋은 예: 합리적인 기본값 제공
InputStream stream = openFile("data.txt");
// 내부적으로 버퍼링이 적용되며, 기본 버퍼 크기는 모듈이 결정
```

---

## 5. 정보 공유가 적절한 경우

정보 은닉이 항상 옳은 것은 아니다. 정보를 공유하는 것이 적절한 경우:

- **공통 상수**: 시스템 전체에서 사용되는 상수(예: HTTP 상태 코드)
- **공통 데이터 구조**: 여러 모듈이 공유하는 도메인 객체
- **인터페이스 계약**: 모듈 간 계약(contract)으로 명시적으로 정의된 정보

핵심 질문: **"이 정보가 변경될 가능성이 있는 설계 결정인가, 아니면 시스템의 근본적 속성인가?"**

- 변경 가능한 설계 결정 → **숨겨야 한다**
- 시스템의 근본적 속성 → **공유해도 된다**

---

## 6. 정보 은닉과 깊은 모듈의 관계

```
정보 은닉은 깊은 모듈을 만드는 핵심 메커니즘이다

┌─────────────────────────────────┐
│  Information Hiding (원인)        │
│  → 설계 결정을 모듈 내부에 숨긴다    │
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│  Deep Module (결과)               │
│  → 단순한 인터페이스, 강력한 기능     │
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│  Reduced Complexity (효과)        │
│  → 개발자가 한 번에 다뤄야 할        │
│    복잡성이 줄어든다                 │
└─────────────────────────────────┘
```

> **핵심 통찰**: 새로운 모듈이나 클래스를 설계할 때 가장 먼저 물어야 할 질문은 "이 모듈이 숨길 수 있는 정보는 무엇인가?"이다. 숨길 수 있는 정보가 많을수록 깊은 모듈이 되고, 시스템의 복잡성이 줄어든다.

---

## 요약

- **정보 은닉**은 설계 결정을 모듈 내부에 캡슐화하는 기법으로, 깊은 모듈을 만드는 핵심 메커니즘이다.
- 숨기는 대상은 데이터뿐 아니라 **알고리즘, 메커니즘, 설계 결정** 등 모든 종류의 정보를 포함한다.
- **정보 누출**은 같은 설계 결정이 여러 모듈에 분산된 상황으로, 모듈 간 의존성을 만든다.
- **시간적 분해**는 실행 순서를 기준으로 모듈을 나누어 정보가 분산되는 흔한 실수다.
- **과도한 노출**은 일반적인 사용 사례에 불필요한 세부사항을 노출하는 것이다.
- `private` 키워드는 정보 은닉의 필요 조건일 뿐 충분 조건이 아니다.
- 모듈 설계 시 "이 모듈이 숨길 수 있는 정보는 무엇인가?"를 먼저 물어라.

---

## Red Flags

- 🚩 **Information Leakage**: 같은 설계 결정이 여러 모듈에 반영됨
- 🚩 **Temporal Decomposition**: 실행 순서 기준으로 모듈을 나누어 정보가 분산됨
- 🚩 **Overexposure**: 일반적 사용에 불필요한 세부사항이 API에 노출됨

---

## 다음 챕터와의 연결

Chapter 6 **"General-Purpose Modules are Deeper (범용 모듈이 더 깊다)"** 에서는 모듈을 설계할 때 범용적(general-purpose)으로 만드는 것이 왜 더 깊은 모듈로 이끄는지, 그리고 범용성과 특수성 사이의 적절한 균형을 어떻게 찾는지를 다룬다.
