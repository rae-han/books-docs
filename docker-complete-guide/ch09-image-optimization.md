# Chapter 9: Image Optimization (이미지 최적화)

## 핵심 질문

프로덕션 이미지를 어떻게 최소화하고, 보안 취약점을 사전에 발견하며, 빌드 속도를 극대화하는가?

---

## 1. 이미지 크기가 중요한 이유

Docker 이미지의 크기는 단순한 디스크 공간 문제가 아니다. 이미지 크기는 배포 속도, 보안, 비용, CI/CD 파이프라인 전체에 직접적인 영향을 미친다.

### 배포 속도

컨테이너를 새로 시작할 때 가장 먼저 일어나는 일은 이미지 풀(*Image Pull - 레지스트리에서 이미지를 다운로드하는 과정*)이다. 이미지가 작을수록 풀 시간이 단축되고, 이는 곧 다음을 의미한다:

- **스케일아웃 속도 향상**: 트래픽 급증 시 새 인스턴스를 빠르게 띄울 수 있다
- **롤백 시간 단축**: 문제 발생 시 이전 버전으로 빠르게 되돌릴 수 있다
- **콜드 스타트 최소화**: Kubernetes 등 오케스트레이터에서 노드에 이미지가 없는 경우의 지연을 줄인다

| 이미지 크기 | 1Gbps 네트워크 풀 시간 | 100Mbps 네트워크 풀 시간 |
|-------------|----------------------|------------------------|
| 1.2GB       | ~10초               | ~96초                  |
| 300MB       | ~2.4초              | ~24초                  |
| 150MB       | ~1.2초              | ~12초                  |
| 50MB        | ~0.4초              | ~4초                   |

### 보안: 공격 표면 감소

이미지에 포함된 패키지가 많을수록 공격 표면(*Attack Surface - 공격자가 악용할 수 있는 시스템의 노출 지점 총합*)이 넓어진다. `node:20` 이미지에는 `curl`, `wget`, `bash`, `apt` 등 수백 개의 시스템 도구가 포함되어 있다. 공격자가 컨테이너에 침투했을 때 이런 도구들을 활용해 추가적인 공격을 수행할 수 있다.

```bash
# node:20 이미지에 포함된 바이너리 수 확인
docker run --rm node:20 sh -c 'find /usr/bin /usr/sbin -type f | wc -l'
# 결과: ~300개 이상

# distroless 이미지는 Node.js 런타임만 포함
# 셸조차 없으므로 위 명령을 실행할 수 없다
```

### 비용

- **레지스트리 저장 비용**: ECR, GCR, Docker Hub 등 모든 레지스트리는 저장 용량에 따라 과금한다
- **네트워크 전송 비용**: 클라우드 환경에서 리전 간 이미지 전송은 데이터 전송 요금이 발생한다
- **CI/CD 러너 비용**: 빌드 시간이 길어지면 GitHub Actions 분 단위 과금, 자체 호스팅 러너의 점유 시간이 증가한다

### CI/CD 파이프라인 영향

```
빌드(Build) → 푸시(Push) → 풀(Pull) → 배포(Deploy)
   ↑              ↑            ↑
   캐시 효율      이미지 크기    이미지 크기
```

이미지 최적화는 이 파이프라인의 모든 단계에 영향을 미친다. 특히 하루에 수십 번 배포하는 환경에서는 1분의 단축이 누적되어 큰 차이를 만든다.

---

## 2. 멀티스테이지 빌드 심화

Ch 4에서 멀티스테이지 빌드의 기본 개념을 다뤘다. 이 섹션에서는 프로덕션 환경에서 실제로 사용하는 심화 패턴을 다룬다.

### 3단계 패턴: deps → builder → runner

프로덕션 Node.js/Next.js 앱의 표준 멀티스테이지 패턴은 3단계로 구성된다.

