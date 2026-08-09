# Appendix C: Distributed Locking with DB (DB로 분산 잠금 구현하기)

## 핵심 질문

여러 노드에서 동시에 실행되는 애플리케이션에서 하나의 프로세스, 하나의 스레드만 작업을 실행하도록 보장하려면 어떻게 해야 하는가? Redis나 ZooKeeper 없이 DB만으로 분산 잠금을 구현할 수 있는가?

---

## 1. 분산 잠금이 필요한 상황

다음과 같은 요구 사항을 만족해야 하는 기능을 구현한다고 가정하자:

- 애플리케이션이 **1분 간격**으로 작업을 실행함
- 애플리케이션 프로세스는 **여러 노드**에서 실행됨
- 동시에 여러 스레드가 작업을 실행하면 **데이터에 문제가 발생**함

즉, 동시에 두 개 이상의 프로세스가 실행되더라도 그중 **하나의 프로세스, 하나의 스레드만** 작업을 실행해야 한다. 이러한 요구를 만족하려면 분산 잠금(*Distributed Lock - 분산 환경에서 동시 접근을 제어하는 잠금 메커니즘*)이 필요하다.

Redis나 ZooKeeper 같은 기술을 사용할 수도 있지만, 구조를 단순하게 유지하고 싶다면 분산 잠금 수단으로 **DB를 사용**할 수 있다. 이 부록에서는 일정 시간 동안 잠금을 소유하는 방식의 분산 잠금을 DB로 구현한다.

> **핵심 통찰**: 분산 잠금을 위해 반드시 Redis나 ZooKeeper 같은 별도 인프라가 필요한 것은 아니다. 이미 사용 중인 DB만으로도 간단한 분산 잠금을 구현할 수 있으며, 이를 통해 시스템 구조를 단순하게 유지할 수 있다.

---

## 2. 잠금 정보 저장 테이블

분산 잠금을 구현하기 위한 DB 테이블 구조는 다음과 같다:

```
+--------------------------------------------+
|              dist_lock                     |
+--------------------------------------------+
| name    | varchar(100) | PK               |
| owner   | varchar(100) |                  |
| expiry  | timestamp    |                  |
+--------------------------------------------+
```

각 칼럼의 역할은 다음과 같다:

| 칼럼 | 타입 | 역할 |
|------|------|------|
| `name` | `varchar(100)` | 개별 잠금을 구분하기 위한 값. 주요 키(*Primary Key*)이다 |
| `owner` | `varchar(100)` | 잠금 소유자를 구분하기 위한 값. 여러 스레드가 같은 이름의 잠금을 시도할 때 충돌을 처리한다 |
| `expiry` | `datetime` | 잠금 소유 만료 시간. 한 소유자가 오랜 시간 잠금을 소유하지 못하도록 한다 |

다음은 MySQL용 테이블 생성 쿼리이다:

```sql
CREATE TABLE dist_lock (
    name varchar(100) NOT NULL COMMENT '락 이름',
    owner varchar(100) COMMENT '락 소유자',
    expiry datetime COMMENT '락 만료 시간',
    primary key (name)
)
```

> **실무 팁**: `expiry` 칼럼은 잠금의 안전장치 역할을 한다. 잠금을 소유한 프로세스가 비정상 종료되어 잠금을 해제하지 못하는 경우에도, 만료 시간이 지나면 다른 프로세스가 잠금을 획득할 수 있다. 분산 환경에서는 이러한 방어 메커니즘이 필수적이다.

---

## 3. 분산 잠금 동작

분산 잠금이 필요한 스레드는 다음 절차에 따라 잠금을 획득한다:

```
[트랜잭션 시작]
       │
[SELECT ... FOR UPDATE로 행 점유]
       │
   ┌───┴───────────────────────────┐
[행 없음]                      [행 존재]
   │                               │
[INSERT 새 데이터]          ┌──────┴──────┐
   │                    [owner 같음]  [owner 다름]
   │                        │              │
   │                  [expiry 갱신]   ┌─────┴─────┐
   │                        │     [만료됨]    [만료 안됨]
   │                        │        │            │
   │                        │  [owner/expiry  [잠금 실패]
   │                        │    변경]
   │                        │        │
   └────────┬───────────────┘        │
            │                        │
      [트랜잭션 커밋]                │
            │                        │
     ┌──────┴──────┐                │
   [성공]       [실패]              │
     │            │                 │
  잠금 획득   잠금 실패          잠금 실패
```

