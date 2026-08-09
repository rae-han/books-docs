# Chapter 13: 모노레포 Docker 전략 (Monorepo Docker Strategies)

## 핵심 질문

모노레포 환경에서 Docker 이미지를 어떻게 효율적으로 빌드하는가? 전체 모노레포를 이미지에 넣지 않고 필요한 패키지만 추출하는 방법은 무엇인가?

---

## 1. 모노레포에서 Docker의 과제

### 일반적인 모노레포 구조

현대 Node.js 프로젝트에서 모노레포(*Monorepo - 여러 프로젝트를 하나의 저장소에서 관리하는 방식*)는 사실상 표준이 되었다. 대표적인 구조는 다음과 같다:

```
my-monorepo/
├── apps/
│   ├── web/              # Next.js 프론트엔드
│   │   ├── package.json
│   │   └── src/
│   ├── api/              # Express API 서버
│   │   ├── package.json
│   │   └── src/
│   └── admin/            # 관리자 대시보드
│       ├── package.json
│       └── src/
├── packages/
│   ├── ui/               # 공유 UI 컴포넌트
│   │   ├── package.json
│   │   └── src/
│   ├── shared/           # 공유 유틸리티
│   │   ├── package.json
│   │   └── src/
│   └── config/           # 공유 설정 (tsconfig, eslint 등)
│       └── package.json
├── package.json          # 루트 package.json
├── pnpm-workspace.yaml
├── pnpm-lock.yaml
└── turbo.json
```

`apps/`에는 배포 가능한 애플리케이션이, `packages/`에는 앱들이 공유하는 라이브러리가 위치한다. 이 구조에서 Docker 이미지를 빌드하려 할 때 네 가지 근본적인 과제에 직면한다.

### 과제 1: 빌드 컨텍스트에 전체 모노레포가 포함됨

`docker build`를 실행하면 지정된 경로의 모든 파일이 빌드 컨텍스트(*Build Context - Docker 데몬에 전송되는 파일 집합*)로 전송된다. 모노레포 루트에서 빌드하면 `apps/web`만 필요하더라도 `apps/api`, `apps/admin`, 그 외 모든 패키지가 함께 전송된다.

```bash
# apps/web만 빌드하고 싶지만...
docker build -f apps/web/Dockerfile .
# 전체 모노레포가 빌드 컨텍스트로 전송됨 (수백 MB ~ 수 GB)
```

### 과제 2: 하나의 앱만 변경해도 모든 앱의 캐시 무효화

가장 단순한 접근법인 `COPY . .`를 사용하면, `apps/api`의 코드를 한 줄만 수정해도 `apps/web`의 Docker 빌드 캐시가 무효화된다. 모든 앱이 같은 `COPY` 레이어를 공유하기 때문이다.

```dockerfile
# 나쁜 예: 어떤 파일이든 변경되면 이 레이어부터 캐시 무효화
COPY . .
RUN pnpm build --filter=web
```

### 과제 3: 공유 패키지 의존성 처리

`apps/web`이 `packages/ui`와 `packages/shared`에 의존한다면, Docker 이미지에는 이 두 패키지도 포함되어야 한다. 하지만 `packages/config`처럼 관련 없는 패키지는 제외해야 한다. 이 의존성 그래프를 수동으로 관리하는 것은 에러가 발생하기 쉽다.

```json
// apps/web/package.json
{
  "dependencies": {
    "@repo/ui": "workspace:*",
    "@repo/shared": "workspace:*"
    // @repo/config는 필요 없음
  }
}
```

### 과제 4: 루트의 lock 파일과 workspace 프로토콜 처리

모노레포에서는 하나의 lock 파일(`pnpm-lock.yaml`)이 모든 패키지의 의존성을 관리한다. `workspace:*` 프로토콜(*Workspace Protocol - 모노레포 내 패키지를 로컬 참조하는 방식*)은 패키지 매니저가 해석해야 하며, 단순히 `npm install`로는 처리되지 않는다.

```yaml
# pnpm-lock.yaml (일부)
dependencies:
  '@repo/ui':
    specifier: workspace:*
    version: link:../../packages/ui
```

