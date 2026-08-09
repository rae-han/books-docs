# Chapter 7: Lambda - 서버리스 컴퓨팅: Serverless Computing

## 핵심 질문

서버를 직접 관리하지 않고 코드를 실행할 수 있는가? Lambda 함수는 어떻게 작성하고, 어떤 이벤트가 함수를 트리거하며, 콜드 스타트 같은 성능 문제는 어떻게 해결하는가?

---

## 1. 서버리스란

### 1.1 서버리스의 정의

서버리스(*Serverless - 서버 인프라의 관리를 클라우드 제공자에게 완전히 위임하고, 개발자는 코드 작성에만 집중하는 클라우드 실행 모델*)는 "서버가 없다"는 뜻이 아니다. 서버는 여전히 존재하지만, **개발자가 서버를 프로비저닝하거나 관리할 필요가 없다**는 의미이다.

EC2를 사용할 때는 인스턴스 타입을 선택하고, OS를 업데이트하고, 스케일링 그룹을 설정하고, 서버 장애를 모니터링해야 한다. 서버리스에서는 이 모든 것을 AWS가 처리한다.

### 1.2 서버리스의 네 가지 특성

| 특성 | 설명 | EC2와의 비교 |
|------|------|-------------|
| **서버 관리 불필요** | OS, 패치, 스케일링을 AWS가 담당 | EC2는 직접 관리 |
| **이벤트 기반 실행** | 요청이 올 때만 코드가 실행됨 | EC2는 24시간 구동 |
| **자동 스케일링** | 동시 요청 수에 따라 자동으로 함수 인스턴스가 늘어남 | Auto Scaling 설정 필요 |
| **실행 시간만 과금** | 코드가 실행된 시간(ms 단위)만 비용 발생 | EC2는 인스턴스가 켜진 시간 전체 과금 |

```
EC2 vs Lambda 과금 비교:

EC2 (시간 기반 과금):
┌──────────────────────────────────────────┐
│█████████████████████████████████████████  │ ← 24시간 과금
│████ 실제 요청 처리 ████                  │
│████████████████████  대기 상태 ██████████│
└──────────────────────────────────────────┘

Lambda (실행 시간 기반 과금):
     ▌  ▌▌ ▌   ▌▌▌  ▌  ▌ ▌▌   ▌  ▌       ← 실행된 시간만 과금
─────────────────────────────────────────
     요청이 없으면 비용 $0
```

### 1.3 AWS의 서버리스 서비스 생태계

Lambda는 AWS 서버리스 생태계의 핵심이지만, 단독으로 사용되는 경우는 드물다.

```
AWS 서버리스 생태계:

[이벤트 소스]                [컴퓨팅]           [데이터/저장]
API Gateway ──────┐
S3 이벤트 ────────┤
CloudWatch ───────┼──→ Lambda ──→ DynamoDB
SQS ──────────────┤              S3
EventBridge ──────┤              RDS (Proxy)
DynamoDB Streams ─┘              SQS
```

---

## 2. Lambda 개념

### 2.1 핵심 구성 요소

Lambda 함수(*Lambda Function - AWS Lambda에서 실행되는 코드의 단위. 특정 이벤트에 반응하여 자동으로 실행된다*)는 네 가지 핵심 개념으로 구성된다.

| 개념 | 설명 |
|------|------|
| **함수(Function)** | 실행할 코드. 런타임(Node.js, Python 등)과 함께 배포 |
| **핸들러(Handler)** | Lambda가 호출하는 함수의 진입점. `파일명.함수명` 형식 |
| **이벤트(Event)** | 함수를 트리거한 데이터. JSON 형식으로 전달됨 |
| **컨텍스트(Context)** | 함수 실행 환경 정보. 남은 실행 시간, 요청 ID 등을 포함 |

### 2.2 Lambda 실행 흐름

```
요청 흐름:

1. 트리거 발생 (API Gateway 요청, S3 업로드 등)
                │
2. Lambda 서비스가 이벤트 수신
                │
3. 실행 환경 준비 (콜드 스타트) 또는 기존 환경 재사용 (웜 스타트)
                │
4. 핸들러 함수 호출 (event, context 전달)
                │
5. 코드 실행 및 결과 반환
                │
6. 실행 환경을 일정 시간 유지 (다음 호출 대비)
```

### 2.3 지원 런타임

| 런타임 | 버전 | 식별자 |
|--------|------|--------|
| **Node.js** | 22.x, 20.x, 18.x | `nodejs22.x`, `nodejs20.x`, `nodejs18.x` |
| **Python** | 3.13, 3.12, 3.11 | `python3.13`, `python3.12`, `python3.11` |
| **Java** | 21, 17, 11 | `java21`, `java17`, `java11` |
| **Go** | (커스텀 런타임) | `provided.al2023` |
| **커스텀** | 사용자 정의 | `provided.al2023` |

> **실무 팁**: 프로덕션에서는 **LTS(Long-Term Support) 버전의 런타임**을 사용하라. Lambda 런타임은 AWS에서 지원 종료일을 두고 있으며, 지원이 끝난 런타임은 새로운 함수 생성이 차단되고, 기존 함수도 보안 패치를 받지 못한다. Node.js는 짝수 버전(18, 20, 22)이 LTS이다.

---

## 3. Node.js Lambda 함수 작성

### 3.1 기본 핸들러 구조

**CommonJS (CJS) 방식:**

```javascript
// index.js (CJS)
exports.handler = async (event, context) => {
  console.log('이벤트:', JSON.stringify(event, null, 2));

  return {
    statusCode: 200,
    body: JSON.stringify({
      message: 'Hello from Lambda!',
      requestId: context.awsRequestId,
    }),
  };
};
```

**ES Modules (ESM) 방식:**

```javascript
// index.mjs (ESM)
export const handler = async (event, context) => {
  console.log('이벤트:', JSON.stringify(event, null, 2));

  return {
    statusCode: 200,
    body: JSON.stringify({
      message: 'Hello from Lambda!',
      requestId: context.awsRequestId,
    }),
  };
};
```

| 방식 | 파일 확장자 | 설정 | Node.js Lambda 지원 |
|------|------------|------|---------------------|
| **CJS** | `.js` | 기본값 | 모든 버전 |
| **ESM** | `.mjs` 또는 `package.json`에 `"type": "module"` | 명시 필요 | Node.js 18.x+ |

> **실무 팁**: 새로운 프로젝트에서는 **ESM(`.mjs`)을 사용**하는 것을 권장한다. Top-level await를 사용할 수 있고, 트리 셰이킹(*Tree Shaking - 사용되지 않는 코드를 번들에서 제거하는 최적화 기법*)이 가능하여 패키지 크기를 줄일 수 있다.

### 3.2 event 객체

`event` 객체는 트리거 소스에 따라 구조가 완전히 달라진다.

**API Gateway 이벤트:**

