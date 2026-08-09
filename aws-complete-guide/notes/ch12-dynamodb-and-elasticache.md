# Chapter 12: DynamoDB와 ElastiCache: NoSQL and Caching

## 핵심 질문

관계형 데이터베이스가 아닌 NoSQL이 더 적합한 상황은 언제인가? DynamoDB의 파티션 키와 정렬 키는 어떻게 설계해야 하며, 단일 테이블 설계란 무엇인가? 애플리케이션의 응답 속도를 극적으로 개선하려면 캐싱을 어떻게 적용해야 하는가?

---

## 1. DynamoDB 개요

### 1.1 DynamoDB란

DynamoDB(*DynamoDB - AWS가 제공하는 완전 관리형 NoSQL 데이터베이스 서비스. 키-값 및 문서 데이터 모델을 지원하며, 한 자릿수 밀리초의 응답 시간을 제공한다*)는 어떤 규모에서든 한 자릿수 밀리초(single-digit millisecond)의 성능을 보장하는 완전 관리형 NoSQL 데이터베이스이다.

RDS(Chapter 11)가 관계형 데이터베이스의 관리형 서비스라면, DynamoDB는 NoSQL의 관리형 서비스이다. 서버 프로비저닝, 패치, 복제, 백업 등의 운영 부담이 전혀 없다.

### 1.2 RDS vs DynamoDB

| 특성 | RDS (관계형) | DynamoDB (NoSQL) |
|------|-------------|-----------------|
| **데이터 모델** | 테이블, 행, 열 (고정 스키마) | 아이템, 속성 (유연한 스키마) |
| **쿼리 언어** | SQL | API 기반 (GetItem, Query, Scan) |
| **스케일링** | 수직 (인스턴스 크기 변경) | 수평 (파티션 자동 분산) |
| **트랜잭션** | 완전한 ACID | 제한적 트랜잭션 지원 |
| **조인** | 지원 (JOIN) | 미지원 (데이터 비정규화 필요) |
| **지연 시간** | 수~수십 ms | 한 자릿수 ms (일관적) |
| **관리** | 일부 관리 필요 (인스턴스 크기, 파라미터) | 완전 서버리스 |
| **비용 모델** | 인스턴스 시간 과금 | 읽기/쓰기 용량 또는 요청 과금 |

```
아키텍처 비교:

RDS (관계형):
┌──────────────────────────────────┐
│  Primary Instance                │
│  ┌──────┐ ┌──────┐ ┌──────┐    │
│  │users │→│orders│→│items │    │  ← JOIN으로 관계를 맺음
│  └──────┘ └──────┘ └──────┘    │
│  고정 스키마, SQL 쿼리           │
└──────────────────────────────────┘

DynamoDB (NoSQL):
┌──────────────────────────────────────┐
│  Table: orders                       │
│  ┌────────────────────────────────┐  │
│  │ PK=USER#1  SK=ORDER#100       │  │
│  │ { user: "Kim", item: "Book",  │  │  ← 관련 데이터를 한 아이템에 비정규화
│  │   qty: 2, price: 15000 }      │  │
│  └────────────────────────────────┘  │
│  유연한 스키마, API 기반 접근         │
└──────────────────────────────────────┘
```

### 1.3 DynamoDB가 적합한 경우

| 적합한 상황 | 이유 |
|------------|------|
| **밀리초 단위 응답이 필요한 경우** | 일관된 한 자릿수 ms 지연 |
| **대규모 트래픽과 자동 스케일링** | 파티션 자동 분산, 초당 수백만 요청 처리 가능 |
| **유연한 스키마가 필요한 경우** | 아이템마다 다른 속성을 가질 수 있음 |
| **서버리스 아키텍처** | Lambda와의 자연스러운 통합 (둘 다 완전 관리형) |
| **키-값 접근이 주된 패턴** | 사용자 프로필, 세션 데이터, 게임 상태 등 |

> **핵심 통찰**: DynamoDB와 RDS의 선택은 "어느 것이 더 좋은가"가 아니라 **"접근 패턴이 무엇인가"**의 문제이다. 접근 패턴이 명확하고 키 기반 조회가 대부분이면 DynamoDB가 더 적합하다. 반면 복잡한 조인, 애드혹 쿼리, 보고서 생성이 주된 작업이면 RDS가 더 적합하다. 두 가지를 **함께 사용하는 것**도 매우 일반적이다 (예: 주문 처리는 RDS, 세션/캐시는 DynamoDB).

---

## 2. DynamoDB 핵심 개념

### 2.1 테이블, 아이템, 속성

DynamoDB의 데이터 구조는 관계형 데이터베이스와 용어가 다르다.

| DynamoDB | RDS (관계형) | 설명 |
|----------|-------------|------|
| **테이블(Table)** | 테이블 | 데이터의 컬렉션 |
| **아이템(Item)** | 행(Row) | 테이블 내의 단일 데이터 레코드 |
| **속성(Attribute)** | 열(Column) | 아이템의 개별 데이터 필드 |

핵심적인 차이점: RDS에서는 모든 행이 동일한 열을 가져야 하지만, DynamoDB에서는 **같은 테이블의 아이템이라도 서로 다른 속성을 가질 수 있다** (기본 키 속성만 필수).

```
DynamoDB 테이블 예시 (users):

┌─────────┬──────────────┬──────────────┬───────────┬──────────┐
│ userId  │ name         │ email        │ age       │ company  │
│ (PK)    │              │              │           │          │
├─────────┼──────────────┼──────────────┼───────────┼──────────┤
│ U001    │ Kim          │ kim@mail.com │ 28        │          │ ← company 없음 (OK)
│ U002    │ Lee          │ lee@mail.com │           │ ACME     │ ← age 없음 (OK)
│ U003    │ Park         │ park@co.kr   │ 35        │ XYZ Inc  │
└─────────┴──────────────┴──────────────┴───────────┴──────────┘
  ↑ 기본 키만 필수, 나머지 속성은 아이템마다 다를 수 있다
```

### 2.2 데이터 타입

DynamoDB는 세 가지 범주의 데이터 타입을 지원한다.

| 범주 | 타입 | 설명 | 예시 |
|------|------|------|------|
| **스칼라** | `S` (String) | 문자열 | `"Kim"` |
| | `N` (Number) | 숫자 (정수, 소수) | `42`, `3.14` |
| | `B` (Binary) | 바이너리 데이터 | Base64 인코딩 |
| | `BOOL` (Boolean) | 참/거짓 | `true`, `false` |
| | `NULL` (Null) | 값 없음 | `null` |
| **문서** | `M` (Map) | JSON 객체 같은 중첩 구조 | `{ "city": "Seoul", "zip": "06000" }` |
| | `L` (List) | JSON 배열 같은 순서 있는 컬렉션 | `["red", "blue", "green"]` |
| **집합** | `SS` (String Set) | 중복 없는 문자열 집합 | `["tag1", "tag2"]` |
| | `NS` (Number Set) | 중복 없는 숫자 집합 | `[1, 2, 3]` |
| | `BS` (Binary Set) | 중복 없는 바이너리 집합 | |

### 2.3 기본 키 (Primary Key)

DynamoDB 테이블의 기본 키는 두 가지 유형이 있다. 기본 키 설계는 DynamoDB에서 **가장 중요한 결정**이다. 한 번 생성하면 변경할 수 없으므로 신중하게 설계해야 한다.

**1. 파티션 키 단독 (Simple Primary Key):**

파티션 키(*Partition Key - DynamoDB가 데이터를 물리적 파티션에 분산 저장할 때 사용하는 키. 해시 함수를 통해 어떤 파티션에 저장할지 결정한다*)만으로 기본 키를 구성한다. 파티션 키 값이 고유해야 한다.

```
파티션 키 단독 (userId가 파티션 키):

                    해시 함수
userId="U001" ─────────────→ 파티션 A ──→ { userId: "U001", name: "Kim" }
userId="U002" ─────────────→ 파티션 B ──→ { userId: "U002", name: "Lee" }
userId="U003" ─────────────→ 파티션 A ──→ { userId: "U003", name: "Park" }

→ 같은 파티션 키 값을 가진 아이템은 존재할 수 없다 (1:1)
```

**2. 복합 키 (Composite Primary Key):**

파티션 키 + 정렬 키(*Sort Key - 같은 파티션 키를 가진 아이템들을 정렬하는 키. 파티션 키와 정렬 키의 조합이 고유하면 된다*)의 조합으로 기본 키를 구성한다. 파티션 키는 같을 수 있지만, 파티션 키 + 정렬 키의 조합이 고유해야 한다.

