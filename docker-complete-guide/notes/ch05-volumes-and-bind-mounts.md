# Chapter 5: 데이터 영속성과 바인드 마운트: Volumes and Bind Mounts

## 핵심 질문

컨테이너가 삭제되면 데이터도 함께 사라지는데, 이를 어떻게 해결하는가? 볼륨, 바인드 마운트, tmpfs의 차이는 무엇이고, Node.js 개발 환경에서 바인드 마운트를 어떻게 활용하는가?

---

## 1. 컨테이너의 데이터 문제

### 컨테이너의 읽기/쓰기 레이어

Ch 3에서 다루었듯이, Docker 컨테이너는 이미지 레이어(읽기 전용) 위에 얇은 R/W 레이어(*Read/Write Layer - 컨테이너가 실행 중일 때 파일을 쓸 수 있는 임시 레이어*)를 가진다. 컨테이너 내부에서 생성하거나 수정한 모든 파일은 이 R/W 레이어에 기록된다.

문제는 **R/W 레이어가 컨테이너의 생명주기에 종속된다**는 것이다:

```bash
# 컨테이너 생성 후 파일 작성
docker run -d --name my-app node:20-alpine sh -c "echo 'important data' > /app/data.txt && sleep 3600"

# 파일 확인
docker exec my-app cat /app/data.txt
# important data

# 컨테이너 삭제
docker rm -f my-app

# 같은 이미지로 새 컨테이너 생성 — 데이터 사라짐
docker run --name my-app node:20-alpine cat /app/data.txt
# cat: can't open '/app/data.txt': No such file or directory
```

### 영속성이 필요한 데이터들

실제 애플리케이션에서 컨테이너 삭제 후에도 보존되어야 하는 데이터는 다양하다:

| 데이터 유형 | 예시 | 영속성 필요도 |
|---|---|---|
| 데이터베이스 파일 | PostgreSQL의 `/var/lib/postgresql/data` | 필수 |
| 사용자 업로드 파일 | `/app/uploads`에 저장된 이미지, 문서 | 필수 |
| 애플리케이션 로그 | `/app/logs`에 쌓이는 로그 파일 | 높음 |
| 캐시 데이터 | Redis의 RDB 스냅샷, 빌드 캐시 | 중간 |
| 설정 파일 | 환경별 설정, 인증서 | 높음 |
| 세션 데이터 | 로그인 세션, 임시 토큰 | 낮음 (메모리도 가능) |

### Docker의 3가지 데이터 마운트 옵션

Docker는 이 문제를 해결하기 위해 세 가지 마운트 방식을 제공한다:

```
┌──────────────────────────────────────────────────┐
│              Docker 컨테이너                       │
│                                                    │
│   /app/data    /app/src     /app/tmp               │
│       │            │            │                   │
└───────┼────────────┼────────────┼──────────────────┘
        │            │            │
   ┌────▼────┐  ┌────▼────┐  ┌───▼────┐
   │  Volume  │  │  Bind   │  │ tmpfs  │
   │         │  │  Mount   │  │ Mount  │
   └────┬────┘  └────┬────┘  └────────┘
        │            │         (메모리)
   Docker가       호스트의
   관리하는       특정 경로
   스토리지      /home/user/src
```

- **볼륨(Volume)**: Docker가 관리하는 영속 스토리지. 프로덕션 데이터에 적합하다.
- **바인드 마운트(Bind Mount)**: 호스트의 특정 디렉터리를 컨테이너에 직접 연결한다. 개발 환경에 적합하다.
- **tmpfs 마운트(tmpfs Mount)**: 메모리에만 존재하는 임시 파일시스템이다. 민감한 데이터에 적합하다.

---

## 2. 볼륨(Volume)

볼륨(*Volume - Docker Engine이 관리하는 호스트 파일시스템 내의 영속 스토리지 영역*)은 Docker가 권장하는 데이터 영속화 메커니즘이다. 볼륨은 Docker가 직접 생성하고 관리하며, 호스트 파일시스템의 특정 영역(`/var/lib/docker/volumes/`)에 데이터를 저장한다.

### 볼륨의 핵심 특성

