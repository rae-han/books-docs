# 사례 연구: 다른 소프트웨어 공학 서적에서 본 버전 마이그레이션 원칙

## 개요

이 문서는 TVING 웹 모노레포 버전 마이그레이션(WC-194) 작업에 적용된 원칙들을 "Working Effectively with Legacy Code" 외의 유명 소프트웨어 공학 서적에서 찾아 정리한 것이다.

마이그레이션 자체가 "레거시 코드를 다루는 일"이라기보다, **소프트웨어 설계와 변경에 관한 보편적 원칙**을 따르는 작업이라는 관점에서 정리했다.

---

## 깊은 관련: 핵심 원칙이 직접 적용된 서적

### Refactoring (Martin Fowler, 2nd Edition)

이 책은 코드의 외부 동작을 바꾸지 않으면서 내부 구조를 개선하는 체계적 기법을 다룬다.

**Strangler Fig Pattern (교살자 무화과 패턴)**

기존 시스템을 한 번에 교체하는 대신, 새로운 시스템을 점진적으로 성장시켜 기존 시스템을 서서히 대체하는 패턴이다. 열대 지방의 무화과가 숙주 나무를 감싸며 자라다가 결국 대체하는 것에서 이름을 따왔다.

이번 마이그레이션에서:
- 루트 `resolutions`로 React를 강제 통일하던 구조를 한 번에 제거하지 않았다
- 앱별 독립 관리를 먼저 도입하고, TV앱에서 React 19를 적용한 뒤, 다른 앱은 기존 버전을 유지했다
- PC Next.js 12를 한 번에 15로 올리지 않고, 보안 패치(12.3.7)만 적용하여 당장의 위험을 제거했다
- 궁극적으로 모든 앱이 최신 버전으로 이동하면 기존 구조는 자연스럽게 사라진다

**Two Hats (두 개의 모자)**

Fowler는 "리팩토링 모자"와 "기능 추가 모자"를 동시에 쓰지 말라고 강조한다. 한 번에 한 가지 종류의 작업만 해야 변경의 의도가 명확해지고, 문제가 생겼을 때 원인을 추적할 수 있다.

이번 마이그레이션에서:
- Phase 1(Yarn)에서는 패키지 매니저만 변경한다. Node 버전은 건드리지 않는다
- Phase 2(Node)에서는 런타임만 변경한다. TypeScript는 건드리지 않는다
- 각 Phase가 완료되고 검증된 후에야 다음 Phase로 넘어간다
- 기능 추가나 버그 수정은 마이그레이션 Phase와 섞지 않았다

**Make the Change Easy, Then Make the Easy Change (변경을 쉽게 만든 다음, 쉬운 변경을 하라)**

Fowler의 핵심 조언: 직접 변경이 어려우면, 먼저 구조를 정리해서 변경이 쉬운 상태로 만든 후 변경하라.

이번 마이그레이션에서:
- React 19로 바로 올리는 것이 어려웠다 → 먼저 앱별 독립 관리 구조로 전환(변경을 쉽게 만듦) → 그 다음 TV앱만 React 19 적용(쉬운 변경)
- Next.js 15로 바로 올리는 것이 어려웠다 → 먼저 async API 래퍼 패턴 도입 등의 준비 → Account/Bill에서 15 적용

---

### Clean Architecture (Robert C. Martin)

이 책은 소프트웨어 아키텍처에서 의존성의 방향과 경계의 중요성을 강조한다.

**Dependency Rule (의존성 규칙)**

"소스 코드의 의존성은 항상 안쪽(상위 정책)을 향해야 한다. 바깥쪽(하위 세부사항)의 변경이 안쪽에 영향을 주어서는 안 된다."

이번 마이그레이션의 Phase 순서는 두 가지 독립된 원칙의 조합이다:

```
독립적 변경          계층적 변경 (하위→상위)

Yarn 3→4             Node 18→22
TypeScript 4→5           ↓
                     React 18→19
                         ↓
                     Next.js 14→15
```

