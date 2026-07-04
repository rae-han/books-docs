# Chapter 6: Multi-Paradigm Programming (멀티패러다임 프로그래밍)

## 핵심 질문

현대 프로그래밍 언어는 함수형, 객체지향, 명령형 패러다임을 모두 지원하는 멀티패러다임 언어가 되었다. 이 다양한 패러다임을 상황에 따라 전략적으로 조합하면 복잡한 문제를 어떻게 더 우아하고 직관적으로 해결할 수 있을까? 구조의 문제는 객체지향으로, 로직의 문제는 함수형으로, 흐름 제어는 명령형으로 해결하는 접근법은 실무에서 어떻게 적용될 수 있을까?

---

현대 프로그래밍 언어는 대부분 멀티패러다임 언어가 되었다. 이제 함수형, 객체지향, 명령형과 같이 다양한 패러다임을 상황에 따라 선택하고 결합하는 멀티패러다임적 접근이 가능하다. 문제 유형은 다양하므로 개발자는 특정 패러다임에 얽매일 필요가 없다. 이러한 자유로운 접근법은 단순히 코드 스타일을 다양화하는 데 그치지 않고, 복잡한 데이터 구조와 다양한 실무 상황을 더 높은 가독성, 유지보수성, 확장성을 갖춘 코드로 해결하는 실용적인 전략을 제시한다.

멀티패러다임적 관점은 그저 '다양한 기능이 제공된다'는 수준을 넘어 우리가 문제를 바라보는 방식 자체를 바꾼다. 함수형 패러다임은 고차 함수와 리스트 프로세싱으로 데이터 변환을 우아하게 처리하고, 객체지향 패러다임은 복잡한 계층 구조나 상태를 명확하게 표현하는 데 도움을 준다. 명령형 패러다임은 흐름 제어와 직관성을 제공하여 이해를 돕는다. 이처럼 각 패러다임의 강점을 상황에 맞춰 적절히 활용하면 문제 해결 과정이 한층 유연해지며 코드 구조 역시 목적에 맞게 자연스럽게 정돈된다.

이 장에서는 언어가 제공하는 다양한 기능을 전략적으로 조합하여 복잡한 동시성 제어와 중첩된 템플릿 처리 등 까다로운 문제를 우아하고 직관적인 코드로 해결하는 방법을 알아본다.

---

## 1. HTML 템플릿 엔진 만들기

### 1.1 Tagged Templates

Tagged Templates는 템플릿 리터럴을 보다 유연하게 활용할 수 있게 하는 강력한 도구다. 일반 템플릿 리터럴과는 달리 Tagged Templates는 사용자 정의 함수를 통해 템플릿 문자열과 삽입된 값을 처리할 수 있다. 이를 통해 문자열을 조작하거나 특수한 출력을 생성하는 등의 다양한 작업을 수행할 수 있다.

```typescript
// [코드 6-1] Tagged Templates 사용법
function upper(strs: TemplateStringsArray, ...vals: string[]) {
  console.log(strs); // ["a: ", ", b: ", "."]  // ①
  console.log(vals); // ["a", "b"]             // ②
  return strs[0]
    + vals[0].toUpperCase()
    + strs[1]
    + vals[1].toUpperCase()
    + strs[2];
}

const a = 'a';
const b = 'b';
const result = upper`a: ${a}, b: ${b}.`;
console.log(result); // a: A, b: B.
```

먼저 `upper` 함수를 `` upper`a: ${a}, b: ${b}.` ``와 같이 평가하면 `upper` 함수가 실행되며 템플릿 리터럴에서 문자열과 동적으로 삽입된 값을 분리하여 문자열 배열(`strs`)과 값 배열(`vals`)을 인자로 전달한다. ① 템플릿 리터럴은 고정 문자열과 동적 값의 경계를 기준으로 분리되며, ② `vals`에는 `${}`로 삽입된 값들이 포함되고 각 값의 앞뒤 문자열이 `strs`에 포함된다.

`strs`의 크기는 항상 `vals`의 크기보다 하나 더 크다. 템플릿 리터럴을 `` `a: ${a}, b: ${b}` ``로 변경하여 마지막 `.`을 제거해도 `strs`는 `["a: ", ", b: ", ""]`가 된다. 템플릿 리터럴은 반드시 마지막 고정 문자열(비어 있을 수도 있음)을 포함하므로 `strs.length`는 항상 `vals.length + 1`이다. 또한 템플릿 리터럴을 `` `${a}${b}` ``와 같이 변경하더라도 `strs`는 `["", "", ""]`, `vals`는 `["a", "b"]`가 되어 여전히 `strs`가 `vals`보다 하나 큰 상태를 유지한다.

`strs`와 `vals`로부터 각각 동일한 인덱스를 기반으로 앞에서부터 순서대로 하나씩 가져와 문자열을 조합한다. 이 과정에서 `vals`의 값을 가로채어 대문자로 변형한 후 최종 결과 문자열에 포함한다.

Tagged Templates 기법을 활용하면 템플릿 리터럴을 분리하여 문자열을 유연하게 처리할 수 있다. 이 기법은 문자열 조작과 다국어 지원, 보안 검사(예: SQL 인젝션 방지, XSS 방지를 위한 이스케이프 처리)와 같은 다양한 작업에 활용할 수 있다.

### 1.2 리스트 프로세싱으로 구현하기

이번에는 Tagged Templates를 활용하여 HTML 템플릿 엔진을 만들어 보겠다. [코드 6-2]에서는 템플릿 리터럴에서 전달된 `strs`(고정 문자열 배열)와 `vals`(삽입된 값 배열)의 길이를 맞춘 후 `zip` 함수로 두 배열을 결합해 튜플을 반환하는 이터레이터를 생성한다.

```typescript
// [코드 6-2] html 함수
import { pipe, zip, toArray } from "@fxts/core";

function html(strs: TemplateStringsArray, ...vals: string[]) {
  vals.push(''); // strs의 길이에 맞추기 위해 빈 문자열을 추가
  return pipe(
    zip(strs, vals), // strs와 vals를 순서대로 결합하여 튜플 이터레이터를 생성
    toArray           // 튜플 이터레이터를 평가하여 배열로 반환
  );
}

const a = 'A',
  b = 'B',
  c = 'C';

const result = html`<b>${a}</b><i>${b}</i><em>${c}</em>`;
console.log(result);
// [["<b>", "A"], ["</b><i>", "B"], ["</i><em>", "C"], ["</em>", ""]]
```

이번에는 결합-누적 `zip`-`reduce` 패턴에 `flat`을 추가하여 튜플을 반환하는 이터레이터를 평탄화한 뒤 `reduce`를 사용해 하나의 문자열로 누적하는 방식을 구현해 보겠다.

```typescript
// [코드 6-3] zip-flat-reduce로 구현
import { pipe, zip, flat, reduce } from "@fxts/core";

function html(strs: TemplateStringsArray, ...vals: string[]) {
  vals.push(''); // strs의 길이에 맞추기 위해 빈 문자열을 추가
  return pipe(
    vals,        // ① 커링을 활용해 zip(strs)(vals)로 실행되도록 변경
    zip(strs),   // strs와 vals를 순서대로 결합하여 튜플 이터레이터를 생성
    flat,        // ②
    reduce((a, b) => a + b), // ③
  );
}

const a = 'A',
  b = 'B',
  c = 'C';

const result = html`<b>${a}</b><i>${b}</i><em>${c}</em>`;
console.log(result);
// <b>A</b><i>B</i><em>C</em>  ④
```

- ① `zip`을 사용하여 `strs`와 `vals`를 결합하여 `[str, val]` 형태의 튜플 이터레이터를 생성한다. 커링을 지원하는 `zip`을 이용해 `pipe(vals, zip(strs))`로 변경했으며 이는 `zip(strs, vals)`와 같다.
- ② `flat`을 사용하여 튜플 이터레이터를 단일 값 이터레이터로 변환한다. `[[str1, val1], [str2, val2]]` 형태의 구조가 `[str1, val1, str2, val2]`로 평탄화된다.
- ③ `reduce`를 사용하여 평탄화된 이터레이터의 모든 값을 누적하여 하나의 문자열로 만든다.
- ④ 최종 결과로 HTML 문자열(`<b>A</b><i>B</i><em>C</em>`)이 출력된다.

### 1.3 push를 concat으로

[코드 6-3]에서는 `vals`의 길이를 맞추기 위해 `push`를 사용했다. 하지만 3.4절에서 살펴보았듯이 이 문제는 `concat`을 활용해 해결할 수도 있다.

`push`는 기존 배열을 변경하지만 `concat`은 기존 배열을 변경하지 않고 지연 평가되는 이터레이터를 반환하므로 부수 효과 없이 동일한 결과를 얻을 수 있다. 또한 필요한 시점에 값을 꺼내면서 추가된 하나의 값에 대해서만 한 번 더 순회하기 때문에 시간 복잡도 면에서도 `push`와 사실상 차이가 없다. 전체 배열을 새로 만들거나 모든 값을 재할당하지 않으므로 메모리 사용 측면에서도 별다른 추가 부하가 없다.

```typescript
// [코드 6-4] concat과 화살표 함수를 통한 간결화
import { pipe, zip, flat, reduce, concat } from "@fxts/core";

// 하나의 표현식으로 구성된 html 함수 (화살표 함수)
const html = (strs: TemplateStringsArray, ...vals: string[]) =>
  pipe(
    concat(vals, ['']), // push 대신 concat으로 길이 맞추기
    zip(strs),
    flat,
    reduce((a, b) => a + b)
  );

const a = 'A',
  b = 'B',
  c = 'C';

const result = html`<b>${a}</b><i>${b}</i><em>${c}</em>`;
console.log(result);
// <b>A</b><i>B</i><em>C</em>
```

