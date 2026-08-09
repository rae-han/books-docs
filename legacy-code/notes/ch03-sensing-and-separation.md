# Chapter 3: 감지와 분리 (Sensing and Separation)

## 핵심 질문

테스트를 작성하기 위해 의존성을 깨뜨려야 하는 이유는 무엇이며, 가짜 객체(Fake Object)와 Mock Object는 어떻게 이 문제를 해결하는가?

---

## 1. 의존성을 깨야 하는 두 가지 이유

테스트 하네스(test harness)에 코드를 넣으려 할 때, 종종 의존성이 방해가 된다. 의존성을 깨뜨려야 하는 이유는 크게 **두 가지**로 분류할 수 있다.

### 1.1 감지 (Sensing)

**Sensing**이란 코드가 계산하는 값이나 수행하는 동작(side effect)을 테스트에서 **확인(감지)할 수 없는** 상황을 말한다.

예를 들어:

- 메서드가 다른 객체의 내부 상태를 변경하는데, 그 상태를 테스트에서 접근할 방법이 없다.
- 메서드가 외부 시스템(네트워크, 콘솔, 로그 등)에 출력을 보내는데, 그 출력을 캡처할 방법이 없다.
- 메서드의 반환값이 없고, 효과(effect)만 발생하는데 그 효과를 관찰할 수 없다.

### 1.2 분리 (Separation)

**Separation**이란 테스트 대상 코드를 나머지 시스템으로부터 **격리(분리)할 수 없는** 상황을 말한다.

예를 들어:

- 클래스의 생성자가 다른 무거운 객체를 생성해야만 한다.
- 메서드를 호출하려면 데이터베이스 연결이 필요하다.
- 테스트 대상 객체가 프로덕션 환경의 외부 서비스에 실제로 요청을 보낸다.

### 1.3 두 문제의 관계

| 문제 | 본질 | 예시 |
|------|------|------|
| **Sensing** | 코드의 효과를 **볼 수 없다** | 메서드가 다른 객체의 상태를 바꾸는데 확인 불가 |
| **Separation** | 코드를 **따로 실행할 수 없다** | 생성자가 DB 연결을 요구하여 테스트 환경에서 생성 불가 |

실제로는 두 문제가 동시에 발생하는 경우가 많다. 가짜 객체(Fake Object)는 두 문제 모두를 해결하는 데 사용할 수 있다.

---

## 2. 구체적 예시: NetworkBridge의 의존성 문제

Feathers는 `NetworkBridge`라는 클래스를 예시로 들어 문제를 설명한다.

### 2.1 문제 상황

```java
public class NetworkBridge {
    public NetworkBridge(EndPoint[] endpoints) {
        // ...
    }

    public void formRouting(String sourceId, String destId) {
        // ... 복잡한 라우팅 로직 ...
    }
}
```

`NetworkBridge`를 테스트하려고 하면 다음 문제에 직면한다:

1. **Separation 문제**: `NetworkBridge`의 생성자는 `EndPoint` 배열을 요구한다. `EndPoint` 객체는 실제 네트워크 하드웨어와 통신하므로, 테스트 환경에서는 생성할 수 없다.

2. **Sensing 문제**: `formRouting` 메서드가 내부적으로 `EndPoint` 객체들의 설정을 변경하지만, 그 변경 결과를 외부에서 확인할 방법이 없다. 실제 하드웨어에 설정이 반영되었는지 확인하려면 실제 네트워크 장비가 필요하다.

### 2.2 의존성 구조

```
[테스트 코드] → [NetworkBridge] → [EndPoint] → [실제 네트워크 하드웨어]
                                      ↑
                                   여기가 문제!
                              테스트에서 생성 불가
                              효과를 감지 불가
```

---

## 3. 가짜 객체 (Fake Object)를 사용한 해결

### 3.1 인터페이스 추출

첫 번째 단계는 `EndPoint` 클래스에서 인터페이스를 추출하는 것이다.

```java
public interface EndPoint {
    void connect();
    void disconnect();
    void configureRouting(String sourceId, String destId);
    // ... 기타 메서드들
}
```

기존의 `EndPoint` 클래스는 이 인터페이스를 구현하도록 변경한다:

