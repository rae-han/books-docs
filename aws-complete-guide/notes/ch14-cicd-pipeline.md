# Chapter 14: CI/CD 파이프라인 구축: Continuous Integration & Deployment

## 핵심 질문

코드를 푸시하면 테스트, 빌드, 배포까지 자동으로 이루어지는 파이프라인을 어떻게 구축하는가? AWS 자체 CI/CD 서비스(CodeBuild, CodePipeline)와 GitHub Actions를 각각 어떤 상황에서 선택해야 하며, OIDC를 이용한 안전한 인증은 어떻게 설정하는가? Blue/Green, Rolling, Canary 같은 배포 전략은 무엇이 다르고, 프론트엔드(S3 + CloudFront)와 백엔드(ECS) 배포 파이프라인은 실전에서 어떻게 구성하는가?

---

## 1. CI/CD 개념

### 1.1 CI/CD란

CI/CD(*Continuous Integration / Continuous Deployment - 코드 변경을 자동으로 빌드, 테스트, 배포하는 소프트웨어 개발 프랙티스*)는 소프트웨어 배포의 전 과정을 자동화하는 것이다. 수동으로 빌드하고, 수동으로 서버에 올리는 과정을 코드 한 줄의 푸시로 대체한다.

```
수동 배포 (CI/CD 없이):

개발자 → git push
개발자 → 로컬에서 npm run build
개발자 → scp로 서버에 파일 업로드
개발자 → SSH로 서버 접속 → 프로세스 재시작
개발자 → 동작 확인

→ 실수 가능, 느림, 반복적, 사람에 의존

CI/CD 파이프라인:

개발자 → git push → [자동] 테스트 → 빌드 → 배포 → 완료

→ 일관성, 빠름, 반복 가능, 자동화
```

### 1.2 CI와 CD의 구분

CI와 CD는 별개의 단계이며, 각각의 목적이 다르다.

| 단계 | 영문 | 목적 | 수행 작업 |
|------|------|------|----------|
| **CI** | Continuous Integration | 코드 변경이 기존 코드와 안전하게 통합되는지 확인 | 린트, 테스트 실행, 빌드 검증 |
| **CD (Delivery)** | Continuous Delivery | 배포 가능한 상태를 항상 유지 | 스테이징 배포, 수동 승인 후 프로덕션 배포 |
| **CD (Deployment)** | Continuous Deployment | 모든 변경을 자동으로 프로덕션까지 배포 | 승인 없이 자동 프로덕션 배포 |

```
CI/CD 단계 흐름:

코드 Push
  │
  ↓
┌──────────── CI (지속적 통합) ─────────────────┐
│  1. 코드 체크아웃                              │
│  2. 의존성 설치 (npm ci)                      │
│  3. 린트 검사 (eslint)                        │
│  4. 유닛 테스트 (jest)                        │
│  5. 빌드 (npm run build)                     │
└───────────────────────────────┬───────────────┘
                                │ 성공 시
                                ↓
┌──────── CD: Delivery (지속적 전달) ───────────┐
│  6. 스테이징 환경에 배포                       │
│  7. 통합 테스트 / E2E 테스트                  │
│  8. [수동 승인]                               │
└───────────────────────────────┬───────────────┘
                                │ 승인 시
                                ↓
┌──────── CD: Deployment (지속적 배포) ─────────┐
│  9. 프로덕션 배포                              │
│  10. 헬스 체크 확인                            │
│  11. 모니터링 (CloudWatch 알람)                │
└───────────────────────────────────────────────┘
```

### 1.3 CI/CD가 중요한 이유

| 이점 | 설명 |
|------|------|
| **빠른 피드백** | 코드 푸시 후 몇 분 내에 테스트 결과를 확인. 문제를 조기에 발견 |
| **배포 빈도 증가** | 자동화되어 있으므로 하루에도 여러 번 배포 가능 |
| **일관성** | 매번 동일한 프로세스로 빌드/배포. "내 컴퓨터에서는 되는데" 문제 해소 |
| **롤백 용이** | 이전 버전으로 즉시 롤백 가능 (배포 이력이 자동으로 남음) |
| **팀 협업 개선** | 코드 병합 시 자동 테스트로 충돌과 버그를 사전 차단 |

> **핵심 통찰**: CI/CD의 본질은 "자동화"가 아니라 **"피드백 루프의 단축"**이다. 코드를 작성한 시점과 문제를 발견하는 시점 사이의 시간을 최소화하면, 수정 비용이 기하급수적으로 줄어든다. 일주일 후 발견하는 버그보다 5분 후 발견하는 버그가 고치기 쉽다.

---

## 2. AWS CI/CD 서비스 생태계

### 2.1 전체 그림

AWS는 CI/CD의 각 단계에 대응하는 개별 서비스를 제공하며, 이를 CodePipeline으로 연결하여 전체 파이프라인을 구성한다.

```
AWS CI/CD 서비스 생태계:

┌──────────────────────────────────────────────────────────┐
│                    CodePipeline (오케스트레이션)            │
│                                                          │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐           │
│  │  Source   │───→│  Build   │───→│  Deploy  │           │
│  │          │    │          │    │          │           │
│  │ GitHub   │    │CodeBuild │    │CodeDeploy│           │
│  │ S3       │    │          │    │ ECS      │           │
│  │ ECR      │    │          │    │ S3       │           │
│  └──────────┘    └──────────┘    │ Lambda   │           │
│                                  └──────────┘           │
└──────────────────────────────────────────────────────────┘
```

| 서비스 | 역할 | 한 줄 요약 |
|--------|------|-----------|
| ~~**CodeCommit**~~ | ~~소스 코드 저장소~~ | **2024년 7월 서비스 종료**. GitHub/GitLab 사용 |
| **CodeBuild** | 빌드 서비스 | 소스 코드를 컴파일, 테스트, 패키징하는 완전관리형 빌드 서버 |
| **CodeDeploy** | 배포 서비스 | EC2, ECS, Lambda에 애플리케이션을 자동 배포 |
| **CodePipeline** | 파이프라인 오케스트레이션 | Source → Build → Deploy 단계를 연결하는 워크플로우 엔진 |

### 2.2 CodeCommit 종료와 대안

