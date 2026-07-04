# Chapter 15: CloudWatch - 모니터링과 운영: Monitoring & Observability

## 핵심 질문

AWS에서 실행 중인 리소스와 애플리케이션의 상태를 어떻게 파악하는가? 장애가 발생했을 때 즉시 알림을 받고, 로그를 분석하여 원인을 추적하며, 시스템 전체의 건강 상태를 한눈에 볼 수 있는 모니터링 체계는 어떻게 구축하는가?

---

## 1. CloudWatch 개요

### 1.1 CloudWatch란

CloudWatch(*Amazon CloudWatch - AWS 리소스와 애플리케이션의 모니터링 및 관찰 서비스. 메트릭 수집, 로그 관리, 알람 설정, 대시보드 시각화를 하나의 서비스에서 제공한다*)는 AWS의 중앙 모니터링 서비스이다. EC2 인스턴스의 CPU 사용률부터 Lambda 함수의 에러율, RDS의 커넥션 수까지 — AWS에서 실행되는 거의 모든 것의 상태를 수집하고 시각화한다.

모니터링 없이 프로덕션 서비스를 운영하는 것은 계기판 없이 비행기를 조종하는 것과 같다. CloudWatch는 AWS 환경의 계기판 역할을 한다.

### 1.2 CloudWatch의 핵심 구성 요소

```
CloudWatch 아키텍처:

[데이터 소스]                    [CloudWatch]                    [액션]
                          ┌────────────────────────┐
EC2 ──────────┐           │  Metrics (메트릭)       │──→ Dashboards (시각화)
Lambda ───────┤           │  ├ 기본 메트릭          │
RDS ──────────┤           │  └ 커스텀 메트릭        │
ECS ──────────┼──────────→│                        │
S3 ───────────┤           │  Alarms (알람)          │──→ SNS (알림)
ALB ──────────┤           │  ├ 임계값 기반          │──→ Auto Scaling (스케일링)
API Gateway ──┘           │  └ 복합 알람            │──→ Lambda (자동 복구)
                          │                        │
애플리케이션 로그 ──────→│  Logs (로그)             │──→ Logs Insights (분석)
CloudWatch Agent ────→│  ├ 로그 그룹/스트림      │──→ Metric Filters (메트릭 추출)
                          │  └ 보존 정책            │
                          └────────────────────────┘
```

| 구성 요소 | 역할 |
|----------|------|
| **Metrics** | 시간 순서로 정렬된 데이터 포인트. CPU 사용률, 요청 수 등 수치 데이터를 수집 |
| **Alarms** | 메트릭이 임계값을 넘으면 알림을 보내거나 자동 액션을 실행 |
| **Logs** | 애플리케이션과 시스템 로그를 중앙에서 수집, 저장, 분석 |
| **Dashboards** | 메트릭과 로그를 시각화하는 커스텀 화면 |
| **Events/EventBridge** | AWS 리소스 상태 변화에 반응하는 이벤트 규칙 (현재는 EventBridge로 통합) |

### 1.3 모니터링의 세 기둥

현대적인 관찰 가능성(*Observability - 시스템의 외부 출력만으로 내부 상태를 추론할 수 있는 능력. 메트릭, 로그, 트레이스의 세 가지 신호로 구성된다*)은 세 가지 핵심 신호로 이루어진다.

```
관찰 가능성의 세 기둥:

┌─────────────────┬─────────────────┬─────────────────┐
│   Metrics       │   Logs          │   Traces        │
│   (메트릭)       │   (로그)         │   (트레이스)     │
│                 │                 │                 │
│ "무엇이 일어나고  │ "왜 일어났는가?" │ "어디서 느려졌   │
│  있는가?"        │                 │  는가?"          │
│                 │                 │                 │
│ CPU: 95%        │ ERROR: DB conn  │ API → Lambda    │
│ 에러율: 5%      │ timeout at ...  │  → DynamoDB     │
│ 지연: 2.3s      │ Stack trace...  │  (800ms 소요)   │
│                 │                 │                 │
│ CloudWatch      │ CloudWatch      │ X-Ray           │
│ Metrics         │ Logs            │                 │
└─────────────────┴─────────────────┴─────────────────┘
```

| 신호 | 질문 | AWS 서비스 |
|------|------|-----------|
| **메트릭** | 시스템에 무엇이 일어나고 있는가? | CloudWatch Metrics |
| **로그** | 왜 그런 일이 일어났는가? | CloudWatch Logs |
| **트레이스** | 요청이 어디서 느려지거나 실패했는가? | AWS X-Ray |

---

## 2. 메트릭 (Metrics)

### 2.1 메트릭의 구조

CloudWatch 메트릭은 세 가지 요소로 식별된다.

| 요소 | 설명 | 예시 |
|------|------|------|
| **네임스페이스** | 메트릭을 그룹화하는 컨테이너. AWS 서비스별로 하나 | `AWS/EC2`, `AWS/Lambda`, `AWS/RDS` |
| **메트릭 이름** | 측정 대상 | `CPUUtilization`, `Invocations`, `Duration` |
| **차원(Dimension)** | 메트릭을 세분화하는 키-값 쌍 | `InstanceId=i-abc123`, `FunctionName=my-api` |

```
메트릭 식별 구조:

네임스페이스:  AWS/EC2
메트릭 이름:  CPUUtilization
차원:        InstanceId = i-0abc123def456
             ↑
             특정 인스턴스의 CPU 사용률을 식별

네임스페이스:  AWS/Lambda
메트릭 이름:  Duration
차원:        FunctionName = my-api-handler
             ↑
             특정 Lambda 함수의 실행 시간을 식별
```

### 2.2 서비스별 기본 메트릭

AWS 서비스는 추가 설정 없이 자동으로 CloudWatch에 기본 메트릭을 발행한다.

**EC2 기본 메트릭 (5분 간격):**

| 메트릭 | 설명 | 활용 |
|--------|------|------|
| `CPUUtilization` | CPU 사용률 (%) | 스케일링 기준, 과부하 감지 |
| `NetworkIn` / `NetworkOut` | 네트워크 입출력 (바이트) | 트래픽 패턴 분석 |
| `StatusCheckFailed` | 인스턴스 상태 검사 실패 | 인스턴스 장애 감지 |
| `DiskReadOps` / `DiskWriteOps` | 디스크 I/O 작업 수 | 디스크 병목 감지 |

