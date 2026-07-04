# Project: 기술 서적 학습 노트

## 프로젝트 개요

소프트웨어 엔지니어링 관련 기술 서적을 **책 없이도 학습 가능한 수준**으로 한국어 마크다운 노트로 정리하는 프로젝트.

## 완료된 작업

### 1. legacy-code/ — Working Effectively with Legacy Code (Michael Feathers)
- 25개 챕터 + 부록 + 사례 연구 + README
- 상태: **완료**

### 2. philosophy-of-software-design/ — A Philosophy of Software Design (John Ousterhout, 2nd Edition)
- 22개 챕터 + README
- 상태: **완료**

### 3. clean-architecture/ — Clean Architecture (Robert C. Martin)
- 상태: **보류**

### 4. test-driven-development-by-example/ — Test-Driven Development: By Example / 테스트 주도 개발 (Kent Beck)
- 3 Parts, 32개 챕터 + README
- 상태: **완료**

### 5. structure-and-interpretation-of-computer-programs-javascript/ — Structure and Interpretation of Computer Programs, JavaScript Edition (Abelson, Sussman / Henz, Wrigstad)
- 5 Chapters, 22개 섹션 + README
- 파일 네이밍: `sec{챕터}.{섹션}-{영문-kebab-case}.md`
- 상태: **완료**

### 6. the-clean-coder/ — The Clean Coder: A Code of Conduct for Professional Programmers (Robert C. Martin)
- Introduction + 14개 챕터 + Appendix + README
- 상태: **완료**

### 7. code-the-hidden-language/ — CODE: The Hidden Language of Computer Hardware and Software (Charles Petzold, 2nd Edition)
- 28개 챕터 + README
- 상태: **완료**

### 8. docker-complete-guide/ — Docker 완전 가이드 (자체 구성)
- Docker Deep Dive + Docker in Action 범위를 커버하는 독자적 가이드
- 6 Parts, 15개 챕터 + README
- 공식 문서 + best practice 기반, 모든 예제는 Node.js/Next.js 기반
- 상태: **진행 중**

### 9. the-hexagonal-developer/ — 육각형 개발자 (최범균, 한빛미디어, 2023)
- 11개 챕터 + README
- 시니어 개발자로 성장하기 위한 10가지 핵심 역량
- 상태: **진행 중**

### 10. aws-complete-guide/ — AWS 완전 가이드 (자체 구성)
- AWS 핵심 서비스를 체계적으로 학습하는 독자적 가이드
- 7 Parts, 16개 챕터 + README
- 공식 문서 + Well-Architected Framework 기반, 모든 예제는 Node.js/Next.js 기반
- 상태: **진행 중**

### 11. objects/ — 오브젝트: 코드로 이해하는 객체지향 설계 (조영호, 위키북스, 2019)
- 15개 챕터 + 3개 부록 + README
- 자매편: the-essence-of-object-orientation-객체지향의-사실과-오해/
- 코드 예제: Java(원본, `<details>` 접기) + TypeScript(변환, 항상 펼침) 병기
- 상태: **완료**

### 12. the-software-craftsman/ — The Software Craftsman: Professionalism, Pragmatism, Pride (Sandro Mancuso, 2015)
- 16개 챕터 + Appendix A + README
- 소프트웨어 장인정신 이념·태도·조직 문화. 로버트 C. 마틴 시리즈
- 저자 경험담(브라질→런던, LSCC, Codurance)이 풍부. 레이블 없는 `>` 인용문으로 표현
- 상태: **완료**

### 13. code-that-fits-in-your-head/ — Code That Fits in Your Head: Heuristics for Software Engineering (Mark Seemann, 2021)
- 16개 챕터 + Appendix A/B/C + README
- 소프트웨어 공학 휴리스틱 안내서. 로버트 C. 마틴 시리즈
- 예제: C# 기반 레스토랑 예약 시스템 (하나의 코드베이스가 챕터마다 성장)
- Part 1(가속): TDD·설계·팀워크 / Part 2(지속가능성): 기능 추가·테스트 편집·문제 해결
- 상태: **완료**

