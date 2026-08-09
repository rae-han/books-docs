# Chapter 7: 다중 컨테이너 애플리케이션: Docker Compose

## 핵심 질문

여러 컨테이너로 구성된 애플리케이션을 어떻게 정의하고 한 번에 관리하는가? compose.yaml의 핵심 문법은 무엇이고, 서비스 간 의존성과 네트워크는 어떻게 구성하는가?

---

## 1. Docker Compose란

실제 애플리케이션은 단일 컨테이너로 구성되는 경우가 드물다. Next.js 프론트엔드, Express API 서버, PostgreSQL 데이터베이스, Redis 캐시 — 이런 서비스들을 각각 `docker run` 명령어로 실행하고, 네트워크를 연결하고, 볼륨을 마운트하는 것은 번거롭고 오류가 발생하기 쉽다.

도커 컴포즈(*Docker Compose - 다중 컨테이너 애플리케이션을 YAML 파일 하나로 정의하고 관리하는 도구*)는 이 문제를 해결한다. 하나의 YAML 파일에 모든 서비스, 네트워크, 볼륨을 선언적으로 정의하고, 단일 명령어로 전체 스택을 시작하거나 종료할 수 있다.

### 1.1 V1에서 V2로의 역사

Docker Compose는 두 세대를 거쳤다.

| 구분 | V1 (레거시) | V2 (현재 표준) |
|------|-------------|----------------|
| **명령어** | `docker-compose` (하이픈) | `docker compose` (공백) |
| **구현 언어** | Python | Go |
| **설치 방식** | 별도 바이너리 설치 | Docker CLI 플러그인으로 내장 |
| **성능** | 상대적으로 느림 | 빠름 (Go 네이티브) |
| **상태** | 2023년 6월 EOL | 활발히 개발 중 |

V1은 2023년 6월에 공식적으로 지원이 종료되었다. 현재는 `docker compose` (V2)가 유일한 표준이며, Docker Desktop을 설치하면 자동으로 포함된다.

> **실무 팁**: CI/CD 스크립트나 Makefile에서 `docker-compose`(하이픈)를 사용하고 있다면 `docker compose`(공백)로 마이그레이션해야 한다. 대부분의 명령어는 동일하게 동작한다.

### 1.2 파일명 규칙

Docker Compose는 다음 순서로 설정 파일을 탐색한다:

1. `compose.yaml` — **현재 권장 표준**
2. `compose.yml`
3. `docker-compose.yaml`
4. `docker-compose.yml`

프로젝트에서 `compose.yaml`을 사용하는 것을 권장한다. `docker-compose.yml`은 여전히 작동하지만 레거시 관습이다.

### 1.3 Compose를 사용해야 하는 이유

```bash
# Compose 없이 4개 서비스를 실행하려면...
docker network create myapp
docker volume create pg-data

docker run -d --name redis --network myapp redis:7-alpine
docker run -d --name db --network myapp \
  -e POSTGRES_USER=user -e POSTGRES_PASSWORD=pass -e POSTGRES_DB=mydb \
  -v pg-data:/var/lib/postgresql/data postgres:16-alpine
docker run -d --name api --network myapp \
  -e DATABASE_URL=postgresql://user:pass@db:5432/mydb \
  -e REDIS_URL=redis://redis:6379 \
  -p 4000:4000 myapp-api
docker run -d --name web --network myapp \
  -e API_URL=http://api:4000 \
  -p 3000:3000 myapp-web
```

이 명령어들을 매번 순서대로 실행해야 하고, 종료할 때도 하나씩 `docker stop`과 `docker rm`을 해야 한다. Compose를 사용하면 이 모든 것이 `docker compose up -d` 한 줄로 대체된다.

---

## 2. compose.yaml 핵심 문법

compose.yaml 파일은 크게 다섯 가지 최상위 키(*Top-level Key*)로 구성된다.

```yaml
# compose.yaml의 전체 구조
services:    # 컨테이너 정의 (필수)
  ...
networks:    # 사용자 정의 네트워크 (선택)
  ...
volumes:     # Named 볼륨 정의 (선택)
  ...
configs:     # 설정 파일 (선택, Swarm/고급)
  ...
secrets:     # 비밀 데이터 (선택, Swarm/고급)
  ...
```

