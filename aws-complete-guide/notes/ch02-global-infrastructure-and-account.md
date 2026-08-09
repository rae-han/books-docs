# Chapter 2: 글로벌 인프라와 계정 설정: Global Infrastructure & Account Setup

## 핵심 질문

AWS의 물리적 인프라는 전 세계에 어떻게 분산되어 있으며, 안전하고 비용 효율적인 AWS 사용을 위해 계정을 어떻게 설정해야 하는가?

---

## 1. AWS 글로벌 인프라

AWS는 전 세계에 분산된 물리적 데이터센터를 기반으로 서비스를 제공한다. 이 인프라의 구조를 이해하면 리소스를 어디에 배치할지, 왜 특정 리전을 선택해야 하는지에 대한 판단 기준이 생긴다.

### 1.1 리전 (Region)

리전(*Region - 지리적으로 분리된 AWS 데이터센터 클러스터의 묶음*)은 AWS 인프라의 최상위 단위이다. 각 리전은 물리적으로 격리되어 있으며, 하나의 리전에서 발생한 장애가 다른 리전에 영향을 주지 않는다.

2024년 기준 AWS는 전 세계 33개 이상의 리전을 운영하고 있으며, 한국에는 **서울 리전(ap-northeast-2)**이 있다.

**주요 리전과 코드:**

| 리전 코드 | 위치 | 특징 |
|-----------|------|------|
| **ap-northeast-2** | 서울 | 한국 사용자에게 가장 낮은 지연 시간 |
| **us-east-1** | 버지니아 | AWS 최초 리전, 가장 많은 서비스 제공, 가장 저렴 |
| **us-west-2** | 오레곤 | 북미 서부, us-east-1 다음으로 저렴 |
| **ap-northeast-1** | 도쿄 | 일본, 서울 리전 백업으로 자주 사용 |
| **eu-west-1** | 아일랜드 | 유럽 주요 리전 |

### 1.2 리전 선택 기준

리전을 선택할 때 고려해야 하는 네 가지 요소가 있다:

**1. 지연 시간 (Latency)**

사용자와 리전 사이의 물리적 거리가 짧을수록 응답 시간이 빠르다. 한국 사용자가 주 대상이라면 서울 리전이 최선이다.

```
사용자(서울) → ap-northeast-2(서울): ~2ms
사용자(서울) → ap-northeast-1(도쿄): ~30ms
사용자(서울) → us-east-1(버지니아): ~180ms
```

**2. 비용**

같은 서비스라도 리전에 따라 가격이 다르다. 일반적으로 미국 리전(us-east-1, us-west-2)이 가장 저렴하고, 아시아 리전은 10~20% 비싸다.

**3. 서비스 가용성**

새로운 AWS 서비스는 대부분 us-east-1에서 먼저 출시되고, 이후 다른 리전으로 확장된다. 최신 서비스가 필요한 경우 리전별 서비스 가용성을 확인해야 한다.

**4. 규정 준수 (Compliance)**

특정 국가의 법률에 따라 데이터가 해당 국가 내에 저장되어야 하는 경우가 있다. 한국의 개인정보보호법은 특정 유형의 데이터가 국내에 저장되도록 요구할 수 있다.

> **실무 팁**: 대부분의 한국 서비스라면 **ap-northeast-2(서울)**을 기본 리전으로 선택하면 된다. 글로벌 서비스라면 사용자 분포에 따라 여러 리전에 배포하되, CloudFront CDN을 앞에 두면 전 세계 사용자에게 빠른 응답을 제공할 수 있다.

### 1.3 가용 영역 (Availability Zone, AZ)

가용 영역(*Availability Zone - 리전 내에서 물리적으로 분리된 독립 데이터센터*)은 리전 안에 있는 개별 데이터센터(또는 데이터센터 클러스터)이다. 각 리전은 보통 **3개 이상의 AZ**로 구성된다.

```
서울 리전 (ap-northeast-2)
├── AZ-a (ap-northeast-2a)  ─── 데이터센터 A
├── AZ-b (ap-northeast-2b)  ─── 데이터센터 B
├── AZ-c (ap-northeast-2c)  ─── 데이터센터 C
└── AZ-d (ap-northeast-2d)  ─── 데이터센터 D
```

**AZ 간 특성:**

