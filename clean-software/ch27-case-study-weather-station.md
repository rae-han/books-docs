# Chapter 27: Case Study: Weather Station (사례 연구: 기상 관측기)

## 핵심 질문

하나의 소프트웨어가 **여러 하드웨어 플랫폼**에서 동일하게 동작해야 하고, **새로운 하드웨어가 12개월 후에야 도착**하며, **사용자 인터페이스는 자주 바뀌고**, **영속성 메커니즘은 플랫폼마다 다르다**면, 우리는 어떻게 설계해야 하는가? PART 5에서 배운 디자인 패턴들(Observer, Bridge, Abstract Factory, Proxy, Template Method)은 이런 현실적 제약 속에서 어떻게 **함께 협력**하여 변경에 강한 아키텍처를 만드는가? 그리고 — **이 모든 결정 뒤에 숨은 원칙(SRP, OCP, DIP, ADP)**은 무엇인가?

> 이 장은 짐 뉴커크(Jim Newkirk)와 공동으로 집필했다. 다음은 꾸민 이야기다. 그러나 여러분의 경험상 많은 부분에서 공감할지도 모른다.

---

## 1. 시나리오 — 클라우드 컴퍼니의 딜레마

### 1.1 사업적 배경

**클라우드 컴퍼니(CloudCompany)**는 산업용 **기상 관측 시스템(*WMS - weather monitoring systems*)** 분야의 업계 선두 기업이다. 이 회사의 제품은 온도·습도·기압·풍속·풍향을 실시간으로 표시하고 시·일 단위 기록을 남긴다. 주요 고객은 항공사·해운업체·농업 분야·방송사 등이다.

| 강점 | 약점 |
|------|------|
| 신뢰성이 높다 | 가격이 비싸다 |
| 까다로운 환경에서도 동작한다 | 저가 시장을 잡지 못한다 |

### 1.2 위협 — 마이크로버스트의 등장

**마이크로버스트(Microburst, Inc.)**라는 경쟁자가 등장했다. 저가형 제품부터 시작해 점진적으로 높은 신뢰성 수준으로 향상해갈 수 있는 **제품 계열(product line)**을 발표했다. 더 나쁜 소식은 고가형에는 **상호 연결 기능**까지 있다는 점이다 — 넓은 범위의 기상 관측 네트워크를 만들 수 있다.

### 1.3 전략 — 님버스-LC

마이크로버스트는 6개월간 실제 출하를 못 하고 있다. 클라우드 컴퍼니는 **6개월 안에 향상 가능하고 상호 연결되는 저가형 제품**을 출시해 마이크로버스트의 시장을 흔들기로 결정한다.

| 단계 | 제품명 | 시기 | 특징 |
|------|--------|------|------|
| 1차 (위장) | **님버스-LC 1.0** | 6개월 | 기존 비싼 하드웨어에 LCD 터치패널 케이스. 한 대 팔 때마다 손해 |
| 2차 (본격) | **님버스-LC 2.0** | 12개월 | 진짜 저가형 하드웨어. 1.0 고객은 무상 교체 |

### 1.4 소프트웨어의 도전

소프트웨어는 **1.0과 2.0 양쪽에서 동일하게 동작**해야 한다. 그런데:

- 2.0 보드의 프로세서는 1.0과 다를 가능성이 높다
- 2.0 하드웨어 프로토타입은 9개월 후에야 나온다
- 소프트웨어는 6개월 안에 1.0 출시 수준에 도달해야 한다
- 1.0 QA에 6주 → 실제 개발 시간은 **20주**뿐
- 2.0은 새 하드웨어이므로 8~10주의 긴 QA가 필요하다

> **핵심 통찰**: 이 사례 연구의 핵심 제약은 **이식성(portability)**이다. 짧은 개발 시간과 미래 하드웨어에 대한 무지가 결합하면, 설계는 반드시 **추상적 행위와 구체적 구현을 분리**해야 한다. 언어로는 자바를 선택했다 — 이식성을 위해.

---

## 2. 첫 번째 시도 — Temperature Sensor

가장 자연스러운 출발점은 **하드웨어 추상화**다. "온도를 어떻게 표시할까?"가 아니라 "온도를 어떻게 추상화할까?"부터 시작한다.

### 2.1 추상 기반 클래스 + 파생형

```
                  ┌──────────────────────┐
                  │  TemperatureSensor   │  ◀── 추상 기반 클래스
                  ├──────────────────────┤
                  │ + read(): double     │
                  └──────────┬───────────┘
                             △
              ┌──────────────┼──────────────┐
              │              │              │
   ┌──────────┴───┐ ┌────────┴─────┐ ┌──────┴─────────┐
   │ Nimbus1.0    │ │ Nimbus2.0    │ │ TestTemperature│
   │ Temperature  │ │ Temperature  │ │ Sensor         │
   │ Sensor       │ │ Sensor       │ │                │
   └──────────────┘ └──────────────┘ └────────────────┘
```

