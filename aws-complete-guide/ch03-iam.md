# Chapter 3: IAM - 접근 제어의 기초: Identity and Access Management

## 핵심 질문

AWS에서 "누가 무엇을 할 수 있는가"를 어떻게 정의하고 관리하는가? IAM의 사용자, 그룹, 역할, 정책은 각각 어떤 역할을 하며, 안전한 접근 제어를 위해 어떤 원칙을 따라야 하는가?

---

## 1. IAM이란

### 1.1 접근 제어의 필요성

AWS 계정 안에는 수많은 리소스(서버, 데이터베이스, 스토리지 등)가 존재한다. 이 리소스에 대해 **누가(Who)** **무엇을(What)** 할 수 있는지를 제어하는 것이 IAM(*Identity and Access Management - AWS 리소스에 대한 접근을 안전하게 제어하는 서비스*)의 역할이다.

IAM 없이는 루트 사용자 하나로 모든 작업을 해야 한다. 이는 팀의 모든 구성원에게 은행 마스터키를 주는 것과 같다.

### 1.2 IAM의 핵심 구성 요소

```
IAM 구성 요소:

[Who?]                      [What can they do?]
┌──────────┐               ┌──────────────────┐
│ IAM User │──── 직접 ────→│   IAM Policy     │
│ (사용자)  │   부여하거나   │   (정책)         │
└──────────┘               │                  │
      │                    │  "Effect": Allow  │
      │ 소속               │  "Action": s3:*   │
      ↓                    │  "Resource": *    │
┌──────────┐               └──────────────────┘
│IAM Group │──── 그룹에 ────→ Policy
│ (그룹)    │   정책 부여
└──────────┘

┌──────────┐
│ IAM Role │──── 역할에 ────→ Policy
│ (역할)    │   정책 부여
└──────────┘
  ↑ 역할을 "assume"하여 사용
  │
  ├── AWS 서비스 (Lambda, EC2 등)
  ├── 다른 AWS 계정의 사용자
  └── 외부 자격 증명 (Google, GitHub 등)
```

IAM은 **글로벌 서비스**이다. 리전에 종속되지 않으며, 한 번 설정하면 모든 리전에서 동일하게 적용된다.

---

## 2. IAM 사용자 (User)

### 2.1 사용자란

IAM 사용자(*IAM User - AWS 계정 내에서 특정 사람이나 애플리케이션을 나타내는 엔터티*)는 AWS와 상호작용하는 사람이나 서비스를 나타낸다. 각 사용자는 고유한 자격 증명(비밀번호 또는 액세스 키)을 가진다.

| 자격 증명 유형 | 용도 | 사용 방법 |
|-------------|------|----------|
| **콘솔 비밀번호** | AWS Management Console 로그인 | 사람이 브라우저에서 사용 |
| **액세스 키** | AWS CLI, SDK, API 호출 | 프로그래밍 방식 접근 |

### 2.2 사용자 생성

```bash
# IAM 사용자 생성
aws iam create-user --user-name developer-kim

# 콘솔 로그인 비밀번호 설정
aws iam create-login-profile \
  --user-name developer-kim \
  --password "TempP@ssw0rd!" \
  --password-reset-required

# 액세스 키 생성 (CLI/SDK용)
aws iam create-access-key --user-name developer-kim
# 출력:
# {
#   "AccessKey": {
#     "AccessKeyId": "AKIA...",
#     "SecretAccessKey": "wJal...",
#     "Status": "Active"
#   }
# }
```

> **비용 주의**: IAM 자체는 **무료** 서비스이다. 사용자, 그룹, 역할, 정책을 얼마든지 만들어도 비용이 발생하지 않는다. 비용이 발생하는 것은 IAM 사용자가 실제로 사용하는 AWS 리소스(EC2, S3 등)이다.

---

## 3. IAM 그룹 (Group)

### 3.1 그룹이란

IAM 그룹(*IAM Group - IAM 사용자의 집합. 그룹에 정책을 부여하면 그룹의 모든 사용자에게 동일한 권한이 적용된다*)은 사용자를 묶어서 권한을 관리하는 단위이다. 사용자마다 개별적으로 정책을 붙이는 대신, 그룹에 정책을 부여하면 관리가 훨씬 간편해진다.

```
그룹 구조 예시:

Developers 그룹 ──→ [EC2 Full, S3 Read, Lambda Full]
├── developer-kim
├── developer-lee
└── developer-park

Operations 그룹 ──→ [EC2 Full, S3 Full, CloudWatch Full, IAM Read]
├── ops-choi
└── ops-jung

ReadOnly 그룹 ──→ [모든 서비스 Read Only]
└── intern-yoon
```