```json
{
  "httpMethod": "GET",
  "path": "/users/123",
  "queryStringParameters": { "fields": "name,email" },
  "headers": { "Authorization": "Bearer eyJhbG..." },
  "pathParameters": { "id": "123" },
  "body": null
}
```

**S3 이벤트:**

```json
{
  "Records": [
    {
      "eventSource": "aws:s3",
      "eventName": "ObjectCreated:Put",
      "s3": {
        "bucket": { "name": "my-bucket" },
        "object": { "key": "uploads/photo.jpg", "size": 1024 }
      }
    }
  ]
}
```

**SQS 이벤트:**

```json
{
  "Records": [
    {
      "messageId": "abc-123",
      "body": "{\"userId\": 42, \"action\": \"signup\"}",
      "eventSource": "aws:sqs"
    }
  ]
}
```

### 3.3 context 객체

```javascript
export const handler = async (event, context) => {
  // 주요 속성
  context.functionName;       // 함수 이름
  context.functionVersion;    // 함수 버전 ($LATEST 또는 숫자)
  context.awsRequestId;       // 이번 호출의 고유 ID
  context.memoryLimitInMB;    // 할당된 메모리 (MB)
  context.getRemainingTimeInMillis(); // 남은 실행 시간 (ms)

  // 남은 시간이 부족하면 작업을 중단하는 패턴
  if (context.getRemainingTimeInMillis() < 5000) {
    console.warn('시간이 부족합니다. 작업을 정리합니다.');
    // 정리 작업 수행
  }
};
```

### 3.4 TypeScript로 Lambda 작성

TypeScript를 사용하려면 빌드 단계가 필요하다. Lambda 런타임은 JavaScript만 직접 실행할 수 있다.

```typescript
// src/handler.ts
import { APIGatewayProxyEvent, APIGatewayProxyResult, Context } from 'aws-lambda';

export const handler = async (
  event: APIGatewayProxyEvent,
  context: Context
): Promise<APIGatewayProxyResult> => {
  const userId = event.pathParameters?.id;

  if (!userId) {
    return {
      statusCode: 400,
      body: JSON.stringify({ error: 'userId is required' }),
    };
  }

  return {
    statusCode: 200,
    body: JSON.stringify({
      userId,
      requestId: context.awsRequestId,
    }),
  };
};
```

```bash
# TypeScript 개발 환경 설정
npm init -y
npm install -D typescript @types/aws-lambda esbuild

# tsconfig.json
# {
#   "compilerOptions": {
#     "target": "ES2022",
#     "module": "ESNext",
#     "moduleResolution": "node",
#     "outDir": "./dist",
#     "strict": true
#   }
# }

# esbuild로 번들링 (Lambda에 적합한 단일 파일 생성)
npx esbuild src/handler.ts --bundle --platform=node --target=node20 \
  --outfile=dist/handler.js --format=esm --external:@aws-sdk/*
```

> **핵심 통찰**: Lambda에서 TypeScript를 사용할 때 **esbuild**를 번들러로 선택하라. tsc는 트랜스파일만 하고 번들링은 하지 않아 `node_modules`를 함께 업로드해야 한다. esbuild는 모든 의존성을 단일 파일로 번들링하여 패키지 크기를 대폭 줄이고, 빌드 속도도 tsc보다 수십 배 빠르다. `@aws-sdk/*`는 Lambda 런타임에 이미 포함되어 있으므로 `--external`로 번들에서 제외한다.

---

## 4. 배포 방법

### 4.1 AWS 콘솔에서 직접 작성

AWS 콘솔의 인라인 에디터에서 직접 코드를 작성할 수 있다. 간단한 테스트나 프로토타이핑에는 적합하지만, 프로덕션에서는 사용하지 않는다.

```bash
# 콘솔에서 함수 생성 후 테스트 이벤트로 호출
aws lambda invoke \
  --function-name my-function \
  --payload '{"key": "value"}' \
  --cli-binary-format raw-in-base64-out \
  response.json

cat response.json
```

### 4.2 ZIP 파일 업로드

가장 기본적인 배포 방법이다. 코드와 의존성을 ZIP으로 압축하여 업로드한다.

```bash
# 1. 프로젝트 구조
# my-function/
# ├── package.json
# ├── node_modules/
# └── index.mjs

# 2. production 의존성만 설치
npm ci --production

# 3. ZIP 파일 생성
zip -r function.zip index.mjs node_modules/

# 4. Lambda 함수 생성
aws lambda create-function \
  --function-name my-api-handler \
  --runtime nodejs20.x \
  --handler index.handler \
  --role arn:aws:iam::123456789012:role/LambdaExecutionRole \
  --zip-file fileb://function.zip \
  --timeout 30 \
  --memory-size 256

# 5. 코드 업데이트 (함수가 이미 존재할 때)
aws lambda update-function-code \
  --function-name my-api-handler \
  --zip-file fileb://function.zip
```

### 4.3 SAM (Serverless Application Model)

SAM(*Serverless Application Model - AWS에서 제공하는 서버리스 애플리케이션 프레임워크. CloudFormation을 확장하여 Lambda, API Gateway 등을 간결하게 정의한다*)은 서버리스 배포를 간소화하는 프레임워크이다.

```yaml
# template.yaml (SAM 템플릿)
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: 사용자 API

Globals:
  Function:
    Timeout: 30
    Runtime: nodejs20.x
    MemorySize: 256

Resources:
  GetUserFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: src/handlers/getUser.handler
      Events:
        GetUser:
          Type: Api
          Properties:
            Path: /users/{id}
            Method: get

  CreateUserFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: src/handlers/createUser.handler
      Events:
        CreateUser:
          Type: Api
          Properties:
            Path: /users
            Method: post
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref UsersTable

  UsersTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: users
      AttributeDefinitions:
        - AttributeName: id
          AttributeType: S
      KeySchema:
        - AttributeName: id
          KeyType: HASH
      BillingMode: PAY_PER_REQUEST
```

```bash
# SAM CLI 명령어
sam init                    # 프로젝트 초기화
sam build                   # 빌드
sam local invoke GetUserFunction  # 로컬에서 함수 실행
sam local start-api         # 로컬에서 API Gateway 에뮬레이션
sam deploy --guided         # AWS에 배포 (대화식)
```

### 4.4 CDK (Cloud Development Kit)

CDK(*Cloud Development Kit - 프로그래밍 언어(TypeScript, Python 등)로 AWS 인프라를 정의하는 IaC 프레임워크*)는 TypeScript로 인프라를 정의할 수 있어 개발자에게 친숙하다.

```typescript
// lib/api-stack.ts (CDK)
import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as nodejs from 'aws-cdk-lib/aws-lambda-nodejs';
import { Construct } from 'constructs';

export class ApiStack extends cdk.Stack {
  constructor(scope: Construct, id: string) {
    super(scope, id);

    // Lambda 함수 (esbuild로 자동 번들링)
    const getUserFn = new nodejs.NodejsFunction(this, 'GetUser', {
      entry: 'src/handlers/getUser.ts',
      handler: 'handler',
      runtime: lambda.Runtime.NODEJS_20_X,
      memorySize: 256,
      timeout: cdk.Duration.seconds(30),
    });

    // API Gateway
    const api = new apigateway.RestApi(this, 'UserApi', {
      restApiName: 'User Service',
    });

    const users = api.root.addResource('users');
    const user = users.addResource('{id}');
    user.addMethod('GET', new apigateway.LambdaIntegration(getUserFn));
  }
}
```

