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
- 상태: **진행 중**

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
- **각주 스타일**: 부가 설명이 필요한 용어에는 `<sub>` 태그를 각주 형태로 사용
  - 본문에서: `용어¹`, `용어²` 형태로 번호 표시
  - 테이블/문단 아래에: `<sub>¹ 용어 — 설명</sub><br>` 형태로 각주 작성 (여러 각주 사이에 `<br>`로 줄바꿈)
- **파일 네이밍**: `ch{번호:두자리}-{영문-kebab-case}.md`

## 작업 시 유의사항

- 각 챕터는 **책을 소유하지 않은 사람도 핵심 개념을 학습할 수 있을 정도로** 상세하게 작성
- 원서의 내용을 기반으로 하되, 이해를 돕기 위한 추가 코드 예시와 설명을 포함
- 새 책 작업 시 먼저 1~2 챕터 샘플을 만들어 사용자 확인 후 진행
