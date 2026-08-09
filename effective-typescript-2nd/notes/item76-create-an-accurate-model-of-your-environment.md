# Item 76: 실행 환경의 정확한 모델 만들기 (Create an Accurate Model of Your Environment)

## 핵심 질문

타입스크립트가 내 코드의 런타임 동작을 정확히 검사하려면 무엇을 알아야 하는가? lib 설정, 전역 변수, 특수 import는 어떻게 모델링하는가?

Item 3에서 봤듯 타입스크립트 코드는 자바스크립트로 변환되어 실행된다. 더 구체적으로는 **특정 런타임**(V8·JavaScriptCore·SpiderMonkey)에서 **특정 환경**(브라우저의 웹 페이지, Node.js의 테스트 러너, Deno, Electron 등) 위에서 실행된다. 타입스크립트가 코드의 런타임 동작을 정적으로 모델링하려면 **그 환경의 모델**이 필요하다. 타입스크립트 프로젝트 설정의 주요 목표 하나는 이 모델을 최대한 정확하게 만드는 것이다 — **환경을 정확하게 모델링할수록 타입스크립트가 오류를 더 잘 찾는다.**

## 1. lib 설정 — 브라우저와 ECMAScript 버전

생성된 자바스크립트가 HTML 페이지에 포함되어 브라우저에서 돈다면, tsconfig.json의 `lib` 설정으로 모델링한다.

```json
{
  "compilerOptions": {
    "lib": ["dom", "es2021"]
  }
}
```

`"dom"`은 브라우저용 타입 선언을 포함하라는 뜻이고, `"es2021"`은 그 해의 자바스크립트 표준을 브라우저가 (네이티브로든 폴리필로든) 지원한다고 기대한다는 뜻이다. 더 새 버전의 기능(예: `array.toSorted()`)을 쓰면 타입 에러가 난다. 어느 ECMAScript 버전에 어떤 기능이 있는지 정확히 몰라도 **타입스크립트는 안다** — 환경의 정확한 모델을 만들어 두면 이런 실수를 잡아 준다. `@types/web` 패키지를 설치해 브라우저 타입의 버전을 좀 더 세밀하게 통제할 수도 있다(타입스크립트와 DOM은 Item 75).

## 2. 페이지의 다른 script 태그들 — 전역과 라이브러리

내 스크립트 태그가 페이지의 유일한 태그가 아닐 것이다.

```html
<script type="text/javascript">
window.userInfo = { name: 'Jane Doe', accountId: '123-abc' };
</script>
<script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
<script type="text/javascript">
// ... Google Analytics 로드 ...
</script>
<script src="path/to/bundle.js"></script>
```

각 `<script>` 태그가 환경을 어떤 식으로든 수정한다 — 내 코드에서 쓸 수 있는 전역 변수를 추가한다. 정확한 타입 체크를 위해 타입스크립트에 알려야 한다.

**전역 변수는 타입 선언 파일로 모델링**한다(Window 문법은 Item 47).

```typescript
// user-info-global.d.ts
interface UserInfo {
  name: string;
  accountId: string;
}
declare global {
  interface Window {
    userInfo: UserInfo;
  }
}
```

**라이브러리는 타입 선언 설치로 모델링**한다.

```
$ npm install --save-dev @types/google.analytics @types/jquery
```

정확한 모델을 위해서는 **@types 패키지가 페이지에서 로드하는 라이브러리의 버전을 모델링하는 것이 필수**다(버전 맞추기는 Item 66). 틀리면 가짜 에러를 보고하거나 진짜 에러를 놓친다.

## 3. 번들러의 특수 import

webpack으로 번들한다면 자바스크립트에서 CSS·이미지 파일을 직접 import할 수 있다. 이 파일들도 환경의 일부지만 타입스크립트는 모른다.

```typescript
import sunrisePath from './images/beautiful-sunrise.jpg';
//                      ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// Cannot find module './images/beautiful-sunrise.jpg' or its type declarations.
```

이런 종류의 import를 모델링해야 한다.

```typescript
// webpack-imports.d.ts
declare module '*.jpg' {
  const src: string;
  export default src;
}
```

webpack의 CSS 모듈(CSS 규칙을 개별 import)을 쓴다면 그것도 모델에 추가하거나 대신 해 주는 npm 패키지를 설치해야 한다.

## 4. 환경이 여럿이라면 — 프로젝트 레퍼런스

앱의 부분마다 다른 환경에서 돌 수 있다 — 브라우저의 클라이언트 코드, Node.js의 서버 코드, 자체 환경의 테스트 코드. 별개의 환경이므로 **따로 모델링**해야 한다. 통상의 방법은 여러 tsconfig.json 파일과 프로젝트 레퍼런스다(Item 78).

브라우저처럼 Node.js 환경도 정확히 모델링하라 — Node.js 20으로 실행한다면 그 버전의 `@types/node`를 설치하라. 런타임에 실제로 쓸 수 있는 라이브러리 기능만 쓰도록 보장해 준다.

## 기억해야 할 것들

- 코드는 특정 환경에서 실행된다. 그 환경의 정확한 정적 모델을 만들면 타입스크립트가 코드를 더 잘 검사한다.
- 코드와 함께 웹 페이지에 로드되는 전역 변수와 라이브러리를 모델링하라.
- 타입 선언과 실제 사용하는 라이브러리·런타임 환경의 버전을 맞춰라.
- 한 프로젝트 안의 서로 다른 환경(클라이언트와 서버 등)은 여러 tsconfig.json과 프로젝트 레퍼런스로 모델링하라.