절차를 단계별로 정리하면 다음과 같다:

1. **트랜잭션을 시작**한다
2. **선점 잠금 쿼리**(`SELECT ... FOR UPDATE`)를 이용해 해당 행을 점유한다
3. **행이 없으면** 잠금 테이블에 새로운 데이터를 추가한다
4. **owner가 다르고 아직 expiry가 지나지 않았다면**, 잠금 획득에 실패한다
5. **owner가 다르고 expiry가 지났다면**, owner와 expiry 값을 변경한 후 잠금을 획득한다
6. **owner가 같다면** expiry만 갱신한 후 잠금을 획득한다
7. 트랜잭션을 **커밋**하고 소유 결과를 리턴한다
8. 트랜잭션 커밋에 **실패**하면 잠금 획득도 실패한다

이 절차에 따라 잠금 소유에 성공했다면 원하는 기능을 실행하고, 실패했다면 기능을 실행하지 않도록 구현한다.

---

## 4. DB 잠금 구현

### 4.1 LockOwner 타입

먼저 잠금 소유자를 표현하는 `LockOwner` 타입을 구현한다:

```java
package distlock;

import java.time.LocalDateTime;

public record LockOwner(String owner, LocalDateTime expiry) {

    public boolean isOwnedBy(String owner) {
        return this.owner.equals(owner);
    }

    public boolean isExpired() {
        return expiry.isBefore(LocalDateTime.now());
    }
}
```

`dist_lock` 테이블에는 현재 잠금 소유자와 만료일 정보를 저장한다. `LockOwner` 클래스는 두 가지 메서드를 제공한다:

| 메서드 | 역할 |
|--------|------|
| `isOwnedBy()` | 현재 소유자가 누구인지 비교한다 |
| `isExpired()` | 잠금이 만료됐는지 여부를 확인한다 |

### 4.2 DistLock 클래스 - tryLock() 메서드

실제 잠금 로직은 `DistLock` 클래스에서 구현한다. 이 클래스를 사용해서 분산 잠금을 시도하는 코드는 다음과 같은 구조를 갖는다:

```java
// 분산 잠금 생성
DistLock lock = new DistLock(ds);
String owner = "owner1";

if (lock.tryLock("lockName", owner, Duration.ofMinutes(1))) {
    // 잠금에 성공
    ... 코드 실행
} else {
    // 잠금에 실패
}
```

`tryLock()` 메서드의 전체 구현은 다음과 같다:

```java
package distlock;

import javax.sql.DataSource;
import java.sql.*;
import java.time.Duration;
import java.time.LocalDateTime;

public class DistLock {
    private final DataSource dataSource;

    public DistLock(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    public boolean tryLock(String name, String owner, Duration duration) {
        Connection conn = null;
        boolean owned;
        try {
            conn = dataSource.getConnection();
            conn.setAutoCommit(false);

            LockOwner lockOwner = getLockOwner(conn, name);

            if (lockOwner == null || lockOwner.owner() == null) {
                // 아직 소유자가 없음 → 잠금 소유 시도
                insertLockOwner(conn, name, owner, duration);
                owned = true;
            } else if (lockOwner.isOwnedBy(owner)) {
                // 소유자 같음 → 만료 시간 연장
                updateLockOwner(conn, name, owner, duration);
                owned = true;
            } else if (lockOwner.isExpired()) {
                // 소유자 다름 && 만료 시간 지남 → 잠금 소유 시도
                updateLockOwner(conn, name, owner, duration);
                owned = true;
            } else {
                // 소유자 다름 && 만료 시간 안 지남 → 잠금 소유 실패
                owned = false;
            }
            conn.commit();
        } catch (Exception e) {
            owned = false;
            rollback(conn);
        } finally {
            close(conn);
        }
        return owned;
    }
}
```

