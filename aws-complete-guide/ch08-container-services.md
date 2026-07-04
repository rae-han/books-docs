# Chapter 8: 컨테이너 서비스 - ECS와 Fargate: Container Services

## 핵심 질문

Docker 이미지를 AWS에서 어떻게 저장하고, 배포하고, 운영하는가? ECS의 핵심 개념(Cluster, Task Definition, Service)은 무엇이며, Fargate와 EC2 시작 유형은 어떻게 다른가? Docker Compose로 개발하던 애플리케이션을 프로덕션 수준의 ECS 아키텍처로 전환하려면 무엇을 고려해야 하는가?

---

## 1. AWS 컨테이너 서비스 생태계

### 1.1 전체 그림

AWS에서 컨테이너를 다루려면 네 가지 서비스의 역할을 먼저 이해해야 한다. Docker 이미지를 **저장**하고, **실행**하고, **관리**하는 각 단계에 대응하는 서비스가 분리되어 있다.

```
AWS 컨테이너 서비스 생태계:

┌──────────────────────────────────────────────────────────┐
│                                                          │
│  [저장]               [오케스트레이션]      [실행 환경]    │
│  ┌─────────┐         ┌─────────────┐     ┌───────────┐  │
│  │  ECR    │──이미지──→│    ECS     │────→│  Fargate  │  │
│  │(Registry)│   풀     │(Orchestrator)│     │(서버리스)  │  │
│  └─────────┘         └──────┬──────┘     └───────────┘  │
│                             │             ┌───────────┐  │
│                             └────────────→│    EC2    │  │
│                                           │(직접 관리) │  │
│                                           └───────────┘  │
│                                                          │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  EKS (Elastic Kubernetes Service)                   │ │
│  │  → K8s가 필요한 경우의 관리형 Kubernetes             │ │
│  └─────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

| 서비스 | 역할 | 한 줄 요약 |
|--------|------|-----------|
| **ECR** | 이미지 저장소 | AWS 전용 Docker Hub |
| **ECS** | 컨테이너 오케스트레이션 | "이 컨테이너를 몇 개, 어떻게 실행할지" 관리 |
| **Fargate** | 서버리스 실행 환경 | 서버 없이 컨테이너 실행 (ECS의 시작 유형) |
| **EKS** | 관리형 Kubernetes | AWS에서 K8s 클러스터 운영 |

> **핵심 통찰**: ECS와 Fargate를 혼동하기 쉽다. ECS는 **오케스트레이터**(무엇을 실행할지 결정)이고, Fargate는 **실행 환경**(어디서 실행할지 결정)이다. ECS는 반드시 Fargate 또는 EC2 중 하나의 시작 유형과 함께 사용한다.

### 1.2 Docker 지식과의 연결

이 챕터는 Docker의 핵심 개념을 알고 있다는 전제로 진행한다. [Docker 완전 가이드](../docker-complete-guide/README.md)에서 다룬 내용이 AWS 컨테이너 서비스와 어떻게 대응되는지 먼저 파악해두면 이해가 빠르다.

| Docker 개념 | AWS 대응 | Docker 가이드 참고 |
|-------------|----------|-------------------|
| Docker Hub / Registry | **ECR** | [Ch 02 이미지](../docker-complete-guide/ch02-images.md) |
| `docker run` | **ECS Task** | [Ch 03 컨테이너](../docker-complete-guide/ch03-containers.md) |
| Dockerfile | ECR에 푸시할 이미지 빌드 | [Ch 04 Dockerfile](../docker-complete-guide/ch04-dockerfile-deep-dive.md) |
| `docker-compose.yml` | **ECS Task Definition + Service** | [Ch 07 Compose](../docker-complete-guide/ch07-docker-compose.md) |
| `docker compose up --scale` | **ECS Service Auto Scaling** | [Ch 08 Compose 고급](../docker-complete-guide/ch08-docker-compose-advanced-patterns.md) |
| 멀티 스테이지 빌드, alpine | Fargate 콜드 스타트 최적화 | [Ch 09 이미지 최적화](../docker-complete-guide/ch09-image-optimization.md) |

---

## 2. ECR (Elastic Container Registry)

### 2.1 ECR이란

ECR(*Elastic Container Registry - AWS에서 제공하는 완전관리형 Docker 이미지 저장소*)은 Docker Hub의 AWS 버전이다. Docker Hub와 달리 **AWS IAM과 통합**되어 있어, 누가 이미지를 푸시/풀할 수 있는지를 IAM 정책으로 제어한다.

```
Docker Hub vs ECR:

Docker Hub:
  docker push myuser/nextjs-app:v1
  → hub.docker.com에 저장
  → 누구나 풀 가능 (public) 또는 유료 private

ECR:
  docker push 123456789.dkr.ecr.ap-northeast-2.amazonaws.com/nextjs-app:v1
  → AWS 계정의 ECR에 저장
  → IAM 인증 필요, VPC 엔드포인트로 프라이빗 접근 가능
```

### 2.2 리포지토리 생성과 이미지 푸시

```bash
# 1. ECR 리포지토리 생성
aws ecr create-repository \
  --repository-name nextjs-app \
  --image-scanning-configuration scanOnPush=true \
  --region ap-northeast-2

# 응답:
# {
#   "repository": {
#     "repositoryUri": "123456789.dkr.ecr.ap-northeast-2.amazonaws.com/nextjs-app"
#   }
# }