```
복합 키 (userId가 파티션 키, orderId가 정렬 키):

파티션 키(PK)   정렬 키(SK)    데이터
─────────────────────────────────────────────
USER#kim       ORDER#001     { item: "Book", amount: 15000 }
USER#kim       ORDER#002     { item: "Pen", amount: 3000 }    ← 같은 PK, 다른 SK (OK)
USER#lee       ORDER#001     { item: "Laptop", amount: 1500000 }
USER#lee       ORDER#002     { item: "Mouse", amount: 25000 }

→ PK + SK 조합이 고유하면 된다
→ 같은 PK의 아이템들은 SK 순서대로 정렬되어 물리적으로 함께 저장된다
```

### 2.4 파티션 키 설계 원칙

파티션 키는 DynamoDB 성능의 핵심이다. 잘못된 파티션 키는 핫 파티션(*Hot Partition - 특정 파티션에 트래픽이 집중되는 현상. 전체 처리량이 충분해도 해당 파티션에서 스로틀링이 발생한다*)을 만들어 성능을 저하시킨다.

| 원칙 | 나쁜 예 | 좋은 예 |
|------|---------|---------|
| **높은 카디널리티** | `status` (active/inactive: 2가지) | `userId` (수백만 가지) |
| **균등한 분포** | `date` (특정 날짜에 트래픽 집중) | `userId` (사용자 간 균등 분산) |
| **자주 쿼리하는 값** | 거의 사용하지 않는 내부 ID | 실제 접근 패턴에서 사용하는 키 |

```
나쁜 파티션 키 (status):

status="active"  → 파티션 A: ████████████████ (99% 데이터 집중 = 핫 파티션!)
status="inactive" → 파티션 B: █ (1%)

좋은 파티션 키 (userId):

userId="U001" → 파티션 A: ██
userId="U002" → 파티션 B: ██
userId="U003" → 파티션 C: ██    ← 고르게 분산
userId="U004" → 파티션 A: ██
...
```

> **실무 팁**: 파티션 키로 날짜(`2024-01-15`)를 사용하면 **오늘 날짜 파티션에 모든 쓰기가 집중**되어 핫 파티션이 된다. 시계열 데이터를 저장한다면, 파티션 키를 `deviceId`로, 정렬 키를 `timestamp`로 사용하여 디바이스 단위로 시간순 데이터를 저장하는 것이 올바른 설계이다.

---

## 3. 읽기/쓰기 용량 모드

### 3.1 온디맨드 모드 vs 프로비저닝 모드

DynamoDB의 비용과 처리량은 용량 모드(*Capacity Mode - 테이블의 읽기/쓰기 처리량을 관리하는 방식. 온디맨드와 프로비저닝 두 가지 모드가 있다*)에 의해 결정된다.

| 특성 | 온디맨드(On-Demand) | 프로비저닝(Provisioned) |
|------|-------------------|----------------------|
| **용량 설정** | 불필요 (자동) | RCU/WCU를 직접 지정 |
| **과금** | 요청 수 기반 (사용한 만큼) | 프로비저닝한 용량 기반 |
| **스케일링** | 즉시 자동 | Auto Scaling 설정 필요 |
| **비용** | 요청당 단가가 더 비쌈 | 단가가 더 저렴 |
| **적합한 경우** | 예측 불가능한 트래픽, 새 프로젝트 | 예측 가능한 트래픽, 비용 최적화 |

### 3.2 RCU와 WCU

프로비저닝 모드에서는 RCU(*Read Capacity Unit - 초당 하나의 강력한 일관성 읽기 또는 두 번의 최종 일관성 읽기를 수행하는 용량 단위. 최대 4KB 아이템 기준*)와 WCU(*Write Capacity Unit - 초당 하나의 쓰기를 수행하는 용량 단위. 최대 1KB 아이템 기준*)를 직접 설정한다.

```
RCU 계산:

강력한 일관성 읽기 (Strongly Consistent):
  4KB 아이템 1개 읽기 = 1 RCU
  8KB 아이템 1개 읽기 = 2 RCU (올림)

최종 일관성 읽기 (Eventually Consistent):
  4KB 아이템 1개 읽기 = 0.5 RCU (강력한 일관성의 절반)

WCU 계산:
  1KB 아이템 1개 쓰기 = 1 WCU
  3KB 아이템 1개 쓰기 = 3 WCU (올림)

예시: 초당 10개의 8KB 아이템을 강력한 일관성으로 읽으려면?
  → 아이템당 2 RCU × 10개 = 20 RCU 필요
```

### 3.3 읽기 일관성

| 일관성 | 설명 | RCU 비용 | 적합한 경우 |
|--------|------|---------|------------|
| **최종 일관성(Eventually Consistent)** | 쓰기 후 약간의 지연이 있을 수 있음 (보통 1초 이내) | 0.5 RCU/4KB | 대부분의 읽기 (기본값) |
| **강력한 일관성(Strongly Consistent)** | 가장 최신의 데이터를 보장 | 1 RCU/4KB | 결제, 재고 등 정확성이 중요한 경우 |

> **비용 주의**: 프로비저닝 모드에서 RCU/WCU를 너무 높게 설정하면 불필요한 비용이 발생하고, 너무 낮게 설정하면 스로틀링(*Throttling - 설정된 용량을 초과하는 요청이 거부되는 현상*)이 발생한다. **새 프로젝트는 온디맨드 모드로 시작**하여 트래픽 패턴을 파악한 후, 안정적인 트래픽이 확인되면 프로비저닝 모드 + Auto Scaling으로 전환하는 것이 비용 효율적이다. 온디맨드에서 프로비저닝으로 전환하면 **60~80% 비용 절감**이 가능하다.

---

## 4. CRUD 작업

### 4.1 Node.js SDK 설정

DynamoDB와 상호작용하려면 두 가지 SDK 패키지가 필요하다.

```bash
# DynamoDB SDK 설치
npm install @aws-sdk/client-dynamodb @aws-sdk/lib-dynamodb
```

- `@aws-sdk/client-dynamodb`: 저수준 클라이언트. DynamoDB의 네이티브 타입 형식(`{ S: "Kim" }`)을 직접 사용한다.
- `@aws-sdk/lib-dynamodb`: 고수준 Document Client. JavaScript 네이티브 타입(`"Kim"`)을 자동 변환해준다.

```typescript
// 클라이언트 초기화 (Lambda에서는 핸들러 밖에 선언)
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient } from '@aws-sdk/lib-dynamodb';

const client = new DynamoDBClient({ region: 'ap-northeast-2' });
const docClient = DynamoDBDocumentClient.from(client, {
  marshallOptions: {
    removeUndefinedValues: true,  // undefined 속성 자동 제거
  },
});
```

```
저수준 vs 고수준 클라이언트:

저수준 (client-dynamodb):
{
  "userId": { "S": "U001" },
  "name": { "S": "Kim" },
  "age": { "N": "28" },
  "tags": { "L": [{ "S": "dev" }, { "S": "aws" }] }
}

고수준 (lib-dynamodb - Document Client):
{
  "userId": "U001",
  "name": "Kim",
  "age": 28,
  "tags": ["dev", "aws"]
}

→ Document Client가 JavaScript ↔ DynamoDB 타입 변환을 자동으로 처리
```

### 4.2 PutItem (쓰기)

```typescript
import { PutCommand } from '@aws-sdk/lib-dynamodb';

// 아이템 생성/덮어쓰기
const result = await docClient.send(new PutCommand({
  TableName: 'users',
  Item: {
    userId: 'U001',
    name: 'Kim',
    email: 'kim@example.com',
    age: 28,
    address: {
      city: 'Seoul',
      district: 'Gangnam',
    },
    tags: ['developer', 'aws'],
    createdAt: new Date().toISOString(),
  },
}));

// 조건부 쓰기: 이미 존재하면 덮어쓰지 않음
await docClient.send(new PutCommand({
  TableName: 'users',
  Item: { userId: 'U001', name: 'Kim' },
  ConditionExpression: 'attribute_not_exists(userId)',  // userId가 없을 때만 쓰기
}));
```

### 4.3 GetItem (단일 읽기)

