# Chapter 1: 도커란 무엇인가: What is Docker?

## 핵심 질문

도커는 왜 등장했으며, 기존 가상화와 무엇이 다른가? 도커 엔진의 내부 아키텍처는 어떻게 구성되어 있는가?

---

## 1. 컨테이너가 필요한 이유

### 1.1 "내 컴퓨터에서는 되는데" 문제

소프트웨어 개발에서 가장 흔하고 고통스러운 문장이 있다: **"It works on my machine."** 로컬 개발 환경에서 완벽히 동작하던 애플리케이션이 스테이징 서버나 프로덕션 환경에 배포하는 순간 실패하는 현상은 거의 모든 개발팀이 경험하는 문제다.

이 문제의 근본 원인은 **환경 차이(environment drift)** 에 있다. 개발자의 로컬 머신, CI/CD 서버, 스테이징 환경, 프로덕션 서버는 각각 다른 OS 버전, 라이브러리 버전, 시스템 설정을 가지고 있다. 아무리 문서화를 철저히 해도 이 차이를 완전히 제거하기는 어렵다.

### 1.2 환경 일관성(Consistency)의 중요성

환경 일관성이란 개발부터 프로덕션까지 **모든 단계에서 동일한 실행 환경을 보장**하는 것을 의미한다. 환경 일관성이 깨지면 다음과 같은 문제가 발생한다:

- **디버깅 난이도 증가**: 버그가 코드 문제인지 환경 문제인지 구분할 수 없다
- **배포 신뢰성 하락**: "이번 배포 괜찮을까?"라는 불안이 항상 따라다닌다
- **온보딩 지연**: 새 팀원이 개발 환경을 구축하는 데 반나절~하루가 소요된다
- **"Snowflake Server" 문제**: 서버마다 미세하게 다른 설정이 누적되어 어떤 서버는 동작하고 어떤 서버는 실패한다

### 1.3 Node.js 프로젝트에서의 실제 사례

Node.js 프로젝트는 환경 차이에 특히 취약하다. 다음은 실제로 자주 발생하는 시나리오다.

**시나리오 1: Node.js 버전 차이**

```typescript
// 로컬 (Node 18): 정상 동작
// 서버 (Node 20): Array.fromAsync 등 새 API로 인해 동작 차이 발생

// Node 20에서 추가된 API를 무심코 사용
const data = await Array.fromAsync(asyncIterable);
// Node 18 환경에서는 TypeError: Array.fromAsync is not a function
```

개발자의 로컬에는 Node 20이 설치되어 있지만, 프로덕션 서버는 아직 Node 18을 사용 중이라면 런타임 에러가 발생한다.

**시나리오 2: OS 차이로 인한 native dependency 문제**

```bash
# macOS (로컬)에서 설치한 sharp 패키지
npm install sharp
# → @img/sharp-darwin-arm64 바이너리 다운로드

# Linux (서버)에서는 다른 바이너리가 필요
# → @img/sharp-linux-x64 바이너리 필요
# macOS에서 생성한 node_modules를 그대로 복사하면 실패
```

**시나리오 3: 시스템 라이브러리 차이**

```bash
# Prisma, canvas, bcrypt 등 native addon을 사용하는 패키지는
# OS에 설치된 C/C++ 라이브러리에 의존한다

# macOS에서는 문제 없지만, Alpine Linux에서는:
# Error: Error loading shared library libstdc++.so.6
```

> **핵심 통찰**: 도커는 이 모든 문제를 **"애플리케이션 + 실행 환경"을 하나의 패키지(이미지)로 묶어** 해결한다. 어디서 실행하든 동일한 OS, 동일한 라이브러리, 동일한 런타임 버전이 보장된다.

---

## 2. 가상 머신 vs 컨테이너

### 2.1 가상 머신(Virtual Machine)의 구조

가상 머신(*Virtual Machine - 하드웨어를 소프트웨어로 에뮬레이션하여 하나의 물리 서버 위에 여러 개의 독립된 OS를 실행하는 기술*)은 하이퍼바이저(*Hypervisor - 물리 하드웨어와 가상 머신 사이에서 리소스를 분배하는 소프트웨어 계층*)를 통해 동작한다.

