# 이펙티브 타입스크립트 2판 (Effective TypeScript, 2nd Edition)

> Dan Vanderkam, *Effective TypeScript: 83 Specific Ways to Improve Your TypeScript* (2nd Edition), O'Reilly, 2024<br>1판 한국어판: "이펙티브 타입스크립트" (장원호 옮김, 인사이트, 2021) - 본 노트는 **원서 2판(영어)** 기반

타입스크립트를 "아는" 단계에서 "잘 쓰는" 단계로 끌어올리는 Effective 시리즈 스타일의 실전 지침서. 83개의 독립적인 아이템(Item)이 각각 하나의 구체적인 조언을 담고, 아이템마다 "Things to Remember"로 마무리된다. 2판은 조건부 타입·템플릿 리터럴 타입 등 최근 5년의 언어 발전을 반영해 제네릭과 타입 수준 프로그래밍에 챕터 하나(Ch6)를 통째로 할애했다.

## 책 정보

| 항목 | 내용 |
|------|------|
| 저자 | 댄 밴더캄(Dan Vanderkam) |
| 원서 | *Effective TypeScript, 2nd Edition* (O'Reilly, 2024-05) |
| 초판 | 2019-11 (1판 한국어판: 인사이트, 2021, 장원호 옮김) |
| 원본 | 영어 원서 2판 (origin.md) |
| 대상 독자 | JS/TS 실무 경험이 있는 초중급~중급 개발자 ("표준 두 번째 책") |

## 개요

이 책의 목표는 타입스크립트나 자바스크립트를 가르치는 것이 아니라, **초중급 사용자를 전문가로 끌어올리는 것**이다. 타입스크립트와 그 생태계가 어떻게 동작하는지에 대한 멘털 모델을 세우고, 피해야 할 함정을 알려 주고, 언어의 여러 기능을 언제 어떻게 써야 하는지 안내한다.

Effective 시리즈(Effective C++ 등)의 전통을 따라 **각 아이템은 독립적으로 읽을 수 있는 짧은 에세이**이며, 아이템 사이의 상호 참조가 촘촘하다. 이 노트도 책의 구조를 따라 **아이템 단위로 파일을 나눈다** - 챕터는 아이템을 주제별로 묶는 그룹 역할만 하므로, 챕터 개요는 아래 목차의 그룹 서두에 담는다.

## 목차

### Chapter 1: Getting to Know TypeScript (Item 1~5)

언어의 큰 그림 - 타입스크립트와 자바스크립트의 관계, 설정에 따라 달라지는 언어의 성격, 코드 생성과 타입의 독립(타입 소거), 구조적 타이핑, `any`의 위험. 이미 타입스크립트를 많이 써 봤어도 멘털 모델을 바로잡기 위해 읽을 가치가 있는 장이다.

| Item | 제목 | 핵심 단어 | 한 줄 요약 |
|------|------|-----------|-----------|
| 1 | [타입스크립트와 자바스크립트의 관계 이해하기](notes/item01-relationship-between-typescript-and-javascript.md) | 슈퍼셋, 타입 체커, 정적 타입, 건전성 | TS는 JS의 문법적 슈퍼셋 - 타입 체커는 런타임 예외를 예측하려 하지만 보장하지는 않는다 |
| 2 | [어떤 타입스크립트 설정을 사용하는지 알기](notes/item02-know-which-typescript-options-youre-using.md) | tsconfig, noImplicitAny, strictNullChecks, strict | 설정이 언어의 성격을 바꾼다 - noImplicitAny → strictNullChecks → strict 순으로 켜라 |
| 3 | [코드 생성과 타입은 독립적임을 이해하기](notes/item03-code-generation-is-independent-of-types.md) | 코드 생성, 타입 소거, 태그된 유니온, 타입 단언, 오버로딩 | 타입은 컴파일 시 지워진다 - 런타임 체크, 값 변환, 성능 어디에도 관여할 수 없다 |
| 4 | [구조적 타이핑에 익숙해지기](notes/item04-get-comfortable-with-structural-typing.md) | 구조적 타이핑, 덕 타이핑, 열린 타입, 테스트 더블 | 타입 호환은 이름이 아니라 구조로 판정된다 - 타입은 봉인되어 있지 않다 |
| 5 | [any 타입 사용 제한하기](notes/item05-limit-use-of-the-any-type.md) | any, 타입 안전성, 언어 서비스, 리팩터링 | any는 타입 체커와 언어 서비스를 끄는 스위치 - 여섯 가지 비용을 알고 피하라 |

### Chapter 2: TypeScript's Type System (Item 6~17)

타입 시스템의 기본기 - 타입을 값의 집합으로 이해하는 관점, 타입 공간과 값 공간의 구분, 편집기 활용, 타입 단언·잉여 속성 체크·`type` vs `interface`·`readonly`·제네릭 타입 연산 등 일상적으로 쓰는 도구들.

| Item | 제목 | 핵심 단어 | 한 줄 요약 |
|------|------|-----------|-----------|
| 6 | [편집기를 사용하여 타입 시스템 탐색하기](notes/item06-use-your-editor-to-interrogate-and-explore-the-type-system.md) | tsserver, 언어 서비스, 추론 확인, Go to Definition | 편집기는 타입 시스템의 실험실 - 추론, 에러, 리팩터링, 타입 선언 탐색을 익혀라 |
| 7 | [타입을 값들의 집합으로 생각하기](notes/item07-think-of-types-as-sets-of-values.md) | 도메인, never, 리터럴 타입, 유니온, 할당 가능성 | assignable, extends, 서브타입은 전부 "부분집합" - 타입 연산은 값의 집합에 적용된다 |
| 8 | [심벌이 타입 공간에 있는지 값 공간에 있는지 구별하기](notes/item08-symbol-in-type-space-or-value-space.md) | 타입 공간, 값 공간, typeof 이중성, class=타입+값 | 같은 이름이 타입과 값을 오간다 - 컴파일 후 사라지면 타입, 남으면 값 |
| 9 | [타입 단언보다 타입 선언 사용하기](notes/item09-prefer-type-annotations-to-type-assertions.md) | 타입 선언, 타입 단언, 널 아님 단언, unknown 경유 | 선언은 검사하고 단언은 침묵시킨다 - 단언은 더 잘 알 때만, 근거 주석과 함께 |
| 10 | [객체 래퍼 타입 피하기](notes/item10-avoid-object-wrapper-types.md) | 원시 타입, 객체 래퍼, String vs string | 래퍼는 원시 값에 메서드를 주기 위한 장치일 뿐 - 항상 소문자 원시 타입을 써라 |
| 11 | [잉여 속성 체크와 타입 체크 구분하기](notes/item11-distinguish-excess-property-checking-from-type-checking.md) | 잉여 속성 체크, 신선도, 약한 타입, 중간 변수 | 객체 리터럴에만 적용되는 오타 방지 장치 - 구조적 할당 검사와 혼동하지 말 것 |
| 12 | [가능하면 함수 표현식 전체에 타입 적용하기](notes/item12-apply-types-to-entire-function-expressions.md) | 함수 표현식, 함수 타입, typeof fn, Parameters | 시그니처 반복은 함수 타입으로 - typeof fn으로 다른 함수와 시그니처를 맞춘다 |
| 13 | [type과 interface의 차이 알기](notes/item13-know-the-differences-between-type-and-interface.md) | type vs interface, 유니온 타입, 선언 병합, 타입 인라인 | 가능하면 interface, 필요하면 type - 유니온은 type만, 병합은 interface만 |
| 14 | [readonly를 사용해 변경으로 인한 오류 방지하기](notes/item14-use-readonly-to-avoid-errors-associated-with-mutation.md) | readonly, Readonly, ReadonlyArray, 얕은 적용 | 변경하지 않는 매개변수는 readonly로 - 계약이 명확해지고 실수가 잡힌다 |
| 15 | [타입 연산과 제네릭 타입으로 반복 줄이기](notes/item15-use-type-operations-and-generic-types-to-avoid-repeating-yourself.md) | DRY, keyof, 매핑된 타입, Pick, Partial, ReturnType | 타입에도 DRY - 인덱싱, 매핑된 타입, 제네릭으로 타입 간 매핑하라 |
| 16 | [인덱스 시그니처보다 더 정확한 대안 사용하기](notes/item16-prefer-more-precise-alternatives-to-index-signatures.md) | 인덱스 시그니처, Map, Record, 동적 데이터 | 인덱스 시그니처는 any처럼 안전성을 갉아먹는다 - 인터페이스, Map, Record를 먼저 |
| 17 | [숫자 인덱스 시그니처 피하기](notes/item17-avoid-numeric-index-signatures.md) | 숫자 인덱스, ArrayLike, Object.keys | 숫자 키는 유용한 허구 - 필요하면 Array, 튜플, ArrayLike를 써라 |

### Chapter 3: Type Inference and Control Flow Analysis (Item 18~28)

어디까지 추론에 맡기고 어디에 타입을 명시할지 - 넓히기(widening)·좁히기(narrowing)·별칭·문맥·evolving type 등 타입스크립트가 코드를 따라가며 타입을 결정하는 방식(제어 흐름 분석)을 이해한다.

| Item | 제목 | 핵심 단어 | 한 줄 요약 |
|------|------|-----------|-----------|
| 18 | [추론 가능한 타입으로 코드를 어지럽히지 않기](notes/item18-avoid-cluttering-your-code-with-inferable-types.md) | 타입 추론, 시그니처만 명시, 반환 타입 | 시그니처에는 타입을, 지역 변수에는 추론을 - 반환 타입은 다중 return, 공개 API에서 명시 |
| 19 | [다른 타입에는 다른 변수 사용하기](notes/item19-use-different-variables-for-different-types.md) | 변수 재사용, 유니온 회피, const 선호 | 값은 바뀌어도 타입은 안 바뀐다 - 다른 개념에는 다른 변수 |
| 20 | [변수가 타입을 얻는 방식 이해하기](notes/item20-understand-how-a-variable-gets-its-type.md) | 넓히기, const, as const, satisfies | 리터럴에서 타입을 결정하는 넓히기, 그리고 그것을 통제하는 도구들 |
| 21 | [객체를 한 번에 만들기](notes/item21-create-objects-all-at-once.md) | 객체 스프레드, 조건부 속성 | 조각조각 만들면 타입이 못 따라온다 - 스프레드로 한 번에 |
| 22 | [타입 좁히기 이해하기](notes/item22-understand-type-narrowing.md) | 좁히기, 제어 흐름 분석, 태그된 유니온, 타입 가드 | 심벌은 위치마다 타입을 갖는다 - 좁히는 법과 좁혀지지 않는 경우 |
| 23 | [별칭을 일관되게 사용하기](notes/item23-be-consistent-in-your-use-of-aliases.md) | 별칭, 제어 흐름 분석, 구조 분해 | 별칭을 만들었으면 체크도 사용도 별칭으로 - 속성보다 지역 변수를 신뢰 |
| 24 | [타입 추론에 문맥이 어떻게 쓰이는지 이해하기](notes/item24-understand-how-context-is-used-in-type-inference.md) | 문맥 추론, 리터럴 유니온, 튜플, 콜백 | 값을 문맥에서 분리하면 추론이 달라진다 - 구문, as const, 인라인으로 해결 |
| 25 | [진화하는 타입 이해하기](notes/item25-understand-evolving-types.md) | evolving any, 빈 배열, null 초기화 | [], null로 시작한 변수만은 타입이 자란다 - 쓸 때만 any |
| 26 | [함수형 구문과 라이브러리로 타입 흐름 돕기](notes/item26-use-functional-constructs-and-libraries-to-help-types-flow.md) | 함수형 구문, Lodash, flat, 체인 | 변경 없는 호출 연쇄는 타입도 새로 만든다 - 루프 대신 map, flat, 체인 |
| 27 | [콜백 대신 async 함수로 타입 흐름 개선하기](notes/item27-use-async-functions-instead-of-callbacks.md) | async/await, 프로미스, Promise.all, 동기/비동기 일관성 | async는 항상 프로미스를 반환하도록 강제한다 - 반쯤 동기인 코드를 원천 봉쇄 |
| 28 | [클래스와 커링으로 새 추론 지점 만들기](notes/item28-use-classes-and-currying-to-create-new-inference-sites.md) | 부분 추론, 클래스 바인딩, 커링, 지역 타입 별칭 | 추론은 전부 아니면 전무 - 명시할 자리와 추론할 자리를 분리하라 |

### Chapter 4: Type Design (Item 29~42)

이 책의 중심 챕터 - 유효한 상태만 표현하는 타입을 설계하는 법. null 다루기, 인터페이스의 유니온, string 남용 지양, 특수 값, 옵셔널 속성 제한, 정밀도와 정확도의 트레이드오프, 도메인 언어로 네이밍.

| Item | 제목 | 핵심 단어 | 한 줄 요약 |
|------|------|-----------|-----------|
| 29 | [항상 유효한 상태만 표현하는 타입 선호하기](notes/item29-prefer-types-that-always-represent-valid-states.md) | 유효 상태, 태그된 유니온, 에어프랑스 447 | 무효한 상태를 허용하는 타입은 구현 불가능한 함수를 낳는다 |
| 30 | [받을 때는 너그럽게, 내놓을 때는 엄격하게](notes/item30-be-liberal-in-what-you-accept-and-strict-in-what-you-produce.md) | 포스텔의 법칙, 정준 형태, Iterable | 넓은 매개변수는 편의, 넓은 반환은 고통 - 정준/느슨한 형태를 구분하라 |
| 31 | [문서에 타입 정보를 반복하지 않기](notes/item31-dont-repeat-type-information-in-documentation.md) | 주석, readonly, 단위 네이밍 | 강제되지 않는 약속은 어긋난다 - 타입은 구문에, 계약은 readonly로 |
| 32 | [타입 별칭에 null이나 undefined 포함하지 않기](notes/item32-avoid-including-null-or-undefined-in-type-aliases.md) | 타입 별칭, nullable | User가 null일 수도 있다면 독자가 배신당한다 - User \| null로 명시하라 |
| 33 | [null 값을 타입의 가장자리로 밀어내기](notes/item33-push-null-values-to-the-perimeter-of-your-types.md) | null 배치, extent, 완전 non-null 클래스 | 값들은 전부 null이거나 전부 non-null이게 - 암묵적 null 관계를 없애라 |
| 34 | [유니온의 인터페이스보다 인터페이스의 유니온 선호하기](notes/item34-prefer-unions-of-interfaces-to-interfaces-with-unions.md) | 인터페이스 유니온, 태그된 유니온, 속성 묶기 | 유니온 속성들은 어긋난 조합을 허용한다 - 관계를 타입으로 표현하라 |
| 35 | [string 타입보다 더 정밀한 대안 선호하기](notes/item35-prefer-more-precise-alternatives-to-string-types.md) | stringly typed, 리터럴 유니온, keyof | string의 도메인은 모비 딕 전문까지 포함한다 - 리터럴 유니온과 keyof로 좁혀라 |
| 36 | [특수 값에는 구별되는 타입 사용하기](notes/item36-use-a-distinct-type-for-special-values.md) | indexOf -1, 특수 값, null 반환 | 일반 값과 같은 타입인 특수 값(-1, 0, "")은 타입 체커를 무력화한다 |
| 37 | [옵셔널 속성 사용 제한하기](notes/item37-limit-the-use-of-optional-properties.md) | 옵셔널 속성, 기본값, 정규화 타입 분리, 조합 폭발 | 편의로 붙인 ?가 버그를 연다 - 필수화 또는 입력/정규화 타입 분리를 고려 |
| 38 | [같은 타입의 매개변수 반복 피하기](notes/item38-avoid-repeated-parameters-of-the-same-type.md) | 위치 매개변수, 객체 매개변수 | 연속된 같은 타입 매개변수는 순서 실수를 못 잡는다 - 구별 타입이나 객체로 |
| 39 | [차이를 모델링하기보다 타입 통합을 선호하기](notes/item39-prefer-unifying-types-to-modeling-differences.md) | 타입 통합, snake_case/camelCase, 변환 코드 | 두 벌의 타입은 인지 부담과 변환 버그 - 가능하면 차이 자체를 없애라 |
| 40 | [부정확한 타입보다 덜 정밀한 타입 선호하기](notes/item40-prefer-imprecise-types-to-inaccurate-types.md) | 정밀도 vs 정확도, 불쾌한 골짜기, 타입 테스트 | 정확히 모델링 못 하겠다면 부정확하게 모델링하지 마라 - any로 빈틈을 인정 |
| 41 | [문제 도메인의 언어로 타입 이름 짓기](notes/item41-name-types-using-the-language-of-your-problem-domain.md) | 네이밍, 도메인 어휘, 모호한 이름 | 도메인의 표준 어휘를 재사용하라 - Info, Entity 같은 이름은 결국 발목을 잡는다 |
| 42 | [일화적 데이터에 기반한 타입 피하기](notes/item42-avoid-types-based-on-anecdotal-data.md) | 명세 기반 타입, DefinitelyTyped, OpenAPI, 코드 생성 | 내가 본 데이터만으로 쓴 타입은 엣지 케이스를 놓친다 - 명세에서 얻거나 생성하라 |

### Chapter 5: Unsoundness and the any Type (Item 43~49)

`any`를 쓰더라도 피해 반경을 줄이는 법 - 좁은 스코프, `any`의 정밀한 변종, 잘 타이핑된 함수 뒤에 숨기기, `unknown`, 그리고 타입 시스템의 불건전성이 발생하는 지점들.

| Item | 제목 | 핵심 단어 | 한 줄 요약 |
|------|------|-----------|-----------|
| 43 | [any 타입은 가능한 한 좁은 스코프로 사용하기](notes/item43-use-the-narrowest-possible-scope-for-any-types.md) | any 스코프, 전염성, @ts-expect-error | any는 표현식 하나에만 - 반환하면 코드베이스 전체로 전염된다 |
| 44 | [그냥 any보다 더 정밀한 any 변종 선호하기](notes/item44-prefer-more-precise-variants-of-any-to-plain-any.md) | any[], Record<string, any>, 함수 시그니처 | 배열인 건 안다면 any[] - 본문 검사, 반환 추론, 호출 검사를 되찾는다 |
| 45 | [안전하지 않은 타입 단언은 잘 타이핑된 함수 안에 숨기기](notes/item45-hide-unsafe-type-assertions-in-well-typed-functions.md) | 단언 은닉, 시그니처 우선, 오버로드 | 시그니처는 공개 API, 구현은 세부 사항 - 단언은 구현 안에, 테스트와 함께 |
| 46 | [타입을 모르는 값에는 any 대신 unknown 사용하기](notes/item46-use-unknown-instead-of-any-for-values-with-an-unknown-type.md) | unknown, 탑 타입, 좁히기 강제, {} vs object | any는 타입 시스템 밖의 존재 - unknown은 같은 역할을 시스템 안에서 한다 |
| 47 | [몽키 패치에는 타입 안전한 접근 선호하기](notes/item47-prefer-type-safe-approaches-to-monkey-patching.md) | 몽키 패치, declare global, 인터페이스 보강, 커스텀 타입 단언 | window, DOM에 붙여야 한다면 보강이나 커스텀 타입으로 - as any는 금물 |
| 48 | [건전성 함정 피하기](notes/item48-avoid-soundness-traps.md) | 건전성, 배열 조회, 이변성, 가변성, 정제 무효화 | any를 없애도 남는 불건전의 원천들 - 공통 해독제는 매개변수를 변경하지 않기 |
| 49 | [타입 커버리지를 추적해 타입 안전성의 퇴행 방지하기](notes/item49-track-your-type-coverage-to-prevent-regressions-in-type-safety.md) | type-coverage, 서드파티 any, CI 추적 | noImplicitAny로도 any는 스며든다 - 수치로 추적하고 재검토하라 |

### Chapter 6: Generics and Type-Level Programming (Item 50~58)

2판에서 통째로 신설된 챕터 - 제네릭을 "타입 간 함수"로 보는 관점, 조건부 타입, 유니온 분배 제어, 템플릿 리터럴 타입, 타입 테스트, 꼬리 재귀 제네릭, 그리고 복잡한 타입의 대안으로서의 코드 생성.

| Item | 제목 | 핵심 단어 | 한 줄 요약 |
|------|------|-----------|-----------|
| 50 | [제네릭을 타입 간 함수로 생각하기](notes/item50-think-of-generics-as-functions-between-types.md) | 제네릭, extends 제약, @template, 제네릭 함수/클래스 | 제네릭은 타입의 함수 - 제약은 매개변수 타입, 이름과 문서도 함수처럼 |
| 51 | [불필요한 타입 매개변수 피하기](notes/item51-avoid-unnecessary-type-parameters.md) | 황금률, 반환 전용 제네릭, unknown 대체 | 타입 매개변수는 두 번 나타나야 한다 - 제네릭의 첫 규칙은 "쓰지 마라" |
| 52 | [오버로드 시그니처보다 조건부 타입 선호하기](notes/item52-prefer-conditional-types-to-overload-signatures.md) | 조건부 타입, 유니온 분배, 단일 오버로드 구현 | 오버로드는 하나씩, 조건부 타입은 유니온 위로 분배되는 한 표현식 |
| 53 | [조건부 타입에서 유니온의 분배 통제하는 법 알기](notes/item53-know-how-to-control-the-distribution-of-unions-over-conditional-types.md) | 분배, [T] 튜플 감싸기, boolean/never 분배 | 분배는 조건이 순수 T일 때만 - 튜플로 끄고, 형식 조건으로 켠다 |
| 54 | [템플릿 리터럴 타입으로 DSL과 문자열 간 관계 모델링하기](notes/item54-use-template-literal-types-to-model-dsls.md) | 템플릿 리터럴 타입, infer, 재귀, querySelector | 유한 유니온과 무한 string 사이 - 패턴 있는 문자열 집합을 타입으로 |
| 55 | [타입에 대한 테스트 작성하기](notes/item55-write-tests-for-your-types.md) | 타입 테스트, 할당 가능성 vs 동등성, expect-type, dtslint | 할당 테스트는 함수 타입, any에서 배신한다 - 표준 도구로 동등성을 검사하라 |
| 56 | [타입이 표시되는 방식에 주의 기울이기](notes/item56-pay-attention-to-how-types-display.md) | 타입 표시, Resolve/Simplify, 특수 케이스 | 같은 타입도 표시는 여럿 - Resolve로 구현 냄새를 지우고 표시를 테스트하라 |
| 57 | [꼬리 재귀 제네릭 타입 선호하기](notes/item57-prefer-tail-recursive-generic-types.md) | 꼬리 재귀, 누산기, 재귀 깊이 한도 | 재귀 뒤에 일하면 ~50에서 터진다 - 누산기로 꼬리 위치로 옮겨라 |
| 58 | [복잡한 타입의 대안으로 코드 생성 고려하기](notes/item58-consider-codegen-as-an-alternative-to-complex-types.md) | codegen, PgTyped, 튜링 타르 구덩이, CI 동기화 | 타입 시스템으로 SQL 파서를 만들기 전에 - 평범한 언어로 타입을 생성하라 |

### Chapter 7: TypeScript Recipes (Item 59~64)

자주 마주치는 문제에 대한 검증된 레시피 - `never`를 이용한 소진(exhaustiveness) 체크, 객체 순회, `Record`로 값 동기화, 나머지 매개변수와 튜플, 옵셔널 `never`로 배타적 OR 모델링, 브랜드로 명목적 타이핑.

| Item | 제목 | 핵심 단어 | 한 줄 요약 |
|------|------|-----------|-----------|
| 59 | [never 타입으로 소진 체크 수행하기](notes/item59-use-never-types-to-perform-exhaustiveness-checking.md) | 소진 체크, assertUnreachable, never, 교차곱 | 빠진 switch 케이스를 타입 에러로 - 누락의 오류도 잡아라 |
| 60 | [객체 순회하는 법 알기](notes/item60-know-how-to-iterate-over-objects.md) | for-in, Object.entries, keyof 단언, Map | 매개변수 객체엔 추가 키가 있을 수 있다 - 상황별 올바른 순회법을 골라라 |
| 61 | [Record 타입으로 값들을 동기화하기](notes/item61-use-record-types-to-keep-values-in-sync.md) | Record, fail open/closed, 동기화 강제 | 새 속성 추가 시 결정을 강제한다 - fail open도 closed도 아닌 "그냥 fail" |
| 62 | [나머지 매개변수와 튜플 타입으로 가변 인수 함수 모델링하기](notes/item62-use-rest-parameters-and-tuple-types-to-model-variadic-functions.md) | 나머지 매개변수, 튜플 레이블, 조건부 타입 | 타입에 따라 인수 개수가 달라지는 함수 - ...args에 조건부 튜플을 |
| 63 | [옵셔널 never 속성으로 배타적 OR 모델링하기](notes/item63-use-optional-never-properties-to-model-exclusive-or.md) | 배타적 OR, 옵셔널 never, XOR 헬퍼 | 타입의 \|는 포괄적 OR - "둘 다"를 막으려면 ?: never로 속성을 금지하라 |
| 64 | [명목적 타이핑을 위한 브랜드 고려하기](notes/item64-consider-brands-for-nominal-typing.md) | 브랜드, 명목적 타이핑, unique symbol, SortedList | 구조가 같아도 의미가 다르면 브랜드로 - 받거나, 증명하거나 |

### Chapter 8: Type Declarations and @types (Item 65~71)

타입 선언과 의존성 관리 - `@types`를 devDependencies에, 타입 선언에 얽힌 세 가지 버전, 공개 API 타입 export, TSDoc, 콜백의 `this`, 미러링으로 의존성 끊기, 모듈 보강.

| Item | 제목 | 핵심 단어 | 한 줄 요약 |
|------|------|-----------|-----------|
| 65 | [TypeScript와 @types를 devDependencies에 두기](notes/item65-put-typescript-and-types-in-devdependencies.md) | devDependencies, @types, npx tsc | 타입은 런타임에 없다 - TypeScript도 @types도 dev 의존성으로 |
| 66 | [타입 선언에 얽힌 세 가지 버전 이해하기](notes/item66-understand-the-three-versions-involved-in-type-declarations.md) | 세 가지 버전, 버전 불일치, 번들 vs DefinitelyTyped | 라이브러리, @types, TS 버전이 어긋나는 네 가지 방식과 그 증상들 |
| 67 | [공개 API에 등장하는 모든 타입 export하기](notes/item67-export-all-types-that-appear-in-public-apis.md) | 타입 export, Parameters, ReturnType | 공개 API에 넣는 순간 이미 export된 것 - 사용자가 어차피 추출한다 |
| 68 | [API 주석에 TSDoc 사용하기](notes/item68-use-tsdoc-for-api-comments.md) | TSDoc, @param, @deprecated, 마크다운 | JSDoc 형식만 툴팁에 뜬다 - 공개 API 주석은 TSDoc으로 |
| 69 | [콜백에서 this가 API의 일부라면 타입 제공하기](notes/item69-provide-a-type-for-this-in-callbacks.md) | this 바인딩, this 매개변수, 화살표 함수 | this를 설정한다면 그것은 API다 - this 매개변수로 모델링하라 |
| 70 | [타입을 미러링해 의존성 끊기](notes/item70-mirror-types-to-sever-dependencies.md) | 타입 미러링, 구조적 타이핑, 이행적 의존성 | 필요한 메서드만 담은 타입을 직접 써서 @types/node 의존을 끊어라 |
| 71 | [모듈 보강으로 타입 개선하기](notes/item71-use-module-augmentation-to-improve-types.md) | 선언 병합, JSON.parse, knock out, ts-reset | any를 반환하는 역사적 유산을 내 프로젝트에서 unknown으로 고쳐라 |

### Chapter 9: Writing and Running Your Code (Item 72~78)

타입 밖에서 만나는 실행 문제들 - 타입스크립트 고유 기능(enum 등)보다 ECMAScript 기능 우선, 소스맵 디버깅, 런타임 타입 재구성, DOM 계층, 실행 환경의 정확한 모델링, 타입 체크와 유닛 테스트의 관계, 컴파일러 성능.

| Item | 제목 | 핵심 단어 | 한 줄 요약 |
|------|------|-----------|-----------|
| 72 | [타입스크립트 기능보다 ECMAScript 기능 선호하기](notes/item72-prefer-ecmascript-features-to-typescript-features.md) | enum 지양, 매개변수 프로퍼티, namespace, #private | TC39가 런타임을, TS는 타입 공간만 - 역사적 예외 기능들을 피하라 |
| 73 | [소스맵으로 타입스크립트 디버깅하기](notes/item73-use-source-maps-to-debug-typescript.md) | 소스맵, sourceMap 옵션, Node 디버깅, declarationMap | 생성된 JS를 디버깅하지 마라 - 소스맵으로 원본 TS에서 중단점을 |
| 74 | [런타임에 타입 재구성하는 법 알기](notes/item74-know-how-to-reconstruct-types-at-runtime.md) | 런타임 검증, Zod, typescript-json-schema, 단일 진실 공급원 | 타입과 검증 로직의 중복을 없애는 세 가지 길 - 스키마, Zod, 타입에서 생성 |
| 75 | [DOM 계층 이해하기](notes/item75-understand-the-dom-hierarchy.md) | EventTarget, Node, Element, HTMLElement, MouseEvent | DOM 코드의 에러 폭탄은 계층을 알면 풀린다 - 구체적 타입 또는 문맥을 |
| 76 | [실행 환경의 정확한 모델 만들기](notes/item76-create-an-accurate-model-of-your-environment.md) | lib 설정, 전역 모델링, @types 버전, 특수 import | 환경 모델이 정확할수록 타입스크립트가 오류를 잘 찾는다 |
| 77 | [타입 체크와 유닛 테스트의 관계 이해하기](notes/item77-understand-the-relationship-between-type-checking-and-unit-testing.md) | 정확성 하한/상한, 무효 입력, @ts-expect-error 테스트 | 테스트는 하한, 타입은 상한 - 양쪽에서 버그를 깎아 낸다 |
| 78 | [컴파일러 성능에 주의 기울이기](notes/item78-pay-attention-to-compiler-performance.md) | tsc vs tsserver, transpile only, 트리맵, 프로젝트 레퍼런스, 거대 유니온 | 빌드와 편집기의 성능 문제를 구분하고 각각에 맞게 최적화하라 |

### Chapter 10: Modernization and Migration (Item 79~83)

레거시 자바스크립트를 점진적으로 타입스크립트로 - 모던 JS로 먼저 전환, `@ts-check`와 JSDoc으로 실험, `allowJs`로 혼용, 의존성 그래프를 따라 모듈 단위 전환, `noImplicitAny`를 켜야 마이그레이션 완료.

| Item | 제목 | 핵심 단어 | 한 줄 요약 |
|------|------|-----------|-----------|
| 79 | [모던 자바스크립트 작성하기](notes/item79-write-modern-javascript.md) | ES 모듈, 클래스, 모던 JS 기능 | JS 현대화가 TS 마이그레이션의 첫걸음 - ES 모듈과 클래스부터 |
| 80 | [@ts-check와 JSDoc으로 타입스크립트 실험하기](notes/item80-use-ts-check-and-jsdoc-to-experiment-with-typescript.md) | @ts-check, JSDoc 단언, 전역 선언 | .ts로 바꾸기 전에 문제를 미리 가늠하라 - 단, 목표는 .ts임을 잊지 말 것 |
| 81 | [allowJs로 타입스크립트와 자바스크립트 혼용하기](notes/item81-use-allowjs-to-mix-typescript-and-javascript.md) | allowJs, ts-loader, ts-jest, outDir | 코드 변경 전에 빌드, 테스트 체인부터 타입스크립트와 함께 돌게 하라 |
| 82 | [의존성 그래프를 따라 모듈 단위로 위로 변환하기](notes/item82-convert-module-by-module-up-your-dependency-graph.md) | 의존성 그래프, @types 먼저, 리팩터링 금지, 테스트 마지막 | 잎에서 뿌리로 - 타입 추가에 집중하고 리팩터링 충동은 참아라 |
| 83 | [noImplicitAny를 켜기 전에는 마이그레이션이 끝난 것이 아니다](notes/item83-dont-consider-migration-complete-until-you-enable-noimplicitany.md) | noImplicitAny, 점진적 강화, strict | 느슨한 체크는 타입 선언의 실수를 가린다 - 켜야 끝난 것이다 |

## 학습 가이드

아이템 간 상호 참조가 대체로 앞 아이템 → 뒤 아이템으로 이어지므로 **순서대로 읽는 것이 기본**이다. 시간이 없다면 아래 경로를 추천한다.

1. **필수 기반**: Ch1 전체(1~5) → 7(타입=집합) → 9(선언 vs 단언) → 11(잉여 속성 체크) - 이후 모든 아이템이 이 개념들을 전제한다
2. **일상 코딩의 반환점**: 18(구문 최소화) · 20(넓히기) · 22(좁히기) · 24(문맥) - 편집기에서 매일 마주치는 추론 동작
3. **설계 감각**: 29(유효 상태) · 33(null 가장자리) · 34(인터페이스 유니온) · 35(string 좁히기) - Ch4의 중심 아이템들
4. **any와의 공존**: 43(스코프) → 46(unknown) → 45(단언 은닉) - any를 쓰게 될 때의 생존 지침

**주제별 역인덱스**

- 라이브러리를 만들거나 타입을 공개한다면: Ch8 전체(65~71) + 30(넓게 받고 좁게 내놓기) + 55(타입 테스트)
- 타입 수준 프로그래밍이 궁금하다면: Ch6 전체(50~58) - 단 51(첫 규칙은 "쓰지 마라")부터
- JS 코드베이스를 전환해야 한다면: Ch10 전체(79~83) + 80 이전에 2(설정)와 5(any)
- 브라우저 코드를 쓴다면: 75(DOM 계층) + 54(querySelector 정밀화) + 76(환경 모델)
- 런타임 검증이 필요하다면: 74(Zod·JSON Schema) + 42(명세 기반 타입) + 45(단언 은닉)

## 핵심 개념 맵

- **"타입 = 값의 집합"(Item 7)이 책 전체를 꿰는 렌즈다**: 할당 가능성·extends·서브타입은 전부 "부분집합"이고, 좁히기(22)·유니온 분배(53)·never(59)·unknown(46)이 모두 집합 연산으로 설명된다
- **코드 생성과 타입의 독립(Item 3)에서 많은 것이 따라 나온다**: 타입 소거 → 런타임 타입 재구성(74)·태그된 유니온(34)·소스맵 디버깅(73), 그리고 "타입은 제로 코스트"(78)
- **구조적 타이핑(Item 4)은 양날의 검이다**: 테스트 더블(4)과 타입 미러링(70)을 가능케 하지만, 잉여 속성 체크(11)·옵셔널 never(63)·브랜드(64)는 그 개방성을 다스리는 장치들이다
- **any의 위험(Item 5)과 완화의 사다리**: 스코프 좁히기(43) → 정밀한 변종(44) → unknown(46) → 잘 타이핑된 함수에 은닉(45) → 커버리지 추적(49)
- **타입 설계의 대원칙은 "유효한 상태만 표현"(Item 29)**: 태그된 유니온(34)·null 가장자리로 밀기(33)·특수 값 분리(36)·옵셔널 제한(37)이 그 구체적 실천이다
- **제네릭은 타입 간 함수(Item 50)**: 황금률(51)·조건부 타입(52·53)·템플릿 리터럴(54)로 정교해지고, 테스트(55)·표시(56)·성능(57)까지 관리하되, 과해지면 codegen(58)이 출구다
- **마이그레이션은 경로가 정해져 있다**: 모던 JS(79) → @ts-check 실험(80) → allowJs 공존(81) → 의존성 그래프 위로(82) → noImplicitAny(83)

## 인용문

> Show me your flowcharts and conceal your tables, and I shall continue to be mystified. Show me your tables, and I won't usually need your flowcharts; they'll be obvious.<br>순서도를 보여 주고 테이블을 감추면 나는 계속 어리둥절할 것이다. 테이블을 보여 달라. 그러면 순서도는 대개 필요 없을 것이다 - 자명할 테니까.<br>- 프레드 브룩스(Fred Brooks), "맨먼스 미신" (위치: Ch4 서두)

> TCP 구현은 일반적 견고성 원칙을 따라야 한다: 자신이 하는 일에는 보수적으로, 남에게서 받는 것에는 너그럽게.<br>- 존 포스텔(Jon Postel), 포스텔의 법칙 (위치: Item 30)

> 컴퓨터 과학에는 어려운 문제가 딱 둘 있다: 캐시 무효화, 그리고 이름 짓기.<br>- 필 칼튼(Phil Karlton) (위치: Item 41)

> 중복은 잘못된 추상화보다 훨씬 싸다.<br>- 샌디 메츠(Sandi Metz) (위치: Item 15)

> 인터페이스는 올바르게 쓰기는 쉽고 잘못 쓰기는 어렵게 만들어라.<br>- 스콧 마이어스(Scott Meyers), "Effective C++" (위치: Item 38)

> 두려움이 지루함으로 바뀔 때까지 테스트를 써라.<br>- Phlip, 켄트 벡 "테스트 주도 개발"에서 재인용 (위치: Item 55)

> 모든 것이 가능하지만 흥미로운 어떤 것도 쉽지 않은 튜링 타르 구덩이를 조심하라.<br>- 앨런 펄리스(Alan Perlis) (위치: Item 58)

> 약간의 복사가 약간의 의존성보다 낫다.<br>- Go 언어 커뮤니티 (위치: Item 70)

> 휴리스틱을 원한다면, type의 기능이 필요해질 때까지는 interface를 써라.<br>- 타입스크립트 공식 핸드북 (위치: Item 13)

> 제네릭의 첫 번째 규칙은 "쓰지 마라"다.<br>- 댄 밴더캄(Dan Vanderkam) (위치: Item 51)

> 정확하게 모델링할 수 없다면 부정확하게 모델링하지 마라. any나 unknown으로 빈틈을 인정하라.<br>- 댄 밴더캄(Dan Vanderkam) (위치: Item 40)

## 시그니처 요소와 표기 규칙

- **아이템 단위 파일**: 이 책은 아이템이 사실상 챕터 역할을 하는 구조라 노트를 `notes/item{NN}-{영문-kebab-case}.md`로 나눈다 (저장소 표준 `ch{NN}-*`의 예외). 챕터 개요는 README 목차의 챕터 그룹 서두에 담는다
- **노트 구성**: `# Item N: 한글 제목 (English Title)` → `## 핵심 질문` → 번호 섹션(`## 1.` …) → `## 기억해야 할 것들`
- **기억해야 할 것들**: 각 아이템 끝의 원서 시그니처 요약("Things to Remember")을 불릿 리스트로 수록 - 별도 `## 요약`은 두지 않는다(중복)
- **twoslash 코드 표기**: 원서 2판의 코드 주석 표기를 그대로 따른다 - `// ~~~ 에러 메시지`(타입 체커 에러), `// ^? 타입`(해당 심벌에 마우스를 올렸을 때 편집기가 보여 주는 타입). 에러 메시지는 컴파일러 출력이므로 영어 원문 유지
- **코드**: 원서가 이미 타입스크립트이므로 병기 없이 TS 단일 (OCR로 흐트러진 코드는 재구성)
- **콜아웃**: `> **핵심 통찰**:` · `> **실무 팁**:` · `> **참고**:` (원서의 note 박스는 `> **참고**:`로)
- **다이어그램**: 단순한 포함/집합 관계는 ASCII 그림 대신 집합 표기(⊂)·불릿으로 표현하고, ASCII 다이어그램은 구조가 그림 없이는 전달되지 않을 때만 쓴다
- **상호 참조**: 원서 표기 그대로 `Item N` / `Chapter N`으로 지칭

## Notion DB 구조

- **위치**: Develop → Raehan's Must reads → **이펙티브 타입스크립트 2판** 페이지 안의 인라인 DB **"아이템"**
- **속성**: `Done`(checkbox) / `Title` / `Part`(select - Ch1~Ch10 색상 딱지) / `Chapter`(number, 1~83) / `핵심 단어`(rich text, 쉼표 구분) / `핵심 요약`(rich text, 한 줄)
  - 이 책은 파트가 아니라 **챕터가 분류 기준**이라 `Part` 속성 값에 `Ch1`~`Ch10`을 넣는다 (아이템이 챕터 역할을 하므로 `Chapter` 번호는 1~83의 아이템 번호)
  - `핵심 단어`·`핵심 요약`의 값 소스는 이 README의 목차 표다
- **뷰**: `SHOW "Done", "Title", "Part", "핵심 단어", "핵심 요약"; SORT BY "Chapter" ASC` (제목에 번호가 있으므로 `Chapter` 열은 숨김)
- **본문**: 각 아이템 페이지 본문은 `notes/itemNN-*.md`에서 H1을 제거하고 콜아웃(`> **핵심 통찰**:` → 💡 / `> **실무 팁**:` → 🔧 / `> **참고**:` → 📌)과 마크다운 표를 `<table header-row="true">`로 변환해 업로드

## 작성 상태

- [x] `origin.md` 원본 투입 (17,105줄, 영어 원서 2판)
- [ ] `origin/` 챕터별 분리 (0~10, 11=부록(1판↔2판 아이템 매핑, 15581행~), 99=색인(15688행~) 예상)
- [x] 목차 확정 (원서 기준 10챕터·83아이템 - 원서 기반이므로 한국어판 제목 교정 해당 없음)
- [x] Item 1~83 노트 전체 (직접 순차 작성, `## 다른 챕터와의 관계` 섹션은 생략하기로 확정)
- [x] 마무리 체크리스트 (학습 가이드·핵심 개념 맵·인용문·KEYWORDS·QUOTES·루트 README·CLAUDE.md 상태 갱신)
- [x] Notion 업로드 (Item 1~83 본문 + 속성 전량, 메인 에이전트 순차 업로드)
