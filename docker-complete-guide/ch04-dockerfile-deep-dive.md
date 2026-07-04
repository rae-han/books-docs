# Chapter 4: Dockerfile 완전 정복: Dockerfile Deep Dive

## 핵심 질문

Dockerfile의 각 인스트럭션은 어떤 역할을 하며, 어떻게 조합해야 효율적인 이미지를 만들 수 있는가? 멀티스테이지 빌드는 왜 필요하고 어떻게 활용하는가?

---

## 1. Dockerfile 기초

### 1.1 Dockerfile이란

Dockerfile은 Docker 이미지를 빌드하기 위한 **텍스트 기반 명세서**다. 어떤 베이스 이미지를 사용할지, 어떤 파일을 복사할지, 어떤 명령어를 실행할지를 순차적으로 기술한다. Docker Engine은 이 명세서를 위에서 아래로 읽으며 각 인스트럭션(*Instruction - Dockerfile에서 하나의 작업 단위를 나타내는 명령어*)을 실행하고, 그 결과를 레이어로 쌓아 최종 이미지를 생성한다.

Dockerfile은 **재현 가능한 빌드(reproducible build)** 를 보장한다. 동일한 Dockerfile과 소스 코드로 빌드하면 어떤 환경에서든 동일한 이미지가 만들어진다. 이것이 수동으로 서버를 설정하는 것과의 근본적인 차이다.

### 1.2 빌드 컨텍스트(Build Context)

`docker build` 명령어를 실행하면 Docker CLI는 지정된 디렉토리의 모든 파일과 하위 디렉토리를 **tar 아카이브로 묶어 Docker Daemon에 전송**한다. 이 전송되는 파일 집합을 빌드 컨텍스트(*Build Context - Docker 빌드 시 Daemon에 전달되는 파일과 디렉토리의 집합*)라 한다.

```bash
# 현재 디렉토리를 빌드 컨텍스트로 사용하여 이미지 빌드
docker build -t my-next-app .

# 마지막의 '.'이 빌드 컨텍스트 경로를 지정한다
# 이 디렉토리의 모든 파일이 Docker Daemon에 전송됨
```

빌드 시작 시 다음과 같은 메시지가 출력된다:

```
Sending build context to Docker daemon  234.5MB
```

만약 `node_modules`나 `.git` 폴더가 포함되어 있다면 수백 MB에서 수 GB까지 전송될 수 있다. 이는 빌드 시간을 크게 증가시키므로 `.dockerignore` 파일로 불필요한 파일을 제외해야 한다(섹션 3에서 상세히 다룬다).

> **핵심 통찰**: Dockerfile의 `COPY` 인스트럭션은 **빌드 컨텍스트 내의 파일만** 복사할 수 있다. 빌드 컨텍스트 바깥의 파일(예: 상위 디렉토리)은 `COPY ../some-file`처럼 접근할 수 없다. 이 제약은 빌드의 재현성을 보장하기 위한 의도적 설계다.

### 1.3 `docker build` 명령어와 빌드 프로세스

`docker build`의 기본 형태와 주요 옵션:

```bash
# 기본 빌드 — 현재 디렉토리의 Dockerfile 사용
docker build -t my-next-app:1.0 .

# Dockerfile 경로를 명시적으로 지정
docker build -f Dockerfile.prod -t my-next-app:prod .

# 빌드 인자 전달
docker build --build-arg NODE_ENV=production -t my-next-app .

# 특정 스테이지만 빌드 (멀티스테이지)
docker build --target builder -t my-next-app:builder .

# 캐시 없이 완전 새로 빌드
docker build --no-cache -t my-next-app .
```

빌드 프로세스의 내부 동작:

```
1. Docker CLI가 빌드 컨텍스트를 tar로 묶어 Daemon에 전송
2. Daemon이 Dockerfile을 파싱
3. 각 인스트럭션을 순차적으로 실행:
   a. 임시 컨테이너 생성
   b. 인스트럭션 실행 (RUN, COPY 등)
   c. 결과를 새 레이어로 커밋
   d. 임시 컨테이너 삭제
4. 모든 인스트럭션이 완료되면 최종 이미지 생성
5. -t 옵션으로 지정한 이름:태그를 이미지에 부여
```

### 1.4 기본 Dockerfile 예제 — Next.js 앱

가장 기본적인 형태의 Next.js Dockerfile을 살펴보자:

```dockerfile
# 베이스 이미지: Node.js 20 + Alpine Linux
FROM node:20-alpine

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 먼저 복사 (레이어 캐시 활용)
COPY package*.json ./

# 의존성 설치 (clean install로 재현성 보장)
RUN npm ci

# 소스 코드 복사
COPY . .

# Next.js 빌드
RUN npm run build

# 문서화: 컨테이너가 3000번 포트를 사용한다는 표시
EXPOSE 3000

# 컨테이너 시작 시 실행할 명령어
CMD ["npm", "start"]
```

이 Dockerfile은 7개의 인스트럭션으로 구성되어 있다. 각 인스트럭션이 어떤 역할을 하는지 다음 섹션에서 하나씩 상세히 살펴본다.

---

## 2. 모든 Dockerfile 인스트럭션 상세

### 2.1 FROM — 베이스 이미지 지정

모든 Dockerfile은 `FROM` 인스트럭션으로 시작한다. 어떤 이미지를 기반으로 새 이미지를 만들 것인지 지정한다.

**문법:**

```dockerfile
FROM <이미지>[:<태그>] [AS <스테이지_이름>]
```

**예제:**

```dockerfile
# 기본 사용
FROM node:20-alpine

# 멀티스테이지 빌드에서 스테이지 이름 부여
FROM node:20-alpine AS builder

# 다이제스트로 정확한 이미지 지정 (가장 안전한 방법)
FROM node@sha256:a1b2c3d4e5f6...

# 빈 이미지에서 시작 (Go 같은 정적 바이너리 언어에서 사용)
FROM scratch
```

**Node.js 베이스 이미지 비교:**

| 이미지 | 기반 OS | 크기 | 특징 | 권장 상황 |
|--------|---------|------|------|-----------|
| `node:20` | Debian (Bookworm) | ~1.1GB | 모든 시스템 라이브러리 포함 | native addon 빌드 필요 시 |
| `node:20-slim` | Debian (최소) | ~240MB | 필수 라이브러리만 포함 | 프로덕션 일반 용도 |
| `node:20-alpine` | Alpine Linux | ~130MB | musl libc, 경량 | 프로덕션 경량 이미지 |
| `gcr.io/distroless/nodejs20` | Distroless | ~120MB | 셸/패키지 매니저 없음 | 보안 최우선 환경 |

