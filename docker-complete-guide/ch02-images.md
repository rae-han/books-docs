# Chapter 2: 이미지 — 컨테이너의 청사진: Images

## 핵심 질문

도커 이미지는 내부적으로 어떤 구조를 가지며, 어떻게 효율적으로 저장되고 배포되는가? 태그와 다이제스트의 차이는 무엇이고, Node.js 프로젝트에 적합한 베이스 이미지는 어떻게 선택하는가?

---

## 1. 이미지란 무엇인가

### 1.1 정의

도커 이미지(*Docker Image - 컨테이너를 생성하기 위한 읽기 전용 템플릿*)는 애플리케이션을 실행하는 데 필요한 모든 것을 담고 있는 **불변의 파일시스템 스냅샷**이다. "모든 것"이란 다음을 의미한다:

- **파일시스템**: OS 기본 유틸리티, 런타임(Node.js), 애플리케이션 코드, `node_modules` 등
- **메타데이터**: 환경변수, 작업 디렉토리, 실행 명령어, 노출 포트 등의 설정 정보

이미지 하나만 있으면 어떤 환경에서든 동일한 컨테이너를 실행할 수 있다. "내 컴퓨터에서는 되는데"라는 문제를 근본적으로 해결하는 핵심 단위가 바로 이미지다.

### 1.2 이미지와 컨테이너의 관계

이미지와 컨테이너의 관계는 **클래스와 인스턴스**의 관계와 동일하다:

```typescript
// 비유: 이미지는 클래스, 컨테이너는 인스턴스
class DockerImage {
  readonly filesystem: FileSystem;
  readonly metadata: ImageConfig;
}

// 하나의 이미지에서 여러 컨테이너를 생성할 수 있다
const container1 = new DockerImage(); // docker run image
const container2 = new DockerImage(); // docker run image
const container3 = new DockerImage(); // docker run image
```

- **이미지**: 읽기 전용(immutable). 한번 빌드되면 내용이 변하지 않는다.
- **컨테이너**: 이미지 위에 쓰기 가능한 레이어를 추가한 실행 인스턴스. 각 컨테이너는 독립적인 상태를 가진다.

```bash
# 하나의 이미지에서 3개의 독립적인 컨테이너 실행
docker run -d --name app1 my-node-app:1.0
docker run -d --name app2 my-node-app:1.0
docker run -d --name app3 my-node-app:1.0
```

세 컨테이너 모두 `my-node-app:1.0` 이미지를 기반으로 하지만, 각각 독립적인 파일시스템과 프로세스를 가진다. `app1`에서 파일을 수정해도 `app2`와 `app3`에는 영향을 주지 않는다.

### 1.3 이미지는 불변(Immutable)이다

이미지의 불변성은 도커의 핵심 설계 원칙이다:

- 한번 빌드된 이미지의 내용은 **절대로 변경할 수 없다**.
- 변경이 필요하면 새로운 이미지를 빌드해야 한다.
- 컨테이너 내부에서 파일을 수정해도 원본 이미지에는 영향을 주지 않는다.

이 불변성 덕분에:
1. **재현 가능성**: 같은 이미지는 언제 어디서 실행해도 동일한 결과를 보장한다.
2. **안전한 롤백**: 이전 버전의 이미지로 즉시 롤백할 수 있다.
3. **캐싱 효율**: 변경되지 않은 부분을 안전하게 재사용할 수 있다.

---

## 2. 레이어(Layer) 구조

### 2.1 레이어란 무엇인가

도커 이미지는 하나의 거대한 파일이 아니라, 여러 **레이어**(*Layer - 파일시스템 변경 사항을 담은 읽기 전용 단위*)가 순서대로 쌓인 구조다. Dockerfile의 각 인스트럭션(`FROM`, `RUN`, `COPY`, `ADD` 등)이 실행될 때마다 새로운 레이어가 생성된다.

다음 Dockerfile을 예로 보자:

```dockerfile
FROM node:20-alpine          # 베이스 이미지의 레이어들을 가져온다
WORKDIR /app                 # 메타데이터만 변경 (빈 레이어)
COPY package*.json ./        # package.json, package-lock.json 복사 → 새 레이어
RUN npm ci --only=production # node_modules 설치 → 새 레이어
COPY . .                     # 나머지 소스코드 복사 → 새 레이어
CMD ["node", "server.js"]    # 메타데이터만 변경 (빈 레이어)
```

### 2.2 레이어 스택킹

위 Dockerfile로 빌드된 이미지의 레이어 구조를 시각화하면 다음과 같다:

```
┌─────────────────────────────┐  ← Container Layer (R/W, 컨테이너 실행 시 추가)
├─────────────────────────────┤
│ CMD ["node", "server.js"]   │  ← Layer 5 (metadata only, 0B)
│ COPY . .                    │  ← Layer 4 (~2MB, 소스코드)
│ RUN npm ci --only=production│  ← Layer 3 (~150MB, node_modules)
│ COPY package*.json ./       │  ← Layer 2 (~4KB, package.json)
│ WORKDIR /app                │  ← Layer 1 (metadata only, 0B)
│ node:20-alpine base         │  ← Base Layers (~130MB, OS + Node.js)
└─────────────────────────────┘
```

