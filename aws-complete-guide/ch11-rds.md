# Chapter 11: RDS - 관계형 데이터베이스: Relational Database Service

## 핵심 질문

AWS에서 관계형 데이터베이스를 어떻게 구축하고 운영하는가? EC2에 직접 DB를 설치하는 것과 RDS를 사용하는 것은 어떻게 다르며, Multi-AZ 배포, Read Replica, 자동 백업, RDS Proxy를 활용하여 고가용성과 확장성을 갖춘 데이터베이스 인프라를 설계하려면 어떻게 해야 하는가?

---

## 1. 관리형 데이터베이스란

### 1.1 EC2에 직접 설치 vs RDS

데이터베이스를 사용하는 방법은 크게 두 가지이다. EC2 인스턴스에 MySQL이나 PostgreSQL을 직접 설치하는 방법과, AWS가 제공하는 관리형 서비스인 RDS를 사용하는 방법이다.

```
EC2에 직접 설치:

┌─── EC2 인스턴스 ───────────────────┐
│                                     │
│  ┌─── 너가 관리 ──────────────────┐ │
│  │  OS 패치, 보안 업데이트         │ │
│  │  DB 엔진 설치 및 업데이트       │ │
│  │  백업 스크립트 작성             │ │
│  │  복제(Replication) 직접 구성   │ │
│  │  모니터링 도구 설치             │ │
│  │  장애 시 수동 복구              │ │
│  │  디스크 용량 관리               │ │
│  └────────────────────────────────┘ │
│  EBS 볼륨 (직접 관리)               │
└─────────────────────────────────────┘

RDS (관리형):

┌─── RDS 인스턴스 ──────────────────┐
│                                    │
│  ┌─── AWS가 관리 ────────────────┐ │
│  │  OS 패치, 보안 업데이트        │ │
│  │  DB 엔진 설치 및 업데이트      │ │
│  │  자동 백업 (35일까지)         │ │
│  │  Multi-AZ 자동 페일오버       │ │
│  │  CloudWatch 메트릭 자동 수집  │ │
│  │  스토리지 자동 확장            │ │
│  └───────────────────────────────┘ │
│                                    │
│  ┌─── 너가 관리 ────────────────┐  │
│  │  스키마 설계, 쿼리 최적화     │  │
│  │  파라미터 그룹 튜닝           │  │
│  │  보안 그룹 설정               │  │
│  │  Read Replica 구성 결정      │  │
│  └───────────────────────────────┘ │
└────────────────────────────────────┘
```

| 항목 | EC2 직접 설치 | RDS |
|------|-------------|-----|
| **OS 패치** | 직접 수행 | AWS 자동 |
| **DB 엔진 업데이트** | 직접 수행 | AWS 관리 (유지보수 창에서 자동) |
| **백업** | 크론잡 + 스크립트 직접 작성 | 자동 백업 + 수동 스냅샷 |
| **고가용성** | 복제 직접 구성 (복잡) | Multi-AZ 체크박스 하나로 활성화 |
| **스케일링** | 수동으로 인스턴스 변경 | 콘솔에서 클릭 또는 CLI 한 줄 |
| **모니터링** | CloudWatch Agent 직접 설치 | 기본 메트릭 자동 제공 |
| **비용** | EC2 + EBS 비용만 | 관리 비용이 포함되어 약간 더 비쌈 |
| **유연성** | OS 레벨 완전 제어 가능 | OS 접근 불가, DB 설정만 변경 가능 |

> **핵심 통찰**: RDS를 선택하면 인프라 관리의 약 70~80%를 AWS에 위임하고, 개발자는 **스키마 설계와 쿼리 최적화**에 집중할 수 있다. EC2에 직접 설치해야 하는 경우는 극히 드물다. OS 레벨 접근이 필요하거나, RDS가 지원하지 않는 DB 엔진을 사용해야 할 때뿐이다. 대부분의 프로젝트에서는 RDS가 정답이다.

---

## 2. 지원하는 DB 엔진

### 2.1 엔진 비교

RDS는 6가지 관계형 데이터베이스 엔진을 지원한다.

| 엔진 | 라이선스 | 특징 | 주요 사용 사례 |
|------|---------|------|-------------|
| **MySQL** | 오픈소스 | 가장 널리 사용되는 오픈소스 RDBMS | 범용 웹 애플리케이션 |
| **PostgreSQL** | 오픈소스 | 고급 기능(JSON, 전문 검색, 지리 데이터), 표준 준수도 높음 | 복잡한 쿼리, GIS, 분석 |
| **MariaDB** | 오픈소스 | MySQL 포크, MySQL과 높은 호환성 | MySQL 대안 |
| **Oracle** | 상용 | 엔터프라이즈 기능, 레거시 시스템에서 많이 사용 | 기업 시스템 마이그레이션 |
| **SQL Server** | 상용 | Microsoft 생태계와 통합 | .NET 기반 애플리케이션 |
| **Aurora** | AWS 독자 | MySQL/PostgreSQL 호환, AWS 최적화 | 고성능/고가용성이 필요한 프로덕션 |

### 2.2 어떤 엔진을 선택할 것인가

```
엔진 선택 의사결정 흐름:

새 프로젝트인가? ───────────────── 레거시 마이그레이션인가?
    │                                     │
    ↓                                     ↓
높은 가용성/성능이                    기존 DB 엔진과
최우선 과제인가?                     같은 엔진 선택
    │                                (Oracle → RDS Oracle)
    ├── Yes → Aurora PostgreSQL
    │         (AWS 최적화, 자동 스케일링)
    │
    └── No → PostgreSQL
              (범용적, 비용 효율적)
```

> **실무 팁**: 새 프로젝트에서 특별한 이유가 없다면 **PostgreSQL**을 선택하라. MySQL보다 SQL 표준 준수도가 높고, JSONB, 전문 검색, CTE 등 고급 기능이 풍부하다. Node.js 생태계의 Prisma, Drizzle, Knex 등 주요 ORM이 PostgreSQL을 가장 잘 지원한다. 프로덕션 요구사항이 높아지면 Aurora PostgreSQL로 엔진 변경 없이 마이그레이션할 수 있다.

---

## 3. 인스턴스 클래스

### 3.1 RDS 인스턴스 클래스 이해하기

RDS 인스턴스 클래스는 EC2 인스턴스 타입과 유사한 네이밍 규칙을 따르지만, `db.` 접두사가 붙는다.

```
RDS 인스턴스 클래스 이름 규칙:

  db.t3.micro
  ── │ │ └──── 크기 (micro, small, medium, large, xlarge ...)
     │ └───── 세대 (숫자가 클수록 최신)
     └────── 패밀리 (t=버스트, m=범용, r=메모리 최적화)
```