[코드 6-4]와 같이 `concat`을 통해 `vals`와 `['']`를 지연적으로 연결하면 `push` 없이도 `strs.length`에 맞춰 길이를 조정할 수 있다. 물론 이 상황에서는 `vals`가 매번 새로 만들어지는 배열이므로 `push('')`를 사용하더라도 외부 상태를 변경하는 부수 효과로 볼 필요는 없다. 그러나 코드가 복잡해지고 문장이 많아질수록 `concat` 같은 아이디어를 활용하면 유용하다.

이번 변경에서 주목해야 할 이점은 부수 효과의 감소보다는 표현식만으로 코드를 조합할 수 있게 되었다는 점이다. `html` 함수를 화살표 함수로 간결하게 작성할 수 있으며 결과적으로 코드가 점차 함수형 스타일을 띠게 된다. 이러한 변화는 추후 코드의 재사용성과 확장성을 높이는 데도 도움이 된다.

표현식만으로 코드를 구성하면 이후 문장에 의한 값 변형이나 참조 가능성이 사라진다. 그 결과로 예측 가능성과 안정성이 향상되고, 특정 표현식의 결과를 고립해 테스트하고 검증하기 쉬워진다. 이러한 제약 조건은 더욱 신뢰할 수 있는 코드를 만드는 데 기여한다.

[코드 6-4a]는 `concat` 대신 `append` 함수를 사용하여 `html` 함수를 구현한 예다.

```typescript
// [코드 6-4a] concat을 비슷한 함수인 append로 변경
import { pipe, zip, flat, reduce, append } from "@fxts/core";

const html = (strs: TemplateStringsArray, ...vals: string[]) =>
  pipe(
    vals,
    append(''),  // vals 뒤에 ''을 append한 새로운 이터레이터를 만듦
    zip(strs),   // zip(strs, appendedVals)와 동일
    flat,
    reduce((a, b) => a + b)
  );
```

`append` 함수는 `concat`과 유사한 기능을 하며 마찬가지로 지연 평가를 지원하므로 필요한 시점에만 요소를 생성한다. 또한 `append`라는 직관적인 함수명과 커링을 활용하면 코드가 더 선언적이고 직관적인 형태로 표현되어 함수형 프로그래밍의 특성과 장점을 더욱 살릴 수 있다.

### 1.4 XSS 공격 방지

XSS(*Cross-Site Scripting - 웹 페이지에 악성 스크립트를 삽입하여 해당 페이지를 보는 다른 사용자에게 피해를 주는 공격 기법*)는 웹 페이지에 악성 스크립트를 삽입하여 해당 페이지를 보는 다른 사용자에게 피해를 주는 공격 기법이다. 예를 들어 사용자 입력을 그대로 HTML에 삽입하면 `<script>` 태그 등을 통해 공격자가 임의의 자바스크립트 코드를 실행할 수 있다. 이를 방지하려면 입력된 값 중 HTML 문법으로 해석될 수 있는 문자를 안전한 형태로 변환(escape)하는 작업이 필요하다. 이렇게 변환된 HTML은 브라우저가 단순한 문자 데이터로 처리하므로 스크립트 코드가 동작할 수 없어 XSS 공격을 예방할 수 있다.

다음은 `escapeHtml.ts` 파일의 예제 코드다. 이 코드는 HTML에서 특별한 의미를 갖는 문자들(`&`, `<`, `>`, `"`, `'`, `` ` ``)을 대응되는 HTML 엔티티(`&amp;`, `&lt;`, `&gt;`, `&quot;`, `&#x27;`, `&#x60;`)로 치환하는 `escapeHtml` 함수를 제공한다. 이를 통해 사용자 입력을 안전하게 HTML에 포함할 수 있다.

```typescript
// [코드 6-5] escapeHtml.ts
const escapeMap: Record<string, string> = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#x27;',
  '`': '&#x60;',
};

const source = '(?:' + Object.keys(escapeMap).join('|') + ')';
const testRegexp = RegExp(source);
const replaceRegexp = RegExp(source, 'g');

function escapeHtml(val: unknown): string {
  const string = `${val}`;
  return testRegexp.test(string)
    ? string.replace(replaceRegexp, (match) => escapeMap[match])
    : string;
}

export { escapeHtml };
```

[코드 6-5]에서는 `escapeMap`을 이용해 특별한 의미의 문자를 대응되는 HTML 엔티티로 치환하는 정규식을 생성한다. 이후 입력 문자열을 검사하여 필요한 경우에만 변환을 수행한다. 반환된 문자열은 HTML 구조에 삽입하더라도 안전하게 렌더링되며 잠재적인 XSS 공격을 예방할 수 있다.

다음은 `escapeHtml` 함수를 테스트하는 예다.

```typescript
// [코드 6-6] escapeHtml 테스트
import { escapeHtml } from './escapeHtml';

console.log(escapeHtml('<script>alert("XSS")</script>'));
// &lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;

console.log(escapeHtml('Hello & Welcome! "Have" a nice day <3'));
// Hello &amp; Welcome! &quot;Have&quot; a nice day &lt;3
```

출력 결과를 보면 꺾쇠 괄호인 `<`나 `>`와 같은 문자들이 엔티티로 변환되어 브라우저에서 스크립트로 해석되지 않음을 확인할 수 있다.

이제 `html` 함수가 생성하는 문자열에 포함될 `vals`를 `escapeHtml`로 변환하여 XSS 공격을 예방할 수 있다. 이는 `map` 함수를 사용하여 `vals`의 각 값에 `escapeHtml` 함수를 적용하면 된다.

```typescript
// [코드 6-7] html에 escapeHtml 적용
import { pipe, zip, flat, reduce, append, map } from "@fxts/core";
import { escapeHtml } from "./escapeHtml";

const html = (strs: TemplateStringsArray, ...vals: unknown[]) =>
  pipe(
    vals,
    map(escapeHtml), // vals의 각 값에 escapeHtml 적용 (XSS 예방)
    append(''),
    zip(strs),
    flat,
    reduce((a, b) => a + b)
  );

const a = '<script>alert("XSS")</script>';
const b = 'Hello & Welcome!';
console.log(html`
  <ul>
    <li>${a}</li>
    <li>${b}</li>
  </ul>
`);
// <ul>
//   <li>&lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;</li>
//   <li>Hello &amp; Welcome!</li>
// </ul>
```

출력 결과를 보면 `<script>` 태그와 큰따옴표 등이 HTML 엔티티로 변환되어 있다. 브라우저는 이를 단순한 문자 데이터로 처리하므로 악성 스크립트가 실행되지 않고 안전하게 렌더링된다.

참고로 `vals`의 타입을 `string[]`에서 `unknown[]`으로 변경한 이유는 `escapeHtml`이 `unknown` 타입의 인자를 받아 문자열로 변환하는 기능을 갖췄기 때문이다. 이로써 `html` 함수는 단순히 문자열에만 국한되지 않고 문자로 변환 가능한 다양한 타입의 값을 처리할 수 있으며 결과적으로 더욱 범용적인 형태로 발전했다.

### 1.5 중첩 데이터 처리로 컴포넌트 방식 개발 지원하기

[코드 6-8]은 하나의 템플릿(`html`) 안에 또 다른 컴포넌트(`menuHtml`)를 호출하는 예제다. 이런 방식으로 코드를 컴포넌트 단위로 분리하면 확실히 관리나 재사용성 측면에서 이점이 있다. 하지만 이 코드에서는 `menuHtml` 함수가 반환하는 HTML 조각조차 `html` 함수에 의해 일반 문자열로 인식되어 이스케이프 처리되고 있다.

```typescript
// [코드 6-8] 컴포넌트로 분리된 HTML이 모두 이스케이프 처리되는 문제
type Menu = {
  name: string;
  price: number;
};

const menuHtml = ({ name, price }: Menu) => html`<li>${name} (${price})</li>`;
const menu: Menu = { name: 'Choco Latte & Cookie', price: 8000 };

const a = '<script>alert("XSS")</script>';
const b = 'Hello & Welcome!';

