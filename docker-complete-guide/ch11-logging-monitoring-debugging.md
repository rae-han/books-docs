# Chapter 11: 로깅, 모니터링, 디버깅 — Logging, Monitoring & Debugging

## 핵심 질문

컨테이너화된 애플리케이션의 로그를 어떻게 수집하고, 리소스 사용량을 어떻게 모니터링하며, 문제가 발생했을 때 어떻게 디버깅하는가?

---

## 1. Docker 로깅 아키텍처

### 컨테이너 로그의 흐름

Docker의 로깅 모델은 놀라울 정도로 단순하다. 컨테이너 내부 프로세스가 **stdout**(표준 출력)과 **stderr**(표준 에러)로 보낸 모든 출력이 곧 로그가 된다. 이 스트림을 로깅 드라이버(*Logging Driver - Docker가 로그를 수집·저장·전달하는 플러그인*)가 받아 지정된 저장소로 전달한다.

```
┌─────────────────────┐
│   Node.js 애플리케이션  │
│   (PID 1 프로세스)     │
│                     │
│  console.log(...)   │──→ stdout ──┐
│  console.error(...) │──→ stderr ──┤
└─────────────────────┘            │
                                   ▼
                          ┌────────────────┐
                          │ Docker Engine   │
                          │ (Logging Driver)│
                          └───────┬────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
              json-file       fluentd       awslogs
              (로컬 파일)    (Fluentd 전달)  (CloudWatch)
```

### 12 Factor App과 로그

12 Factor App(*The Twelve-Factor App - 클라우드 네이티브 애플리케이션 설계를 위한 12가지 원칙*)의 **XI. Logs** 원칙은 다음과 같다:

> 애플리케이션은 로그의 라우팅이나 저장에 관여하지 않는다. 로그를 이벤트 스트림으로 취급하고, stdout으로 출력할 뿐이다.

이 원칙이 Docker와 완벽하게 맞아떨어진다. 애플리케이션은 stdout/stderr로 로그를 보내고, Docker 로깅 드라이버가 이를 수집·라우팅·저장한다. 애플리케이션 코드에서 파일 로깅을 직접 구현할 필요가 없다.

### Node.js에서 stdout 기반 로깅

가장 단순한 형태는 `console.log`이지만, 프로덕션에서는 구조화 로깅(*Structured Logging - JSON 등 파싱 가능한 형식으로 로그를 출력하는 방식*)이 필수다.

**console.log — 비구조화 로깅 (비추천)**:

```typescript
// 파싱 어려움, 검색 불편
console.log('User login failed for user@example.com');
```

**Pino — 구조화 로깅 (추천)**:

```typescript
import pino from 'pino';

// Pino는 기본적으로 stdout에 JSON을 출력한다
const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  // 프로덕션에서는 prettyPrint 비활성화 (JSON 유지)
  transport:
    process.env.NODE_ENV !== 'production'
      ? { target: 'pino-pretty' }
      : undefined,
});

// 구조화된 JSON 출력
logger.info({ userId: 'u-123', email: 'user@example.com' }, 'User login failed');
// → {"level":30,"time":1709827200000,"userId":"u-123","email":"user@example.com","msg":"User login failed"}
```

**Winston — stream을 stdout으로 설정**:

```typescript
import winston from 'winston';

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json(),
  ),
  transports: [
    // 파일이 아닌 Console(stdout/stderr)로 출력
    new winston.transports.Console(),
  ],
});

logger.info('Server started', { port: 3000, env: process.env.NODE_ENV });
// → {"level":"info","message":"Server started","port":3000,"env":"production","timestamp":"2026-03-07T10:00:00.000Z"}
```

> **핵심 통찰**: Node.js 로거를 설정할 때 파일 transport를 사용하지 않는다. 컨테이너 환경에서는 stdout/stderr로 출력하고, 로그 수집은 Docker 로깅 드라이버나 사이드카 컨테이너에 맡기는 것이 정석이다.

### JSON 구조화 로깅의 중요성

구조화 로깅은 단순히 "보기 좋은 로그"가 아니다. 로그를 **검색·필터·집계 가능한 데이터**로 만드는 것이다.

