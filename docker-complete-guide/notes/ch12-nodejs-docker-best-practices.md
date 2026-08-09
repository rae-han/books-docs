# Chapter 12: Node.js + Docker 모범 사례 (Node.js Docker Best Practices)

## 핵심 질문

Node.js 애플리케이션을 Docker로 운영할 때 알아야 할 고유한 문제점과 최적의 패턴은 무엇인가? 패키지 매니저별 캐시 전략, PID 1 문제, graceful shutdown은 어떻게 처리하는가?

---

## 1. npm ci vs npm install

Node.js 프로젝트를 Docker 이미지로 빌드할 때 가장 먼저 결정해야 할 것은 **의존성 설치 명령어**다. `npm install`과 `npm ci`는 비슷해 보이지만 동작 방식이 근본적으로 다르다.

### npm install의 문제점

```bash
npm install
```

`npm install`은 `package.json`을 기준으로 의존성을 해석한다. 이 과정에서 다음과 같은 문제가 발생한다:

- **비결정적 빌드**: 시맨틱 버저닝(*Semantic Versioning - `^`, `~` 등의 범위 지정자를 사용하는 버전 관리 규칙*)의 범위 내에서 최신 버전을 설치하므로, 같은 `package.json`이라도 빌드 시점에 따라 다른 버전이 설치될 수 있다.
- **lock 파일 수정 가능**: `package-lock.json`이 존재해도, `package.json`과 불일치하면 lock 파일을 업데이트한다. Docker 빌드 중 lock 파일이 변경되면 레이어 캐시가 무효화된다.
- **기존 node_modules 병합**: 이미 `node_modules`가 존재하면 부분적으로 업데이트하므로, 이전 빌드의 잔여물이 남을 수 있다.

### npm ci가 Docker에 적합한 이유

```bash
npm ci
```

`npm ci`(*Clean Install*)는 Docker 환경을 위해 설계된 것이나 다름없다:

- **결정적 빌드**: 오직 `package-lock.json`만을 기준으로 설치한다. lock 파일에 명시된 정확한 버전이 설치된다.
- **lock 파일 불일치 시 실패**: `package.json`과 `package-lock.json`이 불일치하면 빌드가 실패한다. 이는 CI/CD 환경에서 오히려 바람직하다.
- **node_modules 완전 삭제 후 재설치**: 기존 `node_modules`를 완전히 삭제하고 처음부터 설치하므로, 깨끗한 상태를 보장한다.
- **프로덕션 전용 설치**: `--omit=dev` 플래그로 `devDependencies`를 제외할 수 있다.

### Docker에서의 올바른 사용법

```dockerfile
# 나쁜 예: npm install 사용
COPY package*.json ./
RUN npm install

# 좋은 예: npm ci 사용
COPY package.json package-lock.json ./
RUN npm ci

# 프로덕션 빌드: devDependencies 제외
COPY package.json package-lock.json ./
RUN npm ci --omit=dev
```

> **핵심 통찰**: Docker 빌드에서 `npm install`을 사용하는 것은 "어제는 됐는데 오늘은 안 되는" 문제의 가장 흔한 원인 중 하나다. `npm ci`는 **재현 가능한 빌드**를 보장하며, 이는 컨테이너화의 핵심 가치와 정확히 일치한다.

### 각 패키지 매니저의 동등 명령어

| 동작 | npm | pnpm | yarn classic | yarn berry | bun |
|------|-----|------|-------------|------------|-----|
| lock 파일 기반 설치 | `npm ci` | `pnpm install --frozen-lockfile` | `yarn install --frozen-lockfile` | `yarn install --immutable` | `bun install --frozen-lockfile` |
| 프로덕션 전용 | `--omit=dev` | `--prod` | `--production` | (별도 설정) | `--production` |
| lock 파일 | `package-lock.json` | `pnpm-lock.yaml` | `yarn.lock` | `yarn.lock` | `bun.lockb` |

---

## 2. 패키지 매니저별 Docker 캐시 전략

Docker 이미지 빌드에서 **의존성 설치는 가장 시간이 오래 걸리는 단계**다. BuildKit의 캐시 마운트(*Cache Mount - 빌드 간에 특정 디렉터리를 캐시로 유지하여 재다운로드를 방지하는 기능*)를 활용하면, 패키지 매니저의 글로벌 캐시를 빌드 간에 공유할 수 있다.

### 2.1 npm

```dockerfile
FROM node:20-alpine AS deps

WORKDIR /app

# 1. lock 파일과 package.json만 먼저 복사 (레이어 캐시 활용)
COPY package.json package-lock.json ./

# 2. BuildKit 캐시 마운트로 npm 캐시 디렉터리 유지
RUN --mount=type=cache,target=/root/.npm \
    npm ci

# 3. 프로덕션 전용 스테이지
FROM node:20-alpine AS prod-deps

WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci --omit=dev
```

npm의 글로벌 캐시(`~/.npm`)는 다운로드된 tarball을 저장한다. 캐시 마운트를 사용하면 패키지를 다시 다운로드하지 않고 캐시에서 꺼내 설치할 수 있다.

### 2.2 pnpm

pnpm은 콘텐츠 주소 지정 저장소(*Content-Addressable Store - 파일 내용의 해시를 주소로 사용하여 중복 없이 저장하는 방식*)를 사용한다. 동일한 패키지는 전체 시스템에서 단 한 번만 저장되고, 프로젝트마다 심볼릭 링크로 연결된다. 이 구조는 Docker 캐시와 시너지가 좋다.

