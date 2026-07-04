# Chapter 4: VPC - 가상 네트워크 설계: Virtual Private Cloud

## 핵심 질문

AWS 리소스가 배치되는 네트워크 환경은 어떻게 설계하는가? VPC, 서브넷, 라우팅, 게이트웨이의 관계를 이해하고, 퍼블릭/프라이빗 리소스를 올바르게 분리하려면 어떻게 해야 하는가?

---

## 1. VPC란

### 1.1 정의

VPC(*Virtual Private Cloud - AWS 클라우드 내에서 논리적으로 격리된 가상 네트워크. AWS 리소스를 배치할 수 있는 자신만의 네트워크 공간*)는 AWS에서 제공하는 가상 네트워크이다. 물리적 데이터센터에서 네트워크 장비로 구축하는 것을 소프트웨어로 정의한 것이라고 생각하면 된다.

EC2 인스턴스, RDS 데이터베이스, Lambda 함수(VPC 연결 시), ECS 컨테이너 등 대부분의 AWS 리소스는 VPC 안에 배치된다.

### 1.2 VPC의 핵심 구성 요소

```
VPC 아키텍처 개요:

인터넷
  │
  ↓
┌──────────────── VPC (10.0.0.0/16) ────────────────────┐
│  ┌────────────── Internet Gateway ──────────────────┐  │
│  └──────────────────────┬───────────────────────────┘  │
│                         │                               │
│  ┌─── 퍼블릭 서브넷 ────┼──── 퍼블릭 서브넷 ────────┐   │
│  │  (10.0.1.0/24)       │    (10.0.2.0/24)         │   │
│  │  AZ-a                │    AZ-b                   │   │
│  │  ┌────────┐          │    ┌────────┐             │   │
│  │  │  EC2   │          │    │  EC2   │             │   │
│  │  │(웹서버)│          │    │(웹서버)│             │   │
│  │  └────────┘          │    └────────┘             │   │
│  └──────────────────────┼───────────────────────────┘   │
│                         │                               │
│  ┌─── 프라이빗 서브넷 ──┼──── 프라이빗 서브넷 ──────┐   │
│  │  (10.0.3.0/24)       │    (10.0.4.0/24)         │   │
│  │  AZ-a                │    AZ-b                   │   │
│  │  ┌────────┐   ┌─────┤    ┌────────┐             │   │
│  │  │  RDS   │   │ NAT │    │  RDS   │             │   │
│  │  │ (DB)   │   │  GW │    │(복제본)│             │   │
│  │  └────────┘   └─────┘    └────────┘             │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

| 구성 요소 | 역할 |
|----------|------|
| **VPC** | 전체 네트워크 공간 (IP 주소 범위 정의) |
| **서브넷** | VPC를 분할한 하위 네트워크 (AZ별로 배치) |
| **Internet Gateway** | VPC와 인터넷 간의 관문 |
| **NAT Gateway** | 프라이빗 서브넷에서 인터넷으로 나가는 관문 (인바운드 차단) |
| **라우팅 테이블** | 네트워크 트래픽의 경로를 결정하는 규칙 |
| **보안 그룹** | 인스턴스 수준의 방화벽 (Stateful) |
| **네트워크 ACL** | 서브넷 수준의 방화벽 (Stateless) |

---

## 2. CIDR과 IP 주소 설계

### 2.1 CIDR 표기법

CIDR(*Classless Inter-Domain Routing - IP 주소 범위를 표현하는 방법. 예: 10.0.0.0/16은 10.0.0.0부터 10.0.255.255까지의 범위*)은 VPC와 서브넷의 IP 주소 범위를 정의하는 표기법이다.

```
CIDR 표기법:  10.0.0.0/16
             ──────── ──
             네트워크   서브넷 마스크 (고정 비트 수)
             주소

/16 → 앞의 16비트가 고정, 뒤의 16비트가 호스트용
    → 2^16 = 65,536개의 IP 주소 사용 가능

/24 → 앞의 24비트가 고정, 뒤의 8비트가 호스트용
    → 2^8 = 256개의 IP 주소 사용 가능