> **실무 팁**: Node.js 프로젝트에서는 **`node:20-alpine`** 이 가장 널리 사용된다. 단, `bcrypt`, `sharp` 같은 native addon을 사용하는 프로젝트에서 Alpine의 musl libc로 인해 호환성 문제가 발생할 수 있다. 이 경우 빌드 스테이지에서는 `node:20`을, 프로덕션 스테이지에서는 `node:20-alpine`을 사용하는 멀티스테이지 전략이 효과적이다.

### 2.2 WORKDIR — 작업 디렉토리 설정

`WORKDIR`은 이후 모든 `RUN`, `CMD`, `ENTRYPOINT`, `COPY`, `ADD` 인스트럭션의 작업 디렉토리를 설정한다. 해당 디렉토리가 존재하지 않으면 **자동으로 생성**한다.

**문법:**

```dockerfile
WORKDIR /경로
```

**예제:**

```dockerfile
WORKDIR /app

# 이후 모든 명령어는 /app 기준으로 실행된다
COPY package.json ./       # /app/package.json으로 복사됨
RUN npm ci                 # /app에서 npm ci 실행
COPY . .                   # /app으로 모든 파일 복사
```

`WORKDIR`은 `mkdir -p /app && cd /app`과 동일한 효과이지만, 중요한 차이가 있다:

```dockerfile
# 나쁜 예: RUN으로 디렉토리 이동 — 다음 인스트럭션에 영향을 주지 않는다
RUN cd /app         # 이 RUN이 끝나면 cd 효과 사라짐
RUN npm ci          # /에서 실행됨 (의도와 다름!)

# 좋은 예: WORKDIR 사용 — 이후 모든 인스트럭션에 적용
WORKDIR /app
RUN npm ci          # /app에서 실행됨
```

각 `RUN` 인스트럭션은 독립된 셸에서 실행되므로 `cd`의 효과는 해당 `RUN` 내에서만 유효하다. `WORKDIR`은 **Dockerfile 전체에 걸쳐 지속**되는 작업 디렉토리를 설정한다.

### 2.3 COPY vs ADD — 파일 복사

#### COPY

빌드 컨텍스트의 파일이나 디렉토리를 이미지 안으로 복사한다.

```dockerfile
# 파일 복사
COPY package.json ./

# 여러 파일 복사 (와일드카드 지원)
COPY package.json pnpm-lock.yaml ./

# 디렉토리 전체 복사
COPY src/ ./src/

# 다른 스테이지에서 파일 복사 (멀티스테이지)
COPY --from=builder /app/.next/standalone ./

# 소유권 변경과 함께 복사
COPY --chown=nextjs:nodejs package.json ./
```

#### ADD

`COPY`의 기능에 추가로 두 가지 특수 기능을 지원한다:

```dockerfile
# URL에서 파일 다운로드 (비권장 — 레이어 캐시 제어 불가)
ADD https://example.com/config.json ./

# tar 파일 자동 해제
ADD app.tar.gz /app/
```

#### 왜 거의 항상 COPY를 써야 하는가?

```dockerfile
# 나쁜 예: ADD의 암묵적 동작이 혼란을 일으킨다
ADD . .
# → 만약 빌드 컨텍스트에 .tar.gz 파일이 있다면 자동으로 해제된다!
#   이 동작을 의도하지 않았다면 예상치 못한 결과가 발생

# 좋은 예: COPY는 항상 단순 복사만 수행 — 동작이 명확하다
COPY . .
```

Docker 공식 베스트 프랙티스에서도 **`ADD` 대신 `COPY`를 사용하라**고 권장한다. `ADD`는 tar 해제가 명시적으로 필요한 경우에만 사용한다.

### 2.4 RUN — 명령어 실행

이미지 빌드 시점에 명령어를 실행하고 그 결과를 새 레이어로 커밋한다. 의존성 설치, 빌드, 디렉토리 생성 등에 사용한다.

**두 가지 형식:**

```dockerfile
# Shell form — /bin/sh -c "..." 로 실행된다
RUN npm ci
RUN echo "Hello" && echo "World"

# Exec form — 셸을 거치지 않고 직접 실행한다
RUN ["npm", "ci"]
RUN ["sh", "-c", "echo Hello && echo World"]
```

Shell form은 환경변수 치환(`$HOME` 등)이 가능하지만, exec form은 셸을 거치지 않으므로 환경변수를 직접 해석하지 않는다.

**레이어 최적화 — `&&`로 체이닝:**

각 `RUN`은 새 레이어를 생성한다. 관련된 명령어는 `&&`로 연결하여 하나의 레이어로 만드는 것이 좋다:

```dockerfile
# 나쁜 예: 3개의 레이어 생성
RUN apt-get update
RUN apt-get install -y curl
RUN rm -rf /var/lib/apt/lists/*

# 좋은 예: 1개의 레이어 생성
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*
```

나쁜 예에서 `apt-get update`가 캐시되면, 이후 빌드에서 `apt-get install`이 캐시된 (오래된) 패키지 인덱스를 사용하여 이전 버전의 패키지가 설치될 수 있다. `&&`로 체이닝하면 `update`와 `install`이 항상 함께 실행되어 이 문제를 방지한다.

> **핵심 통찰**: `RUN`의 레이어 체이닝은 단순히 레이어 수를 줄이는 것 이상의 의미가 있다. 관련 명령어가 항상 함께 실행되도록 강제하여 **빌드의 일관성**을 보장한다.

### 2.5 CMD vs ENTRYPOINT — 컨테이너 시작 명령어

이 두 인스트럭션은 컨테이너가 **시작될 때** 실행할 명령어를 정의한다. `RUN`은 이미지 빌드 시에 실행되고, `CMD`/`ENTRYPOINT`는 컨테이너 실행 시에 동작한다는 점이 근본적으로 다르다.

#### CMD — 기본 명령어

```dockerfile
# Exec form (권장)
CMD ["node", "server.js"]

# Shell form (비권장 — PID 1 문제 발생)
CMD node server.js
```

`CMD`는 `docker run` 시 **덮어쓸 수 있다**:

```bash
# Dockerfile의 CMD 대신 sh를 실행
docker run my-next-app sh
```

#### ENTRYPOINT — 고정 명령어