```dockerfile
FROM node:20-alpine AS base

# corepack으로 pnpm 활성화
RUN corepack enable pnpm

WORKDIR /app

# ---

FROM base AS deps

# pnpm은 pnpm-lock.yaml과 package.json이 필요
# .npmrc가 있다면 함께 복사 (private registry 설정 등)
COPY package.json pnpm-lock.yaml ./
# COPY .npmrc ./  # private registry 사용 시

# pnpm의 content-addressable store를 캐시 마운트
RUN --mount=type=cache,target=/root/.local/share/pnpm/store \
    pnpm install --frozen-lockfile

# ---

FROM base AS prod-deps

COPY package.json pnpm-lock.yaml ./
RUN --mount=type=cache,target=/root/.local/share/pnpm/store \
    pnpm install --frozen-lockfile --prod
```

pnpm 캐시 마운트의 효과는 npm보다 더 크다. content-addressable store에 이미 존재하는 패키지는 네트워크 요청 없이 즉시 하드 링크로 설치되기 때문이다.

> **핵심 통찰**: pnpm의 store는 패키지 **내용**을 기준으로 저장하므로, 서로 다른 프로젝트에서 같은 패키지를 사용해도 단 한 번만 다운로드된다. Docker 멀티스테이지 빌드에서도 이 store를 캐시 마운트로 공유하면 빌드 시간을 극적으로 줄일 수 있다.

### 2.3 yarn (Classic v1)

```dockerfile
FROM node:20-alpine AS deps

WORKDIR /app

COPY package.json yarn.lock ./

# yarn v1의 글로벌 캐시 디렉터리를 캐시 마운트
RUN --mount=type=cache,target=/usr/local/share/.cache/yarn \
    yarn install --frozen-lockfile

# 프로덕션 전용
FROM node:20-alpine AS prod-deps

WORKDIR /app
COPY package.json yarn.lock ./
RUN --mount=type=cache,target=/usr/local/share/.cache/yarn \
    yarn install --frozen-lockfile --production
```

Yarn Classic은 `--frozen-lockfile` 플래그로 lock 파일 수정을 방지한다. 이 플래그 없이 빌드하면 `yarn.lock`이 업데이트될 수 있으므로 반드시 포함해야 한다.

### 2.4 yarn (Berry v3+ / PnP)

Yarn Berry(*Plug'n'Play*)는 `node_modules` 디렉터리를 사용하지 않는 혁신적인 패키지 관리 방식이다. 의존성을 zip 아카이브로 `.yarn/cache`에 저장하고, `.pnp.cjs` 파일로 모듈 해석을 처리한다.

```dockerfile
FROM node:20-alpine AS deps

WORKDIR /app

# Berry에 필요한 설정 파일들을 먼저 복사
COPY package.json yarn.lock .yarnrc.yml ./
COPY .yarn/releases .yarn/releases/
COPY .yarn/plugins .yarn/plugins/

# --immutable은 Berry에서의 --frozen-lockfile 동등 옵션
RUN yarn install --immutable

# 프로덕션 이미지
FROM node:20-alpine AS runner

WORKDIR /app
COPY --from=deps /app/.pnp.cjs ./
COPY --from=deps /app/.yarn .yarn/
COPY --from=deps /app/package.json ./
COPY . .

CMD ["yarn", "node", "server.js"]
```

**Zero-Install 전략**: `.yarn/cache`를 Git에 커밋하면 CI에서 `yarn install`을 생략할 수 있다. Docker 빌드에서도 COPY로 캐시를 가져오면 설치 단계가 불필요해진다.

```dockerfile
# Zero-Install 전략 (cache가 Git에 커밋된 경우)
FROM node:20-alpine

WORKDIR /app
COPY . .

# install이 필요 없다 — 이미 .yarn/cache에 모든 의존성이 있음
# 검증만 수행
RUN yarn install --immutable --immutable-cache

CMD ["yarn", "node", "server.js"]
```

단, Zero-Install은 Git 저장소 크기가 커지는 트레이드오프가 있다. 팀의 상황에 맞게 선택해야 한다.

### 2.5 bun

Bun은 Zig로 작성된 고성능 JavaScript 런타임이자 패키지 매니저다. 설치 속도가 npm 대비 수십 배 빠르다.

```dockerfile
# 방법 1: 공식 Bun 이미지 사용
FROM oven/bun:1 AS deps

WORKDIR /app

COPY package.json bun.lockb ./

RUN bun install --frozen-lockfile

# 방법 2: Node.js 이미지에 Bun 추가 설치
# Node.js API가 필요하지만 패키지 관리는 Bun으로 하고 싶을 때
FROM node:20-alpine AS deps

WORKDIR /app

RUN npm install -g bun

COPY package.json bun.lockb ./
RUN bun install --frozen-lockfile

# 프로덕션 전용
FROM oven/bun:1 AS prod-deps

WORKDIR /app
COPY package.json bun.lockb ./
RUN bun install --frozen-lockfile --production
```

`bun.lockb`는 바이너리 형식의 lock 파일이다. 텍스트 기반인 다른 lock 파일과 달리 파싱이 빠르지만, diff를 확인하기 어려운 단점이 있다.

### 패키지 매니저별 캐시 마운트 요약

| 패키지 매니저 | 캐시 경로 | lock 파일 | 결정적 설치 플래그 |
|-------------|----------|----------|-----------------|
| npm | `/root/.npm` | `package-lock.json` | `npm ci` |
| pnpm | `/root/.local/share/pnpm/store` | `pnpm-lock.yaml` | `--frozen-lockfile` |
| yarn classic | `/usr/local/share/.cache/yarn` | `yarn.lock` | `--frozen-lockfile` |
| yarn berry | (내장 `.yarn/cache`) | `yarn.lock` | `--immutable` |
| bun | `/root/.bun/install/cache` | `bun.lockb` | `--frozen-lockfile` |

