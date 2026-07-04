# Chapter 26: Proxy and Stairway to Heaven (프록시와 천국으로의 계단 — 서드파티 API 관리)

## 핵심 질문

업무 규칙을 데이터베이스, 미들웨어, 서드파티 API 같은 외부 장벽에서 어떻게 분리할 수 있는가? 프록시(*Proxy*) 패턴은 어떻게 클라이언트와 객체 양쪽 모두 모르게 데이터베이스 같은 인프라를 끼워 넣을 수 있는가? 다중 상속을 활용하는 '천국으로의 계단'(*Stairway to Heaven*) 패턴은 어떤 상황에서 프록시의 대안이 되는가? 그리고 이런 무거운 패턴을 언제부터, 언제 적용해야 하는가?

---

## 1. 장벽 문제와 동기

소프트웨어 시스템에는 많은 장벽이 있다. 프로그램에서 데이터베이스로 데이터를 옮길 때는 데이터베이스의 장벽을 넘고, 한 컴퓨터에서 다른 컴퓨터로 메시지를 전송할 때는 네트워크의 장벽을 넘는다.

이런 장벽을 넘는 일은 때로 매우 복잡한 문제가 될 수 있다. 충분히 주의를 기울이지 않으면, 정작 해결하려는 문제보다 장벽 자체에 더 신경을 쓰게 만드는 소프트웨어가 된다.

### 1.1 단순 객체 모델과 데이터베이스 코드의 충돌

쇼핑 카트 시스템을 가정하자. 고객(*Customer*), 주문 목록(*Order*), 항목(*Item*), 상품(*Product*) 객체로 단순히 구성한다.

```
Customer  1 ──┬──  * Order  1 ──┬──  * Item  *  ──┬──  1 Product
              │                  │                 │
              orderList          items             product
```

순수 객체 모델에서 항목을 추가하는 코드는 데이터베이스의 존재를 모른다.

```typescript
class Order {
  private items: Item[] = [];

  addItem(product: Product, qty: number): void {
    const item = new Item(product, qty);
    this.items.push(item);
  }
}
```

<details>
<summary>Java 원본</summary>

```java
public class Order {
  private Vector itsItems = new Vector();

  public void addItem(Product p, int qty) {
    Item item = new Item(p, qty);
    itsItems.add(item);
  }
}
```
</details>

그런데 이 객체들이 관계형 데이터베이스의 데이터를 표현한다면, 같은 기능을 다음과 같이 직접 JDBC로 작성하기 쉽다.

```typescript
class AddItemTransaction extends Transaction {
  addItem(orderId: number, sku: string, qty: number): void {
    const stmt = this.connection.createStatement();
    stmt.executeUpdate(
      `insert into items values(${orderId}, '${sku}', ${qty})`,
    );
  }
}
```

<details>
<summary>Java 원본</summary>

```java
public class AddItemTransaction extends Transaction {
  public void addItem(int orderId, String sku, int qty) {
    Statement s = itsConnection.createStatement();
    s.executeUpdate("insert into items values(" +
        orderId + "," + sku + "," + qty + ")");
  }
}
```
</details>

> **핵심 통찰**: 두 코드 조각은 같은 논리적 기능(주문에 항목을 연결)을 수행하지만, 두 번째는 SQL과 데이터베이스 연결, 질의 문자열을 자랑스럽게 드러낸다. 이는 SRP(단일 책임 원칙) 위반이고, CCP(공통 폐쇄 원칙)도 위반할 수 있다. 항목/주문이라는 도메인 개념과 관계 스키마/SQL이라는 인프라 개념을 한 곳에 섞었기 때문이다. 또한 정책(업무 규칙)이 저장 메커니즘의 세부에 의존하므로 DIP(의존 관계 역전 원칙)도 어긴다.

---

## 2. 프록시 패턴 (Proxy Pattern)

프록시 패턴은 위의 결점을 치유하는 한 방법이다. GoF가 정의한 정규형 프록시는 객체를 세 부분으로 나눈다.

