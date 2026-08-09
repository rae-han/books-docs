# Chapter 5: Cohesion and Coupling (응집도와 결합도)

## 핵심 질문

응집도와 결합도는 무엇이며, 왜 높은 응집도와 낮은 결합도를 추구해야 하고, 이를 달성하기 위한 구체적 방법은 무엇인가?

---

## 1. 응집도와 결합도 개요

설계, 패턴, 아키텍처 등을 공부하다 보면 다음 2가지 용어를 자주 만나게 된다:

- **응집도**(*Cohesion*)
- **결합도**(*Coupling*)

이 둘은 컴퓨터 프로그래밍에서 중요한 단어다. 코드 수준부터 상위 아키텍처까지 모든 위치에서 두 용어가 나타난다. 좋은 코드, 좋은 설계, 패턴, 아키텍처는 **높은 응집도와 낮은 결합도**를 추구한다.

### 딥 다이브: 응집도와 결합도 이해의 어려움

개발하다 보면 응집도와 결합도에 대해 필연적으로 들을 수밖에 없다. 자주 듣는 용어이지만 이 둘은 여전히 어렵다. 저자 역시 이 책에서 응집도와 결합도를 완벽하게 설명하지는 못한 것 같다고 밝힌다. 그래도 이 둘이 무엇인지 전달하기 위해 노력했으니, 이 장에서 응집도와 결합도에 대한 감을 잡고 각자 더 학습해서 본인만의 지식으로 쌓길 바란다.

---

## 2. 응집도

응집도의 정의를 발췌하면 다음과 같다:

> 응집도는 모듈 안에 있는 요소가 함께 모여 있는 정도를 나타낸다.
> 응집도는 한 모듈의 파트가 동일한 모듈 안에 얼마나 포함되어 있는지를 나타낸다.

두 정의에 따르면 응집도는 **관련 요소가 얼마나 한 모듈에 모여 있는지**를 나타낸다. 작게는 메서드·함수 수준부터 크게는 프로세스 수준에 이르기까지 모든 수준에서 응집도를 판단할 수 있다:

- 회원 관련 코드가 한 패키지(또는 한 모듈)에 모여 있는가?
- 스택 관련 코드가 한 클래스에 모여 있는가?
- 폼 검증 로직이 한 함수에 모여 있는가?

관련 코드가 한 곳에 모여 있으면 **응집도가 높다**고 표현하고, 반대로 관련 코드가 여러 곳에 분산되어 있으면 **응집도가 낮다**고 표현한다.

### 2.1 패키지 수준의 응집도

예를 들어 계약 관련 기능이 contract 패키지에 모여 있지 않고 contract 패키지와 member 패키지에 흩어져 있다면 응집도가 낮다. 계약 기능에 변경이 생기면 contract 패키지뿐 아니라 member 패키지도 수정해야 한다. 응집도를 높이려면 계약 관련 코드를 담고 있는 ContractService를 contract 패키지로 옮겨야 한다.

한 기능과 관련된 코드는 한 곳에 모여 있어야 한다. 반대로 구분되는 기능은 서로 다른 곳에 분리되어야 한다. 예를 들어 MemberService가 회원 가입, 회원 정보 변경, 암호 변경, 회원 탈퇴 등의 기능을 구현하면 서로 목적이 다른 코드가 한 클래스에 뒤섞여서 응집도가 떨어진다. 응집도를 높이려면 기능별로 클래스를 분리해야 한다:

| 기능 | 분리된 클래스 |
|---|---|
| 회원 가입 | MemberRegisterService |
| 암호 변경 | ChangePasswordService |
| 회원 승인 | MemberApprovalService |

### 2.2 코드 수준의 응집도

다음 코드를 보자:

```java
public void save(SaveRequest req) {
    if (!StringUtils.hasText(req.getId()))
        throw new IllegalArgumentException("id는 필수");
    if (!StringUtils.hasText(req.getName()))
        throw new IllegalArgumentException("name은 필수");
    if (!StringUtils.hasText(req.getEmail()))
        throw new IllegalArgumentException("email은 필수");
    Long seq = repository.createSeq();
    Member member = Member.builder()
        .seq(seq)
        .id(req.getId()).name(req.getName()).email(req.getEmail())
        .createdAt(LocalDateTime.now())
        .build();
    repository.save(member);
}
```

