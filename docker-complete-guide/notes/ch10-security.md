# Chapter 10: 컨테이너 보안 (Security)

## 핵심 질문

컨테이너 환경에서 보안 위협은 어디에 존재하며, 이미지 빌드부터 런타임까지 어떤 보안 조치를 적용해야 하는가? NEXT_PUBLIC_* 환경변수의 보안 함의는 무엇인가?

---

## 1. 컨테이너 보안 위협 모델

컨테이너 보안을 이해하려면 먼저 **어디에서 위협이 발생하는지** 전체 그림을 파악해야 한다. 위협은 이미지, 빌드, 런타임, 호스트의 네 가지 레이어에 걸쳐 존재한다.

### 이미지 보안

| 위협 | 설명 | 대응 |
|------|------|------|
| 취약한 베이스 이미지 | 오래된 Debian/Ubuntu 이미지에 알려진 CVE 포함 | Alpine 또는 Distroless 사용 (Ch 9) |
| 불필요한 패키지 | `curl`, `wget`, `netcat` 등이 공격 도구로 활용 가능 | 프로덕션 이미지에서 불필요 패키지 제거 |
| 비밀 정보 포함 | `.env` 파일, SSH 키, API 토큰이 레이어에 남음 | `.dockerignore`로 제외, BuildKit secrets 사용 |
| 검증되지 않은 이미지 | Docker Hub에서 아무 이미지나 `pull` | 공식 이미지 또는 서명된 이미지만 사용 |

### 빌드 보안

`ARG`로 전달한 값은 이미지 히스토리에 남는다. `docker history` 명령어로 누구나 확인할 수 있다.

```dockerfile
# 나쁜 예: ARG로 비밀 전달 — 이미지 히스토리에 노출
ARG DATABASE_URL
ENV DATABASE_URL=$DATABASE_URL

# 좋은 예: BuildKit --mount=type=secret 사용
RUN --mount=type=secret,id=db_url \
    DATABASE_URL=$(cat /run/secrets/db_url) npm run build
```

빌드 컨텍스트(*Build Context - `docker build` 시 Docker 데몬에 전송되는 파일 집합*)에 민감한 파일이 포함되면, 의도치 않게 이미지에 `COPY`될 수 있다. `.dockerignore`는 필수다.

```bash
# .dockerignore
.env
.env.*
*.pem
*.key
.git
node_modules
```

### 런타임 보안

- **root 실행**: 컨테이너가 root로 실행되면, 컨테이너 탈출 시 호스트 root 권한을 얻을 수 있다
- **과도한 권한**: `--privileged` 플래그는 모든 Linux 커널 기능을 부여한다
- **네트워크 노출**: 불필요한 포트를 외부에 바인딩하면 공격 표면이 넓어진다

### 호스트 보안

- **docker.sock 노출**: Docker 소켓에 접근 가능하면 호스트를 완전히 제어할 수 있다
- **커널 취약점**: 컨테이너는 호스트 커널을 공유하므로, 커널 취약점은 곧 컨테이너 탈출로 이어진다
- **컨테이너 탈출**: 잘못된 설정이나 커널 버그를 통해 컨테이너 격리를 벗어나는 공격

> **핵심 통찰**: 컨테이너는 VM이 아니다. 컨테이너는 리눅스 namespace와 cgroup으로 **프로세스를 격리**한 것일 뿐, 호스트 커널을 공유한다. "컨테이너에 넣었으니 안전하다"는 착각은 가장 위험한 보안 실수다.

---

## 2. 비루트(Non-root) 실행

### 왜 root가 위험한가

Docker 컨테이너는 기본적으로 **root(UID 0)**로 실행된다. 컨테이너 내부의 root는 호스트의 root와 동일한 UID를 가지므로, 컨테이너 탈출에 성공하면 호스트에서도 root 권한을 얻는다.

```bash
# 기본 실행: root
docker run node:20-alpine whoami
# 출력: root

# UID 확인
docker run node:20-alpine id
# 출력: uid=0(root) gid=0(root)
```

### USER 인스트럭션으로 비루트 사용자 전환

