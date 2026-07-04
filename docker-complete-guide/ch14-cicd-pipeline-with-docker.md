# Chapter 14: Docker 기반 CI/CD 파이프라인 — CI/CD Pipeline with Docker

## 핵심 질문

Docker를 CI/CD 파이프라인에 어떻게 통합하고, 빌드 시간을 어떻게 최적화하며, 멀티 플랫폼 이미지는 어떻게 빌드하는가?

---

## 1. CI/CD에서 Docker의 역할

### 빌드 환경 통일

CI/CD(*Continuous Integration / Continuous Delivery - 코드 변경을 자동으로 빌드·테스트·배포하는 파이프라인*)에서 Docker를 사용하는 가장 큰 이유는 **환경 통일**이다. CI 러너(*Runner - CI/CD 작업을 실행하는 서버 또는 컨테이너*)마다 Node.js 버전이 다르거나, 시스템 라이브러리가 누락되어 "CI에서만 실패하는" 문제가 흔히 발생한다. Docker를 사용하면 Dockerfile 하나로 빌드 환경을 완전히 고정할 수 있다.

```
로컬 개발 환경     →  동일한 Dockerfile  →  동일한 이미지
CI/CD 러너        →  동일한 Dockerfile  →  동일한 이미지
프로덕션 서버      →  동일한 Dockerfile  →  동일한 이미지
```

### Docker 기반 CI/CD 파이프라인 흐름

전형적인 Docker CI/CD 파이프라인은 다음 단계로 구성된다:

```
코드 푸시 → 이미지 빌드 → 테스트 실행 → 보안 스캔 → 레지스트리 푸시 → 배포
```

각 단계를 좀 더 구체적으로 살펴보면:

1. **코드 푸시**: 개발자가 Git에 코드를 푸시하면 CI가 트리거된다
2. **이미지 빌드**: Dockerfile을 기반으로 이미지를 빌드한다
3. **테스트 실행**: 빌드된 이미지 내에서 유닛 테스트, 통합 테스트를 실행한다
4. **보안 스캔**: 이미지의 취약점을 검사한다
5. **레지스트리 푸시**: 검증된 이미지를 컨테이너 레지스트리에 업로드한다
6. **배포**: 레지스트리에서 이미지를 가져와 프로덕션에 배포한다

### CI에서 Docker를 사용하는 두 가지 방식

#### Docker-in-Docker (DinD)

CI 컨테이너 **안에서** 별도의 Docker 데몬을 실행하는 방식이다. 완전히 격리된 Docker 환경을 제공하지만, 중첩 가상화로 인한 성능 오버헤드가 있다.

```yaml
# GitLab CI에서 DinD 사용 예시
services:
  - docker:dind

variables:
  DOCKER_HOST: tcp://docker:2376
  DOCKER_TLS_CERTDIR: "/certs"
```

- 장점: 완전한 격리, 보안적으로 안전
- 단점: 성능 오버헤드, 레이어 캐시가 작업 간 공유되지 않음

#### Docker Socket 마운트

호스트의 Docker 소켓(`/var/run/docker.sock`)을 CI 컨테이너에 마운트하여 **호스트의 Docker 데몬을 공유**하는 방식이다.

```bash
docker run -v /var/run/docker.sock:/var/run/docker.sock my-ci-image
```

- 장점: 빠른 성능, 호스트의 레이어 캐시 활용 가능
- 단점: 보안 위험 (컨테이너가 호스트의 모든 컨테이너에 접근 가능)

> **핵심 통찰**: GitHub Actions는 러너 자체가 VM이므로 Docker 소켓 마운트의 보안 문제가 비교적 적다. 하지만 self-hosted 러너에서는 DinD를 사용하는 것이 안전하다.

---

## 2. GitHub Actions에서 Docker 빌드

### 기본 워크플로우 구조

GitHub Actions에서 Docker 이미지를 빌드하고 푸시하는 워크플로우는 다음 단계로 구성된다:

1. **checkout**: 소스 코드를 체크아웃한다
2. **setup-buildx**: BuildKit 기반의 buildx를 설정한다
3. **login**: 컨테이너 레지스트리에 인증한다
4. **build-push**: 이미지를 빌드하고 푸시한다

### 핵심 Actions 소개

| Action | 역할 |
|--------|------|
| `actions/checkout@v4` | 리포지토리 소스 코드 체크아웃 |
| `docker/setup-buildx-action@v3` | BuildKit 빌더 인스턴스 생성 |
| `docker/login-action@v3` | 레지스트리 인증 |
| `docker/build-push-action@v6` | 이미지 빌드 및 푸시 |
| `docker/metadata-action@v5` | 태그·레이블 자동 생성 |
| `docker/setup-qemu-action@v3` | 멀티 플랫폼 빌드용 QEMU 설정 |

