# 코드 (CODE: The Hidden Language of Computer Hardware and Software)

> *CODE: The Hidden Language of Computer Hardware and Software* (2nd Edition, Charles Petzold, Microsoft Press, 2022)
> 한국어판: 『CODE 코드 — 하드웨어와 소프트웨어에 숨어 있는 언어』 (김현규 옮김, 인사이트)

컴퓨터는 어떻게 작동하는가? 모스 부호와 손전등이라는 가장 단순한 통신 수단에서 출발해 전기 회로 → 논리 게이트 → 가산기 → 메모리 → CPU → 운영체제 → 프로그래밍 언어 → 웹까지, 컴퓨터의 모든 층위를 **밑바닥부터 하나씩 쌓아올리며** 설명하는 책.

## 책 정보

| 항목 | 내용 |
|------|------|
| **저자** | 찰스 펫졸드(Charles Petzold) |
| **역자** | 김현규 |
| **출판** | 인사이트 (원서: Microsoft Press, 2nd Edition 2022 / 초판 1999) |
| **전제 지식** | 없음 — 수학·공학 배경 없이 읽을 수 있게 설계됨 |
| **대상 독자** | 컴퓨터가 '진짜로' 어떻게 동작하는지 알고 싶은 모든 사람 |

## 개요

1판(1999)의 명성을 이어받은 2판은 유니코드, 트랜지스터/IC 설명 강화, 현대 운영체제, 웹(Ch28) 등을 대폭 추가했다. 일상의 비유(손전등, 전신, 바코드)에서 시작해 점진적으로 복잡도를 높이는 서술이 가장 큰 특징으로, 어느 단계도 건너뛰지 않고 이전 챕터의 부품으로 다음 챕터를 조립한다.

## 목차

