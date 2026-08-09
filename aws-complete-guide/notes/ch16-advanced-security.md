# Chapter 16: 보안 심화: Advanced Security

## 핵심 질문

프로덕션 환경에서 AWS 인프라를 안전하게 운영하려면 어떤 보안 계층이 필요한가? 네트워크 방화벽, 웹 애플리케이션 보호, 비밀 정보 관리, 암호화, SSL/TLS 인증서까지 — AWS가 제공하는 보안 서비스를 어떻게 조합하여 견고한 보안 아키텍처를 구축하는가?

---

## 1. 공동 책임 모델 (Shared Responsibility Model)

### 1.1 AWS의 보안 철학

AWS 보안의 출발점은 공동 책임 모델(*Shared Responsibility Model - 보안에 대한 책임을 AWS와 고객이 분담하는 모델. AWS는 "클라우드의" 보안을, 고객은 "클라우드 안의" 보안을 책임진다*)이다. 이 모델을 이해하지 않으면 "AWS가 알아서 해주겠지"라는 위험한 가정에 빠질 수 있다.

```
공동 책임 모델:

┌───────────────────────────────────────────────────────┐
│                 고객의 책임                              │
│          "클라우드 안의(in the Cloud) 보안"               │
│                                                       │
│  ┌─────────────────────────────────────────────────┐  │
│  │  고객 데이터                                      │  │
│  ├─────────────────────────────────────────────────┤  │
│  │  플랫폼, 애플리케이션, IAM                         │  │
│  ├─────────────────────────────────────────────────┤  │
│  │  OS, 네트워크, 방화벽 설정                         │  │
│  ├─────────────────────────────────────────────────┤  │
│  │  클라이언트/서버 측 암호화, 네트워크 트래픽 보호      │  │
│  └─────────────────────────────────────────────────┘  │
├───────────────────────────────────────────────────────┤
│                  AWS의 책임                             │
│          "클라우드의(of the Cloud) 보안"                  │
│                                                       │
│  ┌─────────────────────────────────────────────────┐  │
│  │  하드웨어/AWS 글로벌 인프라                         │  │
│  ├─────────────────────────────────────────────────┤  │
│  │  리전, 가용 영역, 엣지 로케이션                     │  │
│  ├─────────────────────────────────────────────────┤  │
│  │  컴퓨팅, 스토리지, 데이터베이스, 네트워킹 (물리)     │  │
│  ├─────────────────────────────────────────────────┤  │
│  │  관리형 서비스의 소프트웨어 패치                     │  │
│  └─────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────┘
```

### 1.2 서비스별 책임 범위

AWS가 관리하는 범위는 서비스 유형에 따라 달라진다. 관리형 서비스일수록 고객의 책임이 줄어든다.

| 서비스 유형 | 예시 | AWS의 책임 | 고객의 책임 |
|------------|------|-----------|------------|
| **IaaS** | EC2 | 물리 서버, 가상화 | OS 패치, 보안 그룹, 애플리케이션 |
| **관리형 서비스** | RDS, ECS | OS 패치, 엔진 업데이트 | 데이터 암호화, 네트워크 설정, IAM |
| **서버리스** | Lambda, DynamoDB | 실행 환경 전체 | IAM 정책, 코드 보안, 데이터 암호화 |
| **완전 관리형** | S3, CloudFront | 인프라 전체 | 버킷 정책, 암호화 설정, 접근 제어 |

> **핵심 통찰**: **"관리형 서비스를 쓴다고 보안이 자동으로 되는 것은 아니다."** RDS가 OS 패치를 해준다고 해서 데이터베이스 비밀번호 관리, 네트워크 격리, 암호화 설정까지 AWS가 해주는 것은 아니다. 서비스 유형별로 고객의 책임 범위를 정확히 이해하고, 빠짐없이 설정해야 한다.

---

## 2. 보안 그룹 vs 네트워크 ACL 심화

Chapter 4에서 보안 그룹과 네트워크 ACL의 기본 개념을 다루었다. 여기서는 프로덕션 환경에서의 실전 규칙 설계를 다룬다.

### 2.1 핵심 차이 복습

```
트래픽 흐름에서의 평가 순서:

인터넷
  │
  ↓ ① 네트워크 ACL (서브넷 경계)
  │    → Stateless: 인바운드/아웃바운드 각각 평가
  │    → 규칙 번호 순서대로 평가, 첫 매치에서 결정
  │
  ↓ ② 보안 그룹 (인스턴스 경계)
  │    → Stateful: 인바운드 허용 → 응답 자동 허용
  │    → 모든 규칙 평가 후 허용 여부 결정
  │
  ↓
리소스 (EC2, RDS 등)
```

| 특성 | 보안 그룹 (Security Group) | 네트워크 ACL (NACL) |
|------|--------------------------|-------------------|
| **적용 수준** | 인스턴스 (ENI) | 서브넷 |
| **상태 관리** | Stateful | Stateless |
| **규칙 유형** | 허용만 가능 (Allow only) | 허용 + 거부 가능 (Allow/Deny) |
| **규칙 평가** | 모든 규칙 평가 | 번호 순서대로, 첫 매치 적용 |
| **기본 동작** | 인바운드 전체 거부 | 기본 ACL: 전체 허용 |
| **IP 차단** | 불가능 (허용만 정의) | 가능 (특정 IP 거부 규칙 추가) |
| **보안 그룹 참조** | 가능 | 불가능 (IP/CIDR만 지정) |

### 2.2 Stateless의 함정: 임시 포트

네트워크 ACL이 Stateless라는 점은 실전에서 가장 자주 혼란을 일으킨다. HTTP 요청을 허용하려면 인바운드뿐 아니라 **아웃바운드의 임시 포트**(*Ephemeral Port - 클라이언트가 서버에 연결할 때 자동으로 할당받는 임시 포트 번호. 보통 1024-65535 범위*)도 열어야 한다.

```
NACL에서 HTTP 트래픽 허용:

클라이언트 (포트 52431) ─── HTTP 요청 ──→ 서버 (포트 80)
                         ← HTTP 응답 ──── 서버 (포트 80 → 포트 52431)

인바운드 규칙: 포트 80 허용 ✅
아웃바운드 규칙: 포트 1024-65535 허용 필요! ← 이걸 빠뜨리면 응답이 나갈 수 없다
```

### 2.3 프로덕션 네트워크 ACL 설계

**퍼블릭 서브넷 NACL:**

