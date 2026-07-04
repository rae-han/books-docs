# AWS 완전 가이드

**AWS 핵심 서비스를 체계적으로 학습하는 독자적 가이드** | 공식 문서 + Best Practice 기반

---

## 개요

이 가이드는 개발자의 관점에서 AWS 핵심 서비스를 체계적으로 다룬다. 클라우드의 기본 개념부터 네트워킹, 컴퓨팅, 스토리지, 데이터베이스, 배포, 보안까지 — 실무에서 마주치는 AWS의 핵심을 빠짐없이 다룬다.

### 특징

- 모든 예제는 **Node.js/Next.js** 기반으로 즉시 따라할 수 있게 작성
- AWS 공식 문서와 Well-Architected Framework의 best practice를 반영한 **자체 구성**
- 프론트엔드 개발자에게 친숙한 서비스(CloudFront, S3, Amplify)를 충분히 다루면서 인프라 전반을 커버
- [Docker 완전 가이드](../docker-complete-guide/README.md)와 연결되는 컨테이너 서비스(ECS/Fargate) 챕터 포함

---

## 목차

### Part 1: AWS 기초 (Ch 01-03)

| 챕터 | 제목 | 핵심 주제 |
|------|------|----------|
| [Chapter 1](ch01-cloud-computing-fundamentals.md) | AWS와 클라우드 컴퓨팅: Cloud Computing Fundamentals | 온프레미스 vs 클라우드, IaaS/PaaS/SaaS, AWS 서비스 카테고리, Well-Architected Framework |
| [Chapter 2](ch02-global-infrastructure-and-account.md) | 글로벌 인프라와 계정 설정: Global Infrastructure & Account Setup | Region, AZ, Edge Location, 계정 생성, 빌링 알림, AWS CLI 설정 |
| [Chapter 3](ch03-iam.md) | IAM - 접근 제어의 기초: Identity and Access Management | 사용자, 그룹, 역할, 정책, MFA, 최소 권한 원칙 |

### Part 2: 네트워킹 (Ch 04-05)

| 챕터 | 제목 | 핵심 주제 |
|------|------|----------|
| [Chapter 4](ch04-vpc.md) | VPC - 가상 네트워크 설계: Virtual Private Cloud | VPC, Subnet, Internet Gateway, NAT Gateway, 라우팅 테이블, CIDR |
| [Chapter 5](ch05-route53-and-dns.md) | Route 53과 DNS 관리: Domain Name System | DNS 기초, 호스팅 영역, 레코드 타입, 라우팅 정책, 도메인 등록 |

### Part 3: 컴퓨팅 (Ch 06-08)

| 챕터 | 제목 | 핵심 주제 |
|------|------|----------|
| [Chapter 6](ch06-ec2.md) | EC2 - 가상 서버: Elastic Compute Cloud | 인스턴스 타입, AMI, 키 페어, 보안 그룹, EBS, Elastic IP, Auto Scaling |
| [Chapter 7](ch07-lambda.md) | Lambda - 서버리스 컴퓨팅: Serverless Computing | 함수 작성, 트리거, API Gateway 연동, 콜드 스타트, Lambda@Edge |
| [Chapter 8](ch08-container-services.md) | 컨테이너 서비스 - ECS와 Fargate: Container Services | ECR, Task Definition, Service, Fargate vs EC2 시작 유형 |

### Part 4: 스토리지와 콘텐츠 전달 (Ch 09-10)

| 챕터 | 제목 | 핵심 주제 |
|------|------|----------|
| [Chapter 9](ch09-s3.md) | S3 - 객체 스토리지: Simple Storage Service | 버킷, 객체, 정적 웹사이트 호스팅, 버전 관리, 수명 주기, 스토리지 클래스 |
| [Chapter 10](ch10-cloudfront.md) | CloudFront - CDN과 엣지 컴퓨팅: Content Delivery Network | 배포 생성, 캐시 정책, S3 + CloudFront 정적 배포, Lambda@Edge, OAC |

### Part 5: 데이터베이스 (Ch 11-12)

| 챕터 | 제목 | 핵심 주제 |
|------|------|----------|
| [Chapter 11](ch11-rds.md) | RDS - 관계형 데이터베이스: Relational Database Service | MySQL/PostgreSQL, Multi-AZ, Read Replica, 백업, 파라미터 그룹 |
| [Chapter 12](ch12-dynamodb-and-elasticache.md) | DynamoDB와 ElastiCache: NoSQL and Caching | 파티션 키, 보조 인덱스, 온디맨드 vs 프로비저닝, Redis 캐싱 전략 |

### Part 6: 배포와 CI/CD (Ch 13-14)

| 챕터 | 제목 | 핵심 주제 |
|------|------|----------|
| [Chapter 13](ch13-amplify.md) | Amplify - 프론트엔드 배포 플랫폼: Frontend Deployment | Amplify Hosting, Git 기반 배포, SSR 지원, 환경 변수, 커스텀 도메인 |
| [Chapter 14](ch14-cicd-pipeline.md) | CI/CD 파이프라인 구축: Continuous Integration & Deployment | CodePipeline, CodeBuild, GitHub Actions + AWS, ECR 연동 |

### Part 7: 모니터링과 보안 (Ch 15-16)

| 챕터 | 제목 | 핵심 주제 |
|------|------|----------|
| [Chapter 15](ch15-cloudwatch.md) | CloudWatch - 모니터링과 운영: Monitoring & Observability | 메트릭, 알람, 로그 그룹, 대시보드, X-Ray 트레이싱 |
| [Chapter 16](ch16-advanced-security.md) | 보안 심화: Advanced Security | WAF, Secrets Manager, KMS, ACM(SSL/TLS), 보안 그룹 vs NACL |

---

## 핵심 개념 맵

```
계정/IAM(Ch 1-3) ──────── 보안의 기초
    │
    ├── VPC(Ch 4) ─────── 모든 리소스가 배치되는 네트워크
    │     └── Route 53(Ch 5) ── 도메인 → 리소스 연결
    │
    ├── 컴퓨팅
    │     ├── EC2(Ch 6) ────── 전통적 서버
    │     ├── Lambda(Ch 7) ── 서버리스 함수
    │     └── ECS(Ch 8) ───── 컨테이너 오케스트레이션
    │
    ├── 스토리지 + CDN
    │     ├── S3(Ch 9) ────── 정적 파일/에셋 저장
    │     └── CloudFront(Ch 10) ─ 전 세계 캐시 배포
    │
    ├── 데이터베이스
    │     ├── RDS(Ch 11) ──── 관계형 DB
    │     └── DynamoDB(Ch 12) ─ NoSQL + 캐시
    │
    └── 운영
          ├── Amplify(Ch 13) + CI/CD(Ch 14) ── 배포 자동화
          ├── CloudWatch(Ch 15) ──────────── 모니터링
          └── 보안 심화(Ch 16) ────────────── 프로덕션 보안
```

---

## 대상 독자

- AWS를 처음 접하거나 체계적으로 정리하고 싶은 **프론트엔드/풀스택 개발자**
- Node.js/Next.js 프로젝트를 AWS에 배포하려는 개발자
- 인프라 전반의 기초를 다지고 싶은 개발자

## 사전 지식

- Node.js/npm 기본 사용법
- 터미널/CLI 기본 사용법
- Docker 기초 (컨테이너 서비스 챕터에서 필요, [Docker 완전 가이드](../docker-complete-guide/README.md) 참고)