### 14. design-it-from-programmer-to-software-architect/ — Design It!: From Programmer to Software Architect (Michael Keeling, 2017)
- 17개 챕터 + README (Ch1-13 본문 + Ch14-17 38가지 활동 카탈로그)
- 개발자에서 아키텍트로 성장하기 위한 실전 훈련서
- **라이언하트 프로젝트**(스프링필드시 RFP 시스템)를 사례 연구로 전 장 관통
- Part 1(마인드셋), Part 2(설계 프로세스), Part 3(활동 카탈로그) 구성
- 상태: **완료**

## 공통 작성 스타일

- **언어**: 한국어, 서술형 "-다" 체
- **구조**: 각 챕터별 독립 마크다운 파일 + README.md (목차/개요)
- **챕터 파일 구성**:
  - `# Chapter N: 영문 제목 (한국어 부제)` 형식의 제목
  - `## 핵심 질문` — 챕터의 핵심 물음
  - 번호가 매겨진 주요 섹션 (`## 1.`, `## 2.`, ...)
  - 코드 예시 (나쁜 예 vs 좋은 예 대비)
  - `> **핵심 통찰**:` blockquote로 핵심 인사이트 강조
  - 비교 테이블 (markdown table)
  - `## 요약` — 불릿 포인트 정리
  - `## 다른 챕터와의 관계` — 관련 챕터 간 연결고리 설명 (선택적, 챕터 간 연결이 약한 책은 생략 가능)