> **핵심 통찰**: EC2의 기본 메트릭에는 **메모리 사용률과 디스크 사용률이 포함되지 않는다.** 이것들은 OS 내부 지표이므로 CloudWatch Agent를 설치해야 수집할 수 있다. 메모리 부족으로 서버가 죽었는데 CloudWatch에 메트릭이 없어 원인을 찾지 못하는 것은 흔한 실수이다.

**RDS 기본 메트릭:**

| 메트릭 | 설명 | 활용 |
|--------|------|------|
| `CPUUtilization` | DB 인스턴스 CPU 사용률 | 쿼리 최적화 필요 시점 감지 |
| `DatabaseConnections` | 현재 활성 연결 수 | 커넥션 풀 고갈 감지 |
| `FreeableMemory` | 사용 가능한 메모리 (바이트) | 메모리 부족 경고 |
| `ReadIOPS` / `WriteIOPS` | 초당 디스크 I/O 작업 수 | 디스크 성능 병목 |
| `FreeStorageSpace` | 남은 스토리지 용량 | 디스크 풀 방지 |

**Lambda 기본 메트릭:**

| 메트릭 | 설명 | 활용 |
|--------|------|------|
| `Invocations` | 함수 호출 횟수 | 트래픽 패턴 파악 |
| `Errors` | 에러 발생 횟수 | 에러율 모니터링 |
| `Duration` | 함수 실행 시간 (ms) | 성능 추적, 타임아웃 예방 |
| `Throttles` | 스로틀링된 호출 수 | 동시성 한도 도달 감지 |
| `ConcurrentExecutions` | 동시 실행 중인 함수 수 | 동시성 사용량 모니터링 |

### 2.3 통계 (Statistics)

메트릭 데이터를 조회할 때 통계(*Statistic - 지정한 기간 동안의 메트릭 데이터를 집계하는 방식. Average, Sum, Maximum, Minimum, 백분위수 등을 선택할 수 있다*)를 적용하여 집계한다.

| 통계 | 설명 | 적합한 메트릭 |
|------|------|-------------|
| **Average** | 기간 내 평균값 | CPU 사용률, 메모리 사용률 |
| **Sum** | 기간 내 합계 | 요청 수, 에러 수, 호출 수 |
| **Maximum** | 기간 내 최댓값 | 지연 시간의 최악 케이스 |
| **Minimum** | 기간 내 최솟값 | 사용 가능한 메모리의 최저치 |
| **p99** | 99번째 백분위수 | 응답 시간 (상위 1% 최악 지연) |
| **p95** | 95번째 백분위수 | 응답 시간 (상위 5% 최악 지연) |

```bash
# 특정 EC2 인스턴스의 평균 CPU 사용률 조회 (최근 1시간, 5분 간격)
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=i-0abc123def456 \
  --start-time $(date -u -v-1H +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average Maximum

# Lambda 함수의 p99 응답 시간 조회
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=my-api-handler \
  --start-time $(date -u -v-1H +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --extended-statistics p99
```

> **실무 팁**: 응답 시간을 모니터링할 때 **Average가 아닌 p99(또는 p95)를 사용**하라. 평균 응답 시간이 200ms로 양호해 보여도, p99가 5초라면 100명 중 1명은 5초를 기다린다는 뜻이다. 사용자 경험을 정확하게 반영하는 것은 평균이 아니라 백분위수이다.

### 2.4 커스텀 메트릭

AWS 서비스의 기본 메트릭으로 충분하지 않을 때, 애플리케이션에서 직접 메트릭을 발행할 수 있다.

```bash
# CLI로 커스텀 메트릭 발행
aws cloudwatch put-metric-data \
  --namespace "MyApp" \
  --metric-name "ActiveUsers" \
  --value 127 \
  --unit Count \
  --dimensions Environment=production,Service=web-api
```

```javascript
// Node.js에서 커스텀 메트릭 발행
import { CloudWatchClient, PutMetricDataCommand } from '@aws-sdk/client-cloudwatch';

const cw = new CloudWatchClient({});

// 주문 처리 시간을 커스텀 메트릭으로 발행
async function publishOrderMetrics(orderProcessingTime, orderAmount) {
  await cw.send(new PutMetricDataCommand({
    Namespace: 'MyApp/Orders',
    MetricData: [
      {
        MetricName: 'ProcessingTime',
        Value: orderProcessingTime,
        Unit: 'Milliseconds',
        Dimensions: [
          { Name: 'Environment', Value: process.env.STAGE },
          { Name: 'Service', Value: 'order-api' },
        ],
      },
      {
        MetricName: 'OrderAmount',
        Value: orderAmount,
        Unit: 'None',
        Dimensions: [
          { Name: 'Environment', Value: process.env.STAGE },
        ],
      },
    ],
  }));
}
```

> **비용 주의**: 커스텀 메트릭은 **메트릭당 월 $0.30**이다. 차원 조합이 다르면 각각 별도 메트릭으로 과금된다. 예를 들어 `{Service=A, Env=prod}`와 `{Service=B, Env=prod}`는 같은 메트릭 이름이라도 2개의 메트릭으로 간주된다. 차원을 무분별하게 늘리면 비용이 기하급수적으로 증가할 수 있으므로, 꼭 필요한 차원만 사용하라.

### 2.5 기본 모니터링 vs 상세 모니터링

| 항목 | 기본 모니터링 | 상세 모니터링 |
|------|-------------|-------------|
| **수집 간격** | 5분 | 1분 |
| **비용** | 무료 | 인스턴스당 월 $2.10 (EC2 기준) |
| **활성화** | 기본값 | 명시적 활성화 필요 |
| **적합한 경우** | 개발/테스트 환경 | 프로덕션, Auto Scaling 연동 시 |

```bash
# EC2 인스턴스에 상세 모니터링 활성화
aws ec2 monitor-instances --instance-ids i-0abc123def456
```

---

## 3. 알람 (Alarms)

### 3.1 알람의 동작 원리

CloudWatch 알람(*Alarm - 메트릭을 감시하다가 지정한 조건(임계값)에 도달하면 액션을 실행하는 장치*)은 세 가지 상태를 가진다.

```
알람 상태 전이:

                 임계값 초과
    ┌─────────────────────────────┐
    │                             │
    ▼                             │
┌──────┐    임계값 미만    ┌──────────┐
│  OK  │ ←─────────────── │  ALARM   │
└──────┘                  └──────────┘
    │                             ▲
    │     데이터 부족              │
    ▼                             │
┌──────────────────┐              │
│ INSUFFICIENT_DATA │──────────────┘
└──────────────────┘  데이터 수집 시작
```

