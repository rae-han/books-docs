# Chapter 3: 컨테이너 — 이미지의 실행 인스턴스: Containers

## 핵심 질문

컨테이너는 내부적으로 어떻게 격리를 구현하며, 생명주기는 어떻게 관리하는가? PID 1 문제란 무엇이고, Node.js 애플리케이션에서 왜 중요한가?

---

## 1. 컨테이너의 본질

### 1.1 컨테이너는 격리된 프로세스다

컨테이너는 가상 머신(VM)이 아니다. VM은 하이퍼바이저 위에 게스트 OS 전체를 올리지만, 컨테이너는 호스트 커널을 공유하면서 **프로세스 수준의 격리**만 제공한다. `docker run node:20-alpine node -e "console.log('hello')"` 명령을 실행하면, 호스트에서 `ps aux | grep node`로 해당 프로세스를 직접 확인할 수 있다. 컨테이너 안의 프로세스는 호스트 입장에서 그저 하나의 프로세스일 뿐이다.

```bash
# 호스트에서 컨테이너 프로세스 확인
docker run -d --name demo node:20-alpine sleep 3600
ps aux | grep sleep
# 호스트의 프로세스 목록에 sleep 3600이 보인다
```

### 1.2 이미지 + R/W 레이어 = 컨테이너

Ch 2에서 이미지는 읽기 전용(R/O) 레이어의 스택이라고 설명했다. 컨테이너를 생성하면 이 이미지 위에 얇은 **읽기/쓰기(R/W) 레이어**가 하나 추가된다. 컨테이너 내부에서 파일을 생성하거나 수정하면 이 R/W 레이어에 기록된다. 이를 CoW(*Copy-on-Write - 쓰기 시점에 원본을 복사하여 수정하는 전략*)라 한다.

```
┌─────────────────────────────┐
│   R/W Layer (컨테이너 고유)    │  ← 컨테이너가 생성/수정한 파일
├─────────────────────────────┤
│   R/O Layer 3 (npm install) │
├─────────────────────────────┤
│   R/O Layer 2 (COPY . .)   │  ← 이미지 레이어 (공유 가능)
├─────────────────────────────┤
│   R/O Layer 1 (node:20)    │
└─────────────────────────────┘
```

핵심은 R/O 레이어는 여러 컨테이너가 **공유**한다는 점이다. 같은 이미지에서 10개의 컨테이너를 만들어도, 이미지 레이어는 디스크에 한 벌만 존재한다. 추가되는 것은 각 컨테이너의 얇은 R/W 레이어뿐이다.

### 1.3 하나의 이미지, 여러 컨테이너

```bash
# 같은 이미지에서 3개의 독립적인 컨테이너 생성
docker run -d --name app-1 my-next-app
docker run -d --name app-2 my-next-app
docker run -d --name app-3 my-next-app

# 각 컨테이너는 독립된 R/W 레이어, PID 공간, 네트워크를 가진다
docker exec app-1 sh -c "echo 'modified' > /tmp/test.txt"
docker exec app-2 cat /tmp/test.txt  # 파일이 존재하지 않음 — 격리 확인
```

---

## 2. 컨테이너 생명주기

### 2.1 상태 다이어그램

컨테이너는 다음 5가지 상태를 가진다.

```
                docker create
 (없음) ──────────────────────► Created
                                  │
                           docker start
                                  │
                                  ▼
                              Running ◄────────── docker restart
                             /   │   \                  ▲
                docker pause/  docker stop  docker kill  │
                            /    │          \            │
                           ▼     ▼           ▼           │
                       Paused  Stopped ──────────────────┘
                           │     │
                docker unpause   docker rm
                           │     │
                           ▼     ▼
                       Running  (삭제됨)
```

### 2.2 각 상태와 전이 명령어

| 상태 | 설명 | 진입 명령어 |
|------|------|------------|
| **Created** | 컨테이너가 생성되었지만 아직 실행되지 않음 | `docker create` |
| **Running** | 메인 프로세스가 실행 중 | `docker start`, `docker run` |
| **Paused** | 프로세스가 일시 중지됨 (SIGSTOP) | `docker pause` |
| **Stopped** | 메인 프로세스가 종료됨 (exit code 보존) | `docker stop`, `docker kill` |
| **Removed** | 컨테이너와 R/W 레이어가 완전히 삭제됨 | `docker rm` |

### 2.3 docker create vs docker run

`docker run`은 사실 `docker create` + `docker start`를 합친 것이다.