### 완전한 GitHub Actions 워크플로우 (Next.js)

```yaml
# .github/workflows/docker-build.yml
name: Build and Push Docker Image

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      # 1. 소스 코드 체크아웃
      - name: Checkout repository
        uses: actions/checkout@v4

      # 2. BuildKit 빌더 설정
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      # 3. 레지스트리 로그인 (PR에서는 스킵)
      - name: Log in to Container Registry
        if: github.event_name != 'pull_request'
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      # 4. 이미지 메타데이터 (태그, 레이블) 생성
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=sha
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=raw,value=latest,enable={{is_default_branch}}

      # 5. 이미지 빌드 및 푸시
      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: .
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

이 워크플로우의 핵심 포인트를 하나씩 살펴보면:

- **`permissions`**: GHCR에 푸시하려면 `packages: write` 권한이 필요하다
- **PR 분기**: `pull_request` 이벤트에서는 빌드만 하고 푸시는 하지 않는다. 이를 통해 PR에서 Dockerfile이 정상적으로 빌드되는지 검증할 수 있다
- **`cache-from/cache-to`**: GitHub Actions 캐시를 활용하여 빌드 시간을 대폭 단축한다 (다음 섹션에서 상세히 다룬다)

### docker/build-push-action 주요 옵션

```yaml
- uses: docker/build-push-action@v6
  with:
    context: .                    # 빌드 컨텍스트 경로
    file: ./Dockerfile.prod       # Dockerfile 경로 (기본: ./Dockerfile)
    push: true                    # 레지스트리에 푸시 여부
    tags: my-app:latest           # 이미지 태그
    build-args: |                 # 빌드 인수
      NODE_ENV=production
      API_URL=https://api.example.com
    target: runner                # 멀티스테이지 빌드의 타겟 스테이지
    platforms: linux/amd64,linux/arm64  # 멀티 플랫폼
    cache-from: type=gha          # 캐시 소스
    cache-to: type=gha,mode=max   # 캐시 저장
    secrets: |                    # 빌드 시크릿
      npm_token=${{ secrets.NPM_TOKEN }}
```

---

## 3. 레이어 캐시 전략

CI 환경에서 Docker 빌드의 가장 큰 병목은 **레이어 캐시의 부재**이다. 로컬에서는 이전 빌드의 레이어가 남아 있어 변경된 레이어만 다시 빌드하지만, CI 러너는 매번 깨끗한 환경에서 시작하므로 캐시가 없다. 이 문제를 해결하는 여러 캐시 전략이 존재한다.

### GitHub Actions Cache (`type=gha`)

GitHub Actions의 내장 캐시 서비스를 활용하는 방식이다. 설정이 가장 간편하고 GitHub Actions를 사용한다면 기본 선택지이다.

```yaml
- uses: docker/build-push-action@v6
  with:
    context: .
    push: true
    tags: my-app:latest
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

- `mode=max`: 최종 이미지에 포함되지 않는 중간 레이어까지 모두 캐시한다. 멀티스테이지 빌드에서 특히 중요하다.
- `mode=min` (기본값): 최종 이미지의 레이어만 캐시한다.

> **핵심 통찰**: `mode=max`를 사용하지 않으면 멀티스테이지 빌드의 builder 스테이지가 캐시되지 않아, `npm install`이 매번 처음부터 실행된다. 반드시 `mode=max`를 설정하라.

### Registry Cache (`type=registry`)

캐시를 컨테이너 레지스트리에 별도의 이미지로 저장하는 방식이다. CI 제공자를 변경하더라도 캐시를 유지할 수 있다.

```yaml
- uses: docker/build-push-action@v6
  with:
    context: .
    push: true
    tags: ghcr.io/my-org/my-app:latest
    cache-from: type=registry,ref=ghcr.io/my-org/my-app:buildcache
    cache-to: type=registry,ref=ghcr.io/my-org/my-app:buildcache,mode=max
```

### Local Cache (`type=local`)

캐시를 로컬 파일시스템에 저장하는 방식이다. self-hosted 러너처럼 디스크가 유지되는 환경에서 유용하다.

```yaml
- uses: docker/build-push-action@v6
  with:
    context: .
    push: true
    tags: my-app:latest
    cache-from: type=local,src=/tmp/.buildx-cache
    cache-to: type=local,dest=/tmp/.buildx-cache-new,mode=max

# 캐시가 무한히 쌓이지 않도록 교체
- name: Move cache
  run: |
    rm -rf /tmp/.buildx-cache
    mv /tmp/.buildx-cache-new /tmp/.buildx-cache
```

### 캐시 전략별 비교