| 규칙 # | 유형 | 방향 | 프로토콜 | 포트 | 소스/대상 | 허용/거부 |
|--------|------|------|---------|------|----------|---------|
| 100 | 인바운드 | In | TCP | 80 | 0.0.0.0/0 | 허용 |
| 110 | 인바운드 | In | TCP | 443 | 0.0.0.0/0 | 허용 |
| 120 | 인바운드 | In | TCP | 1024-65535 | 0.0.0.0/0 | 허용 |
| * | 인바운드 | In | 전체 | 전체 | 0.0.0.0/0 | 거부 |
| 100 | 아웃바운드 | Out | TCP | 80 | 0.0.0.0/0 | 허용 |
| 110 | 아웃바운드 | Out | TCP | 443 | 0.0.0.0/0 | 허용 |
| 120 | 아웃바운드 | Out | TCP | 1024-65535 | 0.0.0.0/0 | 허용 |
| * | 아웃바운드 | Out | 전체 | 전체 | 0.0.0.0/0 | 거부 |

```bash
# 네트워크 ACL 생성 및 규칙 추가
aws ec2 create-network-acl --vpc-id vpc-0abc123

# 인바운드: HTTPS 허용
aws ec2 create-network-acl-entry \
  --network-acl-id acl-0abc123 \
  --rule-number 110 \
  --protocol tcp \
  --port-range From=443,To=443 \
  --cidr-block 0.0.0.0/0 \
  --rule-action allow \
  --ingress

# 아웃바운드: 임시 포트 허용 (응답 트래픽)
aws ec2 create-network-acl-entry \
  --network-acl-id acl-0abc123 \
  --rule-number 120 \
  --protocol tcp \
  --port-range From=1024,To=65535 \
  --cidr-block 0.0.0.0/0 \
  --rule-action allow \
  --egress
```

### 2.4 특정 IP 차단 (NACL의 핵심 활용)

보안 그룹은 허용만 정의할 수 있지만, NACL은 **특정 IP를 명시적으로 거부**할 수 있다. 이것이 NACL을 사용하는 가장 대표적인 이유이다.

```bash
# 공격이 감지된 IP를 서브넷 수준에서 차단
# 규칙 번호가 낮을수록 먼저 평가됨 → 차단 규칙은 낮은 번호로
aws ec2 create-network-acl-entry \
  --network-acl-id acl-0abc123 \
  --rule-number 50 \
  --protocol -1 \
  --cidr-block 203.0.113.0/24 \
  --rule-action deny \
  --ingress
```

> **실무 팁**: 보안 그룹을 **주 방화벽**으로, 네트워크 ACL을 **보조 방화벽**으로 사용하라. 보안 그룹으로 대부분의 접근 제어를 처리하고, NACL은 특정 IP 대역 차단이나 서브넷 수준의 추가 방어 계층이 필요할 때만 사용한다. 둘을 동시에 세밀하게 관리하면 복잡성이 급격히 증가한다.

---

## 3. WAF (Web Application Firewall)

### 3.1 WAF란

WAF(*Web Application Firewall - HTTP/HTTPS 요청을 검사하여 SQL 인젝션, XSS, 악성 봇 등 웹 애플리케이션 계층의 공격을 차단하는 서비스*)는 보안 그룹이나 NACL이 다루지 못하는 **애플리케이션 계층(Layer 7)**의 공격을 방어한다.

```
보안 계층 비교:

Layer 3/4 (네트워크/전송 계층):
  보안 그룹 ── IP, 포트, 프로토콜 기반 필터링
  NACL ─────── 서브넷 수준 IP/포트 필터링

Layer 7 (애플리케이션 계층):
  WAF ────── HTTP 요청의 내용(헤더, 본문, URI)을 검사
             SQL 인젝션, XSS, 악성 봇 차단
             요청 속도 제한 (Rate Limiting)
```

### 3.2 WAF 구성 요소

```
WAF 아키텍처:

┌─────────────────────────────────────────────────┐
│                  웹 ACL (Web ACL)                 │
│                                                  │
│  ┌──────────────────────────────────────────┐    │
│  │ Rule 1: AWS Managed Rules - Common       │    │
│  │  → SQL 인젝션, XSS 등 일반적인 공격 차단    │    │
│  │  → Action: Block                          │    │
│  ├──────────────────────────────────────────┤    │
│  │ Rule 2: Rate Limiting                     │    │
│  │  → 동일 IP에서 5분당 2,000회 초과 차단      │    │
│  │  → Action: Block                          │    │
│  ├──────────────────────────────────────────┤    │
│  │ Rule 3: 특정 국가 차단                      │    │
│  │  → Geo Match 조건                          │    │
│  │  → Action: Block                          │    │
│  ├──────────────────────────────────────────┤    │
│  │ Default Action: Allow                     │    │
│  │  → 위 규칙에 매치되지 않으면 허용             │    │
│  └──────────────────────────────────────────┘    │
│                                                  │
│  연결 대상: CloudFront / ALB / API Gateway        │
└─────────────────────────────────────────────────┘
```

| 구성 요소 | 설명 |
|----------|------|
| **웹 ACL** (*Web ACL*) | WAF 규칙들의 컨테이너. CloudFront, ALB, API Gateway에 연결한다 |
| **규칙 (Rule)** | 요청을 검사하는 조건과 동작(Block/Allow/Count)의 조합 |
| **규칙 그룹 (Rule Group)** | 여러 규칙을 묶어 재사용 가능한 단위로 관리 |
| **AWS Managed Rules** | AWS가 관리하는 사전 정의된 규칙 그룹 |

### 3.3 AWS Managed Rules

AWS가 직접 관리하는 규칙 그룹을 사용하면, OWASP Top 10 등 일반적인 웹 공격을 별도의 규칙 작성 없이 차단할 수 있다.

| Managed Rule Group | 차단 대상 | WCU |
|-------------------|----------|-----|
| **AWSManagedRulesCommonRuleSet** | SQL 인젝션, XSS, LFI 등 일반 공격 | 700 |
| **AWSManagedRulesSQLiRuleSet** | SQL 인젝션에 특화 | 200 |
| **AWSManagedRulesKnownBadInputsRuleSet** | Log4j, 알려진 악성 입력 | 200 |
| **AWSManagedRulesAmazonIpReputationList** | 악성 IP 평판 목록 | 25 |
| **AWSManagedRulesBotControlRuleSet** | 봇 트래픽 관리 | 50 |

> WCU(*Web ACL Capacity Unit - WAF 규칙의 처리 비용을 나타내는 단위. 웹 ACL당 최대 5,000 WCU*)는 웹 ACL 하나가 처리할 수 있는 규칙의 총량을 제한한다.

### 3.4 WAF 설정