레이어는 **아래에서 위로 쌓이며**, 위 레이어가 아래 레이어의 파일을 "덮어쓸" 수 있다. 최종 이미지의 파일시스템은 모든 레이어를 합친 결과다.

### 2.3 Union File System

레이어를 하나의 파일시스템으로 합쳐 보여주는 기술이 유니온 파일시스템(*Union File System - 여러 파일시스템을 하나로 겹쳐 보여주는 가상 파일시스템*)이다. 도커는 주로 **OverlayFS**를 사용한다.

OverlayFS의 동작 원리:

```
사용자가 보는 통합 뷰 (merged)
         │
    ┌────┴────┐
    │         │
 Upper      Lower
 (R/W)      (R/O)
컨테이너    이미지
 레이어     레이어들
```

- **Lower layers** (읽기 전용): 이미지의 모든 레이어가 겹쳐진다.
- **Upper layer** (읽기/쓰기): 컨테이너 실행 시 추가되는 레이어.
- **Merged view**: 사용자(컨테이너 내 프로세스)가 보는 최종 파일시스템.

파일을 읽을 때는 위에서 아래로 탐색하여 **가장 먼저 찾은 파일**을 반환한다.

### 2.4 레이어 공유

같은 베이스 이미지를 사용하는 여러 이미지는 **레이어를 공유**한다. 이것이 도커의 저장 효율이 높은 핵심 이유다.

```
이미지 A (Next.js 앱)         이미지 B (Express 앱)
┌──────────────────┐         ┌──────────────────┐
│ COPY . . (Next)  │         │ COPY . . (Express)│
│ RUN npm ci       │         │ RUN npm ci        │
│ COPY package*    │         │ COPY package*     │
├──────────────────┤         ├──────────────────┤
│                                                │
│        node:20-alpine (공유, 디스크에 1벌만)     │
│                                                │
└────────────────────────────────────────────────┘
```

`node:20-alpine` 레이어는 디스크에 **한 번만** 저장되고, 이미지 A와 B 모두 이를 참조한다. 10개의 Node.js 앱 이미지를 만들어도 베이스 레이어는 130MB만 차지한다.

### 2.5 레이어 확인하기

**`docker history`** 명령으로 이미지의 레이어별 정보를 확인할 수 있다:

```bash
docker history my-node-app:1.0

# 출력 예시
IMAGE          CREATED        CREATED BY                                      SIZE
a1b2c3d4e5f6   2 hours ago   CMD ["node" "server.js"]                         0B
b2c3d4e5f6a7   2 hours ago   COPY dir:... in /app                             2.1MB
c3d4e5f6a7b8   2 hours ago   RUN /bin/sh -c npm ci --only=production          148MB
d4e5f6a7b8c9   2 hours ago   COPY file:... in /app/package*.json              4.2KB
e5f6a7b8c9d0   2 hours ago   WORKDIR /app                                     0B
f6a7b8c9d0e1   3 days ago    /bin/sh -c #(nop)  CMD ["node"]                  0B
...            3 days ago    (node:20-alpine 베이스 레이어들)                   130MB
```

**`docker image inspect`** 명령으로 더 상세한 메타데이터를 JSON으로 확인할 수 있다:

```bash
# 이미지의 레이어 SHA 목록 확인
docker image inspect my-node-app:1.0 --format '{{json .RootFS.Layers}}' | jq .

# 출력 예시
[
  "sha256:abc123...",   # 베이스 레이어 1
  "sha256:def456...",   # 베이스 레이어 2
  "sha256:ghi789...",   # COPY package*.json
  "sha256:jkl012...",   # RUN npm ci
  "sha256:mno345..."    # COPY . .
]
```

### 2.6 Copy-on-Write (CoW) 전략

컨테이너가 이미지 레이어의 파일을 수정하려 할 때, 도커는 **Copy-on-Write**(*CoW - 쓰기 시 복사, 파일을 수정할 때만 해당 파일을 컨테이너 레이어에 복사하는 전략*) 방식을 사용한다.

동작 과정:

1. 컨테이너에서 `/app/config.json`을 읽는다 → 이미지 레이어에서 직접 읽음 (복사 없음)
2. 컨테이너에서 `/app/config.json`을 **수정**하려 한다
3. 도커가 해당 파일을 이미지 레이어에서 컨테이너의 R/W 레이어로 **복사**한다
4. 컨테이너 R/W 레이어의 복사본을 수정한다
5. 이후 이 파일에 대한 모든 읽기/쓰기는 컨테이너 레이어의 복사본을 사용한다

```
읽기만 할 때:
Container Layer (R/W)  →  (비어있음)
Image Layer (R/O)      →  config.json  ← 여기서 직접 읽음

수정 시 (CoW 발생):
Container Layer (R/W)  →  config.json (복사본, 수정됨) ← 이후 여기서 읽음
Image Layer (R/O)      →  config.json (원본, 변경 없음)
```

CoW의 이점:
- **빠른 컨테이너 시작**: 컨테이너 생성 시 이미지 전체를 복사할 필요가 없다.
- **디스크 절약**: 실제로 수정된 파일만 컨테이너 레이어에 존재한다.
- **이미지 보호**: 원본 이미지 레이어는 절대 수정되지 않는다.