# 2. Docker CLI를 ECR에 인증 (12시간 유효한 토큰 발급)
aws ecr get-login-password --region ap-northeast-2 \
  | docker login --username AWS --password-stdin \
    123456789.dkr.ecr.ap-northeast-2.amazonaws.com

# 3. 이미지 빌드 (Docker 가이드 Ch 04, Ch 09 참고)
docker build -t nextjs-app:v1 .

# 4. ECR 리포지토리 URI로 태그 지정
docker tag nextjs-app:v1 \
  123456789.dkr.ecr.ap-northeast-2.amazonaws.com/nextjs-app:v1

# 5. 이미지 푸시
docker push 123456789.dkr.ecr.ap-northeast-2.amazonaws.com/nextjs-app:v1
```

> **실무 팁**: ECR 인증 토큰은 **12시간 후 만료**된다. CI/CD 파이프라인에서는 매 빌드마다 `aws ecr get-login-password`를 실행하여 인증을 갱신해야 한다. GitHub Actions에서는 `aws-actions/amazon-ecr-login` 액션을 사용하면 자동으로 처리된다.

### 2.3 이미지 스캔

ECR은 푸시된 이미지에 대해 **취약점 스캔**을 제공한다. `scanOnPush=true`로 설정하면 이미지를 푸시할 때마다 자동으로 CVE(*Common Vulnerabilities and Exposures - 공개적으로 알려진 보안 취약점 목록*) 기반 스캔이 실행된다.

```bash
# 수동 스캔 시작
aws ecr start-image-scan \
  --repository-name nextjs-app \
  --image-id imageTag=v1

# 스캔 결과 확인
aws ecr describe-image-scan-findings \
  --repository-name nextjs-app \
  --image-id imageTag=v1
```

Docker 가이드 [Ch 10 보안](../docker-complete-guide/ch10-security.md)에서 다룬 `docker scout` 같은 로컬 스캔 도구와 함께 사용하면, 로컬에서 먼저 스캔하고 ECR에서 한 번 더 검증하는 이중 방어가 가능하다.

### 2.4 수명 주기 정책 (Lifecycle Policy)

ECR에 이미지가 계속 쌓이면 스토리지 비용이 증가한다. 수명 주기 정책(*Lifecycle Policy*)으로 오래된 이미지를 자동 정리할 수 있다.

```bash
# 수명 주기 정책 설정
aws ecr put-lifecycle-policy \
  --repository-name nextjs-app \
  --lifecycle-policy-text '{
    "rules": [
      {
        "rulePriority": 1,
        "description": "최근 10개 이미지만 유지",
        "selection": {
          "tagStatus": "tagged",
          "tagPrefixList": ["v"],
          "countType": "imageCountMoreThan",
          "countNumber": 10
        },
        "action": {
          "type": "expire"
        }
      },
      {
        "rulePriority": 2,
        "description": "태그 없는 이미지는 1일 후 삭제",
        "selection": {
          "tagStatus": "untagged",
          "countType": "sinceImagePushed",
          "countUnit": "days",
          "countNumber": 1
        },
        "action": {
          "type": "expire"
        }
      }
    ]
  }'
```

> **실무 팁**: 태그 없는(*untagged*) 이미지는 새 이미지를 같은 태그로 푸시했을 때 기존 이미지에서 태그가 제거되면서 발생한다. 이를 방치하면 불필요한 스토리지 비용이 쌓이므로, 최소한 untagged 이미지 정리 규칙은 반드시 설정하라.

---

## 3. ECS 핵심 개념

### 3.1 네 가지 핵심 개념의 관계

ECS(*Elastic Container Service - AWS의 완전관리형 컨테이너 오케스트레이션 서비스*)를 이해하려면 네 가지 개념의 관계를 먼저 파악해야 한다.

```
ECS 핵심 개념 관계도:

┌─────────────────── Cluster ───────────────────────────┐
│                                                        │
│  ┌───── Service A ──────────────────────────────────┐  │
│  │  Task Definition: nextjs-task:3                  │  │
│  │  Desired Count: 3                                │  │
│  │                                                  │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐       │  │
│  │  │  Task 1  │  │  Task 2  │  │  Task 3  │       │  │
│  │  │┌────────┐│  │┌────────┐│  │┌────────┐│       │  │
│  │  ││Next.js ││  ││Next.js ││  ││Next.js ││       │  │
│  │  │└────────┘│  │└────────┘│  │└────────┘│       │  │
│  │  └──────────┘  └──────────┘  └──────────┘       │  │
│  └──────────────────────────────────────────────────┘  │
│                                                        │
│  ┌───── Service B ──────────────────────────────────┐  │
│  │  Task Definition: api-task:1                     │  │
│  │  Desired Count: 2                                │  │
│  │                                                  │  │
│  │  ┌──────────┐  ┌──────────┐                      │  │
│  │  │  Task 1  │  │  Task 2  │                      │  │
│  │  │┌────────┐│  │┌────────┐│                      │  │
│  │  ││  API   ││  ││  API   ││                      │  │
│  │  │└────────┘│  │└────────┘│                      │  │
│  │  └──────────┘  └──────────┘                      │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

| 개념 | 역할 | Docker 대응 |
|------|------|-----------|
| **Cluster** | 서비스들의 논리적 그룹. 리소스 격리 경계 | Docker Compose 프로젝트 |
| **Task Definition** | 컨테이너 실행 방법의 청사진 (이미지, CPU, 메모리, 포트, 환경 변수) | `docker-compose.yml`의 서비스 정의 |
| **Task** | Task Definition을 기반으로 실행된 컨테이너 인스턴스 | `docker run`으로 실행된 컨테이너 |
| **Service** | Task의 원하는 수를 유지하고, 로드밸런서와 연동하는 관리자 | `docker compose up --scale` + 자동 복구 |