| 항목 | 비구조화 로그 | 구조화 로그 (JSON) |
|------|-------------|-------------------|
| 형식 | `Error: DB connection failed at 10:23` | `{"level":"error","msg":"DB connection failed","time":"...","host":"db-1"}` |
| 검색 | 정규식 필요 | `jq '.level == "error"'` |
| 집계 | 거의 불가능 | Elasticsearch/Loki에서 대시보드 생성 |
| 컨텍스트 | 수동으로 문자열 조합 | 필드 자동 포함 (requestId, userId 등) |

---

## 2. 로깅 드라이버

### json-file (기본 드라이버)

Docker의 기본 로깅 드라이버는 `json-file`이다. 각 로그 라인을 JSON으로 감싸 호스트의 파일시스템에 저장한다.

```bash
# 로그 파일 위치 확인
docker inspect --format='{{.LogPath}}' my-next-app
# → /var/lib/docker/containers/<container-id>/<container-id>-json.log
```

저장되는 형식:

```json
{"log":"Server started on port 3000\n","stream":"stdout","time":"2026-03-07T10:00:00.000000000Z"}
{"log":"{\"level\":\"info\",\"msg\":\"Request received\"}\n","stream":"stdout","time":"2026-03-07T10:00:01.000000000Z"}
```

**로그 로테이션 설정은 필수다.** 설정하지 않으면 로그 파일이 무한히 커져 디스크가 가득 찬다.

```bash
# 컨테이너별 로그 로테이션 설정
docker run -d \
  --name my-next-app \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  my-next-app:latest
```

Docker Compose에서의 설정:

```yaml
# docker-compose.yml
services:
  next-app:
    image: my-next-app:latest
    logging:
      driver: json-file
      options:
        max-size: "10m"   # 각 로그 파일 최대 10MB
        max-file: "3"     # 최대 3개 파일 유지 (총 30MB)
```

### 전역 기본 드라이버 설정

모든 컨테이너에 일괄 적용하려면 Docker 데몬 설정을 변경한다.

```json
// /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "5"
  }
}
```

```bash
# 데몬 재시작
sudo systemctl restart docker
```

### local 드라이버 (Docker 20.10+)

`local` 드라이버는 `json-file`보다 최적화된 내부 형식을 사용한다. 압축을 적용하여 디스크 사용량이 적고, 기본적으로 로테이션이 활성화되어 있다.

```json
// /etc/docker/daemon.json
{
  "log-driver": "local",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

> **핵심 통찰**: `local` 드라이버는 `json-file`보다 성능이 좋고 기본 로테이션이 적용되지만, `docker logs` 출력 형식이 약간 다르고 외부 도구와의 호환성이 낮을 수 있다. 개발 환경에서는 `json-file`이 디버깅에 더 편리하다.

### 외부 로깅 드라이버

프로덕션에서는 중앙 집중식 로그 수집을 위해 외부 드라이버를 사용한다.

| 드라이버 | 대상 | 사용 사례 |
|---------|------|----------|
| `fluentd` | Fluentd/Fluent Bit | 자체 호스팅 로그 파이프라인 |
| `awslogs` | Amazon CloudWatch Logs | AWS ECS/EC2 환경 |
| `gcplogs` | Google Cloud Logging | GCP 환경 |
| `syslog` | Syslog 서버 | 기존 syslog 인프라 |
| `journald` | systemd journal | systemd 기반 Linux |

```bash
# fluentd 드라이버 예시
docker run -d \
  --log-driver=fluentd \
  --log-opt fluentd-address=localhost:24224 \
  --log-opt tag="docker.{{.Name}}" \
  my-next-app:latest
```

---

## 3. docker logs 명령어 활용

`docker logs`는 컨테이너 로그를 조회하는 가장 기본적인 도구다. `json-file`과 `journald` 드라이버에서만 동작한다는 점에 주의한다.

### 기본 사용법

```bash
# 전체 로그 출력
docker logs my-next-app

# 실시간 로그 스트리밍 (Ctrl+C로 종료)
docker logs -f my-next-app

# 마지막 50줄만 출력
docker logs --tail 50 my-next-app