VM 환경에서는 각 애플리케이션이 **자체 Guest OS**를 가진다. 즉, 3개의 앱을 실행하려면 3개의 완전한 운영체제가 필요하다. 각 Guest OS는 자체 커널, 시스템 라이브러리, 디바이스 드라이버를 포함하므로 리소스 소비가 크다.

### 2.2 컨테이너의 구조

컨테이너(*Container - 호스트 OS의 커널을 공유하면서 프로세스, 파일시스템, 네트워크를 격리하여 독립적인 실행 환경을 제공하는 기술*)는 VM과 근본적으로 다르다. **별도의 OS를 실행하지 않고**, 호스트 커널을 그대로 공유한다. 격리는 리눅스 커널의 네임스페이스(*Namespace*)와 cgroups(*Control Groups*)를 통해 이루어진다.

### 2.3 아키텍처 비교 다이어그램

```
VM 아키텍처:                         컨테이너 아키텍처:
┌───────┐ ┌───────┐ ┌───────┐      ┌───────┐ ┌───────┐ ┌───────┐
│ App A │ │ App B │ │ App C │      │ App A │ │ App B │ │ App C │
├───────┤ ├───────┤ ├───────┤      ├───────┤ ├───────┤ ├───────┤
│ Bins/ │ │ Bins/ │ │ Bins/ │      │ Bins/ │ │ Bins/ │ │ Bins/ │
│ Libs  │ │ Libs  │ │ Libs  │      │ Libs  │ │ Libs  │ │ Libs  │
├───────┤ ├───────┤ ├───────┤      ├───────┴─┴───────┴─┴───────┤
│Guest  │ │Guest  │ │Guest  │      │     Container Runtime      │
│  OS   │ │  OS   │ │  OS   │      │       (Docker Engine)      │
├───────┴─┴───────┴─┴───────┤      ├───────────────────────────┤
│        Hypervisor          │      │         Host OS            │
├────────────────────────────┤      ├───────────────────────────┤
│        Hardware            │      │         Hardware           │
└────────────────────────────┘      └───────────────────────────┘
```

### 2.4 상세 비교

| 항목 | 가상 머신 (VM) | 컨테이너 (Docker) |
|------|---------------|-------------------|
| **시작 시간** | 수십 초 ~ 수 분 | 수백 밀리초 ~ 수 초 |
| **메모리 사용** | 수 GB (Guest OS 포함) | 수십 MB (앱 + 라이브러리만) |
| **이미지 크기** | 수 GB ~ 수십 GB | 수십 MB ~ 수백 MB |
| **격리 수준** | 강력 (하드웨어 수준) | 프로세스 수준 (커널 공유) |
| **성능 오버헤드** | 높음 (하드웨어 에뮬레이션) | 거의 없음 (네이티브에 가까움) |
| **OS 지원** | 어떤 OS든 실행 가능 | 호스트와 동일 커널(Linux)만 |
| **보안 격리** | 강력 (별도 커널) | 상대적으로 약함 (커널 공유) |
| **밀도** | 서버당 수십 개 | 서버당 수백 ~ 수천 개 |

### 2.5 "컨테이너는 가벼운 VM"이 아니다

흔한 오해 중 하나는 컨테이너를 "가벼운 가상 머신"으로 이해하는 것이다. 이는 잘못된 멘탈 모델이다.

- **VM**: 하드웨어를 가상화한다. 가상 CPU, 가상 메모리, 가상 디스크 위에 완전한 OS가 돌아간다.
- **컨테이너**: OS를 가상화하지 않는다. **프로세스를 격리**할 뿐이다. 컨테이너 안의 프로세스는 호스트 커널 위에서 직접 실행되며, 단지 다른 프로세스와 파일시스템/네트워크/PID 등이 분리되어 있을 뿐이다.

Node.js로 비유하면:

```typescript
// VM은 마치 별도의 Node.js 프로세스를 완전히 다른 컴퓨터에서 실행하는 것
// → 완전히 독립적이지만, 별도 컴퓨터(OS)가 필요

// 컨테이너는 마치 같은 Node.js 프로세스 내에서 Worker Thread를 실행하는 것과 유사
// → 같은 커널(메인 스레드)을 공유하지만, 각 Worker는 격리된 실행 환경을 가짐
// (비유일 뿐, 정확한 매핑은 아니다)
```