---

## 3. PID 1 문제와 해결

Ch 3과 Ch 4에서 PID 1 문제의 기본을 다뤘다. 이 섹션에서는 Node.js 관점에서의 심화 내용을 다룬다.

### PID 1 문제란 무엇인가?

리눅스에서 PID 1 프로세스는 **init 프로세스**로서 특별한 책임을 진다:

1. **시그널 전달**: 자식 프로세스에 시그널을 전달하는 역할
2. **좀비 프로세스 수거**: 종료된 자식 프로세스의 리소스를 회수(*reap*)하는 역할
3. **기본 시그널 핸들러 없음**: PID 1은 명시적으로 핸들러를 등록하지 않으면 SIGTERM을 무시한다

Docker 컨테이너에서 `CMD`로 실행된 프로세스가 PID 1이 된다. Node.js는 범용 init 프로세스가 아니므로, PID 1로 실행되면 다음 문제가 발생한다:

```bash
# 컨테이너 내부에서 확인
$ docker exec my-app ps aux
PID   USER     COMMAND
  1   node     node server.js    # Node.js가 PID 1!
```

- `docker stop` → SIGTERM 전송 → Node.js가 PID 1이면 기본 시그널 핸들러가 없어 시그널 무시 → 10초 후 SIGKILL로 강제 종료
- 자식 프로세스(예: child_process.spawn)가 좀비 프로세스로 남을 수 있음

### Shell Form vs Exec Form

`CMD` 작성 방식에 따라 PID 1의 주체가 달라진다:

```dockerfile
# Shell form: sh가 PID 1이 되고, node는 자식 프로세스
CMD node server.js
# 실제 실행: /bin/sh -c "node server.js"
# PID 1: /bin/sh
# PID 2: node server.js

# Exec form: node가 PID 1
CMD ["node", "server.js"]
# 실제 실행: node server.js
# PID 1: node server.js
```

Shell form은 `sh`가 PID 1이 되는데, Alpine의 `sh`(BusyBox)는 시그널을 자식에게 전달하지 않는다. **항상 exec form을 사용해야 한다.**

### 해결책 1: tini

tini(*Tiny Init*)는 약 20KB 크기의 경량 init 프로세스다. PID 1의 책임을 올바르게 수행한다.

```dockerfile
# Alpine에서 tini 설치
FROM node:20-alpine

RUN apk add --no-cache tini

WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# tini를 ENTRYPOINT로, 실제 명령을 CMD로
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["node", "server.js"]
```

tini가 하는 일:
1. PID 1로 실행되어 시그널 핸들링을 담당
2. SIGTERM을 받으면 자식 프로세스(node)에 전달
3. 좀비 프로세스를 자동으로 수거
4. 자식 프로세스가 종료되면 자신도 동일한 종료 코드로 종료

### 해결책 2: Docker의 --init 플래그

Docker 19.03+에서는 `--init` 플래그로 tini를 자동으로 주입할 수 있다:

```bash
# Dockerfile 수정 없이 tini 사용
docker run --init my-node-app

# docker-compose.yml에서
services:
  app:
    image: my-node-app
    init: true
```

이 방법은 Dockerfile을 수정할 수 없는 상황에서 유용하다. 단, 이미지 자체에 tini가 포함되지 않으므로, 다른 환경(예: Kubernetes)에서는 별도로 설정해야 한다.

### 해결책 3: dumb-init

dumb-init은 Yelp에서 개발한 tini의 대안이다:

```dockerfile
FROM node:20-alpine

RUN apk add --no-cache dumb-init

WORKDIR /app
COPY . .

ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "server.js"]
```

### tini vs dumb-init vs 직접 시그널 핸들링 비교

| 항목 | tini | dumb-init | 직접 핸들링 |
|------|------|-----------|-----------|
| 바이너리 크기 | ~20KB | ~50KB | 0 (코드에 포함) |
| 좀비 프로세스 수거 | O | O | X (직접 구현 필요) |
| 시그널 전달 | O | O | O |
| 시그널 리매핑 | X | O | O |
| 설정 복잡도 | 낮음 | 낮음 | 높음 |
| Kubernetes 호환 | O | O | O |
| 추천 상황 | 대부분의 경우 | 시그널 리매핑 필요 시 | 자식 프로세스 없는 단순 앱 |

> **핵심 통찰**: 자식 프로세스를 spawn하는 앱이라면 tini나 dumb-init은 **필수**다. 직접 시그널 핸들링만으로는 좀비 프로세스 수거를 처리할 수 없기 때문이다. 단순 HTTP 서버라면 직접 SIGTERM 핸들링도 충분하지만, 안전을 위해 tini를 기본으로 사용하는 것을 권장한다.

---

## 4. Graceful Shutdown

컨테이너가 종료될 때 진행 중인 요청을 갑자기 끊으면 사용자 경험이 나빠지고 데이터 손실이 발생할 수 있다. 그레이스풀 셧다운(*Graceful Shutdown - 진행 중인 작업을 안전하게 마무리한 후 종료하는 패턴*)은 프로덕션 환경의 필수 요소다.

### 셧다운 시퀀스

