# Chapter 10: Define Errors Out Of Existence (에러를 정의 밖으로 내보내라)

## 핵심 질문

예외 처리가 왜 소프트웨어 복잡성의 주요 원인이 되는가? 예외의 수를 근본적으로 줄이는 설계 기법은 무엇인가?

---

## 1. 예외 처리는 복잡성의 주요 원인이다

### 1.1 왜 예외 처리가 어려운가

예외 처리 코드는 정상 경로(normal path) 코드보다 본질적으로 작성하기 어렵다:

- **재현이 어렵다**: 예외 상황은 드물게 발생하므로 테스트하기 어렵다
- **생각하기 어렵다**: 개발자는 정상 경로에 집중하고, 예외 경로는 소홀히 한다
- **전파된다**: 한 곳에서 던진 예외는 호출 체인을 따라 올라가며 각 계층에 복잡성을 추가한다

### 1.2 너무 많은 예외

프로그래머는 너무 많은 불필요한 예외를 정의하는 경향이 있다:

```java
// 과도한 예외 정의
public class UserService {
    public User findUser(String id) throws
        UserNotFoundException,
        DatabaseConnectionException,
        InvalidIdFormatException,
        CacheTimeoutException,
        DeserializationException {
        ...
    }
}

// 호출자는 5가지 예외를 모두 처리해야 한다
// 대부분의 호출자는 catch (Exception e)로 뭉뚱그린다
// → 예외를 세분화한 의미가 사라진다
```

> **핵심 통찰**: 클래스가 던지는 예외는 그 클래스 인터페이스의 일부다. 예외가 많을수록 인터페이스가 복잡해지고, 모듈이 얕아진다.

---

## 2. 에러를 정의 밖으로 내보내라

### 2.1 핵심 전략

> **예외를 처리하는 최선의 방법은 예외가 발생할 수 없도록 API를 재정의하는 것이다.**

"에러"로 취급하던 상황을 정상적인 동작으로 재정의하면, 예외 자체가 사라진다.

### 2.2 예시: 파일 삭제

**전통적 접근 (에러가 존재):**

```python
# 존재하지 않는 파일을 삭제하면 에러
import os

def delete_config(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config not found: {path}")
    os.remove(path)

# 호출자는 파일이 없는 경우를 처리해야 한다
try:
    delete_config("temp.conf")
except FileNotFoundError:
    pass  # 어차피 삭제하려던 거니까...
```

**재정의된 접근 (에러가 사라짐):**

```python
# "삭제"의 의미를 재정의: "파일이 존재하지 않는 상태를 보장"
def ensure_removed(path):
    """경로에 파일이 없는 상태를 보장한다.
    파일이 이미 없으면 아무 일도 하지 않는다."""
    try:
        os.remove(path)
    except FileNotFoundError:
        pass  # 이미 원하는 상태 — 에러가 아님

# 호출자는 에러를 신경 쓸 필요가 없다
ensure_removed("temp.conf")
```

핵심: `delete`의 의미를 "파일을 지워라"에서 **"파일이 없는 상태를 보장하라"** 로 바꿨다. 파일이 이미 없다면 원하는 상태가 이미 달성된 것이므로 에러가 아니다.

### 2.3 예시: 부분 문자열 추출

**전통적 접근:**

```java
// 인덱스가 범위를 벗어나면 예외
String s = "hello";
s.substring(3, 10);  // StringIndexOutOfBoundsException!

// 호출자는 매번 범위를 검사해야 한다
int end = Math.min(10, s.length());
String sub = s.substring(3, end);
```

**재정의된 접근:**

```python
# Python의 슬라이싱: 범위를 벗어나도 에러가 아님
s = "hello"
s[3:10]  # → "lo" (범위를 자동으로 조정)
s[10:20] # → ""  (완전히 범위 밖이면 빈 문자열)

# 호출자가 범위를 검사할 필요가 없다
```

### 2.4 예시: Unix vs Windows 파일 삭제

**Windows**: 열려 있는 파일은 삭제할 수 없다 → 에러 발생 → 호출자가 처리해야 함

**Unix**: `unlink()`는 디렉토리 항목만 제거하고, 파일 데이터는 마지막 참조가 닫힐 때 삭제된다 → 열려 있는 파일도 `unlink()` 가능 → 에러가 발생하지 않음

Unix의 접근이 더 깔끔하다. "삭제"의 의미를 **"디렉토리 항목 제거"** 로 정의함으로써 에러 상황을 제거했다.

---

## 3. 예외 마스킹 (Exception Masking)

### 3.1 개념

예외 마스킹은 **하위 계층에서 예외를 감지하고 처리하여, 상위 계층에는 전파하지 않는 기법**이다.

### 3.2 예시: TCP의 패킷 손실 처리

TCP는 네트워크에서 패킷이 손실되면 자동으로 재전송한다. 애플리케이션은 패킷 손실을 전혀 알지 못한다.

```
애플리케이션 계층:  send("Hello")  →  정상 전송 완료
                                     (패킷 손실을 모름)
     ┌───────────────────────────┐
TCP: │ 패킷 전송 → 손실 감지      │
     │ → 자동 재전송 → 성공       │
     │ (애플리케이션에 알리지 않음) │
     └───────────────────────────┘
```

만약 TCP가 패킷 손실을 예외로 던졌다면, 모든 네트워크 애플리케이션이 재전송 로직을 직접 구현해야 했을 것이다. TCP가 이 복잡성을 **마스킹**함으로써 상위 계층이 단순해진다.

### 3.3 예시: NFS 클라이언트

