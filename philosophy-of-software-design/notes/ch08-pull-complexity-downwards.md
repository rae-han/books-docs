# Chapter 8: Pull Complexity Downwards (복잡성을 아래로 끌어내려라)

## 핵심 질문

복잡성이 반드시 어딘가에 존재해야 한다면, 모듈의 인터페이스와 구현 중 어디에 두는 것이 나은가?

---

## 1. 핵심 원칙

> **모듈의 인터페이스가 단순한 것이 구현이 단순한 것보다 더 중요하다.**

복잡성이 어딘가에 존재해야 한다면, 모듈의 **구현(아래)** 에 두는 것이 **인터페이스(위)** 에 두는 것보다 낫다.

이유는 간단하다:
- **구현의 복잡성**: 모듈 개발자 한 명이 한 번 감당한다
- **인터페이스의 복잡성**: 모듈을 사용하는 모든 개발자가 매번 감당한다

```
인터페이스에 복잡성이 있으면:
  → N명의 개발자 × M번의 사용 = N×M번의 고통

구현에 복잡성이 있으면:
  → 1명의 개발자 × 1번의 구현 = 1번의 고통
```

---

## 2. 대표적 위반: 설정 파라미터 (Configuration Parameters)

### 2.1 설정 파라미터는 복잡성을 위로 밀어올린다

설정 파라미터는 복잡성을 **끌어내리는** 것이 아니라 **밀어올리는** 대표적인 패턴이다.

```python
# 나쁜 예: 복잡성을 사용자에게 전가
class ConnectionPool:
    def __init__(self,
                 max_connections=10,     # 몇 개가 적절한가?
                 min_idle=2,             # idle은 뭔가?
                 max_idle=5,             # 왜 min과 max가 따로 있나?
                 idle_timeout=300,       # 초? 밀리초?
                 connection_timeout=30,  # 이것과 idle_timeout의 차이는?
                 retry_count=3,          # 실패 시 몇 번?
                 retry_delay=1.0):       # 지수 백오프?
        ...
```

대부분의 사용자는 이 값들의 적절한 설정을 모른다. 모듈 개발자조차 모를 수 있다. 결과적으로:
- 사용자는 기본값을 그대로 사용하거나 (설정이 무의미)
- 잘못된 값을 설정하거나 (버그 유발)
- 올바른 값을 찾기 위해 많은 시간을 소비한다 (인지 부하)

```python
# 좋은 예: 복잡성을 내부로 끌어내림
class ConnectionPool:
    def __init__(self, database_url):
        # 내부적으로 합리적인 값을 자동 결정
        # - 가용 메모리와 CPU 기반으로 pool 크기 산정
        # - 부하에 따라 동적으로 조정
        # - 타임아웃은 네트워크 특성에 맞게 자동 설정
        ...
```

### 2.2 설정이 필요한 경우

물론 설정 파라미터가 필요한 경우도 있다. 하지만 이 경우에도:

- **합리적인 기본값을 반드시 제공**한다
- 설정은 **선택적**으로 만든다
- 가능하면 모듈이 **자동으로 최적 값을 계산**하도록 한다

> **핵심 통찰**: 설정 파라미터를 추가하기 전에 항상 물어라 — "모듈이 이 값을 스스로 결정할 수 있는가?" 대부분의 경우 답은 "예"다.

---

## 3. 예시: 에러 처리의 위치

### 3.1 에러를 위로 던지는 방식 (나쁜 예)

```python
# 복잡성을 위로 밀어올리는 방식
class FileProcessor:
    def read_file(self, path):
        # 모든 에러를 호출자에게 떠넘김
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        if not os.access(path, os.R_OK):
            raise PermissionError(path)
        if os.path.getsize(path) > MAX_SIZE:
            raise FileTooLargeError(path)
        if self._is_locked(path):
            raise FileLockError(path)
        return open(path).read()

# 호출자는 이 모든 에러를 처리해야 한다
try:
    data = processor.read_file("config.json")
except FileNotFoundError:
    ...
except PermissionError:
    ...
except FileTooLargeError:
    ...
except FileLockError:
    ...
```