1. **Docker가 관리**: 사용자가 호스트 경로를 직접 알 필요 없다.
2. **컨테이너 독립적**: 컨테이너를 삭제해도 볼륨은 남아있다.
3. **여러 컨테이너 공유 가능**: 하나의 볼륨을 여러 컨테이너에 마운트할 수 있다.
4. **드라이버 지원**: 로컬 디스크뿐 아니라 NFS, 클라우드 스토리지 등 다양한 드라이버를 사용할 수 있다.
5. **OS 호환성**: Linux, macOS, Windows 모두에서 동일하게 동작한다.

### 볼륨 관리 명령어

```bash
# 볼륨 생성
docker volume create my-data

# 볼륨 목록 확인
docker volume ls

# 볼륨 상세 정보
docker volume inspect my-data
# [
#     {
#         "CreatedAt": "2026-03-07T10:00:00Z",
#         "Driver": "local",
#         "Labels": {},
#         "Mountpoint": "/var/lib/docker/volumes/my-data/_data",
#         "Name": "my-data",
#         "Options": {},
#         "Scope": "local"
#     }
# ]

# 특정 볼륨 삭제
docker volume rm my-data

# 사용되지 않는 모든 볼륨 정리
docker volume prune

# -f 옵션으로 확인 없이 즉시 삭제
docker volume prune -f
```

### Named Volume vs Anonymous Volume

볼륨은 이름의 유무에 따라 두 가지로 나뉜다:

**Named Volume (이름 있는 볼륨)**:

```bash
# 명시적으로 이름을 지정한 볼륨
docker run -d --name postgres \
  -v postgres-data:/var/lib/postgresql/data \
  postgres:16

# 볼륨 확인
docker volume ls
# DRIVER    VOLUME NAME
# local     postgres-data
```

이름이 있으므로 다른 컨테이너에서 같은 이름으로 참조할 수 있고, 관리가 쉽다.

**Anonymous Volume (익명 볼륨)**:

```bash
# 이름 없이 컨테이너 경로만 지정
docker run -d --name my-app \
  -v /app/node_modules \
  node:20-alpine

# 볼륨 확인 — 해시 형태의 이름이 자동 생성됨
docker volume ls
# DRIVER    VOLUME NAME
# local     a1b2c3d4e5f6...
```

익명 볼륨은 자동 생성된 해시 이름을 가지며, 컨테이너 삭제 시 참조를 잃기 쉽다. 주로 특정 경로를 바인드 마운트로부터 보호하는 용도로 사용한다 (5절에서 상세히 다룬다).

### `-v` 문법 vs `--mount` 문법

Docker는 볼륨을 마운트하는 두 가지 문법을 제공한다:

**`-v` (또는 `--volume`) 문법**: 간결하지만 모호할 수 있다:

```bash
# 형식: -v <볼륨명>:<컨테이너경로>[:옵션]
docker run -d \
  -v my-data:/app/data \
  -v my-data:/app/data:ro \  # 읽기 전용
  my-image
```

**`--mount` 문법**: 더 명시적이고 가독성이 좋다:

```bash
# key=value 쌍으로 구성
docker run -d \
  --mount type=volume,source=my-data,target=/app/data \
  --mount type=volume,source=my-data,target=/app/data,readonly \
  my-image
```

> **핵심 통찰**: Docker 공식 문서는 `--mount` 문법을 권장한다. `-v`는 볼륨과 바인드 마운트를 구문만으로 구분하기 어려운 반면, `--mount`는 `type=volume`과 `type=bind`로 명확히 구분된다. 특히 Compose 파일이 아닌 CLI에서 직접 사용할 때 `--mount`가 실수를 줄여준다.

### 실전 예제: PostgreSQL 데이터 영속화

Node.js 앱의 데이터베이스로 PostgreSQL을 사용하는 시나리오를 보자:

```bash
# 볼륨 생성
docker volume create pgdata

# PostgreSQL 컨테이너 실행 (데이터를 볼륨에 저장)
docker run -d \
  --name postgres \
  -e POSTGRES_PASSWORD=mysecret \
  -e POSTGRES_DB=myapp \
  --mount type=volume,source=pgdata,target=/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:16

# Node.js 앱에서 연결 테스트
docker exec postgres psql -U postgres -d myapp -c "CREATE TABLE users (id SERIAL PRIMARY KEY, name TEXT);"
docker exec postgres psql -U postgres -d myapp -c "INSERT INTO users (name) VALUES ('Alice');"

# 컨테이너 삭제
docker rm -f postgres

# 같은 볼륨으로 새 컨테이너 실행 — 데이터가 보존됨
docker run -d \
  --name postgres-new \
  -e POSTGRES_PASSWORD=mysecret \
  --mount type=volume,source=pgdata,target=/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:16

docker exec postgres-new psql -U postgres -d myapp -c "SELECT * FROM users;"
#  id | name
# ----+-------
#   1 | Alice
```

