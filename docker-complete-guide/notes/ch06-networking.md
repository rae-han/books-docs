# Chapter 6: 컨테이너 네트워킹: Networking

## 핵심 질문

컨테이너는 어떻게 외부 세계 및 다른 컨테이너와 통신하는가? Docker의 네트워크 드라이버별 차이는 무엇이고, 프론트엔드-백엔드 컨테이너 간 통신은 어떻게 설정하는가?

---

## 1. Docker 네트워킹 기초

### 컨테이너의 네트워크 격리

Ch 3에서 다룬 네트워크 네임스페이스(*Network Namespace - 리눅스 커널이 제공하는 네트워크 스택 격리 기술*)를 복습하자. Docker는 각 컨테이너마다 독립된 네트워크 네임스페이스를 생성한다. 이로 인해 각 컨테이너는 다음을 독립적으로 보유한다:

- **자체 IP 주소**: 같은 호스트의 다른 컨테이너와 다른 IP를 할당받는다
- **독립된 포트 범위**: 두 컨테이너가 동시에 내부적으로 포트 3000을 사용해도 충돌하지 않는다
- **자체 라우팅 테이블**: 네트워크 트래픽 경로를 독립적으로 관리한다
- **독립된 iptables 규칙**: 방화벽 규칙이 컨테이너별로 분리된다

이 격리 덕분에 컨테이너는 마치 별도의 물리 서버처럼 네트워크를 사용할 수 있다.

```bash
# 컨테이너의 네트워크 설정 확인
docker run --rm alpine ip addr show
# eth0에 할당된 IP 주소를 확인할 수 있다

# 호스트의 네트워크와 비교
ip addr show  # 또는 macOS에서 ifconfig
```

### CNM(Container Network Model)

Docker의 네트워크 아키텍처는 CNM(*Container Network Model - Docker가 정의한 네트워킹 설계 명세*)을 기반으로 한다. CNM은 세 가지 핵심 구성 요소로 이루어진다:

| 구성 요소 | 설명 | 비유 |
|-----------|------|------|
| **Sandbox** | 컨테이너의 전체 네트워크 스택 (인터페이스, 라우팅 테이블, DNS 설정 등) | 컨테이너의 "네트워크 방" |
| **Endpoint** | Sandbox를 Network에 연결하는 가상 네트워크 인터페이스 | "네트워크 케이블" |
| **Network** | Endpoint들이 서로 통신할 수 있는 그룹 | "스위치" 또는 "서브넷" |

하나의 컨테이너(Sandbox)는 여러 Endpoint를 가질 수 있고, 각 Endpoint는 서로 다른 Network에 연결될 수 있다. 이는 하나의 서버가 여러 네트워크 카드를 가지는 것과 같은 원리다.

```
┌─────────────────────────────────────────────┐
│                  Docker Host                 │
│                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Container1│  │Container2│  │Container3│   │
│  │(Sandbox) │  │(Sandbox) │  │(Sandbox) │   │
│  └────┬─────┘  └────┬─────┘  └─┬────┬───┘   │
│       │              │          │    │        │
│  (Endpoint)    (Endpoint)  (EP)  (EP)        │
│       │              │          │    │        │
│  ┌────┴──────────────┴──────────┘    │       │
│  │       Network A (bridge)     │    │       │
│  └──────────────────────────────┘    │       │
│                               ┌──────┘       │
│                               │Network B│    │
│                               └─────────┘    │
└─────────────────────────────────────────────┘
```

Container3은 Network A와 Network B 모두에 연결되어 있어, 양쪽 네트워크의 컨테이너와 모두 통신할 수 있다.

> **핵심 통찰**: CNM의 핵심 가치는 **플러그형 네트워킹**이다. 드라이버만 교체하면 같은 CNM 모델 위에서 bridge, overlay, macvlan 등 전혀 다른 네트워킹 방식을 사용할 수 있다.

---

## 2. 네트워크 드라이버

Docker는 여러 네트워크 드라이버를 제공하며, 각각 다른 사용 사례에 최적화되어 있다.

### bridge (기본 드라이버)

브리지(*Bridge - 가상 네트워크 스위치 역할을 하는 소프트웨어 장치*)는 Docker의 기본 네트워크 드라이버다. 단일 호스트 내에서 컨테이너 간 통신을 가능하게 한다.

