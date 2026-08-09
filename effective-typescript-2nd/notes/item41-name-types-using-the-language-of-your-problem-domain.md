# Item 41: 문제 도메인의 언어로 타입 이름 짓기 (Name Types Using the Language of Your Problem Domain)

## 핵심 질문

이름을 잘 지은 타입과 못 지은 타입은 무엇이 다른가? 도메인 어휘를 재사용하면 무엇을 얻는가?

> There are only two hard problems in Computer Science: cache invalidation and naming things.<br>컴퓨터 과학에는 어려운 문제가 딱 둘 있다: 캐시 무효화, 그리고 이름 짓기.<br>— 필 칼튼(Phil Karlton)

이 책은 타입의 형태와 도메인의 값 집합에 대해 많이 말했지만, **타입에 붙이는 이름**도 타입 설계의 중요한 부분이다. 잘 고른 타입·속성·변수 이름은 의도를 명확히 하고 코드와 타입의 추상화 수준을 끌어올린다. 잘못 고른 이름은 코드를 흐리고 잘못된 멘털 모델로 이끈다.

## 1. 모호한 이름 vs 도메인 어휘

동물 데이터베이스를 만든다고 하자.

```typescript
interface Animal {
  name: string;
  endangered: boolean;
  habitat: string;
}

const leopard: Animal = {
  name: 'Snow Leopard',
  endangered: false,
  habitat: 'tundra',
};
```

문제가 여럿이다.

1. `name`은 매우 일반적인 용어다. 어떤 이름인가? 학명? 통칭?
2. boolean인 `endangered`도 모호하다. 멸종된 동물은? 의도가 "위기 이상"인가, 문자 그대로 위기(endangered)인가?
3. `habitat`은 지나치게 넓은 string 타입(Item 35)이기도 하지만, "서식지"가 무엇을 뜻하는지도 불분명하다.
4. 변수 이름은 `leopard`인데 `name` 속성의 값은 "Snow Leopard"다. 이 구별에 의미가 있는가?

모호함을 줄인 버전:

```typescript
interface Animal {
  commonName: string;
  genus: string;
  species: string;
  status: ConservationStatus;
  climates: KoppenClimate[];
}
type ConservationStatus = 'EX' | 'EW' | 'CR' | 'EN' | 'VU' | 'NT' | 'LC';
type KoppenClimate = |
  'Af' | 'Am' | 'As' | 'Aw' |
  'BSh' | 'BSk' | 'BWh' | 'BWk' |
  'Cfa' | 'Cfb' | 'Cfc' | 'Csa' | 'Csb' | 'Csc' | 'Cwa' | 'Cwb' | 'Cwc' |
  'Dfa' | 'Dfb' | 'Dfc' | 'Dfd' |
  'Dsa' | 'Dsb' | 'Dsc' | 'Dwa' | 'Dwb' | 'Dwc' | 'Dwd' |
  'EF' | 'ET';

const snowLeopard: Animal = {
  commonName: 'Snow Leopard',
  genus: 'Panthera',
  species: 'Uncia',
  status: 'VU',                    // 취약(vulnerable)
  climates: ['ET', 'EF', 'Dfd'],   // 고산대·아고산대
};
```

개선된 점:

- `name`이 더 구체적인 용어로 대체됐다: `commonName`, `genus`, `species`
- `endangered`가 `status`가 됐다 — IUCN의 표준 분류 체계를 쓰는 `ConservationStatus` 타입
- `habitat`이 `climates`가 됐다 — 또 하나의 표준 분류인 쾨펜 기후 구분을 쓴다

첫 버전에서 필드의 의미를 더 알아야 했다면 그것을 쓴 사람을 찾아가 물어야 한다. 십중팔구 퇴사했거나 기억 못 한다. 최악은 이 형편없는 타입을 누가 썼는지 `git blame`을 돌렸더니 **나였던** 경우다! 두 번째 버전이라면 쾨펜 기후 구분이나 보전 상태의 정확한 의미를 알아보는 데 도움이 될 온라인 자료가 무수히 많다.

> **핵심 통찰**: 모든 도메인에는 그 대상을 기술하는 전문 어휘가 있다. 내 용어를 발명하기보다 문제 도메인의 용어를 재사용하라. 수년, 수십 년, 수 세기에 걸쳐 다듬어진 그 어휘는 현장 사람들에게 잘 이해된다. 단, 도메인 어휘는 **정확하게** 써야 한다 — 도메인 언어를 다른 뜻으로 전용하는 것은 자기 용어를 발명하는 것보다 더 혼란스럽다.

같은 고려가 함수 매개변수 이름, 튜플 레이블, 인덱스 타입 레이블 같은 다른 레이블에도 적용된다.

## 2. 이름 짓기의 세 가지 규칙

1. **구별에 의미를 담아라**: 글과 말에서는 같은 단어의 반복이 지루해서 동의어를 쓰지만, 코드에서는 정반대 효과가 난다. 두 용어를 썼다면 의미 있는 구별을 하고 있는지 확인하라. 아니라면 같은 용어를 써야 한다.
2. **모호하고 무의미한 이름을 피하라**: "data", "info", "thing", "item", "object", 그리고 만년 인기인 "entity". 도메인에서 Entity가 특정한 의미를 갖는다면 좋다. 하지만 더 의미 있는 이름을 생각하기 싫어서 쓰는 것이라면 결국 곤경에 처한다 — 프로젝트에 "Entity"라는 서로 다른 타입이 여러 개 생기고, 무엇이 Item이고 무엇이 Entity인지 기억할 수 있겠는가?
3. **무엇을 담는지, 어떻게 계산되는지가 아니라 그것이 무엇인지로 이름 지어라**: `INodeList`보다 `Directory`가 의미 있다. 디렉터리를 구현이 아니라 개념으로 생각할 수 있게 해 준다. 좋은 이름은 추상화 수준을 높이고 우발적 충돌의 위험을 줄인다.

## 기억해야 할 것들

- 가능하면 문제 도메인의 이름을 재사용해서 코드의 가독성과 추상화 수준을 높여라. 도메인 용어는 정확하게 사용하라.
- 같은 것에 다른 이름을 쓰지 마라: 이름의 구별에 의미를 담아라.
- "Info"·"Entity" 같은 모호한 이름을 피하라. 타입의 형태가 아니라 그것이 무엇인지로 이름 지어라.