```

**CIDR 크기별 IP 개수:**

| CIDR | 사용 가능 IP | 설명 |
|------|-------------|------|
| /16 | 65,536 | VPC 기본 크기 |
| /20 | 4,096 | 큰 서브넷 |
| /24 | 256 | 일반적인 서브넷 크기 |
| /28 | 16 | 최소 서브넷 크기 (AWS 최소) |

### 2.2 VPC와 서브넷 설계 예시

```
VPC: 10.0.0.0/16 (65,536개 IP)
│
├── 퍼블릭 서브넷 AZ-a: 10.0.1.0/24 (256개 IP)
├── 퍼블릭 서브넷 AZ-b: 10.0.2.0/24 (256개 IP)
├── 프라이빗 서브넷 AZ-a: 10.0.3.0/24 (256개 IP)
├── 프라이빗 서브넷 AZ-b: 10.0.4.0/24 (256개 IP)
├── DB 서브넷 AZ-a: 10.0.5.0/24 (256개 IP)
└── DB 서브넷 AZ-b: 10.0.6.0/24 (256개 IP)
```

> **실무 팁**: VPC의 CIDR은 **생성 후 축소할 수 없다** (확장은 가능). 처음부터 넉넉한 범위를 잡는 것이 좋다. `/16`이면 대부분의 프로젝트에 충분하다. 또한 온프레미스 네트워크나 다른 VPC와 연결(VPC Peering)할 때 **IP 범위가 겹치면 안 되므로**, 10.0.0.0/16, 10.1.0.0/16, 10.2.0.0/16처럼 미리 계획해두는 것이 좋다.

---

## 3. 서브넷 (Subnet)

### 3.1 퍼블릭 서브넷 vs 프라이빗 서브넷

서브넷(*Subnet - VPC의 IP 주소 범위를 분할한 하위 네트워크. 각 서브넷은 하나의 AZ에 존재한다*)은 퍼블릭과 프라이빗으로 구분되는데, 이 구분은 **라우팅 테이블에 Internet Gateway가 있는지 여부**로 결정된다.

| 유형 | Internet Gateway 경로 | 인터넷 접근 | 적합한 리소스 |
|------|---------------------|------------|-------------|
| **퍼블릭** | 있음 | 양방향 가능 | 웹 서버, 로드밸런서, NAT GW |
| **프라이빗** | 없음 | 외부→내부 불가 | DB, 애플리케이션 서버, 캐시 |

### 3.2 서브넷 생성

```bash
# VPC 생성
aws ec2 create-vpc --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=my-vpc}]'

# 퍼블릭 서브넷 생성 (AZ-a)
aws ec2 create-subnet \
  --vpc-id vpc-0abc123 \
  --cidr-block 10.0.1.0/24 \
  --availability-zone ap-northeast-2a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=public-a}]'

# 프라이빗 서브넷 생성 (AZ-a)
aws ec2 create-subnet \
  --vpc-id vpc-0abc123 \
  --cidr-block 10.0.3.0/24 \
  --availability-zone ap-northeast-2a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=private-a}]'
```

> **핵심 통찰**: 서브넷을 설계할 때 가장 중요한 원칙은 **"인터넷에 노출되어야 하는 것과 그렇지 않은 것을 분리하라"**이다. 데이터베이스, 캐시 서버, 내부 API 서버는 인터넷에서 직접 접근할 수 없는 프라이빗 서브넷에 배치한다. 웹 서버나 로드밸런서만 퍼블릭 서브넷에 둔다.

---

## 4. 게이트웨이와 라우팅

### 4.1 Internet Gateway (IGW)

Internet Gateway(*Internet Gateway - VPC와 인터넷 사이의 양방향 통신을 가능하게 하는 관문*)는 VPC가 인터넷과 통신하기 위한 필수 구성 요소이다. VPC 당 하나만 연결할 수 있다.

```bash
# Internet Gateway 생성 및 VPC에 연결
aws ec2 create-internet-gateway \
  --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=my-igw}]'

