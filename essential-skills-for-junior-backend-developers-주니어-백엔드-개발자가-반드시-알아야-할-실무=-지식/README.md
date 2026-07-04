# 주니어 백엔드 개발자가 반드시 알아야 할 실무 지식

> **시행착오를 줄여주는 실무 밀착 백엔드 개발 가이드**

## 책 정보

| 항목 | 내용 |
|------|------|
| **저자** | 최범균 |
| **출판사** | 한빛미디어 |
| **출판년도** | 2025 |
| **대상 독자** | 백엔드 개발을 시작한 지 몇 년 안 된 주니어 개발자 |

## 책 소개

백엔드 개발자로서 경력을 쌓아 나가다 보면 코드 외에도 다양한 기초 지식이 필요하다는 사실을 알게 된다. 이 책은 성능부터 네트워크 구성까지, 초보 서버 개발자가 알아두면 좋을 기초 지식을 제공한다. 하나의 주제를 깊게 다루기보다는 성능, 외부 연동, 보안 등 10가지 주제의 기초적인 내용을 다룬다.

## 목차

### 본문

| 챕터 | 제목 | 파일 |
|------|------|------|
| Chapter 1 | 들어가며: 코딩을 할 수 있게 된 것일 뿐 | [ch01-introduction.md](ch01-introduction.md) |
| Chapter 2 | 느려진 서비스, 어디부터 봐야 할까 | [ch02-service-performance.md](ch02-service-performance.md) |
| Chapter 3 | 성능을 좌우하는 DB 설계와 쿼리 | [ch03-db-design-and-query.md](ch03-db-design-and-query.md) |
| Chapter 4 | 외부 연동이 문제일 때 살펴봐야 할 것들 | [ch04-external-integration.md](ch04-external-integration.md) |
| Chapter 5 | 비동기 연동, 언제 어떻게 써야 할까 | [ch05-async-integration.md](ch05-async-integration.md) |
| Chapter 6 | 동시성, 데이터가 꼬이기 전에 잡아야 한다 | [ch06-concurrency.md](ch06-concurrency.md) |
| Chapter 7 | IO 병목, 어떻게 해결하지 | [ch07-io-bottleneck.md](ch07-io-bottleneck.md) |
| Chapter 8 | 실무에서 꼭 필요한 보안 지식 | [ch08-security-essentials.md](ch08-security-essentials.md) |
| Chapter 9 | 최소한 알고 있어야 할 서버 지식 | [ch09-server-management.md](ch09-server-management.md) |
| Chapter 10 | 모르면 답답해지는 네트워크 기초 | [ch10-network-fundamentals.md](ch10-network-fundamentals.md) |
| Chapter 11 | 자주 쓰는 서버 구조와 설계 패턴 | [ch11-architecture-patterns.md](ch11-architecture-patterns.md) |

### 부록

| 부록 | 제목 | 파일 |
|------|------|------|
| Appendix A | 처음 해보는 성능 테스트를 위한 기본 정리 | [appendix-a-performance-testing.md](appendix-a-performance-testing.md) |
| Appendix B | NoSQL 이해하기 | [appendix-b-nosql.md](appendix-b-nosql.md) |
| Appendix C | DB로 분산 잠금 구현하기 | [appendix-c-distributed-locking.md](appendix-c-distributed-locking.md) |

## 주제별 로드맵

```
[Ch1: 들어가며]
     │
     ├──▶ 성능 트랙
     │    Ch2: 서비스 성능 ──▶ Ch3: DB 설계/쿼리 ──▶ Ch7: IO 병목
     │                                                    │
     │                                              Appendix A: 성능 테스트
     │
     ├──▶ 연동 트랙
     │    Ch4: 외부 연동 ──▶ Ch5: 비동기 연동
     │
     ├──▶ 안정성 트랙
     │    Ch6: 동시성 ──▶ Appendix C: 분산 잠금
     │
     ├──▶ 보안 트랙
     │    Ch8: 보안 지식
     │
     ├──▶ 인프라 트랙
     │    Ch9: 서버 관리 ──▶ Ch10: 네트워크
     │
     └──▶ 설계 트랙
          Ch11: 아키텍처 패턴
                    │
              Appendix B: NoSQL
```

## 챕터별 특수 요소

이 책의 학습 노트에는 다음과 같은 특수 요소가 포함된다:

- `>` (레이블 없는 인용문): 저자의 실무 경험담
- `> **핵심 통찰**:` 핵심 인사이트 콜아웃
- `> **실무 팁**:` 실무 best practice 콜아웃
- `> **실무 사례**:` 실제 서비스 장애/문제 사례 콜아웃
- `### 알아두기:` 보충 설명 박스
- `## 자주 하는 실수` 안티패턴과 해결법 테이블