1. **인터페이스**: 클라이언트가 호출할 모든 메소드를 선언
2. **구현 클래스**: 데이터베이스에 대한 지식 없이 메소드를 구현 (업무 규칙)
3. **프록시 클래스**: 데이터베이스를 알고, 구현 클래스에 위임

```
              ┌──────────────────┐
              │ «interface»      │
              │    Product       │
              └────────△─────────┘
                       │
            ┌──────────┴──────────┐
            │                     │
    ┌───────┴──────┐      ┌───────┴────────┐
    │ DB Product   │      │ Product        │
    │ Proxy        │──▷──│ Implementation │
    │              │ delegates              │
    └──────────────┘      └────────────────┘
            │
            ▽
           DB
```

### 2.1 정규형 동작 시퀀스

```
Client          ProductDBProxy        DB        ProductImplementation
  │                  │                │                │
  │── getPrice() ───▶│                │                │
  │                  │── fetch(sku) ─▶│                │
  │                  │◀── data ──────│                │
  │                  │─── new ProductImpl(data) ───────▶│
  │                  │── getPrice() ──────────────────▶│
  │                  │◀── price ──────────────────────│
  │◀── price ───────│                │                │
```

클라이언트는 자신이 `Product`라고 생각하는 대상에 `getPrice` 메시지를 보내지만, 실제로는 `ProductDBProxy`다. 프록시는 데이터베이스에서 `ProductImplementation`을 가져와 메소드를 위임한다.

> **핵심 통찰**: 클라이언트도 `ProductImplementation`도 데이터베이스의 존재를 모른다. 양측 모두 모르게 데이터베이스가 애플리케이션 사이에 삽입된다. 이것이 프록시 패턴의 아름다움이다. 이론적으로 프록시는 협력하는 두 객체 사이에 양쪽이 눈치채지 못하게 끼어들 수 있다.

---

## 3. 쇼핑 카트에 프록시 적용하기

이제 실제로 적용해 보자. `Product`를 인터페이스로 분리한다.

```typescript
/** 상품 인터페이스. 클라이언트는 이 타입만 본다. */
interface Product {
  /** 가격 조회 */
  getPrice(): number;
  /** 이름 조회 */
  getName(): string;
  /** SKU(상품 식별 코드) 조회 */
  getSku(): string;
}
```

<details>
<summary>Java 원본</summary>

```java
public interface Product {
  public int getPrice() throws Exception;
  public String getName() throws Exception;
  public String getSku() throws Exception;
}
```
</details>

### 3.1 구현 클래스: 데이터베이스를 모른다

```typescript
class ProductImp implements Product {
  constructor(
    private readonly sku: string,
    private readonly name: string,
    private readonly price: number,
  ) {}

  getPrice(): number {
    return this.price;
  }

  getName(): string {
    return this.name;
  }

  getSku(): string {
    return this.sku;
  }
}
```

### 3.2 프록시 클래스: 데이터베이스만 안다

```typescript
class ProductProxy implements Product {
  constructor(private readonly sku: string) {}

  getPrice(): number {
    const pd = DB.getProductData(this.sku);
    return pd.price;
  }

  getName(): string {
    const pd = DB.getProductData(this.sku);
    return pd.name;
  }

  getSku(): string {
    return this.sku;
  }
}
```

<details>
<summary>Java 원본</summary>

```java
public class ProductProxy implements Product {
  private String itsSku;

  public ProductProxy(String sku) {
    itsSku = sku;
  }

  public int getPrice() throws Exception {
    ProductData pd = DB.getProductData(itsSku);
    return pd.price;
  }

  public String getName() throws Exception {
    ProductData pd = DB.getProductData(itsSku);
    return pd.name;
  }

  public String getSku() throws Exception {
    return itsSku;
  }
}
```
</details>

### 3.3 정규형이 흔들리는 지점

정규형 프록시라면 모든 메소드에서 `ProductImp`를 생성해 위임해야 한다.

```typescript
// 정규형이 요구하는 모양 — 그러나 비효율적
getPrice(): number {
  const pd = DB.getProductData(this.sku);
  const p = new ProductImp(pd.sku, pd.name, pd.price);
  return p.getPrice();
}
```

