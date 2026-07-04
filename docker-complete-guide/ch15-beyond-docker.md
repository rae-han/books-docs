# Chapter 15: Docker 너머 — 컨테이너 오케스트레이션: Beyond Docker

## 핵심 질문

단일 호스트의 Docker를 넘어 프로덕션 환경에서 컨테이너를 어떻게 대규모로 관리하는가? Kubernetes, 서버리스 컨테이너, 셀프호스팅 Next.js의 선택지는 무엇인가?

---

## 1. 왜 Docker만으로는 부족한가

### 1.1 단일 호스트의 한계

지금까지 이 가이드에서 다룬 모든 내용(Dockerfile, 볼륨, 네트워킹, Docker Compose)은 **단일 호스트**를 전제로 한다. 하나의 서버에서 `docker compose up`으로 모든 서비스를 실행하는 구조다. 사이드 프로젝트나 소규모 서비스라면 이것으로 충분하지만, 트래픽이 늘어나고 서비스가 커지면 근본적인 한계에 부딪힌다.

```
단일 호스트 구조의 한계:

┌─────────────────────────────┐
│         서버 1대              │
│  ┌───────┐ ┌───────┐        │
│  │ Next  │ │ Redis │        │ ← 이 서버가 죽으면?
│  │ .js   │ │       │        │ ← 트래픽이 서버 용량을 초과하면?
│  └───────┘ └───────┘        │ ← 무중단 배포를 하려면?
│  ┌───────┐                  │
│  │Postgres│                  │
│  └───────┘                  │
└─────────────────────────────┘
```

구체적으로 다음 문제가 발생한다:

- **가용성(*Availability*)**: 서버 한 대가 다운되면 전체 서비스가 중단된다. `docker compose`에는 다른 서버로 자동 전환하는 기능이 없다
- **확장성(*Scalability*)**: `docker compose up --scale web=3`으로 같은 호스트 내에서 컨테이너 수를 늘릴 수 있지만, 서버의 물리적 자원(CPU, 메모리)을 넘을 수 없다
- **로드 밸런싱**: Compose 자체에는 트래픽을 여러 컨테이너에 분산하는 내장 로드 밸런서가 없다
- **무중단 배포**: 새 버전을 배포할 때 기존 컨테이너를 내리고 새 컨테이너를 올리는 동안 다운타임이 발생한다

### 1.2 프로덕션에서 필요한 것들

프로덕션 환경에서 컨테이너를 안정적으로 운영하려면 Docker 단독으로는 제공할 수 없는 기능들이 필요하다:

| 기능 | 설명 | Docker만으로 가능한가? |
|------|------|----------------------|
| **자동 스케일링** | 트래픽에 따라 컨테이너 수를 자동 조절 | 불가능 |
| **셀프 힐링(*Self-healing*)** | 컨테이너가 죽으면 자동으로 재시작/재배치 | `restart: always`로 제한적 가능 |
| **롤링 업데이트** | 무중단으로 새 버전 배포 | 수동으로 복잡한 스크립트 필요 |
| **서비스 디스커버리** | 컨테이너 IP가 바뀌어도 자동으로 찾아감 | Compose 네트워크 내에서만 가능 |
| **멀티 호스트 네트워킹** | 여러 서버의 컨테이너가 통신 | 불가능 |
| **시크릿 관리** | 비밀 정보를 안전하게 주입 | Docker Secrets (Swarm 모드 전용) |

이러한 기능들을 제공하는 시스템을 컨테이너 오케스트레이터(*Container Orchestrator - 여러 호스트에 걸쳐 컨테이너의 배포, 스케일링, 관리를 자동화하는 시스템*)라고 부른다.

### 1.3 Docker Swarm — Docker 내장 오케스트레이터

Docker 자체에도 오케스트레이션 기능이 내장되어 있다. Docker Swarm(*Docker의 내장 클러스터링/오케스트레이션 도구*)은 여러 Docker 호스트를 하나의 가상 호스트처럼 관리할 수 있게 해준다.

```bash
# Swarm 모드 초기화
docker swarm init

# 서비스 생성 (3개 레플리카)
docker service create --name nextjs --replicas 3 -p 3000:3000 my-nextjs-app

# 서비스 스케일링
docker service scale nextjs=5

# 롤링 업데이트
docker service update --image my-nextjs-app:v2 nextjs
```

Docker Swarm은 Compose 파일과 거의 동일한 문법으로 멀티 호스트 배포가 가능하다는 장점이 있다. 그러나 2020년대 중반 현재, Kubernetes에 비해 **생태계, 커뮤니티, 클라우드 지원 모두에서 크게 뒤처져** 있어 새로운 프로젝트에서 선택하는 경우는 드물다.

> **핵심 통찰**: Docker Swarm이 나쁜 도구라서가 아니라, Kubernetes가 사실상 표준(*de facto standard*)이 되었기 때문에 선택의 문제다. 이미 Swarm을 사용 중인 소규모 팀이라면 굳이 마이그레이션할 필요는 없다.

---

## 2. Kubernetes 핵심 개념

### 2.1 Kubernetes란

