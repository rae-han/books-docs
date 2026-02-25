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
  - `## 다른 챕터와의 관계` — 관련 챕터 간 연결고리 설명
- **책별 특수 요소**: 각 책의 고유 개념에 맞는 요소 추가
  - philosophy-of-software-design: `## Red Flags` 섹션
  - legacy-code: 기법별 단계(Step) 정리
  - test-driven-development-by-example: `## TDD 사이클` (Red → Green → Refactor 단계별 코드), `## TODO 리스트` (Kent Beck 스타일 할 일 목록 추적)
  - structure-and-interpretation-of-computer-programs-javascript: `## 핵심 개념` (섹션에서 도입되는 중요 개념 정의), `## 주요 예제` (SICP 핵심 예제 코드와 상세 설명), `## 계산 모델` (치환 모델, 환경 모델 등 평가 모델 설명), `## 연습 문제 하이라이트` (유명한 연습 문제 소개/풀이)
  - the-clean-coder: `> **Uncle Bob의 경험**:` (저자의 실제 경험담 blockquote), `### 대화:` (PM-개발자 간 대화 시나리오), `## 실전 시나리오` (비프로 vs 프로 대응 대비), `## 프로의 원칙` (챕터별 원칙 테이블), `## 자기 점검` (체크리스트 형태 자기 반성 질문)
  - code-the-hidden-language: `> **Petzold의 비유**:` (저자의 직관적 비유 blockquote), `## 진리표` (논리 게이트/회로 진리표), `## 회로 구성` (텍스트 기반 회로 다이어그램), `## 단계별 구축` (이전 챕터 개념이 현재 챕터로 쌓이는 과정 테이블)
- **용어 설명 스타일**: 부가 설명이 필요한 용어는 인라인 이탤릭으로 처리
  - 형식: `용어(*Term — 설명*)` (예: `테스트 스위트(*Test Suite — 프로젝트에 속한 모든 테스트의 집합*)`)
  - 용어가 처음 등장하는 곳에서 한 번만 설명하고, 이후에는 한국어 용어만 사용
- **파일 네이밍**: `ch{번호:두자리}-{영문-kebab-case}.md`

## Notion 업로드 규칙

마크다운 파일을 Notion에 업로드할 때는 **`notion-uploader` sub-agent** (`.claude/agents/notion-uploader.md`)를 사용한다.

- Sub-agent가 `model: sonnet`으로 자동 실행됨 (별도 모델 지정 불필요)
- 4개 챕터씩 묶어 병렬 sub-agent 실행 (예: 12개 챕터 → 3개 agent 동시)
- 각 sub-agent에는 파일 경로와 Notion 페이지 ID를 명시적으로 전달
- 업로드 후 일부 챕터를 샘플로 fetch하여 내용이 빠짐없이 올라갔는지 검증
- 파일 용량이 커서 sub-agent 업로드 실패 시, 메인 에이전트가 직접 `replace_content`로 원본을 업로드
- **각주 변환**: `<sub>` 태그 각주는 Notion에서 렌더링되지 않으므로, 업로드 시 본문의 `용어¹` → `용어(*Term — 설명*)` 인라인 이탤릭 형태로 변환하고 `<sub>...</sub><br>` 각주 블록은 제거한다

## 작업 시 유의사항

- 각 챕터는 **책을 소유하지 않은 사람도 핵심 개념을 학습할 수 있을 정도로** 상세하게 작성
- 원서의 내용을 기반으로 하되, 이해를 돕기 위한 추가 코드 예시와 설명을 포함
- 새 책 작업 시 먼저 1~2 챕터 샘플을 만들어 사용자 확인 후 진행