`TemperatureSensor`는 다형성을 지닌 `read()` 함수를 제공하고, 파생형이 각 하드웨어 플랫폼에 대응한다. **`TestTemperatureSensor`**는 일반 개발 컴퓨터에서 단위 테스트와 인수 테스트를 작성할 수 있게 해 준다.

> **핵심 통찰**: 테스트 클래스는 단순히 "하드웨어가 없을 때의 대안"이 아니다. **하드웨어로 흉내내기 힘든 실패 상황**을 만들어볼 수 있는 유일한 수단이다. 그리고 **2.0 이식성 문제를 줄이는 보험**이기도 하다 — 다중 플랫폼에서 이미 돌아가고 있는 코드는 또 다른 플랫폼으로 옮기기도 쉽다.

---

## 3. 두 번째 시도 — Scheduler와 그 한계

값마다 갱신 주기가 다르다. 온도는 1분, 기압은 5분. 그렇다면 **스케줄러(Scheduler)**가 필요해 보인다.

### 3.1 초기 설계

```
   ┌─────────────────┐
   │ Scheduler       │──◆── BarometricPressureSensor
   │ + tic()         │──◆── TemperatureSensor
   └────────┬────────┘
            │ 1분마다 read() + displayTemp()
            ▼
   ┌─────────────────┐
   │ MonitoringScreen│
   │ + displayTemp() │
   │ + displayPress()│
   └─────────────────┘
```

`Scheduler`는 10ms마다 호출되는 `tic()`을 가지고, `tic()` 호출 횟수를 세어 1분마다 `TemperatureSensor.read()`를 호출하고, 그 결과를 `MonitoringScreen`에 전달한다.

### 3.2 기압 동향 문제 — 알고리즘은 어디에 두는가?

요구사항: 기압 동향(상승/하강/안정)을 보고해야 한다. 미연방 기상학 핸드북에 따르면 "기압이 시간당 0.06인치 이상 변하고 3시간 측정값이 0.02인치 이상이면 변화로 본다."

**선택지 A** — `BarometricPressureSensor`에 알고리즘을 넣는다:
- 매번 측정 시각을 알아야 한다
- 3시간 분량의 측정값 기록을 가져야 한다
- 사용자 인터페이스 갱신 빈도와 동향 계산이 **결합**된다

**선택지 B** — `Scheduler`에 기록을 둔다:
- 그러면 온도, 풍속 기록도 모두 Scheduler에 둘 것인가?
- 새로운 감지기가 추가될 때마다 Scheduler를 수정해야 한다 → **유지보수 악몽**

### 3.3 Scheduler 다시 보기 — OCP 위반

```
              모든 화살표가 Scheduler로 향한다
              ─────────────────────────────────
   Sensor1   Sensor2   Sensor3   ...   UI Screen
       ↘       ↓        ↙              ↙
              Scheduler            (모두를 안다)
```

`Scheduler`가 모든 감지기와 UI에 연결되어 있다. 감지기가 추가되면 `Scheduler`도 수정해야 한다. 이것은 **OCP(개방-폐쇄 원칙) 위반**이다.

> **핵심 통찰**: "중앙 조정자(central coordinator)"는 처음엔 깔끔해 보이지만 거의 항상 **모든 변화의 축이 통과하는 병목**이 된다. Scheduler가 모두를 알아야 한다는 사실 자체가 잘못된 신호다.

---

## 4. Observer 패턴 — UI와 Scheduler 결합 끊기

사용자 인터페이스는 **변경되기 쉬운 곳**이다. 고객, 마케팅, 제품을 접해본 누구나의 변덕에 따라 바뀐다. 따라서 **먼저 UI 결합을 끊어야 한다**.

### 4.1 Observer 패턴 적용

```
                 update()           displayTemp()
   Sensor ──────────────▶ TemperatureObserver ──────▶ MonitoringScreen
   (Observable)            (Adapter)                   (UI)
```

- `Sensor`는 측정값이 바뀌면 `notifyObservers()`를 호출한다
- `TemperatureObserver`는 어댑터다 — `update()`를 받아 `displayTemp(val)`을 호출한다
- `MonitoringScreen`은 감지기를 **직접 알 필요가 없다**

### 4.2 기압 동향 — 또 다른 옵저버

`BarometricPressureTrendSensor`는 **`BarometricPressureSensor`의 옵저버**가 되어, 측정값을 받아 동향을 계산한다. 동향 계산은 이제 **별개의 컴포넌트**가 되었고, 누구도 Scheduler를 수정할 필요가 없다.

> **핵심 통찰**: Observer 패턴은 단순히 "이벤트 알림"이 아니다. **변경의 축이 다른 두 책임을 결합 없이 연결하는 도구**다. UI는 감지기를 모르고, 감지기는 UI를 모르지만, 측정값은 자동으로 흐른다.