### 4.5 배포 방법 비교

| 방법 | 장점 | 단점 | 적합한 상황 |
|------|------|------|------------|
| **콘솔 직접** | 빠른 프로토타이핑 | 버전 관리 불가, 재현 불가 | 학습, 간단한 테스트 |
| **ZIP 업로드** | 단순, 빠름 | 인프라 관리가 별도 | 소규모 단일 함수 |
| **SAM** | 서버리스에 특화, 로컬 테스트 지원 | CloudFormation 학습 필요 | 서버리스 전용 프로젝트 |
| **CDK** | TypeScript로 인프라 정의, 재사용성 | 학습 곡선 높음 | 복잡한 인프라, 팀 프로젝트 |

---

## 5. 트리거와 이벤트 소스

### 5.1 주요 트리거

Lambda 함수는 다양한 AWS 서비스의 이벤트에 의해 트리거된다. 이것이 Lambda의 핵심이다: **"어떤 일이 발생하면 이 코드를 실행해라."**

```
주요 트리거 유형:

[동기식]                    [비동기식]                [스트림/폴링]
API Gateway ──→ Lambda     S3 이벤트 ──→ Lambda     SQS ──→ Lambda
                           SNS ──→ Lambda           DynamoDB Streams ──→ Lambda
                           EventBridge ──→ Lambda   Kinesis ──→ Lambda
```

| 트리거 | 호출 방식 | 대표적인 사용 사례 |
|--------|----------|-------------------|
| **API Gateway** | 동기식 | REST/HTTP API |
| **S3** | 비동기식 | 파일 업로드 후 처리 (썸네일 생성, 데이터 변환) |
| **EventBridge** | 비동기식 | 스케줄링(cron), 서비스 간 이벤트 전달 |
| **SQS** | 폴링 | 비동기 작업 큐 (이메일 발송, 알림) |
| **DynamoDB Streams** | 폴링 | 데이터 변경 감지 (실시간 집계, 동기화) |
| **CloudWatch Logs** | 비동기식 | 로그 패턴 감지 시 알림 |

### 5.2 S3 트리거 예시

S3 버킷에 이미지가 업로드되면 자동으로 썸네일을 생성하는 함수:

```javascript
// thumbnail.mjs
import { S3Client, GetObjectCommand, PutObjectCommand } from '@aws-sdk/client-s3';
import sharp from 'sharp';

const s3 = new S3Client({});

export const handler = async (event) => {
  for (const record of event.Records) {
    const bucket = record.s3.bucket.name;
    const key = decodeURIComponent(record.s3.object.key.replace(/\+/g, ' '));

    // 원본 이미지 가져오기
    const { Body } = await s3.send(new GetObjectCommand({ Bucket: bucket, Key: key }));
    const imageBuffer = await Body.transformToByteArray();

    // 썸네일 생성 (200x200)
    const thumbnail = await sharp(imageBuffer)
      .resize(200, 200, { fit: 'cover' })
      .jpeg({ quality: 80 })
      .toBuffer();

    // 썸네일 저장
    const thumbnailKey = `thumbnails/${key.split('/').pop()}`;
    await s3.send(new PutObjectCommand({
      Bucket: bucket,
      Key: thumbnailKey,
      Body: thumbnail,
      ContentType: 'image/jpeg',
    }));

    console.log(`썸네일 생성 완료: ${thumbnailKey}`);
  }
};
```

```bash
# S3 트리거 설정
aws lambda add-permission \
  --function-name thumbnail-generator \
  --statement-id s3-trigger \
  --action lambda:InvokeFunction \
  --principal s3.amazonaws.com \
  --source-arn arn:aws:s3:::my-image-bucket

aws s3api put-bucket-notification-configuration \
  --bucket my-image-bucket \
  --notification-configuration '{
    "LambdaFunctionConfigurations": [{
      "LambdaFunctionArn": "arn:aws:lambda:ap-northeast-2:123456789012:function:thumbnail-generator",
      "Events": ["s3:ObjectCreated:*"],
      "Filter": {
        "Key": {
          "FilterRules": [{"Name": "prefix", "Value": "uploads/"}]
        }
      }
    }]
  }'
```

### 5.3 EventBridge (CloudWatch Events) 스케줄 트리거

```javascript
// cleanup.mjs — 매일 자정에 실행되는 정리 작업
export const handler = async (event) => {
  console.log('스케줄 이벤트:', JSON.stringify(event));
  // event.source === 'aws.events'
  // event['detail-type'] === 'Scheduled Event'

  // 30일 이상 된 임시 파일 삭제 등의 작업
  await cleanupOldFiles();
  await sendCleanupReport();
};
```

```bash
# EventBridge 규칙으로 스케줄 설정
aws events put-rule \
  --name daily-cleanup \
  --schedule-expression "cron(0 0 * * ? *)" \
  --description "매일 자정(UTC)에 정리 작업 실행"

aws events put-targets \
  --rule daily-cleanup \
  --targets '[{
    "Id": "cleanup-target",
    "Arn": "arn:aws:lambda:ap-northeast-2:123456789012:function:cleanup"
  }]'
```

### 5.4 SQS 트리거 예시

```javascript
// emailSender.mjs — SQS 메시지를 처리하여 이메일 발송
import { SESClient, SendEmailCommand } from '@aws-sdk/client-ses';

const ses = new SESClient({});

export const handler = async (event) => {
  // SQS는 배치로 여러 메시지를 한 번에 전달할 수 있다
  const failedMessageIds = [];

  for (const record of event.Records) {
    try {
      const { to, subject, body } = JSON.parse(record.body);

      await ses.send(new SendEmailCommand({
        Source: 'noreply@example.com',
        Destination: { ToAddresses: [to] },
        Message: {
          Subject: { Data: subject },
          Body: { Html: { Data: body } },
        },
      }));
    } catch (error) {
      console.error(`메시지 처리 실패: ${record.messageId}`, error);
      failedMessageIds.push(record.messageId);
    }
  }

  // 부분 실패 보고 (실패한 메시지만 다시 큐로 돌아감)
  return {
    batchItemFailures: failedMessageIds.map(id => ({
      itemIdentifier: id,
    })),
  };
};
```

---

## 6. API Gateway + Lambda로 REST API 구축

### 6.1 전체 아키텍처