```dockerfile
ENTRYPOINT ["node", "server.js"]
```

`ENTRYPOINT`는 `docker run` 시 **덮어쓸 수 없다** (명시적으로 `--entrypoint`를 사용해야만 변경 가능):

```bash
# ENTRYPOINT가 설정된 경우, 추가 인자만 전달된다
docker run my-next-app --port 8080
# → node server.js --port 8080 으로 실행됨
```

#### CMD + ENTRYPOINT 조합 패턴

가장 유연한 패턴은 `ENTRYPOINT`로 고정 실행 파일을 지정하고, `CMD`로 기본 인자를 제공하는 것이다:

```dockerfile
ENTRYPOINT ["node"]
CMD ["server.js"]
```

```bash
# 기본: node server.js 실행
docker run my-app

# CMD를 덮어쓰기: node repl.js 실행
docker run my-app repl.js

# ENTRYPOINT까지 덮어쓰기
docker run --entrypoint sh my-app
```

#### PID 1 문제 — Shell form vs Exec form

Shell form을 사용하면 명령어가 `/bin/sh -c`의 자식 프로세스로 실행된다. 이때 `sh`가 PID 1이 되어 SIGTERM 시그널을 Node.js 프로세스에 전달하지 못한다:

```dockerfile
# 나쁜 예: Shell form
CMD node server.js
# PID 1: /bin/sh -c "node server.js"
# PID 2: node server.js
# → docker stop 시 sh가 SIGTERM을 받지만 node에 전달하지 않음
# → 10초 후 SIGKILL로 강제 종료 (graceful shutdown 불가)

# 좋은 예: Exec form
CMD ["node", "server.js"]
# PID 1: node server.js
# → docker stop 시 node가 직접 SIGTERM을 받음
# → process.on('SIGTERM', ...) 핸들러가 정상 동작
```

Node.js에서 graceful shutdown을 구현한 예:

```typescript
// server.ts
const server = app.listen(3000, () => {
  console.log('Server started on port 3000');
});

process.on('SIGTERM', () => {
  console.log('SIGTERM received. Shutting down gracefully...');
  server.close(() => {
    console.log('HTTP server closed');
    process.exit(0);
  });
});
```

이 코드가 정상 동작하려면 **반드시 exec form으로 `CMD`를 작성**해야 한다.

> **핵심 통찰**: `CMD`와 `ENTRYPOINT`는 항상 exec form(`["executable", "arg1"]`)으로 작성하라. Shell form(`executable arg1`)은 PID 1 문제로 인해 SIGTERM이 애플리케이션에 전달되지 않아 graceful shutdown이 불가능하다.

### 2.6 ENV vs ARG — 환경변수

#### ENV — 빌드 + 런타임

`ENV`로 설정한 환경변수는 **빌드 시점과 컨테이너 런타임** 모두에서 사용할 수 있다.

```dockerfile
ENV NODE_ENV=production
ENV PORT=3000

# 빌드 시점에 사용 가능
RUN echo $NODE_ENV            # "production" 출력

# 컨테이너 런타임에도 유지됨
CMD ["node", "server.js"]     # process.env.NODE_ENV === 'production'
```

#### ARG — 빌드 시에만

`ARG`로 설정한 변수는 **빌드 시점에서만** 사용 가능하고, 최종 이미지에는 포함되지 않는다.

```dockerfile
# 기본값 설정
ARG NODE_VERSION=20

# FROM에서 ARG 사용 (FROM 앞에 선언해야 함)
ARG NODE_VERSION=20
FROM node:${NODE_VERSION}-alpine

# 빌드 시 전달
# docker build --build-arg NODE_VERSION=22 .
```

**FROM 이전의 ARG는 특별한 규칙을 따른다:**

```dockerfile
# FROM 앞의 ARG는 FROM에서만 사용 가능
ARG NODE_VERSION=20
FROM node:${NODE_VERSION}-alpine

# FROM 이후에 다시 선언해야 빌드 과정에서 사용 가능
ARG NODE_VERSION
RUN echo $NODE_VERSION
```

#### 보안 주의사항 — ARG도 이미지 히스토리에 남는다

```dockerfile
# 매우 위험: 비밀 정보를 ARG로 전달하면 이미지 히스토리에 기록된다
ARG NPM_TOKEN
RUN echo "//registry.npmjs.org/:_authToken=${NPM_TOKEN}" > .npmrc && \
    npm ci && \
    rm .npmrc  # 파일을 삭제해도 이전 레이어에 .npmrc가 남아있다!
```

```bash
# 누구나 이미지 히스토리에서 비밀 정보를 볼 수 있다
docker history my-app
# → RUN |1 NPM_TOKEN=secret123 echo "//registry.npmjs.org/..."
```

비밀 정보는 반드시 BuildKit의 `--mount=type=secret`을 사용해야 한다(섹션 6에서 다룬다).

### 2.7 EXPOSE — 포트 문서화

`EXPOSE`는 컨테이너가 사용하는 포트를 **문서화**하는 역할만 한다. 실제 포트 매핑은 `docker run`의 `-p` 플래그로 수행해야 한다.

```dockerfile
EXPOSE 3000
```

```bash
# EXPOSE만으로는 호스트에서 접근 불가
docker run my-next-app
# → localhost:3000으로 접근 불가

# -p 플래그로 실제 포트 매핑 필요
docker run -p 3000:3000 my-next-app
# → 호스트 3000 → 컨테이너 3000 매핑

# 호스트 포트를 다르게 매핑할 수도 있다
docker run -p 8080:3000 my-next-app
# → 호스트 8080 → 컨테이너 3000 매핑
```

`EXPOSE`를 작성하지 않아도 `-p`를 사용하면 포트 매핑은 동작한다. 그러나 **어떤 포트를 사용하는지 명시적으로 문서화**하는 좋은 습관이다. `docker inspect`나 Docker Compose에서 이 정보를 활용할 수 있다.

### 2.8 VOLUME — 볼륨 마운트 포인트 선언

```dockerfile
VOLUME ["/data"]
```

`VOLUME` 인스트럭션은 지정된 경로에 **익명 볼륨(anonymous volume)** 을 생성한다. 그러나 Dockerfile에 `VOLUME`을 넣는 것은 권장되지 않는다:

- 볼륨 이름을 지정할 수 없어 관리가 어렵다
- `docker run -v` 또는 Docker Compose의 `volumes` 설정이 더 명확하고 유연하다
- Dockerfile에 `VOLUME`이 있으면 해당 경로에 대한 이후 `RUN` 변경이 **무시**될 수 있어 혼란을 일으킨다