쿠버네티스(*Kubernetes, K8s - 구글이 내부 컨테이너 관리 시스템 Borg를 기반으로 오픈소스화한 컨테이너 오케스트레이션 플랫폼*)는 컨테이너 오케스트레이션의 사실상 표준이다. "원하는 상태(*desired state*)"를 YAML로 선언하면, K8s가 현재 상태를 원하는 상태로 자동 수렴시킨다.

```
선언적 관리의 핵심:

개발자: "Next.js 컨테이너 3개가 항상 실행되어야 해"
  ↓ (YAML로 선언)
K8s:   "알겠어. 지금 2개만 돌고 있으니 1개 더 띄울게"
  ↓ (자동 조정)
K8s:   "1개가 죽었네. 다시 띄워서 3개 유지할게"
```

### 2.2 프론트엔드 개발자를 위한 K8s 핵심 개념

Kubernetes의 전체 생태계는 방대하지만, 프론트엔드/풀스택 개발자가 알아야 할 핵심 개념은 6가지다.

#### Pod

파드(*Pod - K8s의 최소 배포 단위*)는 하나 이상의 컨테이너를 묶은 그룹이다. 대부분의 경우 하나의 Pod에 하나의 컨테이너가 들어간다. Pod은 직접 생성하지 않고, Deployment를 통해 관리한다.

```yaml
# Pod 정의 (직접 사용하는 경우는 드묾)
apiVersion: v1
kind: Pod
metadata:
  name: nextjs-app
spec:
  containers:
    - name: nextjs
      image: my-registry/nextjs-app:v1.2.0
      ports:
        - containerPort: 3000
      resources:
        requests:
          memory: "128Mi"
          cpu: "250m"
        limits:
          memory: "256Mi"
          cpu: "500m"
```

#### Deployment

디플로이먼트(*Deployment — Pod의 원하는 상태(레플리카 수, 이미지 버전 등)를 선언적으로 관리하는 K8s 리소스*)는 Pod을 몇 개 실행할지, 어떤 이미지를 사용할지 등을 정의한다.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nextjs-deployment
spec:
  replicas: 3                    # Pod 3개 유지
  selector:
    matchLabels:
      app: nextjs
  strategy:
    type: RollingUpdate          # 무중단 배포 전략
    rollingUpdate:
      maxSurge: 1                # 최대 1개 추가 Pod 허용
      maxUnavailable: 0          # 배포 중 최소 3개 유지
  template:
    metadata:
      labels:
        app: nextjs
    spec:
      containers:
        - name: nextjs
          image: my-registry/nextjs-app:v1.2.0
          ports:
            - containerPort: 3000
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: app-secrets
                  key: database-url
          readinessProbe:        # 트래픽 받을 준비가 됐는지 확인
            httpGet:
              path: /api/health
              port: 3000
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:         # 컨테이너가 살아있는지 확인
            httpGet:
              path: /api/health
              port: 3000
            initialDelaySeconds: 15
            periodSeconds: 20
```

#### Service

서비스(*Service - Pod 집합에 대한 안정적인 네트워크 엔드포인트를 제공하는 K8s 리소스*)는 Pod의 IP가 변경되더라도 항상 동일한 주소로 접근할 수 있게 해준다. Docker Compose의 서비스 이름 기반 DNS와 비슷하지만, 멀티 호스트에서도 작동한다.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nextjs-service
spec:
  type: ClusterIP              # 클러스터 내부에서만 접근 가능
  selector:
    app: nextjs                # label이 app=nextjs인 Pod을 대상으로
  ports:
    - port: 80                 # Service가 노출하는 포트
      targetPort: 3000         # Pod의 실제 포트
```

주요 Service 타입:

| 타입 | 설명 | 사용 사례 |
|------|------|----------|
| `ClusterIP` | 클러스터 내부 통신용 | 백엔드 간 통신 |
| `NodePort` | 각 노드의 특정 포트를 개방 | 개발/테스트 |
| `LoadBalancer` | 클라우드 로드 밸런서 자동 생성 | 외부 노출 (단독 사용 시) |

#### Ingress

인그레스(*Ingress — 외부 HTTP(S) 트래픽을 클러스터 내부의 Service로 라우팅하는 K8s 리소스*)는 도메인 기반 라우팅과 TLS 종료를 처리한다. Nginx의 리버스 프록시와 비슷한 역할이다.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nextjs-ingress
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
    - hosts:
        - myapp.example.com
      secretName: myapp-tls
  rules:
    - host: myapp.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: nextjs-service
                port:
                  number: 80
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: api-service
                port:
                  number: 80
```

#### ConfigMap / Secret

컨피그맵(*ConfigMap*)은 환경 변수와 설정 파일을, 시크릿(*Secret*)은 비밀 정보를 Pod에 주입하는 데 사용한다. Docker Compose의 `environment`와 `.env` 파일에 대응한다.

```yaml
# ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  NODE_ENV: "production"
  NEXT_PUBLIC_API_URL: "https://api.example.com"

---
# Secret (값은 base64 인코딩)
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
data:
  database-url: cG9zdGdyZXM6Ly91c2VyOnBhc3NAaG9zdDo1NDMyL2Ri
  jwt-secret: c3VwZXItc2VjcmV0LWtleQ==