> **핵심 통찰**: 컨테이너는 "프로세스 격리" 기술이지 "가상화" 기술이 아니다. 이 차이를 이해해야 컨테이너의 빠른 시작 시간, 낮은 오버헤드, 그리고 보안 특성을 올바르게 이해할 수 있다.

---

## 3. Docker Engine 아키텍처

### 3.1 전체 구조

Docker Engine은 단일 모놀리스가 아니라 **여러 컴포넌트가 협력하는 구조**로 설계되어 있다. 사용자가 `docker run`을 실행하면 내부적으로 다음 경로를 거친다:

```
┌──────────┐     REST API     ┌──────────┐     gRPC      ┌────────────┐
│ Docker   │ ──────────────→ │  Docker   │ ───────────→ │            │
│   CLI    │                  │  Daemon   │               │ containerd │
│          │                  │ (dockerd) │               │            │
└──────────┘                  └──────────┘               └──────┬─────┘
                                                                │
                                                          OCI Bundle
                                                                │
                                                          ┌─────▼─────┐
                                                          │   runc    │
                                                          │ (OCI 런타임)│
                                                          └─────┬─────┘
                                                                │
                                                          ┌─────▼─────┐
                                                          │ Container │
                                                          │ Process   │
                                                          └───────────┘
```

### 3.2 Docker CLI

Docker CLI는 사용자가 도커와 상호작용하는 **명령줄 인터페이스**다. CLI 자체는 컨테이너를 직접 관리하지 않는다. 대신 사용자의 명령을 **REST API 호출**로 변환하여 Docker Daemon에 전달한다.

```bash
# 사용자가 입력하는 명령
docker run -d -p 3000:3000 node:20-alpine

# 내부적으로는 다음과 같은 API 호출이 발생한다:
# POST /v1.43/containers/create
# POST /v1.43/containers/{id}/start
```

CLI와 Daemon은 Unix 소켓(`/var/run/docker.sock`)을 통해 통신한다. 이 소켓에 접근할 수 있으면 Docker Daemon을 제어할 수 있으므로 **보안상 중요한 자원**이다.

### 3.3 Docker Daemon (dockerd)

Docker Daemon(*dockerd - Docker의 핵심 서버 프로세스로, API 요청을 받아 이미지, 네트워크, 볼륨, 컨테이너를 관리한다*)은 Docker의 "두뇌" 역할을 한다.

주요 책임:
- **API 서버**: CLI 및 외부 도구의 REST API 요청을 수신하고 처리한다
- **이미지 관리**: 이미지 빌드, 풀(pull), 푸시(push), 태깅 등을 담당한다
- **네트워크 관리**: bridge, overlay, host 등 다양한 네트워크 드라이버를 관리한다
- **볼륨 관리**: 컨테이너의 데이터 영속성을 위한 볼륨을 관리한다
- **인증/보안**: Docker Hub 등 레지스트리와의 인증을 처리한다

### 3.4 containerd

containerd(*컨테이너디 - Docker에서 분리되어 독립 프로젝트가 된 컨테이너 런타임으로, 컨테이너의 전체 생명주기를 관리한다*)는 원래 Docker의 일부였지만, 현재는 CNCF(*Cloud Native Computing Foundation*) 산하의 독립 프로젝트다.

주요 책임:
- **컨테이너 생명주기 관리**: 생성(create), 시작(start), 정지(stop), 일시중지(pause), 삭제(delete)
- **이미지 전송**: 레지스트리에서 이미지를 pull/push
- **스토리지**: 이미지 레이어와 컨테이너 파일시스템 관리
- **네트워크 인터페이스 연결**: CNI 플러그인을 통한 네트워크 설정

### 3.5 runc

runc(*런씨 - OCI 런타임 스펙을 구현한 경량 CLI 도구로, 실제 컨테이너 프로세스를 생성한다*)는 컨테이너를 **실제로 만들어내는** 도구다.

