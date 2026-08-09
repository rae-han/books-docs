# Chapter 6: Refactoring (리팩터링)

## 핵심 질문

레거시 코드는 왜 수정이 두려운가? 코드 수정 비용을 낮추기 위해 어떤 리팩터링 기법을 활용할 수 있으며, 각 기법은 어떤 상황에서 적용해야 하는가?

---

## 1. 수정 공포와 변경 비용

기가 막힌 온라인 서비스 아이디어가 떠올랐다고 해보자. 아이디어를 실현하려면 소프트웨어를 만들어야 한다. 서비스가 완성되고 고객을 모으는 데 성공한다면 서비스는 생존한다. 이렇게 생존한 서비스는 시장에서 경쟁력을 유지하기 위해 지속해서 기능을 추가하고 변경 작업을 거친다. 어느덧 서비스를 개발한 지 5년이 흘렀다. 그리고 코드는 레거시가 되었다.

레거시(*Legacy - 오래되었지만 여전히 사용되고 있는 코드*)는 오래된 코드를 말한다. 이런 레거시를 바라보는 개발자의 감정이 좋지만은 않다. 레거시를 좋아하고 반기는 개발자는 흔치 않다. 아니 레거시를 싫어한다고 보는 게 맞다. 개발자는 레거시에 대해 많은 부담을 갖는다.

### 딥 다이브: 레거시에 대한 정의

레거시 시스템은 오래된 하드웨어에서만 동작하거나 현재는 사용되지 않은 기술로 만들어진 시스템을 말한다. 레거시 시스템은 최신 하드웨어에서 동작하지 않거나 새로운 기술을 적용하기 어렵다. 레거시 시스템을 구동할 하드웨어가 더 이상 생산되지 않으면 완전히 새로 만들어야 레거시 시스템을 변경할 수 있다.

반면에 레거시 코드는 단순히 예전 방식으로 만들어진 코드만을 지칭하는 것이 아니다. 테스트가 없는 코드를 레거시 코드로 부르기도 하고, 이전 버전의 프레임워크를 사용해서 개발한 코드를 의미하기도 한다. 심지어 남이 만든 코드를 레거시 코드라고 부르기도 한다. 레거시에 대한 정의가 무엇이든 간에 하나의 공통점이 있다. 그것은 바로 레거시는 **수정하기 어렵다**는 것이다.

### 1.1 레거시 코드의 흔한 특성

개발자는 왜 레거시에 부담을 느낄까? 다음은 레거시에서 나타나는 흔한 특성이다. 이런 특성은 개발자가 코드를 변경할 때 큰 부담을 주는데, 앞에서 봤던 응집도가 높고 결합도가 낮은 코드와는 반대되는 결과를 낳는다.

- 긴 클래스, 긴 메서드
- 복잡한 코드
- 이상한 이름
- 많은 중복
- 테스트 코드 없음

이런 특징은 코드 수정을 어렵게 만든다. 일단 코드를 분석하는 데 많은 노력이 들어간다. 이상한 이름과 긴 코드는 가독성을 떨어뜨리고 복잡한 if-else와 분산된 로직은 코드 추적을 어렵게 만든다.

### 1.2 변경에 대한 두려움과 악순환

이 상태에서 새로운 요구가 들어온다. 요구를 충족하려면 기존 코드를 분석해야 한다. 하지만 항상 그렇듯 일정상 여유가 없다. 코드를 완벽하게 이해하지 못한 상태에서 코드를 수정해야 한다. 테스트 코드도 없어서 수정한 코드가 기존 기능에 어떤 영향을 끼칠지도 알 수 없다.

당연히 이런 상황에서 기존 코드 수정은 매우 두려운 일이 된다. 오죽하면 "잘 동작하는 코드는 건들지 말라"는 말을 농담 반 진담 반으로 할까? 개발자는 잘 동작하는 코드는 건들지 않고 기존 코드에 새 코드를 덧댄다. 기존 코드를 복사해서 붙여넣기 한 다음 일부 코드만 수정하거나, if-else 블록 안에 새로운 if-else 블록을 중첩하는 식으로 말이다. 기존 메서드와 클래스는 최대한 유지하면서 그 안에 코드를 추가한다.

이런 작업은 코드를 더 길고 복잡하게 만든다. 중복된 코드도 늘어나고 이상한 이름도 그대로 사용한다. 결국 레거시 코드를 더 이해하기 어렵게 만든다. **악순환이 반복되고 레거시 수정에 대한 공포는 더욱 증폭된다.**

악순환은 개발 비용 증가로 이어진다. 마치 공공장소에 떨어져 있는 쓰레기와 같다. 공공장소의 모퉁이에 누군가가 음료컵을 버렸다고 하자. 이 쓰레기를 치우지 않으면 다른 사람도 같은 위치에 음료컵을 버리기 시작한다. 더 방치하면 담배꽁초 같은 다른 쓰레기도 추가된다. 1개였던 쓰레기는 어느 순간 쓰레기 더미로 바뀐다. 쓰레기가 1~2개일 때보다 쓰레기 더미를 치우는 게 힘들다. 비슷하게 코드 덧대기가 쌓여 누더기가 된 코드는 수정이 힘들다. 악순환이 지속될수록 코드 수정 비용은 점점 증가한다.

코드 수정이 힘든 레거시는 피하고 싶지만 우리는 누구나 레거시를 만난다. 10년 전에 만들어져 지금까지 운영 중인 시스템을 만날 때도 있고, 남들은 쓰지 않는 기술을 사용한 시스템을 만날 때도 있다. 하지만 이것만이 레거시가 아니다. 불과 몇 달 전에 내가 만든 코드도 레거시가 될 수 있다. 내가 만든 코드지만 수정하기 두렵다면 그게 바로 레거시다.

