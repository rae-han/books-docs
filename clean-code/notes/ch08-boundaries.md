# Chapter 8: Boundaries (경계)

## 핵심 질문

시스템에 들어가는 모든 소프트웨어를 직접 개발하는 경우는 드물다. 외부 코드(패키지, 오픈 소스, 사내 다른 팀의 컴포넌트)를 우리 코드에 깔끔하게 통합하려면 경계를 어떻게 관리해야 하는가?

---

## 1. 외부 코드 사용하기

인터페이스 **제공자**와 인터페이스 **사용자** 사이에는 특유의 긴장이 존재한다:

| 제공자 | 사용자 |
|---|---|
| 적용성을 최대한 넓히려 한다 | 자신의 요구에 집중하는 인터페이스를 바란다 |
| 더 많은 환경에서 돌아가야 더 많은 고객이 구매하니까 | 불필요한 기능은 위험 요소다 |

이런 긴장으로 인해 시스템 경계에서 문제가 생길 소지가 많다.

### java.util.Map의 문제

`Map`은 굉장히 다양한 인터페이스로 수많은 기능을 제공한다. 유용하지만 그만큼 위험도 크다:

- `Map` 사용자라면 누구나 `clear()` 메서드로 내용을 지울 권한이 있다
- `Map`은 객체 유형을 제한하지 않는다 — 마음만 먹으면 어떤 객체 유형도 추가할 수 있다

```java
// 1단계 — 캐스팅 필요, 의도 불분명
Map sensors = new HashMap();
Sensor s = (Sensor) sensors.get(sensorId);
```

`Map`이 반환하는 `Object`를 올바른 유형으로 변환할 책임이 클라이언트에 있다. 코드는 동작하지만 깨끗하다고 보기 어렵다.

```java
// 2단계 — 제네릭스 사용으로 가독성 향상
Map<String, Sensor> sensors = new HashMap<Sensor>();
Sensor s = sensors.get(sensorId);
```

가독성은 높아지지만 **불필요한 기능까지 제공한다**는 문제는 해결하지 못한다. `Map<String, Sensor>` 인스턴스를 여기저기 넘긴다면, `Map` 인터페이스가 변할 경우 수정할 코드가 상당히 많아진다. 실제로 자바 5가 제네릭스를 지원하면서 `Map` 인터페이스가 변했다.

```java
// 3단계 — 경계 인터페이스를 캡슐화
public class Sensors {
    private Map sensors = new HashMap();

    public Sensor getById(String id) {
        return (Sensor) sensors.get(id);
    }
    // 이하 생략
}
```

### 캡슐화의 장점

| 장점 | 설명 |
|---|---|
| **변경 영향 최소화** | `Map` 인터페이스가 변하더라도 나머지 프로그램에는 영향을 미치지 않는다 |
| **제네릭스 결정 내부화** | 제네릭스를 사용하든 하지 않든 `Sensors` 클래스 안에서 결정한다 |
| **필요한 인터페이스만 제공** | 코드는 이해하기 쉽지만 오용하기는 어렵다 |
| **규칙 강제** | 설계 규칙과 비즈니스 규칙을 따르도록 강제할 수 있다 |

> **핵심 통찰**: `Map` 클래스를 사용할 때마다 캡슐화하라는 소리가 아니다. `Map`을 (혹은 유사한 경계 인터페이스를) **여기저기 넘기지 말라**는 말이다. 경계 인터페이스를 이용할 때는 이를 이용하는 클래스나 클래스 계열 밖으로 노출되지 않도록 주의한다. `Map` 인스턴스를 공개 API의 인수로 넘기거나 반환값으로 사용하지 않는다.

---

## 2. 경계 살피고 익히기

외부 코드를 사용하면 적은 시간에 더 많은 기능을 출시하기 쉬워진다. 하지만 외부 코드를 익히기는 어렵고, 통합하기도 어렵다. **두 가지를 동시에 하기는 두 배나 어렵다.**

다르게 접근하면 어떨까? 곧바로 우리쪽 코드를 작성해 외부 코드를 호출하는 대신, **먼저 간단한 테스트 케이스를 작성해 외부 코드를 익히면** 어떨까? 짐 뉴커크(Jim Newkirk)는 이를 **학습 테스트(learning test)**라 부른다.

학습 테스트는 프로그램에서 사용하려는 방식대로 외부 API를 호출한다. 통제된 환경에서 API를 제대로 이해하는지를 확인하는 셈이다. 학습 테스트는 **API를 사용하려는 목적에 초점**을 맞춘다.

---

## 3. log4j 익히기 — 학습 테스트 실전 예제

로깅 기능을 직접 구현하는 대신 아파치의 log4j 패키지를 사용하려 한다고 가정하자.

### 시도 1 — 가장 간단한 테스트