코드의 핵심 흐름을 정리하면 다음과 같다:

| 행 | 설명 |
|----|------|
| 생성자 | DB를 이용하므로 연결을 구할 `DataSource`를 생성자로 받는다 |
| `owned` 변수 | 잠금 성공 여부를 저장한다 |
| `getLockOwner()` | DB에서 잠금 소유자 정보를 구한다. `SELECT ... FOR UPDATE` 쿼리를 실행하여 동시 실행을 막는다 |
| 소유자 없음 | 잠금 데이터를 추가하는 INSERT 쿼리를 실행하고 `owned`를 `true`로 설정한다 |
| 소유자 같음 | 만료 시간을 연장하는 UPDATE 쿼리를 실행하고 `owned`를 `true`로 설정한다 |
| 소유자 다름 + 만료됨 | 소유자를 변경하는 UPDATE 쿼리를 실행하고 `owned`를 `true`로 설정한다 |
| 소유자 다름 + 만료 안됨 | 잠금에 실패하므로 `owned`를 `false`로 설정한다 |
| `catch` 블록 | DB 연동에 실패하면 잠금에 실패한다. 예를 들어, 잠금 데이터가 없는 상황에서 동시에 INSERT를 실행하면 하나의 트랜잭션은 주요 키 중복 예외가 발생하므로 잠금을 실패 처리한다 |

### 알아두기: 주요 키 중복에 의한 동시성 제어

잠금 데이터가 아직 없는 상태에서 두 개의 스레드가 동시에 `tryLock()`을 호출하면, 두 스레드 모두 `getLockOwner()`에서 `null`을 받게 된다. 이때 두 스레드 모두 INSERT를 시도하지만, `name` 칼럼이 주요 키이므로 하나의 INSERT만 성공하고 나머지 하나는 중복 키 예외가 발생한다. 예외가 발생한 스레드는 `catch` 블록에서 `owned = false`로 처리되어 잠금에 실패한다. 이것이 DB의 제약 조건을 활용한 동시성 제어 방식이다.

### 4.3 getLockOwner(), insertLockOwner(), updateLockOwner() 메서드

`tryLock()` 메서드에서 사용하는 3가지 메서드의 구현은 다음과 같다:

```java
private LockOwner getLockOwner(Connection conn, String name) throws SQLException {
    try (PreparedStatement pstmt = conn.prepareStatement(
            "select * from dist_lock where name = ? for update")) {
        pstmt.setString(1, name);
        try (ResultSet rs = pstmt.executeQuery()) {
            if (rs.next()) {
                return new LockOwner(
                    rs.getString("owner"),
                    rs.getTimestamp("expiry").toLocalDateTime());
            }
        }
    }
    return null;
}

private void insertLockOwner(
        Connection conn, String name, String ownerId, Duration duration)
        throws SQLException {
    try (PreparedStatement pstmt = conn.prepareStatement(
            "insert into dist_lock values (?, ?, ?)")) {
        pstmt.setString(1, name);
        pstmt.setString(2, ownerId);
        pstmt.setTimestamp(3, getExpiry(duration));
        pstmt.executeUpdate();
    }
}

private static Timestamp getExpiry(Duration duration) {
    return Timestamp.valueOf(
        LocalDateTime.now().plusSeconds(duration.getSeconds())
    );
}

private void updateLockOwner(
        Connection conn, String name, String owner, Duration duration)
        throws SQLException {
    try (PreparedStatement pstmt = conn.prepareStatement(
            "update dist_lock set owner = ?, expiry = ? where name = ?")) {
        pstmt.setString(1, owner);
        pstmt.setTimestamp(2, getExpiry(duration));
        pstmt.setString(3, name);
        pstmt.executeUpdate();
    }
}
```

`getLockOwner()` 메서드에서 핵심은 다음 쿼리이다:

```sql
select * from dist_lock where name = ? for update
```