> **핵심 통찰**: 레거시를 수정한다는 것은 두려운 일이다.

### 딥 다이브: 레거시는 폄하 대상이 아니다

가끔 레거시 코드를 무시하는 개발자를 만날 때가 있다. 회사 코드가 최악이라거나 다시 만들면 그것보다 더 잘 만들 수 있다는 식으로 말이다. 물론 틀린 말이 아닐 수도 있지만, 이런 말을 하는 개발자 중 기존 코드를 더 낫게 개선할 수 있는 사람은 많지 않았다. 더 좋게 개선하지도 못하는데 새로 잘 만들 수 있을까?

복잡하고 수정하기 힘든 레거시 코드를 만나면 당연히 투덜댈 수 있다. 하지만 레거시는 폄하 대상이 아니다. 레거시가 있었기에 서비스가 굴러가고 수익이 난 것이다. 그리고 모든 코드에는 나름의 사정이 있다. 그러니 레거시를 만나면 다음처럼 생각해보자.

**"개선할 거리가 있다. 해보자!"**

---

## 2. 리팩터링

앞서 코드를 수정하기 어려워서 코드를 덧대고, 덧댄 코드가 많아지다 보니 코드 분석이 어려워진다고 언급했었다. 이처럼 코드를 덧대면서 수정 비용이 점점 증가하는 악순환을 막을 수 있는 해결 방법을 찾아야 한다. 코드 수정 비용을 낮추려면 결국 코드를 수정하기 쉬운 구조로 바꿔야 한다. 그 방법 중 하나가 리팩터링(*Refactoring*)이다.

리팩터링은 **외부로 드러나는 동작이나 기능을 변경하지 않고 내부 구조를 변경해서 재구성하는 기법**이다. 리팩터링은 새로운 기능을 추가하거나 기존 기능을 개선하지 않는다. 그래서 겉으로 드러나는 이점이 없다. 하지만 리팩터링을 하고 나면 장기적 관점에서 이점이 생긴다. 코드 가독성이 높아지고 리팩터링 이전보다 구현 변경과 확장이 용이해진다. 이러한 변화는 단기적으로는 수정 비용을 낮춰주고 장기적으로는 개발 비용을 줄여준다.

리팩터링에는 다양한 기법이 존재하는데 이 책에서는 기본적인 기법을 소개한다. 이외에 더 많은 기법과 과정이 궁금하면 마틴 파울러가 쓴 『리팩터링 2판』(한빛미디어, 2020)을 읽어보자.

### 딥 다이브: 리팩터링과 테스트

리팩터링은 기존 동작은 그대로 유지하면서 내부 구조를 바꾸는 기법이다. 내부 구현을 변경했는데 다르게 동작하면 안 되기 때문에 리팩터링을 하고 나면 기존과 동일하게 동작하는지 확인해야 한다. 코드를 수정할 때마다 수동으로 확인하다 보면 시간이 오래 걸리고 특정 조건에서의 검증을 놓치기 쉽다. 따라서 **테스트 코드를 사용해서 검증하는 게 좋다**.

물론 레거시 코드에 대한 테스트 코드를 만드는 게 쉽지는 않다. 그래도 테스트 코드를 만들기 위해 노력해야 한다. 일단 테스트 코드를 만들고 나면 리팩터링을 더욱 안전하게 진행할 수 있다. 테스트 코드를 만드는 데 들어가는 시간이 길게 느껴질 수 있지만 리팩터링으로 얻는 장기적인 효과가 더 크다면 시간을 들일 만한 가치가 있다.

경우에 따라 코드를 수정하지 않고서는 테스트 코드를 만들 수 없을 때도 있다. 테스트 코드 없이 리팩터링을 하면 부담될 것이다. 하지만 리팩터링을 하지 않는 것보다 하는 게 낫다. 테스트 코드를 만들지 못해도 리팩터링을 시도해야 한다. 현재의 위험을 회피하다 보면 미래에 더 큰 위험으로 다가오기 때문이다.

---

## 3. 미사용 코드 삭제

가장 쉽지만 가장 부담되는 리팩터링이 코드 삭제다. 삭제 대상이 될 수 있는 흔한 예가 **주석 처리된 코드**이다. 주석 처리된 코드는 지금 사용하지 않는 코드임이 분명하다. 소스 변경 내역을 보면 얼마나 오래전부터 사용하지 않고 있는지도 분명히 알 수 있다. 그런데도 다음과 같은 이유로 주석 처리된 코드를 삭제하지 못하는 개발자가 많다.

- 왜 주석 처리했는지 몰라서
- 나중에 다시 사용할지 몰라서

이런 이유로 삭제하기 두렵다면 해당 코드에 TODO 주석을 추가하자.

```java
// TODO 삭제 대상 2023-05-01 사용하지 않음
// someDeletingCode
// anyCode()
```

앞의 코드처럼 `TODO 삭제 대상 일자 이유` 형식의 주석을 추가하자. 여기서 일자는 TODO 주석을 추가한 날이다. 이렇게 삭제 대상 문구와 TODO 주석을 추가한 일자를 포함해서 주석을 달면 이후에 삭제할 마음을 먹는 데 도움이 된다. "삭제 대상" TODO를 검색한 다음 주석에 적힌 일자가 6개월이 지났다면 그동안 사용되지 않은 게 확실하다 보니 과감하게 삭제할 수 있다.

### 3.1 미사용 변수 삭제

사용하지 않는 변수 삭제도 가장 쉽게 할 수 있는 리팩터링이다. 개발 도구로 사용하지 않는 변수를 쉽게 확인할 수 있다. 변수가 많을수록 코드를 분석하는 데 더 많은 시간이 소요되므로 변수는 적을수록 좋다. 예를 들어 아래 코드처럼 특정 변수를 초기화하고 나서 해당 값을 사용하지 않는다면 초기화를 포함한 변수 선언 코드를 삭제해야 한다.