runc가 수행하는 작업:
1. **네임스페이스 생성**: PID, 네트워크, 마운트, UTS, IPC, 유저 네임스페이스를 설정하여 프로세스를 격리
2. **cgroups 설정**: CPU, 메모리, I/O 등의 리소스 제한을 적용
3. **루트 파일시스템 설정**: 컨테이너의 rootfs를 마운트
4. **프로세스 시작**: 격리된 환경에서 지정된 프로세스(예: `node server.js`)를 실행

runc는 컨테이너 프로세스를 시작한 후 **즉시 종료**된다. 이후 컨테이너 프로세스는 containerd-shim이라는 경량 프로세스에 의해 관리된다.

### 3.6 왜 이렇게 분리했는가? — Daemonless Containers

초기 Docker(v1.10 이전)에서는 모든 기능이 단일 데몬(dockerd)에 집중되어 있었다. 이로 인해 심각한 문제가 있었다:

- **dockerd를 업데이트하면 모든 컨테이너가 중단된다**
- dockerd가 크래시하면 모든 컨테이너가 함께 죽는다
- 단일 장애점(Single Point of Failure)이 된다

현재 구조에서는 containerd-shim이 각 컨테이너의 부모 프로세스가 되므로:

- **dockerd를 재시작해도 컨테이너는 계속 실행된다**
- dockerd가 크래시해도 기존 컨테이너에 영향이 없다
- Docker Engine을 무중단으로 업그레이드할 수 있다

```bash
# dockerd를 재시작해도 실행 중인 컨테이너는 유지된다
sudo systemctl restart docker
docker ps  # 이전에 실행 중이던 컨테이너가 여전히 동작 중
```

> **핵심 통찰**: Docker의 컴포넌트 분리는 단순한 아키텍처 개선이 아니다. 프로덕션 환경에서 **Docker 자체를 무중단으로 업데이트**할 수 있게 만든 핵심 설계 결정이다.

---

## 4. OCI(Open Container Initiative) 표준

### 4.1 OCI란 무엇인가

OCI(*Open Container Initiative - Linux Foundation 산하 프로젝트로, 컨테이너 포맷과 런타임에 대한 개방형 업계 표준을 정의한다*)는 2015년 Docker, CoreOS, Google 등이 공동으로 설립한 표준화 기구다.

Docker가 사실상의 표준(de facto standard)으로 자리 잡으면서, 업계는 특정 벤더에 종속되는 것을 우려했다. OCI는 **컨테이너 기술의 핵심 요소를 표준화**하여 다양한 구현체가 서로 호환되도록 한다.

### 4.2 세 가지 핵심 표준

#### Runtime Specification (runtime-spec)

**컨테이너를 어떻게 실행할 것인가**를 정의한다:

- 컨테이너의 설정 파일(config.json) 형식
- 컨테이너의 생명주기(creating → created → running → stopped)
- 실행 환경(네임스페이스, cgroups, 루트 파일시스템 등)의 요구사항

runc는 이 스펙의 참조 구현체(reference implementation)다.

#### Image Specification (image-spec)

**컨테이너 이미지의 포맷**을 정의한다:

- 이미지 매니페스트(*Image Manifest - 이미지를 구성하는 레이어, 설정, 메타데이터의 목록*)
- 이미지 인덱스(멀티 플랫폼 이미지 지원)
- 레이어 포맷(tar + gzip)
- 이미지 설정(환경변수, 엔트리포인트, 포트 등)

#### Distribution Specification (distribution-spec)

**이미지를 어떻게 배포할 것인가**를 정의한다:

- 레지스트리 HTTP API
- 이미지 push/pull 프로토콜
- 콘텐츠 검증(digest 기반)

### 4.3 OCI 표준이 가져온 생태계

OCI 표준 덕분에 Docker 이미지는 Docker 외의 다양한 도구에서도 사용할 수 있다:

| 도구 | 설명 | OCI 호환 |
|------|------|----------|
| **Docker** | 가장 널리 사용되는 컨테이너 플랫폼 | O |
| **Podman** | 데몬 없는(daemonless) 컨테이너 엔진 | O |
| **containerd** | 독립 컨테이너 런타임 (Kubernetes 기본 런타임) | O |
| **CRI-O** | Kubernetes 전용 경량 런타임 | O |
| **Buildah** | 이미지 빌드 전용 도구 | O |
| **Skopeo** | 이미지 검사/복사 도구 | O |

