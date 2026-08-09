# Chapter 19: 내 프로젝트는 객체 지향이 아니다 (My Project Is Not Object Oriented)

## 핵심 질문

C, COBOL 같은 절차적(procedural) 언어로 작성된 코드에서는 객체지향 기법 없이 어떻게 의존성을 끊고 테스트를 작성할 수 있는가?

---

## 1. 비객체지향 코드에서의 레거시 코드 작업

이 책의 대부분의 기법들은 객체지향 언어를 전제로 한다. 인터페이스 추출, 서브클래스 오버라이드, 의존성 주입 등은 모두 객체지향의 핵심 기능인 다형성(polymorphism)에 의존한다. 그렇다면 C, COBOL, Fortran, 어셈블리 같은 절차적 언어로 작성된 레거시 코드에서는 어떻게 해야 하는가?

Feathers의 핵심 메시지는 이것이다:

> 객체지향 언어를 사용하지 않아도 Seam을 찾고 활용할 수 있다. 다만 사용할 수 있는 Seam의 종류가 다를 뿐이다.

### 1.1 절차적 코드의 특성과 도전

절차적 코드에서 테스트가 어려운 근본적인 이유:

| 도전 | 설명 |
|------|------|
| **다형성 부재** | 인터페이스나 가상 함수가 없어 런타임에 구현체를 교체하기 어렵다 |
| **전역 상태 의존** | 전역 변수와 정적 데이터에 크게 의존하는 경향이 있다 |
| **함수 간 강한 결합** | 함수가 다른 함수를 직접 호출하여 의존성을 끊기 어렵다 |
| **부수효과** | 함수가 전역 상태를 변경하거나 I/O를 수행하여 동작을 감지하기 어렵다 |
| **거대한 함수** | 수백~수천 줄의 함수가 흔하며, 각 부분을 격리하여 테스트하기 어렵다 |

하지만 이런 상황에서도 활용할 수 있는 Seam이 존재한다.

---

## 2. 절차적 코드에서 사용 가능한 Seam

Seam이란 코드를 편집하지 않고도 프로그램의 동작을 변경할 수 있는 지점이다(Chapter 4 참고). 객체지향 코드에서는 Object Seam이 가장 유용하지만, 절차적 코드에서는 **Link Seam**과 **Preprocessing Seam**이 핵심적인 역할을 한다.

### 2.1 Link Seam: 링크 타임에 구현체 교체

**Link Seam**은 프로그램의 링크 단계에서 다른 함수 구현체로 교체하는 기법이다. C 언어에서 특히 강력하게 활용할 수 있다.

#### 원리

C에서 프로그램이 빌드되는 과정:

```
소스 파일(.c) → 컴파일 → 오브젝트 파일(.o) → 링크 → 실행 파일
```

링크 단계에서는 여러 오브젝트 파일의 함수 참조를 연결한다. 같은 이름의 함수가 여러 오브젝트 파일에 있으면, 어떤 것을 사용할지 링커에게 지시할 수 있다. 이것이 Link Seam의 핵심이다.

#### 예시: 하드웨어 의존성 제거

다음은 임베디드 시스템에서 센서 데이터를 읽는 코드다:

```c
// sensor.h
int read_sensor(int sensor_id);
void calibrate_sensor(int sensor_id);

// sensor.c (프로덕션 구현)
#include "sensor.h"
#include <hardware_io.h>

int read_sensor(int sensor_id) {
    return hardware_read_port(SENSOR_BASE_ADDR + sensor_id);
}

void calibrate_sensor(int sensor_id) {
    hardware_write_port(SENSOR_BASE_ADDR + sensor_id, CALIBRATE_CMD);
    wait_ms(100);
}
```

```c
// monitor.c (테스트하고 싶은 코드)
#include "sensor.h"

int check_temperature_alarm(void) {
    int temp = read_sensor(TEMP_SENSOR_ID);
    if (temp > MAX_SAFE_TEMP) {
        activate_alarm();
        return 1;
    }
    return 0;
}
```

테스트에서는 실제 하드웨어에 접근할 수 없다. Link Seam을 활용하면:

```c
// fake_sensor.c (테스트용 구현)
#include "sensor.h"

static int fake_sensor_values[MAX_SENSORS] = {0};

int read_sensor(int sensor_id) {
    return fake_sensor_values[sensor_id];
}

void calibrate_sensor(int sensor_id) {
    // 아무것도 하지 않음
}

// 테스트에서 센서 값을 설정할 수 있는 헬퍼 함수
void set_fake_sensor_value(int sensor_id, int value) {
    fake_sensor_values[sensor_id] = value;
}
```