```

> **핵심 통찰**: K8s의 Secret은 기본적으로 base64 인코딩만 되어 있어 암호화가 아니다. 프로덕션에서는 HashiCorp Vault, AWS Secrets Manager, Sealed Secrets 같은 외부 비밀 관리 도구와 함께 사용해야 한다.

#### Namespace

네임스페이스(*Namespace - K8s 클러스터 내에서 리소스를 논리적으로 격리하는 단위*)를 사용하면 하나의 클러스터에서 여러 환경을 분리할 수 있다.

```bash
# 네임스페이스 생성
kubectl create namespace staging
kubectl create namespace production

# 특정 네임스페이스에 리소스 배포
kubectl apply -f deployment.yaml -n staging
```

### 2.3 Docker Compose와 K8s의 대응 관계

Docker Compose에 익숙하다면 다음 대응 관계를 통해 K8s 개념을 빠르게 이해할 수 있다:

| Docker Compose | Kubernetes | 설명 |
|---------------|-----------|------|
| `docker-compose.yml` | 여러 YAML 매니페스트 | 전체 애플리케이션 정의 |
| `services:` | Deployment + Service | 컨테이너 + 네트워크 설정 |
| `image:` | `spec.containers[].image` | 사용할 이미지 |
| `ports:` | Service + Ingress | 포트 노출 |
| `volumes:` | PersistentVolumeClaim | 영구 저장소 |
| `environment:` | ConfigMap + Secret | 환경 변수 |
| `networks:` | Namespace + NetworkPolicy | 네트워크 격리 |
| `depends_on:` | 없음 (Init Container로 대체) | 시작 순서 제어 |
| `restart: always` | 기본 동작 (셀프 힐링) | 자동 재시작 |
| `docker compose up` | `kubectl apply -f .` | 배포 실행 |
| `docker compose ps` | `kubectl get pods` | 상태 확인 |
| `docker compose logs` | `kubectl logs` | 로그 확인 |

### 2.4 K8s를 배워야 하는가?

역할과 프로젝트 규모에 따라 답이 다르다:

| 역할/상황 | K8s 필요도 | 권장 수준 |
|----------|----------|----------|
| 프론트엔드 개발자 (소규모 팀) | 낮음 | 개념만 이해 |
| 풀스택 개발자 (스타트업) | 중간 | 기본 배포 가능 수준 |
| DevOps / SRE | 높음 | 깊이 있는 운영 지식 |
| 개인 프로젝트 / 사이드 프로젝트 | 매우 낮음 | Docker Compose 또는 서버리스 |
| 엔터프라이즈 (대규모 팀) | 높음 | 팀 전체가 기본 개념 이해 |

> **핵심 통찰**: K8s는 복잡성 비용이 크다. 서비스가 2~3개이고 트래픽이 적다면 Docker Compose + 단일 서버로 충분하다. "우리도 K8s 써야 하지 않을까?"라는 불안감보다는 **실제 문제가 발생했을 때** 도입을 검토하는 것이 현명하다.

---

## 3. 서버리스 컨테이너

### 3.1 개념: 컨테이너 + 서버리스의 결합

서버리스 컨테이너(*Serverless Container*)는 Docker 이미지를 그대로 배포하되, **서버 인프라 관리는 클라우드 제공자가 전담**하는 모델이다. Kubernetes의 강력함이 필요하지만 직접 클러스터를 운영하고 싶지 않을 때 적합하다.

```
전통적 컨테이너 배포:
  개발자가 관리: [서버 구매] → [OS 설치] → [Docker 설치] → [네트워크 설정] → [배포] → [모니터링]

서버리스 컨테이너:
  개발자가 관리: [Dockerfile 작성] → [배포 명령 실행]
  클라우드가 관리: 서버, OS, 런타임, 스케일링, 네트워크, TLS
```

### 3.2 AWS Fargate

AWS Fargate(*AWS ECS/EKS의 서버리스 실행 모드*)는 EC2 인스턴스를 직접 관리하지 않고 컨테이너를 실행할 수 있게 해준다. ECS(*Elastic Container Service*)나 EKS(*Elastic Kubernetes Service*)와 함께 사용한다.

```bash
# AWS CLI로 Fargate 서비스 생성 (ECS 기반)
# 1. 클러스터 생성
aws ecs create-cluster --cluster-name nextjs-cluster

# 2. 태스크 정의 등록
aws ecs register-task-definition --cli-input-json file://task-definition.json

# 3. 서비스 생성
aws ecs create-service \
  --cluster nextjs-cluster \
  --service-name nextjs-service \
  --task-definition nextjs-task:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

태스크 정의 파일:

```json
{
  "family": "nextjs-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "nextjs",
      "image": "123456789.dkr.ecr.ap-northeast-2.amazonaws.com/nextjs-app:latest",
      "portMappings": [
        {
          "containerPort": 3000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        { "name": "NODE_ENV", "value": "production" }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/nextjs-app",
          "awslogs-region": "ap-northeast-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

- **장점**: 서버 관리 불필요, AWS 생태계와 완벽한 통합(ALB, CloudWatch, IAM 등)
- **단점**: 콜드 스타트(*Cold Start - 새 컨테이너가 시작될 때 초기화에 걸리는 시간*)가 존재, 비용이 EC2 대비 비쌈, AWS에 종속적

### 3.3 Google Cloud Run

Cloud Run(*Google Cloud의 서버리스 컨테이너 플랫폼*)은 서버리스 컨테이너 중 **가장 진입 장벽이 낮은** 플랫폼이다. Docker 이미지만 있으면 한 줄 명령으로 배포할 수 있다.

```bash
# 이미지 빌드 후 Artifact Registry에 푸시
gcloud builds submit --tag gcr.io/my-project/nextjs-app