```typescript
import { GetCommand } from '@aws-sdk/lib-dynamodb';

// 기본 키로 단일 아이템 읽기
const result = await docClient.send(new GetCommand({
  TableName: 'users',
  Key: {
    userId: 'U001',  // 파티션 키 (+ 정렬 키가 있으면 함께 지정)
  },
}));

console.log(result.Item);
// { userId: 'U001', name: 'Kim', email: 'kim@example.com', ... }

// 특정 속성만 가져오기 (Projection)
const result2 = await docClient.send(new GetCommand({
  TableName: 'users',
  Key: { userId: 'U001' },
  ProjectionExpression: '#n, email',  // name은 예약어라 표현식 이름 사용
  ExpressionAttributeNames: { '#n': 'name' },
}));
```

### 4.4 UpdateItem (수정)

```typescript
import { UpdateCommand } from '@aws-sdk/lib-dynamodb';

// 특정 속성만 업데이트 (전체 아이템을 덮어쓰지 않음)
const result = await docClient.send(new UpdateCommand({
  TableName: 'users',
  Key: { userId: 'U001' },
  UpdateExpression: 'SET #n = :name, age = :age, updatedAt = :now',
  ExpressionAttributeNames: { '#n': 'name' },
  ExpressionAttributeValues: {
    ':name': 'Kim Minsu',
    ':age': 29,
    ':now': new Date().toISOString(),
  },
  ReturnValues: 'ALL_NEW',  // 업데이트된 전체 아이템을 반환
}));

console.log(result.Attributes);  // 업데이트 후의 전체 아이템

// 원자적 카운터 증가
await docClient.send(new UpdateCommand({
  TableName: 'articles',
  Key: { articleId: 'A001' },
  UpdateExpression: 'SET viewCount = viewCount + :inc',
  ExpressionAttributeValues: { ':inc': 1 },
}));
```

### 4.5 DeleteItem (삭제)

```typescript
import { DeleteCommand } from '@aws-sdk/lib-dynamodb';

await docClient.send(new DeleteCommand({
  TableName: 'users',
  Key: { userId: 'U001' },
}));

// 조건부 삭제: status가 inactive일 때만 삭제
await docClient.send(new DeleteCommand({
  TableName: 'users',
  Key: { userId: 'U001' },
  ConditionExpression: '#s = :status',
  ExpressionAttributeNames: { '#s': 'status' },
  ExpressionAttributeValues: { ':status': 'inactive' },
}));
```

### 4.6 Query (조건부 다건 읽기)

Query(*Query - 파티션 키를 기준으로 아이템을 검색하는 작업. 정렬 키에 조건을 걸어 범위 검색이 가능하며, 매우 효율적이다*)는 DynamoDB에서 **가장 많이 사용하는 작업**이다.

```typescript
import { QueryCommand } from '@aws-sdk/lib-dynamodb';

// 특정 사용자의 주문 목록 조회 (복합 키: userId + orderId)
const result = await docClient.send(new QueryCommand({
  TableName: 'orders',
  KeyConditionExpression: 'userId = :uid AND orderId BETWEEN :start AND :end',
  ExpressionAttributeValues: {
    ':uid': 'USER#kim',
    ':start': 'ORDER#2024-01',
    ':end': 'ORDER#2024-12',
  },
  ScanIndexForward: true,  // true: 오름차순 (기본), false: 내림차순
  Limit: 20,               // 최대 20개 아이템
}));

console.log(result.Items);  // 조건에 맞는 아이템 배열
console.log(result.Count);  // 반환된 아이템 수

// 필터 추가 (정렬 키 조건 후에 추가 필터링)
const filtered = await docClient.send(new QueryCommand({
  TableName: 'orders',
  KeyConditionExpression: 'userId = :uid',
  FilterExpression: '#s = :status AND totalAmount > :min',
  ExpressionAttributeNames: { '#s': 'status' },
  ExpressionAttributeValues: {
    ':uid': 'USER#kim',
    ':status': 'completed',
    ':min': 10000,
  },
}));
```

### 4.7 Scan (전체 테이블 스캔)

Scan(*Scan - 테이블의 모든 아이템을 순차적으로 읽는 작업. 전체 테이블을 스캔하므로 비용이 높고 느리다*)은 테이블의 모든 아이템을 읽는다. **가능한 한 사용을 피해야 한다.**

```typescript
import { ScanCommand } from '@aws-sdk/lib-dynamodb';

// ❌ 전체 스캔: 테이블이 커질수록 느려지고 비용이 증가
const result = await docClient.send(new ScanCommand({
  TableName: 'users',
  FilterExpression: 'age > :minAge',
  ExpressionAttributeValues: { ':minAge': 25 },
}));

// 대량 데이터를 페이지네이션으로 스캔해야 하는 경우
let lastKey = undefined;
const allItems = [];

do {
  const result = await docClient.send(new ScanCommand({
    TableName: 'users',
    ExclusiveStartKey: lastKey,
    Limit: 100,
  }));

  allItems.push(...(result.Items || []));
  lastKey = result.LastEvaluatedKey;
} while (lastKey);
```

> **핵심 통찰**: DynamoDB 설계의 핵심 원칙은 **"Scan을 사용하지 않도록 테이블을 설계하라"**이다. Scan은 전체 테이블을 읽으므로 아이템 수에 비례하여 비용과 시간이 증가한다. 반면 Query는 파티션 키로 필요한 데이터만 정확히 찾으므로 테이블이 아무리 커도 성능이 일정하다. Scan이 필요하다면 그것은 **테이블 설계가 잘못되었다**는 신호이다.

### 4.8 Query vs Scan 비교

| 특성 | Query | Scan |
|------|-------|------|
| **작동 방식** | 파티션 키로 데이터 위치를 바로 찾음 | 전체 테이블을 순차적으로 읽음 |
| **성능** | O(1) 파티션 접근 + 정렬 키 범위 | O(N) 전체 데이터 |
| **비용** | 읽은 데이터 크기만큼만 과금 | 전체 스캔 데이터 크기에 과금 |
| **필수 조건** | 파티션 키 지정 필수 | 조건 없이 전체 스캔 |
| **사용 빈도** | 주 작업 (99%+) | 데이터 마이그레이션, 분석 등 예외적 사용 |

---

## 5. 보조 인덱스

### 5.1 왜 보조 인덱스가 필요한가

기본 키로만 Query할 수 있다면 접근 패턴이 제한된다. 예를 들어 `userId`가 파티션 키인 테이블에서 `email`로 사용자를 찾으려면 Scan을 해야 한다. 보조 인덱스(*Secondary Index - 기본 키 이외의 속성으로 효율적인 Query를 가능하게 하는 추가 인덱스*)를 사용하면 다른 속성으로도 효율적인 Query가 가능하다.

### 5.2 GSI (Global Secondary Index)

GSI(*Global Secondary Index - 테이블과 다른 파티션 키와 정렬 키를 가진 인덱스. 테이블의 모든 파티션에 걸쳐 동작한다*)는 **테이블과 완전히 다른 파티션 키와 정렬 키**로 Query할 수 있게 해준다.

```
원본 테이블:                           GSI (email-index):
PK: userId    SK: -                    PK: email         SK: -

┌────────┬──────────────────┐         ┌──────────────────┬────────┐
│ U001   │ email: kim@co.kr │   ──→   │ kim@co.kr        │ U001   │
│ U002   │ email: lee@co.kr │   ──→   │ lee@co.kr        │ U002   │
│ U003   │ email: park@co.kr│   ──→   │ park@co.kr       │ U003   │
└────────┴──────────────────┘         └──────────────────┴────────┘

원본: userId로 Query           GSI: email로 Query
```

```typescript
// GSI를 사용한 Query
const result = await docClient.send(new QueryCommand({
  TableName: 'users',
  IndexName: 'email-index',  // GSI 이름
  KeyConditionExpression: 'email = :email',
  ExpressionAttributeValues: { ':email': 'kim@example.com' },
}));
```

### 5.3 LSI (Local Secondary Index)

LSI(*Local Secondary Index - 테이블과 같은 파티션 키를 사용하면서 다른 정렬 키로 Query할 수 있는 인덱스. 테이블 생성 시에만 정의할 수 있다*)는 **같은 파티션 키, 다른 정렬 키**로 Query할 수 있게 해준다.

```
원본 테이블:                           LSI (createdAt-index):
PK: userId    SK: orderId              PK: userId    SK: createdAt

┌────────┬──────────┬────────────┐    ┌────────┬────────────┬──────────┐
│ U001   │ ORD#001  │ 2024-03-15 │→   │ U001   │ 2024-01-10 │ ORD#003  │
│ U001   │ ORD#002  │ 2024-01-10 │→   │ U001   │ 2024-02-20 │ ORD#003  │
│ U001   │ ORD#003  │ 2024-02-20 │→   │ U001   │ 2024-03-15 │ ORD#001  │
└────────┴──────────┴────────────┘    └────────┴────────────┴──────────┘

원본: userId + orderId로 Query    LSI: userId + createdAt으로 Query
→ "사용자의 주문을 날짜순으로"
```