`USER` 인스트럭션(*USER Instruction - Dockerfile에서 이후 명령어와 컨테이너 실행 시 사용할 사용자를 지정하는 지시어*)을 사용하여 비루트 사용자로 전환한다.

```dockerfile
# 사용자 생성 후 전환
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

USER nextjs
```

### Node.js 이미지의 내장 node 사용자

공식 Node.js 이미지에는 `node`라는 사용자가 이미 포함되어 있다(UID 1000). 별도 사용자를 만들지 않아도 된다.

```dockerfile
FROM node:20-alpine

WORKDIR /app

# 의존성 설치는 root로 (node_modules 쓰기 권한)
COPY package*.json ./
RUN npm ci --omit=dev

# 소스 복사
COPY --chown=node:node . .

# node 사용자로 전환
USER node

EXPOSE 3000
CMD ["node", "server.js"]
```

### 파일 소유권과 COPY --chown

`USER`를 먼저 전환하면 이후 `COPY`된 파일은 해당 사용자 소유가 되지만, `npm ci`처럼 root 권한이 필요한 작업이 실패할 수 있다. 순서가 중요하다.

```dockerfile
# 패턴 1: COPY --chown (권장)
COPY --chown=node:node . .
USER node

# 패턴 2: USER를 나중에 전환
COPY . .
RUN chown -R node:node /app
USER node
```

`--chown`은 COPY 시점에 소유권을 설정하므로 별도의 `RUN chown` 레이어가 필요 없어 이미지 크기가 작다.

### 실전 Dockerfile: Next.js 비루트 실행

```dockerfile
FROM node:20-alpine AS base

# 1. 의존성 설치
FROM base AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# 2. 빌드
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# 3. 프로덕션
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production

# 비루트 사용자 설정
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Next.js standalone 출력 복사
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
```

### 비루트 실행 검증

```bash
# 실행 중인 컨테이너의 사용자 확인
docker exec my-app whoami
# 출력: nextjs

docker exec my-app id
# 출력: uid=1001(nextjs) gid=1001(nodejs)

# 프로세스 확인
docker top my-app
# UID가 1001인지 확인
```

---

## 3. Docker Secrets

### 환경변수로 비밀 전달의 위험성

환경변수는 편리하지만, 여러 경로로 노출될 수 있다.

```bash
# 위험: docker inspect로 환경변수가 모두 보인다
docker run -e DATABASE_URL="postgres://user:password@db:5432/mydb" my-app

docker inspect my-app --format '{{.Config.Env}}'
# 출력: [DATABASE_URL=postgres://user:password@db:5432/mydb ...]
```

환경변수가 노출되는 경로:

- `docker inspect` 출력
- `/proc/<pid>/environ` 파일 (같은 호스트의 다른 프로세스에서 접근 가능)
- 로그에 실수로 출력 (`console.log(process.env)`)
- 자식 프로세스에 자동 상속

### Docker Compose Secrets

Docker Compose의 시크릿(*Secret - 컨테이너에 안전하게 전달되는 민감한 데이터*)은 파일 시스템을 통해 비밀을 주입한다.

```yaml
# docker-compose.yml
services:
  api:
    build: .
    secrets:
      - db_password
      - api_key
    environment:
      # 비밀이 아닌 설정값만 환경변수로
      NODE_ENV: production
      DB_HOST: postgres
      DB_NAME: myapp

  postgres:
    image: postgres:16-alpine
    secrets:
      - db_password
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password

secrets:
  db_password:
    file: ./secrets/db_password.txt
  api_key:
    file: ./secrets/api_key.txt
```

시크릿 파일은 컨테이너 내부의 `/run/secrets/<시크릿_이름>` 경로에 마운트된다.

### Node.js에서 Secrets 파일 읽기 패턴

