# Chapter 10: CloudFront - CDN과 엣지 컴퓨팅: Content Delivery Network

## 핵심 질문

전 세계 사용자에게 웹 콘텐츠를 빠르게 전달하려면 어떻게 해야 하는가? CloudFront는 S3, ALB 등 오리진 서버의 콘텐츠를 엣지 로케이션에서 캐싱하여 어떻게 지연 시간을 줄이는가? S3 정적 사이트에 CloudFront를 연결하고, 캐시를 효율적으로 관리하며, Lambda@Edge와 CloudFront Functions로 엣지에서 로직을 실행하려면 무엇을 알아야 하는가?

---

## 1. CDN이란

### 1.1 CDN이 필요한 이유

CDN(*Content Delivery Network - 전 세계에 분산된 서버 네트워크를 통해 사용자에게 가장 가까운 위치에서 콘텐츠를 전달하는 시스템*)이 없으면, 모든 요청이 오리진 서버까지 직접 도달해야 한다. 서울에 있는 S3 버킷에 호스팅된 웹사이트를 브라질 사용자가 접속한다고 가정하면, 매번 서울까지 왕복하는 데 수백 밀리초가 소요된다.

```
CDN 없이 (모든 요청이 오리진으로):

브라질 사용자 ────── 태평양 횡단 ──────→ 서울 S3 버킷
               ← 200~300ms 왕복 지연 ←

CDN 사용 시 (엣지 로케이션에서 캐시 반환):

브라질 사용자 ──→ 상파울루 엣지 로케이션 (캐시 히트 → 즉시 반환)
               ← 10~20ms ←

                  캐시 미스 시에만 오리진으로 요청
                  상파울루 엣지 ──→ 서울 S3 버킷
                  (이후 캐시에 저장 → 다음 요청부터는 즉시 반환)
```

CDN이 해결하는 세 가지 문제:

| 문제 | CDN 없이 | CDN 사용 시 |
|------|---------|------------|
| **지연 시간** | 모든 사용자가 오리진까지 왕복 | 가장 가까운 엣지에서 반환 |
| **오리진 부하** | 모든 요청이 오리진에 집중 | 캐시 히트 시 오리진에 요청하지 않음 |
| **가용성** | 오리진 장애 시 서비스 중단 | 캐시된 콘텐츠는 오리진 장애 중에도 제공 가능 |

### 1.2 엣지 로케이션에서의 콘텐츠 캐싱

CDN의 핵심 원리는 단순하다. 전 세계 수백 곳에 캐시 서버(엣지 로케이션)를 배치하고, 사용자의 요청을 가장 가까운 엣지 로케이션으로 라우팅한다.

```
CloudFront 캐싱 흐름:

① 사용자 → 가장 가까운 엣지 로케이션에 요청
② 엣지 로케이션이 캐시를 확인
   ├── 캐시 히트 (Cache Hit): 즉시 반환 → ③ 사용자에게 응답
   └── 캐시 미스 (Cache Miss):
       ④ 리전 엣지 캐시 확인
          ├── 히트: 엣지에 캐시 저장 후 반환
          └── 미스: 오리진에 요청
              ⑤ 오리진 → 리전 엣지 캐시 → 엣지 로케이션에 캐시 저장
              ⑥ 사용자에게 응답
```

CloudFront는 AWS의 CDN 서비스로, 전 세계 **600개 이상의 엣지 로케이션**과 **13개의 리전 엣지 캐시**(*Regional Edge Cache - 엣지 로케이션과 오리진 사이에 위치한 더 큰 캐시 계층. 엣지 로케이션에서 캐시가 만료되어도 리전 엣지 캐시에 남아 있으면 오리진까지 가지 않는다*)를 통해 콘텐츠를 전달한다.

---

## 2. CloudFront 핵심 개념

### 2.1 Distribution (배포)

배포(*Distribution - CloudFront의 기본 설정 단위. 어떤 오리진에서 콘텐츠를 가져오고, 어떻게 캐싱하고, 어떤 도메인으로 서비스할지를 정의한다*)는 CloudFront의 최상위 설정 객체이다. 배포를 생성하면 `d1234abcdef.cloudfront.net` 형태의 도메인이 할당된다.

### 2.2 Origin (오리진)

오리진(*Origin - CloudFront가 원본 콘텐츠를 가져오는 서버. S3 버킷, ALB, EC2, 외부 HTTP 서버 등이 될 수 있다*)은 원본 콘텐츠가 저장된 서버이다.

| 오리진 유형 | 설명 | 사용 사례 |
|------------|------|----------|
| **S3 버킷** | 정적 파일 저장소 | 정적 사이트, 이미지, JS/CSS 에셋 |
| **ALB/EC2** | 동적 콘텐츠 서버 | API 서버, SSR 렌더링 |
| **커스텀 오리진** | 외부 HTTP/HTTPS 서버 | 온프레미스 서버, 다른 클라우드 서비스 |
| **MediaStore/MediaPackage** | 미디어 스트리밍 | 라이브/VOD 스트리밍 |

하나의 배포에 **여러 오리진**을 설정할 수 있다. 예를 들어 `/api/*` 요청은 ALB로, `/static/*` 요청은 S3로 라우팅하는 구성이 가능하다.

### 2.3 Behavior (동작)

동작(*Behavior - URL 경로 패턴에 따라 어떤 오리진으로 요청을 전달하고, 어떤 캐시 정책을 적용할지 정의하는 규칙*)은 경로 패턴별로 요청을 다르게 처리하는 규칙이다.

```
Behavior 설정 예시:

CloudFront 배포 (d1234.cloudfront.net)
    │
    ├── 경로: /api/*       → 오리진: ALB (캐시 비활성화)
    ├── 경로: /static/*    → 오리진: S3 (장기 캐시)
    └── 경로: * (기본)      → 오리진: S3 (기본 캐시)
```

### 2.4 Edge Location (엣지 로케이션)