const result = html`
  <ul>
    <li>${a}</li>
    <li>${b}</li>
    ${menuHtml(menu)}
    ${html`<li>${html`<b>3단계 중첩</b>`}</li>`}
  </ul>
`;
console.log(result);
// 현재 출력:
// <ul>
//   <li>&lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;</li>
//   <li>Hello &amp; Welcome!</li>
//   &lt;li&gt;Choco Latte &amp;amp; Cookie (8000)&lt;/li&gt;
//   &lt;li&gt;&lt;b&gt;3단계 중첩&lt;/b&gt;&lt;/li&gt;
// </ul>
//
// 원하는 결과 (컴포넌트로 분리한 HTML이 이스케이프되지 않기를 기대):
// <ul>
//   <li>&lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;</li>
//   <li>Hello &amp; Welcome!</li>
//   <li>Choco Latte &amp; Cookie (8000)</li>
//   <li><b>3단계 중첩</b></li>
// </ul>
```

이 예제에서 `menuHtml`은 `<li>Choco Latte &amp; Cookie (8000)</li>` 형태를 기대한다. 하지만 `html` 함수는 `menuHtml`을 통해 반환된 HTML을 단순 문자열로 간주하고 이스케이프 처리를 적용해 버렸다. 그 결과 원래 의도했던 `<li>...</li>` 태그가 문자 데이터로 렌더링되어 컴포넌트로 분리하는 방식의 개발이 불가능한 상황이다.

이는 `html` 함수가 입력받은 모든 값을 잠재적인 XSS 공격 벡터로 보고 기본적으로 이스케이프 처리하기 때문이다. 현재 구조에서는 '이 값은 이미 안전하게 처리된 HTML이므로 이스케이프하지 않아도 된다'는 정보를 전달할 방법이 없다.

그렇다면 어떻게 해야 컴포넌트로 분리한 함수에서 반환한 HTML을 이스케이프하지 않고 그대로 적용할 수 있을까? 또 이 문제를 해결할 때 단순히 한 번의 중첩만 고려하는 것이 아니라 `<b>3단계 중첩</b>`와 같이 여러 번 중첩된 상황까지 포괄적으로 처리해야 한다.

### 1.6 구조의 문제는 객체지향으로, 로직의 문제는 함수형으로 해결하기

지금까지 `html` 함수는 문자열 템플릿을 받아 문자열을 반환하는 간단한 형태였다. 그러나 중첩된 HTML 구조나 컴포넌트 방식 개발을 지원하는 과정에서 다음과 같은 문제에 부딪혔다.

- **계층적 구조**: HTML 구문을 중첩된 컴포넌트 형태로 표현하려 할 때 단순한 문자열 결합만으로는 의도한 출력 결과를 관리하기가 어렵다.
- **선택적 이스케이프**: 모든 값을 이스케이프 처리해야 하는 것은 아니며, 경우에 따라 특정 값은 이스케이프 처리하지 않고 그대로 활용해야 하는 상황이 생긴다.

이처럼 중첩된 구조와 선택적 변환 로직이 결합된 문제는 단순하지 않다. 특히 중첩 깊이가 2번인지, 3번인지 또는 그 이상인지와 상관없이, 데이터의 최심부까지 모두 순회하는 재귀적 접근이 필요하다. 이를 즉흥적으로 `if`문이나 `while`문을 추가하는 식으로 해결하려 하면 코드가 금세 복잡해지고 유지보수하기 어려워진다.

그렇다면 어떻게 접근하는 것이 가장 좋을까? 먼저 기존 `html` 함수가 `Html` 클래스를 반환하도록 변경해 보겠다.

```typescript
// [코드 6-9] Html의 인스턴스 반환
const html = (strs: TemplateStringsArray, ...vals: unknown[]) => new Html(strs, vals);
```

먼저 `html` 함수에서 `strs`와 `vals`를 `Html` 클래스의 생성자로 전달하도록 변경했다. 이로써 `html` 함수는 이제 `Html` 클래스의 인스턴스를 반환하게 된다.

다음으로 `Html` 클래스를 정의하겠다. 이전 `html` 함수에서 사용했던 `map`, `append`, `zip`, `flat`, `reduce` 로직은 그대로 유지하되, 기존에 `map(escapeHtml)`로 처리하던 부분을 `map(val => this.escape(val))`로 변경했다. `escape` 메서드는 `val`이 `Html` 인스턴스인지 일반 값인지 구분한 뒤 필요할 경우 재귀적으로 처리하므로 중첩된 구조에서도 올바르게 문자열을 변환할 수 있다.

```typescript
// [코드 6-10] Html 클래스
class Html {
  constructor(
    private strs: TemplateStringsArray,
    private vals: unknown[]
  ) {}

  private escape(val: unknown) {
    return val instanceof Html
      ? val.toHtml()       // Html 인스턴스라면 재귀적으로 toHtml() 호출
      : escapeHtml(val);   // 일반 값이라면 escapeHtml 처리
  }

  toHtml() {
    return pipe(
      this.vals,
      map(val => this.escape(val)),
      append(''),
      zip(this.strs),
      flat,
      reduce((a, b) => a + b)
    );
  }
}
```

여기서 `toHtml()`은 구조(클래스)와 로직(함수형 처리)의 결합을 잘 보여준다. 구조(클래스) 자체는 데이터(`strs`, `vals`)를 들고 있고, 로직(함수형 파이프라인)은 이 데이터를 어떻게 이스케이프하고 결합할지 결정한다. 또한 `escape()` 메서드를 통해 `Html` 인스턴스일 경우 재귀적으로 `toHtml()`을 호출함으로써 여러 단계 중첩된 HTML 구조를 문제없이 풀어낼 수 있다.

이제 준비가 끝났으니 실행하고 살펴보겠다.

```typescript
// [코드 6-11] 중첩 문제를 해결한 html 함수
const a = '<script>alert("XSS")</script>';
const b = 'Hello & Welcome!';
const menu: Menu = { name: 'Choco Latte & Cookie', price: 8000 };

const result = html`
  <ul>
    <li>${a}</li>
    <li>${b}</li>
    ${menuHtml(menu)}
    ${html`<li>${html`<b>3단계 중첩</b>`}</li>`}
  </ul>
`;
console.log(result.toHtml());
// <ul>
//   <li>&lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;</li>
//   <li>Hello &amp; Welcome!</li>
//   <li>Choco Latte &amp; Cookie (8000)</li>
//   <li><b>3단계 중첩</b></li>
// </ul>
```

출력 결과를 보면 단순히 한 단계 중첩 문제가 해결된 것뿐만 아니라 `<b>3단계 중첩</b>`와 같은 여러 단계의 중첩 문제도 재귀적으로 잘 처리된 것을 확인할 수 있다. 즉 구조적으로는 `Html` 클래스를 통한 객체지향적 접근으로 중첩 관계를 명확히 했고, 로직으로는 함수형 파이프라인을 통해 안정적이고 예측 가능한 이스케이프 처리와 문자열 결합을 구현했다.

실무에서 다루는 데이터 구조는 흔히 객체와 배열이 중첩되고 또 중첩되며, 특정 부분만 변환하거나 조합하는 일이 잦다. 이번 예제에서 적용한 패턴은 HTML 템플릿 엔진뿐만 아니라 CSV나 JSON 데이터를 가공하거나 복잡한 계층 구조를 갖는 테이블 렌더링 로직 등에도 유용하게 적용할 수 있다.

이번 문제를 해결하면서 우리는 '구조 문제는 객체지향(OOP)으로, 로직 문제는 함수형(FP)으로 해결하라'는 방법론을 익혔다. 중첩 구조와 같은 계층적인 문제는 클래스를 이용해 구조적으로 명확히 표현하고, 이스케이프 처리나 문자열 결합 로직은 함수형 패러다임을 활용해 순수하고 예측 가능한 방식으로 구현하는 것이다. 이처럼 구조(객체지향)와 로직(함수형)을 적절히 조합하는 접근은 복잡한 문제를 단순하고 예측 가능한 방식으로 해결할 수 있게 해주며, 더욱 확장성 있고 유지보수하기 쉬운 코드를 작성하는 데 기여한다.

### 1.7 배열로부터 html 문자열 만들기

지금까지는 키-값 구조의 중첩 데이터나 단일 값 중심으로 `html` 템플릿 엔진을 다뤘다. 하지만 실제 상황에서는 배열 형태의 데이터도 자주 등장한다. 예를 들어 여러 메뉴를 한 번에 렌더링해야 하는 경우가 대표적이다.

다음 [코드 6-12]에서는 메뉴 배열을 받아 `<ul>` 안에 `<li>`로 렌더링을 시도한다.

```typescript
// [코드 6-12] 메뉴 목록 그리기
type Menu = {
  name: string;
  price: number;
};

const menuHtml = ({ name, price }: Menu) => html`<li>${name} (${price})</li>`;

const menus: Menu[] = [
  { name: '아메리카노', price: 4500 },
  { name: '카푸치노', price: 5000 },
  { name: '라떼 & 쿠키 세트', price: 8000 },
];