| 전략 | 설정 난이도 | 속도 | CI 제공자 독립성 | 비용 |
|------|-----------|------|----------------|------|
| `type=gha` | 매우 쉬움 | 빠름 | GitHub Actions 전용 | 10GB 무료 캐시 포함 |
| `type=registry` | 보통 | 보통 (네트워크 의존) | 독립적 | 레지스트리 저장 비용 |
| `type=local` | 보통 | 매우 빠름 | 독립적 | 디스크 비용 |
| `type=s3` | 복잡 | 보통 | 독립적 | S3 비용 |

### 캐시 효과 극대화를 위한 Dockerfile 패턴

캐시 전략을 아무리 잘 설정해도 Dockerfile 자체가 캐시 친화적이지 않으면 효과가 없다. Ch 4에서 다룬 원칙을 CI 관점에서 다시 정리한다.

```dockerfile
# 나쁜 예: 코드 변경 시 npm install부터 다시 실행
FROM node:20-alpine AS builder
WORKDIR /app
COPY . .
RUN npm ci
RUN npm run build

# 좋은 예: package.json이 변경되지 않으면 npm ci를 캐시에서 가져옴
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build
```

이 패턴이 CI에서 특히 중요한 이유는, 대부분의 커밋이 소스 코드만 변경하고 `package.json`은 그대로이기 때문이다. 의존성 설치 레이어를 캐시하면 빌드 시간이 **2~5분에서 30초 이내**로 줄어들 수 있다.

---

## 4. 이미지 태그 전략

이미지 태그는 단순히 이름을 붙이는 것 이상의 의미를 가진다. 잘 설계된 태그 전략은 **추적성(traceability)**, **롤백 가능성**, **배포 자동화**의 기반이 된다.

### 태그 유형별 특성

| 태그 유형 | 예시 | 불변성 | 용도 |
|----------|------|--------|------|
| Git SHA | `abc1234` | 불변 | 정확한 커밋 추적 |
| Branch | `main`, `develop` | 가변 | 브랜치별 최신 빌드 |
| Semantic Version | `v1.2.3`, `1.2.3` | 불변 | 릴리스 버전 관리 |
| `latest` | `latest` | 가변 | 기본 브랜치의 최신 빌드 |
| PR 번호 | `pr-42` | 가변 | PR별 미리보기 환경 |

### docker/metadata-action으로 자동 태깅

수동으로 태그를 관리하면 실수가 잦다. `docker/metadata-action`을 사용하면 Git 이벤트에 따라 자동으로 태그를 생성할 수 있다.

```yaml
- name: Extract metadata
  id: meta
  uses: docker/metadata-action@v5
  with:
    images: ghcr.io/${{ github.repository }}
    tags: |
      # Git SHA 짧은 해시 (모든 이벤트)
      type=sha

      # 브랜치 이름 (push 이벤트)
      type=ref,event=branch

      # PR 번호 (pull_request 이벤트)
      type=ref,event=pr

      # Semantic Version (태그 push 이벤트)
      type=semver,pattern={{version}}
      type=semver,pattern={{major}}.{{minor}}
      type=semver,pattern={{major}}

      # latest (기본 브랜치에서만)
      type=raw,value=latest,enable={{is_default_branch}}

- name: Build and push
  uses: docker/build-push-action@v6
  with:
    context: .
    push: true
    tags: ${{ steps.meta.outputs.tags }}
    labels: ${{ steps.meta.outputs.labels }}
```

이 설정의 결과를 이벤트별로 살펴보면:

```
# main 브랜치에 push (커밋 SHA: abc1234)
ghcr.io/my-org/my-app:main
ghcr.io/my-org/my-app:sha-abc1234
ghcr.io/my-org/my-app:latest

# develop 브랜치에 push
ghcr.io/my-org/my-app:develop
ghcr.io/my-org/my-app:sha-def5678

# v1.2.3 태그 push
ghcr.io/my-org/my-app:1.2.3
ghcr.io/my-org/my-app:1.2
ghcr.io/my-org/my-app:1
ghcr.io/my-org/my-app:sha-ghi9012

# PR #42 생성
ghcr.io/my-org/my-app:pr-42
ghcr.io/my-org/my-app:sha-jkl3456
```

### 권장 태그 전략

프로덕션 환경에서는 **불변 태그**(Git SHA 또는 Semantic Version)로 배포하고, `latest`나 브랜치 태그는 개발/스테이징 환경에서만 사용하는 것이 좋다.

```
프로덕션 배포:  ghcr.io/my-org/my-app:sha-abc1234  (불변)
스테이징 배포:  ghcr.io/my-org/my-app:develop       (가변, 최신 develop)
릴리스:        ghcr.io/my-org/my-app:1.2.3          (불변)
```

