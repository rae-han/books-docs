# Chapter 15: Facade and Mediator (퍼사드와 미디에이터)

## 핵심 질문

어떻게 한 객체가 다른 객체들의 그룹에 정책(*policy - 객체들이 따라야 할 사용 규약과 절차*)을 부과할 수 있는가? 정책을 "위로부터 가시적으로" 적용하는 것과 "아래로부터 비가시적으로" 적용하는 것은 각각 어떤 상황에서 적절한가? 퍼사드(*Facade - 외관, 건물의 정면*)와 미디에이터(*Mediator - 중재자*)는 같은 목표를 어떻게 다른 방식으로 달성하는가?

> 상징이 체면을 지켜주는 외벽이 되어서 꿈의 외설스러움을 숨겨준다.<br>— 메이슨 쿨리(Mason Cooley)

---

## 1. 두 패턴의 공통점과 차이

이 장에서 논의할 두 패턴은 공통적인 용도를 갖는다. 둘 다 **어떤 종류의 정책을 다른 객체들의 그룹에 부과**한다. 다만 그 방식이 정반대다.

| 측면 | 퍼사드(Facade) | 미디에이터(Mediator) |
|------|----------------|----------------------|
| 정책 적용 방향 | 위에서 아래로 | 아래에서 위로 |
| 가시성 | 가시적(visible) | 비가시적(invisible) |
| 강제성 | 강제적(imposing) | 허용적·암묵적 |
| 사용자 인식 | 사용자는 퍼사드의 존재를 알고 그것을 거쳐야 한다 | 사용자는 미디에이터의 존재를 모른다 |
| 정책의 성격 | 규정(convention) — 합의된 약속 | 기정사실(fait accompli) — 이미 일어나는 일 |

> **핵심 통찰**: 퍼사드는 위로부터 정책을 적용하고, 미디에이터는 아래로부터 정책을 적용한다. 퍼사드의 사용은 가시적이고 강제적인 반면, 미디에이터의 사용은 비가시적이고 허용적이다. 정책의 "어디서, 어떻게" 보이는지가 두 패턴을 가르는 핵심이다.

---

## 2. 퍼사드 패턴

### 2.1 정의와 의도

퍼사드 패턴은 **복잡하고 일반적인 인터페이스를 가진 객체 그룹에 간단하고 구체적인 인터페이스를 제공**하고자 할 때 사용한다. 객체 그룹의 모든 기능을 직접 노출하는 대신, 애플리케이션이 실제로 필요로 하는 좁고 명확한 인터페이스만 외부로 드러낸다.

> 역자 주: "퍼사드(Facade)"는 외관, 건물의 정면 등의 뜻이 있다. 패턴의 의미로 보면 "창구"로 이해하는 것이 가장 적당하다.

### 2.2 데이터베이스 퍼사드 예제

`Application`이 데이터베이스에 접근할 때 `java.sql` 패키지의 복잡하고 일반적인 인터페이스를 직접 다루지 않게 하기 위해 `DB`라는 퍼사드 클래스를 둔다. `DB`는 `ProductData`에게 아주 간단한 인터페이스를 제공하면서, 그 뒤에 `java.sql`의 모든 일반성과 복잡성을 숨긴다.

```
┌─────────────────┐         ┌────────────────┐
│  Application    │────────▶│      DB        │
└────────┬────────┘         ├────────────────┤
         │                  │ + store(pd)    │
         │                  │ + getProduct() │
         │                  │ + deletePro()  │
         ▼                  └────────┬───────┘
   ┌──────────┐                      │
   │ Product  │                      ▼
   │  Data    │              ┌────────────────┐
   └──────────┘              │   java.sql     │
                             ├────────────────┤
                             │ Connection     │
                             │ Statement      │
                             │ DriverManager  │
                             │ ResultSet      │
                             │ PreparedStmt   │
                             │ SQLException   │
                             └────────────────┘
```

<details>
<summary>원문 Java 코드 (개념 스케치)</summary>

