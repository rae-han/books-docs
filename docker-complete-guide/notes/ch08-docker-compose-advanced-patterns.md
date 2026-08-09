# Chapter 8: Compose 고급 패턴: Docker Compose Advanced

## 핵심 질문

개발/스테이징/프로덕션 환경을 하나의 Compose 설정으로 어떻게 관리하는가? 다중 파일 오버라이드, extends, profiles는 어떤 상황에서 활용하는가?

---

## 1. 다중 파일 오버라이드 (Multiple Compose Files)

Ch 7에서 다룬 단일 `compose.yaml`은 소규모 프로젝트에서는 충분하지만, 환경별로 설정이 달라지는 실제 프로젝트에서는 금방 한계에 부딪힌다. 개발 환경에서는 소스 코드를 바인드 마운트하고 디버그 포트를 열어야 하고, 프로덕션에서는 빌드된 이미지를 사용하고 리소스 제한을 걸어야 한다. 이 모든 분기를 하나의 파일에 넣으면 주석으로 뒤덮인 관리 불가능한 파일이 된다.

Docker Compose는 **다중 파일 오버라이드**(*Multiple File Override - 여러 Compose 파일을 순서대로 병합하여 최종 설정을 만드는 메커니즘*)를 지원한다. 기본 설정 파일 위에 환경별 오버라이드 파일을 겹겹이 쌓는 방식이다.

### 1.1 자동 병합: compose.yaml + compose.override.yaml

Docker Compose는 별도 옵션 없이 `docker compose up`을 실행할 때, 현재 디렉토리에서 다음 두 파일을 **자동으로** 탐색하여 병합한다:

1. `compose.yaml` (기본 설정)
2. `compose.override.yaml` (오버라이드)

`compose.override.yaml`이 존재하면 자동으로 `compose.yaml` 위에 병합된다. 별도의 `-f` 옵션이 필요 없다.

```yaml
# compose.yaml — 기본 설정
services:
  app:
    image: myapp:latest
    ports:
      - "3000:3000"
    environment:
      NODE_ENV: production
```

```yaml
# compose.override.yaml — 개발용 오버라이드 (자동 병합)
services:
  app:
    build: .
    volumes:
      - .:/app
      - /app/node_modules
    environment:
      NODE_ENV: development
      DEBUG: "true"
    ports:
      - "9229:9229"  # Node.js 디버거 포트 추가
```

`docker compose up`을 실행하면 두 파일이 병합되어 다음과 같은 **최종 설정**이 생성된다:

```yaml
# 병합 결과 (docker compose config로 확인 가능)
services:
  app:
    build: .              # override가 image를 대체하지 않음 — build와 image가 공존
    image: myapp:latest   # build 후 이 이름으로 태깅
    volumes:
      - .:/app
      - /app/node_modules
    environment:
      NODE_ENV: development   # override가 동일 키를 덮어씀
      DEBUG: "true"           # override에서 추가된 키
    ports:
      - "3000:3000"   # 기본 설정의 포트 유지
      - "9229:9229"   # override에서 추가된 포트
```

> **핵심 통찰**: `compose.override.yaml`은 `.gitignore`에 추가하고 개발자마다 로컬 설정을 자유롭게 커스터마이즈하게 하는 패턴이 일반적이다. 대신 `compose.override.yaml.example`을 저장소에 포함하여 참고하게 한다.

### 1.2 명시적 다중 파일 지정: -f 옵션

자동 병합 대신 명시적으로 파일을 지정할 수 있다. `-f` 옵션을 여러 번 사용하면 **지정한 순서대로** 병합된다.

```bash
# 기본 + 프로덕션 오버라이드
docker compose -f compose.yaml -f compose.prod.yaml up -d

# 기본 + 개발 오버라이드
docker compose -f compose.yaml -f compose.dev.yaml up -d

# 기본 + 개발 + 디버그 추가 오버라이드 (3개 파일도 가능)
docker compose -f compose.yaml -f compose.dev.yaml -f compose.debug.yaml up -d
```

`-f`를 명시적으로 사용하면 `compose.override.yaml`의 **자동 병합은 비활성화**된다. 오직 `-f`로 지정한 파일들만 사용된다.

### 1.3 병합 규칙 상세

병합 규칙은 키의 타입에 따라 다르다. 이 규칙을 정확히 이해하지 못하면 예상치 못한 설정이 생성된다.

| 키 타입 | 병합 방식 | 예시 |
|---------|----------|------|
| **단일 값** (스칼라) | 나중 파일이 **덮어씀** | `image`, `command`, `restart` |
| **매핑** (key-value) | 키별로 **병합** (동일 키는 덮어씀, 새 키는 추가) | `environment`, `labels`, `build.args` |
| **시퀀스** (리스트) | **합쳐짐** (기존 + 추가) | `ports`, `volumes`, `expose`, `dns` |
| **build** | 하위 키별로 병합 | `build.context`, `build.target` 등 개별 적용 |

구체적인 예를 들어 보자:

```yaml
# compose.yaml
services:
  app:
    image: myapp:1.0          # 단일 값
    command: node server.js    # 단일 값
    environment:               # 매핑
      NODE_ENV: production
      PORT: "3000"
    ports:                     # 시퀀스
      - "3000:3000"
    labels:                    # 매핑
      app.version: "1.0"
```

```yaml
# compose.prod.yaml
services:
  app:
    image: myapp:2.0              # 단일 값 → 덮어씀
    environment:                   # 매핑 → 키별 병합
      NODE_ENV: production         # 동일 키 → 유지 (같은 값)
      LOG_LEVEL: warn              # 새 키 → 추가
    ports:                         # 시퀀스 → 합쳐짐
      - "8080:3000"
    labels:                        # 매핑 → 키별 병합
      app.version: "2.0"          # 동일 키 → 덮어씀
      app.env: production          # 새 키 → 추가
```

```yaml
# 병합 결과
services:
  app:
    image: myapp:2.0               # 덮어써짐
    command: node server.js        # 기본 유지 (override에 없으므로)
    environment:
      NODE_ENV: production         # 유지
      PORT: "3000"                 # 유지
      LOG_LEVEL: warn              # 추가됨
    ports:
      - "3000:3000"                # 유지
      - "8080:3000"                # 추가됨 (주의: 포트 충돌 가능!)
    labels:
      app.version: "2.0"          # 덮어써짐
      app.env: production          # 추가됨
```

> **핵심 통찰**: `ports`는 시퀀스이므로 **합쳐진다**. 위 예시에서 호스트 포트 3000과 8080이 모두 컨테이너의 3000번 포트로 매핑된다. 오버라이드 파일에서 포트를 "교체"하고 싶다면, 기본 파일에서 해당 포트를 제거하거나 기본 파일에 포트를 아예 넣지 않는 전략이 필요하다.

### 1.4 최종 병합 결과 확인: docker compose config

실제로 어떤 설정이 적용되는지 확인하려면 `config` 명령어를 사용한다.

```bash
# 자동 병합 결과 확인
docker compose config

# 특정 파일 조합의 병합 결과 확인
docker compose -f compose.yaml -f compose.prod.yaml config

# 특정 서비스만 확인
docker compose -f compose.yaml -f compose.prod.yaml config --services

# YAML 대신 JSON으로 출력
docker compose -f compose.yaml -f compose.prod.yaml config --format json
```

`config` 명령어는 변수 치환, 파일 병합, 경로 해석이 모두 적용된 **최종 상태**를 보여준다. 복잡한 다중 파일 설정에서 디버깅의 첫 번째 도구다.

---

## 2. extends를 활용한 서비스 재사용

`extends`(*Extends - 다른 서비스의 설정을 상속받아 재사용하는 Compose 기능*)는 공통 설정을 한 곳에 정의하고 여러 서비스에서 재사용하는 메커니즘이다. 다중 파일 오버라이드가 "같은 서비스의 환경별 변형"이라면, `extends`는 "서로 다른 서비스 간의 공통 설정 공유"에 초점을 맞춘다.

### 2.1 같은 파일 내에서 extends

```yaml
# compose.yaml
services:
  base-node:
    build:
      context: .
      target: base
    environment:
      NODE_ENV: production
      TZ: Asia/Seoul
    restart: unless-stopped
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

  api:
    extends:
      service: base-node
    build:
      context: ./apps/api
      target: runner
    ports:
      - "4000:4000"
    environment:
      PORT: "4000"
      DATABASE_URL: postgresql://user:pass@db:5432/mydb

  worker:
    extends:
      service: base-node
    build:
      context: ./apps/worker
      target: runner
    environment:
      QUEUE_URL: redis://redis:6379
```

`api`와 `worker`는 `base-node`의 `restart`, `logging`, `environment`(TZ, NODE_ENV) 등을 상속받고, 각자 고유한 설정을 추가한다.

### 2.2 외부 파일에서 extends

공통 설정을 별도 파일로 분리할 수도 있다.

```yaml
# common-services.yaml — 공통 서비스 정의
services:
  node-base:
    build:
      context: .
    environment:
      NODE_ENV: production
      TZ: Asia/Seoul
    restart: unless-stopped
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
    deploy:
      resources:
        limits:
          memory: 512M
```

```yaml
# compose.yaml
services:
  app:
    extends:
      file: common-services.yaml
      service: node-base
    build:
      context: ./app
      target: runner
    ports:
      - "3000:3000"
    environment:
      PORT: "3000"

  api:
    extends:
      file: common-services.yaml
      service: node-base
    build:
      context: ./api
      target: runner
    ports:
      - "4000:4000"
    environment:
      PORT: "4000"
```

### 2.3 extends의 제한사항

`extends`에는 중요한 제한사항이 있다. 다음 키들은 상속되지 않는다:

| 상속 불가 키 | 이유 |
|-------------|------|
| `networks` | 네트워크는 프로젝트 수준 리소스이므로 서비스 간 자동 상속이 위험 |
| `volumes` (최상위 정의 참조) | 볼륨 이름 충돌 방지 |
| `depends_on` | 의존성 그래프가 프로젝트마다 다름 |
| `links` | 레거시 기능, 네트워크로 대체됨 |

