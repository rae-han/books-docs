# 객체지향의 사실과 오해

> **역할, 책임, 협력 관점에서 본 객체지향**

## 책 정보

| 항목 | 내용 |
|------|------|
| **저자** | 조영호 |
| **출판사** | 위키북스 |
| **출판년도** | 2015 |
| **대상 독자** | 객체지향 프로그래밍 언어를 사용하는 소프트웨어 개발자 |

## 책 소개

객체지향이란 무엇인가라는 원론적인 질문에 대한 저자 나름의 대답을 정리한 책이다. 클래스나 상속이 아닌, 역할/책임/협력이라는 관점에서 객체지향의 본질을 탐구한다. 구현 코드가 등장하는 장은 7장이 유일하며, 나머지 장들은 비유와 사고실험을 통해 객체지향의 핵심 개념을 설명한다. 이 책은 객체지향을 다루는 다른 책이나 자료를 읽을 때 미리 알고 있으면 도움이 될 기본 배경과 지식을 다룬다.

## 목차

### 본문

| 챕터 | 제목 | 파일 |
|------|------|------|
| Chapter 1 | 협력하는 객체들의 공동체 | [ch01-cooperating-objects.md](ch01-cooperating-objects.md) |
| Chapter 2 | 이상한 나라의 객체 | [ch02-objects-in-wonderland.md](ch02-objects-in-wonderland.md) |
| Chapter 3 | 타입과 추상화 | [ch03-types-and-abstraction.md](ch03-types-and-abstraction.md) |
| Chapter 4 | 역할, 책임, 협력 | [ch04-roles-responsibilities-collaboration.md](ch04-roles-responsibilities-collaboration.md) |
| Chapter 5 | 책임과 메시지 | [ch05-responsibility-and-messages.md](ch05-responsibility-and-messages.md) |
| Chapter 6 | 객체 지도 | [ch06-object-map.md](ch06-object-map.md) |
| Chapter 7 | 함께 모으기 | [ch07-putting-it-all-together.md](ch07-putting-it-all-together.md) |

### 부록

| 부록 | 제목 | 파일 |
|------|------|------|
| Appendix A | 추상화 기법 | [appendix-a-abstraction-techniques.md](appendix-a-abstraction-techniques.md) |

## 읽기 순서

이 책은 1장부터 7장까지 유기적인 흐름으로 연결되어 있다. 처음부터 끝까지 순서대로 읽는 것이 가장 효과적이다.

```
[Ch1: 협력하는 객체들의 공동체]
     │
     │  객체지향의 본질은 클래스가 아닌
     │  역할, 책임, 협력임을 제시
     │
     ▼
[Ch2: 이상한 나라의 객체]
     │
     │  객체 = 상태 + 행동 + 식별자
     │  행동이 상태를 결정한다
     │
     ▼
[Ch3: 타입과 추상화]
     │
     │  동적 객체를 정적 타입으로 추상화
     │  타입 = 행동에 의한 분류
     │
     ▼
[Ch4: 역할, 책임, 협력]
     │
     │  협력 → 역할 → 책임 → 객체
     │  설계의 핵심 재료
     │
     ▼
[Ch5: 책임과 메시지] ◀── 저자가 "단 하나만 읽는다면" 추천하는 장
     │
     │  메시지가 객체를 결정한다
     │  인터페이스와 구현의 분리
     │
     ▼
[Ch6: 객체 지도]
     │
     │  안정적인 구조 위에 불안정한 기능을 배치
     │  도메인 모델 + 유스케이스
     │
     ▼
[Ch7: 함께 모으기]
     │
     │  1~6장의 개념을 코드로 구현
     │  개념/명세/구현 세 관점의 통합
     │
     ▼
[Appendix A: 추상화 기법]
     분류, 일반화, 집합 세 가지 추상화의 심화
```

## 챕터별 특수 요소

이 책의 학습 노트에는 다음과 같은 특수 요소가 포함된다:

- `>` (레이블 없는 인용문): 저자의 핵심 비유와 사고실험 (커피 공화국, 앨리스, 런던 지하철, 최후통첩 게임 등)
- `> **핵심 통찰**:` 핵심 인사이트 콜아웃
- `## 다른 챕터와의 관계`: 1→7장 유기적 흐름에 따른 챕터 간 연결고리