---

## 5. AlarmClock — Scheduler의 또 다른 OCP 위반 해결

옵저버로 UI와의 결합은 끊었지만, 여전히 **Scheduler가 어떤 감지기를 언제 깨울지 알고 있다**. 감지기를 추가하거나 주기를 바꾸려면 Scheduler를 수정해야 한다.

### 5.1 Listener 패러다임으로 전환

자바의 **Listener 패러다임**을 빌려온다. Listener는 옵저버와 비슷하지만, 특정 **이벤트(시간)**의 발생에 대한 통보를 받는다.

```
   ┌─────────────────┐                ┌────────────────────┐
   │  AlarmClock     │                │ «interface»        │
   ├─────────────────┤                │ AlarmListener      │
   │ + wakeEvery(    │ ─────────────▶ ├────────────────────┤
   │     interval,   │                │ + wakeup()         │
   │     listener)   │                └────────────────────┘
   └─────────────────┘                         △
                                               │ implements
                                               │
                                       «anonymous»
                                       in TemperatureSensor
```

- 감지기는 익명 `AlarmListener` 어댑터를 만들어 `AlarmClock`에 등록한다
- 등록할 때 **자신의 폴링 주기**를 명시한다 ("1초마다", "50ms마다")
- 시간이 되면 `AlarmClock`이 어댑터에게 `wakeup()`을 보내고, 어댑터는 감지기의 `read()`를 호출한다

### 5.2 변신 — Scheduler에서 AlarmClock으로

Scheduler의 성격이 완전히 바뀌었다:

| 항목 | 변경 전 (Scheduler) | 변경 후 (AlarmClock) |
|------|---------------------|----------------------|
| 위치 | 시스템 중심 | 시스템 외곽 |
| 지식 | 모든 컴포넌트를 안다 | 아무것도 모른다 |
| 책임 | 스케줄링 + 디스패치 | 스케줄링만 |
| 재사용성 | 기상 관측 전용 | 다른 애플리케이션에서도 사용 가능 |

이름까지 `AlarmClock`으로 바꿨다. **이름이 책임을 따라간다.**

---

## 6. 감지기의 내부 구조 — Template Method

감지기와 시스템 사이의 결합은 끊겼다. 이제 **감지기 내부**를 살펴보자. 감지기에는 세 가지 독립된 기능이 있다:

1. `AlarmListener`의 익명 파생형 생성 및 등록
2. 측정값을 읽고, 변했으면 `notifyObservers()` 호출
3. 실제 하드웨어와 상호작용해서 측정값 가져오기

### 6.1 Template Method 적용

<details>
<summary>원문 Java 코드</summary>

```java
// Java - TemperatureSensor의 Template Method
public abstract class TemperatureSensor extends Observable {
    private double itsLastReading;

    // 익명 AlarmListener가 wakeup()에서 호출
    private void check() {
        double val = read();
        if (val != itsLastReading) {
            itsLastReading = val;
            setChanged();
            notifyObservers(val);
        }
    }

    // 파생형이 구현 — Template Method의 핵심
    protected abstract double read();
}

// 파생형
public class Nimbus1_0TemperatureSensor extends TemperatureSensor {
    @Override
    protected native double read();  // 하드웨어 직접 호출
}
```

</details>

```typescript
// TypeScript - Template Method 패턴
abstract class TemperatureSensor extends Observable {
    private itsLastReading: number = 0;

    // 일반적인 검사 로직 — 기반 클래스가 소유
    private check(): void {
        const val = this.read();
        if (val !== this.itsLastReading) {
            this.itsLastReading = val;
            this.setChanged();
            this.notifyObservers(val);
        }
    }

    // 하드웨어 의존적 — 파생형이 구현
    protected abstract read(): number;
}

class Nimbus1_0TemperatureSensor extends TemperatureSensor {
    protected read(): number {
        // 네이티브 하드웨어 호출
        return 0;
    }
}
```

> **핵심 통찰**: Template Method는 **일반 로직과 변하는 부분을 분리**한다. `check()`는 모든 감지기에 공통이지만 `read()`는 하드웨어마다 다르다. 새로운 하드웨어가 도착하면 파생형 하나에서 `read()` 한 줄만 구현하면 끝이다.

---

## 7. API는 어디에 있는가? — Bridge 패턴

하드웨어 공학자들은 **간단한 자바 API**를 원한다. 옵저버 등록 같은 귀찮은 일 없이, 직접 하드웨어에 접근하는 도구를 만들 수 있어야 한다.

```java
public interface TemperatureSensor {
    public double read();
}
```

지금까지 만든 클래스 중 이런 API가 될 만한 것은 없다 — `TemperatureSensor`는 옵저버 등록, 익명 리스너 등 너무 많은 책임을 가진다.