# Cloud Run에 배포 — 이것이 전부다
gcloud run deploy nextjs-app \
  --image gcr.io/my-project/nextjs-app \
  --platform managed \
  --region asia-northeast3 \
  --allow-unauthenticated \
  --port 3000 \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars "NODE_ENV=production,DATABASE_URL=postgres://..."
```

Next.js standalone 모드와 함께 사용하는 Dockerfile 예시:

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=3000

COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000
CMD ["node", "server.js"]
```

Cloud Run의 핵심 특징:

- **0까지 축소(*Scale to Zero*)**: 트래픽이 없으면 인스턴스 수가 0이 되어 비용이 발생하지 않는다
- **자동 HTTPS**: 커스텀 도메인에 대한 TLS 인증서를 자동 발급한다
- **요청 기반 과금**: 실제 요청을 처리하는 시간만큼만 비용이 부과된다
- **콜드 스타트 주의**: 0에서 시작하는 경우 초기 요청이 느릴 수 있다. `--min-instances 1`로 최소 인스턴스를 유지하면 방지할 수 있지만, 상시 비용이 발생한다

### 3.4 Fly.io

Fly.io(*엣지 컨테이너 배포 플랫폼*)는 Docker 이미지를 전 세계 엣지 로케이션에 분산 배포할 수 있는 플랫폼이다. Vercel의 엣지 배포와 유사하지만, 컨테이너 수준의 자유도를 제공한다.

```bash
# Fly CLI 설치 후 프로젝트 초기화
fly launch
# → Dockerfile을 자동 감지하여 fly.toml 생성

# 배포
fly deploy

# 스케일링
fly scale count 3

# 리전 추가 (글로벌 분산)
fly regions add nrt  # 도쿄
fly regions add icn  # 서울 (가용 시)
```

`fly.toml` 설정 예시:

```toml
app = "my-nextjs-app"
primary_region = "nrt"          # 도쿄 리전

[build]
  dockerfile = "Dockerfile"

[env]
  NODE_ENV = "production"
  PORT = "3000"

[http_service]
  internal_port = 3000
  force_https = true
  auto_stop_machines = true      # 트래픽 없으면 자동 중지
  auto_start_machines = true     # 요청 오면 자동 시작
  min_machines_running = 1       # 최소 1대 유지

  [http_service.concurrency]
    type = "requests"
    hard_limit = 250
    soft_limit = 200

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 512
```

- **장점**: 글로벌 엣지 배포, 빠른 배포 속도, Dockerfile 그대로 사용, Postgres/Redis 내장 지원
- **단점**: 대규모 트래픽에서 비용 예측이 어려움, 특정 리전 가용성 제한

### 3.5 서버리스 컨테이너 플랫폼 비교

| 항목 | AWS Fargate | Google Cloud Run | Fly.io |
|------|------------|-----------------|--------|
| **복잡도** | 높음 (VPC, IAM 등 필요) | 낮음 | 낮음 |
| **Scale to Zero** | 불가 (최소 1 태스크) | 가능 | 가능 |
| **콜드 스타트** | 30~60초 | 1~10초 | 1~5초 |
| **글로벌 분산** | 리전별 수동 구성 | 리전 단위 | 엣지 자동 분산 |
| **가격 모델** | vCPU + 메모리 시간당 | 요청 + CPU 시간 | VM 시간당 |
| **무료 티어** | 없음 (12개월 프리티어) | 월 200만 요청 무료 | 3개 shared VM 무료 |
| **K8s 호환** | EKS 연동 가능 | 비호환 (독자 플랫폼) | 비호환 |
| **적합한 경우** | AWS 올인 기업 | GCP 사용자, 간단한 배포 | 인디/스타트업, 글로벌 서비스 |

> **핵심 통찰**: 서버리스 컨테이너의 가장 큰 적은 **콜드 스타트**다. Ch 9에서 다룬 이미지 최적화(멀티 스테이지 빌드, alpine 베이스, standalone 모드)가 여기서 직접적인 영향을 미친다. 이미지가 작을수록 컨테이너 시작이 빨라진다.

---

## 4. 셀프호스팅 Next.js 옵션

### 4.1 선택지 전체 지도

Next.js를 프로덕션에 배포하는 방법은 크게 6가지로 나뉜다:

```
┌─────────────────────────────────────────────────┐
│              Next.js 배포 옵션                    │
├─────────────┬───────────────────────────────────┤
│  관리형      │  Vercel (가장 쉬움)                │
│  (Managed)  │  Netlify                           │
├─────────────┼───────────────────────────────────┤
│  서버리스    │  Cloud Run / Fargate / Fly.io      │
│  컨테이너   │  (Docker + 클라우드 관리)            │
├─────────────┼───────────────────────────────────┤
│  셀프호스팅  │  Docker + VPS (완전한 통제)         │
│  (Self-     │  Docker + K8s (대규모)              │
│   hosted)   │  Coolify / Dokku (셀프 PaaS)       │
├─────────────┼───────────────────────────────────┤
│  IaC 기반   │  SST (AWS 기반 프레임워크)           │
└─────────────┴───────────────────────────────────┘
```