```java
private void someMethod() {
    int threshold = 100; // 이 줄을 삭제
    ... // 이후 메서드가 끝날 때까지 threshold 변수를 사용하지 않음
}
```

그런데 미사용 변수를 삭제할 때 주의할 점이 있다. 예를 들어 다음 코드를 보자.

```java
private void someMethod() {
    int threshold = calculateThreshold(); // 이 줄을 삭제하면 안 됨!
    ... // 이후 메서드가 끝날 때까지 threshold 변수를 사용하지 않음
}

private int calculateThreshold() {
    if (this.policy == NOT_THRESHOLD) {
        this.calculated = true;
        return -1;
    } else {
        return this.maxSize * 16;
    }
}
```

이 코드는 `calculateThreshold()` 메서드의 리턴 결과를 `threshold` 변수에 할당하는데 이후 `threshold` 변수를 사용하지 않는다. 그렇다고 해서 `threshold` 변수를 선언한 줄을 전부 삭제하면 안 된다. `calculateThreshold()` 메서드를 호출하는 과정에서 특정 상태값이 바뀌기 때문이다. 즉 `threshold` 변수는 사용하지 않더라도 `calculateThreshold()` 메서드는 실행해야 한다. 따라서 위 코드는 **변수 선언만 삭제해야지** `calculateThreshold()` 메서드를 호출하는 코드 자체를 삭제하면 안 된다.

사용하지 않는 파라미터, 사용하지 않는 메서드, 사용하지 않는 클래스 모두 삭제 대상이다. 메서드나 클래스 전체를 주석 처리하고 일정 기간이 지난 뒤에 삭제한다.

### 딥 다이브: 미사용 코드 삭제 시 주의 사항

메서드와 클래스를 삭제할 때는 리플렉션으로 접근하는 코드인지 확인해봐야 한다. 예를 들어 런타임에 호출할 객체와 메서드 이름을 데이터베이스에 저장하는 시스템이 있다고 해보자. 이런 시스템에서는 소스 파일만 뒤져서 해당 클래스를 사용하는 위치를 찾아내기 어렵다. 실수로 리플렉션으로 사용하고 있는 코드를 지우면 런타임에서 클래스나 메서드를 찾을 수 없다는 에러가 발생하는데, 이 에러를 확인하고 나서야 사용하고 있는 코드를 지웠다는 사실을 알게 된다.

---

## 4. 매직 넘버

다음 코드를 보자.

```java
if (NumberUtils.anyMatch(boilerType, 19, 20)) {
    return true;
}
```

이 코드는 `boilerType`이 19나 20 중 하나와 일치하는지를 검사한다. 여기서 문제가 되는 코드는 19와 20이다. 처음 업무를 맡아 코드를 읽으면 두 정숫값이 각각 무엇을 의미하는지 알 수 없기 때문이다. 흔히 이렇게 값을 갖는 숫자를 매직 넘버(*Magic Number*)라고 표현한다. 매직 넘버는 그 값이 무엇을 의미하는지 유추하기 어렵기 때문에 정확하게 코드 의미를 이해하려면 여러 다른 요소를 함께 분석해야 한다.

위 코드를 다음과 같이 변경하면 어떨까?

```java
if (NumberUtils.anyMatch(boilerType, GAS_BOILER, INDUSTRIAL_BOILER)) {
    return true;
}
```

이 코드를 보면 `boilerType`이 `GAS_BOILER`(가스 보일러)나 `INDUSTRIAL_BOILER`(산업용 보일러)인 경우 true를 리턴한다는 것을 이해할 수 있다. 19, 20과 같은 숫자가 아니라 이름을 사용했기에 코드 의미가 더 잘 드러난다. `GAS_BOILER`와 `INDUSTRIAL_BOILER`의 실제 값은 상수로 정의한다.

```java
public static final int GAS_BOILER = 19;
public static final int INDUSTRIAL_BOILER = 20;
```

열거 타입을 사용하면 관련 상수를 한곳에 모을 수도 있다.

```java
public enum BoilerType {
    GAS(19), INDUSTRIAL(20);

    private int code;

    BoilerType(int code) {
        this.code = code;
    }

    public int code() {
        return code;
    }
}
```

문자열로 된 매직 넘버(문자열)도 동일하게 상수나 열거 타입을 사용해서 이름을 부여하는 방법으로 특정 값의 의미를 드러낼 수 있다. 의미가 드러나는 이름을 사용하면 코드 가독성이 높아지고 분석 시간이 줄어든다.

### 딥 다이브: 이름에 코드 값 함께 쓰기

매직 넘버를 상수나 열거 타입으로 바꿔서 이름을 부여하면 의미가 잘 드러난다. 그런데 코드를 분석하다 보면 "그래서 GAS의 실제 값은 뭐지?"라는 생각이 들 때가 많다. 그럴 땐 선언 위치로 이동해서 값을 확인한다. 개발 도구에 따라 이름에 마우스 커서를 갖다 대면 선언 내용을 보여주기도 한다. 하지만 이름의 실제 값을 보기 위해 추가 행위를 하는 게 귀찮을 수 있다. 그래서 다음과 같이 이름 뒤에 실제 값을 포함해서 코드를 작성하기도 한다.

```java
public enum BoilerType {
    GAS_19(19), INDUSTRIAL_20(20);
}
```

호불호가 갈릴 방법이겠지만 운영할 때 값 자체와 값의 의미를 이름만으로 바로 알 수 있어서 코드를 분석하는 데 도움이 많이 됐다.

