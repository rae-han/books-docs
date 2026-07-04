# Chapter 6: EC2 - 가상 서버: Elastic Compute Cloud

## 핵심 질문

AWS에서 가상 서버를 어떻게 생성하고 관리하는가? 인스턴스 타입은 어떻게 선택하며, 보안 그룹, EBS, Auto Scaling, 로드밸런서를 조합하여 안정적이고 확장 가능한 서버 인프라를 구축하려면 어떻게 해야 하는가?

---

## 1. EC2란

### 1.1 정의

EC2(*Elastic Compute Cloud - AWS에서 제공하는 가상 서버 서비스. 필요한 만큼 서버를 생성하고, 사용한 시간만큼만 비용을 지불한다*)는 AWS의 가장 기본적인 컴퓨팅 서비스이다. Chapter 1에서 다룬 IaaS의 대표 서비스로, 물리 서버를 구매하고 설치하는 대신 몇 분 안에 가상 서버를 생성할 수 있다.

EC2 인스턴스(*Instance - EC2에서 실행 중인 하나의 가상 서버*)는 본질적으로 AWS 데이터센터의 물리 서버 위에서 동작하는 가상 머신(VM)이다.

### 1.2 EC2의 핵심 구성 요소

```
EC2 인스턴스 구조:

┌─────────────── EC2 인스턴스 ───────────────────┐
│                                                 │
│  ┌─────────────┐  ┌──────────────────────────┐  │
│  │   AMI       │  │  인스턴스 타입             │  │
│  │ (OS 이미지)  │  │  (CPU, 메모리 스펙)       │  │
│  └─────────────┘  └──────────────────────────┘  │
│                                                 │
│  ┌─────────────┐  ┌──────────────────────────┐  │
│  │  키 페어     │  │  보안 그룹                │  │
│  │ (SSH 접속)   │  │  (방화벽 규칙)            │  │
│  └─────────────┘  └──────────────────────────┘  │
│                                                 │
│  ┌─────────────┐  ┌──────────────────────────┐  │
│  │  EBS        │  │  Elastic IP (선택)        │  │
│  │ (디스크)     │  │  (고정 IP 주소)           │  │
│  └─────────────┘  └──────────────────────────┘  │
│                                                 │
│  VPC / 서브넷 (Chapter 4)                        │
└─────────────────────────────────────────────────┘
```

| 구성 요소 | 역할 |
|----------|------|
| **AMI** | OS와 소프트웨어가 사전 구성된 템플릿 (Amazon Linux, Ubuntu 등) |
| **인스턴스 타입** | CPU, 메모리, 네트워크 성능을 결정하는 하드웨어 스펙 |
| **키 페어** | SSH 접속에 사용하는 공개키/개인키 쌍 |
| **보안 그룹** | 인바운드/아웃바운드 트래픽을 제어하는 방화벽 (Chapter 4 복습) |
| **EBS** | 인스턴스에 연결되는 블록 스토리지 (디스크) |
| **Elastic IP** | 인스턴스에 연결할 수 있는 고정 퍼블릭 IP 주소 |

---

## 2. 인스턴스 타입과 패밀리

### 2.1 이름 규칙

EC2 인스턴스 타입의 이름은 체계적인 규칙을 따른다. 이 규칙을 이해하면 수십 가지 타입 중에서 적절한 것을 빠르게 선택할 수 있다.

```
인스턴스 타입 이름 규칙:

  t3.micro
  │ │ └──── 크기 (nano, micro, small, medium, large, xlarge, 2xlarge ...)
  │ └───── 세대 (숫자가 클수록 최신, 성능/비용 효율이 더 좋다)
  └────── 패밀리 (용도별 분류: t=범용 버스트, m=범용, c=컴퓨팅, r=메모리)

  c5.2xlarge
  │ │  └──── 크기 (2xlarge = xlarge의 2배 스펙)
  │ └───── 세대 (5세대)
  └────── 패밀리 (c = Compute Optimized)

  t4g.medium
  │ │└───── 프로세서 (g = Graviton ARM 프로세서)
  │ └───── 세대 (4세대)
  └────── 패밀리 (t = 범용 버스트)
```

### 2.2 주요 인스턴스 패밀리

| 패밀리 | 용도 | 특징 | 사용 사례 |
|--------|------|------|----------|
| **t3/t4g** | 범용 (버스트) | CPU 크레딧 기반, 평소 낮은 사용률 + 간헐적 부하에 최적 | 개발/테스트 서버, 소규모 웹 서버, 마이크로서비스 |
| **m5/m6i** | 범용 (고정) | CPU와 메모리의 균형 잡힌 성능, 일정한 워크로드에 적합 | 중간 규모 애플리케이션 서버, 백엔드 API 서버 |
| **c5/c6i** | 컴퓨팅 최적화 | 높은 CPU 성능, CPU 대비 메모리 비율이 낮음 | 배치 처리, 미디어 인코딩, 과학 계산, 게임 서버 |
| **r5/r6i** | 메모리 최적화 | 대용량 메모리, 메모리 대비 CPU 비율이 낮음 | 인메모리 캐시, 실시간 분석, 대용량 데이터 처리 |
| **g5** | GPU 인스턴스 | NVIDIA GPU 탑재 | 머신러닝 추론, 그래픽 렌더링 |

### 2.3 버스트 인스턴스 (t 패밀리) 이해하기