### 실전 예제: MongoDB 데이터 영속화

```bash
docker volume create mongodb-data

docker run -d \
  --name mongo \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=secret \
  --mount type=volume,source=mongodb-data,target=/data/db \
  -p 27017:27017 \
  mongo:7
```

---

## 3. 바인드 마운트(Bind Mount)

바인드 마운트(*Bind Mount - 호스트 파일시스템의 특정 파일 또는 디렉터리를 컨테이너 내부의 경로에 직접 연결하는 방식*)는 호스트의 파일/디렉터리를 컨테이너에 그대로 노출한다. 볼륨과 달리 Docker가 관리하지 않으며, 호스트의 절대 경로를 직접 지정한다.

### `-v` 문법과 `--mount` 문법

```bash
# -v 문법: 호스트 절대경로로 시작하면 바인드 마운트
docker run -d \
  -v $(pwd):/app \
  -v $(pwd)/config.json:/app/config.json:ro \
  my-image

# --mount 문법: type=bind 명시
docker run -d \
  --mount type=bind,source=$(pwd),target=/app \
  --mount type=bind,source=$(pwd)/config.json,target=/app/config.json,readonly \
  my-image
```

> **핵심 통찰**: `-v` 문법에서 `source`가 `/`로 시작하면 바인드 마운트, 그렇지 않으면 볼륨으로 해석된다. 예를 들어 `-v mydata:/app`은 `mydata`라는 이름의 볼륨을 마운트하고, `-v /home/user/data:/app`은 바인드 마운트다. 이 모호함이 `--mount`를 권장하는 이유 중 하나이다.

### 바인드 마운트의 동작 원리

바인드 마운트는 컨테이너의 해당 경로를 **완전히 덮어쓴다**:

```bash
# 컨테이너 이미지에 /app/index.js가 있어도
# 호스트의 $(pwd)가 비어있으면 컨테이너의 /app도 비어있게 됨
docker run -v $(pwd)/empty-dir:/app my-image ls /app
# (아무것도 없음)
```

이 "덮어쓰기" 특성은 양날의 검이다. 개발 시 소스 코드를 실시간 반영하는 데 활용할 수 있지만, 의도치 않게 컨테이너 내부의 파일을 가릴 수도 있다.

### 양방향 동기화

바인드 마운트는 **양방향**이다. 호스트에서 파일을 수정하면 컨테이너에 즉시 반영되고, 컨테이너에서 파일을 수정하면 호스트에도 즉시 반영된다:

```bash
# 호스트에서 파일 생성
echo "hello from host" > $(pwd)/test.txt

# 컨테이너에서 확인 — 즉시 보임
docker exec my-app cat /app/test.txt
# hello from host

# 컨테이너에서 파일 생성
docker exec my-app sh -c "echo 'hello from container' > /app/from-container.txt"

# 호스트에서 확인 — 즉시 보임
cat $(pwd)/from-container.txt
# hello from container
```

### 바인드 마운트의 주의점

**1. 호스트 경로가 반드시 존재해야 한다**

`--mount type=bind`를 사용할 때 호스트 경로가 없으면 에러가 발생한다:

```bash
# --mount는 경로가 없으면 에러
docker run --mount type=bind,source=/nonexistent/path,target=/app my-image
# Error: invalid mount config: bind source path does not exist

# -v는 경로가 없으면 디렉터리를 자동 생성함 (혼란의 원인)
docker run -v /nonexistent/path:/app my-image
# /nonexistent/path 디렉터리가 root 소유로 자동 생성됨
```

**2. 권한 문제**

컨테이너 프로세스의 UID/GID와 호스트 파일의 소유자가 다르면 권한 문제가 발생할 수 있다:

```bash
# 컨테이너 내 node 사용자(UID 1000)가 파일에 쓰려 하지만
# 호스트 파일이 root 소유인 경우 → Permission denied
docker run -u node -v $(pwd):/app my-image sh -c "echo test > /app/output.txt"
```