| 특성 | 설명 |
|------|------|
| **물리적 격리** | 각 AZ는 별도의 전력, 냉각, 물리적 보안을 가진다 |
| **저지연 연결** | AZ 간에는 고대역폭, 저지연 프라이빗 네트워크로 연결 |
| **독립적 장애 도메인** | 한 AZ의 정전/화재가 다른 AZ에 영향을 주지 않음 |

**왜 AZ가 중요한가?**

고가용성(*High Availability - 시스템이 장애 상황에서도 계속 서비스를 제공하는 능력*)을 달성하려면 리소스를 **여러 AZ에 분산 배치**해야 한다. 예를 들어:

- RDS를 **Multi-AZ**로 설정하면, 주 데이터베이스가 있는 AZ에 장애가 발생해도 다른 AZ의 복제본이 즉시 역할을 인수한다.
- EC2 인스턴스를 여러 AZ에 분산하고 로드밸런서를 앞에 두면, 한 AZ가 다운되어도 나머지 AZ의 인스턴스가 트래픽을 처리한다.

> **핵심 통찰**: "단일 AZ에 모든 리소스를 배치하는 것"은 AWS에서 가장 흔한 아키텍처 실수 중 하나다. 프로덕션 환경에서는 반드시 **Multi-AZ 구성**을 고려해야 한다. 비용이 조금 더 들지만, AZ 장애 시 전체 서비스가 다운되는 것보다 훨씬 낫다.

### 1.4 엣지 로케이션 (Edge Location)

엣지 로케이션(*Edge Location - 전 세계 주요 도시에 분산된 캐시 서버*)은 CloudFront(CDN)와 Route 53(DNS)이 사용하는 인프라다. 리전보다 훨씬 많은 수(450개 이상)가 전 세계에 분포되어 있다.

```
인프라 계층 구조:

글로벌
├── 엣지 로케이션 (450+) ─── CloudFront, Route 53
│     서울, 부산, 도쿄, 오사카, 싱가포르, ...
│
└── 리전 (33+)
      ├── ap-northeast-2 (서울)
      │     ├── AZ-a
      │     ├── AZ-b
      │     ├── AZ-c
      │     └── AZ-d
      ├── us-east-1 (버지니아)
      │     ├── AZ-a ~ AZ-f (6개)
      └── ...
```

프론트엔드 개발자에게 엣지 로케이션은 특히 중요하다. Next.js나 React 앱의 정적 에셋(JS 번들, 이미지 등)을 CloudFront를 통해 배포하면, 사용자에게 가장 가까운 엣지 로케이션에서 콘텐츠가 제공되므로 로딩 속도가 크게 개선된다.

### 1.5 글로벌 서비스 vs 리전 서비스

AWS 서비스는 **리전 범위**에서 동작하는 것이 기본이지만, 일부 서비스는 **글로벌**로 동작한다.

| 범위 | 서비스 | 설명 |
|------|--------|------|
| **글로벌** | IAM | 사용자/역할은 전 세계에서 동일 |
| **글로벌** | Route 53 | DNS는 글로벌로 동작 |
| **글로벌** | CloudFront | CDN은 엣지 로케이션 기반 |
| **글로벌** | WAF | CloudFront와 함께 글로벌로 동작 가능 |
| **리전** | EC2, Lambda, S3, RDS 등 | 대부분의 서비스는 리전 단위 |

> **실무 팁**: AWS 콘솔에서 작업할 때 항상 **현재 선택된 리전을 확인**하라. 서울 리전에서 만든 EC2 인스턴스가 콘솔에서 안 보인다면, 리전이 도쿄나 버지니아로 바뀌어 있을 확률이 높다. 콘솔 우측 상단에서 리전을 확인할 수 있다.

---

## 2. AWS 계정 생성

### 2.1 계정 생성 절차

AWS 계정은 https://aws.amazon.com에서 생성할 수 있다. 필요한 것은 이메일 주소, 결제용 신용카드/체크카드, 전화번호다.

**주요 단계:**

1. **이메일과 계정 이름 입력**: 이 이메일이 루트 사용자(*Root User - AWS 계정의 최고 관리자 계정. 모든 권한을 가지며, 계정의 주인*)의 로그인 ID가 된다.
2. **결제 정보 입력**: 무료 체험(Free Tier) 범위 내에서는 과금되지 않지만, 결제 정보는 필수다.
3. **본인 인증**: 전화번호 또는 SMS 인증.
4. **지원 플랜 선택**: 학습 목적이라면 **Basic(무료)** 플랜으로 충분하다.