t 패밀리는 **CPU 크레딧(*CPU Credit - t 인스턴스가 베이스라인 이상으로 CPU를 사용할 수 있는 "쿠폰". 평소에 CPU를 적게 쓰면 크레딧이 쌓이고, 부하가 올 때 소비한다*) 시스템**을 사용한다.

```
t3.micro의 CPU 크레딧 동작:

베이스라인: 10% CPU 사용률

  CPU 사용률
  100% ┤                    ┌─── 크레딧 소비 (버스트)
       │                    │
       │              ┌─────┤
   50% ┤              │     │
       │              │     │
       │    크레딧     │     │     크레딧
   10% ├────축적───────┤     ├─────축적──────
       │              │     │
    0% └──────────────┴─────┴──────────────→ 시간
```

- **베이스라인 이하**: CPU 크레딧이 축적된다
- **베이스라인 이상**: 축적된 크레딧을 소비하며 버스트한다
- **크레딧 소진**: CPU가 베이스라인으로 강제 제한된다 (성능 급감)

| 인스턴스 타입 | vCPU | 메모리 | 베이스라인 | 시간당 비용(서울) |
|-------------|------|--------|----------|-----------------|
| t3.nano | 2 | 0.5 GiB | 5% | ~$0.0068 |
| t3.micro | 2 | 1 GiB | 10% | ~$0.0136 |
| t3.small | 2 | 2 GiB | 20% | ~$0.0272 |
| t3.medium | 2 | 4 GiB | 20% | ~$0.0544 |
| t3.large | 2 | 8 GiB | 30% | ~$0.1088 |

> **핵심 통찰**: 대부분의 웹 서버는 평소 CPU 사용률이 10~20%이고, 요청이 몰릴 때만 잠깐 올라간다. 이런 패턴에는 **t3/t4g 버스트 인스턴스가 가장 비용 효율적**이다. 반면 CPU를 지속적으로 70% 이상 사용하는 워크로드(배치 처리, 미디어 인코딩 등)에서는 크레딧이 금방 소진되므로 m5나 c5 같은 고정 성능 인스턴스가 적합하다.

### 2.4 Graviton (ARM) 인스턴스

AWS가 자체 설계한 **Graviton** 프로세서 기반의 인스턴스(이름에 `g`가 붙는다: t4**g**, m6**g**, c6**g** 등)는 동일 스펙의 Intel/AMD 인스턴스 대비 **최대 20% 저렴하면서 성능도 비슷하거나 더 좋다.**

```bash
# Graviton 인스턴스 예시
# t4g.micro: ARM 기반, t3.micro보다 ~20% 저렴
# m6g.large: ARM 기반, m5.large보다 ~20% 저렴
```

Node.js는 ARM을 완벽하게 지원하므로, Node.js/Next.js 서버를 EC2에서 실행한다면 Graviton 인스턴스를 적극 고려하라.

> **실무 팁**: 새 프로젝트에서 인스턴스 타입을 선택할 때는 **t4g.micro(Free Tier 해당) → t4g.small → t4g.medium** 순서로 시작하라. Graviton은 가격 대비 성능이 가장 뛰어나다. CPU 사용률이 지속적으로 베이스라인을 넘긴다면 그때 m6g나 c6g로 전환하면 된다.

---

## 3. AMI (Amazon Machine Image)

### 3.1 AMI란

AMI(*Amazon Machine Image - EC2 인스턴스를 시작하기 위한 템플릿. OS, 사전 설치된 소프트웨어, 설정을 포함한다*)는 인스턴스의 "틀"이다. 어떤 OS를 사용할지, 어떤 소프트웨어가 사전 설치되어 있을지를 결정한다.

### 3.2 주요 AMI 비교

| AMI | 기반 | 패키지 관리자 | 특징 |
|-----|------|-------------|------|
| **Amazon Linux 2023** | Fedora 기반 | `dnf` | AWS 서비스와 최적 통합, AWS CLI 사전 설치 |
| **Ubuntu 22.04/24.04** | Debian 기반 | `apt` | 커뮤니티 자료 풍부, 개발자 친숙 |
| **Windows Server** | Windows | - | .NET 워크로드, 추가 라이선스 비용 |
| **커스텀 AMI** | 사용자 정의 | - | Node.js, 앱 등을 사전 설치하여 시작 시간 단축 |

```bash
# 최신 Amazon Linux 2023 AMI ID 조회
aws ec2 describe-images \
  --owners amazon \
  --filters "Name=name,Values=al2023-ami-2023*-x86_64" \
  --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
  --output text

# 최신 Ubuntu 24.04 AMI ID 조회
aws ec2 describe-images \
  --owners 099720109477 \
  --filters "Name=name,Values=ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*" \
  --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
  --output text
```

### 3.3 커스텀 AMI 만들기

기본 AMI에 Node.js, PM2, 앱 코드 등을 설치한 후 **커스텀 AMI**로 저장하면, 이후 새 인스턴스를 시작할 때 설치 과정을 생략할 수 있다. Auto Scaling에서 특히 유용하다.

```bash
# 실행 중인 인스턴스에서 AMI 생성
aws ec2 create-image \
  --instance-id i-0abc123def456 \
  --name "nodejs-app-v1.0" \
  --description "Node.js 20 + PM2 + app deployed"
```

