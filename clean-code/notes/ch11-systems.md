# Chapter 11: Systems (시스템)

## 핵심 질문

깨끗한 코드로 낮은 추상화 수준에서 관심사를 분리했다면, 높은 추상화 수준인 시스템 수준에서는 어떻게 깨끗함을 유지할 수 있는가? 시스템의 생성과 사용을 분리하고, 관점 지향 프로그래밍으로 횡단 관심사를 모듈화하는 방법은 무엇인가?

---

## 1. 도시를 세운다면?

도시를 혼자서 직접 관리할 수 있을까? 아마도 불가능하다. 그럼에도 도시는 잘 돌아간다. 수도 관리 팀, 전력 관리 팀, 교통 관리 팀, 치안 관리 팀 등 **각 분야를 관리하는 팀**이 있기 때문이다. 도시에는 큰 그림을 그리는 사람들도 있고 작은 사항에 집중하는 사람들도 있다.

도시가 돌아가는 또 다른 이유는 **적절한 추상화와 모듈화** 때문이다. 큰 그림을 이해하지 못할지라도 개인과 개인이 관리하는 '구성요소'는 효율적으로 돌아간다.

소프트웨어 팀도 도시처럼 구성한다. 하지만 막상 팀이 제작하는 시스템은 비슷한 수준으로 관심사를 분리하지 못한다. 이 장에서는 **높은 추상화 수준, 즉 시스템 수준에서 깨끗함을 유지하는 방법**을 살펴본다.

> **핵심 통찰**: "복잡성은 죽음이다. 개발자에게서 생기를 앗아가며, 제품을 계획하고 제작하고 테스트하기 어렵게 만든다." — 레이 오지(Ray Ozzie), 마이크로소프트 CTO

---

## 2. 시스템 제작과 시스템 사용을 분리하라

**제작(construction)은 사용(use)과 아주 다르다.** 건물을 짓는 동안에는 기중기와 승강기가 있고, 안전모에 작업복을 착용한 사람들이 바쁘게 움직인다. 완공된 후에는 유리벽과 예쁜 색상의 벽으로 꾸며진 건물에서 전혀 다른 사람들이 생활한다.

소프트웨어 시스템도 마찬가지다:
- **(제작)** 애플리케이션 객체를 제작하고 의존성을 서로 '연결'하는 **준비 과정**
- **(사용)** 준비 과정 이후에 이어지는 **런타임 로직**

이 두 과정을 분리해야 한다. 관심사 분리는 우리 분야에서 **가장 오래되고 가장 중요한 설계 기법** 중 하나다.

### 초기화 지연의 문제

```java
// 나쁜 예 — 초기화 지연 (Lazy Initialization)
public Service getService() {
    if (service == null)
        service = new MyServiceImpl(...); // 모든 상황에 적합한 기본값일까?
    return service;
}
```

초기화 지연의 장점:
- 실제로 필요할 때까지 객체를 생성하지 않으므로 불필요한 부하가 걸리지 않는다
- 어떤 경우에도 null 포인터를 반환하지 않는다

하지만 심각한 문제가 있다:

| 문제 | 설명 |
|---|---|
| **명시적 의존성** | `getService` 메서드가 `MyServiceImpl`과 생성자 인수에 명시적으로 의존 |
| **컴파일 의존성** | 런타임 로직에서 `MyServiceImpl`을 사용하지 않더라도 의존성을 해결하지 않으면 컴파일 안 됨 |
| **테스트 문제** | 단위 테스트에서 적절한 TEST DOUBLE이나 MOCK OBJECT를 할당해야 함 |
| **SRP 위반** | 일반 런타임 로직에다 객체 생성 로직을 섞어놓음 (null인 경로와 아닌 경로) |
| **적합성 불확실** | `MyServiceImpl`이 모든 상황에 적합한 객체인지 모름 |

한 번 정도 사용하면 별로 심각하지 않지만, 이처럼 좀스러운 설정 기법을 **수시로 사용**하면 전반적인 설정 방식이 애플리케이션 곳곳에 흩어지고, 모듈성은 저조해지며, 대개 중복이 심각해진다.