### 2.1 services 섹션

서비스(*Service*)는 Compose에서 컨테이너의 단위다. 각 서비스는 하나의 이미지를 기반으로 하나 이상의 컨테이너를 실행한다.

#### image vs build

서비스의 이미지를 지정하는 방법은 두 가지다.

```yaml
services:
  # 방법 1: 기존 이미지를 직접 사용
  redis:
    image: redis:7-alpine

  # 방법 2: Dockerfile에서 빌드
  api:
    build: ./api           # ./api 디렉토리의 Dockerfile 사용

  # 방법 3: 빌드 옵션을 상세하게 지정
  web:
    build:
      context: ./web       # 빌드 컨텍스트 경로
      dockerfile: Dockerfile.dev   # 사용할 Dockerfile 이름
      args:                # 빌드 인수
        NODE_ENV: development
    image: myapp-web:dev   # 빌드된 이미지에 태그 부여
```

`build`와 `image`를 동시에 지정하면, 빌드된 이미지에 해당 태그가 붙는다.

#### ports

호스트와 컨테이너 간 포트 매핑을 정의한다.

```yaml
services:
  api:
    ports:
      - "4000:4000"          # 호스트:컨테이너 (TCP)
      - "4001:4001/udp"      # UDP 프로토콜 지정
      - "127.0.0.1:4000:4000"  # 로컬호스트에만 바인딩
      - "4000"               # 컨테이너 포트만 지정 (호스트 포트 자동 할당)
```

> **실무 팁**: 로컬 개발 환경에서는 `"3000:3000"` 형태로 충분하지만, 프로덕션이나 공유 서버에서는 `"127.0.0.1:3000:3000"`으로 로컬호스트에만 바인딩하는 것이 안전하다. 그렇지 않으면 외부에서 직접 접근할 수 있다.

#### volumes

볼륨 마운트를 정의한다. 바인드 마운트와 Named 볼륨 모두 사용할 수 있다.

```yaml
services:
  api:
    volumes:
      # 바인드 마운트 (호스트 경로:컨테이너 경로)
      - ./api/src:/app/src

      # Named 볼륨 (최상위 volumes에 정의 필요)
      - node-modules:/app/node_modules

      # 읽기 전용 바인드 마운트
      - ./config:/app/config:ro

volumes:
  node-modules:       # Named 볼륨 선언
```

#### environment / env_file

환경변수를 주입하는 두 가지 방법이 있다.

```yaml
services:
  api:
    # 방법 1: 직접 정의 (리스트 형식)
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
      - REDIS_URL=redis://redis:6379
      - NODE_ENV=development

    # 방법 1: 직접 정의 (맵 형식 — 동일 결과)
    environment:
      DATABASE_URL: postgresql://user:pass@db:5432/mydb
      REDIS_URL: redis://redis:6379
      NODE_ENV: development

    # 방법 2: .env 파일에서 로드
    env_file:
      - .env              # 기본
      - .env.local         # 오버라이드 (나중 파일이 우선)
```

`.env` 파일 예시:

```bash
# .env
DATABASE_URL=postgresql://user:pass@db:5432/mydb
REDIS_URL=redis://redis:6379
NODE_ENV=development
```

`environment`와 `env_file`을 동시에 사용하면, `environment`에 직접 정의한 값이 `env_file`의 값을 오버라이드한다.

> **핵심 통찰**: Compose는 자동으로 프로젝트 루트의 `.env` 파일을 읽어 compose.yaml 내의 변수 치환(*Variable Substitution*)에 사용한다. 이것은 `env_file`과는 다른 기능이다. `.env` 파일의 값은 `${VARIABLE}` 문법으로 compose.yaml 안에서 참조할 수 있다.

```yaml
# compose.yaml에서 변수 치환 사용
services:
  db:
    image: postgres:${POSTGRES_VERSION:-16}-alpine
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
```