### 3.2 그룹 관리

```bash
# 그룹 생성
aws iam create-group --group-name Developers

# 그룹에 정책 부여
aws iam attach-group-policy \
  --group-name Developers \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2FullAccess

aws iam attach-group-policy \
  --group-name Developers \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

# 사용자를 그룹에 추가
aws iam add-user-to-group \
  --user-name developer-kim \
  --group-name Developers

# 그룹의 사용자 목록 확인
aws iam get-group --group-name Developers
```

### 3.3 그룹 사용 원칙

- 사용자에게 직접 정책을 부여하지 않고, **반드시 그룹을 통해** 권한을 관리한다.
- 한 사용자가 **여러 그룹에 소속**될 수 있다. 이 경우 모든 그룹의 정책이 합쳐진다.
- 그룹은 **중첩할 수 없다**. 그룹 안에 다른 그룹을 넣을 수 없다.

---

## 4. IAM 정책 (Policy)

### 4.1 정책이란

IAM 정책(*IAM Policy - JSON 형식으로 작성되며, 누가 어떤 리소스에 어떤 작업을 할 수 있는지/없는지를 정의하는 문서*)은 "허용" 또는 "거부"를 정의하는 JSON 문서이다. 이것이 IAM의 핵심이다.

### 4.2 정책 문서 구조

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowS3ReadAccess",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::my-bucket",
        "arn:aws:s3:::my-bucket/*"
      ]
    }
  ]
}
```

**각 필드의 의미:**

| 필드 | 설명 | 필수 |
|------|------|------|
| **Version** | 정책 언어 버전. 항상 `"2012-10-17"` 사용 | 예 |
| **Statement** | 하나 이상의 권한 선언 배열 | 예 |
| **Sid** | 선언의 식별자 (설명용, 선택적) | 아니오 |
| **Effect** | `"Allow"` 또는 `"Deny"` | 예 |
| **Action** | 허용/거부할 AWS 작업 | 예 |
| **Resource** | 작업 대상 리소스의 ARN | 예 |
| **Condition** | 조건부 적용 (선택적) | 아니오 |

### 4.3 ARN (Amazon Resource Name)

ARN(*Amazon Resource Name - AWS의 모든 리소스를 고유하게 식별하는 주소 체계*)은 AWS 리소스의 고유 식별자이다.

```
ARN 형식:
arn:aws:서비스:리전:계정ID:리소스타입/리소스이름