| 상태 | 의미 |
|------|------|
| **OK** | 메트릭이 임계값 내에 있음. 정상 |
| **ALARM** | 메트릭이 임계값을 넘었음. 알림 발송 또는 액션 실행 |
| **INSUFFICIENT_DATA** | 데이터가 부족하여 판단할 수 없음 (알람 생성 직후 또는 메트릭 누락 시) |

### 3.2 임계값 기반 알람

```bash
# EC2 인스턴스 CPU가 80%를 5분간 3회 연속 초과하면 알람
aws cloudwatch put-metric-alarm \
  --alarm-name "high-cpu-web-server" \
  --alarm-description "웹 서버 CPU 사용률 80% 초과" \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=i-0abc123def456 \
  --statistic Average \
  --period 300 \
  --evaluation-periods 3 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:ap-northeast-2:123456789012:ops-alerts

# Lambda 에러율이 5%를 초과하면 알람 (Math Expression 사용)
aws cloudwatch put-metric-alarm \
  --alarm-name "lambda-error-rate" \
  --alarm-description "Lambda 에러율 5% 초과" \
  --metrics '[
    {
      "Id": "errors",
      "MetricStat": {
        "Metric": {
          "Namespace": "AWS/Lambda",
          "MetricName": "Errors",
          "Dimensions": [{"Name": "FunctionName", "Value": "my-api"}]
        },
        "Period": 300,
        "Stat": "Sum"
      },
      "ReturnData": false
    },
    {
      "Id": "invocations",
      "MetricStat": {
        "Metric": {
          "Namespace": "AWS/Lambda",
          "MetricName": "Invocations",
          "Dimensions": [{"Name": "FunctionName", "Value": "my-api"}]
        },
        "Period": 300,
        "Stat": "Sum"
      },
      "ReturnData": false
    },
    {
      "Id": "error_rate",
      "Expression": "(errors / invocations) * 100",
      "Label": "Error Rate (%)",
      "ReturnData": true
    }
  ]' \
  --evaluation-periods 2 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:ap-northeast-2:123456789012:ops-alerts
```

### 3.3 SNS 연동 (알림 채널)

알람이 발생하면 SNS(*Simple Notification Service - 게시-구독 방식의 메시지 전달 서비스. 이메일, SMS, HTTP 엔드포인트, Lambda 함수 등 다양한 수신자에게 메시지를 전달한다*) 토픽을 통해 알림을 보낸다.

```bash
# 1. SNS 토픽 생성
aws sns create-topic --name ops-alerts
# 출력: arn:aws:sns:ap-northeast-2:123456789012:ops-alerts

# 2. 이메일 구독 추가
aws sns subscribe \
  --topic-arn arn:aws:sns:ap-northeast-2:123456789012:ops-alerts \
  --protocol email \
  --notification-endpoint devops@example.com

# 3. Slack 알림 (Lambda 경유)
# SNS → Lambda → Slack Webhook 으로 구성
```

```
알림 흐름:

CloudWatch Alarm ──→ SNS Topic ──→ 이메일 (devops@example.com)
                         │
                         ├──→ Lambda → Slack Webhook
                         │
                         └──→ Lambda → PagerDuty API
```

**Slack으로 알림 전송하는 Lambda 함수:**

```javascript
// slackNotifier.mjs — SNS 메시지를 Slack으로 전달
export const handler = async (event) => {
  const snsMessage = JSON.parse(event.Records[0].Sns.Message);

  const slackPayload = {
    text: `:rotating_light: *CloudWatch Alarm*`,
    blocks: [
      {
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: [
            `*알람:* ${snsMessage.AlarmName}`,
            `*상태:* ${snsMessage.OldStateValue} → ${snsMessage.NewStateValue}`,
            `*이유:* ${snsMessage.NewStateReason}`,
            `*시간:* ${snsMessage.StateChangeTime}`,
          ].join('\n'),
        },
      },
    ],
  };

  await fetch(process.env.SLACK_WEBHOOK_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(slackPayload),
  });
};
```

### 3.4 Auto Scaling 연동

CloudWatch 알람은 Auto Scaling 그룹의 스케일링 액션을 트리거할 수 있다. Chapter 6에서 다룬 Auto Scaling과 CloudWatch 알람의 연동이다.

```bash
# 스케일 아웃 알람: CPU > 70%가 2회 연속이면 인스턴스 추가
aws cloudwatch put-metric-alarm \
  --alarm-name "scale-out-high-cpu" \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=AutoScalingGroupName,Value=my-asg \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 70 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:autoscaling:ap-northeast-2:123456789012:scalingPolicy:...:policyName/scale-out

# 스케일 인 알람: CPU < 30%가 5회 연속이면 인스턴스 제거
aws cloudwatch put-metric-alarm \
  --alarm-name "scale-in-low-cpu" \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=AutoScalingGroupName,Value=my-asg \
  --statistic Average \
  --period 300 \
  --evaluation-periods 5 \
  --threshold 30 \
  --comparison-operator LessThanThreshold \
  --alarm-actions arn:aws:autoscaling:ap-northeast-2:123456789012:scalingPolicy:...:policyName/scale-in
```

```
Auto Scaling 연동 흐름:

CloudWatch Metric (CPU > 70%)
    │
    ▼
CloudWatch Alarm (ALARM 상태)
    │
    ▼
Auto Scaling Policy (스케일 아웃)
    │
    ▼
새 EC2 인스턴스 시작
    │
    ▼
ALB가 새 인스턴스로 트래픽 분배
    │
    ▼
CPU 부하 분산 → 알람 OK 상태 복귀
```

### 3.5 복합 알람 (Composite Alarm)

복합 알람(*Composite Alarm - 여러 알람의 상태를 AND/OR/NOT 논리로 조합하여 하나의 알람으로 만드는 기능*)은 여러 알람을 논리적으로 결합한다. 개별 알람으로는 잦은 오탐(*False Positive*)이 발생할 때 유용하다.

```bash
# CPU가 높고 AND 동시에 네트워크 입력도 높을 때만 알람
aws cloudwatch put-composite-alarm \
  --alarm-name "real-overload" \
  --alarm-rule 'ALARM("high-cpu-web-server") AND ALARM("high-network-in")' \
  --alarm-actions arn:aws:sns:ap-northeast-2:123456789012:ops-alerts
```

