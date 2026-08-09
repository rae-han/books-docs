# Chapter 13: Amplify - 프론트엔드 배포 플랫폼: Frontend Deployment

## 핵심 질문

프론트엔드/풀스택 웹 애플리케이션을 AWS에 가장 빠르고 간편하게 배포하는 방법은 무엇인가? Git에 코드를 푸시하는 것만으로 자동 빌드, 배포, 프리뷰 환경 생성까지 할 수 있는가? Next.js SSR 앱도 서버 설정 없이 배포할 수 있는가?

---

## 1. Amplify란

### 1.1 Amplify의 정의

AWS Amplify(*Amplify - 프론트엔드/풀스택 웹 애플리케이션을 위한 완전 관리형 배포 플랫폼. Git 기반 CI/CD, 정적 호스팅, SSR 지원을 하나의 서비스로 제공한다*)는 프론트엔드 개발자가 AWS 인프라를 깊이 이해하지 않아도 웹 애플리케이션을 프로덕션 수준으로 배포할 수 있게 해주는 서비스이다.

Ch 9(S3)과 Ch 10(CloudFront)에서 정적 사이트 배포를 직접 구성하는 방법을 다뤘다. Amplify는 그 과정을 자동화하고, 여기에 CI/CD, SSR, 프리뷰 환경까지 추가한 상위 서비스이다.

```
Amplify가 자동으로 관리하는 것:

수동 배포 (S3 + CloudFront):
┌──────────────────────────────────────────────────┐
│ 1. npm run build                                 │
│ 2. aws s3 sync ./out s3://my-bucket              │
│ 3. aws cloudfront create-invalidation            │
│ 4. Route 53 레코드 설정                            │
│ 5. ACM에서 SSL 인증서 발급                         │
│ 6. CloudFront 배포 설정                            │
│ 모든 단계를 직접 구성해야 함                        │
└──────────────────────────────────────────────────┘

Amplify:
┌──────────────────────────────────────────────────┐
│ git push → 자동 빌드 → 자동 배포 → 끝             │
│                                                    │
│ SSL, CDN, CI/CD, 프리뷰 환경 모두 자동             │
└──────────────────────────────────────────────────┘
```

### 1.2 Amplify의 두 가지 측면

Amplify라는 이름은 여러 서비스를 포괄한다. 이 챕터에서는 **Amplify Hosting**에 집중한다.

| 구성 요소 | 역할 | 이 챕터 범위 |
|----------|------|------------|
| **Amplify Hosting** | Git 기반 CI/CD + 정적/SSR 호스팅 | 이 챕터의 핵심 |
| **Amplify Studio** | 비주얼 개발 환경 (데이터 모델링, UI 생성) | 다루지 않음 |
| **Amplify Libraries** | 프론트엔드 SDK (Auth, Storage, API 등) | 다루지 않음 |
| **Amplify Backend** | 백엔드 리소스 프로비저닝 (CDK 기반) | 다루지 않음 |

### 1.3 Amplify Hosting의 핵심 기능

Amplify Hosting은 다음을 하나의 서비스로 제공한다.

- **Git 기반 CI/CD**: GitHub, GitLab, Bitbucket, CodeCommit 연동
- **정적 사이트 호스팅**: React SPA, Vite, Gatsby 등
- **SSR 호스팅**: Next.js SSR/ISR/SSG 지원
- **글로벌 CDN**: CloudFront 기반 자동 배포
- **HTTPS 자동 설정**: SSL 인증서 자동 발급/갱신
- **브랜치별 배포**: `main` → 프로덕션, `develop` → 스테이징
- **PR 프리뷰**: Pull Request마다 임시 환경 자동 생성

```
Amplify 내부 아키텍처 (개발자에게는 보이지 않음):

Git Push
  │
  ↓
┌─────────────────────────────────────────────┐
│  Amplify 서비스 (자동 관리)                    │
│                                               │
│  ┌──────────┐    ┌──────────┐                │
│  │  빌드    │───→│ 배포      │                │
│  │  (CI)    │    │          │                │
│  └──────────┘    └────┬─────┘                │
│                       │                       │
│         ┌─────────────┼──────────────┐       │
│         ↓             ↓              ↓       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ CloudFront│  │  Lambda  │  │   S3     │  │
│  │ (CDN)    │  │ (SSR)    │  │ (정적)   │  │
│  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────┘
```

---

## 2. Amplify vs S3+CloudFront vs Vercel

### 2.1 배포 방법 비교

프론트엔드 애플리케이션을 배포하는 세 가지 주요 선택지를 비교한다.

| 항목 | Amplify | S3 + CloudFront | Vercel |
|------|---------|----------------|--------|
| **설정 난이도** | 낮음 (Git 연결만으로 시작) | 높음 (S3, CloudFront, Route 53, ACM 개별 설정) | 매우 낮음 (GitHub 연결 원클릭) |
| **CI/CD** | 내장 | 별도 구성 필요 (CodePipeline/GitHub Actions) | 내장 |
| **SSR 지원** | Next.js SSR 지원 | 정적 사이트만 | Next.js에 최적화 (제작사) |
| **프리뷰 환경** | PR 프리뷰 지원 | 직접 구현 필요 | PR 프리뷰 지원 |
| **커스터마이징** | 중간 (amplify.yml로 빌드 설정) | 높음 (모든 것을 직접 제어) | 낮음~중간 |
| **비용** | 빌드 시간 + 호스팅 요금 | S3 + CloudFront 개별 요금 | 무료 티어 + 유료 플랜 |
| **AWS 통합** | 자연스러운 AWS 생태계 통합 | 완전한 AWS 제어 | AWS와 분리됨 |
| **적합한 경우** | AWS 생태계에서 빠른 배포 | 세밀한 인프라 제어가 필요할 때 | Next.js 중심, 빠른 시작 |

