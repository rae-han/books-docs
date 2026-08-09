# Chapter 5: Route 53과 DNS 관리: Domain Name System

## 핵심 질문

사용자가 `example.com`을 브라우저에 입력하면 어떤 과정을 거쳐 실제 서버에 도달하는가? AWS Route 53은 DNS를 어떻게 관리하며, 다양한 라우팅 정책으로 트래픽을 어떻게 제어하는가? CloudFront + S3 정적 사이트에 커스텀 도메인과 HTTPS를 적용하려면 무엇이 필요한가?

---

## 1. DNS 기초 개념

### 1.1 DNS란

DNS(*Domain Name System - 사람이 읽을 수 있는 도메인 이름을 컴퓨터가 이해하는 IP 주소로 변환하는 시스템*)는 인터넷의 전화번호부이다. 사람은 `example.com`을 기억하지만, 컴퓨터는 `93.184.216.34` 같은 IP 주소로 통신한다. DNS가 이 둘을 연결해준다.

```
DNS의 역할:

사용자 입력: example.com
                │
                ↓
         ┌──────────┐
         │   DNS    │  "example.com은 93.184.216.34야"
         └──────────┘
                │
                ↓
서버 접속: 93.184.216.34
```

### 1.2 도메인 이름의 구조

도메인 이름은 오른쪽에서 왼쪽으로 계층적으로 읽는다:

```
www.api.example.com.
 │   │     │      │
 │   │     │      └── 루트 도메인 (.)  ← 보이지 않지만 항상 존재
 │   │     └── TLD (Top-Level Domain) ← .com, .net, .kr 등
 │   └── SLD (Second-Level Domain)    ← 사용자가 등록하는 도메인
 └── 서브도메인                         ← 자유롭게 생성 가능
```

| 구성 요소 | 예시 | 설명 |
|-----------|------|------|
| **루트 도메인** | `.` | 모든 도메인의 최상위. 보통 생략됨 |
| **TLD** | `.com`, `.kr`, `.io` | ICANN이 관리하는 최상위 도메인 |
| **SLD** | `example` | 사용자가 등록하는 고유한 이름 |
| **서브도메인** | `www`, `api`, `blog` | 도메인 소유자가 자유롭게 생성 |

### 1.3 DNS 해석(Resolution) 과정

브라우저에 `www.example.com`을 입력했을 때 일어나는 일:

```
DNS 해석 과정:

① 브라우저 ──→ 로컬 DNS 캐시 확인
   │            (이전에 방문한 적 있으면 캐시에서 즉시 반환)
   │
② └──→ OS DNS 캐시 확인 (/etc/hosts 등)
         │
③        └──→ 리졸버(ISP DNS 서버)에 질의
                │
④              └──→ 루트 네임서버 (.)
                      ".com은 누가 관리하지?"
                      │
⑤                    └──→ TLD 네임서버 (.com)
                            "example.com은 누가 관리하지?"
                            │
⑥                          └──→ 권한 네임서버 (Route 53 등)
                                  "www.example.com은 93.184.216.34야"
                                  │
                                  ↓
⑦ 브라우저 ←── IP 주소 반환 ←── 리졸버가 결과 캐싱 후 반환
```

1. **브라우저 캐시**: 최근에 방문한 도메인이면 캐시에서 즉시 반환한다.
2. **OS 캐시**: 브라우저 캐시에 없으면 OS 수준의 DNS 캐시를 확인한다.
3. **리졸버**: 캐시에 없으면 ISP(인터넷 서비스 제공자)의 DNS 서버(*Recursive Resolver - 클라이언트를 대신하여 여러 네임서버에 재귀적으로 질의하는 서버*)에 질의한다.
4. **루트 네임서버**: 전 세계 13개 루트 서버 중 하나에 질의하여 TLD 네임서버 주소를 받는다.
5. **TLD 네임서버**: `.com`을 관리하는 서버에서 해당 도메인의 권한 네임서버 주소를 받는다.
6. **권한 네임서버**: 실제 DNS 레코드를 보유한 서버(Route 53)에서 최종 IP 주소를 받는다.
7. **결과 반환**: 리졸버가 결과를 캐싱하고 브라우저에 반환한다.

### 1.4 TTL (Time To Live)

TTL(*Time To Live - DNS 레코드가 캐시에 유지되는 시간(초)*)은 리졸버가 DNS 응답을 캐시하는 기간을 결정한다.

| TTL 값 | 캐시 기간 | 장점 | 단점 |
|--------|----------|------|------|
| **300** (5분) | 짧음 | 변경 사항이 빠르게 전파 | DNS 질의 횟수 증가 |
| **3600** (1시간) | 중간 | 균형 잡힌 설정 | 변경 전파에 최대 1시간 |
| **86400** (24시간) | 김 | DNS 질의 최소화 | 변경 전파에 최대 24시간 |

