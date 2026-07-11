# Chapter 14: Appendix — Leftover Patterns (기타 패턴)

## 핵심 질문

- GoF 23개 중 이 책 본문에서 다루지 않은 **나머지 9개 패턴**은 각각 어떤 문제를 푸는가?
- 이들은 언제 유용하고, 어떤 단점이 있는가?
- (TS/JS) 이 중 프런트엔드/백엔드 실전에서 자주 만나는 것은? (빌더·책임 연쇄·프로토타입 등)

> **참고**: 이 장은 부록 성격으로, 덜 자주 쓰이지만 상황에 따라 유용한 9개 패턴을 **빠르게 훑는다**. 각 패턴을 "정의 · 시나리오 · 장단점" 중심으로 간결히 정리한다.

---

## 1. 브리지 패턴 (Bridge)

> **정의**: 구현뿐 아니라 **추상화 부분까지** 독립적으로 변경해야 할 때, 둘을 서로 다른 클래스 계층으로 **분리(구성으로 연결)** 한다.

**시나리오**: 만능 리모컨. 리모컨(추상화)도 개선되고, TV 종류(구현)도 다양하다. 둘 다 바뀔 수 있다.

```typescript
// 구현 계층 (TV)
interface TV {
  on(): void;
  off(): void;
  tuneChannel(ch: number): void;
}

// 추상화 계층 (리모컨) — TV를 "구성"으로 보유(브리지)
abstract class RemoteControl {
  constructor(protected tv: TV) {} // 브리지
  on(): void { this.tv.on(); }
  off(): void { this.tv.off(); }
  abstract setChannel(ch: number): void;
}

class ConcreteRemote extends RemoteControl {
  private currentStation = 0;
  setChannel(ch: number): void {
    this.currentStation = ch;
    this.tv.tuneChannel(ch); // 구현에 위임
  }
  nextChannel(): void { this.setChannel(this.currentStation + 1); }
}
```

- **장점**: 추상화와 구현을 독립적으로 확장. 구현 변경이 클라이언트에 영향 없음.
- **단점**: 디자인이 복잡해진다. **활용**: 여러 플랫폼용 그래픽/윈도우 시스템.

---

## 2. 빌더 패턴 (Builder)

> **정의**: 복잡한 객체의 **생성 단계를 캡슐화**하여, 여러 단계·절차를 거쳐 객체를 만든다(팩토리는 한 단계에 처리).

**시나리오**: 테마파크 휴가 계획(호텔·입장권·식사·이벤트를 날짜별로 임의 조합).

```typescript
class VacationBuilder {
  private vacation = new Vacation();
  buildDay(date: string): this { /* ... */ return this; }
  addHotel(date: string, hotel: string): this { /* ... */ return this; }
  addTickets(event: string): this { /* ... */ return this; }
  getVacationPlanner(): Vacation { return this.vacation; }
}

// 메서드 체이닝(fluent)으로 단계별 조립
const planner = new VacationBuilder()
  .buildDay("2026-07-12")
  .addHotel("2026-07-12", "Grand Facadian")
  .addTickets("Patterns on Ice")
  .getVacationPlanner();
```

- **장점**: 복합 객체 생성 과정 캡슐화, 내부 구조를 클라이언트로부터 보호.
- **단점**: 팩토리보다 클라이언트가 더 많이 알아야 함.

> **TS 통찰**: **fluent builder**(메서드 체이닝, `this` 반환)는 TS에서 매우 흔하다 — 쿼리 빌더(Prisma·Knex·Drizzle), 테스트 픽스처, 설정 객체 등. 옵션이 많은 객체를 안전하게 조립할 때 유용하다.

---

## 3. 책임 연쇄 패턴 (Chain of Responsibility)

> **정의**: 하나의 요청을 **여러 객체(핸들러) 사슬**이 차례로 검토해, 처리하거나 다음 핸들러로 넘긴다.

**시나리오**: 뽑기 회사에 쏟아지는 이메일 분류(스팸/팬레터/항의/신규설치).

```typescript
abstract class Handler {
  protected next?: Handler;
  setNext(handler: Handler): Handler {
    this.next = handler;
    return handler; // 체이닝
  }
  handle(email: Email): void {
    if (this.next) { this.next.handle(email); } // 못 처리하면 다음으로
  }
}

class SpamHandler extends Handler {
  handle(email: Email): void {
    if (email.isSpam) { email.delete(); }
    else { super.handle(email); } // 다음 핸들러로
  }
}

// 사슬 구성: spam → fan → complaint → newLoc
spamHandler.setNext(fanHandler).setNext(complaintHandler).setNext(newLocHandler);
```

- **장점**: 요청 발신자와 수신자를 분리. 사슬 구성·순서를 동적으로 변경.
- **단점**: 요청이 처리된다는 보장이 없음(사슬 끝까지 갈 수 있음), 디버깅이 어려움.