const menuBoardHtml = (menus: Menu[]) => html`
  <div>
    <h1>메뉴 목록</h1>
    <ul>
      ${menus.map(menuHtml).reduce((acc, a) => acc + a.toHtml(), '')}
    </ul>
  </div>
`;
console.log(menuBoardHtml(menus).toHtml());
// <div>
//   <h1>메뉴 목록</h1>
//   <ul>
//     &lt;li&gt;아메리카노 (4500)&lt;/li&gt;
//     &lt;li&gt;카푸치노 (5000)&lt;/li&gt;
//     &lt;li&gt;라떼 &amp; 쿠키 세트 (8000)&lt;/li&gt;
//   </ul>
// </div>
```

[코드 6-12]에서는 `menus.map(menuHtml).reduce((acc, a) => acc + a.toHtml(), '')`로 이미 `<li>...</li>` 형태의 순수 HTML 문자열을 만든 뒤 이를 다시 상위 `html` 템플릿에 삽입하려 하고 있다. 문제는 `html` 템플릿 엔진이 인자로 주어진 값을 '안전하지 않은 데이터'로 간주하고 기본적으로 이스케이프 처리한다는 점에 있다.

- **toHtml() 결과는 단순 문자열**: `a.toHtml()`은 HTML 태그가 포함된 순수 문자열을 반환한다. 이 문자열은 상위 `html` 템플릿 함수에 전달되며, 상위 `html`은 이 값을 일반 문자열로 인식하고 `<`, `>` 같은 문자를 이스케이프 처리한다. 결국 `<li>` 태그가 `&lt;li&gt;`로 변환되는 상황이 반복된다.
- **안전한 데이터와 일반 문자열의 구분 부재**: 현재 구조에서는 '이 값은 이미 안전하게 처리된 HTML'이라는 정보를 상위 `html` 함수에 전달할 방법이 없다. `html` 함수는 단순히 모든 입력을 '이스케이프 대상'으로 보기 때문에 어느 시점에서든 문자열 형태로 합쳐진 결과는 다시 이스케이프 대상이 되고 만다.

단순히 `.reduce()`를 통해 문자열을 합치는 방식만으로는 '이미 안전한 HTML'과 '이스케이프 처리해야 할 값'을 구분하기 어렵다. 이런 접근으로는 '이미 안전한 HTML'이라는 정보를 상위 레벨로 전달하거나 이스케이프 로직이 이를 인지하게 만들 수 없다.

### 1.8 객체를 함수형으로 더하기

함수형 프로그래밍에 대한 통찰을 바탕으로 하면 이 문제를 새로운 관점에서 접근할 수 있다. 단순히 문자열을 합치는 대신 다수의 `Html` 인스턴스를 하나의 `Html` 인스턴스로 누적한다면 어떨까? 사실 [코드 6-11]에서 이미 이러한 해법의 실마리를 발견할 수 있다.

[코드 6-12a]는 문자열로 합치지 않고 `Html` 인스턴스 자체를 `reduce` 과정에서 결합하는 아이디어를 보여준다.

```typescript
// [코드 6-12a] reduce로 Html 인스턴스 합치기
const menuBoardHtml2 = (menus: Menu[]) => html`
  <div>
    <h1>메뉴 목록</h1>
    <ul>
      ${menus.map(menuHtml).reduce((a, b) => html`${a}${b}`, html``)}
    </ul>
  </div>
`;
console.log(menuBoardHtml2(menus).toHtml());
// <div>
//   <h1>메뉴 목록</h1>
//   <ul>
//     <li>아메리카노 (4500)</li>
//     <li>카푸치노 (5000)</li>
//     <li>라떼 &amp; 쿠키 세트 (8000)</li>
//   </ul>
// </div>
```

이제 `<li>` 태그와 내용이 원하는 형태로 제대로 렌더링된다. 문자열이 아닌 `Html` 인스턴스끼리 결합함으로써 '이미 안전한 HTML'이라는 상태를 유지한 채 중첩된 데이터 처리와 이스케이프 로직을 깔끔하게 해결했다.

`` html`${a}${b}` `` 구문은 마치 `a + b`처럼 두 개의 `Html` 값을 결합하여 또 다른 `Html`을 만든다. 여기서 중요한 점은 이제 더 이상 문자열로 직접 합치지 않고 `Html` 인스턴스끼리 결합하는 (마치 `concat`과 같은) 과정을 통해 '이미 안전한 HTML'이라는 상태 정보를 잃지 않는다는 점이다.

이 사례는 어떤 타입의 값이라도 해당 값을 결합하는 메서드나 식을 제공하기만 하면 `reduce`를 활용해 누적할 수 있다는 아이디어를 일깨워 준다.

### 1.9 배열 처리를 클래스 내부로 이동하여 편의성 높이기

[코드 6-10a]에서는 개발자 편의를 높이기 위해 `Html` 클래스 내부에 `combine` 메서드를 추가했다. 이 메서드는 배열이 입력될 경우 내부적으로 `` reduce((a, b) => html`${a}${b}`) `` 로직을 수행하여 별도의 처리 없이도 배열을 자동으로 하나의 안전한 HTML 문자열로 결합한다. 덕분에 단순히 배열을 전달하는 것만으로도 안전하고 완전한 HTML 문자열을 손쉽게 얻을 수 있다.

```typescript
// [코드 6-10a] 수정한 Html
class Html {
  constructor(
    private strs: TemplateStringsArray,
    private vals: unknown[]
  ) {}

  private combine(vals: unknown) {
    return Array.isArray(vals)
      ? vals.reduce((a, b) => html`${a}${b}`, html``)
      : vals;
  }

  private escape(val: unknown) {
    return val instanceof Html
      ? val.toHtml()
      : escapeHtml(val);
  }

  toHtml() {
    return pipe(
      this.vals,
      map(val => this.escape(this.combine(val))),
      append(''),
      zip(this.strs),
      flat,
      reduce((a, b) => a + b)
    );
  }
}
```

이렇게 변경함으로써 [코드 6-12b]에서 단순히 배열을 넘겨주는 것만으로도 적절한 HTML 문자열을 얻을 수 있게 된다. 이제 개발자는 별도의 `reduce` 로직을 작성할 필요 없이 `menus.map(menuHtml)` 같은 형태로 배열을 전달하면 자동으로 모든 요소가 하나의 `Html` 인스턴스로 결합되어 렌더링된다.

```typescript
// [코드 6-12b] 배열로 전달하는 menuBoardHtml
const menuBoardHtml = (menus: Menu[]) => html`
  <div>
    <h1>메뉴 목록</h1>
    <ul>
      ${menus.map(menuHtml)}
    </ul>
  </div>
`;
console.log(menuBoardHtml(menus).toHtml());
// 결과:
// <div>
//   <h1>메뉴 목록</h1>
//   <ul>
//     <li>아메리카노 (4500)</li>
//     <li>카푸치노 (5000)</li>
//     <li>라떼 &amp; 쿠키 세트 (8000)</li>
//   </ul>
// </div>
```

이제 배열 형태의 데이터를 전달하는 것만으로도 `<li>...</li>` 태그가 올바르게 렌더링된 HTML 문자열을 안전하게 얻을 수 있다. 이러한 개선을 통해 코드의 간결성을 높이고 함수형 스타일을 유지하면서도 다양한 데이터 형태를 자연스럽게 처리할 수 있다.

### 1.10 고차 함수로 추상화하기

`toHtml` 메서드 내부 로직을 고차 함수로 분리하면 재사용성과 유연성을 크게 향상시킬 수 있다. 이처럼 함수 하나로 동작을 변경할 수 있는 상황이라면 고차 함수를 통한 추상화가 간결하고 효율적인 해법이 된다.

[코드 6-13]에서는 이러한 전략을 적용하여 `toHtml` 메서드의 파이프라인 로직을 `fillTemplate`라는 고차 함수로 추상화하고, 변환(`transform`) 함수를 외부에서 전달받도록 구성했다. 이제 `toHtml`과 이 절 초반에 소개했던 `upper` 함수 모두 `fillTemplate` 함수를 활용해 구현할 수 있다.

```typescript
// [코드 6-13] fillTemplate 함수
function fillTemplate<T>(
  strs: TemplateStringsArray,
  vals: T[],
  transform: (val: T) => string
) {
  return pipe(
    vals,
    map(transform),
    append(''),
    zip(strs),
    flat,
    reduce((a, b) => a + b)
  );
}

class Html {
  constructor(
    private strs: TemplateStringsArray,
    private vals: unknown[]
  ) {}

  private combine(vals: unknown) {
    return Array.isArray(vals)
      ? vals.reduce((a, b) => html`${a}${b}`, html``)
      : vals;
  }

  private escape(val: unknown) {
    return val instanceof Html
      ? val.toHtml()
      : escapeHtml(val);
  }

  toHtml() {
    return fillTemplate(
      this.strs,
      this.vals,
      val => this.escape(this.combine(val)),
    );
  }
}

const html = (strs: TemplateStringsArray, ...vals: unknown[]) =>
  new Html(strs, vals);

function upper(strs: TemplateStringsArray, ...vals: string[]) {
  return fillTemplate(
    strs,
    vals,
    val => val.toUpperCase()
  );
}
```

이전에는 `toHtml` 메서드 안에서 `pipe`, `map`, `zip`, `reduce` 등의 함수형 로직을 직접 구성해야 했다. 이제 이들 로직을 `fillTemplate`로 추상화했기 때문에 `Html` 클래스에서는 단지 `transform` 함수만 정의하면 된다. 예를 들어 `combine` 메서드로 중첩된 `Html` 인스턴스를 결합하고 `escape` 메서드로 안전하게 문자열을 이스케이프하는 과정을 `transform` 함수를 통해 간단히 적용할 수 있다.

이처럼 함수형 프로그래밍의 고차 함수 패턴을 활용하면 로직을 쉽게 조립하고 재사용할 수 있다. `fillTemplate` 함수에 다양한 `transform` 함수를 전달하면 HTML 렌더링부터 대문자 변환까지 여러 목적의 템플릿 함수를 손쉽게 만들어낼 수 있다.

또한 `Html` 클래스 사례는 재귀적 구조화와 함수형 파이프라인을 결합하여 객체지향과 함수형 패러다임이 상호 보완적으로 작용한다는 점을 잘 보여준다. 이러한 멀티패러다임적 접근을 통해 중첩된 데이터 구조나 복잡한 문자열 처리 문제를 우아하게 해결할 수 있으며, 다양한 상황에 유연하게 적용하고 확장할 수 있다.

[코드 6-14]는 `fillTemplate`로 구현한 `html`과 `upper`를 사용한 예다.

```typescript
// [코드 6-14] fillTemplate로 구현한 html과 upper 함수 사용
const menuBoardHtml = (menus: Menu[]) => html`
  <div>
    <h1>메뉴 목록</h1>
    <ul>
      ${menus.map(menuHtml)}
    </ul>
  </div>
`;
console.log(menuBoardHtml(menus).toHtml());
// 결과:
// <div>
//   <h1>메뉴 목록</h1>
//   <ul>
//     <li>아메리카노 (4500)</li>
//     <li>카푸치노 (5000)</li>
//     <li>라떼 &amp; 쿠키 세트 (8000)</li>
//   </ul>
// </div>

const a = 'a';
const b = 'b';
console.log(
  upper`a: ${a}, b: ${b}.`
);
// a: A, b: B.
```

`menuBoardHtml`과 `upper`의 출력 결과를 보면 고차 함수 기반의 추상화가 잘 동작함을 확인할 수 있다.

### 1.11 작은 프런트엔드 개발 라이브러리 만들기

HTML 템플릿 엔진을 구현한 것을 계기로 이번에는 이를 활용한 간단한 프런트엔드 개발 라이브러리를 작성하며 Web API(바닐라 JS) 기반 개발 방식을 간략히 살펴보겠다. [코드 6-15]는 함께 만든 `Html` 템플릿 엔진을 사용하는 `View` 클래스의 예다. 제네릭을 통한 데이터 타입 제어와 추상 메서드를 통한 템플릿 정의, 명시적인 `render()` 호출을 통한 DOM 요소 생성 등 객체지향적 패턴을 담고 있다.

```typescript
// [코드 6-15] View 클래스
abstract class View<T> {
  private _element: HTMLElement | null = null;