**3. 보안 고려사항**

바인드 마운트는 호스트 파일시스템에 직접 접근하므로, 컨테이너가 호스트의 중요한 파일을 읽거나 수정할 수 있다. 프로덕션에서는 읽기 전용(`:ro`)을 적극 활용해야 한다:

```bash
# 설정 파일은 읽기 전용으로 마운트
docker run -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf:ro nginx:alpine
```

---

## 4. tmpfs 마운트

tmpfs 마운트(*tmpfs Mount - 호스트의 메모리에만 존재하는 임시 파일시스템으로, 컨테이너 중지 시 데이터가 사라짐*)는 디스크에 전혀 기록하지 않는 마운트 방식이다. 데이터는 호스트의 RAM에만 존재하며, 컨테이너가 중지되면 완전히 사라진다.

```bash
# tmpfs 마운트 사용
docker run -d \
  --name secure-app \
  --mount type=tmpfs,target=/app/tmp,tmpfs-size=100m \
  my-image

# --tmpfs 단축 문법 (옵션 제한적)
docker run -d \
  --name secure-app \
  --tmpfs /app/tmp:size=100m \
  my-image
```

### tmpfs가 적합한 경우

| 용도 | 설명 |
|---|---|
| 세션 저장소 | 로그인 세션을 메모리에만 보관 |
| 임시 토큰/시크릿 | JWT 서명 키 등 민감한 임시 데이터 |
| 빌드 임시 파일 | 컴파일 중간 산출물 |
| 테스트 임시 데이터 | 테스트 실행 중 생성되는 임시 파일 |

### Node.js에서의 tmpfs 활용 예시

```typescript
// Express 앱에서 세션을 tmpfs 경로에 저장
import session from 'express-session';
import FileStore from 'session-file-store';

const FileStoreSession = FileStore(session);

app.use(session({
  store: new FileStoreSession({
    path: '/app/tmp/sessions',  // tmpfs에 마운트된 경로
    ttl: 3600,
  }),
  secret: process.env.SESSION_SECRET!,
  resave: false,
  saveUninitialized: false,
}));
```

```bash
# 실행 시 세션 디렉터리를 tmpfs로 마운트
docker run -d \
  --mount type=tmpfs,target=/app/tmp,tmpfs-size=50m \
  -e SESSION_SECRET=my-secret \
  my-express-app
```

> **핵심 통찰**: tmpfs는 Linux에서만 사용할 수 있다. Docker Desktop(macOS, Windows)에서는 Linux VM 내부의 메모리를 사용하므로 동작은 하지만, 호스트 OS에서 직접 tmpfs를 사용하는 것은 아니다.

---

## 5. Node.js 개발 환경에서의 바인드 마운트

바인드 마운트의 가장 대표적인 활용 사례는 **개발 환경**이다. 소스 코드를 수정할 때마다 이미지를 다시 빌드하지 않고, 변경 사항이 컨테이너에 실시간으로 반영되도록 설정할 수 있다.

### 기본 Dockerfile

```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

EXPOSE 3000
CMD ["npm", "run", "dev"]
```

### 핵심 패턴: 소스 코드 바인드 마운트 + node_modules 익명 볼륨

```bash
docker run -d \
  --name my-next-app \
  -v $(pwd):/app \
  -v /app/node_modules \
  -p 3000:3000 \
  my-next-app
```

이 명령에는 두 개의 `-v` 옵션이 있다:

1. **`-v $(pwd):/app`**: 호스트의 현재 디렉터리를 컨테이너의 `/app`에 바인드 마운트한다. 소스 코드 변경이 실시간으로 반영된다.
2. **`-v /app/node_modules`**: `/app/node_modules` 경로에 익명 볼륨을 생성한다. 이 볼륨이 바인드 마운트를 "가린다".

### 왜 node_modules를 익명 볼륨으로 분리하는가?

이것은 Docker로 Node.js를 개발할 때 가장 흔히 겪는 문제 중 하나이다.

**문제 상황**:

```
호스트 (macOS)              컨테이너 (Linux Alpine)
├── src/                    ├── src/           ← 바인드 마운트로 동기화
├── package.json            ├── package.json   ← 바인드 마운트로 동기화
├── node_modules/           ├── node_modules/  ← 호스트 것이 덮어씀!
│   └── bcrypt/             │   └── bcrypt/
│       └── (macOS binary)  │       └── (macOS binary) ← Linux에서 실행 불가!
```