```typescript
import { readFileSync } from "fs";

function getSecret(name: string): string {
  // Docker secrets 경로에서 먼저 시도
  const secretPath = `/run/secrets/${name}`;
  try {
    return readFileSync(secretPath, "utf-8").trim();
  } catch {
    // 개발 환경: 환경변수 폴백
    const envValue = process.env[name.toUpperCase()];
    if (envValue) return envValue;

    throw new Error(
      `Secret "${name}" not found in ${secretPath} or environment`
    );
  }
}

// 사용
const dbPassword = getSecret("db_password");
const apiKey = getSecret("api_key");

const dbUrl = `postgres://app:${dbPassword}@${process.env.DB_HOST}:5432/${process.env.DB_NAME}`;
```

이 패턴의 장점은 **프로덕션에서는 파일 기반 시크릿**, **개발 환경에서는 환경변수**를 사용할 수 있어 유연하다는 것이다.

### BuildKit --mount=type=secret

빌드 시점에 필요한 비밀(예: 프라이빗 npm 레지스트리 토큰)은 BuildKit의 시크릿 마운트를 사용한다. 이 방법은 Ch 4에서 다루었지만, 보안 관점에서 다시 정리한다.

```dockerfile
# syntax=docker/dockerfile:1

FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./

# 프라이빗 레지스트리 인증이 필요한 경우
RUN --mount=type=secret,id=npmrc,target=/app/.npmrc \
    npm ci --omit=dev

# .npmrc는 이 RUN이 끝나면 사라진다 — 이미지에 남지 않음
```

```bash
# 빌드 시 시크릿 전달
docker build --secret id=npmrc,src=$HOME/.npmrc -t my-app .
```

`--mount=type=secret`으로 마운트된 파일은 해당 `RUN` 명령어가 실행되는 동안에만 존재하며, **이미지 레이어에 절대 기록되지 않는다.**

---

## 4. 읽기전용 파일시스템

### --read-only 플래그

`--read-only` 플래그는 컨테이너의 루트 파일시스템을 읽기전용으로 마운트한다. 공격자가 컨테이너에 침입하더라도 악성 스크립트를 파일시스템에 작성할 수 없다.

```bash
# 파일시스템을 읽기전용으로 실행
docker run --read-only my-app

# 파일 쓰기 시도 시 오류
docker run --read-only my-app sh -c "echo hacked > /tmp/test"
# 출력: sh: can't create /tmp/test: Read-only file system
```

### Next.js에서 필요한 쓰기 가능 디렉토리

Next.js 애플리케이션은 런타임에 일부 디렉토리에 쓰기가 필요하다.

| 디렉토리 | 용도 |
|----------|------|
| `.next/cache` | ISR 캐시, 이미지 최적화 캐시 |
| `/tmp` | Node.js 임시 파일 |

### tmpfs와 조합

tmpfs(*tmpfs - 메모리 기반 임시 파일시스템으로, 컨테이너 종료 시 사라짐*)를 사용하면 필요한 디렉토리만 쓰기 가능하게 만들 수 있다.

```bash
# 기본 사용
docker run \
  --read-only \
  --tmpfs /tmp \
  --tmpfs /app/.next/cache \
  my-nextjs-app
```

Docker Compose에서의 설정:

```yaml
services:
  web:
    image: my-nextjs-app
    read_only: true
    tmpfs:
      - /tmp:size=64M
      - /app/.next/cache:size=256M
    environment:
      NODE_ENV: production
```

`tmpfs`의 `size` 옵션으로 메모리 사용량을 제한할 수 있다. Next.js의 이미지 최적화 캐시가 클 수 있으므로 `.next/cache`에는 충분한 크기를 할당한다.

### 읽기전용 + 비루트 조합

```bash
docker run \
  --read-only \
  --tmpfs /tmp \
  --tmpfs /app/.next/cache \
  --user 1001:1001 \
  my-nextjs-app
```

두 조치를 함께 사용하면 공격자가 할 수 있는 일이 크게 줄어든다. 파일을 쓸 수도, root 권한을 이용할 수도 없다.

---

## 5. 보안 프로파일

### seccomp (Secure Computing Mode)

seccomp(*seccomp - 리눅스 커널이 제공하는 시스템 콜 필터링 메커니즘*)은 컨테이너가 호출할 수 있는 시스템 콜을 제한한다.

Docker는 기본적으로 seccomp 프로파일을 적용한다. 300개 이상의 시스템 콜 중 약 44개를 차단하는데, `reboot`, `mount`, `kexec_load` 같은 위험한 시스템 콜이 포함된다.

```bash
# 기본 seccomp 프로파일 확인
docker run --rm alpine sh -c "grep Seccomp /proc/self/status"
# 출력: Seccomp: 2  (2 = filter mode, 즉 seccomp 활성화)