> **Uncle Bob의 경험**: `ProductImp`를 생성하는 것은 프로그래머와 컴퓨터 자원 모두에 있어 완전히 쓸데없는 짓이다. `ProductProxy`는 이미 `ProductImp` 접근 메소드가 반환할 데이터를 갖고 있다. 그러므로 `ProductImp`를 생성하고 위임할 필요가 전혀 없다. 이것은 원래 기대하던 패턴과 모델에서 프로그래머를 꾀어내어 잘못된 길로 가게 할 수 있는 또 하나의 예다. `getSku`는 한 발 더 깊숙이 들어가 데이터베이스를 건드리지도 않는다 — 이미 sku를 갖고 있는데 말이다.

캐싱을 고민할 수도 있다. 매 접근마다 DB를 친다고 느껴지기 때문이다. 하지만 이 시점에 성능 문제가 있다는 데이터는 없다. 데이터베이스 엔진 자체가 캐싱을 한다는 사실도 알려져 있다. 일부러 골치 아픈 문제를 만들지 말고, 성능 문제가 겉으로 드러날 때까지 기다려야 한다.

---

## 4. 관계(Relationship)에 프록시 적용하기

`Order`는 더 까다롭다. `Order` 인스턴스는 여러 `Item`을 포함하고 있는데, 관계형 스키마에서는 이 관계가 `Item` 테이블의 `orderId` 컬럼에 기록되어 있다. 객체 모델에서는 `Order` 안의 배열이다. 프록시는 두 형식을 변환해야 한다.

### 4.1 위임 정책

- `addItem`: **위임하지 않는다** — 프록시가 직접 DB에 Item 행을 추가한다.
- `total`: **위임한다** — 합계 정책은 업무 규칙이므로 `OrderImp.total`에 위임해야 한다. 그러기 위해 프록시가 DB에서 모든 Item을 읽어 빈 `OrderImp`에 채워 넣은 뒤 `total`을 호출한다.

> **핵심 통찰**: 프록시 구축의 제일 중요한 부분은 데이터베이스 구현부를 업무 규칙에서 분리하는 것이다. 합계를 내는 정책이 `OrderImp`에 캡슐화되기를 원하기 때문에, `total`만큼은 반드시 위임해야 한다.

### 4.2 OrderProxy 구현

```typescript
class OrderProxy implements Order {
  constructor(private readonly orderId: number) {}

  total(): number {
    const imp = new OrderImp(this.getCustomerId());
    const itemDataArray = DB.getItemsForOrder(this.orderId);
    for (const item of itemDataArray) {
      imp.addItem(new ProductProxy(item.sku), item.qty);
    }
    return imp.total();
  }

  getCustomerId(): string {
    const od = DB.getOrderData(this.orderId);
    return od.customerId;
  }

  addItem(product: Product, quantity: number): void {
    const id = new ItemData(this.orderId, quantity, product.getSku());
    DB.store(id);
  }

  getOrderId(): number {
    return this.orderId;
  }
}
```

<details>
<summary>Java 원본</summary>

```java
public class OrderProxy implements Order {
  private int orderId;

  public OrderProxy(int orderId) {
    this.orderId = orderId;
  }

  public int total() {
    try {
      OrderImp imp = new OrderImp(getCustomerId());
      ItemData[] itemDataArray = DB.getItemsForOrder(orderId);
      for (int i = 0; i < itemDataArray.length; i++) {
        ItemData item = itemDataArray[i];
        imp.addItem(new ProductProxy(item.sku), item.qty);
      }
      return imp.total();
    } catch (Exception e) {
      throw new Error(e.toString());
    }
  }

  public void addItem(Product p, int quantity) {
    try {
      ItemData id = new ItemData(orderId, quantity, p.getSku());
      DB.store(id);
    } catch (Exception e) {
      throw new Error(e.toString());
    }
  }
}
```
</details>

---

## 5. 프록시 요약

### 5.1 까다로움

정규형 프록시가 함축하는 단순 위임 모델은 좀처럼 깔끔하게 실체화되지 않는다.