엣지 로케이션(*Edge Location - CloudFront가 콘텐츠를 캐싱하는 전 세계 데이터센터. Chapter 2에서 다룬 AWS 글로벌 인프라의 일부이다*)은 사용자와 가장 가까운 지점에서 콘텐츠를 제공하는 캐시 서버이다.

```
CloudFront의 3-Tier 캐시 계층:

사용자 ──→ [엣지 로케이션] ──→ [리전 엣지 캐시] ──→ [오리진]
           (600+ 지점)         (13 지점)              (1 지점)
           10~20ms             30~50ms                 100~300ms

           캐시 용량: 작음      캐시 용량: 큼           원본 데이터
           TTL: 짧음            TTL: 더 김              항상 최신
```

### 2.5 전체 아키텍처

```
CloudFront 전체 구조:

사용자 브라우저
    │
    │  ① DNS 질의: example.com
    ↓
Route 53 (DNS)
    │
    │  ② Alias → d1234.cloudfront.net
    ↓
CloudFront 엣지 로케이션 (서울)
    │
    │  ③ 캐시 확인
    │  ├── 히트: 즉시 반환
    │  └── 미스:
    ↓
    ├── Behavior: /api/*  →  ALB (서울 리전)
    │                         │
    │                         └── EC2 인스턴스들
    │
    └── Behavior: * (기본) →  S3 버킷 (서울 리전)
                              │
                              └── index.html, *.js, *.css
```

---

## 3. S3 + CloudFront 정적 사이트 배포

프론트엔드 개발자가 가장 자주 접하는 패턴이다. React, Next.js(정적 export), Vue 등의 빌드 결과물을 S3에 업로드하고, CloudFront를 통해 전 세계에 배포한다.

### 3.1 OAC (Origin Access Control)

OAC(*Origin Access Control - CloudFront만 S3 버킷에 접근할 수 있도록 제한하는 메커니즘. S3 버킷의 퍼블릭 접근을 차단하면서도 CloudFront를 통해서는 정상적으로 콘텐츠를 제공할 수 있다*)는 S3 버킷에 대한 직접 접근을 차단하고, CloudFront를 통해서만 콘텐츠를 제공하도록 강제한다.

```
OAC 없이 (비권장):

사용자 ──→ CloudFront ──→ S3 (퍼블릭)     ✅
사용자 ──→ S3 버킷 URL 직접 접근           ✅ ← 위험!

OAC 사용 시 (권장):

사용자 ──→ CloudFront ──→ S3 (프라이빗)    ✅ (OAC 서명으로 인증)
사용자 ──→ S3 버킷 URL 직접 접근           ❌ (403 Forbidden)
```

> **핵심 통찰**: S3 + CloudFront 배포에서는 **반드시 OAC를 설정하라.** S3 버킷을 퍼블릭으로 열어두면 CloudFront를 우회하여 S3에 직접 접근할 수 있고, 이는 (1) 캐시를 거치지 않아 S3 비용이 증가하고, (2) HTTPS나 커스텀 도메인이 적용되지 않으며, (3) 보안 헤더 등 CloudFront에서 추가하는 설정이 무력화된다. OAI(*Origin Access Identity*)는 레거시 방식이며, 새 배포에서는 OAC를 사용해야 한다.

### 3.2 전체 설정 플로우

```
S3 + CloudFront 정적 사이트 배포 순서:

① S3 버킷 생성 (퍼블릭 접근 차단 상태 유지)
    ↓
② 빌드 결과물 업로드 (index.html, *.js, *.css 등)
    ↓
③ CloudFront OAC 생성
    ↓
④ CloudFront 배포 생성 (오리진: S3, OAC 연결)
    ↓
⑤ S3 버킷 정책 업데이트 (CloudFront OAC만 접근 허용)
    ↓
⑥ (선택) ACM 인증서 발급 + 커스텀 도메인 연결
    ↓
⑦ 배포 완료: d1234.cloudfront.net (또는 example.com)
```

### 3.3 단계 1: S3 버킷 생성

```bash
# S3 버킷 생성 (퍼블릭 접근 차단 상태 유지)
aws s3api create-bucket \
  --bucket my-frontend-app \
  --region ap-northeast-2 \
  --create-bucket-configuration LocationConstraint=ap-northeast-2

# 퍼블릭 접근 차단 확인 (기본값이지만 명시적으로)
aws s3api put-public-access-block \
  --bucket my-frontend-app \
  --public-access-block-configuration \
    BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
```

### 3.4 단계 2: 빌드 결과물 업로드

```bash
# React/Next.js 정적 빌드 결과물 업로드
aws s3 sync ./out s3://my-frontend-app \
  --delete \
  --cache-control "public, max-age=31536000, immutable" \
  --exclude "index.html" \
  --exclude "*.json"

# index.html은 짧은 캐시로 별도 업로드
aws s3 cp ./out/index.html s3://my-frontend-app/index.html \
  --cache-control "public, max-age=0, must-revalidate"
```

> **실무 팁**: 정적 에셋(JS, CSS, 이미지)은 파일명에 해시가 포함되어 있으므로(`main.a1b2c3.js`) `max-age=31536000`(1년)으로 설정해도 안전하다. 파일 내용이 변경되면 해시가 바뀌므로 자동으로 새 파일을 가져간다. 반면 `index.html`은 항상 최신 버전을 가져와야 하므로 `max-age=0`으로 설정한다.

### 3.5 단계 3: OAC 생성 및 CloudFront 배포