### 7.1 Bridge 패턴으로 추상과 구현 분리

```
   ┌──────────────────────┐        ┌───────────────────────┐
   │  TemperatureSensor   │ ──◆──▶ │ «interface»           │
   │  (애플리케이션 추상)  │        │ TemperatureSensorImp  │  ◀── 진짜 API
   │  - itsLastReading    │        │ + read(): double      │
   │  + check()           │        └───────────┬───────────┘
   └──────────────────────┘                    △
                                               │ implements
                                ┌──────────────┴───────────┐
                                │ Nimbus1_0TemperatureSensor│
                                │ + read(): double {native}│
                                └──────────────────────────┘
```

- `TemperatureSensor` = **추상** (애플리케이션이 보는 인터페이스)
- `TemperatureSensorImp` = **구현** (진짜 API, 하드웨어 공학자가 직접 호출)
- 추상과 구현이 **각자 변화**할 수 있다 — Bridge 패턴의 의도

---

## 8. 생성 문제 — Abstract Factory와 StationToolkit

`TemperatureSensor`를 생성할 때 `Nimbus1_0TemperatureSensorImp`를 같이 만들어 묶어야 한다. **누가 이 일을 하는가?** 누가 하든 그 부분은 **플랫폼 의존적**이 된다.

### 8.1 첫 번째 시도 — main()에서 직접 생성

<details>
<summary>원문 Java 코드</summary>

```java
public class WeatherStation {
    public static void main(String[] args) {
        AlarmClock ac = new AlarmClock(new Nimbus1_0AlarmClock());
        TemperatureSensor ts = new TemperatureSensor(
            ac, new Nimbus1_0TemperatureSensor());
        BarometricPressureSensor bps = new BarometricPressureSensor(
            ac, new Nimbus1_0BarometricPressureSensor());
        // ... 감지기 추가할 때마다 main을 수정해야 한다
    }
}
```

</details>

문제: **감지기 종류만큼 플랫폼 의존 코드가 main에 늘어난다.**

### 8.2 Abstract Factory — StationToolkit 도입

```
              ┌─────────────────────────────────────────┐
              │ «interface»  StationToolkit             │
              ├─────────────────────────────────────────┤
              │ + makeTemperature():                    │
              │       TemperatureSensorImp              │
              │ + makeBarometricPressure():             │
              │       BarometricPressureSensorImp       │
              │ + getAlarmClock(): AlarmClockImp        │
              └───────────────┬─────────────────────────┘
                              △
                              │ implements
              ┌───────────────┴─────────────────────────┐
              │ Nimbus1_0Toolkit                        │
              │ ─ creates ─▶ Nimbus1_0TemperatureSensor │
              │ ─ creates ─▶ Nimbus1_0BarometricPress.. │
              │ ─ creates ─▶ Nimbus1_0AlarmClock        │
              └─────────────────────────────────────────┘
```

```typescript
// TypeScript - Abstract Factory
interface StationToolkit {
    makeTemperature(): TemperatureSensorImp;
    makeBarometricPressure(): BarometricPressureSensorImp;
    getAlarmClock(): AlarmClockImp;
}

class Nimbus1_0Toolkit implements StationToolkit {
    makeTemperature(): TemperatureSensorImp {
        return new Nimbus1_0TemperatureSensorImp();
    }
    makeBarometricPressure(): BarometricPressureSensorImp {
        return new Nimbus1_0BarometricPressureSensorImp();
    }
    getAlarmClock(): AlarmClockImp {
        return new Nimbus1_0AlarmClockImp();
    }
}
```

감지기 생성자는 `StationToolkit`을 인자로 받아 **자신의 구현을 스스로 생성**한다:

```typescript
class TemperatureSensor extends Observable {
    private itsImp: TemperatureSensorImp;

    constructor(ac: AlarmClock, st: StationToolkit) {
        super();
        this.itsImp = st.makeTemperature();
        // ... AlarmClock에 자신을 등록
    }
}
```

### 8.3 진화하는 main()

```typescript
// 1차 — 모든 구현을 명시
const ts = new TemperatureSensor(ac, new Nimbus1_0TemperatureSensorImp());
const bps = new BarometricPressureSensor(ac, new Nimbus1_0BPSensorImp());

// 2차 — StationToolkit으로 통합
const st: StationToolkit = new Nimbus1_0Toolkit();
const ac = new AlarmClock(st);
const ts = new TemperatureSensor(ac, st);

// 3차 — 명령행 인자로 동적 로딩 (자바의 reflection)
const tkClass = Class.forName(args[0]);
const st = tkClass.newInstance() as StationToolkit;
```