### 2.2 언제 어떤 것을 선택하는가

```
선택 플로우차트:

Next.js SSR이 필요한가?
├── Yes → AWS 생태계에 머물러야 하는가?
│         ├── Yes → Amplify
│         └── No  → Vercel (가장 간편)
│
└── No (정적 SPA) → 세밀한 인프라 제어가 필요한가?
                    ├── Yes → S3 + CloudFront (직접 구성)
                    └── No  → Amplify (가장 빠름)
```

> **핵심 통찰**: Vercel은 Next.js를 만든 회사의 플랫폼이므로 Next.js SSR에 대한 호환성과 최적화가 가장 뛰어나다. 그러나 **AWS VPC 내부 리소스(RDS, ElastiCache 등)에 접근해야 하거나, 조직의 모든 인프라가 AWS에 있어야 하는 경우**에는 Amplify가 합리적인 선택이다. S3 + CloudFront 직접 구성은 SPA 정적 배포에서 가장 비용 효율적이지만, CI/CD와 SSR을 모두 직접 구현해야 한다.

---

## 3. Git 기반 CI/CD 자동 배포

### 3.1 기본 워크플로

Amplify의 핵심은 **Git 리포지토리 연결만으로 CI/CD가 자동 구성**된다는 점이다. 코드를 푸시하면 빌드, 테스트, 배포가 자동으로 실행된다.

```
Git 기반 배포 워크플로:

개발자 → git push origin main
              │
              ↓
┌──── Amplify CI/CD 파이프라인 ────────────────┐
│                                                │
│  1. 소스 다운로드 (Git clone)                   │
│         │                                      │
│  2. 의존성 설치 (npm ci)                        │
│         │                                      │
│  3. 빌드 (npm run build)                       │
│         │                                      │
│  4. 배포 (아티팩트를 CDN에 배포)                 │
│         │                                      │
│  5. 캐시 무효화 (CloudFront invalidation)       │
│                                                │
└──── 결과: https://main.d1a2b3c4.amplifyapp.com ─┘
```

### 3.2 앱 생성 (CLI)

```bash
# 1. Amplify 앱 생성 (GitHub 연결)
aws amplify create-app \
  --name my-nextjs-app \
  --repository https://github.com/username/my-nextjs-app \
  --access-token ghp_xxxxxxxxxxxxxxxxxxxx \
  --platform WEB_COMPUTE

# 2. 브랜치 연결 (main 브랜치)
aws amplify create-branch \
  --app-id d1a2b3c4e5 \
  --branch-name main \
  --stage PRODUCTION \
  --enable-auto-build

# 3. 배포 시작
aws amplify start-job \
  --app-id d1a2b3c4e5 \
  --branch-name main \
  --job-type RELEASE
```

> **실무 팁**: `--platform`은 두 가지 옵션이 있다. **`WEB`**은 정적 사이트(SPA, SSG) 전용이고, **`WEB_COMPUTE`**는 SSR을 지원한다. Next.js SSR을 사용한다면 반드시 `WEB_COMPUTE`를 선택해야 한다. 나중에 변경하려면 앱을 삭제하고 다시 생성해야 할 수 있으므로 처음부터 올바르게 설정하라.

### 3.3 브랜치별 배포

Amplify는 Git 브랜치를 환경과 매핑한다. 이를 통해 프로덕션, 스테이징, 개발 환경을 하나의 Amplify 앱에서 관리할 수 있다.

```
브랜치별 배포:

main 브랜치     → https://main.d1a2b3c4.amplifyapp.com     (프로덕션)
staging 브랜치  → https://staging.d1a2b3c4.amplifyapp.com  (스테이징)
develop 브랜치  → https://develop.d1a2b3c4.amplifyapp.com  (개발)

커스텀 도메인 연결 시:
main 브랜치     → https://www.example.com
staging 브랜치  → https://staging.example.com
```

```bash
# 스테이징 브랜치 추가
aws amplify create-branch \
  --app-id d1a2b3c4e5 \
  --branch-name staging \
  --stage BETA \
  --enable-auto-build \
  --environment-variables '{
    "NEXT_PUBLIC_API_URL": "https://api-staging.example.com",
    "NODE_ENV": "production"
  }'

# 개발 브랜치 추가
aws amplify create-branch \
  --app-id d1a2b3c4e5 \
  --branch-name develop \
  --stage DEVELOPMENT \
  --enable-auto-build
```

### 3.4 지원하는 Git 제공자

| Git 제공자 | 연결 방법 |
|-----------|----------|
| **GitHub** | OAuth 앱 또는 Personal Access Token |
| **GitLab** | OAuth 연동 |
| **Bitbucket** | OAuth 연동 |
| **AWS CodeCommit** | IAM 인증 자동 연동 |

GitHub를 사용하는 경우, AWS 콘솔에서 Amplify 앱을 생성할 때 GitHub 인증 과정을 거치면 웹훅(*Webhook - 특정 이벤트 발생 시 외부 서비스에 HTTP 요청을 보내는 메커니즘*)이 자동으로 설정되어, 코드 푸시마다 배포가 트리거된다.

---

## 4. React SPA 배포

### 4.1 React + Vite 프로젝트 배포