---

## 2. 접근법 비교

| 접근법 | 방식 | 장점 | 단점 |
|--------|------|------|------|
| 전체 복사 | `COPY . .` | 단순함, 추가 도구 불필요 | 이미지 거대, 캐시 비효율적 |
| 수동 복사 | 필요한 파일만 `COPY` | 최적화 가능 | 유지보수 지옥, 의존성 변경 시 Dockerfile 수정 필수 |
| turbo prune | `turbo prune --docker` | 자동 추출, 캐시 최적 | Turborepo 의존 |
| Nx affected | `nx affected:build` | 영향받은 앱만 빌드 | Nx 의존 |
| pnpm deploy | `pnpm deploy` | 패키지 매니저 내장 | pnpm 전용, Turborepo만큼 세밀하지 않음 |

### 전체 복사의 문제를 숫자로 보기

```bash
# 전체 모노레포 크기
$ du -sh my-monorepo/
1.2G    my-monorepo/

# apps/web이 실제로 필요한 파일만
$ du -sh out/
45M     out/
```

전체 복사와 선택적 추출의 차이는 수십 배에 달할 수 있다. 빌드 시간, 이미지 크기, 캐시 효율 모든 면에서 선택적 추출이 우월하다.

### 수동 복사의 한계

```dockerfile
# 수동으로 필요한 파일만 복사 — 유지보수가 힘들다
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY apps/web/package.json ./apps/web/
COPY packages/ui/package.json ./packages/ui/
COPY packages/shared/package.json ./packages/shared/
# 새 공유 패키지가 추가될 때마다 이 목록을 수정해야 한다
```

패키지가 5개일 때는 관리 가능하지만, 20~30개가 넘어가면 사실상 불가능하다. 자동화된 도구가 필요한 이유다.

---

## 3. Turborepo + Docker (turbo prune --docker)

### turbo prune이 하는 일

`turbo prune`은 Turborepo가 제공하는 명령어로, 대상 앱과 그 앱이 의존하는 내부 패키지만 추출한다. `--docker` 플래그를 추가하면 Docker 멀티스테이지 빌드에 최적화된 디렉토리 구조를 생성한다.

```bash
# web 앱과 의존하는 패키지만 추출
turbo prune web --docker
```

### turbo prune --docker의 출력 구조

이 명령은 `out/` 디렉토리에 세 가지를 생성한다:

```
out/
├── json/                    # package.json 파일들만 (의존성 설치 캐시용)
│   ├── package.json         # 루트
│   ├── pnpm-lock.yaml       # 필터링된 lock 파일
│   ├── pnpm-workspace.yaml
│   ├── apps/
│   │   └── web/
│   │       └── package.json
│   └── packages/
│       ├── ui/
│       │   └── package.json
│       └── shared/
│           └── package.json
├── full/                    # 전체 소스 코드 (빌드용)
│   ├── apps/
│   │   └── web/             # web 앱 전체 소스
│   ├── packages/
│   │   ├── ui/              # 의존하는 패키지만 포함
│   │   └── shared/
│   └── turbo.json
└── pnpm-lock.yaml           # 루트 레벨 lock 파일
```

핵심은 `json/`과 `full/`의 분리다:

- **`json/`**: `package.json`과 lock 파일만 포함한다. 소스 코드가 변경되어도 이 디렉토리는 변하지 않으므로, `pnpm install` 레이어의 캐시를 보존할 수 있다.
- **`full/`**: 실제 소스 코드가 포함된다. 빌드 단계에서 사용한다.

### 3단계 멀티스테이지 Dockerfile

turbo prune의 출력을 활용한 최적의 Dockerfile은 4개의 스테이지로 구성된다:

```dockerfile
# =============================================================
# Stage 1: Pruner — turbo prune으로 필요한 파일만 추출
# =============================================================
FROM node:20-alpine AS pruner

RUN corepack enable && corepack prepare pnpm@9 --activate
RUN pnpm add -g turbo@2

WORKDIR /app
COPY . .
RUN turbo prune web --docker

# =============================================================
# Stage 2: Installer — 의존성 설치 (캐시 최적화)
# =============================================================
FROM node:20-alpine AS installer

RUN corepack enable && corepack prepare pnpm@9 --activate

WORKDIR /app

# json/ 디렉토리의 package.json들만 먼저 복사 → 의존성 캐시 보존
COPY --from=pruner /app/out/json/ .

# 의존성 설치 (소스 코드 변경과 무관하게 캐시됨)
RUN pnpm install --frozen-lockfile

# 전체 소스 코드 복사
COPY --from=pruner /app/out/full/ .

# 빌드 실행
RUN pnpm turbo build --filter=web...

# =============================================================
# Stage 3: Runner — 프로덕션 실행 환경
# =============================================================
FROM node:20-alpine AS runner

RUN corepack enable && corepack prepare pnpm@9 --activate

WORKDIR /app

# 시스템 사용자 생성
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Next.js standalone 출력물만 복사
COPY --from=installer /app/apps/web/.next/standalone ./
COPY --from=installer /app/apps/web/.next/static ./apps/web/.next/static
COPY --from=installer /app/apps/web/public ./apps/web/public

USER nextjs

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "apps/web/server.js"]
```

> **핵심 통찰**: `json/` 디렉토리를 먼저 복사하고 `pnpm install`을 실행한 뒤, `full/` 디렉토리를 복사하는 순서가 캐시 최적화의 핵심이다. 소스 코드만 변경된 경우 `pnpm install` 레이어는 캐시에서 재사용된다.

### Next.js standalone 출력 설정

Runner 스테이지에서 `standalone` 출력을 사용하려면 `next.config.js`에 설정이 필요하다:

```typescript
// apps/web/next.config.ts
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  output: 'standalone',
  // 모노레포에서 상위 디렉토리의 node_modules도 포함
  outputFileTracingRoot: '../../',
};

export default nextConfig;
```

`outputFileTracingRoot`는 모노레포 루트를 가리켜야 한다. 이 설정이 없으면 Next.js가 `packages/` 내 공유 코드의 의존성을 standalone 출력에 포함시키지 못한다.

### 이미지 크기 비교

| 접근법 | 이미지 크기 | 빌드 시간 (캐시 미스) | 빌드 시간 (소스만 변경) |
|--------|------------|---------------------|----------------------|
| `COPY . .` (전체 복사) | ~1.2 GB | ~180초 | ~180초 (캐시 무효화) |
| turbo prune + standalone | ~180 MB | ~120초 | ~45초 (install 캐시 적중) |

---

## 4. Nx + Docker

### nx affected:build — 변경된 앱만 감지하여 빌드

Nx(*Nx - Nrwl이 만든 모노레포 빌드 시스템*)는 프로젝트 그래프를 분석하여 변경에 영향받은 앱만 식별할 수 있다.

```bash
# 마지막 커밋 이후 변경에 영향받은 앱 목록
npx nx affected -t build --base=HEAD~1

# 특정 앱만 빌드 (의존하는 패키지 포함)
npx nx build web
```

### Nx 모노레포의 Dockerfile

Nx는 Turborepo의 `prune --docker`처럼 Docker 전용 추출 명령을 제공하지 않는다. 대신 Nx의 빌드 캐시와 Docker의 멀티스테이지를 조합한다:

```dockerfile
# =============================================================
# Stage 1: Dependencies
# =============================================================
FROM node:20-alpine AS deps

RUN corepack enable && corepack prepare pnpm@9 --activate

WORKDIR /app

# 루트와 관련 패키지의 package.json만 복사
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY apps/web/package.json ./apps/web/
COPY packages/ui/package.json ./packages/ui/
COPY packages/shared/package.json ./packages/shared/

RUN pnpm install --frozen-lockfile

# =============================================================
# Stage 2: Builder
# =============================================================
FROM node:20-alpine AS builder

RUN corepack enable && corepack prepare pnpm@9 --activate

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Nx로 web 앱과 의존성 빌드
RUN npx nx build web --prod

# =============================================================
# Stage 3: Runner
# =============================================================
FROM node:20-alpine AS runner

WORKDIR /app

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/apps/web/.next/standalone ./
COPY --from=builder /app/apps/web/.next/static ./apps/web/.next/static
COPY --from=builder /app/apps/web/public ./apps/web/public

USER nextjs

EXPOSE 3000
CMD ["node", "apps/web/server.js"]
```