> **핵심 통찰**: 컨테이너에서 대용량 파일을 수정하면 해당 파일 전체가 컨테이너 레이어에 복사되므로 디스크 사용량이 증가한다. 로그 파일이나 데이터 파일처럼 빈번하게 쓰기가 발생하는 파일은 볼륨(Volume)을 사용하는 것이 효율적이다.

---

## 3. 이미지 레지스트리

### 3.1 레지스트리란

이미지 레지스트리(*Image Registry - 도커 이미지를 저장하고 배포하는 원격 저장소*)는 이미지의 중앙 저장소다. Git의 원격 저장소(GitHub)와 유사한 역할을 한다.

### 3.2 Docker Hub

도커의 기본 레지스트리는 **Docker Hub** (https://hub.docker.com)이다. `docker pull node:20` 명령을 실행하면 자동으로 Docker Hub에서 이미지를 가져온다.

```bash
# 다음 두 명령은 동일하다
docker pull node:20
docker pull docker.io/library/node:20
#          ──────── ─────── ────────
#          레지스트리  네임스페이스  이미지:태그
```

Docker Hub의 이미지는 크게 두 종류로 나뉜다:

| 구분 | 공식 이미지(Official Images) | 커뮤니티 이미지 |
|------|---------------------------|---------------|
| 네임스페이스 | `library/` (생략 가능) | 사용자명/조직명 |
| 예시 | `node:20`, `nginx:latest` | `bitnami/node:20` |
| 관리 | Docker + 업스트림 유지보수자 | 개인/조직 |
| 보안 검증 | Docker Scout 자동 스캔 | 사용자 재량 |
| 신뢰도 | 높음 | 다양함 |

> **실무 팁**: 가능하면 항상 공식 이미지를 베이스로 사용한다. 커뮤니티 이미지를 사용해야 한다면 Docker Hub의 다운로드 수, 스타 수, 최근 업데이트 일자를 반드시 확인한다.

### 3.3 주요 레지스트리 비교

| 레지스트리 | 주소 | 특징 |
|-----------|------|------|
| Docker Hub | `docker.io` | 기본 레지스트리, 무료 계정은 pull rate limit 존재 |
| GitHub Container Registry | `ghcr.io` | GitHub Actions와 통합 용이, GitHub 패키지와 연동 |
| AWS ECR | `{account}.dkr.ecr.{region}.amazonaws.com` | AWS 서비스(ECS, EKS)와 긴밀한 통합 |
| Google Artifact Registry | `{region}-docker.pkg.dev` | GKE와 통합, 멀티 형식(Docker, npm, Maven) 지원 |
| Azure Container Registry | `{name}.azurecr.io` | Azure 서비스와 통합 |

### 3.4 이미지 Push/Pull 워크플로

```bash
# 1. 레지스트리에 로그인
docker login ghcr.io
# Username: your-username
# Password: your-personal-access-token

# 2. 이미지 빌드 (레지스트리 주소를 포함한 태그)
docker build -t ghcr.io/your-org/my-next-app:1.0.0 .

# 3. 이미지 푸시
docker push ghcr.io/your-org/my-next-app:1.0.0

# 4. 다른 서버에서 이미지 풀
docker pull ghcr.io/your-org/my-next-app:1.0.0
```

이미지 이름의 전체 구조:

```
ghcr.io/your-org/my-next-app:1.0.0
───────  ────────  ────────── ─────
레지스트리  네임스페이스  리포지토리   태그
```

### 3.5 Private 레지스트리 운영

사내 프로젝트라면 Private 레지스트리를 사용해야 한다. 간단한 방법은 Docker의 공식 `registry` 이미지를 활용하는 것이다:

```bash
# 로컬 Private 레지스트리 실행
docker run -d -p 5000:5000 --name registry registry:2

# 이미지에 로컬 레지스트리 태그 붙이기
docker tag my-next-app:1.0.0 localhost:5000/my-next-app:1.0.0

# 로컬 레지스트리에 푸시
docker push localhost:5000/my-next-app:1.0.0
```

실무에서는 클라우드 매니지드 레지스트리(ECR, GCR 등)를 사용하는 것이 운영 부담을 줄이는 가장 좋은 방법이다.

---

## 4. 태그(Tag) vs 다이제스트(Digest)

### 4.1 태그(Tag)

태그(*Tag - 이미지에 붙이는 사람이 읽기 쉬운 이름표*)는 이미지의 특정 버전을 가리키는 별칭이다.

```bash
# 이미지 이름:태그 형식
node:20          # Node.js 20.x 최신
node:20.11.1     # Node.js 정확한 버전
node:20-alpine   # Node.js 20.x + Alpine Linux
node:20-slim     # Node.js 20.x + Debian Slim
```

**태그는 변경 가능(mutable)하다.** 이것이 태그의 가장 중요한 특성이다. 같은 태그 `node:20`이 오늘과 다음 주에 서로 다른 이미지를 가리킬 수 있다:

```
2024년 1월: node:20 → 이미지 A (Node 20.10.0)
2024년 2월: node:20 → 이미지 B (Node 20.11.0)  ← 같은 태그, 다른 이미지!
2024년 3월: node:20 → 이미지 C (Node 20.11.1)
```

이 변경 가능성 때문에 `node:20`만으로는 정확히 어떤 이미지인지 보장할 수 없다.

### 4.2 다이제스트(Digest)

다이제스트(*Digest - 이미지 콘텐츠의 SHA256 해시값으로 된 고유 식별자*)는 이미지 콘텐츠 자체에서 계산된 해시값이다. **절대 변경되지 않는다(immutable).**

```bash
# 다이제스트 확인
docker pull node:20-alpine
# 20-alpine: Pulling from library/node
# Digest: sha256:a1b2c3d4e5f6...  ← 이것이 다이제스트

# 다이제스트로 이미지 풀
docker pull node@sha256:a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2
```

### 4.3 태그 vs 다이제스트 비교

| 속성 | 태그(Tag) | 다이제스트(Digest) |
|------|----------|-------------------|
| 형식 | `node:20-alpine` | `node@sha256:a1b2c3...` |
| 가독성 | 높음 | 낮음 |
| 변경 가능 | 가능 (mutable) | 불가능 (immutable) |
| 재현 가능성 | 낮음 | 완벽 |
| 보안 | 중간 (태그 변조 가능) | 높음 (해시로 검증) |
| 용도 | 개발, 로컬 테스트 | 프로덕션, CI/CD |

### 4.4 Dockerfile에서 다이제스트 사용

프로덕션 Dockerfile에서는 다이제스트를 사용하여 빌드 재현성을 보장할 수 있다:

```dockerfile
# 태그 사용 (편리하지만 재현성 낮음)
FROM node:20-alpine

# 다이제스트 사용 (재현성 보장)
FROM node@sha256:a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2

# 태그 + 다이제스트 병용 (가독성 + 재현성)
FROM node:20-alpine@sha256:a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2
```

> **실무 팁**: 태그와 다이제스트를 함께 쓰면 코드 리뷰 시 어떤 베이스 이미지인지 한눈에 파악하면서도 재현성을 보장할 수 있다. Renovate나 Dependabot 같은 자동 업데이트 도구를 사용하면 다이제스트 관리 부담도 줄일 수 있다.

### 4.5 태그 전략

프로젝트에서 이미지 태그를 어떻게 붙일 것인지에 대한 전략이 필요하다:

**1. Semantic Versioning (권장)**

```bash
docker build -t my-next-app:1.0.0 .
docker tag my-next-app:1.0.0 my-next-app:1.0
docker tag my-next-app:1.0.0 my-next-app:1

# 사용자는 필요한 정밀도를 선택할 수 있다
# my-next-app:1     → 메이저 1의 최신
# my-next-app:1.0   → 마이너 1.0의 최신
# my-next-app:1.0.0 → 정확한 버전
```

**2. Git SHA 기반**

```bash
GIT_SHA=$(git rev-parse --short HEAD)
docker build -t my-next-app:${GIT_SHA} .
# my-next-app:a3f8b2c
```

CI/CD에서 어떤 커밋의 이미지인지 바로 추적할 수 있다.

**3. 날짜 기반**

```bash
docker build -t my-next-app:2024-02-15 .
```

**4. 복합 전략 (실무 권장)**

```bash
# CI/CD에서 여러 태그를 동시에 붙인다
VERSION="1.2.3"
GIT_SHA=$(git rev-parse --short HEAD)

docker build -t my-next-app:${VERSION} \
             -t my-next-app:${GIT_SHA} \
             -t my-next-app:latest .
```

### 4.6 :latest 태그의 함정

`:latest`는 "가장 최신 버전"이라는 의미가 **아니다**. 단지 태그를 명시하지 않았을 때 기본으로 붙는 이름일 뿐이다.

```bash
# 태그를 명시하지 않으면 자동으로 :latest
docker build -t my-app .
# → my-app:latest 로 태그됨

docker pull my-app
# → my-app:latest 를 가져옴
```

`:latest`의 문제점:

1. **자동 업데이트되지 않는다**: `docker build -t my-app:1.0 .`을 실행해도 `my-app:latest`는 업데이트되지 않는다. 명시적으로 `docker build -t my-app:latest .`를 실행해야 한다.
2. **어떤 버전인지 알 수 없다**: `my-app:latest`가 실제로 1.0인지 2.0인지 알 방법이 없다.
3. **롤백이 불가능하다**: 이전 `:latest`로 되돌릴 수 없다.

```bash
# 나쁜 예: Dockerfile에서 latest 사용
FROM node:latest  # 빌드할 때마다 다른 버전이 될 수 있다!

# 좋은 예: 구체적인 버전 명시
FROM node:20-alpine
```

> **핵심 통찰**: 프로덕션 환경에서는 `:latest` 태그를 절대 사용하지 않는다. 반드시 구체적인 버전 태그나 다이제스트를 사용하여 이미지를 특정해야 한다.

---

## 5. Node.js 베이스 이미지 비교

### 5.1 주요 베이스 이미지

Node.js 프로젝트에서 선택할 수 있는 주요 베이스 이미지는 네 가지다:

#### node:20 (Debian Bookworm 풀 이미지)

```dockerfile
FROM node:20
```

- **크기**: ~1.1GB
- **기반 OS**: Debian Bookworm (전체 설치)
- **특징**: 거의 모든 시스템 도구와 라이브러리가 포함되어 있다. `gcc`, `make`, `python3` 등 빌드 도구도 포함.
- **용도**: 개발 환경, native addon 빌드가 필요한 경우, 디버깅

#### node:20-slim (Debian Slim)

```dockerfile
FROM node:20-slim
```

- **크기**: ~240MB
- **기반 OS**: Debian Bookworm (최소 설치)
- **특징**: Debian 기반이지만 불필요한 패키지를 제거한 경량 버전. `glibc` 사용.
- **용도**: native addon이 필요하지만 이미지 크기를 줄이고 싶을 때

#### node:20-alpine (Alpine Linux)

```dockerfile
FROM node:20-alpine
```

- **크기**: ~130MB
- **기반 OS**: Alpine Linux
- **특징**: 매우 작은 Alpine Linux 기반. `musl libc` 사용 (glibc 대신).
- **용도**: 대부분의 프로덕션 환경에서의 기본 선택

#### gcr.io/distroless/nodejs20-debian12 (Distroless)

```dockerfile
FROM gcr.io/distroless/nodejs20-debian12
```

- **크기**: ~120MB
- **기반 OS**: Debian 12 기반이지만 셸, 패키지 매니저 등이 모두 제거됨
- **특징**: Node.js 런타임만 포함. `sh`, `bash`, `apt` 등이 없어 `docker exec`로 셸 접속 불가.
- **용도**: 보안이 최우선인 프로덕션 환경

### 5.2 상세 비교 테이블

| 속성 | node:20 | node:20-slim | node:20-alpine | distroless |
|------|---------|-------------|---------------|------------|
| **이미지 크기** | ~1.1GB | ~240MB | ~130MB | ~120MB |
| **C 라이브러리** | glibc | glibc | musl libc | glibc |
| **셸 접속** | bash, sh | bash, sh | sh (busybox) | 불가 |
| **패키지 매니저** | apt | apt | apk | 없음 |
| **빌드 도구** | 포함 | 미포함 | 미포함 | 없음 |
| **CVE 수** | 많음 | 적음 | 매우 적음 | 최소 |
| **디버깅** | 매우 쉬움 | 쉬움 | 보통 | 어려움 |
| **native addon** | 완벽 호환 | 호환 (추가 설치 필요) | 주의 필요 | 사전 빌드 필요 |

### 5.3 Alpine의 musl libc 호환성 이슈

Alpine Linux는 glibc 대신 musl libc를 사용한다. 대부분의 순수 JavaScript 패키지는 문제가 없지만, C/C++ native addon을 사용하는 패키지에서 호환성 이슈가 발생할 수 있다.

**주의가 필요한 패키지들:**

| 패키지 | 문제 | 해결 방법 |
|--------|------|----------|
| `bcrypt` | musl에서 빌드 실패 가능 | `bcryptjs` (순수 JS) 사용 또는 빌드 도구 설치 |
| `sharp` | prebuilt 바이너리가 musl용 별도 제공 | `npm install --platform=linuxmusl` 또는 alpine용 자동 감지 |
| `prisma` | 엔진 바이너리 호환성 | `binaryTargets = ["linux-musl-openssl-3.0.x"]` 설정 |
| `canvas` | Cairo 등 시스템 라이브러리 필요 | `apk add` 로 의존성 설치 |
| `grpc` | native 빌드 필요 | `@grpc/grpc-js` (순수 JS) 사용 권장 |

Alpine에서 native addon을 빌드해야 하는 경우:

```dockerfile
FROM node:20-alpine

# native addon 빌드에 필요한 도구 설치
RUN apk add --no-cache python3 make g++

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .

CMD ["node", "server.js"]
```

### 5.4 실무 추천

```
┌─────────────────────────────────────────────────────┐
│            Node.js 베이스 이미지 선택 가이드           │
├─────────────────────────────────────────────────────┤
│                                                     │
│  native addon 필요?                                  │
│  ├── No  → node:20-alpine (대부분의 경우)             │
│  └── Yes → musl 호환?                                │
│            ├── Yes → node:20-alpine                  │
│            └── No  → node:20-slim                    │
│                                                     │
│  보안이 최우선? → distroless                          │
│  개발/디버깅용? → node:20 (풀 이미지)                  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

실무 Next.js 프로젝트의 프로덕션 Dockerfile 예시:

```dockerfile
# 빌드 스테이지: 풀 이미지로 빌드
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# 프로덕션 스테이지: 경량 이미지로 실행
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
CMD ["node", "server.js"]
```

> **핵심 통찰**: 멀티 스테이지 빌드를 활용하면 빌드에는 필요한 도구를 모두 사용하면서도, 최종 프로덕션 이미지는 최소한의 크기로 유지할 수 있다. 이에 대한 자세한 내용은 Ch 4(Dockerfile 심화)와 Ch 9(이미지 최적화)에서 다룬다.

---

## 6. 이미지 관리

### 6.1 이미지 목록 확인

```bash
# 로컬에 저장된 모든 이미지 목록
docker images
# 또는
docker image ls

# 출력 예시
REPOSITORY      TAG         IMAGE ID       CREATED        SIZE
my-next-app     1.0.0       a1b2c3d4e5f6   2 hours ago    180MB
my-next-app     latest      a1b2c3d4e5f6   2 hours ago    180MB
node            20-alpine   b2c3d4e5f6a7   3 days ago     130MB
```

참고: `my-next-app:1.0.0`과 `my-next-app:latest`가 같은 `IMAGE ID`를 가지고 있다면, 이 둘은 동일한 이미지를 가리키는 서로 다른 태그다. 디스크 공간은 한 번만 사용한다.

```bash
# 필터링 옵션
docker images node              # "node"로 시작하는 이미지만
docker images --filter "dangling=true"  # dangling 이미지만
docker images --format "{{.Repository}}:{{.Tag}} {{.Size}}"  # 커스텀 포맷
```

### 6.2 이미지 삭제

```bash
# 특정 이미지 삭제
docker image rm my-next-app:1.0.0
# 또는 축약 명령
docker rmi my-next-app:1.0.0

# IMAGE ID로 삭제
docker rmi a1b2c3d4e5f6

# 여러 이미지 한번에 삭제
docker rmi my-app:1.0 my-app:2.0 my-app:3.0
```

실행 중인 컨테이너가 사용하는 이미지는 삭제할 수 없다. `-f` 플래그로 강제 삭제할 수 있지만, 권장하지 않는다.

### 6.3 Dangling 이미지 정리

댕글링 이미지(*Dangling Image - 태그가 제거되어 `<none>:<none>`으로 표시되는 이미지*)는 빌드 과정에서 자연스럽게 발생한다.

예를 들어, `my-app:latest`를 두 번 빌드하면:

```bash
# 첫 번째 빌드
docker build -t my-app:latest .  # → IMAGE ID: aaa111

# 코드 수정 후 두 번째 빌드
docker build -t my-app:latest .  # → IMAGE ID: bbb222
# 이제 aaa111은 태그가 없어져서 dangling 상태가 된다
```

```bash
# dangling 이미지 확인
docker images --filter "dangling=true"

# REPOSITORY   TAG     IMAGE ID       SIZE
# <none>       <none>  aaa111bbb222   180MB

# dangling 이미지 일괄 삭제
docker image prune
# WARNING! This will remove all dangling images.
# Are you sure you want to continue? [y/N]: y

# 확인 없이 삭제 (-f 플래그)
docker image prune -f

# 모든 미사용 이미지 삭제 (컨테이너에서 사용하지 않는 모든 이미지)
docker image prune -a
# ⚠️ 주의: 현재 실행 중인 컨테이너가 사용하지 않는 모든 이미지를 삭제한다
```

### 6.4 디스크 사용량 확인

```bash
# 도커가 사용하는 전체 디스크 공간 요약
docker system df

# 출력 예시
TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
Images          15        3         4.2GB     3.1GB (73%)
Containers      5         2         120MB     80MB (66%)
Local Volumes   8         3         2.5GB     1.8GB (72%)
Build Cache     45        0         1.8GB     1.8GB (100%)

# 상세 정보 (-v 플래그)
docker system df -v
```

정기적인 정리:

```bash
# 미사용 이미지 + 중지된 컨테이너 + 미사용 네트워크 + 빌드 캐시 일괄 정리
docker system prune

# 미사용 볼륨까지 포함
docker system prune --volumes

# 확인 없이 실행
docker system prune -f
```

> **실무 팁**: CI/CD 서버에서는 빌드 후 `docker image prune -f`를 실행하거나, 주기적으로 `docker system prune`을 스케줄링하여 디스크 공간을 관리한다. 로컬 개발 환경에서도 한 달에 한 번 정도 `docker system prune -a`를 실행하면 불필요한 이미지를 정리할 수 있다.

### 6.5 이미지 태그 관리

```bash
# 기존 이미지에 새 태그 붙이기
docker tag my-next-app:latest ghcr.io/my-org/my-next-app:1.0.0

# 이 명령은 이미지를 복사하지 않는다 — 같은 이미지를 가리키는 새 태그를 만들 뿐이다
docker images
# my-next-app                    latest    a1b2c3d4   180MB
# ghcr.io/my-org/my-next-app     1.0.0     a1b2c3d4   180MB  ← 같은 IMAGE ID
```

---

## 7. 이미지 내보내기와 공유

레지스트리를 통한 push/pull이 이미지 배포의 표준이지만, 레지스트리를 사용할 수 없는 상황도 있다. 에어갭(*Air-gapped - 보안상 외부 네트워크와 완전히 분리된 환경*) 환경, 오프라인 배포, 이미지 백업, 다른 컨테이너 런타임(Podman 등)과의 이미지 공유 등이 그런 경우다.

### 7.1 container commit — 컨테이너에서 이미지 생성

`docker container commit`은 실행 중인 컨테이너의 현재 상태를 새로운 이미지로 저장하는 명령이다.

```bash
# 컨테이너의 현재 상태를 이미지로 저장
docker container commit my-container my-snapshot:v1

# 메타데이터와 함께 커밋
docker container commit \
  --author "developer@example.com" \
  --message "Added debugging tools" \
  my-container my-debug-image:latest
```

동작 원리:

```
┌─────────────────────────────┐
│ Container Layer (R/W)       │ ← 컨테이너에서 변경된 내용
├─────────────────────────────┤
│ Image Layers (R/O)          │ ← 원본 이미지 레이어들
└─────────────────────────────┘
            │
     docker commit
            ↓
┌─────────────────────────────┐
│ New Image                   │ ← R/W 레이어가 새 R/O 레이어로 확정
├─────────────────────────────┤
│ Original Image Layers (R/O) │
└─────────────────────────────┘
```

컨테이너의 R/W 레이어가 새로운 읽기 전용 레이어로 확정되어, 원본 이미지 레이어 위에 쌓인 새 이미지가 만들어진다.

> **실무 팁**: `commit`은 Dockerfile 기반 빌드를 대체하는 용도가 **아니다**. 재현 가능성이 없고, 어떤 변경이 이루어졌는지 추적할 수 없기 때문이다. 다만 다음과 같은 상황에서 유용하다:
> - 프로덕션에서 문제가 발생한 컨테이너의 상태를 스냅샷으로 보존하여 나중에 분석할 때
> - 디버깅 도구를 설치한 컨테이너를 임시 이미지로 만들어 팀에 공유할 때
> - Dockerfile 작성 전에 인터랙티브하게 이미지를 실험할 때

### 7.2 image save / image load — 이미지 tar 아카이브

`docker image save`는 이미지의 모든 레이어와 메타데이터를 tar 파일로 내보내고, `docker image load`는 이를 다시 이미지로 복원한다.

```bash
# 이미지를 tar 파일로 저장
docker image save -o my-next-app.tar my-next-app:1.0.0

# 여러 이미지를 하나의 tar로 묶기
docker image save -o stack.tar my-next-app:1.0.0 postgres:16-alpine redis:7-alpine

# tar 파일에서 이미지 복원
docker image load -i my-next-app.tar
# Loaded image: my-next-app:1.0.0
```

`save`/`load`는 **이미지의 모든 정보를 완전히 보존**한다 — 레이어 구조, 태그, 메타데이터(ENV, CMD, EXPOSE 등)가 그대로 유지된다.

**사용 사례:**

```bash
# 에어갭 환경으로 이미지 전달
docker image save my-next-app:1.0.0 | gzip > my-next-app.tar.gz
# USB나 보안 파일 전송으로 전달 후:
gunzip -c my-next-app.tar.gz | docker image load

# Podman과 이미지 공유 (OCI 호환)
docker image save my-next-app:1.0.0 | podman image load

# CI/CD에서 빌드 아티팩트로 저장
docker image save my-app:$CI_SHA -o image-artifact.tar
# 다른 파이프라인 단계에서 복원
docker image load -i image-artifact.tar
```

### 7.3 container export / image import — 파일시스템 tar 아카이브

`docker container export`는 컨테이너의 파일시스템을 **단일 레이어** tar로 내보내고, `docker image import`는 이를 새 이미지로 가져온다.

```bash
# 컨테이너의 파일시스템을 tar로 내보내기
docker container export my-container -o container-fs.tar

# tar를 새 이미지로 가져오기
docker image import container-fs.tar my-imported-image:v1

# 메타데이터를 함께 지정하여 가져오기
docker image import \
  --change 'CMD ["node", "server.js"]' \
  --change 'WORKDIR /app' \
  --change 'EXPOSE 3000' \
  container-fs.tar my-imported-image:v1
```

### 7.4 save/load vs export/import 비교

| 속성 | `save` / `load` | `export` / `import` |
|------|-----------------|---------------------|
| **대상** | 이미지 | 컨테이너 |
| **레이어 구조** | 보존 (모든 레이어 유지) | 보존 안 됨 (단일 레이어로 평탄화) |
| **메타데이터** | 보존 (ENV, CMD, EXPOSE 등) | 손실 (`--change`로 재지정 필요) |
| **태그** | 보존 | 새로 지정 필요 |
| **파일 크기** | 레이어별 중복 가능 → 더 클 수 있음 | 평탄화되어 더 작을 수 있음 |
| **용도** | 이미지 백업, 에어갭 배포, 런타임 간 공유 | 컨테이너 파일시스템 추출, 이미지 크기 축소 |

> **핵심 통찰**: 대부분의 경우 `save`/`load`를 사용하라. 레이어 구조와 메타데이터가 보존되어 원본 이미지와 동일하게 작동한다. `export`/`import`는 레이어를 평탄화하여 이미지 크기를 줄이고 싶은 특수한 경우에만 사용한다.

---

## 자주 하는 실수

| 실수 | 문제점 | 올바른 방법 |
|------|--------|-----------|
| `FROM node:latest` 사용 | 빌드할 때마다 다른 버전이 될 수 있어 재현 불가 | `FROM node:20-alpine` 처럼 구체적인 버전 명시 |
| 프로덕션에 `node:20` 풀 이미지 사용 | 1.1GB 크기, 불필요한 도구 포함, CVE 증가 | `node:20-alpine` 또는 `node:20-slim` 사용 |
| dangling 이미지 방치 | 디스크 공간 낭비 (수십 GB 누적 가능) | 정기적으로 `docker image prune` 실행 |
| CI에서 태그 고정 없이 빌드 | 같은 코드에서 다른 결과물 생성 가능 | semver + git SHA 태그 전략 사용 |
| 레이어 캐시를 고려하지 않은 COPY 순서 | 코드 한 줄 변경에도 `npm ci`가 매번 재실행 | `package*.json`을 먼저 COPY, 소스코드를 나중에 COPY |
| alpine에서 native addon 빌드 실패 무시 | 런타임 에러 또는 빌드 실패 | musl 호환성 확인, 필요 시 slim 사용 |
| 같은 태그를 재사용하며 push | 어떤 버전이 배포되었는지 추적 불가 | immutable 태그 전략 사용 (버전별 고유 태그) |

---

## 명령어 레퍼런스

| 명령어 | 설명 | 예시 |
|--------|------|------|
| `docker pull` | 레지스트리에서 이미지 다운로드 | `docker pull node:20-alpine` |
| `docker push` | 이미지를 레지스트리에 업로드 | `docker push ghcr.io/org/app:1.0` |
| `docker images` | 로컬 이미지 목록 조회 | `docker images --filter "dangling=true"` |
| `docker image inspect` | 이미지 메타데이터 상세 조회 (JSON) | `docker image inspect node:20-alpine` |
| `docker history` | 이미지 레이어 히스토리 확인 | `docker history my-app:1.0 --no-trunc` |
| `docker image rm` / `docker rmi` | 이미지 삭제 | `docker rmi my-app:old` |
| `docker image prune` | dangling 이미지 일괄 삭제 | `docker image prune -f` |
| `docker image prune -a` | 미사용 이미지 전체 삭제 | `docker image prune -a --filter "until=24h"` |
| `docker system df` | 도커 디스크 사용량 확인 | `docker system df -v` |
| `docker tag` | 이미지에 새 태그 부여 | `docker tag app:1.0 registry/app:1.0` |
| `docker login` | 레지스트리 인증 | `docker login ghcr.io` |
| `docker container commit` | 컨테이너 상태를 이미지로 저장 | `docker commit my-container my-snapshot:v1` |
| `docker image save` | 이미지를 tar 파일로 내보내기 | `docker image save -o app.tar my-app:1.0` |
| `docker image load` | tar 파일에서 이미지 복원 | `docker image load -i app.tar` |
| `docker container export` | 컨테이너 파일시스템을 tar로 내보내기 | `docker container export my-container -o fs.tar` |
| `docker image import` | tar를 새 이미지로 가져오기 | `docker image import fs.tar my-image:v1` |
| `docker system prune` | 미사용 리소스 일괄 정리 | `docker system prune --volumes` |

---

## 요약

- 도커 **이미지**는 컨테이너를 생성하기 위한 읽기 전용 파일시스템 스냅샷 + 메타데이터이며, 한번 빌드되면 **불변(immutable)**이다.
- 이미지는 여러 **레이어**로 구성되며, Dockerfile의 각 인스트럭션이 하나의 레이어를 생성한다. **OverlayFS**가 이 레이어들을 하나의 파일시스템으로 합쳐 보여준다.
- 같은 베이스 이미지를 사용하는 여러 이미지는 **레이어를 공유**하여 디스크 공간을 절약한다.
- 컨테이너는 이미지 위에 **R/W 레이어**를 추가하며, **Copy-on-Write** 전략으로 수정된 파일만 컨테이너 레이어에 복사한다.
- **태그**는 사람이 읽기 쉬운 이름이지만 **변경 가능(mutable)**하다. **다이제스트**는 SHA256 해시로 **불변(immutable)**이며 정확한 이미지를 보장한다.
- `:latest` 태그는 "최신"이라는 의미가 아니라 기본 태그일 뿐이다. 프로덕션에서는 구체적인 버전 태그를 사용한다.
- Node.js 프로젝트의 베이스 이미지는 대부분 **`node:20-alpine`**이 최적이다. native addon 호환성 문제가 있으면 `node:20-slim`을, 보안이 최우선이면 **distroless**를 선택한다.
- `docker image prune`과 `docker system df`로 정기적으로 이미지를 관리하여 디스크 공간을 확보한다.
- 레지스트리를 사용할 수 없는 환경에서는 **`docker image save/load`**로 이미지를 tar 파일로 내보내고 복원할 수 있다. `container commit`은 디버깅용 스냅샷에 유용하지만, Dockerfile 기반 빌드를 대체해서는 안 된다.

---

## 다른 챕터와의 관계

- **Ch 1 (Docker 기초)**: 도커의 기본 개념과 아키텍처를 이해한 위에서, 이 챕터는 이미지라는 핵심 빌딩 블록을 깊이 다룬다.
- **Ch 3 (컨테이너)**: 컨테이너는 이미지 위에 R/W 레이어를 추가한 실행 인스턴스다. 이 챕터에서 배운 레이어 구조와 CoW가 컨테이너의 동작 원리와 직결된다.
- **Ch 4 (Dockerfile 심화)**: Dockerfile의 각 인스트럭션이 어떻게 레이어를 생성하는지 이 챕터에서 배웠으며, Ch 4에서는 효율적인 Dockerfile 작성법을 다룬다.
- **Ch 9 (이미지 최적화)**: 멀티 스테이지 빌드, 레이어 캐시 최적화, 이미지 크기 줄이기 등 이 챕터의 개념을 실전에서 최적화하는 방법을 다룬다.
- **Ch 14 (CI/CD)**: 이 챕터에서 배운 태그 전략과 다이제스트 개념이 CI/CD 파이프라인에서 이미지를 안전하게 빌드하고 배포하는 데 핵심적으로 활용된다.