> **실무 팁**: DNS 레코드를 변경할 예정이라면, **변경 전에 미리 TTL을 낮춰두라**(예: 300초). 낮은 TTL이 전파된 후 레코드를 변경하면, 전 세계 리졸버가 빠르게 새 값을 가져간다. 변경이 안정된 후 TTL을 다시 높이면 된다.

---

## 2. Route 53 소개

### 2.1 Route 53이란

Route 53(*Amazon Route 53 - AWS의 확장 가능한 DNS 웹 서비스. 도메인 등록, DNS 라우팅, 헬스 체크 기능을 제공한다*)은 AWS의 관리형 DNS 서비스이다. 이름의 유래는 DNS가 사용하는 **TCP/UDP 포트 53**에서 왔으며, 미국 대륙 횡단 고속도로인 Route 66에 빗댄 네이밍이기도 하다.

### 2.2 Route 53의 세 가지 핵심 기능

```
Route 53의 역할:

┌──────────────────────────────────────────────────────┐
│                    Route 53                            │
│                                                        │
│  ① 도메인 등록          ② DNS 라우팅        ③ 헬스 체크  │
│  ┌──────────────┐    ┌──────────────┐   ┌───────────┐  │
│  │ example.com  │    │ A 레코드:     │   │ /health   │  │
│  │ 도메인 구매   │    │ 93.184.216.34│   │ → 200 OK? │  │
│  └──────────────┘    └──────────────┘   └───────────┘  │
└──────────────────────────────────────────────────────┘
```

| 기능 | 설명 | 예시 |
|------|------|------|
| **도메인 등록** | 도메인을 직접 구매하고 관리 | `my-app.com`을 $12/년에 등록 |
| **DNS 라우팅** | 도메인에 대한 DNS 질의에 응답 | `my-app.com` → ALB IP 주소 |
| **헬스 체크** | 리소스의 상태를 모니터링하고, 장애 시 트래픽 전환 | 서버가 다운되면 대체 서버로 전환 |

### 2.3 왜 Route 53인가

다른 DNS 서비스(Cloudflare, GoDaddy 등) 대신 Route 53을 사용하는 이유:

| 이유 | 설명 |
|------|------|
| **AWS 통합** | ALB, CloudFront, S3 등 AWS 리소스와 Alias 레코드로 직접 연결 |
| **100% SLA** | AWS 서비스 중 유일하게 100% 가용성 SLA를 보장 |
| **글로벌 Anycast** | 전 세계 어디서든 가장 가까운 DNS 서버가 응답 |
| **헬스 체크 통합** | DNS 수준에서 장애 감지 및 자동 전환(Failover) |

> **비용 주의**: Route 53은 **Free Tier에 포함되지 않는다.** 호스팅 영역당 **$0.50/월**, DNS 질의 100만 건당 **$0.40**이 과금된다. 도메인 등록비는 TLD에 따라 다르다(`.com`은 $13/년, `.io`는 $39/년 등). 학습 목적이라면 호스팅 영역을 하나만 만들고 불필요하면 삭제하라.

---

## 3. 호스팅 영역 (Hosted Zone)

### 3.1 호스팅 영역이란

호스팅 영역(*Hosted Zone - 특정 도메인에 대한 DNS 레코드의 컨테이너. Route 53에서 도메인의 트래픽을 라우팅하는 방법을 정의한다*)은 도메인의 DNS 레코드를 모아 관리하는 컨테이너이다.

### 3.2 퍼블릭 vs 프라이빗 호스팅 영역

| 유형 | 응답 대상 | 사용 사례 |
|------|----------|----------|
| **퍼블릭** | 인터넷 전체 | 웹사이트, 공개 API |
| **프라이빗** | 특정 VPC 내부만 | 내부 마이크로서비스 간 통신 |

**퍼블릭 호스팅 영역**: `example.com`에 대한 DNS 질의가 인터넷 어디에서든 응답된다.

```bash
# 퍼블릭 호스팅 영역 생성
aws route53 create-hosted-zone \
  --name example.com \
  --caller-reference "2024-01-01-initial"
# caller-reference: 중복 생성 방지를 위한 고유 문자열
```

**프라이빗 호스팅 영역**: VPC 내부에서만 DNS 질의에 응답한다. 예를 들어 `db.internal.example.com`이라는 이름으로 내부 RDS 인스턴스에 접근할 수 있다.

```bash
# 프라이빗 호스팅 영역 생성
aws route53 create-hosted-zone \
  --name internal.example.com \
  --caller-reference "2024-01-01-internal" \
  --vpc VPCRegion=ap-northeast-2,VPCId=vpc-0abc123 \
  --hosted-zone-config PrivateZone=true
```