> **핵심 통찰**: `latest` 태그만으로 프로덕션을 운영하면, 문제 발생 시 "어떤 커밋의 이미지가 배포되어 있는지" 알 수 없고, 이전 버전으로 롤백할 수도 없다. 반드시 불변 태그를 함께 사용하라.

---

## 5. 멀티 플랫폼 빌드 (buildx)

### 왜 멀티 플랫폼 빌드가 필요한가

현대 개발 환경에서는 다양한 CPU 아키텍처가 공존한다:

- **개발 환경**: Apple Silicon Mac (arm64), Intel Mac (amd64)
- **CI 러너**: 대부분 amd64 (GitHub Actions 기본)
- **프로덕션 서버**: amd64 (AWS EC2, GCE 등) 또는 arm64 (AWS Graviton)

M1/M2 Mac에서 빌드한 이미지를 amd64 서버에서 실행하면 `exec format error`가 발생한다. 멀티 플랫폼 빌드(*Multi-platform Build - 하나의 이미지 태그로 여러 아키텍처를 지원하는 빌드 방식*)를 사용하면 이 문제를 해결할 수 있다.

### 멀티 플랫폼 빌드의 원리

Docker 매니페스트 리스트(*Manifest List - 여러 플랫폼의 이미지를 하나의 태그로 묶는 메타데이터*)를 사용하여, `docker pull my-app:latest`를 실행하면 현재 시스템의 아키텍처에 맞는 이미지가 자동으로 선택된다.

```
my-app:latest (매니페스트 리스트)
├── linux/amd64  → sha256:aaa...  (Intel/AMD 서버용)
├── linux/arm64  → sha256:bbb...  (Apple Silicon / Graviton용)
└── linux/arm/v7 → sha256:ccc...  (Raspberry Pi용, 선택적)
```

### 로컬에서 멀티 플랫폼 빌드

```bash
# 빌더 인스턴스 생성 (최초 1회)
docker buildx create --name multiplatform --use

# 멀티 플랫폼 빌드 및 푸시
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag ghcr.io/my-org/my-app:latest \
  --push \
  .

# 빌더 상태 확인
docker buildx ls
```

주의할 점은, 멀티 플랫폼으로 빌드한 이미지는 `--push`나 `--load` 없이는 로컬에 저장되지 않는다. `--load`는 단일 플랫폼에서만 사용 가능하므로, 멀티 플랫폼 이미지는 레지스트리에 푸시해야 한다.

### QEMU 에뮬레이션 vs 네이티브 빌드

비네이티브 아키텍처용 빌드에는 QEMU(*Quick Emulator - CPU 아키텍처를 소프트웨어로 에뮬레이션하는 도구*) 에뮬레이션이 사용된다.

| 방식 | 속도 | 설정 복잡도 | 비용 |
|------|------|-----------|------|
| QEMU 에뮬레이션 | 네이티브 대비 3~10배 느림 | 낮음 | CI 러너 비용만 |
| 네이티브 빌드 (각 아키텍처별 러너) | 빠름 | 높음 | 러너 비용 x N |
| 병합 매니페스트 | 빠름 | 중간 | 러너 비용 x N |

### GitHub Actions에서 멀티 플랫폼 빌드

```yaml
name: Multi-platform Build

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      # QEMU 설정 (arm64 에뮬레이션용)
      - name: Set up QEMU
        uses: docker/setup-qemu-action@v3

      # Buildx 설정
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push (multi-platform)
        uses: docker/build-push-action@v6
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: true
          tags: ghcr.io/${{ github.repository }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### 빌드 시간 최적화: 플랫폼별 병렬 빌드

QEMU 에뮬레이션이 너무 느린 경우, 각 플랫폼을 별도의 작업으로 분리하고 마지막에 매니페스트를 병합하는 전략을 사용할 수 있다.

```yaml
name: Fast Multi-platform Build