### 3.2 주요 인스턴스 클래스

| 클래스 | 용도 | 특징 | 사용 사례 |
|--------|------|------|----------|
| **db.t3 / db.t4g** | 버스트 가능 | CPU 크레딧 기반, 간헐적 부하에 최적 | 개발/테스트, 소규모 프로덕션 |
| **db.m5 / db.m6g** | 범용 | CPU와 메모리 균형, 일정한 워크로드에 적합 | 중간 규모 프로덕션 |
| **db.r5 / db.r6g** | 메모리 최적화 | 대용량 메모리, 쿼리 캐싱에 유리 | 대규모 프로덕션, 복잡한 쿼리 |

| 인스턴스 클래스 | vCPU | 메모리 | 네트워크 | 월 비용(서울, 단일 AZ) |
|---------------|------|--------|----------|---------------------|
| db.t3.micro | 2 | 1 GiB | 저 | ~$19 |
| db.t3.small | 2 | 2 GiB | 저 | ~$38 |
| db.t3.medium | 2 | 4 GiB | 중 | ~$76 |
| db.m5.large | 2 | 8 GiB | 최대 10 Gbps | ~$185 |
| db.r5.large | 2 | 16 GiB | 최대 10 Gbps | ~$230 |
| db.r5.xlarge | 4 | 32 GiB | 최대 10 Gbps | ~$460 |

> **비용 주의**: RDS는 **인스턴스가 중지(stop) 상태여도 7일 후 자동으로 재시작**된다. EC2처럼 무기한 중지해둘 수 없다. 학습 환경에서는 사용 후 반드시 **삭제**하고, 필요하면 스냅샷에서 복원하라. db.t3.micro는 Free Tier에서 750시간/월 무료이다(12개월간).

---

## 4. 스토리지 타입

### 4.1 RDS 스토리지 옵션

RDS는 EBS 기반의 스토리지를 사용하며, 세 가지 타입을 지원한다.

| 타입 | 특징 | IOPS | 용도 | 비용(GiB/월) |
|------|------|------|------|-------------|
| **gp3** | 범용 SSD (최신) | 3,000 기본 (최대 16,000) | 대부분의 워크로드 | ~$0.128 |
| **io1/io2** | 프로비저닝된 IOPS SSD | 최대 256,000 | 높은 I/O가 필요한 대규모 DB | ~$0.149 + IOPS 비용 |
| **magnetic** | 마그네틱 (이전 세대) | 제한적 | 비용 절약이 최우선인 저부하 워크로드 | ~$0.116 |

### 4.2 스토리지 자동 확장 (Storage Auto Scaling)

RDS는 스토리지가 부족해지면 **자동으로 용량을 확장**하는 기능을 제공한다. 초기에 작은 용량으로 시작하고, 데이터가 늘어나면 자동으로 확장되므로 사전에 대용량을 할당할 필요가 없다.

```bash
# RDS 생성 시 스토리지 자동 확장 활성화
aws rds create-db-instance \
  --db-instance-identifier my-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password 'SecurePassword123!' \
  --allocated-storage 20 \
  --max-allocated-storage 100 \
  --storage-type gp3
# --allocated-storage: 초기 20 GiB
# --max-allocated-storage: 최대 100 GiB까지 자동 확장
```

> **실무 팁**: 스토리지 타입은 **gp3를 기본으로 선택**하라. gp2보다 20% 저렴하면서 기본 IOPS가 높다. io1/io2는 수만 IOPS가 필요한 대규모 프로덕션 DB에서만 고려하면 된다. 또한 `--max-allocated-storage`를 반드시 설정하여 디스크 부족으로 DB가 멈추는 사태를 예방하라.

---

## 5. 네트워크 설정

### 5.1 RDS의 네트워크 배치

RDS 인스턴스는 VPC 안에 배치된다. Chapter 4에서 다룬 VPC의 원칙이 그대로 적용된다. 핵심은 **RDS를 프라이빗 서브넷에 배치**하여 인터넷에서 직접 접근할 수 없게 하는 것이다.

```
RDS 네트워크 아키텍처:

인터넷
  │
  ↓
┌──────────────── VPC (10.0.0.0/16) ────────────────────┐
│                                                        │
│  [퍼블릭 서브넷]                                        │
│  ┌──────────────┐  ┌──────────────┐                    │
│  │ ALB (AZ-a)   │  │ ALB (AZ-b)   │                    │
│  └──────┬───────┘  └──────┬───────┘                    │
│         │                  │                            │
│  [프라이빗 서브넷 - 앱]                                  │
│  ┌──────┴───────┐  ┌──────┴───────┐                    │
│  │ EC2/ECS(AZ-a)│  │ EC2/ECS(AZ-b)│                    │
│  └──────┬───────┘  └──────┬───────┘                    │
│         │                  │                            │
│  [프라이빗 서브넷 - DB] ← DB 서브넷 그룹                 │
│  ┌──────┴───────┐  ┌──────┴───────┐                    │
│  │ RDS Primary  │  │ RDS Standby  │                    │
│  │   (AZ-a)     │  │   (AZ-b)     │                    │
│  │ 10.0.5.0/24  │  │ 10.0.6.0/24  │                    │
│  └──────────────┘  └──────────────┘                    │
│                                                        │
│  ※ 인터넷 → RDS 직접 접근 불가                           │
│  ※ EC2/ECS → RDS만 접근 가능 (보안 그룹으로 제어)        │
└────────────────────────────────────────────────────────┘
```

### 5.2 DB 서브넷 그룹

DB 서브넷 그룹(*DB Subnet Group - RDS 인스턴스가 배치될 수 있는 서브넷의 모음. 최소 2개 이상의 AZ에 있는 서브넷을 포함해야 한다*)은 RDS가 사용할 서브넷을 지정하는 것이다. Multi-AZ 배포를 위해 최소 2개 AZ의 서브넷이 필요하다.

```bash
# DB 서브넷 그룹 생성
aws rds create-db-subnet-group \
  --db-subnet-group-name my-db-subnet-group \
  --db-subnet-group-description "Private subnets for RDS" \
  --subnet-ids '["subnet-az-a-private", "subnet-az-b-private"]'
```

### 5.3 보안 그룹 설정

RDS 인스턴스에는 **애플리케이션 서버의 보안 그룹에서만 접근을 허용**하는 보안 그룹을 설정한다.