```
REST API 아키텍처:

클라이언트 (브라우저, 모바일 앱)
      │
      │  HTTPS 요청
      ↓
┌─────────────────────────┐
│  API Gateway             │
│  (REST API / HTTP API)   │
│                          │
│  GET  /users/{id}  ──────┼──→ GetUserFunction
│  POST /users       ──────┼──→ CreateUserFunction
│  PUT  /users/{id}  ──────┼──→ UpdateUserFunction
│  DELETE /users/{id}──────┼──→ DeleteUserFunction
└─────────────────────────┘
                               │
                               ↓
                          DynamoDB / RDS
```

### 6.2 HTTP API vs REST API

API Gateway에는 두 가지 유형이 있다.

| 특성 | HTTP API | REST API |
|------|----------|----------|
| **비용** | REST API 대비 약 70% 저렴 | 더 비쌈 |
| **지연 시간** | 더 낮음 | 상대적으로 높음 |
| **기능** | 핵심 기능만 | API 키, 사용량 플랜, 캐싱, 요청 검증 등 |
| **프로토콜** | HTTP, WebSocket | REST |
| **적합한 경우** | 대부분의 API, 비용 효율 중시 | 고급 기능이 필요한 API |

대부분의 경우 **HTTP API**가 더 저렴하고 빠르다. REST API의 고급 기능(API 키 관리, 요청 검증, 캐싱)이 필요한 경우에만 REST API를 선택한다.

### 6.3 Lambda 핸들러 구현

```typescript
// src/handlers/getUser.ts
import { APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient, GetCommand } from '@aws-sdk/lib-dynamodb';

const client = new DynamoDBClient({});
const docClient = DynamoDBDocumentClient.from(client);

// DynamoDB 클라이언트를 핸들러 밖에서 초기화 → 실행 컨텍스트 재사용 시 이점

export const handler = async (
  event: APIGatewayProxyEvent
): Promise<APIGatewayProxyResult> => {
  try {
    const userId = event.pathParameters?.id;

    if (!userId) {
      return {
        statusCode: 400,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ error: 'userId is required' }),
      };
    }

    const result = await docClient.send(new GetCommand({
      TableName: process.env.TABLE_NAME!,
      Key: { id: userId },
    }));

    if (!result.Item) {
      return {
        statusCode: 404,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ error: 'User not found' }),
      };
    }

    return {
      statusCode: 200,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(result.Item),
    };
  } catch (error) {
    console.error('Error:', error);
    return {
      statusCode: 500,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ error: 'Internal server error' }),
    };
  }
};
```

### 6.4 API Gateway 설정 (CLI)

```bash
# 1. HTTP API 생성
aws apigatewayv2 create-api \
  --name user-api \
  --protocol-type HTTP \
  --target arn:aws:lambda:ap-northeast-2:123456789012:function:getUser

# 2. Lambda 통합 생성
aws apigatewayv2 create-integration \
  --api-id abc123 \
  --integration-type AWS_PROXY \
  --integration-uri arn:aws:lambda:ap-northeast-2:123456789012:function:getUser \
  --payload-format-version 2.0

# 3. 라우트 생성
aws apigatewayv2 create-route \
  --api-id abc123 \
  --route-key "GET /users/{id}"

# 4. Lambda에 API Gateway 호출 권한 부여
aws lambda add-permission \
  --function-name getUser \
  --statement-id apigateway-invoke \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com
```

---

## 7. Lambda@Edge와 CloudFront Functions

### 7.1 엣지 컴퓨팅이란

Lambda@Edge와 CloudFront Functions는 CloudFront의 엣지 로케이션(*Edge Location - 전 세계에 분산된 AWS의 캐시 서버 위치. 사용자에게 가장 가까운 위치에서 콘텐츠를 제공한다*)에서 코드를 실행한다. 사용자에게 가장 가까운 곳에서 요청을 가공할 수 있다.

```
요청/응답 수명주기에서 실행 위치:

클라이언트
  │
  │ ① Viewer Request  ← CloudFront Functions 또는 Lambda@Edge
  ↓
CloudFront 엣지
  │
  │ ② Origin Request  ← Lambda@Edge만 가능
  ↓
오리진 (S3, ALB 등)
  │
  │ ③ Origin Response  ← Lambda@Edge만 가능
  ↓
CloudFront 엣지
  │
  │ ④ Viewer Response  ← CloudFront Functions 또는 Lambda@Edge
  ↓
클라이언트
```

### 7.2 CloudFront Functions vs Lambda@Edge

| 특성 | CloudFront Functions | Lambda@Edge |
|------|---------------------|-------------|
| **실행 위치** | 모든 엣지 로케이션 (400+) | 리전 엣지 캐시 (약 13곳) |
| **런타임** | JavaScript (ECMAScript 5.1) | Node.js, Python |
| **실행 시간** | 최대 1ms | 최대 5초 (Viewer), 30초 (Origin) |
| **메모리** | 2MB | 128MB (Viewer), 10GB (Origin) |
| **네트워크 접근** | 불가 | 가능 |
| **비용** | 매우 저렴 (요청당 $0.0000001) | 상대적으로 비쌈 |
| **적합한 작업** | 간단한 헤더/URL 조작 | API 호출, 이미지 변환 등 |

### 7.3 프론트엔드 관점의 활용 사례

**A/B 테스트 (CloudFront Functions):**

```javascript
// CloudFront Function: A/B 테스트를 위한 쿠키 기반 라우팅
function handler(event) {
  var request = event.request;
  var headers = request.headers;
  var cookie = headers.cookie ? headers.cookie.value : '';

  // 쿠키가 없으면 50% 확률로 그룹 배정
  if (!cookie.includes('ab-group=')) {
    var group = Math.random() < 0.5 ? 'A' : 'B';
    request.headers['x-ab-group'] = { value: group };

    // 그룹 B는 새 버전의 페이지로 라우팅
    if (group === 'B') {
      request.uri = request.uri.replace('/index.html', '/index-v2.html');
    }
  }

  return request;
}
```

**보안 헤더 추가 (CloudFront Functions):**

```javascript
// CloudFront Function: 보안 헤더 자동 추가
function handler(event) {
  var response = event.response;
  var headers = response.headers;

  headers['strict-transport-security'] = { value: 'max-age=63072000; includeSubdomains; preload' };
  headers['x-content-type-options'] = { value: 'nosniff' };
  headers['x-frame-options'] = { value: 'DENY' };
  headers['x-xss-protection'] = { value: '1; mode=block' };
  headers['referrer-policy'] = { value: 'strict-origin-when-cross-origin' };

  return response;
}
```

**이미지 최적화 (Lambda@Edge):**

