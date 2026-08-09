# Chapter 9: Unit Tests (단위 테스트)

## 핵심 질문

테스트 코드는 실제 코드 못지않게 중요한가? 깨끗한 테스트 코드를 작성하려면 어떤 원칙을 따라야 하며, 테스트 코드가 실제 코드의 유연성, 유지보수성, 재사용성에 어떤 영향을 미치는가?

---

## 1. 단위 테스트의 진화

1997년만 해도 TDD(Test Driven Development)라는 개념을 아무도 몰랐다. 대다수에게 단위 테스트란 자기 프로그램이 '돌아간다'는 사실만 확인하는 일회성 코드에 불과했다. 클래스와 메서드를 공들여 구현한 후 임시 코드를 급조해 테스트를 수행했는데, 대개는 간단한 드라이버 프로그램을 구현해 수동으로 실행했다.

> **Uncle Bob의 경험**: 90년대 중반, 임베디드 실시간 시스템에 들어갈 C++ 프로그램을 구현했다. 간단한 타이머 함수 `ScheduleCommand`를 테스트하기 위해 키보드로 입력 받는 간단한 드라이버 프로그램을 급조했다. 키를 누를 때마다 그 키를 출력하는 명령을 `ScheduleCommand`에 넘기고, 5초 후 가사가 출력되는 모습을 확인했다. 노래를 흥얼거리며 테스트했고, 돌아간다는 사실을 확인한 후 테스트 코드를 버렸다.

지금이라면 꼬치꼬치 따지며 코드가 제대로 도는지 확인하는 테스트 코드를 작성했을 것이다. 표준 타이밍 함수를 호출하는 대신 운영체제에서 코드를 분리하고, 타이밍 함수를 직접 구현해 시간을 완전히 통제했을 것이다.

애자일과 TDD 덕택에 단위 테스트를 자동화하는 프로그래머들이 이미 많아졌다. 하지만 급하게 서두르는 와중에 많은 프로그래머들이 **제대로 된 테스트 케이스를 작성해야 한다**는 좀 더 미묘한(그리고 더욱 중요한) 사실을 놓쳐버렸다.

---

## 2. TDD 법칙 세 가지

TDD가 실제 코드를 짜기 전에 단위 테스트부터 짜라고 요구한다는 사실은 빙산의 일각에 불과하다. 다음 세 가지 법칙을 따라야 한다:

| 법칙 | 내용 |
|---|---|
| **첫째 법칙** | 실패하는 단위 테스트를 작성할 때까지 실제 코드를 작성하지 않는다 |
| **둘째 법칙** | 컴파일은 실패하지 않으면서 실행이 실패하는 정도로만 단위 테스트를 작성한다 |
| **셋째 법칙** | 현재 실패하는 테스트를 통과할 정도로만 실제 코드를 작성한다 |

위 세 가지 규칙을 따르면 **개발과 테스트가 대략 30초 주기로 묶인다.** 테스트 코드와 실제 코드가 함께 나올뿐더러 테스트 코드가 실제 코드보다 불과 몇 초 전에 나온다.

이렇게 일하면 매일 수십 개, 매달 수백 개, 매년 수천 개에 달하는 테스트 케이스가 나온다. 실제 코드를 사실상 전부 테스트하는 테스트 케이스가 나온다. 하지만 실제 코드와 맞먹을 정도로 방대한 테스트 코드는 **심각한 관리 문제를 유발**하기도 한다.

---

## 3. 깨끗한 테스트 코드 유지하기

### 지저분한 테스트 코드의 악순환

테스트 코드에 실제 코드와 동일한 품질 기준을 적용하지 않기로 명시적으로 결정한 팀이 있었다. '지저분해도 빨리'가 주제어였다. 변수 이름은 신경 쓸 필요 없고, 테스트 함수는 간결하거나 서술적일 필요 없고, 테스트 코드는 잘 설계하거나 주의해서 분리할 필요 없었다. 그저 돌아만 가면 그만이었다.

하지만 결과는 다음과 같은 악순환이었다:

```
실제 코드 진화 → 테스트 코드도 변해야 함
    ↓
지저분한 테스트 코드 → 변경하기 어려움
    ↓
테스트 케이스 추가 시간 > 실제 코드 작성 시간
    ↓
테스트 코드가 가장 큰 불만으로 자리잡음
    ↓
테스트 슈트 폐기
    ↓
수정한 코드가 제대로 도는지 확인할 방법 없음
    ↓
결함율 상승 → 변경 주저 → 코드 정리 중단
    ↓
코드 망가짐 + 테스트에 쏟은 노력 허사
```

> **핵심 통찰**: 실패를 초래한 원인은 테스트 코드를 막 짜도 좋다고 허용한 결정이었다. 테스트 코드를 깨끗하게 짰다면 테스트에 쏟아 부은 노력은 허사로 돌아가지 않았을 것이다.

### 교훈

**테스트 코드는 실제 코드 못지않게 중요하다.** 테스트 코드는 이류 시민이 아니다. 테스트 코드는 사고와 설계와 주의가 필요하다. 실제 코드 못지않게 깨끗하게 짜야 한다.

### 테스트는 유연성, 유지보수성, 재사용성을 제공한다

코드에 유연성, 유지보수성, 재사용성을 제공하는 버팀목이 바로 **단위 테스트**다. 이유는 단순하다:

- 테스트 케이스가 있으면 **변경이 두렵지 않다**
- 테스트 케이스가 없다면 **모든 변경이 잠정적인 버그**다
- 테스트 커버리지가 높을수록 **공포는 줄어든다**
- 아키텍처가 부실한 코드라도 **별다른 우려 없이 변경**할 수 있다
- 오히려 안심하고 **아키텍처와 설계를 개선**할 수 있다

따라서 테스트 코드가 지저분하면 코드를 변경하는 능력이 떨어지며 코드 구조를 개선하는 능력도 떨어진다. 테스트 코드가 지저분할수록 실제 코드도 지저분해진다.

---

## 4. 깨끗한 테스트 코드

깨끗한 테스트 코드를 만들려면 세 가지가 필요하다: **가독성, 가독성, 가독성.** 어쩌면 가독성은 실제 코드보다 테스트 코드에 더더욱 중요하다. 테스트 코드에서 가독성을 높이려면 명료성, 단순성, 풍부한 표현력이 필요하다. **최소의 표현으로 많은 것을 나타내야 한다.**

### 나쁜 예 — 자질구레한 사항이 너무 많은 테스트

```java
public void testGetPageHieratchyAsXml() throws Exception {
    crawler.addPage(root, PathParser.parse("PageOne"));
    crawler.addPage(root, PathParser.parse("PageOne.ChildOne"));
    crawler.addPage(root, PathParser.parse("PageTwo"));

    request.setResource("root");
    request.addInput("type", "pages");
    Responder responder = new SerializedPageResponder();
    SimpleResponse response =
        (SimpleResponse) responder.makeResponse(
            new FitNesseContext(root), request);
    String xml = response.getContent();

    assertEquals("text/xml", response.getContentType());
    assertSubString("<name>PageOne</name>", xml);
    assertSubString("<name>PageTwo</name>", xml);
    assertSubString("<name>ChildOne</name>", xml);
}
```

`PathParser` 호출은 테스트와 무관하며 테스트 코드의 의도만 흐린다. `responder` 객체를 생성하는 코드와 `response`를 수집해 변환하는 코드 역시 잡음에 불과하다.

### 좋은 예 — BUILD-OPERATE-CHECK 패턴

```java
public void testGetPageHierarchyAsXml() throws Exception {
    makePages("PageOne", "PageOne.ChildOne", "PageTwo");

    submitRequest("root", "type:pages");

    assertResponseIsXML();
    assertResponseContains(
        "<name>PageOne</name>", "<name>PageTwo</name>", "<name>ChildOne</name>"
    );
}

public void testSymbolicLinksAreNotInXmlPageHierarchy() throws Exception {
    WikiPage page = makePage("PageOne");
    makePages("PageOne.ChildOne", "PageTwo");
    addLinkTo(page, "PageTwo", "SymPage");

    submitRequest("root", "type:pages");

    assertResponseIsXML();
    assertResponseContains(
        "<name>PageOne</name>", "<name>PageTwo</name>", "<name>ChildOne</name>"
    );
    assertResponseDoesNotContain("SymPage");
}

public void testGetDataAsXml() throws Exception {
    makePageWithContent("TestPageOne", "test page");

    submitRequest("TestPageOne", "type:data");

    assertResponseIsXML();
    assertResponseContains("test page", "<Test");
}
```