이 쿼리는 `FOR UPDATE`를 사용해서 **한 번에 한 트랜잭션만** 데이터를 조회할 수 있게 제한하고 있다. 이를 통해 분산 환경에서 잠금 데이터에 동시에 접근하는 것을 제어한다.

> **핵심 통찰**: `SELECT ... FOR UPDATE`는 비관적 잠금(*Pessimistic Lock*)의 대표적인 구현 방식이다. 조회 시점에 해당 행에 배타 잠금(*Exclusive Lock*)을 걸어, 다른 트랜잭션이 같은 행을 읽거나 수정하지 못하도록 막는다. 분산 잠금의 핵심은 이 DB 수준의 행 잠금에 있다.

### 4.4 unlock() 메서드

명시적으로 잠금을 해제할 수 있도록 `unlock()` 메서드도 구현한다. 잠금에 성공하면 `unlock()`을 실행하는 방식으로 코드를 작성하면 된다:

```java
if (lock.tryLock("lockName", owner, Duration.ofMinutes(1))) {
    // 잠금에 성공
    try {
        ... 코드 실행
    } finally {
        lock.unlock("lockName", owner);
    }
}
```

`unlock()` 메서드의 구현은 다음과 같다:

```java
public void unlock(String name, String owner) {
    Connection conn = null;
    try {
        conn = dataSource.getConnection();
        conn.setAutoCommit(false);

        LockOwner lockOwner = getLockOwner(conn, name);
        if (lockOwner == null || !lockOwner.isOwnedBy(owner)) {
            throw new IllegalStateException("no lock owner");
        }
        if (lockOwner.isExpired()) {
            throw new IllegalStateException("lock is expired");
        }
        clearOwner(conn, name);
        conn.commit();
    } catch (SQLException e) {
        rollback(conn);
        throw new RuntimeException("fail to unlock: " + e.getMessage());
    } finally {
        close(conn);
    }
}

private void clearOwner(
        Connection conn, String name)
        throws SQLException {
    try (PreparedStatement pstmt = conn.prepareStatement(
            "update dist_lock set owner = null, expiry = null where name = ?")) {
        pstmt.setString(1, name);
        pstmt.executeUpdate();
    }
}
```

`unlock()` 메서드의 동작을 정리하면 다음과 같다:

| 단계 | 설명 |
|------|------|
| 소유자 확인 | 잠금 소유자 정보를 구한다 |
| 소유자 불일치 시 | 잠금 소유자가 아니면 `IllegalStateException`을 발생한다 |
| 만료 시간 초과 시 | 소유자가 본인이 맞지만 만료 시간이 지났으면 `IllegalStateException`을 발생한다 |
| 잠금 해제 | 본인 소유가 맞고 만료 시간이 안 지났으면 잠금을 해제한다 |
| `clearOwner()` | 소유자와 만료 시간 칼럼을 `null`로 설정해서 잠금을 해제 처리한다 |

> **실무 팁**: `unlock()` 호출은 반드시 `finally` 블록 안에서 실행해야 한다. 비즈니스 로직 실행 중 예외가 발생하더라도 잠금이 해제되도록 보장하기 위해서다. 잠금을 해제하지 않으면 만료 시간이 지날 때까지 다른 프로세스가 작업을 실행할 수 없게 된다.

### 4.5 rollback()과 close() 메서드

`tryLock()`과 `unlock()`에서 호출하는 나머지 유틸리티 메서드는 다음과 같다:

```java
private void rollback(Connection conn) {
    if (conn != null) {
        try {
            conn.rollback();
        } catch (SQLException ex) {
        }
    }
}

private void close(Connection conn) {
    if (conn != null) {
        try {
            conn.setAutoCommit(true);
        } catch (SQLException ex) {
        }
        try {
            conn.close();
        } catch (SQLException e) {
        }
    }
}
```

`rollback()` 메서드는 트랜잭션을 롤백하고, `close()` 메서드는 `autoCommit`을 원래 상태로 복원한 뒤 커넥션을 닫는다.

---

## 5. 전체 동작 정리

분산 잠금의 전체 흐름을 시나리오별로 정리하면 다음과 같다:

### 시나리오 1: 최초 잠금 획득

```
스레드 A                          dist_lock 테이블
   │                                  │
   ├─ tryLock("job1", "A", 1분) ──▶  │
   │   SELECT ... FOR UPDATE          │  (행 없음)
   │   INSERT ("job1", "A", now+1분)  │  → 행 추가
   │   COMMIT                         │
   │                                  │
   ├─ 비즈니스 로직 실행               │
   │                                  │
   ├─ unlock("job1", "A") ──────────▶ │
   │   UPDATE owner=null, expiry=null │  → 잠금 해제
   │   COMMIT                         │
```

### 시나리오 2: 동시 잠금 시도

```
스레드 A                     스레드 B                     dist_lock 테이블
   │                            │                            │
   ├─ tryLock() ────────────▶  │                            │  (행 없음)
   │  SELECT FOR UPDATE         │                            │
   │  INSERT 성공               │                            │  → 행 추가
   │  COMMIT                    │                            │
   │                            ├─ tryLock() ────────────▶  │
   │                            │  SELECT FOR UPDATE         │  (A가 소유 중)
   │                            │  owner 다름 + 만료 안됨     │
   │                            │  owned = false             │
   │                            │  ← 잠금 실패               │
```

### 시나리오 3: 만료 후 다른 소유자가 획득

```
스레드 B                          dist_lock 테이블
   │                                  │  (A가 소유, expiry 지남)
   ├─ tryLock("job1", "B", 1분) ──▶  │
   │   SELECT ... FOR UPDATE          │  (owner="A", 만료됨)
   │   UPDATE owner="B", expiry=갱신  │  → 소유자 변경
   │   COMMIT                         │
   │   ← 잠금 성공                     │
```

---

## 자주 하는 실수

| 안티패턴 | 문제점 | 해결법 |
|---------|--------|--------|
| 잠금 만료 시간을 설정하지 않음 | 프로세스 비정상 종료 시 잠금이 영원히 해제되지 않음 | `expiry` 칼럼으로 만료 시간을 반드시 설정 |
| `unlock()`을 `finally` 블록 밖에서 호출 | 예외 발생 시 잠금이 해제되지 않음 | 반드시 `finally` 블록 안에서 호출 |
| `SELECT ... FOR UPDATE` 없이 일반 SELECT 사용 | 동시에 여러 트랜잭션이 같은 행을 읽어 동시성 제어 실패 | 반드시 `FOR UPDATE`로 행 수준 잠금 적용 |
| 트랜잭션 없이 잠금 로직 실행 | INSERT/UPDATE의 원자성이 보장되지 않음 | `autoCommit(false)`로 트랜잭션을 명시적으로 관리 |
| 잠금 만료 시간을 너무 길게 설정 | 프로세스 장애 시 오랜 시간 다른 프로세스가 작업 실행 불가 | 작업 예상 소요 시간에 적절한 여유를 더한 값으로 설정 |

---

## 요약

- **분산 잠금**은 여러 노드에서 동시에 실행되는 프로세스 중 하나만 작업을 수행하도록 보장하는 메커니즘이다
- Redis나 ZooKeeper 없이 **DB만으로** 분산 잠금을 구현할 수 있다. `dist_lock` 테이블에 `name`, `owner`, `expiry` 3개 칼럼을 두면 된다
- 핵심은 `SELECT ... FOR UPDATE` 쿼리로 **행 수준의 배타 잠금**을 걸어 동시 접근을 제어하는 것이다
- 잠금 획득 시 소유자 존재 여부, 소유자 일치 여부, 만료 시간 초과 여부를 **순차적으로 판단**하여 처리한다
- `expiry` 칼럼은 프로세스 비정상 종료 시에도 잠금이 영원히 유지되지 않도록 하는 **안전장치** 역할을 한다
- `unlock()`은 반드시 `finally` 블록에서 호출하여 잠금 해제를 보장해야 한다
- 동시에 INSERT를 시도하는 경우, **주요 키 중복 예외**를 활용하여 하나의 트랜잭션만 성공하도록 동시성을 제어한다