```javascript
// Lambda@Edge: Origin Response에서 이미지를 WebP로 변환
import sharp from 'sharp';
import { S3Client, GetObjectCommand } from '@aws-sdk/client-s3';

const s3 = new S3Client({ region: 'ap-northeast-2' });

export const handler = async (event) => {
  const response = event.Records[0].cf.response;
  const request = event.Records[0].cf.request;

  // 이미지 요청이 아니면 원본 응답 반환
  if (!request.uri.match(/\.(jpe?g|png)$/i)) {
    return response;
  }

  // 클라이언트가 WebP를 지원하는지 확인
  const accept = request.headers.accept?.[0]?.value || '';
  if (!accept.includes('image/webp')) {
    return response;
  }

  // S3에서 원본 이미지를 가져와 WebP로 변환
  const bucket = request.origin.s3.domainName.split('.')[0];
  const { Body } = await s3.send(new GetObjectCommand({
    Bucket: bucket,
    Key: request.uri.substring(1),
  }));

  const imageBuffer = await Body.transformToByteArray();
  const webpBuffer = await sharp(imageBuffer).webp({ quality: 80 }).toBuffer();

  return {
    status: '200',
    statusDescription: 'OK',
    headers: {
      'content-type': [{ value: 'image/webp' }],
      'cache-control': [{ value: 'public, max-age=31536000' }],
    },
    body: webpBuffer.toString('base64'),
    bodyEncoding: 'base64',
  };
};
```

**리다이렉트 (CloudFront Functions):**

```javascript
// CloudFront Function: www → apex 도메인 리다이렉트
function handler(event) {
  var request = event.request;
  var host = request.headers.host.value;

  if (host.startsWith('www.')) {
    return {
      statusCode: 301,
      statusDescription: 'Moved Permanently',
      headers: {
        location: { value: 'https://' + host.replace('www.', '') + request.uri }
      }
    };
  }

  return request;
}
```

---

## 8. 환경 변수와 Secrets

### 8.1 환경 변수 설정

Lambda 함수에 설정값을 전달하는 가장 기본적인 방법은 환경 변수이다.

```bash
# 함수 생성 시 환경 변수 설정
aws lambda create-function \
  --function-name my-api \
  --runtime nodejs20.x \
  --handler index.handler \
  --role arn:aws:iam::123456789012:role/LambdaRole \
  --zip-file fileb://function.zip \
  --environment "Variables={TABLE_NAME=users,STAGE=production,LOG_LEVEL=info}"

# 기존 함수의 환경 변수 업데이트
aws lambda update-function-configuration \
  --function-name my-api \
  --environment "Variables={TABLE_NAME=users,STAGE=production,LOG_LEVEL=warn}"
```

```javascript
// 코드에서 환경 변수 접근
const tableName = process.env.TABLE_NAME;
const stage = process.env.STAGE;
```

### 8.2 Secrets Manager 연동

데이터베이스 비밀번호, API 키 같은 민감 정보는 환경 변수가 아닌 Secrets Manager(*Secrets Manager - 데이터베이스 자격 증명, API 키 등 비밀 정보를 안전하게 저장하고, 자동 교체(rotation)를 지원하는 AWS 서비스*)를 사용한다.

**환경 변수에 비밀 정보를 넣으면 안 되는 이유:**

- 환경 변수는 AWS 콘솔에서 평문으로 볼 수 있다
- 환경 변수 업데이트 시 함수의 새 버전이 배포된다
- 비밀 정보의 자동 교체가 불가능하다

```typescript
// Secrets Manager에서 비밀 정보 가져오기
import {
  SecretsManagerClient,
  GetSecretValueCommand,
} from '@aws-sdk/client-secrets-manager';

const secretsClient = new SecretsManagerClient({});

// 캐시: 핸들러 밖에서 선언하여 실행 컨텍스트 재사용 시 캐시 활용
let cachedSecret: Record<string, string> | null = null;

async function getSecret(secretId: string): Promise<Record<string, string>> {
  if (cachedSecret) return cachedSecret;

  const response = await secretsClient.send(
    new GetSecretValueCommand({ SecretId: secretId })
  );

  cachedSecret = JSON.parse(response.SecretString!);
  return cachedSecret!;
}

export const handler = async (event: any) => {
  const secret = await getSecret(process.env.DB_SECRET_ARN!);
  const { host, port, username, password, dbname } = secret;

  // 데이터베이스 연결
  const connectionString = `postgresql://${username}:${password}@${host}:${port}/${dbname}`;
  // ...
};
```

### 8.3 SSM Parameter Store 연동

SSM Parameter Store(*SSM Parameter Store - 설정 데이터와 비밀 정보를 계층적으로 저장하는 서비스. Secrets Manager보다 단순하고 기본 사용은 무료*)는 Secrets Manager보다 가볍고, 기본 사용이 무료이다.

```bash
# 파라미터 저장
aws ssm put-parameter \
  --name "/myapp/production/api-url" \
  --value "https://api.example.com" \
  --type String

# SecureString으로 암호화하여 저장
aws ssm put-parameter \
  --name "/myapp/production/db-password" \
  --value "s3cretP@ss" \
  --type SecureString
```

```typescript
import { SSMClient, GetParameterCommand } from '@aws-sdk/client-ssm';

const ssm = new SSMClient({});

export const handler = async () => {
  const { Parameter } = await ssm.send(new GetParameterCommand({
    Name: '/myapp/production/db-password',
    WithDecryption: true,  // SecureString인 경우 복호화
  }));

  const dbPassword = Parameter!.Value;
  // ...
};
```

| 서비스 | 비용 | 자동 교체 | 적합한 경우 |
|--------|------|----------|------------|
| **환경 변수** | 무료 | 불가 | 비민감 설정 (테이블명, 로그 레벨) |
| **SSM Parameter Store** | 기본 무료 (고급 유료) | 불가 | 설정값, 저비용 비밀 관리 |
| **Secrets Manager** | 비밀당 $0.40/월 | 지원 | DB 자격 증명, API 키, 자동 교체 필요 |

---

## 9. Lambda 실행 환경

### 9.1 콜드 스타트와 웜 스타트

Lambda의 가장 중요한 성능 특성은 콜드 스타트(*Cold Start - Lambda 함수를 처음 호출하거나 새로운 실행 환경이 필요할 때 발생하는 초기화 지연*)이다.

```
콜드 스타트 vs 웜 스타트:

[콜드 스타트] (첫 호출 또는 새 환경 필요 시)
┌──────────────┬──────────────┬──────────────┐
│ 실행 환경     │ 런타임 초기화  │ 핸들러 실행    │
│ 생성 (AWS)   │ + 코드 로드   │ (비즈니스 로직)│
│              │ (Init)       │ (Invoke)     │
│ ~100-500ms   │ ~100-1000ms  │ 실제 처리     │
└──────────────┴──────────────┴──────────────┘
│←────── 콜드 스타트 지연 ──────→│

[웜 스타트] (기존 환경 재사용)
                               ┌──────────────┐
                               │ 핸들러 실행    │
                               │ (비즈니스 로직)│
                               │ (Invoke)     │
                               └──────────────┘
                               │← 빠름! ──→│