---

## 5. 이름 변경

보이는 이름과 실제 의미가 일치하지 않으면 코드를 분석할 때 혼란을 겪게 된다. 4장에서 언급한 코드를 다시 보자.

```java
List<Input> inputs = selectInput(inputList);
```

이름만 보면 `selectInput` 메서드는 어떤 것을 조회해서 리턴할 것 같다. 그런데 실제로는 데이터를 데이터베이스에 저장하고, 저장된 대상을 리턴하고 있다고 가정해보자. 코드를 분석하는 개발자는 `selectInput` 메서드의 구현 코드를 보기 전까지는 이 메서드가 데이터베이스에 데이터를 저장한다고 유추하지 못한다. `selectInput`을 `saveInput`으로 바꿔보자.

```java
List<Input> inputs = saveInput(inputList);
```

이제 메서드 이름만으로도 파라미터로 받은 값을 사용해서 저장한다는 사실을 유추할 수 있다. 만약 성공한 결과만 걸러서 저장하고, 저장한 목록을 리턴한다면 어떨까? `saveInput`만으로는 이 사실이 잘 드러나지 않는다. 이름을 한 번 더 바꿔보자.

```java
List<Input> savedInputs = filterAndSaveSuccessInput(inputList);
```

이름이 다소 길어졌는데 이름만으로도 성공한 결과만 추려서 저장한다는 것을 어느 정도 유추할 수 있다. 또한 기존에 `inputs`였던 변수 이름도 '저장된'이란 의미를 갖도록 `savedInputs`로 바꿨다. **이름은 짧을수록 좋지만 이름을 짧게 만들어 너무 많은 의미가 생략된다면 짧은 이름보다 차라리 긴 이름이 낫다.**

이름 변경은 가장 쉬우면서도 개발 도구가 가장 잘 지원하는 리팩터링이기도 하다. 의미가 잘 드러나지 않는 이름을 만나면 좀 더 알맞은 이름으로 변경하는 시도를 지속해보자. 그만큼 코드 가독성이 좋아진다.

### 딥 다이브: 이름 짓기

이름을 결정하는 과정은 언제나 힘들다. 코드는 영어로 작성하는데 모두가 영어를 완벽하게 잘 하는 건 아니므로 영어 단어를 잘못 선택하기도 한다. 우리말을 영어로 번역하는 과정은 힘듦을 넘어 고통스럽기도 하다. 그런데도 어쨌든 지금 알맞다고 생각되는 단어를 골라 사용해야 한다. 단어를 고르는 데 어려움이 있다면 시간을 많이 낭비하지 말고 일단 당장 생각나는 단어를 사용해서 구현하자. 대신 주석으로 어떤 의미인지 적어놓으면 된다. 이후 더 나은 단어가 떠오르면 그때 이름을 바꾸는 리팩터링을 하자.

다행인 점은 번역기가 점점 훌륭해지고 있다는 점이다. 한영 사전과 함께 번역기를 적극적으로 이름 짓는 데 활용하자.

---

## 6. 메서드 추출

이름 변경 다음으로 많이 활용하는 리팩터링은 메서드 추출이다. 메서드 추출을 잘 활용하면 코드 가독성이 높아진다.

```java
// 리팩터링 전
public void register(RegisterRequest req) {
    int sameIdCount = userRepository.countById(req.getId());
    if (sameIdCount > 0) throw new DupIdException();
    ...
}

// 리팩터링 후
public void register(RegisterRequest req) {
    checkSameIdExists(req.getId());
    ...
}

private void checkSameIdExists(String id) {
    int sameIdCount = userRepository.countById(id);
    if (sameIdCount > 0) throw new DupIdException();
}
```

메서드 추출은 관련 코드를 묶어서 별도 메서드로 추출하는 방법이다. 메서드 추출은 **논리적으로 하나의 작업을 수행하는 코드**를 대상으로 한다. 추출한 메서드에 알맞은 이름을 부여함으로써 가독성이 좋아지고, 관련 코드가 한 메서드에 모이면서 코드도 더 응집된다.

### 6.1 if-else 블록 추출

메서드를 추출하기 좋은 대상은 if-else의 각 블록에 있는 코드이다.

```java
// 리팩터링 전
if (req.isNoCheck()) {
    burner.changeNoCheck();
    safeCheckVisitAppender.appendCheckVisit(burner);
} else {
    String checkResult = CheckResultRule.decideResult(req.getCheckValues());
    CheckResult safeCheck = CheckResult.builder()
        .lastResult(checkResult)
        ... // 생략
        .build();
    burner.saveCheckResult(safeCheck);
    safeCheckVisitAppender.appendCheckVisit(burner);
}

// 리팩터링 후
if (req.isNoCheck()) {
    changeBurnerToNoCheck(burner);
} else {
    updateBurnerCheckResult(burner, req);
}
```

이 코드에서 if 블록은 검사를 하지 않았을 때(noCheck) 로직을 수행하고 else 블록은 검사를 했을 때의 로직을 수행한다. if 블록과 else 블록이 서로 다른 로직을 수행하기 때문에 각 블록을 별도 메서드로 추출하면 코드 구조를 개선할 수 있다.

### 6.2 과도한 메서드 추출 주의

메서드 추출 리팩터링의 매력에 빠져들면 코드가 길든 짧든 계속 메서드를 추출하고 싶은 욕구에 사로잡힐 수 있다. 하지만 무턱대고 메서드를 추출하면 안 된다. 가독성이나 응집도가 좋아지는 방향으로 메서드를 추출해야 한다. 과할 정도로 메서드 추출을 많이 하면 오히려 코드 분석이 어려워질 수도 있다. 조금은 부족해 보이더라도 메서드가 비교적 의미를 잘 드러내고, 코드를 자연스럽게 읽을 수 있다면 적정선에서 메서드 추출을 멈춰도 괜찮다.