```
docker stop 실행
    │
    ▼
SIGTERM 수신 (PID 1 → tini → node)
    │
    ▼
새로운 연결 거부 (server.close())
    │
    ▼
기존 요청 완료 대기
    │
    ▼
데이터베이스 연결 종료
    │
    ▼
메시지 큐 연결 종료
    │
    ▼
Redis 연결 종료
    │
    ▼
process.exit(0)
    │
    ▼
(타임아웃 초과 시 → SIGKILL로 강제 종료)
```

### Express 구현

```typescript
import express from 'express';
import { createServer } from 'http';

const app = express();
const server = createServer(app);

app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok' });
});

app.get('/api/data', async (req, res) => {
  // 오래 걸리는 작업 시뮬레이션
  const data = await fetchFromDatabase();
  res.json(data);
});

const PORT = process.env.PORT || 3000;

server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

// --- Graceful Shutdown ---

let isShuttingDown = false;

const shutdown = async (signal: string) => {
  if (isShuttingDown) return; // 중복 호출 방지
  isShuttingDown = true;

  console.log(`${signal} received. Starting graceful shutdown...`);

  // 1. 새로운 연결 거부
  server.close(async (err) => {
    if (err) {
      console.error('Error closing server:', err);
      process.exit(1);
    }

    try {
      // 2. 데이터베이스 연결 종료
      await database.disconnect();
      console.log('Database disconnected');

      // 3. Redis 연결 종료
      await redis.quit();
      console.log('Redis disconnected');

      // 4. 메시지 큐 연결 종료
      await messageQueue.close();
      console.log('Message queue closed');

      console.log('Graceful shutdown complete');
      process.exit(0);
    } catch (cleanupError) {
      console.error('Error during cleanup:', cleanupError);
      process.exit(1);
    }
  });

  // 3. 강제 종료 안전망: 정리 작업이 너무 오래 걸리면 강제 종료
  setTimeout(() => {
    console.error('Graceful shutdown timed out. Forcing exit.');
    process.exit(1);
  }, 10_000); // 10초
};

process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT', () => shutdown('SIGINT'));
```

### Fastify 구현

Fastify는 graceful shutdown을 내장 지원한다:

```typescript
import Fastify from 'fastify';

const app = Fastify({
  logger: true,
});

app.get('/health', async () => ({ status: 'ok' }));

const start = async () => {
  try {
    await app.listen({ port: 3000, host: '0.0.0.0' });
  } catch (err) {
    app.log.error(err);
    process.exit(1);
  }
};

const shutdown = async (signal: string) => {
  app.log.info(`${signal} received. Shutting down...`);

  // Fastify의 close()는 진행 중인 요청 완료를 기다린다
  await app.close();

  // 추가 정리 작업
  await database.disconnect();
  await redis.quit();

  process.exit(0);
};

process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT', () => shutdown('SIGINT'));

start();
```

### Next.js (Standalone 모드) 구현

Next.js의 standalone 출력을 사용할 때는 `server.js`를 직접 커스터마이징할 수 없다. 대신 래퍼 스크립트를 사용한다:

```typescript
// start.ts — Next.js standalone 서버의 graceful shutdown 래퍼
import { execSync, fork } from 'child_process';

const child = fork('./server.js', {
  env: { ...process.env },
});

const shutdown = (signal: string) => {
  console.log(`${signal} received. Shutting down Next.js...`);
  child.kill('SIGTERM');
};

child.on('exit', (code) => {
  process.exit(code ?? 0);
});

process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT', () => shutdown('SIGINT'));
```

또는 Next.js 14.1+ 에서는 `next start`가 SIGTERM을 올바르게 처리하므로, tini와 함께 사용하면 별도 래퍼 없이도 graceful shutdown이 동작한다.

### docker stop 타임아웃

```bash
# 기본 타임아웃: 10초
docker stop my-app

# 커스텀 타임아웃: 30초
docker stop --time 30 my-app

# Dockerfile에서 기본값 설정
# STOPSIGNAL SIGTERM  # 기본값
```

```yaml
# docker-compose.yml
services:
  app:
    image: my-node-app
    stop_grace_period: 30s  # SIGTERM 후 SIGKILL까지 대기 시간
```

### Kubernetes에서의 Graceful Shutdown

Kubernetes 환경에서는 `terminationGracePeriodSeconds`가 docker stop의 타임아웃 역할을 한다 (Ch 15에서 상세히 다룬다):

```yaml
# k8s deployment (미리보기)
spec:
  terminationGracePeriodSeconds: 30
  containers:
    - name: app
      lifecycle:
        preStop:
          exec:
            command: ["sh", "-c", "sleep 5"]  # 로드밸런서 반영 대기
```

Kubernetes에서의 종료 시퀀스:
1. Pod가 Terminating 상태로 변경
2. Service의 엔드포인트에서 제거 (새 트래픽 차단)
3. `preStop` 훅 실행
4. SIGTERM 전송
5. `terminationGracePeriodSeconds` 대기
6. SIGKILL 강제 종료

`preStop`에 `sleep 5`를 넣는 이유는 엔드포인트 제거와 SIGTERM 전송이 **동시에** 발생하기 때문이다. sleep 없이는 이미 라우팅된 요청이 SIGTERM 이후에 도착할 수 있다.

> **핵심 통찰**: graceful shutdown의 타임아웃은 **계층별로 설정**해야 한다. 애플리케이션 코드의 타임아웃(10초) < docker stop 타임아웃(15초) < Kubernetes terminationGracePeriodSeconds(30초)로 설정하면, 각 계층에서 안전망을 제공한다.

---

## 5. Node.js 메모리 관리