### 3.2 에러를 내부에서 처리하는 방식 (좋은 예)

```python
# 복잡성을 아래로 끌어내리는 방식
class FileProcessor:
    def read_file(self, path, default=None):
        """파일을 읽어 내용을 반환한다.
        파일을 읽을 수 없는 경우 default를 반환한다."""
        try:
            return open(path).read()
        except (FileNotFoundError, PermissionError, OSError):
            if default is not None:
                return default
            raise  # default가 없으면 그때 던진다

# 호출자의 코드가 훨씬 단순해진다
data = processor.read_file("config.json", default="{}")
```

---

## 4. 트레이드오프와 한계

### 4.1 언제 복잡성을 아래로 끌어내려야 하는가

- 하위 모듈이 복잡성을 처리할 **충분한 정보와 맥락**을 가지고 있을 때
- 복잡성을 내부에서 처리해도 **정보 누출이 발생하지 않을 때**
- 구현이 복잡해지더라도 **인터페이스가 크게 단순해질 때**

### 4.2 언제 끌어내리면 안 되는가

- 하위 모듈이 올바른 결정을 내릴 **맥락이 부족할 때**
- 끌어내리면 **정보 누출**이 발생할 때 (상위 계층의 지식이 하위로 새어들어감)
- 구현이 지나치게 복잡해져서 오히려 **전체 복잡성이 증가**할 때

```java
// 끌어내리면 안 되는 경우: 모듈이 결정할 맥락이 없다
class Logger {
    // 로그 레벨을 모듈이 자동 결정? → 불가능
    // 어떤 메시지가 DEBUG이고 어떤 것이 ERROR인지는
    // 호출자만 알 수 있다
    public void log(String message) {
        // 자동으로 레벨 결정? 불가능!
    }

    // 이 경우는 호출자가 결정하는 것이 맞다
    public void log(Level level, String message) { ... }
}
```

### 4.3 판단 기준

> **핵심 통찰**: "이 복잡성을 누가 처리하는 것이 전체 시스템에 가장 이득인가?"를 기준으로 판단한다. 대부분의 경우, 모듈 내부에서 처리하는 것이 이득이다. 하지만 모듈이 충분한 맥락을 갖지 못할 때는 예외다.

---

## 5. 복잡성의 공식과의 연결

Chapter 2의 복잡성 공식 `C = Σ(cp × tp)`를 떠올려 보자:

- **인터페이스의 복잡성**: 모듈을 사용하는 모든 곳에서 tp가 높다 → cp × tp가 크다
- **구현의 복잡성**: 모듈 내부에서만 tp가 높고, 외부에서는 0이다 → 전체 기여가 작다

따라서 같은 양의 복잡성이라면 **구현에 두는 것이 전체 복잡성을 더 낮춘다**.

---

## 요약

- 복잡성이 어딘가에 존재해야 한다면, 인터페이스(위)가 아닌 **구현(아래)에 두라**.
- 모듈의 **인터페이스가 단순한 것**이 구현이 단순한 것보다 더 중요하다.
- **설정 파라미터**는 복잡성을 위로 밀어올리는 대표적 패턴이다. 가능하면 모듈이 자동으로 결정하게 하라.
- 에러 처리를 모듈 내부에서 흡수하면 호출자의 코드가 단순해진다.
- 단, 모듈이 결정할 **충분한 맥락이 없는 경우**에는 끌어내리면 안 된다.
- 판단 기준: "누가 처리하는 것이 **전체 시스템**에 가장 이득인가?"

---

## 다음 챕터와의 연결

Chapter 9 **"Better Together Or Better Apart? (합치는 게 나은가, 분리하는 게 나은가?)"** 에서는 두 기능을 하나의 모듈에 합칠지 별도 모듈로 분리할지 결정하는 기준을 다룬다. 정보 공유, 함께 사용되는 빈도, 개념적 겹침 등의 기준으로 전체 복잡성을 최소화하는 선택을 한다.