on:
  push:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-amd64:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          context: .
          platforms: linux/amd64
          push: true
          tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:amd64
          cache-from: type=gha,scope=amd64
          cache-to: type=gha,scope=amd64,mode=max

  build-arm64:
    runs-on: ubuntu-latest  # 또는 arm64 러너 사용 가능
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-qemu-action@v3
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          context: .
          platforms: linux/arm64
          push: true
          tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:arm64
          cache-from: type=gha,scope=arm64
          cache-to: type=gha,scope=arm64,mode=max

  merge-manifests:
    needs: [build-amd64, build-arm64]
    runs-on: ubuntu-latest
    steps:
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - name: Create and push manifest
        run: |
          docker buildx imagetools create \
            --tag ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest \
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:amd64 \
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:arm64
```

이 방식은 두 플랫폼 빌드가 병렬로 실행되므로, 순차 빌드 대비 시간을 절반 가까이 줄일 수 있다.

---

## 6. 컨테이너 레지스트리

컨테이너 레지스트리(*Container Registry - Docker 이미지를 저장하고 배포하는 원격 저장소*)는 빌드된 이미지를 팀원 및 배포 환경에서 공유하기 위해 필수적이다.

### 주요 레지스트리 비교

| 레지스트리 | 무료 플랜 | 장점 | 단점 |
|-----------|----------|------|------|
| **GHCR** (GitHub Container Registry) | 공개 이미지 무료, 비공개 500MB | GitHub 통합, GITHUB_TOKEN 인증 | GitHub 생태계 한정 |
| **Docker Hub** | 1개 비공개 리포, 공개 무제한 | 가장 널리 사용, 기본 레지스트리 | Rate limit (익명 100pulls/6h) |
| **AWS ECR** | 프리 티어 500MB/12개월 | AWS 서비스 통합, IAM 인증 | AWS 종속 |
| **Google Artifact Registry** | 프리 티어 500MB | GCP 통합, 멀티 포맷 지원 | GCP 종속 |

### GHCR (GitHub Container Registry) 설정

GitHub Actions에서 가장 간편하게 사용할 수 있다. `GITHUB_TOKEN`만으로 인증이 완료된다.

```yaml
# GitHub Actions에서 GHCR 로그인
- uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

```bash
# 로컬에서 GHCR 로그인 (PAT 필요)
echo $GITHUB_PAT | docker login ghcr.io -u USERNAME --password-stdin

# 이미지 푸시
docker push ghcr.io/my-org/my-app:latest

# 이미지 풀
docker pull ghcr.io/my-org/my-app:latest
```

### AWS ECR 설정

```yaml
# GitHub Actions에서 AWS ECR 로그인
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    aws-region: ap-northeast-2

- name: Login to Amazon ECR
  id: login-ecr
  uses: aws-actions/amazon-ecr-login@v2

- name: Build and push
  uses: docker/build-push-action@v6
  with:
    context: .
    push: true
    tags: ${{ steps.login-ecr.outputs.registry }}/my-app:${{ github.sha }}
```

```bash
# 로컬에서 AWS ECR 로그인
aws ecr get-login-password --region ap-northeast-2 | \
  docker login --username AWS --password-stdin 123456789.dkr.ecr.ap-northeast-2.amazonaws.com
```

### Docker Hub 설정

```yaml
# GitHub Actions에서 Docker Hub 로그인
- uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_TOKEN }}
```

```bash
# 로컬에서 Docker Hub 로그인
docker login -u username

# 이미지 태깅 및 푸시
docker tag my-app:latest username/my-app:latest
docker push username/my-app:latest
```

---

## 7. CI에서 E2E 테스트

### Docker Compose로 테스트 환경 구성

E2E(*End-to-End - 사용자 관점에서 전체 시스템을 통합 테스트하는 방식*) 테스트는 데이터베이스, 외부 서비스 등 전체 스택이 필요하다. Docker Compose를 활용하면 CI에서도 완전한 테스트 환경을 구성할 수 있다.

```yaml
# docker-compose.test.yml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
      POSTGRES_DB: testdb
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U test"]
      interval: 5s
      timeout: 3s
      retries: 5

  app:
    build:
      context: .
      target: runner
    environment:
      DATABASE_URL: postgresql://test:test@db:5432/testdb
      NODE_ENV: test
    depends_on:
      db:
        condition: service_healthy
    ports:
      - "3000:3000"

  e2e:
    build:
      context: .
      dockerfile: Dockerfile.e2e
    environment:
      BASE_URL: http://app:3000
    depends_on:
      - app
```

```dockerfile
# Dockerfile.e2e — Playwright 테스트 러너
FROM mcr.microsoft.com/playwright:v1.48.0-noble

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .

CMD ["npx", "playwright", "test"]
```

### GitHub Actions에서 E2E 테스트 실행

```yaml
jobs:
  e2e-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run E2E tests
        run: |
          docker compose -f docker-compose.test.yml up \
            --build \
            --abort-on-container-exit \
            --exit-code-from e2e

      - name: Upload test report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-report
          path: playwright-report/

      - name: Cleanup
        if: always()
        run: docker compose -f docker-compose.test.yml down -v
```

핵심 옵션 설명:

- `--abort-on-container-exit`: 어떤 컨테이너든 종료되면 전체 스택을 중지한다
- `--exit-code-from e2e`: `e2e` 서비스의 종료 코드를 CI의 종료 코드로 사용한다. 테스트 실패 시 CI도 실패한다

### GitHub Actions Service Containers