**BUILD-OPERATE-CHECK** 패턴이 적합하다. 각 테스트는 명확히 세 부분으로 나뉜다:

| 단계 | 역할 | 예시 |
|---|---|---|
| **Build** | 테스트 자료를 만든다 | `makePages(...)` |
| **Operate** | 테스트 자료를 조작한다 | `submitRequest(...)` |
| **Check** | 조작한 결과가 올바른지 확인한다 | `assertResponseIsXML()` |

잡다하고 세세한 코드를 거의 다 없앴다. 테스트 코드는 본론에 돌입해 진짜 필요한 자료 유형과 함수만 사용한다.

---

## 5. 도메인에 특화된 테스트 언어 (DSL)

위 예제는 **도메인에 특화된 언어(DSL)**로 테스트 코드를 구현하는 기법을 보여준다. 흔히 쓰는 시스템 조작 API를 사용하는 대신 API 위에다 함수와 유틸리티를 구현한 후 그 함수와 유틸리티를 사용한다. 테스트 코드를 짜기도 읽기도 쉬워진다.

이런 테스트 API는 처음부터 설계된 API가 아니다. 잡다하고 세세한 사항으로 범벅된 코드를 **계속 리팩터링하다가 진화된 API**다.

---

## 6. 이중 표준

테스트 API 코드에 적용하는 표준은 실제 코드에 적용하는 표준과 확실히 다르다. 단순하고, 간결하고, 표현력이 풍부해야 하지만, **실제 코드만큼 효율적일 필요는 없다.** 실제 환경이 아니라 테스트 환경에서 돌아가는 코드이기 때문이다.

### 나쁜 예 — 상태 확인이 흩어져 읽기 어려운 테스트

```java
@Test
public void turnOnLoTempAlarmAtThreashold() throws Exception {
    hw.setTemp(WAY_TOO_COLD);
    controller.tic();
    assertTrue(hw.heaterState());
    assertTrue(hw.blowerState());
    assertFalse(hw.coolerState());
    assertFalse(hw.hiTempAlarm());
    assertTrue(hw.loTempAlarm());
}
```

상태 이름과 상태 값을 확인하느라 눈길이 이리저리 흩어진다. 따분하고 미덥잖다.

### 좋은 예 — 간결한 상태 문자열로 가독성 극대화

```java
@Test
public void turnOnLoTempAlarmAtThreshold() throws Exception {
    wayTooCold();
    assertEquals("HBchL", hw.getState());
}
```

대문자는 '켜짐(on)', 소문자는 '꺼짐(off)'을 뜻한다. 문자는 항상 `{heater, blower, cooler, hi-temp-alarm, lo-temp-alarm}` 순서다. 비록 "그릇된 정보를 피하라"는 규칙의 위반에 가깝지만, 여기서는 적절해 보인다. 일단 의미만 안다면 결과를 재빨리 판단한다.

```java
@Test
public void turnOnCoolerAndBlowerIfTooHot() throws Exception {
    tooHot();
    assertEquals("hBChl", hw.getState());
}

@Test
public void turnOnHeaterAndBlowerIfTooCold() throws Exception {
    tooCold();
    assertEquals("HBchl", hw.getState());
}

@Test
public void turnOnHiTempAlarmAtThreshold() throws Exception {
    wayTooHot();
    assertEquals("hBCHl", hw.getState());
}

@Test
public void turnOnLoTempAlarmAtThreshold() throws Exception {
    wayTooCold();
    assertEquals("HBchL", hw.getState());
}
```

`getState` 함수 구현을 보면 효율적이지 못하다 — `StringBuffer`가 더 적합하다:

```java
public String getState() {
    String state = "";
    state += heater ? "H" : "h";
    state += blower ? "B" : "b";
    state += cooler ? "C" : "c";
    state += hiTempAlarm ? "H" : "h";
    state += loTempAlarm ? "L" : "l";
    return state;
}
```

`StringBuffer`는 보기에 흉하다. 테스트 환경은 자원이 제한적일 가능성이 낮으므로, `String` 연결로 인한 성능 저하는 미미하다.

> **핵심 통찰**: 이것이 **이중 표준의 본질**이다. 실제 환경에서는 절대로 안 되지만 테스트 환경에서는 전혀 문제없는 방식이 있다. 대개 메모리나 CPU 효율과 관련 있는 경우다. 코드의 깨끗함과는 철저히 무관하다.

---

## 7. 테스트 당 assert 하나

함수마다 assert 문을 단 하나만 사용해야 한다고 주장하는 학파가 있다. 가혹한 규칙이지만 확실히 장점이 있다 — assert 문이 단 하나인 함수는 결론이 하나라서 코드를 이해하기 쉽고 빠르다.

### given-when-then 관례

```java
public void testGetPageHierarchyAsXml() throws Exception {
    givenPages("PageOne", "PageOne.ChildOne", "PageTwo");
    whenRequestIsIssued("root", "type:pages");
    thenResponseShouldBeXML();
}

public void testGetPageHierarchyHasRightTags() throws Exception {
    givenPages("PageOne", "PageOne.ChildOne", "PageTwo");
    whenRequestIsIssued("root", "type:pages");
    thenResponseShouldContain(
        "<name>PageOne</name>", "<name>PageTwo</name>", "<name>ChildOne</name>"
    );
}
```

테스트를 분리하면 코드 읽기가 쉬워지지만 **중복되는 코드가 많아진다.** `TEMPLATE METHOD` 패턴을 사용하면 중복을 제거할 수 있지만, 배보다 배꼽이 더 크다.

**결론**: '단일 assert 문'이라는 규칙은 훌륭한 지침이지만, 때로는 주저 없이 함수 하나에 여러 assert 문을 넣기도 한다. 단지 **assert 문 개수는 최대한 줄여야 좋다**는 생각이다.

---

## 8. 테스트 당 개념 하나

"테스트 함수마다 **한 개념만 테스트하라**"는 규칙이 더 낫다. 이것저것 잡다한 개념을 연속으로 테스트하는 긴 함수는 피한다.

### 나쁜 예 — 한 함수에 여러 개념

```java
public void testAddMonths() {
    SerialDate d1 = SerialDate.createInstance(31, 5, 2004);

    // 개념 1: 31일로 끝나는 달에 한 달을 더하면 → 30일
    SerialDate d2 = SerialDate.addMonths(1, d1);
    assertEquals(30, d2.getDayOfMonth());
    assertEquals(6, d2.getMonth());
    assertEquals(2004, d2.getYYYY());

    // 개념 2: 31일로 끝나는 달에 두 달을 더하면 → 31일
    SerialDate d3 = SerialDate.addMonths(2, d1);
    assertEquals(31, d3.getDayOfMonth());
    assertEquals(7, d3.getMonth());
    assertEquals(2004, d3.getYYYY());

    // 개념 3: 30일로 끝나는 달에 한 달을 더하면 → 30일
    SerialDate d4 = SerialDate.addMonths(1, SerialDate.addMonths(1, d1));
    assertEquals(30, d4.getDayOfMonth());
    assertEquals(7, d4.getMonth());
    assertEquals(2004, d4.getYYYY());
}
```

독자적인 개념 세 개를 테스트하므로 독자적인 테스트 세 개로 쪼개야 마땅하다. 장황한 테스트 코드 속에 감춰진 일반적인 규칙이 보인다: **날짜에 어떤 달을 더하면 날짜는 그 달의 마지막 날짜보다 커지지 못한다.**