> **핵심 통찰**: 체계적이고 탄탄한 시스템을 만들고 싶다면 흔히 쓰는 좀스럽고 손쉬운 기법으로 모듈성을 깨서는 절대로 안 된다. 설정 논리는 일반 실행 논리와 분리해야 모듈성이 높아진다.

---

## 3. Main 분리

시스템 생성과 사용을 분리하는 한 가지 방법으로, **생성과 관련한 코드는 모두 `main`이나 `main`이 호출하는 모듈로 옮기고**, 나머지 시스템은 모든 객체가 생성되었고 모든 의존성이 연결되었다고 가정한다.

```
main ──(구축)──→ 구축자 ──(생성)──→ 설정된 객체
  │                                       │
  └────────(실행)────────→ 애플리케이션 ←──┘
```

제어 흐름은 따라가기 쉽다:
1. `main` 함수에서 시스템에 필요한 객체를 생성한다
2. 생성된 객체를 애플리케이션에 넘긴다
3. 애플리케이션은 그저 객체를 사용할 뿐이다

모든 의존성 화살표가 **main 쪽에서 애플리케이션 쪽**을 향한다. 즉, 애플리케이션은 main이나 객체가 생성되는 과정을 **전혀 모른다**.

---

## 4. 팩토리

때로는 객체가 생성되는 **시점**을 애플리케이션이 결정할 필요도 생긴다. 이때는 **ABSTRACT FACTORY 패턴**을 사용한다.

예를 들어, 주문처리 시스템에서 애플리케이션은 `LineItem` 인스턴스를 생성해 `Order`에 추가한다:

```
main ──→ OrderProcessing ──→ «인터페이스» LineItemFactory
                                          ↑
                 LineItemFactoryImpl ──────┘
                       │
                       └──(생성)──→ LineItem
```

- `OrderProcessing`은 `LineItem`이 생성되는 **구체적인 방법을 모른다** (그 방법은 `main` 쪽의 `LineItemFactoryImpl`이 안다)
- 그럼에도 `OrderProcessing`은 `LineItem` 인스턴스가 생성되는 **시점을 완벽하게 통제**하며, 필요하다면 생성자 인수도 넘길 수 있다
- 모든 의존성이 main에서 `OrderProcessing` 애플리케이션으로 향한다

---

## 5. 의존성 주입 (Dependency Injection, DI)

사용과 제작을 분리하는 강력한 메커니즘이 **의존성 주입(DI)** 이다. DI는 **제어 역전(Inversion of Control, IoC)** 기법을 의존성 관리에 적용한 메커니즘이다.

### 제어 역전의 핵심

한 객체가 맡은 보조 책임을 새로운 객체에게 전적으로 떠넘긴다. 새로운 객체는 넘겨받은 책임만 맡으므로 **SRP를 지키게 된다**. 의존성 관리 맥락에서 객체는 의존성 자체를 인스턴스로 만드는 책임은 지지 않는다.

### JNDI 검색 — 부분적 DI

```java
MyService myService = (MyService)(jndiContext.lookup("NameOfMyService"));
```

호출하는 객체는 실제로 반환되는 객체의 유형을 제어하지 않지만, 의존성을 **능동적으로** 해결한다.

### 진정한 DI

클래스가 의존성을 해결하려 시도하지 않는다. 클래스는 **완전히 수동적**이다. 대신에 의존성을 주입하는 방법으로 **설정자(setter) 메서드**나 **생성자 인수**를 제공한다.

DI 컨테이너는:
1. 필요한 객체의 인스턴스를 만든다
2. 생성자 인수나 설정자 메서드를 사용해 의존성을 설정한다
3. 실제로 생성되는 객체 유형은 설정 파일이나 특수 생성 모듈에서 지정한다

**스프링 프레임워크**는 가장 널리 알려진 자바 DI 컨테이너를 제공한다. 대다수 DI 컨테이너는 필요할 때까지 객체를 생성하지 않고, 계산 지연이나 비슷한 최적화에 쓸 수 있도록 **팩토리를 호출하거나 프록시를 생성하는 방법**도 제공한다.