- **책별 특수 요소**: 각 책의 고유 개념에 맞는 요소 추가
  - philosophy-of-software-design: `## Red Flags` 섹션
  - legacy-code: 기법별 단계(Step) 정리
  - test-driven-development-by-example: `## TDD 사이클` (Red → Green → Refactor 단계별 코드), `## TODO 리스트` (Kent Beck 스타일 할 일 목록 추적)
  - structure-and-interpretation-of-computer-programs-javascript: `## 핵심 개념` (섹션에서 도입되는 중요 개념 정의), `## 주요 예제` (SICP 핵심 예제 코드와 상세 설명), `## 계산 모델` (치환 모델, 환경 모델 등 평가 모델 설명), `## 연습 문제 하이라이트` (유명한 연습 문제 소개/풀이)
  - the-clean-coder: `> **Uncle Bob의 경험**:` (저자의 실제 경험담 blockquote), `### 대화:` (PM-개발자 간 대화 시나리오), `## 실전 시나리오` (비프로 vs 프로 대응 대비), `## 프로의 원칙` (챕터별 원칙 테이블), `## 자기 점검` (체크리스트 형태 자기 반성 질문)
  - code-the-hidden-language: `> **Petzold의 비유**:` (저자의 직관적 비유 blockquote), `## 진리표` (논리 게이트/회로 진리표), `## 회로 구성` (텍스트 기반 회로 다이어그램), `## 단계별 구축` (이전 챕터 개념이 현재 챕터로 쌓이는 과정 테이블)
  - docker-complete-guide: `> **실무 팁**:` (운영 환경 best practice blockquote), `## 자주 하는 실수` (안티패턴과 해결법 테이블), `## 명령어 레퍼런스` (챕터별 핵심 명령어 테이블)
  - aws-complete-guide: `> **실무 팁**:` (운영 best practice blockquote), `> **비용 주의**:` (AWS 비용 관련 경고 blockquote), `## 자주 하는 실수` (안티패턴과 해결법 테이블), `## AWS CLI 레퍼런스` (챕터별 핵심 CLI 명령어 테이블)
  - the-hexagonal-developer: `>` 인용문 (저자의 실무 경험담, 레이블 없는 blockquote), `> **핵심 통찰**:` (핵심 인사이트 콜아웃), `### 딥 다이브:` (원서의 "더" 박스 심화 사례), `## 성장 체크리스트` (챕터별 자기 점검 체크박스 리스트, 해당 챕터만)
  - objects: `## 리팩터링 과정` (나쁜 코드→좋은 코드 단계별 개선 테이블), `## 설계 원칙` (챕터별 OOP 원칙 테이블), `### 나쁜 설계`/`### 좋은 설계` (before/after 코드 대비), 클래스 다이어그램 (ASCII/유니코드 텍스트 기반), `>` 인용문 (저자 경험담/외부 인용, 레이블 없는 blockquote), `> **핵심 통찰**:` (핵심 인사이트 콜아웃), 코드 예제는 Java(`<details>` 접기)+TypeScript(펼침) 병기
  - the-software-craftsman: `>` 인용문 (산드로 만쿠소의 개인 경험담과 외부 명언, 레이블 없는 blockquote), `> **핵심 통찰**:` (핵심 인사이트 콜아웃), 비교 테이블 (좋은/나쁜 실행 관례, 채용 안티패턴 등), 커리어 관점의 서술 (개인·조직 두 축)
  - code-that-fits-in-your-head: `>` 인용문 (마크 시먼의 경험담과 외부 명언, Kent Beck·Robert Martin·Kevlin Henney·Adam Barr 등), `> **핵심 통찰**:` (핵심 인사이트 콜아웃), **C# 코드 예제** (레스토랑 예약 시스템 예제 코드베이스 일관 유지), 휴리스틱 관점 강조 (규칙이 아니라 상황에 따라 적용되는 지침), 인간 뇌 한계(단기 기억 7개, 순환 복잡도 7 이하)를 기준으로 한 정량적 임계값 강조
  - design-it-from-programmer-to-software-architect: `>` 인용문 (저자 마이클 킬링의 경험담과 외부 인용), `> **핵심 통찰**:` (핵심 인사이트 콜아웃), `> **직접 해보기**:` (실전 실습 안내 blockquote), `## N. 라이언하트 프로젝트 사례` 별도 섹션 (Ch1-13에서 사례 연구를 통일된 형태로 정리), Ch14-17은 다른 구조 — `## 활동 개요` 표 + 각 활동을 `## 활동 N: 활동명 (영문명)`으로 상세 정리(목적·참가자·소요 시간·준비물·실행 단계·지침과 팁)
- **용어 설명 스타일**: 부가 설명이 필요한 용어는 인라인 이탤릭으로 처리
  - 형식: `용어(*Term - 설명*)` (예: `테스트 스위트(*Test Suite - 프로젝트에 속한 모든 테스트의 집합*)`)
  - 용어가 처음 등장하는 곳에서 한 번만 설명하고, 이후에는 한국어 용어만 사용
- **파일 네이밍**: `ch{번호:두자리}-{영문-kebab-case}.md`

## Notion 업로드 규칙

마크다운 파일을 Notion에 업로드할 때는 **`notion-uploader` sub-agent** (`.claude/agents/notion-uploader.md`)를 사용한다.

- Sub-agent가 `model: sonnet`으로 자동 실행됨 (별도 모델 지정 불필요)
- 4개 챕터씩 묶어 병렬 sub-agent 실행 (예: 12개 챕터 → 3개 agent 동시)
- 각 sub-agent에는 파일 경로와 Notion 페이지 ID를 명시적으로 전달
- 업로드 후 일부 챕터를 샘플로 fetch하여 내용이 빠짐없이 올라갔는지 검증
- 파일 용량이 커서 sub-agent 업로드 실패 시, 메인 에이전트가 직접 `replace_content`로 원본을 업로드
- **원본 그대로 업로드 필수**: Notion에 업로드할 때 내용을 요약하거나 압축하지 않는다. 반드시 로컬 마크다운 파일의 원본 내용을 그대로 업로드해야 한다. 파일이 커서 한 번에 올릴 수 없으면 여러 번에 나눠서라도 원본 전체를 올린다. 사용자가 작성한 내용과 다른 것이 Notion에 올라가면 안 된다.
- **각주 변환**: `<sub>` 태그 각주는 Notion에서 렌더링되지 않으므로, 업로드 시 본문의 `용어¹` → `용어(*Term - 설명*)` 인라인 이탤릭 형태로 변환하고 `<sub>...</sub><br>` 각주 블록은 제거한다