### Nx의 빌드 캐시와 Docker 캐시의 차이

| 구분 | Nx 빌드 캐시 | Docker 레이어 캐시 |
|------|-------------|-------------------|
| 캐시 위치 | 로컬 `.nx/cache` 또는 원격 캐시 | Docker 데몬 내부 |
| 캐시 키 | 소스 파일 해시 + 설정 | Dockerfile 명령어 + 이전 레이어 |
| 공유 범위 | CI 전체에서 공유 가능 (Nx Cloud) | 같은 머신 내에서만 (BuildKit 캐시 마운트 별도) |
| 세분성 | 태스크 단위 | 레이어 단위 |

Nx Cloud의 원격 캐시를 활용하면, CI에서 이미 빌드된 태스크는 Docker 내부에서도 캐시 적중하여 빌드 시간을 단축할 수 있다.

### @nx/docker 플러그인

Nx 생태계에는 `@nx/docker` 플러그인이 존재하여 프로젝트 그래프 기반으로 자동화된 Docker 빌드를 설정할 수 있다:

```json
// project.json
{
  "targets": {
    "docker-build": {
      "executor": "@nx/docker:build",
      "options": {
        "push": false,
        "tags": ["my-registry/web:latest"]
      }
    }
  }
}
```

---

## 5. pnpm workspace + Docker

### pnpm deploy 명령어

`pnpm deploy`는 특정 패키지와 그 의존성(node_modules 포함)을 독립된 디렉토리로 추출하는 명령어다. Turborepo 없이도 pnpm만으로 최적화된 Docker 이미지를 만들 수 있다.

```bash
# web 앱과 의존성을 /tmp/web-deploy로 추출
pnpm deploy --filter=web --prod /tmp/web-deploy
```

추출된 디렉토리는 다음과 같은 구조를 가진다:

```
/tmp/web-deploy/
├── package.json
├── node_modules/       # 프로덕션 의존성만 포함 (hoisted 아님)
├── src/
└── ...                 # web 앱의 소스 파일
```

### pnpm --filter를 활용한 선택적 설치

`--filter` 플래그로 특정 패키지의 의존성만 설치할 수도 있다:

```bash
# web 앱과 의존하는 워크스페이스 패키지의 의존성만 설치
pnpm install --filter=web...
```

`web...`의 `...`은 web이 의존하는 모든 워크스페이스 패키지를 포함한다는 의미다.

### pnpm-workspace.yaml과 .npmrc 설정

```yaml
# pnpm-workspace.yaml
packages:
  - 'apps/*'
  - 'packages/*'
```

```ini
# .npmrc
shamefully-hoist=false
strict-peer-dependencies=true
# Docker 빌드 시 중요: link-workspace-packages를 true로 설정
link-workspace-packages=true
```

### Dockerfile 예제 (pnpm deploy 패턴)

```dockerfile
# =============================================================
# Stage 1: Builder — 빌드 수행
# =============================================================
FROM node:20-alpine AS builder

RUN corepack enable && corepack prepare pnpm@9 --activate

WORKDIR /app

# 전체 모노레포 복사 (빌드를 위해)
COPY . .

RUN pnpm install --frozen-lockfile

# 공유 패키지 먼저 빌드
RUN pnpm --filter=@repo/ui build
RUN pnpm --filter=@repo/shared build

# web 앱 빌드
RUN pnpm --filter=web build

# =============================================================
# Stage 2: Deployer — 프로덕션 패키지만 추출
# =============================================================
FROM node:20-alpine AS deployer

RUN corepack enable && corepack prepare pnpm@9 --activate

WORKDIR /app

COPY --from=builder /app .

# pnpm deploy로 web 앱의 프로덕션 의존성만 추출
RUN pnpm deploy --filter=web --prod /deploy/web

# =============================================================
# Stage 3: Runner
# =============================================================
FROM node:20-alpine AS runner

WORKDIR /app

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# pnpm deploy 결과물만 복사
COPY --from=deployer /deploy/web .

USER nextjs

EXPOSE 3000
CMD ["node", "server.js"]
```