```bash
# .env (compose.yaml 변수 치환용)
POSTGRES_VERSION=16
DB_PASSWORD=mysecretpassword
```

#### command / entrypoint

컨테이너의 기본 명령어를 오버라이드한다.

```yaml
services:
  api:
    build: ./api
    # Dockerfile의 CMD를 오버라이드
    command: npm run dev

    # 또는 exec 형식 (권장)
    command: ["npm", "run", "dev"]

    # ENTRYPOINT 오버라이드
    entrypoint: ["node", "--inspect=0.0.0.0:9229"]
    command: ["dist/main.js"]
```

#### depends_on

서비스 간 시작 순서와 종속성을 정의한다. 이 옵션은 뒤에서 상세히 다룬다.

```yaml
services:
  web:
    depends_on:
      - api
  api:
    depends_on:
      - db
      - redis
```

#### restart

컨테이너 재시작 정책을 정의한다.

```yaml
services:
  api:
    restart: "no"              # 재시작 안 함 (기본값)
    restart: always            # 항상 재시작
    restart: on-failure        # 비정상 종료 시에만 재시작
    restart: on-failure:5      # 비정상 종료 시 최대 5회 재시작
    restart: unless-stopped    # 수동 중지 전까지 항상 재시작
```

> **실무 팁**: 개발 환경에서는 `restart: unless-stopped`가 편리하다. 시스템 재부팅 후에도 자동으로 컨테이너가 다시 시작되므로, 개발 DB나 Redis를 항상 띄워놓을 수 있다.

#### healthcheck

컨테이너의 건강 상태를 주기적으로 확인한다.

```yaml
services:
  api:
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--spider", "http://localhost:4000/health"]
      interval: 10s      # 검사 간격
      timeout: 3s        # 타임아웃
      retries: 3         # 실패 허용 횟수
      start_period: 15s  # 시작 후 대기 시간 (이 기간 내 실패는 무시)
      start_interval: 2s # start_period 동안의 검사 간격
```

`test` 필드의 형식:

| 형식 | 설명 | 예시 |
|------|------|------|
| `CMD` | 컨테이너 내에서 명령어 직접 실행 | `["CMD", "curl", "-f", "http://localhost:4000"]` |
| `CMD-SHELL` | 셸을 통해 실행 (파이프 등 사용 가능) | `["CMD-SHELL", "pg_isready -U user \|\| exit 1"]` |

### 2.2 networks 섹션

Compose는 기본적으로 프로젝트 이름을 기반으로 네트워크를 자동 생성한다. 하지만 사용자 정의 네트워크를 만들어 서비스를 분리할 수 있다.

```yaml
services:
  web:
    networks:
      - frontend

  api:
    networks:
      - frontend
      - backend

  db:
    networks:
      - backend

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
```

이 구성에서 `web`은 `api`에 접근할 수 있지만 `db`에는 접근할 수 없다. `api`는 `frontend`과 `backend` 모두에 속하므로 양쪽 서비스에 접근할 수 있다. 이것이 네트워크 분리(*Network Segmentation*)의 핵심이다.

> **핵심 통찰**: Compose가 자동 생성하는 기본 네트워크에서는 모든 서비스가 서로 통신할 수 있다. 보안이 중요한 환경에서는 위처럼 네트워크를 분리하여 불필요한 서비스 간 통신을 차단해야 한다.

### 2.3 volumes 섹션

최상위 `volumes`에 Named 볼륨을 선언하면, Compose가 관리하는 볼륨이 생성된다.

```yaml
services:
  db:
    volumes:
      - pg-data:/var/lib/postgresql/data
  redis:
    volumes:
      - redis-data:/data

volumes:
  pg-data:                    # 기본 설정
  redis-data:
    driver: local             # 드라이버 명시 (기본값은 local)
    driver_opts:
      type: none
      o: bind
      device: /data/redis     # 특정 호스트 경로에 바인딩
```

---

## 3. 완전한 실전 예제: Next.js + Express + PostgreSQL + Redis

실제 프로젝트에서 사용하는 수준의 compose.yaml을 단계별로 구축해본다.

### 3.1 프로젝트 디렉토리 구조