```bash
# 1. 웹 ACL 생성 (CloudFront 연동용은 반드시 us-east-1에서 생성)
aws wafv2 create-web-acl \
  --name my-web-acl \
  --scope CLOUDFRONT \
  --region us-east-1 \
  --default-action Allow={} \
  --visibility-config SampledRequestsEnabled=true,CloudWatchMetricsEnabled=true,MetricName=my-web-acl \
  --rules '[
    {
      "Name": "AWS-AWSManagedRulesCommonRuleSet",
      "Priority": 0,
      "Statement": {
        "ManagedRuleGroupStatement": {
          "VendorName": "AWS",
          "Name": "AWSManagedRulesCommonRuleSet"
        }
      },
      "OverrideAction": { "None": {} },
      "VisibilityConfig": {
        "SampledRequestsEnabled": true,
        "CloudWatchMetricsEnabled": true,
        "MetricName": "CommonRuleSet"
      }
    },
    {
      "Name": "RateLimitRule",
      "Priority": 1,
      "Statement": {
        "RateBasedStatement": {
          "Limit": 2000,
          "AggregateKeyType": "IP"
        }
      },
      "Action": { "Block": {} },
      "VisibilityConfig": {
        "SampledRequestsEnabled": true,
        "CloudWatchMetricsEnabled": true,
        "MetricName": "RateLimit"
      }
    }
  ]'
```

### 3.5 CloudFront + WAF 연동

CloudFront 배포에 WAF를 연결하면 엣지 로케이션에서 악성 트래픽을 차단할 수 있다. 오리진 서버에 도달하기 전에 차단하므로, 서버 부하도 줄어든다.

```bash
# CloudFront 배포에 웹 ACL 연결
aws cloudfront update-distribution \
  --id E1ABCDEF123456 \
  --distribution-config '{
    ...기존 설정...,
    "WebACLId": "arn:aws:wafv2:us-east-1:123456789012:global/webacl/my-web-acl/abc123"
  }'
```

```
CloudFront + WAF 아키텍처:

사용자 ──→ CloudFront 엣지 ──→ WAF 검사 ──→ 오리진 (S3, ALB)
                │                  │
                │                  ├── 정상 요청 → 허용 → 오리진으로 전달
                │                  ├── SQL 인젝션 → 차단 → 403 반환
                │                  └── Rate 초과 → 차단 → 429 반환
                │
                └── 악성 트래픽이 오리진에 도달하지 않음
```

> **실무 팁**: 새로운 WAF 규칙을 적용할 때는 먼저 **Count 모드**로 설정하여 어떤 요청이 매치되는지 모니터링하라. 정상적인 요청이 오탐(*False Positive - 정상 요청을 악성으로 잘못 판별하는 것*)으로 차단되지 않는지 충분히 확인한 후 Block 모드로 전환한다. 특히 AWS Managed Rules의 일부 규칙은 API 요청의 JSON 본문을 SQL 인젝션으로 오인할 수 있다.

---

## 4. AWS Shield (DDoS 방어)

### 4.1 Shield Standard vs Shield Advanced

AWS Shield(*AWS Shield - DDoS(Distributed Denial of Service) 공격으로부터 AWS 리소스를 보호하는 서비스*)는 DDoS 공격에 대한 방어를 제공한다.

| 특성 | Shield Standard | Shield Advanced |
|------|----------------|-----------------|
| **비용** | 무료 (모든 AWS 계정에 자동 적용) | 월 $3,000 + 데이터 전송 비용 |
| **보호 대상** | CloudFront, Route 53, ALB | CloudFront, Route 53, ALB, EC2, EIP, Global Accelerator |
| **방어 수준** | Layer 3/4 공격 (SYN Flood, UDP Reflection 등) | Layer 3/4 + Layer 7 공격 |
| **DDoS 전문가 지원** | 없음 | 24/7 DDoS Response Team (DRT) |
| **비용 보호** | 없음 | DDoS로 인한 스케일링 비용을 AWS가 보전 |
| **가시성** | 기본 CloudWatch 메트릭 | 실시간 공격 가시성, 상세 보고서 |

> **비용 주의**: Shield Advanced의 **월 $3,000**은 대부분의 소규모-중규모 프로젝트에는 과도한 비용이다. Shield Standard가 Layer 3/4 DDoS 공격의 대부분을 자동으로 방어하며, **WAF의 Rate Limiting**으로 Layer 7 공격도 어느 정도 방어할 수 있다. Shield Advanced는 금융, 게임 등 DDoS 공격 피해가 치명적인 대규모 서비스에서 검토한다.

### 4.2 Shield + WAF + CloudFront 통합 방어

```
DDoS 방어 아키텍처:

인터넷
  │
  ↓
┌─────────────── Shield Standard (자동) ────────────┐
│  Layer 3/4 공격 차단 (SYN Flood, UDP Reflection)   │
├───────────────────────────────────────────────────┤
│               CloudFront (엣지)                    │
│  → 전 세계 400+ 엣지에서 트래픽 분산               │
│  → 대규모 트래픽 흡수 능력                         │
├───────────────────────────────────────────────────┤
│               WAF (Layer 7)                       │
│  → Rate Limiting으로 HTTP Flood 차단               │
│  → 악성 봇, SQL 인젝션 차단                        │
├───────────────────────────────────────────────────┤
│               오리진 서버 (ALB, EC2, S3)            │
│  → 정상 트래픽만 도달                              │
└───────────────────────────────────────────────────┘
```

---

## 5. Secrets Manager

### 5.1 비밀 정보 관리의 필요성

데이터베이스 비밀번호, API 키, OAuth 토큰 같은 민감 정보는 코드에 하드코딩하거나 환경 변수에 평문으로 저장해서는 안 된다. Secrets Manager(*Secrets Manager - 비밀 정보를 안전하게 저장하고, 프로그래밍 방식으로 조회하며, 자동 교체(rotation)를 지원하는 관리형 서비스*)는 이러한 비밀 정보의 전체 생명주기를 관리한다.

### 5.2 비밀 생성과 조회

```bash
# 비밀 생성 (DB 자격 증명)
aws secretsmanager create-secret \
  --name production/database/credentials \
  --description "프로덕션 DB 자격 증명" \
  --secret-string '{
    "username": "admin",
    "password": "s3cur3P@ssw0rd!",
    "host": "mydb.cluster-xyz.ap-northeast-2.rds.amazonaws.com",
    "port": "5432",
    "dbname": "myapp"
  }'

# 비밀 생성 (API 키)
aws secretsmanager create-secret \
  --name production/stripe/api-key \
  --secret-string '{"apiKey": "sk_live_abc123..."}'

# 비밀 조회
aws secretsmanager get-secret-value \
  --secret-id production/database/credentials

# 비밀 값 업데이트
aws secretsmanager update-secret \
  --secret-id production/database/credentials \
  --secret-string '{
    "username": "admin",
    "password": "newS3cur3P@ss!",
    "host": "mydb.cluster-xyz.ap-northeast-2.rds.amazonaws.com",
    "port": "5432",
    "dbname": "myapp"
  }'
```