Docker를 설치하면 `docker0`이라는 기본 브리지 네트워크가 자동 생성된다. `--network` 옵션 없이 컨테이너를 실행하면 이 기본 브리지에 연결된다.

```bash
# 기본 브리지 네트워크 확인
docker network ls
# NETWORK ID     NAME      DRIVER    SCOPE
# a1b2c3d4e5f6   bridge    bridge    local
# f6e5d4c3b2a1   host      host      local
# 1a2b3c4d5e6f   none      null      local

# 기본 브리지 상세 정보
docker network inspect bridge
```

#### 기본 bridge vs 사용자 정의 bridge

이 구분은 Docker 네트워킹에서 가장 중요한 개념 중 하나다.

| 특성 | 기본 bridge | 사용자 정의 bridge |
|------|-------------|-------------------|
| DNS 해석 | 불가 (IP만 사용 가능) | **컨테이너 이름으로 통신 가능** |
| 컨테이너 격리 | 모든 컨테이너가 같은 네트워크 | 필요한 컨테이너만 선택적 연결 |
| 환경변수 공유 | `--link`로 가능 (레거시) | 불필요 (DNS 사용) |
| 실행 중 연결/해제 | 불가 | `docker network connect/disconnect` 가능 |

> **핵심 통찰**: 사용자 정의 bridge 네트워크에서는 **컨테이너 이름이 곧 호스트명**이 된다. `http://my-api:4000`처럼 컨테이너 이름으로 직접 통신할 수 있다. 기본 bridge에서는 이것이 불가능하다.

```bash
# 사용자 정의 bridge 네트워크 생성
docker network create my-app-network

# 네트워크를 지정하여 컨테이너 실행
docker run -d --name api --network my-app-network node:20-alpine sleep 3600
docker run -d --name web --network my-app-network node:20-alpine sleep 3600

# web 컨테이너에서 api 컨테이너로 DNS를 통한 통신 확인
docker exec web ping api
# PING api (172.18.0.2): 56 data bytes
# 64 bytes from 172.18.0.2: seq=0 ttl=64 time=0.095 ms

# 기본 bridge에서는 같은 시도가 실패한다
docker run -d --name api2 node:20-alpine sleep 3600
docker run -d --name web2 node:20-alpine sleep 3600
docker exec web2 ping api2
# ping: bad address 'api2'  ← DNS 해석 실패!
```

#### 서브넷과 게이트웨이 지정

```bash
# 서브넷과 게이트웨이를 명시적으로 설정한 네트워크 생성
docker network create \
  --driver bridge \
  --subnet 172.20.0.0/16 \
  --gateway 172.20.0.1 \
  my-custom-network

# 컨테이너에 고정 IP 할당
docker run -d \
  --name api \
  --network my-custom-network \
  --ip 172.20.0.10 \
  node:20-alpine sleep 3600
```

### host 드라이버

호스트 네트워크 드라이버는 컨테이너와 호스트 간의 네트워크 격리를 제거한다. 컨테이너가 호스트의 네트워크 스택을 직접 사용하므로 포트 매핑이 불필요하다.

```bash
# host 네트워크로 컨테이너 실행
docker run -d --name api --network host node:20-alpine node -e "
  require('http').createServer((req, res) => {
    res.end('Hello from host network');
  }).listen(4000);
"
# 포트 매핑 없이 바로 localhost:4000으로 접근 가능
```

**장점**:
- NAT(*Network Address Translation - 네트워크 주소 변환*) 오버헤드가 없어 네트워크 성능이 최적이다
- 포트 매핑 설정이 불필요하다

**주의사항**:
- 네트워크 격리가 없으므로 보안이 취약하다
- 같은 포트를 사용하는 여러 컨테이너를 동시에 실행할 수 없다
- **macOS/Windows에서는 Docker Desktop이 VM 위에서 실행되므로**, `--network host`는 VM 내부의 호스트 네트워크를 의미한다. 즉, macOS/Windows에서는 `--network host`가 기대한 대로 동작하지 않는 경우가 많다

> **실무 팁**: macOS에서 개발할 때는 `--network host` 대신 명시적 포트 매핑(`-p`)을 사용하는 것이 안전하다. 프로덕션 Linux 서버에서만 host 네트워크의 성능 이점을 누릴 수 있다.

### none 드라이버

네트워크를 완전히 비활성화한다. 외부 통신이 일절 불가능하며, loopback 인터페이스만 존재한다.