```bash
# OAC 생성
aws cloudfront create-origin-access-control \
  --origin-access-control-config '{
    "Name": "my-frontend-oac",
    "Description": "OAC for my-frontend-app S3 bucket",
    "SigningProtocol": "sigv4",
    "SigningBehavior": "always",
    "OriginAccessControlOriginType": "s3"
  }'
# 출력에서 OAC ID를 기록: E1XXXXXXXXXXXXXX

# CloudFront 배포 생성 (설정 파일로)
cat > /tmp/cf-distribution.json << 'EOF'
{
  "CallerReference": "my-frontend-app-2024",
  "Comment": "Frontend static site distribution",
  "DefaultCacheBehavior": {
    "TargetOriginId": "S3-my-frontend-app",
    "ViewerProtocolPolicy": "redirect-to-https",
    "CachePolicyId": "658327ea-f89d-4fab-a63d-7e88639e58f6",
    "Compress": true,
    "AllowedMethods": {
      "Quantity": 2,
      "Items": ["GET", "HEAD"]
    }
  },
  "Origins": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "S3-my-frontend-app",
        "DomainName": "my-frontend-app.s3.ap-northeast-2.amazonaws.com",
        "OriginAccessControlId": "E1XXXXXXXXXXXXXX",
        "S3OriginConfig": {
          "OriginAccessIdentity": ""
        }
      }
    ]
  },
  "DefaultRootObject": "index.html",
  "Enabled": true,
  "HttpVersion": "http2and3",
  "PriceClass": "PriceClass_200"
}
EOF

aws cloudfront create-distribution \
  --distribution-config file:///tmp/cf-distribution.json
```

> `CachePolicyId: 658327ea-f89d-4fab-a63d-7e88639e58f6`는 AWS 관리형 정책인 **CachingOptimized**의 ID이다. 정적 사이트에 가장 적합한 기본 캐시 정책이다.

### 3.6 단계 4: S3 버킷 정책 업데이트

CloudFront OAC가 S3에 접근할 수 있도록 버킷 정책을 추가한다.

```bash
cat > /tmp/bucket-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowCloudFrontServicePrincipal",
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudfront.amazonaws.com"
      },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-frontend-app/*",
      "Condition": {
        "StringEquals": {
          "AWS:SourceArn": "arn:aws:cloudfront::123456789012:distribution/E1234567890ABC"
        }
      }
    }
  ]
}
EOF

aws s3api put-bucket-policy \
  --bucket my-frontend-app \
  --policy file:///tmp/bucket-policy.json
```

### 3.7 SPA(Single Page Application) 설정

React, Vue 같은 SPA는 클라이언트 사이드 라우팅을 사용한다. `/about`, `/dashboard` 같은 URL로 직접 접근하면 S3에는 해당 경로의 파일이 없으므로 403/404 에러가 발생한다. CloudFront의 **커스텀 에러 응답**으로 이를 해결한다.

```bash
# 커스텀 에러 응답 설정 (배포 생성 시 또는 업데이트 시)
# 403, 404 에러 → index.html로 리다이렉트
aws cloudfront update-distribution \
  --id E1234567890ABC \
  --if-match ETAG_VALUE \
  --distribution-config '{
    ...
    "CustomErrorResponses": {
      "Quantity": 2,
      "Items": [
        {
          "ErrorCode": 403,
          "ResponsePagePath": "/index.html",
          "ResponseCode": "200",
          "ErrorCachingMinTTL": 10
        },
        {
          "ErrorCode": 404,
          "ResponsePagePath": "/index.html",
          "ResponseCode": "200",
          "ErrorCachingMinTTL": 10
        }
      ]
    }
    ...
  }'
```

---

## 4. 캐시 정책 (Cache Policy)

### 4.1 캐시 정책이란

캐시 정책(*Cache Policy - CloudFront가 콘텐츠를 캐시하는 방법을 정의하는 설정. TTL, 캐시 키에 포함할 헤더/쿼리 스트링/쿠키를 지정한다*)은 "무엇을 캐시하고, 얼마나 오래 유지하고, 어떤 요청을 같은 캐시로 취급할지"를 결정한다.

### 4.2 TTL (Time To Live)

TTL은 캐시된 콘텐츠가 엣지 로케이션에 유지되는 시간이다. CloudFront는 세 가지 TTL 설정을 통해 캐시 수명을 관리한다.

| TTL 설정 | 설명 | 기본값 (CachingOptimized) |
|---------|------|--------------------------|
| **Minimum TTL** | 캐시 최소 유지 시간. 오리진의 `Cache-Control`이 이보다 짧아도 이 값 이상 캐시 | 1초 |
| **Maximum TTL** | 캐시 최대 유지 시간. 오리진의 `Cache-Control`이 이보다 길어도 이 값까지만 캐시 | 31536000초 (1년) |
| **Default TTL** | 오리진이 `Cache-Control` 헤더를 보내지 않을 때 사용하는 기본값 | 86400초 (24시간) |

```
TTL 결정 우선순위:

오리진이 Cache-Control 헤더를 보낸 경우:
  max-age=600 → CloudFront는 600초 동안 캐시
  (단, Minimum TTL ≤ 600 ≤ Maximum TTL 범위 내)

오리진이 Cache-Control 헤더를 보내지 않은 경우:
  Default TTL(86400초) 동안 캐시
```

### 4.3 캐시 키 (Cache Key)

캐시 키(*Cache Key - CloudFront가 캐시된 객체를 식별하는 고유한 값. 같은 캐시 키를 가진 요청은 같은 캐시 응답을 받는다*)는 캐시 히트 여부를 결정하는 핵심 요소이다.

기본 캐시 키는 **URL 경로**만 포함한다. 추가로 헤더, 쿼리 스트링, 쿠키를 캐시 키에 포함할 수 있지만, 포함하는 값이 많을수록 캐시 히트율이 낮아진다.

```
캐시 키 구성 예시:

기본 (URL만):
  /images/logo.png → 캐시 키: /images/logo.png
  모든 사용자가 같은 캐시를 공유 → 히트율 높음 ✅

쿼리 스트링 포함:
  /api/products?page=1 → 캐시 키: /api/products?page=1
  /api/products?page=2 → 캐시 키: /api/products?page=2
  같은 경로라도 쿼리가 다르면 별도 캐시 → 히트율 보통

헤더 포함 (Accept-Language):
  /index.html + Accept-Language: ko → 캐시 키 A
  /index.html + Accept-Language: en → 캐시 키 B
  같은 URL이라도 헤더가 다르면 별도 캐시 → 히트율 낮음 ⚠️
```

