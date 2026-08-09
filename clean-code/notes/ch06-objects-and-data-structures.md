# Chapter 6: Objects and Data Structures (객체와 자료 구조)

## 핵심 질문

변수를 비공개(private)로 정의하면서도 왜 조회(get) 함수와 설정(set) 함수를 당연하게 공개(public)하는가? 객체와 자료 구조의 근본적인 차이는 무엇이며, 언제 어떤 것을 선택해야 하는가?

---

## 1. 자료 추상화

변수를 비공개로 정의하는 이유는 남들이 변수에 의존하지 않게 만들고 싶어서다. 충동이든 변덕이든, 변수 타입이나 구현을 맘대로 바꾸고 싶어서다. 그런데 수많은 프로그래머가 조회 함수와 설정 함수를 당연하게 공개해 비공개 변수를 외부에 노출한다.

### 구체적인 클래스 vs 추상적인 클래스

```java
// 나쁜 예 — 구체적인 Point 클래스: 구현을 외부로 노출
public class Point {
    public double x;
    public double y;
}
```

```java
// 좋은 예 — 추상적인 Point 클래스: 구현을 완전히 숨김
public interface Point {
    double getX();
    double getY();
    void setCartesian(double x, double y);
    double getR();
    double getTheta();
    void setPolar(double r, double theta);
}
```

추상적인 `Point` 인터페이스는 점이 직교좌표계를 사용하는지 극좌표계를 사용하는지 알 길이 없다. 둘 다 아닐지도 모른다. 그럼에도 불구하고 인터페이스는 자료 구조를 명백하게 표현한다. 더 나아가 클래스 메서드가 **접근 정책을 강제**한다 — 좌표를 읽을 때는 각 값을 개별적으로, 설정할 때는 두 값을 한꺼번에 설정해야 한다.

반면 구체적인 `Point` 클래스는 확실히 직교좌표계를 사용한다. 변수를 `private`으로 선언하더라도 각 값마다 조회/설정 함수를 제공한다면 구현을 외부로 노출하는 셈이다.

### 구체적인 Vehicle vs 추상적인 Vehicle

```java
// 나쁜 예 — 구체적인 Vehicle: 변수값을 읽어 반환할 뿐이라는 사실이 거의 확실
public interface Vehicle {
    double getFuelTankCapacityInGallons();
    double getGallonsOfGasoline();
}
```

```java
// 좋은 예 — 추상적인 Vehicle: 정보가 어디서 오는지 전혀 드러나지 않음
public interface Vehicle {
    double getPercentFuelRemaining();
}
```

> **핵심 통찰**: 자료를 세세하게 공개하기보다는 **추상적인 개념으로 표현**하는 편이 좋다. 인터페이스나 조회/설정 함수만으로는 추상화가 이뤄지지 않는다. 개발자는 객체가 포함하는 자료를 표현할 가장 좋은 방법을 심각하게 고민해야 한다. 아무 생각 없이 조회/설정 함수를 추가하는 방법이 가장 나쁘다.

---

## 2. 자료/객체 비대칭

객체와 자료 구조 사이에는 근본적인 차이가 있다:

| | 객체 | 자료 구조 |
|---|---|---|
| **자료** | 추상화 뒤로 숨긴다 | 그대로 공개한다 |
| **함수** | 자료를 다루는 함수만 공개한다 | 별다른 함수를 제공하지 않는다 |

이 두 정의는 본질적으로 **상반된다**. 사소한 차이로 보일지 모르지만 그 차이가 미치는 영향은 굉장하다.

### 절차적인 도형 (자료 구조 방식)

```java
public class Square {
    public Point topLeft;
    public double side;
}

public class Rectangle {
    public Point topLeft;
    public double height;
    public double width;
}

public class Circle {
    public Point center;
    public double radius;
}

public class Geometry {
    public final double PI = 3.141592653589793;

    public double area(Object shape) throws NoSuchShapeException {
        if (shape instanceof Square) {
            Square s = (Square) shape;
            return s.side * s.side;
        } else if (shape instanceof Rectangle) {
            Rectangle r = (Rectangle) shape;
            return r.height * r.width;
        } else if (shape instanceof Circle) {
            Circle c = (Circle) shape;
            return PI * c.radius * c.radius;
        }
        throw new NoSuchShapeException();
    }
}
```

