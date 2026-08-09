# Chapter 26: The Main Component (메인 컴포넌트)

## 핵심 질문

모든 시스템에 존재하는 최초 진입점인 메인(Main) 컴포넌트는 클린 아키텍처에서 어떤 위치를 차지하며, 왜 "가장 지저분한 컴포넌트"라고 불리는가? 메인을 플러그인으로 바라보면 아키텍처에 어떤 이점이 생기는가?

---

## 1. 궁극적인 세부사항

모든 시스템에는 최소한 하나의 컴포넌트가 존재하고, 이 컴포넌트가 나머지 컴포넌트를 생성하고, 조정하며, 관리한다. 이것이 바로 **메인(Main) 컴포넌트**다.

메인 컴포넌트는 **궁극적인 세부사항**으로, 가장 낮은 수준의 정책이다. 메인은 시스템의 초기 진입점이다. 운영체제를 제외하면 어떤 것도 메인에 의존하지 않는다.

메인이 담당하는 역할은 다음과 같다:

| 역할 | 설명 |
|------|------|
| **팩토리와 전략 생성** | 모든 Factory, Strategy 및 시스템 전반의 기반 설비를 생성한다 |
| **의존성 주입** | DI 프레임워크를 이용해 의존성을 주입하는 일이 바로 메인에서 이뤄진다 |
| **제어권 위임** | 생성과 주입이 끝나면, 더 높은 수준을 담당하는 부분으로 제어권을 넘긴다 |

메인에 의존성이 일단 주입되고 나면, 메인은 의존성 주입 프레임워크를 사용하지 않고도 일반적인 방식으로 의존성을 분배할 수 있어야 한다.

> **핵심 통찰**: 메인을 지저분한 컴포넌트 중에서도 가장 지저분한 컴포넌트라고 생각하라. 메인은 클린 아키텍처에서 가장 바깥 원에 위치하는, 지저분한 저수준 모듈이다.

---

## 2. 움퍼스 사냥 게임 예제

최신 버전의 "움퍼스 사냥(Hunt the Wumpus)" 게임의 메인 컴포넌트를 살펴보자. 주목할 부분은 문자열을 로드하는 방법으로, 코드의 나머지 핵심 영역에서 구체적인 문자열을 알지 못하도록 만들었다는 점이다.

### 2.1 클래스 선언과 데이터 초기화

```java
public class Main implements HtwMessageReceiver {
    private static HuntTheWumpus game;
    private static int hitPoints = 10;
    private static final List<String> caverns = new ArrayList<>();
    private static final String[] environments = new String[] {
        "bright", "humid", "dry", "creepy", "ugly",
        "foggy", "hot", "cold", "drafty", "dreadful"
    };
    private static final String[] shapes = new String[] {
        "round", "square", "oval", "irregular", "long",
        "craggy", "rough", "tall", "narrow"
    };
    private static final String[] cavernTypes = new String[] {
        "cavern", "room", "chamber", "catacomb", "crevasse",
        "cell", "tunnel", "passageway", "hall", "expanse"
    };
    private static final String[] adornments = new String[] {
        "smelling of sulfur", "with engravings on the walls",
        "with a bumpy floor", "",
        "littered with garbage", "spattered with guano",
        "with piles of Wumpus droppings", "with bones scattered around",
        "with a corpse on the floor", "that seems to vibrate",
        "that feels stuffy", "that fills you with dread"
    };
```

모든 게임 환경에 대한 구체적인 문자열 데이터가 메인에 집중되어 있다. 고수준 정책은 이러한 세부사항을 알 필요가 없다.

### 2.2 main 함수

```java
public static void main(String[] args) throws IOException {
    game = HtwFactory.makeGame(
        "htw.game.HuntTheWumpusFacade", new Main());
    createMap();
    BufferedReader br =
        new BufferedReader(new InputStreamReader(System.in));
    game.makeRestCommand().execute();
    while (true) {
        System.out.println(game.getPlayerCavern());
        System.out.println("Health: " + hitPoints +
            " arrows: " + game.getQuiver());
        HuntTheWumpus.Command c = game.makeRestCommand();
        System.out.println(">");
        String command = br.readLine();
        if (command.equalsIgnoreCase("e"))
            c = game.makeMoveCommand(EAST);
        else if (command.equalsIgnoreCase("w"))
            c = game.makeMoveCommand(WEST);
        else if (command.equalsIgnoreCase("n"))
            c = game.makeMoveCommand(NORTH);
        else if (command.equalsIgnoreCase("s"))
            c = game.makeMoveCommand(SOUTH);
        else if (command.equalsIgnoreCase("r"))
            c = game.makeRestCommand();
        else if (command.equalsIgnoreCase("sw"))
            c = game.makeShootCommand(WEST);
        else if (command.equalsIgnoreCase("se"))
            c = game.makeShootCommand(EAST);
        else if (command.equalsIgnoreCase("sn"))
            c = game.makeShootCommand(NORTH);
        else if (command.equalsIgnoreCase("ss"))
            c = game.makeShootCommand(SOUTH);
        else if (command.equalsIgnoreCase("q"))
            return;
        c.execute();
    }
}
```

이 코드에서 주목할 점이 여러 가지 있다:

1. **HtwFactory를 사용한 게임 생성**: `"htw.game.HuntTheWumpusFacade"`라는 클래스 이름을 문자열로 전달한다. 클래스를 직접 참조하지 않으므로 해당 클래스에 대한 소스 코드 의존성이 없다.(*클래스를 직접 생성하지 않았으므로, 해당 클래스가 변경되더라도 Main을 다시 빌드할 필요가 없다.*) 이를 통해 해당 클래스에서 변경이 생겨도 메인을 재컴파일/재배포하지 않아도 된다.
2. **입력 스트림 생성, 메인 루프 처리, 입력 명령어 해석**은 모두 main 함수에서 처리하지만, **명령어를 실제로 처리하는 일은 다른 고수준 컴포넌트로 위임**한다.

### 2.3 지도 생성

```java
private static void createMap() {
    int nCaverns = (int) (Math.random() * 30.0 + 10.0);
    while (nCaverns-- > 0)
        caverns.add(makeName());
    for (String cavern : caverns) {
        maybeConnectCavern(cavern, NORTH);
        maybeConnectCavern(cavern, SOUTH);
        maybeConnectCavern(cavern, EAST);
        maybeConnectCavern(cavern, WEST);
    }
    String playerCavern = anyCavern();
    game.setPlayerCavern(playerCavern);
    game.setWumpusCavern(anyOther(playerCavern));
    game.addBatCavern(anyOther(playerCavern));
    game.addBatCavern(anyOther(playerCavern));
    game.addBatCavern(anyOther(playerCavern));
    game.addPitCavern(anyOther(playerCavern));
    game.addPitCavern(anyOther(playerCavern));
    game.addPitCavern(anyOther(playerCavern));
    game.setQuiver(5);
}
```

지도 생성 역시 main에서 처리한다. 요지는 **메인은 클린 아키텍처에서 가장 바깥 원에 위치하는, 지저분한 저수준 모듈**이라는 점이다. 메인은 고수준의 시스템을 위한 모든 것을 로드한 후, 제어권을 고수준의 시스템에게 넘긴다.

---

## 3. 메인은 플러그인이다

메인을 **애플리케이션의 플러그인**이라고 생각하자. 메인은 다음과 같은 역할을 수행하는 플러그인이다:

1. 초기 조건과 설정을 구성한다
2. 외부 자원을 모두 수집한다
3. 제어권을 애플리케이션의 고수준 정책으로 넘긴다

메인이 플러그인이므로 메인 컴포넌트를 애플리케이션의 설정별로 하나씩 두도록 하여 **둘 이상의 메인 컴포넌트**를 만들 수도 있다.

| 메인 플러그인 유형 | 용도 |
|-------------------|------|
| 개발용 메인 플러그인 | 개발 환경에 맞는 설정과 목 객체 사용 |
| 테스트용 메인 플러그인 | 테스트 환경에 맞는 설정 |
| 상용 메인 플러그인 | 실제 프로덕션 환경의 설정 |
| 국가별/고객별 메인 플러그인 | 배포 대상에 맞는 로캘과 설정 |

> **핵심 통찰**: 메인을 플러그인 컴포넌트로 여기고, 아키텍처 경계 바깥에 위치한다고 보면 설정 관련 문제를 훨씬 쉽게 해결할 수 있다.

---

## 요약

- **메인은 궁극적인 세부사항이다.** 가장 낮은 수준의 정책이며, 시스템의 초기 진입점이다. 운영체제를 제외하면 어떤 것도 메인에 의존하지 않는다.
- **가장 지저분한 컴포넌트다.** 모든 팩토리, 전략, 기반 설비를 생성하고, 의존성을 주입하며, 구체적인 세부사항(문자열, 설정값 등)을 알고 있다.
- **제어권을 고수준으로 위임한다.** 초기 설정이 끝나면 즉시 고수준 정책에게 제어권을 넘긴다.
- **메인은 애플리케이션의 플러그인이다.** 설정별로 여러 메인 컴포넌트를 만들 수 있으며, 이를 통해 개발/테스트/상용 환경을 유연하게 관리할 수 있다.
- **아키텍처 경계 바깥에 위치한다.** 메인을 플러그인으로 바라보면 설정 관련 문제를 훨씬 쉽게 해결할 수 있다.

---

## 다른 챕터와의 관계

- **Chapter 14 (컴포넌트 결합)**: 메인 컴포넌트는 의존성 화살표를 따라가면 가장 마지막에 위치한다. 메인이 새로 릴리스되더라도 나머지 컴포넌트는 영향을 받지 않는다는 사실은 컴포넌트 의존성 원칙의 직접적인 적용이다.
- **Chapter 22 (클린 아키텍처)**: 메인은 클린 아키텍처 다이어그램에서 가장 바깥쪽 원에 위치한다. 프레임워크, 드라이버, 세부사항이 존재하는 영역이며, 의존성은 항상 안쪽(고수준)을 향한다.
- **Chapter 25 (계층과 경계)**: 메인은 아키텍처 경계 바깥에 놓이는 가장 저수준의 컴포넌트다. 25장에서 논의한 경계 전략의 실질적인 종착점이 메인이다.
- **Chapter 27 (서비스)**: 서비스 기반 시스템에서도 각 서비스는 자체적인 메인 컴포넌트를 가질 수 있다. 메인의 플러그인 특성은 서비스 배포 전략과 직결된다.