> **실무 팁**: 커스텀 AMI를 만들 때는 **민감한 정보(SSH 키, 환경 변수, 로그 파일 등)를 반드시 제거**한 후 이미지를 생성하라. AMI를 공유하거나 다른 계정에서 사용할 때 보안 문제가 발생할 수 있다.

---

## 4. 키 페어와 접속

### 4.1 키 페어 (Key Pair)

키 페어(*Key Pair - SSH 접속에 사용하는 공개키/개인키 쌍. 공개키는 인스턴스에, 개인키는 로컬에 보관한다*)를 사용하면 비밀번호 없이 안전하게 SSH로 인스턴스에 접속할 수 있다.

```bash
# 키 페어 생성
aws ec2 create-key-pair \
  --key-name my-app-key \
  --key-type ed25519 \
  --query 'KeyMaterial' \
  --output text > my-app-key.pem

# 키 파일 권한 설정 (필수)
chmod 400 my-app-key.pem

# SSH 접속
ssh -i my-app-key.pem ec2-user@<퍼블릭-IP>    # Amazon Linux
ssh -i my-app-key.pem ubuntu@<퍼블릭-IP>       # Ubuntu
```

### 4.2 SSM Session Manager (대안)

SSH 키 관리가 번거롭거나, 보안 그룹에서 22번 포트를 열고 싶지 않을 때는 **SSM Session Manager**가 좋은 대안이다.

```
접속 방식 비교:

SSH:
  로컬 PC ──[22번 포트]──→ EC2 (보안 그룹에 22번 포트 허용 필요)
                           + 키 페어 파일 관리 필요

SSM Session Manager:
  로컬 PC ──[AWS API]──→ SSM 서비스 ──→ EC2 (22번 포트 불필요)
                                        + IAM 역할만 있으면 됨
```

| 방식 | 장점 | 단점 |
|------|------|------|
| **SSH** | 단순하고 익숙함 | 22번 포트 노출, 키 파일 관리 필요 |
| **SSM** | 포트 노출 없음, IAM 기반 접근 제어, 세션 로깅 | SSM Agent 설치 필요, 약간의 설정 필요 |

```bash
# SSM Session Manager로 접속 (AWS CLI + Session Manager Plugin 필요)
aws ssm start-session --target i-0abc123def456

# EC2에 SSM 접속을 위한 IAM 역할 (AmazonSSMManagedInstanceCore 정책 필요)
aws iam attach-role-policy \
  --role-name EC2SSMRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore
```

---

## 5. EBS (Elastic Block Store)

### 5.1 EBS란

EBS(*Elastic Block Store - EC2 인스턴스에 연결하는 블록 수준 스토리지. 인스턴스의 하드 디스크/SSD 역할을 한다*)는 EC2 인스턴스의 디스크이다. 인스턴스를 종료해도 EBS 볼륨의 데이터는 유지된다(설정에 따라).

```
EC2와 EBS의 관계:

┌─── EC2 인스턴스 ───┐     ┌─── EBS 볼륨 ────┐
│                     │     │                  │
│  OS + 애플리케이션   │────→│  루트 볼륨 (/)    │  ← OS가 설치된 디스크
│                     │     │  gp3, 30 GiB     │
│                     │     └──────────────────┘
│                     │
│                     │     ┌─── EBS 볼륨 ────┐
│  데이터 저장         │────→│  데이터 볼륨      │  ← 추가 디스크 (선택)
│                     │     │  gp3, 100 GiB    │
└─────────────────────┘     └──────────────────┘

※ EBS 볼륨은 같은 AZ 안에서만 연결 가능
※ 하나의 EBS 볼륨은 기본적으로 하나의 인스턴스에만 연결
```

### 5.2 EBS 볼륨 타입

| 타입 | 특징 | IOPS | 용도 | 비용(GiB/월) |
|------|------|------|------|-------------|
| **gp3** | 범용 SSD (최신) | 3,000 기본 (최대 16,000) | 대부분의 워크로드에 적합 | ~$0.096 |
| **gp2** | 범용 SSD (이전 세대) | 크기에 비례 (3 IOPS/GiB) | gp3로 마이그레이션 권장 | ~$0.12 |
| **io2** | 프로비저닝된 IOPS SSD | 최대 64,000 | 고성능 DB (대규모 MySQL, PostgreSQL) | ~$0.149 + IOPS 비용 |
| **st1** | 처리량 최적화 HDD | - | 빅데이터, 로그 처리 | ~$0.054 |

```bash
# gp3 볼륨 생성
aws ec2 create-volume \
  --volume-type gp3 \
  --size 30 \
  --availability-zone ap-northeast-2a \
  --tag-specifications 'ResourceType=volume,Tags=[{Key=Name,Value=app-data}]'

# 볼륨을 인스턴스에 연결
aws ec2 attach-volume \
  --volume-id vol-0abc123 \
  --instance-id i-0abc123 \
  --device /dev/xvdf
```

> **핵심 통찰**: **gp3는 gp2보다 20% 저렴하면서 기본 IOPS가 3배 높다** (gp2의 3 IOPS/GiB vs gp3의 3,000 기본 IOPS). 새로 생성하는 볼륨은 무조건 gp3를 선택하라. 기존 gp2 볼륨도 중단 없이 gp3로 마이그레이션할 수 있다.

### 5.3 EBS 스냅샷

스냅샷(*Snapshot - EBS 볼륨의 특정 시점 백업. S3에 저장되며, 이로부터 새 볼륨을 생성하거나 다른 리전에 복사할 수 있다*)은 EBS 볼륨의 백업이다.