```dockerfile
# 나쁜 예: Dockerfile에 VOLUME 선언
VOLUME ["/app/data"]
RUN echo "hello" > /app/data/test.txt  # 이 변경이 무시될 수 있다!

# 좋은 예: docker run 또는 Compose에서 볼륨 매핑
# docker run -v my-data:/app/data my-app
```

> **실무 팁**: Dockerfile에 `VOLUME` 인스트럭션을 넣지 마라. 볼륨 관리는 `docker run -v` 또는 Docker Compose에서 처리하는 것이 명확하고 예측 가능하다.

### 2.9 USER — 실행 사용자 변경

기본적으로 Docker 컨테이너 내부의 프로세스는 **root 권한**으로 실행된다. 보안상 프로덕션 이미지에서는 비루트 사용자로 전환해야 한다.

```dockerfile
# 사용자 그룹 및 사용자 생성
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# 이후 모든 명령어가 nextjs 사용자로 실행됨
USER nextjs

# CMD도 nextjs 사용자로 실행됨
CMD ["node", "server.js"]
```

`node:20-alpine` 이미지에는 이미 `node`라는 비루트 사용자가 포함되어 있으므로 이를 활용할 수도 있다:

```dockerfile
FROM node:20-alpine
WORKDIR /app
# ... 파일 복사 및 빌드 ...
USER node
CMD ["node", "server.js"]
```

단, `USER` 전환 전에 파일 복사와 `npm ci`를 완료해야 한다. 비루트 사용자는 `/app` 디렉토리에 대한 쓰기 권한이 없을 수 있기 때문이다. 멀티스테이지 빌드에서는 `COPY --chown`을 사용하여 소유권을 지정한다.

### 2.10 HEALTHCHECK — 컨테이너 헬스 체크

Docker가 컨테이너의 **건강 상태**를 주기적으로 확인하도록 설정한다. 단순히 프로세스가 실행 중인지가 아니라, 애플리케이션이 정상적으로 요청을 처리할 수 있는지 확인한다.

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:3000/api/health || exit 1
```

각 옵션:

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--interval` | 헬스 체크 실행 간격 | 30s |
| `--timeout` | 응답 대기 시간 (초과 시 실패) | 30s |
| `--start-period` | 컨테이너 시작 후 헬스 체크 유예 기간 | 0s |
| `--retries` | 연속 실패 횟수 (초과 시 unhealthy) | 3 |

Alpine 이미지에는 `curl`이 기본 포함되어 있지 않으므로 `wget`을 사용하거나 별도로 설치해야 한다:

```dockerfile
# Alpine에서는 wget 사용 (기본 포함)
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/api/health || exit 1
```

```bash
# 헬스 상태 확인
docker ps
# CONTAINER ID   IMAGE        STATUS
# a1b2c3d4e5f6   my-app       Up 30s (healthy)
```

### 2.11 LABEL — 메타데이터 추가

이미지에 메타데이터를 키-값 쌍으로 추가한다. 이미지 관리, 필터링, 자동화에 유용하다.

```dockerfile
LABEL maintainer="team@example.com"
LABEL org.opencontainers.image.source="https://github.com/org/repo"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.description="Next.js production app"
```

```bash
# 레이블 확인
docker inspect --format='{{json .Config.Labels}}' my-app
```

### 2.12 SHELL — 기본 셸 변경

`RUN`, `CMD`, `ENTRYPOINT`의 shell form에서 사용되는 기본 셸을 변경한다. 기본값은 Linux에서 `["/bin/sh", "-c"]`다.

```dockerfile
# bash를 기본 셸로 변경
SHELL ["/bin/bash", "-c"]

# 이후 shell form의 RUN은 bash로 실행됨
RUN source ~/.bashrc && echo $MY_VAR
```

Alpine 이미지에는 `bash`가 기본 포함되어 있지 않으므로, 필요하다면 먼저 설치해야 한다. 대부분의 Node.js Dockerfile에서는 `SHELL`을 변경할 필요가 없다.

---

## 3. 빌드 컨텍스트와 .dockerignore

### 3.1 빌드 컨텍스트가 왜 중요한가

`docker build`를 실행하면 지정된 디렉토리의 **모든 파일**이 Docker Daemon에 전송된다. Node.js 프로젝트에서 `node_modules`(수백 MB), `.git`(수십~수백 MB), `.next`(수십 MB)가 모두 전송되면 빌드 시작 전에 이미 수십 초를 낭비하게 된다.

```bash
# 빌드 컨텍스트 크기 확인
du -sh --exclude=.git .
# 또는 macOS에서:
du -sh -I .git .

# 상세 크기 확인
du -sh node_modules .next .git
# 350M   node_modules
# 45M    .next
# 120M   .git
```

### 3.2 .dockerignore 파일 작성법

`.dockerignore`는 `.gitignore`와 동일한 문법을 사용하며, 프로젝트 루트에 위치한다:

```
# 의존성 — 컨테이너 안에서 새로 설치
node_modules

# 빌드 산출물 — 컨테이너 안에서 새로 빌드
.next
out
dist
build

# 버전 관리
.git
.gitignore

# 개발 도구
.vscode
.idea
*.swp
*.swo

# 환경 설정 — 런타임에 주입해야 함
.env
.env.local
.env.*.local

# 문서 및 설정
*.md
LICENSE
docker-compose*.yml
Dockerfile*

# 테스트 및 품질 도구
coverage
.nyc_output
jest.config.*
cypress
e2e
__tests__

# 캐시
.turbo
.cache
.eslintcache

# 기타
.DS_Store
Thumbs.db
```

### 3.3 .dockerignore의 효과 확인

```bash
# .dockerignore 적용 전
$ docker build -t test .
Sending build context to Docker daemon  534.2MB
# → 534MB 전송, 빌드 시작까지 8초

# .dockerignore 적용 후
$ docker build -t test .
Sending build context to Docker daemon  2.4MB
# → 2.4MB 전송, 빌드 즉시 시작
```

> **핵심 통찰**: `.dockerignore`는 단순한 최적화가 아니다. 보안적으로도 중요하다. `.env` 파일에 담긴 비밀 정보, `.git`에 담긴 전체 커밋 히스토리가 이미지 빌드 과정에 노출되는 것을 방지한다.

---