| Ch | 제목 | 핵심 단어 | 한 줄 요약 |
|----|------|-----------|-----------|
| 1 | [Best Friends](ch01-best-friends.md) | 손전등 · 모스 부호 · 코드의 본질 | 코드 = 정보를 다른 형태로 옮기는 약속 — 손전등 깜빡임에서 시작 |
| 2 | [Codes and Combinations](ch02-codes-and-combinations.md) | 조합론 · 정보 용량 | 부호 n개로 2^n가지 표현 — 코드의 수학 |
| 3 | [Braille and Binary Codes](ch03-braille-and-binary-codes.md) | 점자 · 이진 코드 · 이스케이프 코드 | 점자 체계로 배우는 이진 코드와 이스케이프의 원형 |
| 4 | [Anatomy of a Flashlight](ch04-anatomy-of-a-flashlight.md) | 전기 회로 · 전자 · 도체와 절연체 | 손전등 분해 — 전기가 흐른다는 것의 물리학 |
| 5 | [Communicating Around Corners](ch05-communicating-around-corners.md) | 양방향 통신 · 접지 | 옆집 친구와의 통신 — 접지로 전선을 절약하는 회로 확장 |
| 6 | [Logic with Switches](ch06-logic-with-switches.md) | 불 대수 · 직렬과 병렬 | 스위치 직렬 = AND, 병렬 = OR — 논리학과 회로의 만남 |
| 7 | [Telegraphs and Relays](ch07-telegraphs-and-relays.md) | 전신 · 릴레이 · 증폭 | 릴레이(중계기) — 스위치를 움직이는 스위치라는 발명 |
| 8 | [Relays and Gates](ch08-relays-and-gates.md) | 논리 게이트 · AND/OR/NOT/NAND/NOR | 릴레이를 조합해 논리 게이트를 만들다 |
| 9 | [Our Ten Digits](ch09-our-ten-digits.md) | 십진법 · 수 체계의 역사 | 당연하게 쓰던 십진법의 구조를 재발견 |
| 10 | [Alternative 10s](ch10-alternative-10s.md) | 8진법 · 2진법 · 자릿값 | 손가락이 8개였다면? — 진법의 일반화와 이진수 |
| 11 | [Bit by Bit by Bit](ch11-bit-by-bit-by-bit.md) | 비트 · 정보의 최소 단위 · UPC 바코드 | 비트 = 정보의 최소 단위 — 바코드·QR로 보는 실전 비트 |
| 12 | [Bytes and Hexadecimal](ch12-bytes-and-hexadecimal.md) | 바이트 · 16진법 · 니블 | 비트를 다루는 실용 단위, 바이트와 16진 표기 |
| 13 | [From ASCII to Unicode](ch13-from-ascii-to-unicode.md) | ASCII · 유니코드 · UTF-8 | 문자 인코딩의 역사 — 7비트 ASCII에서 UTF-8까지 |
| 14 | [Adding with Logic Gates](ch14-adding-with-logic-gates.md) | 반가산기 · 전가산기 · 리플 캐리 | 논리 게이트로 덧셈 기계를 조립하다 |
| 15 | [Is This for Real?](ch15-is-this-for-real.md) | 트랜지스터 · 집적회로 | 릴레이 회로가 실제 하드웨어(트랜지스터·IC)가 되는 법 |
| 16 | [But What About Subtraction?](ch16-but-what-about-subtraction.md) | 2의 보수 · 오버플로 | 뺄셈을 덧셈으로 — 2의 보수와 음수 표현 |
| 17 | [Feedback and Flip-Flops](ch17-feedback-and-flip-flops.md) | 피드백 · SR 래치 · D 플립플롭 | 피드백 회로가 '기억'을 만든다 |
| 18 | [Let's Build a Clock!](ch18-lets-build-a-clock.md) | 오실레이터 · 카운터 · 분주기 | 진동하는 회로로 디지털 시계 만들기 |
| 19 | [An Assemblage of Memory](ch19-an-assemblage-of-memory.md) | RAM · 주소 지정 · 메모리 배열 | 래치를 배열로 조직해 RAM을 만들다 |
| 20 | [Automating Arithmetic](ch20-automating-arithmetic.md) | 자동 계산 · 명령어 코드 | 계산의 자동화 — 명령어와 데이터의 분리라는 대발상 |
| 21 | [The Arithmetic Logic Unit](ch21-the-arithmetic-logic-unit.md) | ALU · 연산 선택 · 상태 플래그 | CPU의 계산 심장부 ALU 설계 |
| 22 | [Registers and Busses](ch22-registers-and-busses.md) | 레지스터 · 버스 · 3-상태 출력 | 레지스터와 버스 — 부품들이 신호를 공유하는 법 |
| 23 | [CPU Control Signals](ch23-cpu-control-signals.md) | 제어 신호 · 명령어 디코딩 | 제어 신호로 부품을 지휘 — CPU의 완성 |
| 24 | [Jumps, Loops, and Calls](ch24-jumps-loops-and-calls.md) | 분기 · 반복 · 서브루틴 · 스택 | 점프·루프·호출 — 프로그램다운 프로그램의 조건 |
| 25 | [Peripherals](ch25-peripherals.md) | 입출력 · 키보드 · 디스플레이 · 디스크 | CPU 바깥 세상 — 주변장치와의 대화 |
| 26 | [The Operating System](ch26-the-operating-system.md) | 운영체제 · 파일 시스템 · API | 하드웨어 위의 첫 소프트웨어 층 — OS의 역할 |
| 27 | [Coding](ch27-coding.md) | 프로그래밍 언어 · 컴파일러 · 고급 언어 | 어셈블리에서 고급 언어로 — 코딩이라는 추상화 |
| 28 | [The World Wide Web](ch28-the-world-wide-web.md) | HTML · URL · HTTP | 웹의 작동 원리 — 이 책의 모든 층위가 만나는 곳 (2판 신규) |

## 학습 가이드

1. **처음부터 순서대로** — 이 책은 건너뛰기가 통하지 않는다. 모든 챕터가 이전 챕터의 부품으로 조립된다 (손전등 → 릴레이 → 게이트 → 가산기 → 메모리 → CPU → OS → 웹)
2. **밀도가 높아지는 구간은 Ch14~24** — 가산기부터 CPU 완성까지. 진리표와 회로 구성을 손으로 따라 그리면 효과적
3. **개발자라면 Ch13(인코딩)·Ch16(2의 보수)·Ch24(스택)** 이 실무와 바로 연결되는 지점
4. 소프트웨어 쪽 배경이면 Ch26~28은 복습에 가깝고, 하드웨어 층(Ch4~25)이 이 책의 진짜 가치다

## 핵심 개념 맵

- **코드 = 약속**: 모스 부호·점자·ASCII·기계어 모두 "정보를 다른 형태로 옮기는 합의"라는 하나의 개념
- **스위치 → 게이트 → 조합 회로**: 불 대수가 물리적 회로로 구현되는 경로 (Ch6~8·14)
- **피드백 → 기억**: 출력을 입력으로 되먹이면 상태(래치·플립플롭·RAM)가 생긴다 (Ch17~19)
- **명령어와 데이터의 분리**: 계산 자동화의 결정적 발상 — 프로그램 내장 방식의 뿌리 (Ch20·23)
- **계층적 추상화**: 전자 → 게이트 → CPU → OS → 언어 → 웹. 각 층은 아래 층의 세부를 숨긴다
- **점진적 구축(Bottom-Up)**: 이 책 자체가 "추상화는 아래에서 위로 쌓인다"의 시연이다

## 시그니처 요소와 표기 규칙

- `> **Petzold의 비유**:` — 저자 특유의 일상적 비유 콜아웃 (Notion 변환: 📖 콜아웃)
- `## 진리표` — 논리 게이트/회로의 입출력 관계 테이블
- `## 회로 구성` — 텍스트 기반 회로 다이어그램
- `## 단계별 구축` — 이전 챕터 개념이 현재 챕터로 쌓이는 과정 정리

## Notion DB 구조

- 위치: Raehan's Must reads 하위 챕터 DB (콜아웃 마이그레이션·재업로드 완료, 전체 29파일)