### 5.4 GSI vs LSI 비교

| 특성 | GSI (Global) | LSI (Local) |
|------|-------------|-------------|
| **파티션 키** | 테이블과 다를 수 있음 | 테이블과 같아야 함 |
| **정렬 키** | 테이블과 다를 수 있음 | 테이블과 달라야 함 |
| **생성 시점** | 언제든 추가/삭제 가능 | 테이블 생성 시에만 정의 |
| **최대 개수** | 테이블당 20개 | 테이블당 5개 |
| **용량** | 별도의 RCU/WCU 필요 | 테이블의 RCU/WCU 공유 |
| **일관성** | 최종 일관성만 지원 | 강력한 일관성 지원 |
| **사용 빈도** | 매우 높음 (주로 GSI 사용) | 제한적 (LSI가 필요한 경우가 드묾) |

> **실무 팁**: 실무에서는 **GSI를 주로 사용**한다. LSI는 테이블 생성 시에만 정의할 수 있고 파티션 키를 변경할 수 없어 유연성이 떨어진다. GSI는 언제든 추가/삭제할 수 있으므로 접근 패턴이 변경되어도 대응이 가능하다. 단, GSI는 별도의 읽기/쓰기 용량을 소비하므로 **비용에 주의**하라.

---

## 6. DynamoDB Streams

### 6.1 Streams란

DynamoDB Streams(*DynamoDB Streams - 테이블의 아이템이 변경될 때 변경 이벤트를 시간 순서대로 캡처하는 기능. 최대 24시간 동안 이벤트를 보관한다*)는 테이블에서 발생하는 모든 변경(생성, 수정, 삭제)을 시간 순서대로 기록하는 변경 데이터 캡처(*Change Data Capture*) 기능이다.

```
DynamoDB Streams 동작 흐름:

   쓰기/수정/삭제
        │
        ↓
┌───────────────┐     ┌──────────────┐     ┌──────────────────┐
│  DynamoDB     │────→│  Stream      │────→│  Lambda          │
│  Table        │     │  (변경 이벤트) │     │  (트리거)         │
└───────────────┘     └──────────────┘     └────────┬─────────┘
                                                    │
                                         ┌──────────┼──────────┐
                                         ↓          ↓          ↓
                                    검색 인덱스   알림 발송   다른 테이블
                                    (OpenSearch)  (SNS/SES)  (집계/복제)
```

### 6.2 Stream View Type

Streams에서 캡처할 데이터의 범위를 설정한다.

| View Type | 캡처 내용 | 사용 사례 |
|-----------|----------|----------|
| `KEYS_ONLY` | 변경된 아이템의 키만 | 변경 사실만 알면 되는 경우 |
| `NEW_IMAGE` | 변경 후의 전체 아이템 | 새 데이터를 다른 시스템에 동기화 |
| `OLD_IMAGE` | 변경 전의 전체 아이템 | 변경 전 데이터를 감사 로그에 기록 |
| `NEW_AND_OLD_IMAGES` | 변경 전후의 전체 아이템 | 변경 전후를 비교해야 하는 경우 |

### 6.3 Lambda 트리거 예시

```typescript
// DynamoDB Stream → Lambda: 주문이 생성되면 알림 발송
import { DynamoDBStreamEvent, DynamoDBRecord } from 'aws-lambda';
import { unmarshall } from '@aws-sdk/util-dynamodb';

export const handler = async (event: DynamoDBStreamEvent) => {
  for (const record of event.Records) {
    console.log('이벤트 타입:', record.eventName);  // INSERT, MODIFY, REMOVE

    if (record.eventName === 'INSERT' && record.dynamodb?.NewImage) {
      // DynamoDB 네이티브 타입을 JavaScript 객체로 변환
      const newItem = unmarshall(record.dynamodb.NewImage as any);

      console.log('새 주문:', newItem);
      // { orderId: 'ORD#001', userId: 'USER#kim', amount: 15000, ... }

      await sendOrderNotification(newItem);
    }

    if (record.eventName === 'MODIFY') {
      const oldItem = unmarshall(record.dynamodb!.OldImage as any);
      const newItem = unmarshall(record.dynamodb!.NewImage as any);

      // 주문 상태가 변경되었는지 확인
      if (oldItem.status !== newItem.status) {
        console.log(`상태 변경: ${oldItem.status} → ${newItem.status}`);
        await sendStatusChangeNotification(newItem);
      }
    }
  }
};
```

```bash
# DynamoDB Streams 활성화
aws dynamodb update-table \
  --table-name orders \
  --stream-specification StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES

# Lambda에 Stream 트리거 연결
aws lambda create-event-source-mapping \
  --function-name order-notification \
  --event-source-arn arn:aws:dynamodb:ap-northeast-2:123456789012:table/orders/stream/2024-01-01T00:00:00.000 \
  --starting-position LATEST \
  --batch-size 10
```

---

## 7. 단일 테이블 설계

### 7.1 NoSQL 설계 철학

관계형 데이터베이스는 **데이터 모델링 우선**: 엔티티(Entity)와 관계(Relationship)를 먼저 정의하고, 쿼리는 나중에 SQL로 유연하게 작성한다.

DynamoDB는 **접근 패턴 우선**: 애플리케이션이 어떤 쿼리를 수행해야 하는지를 먼저 정의하고, 그에 맞춰 테이블 구조를 설계한다.

```
관계형 설계 (RDS):

1단계: 엔티티 정의
   users, orders, products, reviews (4개 테이블)

2단계: 관계 정의
   users 1:N orders, orders N:M products, users 1:N reviews

3단계: 쿼리 작성 (필요할 때 JOIN)
   SELECT * FROM orders JOIN users ON ... WHERE ...

DynamoDB 설계:

1단계: 접근 패턴 정의
   - 사용자 정보 조회
   - 사용자의 주문 목록
   - 특정 주문의 상세 정보
   - 사용자의 리뷰 목록

2단계: 접근 패턴에 맞는 키 설계
   PK = USER#userId, SK = PROFILE / ORDER#orderId / REVIEW#reviewId

3단계: 단일 테이블에 모든 엔티티를 저장
```

### 7.2 단일 테이블 설계란

단일 테이블 설계(*Single-Table Design - 관련된 여러 엔티티를 하나의 DynamoDB 테이블에 저장하는 패턴. 파티션 키와 정렬 키의 접두사로 엔티티 타입을 구분한다*)는 관계형 DB에서 여러 테이블로 분리했을 엔티티들을 **하나의 테이블**에 저장하는 패턴이다.

```
단일 테이블 예시 (전자상거래):

┌──────────────┬──────────────────┬──────────┬──────────────┬─────────────┐
│ PK           │ SK               │ Type     │ data1        │ data2       │
├──────────────┼──────────────────┼──────────┼──────────────┼─────────────┤
│ USER#kim     │ PROFILE          │ User     │ name: "Kim"  │ email: ...  │
│ USER#kim     │ ORDER#2024-001   │ Order    │ total: 15000 │ status: ... │
│ USER#kim     │ ORDER#2024-002   │ Order    │ total: 32000 │ status: ... │
│ USER#kim     │ REVIEW#R001      │ Review   │ rating: 5    │ text: ...   │
│ USER#lee     │ PROFILE          │ User     │ name: "Lee"  │ email: ...  │
│ USER#lee     │ ORDER#2024-003   │ Order    │ total: 8000  │ status: ... │
│ PRODUCT#P001 │ METADATA         │ Product  │ name: "Book" │ price: ...  │
│ PRODUCT#P001 │ REVIEW#R001      │ Review   │ userId: kim  │ rating: 5   │
└──────────────┴──────────────────┴──────────┴──────────────┴─────────────┘

접근 패턴 매핑:
  1. 사용자 프로필: PK="USER#kim", SK="PROFILE"                → GetItem
  2. 사용자의 모든 주문: PK="USER#kim", SK begins_with "ORDER#" → Query
  3. 사용자의 모든 데이터: PK="USER#kim"                        → Query
  4. 특정 상품의 모든 리뷰: PK="PRODUCT#P001", SK begins_with "REVIEW#" → Query
```

### 7.3 단일 테이블 설계 구현

