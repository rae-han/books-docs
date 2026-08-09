# 기술 서적 학습 노트

소프트웨어 엔지니어링 관련 기술 서적을 **책 없이도 학습 가능한 수준**으로 정리한 한국어 마크다운 노트 저장소. 각 책은 폴더 하나로 관리하며, 노트는 Notion에도 미러링한다.

## 저장소 구조

```
docs/
├── README.md          ← 이 파일 (전체 현황)
├── CLAUDE.md          ← 작업 규칙 (노트 스타일·Notion 업로드·origin 분리 절차)
├── AGENTS.md          ← 에이전트용 지침
├── KEYWORDS.md        ← 용어 사전 (핵심 단어 표기 통일용)
├── QUOTES.md          ← 전 책 인용문 통합 모음
└── <책 폴더>/
    ├── README.md              ← 책 정보·목차 표·학습 가이드·핵심 개념 맵
    ├── chNN-<kebab-case>.md   ← 챕터 노트
    └── N.origin.md            ← PDF/OCR 원본 분리본 (.gitignore 대상, 커밋되지 않음)
```

각 책 README의 **목차 표**(`| Ch | 제목 | 핵심 단어 | 한 줄 요약 |`)가 Notion 챕터 DB의 `핵심 단어`·`핵심 요약` 값의 **유일한 소스**다. 재업로드 시 항상 이 표를 기준으로 채운다.

## 책 목록

### 노트 완료 · Notion 업로드 완료