```bash
# 스냅샷 생성
aws ec2 create-snapshot \
  --volume-id vol-0abc123 \
  --description "App data backup 2024-01-15" \
  --tag-specifications 'ResourceType=snapshot,Tags=[{Key=Name,Value=app-backup}]'

# 스냅샷에서 새 볼륨 복원
aws ec2 create-volume \
  --snapshot-id snap-0abc123 \
  --volume-type gp3 \
  --availability-zone ap-northeast-2a

# 스냅샷을 다른 리전에 복사 (재해 복구용)
aws ec2 copy-snapshot \
  --source-region ap-northeast-2 \
  --source-snapshot-id snap-0abc123 \
  --destination-region us-east-1 \
  --description "DR copy"
```

---

## 6. Elastic IP

### 6.1 왜 필요한가

EC2 인스턴스를 중지(stop)했다가 다시 시작(start)하면 **퍼블릭 IP가 변경**된다. 이는 DNS 설정이나 외부 시스템 연동에 문제를 일으킨다. Elastic IP(*Elastic IP - AWS 계정에 할당되는 고정 퍼블릭 IP 주소. 인스턴스가 중지/시작되어도 IP가 변하지 않는다*)를 사용하면 IP 주소를 고정할 수 있다.

```bash
# Elastic IP 할당
aws ec2 allocate-address --domain vpc
# 출력: { "AllocationId": "eipalloc-0abc123", "PublicIp": "54.180.xxx.xxx" }

# EC2 인스턴스에 연결
aws ec2 associate-address \
  --allocation-id eipalloc-0abc123 \
  --instance-id i-0abc123

# Elastic IP 연결 해제
aws ec2 disassociate-address --association-id eipassoc-0abc123

# Elastic IP 반환 (사용하지 않을 때 반드시 반환)
aws ec2 release-address --allocation-id eipalloc-0abc123
```

> **비용 주의**: Elastic IP는 **인스턴스에 연결되어 실행 중일 때는 무료**이다. 그러나 **할당만 해두고 연결하지 않거나, 연결된 인스턴스가 중지 상태**이면 시간당 약 $0.005가 과금된다. 사용하지 않는 Elastic IP는 반드시 반환하라. AWS의 IPv4 주소 부족 문제로 인해 과금 정책이 강화되었으며, 2024년 2월부터는 실행 중인 인스턴스에 연결된 경우에도 퍼블릭 IPv4 주소당 시간당 $0.005가 과금된다.

---

## 7. 인스턴스 수명주기

### 7.1 상태 전이

EC2 인스턴스는 다음과 같은 상태를 가진다:

```
인스턴스 수명주기:

  launch
    │
    ↓
┌─────────┐      stop       ┌─────────┐    terminate   ┌────────────┐
│ pending  │──→ running ───────→ stopping ──────────→│ terminated │
└─────────┘    │       │     └─────────┘              └────────────┘
               │       │          │
               │       │          ↓ start
               │       │     ┌─────────┐
               │       │     │ stopped  │
               │       │     └────┬────┘
               │       │          │ start
               │       ←──────────┘
               │
               │ terminate
               └──────────────────→ shutting-down → terminated
```

### 7.2 상태별 비용과 동작

| 상태 | 컴퓨팅 비용 | EBS 비용 | 퍼블릭 IP | 설명 |
|------|-----------|---------|----------|------|
| **running** | 과금 | 과금 | 유지 | 정상 실행 중 |
| **stopped** | **무료** | 과금 | **변경** | 중지 상태, EBS 데이터는 유지 |
| **terminated** | 무료 | **삭제** (기본) | 해제 | 완전 삭제, 복구 불가 |

```bash
# 인스턴스 중지 (비용 절약, EBS 데이터 유지)
aws ec2 stop-instances --instance-ids i-0abc123

# 인스턴스 시작
aws ec2 start-instances --instance-ids i-0abc123

# 인스턴스 종료 (완전 삭제 — 주의!)
aws ec2 terminate-instances --instance-ids i-0abc123
```

> **실무 팁**: 개발/테스트 인스턴스는 퇴근 시 **stop**하고 출근 시 **start**하면 비용을 크게 줄일 수 있다. 하루 8시간만 실행하면 24시간 대비 **67%를 절약**한다. AWS Instance Scheduler 또는 Lambda + EventBridge로 자동화할 수 있다.

---

## 8. User Data

### 8.1 User Data란

User Data는 인스턴스가 **최초 시작될 때 자동으로 실행되는 스크립트**이다. OS 패키지 설치, 애플리케이션 배포, 환경 설정 등을 자동화할 수 있다.

### 8.2 Node.js 서버 배포 예시

```bash
#!/bin/bash
# User Data 스크립트 (Amazon Linux 2023 기준)

# 시스템 업데이트
dnf update -y

# Node.js 20 설치
dnf install -y nodejs20

# PM2 전역 설치
npm install -g pm2

# 애플리케이션 코드 클론
cd /home/ec2-user
git clone https://github.com/my-org/my-api.git
cd my-api

# 의존성 설치 및 빌드
npm ci --production
npm run build

# PM2로 서버 실행
pm2 start dist/index.js --name my-api
pm2 startup
pm2 save

# CloudWatch Agent 설치 (로그 수집용)
dnf install -y amazon-cloudwatch-agent
```