```bash
# Docker로 빌드한 이미지를 Podman으로 실행할 수 있다
docker build -t my-next-app .
docker save my-next-app | podman load

# Podman에서도 동일하게 동작
podman run -p 3000:3000 my-next-app
```

> **핵심 통찰**: OCI 표준은 컨테이너 생태계의 "USB 규격"과 같다. 어떤 제조사의 USB 장치든 표준을 따르면 호환되듯이, OCI를 따르는 모든 도구는 동일한 이미지와 컨테이너를 다룰 수 있다.

---

## 5. Docker Desktop과 설치

### 5.1 Docker Desktop이 필요한 이유

Docker Engine은 **리눅스 커널 기능**(네임스페이스, cgroups)에 의존한다. macOS와 Windows는 리눅스 커널을 사용하지 않으므로, Docker를 직접 실행할 수 없다. Docker Desktop은 이 문제를 해결하기 위해 **경량 Linux VM을 내부적으로 실행**한다.

### 5.2 macOS에서의 Docker 아키텍처

```
┌────────────────────────────────────────────┐
│              macOS Host                     │
│                                            │
│  ┌──────────┐    ┌───────────────────────┐ │
│  │ Docker   │    │  Lightweight Linux VM │ │
│  │   CLI    │───→│  ┌─────────────────┐  │ │
│  └──────────┘    │  │  Docker Engine   │  │ │
│                  │  │  (dockerd)       │  │ │
│                  │  ├─────────────────┤  │ │
│                  │  │  containerd     │  │ │
│                  │  ├─────────────────┤  │ │
│                  │  │  Linux Kernel   │  │ │
│                  │  └─────────────────┘  │ │
│                  └───────────────────────┘ │
│              Apple Hypervisor Framework     │
└────────────────────────────────────────────┘
```

macOS에서 Docker Desktop은:
1. **Apple Hypervisor Framework**를 사용하여 경량 Linux VM을 생성한다
2. 이 VM 안에서 Docker Engine(dockerd + containerd)이 실행된다
3. Docker CLI는 macOS에 설치되어, 소켓을 통해 VM 안의 dockerd와 통신한다
4. 파일 공유, 네트워크 포워딩 등은 Docker Desktop이 자동으로 처리한다

### 5.3 설치 확인

Docker Desktop을 설치한 후, 다음 명령어로 정상 설치를 확인한다:

```bash
# Docker 클라이언트와 서버 버전 확인
docker version
```

출력 예시:

```
Client:
 Version:           24.0.7
 API version:       1.43
 Go version:        go1.21.3
 OS/Arch:           darwin/arm64

Server: Docker Desktop 4.26.1 (131620)
 Engine:
  Version:          24.0.7
  API version:      1.43
  Go version:       go1.21.3
  OS/Arch:          linux/arm64
```

여기서 주목할 점: **Client는 darwin/arm64(macOS)**이고 **Server는 linux/arm64(Linux VM)**다. 이것이 Docker Desktop이 내부적으로 Linux VM을 사용한다는 증거다.

```bash
# Docker 시스템 상세 정보 확인
docker info
```

이 명령어는 스토리지 드라이버, 로깅 드라이버, cgroup 드라이버, 커널 버전 등 Docker 엔진의 상세 설정 정보를 보여준다.

### 5.4 Docker Desktop 대안

Docker Desktop은 유료 라이선스 정책(직원 250명 이상 또는 매출 $10M 이상 기업)이 있어, 대안 도구를 고려할 수 있다:

| 도구 | 특징 | 무료 여부 |
|------|------|-----------|
| **Colima** | Lima 기반 경량 Docker 런타임 (macOS/Linux) | 무료 (오픈소스) |
| **Rancher Desktop** | Kubernetes 통합, containerd/dockerd 선택 가능 | 무료 (오픈소스) |
| **OrbStack** | macOS 전용, 매우 빠른 시작 시간과 낮은 리소스 사용 | 개인 무료, 기업 유료 |
| **Podman Desktop** | 데몬 없는 구조, Docker CLI 호환 | 무료 (오픈소스) |