### 5.3 자동 교체 (Rotation)

Secrets Manager의 가장 강력한 기능은 비밀 정보의 자동 교체(*Rotation - 비밀 정보를 주기적으로 자동 변경하여 보안을 강화하는 메커니즘. Lambda 함수를 사용하여 구현한다*)이다. RDS 데이터베이스 비밀번호를 예로 들면, Lambda 함수가 주기적으로 새 비밀번호를 생성하고 RDS에 적용하며 Secrets Manager에 저장한다.

```
자동 교체 흐름:

┌─────────────────────────────────────────────────┐
│ Secrets Manager                                  │
│                                                  │
│  1. 교체 주기 도래 (예: 30일)                      │
│     │                                            │
│  2. Rotation Lambda 호출                          │
│     │                                            │
│  3. Lambda가:                                     │
│     ├── 새 비밀번호 생성                           │
│     ├── RDS에 새 비밀번호 적용                     │
│     └── Secrets Manager에 새 값 저장              │
│                                                  │
│  4. 다음 조회부터 새 비밀번호 반환                  │
└─────────────────────────────────────────────────┘
```

```bash
# RDS 비밀의 자동 교체 활성화
aws secretsmanager rotate-secret \
  --secret-id production/database/credentials \
  --rotation-lambda-arn arn:aws:lambda:ap-northeast-2:123456789012:function:SecretsManagerRotation \
  --rotation-rules AutomaticallyAfterDays=30
```

### 5.4 Lambda에서 Secrets Manager 사용하기

```typescript
// src/handlers/api.ts
import {
  SecretsManagerClient,
  GetSecretValueCommand,
} from '@aws-sdk/client-secrets-manager';
import { Client } from 'pg';

const secretsClient = new SecretsManagerClient({});

// 핸들러 밖에서 캐시 — 실행 컨텍스트 재사용 시 API 호출 절약
let cachedCredentials: {
  username: string;
  password: string;
  host: string;
  port: string;
  dbname: string;
} | null = null;

async function getDbCredentials() {
  if (cachedCredentials) return cachedCredentials;

  const response = await secretsClient.send(
    new GetSecretValueCommand({
      SecretId: process.env.DB_SECRET_ARN!,
    })
  );

  cachedCredentials = JSON.parse(response.SecretString!);
  return cachedCredentials!;
}

export const handler = async (event: any) => {
  const creds = await getDbCredentials();

  const client = new Client({
    host: creds.host,
    port: parseInt(creds.port),
    user: creds.username,
    password: creds.password,
    database: creds.dbname,
    ssl: { rejectUnauthorized: false },
  });

  try {
    await client.connect();
    const result = await client.query('SELECT * FROM users WHERE id = $1', [
      event.pathParameters?.id,
    ]);

    return {
      statusCode: 200,
      body: JSON.stringify(result.rows[0] ?? null),
    };
  } finally {
    await client.end();
  }
};
```

### 5.5 환경 변수 vs Secrets Manager

| 기준 | 환경 변수 | Secrets Manager |
|------|----------|----------------|
| **저장 대상** | 비민감 설정 (테이블명, 로그 레벨, 리전) | 민감 정보 (DB 비밀번호, API 키, 토큰) |
| **암호화** | KMS로 저장 시 암호화되지만 콘솔에서 평문 노출 | 저장/전송 시 KMS로 암호화, 접근 시 IAM 제어 |
| **자동 교체** | 불가능 (수동 업데이트 필요) | Lambda 기반 자동 교체 지원 |
| **감사** | CloudTrail에 설정 변경 기록 | CloudTrail에 모든 접근/변경 기록 |
| **비용** | 무료 | 비밀당 $0.40/월 + API 호출 비용 |
| **크기 제한** | 전체 4KB | 비밀당 최대 64KB |

> **실무 팁**: **"이 값이 노출되면 피해가 발생하는가?"**를 기준으로 판단하라. DB 비밀번호, API 키, OAuth 시크릿은 반드시 Secrets Manager에 저장한다. 테이블 이름, 로그 레벨, 스테이지(dev/prod) 같은 비민감 설정은 환경 변수로 충분하다. Secrets Manager의 비밀 ARN 자체는 환경 변수로 Lambda에 전달하는 것이 일반적인 패턴이다.

---

## 6. KMS (Key Management Service)

### 6.1 암호화 키 관리

KMS(*Key Management Service - 암호화 키를 생성, 관리, 사용하는 서비스. AWS 서비스들의 서버 측 암호화에 사용된다*)는 AWS 전체에서 사용되는 암호화의 중심이다. S3 객체 암호화, EBS 볼륨 암호화, RDS 스토리지 암호화, Secrets Manager의 비밀 암호화 등 거의 모든 AWS 서비스의 암호화가 KMS 키를 사용한다.

```
KMS 키 유형:

┌─────────────────────────────────────────────────┐
│  AWS 관리형 키 (aws/service)                      │
│  → AWS가 자동 생성 및 관리                         │
│  → S3의 SSE-S3, RDS의 기본 암호화에 사용           │
│  → 무료                                          │
├─────────────────────────────────────────────────┤
│  고객 관리형 키 (CMK)                              │
│  → 사용자가 직접 생성                              │
│  → 키 정책, 교체 주기, 삭제 등을 직접 제어           │
│  → 월 $1/키 + API 호출 비용                        │
├─────────────────────────────────────────────────┤
│  고객 제공 키 (SSE-C)                              │
│  → 사용자가 직접 키를 생성하고 AWS에 전달            │
│  → AWS는 키를 저장하지 않음                         │
│  → KMS 비용 없음, 키 관리 부담은 사용자에게          │
└─────────────────────────────────────────────────┘
```

### 6.2 주요 서비스별 암호화

