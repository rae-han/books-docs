# Docker 완전 가이드

**Docker Deep Dive + Docker in Action** 범위를 커버하는 독자적 가이드 | 공식 문서 + Best Practice 기반

---

## 개요

이 가이드는 프론트엔드 개발자(Node.js/Next.js)의 관점에서 Docker를 체계적으로 다룬다. 컨테이너의 기본 개념부터 프로덕션 배포, 모노레포 전략, CI/CD 파이프라인까지 - 실무에서 마주치는 모든 Docker 시나리오를 다룬다.

### 특징

- 모든 예제는 **Node.js/Next.js** 기반으로 즉시 따라할 수 있게 작성
- Docker Deep Dive(Nigel Poulton)와 Docker in Action(Jeff Nickoloff)의 핵심 범위를 커버
- 공식 문서와 커뮤니티 best practice를 반영한 **자체 구성**

---

## 목차

### Part 1: 기초 - 컨테이너와 이미지 (Ch 01-04)

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 1 | [도커란 무엇인가 (What is Docker?)](notes/ch01-what-is-docker.md) | VM vs 컨테이너, Docker Engine, containerd/runc, OCI | 가상 머신과의 차이부터 데몬 아키텍처까지 - 도커의 정체 |
| 2 | [이미지 - 컨테이너의 청사진 (Images)](notes/ch02-images.md) | 이미지 레이어, Union FS, 레지스트리, 태그/다이제스트 | 컨테이너의 청사진 - 레이어 구조와 Node.js 베이스 이미지 선택 |
| 3 | [컨테이너 - 이미지의 실행 인스턴스 (Containers)](notes/ch03-containers.md) | 컨테이너 생명주기, 네임스페이스, cgroups, PID 1 | 이미지의 실행 인스턴스 - 격리 원리와 기본 명령어 |
| 4 | [Dockerfile 완전 정복 (Dockerfile Deep Dive)](notes/ch04-dockerfile-deep-dive.md) | Dockerfile, 멀티스테이지 빌드, BuildKit, 레이어 캐시 | 모든 인스트럭션과 캐시 전략 - 멀티스테이지로 작고 빠르게 |

### Part 2: 개발 환경 (Ch 05-06)

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 5 | [데이터 영속성과 바인드 마운트 (Volumes and Bind Mounts)](notes/ch05-volumes-and-bind-mounts.md) | 볼륨, 바인드 마운트, node_modules 익명 볼륨, HMR | 데이터 영속성 3방식 비교 - 개발 환경 마운트 패턴 |
| 6 | [컨테이너 네트워킹 (Networking)](notes/ch06-networking.md) | bridge 네트워크, DNS, 포트 매핑 | 컨테이너를 잇는 네트워크 - 드라이버별 특성과 컨테이너 간 통신 |

### Part 3: 다중 컨테이너 (Ch 07-08)

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 7 | [다중 컨테이너 애플리케이션 (Docker Compose)](notes/ch07-docker-compose.md) | Docker Compose, compose.yaml, depends_on, watch 모드 | 다중 컨테이너를 선언형으로 - 서비스/네트워크/볼륨 정의 |
| 8 | [Compose 고급 패턴 (Docker Compose Advanced)](notes/ch08-docker-compose-advanced-patterns.md) | 다중 파일 오버라이드, extends, profiles | dev/prod 분리 - 오버라이드와 프로파일 패턴 |

### Part 4: 프로덕션과 보안 (Ch 09-11)

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 9 | [이미지 최적화 (Image Optimization)](notes/ch09-image-optimization.md) | distroless, docker scout, trivy, 이미지 크기 분석 | 더 작고 안전한 이미지 - 멀티스테이지 심화와 취약점 스캔 |
| 10 | [컨테이너 보안 (Security)](notes/ch10-security.md) | 비루트 실행, secrets, 읽기전용 FS, seccomp | 컨테이너 보안 계층 쌓기 - NEXT_PUBLIC_* 노출 함의까지 |
| 11 | [로깅, 모니터링, 디버깅 (Logging, Monitoring & Debugging)](notes/ch11-logging-monitoring-debugging.md) | 로깅 드라이버, 헬스체크, OOM 진단 | 운영 가시성 - docker stats·헬스체크·Node.js 메모리 설정 |