## origin.md 파일 분리 작업

PDF에서 추출한 `origin.md` 원본 파일을 챕터별로 분리하는 작업. 내용 수정 없이 라인 기반으로 분할한다.

### 파일 네이밍 규칙

| 파일명 | 내용 |
|--------|------|
| `0.origin.md` | 서문, 대상 독자, 책 구성, 집필 동기, 감사의 글, 목차 등 앞부분 |
| `1.origin.md` ~ `N.origin.md` | 챕터 본문 (챕터 번호 = 파일 번호) |
| `N+1.origin.md` ~ | 부록 (내용이 있는 부록은 숫자 순서대로) |
| `99.origin.md` | 색인/찾아보기 (쓸모없는 부분) |

### 작업 절차

1. **구조 파악**: `Grep`으로 챕터 제목 패턴 검색 → 목차(TOC) vs 본문 시작 라인 구분
2. **경계 확인**: 각 챕터의 시작/끝 라인을 `Read`로 확인 (페이지 헤더/푸터 패턴 활용)
3. **분리**: `sed -n 'start,endp'`로 라인 범위별 추출
4. **검증**: 분리된 파일들의 `wc -l` 합계가 원본과 일치하는지 확인

### 완료된 분리 작업

- [x] `the-essence-of-object-orientation-객체지향의-사실과-오해/` (0~9, 99 = 11개 파일)
- [x] `essential-skills-for-junior-backend-developers-주니어-백엔드-개발자가-반드시-알아야-할-실무=-지식/` (0~14, 99 = 16개 파일)
- [x] `objects/` (0~19, 99 = 21개 파일)
- [x] `programmers-coding-test/` (0~18, 99 = 20개 파일) — 0=서문+00장, 1~16=01~16장, 17=부록 모의고사, 18=별책 정리노트, 99=찾아보기+판권
- [x] `design-it-from-programmer-to-software-architect/` (0~17, 18~19, 99 = 21개 파일) — 0=서문/목차, 1~17=Ch1~Ch17, 18=부록 기여자들, 19=참고문헌, 99=찾아보기
- [x] `the-software-craftsman/` (0~17 = 18개 파일) — 0=서문, 1~16=Ch1~Ch16, 17=Appendix A
- [x] `code-that-fits-in-your-head/` (0~19, 99 = 21개 파일) — 0=서문, 1~16=Ch1~Ch16, 17=부록A(프랙티스), 18=부록B(참고문헌), 19=부록C(빌드), 99=주석

---

## Notion 업로드용 마크다운 작성 규칙

로컬 마크다운을 Notion에 업로드했을 때 렌더링이 어긋나지 않도록 **로컬 파일 작성 단계부터** 지켜야 하는 규칙.

### 리스트 넘버링 규칙

코드 블록 내부에 `// ①` `// ②` 원문자 주석이 **있는지 없는지**에 따라 설명 리스트 형식을 분기한다.

**Case A — 코드에 `// ①` 마커 없음 → `1. 2. 3.` numbered list**
- 원문자가 임의 번호 역할만 하므로 표준 numbered list 사용
- ❌ 금지: `- ① 설명` (Notion에서 불릿 + 원문자 이중 마킹으로 보임)
- ✅ 사용: `1. 설명`

**Case B — 코드에 `// ①` 마커 있음 → 원문자 유지 필수**
- 코드 주석과 설명이 일대일 매칭되어야 하므로 리터럴 원문자 유지
- ✅ 사용: `- **① `code signature`**: 설명` 또는 `**①** `code`\n설명` 형식