> **TS 통찰**: **Express/Koa 미들웨어**(`app.use(...)`, `next()`)가 바로 책임 연쇄다. 각 미들웨어가 요청을 처리하거나 `next()`로 넘긴다. 이벤트 버블링(DOM)도 유사하다.

---

## 4. 플라이웨이트 패턴 (Flyweight)

> **정의**: 클래스 인스턴스 **하나로 여러 가상 인스턴스**를 제공한다. 공유되는 **본질 상태(intrinsic)** 는 한곳에, 개별 상태(extrinsic)는 밖에 둔다.

**시나리오**: 조경 앱에서 나무 수천 그루. 각 `Tree` 객체를 다 만들면 느려진다.

```typescript
// 상태 없는 Tree 하나만 공유, 상태(좌표·나이)는 외부 배열에
class Tree {
  display(x: number, y: number, age: number): void { /* 그리기 */ }
}
class TreeManager {
  private tree = new Tree();
  private treeData: [number, number, number][] = []; // [x, y, age]
  displayTrees(): void {
    for (const [x, y, age] of this.treeData) {
      this.tree.display(x, y, age); // 인스턴스 하나로 모두 처리
    }
  }
}
```

- **장점**: 인스턴스 수를 줄여 **메모리 절약**. 여러 가상 객체 상태를 한곳에 관리.
- **단점**: 인스턴스별로 다르게 행동하게 만들 수 없다. **활용**: 같은 종류의 객체가 아주 많을 때.

---

## 5. 인터프리터 패턴 (Interpreter)

> **정의**: 간단한 **언어의 문법을 클래스로 표현**하고, 그 언어를 해석하는 인터프리터를 만든다.

**시나리오**: 아이들에게 오리를 조종하는 미니 언어(`right; while (daylight) fly; quack;`)를 가르친다. 문법 규칙(expression, sequence, command, repetition)을 각각 클래스로.

```typescript
interface Expression {
  interpret(context: Context): void;
}
class QuackCommand implements Expression {
  interpret(_context: Context): void { /* 꽥 */ }
}
class Sequence implements Expression {
  constructor(private expr1: Expression, private expr2: Expression) {}
  interpret(context: Context): void {
    this.expr1.interpret(context);
    this.expr2.interpret(context);
  }
}
```

- **장점**: 문법을 클래스로 표현해 언어를 쉽게 구현·확장.
- **단점**: 문법 규칙이 많아지면 매우 복잡. 그때는 **파서/컴파일러 생성기**가 낫다. **활용**: 간단한 스크립트 언어, 규칙 엔진.

---

## 6. 중재자 패턴 (Mediator)

> **정의**: 서로 관련된 객체들의 **복잡한 통신·제어를 중재자 한 곳으로 집중**시킨다.

**시나리오**: 자동화 주택. 알람·커피포트·달력·스프링클러가 서로를 직접 알면(다대다) 규칙이 얽힌다. 중재자를 두면 각 가전은 중재자에게만 상태를 알린다.

```typescript
class Mediator {
  // 모든 제어 로직을 여기 집중
  onAlarmEvent(): void {
    if (this.calendar.isWeekend()) { /* 커피 안 끓임 */ }
    else { this.coffeePot.startCoffee(); }
    if (this.calendar.isTrashDay()) { this.alarm.resetEarlier(); }
  }
}
// 각 가전은 중재자에게만 알림 (서로를 모름)
```

- **장점**: 객체 간 결합을 크게 줄여 재사용성 향상, 제어 로직을 한곳에서 관리.
- **단점**: 중재자 자체가 너무 복잡해질 수 있음. **활용**: 서로 얽힌 GUI 구성 요소 관리.

---

## 7. 메멘토 패턴 (Memento)

> **정의**: 객체를 **이전 상태로 복구**할 수 있도록, 상태를 별도 객체(메멘토)에 저장한다. (실행 취소, 세이브)

**시나리오**: RPG 게임 세이브. 캐릭터가 죽기 전 상태로 복구.

```typescript
// 메멘토: 상태를 담는 별도 객체 (캡슐화 유지)
class GameMemento {
  constructor(readonly savedState: string) {}
}
class Game {
  private state = "";
  save(): GameMemento { return new GameMemento(this.state); } // 상태 추출
  restore(memento: GameMemento): void { this.state = memento.savedState; }
}
```

- **장점**: 저장 상태를 **핵심 객체와 분리**해 안전, 핵심 객체의 캡슐화 유지, 복구 구현이 쉬움.
- **단점**: 상태 저장·복구에 시간/메모리 소요. **활용**: 자바에서는 직렬화로 상태 저장.

> **TS 통찰**: 커맨드 패턴(6장)의 `undo`와 결합해 실행 취소 히스토리를 구현하거나, Redux의 상태 스냅샷/타임트래블 디버깅이 메멘토의 정신이다.

---

## 8. 프로토타입 패턴 (Prototype)