따라서 `extends`를 사용하는 서비스에서는 `networks`, `depends_on` 등을 반드시 직접 지정해야 한다.

```yaml
services:
  api:
    extends:
      file: common-services.yaml
      service: node-base
    # extends에서 상속되지 않으므로 직접 지정
    networks:
      - backend
    depends_on:
      db:
        condition: service_healthy
```

### 2.4 extends vs YAML 앵커

`extends`와 YAML 앵커(섹션 7에서 다룸)는 비슷한 목적을 가지지만 차이가 있다:

| 비교 | extends | YAML 앵커 |
|------|---------|-----------|
| **파일 간 참조** | 가능 (외부 파일 지원) | 불가 (같은 파일 내에서만) |
| **병합 방식** | Compose 수준 스마트 병합 | YAML 수준 단순 병합 |
| **가독성** | 명시적 (`extends:` 키워드) | 암시적 (`<<: *alias`) |
| **지원 범위** | Compose 전용 | 모든 YAML 파서 |

일반적으로 **같은 파일 내 중복 제거**에는 YAML 앵커를, **파일 간 서비스 재사용**에는 `extends`를 사용한다.

---

## 3. 개발/프로덕션 환경 분리 전략

### 3.1 권장 파일 구조

실무에서 가장 널리 사용되는 파일 구조다:

```
project/
├── compose.yaml          # 공통 설정 (서비스 정의, 네트워크, 볼륨)
├── compose.dev.yaml      # 개발 오버라이드
├── compose.prod.yaml     # 프로덕션 오버라이드
├── compose.test.yaml     # 테스트 오버라이드 (선택)
├── .env                  # 공통 환경변수
├── .env.dev              # 개발 환경변수
├── .env.prod             # 프로덕션 환경변수
├── Makefile              # 명령어 단축
├── Dockerfile            # 멀티스테이지 빌드
└── src/
```

### 3.2 공통 설정 (compose.yaml)

공통 설정에는 모든 환경에서 **변하지 않는** 요소만 넣는다.

```yaml
# compose.yaml — 공통 설정
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    networks:
      - backend

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    volumes:
      - pg-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 5s
      timeout: 3s
      retries: 5
    networks:
      - backend

  redis:
    image: redis:7-alpine
    volumes:
      - redis-data:/data
    networks:
      - backend

volumes:
  pg-data:
  redis-data:

networks:
  backend:
```

공통 설정에서 `ports`를 의도적으로 **빠뜨린** 것에 주목하라. 포트 매핑은 환경마다 다르므로 오버라이드 파일에서 지정한다.

### 3.3 개발 오버라이드 (compose.dev.yaml)

```yaml
# compose.dev.yaml — 개발 환경
services:
  app:
    build:
      target: dev                    # 멀티스테이지의 dev 스테이지
    ports:
      - "3000:3000"                  # 앱 포트
      - "9229:9229"                  # Node.js 디버거
    volumes:
      - .:/app                       # 소스 코드 바인드 마운트
      - /app/node_modules            # node_modules는 컨테이너 것 사용
      - /app/.next                   # .next 캐시도 컨테이너 것 사용
    environment:
      NODE_ENV: development
      LOG_LEVEL: debug
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}
      REDIS_URL: redis://redis:6379
    develop:
      watch:                         # docker compose watch (Ch 7 참고)
        - action: sync
          path: ./src
          target: /app/src
        - action: rebuild
          path: ./package.json

  db:
    ports:
      - "5432:5432"                  # 호스트에서 직접 DB 접근 가능

  redis:
    ports:
      - "6379:6379"                  # 호스트에서 직접 Redis 접근 가능
```

### 3.4 프로덕션 오버라이드 (compose.prod.yaml)

```yaml
# compose.prod.yaml — 프로덕션 환경
services:
  app:
    build:
      target: runner                 # 멀티스테이지의 최종 runner 스테이지
    image: ghcr.io/myorg/myapp:${APP_VERSION:-latest}
    ports:
      - "3000:3000"                  # 앱 포트만 노출
    environment:
      NODE_ENV: production
      LOG_LEVEL: warn
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}
      REDIS_URL: redis://redis:6379
    restart: always
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 512M
        reservations:
          cpus: "0.5"
          memory: 256M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  db:
    restart: always
    deploy:
      resources:
        limits:
          memory: 1G
    # 포트를 노출하지 않음 — 외부 접근 차단

  redis:
    restart: always
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
    deploy:
      resources:
        limits:
          memory: 512M
    # 포트를 노출하지 않음
```

### 3.5 Makefile로 명령어 단축

매번 `-f` 옵션을 타이핑하는 것은 번거롭다. Makefile로 단축한다.