# 실시간 스트리밍 + 마지막 20줄부터 시작
docker logs -f --tail 20 my-next-app
```

### 시간 기반 필터링

```bash
# 최근 30분 로그
docker logs --since 30m my-next-app

# 특정 시간 이후 로그
docker logs --since "2026-03-07T10:00:00" my-next-app

# 특정 시간 범위 로그
docker logs --since "2026-03-07T10:00:00" --until "2026-03-07T11:00:00" my-next-app
```

### stdout과 stderr 분리

```bash
# stdout만 출력
docker logs my-next-app 2>/dev/null

# stderr만 출력
docker logs my-next-app 1>/dev/null
```

### Docker Compose 로그

```bash
# 모든 서비스 로그 (서비스별 색상 구분)
docker compose logs

# 특정 서비스 로그
docker compose logs next-app

# 실시간 스트리밍 + 마지막 100줄
docker compose logs -f --tail 100

# 여러 서비스 동시 조회
docker compose logs next-app postgres redis
```

### jq와 조합한 JSON 로그 분석

애플리케이션이 JSON 구조화 로그를 출력하면 `jq`(*jq - 커맨드라인 JSON 프로세서*)로 강력한 분석이 가능하다.

```bash
# error 레벨 로그만 필터링
docker logs my-next-app 2>&1 | jq -r 'select(.level == "error")'

# 특정 사용자의 로그만 추출
docker logs my-next-app 2>&1 | jq -r 'select(.userId == "u-123")'

# 응답 시간이 1초 이상인 요청 찾기
docker logs my-next-app 2>&1 | jq -r 'select(.responseTime > 1000)'

# 에러 메시지만 추출하여 카운트
docker logs my-next-app 2>&1 | jq -r 'select(.level == "error") | .msg' | sort | uniq -c | sort -rn
```

---

## 4. 리소스 모니터링

### docker stats — 실시간 리소스 사용량

```bash
# 모든 실행 중인 컨테이너의 리소스 사용량
docker stats

# 특정 컨테이너만
docker stats my-next-app postgres redis

# 스냅샷 (1회만 출력, 스크립트용)
docker stats --no-stream
```

출력 예시:

```
CONTAINER ID   NAME          CPU %   MEM USAGE / LIMIT     MEM %   NET I/O         BLOCK I/O     PIDS
a1b2c3d4e5f6   my-next-app   2.34%   187.2MiB / 512MiB     36.56%  12.3kB / 8.1kB  4.1MB / 0B    23
f6e5d4c3b2a1   postgres      0.45%   98.7MiB / 256MiB      38.55%  1.2kB / 890B    8.3MB / 12MB  12
```

| 항목 | 의미 |
|------|------|
| CPU % | CPU 사용률 (멀티코어 시 100% 이상 가능) |
| MEM USAGE / LIMIT | 현재 메모리 사용량 / 설정된 제한 |
| MEM % | 메모리 사용 비율 |
| NET I/O | 네트워크 송수신량 |
| BLOCK I/O | 디스크 읽기/쓰기량 |
| PIDS | 컨테이너 내 프로세스 수 |

### 커스텀 포맷으로 원하는 정보만 출력

```bash
# 이름, CPU, 메모리만 출력
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# JSON 형식으로 출력 (모니터링 스크립트용)
docker stats --no-stream --format '{"name":"{{.Name}}","cpu":"{{.CPUPerc}}","mem":"{{.MemPerc}}"}'
```

### docker top — 컨테이너 내 프로세스 목록

```bash
# 컨테이너 내부 프로세스 확인
docker top my-next-app

# ps 옵션 전달 가능
docker top my-next-app -o pid,ppid,user,%cpu,%mem,command
```

출력 예시:

```
UID    PID     PPID    C   STIME   TTY   TIME       CMD
node   12345   12300   2   10:00   ?     00:00:15   node server.js
```

### docker system df — 디스크 사용량

```bash
# 디스크 사용량 요약
docker system df

