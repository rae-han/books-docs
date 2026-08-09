# Item 83: noImplicitAny를 켜기 전에는 마이그레이션이 끝난 것이 아니다 (Don't Consider Migration Complete Until You Enable noImplicitAny)

## 핵심 질문

전체 프로젝트를 .ts로 바꿨는데 왜 아직 끝이 아닌가? noImplicitAny 없는 타입스크립트는 무엇을 감추는가?

프로젝트 전체를 .ts로 변환한 것은 큰 성취다. 하지만 아직 일이 끝나지 않았다. 다음 목표는 **`noImplicitAny`를 켜는 것**이다. noImplicitAny 없는 타입스크립트 코드는 **과도기**로 봐야 한다 — 타입 선언에 저지른 진짜 실수를 가릴 수 있기 때문이다.

## 1. 느슨함이 감추는 실수

Item 82의 "누락 멤버 추가" 빠른 수정으로 클래스에 속성 선언을 추가했고, 남은 any를 고치려 한다고 하자.

```typescript
class Chart {
  indices: any;
  // ...
}
```

indices는 숫자 배열일 것 같아서 타입을 끼운다.

```typescript
class Chart {
  indices: number[];
  // ...
}
```

새 에러가 없으니 넘어간다. 불행히도 실수했다 — `number[]`는 틀린 타입이다. 클래스의 다른 곳에 이런 코드가 있다.

```typescript
getRanges() {
  for (const r of this.indices) {
    const low = r[0];
    //    ^? const low: any
    const high = r[1];
    //    ^? const high: any
    // ...
  }
}
```

분명 `number[][]`나 `[number, number][]`가 더 정확한 타입이다. **number에 인덱싱하는 것이 허용된다는 게 놀라운가?** noImplicitAny 없는 타입스크립트가 얼마나 느슨할 수 있는지의 지표로 받아들여라. noImplicitAny를 켜면 에러가 된다.

```typescript
getRanges() {
  for (const r of this.indices) {
    const low = r[0];
    //          ~~~~ Element implicitly has an 'any' type because
    //               type 'Number' has no index signature
    const high = r[1];
    //           ~~~~ Element implicitly has an 'any' type because
    //                type 'Number' has no index signature
    // ...
  }
}
```

## 2. 켜는 전략

- **로컬에서 먼저 켜고 에러를 고치기 시작하라.** 타입 체커가 내는 에러 수가 진행도의 좋은 지표다. 타입 커버리지 추적(Item 49)도 이 단계의 진행 감각을 준다.
- **변경마다 테스트를 돌리고 자주 커밋하라** — 실수를 나중에야 발견할 수 있으니까.
- noImplicitAny 에러도 Item 82처럼 "그래프를 따라 위로" 고치는 것이 도움이 될 수 있다.
- **에러가 0이 될 때까지 tsconfig.json 변경은 커밋하지 않고** 타입 수정만 커밋할 수 있다.
- 코드베이스의 일부에 타입 안전성의 우선순위를 둘 수도 있다 — 유닛 테스트보다 프로덕션 코드의 noImplicitAny 에러 먼저. 프로젝트 레퍼런스(Item 78)를 쓴다면 부분별로 다른 엄격도의 tsconfig.json을 둘 수도 있다.

## 3. 그다음은 — strict를 향해, 그러나 서두르지 말고

타입 체크의 엄격도를 올리는 손잡이는 많고 정점은 `"strict": true`다. 하지만 **noImplicitAny가 가장 중요하며**, strictNullChecks 같은 다른 설정을 채택하지 않아도 타입스크립트의 이점 대부분을 얻는다. 더 엄격한 설정을 채택하기 전에 팀 모두가 타입스크립트에 익숙해질 시간을 줘라.

> **핵심 통찰**: 마이그레이션의 완료 조건은 ".ts 확장자"가 아니라 "noImplicitAny 활성화"다. 느슨한 타입 체크는 타입 선언의 진짜 실수를 가린다.

## 기억해야 할 것들

- noImplicitAny를 채택하기 전에는 타입스크립트 마이그레이션이 끝났다고 여기지 마라. 느슨한 타입 체크는 타입 선언의 진짜 실수를 가릴 수 있다.
- noImplicitAny를 강제하기 전에 타입 에러를 점진적으로 고쳐라. 더 엄격한 검사를 채택하기 전에 팀이 타입스크립트에 익숙해질 기회를 줘라.