```

**콜드 스타트가 발생하는 상황:**

- 함수가 처음 호출될 때
- 오랫동안 호출이 없어 실행 환경이 회수된 후
- 동시 호출이 늘어나 새로운 실행 환경이 필요할 때
- 코드나 설정을 업데이트한 후

### 9.2 실행 컨텍스트 재사용

Lambda는 함수 호출이 끝난 후 실행 환경을 일정 시간 유지한다. 다음 호출이 이 환경을 재사용하면 웜 스타트가 된다. 이 특성을 활용하면 성능을 크게 개선할 수 있다.

```javascript
// ❌ 나쁜 예: 매 호출마다 클라이언트를 생성
export const handler = async (event) => {
  const dynamodb = new DynamoDBClient({});       // 매번 새로 생성
  const docClient = DynamoDBDocumentClient.from(dynamodb);

  const result = await docClient.send(new GetCommand({
    TableName: 'users',
    Key: { id: event.pathParameters.id },
  }));

  return { statusCode: 200, body: JSON.stringify(result.Item) };
};
```

```javascript
// ✅ 좋은 예: 핸들러 밖에서 초기화 → 실행 컨텍스트 재사용
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient, GetCommand } from '@aws-sdk/lib-dynamodb';

// 핸들러 밖에서 한 번만 초기화
const dynamodb = new DynamoDBClient({});
const docClient = DynamoDBDocumentClient.from(dynamodb);

export const handler = async (event) => {
  const result = await docClient.send(new GetCommand({
    TableName: 'users',
    Key: { id: event.pathParameters.id },
  }));

  return { statusCode: 200, body: JSON.stringify(result.Item) };
};
```

> **핵심 통찰**: **핸들러 밖에서 초기화한 변수는 실행 컨텍스트가 재사용될 때 그대로 유지된다.** DB 커넥션, SDK 클라이언트, 설정 파일 파싱 결과 등 비용이 큰 초기화 작업은 반드시 핸들러 밖에서 수행하라. 이것만으로도 웜 스타트 시 수백 ms의 지연을 절약할 수 있다.

### 9.3 /tmp 디렉토리

Lambda는 각 실행 환경에 `/tmp` 디렉토리를 제공한다. 최대 **10GB**까지 사용할 수 있으며, 실행 컨텍스트가 재사용되면 `/tmp`의 내용도 유지된다.

```javascript
import { writeFileSync, existsSync, readFileSync } from 'fs';

export const handler = async (event) => {
  const cacheFile = '/tmp/config-cache.json';

  // 캐시된 파일이 있으면 재사용
  if (existsSync(cacheFile)) {
    const cached = JSON.parse(readFileSync(cacheFile, 'utf-8'));
    console.log('캐시된 설정 사용');
    return { statusCode: 200, body: JSON.stringify(cached) };
  }

  // 없으면 새로 가져와서 /tmp에 캐시
  const config = await fetchRemoteConfig();
  writeFileSync(cacheFile, JSON.stringify(config));

  return { statusCode: 200, body: JSON.stringify(config) };
};
```

> **실무 팁**: `/tmp` 디렉토리는 임시 파일 저장, 다운로드한 데이터 처리, 캐싱에 유용하다. 다만, 실행 환경이 항상 재사용되는 것은 아니므로 `/tmp`에 데이터가 **반드시 존재한다고 가정하면 안 된다.** 항상 파일 존재 여부를 확인하고 없으면 새로 생성하는 방어적 패턴을 사용하라.

---

## 10. 동시성 관리

### 10.1 Lambda의 스케일링 모델

Lambda는 요청마다 하나의 실행 환경을 사용한다. 동시에 100개의 요청이 들어오면 100개의 실행 환경이 필요하다.

```
동시성 모델:

시간 →
──────────────────────────────────────
요청1: ████                           (환경 A)
요청2:   ██████                       (환경 B)
요청3:     ████                       (환경 C)
요청4:         ████                   (환경 A 재사용)
요청5:         ██████                 (환경 B 재사용)

최대 동시 실행: 3 (요청 1,2,3이 동시에 실행될 때)
```

| 제한 | 값 | 변경 가능 |
|------|-----|----------|
| **리전별 기본 동시성** | 1,000 | AWS에 요청하여 증가 가능 |
| **버스트 동시성** | 500~3,000 (리전별 상이) | 불가 |
| **함수별 기본 동시성** | 리전 동시성을 함수끼리 공유 | 예약(Reserved)으로 제한 가능 |

### 10.2 예약된 동시성 (Reserved Concurrency)

예약된 동시성(*Reserved Concurrency - 특정 함수에 동시 실행 수의 상한을 예약하여 보장하는 설정*)은 특정 함수가 사용할 수 있는 최대 동시 실행 수를 지정한다. 이는 두 가지 목적이 있다:

1. **중요 함수 보호**: 다른 함수의 트래픽 폭증으로 인해 중요 함수가 스로틀링되는 것을 방지
2. **리소스 보호**: 특정 함수가 과도하게 스케일링하여 다운스트림 서비스(DB 등)를 과부하시키는 것을 방지

```bash
# 함수의 예약된 동시성을 100으로 설정
aws lambda put-function-concurrency \
  --function-name my-critical-api \
  --reserved-concurrent-executions 100

# 예약된 동시성 제거 (기본 동작으로 복원)
aws lambda delete-function-concurrency \
  --function-name my-critical-api
```

### 10.3 프로비저닝된 동시성 (Provisioned Concurrency)

프로비저닝된 동시성(*Provisioned Concurrency - 지정한 수만큼의 실행 환경을 미리 초기화해두어 콜드 스타트를 제거하는 설정*)은 콜드 스타트 문제의 근본적인 해결책이다. 실행 환경을 미리 워밍업해두므로 모든 요청이 웜 스타트로 처리된다.

```bash
# 프로비저닝된 동시성 설정 (특정 버전 또는 별칭에만 가능)
aws lambda publish-version --function-name my-api
# 출력에서 Version 번호 확인 (예: 3)

aws lambda put-provisioned-concurrency-config \
  --function-name my-api \
  --qualifier 3 \
  --provisioned-concurrent-executions 50
```

> **비용 주의**: 프로비저닝된 동시성은 **실행 환경을 미리 예약하는 것이므로 비용이 지속적으로 발생**한다. 함수가 호출되지 않아도 프로비저닝된 환경에 대한 비용을 지불해야 한다. 서울 리전 기준으로 프로비저닝된 동시성 1개당 약 $0.000004046/초(약 $10.5/월)이다. 모든 함수에 적용하면 비용이 급격히 증가하므로, **지연 시간에 민감한 핵심 API에만 선택적으로 적용**하라.

```
동시성 전략 비교:

예약된 동시성 (Reserved):
- 비용: 무료 (함수 실행 비용만)
- 콜드 스타트: 여전히 발생
- 목적: 스로틀링 방지, 동시성 상한 설정