```java
@Test
public void testLogCreate() {
    Logger logger = Logger.getLogger("MyLogger");
    logger.info("hello");
}
```

테스트를 돌리니 `Appender`라는 뭔가가 필요하다는 오류가 발생한다.

### 시도 2 — ConsoleAppender 추가

```java
@Test
public void testLogAddAppender() {
    Logger logger = Logger.getLogger("MyLogger");
    ConsoleAppender appender = new ConsoleAppender();
    logger.addAppender(appender);
    logger.info("hello");
}
```

`Appender`에 출력 스트림이 없다는 사실을 발견한다.

### 시도 3 — PatternLayout 추가

```java
@Test
public void testLogAddAppender() {
    Logger logger = Logger.getLogger("MyLogger");
    logger.removeAllAppenders();
    logger.addAppender(new ConsoleAppender(
        new PatternLayout("%p %t %m%n"),
        ConsoleAppender.SYSTEM_OUT));
    logger.info("hello");
}
```

이제 제대로 돌아간다. 흥미롭게도 `ConsoleAppender.SYSTEM_OUT` 인수를 제거해도 문제가 없다. 하지만 `PatternLayout`을 제거하면 출력 스트림이 없다는 오류가 뜬다. 기본 `ConsoleAppender` 생성자는 '설정되지 않은' 상태란다 — log4j 버그이거나 적어도 일관성 부족으로 여겨진다.

### 최종 결과 — 학습 테스트 모음

```java
public class LogTest {
    private Logger logger;

    @Before
    public void initialize() {
        logger = Logger.getLogger("logger");
        logger.removeAllAppenders();
        Logger.getRootLogger().removeAllAppenders();
    }

    @Test
    public void basicLogger() {
        BasicConfigurator.configure();
        logger.info("basicLogger");
    }

    @Test
    public void addAppenderWithStream() {
        logger.addAppender(new ConsoleAppender(
            new PatternLayout("%p %t %m%n"),
            ConsoleAppender.SYSTEM_OUT));
        logger.info("addAppenderWithStream");
    }

    @Test
    public void addAppenderWithoutStream() {
        logger.addAppender(new ConsoleAppender(
            new PatternLayout("%p %t %m%n")));
        logger.info("addAppenderWithoutStream");
    }
}
```

간단한 콘솔 로거를 초기화하는 방법을 익혔으니, 이제 모든 지식을 **독자적인 로거 클래스로 캡슐화**한다. 그러면 나머지 프로그램은 log4j 경계 인터페이스를 몰라도 된다.

---

## 4. 학습 테스트는 공짜 이상이다

학습 테스트에 드는 비용은 없다. 어쨌든 API를 배워야 하므로, 오히려 **필요한 지식만 확보하는 손쉬운 방법**이다.

### 학습 테스트의 가치

| 가치 | 설명 |
|---|---|
| **이해도 향상** | API 사용법을 정확한 실험으로 확인 |
| **호환성 검증** | 패키지 새 버전이 나오면 학습 테스트를 돌려 차이 확인 |
| **이전 용이** | 경계 테스트가 있으면 패키지의 새 버전으로 이전하기 쉬움 |
| **조기 경고** | 새 버전이 우리 코드와 호환되지 않으면 학습 테스트가 곧바로 밝혀냄 |

학습 테스트를 이용한 학습이 필요하든 그렇지 않든, 실제 코드와 동일한 방식으로 인터페이스를 사용하는 테스트 케이스가 필요하다. 이런 **경계 테스트**가 있다면 패키지의 새 버전으로 이전하기 쉬워진다. 그렇지 않다면 낡은 버전을 필요 이상으로 오랫동안 사용하려는 유혹에 빠지기 쉽다.

---

## 5. 아직 존재하지 않는 코드를 사용하기

경계와 관련해 또 다른 유형은 **아는 코드와 모르는 코드를 분리하는 경계**다. 때로는 우리 지식이 경계를 너머 미치지 못하는 코드 영역도 있다.

> **Uncle Bob의 경험**: 몇 년 전 무선통신 시스템에 들어갈 소프트웨어 개발에 참여했다. 우리 소프트웨어에는 '송신기(Transmitter)'라는 하위 시스템이 있었는데, 우리는 여기에 대한 지식이 거의 없었다. '송신기' 시스템을 책임진 사람들은 인터페이스도 정의하지 못한 상태였다.

프로젝트 지연을 원하지 않았기에 '송신기' 하위 시스템과 아주 먼 부분부터 작업을 시작했다. 우리가 '송신기' 모듈에게 원하는 기능은 다음과 같았다:

> *지정한 주파수를 이용해 이 스트림에서 들어오는 자료를 아날로그 신호로 전송하라.*

저쪽 팀이 아직 API를 설계하지 않았으므로 구체적인 방법은 몰랐다. 그래서 **자체적으로 인터페이스를 정의**했다:

```
<<interface>>
Transmitter
  + transmit(frequency, stream)

CommunicationController ──→ Transmitter

FakeTransmitter (테스트용)
TransmitterAdapter ──→ <<future>> Transmitter API
```

- `Transmitter` 인터페이스: 주파수와 자료 스트림을 입력으로 받는 **우리가 바라는 인터페이스**
- `FakeTransmitter`: 테스트에 사용하는 가짜 구현
- `TransmitterAdapter`: 저쪽 팀이 API를 정의한 후 ADAPTER 패턴(*ADAPTER 패턴 — GoF의 디자인 패턴 중 하나. 인터페이스를 다른 인터페이스로 변환하여 호환되지 않는 클래스들이 함께 동작할 수 있게 한다.*)으로 간극을 메움

### 자체 인터페이스 정의의 장점

| 장점 | 설명 |
|---|---|
| **전적인 통제** | 우리가 인터페이스를 전적으로 통제한다 |
| **가독성** | 코드 가독성과 의도가 분명해진다 |
| **테스트 용이** | `FakeTransmitter`로 `CommunicationController`를 테스트할 수 있다 |
| **변경 격리** | ADAPTER 패턴으로 API 사용을 캡슐화해 API가 바뀔 때 수정할 코드를 한곳으로 모음 |

---

## 6. 깨끗한 경계

경계에서는 흥미로운 일이 많이 벌어진다. **변경**이 대표적인 예다. 소프트웨어 설계가 우수하다면 변경하는데 많은 투자와 재작업이 필요하지 않다.

### 경계 관리 원칙

1. **경계에 위치하는 코드는 깔끔히 분리**한다
2. **기대치를 정의하는 테스트 케이스**도 작성한다
3. 이쪽 코드에서 외부 패키지를 **세세하게 알아야 할 필요가 없다**
4. 통제가 불가능한 외부 패키지에 의존하는 대신 **통제가 가능한 우리 코드에 의존**하는 편이 훨씬 좋다
5. 외부 패키지를 호출하는 코드를 가능한 줄여 경계를 관리한다

### 경계 관리 기법

| 기법 | 적용 상황 | 핵심 |
|---|---|---|
| **감싸기(Wrapper) 클래스** | `Map`처럼 범용적인 경계 인터페이스 | 새로운 클래스로 경계를 감싸 필요한 인터페이스만 노출 |
| **ADAPTER 패턴** | 아직 정의되지 않은 API, 변경될 가능성이 큰 API | 우리가 원하는 인터페이스를 패키지가 제공하는 인터페이스로 변환 |
| **학습 테스트** | 새로운 외부 패키지 도입 | 통제된 환경에서 API 이해도를 확인하고 호환성을 검증 |

> **핵심 통찰**: 어느 방법이든 **코드 가독성이 높아지며**, 경계 인터페이스를 사용하는 **일관성도 높아지며**, 외부 패키지가 변했을 때 **변경할 코드도 줄어든다.**

---

## 요약

- **외부 코드 사용 시 경계를 관리**하라 — 경계 인터페이스를 여기저기 넘기지 말고 캡슐화하라
- **학습 테스트**로 외부 API를 익히라 — 비용은 없고 이해도 향상, 호환성 검증, 이전 용이 등의 가치를 제공한다
- **아직 존재하지 않는 코드**에 대해서는 우리가 바라는 인터페이스를 정의하고 ADAPTER 패턴으로 간극을 메우라
- 통제가 불가능한 외부 패키지에 의존하는 대신 **통제가 가능한 우리 코드에 의존**하라
- 외부 패키지를 호출하는 코드를 **가능한 줄여** 경계를 관리하라
- **감싸기 클래스**나 **ADAPTER 패턴**으로 외부 패키지가 변했을 때 변경할 코드를 한곳으로 모으라

---

## 다른 챕터와의 관계

- **← Chapter 6 (객체와 자료 구조)**: `Map`을 `Sensors` 클래스로 감싸는 예제가 자료 추상화 원칙을 경계 인터페이스에 적용한 것이다
- **← Chapter 7 (오류 처리)**: 외부 API 감싸기(wrapper) 기법이 예외 처리의 감싸기 클래스와 같은 맥락이다
- **→ Chapter 9 (단위 테스트)**: 학습 테스트가 단위 테스트의 한 형태이며, 경계 테스트가 외부 API의 호환성을 검증하는 역할을 한다
- **→ Chapter 11 (시스템)**: 시스템 수준의 관심사 분리와 의존성 주입이 경계 관리 원칙을 확장한 것이다
- **→ Chapter 17 (냄새와 휴리스틱)**: 경계 조건 처리([G3] 경계 조건을 캡슐화하라)가 이 장의 원칙을 코드 냄새로 체계화한 것이다