```
myapp/
├── compose.yaml
├── .env
├── web/                   # Next.js 프론트엔드
│   ├── Dockerfile
│   ├── package.json
│   └── src/
├── api/                   # Express API 서버
│   ├── Dockerfile
│   ├── package.json
│   └── src/
└── db/
    └── init.sql           # DB 초기화 스크립트
```

### 3.2 완성된 compose.yaml

```yaml
services:
  # ─── Next.js 프론트엔드 ─────────────────────────
  web:
    build:
      context: ./web
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    depends_on:
      api:
        condition: service_healthy
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:4000
      - API_URL=http://api:4000
    develop:
      watch:
        - action: sync
          path: ./web/src
          target: /app/src
        - action: rebuild
          path: ./web/package.json

  # ─── Express API 서버 ───────────────────────────
  api:
    build:
      context: ./api
      dockerfile: Dockerfile
    ports:
      - "4000:4000"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    environment:
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}
      - REDIS_URL=redis://redis:6379
      - NODE_ENV=development
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--spider", "http://localhost:4000/health"]
      interval: 10s
      timeout: 3s
      retries: 3
      start_period: 15s
    develop:
      watch:
        - action: sync
          path: ./api/src
          target: /app/src
        - action: rebuild
          path: ./api/package.json

  # ─── PostgreSQL 데이터베이스 ────────────────────
  db:
    image: postgres:16-alpine
    ports:
      - "5432:5432"
    volumes:
      - pg-data:/var/lib/postgresql/data
      - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 5s
      timeout: 3s
      retries: 5
      start_period: 10s

  # ─── Redis 캐시 ─────────────────────────────────
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes

volumes:
  pg-data:
  redis-data:
```

### 3.3 .env 파일

```bash
# .env — compose.yaml 변수 치환용
DB_USER=myapp_user
DB_PASSWORD=supersecretpassword
DB_NAME=myapp_db
```

### 3.4 각 서비스 상세 설명

**web (Next.js)**

- `NEXT_PUBLIC_API_URL`은 브라우저에서 API에 접근할 때 사용한다. 브라우저는 Docker 네트워크 밖에 있으므로 `localhost:4000`을 사용한다.
- `API_URL`은 Next.js의 서버 사이드(*Server-Side Rendering, API Routes*)에서 사용한다. 서버는 Docker 네트워크 안에 있으므로 서비스 이름 `api`를 호스트명으로 사용한다.
- `depends_on`에서 `condition: service_healthy`를 사용하여 API 서버가 완전히 준비된 후에 시작한다.

**api (Express)**

- `DATABASE_URL`에서 호스트명으로 `db`를 사용한다. Compose가 자동 생성하는 네트워크에서 서비스 이름이 DNS 호스트명이 된다.
- `healthcheck`가 `/health` 엔드포인트를 호출하여 서버 상태를 확인한다. Express 서버에 해당 라우트가 반드시 있어야 한다.

```typescript
// api/src/index.ts — 헬스체크 엔드포인트 예시
import express from "express";

const app = express();

app.get("/health", (req, res) => {
  res.status(200).json({ status: "ok" });
});

app.listen(4000, () => {
  console.log("API server running on port 4000");
});
```

**db (PostgreSQL)**

- `pg-data` Named 볼륨으로 데이터가 영속화된다. `docker compose down`으로 컨테이너를 삭제해도 데이터는 유지된다.
- `./db/init.sql`을 `/docker-entrypoint-initdb.d/`에 마운트하면, 볼륨이 비어있을 때(최초 실행 시) 자동으로 SQL이 실행된다.
- `healthcheck`에서 `pg_isready` 유틸리티로 PostgreSQL의 연결 수락 준비 상태를 확인한다.

**redis (Redis)**

- `--appendonly yes` 옵션으로 AOF(*Append Only File - Redis의 영속화 방식 중 하나*)를 활성화한다.
- `redis-data` 볼륨에 데이터가 영속화된다.

### 3.5 네트워크 자동 생성