> **핵심 통찰**: 캐시 키에 포함하는 값은 **정말 필요한 것만 최소한으로** 설정하라. 쿼리 스트링, 헤더, 쿠키를 무분별하게 캐시 키에 포함하면 캐시가 지나치게 세분화되어 히트율이 급락한다. 예를 들어 사용자 고유한 `Authorization` 헤더를 캐시 키에 포함하면 사실상 모든 요청이 캐시 미스가 된다.

### 4.4 AWS 관리형 캐시 정책

AWS는 일반적인 시나리오에 맞는 관리형 캐시 정책을 제공한다.

| 정책 이름 | 용도 | TTL | 캐시 키 |
|----------|------|-----|--------|
| **CachingOptimized** | 정적 에셋 (S3, 정적 사이트) | Default 24h, Max 1y | URL만 |
| **CachingOptimizedForUncompressedObjects** | 비압축 콘텐츠 | Default 24h, Max 1y | URL만 |
| **CachingDisabled** | 캐시 비활성화 (API, 동적 콘텐츠) | 모두 0 | 없음 (항상 오리진) |
| **Elemental-MediaPackage** | 미디어 스트리밍 | 맞춤 설정 | 쿼리 스트링 포함 |

```bash
# AWS 관리형 캐시 정책 목록 확인
aws cloudfront list-cache-policies --type managed

# 커스텀 캐시 정책 생성
aws cloudfront create-cache-policy \
  --cache-policy-config '{
    "Name": "my-api-cache-policy",
    "Comment": "API responses with query string caching",
    "DefaultTTL": 60,
    "MaxTTL": 300,
    "MinTTL": 0,
    "ParametersInCacheKeyAndForwardedToOrigin": {
      "EnableAcceptEncodingGzip": true,
      "EnableAcceptEncodingBrotli": true,
      "HeadersConfig": {
        "HeaderBehavior": "none"
      },
      "CookiesConfig": {
        "CookieBehavior": "none"
      },
      "QueryStringsConfig": {
        "QueryStringBehavior": "whitelist",
        "QueryStrings": {
          "Quantity": 2,
          "Items": ["page", "limit"]
        }
      }
    }
  }'
```

---

## 5. 캐시 무효화 (Invalidation)

### 5.1 캐시 무효화란

캐시 무효화(*Invalidation - 엣지 로케이션에 캐시된 콘텐츠를 TTL 만료 전에 강제로 제거하는 작업*)는 배포 후 이전 버전의 콘텐츠가 캐시에 남아 있을 때 강제로 갱신하는 방법이다.

```
캐시 무효화 시나리오:

1. index.html을 S3에 업데이트
2. CloudFront 엣지에는 이전 버전이 캐시되어 있음
3. 사용자는 여전히 이전 버전을 받음 ← 문제!
4. 캐시 무효화 실행: /* 또는 /index.html
5. 엣지에서 캐시 삭제됨
6. 다음 요청 시 오리진에서 최신 버전을 가져옴 ← 해결
```

### 5.2 무효화 실행

```bash
# 특정 파일 무효화
aws cloudfront create-invalidation \
  --distribution-id E1234567890ABC \
  --paths "/index.html" "/manifest.json"

# 특정 경로 하위 전체 무효화
aws cloudfront create-invalidation \
  --distribution-id E1234567890ABC \
  --paths "/static/*"

# 전체 무효화 (모든 캐시 삭제)
aws cloudfront create-invalidation \
  --distribution-id E1234567890ABC \
  --paths "/*"

# 무효화 상태 확인
aws cloudfront get-invalidation \
  --distribution-id E1234567890ABC \
  --id I1234567890ABC
```

### 5.3 무효화 비용과 대안

| 항목 | 설명 |
|------|------|
| **무료 할당량** | 월 1,000개 경로까지 무료 |
| **초과 비용** | 경로당 $0.005 |
| **`/*` 와일드카드** | 1개 경로로 카운트 (파일 수와 무관) |
| **소요 시간** | 보통 1~2분, 최대 수 분 |

> **실무 팁**: 무효화에 의존하는 대신, **파일명에 해시를 포함**하는 전략이 더 효율적이다. `main.js` 대신 `main.a1b2c3.js`를 사용하면 내용이 바뀔 때 파일명도 바뀌므로 캐시 무효화가 필요 없다. 무효화가 필요한 파일은 `index.html` 같은 진입점 파일 정도로 한정하라. 대부분의 프론트엔드 빌드 도구(Webpack, Vite, Next.js)는 기본적으로 에셋 파일명에 해시를 포함한다.

---

## 6. HTTPS 설정

### 6.1 Viewer Protocol Policy

Viewer Protocol Policy는 사용자(Viewer)와 CloudFront 간의 프로토콜을 제어한다.

| 정책 | 동작 | 권장 여부 |
|------|------|----------|
| **HTTP and HTTPS** | 둘 다 허용 | 비권장 |
| **Redirect HTTP to HTTPS** | HTTP 접속 시 HTTPS로 301 리다이렉트 | **권장** |
| **HTTPS Only** | HTTP 접속을 완전 차단 | API 전용 배포 시 사용 |

### 6.2 ACM 인증서 연동

CloudFront에서 HTTPS를 사용하려면 ACM(*AWS Certificate Manager*)에서 발급한 SSL/TLS 인증서가 필요하다. Chapter 5에서 다룬 ACM 인증서 발급 흐름을 복습한다.

