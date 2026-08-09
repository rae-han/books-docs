# Item 29: 항상 유효한 상태만 표현하는 타입 선호하기 (Prefer Types That Always Represent Valid States)

## 핵심 질문

왜 어떤 코드는 아무리 머리를 짜내도 제대로 구현할 수 없는가? "무효한 상태를 허용하는 타입"은 코드를 어떻게 망가뜨리는가?

타입을 잘 설계하면 코드는 곧게 써진다. 타입을 잘못 설계하면 어떤 영리함도 문서화도 구하지 못한다 - 코드는 혼란스럽고 버그가 꼬인다. 효과적인 타입 설계의 열쇠는 **유효한 상태만 표현할 수 있는 타입을 빚는 것**이다.

이 장(Chapter 4) 전체를 여는 인용문이 방향을 잡아 준다.

> Show me your flowcharts and conceal your tables, and I shall continue to be mystified. Show me your tables, and I won't usually need your flowcharts; they'll be obvious.<br>순서도를 보여 주고 테이블을 감추면 나는 계속 어리둥절할 것이다. 테이블을 보여 달라. 그러면 순서도는 대개 필요 없을 것이다 - 자명할 테니까.<br>- 프레드 브룩스(Fred Brooks), "맨먼스 미신"

## 1. 웹 앱 상태 설계 - 무효한 상태가 만드는 혼란

페이지를 선택하면 내용을 로드해 표시하는 웹 앱의 상태를 이렇게 썼다고 하자.

```typescript
interface State {
  pageText: string;
  isLoading: boolean;
  error?: string;
}
```

렌더링 코드는 모든 필드를 고려해야 한다.

```typescript
function renderPage(state: State) {
  if (state.error) {
    return `Error! Unable to load ${currentPage}: ${state.error}`;
  } else if (state.isLoading) {
    return `Loading ${currentPage}...`;
  }
  return `<h1>${currentPage}</h1>\n${state.pageText}`;
}
```

그런데 이게 맞나? **`isLoading`과 `error`가 둘 다 설정되어 있으면?** 로딩 메시지와 에러 메시지 중 무엇을 보여야 하나? 알 수 없다 - 정보가 부족하다. `changePage`를 쓰면 문제가 더 드러난다.

```typescript
async function changePage(state: State, newPage: string) {
  state.isLoading = true;
  try {
    const response = await fetch(getUrlForPage(newPage));
    if (!response.ok) {
      throw new Error(`Unable to load ${newPage}: ${response.statusText}`);
    }
    const text = await response.text();
    state.isLoading = false;
    state.pageText = text;
  } catch (e) {
    state.error = '' + e;
  }
}
```

문제가 수두룩하다.

1. 에러 케이스에서 `state.isLoading`을 false로 되돌리는 것을 잊었다.
2. `state.error`를 비우지 않아서, 이전 요청이 실패했다면 로딩 메시지나 새 페이지 대신 그 에러 메시지가 계속 보인다.
3. 로딩 중에 사용자가 페이지를 또 바꾸면 무슨 일이 벌어질지 아무도 모른다 - 응답이 돌아오는 순서에 따라 새 페이지 다음에 에러가 보일 수도, 두 번째가 아니라 첫 페이지가 보일 수도 있다.

문제의 근원: 이 상태는 **정보가 너무 적으면서**(어느 요청이 실패했나? 어느 것이 로딩 중인가?) **동시에 너무 많다**(`isLoading`과 `error`가 동시에 설정되는 무효한 상태를 허용한다). 그래서 `renderPage`도 `changePage`도 잘 구현하는 것이 불가능하다.

더 나은 표현:

```typescript
interface RequestPending {
  state: 'pending';
}
interface RequestError {
  state: 'error';
  error: string;
}
interface RequestSuccess {
  state: 'ok';
  pageText: string;
}
type RequestState = RequestPending | RequestError | RequestSuccess;

interface State {
  currentPage: string;
  requests: {[page: string]: RequestState};
}
```

태그된 유니온으로 네트워크 요청이 있을 수 있는 상태들을 명시적으로 모델링했다. 상태 코드가 서너 배 길어졌지만 **무효한 상태를 허용하지 않는다**는 거대한 이점을 얻었다. 현재 페이지도, 발행한 모든 요청의 상태도 명시적으로 모델링된다. 그 결과 두 함수 모두 구현이 쉬워진다.