```
퍼블릭 vs 프라이빗 호스팅 영역:

인터넷 사용자 ──→ [퍼블릭 호스팅 영역]
                  example.com → CloudFront
                  api.example.com → ALB

VPC 내부 서비스 ──→ [프라이빗 호스팅 영역]
                    db.internal.example.com → RDS 엔드포인트
                    cache.internal.example.com → ElastiCache
                    ※ 인터넷에서는 해석 불가
```

### 3.3 호스팅 영역 생성 시 자동 생성되는 레코드

호스팅 영역을 생성하면 두 가지 레코드가 자동으로 만들어진다:

| 레코드 | 역할 |
|--------|------|
| **NS** (Name Server) | 이 도메인의 권한 네임서버 4개를 지정 |
| **SOA** (Start of Authority) | 도메인의 관리 정보 (시리얼 번호, TTL 등) |

이 두 레코드는 **절대 삭제하면 안 된다.** DNS 해석이 완전히 중단된다.

---

## 4. DNS 레코드 타입

### 4.1 주요 레코드 타입

| 레코드 타입 | 용도 | 값 예시 |
|------------|------|--------|
| **A** | 도메인 → IPv4 주소 | `93.184.216.34` |
| **AAAA** | 도메인 → IPv6 주소 | `2001:0db8:85a3::8a2e:0370:7334` |
| **CNAME** | 도메인 → 다른 도메인(별칭) | `www.example.com` → `example.com` |
| **Alias** | 도메인 → AWS 리소스 (Route 53 고유) | `example.com` → `d1234.cloudfront.net` |
| **MX** | 이메일 수신 서버 지정 | `10 mail.example.com` |
| **TXT** | 텍스트 정보 저장 (인증, SPF 등) | `"v=spf1 include:_spf.google.com ~all"` |
| **NS** | 도메인의 네임서버 지정 | `ns-123.awsdns-45.com` |
| **SOA** | 도메인 관리 정보 | 시리얼 번호, 갱신 간격 등 |

### 4.2 A 레코드

A 레코드는 가장 기본적인 DNS 레코드로, 도메인을 IPv4 주소에 매핑한다.

```bash
# A 레코드 생성 (JSON 파일로)
cat > /tmp/a-record.json << 'EOF'
{
  "Changes": [
    {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "api.example.com",
        "Type": "A",
        "TTL": 300,
        "ResourceRecords": [
          { "Value": "54.123.45.67" }
        ]
      }
    }
  ]
}
EOF

aws route53 change-resource-record-sets \
  --hosted-zone-id Z0123456789 \
  --change-batch file:///tmp/a-record.json
```

### 4.3 CNAME 레코드

CNAME(*Canonical Name - 도메인을 다른 도메인으로 매핑하는 레코드. 최종적으로 A 레코드를 따라가서 IP를 해석한다*)은 도메인의 별칭을 만든다.

```
CNAME 해석 과정:

www.example.com ──CNAME──→ example.com ──A──→ 93.184.216.34

blog.example.com ──CNAME──→ my-blog.herokuapp.com ──A──→ 52.xx.xx.xx
```

**CNAME의 제약 사항:**

- **Zone Apex(루트 도메인)에 사용할 수 없다.** `example.com`에 CNAME을 설정할 수 없다. `www.example.com`처럼 서브도메인에만 사용 가능하다.
- 이 제약은 RFC 1034의 규칙이다. CNAME이 존재하면 같은 이름에 다른 레코드(MX, NS 등)가 있을 수 없는데, 루트 도메인에는 반드시 NS, SOA 레코드가 있어야 하기 때문이다.

### 4.4 MX 레코드

MX(*Mail Exchange - 도메인으로 수신되는 이메일을 처리할 메일 서버를 지정하는 레코드*)는 이메일 라우팅을 담당한다.

```bash
# Google Workspace 메일 설정 예시
cat > /tmp/mx-record.json << 'EOF'
{
  "Changes": [
    {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "example.com",
        "Type": "MX",
        "TTL": 3600,
        "ResourceRecords": [
          { "Value": "1 ASPMX.L.GOOGLE.COM" },
          { "Value": "5 ALT1.ASPMX.L.GOOGLE.COM" },
          { "Value": "5 ALT2.ASPMX.L.GOOGLE.COM" }
        ]
      }
    }
  ]
}
EOF
```

숫자(`1`, `5`)는 **우선순위**이다. 값이 낮을수록 우선 사용된다.

### 4.5 TXT 레코드

TXT 레코드는 도메인에 텍스트 정보를 저장한다. 주로 **도메인 소유권 인증**과 **이메일 보안 설정**에 사용된다.