> **핵심 통찰**: 이제 **플랫폼 의존 코드는 단 한 줄**이다. 새로운 플랫폼이 도착하면 새 `Toolkit` 구현 하나만 추가하고, main의 한 라인만 바꾸면 된다. 이것이 PART 5 패턴들의 **누적 효과**다.

---

## 9. 패키지 구조와 의존성 비순환 원칙(ADP)

### 9.1 1차 시도 — 순환 의존성

UI를 별개 패키지로 빼고 싶지만, `MonitoringScreen`이 모든 감지기를 알아야 하므로 **UI와 WeatherMonitoringSystem 사이에 순환 의존**이 생긴다 → **ADP(Acyclic Dependencies Principle) 위반**.

### 9.2 main()을 바깥으로 빼기

```
                    ┌─────────────┐
                    │    Main     │
                    │ + main()    │
                    └──┬──────┬───┘
                       │      │ creates
                       ▼      ▼
              ┌──────────┐  ┌─────────────────────────┐
              │    UI    │  │ WeatherMonitoringSystem │
              │ Monitor- │──│ • TemperatureSensor     │
              │ Screen   │  │ • WeatherStation        │
              └──────────┘  └─────────────────────────┘
                       의존 관계가 단방향
```

`MonitoringScreen`은 `WeatherStation`을 받아 감지기에 옵저버를 등록한다. 이를 위해 `WeatherStation`에 `addTempObserver()` 같은 메서드를 추가한다.

### 9.3 2차 문제 — DIP 위반

UI가 구체 패키지인 `WeatherMonitoringSystem`에 직접 의존하면 **DIP(의존 관계 역전 원칙) 위반**이다. UI는 추상에 의존해야 한다.

### 9.4 해결 — WeatherStationComponent 인터페이스

```
   ┌────────────────────┐
   │  Main              │
   └──┬───────────┬─────┘
      │           │
      ▼           ▼
   ┌────────┐  ┌──────────────────────────┐
   │   UI   │  │ WeatherStationComponent  │  ◀── 추상 패키지
   │ Monit- │─▶│ «interface»              │
   │ orScr  │  │ + addTempObserver(o)     │
   └────────┘  │ + addBPObserver(o)       │
               └──────────────┬───────────┘
                              △
                              │ implements
               ┌──────────────┴──────────┐
               │ WeatherMonitoringSystem │  ◀── 구체 패키지
               │ • WeatherStation        │
               └─────────────────────────┘
```

UI와 WeatherMonitoringSystem은 이제 서로를 모른다. **둘 다 추상 패키지에만 의존**한다 — 진정한 DIP 적용이다.

---

## 10. 영속성 — 24시간 기록과 SRP 위반

릴리즈 1 요구사항: 지난 24시간의 최댓값/최솟값 기록을 유지하라. 단, "지난 24시간"이 아니라 **달력상 어제**의 값이다 (요구사항 명세를 재확인하여 발견).

### 10.1 PersistentImp 인터페이스

```typescript
// Java 직렬화를 활용한 영속성 API
interface PersistentImp {
    store(name: string, obj: Serializable): void;
    retrieve(name: string): unknown;
    directory(regExp: string): AbstractList;
}
```

객체와 이름을 통해 읽고 쓰는 단순한 인터페이스다. **`Serializable` 구현이 유일한 제약**이다.

### 10.2 HiLoData — Observer + AlarmClock 조합

```
              ┌──────────────┐  observes
              │ TemperatureHi│ ──────────▶ TemperatureSensor
              │ Lo           │
              └──────┬───────┘
                     │ uses
                     ▼
              ┌──────────────────────┐
              │ «interface» HiLoData │
              ├──────────────────────┤
              │ + currentReading(    │
              │     value, time)     │
              │ + newDay(initial,    │
              │     time)            │
              │ + getHighValue()     │
              │ + getLowValue()      │
              └──────────────────────┘
```

- `TemperatureHiLo`: `TemperatureSensor`의 옵저버이자 `AlarmClock`의 리스너 (매일 자정 깨어남)
- `HiLoData`: 데이터를 보관하고 갱신 알고리즘을 가진다
- **두 클래스 분리 이유**: HiLo 알고리즘은 `BarometricPressureHiLo`, `DewPointHiLo` 등에서 **재사용**할 수 있다

### 10.3 깔끔하지 않은 코드 — HiLoDataImp의 SRP 위반

<details>
<summary>원문 Java 코드 (목록 27-8 일부)</summary>

```java
public class HiLoDataImp implements HiLoData, Serializable {
    public void currentReading(double current, long time) {
        if (current > itsHighValue) {
            itsHighValue = current;
            itsHighTime = time;
            store();  // ◀── 영속성 책임이 섞여 있다
        } else if (current < itsLowValue) {
            itsLowValue = current;
            itsLowTime = time;
            store();  // ◀── 영속성 책임이 섞여 있다
        }
    }

    private void store() {
        try {
            itsPI.store(itsStorageKey, this);  // 영속성
        } catch (StoreException e) { /* ... */ }
    }

    private String calculateStorageKey(Date d) {
        // 영속성 키 생성 책임
    }

    transient private api.PersistentImp itsPI;  // 영속성 의존
}
```