# 상세 정보
docker system df -v
```

출력 예시:

```
TYPE            TOTAL   ACTIVE  SIZE      RECLAIMABLE
Images          15      5       4.832GB   3.214GB (66%)
Containers      8       3       125.4MB   98.2MB (78%)
Local Volumes   12      4       2.156GB   1.823GB (84%)
Build Cache     45      0       1.567GB   1.567GB (100%)
```

> **핵심 통찰**: `Build Cache`의 RECLAIMABLE이 100%라면 `docker builder prune`으로 안전하게 회수할 수 있다. 이미지는 `docker image prune -a`로 사용하지 않는 이미지를 정리한다.

### docker system events — Docker 데몬 이벤트

```bash
# 실시간 이벤트 스트림
docker system events

# 필터링: 컨테이너 이벤트만
docker system events --filter type=container

# 특정 이벤트만: die (컨테이너 종료)
docker system events --filter type=container --filter event=die

# JSON 형식으로 출력
docker system events --format '{{json .}}'
```

컨테이너가 예기치 않게 종료될 때 `die` 이벤트를 모니터링하면 원인 파악에 도움이 된다.

```bash
# 30분 동안 죽는 컨테이너 감시
docker system events --filter event=die --since 30m
```

---

## 5. 헬스체크(Healthcheck) 심화

### 헬스체크의 목적

헬스체크(*Healthcheck - 컨테이너 내부 애플리케이션이 정상 동작하는지 주기적으로 확인하는 메커니즘*)는 컨테이너가 "실행 중(running)"인 것과 "정상 동작 중(healthy)"인 것을 구분한다. 프로세스가 살아 있더라도 DB 연결이 끊어졌거나 이벤트 루프가 블로킹되면 서비스는 사실상 장애 상태다.

### Node.js 헬스 엔드포인트 구현

**기본 헬스 엔드포인트**:

```typescript
// src/health.ts
import { Router, Request, Response } from 'express';
import { Pool } from 'pg';

const router = Router();

// Liveness: 프로세스가 살아 있는지 확인
router.get('/health/live', (_req: Request, res: Response) => {
  res.status(200).json({ status: 'ok' });
});

// Readiness: 외부 의존성까지 정상인지 확인
router.get('/health/ready', async (_req: Request, res: Response) => {
  try {
    // DB 연결 확인
    await pool.query('SELECT 1');

    // Redis 연결 확인
    await redis.ping();

    res.status(200).json({
      status: 'ok',
      uptime: process.uptime(),
      memory: process.memoryUsage(),
      checks: {
        database: 'connected',
        redis: 'connected',
      },
    });
  } catch (error) {
    res.status(503).json({
      status: 'error',
      error: error instanceof Error ? error.message : 'Unknown error',
    });
  }
});

export default router;
```

### Dockerfile HEALTHCHECK

```dockerfile
FROM node:20-slim AS runner

WORKDIR /app
COPY --from=builder /app .

# 헬스체크: 30초마다 실행, 5초 타임아웃, 3회 실패 시 unhealthy
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD node -e "fetch('http://localhost:3000/health/live').then(r => { if (!r.ok) throw new Error(); })" || exit 1

EXPOSE 3000
CMD ["node", "server.js"]
```

| 옵션 | 의미 | 기본값 |
|------|------|--------|
| `--interval` | 검사 주기 | 30s |
| `--timeout` | 응답 대기 시간 | 30s |
| `--start-period` | 초기 유예 시간 (이 동안 실패 무시) | 0s |
| `--retries` | unhealthy 판정까지 연속 실패 횟수 | 3 |

### Docker Compose 헬스체크

```yaml
# docker-compose.yml
services:
  next-app:
    build: .
    ports:
      - "3000:3000"
    healthcheck:
      test: ["CMD", "node", "-e", "fetch('http://localhost:3000/health/live').then(r => { if (!r.ok) throw new Error(); })"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
    depends_on:
      postgres:
        condition: service_healthy

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: myapp
      POSTGRES_PASSWORD: secret
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
```

### 헬스 상태 확인

```bash
# 헬스 상태 확인
docker inspect --format='{{.State.Health.Status}}' my-next-app
# → healthy | unhealthy | starting

# 헬스체크 로그 확인
docker inspect --format='{{json .State.Health}}' my-next-app | jq .
```

상태 전이:

```
starting ──(start_period 경과)──→ healthy ──(retries회 연속 실패)──→ unhealthy
                                     ↑                                   │
                                     └──────(1회 성공)──────────────────┘
```

### unhealthy 시 자동 재시작

Docker Swarm이나 Kubernetes에서는 unhealthy 컨테이너를 자동으로 재시작한다. 단독 Docker에서는 `restart` 정책과 조합하여 사용한다.

```yaml
services:
  next-app:
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "node", "-e", "fetch('http://localhost:3000/health/live').then(r => { if (!r.ok) throw new Error(); })"]
      interval: 15s
      timeout: 5s
      retries: 3