```makefile
# Makefile
COMPOSE_DEV = docker compose -f compose.yaml -f compose.dev.yaml
COMPOSE_PROD = docker compose -f compose.yaml -f compose.prod.yaml

.PHONY: dev dev-down prod prod-down logs config-dev config-prod

# 개발 환경
dev:
	$(COMPOSE_DEV) --env-file .env.dev up -d
	$(COMPOSE_DEV) --env-file .env.dev watch

dev-down:
	$(COMPOSE_DEV) --env-file .env.dev down

dev-logs:
	$(COMPOSE_DEV) --env-file .env.dev logs -f app

# 프로덕션 환경
prod:
	$(COMPOSE_PROD) --env-file .env.prod up -d --build

prod-down:
	$(COMPOSE_PROD) --env-file .env.prod down

# 설정 확인
config-dev:
	$(COMPOSE_DEV) --env-file .env.dev config

config-prod:
	$(COMPOSE_PROD) --env-file .env.prod config
```

```bash
# 사용법
make dev          # 개발 환경 시작 + watch 모드
make dev-down     # 개발 환경 종료
make prod         # 프로덕션 빌드 + 시작
make config-dev   # 개발 환경 최종 설정 확인
```

혹은 `package.json`의 `scripts`를 사용할 수도 있다:

```json
{
  "scripts": {
    "docker:dev": "docker compose -f compose.yaml -f compose.dev.yaml --env-file .env.dev up -d && docker compose -f compose.yaml -f compose.dev.yaml watch",
    "docker:dev:down": "docker compose -f compose.yaml -f compose.dev.yaml down",
    "docker:prod": "docker compose -f compose.yaml -f compose.prod.yaml --env-file .env.prod up -d --build"
  }
}
```

---

## 4. Profiles

프로파일(*Profile - 서비스에 태그를 붙여 조건부로 활성화/비활성화하는 메커니즘*)은 특정 서비스를 **선택적으로** 실행할 때 사용한다. 디버깅 도구, 관리 도구, 일회성 마이그레이션 등 항상 필요하지 않은 서비스에 적합하다.

### 4.1 기본 사용법

```yaml
# compose.yaml
services:
  app:
    build: .
    ports:
      - "3000:3000"
    # profiles가 없음 → 항상 실행됨

  db:
    image: postgres:16-alpine
    # profiles가 없음 → 항상 실행됨

  pgadmin:
    image: dpage/pgadmin4:latest
    ports:
      - "5050:80"
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@local.dev
      PGADMIN_DEFAULT_PASSWORD: admin
    profiles:
      - debug                    # debug 프로파일에서만 실행

  redis-commander:
    image: rediscommander/redis-commander:latest
    ports:
      - "8081:8081"
    environment:
      REDIS_HOSTS: local:redis:6379
    profiles:
      - debug                    # debug 프로파일에서만 실행

  mailhog:
    image: mailhog/mailhog:latest
    ports:
      - "1025:1025"
      - "8025:8025"
    profiles:
      - debug                    # debug 프로파일에서만 실행

  migrate:
    build: .
    command: npx prisma migrate deploy
    depends_on:
      db:
        condition: service_healthy
    profiles:
      - setup                    # setup 프로파일에서만 실행

  seed:
    build: .
    command: npx prisma db seed
    depends_on:
      db:
        condition: service_healthy
    profiles:
      - setup                    # setup 프로파일에서만 실행
```

### 4.2 프로파일 활성화

```bash
# 기본 서비스만 실행 (app, db만)
docker compose up -d

# 기본 + debug 프로파일 (app, db, pgadmin, redis-commander, mailhog)
docker compose --profile debug up -d

# 기본 + setup 프로파일 (app, db, migrate, seed)
docker compose --profile setup up -d

# 여러 프로파일 동시 활성화
docker compose --profile debug --profile setup up -d
```

환경변수로도 프로파일을 활성화할 수 있다:

```bash
# COMPOSE_PROFILES 환경변수
COMPOSE_PROFILES=debug docker compose up -d

# 여러 프로파일을 쉼표로 구분
COMPOSE_PROFILES=debug,setup docker compose up -d
```

### 4.3 프로파일과 depends_on의 상호작용

프로파일 서비스가 프로파일이 없는 서비스에 `depends_on`으로 의존하는 것은 문제없다. 하지만 **반대 방향**은 주의가 필요하다.

```yaml
services:
  app:
    build: .
    depends_on:
      - db
      - mailhog      # mailhog는 debug 프로파일!

  mailhog:
    image: mailhog/mailhog
    profiles:
      - debug
```

위 설정에서 `docker compose up`(프로파일 없이)을 실행하면 `app`이 `mailhog`에 의존하므로 **mailhog도 자동으로 시작**된다. 프로파일이 있더라도 다른 서비스가 직접 의존하면 암묵적으로 활성화된다.

이를 방지하려면 프로파일 서비스에 대한 의존성을 조건부로 만드는 것이 좋다:

```yaml
services:
  app:
    build: .
    depends_on:
      - db
    # mailhog에 대한 depends_on은 제거
    # 앱 코드에서 SMTP 서버 연결 실패를 graceful하게 처리
```

### 4.4 실전 프로파일 패턴