```dockerfile
# ============================================
# Stage 1: deps — 의존성 설치
# ============================================
FROM node:20-alpine AS deps

WORKDIR /app

# 패키지 매니저 락파일만 먼저 복사하여 캐시 활용 극대화
COPY package.json package-lock.json ./

# 프로덕션 + 개발 의존성 모두 설치 (빌드에 devDependencies 필요)
RUN npm ci

# ============================================
# Stage 2: builder — 애플리케이션 빌드
# ============================================
FROM node:20-alpine AS builder

WORKDIR /app

# deps 스테이지에서 node_modules 복사
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Next.js 빌드
RUN npm run build

# ============================================
# Stage 3: runner — 프로덕션 실행
# ============================================
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

# 보안: 비root 사용자 생성 및 사용
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# 빌드 결과물만 복사
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

USER nextjs

EXPOSE 3000

CMD ["npm", "start"]
```

각 스테이지의 역할:

| 스테이지 | 목적 | 포함 내용 |
|---------|------|----------|
| `deps` | 의존성 설치 전용 | package.json, lock 파일, node_modules |
| `builder` | 빌드 수행 | 소스 코드 + node_modules → 빌드 산출물 |
| `runner` | 프로덕션 실행 | 빌드 산출물 + 프로덕션 의존성만 |

> **핵심 통찰**: `deps`를 별도 스테이지로 분리하면 소스 코드가 변경되어도 `package.json`이 동일하면 의존성 설치 캐시가 유지된다. 이것이 빌드 속도의 핵심이다.

### Next.js standalone 모드 활용

Next.js는 `output: 'standalone'` 설정을 통해 프로덕션에 필요한 파일만 추출할 수 있다. 이 모드는 `node_modules`에서 실제로 사용되는 파일만 트레이싱(*Tracing - 런타임에 실제로 import되는 파일을 추적하는 과정*)하여 복사한다.

```typescript
// next.config.ts
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  output: 'standalone',
};

export default nextConfig;
```

standalone 모드를 활용한 최적화된 Dockerfile:

```dockerfile
# Stage 1: deps
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# Stage 2: builder
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Stage 3: runner — standalone 활용
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# standalone 산출물만 복사 (node_modules 전체가 아님!)
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

USER nextjs

EXPOSE 3000

# standalone 모드는 자체 서버를 포함
CMD ["node", "server.js"]
```

### 이미지 크기 비교

동일한 Next.js 앱을 다른 전략으로 빌드했을 때의 이미지 크기 비교:

| 전략 | 베이스 이미지 | 이미지 크기 | 비고 |
|-----|-------------|-----------|------|
| 단일 스테이지 | node:20 | ~1.2GB | devDependencies 포함, Debian 풀 이미지 |
| 멀티스테이지 (기본) | node:20-alpine | ~350MB | node_modules 전체 복사 |
| 멀티스테이지 + standalone | node:20-alpine | ~150MB | 필요한 파일만 트레이싱 |
| 멀티스테이지 + standalone + distroless | distroless/nodejs20 | ~130MB | 최소 런타임 |

### turbo prune --docker를 활용한 모노레포 최적화

Turborepo(*Turbo - Vercel이 관리하는 모노레포 빌드 시스템*)를 사용하는 모노레포 환경에서는 `turbo prune`으로 특정 패키지와 그 의존성만 추출할 수 있다. 이는 Ch 13에서 자세히 다루지만, 이미지 최적화 관점에서 미리 살펴본다.

```dockerfile
# Stage 1: 모노레포에서 필요한 패키지만 추출
FROM node:20-alpine AS pruner
WORKDIR /app

RUN npm install -g turbo
COPY . .

# web 앱과 그 의존성만 추출
RUN turbo prune web --docker

# Stage 2: 추출된 패키지의 의존성만 설치
FROM node:20-alpine AS deps
WORKDIR /app

# prune 결과의 lock 파일과 package.json만 복사
COPY --from=pruner /app/out/json/ .
COPY --from=pruner /app/out/package-lock.json ./package-lock.json
RUN npm ci

# Stage 3: 빌드
FROM node:20-alpine AS builder
WORKDIR /app

COPY --from=deps /app/ .
COPY --from=pruner /app/out/full/ .
RUN npx turbo run build --filter=web

# Stage 4: runner
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
COPY --from=builder /app/apps/web/.next/standalone ./
COPY --from=builder /app/apps/web/.next/static ./.next/static
COPY --from=builder /app/apps/web/public ./public

CMD ["node", "server.js"]
```