```

> **핵심 통찰**: 단독 Docker Engine에서 `restart: unless-stopped`은 프로세스가 종료(exit)될 때만 재시작한다. healthcheck가 unhealthy로 바뀌어도 자동 재시작하지 않는다. unhealthy 기반 자동 복구가 필요하면 Docker Swarm, Kubernetes, 또는 `autoheal` 같은 서드파티 도구를 사용해야 한다.

---

## 6. OOM(Out of Memory) 진단

### OOM Killer란

Linux 커널의 OOM Killer(*Out of Memory Killer - 시스템 메모리가 부족할 때 프로세스를 강제 종료하는 커널 메커니즘*)는 메모리가 부족해지면 가장 많은 메모리를 사용하는 프로세스를 강제 종료한다. 컨테이너에 `--memory` 제한이 걸려 있으면 해당 제한을 초과할 때 OOM Killer가 동작한다.

### OOM 발생 확인

```bash
# 컨테이너가 OOM으로 종료되었는지 확인
docker inspect --format='{{.State.OOMKilled}}' my-next-app
# → true

# 종료 코드 확인 (137 = SIGKILL, OOM 가능성 높음)
docker inspect --format='{{.State.ExitCode}}' my-next-app
# → 137
```

```bash
# docker system events로 OOM 이벤트 감지
docker system events --filter event=oom
```

### Node.js 메모리 설정

Node.js의 V8 엔진은 자체적인 힙(*Heap - V8이 JavaScript 객체를 저장하는 메모리 영역*) 한도를 가진다. 컨테이너 메모리 제한과 V8 힙 한도를 적절히 조율해야 한다.

```
┌──────────────────────────────────────────┐
│          컨테이너 메모리 제한 (512MB)        │
│                                          │
│  ┌────────────────────────────────────┐  │
│  │    V8 Heap (~384MB, 75%)          │  │
│  │    --max-old-space-size=384       │  │
│  └────────────────────────────────────┘  │
│                                          │
│  [ V8 외부 버퍼, libuv, OS 오버헤드 ~128MB ] │
└──────────────────────────────────────────┘
```

**권장 설정**: V8 힙 한도 = 컨테이너 메모리의 약 75%

```yaml
# docker-compose.yml
services:
  next-app:
    build: .
    deploy:
      resources:
        limits:
          memory: 512M
    environment:
      NODE_OPTIONS: "--max-old-space-size=384"
```

| 컨테이너 메모리 | --max-old-space-size | 비고 |
|----------------|---------------------|------|
| 256MB | 192 | 경량 서비스 |
| 512MB | 384 | 일반적인 Next.js 앱 |
| 1024MB | 768 | SSR이 무거운 경우 |
| 2048MB | 1536 | 대규모 데이터 처리 |

### 메모리 누수 디버깅

Node.js의 `--inspect` 플래그를 사용하면 Chrome DevTools로 힙 스냅샷을 분석할 수 있다.

```yaml
# docker-compose.debug.yml
services:
  next-app:
    build: .
    ports:
      - "3000:3000"
      - "9229:9229"    # 디버거 포트
    environment:
      NODE_OPTIONS: "--inspect=0.0.0.0:9229 --max-old-space-size=384"
    deploy:
      resources:
        limits:
          memory: 512M
```

```bash
# 디버그 모드로 실행
docker compose -f docker-compose.yml -f docker-compose.debug.yml up next-app
```

Chrome에서 `chrome://inspect`로 접속하여:

1. **Memory** 탭 → **Take heap snapshot** 클릭
2. 의심되는 동작 수행
3. 두 번째 스냅샷 촬영
4. **Comparison** 뷰에서 증가한 객체 확인

### 런타임 메모리 모니터링 엔드포인트