### pnpm deploy vs turbo prune 비교

| 항목 | pnpm deploy | turbo prune --docker |
|------|-------------|---------------------|
| 도구 의존성 | pnpm만 필요 | Turborepo 필요 |
| 캐시 최적화 | json/full 분리 없음 | json/full 분리로 install 캐시 보존 |
| 의존성 추출 | 프로덕션 node_modules까지 포함 | package.json + 소스만 추출 |
| 빌드 통합 | 별도 빌드 단계 필요 | turbo build와 자연스럽게 연동 |

---

## 6. 공유 패키지(Shared Packages) 처리

### Internal Packages (빌드가 필요한 공유 코드)

모노레포의 공유 패키지는 두 가지 유형으로 나뉜다:

1. **소스 공유 패키지**: TypeScript 소스를 그대로 가져와 앱에서 빌드하는 방식
2. **사전 빌드 패키지**: 패키지 자체를 빌드한 뒤 배포 산출물을 가져오는 방식

```json
// packages/ui/package.json — 소스 공유 방식
{
  "name": "@repo/ui",
  "main": "./src/index.ts",     // 소스를 직접 참조
  "types": "./src/index.ts"
}
```

```json
// packages/ui/package.json — 사전 빌드 방식
{
  "name": "@repo/ui",
  "main": "./dist/index.js",    // 빌드 산출물 참조
  "types": "./dist/index.d.ts",
  "scripts": {
    "build": "tsup src/index.ts --format cjs,esm --dts"
  }
}
```

### 빌드 순서 보장

사전 빌드 방식을 사용할 때는 빌드 순서가 중요하다. `apps/web`이 `packages/ui`에 의존하면, `packages/ui`가 먼저 빌드되어야 한다.

```dockerfile
# Turborepo를 사용하면 의존성 그래프에 따라 자동으로 순서 결정
RUN pnpm turbo build --filter=web...

# 수동으로 할 경우 직접 순서를 지정해야 한다
RUN pnpm --filter=@repo/shared build && \
    pnpm --filter=@repo/ui build && \
    pnpm --filter=web build
```

Turborepo의 `turbo build --filter=web...`은 의존성 그래프를 분석하여 올바른 순서로 빌드를 실행한다. `...` 접미사가 의존하는 모든 패키지를 포함하라는 뜻이다.

### TypeScript 프로젝트 참조와 Docker 빌드

소스 공유 방식에서는 TypeScript의 프로젝트 참조(*Project References - 여러 tsconfig를 연결하여 증분 빌드를 가능하게 하는 기능*)를 활용한다:

```json
// apps/web/tsconfig.json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@repo/ui/*": ["../../packages/ui/src/*"],
      "@repo/shared/*": ["../../packages/shared/src/*"]
    }
  },
  "references": [
    { "path": "../../packages/ui" },
    { "path": "../../packages/shared" }
  ]
}
```

Docker 빌드 시 이 경로가 올바르게 해석되려면, 모노레포의 디렉토리 구조가 컨테이너 내부에서도 동일하게 유지되어야 한다. turbo prune은 이 구조를 보존하므로 문제가 없다.

### tsconfig.json의 paths와 Docker 내 모듈 해석

Next.js의 경우 `next.config.ts`에서 `transpilePackages`를 설정하여 워크스페이스 패키지의 TypeScript를 트랜스파일할 수 있다:

```typescript
// apps/web/next.config.ts
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  output: 'standalone',
  outputFileTracingRoot: '../../',
  transpilePackages: ['@repo/ui', '@repo/shared'],
};

export default nextConfig;
```

이 설정이 없으면 Docker 빌드 중 공유 패키지의 TypeScript 파일을 해석하지 못해 빌드가 실패한다.

---

## 7. CI에서의 모노레포 Docker 빌드

### 변경 감지

CI에서 모든 앱을 매번 빌드하는 것은 낭비다. 변경에 영향받은 앱만 빌드해야 한다.