```bash
# ① ACM 인증서 발급 (반드시 us-east-1 리전!)
aws acm request-certificate \
  --region us-east-1 \
  --domain-name example.com \
  --subject-alternative-names "*.example.com" \
  --validation-method DNS

# ② DNS 검증 (Route 53 사용 시 콘솔에서 자동 추가 가능)
# ACM이 제공하는 CNAME 레코드를 Route 53에 추가

# ③ CloudFront 배포에 인증서 연결
aws cloudfront update-distribution \
  --id E1234567890ABC \
  --if-match ETAG_VALUE \
  --distribution-config '{
    ...
    "ViewerCertificate": {
      "ACMCertificateArn": "arn:aws:acm:us-east-1:123456789012:certificate/abc-123",
      "SSLSupportMethod": "sni-only",
      "MinimumProtocolVersion": "TLSv1.2_2021"
    }
    ...
  }'
```

```
HTTPS 연결 구조:

사용자 ──── HTTPS (ACM 인증서) ────→ CloudFront 엣지
                                         │
CloudFront ──── HTTPS 또는 HTTP ────→ 오리진 (S3/ALB)
                                       (Origin Protocol Policy로 설정)
```

> **비용 주의**: ACM 인증서 자체는 **무료**이다. 하지만 CloudFront의 HTTPS 요청은 HTTP 요청보다 약간 비싸다(미국/유럽 기준 HTTPS 10,000건당 $0.0100 vs HTTP 10,000건당 $0.0075). 그럼에도 보안과 SEO(Google은 HTTPS 사이트를 우대)를 고려하면 HTTPS는 선택이 아닌 필수이다.

---

## 7. 커스텀 도메인 연결

CloudFront 배포에 `d1234.cloudfront.net` 대신 `example.com` 같은 커스텀 도메인을 연결하는 과정이다. Chapter 5의 Route 53 Alias 레코드와 연결된다.

### 7.1 설정 순서

```
커스텀 도메인 연결 3단계:

① CloudFront 배포에 대체 도메인(CNAME) 추가
   → Aliases: ["example.com", "www.example.com"]
   → ACM 인증서 연결 (도메인이 인증서에 포함되어야 함)

② Route 53에서 Alias 레코드 생성
   → example.com     (A)  → d1234.cloudfront.net
   → www.example.com (A)  → d1234.cloudfront.net

③ 확인
   → curl -I https://example.com
   → x-cache: Hit from cloudfront 헤더 확인
```

### 7.2 Route 53 Alias 레코드 생성

```bash
cat > /tmp/cf-alias.json << 'EOF'
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
    },
    {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "www.example.com",
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
  --change-batch file:///tmp/cf-alias.json
```

> CloudFront의 HostedZoneId는 **`Z2FDTNDATAQYW2`**로 글로벌 고정값이다 (Chapter 5 참고).

---

## 8. CloudFront Functions vs Lambda@Edge

CloudFront는 엣지 로케이션에서 경량 로직을 실행하는 두 가지 메커니즘을 제공한다.

### 8.1 비교

| 특성 | CloudFront Functions | Lambda@Edge |
|------|---------------------|-------------|
| **실행 위치** | 엣지 로케이션 (600+) | 리전 엣지 캐시 (13) |
| **런타임** | JavaScript (ECMAScript 5.1) | Node.js, Python |
| **실행 시간** | 최대 1ms | 최대 5초 (Viewer), 30초 (Origin) |
| **메모리** | 2 MB | 128~10,240 MB |
| **네트워크 접근** | 불가 | 가능 (외부 API 호출 가능) |
| **요청/응답 본문 접근** | 불가 | 가능 |
| **트리거 이벤트** | Viewer Request, Viewer Response | Viewer Request/Response, Origin Request/Response |
| **비용** | 100만 요청당 $0.10 | 100만 요청당 $0.60 + 실행 시간 |
| **배포 속도** | 수 초 | 수 분 (Lambda 복제) |

```
CloudFront Functions vs Lambda@Edge 실행 위치:

사용자
  │
  │ ← Viewer Request (CF Functions 또는 Lambda@Edge)
  ↓
CloudFront 엣지 로케이션
  │ ← Viewer Response (CF Functions 또는 Lambda@Edge)
  │
  │ ← Origin Request (Lambda@Edge만)
  ↓
오리진 (S3, ALB)
  │ ← Origin Response (Lambda@Edge만)
  ↓
CloudFront 엣지 로케이션 (캐시 저장)
  │
  ↓
사용자
```

### 8.2 CloudFront Functions 사용 사례

CloudFront Functions는 간단하고 빠른 요청/응답 변환에 적합하다.

**URL 리다이렉트 (www → 루트 도메인):**

```javascript
// CloudFront Function: www → 루트 도메인 리다이렉트
function handler(event) {
  var request = event.request;
  var host = request.headers.host.value;

  if (host.startsWith('www.')) {
    var newUrl = 'https://' + host.replace('www.', '') + request.uri;
    return {
      statusCode: 301,
      statusDescription: 'Moved Permanently',
      headers: {
        location: { value: newUrl }
      }
    };
  }

  return request;
}
```

**보안 헤더 추가:**

```javascript
// CloudFront Function: 보안 헤더 추가 (Viewer Response)
function handler(event) {
  var response = event.response;
  var headers = response.headers;

  headers['strict-transport-security'] = {
    value: 'max-age=63072000; includeSubdomains; preload'
  };
  headers['x-content-type-options'] = { value: 'nosniff' };
  headers['x-frame-options'] = { value: 'DENY' };
  headers['x-xss-protection'] = { value: '1; mode=block' };
  headers['referrer-policy'] = { value: 'strict-origin-when-cross-origin' };

  return response;
}
```

**SPA 라우팅 (index.html 폴백):**

```javascript
// CloudFront Function: SPA 클라이언트 사이드 라우팅
function handler(event) {
  var request = event.request;
  var uri = request.uri;

  // 파일 확장자가 있으면 그대로 통과 (정적 에셋)
  if (uri.includes('.')) {
    return request;
  }

  // 확장자가 없으면 index.html로 리라이트 (SPA 라우팅)
  request.uri = '/index.html';
  return request;
}
```

### 8.3 Lambda@Edge 사용 사례

Lambda@Edge는 네트워크 접근이 필요하거나, 복잡한 로직이 필요할 때 사용한다.