### 8.3 인스턴스 생성 시 User Data 지정

```bash
# User Data를 파일로 저장한 후 인스턴스 생성
aws ec2 run-instances \
  --image-id ami-0abc123 \
  --instance-type t4g.micro \
  --key-name my-app-key \
  --security-group-ids sg-0abc123 \
  --subnet-id subnet-0abc123 \
  --user-data file://user-data.sh \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=my-api-server}]'
```

```bash
# User Data 실행 로그 확인 (인스턴스 접속 후)
sudo cat /var/log/cloud-init-output.log
```

---

## 9. 보안 그룹 설정 (EC2 관점)

### 9.1 보안 그룹 복습

보안 그룹은 Chapter 4에서 다루었다. 여기서는 EC2 인스턴스에 특화된 보안 그룹 설정을 살펴본다.

### 9.2 일반적인 웹 서버 보안 그룹

```bash
# 웹 서버 보안 그룹 생성
aws ec2 create-security-group \
  --group-name web-server-sg \
  --description "Web server security group" \
  --vpc-id vpc-0abc123

# HTTP (80) — 모든 IP에서 허용 (ALB를 사용한다면 ALB SG에서만 허용)
aws ec2 authorize-security-group-ingress \
  --group-id sg-web123 \
  --protocol tcp --port 80 --cidr 0.0.0.0/0

# HTTPS (443) — 모든 IP에서 허용
aws ec2 authorize-security-group-ingress \
  --group-id sg-web123 \
  --protocol tcp --port 443 --cidr 0.0.0.0/0

# SSH (22) — 내 IP에서만 허용 (또는 SSM 사용 시 불필요)
aws ec2 authorize-security-group-ingress \
  --group-id sg-web123 \
  --protocol tcp --port 22 --cidr 203.0.113.50/32

# Node.js 앱 포트 (3000) — ALB 보안 그룹에서만 허용
aws ec2 authorize-security-group-ingress \
  --group-id sg-web123 \
  --protocol tcp --port 3000 --source-group sg-alb123
```

### 9.3 계층별 보안 그룹 구성

```
보안 그룹 체이닝 (3-Tier):

인터넷
  │
  ↓
┌──────────── ALB 보안 그룹 ────────────┐
│  인바운드: 80, 443 from 0.0.0.0/0     │
└───────────────┬───────────────────────┘
                │
                ↓
┌──────────── EC2 보안 그룹 ────────────┐
│  인바운드: 3000 from ALB SG만          │
│  인바운드: 22 from 내 IP만 (선택)      │
└───────────────┬───────────────────────┘
                │
                ↓
┌──────────── RDS 보안 그룹 ────────────┐
│  인바운드: 5432 from EC2 SG만          │
└───────────────────────────────────────┘
```

---

## 10. Auto Scaling

### 10.1 왜 필요한가

단일 EC2 인스턴스로는 트래픽 급증을 감당할 수 없다. 서버가 다운되면 서비스 전체가 중단된다. Auto Scaling은 **트래픽에 따라 인스턴스 수를 자동으로 늘리거나 줄여주는** 서비스이다.

```
Auto Scaling 동작:

평소 (트래픽 낮음):                  피크 시간 (트래픽 높음):
┌───────┐                           ┌───────┐ ┌───────┐ ┌───────┐
│ EC2-1 │  ← 최소 1대 유지           │ EC2-1 │ │ EC2-2 │ │ EC2-3 │
└───────┘                           └───────┘ └───────┘ └───────┘
                                     ← 자동으로 3대까지 확장

트래픽 감소 후:
┌───────┐
│ EC2-1 │  ← 자동으로 1대로 축소
└───────┘
```

### 10.2 핵심 구성 요소

| 구성 요소 | 역할 |
|----------|------|
| **시작 템플릿 (Launch Template)** | 새 인스턴스를 어떻게 생성할지 정의 (AMI, 인스턴스 타입, 키 페어, 보안 그룹, User Data) |
| **Auto Scaling 그룹 (ASG)** | 인스턴스 그룹 관리 (최소/최대/원하는 인스턴스 수, 서브넷, 헬스 체크) |
| **스케일링 정책** | 언제, 얼마나 인스턴스를 늘리거나 줄일지 결정하는 규칙 |

### 10.3 시작 템플릿 (Launch Template)

```bash
# 시작 템플릿 생성
aws ec2 create-launch-template \
  --launch-template-name my-api-template \
  --version-description "v1" \
  --launch-template-data '{
    "ImageId": "ami-0abc123",
    "InstanceType": "t4g.small",
    "KeyName": "my-app-key",
    "SecurityGroupIds": ["sg-web123"],
    "UserData": "'$(base64 -i user-data.sh)'",
    "TagSpecifications": [
      {
        "ResourceType": "instance",
        "Tags": [{"Key": "Name", "Value": "my-api-server"}]
      }
    ]
  }'
```

### 10.4 Auto Scaling 그룹 (ASG)

```bash
# Auto Scaling 그룹 생성
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name my-api-asg \
  --launch-template LaunchTemplateName=my-api-template,Version='$Latest' \
  --min-size 1 \
  --max-size 5 \
  --desired-capacity 2 \
  --vpc-zone-identifier "subnet-az-a,subnet-az-b" \
  --health-check-type ELB \
  --health-check-grace-period 300 \
  --target-group-arns "arn:aws:elasticloadbalancing:ap-northeast-2:123456789012:targetgroup/my-api-tg/abc123"
```