Docker 컨테이너에는 메모리 제한이 설정되어 있고, Node.js의 V8 엔진도 자체적인 힙 메모리 한도를 갖고 있다. 이 두 가지를 올바르게 조율하지 않으면 OOM(*Out of Memory - 메모리 부족으로 인한 프로세스 강제 종료*) 킬이 발생한다.

### V8 힙 한도와 컨테이너 메모리 제한

V8 엔진은 Node.js 버전과 시스템 메모리에 따라 기본 힙 한도를 자동 설정한다:

| 시스템 메모리 | V8 기본 힙 한도 (대략) |
|-------------|---------------------|
| 2GB 이하 | ~512MB |
| 2–4GB | ~1GB |
| 4GB 이상 | ~1.5GB |

문제는 Docker 컨테이너의 메모리 제한과 V8 힙 한도가 **독립적**이라는 점이다:

```bash
# 컨테이너에 512MB 메모리 제한
docker run --memory=512m my-node-app

# 하지만 V8은 시스템 메모리(호스트)를 기준으로 힙 한도를 설정할 수 있음!
# → V8이 512MB 이상 힙을 잡으려고 하면 → OOM Kill
```

Node.js 12.0+ 부터는 `--max-semi-space-size`와 `--max-old-space-size`가 cgroup 메모리 제한을 인식하지만, 완벽하지 않다. 명시적으로 설정하는 것이 안전하다.

### --max-old-space-size 설정 공식

V8 힙은 Node.js 프로세스가 사용하는 메모리의 일부에 불과하다. 나머지는 네이티브 메모리(Buffer, C++ 애드온 등), 스택, 코드 공간 등이 차지한다:

```
컨테이너 메모리 = V8 힙 + 네이티브 메모리 + 스택 + 기타 오버헤드
```

**권장 공식**: `--max-old-space-size`를 컨테이너 메모리의 약 **75%**로 설정한다.

```dockerfile
# 컨테이너 메모리 512MB → V8 힙 384MB
ENV NODE_OPTIONS="--max-old-space-size=384"

# 컨테이너 메모리 1GB → V8 힙 768MB
ENV NODE_OPTIONS="--max-old-space-size=768"

# 컨테이너 메모리 2GB → V8 힙 1536MB
ENV NODE_OPTIONS="--max-old-space-size=1536"
```

```yaml
# docker-compose.yml
services:
  app:
    image: my-node-app
    deploy:
      resources:
        limits:
          memory: 512M
    environment:
      - NODE_OPTIONS=--max-old-space-size=384
```

### NODE_OPTIONS 환경변수

`NODE_OPTIONS`는 V8 및 Node.js 런타임 옵션을 환경변수로 전달하는 공식 방법이다:

```dockerfile
# 여러 옵션을 공백으로 구분
ENV NODE_OPTIONS="--max-old-space-size=384 --max-http-header-size=16384"
```

```yaml
# docker-compose.yml에서
environment:
  - NODE_OPTIONS=--max-old-space-size=384 --dns-result-order=ipv4first
```

주의: `NODE_OPTIONS`에 넣을 수 없는 옵션도 있다 (예: `--eval`, `--print`). 보안상의 이유다.

### UV_THREADPOOL_SIZE

Node.js는 libuv의 스레드 풀을 사용하여 비동기 파일 I/O, DNS 조회 등을 처리한다. 기본 스레드 풀 크기는 **4**다:

```typescript
// 기본값: 4개 스레드
// 파일 I/O가 많은 앱에서는 병목이 될 수 있다

// 최대 1024까지 설정 가능
process.env.UV_THREADPOOL_SIZE = '8';
```

```dockerfile
# Dockerfile에서 설정
ENV UV_THREADPOOL_SIZE=8

# 컨테이너 CPU 코어 수에 맞게 설정하는 것이 일반적
# 공식: Math.ceil(CPU 코어 수 * 1.5)
```

| 컨테이너 CPU 코어 | 권장 UV_THREADPOOL_SIZE |
|----------------|----------------------|
| 1 | 4 (기본값 유지) |
| 2 | 4~8 |
| 4 | 8~12 |
| 8 | 12~16 |

너무 큰 값은 컨텍스트 스위칭 오버헤드를 증가시키므로, 벤치마크를 통해 최적값을 찾아야 한다.

---

## 6. .dockerignore for Node.js

`.dockerignore` 파일은 Docker 빌드 컨텍스트에서 불필요한 파일을 제외한다. Node.js 프로젝트에서는 `node_modules`가 가장 중요한 제외 대상이다.

### 완전한 .dockerignore 예시

```bash
# ===== 의존성 =====
node_modules
.pnp.*
.yarn/cache
.yarn/unplugged
.yarn/build-state.yml
.yarn/install-state.gz

# ===== 빌드 산출물 =====
dist
build
.next
out
.turbo
.vercel

# ===== 개발 도구 =====
.git
.gitignore
.eslintrc*
.eslintignore
.prettierrc*
.prettierignore
.editorconfig
tsconfig.tsbuildinfo

# ===== 테스트 =====
__tests__
__mocks__
*.test.ts
*.test.tsx
*.spec.ts
*.spec.tsx
coverage
.nyc_output
jest.config.*
vitest.config.*
playwright.config.*
cypress

# ===== Docker 관련 =====
Dockerfile*
docker-compose*
.dockerignore

# ===== IDE =====
.vscode
.idea
*.swp
*.swo
*~

# ===== 환경 설정 =====
.env
.env.*
!.env.example

# ===== 문서 / 기타 =====
README.md
CHANGELOG.md
LICENSE
docs

# ===== OS 파일 =====
.DS_Store
Thumbs.db

# ===== Storybook =====
.storybook
*.stories.tsx

# ===== CI/CD =====
.github
.gitlab-ci.yml
.circleci
Jenkinsfile
```