Dependency Rule은 **계층적 변경**에 적용된다. Node(런타임) → React(UI) → Next.js(프레임워크)에는 실제 계층 의존성이 있으므로, 하위를 먼저 안정화한 후 상위를 변경해야 한다. 만약 역순(Next.js부터)으로 했다면, Node 업그레이드 시 Next.js가 다시 깨질 수 있다.

한편 Yarn↔Node, TypeScript↔React는 서로 다른 차원(도구 vs 런타임, 빌드 도구 vs UI 라이브러리)이라 계층 상하 관계가 성립하지 않는다. Yarn과 TypeScript는 다른 변경에 영향을 주지 않는 **독립적 변경**이므로 계층 순서와 별개로 먼저 처리되었다.

**Stable Dependencies Principle (안정된 의존성 원칙)**

"덜 안정적인 모듈이 더 안정적인 모듈에 의존해야 한다." 자주 바뀌는 것이 안정적인 것에 의존해야지, 그 반대가 되면 변경의 파급 효과가 커진다.

루트 `resolutions`로 모든 앱의 React 버전을 강제하던 구조는 이 원칙을 위반하고 있었다. 자주 변경되어야 할 개별 앱의 의존성이, 변경이 어려운(모든 앱에 영향을 주는) 루트 설정에 묶여 있었다. 앱별 독립 관리로 전환하여 이 위반을 해소했다.

**Screaming Architecture (비명 아키텍처)**

Martin은 "아키텍처를 보면 시스템이 무엇을 하는지 소리쳐야 한다"고 말한다. 프레임워크는 도구일 뿐, 아키텍처를 지배해서는 안 된다.

PC 앱이 Next.js 12에 깊이 결합되어 160개 파일을 수정해야 하는 상황이, 프레임워크가 아키텍처를 지배한 결과다. Account/Bill은 이미 Next.js 14 + App Router를 사용하고 있어 15로의 전환이 1단계 메이저 점프로 수월했다. 반면 PC는 Next.js 12 + Pages Router에서 App Router로의 전환까지 필요해 3단계 메이저 점프(12→13→14→15)와 라우팅 패러다임 변경이 겹치는 상황이었다.

---

### The Pragmatic Programmer (David Thomas & Andrew Hunt, 20th Anniversary Edition)

이 책은 실용주의적 소프트웨어 개발 철학과 구체적 실천법을 다룬다.

**Orthogonality (직교성)**

"두 개 이상의 것이 서로 영향을 주지 않으면 직교적이다." 직교적인 시스템에서는 한 부분의 변경이 다른 부분에 영향을 주지 않는다.

루트 `resolutions`로 React를 강제 통일하던 구조는 **비직교적**이었다. TV앱의 React 업그레이드가 PC앱에 영향을 줄 수 있었다. 앱별 독립 관리로 전환한 것은 **직교성을 확보**한 것이다. TV앱이 React 19를 쓰든 PC앱이 18.3.1을 쓰든 서로 영향을 주지 않는다.

**Reversibility (가역성)**

"최종 결정은 없다. 돌이킬 수 없는 결정의 수를 줄여라."

Phase별 마이그레이션의 핵심 장점이 가역성이다:
- Yarn 4에서 문제가 생기면 Yarn 3으로 롤백 가능
- Node 22에서 문제가 생기면 Node 18로 롤백 가능
- 각 Phase가 독립적이라 하나를 되돌려도 다른 Phase에 영향이 없다
- PC Next.js 15를 보류한 것도 "돌이킬 수 없는 160개 파일 변경"을 피한 것이다

**Tracer Bullets (예광탄)**

"예광탄은 목표물과 총구 사이의 실시간 피드백을 제공한다." 전체를 완성하기 전에 끝에서 끝까지 동작하는 얇은 경로를 먼저 만들어 검증하라.

각 Phase의 PoC(빌드/실행 검증)가 예광탄이다:
- Yarn 4로 전환 후 바로 빌드가 되는지 확인 (전체 테스트 전에)
- Node 22로 전환 후 바로 앱이 실행되는지 확인
- TypeScript 5로 전환 후 바로 타입 체크가 통과하는지 확인
- "먼저 되는지 확인하고, 그 다음 세부 사항을 처리한다"