| 프로파일 이름 | 포함 서비스 | 용도 |
|-------------|-----------|------|
| `debug` | pgadmin, redis-commander, mailhog | DB/캐시/메일 관리 도구 |
| `setup` | migrate, seed | 초기 설정, 마이그레이션 |
| `monitoring` | prometheus, grafana, node-exporter | 모니터링 스택 |
| `test` | test-runner, test-db | 테스트 전용 서비스 |

---

## 5. 환경변수 관리 심화

Ch 7에서 기본적인 환경변수 사용법을 다뤘다. 이 섹션에서는 다중 환경에서의 환경변수 관리를 심화한다.

### 5.1 .env 파일 자동 로드

Docker Compose는 프로젝트 디렉토리의 `.env` 파일을 **자동으로** 로드한다. 이 파일의 변수는 **Compose 파일 내의 변수 치환**(`${VAR}`)에 사용된다.

```bash
# .env
DB_USER=myuser
DB_PASSWORD=secret123
DB_NAME=mydb
APP_VERSION=1.2.3
```

```yaml
# compose.yaml — .env의 변수가 치환됨
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${DB_USER}         # myuser로 치환
      POSTGRES_PASSWORD: ${DB_PASSWORD} # secret123으로 치환
      POSTGRES_DB: ${DB_NAME}           # mydb로 치환
```

### 5.2 env_file 지시어

`env_file`은 컨테이너 내부에 환경변수를 주입하는 용도다. `.env` 자동 로드와는 목적이 다르다.

```yaml
services:
  app:
    build: .
    env_file:
      - .env.common         # 공통 환경변수
      - .env.${APP_ENV}     # 환경별 환경변수 (변수 치환 지원)
    environment:
      NODE_ENV: production   # env_file보다 우선
```

```bash
# .env.common
TZ=Asia/Seoul
LANG=ko_KR.UTF-8

# .env.dev
LOG_LEVEL=debug
ENABLE_SWAGGER=true

# .env.prod
LOG_LEVEL=warn
ENABLE_SWAGGER=false
```

### 5.3 환경변수 우선순위

Docker Compose에서 환경변수의 우선순위는 다음과 같다 (높은 것이 낮은 것을 덮어씀):

| 우선순위 | 소스 | 설명 |
|---------|------|------|
| 1 (최고) | `docker compose run -e VAR=val` | 명령행에서 직접 지정 |
| 2 | 호스트 셸 환경변수 | `export VAR=val` 후 실행 |
| 3 | `environment:` 키 | compose.yaml에 직접 작성 |
| 4 | `--env-file` 옵션 | CLI에서 지정한 env 파일 |
| 5 | `env_file:` 키 | compose.yaml에서 지정한 env 파일 |
| 6 | Dockerfile `ENV` | 이미지 빌드 시 설정된 기본값 |

```bash
# 셸 환경변수가 .env 파일보다 우선한다
export DB_PASSWORD=override_from_shell
docker compose up -d
# → DB_PASSWORD는 "override_from_shell"이 됨
```

### 5.4 변수 치환 문법

Compose 파일 내에서 사용할 수 있는 변수 치환(*Variable Substitution - `${VAR}` 형태로 Compose 파일에서 외부 변수를 참조하는 문법*) 옵션들이다:

```yaml
services:
  app:
    image: myapp:${APP_VERSION:-latest}
    # ${VAR:-default}  → VAR이 비어 있거나 미설정이면 "default" 사용
    # ${VAR-default}   → VAR이 미설정이면 "default" 사용 (빈 문자열은 그대로)

    environment:
      SECRET_KEY: ${SECRET_KEY:?SECRET_KEY must be set}
      # ${VAR:?error}  → VAR이 비어 있거나 미설정이면 에러 메시지 출력 후 중단
      # ${VAR?error}   → VAR이 미설정이면 에러 출력 (빈 문자열은 허용)

      OPTIONAL_VAR: ${OPTIONAL_VAR:+set_value}
      # ${VAR:+value}  → VAR이 설정되어 있으면 "value" 사용, 아니면 빈 문자열
```

실전에서 가장 많이 쓰이는 패턴:

```yaml
services:
  app:
    image: myapp:${APP_VERSION:-latest}          # 기본값 패턴
    restart: ${RESTART_POLICY:-unless-stopped}    # 정책 기본값

  db:
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD:?DB_PASSWORD is required}  # 필수값 검증
```

### 5.5 Compose 변수 치환 vs 컨테이너 환경변수

이 두 개념은 자주 혼동된다.

**Compose 변수 치환**은 Compose가 YAML 파일을 파싱할 때 `${VAR}`를 실제 값으로 바꾸는 과정이다. `.env` 파일이나 셸 환경변수를 소스로 사용한다.

**컨테이너 환경변수**는 컨테이너 내부에서 `process.env.VAR`로 접근할 수 있는 변수다. `environment:` 키나 `env_file:` 키로 설정한다.