```bash
# Turborepo: 마지막 커밋 이후 변경된 패키지 확인
turbo build --filter="...[HEAD^1]" --dry-run=json

# Nx: 영향받은 프로젝트 목록
npx nx affected -t build --base=HEAD~1 --head=HEAD
```

### GitHub Actions 워크플로우: 변경된 앱만 빌드/푸시

```yaml
# .github/workflows/docker-build.yaml
name: Build Changed Apps

on:
  push:
    branches: [main]

jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      web: ${{ steps.filter.outputs.web }}
      api: ${{ steps.filter.outputs.api }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 2

      - name: Detect changed apps
        id: filter
        run: |
          # turbo dry-run으로 빌드가 필요한 앱 감지
          npx turbo build --filter="...[HEAD^1]" --dry-run=json > dry-run.json

          echo "web=$(jq '.tasks | map(select(.taskId == "web#build")) | length > 0' dry-run.json)" >> $GITHUB_OUTPUT
          echo "api=$(jq '.tasks | map(select(.taskId == "api#build")) | length > 0' dry-run.json)" >> $GITHUB_OUTPUT

  build-web:
    needs: detect-changes
    if: needs.detect-changes.outputs.web == 'true'
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

      - name: Build and push web
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./apps/web/Dockerfile
          push: true
          tags: ghcr.io/${{ github.repository }}/web:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  build-api:
    needs: detect-changes
    if: needs.detect-changes.outputs.api == 'true'
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

      - name: Build and push api
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./apps/api/Dockerfile
          push: true
          tags: ghcr.io/${{ github.repository }}/api:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### Docker Bake를 활용한 다중 이미지 동시 빌드

Docker Bake(*Docker Bake - docker-bake.hcl 파일로 여러 이미지 빌드를 선언적으로 정의하는 도구*)를 사용하면 모노레포의 여러 앱을 동시에 빌드할 수 있다:

```hcl
// docker-bake.hcl
group "default" {
  targets = ["web", "api", "admin"]
}

target "web" {
  context    = "."
  dockerfile = "apps/web/Dockerfile"
  tags       = ["ghcr.io/my-org/web:latest"]
  cache-from = ["type=gha,scope=web"]
  cache-to   = ["type=gha,scope=web,mode=max"]
}

target "api" {
  context    = "."
  dockerfile = "apps/api/Dockerfile"
  tags       = ["ghcr.io/my-org/api:latest"]
  cache-from = ["type=gha,scope=api"]
  cache-to   = ["type=gha,scope=api,mode=max"]
}

target "admin" {
  context    = "."
  dockerfile = "apps/admin/Dockerfile"
  tags       = ["ghcr.io/my-org/admin:latest"]
  cache-from = ["type=gha,scope=admin"]
  cache-to   = ["type=gha,scope=admin,mode=max"]
}
```

```bash
# 모든 앱 동시 빌드
docker buildx bake

# 특정 앱만 빌드
docker buildx bake web api
```

Docker Bake는 BuildKit의 병렬 빌드 기능을 활용하여, 독립적인 이미지를 동시에 빌드한다. CI에서 빌드 시간을 크게 단축할 수 있다.

---

## 자주 하는 실수

### 1. 전체 모노레포를 COPY . .로 넣음

```dockerfile
# 나쁜 예
COPY . .
# apps/api, apps/admin 등 불필요한 앱까지 모두 포함됨
```

turbo prune이나 pnpm deploy를 사용하여 필요한 파일만 추출해야 한다.

### 2. lock 파일 처리 미스

```dockerfile
# 나쁜 예: lock 파일 없이 install
COPY apps/web/package.json .
RUN pnpm install
# lock 파일이 없으므로 매번 다른 버전이 설치될 수 있음
```

```dockerfile
# 좋은 예: lock 파일을 항상 함께 복사
COPY pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
```

### 3. workspace 프로토콜 무시

`workspace:*`로 선언된 의존성은 패키지 매니저의 워크스페이스 기능이 활성화된 상태에서만 해석된다. `pnpm-workspace.yaml`을 빠뜨리면 설치가 실패한다.

```dockerfile
# 나쁜 예: pnpm-workspace.yaml을 빼먹음
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
# Error: workspace:* 프로토콜을 해석할 수 없음