```bash
# RDS 보안 그룹 생성
aws ec2 create-security-group \
  --group-name rds-sg \
  --description "Security group for RDS" \
  --vpc-id vpc-0abc123

# PostgreSQL(5432) - 앱 서버 보안 그룹에서만 허용
aws ec2 authorize-security-group-ingress \
  --group-id sg-rds123 \
  --protocol tcp \
  --port 5432 \
  --source-group sg-app123

# MySQL(3306) 사용 시
# aws ec2 authorize-security-group-ingress \
#   --group-id sg-rds123 \
#   --protocol tcp \
#   --port 3306 \
#   --source-group sg-app123
```

```
보안 그룹 체이닝:

ALB SG ──[3000]──→ App SG ──[5432]──→ RDS SG
0.0.0.0/0          ALB SG만            App SG만

※ RDS는 인터넷에서 절대 직접 접근 불가
※ 개발자도 EC2 Bastion 또는 SSM을 통해서만 접근
```

> **핵심 통찰**: RDS를 퍼블릭 서브넷에 배치하고 `Publicly Accessible`을 활성화하면 인터넷에서 직접 DB에 접속할 수 있지만, **프로덕션에서는 절대 이렇게 하지 마라.** 개발 편의를 위해 잠깐 열어두었다가 잊는 경우가 많고, 이는 심각한 보안 사고로 이어진다. 개발 중에도 Bastion Host 또는 SSM Port Forwarding을 사용하는 습관을 들여라.

---

## 6. Multi-AZ 배포

### 6.1 고가용성이란

프로덕션 데이터베이스에서 가장 중요한 것은 **데이터를 잃지 않는 것**과 **서비스가 중단되지 않는 것**이다. Multi-AZ(*Multi-AZ Deployment - RDS가 두 개의 가용 영역에 동기식 복제본을 유지하여, 장애 시 자동으로 페일오버하는 고가용성 구성*)는 이 두 가지를 동시에 해결한다.

### 6.2 Multi-AZ 동작 방식

```
Multi-AZ 배포 구조:

┌─── AZ-a ────────────┐     ┌─── AZ-b ────────────┐
│                      │     │                      │
│  ┌─── Primary ────┐  │     │  ┌─── Standby ────┐  │
│  │  RDS 인스턴스   │  │     │  │  RDS 인스턴스   │  │
│  │  읽기 + 쓰기    │──┼──동기──┼→│  대기 (접근불가) │  │
│  │                 │  │  복제  │  │                 │  │
│  └─────────────────┘  │     │  └─────────────────┘  │
│                      │     │                      │
└──────────────────────┘     └──────────────────────┘

장애 발생 시 (Primary 다운):

┌─── AZ-a ────────────┐     ┌─── AZ-b ────────────┐
│                      │     │                      │
│  ┌─── Primary ────┐  │     │  ┌─── New Primary ──┐ │
│  │  ██ 장애 ██    │  │     │  │  RDS 인스턴스     │ │
│  │  (접근 불가)    │  │     │  │  읽기 + 쓰기      │ │
│  │                 │  │     │  │  ← DNS 자동 전환  │ │
│  └─────────────────┘  │     │  └─────────────────┘  │
│                      │     │                      │
└──────────────────────┘     └──────────────────────┘

※ DNS 엔드포인트는 그대로 유지 → 애플리케이션 코드 변경 불필요
※ 페일오버 소요 시간: 보통 60~120초
```

### 6.3 Multi-AZ 핵심 포인트

| 특성 | 설명 |
|------|------|
| **복제 방식** | 동기식 (Primary에 쓰면 Standby에도 즉시 반영) |
| **페일오버** | 자동 (60~120초 내) |
| **DNS** | 엔드포인트 변경 없음 (DNS가 새 Primary를 가리킴) |
| **읽기 트래픽** | Standby에서 읽기 불가 (읽기 확장은 Read Replica 사용) |
| **비용** | 인스턴스 비용의 약 2배 (Standby도 동일 스펙) |
| **페일오버 트리거** | AZ 장애, 인스턴스 장애, 스토리지 장애, 네트워크 장애 |

```bash
# Multi-AZ RDS 인스턴스 생성
aws rds create-db-instance \
  --db-instance-identifier my-prod-db \
  --db-instance-class db.m5.large \
  --engine postgres \
  --engine-version 16.4 \
  --master-username admin \
  --master-user-password 'SecurePassword123!' \
  --allocated-storage 100 \
  --max-allocated-storage 500 \
  --storage-type gp3 \
  --multi-az \
  --db-subnet-group-name my-db-subnet-group \
  --vpc-security-group-ids sg-rds123

# 기존 단일 AZ → Multi-AZ로 변환 (운영 중 가능, 일시적 성능 저하 있음)
aws rds modify-db-instance \
  --db-instance-identifier my-db \
  --multi-az \
  --apply-immediately
```

---

## 7. Read Replica

### 7.1 읽기 확장이 필요한 이유

대부분의 웹 애플리케이션은 **읽기 트래픽이 쓰기 트래픽의 5~10배**이다. 상품 목록 조회, 게시글 읽기, 검색 등이 모두 읽기이다. 하나의 DB 인스턴스로 모든 읽기/쓰기를 처리하면 성능 병목이 발생한다.

Read Replica(*Read Replica - Primary DB의 비동기식 복제본으로, 읽기 전용 트래픽을 분산하는 데 사용한다. 쓰기는 Primary에서만 가능하다*)는 이 문제를 해결한다.

### 7.2 Multi-AZ vs Read Replica

이 두 개념을 혼동하기 쉽다. 목적이 완전히 다르다.

| 특성 | Multi-AZ | Read Replica |
|------|----------|-------------|
| **목적** | 고가용성 (장애 대비) | 읽기 성능 확장 |
| **복제 방식** | 동기식 | 비동기식 |
| **읽기 가능** | Standby에서 불가 | Replica에서 가능 |
| **쓰기 가능** | Primary에서만 | Primary에서만 |
| **자동 페일오버** | 있음 | 없음 (수동 승격 가능) |
| **리전** | 같은 리전 내 다른 AZ | 같은 리전 또는 다른 리전 |
| **개수** | 1개 (Standby) | 최대 5개 |

```
Multi-AZ + Read Replica 조합:

┌─── AZ-a ──────────┐  ┌─── AZ-b ──────────┐  ┌─── AZ-c ──────────┐
│                    │  │                    │  │                    │
│  ┌── Primary ───┐  │  │  ┌── Standby ───┐  │  │  ┌── Replica ──┐  │
│  │ 읽기 + 쓰기  │──┼──┼→│ 대기 (동기)   │  │  │  │ 읽기 전용   │  │
│  │              │──┼──┼──┼──────────────┼──┼──┼→│ (비동기)    │  │
│  └──────────────┘  │  │  └──────────────┘  │  │  └─────────────┘  │
│                    │  │                    │  │                    │
└────────────────────┘  └────────────────────┘  └────────────────────┘

앱 서버:
  쓰기(INSERT/UPDATE/DELETE) → Primary 엔드포인트
  읽기(SELECT)              → Replica 엔드포인트
```