```yaml
services:
  app:
    image: myapp:${APP_VERSION}    # ① Compose 변수 치환 (파싱 시점)
    environment:
      DB_HOST: db                  # ② 컨테이너 환경변수 (런타임)
      DB_PORT: ${DB_PORT:-5432}    # ①과 ②가 동시에 적용
      # Compose가 먼저 ${DB_PORT:-5432}를 치환 → 컨테이너에 전달
```

---

## 6. 빌드 설정 심화

### 6.1 build 키의 전체 옵션

```yaml
services:
  app:
    build:
      context: .                           # 빌드 컨텍스트 경로
      dockerfile: Dockerfile               # Dockerfile 경로 (context 기준 상대)
      target: runner                       # 멀티스테이지 빌드에서 특정 스테이지 지정
      args:                                # 빌드 인자 (ARG)
        NODE_VERSION: "20"
        NEXT_PUBLIC_API_URL: ${API_URL}
      cache_from:                          # 캐시 소스 지정
        - type=registry,ref=ghcr.io/myorg/myapp:cache
      labels:                              # 이미지에 라벨 추가
        app.build.timestamp: ${BUILD_TIME}
      platforms:                           # 멀티 플랫폼 빌드
        - linux/amd64
        - linux/arm64
    image: ghcr.io/myorg/myapp:${APP_VERSION:-latest}
    # build + image를 함께 쓰면 빌드 후 이 이름으로 태깅
```

### 6.2 멀티스테이지 빌드에서 target 활용

Ch 4에서 다룬 멀티스테이지 빌드와 Compose의 `target`을 결합하면 환경별로 다른 스테이지를 사용할 수 있다.

```dockerfile
# Dockerfile — 멀티스테이지
FROM node:20-alpine AS base
WORKDIR /app
COPY package*.json ./
RUN npm ci

# --- 개발 스테이지 ---
FROM base AS dev
RUN npm install -g nodemon
COPY . .
CMD ["nodemon", "--inspect=0.0.0.0:9229", "src/server.ts"]

# --- 빌드 스테이지 ---
FROM base AS builder
COPY . .
RUN npm run build

# --- 프로덕션 스테이지 ---
FROM node:20-alpine AS runner
WORKDIR /app
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
USER nextjs
EXPOSE 3000
CMD ["node", "server.js"]
```

```yaml
# compose.dev.yaml — dev 스테이지 사용
services:
  app:
    build:
      target: dev
```

```yaml
# compose.prod.yaml — runner 스테이지 사용
services:
  app:
    build:
      target: runner
```

이렇게 하면 **하나의 Dockerfile**로 개발과 프로덕션 이미지를 모두 빌드할 수 있다. 개발 이미지에는 `nodemon`과 소스 코드가 포함되고, 프로덕션 이미지에는 빌드된 결과물만 포함된다.

### 6.3 빌드 인자 (ARG)와 환경변수 연동

```yaml
services:
  app:
    build:
      context: .
      args:
        # .env 파일이나 셸 환경변수에서 값을 가져옴
        NEXT_PUBLIC_API_URL: ${NEXT_PUBLIC_API_URL}
        NEXT_PUBLIC_SITE_URL: ${NEXT_PUBLIC_SITE_URL}
        # 빌드 시점에 NEXT_PUBLIC_* 환경변수를 주입
        # Next.js는 빌드 시 NEXT_PUBLIC_* 변수를 번들에 포함시킴
```

```dockerfile
# Dockerfile
ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_SITE_URL

FROM node:20-alpine AS builder
WORKDIR /app
COPY . .
# ARG → ENV 변환 (RUN 시 접근 가능하도록)
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_SITE_URL=$NEXT_PUBLIC_SITE_URL
RUN npm run build
```

> **핵심 통찰**: Next.js의 `NEXT_PUBLIC_*` 변수는 **빌드 시점**에 클라이언트 번들에 인라인된다. 따라서 런타임 `environment:`가 아니라 빌드 인자 `args:`로 전달해야 한다. 이것은 Docker + Next.js 조합에서 가장 흔한 실수 중 하나다.

---

## 7. YAML 앵커와 머지 키

YAML 앵커(*YAML Anchor - `&이름`으로 값을 정의하고 `*이름`으로 재사용하는 YAML 표준 기능*)와 머지 키(*Merge Key - `<<:`로 매핑을 병합하는 YAML 기능*)는 Docker Compose 전용 기능이 아니라 YAML 표준이다. 하지만 Compose 파일에서 중복을 줄이는 데 매우 유용하다.

### 7.1 기본 문법

```yaml
# 앵커 정의: &이름
# 앵커 참조: *이름
# 머지 키: <<: *이름 (매핑을 현재 매핑에 병합)

x-common-env: &common-env
  TZ: Asia/Seoul
  LANG: ko_KR.UTF-8
  NODE_ENV: production

x-logging: &default-logging
  driver: json-file
  options:
    max-size: "10m"
    max-file: "3"

x-healthcheck: &default-healthcheck
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 30s

services:
  app:
    build: .
    environment:
      <<: *common-env            # 앵커 병합
      PORT: "3000"               # 추가 환경변수
      DATABASE_URL: postgresql://user:pass@db:5432/mydb
    logging: *default-logging    # 앵커 참조 (전체 교체)
    healthcheck:
      <<: *default-healthcheck
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]

  worker:
    build: .
    command: node worker.js
    environment:
      <<: *common-env            # 같은 앵커 재사용
      QUEUE_URL: redis://redis:6379
    logging: *default-logging
    healthcheck:
      <<: *default-healthcheck
      test: ["CMD", "node", "healthcheck.js"]
```