  constructor(public data: T) {}

  element() {
    if (this._element === null) {
      throw new Error("You must call render() before accessing the element.");
    } else {
      return this._element;
    }
  }

  abstract template(): Html;

  render(): HTMLElement {
    const wrapEl = document.createElement('div');
    wrapEl.innerHTML = this.template().toHtml();
    this._element = wrapEl.children[0] as HTMLElement;
    this._element.classList.add(this.constructor.name);
    this.onRender();
    return this._element;
  }

  protected onRender() {}
}
```

`View` 클래스는 다음과 같이 구성된다.

- **제네릭을 통한 데이터 타입 지정**: 클래스 선언부에서 `abstract class View<T>`와 같이 제네릭 타입 매개변수 `T`를 사용한다. 이를 통해 `View` 인스턴스를 생성할 때 해당 뷰가 다룰 데이터 타입을 명시할 수 있으며, `this.data`를 활용할 때 타입 안전성을 확보할 수 있다.
- **템플릿 메서드 패턴 활용**: `abstract template(): Html;` 메서드는 추상 메서드로 선언되어 있으므로 구체적인 `View` 클래스는 이 메서드를 구현하여 DOM에 렌더링할 HTML 구조를 정의해야 한다. 이러한 구조는 `Html` 템플릿 엔진을 통해 문자열로 변환되며, 결과적으로 웹 브라우저상에서 실제 DOM 요소로 변환된다.
- **렌더 처리 로직**: `render()` 메서드는 `this.template()`로 `Html` 인스턴스를 반환한 뒤, `toHtml()` 메서드를 통해 받은 HTML 문자열을 임시 `div` 요소(`wrapEl`)에 삽입한다. 그리고 생성된 첫 번째 자식 요소를 `_element`에 저장하여 이후 `element()` 메서드를 통해 참조할 수 있게 한다. 생성자 이름을 `classList.add(this.constructor.name)`으로 `class=""` 속성에 추가한다. `onRender()` 메서드는 렌더 완료 후 추가로 처리가 필요할 경우 하위 클래스에서 오버라이드하여 구현할 수 있다.
- **예외 처리**: `element()` 메서드는 `_element`가 아직 렌더되지 않은 상태에서 접근하려 하면 `Error`를 발생시킨다. 이를 통해 `render()` 호출 순서에 대한 명확한 계약을 제시하며 예상치 못한 상태에 대한 에러 처리를 간단히 해결한다.

> **참고**: 여기서 `onRender()` 메서드를 `protected`로 설정한 이유나 `public`, `private`, `protected`와 같은 접근 제어자에 대한 자세한 내용은 이어지는 7.1절에서 다룬다. 해당 내용을 참고하면 접근 제어자 사용에 대한 설계 의도와 구체적인 적용 방식을 더 명확히 이해할 수 있다.

종합적으로 살펴보면 `View` 클래스는 제네릭을 통한 데이터 타입 관리, 추상 메서드를 통한 템플릿 정의, 명시적 렌더링 프로세스 및 후처리 로직 지원, 그리고 기본적인 예외 처리를 하나의 구조로 묶은 간단한 기반 클래스다.

다음은 앞서 구현한 `Html` 템플릿 엔진과 `View` 클래스를 활용해 간단한 앱을 구성한 예다.

```typescript
// [코드 6-16] UserView 예제
type User = {
  name: string;
  age: number;
};

class UserView extends View<User> {
  template(): Html {
    return html`
      <div>
        ${this.data.name} (${this.data.age})
        <button>x</button>
      </div>
    `;
  }

  protected override onRender() {
    this.element()
      .querySelector('button')!
      .addEventListener('click', () => this.remove());
  }

  private remove() {
    this.element().remove();
    alert(`${this.data.name}님을 삭제하였습니다.`);
  }
}

const users: User[] = [
  { name: 'Marty', age: 40 },
  { name: 'Jenna', age: 34 },
  { name: 'Ethan', age: 31 },
];

console.log(
  new UserView(users[0]).render().outerHTML
);
// <div class="UserView">
//   Marty (40)
//   <button>x</button>
// </div>

users
  .map(user => new UserView(user))
  .map(view => view.render())
  .forEach(element => document.body.append(element));

console.log(document.body.innerHTML);
// <div class="UserView">
//   Marty (40)
//   <button>x</button>
// </div>
// <div class="UserView">
//   Jenna (34)
//   <button>x</button>
// </div>
// <div class="UserView">
//   Ethan (31)
//   <button>x</button>
// </div>
```

[코드 6-16]에서는 Marty, Jenna, Ethan 세 명의 사용자 정보를 바탕으로 `UserView` 인스턴스를 생성하고, 콘솔에 HTML 문자열을 출력하며, `map`, `forEach`, `render()`를 통해 화면에 요소를 표시한다. 각각의 요소에는 x 버튼이 있으며 버튼을 누르면 해당 DOM 요소가 제거된다.

이 코드는 객체지향적 설계 사례다. `View`는 `Html` 클래스를 활용하여 HTML 문자열을 생성하고, 간단한 라이프사이클(`render()`, `onRender()`)에 따라 개발자가 구현한 렌더링 이후의 후처리 로직을 실행한다. 또한 `element()`를 통해 자신이 관리하는 Web API DOM 기반의 `HTMLElement`에 접근하여 `remove()` 메서드를 실행할 수 있고, 자신이 관리하는 `data`를 활용해 alert 메시지를 띄울 수 있도록 돕는다.

6.1절의 예제에서는 작은 함수와 클래스를 유기적으로 조합하며 점진적으로 문제를 해결하는 과정을 살펴봤다. 이처럼 단순한 구성 요소를 단계적으로 결합하는 접근은 문제 해결 방식을 더욱 효율적이고 확장 가능한 방향으로 이끌어 준다.

### 1.12 멀티패러다임 언어가 제시하는 기회

이 절에서 다룬 접근 방식은 멀티패러다임 언어가 제공하는 기회를 잘 활용한 사례다. 현대적인 주류 언어들은 함수형과 객체지향 그리고 명령형 패러다임까지 함께 지원한다. 이러한 언어적 기반에서 우리는 문제 상황에 따라 유연하게 패러다임을 선택하거나 섞어 쓸 수 있다. 이는 단순히 문법적 편의를 넘어 문제 해결 전략 전반을 풍성하게 만든다.

만약 이 절에서 다룬 문제들을 오직 하나의 패러다임으로만 구현하려 했다면 중첩된 구조나 변환 로직 처리 같은 복잡한 요구 사항을 해결하기가 훨씬 어려웠을 것이다. 반면 멀티패러다임 언어의 장점을 적극 활용하면 구조적 복잡성(객체지향)과 변환 로직(함수형)이라는 서로 다른 문제를 조화롭게 해결할 수 있으며, 이로써 한층 더 체계적이고 예측 가능한 코드를 작성할 수 있다. 이러한 접근은 다양한 영역에서 더 많은 문제를 효율적이고 안전하게 다룰 수 있는 능력으로 이어지며, 특정 패러다임에 매이지 않고 유연한 전략을 구사할 수 있는 토대가 된다.

현대 언어들이 제공하는 클래스, 일급 함수, 이터러블, 리스트 프로세싱 함수 세트 등은 단순한 편의 이상의 의미를 갖는다. 객체지향, 함수형, 명령형 패러다임은 각각 긴 시간에 걸쳐 발전하고 정통성을 쌓아 온 패턴과 개념, 기능, 사고 방식을 품고 있다. 이 유산들을 적절히 조합하고 활용함으로써 일시적인 라이브러리나 특정 프레임워크에 치중된 접근을 넘어 보다 근본적이고 검증된 해결책을 적용할 수 있다. 이는 우리가 작성하는 코드가 단순히 동작하는 수준을 넘어 오랫동안 축적된 프로그래밍 지혜에 기반한 '좋은 코드'로 평가받는 합리적인 근거가 된다.

이처럼 언어적 토양과 패러다임적 유산을 풍부하게 활용하는 멀티패러다임적 접근은 다양한 문제에 대응할 수 있는 안정적이고 확장 가능한 해법을 제시하며, 앞으로의 프로그래밍 업무에 든든한 기반이 될 것이다.

---

## 2. 멀티패러다임을 활용한 동시성 핸들링

이번에는 멀티패러다임 접근을 활용하여 동시성을 효과적으로 다루는 사례를 살펴보겠다. 4.2절에서는 `Promise`를 반환하는 함수들의 배열과 `limit` 값을 받아 해당 `limit` 단위로 순차적으로 작업을 그룹화하여 실행하는 `executeWithLimit` 함수를 구현한 뒤, 이를 함수형 패러다임으로 재구성하는 과정을 다룬 바 있다.

이번 절에서는 조금 다른 요구 사항을 가진 `runTasksWithPool` 함수를 만들어 본다. 이번에는 단순히 `limit` 단위로 순차 실행하는 것이 아니라 동시에 실행되는 작업을 특정 개수로 유지하면서 진행하도록 한다. 우선 ChatGPT에게 `runTasksWithPool` 함수를 구현해보도록 맡긴 뒤, 다시 멀티패러다임적인 관점에서 이를 재구성하는 과정을 통해 동시성 핸들링을 안전하게 해결하는 방법을 살펴보겠다.

### 2.1 executeWithLimit 다시 보기

`runTasksWithPool` 함수를 구현하기 전에 4.2절에서 다뤘던 `executeWithLimit` 함수를 간단히 되짚어 보겠다. `executeWithLimit`는 함수를 일정 개수(`limit`) 단위로 모아 순차적으로 `Promise.all`을 실행하는 방식으로 동시성 부하를 제어하는 함수였다.

```typescript
// [코드 6-17] 명령형 executeWithLimit 함수
async function executeWithLimit<T>(
  fs: (() => Promise<T>)[],
  limit: number
): Promise<T[]> {
  const results: T[] = [];
  for (let i = 0; i < fs.length; i += limit) {
    const batchPromises = [];
    for (let j = 0; j < limit && (i + j) < fs.length; j++) {
      batchPromises.push(fs[i + j]());
    }
    const batchResults = await Promise.all(batchPromises);
    results.push(...batchResults);
  }
  return results;
}
```

[코드 6-17]은 전통적인 명령형 방식으로 `executeWithLimit`를 구현한 예시다. 함수들을 `limit` 크기의 청크로 나누어 순차 실행하므로 한 번에 처리하는 Promise의 수를 제어할 수 있다.

4.2절에서는 이 로직을 함수형 패러다임을 활용해 다음과 같이 재구현하는 과정을 소개했다.

```typescript
// [코드 6-18] 함수형 executeWithLimit 함수
const executeWithLimit = <T>(fs: (() => Promise<T>)[], limit: number): Promise<T[]> =>
  fx(fs)
    .map(f => f())
    .chunk(limit)
    .map(ps => Promise.all(ps))
    .to(fromAsync)
    .then(arr => arr.flat());
