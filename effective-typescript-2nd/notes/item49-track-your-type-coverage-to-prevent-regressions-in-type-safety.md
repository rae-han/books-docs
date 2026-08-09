# Item 49: 타입 커버리지를 추적해 타입 안전성의 퇴행 방지하기 (Track Your Type Coverage to Prevent Regressions in Type Safety)

## 핵심 질문

`noImplicitAny`를 켜고 모든 암시적 any에 구문을 달았다면 any의 문제에서 안전한가?

답은 "아니오"다. any 타입은 여전히 두 가지 주요 경로로 프로그램에 들어온다.

1. **명시적 any 타입**: Item 43·44의 조언대로 any를 좁고 구체적으로 만들었어도 any는 any다. 특히 `any[]`나 `{[key: string]: any}` 같은 타입은 인덱싱하는 순간 그냥 any가 되고, 그 any가 코드로 흘러 다닌다.
2. **서드파티 타입 선언**: 특히 음험하다. `@types` 선언 파일에서 오는 any는 **소리 없이** 들어온다 - noImplicitAny를 켰고 "any"라는 단어를 한 번도 쓰지 않았는데도 any가 코드에 흐른다.

any가 타입 안전성과 개발 경험에 미치는 악영향(Item 5)을 생각하면, **코드베이스의 any 개수를 추적하는 것**이 좋다. npm의 type-coverage 패키지가 한 방법이다.

```
$ npx type-coverage
9985 / 10117 98.69%
```

이 프로젝트의 심벌 10,117개 중 9,985개(98.69%)가 any(또는 any의 별칭)가 아닌 타입을 가졌다는 뜻이다. 변경이 무심코 any를 도입해서 코드에 퍼지면 이 퍼센트가 떨어지는 것으로 나타난다. 이 퍼센트는 어떤 의미에서 이 장의 다른 아이템들을 얼마나 잘 따랐는지의 점수이기도 하다 - 좁은 스코프의 any도, `any[]` 같은 구체적 형태도 any 타입 심벌의 수를 줄인다. 수치로 추적하면 시간이 갈수록 좋아지기만 하는지 확인할 수 있다.

## 1. --detail로 any의 출처 조사하기

한 번 수집하는 것만으로도 유익하다. `--detail` 플래그는 코드의 모든 any 위치를 찍어 준다.

```
$ npx type-coverage --detail
path/to/code.ts:1:10 getColumnInfo
path/to/module.ts:7:1 pt2
...
```

생각지 못한 any의 출처가 드러나기 십상이라 조사할 가치가 있다. 몇 가지 사례:

**철 지난 명시적 any** - 예전에 편의로 내린 결정의 흔적. 표 데이터 앱에서 컬럼 설명을 만드는 함수가 있었다고 하자.

```typescript
function getColumnInfo(name: string): any {
  return utils.buildColumnInfo(appState.dataSchema, name);  // any를 반환했었음
}
```

`utils.buildColumnInfo`가 any를 반환하던 시절에 주석과 함께 `: any` 구문을 달아 뒀다. 하지만 그 사이 `ColumnInfo` 타입이 생겼고 이제 any를 반환하지 않는다. **이제 any 구문은 귀중한 타입 정보를 내다 버리고 있다. 없애라!**

**모듈 통째 any** - 서드파티 any의 가장 극단적 형태.

```typescript
declare module 'my-module';
```

이제 `my-module`에서 무엇이든 에러 없이 import할 수 있다. 그 심벌들은 전부 any이고, 값을 통과시키면 더 많은 any를 낳는다.

```typescript
import {someMethod, someSymbol} from 'my-module';  // OK
const pt1 = { x: 1, y: 2 };
//    ^? const pt1: { x: number; y: number; }
const pt2 = someMethod(pt1, someSymbol);  // OK
//    ^? const pt2: any
```

사용하는 모습이 잘 타이핑된 모듈과 똑같아서 모듈을 스텁 처리했다는 사실을 잊기 쉽다. 동료가 해 놨다면 애초에 몰랐을 수도 있다. 때때로 재방문할 가치가 있다 - 공식 타입 선언이 생겼을 수도 있고, Chapter 8을 읽고 나면 직접 타입을 써서 커뮤니티에 기여할 수도 있다.

**타입 버그 우회용 단언** - 서드파티 선언의 버그(예: Item 30을 안 따르고 실제보다 넓은 유니온을 반환한다고 선언) 때문에 any 단언으로 우회했는데, 그 사이 선언이 고쳐졌을 수 있다. 아니면 이제 직접 고칠 때가 됐거나!

## 2. 지속적 추적

코드의 any를 상시 인지하고 싶다면 type-coverage를 **타입스크립트 언어 서비스 플러그인**으로 설정할 수 있다 - 코드에 숨어 있는 모든 any를 편집기에서 강조해 주는 엑스레이 투시 같은 것이다. **CI에 추가**하면 타입 안전성이 갑자기 떨어지는 순간 바로 알게 된다.

> **핵심 통찰**: any를 쓰게 만들었던 사정은 더 이상 유효하지 않을 수 있다. 이제는 끼워 넣을 타입이 생겼을 수도, 안전하지 않은 단언이 불필요해졌을 수도, 우회하던 선언 버그가 고쳐졌을 수도 있다. 타입 커버리지 추적은 이 선택들을 드러내고 계속 재검토하게 만든다.

## 기억해야 할 것들

- noImplicitAny를 켜도 명시적 any나 서드파티 타입 선언(@types)을 통해 any 타입이 코드에 들어올 수 있다.
- type-coverage 같은 도구로 프로그램이 얼마나 잘 타이핑됐는지 추적하는 것을 고려하라. any 사용 결정을 재검토하게 하고 시간이 갈수록 타입 안전성을 높여 준다.