aws ec2 attach-internet-gateway \
  --internet-gateway-id igw-0abc123 \
  --vpc-id vpc-0abc123
```

### 4.2 NAT Gateway

NAT Gateway(*NAT Gateway - 프라이빗 서브넷의 리소스가 인터넷으로 나가는 트래픽을 허용하면서, 인터넷에서 프라이빗 서브넷으로 들어오는 트래픽은 차단하는 서비스*)는 프라이빗 서브넷의 리소스가 인터넷에 접근해야 할 때 사용한다.

**왜 필요한가?**

프라이빗 서브넷의 EC2 인스턴스도 소프트웨어 업데이트(`apt update`, `npm install`)를 위해 인터넷에 접근해야 할 수 있다. NAT Gateway를 통해 **아웃바운드만 허용**하고 인바운드는 차단한다.

```bash
# Elastic IP 할당 (NAT Gateway에 필요)
aws ec2 allocate-address --domain vpc

# NAT Gateway 생성 (퍼블릭 서브넷에 배치)
aws ec2 create-nat-gateway \
  --subnet-id subnet-0abc123 \
  --allocation-id eipalloc-0abc123 \
  --tag-specifications 'ResourceType=natgateway,Tags=[{Key=Name,Value=my-nat}]'
```

> **비용 주의**: NAT Gateway는 **시간당 약 $0.059(서울 리전)**이 과금되며, 처리하는 데이터 양에 따라 추가 비용이 발생한다. 월 약 $43+α로, Free Tier에 포함되지 않는다. 학습 환경에서는 사용 후 반드시 삭제하라. 대안으로 **NAT Instance**(EC2 기반)를 사용하면 t3.micro Free Tier로 비용을 줄일 수 있다.

### 4.3 라우팅 테이블 (Route Table)

라우팅 테이블(*Route Table - 네트워크 트래픽이 어디로 향할지 결정하는 규칙 집합*)은 서브넷의 트래픽 경로를 결정한다.

**퍼블릭 서브넷의 라우팅 테이블:**

| Destination | Target | 설명 |
|------------|--------|------|
| 10.0.0.0/16 | local | VPC 내부 트래픽은 로컬에서 처리 |
| 0.0.0.0/0 | igw-0abc123 | 나머지 모든 트래픽은 Internet Gateway로 |

**프라이빗 서브넷의 라우팅 테이블:**

| Destination | Target | 설명 |
|------------|--------|------|
| 10.0.0.0/16 | local | VPC 내부 트래픽은 로컬에서 처리 |
| 0.0.0.0/0 | nat-0abc123 | 나머지 모든 트래픽은 NAT Gateway로 |

```bash
# 라우팅 테이블 생성
aws ec2 create-route-table --vpc-id vpc-0abc123

# Internet Gateway 경로 추가 (퍼블릭 서브넷용)
aws ec2 create-route \
  --route-table-id rtb-0abc123 \
  --destination-cidr-block 0.0.0.0/0 \
  --gateway-id igw-0abc123

# 라우팅 테이블을 서브넷에 연결
aws ec2 associate-route-table \
  --route-table-id rtb-0abc123 \
  --subnet-id subnet-0abc123
```

---

## 5. 보안 그룹 (Security Group)

### 5.1 보안 그룹이란

보안 그룹(*Security Group - EC2 인스턴스 등 리소스 수준에서 동작하는 가상 방화벽. 인바운드와 아웃바운드 트래픽을 규칙으로 제어한다*)은 인스턴스에 대한 트래픽을 제어하는 **Stateful** 방화벽이다.

**Stateful의 의미**: 인바운드로 허용된 요청에 대한 응답은 자동으로 아웃바운드가 허용된다. 아웃바운드 규칙을 별도로 설정할 필요가 없다.

### 5.2 규칙 설정

```bash
# 보안 그룹 생성
aws ec2 create-security-group \
  --group-name web-server-sg \
  --description "Security group for web servers" \
  --vpc-id vpc-0abc123

