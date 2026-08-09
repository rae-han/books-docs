# Chapter 21: Decide What Matters (무엇이 중요한지 결정하라)

## 핵심 질문

좋은 설계는 중요한 것과 덜 중요한 것을 어떻게 다르게 다루는가?

---

## 1. 핵심 원칙

> **좋은 소프트웨어 설계는 중요한 것과 덜 중요한 것을 구분하고, 이 둘을 다르게 다루는 것이다.**

이 원칙은 이 책의 모든 개념을 관통한다:

- **깊은 모듈**: 중요한 것(기능)은 크게, 덜 중요한 것(인터페이스)은 작게
- **정보 은닉**: 사용자에게 중요한 것만 노출, 덜 중요한 세부사항은 숨김
- **주석**: 중요하고 비자명한 것만 주석으로 설명

---

## 2. 중요한 것을 전면에 내세워라

중요한 것은 **발견하기 쉽고, 눈에 잘 띄어야** 한다:

```java
// 좋은 설계: 핵심 메서드가 인터페이스에서 명확히 드러남
public interface PaymentService {
    PaymentResult charge(Amount amount, PaymentMethod method);
    RefundResult refund(TransactionId transactionId);
}

// 나쁜 설계: 핵심 기능이 수십 개의 메서드 사이에 묻혀 있음
public interface PaymentService {
    void setConfig(Config c);
    void initialize();
    boolean isReady();
    PaymentResult charge(Amount amount, PaymentMethod method);
    void setRetryPolicy(RetryPolicy p);
    RefundResult refund(TransactionId transactionId);
    void setLogger(Logger l);
    Metrics getMetrics();
    void shutdown();
    // ... 15개 더
}
```

---

## 3. 중요한 것의 수를 최소화하라

> 중요한 것이 적을수록 시스템은 단순하다. 모든 것이 "중요"하면 아무것도 중요하지 않다.

Unix I/O가 훌륭한 이유: 중요한 연산이 딱 5개다 (open, close, read, write, lseek). 나머지 모든 복잡성은 숨겨져 있다.

---

## 4. 일반적 경우 vs 특수 경우

- **일반적 경우가 중요하다** — 이것을 위해 최적화하라
- **특수 경우는 덜 중요하다** — 일반적 경우를 복잡하게 만들지 않도록 분리하라

```python
# 나쁜: 특수 경우가 일반적 경우를 오염
def send_email(to, subject, body, is_bulk=False,
               is_transactional=False, priority=None,
               track_opens=False, unsubscribe_link=None):
    ...

# 좋은: 일반적 경우를 단순하게 유지
def send_email(to, subject, body):
    """이메일을 보낸다. 대부분의 경우 이것으로 충분하다."""
    ...

def send_bulk_email(recipients, subject, body, options=None):
    """대량 이메일 전송. 추적, 수신 거부 등 고급 옵션 지원."""
    ...
```

---

## 5. 이 책의 원칙과의 연결

| 원칙 | "중요한 것"을 다루는 방식 |
|------|----------------------|
| 깊은 모듈 | 기능(중요) ↑, 인터페이스(덜 중요) ↓ |
| 정보 은닉 | 중요한 것만 인터페이스에, 나머지는 숨김 |
| 에러 정의 밖으로 | 에러(덜 중요)를 제거하여 정상 경로(중요)를 단순하게 |
| 복잡성 아래로 | 사용자가 다루는 것(중요)을 단순하게 |
| 주석 | 중요하고 비자명한 것만 설명 |
| 성능 | 빈번한 연산(중요)을 위해 최적화 |

---

## 요약

- 좋은 설계는 **중요한 것을 강조하고, 덜 중요한 것을 숨긴다**.
- 중요한 것은 **쉽게 발견되고 이해**되어야 한다.
- 중요한 것의 **수를 최소화**하라 — 적을수록 단순하다.
- **일반적 경우**를 위해 설계하고, 특수 경우는 분리하라.
- 이 원칙은 이 책의 모든 개념을 관통한다.

---

## 다음 챕터와의 연결

Chapter 22 **"Conclusion (결론)"** 에서는 이 책의 모든 설계 원칙과 Red Flag를 종합적으로 정리한다.