## 4. 레이어 캐시 전략

### 4.1 Docker 빌드의 레이어 캐싱 메커니즘

Docker는 각 인스트럭션의 결과를 레이어로 저장하고, 다음 빌드에서 **동일한 인스트럭션 + 동일한 입력**이면 캐시된 레이어를 재사용한다. 이를 **레이어 캐싱**이라 한다.

캐시 히트 여부를 판단하는 기준:

| 인스트럭션 | 캐시 히트 조건 |
|------------|---------------|
| `FROM` | 동일한 이미지:태그 |
| `RUN` | 동일한 명령어 문자열 |
| `COPY` / `ADD` | 복사할 파일의 **체크섬**이 동일 |
| `ENV`, `WORKDIR` 등 | 동일한 값 |

### 4.2 캐시 무효화(Cache Invalidation) 규칙

가장 중요한 규칙: **어떤 레이어의 캐시가 무효화되면, 그 이후의 모든 레이어도 재빌드된다.**

```
Layer 1: FROM node:20-alpine              ✅ 캐시 히트
Layer 2: WORKDIR /app                     ✅ 캐시 히트
Layer 3: COPY package.json ./             ✅ 캐시 히트 (파일 변경 없음)
Layer 4: RUN npm ci                       ✅ 캐시 히트 (이전 레이어 캐시 유효)
Layer 5: COPY . .                         ❌ 캐시 미스 (소스 코드 변경됨)
Layer 6: RUN npm run build                ❌ 재빌드 (Layer 5가 변경됨)
Layer 7: CMD ["npm", "start"]             ❌ 재빌드 (Layer 6이 변경됨)
```

Layer 5에서 소스 코드가 변경되어 캐시가 깨졌지만, Layer 3-4(의존성 설치)는 캐시를 활용하여 `npm ci`를 건너뛸 수 있다.

### 4.3 핵심 원칙: 자주 변경되는 파일은 뒤에

이 원칙은 Dockerfile 최적화의 **가장 기본적이고 가장 중요한 전략**이다.

```dockerfile
# ❌ 나쁜 예: 소스 코드를 먼저 복사
FROM node:20-alpine
WORKDIR /app
COPY . .                    # 소스 코드 한 줄만 바꿔도...
RUN npm ci                  # ... npm ci가 매번 재실행! (수 분 소요)
RUN npm run build
CMD ["npm", "start"]
```

```dockerfile
# ✅ 좋은 예: 의존성 파일을 먼저 복사
FROM node:20-alpine
WORKDIR /app
COPY package.json package-lock.json ./    # 의존성이 변경될 때만 캐시 무효화
RUN npm ci                                # 의존성 변경 없으면 캐시 히트 (0초)
COPY . .                                  # 소스 코드 복사 (여기서 캐시 깨짐)
RUN npm run build                         # 빌드만 재실행
CMD ["npm", "start"]
```

**실제 빌드 시간 차이:**

| 변경 내용 | 나쁜 예 | 좋은 예 |
|-----------|---------|---------|
| 소스 코드 1줄 변경 | npm ci(120초) + build(30초) = **150초** | build(30초) = **30초** |
| package.json 변경 | npm ci(120초) + build(30초) = **150초** | npm ci(120초) + build(30초) = **150초** |
| 변경 없음 (재빌드) | **0초** (전체 캐시) | **0초** (전체 캐시) |

소스 코드 변경은 하루에도 수십 번 발생하지만, `package.json` 변경은 일주일에 한두 번이다. 좋은 예에서는 **대부분의 빌드에서 `npm ci`를 건너뛴다**.

### 4.4 패키지 매니저별 캐시 전략 맛보기

각 패키지 매니저마다 복사해야 할 lock 파일이 다르다:

```dockerfile
# npm
COPY package.json package-lock.json ./
RUN npm ci

# pnpm
COPY package.json pnpm-lock.yaml ./
RUN corepack enable pnpm && pnpm install --frozen-lockfile

# yarn (Classic)
COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile

# yarn (Berry / PnP)
COPY package.json yarn.lock .yarnrc.yml ./
COPY .yarn/releases ./.yarn/releases
COPY .yarn/plugins ./.yarn/plugins
RUN yarn install --immutable

# bun
COPY package.json bun.lockb ./
RUN bun install --frozen-lockfile
```

> **실무 팁**: 패키지 매니저별 상세 캐시 전략(BuildKit cache mount 활용, turbo prune 등)은 Ch 12 (Node.js Docker Best Practices)에서 심화하여 다룬다.

---

## 5. 멀티스테이지 빌드

### 5.1 왜 멀티스테이지 빌드가 필요한가

싱글 스테이지 빌드에서는 빌드에 필요한 모든 도구와 의존성이 최종 이미지에 포함된다:

```dockerfile
# 싱글 스테이지: 최종 이미지에 불필요한 것들이 모두 포함됨
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci                  # devDependencies 포함 (typescript, eslint, etc.)
COPY . .
RUN npm run build           # TypeScript 컴파일러, 빌드 도구 등이 이미지에 남음
# → 최종 이미지 크기: ~800MB ~ 1GB
CMD ["npm", "start"]
```

이 이미지에는 프로덕션에 전혀 필요 없는 것들이 포함된다:
- `devDependencies` (TypeScript, ESLint, Prettier, Jest 등)
- TypeScript 소스 파일 (`.ts`, `.tsx`)
- 테스트 파일
- 빌드 설정 파일 (`tsconfig.json`, `.eslintrc` 등)

멀티스테이지 빌드(*Multi-stage Build - 하나의 Dockerfile에 여러 `FROM`을 사용하여 빌드 단계를 분리하고, 최종 이미지에는 필요한 산출물만 포함시키는 기법*)는 이 문제를 해결한다.

### 5.2 기본 패턴: builder + runner

```dockerfile
# ---- Stage 1: 빌드 ----
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# ---- Stage 2: 프로덕션 ----
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

# 프로덕션 의존성만 설치
COPY package.json package-lock.json ./
RUN npm ci --omit=dev

# 빌드 산출물만 복사
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

CMD ["npm", "start"]
```

`COPY --from=builder`가 핵심이다. `builder` 스테이지에서 빌드한 결과물만 `runner` 스테이지로 복사하고, 빌드 도구와 소스 코드는 버린다.

### 5.3 Next.js standalone 모드를 활용한 완전한 멀티스테이지 Dockerfile

