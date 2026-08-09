# Item 65: TypeScript와 @types를 devDependencies에 두기 (Put TypeScript and @types in devDependencies)

## 핵심 질문

TypeScript와 @types 패키지는 package.json의 어느 섹션에 속하며, 왜 그런가?

npm은 몇 가지 의존성 종류를 구분하며 각각 package.json의 별도 섹션에 들어간다.

- **dependencies**: 자바스크립트를 **실행하는 데** 필요한 패키지. 런타임에 lodash를 import한다면 여기다. npm에 코드를 공개하고 다른 사용자가 설치하면 이것들도 함께 설치된다(이행적 의존성).
- **devDependencies**: 개발·테스트에 쓰이지만 런타임에는 필요 없는 패키지. 테스트 프레임워크가 예다. dependencies와 달리 이행적으로 설치되지 않는다.
- **peerDependencies**: 런타임에 필요하지만 추적을 책임지고 싶지 않은 패키지. React 컴포넌트를 공개한다면 React 자체의 여러 버전과 호환될 텐데, 내가 골라 주기보다 사용자가 고르는 편이 낫다(안 그러면 같은 페이지에 React가 여러 버전 뜰 수 있다).

**타입스크립트는 개발 도구이고 타입스크립트 타입은 런타임에 존재하지 않으므로(Item 3), 타입스크립트 관련 패키지는 일반적으로 devDependencies에 속한다.**

## 1. TypeScript 자체 — 시스템 전역 설치 금지

타입스크립트를 시스템 전역에 설치할 수 있지만 나쁜 생각이다.

1. 나와 동료들이 항상 같은 버전을 설치했다는 보장이 없다.
2. 프로젝트 셋업에 단계가 하나 늘어난다.

대신 **devDependency로** 만들어라. `npm install`만 하면 모두가 올바른 버전을 받고, 다른 패키지처럼 업데이트한다. IDE와 빌드 도구는 이렇게 설치된 타입스크립트를 잘 찾아내며, 커맨드라인에서는 npx로 npm이 설치한 tsc를 실행할 수 있다.

```
$ npx tsc
```

## 2. @types — 구현이 직접 의존성이어도 타입은 dev

라이브러리 자체에 타입 선언이 없다면 DefinitelyTyped — 자바스크립트 라이브러리 타입 정의의 커뮤니티 유지 모음 — 에서 찾을 수 있다. 여기의 타입 정의는 npm 레지스트리의 `@types` 스코프로 공개된다: jQuery는 `@types/jquery`, Lodash는 `@types/lodash`. **@types 패키지는 타입만 담고 구현은 담지 않는다.**

**패키지 자체가 직접 의존성이더라도 @types는 devDependencies에 둬야 한다.**

```
$ npm install react
$ npm install --save-dev @types/react
```

```json
{
  "devDependencies": {
    "@types/react": "^18.2.23",
    "typescript": "^5.2.2"
  },
  "dependencies": {
    "react": "^18.2.0"
  }
}
```

발상은 이렇다 — **공개하는 것은 타입스크립트가 아니라 자바스크립트이고, 그 자바스크립트는 실행될 때 @types에 의존하지 않는다.** (타입스크립트 사용자들이 이 @types에 의존할 수는 있지만, 이행적 타입 의존성은 피하는 것이 좋다 — 방법은 Item 70.)

## 3. npm에 공개할 일 없는 웹 앱이라도

"그 경우엔 devDependencies 분리가 의미 없으니 다 prod 의존성으로 해도 된다"는 조언을 볼 수도 있다. 하지만 웹 앱이라도 @types를 devDependencies에 두면 이점이 있다.

1. **서버 컴포넌트가 있다면** `npm install --production`으로 프로덕션 이미지에 prod 의존성만 설치할 수 있다. 타입스크립트를 이미 자바스크립트로 컴파일했다면 코드 실행에 필요한 의존성은 그것뿐이다 — 더 날씬하고 빨리 뜨는 이미지가 된다.
2. **자동 의존성 업데이트 도구**(Renovate·Dependabot 등)에 프로덕션 의존성을 우선하라고 시킬 수 있다. 최종 사용자에게 영향을 줄 수 있는 중요한 보안 업데이트가 있을 가능성이 높은 쪽이 그쪽이니까.

@types 의존성에서 잘못될 수 있는 것들은 다음 아이템(Item 66)에서 더 깊이 판다.

## 기억해야 할 것들

- package.json의 dependencies와 devDependencies의 차이를 이해하라.
- TypeScript는 프로젝트의 devDependencies에 두라. 시스템 전역에 설치하지 마라.
- @types 의존성은 dependencies가 아니라 devDependencies에 두라.