```

[코드 6-18]에서 사용한 `fx`는 이 책에서 함께 만든 `FxIterable`을 반환한다.

그리고 다음 [코드 6-19]에서 사용한 `fx`는 FxTS 라이브러리의 함수이며, 이를 이용하면 동일한 로직을 더욱 간결하고 선언적으로 표현할 수 있다.

```typescript
// [코드 6-19] FxTS를 활용한 함수형 executeWithLimit 함수
import { fx } from "@fxts/core";

const executeWithLimit = <T>(fs: (() => Promise<T>)[], limit: number): Promise<T[]> =>
  fx(fs)
    .toAsync()
    .map(f => f())
    .concurrent(limit)
    .toArray();
```

앞선 예시들은 모두 의도한 대로 동작하며 동시성 부하를 제어하는 다양한 접근 방식을 잘 보여준다. 이제 이러한 경험을 바탕으로 동시에 실행되는 작업 수를 특정 개수로 유지하는 `runTasksWithPool` 함수를 살펴보겠다. 이번에도 마찬가지로 ChatGPT를 활용해 명령형 스타일로 먼저 구현한 뒤, 멀티패러다임 접근을 통해 더욱 선언적이고 확장성 있는 형태로 재구성하는 과정을 거칠 예정이다.

### 2.2 ChatGPT가 명령형으로 구현한 동시성 핸들링 함수

`executeWithLimit` 함수는 비동기 작업을 일정한 크기(`limit`) 단위로 나누어 순차적으로 실행하는 단순한 부하 조절 로직을 갖추고 있다. 이번에는 이보다 한 단계 더 복잡한 상태 관리가 필요한 동시성 핸들링 함수 `runTasksWithPool`을 구현해 보려고 한다.

`runTasksWithPool`은 특정 `poolSize` 값만큼 동시에 작업을 실행하고, 하나의 작업이 완료될 때마다 대기 중인 새로운 작업을 실행하는 형태로 동작하도록 설계한다. 이전과 마찬가지로 먼저 ChatGPT에게 이 함수를 구현하도록 요청한다.

```typescript
// [코드 6-20] ChatGPT가 구현한 runTasksWithPool 함수
async function runTasksWithPool<T>(
  fs: (() => Promise<T>)[],
  poolSize: number
): Promise<T[]> {
  const results: T[] = [];                        // ①
  const activePromises: Promise<void>[] = [];     // ②

  for (let i = 0; i < fs.length; i++) {           // ③
    const taskFactory = fs[i];
    // 각 작업을 실행하고 결과를 해당 인덱스에 저장한 뒤, 완료 시 activePromises에서 제거
    const p = taskFactory()
      .then((fetchedValue) => {
        // 작업 완료 시 결과 배열에 할당
        results[i] = fetchedValue;
        // 해당 작업이 완료되었으므로 activePromises에서 제거
        const removeIndex = activePromises.indexOf(p);
        if (removeIndex > -1) {
          activePromises.splice(removeIndex, 1);
        }
      });

    // 실행 중인 작업 리스트에 현재 작업 추가
    activePromises.push(p);

    // 현재 실행 중인 작업 수가 제한에 도달하면 하나가 끝날 때까지 대기
    if (activePromises.length >= poolSize) {       // ④
      // 가장 먼저 완료되는 작업을 기다려 실행 중인 작업 수를 조정
      await Promise.race(activePromises);
    }
  }
  // 남은 모든 작업이 완료될 때까지 대기 후 결과 반환
  await Promise.all(activePromises);               // ⑤
  return results;
}
```

이 코드는 다음과 같이 작동한다.

- ① **results 배열**: 각 `fs` 요소(작업 함수)가 반환하는 Promise의 결과를 인덱스에 맞춰 저장한다. 실행 순서와 상관없이 원래의 함수 순서대로 결과를 관리할 수 있다.
- ② **activePromises 배열**: 현재 실행 중인 Promise들을 추적하는 배열이다. 작업 하나가 완료되면 이 배열에서 해당 Promise를 제거한다.
- ③ **루프 내 작업 실행**: `for` 루프를 사용해 각 작업을 순회한다. 각 작업(`taskFactory`)을 호출하고 결과를 `then` 체인에서 `results[i]`에 할당한다. 이어서 `then`을 추가로 호출하여 작업 완료 시 `activePromises`에서 해당 Promise를 제거한다.
- ④ **동시 실행 개수 제어**: 새로운 작업을 `activePromises` 배열에 추가한 뒤, 배열 길이가 `poolSize`에 도달하면 `Promise.race(activePromises)`를 통해 가장 먼저 완료되는 작업을 대기한다. 이로써 한 번에 최대 `poolSize` 개수만큼만 동시 실행한다.
- ⑤ **모든 작업 완료 대기**: 루프가 끝난 뒤에도 아직 완료되지 않은 작업들이 `activePromises`에 남아 있을 수 있다. `Promise.all(activePromises)`를 호출하여 모든 남은 작업이 완료될 때까지 기다린 뒤 최종적으로 `results` 배열을 반환한다.

[코드 6-21]은 `runTasksWithPool` 함수의 동작을 테스트하는 예제 코드다. 이를 통해 콘솔 로그가 의도한 타이밍에 맞춰 출력되는지 확인할 수 있다.

```typescript
// [코드 6-21] 동작 테스트
function createAsyncTask(name: string, ms: number): () => Promise<string> {
  return () =>
    new Promise(resolve => {
      console.log(`Started: ${name}`);
      setTimeout(() => {
        console.log(`Finished: ${name}`);
        resolve(name);
      }, ms);
    });
}

const tasks = [
  createAsyncTask("A", 1000),
  createAsyncTask("B", 500),
  createAsyncTask("C", 800),
  createAsyncTask("D", 300),
  createAsyncTask("E", 1200),
];

const poolSize = 2;
const results = await runTasksWithPool(tasks, poolSize);
console.log("Results:", results);
```

ChatGPT가 작성한 `runTasksWithPool` 함수는 의도에 맞게 동작하긴 하지만 코드를 읽고 추적하기가 상당히 어렵게 느껴진다. 최대 `poolSize`개의 작업이 동시에 실행되는 과정에서 완료된 작업과 대기 중인 작업 간의 상태 변화가 복잡하게 얽히면서 여러 상태 변수가 기록되고 참조된다. 이러한 코드를 이해하고 유지보수하는 일은 쉽지 않다.

### 2.3 멀티패러다임으로 구현한 동시성 핸들링 함수

이번에는 이 문제를 멀티패러다임으로 접근하여 다시 해결하는 과정을 살펴보며, 복잡한 동시성 로직을 보다 명확하고 직관적으로 표현하는 방법을 모색해 보겠다.

[코드 6-22]의 `runTasksWithPool` 함수는 추가적인 라이브러리나 복잡한 헬퍼 함수 없이 언어에서 기본적으로 제공하는 기능들만 이용해 구현되었다. Array의 내장 메서드(`map`, `findIndex`, `splice` 등)와 간단한 사용자 정의 클래스(`TaskRunner`)를 활용하여 별도 패러다임 전환 없이도 직관적인 명령형 스타일로 동시성 제어 로직을 완성할 수 있다.

```typescript
// [코드 6-22] 멀티패러다임으로 구현한 runTasksWithPool 함수
class TaskRunner<T> {
  private _promise: Promise<T> | null = null;
  private _isDone = false;

  get promise() { return this._promise ?? this.run(); }
  get isDone() { return this._isDone; }

  constructor(private f: () => Promise<T>) {}

  async run() {
    if (this._promise) {
      return this._promise;
    } else {
      return this._promise = this.f().then(res => {
        this._isDone = true;
        return res;
      });
    }
  }
}