---

## 6. 확장

'처음부터 올바르게' 시스템을 만들 수 있다는 믿음은 **미신**이다. 오늘 주어진 사용자 스토리에 맞춰 시스템을 구현하고, 내일은 새로운 스토리에 맞춰 시스템을 조정하고 확장하면 된다. 이것이 반복적이고 점진적인 **애자일 방식**의 핵심이다.

**소프트웨어 시스템은 물리적인 시스템과 다르다.** 관심사를 적절히 분리해 관리한다면 소프트웨어 아키텍처는 **점진적으로 발전**할 수 있다.

### EJB2의 실패 사례

원래 EJB1과 EJB2 아키텍처는 관심사를 적절히 분리하지 못했기에 유기적인 성장이 어려웠다. Bank 엔티티 빈을 구현하려면:

1. 클라이언트가 사용할 **지역 인터페이스**를 정의해야 한다
2. **엔티티 빈 구현 클래스**를 작성해야 한다 (컨테이너에서 파생, 생명주기 메서드 제공)
3. **XML 배포 기술자**를 작성해야 한다 (영속 저장소 매핑, 트랜잭션, 보안)

```java
// 나쁜 예 — EJB2 엔티티 빈 구현
public abstract class Bank implements javax.ejb.EntityBean {
    // 비즈니스 논리...
    public abstract String getStreetAddr1();
    public abstract String getStreetAddr2();
    public abstract void setStreetAddr1(String street1);
    // ...

    public void addAccount(AccountDTO accountDTO) {
        InitialContext context = new InitialContext();
        AccountHomeLocal accountHome = context.lookup("AccountHomeLocal");
        AccountLocal account = accountHome.create(accountDTO);
        Collection accounts = getAccounts();
        accounts.add(account);
    }

    // EJB 컨테이너 논리 — 나머지도 구현해야 하지만 일반적으로 비어있다
    public abstract void setId(Integer id);
    public abstract Integer getId();
    public Integer ejbCreate(Integer id) { ... }
    public void ejbPostCreate(Integer id) { ... }
    public void setEntityContext(EntityContext ctx) {}
    public void unsetEntityContext() {}
    public void ejbActivate() {}
    public void ejbPassivate() {}
    public void ejbLoad() {}
    public void ejbStore() {}
    public void ejbRemove() {}
}
```

| EJB2의 문제점 | 설명 |
|---|---|
| **강한 결합** | 비즈니스 논리가 덩치 큰 컨테이너와 밀접하게 결합 |
| **독자적 단위 테스트 어려움** | 컨테이너를 흉내 내거나 실제 서버에 배치해야 함 |
| **재사용 불가** | 프레임워크 밖에서 재사용하기란 사실상 불가능 |
| **OOP 훼손** | 빈은 다른 빈을 상속 받지 못함 |
| **DTO 중복** | 동일한 정보를 저장하는 자료 유형이 두 개, 반복적인 규격 코드 필요 |

### 횡단 관심사 (Cross-Cutting Concerns)

영속성, 보안, 트랜잭션과 같은 관심사는 애플리케이션의 자연스러운 객체 경계를 **넘나드는** 경향이 있다. 모든 객체가 전반적으로 동일한 방식을 이용하게 만들어야 한다. 여기서 **횡단 관심사**라는 용어가 나온다.

EJB 아키텍처가 영속성, 보안, 트랜잭션을 처리하는 방식은 **관점 지향 프로그래밍(AOP)** 을 예견했다. AOP는 횡단 관심사에 대처해 모듈성을 확보하는 일반적인 방법론이다.

---

## 7. 자바 프록시

자바 프록시는 단순한 상황에 적합하다. 개별 객체나 클래스에서 메서드 호출을 감싸는 경우가 좋은 예다.