### 10.5 스케일링 정책

| 정책 유형 | 설명 | 예시 |
|----------|------|------|
| **대상 추적 (Target Tracking)** | 지정한 메트릭의 목표값을 유지하도록 자동 조절 | CPU 평균 50% 유지 |
| **단계별 (Step Scaling)** | 메트릭 임계값에 따라 단계적으로 인스턴스 추가/제거 | CPU 70% → 1대 추가, 90% → 2대 추가 |
| **예약 (Scheduled)** | 예측 가능한 트래픽 패턴에 맞춰 시간대별 설정 | 오전 9시에 5대, 오후 6시에 2대 |

```bash
# 대상 추적 스케일링 정책 (가장 권장)
aws autoscaling put-scaling-policy \
  --auto-scaling-group-name my-api-asg \
  --policy-name cpu-target-tracking \
  --policy-type TargetTrackingScaling \
  --target-tracking-configuration '{
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ASGAverageCPUUtilization"
    },
    "TargetValue": 50.0,
    "ScaleInCooldownSeconds": 300,
    "ScaleOutCooldownSeconds": 60
  }'
```

---

## 11. Elastic Load Balancer (ALB)

### 11.1 로드밸런서의 역할

로드밸런서(*Load Balancer - 들어오는 트래픽을 여러 서버로 분산시키는 서비스. 단일 진입점을 제공하고, 비정상 서버를 자동으로 제외한다*)는 Auto Scaling과 함께 사용하여 트래픽을 여러 인스턴스에 균등하게 분배한다.

```
로드밸런서 아키텍처:

사용자 → Route 53 (DNS)
              │
              ↓
         ┌─── ALB (Application Load Balancer) ───┐
         │    443 (HTTPS) → 리스너                 │
         │         │                               │
         │    ┌────┴──── 타겟 그룹 ────────┐        │
         │    │                            │        │
         │    ↓            ↓              ↓        │
         │  EC2-1 (AZ-a) EC2-2 (AZ-b) EC2-3(AZ-a)│
         │  :3000         :3000         :3000      │
         └─────────────────────────────────────────┘
```

### 11.2 ALB vs NLB

AWS는 여러 종류의 로드밸런서를 제공하지만, 웹 애플리케이션에서 가장 자주 사용하는 것은 **ALB**이다.

| 특성 | ALB (Application) | NLB (Network) |
|------|-------------------|---------------|
| **OSI 계층** | 7계층 (HTTP/HTTPS) | 4계층 (TCP/UDP) |
| **라우팅** | URL 경로, 호스트, 헤더 기반 | IP, 포트 기반 |
| **적합한 워크로드** | 웹 애플리케이션, API 서버 | 극도로 낮은 지연 시간, 게임 서버, IoT |
| **WebSocket** | 지원 | 지원 |
| **비용** | 약간 더 비쌈 | 약간 더 저렴 |

### 11.3 ALB 생성

```bash
# ALB 생성
aws elbv2 create-load-balancer \
  --name my-api-alb \
  --type application \
  --subnets subnet-az-a subnet-az-b \
  --security-groups sg-alb123

# 타겟 그룹 생성
aws elbv2 create-target-group \
  --name my-api-tg \
  --protocol HTTP \
  --port 3000 \
  --vpc-id vpc-0abc123 \
  --target-type instance \
  --health-check-path /health \
  --health-check-interval-seconds 30 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 3

# 리스너 생성 (HTTPS)
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:...:loadbalancer/app/my-api-alb/abc123 \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=arn:aws:acm:ap-northeast-2:123456789012:certificate/abc123 \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:...:targetgroup/my-api-tg/abc123
```

### 11.4 ALB + Auto Scaling 전체 흐름

```
전체 아키텍처:

Route 53 (api.example.com)
    │
    ↓
ALB (퍼블릭 서브넷)
    │
    ├──→ EC2-1 (프라이빗 서브넷 AZ-a) ──→ RDS Primary (프라이빗 서브넷 AZ-a)
    ├──→ EC2-2 (프라이빗 서브넷 AZ-b) ──→ RDS Standby (프라이빗 서브넷 AZ-b)
    └──→ EC2-3 (프라이빗 서브넷 AZ-a)
         │
         └── Auto Scaling 그룹이 관리 (최소 2, 최대 5)
              └── CPU 50% 유지 정책

※ ALB만 퍼블릭 서브넷에 배치
※ EC2 인스턴스는 프라이빗 서브넷에 배치
※ EC2는 NAT Gateway를 통해 인터넷(npm install 등)에 접근
```

> **핵심 통찰**: EC2를 프로덕션에서 운영할 때는 **단일 인스턴스가 아닌 ALB + Auto Scaling 조합**이 사실상 필수이다. 이 조합은 세 가지를 동시에 해결한다: (1) **가용성** - 인스턴스 하나가 죽어도 다른 인스턴스가 트래픽을 받는다, (2) **확장성** - 트래픽에 따라 자동으로 인스턴스가 늘어난다, (3) **비용 효율** - 트래픽이 줄면 자동으로 인스턴스가 줄어든다.

---

## 12. 구매 옵션

### 12.1 옵션 비교

EC2는 동일한 인스턴스 타입이라도 **어떻게 구매하느냐**에 따라 비용이 크게 달라진다.