```typescript
// 단일 테이블 CRUD 예시

// 1. 사용자 프로필 생성
await docClient.send(new PutCommand({
  TableName: 'app-table',
  Item: {
    PK: 'USER#kim',
    SK: 'PROFILE',
    type: 'User',
    name: 'Kim',
    email: 'kim@example.com',
    createdAt: new Date().toISOString(),
  },
}));

// 2. 주문 생성
await docClient.send(new PutCommand({
  TableName: 'app-table',
  Item: {
    PK: 'USER#kim',
    SK: `ORDER#${new Date().toISOString()}#${orderId}`,
    type: 'Order',
    orderId,
    items: [{ productId: 'P001', qty: 2 }],
    totalAmount: 30000,
    status: 'pending',
  },
}));

// 3. 사용자의 모든 주문 조회
const orders = await docClient.send(new QueryCommand({
  TableName: 'app-table',
  KeyConditionExpression: 'PK = :pk AND begins_with(SK, :sk)',
  ExpressionAttributeValues: {
    ':pk': 'USER#kim',
    ':sk': 'ORDER#',
  },
  ScanIndexForward: false,  // 최신 주문부터 (내림차순)
}));

// 4. 사용자의 모든 데이터 조회 (프로필 + 주문 + 리뷰)
const allUserData = await docClient.send(new QueryCommand({
  TableName: 'app-table',
  KeyConditionExpression: 'PK = :pk',
  ExpressionAttributeValues: { ':pk': 'USER#kim' },
}));

// type 필드로 엔티티를 구분
const profile = allUserData.Items?.find(item => item.type === 'User');
const userOrders = allUserData.Items?.filter(item => item.type === 'Order');
const reviews = allUserData.Items?.filter(item => item.type === 'Review');
```

### 7.4 GSI 오버로딩

단일 테이블 설계에서 GSI를 재활용하여 다양한 접근 패턴을 지원하는 기법이다.

```
GSI 오버로딩 (GSI1):

원본 테이블:                    GSI1 (GSI1PK, GSI1SK):
PK           SK                 GSI1PK          GSI1SK
──────────────────────         ──────────────────────────
USER#kim     PROFILE            kim@co.kr       USER#kim        ← 이메일로 사용자 조회
USER#kim     ORDER#001          ORD#pending     ORDER#2024-03   ← 상태별 주문 조회
PRODUCT#P001 METADATA           CAT#electronics PRODUCT#P001    ← 카테고리별 상품 조회

→ 하나의 GSI로 세 가지 접근 패턴을 지원
```

### 7.5 단일 테이블 vs 다중 테이블

| 특성 | 단일 테이블 | 다중 테이블 |
|------|-----------|-----------|
| **성능** | 한 번의 Query로 관련 데이터 모두 조회 | 여러 테이블에 여러 요청 필요 |
| **비용** | 하나의 테이블만 관리 | 테이블마다 별도 용량/인덱스 |
| **복잡도** | 설계가 어렵고, PK/SK 패턴 이해 필요 | 직관적이고 이해하기 쉬움 |
| **유연성** | 새 접근 패턴 추가 시 GSI 추가 | 새 테이블 생성으로 유연하게 대응 |
| **적합한 경우** | 관련 데이터를 함께 조회하는 경우가 많을 때 | 엔티티 간 관계가 약하거나, 팀이 DynamoDB에 익숙하지 않을 때 |

> **실무 팁**: 단일 테이블 설계가 DynamoDB의 "정석"으로 알려져 있지만, **팀의 경험 수준**에 따라 다중 테이블부터 시작하는 것도 좋은 전략이다. 다중 테이블로 시작하여 접근 패턴을 충분히 파악한 후, 성능이나 비용 최적화가 필요한 시점에 단일 테이블로 마이그레이션해도 늦지 않다.

---

## 8. DynamoDB 테이블 생성과 관리

### 8.1 AWS CLI로 테이블 생성

```bash
# 파티션 키 단독 테이블 생성 (온디맨드)
aws dynamodb create-table \
  --table-name users \
  --attribute-definitions \
    AttributeName=userId,AttributeType=S \
  --key-schema \
    AttributeName=userId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

# 복합 키 테이블 생성 (온디맨드)
aws dynamodb create-table \
  --table-name orders \
  --attribute-definitions \
    AttributeName=userId,AttributeType=S \
    AttributeName=orderId,AttributeType=S \
  --key-schema \
    AttributeName=userId,KeyType=HASH \
    AttributeName=orderId,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST

# 프로비저닝 모드 + Auto Scaling 테이블 생성
aws dynamodb create-table \
  --table-name products \
  --attribute-definitions \
    AttributeName=productId,AttributeType=S \
  --key-schema \
    AttributeName=productId,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=10,WriteCapacityUnits=5
```

### 8.2 GSI 추가

```bash
# 기존 테이블에 GSI 추가
aws dynamodb update-table \
  --table-name users \
  --attribute-definitions \
    AttributeName=email,AttributeType=S \
  --global-secondary-index-updates '[{
    "Create": {
      "IndexName": "email-index",
      "KeySchema": [
        { "AttributeName": "email", "KeyType": "HASH" }
      ],
      "Projection": { "ProjectionType": "ALL" }
    }
  }]'
```

### 8.3 TTL (Time to Live)

TTL(*Time to Live - 아이템의 만료 시간을 지정하여, 만료된 아이템을 DynamoDB가 자동으로 삭제하는 기능. 추가 비용 없이 사용할 수 있다*)을 사용하면 오래된 데이터를 자동으로 정리할 수 있다.

```bash
# TTL 활성화
aws dynamodb update-time-to-live \
  --table-name sessions \
  --time-to-live-specification Enabled=true,AttributeName=expiresAt
```

```typescript
// TTL이 설정된 세션 아이템 생성
await docClient.send(new PutCommand({
  TableName: 'sessions',
  Item: {
    sessionId: 'sess_abc123',
    userId: 'USER#kim',
    data: { cart: ['P001', 'P002'] },
    expiresAt: Math.floor(Date.now() / 1000) + 3600,  // 1시간 후 만료 (Unix 타임스탬프)
  },
}));
```

> **비용 주의**: TTL로 삭제된 아이템은 **WCU를 소비하지 않는다**. 오래된 데이터를 직접 DeleteItem으로 삭제하면 WCU가 소비되지만, TTL을 사용하면 무료로 자동 정리된다. 세션 데이터, 로그, 임시 데이터 등 수명이 있는 데이터에는 반드시 TTL을 설정하라.

---

## 9. ElastiCache 개요

### 9.1 캐싱의 필요성

데이터베이스 쿼리는 애플리케이션의 가장 큰 병목 중 하나이다. 동일한 데이터를 반복해서 읽을 때, 매번 데이터베이스에 접근하는 것은 비효율적이다.

```
캐싱 없이:

클라이언트 → API → DynamoDB/RDS (매번 DB 호출)
                     ~5ms                        ← 100 req/s → DB에 100번 접근

캐싱 적용 후:

                  ┌─ 캐시 히트 → ElastiCache (Redis)  ~0.5ms (95%)
클라이언트 → API ─┤
                  └─ 캐시 미스 → DynamoDB/RDS → 캐시에 저장 ~5ms (5%)

→ 평균 응답 시간: 0.5 × 0.95 + 5 × 0.05 = 0.725ms (약 7배 개선)
→ DB 부하: 100 req/s → 5 req/s (95% 감소)
```

### 9.2 ElastiCache란

ElastiCache(*ElastiCache - AWS의 완전 관리형 인메모리 캐시 서비스. Redis 또는 Memcached 엔진을 사용하여 밀리초 미만의 응답 속도를 제공한다*)는 인메모리(*In-Memory - 데이터를 디스크가 아닌 메모리(RAM)에 저장하여 초고속 읽기/쓰기를 달성하는 방식*)에 데이터를 저장하여 극도로 빠른 읽기/쓰기를 제공하는 관리형 서비스이다.

### 9.3 Redis vs Memcached

| 특성 | Redis | Memcached |
|------|-------|-----------|
| **데이터 구조** | String, Hash, List, Set, Sorted Set 등 풍부 | 단순 키-값만 |
| **데이터 지속성** | 스냅샷, AOF로 디스크에 저장 가능 | 메모리만 (재시작 시 데이터 소실) |
| **복제** | Read Replica 지원 | 미지원 |
| **클러스터** | 클러스터 모드로 수평 확장 | 멀티 노드 분산 |
| **Pub/Sub** | 지원 | 미지원 |
| **Lua 스크립팅** | 지원 | 미지원 |
| **트랜잭션** | MULTI/EXEC 지원 | 미지원 |
| **적합한 경우** | 대부분의 사용 사례 | 단순 캐싱만 필요하고 비용 최소화 |

> **실무 팁**: 특별한 이유가 없다면 **Redis를 선택**하라. Redis는 Memcached의 모든 기능을 포함하면서 데이터 지속성, 복제, 풍부한 데이터 구조 등 훨씬 많은 기능을 제공한다. Memcached가 유리한 경우는 매우 단순한 키-값 캐싱만 필요하고 멀티스레드 성능이 중요할 때뿐이다.

---

## 10. Redis 활용 사례

### 10.1 API 응답 캐싱

가장 기본적이고 효과적인 사용 사례이다.

```typescript
import { createClient } from 'redis';