**A/B 테스트 (Origin Request에서 오리진 분기):**

```javascript
// Lambda@Edge: A/B 테스트 (Origin Request 트리거)
exports.handler = async (event) => {
  const request = event.Records[0].cf.request;

  // 쿠키에서 실험 그룹 확인
  const cookies = request.headers.cookie || [];
  const abCookie = cookies
    .map(c => c.value)
    .join(';')
    .match(/ab-group=([AB])/);

  // 쿠키가 없으면 랜덤 배정
  const group = abCookie ? abCookie[1] : (Math.random() < 0.5 ? 'A' : 'B');

  // 그룹에 따라 오리진 경로 변경
  if (group === 'B') {
    request.origin.s3.path = '/experiment-b';
  }

  return request;
};
```

**인증 검사 (Viewer Request에서 JWT 검증):**

```javascript
// Lambda@Edge: JWT 인증 검사 (Viewer Request 트리거)
const jwt = require('jsonwebtoken');

exports.handler = async (event) => {
  const request = event.Records[0].cf.request;
  const headers = request.headers;

  // Authorization 헤더 확인
  const authHeader = headers.authorization?.[0]?.value;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return {
      status: '401',
      statusDescription: 'Unauthorized',
      body: JSON.stringify({ error: 'Missing or invalid token' })
    };
  }

  try {
    const token = authHeader.split(' ')[1];
    jwt.verify(token, process.env.JWT_SECRET);
    return request; // 인증 성공 → 요청 계속 진행
  } catch (err) {
    return {
      status: '403',
      statusDescription: 'Forbidden',
      body: JSON.stringify({ error: 'Invalid token' })
    };
  }
};
```

### 8.4 선택 기준

```
어떤 것을 사용할지 결정 플로우:

외부 API/DB 호출이 필요한가?
  ├── 예 → Lambda@Edge
  └── 아니오
       │
       요청/응답 본문 접근이 필요한가?
         ├── 예 → Lambda@Edge
         └── 아니오
              │
              실행 시간이 1ms 내로 충분한가?
                ├── 예 → CloudFront Functions (더 빠르고 저렴)
                └── 아니오 → Lambda@Edge
```

> **실무 팁**: 대부분의 프론트엔드 관련 엣지 로직(URL 리다이렉트, 보안 헤더 추가, 간단한 리라이트)은 **CloudFront Functions로 충분**하다. Lambda@Edge의 비용은 CloudFront Functions의 6배이며 배포도 느리다. Lambda@Edge는 인증 검사, A/B 테스트, 이미지 리사이징 등 복잡한 로직이 필요한 경우에만 사용하라.

---

## 9. Next.js + CloudFront 배포 패턴

### 9.1 정적 export (Static Export)

Next.js의 `output: 'export'` 설정으로 완전한 정적 사이트를 생성하고 S3 + CloudFront로 배포하는 패턴이다. 가장 단순하고 비용 효율적이다.

```typescript
// next.config.ts
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  output: 'export',        // 정적 HTML/CSS/JS만 생성
  trailingSlash: true,     // /about → /about/index.html (S3 호환)
  images: {
    unoptimized: true,     // next/image 최적화 비활성화 (서버 없으므로)
  },
};

export default nextConfig;
```

```bash
# 빌드 및 배포
npm run build              # out/ 디렉터리에 정적 파일 생성
aws s3 sync ./out s3://my-frontend-app --delete

# index.html만 캐시 무효화
aws cloudfront create-invalidation \
  --distribution-id E1234567890ABC \
  --paths "/index.html" "/*/index.html"
```

**장점:** 서버 비용 없음, S3 + CloudFront만으로 운영, 가장 빠른 응답 속도
**제한:** `getServerSideProps`, API Routes, 미들웨어, 이미지 최적화 사용 불가

### 9.2 SSR (Server-Side Rendering)

SSR이 필요한 Next.js 앱은 서버가 필요하므로 배포 구조가 달라진다.

```
Next.js SSR + CloudFront 구조:

사용자
  │
  ↓
CloudFront
  │
  ├── /\_next/static/* → S3 (정적 에셋, 장기 캐시)
  │
  └── /* (기본) → ALB → ECS/EC2 (Next.js 서버)
                         │
                         └── SSR 렌더링 + API Routes
```

```bash
# CloudFront 배포에 2개의 Behavior 설정:

# Behavior 1: 정적 에셋 → S3 (캐시 최적화)
# 경로 패턴: /_next/static/*
# 오리진: S3 버킷
# 캐시 정책: CachingOptimized (장기 캐시)

# Behavior 2: 나머지 → ALB (SSR 서버)
# 경로 패턴: * (기본)
# 오리진: ALB
# 캐시 정책: CachingDisabled (항상 서버로)
```

| 배포 방식 | 서버 필요 | 비용 | 기능 범위 | 적합한 경우 |
|----------|----------|------|----------|------------|
| **정적 export** | 없음 (S3만) | 매우 낮음 | 제한적 | 블로그, 랜딩 페이지, 문서 사이트 |
| **SSR (ALB + ECS)** | 있음 | 중간~높음 | 전체 | 동적 콘텐츠, 인증, API |
| **AWS Amplify** | 관리형 | 사용량 기반 | 전체 | 빠른 배포, 관리 최소화 (Ch 13) |

---

## 10. 캐시 히트율 최적화

### 10.1 Cache-Control 헤더 전략

오리진에서 보내는 `Cache-Control` 헤더가 CloudFront의 캐시 동작을 결정한다. 파일 유형별로 적절한 캐시 전략을 설정하는 것이 중요하다.