```java
// Java
public class DB {
    public static void store(ProductData pd) {
        // Connection, Statement, PreparedStatement 등을 사용해
        // ProductData를 데이터베이스 필드로 변환하고 저장
    }

    public static ProductData getProductData(String sku) {
        // 적절한 SELECT 질의를 구성, 결과를 ProductData로 변환
        return null;
    }

    public static void deleteProductData(String sku) {
        // DELETE 명령 구성과 실행
    }
}
```

</details>

```typescript
// TypeScript
class DB {
    static store(pd: ProductData): void {
        // Connection, Statement 등을 사용해
        // ProductData를 데이터베이스 필드로 변환하고 저장
    }

    static getProductData(sku: string): ProductData {
        // 적절한 SELECT 질의를 구성, 결과를 ProductData로 변환
        return new ProductData();
    }

    static deleteProductData(sku: string): void {
        // DELETE 명령 구성과 실행
    }
}
```

### 2.3 퍼사드가 적용하는 정책

`DB` 같은 퍼사드는 `java.sql` 패키지의 사용법에 아주 많은 정책을 적용한다:

- **연결 관리 정책**: 데이터베이스 연결을 초기화하고 끊는 방법을 알고 있다
- **변환 정책**: `ProductData`의 멤버들을 데이터베이스의 필드로, 또 그 반대로 변환하는 방법을 알고 있다
- **질의 구성 정책**: 데이터베이스를 조작하는 적절한 질의와 명령을 구성하는 방법을 알고 있다

그리고 이 모든 복잡성을 사용자에게 보이지 않도록 숨긴다. `Application`의 관점에서 보면, `java.sql`은 존재하지도 않는다. 퍼사드 뒤에 숨겨져 있는 것이다.

### 2.4 가시적·강제적 정책

퍼사드 패턴의 사용은 개발자가 **"모든 데이터베이스 호출이 `DB`를 통과해야 한다"**는 규정을 채택했다는 사실을 내포한다. `Application` 코드의 어떤 부분이 퍼사드를 통해서가 아니라 `java.sql`로 바로 간다면, 이것은 규정을 위반하는 것이다.

> **핵심 통찰**: 퍼사드는 자신의 정책을 `Application`에 적용한다. 규정에 의해, `DB`는 `java.sql`에 있는 기능들의 **독점 중개인**이 된다. 이 독점성은 컴파일러가 강제해 주지는 않지만, 팀의 약속과 코드 리뷰에 의해 유지된다.

---

## 3. 미디에이터 패턴

### 3.1 정의와 의도

미디에이터 패턴도 역시 정책을 적용한다. 그러나 퍼사드가 자신의 정책을 **가시적이고 강제적인** 방식으로 적용하는 반면, 미디에이터는 자신의 정책을 **은밀하고 강제적이지 않은** 방식으로 적용한다. 정책이 적용되는 대상 객체들은 미디에이터의 존재 자체를 알지 못한다.

### 3.2 QuickEntryMediator 예제

`QuickEntryMediator` 클래스는 조용히 이면에서 텍스트 입력 필드(`JTextField`)를 어떤 리스트(`JList`)와 결합한다. 텍스트 입력 필드에 입력을 하면, 입력한 것과 일치하는 리스트의 첫 요소가 하이라이트된다. 이것은 단축형의 입력으로 리스트의 요소를 빨리 선택할 수 있게 해 준다.

```
   ┌────────────┐                   ┌─────────────┐
   │   JList    │                   │ JTextField  │
   └─────▲──────┘                   └──────▲──────┘
         │                                 │
         │  (참조)                  (참조) │
         │                                 │
         │       ┌─────────────────┐       │
         └───────│  QuickEntry     │───────┘
                 │   Mediator      │
                 └────────┬────────┘
                          │ 등록(register)
                          ▼
                 ┌─────────────────┐
                 │  «anonymous»    │
                 │ DocumentListener│
                 └─────────────────┘
```

<details>
<summary>원문 Java 코드</summary>