```bash
# Colima로 Docker 환경 실행 예시
brew install colima docker
colima start
docker run hello-world  # Docker CLI는 동일하게 사용
```

> **실무 팁**: 개인 개발이나 소규모 팀이라면 Docker Desktop이 가장 편리하다. 기업 환경에서 라이선스가 문제된다면 OrbStack(macOS)이나 Colima를 추천한다. OrbStack은 Docker Desktop보다 시작 시간과 메모리 사용량이 현저히 적다.

---

## 6. 첫 번째 컨테이너 실행

### 6.1 Hello Docker

가장 간단한 컨테이너 실행부터 시작하자:

```bash
docker run node:20-alpine node -e "console.log('Hello from Docker!')"
```

이 한 줄의 명령어가 내부적으로 수행하는 과정을 단계별로 살펴보자.

### 6.2 docker run의 내부 동작

`docker run`은 실제로 세 가지 동작을 순차적으로 수행하는 **단축 명령어(shortcut)** 다:

**Step 1: 이미지 Pull**

```bash
# docker run이 내부적으로 실행하는 첫 번째 동작
docker pull node:20-alpine
```

로컬에 `node:20-alpine` 이미지가 없으면 Docker Hub(기본 레지스트리)에서 이미지를 다운로드한다. 이미지는 여러 레이어(*Layer - 이미지를 구성하는 읽기 전용 파일시스템 조각*)로 구성되며, 각 레이어는 독립적으로 다운로드된다.

```
20-alpine: Pulling from library/node
4abcf2066143: Pull complete    ← Alpine Linux 기본 레이어
e23a2b0f0b51: Pull complete    ← Node.js 바이너리 레이어
9e3afed3e39e: Pull complete    ← npm/yarn 설치 레이어
Digest: sha256:a1b2c3d4...
Status: Downloaded newer image for node:20-alpine
```

**Step 2: 컨테이너 생성**

```bash
# docker run이 내부적으로 실행하는 두 번째 동작
docker create node:20-alpine node -e "console.log('Hello from Docker!')"
```

이미지를 기반으로 컨테이너를 생성한다. 이 시점에서 컨테이너에는 고유한 ID, 격리된 파일시스템, 네트워크 설정 등이 할당되지만 **아직 실행되지는 않는다**.

**Step 3: 컨테이너 시작**

```bash
# docker run이 내부적으로 실행하는 세 번째 동작
docker start <container-id>
```

컨테이너 프로세스가 시작되고, 지정된 명령어(`node -e "console.log('Hello from Docker!')"`)가 격리된 환경에서 실행된다.

### 6.3 인터랙티브 모드로 Node.js REPL 실행

컨테이너 안에서 대화형으로 작업하려면 `-it` 플래그를 사용한다:

```bash
# -i: stdin을 열어둔다 (interactive)
# -t: TTY를 할당한다 (terminal)
docker run -it node:20-alpine node
```

이 명령어를 실행하면 Docker 컨테이너 안의 Node.js REPL에 접속한다:

```
Welcome to Node.js v20.11.0.
Type ".help" for more information.
> process.platform
'linux'
> process.arch
'arm64'
> os.freemem() / 1024 / 1024
7834.2
> .exit
```

`process.platform`이 macOS에서 실행해도 `'linux'`를 반환하는 것에 주목하자. 컨테이너 안은 **Linux 환경**이다.

### 6.4 Next.js 앱을 컨테이너에서 실행해보기

좀 더 실용적인 예제로, Next.js 앱을 컨테이너에서 실행해보자:

```bash
# Next.js 프로젝트 디렉토리에서
# 현재 디렉토리를 컨테이너에 마운트하고 의존성 설치 후 개발 서버 실행
docker run -it \
  -p 3000:3000 \
  -v $(pwd):/app \
  -w /app \
  node:20-alpine \
  sh -c "npm install && npm run dev"
```

각 플래그의 의미:

| 플래그 | 설명 |
|--------|------|
| `-it` | 인터랙티브 모드 + TTY 할당 |
| `-p 3000:3000` | 호스트의 3000번 포트를 컨테이너의 3000번 포트에 연결 |
| `-v $(pwd):/app` | 현재 디렉토리를 컨테이너의 `/app`에 마운트 |
| `-w /app` | 컨테이너의 작업 디렉토리를 `/app`으로 설정 |
| `node:20-alpine` | 사용할 이미지 |
| `sh -c "npm install && npm run dev"` | 컨테이너에서 실행할 명령어 |

브라우저에서 `http://localhost:3000`에 접속하면 컨테이너에서 실행 중인 Next.js 앱을 확인할 수 있다.

> **실무 팁**: 위 방식은 학습용으로는 좋지만, 실제 프로젝트에서는 Dockerfile을 작성하여 이미지를 빌드하는 것이 올바른 방법이다. `-v` 마운트와 직접 `npm install`은 "내 컴퓨터에서는 되는데" 문제를 완전히 해결하지 못한다. Dockerfile 작성은 Ch 4에서 다룬다.

### 6.5 컨테이너 상태 확인

```bash
# 실행 중인 컨테이너 목록
docker ps

# 모든 컨테이너 (종료된 것 포함)
docker ps -a
```

출력 예시:

```
CONTAINER ID   IMAGE             COMMAND                  STATUS          PORTS                    NAMES
a1b2c3d4e5f6   node:20-alpine    "docker-entrypoint.s…"   Up 2 minutes    0.0.0.0:3000->3000/tcp   eager_newton
```

```bash
# 로컬에 있는 이미지 목록
docker images
```

출력 예시:

```
REPOSITORY   TAG          IMAGE ID       CREATED       SIZE
node         20-alpine    a1b2c3d4e5f6   2 weeks ago   132MB
node         20           f1e2d3c4b5a6   2 weeks ago   1.09GB
```

`20-alpine`(132MB)과 `20`(1.09GB)의 크기 차이에 주목하자. Alpine Linux(*경량 리눅스 배포판으로, 약 5MB의 기본 이미지 크기를 가진다*)를 기반으로 한 이미지는 풀 이미지에 비해 **약 8배 작다**. 이미지 크기 최적화는 Ch 2에서 자세히 다룬다.

### 6.6 컨테이너 정리

```bash
# 실행 중인 컨테이너 중지
docker stop a1b2c3d4e5f6

# 중지된 컨테이너 삭제
docker rm a1b2c3d4e5f6

# 한 번에 중지 + 삭제 (실행 중인 컨테이너 강제 삭제)
docker rm -f a1b2c3d4e5f6

# 중지된 모든 컨테이너 삭제
docker container prune

# 사용하지 않는 이미지, 컨테이너, 네트워크 모두 정리
docker system prune
```

> **실무 팁**: 학습 중에는 컨테이너가 금방 쌓인다. `docker system prune`을 주기적으로 실행하여 디스크 공간을 확보하자. 단, 이 명령어는 **사용하지 않는 모든 리소스**를 삭제하므로 프로덕션 환경에서는 주의가 필요하다.

---

## 자주 하는 실수

| 실수 | 문제점 | 올바른 방법 |
|------|--------|-------------|
| Docker = 가상 머신이라고 생각 | 잘못된 멘탈 모델로 인한 설계 오류. VM처럼 SSH 접속하여 내부를 수정하는 패턴 등 | 컨테이너는 **격리된 프로세스**임을 이해. 이미지로 환경을 정의하고, 컨테이너는 일회용으로 취급 |
| Docker Desktop 없이 macOS에서 docker 명령어 실행 | `Cannot connect to the Docker daemon` 에러 발생. Docker Engine은 Linux 커널 기능을 필요로 한다 | Docker Desktop, Colima, OrbStack 등을 먼저 설치하고 실행 |
| `latest` 태그만 사용 | 빌드 재현성이 없다. 어제와 오늘의 `latest`가 다를 수 있다. 프로덕션에서 예상치 못한 업데이트 발생 | 구체적 버전 태그 사용: `node:20.11-alpine` |
| 컨테이너를 종료하지 않고 방치 | 불필요한 CPU/메모리 점유, 포트 충돌 | `docker ps`로 확인 후 `docker stop`으로 정리. `--rm` 플래그로 자동 삭제 활용 |
| 모든 것을 root로 실행 | 컨테이너 탈출 시 호스트의 root 권한 획득 가능 | 비root 사용자로 실행 (Ch 12에서 상세 다룸) |