> **핵심 통찰**: `node_modules`를 `.dockerignore`에 포함하는 것은 단순히 빌드 속도를 위한 것이 아니다. 로컬의 `node_modules`에는 운영체제별 네이티브 바이너리가 포함될 수 있다. macOS에서 빌드한 `node_modules`를 Linux 컨테이너에 복사하면 네이티브 모듈이 동작하지 않는다. **항상 컨테이너 내부에서 npm ci로 설치해야 한다.**

---

## 7. 완전한 프로덕션 Dockerfile

지금까지 다룬 모든 모범 사례를 종합한 프로덕션급 Dockerfile이다. Next.js standalone 모드 + pnpm + tini + 비루트 사용자 + 헬스체크를 결합한다.

```dockerfile
# ============================================================
# Stage 0: Base — 공통 설정
# ============================================================
FROM node:20-alpine AS base

# tini 설치 (PID 1 문제 해결)
RUN apk add --no-cache tini

# corepack으로 pnpm 활성화
RUN corepack enable pnpm

WORKDIR /app

# ============================================================
# Stage 1: Dependencies — 의존성 설치
# ============================================================
FROM base AS deps

# lock 파일과 package.json만 먼저 복사 (레이어 캐시 최적화)
COPY package.json pnpm-lock.yaml ./

# pnpm store를 BuildKit 캐시 마운트로 유지
RUN --mount=type=cache,target=/root/.local/share/pnpm/store \
    pnpm install --frozen-lockfile

# ============================================================
# Stage 2: Builder — 애플리케이션 빌드
# ============================================================
FROM base AS builder

# deps 스테이지에서 node_modules 복사
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Next.js standalone 빌드를 위한 환경변수
ENV NEXT_TELEMETRY_DISABLED=1

# Next.js 빌드
RUN pnpm build

# ============================================================
# Stage 3: Runner — 프로덕션 실행
# ============================================================
FROM node:20-alpine AS runner

# tini만 설치 (pnpm, 빌드 도구 불필요)
RUN apk add --no-cache tini

WORKDIR /app

# 보안: 비루트 사용자 생성 및 전환
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Next.js standalone 출력 복사
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

# 환경변수 설정
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# V8 메모리 설정 (컨테이너 메모리의 ~75%에 맞게 조정)
ENV NODE_OPTIONS="--max-old-space-size=384"

# 비루트 사용자로 전환
USER nextjs

# 포트 노출
EXPOSE 3000

# 헬스체크 (30초 간격, 3초 타임아웃, 3회 재시도)
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD ["node", "-e", " \
      const http = require('http'); \
      const req = http.get('http://localhost:3000/api/health', (res) => { \
        process.exit(res.statusCode === 200 ? 0 : 1); \
      }); \
      req.on('error', () => process.exit(1)); \
      req.setTimeout(2000, () => { req.destroy(); process.exit(1); }); \
    "]

# tini를 PID 1로, Node.js를 자식 프로세스로 실행
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["node", "server.js"]
```

### 각 요소가 해결하는 문제

| Dockerfile 요소 | 해결하는 문제 | 관련 섹션 |
|----------------|-------------|---------|
| `node:20-alpine` | 이미지 크기 최소화 | Ch 9 |
| 멀티스테이지 빌드 | devDependencies, 빌드 도구 제거 | Ch 9 |
| `pnpm install --frozen-lockfile` | 결정적 빌드 보장 | 섹션 1, 2 |
| `--mount=type=cache` | 빌드 속도 향상 | 섹션 2 |
| `tini` | PID 1 시그널 핸들링, 좀비 프로세스 수거 | 섹션 3 |
| `adduser --system` | 비루트 실행으로 보안 강화 | Ch 9 |
| `NEXT_TELEMETRY_DISABLED=1` | 불필요한 네트워크 요청 제거 | - |
| `NODE_OPTIONS` | V8 메모리 한도와 컨테이너 제한 조율 | 섹션 5 |
| `HEALTHCHECK` | 컨테이너 상태 모니터링 | Ch 11 |
| Next.js standalone | 서버에 필요한 파일만 포함 (~100MB 절감) | Ch 9 |

### 이미지 크기 비교

| 구성 | 이미지 크기 (대략) |
|-----|-----------------|
| `node:20` + `npm install` + 전체 소스 | ~1.2GB |
| `node:20-alpine` + `npm ci` | ~400MB |
| `node:20-alpine` + 멀티스테이지 + standalone | ~150MB |
| 위 Dockerfile (모든 최적화 적용) | ~130MB |

---

## 8. Apple Silicon과 멀티 플랫폼

### 8.1 왜 문제가 되는가

Apple Silicon(M1/M2/M3/M4) Mac은 **arm64** 아키텍처를 사용하지만, 대부분의 프로덕션 서버와 CI 러너는 **amd64**(x86_64)를 사용한다. 도커 이미지는 특정 아키텍처에 종속되므로, M1 Mac에서 빌드한 이미지를 amd64 서버에서 실행하면 `exec format error`가 발생한다.

```bash
# M1 Mac에서 빌드 (arm64 이미지가 생성됨)
docker build -t my-app:latest .

# amd64 서버에서 실행 시
docker run my-app:latest
# exec /usr/local/bin/node: exec format error
```

Docker Desktop은 QEMU 에뮬레이션을 통해 다른 아키텍처의 이미지를 **로컬에서 실행**하는 것은 지원하지만, 빌드된 이미지의 아키텍처는 호스트와 동일하다.