```typescript
// src/routes/debug.ts
import { Router, Request, Response } from 'express';

const router = Router();

router.get('/debug/memory', (_req: Request, res: Response) => {
  const usage = process.memoryUsage();

  res.json({
    rss: `${(usage.rss / 1024 / 1024).toFixed(1)}MB`,        // 전체 메모리
    heapTotal: `${(usage.heapTotal / 1024 / 1024).toFixed(1)}MB`, // V8 힙 전체
    heapUsed: `${(usage.heapUsed / 1024 / 1024).toFixed(1)}MB`,  // V8 힙 사용량
    external: `${(usage.external / 1024 / 1024).toFixed(1)}MB`,   // V8 외부 C++ 객체
    arrayBuffers: `${(usage.arrayBuffers / 1024 / 1024).toFixed(1)}MB`,
  });
});

export default router;
```

---

## 7. 컨테이너 디버깅 기법

### docker exec — 실행 중인 컨테이너 접속

```bash
# 셸 접속 (Alpine은 sh, Debian은 bash)
docker exec -it my-next-app sh
docker exec -it my-next-app bash

# 특정 명령어만 실행
docker exec my-next-app node -e "console.log(process.memoryUsage())"

# 환경 변수 확인
docker exec my-next-app env

# 네트워크 상태 확인
docker exec my-next-app cat /etc/hosts
docker exec my-next-app cat /etc/resolv.conf
```

### docker cp — 파일 복사

```bash
# 컨테이너 → 호스트: 로그 파일이나 코어 덤프 추출
docker cp my-next-app:/app/logs/error.log ./error.log

# 호스트 → 컨테이너: 디버깅용 스크립트 주입
docker cp ./debug-script.js my-next-app:/tmp/debug-script.js
docker exec my-next-app node /tmp/debug-script.js
```

### docker diff — 파일시스템 변경 확인

```bash
# 컨테이너 시작 이후 변경된 파일 확인
docker diff my-next-app
```

출력 예시:

```
C /tmp                    # C = Changed (변경됨)
A /tmp/debug-script.js    # A = Added (추가됨)
D /app/node_modules/.cache # D = Deleted (삭제됨)
```

이 명령어는 예상치 못한 파일 변경(보안 침해 등)을 탐지할 때 유용하다.

### distroless 이미지 디버깅

distroless(*Distroless - 셸, 패키지 매니저 등을 제거하여 공격 표면을 최소화한 컨테이너 이미지*) 이미지에는 `sh`이 없어 `docker exec`로 셸 접속이 불가능하다.

**방법 1: debug 변형 이미지 사용**

```dockerfile
# 프로덕션은 distroless, 디버깅은 debug 변형
# gcr.io/distroless/nodejs20-debian12:debug 에는 busybox 셸이 포함됨
FROM gcr.io/distroless/nodejs20-debian12:debug AS debug
FROM gcr.io/distroless/nodejs20-debian12 AS production
```

**방법 2: 동일 네트워크에서 디버깅 컨테이너 실행**

```bash
# 기존 컨테이너의 네트워크 네임스페이스 공유
docker run -it --rm \
  --network container:my-next-app \
  --pid container:my-next-app \
  alpine sh
```

### 네트워크 디버깅: nicolaka/netshoot

네트워크 문제 진단에 특화된 디버깅 컨테이너다. curl, dig, nslookup, tcpdump, iftop 등이 모두 포함되어 있다.

```bash
# 대상 컨테이너의 네트워크로 접속
docker run -it --rm \
  --network container:my-next-app \
  nicolaka/netshoot

# 내부에서 DNS 확인
nslookup postgres
dig postgres

# HTTP 요청 테스트
curl -v http://localhost:3000/health/live

# TCP 연결 확인
nc -zv postgres 5432

# 네트워크 트래픽 캡처
tcpdump -i eth0 port 5432
```

Docker Compose 네트워크에서 서비스 간 통신을 디버깅할 때:

```bash
# Compose 네트워크에 직접 연결
docker run -it --rm \
  --network myapp_default \
  nicolaka/netshoot

# 서비스 이름으로 DNS 조회
nslookup next-app
nslookup postgres
```

### Node.js 원격 디버깅