```bash
# S3 버킷: 기본 암호화 활성화 (SSE-S3)
aws s3api put-bucket-encryption \
  --bucket my-bucket \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "aws:kms",
        "KMSMasterKeyID": "arn:aws:kms:ap-northeast-2:123456789012:key/abc-123"
      },
      "BucketKeyEnabled": true
    }]
  }'

# EBS 볼륨: 암호화된 볼륨 생성
aws ec2 create-volume \
  --availability-zone ap-northeast-2a \
  --size 100 \
  --volume-type gp3 \
  --encrypted \
  --kms-key-id arn:aws:kms:ap-northeast-2:123456789012:key/abc-123

# RDS: 암호화 활성화 (인스턴스 생성 시에만 설정 가능)
aws rds create-db-instance \
  --db-instance-identifier my-db \
  --engine postgres \
  --storage-encrypted \
  --kms-key-id arn:aws:kms:ap-northeast-2:123456789012:key/abc-123 \
  # ...기타 설정
```

### 6.3 봉투 암호화 (Envelope Encryption)

봉투 암호화(*Envelope Encryption - 데이터를 데이터 키로 암호화하고, 그 데이터 키를 마스터 키(KMS 키)로 다시 암호화하는 이중 암호화 방식*)는 KMS의 핵심 개념이다. 대용량 데이터를 직접 KMS로 암호화하는 대신, 데이터 키를 사용하여 로컬에서 암호화한다.

```
봉투 암호화 흐름:

1. 데이터 키 생성 요청
   앱 ──→ KMS: "데이터 키를 생성해주세요"
   KMS ──→ 앱: 평문 데이터 키 + 암호화된 데이터 키

2. 데이터 암호화 (로컬)
   앱: 평문 데이터 키로 데이터를 암호화
   앱: 평문 데이터 키를 메모리에서 삭제!

3. 저장
   저장: [암호화된 데이터] + [암호화된 데이터 키]
         (둘 다 암호화 상태)

4. 복호화 시
   앱 ──→ KMS: "이 암호화된 데이터 키를 복호화해주세요"
   KMS ──→ 앱: 평문 데이터 키
   앱: 평문 데이터 키로 데이터를 복호화
```

**왜 봉투 암호화를 사용하는가?**

- KMS API는 **최대 4KB 데이터**만 직접 암호화/복호화할 수 있다
- 대용량 데이터를 KMS로 보내면 네트워크 비용과 지연이 발생한다
- 데이터 키로 로컬에서 암호화하면 빠르고 효율적이다
- KMS 키는 데이터 키를 보호하는 역할만 하므로 보안이 유지된다

```bash
# 데이터 키 생성 (GenerateDataKey)
aws kms generate-data-key \
  --key-id arn:aws:kms:ap-northeast-2:123456789012:key/abc-123 \
  --key-spec AES_256
# 반환: Plaintext (평문 키) + CiphertextBlob (암호화된 키)
```

> **핵심 통찰**: 대부분의 AWS 서비스(S3, EBS, RDS)는 **내부적으로 봉투 암호화를 사용**한다. 개발자가 `--encrypted` 플래그만 설정하면 KMS 키 관리, 데이터 키 생성, 암호화/복호화를 AWS가 자동으로 처리한다. 봉투 암호화를 직접 구현해야 하는 경우는 **클라이언트 측 암호화**(앱에서 직접 데이터를 암호화한 후 S3에 저장하는 경우 등)뿐이다.

---

## 7. ACM (AWS Certificate Manager)

### 7.1 SSL/TLS 인증서

ACM(*AWS Certificate Manager - SSL/TLS 인증서를 무료로 발급, 관리, 갱신하는 서비스. CloudFront, ALB, API Gateway 등에 연결하여 HTTPS를 적용한다*)은 HTTPS 통신에 필요한 SSL/TLS 인증서를 무료로 제공한다.

| 항목 | 설명 |
|------|------|
| **비용** | AWS 서비스에 연결하는 공개 인증서는 **무료** |
| **갱신** | 자동 갱신 (수동 관리 불필요) |
| **검증 방식** | DNS 검증 (권장) 또는 이메일 검증 |
| **연결 대상** | CloudFront, ALB, API Gateway, Elastic Beanstalk |
| **제한** | EC2에 직접 설치 불가 (ALB/CloudFront를 통해야 함) |

### 7.2 인증서 발급 (DNS 검증)

```bash
# 인증서 요청
aws acm request-certificate \
  --domain-name example.com \
  --subject-alternative-names "*.example.com" \
  --validation-method DNS \
  --region ap-northeast-2

# 반환된 인증서 ARN 확인
# arn:aws:acm:ap-northeast-2:123456789012:certificate/abc-123
```

DNS 검증은 Route 53에 CNAME 레코드를 추가하여 도메인 소유권을 증명한다.

```bash
# DNS 검증에 필요한 CNAME 레코드 확인
aws acm describe-certificate \
  --certificate-arn arn:aws:acm:ap-northeast-2:123456789012:certificate/abc-123 \
  --query 'Certificate.DomainValidationOptions[0].ResourceRecord'

# Route 53에 CNAME 레코드 추가 (자동 검증)
aws route53 change-resource-record-sets \
  --hosted-zone-id Z0123456789 \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "_abc123.example.com",
        "Type": "CNAME",
        "TTL": 300,
        "ResourceRecords": [{"Value": "_def456.acm-validations.aws."}]
      }
    }]
  }'
```

### 7.3 CloudFront에 인증서 연결

```bash
# CloudFront 배포에 ACM 인증서 연결
aws cloudfront update-distribution \
  --id E1ABCDEF123456 \
  --distribution-config '{
    ...기존 설정...,
    "ViewerCertificate": {
      "ACMCertificateArn": "arn:aws:acm:us-east-1:123456789012:certificate/abc-123",
      "SSLSupportMethod": "sni-only",
      "MinimumProtocolVersion": "TLSv1.2_2021"
    },
    "Aliases": {
      "Quantity": 2,
      "Items": ["example.com", "www.example.com"]
    }
  }'
```

> **실무 팁**: **CloudFront용 ACM 인증서는 반드시 `us-east-1` (버지니아 북부) 리전에서 발급**해야 한다. CloudFront는 글로벌 서비스이며, 인증서를 us-east-1에서만 가져온다. ALB용 인증서는 ALB가 위치한 리전(예: `ap-northeast-2`)에서 발급한다. 이 리전 규칙은 가장 자주 실수하는 부분이다.

### 7.4 ALB에 인증서 연결

```bash
# ALB HTTPS 리스너에 인증서 연결
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:ap-northeast-2:123456789012:loadbalancer/app/my-alb/abc123 \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=arn:aws:acm:ap-northeast-2:123456789012:certificate/abc-123 \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:ap-northeast-2:123456789012:targetgroup/my-tg/def456

# HTTP → HTTPS 리다이렉트 설정
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:ap-northeast-2:123456789012:loadbalancer/app/my-alb/abc123 \
  --protocol HTTP \
  --port 80 \
  --default-actions '[{
    "Type": "redirect",
    "RedirectConfig": {
      "Protocol": "HTTPS",
      "Port": "443",
      "StatusCode": "HTTP_301"
    }
  }]'
```