### 7.3 Read Replica 생성

```bash
# Read Replica 생성
aws rds create-db-instance-read-replica \
  --db-instance-identifier my-db-replica-1 \
  --source-db-instance-identifier my-prod-db \
  --db-instance-class db.r5.large \
  --availability-zone ap-northeast-2c

# 다른 리전에 Read Replica 생성 (재해 복구 + 글로벌 읽기 분산)
aws rds create-db-instance-read-replica \
  --db-instance-identifier my-db-replica-us \
  --source-db-instance-identifier arn:aws:rds:ap-northeast-2:123456789012:db:my-prod-db \
  --db-instance-class db.r5.large \
  --region us-east-1
```

> **실무 팁**: Read Replica는 비동기 복제이므로 **복제 지연(*Replication Lag - Primary에 쓴 데이터가 Replica에 반영되기까지 걸리는 시간*)이 발생할 수 있다.** 보통 수백 밀리초에서 수 초 수준이다. 따라서 "방금 글을 작성한 사용자가 즉시 자기 글을 조회"하는 패턴에서는 Replica가 아닌 Primary에서 읽어야 한다. 이를 **읽기 후 쓰기 일관성(*Read-after-Write Consistency*)** 전략이라고 한다.

---

## 8. 백업과 복구

### 8.1 자동 백업

RDS는 두 가지 백업 메커니즘을 제공한다.

| 방식 | 설명 | 보존 기간 | 비용 |
|------|------|----------|------|
| **자동 백업** | 매일 지정된 백업 창(시간)에 전체 백업 + 5분 간격 트랜잭션 로그 | 1~35일 (기본 7일) | 할당 스토리지까지 무료 |
| **수동 스냅샷** | 사용자가 원하는 시점에 수동으로 생성 | 삭제할 때까지 영구 보존 | 스냅샷 크기만큼 과금 |

```bash
# 자동 백업 설정 (백업 보존 기간 14일, 백업 창 03:00~04:00 UTC)
aws rds modify-db-instance \
  --db-instance-identifier my-prod-db \
  --backup-retention-period 14 \
  --preferred-backup-window "03:00-04:00" \
  --apply-immediately

# 수동 스냅샷 생성
aws rds create-db-snapshot \
  --db-instance-identifier my-prod-db \
  --db-snapshot-identifier my-db-snapshot-2024-01-15
```

### 8.2 특정 시점 복구 (Point-in-Time Recovery)

자동 백업이 활성화되어 있으면, 보존 기간 내의 **아무 시점으로든 복구**할 수 있다. 이것이 RDS 백업의 가장 강력한 기능이다. "오늘 오후 2시 30분에 실수로 테이블을 DROP했다"는 상황에서 2시 29분 상태로 복구할 수 있다.

```bash
# 특정 시점으로 복구 (새 인스턴스로 생성됨)
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier my-prod-db \
  --target-db-instance-identifier my-db-restored \
  --restore-time "2024-01-15T14:29:00Z" \
  --db-instance-class db.m5.large \
  --db-subnet-group-name my-db-subnet-group

# 스냅샷에서 복구 (새 인스턴스로 생성됨)
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier my-db-from-snapshot \
  --db-snapshot-identifier my-db-snapshot-2024-01-15 \
  --db-instance-class db.m5.large \
  --db-subnet-group-name my-db-subnet-group
```

> **핵심 통찰**: RDS의 복구는 항상 **새 인스턴스를 생성**한다. 기존 인스턴스를 "덮어쓰기"하는 것이 아니다. 복구된 인스턴스에서 데이터를 확인한 후, 필요한 데이터만 기존 DB로 옮기거나, DNS 엔드포인트를 새 인스턴스로 전환하는 방식으로 운영한다.

---

## 9. 파라미터 그룹

### 9.1 파라미터 그룹이란

파라미터 그룹(*Parameter Group - DB 엔진의 설정값을 모아둔 컨테이너. my.cnf(MySQL)나 postgresql.conf(PostgreSQL)의 설정을 AWS 콘솔이나 CLI로 관리할 수 있게 한 것*)은 DB 엔진의 동작을 커스터마이징하는 방법이다.

EC2에 직접 DB를 설치하면 설정 파일을 편집하지만, RDS에서는 OS에 접근할 수 없으므로 파라미터 그룹을 통해 설정을 변경한다.

### 9.2 주요 커스터마이징 예시

| 파라미터 | 엔진 | 기본값 | 변경 이유 |
|---------|------|--------|----------|
| `max_connections` | PostgreSQL | 인스턴스 크기에 따라 다름 | 동시 연결 수 조절 |
| `shared_buffers` | PostgreSQL | 인스턴스 메모리의 25% | 캐시 성능 조절 |
| `log_min_duration_statement` | PostgreSQL | -1 (비활성) | 슬로우 쿼리 로깅 활성화 |
| `timezone` | PostgreSQL/MySQL | UTC | 타임존 변경 |
| `character_set_server` | MySQL | latin1 | UTF-8로 변경 |

```bash
# 커스텀 파라미터 그룹 생성
aws rds create-db-parameter-group \
  --db-parameter-group-name my-postgres-params \
  --db-parameter-group-family postgres16 \
  --description "Custom parameters for my app"

# 파라미터 변경 (슬로우 쿼리 로깅: 1초 이상 걸리는 쿼리 기록)
aws rds modify-db-parameter-group \
  --db-parameter-group-name my-postgres-params \
  --parameters \
    "ParameterName=log_min_duration_statement,ParameterValue=1000,ApplyMethod=immediate" \
    "ParameterName=timezone,ParameterValue=Asia/Seoul,ApplyMethod=immediate"

# 파라미터 그룹을 인스턴스에 적용
aws rds modify-db-instance \
  --db-instance-identifier my-prod-db \
  --db-parameter-group-name my-postgres-params \
  --apply-immediately
```

> **실무 팁**: 기본 파라미터 그룹은 수정할 수 없다. RDS 인스턴스를 생성할 때 반드시 **커스텀 파라미터 그룹을 먼저 만들어서 연결**하라. 나중에 파라미터를 변경해야 할 때 기본 그룹에서 커스텀 그룹으로 전환하면 재부팅이 필요하다. 처음부터 커스텀 그룹을 사용하면 이런 번거로움을 피할 수 있다.

---

## 10. RDS Proxy

### 10.1 왜 필요한가