### 3.2 Cluster 생성

Cluster(*ECS의 최상위 논리 그룹으로, 서비스와 태스크가 실행되는 공간*)는 ECS의 시작점이다.

```bash
# Fargate 전용 클러스터 생성
aws ecs create-cluster \
  --cluster-name my-app-cluster \
  --capacity-providers FARGATE FARGATE_SPOT \
  --default-capacity-provider-strategy \
    capacityProvider=FARGATE,weight=1 \
    capacityProvider=FARGATE_SPOT,weight=3
```

`FARGATE_SPOT`은 Fargate의 여유 용량을 할인된 가격(최대 70% 할인)으로 사용하는 옵션이다. 중단될 수 있으므로, 배치 작업이나 중단 허용 가능한 워크로드에 적합하다.

### 3.3 Task Definition 작성

Task Definition(*태스크 정의 - 컨테이너를 어떻게 실행할지 정의하는 JSON 템플릿*)은 ECS의 가장 핵심적인 설정이다. `docker-compose.yml`에서 서비스 하나를 정의하는 것과 같은 역할을 한다.

```json
{
  "family": "nextjs-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::123456789:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::123456789:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "nextjs",
      "image": "123456789.dkr.ecr.ap-northeast-2.amazonaws.com/nextjs-app:v1",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 3000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        { "name": "NODE_ENV", "value": "production" },
        { "name": "NEXT_PUBLIC_API_URL", "value": "https://api.example.com" }
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:ap-northeast-2:123456789:secret:prod/db-url"
        }
      ],
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:3000/api/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      },
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

**Task Definition 주요 필드 해설:**

| 필드 | 설명 |
|------|------|
| `family` | Task Definition의 이름. 버전은 자동 증가 (nextjs-task:1, :2, :3...) |
| `networkMode: awsvpc` | 각 Task에 고유 ENI(네트워크 인터페이스)를 할당. Fargate에서는 필수 |
| `cpu` / `memory` | Task 전체의 CPU/메모리 상한. Fargate에서는 허용 조합이 정해져 있다 |
| `executionRoleArn` | ECS 에이전트가 사용하는 역할 (ECR에서 이미지 풀, CloudWatch에 로그 전송) |
| `taskRoleArn` | 컨테이너 내부의 애플리케이션이 사용하는 역할 (S3 접근, DynamoDB 쿼리 등) |
| `essential` | `true`면 이 컨테이너가 죽으면 Task 전체가 중단 |
| `secrets` | AWS Secrets Manager 또는 SSM Parameter Store에서 비밀 값을 주입 |

**Fargate CPU/메모리 허용 조합:**

| CPU (vCPU) | 메모리 범위 |
|-----------|-----------|
| 256 (.25 vCPU) | 512 MB ~ 2 GB |
| 512 (.5 vCPU) | 1 GB ~ 4 GB |
| 1024 (1 vCPU) | 2 GB ~ 8 GB |
| 2048 (2 vCPU) | 4 GB ~ 16 GB |
| 4096 (4 vCPU) | 8 GB ~ 30 GB |

```bash
# Task Definition 등록
aws ecs register-task-definition \
  --cli-input-json file://task-definition.json

# 등록된 Task Definition 확인
aws ecs describe-task-definition \
  --task-definition nextjs-task:1
```

### 3.4 executionRole vs taskRole

ECS에는 두 가지 IAM 역할이 있으며, 이 둘을 혼동하면 권한 문제가 발생한다.

```
IAM 역할 비교:

┌──────────── ECS Task ─────────────────────────────┐
│                                                    │
│  executionRole (ECS 에이전트용)                      │
│  ├── ECR에서 이미지 풀                              │
│  ├── CloudWatch Logs에 로그 전송                    │
│  └── Secrets Manager에서 비밀 값 조회               │
│                                                    │
│  ┌────────── 컨테이너 ──────────┐                  │
│  │                              │                  │
│  │  taskRole (애플리케이션용)     │                  │
│  │  ├── S3 버킷 읽기/쓰기       │                  │
│  │  ├── DynamoDB 쿼리           │                  │
│  │  └── SQS 메시지 전송         │                  │
│  │                              │                  │
│  └──────────────────────────────┘                  │
└────────────────────────────────────────────────────┘
```

```bash
# executionRole 신뢰 정책 (ECS가 이 역할을 assume)
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

> **핵심 통찰**: `executionRole`은 ECS 인프라가 동작하기 위한 역할이고, `taskRole`은 우리 애플리케이션 코드가 AWS 서비스에 접근하기 위한 역할이다. 최소 권한 원칙(Ch 3 참고)에 따라, taskRole에는 애플리케이션이 실제로 필요한 권한만 부여해야 한다.

---

## 4. 시작 유형: EC2 vs Fargate

### 4.1 두 가지 선택지

ECS에서 Task를 "어디서" 실행할지는 시작 유형(*Launch Type*)으로 결정한다. EC2 인스턴스 위에서 직접 실행하거나, Fargate에 위임할 수 있다.