```yaml
# docker-compose.yml
services:
  next-app:
    build: .
    ports:
      - "3000:3000"
      - "9229:9229"
    command: ["node", "--inspect=0.0.0.0:9229", "server.js"]
```

VS Code에서 연결:

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Docker: Attach to Node",
      "type": "node",
      "request": "attach",
      "port": 9229,
      "address": "localhost",
      "localRoot": "${workspaceFolder}",
      "remoteRoot": "/app",
      "restart": true
    }
  ]
}
```

> **핵심 통찰**: `--inspect=0.0.0.0:9229`에서 `0.0.0.0`은 필수다. 기본값인 `127.0.0.1`로 바인딩하면 컨테이너 외부에서 접근할 수 없다. 단, 프로덕션에서는 디버그 포트를 절대 노출하지 않는다.

---

## 8. 프로덕션 로깅 파이프라인 개요

### 일반적인 아키텍처

```
┌──────────┐   ┌──────────┐   ┌──────────┐
│ Next.js  │   │ API 서버  │   │ Worker   │
│ (stdout) │   │ (stdout) │   │ (stdout) │
└────┬─────┘   └────┬─────┘   └────┬─────┘
     │              │              │
     └──────────────┼──────────────┘
                    │
                    ▼
          ┌──────────────────┐
          │   Fluent Bit     │    ← 경량 로그 수집기
          │   (DaemonSet)    │
          └────────┬─────────┘
                   │
         ┌─────────┴──────────┐
         ▼                    ▼
┌─────────────────┐  ┌──────────────┐
│  Elasticsearch  │  │    Loki      │   ← 로그 저장소
│  (풀텍스트 검색)  │  │ (레이블 기반) │
└────────┬────────┘  └──────┬───────┘
         │                  │
         ▼                  ▼
┌─────────────────┐  ┌──────────────┐
│    Kibana       │  │   Grafana    │   ← 시각화/대시보드
└─────────────────┘  └──────────────┘
```

### Docker Compose로 로깅 스택 구성 (Loki + Grafana)

```yaml
# docker-compose.logging.yml
services:
  # 애플리케이션
  next-app:
    build: .
    ports:
      - "3000:3000"
    logging:
      driver: fluentd
      options:
        fluentd-address: "localhost:24224"
        tag: "app.next"

  # 로그 수집기
  fluent-bit:
    image: fluent/fluent-bit:latest
    ports:
      - "24224:24224"
    volumes:
      - ./fluent-bit.conf:/fluent-bit/etc/fluent-bit.conf:ro
    depends_on:
      - loki

  # 로그 저장소
  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    volumes:
      - loki-data:/loki

  # 시각화
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
    volumes:
      - grafana-data:/var/lib/grafana
    depends_on:
      - loki

volumes:
  loki-data:
  grafana-data:
```

Fluent Bit 설정:

```yaml
# fluent-bit.conf
[SERVICE]
    Flush        1
    Log_Level    info

[INPUT]
    Name         forward
    Listen       0.0.0.0
    Port         24224

[FILTER]
    Name         parser
    Match        app.*
    Key_Name     log
    Parser       json

[OUTPUT]
    Name         loki
    Match        *
    Host         loki
    Port         3100
    Labels       job=docker,app=$TAG