```bash
docker run --rm --network none alpine ip addr show
# lo (loopback)만 표시된다. eth0이 없다.

docker run --rm --network none alpine ping google.com
# ping: bad address 'google.com'  ← 외부 통신 불가
```

**사용 사례**:
- 민감한 데이터를 처리하는 배치 작업 (네트워크 유출 방지)
- 테스트 시 네트워크 의존성 제거

### overlay 드라이버

오버레이 네트워크는 여러 Docker 호스트에 걸쳐 컨테이너 간 통신을 가능하게 한다. Docker Swarm이나 Kubernetes 환경에서 주로 사용된다.

```bash
# Docker Swarm 모드에서 overlay 네트워크 생성
docker network create --driver overlay my-overlay-network
```

단일 호스트 개발 환경에서는 거의 사용하지 않으므로 이 챕터에서는 개념만 소개한다.

### macvlan 드라이버

맥브이랜(*macvlan - 컨테이너에 물리 네트워크의 실제 MAC 주소를 할당하는 드라이버*)은 컨테이너가 물리 네트워크에 직접 연결된 것처럼 보이게 한다.

```bash
docker network create -d macvlan \
  --subnet=192.168.1.0/24 \
  --gateway=192.168.1.1 \
  -o parent=eth0 \
  my-macvlan-network
```

레거시 시스템과의 통합이나 네트워크 모니터링 도구 사용 시 유용하지만, 일반적인 웹 애플리케이션에서는 거의 사용하지 않는다.

### 네트워크 드라이버 비교

| 드라이버 | 범위 | DNS 지원 | 격리 수준 | 성능 | 주요 사용 사례 |
|---------|------|---------|----------|------|--------------|
| bridge (기본) | 단일 호스트 | 불가 | 중간 | 좋음 | 테스트, 간단한 실행 |
| bridge (사용자 정의) | 단일 호스트 | **지원** | 높음 | 좋음 | **개발/프로덕션 권장** |
| host | 단일 호스트 | N/A | 없음 | **최고** | 고성능 필요 시 |
| none | N/A | N/A | **최고** | N/A | 보안 격리 |
| overlay | **다중 호스트** | 지원 | 높음 | 보통 | Swarm/K8s 클러스터 |
| macvlan | 단일 호스트 | 불가 | 높음 | 좋음 | 레거시 통합 |

---

## 3. 포트 매핑 (-p)

컨테이너 내부의 포트는 기본적으로 외부에서 접근할 수 없다. 포트 매핑(*Port Mapping - 호스트의 포트를 컨테이너 내부 포트에 연결하는 것*)을 통해 외부에서 컨테이너 서비스에 접근할 수 있게 한다.

### 포트 매핑 문법

```bash
# 기본: 호스트포트:컨테이너포트
docker run -d -p 3000:3000 --name web my-next-app
# 호스트의 3000번 포트 → 컨테이너의 3000번 포트

# 호스트와 컨테이너 포트가 다른 경우
docker run -d -p 8080:3000 --name web my-next-app
# 호스트의 8080번 포트 → 컨테이너의 3000번 포트

# 특정 인터페이스에만 바인딩
docker run -d -p 127.0.0.1:3000:3000 --name web my-next-app
# localhost에서만 접근 가능 (외부 네트워크에서 접근 불가)

# 랜덤 호스트 포트 할당
docker run -d -p 3000 --name web my-next-app
# 호스트의 랜덤 포트 → 컨테이너의 3000번 포트
docker port web  # 할당된 포트 확인

# EXPOSE된 모든 포트에 랜덤 포트 매핑
docker run -d -P --name web my-next-app
# Dockerfile의 EXPOSE에 선언된 모든 포트에 랜덤 포트 매핑
```

### 여러 포트 동시 매핑

```bash
# Next.js 개발 서버 + 디버거 포트
docker run -d \
  -p 3000:3000 \
  -p 9229:9229 \
  --name web my-next-app

# 포트 범위 매핑
docker run -d -p 8000-8010:8000-8010 --name multi-port-app my-app
```

### UDP 포트 매핑

```bash
# UDP 프로토콜 명시
docker run -d -p 5353:53/udp --name dns my-dns-server

# TCP와 UDP 동시
docker run -d -p 3000:3000/tcp -p 3000:3000/udp --name app my-app
```

### 포트 충돌 해결