이 메서드는 회원 저장과 관련된 모든 코드를 포함하고 있어 응집도가 높다고 생각할 수 있다. 하지만 코드 수준에서 보면 서로 다른 역할을 하는 코드가 섞여 있다: 값을 검증하는 코드, Member 객체를 생성하는 코드, 저장하는 코드. 응집도를 높이려면 서로 다른 역할을 하는 코드를 **별도 메서드로 분리**하면 된다:

```java
public void save(SaveRequest req) {
    validateRequest(req);
    // ... 생략
}

// 값 검증과 관련된 코드만 한 곳에 모았다
private void validateRequest(SaveRequest req) {
    if (!StringUtils.hasText(req.getId()))
        throw new IllegalArgumentException("id는 필수");
    if (!StringUtils.hasText(req.getName()))
        throw new IllegalArgumentException("name은 필수");
    if (!StringUtils.hasText(req.getEmail()))
        throw new IllegalArgumentException("email은 필수");
}
```

메서드 추출을 잘 활용하면 코드 가독성을 높이면서 응집도도 함께 높일 수 있다.

### 2.3 왜 응집도를 높여야 하는가

응집도는 결국 **수정 비용**과 관련이 있다:

1. **코드 분석 시간 감소**: 역할에 따라 클래스가 분리되면 자연스럽게 클래스 길이가 줄고, 메서드 단위로 작성되기 때문에 가독성이 좋아진다
2. **수정 범위 감소**: 여러 모듈을 수정하지 않고 하나의 모듈만, 여러 클래스를 수정하지 않고 한 클래스만, 여러 메서드를 수정하지 않고 한 메서드만 수정하면 된다

### 2.4 응집도·역할·수정 범위

응집도는 역할 또는 책임과 관련이 있다. 응집도가 높아지면 구성 요소가 역할에 따라 알맞게 분리될 가능성이 커진다. 구성 요소가 역할에 따라 분리될수록 수정 범위가 좁아진다. 또한 응집도가 높아질수록 구성 요소를 수정하려는 이유도 하나로 줄어든다.

예를 들어 모든 회원 관련 타입이 member 패키지에, 계약 관련 타입은 contract 패키지에 존재한다면, 회원 관련 기능을 변경할 때 member 패키지에 위치한 코드만 수정하면 된다. 회원 가입과 회원 승인 기능을 각각 MemberRegisterer와 MemberApprover 클래스로 구현했다면, 회원 가입 로직을 변경하려면 MemberRegisterer만 수정하면 된다.

코드 수준에서도 마찬가지다:

```java
public void save(SaveRequest req) {
    validateRequest(req);
    Member member = createPendingMember(req);
    saveMember(member);
}
```

값 요청 검증 로직을 변경하려면 `validateRequest()` 메서드만 수정하면 된다. 대기 상태 회원을 생성하는 로직을 변경하려면 `createPendingMember()` 메서드만 수정하면 된다.

### 딥 다이브: 응집도와 단일 책임 원칙

변경할 이유가 적을수록 응집도가 올라간다. 단일 책임 원칙(*Single Responsibility Principle*)은 각 구성 요소는 하나의 책임만 가져야 한다는 원칙이다. 다르게 표현하면 구성 요소를 수정할 이유는 하나여야 한다는 것이다. 응집도를 높이려면 역할에 따라 구성 요소를 나눠야 하는데, 역할에 맞게 구성 요소를 나누면 각 구성 요소를 수정할 이유가 줄어들게 된다. 즉 **응집도가 높아지면 단일 책임 원칙을 따를 가능성이 올라간다.**

---

## 3. 캡슐화와 응집도

객체 지향에서 캡슐화(*encapsulation*)는 데이터와 함수를 한 곳에 모은다. 흔히 말하는 캡슐화는 정보 은닉(*information hiding - 데이터를 외부에 노출하지 않고 감추는 것*)을 포함한다.

캡슐화는 **응집도를 높이는 방법**의 하나다. 데이터에 대한 직접 접근을 최소화해서 구현을 감추고 외부에 기능을 제공한다. 이렇게 하면 구현을 변경해야 할 때 수정 범위가 캡슐화한 객체로 좁혀진다.

**캡슐화하지 않은 코드:**