AWS CodeCommit은 2024년 7월에 신규 고객 접수를 중단하고 서비스가 종료되었다. AWS도 공식적으로 **GitHub**이나 **GitLab**과의 연동을 권장한다.

```
CodeCommit 종료 후 소스 선택지:

┌──────────────────────────────────────────────┐
│  [권장] GitHub / GitLab                       │
│  ├── CodePipeline의 소스 스테이지로 직접 연동  │
│  ├── GitHub Actions로 AWS 배포 (가장 인기)    │
│  └── 풍부한 생태계, 코드 리뷰, Actions 마켓   │
│                                              │
│  [대안] S3                                    │
│  └── ZIP 파일을 S3에 업로드하여 소스로 사용    │
│                                              │
│  [대안] ECR 이미지 변경                        │
│  └── 새 이미지 푸시를 트리거로 파이프라인 시작  │
└──────────────────────────────────────────────┘
```

> **실무 팁**: 2024년 이후로 AWS CI/CD를 구성할 때는 **GitHub + GitHub Actions**를 소스/CI 계층으로 사용하고, AWS 서비스(CodeDeploy, ECS, S3)를 배포 타깃으로 삼는 조합이 실무에서 가장 널리 쓰인다. CodePipeline + CodeBuild 조합은 AWS 서비스에 더 깊이 통합되지만, GitHub Actions의 유연성과 생태계를 따라가기 어렵다.

---

## 3. CodeBuild (빌드 서비스)

### 3.1 CodeBuild란

CodeBuild(*AWS CodeBuild - 소스 코드를 컴파일하고, 테스트를 실행하고, 배포 가능한 아티팩트를 생성하는 완전관리형 빌드 서비스*)는 Jenkins 같은 빌드 서버를 직접 운영할 필요 없이 AWS가 관리하는 빌드 환경에서 코드를 빌드한다.

```
CodeBuild 동작 흐름:

소스 코드 (GitHub, S3 등)
      │
      ↓
┌─────────────── CodeBuild 빌드 환경 ──────────────┐
│  Docker 컨테이너 (관리형 이미지)                    │
│                                                  │
│  1. 소스 다운로드                                 │
│  2. buildspec.yml의 명령 실행                     │
│     ├── install: 의존성 설치                     │
│     ├── pre_build: 빌드 전 준비                  │
│     ├── build: 빌드 실행                         │
│     └── post_build: 빌드 후 처리                 │
│  3. 아티팩트 생성 및 업로드                        │
│                                                  │
└──────────────────┬───────────────────────────────┘
                   │
                   ↓
          아티팩트 (S3, ECR 등)
```

### 3.2 buildspec.yml 작성법

`buildspec.yml`은 CodeBuild가 실행할 명령을 정의하는 파일이다. 프로젝트 루트에 위치시킨다.

```yaml
# buildspec.yml — 기본 구조
version: 0.2

env:
  variables:
    NODE_ENV: "production"
  parameter-store:
    DB_HOST: "/myapp/production/db-host"
  secrets-manager:
    DB_PASSWORD: "prod/db-creds:password"

phases:
  install:
    runtime-versions:
      nodejs: 20
    commands:
      - echo "의존성 설치 시작"
      - npm ci

  pre_build:
    commands:
      - echo "린트 및 테스트 실행"
      - npm run lint
      - npm run test

  build:
    commands:
      - echo "빌드 시작: $(date)"
      - npm run build
      - echo "빌드 완료: $(date)"

  post_build:
    commands:
      - echo "빌드 아티팩트 정리"

artifacts:
  files:
    - '**/*'
  base-directory: 'dist'

cache:
  paths:
    - 'node_modules/**/*'
```

**buildspec.yml 주요 섹션:**

| 섹션 | 역할 | 실행 순서 |
|------|------|----------|
| `env` | 환경 변수 정의. SSM Parameter Store, Secrets Manager 연동 가능 | 빌드 시작 전 |
| `phases.install` | 런타임 설치, 의존성 설치 | 1번째 |
| `phases.pre_build` | 빌드 전 준비 (로그인, 테스트 등) | 2번째 |
| `phases.build` | 실제 빌드 명령 | 3번째 |
| `phases.post_build` | 빌드 후 정리, 알림 전송 | 4번째 |
| `artifacts` | 빌드 결과물 정의. S3에 업로드될 파일 지정 | 빌드 완료 후 |
| `cache` | 캐시할 경로 지정. 다음 빌드 시 재사용하여 빌드 시간 단축 | 빌드 완료 후 |

### 3.3 Node.js 프로젝트 빌드 예시

```yaml
# buildspec.yml — Next.js 빌드
version: 0.2

phases:
  install:
    runtime-versions:
      nodejs: 20
    commands:
      - npm ci

  pre_build:
    commands:
      - npm run lint
      - npm run test -- --coverage --watchAll=false

  build:
    commands:
      - npm run build

artifacts:
  files:
    - '.next/**/*'
    - 'public/**/*'
    - 'package.json'
    - 'package-lock.json'
    - 'next.config.js'
  discard-paths: no

cache:
  paths:
    - 'node_modules/**/*'
    - '.next/cache/**/*'
```

### 3.4 Docker 이미지 빌드 + ECR 푸시

CodeBuild에서 Docker 이미지를 빌드하고 ECR에 푸시하는 것은 가장 흔한 사용 사례이다. Ch 8에서 다룬 ECR 인증과 이미지 푸시 과정을 buildspec.yml로 자동화한다.

```yaml
# buildspec.yml — Docker 빌드 + ECR 푸시
version: 0.2

env:
  variables:
    AWS_ACCOUNT_ID: "123456789012"
    AWS_REGION: "ap-northeast-2"
    ECR_REPO: "nextjs-app"
    IMAGE_TAG: "latest"

phases:
  pre_build:
    commands:
      # ECR 로그인
      - aws ecr get-login-password --region $AWS_REGION
          | docker login --username AWS --password-stdin
            $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
      # 이미지 태그를 Git 커밋 SHA로 설정
      - IMAGE_TAG=$(echo $CODEBUILD_RESOLVED_SOURCE_VERSION | head -c 7)
      - FULL_IMAGE="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO"

  build:
    commands:
      - echo "Docker 이미지 빌드 시작"
      - docker build -t $FULL_IMAGE:$IMAGE_TAG .
      - docker tag $FULL_IMAGE:$IMAGE_TAG $FULL_IMAGE:latest

  post_build:
    commands:
      - echo "ECR에 이미지 푸시"
      - docker push $FULL_IMAGE:$IMAGE_TAG
      - docker push $FULL_IMAGE:latest
      # ECS 배포를 위한 이미지 정보 파일 생성
      - printf '[{"name":"nextjs","imageUri":"%s"}]' $FULL_IMAGE:$IMAGE_TAG
          > imagedefinitions.json

artifacts:
  files:
    - imagedefinitions.json
```