### 7.2 x- 접두사 확장 필드

`x-`로 시작하는 최상위 키는 Docker Compose가 **무시**하는 확장 필드(*Extension Field*)다. YAML 앵커를 정의할 장소로 활용한다.

```yaml
# x- 접두사 → Compose가 무시하므로 자유롭게 앵커 정의 가능
x-common-variables: &common-variables
  DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}
  REDIS_URL: redis://redis:6379
  TZ: Asia/Seoul

x-restart-policy: &restart-policy
  restart: unless-stopped

x-resource-limits: &resource-limits
  deploy:
    resources:
      limits:
        cpus: "0.5"
        memory: 256M

services:
  app:
    <<: *restart-policy
    <<: *resource-limits          # 주의: YAML에서 같은 키를 두 번 쓸 수 없음!
    build: .
    environment:
      <<: *common-variables
      PORT: "3000"
```

위 예제에서 `<<:`를 두 번 사용한 것은 **YAML 표준 위반**이다. 대부분의 YAML 파서에서 마지막 것만 적용되거나 에러가 발생한다. 여러 앵커를 병합하려면 다음 패턴을 사용한다:

```yaml
x-base-service: &base-service
  restart: unless-stopped
  logging:
    driver: json-file
    options:
      max-size: "10m"
      max-file: "3"
  deploy:
    resources:
      limits:
        cpus: "0.5"
        memory: 256M

services:
  app:
    <<: *base-service            # 하나의 앵커에 모든 공통 설정을 모음
    build: .
    environment:
      <<: *common-variables
      PORT: "3000"
```

### 7.3 앵커의 한계

YAML 앵커는 같은 파일 내에서만 동작한다. 다중 파일 오버라이드 구성에서 `compose.yaml`에 정의한 앵커를 `compose.prod.yaml`에서 `*참조`할 수 없다. 파일 간 설정 재사용에는 `extends`를 사용해야 한다.

또한 앵커 병합은 **얕은 병합**(*Shallow Merge*)이다. 중첩된 매핑은 재귀적으로 병합되지 않고 통째로 교체된다.

```yaml
x-base: &base
  environment:
    A: "1"
    B: "2"

services:
  app:
    <<: *base
    environment:       # environment 전체가 교체됨!
      C: "3"
    # 결과: environment에는 C: "3"만 존재 (A, B는 사라짐)
```

환경변수를 확장하려면 `<<:`를 `environment` 수준에서 사용해야 한다:

```yaml
x-common-env: &common-env
  A: "1"
  B: "2"

services:
  app:
    environment:
      <<: *common-env    # environment 매핑 내에서 병합
      C: "3"
    # 결과: A: "1", B: "2", C: "3" 모두 존재
```

---

## 자주 하는 실수

### 1. 오버라이드 파일 병합 순서 착각

```bash
# 순서가 중요하다 — 나중 파일이 이전 파일을 덮어씀
docker compose -f compose.yaml -f compose.prod.yaml up  # ✅ 올바름
docker compose -f compose.prod.yaml -f compose.yaml up  # ❌ 기본 설정이 프로덕션을 덮어씀
```

### 2. profiles 서비스의 depends_on 누락

```yaml
# ❌ pgadmin이 db에 접속해야 하는데 depends_on이 없음
pgadmin:
  image: dpage/pgadmin4
  profiles: [debug]

# ✅ depends_on 명시
pgadmin:
  image: dpage/pgadmin4
  profiles: [debug]
  depends_on:
    db:
      condition: service_healthy
```

### 3. .env 파일 경로/우선순위 혼동

```bash
# .env는 compose.yaml이 있는 디렉토리에서 자동 로드됨
# --env-file로 다른 파일을 지정하면 .env 자동 로드는 비활성화되지 않음!
# --env-file은 .env 파일을 "대체"하는 것이 아니라 Compose 변수 치환 소스를 추가하는 것

# .env + --env-file이 동시에 적용됨 (--env-file이 우선)
docker compose --env-file .env.prod up
```

### 4. 프로덕션에서 바인드 마운트 사용

```yaml
# ❌ 프로덕션에서 바인드 마운트 — 이미지의 의미가 없어짐
services:
  app:
    image: myapp:1.0
    volumes:
      - ./src:/app/src   # 서버에 소스 코드가 있어야 함

# ✅ 프로덕션에서는 이미지에 포함된 코드만 사용
services:
  app:
    image: myapp:1.0
    # volumes 없음 — 이미지가 곧 배포 단위
```

### 5. ports 시퀀스가 병합됨을 잊음