| 파일 유형 | Cache-Control 값 | 이유 |
|----------|-----------------|------|
| **해시된 에셋** (`main.a1b2c3.js`, `style.xyz789.css`) | `public, max-age=31536000, immutable` | 파일명에 해시 포함, 내용 변경 시 파일명도 변경 |
| **index.html** | `public, max-age=0, must-revalidate` | 항상 최신 버전이어야 하므로 매번 검증 |
| **이미지** (변경 드문 경우) | `public, max-age=604800` (1주) | 적절한 기간 캐시 후 갱신 |
| **API 응답** | `private, no-cache` 또는 `max-age=60` | 사용자별 데이터는 캐시 금지, 공용 데이터는 짧은 캐시 |

```bash
# S3 업로드 시 파일별 Cache-Control 설정
# 해시된 에셋: 1년 캐시
aws s3 sync ./out/_next s3://my-frontend-app/_next \
  --cache-control "public, max-age=31536000, immutable"

# HTML: 캐시 없음
aws s3 sync ./out s3://my-frontend-app \
  --exclude "*" --include "*.html" \
  --cache-control "public, max-age=0, must-revalidate"

# 이미지: 1주 캐시
aws s3 sync ./out/images s3://my-frontend-app/images \
  --cache-control "public, max-age=604800"
```

### 10.2 쿼리 스트링 정규화

쿼리 스트링의 순서가 달라도 실제로는 같은 리소스인 경우가 많다. 이를 캐시 키에 포함하면 불필요하게 캐시가 분리된다.

```
쿼리 스트링 정규화 문제:

/products?page=1&sort=price    ← 캐시 키 A
/products?sort=price&page=1    ← 캐시 키 B (순서만 다름, 같은 리소스!)

해결: 캐시 정책에서 필요한 쿼리 스트링만 화이트리스트로 지정
```

### 10.3 압축 (Gzip/Brotli)

CloudFront는 오리진에서 받은 콘텐츠를 자동으로 압축하여 전송할 수 있다. 캐시 정책에서 `EnableAcceptEncodingGzip`과 `EnableAcceptEncodingBrotli`를 활성화하면 된다.

```
압축 효과:

파일: main.js (500 KB)
  → Gzip 압축: ~150 KB (70% 감소)
  → Brotli 압축: ~130 KB (74% 감소)

전송 속도 향상 + 데이터 전송 비용 절감
```

### 10.4 캐시 히트율 모니터링

```bash
# CloudFront 캐시 통계 확인 (CloudWatch 메트릭)
aws cloudwatch get-metric-statistics \
  --namespace AWS/CloudFront \
  --metric-name CacheHitRate \
  --dimensions Name=DistributionId,Value=E1234567890ABC \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Average
```

```
캐시 히트율 목표:

정적 사이트: 90% 이상을 목표
동적 + 정적 혼합: 70% 이상을 목표

히트율이 낮다면 점검할 항목:
  1. Cache-Control 헤더가 올바른가?
  2. 캐시 키에 불필요한 값이 포함되어 있지 않은가?
  3. 쿼리 스트링이 정규화되어 있는가?
  4. TTL이 너무 짧지 않은가?
```

---

## 11. 가격 등급 (Price Class)

CloudFront는 전 세계 엣지 로케이션을 사용하지만, 모든 지역의 요금이 같지는 않다. 가격 등급으로 사용할 엣지 로케이션의 범위를 제한하여 비용을 줄일 수 있다.

### 11.1 가격 등급 비교

| 가격 등급 | 포함 지역 | 비용 | 적합한 경우 |
|----------|----------|------|------------|
| **Price Class All** | 전 세계 모든 엣지 | 가장 비쌈 | 글로벌 서비스, 모든 지역의 사용자 |
| **Price Class 200** | 북미, 유럽, 아시아, 아프리카, 중동 | 중간 | 대부분의 서비스 (남미, 호주 제외) |
| **Price Class 100** | 북미, 유럽만 | 가장 저렴 | 북미/유럽 대상 서비스 |

```
가격 등급별 데이터 전송 비용 (1 GB당, HTTPS):

                 북미/유럽   아시아     남미      호주
Price Class All:  $0.085    $0.114    $0.170    $0.170
Price Class 200:  $0.085    $0.114    제외      제외
Price Class 100:  $0.085    제외      제외      제외
```

> **비용 주의**: 한국 사용자가 주 대상이라면 **Price Class 200**이 최적이다. Price Class 100은 아시아가 제외되므로 한국 사용자에게 가장 가까운 엣지 로케이션을 사용할 수 없다. Price Class All은 남미와 호주 사용자가 많지 않다면 불필요한 비용 증가만 초래한다. 단, 가격 등급에서 제외된 지역의 사용자는 접속이 불가능한 것이 아니라, 포함된 지역 중 가장 가까운 엣지에서 서비스된다(지연 시간만 약간 증가).

### 11.2 CloudFront 비용 구조

| 비용 항목 | 설명 | 대략적 비용 |
|----------|------|------------|
| **데이터 전송 (엣지 → 사용자)** | 사용자에게 전달하는 데이터 양 | 1 GB당 $0.085~$0.170 (지역별) |
| **HTTP/HTTPS 요청** | 요청 건수 | 10,000건당 $0.0075~$0.0100 |
| **오리진 전송** | 오리진에서 가져오는 데이터 | 무료 (AWS 오리진 → CloudFront) |
| **캐시 무효화** | 월 1,000개 경로 초과 시 | 경로당 $0.005 |
| **CloudFront Functions** | 함수 호출 | 100만 요청당 $0.10 |
| **Lambda@Edge** | 함수 호출 + 실행 시간 | 100만 요청당 $0.60 + GB-초 |

> **핵심 통찰**: CloudFront를 사용하면 S3에서 직접 전송하는 것보다 **오히려 비용이 줄어드는** 경우가 많다. 이유는 두 가지다: (1) 캐시 히트로 인해 S3에 대한 요청 수 자체가 줄어들고, (2) S3에서 인터넷으로 직접 전송하는 비용($0.126/GB, 서울)보다 CloudFront의 전송 비용($0.114/GB, 아시아)이 더 저렴하다. 즉, CDN은 속도뿐 아니라 비용 최적화 도구이기도 하다.

---

## 자주 하는 실수