```java
public class Member {
    private LocalDate expiry;
    // getter 생략
}

// 사용하는 코드 — 만료 판단 로직이 여러 곳에 분산
Member m = getMember(id);
if (m.getExpiry().isBefore(LocalDate.now())) {
    // ...
}
```

만료일을 무한대로 제공해야 해서 expiry 값을 null로 저장하기로 했다면, `getExpiry()`를 사용한 코드를 **모두 찾아서** null 체크를 추가해야 한다.

**캡슐화한 코드:**

```java
public class Member {
    private LocalDate expiry;

    public boolean isExpired() {
        return expiry != null && expiry.isBefore(LocalDate.now());
    }
}

// 사용하는 코드 — 만료 판단은 Member에게 위임
if (m.isExpired()) {
    // ...
}
```

캡슐화한 코드는 데이터(만료일)와 관련 로직(만료 여부 판단)을 한 클래스에 모았다. 외부에는 `isExpired()`만 노출하고 expiry는 제공하지 않는다. 요구사항 변경으로 만료일이 없을 때 null을 사용하기로 해도, `isExpired()` 메서드 **한 곳만** 수정하면 된다. 사용하는 코드는 바뀌지 않는다.

> **핵심 통찰**: 캡슐화하지 않은 코드에서는 만료 여부를 판단하는 로직을 변경할 때 여러 곳을 수정해야 하지만, 캡슐화한 코드는 한 곳만 수정하면 된다. 관련 코드(데이터와 데이터를 사용하는 로직)가 한 곳에 모여 있어(즉, 응집되어 있어) 수정할 범위가 줄어든 것이다.

---

## 4. 결합도

위키피디아에 정의된 결합도의 정의:

> 결합도는 소프트웨어 모듈이 서로 의존하는 정도이다. 두 모듈이 얼마나 밀접하게 연결되어 있는지 모듈 간 관계 정도를 나타낸다.

한 요소를 수정할 때 다른 요소도 함께 수정해야 하면 두 요소 간 **결합도가 높다**고 표현한다. 반대로 한 모듈을 수정할 때 다른 모듈을 수정하지 않아도 되면 **결합도가 낮다**고 말한다.

수정할 대상이 많아지면 코드 분석과 수정에 드는 시간이 증가한다. 따라서 **수정 비용을 낮추기 위해서는 응집도는 높이고 결합도는 낮춰야 한다.**

응집도가 높다고 해서 반드시 결합도가 낮아지는 것은 아니다. 응집도를 높이려면 코드를 역할에 따라 분리해야 한다. 그러나 분리된 요소 간에 의존이 발생하게 되고, 서로 의존하는 정도가 올라갈수록 결합도가 증가한다.

응집도를 높이고 결합도를 낮추려면 **구성 요소 간 상호 작용을 최소화**해야 한다. 구성 요소 간 상호 작용을 최소화하려면 **구현에 대한 의존을 줄이는 것**이 중요하다. 앞서 언급한 캡슐화는 구현을 감춤으로써 두 구성 요소 간의 상호 작용을 줄여 주어 응집도를 높이는 동시에 결합도를 낮춰 준다.

---

## 5. 추상화 타입과 결합도

추상화 타입을 사용해도 결합도를 낮출 수 있다. 다음 코드를 보자:

```java
public class MemberRegister {
    private JdbcTemplate jdbcTemplate;
    // ...

    public void register(RegisterRequest req) {
        validate(req);
        Member m = createPendingMember(req);
        saveMember(m);
        sendNotiSms(m);
    }

    private void sendNotiSms(Member m) {
        String content = "... 생략";
        jdbcTemplate.update(
            "insert into SMS_SEND (PHONE, CONTENT) values (?, ?)",
            m.getPhone(), content);
    }
}
```

`sendNotiSms()` 메서드는 SMS를 전송하기 위해 SMS_SEND 테이블에 레코드를 삽입한다. 이 메서드는 SMS 발송을 위해 **SMS_SEND 테이블이라는 구현에 직접 의존**하고 있다. 구현에 직접 의존하고 있기 때문에 다음과 같은 상황이 발생하면 MemberRegister 클래스를 함께 변경해야 한다:

- LMS로 발송하기 위해 insert 쿼리에 LMS_YN 칼럼을 추가해야 한다
- 문자가 아닌 알림톡으로 발송하기 위해 저장 대상 테이블을 변경한다
- 테이블에 삽입하는 방식이 아닌 API를 호출하는 방식으로 변경한다