async function runTasksWithPool<T>(
  fs: (() => Promise<T>)[],
  poolSize: number
): Promise<T[]> {
  const tasks = fs.map(f => new TaskRunner(f));
  const pool: TaskRunner<T>[] = [];

  for (const task of tasks) {
    pool.push(task);
    if (pool.length < poolSize) continue;
    await Promise.race(pool.map(task => task.run()));
    pool.splice(pool.findIndex(task => task.isDone), 1);
  }

  return Promise.all(tasks.map(task => task.promise));
}
```

`TaskRunner` 클래스는 비동기 작업을 감싸는 래퍼로, 작업의 실행 상태(`_isDone`)와 Promise를 관리한다. `run()` 메서드는 멱등성을 보장하여 이미 실행된 작업을 다시 호출해도 같은 Promise를 반환한다. 이 클래스 덕분에 `runTasksWithPool` 함수의 본체 로직이 매우 간결해진다.

`for...of` 루프로 각 작업을 순회하며 `pool`에 추가한다. `pool`의 크기가 `poolSize`보다 작으면 `continue`로 다음 작업을 바로 추가한다. `poolSize`에 도달하면 `Promise.race`로 가장 먼저 완료되는 작업을 기다린 뒤, 완료된 작업을 `pool`에서 제거한다. 마지막으로 모든 작업의 결과를 `Promise.all`로 수집하여 반환한다.

이 예제에는 명령형 흐름(`for` 루프, `await`, `Promise.race`)과 객체지향적 상태 관리(`TaskRunner` 인스턴스) 그리고 배열 메서드(`map`, `findIndex`, `splice`)를 활용한 부분적 함수형 스타일을 조화롭게 결합했다. 이를 통해 복잡한 문제를 간결하면서도 이해하기 쉽게 해결할 수 있다.

### 2.4 함수에서 클래스로 점진적 확장

이제 외부의 자원 상황이나 판단에 따라 `setPoolSize` 메서드를 통해 `TaskPool`의 `poolSize`를 자유롭게 동적으로 변경할 수 있다.

한편 `TaskPool` 클래스는 처음부터 클래스로 출발한 것이 아니라 초기에는 단순히 `runTasksWithPool` 함수로 시작했다. 이후 `setPoolSize()`와 같은 새로운 요구 사항이 생기면서 이를 수용하기 위해 클래스를 도입하고 구조를 확장한 것이다. 이처럼 처음에는 간단한 함수 형태로 문제를 해결한 뒤, 기능적 요구 사항이나 복잡성이 늘어날 때 점진적으로 클래스를 도입하고 추상화를 높이는 방식이 더 실용적이다. 이런 방식으로 접근하면 불필요한 선행 설계로 인한 코드 부담을 줄이고, 필요한 시점에 필요한 만큼만 추상화를 적용함으로써 팀 생산성과 코드 품질 모두를 향상시킬 수 있다.

### 2.5 무한 반복되는 작업의 부하 조절하기

만약 무한 반복되는 작업의 부하를 `TaskPool`로 조절하고자 한다면 어떻게 해야 할까? 이때는 작업을 이터레이터로 받아들일 수 있도록 구조를 변경하고, 이터레이터의 지연성을 활용해 무한 반복이 가능하도록 대응하면 된다.

```typescript
// [코드 6-25] 이터러블 이터레이터를 지원하는 TaskPool 클래스
function* map<A, B>(
  f: (value: A) => B, iterable: Iterable<A>
): IterableIterator<B> {
  for (const value of iterable) {
    yield f(value);
  }
}

class TaskPool<T> {
  private readonly taskIterator: IterableIterator<TaskRunner<T>>;
  private readonly pool: TaskRunner<T>[] = [];
  public poolSize: number;

  // ① (() => Promise<T>)[]에서 Iterable<() => Promise<T>>로 변경
  constructor(fs: Iterable<() => Promise<T>>, poolSize: number) {
    this.taskIterator = map(f => new TaskRunner(f), fs); // ② 이터러블 map으로 변경
    this.poolSize = poolSize;
  }

  setPoolSize(poolSize: number) {
    this.poolSize = poolSize;
  }

  private canExpandPool() {
    return this.pool.length < this.poolSize;
  }

  async runAll() {
    const { pool, taskIterator } = this;
    const tasks: TaskRunner<T>[] = [];

    while (true) {                                       // ③ 반복 방식 변경
      const { done, value: nextTask } = taskIterator.next();
      if (!done) {
        pool.push(nextTask);
        tasks.push(nextTask);
        if (this.canExpandPool()) continue;
      }
      if (done && pool.length === 0) break;
      await Promise.race(pool.map(task => task.run()));
      pool.splice(pool.findIndex(task => task.isDone), 1);
    }
    return Promise.all(tasks.map(task => task.promise));
  }
}
```

다음은 이전 버전에서 [코드 6-25]로 변경된 주요 사항과 이유를 정리한 내용이다.

- ① **fs 타입 변경**: `(() => Promise<T>)[]`에서 `Iterable<() => Promise<T>>`로 변경했다. 무한 반복 작업을 지원하려면 `fs`가 배열이 아니라 이터러블 혹은 이터러블 이터레이터여야 한다.
- ② **this.tasks 초기화 로직 변경**: `fs.map(f => new TaskRunner(f))`에서 `map(f => new TaskRunner(f), fs)`로 변경했다. `map` 제너레이터 함수는 `fs` 이터러블을 입력받아 `TaskRunner`들을 반환할 이터러블 이터레이터를 생성한다.
- ③ **runAll 메서드에서 작업 반복 방식 변경**: `taskIterator.next()`로 이터레이터에서 항목을 하나씩 꺼내고, `nextTask`를 `pool`과 `tasks`에 담는다. 더 이상 꺼낼 항목이 없고(`done === true`) `pool`이 모두 소진되었을 때(`pool.length === 0`) 반복을 종료한다. `taskIterator`가 무한 이터레이터라면 무한 반복을 지원한다.

이전 버전에서는 고정된 크기의 배열(`(() => Promise<T>)[]`)로 전달된 작업을 순차적으로 처리하고 모두 완료한 뒤 종료한다. 반면 [코드 6-25]에서는 이터러블(`Iterable<() => Promise<T>>`)을 사용하여 `while(true)` 루프 안에서 필요할 때마다 `taskIterator.next()`로 새 작업을 꺼내 `pool`에 추가한다. 더 이상 가져올 작업이 없으면(`done === true`) `pool`의 모든 작업이 끝날 때까지 기다린 후 종료한다. 이로써 `TaskPool`은 무한히 동적으로 생성되는 작업에도 부하를 조절하며 유연하게 대응할 수 있게 된다.

다음은 무한 이터레이터를 활용해 페이지를 계속해서 크롤링하는 작업을 `TaskPool`로 부하를 조절하며 처리하는 개념적인 예시다.

```typescript
// [코드 6-26] 무한 반복 이터레이터로 TaskPool을 생성하는 콘셉트의 코드
import { map, range, delay } from "@fxts/core";

async function crawling(page: number) {
  console.log(`${page} 페이지 분석 시작`);
  await delay(5_000);
  console.log(`${page} 페이지 저장 완료`);
  return page;
}

void new TaskPool(
  map(page => () => crawling(page), range(Infinity)),
  5
).runAll();
```

결과적으로 이 코드는 무한히 많은 페이지를 순회하면서도 동시에 실행되는 크롤링 작업 수를 5개로 제한해 무리 없이 데이터를 수집하는 구조를 보여준다. 이처럼 클래스, 명령형, 함수형, 이터레이터 등 각각의 강점을 살려 멀티패러다임적으로 문제를 해결하면 유연성과 가독성, 확장성 등 여러 이점을 함께 살릴 수 있다.

### 2.6 runAllSettled 추가하기

마지막으로 `Promise.allSettled()` 역할을 구현하는 `runAllSettled()` 메서드를 추가하여 마무리하겠다. `runAllSettled()`는 `Promise.allSettled()`와 동일하게 모든 작업이 완료될 때까지 기다린 뒤 각 작업의 성공/실패 상태를 배열 형태로 반환한다. 그러면서도 `TaskPool`은 `poolSize`를 활용하여 동시에 실행하는 작업 수를 제어하므로 부하를 적절히 분산하면서 모든 작업의 결과를 한 번에 확인할 수 있다.

```typescript
// [코드 6-27] runAllSettled 추가
class TaskPool<T> {
  private readonly taskIterator: IterableIterator<TaskRunner<T>>;
  private readonly pool: TaskRunner<T>[] = [];
  public poolSize: number;

  constructor(fs: Iterable<() => Promise<T>>, poolSize: number) {
    this.taskIterator = map(f => new TaskRunner(f), fs);
    this.poolSize = poolSize;
  }

  setPoolSize(poolSize: number) {
    this.poolSize = poolSize;
  }

  private canExpandPool() {
    return this.pool.length < this.poolSize;
  }

  private async run(errorHandle: (err: unknown) => unknown) {
    const { pool, taskIterator } = this;
    const tasks: TaskRunner<T>[] = [];

    while (true) {
      const { done, value: nextTask } = taskIterator.next();
      if (!done) {
        pool.push(nextTask);
        tasks.push(nextTask);
        if (this.canExpandPool()) continue;
      }
      if (done && pool.length === 0) break;
      await Promise.race(pool.map(task => task.run())).catch(errorHandle);
      pool.splice(pool.findIndex(task => task.isDone), 1);
    }
    return tasks.map(task => task.promise);
  }

  async runAll() {
    return Promise.all(await this.run(err => Promise.reject(err)));
  }