```java
public class RealEndPoint implements EndPoint {
    // 실제 네트워크 하드웨어와 통신하는 기존 구현
    public void connect() { /* 실제 연결 */ }
    public void disconnect() { /* 실제 연결 해제 */ }
    public void configureRouting(String sourceId, String destId) {
        // 실제 하드웨어에 라우팅 설정
    }
}
```

### 3.2 가짜 객체 만들기

이제 테스트용 가짜(Fake) 구현체를 만들 수 있다:

```java
public class FakeEndPoint implements EndPoint {
    // Sensing을 위한 내부 기록
    private boolean connected = false;
    private List<String[]> routingConfigs = new ArrayList<>();

    public void connect() {
        connected = true;
    }

    public void disconnect() {
        connected = false;
    }

    public void configureRouting(String sourceId, String destId) {
        routingConfigs.add(new String[]{sourceId, destId});
    }

    // 테스트에서 확인하기 위한 메서드들
    public boolean isConnected() {
        return connected;
    }

    public List<String[]> getRoutingConfigs() {
        return routingConfigs;
    }
}
```

### 3.3 테스트 작성

이제 `NetworkBridge`를 테스트 하네스에서 자유롭게 테스트할 수 있다:

```java
public void testFormRouting() {
    // Separation: 실제 하드웨어 없이 객체 생성 가능
    FakeEndPoint endPoint1 = new FakeEndPoint();
    FakeEndPoint endPoint2 = new FakeEndPoint();
    EndPoint[] endpoints = { endPoint1, endPoint2 };

    NetworkBridge bridge = new NetworkBridge(endpoints);

    // 테스트 대상 동작 수행
    bridge.formRouting("source123", "dest456");

    // Sensing: 가짜 객체를 통해 효과를 확인
    assertEquals(1, endPoint1.getRoutingConfigs().size());
    assertEquals("source123", endPoint1.getRoutingConfigs().get(0)[0]);
    assertEquals("dest456", endPoint1.getRoutingConfigs().get(0)[1]);
}
```

### 3.4 해결된 의존성 구조

```
[테스트 코드] → [NetworkBridge] → [EndPoint 인터페이스]
                                       ↑
                              ┌────────┴────────┐
                      [FakeEndPoint]     [RealEndPoint]
                      (테스트용)          (프로덕션용)
                      생성 가능!          실제 하드웨어
                      효과 감지 가능!      와 통신
```

가짜 객체가 **두 가지 문제를 동시에 해결**한 것을 볼 수 있다:

- **Separation**: `FakeEndPoint`는 실제 하드웨어 없이 생성할 수 있으므로, `NetworkBridge`를 테스트 환경에서 격리하여 실행할 수 있다.
- **Sensing**: `FakeEndPoint`는 `configureRouting` 호출 기록을 내부에 저장하므로, `NetworkBridge`가 수행한 동작을 테스트에서 확인(감지)할 수 있다.

---

## 4. Mock Object 패턴

### 4.1 Mock Object란?

**Mock Object**는 가짜 객체(Fake Object)의 특수한 형태로, **내부적으로 assertion(검증)을 수행하는 가짜 객체**다.

일반 Fake Object에서는 테스트 코드가 가짜 객체의 상태를 확인하여 검증을 수행한다. 반면, Mock Object에서는 **Mock 객체 자신이 기대하는 호출을 알고 있고, 기대와 다른 호출이 오면 스스로 실패를 보고**한다.

### 4.2 Mock Object 사용 예시

```java
public void testFormRouting() {
    // Mock 객체에 기대 동작을 설정
    MockEndPoint mockEndPoint = new MockEndPoint();
    mockEndPoint.expectCall("configureRouting")
                .withArgs("source123", "dest456")
                .times(1);

    EndPoint[] endpoints = { mockEndPoint };
    NetworkBridge bridge = new NetworkBridge(endpoints);

    // 테스트 대상 동작 수행
    bridge.formRouting("source123", "dest456");

    // Mock 객체가 기대한 대로 호출되었는지 검증
    mockEndPoint.verify();
}
```

### 4.3 Mock Object vs Fake Object