**Case C — `> **참고**:` 안에 리스트가 들어가는 패턴 → 인용문 해체**
- Notion에서 인용문 안 리스트는 별개 블록으로 조각남
- 해결: 인용문(`>`)을 제거하고 일반 텍스트 + numbered list로 재구성

### 인용문 개행 규칙

**연속된 `>` 라인은 Notion에서 별개 인용 블록으로 조각난다.** 하나의 인용 블록 안에 여러 줄로 렌더링하려면 `<br>`로 명시적 병합 필수.

```md
❌ Notion에서 두 개의 별개 인용 블록으로 나옴
> 교회 첨탑 위의 풍향계가 강철로 만들어졌다 해도, ...
> — 하인리히 하이네(Heinrich Heine)

✅ 하나의 인용 블록에 두 줄로 렌더링
> 교회 첨탑 위의 풍향계가 강철로 만들어졌다 해도, ...<br>— 하인리히 하이네(Heinrich Heine)
```

**적용 대상 (isolated 인용 run)**:
- 챕터 여는 인용문 + 저자 표기 (`> 인용문<br>— 저자명`)
- 원칙/개념 정의 (`> **원칙명**<br>**정의 내용**`)
- 대화 시나리오 (`> 화자A: "..."<br>화자B: "..."<br>...`)
- 영문 원문 + 한국어 번역 병기 (`> English<br>한국어`)

**병합 예외 (그대로 유지)**:
- 콜아웃 라벨로 시작하는 인용문 (`> **핵심 통찰**:`, `> **Uncle Bob의 경험**:`, `> **Petzold의 비유**:`, `> **실무 팁**:`) — Notion 업로드 시 콜아웃 블록으로 별도 변환됨
- `>` 빈 줄이 포함된 multi-line 인용문 (콜아웃 내부 구조, 유스케이스 블록 등) — 자체 구조 보존 필요

**문단 구분이 필요한 경우**: `<br><br>` 사용
```md
> 첫 번째 문단<br><br>두 번째 문단<br><br>— 저자
```

### 인라인 코드 백틱 규칙

**인라인 코드 안에 백틱이 포함되는 경우** (예: 템플릿 리터럴 `` `${a}` ``, 스프레드 문자열 등)는 반드시 **더블 백틱(``)** 으로 감싼다.

```md
❌ 백틱 짝이 잘못 매칭되어 파싱 깨짐
예를 들면 `arr => arr.reduce((a, b) => `${a} ${b}`)`와 같은 형태

✅ 더블 백틱으로 감싸서 내부 단일 백틱 허용
예를 들면 ``arr => arr.reduce((a, b) => `${a} ${b}`)`` 와 같은 형태
```

**리터럴 백틱 문자를 인라인 코드로 표기**할 때도 더블 백틱 사용:
```md
✅ `` ` `` — 백틱 문자 한 개 표기
```

### 검증 도구

새 챕터 작성 후 다음 스크립트로 검증할 수 있다:

```python
# 1. Case A 위반 검사 (- ① 인데 위 코드에 // ① 없는 경우)
# 2. Case C 위반 검사 (> **참고**: 안에 - 리스트 있는 경우)
# 3. isolated 인용 run 병합 누락 검사
# 4. 백틱 짝 홀수 검사 (`` 를 placeholder로 치환 후 남은 ` 개수가 짝수인지)
```

---

## 작업 시 유의사항

- 각 챕터는 **책을 소유하지 않은 사람도 핵심 개념을 학습할 수 있을 정도로** 상세하게 작성
- 원서의 내용을 기반으로 하되, 이해를 돕기 위한 추가 코드 예시와 설명을 포함
- 새 책 작업 시 먼저 1~2 챕터 샘플을 만들어 사용자 확인 후 진행