**추상화로 이러한 강결합을 낮출 수 있다.** SMS 문자 통지 기능을 Notifier 타입으로 추상화해서 분리한다:

```java
public class MemberRegister {
    private Notifier notifier;  // 구현이 아닌 추상화 타입에 의존
    // ...

    public void register(RegisterRequest req) {
        validate(req);
        Member m = createPendingMember(req);
        saveMember(m);
        notifier.notifyTo(m);
    }
}
```

Notifier의 실제 구현체는 MemberRegister 객체를 생성할 때 전달한다:

```java
Notifier notifier = new SmsNotifier();
MemberRegister register = new MemberRegister(notifier, ...);

// 통지 수단을 알림톡으로 변경해도 MemberRegister는 수정 불필요
Notifier notifier = new AlimtalkNotifier();
MemberRegister register = new MemberRegister(notifier, ...);
```

SMS_SEND 테이블에 데이터를 넣는 방식을 변경해야 할 때는 SmsNotifier 클래스만 수정하면 된다. MemberRegister 클래스는 수정할 필요가 없다. 추상화 타입을 사용해서 MemberRegister와 통지 기능 간 **결합도를 낮추고 응집도는 높인 것**이다.

---

## 6. 이벤트와 결합도

결합도를 낮추는 또 다른 방법은 **이벤트**를 사용하는 것이다. 이벤트는 발생한 어떤 사건을 의미한다:

```java
public class MemberRegister {
    public void register(RegisterRequest req) {
        validate(req);
        Member m = createPendingMember(req);
        saveMember(m);
        Events.raise(new MemberRegisteredEvent(m));  // 이벤트 발생
    }
}

public class MemberEventListener {
    public void handle(MemberRegisteredEvent event) {
        // ... SMS 전송 코드 위치
    }
}
```

추상화 타입을 사용해서 결합을 낮춘 경우에도 MemberRegister 클래스가 Notifier 인터페이스에 의존하고 있었다. 반면에 이벤트를 사용한 코드에서 MemberRegister 클래스가 **더 이상 통지에 대한 코드에 의존하지 않는다.** MemberEventListener도 회원 가입 코드와 관련이 없다. 단지 MemberRegisteredEvent를 수신하면 통지할 뿐이다.

이벤트를 사용함으로써 회원 가입과 SMS 통지 코드 간의 **결합을 낮추고 응집도는 높아졌다.**

### 추상화, 이벤트와 코드 추적

추상화와 이벤트는 결합도를 낮추는 이점이 있지만, 두 코드를 직접 연결하지 않고 **간접적으로 연결**하기 때문에 직접 연결된 코드에 비해 코드를 분석하는 데 더 많은 노력이 들어간다. 또한 새로운 타입이 추가되어 구조도 약간 복잡해진다.

따라서 추상화나 이벤트를 적용할 때는 **결합도 감소, 응집도 증가, 변경 비용 감소, 테스트 가능성** 등 얻을 수 있는 이점을 따져 봐야 한다. 이점이 별로 없다면 추상화 타입을 사용하지 않고 **구현만 분리해서 응집도를 높이는 것**도 좋은 선택이 될 수 있다.

---

## 7. 결합 유형

결합은 다양한 형태로 존재한다. 어떤 형태의 결합이 존재하는지 알면 결합도를 높이지 않는 방향으로 코드를 작성하는 데 도움이 된다.

### 7.1 공통 결합

공통 결합(*common coupling*)은 여러 모듈이 동일한 글로벌 데이터에 접근할 때 발생한다. 여러 기능이 글로벌 데이터에 직접 접근하기 때문에 글로벌 데이터에서 변경이 발생하면 예측하기 힘든 문제가 생길 수 있다.

예를 들어 회원·주문·상품 모듈이 모두 고객 데이터에 직접 접근하여 변경할 수 있다고 하자. 이때 고객 데이터는 글로벌 데이터가 된다. 회원 모듈이 고객 데이터의 특정 속성에 추가적인 의미를 부여하면 해당 속성을 사용해서 로직을 수행하는 주문 또는 상품 모듈에서 에러가 발생하거나 비정상적으로 동작할 수 있다.

### 7.2 제어 결합