정적 SPA(*Single Page Application - 단일 HTML 파일과 JavaScript 번들로 구성된 웹 애플리케이션. 클라이언트에서 라우팅을 처리한다*)는 Amplify에서 가장 간단하게 배포할 수 있다.

```bash
# React + Vite 프로젝트 생성
npm create vite@latest my-react-app -- --template react-ts
cd my-react-app
npm install

# GitHub에 푸시
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/username/my-react-app.git
git push -u origin main
```

Amplify 앱 생성 후 기본 빌드 설정(`amplify.yml`)은 자동으로 감지된다.

```yaml
# amplify.yml (Vite React SPA)
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: dist
    files:
      - '**/*'
  cache:
    paths:
      - node_modules/**/*
```

### 4.2 SPA 라우팅 처리

React SPA는 클라이언트 사이드 라우팅을 사용한다. `/about` 같은 경로로 직접 접근하면 S3에 해당 파일이 없어 404가 발생한다. Amplify는 이를 자동으로 처리하지만, 커스텀 리다이렉트 규칙을 설정할 수도 있다.

```bash
# SPA 라우팅을 위한 리다이렉트/리라이트 규칙 설정
aws amplify update-app \
  --app-id d1a2b3c4e5 \
  --custom-rules '[
    {
      "source": "</^[^.]+$|\\.(?!(css|gif|ico|jpg|js|png|txt|svg|woff|woff2|ttf|map|json|webp)$)([^.]+$)/>",
      "target": "/index.html",
      "status": "200"
    }
  ]'
```

이 규칙은 "파일 확장자가 없는 경로(예: `/about`, `/users/123`)는 모두 `index.html`로 리라이트한다"는 의미이다. Ch 10에서 다룬 CloudFront의 커스텀 에러 페이지 설정과 동일한 목적이지만, Amplify에서는 JSON 규칙으로 간단하게 처리한다.

---

## 5. Next.js SSR 배포

### 5.1 Amplify의 SSR 지원

Amplify는 Next.js의 SSR(*Server-Side Rendering - 서버에서 HTML을 생성하여 클라이언트에 전달하는 렌더링 방식*)을 지원한다. 내부적으로 Lambda@Edge 또는 CloudFront Functions를 사용하여 서버 사이드 렌더링을 처리한다.

```
Amplify Next.js SSR 아키텍처:

요청: GET /products/123
         │
         ↓
┌──── CloudFront CDN ──────────────────────┐
│                                           │
│  정적 에셋 (/_next/static/*)              │
│  → S3에서 직접 제공 (캐시됨)               │
│                                           │
│  동적 페이지 (/products/123)              │
│  → Lambda 함수에서 SSR 실행               │
│     → HTML 생성 후 응답                   │
│     → 캐시 정책에 따라 CDN 캐시           │
│                                           │
│  API 라우트 (/api/*)                      │
│  → Lambda 함수에서 실행                    │
│                                           │
│  ISR 페이지                               │
│  → 캐시 만료 시 백그라운드 재생성          │
└───────────────────────────────────────────┘
```

### 5.2 지원되는 Next.js 기능

| Next.js 기능 | Amplify 지원 | 비고 |
|-------------|-------------|------|
| **SSG** (Static Site Generation) | 지원 | `getStaticProps`, 정적 export |
| **SSR** (Server-Side Rendering) | 지원 | `getServerSideProps`, App Router Server Components |
| **ISR** (Incremental Static Regeneration) | 지원 | `revalidate` 옵션 사용 가능 |
| **API Routes** | 지원 | `/api/*` 경로 |
| **Middleware** | 지원 | Edge Middleware |
| **Image Optimization** | 지원 | `next/image` 자동 최적화 |
| **App Router** | 지원 | Next.js 13+ App Router |
| **Streaming** | 부분 지원 | React Server Components Streaming |
| **Edge Runtime** | 부분 지원 | 일부 제한 있음 |

### 5.3 Next.js 프로젝트 배포

```bash
# 1. Next.js 프로젝트 생성
npx create-next-app@latest my-nextjs-app --typescript --app
cd my-nextjs-app

# 2. next.config.js 확인 (standalone 모드는 Amplify에서 불필요)
# Amplify가 자동으로 적절한 출력 모드를 설정한다
```

```yaml
# amplify.yml (Next.js SSR)
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: .next
    files:
      - '**/*'
  cache:
    paths:
      - node_modules/**/*
      - .next/cache/**/*
```

```bash
# Amplify 앱 생성 (SSR 지원 플랫폼)
aws amplify create-app \
  --name my-nextjs-ssr \
  --repository https://github.com/username/my-nextjs-app \
  --access-token ghp_xxxxxxxxxxxxxxxxxxxx \
  --platform WEB_COMPUTE \
  --environment-variables '{
    "AMPLIFY_NEXTJS_EXPERIMENTAL_TRACE": "true"
  }'
```

> **실무 팁**: Amplify에서 Next.js SSR을 배포할 때 `.next/cache`를 캐시 경로에 포함하면 **ISR 캐시와 빌드 캐시가 재사용**되어 후속 빌드 시간이 크게 단축된다. 첫 빌드에 3분 걸리던 것이 이후 1분 내외로 줄어들 수 있다.

### 5.4 SSR 배포 시 주의사항