const redis = createClient({
  url: `redis://${process.env.REDIS_ENDPOINT}:6379`,
});
await redis.connect();

// 캐시를 활용한 사용자 조회
async function getUser(userId: string) {
  const cacheKey = `user:${userId}`;

  // 1. 캐시에서 먼저 조회
  const cached = await redis.get(cacheKey);
  if (cached) {
    console.log('캐시 히트');
    return JSON.parse(cached);
  }

  // 2. 캐시 미스: DB에서 조회
  console.log('캐시 미스 → DB 조회');
  const user = await docClient.send(new GetCommand({
    TableName: 'users',
    Key: { userId },
  }));

  // 3. 결과를 캐시에 저장 (TTL: 300초)
  if (user.Item) {
    await redis.setEx(cacheKey, 300, JSON.stringify(user.Item));
  }

  return user.Item;
}
```

### 10.2 세션 스토어

Redis는 사용자 세션 데이터를 저장하는 데 매우 적합하다.

```typescript
// 세션 저장
async function createSession(sessionId: string, userId: string) {
  const sessionData = {
    userId,
    createdAt: new Date().toISOString(),
    cart: [],
  };

  // HSET: Hash 구조로 세션 데이터 저장
  await redis.hSet(`session:${sessionId}`, {
    userId,
    createdAt: sessionData.createdAt,
    cart: JSON.stringify(sessionData.cart),
  });

  // 세션 만료 시간 설정 (1시간)
  await redis.expire(`session:${sessionId}`, 3600);
}

// 세션 조회
async function getSession(sessionId: string) {
  const session = await redis.hGetAll(`session:${sessionId}`);
  if (!session.userId) return null;

  return {
    ...session,
    cart: JSON.parse(session.cart || '[]'),
  };
}

// 세션의 특정 필드만 업데이트
async function addToCart(sessionId: string, productId: string) {
  const cart = await redis.hGet(`session:${sessionId}`, 'cart');
  const items = JSON.parse(cart || '[]');
  items.push(productId);
  await redis.hSet(`session:${sessionId}`, 'cart', JSON.stringify(items));
}
```

### 10.3 리더보드 (Sorted Set)

Redis의 Sorted Set(*Sorted Set - 각 멤버에 점수(score)가 부여되어 자동으로 정렬되는 Redis 데이터 구조. 리더보드, 랭킹 시스템에 이상적이다*)은 리더보드 구현에 이상적이다.

```typescript
// 점수 업데이트
async function updateScore(userId: string, score: number) {
  await redis.zAdd('leaderboard', { score, value: userId });
}

// 상위 N명 조회
async function getTopPlayers(count: number) {
  // ZREVRANGE: 높은 점수부터 내림차순으로 조회
  const results = await redis.zRangeWithScores('leaderboard', 0, count - 1, {
    REV: true,
  });

  return results.map((entry, index) => ({
    rank: index + 1,
    userId: entry.value,
    score: entry.score,
  }));
}

// 특정 사용자의 순위 조회
async function getUserRank(userId: string) {
  // ZREVRANK: 내림차순 기준 순위 (0부터 시작)
  const rank = await redis.zRevRank('leaderboard', userId);
  return rank !== null ? rank + 1 : null;  // 1-based 순위로 변환
}

// 사용 예시
await updateScore('player:kim', 1500);
await updateScore('player:lee', 2300);
await updateScore('player:park', 1800);

const top3 = await getTopPlayers(3);
// [{ rank: 1, userId: 'player:lee', score: 2300 },
//  { rank: 2, userId: 'player:park', score: 1800 },
//  { rank: 3, userId: 'player:kim', score: 1500 }]
```

### 10.4 Rate Limiting

API 요청 속도를 제한하는 데 Redis가 효과적이다.

```typescript
// 슬라이딩 윈도우 Rate Limiter
async function checkRateLimit(
  clientId: string,
  maxRequests: number,
  windowSeconds: number
): Promise<{ allowed: boolean; remaining: number }> {
  const key = `ratelimit:${clientId}`;
  const now = Date.now();
  const windowStart = now - windowSeconds * 1000;

  // 트랜잭션으로 원자적 실행
  const multi = redis.multi();
  multi.zRemRangeByScore(key, 0, windowStart);   // 윈도우 밖의 오래된 요청 제거
  multi.zAdd(key, { score: now, value: `${now}` }); // 현재 요청 추가
  multi.zCard(key);                                  // 윈도우 내 요청 수 조회
  multi.expire(key, windowSeconds);                  // TTL 설정

  const results = await multi.exec();
  const requestCount = results?.[2] as number;

  return {
    allowed: requestCount <= maxRequests,
    remaining: Math.max(0, maxRequests - requestCount),
  };
}

// 사용 예시: 분당 100요청 제한
const { allowed, remaining } = await checkRateLimit('user:kim', 100, 60);
if (!allowed) {
  return { statusCode: 429, body: 'Too Many Requests' };
}
```

---

## 11. 캐싱 전략

### 11.1 Cache-Aside (Lazy Loading)

Cache-Aside(*Cache-Aside - 애플리케이션이 캐시를 직접 관리하는 패턴. 캐시 미스 시 DB에서 데이터를 가져와 캐시에 저장한다. Lazy Loading이라고도 한다*)는 가장 널리 사용되는 캐싱 패턴이다.

```
Cache-Aside 흐름:

1. 캐시에서 조회
   App ──→ Redis: GET user:123
         ← 캐시 히트 → 바로 반환

   App ──→ Redis: GET user:123
         ← 캐시 미스 (null)
              │
2. DB에서 조회  ↓
   App ──→ DynamoDB: GetItem(userId=123)
         ← { name: "Kim", ... }
              │
3. 캐시에 저장  ↓
   App ──→ Redis: SETEX user:123 300 '{"name":"Kim",...}'
```

```typescript
// Cache-Aside 패턴 구현
async function getUserCacheAside(userId: string) {
  const cacheKey = `user:${userId}`;

  // 1. 캐시 조회
  const cached = await redis.get(cacheKey);
  if (cached) return JSON.parse(cached);

  // 2. DB 조회
  const { Item } = await docClient.send(new GetCommand({
    TableName: 'users',
    Key: { userId },
  }));

  // 3. 캐시 저장
  if (Item) {
    await redis.setEx(cacheKey, 300, JSON.stringify(Item));
  }

  return Item;
}
```

**장점**: 요청된 데이터만 캐시하므로 메모리 효율적. 캐시 장애 시에도 DB에서 직접 조회 가능.

**단점**: 첫 요청은 항상 캐시 미스 (콜드 스타트). 데이터가 변경되어도 TTL까지 오래된 데이터를 반환할 수 있음.

### 11.2 Write-Through

Write-Through(*Write-Through - 데이터를 DB에 쓸 때 동시에 캐시에도 쓰는 패턴. 캐시와 DB가 항상 동기화되어 있다*)는 쓰기 시점에 캐시를 함께 업데이트하여 일관성을 보장한다.

```
Write-Through 흐름:

1. DB에 쓰기
   App ──→ DynamoDB: PutItem(userId=123, name="Kim")
              │
2. 캐시에도 쓰기  ↓
   App ──→ Redis: SETEX user:123 300 '{"name":"Kim",...}'