| 특성 | Fake Object | Mock Object |
|------|-------------|-------------|
| **본질** | 프로덕션 객체의 가벼운 대체물 | 기대 동작이 내장된 대체물 |
| **검증 방식** | 테스트 코드가 Fake의 상태를 직접 확인 | Mock 자신이 기대와의 일치를 검증 |
| **설정** | 단순한 구현, 호출 기록만 저장 | 기대 호출, 인자, 횟수 등을 미리 설정 |
| **구현 비용** | 직접 클래스를 작성 (간단) | 보통 Mock 프레임워크 사용 |
| **실패 보고** | 테스트의 assert문에서 실패 | Mock 객체의 verify에서 실패 |
| **적합한 경우** | 단순한 상호작용 검증 | 복잡한 상호작용 프로토콜 검증 |

### 4.4 Mock 프레임워크

Mock Object를 매번 직접 작성하는 것은 번거롭다. 이를 위해 다양한 **Mock 프레임워크**가 존재한다:

- **Java**: Mockito, EasyMock, JMock
- **C#**: Moq, NSubstitute, Rhino Mocks
- **Python**: unittest.mock
- **C++**: Google Mock

이런 프레임워크를 사용하면 Mock 객체를 간결하게 생성하고 기대 동작을 설정할 수 있다.

> Mock Object는 매우 강력한 도구지만, Feathers는 이 책에서 Mock보다는 단순한 Fake Object를 더 자주 사용한다. 레거시 코드 작업에서는 복잡한 Mock 설정보다 **단순하고 이해하기 쉬운 Fake**가 더 실용적인 경우가 많기 때문이다.

---

## 5. 감지와 분리의 실무적 의미

### 5.1 의존성을 깨뜨리는 것의 의미

의존성을 깨뜨린다는 것은 프로덕션 코드를 영구적으로 손상시키는 것이 아니다. 핵심은 **테스트 시점에 다른 구현으로 교체할 수 있는 접점(seam)을 만드는 것**이다.

프로덕션 코드에서는 여전히 실제 객체가 사용되고, 테스트 코드에서만 가짜 객체가 사용된다. 이를 가능하게 하는 기법은:

- **인터페이스 추출 (Extract Interface)**: 기존 클래스에서 인터페이스를 뽑아내고, 의존하는 코드가 인터페이스에 의존하도록 변경
- **하위 클래스 오버라이드 (Subclass and Override Method)**: 테스트에서 하위 클래스를 만들어 특정 메서드만 오버라이드
- **파라미터 주입**: 의존 객체를 직접 생성하지 않고 외부에서 전달받도록 변경

### 5.2 Sensing과 Separation 판단 기준

테스트를 작성할 때 다음을 스스로에게 물어보자:

1. **"이 코드의 결과를 확인할 수 있는가?"** → 확인할 수 없다면 **Sensing 문제**
2. **"이 코드를 테스트 환경에서 실행할 수 있는가?"** → 실행할 수 없다면 **Separation 문제**

어떤 문제인지 파악하면, 그에 맞는 해결 전략을 선택할 수 있다.

---

## 요약

- 테스트를 위해 의존성을 깨뜨려야 하는 이유는 **감지(Sensing)** 와 **분리(Separation)** 두 가지다.
- **Sensing**: 코드가 수행하는 동작이나 계산 결과를 테스트에서 확인할 수 없는 문제.
- **Separation**: 테스트 대상 코드를 나머지 시스템으로부터 격리할 수 없는 문제.
- **가짜 객체(Fake Object)** 를 사용하면 두 문제를 동시에 해결할 수 있다.
- 인터페이스를 추출하고, 테스트에서는 가짜 구현체를 주입함으로써 의존성을 깨뜨린다.
- **Mock Object**는 내부적으로 assertion을 가진 특수한 형태의 가짜 객체다.
- Mock Object는 기대 호출을 미리 설정하고, 자체적으로 검증을 수행한다.
- 레거시 코드 작업에서는 복잡한 Mock보다 **단순한 Fake Object**가 더 실용적인 경우가 많다.

---

## 다음 챕터와의 연결

Chapter 4 **"봉합 모델 (The Seam Model)"** 에서는 코드를 편집하지 않고도 프로그램의 동작을 변경할 수 있는 지점인 **Seam(이음새)** 의 개념을 정의하고, Preprocessing Seam, Link Seam, Object Seam 세 가지 유형을 소개한다. 이는 의존성을 깨뜨리는 구체적인 "어디에서, 어떻게"에 대한 답을 제공한다.