---

## 8. 프론트엔드 보안 고려사항

### 8.1 NEXT_PUBLIC_* 환경 변수의 보안 함의

Next.js에서 `NEXT_PUBLIC_` 접두사가 붙은 환경 변수는 **클라이언트 번들에 포함**된다. 즉, 브라우저의 개발자 도구에서 누구나 볼 수 있다.

```typescript
// .env.local

// ✅ 안전: 서버에서만 접근 가능
DATABASE_URL="postgresql://user:pass@host:5432/db"
STRIPE_SECRET_KEY="sk_live_abc123"

// ⚠️ 주의: 브라우저에서 노출됨
NEXT_PUBLIC_API_URL="https://api.example.com"
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY="pk_live_xyz789"
NEXT_PUBLIC_GA_TRACKING_ID="G-XXXXXXX"
```

```
NEXT_PUBLIC_ 변수의 노출 경로:

빌드 시:
  NEXT_PUBLIC_API_URL → JavaScript 번들에 리터럴로 삽입
                       → 브라우저 DevTools → Sources 탭에서 검색 가능
                       → 번들 파일 다운로드 후 grep으로 추출 가능

안전한 패턴:
  ┌─────────────────────────────────────────────────┐
  │ 클라이언트 (브라우저)                              │
  │   NEXT_PUBLIC_API_URL ✅ (공개 가능한 URL)        │
  │   NEXT_PUBLIC_STRIPE_PK ✅ (공개용 키)            │
  │                                                  │
  │   STRIPE_SECRET_KEY ❌ (서버에만!)                 │
  │   DATABASE_URL ❌ (서버에만!)                      │
  └────────────────────┬────────────────────────────┘
                       │ API 호출
                       ↓
  ┌─────────────────────────────────────────────────┐
  │ 서버 (API Route / Server Action)                 │
  │   process.env.STRIPE_SECRET_KEY ✅ (서버에서만)    │
  │   process.env.DATABASE_URL ✅ (서버에서만)         │
  └─────────────────────────────────────────────────┘
```

### 8.2 CORS 설정

CORS(*Cross-Origin Resource Sharing - 브라우저가 다른 도메인의 리소스에 접근할 수 있도록 허용하는 HTTP 메커니즘*)는 API 서버가 특정 도메인에서의 요청만 허용하도록 제어한다.

```typescript
// Next.js API Route에서 CORS 설정
// src/app/api/data/route.ts
import { NextResponse } from 'next/server';

const ALLOWED_ORIGINS = [
  'https://example.com',
  'https://www.example.com',
];

export async function GET(request: Request) {
  const origin = request.headers.get('origin') ?? '';
  const isAllowed = ALLOWED_ORIGINS.includes(origin);

  const response = NextResponse.json({ data: 'hello' });

  if (isAllowed) {
    response.headers.set('Access-Control-Allow-Origin', origin);
    response.headers.set('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    response.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    response.headers.set('Access-Control-Max-Age', '86400');
  }

  return response;
}

// Preflight 요청 처리
export async function OPTIONS(request: Request) {
  const origin = request.headers.get('origin') ?? '';
  const isAllowed = ALLOWED_ORIGINS.includes(origin);

  return new NextResponse(null, {
    status: 204,
    headers: {
      ...(isAllowed && {
        'Access-Control-Allow-Origin': origin,
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Access-Control-Max-Age': '86400',
      }),
    },
  });
}
```

### 8.3 Content Security Policy (CSP)

CSP(*Content Security Policy - 브라우저에게 어떤 소스의 리소스를 로드할 수 있는지 지시하는 HTTP 응답 헤더. XSS 공격 방지에 효과적이다*)는 XSS 공격을 방지하는 가장 강력한 브라우저 보안 메커니즘이다.

```typescript
// next.config.ts — CSP 헤더 설정
import type { NextConfig } from 'next';

const cspHeader = `
  default-src 'self';
  script-src 'self' 'nonce-{NONCE}' https://cdn.example.com;
  style-src 'self' 'unsafe-inline';
  img-src 'self' https: data:;
  font-src 'self' https://fonts.gstatic.com;
  connect-src 'self' https://api.example.com;
  frame-ancestors 'none';
  base-uri 'self';
  form-action 'self';
`.replace(/\n/g, '');

const nextConfig: NextConfig = {
  headers: async () => [
    {
      source: '/(.*)',
      headers: [
        { key: 'Content-Security-Policy', value: cspHeader },
        { key: 'X-Content-Type-Options', value: 'nosniff' },
        { key: 'X-Frame-Options', value: 'DENY' },
        { key: 'X-XSS-Protection', value: '1; mode=block' },
        { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
        { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=()' },
      ],
    },
  ],
};

export default nextConfig;
```

### 8.4 CloudFront Response Headers Policy

Next.js 설정 외에도, CloudFront에서 보안 헤더를 추가할 수 있다. 이 방법은 S3 정적 사이트 호스팅처럼 서버 측에서 헤더를 설정할 수 없는 경우에 유용하다.

```bash
# CloudFront 보안 헤더 정책 생성
aws cloudfront create-response-headers-policy \
  --response-headers-policy-config '{
    "Name": "security-headers-policy",
    "SecurityHeadersConfig": {
      "StrictTransportSecurity": {
        "Override": true,
        "AccessControlMaxAgeSec": 63072000,
        "IncludeSubdomains": true,
        "Preload": true
      },
      "ContentTypeOptions": {
        "Override": true
      },
      "FrameOptions": {
        "Override": true,
        "FrameOption": "DENY"
      },
      "XSSProtection": {
        "Override": true,
        "Protection": true,
        "ModeBlock": true
      },
      "ReferrerPolicy": {
        "Override": true,
        "ReferrerPolicy": "strict-origin-when-cross-origin"
      },
      "ContentSecurityPolicy": {
        "Override": true,
        "ContentSecurityPolicy": "default-src '\''self'\''; script-src '\''self'\''"
      }
    }
  }'
```

```
보안 헤더 적용 흐름:

사용자 → CloudFront → (Response Headers Policy 적용) → 응답에 보안 헤더 추가
                                                        ├── Strict-Transport-Security
                                                        ├── X-Content-Type-Options
                                                        ├── X-Frame-Options
                                                        ├── Content-Security-Policy
                                                        └── Referrer-Policy
```

---

## 9. AWS Config

### 9.1 Config란