바인드 마운트 `-v $(pwd):/app`은 호스트의 전체 프로젝트 디렉터리를 컨테이너에 마운트한다. 이때 호스트에 `node_modules`가 있으면, 컨테이너 이미지 빌드 중 `npm ci`로 설치한 Linux용 `node_modules`를 **호스트의 macOS용 `node_modules`가 덮어쓴다**.

`bcrypt`, `sharp`, `esbuild` 같은 네이티브 바이너리(*Native Binary - OS와 CPU 아키텍처에 맞게 컴파일된 실행 파일*)를 포함하는 패키지는 OS별로 다른 바이너리를 설치하므로, macOS에서 설치한 것은 Linux 컨테이너에서 동작하지 않는다.

**해결: 익명 볼륨으로 node_modules 보호**:

```
호스트 (macOS)              컨테이너 (Linux Alpine)
├── src/                    ├── src/             ← 바인드 마운트
├── package.json            ├── package.json     ← 바인드 마운트
├── node_modules/           ├── node_modules/    ← 익명 볼륨 (컨테이너 것 보존!)
│   └── (macOS binary)      │   └── (Linux binary) ← Docker 빌드 시 설치된 것
```

Docker는 마운트 우선순위에서 **더 구체적인 경로의 마운트가 우선**한다. `/app`에 바인드 마운트가 있어도, `/app/node_modules`에 볼륨이 있으면 후자가 우선한다. 결과적으로 컨테이너의 `node_modules`는 이미지 빌드 시 `npm ci`로 설치한 Linux용 패키지를 유지한다.

> **실무 팁**: 호스트에서 `node_modules`를 아예 `.dockerignore`에 추가하는 것이 일반적이다. 하지만 바인드 마운트 시에는 `.dockerignore`가 적용되지 않으므로 (`.dockerignore`는 빌드 컨텍스트에만 영향), 익명 볼륨 기법이 필수다.

### HMR(Hot Module Replacement) 설정

바인드 마운트로 소스 코드를 연결했지만, 파일 변경을 감지하지 못해 HMR이 동작하지 않는 경우가 흔하다.

**원인**: Docker Desktop(macOS, Windows)에서 바인드 마운트된 파일의 변경을 컨테이너 내부에 전달할 때, 네이티브 파일시스템 이벤트(*inotify - Linux 커널의 파일시스템 변경 감지 메커니즘*)가 정상적으로 전달되지 않을 수 있다.

**Next.js 해결 방법**:

```typescript
// next.config.ts
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  webpack: (config) => {
    config.watchOptions = {
      poll: 1000,       // 1초마다 파일 변경 확인
      aggregateTimeout: 300,  // 변경 감지 후 300ms 대기 후 리빌드
    };
    return config;
  },
};

export default nextConfig;
```

또는 환경변수로 설정:

```bash
# WATCHPACK_POLLING을 활성화하면 Next.js가 폴링 방식으로 파일 감지
docker run -d \
  -e WATCHPACK_POLLING=true \
  -v $(pwd):/app \
  -v /app/node_modules \
  -p 3000:3000 \
  my-next-app
```

**Vite(React) 해결 방법**:

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',  // 컨테이너 외부에서 접근 허용
    watch: {
      usePolling: true,    // 폴링 방식 사용
      interval: 1000,      // 1초 간격
    },
    hmr: {
      port: 3000,  // HMR WebSocket 포트
    },
  },
});
```

### macOS에서의 바인드 마운트 성능

macOS에서 Docker Desktop은 Linux VM 위에서 동작하며, 바인드 마운트는 호스트(macOS)와 VM(Linux) 사이의 파일 공유를 필요로 한다. 이 과정에서 성능 저하가 발생할 수 있다.

**파일 공유 백엔드의 변천**:

| 백엔드 | 시기 | 성능 | 비고 |
|---|---|---|---|
| osxfs | 초기 | 느림 | 초기 구현 |
| gRPC FUSE | 2020년~ | 보통 | 개선된 버전 |
| VirtioFS | 2022년~ | 빠름 | 현재 기본값, 네이티브에 근접 |

이전에는 `-v $(pwd):/app:delegated` 또는 `:cached` 같은 일관성 옵션을 사용했지만, VirtioFS가 기본이 된 현재 Docker Desktop에서는 이 옵션들이 무시된다(호환성을 위해 에러를 발생시키지는 않는다).

> **실무 팁**: Docker Desktop 4.15+ (2022년 말)부터 VirtioFS가 기본이다. 그 이전 버전을 사용 중이라면 Docker Desktop 설정에서 VirtioFS를 활성화하면 바인드 마운트 성능이 크게 향상된다.

### Docker Compose에서의 설정

실무에서는 개발 환경을 Docker Compose로 관리하는 것이 일반적이다:

```yaml
# compose.yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - WATCHPACK_POLLING=true
      - NODE_ENV=development
    volumes:
      - .:/app                  # 소스 코드 바인드 마운트
      - /app/node_modules       # node_modules 익명 볼륨
      - /app/.next              # .next 빌드 캐시도 보호 (선택)
    depends_on:
      - db

  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: devpassword
      POSTGRES_DB: myapp
    volumes:
      - pgdata:/var/lib/postgresql/data   # Named volume으로 DB 영속화
    ports:
      - "5432:5432"