위 compose.yaml에는 `networks` 섹션이 없다. 이 경우 Compose는 프로젝트 이름을 기반으로 `myapp_default`라는 기본 네트워크를 자동 생성하고, 모든 서비스를 이 네트워크에 연결한다. 서비스 이름이 곧 DNS 호스트명이 되므로, `api` 서비스에서 `db:5432`로 PostgreSQL에 접근할 수 있다.

```bash
# 생성된 네트워크 확인
docker network ls | grep myapp
# myapp_default   bridge   local
```

### 3.6 실행과 확인

```bash
# 전체 스택 시작 (백그라운드)
docker compose up -d

# 모든 서비스 상태 확인
docker compose ps

# 출력 예시:
# NAME        SERVICE   STATUS                PORTS
# myapp-web-1   web     running               0.0.0.0:3000->3000/tcp
# myapp-api-1   api     running (healthy)     0.0.0.0:4000->4000/tcp
# myapp-db-1    db      running (healthy)     0.0.0.0:5432->5432/tcp
# myapp-redis-1 redis   running               0.0.0.0:6379->6379/tcp

# API 로그 확인
docker compose logs api -f

# 전체 스택 종료 (볼륨은 유지)
docker compose down

# 전체 스택 종료 + 볼륨도 삭제
docker compose down -v
```

---

## 4. depends_on과 서비스 시작 순서

### 4.1 depends_on만으로는 부족하다

`depends_on`의 기본 동작은 단순히 **컨테이너 시작 순서**만 제어한다. 컨테이너가 시작되었다고 해서 그 안의 서비스가 준비되었다는 뜻은 아니다.

```yaml
# 이 설정은 위험하다
services:
  api:
    depends_on:
      - db        # db 컨테이너가 "시작"되면 api를 시작
```

PostgreSQL 컨테이너가 시작된 직후에는 아직 연결을 받아들이지 못하는 초기화 단계가 있다. 이 시점에 API 서버가 DB 연결을 시도하면 실패한다.

### 4.2 condition과 healthcheck 조합

이 문제의 해결책은 `condition`과 `healthcheck`를 조합하는 것이다.

```yaml
services:
  api:
    depends_on:
      db:
        condition: service_healthy    # db의 healthcheck가 통과해야 시작
      redis:
        condition: service_started    # redis 컨테이너가 시작되면 바로 시작

  db:
    image: postgres:16-alpine
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 5s
      timeout: 3s
      retries: 5
```

### 4.3 세 가지 condition 옵션

| condition | 의미 | 사용 시점 |
|-----------|------|-----------|
| `service_started` | 컨테이너가 시작되면 충족 (기본값) | 빠르게 준비되는 서비스 (Redis 등) |
| `service_healthy` | healthcheck가 `healthy` 상태가 되면 충족 | 초기화 시간이 필요한 서비스 (DB, API 등) |
| `service_completed_successfully` | 컨테이너가 정상 종료(exit 0)하면 충족 | 마이그레이션, 시드 스크립트 등 일회성 작업 |

### 4.4 마이그레이션 서비스 패턴

`service_completed_successfully`를 활용하면 DB 마이그레이션을 자동화할 수 있다.

```yaml
services:
  db:
    image: postgres:16-alpine
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 5s
      timeout: 3s
      retries: 5

  migrate:
    build: ./api
    command: npx prisma migrate deploy
    depends_on:
      db:
        condition: service_healthy
    # 마이그레이션 완료 후 컨테이너 종료

  api:
    build: ./api
    depends_on:
      migrate:
        condition: service_completed_successfully
    # 마이그레이션이 성공적으로 완료된 후에만 시작
```

이렇게 하면 `db 시작 → db 준비 완료 → migrate 실행 → migrate 정상 종료 → api 시작`이라는 안전한 시작 순서가 보장된다.

> **핵심 통찰**: `depends_on`은 "시작 순서"만 제어하는 것이 아니라, `condition`과 함께 사용하면 "준비 상태"까지 제어할 수 있다. 프로덕션 수준의 Compose 파일에서는 반드시 `healthcheck`와 `condition: service_healthy`를 조합해야 한다.

---

## 5. Docker Compose Watch 모드