# seccomp 비활성화 (절대 프로덕션에서 사용하지 말 것)
docker run --security-opt seccomp=unconfined my-app
```

대부분의 Node.js 애플리케이션에서 커스텀 seccomp 프로파일은 불필요하다. 기본 프로파일로 충분하다.

### AppArmor / SELinux

AppArmor(*AppArmor - Ubuntu/Debian 기반 시스템에서 사용하는 MAC 보안 모듈*)와 SELinux(*SELinux - Red Hat/CentOS 기반 시스템에서 사용하는 MAC 보안 모듈*)는 MAC(*Mandatory Access Control - 관리자가 정의한 정책에 따라 접근을 강제 제어하는 모델*)을 구현한다.

Docker는 AppArmor가 설치된 호스트에서 기본 AppArmor 프로파일(`docker-default`)을 자동 적용한다.

```bash
# AppArmor 프로파일 확인
docker inspect my-app --format '{{.AppArmorProfile}}'
# 출력: docker-default
```

### Linux Capabilities 제어

Linux Capabilities(*Capabilities - root 권한을 세분화한 개별 권한 단위*)는 root의 권한을 약 40개의 개별 권한으로 분리한 것이다. Docker는 기본적으로 일부 Capabilities만 부여한다.

```bash
# 기본 부여되는 Capabilities 확인
docker run --rm alpine sh -c "cat /proc/self/status | grep Cap"

# 모든 Capabilities 제거 후 필요한 것만 추가 (권장)
docker run \
  --cap-drop=ALL \
  --cap-add=NET_BIND_SERVICE \
  my-app
```

Node.js 애플리케이션에서 일반적으로 필요한 Capabilities:

| Capability | 용도 | 필요 여부 |
|-----------|------|----------|
| `CHOWN` | 파일 소유자 변경 | 비루트 실행 시 불필요 |
| `NET_BIND_SERVICE` | 1024 이하 포트 바인딩 | 포트 3000 사용 시 불필요 |
| `SETUID` / `SETGID` | 사용자/그룹 전환 | 비루트 실행 시 불필요 |
| `SYS_CHROOT` | chroot 사용 | 대부분 불필요 |

**결론: Node.js 앱은 `--cap-drop=ALL`만으로 대부분 동작한다.**

```yaml
# docker-compose.yml
services:
  web:
    image: my-nextjs-app
    cap_drop:
      - ALL
    security_opt:
      - no-new-privileges:true
```

### --security-opt=no-new-privileges

이 옵션은 컨테이너 내부의 프로세스가 `setuid` 비트 등을 통해 추가 권한을 획득하는 것을 방지한다.

```bash
docker run --security-opt=no-new-privileges my-app
```

항상 활성화하는 것을 권장한다. Node.js 애플리케이션에서 이 옵션으로 인한 문제가 발생하는 경우는 거의 없다.

---

## 6. NEXT_PUBLIC_* 환경변수의 보안 함의

### 빌드 시점 인라인

Next.js에서 `NEXT_PUBLIC_` 접두사가 붙은 환경변수는 **빌드 시점에 JavaScript 번들에 하드코딩**된다. 이것은 런타임 환경변수가 아니라 **문자열 리터럴로 치환**되는 것이다.

```typescript
// 소스 코드
const apiUrl = process.env.NEXT_PUBLIC_API_URL;