| 항목 | 설명 |
|------|------|
| **빌드 시간** | SSR 앱은 정적 사이트보다 빌드 시간이 길다. 대규모 프로젝트는 5분 이상 소요될 수 있다 |
| **콜드 스타트** | SSR은 Lambda 기반이므로 Ch 7에서 다룬 콜드 스타트가 발생할 수 있다 |
| **Node.js 버전** | Amplify의 빌드 이미지에 포함된 Node.js 버전을 확인해야 한다 |
| **패키지 크기** | Lambda 패키지 크기 제한(50MB)에 주의. 대규모 의존성이 있으면 빌드 실패 가능 |
| **런타임 API** | `fs`, `path` 등 Node.js API는 서버 컴포넌트/API Route에서만 사용 가능 |

---

## 6. 빌드 설정 (amplify.yml)

### 6.1 amplify.yml 구조

`amplify.yml`은 Amplify 빌드 파이프라인의 전체 동작을 정의하는 설정 파일이다. 프로젝트 루트에 배치한다.

```yaml
# amplify.yml 전체 구조
version: 1

# 백엔드 빌드 설정 (Amplify Backend 사용 시)
backend:
  phases:
    build:
      commands:
        - amplifyPush --simple

# 프론트엔드 빌드 설정
frontend:
  phases:
    preBuild:
      commands:
        - npm ci                 # 의존성 설치
    build:
      commands:
        - npm run build          # 빌드 실행
  artifacts:
    baseDirectory: .next         # 빌드 출력 디렉토리
    files:
      - '**/*'                   # 배포할 파일 패턴
  cache:
    paths:
      - node_modules/**/*        # 캐시할 디렉토리
      - .next/cache/**/*

# 테스트 설정 (선택)
test:
  phases:
    preTest:
      commands:
        - npm ci
    test:
      commands:
        - npm run test -- --ci
  artifacts:
    baseDirectory: coverage
    files:
      - '**/*'
```

### 6.2 빌드 단계 상세

```
amplify.yml 빌드 단계:

┌─────────────┐
│  preBuild   │  → 의존성 설치, 환경 설정
│  commands   │     npm ci, env 확인
└──────┬──────┘
       │
┌──────↓──────┐
│    build    │  → 실제 빌드 실행
│  commands   │     npm run build
└──────┬──────┘
       │
┌──────↓──────┐
│  artifacts  │  → 빌드 결과물 수집
│  (배포 대상) │     baseDirectory + files 패턴
└──────┬──────┘
       │
┌──────↓──────┐
│   cache     │  → 다음 빌드를 위한 캐시 저장
│   paths     │     node_modules, .next/cache
└─────────────┘
```

### 6.3 프레임워크별 설정 예시

**React + Vite:**

```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: dist
    files:
      - '**/*'
  cache:
    paths:
      - node_modules/**/*
```

**Next.js (SSR):**

```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - npm ci
    build:
      commands:
        - env | grep -e NEXT_PUBLIC_ >> .env.production
        - npm run build
  artifacts:
    baseDirectory: .next
    files:
      - '**/*'
  cache:
    paths:
      - node_modules/**/*
      - .next/cache/**/*
```

**Next.js (정적 Export):**

```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: out
    files:
      - '**/*'
  cache:
    paths:
      - node_modules/**/*
```

### 6.4 빌드 이미지와 Node.js 버전

Amplify의 빌드 환경은 Amazon Linux 2 기반의 Docker 이미지이다. Node.js 버전을 지정하려면 `preBuild` 단계에서 `nvm`을 사용한다.

```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        # Node.js 20 사용
        - nvm install 20
        - nvm use 20
        - node -v
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: .next
    files:
      - '**/*'
  cache:
    paths:
      - node_modules/**/*
```

또는 Amplify 콘솔에서 빌드 이미지 설정을 통해 기본 Node.js 버전을 변경할 수 있다.

```bash
# 빌드 이미지의 Node.js 버전 확인 (빌드 로그에서)
# Build Settings → Build image settings → Live package updates
# Node.js 버전을 "20" 등으로 지정 가능
```

---

## 7. 환경 변수 관리

### 7.1 빌드 시 vs 런타임 환경 변수

Amplify에서 환경 변수는 **빌드 시**와 **런타임**에 각각 다르게 작동한다. 이 구분을 이해하지 못하면 "로컬에서는 되는데 배포하면 환경 변수가 없다"는 문제에 부딪힌다.

| 구분 | 접근 가능 시점 | 예시 | Next.js에서의 접두사 |
|------|-------------|------|---------------------|
| **빌드 시** | `npm run build` 실행 중 | API URL, 공개 키 | `NEXT_PUBLIC_*` |
| **런타임** | SSR 함수 실행 중 (서버에서) | DB 비밀번호, 비공개 API 키 | 접두사 없음 |
| **클라이언트** | 브라우저에서 | 공개 설정 | `NEXT_PUBLIC_*` (빌드 시 번들에 포함) |

```
환경 변수 흐름:

NEXT_PUBLIC_API_URL (빌드 시 → 번들에 포함 → 브라우저에서 접근 가능)
┌────────────────────────────────────────────────────────────┐
│  빌드 시: process.env.NEXT_PUBLIC_API_URL ✅                │
│  런타임 (서버): process.env.NEXT_PUBLIC_API_URL ✅           │
│  런타임 (브라우저): process.env.NEXT_PUBLIC_API_URL ✅       │
│  → 빌드 시 JavaScript 번들에 문자열로 인라인됨               │
└────────────────────────────────────────────────────────────┘

DATABASE_URL (런타임 전용 → 서버에서만 접근 가능)
┌────────────────────────────────────────────────────────────┐
│  빌드 시: process.env.DATABASE_URL ❌ (사용 불가)            │
│  런타임 (서버): process.env.DATABASE_URL ✅                  │
│  런타임 (브라우저): process.env.DATABASE_URL ❌               │
│  → 서버 사이드(SSR, API Route)에서만 접근 가능               │
└────────────────────────────────────────────────────────────┘
```