- 하찮은 접근 메소드의 위임을 생략하게 된다 (이미 데이터를 갖고 있으니까).
- 1:N 관계 메소드는 위임을 지연(*delaying*)하고 다른 메소드에 미루게 된다 (`addItem` 위임이 `total`로 옮겨진 것처럼).
- 종국에는 캐싱의 망령을 마주하게 된다.

### 5.2 강력한 이점: 관심사의 분리

> **핵심 통찰**: 프록시의 그 모든 까다로운 특성에도 불구하고, 매우 강력한 이점이 한 가지 있다. 바로 '관심사의 분리'다. 업무 규칙과 데이터베이스가 완전히 분리된다. `OrderImp`는 데이터베이스의 어떤 것에도 의존하지 않는다. 데이터베이스 스키마나 엔진을 바꿔도 `Order`, `OrderImp`, 다른 업무 영역 클래스에 전혀 영향을 주지 않고 변경할 수 있다.

또한 프록시는 업무 규칙을 다른 모든 종류의 구현 관련 문제(COM, CORBA, EJB 등)에서 분리하는 데 쓸 수 있다.

---

## 6. 서드파티 API를 다루는 방법

### 6.1 기본 관계 — 직접 호출

엔지니어는 데이터베이스, 미들웨어, 클래스 라이브러리 등을 구입해 자신의 애플리케이션에서 직접 호출한다.

```
┌─────────────────┐
│  Application    │
└────────┬────────┘
         │  직접 호출
         ▽
┌─────────────────┐
│    3rd-Party    │
│      API        │
└─────────────────┘
```

시간이 흐르면 애플리케이션 코드가 점점 API 호출로 지저분해진다. API나 스키마가 바뀔 때마다 애플리케이션을 광범위하게 고쳐야 한다.

### 6.2 보호 레이어

개발자는 보호 레이어를 만들기로 한다. ODBC나 JDBC가 그런 레이어다.

```
┌─────────────────┐
│  Application    │
└────────┬────────┘
         ▽
┌─────────────────┐
│     Layer       │
└────────┬────────┘
         ▽
┌─────────────────┐
│    3rd-Party    │
│      API        │
└─────────────────┘
```

그런데 애플리케이션이 레이어에 의존하므로, 레이어를 거쳐 API로 전이 종속성(*transitive dependency - A→B, B→C이면 A는 C에 간접적으로 의존하게 되는 종속성*)이 생긴다. JDBC는 애플리케이션을 스키마 세부에서 보호하지 않는다.

### 6.3 종속성 뒤집기 — 이것이 프록시가 하는 일

```
┌─────────────────┐
│  Application    │
└─────────△───────┘
          │ 의존
┌─────────┴───────┐
│     Layer       │   ← 레이어가 애플리케이션에 의존
│   (Proxy)       │
└────────┬────────┘
         ▽
┌─────────────────┐
│    3rd-Party    │
│      API        │
└─────────────────┘
```

애플리케이션은 프록시에 전혀 의존하지 않는다. 반대로 프록시가 애플리케이션과 API 둘 다에 의존한다. 애플리케이션과 API 사이의 관계 정보는 프록시에 집중된다.

### 6.4 프록시의 부작용

이 정보 집중은 프록시가 악몽이 된다는 뜻이다. API가 변경될 때마다, 애플리케이션이 변경될 때마다 프록시도 변경된다.

> **Uncle Bob의 경험**: 차라리 자신의 악몽이 어디에 사는지 알고 있는 편이 낫다. 프록시가 없다면 악몽은 애플리케이션 코드 전체에 퍼질 것이다. 하지만 대부분의 애플리케이션에는 프록시가 필요 없다. 프록시는 아주 무거운 솔루션이다. 내가 프록시 솔루션이 쓰이는 모습을 본다면 대개는 그것을 포기하고 좀 더 간단한 것을 쓰라고 충고할 것이다.

프록시가 빛나는 경우는: 스키마와 API 둘 모두 또는 어느 한쪽에 잦은 변화가 발생하는 아주 큰 시스템이거나, 여러 종류의 데이터베이스 엔진/미들웨어 엔진 위에 얹힐 수 있어야 하는 시스템이다.