> **실무 팁**: 이미지 태그에 `latest`만 사용하면 어떤 커밋이 배포되었는지 추적할 수 없다. **Git 커밋 SHA의 앞 7자리를 태그로 사용**하고, `latest`는 편의를 위해 함께 태그한다. CodeBuild의 `$CODEBUILD_RESOLVED_SOURCE_VERSION` 환경 변수가 현재 빌드의 Git SHA를 제공한다.

### 3.5 환경 변수와 Secrets Manager 연동

CodeBuild는 민감 정보를 세 가지 방법으로 관리한다.

```yaml
env:
  # 1. 일반 환경 변수 (평문, 비민감 정보에만 사용)
  variables:
    NODE_ENV: "production"
    AWS_REGION: "ap-northeast-2"

  # 2. SSM Parameter Store (암호화 지원)
  parameter-store:
    API_URL: "/myapp/prod/api-url"              # String
    DB_HOST: "/myapp/prod/db-host"              # SecureString (자동 복호화)

  # 3. Secrets Manager (자동 교체 지원)
  secrets-manager:
    DB_PASSWORD: "prod/db-creds:password"       # 시크릿이름:키
    API_KEY: "prod/external-api:key"
```

| 방법 | 적합한 정보 | 비용 |
|------|------------|------|
| `variables` | 비민감 설정 (NODE_ENV, 리전) | 무료 |
| `parameter-store` | 중간 수준 비밀 (DB 호스트, API URL) | 기본 무료 |
| `secrets-manager` | 고수준 비밀 (DB 비밀번호, API 키) | 시크릿당 $0.40/월 |

```bash
# CodeBuild 프로젝트 생성
aws codebuild create-project \
  --name nextjs-build \
  --source "type=GITHUB,location=https://github.com/myorg/nextjs-app.git" \
  --artifacts "type=NO_ARTIFACTS" \
  --environment "type=LINUX_CONTAINER,computeType=BUILD_GENERAL1_MEDIUM,image=aws/codebuild/amazonlinux2-x86_64-standard:5.0,privilegedMode=true" \
  --service-role arn:aws:iam::123456789012:role/CodeBuildServiceRole

# privilegedMode=true: Docker 빌드를 위해 필수
```

> **비용 주의**: CodeBuild는 **빌드 시간(분 단위)으로 과금**된다. `build.general1.small`(3 GB, 2 vCPU)은 분당 $0.005, `build.general1.medium`(7 GB, 4 vCPU)은 분당 $0.01이다. 월 100분의 무료 티어가 제공된다. Docker 빌드는 캐시를 적극 활용하고, 멀티 스테이지 빌드로 빌드 시간을 줄여라.

---

## 4. CodePipeline (파이프라인 오케스트레이션)

### 4.1 CodePipeline이란

CodePipeline(*AWS CodePipeline - 소스, 빌드, 테스트, 배포 단계를 연결하여 소프트웨어 릴리스 프로세스를 자동화하는 완전관리형 CI/CD 오케스트레이션 서비스*)은 여러 단계(Stage)를 연결하여 코드가 소스에서 프로덕션까지 흐르는 파이프라인을 구성한다. 각 단계에서 CodeBuild, CodeDeploy, Lambda 등 다양한 AWS 서비스를 액션으로 사용할 수 있다.

```
CodePipeline 기본 구조:

┌─────────┐    ┌─────────┐    ┌──────────┐    ┌─────────┐
│ Source   │───→│  Build  │───→│  Manual  │───→│ Deploy  │
│ Stage    │    │ Stage   │    │ Approval │    │ Stage   │
│          │    │         │    │ Stage    │    │         │
│ GitHub   │    │CodeBuild│    │ (선택적)  │    │CodeDeploy│
│ push     │    │ 빌드    │    │          │    │ ECS     │
└─────────┘    └─────────┘    └──────────┘    └─────────┘
     │
     │ 웹훅으로 자동 트리거
     │
  git push
```

### 4.2 Source → Build → Deploy 파이프라인

```bash
# CodePipeline 생성 (JSON 설정 파일 사용)
aws codepipeline create-pipeline --cli-input-json file://pipeline.json
```

```json
{
  "pipeline": {
    "name": "nextjs-pipeline",
    "roleArn": "arn:aws:iam::123456789012:role/CodePipelineServiceRole",
    "stages": [
      {
        "name": "Source",
        "actions": [
          {
            "name": "GitHub-Source",
            "actionTypeId": {
              "category": "Source",
              "owner": "ThirdParty",
              "provider": "GitHub",
              "version": "1"
            },
            "configuration": {
              "Owner": "myorg",
              "Repo": "nextjs-app",
              "Branch": "main",
              "OAuthToken": "{{resolve:secretsmanager:github-token}}"
            },
            "outputArtifacts": [{ "name": "SourceOutput" }]
          }
        ]
      },
      {
        "name": "Build",
        "actions": [
          {
            "name": "CodeBuild-Action",
            "actionTypeId": {
              "category": "Build",
              "owner": "AWS",
              "provider": "CodeBuild",
              "version": "1"
            },
            "configuration": {
              "ProjectName": "nextjs-build"
            },
            "inputArtifacts": [{ "name": "SourceOutput" }],
            "outputArtifacts": [{ "name": "BuildOutput" }]
          }
        ]
      },
      {
        "name": "Deploy",
        "actions": [
          {
            "name": "ECS-Deploy",
            "actionTypeId": {
              "category": "Deploy",
              "owner": "AWS",
              "provider": "ECS",
              "version": "1"
            },
            "configuration": {
              "ClusterName": "my-app-cluster",
              "ServiceName": "nextjs-service",
              "FileName": "imagedefinitions.json"
            },
            "inputArtifacts": [{ "name": "BuildOutput" }]
          }
        ]
      }
    ],
    "artifactStore": {
      "type": "S3",
      "location": "my-pipeline-artifacts-bucket"
    }
  }
}
```