빌드 시 어떤 오브젝트 파일을 링크하느냐에 따라 프로덕션/테스트 구현을 교체한다:

```makefile
# 프로덕션 빌드
production: monitor.o sensor.o
	$(CC) -o monitor monitor.o sensor.o

# 테스트 빌드
test: monitor.o fake_sensor.o monitor_test.o
	$(CC) -o monitor_test monitor.o fake_sensor.o monitor_test.o
```

```c
// monitor_test.c
#include "sensor.h"

extern void set_fake_sensor_value(int sensor_id, int value);

void test_alarm_activates_on_high_temp(void) {
    set_fake_sensor_value(TEMP_SENSOR_ID, MAX_SAFE_TEMP + 1);
    int result = check_temperature_alarm();
    assert(result == 1);
}

void test_no_alarm_on_normal_temp(void) {
    set_fake_sensor_value(TEMP_SENSOR_ID, MAX_SAFE_TEMP - 10);
    int result = check_temperature_alarm();
    assert(result == 0);
}
```

#### Link Seam의 장단점

| 장점 | 단점 |
|------|------|
| 프로덕션 코드를 전혀 변경하지 않아도 된다 | 같은 파일 내의 함수는 교체할 수 없다 |
| 함수 단위로 깔끔하게 교체할 수 있다 | 빌드 구성이 복잡해질 수 있다 |
| 전체 모듈을 한 번에 교체할 수 있다 | 교체할 함수마다 Fake 구현을 작성해야 한다 |

### 2.2 Preprocessing Seam: 매크로를 이용한 함수 교체

**Preprocessing Seam**은 C/C++의 전처리기(preprocessor)를 활용하여 컴파일 전에 코드를 변환하는 기법이다.

#### 원리

C/C++의 컴파일 과정:

```
소스 파일(.c) → 전처리 → 전처리된 소스 → 컴파일 → 오브젝트 파일(.o)
```

전처리 단계에서 `#define`, `#ifdef`, `#include` 등의 지시문이 처리된다. 이를 활용하면 코드를 변경하지 않고도 함수 호출을 다른 것으로 교체할 수 있다.

#### 예시: #define을 이용한 함수 교체

```c
// database.h
int db_query(const char* sql, QueryResult* result);
int db_connect(const char* connection_string);
void db_disconnect(void);
```

```c
// report_generator.c
#include "database.h"

void generate_monthly_report(void) {
    db_connect("production_server");
    QueryResult result;
    db_query("SELECT * FROM sales WHERE month = current_month", &result);
    // ... 결과 처리 ...
    db_disconnect();
}
```

테스트에서 데이터베이스 접근을 제거하려면:

```c
// fake_database.h
// 실제 함수를 매크로로 교체
#define db_connect(cs)        fake_db_connect(cs)
#define db_query(sql, result) fake_db_query(sql, result)
#define db_disconnect()       fake_db_disconnect()

int fake_db_connect(const char* connection_string);
int fake_db_query(const char* sql, QueryResult* result);
void fake_db_disconnect(void);
```

```c
// report_generator_test.c
#include "fake_database.h"   // 이 include가 먼저!
#include "report_generator.c" // 소스 파일을 직접 include

// 이제 report_generator.c 안의 db_query() 호출은
// 전처리 단계에서 fake_db_query()로 교체된다
```

#### #ifdef를 이용한 조건부 컴파일

```c
// sensor.c
#include "sensor.h"

#ifdef TESTING
    int read_sensor(int sensor_id) {
        return fake_sensor_values[sensor_id];
    }
#else
    int read_sensor(int sensor_id) {
        return hardware_read_port(SENSOR_BASE_ADDR + sensor_id);
    }
#endif
```

```makefile
# 테스트 빌드: TESTING 매크로 정의
test: CFLAGS += -DTESTING
test: monitor_test
```

#### Preprocessing Seam의 장단점

| 장점 | 단점 |
|------|------|
| 같은 파일 내의 함수도 교체 가능 | 코드 가독성이 떨어질 수 있다 |
| 매우 세밀한 단위로 교체 가능 | 디버깅이 어려워질 수 있다 (전처리 후 코드가 다름) |
| 기존 코드 변경 최소화 | 매크로 이름 충돌 위험 |

> **핵심 통찰**: Preprocessing Seam은 C/C++ 코드에서 "마지막 수단"으로 매우 유용하다. 하지만 남용하면 코드를 이해하기 어렵게 만들 수 있으므로, 가능하면 Link Seam을 우선 고려하고, Link Seam으로 해결할 수 없는 경우에 Preprocessing Seam을 사용하는 것이 좋다.