### 7.2 환경 변수 설정

```bash
# 앱 수준 환경 변수 설정 (모든 브랜치에 적용)
aws amplify update-app \
  --app-id d1a2b3c4e5 \
  --environment-variables '{
    "NEXT_PUBLIC_APP_NAME": "My App",
    "NEXT_PUBLIC_GA_ID": "G-XXXXXXXXXX"
  }'

# 브랜치별 환경 변수 설정 (특정 브랜치에만 적용)
aws amplify update-branch \
  --app-id d1a2b3c4e5 \
  --branch-name main \
  --environment-variables '{
    "NEXT_PUBLIC_API_URL": "https://api.example.com",
    "DATABASE_URL": "postgresql://user:pass@prod-db:5432/mydb"
  }'

# 스테이징 브랜치에는 다른 환경 변수
aws amplify update-branch \
  --app-id d1a2b3c4e5 \
  --branch-name staging \
  --environment-variables '{
    "NEXT_PUBLIC_API_URL": "https://api-staging.example.com",
    "DATABASE_URL": "postgresql://user:pass@staging-db:5432/mydb"
  }'
```

### 7.3 브랜치별 환경 변수 우선순위

```
환경 변수 우선순위 (높은 순):

1. 브랜치 수준 환경 변수     ← 가장 높은 우선순위
2. 앱 수준 환경 변수         ← 기본값 역할
3. amplify.yml에서 설정한 값 ← 빌드 시 동적 설정

예시:
앱 수준:     NEXT_PUBLIC_API_URL = "https://api-default.example.com"
main 브랜치: NEXT_PUBLIC_API_URL = "https://api.example.com"
→ main 빌드 시: "https://api.example.com" (브랜치 값이 우선)
→ develop 빌드 시: "https://api-default.example.com" (앱 수준 값 사용)
```

> **비용 주의**: Amplify 환경 변수에 민감한 정보(DB 비밀번호, API 시크릿 키)를 저장하면 Amplify 콘솔에서 평문으로 노출된다. 프로덕션 환경에서는 **AWS Secrets Manager 또는 SSM Parameter Store**에 비밀 정보를 저장하고, 빌드 시 또는 런타임에 동적으로 가져오는 것이 안전하다. Amplify 환경 변수는 공개 가능한 설정(`NEXT_PUBLIC_*`, API 엔드포인트 등)에만 사용하라.

---

## 8. 커스텀 도메인 연결

### 8.1 커스텀 도메인 설정

Amplify는 기본적으로 `https://{branch}.{app-id}.amplifyapp.com` 형식의 URL을 제공한다. 실제 서비스에서는 커스텀 도메인을 연결한다.

```bash
# 커스텀 도메인 연결
aws amplify create-domain-association \
  --app-id d1a2b3c4e5 \
  --domain-name example.com \
  --sub-domain-settings '[
    {
      "prefix": "",
      "branchName": "main"
    },
    {
      "prefix": "www",
      "branchName": "main"
    },
    {
      "prefix": "staging",
      "branchName": "staging"
    }
  ]'
```

이 설정은 다음과 같은 매핑을 생성한다.

| 도메인 | 브랜치 |
|--------|-------|
| `example.com` | main |
| `www.example.com` | main |
| `staging.example.com` | staging |

### 8.2 Route 53 자동 연동

도메인이 Route 53에서 관리되고 있다면, Amplify가 DNS 레코드를 **자동으로 생성**한다. 별도의 Route 53 설정이 필요 없다.

```
Route 53 + Amplify 자동 연동:

1. Amplify에서 커스텀 도메인 설정
         │
2. Amplify가 ACM에 SSL 인증서 자동 요청
         │
3. Route 53에 DNS 검증 레코드 자동 추가 (CNAME)
         │
4. SSL 인증서 발급 완료 (수 분 ~ 수십 분)
         │
5. Route 53에 A 레코드 (ALIAS) 자동 추가
         │
6. https://example.com 접속 가능
```

### 8.3 외부 DNS 사용 시

도메인이 Route 53이 아닌 외부 DNS(Cloudflare, GoDaddy 등)에서 관리되는 경우, Amplify가 제공하는 DNS 레코드를 수동으로 추가해야 한다.

```bash
# 도메인 연결 상태 확인
aws amplify get-domain-association \
  --app-id d1a2b3c4e5 \
  --domain-name example.com

# 출력에서 DNS 레코드 정보 확인:
# "certificateVerificationDNSRecord": "_acme.example.com CNAME xxx.acm-validations.aws"
# → 이 CNAME 레코드를 외부 DNS에 수동으로 추가해야 SSL 인증서가 발급됨
```

### 8.4 SSL 인증서 자동 발급

Amplify는 커스텀 도메인 연결 시 **ACM(AWS Certificate Manager)을 통해 SSL 인증서를 자동으로 발급하고 갱신**한다. Ch 5(Route 53)에서 다룬 ACM 인증서 발급 과정이 Amplify에서는 완전히 자동화된다.

- 도메인 소유권 검증: DNS 레코드 기반 자동 검증
- 인증서 갱신: 만료 전 자동 갱신
- 와일드카드 지원: `*.example.com` 인증서 자동 생성

---

## 9. 브랜치 프리뷰

### 9.1 PR 프리뷰 배포란

