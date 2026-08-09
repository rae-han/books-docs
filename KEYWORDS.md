# 핵심 단어 용어 사전

README 목차 표와 Notion 챕터 DB의 `핵심 단어`에 쓰는 **대표 표기**를 통일하기 위한 사전. 같은 개념이 책마다 다른 표기로 흩어지면 검색이 안 되므로, 핵심 단어를 쓰기 전에 여기서 대표 표기를 확인한다.

## 사용 규칙

- 형식: `- 대표 표기: 동의어1, 동의어2, ...` - 핵심 단어에는 **대표 표기만** 사용하고 동의어는 쓰지 않는다
- 새 핵심 단어를 쓸 때 이 사전에 없으면 그대로 쓰되, **동의어·이표기가 존재하는 개념이면 반드시 등록**한다 (등록은 가나다순)
- 대표 표기는 한국어 우선, 통용 약어는 동의어로 등재 (예: 의존성 역전 ← DIP)
- **영문·약어로 시작하는 표기**(API 게이트웨이, JWT 등)는 한국어 대응어가 통용되지 않는 경우만 쓰고, 목록 맨 뒤 `영문 시작 표기` 구역에 알파벳순으로 둔다

## 사전 (가나다순)

- 값 객체: value object, VO
- 개방-폐쇄 원칙: OCP, 열림-닫힘 원칙
- 결합도: coupling, 커플링 (반대 축: 응집도)
- 계약 테스트: contract test, 소비자 주도 계약, CDC
- 고차 함수: higher-order function, HOF
- 관측 가능성: observability, 관측용이성, 관찰 가능성
- 교살자 무화과나무: strangler fig, 스트랭글러 피그, 교살자 무화과 패턴
- 깊은 모듈: deep module (반대: 얕은 모듈 shallow module)
- 깊이 우선 탐색: DFS, depth-first search
- 너비 우선 탐색: BFS, breadth-first search
- 단일 책임 원칙: SRP
- 동적 프로그래밍: DP, 동적 계획법, dynamic programming
- 디미터 법칙: Law of Demeter, 데메테르 법칙, 최소 지식 원칙
- 리스코프 치환 원칙: LSP, 리스코프 치환
- 리팩터링: 리팩토링, refactoring
- 메모이제이션: memoization, 메모화
- 목 객체: mock object, 모의 객체, 목
- 봉합: Seam, 이음새, 심
- 불변성: immutability, 이뮤터블
- 빅 오 표기법: Big O, 빅오, 점근 표기법
- 사이드카 프록시: sidecar proxy, 사이드카
- 삼각측량: triangulation
- 서비스 메시: service mesh
- 시맨틱 버저닝: semantic versioning, semver, 유의적 버전
- 아키텍처 결정 레코드: ADR, architecture decision record
- 아키텍처 특성: architecture characteristics, 품질 속성, quality attributes, -ilities
- 연결 리스트: linked list, 링크드 리스트
- 옵저버 패턴: 관찰자 패턴, Observer 패턴
- 위협 모델링: threat modeling (기법: 스트라이드 STRIDE, 드레드 DREAD)
- 응집도: cohesion (반대 축: 결합도)
- 의존성 역전: DIP, 의존관계 역전
- 의존성 주입: DI, 의존관계 주입
- 이진 검색: binary search, 이진 탐색, 이분 탐색
- 이진 탐색 트리: BST, binary search tree, 이진 검색 트리
- 이터레이터: 반복자, iterator
- 인수 테스트: acceptance test, 인수 검사
- 인터페이스 분리 원칙: ISP
- 일급 함수: first-class function, 1급 함수
- 자가 테스트 코드: self-testing code
- 전략 패턴: 스트래티지 패턴, Strategy 패턴
- 정보 은닉: information hiding, 정보 은폐
- 제로 트러스트: zero trust, 경계 없는 보안
- 지연 평가: lazy evaluation, 게으른 평가, 늦은 평가
- 진화적 아키텍처: evolutionary architecture
- 짝 프로그래밍: pair programming, 페어 프로그래밍
- 카나리 릴리스: canary release, 카나리 배포
- 캡슐화: encapsulation
- 커링: currying
- 코드 악취: bad smell, 나쁜 냄새, 코드 스멜
- 퀵 정렬: quicksort, 퀵소트
- 클로저: closure (SICP의 '닫힘 성질 closure property'와는 다른 개념)
- 테스트 주도 개발: TDD
- 트라이: trie, 접두사 트리, prefix tree
- 트래픽 미러링: traffic mirroring, 다크 론치, dark launch
- 특성화 테스트: characterization test, 문서화 테스트
- 포트와 어댑터: 헥사고날 아키텍처, ports and adapters
- 피트니스 함수: fitness function, 적합도 함수, 적합성 함수
- 함수 추출하기: Extract Function, 메서드 추출, Extract Method
- 합성: composition, 컴포지션, 객체 합성
- 해시 테이블: hash table, 해시맵, 해시 맵

## 영문 시작 표기 (알파벳순)

한국어 대응어가 통용되지 않아 원어 표기를 대표로 쓰는 항목들이다.

- API 게이트웨이: API gateway, 에지 게이트웨이
- gRPC: 원격 프로시저 호출(RPC)의 구현체 - 개념어로서의 RPC와 구분해 쓴다
- JWT: JSON 웹 토큰, JSON Web Token
- OAuth2: OAuth 2.0
- OpenAPI 명세: OAS, 스와거, Swagger