---

## 7. 천국으로의 계단(Stairway to Heaven) 패턴

프록시 외에도 종속성 뒤집기의 효과를 얻는 또 다른 패턴이다. 어댑터 패턴의 클래스 형식 변형으로, **다중 상속**을 활용한다.

### 7.1 구조

```
        ┌─────────────────────┐
        │   PersistentObject  │
        │   + write           │  (DB를 안다)
        │   + read            │
        └─────────△───────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
┌───────┴───────────┐   ┌───┴────────────────────┐
│ PersistentProduct │   │ PersistentAssembly     │
└───────△───────────┘   └─────△──────△───────────┘
        │                     │      │
        ▽ implements          ▽      ▽ implements
┌───────┴───────────┐   ┌─────┴──────┴───────────┐
│     Product       │◁──┤        Assembly        │
└───────────────────┘   └────────────────────────┘
    (업무 규칙만)           (업무 규칙만)
```

- `PersistentObject`: 데이터베이스를 아는 추상 클래스. `read`/`write` 추상 메소드 제공.
- `Product`, `Assembly`: 순수 업무 영역 객체. 영속성을 모른다.
- `PersistentProduct`: `Product`와 `PersistentObject`를 모두 상속하여 `Product`의 영속성을 구현.
- `PersistentAssembly`: `Assembly`와 `PersistentProduct`를 상속. **다이아몬드 상속**이 발생한다.

### 7.2 다이아몬드 상속과 가상 상속

`PersistentAssembly`는 `Assembly`를 통해서도 `Product`를 상속받고, `PersistentProduct`를 통해서도 `Product`를 상속받는다. C++에서는 가상 상속(*virtual inheritance*)을 사용해 `Product`의 두 인스턴스가 합쳐지도록 한다. 익살스럽게는 '치명적인 죽음의 다이아몬드(*deadly diamond of death*)'라고 부른다.

### 7.3 사용 방식

업무 규칙에서 영속성으로의 종속성이 없다. 영속화가 필요한 부분은 동적 캐스트로 알아본다.

```cpp
PersistentObject* o = dynamic_cast<PersistentObject*>(product);
if (o) {
  o->write();
}
```

> **핵심 통찰**: 이 패턴의 장점은 데이터베이스 정보를 애플리케이션의 업무 규칙과 완벽하게 분리한다는 것이다. `Product`와 `Assembly` 클래스에는 영속성의 흔적이 전혀 없다. 업무 규칙에서 영속성 메커니즘으로의 어떤 종속성도 존재하지 않는다. 이것이 이 패턴의 가장 중요한 부분이다.

### 7.4 C++ 코드 스케치

C++에서의 핵심 구조만 발췌한다.

```cpp
// Product — 영속성 모른다
class Product {
public:
  Product(const string& name);
  virtual ~Product();
  const string& getName() const { return itsName; }
private:
  string itsName;
};

// Assembly — Product를 가상 상속
class Assembly : public virtual Product {
public:
  Assembly(const string& name, const string& assyCode);
  const string& getAssyCode() const { return itsAssyCode; }
private:
  string itsAssyCode;
};

// PersistentObject — DB만 안다. 템플릿 메소드로 write 제어
class PersistentObject {
public:
  virtual ~PersistentObject();
  virtual void write(ostream&) const;
protected:
  virtual void writeFields(ostream&) const = 0;
private:
  virtual void writeHeader(ostream&) const = 0;
  virtual void writeFooter(ostream&) const = 0;
};

void PersistentObject::write(ostream& s) const {
  writeHeader(s);
  writeFields(s);
  writeFooter(s);
}

// PersistentProduct — Product + PersistentObject
class PersistentProduct : public virtual Product,
                          public PersistentObject {
protected:
  virtual void writeFields(ostream& s) const {
    s << "<NAME>" << getName() << "</NAME>";
  }
private:
  virtual void writeHeader(ostream& s) const { s << "<PRODUCT>"; }
  virtual void writeFooter(ostream& s) const { s << "</PRODUCT>"; }
};

// PersistentAssembly — Assembly + PersistentProduct
class PersistentAssembly : public Assembly, public PersistentProduct {
protected:
  virtual void writeFields(ostream& s) const {
    PersistentProduct::writeFields(s);
    s << "<ASSYCODE>" << getAssyCode() << "</ASSYCODE>";
  }
private:
  virtual void writeHeader(ostream& s) const { s << "<ASSEMBLY>"; }
  virtual void writeFooter(ostream& s) const { s << "</ASSEMBLY>"; }
};
```