Docker Compose 대신 GitHub Actions의 서비스 컨테이너(*Service Container - GitHub Actions 작업에서 자동으로 관리되는 보조 컨테이너*)를 사용할 수도 있다.

```yaml
jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: testdb
        ports:
          - 5432:5432
        options: >-
          --health-cmd "pg_isready -U test"
          --health-interval 5s
          --health-timeout 3s
          --health-retries 5

      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 5s
          --health-timeout 3s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm

      - name: Install dependencies
        run: npm ci

      - name: Run integration tests
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/testdb
          REDIS_URL: redis://localhost:6379
        run: npm run test:integration
```

서비스 컨테이너는 Docker Compose보다 간편하지만, 앱 자체는 컨테이너가 아닌 러너에서 직접 실행된다. 앱도 컨테이너로 실행해야 하는 경우에는 Docker Compose를 사용하라.

---

## 8. CI에서 보안 스캔 통합

### Trivy를 GitHub Actions에 통합

Trivy(*Trivy - Aqua Security가 개발한 오픈소스 컨테이너 이미지 취약점 스캐너*)를 CI 파이프라인에 통합하면 취약한 이미지가 프로덕션에 배포되는 것을 방지할 수 있다.

```yaml
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build image for scanning
        uses: docker/build-push-action@v6
        with:
          context: .
          load: true  # 로컬에 로드 (푸시하지 않음)
          tags: my-app:scan

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: my-app:scan
          format: sarif
          output: trivy-results.sarif
          severity: CRITICAL,HIGH
          exit-code: 1  # 취약점 발견 시 CI 실패

      # GitHub Security 탭에 결과 표시
      - name: Upload Trivy scan results to GitHub Security
        if: always()
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: trivy-results.sarif
```

이 워크플로우의 흐름:

1. 이미지를 빌드하되 레지스트리에 푸시하지 않고 로컬에 로드한다 (`load: true`)
2. Trivy로 이미지를 스캔한다
3. CRITICAL 또는 HIGH 취약점이 발견되면 CI를 실패시킨다 (`exit-code: 1`)
4. 결과를 SARIF(*Static Analysis Results Interchange Format - 정적 분석 결과 교환 형식*) 포맷으로 GitHub Security 탭에 업로드한다

### Docker Scout 통합

```yaml
- name: Docker Scout scan
  uses: docker/scout-action@v1
  with:
    command: cves
    image: my-app:scan
    sarif-file: scout-results.sarif
    only-severities: critical,high
```

### 스캔을 빌드-푸시 파이프라인에 통합하기

보안 스캔은 이미지 **푸시 전에** 실행해야 한다. 전형적인 패턴은 다음과 같다:

```
빌드 (load) → 스캔 → [통과] → 푸시
                   → [실패] → CI 실패, 푸시하지 않음
```

```yaml
jobs:
  build-scan-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3

      # 1. 빌드 (로컬에만 로드)
      - name: Build image
        uses: docker/build-push-action@v6
        with:
          context: .
          load: true
          tags: my-app:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      # 2. 보안 스캔
      - name: Security scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: my-app:${{ github.sha }}
          severity: CRITICAL,HIGH
          exit-code: 1

      # 3. 스캔 통과 시에만 푸시
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Push image
        run: |
          docker tag my-app:${{ github.sha }} ghcr.io/${{ github.repository }}:${{ github.sha }}
          docker push ghcr.io/${{ github.repository }}:${{ github.sha }}
```

---

## 9. 완전한 프로덕션 CI/CD 워크플로우

지금까지의 모든 개념을 결합하여, Next.js 프로젝트의 프로덕션 CI/CD 파이프라인을 구성한다.

### 전체 파이프라인 구조

```
PR 생성/업데이트:  lint → test → build(검증만)
main 브랜치 push: lint → test → build → scan → push → deploy(staging)
태그 push:        lint → test → build → scan → push → deploy(production)
```