### 5.1 Watch 모드란

도커 컴포즈 워치(*Docker Compose Watch - 파일 변경을 감지하여 자동으로 컨테이너에 반영하는 기능*)는 Docker Compose v2.22 이상에서 사용할 수 있다. 로컬 파일 시스템의 변경사항을 감지하여 컨테이너에 자동으로 동기화하거나, 필요 시 이미지를 다시 빌드한다.

```bash
# Watch 모드로 실행
docker compose watch

# 백그라운드에서 실행 중인 서비스에 Watch 적용
docker compose up -d
docker compose watch
```

### 5.2 Watch 설정

```yaml
services:
  web:
    build: ./web
    develop:
      watch:
        # 소스 코드 변경 → 컨테이너에 동기화
        - action: sync
          path: ./web/src
          target: /app/src
          ignore:
            - "**/*.test.ts"
            - "**/*.spec.ts"

        # package.json 변경 → 이미지 다시 빌드
        - action: rebuild
          path: ./web/package.json

        # 설정 파일 변경 → 동기화 후 컨테이너 재시작
        - action: sync+restart
          path: ./web/next.config.js
          target: /app/next.config.js
```

### 5.3 세 가지 Watch 액션

| 액션 | 동작 | 사용 시점 |
|------|------|-----------|
| `sync` | 변경된 파일을 컨테이너에 복사 | 소스 코드 변경 (HMR이 처리) |
| `rebuild` | 이미지를 다시 빌드하고 컨테이너 재생성 | 의존성 변경 (package.json 등) |
| `sync+restart` | 파일 동기화 후 컨테이너 재시작 | 설정 파일 변경 (프로세스 재시작 필요) |

### 5.4 바인드 마운트 vs Watch 모드

기존에는 개발 환경에서 소스 코드 변경을 반영하기 위해 바인드 마운트를 사용했다.

```yaml
# 기존 방식: 바인드 마운트
services:
  web:
    volumes:
      - ./web/src:/app/src           # 호스트 파일을 컨테이너에 직접 마운트
      - /app/node_modules            # node_modules는 컨테이너 것 유지
```

```yaml
# 새로운 방식: Watch 모드
services:
  web:
    develop:
      watch:
        - action: sync
          path: ./web/src
          target: /app/src
        - action: rebuild
          path: ./web/package.json
```

| 비교 항목 | 바인드 마운트 | Watch 모드 |
|-----------|--------------|------------|
| **파일 시스템** | 호스트 파일을 직접 마운트 | 변경 시 파일을 복사 |
| **macOS/Windows 성능** | 느림 (파일 시스템 번역 오버헤드) | 빠름 (복사 기반) |
| **node_modules 충돌** | 호스트/컨테이너 모듈 충돌 가능 | 충돌 없음 |
| **의존성 변경** | 수동으로 `docker compose up --build` 필요 | `rebuild` 액션으로 자동 처리 |
| **설정** | 간단 (`volumes`에 한 줄) | 약간 복잡 (`develop.watch` 설정) |

> **실무 팁**: macOS와 Windows에서 Docker를 사용할 때 바인드 마운트의 파일 시스템 성능이 느린 것은 잘 알려진 문제다. Watch 모드는 이 문제를 근본적으로 해결한다. Next.js처럼 HMR(*Hot Module Replacement*)을 지원하는 프레임워크와 특히 궁합이 좋다.

### 5.5 Watch와 .dockerignore

Watch 모드에서 `path`에 지정된 경로의 모든 파일이 감시 대상이 된다. 불필요한 파일을 제외하려면 `ignore` 옵션을 사용한다.

```yaml
develop:
  watch:
    - action: sync
      path: ./api/src
      target: /app/src
      ignore:
        - "node_modules/"
        - "**/*.test.ts"
        - ".git/"
```

---

## 6. 핵심 명령어

### 6.1 서비스 실행과 종료

