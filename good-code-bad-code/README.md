# Good Code, Bad Code: Think Like a Software Engineer

> *Good Code, Bad Code: Think Like a Software Engineer* (Tom Long, Manning, 2021)
> 한국어판: 『좋은 코드, 나쁜 코드 — 프로그래머의 코드 품질 개선법』 (톰 롱 지음, 차건회 옮김, 제이펍)

소프트웨어 엔지니어 톰 롱(Tom Long)이 **높은 품질의 코드**를 만드는 구체적 원칙을 정리한 실무서. "이 코드가 미래에 어떻게 잘못될 수 있는가"를 늘 염두에 두고, 코드 품질을 **6대 핵심 요소**(읽기 쉬움 · 예측 가능 · 오용 방지 · 모듈화 · 재사용/일반화 · 테스트 용이)로 나누어 코드 수준의 실천으로 풀어낸다.

- **코드 예제**: 원서의 언어 중립적 **의사코드**를 `<details>`로 접어 두고, **TypeScript 변환본**을 펼쳐 병기한다.
- **각 챕터 공통**: `핵심 질문` → 번호 섹션(나쁜 예 → 좋은 예 대비) → `코드 품질 6대 요소 연결` → `요약`.

---

## 전체 목차

### Part 1 — 이론 (In Theory)

| Ch | 제목 | 파일 |
|---|---|---|
| 1 | **Code Quality (코드 품질)** | [ch01-code-quality.md](ch01-code-quality.md) |
| 2 | **Layers of Abstraction (추상화 계층)** | [ch02-layers-of-abstraction.md](ch02-layers-of-abstraction.md) |
| 3 | **Other Engineers and Code Contracts (다른 개발자와 코드 계약)** | [ch03-other-engineers-and-code-contracts.md](ch03-other-engineers-and-code-contracts.md) |
| 4 | **Errors (오류)** | [ch04-errors.md](ch04-errors.md) |

### Part 2 — 실전 (In Practice)

| Ch | 제목 | 파일 |
|---|---|---|
| 5 | **Make Code Readable (가독성 높은 코드를 작성하라)** | [ch05-make-code-readable.md](ch05-make-code-readable.md) |
| 6 | **Avoid Surprises (예측 가능한 코드를 작성하라)** | [ch06-avoid-surprises.md](ch06-avoid-surprises.md) |
| 7 | **Make Code Hard to Misuse (코드를 오용하기 어렵게 만들라)** | [ch07-make-code-hard-to-misuse.md](ch07-make-code-hard-to-misuse.md) |
| 8 | **Make Code Modular (코드를 모듈화하라)** | [ch08-make-code-modular.md](ch08-make-code-modular.md) |
| 9 | **Make Code Reusable and Generalizable (코드를 재사용하고 일반화할 수 있도록 하라)** | [ch09-make-code-reusable-and-generalizable.md](ch09-make-code-reusable-and-generalizable.md) |

### Part 3 — 단위 테스트 (Unit Testing)

| Ch | 제목 | 파일 |
|---|---|---|
| 10 | **Unit Testing Principles (단위 테스트의 원칙)** | [ch10-unit-testing-principles.md](ch10-unit-testing-principles.md) |
| 11 | **Unit Testing Practices (단위 테스트의 실제)** | [ch11-unit-testing-practices.md](ch11-unit-testing-practices.md) |

### 부록 (Appendices)

| 부록 | 제목 | 파일 |
|---|---|---|
| A | **Chocolate Brownie Recipe (초콜릿 브라우니 레시피)** | [appendix-a-chocolate-brownie-recipe.md](appendix-a-chocolate-brownie-recipe.md) |
| B | **Null Safety and Optionals (널 안전성과 옵셔널)** | [appendix-b-null-safety-and-optionals.md](appendix-b-null-safety-and-optionals.md) |
| C | **Additional Code Examples (추가 예제 코드)** | [appendix-c-additional-code-examples.md](appendix-c-additional-code-examples.md) |

> 부록 A는 Ch1에서 가독성 낮은 예로 든 브라우니 레시피의 "읽기 쉬운 버전"이다.
