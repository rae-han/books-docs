# AWS 완전 가이드

> **자체 구성 가이드** — AWS 공식 문서 + Well-Architected Framework 기반. 특정 원서 없이 핵심 서비스를 체계적으로 학습하도록 직접 구성

개발자의 관점에서 AWS 핵심 서비스를 체계적으로 다루는 가이드. 클라우드의 기본 개념부터 네트워킹, 컴퓨팅, 스토리지, 데이터베이스, 배포, 보안까지 실무에서 마주치는 AWS의 핵심을 다룬다.

## 책 정보

| 항목 | 내용 |
|------|------|
| **성격** | 자체 구성 가이드 (7 Parts, 16개 챕터) |
| **기반** | AWS 공식 문서 · Well-Architected Framework · 커뮤니티 best practice |
| **예제** | 모든 예제 Node.js/Next.js 기반 |
| **대상 독자** | AWS를 체계적으로 정리하고 싶은 프론트엔드/풀스택 개발자, Next.js를 AWS에 배포하려는 개발자 |
| **사전 지식** | Node.js/npm·터미널 기본, Docker 기초(Ch8 — [Docker 완전 가이드](../docker-complete-guide/README.md) 참고) |

## 개요

프론트엔드 개발자에게 친숙한 서비스(CloudFront·S3·Amplify)를 충분히 다루면서 인프라 전반(VPC·EC2·RDS)을 커버하도록 구성했다. [Docker 완전 가이드](../docker-complete-guide/README.md)와 연결되는 컨테이너 서비스(ECS/Fargate) 챕터를 포함한다.

## 목차

### Part 1: AWS 기초 (Ch 01-03)

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 1 | [AWS와 클라우드 컴퓨팅](ch01-cloud-computing-fundamentals.md) | IaaS/PaaS/SaaS · Well-Architected | 온프레미스 vs 클라우드 — AWS 서비스 지도와 설계 원칙 |
| 2 | [글로벌 인프라와 계정 설정](ch02-global-infrastructure-and-account.md) | 리전 · AZ · 엣지 로케이션 · CLI | 리전/AZ 개념과 계정 초기 설정(빌링 알림·CLI) |
| 3 | [IAM - 접근 제어의 기초](ch03-iam.md) | IAM · 역할 · 정책 · 최소 권한 원칙 | 사용자·그룹·역할·정책 — 모든 AWS 보안의 출발점 |

### Part 2: 네트워킹 (Ch 04-05)

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 4 | [VPC - 가상 네트워크 설계](ch04-vpc.md) | VPC · 서브넷 · NAT 게이트웨이 · CIDR | 모든 리소스가 놓이는 가상 네트워크 설계 |
| 5 | [Route 53과 DNS 관리](ch05-route53-and-dns.md) | DNS · 호스팅 영역 · 라우팅 정책 | 도메인을 리소스에 연결 — 레코드 타입과 라우팅 정책 |

### Part 3: 컴퓨팅 (Ch 06-08)

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 6 | [EC2 - 가상 서버](ch06-ec2.md) | EC2 · 보안 그룹 · EBS · 오토 스케일링 | 전통적 가상 서버 — 인스턴스 타입부터 오토 스케일링까지 |
| 7 | [Lambda - 서버리스 컴퓨팅](ch07-lambda.md) | Lambda · API Gateway · 콜드 스타트 | 서버 없이 함수만 — 트리거·연동·콜드 스타트 대응 |
| 8 | [컨테이너 서비스 - ECS와 Fargate](ch08-container-services.md) | ECS · Fargate · ECR · 태스크 정의 | Docker 이미지를 AWS에서 실행 — Fargate vs EC2 시작 유형 |

### Part 4: 스토리지와 콘텐츠 전달 (Ch 09-10)

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 9 | [S3 - 객체 스토리지](ch09-s3.md) | S3 · 정적 호스팅 · 수명 주기 · 스토리지 클래스 | 객체 스토리지의 모든 것 — 버킷·버전 관리·비용 최적화 |
| 10 | [CloudFront - CDN과 엣지 컴퓨팅](ch10-cloudfront.md) | CloudFront · 캐시 정책 · OAC · Lambda@Edge | 전 세계 캐시 배포 — S3+CloudFront 정적 배포 패턴 |

### Part 5: 데이터베이스 (Ch 11-12)

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 11 | [RDS - 관계형 데이터베이스](ch11-rds.md) | RDS · Multi-AZ · 읽기 전용 복제본 | 관리형 관계형 DB — 고가용성과 읽기 확장 |
| 12 | [DynamoDB와 ElastiCache](ch12-dynamodb-and-elasticache.md) | DynamoDB · 파티션 키 · Redis 캐싱 | NoSQL 모델링과 캐싱 전략 |

### Part 6: 배포와 CI/CD (Ch 13-14)

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 13 | [Amplify - 프론트엔드 배포 플랫폼](ch13-amplify.md) | Amplify · Git 기반 배포 · SSR | Next.js를 가장 쉽게 — Git 연동 자동 배포 |
| 14 | [CI/CD 파이프라인 구축](ch14-cicd-pipeline.md) | CodePipeline · GitHub Actions · ECR 연동 | 코드에서 배포까지 자동화 파이프라인 |

### Part 7: 모니터링과 보안 (Ch 15-16)

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 15 | [CloudWatch - 모니터링과 운영](ch15-cloudwatch.md) | CloudWatch · 메트릭 · 알람 · X-Ray | 메트릭·로그·알람·트레이싱 — 운영 가시성 |
| 16 | [보안 심화](ch16-advanced-security.md) | WAF · Secrets Manager · KMS · ACM | 프로덕션 보안 — 방화벽·비밀 관리·암호화·인증서 |

## 학습 가이드

1. **Part 1~2는 순서대로 필수** — IAM(Ch3)과 VPC(Ch4)는 이후 모든 서비스의 전제
2. **프론트엔드 배포가 목적이면**: Ch9(S3) → Ch10(CloudFront) → Ch13(Amplify) → Ch14(CI/CD)
3. **백엔드/인프라 트랙**: Ch6(EC2) → Ch7(Lambda) → Ch8(ECS) → Ch11~12(DB) → Ch15~16(운영·보안)
4. **Docker 가이드와 병행**: Ch8(ECS/Fargate)은 [Docker 완전 가이드](../docker-complete-guide/README.md) Ch1~4 이후에 읽으면 자연스럽다

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

## 시그니처 요소와 표기 규칙

- `> **실무 팁**:` — 운영 best practice 콜아웃
- `> **비용 주의**:` — AWS 비용 관련 경고 콜아웃
- `## 자주 하는 실수` — 안티패턴과 해결법 테이블
- `## AWS CLI 레퍼런스` — 챕터별 핵심 CLI 명령어 테이블