### 2.2 루트 사용자 보안 설정

계정을 생성하면 가장 먼저 해야 할 일은 **루트 사용자를 보호**하는 것이다. 루트 사용자는 계정의 모든 리소스에 대한 완전한 제어 권한을 가지며, 이 권한은 제한할 수 없다.

**필수 보안 조치:**

1. **MFA(Multi-Factor Authentication) 활성화**: 루트 사용자에 반드시 MFA를 설정한다. 비밀번호가 유출되어도 물리적 디바이스(또는 인증 앱) 없이는 로그인할 수 없도록 한다.
2. **루트 사용자 사용 최소화**: 루트 사용자로 일상적인 작업을 하지 않는다. IAM 사용자를 생성하여 사용한다(Chapter 3에서 다룸).
3. **강력한 비밀번호 설정**: 다른 서비스에서 사용하지 않는 고유한 강력한 비밀번호를 설정한다.

```
루트 사용자를 사용해야 하는 경우 (이것만 루트로):
- 계정 설정 변경 (이메일, 비밀번호, 결제 정보)
- IAM 사용자가 처음으로 생성될 때
- 계정 해지
- 지원 플랜 변경
- 특정 S3 버킷 정책 복구

그 외 모든 작업: IAM 사용자/역할 사용
```

---

## 3. Free Tier와 빌링 관리

### 3.1 Free Tier의 세 가지 유형

AWS Free Tier는 세 가지 유형으로 나뉜다. 이를 정확히 이해하지 못하면 예상치 못한 과금이 발생할 수 있다.

| 유형 | 기간 | 설명 | 예시 |
|------|------|------|------|
| **12개월 무료** | 계정 생성 후 12개월 | 인기 서비스의 일정 사용량 무료 | EC2 t2.micro 750시간/월, S3 5GB |
| **항상 무료** | 무기한 | 기간 제한 없이 일정 사용량 무료 | Lambda 월 100만 요청, DynamoDB 25GB |
| **단기 체험** | 일회성 | 특정 서비스의 체험 기간 | SageMaker 2개월, Redshift 2개월 |

**12개월 무료의 주요 서비스:**

| 서비스 | 무료 한도 (월) | 초과 시 비용 (서울 리전 기준) |
|--------|-------------|--------------------------|
| **EC2** (t2.micro/t3.micro) | 750시간 | ~$0.013/시간 |
| **S3** | 5GB 스토리지, GET 20,000건 | $0.025/GB |
| **RDS** (db.t2.micro/t3.micro) | 750시간 | ~$0.028/시간 |
| **CloudFront** | 1TB 데이터 전송 | $0.114/GB |
| **Lambda** | 100만 요청, 40만 GB-초 | $0.20/100만 요청 |

> **비용 주의**: Free Tier의 "12개월"은 계정 생성일 기준이다. 1년이 지나면 무료 한도가 사라지고 모든 리소스에 과금이 시작된다. 학습용으로 만든 EC2 인스턴스나 RDS를 방치하면 매달 수십 달러가 청구될 수 있다. **사용하지 않는 리소스는 즉시 삭제하라.**

### 3.2 빌링 알림 설정 (필수!)

AWS를 사용하기 시작했다면, 가장 먼저 **빌링 알림**을 설정해야 한다. 예상치 못한 과금을 방지하는 최소한의 안전장치다.

**방법 1: AWS Budgets (권장)**

AWS Budgets는 예산을 설정하고 초과 시 알림을 받을 수 있는 서비스다.

```
설정 절차:
1. AWS 콘솔 → Billing and Cost Management → Budgets
2. "Create budget" 클릭
3. "Cost budget" 선택
4. 예산 금액 설정 (예: $10/월)
5. 알림 조건 설정:
   - 실제 비용이 80%에 도달하면 알림
   - 실제 비용이 100%에 도달하면 알림
   - 예측 비용이 100%를 초과하면 알림
6. 이메일 주소 입력
7. "Create budget" 완료
```

**방법 2: CloudWatch Billing Alarm**

```bash
# AWS CLI로 빌링 알림 생성 (us-east-1 리전에서만 가능)
aws cloudwatch put-metric-alarm \
  --alarm-name "BillingAlarm-10USD" \
  --alarm-description "Alarm when charges exceed $10" \
  --metric-name EstimatedCharges \
  --namespace AWS/Billing \
  --statistic Maximum \
  --period 21600 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=Currency,Value=USD \
  --evaluation-periods 1 \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT_ID:billing-alerts \
  --region us-east-1
```