### 8.2 빌드 시 플랫폼 명시

가장 간단한 해결책은 빌드 시 타겟 플랫폼을 명시하는 것이다:

```bash
# amd64 이미지를 M1 Mac에서 빌드 (QEMU 에뮬레이션)
docker build --platform linux/amd64 -t my-app:latest .
```

이 방식은 QEMU 에뮬레이션을 사용하므로 네이티브 빌드보다 **3~10배 느리다**. 특히 `npm ci`나 `npm run build` 같은 무거운 단계에서 체감된다.

> **실무 팁**: 로컬 개발에서는 네이티브 arm64로 빌드하여 빠른 피드백을 받고, CI에서만 amd64(또는 멀티 플랫폼)로 빌드하는 것이 가장 효율적이다. 로컬에서 `--platform linux/amd64`를 상시 사용할 필요는 없다.

### 8.3 Native Addon 호환성

Node.js의 native addon(C/C++ 바인딩)은 아키텍처에 종속적이다. 대부분의 인기 패키지는 prebuilt 바이너리를 제공하지만, 아키텍처별로 다른 바이너리가 필요하다.

| 패키지 | arm64 지원 | 주의사항 |
|--------|-----------|---------|
| `sharp` | prebuilt 제공 | `npm install` 시 자동으로 올바른 바이너리 다운로드 |
| `bcrypt` | 소스 빌드 필요 | `python3`, `make`, `g++` 빌드 도구 필요 |
| `sqlite3` | prebuilt 제공 | Alpine musl + arm64 조합은 소스 빌드 필요할 수 있음 |
| `canvas` | 소스 빌드 필요 | Cairo, Pango 등 시스템 라이브러리 필요 |
| `esbuild` | prebuilt 제공 | 플랫폼별 선택적 의존성(`@esbuild/linux-arm64` 등) |

**문제가 되는 시나리오:**

로컬(arm64)에서 `node_modules`를 설치한 후 컨테이너(amd64)에 복사하면, arm64용 바이너리가 amd64 환경에서 작동하지 않는다:

```dockerfile
# 절대 하지 말 것: 로컬 node_modules를 복사
COPY node_modules ./node_modules

# 올바른 방법: 컨테이너 내부에서 설치
COPY package.json package-lock.json ./
RUN npm ci
```

이것이 `.dockerignore`에 `node_modules`를 반드시 포함해야 하는 이유 중 하나다.

### 8.4 멀티 플랫폼 Dockerfile 패턴

arm64와 amd64 모두 지원하는 Dockerfile을 작성할 때는 아키텍처에 따라 분기가 필요한 경우가 거의 없다. 대부분의 Node.js 패키지와 Alpine apk 패키지는 양쪽 아키텍처를 모두 지원한다.

```dockerfile
# 멀티 플랫폼 호환 Dockerfile — 특별한 처리 불필요
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
USER nextjs
EXPOSE 3000
CMD ["node", "server.js"]
```

```bash
# buildx로 멀티 플랫폼 빌드
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag ghcr.io/my-org/my-app:latest \
  --push .
```

다만, 특정 아키텍처에서만 필요한 시스템 패키지가 있다면 `TARGETPLATFORM` 빌드 인수를 활용할 수 있다:

```dockerfile
FROM node:20-alpine AS builder
ARG TARGETPLATFORM

# 아키텍처별 분기가 필요한 드문 경우
RUN if [ "$TARGETPLATFORM" = "linux/arm64" ]; then \
      apk add --no-cache vips-dev; \
    fi
```

> **핵심 통찰**: Node.js 프로젝트에서 멀티 플랫폼 호환성 문제의 대부분은 **로컬 `node_modules`를 컨테이너에 복사**하거나 **`.dockerignore` 미설정**에서 발생한다. Dockerfile 안에서 `npm ci`를 실행하는 기본 패턴만 지키면, 대부분의 프로젝트는 별도의 플랫폼 분기 없이 arm64/amd64 모두에서 정상 동작한다.

---

## 자주 하는 실수

### 1. npm install 사용

```dockerfile
# 나쁜 예
RUN npm install

# 좋은 예
RUN npm ci --omit=dev
```

`npm install`은 비결정적이며 lock 파일을 수정할 수 있다. Docker 빌드에서는 항상 `npm ci`를 사용한다.

### 2. PID 1 미처리

```dockerfile
# 나쁜 예: Node.js가 PID 1로 직접 실행
CMD ["node", "server.js"]

# 좋은 예: tini를 통해 실행
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["node", "server.js"]
```

PID 1 문제를 무시하면 `docker stop`이 SIGTERM을 보내도 Node.js가 이를 무시하고, 10초 후 SIGKILL로 강제 종료된다.

### 3. Graceful Shutdown 미구현

시그널 핸들러 없이 서버를 실행하면, 종료 시 진행 중인 요청이 끊기고 데이터베이스 연결이 정리되지 않는다. `process.on('SIGTERM', ...)` 핸들러는 프로덕션 필수 요소다.

### 4. 메모리 제한 미설정

```dockerfile
# 나쁜 예: 메모리 설정 없음 → OOM Kill 위험
CMD ["node", "server.js"]

# 좋은 예: 컨테이너 메모리의 75%로 힙 제한
ENV NODE_OPTIONS="--max-old-space-size=384"
```

### 5. node_modules를 이미지에 복사

