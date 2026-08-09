# Item 26: 함수형 구문과 라이브러리로 타입 흐름 돕기 (Use Functional Constructs and Libraries to Help Types Flow)

## 핵심 질문

같은 로직인데 왜 손으로 만든 루프는 타입 구문이 필요하고 `map`·`flat`·Lodash 체인은 필요 없는가?

자바스크립트에는 파이썬·C·자바 같은 표준 라이브러리가 없었고, 그 공백을 jQuery → Underscore → Lodash → Ramda로 이어지는 라이브러리들이 채워 왔다. 그중 `map`·`flatMap`·`filter`·`reduce` 같은 기능은 언어 자체에 들어왔다. 이런 구문들은 자바스크립트에서도 손수 만든 루프보다 나은 경우가 많지만, **타입스크립트를 얹으면 저울이 훨씬 더 기운다** — 타입 선언이 있어서 **타입이 구문을 타고 흐르기** 때문이다. 손수 만든 루프에서는 타입을 직접 책임져야 한다.

## 1. CSV 파싱 — 세 가지 스타일

명령형:

```typescript
const rawRows = csvData.split('\n');
const headers = rawRows[0].split(',');

const rowsImperative = rawRows.slice(1).map(rowStr => {
  const row = {};
  rowStr.split(',').forEach((val, j) => {
    row[headers[j]] = val;
    // ~~~~~~~~~~~~ No index signature with a parameter of
    //              type 'string' was found on type '{}'
  });
  return row;
});
```

함수형(reduce):

```typescript
const rowsFunctional = rawRows.slice(1)
  .map(rowStr => rowStr.split(',')
    .reduce((row, val, i) => ((row[headers[i]] = val), row), {}));
    //       ~~~~~~~~~~~~~~~ No index signature with a parameter of
    //                       type 'string' was found on type '{}'
```

두 순수 자바스크립트 버전 모두 타입스크립트에서 같은 에러가 난다. 해법은 `{}`에 타입 구문(`{[column: string]: string}` 또는 `Record<string, string>`)을 붙이는 것이다. 반면 키 배열과 값 배열을 "지퍼처럼" 묶어 객체를 만드는 Lodash의 `zipObject` 버전은 **수정 없이 통과**한다.

```typescript
import _ from 'lodash';
const rowsLodash = rawRows.slice(1)
  .map(rowStr => _.zipObject(headers, rowStr.split(',')));
//    ^? const rowsLodash: _.Dictionary<string>[]
```

`Dictionary<string>`은 `{[key: string]: string}`(=`Record<string, string>`)과 같은 Lodash 타입 별칭이다. 중요한 것은 **타입 구문 없이 `rows`의 타입이 정확히 맞는다**는 점이다. 자바스크립트만 쓸 때는 "서드파티 의존성을 추가하고 동료들이 배워야 할 가치가 있나?"를 고민하게 되지만, 타입스크립트는 그 균형을 Lodash 쪽으로 기울인다.

## 2. 데이터 가공이 복잡해질수록 격차가 커진다

NBA 각 팀의 선수 명단이 있다고 하자.

```typescript
interface BasketballPlayer {
  name: string;
  team: string;
  salary: number;
}
declare const rosters: {[team: string]: BasketballPlayer[]};
```

루프와 `concat`으로 평평한 리스트를 만들면 실행은 되지만 타입 체크는 안 된다.

```typescript
let allPlayers = [];
//  ~~~~~~~~~~ Variable 'allPlayers' implicitly has type 'any[]'
//             in some locations where its type cannot be determined
for (const players of Object.values(rosters)) {
  allPlayers = allPlayers.concat(players);
  //           ~~~~~~~~~~ Variable 'allPlayers' implicitly has an 'any[]' type
}
```

(`concat`은 Item 25의 진화하는 타입을 발동시키지 않는다.) 고치려면 `allPlayers: BasketballPlayer[]` 구문이 필요하다. 하지만 더 나은 해법은 `Array.prototype.flat`이다.

```typescript
const allPlayers = Object.values(rosters).flat();  // OK
//    ^? const allPlayers: BasketballPlayer[]
```

`flat`은 다차원 배열을 평평하게 만든다(시그니처는 대략 `T[][] => T[]`). 가장 간결하고 타입 구문이 필요 없으며, 덤으로 `let` 대신 `const`를 써서 이후 변경도 막을 수 있다.

이제 팀별 최고 연봉 선수를 연봉순으로 뽑아 보자. Lodash 없는 해법은 함수형 구문을 쓰지 않은 곳마다 타입 구문이 필요하다.

```typescript
const teamToPlayers: {[team: string]: BasketballPlayer[]} = {};
for (const player of allPlayers) {
  const {team} = player;
  teamToPlayers[team] = teamToPlayers[team] || [];
  teamToPlayers[team].push(player);
}
for (const players of Object.values(teamToPlayers)) {
  players.sort((a, b) => b.salary - a.salary);
}
const bestPaid = Object.values(teamToPlayers).map(players => players[0]);
bestPaid.sort((playerA, playerB) => playerB.salary - playerA.salary);
```

Lodash 등가물:

```typescript
const bestPaid = _(allPlayers)
  .groupBy(player => player.team)
  .mapValues(players => _.maxBy(players, p => p.salary)!)
  .values()
  .sortBy(p => -p.salary)
  .value();
console.log(bestPaid.slice(0, 10));
//          ^? const bestPaid: BasketballPlayer[]
```

길이가 절반이면서 필요한 것은 널 아님 단언 하나뿐이다(`_.maxBy`에 넘어가는 players 배열이 비어 있지 않다는 것을 타입 체커가 모르므로). Lodash·Underscore의 체인(chain) 개념 덕에 연산 순서가 자연스럽다 — `_.c(_.b(_.a(v)))` 대신 `_(v).a().b().c().value()`로 쓴다. `_(v)`가 값을 "감싸고" `.value()`가 "푼다". 체인의 각 함수 호출에서 감싸인 값의 타입을 확인할 수 있고, 언제나 정확하다.

> **핵심 통찰**: 내장 함수형 구문과 Lodash류 라이브러리에서 타입이 잘 흐르는 것은 우연이 아니다. **변경을 피하고 호출마다 새 값을 반환하기 때문에 새 타입도 만들 수 있는 것**이다(Item 19). 타입스크립트의 발전 상당 부분이 야생의 자바스크립트 라이브러리 동작을 정확히 모델링하려는 노력으로 추동됐다 — 그 성과를 활용하라.

## 기억해야 할 것들

- 타입 흐름을 개선하고 가독성을 높이고 명시적 타입 구문의 필요를 줄이려면, 손수 만든 구문 대신 내장 함수형 구문과 Lodash 같은 유틸리티 라이브러리를 사용하라.