### 3.3 비용 확인 방법

```bash
# 이번 달 비용 확인
aws ce get-cost-and-usage \
  --time-period Start=2024-03-01,End=2024-03-31 \
  --granularity MONTHLY \
  --metrics "BlendedCost" \
  --output table

# 서비스별 비용 분석
aws ce get-cost-and-usage \
  --time-period Start=2024-03-01,End=2024-03-31 \
  --granularity MONTHLY \
  --metrics "BlendedCost" \
  --group-by Type=DIMENSION,Key=SERVICE \
  --output table
```

### 3.4 Budget Actions로 과금 안전장치 설정 (실습)

빌링 알림은 "알려주기만" 할 뿐 과금을 막지는 않는다. AWS에는 "일정 금액 초과 시 모든 서비스를 자동 차단"하는 기능이 없지만, **Budget Actions**를 설정하면 예산 초과 시 EC2/RDS를 자동 중지하고 새 리소스 생성을 제한할 수 있다. 토이 프로젝트 수준에서는 이것만으로 충분한 안전장치가 된다.

> **실무 팁**: AWS가 자동 차단 기능을 제공하지 않는 이유는 프로덕션 서비스가 예산 초과만으로 중단되면 더 큰 피해가 발생하기 때문이다. 하지만 학습/토이 프로젝트에서는 Budget Actions를 적극 활용하는 것이 안전하다.

**Step 1: 예산 생성**

```
1. AWS 콘솔 → Billing and Cost Management → Budgets
2. "Create budget" 클릭
3. "Customize (advanced)" 선택
4. "Cost budget" 선택 → Next
5. 예산 설정:
   - Budget name: "MonthlyLimit-10USD"
   - Period: Monthly
   - Budget amount: Fixed → $10.00
6. Next
```

**Step 2: 알림 임계값 설정**

```
알림 조건 (3개 권장):
┌─────────────┬──────────────────────┬──────────────────────┐
│ 임계값       │ 조건                  │ 목적                  │
├─────────────┼──────────────────────┼──────────────────────┤
│ 50% ($5)    │ Actual cost > 50%    │ 조기 경고              │
│ 80% ($8)    │ Actual cost > 80%    │ 주의 경고              │
│ 100% ($10)  │ Actual cost > 100%   │ 자동 조치 트리거        │
└─────────────┴──────────────────────┴──────────────────────┘

각 임계값에 이메일 주소를 입력한다.
```

**Step 3: Budget Action 설정 (핵심)**

100% 임계값에 자동 조치를 연결한다:

```
1. 100% 알림의 "Add Action" 클릭
2. Action 설정:
   - Action type: "Apply IAM policy"
   - IAM policy: "AWS managed policy → AWSBudgetsActions_SSMRunCommand"
     또는 커스텀 정책으로 Deny All 설정
   - Action trigger: Automatic (자동 실행)
   - Target: 제한할 IAM 사용자/역할 선택
3. "Create budget" 완료
```

**커스텀 Deny 정책 예시:**

예산 초과 시 적용할 IAM 정책을 미리 만들어두면, 새 리소스 생성을 완전히 차단할 수 있다.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyAllExceptBillingAndBudgets",
      "Effect": "Deny",
      "NotAction": [
        "budgets:*",
        "billing:*",
        "aws-portal:*",
        "iam:Get*",
        "iam:List*",
        "sts:GetCallerIdentity"
      ],
      "Resource": "*"
    }
  ]
}
```

이 정책이 적용되면 Billing/Budgets 관련 작업만 허용되고, EC2 생성, S3 업로드 등 **모든 리소스 조작이 차단**된다. 예산을 조정하거나 불필요한 리소스를 삭제한 뒤, Budgets 콘솔에서 Action을 해제하면 다시 정상적으로 사용할 수 있다.

**Step 4: EC2/RDS 자동 중지 Action 추가 (선택)**

EC2나 RDS를 사용 중이라면 중지 액션도 함께 설정할 수 있다:

```
1. 100% 알림에 Action 추가
2. Action type: "Run SSM action"
3. SSM action: "Stop EC2 instances" 또는 "Stop RDS instances"
4. Target: 중지할 인스턴스의 태그 또는 리전 지정
5. Action trigger: Automatic
```

**최종 안전장치 구성:**

```
$5 (50%) → 이메일 알림
$8 (80%) → 이메일 알림
$10 (100%) → 이메일 알림
              + IAM Deny 정책 자동 적용 (새 리소스 생성 차단)
              + EC2/RDS 자동 중지 (선택)