```typescript
function renderPage(state: State) {
  const {currentPage} = state;
  const requestState = state.requests[currentPage];
  switch (requestState.state) {
    case 'pending':
      return `Loading ${currentPage}...`;
    case 'error':
      return `Error! Unable to load ${currentPage}: ${requestState.error}`;
    case 'ok':
      return `<h1>${currentPage}</h1>\n${requestState.pageText}`;
  }
}

async function changePage(state: State, newPage: string) {
  state.requests[newPage] = {state: 'pending'};
  state.currentPage = newPage;
  try {
    const response = await fetch(getUrlForPage(newPage));
    if (!response.ok) {
      throw new Error(`Unable to load ${newPage}: ${response.statusText}`);
    }
    const pageText = await response.text();
    state.requests[newPage] = {state: 'ok', pageText};
  } catch (e) {
    state.requests[newPage] = {state: 'error', error: '' + e};
  }
}
```

첫 구현의 모호함이 완전히 사라졌다 - 현재 페이지가 무엇인지 분명하고, 모든 요청은 정확히 하나의 상태에 있다. 로딩 중에 페이지를 바꿔도 문제없다. 옛 요청은 완료되지만 UI에 영향을 주지 않는다.

## 2. 에어프랑스 447편 - 상태 설계가 생사를 가른 사례

더 단순하지만 훨씬 참혹한 예가 2009년 6월 1일 대서양 상공에서 사라진 에어버스 330, 에어프랑스 447편이다. 에어버스는 플라이 바이 와이어(fly-by-wire) 항공기였다 - 조종사의 조작이 컴퓨터를 거쳐 조종면에 전달된다. 2년 뒤 해저에서 블랙박스가 회수되자 추락의 여러 요인이 드러났는데, 핵심 요인 하나가 **나쁜 상태 설계**였다.

에어버스 330의 조종석에는 기장과 부기장 각각의 조종간(사이드 스틱)이 있었고, "듀얼 인풋" 모드로 **두 스틱이 독립적으로 움직였다**. 타입스크립트로 모델링하면:

```typescript
interface CockpitControls {
  /** 왼쪽 스틱의 각도(도). 0 = 중립, + = 앞으로 */
  leftSideStick: number;
  /** 오른쪽 스틱의 각도(도). 0 = 중립, + = 앞으로 */
  rightSideStick: number;
}
```

이 자료 구조로 현재 스틱 설정을 계산하는 `getStickSetting`을 짜 보라. 기장(왼쪽) 우선? 부기장이 조종 중이면? 0이 아닌 쪽을 쓰자니 둘 다 0이 아니면? 둘이 비슷하면 평균을 내자니, 다르면? 에러를 던질 수도 없다 - **날개 플랩은 어떤 각도로든 설정되어야 한다!**

447편에서 부기장은 폭풍에 진입하며 말없이 스틱을 당겼다. 고도는 올랐지만 속도를 잃고 실속(*stall - 양력을 만들기에 속도가 너무 느린 상태*)에 빠져 추락하기 시작했다. 실속 탈출 훈련대로 기장은 스틱을 앞으로 밀었다. 하지만 부기장은 여전히 말없이 당기고 있었고, 에어버스의 함수는 이랬다.

```typescript
function getStickSetting(controls: CockpitControls) {
  return (controls.leftSideStick + controls.rightSideStick) / 2;
}
```

기장이 스틱을 끝까지 밀어도 **평균은 0**이었다. 기장은 왜 기수가 내려가지 않는지 알 수 없었다. 부기장이 자신이 한 일을 밝혔을 때는 이미 회복하기에 고도가 너무 낮았고, 탑승자 228명 전원이 사망했다.

요점: **저 입력이 주어지는 한 `getStickSetting`을 잘 구현할 방법은 없다. 함수는 실패하도록 설정되어 있었다.** 대부분의 항공기에서 두 조종간은 기계적으로 연결되어 있다 - 부기장이 당기면 기장 쪽도 당겨진다. 그 상태는 표현이 단순하다.

```typescript
interface CockpitControls {
  /** 스틱의 각도(도). 0 = 중립, + = 앞으로 */
  stickAngle: number;
}
```

프레드 브룩스의 인용처럼, 이제 순서도는 자명하다 - `getStickSetting` 함수 자체가 필요 없다.

> **핵심 통찰**: 타입을 설계할 때 어떤 값을 포함하고 어떤 값을 배제하는지 숙고하라. 유효한 상태를 표현하는 값만 허용하면 코드를 쓰기 쉬워지고 타입스크립트의 검사도 쉬워진다. 이것은 매우 일반적인 원칙이며, 이 장의 여러 아이템이 그 구체적 발현이다.

## 기억해야 할 것들

- 유효한 상태와 무효한 상태를 모두 표현하는 타입은 혼란스럽고 오류를 부르는 코드로 이어지기 쉽다.
- 유효한 상태만 표현하는 타입을 선호하라. 길어지고 표현하기 어려워지더라도 결국 시간과 고통을 아껴 준다!
