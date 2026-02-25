# CODE: The Hidden Language of Computer Hardware and Software

> **Charles Petzold** | 2nd Edition (2022)

## 개요

컴퓨터는 어떻게 작동하는가? 이 책은 모스 부호와 손전등이라는 가장 단순한 통신 수단에서 출발하여, 전기 회로 → 논리 게이트 → 가산기 → 메모리 → CPU → 운영체제 → 프로그래밍 언어 → 월드 와이드 웹까지, 컴퓨터의 모든 층위를 밑바닥부터 하나씩 쌓아올리며 설명한다.

1판(1999)의 명성을 이어받은 2판은 유니코드, ARM 프로세서, 현대 운영체제, 웹 기술 등 최신 내용을 대폭 추가했다. 수학이나 공학 배경 없이도 읽을 수 있도록 일상의 비유에서 시작하여 점진적으로 복잡도를 높여가는 것이 이 책의 가장 큰 특징이다.

## 목차

| 챕터 | 제목 | 핵심 주제 |
|------|------|-----------|
| [Ch 01](ch01-best-friends.md) | Best Friends | 손전등, 모스 부호, 코드의 본질 |
| [Ch 02](ch02-codes-and-combinations.md) | Codes and Combinations | 조합론, 이진 코드, 정보 용량 |
| [Ch 03](ch03-braille-and-binary-codes.md) | Braille and Binary Codes | 점자, 이진 코드 체계, 이스케이프 코드 |
| [Ch 04](ch04-anatomy-of-a-flashlight.md) | Anatomy of a Flashlight | 전기 회로, 원자, 전자, 도체와 절연체 |
| [Ch 05](ch05-communicating-around-corners.md) | Communicating Around Corners | 양방향 통신, 접지, 회로 확장 |
| [Ch 06](ch06-logic-with-switches.md) | Logic with Switches | 불 대수, 스위치로 구현하는 논리 |
| [Ch 07](ch07-telegraphs-and-relays.md) | Telegraphs and Relays | 전신, 릴레이, 장거리 통신 |
| [Ch 08](ch08-relays-and-gates.md) | Relays and Gates | AND, OR, NOT 게이트, 논리 회로 |
| [Ch 09](ch09-our-ten-digits.md) | Our Ten Digits | 십진법, 수 체계의 역사 |
| [Ch 10](ch10-alternative-10s.md) | Alternative 10s | 8진법, 16진법, 2진법 |
| [Ch 11](ch11-bit-by-bit-by-bit.md) | Bit by Bit by Bit | 비트, 이진 연산, 논리와 산술의 통합 |
| [Ch 12](ch12-bytes-and-hexadecimal.md) | Bytes and Hexadecimal | 바이트, 16진법, 니블 |
| [Ch 13](ch13-from-ascii-to-unicode.md) | From ASCII to Unicode | 문자 인코딩, ASCII, Unicode, UTF-8 |
| [Ch 14](ch14-adding-with-logic-gates.md) | Adding with Logic Gates | 반가산기, 전가산기, 리플 캐리 가산기 |
| [Ch 15](ch15-is-this-for-real.md) | Is This for Real? | 실제 논리 게이트, 트랜지스터, IC |
| [Ch 16](ch16-but-what-about-subtraction.md) | But What About Subtraction? | 2의 보수, 뺄셈, 오버플로우 |
| [Ch 17](ch17-feedback-and-flip-flops.md) | Feedback and Flip-Flops | 피드백, SR 래치, D 플립플롭 |
| [Ch 18](ch18-lets-build-a-clock.md) | Let's Build a Clock! | 오실레이터, 카운터, 분주기 |
| [Ch 19](ch19-an-assemblage-of-memory.md) | An Assemblage of Memory | RAM, 어드레싱, 메모리 배열 |
| [Ch 20](ch20-automating-arithmetic.md) | Automating Arithmetic | 자동 계산, 명령어와 데이터의 분리 |
| [Ch 21](ch21-the-arithmetic-logic-unit.md) | The Arithmetic Logic Unit | ALU 설계, 연산 선택, 상태 플래그 |
| [Ch 22](ch22-registers-and-busses.md) | Registers and Busses | 레지스터, 버스, 3-상태 출력 |
| [Ch 23](ch23-cpu-control-signals.md) | CPU Control Signals | 제어 신호, 명령어 디코딩, CPU 동작 |
| [Ch 24](ch24-jumps-loops-and-calls.md) | Jumps, Loops, and Calls | 분기, 반복, 서브루틴, 스택 |
| [Ch 25](ch25-peripherals.md) | Peripherals | 입출력, 키보드, 디스플레이, 디스크 |
| [Ch 26](ch26-the-operating-system.md) | The Operating System | 운영체제, 명령줄, GUI, API |
| [Ch 27](ch27-coding.md) | Coding | 프로그래밍 언어, 컴파일러, 고급 언어 |
| [Ch 28](ch28-the-world-wide-web.md) | The World Wide Web | HTML, URL, HTTP, 웹의 작동 원리 |

## 이 책의 특별한 점

### 점진적 구축 (Bottom-Up)
모든 챕터가 이전 챕터의 지식 위에 쌓인다. 손전등 → 전선 → 릴레이 → 논리 게이트 → 가산기 → 메모리 → CPU → OS → 웹. 어느 단계도 건너뛰지 않는다.

### 1판과 2판의 차이
- **문자 인코딩**: ASCII 중심 → Unicode/UTF-8까지 확장
- **프로세서**: 가상 8080 중심 → ARM 아키텍처 추가
- **현대 기술**: 웹(Chapter 28) 등 최신 내용 추가
- **회로 기술**: 릴레이 → 트랜지스터/IC 설명 강화

## 챕터별 특수 요소

| 요소 | 형식 | 설명 |
|------|------|------|
| `> **Petzold의 비유**:` | blockquote | 저자 특유의 일상적 비유를 통한 설명 |
| `## 진리표` | 마크다운 테이블 | 논리 게이트/회로의 입출력 관계 |
| `## 회로 구성` | 텍스트 다이어그램 | 회로 배선과 구성 요소 시각화 |
| `## 단계별 구축` | 번호 목록 | 단순 → 복잡으로 개념을 쌓아가는 과정 |
