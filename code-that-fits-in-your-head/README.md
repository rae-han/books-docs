# Code That Fits in Your Head: Heuristics for Software Engineering

> *Code That Fits in Your Head: Heuristics for Software Engineering* (Mark Seemann, 2021)
> 한국어판: 『읽기 쉬운 코드 — 좋은 코드를 작성하는 좋은 개발자 습관』 (김현규 옮김, 길벗, 2022)
> **로버트 C. 마틴 시리즈**

마크 시먼(*Mark Seemann - 『Dependency Injection Principles, Practices, and Patterns』의 저자이자 20년 이상 소프트웨어 컨설턴트로 활동한 개발자*)의 소프트웨어 공학 휴리스틱 안내서. 완벽한 규칙이 아니라 **경험 법칙(*Heuristics - 완벽하지는 않아도 실용적으로 유용한 문제 해결 지침*)** 을 통해 프로그래밍을 공학에 가깝게 만드는 실용적 가이드다. C# 기반 레스토랑 예약 시스템을 예제로, TDD부터 리팩터링, 문제 해결, 팀워크까지 이 책이 다루는 모든 개념을 하나의 코드베이스 위에서 보여준다.

---

## 책의 핵심 메시지

> **미래는 이미 여기에 와 있습니다. 다만 고르게 퍼져 있지 않을 뿐입니다.**
> — 윌리엄 깁슨(William Gibson)

- **소프트웨어는 규칙이 아니라 휴리스틱으로 이루어진다**: 상황에 따라 다르지만, 그렇다고 아무거나 해도 되는 것은 아니다
- **인간의 뇌에 맞추어라**: 단기 기억 7개 한계, 순환 복잡도 7 이하, 의존성 7 이하 — 코드는 머리에 들어와야 한다
- **엔지니어처럼 일하라**: 컴파일은 공짜지만 설계는 비싸다. 체크리스트·검토·프로세스를 활용하라
- **작은 반복이 큰 계획을 이긴다**: 지속적 배포, 수직 슬라이스, 스트랭글러 패턴 — 큰 재작성 대신 작은 개선을 반복하라

---

## 학습 가이드

### 처음 읽는 경우

**전체 순서대로 읽는 것을 권장**한다. Part 1(Ch1-9)에서 새 코드베이스에서 배포까지 가속하는 방법을, Part 2(Ch10-16)에서 이미 배포된 코드베이스를 지속 가능하게 유지하는 방법을 다룬다. 하나의 레스토랑 예약 시스템이 챕터마다 조금씩 성장하므로 순차 읽기가 자연스럽다.

### 실무 활용에 초점을 둔다면

- Ch2 (체크리스트) — 즉시 도입 가능
- Ch3 (복잡성 관리) — 순환 복잡도 임계값
- Ch11 (유닛 테스트 편집) — 안전한 리팩터링
- Ch12 (문제 해결) — 과학적 디버깅
- Appendix A (프랙티스 목록) — 28개 체크리스트

### TDD·설계에 관심이 있다면

- Ch4 (수직 슬라이스) — 외부 접근 TDD
- Ch5 (캡슐화) — 항상 유효한 상태
- Ch6 (다각화) — 삼각측량
- Ch7 (분해) — 순환 복잡도, 80/24 규칙
- Ch8 (API 설계) — 어포던스, poka-yoke, CQS

### 코드를 오래 유지 보수 중이라면

- Ch10 (코드 보강) — 기능 플래그, 스트랭글러 패턴
- Ch13 (관심사 분리) — 함수형 코어·명령 셸
- Ch14 (리듬) — 타임박싱, 의존성 갱신
- Ch15 (유력한 용의자) — 성능·보안·기타 관심사

---

## 전체 목차

### Part 1 — 가속 (Acceleration)

새 코드베이스에서 시작해 배포 가능한 기능까지 가속해나가는 구조. 예제 중심으로 진행된다.

| Ch | 제목 | 핵심 |
|---|---|---|
| [1](ch01-art-or-science.md) | **Art or Science? (예술인가? 과학인가?)** | 집짓기·정원·장인정신 비유의 한계, 휴리스틱 방식의 발견, 소프트웨어 공학의 원대한 목표 |
| [2](ch02-checklists.md) | **Checklists (체크리스트)** | B-17 폭격기 사례, 새 코드베이스 3항목(깃/자동 빌드/모든 오류 켜기), 기존 코드에 점진적 적용 |
| [3](ch03-tackling-complexity.md) | **Tackling Complexity (복잡성을 잘 다루는 법)** | 시스템 1/2, 단기 기억 7개 한계, 인간 친화 코드, 뇌와 컴퓨터 비교 |
| [4](ch04-vertical-slice.md) | **Vertical Slice (수직 슬라이스)** | 외부 접근 TDD, AAA 패턴, 값 객체·DTO·도메인 모델, 가짜 객체와 험블 객체 |
| [5](ch05-encapsulation.md) | **Encapsulation (캡슐화하기)** | 계약 은유, 변환 우선순위 전제, 빨강-초록-리팩터, 포스텔의 법칙, 항상 유효한 상태 |
| [6](ch06-triangulation.md) | **Triangulation (다각화하기)** | 악마의 변호인, 변환 우선순위, 삼각측량, 표준 위험 평가로 테스트 충분성 판단 |
| [7](ch07-decomposition.md) | **Decomposition (분해하기)** | 순환 복잡도 ≤ 7, 80/24 규칙, 기능 편애 감지 → 메서드 추출, 임계치 자동 강제 |
| [8](ch08-api-design.md) | **API Design (API 설계)** | 어포던스, poka-yoke, 커뮤니케이션 계층(타입 > 이름 > 주석 > 문서 > 테스트), CQS |
| [9](ch09-teamwork.md) | **Teamwork (팀워크)** | 작은 커밋, 지속적 통합, 짧게 사는 브랜치, 짝/몹 프로그래밍, 코드 리뷰, 공동 코드 소유권 |