데이터베이스 연결(*Connection - 애플리케이션과 DB 사이에 맺는 네트워크 세션. 각 연결은 DB 서버의 메모리와 CPU를 소비한다*)은 비용이 비싸다. 연결을 맺고 끊는 과정(TCP 핸드셰이크, 인증, 세션 초기화)에 시간이 걸리고, 열려 있는 연결은 DB 메모리를 소비한다.

특히 **Lambda + RDS** 조합에서 문제가 심각해진다.

```
Lambda + RDS (Proxy 없이):

동시 Lambda 호출 100개 → DB 연결 100개 동시 생성
                         ↓
                    DB max_connections 초과!
                    → 연결 거부 에러 발생

Lambda는 요청마다 새 실행 환경을 생성하고,
각 환경이 독립적으로 DB 연결을 맺기 때문에
연결 수가 폭발적으로 증가한다.
```

### 10.2 RDS Proxy의 역할

RDS Proxy(*RDS Proxy - 애플리케이션과 RDS 사이에 위치하여 데이터베이스 연결을 풀링하고 관리하는 완전관리형 프록시 서비스*)는 연결 풀링(*Connection Pooling - DB 연결을 미리 만들어두고 재사용하는 기법*)을 AWS 인프라 수준에서 제공한다.

```
RDS Proxy 동작:

Lambda 함수 100개 ─┐
Lambda 함수 200개 ─┤
Lambda 함수 300개 ─┤      ┌─── RDS Proxy ───┐      ┌─── RDS ──────┐
ECS Task 10개    ─┤      │                  │      │              │
EC2 인스턴스 5개  ─┘      │  연결 풀 관리     │      │  실제 연결    │
                  │      │  (수백 개 요청을  │──→──→│  20~30개만   │
   애플리케이션    │──→──→│   20~30개 연결로  │      │  유지         │
   연결 요청 615개 │      │   다중화)         │      │              │
                         └──────────────────┘      └──────────────┘
```

### 10.3 RDS Proxy 설정

```bash
# RDS Proxy 생성
aws rds create-db-proxy \
  --db-proxy-name my-app-proxy \
  --engine-family POSTGRESQL \
  --auth '[{
    "AuthScheme": "SECRETS",
    "SecretArn": "arn:aws:secretsmanager:ap-northeast-2:123456789012:secret:my-db-creds",
    "IAMAuth": "DISABLED"
  }]' \
  --role-arn arn:aws:iam::123456789012:role/rds-proxy-role \
  --vpc-subnet-ids subnet-az-a subnet-az-b \
  --vpc-security-group-ids sg-proxy123

# 타겟 그룹에 RDS 인스턴스 등록
aws rds register-db-proxy-targets \
  --db-proxy-name my-app-proxy \
  --db-instance-identifiers my-prod-db
```

### 10.4 Lambda에서 RDS Proxy 연결

RDS Proxy를 사용하면 Lambda에서 RDS에 연결할 때 **Proxy 엔드포인트**를 사용한다. 기존 연결 코드를 거의 변경하지 않아도 된다.

```typescript
// Lambda에서 RDS Proxy를 통해 PostgreSQL 연결
import { Client } from 'pg';

const client = new Client({
  host: 'my-app-proxy.proxy-xxxxxx.ap-northeast-2.rds.amazonaws.com', // Proxy 엔드포인트
  port: 5432,
  database: 'myapp',
  user: 'admin',
  password: process.env.DB_PASSWORD,
  ssl: { rejectUnauthorized: false },
});

export const handler = async (event: any) => {
  await client.connect();
  try {
    const result = await client.query('SELECT * FROM users WHERE id = $1', [event.userId]);
    return { statusCode: 200, body: JSON.stringify(result.rows[0]) };
  } finally {
    await client.end();
  }
};
```

> **핵심 통찰**: **Lambda + RDS를 사용한다면 RDS Proxy는 사실상 필수이다.** Lambda의 동시 실행 수가 수백~수천에 달하면, DB 연결이 폭발적으로 증가하여 `max_connections` 초과 에러가 발생한다. RDS Proxy는 이 수백 개의 연결 요청을 수십 개의 실제 DB 연결로 다중화하여 문제를 해결한다. ECS나 EC2에서도 연결 관리가 복잡할 때 유용하다.

---

## 11. Node.js에서 RDS 연결하기

### 11.1 Prisma로 PostgreSQL 연결

Prisma(*Prisma - Node.js/TypeScript용 ORM으로, 타입 안전한 쿼리 빌더와 스키마 마이그레이션을 제공한다*)는 현대 Node.js/TypeScript 프로젝트에서 가장 널리 사용되는 ORM이다.

```bash
# Prisma 설치
npm install prisma @prisma/client
npx prisma init
```

```
// prisma/schema.prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

generator client {
  provider = "prisma-client-js"
}

model User {
  id        Int      @id @default(autoincrement())
  email     String   @unique
  name      String
  posts     Post[]
  createdAt DateTime @default(now())
}

model Post {
  id        Int      @id @default(autoincrement())
  title     String
  content   String?
  author    User     @relation(fields: [authorId], references: [id])
  authorId  Int
  createdAt DateTime @default(now())
}
```

```bash
# .env 파일 (RDS 엔드포인트 사용)
DATABASE_URL="postgresql://admin:SecurePassword123@my-prod-db.xxxxxx.ap-northeast-2.rds.amazonaws.com:5432/myapp?schema=public"

# RDS Proxy 사용 시
DATABASE_URL="postgresql://admin:SecurePassword123@my-app-proxy.proxy-xxxxxx.ap-northeast-2.rds.amazonaws.com:5432/myapp?schema=public"
```

```typescript
// src/db.ts — Prisma 클라이언트 싱글턴
import { PrismaClient } from '@prisma/client';

const globalForPrisma = globalThis as unknown as { prisma: PrismaClient };

export const prisma =
  globalForPrisma.prisma ||
  new PrismaClient({
    log: process.env.NODE_ENV === 'development' ? ['query', 'warn', 'error'] : ['error'],
  });

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma;
```

```typescript
// src/routes/users.ts — 사용 예시
import { prisma } from '../db';

// 사용자 생성
const newUser = await prisma.user.create({
  data: { email: 'user@example.com', name: '홍길동' },
});

// 사용자 조회 (게시글 포함)
const userWithPosts = await prisma.user.findUnique({
  where: { id: 1 },
  include: { posts: true },
});
```

### 11.2 Knex로 PostgreSQL 연결

Knex(*Knex - Node.js용 SQL 쿼리 빌더로, SQL에 가까운 문법으로 쿼리를 작성할 수 있다. ORM보다 SQL에 대한 통제권이 높다*)는 ORM보다 SQL에 가까운 쿼리를 선호할 때 좋은 선택이다.