`Geometry` 클래스에 `perimeter()` 함수를 추가하고 싶다면? **도형 클래스는 아무 영향도 받지 않는다.** 반대로 새 도형을 추가하고 싶다면? `Geometry` 클래스에 속한 함수를 **모두 고쳐야** 한다.

### 다형적인 도형 (객체 방식)

```java
public class Square implements Shape {
    private Point topLeft;
    private double side;

    public double area() {
        return side * side;
    }
}

public class Rectangle implements Shape {
    private Point topLeft;
    private double height;
    private double width;

    public double area() {
        return height * width;
    }
}

public class Circle implements Shape {
    private Point center;
    private double radius;
    public final double PI = 3.141592653589793;

    public double area() {
        return PI * radius * radius;
    }
}
```

새 도형을 추가해도 **기존 함수에 아무런 영향을 미치지 않는다.** 반면 새 함수를 추가하고 싶다면 **도형 클래스 전부를 고쳐야** 한다.(*노련한 객체 지향 설계자는 VISITOR 혹은 Dual-Patch 등의 기법을 사용해 이 문제를 해결한다. 하지만 이들 기법 역시 대가가 따르며, 일반적으로 절차적인 프로그램에서 볼 수 있는 구조를 반환한다.*)

### 절차적 코드 vs 객체 지향 코드 — 핵심 대칭

| | 새 함수 추가 | 새 자료 타입 추가 |
|---|---|---|
| **절차적 코드** (자료 구조) | 쉽다 — 기존 자료 구조 변경 없음 | 어렵다 — 모든 함수를 고쳐야 함 |
| **객체 지향 코드** | 어렵다 — 모든 클래스를 고쳐야 함 | 쉽다 — 기존 함수 변경 없음 |

> **핵심 통찰**: 객체 지향 코드에서 어려운 변경은 절차적인 코드에서 쉬우며, 절차적인 코드에서 어려운 변경은 객체 지향 코드에서 쉽다. **분별 있는 프로그래머는 모든 것이 객체라는 생각이 미신임을 잘 안다.** 때로는 단순한 자료 구조와 절차적인 코드가 가장 적합한 상황도 있다.

---

## 3. 디미터 법칙

디미터 법칙(Law of Demeter)은 잘 알려진 휴리스틱으로, **모듈은 자신이 조작하는 객체의 속사정을 몰라야 한다**는 법칙이다. 객체는 자료를 숨기고 함수를 공개한다 — 즉, 객체는 조회 함수로 내부 구조를 공개하면 안 된다.

좀 더 정확히 표현하자면, 디미터 법칙은 **"클래스 C의 메서드 f는 다음과 같은 객체의 메서드만 호출해야 한다"**고 주장한다:

- 클래스 C
- f가 생성한 객체
- f 인수로 넘어온 객체
- C 인스턴스 변수에 저장된 객체

위 객체에서 허용된 메서드가 **반환하는 객체**의 메서드는 호출하면 안 된다. 다시 말해, **낯선 사람은 경계하고 친구랑만 놀라**는 의미다.

### 기차 충돌 (Train Wreck)

```java
// 나쁜 예 — 기차 충돌: 디미터 법칙 위반
final String outputDir = ctxt.getOptions().getScratchDir().getAbsolutePath();
```

여러 객차가 한 줄로 이어진 기차처럼 보이기 때문에 **기차 충돌(train wreck)**이라 부른다. 일반적으로 조잡하다 여겨지는 방식이므로 피하는 편이 좋다.

```java
// 개선 — 분리
Options opts = ctxt.getOptions();
File scratchDir = opts.getScratchDir();
final String outputDir = scratchDir.getAbsolutePath();
```