```bash
# 이미 3000번 포트를 사용하는 컨테이너가 있을 때
docker run -d -p 3000:3000 --name web2 my-next-app
# Error: Bind for 0.0.0.0:3000 failed: port is already allocated

# 해결 방법 1: 다른 호스트 포트 사용
docker run -d -p 3001:3000 --name web2 my-next-app

# 해결 방법 2: 어떤 프로세스가 포트를 점유하는지 확인
lsof -i :3000  # macOS/Linux
docker ps --format "{{.Names}}: {{.Ports}}" | grep 3000
```

> **실무 팁**: 프로덕션에서 `127.0.0.1`에만 바인딩하고, 리버스 프록시(Nginx 등)를 통해 외부 트래픽을 처리하는 것이 보안상 권장된다. `-p 3000:3000`은 기본적으로 `0.0.0.0:3000:3000`과 동일하여 모든 네트워크 인터페이스에서 접근 가능하다.

---

## 4. Docker DNS와 서비스 디스커버리

### 내장 DNS 서버

사용자 정의 네트워크에 연결된 컨테이너들은 Docker의 내장 DNS 서버(127.0.0.11)를 자동으로 사용한다. 이 DNS 서버는 같은 네트워크에 있는 다른 컨테이너의 이름을 IP 주소로 해석해 준다.

```bash
# 사용자 정의 네트워크 생성
docker network create app-network

# API 서버 실행
docker run -d --name api --network app-network node:20-alpine sh -c "
  node -e \"
    const http = require('http');
    http.createServer((req, res) => {
      res.writeHead(200, {'Content-Type': 'application/json'});
      res.end(JSON.stringify({ message: 'Hello from API' }));
    }).listen(4000, () => console.log('API running on :4000'));
  \"
"

# 다른 컨테이너에서 컨테이너 이름으로 접근
docker run --rm --network app-network node:20-alpine sh -c "
  wget -qO- http://api:4000
"
# {"message":"Hello from API"}
```

### 네트워크 별칭 (Network Alias)

하나의 컨테이너에 여러 DNS 이름을 부여하거나, 여러 컨테이너를 하나의 이름으로 묶을 수 있다.

```bash
# 네트워크 별칭 부여
docker run -d \
  --name api-v1 \
  --network app-network \
  --network-alias api \
  my-api:v1

docker run -d \
  --name api-v2 \
  --network app-network \
  --network-alias api \
  my-api:v2

# "api"로 요청하면 api-v1, api-v2 중 하나로 라운드 로빈 분배
docker run --rm --network app-network node:20-alpine sh -c "
  nslookup api
"
# Name:      api
# Address 1: 172.18.0.2  ← api-v1
# Address 2: 172.18.0.3  ← api-v2
```

### DNS 라운드 로빈

위 예시에서 볼 수 있듯이, 같은 네트워크 별칭을 가진 여러 컨테이너가 있으면 DNS 라운드 로빈(*DNS Round Robin - DNS 조회 시 여러 IP를 순환하며 반환하는 간단한 부하 분산 방식*)으로 요청이 분배된다. 이는 간단한 로드 밸런싱에 활용할 수 있다.

> **핵심 통찰**: Docker의 DNS 라운드 로빈은 간단한 서비스 디스커버리를 제공하지만, 헬스 체크나 가중치 기반 라우팅을 지원하지 않는다. 프로덕션에서는 Nginx, HAProxy, 또는 Kubernetes의 Service를 사용하는 것이 적절하다.

---

## 5. 프론트엔드-백엔드 컨테이너 간 통신 실전

### 아키텍처 개요

실전에서 가장 흔한 구성인 Next.js + Express API + PostgreSQL 3계층 아키텍처를 Docker 네트워크로 구성해 보자.

```
┌─────────────────────────────────────────────────┐
│                 Docker Host                      │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │
│  │  next-web │  │   api    │  │   postgres   │   │
│  │  :3000    │  │  :4000   │  │   :5432      │   │
│  └────┬──┬──┘  └────┬─────┘  └──────┬───────┘   │
│       │  │          │               │            │
│  -p 3000 │     -p 4000              │            │
│       │  │          │               │            │
│  ┌────┴──┴──────────┴───────────────┴─────────┐  │
│  │            app-network (bridge)            │  │
│  └────────────────────────────────────────────┘  │
│                                                  │
└─────────────────────────────────────────────────┘
         │            │
    호스트:3000   호스트:4000
         │            │
    ┌────┴────────────┴────┐
    │      브라우저          │
    └──────────────────────┘
```