PR 프리뷰(*Pull Request Preview - Pull Request를 생성하면 해당 변경사항이 반영된 임시 배포 환경이 자동으로 생성되는 기능*)는 코드 리뷰의 효율을 크게 높인다. 리뷰어가 코드만 보는 것이 아니라, **실제 동작하는 환경에서 변경사항을 확인**할 수 있다.

```
PR 프리뷰 워크플로:

1. 개발자가 feature/login 브랜치에서 PR 생성
         │
2. Amplify가 자동으로 프리뷰 환경 빌드
         │
3. PR에 프리뷰 URL 코멘트 자동 추가
   https://pr-42.d1a2b3c4.amplifyapp.com
         │
4. 리뷰어가 프리뷰 환경에서 기능 확인
         │
5. PR 머지 또는 닫기 시 프리뷰 환경 자동 삭제
```

### 9.2 PR 프리뷰 설정

```bash
# PR 프리뷰 활성화
aws amplify update-app \
  --app-id d1a2b3c4e5 \
  --enable-branch-auto-build \
  --auto-branch-creation-config '{
    "enableAutoBuild": true,
    "enablePullRequestPreview": true,
    "pullRequestEnvironmentName": "pr",
    "stage": "PULL_REQUEST",
    "environmentVariables": {
      "NEXT_PUBLIC_API_URL": "https://api-dev.example.com"
    }
  }'
```

### 9.3 PR 프리뷰 활용 팁

| 활용 방법 | 설명 |
|----------|------|
| **UI 리뷰** | 디자인 변경이 실제로 어떻게 보이는지 확인 |
| **기능 테스트** | QA 팀이 PR 단계에서 기능을 테스트 |
| **스테이크홀더 확인** | 비개발자(PM, 디자이너)가 변경사항을 직접 확인 |
| **E2E 테스트** | Cypress/Playwright로 프리뷰 URL에 대해 자동 테스트 실행 |

> **실무 팁**: PR 프리뷰 환경의 환경 변수는 프로덕션과 다르게 설정하라. 프리뷰 환경에서 프로덕션 DB에 접근하거나 결제 API를 호출하는 사고를 방지해야 한다. `autobranchCreationConfig`의 `environmentVariables`에 개발/테스트용 값을 지정하여, 프리뷰 환경이 항상 안전한 설정으로 생성되도록 하라.

---

## 10. 모노레포 지원

### 10.1 모노레포에서 Amplify 사용

모노레포(*Monorepo - 여러 프로젝트나 패키지를 단일 Git 리포지토리에서 관리하는 구조*)에서 Amplify를 사용하려면, 프론트엔드 앱이 위치한 디렉토리를 루트 디렉토리로 지정해야 한다.

```
모노레포 구조 예시:

my-monorepo/
├── packages/
│   ├── shared/          ← 공통 라이브러리
│   ├── web/             ← Next.js 앱 (Amplify 배포 대상)
│   │   ├── package.json
│   │   ├── next.config.js
│   │   └── src/
│   └── api/             ← 백엔드 API (별도 배포)
├── package.json         ← 루트 package.json (워크스페이스)
└── turbo.json           ← Turborepo 설정
```

### 10.2 루트 디렉토리 설정

```bash
# 앱 생성 시 루트 디렉토리 지정
aws amplify create-app \
  --name web-app \
  --repository https://github.com/username/my-monorepo \
  --access-token ghp_xxxxxxxxxxxxxxxxxxxx \
  --platform WEB_COMPUTE

# 브랜치에 루트 디렉토리 설정
aws amplify update-branch \
  --app-id d1a2b3c4e5 \
  --branch-name main \
  --environment-variables '{
    "AMPLIFY_MONOREPO_APP_ROOT": "packages/web"
  }'
```

또는 Amplify 콘솔에서 "App settings > General > Monorepo" 섹션에서 `packages/web`을 루트 디렉토리로 지정할 수 있다.

### 10.3 모노레포 빌드 설정

```yaml
# amplify.yml (모노레포 - packages/web에 위치)
version: 1
applications:
  - frontend:
      phases:
        preBuild:
          commands:
            # 루트에서 의존성 설치 (워크스페이스)
            - cd ../.. && npm ci
        build:
          commands:
            - cd ../.. && npx turbo run build --filter=web
      artifacts:
        baseDirectory: .next
        files:
          - '**/*'
      cache:
        paths:
          - ../../node_modules/**/*
          - .next/cache/**/*
    appRoot: packages/web
```

---

## 11. Amplify의 한계와 대안

### 11.1 Amplify의 한계

Amplify는 빠르고 편리하지만, 복잡한 요구사항에는 한계가 있다.

| 한계 | 설명 | 대안 |
|------|------|------|
| **SSR 기능 제한** | 최신 Next.js 기능이 즉시 지원되지 않을 수 있음 | ECS/Fargate에서 Next.js standalone 배포 (Ch 8 참고) |
| **빌드 시간 제한** | 기본 30분, 대규모 프로젝트에서 타임아웃 가능 | 빌드 최적화 또는 CodeBuild로 전환 |
| **VPC 접근 불가** | Amplify SSR 함수에서 VPC 내부 리소스 직접 접근 불가 | ECS/Fargate + VPC 연결 (Ch 8 참고) |
| **컴퓨팅 커스터마이징** | Lambda 기반 SSR의 메모리/타임아웃 세밀 제어 불가 | ECS/Fargate로 전환 |
| **다중 서비스 오케스트레이션** | 프론트엔드 배포에 특화, 백엔드 서비스 조합 제한적 | ECS + CodePipeline 조합 |
| **리전 제한** | 일부 리전에서 Amplify Hosting 미지원 | S3 + CloudFront (모든 리전 지원) |