| 용도 | TXT 값 예시 |
|------|------------|
| **도메인 소유권 인증** | `"google-site-verification=abc123..."` |
| **SPF (이메일 발신 서버 인증)** | `"v=spf1 include:_spf.google.com ~all"` |
| **DKIM (이메일 서명)** | `"v=DKIM1; k=rsa; p=MIGfMA0..."` |
| **DMARC (이메일 정책)** | `"v=DMARC1; p=quarantine; rua=mailto:..."` |

---

## 5. AWS Alias 레코드

### 5.1 Alias 레코드란

Alias 레코드는 Route 53에서만 제공하는 **AWS 고유의 DNS 확장**이다. CNAME과 비슷하게 도메인을 다른 도메인으로 매핑하지만, 근본적인 차이가 있다.

### 5.2 Alias vs CNAME

| 특성 | CNAME | Alias |
|------|-------|-------|
| **Zone Apex 사용** | 불가 (`example.com`에 설정 불가) | **가능** (`example.com`에 설정 가능) |
| **DNS 질의 비용** | 과금됨 | **무료** (AWS 리소스를 대상으로 할 때) |
| **해석 속도** | 추가 DNS 질의 필요 (CNAME → A) | Route 53이 내부적으로 즉시 IP 반환 |
| **대상** | 모든 도메인 | AWS 리소스만 (CloudFront, ALB, S3 등) |
| **TTL 설정** | 직접 설정 | AWS가 자동 관리 |

```
CNAME 해석 (2단계):
www.example.com ──CNAME──→ d1234.cloudfront.net ──A──→ IP

Alias 해석 (1단계):
example.com ──Alias──→ d1234.cloudfront.net (Route 53이 즉시 IP 반환)
```

### 5.3 Alias 레코드 대상 AWS 리소스

Alias 레코드를 사용할 수 있는 AWS 리소스:

| 리소스 | Alias 대상 |
|--------|-----------|
| **CloudFront 배포** | `d1234.cloudfront.net` |
| **ALB/NLB** | `my-alb-123456.ap-northeast-2.elb.amazonaws.com` |
| **S3 정적 웹사이트** | `my-bucket.s3-website.ap-northeast-2.amazonaws.com` |
| **Elastic Beanstalk** | `my-env.ap-northeast-2.elasticbeanstalk.com` |
| **API Gateway** | `d-abc123.execute-api.ap-northeast-2.amazonaws.com` |
| **같은 호스팅 영역의 다른 레코드** | 같은 도메인 내 다른 레코드 참조 |

> **핵심 통찰**: AWS 리소스를 도메인에 연결할 때는 **CNAME 대신 항상 Alias를 사용하라.** Zone Apex에도 사용할 수 있고, DNS 질의 비용이 무료이며, 해석 속도도 빠르다. CNAME은 AWS 외부 서비스(Heroku, Vercel 등)를 연결할 때만 사용한다.

### 5.4 Alias 레코드 생성

```bash
# CloudFront 배포에 Alias 레코드 연결
cat > /tmp/alias-record.json << 'EOF'
{
  "Changes": [
    {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "example.com",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "Z2FDTNDATAQYW2",
          "DNSName": "d1234abcdef.cloudfront.net",
          "EvaluateTargetHealth": false
        }
      }
    }
  ]
}
EOF

aws route53 change-resource-record-sets \
  --hosted-zone-id Z0123456789 \
  --change-batch file:///tmp/alias-record.json
```

`HostedZoneId`는 대상 AWS 서비스마다 고정된 값이 있다:

| 서비스 | HostedZoneId |
|--------|-------------|
| **CloudFront** | `Z2FDTNDATAQYW2` (글로벌 고정) |
| **S3 웹사이트 (서울)** | `Z3W03O7B5YMIYP` |
| **ALB (서울)** | `ZWKZPGTI48KDX` |

---

## 6. 라우팅 정책

Route 53은 단순히 도메인을 IP에 매핑하는 것을 넘어, **어떤 기준으로 트래픽을 라우팅할지** 정책을 설정할 수 있다.

### 6.1 라우팅 정책 비교

| 정책 | 기준 | 사용 사례 |
|------|------|----------|
| **Simple** | 없음 (기본) | 단일 리소스에 트래픽 전달 |
| **Weighted** | 가중치 비율 | A/B 테스트, 점진적 배포 |
| **Latency** | 지연 시간 | 글로벌 사용자에게 가장 빠른 리전으로 라우팅 |
| **Failover** | 헬스 체크 | Active-Passive 장애 대응 |
| **Geolocation** | 사용자 위치 | 국가/대륙별 콘텐츠 제공, 규제 준수 |

### 6.2 Simple 라우팅

가장 기본적인 정책이다. 하나의 도메인을 하나(또는 여러 개)의 리소스로 연결한다. 여러 IP를 지정하면 랜덤으로 반환한다.