**Don't Outrun Your Headlights (헤드라이트를 앞서지 마라)**

"확실하게 보이는 만큼만 진행하라. 너무 먼 미래를 예측하지 마라."

PC Next.js 15를 보류한 것이 이 원칙이다. 12→15까지 3단계 메이저 점프는 "헤드라이트 너머"다. 보이는 범위(12.3.7 보안 패치)까지만 진행하고, 나머지는 별도 작업으로 남겨둔다.

---

### Continuous Delivery (Jez Humble & David Farley)

이 책은 소프트웨어를 항상 배포 가능한 상태로 유지하는 방법을 다룬다.

**Branch by Abstraction (추상화에 의한 분기)**

기존 구현과 새 구현이 공존해야 할 때, 코드 브랜치(Git branch)가 아닌 **추상화 계층**을 통해 분기하는 기법이다.

이번 마이그레이션에서:
- TV앱은 React 19, PC앱은 React 18.3.1 — 같은 모노레포에서 두 버전이 공존한다
- webpack alias가 추상화 계층 역할을 하여, 각 앱이 자신의 React 버전을 사용하되 싱글톤을 보장한다
- Git branch로 버전별 코드를 분리하지 않고, 같은 코드베이스에서 추상화를 통해 공존시킨다

**Deployment Pipeline (배포 파이프라인)**

"모든 변경은 동일한 파이프라인을 통과해야 한다. 파이프라인을 통과한 변경만 프로덕션에 배포된다."

각 Phase의 "QA 배포 → 검증 → 프로덕션 배포" 흐름이 배포 파이프라인이다. CI/CD 워크플로우 25개 파일을 함께 변경한 것도, 파이프라인 자체가 새로운 버전을 올바르게 빌드/배포할 수 있도록 보장하기 위한 것이다.

**Keep the Build Green (빌드를 항상 녹색으로)**

"빌드가 깨진 상태를 방치하지 마라. 깨지면 모든 것을 멈추고 고쳐라."

각 Phase를 작게 나눈 이유 중 하나다. Yarn 4 업그레이드 후 빌드가 녹색인 것을 확인하고 나서야 Node 22로 넘어간다. 한 번에 여러 것을 바꾸면, 빌드가 깨졌을 때 어떤 변경이 원인인지 알 수 없다.

---

### Release It! (Michael Nygard, 2nd Edition)

이 책은 프로덕션 환경에서의 안정성 패턴과 배포 전략을 다룬다.

**Bulkhead Pattern (격벽 패턴)**

선박에서 한 구획이 침수되어도 다른 구획은 안전하도록 격벽을 두는 것처럼, 시스템의 한 부분의 장애가 다른 부분으로 전파되지 않도록 격리하는 패턴이다.

앱별 React 버전 독립 관리가 격벽 패턴이다:
- TV앱의 React 19 문제가 PC앱에 영향을 주지 않는다
- Account/Bill의 Next.js 15 문제가 PC의 Next.js 12에 영향을 주지 않는다
- 한 앱에서 문제가 발생해도 다른 앱은 안전하게 운영된다

**Fail Fast (빠르게 실패하라)**

문제가 발생하면 가능한 한 빨리, 가능한 한 가까운 곳에서 실패하라. 문제를 숨기거나 우회하면 나중에 더 큰 장애로 돌아온다.

node-sass 빌드 실패가 좋은 예다. Node 22에서 node-sass가 바로 빌드 에러를 내뱉었기 때문에, dart-sass로의 전환이 필요하다는 것을 즉시 알 수 있었다. 만약 런타임에 조용히 실패했다면 프로덕션에서 문제가 발견되었을 것이다.

---

## 보통 관련: 부분적으로 원칙이 적용된 서적

### Building Evolutionary Architectures (Neal Ford, Rebecca Parsons, Patrick Kua)