</details>

이 클래스에는 **두 책임**이 섞여 있다:

| 책임 | 메서드 |
|------|--------|
| HiLo 정책 (값 비교/갱신) | `currentReading`, `newDay` |
| 영속성 메커니즘 | `store`, `calculateStorageKey`, 생성자의 retrieve |

영속성 메커니즘이 바뀌면 정책 메서드도 수정해야 한다. **SRP 위반**.

---

## 11. Proxy 패턴 — 정책과 메커니즘 분리

### 11.1 HiLoDataProxy 도입

```
   ┌────────────┐
   │TemperatureH│
   │Lo          │
   └─────┬──────┘
         │ uses
         ▼
   ┌─────────────────────┐
   │ «interface»         │
   │ HiLoData            │
   └────────┬────────────┘
            △
            │ implements
   ┌────────┴────────────────┐         ┌────────────────┐
   │ HiLoDataProxy           │ ◆ ───▶  │ HiLoDataImp    │
   │ - itsImp                │         │ (순수 정책만)   │
   │ + currentReading()      │         │ - itsHighValue │
   │ + newDay()              │         │ + currentRead. │
   │ - store()               │         │ + newDay()     │
   │ - calculateStorageKey() │         └────────────────┘
   └─────────────────────────┘
            │
            ▼
   ┌─────────────────┐
   │ PersistentImp   │  ◀── 메커니즘 레이어
   └─────────────────┘
```

```typescript
// TypeScript - Proxy 패턴
class HiLoDataProxy implements HiLoData {
    private itsImp: HiLoDataImp;
    private itsStorageKey: string;

    currentReading(current: number, time: number): boolean {
        const changed = this.itsImp.currentReading(current, time);
        if (changed) {
            this.store();
        }
        return changed;
    }

    newDay(initial: number, time: number): void {
        this.store();
        this.itsImp.newDay(initial, time);
        this.calculateStorageKey(new Date(time));
        this.store();
    }

    private store(): void { /* PersistentImp 호출 */ }
}

class HiLoDataImp implements HiLoData {
    private itsHighValue = 0;
    private itsLowValue = 0;

    currentReading(current: number, time: number): boolean {
        let changed = false;
        if (current > this.itsHighValue) {
            this.itsHighValue = current;
            changed = true;
        } else if (current < this.itsLowValue) {
            this.itsLowValue = current;
            changed = true;
        }
        return changed;
    }

    newDay(initial: number, time: number): void {
        this.itsHighValue = this.itsLowValue = initial;
    }
}
```

### 11.2 boolean 반환의 사연

`currentReading`이 `boolean`을 반환하도록 변경했다. **프록시가 언제 `store()`를 호출해야 하는지 알기 위해서**다.

> **핵심 통찰**: "변경이 일어났을 때만 저장"하는 것은 NVRAM(*Non-Volatile RAM - 비휘발성 메모리*) 중 **기록 횟수에 한계가 있는 종류**가 있기 때문이다. 즉, 현실 세계의 하드웨어 제약이 인터페이스 시그너처를 결정한다. 깨끗한 설계도 현실에 양보해야 할 때가 있다.

---

## 12. DataToolkit과 패키지 구조의 최종 형태

### 12.1 Proxy 생성을 위한 또 하나의 Factory

`TemperatureHiLo`는 `HiLoDataProxy`를 직접 알면 안 된다 — 정책 레이어가 메커니즘 레이어에 의존하게 되기 때문이다. 따라서 또 하나의 추상 팩토리 `DataToolkit`을 도입한다.

```
   ┌────────────────────────┐
   │  «interface»           │
   │  DataToolkit           │ ◀── wmsdata 패키지
   ├────────────────────────┤
   │ + getTempHiLoData():   │
   │       HiLoData         │
   └──────────┬─────────────┘
              △
              │ implements
   ┌──────────┴─────────────┐
   │  DataToolkitImp        │ ◀── persistence 패키지
   │  creates HiLoDataProxy │
   └────────────────────────┘
```

### 12.2 패키지 의존 관계의 최종 모습

```
                  ┌──────────┐
                  │   wms    │  ◀── 정책 (TemperatureHiLo)
                  └────┬─────┘
                       │
            ┌──────────┴──────────┐
            ▼                     ▼
       ┌─────────┐         ┌───────────┐
       │ wmsdata │         │wmsdataimp │  ◀── 정책 구현 (HiLoDataImp)
       │ (인터페 │         │           │
       │  이스)   │         └───────────┘
       └─────────┘
            △                     △
            │ implements          │ uses
   ┌────────┴───────┐             │
   │  persistence   │─────────────┘  ◀── 메커니즘 (HiLoDataProxy, DataToolkitImp)
   └────────────────┘
            │
            ▼
   ┌────────────────┐
   │      api       │  ◀── PersistentImp
   └────────────────┘
```