# 인바운드 규칙 추가
# HTTP (80) 허용 - 모든 IP에서
aws ec2 authorize-security-group-ingress \
  --group-id sg-0abc123 \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

# HTTPS (443) 허용 - 모든 IP에서
aws ec2 authorize-security-group-ingress \
  --group-id sg-0abc123 \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# SSH (22) 허용 - 내 IP에서만
aws ec2 authorize-security-group-ingress \
  --group-id sg-0abc123 \
  --protocol tcp \
  --port 22 \
  --cidr 203.0.113.50/32
```

### 5.3 보안 그룹 간 참조

보안 그룹의 강력한 기능 중 하나는 **다른 보안 그룹을 소스로 지정**할 수 있다는 것이다. IP 대신 보안 그룹 ID를 지정하면, 해당 보안 그룹이 부여된 모든 리소스의 트래픽을 허용한다.

```bash
# DB 보안 그룹: 웹 서버 보안 그룹에서 오는 트래픽만 허용
aws ec2 authorize-security-group-ingress \
  --group-id sg-db123 \
  --protocol tcp \
  --port 5432 \
  --source-group sg-web123
```

```
보안 그룹 체이닝:

인터넷 ──→ [ALB SG] ──→ [Web Server SG] ──→ [DB SG]
           80, 443       ALB SG에서만        Web SG에서만
           모든 IP       8080 허용            5432 허용
```

### 5.4 보안 그룹 vs 네트워크 ACL

| 특성 | 보안 그룹 | 네트워크 ACL |
|------|----------|-------------|
| **적용 수준** | 인스턴스 (ENI) | 서브넷 |
| **상태** | Stateful (응답 자동 허용) | Stateless (인바운드/아웃바운드 별도 설정) |
| **규칙 유형** | 허용만 가능 | 허용 + 거부 가능 |
| **규칙 평가** | 모든 규칙 평가 후 허용 | 번호 순서대로 평가, 첫 매치에서 결정 |
| **기본 동작** | 모든 아웃바운드 허용, 인바운드 거부 | 모든 트래픽 허용 (기본 ACL) |

> **실무 팁**: 대부분의 경우 **보안 그룹만으로 충분**하다. 네트워크 ACL은 추가적인 방어 계층이 필요하거나, 특정 IP를 서브넷 수준에서 차단해야 할 때 사용한다. 보안 그룹을 주 방화벽으로, 네트워크 ACL을 보조 방화벽으로 사용하라.

---

## 6. 실전 VPC 설계

### 6.1 일반적인 3-Tier 아키텍처

```
인터넷
  │
  ↓
┌────────────── VPC (10.0.0.0/16) ──────────────────────┐
│                                                        │
│  [퍼블릭 서브넷 계층] - 로드밸런서                        │
│  ┌──────────────┐  ┌──────────────┐                    │
│  │ ALB (AZ-a)   │  │ ALB (AZ-b)   │                    │
│  │ 10.0.1.0/24  │  │ 10.0.2.0/24  │                    │
│  └──────┬───────┘  └──────┬───────┘                    │
│         │                  │                            │
│  [프라이빗 서브넷 계층] - 애플리케이션 서버                │
│  ┌──────┴───────┐  ┌──────┴───────┐                    │
│  │ EC2/ECS(AZ-a)│  │ EC2/ECS(AZ-b)│                    │
│  │ 10.0.3.0/24  │  │ 10.0.4.0/24  │                    │
│  └──────┬───────┘  └──────┬───────┘                    │
│         │                  │                            │
│  [DB 서브넷 계층] - 데이터베이스                          │
│  ┌──────┴───────┐  ┌──────┴───────┐                    │
│  │ RDS (AZ-a)   │  │ RDS (AZ-b)   │                    │
│  │ 10.0.5.0/24  │  │ 10.0.6.0/24  │                    │
│  └──────────────┘  └──────────────┘                    │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### 6.2 프론트엔드 정적 배포 아키텍처