> **핵심 통찰**: 한 테스트 함수에서 여러 개념을 테스트한다는 사실이 문제다. 가장 좋은 규칙은 **"개념 당 assert 문 수를 최소로 줄여라"**와 **"테스트 함수 하나는 개념 하나만 테스트하라"**라 하겠다.

---

## 9. F.I.R.S.T. — 깨끗한 테스트의 다섯 가지 규칙

깨끗한 테스트는 다음 다섯 가지 규칙을 따른다:

| 규칙 | 설명 |
|---|---|
| **F**ast (빠르게) | 테스트는 빨리 돌아야 한다. 느리면 자주 돌릴 엄두를 못 내고, 초반에 문제를 찾아내지 못하며, 코드 품질이 망가지기 시작한다 |
| **I**ndependent (독립적으로) | 각 테스트는 서로 의존하면 안 된다. 한 테스트가 다음 테스트 환경을 준비해서는 안 된다. 어떤 순서로 실행해도 괜찮아야 한다 |
| **R**epeatable (반복가능하게) | 테스트는 어떤 환경에서도 반복 가능해야 한다 — 실제 환경, QA 환경, 네트워크 없는 노트북에서도. 환경 탓으로 돌릴 변명이 없어야 한다 |
| **S**elf-Validating (자가검증하는) | 테스트는 부울(bool) 값으로 결과를 내야 한다 — 성공 아니면 실패. 로그 파일을 읽거나 텍스트 파일 두 개를 수작업으로 비교하게 만들면 안 된다 |
| **T**imely (적시에) | 단위 테스트는 실제 코드를 구현하기 **직전에** 구현한다. 실제 코드를 먼저 구현하면 테스트하기 어렵다는 사실을 발견할지 모르며, 테스트가 불가능하도록 실제 코드를 설계할지도 모른다 |

---

## 요약

- **테스트 코드는 실제 코드 못지않게 중요하다** — 이류 시민이 아니며, 사고와 설계와 주의가 필요하다
- **TDD 법칙 세 가지**: 실패하는 테스트 먼저, 실행 실패 정도만 테스트, 통과할 정도만 코드
- **지저분한 테스트 코드는 테스트가 없는 것보다 못하다** — 테스트 코드 관리 비용이 폭증하고 결국 폐기하게 된다
- **테스트는 유연성, 유지보수성, 재사용성을 제공**한다 — 테스트 케이스가 있으면 변경이 두렵지 않다
- 깨끗한 테스트의 핵심은 **가독성** — BUILD-OPERATE-CHECK 패턴, 도메인 특화 테스트 언어(DSL)를 활용하라
- **이중 표준**: 테스트 코드는 실제 코드만큼 효율적일 필요 없지만, 깨끗해야 한다
- **테스트 당 개념 하나** — assert 문 개수를 최소로, 한 테스트 함수는 한 개념만
- **F.I.R.S.T. 규칙**: 빠르게, 독립적으로, 반복 가능하게, 자가검증하는, 적시에
- 테스트 코드가 방치되어 망가지면 **실제 코드도 망가진다**

---

## 다른 챕터와의 관계

- **← Chapter 1 (깨끗한 코드)**: 데이브 토마스가 단언한 "테스트 케이스가 없는 코드는 깨끗한 코드가 아니다"를 구체적으로 다룬 장이다
- **← Chapter 3 (함수)**: 테스트 함수도 "한 가지만 한다" 원칙을 따라야 한다 — 테스트 당 개념 하나
- **← Chapter 7 (오류 처리)**: try-catch-finally 문을 TDD로 구현하는 방식이 이 장의 테스트 작성 전략과 연결된다
- **← Chapter 8 (경계)**: 학습 테스트가 단위 테스트의 한 형태이며, 외부 API의 호환성을 검증하는 역할을 한다
- **→ Chapter 12 (창발성)**: 론 제프리스의 단순한 코드 규칙 중 첫째인 "모든 테스트를 통과한다"가 창발적 설계의 출발점이다
- **→ Chapter 17 (냄새와 휴리스틱)**: [T1]~[T9] 테스트 관련 냄새 항목이 이 장의 원칙을 코드 리뷰 체크리스트로 정리한 것이다