```typescript
// knexfile.ts
import type { Knex } from 'knex';

const config: Knex.Config = {
  client: 'pg',
  connection: {
    host: process.env.DB_HOST, // RDS 또는 RDS Proxy 엔드포인트
    port: 5432,
    database: 'myapp',
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    ssl: { rejectUnauthorized: false }, // RDS는 SSL 권장
  },
  pool: {
    min: 2,
    max: 10, // EC2/ECS에서는 적절한 풀 사이즈 설정
  },
  migrations: {
    directory: './migrations',
  },
};

export default config;
```

```typescript
// 쿼리 예시
import knex from './knexfile';

// 사용자 조회
const users = await knex('users')
  .select('id', 'email', 'name')
  .where('created_at', '>', '2024-01-01')
  .orderBy('created_at', 'desc')
  .limit(20);

// 트랜잭션
await knex.transaction(async (trx) => {
  const [user] = await trx('users')
    .insert({ email: 'user@example.com', name: '홍길동' })
    .returning('*');

  await trx('posts')
    .insert({ title: '첫 게시글', content: '내용', author_id: user.id });
});
```

### 11.3 연결 보안 (SSL/TLS)

RDS에 연결할 때는 **SSL/TLS를 활성화**하여 전송 중인 데이터를 암호화해야 한다. AWS는 RDS용 CA 인증서를 제공한다.

```typescript
// SSL 연결 설정 (pg 드라이버)
import { Client } from 'pg';
import fs from 'fs';

const client = new Client({
  host: 'my-prod-db.xxxxxx.ap-northeast-2.rds.amazonaws.com',
  port: 5432,
  database: 'myapp',
  user: 'admin',
  password: process.env.DB_PASSWORD,
  ssl: {
    ca: fs.readFileSync('/path/to/global-bundle.pem').toString(), // AWS RDS CA 인증서
    rejectUnauthorized: true,
  },
});
```

```bash
# AWS RDS CA 인증서 번들 다운로드
curl -o global-bundle.pem \
  https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem
```

---

## 12. Aurora

### 12.1 Aurora란

Aurora(*Amazon Aurora - AWS가 자체 개발한 클라우드 네이티브 관계형 데이터베이스 엔진. MySQL 및 PostgreSQL과 호환되면서 최대 5배(MySQL), 3배(PostgreSQL)의 성능을 제공한다*)는 RDS의 "프리미엄 버전"이라고 할 수 있다.

```
일반 RDS vs Aurora 아키텍처:

일반 RDS:
┌─── 인스턴스 ───┐     ┌─── EBS ────┐
│  DB 엔진       │────→│  스토리지   │  ← 단일 EBS 볼륨
│                │     │  (gp3/io1)  │
└────────────────┘     └────────────┘

Aurora:
┌─── 인스턴스 ───┐     ┌─────────────────────────────────┐
│  DB 엔진       │────→│  Aurora 분산 스토리지 클러스터    │
│                │     │  ┌───┐ ┌───┐ ┌───┐              │
│                │     │  │AZ-a│ │AZ-b│ │AZ-c│  ← 3개 AZ  │
│                │     │  │ 2  │ │ 2  │ │ 2  │    6개 복사본│
│                │     │  └───┘ └───┘ └───┘              │
│                │     │  자동 확장 (10 GiB 단위, 최대 128 TiB) │
│                │     └─────────────────────────────────┘
└────────────────┘
```

### 12.2 Aurora의 핵심 장점

| 특성 | 일반 RDS | Aurora |
|------|---------|--------|
| **스토리지** | 단일 EBS (수동 확장) | 3개 AZ에 6개 복사본, 자동 확장 |
| **성능** | 기본 | MySQL 대비 5배, PostgreSQL 대비 3배 |
| **페일오버** | 60~120초 | 30초 이내 |
| **Read Replica** | 최대 5개 | 최대 15개 |
| **복구** | 스냅샷/시점 복구 | 연속 백업 (S3에 자동), 백트래킹 |
| **비용** | 인스턴스 + EBS | 인스턴스 + I/O + 스토리지 (약 20~30% 비쌈) |

### 12.3 Aurora Serverless v2

Aurora Serverless v2(*Aurora Serverless v2 - 워크로드에 따라 자동으로 컴퓨팅 용량을 조절하는 Aurora의 서버리스 모드. ACU 단위로 스케일링된다*)는 트래픽에 따라 **자동으로 DB 컴퓨팅 용량을 확장/축소**한다.

```
Aurora Serverless v2 자동 스케일링:

  ACU (Aurora Capacity Units)
  64  ┤                    ┌─── 트래픽 피크
      │                    │
  32  ┤              ┌─────┤
      │              │     │
  16  ┤         ┌────┤     │
      │         │    │     │
   4  ┤────┬────┤    │     ├────┬────
      │    │    │    │     │    │
 0.5  ┤    │    │    │     │    │     ← 최소 ACU (야간 최저 부하)
      └────┴────┴────┴─────┴────┴────→ 시간

  0.5 ACU (약 1 GiB 메모리) ~ 128 ACU (약 256 GiB 메모리)
  초 단위로 자동 스케일링, 사용한 ACU만큼만 과금
```

| 사용 사례 | Provisioned (고정) | Serverless v2 |
|----------|-------------------|---------------|
| **트래픽 패턴** | 예측 가능, 일정한 부하 | 변동 큼, 예측 어려움 |
| **비용 모델** | 인스턴스 시간당 고정 | 사용한 ACU만큼 |
| **적합한 경우** | 24/7 높은 부하 프로덕션 | 개발/테스트, 간헐적 트래픽 |
| **스케일링** | 수동 (인스턴스 타입 변경) | 자동 (초 단위) |

```bash
# Aurora Serverless v2 클러스터 생성
aws rds create-db-cluster \
  --db-cluster-identifier my-aurora-cluster \
  --engine aurora-postgresql \
  --engine-version 16.4 \
  --master-username admin \
  --master-user-password 'SecurePassword123!' \
  --db-subnet-group-name my-db-subnet-group \
  --vpc-security-group-ids sg-rds123 \
  --serverless-v2-scaling-configuration MinCapacity=0.5,MaxCapacity=16

# Serverless v2 인스턴스 추가
aws rds create-db-instance \
  --db-instance-identifier my-aurora-instance-1 \
  --db-cluster-identifier my-aurora-cluster \
  --db-instance-class db.serverless \
  --engine aurora-postgresql
```