| 옵션 | 할인율 | 약정 | 적합한 워크로드 |
|------|--------|------|---------------|
| **온디맨드** | 기준 가격 | 없음 | 단기 작업, 예측 불가능한 워크로드 |
| **예약 인스턴스 (RI)** | 최대 72% 할인 | 1년 또는 3년 | 24/7 실행하는 프로덕션 서버 |
| **Savings Plans** | 최대 72% 할인 | 1년 또는 3년 | 일정 금액 이상의 컴퓨팅 사용 |
| **스팟 인스턴스** | 최대 90% 할인 | 없음 (중단 가능) | 배치 처리, CI/CD, 데이터 분석 |

### 12.2 온디맨드 (On-Demand)

가장 기본적인 구매 방식이다. 사용한 시간(초 단위)만큼만 과금된다. 약정이 없어 언제든 시작하고 중지할 수 있다.

```
t4g.micro 온디맨드 월 비용 (서울 리전):
  $0.0108/시간 × 24시간 × 30일 = 약 $7.78/월
```

### 12.3 예약 인스턴스 (Reserved Instance)

1년 또는 3년 약정으로 대폭 할인받는 방식이다. 24시간 365일 실행하는 프로덕션 서버에 적합하다.

| 결제 방식 | 할인율 (1년) | 할인율 (3년) |
|----------|------------|------------|
| **전체 선결제** | ~40% | ~60% |
| **부분 선결제** | ~30% | ~50% |
| **선결제 없음** | ~20% | ~40% |

### 12.4 스팟 인스턴스 (Spot Instance)

AWS의 **유휴 컴퓨팅 용량**을 매우 저렴하게 사용하는 방식이다. 최대 90%까지 할인되지만, AWS가 용량이 필요하면 **2분 전 경고 후 인스턴스를 회수**할 수 있다.

```bash
# 스팟 인스턴스 요청
aws ec2 run-instances \
  --image-id ami-0abc123 \
  --instance-type c5.xlarge \
  --instance-market-options '{
    "MarketType": "spot",
    "SpotOptions": {
      "MaxPrice": "0.05",
      "SpotInstanceType": "one-time"
    }
  }'
```

**스팟 인스턴스에 적합한 워크로드:**

- CI/CD 빌드 서버 (중단되면 재시도하면 됨)
- 데이터 분석/배치 처리 (체크포인트로 진행 상황 저장)
- 개발/테스트 환경
- Auto Scaling 그룹에 온디맨드와 혼합 사용

**스팟 인스턴스에 부적합한 워크로드:**

- 프로덕션 웹 서버 (중단 시 서비스 장애)
- 데이터베이스 (중단 시 데이터 손실 위험)

> **비용 주의**: EC2는 AWS 청구서에서 가장 큰 비중을 차지하는 서비스 중 하나이다. **"일단 큰 인스턴스를 띄우자"**는 접근은 위험하다. 반드시 (1) 작은 인스턴스로 시작하고, (2) CloudWatch 메트릭으로 사용률을 모니터링한 후, (3) 필요한 만큼만 스케일업하라. 학습 중에는 인스턴스를 사용하지 않을 때 반드시 **stop** 또는 **terminate**하고, 불필요한 EBS 볼륨과 Elastic IP를 정리하라.

---

## 13. EC2 인스턴스 생성 전체 실습

지금까지 배운 구성 요소를 조합하여 Node.js 서버를 EC2에 배포하는 전체 과정을 정리한다.

```bash
# 1. 키 페어 생성
aws ec2 create-key-pair \
  --key-name my-app-key \
  --key-type ed25519 \
  --query 'KeyMaterial' --output text > my-app-key.pem
chmod 400 my-app-key.pem

# 2. 보안 그룹 생성
aws ec2 create-security-group \
  --group-name my-app-sg \
  --description "My app security group" \
  --vpc-id vpc-0abc123

# 3. 보안 그룹 규칙 추가
aws ec2 authorize-security-group-ingress \
  --group-id sg-0abc123 \
  --protocol tcp --port 22 --cidr $(curl -s ifconfig.me)/32  # 내 IP만

aws ec2 authorize-security-group-ingress \
  --group-id sg-0abc123 \
  --protocol tcp --port 3000 --cidr 0.0.0.0/0

# 4. User Data 스크립트 작성
cat > user-data.sh << 'EOF'
#!/bin/bash
dnf update -y
dnf install -y nodejs20 git
npm install -g pm2
cd /home/ec2-user
git clone https://github.com/my-org/my-api.git
cd my-api
npm ci --production
npm run build
pm2 start dist/index.js --name my-api
pm2 startup
pm2 save
EOF

# 5. EC2 인스턴스 생성
aws ec2 run-instances \
  --image-id ami-0abc123 \
  --instance-type t4g.micro \
  --key-name my-app-key \
  --security-group-ids sg-0abc123 \
  --subnet-id subnet-0abc123 \
  --user-data file://user-data.sh \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=my-api-server}]'

# 6. 인스턴스 퍼블릭 IP 확인
aws ec2 describe-instances \
  --instance-ids i-0abc123 \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text

# 7. SSH 접속 확인
ssh -i my-app-key.pem ec2-user@<퍼블릭-IP>

# 8. 앱 동작 확인
curl http://<퍼블릭-IP>:3000/health
```

---

## 자주 하는 실수