AWS Config(*AWS Config - AWS 리소스의 설정 변경을 지속적으로 기록하고, 규정 준수 여부를 자동으로 평가하는 서비스*)는 "누가 언제 무엇을 변경했는가"를 추적한다. 보안 감사와 컴플라이언스에 필수적인 서비스이다.

```
AWS Config의 동작:

┌──────────────────────────────────────────────────┐
│  리소스 변경 감지                                   │
│                                                   │
│  보안 그룹 규칙 변경 ──┐                            │
│  S3 버킷 정책 변경 ────┤                            │
│  IAM 정책 변경 ────────┼──→ AWS Config ──→ 기록     │
│  EC2 설정 변경 ────────┤         │                  │
│  RDS 설정 변경 ────────┘         │                  │
│                                  ↓                 │
│                          ┌───────────────┐         │
│                          │  Config Rules  │         │
│                          │  (규정 준수    │         │
│                          │   자동 평가)   │         │
│                          └───────┬───────┘         │
│                                  │                  │
│                    비준수 → SNS 알림 / 자동 교정     │
└──────────────────────────────────────────────────┘
```

### 9.2 유용한 Config Rules

| Config Rule | 감시 대상 | 설명 |
|------------|----------|------|
| `s3-bucket-public-read-prohibited` | S3 | 퍼블릭 읽기 접근이 열린 버킷 탐지 |
| `restricted-ssh` | EC2 | SSH(22)가 0.0.0.0/0으로 열린 보안 그룹 탐지 |
| `rds-storage-encrypted` | RDS | 스토리지 암호화 미적용 인스턴스 탐지 |
| `iam-root-access-key-check` | IAM | 루트 계정에 액세스 키가 존재하는지 확인 |
| `encrypted-volumes` | EBS | 암호화되지 않은 EBS 볼륨 탐지 |
| `multi-region-cloudtrail-enabled` | CloudTrail | 다중 리전 CloudTrail 활성화 여부 확인 |

```bash
# Config 규칙 생성 (SSH 0.0.0.0/0 차단 감시)
aws configservice put-config-rule \
  --config-rule '{
    "ConfigRuleName": "restricted-ssh",
    "Source": {
      "Owner": "AWS",
      "SourceIdentifier": "INCOMING_SSH_DISABLED"
    },
    "Scope": {
      "ComplianceResourceTypes": ["AWS::EC2::SecurityGroup"]
    }
  }'
```

---

## 10. GuardDuty (위협 탐지)

### 10.1 GuardDuty란

GuardDuty(*GuardDuty - AWS 계정과 워크로드에 대한 지능형 위협 탐지 서비스. 머신러닝과 이상 행동 탐지를 사용하여 악의적인 활동을 식별한다*)는 AWS 환경에서의 비정상적인 활동을 자동으로 감지한다.

```
GuardDuty 데이터 소스:

┌─────────────────────────────────────────────────┐
│  데이터 수집                  분석 및 탐지          │
│                                                  │
│  CloudTrail 이벤트 ───┐                           │
│  VPC Flow Logs ───────┼──→ GuardDuty ──→ Findings│
│  DNS 로그 ────────────┤     (ML 기반)    (위협 목록)│
│  S3 데이터 이벤트 ────┘                           │
│                                                  │
│  탐지 예시:                                       │
│  · 비정상 API 호출 패턴                            │
│  · 알려진 악성 IP와의 통신                         │
│  · 비트코인 채굴 활동                              │
│  · 무차별 대입 공격(Brute Force)                   │
│  · S3 버킷 무단 접근 시도                          │
└─────────────────────────────────────────────────┘
```

```bash
# GuardDuty 활성화 (리전별로 활성화 필요)
aws guardduty create-detector --enable

# 활성 탐지 결과 조회
aws guardduty list-findings \
  --detector-id abc123def456 \
  --finding-criteria '{
    "Criterion": {
      "severity": { "Gte": 7 }
    }
  }'
```

### 10.2 주요 탐지 유형

| 위협 유형 | 설명 | 심각도 |
|----------|------|--------|
| **UnauthorizedAccess:IAMUser/MaliciousIPCaller** | 알려진 악성 IP에서 API 호출 | 높음 |
| **Recon:EC2/PortProbeUnprotectedPort** | EC2의 열린 포트에 대한 스캔 탐지 | 낮음 |
| **CryptoCurrency:EC2/BitcoinTool.B** | EC2에서 비트코인 채굴 활동 탐지 | 높음 |
| **UnauthorizedAccess:S3/TorIPCaller** | Tor 네트워크에서 S3 접근 | 중간 |
| **Trojan:EC2/BlackholeTraffic** | EC2가 블랙홀 IP로 트래픽 전송 | 높음 |

> **실무 팁**: GuardDuty는 **활성화만 하면 자동으로 동작**한다. 별도의 에이전트 설치나 로그 설정이 필요 없다. 30일 무료 평가판이 있으므로, 프로덕션 환경에서는 반드시 활성화하고 CloudWatch Events(EventBridge)와 연동하여 고위험 탐지 시 Slack이나 이메일로 알림을 받도록 설정하라.

---

## 11. 프로덕션 보안 체크리스트

### 11.1 IAM / 계정 보안

- [ ] 루트 계정에 MFA 활성화
- [ ] 루트 계정의 액세스 키 삭제
- [ ] IAM 사용자별 최소 권한 정책 적용
- [ ] 프로그래밍 접근에는 IAM 역할 사용 (장기 액세스 키 지양)
- [ ] IAM 비밀번호 정책 설정 (최소 길이, 복잡도, 만료 주기)
- [ ] 사용하지 않는 IAM 사용자/역할 정리

### 11.2 네트워크 보안

- [ ] 데이터베이스, 캐시는 프라이빗 서브넷에 배치
- [ ] 보안 그룹에서 SSH(22)를 0.0.0.0/0으로 열지 않음
- [ ] 보안 그룹 간 참조를 사용하여 계층별 접근 제어
- [ ] 필요한 경우 NACL로 추가 방어 계층 구성
- [ ] VPC Flow Logs 활성화

### 11.3 데이터 보호

- [ ] S3 버킷 퍼블릭 접근 차단 (Block Public Access)
- [ ] S3, EBS, RDS 암호화 활성화
- [ ] Secrets Manager로 비밀 정보 관리 (코드에 하드코딩 금지)
- [ ] HTTPS 전용 통신 (ACM 인증서 + HTTP→HTTPS 리다이렉트)
- [ ] CloudFront에 최소 TLS 1.2 설정

### 11.4 애플리케이션 보안