### 4.3 GitHub 소스 연동 (v2 권장)

CodePipeline의 GitHub 연동에는 v1(OAuth 토큰)과 v2(CodeStar Connections)가 있다. v2가 보안과 기능 면에서 우수하다.

```bash
# 1. CodeStar Connection 생성 (콘솔에서 GitHub 앱 승인 필요)
aws codestar-connections create-connection \
  --provider-type GitHub \
  --connection-name my-github-connection

# 2. 콘솔에서 연결 승인 후 파이프라인에서 사용
# Source 스테이지 설정:
# {
#   "actionTypeId": {
#     "category": "Source",
#     "owner": "AWS",
#     "provider": "CodeStarSourceConnection",
#     "version": "1"
#   },
#   "configuration": {
#     "ConnectionArn": "arn:aws:codestar-connections:...:connection/xxx",
#     "FullRepositoryId": "myorg/nextjs-app",
#     "BranchName": "main"
#   }
# }
```

| 연동 방식 | 인증 | 장점 | 단점 |
|-----------|------|------|------|
| **v1 (OAuth)** | 개인 토큰 | 설정 간단 | 토큰 만료/유출 위험, 개인 계정에 의존 |
| **v2 (CodeStar)** | GitHub App | 조직 수준 권한, 세밀한 접근 제어 | 초기 설정에 콘솔 승인 필요 |

### 4.4 수동 승인 단계

프로덕션 배포 전 팀 리더나 QA가 승인하는 단계를 추가할 수 있다.

```json
{
  "name": "ManualApproval",
  "actions": [
    {
      "name": "Approve-Production",
      "actionTypeId": {
        "category": "Approval",
        "owner": "AWS",
        "provider": "Manual",
        "version": "1"
      },
      "configuration": {
        "NotificationArn": "arn:aws:sns:ap-northeast-2:123456789012:deploy-approval",
        "CustomData": "프로덕션 배포를 승인하시겠습니까? 스테이징 테스트 결과를 확인해주세요."
      }
    }
  ]
}
```

```bash
# SNS 토픽 생성 (승인 요청 알림용)
aws sns create-topic --name deploy-approval

# 이메일 구독 추가
aws sns subscribe \
  --topic-arn arn:aws:sns:ap-northeast-2:123456789012:deploy-approval \
  --protocol email \
  --notification-endpoint team-lead@example.com
```

수동 승인 단계에 도달하면 지정된 SNS 토픽으로 알림이 전송되고, 승인권자가 콘솔 또는 CLI에서 승인/거부할 수 있다.

```bash
# 파이프라인 상태 확인
aws codepipeline get-pipeline-state --name nextjs-pipeline

# 수동 승인 (CLI로 가능)
aws codepipeline put-approval-result \
  --pipeline-name nextjs-pipeline \
  --stage-name ManualApproval \
  --action-name Approve-Production \
  --result "summary=스테이징 테스트 통과,status=Approved" \
  --token TOKEN_FROM_GET_PIPELINE_STATE
```

---

## 5. GitHub Actions + AWS 연동

### 5.1 왜 GitHub Actions인가

실무에서 가장 많이 쓰이는 CI/CD 조합은 **GitHub Actions + AWS 서비스 배포**이다. CodePipeline을 사용하지 않고도 GitHub Actions만으로 AWS 배포를 완전히 자동화할 수 있다.

| 항목 | CodePipeline + CodeBuild | GitHub Actions |
|------|------------------------|----------------|
| **소스 관리** | GitHub/S3 연동 필요 | GitHub에 내장 |
| **워크플로우 정의** | JSON (복잡) | YAML (직관적) |
| **마켓플레이스** | 제한적 | 수천 개의 재사용 가능한 액션 |
| **비용** | 파이프라인당 $1/월 + CodeBuild 분당 과금 | Public 리포 무료, Private 리포 2,000분/월 무료 |
| **AWS 통합** | 네이티브 | OIDC 또는 액세스 키로 연동 |
| **유연성** | AWS 서비스에 특화 | 모든 클라우드, 모든 서비스에 대응 |
| **디버깅** | CloudWatch Logs | GitHub UI에서 즉시 확인 |

### 5.2 OIDC를 이용한 안전한 인증

GitHub Actions에서 AWS에 접근할 때 **액세스 키(Access Key)를 사용하면 안 된다.** 키가 유출되면 AWS 계정 전체가 위험해진다. 대신 OIDC(*OpenID Connect - 외부 ID 공급자를 통해 임시 보안 자격 증명을 발급받는 인증 프로토콜*)를 사용하면 **영구 키 없이** AWS 리소스에 접근할 수 있다.

```
액세스 키 방식 (위험):

GitHub Secrets에 AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY 저장
→ 키 유출 시 무제한 접근 가능
→ 키 교체가 수동
→ 모든 리포에서 같은 키를 공유할 위험

OIDC 방식 (권장):

GitHub Actions ──(OIDC 토큰)──→ AWS STS
                                  │
                                  ↓ 임시 자격 증명 발급 (1시간)
                                AWS 리소스 접근
→ 영구 키 불필요
→ 임시 자격 증명은 자동 만료
→ 리포/브랜치별로 접근 범위 제한 가능
```

**OIDC 설정 단계:**

```bash
# 1. GitHub OIDC 공급자 등록 (계정당 한 번만)
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1

# 2. IAM 역할 생성 (GitHub Actions가 assume할 역할)
aws iam create-role \
  --role-name GitHubActionsDeployRole \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {
          "Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com"
        },
        "Action": "sts:AssumeRoleWithWebIdentity",
        "Condition": {
          "StringEquals": {
            "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
          },
          "StringLike": {
            "token.actions.githubusercontent.com:sub": "repo:myorg/nextjs-app:*"
          }
        }
      }
    ]
  }'

# 3. 필요한 권한 정책 연결
aws iam attach-role-policy \
  --role-name GitHubActionsDeployRole \
  --policy-arn arn:aws:iam::123456789012:policy/DeployPolicy
```