---

## 명령어 레퍼런스

| 명령어 | 설명 | 예시 |
|--------|------|------|
| `docker version` | Docker 클라이언트/서버 버전 확인 | `docker version` |
| `docker info` | Docker 시스템 상세 정보 | `docker info` |
| `docker run` | 이미지로부터 새 컨테이너 생성 + 시작 | `docker run -it node:20-alpine node` |
| `docker run -d` | 백그라운드(detached) 모드로 실행 | `docker run -d -p 3000:3000 my-app` |
| `docker run --rm` | 컨테이너 종료 시 자동 삭제 | `docker run --rm node:20-alpine node -v` |
| `docker pull` | 레지스트리에서 이미지 다운로드 | `docker pull node:20-alpine` |
| `docker ps` | 실행 중인 컨테이너 목록 | `docker ps` |
| `docker ps -a` | 모든 컨테이너 목록 (종료 포함) | `docker ps -a` |
| `docker images` | 로컬 이미지 목록 | `docker images` |
| `docker stop` | 실행 중인 컨테이너 중지 | `docker stop <container-id>` |
| `docker rm` | 컨테이너 삭제 | `docker rm <container-id>` |
| `docker rm -f` | 강제 삭제 (실행 중이어도) | `docker rm -f <container-id>` |
| `docker system prune` | 미사용 리소스 일괄 정리 | `docker system prune` |

---

## 요약

- **컨테이너가 필요한 이유**: "내 컴퓨터에서는 되는데" 문제를 해결하기 위해 애플리케이션과 실행 환경을 하나의 패키지(이미지)로 묶는다
- **VM vs 컨테이너**: VM은 하드웨어를 가상화하여 전체 OS를 실행하고, 컨테이너는 호스트 커널을 공유하며 프로세스만 격리한다. 컨테이너는 VM보다 빠르고, 가볍고, 밀도가 높다
- **Docker Engine 아키텍처**: Docker CLI → dockerd → containerd → runc의 4단계 구조로, 각 컴포넌트가 명확한 책임을 가진다. 이 분리 덕분에 dockerd가 죽어도 컨테이너는 계속 실행된다
- **OCI 표준**: Runtime, Image, Distribution 세 가지 표준이 컨테이너 생태계의 호환성을 보장한다. Docker 이미지는 Podman, containerd 등 OCI 호환 도구에서도 사용 가능하다
- **Docker Desktop**: macOS/Windows에서는 내부적으로 Linux VM을 실행하여 Docker Engine을 구동한다. Colima, OrbStack 등의 대안이 존재한다
- **docker run**: pull → create → start를 순차적으로 수행하는 단축 명령어다. `-it`, `-p`, `-v`, `-d`, `--rm` 등의 플래그로 실행 방식을 제어한다

---

## 다른 챕터와의 관계

- **Ch 2 (이미지와 레이어)**: 이 챕터에서 언급한 이미지의 내부 레이어 구조, Alpine vs 풀 이미지의 크기 차이, 이미지 캐싱 메커니즘을 상세히 다룬다
- **Ch 3 (컨테이너 심화)**: Docker Engine 아키텍처에서 언급한 네임스페이스(PID, 네트워크, 마운트, UTS, IPC, 유저)와 cgroups가 어떻게 프로세스 격리와 리소스 제한을 구현하는지 심화 설명한다
- **Ch 4 (Dockerfile 작성)**: 이 챕터에서 `docker run`으로 수동 실행했던 Next.js 앱을 Dockerfile로 자동화하여 자신만의 이미지를 만드는 방법을 배운다
- **Ch 15 (Beyond Docker)**: OCI 표준 덕분에 가능한 Docker 대안 도구들(Podman, Buildah, Skopeo, nerdctl)의 사용법과 장단점을 살펴본다