> **비용 주의**: Aurora는 일반 RDS보다 **약 20~30% 비싸다.** 소규모 프로젝트나 개발 환경에서는 일반 RDS PostgreSQL이 비용 효율적이다. Aurora는 **높은 가용성과 성능이 필수인 프로덕션 워크로드**에서 가치를 발휘한다. Serverless v2는 트래픽이 없으면 최소 ACU(0.5 ACU)까지 줄어들지만, 완전히 0으로 내려가지는 않으므로 최소 비용이 발생한다.

---

## 13. 모니터링

### 13.1 CloudWatch 메트릭

RDS는 CloudWatch에 자동으로 메트릭을 전송한다. 별도 에이전트 설치 없이 바로 모니터링할 수 있다.

| 메트릭 | 설명 | 주의 기준 |
|--------|------|----------|
| **CPUUtilization** | CPU 사용률 | 지속적으로 80% 이상이면 인스턴스 업그레이드 고려 |
| **FreeableMemory** | 사용 가능한 메모리 | 급격히 감소하면 쿼리/연결 수 점검 |
| **DatabaseConnections** | 현재 DB 연결 수 | max_connections의 80%에 도달하면 경고 |
| **ReadIOPS / WriteIOPS** | 초당 읽기/쓰기 I/O 횟수 | gp3 기본 IOPS(3,000)에 근접하면 스토리지 업그레이드 |
| **FreeStorageSpace** | 남은 스토리지 용량 | 10% 이하일 때 경고 |
| **ReplicaLag** | Read Replica 복제 지연 | 수 초 이상 지속되면 Replica 성능 점검 |

```bash
# CPU 사용률 80% 이상 시 알람
aws cloudwatch put-metric-alarm \
  --alarm-name rds-high-cpu \
  --metric-name CPUUtilization \
  --namespace AWS/RDS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --evaluation-periods 3 \
  --dimensions Name=DBInstanceIdentifier,Value=my-prod-db \
  --alarm-actions arn:aws:sns:ap-northeast-2:123456789012:ops-alerts

# DB 연결 수 알람
aws cloudwatch put-metric-alarm \
  --alarm-name rds-connections-high \
  --metric-name DatabaseConnections \
  --namespace AWS/RDS \
  --statistic Average \
  --period 300 \
  --threshold 100 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --evaluation-periods 2 \
  --dimensions Name=DBInstanceIdentifier,Value=my-prod-db \
  --alarm-actions arn:aws:sns:ap-northeast-2:123456789012:ops-alerts
```

### 13.2 Performance Insights

Performance Insights(*Performance Insights - RDS 데이터베이스의 성능을 시각적으로 분석하는 도구. 어떤 쿼리가 DB 부하의 원인인지 직관적으로 파악할 수 있다*)는 "DB가 느린데, 어떤 쿼리 때문인지 모르겠다"는 상황에서 핵심 도구이다.

```
Performance Insights 대시보드:

┌─────────────────────────────────────────────────┐
│  DB Load (Average Active Sessions)              │
│                                                 │
│  4 ┤         ████                               │
│    │    ████ ████                               │
│  2 ┤    ████ ████ ████                           │
│    │    ████ ████ ████ ████                       │
│  0 └────┴────┴────┴────┴────→ 시간              │
│                                                 │
│  ■ CPU   ■ IO Wait   ■ Lock Wait                │
│                                                 │
│  Top SQL:                                       │
│  1. SELECT * FROM orders WHERE ... (40% 부하)   │
│  2. UPDATE users SET ... (25% 부하)             │
│  3. INSERT INTO logs ... (15% 부하)             │
└─────────────────────────────────────────────────┘
```

```bash
# Performance Insights 활성화 (인스턴스 생성 시 또는 수정 시)
aws rds modify-db-instance \
  --db-instance-identifier my-prod-db \
  --enable-performance-insights \
  --performance-insights-retention-period 7 \
  --apply-immediately
```

> **실무 팁**: Performance Insights는 **무료 티어(7일 보존)**가 있으므로 반드시 활성화하라. DB 성능 문제가 발생했을 때 "어떤 쿼리가 병목인지" 즉시 파악할 수 있다. 로깅보다 훨씬 직관적이며, 인덱스 추가나 쿼리 최적화의 우선순위를 결정하는 데 핵심적인 데이터를 제공한다.

---

## 14. RDS 인스턴스 생성 전체 실습

지금까지 배운 구성 요소를 조합하여 Node.js 애플리케이션용 PostgreSQL 데이터베이스를 구축하는 전체 과정을 정리한다.

```bash
# 1. DB 서브넷 그룹 생성
aws rds create-db-subnet-group \
  --db-subnet-group-name my-db-subnet-group \
  --db-subnet-group-description "Private subnets for RDS" \
  --subnet-ids '["subnet-private-a", "subnet-private-b"]'

# 2. RDS 보안 그룹 생성
aws ec2 create-security-group \
  --group-name rds-sg \
  --description "RDS security group" \
  --vpc-id vpc-0abc123

# 3. 앱 서버 보안 그룹에서 PostgreSQL(5432) 허용
aws ec2 authorize-security-group-ingress \
  --group-id sg-rds123 \
  --protocol tcp \
  --port 5432 \
  --source-group sg-app123

# 4. 커스텀 파라미터 그룹 생성
aws rds create-db-parameter-group \
  --db-parameter-group-name my-postgres-params \
  --db-parameter-group-family postgres16 \
  --description "Custom PostgreSQL parameters"

# 5. 파라미터 설정 (타임존, 슬로우 쿼리 로깅)
aws rds modify-db-parameter-group \
  --db-parameter-group-name my-postgres-params \
  --parameters \
    "ParameterName=timezone,ParameterValue=Asia/Seoul,ApplyMethod=immediate" \
    "ParameterName=log_min_duration_statement,ParameterValue=1000,ApplyMethod=immediate"

# 6. RDS 인스턴스 생성 (Multi-AZ, 자동 백업, Performance Insights)
aws rds create-db-instance \
  --db-instance-identifier my-prod-db \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --engine-version 16.4 \
  --master-username admin \
  --master-user-password 'SecurePassword123!' \
  --allocated-storage 20 \
  --max-allocated-storage 100 \
  --storage-type gp3 \
  --multi-az \
  --db-subnet-group-name my-db-subnet-group \
  --vpc-security-group-ids sg-rds123 \
  --db-parameter-group-name my-postgres-params \
  --backup-retention-period 14 \
  --preferred-backup-window "18:00-19:00" \
  --enable-performance-insights \
  --performance-insights-retention-period 7 \
  --no-publicly-accessible \
  --storage-encrypted \
  --tags Key=Environment,Value=production Key=Project,Value=my-app

# 7. 인스턴스 생성 완료 대기 (5~10분 소요)
aws rds wait db-instance-available \
  --db-instance-identifier my-prod-db

# 8. 엔드포인트 확인
aws rds describe-db-instances \
  --db-instance-identifier my-prod-db \
  --query 'DBInstances[0].Endpoint' \
  --output json
# { "Address": "my-prod-db.xxxxxx.ap-northeast-2.rds.amazonaws.com", "Port": 5432 }

# 9. 앱 서버(EC2/ECS)에서 연결 확인
# psql -h my-prod-db.xxxxxx.ap-northeast-2.rds.amazonaws.com -U admin -d postgres
```