```
복합 알람 예시:

단일 알람의 문제:
  CPU > 80% → ALARM → 알림 (배포 직후에도 잠깐 올라감 → 오탐)

복합 알람으로 해결:
  CPU > 80%  ─┐
              ├─ AND ─→ ALARM → 알림 (진짜 과부하일 때만)
  요청 수 > 1000 ─┘
```

> **실무 팁**: 프로덕션 환경에서는 **단일 알람보다 복합 알람을 적극 활용**하라. CPU가 잠깐 치솟는 것은 배포, cron 작업, 캐시 워밍 등 다양한 원인이 있다. CPU 증가 AND 응답 시간 증가 AND 에러율 증가를 조합하면 실제 장애만 정확하게 감지할 수 있고, 알림 피로(*Alert Fatigue*)를 줄일 수 있다.

---

## 4. 로그 (Logs)

### 4.1 로그 구조

CloudWatch Logs는 계층적 구조로 로그를 관리한다.

```
CloudWatch Logs 구조:

로그 그룹 (Log Group)
├── /aws/lambda/my-api-handler          ← Lambda 함수별 자동 생성
├── /aws/ecs/my-service                 ← ECS 태스크 로그
├── /ec2/my-web-server/application      ← CloudWatch Agent로 수집
└── /custom/my-app                      ← 직접 생성

로그 스트림 (Log Stream)
├── 2026/03/14/[$LATEST]abc123          ← Lambda 실행 환경별
├── ecs/my-container/task-id-xyz        ← ECS 태스크별
└── i-0abc123/application.log           ← EC2 인스턴스별

로그 이벤트 (Log Event)
├── timestamp: 1710000000000
│   message: "INFO  주문 처리 시작 orderId=12345"
├── timestamp: 1710000001000
│   message: "ERROR DB 연결 실패: Connection refused"
└── ...
```

| 개념 | 설명 | 비유 |
|------|------|------|
| **로그 그룹** | 같은 소스의 로그를 묶는 컨테이너 | 폴더 |
| **로그 스트림** | 하나의 소스 인스턴스에서 온 시간순 로그 | 파일 |
| **로그 이벤트** | 타임스탬프가 있는 개별 로그 항목 | 파일의 한 줄 |

### 4.2 Lambda 로그 자동 수집

Lambda 함수는 추가 설정 없이 `console.log()` 출력이 자동으로 CloudWatch Logs에 수집된다. 로그 그룹은 `/aws/lambda/{함수 이름}` 형식으로 자동 생성된다.

```javascript
// Lambda 함수에서 구조화된 로그 출력
export const handler = async (event) => {
  // 구조화된 JSON 로그 (검색과 분석에 유리)
  console.log(JSON.stringify({
    level: 'INFO',
    message: '주문 처리 시작',
    orderId: event.orderId,
    userId: event.userId,
    timestamp: new Date().toISOString(),
  }));

  try {
    const result = await processOrder(event.orderId);
    console.log(JSON.stringify({
      level: 'INFO',
      message: '주문 처리 완료',
      orderId: event.orderId,
      processingTime: result.duration,
    }));
  } catch (error) {
    console.error(JSON.stringify({
      level: 'ERROR',
      message: '주문 처리 실패',
      orderId: event.orderId,
      error: error.message,
      stack: error.stack,
    }));
    throw error;
  }
};
```

> **실무 팁**: Lambda 로그는 **JSON 형식으로 구조화**하여 출력하라. 비구조화된 텍스트 로그(`console.log('에러 발생: ' + error)`)는 나중에 Logs Insights로 분석할 때 파싱이 어렵다. JSON 로그는 `{ $.level = "ERROR" }`처럼 필드 기반으로 쉽게 필터링하고 집계할 수 있다.

### 4.3 EC2/ECS에서 CloudWatch Agent로 로그 수집

EC2 인스턴스나 ECS 컨테이너에서는 CloudWatch Agent(*CloudWatch Agent - EC2 인스턴스나 온프레미스 서버에 설치하여 OS 수준 메트릭(메모리, 디스크)과 로그를 CloudWatch로 전송하는 프로그램*)를 설치해야 로그를 수집할 수 있다.

```bash
# EC2에 CloudWatch Agent 설치 (Amazon Linux 2023)
sudo dnf install amazon-cloudwatch-agent -y

# Agent 설정 파일 생성
sudo cat > /opt/aws/amazon-cloudwatch-agent/etc/config.json << 'EOF'
{
  "agent": {
    "metrics_collection_interval": 60,
    "run_as_user": "cwagent"
  },
  "metrics": {
    "metrics_collected": {
      "mem": {
        "measurement": ["mem_used_percent"]
      },
      "disk": {
        "measurement": ["used_percent"],
        "resources": ["/"]
      }
    }
  },
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/my-app/application.log",
            "log_group_name": "/ec2/my-web-server/application",
            "log_stream_name": "{instance_id}/application",
            "timestamp_format": "%Y-%m-%dT%H:%M:%S"
          },
          {
            "file_path": "/var/log/my-app/error.log",
            "log_group_name": "/ec2/my-web-server/error",
            "log_stream_name": "{instance_id}/error",
            "timestamp_format": "%Y-%m-%dT%H:%M:%S"
          }
        ]
      }
    }
  }
}
EOF

# Agent 시작
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -c file:/opt/aws/amazon-cloudwatch-agent/etc/config.json \
  -s
```

### 4.4 로그 보존 정책

CloudWatch Logs는 기본적으로 로그를 **영구 보존**한다. 보존 기간을 설정하지 않으면 로그가 계속 쌓여 비용이 늘어난다.

```bash
# 로그 그룹의 보존 기간 설정 (30일)
aws logs put-retention-policy \
  --log-group-name /aws/lambda/my-api-handler \
  --retention-in-days 30
```

| 보존 기간 | 적합한 로그 | 비고 |
|----------|-----------|------|
| **1~7일** | 개발/테스트 환경 로그 | 최소 비용 |
| **30일** | 일반 애플리케이션 로그 | 대부분의 디버깅에 충분 |
| **90일** | 프로덕션 중요 로그 | 분기 단위 분석 가능 |
| **365일** | 감사/규정 준수 로그 | 규정 요구사항 |
| **영구** | 기본값 (주의!) | 비용이 계속 증가 |