> **핵심 통찰**: OIDC의 `Condition` 블록이 보안의 핵심이다. `repo:myorg/nextjs-app:*`는 특정 리포지토리의 워크플로우만 이 역할을 assume할 수 있도록 제한한다. 더 세밀하게 `repo:myorg/nextjs-app:ref:refs/heads/main`으로 설정하면 **main 브랜치에서 실행된 워크플로우만** AWS에 접근할 수 있다. 이렇게 하면 PR 브랜치에서는 프로덕션 배포가 불가능해진다.

### 5.3 S3 + CloudFront 배포 워크플로우

정적 프론트엔드(React SPA 등)를 S3에 업로드하고 CloudFront 캐시를 무효화하는 워크플로우이다.

```yaml
# .github/workflows/deploy-frontend.yml
name: Deploy Frontend to S3 + CloudFront

on:
  push:
    branches: [main]

permissions:
  id-token: write   # OIDC 토큰 발급에 필요
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm run test -- --watchAll=false

      - name: Build
        run: npm run build
        env:
          NEXT_PUBLIC_API_URL: ${{ vars.API_URL }}

      - name: Configure AWS Credentials (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsDeployRole
          aws-region: ap-northeast-2

      - name: Deploy to S3
        run: |
          aws s3 sync out/ s3://my-frontend-bucket \
            --delete \
            --cache-control "public, max-age=31536000, immutable" \
            --exclude "index.html" \
            --exclude "*.json"

          # index.html과 JSON은 캐시하지 않음
          aws s3 cp out/index.html s3://my-frontend-bucket/index.html \
            --cache-control "no-cache, no-store, must-revalidate"

      - name: Invalidate CloudFront Cache
        run: |
          aws cloudfront create-invalidation \
            --distribution-id E1234567890 \
            --paths "/index.html" "/*.json"
```

### 5.4 ECR 푸시 + ECS 배포 워크플로우

Docker 이미지를 ECR에 푸시하고 ECS 서비스를 업데이트하는 워크플로우이다. Ch 8에서 다룬 ECS 배포 플로우를 GitHub Actions로 자동화한다.

```yaml
# .github/workflows/deploy-backend.yml
name: Deploy Backend to ECS

on:
  push:
    branches: [main]

permissions:
  id-token: write
  contents: read

env:
  AWS_REGION: ap-northeast-2
  ECR_REPOSITORY: nextjs-app
  ECS_CLUSTER: my-app-cluster
  ECS_SERVICE: nextjs-service
  TASK_DEFINITION: task-definition.json
  CONTAINER_NAME: nextjs

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Configure AWS Credentials (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsDeployRole
          aws-region: ${{ env.AWS_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build, tag, and push image to ECR
        id: build-image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          echo "image=$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG" >> $GITHUB_OUTPUT

      - name: Download current task definition
        run: |
          aws ecs describe-task-definition \
            --task-definition nextjs-task \
            --query taskDefinition \
            > task-definition.json

      - name: Update task definition with new image
        id: task-def
        uses: aws-actions/amazon-ecs-render-task-definition@v1
        with:
          task-definition: ${{ env.TASK_DEFINITION }}
          container-name: ${{ env.CONTAINER_NAME }}
          image: ${{ steps.build-image.outputs.image }}

      - name: Deploy to ECS
        uses: aws-actions/amazon-ecs-deploy-task-definition@v2
        with:
          task-definition: ${{ steps.task-def.outputs.task-definition }}
          service: ${{ env.ECS_SERVICE }}
          cluster: ${{ env.ECS_CLUSTER }}
          wait-for-service-stability: true
```

### 5.5 Amplify 자동 배포 트리거

Amplify(Ch 13 참고)는 GitHub 연동 시 자동 배포가 내장되어 있다. 별도의 GitHub Actions 워크플로우 없이도 `git push`만으로 배포가 트리거된다. 그러나 Amplify 배포 전후로 추가 작업(E2E 테스트, Slack 알림 등)이 필요한 경우에는 GitHub Actions에서 Amplify를 제어할 수 있다.

```yaml
# .github/workflows/amplify-deploy.yml
name: Amplify Deploy with E2E Test

on:
  push:
    branches: [main]

permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsDeployRole
          aws-region: ap-northeast-2

      - name: Trigger Amplify deployment
        run: |
          aws amplify start-job \
            --app-id d1234567890 \
            --branch-name main \
            --job-type RELEASE

      - name: Wait for deployment
        run: |
          while true; do
            STATUS=$(aws amplify get-job \
              --app-id d1234567890 \
              --branch-name main \
              --job-id latest \
              --query 'job.summary.status' \
              --output text)
            echo "Deployment status: $STATUS"
            if [ "$STATUS" = "SUCCEED" ]; then break; fi
            if [ "$STATUS" = "FAILED" ]; then exit 1; fi
            sleep 15
          done

      - name: Run E2E tests against production
        run: |
          npx playwright test --config=e2e/playwright.config.ts
        env:
          BASE_URL: https://main.d1234567890.amplifyapp.com
```

---

## 6. 배포 전략

### 6.1 배포 전략 개요

새 버전을 프로덕션에 어떻게 반영하느냐에 따라 다운타임, 위험도, 롤백 속도가 달라진다.

```
배포 전략 비교:

[Rolling]
v1: ████████████████
      ↓ 하나씩 교체
v1: ████████    v2: ████
      ↓
v1: ████    v2: ████████
      ↓
v2: ████████████████

[Blue/Green]
Blue (v1): ████████████████  ← 현재 트래픽
Green (v2): ████████████████ ← 대기 (100% 준비)
      ↓ 트래픽 전환 (한 번에)
Blue (v1): ████████████████  ← 대기 (롤백용)
Green (v2): ████████████████ ← 현재 트래픽

[Canary]
v1: ████████████████  (100% 트래픽)
      ↓
v1: ██████████████    v2: ██  (v2에 5% 트래픽)
      ↓ 문제 없으면 점진적 확대
v1: ████████    v2: ████████  (v2에 50% 트래픽)
      ↓
v2: ████████████████  (v2에 100% 트래픽)
```

### 6.2 상세 비교