---

## 3. C 코드에서의 의존성 해제 기법

### 3.1 함수 포인터를 매개변수로 전달

절차적 코드에서도 일종의 "의존성 주입"이 가능하다. **함수 포인터**를 매개변수로 전달하면, 호출하는 함수를 런타임에 교체할 수 있다.

```c
// Before: 직접 호출로 인한 강한 결합
void process_data(int* data, int count) {
    for (int i = 0; i < count; i++) {
        send_to_server(data[i]);  // 직접 호출 → 테스트 불가
    }
}
```

```c
// After: 함수 포인터를 통한 느슨한 결합
typedef void (*DataSender)(int value);

void process_data(int* data, int count, DataSender sender) {
    for (int i = 0; i < count; i++) {
        sender(data[i]);  // 함수 포인터를 통한 호출
    }
}
```

```c
// 프로덕션 코드
process_data(data, count, send_to_server);

// 테스트 코드
static int sent_values[100];
static int sent_count = 0;

void fake_sender(int value) {
    sent_values[sent_count++] = value;
}

void test_process_data(void) {
    int data[] = {10, 20, 30};
    sent_count = 0;

    process_data(data, 3, fake_sender);

    assert(sent_count == 3);
    assert(sent_values[0] == 10);
    assert(sent_values[1] == 20);
    assert(sent_values[2] == 30);
}
```

이 기법은 객체지향의 Strategy 패턴과 본질적으로 동일하다. 함수 포인터가 인터페이스의 역할을 하는 것이다.

### 3.2 헤더 파일 조작으로 다른 구현체 링크

헤더 파일은 C에서 모듈 간의 "계약(contract)"을 정의하는 역할을 한다. 헤더 파일을 교체하면 다른 구현체를 쉽게 연결할 수 있다.

```c
// display.h (프로덕션 헤더)
void display_init(void);
void display_write(int x, int y, const char* text);
void display_clear(void);
```

```c
// fake_display.h (테스트용 헤더)
void display_init(void);
void display_write(int x, int y, const char* text);
void display_clear(void);

// 테스트에서 확인하기 위한 추가 함수
const char* get_displayed_text(int x, int y);
int get_display_clear_count(void);
```

테스트 빌드에서는 include 경로를 조정하여 테스트용 헤더와 구현체를 사용한다:

```makefile
test: CFLAGS += -I./test_includes
test: monitor.o fake_display.o monitor_test.o
	$(CC) -o monitor_test $^
```

### 3.3 #include를 이용한 테스트 전용 코드 주입

C에서 `#include`는 단순히 지정된 파일의 내용을 그 위치에 삽입하는 전처리기 지시문이다. 이를 창의적으로 활용하면 테스트를 위한 코드를 주입할 수 있다.

```c
// 테스트에서 .c 파일을 직접 include하여 static 함수까지 테스트
// calculator_test.c
#include "calculator.c"  // .h가 아닌 .c 파일을 include!

// 이제 calculator.c의 static 함수에도 접근 가능
void test_internal_calculation(void) {
    // internal_calculate()가 static이어도 접근 가능
    int result = internal_calculate(10, 20);
    assert(result == 30);
}
```

이 기법은 `static` 함수(파일 스코프 함수)를 테스트해야 할 때 특히 유용하다. `static` 함수는 해당 파일 내에서만 접근 가능하므로, 외부에서 테스트할 방법이 없다. `.c` 파일을 직접 include하면 이 제한을 우회할 수 있다.

> 주의: `.c` 파일을 직접 include하는 것은 일반적인 관행이 아니며, 다중 정의(multiple definition) 링크 오류를 일으킬 수 있다. 테스트 빌드를 별도로 구성하여 원본 `.c` 파일을 링크에서 제외해야 한다.

---

## 4. 절차적 코드에서 테스트 작성하기

### 4.1 전역 변수 접근 문제

절차적 코드에서 가장 흔한 문제 중 하나는 전역 변수에 대한 의존이다. 전역 변수는 테스트의 격리성을 파괴한다.

```c
// 전역 상태에 의존하는 코드
static int error_count = 0;
static char last_error[256] = "";

void log_error(const char* message) {
    error_count++;
    strncpy(last_error, message, 255);
    write_to_file("/var/log/app.log", message);
}

int get_error_count(void) {
    return error_count;
}
```

테스트에서의 해결 방법:

```c
// 전역 상태를 초기화하는 함수를 추가
void reset_error_state(void) {
    error_count = 0;
    last_error[0] = '\0';
}

// 각 테스트 전에 상태 초기화
void test_log_error_increments_count(void) {
    reset_error_state();

    log_error("test error");

    assert(get_error_count() == 1);
}

void test_multiple_errors(void) {
    reset_error_state();

    log_error("error 1");
    log_error("error 2");

    assert(get_error_count() == 2);
}
```

전역 변수 문제를 다루는 원칙:

1. **각 테스트 전에 전역 상태를 초기화한다**: setup/teardown 함수를 만든다.
2. **전역 변수를 구조체로 묶는다**: 관련된 전역 변수들을 하나의 구조체로 묶으면 초기화와 관리가 쉬워진다.
3. **점진적으로 전역 상태를 제거한다**: 테스트가 확보되면, 전역 변수를 함수 매개변수나 구조체로 전환한다.

```c
// 전역 변수를 구조체로 묶기
typedef struct {
    int error_count;
    char last_error[256];
} ErrorState;

// 전역 인스턴스
static ErrorState g_error_state = {0, ""};

// 초기화가 깔끔해짐
void reset_error_state(void) {
    memset(&g_error_state, 0, sizeof(ErrorState));
}
```

### 4.2 함수의 부수효과 감지

절차적 코드에서 함수가 올바르게 동작하는지 확인하려면, 함수의 **부수효과(side effect)** 를 감지할 수 있어야 한다. 부수효과란 함수가 반환값 이외에 외부 상태를 변경하는 것을 말한다.

**부수효과의 종류와 감지 방법:**

| 부수효과 | 감지 방법 |
|----------|----------|
| 전역 변수 변경 | 함수 호출 전후로 전역 변수 값을 비교 |
| 파일 쓰기 | Fake 파일 시스템 사용 또는 임시 파일로 리다이렉션 |
| 네트워크 전송 | Fake 네트워크 함수로 Link Seam 교체 |
| 하드웨어 조작 | Fake 하드웨어 함수로 교체 |
| 메모리 할당 | 커스텀 할당자로 교체하여 추적 |

```c
// 부수효과를 감지하기 위한 Fake 구현
static int alarm_activated = 0;
static int alarm_deactivated = 0;

void activate_alarm(void) {
    alarm_activated = 1;
}

void deactivate_alarm(void) {
    alarm_deactivated = 1;
}

void test_high_temp_activates_alarm(void) {
    alarm_activated = 0;
    set_fake_sensor_value(TEMP_SENSOR_ID, MAX_SAFE_TEMP + 1);

    check_temperature_alarm();

    assert(alarm_activated == 1);
}
```

### 4.3 Sensing과 Separation의 적용

Chapter 3에서 다룬 **Sensing(감지)** 과 **Separation(분리)** 의 개념은 절차적 코드에도 그대로 적용된다:

- **Sensing**: 함수가 수행한 작업의 결과를 확인할 수 있게 만들기 → Fake 함수에 기록 기능을 추가
- **Separation**: 테스트 대상을 의존성으로부터 분리하기 → Link Seam이나 Preprocessing Seam으로 의존성 교체

---

## 5. 절차적 코드를 점진적으로 구조화하는 방향

테스트를 작성할 수 있게 되면, 절차적 코드를 점진적으로 더 나은 구조로 개선할 수 있다.

### 5.1 거대한 함수 분해

절차적 레거시 코드에서 가장 흔한 문제는 수백 줄 이상의 거대한 함수다. 테스트의 보호 아래 이를 작은 함수로 분해할 수 있다.

```c
// Before: 500줄짜리 함수
void process_transaction(Transaction* txn) {
    // 100줄: 입력 검증
    // ...

    // 150줄: 비즈니스 규칙 적용
    // ...

    // 100줄: 데이터베이스 저장
    // ...

    // 150줄: 결과 보고서 생성
    // ...
}
```

```c
// After: 작은 함수로 분해
void process_transaction(Transaction* txn) {
    if (!validate_transaction(txn)) return;
    apply_business_rules(txn);
    save_transaction(txn);
    generate_report(txn);
}

static int validate_transaction(Transaction* txn) {
    // 입력 검증 로직
}

static void apply_business_rules(Transaction* txn) {
    // 비즈니스 규칙 적용
}

// ... 각 함수를 독립적으로 테스트 가능
```

### 5.2 데이터와 함수를 구조체로 묶기

관련된 전역 변수와 함수를 구조체와 함수 그룹으로 묶으면, 객체지향의 장점을 일부 얻을 수 있다.