> **핵심 통찰**: 패키지 구조는 **추상 인터페이스를 담는 패키지(wmsdata)**가 위에, **구체 구현을 담는 패키지(persistence)**가 아래에 위치한다. 모든 의존성은 **추상 쪽을 향한다** — DIP의 패키지 레벨 적용이다.

### 12.3 Scope 유틸리티 — 정적 전역 변수의 자리

```typescript
// wmsdata.Scope - 추상 패키지의 유틸리티 (변수만)
class Scope {
    static itsDataToolkit: DataToolkit;
}

// persistence.Scope - 구체 패키지의 유틸리티 (함수만)
class Scope {
    static init(): void {
        wmsdataScope.itsDataToolkit = new DataToolkitImp();
    }
}
```

**흥미로운 대칭**: 추상 패키지의 Scope는 변수만, 구체 패키지의 Scope는 함수만 가진다.

### 12.4 Factory를 추가하지 않는 결정

`HiLoDataProxy`가 `HiLoDataImp`를 생성할 때 또 다른 팩토리가 필요할 수 있다. 하지만:

> **Uncle Bob의 경험**: 우리는 프록시와 imp 사이의 의존 관계가 큰 유지보수 위험이 되지 않을 것이라고 결정을 내렸으며, 이 결정에 따라 팩토리 없이 그냥 갈 것이다. wmsDataImp 패키지는 앞으로 상당 기간 변하지 않을 기상 관측 정책과 업무 규칙을 담고 있다. "이것은 앞으로 변하지 않을 거야"라고 말하는 것을 믿기는 힘들겠지만, 그래도 어딘가에서 선을 긋긴 그어야 한다.

**모든 의존성에 팩토리를 둘 수는 없다.** 어디선가는 선을 그어야 한다 — 변경 가능성을 평가하고, 위험 대비 비용을 따져야 한다.

---

## 13. 사용된 패턴과 원칙 정리

### 13.1 패턴 카탈로그

| 패턴 | 역할 | 어디서 |
|------|------|--------|
| **Observer** | UI/Scheduler 결합 끊기, 측정값 전파 | TemperatureSensor → MonitoringScreen, TemperatureHiLo |
| **Adapter** | Observer 인터페이스를 UI 메서드로 변환 | TemperatureObserver |
| **Listener** | AlarmClock과 감지기 결합 끊기 | AlarmListener (익명 어댑터) |
| **Template Method** | 일반 로직(check)과 하드웨어 의존 로직(read) 분리 | TemperatureSensor의 check/read |
| **Bridge** | 애플리케이션 추상과 하드웨어 구현 분리 | TemperatureSensor/TemperatureSensorImp |
| **Abstract Factory** | 플랫폼별 구현 생성 통합 | StationToolkit, DataToolkit |
| **Proxy** | 정책과 영속성 메커니즘 분리 | HiLoDataProxy |
| **Singleton** | AlarmClockImp는 시스템에 하나만 | Nimbus1.0AlarmClock |

### 13.2 적용된 원칙

| 원칙 | 적용 사례 |
|------|----------|
| **SRP** | HiLoDataImp에서 영속성을 Proxy로 분리, Scheduler에서 디스패치 책임을 옵저버로 분리 |
| **OCP** | StationToolkit으로 새 플랫폼 추가 가능, Observer로 새 감지기 추가 가능 |
| **LSP** | 모든 `*Imp` 구현은 인터페이스 계약을 지킴 |
| **DIP** | UI → WeatherStationComponent ← WeatherStation, persistence → wmsdata |
| **ISP** | TemperatureSensor(애플리케이션용)와 TemperatureSensorImp(하드웨어용) 인터페이스 분리 |
| **ADP** | Main을 바깥으로 빼서 UI/WMS 순환 의존 해소 |

---

## 14. 자주 하는 실수

| 안티패턴 | 문제 | 해결 |
|----------|------|------|
| **중앙 조정자(God Scheduler)** | 모든 컴포넌트가 한 클래스로 연결, OCP 위반 | Observer + Listener로 분산, 각자 등록 |
| **하드웨어와 정책 결합** | 하드웨어 교체 시 비즈니스 로직까지 영향 | Bridge로 추상과 구현 분리 |
| **알고리즘 + 영속성 결합** | DB 변경이 알고리즘 코드를 깨뜨림 | Proxy로 메커니즘 격리 |
| **main()이 시스템 안에 위치** | 패키지 순환 의존 유발 | main을 별도 root 패키지로 추출 |
| **구체 패키지에 직접 의존하는 UI** | DIP 위반, UI 변경이 시스템 전체에 영향 | 인터페이스 패키지 도입 (WeatherStationComponent) |
| **모든 곳에 팩토리** | 과도한 추상화, 의미 없는 복잡도 증가 | 변경 가능성을 평가하여 의미 있는 곳에만 적용 |