```bash
# docker create: 컨테이너를 생성만 한다 (실행하지 않음)
docker create --name my-app -p 3000:3000 my-next-app
# 출력: 컨테이너 ID (예: a1b2c3d4e5f6)

docker start my-app  # 이제 실행

# docker run: 생성 + 실행을 한 번에
docker run --name my-app -p 3000:3000 my-next-app
```

`docker create`가 유용한 경우는 컨테이너를 미리 구성해두고, 특정 시점에 시작하고 싶을 때다. 예를 들어 CI/CD에서 테스트 환경을 미리 준비할 때 쓸 수 있다.

### 2.4 docker stop vs docker kill

이 둘의 차이는 **그레이스풀 셧다운(*Graceful Shutdown - 진행 중인 작업을 안전하게 마무리한 뒤 종료하는 것*)**을 허용하느냐다.

```bash
# docker stop: SIGTERM → 10초 대기 → SIGKILL
docker stop my-app          # 기본 10초 대기
docker stop -t 30 my-app    # 30초까지 대기

# docker kill: 즉시 SIGKILL (프로세스가 정리할 시간 없음)
docker kill my-app
```

**docker stop의 동작 순서:**

1. 컨테이너의 메인 프로세스(PID 1)에 `SIGTERM` 전송
2. 프로세스가 시그널을 받고 정리 작업 수행 (DB 연결 해제, 진행 중인 요청 완료 등)
3. 프로세스가 스스로 종료하면 완료
4. 10초(기본값) 내에 종료하지 않으면 `SIGKILL`로 강제 종료

Node.js/Next.js 애플리케이션에서 이 10초는 매우 중요하다. 진행 중인 HTTP 요청을 완료하고, 데이터베이스 커넥션 풀을 정리하는 시간이 필요하기 때문이다.

### 2.5 docker restart, docker pause/unpause

```bash
# restart = stop + start
docker restart my-app        # SIGTERM → 대기 → start
docker restart -t 5 my-app   # 5초 대기 후 강제 종료 → start

# pause/unpause: cgroups의 freezer를 사용하여 프로세스를 일시 중지
docker pause my-app
# 모든 프로세스가 얼어붙음 — CPU를 전혀 사용하지 않지만 메모리는 유지
docker unpause my-app
```

`docker pause`는 디버깅 시 유용하다. 컨테이너 상태를 그대로 보존하면서 잠시 멈추고 싶을 때 사용한다.

### 2.6 --rm 플래그: 종료 시 자동 삭제

```bash
# 학습/테스트용 컨테이너는 --rm을 사용하여 종료 시 자동 삭제
docker run --rm -it node:20-alpine node -e "console.log(process.version)"
# 실행 후 즉시 삭제됨 — docker ps -a에도 남지 않음

# --rm 없이 실행하면 Stopped 상태로 계속 남아 디스크 공간을 차지
docker run node:20-alpine echo "hello"
docker ps -a  # Exited 상태로 남아있음
```

> **실무 팁**: 개발 환경에서는 `--rm`을 습관적으로 사용하라. Stopped 상태의 컨테이너가 수십 개 쌓이면 `docker system df`에서 확인할 수 있듯이 상당한 디스크 공간을 차지한다. 정리하려면 `docker container prune`을 사용한다.

---

## 3. 리눅스 네임스페이스

### 3.1 네임스페이스란

네임스페이스(*Namespace - 프로세스가 보는 시스템 리소스의 범위를 제한하는 리눅스 커널 기능*)는 컨테이너 격리의 핵심 메커니즘이다. 각 네임스페이스는 특정 종류의 시스템 리소스를 격리한다. 프로세스는 자신이 속한 네임스페이스 안의 리소스만 볼 수 있다.

Docker는 컨테이너를 생성할 때 다음 6가지 네임스페이스를 설정한다.

### 3.2 PID 네임스페이스

컨테이너 안에서 프로세스 ID는 1부터 시작한다. 컨테이너의 메인 프로세스는 PID 1을 받는다.

```bash
# 컨테이너 안에서 PID 확인
docker run --rm node:20-alpine ps aux
# PID  USER  COMMAND
#   1  root  ps aux

# Next.js 앱을 실행하면
docker run --rm -d --name next-app my-next-app
docker exec next-app ps aux
# PID  USER  COMMAND
#   1  root  node server.js
#  20  root  ps aux
```

호스트에서 같은 프로세스를 보면 PID는 완전히 다른 번호를 가진다. 이것이 PID 네임스페이스의 격리 효과다.

```bash
# 호스트에서 확인 — 같은 프로세스가 다른 PID를 가짐
docker top next-app
# PID     PPID    COMMAND
# 48291   48270   node server.js
```