```c
// Before: 흩어진 전역 변수와 함수
static int conn_handle;
static char conn_host[256];
static int conn_port;
static int conn_timeout;

int connect_to_server(void);
int send_data(const char* data);
void disconnect(void);
```

```c
// After: 구조체로 묶기
typedef struct {
    int handle;
    char host[256];
    int port;
    int timeout;
} Connection;

int connection_connect(Connection* conn);
int connection_send(Connection* conn, const char* data);
void connection_disconnect(Connection* conn);
```

이 구조는 C에서의 "객체"와 같다. 구조체가 데이터를, 함수가 행동을 담당하며, 첫 번째 매개변수(`conn`)가 `this` 포인터의 역할을 한다. 이렇게 구조화하면:

- 전역 상태가 제거되어 테스트가 쉬워진다.
- 여러 인스턴스를 만들 수 있다.
- 관련된 코드가 한곳에 모여 이해하기 쉬워진다.

### 5.3 점진적 구조화의 원칙

1. **한 번에 너무 많이 바꾸지 않는다**: 테스트를 작성하고, 작은 리팩토링을 수행하고, 테스트가 통과하는지 확인하는 사이클을 반복한다.
2. **새로운 코드는 더 나은 구조로 작성한다**: 기존 코드를 한 번에 바꿀 수 없더라도, 새로 작성하는 코드는 테스트 가능한 구조로 만든다.
3. **Seam을 의식적으로 만든다**: 함수 포인터, 모듈화된 헤더/소스 분리 등을 통해 향후 테스트와 교체가 용이한 구조를 만든다.

---

## 6. 객체지향 없이도 Seam을 활용할 수 있다

이 장의 핵심 메시지는 **"객체지향 언어가 아니라고 포기할 이유는 없다"** 는 것이다. Feathers는 다음과 같이 정리한다:

| Seam 종류 | OO 언어 | 절차적 언어 |
|-----------|---------|------------|
| **Object Seam** | 인터페이스/상속을 통한 교체 | 사용 불가 |
| **Link Seam** | 사용 가능 (하지만 드물게 사용) | **핵심 기법** |
| **Preprocessing Seam** | C++에서 사용 가능 | **핵심 기법** (C) |
| **함수 포인터** | 사용 가능 (하지만 다형성이 더 편리) | **유사 다형성 구현** |

절차적 언어에서의 작업은 객체지향 언어보다 더 많은 노력이 필요하지만, 불가능하지는 않다. 핵심은 **사용 가능한 Seam을 인식하고 활용하는 것**이다.

> 어떤 언어에서든 테스트를 작성할 수 있다. 다만 어떤 언어는 다른 언어보다 더 많은 노력이 필요할 뿐이다. 테스트가 없는 코드를 그대로 두는 것은 어떤 상황에서도 정당화되지 않는다.

---

## 요약

- 절차적 언어(C, COBOL 등)에서도 **Seam을 찾아 의존성을 끊고 테스트를 작성**할 수 있다.
- **Link Seam**은 링크 단계에서 함수 구현체를 교체하는 기법으로, 프로덕션 코드를 변경하지 않고 사용할 수 있다.
- **Preprocessing Seam**은 C/C++의 전처리기를 활용하여 함수 호출을 매크로로 교체하는 기법이다.
- **함수 포인터**를 매개변수로 전달하면 절차적 코드에서도 의존성 주입과 유사한 효과를 얻을 수 있다.
- 전역 변수 의존 문제는 **상태 초기화 함수**, **구조체로 묶기** 등으로 해결할 수 있다.
- 함수의 **부수효과**는 Fake 구현을 통해 감지할 수 있다.
- `.c` 파일을 직접 `#include`하면 `static` 함수도 테스트할 수 있다.
- 테스트를 확보한 후, 거대한 함수 분해, 데이터와 함수의 구조체 그룹화 등으로 **점진적으로 코드를 구조화**할 수 있다.
- 객체지향 언어가 아니라고 해서 테스트를 포기할 이유는 없다.

---

## 다음 챕터와의 연결

Chapter 20 **"이 클래스는 너무 비대해서 더 이상 확장하고 싶지 않다 (This Class Is Too Big and I Don't Want It to Get Any Bigger)"** 에서는 수백~수천 줄에 달하는 거대한 클래스(God Class)에서 책임을 식별하고 분리하는 구체적인 기법들을 소개한다. Single Responsibility Principle, Method Grouping, Feature Sketch 등을 통해 클래스를 합리적인 크기로 분해하는 방법을 배운다.