### 딥 다이브: 메서드를 추출할 때 주의할 점

메서드 추출을 잘못하면 오히려 코드를 탐색하는 데 부담이 증가하고 가독성이 떨어지며 코드를 추적하기가 어려워질 수 있다. 이런 증상이 나타나는 주된 이유는 **메서드로 추출한 코드 블록이 개념적으로 구분되는 로직이 아니기 때문**이다. 이럴 때는 일단 추출한 메서드를 인라인(*Inline*)해서 원래 메서드로 다시 코드를 옮긴다. 그리고 코드를 분석해서 관련된 코드 묶음을 다시 찾아서 적절한 메서드로 추출해야 한다.

---

## 7. 클래스 추출

다음 코드에서 `provideServicePeriod()` 메서드는 로그인 일자를 기준으로 특정 주문의 서비스 기간을 알려주는 기능을 구현한 것이다.

```java
public void provideServicePeriod(Long ordNo, LocalDate loginDate) {
    Order order = getOrder(ordNo);
    Period period = null;
    if (order.getGubun().equals("A")) {
        ... // 생략
        period = Period.of(order.getOrderDate(), YearMonth.from(...));
    } else {
        if (order.getUnit().equals("D")) {
            ... // 생략 (order.getQuantity() 사용)
            period = Period.of(loginDate, ...);
        } else if (order.getUnit().equals("M")) {
            ... // 생략 (order.getQuantity() 사용)
            period = Period.of(loginDate, ...);
        }
    }
    updatePeriod(order.getNo(), period.getSdate(), period.getEdate());
}
```

중간에 Period를 구하는 코드가 있다. 실제로 Period를 구하는 로직이 30줄 이상 된다고 가정해보자. 메서드 추출로 리팩터링하면 다음과 같다.

```java
public void provideServicePeriod(Long ordNo, LocalDate loginDate) {
    Order order = getOrder(ordNo);
    Period period = calculatePeriod(order, loginDate);
    updatePeriod(order.getNo(), period.getSdate(), period.getEdate());
}

private Period calculatePeriod(Order order, LocalDate loginDate) {
    if (order.getGubun().equals("A")) {
        return calculatePeriodOfAOrder(order.getOrderDate());
    } else {
        if (order.getUnit().equals("D")) {
            return calculateDayPeriod(loginDate, order.getQuantity());
        } else {
            return calculateMonthPeriod(loginDate, order.getQuantity());
        }
    }
}
```

리팩터링한 코드는 `calculatePeriod` 메서드를 호출할 때 로컬 변수인 `order`와 파라미터로 전달받은 `loginDate`를 재전달하고 있다. `calculatePeriod()` 메서드 또한 내부에서 다른 메서드를 호출할 때 파라미터로 전달받은 order의 속성을 전달하거나 `loginDate` 파라미터를 재전달했다. 메서드 추출로 코드를 정리했지만 **파라미터 전달 관계가 복잡해졌다**.

또 하나 생각할 점은 Period를 구하는 로직은 `provideServicePeriod()` 메서드의 전체 로직 중 구분되는 일부 로직이라는 것이다. 이 메서드는 다음의 3가지 로직으로 구성되어 있다.

- Order를 구한다.
- Order와 loginDate를 이용해서 Period를 계산한다.
- Period를 수정한다.

여기서 Period를 계산하는 로직을 중첩된 메서드로 추출했다. 그런데 메서드를 중첩하여 추출하는 과정에서 파라미터로 값을 전달하는 과정이 복잡해졌다. 이렇게 된 이유는 로직을 구현한 코드가 길고 로컬 변수를 사용하기 때문이다. **이런 경우 메서드 추출 대신 클래스 추출을 고려해볼 수 있다.**

다음은 계산 로직을 별도 클래스로 분리한 예시이다. 계산에 필요한 `order`와 `loginDate`는 생성자를 통해 전달받아 해당 클래스의 필드에 보관된다.

```java
public class PeriodCalculator {
    private Order order;
    private LocalDate loginDate;

    public PeriodCalculator(Order order, LocalDate loginDate) {
        this.order = order;
        this.loginDate = loginDate;
    }

    public Period calculate() {
        if (order.getGubun().equals("A")) {
            ... // 생략
            return Period.of(order.getOrderDate(), YearMonth.from(...));
        } else {
            if (order.getUnit().equals("D")) {
                ... // 생략 (order.getQuantity() 사용)
                return Period.of(loginDate, ...);
            } else if (order.getUnit().equals("M")) {
                ... // 생략 (order.getQuantity() 사용)
                return Period.of(loginDate, ...);
            }
        }
    }
}
```

기존 코드는 분리한 클래스를 사용하면 된다.

```java
public void provideServicePeriod(Long ordNo, LocalDate loginDate) {
    Order order = getOrder(ordNo);
    Period period = new PeriodCalculator(order, loginDate).calculate();
    updatePeriod(order.getNo(), period.getSdate(), period.getEdate());
}
```

클래스로 추출한 `PeriodCalculator` 클래스의 `calculate()` 메서드를 다시 메서드 추출로 리팩터링하면 이전과 달리 추출한 메서드를 호출할 때 **파라미터로 전달하는 값이 없어** 코드가 이전보다 단순해진다.