`PersistentAssembly::writeFields`가 `PersistentProduct::writeFields`를 호출해 `Product` 부분의 쓰기 기능을 재사용한다. 이것이 '계단'의 의미다 — 한 단씩 쌓아 올린다.

### 7.5 한계

> **Uncle Bob의 경험**: 나는 천국으로의 계단 패턴이 많은 상황에서 좋은 결과를 내는 모습을 봐 왔다. 구성하기도 상대적으로 쉽고, 업무 규칙을 포함하는 객체에 최소한의 영향만 줄 수 있다. 반면, 구현의 다중 상속을 지원하는 C++ 같은 언어 사용을 필요로 한다.

Java/TypeScript처럼 단일 상속 + 인터페이스 모델인 언어에서는 이 패턴을 그대로 옮길 수 없다. Mixin이나 Decorator 등 다른 패턴으로 우회해야 한다.

---

## 8. 데이터베이스와 쓸 수 있는 그 밖의 패턴

데이터베이스와 업무 규칙을 분리하는 패턴은 프록시와 천국으로의 계단만이 아니다.

### 8.1 확장 객체(Extension Object)

확장된 객체를 DB에 기록하는 방법을 아는 확장 객체가 있다. "Database" 키로 확장을 요청한 뒤 `write`를 호출한다.

```typescript
const e = product.getExtension('Database');
if (e !== null) {
  const dwe = e as DatabaseWriterExtension;
  dwe.write();
}
```

### 8.2 비지터(Visitor)

방문을 받은 객체를 DB에 기록하는 비지터 계층을 만든다.

```typescript
const product = /* ... */;
const dwv = new DatabaseWriterVisitor();
product.accept(dwv);
```

### 8.3 데코레이터(Decorator)

두 가지 방식이 있다.

1. 업무 객체를 장식해 `read`/`write` 메소드를 주는 방법
2. 자신을 읽고 쓰는 방법을 아는 데이터 객체를 장식해 업무 규칙을 주는 방법 (OODB에서 드문 방식)

### 8.4 퍼사드(Facade) — Uncle Bob이 좋아하는 시작점

가장 단순하고 효과적이다. 단점은 업무 규칙 객체를 DB와 결합시킨다는 점이다.

```
┌─────────────────────┐
│      Product        │◀──┐
└─────────────────────┘   │
┌─────────────────────┐   │  uses
│     Assembly        │◀──┤
└─────────────────────┘   │
                          │
┌─────────────────────┐   │
│  DatabaseFacade     │───┘
│  + readProduct      │
│  + writeProduct     │
│  + readAssembly     │
│  + writeAssembly    │
└─────────────────────┘
```

`DatabaseFacade`는 객체의 접근/변경 메소드를 사용해 `read`/`write`를 구현하므로 객체를 안다. 객체도 종종 퍼사드의 `read`/`write`를 호출하므로 퍼사드를 안다.

큰 애플리케이션에서는 결합 문제를 일으킬 수 있지만, 작은 애플리케이션이나 거대해지기 직전의 애플리케이션에서는 아주 효율적이다. 퍼사드는 리팩토링하기 아주 쉬워서, 일단 퍼사드로 시작했다가 나중에 다른 패턴으로 옮길 수 있다.

---

## 9. 자주 하는 실수