| 전략 | 다운타임 | 위험도 | 롤백 속도 | 리소스 비용 | 적합한 경우 |
|------|---------|--------|----------|------------|------------|
| **Rolling** | 없음 | 중간 (일시적으로 두 버전 공존) | 느림 (다시 롤링) | 기존과 동일 | ECS 기본 배포, 일반적인 서비스 |
| **Blue/Green** | 없음 | 낮음 (한 번에 전환) | 즉시 (이전 환경으로 전환) | 2배 (두 환경 동시 운영) | 데이터베이스 마이그레이션 동반, 무중단 필수 |
| **Canary** | 없음 | 가장 낮음 (소수만 노출) | 즉시 (카나리 중단) | 약간 추가 | 대규모 사용자, 변경 영향이 불확실할 때 |
| **All-at-once** | 있을 수 있음 | 높음 | 느림 | 기존과 동일 | 개발/테스트 환경 |

### 6.3 ECS에서의 배포 전략

```bash
# ECS Rolling Update (기본값)
aws ecs create-service \
  --cluster my-cluster \
  --service-name nextjs-service \
  --deployment-configuration "maximumPercent=200,minimumHealthyPercent=100" \
  --task-definition nextjs-task:2

# maximumPercent=200: 배포 중 Task 수가 최대 2배까지 증가 가능
# minimumHealthyPercent=100: 기존 Task를 모두 유지하면서 새 Task 추가

# ECS Blue/Green (CodeDeploy 필요)
aws deploy create-deployment-group \
  --application-name nextjs-app \
  --deployment-group-name nextjs-dg \
  --service-role-arn arn:aws:iam::123456789012:role/CodeDeployServiceRole \
  --ecs-services "clusterName=my-cluster,serviceName=nextjs-service" \
  --deployment-style "deploymentType=BLUE_GREEN,deploymentOption=WITH_TRAFFIC_CONTROL" \
  --blue-green-deployment-configuration '{
    "terminateBlueInstancesOnDeploymentSuccess": {
      "action": "TERMINATE",
      "terminationWaitTimeInMinutes": 60
    },
    "deploymentReadyOption": {
      "actionOnTimeout": "CONTINUE_DEPLOYMENT",
      "waitTimeInMinutes": 0
    }
  }' \
  --load-balancer-info '{
    "targetGroupPairInfoList": [{
      "targetGroups": [
        {"name": "nextjs-tg-blue"},
        {"name": "nextjs-tg-green"}
      ],
      "prodTrafficRoute": {
        "listenerArns": ["arn:aws:elasticloadbalancing:...:listener/..."]
      }
    }]
  }'
```

> **실무 팁**: ECS의 Rolling Update는 별도 설정 없이 바로 사용할 수 있고, 대부분의 웹 서비스에 충분하다. Blue/Green은 CodeDeploy와의 연동이 필요하여 설정이 복잡하지만, **데이터베이스 스키마 변경이 동반되는 배포**처럼 이전 버전과 새 버전이 동시에 동작하면 안 되는 경우에 필수적이다.

---

## 7. 환경별 파이프라인

### 7.1 환경 분리 전략

프로덕션에 바로 배포하는 것은 위험하다. 일반적으로 dev → staging → production의 단계를 거친다.

```
환경별 파이프라인:

feature 브랜치
  │
  └── PR → dev 환경에 자동 배포 (테스트용)
         │
         ↓
main 브랜치
  │
  ├── staging 환경에 자동 배포
  │     │
  │     ↓ E2E 테스트 + QA 검증
  │     │
  │     ↓ [수동 승인]
  │
  └── production 환경에 배포
```

### 7.2 GitHub Actions의 환경(Environment) 기능

GitHub Environments를 사용하면 환경별로 비밀 변수를 분리하고, 배포 보호 규칙(승인자, 대기 시간)을 설정할 수 있다.

```yaml
# .github/workflows/deploy.yml
name: Deploy to AWS

on:
  push:
    branches: [main, develop]

permissions:
  id-token: write
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'
      - run: npm ci
      - run: npm run test -- --watchAll=false
      - run: npm run build
      - uses: actions/upload-artifact@v4
        with:
          name: build-output
          path: out/

  deploy-staging:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: staging     # GitHub Environment 설정
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: build-output
          path: out/

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.AWS_ROLE_ARN }}  # staging용 역할
          aws-region: ap-northeast-2

      - name: Deploy to staging S3
        run: aws s3 sync out/ s3://${{ vars.S3_BUCKET }} --delete

      - name: Invalidate staging CloudFront
        run: |
          aws cloudfront create-invalidation \
            --distribution-id ${{ vars.CF_DISTRIBUTION_ID }} \
            --paths "/*"

  deploy-production:
    needs: deploy-staging
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production  # 수동 승인 필요 (GitHub 설정)
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: build-output
          path: out/

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.AWS_ROLE_ARN }}  # production용 역할
          aws-region: ap-northeast-2

      - name: Deploy to production S3
        run: aws s3 sync out/ s3://${{ vars.S3_BUCKET }} --delete

      - name: Invalidate production CloudFront
        run: |
          aws cloudfront create-invalidation \
            --distribution-id ${{ vars.CF_DISTRIBUTION_ID }} \
            --paths "/*"
```

### 7.3 환경별 설정 분리

| 항목 | dev | staging | production |
|------|-----|---------|------------|
| **트리거** | PR push | main push | 수동 승인 후 |
| **AWS 계정** | 개발용 계정 (별도) | 개발용 계정 (별도) | 프로덕션 계정 |
| **IAM 역할** | 넓은 권한 | staging 전용 | 최소 권한 |
| **도메인** | dev.example.com | staging.example.com | example.com |
| **데이터베이스** | 테스트 DB (초기화 가능) | 프로덕션 복제본 | 프로덕션 DB |
| **모니터링** | 기본 | 프로덕션과 동일 | 전체 알람 + 대시보드 |

> **핵심 통찰**: 환경 분리의 가장 중요한 원칙은 **"production 계정의 IAM 역할은 main 브랜치에서만 assume 가능하게 제한"**하는 것이다. OIDC의 Condition에 `repo:myorg/app:ref:refs/heads/main`을 명시하면, 어떤 개발자도 feature 브랜치에서 프로덕션에 배포할 수 없다.

---

## 8. 프론트엔드 배포 파이프라인 실전: Next.js → S3 + CloudFront

### 8.1 아키텍처