### 4.2 Vercel — 관리형 플랫폼

Vercel은 Next.js를 만든 회사의 공식 호스팅 플랫폼으로, **가장 쉬운 배포 경험**을 제공한다. Git 저장소를 연결하면 자동으로 빌드하고 배포한다.

- **장점**: 제로 설정, 자동 프리뷰 배포, 엣지 네트워크, ISR/SSR 네이티브 지원
- **단점**: 비용이 트래픽 증가 시 급격히 상승, 벤더 종속(*Vendor Lock-in*), 특정 Next.js 기능이 Vercel에서만 최적화

벤더 종속이 문제가 되는 이유:

```
Vercel 전용 기능 의존 시:
  Next.js Image Optimization → Vercel에서만 기본 제공
  ISR(Incremental Static Regeneration) → 다른 플랫폼에서는 추가 설정 필요
  Edge Middleware → Vercel 런타임에 최적화
  Analytics / Speed Insights → Vercel 전용
```

### 4.3 Docker + VPS — 완전한 통제

VPS(*Virtual Private Server - DigitalOcean, Hetzner, Vultr 등이 제공하는 가상 서버*)에 Docker로 직접 배포하는 방식이다. 가장 자유도가 높고, 비용도 예측 가능하다.

standalone 모드의 Docker Compose 배포 구성:

```yaml
# docker-compose.prod.yml
services:
  nextjs:
    build:
      context: .
      dockerfile: Dockerfile
    restart: always
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgres://user:pass@db:5432/myapp
    depends_on:
      db:
        condition: service_healthy
    networks:
      - app-network

  db:
    image: postgres:16-alpine
    restart: always
    volumes:
      - postgres-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d myapp"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - app-network

  caddy:
    image: caddy:2-alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - caddy-data:/data
      - caddy-config:/config
    depends_on:
      - nextjs
    networks:
      - app-network

volumes:
  postgres-data:
  caddy-data:
  caddy-config:

networks:
  app-network:
```

Caddy 리버스 프록시 설정 (자동 HTTPS 포함):

```
# Caddyfile
myapp.example.com {
    reverse_proxy nextjs:3000
    encode gzip

    header {
        X-Content-Type-Options nosniff
        X-Frame-Options DENY
        Referrer-Policy strict-origin-when-cross-origin
    }
}
```