| 실수 | 설명 | 올바른 접근 |
|------|------|------------|
| **S3 버킷을 퍼블릭으로 열어둠** | CloudFront를 우회하여 S3에 직접 접근 가능 | OAC를 설정하고 S3 퍼블릭 접근 차단 |
| **ACM 인증서를 서울 리전에서 발급** | CloudFront에서 인증서가 보이지 않음 | CloudFront용 인증서는 반드시 `us-east-1`에서 발급 |
| **SPA 에러 응답 미설정** | SPA에서 직접 URL 접속 시 403/404 에러 | 커스텀 에러 응답으로 403/404 → `/index.html` 리다이렉트 |
| **index.html에 장기 캐시 설정** | 배포 후에도 사용자가 이전 버전을 계속 봄 | `index.html`은 `max-age=0, must-revalidate`로 설정 |
| **캐시 키에 모든 쿼리 스트링 포함** | 캐시 히트율 급락 | 필요한 쿼리 스트링만 화이트리스트로 지정 |
| **`/*` 무효화를 매 배포마다 실행** | 전체 캐시가 날아가 히트율 저하 + 오리진 부하 | 파일명 해시 전략 사용, `index.html`만 무효화 |
| **OAI 사용 (레거시)** | AWS가 더 이상 권장하지 않는 방식 | 새 배포에서는 OAC 사용 |
| **Price Class All 기본 사용** | 불필요한 지역까지 포함되어 비용 증가 | 서비스 대상 지역에 맞는 Price Class 선택 |
| **CloudFront Functions 대신 Lambda@Edge 사용** | 간단한 로직에 불필요하게 비싸고 느린 솔루션 | 단순 리다이렉트, 헤더 추가 등은 CloudFront Functions 사용 |
| **오리진에 Cache-Control 헤더 미설정** | Default TTL에 의존하여 예측 불가능한 캐시 동작 | 오리진에서 명시적으로 Cache-Control 헤더 전송 |

---

## AWS CLI 레퍼런스

| 명령어 | 설명 |
|--------|------|
| `aws cloudfront create-distribution --distribution-config file://FILE` | CloudFront 배포 생성 |
| `aws cloudfront list-distributions` | 배포 목록 조회 |
| `aws cloudfront get-distribution --id DIST_ID` | 배포 상세 조회 |
| `aws cloudfront update-distribution --id DIST_ID --if-match ETAG --distribution-config file://FILE` | 배포 설정 업데이트 |
| `aws cloudfront delete-distribution --id DIST_ID --if-match ETAG` | 배포 삭제 (비활성화 후) |
| `aws cloudfront create-invalidation --distribution-id DIST_ID --paths "PATH1" "PATH2"` | 캐시 무효화 |
| `aws cloudfront get-invalidation --distribution-id DIST_ID --id INV_ID` | 무효화 상태 조회 |
| `aws cloudfront create-origin-access-control --origin-access-control-config JSON` | OAC 생성 |
| `aws cloudfront list-cache-policies --type managed` | 관리형 캐시 정책 조회 |
| `aws cloudfront create-cache-policy --cache-policy-config JSON` | 커스텀 캐시 정책 생성 |
| `aws cloudfront create-function --name NAME --runtime cloudfront-js-2.0 --function-code fileb://FILE` | CloudFront Function 생성 |
| `aws cloudfront publish-function --name NAME --if-match ETAG` | CloudFront Function 게시 |
| `aws cloudfront test-function --name NAME --if-match ETAG --event-object fileb://FILE` | CloudFront Function 테스트 |

---

## 요약

- **CDN**은 전 세계에 분산된 엣지 로케이션에서 콘텐츠를 캐싱하여 사용자에게 가장 가까운 위치에서 빠르게 전달하는 시스템이다. CloudFront는 AWS의 CDN 서비스로 600개 이상의 엣지 로케이션을 보유한다.
- **CloudFront 핵심 개념**: Distribution(배포 설정 단위), Origin(원본 서버), Behavior(경로별 처리 규칙), Edge Location(캐시 서버)으로 구성된다.
- **S3 + CloudFront 정적 배포**에서는 반드시 **OAC**를 설정하여 S3 직접 접근을 차단하라. OAI는 레거시이며, 새 배포에서는 OAC를 사용한다.
- **캐시 정책**은 TTL(캐시 수명)과 캐시 키(캐시 식별자)를 제어한다. 캐시 키에 포함하는 값은 최소한으로 유지하여 히트율을 극대화하라.
- **캐시 무효화**는 배포 후 캐시를 강제 갱신하는 방법이다. 파일명 해시 전략을 사용하면 무효화 의존도를 줄일 수 있다. `index.html`만 무효화하는 것이 가장 효율적이다.
- **HTTPS**는 ACM 인증서(us-east-1에서 발급)를 CloudFront에 연결하여 설정한다. Viewer Protocol Policy를 `redirect-to-https`로 설정하라.
- **커스텀 도메인**은 CloudFront 배포에 대체 도메인(CNAME)을 추가하고, Route 53에서 Alias 레코드를 생성하여 연결한다.
- **CloudFront Functions**는 간단한 엣지 로직(URL 리다이렉트, 헤더 추가)에, **Lambda@Edge**는 복잡한 로직(인증, A/B 테스트)에 사용한다. 대부분의 프론트엔드 관련 작업은 CloudFront Functions로 충분하다.
- **Next.js 배포**: 정적 export는 S3 + CloudFront로 간단하게, SSR은 ALB + ECS를 오리진으로 구성한다.
- **캐시 히트율 최적화**: 파일별 적절한 Cache-Control 헤더, 최소한의 캐시 키, 쿼리 스트링 화이트리스트, Gzip/Brotli 압축을 적용하라.
- **가격 등급**: 한국 대상 서비스는 **Price Class 200**이 최적이다. CloudFront는 S3 직접 전송보다 오히려 저렴할 수 있으므로 CDN은 속도와 비용 모두에 유리하다.