  async runAllSettled() {
    return Promise.allSettled(await this.run(() => undefined));
  }
}
```

앞서 [코드 6-25]에서는 `runAll()` 메서드 내에서 모든 로직을 처리했지만, 이제는 공통된 로직을 `run()` 메서드로 추출하고 `runAll`과 `runAllSettled()`에서 이 로직을 활용하도록 구조를 변경했다.

1. **공통 로직 추출**: `run()` 메서드가 작업들을 순차적으로 풀에 추가하고 `poolSize`만큼 병렬로 수행되도록 관리하는 공통 로직을 담당한다.
2. **runAll() 동작**: `runAll()`은 `run()`에서 반환한 Promise 배열을 `Promise.all()`로 처리한다. 모든 작업이 성공적으로 완료될 때까지 대기하는 패턴을 구현한다.
3. **runAllSettled() 동작**: `runAllSettled()`는 `run()`에서 반환한 Promise 배열을 `Promise.allSettled()`로 처리한다. 모든 작업을 실패 여부와 상관없이 끝날 때까지 기다리고 결과를 한 번에 받아볼 수 있는 패턴을 적용한다.

에러 처리 방식도 이를 반영하도록 바뀌었다.

- ④ **run 메서드의 보조 함수와 catch 추가**: `run()` 메서드는 `errorHandle: (err: unknown) => unknown`과 같은 보조 함수를 인자로 받는다. 이를 통해 외부에서 에러 처리 전략을 유연하게 바꿀 수 있다. `Promise.race(...)`에는 `.catch(errorHandle)`을 추가했다.
- ⑤ **runAll()의 에러 처리**: `runAll()`은 `errorHandle`로 `err => Promise.reject(err)`를 전달한다. 이는 `await Promise.race(...)`가 실행될 때 만약 어떤 작업(`task.run()`)이 에러를 발생시키면 `Promise.reject`를 던져 그 즉시 실패하도록 만든다. 결과적으로 `runAll()`은 '하나라도 실패하면 전체가 실패'하는 `Promise.all()`의 원래 동작 방식에 충실하다.
- ⑥ **runAllSettled()의 에러 처리**: `runAllSettled()`는 `errorHandle`로 `() => undefined`를 전달한다. 이는 `task.run()`에서 발생하는 에러를 사실상 무시(숨김)하는 방식으로 처리하여 `await Promise.race(...)` 호출 시 에러가 전파되지 않게 한다. 그 결과 모든 작업이 끝날 때까지 계속 진행할 수 있고, 마지막에 `Promise.allSettled()`를 통해 성공/실패 결과를 모두 담은 배열을 얻을 수 있다.

이렇게 설계한 `TaskPool` 클래스는 원하는 시나리오에 맞춰 동작 모드를 쉽게 전환할 수 있다. 메서드를 선택하는 것만으로 '하나라도 실패 시 즉시 중단'하거나 '실패한 작업이 있어도 끝까지 진행한 뒤 전체 결과를 수집'하는 식으로 로직과 결과물을 결정할 수 있다. 이를 구현하면 [코드 6-28]과 같다.

```typescript
// [코드 6-28] runAllTest, runAllSettledTest
const tasks = [
  createAsyncTask("A", 1000),
  () => createAsyncTask("B", 500)().then(() => Promise.reject('no!')),
  createAsyncTask("C", 800),
  createAsyncTask("D", 300),
  createAsyncTask("E", 1200),
];

async function runAllTest() {
  try {
    const result = await new TaskPool(tasks, 2).runAll();
    console.log(result); // 여기 오지 않음
  } catch (e) {
    // 하나라도 실패하면 여기로
    console.log(e); // "no!"
  }
}
await runAllTest();

async function runAllSettledTest() {
  const result = await new TaskPool(tasks, 2).runAllSettled();
  console.log(result);
  // [
  //   { status: "fulfilled", value: "A" },
  //   { status: "rejected", reason: "no!" },
  //   { status: "fulfilled", value: "C" },
  //   { status: "fulfilled", value: "D" },
  //   { status: "fulfilled", value: "E" }
  // ]
}
await runAllSettledTest();

async function runAllTest2() {
  try {
    const task = (page: number) => () =>
      page === 7
        ? Promise.reject(page)
        : crawling(page);
    await new TaskPool(map(task, range(Infinity)), 5).runAll();
  } catch (e) {
    // 하나라도 실패하면 무한 작업을 중단하고 여기로
    console.log(`crawling 중간에 실패! (${e} 페이지)`);
    // crawling 중간에 실패! (7 페이지)
  }
}
await runAllTest2();

await delay(10_000);
console.log('--');

async function runAllSettledTest2() {
  const task = (page: number) => () =>
    page === 7
      ? Promise.reject(page)
      : crawling(page);
  const taskPool = new TaskPool(map(task, range(Infinity)), 5);
  // 중간에 실패해도 무한 작업 계속 진행
  void taskPool.runAllSettled();
  // 10초 후 poolSize를 5에서 10으로 변경
  setTimeout(() => {
    taskPool.setPoolSize(10);
  }, 10_000);
}
void runAllSettledTest2();
```

`TaskPool` 클래스는 객체지향, 함수형, 명령형 패러다임을 조화롭게 활용한 예다. `poolSize`와 같은 상태를 관리하고 외부에서 메시지를 전달받으려면 객체지향적 설계가 유리하다. `for...of`, `while`, `if`, `await`, `continue` 등을 사용하는 명령형 스타일은 상황에 따라 오히려 코드를 단순하고 명확하게 만들 수 있다. 거기에 함수형적이고 선언적인 메서드와 값(`map`, `findIndex`, `Promise.all`, `race` 등)을 적절히 조합함으로써 간결하고 이해하기 쉬운 코드를 완성할 수 있다. 또한 이터레이터를 활용하여 무한 반복 작업과 같은 확장성을 구조적으로 제공하고 안전하게 제어할 수 있다.

추가로 `runAllSettled()`를 구현하는 과정에서 함수 전달을 통해 로직을 확장하는 아이디어를 사용한 점에 주목해 볼 가치가 있다. 이를 통해 `Promise.all`과 `Promise.allSettled`의 동작 방식을 세밀하고 정확하게 구현하면서 에러 처리 또한 유연하게 제어할 수 있다. 결국 언어의 기능을 충분히 활용하면 더 강력하고 유연한 문제 해결 능력을 얻을 수 있다.

정리하자면 이 절의 사례들은 함수형 패러다임만을 고집하거나 상태 없는 설계를 강조할 때 오히려 복잡해질 수 있는 문제를 명령형 및 객체지향 패러다임과 적절히 조합함으로써 간단하고 이해하기 쉬운 코드로 해결했다. 함수형 패러다임만으로 해결하려 했다면 상태 추적을 위해 부담스러운 추상화가 필요할 수도 있고, 순수 명령형 접근만으로는 상태 변경과 외부와의 통신을 깔끔하게 처리하기 어려웠을 것이다. 결국 이러한 복잡한 요구 사항에서는 멀티패러다임적 접근이 실용적이며, 상황에 따라 하나의 함수 내에서도 적합한 패러다임을 유연하게 선택하는 것이 생산성, 유지보수성, 가독성, 확장성 모두를 확보하는 길임을 확인할 수 있다.

---

## 요약

- **구조 문제는 객체지향으로, 로직 문제는 함수형으로 해결하기**: 복잡하고 중첩된 데이터나 계층적인 구조를 다룰 때는 객체지향 패러다임을 활용해 명확한 구조를 잡을 수 있다. 반면 데이터 변환이나 리스트 프로세싱과 같은 순수한 로직 문제는 함수형 패러다임을 통해 예측 가능하고 안정적으로 구현할 수 있다. 이러한 역할 분담은 코드 이해도를 높이고 유지보수성을 향상시키는 데 큰 도움이 된다.
- **문제에 적합한 패러다임을 과감히 선택하기**: 단일 패러다임에 매여 복잡한 문제를 억지로 풀기보다는 상황에 따라 객체지향, 함수형, 명령형 패러다임을 조화롭게 섞어 쓰는 전략이 훨씬 효율적이다. 문제의 본질에 맞는 패러다임을 과감히 선택하고 해당 패러다임이 제공하는 강점을 적극 활용하면 복잡한 요구 사항도 깔끔하게 해결할 수 있다.
- **객체에 상태를 기록하고 값으로 다루기**: 객체지향 패러다임을 활용하면 관심사를 명확히 분리하고 문제 영역의 개념을 직관적으로 모델링할 수 있다. 클래스와 객체는 데이터(상태)와 그 상태를 변화시키는 행위(메서드)를 하나의 추상화 단위로 묶어 준다. 이를 통해 변화하는 상황을 체계적으로 관리하고 다른 부분에서 반복적으로 고려해야 할 세부 사항을 숨길 수 있다. 예를 들어 동시성 제어를 담당하는 `TaskRunner`와 `TaskPool` 클래스처럼 객체에 상태를 기록하고 이 상태를 명확히 제어하는 것은 직관적인 코드 흐름을 확보하는 데 유용하다. 또한 이런 객체를 함수형 변환 로직과 결합하면 순수하고 예측 가능한 데이터를 처리하는 과정과 구조적이고 명확한 상태 관리를 자연스럽게 통합하여 궁극적으로 안정적이고 읽기 쉬운 코드를 만들어낼 수 있다.
- **변화를 알리고 통신하기**: 분리된 객체들은 자신의 상태 변화를 이벤트 형태로 외부에 알리도록 설계할 수 있다. 이를 통해 다른 객체나 로직이 상황 변화를 감지하고 적절히 대응하는 구조를 손쉽게 구축할 수 있다. 이러한 객체 간 통신은 일급 함수, 이터레이터, 제너레이터 등 멀티패러다임 언어에서 제공하는 다양한 기능을 적극 활용함으로써 더욱 직관적이고 우아하게 구현 가능하다. 결과적으로 각 컴포넌트의 복잡한 상호 작용을 명확하고 이해하기 쉬운 방식으로 표현할 수 있게 된다.