Next.js의 정적 내보내기(`output: 'export'`)를 S3에 호스팅하고 CloudFront로 서비스하는 전체 배포 파이프라인을 구성한다. Ch 9(S3)와 Ch 10(CloudFront)에서 다룬 인프라 위에 CI/CD를 올리는 구성이다.

```
프론트엔드 배포 파이프라인:

개발자 → git push (main)
            │
            ↓
┌─── GitHub Actions ──────────────────────────────────┐
│                                                      │
│  1. checkout                                        │
│  2. npm ci                                          │
│  3. npm run lint                                    │
│  4. npm run test                                    │
│  5. npm run build (next build → static export)      │
│  6. OIDC로 AWS 인증                                 │
│  7. S3 sync (빌드 결과물 업로드)                     │
│  8. CloudFront 무효화 (캐시 갱신)                    │
│                                                      │
└──────────────────────────────────────────────────────┘
            │
            ↓
┌─── AWS 인프라 ──────────────────────────────────────┐
│                                                      │
│  S3 (정적 파일 호스팅)                                │
│    └── CloudFront (CDN, HTTPS, 캐시)                │
│          └── Route 53 (커스텀 도메인)                 │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### 8.2 전체 워크플로우

```yaml
# .github/workflows/deploy-nextjs.yml
name: Deploy Next.js to S3 + CloudFront

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  id-token: write
  contents: read

env:
  NODE_VERSION: 20