### 완전한 워크플로우 파일

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main]
    tags: ["v*"]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  # ───────────────────────────────────────────────
  # 1단계: 린트 및 타입 체크
  # ───────────────────────────────────────────────
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run lint
      - run: npm run type-check

  # ───────────────────────────────────────────────
  # 2단계: 유닛 테스트
  # ───────────────────────────────────────────────
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: testdb
        ports:
          - 5432:5432
        options: >-
          --health-cmd "pg_isready -U test"
          --health-interval 5s
          --health-timeout 3s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run test:ci
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/testdb

  # ───────────────────────────────────────────────
  # 3단계: Docker 이미지 빌드 및 스캔
  # ───────────────────────────────────────────────
  build:
    needs: [lint, test]
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
      security-events: write
    outputs:
      image-tag: ${{ steps.meta.outputs.version }}
      image-digest: ${{ steps.build.outputs.digest }}

    steps:
      - uses: actions/checkout@v4

      - name: Set up QEMU
        uses: docker/setup-qemu-action@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=sha
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=raw,value=latest,enable={{is_default_branch}}

      # PR에서는 amd64만, main/태그에서는 멀티 플랫폼
      - name: Determine platforms
        id: platforms
        run: |
          if [ "${{ github.event_name }}" = "pull_request" ]; then
            echo "platforms=linux/amd64" >> $GITHUB_OUTPUT
          else
            echo "platforms=linux/amd64,linux/arm64" >> $GITHUB_OUTPUT
          fi

      - name: Log in to Container Registry
        if: github.event_name != 'pull_request'
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      # 스캔용으로 먼저 amd64만 로컬에 빌드
      - name: Build for scanning
        uses: docker/build-push-action@v6
        with:
          context: .
          load: true
          tags: ${{ env.IMAGE_NAME }}:scan
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ env.IMAGE_NAME }}:scan
          format: sarif
          output: trivy-results.sarif
          severity: CRITICAL,HIGH
          exit-code: 1

      - name: Upload scan results to GitHub Security
        if: always()
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: trivy-results.sarif

      # 스캔 통과 후 멀티 플랫폼 빌드 및 푸시
      - name: Build and push
        id: build
        if: github.event_name != 'pull_request'
        uses: docker/build-push-action@v6
        with:
          context: .
          platforms: ${{ steps.platforms.outputs.platforms }}
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # ───────────────────────────────────────────────
  # 4단계: 스테이징 배포 (main 브랜치)
  # ───────────────────────────────────────────────
  deploy-staging:
    needs: [build]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - name: Deploy to staging
        run: |
          echo "Deploying ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:sha-${GITHUB_SHA::7} to staging"
          # 실제 배포 명령 (예: kubectl set image, AWS ECS update-service 등)

  # ───────────────────────────────────────────────
  # 5단계: 프로덕션 배포 (태그 push)
  # ───────────────────────────────────────────────
  deploy-production:
    needs: [build]
    if: startsWith(github.ref, 'refs/tags/v')
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Deploy to production
        run: |
          echo "Deploying ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ needs.build.outputs.image-tag }} to production"
          # 실제 배포 명령
```

### 워크플로우 핵심 설계 결정

**`concurrency` 설정**: 동일한 브랜치/PR에서 새 커밋이 푸시되면 이전 실행을 취소한다. 불필요한 빌드를 방지하여 CI 비용을 절감한다.

**환경별 분기**: `github.ref`를 기반으로 스테이징과 프로덕션을 분기한다. `environment` 키워드를 사용하면 GitHub에서 수동 승인 게이트를 설정할 수도 있다.

**PR에서의 빌드 검증**: PR에서는 이미지를 빌드만 하고 푸시하지 않는다. Dockerfile이 정상적으로 빌드되는지, 보안 취약점은 없는지 검증하는 것이 목적이다.

### 롤백 전략

불변 태그(Git SHA)로 배포하면 롤백이 간단하다:

```bash
# 현재 배포된 이미지 확인
kubectl get deployment my-app -o jsonpath='{.spec.template.spec.containers[0].image}'
# 출력: ghcr.io/my-org/my-app:sha-abc1234

# 이전 버전으로 롤백
kubectl set image deployment/my-app \
  my-app=ghcr.io/my-org/my-app:sha-prev789

# 또는 Kubernetes rollout 사용
kubectl rollout undo deployment/my-app
```

이미지가 레지스트리에 남아 있으므로, 어떤 커밋의 이미지로든 즉시 롤백할 수 있다. 이것이 불변 태그를 사용해야 하는 가장 중요한 이유이다.

---

## 자주 하는 실수

### 1. 캐시를 설정하지 않아 매번 전체 빌드

```yaml
# 나쁜 예: 캐시 없음 — 매번 npm ci부터 전체 빌드
- uses: docker/build-push-action@v6
  with:
    context: .
    push: true
    tags: my-app:latest

# 좋은 예: GHA 캐시 활용
- uses: docker/build-push-action@v6
  with:
    context: .
    push: true
    tags: my-app:latest
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

### 2. `latest` 태그만 사용하여 롤백 불가

```yaml
# 나쁜 예: latest만 존재
tags: ghcr.io/my-org/my-app:latest

# 좋은 예: 불변 태그와 latest 병행
tags: |
  ghcr.io/my-org/my-app:sha-${{ github.sha }}
  ghcr.io/my-org/my-app:latest
```

### 3. 보안 스캔 없이 바로 푸시

취약점이 있는 이미지가 프로덕션에 배포될 수 있다. 반드시 푸시 전에 스캔 단계를 추가하라.