```dockerfile
# 나쁜 예: 로컬 node_modules를 컨테이너에 복사
COPY . .
# → macOS의 네이티브 바이너리가 Linux 컨테이너에서 동작하지 않음

# 좋은 예: .dockerignore에 node_modules 포함 + 컨테이너 내에서 설치
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY . .
```

### 6. devDependencies 포함

```dockerfile
# 나쁜 예: 모든 의존성 설치
RUN npm ci

# 좋은 예: 프로덕션 의존성만 설치
RUN npm ci --omit=dev
```

eslint, typescript, jest 등 개발 도구가 프로덕션 이미지에 포함되면 이미지 크기가 불필요하게 커지고, 공격 표면이 넓어진다.

---

## 명령어 레퍼런스

| 명령어 | 설명 |
|-------|------|
| `npm ci` | lock 파일 기반 결정적 설치 |
| `npm ci --omit=dev` | 프로덕션 의존성만 설치 |
| `pnpm install --frozen-lockfile` | pnpm 결정적 설치 |
| `pnpm install --frozen-lockfile --prod` | pnpm 프로덕션 전용 설치 |
| `yarn install --frozen-lockfile` | yarn classic 결정적 설치 |
| `yarn install --immutable` | yarn berry 결정적 설치 |
| `bun install --frozen-lockfile` | bun 결정적 설치 |
| `docker run --init <image>` | Docker 내장 tini로 컨테이너 실행 |
| `docker stop <container>` | SIGTERM 전송 (기본 10초 후 SIGKILL) |
| `docker stop --time 30 <container>` | SIGTERM 전송 (30초 후 SIGKILL) |
| `apk add --no-cache tini` | Alpine에 tini 설치 |
| `node --max-old-space-size=384` | V8 힙 한도 384MB로 설정 |

---

## 요약

- Docker에서 Node.js 의존성을 설치할 때는 **항상 lock 파일 기반의 결정적 설치 명령어**를 사용한다 (`npm ci`, `pnpm install --frozen-lockfile` 등). `npm install`은 비결정적이므로 Docker 빌드에 적합하지 않다.
- 각 패키지 매니저의 **글로벌 캐시 디렉터리를 BuildKit 캐시 마운트**로 연결하면, 빌드 간에 다운로드된 패키지를 재사용하여 빌드 속도를 크게 향상시킬 수 있다.
- **PID 1 문제**는 Node.js 컨테이너에서 반드시 해결해야 하는 문제다. tini나 dumb-init 같은 경량 init 프로세스를 사용하거나, `docker run --init`을 활용한다.
- **Graceful shutdown**은 SIGTERM 수신 → 새 연결 거부 → 기존 요청 완료 → 리소스 정리 → 종료의 순서로 구현한다. 강제 종료 안전망(setTimeout)도 반드시 포함한다.
- V8 힙 메모리 한도(`--max-old-space-size`)를 **컨테이너 메모리 제한의 약 75%**로 설정하여 OOM Kill을 방지한다. `NODE_OPTIONS` 환경변수로 전달하는 것이 가장 깔끔하다.
- `.dockerignore`에 `node_modules`, 테스트 파일, IDE 설정, `.git` 등을 포함하여 빌드 컨텍스트를 최소화한다.
- 모든 모범 사례를 종합하면: **Alpine 이미지 + 멀티스테이지 빌드 + 결정적 의존성 설치 + tini + 비루트 사용자 + 메모리 설정 + 헬스체크**가 프로덕션 Dockerfile의 표준 구성이다.
- Apple Silicon Mac에서 개발할 때는 로컬 `node_modules`를 컨테이너에 복사하지 않고, **컨테이너 내부에서 의존성을 설치**하는 것만으로 대부분의 아키텍처 호환성 문제를 해결할 수 있다.

---

## 다른 챕터와의 관계

- **Ch 3 (컨테이너 라이프사이클)**: PID 1 문제와 시그널 처리의 기본 개념을 소개했다. 이 챕터에서는 Node.js 관점에서 tini, dumb-init, graceful shutdown으로 심화한다.
- **Ch 4 (Dockerfile 작성)**: `CMD`의 shell form vs exec form, `ENTRYPOINT`와 `CMD`의 조합 등 Dockerfile 기초를 다뤘다. 이 챕터에서는 그 위에 Node.js 특화 패턴을 쌓는다.
- **Ch 9 (이미지 최적화)**: 멀티스테이지 빌드, Alpine 이미지, 레이어 캐시 등 일반적인 이미지 최적화를 다뤘다. 이 챕터에서는 Node.js의 패키지 매니저별 캐시 전략과 standalone 빌드 등 언어 특화 최적화를 다룬다.
- **Ch 11 (컨테이너 모니터링)**: OOM Kill, 메모리 모니터링 등을 소개했다. 이 챕터에서는 V8 힙 한도 설정으로 OOM을 사전에 방지하는 방법을 다룬다.
- **Ch 13 (모노레포와 Docker)**: 모노레포 환경에서의 Node.js Docker 빌드는 이 챕터의 패키지 매니저 지식을 기반으로 확장된다. 특히 pnpm workspace와 Turborepo의 Docker 빌드 전략을 다룬다.
- **Ch 14 (CI/CD)**: 이 챕터의 Apple Silicon 섹션에서 다룬 멀티 플랫폼 개념은, Ch 14에서 `docker buildx`와 GitHub Actions를 활용한 CI 멀티 플랫폼 빌드 파이프라인으로 확장된다.
- **Ch 15 (Kubernetes 배포)**: graceful shutdown의 Kubernetes 확장 — `terminationGracePeriodSeconds`, `preStop` 훅, readiness probe 등을 이 챕터의 기초 위에 다룬다.
