# Item 37: 옵셔널 속성 사용 제한하기 (Limit the Use of Optional Properties)

## 핵심 질문

기존 코드를 깨지 않으려고 붙인 `?` 하나가 어떤 버그를 열어 주는가? 옵셔널 대신 무엇을 할 수 있는가?

타입이 진화하다 보면 새 속성을 추가하게 된다. 기존 코드나 데이터를 무효화하지 않으려고 옵셔널로 만들곤 하는데, 때로는 옳은 선택이지만 **옵셔널 속성에는 비용이 따른다.** 추가하기 전에 두 번 생각해야 한다.

## 1. 옵셔널이 감춘 버그 - 단위계 예제

레이블과 단위가 붙은 숫자를 표시하는 UI 컴포넌트가 있다("Height: 12 ft", "Speed: 10 mph").

```typescript
interface FormattedValue {
  value: number;
  units: string;
}
function formatValue(value: FormattedValue) { /* ... */ }

interface Hike {
  miles: number;
  hours: number;
}
function formatHike({miles, hours}: Hike) {
  const distanceDisplay = formatValue({value: miles, units: 'miles'});
  const paceDisplay = formatValue({value: miles / hours, units: 'mph'});
  return `${distanceDisplay} at ${paceDisplay}`;
}
```

어느 날 미터법을 지원하기로 한다. 기존 코드와 테스트의 변경을 최소화하려고 속성을 **옵셔널**로 추가한다.

```typescript
type UnitSystem = 'metric' | 'imperial';

interface FormattedValue {
  value: number;
  units: string;
  /** 기본값은 imperial */
  unitSystem?: UnitSystem;
}
interface AppConfig {
  darkMode: boolean;
  /** 기본값은 imperial */
  unitSystem?: UnitSystem;
}
```

`formatHike`를 갱신하는데…

```typescript
function formatHike({miles, hours}: Hike, config: AppConfig) {
  const { unitSystem } = config;
  const distanceDisplay = formatValue({
    value: miles, units: 'miles', unitSystem
  });
  const paceDisplay = formatValue({
    value: miles / hours, units: 'mph'  // unitSystem을 깜빡했다!
  });
  return `${distanceDisplay} at ${paceDisplay}`;
}
```

한 호출에는 `unitSystem`을 넘기고 다른 호출에는 안 넘겼다. 미터법 사용자가 임페리얼과 미터가 뒤섞인 화면을 보게 되는 버그다. 사실 이 설계는 **정확히 이런 버그의 레시피**다 - `formatValue`를 쓰는 모든 곳에서 `unitSystem`을 기억해서 넘겨야 하고, 잊을 때마다 미터법 사용자는 야드·에이커 같은 헷갈리는 단위를 본다.

`unitSystem`을 빠뜨린 모든 곳을 자동으로 찾아 주는 것이야말로 타입 체크가 잘하는 일인데, **속성을 옵셔널로 만들어서 그 도움을 스스로 차단했다.** 필수로 만들면 빠뜨린 모든 곳에서 타입 에러가 난다. 하나하나 고쳐야 하지만, 혼란에 빠진 사용자에게 듣는 것보다 타입스크립트가 찾아 주는 편이 훨씬 낫다!

## 2. "기본값" 주석의 문제와 타입 분리 해법

"기본값은 imperial"이라는 문서 주석도 걱정스럽다. 타입스크립트에서 옵셔널 속성의 기본값은 항상 `undefined`이므로, 대체 기본값을 구현하려면 코드 곳곳에 이런 줄이 흩어지게 된다.

```typescript
const unitSystem = config.unitSystem ?? 'imperial';
```

이 하나하나가 버그의 기회다. 팀의 다른 개발자가 기본값이 imperial이라는 것을 잊고(애초에 왜 imperial이 기본이지?) `?? 'metric'`이라 쓰면 또 표시가 어긋난다.

`AppConfig`의 옛 값들을 지원해야 해서(디스크나 DB에 JSON으로 저장되어 있다면) 새 필드를 필수로 만들 수 없다면, **타입을 둘로 쪼개라** - 디스크에서 읽은 비정규화 설정용 타입과, 앱에서 쓰는 옵셔널이 적은 타입.

```typescript
interface InputAppConfig {
  darkMode: boolean;
  // ... 다른 설정들 ...
  /** 기본값은 imperial */
  unitSystem?: UnitSystem;
}
interface AppConfig extends InputAppConfig {
  unitSystem: UnitSystem;  // 필수
}

function normalizeAppConfig(inputConfig: InputAppConfig): AppConfig {
  return {
    ...inputConfig,
    unitSystem: inputConfig.unitSystem ?? 'imperial',
  };
}
```

서브타입에서 옵셔널을 필수로 바꾸는 것이 이상하게 느껴진다면 Item 7을 보라(좁히기이므로 유효하다). `Required<InputAppConfig>`를 쓸 수도 있다. 이 분리가 해결하는 것:

1. 앱 전체에 복잡성을 더하지 않으면서 설정이 진화하고 하위 호환성을 유지할 수 있다.
2. 기본값 적용이 한 곳에 집중된다.
3. `AppConfig`가 기대되는 곳에 `InputAppConfig`를 쓰기 어려워진다.

이런 "공사 중" 타입은 네트워크 코드에서 자주 나온다(Item 33의 `UserPosts`도 한 예).

## 3. 조합 폭발과 불건전성

인터페이스에 옵셔널 속성을 더할수록 새로운 문제를 만난다 - 옵셔널이 N개면 조합이 **2^N**개다. 10개면 1,024가지 조합을 다 테스트했는가? 모든 조합이 말이 되기는 하는가? 옵션들에 구조가 있을 가능성이 높다 - 상호 배타적인 것들이 있다면 상태가 그것을 모델링해야 한다(Item 29). 이것은 옵셔널 속성만이 아니라 옵션 일반의 문제다.

마지막으로, 옵셔널 속성은 타입스크립트 불건전성의 발생원이기도 하다(Item 48).

## 4. 그럼에도 옵셔널을 쓸 때

- **기존 API를 기술하거나 하위 호환을 유지하며 API를 진화**시킬 때는 대체로 불가피하다.
- **거대한 설정 객체**는 모든 옵셔널 필드를 기본값으로 채우는 비용이 엄두가 안 날 수 있다.
- **진짜로 선택적인 속성**도 있다 - 모두가 middle name을 갖지는 않으므로 `Person`의 옵셔널 `middleName`은 정확한 모델이다.

단점들을 알고, 완화하는 법을 알고, 유효한 대안이 있다면 옵셔널 속성을 추가하기 전에 두 번 생각하라.

## 기억해야 할 것들

- 옵셔널 속성은 타입 체커가 버그를 찾는 것을 막을 수 있고, 기본값 채우기 코드의 반복과 불일치로 이어질 수 있다.
- 인터페이스에 옵셔널 속성을 추가하기 전에 두 번 생각하라. 필수로 만들 수 없는지 고려하라.
- 비정규화된 입력 데이터용 타입과 코드에서 쓸 정규화된 데이터용 타입을 구별해서 만드는 것을 고려하라.
- 옵션의 조합 폭발을 피하라.