| 안티패턴 | 문제 | 해결 |
|---|---|---|
| 업무 규칙 코드에 SQL/JDBC 직접 호출 | SRP/DIP 위반, 스키마 변경이 도메인을 흔든다 | 인터페이스로 분리, 프록시 또는 퍼사드 도입 |
| 정규형 프록시를 맹목적으로 따라 모든 메소드에서 구현 클래스 생성 | 데이터 중복, 컴퓨터 자원 낭비 | 이미 가진 데이터는 직접 반환, 업무 규칙이 필요한 메소드만 위임 |
| 성능 걱정으로 처음부터 캐시 도입 | 복잡도 증가, 실제로 더 느려질 수 있음 | DB 엔진 자체가 캐싱한다. 측정 후 도입 |
| 모든 시스템에 프록시 적용 | 프록시는 무겁고 변경에 취약함 | 대부분은 퍼사드로 충분. 정말 큰/변동 많은 시스템에만 프록시 |
| 천국으로의 계단을 단일 상속 언어에서 무리하게 구현 | 다중 상속이 필요한 패턴 | Java/TS에서는 다른 패턴(데코레이터, 퍼사드) 선택 |
| 필요해질 것이라 예상해 미리 프록시/계단 구축 | YAGNI 위반, 시간 낭비 | 퍼사드로 시작해 필요할 때 리팩토링 |

---

## 10. 패턴 선택 가이드

| 상황 | 추천 패턴 |
|---|---|
| 작은 애플리케이션, 거대해지기 직전 | 퍼사드 — 단순, 효과적, 리팩토링 쉽다 |
| 큰 시스템, 스키마/API가 자주 변경됨 | 프록시 — 업무 규칙 완벽 분리, 변경 영향을 한 곳에 집중 |
| 다양한 DB/미들웨어 엔진을 갈아끼워야 함 | 프록시 |
| C++/다중 상속 언어 + 영속성 완전 분리가 필요 | 천국으로의 계단 |
| 객체별로 자료형이 다양하고 동작이 늘어남 | 비지터 |
| 객체의 직교적인 기능을 옵셔널하게 결합 | 데코레이터 |
| 확장 가능한 책임을 객체에 추가 | 확장 객체 |

---

## 요약

- **장벽 문제**: 데이터베이스, 네트워크, 서드파티 API 같은 장벽이 업무 규칙과 섞이면 SRP, DIP, CCP를 위반하고 시스템을 변경하기 어렵게 만든다.

- **프록시 패턴**: 인터페이스 + 구현 + 프록시 세 부분으로 나눠, 양쪽 모두 모르게 데이터베이스를 끼워 넣는다. 업무 규칙과 인프라의 관심사를 완전히 분리한다.

- **정규형 vs 실제**: GoF 정규형은 항상 구현 객체를 생성하고 위임하지만, 실제로는 (a) 단순 접근자는 직접 반환, (b) 1:N 관계는 위임 지연 등 변형이 자연스럽게 일어난다.

- **위임 정책**: 업무 규칙(`total` 같은 계산)은 반드시 구현 클래스에 위임해야 한다. 데이터 변형(`addItem` 같은 저장)은 프록시가 직접 처리한다.

- **캐싱은 두려움이 아니라 측정에서**: 프록시가 매 호출마다 DB를 친다고 처음부터 캐시를 만들지 말 것. DB 엔진이 캐싱한다. 성능 문제가 증명되었을 때 도입한다.

- **종속성 뒤집기**: 프록시는 애플리케이션이 API에 의존하는 방향을 뒤집어, API에 대한 모든 지식을 프록시에 집중시킨다. 악몽이 한 곳에 사는 편이 코드 전체에 퍼진 것보다 낫다.

- **천국으로의 계단**: 다중 상속을 사용해 업무 객체 계층과 영속성 계층을 다이아몬드 형태로 결합한다. 업무 규칙 객체에는 영속성의 흔적이 전혀 없다는 큰 장점이 있지만, C++ 같은 다중 상속 언어가 필요하다.

- **그 밖의 선택지**: 확장 객체, 비지터, 데코레이터, 퍼사드. 특히 **퍼사드는 가장 단순하고 가장 좋은 시작점**이다.

- **YAGNI 정신**: 프록시나 천국으로의 계단이 필요할 것이라 예상해 미리 구축하지 말 것. 일단 퍼사드로 시작하고, 필요해지면 리팩토링한다. 그렇게 하면 시간을 아끼고 문제를 줄일 수 있다.