| 책 | 저자 | 노트 | 인용문 | Notion |
|----|------|------|--------|--------|
| [레거시 코드 활용 전략](legacy-code/) | 마이클 페더스 | 25장+부록 | ✓ | [🔗](https://app.notion.com/p/3dd693832f7a485095caf66b68b2e710) |
| [A Philosophy of Software Design](philosophy-of-software-design/) | 존 오스터하우트 | 22장 | ✓ | [🔗](https://app.notion.com/p/30fde4986fe380c38ef2d4adfadaf163) |
| [테스트 주도 개발](test-driven-development-by-example/) | 켄트 벡 | 32장 | ✓ | [🔗](https://app.notion.com/p/92aa690eab454410be67ca61805ab3c6) |
| [SICP (JavaScript Edition)](structure-and-interpretation-of-computer-programs-javascript/) | 에이블슨·서스먼 / 헨츠 | 22섹션 | ✓ | [🔗](https://app.notion.com/p/1c8de4986fe380ccb9fbde00249f6994) |
| [클린 코더](the-clean-coder/) | 로버트 C. 마틴 | 14장+부록 | ✓ | [🔗](https://app.notion.com/p/86f0d9bc0c6d4ac8b4865f0f37b64cc3) |
| [CODE: 하드웨어·소프트웨어에 숨어 있는 언어](code-the-hidden-language/) | 찰스 페촐트 | 28장 | ✓ | [🔗](https://app.notion.com/p/b473bab308a042e1bca2c6a28d477ce4) |
| [오브젝트](objects/) | 조영호 | 15장+부록3 | ✓ | [🔗](https://app.notion.com/p/7bcca88b054c4f4390b1be7ae56185f6) |
| [소프트웨어 장인](the-software-craftsman/) | 산드로 만쿠소 | 16장+부록 | ✓ | [🔗](https://app.notion.com/p/d0996efa9c914439bc90b701a5e0bf48) |
| [읽기 쉬운 코드](code-that-fits-in-your-head/) | 마크 시먼 | 16장+부록3 | ✓ | [🔗](https://app.notion.com/p/395de4986fe381e48b78c7dba15cdf64) |
| [개발자에서 아키텍트로](design-it-from-programmer-to-software-architect/) | 마이클 킬링 | 17장 | ✓ | [🔗](https://app.notion.com/p/450208c4cc2244bfac12fc77004eae00) |
| [소프트웨어 아키텍처 101 (1판)](fundamentals-of-software-architecture-1st-edition/) | 리처즈·포드 | 24장+부록 | ✓ | [🔗](https://app.notion.com/p/5904199b064c4f47ac1df9a3338d9ecf) |
| [소프트웨어 아키텍처 The Basics (2판)](fundamentals-of-software-architecture-2nd-edition/) | 리처즈·포드 | 27장+부록 | ✓ | [🔗](https://app.notion.com/p/3a7de4986fe3816786ccf65739e4c452) |
| [리팩터링 2판](refactoring-2nd-edition/) | 마틴 파울러 | 12장+부록2 | ✓ | [🔗](https://app.notion.com/p/6f13c5703447472680dc3d8bd2744112) |
| [실용주의 프로그래머](the-pragmatic-programmer/) | 토머스·헌트 | 9장+tips | ✓ | [🔗](https://app.notion.com/p/3bf2491927e94ecc8e8343008c802507) |
| [헤드 퍼스트 디자인 패턴](head-first-design-patterns/) | 프리먼·롭슨 외 | 14장 | ✓ | [🔗](https://app.notion.com/p/39ade4986fe3815aa455c606384ec41f) |
| [커리어 스킬](the-complete-software-developers-career-guide/) | 존 손메즈 | 60장+부록 | ✓ | [🔗](https://app.notion.com/p/99ba98f1a0c74d2581d1a9324af96e1c) |
| [누구나 자료 구조와 알고리즘](a-common-sense-guide-to-data-structures-and-algorithms/) | 제이 웬그로우 | 20장 | ✓ | [🔗](https://app.notion.com/p/3aede4986fe381768c5cc820a683ac65) |
| [클린 아키텍처](clean-architecture/) | 로버트 C. 마틴 | 34장+부록 | ✓ | [🔗](https://app.notion.com/p/9a9f17e17ecd424eaeb5f5b83e5d894b) |
| [클린 코드](clean-code/) | 로버트 C. 마틴 | 17장+부록4 | ✓ | [🔗](https://app.notion.com/p/af3ed0d20c22408484c5ab820b29e6c4) |
| [클린 소프트웨어](clean-software/) | 로버트 C. 마틴 | 34장 | ✓ | [🔗](https://app.notion.com/p/c167ff747602415c9c66dde01e70dc9c) |
| [좋은 코드, 나쁜 코드](good-code-bad-code/) | 톰 롱 | 11장+부록3 | ✓ | [🔗](https://app.notion.com/p/0da167c5de09400bb5794f0956a73638) |
| [객체지향의 사실과 오해](the-essence-of-object-orientation-객체지향의-사실과-오해/) | 조영호 | 7장 | ✓ | [🔗](https://app.notion.com/p/8e1b21881ff340e5a3215650fa8eb42c) |
| [육각형 개발자](the-hexagonal-developer/) | 최범균 | 11장 | ✓ | [🔗](https://app.notion.com/p/328de4986fe3819682b0e62f3ee12e28) |
| [단위 테스트](unit-testing/) | 블라디미르 코리코프 | 11장 | ✓ | [🔗](https://app.notion.com/p/31bde4986fe3812d9ce1dbd5539aab84) |
| [멀티패러다임 프로그래밍](multi-paradigm-programming/) | 유인동 | 8장 | — | [🔗](https://app.notion.com/p/324de4986fe381bf8bfbfc83645bdb8d) |
| [주니어 백엔드 개발자 실무 지식](essential-skills-for-junior-backend-developers-주니어-백엔드-개발자가-반드시-알아야-할-실무=-지식/) | — | 11장+부록3 | — | [🔗](https://app.notion.com/p/326de4986fe38118ba0cd78e74612b92) |
| [함수형 프로그래밍 완전 가이드](functional-programming-complete-guide/) | 자체 구성 | 5부 19장 | ✓ | [🔗](https://app.notion.com/p/3a3de4986fe38162896dd655d2d07456) |
| [Docker 완전 가이드](docker-complete-guide/) | 자체 구성 | 6부 15장 | — | [🔗](https://app.notion.com/p/31cde4986fe3819483b9c30ae57764c8) |
| [AWS 완전 가이드](aws-complete-guide/) | 자체 구성 | 7부 16장 | — | [🔗](https://app.notion.com/p/325de4986fe381d4a71bd4eb9073188b) |
| [자바스크립트 + 리액트 디자인 패턴](javascript-react-pattern/) | 애디 오스마니 | 16장 | — | [🔗](https://app.notion.com/p/31cde4986fe381cfb282cdbabe55db08) |
| [미니멀리즘 프로그래머](minimalism-programmer/) | 데이비드 토머스 | 9장 | ✓ | [🔗](https://app.notion.com/p/35cde4986fe380b88921dc601eb5c917) |
| [함수형 자바스크립트 (fp)](fp/) | Notion 이관본 | 22편 | — | [🔗](https://app.notion.com/p/f5344f83755c4de68f96732af6eb21f9) |

> **Notion 페이지 위치 주의**: 대부분은 `Must reads` → `Dev` DB 항목 안에 있지만, **자바스크립트+리액트 디자인 패턴**은 `Front-End & JavaScript & Typescript` DB 아래, **미니멀리즘 프로그래머**는 Dev DB 밖의 별도 페이지 트리에, **fp**는 이관 원본(`Functional Javascript with ES6+` / `FP with ES6+` DB / `Functional JS`)으로 각각 다른 위치에 있다. Dev DB만 훑으면 누락된다.

### 노트 완료 · Notion 미업로드

| 책 | 저자 | 노트 | 비고 |
|----|------|------|------|
| [프런트엔드 성능 최적화 Deep Dive](frontend-performance-optimization-deep-dive/) | 김용찬 | 26장+부록 | 최근 작성 |
| [이것이 취업을 위한 코딩 테스트다](this-is-coding-test/) | 나동빈 | 19장 | 파이썬 → TypeScript 변환 |
| [코딩 테스트 합격자 되기 (JS편)](programmers-coding-test/) | 이선협·박경록 | 17장+부록 | |
| [하면 된다! 퀀트 투자](quant/) | 강환국 | 6장 | Part 4~5 발췌본 |
| [모던 API 아키텍처 설계 전략](mastering-api-architecture/) | 제임스 고프 외 | 11장 | 0장~10장 · Java→TypeScript 병기 |

### origin 분리만 완료 (노트 미작성)

| 책 | 저자 | 상태 |
|----|------|------|
| [그림으로 배우는 도커](docker-illustrated-introduction/) | 스즈키 료 | origin 32장 분리 완료 |
| [만들면서 배우는 헥사고날 아키텍처](hex/) | 다비 비에이라 | origin 15장 분리 완료 · 인용문 절만 작성 |

## 공통 자산

- **[QUOTES.md](QUOTES.md)** — 전 책 인용문 통합 모음. 각 책 README의 `## 인용문` 절과 동기화하며, **현재 27권**이 인용문 절을 보유한다. 노트가 없는 책(클린 애자일·맨먼스 미신 등 12권)의 인용도 하단 구역에 수집하고, 출처가 책이 아닌 것은 `개발 명언 모음`에 둔다.
- **[KEYWORDS.md](KEYWORDS.md)** — 용어 사전. 목차 표의 `핵심 단어`를 쓰기 전에 여기서 대표 표기를 확인하고, 동의어가 생기면 등록한다. 같은 개념은 책이 달라도 같은 표기를 쓴다.
- **[CLAUDE.md](CLAUDE.md)** — 작업 규칙 전체. 노트 작성 스타일, 표 vs 리스트 선택 규칙, Notion 업로드 규칙(한글 리터럴·콜아웃 변환·표 형식), DB/뷰 표준, origin 분리 절차가 들어 있다.

## Notion 연동

허브: **[Raehan's Must reads](https://app.notion.com/p/a06845cc6c554dff965624974d90db5e)** (Develop → Must reads)

책 하나당 페이지 하나를 두고, 그 안에 **인라인 챕터 DB**를 둔다.

**챕터 DB 표준 속성**

| 속성 | 타입 | 값의 소스 |
|------|------|-----------|
| `Done` | checkbox | 읽음 표시 (수동) |
| `Title` / `Name` | title | 챕터 제목 |
| `Chapter` | number | 챕터 번호 (정렬용) |
| `Part` | select 색상 딱지 | 책의 파트 구분 (없으면 다른 분류 기준 — 예: 헤드 퍼스트의 `패턴 범주`) |
| `핵심 단어` | text 또는 multi-select | 책 README 목차 표 |
| `핵심 요약` | text (~80자) | 책 README 목차 표 |

**뷰 표준**

```
SHOW "Done", "Title", "Part", "핵심 단어", "핵심 요약"; SORT BY "Chapter" ASC
```

`Done`이 맨 앞, `Chapter` 열은 제목에 번호가 이미 있으면 숨긴다(숨겨도 정렬은 정상 동작). 제목에 번호가 없는 CODE만 `Chapter` 열을 노출한다.

**업로드 시 반드시 지킬 것**

- 원본 그대로 올린다 — 요약·압축 금지. 파일이 크면 나눠서라도 전체를 올린다
- **한글은 리터럴 그대로** — `\uXXXX` 이스케이프를 손수 계산해 넣으면 음절이 깨진다(캡슐화→캐슸화 등 실사례 다수)
- 업로드 후 1~2개 페이지를 열어 한글 손상을 눈으로 확인한다

자세한 절차와 함정은 [CLAUDE.md](CLAUDE.md)의 "Notion 업로드 규칙" 절 참조.

## 작업 순서 (새 책 추가 시)

0. 책 폴더 스캐폴딩 — `origin.md`(빈 파일)와 `README.md`(표준 뼈대)만 먼저 만든다 (챕터 파일은 노트 작성 시점에)
1. PDF/OCR 원본을 `origin.md` → 챕터별 `N.origin.md`로 분리 (라인 합계·byte 검증)
2. 1~2개 챕터를 샘플로 작성해 확인받은 뒤 전체 진행
3. 책 README 작성 — 목차 표의 `핵심 단어`는 KEYWORDS.md 표기를 따를 것
4. 인용문이 있으면 README `## 인용문` 절 + QUOTES.md에 동시 반영
5. Notion 페이지 + 인라인 DB 생성 → 챕터 업로드 → 목차 표 기준으로 속성 채우기
6. 이 파일(루트 README)의 책 목록에 한 줄 추가