### 단계별 구축

**1단계: 네트워크 생성**

```bash
docker network create app-network
```

**2단계: PostgreSQL 실행**

```bash
docker run -d \
  --name postgres \
  --network app-network \
  -e POSTGRES_USER=app \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=myapp \
  -v pgdata:/var/lib/postgresql/data \
  postgres:16-alpine
```

PostgreSQL은 포트 매핑을 하지 않았다. 외부에서 직접 접근할 필요가 없고, 같은 네트워크의 API 컨테이너에서만 접근하면 되기 때문이다.

**3단계: Express API 서버 실행**

```bash
docker run -d \
  --name api \
  --network app-network \
  -p 4000:4000 \
  -e DATABASE_URL=postgresql://app:secret@postgres:5432/myapp \
  my-express-api
```

`DATABASE_URL`에서 호스트 부분이 `postgres`인 것에 주목하자. 이것이 Docker DNS를 통해 PostgreSQL 컨테이너로 해석된다.

**4단계: Next.js 프론트엔드 실행**

```bash
docker run -d \
  --name next-web \
  --network app-network \
  -p 3000:3000 \
  -e INTERNAL_API_URL=http://api:4000 \
  -e NEXT_PUBLIC_API_URL=http://localhost:4000 \
  my-next-app
```

### SSR과 CSR에서의 API URL 차이

이 부분은 Docker 네트워크에서 Next.js를 사용할 때 가장 흔히 발생하는 혼란이다.

```
┌─────────────────────────────────────────────────────────────┐
│                     브라우저 (클라이언트)                       │
│                                                             │
│  fetch('http://localhost:4000/api/users')                   │
│         │                                                   │
│         │  ← 브라우저는 Docker 네트워크 밖에 있다.              │
│         │     "api"라는 호스트명을 알 수 없다.                  │
│         │     localhost:4000 → 호스트의 포트 매핑을 통해 접근    │
│         ▼                                                   │
└─────────┬───────────────────────────────────────────────────┘
          │
     호스트:4000 → 컨테이너 api:4000
          │
┌─────────┴───────────────────────────────────────────────────┐
│                     Docker 네트워크 내부                      │
│                                                             │
│  Next.js SSR에서:                                           │
│  fetch('http://api:4000/api/users')                         │
│         │                                                   │
│         │  ← Next.js 서버는 Docker 네트워크 안에 있다.         │
│         │     "api"를 Docker DNS로 해석할 수 있다.             │
│         ▼                                                   │
│       api 컨테이너 (172.18.0.3:4000)                        │
└─────────────────────────────────────────────────────────────┘
```

이 문제를 해결하는 패턴은 환경변수를 분리하는 것이다:

```typescript
// lib/api.ts
const getApiUrl = () => {
  // 서버 사이드: Docker 내부 DNS 사용
  if (typeof window === 'undefined') {
    return process.env.INTERNAL_API_URL || 'http://api:4000';
  }
  // 클라이언트 사이드: 호스트 URL 사용
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:4000';
};

export async function fetchUsers() {
  const res = await fetch(`${getApiUrl()}/api/users`);
  return res.json();
}
```

```typescript
// app/users/page.tsx (Server Component)
import { fetchUsers } from '@/lib/api';

export default async function UsersPage() {
  // 서버 사이드에서 실행 → INTERNAL_API_URL 사용 → http://api:4000
  const users = await fetchUsers();

  return (
    <div>
      {users.map((user: { id: number; name: string }) => (
        <p key={user.id}>{user.name}</p>
      ))}
    </div>
  );
}
```