> **비용 주의**: CloudWatch Logs는 **수집(Ingestion)과 저장(Storage)에 모두 비용이 발생**한다. 수집 비용은 GB당 약 $0.76(서울 리전), 저장 비용은 GB당 월 $0.0314이다. 로그양이 많은 프로덕션 환경에서는 보존 기간을 반드시 설정하고, 장기 보존이 필요한 로그는 S3로 내보내라. S3 스토리지 비용(GB당 월 $0.025)이 CloudWatch Logs 저장 비용보다 저렴하다.

### 4.5 Logs Insights (로그 쿼리)

Logs Insights(*CloudWatch Logs Insights - CloudWatch Logs에 저장된 로그를 SQL과 유사한 쿼리 언어로 대화형 분석하는 서비스*)는 로그를 검색하고 분석하는 강력한 쿼리 도구이다.

```bash
# Logs Insights 쿼리 실행 (CLI)
aws logs start-query \
  --log-group-name /aws/lambda/my-api-handler \
  --start-time $(date -u -v-1H +%s) \
  --end-time $(date -u +%s) \
  --query-string 'fields @timestamp, @message
    | filter @message like /ERROR/
    | sort @timestamp desc
    | limit 50'
```

**자주 쓰는 Logs Insights 쿼리:**

```
# 1. 최근 에러 로그 조회
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 20

# 2. Lambda 콜드 스타트 분석
filter @type = "REPORT"
| stats avg(@duration), max(@duration), count(*) as invocations
  by ispresent(@initDuration) as isColdStart
| sort isColdStart desc

# 3. 상위 10개 에러 메시지 집계
fields @message
| filter @message like /ERROR/
| parse @message '"error":"*"' as errorMsg
| stats count(*) as errorCount by errorMsg
| sort errorCount desc
| limit 10

# 4. 시간대별 요청 수와 에러율
filter @type = "REPORT"
| stats count(*) as total,
        sum(strcontains(@message, "ERROR")) as errors,
        (sum(strcontains(@message, "ERROR")) / count(*)) * 100 as errorRate
  by bin(5m) as timeWindow
| sort timeWindow desc

# 5. 느린 Lambda 호출 (Duration > 3초)
filter @type = "REPORT" and @duration > 3000
| fields @timestamp, @duration, @memorySize, @maxMemoryUsed
| sort @duration desc
| limit 20
```

### 4.6 메트릭 필터 (Metric Filters)

메트릭 필터(*Metric Filter - 로그 데이터에서 특정 패턴을 찾아 CloudWatch 메트릭으로 변환하는 기능. 로그에서 자동으로 수치를 추출한다*)는 로그에서 메트릭을 추출한다. 예를 들어 로그에 "ERROR"가 나타날 때마다 에러 카운트 메트릭을 증가시킬 수 있다.

```bash
# "ERROR"가 포함된 로그를 카운트하는 메트릭 필터 생성
aws logs put-metric-filter \
  --log-group-name /aws/lambda/my-api-handler \
  --filter-name "ErrorCount" \
  --filter-pattern "ERROR" \
  --metric-transformations \
    metricName=LambdaErrorCount,metricNamespace=MyApp,metricValue=1,defaultValue=0

# JSON 로그에서 특정 필드 값을 메트릭으로 추출
# 예: { "level": "ERROR", "statusCode": 500 } 패턴 매칭
aws logs put-metric-filter \
  --log-group-name /aws/lambda/my-api-handler \
  --filter-name "Status500Count" \
  --filter-pattern '{ $.statusCode = 500 }' \
  --metric-transformations \
    metricName=Http500Count,metricNamespace=MyApp,metricValue=1,defaultValue=0
```

```
메트릭 필터 → 알람 연결:

로그: "ERROR DB connection timeout"
         │
         ▼
메트릭 필터 (패턴: "ERROR")
         │
         ▼
커스텀 메트릭: MyApp/LambdaErrorCount = 1 증가
         │
         ▼
CloudWatch Alarm: 5분간 에러 10회 초과?
         │ Yes
         ▼
SNS → Slack 알림
```

---

## 5. 대시보드 (Dashboards)

### 5.1 대시보드란

CloudWatch 대시보드는 메트릭과 로그를 시각화하는 커스텀 화면이다. 서비스의 전반적인 상태를 한눈에 파악할 수 있도록 주요 지표를 모아 구성한다.

```bash
# 대시보드 생성 (CLI)
aws cloudwatch put-dashboard \
  --dashboard-name "production-overview" \
  --dashboard-body '{
    "widgets": [
      {
        "type": "metric",
        "x": 0, "y": 0, "width": 12, "height": 6,
        "properties": {
          "title": "API Lambda - 호출 수 & 에러",
          "metrics": [
            ["AWS/Lambda", "Invocations", "FunctionName", "my-api", {"stat": "Sum"}],
            ["AWS/Lambda", "Errors", "FunctionName", "my-api", {"stat": "Sum", "color": "#d62728"}]
          ],
          "period": 300,
          "view": "timeSeries"
        }
      },
      {
        "type": "metric",
        "x": 12, "y": 0, "width": 12, "height": 6,
        "properties": {
          "title": "API Lambda - p99 응답 시간",
          "metrics": [
            ["AWS/Lambda", "Duration", "FunctionName", "my-api", {"stat": "p99"}]
          ],
          "period": 300
        }
      },
      {
        "type": "metric",
        "x": 0, "y": 6, "width": 12, "height": 6,
        "properties": {
          "title": "RDS - CPU & 커넥션",
          "metrics": [
            ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", "my-db"],
            ["AWS/RDS", "DatabaseConnections", "DBInstanceIdentifier", "my-db", {"yAxis": "right"}]
          ],
          "period": 300
        }
      },
      {
        "type": "log",
        "x": 12, "y": 6, "width": 12, "height": 6,
        "properties": {
          "title": "최근 에러 로그",
          "query": "fields @timestamp, @message\n| filter @message like /ERROR/\n| sort @timestamp desc\n| limit 10",
          "region": "ap-northeast-2",
          "stacked": false,
          "view": "table"
        }
      }
    ]
  }'
```

### 5.2 실전 대시보드 구성 가이드