`turbo prune --docker`는 두 가지 디렉터리를 생성한다:
- `out/json/` — `package.json`과 락 파일만 포함 (의존성 설치용, 캐시 최적화)
- `out/full/` — 실제 소스 코드 포함

---

## 3. 경량 베이스 이미지 선택

베이스 이미지 선택은 이미지 최적화의 가장 기본적이면서도 효과가 큰 단계다.

### Alpine Linux

Alpine은 musl libc(*musl - glibc의 경량 대안으로, 정적 링킹에 최적화된 C 표준 라이브러리 구현체*)를 기반으로 한 초경량 Linux 배포판이다.

```dockerfile
FROM node:20-alpine

# Alpine은 apk 패키지 매니저 사용
RUN apk add --no-cache python3 make g++
```

- **장점**: ~5MB 베이스 크기, 빠른 풀, 넓은 커뮤니티 지원
- **단점**: musl libc로 인해 일부 네이티브 모듈(bcrypt, sharp 등)에서 호환성 문제 발생 가능
- **주의**: `--no-cache` 플래그를 사용하여 apk 캐시가 이미지에 남지 않도록 해야 한다

### Debian Slim

Debian Slim은 glibc 기반의 경량 Debian 변형이다. 풀 Debian 이미지에서 문서, man 페이지, 불필요한 도구를 제거한 버전이다.

```dockerfile
FROM node:20-slim

# Debian Slim은 apt 패키지 매니저 사용
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 make g++ \
    && rm -rf /var/lib/apt/lists/*
```

- **장점**: glibc 기반으로 네이티브 모듈 호환성이 높다, ~80MB
- **단점**: Alpine보다 크다
- **주의**: `--no-install-recommends`로 불필요한 추천 패키지 설치 방지, `rm -rf /var/lib/apt/lists/*`로 apt 캐시 삭제

### Distroless

Distroless(*Distroless - Google이 관리하는, 애플리케이션 런타임만 포함하고 OS 도구를 제거한 컨테이너 이미지*)는 Docker 이미지 최적화의 극한이다. 셸, 패키지 매니저, 기타 OS 유틸리티가 전혀 포함되지 않는다.

```dockerfile
# 빌드 스테이지
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# 프로덕션 스테이지: Distroless 사용
FROM gcr.io/distroless/nodejs20-debian12 AS runner
WORKDIR /app

COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000

# Distroless는 ENTRYPOINT가 node로 설정되어 있음
CMD ["server.js"]
```

**Distroless의 장점**:
- 최소 공격 표면: 셸이 없으므로 `docker exec sh`로 침투 불가
- CVE 감소: 포함된 패키지가 극소수이므로 취약점 자체가 적다
- 규정 준수: 보안 감사에서 유리하다

**Distroless의 단점**:
- 디버깅이 매우 어렵다. 컨테이너에 셸로 접속할 수 없다
- `RUN` 명령을 사용할 수 없다 (셸이 없으므로). 빌드 스테이지에서 모든 작업을 완료해야 한다
- 파일 권한 설정 등 OS 레벨 작업이 제한된다

**디버그 변형**: 디버깅이 필요한 상황을 위해 `debug` 태그가 제공된다.

```bash
# 프로덕션: 셸 없는 이미지
docker run gcr.io/distroless/nodejs20-debian12

# 디버깅: busybox 셸 포함 이미지
docker run -it gcr.io/distroless/nodejs20-debian12:debug sh
```

### Chainguard Images

Chainguard Images는 Distroless의 대안으로, wolfi(*Wolfi - Chainguard가 개발한 컨테이너 전용 Linux 언디스트로*)를 기반으로 한다. Distroless와 유사하게 최소한의 패키지만 포함하지만, apk 패키지 매니저를 통한 추가 설치가 가능하다.

```dockerfile
FROM cgr.dev/chainguard/node:latest

WORKDIR /app
COPY --from=builder /app/.next/standalone ./
CMD ["server.js"]
```

### 선택 가이드