### Part 5: 프론트엔드 실전 (Ch 12-14)

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 12 | [Node.js + Docker 모범 사례 (Node.js Docker Best Practices)](notes/ch12-nodejs-docker-best-practices.md) | pnpm/yarn/bun 캐시, tini, SIGTERM, npm ci | Node.js 전용 베스트 프랙티스 - 신호 처리와 패키지 매니저 캐시 |
| 13 | [모노레포 Docker 전략 (Monorepo Docker Strategies)](notes/ch13-monorepo-docker-strategies.md) | turbo prune, 멀티스테이지 pruning, Nx affected | 모노레포에서 필요한 것만 빌드 - prune과 공유 패키지 전략 |
| 14 | [Docker 기반 CI/CD 파이프라인 (CI/CD Pipeline with Docker)](notes/ch14-cicd-pipeline-with-docker.md) | GitHub Actions, buildx, GHCR/ECR, 레이어 캐시 | 빌드→푸시→배포 자동화 - 캐시 전략과 멀티플랫폼 빌드 |

### Part 6: 너머 (Ch 15)

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 15 | [Docker 너머 - 컨테이너 오케스트레이션 (Beyond Docker)](notes/ch15-beyond-docker.md) | 쿠버네티스, 서버리스 컨테이너, Fargate/Cloud Run | 도커 다음 지형 - K8s 핵심 개념과 서버리스 컨테이너, 셀프호스팅 Next.js |

---

## 핸즈온 복습 노트

교재와 별도로, 직접 터미널에 명령어를 치고 Docker Desktop GUI로 확인하며 실습한 과정의 복습 노트가 있다.

- [핸즈온 Q&A & vs 비교 노트](notes/hands-on-qna-notes.md): 실습 중 **실제로 막혔던 지점과 던졌던 질문**을 정리한 자립형 노트. 세션별 흐름+교재 핵심(Part A), vs 비교 모음(Part B), Q&A(Part C), 누적 명령어 치트시트(Part D)로 구성되며, 실습 세션이 챕터 진도를 따라 추가된다. (현재 세션 0~4 = ch01~ch04)

---

## 핵심 개념 맵

```
이미지(Ch 2) ──build──→ Dockerfile(Ch 4)
    │                        │
    │ run                    │ 멀티스테이지
    ↓                        ↓
컨테이너(Ch 3) ←──── 최적화된 이미지(Ch 9)
    │
    ├── 볼륨/마운트(Ch 5) ── 데이터 영속성
    ├── 네트워크(Ch 6) ───── 컨테이너 간 통신
    └── Compose(Ch 7-8) ──── 다중 컨테이너 오케스트레이션
            │
            ├── 보안(Ch 10) + 모니터링(Ch 11)
            ├── Node.js 최적화(Ch 12) + 모노레포(Ch 13)
            └── CI/CD(Ch 14) → K8s/서버리스(Ch 15)
```

---

## 대상 독자

- Docker를 처음 접하거나 체계적으로 정리하고 싶은 **프론트엔드/풀스택 개발자**
- Node.js/Next.js 프로젝트를 컨테이너화하려는 개발자
- 모노레포 환경에서 Docker를 활용하려는 팀

## 사전 지식

- Node.js/npm 기본 사용법
- 터미널/CLI 기본 사용법
- Git 기본 워크플로

---

## Notion DB 구조

- **위치**: `Develop` → `Raehan's Must reads` → `Docker 완전 가이드` 페이지 안의 인라인 DB `Docker 완전 가이드`
  - 페이지: `31cde498-6fe3-8194-83b9-c30ae57764c8` / DB: `collection://e207a3f8-4978-4769-a82d-f34b18d93a69`
- **속성**: `Done`(checkbox), `Title`(title), `Chapter`(number), `Part`(select), `핵심 단어`(text), `핵심 요약`(text)
  - `핵심 단어`·`핵심 요약` 값의 소스는 위 [목차](#목차) 표다. 재업로드 시 이 표를 기준으로 채운다.
- **Part 딱지**: Part 1 기초 - 컨테이너와 이미지(파랑, Ch1-4) / Part 2 개발 환경(초록, Ch5-6) / Part 3 다중 컨테이너(보라, Ch7-8) / Part 4 프로덕션과 보안(주황, Ch9-11) / Part 5 프론트엔드 실전(빨강, Ch12-14) / Part 6 너머(회색, Ch15)
- **Title 형식**: `Chapter N: 한글 제목 (English Title)` - `Chapter` 오름차순 정렬로 순서 유지
- ⚠️ **한글은 리터럴 그대로 업로드**: `notion-create-pages`/`update-page`의 `content`에 `\uXXXX` 이스케이프를 손수 계산해 넣지 말 것(음절 손상 사례 다수). 업로드 후 1~2개 페이지를 `notion-fetch`로 열어 한글을 눈으로 확인한다.
- **이력**: 2026-08-01 Ch1~11이 DB에서 사라져(Ch12~15만 잔존) 로컬 마크다운 기준으로 전량 재업로드. 콜아웃(`> **핵심 통찰**:`/`> **실무 팁**:` → `::: callout {icon="💡" color="gray_bg"}`)과 마크다운 표(→ `<table header-row="true">`) 변환 후 생성.