```
프로덕션 대시보드 레이아웃:

┌───────────────────────────┬───────────────────────────┐
│  API 호출 수 & 에러 수     │  API p99 응답 시간         │
│  (Lambda Invocations/     │  (Lambda Duration p99)     │
│   Errors - Sum)           │                           │
├───────────────────────────┼───────────────────────────┤
│  RDS CPU & 커넥션 수       │  최근 에러 로그            │
│  (RDS CPUUtilization/     │  (Logs Insights 쿼리)     │
│   DatabaseConnections)    │                           │
├───────────────────────────┼───────────────────────────┤
│  ALB 요청 수 & 5xx 에러   │  DynamoDB 읽기/쓰기       │
│  (ALB RequestCount/       │  용량 소비                 │
│   HTTPCode_ELB_5XX)       │                           │
├───────────────────────────┴───────────────────────────┤
│  알람 상태 위젯                                         │
│  (현재 ALARM 상태인 알람 목록)                           │
└───────────────────────────────────────────────────────┘
```

> **비용 주의**: CloudWatch 대시보드는 **대시보드 3개까지 무료**, 이후 대시보드당 월 $3.00이다. 50개의 메트릭까지 표시할 수 있으므로, 환경별로 대시보드를 무분별하게 만들기보다는 하나의 대시보드에 핵심 지표를 집약하는 것이 비용 효율적이다.

---

## 6. CloudWatch Synthetics (Canary)

### 6.1 Synthetics란

CloudWatch Synthetics(*CloudWatch Synthetics - 사용자의 행동을 시뮬레이션하는 카나리(Canary) 스크립트를 정기적으로 실행하여 엔드포인트의 가용성과 지연 시간을 사전 감지하는 서비스*)는 실제 사용자가 접속하기 전에 서비스의 문제를 감지한다. 카나리는 지정된 일정으로 URL에 접속하거나 API를 호출하여, 응답 상태와 성능을 기록한다.

```
Synthetics 동작 흐름:

CloudWatch Synthetics
    │
    │ 매 5분마다 실행
    ▼
카나리 스크립트 (Lambda 기반)
    │
    ├──→ https://www.example.com  (상태 코드 200?, 응답 시간 < 3초?)
    ├──→ https://api.example.com/health  (JSON 응답 확인)
    └──→ https://app.example.com/login  (로그인 플로우 시뮬레이션)
    │
    ▼
결과 기록 → CloudWatch Metrics + S3 (스크린샷, HAR 파일)
    │
    ▼
실패 시 → CloudWatch Alarm → SNS → Slack 알림
```

### 6.2 카나리 유형

| 유형 | 설명 | 사용 사례 |
|------|------|----------|
| **Heartbeat** | URL에 GET 요청을 보내고 응답 확인 | 웹사이트/API 가용성 체크 |
| **API** | REST API 엔드포인트를 호출하고 응답 검증 | API 헬스 체크, 상태 코드 검증 |
| **Broken link** | 페이지의 모든 링크를 검사하여 깨진 링크 탐지 | 웹사이트 링크 무결성 검사 |
| **Visual** | 스크린샷을 찍어 기준 이미지와 비교 | UI 변경 감지 |
| **Flow** | 여러 단계의 사용자 플로우를 시뮬레이션 | 로그인 → 검색 → 결제 흐름 |

```bash
# 간단한 Heartbeat 카나리 생성 (CLI, 간략화)
aws synthetics create-canary \
  --name "homepage-check" \
  --artifact-s3-location "s3://my-canary-artifacts/" \
  --execution-role-arn arn:aws:iam::123456789012:role/CanaryRole \
  --schedule "Expression=rate(5 minutes)" \
  --runtime-version syn-nodejs-puppeteer-9.0 \
  --code '{"Handler": "index.handler", "Script": "..."}'
```

---

## 7. X-Ray (분산 트레이싱)

### 7.1 X-Ray란

X-Ray(*AWS X-Ray - 분산 애플리케이션의 요청 흐름을 추적하고 시각화하는 서비스. 마이크로서비스 아키텍처에서 병목 구간과 에러 발생 지점을 정확히 파악할 수 있다*)는 관찰 가능성의 세 번째 기둥인 "트레이스"를 담당한다.

하나의 API 요청이 API Gateway → Lambda → DynamoDB → 외부 API를 거치는 경우, CloudWatch 메트릭과 로그만으로는 어디서 시간이 소요되었는지 파악하기 어렵다. X-Ray는 이 전체 여정을 하나의 트레이스로 연결한다.

```
X-Ray 트레이스 시각화:

요청: GET /users/123  (총 820ms)

│ API Gateway (35ms)
├────┤
│    │ Lambda Cold Start (180ms)
│    ├──────────┤
│    │          │ Lambda Handler (605ms)
│    │          ├─────────────────────────────────────┤
│    │          │  │ DynamoDB GetItem (45ms)          │
│    │          │  ├─────┤                            │
│    │          │  │     │ 외부 API 호출 (520ms)  ← 병목!│
│    │          │  │     ├────────────────────────┤   │
│    │          │  │     │                        │   │
│    │          │  │     │                        │   │
```

### 7.2 Lambda에서 X-Ray 활성화

```bash
# Lambda 함수에 X-Ray 트레이싱 활성화
aws lambda update-function-configuration \
  --function-name my-api-handler \
  --tracing-config Mode=Active
```

```javascript
// X-Ray SDK로 하위 호출 추적
import AWSXRay from 'aws-xray-sdk-core';
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';

// AWS SDK 클라이언트를 X-Ray로 래핑 → 자동 트레이싱
const dynamodb = AWSXRay.captureAWSv3Client(new DynamoDBClient({}));

export const handler = async (event) => {
  // 커스텀 하위 세그먼트로 외부 API 호출 추적
  const segment = AWSXRay.getSegment();
  const subsegment = segment.addNewSubsegment('external-api-call');

  try {
    const response = await fetch('https://api.example.com/data');
    subsegment.addAnnotation('statusCode', response.status);
    subsegment.close();
    return { statusCode: 200, body: JSON.stringify(await response.json()) };
  } catch (error) {
    subsegment.addError(error);
    subsegment.close();
    throw error;
  }
};
```

### 7.3 CloudWatch vs X-Ray

| 관점 | CloudWatch | X-Ray |
|------|-----------|-------|
| **초점** | 개별 서비스의 상태 (CPU, 에러율, 로그) | 서비스 간 요청 흐름 |
| **질문** | "Lambda 에러율이 5%인가?" | "이 요청이 왜 3초나 걸렸는가?" |
| **데이터** | 메트릭(숫자), 로그(텍스트) | 트레이스(서비스 간 호출 그래프) |
| **적합한 상황** | 리소스 모니터링, 알람, 로그 분석 | 분산 시스템 디버깅, 성능 병목 분석 |
| **비용 모델** | 메트릭/로그 양 기반 | 트레이스 기록/검색 건수 기반 |