```
베이스 이미지 선택 플로우:

네이티브 모듈(bcrypt, sharp 등) 사용?
├─ Yes → glibc 필요
│   ├─ 최소 크기 우선 → Distroless (nodejs20-debian12)
│   └─ 디버깅 편의 우선 → node:20-slim
└─ No
    ├─ 최소 크기 우선 → Distroless 또는 Alpine
    └─ 범용성 우선 → node:20-alpine
```

| 베이스 이미지 | 크기 | 셸 | 패키지 매니저 | glibc | CVE 수 (평균) |
|-------------|------|-----|-------------|-------|--------------|
| node:20 | ~1.1GB | O | apt | O | 200+ |
| node:20-slim | ~200MB | O | apt | O | 50~100 |
| node:20-alpine | ~130MB | O | apk | X (musl) | 10~30 |
| distroless/nodejs20 | ~120MB | X | X | O | 0~5 |
| chainguard/node | ~110MB | X | X | O | 0~3 |

---

## 4. 레이어 크기 분석 도구

이미지 최적화의 첫걸음은 현재 이미지의 레이어 구성을 파악하는 것이다.

### docker history

`docker history`는 이미지의 각 레이어가 어떤 명령에 의해 생성되었고, 크기가 얼마인지 보여준다.

```bash
docker history my-next-app:latest

# IMAGE          CREATED        CREATED BY                                     SIZE
# a1b2c3d4e5f6   2 hours ago    CMD ["node" "server.js"]                       0B
# f6e5d4c3b2a1   2 hours ago    COPY dir:abc123 in /app/.next/static           5.2MB
# 1a2b3c4d5e6f   2 hours ago    COPY dir:def456 in /app                        45MB
# ...

# --no-trunc 옵션으로 전체 명령 표시
docker history --no-trunc my-next-app:latest

# --format 옵션으로 필요한 정보만 표시
docker history --format "table {{.Size}}\t{{.CreatedBy}}" my-next-app:latest
```

### docker image inspect

`docker image inspect`는 이미지의 메타데이터를 JSON 형태로 보여준다. 레이어 다이제스트, 환경 변수, 라벨 등 상세 정보를 확인할 수 있다.

```bash
# 이미지의 전체 레이어 다이제스트 확인
docker image inspect my-next-app:latest --format '{{json .RootFS.Layers}}' | jq .

# 이미지의 전체 크기 확인
docker image inspect my-next-app:latest --format '{{.Size}}' | numfmt --to=iec
```

### dive — 인터랙티브 레이어 분석 TUI

dive(*dive - Docker 이미지의 레이어를 시각적으로 탐색하는 터미널 기반 도구*)는 각 레이어에서 추가/수정/삭제된 파일을 인터랙티브하게 탐색할 수 있다.

**설치**:

```bash
# macOS
brew install dive

# Linux
wget https://github.com/wagoodman/dive/releases/latest/download/dive_linux_amd64.deb
sudo dpkg -i dive_linux_amd64.deb
```

**사용법**:

```bash
# 기존 이미지 분석
dive my-next-app:latest

# 빌드와 동시에 분석
dive build -t my-next-app:latest .
```

dive TUI에서 확인할 수 있는 정보:
- 각 레이어의 크기와 명령
- 레이어별 파일 시스템 변경 사항 (추가/수정/삭제)
- **낭비된 공간**(*Wasted Space - 하위 레이어에서 추가되었다가 상위 레이어에서 삭제된 파일이 차지하는 공간*): 이전 레이어에서 생성된 파일이 이후 레이어에서 삭제되어도 이미지 크기에는 그대로 남는 공간
- 이미지 효율성 점수

**CI에서 자동 효율성 검증**:

```bash
# CI=true 환경에서 비인터랙티브 모드로 실행
CI=true dive my-next-app:latest --lowestEfficiency 0.9 --highestWastedBytes 50MB

# 효율성이 90% 미만이거나 낭비 공간이 50MB 초과하면 exit code 1 반환
```

`.dive-ci` 설정 파일로 기준을 지정할 수도 있다:

```yaml
rules:
  lowestEfficiency: 0.9
  highestWastedBytes: 52428800  # 50MB
  highestUserWastedPercent: 0.1
```

### docker buildx du