이 코드가 디미터 법칙을 위반하는지 여부는 `ctxt`, `Options`, `ScratchDir`이 **객체인지 자료 구조인지**에 달렸다. 객체라면 내부 구조를 숨겨야 하므로 확실히 디미터 법칙을 위반한다. 자료 구조라면 당연히 내부 구조를 노출하므로 디미터 법칙이 적용되지 않는다.

```java
// 자료 구조라면 — 디미터 법칙 거론 불필요
final String outputDir = ctxt.options.scratchDir.absolutePath;
```

### 잡종 구조

절반은 객체, 절반은 자료 구조인 **잡종 구조**가 나오기도 한다. 잡종 구조는 중요한 기능을 수행하는 함수도 있고, 공개 변수나 공개 조회/설정 함수도 있다. 이런 구조는 **새로운 함수는 물론이고 새로운 자료 구조도 추가하기 어렵다** — 양쪽 세상에서 단점만 모아놓은 구조다. 프로그래머가 함수나 타입을 보호할지 공개할지 확신하지 못해 어중간하게 내놓은 설계에 불과하다.

### 구조체 감추기

만약 `ctxt`, `options`, `scratchDir`이 진짜 객체라면? 객체라면 내부 구조를 감춰야 한다. 그렇다면 임시 디렉터리의 절대 경로는 어떻게 얻어야 할까?

```java
// 방법 1 — ctxt 객체에 공개해야 하는 메서드가 너무 많아진다
ctxt.getAbsolutePathOfScratchDirectoryOption();

// 방법 2 — 자료 구조를 반환한다고 가정
ctxt.getScratchDirectoryOption().getAbsolutePath();
```

어느 방법도 썩 내키지 않는다. **ctxt가 객체라면 뭔가를 하라고 말해야지 속을 드러내라고 말하면 안 된다.** 절대 경로가 왜 필요할까? 같은 모듈 아래쪽 코드를 보면:

```java
String outFile = outputDir + "/" + className.replace('.', '/') + ".class";
FileOutputStream fout = new FileOutputStream(outFile);
BufferedOutputStream bos = new BufferedOutputStream(fout);
```

임시 파일을 생성하기 위한 목적이라는 사실이 드러난다. 그렇다면 ctxt 객체에 **임시 파일을 생성하라고 시키면** 된다:

```java
// 좋은 예 — 객체에게 행동을 요청
BufferedOutputStream bos = ctxt.createScratchFileStream(classFileName);
```

> **핵심 통찰**: 객체에게 맡기기에 적당한 임무로 보인다. `ctxt`는 내부 구조를 드러내지 않으며, 모듈에서 해당 함수는 자신이 몰라야 하는 여러 객체를 탐색할 필요가 없다. 따라서 디미터 법칙을 위반하지 않는다.

---

## 4. 자료 전달 객체 (DTO)

자료 구조체의 전형적인 형태는 공개 변수만 있고 함수가 없는 클래스다. 이런 자료 구조체를 **자료 전달 객체(Data Transfer Object, DTO)**라 한다. DTO는 데이터베이스와 통신하거나 소켓에서 받은 메시지의 구문을 분석할 때 굉장히 유용하다. 데이터베이스에 저장된 가공되지 않은 정보를 애플리케이션 코드에서 사용할 객체로 변환하는 일련의 단계에서 가장 처음으로 사용하는 구조체다.

### 빈(Bean) 구조

좀 더 일반적인 형태는 **빈(bean)** 구조다. 비공개 변수를 조회/설정 함수로 조작한다. 일종의 사이비 캡슐화로, 일부 OO 순수주의자나 만족시킬 뿐 별다른 이익을 제공하지 않는다.