Next.js의 `output: 'standalone'` 설정을 활용하면 이미지 크기를 극적으로 줄일 수 있다. 이 모드는 Next.js가 필요한 `node_modules`만 추출하여 독립 실행 가능한 서버를 생성한다.

먼저 `next.config.js`에 설정을 추가한다:

```typescript
// next.config.ts
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  output: 'standalone',
};

export default nextConfig;
```

그리고 3단계 멀티스테이지 Dockerfile을 작성한다:

```dockerfile
# ============================================
# Stage 1: 의존성 설치 (deps)
# ============================================
FROM node:20-alpine AS deps
WORKDIR /app

# pnpm 사용 예시 (npm이라면 package-lock.json 사용)
COPY package.json pnpm-lock.yaml ./
RUN corepack enable pnpm && pnpm install --frozen-lockfile

# ============================================
# Stage 2: 빌드 (builder)
# ============================================
FROM node:20-alpine AS builder
WORKDIR /app

# deps 스테이지에서 node_modules만 복사
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Next.js는 빌드 시 NEXT_PUBLIC_* 환경변수를 인라인한다
# 빌드 시 필요한 환경변수가 있다면 여기서 ARG로 받는다
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

RUN corepack enable pnpm && pnpm run build

# ============================================
# Stage 3: 프로덕션 실행 (runner)
# ============================================
FROM node:20-alpine AS runner
WORKDIR /app

# 프로덕션 환경 설정
ENV NODE_ENV=production

# 보안: 비루트 사용자 생성
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# 정적 파일 복사 (public 디렉토리)
COPY --from=builder /app/public ./public

# standalone 산출물 복사 (소유권을 nextjs 사용자로 설정)
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# 비루트 사용자로 전환
USER nextjs

# 포트 문서화
EXPOSE 3000
ENV PORT=3000
# hostname을 0.0.0.0으로 설정해야 Docker 외부에서 접근 가능
ENV HOSTNAME="0.0.0.0"

# standalone 모드의 서버 실행
CMD ["node", "server.js"]
```

### 5.4 각 스테이지별 역할 상세 해설

**Stage 1 — deps (의존성 설치):**
- `package.json`과 lock 파일만 복사하여 의존성을 설치한다
- 소스 코드와 분리하여 **의존성 레이어 캐싱**을 극대화한다
- `package.json`이 변경되지 않으면 이 스테이지 전체가 캐시된다

**Stage 2 — builder (빌드):**
- `deps` 스테이지의 `node_modules`를 복사받아 빌드를 수행한다
- `COPY --from=deps`로 다른 스테이지의 파일을 참조하는 것이 멀티스테이지의 핵심 메커니즘이다
- `NEXT_PUBLIC_*` 환경변수는 빌드 시 클라이언트 번들에 인라인되므로 `ARG`로 받아 `ENV`로 설정한다
- 빌드 결과물(`.next/standalone`, `.next/static`)만이 다음 스테이지에서 사용된다

**Stage 3 — runner (프로덕션):**
- **새 베이스 이미지**에서 시작하므로 빌드 도구, 소스 코드, devDependencies가 모두 제거된다
- `standalone` 산출물에는 Next.js 서버 + 필요한 `node_modules`만 포함되어 있어 극도로 가볍다
- `addgroup`/`adduser`로 비루트 사용자를 생성하고 `USER`로 전환한다
- `HOSTNAME="0.0.0.0"`은 Next.js standalone 서버가 모든 네트워크 인터페이스에서 수신하도록 설정한다. 이 없으면 `localhost`만 리스닝하여 Docker 외부에서 접근할 수 없다

### 5.5 이미지 크기 비교

```bash
# 빌드
docker build -t next-single --target builder .   # 싱글 스테이지 시뮬레이션
docker build -t next-multi .                      # 멀티스테이지 (runner)

# 크기 확인
docker images | grep next
```

| 방식 | 이미지 크기 | 포함 내용 |
|------|------------|-----------|
| 싱글 스테이지 | ~800MB ~ 1.2GB | Node.js + 전체 node_modules + 소스 + 빌드 산출물 |
| 멀티스테이지 (기본) | ~300MB ~ 400MB | Node.js + 프로덕션 node_modules + 빌드 산출물 |
| 멀티스테이지 (standalone) | ~120MB ~ 180MB | Node.js + 최소 node_modules + standalone 서버 |

standalone 모드를 활용한 멀티스테이지 빌드는 싱글 스테이지 대비 **이미지 크기를 약 80~85% 줄인다.**

### 5.6 특정 스테이지만 빌드하기

디버깅이나 CI에서 특정 스테이지까지만 빌드해야 할 때 `--target` 플래그를 사용한다:

```bash
# deps 스테이지까지만 빌드
docker build --target deps -t my-app:deps .

# builder 스테이지까지 빌드 (빌드 결과물 확인용)
docker build --target builder -t my-app:builder .

# 전체 빌드 (runner — 기본)
docker build -t my-app:latest .
```

---

## 6. BuildKit

### 6.1 BuildKit이란

BuildKit(*Docker의 차세대 빌드 엔진으로, 기존 빌드 엔진 대비 성능, 캐시, 보안을 대폭 개선한다*)은 Docker 18.09에서 도입되어, Docker Desktop 23.0부터는 **기본 빌드 엔진**으로 활성화되어 있다.

```bash
# BuildKit 활성화 확인 — Docker Desktop을 사용 중이라면 기본 활성화
docker buildx version

# 명시적으로 BuildKit 활성화 (Linux 서버 등)
DOCKER_BUILDKIT=1 docker build -t my-app .

# 또는 Docker 설정에서 영구적으로 활성화
# /etc/docker/daemon.json
# { "features": { "buildkit": true } }
```

### 6.2 BuildKit의 핵심 장점

#### 병렬 빌드

기존 빌드 엔진은 모든 인스트럭션을 순차적으로 실행한다. BuildKit은 의존 관계가 없는 스테이지를 **동시에 빌드**한다:

```dockerfile
# deps와 assets는 서로 독립적 → BuildKit이 병렬로 빌드
FROM node:20-alpine AS deps
COPY package.json pnpm-lock.yaml ./
RUN corepack enable pnpm && pnpm install --frozen-lockfile

FROM node:20-alpine AS assets
COPY public/ ./public/
RUN echo "Processing static assets..."

FROM node:20-alpine AS builder
COPY --from=deps /app/node_modules ./node_modules
COPY --from=assets /app/public ./public
COPY . .
RUN npm run build
```