```bash
# Simple 라우팅 - 단일 IP
cat > /tmp/simple.json << 'EOF'
{
  "Changes": [
    {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "app.example.com",
        "Type": "A",
        "TTL": 300,
        "ResourceRecords": [
          { "Value": "54.123.45.67" }
        ]
      }
    }
  ]
}
EOF
```

### 6.3 Weighted 라우팅

트래픽을 **비율**로 분배한다. 새 버전을 점진적으로 롤아웃하거나 A/B 테스트에 유용하다.

```
Weighted 라우팅:

app.example.com
    │
    ├── 70% ──→ 서버 A (v1.0 - 기존 버전)
    │
    └── 30% ──→ 서버 B (v2.0 - 새 버전)
```

```bash
# 서버 A에 70% 트래픽
cat > /tmp/weighted-a.json << 'EOF'
{
  "Changes": [
    {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "app.example.com",
        "Type": "A",
        "SetIdentifier": "server-a",
        "Weight": 70,
        "TTL": 300,
        "ResourceRecords": [
          { "Value": "54.123.45.67" }
        ]
      }
    }
  ]
}
EOF

# 서버 B에 30% 트래픽
cat > /tmp/weighted-b.json << 'EOF'
{
  "Changes": [
    {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "app.example.com",
        "Type": "A",
        "SetIdentifier": "server-b",
        "Weight": 30,
        "TTL": 300,
        "ResourceRecords": [
          { "Value": "54.123.45.89" }
        ]
      }
    }
  ]
}
EOF
```

> **실무 팁**: Weighted 라우팅으로 새 버전을 배포할 때는 **Weight를 0 → 10 → 50 → 100** 순서로 점진적으로 올리라. Weight를 0으로 설정하면 해당 레코드로 트래픽이 전혀 가지 않으므로, 긴급 롤백 시에도 유용하다. 단, 모든 레코드의 Weight가 0이면 모든 레코드에 동일하게 분배된다.

### 6.4 Latency 라우팅

사용자에게 **가장 낮은 지연 시간**을 제공하는 리전으로 트래픽을 라우팅한다. 글로벌 서비스에서 사용자 경험을 최적화할 때 필수적이다.

```
Latency 라우팅:

한국 사용자 ──→ 서울 리전 (ap-northeast-2)   ← 지연 ~5ms
미국 사용자 ──→ 버지니아 리전 (us-east-1)     ← 지연 ~10ms
유럽 사용자 ──→ 프랑크푸르트 리전 (eu-west-1)  ← 지연 ~15ms
```

```bash
# 서울 리전 레코드
cat > /tmp/latency-seoul.json << 'EOF'
{
  "Changes": [
    {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "api.example.com",
        "Type": "A",
        "SetIdentifier": "seoul",
        "Region": "ap-northeast-2",
        "TTL": 300,
        "ResourceRecords": [
          { "Value": "54.180.xx.xx" }
        ]
      }
    }
  ]
}
EOF
```

### 6.5 Failover 라우팅

헬스 체크와 연동하여, 주 서버(*Primary*)가 다운되면 자동으로 대체 서버(*Secondary*)로 트래픽을 전환한다.

```
Failover 라우팅:

정상 시:
app.example.com ──→ Primary (EC2/ALB) ✅

장애 시:
app.example.com ──→ Primary (EC2/ALB) ❌ 헬스 체크 실패
                ──→ Secondary (S3 정적 "점검 중" 페이지) ✅
```

```bash
# 헬스 체크 생성
aws route53 create-health-check --caller-reference "primary-hc" \
  --health-check-config '{
    "IPAddress": "54.123.45.67",
    "Port": 443,
    "Type": "HTTPS",
    "ResourcePath": "/health",
    "RequestInterval": 30,
    "FailureThreshold": 3
  }'

# Primary 레코드
cat > /tmp/failover-primary.json << 'EOF'
{
  "Changes": [
    {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "app.example.com",
        "Type": "A",
        "SetIdentifier": "primary",
        "Failover": "PRIMARY",
        "TTL": 60,
        "ResourceRecords": [
          { "Value": "54.123.45.67" }
        ],
        "HealthCheckId": "abcdef12-3456-7890-abcd-ef1234567890"
      }
    }
  ]
}
EOF
```

### 6.6 Geolocation 라우팅

사용자의 **지리적 위치**(대륙 또는 국가)에 따라 트래픽을 라우팅한다. 규제 준수(데이터 주권), 언어별 콘텐츠 제공, 지역별 서비스 제한에 사용한다.

```
Geolocation 라우팅:

한국(KR) 사용자 ──→ 한국어 서비스 서버
일본(JP) 사용자 ──→ 일본어 서비스 서버
기타 사용자     ──→ 영어 기본 서버 (Default)
```