### 3.3 Network 네임스페이스

각 컨테이너는 독립된 네트워크 스택을 가진다. 자체 IP 주소, 포트 범위, 라우팅 테이블, iptables 규칙이 있다.

```bash
# 컨테이너의 네트워크 인터페이스 확인
docker run --rm node:20-alpine ip addr
# lo: 127.0.0.1 (루프백)
# eth0: 172.17.0.2 (Docker 브리지 네트워크에서 할당받은 IP)

# 두 컨테이너가 동일한 포트를 사용해도 충돌하지 않음
docker run -d --name app-a -p 3001:3000 my-next-app
docker run -d --name app-b -p 3002:3000 my-next-app
# 둘 다 컨테이너 내부에서 3000번 포트를 사용하지만, 호스트에서는 3001, 3002로 매핑
```

### 3.4 Mount 네임스페이스

각 컨테이너는 독립된 파일시스템 뷰를 가진다. 이미지의 레이어가 겹쳐져 만들어진 루트 파일시스템이 컨테이너의 `/`가 된다.

```bash
# 컨테이너의 파일시스템은 이미지로부터 만들어진다
docker run --rm node:20-alpine ls /
# bin  dev  etc  home  lib  media  mnt  opt  proc  root  run  sbin  srv  sys  tmp  usr  var

# 호스트의 파일시스템과 완전히 분리되어 있다
docker run --rm node:20-alpine cat /etc/os-release
# Alpine Linux — 호스트가 Ubuntu여도 컨테이너 안은 Alpine
```

### 3.5 UTS 네임스페이스

UTS(*UNIX Time-Sharing*) 네임스페이스는 호스트네임을 격리한다.

```bash
# 컨테이너의 hostname은 기본적으로 컨테이너 ID의 앞 12자리
docker run --rm node:20-alpine hostname
# a1b2c3d4e5f6

# --hostname 옵션으로 커스텀 호스트네임 설정
docker run --rm --hostname my-next-server node:20-alpine hostname
# my-next-server
```

### 3.6 IPC 네임스페이스

IPC(*Inter-Process Communication - 프로세스 간 통신*) 네임스페이스는 공유 메모리, 세마포어, 메시지 큐를 격리한다. 컨테이너 A의 공유 메모리 세그먼트는 컨테이너 B에서 접근할 수 없다.

```bash
# IPC 리소스 확인
docker run --rm node:20-alpine ipcs
# 빈 목록 — 격리된 IPC 네임스페이스이므로 호스트의 IPC 리소스가 보이지 않음
```

### 3.7 User 네임스페이스

User 네임스페이스는 UID/GID를 매핑한다. 컨테이너 안에서 root(UID 0)로 실행되는 프로세스를 호스트에서는 비특권 사용자로 매핑할 수 있다. 이는 보안상 매우 중요하다.

```bash
# 컨테이너 안에서 UID 확인
docker run --rm node:20-alpine id
# uid=0(root) gid=0(root) — 기본적으로 root로 실행됨

# 비root 사용자로 실행 (보안 모범 사례)
docker run --rm --user 1000:1000 node:20-alpine id
# uid=1000 gid=1000
```

> **핵심 통찰**: 네임스페이스는 "무엇을 볼 수 있는가"를 제한하고, 뒤에서 다룰 cgroups는 "얼마나 사용할 수 있는가"를 제한한다. 이 두 가지가 합쳐져 컨테이너의 격리가 완성된다.

---

## 4. cgroups (Control Groups)

### 4.1 cgroups란

cgroups(*Control Groups - 프로세스 그룹의 리소스 사용량을 제한하고 모니터링하는 리눅스 커널 기능*)는 컨테이너가 호스트의 리소스를 독점하지 못하게 한다. 네임스페이스가 "격리"라면, cgroups는 "제한"이다.

### 4.2 CPU 제한

```bash
# --cpus: 사용 가능한 CPU 코어 수 제한
docker run -d --cpus=1.5 --name cpu-limited my-next-app
# 최대 1.5개의 CPU 코어만 사용 가능

# --cpu-shares: 상대적 가중치 (기본값 1024)
docker run -d --cpu-shares=512 --name low-priority my-next-app
docker run -d --cpu-shares=2048 --name high-priority my-next-app
# CPU 경합 시 high-priority가 low-priority보다 4배 더 많은 CPU 시간을 받음
# CPU가 충분하면 shares는 효과가 없다 — 경합 시에만 작동

# --cpuset-cpus: 특정 CPU 코어에 고정
docker run -d --cpuset-cpus="0,1" --name pinned-app my-next-app
# 0번, 1번 코어에서만 실행
```