```

```typescript
// Write-Through 패턴 구현
async function updateUserWriteThrough(userId: string, updates: Record<string, any>) {
  // 1. DB에 업데이트
  const result = await docClient.send(new UpdateCommand({
    TableName: 'users',
    Key: { userId },
    UpdateExpression: 'SET #n = :name, email = :email',
    ExpressionAttributeNames: { '#n': 'name' },
    ExpressionAttributeValues: {
      ':name': updates.name,
      ':email': updates.email,
    },
    ReturnValues: 'ALL_NEW',
  }));

  // 2. 캐시도 업데이트
  const cacheKey = `user:${userId}`;
  await redis.setEx(cacheKey, 300, JSON.stringify(result.Attributes));

  return result.Attributes;
}
```

**장점**: 캐시와 DB가 항상 동기화. 읽기 시 항상 최신 데이터.

**단점**: 쓰기 지연 증가 (DB + 캐시 두 번 쓰기). 읽히지 않는 데이터도 캐시에 저장될 수 있음.

### 11.3 TTL 기반 캐시 무효화

```typescript
// TTL 전략 가이드라인
const TTL_CONFIG = {
  userProfile: 300,     // 5분: 자주 변경되지 않는 프로필
  productList: 60,      // 1분: 비교적 자주 갱신되는 목록
  searchResults: 30,    // 30초: 자주 변하는 검색 결과
  session: 3600,        // 1시간: 세션 데이터
  config: 3600 * 24,   // 24시간: 거의 변하지 않는 설정
};

// 명시적 캐시 무효화 (데이터 변경 시)
async function invalidateCache(userId: string) {
  await redis.del(`user:${userId}`);
  await redis.del(`user:${userId}:orders`);
}
```

### 11.4 캐싱 전략 비교

| 전략 | 읽기 성능 | 쓰기 성능 | 데이터 일관성 | 적합한 상황 |
|------|----------|----------|-------------|------------|
| **Cache-Aside** | 첫 요청 느림, 이후 빠름 | 영향 없음 | TTL까지 오래된 데이터 가능 | 읽기 중심, 일관성이 덜 중요 |
| **Write-Through** | 항상 빠름 | 느려짐 (두 번 쓰기) | 항상 최신 | 읽기/쓰기 모두 빈번, 일관성 중요 |
| **Write-Behind** | 항상 빠름 | 빠름 (비동기 쓰기) | 일시적 불일치 가능 | 쓰기 성능이 중요, 일시적 불일치 허용 |

> **핵심 통찰**: 캐싱에서 가장 어려운 문제는 **캐시 무효화**이다. "컴퓨터 과학에서 어려운 두 가지: 캐시 무효화와 이름 짓기"라는 격언이 있을 정도이다. 실무에서는 **Cache-Aside + 적절한 TTL**로 시작하고, 데이터 변경 시 명시적으로 캐시를 삭제(`DEL`)하는 조합이 가장 실용적이다. 완벽한 일관성이 필요하면 Write-Through를 추가하되, **대부분의 경우 짧은 TTL로 충분하다**.

---

## 12. ElastiCache 설정

### 12.1 노드 타입 선택

| 카테고리 | 노드 타입 예시 | 메모리 | 적합한 경우 |
|----------|--------------|--------|------------|
| **범용(M)** | `cache.m7g.large` | 6.38GB | 대부분의 워크로드 |
| **메모리 최적화(R)** | `cache.r7g.large` | 13.07GB | 대규모 데이터셋, 리더보드 |
| **소규모(T)** | `cache.t4g.micro` | 0.5GB | 개발/테스트, 소규모 캐싱 |

### 12.2 클러스터 모드

```
스탠드얼론 (클러스터 모드 비활성화):

┌─────────────┐    ┌─────────────┐
│  Primary     │───→│  Replica 1   │  ← 읽기 부하 분산
│  (읽기/쓰기) │    └─────────────┘
└─────────────┘    ┌─────────────┐
                   │  Replica 2   │  ← 장애 시 자동 승격 (Multi-AZ)
                   └─────────────┘

클러스터 모드 (활성화):

┌─ Shard 1 ───────────┐  ┌─ Shard 2 ───────────┐  ┌─ Shard 3 ───────────┐
│ Primary  │ Replica   │  │ Primary  │ Replica   │  │ Primary  │ Replica   │
│ 키: a~h  │ 키: a~h   │  │ 키: i~p  │ 키: i~p   │  │ 키: q~z  │ 키: q~z   │
└──────────┴───────────┘  └──────────┴───────────┘  └──────────┴───────────┘

→ 클러스터 모드는 데이터를 샤드에 분산하여 메모리와 쓰기 처리량을 수평 확장
```

### 12.3 VPC 배치

ElastiCache는 반드시 VPC 내의 프라이빗 서브넷에 배치해야 한다. 인터넷에서 직접 접근할 수 없으며, 같은 VPC 내의 애플리케이션(EC2, Lambda, ECS)에서만 접근한다.

```
ElastiCache 네트워크 구성:

┌─── VPC ──────────────────────────────────────┐
│                                                │
│  ┌─ 퍼블릭 서브넷 ──────────────────┐         │
│  │  ALB / NAT Gateway               │         │
│  └───────────────────────────────────┘         │
│                                                │
│  ┌─ 프라이빗 서브넷 (앱) ───────────┐         │
│  │  EC2 / ECS / Lambda(VPC)         │         │
│  │       │                          │         │
│  └───────┼──────────────────────────┘         │
│          │ (보안 그룹으로 접근 제어)             │
│  ┌───────┼──────────────────────────┐         │
│  │  프라이빗 서브넷 (데이터)         │         │
│  │       ↓                          │         │
│  │  ElastiCache Redis               │         │
│  │  RDS                             │         │
│  └───────────────────────────────────┘         │
└────────────────────────────────────────────────┘
```

```bash
# 서브넷 그룹 생성 (ElastiCache가 배치될 서브넷 지정)
aws elasticache create-cache-subnet-group \
  --cache-subnet-group-name my-redis-subnets \
  --cache-subnet-group-description "Redis subnet group" \
  --subnet-ids subnet-abc123 subnet-def456

# Redis 클러스터 생성 (클러스터 모드 비활성화, 1 Primary + 1 Replica)
aws elasticache create-replication-group \
  --replication-group-id my-redis \
  --replication-group-description "My Redis cluster" \
  --engine redis \
  --engine-version 7.1 \
  --cache-node-type cache.t4g.micro \
  --num-cache-clusters 2 \
  --cache-subnet-group-name my-redis-subnets \
  --security-group-ids sg-redis123 \
  --automatic-failover-enabled \
  --multi-az-enabled \
  --at-rest-encryption-enabled \
  --transit-encryption-enabled
```

> **비용 주의**: ElastiCache는 **노드가 실행되는 시간 전체에 과금**된다 (EC2와 유사). 개발/테스트 환경에서는 `cache.t4g.micro` 같은 소형 노드를 사용하고, Replica 없이 단일 노드로 운영하여 비용을 절약하라. 프로덕션에서는 Multi-AZ + Replica로 고가용성을 확보하되, 필요한 메모리 크기에 맞는 최소 노드 타입을 선택하라.

---

## 13. DynamoDB + ElastiCache 통합 아키텍처

### 13.1 전체 아키텍처

```
프로덕션 아키텍처:

클라이언트
    │
    ↓
API Gateway
    │
    ↓
Lambda ──────────────────────────────────────────────────────┐
    │                                                        │
    │  ① 캐시 조회 (0.5ms)                                   │
    ├──→ ElastiCache (Redis) ──→ 캐시 히트? → 바로 반환       │
    │                           캐시 미스 ↓                   │
    │  ② DB 조회 (5ms)                                       │
    ├──→ DynamoDB ──→ 데이터 반환                             │
    │                    │                                    │
    │  ③ 캐시 저장       ↓                                    │
    └──→ ElastiCache: SET (TTL)                              │
                                                              │
DynamoDB Streams ──→ Lambda (캐시 무효화) ──→ ElastiCache: DEL │
                                                              │
→ 데이터 변경 시 자동으로 캐시를 무효화하여 일관성 유지         │
──────────────────────────────────────────────────────────────┘
```

### 13.2 Streams + 캐시 무효화 패턴

```typescript
// DynamoDB Streams → Lambda: 변경된 데이터의 캐시를 자동으로 무효화
import { DynamoDBStreamEvent } from 'aws-lambda';
import { unmarshall } from '@aws-sdk/util-dynamodb';
import { createClient } from 'redis';

const redis = createClient({ url: `redis://${process.env.REDIS_ENDPOINT}:6379` });
await redis.connect();