```

> **비용 주의**: Budget Actions 자체는 **무료**다. AWS Budgets도 처음 2개 예산까지 무료이므로, 이 설정에 추가 비용이 발생하지 않는다. 계정 생성 직후, 어떤 실습보다도 먼저 이 안전장치를 설정하라.

---

## 4. AWS CLI 설치와 설정

AWS 콘솔(웹 UI)으로도 모든 작업을 할 수 있지만, **AWS CLI**를 사용하면 터미널에서 훨씬 빠르고 정확하게 작업할 수 있다. 특히 반복적인 작업이나 자동화에 필수적이다.

### 4.1 설치

**macOS:**

```bash
# Homebrew로 설치 (권장)
brew install awscli

# 또는 공식 설치 프로그램
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /

# 설치 확인
aws --version
# aws-cli/2.x.x Python/3.x.x Darwin/... source/arm64
```

**Linux:**

```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

aws --version
```

### 4.2 자격 증명 설정

CLI를 사용하려면 AWS에 인증할 자격 증명이 필요하다. 이를 위해 IAM 사용자의 **액세스 키(Access Key)**를 사용한다.

```bash
# 초기 설정
aws configure

# 입력 항목:
# AWS Access Key ID: AKIA...     (IAM 사용자의 액세스 키)
# AWS Secret Access Key: wJal...  (IAM 사용자의 비밀 액세스 키)
# Default region name: ap-northeast-2  (기본 리전: 서울)
# Default output format: json     (출력 형식: json, table, text)
```

설정은 `~/.aws/` 디렉토리에 저장된다:

```bash
# ~/.aws/credentials (자격 증명)
[default]
aws_access_key_id = AKIA...
aws_secret_access_key = wJal...

# ~/.aws/config (설정)
[default]
region = ap-northeast-2
output = json
```

### 4.3 프로필(Profile)을 이용한 다중 계정 관리

개인 계정과 회사 계정을 동시에 사용하거나, 개발/스테이징/프로덕션 환경을 분리할 때 프로필이 유용하다.

```bash
# 프로필 추가
aws configure --profile personal
aws configure --profile work

# 프로필 지정하여 사용
aws s3 ls --profile personal
aws ec2 describe-instances --profile work

# 환경 변수로 기본 프로필 변경
export AWS_PROFILE=personal
aws s3 ls  # personal 프로필 사용
```

```bash
# ~/.aws/credentials
[default]
aws_access_key_id = AKIA_DEFAULT...
aws_secret_access_key = ...

[personal]
aws_access_key_id = AKIA_PERSONAL...
aws_secret_access_key = ...

[work]
aws_access_key_id = AKIA_WORK...
aws_secret_access_key = ...
```

### 4.4 설정 확인

```bash
# 현재 자격 증명이 어떤 IAM 사용자/역할인지 확인
aws sts get-caller-identity
# {
#   "UserId": "AIDA...",
#   "Account": "123456789012",
#   "Arn": "arn:aws:iam::123456789012:user/my-user"
# }

# 현재 설정된 리전 확인
aws configure get region
# ap-northeast-2
```

> **실무 팁**: 액세스 키를 **코드에 직접 하드코딩하지 마라**. Git 저장소에 푸시되면 AWS 계정이 탈취될 수 있다. GitHub에는 AWS 키를 스캔하는 봇이 있으며, 유출된 키는 수 분 내에 암호화폐 채굴 등에 악용된다. 키 대신 IAM 역할(Chapter 3)이나 환경 변수를 사용하라.

---

## 5. AWS Management Console

### 5.1 콘솔 기본 구조

AWS Management Console은 웹 브라우저에서 AWS 리소스를 관리하는 GUI이다. https://console.aws.amazon.com에서 접근한다.

```
콘솔 레이아웃:

┌─────────────────────────────────────────────────────┐
│ [🔍 서비스 검색]        리전: ap-northeast-2 ▼  👤  │  ← 상단 바
├─────────────────────────────────────────────────────┤
│                                                     │
│  최근 방문한 서비스     즐겨찾기                      │
│  ├── EC2              ├── S3                        │
│  ├── S3               ├── Lambda                    │
│  └── CloudFront       └── CloudWatch                │
│                                                     │
│  [서비스 카테고리별 목록]                              │
│  컴퓨팅: EC2, Lambda, ECS, ...                       │
│  스토리지: S3, EBS, EFS, ...                         │
│  데이터베이스: RDS, DynamoDB, ...                     │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**핵심 팁:**