프론트엔드 애플리케이션(React, Next.js 정적 빌드)은 S3 + CloudFront로 배포할 때 VPC가 필요하지 않다. S3와 CloudFront는 VPC 외부에서 동작하는 글로벌 서비스이다.

```
사용자 → CloudFront(CDN) → S3(정적 파일)
                              │
         ※ S3와 CloudFront는 VPC 밖에서 동작
         ※ VPC가 필요한 것은 백엔드 서버, DB 등
```

다만 Next.js SSR 서버를 ECS Fargate로 운영하거나, API 서버가 있다면 VPC가 필요하다.

---

## 자주 하는 실수

| 실수 | 설명 | 올바른 접근 |
|------|------|------------|
| **SSH(22)를 0.0.0.0/0으로 열어둠** | 전 세계에서 SSH 접속 시도가 들어옴 | 내 IP만 허용하거나 SSM Session Manager 사용 |
| **모든 리소스를 퍼블릭 서브넷에 배치** | DB가 인터넷에 노출됨 | DB, 캐시는 반드시 프라이빗 서브넷 |
| **NAT Gateway를 방치** | 월 $43+ 비용이 계속 발생 | 학습 후 반드시 삭제, 프로덕션은 비용 감안 |
| **VPC CIDR을 너무 작게 설정** | 서브넷을 추가할 IP가 부족 | /16으로 넉넉하게 시작 |
| **단일 AZ에만 서브넷 생성** | AZ 장애 시 서비스 전체 다운 | 최소 2개 AZ에 서브넷 배치 |

---

## AWS CLI 레퍼런스

| 명령어 | 설명 |
|--------|------|
| `aws ec2 create-vpc --cidr-block CIDR` | VPC 생성 |
| `aws ec2 create-subnet --vpc-id VPC --cidr-block CIDR --availability-zone AZ` | 서브넷 생성 |
| `aws ec2 create-internet-gateway` | Internet Gateway 생성 |
| `aws ec2 attach-internet-gateway --igw-id IGW --vpc-id VPC` | IGW를 VPC에 연결 |
| `aws ec2 create-nat-gateway --subnet-id SUBNET --allocation-id EIP` | NAT Gateway 생성 |
| `aws ec2 create-route-table --vpc-id VPC` | 라우팅 테이블 생성 |
| `aws ec2 create-route --route-table-id RTB --destination-cidr-block 0.0.0.0/0 --gateway-id IGW` | 라우트 추가 |
| `aws ec2 create-security-group --group-name NAME --vpc-id VPC` | 보안 그룹 생성 |
| `aws ec2 authorize-security-group-ingress --group-id SG --protocol tcp --port PORT --cidr CIDR` | 인바운드 규칙 추가 |
| `aws ec2 describe-vpcs` | VPC 목록 조회 |
| `aws ec2 describe-subnets --filters "Name=vpc-id,Values=VPC_ID"` | 서브넷 목록 조회 |

---

## 요약

- **VPC**는 AWS 리소스를 배치하는 논리적으로 격리된 가상 네트워크이다.
- **CIDR** 표기법으로 IP 주소 범위를 정의한다. VPC는 `/16`, 서브넷은 `/24`가 일반적이다.
- **서브넷**은 퍼블릭과 프라이빗으로 구분되며, 이 구분은 라우팅 테이블에 Internet Gateway 경로가 있는지로 결정된다.
- **Internet Gateway**는 VPC와 인터넷의 양방향 통신을 가능하게 한다.
- **NAT Gateway**는 프라이빗 서브넷에서 인터넷으로 나가는 아웃바운드만 허용한다 (비용 주의).
- **보안 그룹**은 인스턴스 수준의 Stateful 방화벽이다. 보안 그룹 간 참조를 통해 계층별 접근 제어가 가능하다.
- 데이터베이스와 내부 서버는 **프라이빗 서브넷**에, 로드밸런서만 **퍼블릭 서브넷**에 배치한다.
- S3 + CloudFront를 이용한 정적 사이트 배포에는 VPC가 필요하지 않다.
- 최소 **2개 AZ에 서브넷을 분산** 배치하여 고가용성을 확보한다.