```yaml
# compose.yaml
services:
  app:
    ports:
      - "3000:3000"

# compose.prod.yaml
services:
  app:
    ports:
      - "80:3000"

# 병합 결과: 3000:3000 + 80:3000 둘 다 매핑됨!
# 의도가 "포트 교체"였다면 기본 파일에서 ports를 빼야 함
```

### 6. `<<:` 머지 키를 두 번 사용

```yaml
# ❌ YAML 표준 위반 — 같은 키를 두 번 쓸 수 없음
services:
  app:
    <<: *anchor1
    <<: *anchor2     # 파서에 따라 첫 번째가 무시되거나 에러

# ✅ 하나의 앵커에 모든 공통 설정을 통합
x-base: &base
  restart: unless-stopped
  logging: *default-logging
  deploy: *resource-limits

services:
  app:
    <<: *base
```

---

## 명령어 레퍼런스

| 명령어 | 설명 |
|--------|------|
| `docker compose -f A.yaml -f B.yaml up` | 여러 Compose 파일을 순서대로 병합하여 실행 |
| `docker compose --profile debug up` | 특정 프로파일의 서비스를 포함하여 실행 |
| `docker compose --env-file .env.prod up` | 지정한 env 파일을 변수 치환 소스로 사용 |
| `docker compose config` | 최종 병합 + 변수 치환 결과를 YAML로 출력 |
| `docker compose config --services` | 활성화될 서비스 이름만 출력 |
| `docker compose config --format json` | 최종 설정을 JSON으로 출력 |
| `docker compose config --profiles` | 정의된 프로파일 목록 출력 |
| `docker compose -f A.yaml -f B.yaml config` | 특정 파일 조합의 병합 결과 확인 |
| `COMPOSE_PROFILES=debug docker compose up` | 환경변수로 프로파일 활성화 |
| `COMPOSE_FILE=a.yaml:b.yaml docker compose up` | 환경변수로 다중 파일 지정 (`:` 구분) |

---

## 요약

- **다중 파일 오버라이드**: `compose.yaml` + `compose.override.yaml`은 자동 병합되며, `-f` 옵션으로 명시적 조합이 가능하다. 병합 규칙은 키 타입(스칼라/매핑/시퀀스)에 따라 다르다.
- **extends**: 서로 다른 서비스 간 공통 설정을 상속한다. 같은 파일 또는 외부 파일에서 참조 가능하지만, `networks`, `depends_on`, `volumes`는 상속되지 않는다.
- **환경 분리 전략**: `compose.yaml`(공통) + `compose.dev.yaml`(개발) + `compose.prod.yaml`(프로덕션)으로 분리하고, Makefile로 명령어를 단축한다.
- **Profiles**: 디버깅 도구, 마이그레이션 등 조건부 서비스에 `profiles:` 태그를 부여하고 `--profile`로 선택적 활성화한다.
- **환경변수**: `.env` 자동 로드, `env_file:` 지시어, 변수 치환 문법(`${VAR:-default}`, `${VAR:?error}`)을 조합하여 관리한다. 우선순위를 정확히 이해해야 한다.
- **빌드 설정**: 멀티스테이지 빌드의 `target`을 환경별 오버라이드로 바꿔 하나의 Dockerfile에서 개발/프로덕션 이미지를 모두 생성한다.
- **YAML 앵커**: `x-` 확장 필드에 `&앵커`를 정의하고 `<<: *앵커`로 병합하여 같은 파일 내 중복을 줄인다. 얕은 병합에 주의한다.
- **`docker compose config`**: 병합과 변수 치환의 최종 결과를 확인하는 디버깅 필수 도구다.

---

## 다른 챕터와의 관계

- **Ch 4 (Dockerfile Deep Dive)**: 멀티스테이지 빌드에서 `target` 지정은 이 챕터의 환경 분리 전략과 직접 결합된다. Dockerfile의 스테이지 설계가 Compose 오버라이드의 `build.target`과 짝을 이룬다.
- **Ch 5 (볼륨과 바인드 마운트)**: 개발 환경의 바인드 마운트 vs 프로덕션의 이미지 내장 전략은 Ch 5의 볼륨 유형 선택 기준과 연결된다.
- **Ch 7 (Docker Compose 기본)**: 이 챕터는 Ch 7의 단일 파일 Compose를 다중 환경으로 확장한다. Ch 7의 `services`, `networks`, `volumes`, `depends_on`, `healthcheck`, `develop.watch` 등 모든 기본 문법 위에 오버라이드/extends/profiles를 쌓는 구조다.
- **Ch 9 (프로덕션 이미지 최적화)**: `compose.prod.yaml`에서 설정하는 `deploy.resources`, `restart`, `healthcheck` 등은 Ch 9에서 다루는 프로덕션 최적화 원칙의 Compose 적용이다.
- **Ch 14 (CI/CD에서 Compose 활용)**: CI 파이프라인에서 `docker compose -f compose.yaml -f compose.test.yaml`로 테스트 환경을 구성하거나, profiles로 마이그레이션을 실행하는 패턴은 이 챕터의 직접적인 응용이다.