### 11.2 Amplify에서 ECS/Fargate로 전환해야 하는 시점

```
Amplify로 충분한 경우:
├── 정적 사이트 (React SPA, Gatsby, Vite)
├── 간단한 SSR (Next.js 기본 기능)
├── 브랜치별 배포 + PR 프리뷰가 필요
├── AWS 인프라에 대한 깊은 지식 없이 빠르게 배포
└── 트래픽이 중소 규모

ECS/Fargate로 전환해야 하는 경우:
├── VPC 내부 리소스 (RDS, ElastiCache)에 직접 접근 필요
├── Next.js 최신 기능을 즉시 사용해야 함
├── 서버 사이드의 세밀한 제어 필요 (메모리, CPU, 타임아웃)
├── WebSocket이나 장시간 연결이 필요
├── 복잡한 멀티 서비스 아키텍처
└── 대규모 트래픽에서 비용 최적화 필요
```

> **핵심 통찰**: Amplify로 시작하고 필요해지면 ECS/Fargate로 전환하는 것이 현실적인 전략이다. Amplify는 **MVP와 초기 프로덕션에 이상적**이며, 서비스가 성장하여 인프라 요구사항이 복잡해지면 ECS/Fargate(Ch 8) 또는 CodePipeline(Ch 14)으로 마이그레이션한다. 처음부터 완벽한 인프라를 구축하려다 배포 자체가 늦어지는 것보다, 빠르게 배포하고 점진적으로 발전시키는 것이 낫다.

---

## 12. 배포 트러블슈팅

### 12.1 빌드 실패 원인

| 증상 | 원인 | 해결 방법 |
|------|------|----------|
| `npm ci` 실패 | `package-lock.json`과 `package.json` 불일치 | 로컬에서 `npm install` 후 `package-lock.json` 커밋 |
| `node: command not found` | Node.js 버전 미설정 | `amplify.yml`에서 `nvm use 20` 추가 |
| `ENOMEM` (메모리 부족) | 빌드 시 메모리 초과 | `NODE_OPTIONS=--max-old-space-size=4096` 환경 변수 추가 |
| `Build timed out` | 빌드 30분 초과 | 빌드 최적화, 캐시 활용, 또는 CodeBuild 전환 |
| `NEXT_PUBLIC_*` 환경 변수 미적용 | 환경 변수가 빌드 시 주입되지 않음 | Amplify 콘솔/CLI에서 환경 변수 설정 확인 |
| `404 Not Found` (SPA) | 클라이언트 사이드 라우팅 미설정 | 리다이렉트/리라이트 규칙 추가 |
| SSR 페이지 `500 Internal Server Error` | 런타임 환경 변수 누락 또는 Lambda 타임아웃 | CloudWatch 로그 확인, 환경 변수 점검 |

### 12.2 빌드 로그 확인

```bash
# 최근 빌드 작업 목록
aws amplify list-jobs \
  --app-id d1a2b3c4e5 \
  --branch-name main \
  --max-results 5

# 특정 빌드의 상세 로그
aws amplify get-job \
  --app-id d1a2b3c4e5 \
  --branch-name main \
  --job-id 1

# 빌드 아티팩트 URL 확인
aws amplify get-artifact-url \
  --app-id d1a2b3c4e5 \
  --artifact-id build-artifact-id
```

### 12.3 일반적인 트러블슈팅 체크리스트

```bash
# 1. 로컬에서 빌드가 성공하는지 확인
npm ci && npm run build

# 2. 환경 변수 확인
aws amplify get-app --app-id d1a2b3c4e5 \
  --query 'app.environmentVariables'

aws amplify get-branch --app-id d1a2b3c4e5 --branch-name main \
  --query 'branch.environmentVariables'

# 3. 빌드 설정 확인
aws amplify get-app --app-id d1a2b3c4e5 \
  --query 'app.buildSpec'

# 4. 도메인 상태 확인
aws amplify list-domain-associations --app-id d1a2b3c4e5
```

### 12.4 Node.js 메모리 부족 해결

대규모 Next.js 프로젝트에서 빌드 시 메모리 부족 에러가 자주 발생한다.

```bash
# 환경 변수로 Node.js 힙 메모리 증가
aws amplify update-app \
  --app-id d1a2b3c4e5 \
  --environment-variables '{
    "NODE_OPTIONS": "--max-old-space-size=4096"
  }'
```

또는 `amplify.yml`에서 직접 설정한다.

```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - export NODE_OPTIONS="--max-old-space-size=4096"
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: .next
    files:
      - '**/*'
```

---

## 자주 하는 실수