> **정의**: 인스턴스 생성 비용이 크거나 복잡할 때, **기존 인스턴스를 복사(clone)** 해 새 인스턴스를 만든다.

**시나리오**: RPG에서 지형에 맞춰 동적으로 생성되는 몬스터. 클라이언트는 몬스터의 구체 타입을 모른 채 복제로 생성.

```typescript
interface Monster {
  clone(): Monster; // 자신을 복제
}
class MonsterRegistry {
  getMonster(type: string): Monster {
    const prototype = this.registry.get(type)!;
    return prototype.clone(); // 등록된 원형을 복제해 반환
  }
}
```

- **장점**: 클라이언트가 구체 타입·생성 과정을 몰라도 객체 생성. 새로 만드는 것보다 복사가 효율적일 수 있음.
- **단점**: 깊은 복사(deep clone)가 복잡할 수 있음.

> **TS 통찰**: **자바스크립트 자체가 프로토타입 기반 언어**다. `Object.create(proto)`로 프로토타입 상속을, **`structuredClone(obj)`** 로 깊은 복사를 언어가 직접 지원한다 — 이 패턴이 언어에 내장된 셈이다.

---

## 9. 비지터 패턴 (Visitor)

> **정의**: 다양한 객체 구조에 **새 기능을 추가**하되, 그 객체들의 클래스를 **변경하지 않는다**(캡슐화가 덜 중요할 때).

**시나리오**: 메뉴/메뉴항목/재료 컴포지트 구조에 "영양 정보(칼로리·단백질·탄수화물)" 기능을 추가. 각 클래스에 메서드를 다 추가하면 여러 곳을 고쳐야 한다. → **비지터**가 트래버서와 함께 구조를 순회하며 상태를 모아, 새 기능은 비지터에만 추가.

```typescript
interface Visitor {
  visitMenuItem(item: MenuItem): void;
  visitIngredient(ingredient: Ingredient): void;
}
class NutritionVisitor implements Visitor { // 새 기능은 여기만 추가
  visitMenuItem(item: MenuItem): void { /* 칼로리 계산 */ }
  visitIngredient(ingredient: Ingredient): void { /* ... */ }
}
// 각 요소는 getState()로 상태를 노출하고, 비지터를 받아들인다
```

- **장점**: **구조를 바꾸지 않고** 새 기능 추가, 관련 코드를 비지터 한곳에 모음.
- **단점**: 복합 클래스의 **캡슐화가 깨진다**(상태를 노출해야 함), 구조 변경이 어려워짐.

---

## 요약 — GoF 23개 전체 지도

이 장의 9개를 더하면 GoF 23개가 완성된다.

| 범주 | 본문(13개) | 이 장(9개) |
|------|-----------|-----------|
| **생성** | 싱글턴, 추상 팩토리, 팩토리 메서드 | **빌더, 프로토타입** |
| **구조** | 데코레이터, 어댑터, 퍼사드, 컴포지트, 프록시 | **브리지, 플라이웨이트** |
| **행동** | 전략, 옵저버, 커맨드, 템플릿 메서드, 반복자, 상태 | **책임 연쇄, 인터프리터, 중재자, 메멘토, 비지터** |

> **핵심 통찰**: 이 9개는 덜 자주 쓰이지만, 문제에 딱 맞으면 강력하다. 특히 TS/JS 실전에서는 **빌더(fluent API)·책임 연쇄(미들웨어)·프로토타입(구조적 복제)·메멘토(undo·상태 스냅샷)** 를 자주 만난다. 13장의 교훈대로, **문제에 맞을 때만** 꺼내 쓰자.

---

## 다른 챕터와의 관계

- **13장 실전**: 여기서 소개한 9개는 13장의 분류표(생성/구조/행동)를 완성한다.
- **9장 컴포지트/반복자**: 빌더(내부 구조 보호)·비지터(트래버서로 순회)가 컴포지트/반복자와 이어진다.
- **6장 커맨드**: 메멘토는 커맨드의 `undo`와 결합해 실행 취소를 구현한다.

---

## 보너스: 원서 복습 요소

### 📇 9개 패턴 한 줄 요약

- **브리지**: 추상화와 구현을 각각의 계층으로 분리해 둘 다 독립 변경.
- **빌더**: 복잡한 객체를 단계별로 조립(생성 과정 캡슐화).
- **책임 연쇄**: 요청을 핸들러 사슬이 차례로 처리/전달.
- **플라이웨이트**: 공유 인스턴스로 대량 객체의 메모리 절약.
- **인터프리터**: 언어 문법을 클래스로 표현해 해석.
- **중재자**: 객체 간 복잡한 통신을 중재자에 집중.
- **메멘토**: 상태를 별도 객체에 저장해 복구(undo).
- **프로토타입**: 기존 인스턴스를 복제해 새 인스턴스 생성.
- **비지터**: 구조를 바꾸지 않고 새 기능(연산)을 추가.