BuildKit의 캐시 사용량을 확인한다.

```bash
# BuildKit 캐시 사용량 확인
docker buildx du

# 캐시 정리
docker buildx prune

# 오래된 캐시만 정리 (72시간 이상)
docker buildx prune --filter until=72h
```

---

## 5. 보안 취약점 스캔

이미지를 프로덕션에 배포하기 전에 반드시 취약점 스캔을 수행해야 한다. 보안 취약점은 CVE(*CVE, Common Vulnerabilities and Exposures - 공개적으로 알려진 보안 취약점에 부여되는 고유 식별자*)로 추적된다.

### docker scout

Docker Desktop에 내장된 공식 취약점 스캔 도구다.

```bash
# 이미지 보안 개요 확인
docker scout quickview my-next-app:latest

# 상세 CVE 목록 확인
docker scout cves my-next-app:latest

# Critical과 High 심각도만 필터링
docker scout cves --only-severity critical,high my-next-app:latest

# 두 이미지 간 취약점 비교
docker scout compare my-next-app:latest --to my-next-app:previous

# SBOM 생성
docker scout sbom my-next-app:latest
```

SBOM(*SBOM, Software Bill of Materials - 소프트웨어에 포함된 모든 구성 요소의 목록*)은 이미지에 포함된 모든 패키지와 버전을 나열한 명세서다. 보안 감사, 라이선스 준수 확인, 취약점 추적에 사용된다.

### trivy

Aqua Security가 개발한 오픈소스 취약점 스캐너로, Docker 이미지뿐 아니라 파일시스템, Git 리포지토리, Kubernetes 클러스터까지 스캔할 수 있다.

**설치**:

```bash
# macOS
brew install trivy

# Docker로 실행
docker run --rm aquasec/trivy image my-next-app:latest
```

**이미지 스캔**:

```bash
# 이미지의 OS 패키지 + 앱 의존성 취약점 스캔
trivy image my-next-app:latest

# 심각도 필터링
trivy image --severity HIGH,CRITICAL my-next-app:latest

# JSON 형식 출력 (CI 파이프라인 연동용)
trivy image --format json --output result.json my-next-app:latest

# 테이블 형식으로 깔끔하게 출력
trivy image --format table my-next-app:latest
```

**Dockerfile 스캔** (빌드 전 설정 오류 탐지):

```bash
# Dockerfile의 보안 모범 사례 위반 탐지
trivy config ./Dockerfile

# 예시 출력:
# CRITICAL: Running as root user (DS002)
# HIGH: apt-get update without cleanup (DS013)
```

**CI에서 자동 스캔 (GitHub Actions)**:

```yaml
# .github/workflows/security-scan.yml
name: Security Scan

on:
  push:
    branches: [main]
  pull_request:

jobs:
  trivy-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build Image
        run: docker build -t my-next-app:${{ github.sha }} .

      - name: Run Trivy Scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: my-next-app:${{ github.sha }}
          format: table
          exit-code: 1           # Critical/High 발견 시 빌드 실패
          severity: CRITICAL,HIGH
          ignore-unfixed: true   # 아직 패치가 없는 취약점은 무시

      - name: Upload Trivy Report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: trivy-report
          path: trivy-report.json
```

### CVE 심각도와 대응 전략

| 심각도 | CVSS 점수 | 대응 | 예시 |
|-------|----------|------|------|
| Critical | 9.0~10.0 | **즉시 패치**. 배포 차단 | 원격 코드 실행(RCE), 인증 우회 |
| High | 7.0~8.9 | **24시간 내 패치**. 신규 배포 차단 권장 | 권한 상승, 데이터 유출 |
| Medium | 4.0~6.9 | **다음 정기 업데이트에 포함** | 서비스 거부(DoS), 정보 노출 |
| Low | 0.1~3.9 | **모니터링**, 편의 시 패치 | 경미한 정보 노출 |

### 베이스 이미지별 CVE 수 비교

실제 CVE 수는 시점에 따라 달라지지만, 일반적인 경향:

```bash
# 각 베이스 이미지의 CVE 수 비교 (예시)
trivy image --severity HIGH,CRITICAL node:20
# HIGH: 15, CRITICAL: 3

trivy image --severity HIGH,CRITICAL node:20-slim
# HIGH: 5, CRITICAL: 1

trivy image --severity HIGH,CRITICAL node:20-alpine
# HIGH: 2, CRITICAL: 0

trivy image --severity HIGH,CRITICAL gcr.io/distroless/nodejs20-debian12
# HIGH: 0, CRITICAL: 0
```

> **핵심 통찰**: 베이스 이미지를 `node:20`에서 `node:20-alpine`으로 바꾸는 것만으로도 Critical/High CVE의 대부분을 제거할 수 있다. Distroless를 사용하면 거의 0에 가까워진다.

---

## 6. 빌드 캐시 최적화

빌드 캐시는 이미지 빌드 속도를 극대화하는 핵심이다. BuildKit은 다양한 캐시 백엔드를 지원한다.

### BuildKit 캐시 백엔드

```bash
# local: 로컬 디스크에 캐시 저장 (기본)
docker buildx build --cache-to type=local,dest=/tmp/buildcache \
                    --cache-from type=local,src=/tmp/buildcache \
                    -t my-app:latest .

# registry: OCI 레지스트리에 캐시 저장
docker buildx build --cache-to type=registry,ref=myregistry/cache:latest \
                    --cache-from type=registry,ref=myregistry/cache:latest \
                    -t my-app:latest .

# gha: GitHub Actions 캐시 연동
docker buildx build --cache-to type=gha \
                    --cache-from type=gha \
                    -t my-app:latest .

# s3: AWS S3에 캐시 저장
docker buildx build --cache-to type=s3,region=ap-northeast-2,bucket=my-cache \
                    --cache-from type=s3,region=ap-northeast-2,bucket=my-cache \
                    -t my-app:latest .
```

| 캐시 백엔드 | 사용 환경 | 장점 | 단점 |
|------------|---------|------|------|
| local | 로컬 개발, 자체 호스팅 CI | 빠른 속도 | CI 러너 간 공유 불가 |
| registry | 모든 환경 | 러너 간 공유 가능, 별도 설정 불필요 | 레지스트리 비용 |
| gha | GitHub Actions | 설정 간단, Actions 캐시 통합 | GitHub Actions 전용, 10GB 제한 |
| s3 | AWS 환경 | 대용량, 저비용 | AWS 설정 필요 |

### --mount=type=cache 활용

Ch 4에서 소개한 `--mount=type=cache`를 더 심화적으로 활용한다. 이 기능은 빌드 간에 디렉터리를 캐시로 유지하여 반복 빌드를 극적으로 빠르게 만든다.

```dockerfile
FROM node:20-alpine AS deps
WORKDIR /app

COPY package.json package-lock.json ./

# npm 캐시를 BuildKit 캐시로 마운트
# → npm ci가 이미 다운로드된 패키지를 재사용
RUN --mount=type=cache,target=/root/.npm \
    npm ci

FROM node:20-alpine AS builder
WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Next.js 빌드 캐시를 유지
RUN --mount=type=cache,target=/app/.next/cache \
    npm run build
```

**캐시 마운트의 핵심 포인트**:
- `target`: 캐시할 디렉터리 경로
- 캐시된 디렉터리는 최종 이미지에 포함되지 않는다 (빌드 시에만 사용)
- 동일 BuildKit 인스턴스에서의 후속 빌드에서 캐시가 재사용된다

### 캐시 만료 전략

캐시가 무한히 쌓이면 디스크를 압박한다. 적절한 정리 전략이 필요하다.

```bash
# 사용하지 않는 빌드 캐시 전체 삭제
docker buildx prune --all

# 7일 이상 된 캐시만 삭제
docker buildx prune --filter until=168h

# 최대 10GB만 유지하고 나머지 삭제
docker buildx prune --keep-storage 10GB

# 모든 미사용 Docker 리소스 정리 (이미지, 컨테이너, 볼륨, 캐시)
docker system prune --all --volumes
```

### CI에서의 캐시 전략: GitHub Actions 연동