```java
// Bank 인터페이스
public interface Bank {
    Collection<Account> getAccounts();
    void setAccounts(Collection<Account> accounts);
}

// POJO 구현
public class BankImpl implements Bank {
    private List<Account> accounts;
    public Collection<Account> getAccounts() { return accounts; }
    public void setAccounts(Collection<Account> accounts) {
        this.accounts = new ArrayList<Account>();
        for (Account account: accounts) {
            this.accounts.add(account);
        }
    }
}

// 프록시 핸들러
public class BankProxyHandler implements InvocationHandler {
    private Bank bank;

    public BankProxyHandler(Bank bank) {
        this.bank = bank;
    }

    public Object invoke(Object proxy, Method method, Object[] args)
            throws Throwable {
        String methodName = method.getName();
        if (methodName.equals("getAccounts")) {
            bank.setAccounts(getAccountsFromDatabase());
            return bank.getAccounts();
        } else if (methodName.equals("setAccounts")) {
            bank.setAccounts((Collection<Account>) args[0]);
            setAccountsToDatabase(bank.getAccounts());
            return null;
        } else {
            // ...
        }
    }
    // 세부사항은 여기에 이어진다.
    protected Collection<Account> getAccountsFromDatabase() { ... }
    protected void setAccountsToDatabase(Collection<Account> accounts) { ... }
}

// 프록시 생성
Bank bank = (Bank) Proxy.newProxyInstance(
    Bank.class.getClassLoader(),
    new Class[] { Bank.class },
    new BankProxyHandler(new BankImpl()));
```

프록시의 단점:
- 단순한 예제지만 **코드가 상당히 많으며 제법 복잡**하다
- **깨끗한 코드를 작성하기 어렵다**
- 시스템 단위로 실행 '지점'을 명시하는 메커니즘을 제공하지 않는다

---

## 8. 순수 자바 AOP 프레임워크

순수 자바 관점을 구현하는 **스프링 AOP, JBoss AOP** 등의 프레임워크는 내부적으로 프록시를 사용하지만, 프록시 코드 대부분을 자동화한다.

스프링은 비즈니스 논리를 **POJO**로 구현한다. POJO는 순수하게 도메인에 초점을 맞추며, 엔터프라이즈 프레임워크에 의존하지 않는다. 따라서 테스트가 개념적으로 더 쉽고 간단하다.

```xml
<!-- 스프링 2.X 설정 파일 -->
<beans>
    <bean id="appDataSource"
        class="org.apache.commons.dbcp.BasicDataSource"
        destroy-method="close"
        p:driverClassName="com.mysql.jdbc.Driver"
        p:url="jdbc:mysql://localhost:3306/mydb"
        p:username="me"/>

    <bean id="bankDataAccessObject"
        class="com.example.banking.persistence.BankDataAccessObject"
        p:dataSource-ref="appDataSource"/>

    <bean id="bank"
        class="com.example.banking.model.Bank"
        p:dataAccessObject-ref="bankDataAccessObject"/>
</beans>
```

각 '빈'은 중첩된 '러시아 인형'(*Matryoshka — 통통한 인형 안에 똑같은 인형이 중첩되어 들어있는 러시아 전통 목각 인형. DECORATOR 패턴의 중첩 구조를 비유한다.*)의 일부분과 같다. 클라이언트는 `Bank` 객체에서 `getAccounts()`를 호출한다고 믿지만, 실제로는 Bank POJO의 기본 동작을 확장한 **중첩 DECORATOR 객체 집합**의 가장 외곽과 통신한다.

```java
// 애플리케이션에서 DI 컨테이너에게 최상위 객체를 요청
XmlBeanFactory bf =
    new XmlBeanFactory(new ClassPathResource("app.xml", getClass()));
Bank bank = (Bank) bf.getBean("bank");
```

스프링 관련 자바 코드가 거의 필요 없으므로 애플리케이션은 **사실상 스프링과 독립적**이다.

### EJB3로의 진화

스프링 프레임워크의 영향으로 EJB3는 완전히 뜯어고쳐졌다:

```java
// 좋은 예 — EJB3 Bank 엔티티
@Entity
@Table(name = "BANKS")
public class Bank implements java.io.Serializable {
    @Id @GeneratedValue(strategy=GenerationType.AUTO)
    private int id;

    @Embeddable
    public class Address {
        protected String streetAddr1;
        protected String streetAddr2;
        protected String city;
        protected String state;
        protected String zipCode;
    }

    @Embedded
    private Address address;

    @OneToMany(cascade = CascadeType.ALL, fetch = FetchType.EAGER,
        mappedBy="bank")
    private Collection<Account> accounts = new ArrayList<Account>();

    public int getId() { return id; }
    public void setId(int id) { this.id = id; }

    public void addAccount(Account account) {
        account.setBank(this);
        accounts.add(account);
    }

    public Collection<Account> getAccounts() { return accounts; }
    public void setAccounts(Collection<Account> accounts) {
        this.accounts = accounts;
    }
}
```

모든 정보가 **애너테이션 속에** 있으므로 코드 자체는 깔끔하고 깨끗하다. 테스트하고 개선하고 보수하기가 훨씬 쉬워졌다.

---

## 9. AspectJ 관점

관심사를 관점으로 분리하는 가장 강력한 도구는 **AspectJ 언어**다. AspectJ는 언어 차원에서 관점을 모듈화 구성으로 지원하는 자바 언어 확장이다.

스프링 AOP와 JBoss AOP가 제공하는 순수 자바 방식은 관점이 필요한 상황 중 **80-90%에 충분**하다. AspectJ는 관점을 분리하는 강력하고 풍부한 도구 집합을 제공하지만, 새 도구를 사용하고 새 언어 문법과 사용법을 익혀야 한다는 단점이 있다.

최근에 나온 AspectJ '애너테이션 폼'은 순수한 자바 코드에 자바 5 애너테이션을 사용해 관점을 정의하여 이 부담을 어느 정도 완화한다.

---

## 10. 테스트 주도 시스템 아키텍처 구축

관점으로 관심사를 분리하는 방식은 그 위력이 막강하다. 애플리케이션 도메인 논리를 POJO로 작성할 수 있다면, 즉 코드 수준에서 아키텍처 관심사를 분리할 수 있다면, 진정한 **테스트 주도 아키텍처 구축**이 가능해진다.

BDUF(Big Design Up Front)(*Big Design Up Front — 구현을 시작하기 전에 앞으로 벌어질 모든 사항을 설계하는 기법. 선행 설계(up-front design)라는 우수한 설계 기법과 혼동하지 않도록 주의한다.*)를 추구할 필요가 없다. 실제로 BDUF는 해롭기까지 하다:
- 처음에 쏟아 부은 노력을 버리지 않으려는 **심리적 저항**
- 처음 선택한 아키텍처가 향후 사고 방식에 미치는 **영향**
- 변경을 쉽사리 수용하지 못하는 결과

> **핵심 통찰**: 최선의 시스템 구조는 각기 POJO(또는 다른) 객체로 구현되는 모듈화된 관심사 영역(도메인)으로 구성된다. 이렇게 서로 다른 영역은 해당 영역 코드에 최소한의 영향을 미치는 관점이나 유사한 도구를 사용해 통합한다. 이런 구조 역시 코드와 마찬가지로 테스트 주도 기법을 적용할 수 있다.

---

## 11. 의사 결정을 최적화하라

모듈을 나누고 관심사를 분리하면 **지엽적인 관리와 결정**이 가능해진다. 우리는 때때로 가능한 **마지막 순간까지 결정을 미루는 방법**이 최선이라는 사실을 까먹곤 한다.

게으르거나 무책임해서가 아니다. **최대한 정보를 모아 최선의 결정을 내리기 위해서**다. 성급한 결정은 불충분한 지식으로 내린 결정이다. 너무 일찍 결정하면:
- 고객 피드백을 더 모을 기회가 사라진다
- 프로젝트를 더 고민할 기회가 사라진다
- 구현 방안을 더 탐험할 기회가 사라진다