```
EC2 시작 유형:

개발자 → ECS → EC2 인스턴스 (직접 관리)
               ┌──────────────────┐
               │  EC2 Instance    │
               │  ┌──────┐       │  ← OS, Docker, 에이전트 관리 필요
               │  │ Task │       │  ← 인스턴스 크기, 수량 직접 결정
               │  └──────┘       │  ← 비용 최적화 가능 (RI, Savings Plan)
               │  ┌──────┐       │
               │  │ Task │       │
               │  └──────┘       │
               └──────────────────┘

Fargate 시작 유형:

개발자 → ECS → Fargate (AWS가 관리)
               ┌ ─ ─ ─ ─ ─ ─ ─ ─ ┐
                 인프라 보이지 않음
               │  ┌──────┐       │  ← 서버 관리 불필요
                  │ Task │          ← CPU/메모리만 지정
               │  └──────┘       │  ← Task 단위로 과금
                  ┌──────┐
               │  │ Task │       │
                  └──────┘
               └ ─ ─ ─ ─ ─ ─ ─ ─ ┘
```

### 4.2 상세 비교

| 항목 | EC2 시작 유형 | Fargate |
|------|-------------|---------|
| **인프라 관리** | EC2 인스턴스 직접 관리 (AMI, 패치, 스케일링) | 완전 관리형, 인프라 신경 쓸 필요 없음 |
| **비용 모델** | 인스턴스 단위 과금 (사용률 높을수록 유리) | Task 단위 과금 (vCPU + 메모리 초당) |
| **비용 최적화** | Reserved Instance, Savings Plan, Spot 사용 가능 | Fargate Spot (최대 70% 할인) |
| **스케일링** | ASG + ECS 용량 공급자로 인스턴스 스케일링 | Task 수만 조절하면 됨 |
| **시작 속도** | 빠름 (인스턴스가 이미 준비된 경우) | 30~60초 (새 Task 시작 시) |
| **GPU 지원** | 가능 (p3, g4 인스턴스) | 불가 |
| **운영 복잡도** | 높음 | 낮음 |
| **적합한 경우** | 대규모 트래픽, 비용 민감, GPU 필요 | 대부분의 웹 애플리케이션 (권장) |

> **비용 주의**: Fargate는 **동일한 CPU/메모리 기준으로 EC2보다 약 13~40% 비싸다.** 그러나 EC2의 운영 비용(패치, 모니터링, 스케일링 관리, 장애 대응)을 인건비로 환산하면 Fargate가 대부분의 팀에게 더 경제적이다. 월 100만 원 이상의 컴퓨팅 비용이 발생하는 시점부터 EC2 전환을 검토해볼 만하다.

### 4.3 Fargate를 권장하는 이유

대부분의 웹 애플리케이션에서 Fargate가 더 나은 선택인 이유:

1. **운영 부담 제로**: OS 패치, Docker 업데이트, 보안 패치를 AWS가 처리
2. **보안 강화**: 각 Task가 전용 커널에서 실행되어, 다른 고객의 워크로드와 완전히 격리
3. **정확한 리소스 할당**: 요청한 CPU/메모리가 보장됨 (EC2는 같은 인스턴스의 다른 Task와 경쟁)
4. **빠른 스케일링**: 인스턴스 추가 없이 Task 수만 늘리면 됨

```bash
# EC2 시작 유형: 인스턴스도 관리해야 함
aws ecs create-service \
  --cluster my-cluster \
  --service-name nextjs-ec2 \
  --task-definition nextjs-task:1 \
  --desired-count 2 \
  --launch-type EC2

# Fargate 시작 유형: 네트워크 설정만 하면 됨 (권장)
aws ecs create-service \
  --cluster my-cluster \
  --service-name nextjs-fargate \
  --task-definition nextjs-task:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={
    subnets=[subnet-private-a,subnet-private-b],
    securityGroups=[sg-ecs-tasks],
    assignPublicIp=DISABLED
  }"
```

---

## 5. ECS Service와 로드밸런서 연동

### 5.1 왜 로드밸런서가 필요한가

ECS Service로 여러 Task를 실행하면, 각 Task에 개별 IP가 할당된다. 사용자의 트래픽을 이 Task들에 균등하게 분산하고, 죽은 Task에는 트래픽을 보내지 않으려면 로드밸런서가 필수이다.

```
로드밸런서 없이:

사용자 → Task 1 (10.0.3.15)    ← IP 하드코딩 필요
       → Task 2 (10.0.4.22)    ← Task가 재시작되면 IP 변경
       → Task 3 (10.0.3.87)    ← 헬스 체크 없음

ALB + ECS Service:

사용자 → ALB (고정 DNS) → Target Group → Task 1 ✓
                                        → Task 2 ✓
                                        → Task 3 ✗ (unhealthy, 트래픽 제외)
```

### 5.2 ALB + Target Group + ECS Service 연동

ALB(*Application Load Balancer - HTTP/HTTPS 트래픽을 분산하는 L7 로드밸런서*)를 ECS Service와 연동하면, ECS가 Task의 생성/제거를 ALB Target Group에 자동으로 반영한다.