### 4.3 메모리 제한

```bash
# --memory: 최대 메모리 사용량 제한
docker run -d --memory=512m --name mem-limited my-next-app
# 512MB 초과 시 OOM Killer가 컨테이너를 종료

# --memory-swap: 스왑 포함 메모리 한도
docker run -d --memory=512m --memory-swap=1g my-next-app
# RAM 512MB + Swap 512MB = 총 1GB

# 스왑 비활성화 (권장)
docker run -d --memory=512m --memory-swap=512m my-next-app
# --memory와 --memory-swap이 같으면 스왑을 사용하지 않음
```

### 4.4 Node.js에서 메모리 제한의 중요성

Node.js(V8 엔진)는 기본적으로 시스템 전체 메모리를 기준으로 힙 한도를 설정한다. 문제는 **컨테이너의 메모리 제한을 인식하지 못할 수 있다**는 점이다.

```bash
# V8의 기본 힙 한도 확인
docker run --rm --memory=512m node:20-alpine \
  node -e "console.log(Math.round(v8.getHeapStatistics().heap_size_limit / 1024 / 1024) + 'MB')"
```

Node.js 12.x부터는 cgroups 메모리 제한을 감지하여 자동으로 힙 한도를 조정하지만, 여전히 명시적으로 설정하는 것이 안전하다.

```bash
# --max-old-space-size로 V8 힙 한도를 명시적으로 설정
# 컨테이너 메모리의 ~75%를 V8 힙에 할당 (나머지는 스택, 네이티브 메모리 등)
docker run --rm --memory=512m node:20-alpine \
  node --max-old-space-size=384 -e "console.log(Math.round(v8.getHeapStatistics().heap_size_limit / 1024 / 1024) + 'MB')"
# 384MB
```

Next.js 프로젝트에서의 적용:

```dockerfile
# Dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# 메모리 제한에 맞춘 V8 힙 설정
ENV NODE_OPTIONS="--max-old-space-size=384"
EXPOSE 3000
CMD ["node", "server.js"]
```

```bash
# 512MB 메모리 제한으로 실행
docker run -d --memory=512m -p 3000:3000 my-next-app
```

> **핵심 통찰**: 컨테이너 메모리 제한(`--memory`)과 V8 힙 한도(`--max-old-space-size`)를 반드시 동기화하라. `--memory=512m`인데 V8이 2GB 힙을 잡으려 하면 OOM Killer가 컨테이너를 강제 종료한다. 디버깅하기 매우 어려운 장애를 유발하는 원인이다.

### 4.5 리소스 사용량 모니터링

```bash
# docker stats: 실시간 리소스 사용량 모니터링
docker stats my-next-app
# CONTAINER ID  NAME        CPU %  MEM USAGE / LIMIT  MEM %  NET I/O   BLOCK I/O
# a1b2c3d4e5f6  my-next-app 0.50%  128MiB / 512MiB    25.00% 1.2kB/0B  0B/0B

# 특정 컨테이너만 모니터링 (스트리밍 중지: --no-stream)
docker stats --no-stream my-next-app
```

---

## 5. PID 1 문제와 시그널 처리

### 5.1 리눅스에서 PID 1의 특수한 역할

리눅스 시스템에서 PID 1은 init(*Init Process - 시스템 부팅 시 커널이 가장 먼저 시작하는 프로세스*) 프로세스다. PID 1은 두 가지 특수한 책임을 가진다.

1. **시그널 처리**: PID 1은 명시적으로 시그널 핸들러를 등록하지 않으면 `SIGTERM`, `SIGINT` 등의 시그널을 **무시**한다. 일반 프로세스(PID 1이 아닌)는 기본 핸들러가 있어서 `SIGTERM`을 받으면 종료하지만, PID 1은 그렇지 않다.

2. **좀비 프로세스 수확(reaping)**: 자식 프로세스가 종료되면 부모가 `wait()` 시스템 콜로 종료 상태를 수거해야 한다. 부모가 이를 하지 않으면 자식은 좀비 프로세스(*Zombie Process - 실행은 끝났지만 프로세스 테이블에서 제거되지 않은 프로세스*)로 남는다. PID 1은 고아가 된 모든 프로세스의 양부모 역할을 하므로, 좀비를 수확할 책임이 있다.

### 5.2 컨테이너에서의 PID 1 문제