예시:
arn:aws:s3:::my-bucket                        # S3 버킷
arn:aws:s3:::my-bucket/*                       # 버킷 내 모든 객체
arn:aws:ec2:ap-northeast-2:123456789012:instance/i-0abc123  # EC2 인스턴스
arn:aws:lambda:ap-northeast-2:123456789012:function:my-func # Lambda 함수
arn:aws:iam::123456789012:user/developer-kim    # IAM 사용자 (글로벌)
```

### 4.4 자주 사용하는 Action 패턴

```json
// 특정 작업만 허용
"Action": "s3:GetObject"

// 서비스의 모든 작업 허용
"Action": "s3:*"

// 여러 작업을 배열로 지정
"Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]

// 와일드카드 패턴
"Action": "s3:Get*"        // s3:GetObject, s3:GetBucketPolicy 등
"Action": "ec2:Describe*"  // 모든 Describe 작업 (읽기 전용)
```

### 4.5 실전 정책 예시

**예시 1: 프론트엔드 개발자용 정책**

프론트엔드 개발자가 S3에 정적 파일을 업로드하고, CloudFront 캐시를 무효화하며, Lambda@Edge 함수를 관리할 수 있도록 하는 정책:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3StaticSiteManagement",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::my-frontend-bucket",
        "arn:aws:s3:::my-frontend-bucket/*"
      ]
    },
    {
      "Sid": "CloudFrontInvalidation",
      "Effect": "Allow",
      "Action": [
        "cloudfront:CreateInvalidation",
        "cloudfront:GetInvalidation",
        "cloudfront:ListInvalidations"
      ],
      "Resource": "arn:aws:cloudfront::123456789012:distribution/E1234567890"
    },
    {
      "Sid": "LambdaEdgeManagement",
      "Effect": "Allow",
      "Action": [
        "lambda:GetFunction",
        "lambda:UpdateFunctionCode",
        "lambda:PublishVersion"
      ],
      "Resource": "arn:aws:lambda:us-east-1:123456789012:function:my-edge-*"
    }
  ]
}
```

**예시 2: 특정 IP에서만 접근 허용**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "*",
      "Resource": "*",
      "Condition": {
        "IpAddress": {
          "aws:SourceIp": ["203.0.113.0/24", "198.51.100.0/24"]
        }
      }
    }
  ]
}
```

### 4.6 AWS 관리형 정책 vs 커스텀 정책

| 유형 | 설명 | 사용 시점 |
|------|------|----------|
| **AWS 관리형** | AWS가 미리 만들어 제공하는 정책 | 일반적인 사용 사례에 적합 |
| **커스텀** | 직접 JSON으로 작성하는 정책 | 세밀한 권한 제어가 필요할 때 |

```bash
# AWS 관리형 정책 목록 조회
aws iam list-policies --scope AWS --query 'Policies[?starts_with(PolicyName, `Amazon`)]' --output table

# 자주 사용하는 관리형 정책:
# - AdministratorAccess: 모든 서비스에 대한 전체 접근
# - PowerUserAccess: IAM을 제외한 모든 서비스 전체 접근
# - ReadOnlyAccess: 모든 서비스 읽기 전용
# - AmazonS3FullAccess: S3 전체 접근
# - AmazonEC2FullAccess: EC2 전체 접근
# - AWSLambda_FullAccess: Lambda 전체 접근
```

> **핵심 통찰**: 정책의 기본 원칙은 **"명시적으로 허용하지 않은 것은 모두 거부"**이다. IAM은 기본적으로 모든 것을 거부하며, 명시적 `Allow`가 있어야만 접근을 허용한다. 다만 `Deny`는 항상 `Allow`보다 우선한다. 어떤 정책에서 `Allow`하더라도, 다른 정책에서 `Deny`하면 최종적으로 거부된다.

---

## 5. IAM 역할 (Role)

### 5.1 역할이란

IAM 역할(*IAM Role - 특정 권한을 가진 IAM 엔터티. 사용자처럼 영구 자격 증명을 갖지 않고, 필요할 때 "assume"하여 임시 자격 증명을 받는다*)은 사용자와 비슷하게 정책을 부여받지만, 근본적으로 다른 점이 있다.

**사용자 vs 역할:**

| 특성 | IAM 사용자 | IAM 역할 |
|------|----------|----------|
| **자격 증명** | 영구 (비밀번호, 액세스 키) | 임시 (STS 토큰, 자동 만료) |
| **소유자** | 특정 사람 또는 애플리케이션 | 누구든 "assume" 가능 |
| **주요 사용처** | 사람이 콘솔/CLI에서 작업 | AWS 서비스, 크로스 계정 접근 |

### 5.2 역할이 필요한 이유

**시나리오 1: Lambda 함수가 S3에 접근**

Lambda 함수는 사람이 아니므로 IAM "사용자"를 만들어 액세스 키를 넣어주는 것은 부적절하다. 대신 역할을 만들어 Lambda 함수에 부여한다.

```
Lambda 함수 ── assume ──→ S3ReadRole ──→ S3 버킷 읽기 가능
                          (정책: s3:GetObject)
```

**시나리오 2: EC2 인스턴스에서 DynamoDB 접근**

EC2 인스턴스에서 실행되는 Node.js 서버가 DynamoDB에 데이터를 읽고 쓸 때, 액세스 키를 환경 변수로 넣는 것보다 역할이 안전하다.

```
EC2 인스턴스 ── assume ──→ DynamoDBRole ──→ DynamoDB 읽기/쓰기
                           (정책: dynamodb:GetItem, PutItem)
```

**시나리오 3: GitHub Actions에서 AWS에 배포**

CI/CD 파이프라인에서 AWS에 배포할 때, 액세스 키 대신 OIDC(OpenID Connect)를 통해 역할을 assume한다.

```
GitHub Actions ── OIDC ──→ DeployRole ──→ S3 업로드, CloudFront 무효화
```

### 5.3 역할 생성과 사용

역할을 만들려면 두 가지가 필요하다: **신뢰 정책(Trust Policy)**과 **권한 정책(Permission Policy)**.

- **신뢰 정책**: "누가 이 역할을 assume할 수 있는가?"
- **권한 정책**: "이 역할은 무엇을 할 수 있는가?"

```bash
# 1. Lambda가 assume할 수 있는 역할 생성
aws iam create-role \
  --role-name LambdaS3ReadRole \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {
          "Service": "lambda.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
      }
    ]
  }'

# 2. 역할에 권한 정책 부여
aws iam attach-role-policy \
  --role-name LambdaS3ReadRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

# 3. Lambda 함수 생성 시 이 역할을 지정
aws lambda create-function \
  --function-name my-function \
  --role arn:aws:iam::123456789012:role/LambdaS3ReadRole \
  --runtime nodejs20.x \
  --handler index.handler \
  --zip-file fileb://function.zip
```

### 5.4 서비스 연결 역할 (Service-Linked Role)

일부 AWS 서비스는 자동으로 서비스 연결 역할을 생성한다. 예를 들어, Auto Scaling은 EC2 인스턴스를 시작/종료하기 위해 `AWSServiceRoleForAutoScaling`이라는 역할이 필요하다. 이 역할은 서비스가 자동으로 관리하므로 직접 수정하지 않는 것이 좋다.

> **실무 팁**: AWS에서 권한 오류(`AccessDenied`)가 발생하면 대부분 **역할의 권한 정책**이 부족하거나 **신뢰 정책**이 잘못된 것이다. 디버깅 순서: (1) 어떤 역할을 사용 중인지 확인 → (2) 역할의 권한 정책에 필요한 Action이 있는지 확인 → (3) Resource ARN이 정확한지 확인.

---

## 6. 최소 권한 원칙 (Principle of Least Privilege)

### 6.1 정의

최소 권한 원칙이란 **"각 사용자와 서비스에게 작업을 수행하는 데 필요한 최소한의 권한만 부여한다"**는 보안 원칙이다. 이것은 IAM 설계에서 가장 중요한 원칙이다.

### 6.2 나쁜 예 vs 좋은 예

```json
// ❌ 나쁜 예: 모든 서비스에 모든 권한
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "*",
      "Resource": "*"
    }
  ]
}
```

```json
// ✅ 좋은 예: 필요한 서비스에 필요한 작업만
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::my-app-assets/*"
    }
  ]
}
```

### 6.3 점진적 권한 부여 전략

처음부터 완벽한 최소 권한 정책을 작성하기는 어렵다. 실무에서는 다음과 같은 점진적 접근이 효과적이다:

```
1단계: 관리형 정책으로 시작
   → AmazonS3FullAccess 같은 넓은 정책으로 개발/테스트

2단계: IAM Access Analyzer 활용
   → 실제 사용된 API 호출을 분석하여 필요한 Action 파악

3단계: 커스텀 정책으로 축소
   → 분석 결과를 바탕으로 최소 권한 정책 작성

4단계: 지속적 모니터링
   → CloudTrail로 API 호출 기록을 확인하고 불필요한 권한 제거
```

```bash
# IAM Access Analyzer로 정책 생성 (실제 활동 기반)
aws accessanalyzer start-policy-generation \
  --policy-generation-details '{
    "principalArn": "arn:aws:iam::123456789012:role/MyRole"
  }'
```

---

## 7. MFA (Multi-Factor Authentication)

### 7.1 MFA란

MFA(*Multi-Factor Authentication - 비밀번호 외에 추가 인증 수단을 요구하는 보안 기법. "알고 있는 것" + "가지고 있는 것"의 조합*)는 비밀번호가 유출되어도 계정을 보호하는 추가 보안 계층이다.

### 7.2 MFA 유형

| 유형 | 방식 | 예시 |
|------|------|------|
| **가상 MFA** | 스마트폰 앱이 생성하는 일회용 코드 | Google Authenticator, Authy |
| **하드웨어 MFA** | 물리적 디바이스가 생성하는 코드 | YubiKey, Gemalto 토큰 |
| **SMS MFA** | 문자 메시지로 전송되는 코드 | (보안상 권장하지 않음) |

### 7.3 MFA 설정

```bash
# 가상 MFA 디바이스 생성
aws iam create-virtual-mfa-device \
  --virtual-mfa-device-name root-mfa \
  --outfile /tmp/QRCode.png \
  --bootstrap-method QRCodePNG

# MFA 활성화 (연속된 두 개의 인증 코드 필요)
aws iam enable-mfa-device \
  --user-name developer-kim \
  --serial-number arn:aws:iam::123456789012:mfa/developer-kim \
  --authentication-code1 123456 \
  --authentication-code2 789012
```

> **실무 팁**: 최소한 **루트 사용자와 관리자 권한을 가진 IAM 사용자**에는 반드시 MFA를 설정하라. MFA를 설정하지 않은 관리자 계정이 탈취되면 계정의 모든 리소스가 위험에 노출된다.

---

## 8. IAM 보안 모범 사례

### 8.1 체크리스트

| 항목 | 설명 | 우선순위 |
|------|------|---------|
| **루트 사용자 MFA** | 루트 사용자에 MFA를 반드시 활성화 | 필수 |
| **루트 사용자 미사용** | 일상 작업은 IAM 사용자/역할로 수행 | 필수 |
| **그룹 기반 권한 관리** | 사용자에게 직접 정책을 부여하지 않음 | 강력 권장 |
| **최소 권한 원칙** | 필요한 최소한의 권한만 부여 | 강력 권장 |
| **역할 우선 사용** | 서비스 간 통신에는 역할 사용, 액세스 키 지양 | 강력 권장 |
| **액세스 키 주기적 교체** | 90일마다 액세스 키를 교체 | 권장 |
| **비밀번호 정책 설정** | 최소 길이, 복잡성, 교체 주기 설정 | 권장 |
| **미사용 자격 증명 제거** | 사용하지 않는 사용자/키를 정기적으로 정리 | 권장 |

### 8.2 비밀번호 정책 설정

```bash
# 계정 수준의 비밀번호 정책 설정
aws iam update-account-password-policy \
  --minimum-password-length 12 \
  --require-symbols \
  --require-numbers \
  --require-uppercase-characters \
  --require-lowercase-characters \
  --max-password-age 90 \
  --password-reuse-prevention 12
```

---

## 자주 하는 실수

| 실수 | 설명 | 올바른 접근 |
|------|------|------------|
| **루트 사용자로 개발** | 보안 사고 시 계정 전체 탈취 | IAM 사용자/역할을 만들어 사용 |
| **`Action: "*"` 정책** | 모든 권한을 열어두면 사고 범위가 무제한 | 필요한 Action만 명시적으로 나열 |
| **액세스 키를 코드에 삽입** | Git 유출 시 계정 탈취. GitHub에 키 스캐너 봇이 활동 중 | IAM 역할 또는 환경 변수 사용 |
| **사용자에게 직접 정책 부여** | 권한 관리가 파편화되어 추적 불가 | 그룹을 만들고 그룹에 정책 부여 |
| **MFA 미설정** | 비밀번호만으로는 보안 부족 | 최소 루트 + 관리자 계정에 MFA 필수 |
| **미사용 사용자/키 방치** | 공격자의 잠재적 진입점 | 90일 이상 미사용 자격 증명은 비활성화/삭제 |

---

## AWS CLI 레퍼런스

| 명령어 | 설명 |
|--------|------|
| `aws iam create-user --user-name NAME` | IAM 사용자 생성 |
| `aws iam create-group --group-name NAME` | IAM 그룹 생성 |
| `aws iam add-user-to-group --user-name USER --group-name GROUP` | 사용자를 그룹에 추가 |
| `aws iam attach-group-policy --group-name GROUP --policy-arn ARN` | 그룹에 정책 부여 |
| `aws iam create-role --role-name NAME --assume-role-policy-document JSON` | IAM 역할 생성 |
| `aws iam attach-role-policy --role-name NAME --policy-arn ARN` | 역할에 정책 부여 |
| `aws iam create-access-key --user-name NAME` | 액세스 키 생성 |
| `aws iam list-users` | 모든 IAM 사용자 조회 |
| `aws iam list-groups` | 모든 IAM 그룹 조회 |
| `aws iam list-roles` | 모든 IAM 역할 조회 |
| `aws iam get-policy --policy-arn ARN` | 정책 상세 조회 |
| `aws sts get-caller-identity` | 현재 인증된 IAM 엔터티 확인 |

---

## 요약

- **IAM**은 AWS 리소스에 대한 접근을 제어하는 글로벌 서비스이며, 무료이다.
- **사용자(User)**: 사람이나 애플리케이션을 나타내며, 영구 자격 증명(비밀번호, 액세스 키)을 갖는다.
- **그룹(Group)**: 사용자의 집합. 그룹에 정책을 부여하여 권한을 관리한다. 사용자에게 직접 정책을 붙이지 않는다.
- **정책(Policy)**: JSON 문서로, `Effect`(Allow/Deny) + `Action`(작업) + `Resource`(대상)로 구성된다.
- **역할(Role)**: 임시 자격 증명을 사용하며, AWS 서비스(Lambda, EC2)나 외부 시스템(GitHub Actions)이 assume하여 사용한다. 액세스 키보다 안전하다.
- 기본 원칙은 **"명시적 Allow가 없으면 Deny"**이며, **명시적 Deny는 항상 Allow보다 우선**한다.
- **최소 권한 원칙**: 작업에 필요한 최소한의 권한만 부여한다.
- **MFA**: 최소한 루트 사용자와 관리자 계정에는 반드시 설정한다.
- 액세스 키를 코드에 하드코딩하지 마라. IAM 역할이 더 안전하다.