NFS 클라이언트는 서버가 일시적으로 응답하지 않으면 자동으로 재시도한다. 애플리케이션은 네트워크 장애를 인지하지 못한다.

> **핵심 통찰**: 예외 마스킹은 "복잡성을 아래로 끌어내리기"(Ch 8)의 구체적 적용이다. 하위 모듈이 예외를 내부에서 처리하면, 상위 모듈의 인터페이스가 단순해진다.

---

## 4. 예외 집약 (Exception Aggregation)

### 4.1 개념

예외 집약은 **여러 예외를 한 곳에서 일괄 처리**하는 기법이다. 각 예외마다 개별 핸들러를 두는 대신, 상위 계층에서 하나의 핸들러로 모든 예외를 처리한다.

### 4.2 예시: 웹 서버

```python
# 나쁜 예: 각 핸들러에서 개별적으로 예외 처리
class UserHandler:
    def handle(self, request):
        try:
            user = self.find_user(request.user_id)
            return Response(200, user.to_json())
        except UserNotFoundError:
            return Response(404, "User not found")
        except DatabaseError:
            return Response(500, "Database error")
        except ValidationError as e:
            return Response(400, str(e))

class OrderHandler:
    def handle(self, request):
        try:
            order = self.create_order(request.data)
            return Response(201, order.to_json())
        except OrderValidationError:
            return Response(400, "Invalid order")
        except DatabaseError:
            return Response(500, "Database error")
        except InsufficientStockError:
            return Response(409, "Out of stock")
```

```python
# 좋은 예: 디스패처에서 예외를 일괄 처리
class WebServer:
    def dispatch(self, request):
        try:
            handler = self.find_handler(request.path)
            return handler.handle(request)
        except NotFoundError:
            return Response(404, "Not found")
        except ValidationError as e:
            return Response(400, str(e))
        except ConflictError as e:
            return Response(409, str(e))
        except Exception:
            return Response(500, "Internal error")

# 개별 핸들러는 예외를 그냥 던지면 된다
class UserHandler:
    def handle(self, request):
        user = self.find_user(request.user_id)  # NotFoundError 가능
        return Response(200, user.to_json())

class OrderHandler:
    def handle(self, request):
        order = self.create_order(request.data)  # ValidationError 가능
        return Response(201, order.to_json())
```

### 4.3 "예외는 발생 지점에서 가까운 곳에서 처리하라"에 대한 반론

전통적 조언은 예외를 가능한 한 발생 지점 가까이에서 처리하라는 것이다. 하지만 Ousterhout는 반대로, **예외를 상위로 모아서 한 곳에서 처리하는 것이 더 간단할 수 있다**고 주장한다.

---

## 5. 그냥 크래시하라 (Just Crash)

### 5.1 복구 불가능한 에러

정말 드물고, 복구가 불가능한 에러에 대해서는 **그냥 프로그램을 종료**하는 것이 최선일 수 있다:

- 메모리 부족 (Out of Memory)
- 내부 일관성 위반 (데이터 구조 손상)
- 필수 시스템 파일 접근 불가

```python
# 복구 불가능한 에러: 그냥 크래시
def verify_invariant(data):
    if data.checksum != compute_checksum(data.payload):
        # 데이터가 손상됨 — 복구할 방법이 없음
        # 잘못된 데이터로 계속 실행하는 것이 더 위험
        raise SystemExit("FATAL: Data corruption detected")
```

### 5.2 왜 크래시가 나은가

복구 불가능한 에러를 복구하려고 시도하면:
- 복구 코드 자체가 매우 복잡하다
- 복구가 제대로 되었는지 검증하기 어렵다
- 잘못된 복구가 더 심각한 문제를 유발할 수 있다
- 이 모든 코드가 거의 실행되지 않으므로 테스트도 어렵다

---

## 6. 설계 결정: 에러를 줄이는 질문

새로운 API를 설계할 때 스스로 물어야 할 질문:

| 질문 | 적용 기법 |
|------|----------|
| "이 상황을 에러가 아닌 것으로 재정의할 수 있는가?" | 에러를 정의 밖으로 |
| "이 예외를 모듈 내부에서 처리할 수 있는가?" | 예외 마스킹 |
| "여러 예외를 한 곳에서 처리할 수 있는가?" | 예외 집약 |
| "이 에러가 복구 불가능한가?" | 크래시 |

---

## 요약

- **예외 처리는 소프트웨어 복잡성의 주요 원인**이다. 예외가 많을수록 인터페이스가 복잡해진다.
- **에러를 정의 밖으로 내보내라**: API의 의미를 재정의하여 "에러"였던 상황을 정상 동작으로 만든다.
  - `delete` → "파일이 없는 상태를 보장"으로 재정의
  - `substring` → 범위를 자동 조정하여 예외 제거
- **예외 마스킹**: 하위 계층에서 예외를 감지하고 내부적으로 처리 (TCP 재전송).
- **예외 집약**: 여러 예외를 상위 계층에서 한 곳에서 일괄 처리 (웹 서버 디스패처).
- **그냥 크래시**: 복구 불가능한 에러는 복구를 시도하지 말고 종료하라.
- 목표: **예외가 처리되어야 하는 횟수를 최소화**하는 것이다.

---

## 다음 챕터와의 연결

Chapter 11 **"Design it Twice (두 번 설계하라)"** 에서는 중요한 설계 결정에서 대안을 비교하는 원칙을 다룬다. 에러 처리 전략도 마찬가지로, 여러 접근법을 비교하여 가장 복잡성을 줄이는 방향을 선택해야 한다.