관심사를 모듈로 분리한 POJO 시스템은 **기민함**을 제공한다. 최신 정보에 기반해 최선의 시점에 최적의 결정을 내리기가 쉬워지고, 결정의 복잡성도 줄어든다.

---

## 12. 명백한 가치가 있을 때 표준을 현명하게 사용하라

EJB2는 **단지 표준이라는 이유만으로** 많은 팀이 사용했다. 가볍고 간단한 설계로 충분했을 프로젝트에서도 EJB2를 채택했다.

표준을 사용하면:
- 아이디어와 컴포넌트를 **재사용**하기 쉽다
- 적절한 경험을 가진 **사람을 구하기** 쉽다
- 좋은 아이디어를 **캡슐화**하기 쉽다
- 컴포넌트를 **엮기** 쉽다

하지만 때로는 표준을 만드는 시간이 너무 오래 걸려 업계가 기다리지 못한다. 어떤 표준은 원래 표준을 제정한 **목적을 잊어버리기도** 한다.

---

## 13. 시스템은 도메인 특화 언어가 필요하다

**DSL(Domain-Specific Language)** 은 간단한 스크립트 언어나 표준 언어로 구현한 API를 가리킨다. DSL로 짠 코드는 도메인 전문가가 작성한 구조적인 산문처럼 읽힌다.

좋은 DSL의 가치:

| 가치 | 설명 |
|---|---|
| **의사소통 간극 축소** | 도메인 개념과 구현 코드 사이의 간극을 줄여준다 |
| **오구현 방지** | 도메인 전문가가 사용하는 언어로 도메인 논리를 구현하면 잘못 구현할 가능성이 줄어든다 |
| **추상화 수준 향상** | 코드 관용구나 디자인 패턴 이상으로 추상화 수준을 끌어올린다 |
| **POJO 표현** | 고차원 정책에서 저차원 세부사항에 이르기까지 모든 추상화 수준과 모든 도메인을 POJO로 표현할 수 있다 |

---

## 요약

- **시스템 제작과 사용을 분리하라** — 준비 과정과 런타임 로직을 섞지 마라
- **Main 분리, 팩토리, 의존성 주입** — 생성 관심사를 애플리케이션에서 격리하는 세 가지 방법
- **관심사를 적절히 분리하면** 소프트웨어 아키텍처는 점진적으로 발전할 수 있다 — 물리적 시스템과 달리
- **AOP**로 횡단 관심사를 모듈화하라 — 자바 프록시, 순수 자바 AOP 프레임워크(스프링), AspectJ
- **POJO로 비즈니스 논리를 구현**하면 테스트가 쉽고 사용자 스토리를 올바로 구현하기 쉽다
- **BDUF를 피하라** — '아주 단순하면서도' 멋지게 분리된 아키텍처로 시작해 조금씩 확장해 나가라
- **의사 결정은 가능한 늦추라** — 최대한 정보를 모아 최선의 결정을 내려라
- **표준은 명백한 가치가 있을 때만** 사용하라
- **DSL**로 도메인 개념과 구현 코드 사이의 간극을 줄여라

---

## 다른 챕터와의 관계

- **← Chapter 10 (클래스)**: 클래스 수준의 SRP와 OCP가 시스템 수준의 관심사 분리와 확장으로 이어진다
- **→ Chapter 12 (창발성)**: "모든 테스트를 실행하라"는 규칙이 테스트 주도 시스템 아키텍처 구축의 기반이 된다
- **← Chapter 1 (깨끗한 코드)**: 론 제프리스의 단순한 코드 규칙과 SRP, DIP 원칙이 이 장에서 시스템 수준으로 확장된다
- **← Chapter 9 (단위 테스트)**: DI와 인터페이스를 통한 결합도 낮추기는 테스트 가능한 시스템의 전제 조건이다
- **→ Chapter 17 (냄새와 휴리스틱)**: "구현에 의존하지 마라", "인터페이스를 사용하라" 등의 휴리스틱이 이 장의 원칙을 코드 수준으로 정리한 것이다