---

## 15. 설계 원칙

| 원칙 | 설명 |
|------|------|
| **이식성을 첫 번째 제약으로** | 다중 플랫폼 요구가 있으면 추상화가 모든 결정의 기반이 된다 |
| **변경의 축마다 다른 패턴** | Observer는 데이터 흐름의 축, Bridge는 구현의 축, Abstract Factory는 플랫폼의 축 |
| **이름이 책임을 따라간다** | Scheduler → AlarmClock으로 변경, 책임이 바뀌면 이름도 바뀐다 |
| **테스트 플랫폼은 일급 시민** | TestTemperatureSensor는 보조가 아니라 다중 플랫폼 검증의 첫 번째 사례 |
| **현실이 깨끗한 설계에 양보를 요구한다** | NVRAM 수명 같은 하드웨어 제약이 boolean 반환 같은 시그너처를 결정한다 |
| **어딘가에서는 선을 긋는다** | 모든 의존성을 팩토리로 추상화할 수는 없다 — 위험을 평가해 결정한다 |

---

## 16. 결론

> **Uncle Bob의 경험**: 짐 뉴커크와 나는 이 장을 1998년 초반에 집필했다. 짐이 대부분의 코드를 작성했고, 나는 그 코드를 UML 다이어그램으로 옮겨서 거기에 살을 붙이는 작업을 했다. 코드는 이미 없어진 지 오래됐지만, 사실상 그 코드를 만들면서 이 장에서 본 설계를 이끌어낸 것이다. 다이어그램 대부분은 코드가 완성된 다음에 만들어졌다.

> **Uncle Bob의 경험**: 1998년에는 짐이나 나나 익스트림 프로그래밍(Extreme Programming)에 대해 들어본 적이 없었다. 따라서 이 장에서 여러분이 본 설계는 짝 프로그래밍과 테스트 중심 개발 환경에서 만들어진 것이 아니다. 하지만 짐과 나는 언제나 긴밀하게 협력하며 일했다. 우리 둘은 함께 그가 작성한 코드를 검토하고, 실행할 수 있으면 실행해보고, 함께 설계를 변경하고, 이 장의 UML과 글을 작성했다. 그러므로 비록 이 설계가 XP 이전의 것이긴 하지만, 그래도 이 설계는 긴밀한 협력 속에서 코드에 중심을 두는 방법으로 만들어졌다.

> **핵심 통찰**: 이 사례 연구의 진정한 가르침은 "어떤 패턴이 좋다"가 아니라 **"패턴들이 어떻게 협력하는가"**다. Observer는 Bridge 없이도 작동하지만, 함께 쓰면 다중 플랫폼에서 자유로워진다. Abstract Factory는 Proxy 없이도 작동하지만, 함께 쓰면 영속성까지 추상화된다. 패턴의 가치는 **개별 능력이 아니라 합주 능력**에 있다.

---

## 요약

- **시나리오 제약**: 6개월 만에 출시, 12개월에 새 하드웨어, 양쪽에서 동일 동작 → 이식성이 최우선
- **Template Method**: 일반 로직(check)과 하드웨어 의존 로직(read) 분리 → 새 하드웨어는 read 한 줄만 구현
- **Observer + Listener**: UI/Scheduler/감지기 결합 해체 → 중앙 조정자를 시스템 외곽의 AlarmClock으로 변환
- **Bridge**: 애플리케이션 추상(TemperatureSensor)과 하드웨어 구현(TemperatureSensorImp) 분리 → 둘이 각자 변화
- **Abstract Factory**: StationToolkit으로 플랫폼 의존 코드를 단 한 줄로 압축 → 플랫폼 추가는 새 Toolkit 한 클래스
- **Proxy**: HiLoDataProxy가 정책(HiLoDataImp)과 메커니즘(PersistentImp)을 격리 → SRP 회복
- **패키지 구조와 ADP/DIP**: main을 root 패키지로 빼고, 인터페이스 패키지(WeatherStationComponent, wmsdata)를 분리 → 순환 의존 제거, 추상에 의존
- **현실의 양보**: NVRAM 수명 제약 → currentReading의 boolean 반환. 깨끗한 설계도 하드웨어 현실에 맞춰야 한다
- **어딘가는 선을 긋는다**: 모든 의존성에 팩토리를 두지는 않는다 → 변경 가능성과 비용을 평가해 결정
- **진정한 교훈**: 패턴의 가치는 개별 능력이 아니라 **합주 능력**에 있다. SOLID 원칙이 그 합주를 이끄는 지휘봉이다