```typescript
// components/UserList.tsx (Client Component)
'use client';

import { useEffect, useState } from 'react';

export default function UserList() {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    // 클라이언트 사이드에서 실행 → NEXT_PUBLIC_API_URL 사용 → http://localhost:4000
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/users`)
      .then(res => res.json())
      .then(setUsers);
  }, []);

  return <ul>{users.map((u: any) => <li key={u.id}>{u.name}</li>)}</ul>;
}
```

> **핵심 통찰**: Next.js의 Server Component/SSR은 Docker 네트워크 **내부**에서 실행되므로 컨테이너 이름(http://api:4000)을 사용해야 한다. Client Component는 브라우저에서 실행되므로 Docker 네트워크 **외부**이며, 호스트의 포트 매핑(http://localhost:4000)을 사용해야 한다.

### Docker Compose 미리보기

위의 복잡한 `docker run` 명령어들을 Ch 7에서 다룰 Docker Compose로 단순화할 수 있다:

```yaml
# docker-compose.yml (Ch 7에서 상세 설명)
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: myapp
    volumes:
      - pgdata:/var/lib/postgresql/data
    # 포트 매핑 없음 — 내부 통신만

  api:
    build: ./api
    ports:
      - "4000:4000"
    environment:
      DATABASE_URL: postgresql://app:secret@postgres:5432/myapp
    depends_on:
      - postgres

  web:
    build: ./web
    ports:
      - "3000:3000"
    environment:
      INTERNAL_API_URL: http://api:4000
      NEXT_PUBLIC_API_URL: http://localhost:4000
    depends_on:
      - api

volumes:
  pgdata:
```

Docker Compose는 자동으로 사용자 정의 bridge 네트워크를 생성하고 모든 서비스를 연결한다. 네트워크를 별도로 선언하지 않아도 된다.

---

## 6. 네트워크 디버깅

### 네트워크 관리 명령어

```bash
# 모든 네트워크 목록
docker network ls

# 네트워크 상세 정보 (연결된 컨테이너, IP 대역 등)
docker network inspect app-network

# 특정 정보만 추출
docker network inspect app-network --format '{{range .Containers}}{{.Name}}: {{.IPv4Address}}{{"\n"}}{{end}}'
# api: 172.18.0.3/16
# postgres: 172.18.0.2/16
# next-web: 172.18.0.4/16

# 네트워크 생성
docker network create --driver bridge my-network

# 실행 중인 컨테이너를 네트워크에 연결/해제
docker network connect app-network my-container
docker network disconnect app-network my-container

# 네트워크 삭제
docker network rm my-network

# 사용하지 않는 네트워크 일괄 삭제
docker network prune
```

### 컨테이너 내부에서 디버깅

```bash
# 컨테이너에서 DNS 확인
docker exec api nslookup postgres
# Server:    127.0.0.11
# Address 1: 127.0.0.11
# Name:      postgres
# Address 1: 172.18.0.2

# 컨테이너 간 연결 테스트
docker exec api ping -c 3 postgres

# HTTP 요청 테스트
docker exec next-web wget -qO- http://api:4000/health

# 포트 연결 테스트
docker exec api sh -c "nc -zv postgres 5432"
# postgres (172.18.0.2:5432) open
```

### nicolaka/netshoot 디버깅 컨테이너

프로덕션 이미지에는 보통 `ping`, `curl`, `nslookup` 같은 네트워크 도구가 포함되어 있지 않다. 이때 네트워크 디버깅 전용 컨테이너를 활용한다.

```bash
# netshoot 컨테이너를 같은 네트워크에 연결하여 디버깅
docker run -it --rm \
  --network app-network \
  nicolaka/netshoot

# netshoot 안에서 다양한 도구 사용 가능
# DNS 조회
nslookup api
dig api

# TCP 포트 스캔
nmap -p 4000 api

# HTTP 요청
curl http://api:4000/health

# 네트워크 경로 추적
traceroute api

# 패킷 캡처
tcpdump -i eth0 port 4000
```

```bash
# 특정 컨테이너의 네트워크 네임스페이스에 직접 접속하여 디버깅
docker run -it --rm \
  --network container:api \
  nicolaka/netshoot