```

### 간단한 대안: docker logs + 로그 로테이션

프로덕션 로깅 스택을 구축할 여력이 없다면, 최소한 다음은 설정해야 한다.

```json
// /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "50m",
    "max-file": "5",
    "compress": "true"
  }
}
```

이렇게 하면 컨테이너당 최대 250MB(50MB x 5)로 로그가 제한된다. 이후 `docker logs`와 `jq`로 필요한 분석을 수행한다.

---

## 자주 하는 실수

| 실수 | 결과 | 해결 |
|------|------|------|
| 로그 로테이션 미설정 | 디스크가 가득 차서 시스템 장애 | `daemon.json`에서 `max-size`, `max-file` 설정 |
| 파일 로깅 사용 (stdout 대신) | Docker 로깅 드라이버 무력화, 로그 수집 불가 | Winston/Pino에서 Console transport만 사용 |
| OOM 원인 파악 못함 | "컨테이너가 갑자기 죽는다"만 반복 | `docker inspect`로 OOMKilled 확인, `--max-old-space-size` 조정 |
| 헬스체크 미설정 | 프로세스는 살아있지만 서비스 불능 상태 방치 | HEALTHCHECK 또는 Compose healthcheck 설정 |
| `--memory` 없이 실행 | 한 컨테이너가 호스트 메모리 전체를 소진 | deploy.resources.limits.memory 설정 |
| `--inspect=127.0.0.1` 사용 | 컨테이너 외부에서 디버거 접속 불가 | `--inspect=0.0.0.0:9229` 사용 (개발 환경만) |
| 프로덕션에서 디버그 포트 노출 | 보안 취약점 (원격 코드 실행 가능) | 프로덕션에서는 9229 포트 절대 비노출 |

---

## 명령어 레퍼런스

| 명령어 | 용도 |
|--------|------|
| `docker logs <container>` | 컨테이너 로그 출력 |
| `docker logs -f --tail N` | 마지막 N줄부터 실시간 스트리밍 |
| `docker logs --since 30m` | 최근 30분 로그 조회 |
| `docker stats` | 실시간 CPU/메모리/네트워크/IO 모니터링 |
| `docker stats --no-stream` | 리소스 사용량 스냅샷 (1회) |
| `docker top <container>` | 컨테이너 내 프로세스 목록 |
| `docker system df` | 이미지/컨테이너/볼륨/캐시 디스크 사용량 |
| `docker system events` | Docker 데몬 이벤트 실시간 스트림 |
| `docker inspect --format='{{.State.OOMKilled}}'` | OOM 종료 여부 확인 |
| `docker inspect --format='{{.State.Health.Status}}'` | 헬스체크 상태 확인 |
| `docker exec -it <container> sh` | 실행 중인 컨테이너에 셸 접속 |
| `docker cp <container>:<path> <host-path>` | 컨테이너에서 호스트로 파일 복사 |
| `docker diff <container>` | 컨테이너 파일시스템 변경 내역 |

---

## 요약

- Docker는 **stdout/stderr**을 로그로 수집한다. Node.js 애플리케이션은 파일이 아닌 stdout으로 JSON 구조화 로그를 출력해야 한다.
- **로그 로테이션**은 반드시 설정한다. `max-size`와 `max-file` 없이는 디스크가 가득 찬다.
- `docker stats`로 실시간 리소스를, `docker system df`로 디스크 사용량을, `docker system events`로 데몬 이벤트를 모니터링한다.
- **헬스체크**로 "프로세스 살아 있음"과 "서비스 정상"을 구분한다. liveness와 readiness 엔드포인트를 분리하는 것이 좋다.
- **OOM**은 `docker inspect`에서 `OOMKilled: true`로 확인하며, `--max-old-space-size`를 컨테이너 메모리의 약 75%로 설정한다.
- 디버깅은 `docker exec`, `docker cp`, `docker diff`를 조합하고, 네트워크 문제는 `nicolaka/netshoot`으로 진단한다.
- 프로덕션 로깅 파이프라인은 **Fluent Bit → Loki/Elasticsearch → Grafana/Kibana** 구조가 일반적이다.

---

## 다른 챕터와의 관계

| 챕터 | 연관 내용 |
|------|----------|
| **Ch 3** (기본 명령어) | `docker stats`, `docker logs`의 기본 사용법을 다루었으며, 본 챕터에서 심화 활용법으로 확장 |
| **Ch 4** (Dockerfile) | `HEALTHCHECK` 인스트럭션의 기본 문법을 소개했으며, 본 챕터에서 Node.js 헬스 엔드포인트와 연동하는 실전 패턴으로 심화 |
| **Ch 7** (Docker Compose) | `depends_on: condition: service_healthy`로 서비스 간 시작 순서를 제어하는 패턴을 본 챕터의 헬스체크와 연결 |
| **Ch 10** (보안) | 보안 이벤트 추적에 `docker system events`와 `docker diff`를 활용하는 방법과 연결 |
| **Ch 12** (프로덕션 최적화) | Node.js 메모리 설정(`--max-old-space-size`)과 리소스 제한의 심화 내용으로 확장 |