```java
// 빈(bean) 구조 예제 — Address.java
public class Address {
    private String street;
    private String streetExtra;
    private String city;
    private String state;
    private String zip;

    public Address(String street, String streetExtra,
                   String city, String state, String zip) {
        this.street = street;
        this.streetExtra = streetExtra;
        this.city = city;
        this.state = state;
        this.zip = zip;
    }

    public String getStreet()      { return street;      }
    public String getStreetExtra()  { return streetExtra;  }
    public String getCity()         { return city;         }
    public String getState()        { return state;        }
    public String getZip()          { return zip;          }
}
```

### 활성 레코드 (Active Record)

활성 레코드는 DTO의 특수한 형태다. 공개 변수가 있거나 비공개 변수에 조회/설정 함수가 있는 자료 구조지만, 대개 `save`나 `find`와 같은 탐색 함수도 제공한다. 데이터베이스 테이블이나 다른 소스에서 자료를 직접 변환한 결과다.

불행히도 활성 레코드에 **비즈니스 규칙 메서드를 추가해 객체로 취급**하는 개발자가 흔하다. 하지만 이는 바람직하지 않다 — 자료 구조도 아니고 객체도 아닌 **잡종 구조**가 나오기 때문이다.

**해결책**: 활성 레코드는 **자료 구조로 취급**한다. 비즈니스 규칙을 담으면서 내부 자료를 숨기는 객체는 따로 생성한다. (여기서 내부 자료는 활성 레코드의 인스턴스일 가능성이 높다.)

---

## 5. 객체와 자료 구조 선택 기준

| 요구사항 | 적합한 방식 |
|---|---|
| 새로운 자료 타입을 추가하는 유연성이 필요 | **객체** (클래스 + 다형성) |
| 새로운 동작(함수)을 추가하는 유연성이 필요 | **자료 구조** + 절차적인 코드 |
| 외부에 자료를 숨기고 접근 정책을 강제 | **객체** |
| 단순한 데이터 전달/변환 | **자료 구조** (DTO, 활성 레코드) |

---

## 요약

- **자료 추상화**: 조회/설정 함수로 변수를 다룬다고 클래스가 되지 않는다. **추상 인터페이스를 제공해 사용자가 구현을 모른 채 자료의 핵심을 조작**할 수 있어야 진정한 클래스다
- **자료/객체 비대칭**: 절차적 코드는 새 함수 추가가 쉽고, 객체 지향 코드는 새 타입 추가가 쉽다 — 이 둘은 정반대이며 상호 보완적이다
- **디미터 법칙**: 모듈은 자신이 조작하는 객체의 속사정을 몰라야 한다. 기차 충돌을 피하고, **객체에게 행동을 요청**하라
- **잡종 구조를 피하라**: 절반은 객체, 절반은 자료 구조인 잡종은 양쪽의 단점만 모은 구조다
- **DTO와 활성 레코드**: 자료 구조로 취급하고, 비즈니스 로직을 담는 객체는 따로 생성하라
- **모든 것이 객체라는 생각은 미신이다** — 때로는 단순한 자료 구조와 절차적인 코드가 가장 적합하다

---

## 다른 챕터와의 관계

- **← Chapter 2 (의미 있는 이름)**: 추상화 수준에 맞는 이름 선택이 자료 추상화의 핵심이다
- **← Chapter 3 (함수)**: "한 가지를 제대로 한다"는 함수 원칙이 객체의 메서드 설계에도 동일하게 적용된다
- **→ Chapter 7 (오류 처리)**: 예외 클래스를 감싸기(wrapper) 클래스로 처리하는 기법은 경계 인터페이스를 캡슐화하는 패턴과 맥을 같이 한다
- **→ Chapter 8 (경계)**: `Map`을 `Sensors` 클래스로 감싸는 예제가 이 장의 자료 추상화 원칙을 경계 인터페이스에 적용한 것이다
- **→ Chapter 10 (클래스)**: 클래스 설계 원칙(SRP, 응집도)이 객체의 자료 은닉과 동작 공개 원칙을 확장한다
- **→ Chapter 11 (시스템)**: 시스템 수준의 관심사 분리가 객체와 자료 구조의 역할 분리를 더 큰 규모로 적용한 것이다