---

## 8. CloudTrail (API 감사 로그)

### 8.1 CloudTrail이란

CloudTrail(*AWS CloudTrail - AWS 계정에서 발생하는 모든 API 호출을 기록하는 감사 로그 서비스. "누가, 언제, 무엇을 했는가"를 추적한다*)은 CloudWatch와 자주 혼동되지만 완전히 다른 목적을 가진 서비스이다.

```
CloudWatch vs CloudTrail:

CloudWatch — "시스템이 어떤 상태인가?"
  CPU 사용률이 95%이다
  Lambda 에러가 분당 50건이다
  디스크 사용량이 90%이다

CloudTrail — "누가 무엇을 했는가?"
  user/admin이 EC2 인스턴스를 종료했다
  role/deploy가 Lambda 코드를 업데이트했다
  user/intern이 S3 버킷을 삭제했다
```

### 8.2 주요 차이점

| 항목 | CloudWatch | CloudTrail |
|------|-----------|------------|
| **목적** | 성능 모니터링, 운영 | 보안 감사, 규정 준수 |
| **기록 내용** | 메트릭, 로그, 이벤트 | AWS API 호출 기록 |
| **질문** | "CPU가 몇 %인가?" | "누가 이 인스턴스를 삭제했는가?" |
| **데이터 소스** | AWS 리소스가 발행하는 메트릭 | AWS API (콘솔, CLI, SDK 모두 포함) |
| **보존** | 로그: 설정에 따라 / 메트릭: 15개월 | 90일 (기본) / S3로 장기 보존 |
| **비용** | 메트릭, 로그 양 기반 | 관리 이벤트: 무료 / 데이터 이벤트: 유료 |

### 8.3 CloudTrail 활용 예시

```bash
# 최근 EC2 인스턴스 종료 이벤트 조회
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=TerminateInstances \
  --max-results 5

# 특정 사용자의 최근 활동 조회
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=Username,AttributeValue=admin \
  --start-time "2026-03-13T00:00:00Z" \
  --end-time "2026-03-14T23:59:59Z"
```

> **핵심 통찰**: 프로덕션 환경에서 "누가 이 리소스를 삭제했는가?"라는 질문에 답할 수 있는 것은 **CloudTrail뿐**이다. CloudWatch는 리소스의 상태를 알려주지만, 누가 어떤 조작을 했는지는 기록하지 않는다. 보안 사고 조사, 규정 준수 감사, 변경 추적이 필요한 조직에서는 CloudTrail 로그를 S3에 장기 보존하고, 중요 이벤트에 대해 CloudWatch 알람을 설정하라.

---

## 9. 실전 모니터링 전략

### 9.1 무엇을 모니터링해야 하는가

모든 것을 모니터링하려 하면 정보 과부하에 빠진다. 핵심 지표에 집중하라.

**서비스 계층별 필수 메트릭:**

| 계층 | 필수 메트릭 | 알람 기준 (예시) |
|------|-----------|----------------|
| **API Gateway / ALB** | 요청 수, 4xx/5xx 에러율, 지연 시간 | 5xx 에러율 > 1%, p99 지연 > 3초 |
| **Lambda** | 에러율, Duration p99, Throttles, ConcurrentExecutions | 에러율 > 5%, Throttles > 0 |
| **EC2** | CPU, 메모리(Agent), 디스크(Agent), StatusCheck | CPU > 80%, 메모리 > 85%, 디스크 > 90% |
| **RDS** | CPU, DatabaseConnections, FreeableMemory, FreeStorageSpace | CPU > 80%, 스토리지 < 10GB |
| **DynamoDB** | ConsumedReadCapacity, ThrottledRequests | Throttle > 0 (온디맨드가 아닌 경우) |
| **ECS** | CPU, Memory, RunningTaskCount | CPU > 80%, 실행 태스크 < 최소 수 |

### 9.2 알람 설계 원칙

```
좋은 알람 vs 나쁜 알람:

나쁜 알람 (알림 피로 유발):
  ✗ CPU > 50% 즉시 알람           → 정상적인 부하에도 알림
  ✗ 모든 4xx 에러에 알람           → 사용자 입력 에러까지 포함
  ✗ 1회 초과로 즉시 알람           → 일시적 스파이크에 반응

좋은 알람 (실제 장애만 감지):
  ✓ CPU > 80%, 5분간 3회 연속     → 지속적인 과부하만 감지
  ✓ 5xx 에러율 > 1%, 5분간 2회    → 서버 측 문제만 감지
  ✓ 복합 알람 (CPU + 에러율 + 지연) → 진짜 장애만 감지
```

| 원칙 | 설명 |
|------|------|
| **평가 기간을 충분히 설정** | 1회 초과로 바로 알람을 울리지 말고, 연속 2~3회 이상 초과 시 알람 |
| **증상 기반 알람** | 원인(CPU)보다 증상(에러율, 응답 시간)에 알람을 걸어라 |
| **알람 계층화** | 경고(Warning) → 심각(Critical) → 긴급(Emergency) 단계별 대응 |
| **대응 방법 문서화** | 알람이 울렸을 때 무엇을 확인하고 어떻게 대응할지 런북(*Runbook*)을 작성 |
| **정기적 리뷰** | 한 달에 한 번 알람 이력을 검토하여 오탐 알람은 조정, 놓친 장애는 알람 추가 |

### 9.3 3계층 웹 애플리케이션 모니터링 예시

```
모니터링 전략 — 3계층 웹 앱:

[사용자 경험 계층]
Synthetics Canary (5분 간격)
  → 홈페이지 응답 시간 < 3초?
  → API 헬스 체크 통과?
  → 로그인 플로우 정상?

[애플리케이션 계층]
API Gateway + Lambda
  → 5xx 에러율 < 1%?
  → p99 응답 시간 < 2초?
  → 스로틀링 발생 여부?

[데이터 계층]
RDS / DynamoDB
  → DB CPU < 80%?
  → 커넥션 수 < 최대치 80%?
  → 스토리지 여유 > 20%?

[인프라 계층]
EC2 (사용 시)
  → 인스턴스 StatusCheck 통과?
  → 메모리 사용률 < 85%?
  → 디스크 사용률 < 90%?

[비용 계층]
Billing Alarm
  → 예상 월 비용이 예산의 80%를 초과?
```