```bash
# 한국 사용자를 서울 서버로
cat > /tmp/geo-kr.json << 'EOF'
{
  "Changes": [
    {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "app.example.com",
        "Type": "A",
        "SetIdentifier": "korea",
        "GeoLocation": {
          "CountryCode": "KR"
        },
        "TTL": 300,
        "ResourceRecords": [
          { "Value": "54.180.xx.xx" }
        ]
      }
    }
  ]
}
EOF
```

> **핵심 통찰**: Geolocation 라우팅을 사용할 때는 **반드시 Default 레코드를 설정하라.** Geolocation 규칙에 매칭되지 않는 위치의 사용자가 있을 수 있고, Default가 없으면 해당 사용자는 DNS 응답을 받지 못한다.

---

## 7. 도메인 등록

### 7.1 Route 53에서 직접 등록

Route 53은 도메인 등록 대행(*Domain Registrar - ICANN의 승인을 받아 도메인 등록을 대행하는 서비스*)도 제공한다. Route 53에서 도메인을 등록하면 호스팅 영역이 자동으로 생성되어 설정이 간편하다.

```bash
# 도메인 가용성 확인
aws route53domains check-domain-availability \
  --domain-name my-awesome-app.com
# 결과: "AVAILABLE" 또는 "UNAVAILABLE"

# 도메인 등록 (콘솔에서 하는 것이 일반적)
aws route53domains register-domain \
  --domain-name my-awesome-app.com \
  --duration-in-years 1 \
  --admin-contact '{
    "FirstName": "Gildong",
    "LastName": "Hong",
    "ContactType": "PERSON",
    "Email": "gildong@example.com",
    "PhoneNumber": "+82.1012345678",
    "CountryCode": "KR",
    "City": "Seoul",
    "State": "Seoul",
    "ZipCode": "06000",
    "AddressLine1": "123 Gangnam"
  }' \
  --tech-contact ... \
  --registrant-contact ...
```

### 7.2 외부에서 등록한 도메인 연결

GoDaddy, Namecheap 등 외부 레지스트라에서 도메인을 이미 등록한 경우, 네임서버만 Route 53으로 변경하면 된다.

```
외부 도메인 → Route 53 연결 과정:

1. Route 53에서 호스팅 영역 생성
   → NS 레코드 4개가 자동 생성됨
   → ns-123.awsdns-45.com
   → ns-456.awsdns-78.org
   → ns-789.awsdns-12.co.uk
   → ns-012.awsdns-34.net

2. 외부 레지스트라의 네임서버 설정에서
   기존 NS를 Route 53의 NS 4개로 변경

3. 전파 대기 (최대 48시간, 보통 몇 시간 내)

4. 이제 Route 53이 도메인의 DNS를 관리
```

```bash
# 1단계: 호스팅 영역 생성
aws route53 create-hosted-zone \
  --name example.com \
  --caller-reference "2024-migration"

# 2단계: 생성된 NS 레코드 확인
aws route53 get-hosted-zone --id Z0123456789
# 출력의 DelegationSet.NameServers 값을 외부 레지스트라에 입력

# 3단계: DNS 전파 확인
dig example.com NS
# Route 53의 네임서버가 응답하면 성공
```

> **실무 팁**: 외부 레지스트라에서 Route 53으로 네임서버를 변경할 때, 기존 DNS 레코드(A, MX, TXT 등)를 Route 53에 **먼저 모두 생성해둔 후** 네임서버를 변경하라. 순서가 반대이면 네임서버 전환 시점에 이메일 수신, 웹사이트 접속 등이 일시적으로 중단될 수 있다.

---

## 8. 실전: CloudFront + S3 정적 사이트에 커스텀 도메인 연결

프론트엔드 개발자가 가장 흔히 접하는 시나리오이다. React/Next.js(정적 빌드)를 S3 + CloudFront로 배포하고, `my-app.com` 같은 커스텀 도메인을 연결하는 전체 흐름을 다룬다.

### 8.1 전체 아키텍처

```
사용자 브라우저
  │
  │  ① https://my-app.com 요청
  ↓
Route 53 (DNS)
  │
  │  ② Alias 레코드 → CloudFront 배포
  ↓
CloudFront (CDN + SSL 종료)
  │
  │  ③ ACM 인증서로 HTTPS 처리
  │  ④ 캐시에 있으면 즉시 반환, 없으면 오리진에 요청
  ↓
S3 버킷 (오리진)
  │
  └── index.html, _next/*, assets/* 등 정적 파일
```

### 8.2 단계별 설정 흐름

```
설정 순서:

1. S3 버킷 생성 + 정적 파일 업로드         (Ch 9에서 상세히 다룸)
2. ACM에서 SSL 인증서 발급                 (아래 섹션 9에서 소개)
3. CloudFront 배포 생성 + 인증서 연결       (Ch 10에서 상세히 다룸)
4. Route 53에서 Alias 레코드 생성           (이 챕터의 핵심)
```