### 4. 멀티 플랫폼을 고려하지 않음

M1/M2 Mac에서 빌드한 이미지를 amd64 CI 또는 서버에서 실행하면 `exec format error`가 발생한다. `--platform linux/amd64`를 명시하거나 멀티 플랫폼 빌드를 설정하라.

### 5. Secrets를 워크플로우 파일에 하드코딩

```yaml
# 절대 하지 말 것
env:
  AWS_ACCESS_KEY_ID: AKIAIOSFODNN7EXAMPLE
  AWS_SECRET_ACCESS_KEY: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

# 올바른 방법: GitHub Secrets 사용
env:
  AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
  AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

### 6. `cache-to`에서 `mode=max`를 빠뜨림

```yaml
# 나쁜 예: 멀티스테이지 빌드의 중간 레이어가 캐시되지 않음
cache-to: type=gha

# 좋은 예: 모든 레이어 캐시
cache-to: type=gha,mode=max
```

---

## 명령어 레퍼런스

| 명령어 | 설명 | 예시 |
|--------|------|------|
| `docker buildx build` | BuildKit으로 이미지 빌드 | `docker buildx build --platform linux/amd64,linux/arm64 -t my-app .` |
| `docker buildx create` | 빌더 인스턴스 생성 | `docker buildx create --name mybuilder --use` |
| `docker buildx ls` | 빌더 인스턴스 목록 | `docker buildx ls` |
| `docker buildx imagetools create` | 매니페스트 리스트 생성 | `docker buildx imagetools create -t my-app:latest my-app:amd64 my-app:arm64` |
| `docker buildx imagetools inspect` | 매니페스트 리스트 확인 | `docker buildx imagetools inspect my-app:latest` |
| `docker login` | 레지스트리 인증 | `docker login ghcr.io -u username` |
| `docker push` | 이미지 푸시 | `docker push ghcr.io/my-org/my-app:latest` |
| `docker pull` | 이미지 풀 | `docker pull ghcr.io/my-org/my-app:latest` |
| `docker tag` | 이미지 태그 추가 | `docker tag my-app:latest ghcr.io/my-org/my-app:v1.0.0` |

---

## 요약

- **환경 통일**: Docker를 CI/CD에 사용하면 "로컬에서는 되는데 CI에서 안 되는" 문제를 근본적으로 해결한다
- **GitHub Actions 통합**: `docker/build-push-action`과 관련 Actions를 조합하면 빌드·태깅·캐싱·푸시를 선언적으로 구성할 수 있다
- **레이어 캐시**: CI에서 `type=gha`와 `mode=max`를 설정하면 빌드 시간을 수 분에서 수십 초로 단축할 수 있다
- **태그 전략**: 불변 태그(Git SHA, Semantic Version)로 프로덕션을 배포하고, `docker/metadata-action`으로 자동화한다
- **멀티 플랫폼**: `docker buildx`와 QEMU를 사용하면 하나의 CI 파이프라인에서 amd64/arm64 이미지를 동시에 빌드할 수 있다
- **보안 스캔**: Trivy 등의 스캐너를 푸시 **전에** 실행하여 취약한 이미지가 배포되는 것을 방지한다
- **E2E 테스트**: Docker Compose 또는 Service Containers로 CI에서 완전한 테스트 환경을 구성할 수 있다
- **프로덕션 파이프라인**: lint → test → build → scan → push → deploy 순서로 구성하되, PR/main/태그에 따라 분기한다

---

## 다른 챕터와의 관계

- **Ch 4 (BuildKit과 캐시)**: CI에서의 `cache-from`/`cache-to` 전략은 BuildKit의 캐시 메커니즘을 기반으로 한다. Dockerfile의 레이어 순서 최적화가 CI 캐시 효과에 직접적인 영향을 준다
- **Ch 9 (이미지 최적화)**: 작은 이미지는 빌드·푸시·풀 시간을 줄여 CI/CD 파이프라인 전체를 빠르게 만든다. 멀티스테이지 빌드로 최적화된 이미지가 CI에서도 캐시 효율이 높다
- **Ch 10 (보안 스캔)**: 이 챕터에서 소개한 Trivy/Scout 스캔은 Ch 10에서 다룬 보안 원칙을 자동화한 것이다
- **Ch 13 (모노레포)**: 모노레포에서는 변경된 패키지만 빌드하는 조건부 CI가 필요하다. `paths` 필터와 빌드 매트릭스를 결합하여 효율적인 파이프라인을 구성한다
- **Ch 15 (배포)**: 이 챕터의 CI/CD 파이프라인이 만든 이미지가 Ch 15에서 다루는 Kubernetes, AWS ECS 등의 배포 대상으로 전달된다