```java
// Java
package utility;

import javax.swing.JList;
import javax.swing.JTextField;
import javax.swing.ListModel;
import javax.swing.event.DocumentEvent;
import javax.swing.event.DocumentListener;

/**
 * 이 클래스는 JTextField 하나와 JList 하나를 받는다.
 * 사용자가 JList에 있는 항목들의 접두어(prefix)를 JTextField에 입력한다고 가정한다.
 * JTextField의 현재 접두어와 일치하는 JList의 첫 번째 항목을 자동으로 선택한다.
 *
 * 만약 JTextField가 null이거나, 접두어가 JList에 있는 어떤 원소와도 일치하지 않으면
 * JList의 선택은 지워진다. 이 객체를 호출하기 위한 방법은 없다.
 * 그냥 생성하고, 잊어버리면 된다(하지만 가비지 컬렉션에 의해 없어지도록 놔두지 말자).
 *
 * 예제:
 *   JTextField t = new JTextField();
 *   JList l = new JList();
 *   QuickEntryMediator qem = new QuickEntryMediator(t, l); // 이게 전부다.
 *
 * @author Robert C. Martin, Robert S. Koss
 * @date 30 Jun, 1999 21:13 (SLAC)
 */
public class QuickEntryMediator {
    public QuickEntryMediator(JTextField t, JList l) {
        itsTextField = t;
        itsList = l;
        itsTextField.getDocument().addDocumentListener(new DocumentListener() {
            public void changedUpdate(DocumentEvent e) {
                textFieldChanged();
            }
            public void insertUpdate(DocumentEvent e) {
                textFieldChanged();
            }
            public void removeUpdate(DocumentEvent e) {
                textFieldChanged();
            }
        });
    }

    private void textFieldChanged() {
        String prefix = itsTextField.getText();
        if (prefix.length() == 0) {
            itsList.clearSelection();
            return;
        }
        ListModel m = itsList.getModel();
        boolean found = false;
        for (int i = 0; found == false && i < m.getSize(); i++) {
            Object o = m.getElementAt(i);
            String s = o.toString();
            if (s.startsWith(prefix)) {
                itsList.setSelectedValue(o, true);
                found = true;
            }
        }
        if (!found) {
            itsList.clearSelection();
        }
    }

    private JTextField itsTextField;
    private JList itsList;
}
```

</details>

```typescript
// TypeScript (개념적 대응 — 브라우저 환경의 input/select 사용)
/** 텍스트 입력 접두어와 일치하는 첫 옵션을 선택하는 미디에이터. */
class QuickEntryMediator {
    private readonly itsTextField: HTMLInputElement;
    private readonly itsList: HTMLSelectElement;

    constructor(textField: HTMLInputElement, list: HTMLSelectElement) {
        this.itsTextField = textField;
        this.itsList = list;

        // textField에 리스너를 등록한다 — list와 textField는 미디에이터를 모른다
        this.itsTextField.addEventListener('input', () => {
            this.textFieldChanged();
        });
    }

    private textFieldChanged(): void {
        const prefix = this.itsTextField.value;
        if (prefix.length === 0) {
            this.itsList.selectedIndex = -1;
            return;
        }

        let found = false;
        for (let i = 0; !found && i < this.itsList.options.length; i++) {
            const option = this.itsList.options[i];
            if (option.text.startsWith(prefix)) {
                this.itsList.selectedIndex = i;
                found = true;
            }
        }

        if (!found) {
            this.itsList.selectedIndex = -1;
        }
    }
}

// 사용 예 — 생성하고 잊어버리면 된다
const t = document.querySelector<HTMLInputElement>('#text')!;
const l = document.querySelector<HTMLSelectElement>('#list')!;
new QuickEntryMediator(t, l); // 이게 전부다.
```

### 3.3 동작 흐름

`QuickEntryMediator`의 인스턴스는 `JList` 하나와 `JTextField` 하나로 생성된다. 이 미디에이터는 익명 `DocumentListener`를 `JTextField`에 등록한다. 이 리스너는 텍스트에 변화가 있을 때마다 `textFieldChanged`를 호출한다. 그러면 이 메서드는 이 텍스트를 접두어로 갖는 `JList`의 원소를 찾아 그것을 선택한다.