```bash
# 빌링 알람 설정 (예산 $100의 80% = $80 초과 시)
aws cloudwatch put-metric-alarm \
  --alarm-name "billing-alarm-80pct" \
  --alarm-description "월 예상 비용이 $80를 초과했습니다" \
  --namespace AWS/Billing \
  --metric-name EstimatedCharges \
  --dimensions Name=Currency,Value=USD \
  --statistic Maximum \
  --period 21600 \
  --evaluation-periods 1 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:billing-alerts \
  --region us-east-1
```

> **핵심 통찰**: 모니터링은 **바깥에서 안으로(Outside-In)** 설계하라. 사용자가 경험하는 것(응답 시간, 에러율)부터 모니터링하고, 이상이 감지되면 내부(Lambda, RDS, EC2)를 분석한다. CPU 사용률이 높아도 사용자 응답 시간이 정상이라면 즉각 대응할 필요가 없지만, 응답 시간이 느려졌다면 CPU가 정상이라도 원인을 파악해야 한다.

---

## 자주 하는 실수

| 실수 | 설명 | 올바른 접근 |
|------|------|------------|
| **로그 보존 정책 미설정** | 기본값이 영구 보존이라 비용이 계속 증가 | 로그 그룹 생성 시 반드시 보존 기간 설정 (30일 권장) |
| **EC2 메모리 모니터링 누락** | 기본 메트릭에 메모리가 포함되지 않음 | CloudWatch Agent를 설치하여 메모리/디스크 수집 |
| **Average로 응답 시간 모니터링** | 평균은 소수의 느린 요청을 숨김 | p99 또는 p95 백분위수 통계 사용 |
| **1회 초과로 즉시 알람** | 일시적 스파이크에도 알림 발생 → 알림 피로 | evaluation-periods를 2~3으로 설정하여 연속 초과 시만 알람 |
| **모든 것에 알람 설정** | 너무 많은 알림으로 중요한 알림을 놓침 | 핵심 비즈니스 메트릭에만 알람, 복합 알람 활용 |
| **CloudWatch와 CloudTrail 혼동** | "누가 삭제했는가?"를 CloudWatch에서 찾으려 함 | 감사 추적은 CloudTrail, 성능 모니터링은 CloudWatch |
| **구조화되지 않은 로그** | 텍스트 로그는 Logs Insights로 분석하기 어려움 | JSON 형식으로 구조화된 로그 출력 |
| **커스텀 메트릭 차원 폭발** | userId 같은 고카디널리티 차원 사용 → 비용 폭증 | 차원은 Environment, Service 등 저카디널리티 값만 사용 |

---

## AWS CLI 레퍼런스

| 명령어 | 설명 |
|--------|------|
| `aws cloudwatch list-metrics --namespace AWS/Lambda` | 네임스페이스의 메트릭 목록 조회 |
| `aws cloudwatch get-metric-statistics --namespace NS --metric-name NAME --period SEC --statistics STAT --start-time T --end-time T` | 메트릭 통계 조회 |
| `aws cloudwatch put-metric-data --namespace NS --metric-name NAME --value V` | 커스텀 메트릭 발행 |
| `aws cloudwatch put-metric-alarm --alarm-name NAME --threshold N ...` | 알람 생성/수정 |
| `aws cloudwatch describe-alarms --alarm-names NAME` | 알람 상태 조회 |
| `aws cloudwatch put-composite-alarm --alarm-name NAME --alarm-rule RULE` | 복합 알람 생성 |
| `aws cloudwatch put-dashboard --dashboard-name NAME --dashboard-body JSON` | 대시보드 생성/수정 |
| `aws logs create-log-group --log-group-name NAME` | 로그 그룹 생성 |
| `aws logs put-retention-policy --log-group-name NAME --retention-in-days N` | 로그 보존 기간 설정 |
| `aws logs start-query --log-group-name NAME --query-string QUERY` | Logs Insights 쿼리 실행 |
| `aws logs put-metric-filter --log-group-name NAME --filter-name NAME --filter-pattern PAT` | 메트릭 필터 생성 |
| `aws cloudtrail lookup-events --lookup-attributes AttributeKey=KEY,AttributeValue=VAL` | CloudTrail 이벤트 조회 |

---

## 요약

- **CloudWatch**는 AWS의 중앙 모니터링 서비스로, 메트릭 수집, 로그 관리, 알람 설정, 대시보드 시각화를 하나의 서비스에서 제공한다.
- 관찰 가능성의 세 기둥은 **메트릭(CloudWatch Metrics)**, **로그(CloudWatch Logs)**, **트레이스(X-Ray)**이다.
- AWS 서비스는 기본 메트릭을 자동 발행하지만, **EC2의 메모리/디스크는 CloudWatch Agent**를 설치해야 수집할 수 있다.
- 응답 시간은 **Average가 아닌 p99/p95**로 모니터링해야 실제 사용자 경험을 반영한다.
- **커스텀 메트릭**으로 애플리케이션 고유 지표(주문 처리 시간, 활성 사용자 수 등)를 발행할 수 있다. 차원 조합에 따라 비용이 증가하므로 주의한다.
- **알람**은 임계값 기반으로 SNS(이메일, Slack)나 Auto Scaling 액션을 트리거한다. **복합 알람**으로 오탐을 줄이고 실제 장애만 감지하라.
- **CloudWatch Logs**는 Lambda(자동), EC2/ECS(Agent 필요)의 로그를 중앙 수집한다. 보존 기간을 반드시 설정하고, JSON 구조화 로그를 사용하라.
- **Logs Insights**로 로그를 SQL과 유사한 쿼리 언어로 분석하고, **메트릭 필터**로 로그에서 메트릭을 추출하여 알람에 연결할 수 있다.
- **CloudWatch Synthetics(Canary)**는 사용자 관점에서 URL 가용성과 응답 시간을 사전 감지한다.
- **X-Ray**는 분산 시스템에서 요청의 전체 흐름을 추적하여 병목 구간과 에러 지점을 파악한다.
- **CloudTrail**은 "누가, 언제, 무엇을 했는가"를 기록하는 감사 서비스로, CloudWatch(성능 모니터링)와 목적이 완전히 다르다.
- 모니터링은 **바깥에서 안으로(Outside-In)** 설계하라. 사용자 경험(에러율, 응답 시간)부터 모니터링하고, 이상 시 내부 계층(인프라, DB)을 분석한다.