volumes:
  pgdata:    # Named volume 선언
```

이 설정에서:
- `app` 서비스: 바인드 마운트(소스 코드) + 익명 볼륨(node_modules, .next)
- `db` 서비스: Named 볼륨(PostgreSQL 데이터)
- 최상위 `volumes:` 섹션: Named 볼륨을 선언 (Ch 7에서 상세 다룸)

---

## 6. 볼륨 vs 바인드 마운트 선택 기준

### 비교 테이블

| 항목 | 볼륨 (Volume) | 바인드 마운트 (Bind Mount) | tmpfs |
|---|---|---|---|
| **관리 주체** | Docker Engine | 사용자 (호스트 경로 직접 지정) | Docker Engine (메모리) |
| **호스트 위치** | `/var/lib/docker/volumes/` | 사용자가 지정한 경로 | 메모리 (디스크 없음) |
| **영속성** | 컨테이너 삭제 후에도 유지 | 호스트 파일 그대로 유지 | 컨테이너 중지 시 소멸 |
| **여러 컨테이너 공유** | 가능 | 가능 | 불가 |
| **Docker CLI로 관리** | `docker volume` 명령 | 해당 없음 | 해당 없음 |
| **성능** | 최적 (특히 Linux) | macOS에서 오버헤드 가능 | 가장 빠름 (메모리) |
| **호스트에서 직접 접근** | 어려움 (Docker 경로) | 쉬움 (일반 경로) | 불가 |
| **프로덕션 적합성** | 적합 | 비권장 (설정 파일 정도만) | 임시 데이터만 |
| **주요 용도** | DB 데이터, 업로드 파일 | 개발 시 소스 코드 마운트 | 세션, 시크릿, 캐시 |

### 결정 플로우차트

```
데이터 영속성이 필요한가?
├── 아니오 → tmpfs 마운트 (메모리만)
└── 예
    ├── 호스트에서 파일을 직접 편집해야 하는가?
    │   ├── 예 (개발 환경) → 바인드 마운트
    │   └── 아니오
    │       └── 볼륨 (Volume)
    └── 여러 컨테이너가 데이터를 공유해야 하는가?
        ├── 예 → Named 볼륨
        └── 아니오 → Named 볼륨 또는 바인드 마운트 (용도에 따라)
```

> **핵심 통찰**: 확신이 없다면 볼륨을 선택하라. Docker 공식 문서도 볼륨을 기본 권장하며, 바인드 마운트는 개발 환경이나 호스트 설정 파일 주입처럼 호스트 경로에 의존해야 하는 경우에만 사용하는 것이 좋다.

---

## 7. 볼륨 백업과 복원

### `--volumes-from`을 이용한 백업

`--volumes-from` 플래그는 다른 컨테이너의 볼륨을 그대로 마운트한다. 이를 활용하면 임시 컨테이너로 볼륨 데이터를 백업할 수 있다:

```bash
# 1. 백업 대상 컨테이너 확인
docker inspect postgres --format '{{ range .Mounts }}{{ .Name }}:{{ .Destination }}{{ end }}'
# pgdata:/var/lib/postgresql/data