```
전체 아키텍처:

인터넷
  │
  ↓
┌──────────── VPC ───────────────────────────────────┐
│                                                     │
│  [퍼블릭 서브넷]                                     │
│  ┌──────────────────────────────────────────────┐   │
│  │  ALB (Application Load Balancer)             │   │
│  │  ├── 리스너: HTTPS:443                        │   │
│  │  └── 규칙: / → nextjs-tg                     │   │
│  └──────────────────┬───────────────────────────┘   │
│                      │                               │
│  [프라이빗 서브넷]    │                               │
│  ┌───────────────────┴──────────────────────────┐   │
│  │  Target Group: nextjs-tg                     │   │
│  │  ├── Task 1 (10.0.3.15:3000) ✓ healthy       │   │
│  │  ├── Task 2 (10.0.4.22:3000) ✓ healthy       │   │
│  │  └── Task 3 (10.0.3.87:3000) ✗ draining     │   │
│  └──────────────────────────────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

```bash
# 1. Target Group 생성 (IP 타입 — Fargate에서 필수)
aws elbv2 create-target-group \
  --name nextjs-tg \
  --protocol HTTP \
  --port 3000 \
  --vpc-id vpc-0abc123 \
  --target-type ip \
  --health-check-path /api/health \
  --health-check-interval-seconds 30 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 3

# 2. ALB 생성 (퍼블릭 서브넷에 배치)
aws elbv2 create-load-balancer \
  --name nextjs-alb \
  --subnets subnet-public-a subnet-public-b \
  --security-groups sg-alb \
  --scheme internet-facing \
  --type application

# 3. HTTPS 리스너 추가
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:...:loadbalancer/app/nextjs-alb/xxx \
  --protocol HTTPS \
  --port 443 \
  --ssl-policy ELBSecurityPolicy-TLS13-1-2-2021-06 \
  --certificates CertificateArn=arn:aws:acm:...:certificate/xxx \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:...:targetgroup/nextjs-tg/xxx

# 4. ECS Service에 로드밸런서 연동
aws ecs create-service \
  --cluster my-app-cluster \
  --service-name nextjs-service \
  --task-definition nextjs-task:1 \
  --desired-count 3 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={
    subnets=[subnet-private-a,subnet-private-b],
    securityGroups=[sg-ecs-tasks],
    assignPublicIp=DISABLED
  }" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:...:targetgroup/nextjs-tg/xxx,containerName=nextjs,containerPort=3000"
```

### 5.3 보안 그룹 설정

ALB와 ECS Task의 보안 그룹은 체이닝으로 구성한다. Ch 4에서 다룬 보안 그룹 간 참조 패턴을 적용한다.

```bash
# ALB 보안 그룹: 인터넷에서 HTTPS만 허용
aws ec2 create-security-group \
  --group-name sg-alb \
  --description "ALB security group" \
  --vpc-id vpc-0abc123

aws ec2 authorize-security-group-ingress \
  --group-id sg-alb \
  --protocol tcp --port 443 --cidr 0.0.0.0/0

# ECS Task 보안 그룹: ALB에서만 3000 포트 허용
aws ec2 create-security-group \
  --group-name sg-ecs-tasks \
  --description "ECS tasks security group" \
  --vpc-id vpc-0abc123

aws ec2 authorize-security-group-ingress \
  --group-id sg-ecs-tasks \
  --protocol tcp --port 3000 --source-group sg-alb
```

---

## 6. Auto Scaling

### 6.1 ECS Service Auto Scaling

ECS Service Auto Scaling(*서비스 수준의 자동 스케일링*)은 트래픽에 따라 Task 수를 자동으로 조절한다. Docker Compose의 `--scale`을 수동으로 실행하는 대신, AWS가 메트릭 기반으로 자동 판단한다.

```
Auto Scaling 흐름:

CloudWatch 메트릭 (CPU 75% 초과)
  ↓
Application Auto Scaling (정책 평가)
  ↓
ECS Service (desired count 3 → 5)
  ↓
Fargate (Task 2개 추가 실행)
  ↓
ALB Target Group (새 Task 자동 등록)
```

### 6.2 Target Tracking 정책

가장 일반적인 스케일링 전략은 Target Tracking(*목표 추적*)이다. "CPU 사용률을 70%로 유지하라"처럼 목표를 설정하면, ECS가 Task 수를 자동 조절한다.

```bash
# 1. Auto Scaling 대상 등록
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/my-app-cluster/nextjs-service \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 2 \
  --max-capacity 10

# 2. CPU 기반 Target Tracking 정책
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --resource-id service/my-app-cluster/nextjs-service \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name cpu-target-tracking \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{
    "TargetValue": 70.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
    },
    "ScaleInCooldown": 300,
    "ScaleOutCooldown": 60
  }'

# 3. 메모리 기반 Target Tracking 정책 (선택)
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --resource-id service/my-app-cluster/nextjs-service \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name memory-target-tracking \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{
    "TargetValue": 80.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ECSServiceAverageMemoryUtilization"
    },
    "ScaleInCooldown": 300,
    "ScaleOutCooldown": 60
  }'
```

| 파라미터 | 설명 | 권장 값 |
|---------|------|--------|
| `TargetValue` | 유지하고 싶은 메트릭 목표치 (%) | CPU 60~70%, 메모리 70~80% |
| `ScaleOutCooldown` | 스케일 아웃 후 다음 판단까지 대기 시간 (초) | 60초 (빠른 대응) |
| `ScaleInCooldown` | 스케일 인 후 다음 판단까지 대기 시간 (초) | 300초 (성급한 축소 방지) |
| `MinCapacity` | 최소 Task 수 | 2 (고가용성) |
| `MaxCapacity` | 최대 Task 수 | 비용 상한에 맞게 설정 |

> **실무 팁**: `ScaleInCooldown`(축소 대기)은 `ScaleOutCooldown`(확장 대기)보다 **충분히 길게** 설정하라. 트래픽이 잠시 줄었다고 Task를 즉시 줄이면, 다시 트래픽이 올라왔을 때 스케일 아웃 지연으로 서비스 품질이 저하된다.

---

## 7. Next.js SSR을 ECS Fargate로 배포하기

### 7.1 아키텍처 개요

Next.js SSR 서버를 프로덕션 수준으로 ECS Fargate에 배포하는 전체 아키텍처를 구성한다. Docker 가이드 [Ch 12 Node.js Docker Best Practices](../docker-complete-guide/ch12-nodejs-docker-best-practices.md)에서 다룬 최적화 기법을 기반으로 한다.

```
프로덕션 아키텍처:

Route 53 (DNS)
  │
  ↓
CloudFront (CDN) ── 정적 에셋 ──→ S3 (/_next/static/*)
  │
  ↓ (동적 요청)
ALB (HTTPS:443)
  │
  ↓
┌──────────── ECS Fargate (프라이빗 서브넷) ──────┐
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Next.js  │  │ Next.js  │  │ Next.js  │       │
│  │ Task 1   │  │ Task 2   │  │ Task 3   │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │              │              │             │
│       └──────────────┼──────────────┘             │
│                      │                            │
└──────────────────────┼────────────────────────────┘
                       │
              ┌────────┴────────┐
              │                 │
         RDS (PostgreSQL)  ElastiCache (Redis)
         (프라이빗 서브넷)   (프라이빗 서브넷)
```

### 7.2 Dockerfile (프로덕션 최적화)

Next.js standalone 모드를 활용한 최적화된 Dockerfile이다. 이미지 크기를 최소화하면 ECR 스토리지 비용과 Fargate 콜드 스타트 시간을 모두 줄일 수 있다.

```dockerfile
# === 1단계: 의존성 설치 ===
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --only=production

# === 2단계: 빌드 ===
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# === 3단계: 실행 (최소 이미지) ===
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# 보안: non-root 사용자
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# ECS 헬스 체크를 위한 curl 설치
RUN apk add --no-cache curl

CMD ["node", "server.js"]
```

`next.config.js`에서 standalone 모드를 활성화해야 한다:

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
};

module.exports = nextConfig;
```

### 7.3 Task Definition

```json
{
  "family": "nextjs-ssr",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::123456789:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::123456789:role/nextjsTaskRole",
  "containerDefinitions": [
    {
      "name": "nextjs",
      "image": "123456789.dkr.ecr.ap-northeast-2.amazonaws.com/nextjs-app:v1",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 3000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        { "name": "NODE_ENV", "value": "production" },
        { "name": "HOSTNAME", "value": "0.0.0.0" }
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:ap-northeast-2:123456789:secret:prod/database-url"
        },
        {
          "name": "REDIS_URL",
          "valueFrom": "arn:aws:ssm:ap-northeast-2:123456789:parameter/prod/redis-url"
        }
      ],
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:3000/api/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      },
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/nextjs-ssr",
          "awslogs-region": "ap-northeast-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### 7.4 배포 플로우

```
CI/CD 배포 파이프라인:

1. 코드 Push → GitHub
2. GitHub Actions 트리거
3. Docker 이미지 빌드 + ECR 푸시
4. Task Definition 업데이트 (새 이미지 태그)
5. ECS Service 업데이트 → 롤링 배포
6. ALB 헬스 체크 통과 → 구 Task 종료

타임라인:
  ├── 빌드 + 푸시: ~2~3분
  ├── 새 Task 시작: ~30~60초
  ├── 헬스 체크 통과: ~30초
  └── 구 Task 드레이닝 + 종료: ~30초
  총 약 4~5분
```

```bash
# ECS Service 업데이트 (새 Task Definition 버전으로 롤링 배포)
aws ecs update-service \
  --cluster my-app-cluster \
  --service nextjs-service \
  --task-definition nextjs-ssr:2 \
  --force-new-deployment

# 배포 상태 확인
aws ecs describe-services \
  --cluster my-app-cluster \
  --services nextjs-service \
  --query 'services[0].deployments'
```

---

## 8. Docker Compose에서 ECS로 전환할 때

### 8.1 핵심 차이점

Docker Compose로 개발하던 애플리케이션을 ECS로 전환할 때 가장 자주 부딪히는 차이점을 정리한다.

| Docker Compose | ECS/Fargate | 전환 시 유의사항 |
|---------------|------------|----------------|
| `volumes:` (로컬 볼륨) | EFS 또는 S3 | 컨테이너 내부 저장소는 Task 종료 시 사라짐 |
| `depends_on:` | 없음 | 애플리케이션에서 재연결 로직 구현 필요 |
| `localhost` 통신 | Task 내 컨테이너끼리만 localhost | 서비스 간 통신은 Service Discovery 또는 ALB 사용 |
| `.env` 파일 | Secrets Manager / SSM Parameter Store | 환경 변수를 AWS 비밀 관리 서비스에 저장 |
| `networks:` | VPC 서브넷 + 보안 그룹 | Ch 4의 VPC 설계가 그대로 적용 |
| `restart: always` | ECS Service가 자동 관리 | desired count 유지, 실패 시 자동 재시작 |
| `docker compose logs` | CloudWatch Logs | `awslogs` 드라이버 설정 필요 |
| 포트 매핑 (`8080:3000`) | ALB → Target Group → Task | 호스트 포트 개념이 없음 (awsvpc 모드) |

### 8.2 서비스 간 통신

Docker Compose에서는 서비스 이름으로 통신했다 (`http://api:3001`). ECS에서는 두 가지 방법이 있다.

**방법 1: Service Discovery (내부 DNS)**

```bash
# Cloud Map 네임스페이스 생성
aws servicediscovery create-private-dns-namespace \
  --name my-app.local \
  --vpc vpc-0abc123

# Service Discovery 서비스 등록
aws servicediscovery create-service \
  --name api \
  --namespace-id ns-xxx \
  --dns-config "NamespaceId=ns-xxx,DnsRecords=[{Type=A,TTL=10}]"

# ECS Service에 Service Discovery 연결
aws ecs create-service \
  --cluster my-app-cluster \
  --service-name api-service \
  --task-definition api-task:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --service-registries "registryArn=arn:aws:servicediscovery:...:service/srv-xxx" \
  --network-configuration "..."
```

이렇게 하면 ECS 내부에서 `api.my-app.local`로 다른 서비스에 접근할 수 있다. Docker Compose의 서비스 이름 DNS와 동일한 패턴이다.

**방법 2: 내부 ALB (Internal Load Balancer)**

트래픽 분산이 필요하거나, 서비스 간 헬스 체크가 중요한 경우 내부 ALB를 사용한다.

```bash
# Internal ALB (프라이빗 서브넷에 배치)
aws elbv2 create-load-balancer \
  --name internal-alb \
  --subnets subnet-private-a subnet-private-b \
  --security-groups sg-internal-alb \
  --scheme internal \
  --type application
```

### 8.3 영구 저장소

Docker Compose의 `volumes:`는 호스트 파일시스템에 데이터를 저장한다. ECS Fargate에서는 Task가 종료되면 로컬 저장소도 사라진다. 영구 저장소가 필요한 경우:

| 용도 | 해결 방법 |
|------|----------|
| 파일 업로드 | **S3**에 저장 (가장 일반적) |
| 공유 파일시스템 | **EFS** (Elastic File System) 마운트 |
| 데이터베이스 | **RDS** 또는 **DynamoDB** 사용 (컨테이너 내 DB 금지) |
| 캐시 | **ElastiCache** (Redis/Memcached) |

> **핵심 통찰**: Docker Compose에서 ECS로 전환할 때 가장 큰 마인드셋 전환은 **"컨테이너는 언제든 사라질 수 있다"**는 것이다. 상태(*state*)를 컨테이너 외부(S3, RDS, ElastiCache)에 저장하는 것이 클라우드 네이티브 설계의 핵심이다. 이 원칙은 Docker 가이드 [Ch 05 볼륨과 바인드 마운트](../docker-complete-guide/ch05-volumes-and-bind-mounts.md)에서 강조한 "데이터를 컨테이너 밖에 저장하라"의 연장이다.

---

## 9. EKS 간단 소개

### 9.1 EKS란

EKS(*Elastic Kubernetes Service - AWS에서 제공하는 관리형 Kubernetes 서비스*)는 Kubernetes의 컨트롤 플레인(*Control Plane - K8s 클러스터의 관리 계층. API 서버, 스케줄러, etcd 등으로 구성*)을 AWS가 관리해주는 서비스이다.

```
ECS vs EKS:

ECS:                                EKS:
┌────────────────────┐             ┌────────────────────┐
│ AWS 독자 API       │             │ Kubernetes API     │
│ Task Definition    │             │ Deployment YAML    │
│ Service            │             │ Service            │
│ Task               │             │ Pod                │
│                    │             │                    │
│ AWS에 최적화       │             │ 업계 표준, 이식성  │
│ 학습 곡선 낮음     │             │ 학습 곡선 높음     │
│ AWS 전용           │             │ 어디서든 동일      │
└────────────────────┘             └────────────────────┘
```

### 9.2 ECS vs EKS 선택 기준

| 기준 | ECS | EKS |
|------|-----|-----|
| **학습 곡선** | 낮음 (AWS만 알면 됨) | 높음 (K8s + AWS 모두 필요) |
| **운영 비용** | 컨트롤 플레인 무료 | 컨트롤 플레인 시간당 $0.10 (월 ~$73) |
| **이식성** | AWS 전용 | K8s 표준 → GCP, Azure로 이전 가능 |
| **생태계** | AWS 서비스와 깊은 통합 | Helm, Istio, ArgoCD 등 K8s 생태계 활용 |
| **멀티 클라우드** | 불가 | 가능 (동일 매니페스트 재사용) |
| **적합한 팀** | AWS 중심 소~중규모 팀 | K8s 경험 있는 팀, 멀티 클라우드 필요 |

> **실무 팁**: 이미 Kubernetes를 사용 중이거나 멀티 클라우드 전략이 있다면 EKS를, 그 외 대부분의 경우에는 ECS + Fargate를 선택하라. Docker 가이드 [Ch 15 Docker 너머](../docker-complete-guide/ch15-beyond-docker.md)에서 설명한 K8s 핵심 개념(Pod, Deployment, Service, Ingress)을 EKS에서 그대로 사용한다.

---

## 자주 하는 실수

| 실수 | 설명 | 올바른 접근 |
|------|------|------------|
| **Task에 Public IP를 직접 할당** | 보안 위험. 컨테이너가 인터넷에 직접 노출됨 | ALB를 퍼블릭 서브넷에, Task를 프라이빗 서브넷에 배치 |
| **executionRole과 taskRole을 하나로 합침** | 과도한 권한 부여 (ECR 풀 + 애플리케이션 권한을 하나의 역할에) | 역할을 분리하고 최소 권한 원칙 적용 |
| **헬스 체크를 설정하지 않음** | ECS가 컨테이너 상태를 판단할 수 없어, 죽은 Task에 계속 트래픽 전송 | Task Definition과 Target Group 양쪽 모두에 헬스 체크 설정 |
| **CPU/메모리를 너무 작게 설정** | Next.js 빌드 시 OOM 발생, 런타임 성능 저하 | SSR의 경우 최소 512 CPU / 1024 MB, 부하 테스트로 적정값 확인 |
| **ECR 수명 주기 정책 미설정** | 이미지가 무한히 쌓여 스토리지 비용 증가 | 최근 N개만 유지하는 수명 주기 정책 설정 |
| **`latest` 태그만 사용** | 어떤 버전이 배포되었는지 추적 불가, 롤백 어려움 | Git SHA 또는 시맨틱 버전으로 태그 (예: `v1.2.3`, `abc1234`) |
| **ScaleIn을 너무 공격적으로 설정** | 트래픽 감소 후 즉시 Task 축소 → 재증가 시 대응 지연 | ScaleInCooldown을 300초 이상으로 설정 |
| **Docker Compose의 DB를 그대로 ECS에 올림** | 컨테이너 내 DB는 Task 종료 시 데이터 손실 | RDS, DynamoDB 등 관리형 데이터베이스 사용 |

---

## AWS CLI 레퍼런스

### ECR

| 명령어 | 설명 |
|--------|------|
| `aws ecr create-repository --repository-name NAME` | ECR 리포지토리 생성 |
| `aws ecr get-login-password \| docker login ...` | ECR 인증 (12시간 유효) |
| `aws ecr describe-repositories` | 리포지토리 목록 조회 |
| `aws ecr list-images --repository-name NAME` | 이미지 목록 조회 |
| `aws ecr put-lifecycle-policy --repository-name NAME --lifecycle-policy-text JSON` | 수명 주기 정책 설정 |
| `aws ecr start-image-scan --repository-name NAME --image-id imageTag=TAG` | 이미지 취약점 스캔 |
| `aws ecr delete-repository --repository-name NAME --force` | 리포지토리 삭제 (이미지 포함) |

### ECS

| 명령어 | 설명 |
|--------|------|
| `aws ecs create-cluster --cluster-name NAME` | ECS 클러스터 생성 |
| `aws ecs register-task-definition --cli-input-json file://FILE` | Task Definition 등록 |
| `aws ecs create-service --cluster CLUSTER --service-name NAME ...` | ECS Service 생성 |
| `aws ecs update-service --cluster CLUSTER --service NAME --task-definition TD` | 서비스 업데이트 (배포) |
| `aws ecs describe-services --cluster CLUSTER --services NAME` | 서비스 상태 확인 |
| `aws ecs list-tasks --cluster CLUSTER --service-name NAME` | 실행 중인 Task 목록 |
| `aws ecs describe-tasks --cluster CLUSTER --tasks TASK_ARN` | Task 상세 정보 |
| `aws ecs stop-task --cluster CLUSTER --task TASK_ARN` | Task 강제 종료 |
| `aws ecs execute-command --cluster CLUSTER --task TASK --container NAME --interactive --command "/bin/sh"` | Task에 셸 접속 (디버깅) |
| `aws ecs delete-service --cluster CLUSTER --service NAME --force` | 서비스 삭제 |
| `aws ecs delete-cluster --cluster NAME` | 클러스터 삭제 |

### Auto Scaling

| 명령어 | 설명 |
|--------|------|
| `aws application-autoscaling register-scalable-target --service-namespace ecs ...` | 스케일링 대상 등록 |
| `aws application-autoscaling put-scaling-policy ...` | 스케일링 정책 설정 |
| `aws application-autoscaling describe-scaling-activities --service-namespace ecs` | 스케일링 활동 이력 조회 |

---

## 요약

- **AWS 컨테이너 생태계**는 ECR(이미지 저장), ECS(오케스트레이션), Fargate/EC2(실행 환경), EKS(관리형 K8s)로 구성된다.
- **ECR**은 AWS 전용 Docker 이미지 저장소이다. IAM 통합 인증, 이미지 스캔, 수명 주기 정책을 제공한다.
- **ECS**의 핵심 개념은 Cluster(논리 그룹), Task Definition(컨테이너 청사진), Service(원하는 Task 수 유지), Task(실행 인스턴스) 네 가지이다.
- **Fargate는 대부분의 웹 애플리케이션에 권장**되는 시작 유형이다. 서버 관리가 불필요하고 보안이 강화되지만, EC2 대비 13~40% 비싸다. 대규모 트래픽에서는 EC2 시작 유형이 비용 효율적일 수 있다.
- **ALB + Target Group**을 ECS Service에 연동하면, Task 생성/제거가 로드밸런서에 자동 반영된다.
- **Auto Scaling**은 Target Tracking 정책으로 CPU/메모리 사용률 기반 자동 스케일링을 구성한다. ScaleIn은 보수적으로, ScaleOut은 빠르게 설정하라.
- **Docker Compose에서 ECS 전환** 시 핵심은 "컨테이너는 언제든 사라질 수 있다"는 마인드셋이다. 상태를 S3, RDS, ElastiCache 등 외부 서비스에 저장한다.
- **EKS**는 Kubernetes가 필요한 경우(멀티 클라우드, K8s 생태계, 이식성)에 선택한다. 그 외에는 ECS + Fargate가 더 단순하고 비용 효율적이다.
- Task Definition의 **executionRole**(인프라용)과 **taskRole**(애플리케이션용)을 반드시 분리하여 최소 권한 원칙을 적용한다.