`deps`와 `assets` 스테이지가 동시에 실행되어 전체 빌드 시간이 단축된다.

#### 향상된 캐시

BuildKit은 기존 레이어 캐시 외에 다양한 캐시 백엔드를 지원한다:

```bash
# 인라인 캐시 — 이미지 자체에 캐시 메타데이터 포함
docker build --build-arg BUILDKIT_INLINE_CACHE=1 -t my-app .

# 레지스트리 캐시 — 원격 레지스트리에서 캐시를 가져옴
docker buildx build \
  --cache-from type=registry,ref=ghcr.io/org/my-app:cache \
  --cache-to type=registry,ref=ghcr.io/org/my-app:cache \
  -t my-app .

# GitHub Actions 캐시 (CI/CD에서 유용)
docker buildx build \
  --cache-from type=gha \
  --cache-to type=gha,mode=max \
  -t my-app .
```

### 6.3 마운트 캐시 (`--mount=type=cache`)

BuildKit의 가장 강력한 기능 중 하나다. 패키지 매니저의 캐시 디렉토리를 **빌드 간에 유지**하여 의존성 설치 속도를 극적으로 개선한다.

```dockerfile
# syntax=docker/dockerfile:1

# npm 캐시 마운트
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci --prefer-offline

# pnpm 캐시 마운트
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN --mount=type=cache,target=/root/.local/share/pnpm/store \
    corepack enable pnpm && pnpm install --frozen-lockfile
```

`--mount=type=cache`의 동작 원리:

1. 첫 빌드: `npm ci`가 패키지를 다운로드하고 `/root/.npm` 캐시에 저장
2. 다음 빌드: 캐시가 마운트되어 이미 다운로드된 패키지를 재사용 (`--prefer-offline`)
3. `package.json`이 변경되어 레이어 캐시가 깨져도, **다운로드 캐시는 유지**됨

일반 레이어 캐시만 사용하면 `package.json`이 변경될 때마다 모든 패키지를 처음부터 다운로드해야 한다. 마운트 캐시를 사용하면 변경된 패키지만 새로 다운로드한다.

> **핵심 통찰**: `--mount=type=cache`는 레이어 캐시와 **보완적으로** 작동한다. 레이어 캐시가 히트하면 RUN 자체를 건너뛰고, 레이어 캐시가 미스해도 마운트 캐시 덕분에 다운로드를 최소화한다.

### 6.4 시크릿 마운트 (`--mount=type=secret`)

비밀 정보(private npm 레지스트리 토큰 등)를 **이미지 히스토리에 남기지 않고** 빌드 시에만 사용할 수 있다.

```dockerfile
# syntax=docker/dockerfile:1

FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json pnpm-lock.yaml ./

# .npmrc 파일을 시크릿으로 마운트
# → 빌드 시에만 /root/.npmrc로 마운트되고, 이미지에는 포함되지 않음
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc \
    corepack enable pnpm && pnpm install --frozen-lockfile
```

빌드 시 시크릿 파일을 전달한다:

```bash
docker build --secret id=npmrc,src=$HOME/.npmrc -t my-app .
```

`ARG`로 토큰을 전달하는 방법과의 차이:

```bash
# ARG 방식 — docker history에 토큰이 노출됨 (위험!)
docker build --build-arg NPM_TOKEN=secret123 .
docker history my-app
# → RUN |1 NPM_TOKEN=secret123 ...

# Secret 마운트 방식 — 이미지에 어떤 흔적도 남지 않음 (안전)
docker build --secret id=npmrc,src=.npmrc .
docker history my-app
# → RUN ... (시크릿 정보 없음)
```

### 6.5 Dockerfile 첫 줄의 syntax 지시어

BuildKit의 고급 기능(`--mount` 등)을 사용하려면 Dockerfile 첫 줄에 syntax 지시어를 추가하는 것이 권장된다:

```dockerfile
# syntax=docker/dockerfile:1
FROM node:20-alpine
# ...
```

이 지시어는 BuildKit에게 Dockerfile 파서 버전을 알려준다. `docker/dockerfile:1`은 1.x의 최신 안정 버전을 사용한다는 의미다. 이 없이도 최신 Docker에서는 대부분 동작하지만, 명시적으로 작성하면 호환성을 보장할 수 있다.

---

## 7. 실전 Dockerfile 작성 체크리스트

프로덕션 Dockerfile을 작성할 때 다음 항목을 반드시 확인하라:

- [ ] **구체적인 버전 태그 사용**: `node:20.11-alpine` (not `node:latest`, not `node:20`)
- [ ] **.dockerignore 작성**: `node_modules`, `.git`, `.next`, `.env*` 등 제외
- [ ] **의존성 파일 먼저 복사 → 설치 → 소스 복사**: 레이어 캐시 극대화
- [ ] **`npm ci` (또는 `--frozen-lockfile`) 사용**: 재현 가능한 빌드
- [ ] **멀티스테이지 빌드 사용**: 빌드 도구와 devDependencies를 최종 이미지에서 제거
- [ ] **비루트 사용자로 실행**: `USER nextjs` 또는 `USER node`
- [ ] **exec form으로 CMD 작성**: `CMD ["node", "server.js"]` (PID 1 문제 방지)
- [ ] **HEALTHCHECK 설정**: 컨테이너 상태 모니터링
- [ ] **`ENV NODE_ENV=production` 설정**: npm이 devDependencies를 설치하지 않도록
- [ ] **불필요한 파일이 최종 이미지에 포함되지 않는지 확인**: `docker exec`으로 진입하여 확인
- [ ] **HOSTNAME="0.0.0.0" 설정**: Next.js standalone 서버가 외부에서 접근 가능하도록
- [ ] **비밀 정보가 이미지에 포함되지 않는지 확인**: `docker history`로 확인

확인 방법:

```bash
# 최종 이미지 크기 확인
docker images my-app

# 이미지 레이어 및 히스토리 확인 (비밀 정보 노출 여부)
docker history my-app

# 이미지 내부 파일 확인 (불필요한 파일 포함 여부)
docker run --rm -it my-app sh
ls -la
ls node_modules | wc -l
whoami    # root가 아닌지 확인

# 헬스체크 확인
docker inspect --format='{{json .Config.Healthcheck}}' my-app
```

---

## 자주 하는 실수