```yaml
# .github/workflows/build.yml
name: Build and Push

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and Push
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

`mode=max`는 모든 스테이지의 레이어를 캐시에 저장한다. 기본값 `mode=min`은 최종 스테이지의 레이어만 저장한다. `mode=max`를 사용하면 중간 스테이지(deps, builder)의 캐시도 유지되어 후속 빌드가 더 빨라진다.

---

## 7. 최적화 체크리스트

### 이미지 크기 목표

Node.js/Next.js 앱 기준 권장 이미지 크기:

| 앱 유형 | 목표 크기 | 전략 |
|--------|---------|------|
| Next.js (standalone) | ~100~150MB | 멀티스테이지 + standalone + alpine |
| Express API | ~80~120MB | 멀티스테이지 + alpine |
| 정적 사이트 (Next.js export) | ~30~50MB | nginx-alpine에 정적 파일만 |

### 단계별 최적화 순서

최적화는 효과가 큰 것부터 적용하는 것이 효율적이다:

| 순서 | 최적화 항목 | 기대 효과 | 난이도 |
|------|-----------|----------|-------|
| 1 | `.dockerignore` 작성 | 빌드 컨텍스트 축소, 캐시 무효화 방지 | 낮음 |
| 2 | 멀티스테이지 빌드 | 50~70% 크기 감소 | 중간 |
| 3 | 경량 베이스 이미지 (alpine/slim) | 추가 30~50% 감소 | 낮음 |
| 4 | Next.js standalone 모드 | 추가 50% 감소 | 낮음 |
| 5 | `--mount=type=cache` | 빌드 시간 50~80% 단축 | 낮음 |
| 6 | Distroless/Chainguard | 추가 10~20% 감소 + CVE 최소화 | 중간 |
| 7 | CI 캐시 전략 (gha/registry) | CI 빌드 시간 50~70% 단축 | 중간 |
| 8 | 자동 취약점 스캔 | 보안 위험 사전 차단 | 낮음 |

---

## 자주 하는 실수

### 1. devDependencies를 프로덕션 이미지에 포함

```dockerfile
# 나쁜 예: devDependencies 포함
FROM node:20-alpine
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install          # devDependencies도 설치됨
COPY . .
RUN npm run build
CMD ["npm", "start"]     # devDependencies가 이미지에 남아 있음
```

```dockerfile
# 좋은 예: 멀티스테이지로 devDependencies 제거
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci               # 빌드에 필요한 devDependencies 포함 설치
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
CMD ["node", "server.js"]  # node_modules 자체가 불필요 (standalone)
```

### 2. .dockerignore 누락

`.dockerignore`가 없으면 `node_modules`, `.git`, `.next` 등이 빌드 컨텍스트에 포함되어 빌드가 느려지고, 캐시가 불필요하게 무효화된다.

```bash
# .dockerignore 필수 항목
node_modules
.next
.git
.env*
*.log
dist
coverage
.turbo
```

### 3. 불필요한 시스템 패키지 설치 후 미삭제

```dockerfile
# 나쁜 예: 빌드 도구가 최종 이미지에 남음
FROM node:20-alpine
RUN apk add python3 make g++
COPY . .
RUN npm ci
CMD ["node", "server.js"]

# 좋은 예: 빌드 도구는 빌드 스테이지에서만 사용
FROM node:20-alpine AS builder
RUN apk add --no-cache python3 make g++
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
COPY --from=builder /app/.next/standalone ./
CMD ["node", "server.js"]
```

### 4. 취약점 스캔 없이 배포

프로덕션 이미지를 빌드한 후 스캔 없이 바로 배포하면, 알려진 취약점이 있는 패키지가 프로덕션에 노출된다. CI 파이프라인에 취약점 스캔 단계를 반드시 추가해야 한다.

### 5. 캐시 무효화 인지 부족

```dockerfile
# 나쁜 예: 소스 코드 변경 시 npm ci 캐시도 무효화됨
COPY . .
RUN npm ci
RUN npm run build