이 책은 시간이 지나도 변화에 대응할 수 있는 아키텍처를 설계하는 방법을 다룬다.

**Fitness Functions (적합도 함수)**

아키텍처가 의도된 특성을 유지하는지 자동으로 검증하는 메커니즘이다. 단위 테스트가 기능을 검증하듯, 적합도 함수는 아키텍처 특성(성능, 보안, 의존성 규칙 등)을 검증한다.

각 Phase의 PoC 빌드/실행 검증이 적합도 함수 역할을 한다. "Yarn 4 + Node 22 환경에서 빌드 성공하는가?" "React 19에서 기존 컴포넌트가 동작하는가?" 등이 이 마이그레이션의 적합도 함수다.

**Incremental Change (점진적 변경)**

"아키텍처를 한 번에 교체하지 말고, 작은 단위의 진화적 변경을 반복하라."

Phase 1→6까지의 순차적 접근이 점진적 변경이다. 각 Phase가 아키텍처의 한 측면만 변경하고, 변경 후 시스템이 여전히 적합도 함수를 통과하는지 확인한다.

---

### A Philosophy of Software Design (John Ousterhout)

이 책은 소프트웨어 복잡성의 본질과 이를 줄이는 설계 원칙을 다룬다.

**Strategic vs Tactical Programming (전략적 vs 전술적 프로그래밍)**

Ousterhout는 "전술적 프로그래밍"(당장 동작하게 만드는 것)과 "전략적 프로그래밍"(좋은 설계에 투자하는 것)을 구분한다. 전술적 프로그래밍이 쌓이면 복잡성이 기하급수적으로 증가한다.

PC Next.js 15 보류에서 12.3.7 보안 패치만 적용한 것은 전술적 선택이지만, 이것은 의식적인 전략적 결정의 일부다. "지금은 보안만 해결하고, 근본적 전환은 별도 작업으로 계획한다"는 것은 전략적 사고를 바탕으로 한 전술적 실행이다.

**Complexity is Incremental (복잡성은 점진적이다)**

"복잡성은 한 번에 오지 않는다. 작은 것들이 쌓여서 만들어진다."

루트 `resolutions`로 React를 강제 통일하는 구조도 처음에는 합리적인 결정이었을 것이다. 하지만 앱이 늘어나고, 각 앱의 요구사항이 달라지면서 이 "간단한 설정"이 점점 복잡성의 원인이 되었다. 마이그레이션은 이렇게 축적된 복잡성을 해소하는 과정이다.

---

### Clean Code (Robert C. Martin)

이 책은 읽기 좋고 유지보수하기 좋은 코드를 작성하는 실천법을 다룬다.

**Boy Scout Rule (보이스카우트 규칙)**

"캠프장을 떠날 때 왔을 때보다 깨끗하게 남겨라." 코드를 수정할 때마다 그 주변을 조금 더 깨끗하게 만들라.

이번 마이그레이션 전체가 보이스카우트 규칙의 대규모 실천이다. 버전을 올리면서 동시에:
- node-sass → dart-sass로 현대화
- 루트 resolutions 강제 구조 → 앱별 독립 관리로 개선
- 오래된 CI/CD 설정을 새 버전에 맞게 정리

단순히 "버전 숫자만 올리는" 것이 아니라, 지나가면서 만나는 기술 부채를 함께 청소했다.

**Single Responsibility Principle — SRP (단일 책임 원칙)**

"한 모듈은 변경의 이유가 하나여야 한다."

루트 `resolutions`가 모든 앱의 React 버전을 결정하는 것은 SRP 위반이다. 이 하나의 설정이 TV앱, PC앱, Account앱, Bill앱 모두에 영향을 준다. 앱별 `package.json`에서 각자 관리하도록 변경한 것은 "각 앱은 자신의 의존성에 대해서만 책임진다"는 SRP를 따른 것이다.

---

### 좋은 코드, 나쁜 코드 (Tom Long)

이 책은 코드 품질을 높이는 실용적 원칙을 다룬다.