- **서비스 검색**: 상단 검색창에 서비스 이름을 입력하면 빠르게 이동할 수 있다. 200개 이상의 서비스 중에서 메뉴를 탐색하는 것보다 훨씬 빠르다.
- **리전 확인**: 우측 상단에 현재 리전이 표시된다. 리소스가 보이지 않으면 리전이 잘못 설정되어 있을 확률이 높다.
- **즐겨찾기**: 자주 사용하는 서비스는 별표(☆)를 눌러 즐겨찾기에 추가하면 빠르게 접근할 수 있다.

### 5.2 CloudShell

CloudShell은 AWS 콘솔 내에서 바로 사용할 수 있는 브라우저 기반 터미널이다. AWS CLI가 사전 설치되어 있으며, 별도의 자격 증명 설정 없이 현재 콘솔에 로그인한 사용자의 권한으로 CLI 명령을 실행할 수 있다.

```bash
# CloudShell 열기: 콘솔 하단 바의 터미널 아이콘 클릭 (또는 상단 바)

# 별도 설정 없이 바로 사용 가능
aws s3 ls
aws sts get-caller-identity
```

로컬에 AWS CLI를 아직 설치하지 않았다면, CloudShell로 먼저 실습해볼 수 있다.

---

## 자주 하는 실수

| 실수 | 설명 | 올바른 접근 |
|------|------|------------|
| **리전을 확인하지 않음** | 서울에서 만든 리소스가 도쿄 리전 콘솔에서 안 보임 | 작업 전 항상 콘솔 우측 상단 리전 확인 |
| **빌링 알림 미설정** | 방치된 리소스로 예상치 못한 과금 발생 | 계정 생성 직후 $10 예산 알림 설정 |
| **루트 사용자로 일상 작업** | 보안 사고 시 계정 전체가 위험에 노출 | IAM 사용자를 생성하여 일상 작업에 사용 |
| **액세스 키를 코드에 하드코딩** | Git에 푸시되면 수 분 내에 악용됨 | 환경 변수, IAM 역할, AWS CLI 프로필 사용 |
| **단일 AZ에 모든 리소스 배치** | AZ 장애 시 서비스 전체 다운 | 프로덕션은 Multi-AZ 구성 필수 |
| **Free Tier 만료 후 리소스 방치** | 12개월 후 자동 과금 시작 | 캘린더에 Free Tier 만료일 기록, 불필요 리소스 삭제 |

---

## AWS CLI 레퍼런스

| 명령어 | 설명 |
|--------|------|
| `aws configure` | CLI 자격 증명 및 기본 설정 구성 |
| `aws configure --profile NAME` | 특정 프로필의 설정 구성 |
| `aws configure list` | 현재 활성 설정 확인 |
| `aws sts get-caller-identity` | 현재 인증된 사용자/역할 정보 확인 |
| `aws configure get region` | 현재 기본 리전 확인 |
| `aws ce get-cost-and-usage ...` | 비용 및 사용량 조회 |

---

## 요약

- AWS 인프라는 **리전 → 가용 영역(AZ) → 엣지 로케이션**의 계층 구조를 갖는다.
- 리전 선택은 **지연 시간, 비용, 서비스 가용성, 규정 준수** 네 가지 요소를 기준으로 한다. 한국 서비스는 **ap-northeast-2(서울)**이 기본이다.
- **Multi-AZ 배포**는 프로덕션 환경에서 고가용성을 위한 필수 구성이다.
- 엣지 로케이션(450+)은 CloudFront와 Route 53이 사용하며, 사용자에게 가장 가까운 위치에서 콘텐츠를 제공한다.
- 계정 생성 후 반드시 **루트 사용자 MFA 활성화**와 **빌링 알림 설정**을 수행하라.
- **Free Tier**는 세 가지 유형(12개월 무료, 항상 무료, 단기 체험)이 있으며, 한도 초과 시 과금된다.
- AWS CLI는 `aws configure`로 설정하며, 프로필을 이용해 다중 계정을 관리할 수 있다.
- 액세스 키를 코드에 하드코딩하지 마라. IAM 역할이나 환경 변수를 사용하라.