```bash
# 모든 서비스 시작 (포그라운드, 로그 출력)
docker compose up

# 모든 서비스 시작 (백그라운드)
docker compose up -d

# 이미지를 다시 빌드하고 시작
docker compose up --build

# 특정 서비스만 시작
docker compose up -d api db

# 모든 서비스 종료 및 컨테이너 삭제
docker compose down

# 종료 + Named 볼륨도 삭제
docker compose down -v

# 종료 + 이미지도 삭제
docker compose down --rmi all
```

### 6.2 상태 확인과 로그

```bash
# 서비스 상태 확인
docker compose ps

# 모든 서비스 로그 출력
docker compose logs

# 특정 서비스 로그를 실시간으로 추적
docker compose logs -f api

# 최근 100줄만 출력 후 실시간 추적
docker compose logs -f --tail 100 api

# 타임스탬프 포함
docker compose logs -t api
```

### 6.3 서비스 접속과 실행

```bash
# 실행 중인 서비스에 셸 접속
docker compose exec api sh

# 서비스에서 일회성 명령어 실행
docker compose exec db psql -U user -d mydb

# 새 컨테이너를 생성하여 명령어 실행 (일회성)
docker compose run --rm api npm test

# run은 새 컨테이너를 만들고, exec은 기존 컨테이너에 접속한다
```

> **핵심 통찰**: `exec`과 `run`의 차이를 이해하는 것이 중요하다. `exec`은 이미 실행 중인 컨테이너에 추가 프로세스를 붙이고, `run`은 서비스 설정을 기반으로 새 컨테이너를 생성한다. 테스트 실행처럼 일회성 작업에는 `run --rm`이 적합하고, 디버깅을 위해 셸에 접속할 때는 `exec`이 적합하다.

### 6.4 빌드와 관리

```bash
# 이미지 빌드 (시작하지 않음)
docker compose build

# 특정 서비스만 빌드
docker compose build api

# 캐시 없이 빌드
docker compose build --no-cache

# 이미지 pull (빌드하지 않는 서비스)
docker compose pull

# 최종 compose 설정 확인 (변수 치환 결과 포함)
docker compose config

# 서비스 재시작
docker compose restart api

# 서비스 중지 (컨테이너 유지)
docker compose stop

# 중지된 서비스 시작
docker compose start
```

### 6.5 Watch 모드

```bash
# Watch 모드 시작
docker compose watch

# 백그라운드 서비스와 함께 Watch 실행
docker compose up -d && docker compose watch
```

---

## 자주 하는 실수

| 실수 | 문제점 | 올바른 방법 |
|------|--------|-------------|
| `depends_on`만으로 서비스 준비를 기대 | DB 컨테이너가 시작되었지만 아직 연결을 받지 못하는 상태에서 API가 시작됨 | `healthcheck`와 `condition: service_healthy`를 조합 |
| `docker compose down -v`를 무심코 실행 | Named 볼륨이 삭제되어 DB 데이터가 모두 날아감 | `down`만 사용하고, 볼륨 삭제가 필요할 때만 명시적으로 `-v` 추가 |
| `.env` 파일 경로 혼동 | `env_file`은 서비스 컨테이너에 변수를 주입하고, 프로젝트 루트 `.env`는 compose.yaml 변수 치환용 | 두 가지 용도를 구분하고 파일을 분리 |
| build 컨텍스트와 Dockerfile 경로 혼동 | `build: ./api`는 `./api/Dockerfile`을 찾지만, API 소스 전체가 빌드 컨텍스트가 됨 | `context`와 `dockerfile`을 명시적으로 분리 |
| 레거시 `docker-compose` (V1) 사용 | EOL된 도구이며, 최신 기능(Watch 등)을 사용할 수 없음 | `docker compose` (V2, 공백)로 마이그레이션 |
| 환경변수에 민감 정보를 직접 작성 | compose.yaml이 Git에 커밋되면 비밀번호가 노출됨 | `.env` 파일에 분리하고 `.gitignore`에 추가 |
| 모든 서비스에 포트를 노출 | DB, Redis 등 내부 서비스가 외부에 노출됨 | 외부 접근이 필요한 서비스(web, api)만 `ports` 설정. 내부 서비스는 Docker 네트워크로만 통신 |
| `docker compose up` 후 소스 변경이 안 반영됨 | 이전에 빌드된 이미지가 캐시되어 사용됨 | `docker compose up --build`로 재빌드하거나, Watch 모드 사용 |