# 이제 api 컨테이너와 동일한 네트워크 스택을 공유한다
# localhost:4000으로 api에 접근 가능
ss -tlnp  # api 컨테이너의 열린 포트 확인
```

> **실무 팁**: `nicolaka/netshoot` 이미지는 약 300MB지만, 네트워크 문제를 진단하는 데 필요한 거의 모든 도구(`curl`, `dig`, `nmap`, `tcpdump`, `iperf`, `netstat` 등)를 포함하고 있다. 프로덕션 환경에서도 문제 발생 시 임시로 실행하여 디버깅한 뒤 제거할 수 있다.

---

## 자주 하는 실수

| 실수 | 문제점 | 올바른 방법 |
|------|--------|------------|
| 기본 bridge에서 컨테이너 이름으로 통신 시도 | 기본 bridge는 DNS를 지원하지 않아 이름 해석이 실패한다 | 사용자 정의 bridge 네트워크를 생성하여 사용한다 |
| `localhost`로 다른 컨테이너에 접근 시도 | 컨테이너 내부의 `localhost`는 자기 자신만을 가리킨다 | 컨테이너 이름(예: `http://api:4000`)으로 접근한다 |
| SSR과 CSR에서 같은 API URL 사용 | SSR은 Docker 내부, CSR은 브라우저(외부)에서 실행된다 | `INTERNAL_API_URL`과 `NEXT_PUBLIC_API_URL`을 분리한다 |
| 호스트 포트 충돌 | 같은 호스트 포트에 여러 컨테이너 매핑 시 에러 발생 | 다른 호스트 포트를 사용하거나, 기존 컨테이너를 중지한다 |
| macOS에서 `--network host` 기대 | macOS의 host 네트워크는 Linux VM 내부의 호스트이다 | macOS에서는 `-p` 포트 매핑을 사용한다 |
| DB 컨테이너에 불필요한 포트 매핑 | 외부에서 DB에 직접 접근 가능해져 보안 위험 | 내부 통신만 필요하면 포트 매핑을 생략한다 |
| `--link` 사용 | Docker 공식 문서에서도 레거시로 분류된 기능이다 | 사용자 정의 네트워크와 DNS를 사용한다 |

---

## 명령어 레퍼런스

| 명령어 | 설명 | 예시 |
|--------|------|------|
| `docker network create` | 새 네트워크 생성 | `docker network create app-net` |
| `docker network ls` | 모든 네트워크 목록 | `docker network ls` |
| `docker network inspect` | 네트워크 상세 정보 | `docker network inspect app-net` |
| `docker network rm` | 네트워크 삭제 | `docker network rm app-net` |
| `docker network prune` | 미사용 네트워크 일괄 삭제 | `docker network prune -f` |
| `docker network connect` | 실행 중 컨테이너를 네트워크에 연결 | `docker network connect app-net api` |
| `docker network disconnect` | 컨테이너를 네트워크에서 해제 | `docker network disconnect app-net api` |
| `docker run --network` | 특정 네트워크에서 컨테이너 실행 | `docker run --network app-net my-img` |
| `docker run -p` | 포트 매핑 | `docker run -p 3000:3000 my-img` |
| `docker run -P` | EXPOSE 포트 전체 랜덤 매핑 | `docker run -P my-img` |
| `docker port` | 컨테이너 포트 매핑 확인 | `docker port my-container` |

---

## 요약

- Docker는 각 컨테이너에 **독립된 네트워크 네임스페이스**를 할당하여 네트워크를 격리한다.
- CNM(Container Network Model)은 Sandbox, Endpoint, Network 세 요소로 구성된다.
- **사용자 정의 bridge 네트워크**가 가장 권장되는 드라이버이며, 자동 DNS를 제공한다.
- 기본 bridge에서는 DNS가 작동하지 않으므로 반드시 사용자 정의 네트워크를 생성해야 한다.
- **포트 매핑**(`-p`)은 호스트 포트를 컨테이너 포트에 연결하여 외부 접근을 허용한다.
- Next.js 같은 SSR 프레임워크에서는 **서버 사이드 API URL(Docker 내부 DNS)과 클라이언트 사이드 API URL(호스트 포트 매핑)을 분리**해야 한다.
- 내부 서비스(DB 등)는 포트 매핑 없이 Docker 네트워크를 통해서만 접근하도록 구성하는 것이 보안상 좋다.
- `nicolaka/netshoot` 컨테이너를 활용하면 네트워크 문제를 효과적으로 디버깅할 수 있다.

---

## 다른 챕터와의 관계

| 챕터 | 관계 |
|------|------|
| **Ch 3 (컨테이너 내부 구조)** | 네트워크 네임스페이스의 원리를 이 챕터에서 실전에 적용한다 |
| **Ch 7 (Docker Compose 기초)** | 이 챕터에서 수동으로 구성한 네트워크를 Compose가 자동화한다. `docker-compose.yml`에서 서비스 이름이 곧 DNS 호스트명이 된다 |
| **Ch 8 (Docker Compose 고급)** | 다중 네트워크 구성, 프론트엔드/백엔드 네트워크 분리 등 고급 네트워크 패턴을 다룬다 |
| **Ch 10 (보안)** | 네트워크 격리를 활용한 보안 강화 전략(내부 전용 네트워크, 불필요한 포트 매핑 제거 등)을 다룬다 |