- [ ] WAF 적용 (CloudFront 또는 ALB)
- [ ] AWS Managed Rules로 OWASP Top 10 방어
- [ ] Rate Limiting으로 DDoS/무차별 대입 방어
- [ ] CORS 설정 (허용 도메인 명시)
- [ ] 보안 헤더 설정 (CSP, HSTS, X-Frame-Options 등)
- [ ] `NEXT_PUBLIC_*` 환경 변수에 민감 정보 미포함 확인

### 11.5 모니터링 / 감사

- [ ] CloudTrail 활성화 (모든 리전)
- [ ] GuardDuty 활성화
- [ ] AWS Config Rules로 설정 규정 준수 감시
- [ ] CloudWatch 알람으로 비정상 패턴 감지
- [ ] 고위험 이벤트 발생 시 알림(Slack, 이메일) 설정

---

## 자주 하는 실수

| 실수 | 설명 | 올바른 접근 |
|------|------|------------|
| **보안 그룹에 0.0.0.0/0 SSH 허용** | 전 세계에서 SSH 접속 시도가 들어온다 | 특정 IP만 허용하거나 SSM Session Manager 사용 |
| **S3 버킷 퍼블릭 접근 방치** | 데이터 유출 사고의 가장 흔한 원인 | Block Public Access 활성화, OAC 사용 |
| **환경 변수에 DB 비밀번호 저장** | AWS 콘솔에서 평문 노출, 자동 교체 불가 | Secrets Manager에 저장, Lambda에서 SDK로 조회 |
| **NEXT_PUBLIC_에 시크릿 키 포함** | 브라우저 번들에 포함되어 누구나 볼 수 있다 | 서버 전용 환경 변수로 분리, API Route에서만 접근 |
| **CloudFront용 인증서를 서울 리전에서 발급** | CloudFront에 연결할 수 없다 | CloudFront용은 반드시 us-east-1에서 발급 |
| **WAF 규칙을 바로 Block 모드로 적용** | 정상 요청이 오탐으로 차단될 수 있다 | 먼저 Count 모드로 모니터링 후 Block 전환 |
| **RDS 인스턴스 생성 후 암호화 시도** | 기존 인스턴스에 암호화를 추가할 수 없다 | 생성 시 암호화 활성화, 또는 스냅샷 → 암호화 복원 |
| **모든 IAM 사용자에게 Admin 권한** | 한 명의 실수가 전체 인프라에 영향 | 최소 권한 원칙, 역할별 정책 분리 |

---

## AWS CLI 레퍼런스

| 명령어 | 설명 |
|--------|------|
| `aws wafv2 create-web-acl --name NAME --scope SCOPE --default-action ACTION` | WAF 웹 ACL 생성 |
| `aws wafv2 list-web-acls --scope SCOPE` | 웹 ACL 목록 조회 |
| `aws wafv2 get-web-acl --name NAME --scope SCOPE --id ID` | 웹 ACL 상세 조회 |
| `aws shield describe-protection --resource-arn ARN` | Shield 보호 상태 확인 |
| `aws secretsmanager create-secret --name NAME --secret-string JSON` | 비밀 생성 |
| `aws secretsmanager get-secret-value --secret-id NAME` | 비밀 조회 |
| `aws secretsmanager rotate-secret --secret-id NAME --rotation-lambda-arn ARN` | 비밀 자동 교체 설정 |
| `aws kms create-key --description DESC` | KMS 키 생성 |
| `aws kms generate-data-key --key-id KEY --key-spec AES_256` | 데이터 키 생성 |
| `aws acm request-certificate --domain-name DOMAIN --validation-method DNS` | SSL/TLS 인증서 요청 |
| `aws acm list-certificates` | 인증서 목록 조회 |
| `aws configservice put-config-rule --config-rule JSON` | Config 규칙 생성 |
| `aws guardduty create-detector --enable` | GuardDuty 활성화 |
| `aws guardduty list-findings --detector-id ID` | GuardDuty 탐지 결과 조회 |
| `aws ec2 create-network-acl-entry --network-acl-id ID --rule-number N` | NACL 규칙 추가 |

---

## 요약

- **공동 책임 모델**: AWS는 "클라우드의" 보안을, 고객은 "클라우드 안의" 보안을 책임진다. 관리형 서비스를 사용해도 데이터 암호화, 접근 제어, 네트워크 설정은 고객의 몫이다.
- **보안 그룹**은 인스턴스 수준의 Stateful 방화벽이고, **네트워크 ACL**은 서브넷 수준의 Stateless 방화벽이다. 보안 그룹을 주로 사용하고, NACL은 특정 IP 차단 등 보조 역할로 활용한다.
- **WAF**는 Layer 7 공격(SQL 인젝션, XSS, DDoS)을 방어한다. AWS Managed Rules를 사용하면 별도의 규칙 작성 없이 일반적인 공격을 차단할 수 있다. CloudFront + WAF 조합이 가장 효과적이다.
- **AWS Shield Standard**는 무료로 Layer 3/4 DDoS 공격을 방어한다. Shield Advanced(월 $3,000)는 대규모 서비스에서만 검토한다.
- **Secrets Manager**로 DB 비밀번호, API 키 등 민감 정보를 관리한다. 자동 교체(Rotation)를 지원하며, Lambda에서 SDK로 조회하여 사용한다.
- **KMS**는 AWS 전체의 암호화 키를 관리한다. S3, EBS, RDS 등의 암호화는 `--encrypted` 플래그만 설정하면 내부적으로 봉투 암호화가 자동 적용된다.
- **ACM**으로 SSL/TLS 인증서를 무료로 발급받고 자동 갱신한다. CloudFront용은 반드시 us-east-1에서 발급해야 한다.
- **프론트엔드 보안**: `NEXT_PUBLIC_*`에 민감 정보를 넣지 않고, CORS를 올바르게 설정하며, CSP 등 보안 헤더를 적용한다.
- **AWS Config**으로 리소스 설정 변경을 추적하고, **GuardDuty**로 위협을 자동 탐지한다.
- **프로덕션 보안 체크리스트**를 배포 전에 반드시 점검하라: IAM 최소 권한, 네트워크 격리, 데이터 암호화, WAF/보안 헤더 적용, 모니터링/감사 활성화.

---

이것으로 AWS 완전 가이드의 모든 챕터를 마친다. Chapter 1의 클라우드 컴퓨팅 기초부터 이 Chapter 16의 보안 심화까지, AWS의 핵심 서비스를 체계적으로 다루었다. 이 가이드가 AWS 인프라를 설계하고 운영하는 데 실질적인 참고 자료가 되기를 바란다.