jobs:
  # ===== CI: 테스트 및 빌드 =====
  ci:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Lint
        run: npm run lint

      - name: Type check
        run: npx tsc --noEmit

      - name: Unit tests
        run: npm run test -- --watchAll=false --coverage

      - name: Build
        run: npm run build
        env:
          NEXT_PUBLIC_API_URL: ${{ vars.API_URL }}
          NEXT_PUBLIC_GA_ID: ${{ vars.GA_ID }}

      - name: Upload build artifacts
        if: github.ref == 'refs/heads/main'
        uses: actions/upload-artifact@v4
        with:
          name: nextjs-build
          path: out/
          retention-days: 1

  # ===== CD: S3 + CloudFront 배포 =====
  deploy:
    needs: ci
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Download build artifacts
        uses: actions/download-artifact@v4
        with:
          name: nextjs-build
          path: out/

      - name: Configure AWS Credentials (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsDeployRole
          aws-region: ap-northeast-2

      # 정적 에셋: 장기 캐시 (해시가 파일명에 포함되어 있으므로 안전)
      - name: Upload static assets with long cache
        run: |
          aws s3 sync out/_next/static/ s3://my-frontend-bucket/_next/static/ \
            --cache-control "public, max-age=31536000, immutable"

      # HTML과 JSON: 캐시하지 않음 (항상 최신 버전 서비스)
      - name: Upload HTML and data files
        run: |
          aws s3 sync out/ s3://my-frontend-bucket/ \
            --exclude "_next/static/*" \
            --cache-control "public, max-age=0, must-revalidate"

      # 삭제된 파일 정리
      - name: Clean up old files
        run: |
          aws s3 sync out/ s3://my-frontend-bucket/ --delete

      # CloudFront 캐시 무효화 (HTML, JSON만)
      - name: Invalidate CloudFront cache
        run: |
          INVALIDATION_ID=$(aws cloudfront create-invalidation \
            --distribution-id ${{ vars.CF_DISTRIBUTION_ID }} \
            --paths "/index.html" "/*.html" "/*.json" \
            --query 'Invalidation.Id' \
            --output text)
          echo "Invalidation ID: $INVALIDATION_ID"

          # 무효화 완료 대기
          aws cloudfront wait invalidation-completed \
            --distribution-id ${{ vars.CF_DISTRIBUTION_ID }} \
            --id $INVALIDATION_ID

      - name: Verify deployment
        run: |
          HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://example.com)
          if [ "$HTTP_STATUS" != "200" ]; then
            echo "배포 검증 실패! HTTP 상태: $HTTP_STATUS"
            exit 1
          fi
          echo "배포 검증 성공 (HTTP $HTTP_STATUS)"
```

### 8.3 캐시 전략의 핵심

프론트엔드 배포에서 가장 흔한 문제는 **캐시 무효화**이다. 잘못된 캐시 설정은 사용자가 구 버전의 코드를 보게 만든다.

```
캐시 전략:

/_next/static/* (JS, CSS 번들)
  → Cache-Control: public, max-age=31536000, immutable
  → 파일명에 해시가 포함되어 있으므로 내용이 바뀌면 파일명도 바뀜
  → 영구 캐시해도 안전

/index.html, /*.json (HTML, 데이터)
  → Cache-Control: public, max-age=0, must-revalidate
  → 항상 최신 버전을 서비스
  → 새 JS/CSS 번들 경로를 참조하므로 캐시하면 안 됨

CloudFront 무효화:
  → HTML과 JSON 파일만 무효화
  → 정적 에셋은 해시 기반이므로 무효화 불필요
  → 무효화는 1,000경로/월 무료, 이후 경로당 $0.005
```

| 파일 유형 | 캐시 정책 | 이유 |
|-----------|----------|------|
| `/_next/static/*` | 1년 (immutable) | 파일명에 해시 포함. 내용 변경 = 파일명 변경 |
| `/index.html` | 캐시 없음 | 새 빌드의 JS/CSS 경로를 가리킴 |
| `/*.json` (데이터) | 캐시 없음 | 동적 데이터, 항상 최신이어야 함 |
| `/images/*` (직접 관리) | 1일~1주 | 변경 빈도에 따라 설정 |

> **비용 주의**: CloudFront 무효화(*Invalidation*)는 **월 1,000 경로까지 무료**이다. 와일드카드(`/*`)를 사용하면 전체 캐시가 무효화되어 오리진(S3) 요청이 급증한다. 꼭 필요한 경로만 무효화하고, 정적 에셋은 해시 기반 파일명으로 관리하여 무효화 자체를 최소화하라.

---

## 자주 하는 실수

| 실수 | 설명 | 올바른 접근 |
|------|------|------------|
| **GitHub Secrets에 AWS 액세스 키 저장** | 키 유출 시 AWS 계정 전체가 위험. 키 교체도 수동 | OIDC로 임시 자격 증명 사용. 영구 키 불필요 |
| **모든 환경에 동일한 IAM 역할 사용** | dev 환경에서 프로덕션 리소스에 접근 가능 | 환경별 IAM 역할 분리, OIDC Condition으로 브랜치 제한 |
| **CloudFront 전체 캐시 무효화(`/*`)** | 모든 에셋을 오리진에서 다시 가져옴. S3 요청 비용 증가 | 해시 기반 정적 에셋 + HTML/JSON만 선택적 무효화 |
| **buildspec.yml에 비밀 정보 하드코딩** | 소스 코드에 비밀 정보가 노출됨 | `env.secrets-manager` 또는 `env.parameter-store` 사용 |
| **테스트 없이 바로 배포** | 버그가 프로덕션에 직접 반영됨 | CI 단계에서 린트 + 테스트를 반드시 통과해야 배포 진행 |
| **환경별 분리 없이 프로덕션 직접 배포** | 롤백이 어렵고, 테스트 없이 사용자에게 노출 | dev → staging → production 순서로 단계적 배포 |
| **이미지 태그를 `latest`만 사용** | 어떤 버전이 배포되었는지 추적 불가. 롤백 어려움 | Git SHA 또는 시맨틱 버전으로 태그 (예: `abc1234`, `v1.2.3`) |
| **CodePipeline 아티팩트 버킷 미정리** | 빌드 아티팩트가 S3에 무한히 쌓임 | S3 수명 주기 정책으로 오래된 아티팩트 자동 삭제 |
| **GitHub Actions 캐시를 활용하지 않음** | 매 빌드마다 `npm install`로 수 분 소요 | `actions/setup-node`의 `cache: 'npm'`으로 의존성 캐시 |

---

## AWS CLI 레퍼런스

### CodeBuild

| 명령어 | 설명 |
|--------|------|
| `aws codebuild create-project --name NAME --source TYPE --environment TYPE --service-role ROLE` | CodeBuild 프로젝트 생성 |
| `aws codebuild start-build --project-name NAME` | 빌드 수동 시작 |
| `aws codebuild batch-get-builds --ids BUILD_ID` | 빌드 상태 조회 |
| `aws codebuild list-projects` | 프로젝트 목록 조회 |
| `aws codebuild list-builds-for-project --project-name NAME` | 프로젝트의 빌드 이력 조회 |
| `aws codebuild delete-project --name NAME` | 프로젝트 삭제 |

### CodePipeline

| 명령어 | 설명 |
|--------|------|
| `aws codepipeline create-pipeline --cli-input-json file://FILE` | 파이프라인 생성 |
| `aws codepipeline get-pipeline --name NAME` | 파이프라인 설정 조회 |
| `aws codepipeline get-pipeline-state --name NAME` | 파이프라인 실행 상태 확인 |
| `aws codepipeline start-pipeline-execution --name NAME` | 파이프라인 수동 실행 |
| `aws codepipeline list-pipelines` | 파이프라인 목록 조회 |
| `aws codepipeline put-approval-result --pipeline-name NAME --stage-name STAGE --action-name ACTION --result STATUS` | 수동 승인/거부 |
| `aws codepipeline delete-pipeline --name NAME` | 파이프라인 삭제 |

### CodeDeploy

| 명령어 | 설명 |
|--------|------|
| `aws deploy create-application --application-name NAME --compute-platform ECS` | CodeDeploy 애플리케이션 생성 |
| `aws deploy create-deployment-group --application-name NAME --deployment-group-name DG ...` | 배포 그룹 생성 |
| `aws deploy create-deployment --application-name NAME --deployment-group-name DG ...` | 배포 시작 |
| `aws deploy get-deployment --deployment-id ID` | 배포 상태 확인 |
| `aws deploy stop-deployment --deployment-id ID` | 배포 중단 |

### CloudFront (배포 관련)

| 명령어 | 설명 |
|--------|------|
| `aws cloudfront create-invalidation --distribution-id ID --paths "/*"` | 캐시 무효화 |
| `aws cloudfront wait invalidation-completed --distribution-id ID --id INVALIDATION_ID` | 무효화 완료 대기 |
| `aws cloudfront list-invalidations --distribution-id ID` | 무효화 이력 조회 |

---

## 요약

- **CI/CD**는 코드 변경을 자동으로 테스트, 빌드, 배포하는 프랙티스이다. CI(지속적 통합)는 코드 품질을, CD(지속적 배포)는 배포 자동화를 담당한다.
- **AWS CodeCommit은 2024년 종료**되었다. GitHub + GitHub Actions를 소스/CI 계층으로, AWS 서비스를 배포 타깃으로 삼는 조합이 실무 표준이다.
- **CodeBuild**는 `buildspec.yml`로 빌드 과정을 정의하는 완전관리형 빌드 서비스이다. Docker 빌드 + ECR 푸시, Node.js 프로젝트 빌드에 주로 사용한다.
- **CodePipeline**은 Source → Build → (승인) → Deploy 단계를 연결하는 오케스트레이터이다. 수동 승인 단계로 프로덕션 배포를 제어할 수 있다.
- **GitHub Actions + AWS 연동에서는 OIDC가 필수**이다. 영구 액세스 키 대신 임시 자격 증명을 사용하여 보안을 강화한다. Condition으로 리포지토리와 브랜치를 제한하라.
- **배포 전략**: Rolling(기본, 점진적 교체), Blue/Green(한 번에 전환, 즉시 롤백), Canary(소수에게 먼저 노출, 가장 안전)가 있다. ECS 기본 배포는 Rolling이며, Blue/Green은 CodeDeploy와 연동이 필요하다.
- **환경별 파이프라인**(dev → staging → production)으로 단계적 배포를 구성하고, 프로덕션 배포에는 수동 승인이나 브랜치 제한을 적용하라.
- **프론트엔드(S3 + CloudFront) 배포**에서 캐시 전략이 핵심이다. 해시 기반 정적 에셋은 영구 캐시, HTML은 캐시하지 않으며, CloudFront 무효화는 선택적으로 최소화한다.
- **비용 관점**: CodeBuild는 빌드 분당 과금(월 100분 무료), CodePipeline은 파이프라인당 $1/월, GitHub Actions는 퍼블릭 리포 무료/프라이빗 월 2,000분 무료이다.