컨테이너의 메인 프로세스는 PID 1이 된다. Node.js 프로세스가 PID 1로 실행되면 두 가지 문제가 발생한다.

**문제 1: SIGTERM을 못 받을 수 있다**

```dockerfile
# 나쁜 예: shell form — sh가 PID 1, node는 PID 1이 아님
CMD npm start
# sh -c "npm start" → sh(PID 1) → npm → node(PID ~20)
# docker stop 시 sh에 SIGTERM 전송 → sh는 자식에게 전달하지 않음 → 10초 후 SIGKILL
```

```dockerfile
# 좋은 예: exec form — node가 직접 PID 1
CMD ["node", "server.js"]
# node(PID 1) — SIGTERM을 직접 받을 수 있음
```

**문제 2: Node.js는 좀비를 수확하지 않는다**

```typescript
// Node.js에서 자식 프로세스를 생성하는 경우
import { spawn } from 'child_process';

// 이미지 리사이징 등 CPU 집약적 작업을 자식 프로세스로 처리
const child = spawn('node', ['worker.js']);
// worker.js가 비정상 종료되면 좀비가 될 수 있다
// Node.js(PID 1)는 init처럼 자동으로 좀비를 수확하지 않는다
```

### 5.3 Node.js의 SIGTERM 처리

Node.js 프로세스가 PID 1로 실행될 때는, 반드시 시그널 핸들러를 등록해야 `docker stop`이 정상 작동한다.

```typescript
import http from 'http';

const server = http.createServer((req, res) => {
  res.writeHead(200);
  res.end('Hello from Next.js');
});

server.listen(3000, () => {
  console.log('Server running on port 3000');
});

// SIGTERM 핸들러 등록 — docker stop 시 호출됨
process.on('SIGTERM', () => {
  console.log('SIGTERM received. Starting graceful shutdown...');

  server.close(() => {
    console.log('HTTP server closed. Cleaning up...');
    // DB 커넥션 풀 정리, 진행 중인 작업 완료 등
    process.exit(0);
  });

  // 강제 종료 타이머 (서버가 닫히지 않는 경우 대비)
  setTimeout(() => {
    console.error('Forced shutdown after timeout');
    process.exit(1);
  }, 8000); // docker stop의 10초보다 짧게 설정
});

// SIGINT 핸들러 (Ctrl+C)
process.on('SIGINT', () => {
  console.log('SIGINT received. Shutting down...');
  process.exit(0);
});
```

Next.js에서는 `next start`가 내부적으로 SIGTERM 핸들러를 등록하므로, 커스텀 서버를 사용하지 않는 한 별도 처리가 필요 없다. 하지만 커스텀 서버를 사용한다면 위 패턴을 적용해야 한다.

### 5.4 해결책 1: tini

tini(*Tini - 컨테이너용 경량 init 프로세스*)는 Docker 공식 권장 init 프로세스다. PID 1로 실행되어 시그널 전달과 좀비 수확을 담당한다.

```dockerfile
# Dockerfile에서 tini 사용
FROM node:20-alpine
RUN apk add --no-cache tini

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["node", "server.js"]
```

```
tini(PID 1) → node server.js(PID ~2)
```

tini는 다음을 수행한다:
- `SIGTERM`을 받으면 자식 프로세스(node)에게 전달
- 자식 프로세스가 종료되면 자신도 같은 exit code로 종료
- 좀비 프로세스를 자동으로 수확

### 5.5 해결책 2: dumb-init

dumb-init은 Yelp에서 만든 또 다른 경량 init 프로세스다. tini와 유사한 역할을 한다.

```dockerfile
FROM node:20-alpine
RUN apk add --no-cache dumb-init

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "server.js"]
```

### 5.6 해결책 3: docker run --init

tini를 이미지에 설치하지 않고도 `--init` 플래그로 Docker 내장 tini를 사용할 수 있다.

```bash
# Docker 내장 tini 사용
docker run --init -d -p 3000:3000 my-next-app
# Docker가 자동으로 tini를 PID 1로 주입
```

이 방법은 이미지를 수정할 수 없을 때 유용하다. 단, Kubernetes 환경에서는 `--init` 플래그를 직접 사용할 수 없으므로, Dockerfile에 tini를 설치하는 방법이 더 범용적이다.

> **핵심 통찰**: Node.js 컨테이너에서 PID 1 문제를 무시하면 `docker stop`이 항상 10초 후 SIGKILL로 끝나게 된다. 이는 진행 중인 HTTP 요청이 갑자기 끊기고, 데이터베이스 트랜잭션이 롤백되며, 파일 쓰기가 불완전해지는 등의 문제를 일으킨다. tini 또는 dumb-init을 사용하거나, exec form CMD + SIGTERM 핸들러를 조합하라.