### Part 2 — 지속가능성 (Sustainability)

이미 배포된 코드베이스를 지속 가능하게 유지하는 실무. 기능 추가, 테스트 편집, 문제 해결, 관심사 분리가 축이다.

| Ch | 제목 | 핵심 |
|---|---|---|
| [10](ch10-augmenting-code.md) | **Augmenting Code (코드를 보강해봅시다)** | 기능 플래그, 스트랭글러 패턴(메서드/클래스 수준), 유의적 버전 관리 |
| [11](ch11-editing-unit-tests.md) | **Editing Unit Tests (유닛 테스트 편집하기)** | 안전한 "추가" vs 위험한 "삭제", 리스코프 치환 원칙, git stash로 방해공작 방지 |
| [12](ch12-troubleshooting.md) | **Troubleshooting (문제 해결하기)** | 과학적 방법, 고무 오리 디버깅, 결함을 실패 테스트로 재현, 위양성/위음성, git bisect |
| [13](ch13-separation-of-concerns.md) | **Separation of Concerns (관심사의 분리)** | 순수 함수·CQS, 함수형 코어·명령 셸, 데코레이터 패턴, "금쪽같은 로그" |
| [14](ch14-rhythm.md) | **Rhythm (리듬)** | 타임박싱, 휴식, 콘웨이의 법칙, 자판 외우기, 정기 의존성 갱신 |
| [15](ch15-the-usual-suspects.md) | **The Usual Suspects (유력한 용의자)** | 성능 집착의 뿌리, STRIDE 위협 모델, 속성 기반 테스트(FsCheck), 행위 기반 분석 |
| [16](ch16-tour.md) | **Tour (여행 — 코드베이스 탐색)** | Main→Startup 진입점, 파일 정리, 프랙탈 아키텍처, 모놀리식·순환 의존성, 테스트를 통한 학습 |

### 부록

| Appendix | 제목 | 핵심 |
|---|---|---|
| [A](appendix-a-list-of-practices.md) | **List of Practices (프랙티스 목록)** | 28개 프랙티스 요약표 + 8개 카테고리 정리 |
| [B](appendix-b-bibliography.md) | **Bibliography (참고문헌)** | 12개 카테고리로 정리된 참고 도서 + 저자 블로그 포스트 |
| [C](appendix-c-building-the-example.md) | **Building the Example (예제 빌드해 보기)** | 윈도우/WSL 빌드 절차. 저자의 진짜 의도는 "빌드보다 깃 로그 학습" |

---

## 노트의 구성 요소

각 챕터는 다음 요소로 구성되어 있다:

- `## 핵심 질문` — 챕터가 답하려는 물음 (인라인 텍스트)
- 번호가 매겨진 주요 섹션 (`## 1.`, `## 2.`, ...)
- `> **핵심 통찰**:` 콜아웃 — 챕터의 핵심 인사이트 (💡 gray_bg)
- 레이블 없는 `>` 인용문 — 마크 시먼의 경험담과 외부 인용
- `(*Term - 설명*)` 인라인 이탤릭 — 처음 등장하는 용어 설명
- **C# 코드 예제** — 원본과 동일한 레스토랑 예약 시스템 맥락
- 비교/카테고리 정리하는 마크다운 표
- `## 요약` — 챕터 마지막 불릿 정리

---

## 책의 인상적인 인용

> 프로그램을 상세한 부분까지 명확하게 기술하는 것과 프로그래밍하는 것은 하나이며 같은 것이다.
> — 케블린 헤니(Kevlin Henney)

> 여러분도 나와 같다면, 소프트웨어 공학이 사려깊고 체계적인 방식으로 연구되고, 프로그래머의 지침이 마치 흘러내리는 개인 경험의 모래(the shifting sands of individual experience)처럼 흩어지지 않고 실험에 기반을 두는 날을 꿈꿀 것입니다.
> — 애덤 바(Adam Barr)

> 대중문화는 역사를 무시합니다. ... 돈을 위해 코드를 작성하는 대부분의 사람들도 마찬가지입니다. 그들은 그들의 문화가 어디서 왔는지 전혀 모릅니다.
> — 앨런 케이(Alan Kay)

> 불행하게도, 소프트웨어 설계는 물리적 설계 활동에서 비롯된 메타포들 때문에 족쇄가 채워져 있다.
> — 켄트 벡(Kent Beck)

---

## 관련 책

- [the-clean-coder/](../the-clean-coder/) — 로버트 C. 마틴의 프로페셔널리즘 (같은 시리즈)
- [the-software-craftsman/](../the-software-craftsman/) — 산드로 만쿠소의 소프트웨어 장인정신 (같은 시리즈)
- [clean-software/](../clean-software/) — 로버트 C. 마틴의 애자일 원칙·패턴·실천 방법
- [test-driven-development-by-example/](../test-driven-development-by-example/) — 켄트 벡의 TDD 원전
- [philosophy-of-software-design/](../philosophy-of-software-design/) — John Ousterhout의 소프트웨어 설계 철학
- [legacy-code/](../legacy-code/) — Michael Feathers의 레거시 코드 작업법