```java
public class PeriodCalculator {
    private Order order;
    private LocalDate loginDate;
    ... // 생략

    public Period calculate() {
        if (order.getGubun().equals("A")) {
            return calculatePeriodOfAOrder();
        } else {
            if (order.getUnit().equals("D")) {
                return calculateDayPeriod();
            } else {
                return calculateMonthPeriod();
            }
        }
    }

    private Period calculatePeriodOfAOrder() {
        ... // 생략
        return Period.of(order.getOrderDate(), YearMonth.from(...));
    }

    private Period calculateDayPeriod() {
        ... // 생략 (order.getQuantity() 사용)
        return Period.of(loginDate, ...);
    }
}
```

> **핵심 통찰**: 로직을 클래스로 추출하면 해당 로직만 따로 테스트할 수 있는 이점도 생긴다.

---

## 8. 클래스 분리

한 클래스에 많은 기능이 모여 있으면 각 기능을 별도 클래스로 분리한다. 기능을 분리할 때는 한 번에 다 하기보다 **한 기능씩 점진적으로 진행**한다.

```java
public class MemberService {
    private MemberRepository repository;

    public void create(CreateRequest req) {
        ... // repository.save(member);
    }

    ... // 메서드 많음
}
```

`MemberService` 클래스는 `create()`를 포함한 회원과 관련된 많은 기능을 구현하고 있다. 한 클래스에 많은 기능이 모여 있으면 클래스가 커지면서 복잡도가 증가하고 코드 분석이 어려워진다. 이럴 땐 클래스의 기능 일부를 분리하면 복잡도를 낮추면서 코드 분석의 어려움을 낮출 수 있다.

```java
// create() 메서드를 별도 클래스로 분리
public class CreateMemberService {
    private MemberRepository repository;

    public void create(CreateRequest req) {
        ... // repository.save(member);
    }
}

// 기존 클래스에서 create() 메서드는 삭제
public class MemberService {
    private MemberRepository repository;
    // create() 메서드는 삭제함
    ... // 메서드 많음
}
```

`MemberService`의 `create()` 메서드를 호출했던 코드를 `CreateMemberService`의 `create()` 메서드를 호출하도록 변경한다. 클래스 추출과 마찬가지로 분리한 클래스는 코드 줄 수가 줄어들고 한 기능에 초점을 맞추고 있기 때문에 후속 리팩터링이 더 쉬워진다.

---

## 9. 메서드 분리

다음 코드를 보자.

```java
public void saveContractCancel(CancelDto dto) {
    if (dto.getConfirmYn().equals("Y")) {
        ... // 취소 확정 로직 코드
    } else if (!dto.getConfirmYn().equals("Y")) {
        ... // 취소 완료 로직 코드
    }
    if (dto.getConfirmYn().equals("Y")) {
        ... // 취소 확정 관련 후처리 로직
    }
}
```

이 코드에서 `saveContractCancel()` 메서드는 **취소 확정**과 **취소 완료**라는 서로 다른 기능을 구현하고 있다. 서로 다른 기능을 한 메서드에 구현하면 유사한 if-else가 곳곳에 생겨 코드가 복잡해지고 실행 흐름 추적이 어려워진다. 또한 이 상태에서 메서드 추출 같은 리팩터링을 하면 가독성은 개선되지 않고 구조만 더 복잡해질 수 있다.

이렇게 메서드가 완전히 구분되는 기능을 구현하고 있는 경우에는 각 기능을 구현하는 메서드를 따로 만들고 분리해서 기능별로 응집도를 높여야 한다.

### 메서드 분리 절차

메서드를 분리할 때는 다음 순서대로 진행한다.

| 단계 | 설명 |
|------|------|
| 1 | 두 기능 중 한 기능을 위한 메서드를 추가한다. 이 메서드는 내부에서 기존 메서드를 호출한다. |
| 2 | 기존 메서드를 호출하는 코드가 새 메서드를 호출하도록 변경한다. |
| 3 | 기존 메서드의 코드를 새 메서드로 이동한다. |
| 4 | 이름을 변경한다. |
| 5 | 코드를 정리한다. |

**1단계**: 확정 기능을 위한 메서드를 따로 만들고 이 메서드에서 기존 코드를 호출한다.

```java
// 확정 기능을 위한 메서드 추가
public void saveCancelConfirm(CancelDto dto) {
    this.saveContractCancel(dto); // 기존 메서드 호출
}
```

**2단계**: 기존 확정 API에서 호출하는 메서드를 변경한다.

```java
// 확정 API
// cancelService.saveContractCancel(dto); // 기존 코드 주석 처리
cancelService.saveCancelConfirm(dto); // 새 메서드 호출로 변경
```

**3단계**: 기존 메서드 코드를 새 메서드로 이동시킨다.

```java
public void saveCancelConfirm(CancelDto dto) {
    if (dto.getConfirmYn().equals("Y")) {
        ... // 취소 확정 로직 코드
    }
    if (dto.getConfirmYn().equals("Y")) {
        ... // 취소 확정 관련 후처리 로직
    }
}

public void saveContractCancel(CancelDto dto) {
    if (!dto.getConfirmYn().equals("Y")) {
        ... // 취소 완료 로직 코드
    }
}
```

**4단계**: 기존 메서드 이름을 변경한다.

```java
// saveContractCancel → saveCancelComplete로 변경
public void saveCancelComplete(CancelDto dto) {
    if (!dto.getConfirmYn().equals("Y")) {
        ... // 취소 완료 로직 코드
    }
}
```

**5단계**: 분리한 두 메서드에 분기 처리를 위한 코드가 남아 있는데 이 분기 처리 코드를 삭제하면 된다.

```java
public void saveCancelConfirm(CancelDto dto) {
    ... // 취소 확정 로직 코드
    ... // 취소 확정 관련 후처리 로직
}

public void saveCancelComplete(CancelDto dto) {
    ... // 취소 완료 로직 코드
}
```

메서드를 분리하고 이어서 클래스 분리 리팩터링을 해서 코드 응집도를 더 높일 수 있다.