# 2. 임시 컨테이너로 볼륨을 tar 압축하여 호스트에 저장
docker run --rm \
  --volumes-from postgres \
  -v $(pwd)/backups:/backup \
  alpine \
  tar czf /backup/pgdata-backup-$(date +%Y%m%d).tar.gz -C /var/lib/postgresql/data .

# 결과: ./backups/pgdata-backup-20260307.tar.gz 파일 생성
```

이 명령의 동작을 분석하면:
- `--rm`: 작업 완료 후 임시 컨테이너를 자동 삭제한다.
- `--volumes-from postgres`: `postgres` 컨테이너의 모든 볼륨을 같은 경로에 마운트한다.
- `-v $(pwd)/backups:/backup`: 백업 파일을 호스트에 저장하기 위한 바인드 마운트다.
- `tar czf ...`: 볼륨 데이터를 gzip 압축한다.

### 직접 볼륨을 지정한 백업

`--volumes-from` 대신 볼륨 이름을 직접 지정할 수도 있다:

```bash
docker run --rm \
  -v pgdata:/source:ro \
  -v $(pwd)/backups:/backup \
  alpine \
  tar czf /backup/pgdata-backup.tar.gz -C /source .
```

`/source:ro`로 읽기 전용 마운트하여 백업 중 데이터 변경을 방지한다.

### 복원

```bash
# 1. 새 볼륨 생성
docker volume create pgdata-restored

# 2. 백업 파일에서 복원
docker run --rm \
  -v pgdata-restored:/target \
  -v $(pwd)/backups:/backup:ro \
  alpine \
  sh -c "cd /target && tar xzf /backup/pgdata-backup.tar.gz"

# 3. 복원된 볼륨으로 컨테이너 실행
docker run -d \
  --name postgres-restored \
  -e POSTGRES_PASSWORD=mysecret \
  -v pgdata-restored:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:16
```

### 자동화 스크립트 예시

```bash
#!/bin/bash
# backup-volume.sh — 볼륨 백업 스크립트

VOLUME_NAME=$1
BACKUP_DIR=${2:-./backups}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/${VOLUME_NAME}-${TIMESTAMP}.tar.gz"

mkdir -p "$BACKUP_DIR"

docker run --rm \
  -v "${VOLUME_NAME}:/source:ro" \
  -v "${BACKUP_DIR}:/backup" \
  alpine \
  tar czf "/backup/${VOLUME_NAME}-${TIMESTAMP}.tar.gz" -C /source .

echo "Backup created: ${BACKUP_FILE}"