**Minimize Assumptions (가정을 최소화하라)**

다른 모듈이 특정 방식으로 동작할 것이라는 가정을 줄여라. 가정이 깨지면 버그가 된다.

"모든 앱이 같은 React 버전을 쓸 것"이라는 가정이 깨진 순간이, React 듀얼 인스턴스 문제가 발생한 시점이다. webpack alias로 이 가정을 명시적으로 처리(각 앱이 사용할 React를 명시적으로 지정)하여 문제를 해결했다.

**Make Code Modular (코드를 모듈화하라)**

모듈 간의 결합을 줄이고, 각 모듈이 독립적으로 변경될 수 있게 하라.

모노레포 내 앱들 간의 결합을 줄인 것(앱별 독립 관리)이 이 원칙의 적용이다.

---

## 약한 관련: 개념적으로 연결되는 서적

### Designing Data-Intensive Applications (Martin Kleppmann)

**Rolling Upgrade (순차적 업그레이드)**

분산 시스템에서 모든 노드를 한 번에 업그레이드하지 않고, 한 노드씩 순차적으로 업그레이드하여 서비스 중단 없이 전환하는 기법이다.

모노레포의 앱별 독립적 마이그레이션이 이 개념과 유사하다. Account/Bill은 Next.js 15로 업그레이드하고, PC는 12.3.7에 머무르는 것은, "모든 앱을 한 번에 올리지 않는" 순차적 업그레이드 전략이다.

### The Clean Coder (Robert C. Martin)

**Saying No (아니라고 말하기)**

전문가는 불합리한 요구에 "아니요"라고 말할 수 있어야 한다.

PC Next.js 15를 "지금은 아니다"라고 판단한 것이 이 원칙이다. 160개 파일, 3단계 메이저 점프라는 리스크를 인정하고, 보안 패치만 적용하는 현실적 대안을 제시했다.

---

## 정리: 서적별 핵심 원칙 맵

### 깊은 관련

| 서적 | 핵심 원칙 | 해당 작업 |
|------|----------|----------|
| Refactoring | Strangler Fig Pattern | React 앱별 독립 관리, PC 보류 |
| Refactoring | Two Hats | Phase별 단일 목표만 수행 |
| Refactoring | Make the Change Easy | 구조 전환 후 버전 업그레이드 |
| Clean Architecture | Dependency Rule | 계층적 변경(Node→React→Next.js)은 하위→상위 |
| Clean Architecture | Stable Dependencies Principle | 루트 resolutions → 앱별 관리 |
| Pragmatic Programmer | Orthogonality | 앱 간 의존성 제거 |
| Pragmatic Programmer | Reversibility | Phase별 독립 롤백 가능 |
| Pragmatic Programmer | Tracer Bullets | 각 Phase PoC 검증 |
| Continuous Delivery | Branch by Abstraction | webpack alias로 React 버전 공존 |
| Release It! | Bulkhead Pattern | 앱별 격리, 장애 전파 차단 |

### 보통 관련

| 서적 | 핵심 원칙 | 해당 작업 |
|------|----------|----------|
| Building Evolutionary Architectures | Fitness Functions | Phase별 빌드/실행 검증 |
| Building Evolutionary Architectures | Incremental Change | Phase 1→6 순차 진행 |
| A Philosophy of Software Design | Strategic vs Tactical | PC 보안 패치 + 별도 계획 |
| A Philosophy of Software Design | Complexity is Incremental | resolutions 강제의 복잡성 축적 |
| Clean Code | Boy Scout Rule | 마이그레이션 + 기술 부채 청소 |
| Clean Code | SRP | 앱별 의존성 독립 관리 |
| 좋은 코드, 나쁜 코드 | Minimize Assumptions | webpack alias로 명시적 처리 |

### 약한 관련

| 서적 | 핵심 원칙 | 해당 작업 |
|------|----------|----------|
| DDIA | Rolling Upgrade | 앱별 순차적 마이그레이션 |
| The Clean Coder | Saying No | PC Next.js 15 보류 판단 |