Caddy(*Go 기반 웹 서버로, Let's Encrypt 자동 HTTPS를 기본 제공*)를 사용하면 단 3줄로 리버스 프록시 + 자동 HTTPS 설정이 완료된다. Nginx보다 설정이 훨씬 간결하다.

배포 플로우:

```bash
# VPS에 SSH 접속 후
cd /opt/myapp

# 최신 코드 가져오기
git pull origin main

# 이미지 빌드 및 서비스 재시작
docker compose -f docker-compose.prod.yml up -d --build

# 또는 CI/CD에서 이미지를 레지스트리에 푸시한 경우
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

### 4.4 Coolify / Dokku — 셀프호스팅 PaaS

직접 서버를 관리하면서도 Heroku/Vercel 같은 편의성을 원한다면 셀프호스팅 PaaS(*Platform as a Service*)가 답이다.

#### Coolify

Coolify(*Docker 기반 오픈소스 셀프호스팅 PaaS*)는 웹 UI를 통해 Docker 기반 애플리케이션을 배포하고 관리할 수 있는 도구다.

```bash
# Coolify 설치 (VPS에서 한 줄로 설치)
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
```

주요 특징:
- 웹 UI에서 Git 저장소 연결 → 자동 빌드/배포
- 자동 HTTPS (Let's Encrypt)
- 데이터베이스(Postgres, MySQL, Redis) 원클릭 배포
- 프리뷰 배포 지원
- 여러 서버를 하나의 대시보드로 관리

#### Dokku

Dokku(*미니 Heroku를 표방하는 오픈소스 PaaS*)는 `git push`만으로 배포할 수 있는 경량 PaaS다.

```bash
# Dokku 설치
wget -NP . https://dokku.com/install/v0.34.x/bootstrap.sh
sudo DOKKU_TAG=v0.34.8 bash bootstrap.sh

# 앱 생성
dokku apps:create nextjs-app

# Dockerfile 기반 배포 설정
dokku builder:set nextjs-app selected dockerfile

# 환경 변수 설정
dokku config:set nextjs-app NODE_ENV=production DATABASE_URL=postgres://...

# 도메인 설정
dokku domains:set nextjs-app myapp.example.com

# Let's Encrypt HTTPS
dokku letsencrypt:enable nextjs-app

# 로컬에서 git push로 배포
git remote add dokku dokku@your-server:nextjs-app
git push dokku main
```

### 4.5 SST (Serverless Stack)

SST(*AWS 위에서 풀스택 앱을 배포하는 Infrastructure as Code 프레임워크*)는 Next.js를 AWS Lambda, CloudFront, S3 등에 자동으로 분해하여 배포한다.

```typescript
// sst.config.ts
export default $config({
  app(input) {
    return {
      name: "my-nextjs-app",
      removal: input.stage === "production" ? "retain" : "remove",
    };
  },
  async run() {
    new sst.aws.Nextjs("Web", {
      domain: "myapp.example.com",
      environment: {
        DATABASE_URL: process.env.DATABASE_URL!,
      },
    });
  },
});
```

```bash
# 개발 환경
npx sst dev

# 프로덕션 배포
npx sst deploy --stage production
```

- **장점**: AWS 인프라를 코드로 관리, Next.js의 모든 기능 지원, 스테이지별 환경 분리
- **단점**: AWS에 종속, 학습 곡선, 디버깅이 복잡할 수 있음

### 4.6 선택 가이드 — 의사결정 테이블

| 기준 | Vercel | Docker + VPS | Cloud Run | Coolify/Dokku | SST | K8s |
|------|--------|-------------|-----------|--------------|-----|-----|
| **초기 설정 난이도** | 매우 쉬움 | 중간 | 쉬움 | 쉬움 | 중간 | 어려움 |
| **월 비용 (소규모)** | $0~20 | $5~10 | $0~5 | $5~10 | $1~10 | $50+ |
| **월 비용 (대규모)** | $100~1000+ | $20~100 | $50~200 | $20~100 | $50~200 | $200+ |
| **스케일링** | 자동 | 수동 | 자동 | 수동 | 자동 | 자동 |
| **벤더 종속** | 높음 | 없음 | 중간 | 없음 | 높음 (AWS) | 낮음 |
| **운영 부담** | 없음 | 높음 | 낮음 | 중간 | 낮음 | 매우 높음 |
| **적합한 팀** | 소규모, 빠른 출시 | 비용 민감, 통제 원함 | 중소규모 | 인디 개발자 | AWS 숙련 팀 | 대규모 조직 |

> **핵심 통찰**: 정답은 없다. "최적의 배포 방법"은 팀의 규모, 예산, 기술 역량, 트래픽 패턴에 따라 달라진다. 대부분의 사이드 프로젝트와 초기 스타트업에게는 **Vercel 또는 Docker + VPS**가 가장 합리적인 선택이다. K8s는 명확한 필요가 있을 때만 도입하라.

---

## 5. 컨테이너 생태계 도구

### 5.1 OCI 표준과 도구 호환성

Ch 1에서 다룬 OCI(*Open Container Initiative - 컨테이너 이미지 및 런타임의 개방형 표준*)가 여기서 빛을 발한다. Docker가 만든 이미지 형식과 런타임 스펙이 표준화되었기 때문에, Docker 외에도 다양한 도구가 동일한 컨테이너 이미지를 다룰 수 있다.

```
OCI 표준 덕분에:

docker build → 이미지 → docker run
podman build → 같은 이미지 → podman run
buildah bud → 같은 이미지 → cri-o로 실행
nerdctl build → 같은 이미지 → containerd로 실행

모든 도구가 동일한 이미지 형식을 공유한다.
```

### 5.2 Podman — Docker의 대안

Podman(*Pod Manager - Red Hat이 개발한 daemonless 컨테이너 엔진*)은 Docker와 CLI가 거의 동일하지만, **데몬 프로세스 없이** 컨테이너를 실행한다.

```bash
# Docker 명령어를 그대로 사용 가능
podman build -t my-app .
podman run -d -p 3000:3000 my-app
podman compose up -d        # docker-compose.yml 호환

# rootless 모드 — 일반 사용자 권한으로 컨테이너 실행
podman run --rm -p 3000:3000 my-nextjs-app
```

Docker와의 주요 차이점:

| 특성 | Docker | Podman |
|------|--------|--------|
| 데몬 | dockerd 상시 실행 필요 | 데몬 없음 (각 컨테이너가 독립 프로세스) |
| 루트 권한 | 기본적으로 root 필요 | rootless 기본 지원 |
| Pod 지원 | 없음 (단일 컨테이너) | K8s Pod 개념 네이티브 지원 |
| Compose | docker compose | podman-compose 또는 podman compose |
| 보안 | 데몬이 root로 실행 → 공격 표면 넓음 | 프로세스별 격리 → 보안 강화 |

### 5.3 기타 도구

- **nerdctl**: containerd(*Docker 내부에서 실제 컨테이너를 관리하는 런타임*)를 직접 사용하는 CLI로, Docker CLI와 호환된다. K8s 환경에서 Docker 없이 이미지를 빌드/관리할 때 유용하다

- **Buildah**: 이미지 빌드에 특화된 도구로, Dockerfile 없이 스크립트로 이미지를 조립할 수 있다. CI/CD 환경에서 보안을 강화하기 위해 빌드만 분리할 때 사용한다

- **Skopeo**: 이미지를 검사하거나 레지스트리 간에 복사하는 도구로, 이미지를 로컬에 다운로드하지 않고도 메타데이터를 확인할 수 있다

```bash
# Skopeo로 레지스트리의 이미지 정보 확인 (다운로드 없이)
skopeo inspect docker://docker.io/library/node:20-alpine

# 레지스트리 간 이미지 복사
skopeo copy docker://source-registry/my-app:v1 docker://dest-registry/my-app:v1
```

> **핵심 통찰**: 대부분의 개발자에게는 Docker만으로 충분하다. Podman이나 Buildah는 **보안 요구사항이 높은 기업 환경**이나 **Docker 라이선스가 문제되는 경우**에 대안으로 고려하면 된다.

---

## 6. 다음 학습 경로

### 6.1 이 가이드 이후 무엇을 학습해야 하는가

이 가이드에서 Docker의 기초부터 프로덕션 배포까지 다루었다. 다음 단계는 관심 분야에 따라 달라진다:

#### Kubernetes 심화

K8s를 본격적으로 학습하려면:

1. **minikube 또는 kind로 로컬 클러스터 구축**: 실제 클러스터 없이 로컬에서 실습
2. **공식 튜토리얼**: [kubernetes.io/docs/tutorials](https://kubernetes.io/docs/tutorials/)
3. **추천 서적**: *Kubernetes in Action* (Marko Luksa), *Kubernetes Up and Running* (Brendan Burns 외)
4. **Helm 학습**: K8s 패키지 매니저로, 복잡한 애플리케이션을 차트 단위로 관리

```bash
# minikube로 로컬 K8s 클러스터 시작
minikube start

# Next.js 배포 실습
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml

# 상태 확인
kubectl get pods -w
```

#### Infrastructure as Code (IaC)

인프라를 코드로 관리하면 환경을 재현 가능하고 버전 관리할 수 있다:

- **Terraform**: 클라우드 인프라를 선언적으로 관리하는 업계 표준 도구
- **Pulumi**: Terraform과 유사하지만, TypeScript/Python 등 일반 프로그래밍 언어로 인프라를 정의

```typescript
// Pulumi로 Cloud Run 서비스 정의 (TypeScript)
import * as gcp from "@pulumi/gcp";

const service = new gcp.cloudrun.Service("nextjs-app", {
  location: "asia-northeast3",
  template: {
    spec: {
      containers: [{
        image: "gcr.io/my-project/nextjs-app:latest",
        ports: [{ containerPort: 3000 }],
        resources: {
          limits: { memory: "512Mi", cpu: "1000m" },
        },
      }],
    },
  },
});
```

#### 모니터링과 관측 가능성

컨테이너를 배포한 후에는 상태를 모니터링해야 한다:

- **Prometheus + Grafana**: 메트릭 수집 및 시각화의 업계 표준 조합
- **Loki**: 로그 집계 (Ch 11의 Docker 로깅 확장)
- **OpenTelemetry**: 분산 트레이싱 표준

#### GitOps

Git 저장소를 "진실의 원천(*Single Source of Truth*)"으로 사용하여, Git에 변경사항을 푸시하면 자동으로 클러스터에 반영되는 패러다임:

- **ArgoCD**: K8s용 GitOps 컨트롤러, 선언적 배포 관리
- **Flux**: ArgoCD의 대안, CNCF 프로젝트

```
GitOps 워크플로우:

개발자 → Git push → CI가 이미지 빌드 → Git 매니페스트 업데이트
                                           ↓
                                    ArgoCD가 감지
                                           ↓
                                    K8s 클러스터에 자동 반영
```

---

## 자주 하는 실수

### 1. Kubernetes를 너무 일찍 도입한다

**문제**: "우리 서비스도 K8s를 써야 하지 않을까?"라는 FOMO로 팀 규모와 트래픽에 비해 과도한 인프라를 구축한다.

**현실**: 월 트래픽 수만~수십만 수준이라면 Docker Compose + 단일 VPS로 충분하다. K8s 클러스터 운영에는 전담 인력이 필요하다.

**기준**: 다음 중 하나라도 해당하면 K8s를 고려할 때다.
- 서버 3대 이상에 걸쳐 서비스를 분산해야 한다
- 자동 스케일링이 비즈니스 요구사항이다
- 여러 팀이 독립적으로 서비스를 배포해야 한다

### 2. 서버리스 컨테이너의 콜드 스타트를 무시한다

**문제**: Cloud Run이나 Fargate에 배포했는데 간헐적으로 첫 요청이 5~10초 걸린다.

**해결**:
- 이미지 크기 최적화 (Ch 9 참조)
- `min-instances`를 1 이상으로 설정
- 헬스체크 엔드포인트로 워밍업

### 3. 벤더 종속을 고려하지 않는다

**문제**: 특정 플랫폼의 전용 기능에 깊이 의존하다가, 비용 문제로 이전하려 할 때 막대한 마이그레이션 비용이 발생한다.

**예방**: Docker 이미지 기반으로 배포하면, 어떤 플랫폼이든 이전이 쉽다. 이것이 컨테이너의 핵심 가치 중 하나다.

### 4. Docker Compose를 프로덕션에서 그대로 사용한다

**문제**: 개발용 `docker-compose.yml`을 수정 없이 프로덕션에서 사용하면 보안, 성능, 안정성 문제가 발생한다.

**해결**: 프로덕션 전용 Compose 파일을 분리하고, 최소한 다음 항목을 확인한다.
- `restart: always` 설정
- 리소스 제한 (`deploy.resources.limits`)
- 헬스체크 정의
- 민감 정보를 환경 변수 파일 또는 시크릿으로 관리
- 리버스 프록시(Caddy/Nginx) 앞단 배치

---

## 명령어 레퍼런스

### kubectl (Kubernetes CLI)

```bash
# 리소스 배포/적용
kubectl apply -f deployment.yaml         # YAML 파일로 리소스 생성/업데이트
kubectl apply -f ./k8s/                  # 디렉토리 내 모든 YAML 적용

# 상태 확인
kubectl get pods                         # Pod 목록
kubectl get pods -w                      # 실시간 상태 감시
kubectl get services                     # Service 목록
kubectl get all -n production            # 특정 네임스페이스의 모든 리소스

# 상세 정보
kubectl describe pod <pod-name>          # Pod 상세 정보 (이벤트 포함)
kubectl describe deployment <name>       # Deployment 상세 정보

# 로그
kubectl logs <pod-name>                  # Pod 로그 출력
kubectl logs <pod-name> -f               # 실시간 로그 스트리밍
kubectl logs <pod-name> --previous       # 이전(크래시된) 컨테이너 로그

# 디버깅
kubectl exec -it <pod-name> -- /bin/sh   # Pod에 쉘 접속
kubectl port-forward svc/<name> 3000:80  # 로컬 포트를 Service로 포워딩

# 스케일링
kubectl scale deployment <name> --replicas=5

# 롤링 업데이트
kubectl set image deployment/<name> nextjs=my-app:v2
kubectl rollout status deployment/<name> # 업데이트 진행 상태 확인
kubectl rollout undo deployment/<name>   # 이전 버전으로 롤백
```

### gcloud (Google Cloud Run)

```bash
# 배포
gcloud run deploy <service> --image <image> --region <region>

# 서비스 목록
gcloud run services list

# 로그 확인
gcloud run services logs read <service>

# 트래픽 분할 (카나리 배포)
gcloud run services update-traffic <service> --to-revisions=v2=10,v1=90
```

### fly (Fly.io)

```bash
# 프로젝트 초기화
fly launch

# 배포
fly deploy

# 상태 확인
fly status

# 로그
fly logs

# 스케일링
fly scale count 3
fly scale vm shared-cpu-2x    # VM 사양 변경

# 시크릿 관리
fly secrets set DATABASE_URL=postgres://...
fly secrets list

# SSH 접속
fly ssh console
```

### Docker Compose (프로덕션)

```bash
# 프로덕션 파일 지정 배포
docker compose -f docker-compose.prod.yml up -d

# 이미지만 새로 빌드 후 재시작
docker compose -f docker-compose.prod.yml up -d --build

# 레지스트리에서 최신 이미지 가져오기
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d

# 특정 서비스만 재시작
docker compose -f docker-compose.prod.yml restart nextjs

# 리소스 사용량 확인
docker compose -f docker-compose.prod.yml top
docker stats
```

---

## 요약

- **Docker만으로는 프로덕션의 모든 요구를 충족할 수 없다.** 가용성, 자동 스케일링, 멀티 호스트 배포에는 오케스트레이터나 관리형 플랫폼이 필요하다
- **Kubernetes는 컨테이너 오케스트레이션의 표준**이지만, 복잡성 비용이 크다. Pod, Deployment, Service, Ingress, ConfigMap/Secret, Namespace 6가지 핵심 개념을 이해하면 기본 배포가 가능하다
- **서버리스 컨테이너(Cloud Run, Fargate, Fly.io)** 는 Docker 이미지를 그대로 사용하면서 인프라 관리 부담을 제거한다. 콜드 스타트와 비용 모델을 이해하고 선택해야 한다
- **셀프호스팅 Next.js 옵션**은 Vercel(가장 쉬움)부터 Docker + VPS(완전한 통제), Coolify/Dokku(셀프 PaaS), SST(AWS IaC)까지 다양하다. 팀 규모, 예산, 기술 역량에 맞게 선택한다
- **OCI 표준** 덕분에 Docker, Podman, Buildah, nerdctl 등 다양한 도구가 동일한 컨테이너 이미지를 호환한다. Docker에 종속될 걱정은 없다
- **다음 학습 경로**: Kubernetes 심화, IaC(Terraform/Pulumi), 모니터링(Prometheus/Grafana), GitOps(ArgoCD/Flux)

---

## 다른 챕터와의 관계

- **Ch 1 (도커란 무엇인가)**: OCI 표준의 중요성이 이 챕터에서 현실화된다. Docker가 만든 표준 덕분에 Podman, Buildah 등 대안 도구와 K8s 생태계가 가능해졌다
- **Ch 7~8 (Docker Compose)**: Compose는 단일 호스트 개발/테스트에 최적화된 도구다. 프로덕션에서는 이 챕터의 옵션들로 확장해야 한다. 단, 소규모 프로젝트에서는 Compose + VPS도 훌륭한 프로덕션 구성이다
- **Ch 9 (이미지 최적화)**: 이미지 크기가 서버리스 컨테이너의 콜드 스타트에 직접 영향을 미친다. 멀티 스테이지 빌드, alpine 베이스, standalone 모드가 여기서 실질적 가치를 발휘한다
- **Ch 10 (보안)**: K8s 환경에서의 보안은 Docker 보안(Ch 10)의 확장이다. Pod 보안 정책, RBAC, 네트워크 정책 등이 추가된다
- **Ch 14 (CI/CD)**: CI/CD 파이프라인의 마지막 단계인 "배포"의 대상이 이 챕터에서 다루는 플랫폼들이다. GitHub Actions에서 빌드한 이미지를 Cloud Run, K8s, Fly.io 등에 배포하는 흐름으로 연결된다