| 실수 | 문제점 | 올바른 방법 |
|------|--------|-------------|
| `COPY . .`을 `RUN npm ci` 앞에 배치 | 소스 코드 한 줄 변경 시 의존성 전체 재설치 (수 분 낭비) | `COPY package*.json ./` → `RUN npm ci` → `COPY . .` |
| `npm install` 대신 `npm ci` 미사용 | lock 파일 무시, 비결정적 빌드. 로컬과 CI에서 서로 다른 버전 설치 가능 | 항상 `npm ci` (또는 `pnpm install --frozen-lockfile`) |
| `CMD`를 shell form으로 작성 | PID 1이 `/bin/sh`가 되어 SIGTERM이 Node.js에 전달되지 않음. graceful shutdown 불가 | exec form 사용: `CMD ["node", "server.js"]` |
| `ARG`로 비밀 정보 전달 | `docker history`로 누구나 비밀 정보를 확인 가능 | BuildKit의 `--mount=type=secret` 사용 |
| `.dockerignore` 없이 빌드 | `node_modules`, `.git` 등이 빌드 컨텍스트에 포함되어 빌드 시간 증가 + 보안 위험 | `.dockerignore`로 불필요한 파일 제외 |
| `latest` 태그 사용 | 빌드 재현성 없음. 어제와 오늘의 `latest`가 다른 이미지일 수 있다 | 구체적 버전+변형 태그: `node:20.11-alpine` |
| `apt-get update`와 `apt-get install`을 별도 `RUN`으로 분리 | 캐시된 `update` 레이어로 인해 오래된 패키지 인덱스 사용, 구버전 패키지 설치 | `&&`로 체이닝: `RUN apt-get update && apt-get install -y curl` |
| `devDependencies`를 프로덕션 이미지에 포함 | 이미지 크기 2~3배 증가, 불필요한 패키지로 보안 취약점 표면 확대 | 멀티스테이지 빌드 또는 `npm ci --omit=dev` |

---

## 명령어 레퍼런스

| 명령어 | 설명 | 예시 |
|--------|------|------|
| `docker build` | Dockerfile로 이미지 빌드 | `docker build -t my-app:1.0 .` |
| `docker build -f` | Dockerfile 경로 지정 | `docker build -f Dockerfile.prod -t my-app .` |
| `docker build --target` | 특정 스테이지까지만 빌드 | `docker build --target builder -t my-app:builder .` |
| `docker build --build-arg` | 빌드 인자 전달 (ARG) | `docker build --build-arg NODE_ENV=production .` |
| `docker build --secret` | 시크릿 파일 전달 (BuildKit) | `docker build --secret id=npmrc,src=.npmrc .` |
| `docker build --no-cache` | 캐시 없이 전체 재빌드 | `docker build --no-cache -t my-app .` |
| `docker history` | 이미지 레이어 히스토리 확인 | `docker history my-app` |
| `docker image inspect` | 이미지 상세 정보 (JSON) | `docker image inspect my-app` |
| `docker buildx build` | BuildKit 확장 빌드 (캐시 옵션 등) | `docker buildx build --cache-from type=gha .` |
| `docker buildx ls` | 사용 가능한 빌더 목록 | `docker buildx ls` |

---

## 요약

- **Dockerfile은 이미지의 청사진이다**: 텍스트 기반 명세서로, 재현 가능한 빌드를 보장한다. 빌드 컨텍스트의 파일만 접근 가능하며, `.dockerignore`로 불필요한 파일을 제외해야 한다
- **인스트럭션의 역할**: `FROM`(베이스 이미지), `WORKDIR`(작업 디렉토리), `COPY`(파일 복사), `RUN`(명령 실행), `CMD`/`ENTRYPOINT`(시작 명령), `ENV`/`ARG`(변수), `USER`(보안), `HEALTHCHECK`(상태 확인)
- **레이어 캐시가 핵심이다**: 자주 변경되는 파일을 뒤에 배치하여 캐시 적중률을 극대화한다. 의존성 파일 복사 → 설치 → 소스 복사 순서가 기본 패턴이다
- **멀티스테이지 빌드는 필수다**: 빌드 도구와 devDependencies를 최종 이미지에서 제거하여 크기를 80% 이상 줄인다. Next.js standalone 모드와 결합하면 ~150MB 이하의 이미지를 만들 수 있다
- **CMD는 반드시 exec form으로**: Shell form은 PID 1 문제를 일으켜 SIGTERM이 애플리케이션에 전달되지 않는다
- **BuildKit은 기본 빌드 엔진이다**: 병렬 빌드, 마운트 캐시(`--mount=type=cache`), 시크릿 마운트(`--mount=type=secret`), 향상된 캐시 백엔드를 제공한다
- **비밀 정보는 ARG가 아닌 `--mount=type=secret`으로**: ARG 값은 `docker history`에 노출된다

---

## 다른 챕터와의 관계

- **Ch 2 (이미지)**: 이미지의 레이어 구조가 Dockerfile의 각 인스트럭션과 직접 대응된다. `FROM`, `RUN`, `COPY`는 각각 새 레이어를 생성하고, `ENV`, `WORKDIR`, `CMD` 등은 메타데이터만 변경한다
- **Ch 3 (컨테이너)**: PID 1 문제가 `CMD`/`ENTRYPOINT`의 exec form 선택에 직접적인 영향을 준다. 컨테이너 생명주기와 시그널 처리를 이해해야 올바른 Dockerfile을 작성할 수 있다
- **Ch 5 (볼륨)**: `VOLUME` 인스트럭션의 한계와 대안을 살펴본다. 데이터 영속성이 필요한 경우 `docker run -v` 또는 Compose의 `volumes` 설정이 Dockerfile의 `VOLUME`보다 훨씬 적합하다
- **Ch 9 (이미지 최적화)**: 멀티스테이지 빌드를 더 심화하여 다룬다. distroless 이미지, `docker scout`/`trivy`를 활용한 취약점 분석, 레이어 크기 분석 도구 등을 다룬다
- **Ch 10 (보안)**: `USER`, `--mount=type=secret`, 읽기전용 파일시스템을 보안 관점에서 체계적으로 다룬다. Dockerfile에서의 보안 결정이 컨테이너 전체 보안 수준에 미치는 영향을 분석한다
- **Ch 12 (Node.js Best Practices)**: pnpm/yarn/bun별 상세 캐시 전략, BuildKit 마운트 캐시의 패키지 매니저별 최적 경로, PID 1 문제의 tini를 활용한 해결법, `npm ci` vs `npm install`의 차이를 심화한다