// 빌드 후 번들 (실제 값으로 치환됨)
const apiUrl = "https://api.example.com";
```

이는 `webpack.DefinePlugin` 또는 Next.js 내부의 문자열 치환으로 동작하며, 빌드 후에는 환경변수 참조가 완전히 사라진다.

### 브라우저에서 확인 가능

클라이언트 번들에 포함된 값은 **브라우저 DevTools의 Sources 탭**에서 누구나 확인할 수 있다. "소스 코드에 하드코딩하지 않았으니 안전하다"는 것은 착각이다.

```bash
# 빌드된 번들에서 값 검색
grep -r "NEXT_PUBLIC" .next/static/chunks/
# 환경변수 이름은 사라지고 값만 남아 있음
```

### 절대 넣으면 안 되는 것 vs 넣어도 되는 것

| 구분 | 예시 | 이유 |
|------|------|------|
| **금지** | API 시크릿 키 | 클라이언트에서 악용 가능 |
| **금지** | 데이터베이스 URL | 직접 DB 접근 가능 |
| **금지** | JWT 서명 키 | 토큰 위조 가능 |
| **금지** | 내부 마이크로서비스 URL | 내부 네트워크 구조 노출 |
| **허용** | 공개 API 엔드포인트 | 어차피 브라우저가 요청함 |
| **허용** | Google Analytics ID | 공개 정보 |
| **허용** | Sentry DSN (public) | 공개 키 기반 |
| **허용** | 기능 플래그 (공개) | UI 동작만 제어 |

### 런타임 환경변수 주입 패턴

환경에 따라 값을 바꿔야 하지만 클라이언트에서도 접근이 필요한 경우, 런타임 주입 패턴을 사용한다.

```typescript
// pages/api/config.ts (또는 app/api/config/route.ts)
import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    apiUrl: process.env.API_URL, // NEXT_PUBLIC_ 없이 서버에서만 읽음
    featureFlags: {
      newDashboard: process.env.FEATURE_NEW_DASHBOARD === "true",
    },
  });
}
```

```typescript
// lib/config.ts — 클라이언트에서 API로 설정값 조회
let cachedConfig: AppConfig | null = null;

export async function getConfig(): Promise<AppConfig> {
  if (cachedConfig) return cachedConfig;

  const res = await fetch("/api/config");
  cachedConfig = await res.json();
  return cachedConfig;
}
```

또는 `window.__ENV__` 패턴을 사용할 수 있다.

```dockerfile
# entrypoint.sh에서 런타임 환경변수를 JS 파일로 생성
#!/bin/sh
cat <<EOF > /app/public/__env.js
window.__ENV__ = {
  API_URL: "${API_URL}",
  FEATURE_FLAGS: "${FEATURE_FLAGS}"
};
EOF

exec node server.js
```

```html
<!-- _document.tsx 또는 layout.tsx -->
<script src="/__env.js"></script>
```

```typescript
// 클라이언트에서 접근
declare global {
  interface Window {
    __ENV__: {
      API_URL: string;
      FEATURE_FLAGS: string;
    };
  }
}

const apiUrl = window.__ENV__.API_URL;
```

이 방식은 **하나의 이미지를 여러 환경(staging, production)에서** 환경변수만 바꿔 사용할 수 있다는 장점이 있다.

---

## 7. docker.sock 보안

### docker.sock이란

`/var/run/docker.sock`은 Docker 데몬의 Unix 소켓이다. 이 소켓에 접근할 수 있으면 Docker API를 직접 호출하여 **모든 컨테이너를 제어**할 수 있다.

```bash
# docker.sock으로 할 수 있는 일 (= docker CLI의 모든 기능)
curl --unix-socket /var/run/docker.sock http://localhost/containers/json
curl --unix-socket /var/run/docker.sock http://localhost/images/json
```

### docker.sock 마운트가 위험한 이유

```yaml
# 절대 하지 말 것 (프로덕션 환경)
services:
  app:
    image: my-app
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
```

docker.sock에 접근 가능한 컨테이너는 다음을 할 수 있다:

1. **호스트 파일시스템 전체 마운트**: 새 컨테이너를 만들어 `/` 를 마운트
2. **다른 컨테이너의 환경변수 조회**: 다른 컨테이너의 비밀 정보 탈취
3. **특권 컨테이너 생성**: `--privileged` 컨테이너를 만들어 호스트 완전 제어
4. **이미지 빌드/푸시**: 악성 이미지를 레지스트리에 푸시

```bash
# docker.sock 접근 가능한 컨테이너에서 호스트 탈출
docker run -v /:/host --privileged alpine chroot /host
# 이제 호스트의 root 셸에 접근 가능
```

**docker.sock에 접근 가능 = 호스트의 root 권한과 동일하다.**

### docker.sock이 필요한 경우의 대안

일부 도구(CI 러너, 모니터링 에이전트)는 docker.sock 접근이 필요하다. 이 경우:

| 대안 | 설명 |
|------|------|
| Docker-in-Docker (dind) | 별도의 Docker 데몬을 컨테이너 안에서 실행 |
| Rootless Docker | 비루트 사용자로 Docker 데몬 실행, 호스트 root 탈취 불가 |
| TCP + TLS | 소켓 대신 TLS 인증서로 보호된 TCP 연결 사용 |
| 읽기전용 마운트 | `:/var/run/docker.sock:ro` (제한적 보호, 여전히 위험) |

```yaml
# Docker-in-Docker 사용 (CI 환경)
services:
  ci-runner:
    image: my-ci-runner
    environment:
      DOCKER_HOST: tcp://dind:2376
      DOCKER_TLS_CERTDIR: /certs
    volumes:
      - docker-certs:/certs/client:ro

  dind:
    image: docker:dind
    privileged: true  # dind 자체는 privileged 필요
    environment:
      DOCKER_TLS_CERTDIR: /certs
    volumes:
      - docker-certs:/certs