# 좋은 예
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
```

### 4. 공유 패키지 빌드 순서 미보장

```dockerfile
# 나쁜 예: 빌드 순서를 고려하지 않음
RUN pnpm --filter=web build
# packages/ui가 아직 빌드되지 않았으므로 실패

# 좋은 예: turbo가 의존성 순서를 자동 처리
RUN pnpm turbo build --filter=web...
```

### 5. .dockerignore 미설정

모노레포에서 `.dockerignore`가 없으면 `node_modules`, `.next`, `.turbo` 등 거대한 디렉토리가 빌드 컨텍스트에 포함된다:

```
# .dockerignore
node_modules
.next
.turbo
*.tsbuildinfo
dist
coverage
.git
```

---

## 명령어 레퍼런스

| 명령어 | 설명 |
|--------|------|
| `turbo prune <app> --docker` | 대상 앱과 의존 패키지를 Docker 최적화 구조로 추출 |
| `turbo build --filter=<app>...` | 대상 앱과 의존 패키지를 의존성 순서대로 빌드 |
| `turbo build --filter="...[HEAD^1]"` | 마지막 커밋 이후 변경에 영향받은 패키지만 빌드 |
| `pnpm deploy --filter=<app> --prod <dir>` | 대상 앱의 프로덕션 의존성을 지정 디렉토리로 추출 |
| `pnpm install --filter=<app>...` | 대상 앱과 의존 패키지의 의존성만 설치 |
| `npx nx affected -t build` | Nx 그래프 기반으로 영향받은 프로젝트만 빌드 |
| `docker buildx bake` | docker-bake.hcl에 정의된 모든 이미지를 병렬 빌드 |
| `docker buildx bake <target>` | 특정 타겟만 빌드 |

---

## 요약

- 모노레포에서 Docker 빌드의 핵심 과제는 **빌드 컨텍스트 크기**, **캐시 효율**, **공유 패키지 의존성**, **lock 파일 처리** 네 가지다
- `COPY . .`는 가장 단순하지만 이미지가 비대하고 캐시 효율이 최악이다
- **turbo prune --docker**가 현재 가장 성숙한 솔루션이다: `json/`과 `full/` 분리로 의존성 설치 캐시를 보존하면서 필요한 패키지만 추출한다
- **pnpm deploy**는 Turborepo 없이도 프로덕션 의존성을 추출할 수 있지만, 캐시 최적화 측면에서 turbo prune에 미치지 못한다
- **Nx**는 affected 기반 빌드에 강점이 있으나, Docker 전용 추출 도구는 부재하다
- 공유 패키지의 빌드 순서는 반드시 의존성 그래프를 따라야 하며, Turborepo와 Nx가 이를 자동으로 처리한다
- CI에서는 **변경 감지**를 통해 영향받은 앱만 빌드하고, **Docker Bake**로 다중 이미지를 병렬 빌드하여 파이프라인 시간을 단축한다
- Next.js 모노레포에서는 `output: 'standalone'`과 `outputFileTracingRoot` 설정이 필수다

---

## 다른 챕터와의 관계

- **Ch 4 (멀티스테이지 빌드)**: 이 챕터의 모든 Dockerfile이 멀티스테이지 패턴을 기반으로 한다. pruner → installer → builder → runner의 4단계 구조는 Ch 4의 확장이다
- **Ch 9 (이미지 최적화)**: standalone 출력, alpine 베이스, 시스템 사용자 생성 등 이미지 크기와 보안 최적화 기법은 Ch 9에서 다룬 내용의 모노레포 적용이다
- **Ch 12 (pnpm/npm 캐시)**: `json/` 디렉토리 분리와 `--frozen-lockfile`을 통한 의존성 캐시 전략은 Ch 12의 캐시 최적화를 모노레포 환경에 적용한 것이다
- **Ch 14 (CI에서 모노레포 빌드)**: 이 챕터에서 소개한 GitHub Actions 워크플로우와 Docker Bake 패턴을 Ch 14에서 더 심화하여 다룬다