제어 결합(*control coupling*)은 한 모듈이 다른 모듈의 흐름을 제어할 때 발생한다. 무엇을 할지를 전달하는 형태로 흐름을 제어하는데, 보통 파라미터를 사용해서 정보를 전달한다. 제어 결합은 **내부 동작 방식을 외부에 노출해서 결합도를 높인다:**

```java
public void saveContractCancel(CancelDto dto) {
    if (dto.getConfirmYn().equals("Y")) {
        ... 취소 확정 로직 코드
    } else if (!dto.getConfirmYn().equals("Y")) {
        ... 취소 완료 로직 코드
    }
    if (dto.getConfirmYn().equals("Y")) {
        ... 취소 확정 관련 후처리 로직
    }
}
```

`saveContractCancel()` 메서드를 호출하는 쪽에서 confirmYn 값으로 무엇을 전달하는지에 따라 메서드 동작이 달라진다.

### 7.3 하위 클래스 결합

하위 클래스 결합은 하위 클래스와 상위 클래스 간의 관계를 설명한다. 하위 클래스가 상위 클래스에 의존하고 상위 클래스는 하위 클래스에 의존하지 않는다. 하지만 **상위 클래스 기능을 사용하는 하위 클래스가 많을수록 상위 클래스를 수정하기 어려워진다.** 상위 클래스를 수정하면 하위 클래스에 많은 영향을 주기 때문이다.

상속보다는 조립(*Composition over inheritance*) 원칙은 상속을 생각하기 전에 조립을 먼저 고려하라는 원칙이다. 상속은 두 요소(상위 클래스와 하위 클래스) 간 강한 결합을 발생시키는데, 조립을 사용하면 상속에 비해 결합도를 낮출 수 있다.

### 7.4 시간적 결합

시간적 결합(*temporal coupling*)은 단지 함께 실행해야 하므로 두 기능을 한 모듈에 묶을 때 발생한다. 앞서 살펴봤던 회원 가입도 시간적 결합에 해당한다. 회원 데이터를 저장하는 기능과 문자를 전송하는 기능을 함께 실행하기 위해 회원 가입 기능에 묶여 있다. 이런 형태의 결합은 추상화나 이벤트 같은 방법으로 결합을 낮출 수 있다.

지켜야 하는 실행 순서도 시간적 결합에 해당한다. 예를 들어 반드시 `init()` 메서드를 먼저 호출한 뒤에 `play()` 메서드를 실행해야 한다면 이것은 시간적 결합을 갖는다.

### 7.5 논리 결합(변경 결합)

논리 결합(*logical coupling*) 또는 변경 결합(*change coupling*)은 두 모듈 간의 변경 패턴이 존재할 때 발생한다. 만약 모듈·시스템 데이터를 변경할 때 다른 모듈·시스템 데이터도 함께 변경해야 한다면 논리 결합이 발생한다. 예를 들어 회원 시스템에서 회원 이메일 주소를 변경했을 때 포인트 시스템의 이메일 주소도 함께 변경해야 하면 두 시스템은 논리적으로 결합하고 있다고 할 수 있다.

---

## 요약

- **응집도**는 관련 요소가 얼마나 한 모듈에 모여 있는지를 나타내며, 높을수록 수정 범위가 줄어든다
- **결합도**는 소프트웨어 모듈이 서로 의존하는 정도이며, 높을수록 유지보수 비용이 증가한다
- 좋은 설계는 **높은 응집도와 낮은 결합도**를 추구한다
- 응집도를 높이려면 역할에 따라 구성 요소를 분리하고, 메서드 추출을 활용한다
- **캡슐화**는 데이터와 관련 로직을 한 곳에 모아 응집도를 높이고 결합도를 낮추는 대표적인 방법이다
- **추상화 타입**(인터페이스)을 사용하면 구현에 대한 의존을 줄여 결합도를 낮출 수 있다
- **이벤트**를 사용하면 두 기능 간의 직접적인 의존을 제거할 수 있다
- 추상화와 이벤트는 코드 추적을 어렵게 만드는 단점이 있으므로 이점을 따져보고 적용해야 한다
- 주요 결합 유형: 공통 결합(글로벌 데이터), 제어 결합(흐름 제어 파라미터), 하위 클래스 결합(상속), 시간적 결합(함께 실행), 논리 결합(변경 패턴)