---

## 명령어 레퍼런스

| 명령어 | 설명 | 예시 |
|--------|------|------|
| `docker compose up` | 서비스 시작 | `docker compose up -d --build` |
| `docker compose down` | 서비스 종료 및 삭제 | `docker compose down -v` |
| `docker compose ps` | 서비스 상태 확인 | `docker compose ps` |
| `docker compose logs` | 서비스 로그 출력 | `docker compose logs -f api` |
| `docker compose exec` | 실행 중 컨테이너에 명령어 실행 | `docker compose exec api sh` |
| `docker compose run` | 새 컨테이너로 일회성 명령어 실행 | `docker compose run --rm api npm test` |
| `docker compose build` | 이미지 빌드 | `docker compose build --no-cache` |
| `docker compose pull` | 이미지 다운로드 | `docker compose pull` |
| `docker compose restart` | 서비스 재시작 | `docker compose restart api` |
| `docker compose stop` | 서비스 중지 (컨테이너 유지) | `docker compose stop` |
| `docker compose start` | 중지된 서비스 시작 | `docker compose start` |
| `docker compose config` | 최종 설정 확인 | `docker compose config` |
| `docker compose watch` | Watch 모드 시작 | `docker compose watch` |

---

## 요약

- **Docker Compose**는 다중 컨테이너 애플리케이션을 하나의 YAML 파일로 선언적으로 정의하고 관리하는 도구다.
- 현재 표준은 **V2** (`docker compose`, Go 기반 CLI 플러그인)이며, 파일명은 `compose.yaml`을 사용한다.
- compose.yaml의 핵심 구조는 `services`, `networks`, `volumes` 세 가지다.
- **서비스(services)**에서는 `image`/`build`, `ports`, `volumes`, `environment`, `depends_on`, `healthcheck` 등을 정의한다.
- `depends_on`만으로는 서비스의 **준비 상태**를 보장할 수 없다. 반드시 `healthcheck`와 `condition: service_healthy`를 조합해야 한다.
- `condition`의 세 가지 옵션: `service_started` (시작됨), `service_healthy` (건강함), `service_completed_successfully` (정상 종료됨).
- **Docker Compose Watch** (v2.22+)는 파일 변경을 감지하여 `sync`, `rebuild`, `sync+restart` 세 가지 액션으로 자동 반영한다.
- Watch 모드는 macOS/Windows에서 바인드 마운트의 성능 문제를 해결하고, 의존성 변경 시 자동 리빌드를 지원한다.
- `.env` 파일은 compose.yaml 내 변수 치환용과 컨테이너 환경변수 주입용(`env_file`)으로 구분하여 사용한다.
- 핵심 명령어: `up -d --build`, `down`, `ps`, `logs -f`, `exec`, `run --rm`, `config`, `watch`.

---

## 다른 챕터와의 관계

- **Ch 5 (볼륨)**: compose.yaml의 `volumes` 섹션에서 Named 볼륨과 바인드 마운트를 선언적으로 정의한다. Ch 5에서 배운 볼륨 개념이 Compose에서 그대로 적용된다.
- **Ch 6 (네트워크)**: Compose는 프로젝트별로 기본 브리지 네트워크를 자동 생성한다. Ch 6에서 배운 사용자 정의 네트워크와 DNS 기반 서비스 디스커버리가 Compose에서 자동으로 구성된다.
- **Ch 8 (Compose 고급 패턴)**: 이 챕터의 기본 문법을 확장하여 프로파일, 다중 환경 오버라이드(`compose.override.yaml`), 확장 필드(`x-`), `include` 등 고급 기능을 다룬다.
- **Ch 12 (Node.js 서비스 구성)**: 이 챕터에서 다룬 Next.js + Express 예제를 더 깊이 확장하여, Prisma 마이그레이션, 멀티 스테이지 빌드, 프로덕션 Compose 구성 등을 실전 수준으로 구성한다.