### 8.3 Route 53 Alias 레코드 설정

```bash
# example.com → CloudFront 배포 (Alias A 레코드)
cat > /tmp/custom-domain.json << 'EOF'
{
  "Changes": [
    {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "my-app.com",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "Z2FDTNDATAQYW2",
          "DNSName": "d1234abcdef.cloudfront.net",
          "EvaluateTargetHealth": false
        }
      }
    },
    {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "www.my-app.com",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "Z2FDTNDATAQYW2",
          "DNSName": "d1234abcdef.cloudfront.net",
          "EvaluateTargetHealth": false
        }
      }
    }
  ]
}
EOF

aws route53 change-resource-record-sets \
  --hosted-zone-id Z0123456789 \
  --change-batch file:///tmp/custom-domain.json
```

`my-app.com`(루트 도메인)과 `www.my-app.com`(서브도메인) 모두 같은 CloudFront 배포를 가리킨다. 루트 도메인은 CNAME을 쓸 수 없으므로, Alias가 필수적이다.

### 8.4 CloudFront 배포에 대체 도메인 추가

Route 53에서 도메인을 CloudFront로 연결하려면, CloudFront 배포 설정에도 해당 도메인을 CNAME(대체 도메인)으로 등록해야 한다. 그렇지 않으면 CloudFront가 요청을 거부한다.

```bash
# CloudFront 배포 설정에 커스텀 도메인 추가 (콘솔이 더 편리함)
aws cloudfront update-distribution \
  --id E1234567890 \
  --distribution-config '{
    ...
    "Aliases": {
      "Quantity": 2,
      "Items": ["my-app.com", "www.my-app.com"]
    },
    "ViewerCertificate": {
      "ACMCertificateArn": "arn:aws:acm:us-east-1:123456789012:certificate/abc-123",
      "SSLSupportMethod": "sni-only",
      "MinimumProtocolVersion": "TLSv1.2_2021"
    }
    ...
  }'
```

---

## 9. ACM으로 SSL 인증서 발급 (HTTPS)

### 9.1 ACM이란

ACM(*AWS Certificate Manager - SSL/TLS 인증서를 무료로 발급하고, AWS 서비스에 자동 배포/갱신하는 서비스*)을 사용하면 HTTPS에 필요한 SSL 인증서를 **무료로** 발급받고, **자동으로 갱신**할 수 있다. 보안 심화는 Ch 16에서 다루지만, 커스텀 도메인 연결에 필수적이므로 여기서 기본 흐름을 소개한다.

### 9.2 인증서 발급 흐름

```
ACM 인증서 발급 과정:

1. ACM에서 인증서 요청
   "my-app.com과 *.my-app.com에 대한 인증서를 발급해주세요"

2. 도메인 소유권 검증 (DNS 검증 권장)
   ACM이 제공하는 CNAME 레코드를 Route 53에 추가
   → Route 53이면 콘솔에서 "Create record in Route 53" 클릭 한 번으로 완료

3. AWS가 CNAME 레코드를 확인하여 소유권 인증

4. 인증서 발급 완료 → CloudFront에 연결

5. 이후 ACM이 자동으로 갱신 (CNAME 레코드를 유지하는 한)
```

```bash
# 1. 인증서 요청 (CloudFront용은 반드시 us-east-1 리전!)
aws acm request-certificate \
  --region us-east-1 \
  --domain-name my-app.com \
  --subject-alternative-names "*.my-app.com" \
  --validation-method DNS

# 2. 검증용 CNAME 레코드 확인
aws acm describe-certificate \
  --region us-east-1 \
  --certificate-arn arn:aws:acm:us-east-1:123456789012:certificate/abc-123 \
  --query 'Certificate.DomainValidationOptions'

# 3. 출력된 CNAME을 Route 53에 추가 (또는 콘솔에서 자동 추가)
```

> **핵심 통찰**: CloudFront에서 사용할 ACM 인증서는 **반드시 `us-east-1`(버지니아) 리전**에서 발급해야 한다. 이것은 CloudFront가 글로벌 서비스이므로 us-east-1 리전의 인증서만 인식하기 때문이다. ALB에 사용할 인증서는 ALB가 위치한 리전(예: ap-northeast-2)에서 발급한다. 리전을 잘못 선택하면 인증서가 목록에 나타나지 않으므로 주의하라.

### 9.3 DNS 검증 vs 이메일 검증

| 검증 방법 | 과정 | 자동 갱신 | 권장 여부 |
|-----------|------|----------|----------|
| **DNS 검증** | CNAME 레코드 추가 | 가능 (CNAME 유지 시) | **강력 권장** |
| **이메일 검증** | 도메인 관리자 이메일로 승인 | 불가 (매번 수동 승인) | 비권장 |

---