---

## 자주 하는 실수

| 실수 | 설명 | 올바른 접근 |
|------|------|------------|
| **RDS를 퍼블릭 서브넷에 배치** | DB가 인터넷에 노출되어 보안 사고 위험 | 반드시 프라이빗 서브넷에 배치, `--no-publicly-accessible` 사용 |
| **기본 파라미터 그룹 사용** | 나중에 커스터마이징 시 재부팅 필요 | 처음부터 커스텀 파라미터 그룹 생성 후 적용 |
| **Multi-AZ 없이 프로덕션 운영** | Primary 장애 시 수동 복구, 서비스 장시간 중단 | 프로덕션에서는 Multi-AZ 필수 활성화 |
| **Read Replica에서 쓰기 시도** | 읽기 전용이므로 쓰기 쿼리가 에러 발생 | 쓰기는 Primary 엔드포인트, 읽기는 Replica 엔드포인트 분리 |
| **Lambda에서 RDS 직접 연결** | 동시 실행 시 연결 폭발, max_connections 초과 | RDS Proxy를 반드시 사용 |
| **자동 백업 비활성화** | 장애 시 특정 시점 복구 불가능 | 백업 보존 기간 최소 7일 이상 설정 |
| **스토리지 자동 확장 미설정** | 디스크 풀로 DB 중단 | `--max-allocated-storage` 설정하여 자동 확장 활성화 |
| **SSL 없이 연결** | 전송 중 데이터가 암호화되지 않음 | 연결 시 SSL 활성화, `rds.force_ssl` 파라미터로 강제 |
| **인스턴스를 stop 후 방치** | 7일 후 자동 재시작되어 과금 | 학습 환경에서는 삭제 후 스냅샷에서 복원 |
| **마스터 비밀번호 코드에 하드코딩** | 소스 코드 유출 시 DB 접근 가능 | Secrets Manager 또는 환경 변수 사용 |

---

## AWS CLI 레퍼런스

| 명령어 | 설명 |
|--------|------|
| `aws rds create-db-instance --db-instance-identifier ID --engine ENGINE --db-instance-class CLASS` | RDS 인스턴스 생성 |
| `aws rds describe-db-instances --db-instance-identifier ID` | 인스턴스 상세 조회 |
| `aws rds modify-db-instance --db-instance-identifier ID` | 인스턴스 설정 변경 |
| `aws rds delete-db-instance --db-instance-identifier ID --skip-final-snapshot` | 인스턴스 삭제 |
| `aws rds stop-db-instance --db-instance-identifier ID` | 인스턴스 중지 (최대 7일) |
| `aws rds start-db-instance --db-instance-identifier ID` | 인스턴스 시작 |
| `aws rds create-db-instance-read-replica --db-instance-identifier REPLICA --source-db-instance-identifier SOURCE` | Read Replica 생성 |
| `aws rds create-db-snapshot --db-instance-identifier ID --db-snapshot-identifier SNAP` | 수동 스냅샷 생성 |
| `aws rds restore-db-instance-to-point-in-time --source-db-instance-identifier ID --restore-time TIME` | 특정 시점 복구 |
| `aws rds restore-db-instance-from-db-snapshot --db-snapshot-identifier SNAP` | 스냅샷에서 복구 |
| `aws rds create-db-subnet-group --db-subnet-group-name NAME --subnet-ids IDS` | DB 서브넷 그룹 생성 |
| `aws rds create-db-parameter-group --db-parameter-group-name NAME --db-parameter-group-family FAMILY` | 파라미터 그룹 생성 |
| `aws rds modify-db-parameter-group --db-parameter-group-name NAME --parameters PARAMS` | 파라미터 변경 |
| `aws rds create-db-proxy --db-proxy-name NAME --engine-family FAMILY` | RDS Proxy 생성 |
| `aws rds create-db-cluster --db-cluster-identifier ID --engine aurora-postgresql` | Aurora 클러스터 생성 |

---

## 요약

- **RDS**는 AWS의 완전관리형 관계형 데이터베이스 서비스이다. OS 패치, 백업, 고가용성 구성 등 인프라 관리의 대부분을 AWS가 담당하므로 개발자는 스키마 설계와 쿼리 최적화에 집중할 수 있다.
- 6가지 엔진(MySQL, PostgreSQL, MariaDB, Oracle, SQL Server, Aurora)을 지원한다. 새 프로젝트에서는 **PostgreSQL**이 가장 범용적이고 Node.js 생태계와 궁합이 좋다.
- **인스턴스 클래스**는 `db.t3`(버스트, 개발/소규모), `db.m5`(범용, 중규모), `db.r5`(메모리, 대규모) 패밀리로 나뉜다. 작게 시작하고 모니터링 후 확장하라.
- **스토리지**는 gp3를 기본으로 선택하고, `max-allocated-storage`로 자동 확장을 반드시 설정하라.
- RDS는 반드시 **프라이빗 서브넷에 배치**하고, 앱 서버의 보안 그룹에서만 접근을 허용한다.
- **Multi-AZ**는 동기식 복제와 자동 페일오버로 고가용성을 제공한다. 프로덕션에서는 필수이다.
- **Read Replica**는 비동기식 복제본으로 읽기 트래픽을 분산한다. 복제 지연에 주의하라.
- **자동 백업**을 활성화하면 보존 기간 내의 아무 시점으로든 복구할 수 있다 (Point-in-Time Recovery). 복구는 항상 새 인스턴스로 생성된다.
- **파라미터 그룹**으로 DB 엔진 설정을 커스터마이징한다. 처음부터 커스텀 그룹을 생성하여 적용하라.
- **RDS Proxy**는 연결 풀링을 제공하여 Lambda + RDS 조합에서 발생하는 연결 폭발 문제를 해결한다.
- **Aurora**는 MySQL/PostgreSQL 호환의 고성능 엔진이다. Serverless v2는 트래픽에 따라 자동 스케일링되어 변동이 큰 워크로드에 적합하다.
- **Performance Insights**(무료 티어 7일)를 반드시 활성화하여 어떤 쿼리가 성능 병목인지 파악하라.