---

## 10. 파라미터 값 정리

앞서 메서드 분리 리팩터링 예시에서 메서드 분리 결과를 다시 보자.

```java
public void saveCancelComplete(CancelDto dto) {
    ... // 취소 완료 로직 코드
}

public void saveCancelConfirm(CancelDto dto) {
    ... // 취소 확정 로직 코드
}
```

두 메서드의 파라미터 타입은 `CancelDto`로 같다. 하지만 `CancelDto`에서 두 메서드가 필요로 하는 데이터는 다르다. 또한 두 메서드에서 사용하지 않는 데이터도 있다. 예를 들어 코드를 정리하기 전 `saveCancelComplete()` 메서드는 `dto.getConfirmYn()` 메서드를 사용하는데 이 데이터는 `saveCancelComplete()` 메서드에서 더 이상 필요하지 않다.

**메서드에서 사용하지 않는 파라미터 데이터는 제거해야 한다.** 사용하지 않는 파라미터 값은 코드 분석을 어렵게 만들기 때문이다. 파라미터의 특정 값이 실제로 사용되는지 확인하려면 메서드 자체와 그 메서드가 같은 파라미터를 사용해서 호출하는 메서드까지 흐름에 따라 모든 코드를 뒤져야 한다. 한 타입을 여러 메서드에서 파라미터로 사용하거나, 같은 파라미터 타입이 메서드 호출 흐름대로 전파될수록 어떤 값을 사용하는지 확인하는 과정은 배로 어려워진다.

### 딥 다이브: 파라미터 값 정리

여러 메서드에서 한 타입을 파라미터로 사용하고 있다면, 메서드마다 알맞은 파라미터 타입을 추가한다. 이를 위한 과정은 다음과 같다.

1. 메서드 상단에 새 타입을 사용한 객체 생성
2. 메서드가 새 타입 객체를 사용할 때까지 다음 반복:
   - A. 메서드에서 사용하는 파라미터 프로퍼티를 새 타입 객체에 추가
   - B. 메서드에서 새 타입 객체의 프로퍼티를 사용하도록 변경
3. 새 타입 객체를 생성하는 부분을 뺀 나머지를 별도 public 메서드로 추출
4. 메서드 호출을 인라인 처리
5. 과정 3에서 추출한 메서드 이름을 원래 메서드 이름으로 변경

---

## 11. for에서 하는 2가지 일 분리

코드를 작성하다 보면 하나의 for 문에서 한 번에 여러 일을 처리하고 싶을 때가 있다. for 문을 두 번 실행하는 것보다 한 번만 실행하는 게 효율적으로 느껴지기도 한다.

```java
List<StoreApiDto> dtoList = new ArrayList<>();
List<InvoiceDto> invoices = mapper.selectRegularInvoices(cond);
for (InvoiceDto invoice : invoices) {
    try {
        ApprovalResp resp = payGwApi.approve(..);   // 결제 시도
        paymentService.saveAfterApproval(resp, ..);  // 결제 성공 결과 반영
        // 외부 API를 호출할 때 사용할 데이터 생성: 성공용 데이터
        StoreApiDto dto = ... // 성공 dto 생성
        dtoList.add(dto);
    } catch (Exception ex) {
        applyErrorResult(invoice, ex);  // 결제 실패 결과 반영
        StoreApiDto dto = ... // 실패 dto 생성
        dtoList.add(dto);
    }
}
if (dtoList.size() > 0) {
    callStoreApi(dtoList); // 외부 API 호출: 성공/실패 전달
}
```

이 코드는 각 청구(invoice) 목록을 구한 뒤, 각 청구에 대한 결제를 시도한다. 결제가 성공하면 성공 결과를 반영하고, 외부 시스템에 성공 결과를 전달할 때 사용할 `StoreApiDto` 객체를 생성해서 `dtoList`에 추가한다. 결제가 실패하면 실패 결과를 반영하고, 외부 시스템에 실패 결과를 전달할 때 사용할 `StoreApiDto` 객체를 생성해서 `dtoList`에 추가한다.

이 코드에서 for 문은 다음 **2가지 작업**을 하고 있다.

- 청구에 대한 결제 시도 후 성공/실패 결과 반영
- 외부 시스템에 전달할 StoreApiDto 객체 생성

여기에 결제 결과를 엑셀로 생성해서 메일로 발송해달라는 추가 요청이 들어왔다고 가정하자. 아마도 코드 사이사이에 엑셀 관련 코드가 추가될 것이다. 이렇게 하나의 for 문에서 여러 가지 작업을 실행하면 서로 다른 목적을 가진 코드가 뒤섞일 수 있다. 서로 다른 목적의 코드가 뒤섞이면 코드 복잡도가 증가하고 코드를 이해하기가 어려워진다.

### for 문 분리

for 문이 복잡해지지 않게 방지하는 방법의 하나는 **for 루프가 1개의 일만 하도록 수정**하는 것이다.

```java
List<InvoiceDto> invoices = mapper.selectRegularInvoices(cond);

// 결제 처리 및 결과 목록 생성
List<InvoiceResult> results = new ArrayList<>();
for (InvoiceDto invoice : invoices) {
    try {
        ApprovalResp resp = payGwApi.approve(..);   // 결제 시도
        paymentService.saveAfterApproval(resp, ..);  // 결제 성공 결과 반영
        results.add(InvoiceResult.ofSuccess(invoice, resp));
    } catch (Exception ex) {
        applyErrorResult(invoice, ex);  // 결제 실패 결과 반영
        results.add(InvoiceResult.ofFail(invoice, ex));
    }
}

// 외부 API를 호출할 때 필요한 StoreApiDto 생성
List<StoreApiDto> dtoList = new ArrayList<>();
for (InvoiceResult result : results) {
    if (result.isSuccess()) {
        StoreApiDto dto = ... // 성공 dto 생성
        dtoList.add(dto);
    } else {
        StoreApiDto dto = ... // 실패 dto 생성
        dtoList.add(dto);
    }
}
if (dtoList.size() > 0) {
    callStoreApi(dtoList); // 외부 API 호출: 성공/실패 전달
}
```