## 자주 하는 실수

| 실수 | 설명 | 올바른 접근 |
|------|------|------------|
| **루트 도메인에 CNAME 사용** | RFC 위반으로 DNS 해석이 깨짐 | Route 53 Alias 레코드 사용 |
| **ACM 인증서를 서울 리전에서 발급** | CloudFront에서 인증서가 보이지 않음 | CloudFront용은 반드시 `us-east-1`에서 발급 |
| **네임서버 변경 전 레코드 미생성** | DNS 전환 시 서비스 중단 발생 | Route 53에 기존 레코드를 먼저 모두 생성한 후 NS 변경 |
| **NS/SOA 레코드 삭제** | 도메인의 DNS 해석이 완전히 중단 | NS와 SOA 레코드는 절대 삭제하지 않음 |
| **Geolocation에 Default 누락** | 규칙에 매칭되지 않는 위치의 사용자가 접속 불가 | 반드시 Default 레코드 설정 |
| **TTL을 변경 없이 낮추지 않음** | DNS 레코드 변경 후 오래된 캐시로 인해 접속 오류 | 변경 전 TTL을 300초 이하로 낮추고, 전파 후 변경 |
| **호스팅 영역 방치** | 사용하지 않는 호스팅 영역에 $0.50/월 과금 | 불필요한 호스팅 영역 삭제 |
| **CloudFront에 대체 도메인 미등록** | Route 53에서 연결해도 CloudFront가 요청 거부 | CloudFront 배포의 Aliases에 도메인 추가 |

---

## AWS CLI 레퍼런스

| 명령어 | 설명 |
|--------|------|
| `aws route53 create-hosted-zone --name DOMAIN --caller-reference REF` | 호스팅 영역 생성 |
| `aws route53 list-hosted-zones` | 호스팅 영역 목록 조회 |
| `aws route53 get-hosted-zone --id ZONE_ID` | 호스팅 영역 상세 조회 |
| `aws route53 change-resource-record-sets --hosted-zone-id ZONE_ID --change-batch file://FILE` | DNS 레코드 생성/수정/삭제 |
| `aws route53 list-resource-record-sets --hosted-zone-id ZONE_ID` | 레코드 목록 조회 |
| `aws route53 create-health-check --caller-reference REF --health-check-config JSON` | 헬스 체크 생성 |
| `aws route53 delete-hosted-zone --id ZONE_ID` | 호스팅 영역 삭제 |
| `aws route53domains check-domain-availability --domain-name DOMAIN` | 도메인 등록 가능 여부 확인 |
| `aws route53domains register-domain --domain-name DOMAIN --duration-in-years N` | 도메인 등록 |
| `aws acm request-certificate --domain-name DOMAIN --validation-method DNS` | SSL 인증서 요청 |
| `aws acm describe-certificate --certificate-arn ARN` | 인증서 상세 조회 |
| `aws acm list-certificates` | 인증서 목록 조회 |

---

## 요약

- **DNS**는 도메인 이름을 IP 주소로 변환하는 시스템이다. 브라우저 캐시 → OS 캐시 → 리졸버 → 루트 NS → TLD NS → 권한 NS 순서로 해석된다.
- **Route 53**은 AWS의 관리형 DNS 서비스로, 도메인 등록 + DNS 라우팅 + 헬스 체크 기능을 제공한다. 100% 가용성 SLA를 보장하는 유일한 AWS 서비스이다.
- **호스팅 영역**은 도메인의 DNS 레코드 컨테이너이다. 퍼블릭(인터넷 전체 응답)과 프라이빗(VPC 내부 전용)으로 나뉜다.
- **Alias 레코드**는 Route 53 고유의 확장으로, Zone Apex에도 사용할 수 있고 DNS 질의 비용이 무료이다. AWS 리소스를 도메인에 연결할 때는 CNAME 대신 **항상 Alias를 사용하라.**
- **라우팅 정책**: Simple(기본), Weighted(비율 분배), Latency(최저 지연), Failover(장애 전환), Geolocation(위치 기반)을 제공한다.
- **도메인 등록**은 Route 53에서 직접 하거나, 외부 레지스트라에서 등록 후 네임서버만 Route 53으로 변경할 수 있다.
- **CloudFront + S3 정적 사이트**에 커스텀 도메인을 연결하려면: ACM 인증서 발급(us-east-1) → CloudFront에 대체 도메인 + 인증서 설정 → Route 53에서 Alias 레코드 생성.
- **ACM**은 SSL 인증서를 무료로 발급하고 자동 갱신한다. DNS 검증 방식을 사용하면 CNAME 레코드만 유지하면 된다.
- Route 53은 Free Tier에 포함되지 않는다. 호스팅 영역당 **$0.50/월**, 질의 100만 건당 **$0.40**이 과금된다.