export const handler = async (event: DynamoDBStreamEvent) => {
  for (const record of event.Records) {
    const keys = unmarshall(record.dynamodb!.Keys as any);

    // 변경된 아이템의 캐시 키를 계산하여 무효화
    const cacheKey = `user:${keys.userId}`;
    await redis.del(cacheKey);

    console.log(`캐시 무효화: ${cacheKey} (이벤트: ${record.eventName})`);
  }
};
```

---

## 14. DynamoDB vs RDS 선택 기준

### 14.1 결정 플로우차트

```
테이블 간 관계가 복잡한가? (다중 JOIN 필요)
  ├── YES → RDS (PostgreSQL/MySQL)
  └── NO ↓

접근 패턴이 예측 가능하고 명확한가?
  ├── NO → RDS (SQL의 유연한 쿼리)
  └── YES ↓

밀리초 단위의 일관된 응답이 필요한가?
  ├── YES → DynamoDB
  └── NO ↓

트래픽 변동이 크고 자동 스케일링이 필요한가?
  ├── YES → DynamoDB
  └── NO ↓

완전한 ACID 트랜잭션이 필요한가?
  ├── YES → RDS
  └── NO → DynamoDB (단순) 또는 RDS (복잡) — 상황에 따라 판단
```

### 14.2 사용 사례별 권장

| 사용 사례 | 권장 서비스 | 이유 |
|----------|-----------|------|
| **사용자 프로필/세션** | DynamoDB | 키-값 접근, 유연한 스키마 |
| **전자상거래 상품 카탈로그** | DynamoDB | 상품마다 다른 속성, 빠른 읽기 |
| **주문/결제 시스템** | RDS | ACID 트랜잭션, 복잡한 관계 |
| **소셜 미디어 피드** | DynamoDB | 대규모 쓰기, 시간순 정렬 |
| **분석/보고서** | RDS | 복잡한 집계 쿼리, JOIN |
| **IoT 센서 데이터** | DynamoDB | 대량 쓰기, 시계열 데이터 |
| **게임 리더보드** | DynamoDB + ElastiCache | 빠른 읽기/쓰기, Sorted Set |
| **CMS/블로그** | RDS | 콘텐츠 간 관계, 전문 검색 |

> **핵심 통찰**: 현대 애플리케이션은 DynamoDB와 RDS를 **함께 사용**하는 것이 일반적이다. 예를 들어, 전자상거래 서비스에서 주문/결제는 RDS(트랜잭션 보장), 상품 카탈로그와 사용자 세션은 DynamoDB(빠른 읽기, 유연한 스키마), 검색 자동완성과 리더보드는 ElastiCache(초저지연)를 사용하는 것이 좋은 설계이다. "하나의 데이터베이스로 모든 것을 해결하겠다"는 접근보다는, **각 서비스의 강점에 맞는 워크로드를 배치**하라.

---

## 자주 하는 실수

| 실수 | 설명 | 올바른 접근 |
|------|------|------------|
| **카디널리티가 낮은 파티션 키** | `status`, `country` 등 몇 가지 값만 갖는 속성을 PK로 사용 | 고유한 값이 많은 속성(`userId`, `orderId`)을 PK로 사용 |
| **Scan에 의존하는 설계** | 접근 패턴을 고려하지 않고 테이블을 만든 후 Scan으로 해결 | 접근 패턴을 먼저 정의하고, Query로 해결되도록 키와 인덱스를 설계 |
| **GSI 없이 다양한 쿼리 시도** | PK 외의 속성으로 검색할 때 Scan 사용 | 필요한 접근 패턴마다 GSI를 추가 |
| **큰 아이템에 강력한 일관성 읽기** | 불필요하게 RCU를 2배 소비 | 대부분의 읽기는 최종 일관성으로 충분. 정확성이 중요한 곳에만 강력한 일관성 사용 |
| **TTL 미설정** | 임시 데이터가 영구히 남아 비용 증가 | 세션, 로그 등 수명이 있는 데이터에 반드시 TTL 설정 |
| **캐시 무효화 없이 긴 TTL** | 데이터 변경 후에도 오래된 캐시 데이터 반환 | 적절한 TTL + 데이터 변경 시 명시적 캐시 삭제(`DEL`) |
| **ElastiCache를 VPC 외부에서 접근 시도** | 연결 타임아웃 발생 | ElastiCache는 같은 VPC 내에서만 접근 가능. Lambda는 VPC에 연결 필요 |
| **Redis에 영구 데이터 저장** | 메모리 초과 시 데이터 손실 위험 | Redis는 캐시/세션용. 영구 저장은 DynamoDB나 RDS 사용 |

---

## AWS CLI 레퍼런스

| 명령어 | 설명 |
|--------|------|
| `aws dynamodb create-table --table-name NAME --attribute-definitions ... --key-schema ... --billing-mode PAY_PER_REQUEST` | DynamoDB 테이블 생성 (온디맨드) |
| `aws dynamodb put-item --table-name NAME --item '{...}'` | 아이템 쓰기 |
| `aws dynamodb get-item --table-name NAME --key '{...}'` | 아이템 읽기 |
| `aws dynamodb query --table-name NAME --key-condition-expression EXPR` | 조건부 다건 조회 |
| `aws dynamodb scan --table-name NAME` | 전체 스캔 |
| `aws dynamodb update-item --table-name NAME --key '{...}' --update-expression EXPR` | 아이템 업데이트 |
| `aws dynamodb delete-item --table-name NAME --key '{...}'` | 아이템 삭제 |
| `aws dynamodb update-table --table-name NAME --global-secondary-index-updates '[...]'` | GSI 추가/삭제 |
| `aws dynamodb update-time-to-live --table-name NAME --time-to-live-specification ...` | TTL 설정 |
| `aws dynamodb describe-table --table-name NAME` | 테이블 상세 정보 |
| `aws dynamodb list-tables` | 테이블 목록 조회 |
| `aws elasticache create-replication-group --replication-group-id ID --engine redis ...` | Redis 클러스터 생성 |
| `aws elasticache describe-replication-groups` | 클러스터 목록 조회 |
| `aws elasticache create-cache-subnet-group --cache-subnet-group-name NAME --subnet-ids ...` | 서브넷 그룹 생성 |
| `aws elasticache delete-replication-group --replication-group-id ID` | Redis 클러스터 삭제 |

---

## 요약

- **DynamoDB**는 AWS의 완전 관리형 NoSQL 데이터베이스이다. 한 자릿수 밀리초의 일관된 성능과 자동 스케일링을 제공하며, 서버리스 아키텍처에 이상적이다.
- 테이블의 **기본 키**는 파티션 키 단독 또는 파티션 키 + 정렬 키의 복합 키로 구성한다. 파티션 키는 카디널리티가 높고 균등하게 분포되는 속성을 선택해야 한다.
- **용량 모드**는 온디맨드(사용한 만큼 과금)와 프로비저닝(RCU/WCU 직접 설정) 중 선택한다. 새 프로젝트는 온디맨드로 시작하고 트래픽 안정화 후 프로비저닝으로 전환하는 것이 비용 효율적이다.
- CRUD 작업에는 **Document Client(`@aws-sdk/lib-dynamodb`)**를 사용하여 JavaScript 네이티브 타입으로 작업한다.
- **Query**는 파티션 키 기반의 효율적인 검색이며, **Scan**은 전체 테이블 스캔이므로 가능한 한 피해야 한다. Scan이 필요한 상황은 테이블 설계를 재검토해야 한다는 신호이다.
- **GSI(Global Secondary Index)**로 기본 키 외의 속성으로도 효율적인 Query가 가능하다. 실무에서는 LSI보다 GSI를 주로 사용한다.
- **DynamoDB Streams**로 테이블의 변경 이벤트를 캡처하여 Lambda 트리거, 캐시 무효화, 데이터 동기화 등을 구현한다.
- **단일 테이블 설계**는 관련 엔티티를 하나의 테이블에 저장하여 Query 한 번으로 관련 데이터를 모두 가져오는 패턴이다. 접근 패턴을 먼저 정의한 후 키를 설계하는 것이 핵심이다.
- **ElastiCache(Redis)**는 인메모리 캐시로 API 응답 캐싱, 세션 스토어, 리더보드, Rate Limiting 등에 사용한다.
- 캐싱 전략은 **Cache-Aside + 적절한 TTL**이 가장 실용적이다. 데이터 변경 시 DynamoDB Streams + Lambda로 캐시를 자동 무효화하면 일관성을 유지할 수 있다.
- DynamoDB와 RDS는 경쟁 관계가 아니라 **상호 보완** 관계이다. 각 워크로드의 특성에 맞는 서비스를 조합하여 사용하는 것이 좋은 설계이다.