| 실수 | 설명 | 올바른 접근 |
|------|------|------------|
| **SSH(22)를 0.0.0.0/0으로 열어둠** | 전 세계에서 무차별 SSH 접속 시도가 들어온다 | 내 IP만 허용하거나 SSM Session Manager 사용 |
| **인스턴스를 stop 대신 terminate** | terminate하면 EBS 데이터가 삭제되어 복구 불가 | 의도적인 삭제가 아니면 stop 사용, 종료 보호 활성화 |
| **Elastic IP 할당 후 방치** | 연결하지 않은 Elastic IP는 시간당 과금 | 사용하지 않으면 즉시 release |
| **루트 볼륨 크기를 너무 작게 설정** | 디스크 풀로 인스턴스가 먹통이 됨 | 최소 20~30 GiB, 모니터링으로 사용량 추적 |
| **User Data 스크립트 디버깅 미흡** | 스크립트 실패 시 인스턴스가 빈 상태로 뜸 | `/var/log/cloud-init-output.log` 확인 |
| **보안 그룹 없이 모든 포트 오픈** | 불필요한 포트가 인터넷에 노출됨 | 필요한 포트만 최소한으로 오픈 |
| **단일 AZ에 모든 인스턴스 배치** | AZ 장애 시 서비스 전체 다운 | ASG에서 최소 2개 AZ에 인스턴스 분산 |
| **gp2 볼륨을 계속 사용** | gp3보다 20% 더 비싸고 기본 성능도 낮음 | 새 볼륨은 gp3, 기존 볼륨도 gp3로 마이그레이션 |

---

## AWS CLI 레퍼런스

| 명령어 | 설명 |
|--------|------|
| `aws ec2 run-instances --image-id AMI --instance-type TYPE` | EC2 인스턴스 생성 |
| `aws ec2 describe-instances` | 인스턴스 목록 조회 |
| `aws ec2 start-instances --instance-ids ID` | 인스턴스 시작 |
| `aws ec2 stop-instances --instance-ids ID` | 인스턴스 중지 |
| `aws ec2 terminate-instances --instance-ids ID` | 인스턴스 종료 (삭제) |
| `aws ec2 create-key-pair --key-name NAME` | 키 페어 생성 |
| `aws ec2 create-security-group --group-name NAME --vpc-id VPC` | 보안 그룹 생성 |
| `aws ec2 authorize-security-group-ingress --group-id SG --protocol tcp --port PORT --cidr CIDR` | 인바운드 규칙 추가 |
| `aws ec2 create-volume --volume-type gp3 --size SIZE --availability-zone AZ` | EBS 볼륨 생성 |
| `aws ec2 create-snapshot --volume-id VOL` | EBS 스냅샷 생성 |
| `aws ec2 allocate-address --domain vpc` | Elastic IP 할당 |
| `aws ec2 associate-address --allocation-id EIP --instance-id ID` | Elastic IP 연결 |
| `aws ec2 release-address --allocation-id EIP` | Elastic IP 반환 |
| `aws ec2 create-image --instance-id ID --name NAME` | 커스텀 AMI 생성 |
| `aws ec2 create-launch-template --launch-template-name NAME` | 시작 템플릿 생성 |
| `aws autoscaling create-auto-scaling-group --auto-scaling-group-name NAME` | Auto Scaling 그룹 생성 |
| `aws elbv2 create-load-balancer --name NAME --type application` | ALB 생성 |
| `aws elbv2 create-target-group --name NAME --protocol HTTP --port PORT` | 타겟 그룹 생성 |
| `aws ssm start-session --target INSTANCE_ID` | SSM Session Manager 접속 |

---

## 요약

- **EC2**는 AWS의 대표적인 IaaS 서비스로, 몇 분 안에 가상 서버를 생성하고 사용한 시간만큼만 비용을 지불한다.
- **인스턴스 타입**은 `패밀리 + 세대 + 크기` 규칙을 따른다. 대부분의 웹 서버에는 **t4g(Graviton 버스트)** 인스턴스가 가장 비용 효율적이다.
- **AMI**는 OS 템플릿이다. Amazon Linux 2023 또는 Ubuntu를 주로 사용하며, 커스텀 AMI로 배포 시간을 단축할 수 있다.
- **키 페어**로 SSH 접속하거나, **SSM Session Manager**로 포트 노출 없이 접속할 수 있다.
- **EBS**는 인스턴스의 디스크이다. 새 볼륨은 **gp3**를 선택하라 (gp2보다 20% 저렴, 3배 높은 기본 IOPS).
- **Elastic IP**는 고정 퍼블릭 IP이다. 사용하지 않으면 반드시 반환하라.
- 인스턴스는 **running**(과금), **stopped**(컴퓨팅 무료, EBS 과금), **terminated**(삭제) 세 가지 주요 상태를 갖는다.
- **User Data**로 인스턴스 시작 시 Node.js 설치, 앱 배포 등을 자동화할 수 있다.
- 프로덕션 환경에서는 **ALB + Auto Scaling** 조합으로 가용성, 확장성, 비용 효율을 모두 확보한다.
- **구매 옵션**: 온디맨드(기본), 예약 인스턴스(최대 72% 할인, 장기 약정), 스팟(최대 90% 할인, 중단 가능)을 워크로드에 맞게 선택한다.
- EC2 비용은 AWS 청구서의 큰 비중을 차지한다. **작게 시작하고, 모니터링하고, 필요한 만큼만 확장**하는 것이 핵심이다.