---

## 6. 컨테이너 조회 및 디버깅

### 6.1 컨테이너 목록 조회

```bash
# 실행 중인 컨테이너만
docker ps

# 모든 컨테이너 (Stopped 포함)
docker ps -a

# 필터링
docker ps --filter "status=running"
docker ps --filter "name=next"
docker ps --filter "ancestor=node:20-alpine"  # 특정 이미지에서 생성된 컨테이너

# 출력 포맷 커스터마이징
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### 6.2 로그 확인

```bash
# 전체 로그
docker logs my-next-app

# 실시간 로그 스트리밍 (tail -f와 유사)
docker logs -f my-next-app

# 마지막 100줄만
docker logs --tail 100 my-next-app

# 타임스탬프 포함
docker logs -t my-next-app

# 특정 시간 이후 로그
docker logs --since 2024-01-01T00:00:00 my-next-app
docker logs --since 30m my-next-app  # 최근 30분
```

### 6.3 실행 중인 컨테이너에 접속

```bash
# 셸 접속 (인터랙티브 모드)
docker exec -it my-next-app sh
# Alpine 이미지는 bash가 없으므로 sh 사용

# 단일 명령 실행
docker exec my-next-app ls /app
docker exec my-next-app cat /app/package.json

# 환경변수 확인
docker exec my-next-app env

# Node.js REPL 접속
docker exec -it my-next-app node
```

### 6.4 상세 정보 조회

```bash
# 컨테이너의 전체 메타데이터 (JSON)
docker inspect my-next-app

# 특정 필드만 추출 (Go 템플릿)
docker inspect --format '{{.State.Status}}' my-next-app
docker inspect --format '{{.NetworkSettings.IPAddress}}' my-next-app
docker inspect --format '{{json .Config.Env}}' my-next-app
docker inspect --format '{{.State.Pid}}' my-next-app  # 호스트에서의 PID
```

### 6.5 프로세스 및 리소스 모니터링

```bash
# 컨테이너 내 프로세스 목록
docker top my-next-app

# 실시간 리소스 사용량 (CPU, 메모리, 네트워크, 디스크 I/O)
docker stats
docker stats my-next-app  # 특정 컨테이너만
docker stats --no-stream   # 한 번만 출력하고 종료
```

### 6.6 파일 복사 및 변경사항 확인

```bash
# 컨테이너 → 호스트 파일 복사
docker cp my-next-app:/app/package.json ./package-from-container.json

# 호스트 → 컨테이너 파일 복사
docker cp ./config.json my-next-app:/app/config.json

# 컨테이너의 파일시스템 변경사항 확인
docker diff my-next-app
# A /app/logs/access.log    (Added)
# C /app                     (Changed)
# D /app/tmp/cache.txt       (Deleted)
```

> **실무 팁**: `docker cp`와 `docker diff`는 "컨테이너 안에서 무슨 일이 일어나고 있는가"를 이해할 때 매우 유용하다. 특히 프로덕션에서 이상 동작이 발생했을 때, `docker exec`로 들어가 로그 파일을 `docker cp`로 꺼내오는 것은 일반적인 디버깅 패턴이다.

---

## 7. 실행 옵션 상세

### 7.1 실행 모드

```bash
# -d (detached): 백그라운드 실행
docker run -d --name my-app my-next-app
# 컨테이너 ID만 출력하고 터미널 제어권 반환

# -it (interactive + tty): 포그라운드 인터랙티브 모드
docker run -it node:20-alpine sh
# -i: 표준 입력(stdin)을 열어둠
# -t: pseudo-TTY 할당 (터미널 색상, 줄 편집 등)
```

### 7.2 포트 매핑과 볼륨 마운트 (간략)

```bash
# -p (포트 매핑) — Ch 6에서 상세
docker run -d -p 3000:3000 my-next-app                    # 호스트 3000 → 컨테이너 3000
docker run -d -p 127.0.0.1:3000:3000 my-next-app          # localhost에서만 접근 가능
docker run -d -p 8080:3000 my-next-app                     # 호스트 8080 → 컨테이너 3000

# -v (볼륨 마운트) — Ch 5에서 상세
docker run -d -v my-data:/app/data my-next-app             # 네임드 볼륨
docker run -d -v $(pwd)/src:/app/src my-next-app           # 바인드 마운트
```

### 7.3 컨테이너 이름

```bash
# --name: 컨테이너에 사람이 읽을 수 있는 이름 부여
docker run -d --name my-next-app-prod my-next-app