volumes:
  docker-certs:
```

---

## 8. 보안 체크리스트

프로덕션 배포 전에 확인해야 할 보안 항목을 단계별로 정리한다.

### 이미지 빌드 단계

- [ ] 경량 베이스 이미지 사용 (Alpine 또는 Distroless)
- [ ] 멀티스테이지 빌드로 빌드 도구 제거
- [ ] `.dockerignore`로 `.env`, `.git`, `node_modules` 제외
- [ ] `ARG`로 비밀 전달하지 않음 (BuildKit secrets 사용)
- [ ] 취약점 스캔 수행 (`docker scout quickview`)
- [ ] 이미지 태그 고정 (`node:20.11.0-alpine`, `latest` 사용 금지)

### Dockerfile 작성 단계

- [ ] `USER` 인스트럭션으로 비루트 사용자 지정
- [ ] `COPY --chown`으로 파일 소유권 설정
- [ ] 불필요한 패키지 설치하지 않음
- [ ] `RUN` 레이어에 비밀 정보 남기지 않음

### 런타임 단계

- [ ] `--cap-drop=ALL` 적용
- [ ] `--security-opt=no-new-privileges` 적용
- [ ] `--read-only` 적용 (필요한 곳만 tmpfs)
- [ ] 불필요한 포트 바인딩하지 않음
- [ ] `--privileged` 플래그 사용하지 않음
- [ ] docker.sock 마운트하지 않음

### 비밀 관리 단계

- [ ] 환경변수 대신 Docker secrets 사용
- [ ] `NEXT_PUBLIC_*`에 비밀 정보 포함하지 않음
- [ ] `.env` 파일이 이미지에 포함되지 않음

### 종합 Docker Compose 예시

```yaml
services:
  web:
    build:
      context: .
      secrets:
        - npmrc
    image: my-nextjs-app
    read_only: true
    tmpfs:
      - /tmp:size=64M
      - /app/.next/cache:size=256M
    cap_drop:
      - ALL
    security_opt:
      - no-new-privileges:true
    secrets:
      - db_password
      - api_key
    environment:
      NODE_ENV: production
      DB_HOST: postgres
    ports:
      - "3000:3000"
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: "1.0"

  postgres:
    image: postgres:16-alpine
    read_only: true
    tmpfs:
      - /tmp
      - /var/run/postgresql
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - SETUID
      - SETGID
      - FOWNER
    secrets:
      - db_password
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    volumes:
      - pgdata:/var/lib/postgresql/data

secrets:
  npmrc:
    file: ~/.npmrc
  db_password:
    file: ./secrets/db_password.txt
  api_key:
    file: ./secrets/api_key.txt

volumes:
  pgdata:
```

---

## 자주 하는 실수

| 실수 | 문제 | 해결 |
|------|------|------|
| root로 컨테이너 실행 | 컨테이너 탈출 시 호스트 root 획득 | `USER` 인스트럭션으로 비루트 실행 |
| docker.sock 무분별 마운트 | 호스트 완전 제어 가능 | dind 또는 rootless Docker 사용 |
| `NEXT_PUBLIC_*`에 비밀 정보 | 클라이언트 번들에 노출 | 서버 사이드에서만 접근, API route로 필요한 값만 전달 |
| `.env` 파일이 이미지에 포함 | 누구나 이미지에서 추출 가능 | `.dockerignore`에 추가 |
| 취약점 스캔 미수행 | 알려진 CVE가 프로덕션에 배포 | CI에서 `docker scout` 자동화 (Ch 14) |
| `--privileged` 플래그 남용 | 모든 보안 격리 해제 | 필요한 Capabilities만 `--cap-add` |
| `ARG`로 비밀 전달 | 이미지 히스토리에 기록 | `--mount=type=secret` 사용 |
| `latest` 태그 사용 | 검증되지 않은 새 이미지가 자동 적용 | 특정 버전 태그 고정 |

---

## 명령어 레퍼런스

| 명령어 | 설명 |
|--------|------|
| `docker run --read-only` | 컨테이너 파일시스템을 읽기전용으로 마운트 |
| `docker run --tmpfs /path` | 메모리 기반 임시 파일시스템 마운트 |
| `docker run --cap-drop=ALL` | 모든 Linux Capabilities 제거 |
| `docker run --cap-add=CAP` | 특정 Capability 추가 |
| `docker run --security-opt=no-new-privileges` | 권한 에스컬레이션 방지 |
| `docker run --security-opt seccomp=profile.json` | 커스텀 seccomp 프로파일 적용 |
| `docker run --user 1001:1001` | 특정 UID:GID로 실행 |
| `docker secret create NAME FILE` | Docker Swarm 시크릿 생성 |
| `docker scout quickview IMAGE` | 이미지 취약점 요약 (Ch 9) |
| `docker scout cves IMAGE` | 이미지 CVE 상세 조회 (Ch 9) |
| `docker history IMAGE` | 이미지 레이어 히스토리 확인 (비밀 노출 검증) |
| `docker inspect --format '{{.Config.Env}}' CONTAINER` | 컨테이너 환경변수 조회 (노출 확인) |
| `docker build --secret id=NAME,src=FILE` | BuildKit 시크릿으로 빌드 |
| `docker top CONTAINER` | 컨테이너 프로세스의 실행 사용자 확인 |

---

## 요약

- **컨테이너는 VM이 아니다**: 호스트 커널을 공유하며, 잘못된 설정은 호스트 전체를 위험에 노출한다
- **비루트 실행은 필수다**: `USER` 인스트럭션으로 비루트 사용자를 지정하고, `COPY --chown`으로 파일 소유권을 관리한다
- **환경변수는 안전하지 않다**: `docker inspect`로 노출되므로, Docker secrets(파일 기반)를 사용한다
- **읽기전용 파일시스템**: `--read-only`와 `tmpfs`를 조합하여 공격자의 파일 쓰기를 차단한다
- **Capabilities는 최소한으로**: `--cap-drop=ALL` 후 필요한 것만 `--cap-add`한다
- **`NEXT_PUBLIC_*`에 비밀을 넣지 않는다**: 클라이언트 번들에 하드코딩되어 누구나 볼 수 있다
- **docker.sock은 root 권한과 같다**: 프로덕션 컨테이너에 절대 마운트하지 않는다
- **보안은 레이어다**: 하나의 조치만으로는 부족하며, 여러 보안 조치를 겹쳐 적용하는 심층 방어(*Defense in Depth*)가 원칙이다

---

## 다른 챕터와의 관계

| 챕터 | 관계 |
|------|------|
| **Ch 4 (Dockerfile 심화)** | `USER` 인스트럭션, `--mount=type=secret`의 기본 사용법을 다룸 — 본 챕터에서 보안 관점으로 재조명 |
| **Ch 9 (이미지 최적화)** | 취약점 스캔(`docker scout`), 경량 베이스 이미지 선택이 보안에도 직결됨 |
| **Ch 11 (로깅과 모니터링)** | 보안 이벤트(비정상 접근, 권한 에스컬레이션 시도)를 로그로 추적하는 방법 |
| **Ch 14 (CI/CD)** | 보안 스캔을 CI 파이프라인에 통합하여 취약한 이미지가 배포되지 않도록 자동화 |