이 코드는 for 문을 2개로 분리했다. 첫 번째 for 문은 결제를 시도하고 결과를 생성한다. 두 번째 for 문은 결제 결과 목록을 이용해서 외부 API를 호출할 때 사용할 `StoreApiDto` 객체를 생성한다. 코드가 길어져서 더 복잡해 보일 수 있다. 하지만 이제 추상화 수준에 따라 메서드를 추출할 수 있다.

```java
List<InvoiceDto> invoices = mapper.selectRegularInvoices(cond);
// 결제 처리 및 결과 목록 생성
List<InvoiceResult> results = approveInvoices(invoices);
// 외부 시스템에 결제 결과 전송
sendInvoiceResultsToStore(results);
```

이제 결제 결과를 엑셀로 생성해서 담당자에게 전송하는 기능을 추가해보자. 해당 기능을 구현한 메서드를 만들고 호출하면 된다.

```java
List<InvoiceDto> invoices = mapper.selectRegularInvoices(cond);
// 결제 처리 및 결과 목록 생성
List<InvoiceResult> results = approveInvoices(invoices);
// 외부 시스템에 결제 결과 전송
sendInvoiceResultsToStore(results);
// 결과를 엑셀로 생성해서 담당자에 전송
sendInvoiceResultExcelToWorker(results);
```

for 문이 하는 일을 논리적인 단위로 분리한 덕분에 다음과 같은 이점이 생겼다.

- 코드가 복잡해지지 않고 논리적인 단위로 구분된다.
- 논리적인 단위로 구분되어 코드를 이해하기가 쉽다.
- 메서드 추출과 같은 리팩터링이 용이하다.
- 다른 로직을 추가하기가 용이하다.

루프를 한 번만 돌면 되는데 여러 번 돌게 되면 성능이 느려진다고 걱정하는 개발자도 있다. 하지만 미리 걱정할 필요는 없다. 대부분 성능에 문제가 없다. 정말로 문제가 될 때만 측정해서 개선하면 된다. 그리고 **복잡한 코드보다 이해하기 좋은 코드가 주는 이점이 훨씬 크다**.

---

## 12. 리팩터링 vs 새로 만들기

리팩터링은 기존 코드를 점진적으로 개선한다. 리팩터링으로 조금씩 코드를 개선하다 보면 어느새 코드 품질이 확연히 좋아진다. 하지만 코드 품질을 개선하는 방법이 리팩터링만 있는 것은 아니다. **새로 만드는 방법**도 있다.

새로 만드는 방법 중 하나는 일부 기능을 마이크로서비스(*Microservice*)로 분리하는 것이다. 일부 기능만 새로 만들기 때문에 전체를 새로 만드는 것보다 위험 부담이 적다. 단 프로세스가 분리되기 때문에 데이터 동기화나 통신 실패 같은 기존에 겪지 않았던 다른 문제에 직면할 수 있다. 새로 만들 때의 단점보다 이점이 더 클 때 개선의 방법으로 마이크로서비스를 선택해야 한다.

> **핵심 통찰**: 또한 새로 만든다고 코드가 좋아진다는 법은 없다. 좋은 코드를 만드는 방법을 알아야 코드 품질이 좋아진다. 이 사실을 꼭 기억하자.

---

## 요약

- 레거시 코드는 긴 클래스, 복잡한 코드, 이상한 이름, 많은 중복, 테스트 코드 부재 등의 특성을 가지며, 수정할수록 악순환이 반복되어 변경 비용이 증가한다
- 리팩터링은 외부 동작을 변경하지 않고 내부 구조를 재구성하는 기법으로, 단기적으로는 수정 비용을 낮추고 장기적으로는 개발 비용을 줄여준다
- **미사용 코드 삭제**: 주석 처리된 코드, 미사용 변수·메서드·클래스를 삭제한다. 부담되면 TODO 주석을 달고 일정 기간 뒤에 삭제한다
- **매직 넘버 제거**: 의미를 알 수 없는 숫자나 문자열을 상수 또는 열거 타입으로 바꿔 이름을 부여한다
- **이름 변경**: 보이는 이름과 실제 의미가 일치하도록 변경한다. 짧은 이름보다 의미가 드러나는 긴 이름이 낫다
- **메서드 추출**: 논리적으로 하나의 작업을 수행하는 코드를 별도 메서드로 추출하여 가독성과 응집도를 높인다
- **클래스 추출**: 메서드 추출 시 파라미터 전달이 복잡해지면 별도 클래스로 분리하여 필드로 상태를 공유한다
- **클래스 분리**: 한 클래스에 너무 많은 기능이 모여 있으면 기능별로 별도 클래스로 분리한다
- **메서드 분리**: 한 메서드가 서로 다른 기능을 구현하고 있으면 기능별로 메서드를 나눈다
- **파라미터 값 정리**: 메서드에서 사용하지 않는 파라미터 데이터를 제거하고, 메서드별로 알맞은 파라미터 타입을 사용한다
- **for 문 분리**: 하나의 for 문이 여러 작업을 수행하면 논리적 단위로 분리하여 코드 복잡도를 낮춘다
- 리팩터링이 유일한 개선 방법은 아니다. 일부 기능을 마이크로서비스로 분리하는 것도 방법이지만, 새로 만든다고 코드가 좋아지는 것은 아니다