프로비저닝된 동시성 (Provisioned):
- 비용: 추가 비용 발생 (환경 유지 비용)
- 콜드 스타트: 제거됨
- 목적: 지연 시간 최소화
```

---

## 11. Lambda 제한사항

### 11.1 주요 제한

| 제한 항목 | 값 | 비고 |
|----------|-----|------|
| **최대 실행 시간** | 15분 (900초) | 이보다 긴 작업은 Step Functions 또는 ECS 사용 |
| **메모리** | 128MB ~ 10,240MB (10GB) | 1MB 단위로 설정 가능 |
| **CPU** | 메모리에 비례하여 자동 할당 | 1,769MB에서 1 vCPU에 해당 |
| **배포 패키지 (ZIP)** | 50MB (직접 업로드) / 250MB (S3 경유, 압축 해제 후) | Layer 포함 |
| **컨테이너 이미지** | 10GB | ECR에서 가져옴 |
| **/tmp 디렉토리** | 10GB | 함수별 임시 저장소 |
| **환경 변수** | 전체 크기 4KB | 키와 값 합산 |
| **동기식 페이로드** | 6MB | API Gateway 응답 포함 |
| **비동기식 페이로드** | 256KB | S3, SNS 등의 이벤트 |
| **동시 실행** | 리전당 1,000 (기본) | AWS에 요청하여 증가 가능 |

### 11.2 Lambda에 적합하지 않은 경우

| 시나리오 | 이유 | 대안 |
|----------|------|------|
| **15분 이상 걸리는 작업** | 실행 시간 제한 초과 | ECS Fargate, Step Functions |
| **WebSocket 상시 연결** | Lambda는 요청-응답 모델 | API Gateway WebSocket + Lambda, ECS |
| **높은 GPU 사용** | Lambda에 GPU 없음 | EC2 P/G 인스턴스, SageMaker |
| **일정한 고트래픽 (24시간)** | 비용이 EC2보다 비쌀 수 있음 | ECS Fargate, EC2 |
| **대용량 파일 처리** | 메모리/tmp 제한 | ECS, EC2, Step Functions + S3 |

---

## 12. VPC 연결

### 12.1 Lambda가 VPC에 접근해야 하는 경우

Lambda 함수는 기본적으로 VPC 외부에서 실행된다. 그러나 VPC 내부의 리소스(RDS, ElastiCache, 프라이빗 서브넷의 EC2 등)에 접근해야 할 때는 Lambda를 VPC에 연결해야 한다.

```
기본 상태 (VPC 미연결):

Lambda ──→ 인터넷 ──→ DynamoDB (✅ 접근 가능, 퍼블릭 서비스)
Lambda ──→ 인터넷 ──→ 외부 API (✅ 접근 가능)
Lambda ──✕──→ VPC 내부 RDS (❌ 접근 불가)

VPC 연결 후:

Lambda ──→ VPC (프라이빗 서브넷) ──→ RDS (✅ 접근 가능)
Lambda ──→ VPC ──→ NAT GW ──→ 인터넷 (✅ 접근 가능, NAT 필요)
Lambda ──→ VPC ──→ VPC Endpoint ──→ DynamoDB (✅ 접근 가능, 엔드포인트 필요)
```

### 12.2 VPC 연결 설정

```bash
# Lambda를 VPC에 연결
aws lambda update-function-configuration \
  --function-name my-api \
  --vpc-config "SubnetIds=subnet-abc123,subnet-def456,SecurityGroupIds=sg-xyz789"
```

**Lambda 실행 역할에 필요한 권한:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:CreateNetworkInterface",
        "ec2:DescribeNetworkInterfaces",
        "ec2:DeleteNetworkInterface"
      ],
      "Resource": "*"
    }
  ]
}
```

### 12.3 VPC 연결의 영향

| 항목 | VPC 미연결 | VPC 연결 |
|------|-----------|----------|
| **인터넷 접근** | 자동으로 가능 | NAT Gateway 필요 |
| **VPC 내부 리소스** | 접근 불가 | 접근 가능 |
| **AWS 퍼블릭 서비스** | 직접 접근 | VPC Endpoint 또는 NAT Gateway 필요 |
| **콜드 스타트** | 빠름 | 과거에는 느렸으나 Hyperplane ENI로 개선됨 |
| **비용** | 추가 비용 없음 | NAT Gateway 비용 추가 가능 |

> **핵심 통찰**: VPC에 연결된 Lambda가 인터넷이나 AWS 퍼블릭 서비스(S3, DynamoDB, SQS 등)에 접근하려면 **NAT Gateway** 또는 **VPC Endpoint**가 필요하다. NAT Gateway는 비용이 발생하므로, **VPC Endpoint를 사용하여 AWS 서비스에 접근하고, 인터넷 접근이 꼭 필요한 경우에만 NAT Gateway를 사용**하는 것이 비용 효율적이다.

### 12.4 RDS Proxy

Lambda에서 RDS에 직접 연결하면 심각한 문제가 발생할 수 있다. Lambda는 동시에 수백 개의 실행 환경이 생길 수 있고, 각 환경이 DB 커넥션을 열면 RDS의 최대 커넥션 수를 순식간에 소진한다.

```
문제 상황:

Lambda (동시 500개) ──→ RDS (max_connections: 100)
   500개 커넥션 요청     → 400개가 거부됨!

해결:

Lambda (동시 500개) ──→ RDS Proxy ──→ RDS
   500개 커넥션 요청     커넥션 풀링    실제 50개 커넥션만 사용
```

```bash
# RDS Proxy 생성 (간략화)
aws rds create-db-proxy \
  --db-proxy-name my-proxy \
  --engine-family POSTGRESQL \
  --auth '[{
    "AuthScheme": "SECRETS",
    "SecretArn": "arn:aws:secretsmanager:...:secret:db-creds",
    "IAMAuth": "REQUIRED"
  }]' \
  --role-arn arn:aws:iam::123456789012:role/RDSProxyRole \
  --vpc-subnet-ids subnet-abc123 subnet-def456
```

---

## 13. Lambda Layers

### 13.1 Layer란

Lambda Layer(*Lambda Layer - 라이브러리, 사용자 정의 런타임, 설정 파일 등 공통 코드를 패키징하여 여러 함수에서 공유할 수 있는 ZIP 아카이브*)는 함수 코드와 분리된 공유 라이브러리이다.

```
Layer 없이:                          Layer 사용:

┌───────────┐ ┌───────────┐          ┌───────────┐ ┌───────────┐
│ Function A │ │ Function B │         │ Function A │ │ Function B │
│            │ │            │         │ (코드만)    │ │ (코드만)    │
│ axios      │ │ axios      │         └─────┬─────┘ └─────┬─────┘
│ lodash     │ │ lodash     │               │              │
│ sharp      │ │ sharp      │               └──────┬───────┘
│ 코드       │ │ 코드       │                      │
└───────────┘ └───────────┘              ┌─────────┴──────────┐
                                         │   Shared Layer      │
각 함수에 동일한 의존성이                    │   axios, lodash,    │
중복으로 포함됨                             │   sharp             │
                                         └────────────────────┘
                                         의존성을 한 번만 관리
```

### 13.2 Layer 생성과 사용