# 좋은 예: 패키지 파일만 먼저 복사하여 캐시 보존
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build
```

Docker는 레이어를 순차적으로 평가하며, 한 레이어가 변경되면 그 이후의 모든 레이어 캐시가 무효화된다. `COPY . .`을 먼저 실행하면 소스 코드의 어떤 파일이라도 변경될 때마다 `npm ci`가 다시 실행된다.

---

## 명령어 레퍼런스

| 명령어 | 설명 |
|-------|------|
| `docker history <image>` | 이미지의 레이어별 크기와 생성 명령 확인 |
| `docker history --no-trunc <image>` | 전체 명령어를 잘리지 않게 표시 |
| `docker image inspect <image>` | 이미지 메타데이터(레이어 다이제스트, 환경변수 등) JSON 출력 |
| `docker scout quickview <image>` | 이미지 보안 개요 (취약점 수 요약) |
| `docker scout cves <image>` | 이미지의 상세 CVE 목록 출력 |
| `docker scout sbom <image>` | SBOM(소프트웨어 구성 명세서) 생성 |
| `docker scout compare <image> --to <other>` | 두 이미지 간 취약점 비교 |
| `docker buildx du` | BuildKit 캐시 사용량 확인 |
| `docker buildx prune` | BuildKit 캐시 정리 |
| `docker buildx prune --filter until=72h` | 72시간 이상 된 캐시만 정리 |
| `dive <image>` | 인터랙티브 레이어 분석 TUI 실행 |
| `CI=true dive <image> --lowestEfficiency 0.9` | CI에서 이미지 효율성 자동 검증 |
| `trivy image <image>` | 이미지 취약점 스캔 |
| `trivy image --severity HIGH,CRITICAL <image>` | 높은 심각도만 필터링하여 스캔 |
| `trivy config Dockerfile` | Dockerfile 보안 모범 사례 검사 |

---

## 요약

- **이미지 크기**는 배포 속도, 보안 표면, 비용, CI/CD 파이프라인 전체에 직접적으로 영향을 미친다
- **멀티스테이지 빌드**의 3단계 패턴(deps → builder → runner)은 프로덕션 Node.js 앱의 표준이다
- **Next.js standalone** 모드는 `node_modules`에서 실제로 사용되는 파일만 트레이싱하여 이미지 크기를 극적으로 줄인다
- **베이스 이미지 선택**은 가장 효과가 큰 최적화다: `node:20`(~1.1GB) → `alpine`(~130MB) → `distroless`(~120MB)
- **Distroless/Chainguard** 이미지는 셸과 패키지 매니저를 제거하여 공격 표면을 최소화한다
- **dive**로 레이어를 분석하여 낭비된 공간을 찾고, **trivy**나 **docker scout**로 취약점을 스캔해야 한다
- **BuildKit 캐시 백엔드**(local, registry, gha, s3)와 `--mount=type=cache`를 활용하여 빌드 시간을 단축한다
- CI 파이프라인에 **자동 취약점 스캔**과 **이미지 효율성 검증**을 포함해야 한다
- `.dockerignore` 작성, 패키지 파일 우선 복사, devDependencies 제거 등 기본적인 실수를 피해야 한다

---

## 다른 챕터와의 관계

- **Ch 2 (이미지)**: 베이스 이미지의 기본 개념과 태그 전략을 다뤘다. 이 챕터에서는 베이스 이미지 선택을 보안과 크기 관점에서 심화했다
- **Ch 4 (Dockerfile 심화)**: 멀티스테이지 빌드와 BuildKit의 기본을 다뤘다. 이 챕터에서는 3단계 패턴, standalone 모드, 캐시 백엔드 등 프로덕션 수준의 심화 패턴을 다뤘다
- **Ch 10 (보안)**: 이 챕터에서 다룬 취약점 스캔, Distroless 이미지는 Ch 10의 컨테이너 보안 강화와 직결된다. Ch 10에서는 런타임 보안, 시크릿 관리 등을 추가로 다룬다
- **Ch 13 (모노레포)**: `turbo prune --docker` 패턴을 미리 소개했다. Ch 13에서는 모노레포 전체 Docker 워크플로우를 자세히 다룬다
- **Ch 14 (CI/CD)**: GitHub Actions 캐시 연동, 자동 취약점 스캔 등의 CI 설정을 소개했다. Ch 14에서는 전체 CI/CD 파이프라인 설계를 다룬다
