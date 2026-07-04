# Docker 완전 가이드

**Docker Deep Dive + Docker in Action** 범위를 커버하는 독자적 가이드 | 공식 문서 + Best Practice 기반

---

## 개요

이 가이드는 프론트엔드 개발자(Node.js/Next.js)의 관점에서 Docker를 체계적으로 다룬다. 컨테이너의 기본 개념부터 프로덕션 배포, 모노레포 전략, CI/CD 파이프라인까지 — 실무에서 마주치는 모든 Docker 시나리오를 다룬다.

### 특징

- 모든 예제는 **Node.js/Next.js** 기반으로 즉시 따라할 수 있게 작성
- Docker Deep Dive(Nigel Poulton)와 Docker in Action(Jeff Nickoloff)의 핵심 범위를 커버
- 공식 문서와 커뮤니티 best practice를 반영한 **자체 구성**

---

## 목차

### Part 1: 기초 — 컨테이너와 이미지 (Ch 01-04)

| 챕터 | 제목 | 핵심 주제 |
|------|------|----------|
| [Chapter 1](ch01-what-is-docker.md) | 도커란 무엇인가: What is Docker? | VM vs 컨테이너, Docker Engine 아키텍처(daemon, containerd, runc), OCI 표준 |
| [Chapter 2](ch02-images.md) | 이미지 — 컨테이너의 청사진: Images | 레이어 구조, Union FS, 레지스트리, 태그 vs 다이제스트, Node.js 베이스 이미지 비교 |
| [Chapter 3](ch03-containers.md) | 컨테이너 — 이미지의 실행 인스턴스: Containers | 생명주기, 네임스페이스, cgroups, PID 1 문제, 기본 명령어 |
| [Chapter 4](ch04-dockerfile-deep-dive.md) | Dockerfile 완전 정복: Dockerfile Deep Dive | 모든 인스트럭션, 멀티스테이지 빌드, BuildKit, 레이어 캐시, .dockerignore |

### Part 2: 개발 환경 (Ch 05-06)

| 챕터 | 제목 | 핵심 주제 |
|------|------|----------|
| [Chapter 5](ch05-volumes-and-bind-mounts.md) | 데이터 영속성과 바인드 마운트: Volumes and Bind Mounts | 볼륨 vs 바인드 마운트 vs tmpfs, node_modules 익명 볼륨 패턴, HMR 설정 |
| [Chapter 6](ch06-networking.md) | 컨테이너 네트워킹: Networking | bridge/host/overlay, DNS, 포트 매핑, 프론트-백엔드 컨테이너 간 통신 |

### Part 3: 다중 컨테이너 (Ch 07-08)

| 챕터 | 제목 | 핵심 주제 |
|------|------|----------|
| [Chapter 7](ch07-docker-compose.md) | 다중 컨테이너 애플리케이션: Docker Compose | compose.yaml 문법, services/networks/volumes, depends_on, watch 모드 |
| [Chapter 8](ch08-docker-compose-advanced-patterns.md) | Compose 고급 패턴: Docker Compose Advanced | 다중 파일 오버라이드, extends, dev/prod 분리, profiles |

### Part 4: 프로덕션과 보안 (Ch 09-11)

| 챕터 | 제목 | 핵심 주제 |
|------|------|----------|
| [Chapter 9](ch09-image-optimization.md) | 이미지 최적화: Image Optimization | 멀티스테이지 심화, distroless, docker scout/trivy, 이미지 크기 분석 |
| [Chapter 10](ch10-security.md) | 컨테이너 보안: Security | 비루트 실행, secrets, 읽기전용 FS, seccomp, NEXT_PUBLIC_* 보안 함의 |
| [Chapter 11](ch11-logging-monitoring-debugging.md) | 로깅, 모니터링, 디버깅: Logging, Monitoring & Debugging | 로깅 드라이버, docker stats, 헬스체크, OOM 진단, Node.js 메모리 설정 |

### Part 5: 프론트엔드 실전 (Ch 12-14)

| 챕터 | 제목 | 핵심 주제 |
|------|------|----------|
| [Chapter 12](ch12-nodejs-docker-best-practices.md) | Node.js + Docker 모범 사례: Node.js Docker Best Practices | pnpm/yarn/bun 캐시 전략, PID 1 + tini, SIGTERM, npm ci vs install |
| [Chapter 13](ch13-monorepo-docker-strategies.md) | 모노레포 Docker 전략: Monorepo Docker Strategies | turbo prune --docker, 멀티스테이지 pruning, Nx affected, 공유 패키지 |
| [Chapter 14](ch14-cicd-pipeline-with-docker.md) | Docker 기반 CI/CD 파이프라인: CI/CD Pipeline with Docker | GitHub Actions, 레이어 캐시, buildx 멀티플랫폼, GHCR/ECR, E2E in CI |

### Part 6: 너머 (Ch 15)

| 챕터 | 제목 | 핵심 주제 |
|------|------|----------|
| [Chapter 15](ch15-beyond-docker.md) | Docker 너머 — 컨테이너 오케스트레이션: Beyond Docker | K8s 핵심 개념, 서버리스 컨테이너(Fargate, Cloud Run, Fly.io), 셀프호스팅 Next.js |

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