### 3.4 비가시적·허용적 정책

> **핵심 통찰**: `JList`와 `JTextField`의 사용자는 이 미디에이터가 존재하는지 알지 못한다. 미디에이터는 조용히 앉아, 자신의 정책을 이들 객체의 허락이나 인식 없이 적용한다. 정책이 적용되는 객체들은 자신이 정책의 대상임을 인식조차 하지 않는다.

이 점이 퍼사드와 결정적으로 다르다. 퍼사드는 "이걸 거쳐서 가야 한다"는 약속 위에 서지만, 미디에이터는 "어떻게 거쳐 가는지" 자체를 객체들에게서 감춘다.

---

## 4. 두 패턴의 비교 — 언제 무엇을 쓸 것인가

### 4.1 결정 기준

| 상황 | 적합한 패턴 |
|------|-------------|
| 정책이 팀 전체의 규정으로 명문화되어야 하는 경우 | 퍼사드 |
| 모든 접근 경로를 하나의 창구로 강제하고 싶은 경우 | 퍼사드 |
| 사용자가 자신을 통제하는 정책의 존재를 알 필요가 없는 경우 | 미디에이터 |
| 객체들 사이의 상호작용 자체가 정책인 경우 | 미디에이터 |
| 기존 객체들을 변경하지 않고 이면에서 정책을 끼워 넣고 싶은 경우 | 미디에이터 |

### 4.2 정책의 무게

- **퍼사드의 정책**: 어떤 규정의 중심이 되며, 모든 사람은 그 아래에 있는 객체들이 아니라 이 퍼사드를 사용하기로 합의한다. 정책은 **합의(convention)**의 산물이다.
- **미디에이터의 정책**: 사용자에게 감춰져 있다. 이것의 정책은 규정의 문제라기보다는 **기정사실(fait accompli)**이다. 사용자가 인식하든 안 하든, 이미 적용되고 있다.

> **Uncle Bob의 경험**: 정책 적용이 크고 가시적이어야 하는 경우에는 퍼사드를 사용해 위로부터 행해질 수 있고, 교묘함과 재량이 필요한 경우에는 미디에이터가 좀 더 나은 선택이 될 것이다. 두 패턴은 경쟁 관계가 아니라, "정책이 얼마나 드러나야 하는가"라는 한 축의 양 극단이다.

---

## 5. 결론

정책 적용이 크고 가시적이어야 하는 경우에는 퍼사드를 사용해 위로부터 행해질 수 있고, 교묘함과 재량이 필요한 경우에는 미디에이터가 좀 더 나은 선택이 될 것이다. 퍼사드는 보통 어떤 규정의 중심이 되며, 모든 사람은 그 아래에 있는 객체들이 아니라 이 퍼사드를 사용하기로 합의한다. 한편, 미디에이터는 사용자에게 감춰져 있다. 이것의 정책은 규정의 문제라기보다는 기정사실이다.

---

## 요약

- 퍼사드와 미디에이터는 모두 **객체들의 그룹에 정책을 부과**한다는 공통점을 가진다
- 차이는 **정책 적용 방향과 가시성**이다 — 퍼사드는 위에서 가시적·강제적으로, 미디에이터는 아래에서 비가시적·허용적으로
- **퍼사드**는 복잡하고 일반적인 인터페이스 위에 간단하고 구체적인 인터페이스를 씌운다. 예: `DB` 클래스가 `java.sql`을 감싸 `Application`에게 좁은 창구만 제공
- 퍼사드의 정책은 **합의된 규정**이다 — "모든 호출은 퍼사드를 거친다"
- **미디에이터**는 객체들 사이의 상호작용을 캡슐화하되, 그 객체들이 미디에이터의 존재를 모르게 한다. 예: `QuickEntryMediator`가 `JTextField`와 `JList`를 결합
- 미디에이터의 정책은 **기정사실**이다 — 객체들의 허락이나 인식 없이 적용된다
- 선택 기준: **정책이 얼마나 드러나야 하는가** — 크고 가시적이면 퍼사드, 교묘하고 재량적이면 미디에이터