```bash
# 1. Layer용 디렉토리 구조 생성 (Node.js의 경우 nodejs/ 디렉토리 필수)
mkdir -p my-layer/nodejs
cd my-layer/nodejs
npm init -y
npm install axios lodash

# 2. ZIP 파일 생성
cd ..
zip -r my-shared-layer.zip nodejs/

# 3. Layer 발행
aws lambda publish-layer-version \
  --layer-name shared-utils \
  --description "공통 유틸리티 라이브러리" \
  --zip-file fileb://my-shared-layer.zip \
  --compatible-runtimes nodejs18.x nodejs20.x nodejs22.x

# 4. 함수에 Layer 연결 (최대 5개)
aws lambda update-function-configuration \
  --function-name my-function \
  --layers arn:aws:lambda:ap-northeast-2:123456789012:layer:shared-utils:1
```

```javascript
// Layer에 포함된 라이브러리를 일반적으로 import하면 된다
import axios from 'axios';
import _ from 'lodash';

export const handler = async (event) => {
  const response = await axios.get('https://api.example.com/data');
  const uniqueItems = _.uniqBy(response.data, 'id');
  // ...
};
```

### 13.3 Layer 사용 시 주의사항

| 항목 | 제한/권장 |
|------|----------|
| **함수당 최대 Layer 수** | 5개 |
| **전체 크기 제한** | 함수 코드 + 모든 Layer 합산 250MB (압축 해제 후) |
| **디렉토리 구조** | Node.js: `nodejs/node_modules/`, Python: `python/` |
| **버전 관리** | Layer는 불변(immutable), 업데이트 시 새 버전이 생성됨 |

> **실무 팁**: Layer는 **자주 변하지 않는 공통 의존성**에 적합하다. 자주 변경되는 비즈니스 로직은 함수 코드에 두고, 안정적인 라이브러리(aws-sdk 확장, 유틸리티, 바이너리)를 Layer로 분리하라. 함수 코드만 업데이트할 때 배포 패키지 크기가 작아져 배포 속도가 빨라진다.

---

## 자주 하는 실수

| 실수 | 설명 | 올바른 접근 |
|------|------|------------|
| **핸들러 안에서 SDK 클라이언트 초기화** | 매 호출마다 초기화 비용 발생 | 핸들러 밖에서 초기화하여 실행 컨텍스트 재사용 |
| **환경 변수에 비밀 정보 저장** | 콘솔에서 평문으로 노출됨 | Secrets Manager 또는 SSM Parameter Store 사용 |
| **모든 함수에 `AdministratorAccess` 역할** | 보안 사고 시 전체 계정이 위험 | 함수별 최소 권한 정책 부여 |
| **동기식 호출에서 15분 작업 시도** | API Gateway 타임아웃은 29초 | 긴 작업은 비동기(SQS + Lambda)로 분리 |
| **VPC 연결 후 인터넷 접근 불가 방치** | 외부 API 호출이 실패함 | NAT Gateway 또는 VPC Endpoint 설정 |
| **Lambda에서 RDS 직접 연결** | 동시 실행 증가 시 DB 커넥션 고갈 | RDS Proxy를 통해 커넥션 풀링 |
| **콜드 스타트 무시** | 사용자 경험이 불일치 | Provisioned Concurrency 또는 경량 패키지 유지 |
| **거대한 배포 패키지** | 콜드 스타트 시간 증가 | esbuild 번들링, Layer 분리, tree shaking |

---

## AWS CLI 레퍼런스

| 명령어 | 설명 |
|--------|------|
| `aws lambda create-function --function-name NAME --runtime RUNTIME --handler HANDLER --role ROLE --zip-file fileb://FILE` | Lambda 함수 생성 |
| `aws lambda update-function-code --function-name NAME --zip-file fileb://FILE` | 함수 코드 업데이트 |
| `aws lambda update-function-configuration --function-name NAME --memory-size MB --timeout SEC` | 함수 설정 변경 |
| `aws lambda invoke --function-name NAME --payload JSON response.json` | 함수 직접 호출 |
| `aws lambda list-functions` | 함수 목록 조회 |
| `aws lambda get-function --function-name NAME` | 함수 상세 정보 |
| `aws lambda publish-version --function-name NAME` | 새 버전 발행 |
| `aws lambda put-function-concurrency --function-name NAME --reserved-concurrent-executions N` | 예약된 동시성 설정 |
| `aws lambda put-provisioned-concurrency-config --function-name NAME --qualifier VER --provisioned-concurrent-executions N` | 프로비저닝된 동시성 설정 |
| `aws lambda publish-layer-version --layer-name NAME --zip-file fileb://FILE` | Layer 발행 |
| `aws lambda add-permission --function-name NAME --statement-id ID --action lambda:InvokeFunction --principal SERVICE` | 리소스 기반 권한 추가 |
| `aws lambda delete-function --function-name NAME` | 함수 삭제 |

---

## 요약

- **서버리스**는 서버 관리 없이 코드를 실행하는 모델이다. Lambda는 AWS 서버리스의 핵심 컴퓨팅 서비스이다.
- Lambda 함수는 **핸들러, 이벤트, 컨텍스트**로 구성되며, Node.js에서는 ESM(`.mjs`) 방식을 권장한다.
- TypeScript를 사용할 때는 **esbuild**로 번들링하여 단일 파일로 배포하라. `@aws-sdk/*`는 런타임에 포함되어 있으므로 외부로 제외한다.
- 배포 방법은 ZIP 업로드(소규모), SAM(서버리스 특화), CDK(TypeScript 인프라) 중 프로젝트 규모에 맞게 선택한다.
- Lambda는 **API Gateway, S3, EventBridge, SQS, DynamoDB Streams** 등 다양한 이벤트 소스로 트리거된다.
- **API Gateway + Lambda**로 서버 없이 REST API를 구축할 수 있다. 대부분의 경우 HTTP API가 비용 효율적이다.
- **Lambda@Edge**와 **CloudFront Functions**로 엣지에서 A/B 테스트, 보안 헤더 추가, 이미지 최적화, 리다이렉트를 구현한다.
- 민감 정보는 환경 변수가 아닌 **Secrets Manager** 또는 **SSM Parameter Store**에 저장한다.
- **콜드 스타트**를 줄이려면 핸들러 밖에서 SDK를 초기화하고, 패키지 크기를 최소화하며, 필요한 경우 프로비저닝된 동시성을 사용한다.
- VPC 연결 시 인터넷 접근을 위해 **NAT Gateway** 또는 **VPC Endpoint**가 필요하다. RDS 연결 시에는 **RDS Proxy**로 커넥션 풀링을 사용한다.
- **Lambda Layer**로 공통 의존성을 공유하여 배포 패키지 크기를 줄이고 관리를 간소화한다.
- Lambda에는 **실행 시간 15분, 메모리 10GB, 패키지 크기 250MB** 등의 제한이 있다. 이 제한을 넘는 작업은 ECS Fargate나 Step Functions을 고려한다.