# 이름은 고유해야 함 — 같은 이름으로 두 번째 컨테이너를 만들면 에러
docker run -d --name my-next-app-prod my-next-app
# Error: Conflict. The container name "/my-next-app-prod" is already in use.

# 이름을 지정하지 않으면 Docker가 랜덤 이름을 생성 (예: quirky_einstein)
```

### 7.4 환경변수

```bash
# -e / --env: 개별 환경변수 전달
docker run -d \
  -e NODE_ENV=production \
  -e DATABASE_URL=postgresql://db:5432/app \
  -e NEXT_PUBLIC_API_URL=https://api.example.com \
  my-next-app

# --env-file: 파일에서 환경변수 일괄 로드
docker run -d --env-file .env.production my-next-app
```

`.env.production` 파일 형식:

```bash
NODE_ENV=production
DATABASE_URL=postgresql://db:5432/app
NEXT_PUBLIC_API_URL=https://api.example.com
# 주석 가능
# 빈 줄 무시
```

> **실무 팁**: 비밀 정보(API 키, DB 비밀번호)를 `-e` 플래그로 전달하면 `docker inspect`로 누구나 확인할 수 있다. 프로덕션에서는 Docker Secrets(Swarm) 또는 외부 비밀 관리 시스템을 사용하라.

### 7.5 재시작 정책

```bash
# --restart: 컨테이너 종료 시 자동 재시작 정책
docker run -d --restart=no my-next-app           # 기본값: 재시작하지 않음
docker run -d --restart=always my-next-app        # 항상 재시작 (Docker 데몬 시작 시에도)
docker run -d --restart=unless-stopped my-next-app # always와 유사하나, 수동 stop 후 데몬 재시작 시 제외
docker run -d --restart=on-failure:5 my-next-app  # exit code가 0이 아닐 때만, 최대 5회 재시작
```

| 정책 | 비정상 종료 시 | 정상 종료 시 | 데몬 재시작 시 |
|------|--------------|-------------|--------------|
| `no` | 재시작 안 함 | 재시작 안 함 | 재시작 안 함 |
| `always` | 재시작 | 재시작 | 재시작 |
| `unless-stopped` | 재시작 | 재시작 | 수동 stop이면 안 함 |
| `on-failure:N` | 최대 N회 재시작 | 재시작 안 함 | 재시작 안 함 |

### 7.6 --init 플래그

```bash
# Docker 내장 tini를 PID 1로 주입
docker run --init -d -p 3000:3000 my-next-app
# 섹션 5에서 설명한 PID 1 문제를 해결하는 가장 간단한 방법
```

---

## 자주 하는 실수

| 실수 | 문제점 | 올바른 방법 |
|------|--------|------------|
| `docker stop`의 10초 타임아웃을 모름 | 그레이스풀 셧다운이 10초 안에 끝나지 않으면 SIGKILL로 강제 종료 | `-t` 옵션으로 타임아웃 조정, 애플리케이션의 셧다운 시간 확인 |
| PID 1 문제를 무시 | `docker stop` 시 SIGTERM이 전달되지 않아 항상 10초 대기 후 SIGKILL | tini/dumb-init 사용 또는 exec form CMD + SIGTERM 핸들러 |
| 메모리 제한 없이 실행 | Node.js가 호스트 전체 메모리를 기준으로 힙을 잡아 OOM 위험 | `--memory` + `--max-old-space-size` 동기화 |
| 컨테이너 내부를 직접 수정하고 유지 기대 | R/W 레이어 변경은 컨테이너 삭제 시 사라짐 | Dockerfile을 수정하고 이미지를 재빌드 |
| `--rm` 없이 학습용 컨테이너 실행 | Stopped 상태 컨테이너가 계속 쌓여 디스크 낭비 | 일회성 실행 시 항상 `--rm` 사용 |
| shell form CMD로 Node.js 실행 | sh가 PID 1이 되어 시그널이 node에 전달되지 않음 | exec form `CMD ["node", "server.js"]` 사용 |
| `-e`로 비밀 정보 전달 | `docker inspect`로 환경변수가 평문 노출 | Docker Secrets 또는 외부 비밀 관리 사용 |

---

## 명령어 레퍼런스

| 명령어 | 설명 | 예시 |
|--------|------|------|
| `docker run` | 컨테이너 생성 + 실행 | `docker run -d -p 3000:3000 --name app my-next-app` |
| `docker create` | 컨테이너 생성만 (실행 안 함) | `docker create --name app my-next-app` |
| `docker start` | Stopped/Created 컨테이너 시작 | `docker start app` |
| `docker stop` | SIGTERM → 대기 → SIGKILL | `docker stop -t 30 app` |
| `docker kill` | 즉시 SIGKILL | `docker kill app` |
| `docker restart` | stop + start | `docker restart app` |
| `docker rm` | 컨테이너 삭제 | `docker rm app` / `docker rm -f app` (강제) |
| `docker ps` | 컨테이너 목록 | `docker ps -a --filter "status=exited"` |
| `docker logs` | 로그 출력 | `docker logs -f --tail 100 app` |
| `docker exec` | 실행 중인 컨테이너에서 명령 실행 | `docker exec -it app sh` |
| `docker inspect` | 상세 메타데이터 (JSON) | `docker inspect --format '{{.State.Pid}}' app` |
| `docker top` | 컨테이너 내 프로세스 목록 | `docker top app` |
| `docker stats` | 실시간 리소스 사용량 | `docker stats --no-stream app` |
| `docker cp` | 호스트 ↔ 컨테이너 파일 복사 | `docker cp app:/app/log.txt ./log.txt` |
| `docker diff` | 컨테이너 파일시스템 변경사항 | `docker diff app` |
| `docker pause` | 프로세스 일시 중지 | `docker pause app` |
| `docker unpause` | 일시 중지 해제 | `docker unpause app` |

---

## 요약

- **컨테이너는 VM이 아니라 격리된 프로세스**다. 이미지의 R/O 레이어 위에 R/W 레이어를 얹어 생성된다.
- **생명주기**: Created → Running → Paused → Stopped → Removed. `docker stop`은 SIGTERM 후 10초 대기, `docker kill`은 즉시 SIGKILL이다.
- **네임스페이스**는 "무엇을 볼 수 있는가"(PID, Network, Mount, UTS, IPC, User)를 격리하고, **cgroups**는 "얼마나 사용할 수 있는가"(CPU, 메모리)를 제한한다.
- **PID 1 문제**는 Node.js 컨테이너에서 가장 흔한 함정이다. tini/dumb-init을 사용하거나, exec form CMD + SIGTERM 핸들러를 조합하여 해결한다.
- **Node.js 메모리**: 컨테이너의 `--memory` 제한과 V8의 `--max-old-space-size`를 반드시 동기화하라.
- 컨테이너 내부 수정은 일시적이다. 영속적인 변경은 Dockerfile을 수정하고 이미지를 재빌드해야 한다.
- 디버깅 도구: `docker logs`, `docker exec`, `docker inspect`, `docker stats`, `docker cp`, `docker diff`를 상황에 맞게 조합하라.

---

## 다른 챕터와의 관계

- **Ch 1 (Docker Engine 아키텍처)**: runc가 컨테이너 생성 시 네임스페이스와 cgroups를 설정하는 주체임을 배웠다. 이 챕터에서는 그 결과로 컨테이너가 어떤 격리를 얻는지 확인했다.
- **Ch 2 (이미지)**: 이미지의 R/O 레이어 스택 위에 R/W 레이어가 추가되어 컨테이너가 되는 구조를 다시 확인했다. CoW 전략으로 여러 컨테이너가 동일 이미지 레이어를 공유한다.
- **Ch 4 (Dockerfile)**: CMD/ENTRYPOINT의 shell form vs exec form이 PID 1에 미치는 영향을 여기서 다루었다. Ch 4에서 더 깊이 다룬다.
- **Ch 5 (볼륨과 바인드 마운트)**: 컨테이너의 R/W 레이어는 컨테이너 삭제 시 사라진다. 데이터를 영속적으로 유지하려면 볼륨을 사용해야 하며, 이는 Ch 5의 주제다.
- **Ch 6 (네트워킹)**: Network 네임스페이스로 격리된 컨테이너들이 어떻게 통신하는지, 포트 매핑과 Docker 네트워크의 동작을 Ch 6에서 다룬다.
- **Ch 11 (로깅과 모니터링)**: `docker logs`와 `docker stats`는 이 챕터에서 기본만 다루었다. 프로덕션 수준의 로깅 드라이버, 메트릭 수집, 모니터링 스택은 Ch 11에서 심화한다.
- **Ch 12 (Node.js 최적화)**: PID 1 + tini 패턴, 메모리 제한과 V8 힙 동기화, 그레이스풀 셧다운 패턴을 프로덕션 수준으로 완성하는 내용은 Ch 12에서 다룬다.