# 7일 이상 된 백업 삭제
find "$BACKUP_DIR" -name "${VOLUME_NAME}-*.tar.gz" -mtime +7 -delete
echo "Old backups cleaned up."
```

```bash
# 사용 예
./backup-volume.sh pgdata ./backups
./backup-volume.sh mongodb-data ./backups
```

---

## 자주 하는 실수

| 실수 | 문제점 | 올바른 방법 |
|---|---|---|
| node_modules를 바인드 마운트에 포함 | 호스트의 OS별 네이티브 바이너리가 컨테이너를 덮어씀 | `-v /app/node_modules` 익명 볼륨으로 분리 |
| 볼륨과 바인드 마운트를 `-v`로 혼동 | `-v mydata:/app`이 볼륨인지 바인드인지 불분명 | `--mount type=volume` 또는 `type=bind`로 명시 |
| macOS에서 HMR이 안 됨 | inotify 이벤트가 VM을 통과하지 못함 | `WATCHPACK_POLLING=true` 또는 `usePolling: true` 설정 |
| 볼륨을 정리하지 않아 디스크 부족 | 익명 볼륨과 미사용 볼륨이 계속 쌓임 | 주기적으로 `docker volume prune` 실행 |
| Dockerfile에 `VOLUME` 인스트럭션 사용 | 이미지 사용자가 의도치 않은 익명 볼륨 생성, 디버깅 어려움 | Dockerfile에서 `VOLUME`을 제거하고 런타임에 `-v`로 마운트 |
| `--mount type=bind`로 없는 경로 지정 | 에러 발생 (`bind source path does not exist`) | 마운트 전 호스트 경로 존재 여부 확인 |
| 바인드 마운트에 `.env` 파일 노출 | 민감한 환경 변수가 컨테이너에 노출됨 | Docker secrets 또는 환경변수 사용, `.env`는 `.dockerignore`에 추가 |
| 볼륨 데이터 백업 없이 `docker volume rm` | 영속 데이터 영구 손실 | 삭제 전 반드시 백업 수행 |

> **실무 팁**: `docker system df`로 Docker가 사용하는 디스크 공간을 확인할 수 있다. 볼륨이 차지하는 공간은 `docker system df -v`로 더 상세히 볼 수 있다.

```bash
docker system df
# TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
# Images          15        5         4.2GB     2.8GB (66%)
# Containers      8         3         120MB     80MB (66%)
# Local Volumes   12        4         1.5GB     900MB (60%)
# Build Cache     25        0         800MB     800MB (100%)
```

---

## 명령어 레퍼런스

| 명령어 | 설명 | 예시 |
|---|---|---|
| `docker volume create` | Named 볼륨 생성 | `docker volume create pgdata` |
| `docker volume ls` | 볼륨 목록 표시 | `docker volume ls` |
| `docker volume inspect` | 볼륨 상세 정보 | `docker volume inspect pgdata` |
| `docker volume rm` | 볼륨 삭제 | `docker volume rm pgdata` |
| `docker volume prune` | 미사용 볼륨 일괄 삭제 | `docker volume prune -f` |
| `docker run -v` | 볼륨 또는 바인드 마운트 (간결 문법) | `docker run -v pgdata:/data my-image` |
| `docker run --mount` | 마운트 (명시적 문법) | `docker run --mount type=volume,src=pgdata,dst=/data my-image` |
| `docker run --tmpfs` | tmpfs 마운트 (단축) | `docker run --tmpfs /tmp:size=100m my-image` |
| `docker run --volumes-from` | 다른 컨테이너의 볼륨 공유 | `docker run --volumes-from postgres alpine` |
| `docker system df` | Docker 디스크 사용량 확인 | `docker system df -v` |

---

## 요약

- 컨테이너의 R/W 레이어는 컨테이너 삭제 시 함께 소멸한다. 영속 데이터를 위해 **볼륨, 바인드 마운트, tmpfs** 세 가지 마운트 옵션을 사용한다.
- **볼륨**은 Docker가 관리하는 영속 스토리지로, 프로덕션 데이터(DB, 업로드 파일)에 적합하다. Named 볼륨은 이름으로 참조하고, 익명 볼륨은 특정 경로를 보호하는 데 사용한다.
- **바인드 마운트**는 호스트의 파일/디렉터리를 컨테이너에 직접 연결하며, 개발 환경에서 소스 코드를 실시간 반영하는 데 핵심이다.
- **tmpfs 마운트**는 메모리에만 존재하는 임시 파일시스템으로, 민감한 데이터나 임시 캐시에 적합하다.
- Node.js 개발에서는 **소스 코드 바인드 마운트 + node_modules 익명 볼륨** 패턴이 필수다. 호스트의 OS별 네이티브 바이너리가 컨테이너를 덮어쓰는 문제를 방지한다.
- macOS에서 HMR이 동작하지 않으면 **폴링 방식**(`WATCHPACK_POLLING=true`)을 활성화한다.
- `-v` 문법은 간결하지만 모호할 수 있으므로, `--mount` 문법으로 `type`을 명시하는 것이 권장된다.
- 볼륨 백업은 `--volumes-from`이나 직접 볼륨 마운트 후 `tar`로 수행하며, 주기적인 `docker volume prune`으로 디스크를 관리한다.

---

## 다른 챕터와의 관계

- **Ch 3 (컨테이너 기초)**: 컨테이너의 R/W 레이어 개념을 이해해야 왜 볼륨이 필요한지 알 수 있다.
- **Ch 4 (Dockerfile 작성)**: Dockerfile의 `VOLUME` 인스트럭션은 익명 볼륨을 생성하지만, 런타임 `-v` 옵션에 비해 유연성이 떨어지므로 사용을 피하는 것이 좋다.
- **Ch 7 (Docker Compose)**: Compose 파일의 `volumes:` 섹션에서 볼륨 선언과 서비스별 마운트를 선언적으로 관리한다. 이 챕터의 `-v` 명령이 Compose의 `volumes:` 설정으로 변환된다.
- **Ch 8 (개발/프로덕션 분리)**: 개발 환경에서는 바인드 마운트로 실시간 코드 반영, 프로덕션에서는 Named 볼륨으로 데이터만 영속화하는 패턴을 다룬다.