| 실수 | 설명 | 올바른 접근 |
|------|------|------------|
| **`WEB` 플랫폼으로 SSR 앱 배포** | SSR이 동작하지 않고 정적 페이지만 제공됨 | Next.js SSR 사용 시 `WEB_COMPUTE` 플랫폼으로 앱 생성 |
| **`NEXT_PUBLIC_*` 접두사 누락** | 클라이언트에서 환경 변수가 `undefined`로 표시됨 | 브라우저에서 사용할 환경 변수는 반드시 `NEXT_PUBLIC_` 접두사 추가 |
| **환경 변수 변경 후 재배포 안 함** | 빌드 시 환경 변수(NEXT_PUBLIC_*)는 빌드 시점에 번들에 포함됨 | 환경 변수 변경 후 반드시 재빌드/재배포 실행 |
| **`amplify.yml`의 `baseDirectory` 잘못 설정** | 빌드는 성공하지만 배포된 사이트에 파일이 없음 | Vite는 `dist`, Next.js SSR은 `.next`, Next.js 정적 export는 `out` |
| **모노레포에서 루트 디렉토리 미설정** | 전체 리포지토리를 빌드하려다 실패 | `AMPLIFY_MONOREPO_APP_ROOT` 환경 변수 또는 콘솔에서 루트 디렉토리 지정 |
| **프리뷰 환경에 프로덕션 환경 변수 사용** | PR 프리뷰에서 프로덕션 DB에 접근하거나 실제 결제 발생 | 프리뷰 환경 전용 환경 변수를 별도로 설정 |
| **`package-lock.json`을 `.gitignore`에 포함** | `npm ci`가 실패하여 빌드 전체가 실패 | `package-lock.json`은 반드시 Git에 커밋 |
| **빌드 캐시를 설정하지 않음** | 매 빌드마다 의존성을 처음부터 설치하여 빌드 시간 증가 | `amplify.yml`의 `cache.paths`에 `node_modules/**/*` 포함 |

---

## AWS CLI 레퍼런스

| 명령어 | 설명 |
|--------|------|
| `aws amplify create-app --name NAME --repository URL --platform PLATFORM` | Amplify 앱 생성 |
| `aws amplify create-branch --app-id ID --branch-name BRANCH --stage STAGE` | 브랜치 연결 |
| `aws amplify start-job --app-id ID --branch-name BRANCH --job-type RELEASE` | 수동 배포 시작 |
| `aws amplify stop-job --app-id ID --branch-name BRANCH --job-id JOB_ID` | 진행 중인 빌드 중지 |
| `aws amplify list-jobs --app-id ID --branch-name BRANCH` | 빌드 작업 목록 조회 |
| `aws amplify get-job --app-id ID --branch-name BRANCH --job-id JOB_ID` | 빌드 상세 정보/로그 |
| `aws amplify update-app --app-id ID --environment-variables JSON` | 앱 수준 환경 변수 설정 |
| `aws amplify update-branch --app-id ID --branch-name BRANCH --environment-variables JSON` | 브랜치별 환경 변수 설정 |
| `aws amplify create-domain-association --app-id ID --domain-name DOMAIN` | 커스텀 도메인 연결 |
| `aws amplify get-domain-association --app-id ID --domain-name DOMAIN` | 도메인 연결 상태 확인 |
| `aws amplify list-domain-associations --app-id ID` | 도메인 목록 조회 |
| `aws amplify get-app --app-id ID` | 앱 상세 정보 조회 |
| `aws amplify list-apps` | 모든 Amplify 앱 목록 |
| `aws amplify list-branches --app-id ID` | 연결된 브랜치 목록 |
| `aws amplify delete-branch --app-id ID --branch-name BRANCH` | 브랜치 배포 삭제 |
| `aws amplify delete-app --app-id ID` | Amplify 앱 삭제 |

---

## 요약

- **AWS Amplify**는 프론트엔드/풀스택 앱을 위한 완전 관리형 배포 플랫폼이다. Git 연결만으로 CI/CD, CDN, SSL, 프리뷰 환경이 자동으로 구성된다.
- **Amplify Hosting**은 정적 사이트(React SPA, Vite)와 SSR(Next.js)을 모두 지원한다. SSR이 필요하면 `WEB_COMPUTE` 플랫폼을 선택한다.
- **Amplify vs S3+CloudFront vs Vercel**: AWS 생태계에서 빠른 배포가 목적이면 Amplify, 세밀한 인프라 제어가 필요하면 S3+CloudFront, Next.js 최적 경험이면 Vercel을 선택한다.
- **브랜치별 배포**로 main(프로덕션), staging(스테이징), develop(개발) 환경을 하나의 앱에서 관리한다. 각 브랜치에 별도의 환경 변수를 설정할 수 있다.
- **환경 변수**는 빌드 시(`NEXT_PUBLIC_*`)와 런타임으로 구분된다. 클라이언트에서 사용할 변수는 반드시 `NEXT_PUBLIC_` 접두사가 필요하며, 변경 후 재빌드해야 반영된다.
- **커스텀 도메인** 연결 시 Route 53을 사용하면 DNS 레코드와 SSL 인증서가 자동으로 설정된다.
- **`amplify.yml`**로 빌드 단계(preBuild, build), 아티팩트 경로, 캐시를 세밀하게 제어한다. `node_modules`와 `.next/cache`를 캐시하면 빌드 시간이 크게 단축된다.
- **PR 프리뷰**를 활성화하면 Pull Request마다 임시 배포 환경이 생성되어, 코드 리뷰 시 실제 동작을 확인할 수 있다.
- **모노레포**에서는 `AMPLIFY_MONOREPO_APP_ROOT` 환경 변수로 프론트엔드 앱의 루트 디렉토리를 지정한다.
- **Amplify의 한계**: VPC 내부 리소스 접근 불가, SSR 기능 제한, 컴퓨팅 커스터마이징 제한 등이 있다. 이러한 한계에 부딪히면 ECS/Fargate(Ch 8)로 전환을 고려한다.
- **트러블슈팅**: 빌드 실패 시 로컬 빌드 확인, 환경 변수 점검, `amplify.yml`의 `baseDirectory` 확인, 빌드 로그 분석 순서로 진행한다. 메모리 부족은 `NODE_OPTIONS=--max-old-space-size=4096`으로 해결한다.
