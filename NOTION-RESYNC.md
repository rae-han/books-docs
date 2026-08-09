# Notion 재동기화 기록

로컬 노트가 수정되어 Notion에 올라간 버전과 달라진 내역을 추적한다. 재업로드를 마친 항목은 체크한다.

## 2026-08-09 문장부호 정리 (dash + 가운뎃점)

**무엇이 바뀌었나**

1. **대시류 -> 하이픈**: em dash(U+2014) 9,091건, en dash 1건, 유니코드 마이너스 69건을 전부 `-`로 치환. 인용 출처 `> — 화자` 32건은 앞 줄에 `<br>- 화자`로 병합 (커밋 3874f4c)
2. **나열 구분자 ` · ` -> `, `**: 1,442건 / 95개 파일. 코드 펜스 안 다이어그램의 가운뎃점 75건은 보존 (커밋 fa17ce7)
3. head-first Ch1 문장 수정: `나는 행동·꽥꽥거리는 행동` -> `나는 행동과 꽥꽥거리는 행동`

**재업로드 판단 기준**

- `notes/` 본문이 바뀐 책만 재업로드 대상. Notion에 올라간 본문에 옛 표기(em dash, ` · `)가 남아 있다
- README만 바뀐 책은 재업로드 불필요: 핵심 단어 **구분자**만 바뀌었고 단어 값 자체는 동일해서 Notion DB multi-select 값에 차이가 없다
- 요약 노트(`summary/`)는 아직 Notion에 올린 적이 없으므로 해당 없음

**책별 변경 규모** (변경 노트 수 기준)

| 책 | 변경 노트 수 | Notion 조치 |
|----|----|----|
| a-common-sense-guide-to-data-structures-and-algorithms | 20 | **재업로드 필요** |
| aws-complete-guide | 10 | **재업로드 필요** |
| clean-architecture | 26 | **재업로드 필요** |
| clean-code | 17 | **재업로드 필요** |
| clean-software | 34 | **재업로드 필요** |
| code-that-fits-in-your-head | 18 | **재업로드 필요** |
| code-the-hidden-language | 28 | **재업로드 필요** |
| design-it-from-programmer-to-software-architect | 14 | **재업로드 필요** |
| docker-complete-guide | 16 | **재업로드 필요** |
| essential-skills-for-junior-backend-developers-주니어-백엔드-개발자가-반드시-알아야-할-실무=-지식 | 1 | **재업로드 필요** |
| frontend-performance-optimization-deep-dive | 27 | **재업로드 필요** |
| functional-programming-complete-guide | 17 | **재업로드 필요** |
| fundamentals-of-software-architecture-1st-edition | 23 | **재업로드 필요** |
| fundamentals-of-software-architecture-2nd-edition | 27 | **재업로드 필요** |
| good-code-bad-code | 14 | **재업로드 필요** |
| head-first-design-patterns | 14 | **재업로드 필요** |
| javascript-react-pattern | 16 | **재업로드 필요** |
| legacy-code | 8 | **재업로드 필요** |
| mastering-api-architecture | 11 | 미업로드 - 해당 없음 |
| minimalism-programmer | 9 | **재업로드 필요** |
| multi-paradigm-programming | 4 | **재업로드 필요** |
| objects | 8 | **재업로드 필요** |
| philosophy-of-software-design | 8 | **재업로드 필요** |
| programmers-coding-test | 8 | 미업로드 - 해당 없음 |
| quant | 6 | 미업로드 - 해당 없음 |
| refactoring-2nd-edition | 14 | **재업로드 필요** |
| structure-and-interpretation-of-computer-programs-javascript | 18 | **재업로드 필요** |
| test-driven-development-by-example | 32 | **재업로드 필요** |
| the-clean-coder | 14 | **재업로드 필요** |
| the-complete-software-developers-career-guide | 59 | **재업로드 필요** |
| the-essence-of-object-orientation-객체지향의-사실과-오해 | 2 | **재업로드 필요** |
| the-hexagonal-developer | 8 | **재업로드 필요** |
| the-pragmatic-programmer | 10 | **재업로드 필요** |
| the-software-craftsman | 17 | **재업로드 필요** |
| this-is-coding-test | 19 | 미업로드 - 해당 없음 |
| unit-testing | 10 | **재업로드 필요** |

**재업로드 체크리스트** (재업로드 필요 책만, 완료 시 체크)

- [ ] a-common-sense-guide-to-data-structures-and-algorithms (20개)
- [ ] aws-complete-guide (10개)
- [ ] clean-architecture (26개)
- [ ] clean-code (17개)
- [ ] clean-software (34개)
- [ ] code-that-fits-in-your-head (18개)
- [ ] code-the-hidden-language (28개)
- [ ] design-it-from-programmer-to-software-architect (14개)
- [ ] docker-complete-guide (16개)
- [ ] essential-skills-for-junior-backend-developers-주니어-백엔드-개발자가-반드시-알아야-할-실무=-지식 (1개)
- [ ] frontend-performance-optimization-deep-dive (27개)
- [ ] functional-programming-complete-guide (17개)
- [ ] fundamentals-of-software-architecture-1st-edition (23개)
- [ ] fundamentals-of-software-architecture-2nd-edition (27개)
- [ ] good-code-bad-code (14개)
- [ ] head-first-design-patterns (14개)
- [ ] javascript-react-pattern (16개)
- [ ] legacy-code (8개)
- [ ] minimalism-programmer (9개)
- [ ] multi-paradigm-programming (4개)
- [ ] objects (8개)
- [ ] philosophy-of-software-design (8개)
- [ ] refactoring-2nd-edition (14개)
- [ ] structure-and-interpretation-of-computer-programs-javascript (18개)
- [ ] test-driven-development-by-example (32개)
- [ ] the-clean-coder (14개)
- [ ] the-complete-software-developers-career-guide (59개)
- [ ] the-essence-of-object-orientation-객체지향의-사실과-오해 (2개)
- [ ] the-hexagonal-developer (8개)
- [ ] the-pragmatic-programmer (10개)
- [ ] the-software-craftsman (17개)
- [ ] unit-testing (10개)

<details>
<summary>변경 노트 전체 파일 목록</summary>

**a-common-sense-guide-to-data-structures-and-algorithms** (20개)
- a-common-sense-guide-to-data-structures-and-algorithms/notes/ch01-why-data-structures-matter.md
- a-common-sense-guide-to-data-structures-and-algorithms/notes/ch02-why-algorithms-matter.md
- a-common-sense-guide-to-data-structures-and-algorithms/notes/ch03-big-o-notation.md
- a-common-sense-guide-to-data-structures-and-algorithms/notes/ch04-speeding-up-your-code-with-big-o.md
- a-common-sense-guide-to-data-structures-and-algorithms/notes/ch05-optimizing-code-with-and-without-big-o.md
- a-common-sense-guide-to-data-structures-and-algorithms/notes/ch06-optimizing-for-optimistic-scenarios.md
- a-common-sense-guide-to-data-structures-and-algorithms/notes/ch07-big-o-in-everyday-code.md
- a-common-sense-guide-to-data-structures-and-algorithms/notes/ch08-blazing-fast-lookup-with-hash-tables.md
- a-common-sense-guide-to-data-structures-and-algorithms/notes/ch09-crafting-elegant-code-with-stacks-and-queues.md
- a-common-sense-guide-to-data-structures-and-algorithms/notes/ch10-recursively-recurse-with-recursion.md
- a-common-sense-guide-to-data-structures-and-algorithms/notes/ch11-learning-to-write-in-recursive.md
- a-common-sense-guide-to-data-structures-and-algorithms/notes/ch12-dynamic-programming.md
- a-common-sense-guide-to-data-structures-and-algorithms/notes/ch13-recursive-algorithms-for-speed.md
- a-common-sense-guide-to-data-structures-and-algorithms/notes/ch14-node-based-data-structures.md
- a-common-sense-guide-to-data-structures-and-algorithms/notes/ch15-speeding-up-all-the-things-with-binary-search-trees.md
- a-common-sense-guide-to-data-structures-and-algorithms/notes/ch16-keeping-your-priorities-straight-with-heaps.md
- a-common-sense-guide-to-data-structures-and-algorithms/notes/ch17-it-doesnt-hurt-to-trie.md
- a-common-sense-guide-to-data-structures-and-algorithms/notes/ch18-connecting-everything-with-graphs.md
- a-common-sense-guide-to-data-structures-and-algorithms/notes/ch19-dealing-with-space-constraints.md
- a-common-sense-guide-to-data-structures-and-algorithms/notes/ch20-techniques-for-code-optimization.md

**aws-complete-guide** (10개)
- aws-complete-guide/notes/ch01-cloud-computing-fundamentals.md
- aws-complete-guide/notes/ch06-ec2.md
- aws-complete-guide/notes/ch07-lambda.md
- aws-complete-guide/notes/ch08-container-services.md
- aws-complete-guide/notes/ch09-s3.md
- aws-complete-guide/notes/ch11-rds.md
- aws-complete-guide/notes/ch12-dynamodb-and-elasticache.md
- aws-complete-guide/notes/ch14-cicd-pipeline.md
- aws-complete-guide/notes/ch15-cloudwatch.md
- aws-complete-guide/notes/ch16-advanced-security.md

**clean-architecture** (26개)
- clean-architecture/notes/appendix-architecture-archaeology.md
- clean-architecture/notes/ch01-what-is-design-and-architecture.md
- clean-architecture/notes/ch02-a-tale-of-two-values.md
- clean-architecture/notes/ch03-paradigm-overview.md
- clean-architecture/notes/ch04-structured-programming.md
- clean-architecture/notes/ch05-object-oriented-programming.md
- clean-architecture/notes/ch06-functional-programming.md
- clean-architecture/notes/ch07-srp-the-single-responsibility-principle.md
- clean-architecture/notes/ch08-ocp-the-open-closed-principle.md
- clean-architecture/notes/ch09-lsp-the-liskov-substitution-principle.md
- clean-architecture/notes/ch10-isp-the-interface-segregation-principle.md
- clean-architecture/notes/ch11-dip-the-dependency-inversion-principle.md
- clean-architecture/notes/ch12-components.md
- clean-architecture/notes/ch14-component-coupling.md
- clean-architecture/notes/ch15-what-is-architecture.md
- clean-architecture/notes/ch16-independence.md
- clean-architecture/notes/ch17-boundaries-drawing-lines.md
- clean-architecture/notes/ch18-boundary-anatomy.md
- clean-architecture/notes/ch19-policy-and-level.md
- clean-architecture/notes/ch20-business-rules.md
- clean-architecture/notes/ch22-the-clean-architecture.md
- clean-architecture/notes/ch23-presenters-and-humble-objects.md
- clean-architecture/notes/ch24-partial-boundaries.md
- clean-architecture/notes/ch29-clean-embedded-architecture.md
- clean-architecture/notes/ch31-the-web-is-a-detail.md
- clean-architecture/notes/ch34-the-missing-chapter.md

**clean-code** (17개)
- clean-code/notes/ch01-clean-code.md
- clean-code/notes/ch02-meaningful-names.md
- clean-code/notes/ch03-functions.md
- clean-code/notes/ch04-comments.md
- clean-code/notes/ch05-formatting.md
- clean-code/notes/ch06-objects-and-data-structures.md
- clean-code/notes/ch07-error-handling.md
- clean-code/notes/ch08-boundaries.md
- clean-code/notes/ch09-unit-tests.md
- clean-code/notes/ch10-classes.md
- clean-code/notes/ch11-systems.md
- clean-code/notes/ch12-emergence.md
- clean-code/notes/ch13-concurrency.md
- clean-code/notes/ch14-successive-refinement.md
- clean-code/notes/ch15-junit-internals.md
- clean-code/notes/ch16-refactoring-serialdate.md
- clean-code/notes/ch17-smells-and-heuristics.md

**clean-software** (34개)
- clean-software/notes/appendix-a-uml-notation-cgi.md
- clean-software/notes/appendix-b-uml-notation-statmux.md
- clean-software/notes/appendix-c-satire-of-two-companies.md
- clean-software/notes/appendix-d-source-code-is-the-design.md
- clean-software/notes/ch01-agile-practices.md
- clean-software/notes/ch02-extreme-programming-overview.md
- clean-software/notes/ch03-planning.md
- clean-software/notes/ch04-testing.md
- clean-software/notes/ch05-refactoring.md
- clean-software/notes/ch06-programming-episode.md
- clean-software/notes/ch07-what-is-agile-design.md
- clean-software/notes/ch08-single-responsibility-principle.md
- clean-software/notes/ch09-open-closed-principle.md
- clean-software/notes/ch10-liskov-substitution-principle.md
- clean-software/notes/ch11-dependency-inversion-principle.md
- clean-software/notes/ch12-interface-segregation-principle.md
- clean-software/notes/ch13-command-and-active-object.md
- clean-software/notes/ch14-template-method-and-strategy.md
- clean-software/notes/ch15-facade-and-mediator.md
- clean-software/notes/ch16-singleton-and-monostate.md
- clean-software/notes/ch17-null-object-pattern.md
- clean-software/notes/ch18-payroll-case-study-iteration-1.md
- clean-software/notes/ch19-payroll-case-study-implementation.md
- clean-software/notes/ch20-principles-of-package-design.md
- clean-software/notes/ch21-factory-pattern.md
- clean-software/notes/ch22-payroll-case-study-packaging.md
- clean-software/notes/ch23-composite-pattern.md
- clean-software/notes/ch24-observer-pattern.md
- clean-software/notes/ch25-abstract-server-adapter-bridge.md
- clean-software/notes/ch26-proxy-and-stairway-to-heaven.md
- clean-software/notes/ch27-case-study-weather-station.md
- clean-software/notes/ch28-visitor-pattern.md
- clean-software/notes/ch29-state-pattern.md
- clean-software/notes/ch30-ets-framework.md

**code-that-fits-in-your-head** (18개)
- code-that-fits-in-your-head/notes/appendix-a-list-of-practices.md
- code-that-fits-in-your-head/notes/appendix-b-bibliography.md
- code-that-fits-in-your-head/notes/appendix-c-building-the-example.md
- code-that-fits-in-your-head/notes/ch01-art-or-science.md
- code-that-fits-in-your-head/notes/ch02-checklists.md
- code-that-fits-in-your-head/notes/ch03-tackling-complexity.md
- code-that-fits-in-your-head/notes/ch04-vertical-slice.md
- code-that-fits-in-your-head/notes/ch05-encapsulation.md
- code-that-fits-in-your-head/notes/ch06-triangulation.md
- code-that-fits-in-your-head/notes/ch07-decomposition.md
- code-that-fits-in-your-head/notes/ch08-api-design.md
- code-that-fits-in-your-head/notes/ch09-teamwork.md
- code-that-fits-in-your-head/notes/ch11-editing-unit-tests.md
- code-that-fits-in-your-head/notes/ch12-troubleshooting.md
- code-that-fits-in-your-head/notes/ch13-separation-of-concerns.md
- code-that-fits-in-your-head/notes/ch14-rhythm.md
- code-that-fits-in-your-head/notes/ch15-the-usual-suspects.md
- code-that-fits-in-your-head/notes/ch16-tour.md

**code-the-hidden-language** (28개)
- code-the-hidden-language/notes/ch01-best-friends.md
- code-the-hidden-language/notes/ch02-codes-and-combinations.md
- code-the-hidden-language/notes/ch03-braille-and-binary-codes.md
- code-the-hidden-language/notes/ch04-anatomy-of-a-flashlight.md
- code-the-hidden-language/notes/ch05-communicating-around-corners.md
- code-the-hidden-language/notes/ch06-logic-with-switches.md
- code-the-hidden-language/notes/ch07-telegraphs-and-relays.md
- code-the-hidden-language/notes/ch08-relays-and-gates.md
- code-the-hidden-language/notes/ch09-our-ten-digits.md
- code-the-hidden-language/notes/ch10-alternative-10s.md
- code-the-hidden-language/notes/ch11-bit-by-bit-by-bit.md
- code-the-hidden-language/notes/ch12-bytes-and-hexadecimal.md
- code-the-hidden-language/notes/ch13-from-ascii-to-unicode.md
- code-the-hidden-language/notes/ch14-adding-with-logic-gates.md
- code-the-hidden-language/notes/ch15-is-this-for-real.md
- code-the-hidden-language/notes/ch16-but-what-about-subtraction.md
- code-the-hidden-language/notes/ch17-feedback-and-flip-flops.md
- code-the-hidden-language/notes/ch18-lets-build-a-clock.md
- code-the-hidden-language/notes/ch19-an-assemblage-of-memory.md
- code-the-hidden-language/notes/ch20-automating-arithmetic.md
- code-the-hidden-language/notes/ch21-the-arithmetic-logic-unit.md
- code-the-hidden-language/notes/ch22-registers-and-busses.md
- code-the-hidden-language/notes/ch23-cpu-control-signals.md
- code-the-hidden-language/notes/ch24-jumps-loops-and-calls.md
- code-the-hidden-language/notes/ch25-peripherals.md
- code-the-hidden-language/notes/ch26-the-operating-system.md
- code-the-hidden-language/notes/ch27-coding.md
- code-the-hidden-language/notes/ch28-the-world-wide-web.md

**design-it-from-programmer-to-software-architect** (14개)
- design-it-from-programmer-to-software-architect/notes/ch01-becoming-a-software-architect.md
- design-it-from-programmer-to-software-architect/notes/ch02-design-thinking-fundamentals.md
- design-it-from-programmer-to-software-architect/notes/ch03-designing-strategies.md
- design-it-from-programmer-to-software-architect/notes/ch04-empathizing-with-stakeholders.md
- design-it-from-programmer-to-software-architect/notes/ch05-architecturally-significant-requirements.md
- design-it-from-programmer-to-software-architect/notes/ch06-choosing-architecture.md
- design-it-from-programmer-to-software-architect/notes/ch07-patterns.md
- design-it-from-programmer-to-software-architect/notes/ch08-modeling-complexity.md
- design-it-from-programmer-to-software-architect/notes/ch09-architecture-design-studio.md
- design-it-from-programmer-to-software-architect/notes/ch10-visualizing-design.md
- design-it-from-programmer-to-software-architect/notes/ch11-documenting-architecture.md
- design-it-from-programmer-to-software-architect/notes/ch12-evaluating-architecture.md
- design-it-from-programmer-to-software-architect/notes/ch13-empowering-the-architect.md
- design-it-from-programmer-to-software-architect/notes/ch14-understanding-the-problem.md

**docker-complete-guide** (16개)
- docker-complete-guide/notes/ch01-what-is-docker.md
- docker-complete-guide/notes/ch02-images.md
- docker-complete-guide/notes/ch03-containers.md
- docker-complete-guide/notes/ch04-dockerfile-deep-dive.md
- docker-complete-guide/notes/ch05-volumes-and-bind-mounts.md
- docker-complete-guide/notes/ch06-networking.md
- docker-complete-guide/notes/ch07-docker-compose.md
- docker-complete-guide/notes/ch08-docker-compose-advanced-patterns.md
- docker-complete-guide/notes/ch09-image-optimization.md
- docker-complete-guide/notes/ch10-security.md
- docker-complete-guide/notes/ch11-logging-monitoring-debugging.md
- docker-complete-guide/notes/ch12-nodejs-docker-best-practices.md
- docker-complete-guide/notes/ch13-monorepo-docker-strategies.md
- docker-complete-guide/notes/ch14-cicd-pipeline-with-docker.md
- docker-complete-guide/notes/ch15-beyond-docker.md
- docker-complete-guide/notes/hands-on-qna-notes.md

**essential-skills-for-junior-backend-developers-주니어-백엔드-개발자가-반드시-알아야-할-실무=-지식** (1개)
- essential-skills-for-junior-backend-developers-주니어-백엔드-개발자가-반드시-알아야-할-실무=-지식/notes/ch02-service-performance.md

**frontend-performance-optimization-deep-dive** (27개)
- frontend-performance-optimization-deep-dive/notes/appendix-a-history-of-core-web-vitals.md
- frontend-performance-optimization-deep-dive/notes/ch00-introduction.md
- frontend-performance-optimization-deep-dive/notes/ch01-network-optimization.md
- frontend-performance-optimization-deep-dive/notes/ch03-browser-cache-design.md
- frontend-performance-optimization-deep-dive/notes/ch04-resource-priority.md
- frontend-performance-optimization-deep-dive/notes/ch05-preload-scanner.md
- frontend-performance-optimization-deep-dive/notes/ch06-async-and-defer.md
- frontend-performance-optimization-deep-dive/notes/ch07-render-blocking-resources.md
- frontend-performance-optimization-deep-dive/notes/ch08-polyfills-on-demand.md
- frontend-performance-optimization-deep-dive/notes/ch09-remove-unused-resources-first.md
- frontend-performance-optimization-deep-dive/notes/ch10-code-splitting-strategy.md
- frontend-performance-optimization-deep-dive/notes/ch11-move-work-to-server.md
- frontend-performance-optimization-deep-dive/notes/ch12-image-delivery.md
- frontend-performance-optimization-deep-dive/notes/ch13-video-optimization.md
- frontend-performance-optimization-deep-dive/notes/ch14-fonts-as-performance-asset.md
- frontend-performance-optimization-deep-dive/notes/ch15-minimal-css.md
- frontend-performance-optimization-deep-dive/notes/ch16-eliminate-hydration.md
- frontend-performance-optimization-deep-dive/notes/ch17-data-caching-optimistic-updates.md
- frontend-performance-optimization-deep-dive/notes/ch18-short-frequent-javascript.md
- frontend-performance-optimization-deep-dive/notes/ch19-memory-leak-lifecycle.md
- frontend-performance-optimization-deep-dive/notes/ch20-cls-dynamic-content.md
- frontend-performance-optimization-deep-dive/notes/ch21-animations-at-60fps.md
- frontend-performance-optimization-deep-dive/notes/ch22-component-optimization-state-scope.md
- frontend-performance-optimization-deep-dive/notes/ch23-control-third-party-code.md
- frontend-performance-optimization-deep-dive/notes/ch24-i18n-per-user-code.md
- frontend-performance-optimization-deep-dive/notes/ch25-next-gen-web-standards.md
- frontend-performance-optimization-deep-dive/notes/ch26-closing.md

**functional-programming-complete-guide** (17개)
- functional-programming-complete-guide/notes/ch01-what-is-functional-programming.md
- functional-programming-complete-guide/notes/ch02-from-imperative-to-functional.md
- functional-programming-complete-guide/notes/ch03-currying-and-composition.md
- functional-programming-complete-guide/notes/ch04-collection-centric-programming.md
- functional-programming-complete-guide/notes/ch05-iterator-pattern-and-iteration-protocol.md
- functional-programming-complete-guide/notes/ch06-generators.md
- functional-programming-complete-guide/notes/ch07-higher-order-functions-for-iterables.md
- functional-programming-complete-guide/notes/ch08-lazy-evaluation.md
- functional-programming-complete-guide/notes/ch09-type-inference-and-generics.md
- functional-programming-complete-guide/notes/ch10-fxiterable-and-metaprogramming.md
- functional-programming-complete-guide/notes/ch11-learning-from-haskell.md
- functional-programming-complete-guide/notes/ch12-async-as-values.md
- functional-programming-complete-guide/notes/ch13-monads-and-kleisli-composition.md
- functional-programming-complete-guide/notes/ch14-laziness-and-concurrency.md
- functional-programming-complete-guide/notes/ch15-async-await-pipelines-and-error-handling.md
- functional-programming-complete-guide/notes/ch16-practical-list-processing-patterns.md
- functional-programming-complete-guide/notes/ch19-conditions-and-effects-as-values.md

**fundamentals-of-software-architecture-1st-edition** (23개)
- fundamentals-of-software-architecture-1st-edition/notes/ch01-introduction.md
- fundamentals-of-software-architecture-1st-edition/notes/ch02-architectural-thinking.md
- fundamentals-of-software-architecture-1st-edition/notes/ch03-modularity.md
- fundamentals-of-software-architecture-1st-edition/notes/ch05-identifying-architecture-characteristics.md
- fundamentals-of-software-architecture-1st-edition/notes/ch06-measuring-and-governing-architecture-characteristics.md
- fundamentals-of-software-architecture-1st-edition/notes/ch07-scope-of-architecture-characteristics.md
- fundamentals-of-software-architecture-1st-edition/notes/ch08-component-based-thinking.md
- fundamentals-of-software-architecture-1st-edition/notes/ch09-foundations.md
- fundamentals-of-software-architecture-1st-edition/notes/ch10-layered-architecture-style.md
- fundamentals-of-software-architecture-1st-edition/notes/ch11-pipeline-architecture-style.md
- fundamentals-of-software-architecture-1st-edition/notes/ch12-microkernel-architecture-style.md
- fundamentals-of-software-architecture-1st-edition/notes/ch13-service-based-architecture-style.md
- fundamentals-of-software-architecture-1st-edition/notes/ch14-event-driven-architecture-style.md
- fundamentals-of-software-architecture-1st-edition/notes/ch15-space-based-architecture-style.md
- fundamentals-of-software-architecture-1st-edition/notes/ch16-orchestration-driven-service-oriented-architecture.md
- fundamentals-of-software-architecture-1st-edition/notes/ch17-microservices-architecture.md
- fundamentals-of-software-architecture-1st-edition/notes/ch18-choosing-the-appropriate-architecture-style.md
- fundamentals-of-software-architecture-1st-edition/notes/ch19-architecture-decisions.md
- fundamentals-of-software-architecture-1st-edition/notes/ch20-analyzing-architecture-risk.md
- fundamentals-of-software-architecture-1st-edition/notes/ch21-diagramming-and-presenting-architecture.md
- fundamentals-of-software-architecture-1st-edition/notes/ch22-making-teams-effective.md
- fundamentals-of-software-architecture-1st-edition/notes/ch23-negotiation-and-leadership-skills.md
- fundamentals-of-software-architecture-1st-edition/notes/ch24-developing-a-career-path.md

**fundamentals-of-software-architecture-2nd-edition** (27개)
- fundamentals-of-software-architecture-2nd-edition/notes/ch01-introduction.md
- fundamentals-of-software-architecture-2nd-edition/notes/ch02-architectural-thinking.md
- fundamentals-of-software-architecture-2nd-edition/notes/ch03-modularity.md
- fundamentals-of-software-architecture-2nd-edition/notes/ch04-defining-architecture-characteristics.md
- fundamentals-of-software-architecture-2nd-edition/notes/ch05-identifying-architecture-characteristics.md
- fundamentals-of-software-architecture-2nd-edition/notes/ch06-measuring-and-governing-architecture-characteristics.md
- fundamentals-of-software-architecture-2nd-edition/notes/ch07-scope-of-architecture-characteristics.md
- fundamentals-of-software-architecture-2nd-edition/notes/ch08-component-based-thinking.md
- fundamentals-of-software-architecture-2nd-edition/notes/ch09-foundations.md
- fundamentals-of-software-architecture-2nd-edition/notes/ch10-layered-architecture-style.md
- fundamentals-of-software-architecture-2nd-edition/notes/ch11-modular-monolith-architecture-style.md
- fundamentals-of-software-architecture-2nd-edition/notes/ch12-pipeline-architecture-style.md
- fundamentals-of-software-architecture-2nd-edition/notes/ch13-microkernel-architecture-style.md
- fundamentals-of-software-architecture-2nd-edition/notes/ch14-service-based-architecture-style.md
- fundamentals-of-software-architecture-2nd-edition/notes/ch15-event-driven-architecture-style.md
- fundamentals-of-software-architecture-2nd-edition/notes/ch16-space-based-architecture-style.md
- fundamentals-of-software-architecture-2nd-edition/notes/ch17-orchestration-driven-service-oriented-architecture.md
- fundamentals-of-software-architecture-2nd-edition/notes/ch18-microservices-architecture-style.md
- fundamentals-of-software-architecture-2nd-edition/notes/ch19-choosing-the-appropriate-architecture-style.md
- fundamentals-of-software-architecture-2nd-edition/notes/ch20-architectural-patterns.md
- fundamentals-of-software-architecture-2nd-edition/notes/ch21-architecture-decisions.md
- fundamentals-of-software-architecture-2nd-edition/notes/ch22-analyzing-architecture-risk.md
- fundamentals-of-software-architecture-2nd-edition/notes/ch23-diagramming-architecture.md
- fundamentals-of-software-architecture-2nd-edition/notes/ch24-making-teams-effective.md
- fundamentals-of-software-architecture-2nd-edition/notes/ch25-negotiation-and-leadership-skills.md
- fundamentals-of-software-architecture-2nd-edition/notes/ch26-architecture-intersections.md
- fundamentals-of-software-architecture-2nd-edition/notes/ch27-software-architecture-laws-revisited.md

**good-code-bad-code** (14개)
- good-code-bad-code/notes/appendix-a-chocolate-brownie-recipe.md
- good-code-bad-code/notes/appendix-b-null-safety-and-optionals.md
- good-code-bad-code/notes/appendix-c-additional-code-examples.md
- good-code-bad-code/notes/ch01-code-quality.md
- good-code-bad-code/notes/ch02-layers-of-abstraction.md
- good-code-bad-code/notes/ch03-other-engineers-and-code-contracts.md
- good-code-bad-code/notes/ch04-errors.md
- good-code-bad-code/notes/ch05-make-code-readable.md
- good-code-bad-code/notes/ch06-avoid-surprises.md
- good-code-bad-code/notes/ch07-make-code-hard-to-misuse.md
- good-code-bad-code/notes/ch08-make-code-modular.md
- good-code-bad-code/notes/ch09-make-code-reusable-and-generalizable.md
- good-code-bad-code/notes/ch10-unit-testing-principles.md
- good-code-bad-code/notes/ch11-unit-testing-practices.md

**head-first-design-patterns** (14개)
- head-first-design-patterns/notes/ch01-strategy-pattern.md
- head-first-design-patterns/notes/ch02-observer-pattern.md
- head-first-design-patterns/notes/ch03-decorator-pattern.md
- head-first-design-patterns/notes/ch04-factory-pattern.md
- head-first-design-patterns/notes/ch05-singleton-pattern.md
- head-first-design-patterns/notes/ch06-command-pattern.md
- head-first-design-patterns/notes/ch07-adapter-facade-pattern.md
- head-first-design-patterns/notes/ch08-template-method-pattern.md
- head-first-design-patterns/notes/ch09-iterator-composite-pattern.md
- head-first-design-patterns/notes/ch10-state-pattern.md
- head-first-design-patterns/notes/ch11-proxy-pattern.md
- head-first-design-patterns/notes/ch12-compound-pattern.md
- head-first-design-patterns/notes/ch13-patterns-in-real-world.md
- head-first-design-patterns/notes/ch14-leftover-patterns.md

**javascript-react-pattern** (16개)
- javascript-react-pattern/notes/ch01-introduction-to-design-patterns.md
- javascript-react-pattern/notes/ch02-patternity-testing-and-proto-patterns.md
- javascript-react-pattern/notes/ch03-structuring-design-patterns.md
- javascript-react-pattern/notes/ch04-anti-patterns.md
- javascript-react-pattern/notes/ch05-modern-javascript-syntax-and-features.md
- javascript-react-pattern/notes/ch06-categories-of-design-patterns.md
- javascript-react-pattern/notes/ch07-creational-patterns.md
- javascript-react-pattern/notes/ch08-structural-patterns.md
- javascript-react-pattern/notes/ch09-behavioral-patterns.md
- javascript-react-pattern/notes/ch10-mv-star-patterns.md
- javascript-react-pattern/notes/ch11-asynchronous-programming-patterns.md
- javascript-react-pattern/notes/ch12-modular-javascript-design-patterns.md
- javascript-react-pattern/notes/ch13-namespacing-patterns.md
- javascript-react-pattern/notes/ch14-react-design-patterns.md
- javascript-react-pattern/notes/ch15-rendering-patterns.md
- javascript-react-pattern/notes/ch16-react-application-structure.md

**legacy-code** (8개)
- legacy-code/notes/case-study-other-books.md
- legacy-code/notes/case-study-version-migration.md
- legacy-code/notes/ch02-working-with-feedback.md
- legacy-code/notes/ch05-tools.md
- legacy-code/notes/ch15-my-application-is-all-api-calls.md
- legacy-code/notes/ch16-i-dont-understand-the-code.md
- legacy-code/notes/ch17-my-application-has-no-structure.md
- legacy-code/notes/ch24-we-feel-overwhelmed.md

**mastering-api-architecture** (11개)
- mastering-api-architecture/notes/ch00-introduction.md
- mastering-api-architecture/notes/ch01-design-build-and-specify-apis.md
- mastering-api-architecture/notes/ch02-testing-apis.md
- mastering-api-architecture/notes/ch03-api-gateways.md
- mastering-api-architecture/notes/ch04-service-mesh.md
- mastering-api-architecture/notes/ch05-deploying-and-releasing-apis.md
- mastering-api-architecture/notes/ch06-threat-modeling-for-apis.md
- mastering-api-architecture/notes/ch07-authentication-and-authorization.md
- mastering-api-architecture/notes/ch08-redesigning-to-api-driven-architectures.md
- mastering-api-architecture/notes/ch09-evolving-toward-cloud-platforms.md
- mastering-api-architecture/notes/ch10-wrap-up.md

**minimalism-programmer** (9개)
- minimalism-programmer/notes/ch01-the-aesthetics-of-simplicity.md
- minimalism-programmer/notes/ch02-code-diet.md
- minimalism-programmer/notes/ch03-project-optimization.md
- minimalism-programmer/notes/ch04-task-automation.md
- minimalism-programmer/notes/ch05-embracing-change.md
- minimalism-programmer/notes/ch06-soft-skills.md
- minimalism-programmer/notes/ch07-data-driven-development.md
- minimalism-programmer/notes/ch08-readable-code.md
- minimalism-programmer/notes/ch09-conclusion.md

**multi-paradigm-programming** (4개)
- multi-paradigm-programming/notes/ch01-multi-paradigm-extends-modern-languages.md
- multi-paradigm-programming/notes/ch03-code-object-function-generator-iterator-lisp.md
- multi-paradigm-programming/notes/ch04-asynchronous-programming.md
- multi-paradigm-programming/notes/ch05-practical-functional-programming.md

**objects** (8개)
- objects/notes/appendix-a-design-by-contract.md
- objects/notes/appendix-b-implementing-type-hierarchies.md
- objects/notes/appendix-c-dynamic-collaboration-static-code.md
- objects/notes/ch03-roles-responsibilities-collaboration.md
- objects/notes/ch09-flexible-design.md
- objects/notes/ch10-inheritance-and-code-reuse.md
- objects/notes/ch12-polymorphism.md
- objects/notes/ch15-design-patterns-and-frameworks.md

**philosophy-of-software-design** (8개)
- philosophy-of-software-design/notes/ch01-introduction.md
- philosophy-of-software-design/notes/ch02-the-nature-of-complexity.md
- philosophy-of-software-design/notes/ch06-general-purpose-modules-are-deeper.md
- philosophy-of-software-design/notes/ch08-pull-complexity-downwards.md
- philosophy-of-software-design/notes/ch10-define-errors-out-of-existence.md
- philosophy-of-software-design/notes/ch16-modifying-existing-code.md
- philosophy-of-software-design/notes/ch21-decide-what-matters.md
- philosophy-of-software-design/notes/ch22-conclusion.md

**programmers-coding-test** (8개)
- programmers-coding-test/notes/ch05-array.md
- programmers-coding-test/notes/ch06-stack.md
- programmers-coding-test/notes/ch07-queue.md
- programmers-coding-test/notes/ch08-hash.md
- programmers-coding-test/notes/ch09-tree.md
- programmers-coding-test/notes/ch10-set.md
- programmers-coding-test/notes/ch11-graph.md
- programmers-coding-test/notes/ch12-backtracking.md

**quant** (6개)
- quant/notes/ch14-undervalued-stocks.md
- quant/notes/ch15-quality-and-value-quality.md
- quant/notes/ch16-momentum-and-ultra.md
- quant/notes/ch17-strategy-selection.md
- quant/notes/ch18-reducing-mdd.md
- quant/notes/ch19-final-words.md

**refactoring-2nd-edition** (14개)
- refactoring-2nd-edition/notes/appendix-a-list-of-refactorings.md
- refactoring-2nd-edition/notes/appendix-b-smells-to-refactorings.md
- refactoring-2nd-edition/notes/ch01-refactoring-a-first-example.md
- refactoring-2nd-edition/notes/ch02-principles-in-refactoring.md
- refactoring-2nd-edition/notes/ch03-bad-smells-in-code.md
- refactoring-2nd-edition/notes/ch04-building-tests.md
- refactoring-2nd-edition/notes/ch05-introducing-the-catalog.md
- refactoring-2nd-edition/notes/ch06-a-first-set-of-refactorings.md
- refactoring-2nd-edition/notes/ch07-encapsulation.md
- refactoring-2nd-edition/notes/ch08-moving-features.md
- refactoring-2nd-edition/notes/ch09-organizing-data.md
- refactoring-2nd-edition/notes/ch10-simplifying-conditional-logic.md
- refactoring-2nd-edition/notes/ch11-refactoring-apis.md
- refactoring-2nd-edition/notes/ch12-dealing-with-inheritance.md

**structure-and-interpretation-of-computer-programs-javascript** (18개)
- structure-and-interpretation-of-computer-programs-javascript/notes/sec1.1-elements-of-programming.md
- structure-and-interpretation-of-computer-programs-javascript/notes/sec1.2-functions-and-processes.md
- structure-and-interpretation-of-computer-programs-javascript/notes/sec1.3-higher-order-functions.md
- structure-and-interpretation-of-computer-programs-javascript/notes/sec2.1-data-abstraction.md
- structure-and-interpretation-of-computer-programs-javascript/notes/sec2.2-hierarchical-data.md
- structure-and-interpretation-of-computer-programs-javascript/notes/sec2.3-symbolic-data.md
- structure-and-interpretation-of-computer-programs-javascript/notes/sec2.4-multiple-representations.md
- structure-and-interpretation-of-computer-programs-javascript/notes/sec2.5-generic-operations.md
- structure-and-interpretation-of-computer-programs-javascript/notes/sec3.1-assignment-and-local-state.md
- structure-and-interpretation-of-computer-programs-javascript/notes/sec3.2-environment-model.md
- structure-and-interpretation-of-computer-programs-javascript/notes/sec3.3-mutable-data.md
- structure-and-interpretation-of-computer-programs-javascript/notes/sec3.4-concurrency.md
- structure-and-interpretation-of-computer-programs-javascript/notes/sec3.5-streams.md
- structure-and-interpretation-of-computer-programs-javascript/notes/sec4.1-metacircular-evaluator.md
- structure-and-interpretation-of-computer-programs-javascript/notes/sec4.2-lazy-evaluation.md
- structure-and-interpretation-of-computer-programs-javascript/notes/sec4.3-nondeterministic-computing.md
- structure-and-interpretation-of-computer-programs-javascript/notes/sec5.1-register-machines.md
- structure-and-interpretation-of-computer-programs-javascript/notes/sec5.3-storage-and-gc.md

**test-driven-development-by-example** (32개)
- test-driven-development-by-example/notes/ch01-multi-currency-money.md
- test-driven-development-by-example/notes/ch02-degenerate-objects.md
- test-driven-development-by-example/notes/ch03-equality-for-all.md
- test-driven-development-by-example/notes/ch04-privacy.md
- test-driven-development-by-example/notes/ch05-franc-ly-speaking.md
- test-driven-development-by-example/notes/ch06-equality-for-all-redux.md
- test-driven-development-by-example/notes/ch07-apples-and-oranges.md
- test-driven-development-by-example/notes/ch08-makin-objects.md
- test-driven-development-by-example/notes/ch09-times-were-livin-in.md
- test-driven-development-by-example/notes/ch10-interesting-times.md
- test-driven-development-by-example/notes/ch11-the-root-of-all-evil.md
- test-driven-development-by-example/notes/ch12-addition-finally.md
- test-driven-development-by-example/notes/ch13-make-it.md
- test-driven-development-by-example/notes/ch14-change.md
- test-driven-development-by-example/notes/ch15-mixed-currencies.md
- test-driven-development-by-example/notes/ch16-abstraction-finally.md
- test-driven-development-by-example/notes/ch17-money-retrospective.md
- test-driven-development-by-example/notes/ch18-first-steps-to-xunit.md
- test-driven-development-by-example/notes/ch19-set-the-table.md
- test-driven-development-by-example/notes/ch20-cleaning-up-after.md
- test-driven-development-by-example/notes/ch21-counting.md
- test-driven-development-by-example/notes/ch22-dealing-with-failure.md
- test-driven-development-by-example/notes/ch23-how-suite-it-is.md
- test-driven-development-by-example/notes/ch24-xunit-retrospective.md
- test-driven-development-by-example/notes/ch25-test-driven-development-patterns.md
- test-driven-development-by-example/notes/ch26-red-bar-patterns.md
- test-driven-development-by-example/notes/ch27-testing-patterns.md
- test-driven-development-by-example/notes/ch28-green-bar-patterns.md
- test-driven-development-by-example/notes/ch29-xunit-patterns.md
- test-driven-development-by-example/notes/ch30-design-patterns.md
- test-driven-development-by-example/notes/ch31-refactoring.md
- test-driven-development-by-example/notes/ch32-mastering-tdd.md

**the-clean-coder** (14개)
- the-clean-coder/notes/ch00-introduction.md
- the-clean-coder/notes/ch01-professionalism.md
- the-clean-coder/notes/ch02-saying-no.md
- the-clean-coder/notes/ch03-saying-yes.md
- the-clean-coder/notes/ch04-coding.md
- the-clean-coder/notes/ch05-test-driven-development.md
- the-clean-coder/notes/ch06-practicing.md
- the-clean-coder/notes/ch07-acceptance-testing.md
- the-clean-coder/notes/ch08-testing-strategies.md
- the-clean-coder/notes/ch09-time-management.md
- the-clean-coder/notes/ch10-estimation.md
- the-clean-coder/notes/ch11-pressure.md
- the-clean-coder/notes/ch12-collaboration.md
- the-clean-coder/notes/ch13-teams-and-projects.md

**the-complete-software-developers-career-guide** (59개)
- the-complete-software-developers-career-guide/notes/ch01-how-to-use-this-book.md
- the-complete-software-developers-career-guide/notes/ch02-getting-started.md
- the-complete-software-developers-career-guide/notes/ch03-what-skills-you-need.md
- the-complete-software-developers-career-guide/notes/ch04-how-to-improve-your-skills.md
- the-complete-software-developers-career-guide/notes/ch05-choosing-a-programming-language.md
- the-complete-software-developers-career-guide/notes/ch06-learning-your-first-language.md
- the-complete-software-developers-career-guide/notes/ch07-going-to-college.md
- the-complete-software-developers-career-guide/notes/ch08-coding-bootcamps.md
- the-complete-software-developers-career-guide/notes/ch09-self-study.md
- the-complete-software-developers-career-guide/notes/ch10-internships.md
- the-complete-software-developers-career-guide/notes/ch11-getting-a-job-without-experience.md
- the-complete-software-developers-career-guide/notes/ch12-how-to-find-a-job.md
- the-complete-software-developers-career-guide/notes/ch13-creating-a-resume.md
- the-complete-software-developers-career-guide/notes/ch14-the-interview-process.md
- the-complete-software-developers-career-guide/notes/ch15-salary-and-negotiation.md
- the-complete-software-developers-career-guide/notes/ch16-how-to-quit-a-job.md
- the-complete-software-developers-career-guide/notes/ch18-moving-from-another-tech-field.md
- the-complete-software-developers-career-guide/notes/ch19-contractor-vs-employee.md
- the-complete-software-developers-career-guide/notes/ch20-how-recruiting-works.md
- the-complete-software-developers-career-guide/notes/ch21-overview-of-programming-languages.md
- the-complete-software-developers-career-guide/notes/ch22-what-is-web-development.md
- the-complete-software-developers-career-guide/notes/ch23-mobile-development.md
- the-complete-software-developers-career-guide/notes/ch24-backend-development.md
- the-complete-software-developers-career-guide/notes/ch25-video-game-development.md
- the-complete-software-developers-career-guide/notes/ch26-dba-and-devops.md
- the-complete-software-developers-career-guide/notes/ch27-software-development-methodologies.md
- the-complete-software-developers-career-guide/notes/ch28-testing-and-qa-basics.md
- the-complete-software-developers-career-guide/notes/ch29-tdd-and-unit-testing.md
- the-complete-software-developers-career-guide/notes/ch30-source-control.md
- the-complete-software-developers-career-guide/notes/ch32-debugging.md
- the-complete-software-developers-career-guide/notes/ch33-code-maintenance.md
- the-complete-software-developers-career-guide/notes/ch34-jobs-and-titles.md
- the-complete-software-developers-career-guide/notes/ch35-types-of-work.md
- the-complete-software-developers-career-guide/notes/ch36-dealing-with-coworkers.md
- the-complete-software-developers-career-guide/notes/ch37-dealing-with-your-boss.md
- the-complete-software-developers-career-guide/notes/ch38-dealing-with-qa.md
- the-complete-software-developers-career-guide/notes/ch39-work-life-balance.md
- the-complete-software-developers-career-guide/notes/ch40-working-on-a-team.md
- the-complete-software-developers-career-guide/notes/ch41-being-persuasive.md
- the-complete-software-developers-career-guide/notes/ch42-dressing-for-success.md
- the-complete-software-developers-career-guide/notes/ch43-getting-a-good-review.md
- the-complete-software-developers-career-guide/notes/ch44-dealing-with-prejudice.md
- the-complete-software-developers-career-guide/notes/ch45-being-a-good-leader.md
- the-complete-software-developers-career-guide/notes/ch46-raises-and-promotions.md
- the-complete-software-developers-career-guide/notes/ch47-women-in-tech.md
- the-complete-software-developers-career-guide/notes/ch48-building-your-reputation.md
- the-complete-software-developers-career-guide/notes/ch49-networking.md
- the-complete-software-developers-career-guide/notes/ch50-staying-relevant.md
- the-complete-software-developers-career-guide/notes/ch51-generalist-vs-specialist.md
- the-complete-software-developers-career-guide/notes/ch52-speaking-at-conferences.md
- the-complete-software-developers-career-guide/notes/ch53-blogging.md
- the-complete-software-developers-career-guide/notes/ch54-freelancing-and-entrepreneurship.md
- the-complete-software-developers-career-guide/notes/ch55-career-paths.md
- the-complete-software-developers-career-guide/notes/ch56-job-security.md
- the-complete-software-developers-career-guide/notes/ch57-education-and-certifications.md
- the-complete-software-developers-career-guide/notes/ch58-side-projects.md
- the-complete-software-developers-career-guide/notes/ch59-recommended-reading.md
- the-complete-software-developers-career-guide/notes/ch60-conclusion.md
- the-complete-software-developers-career-guide/notes/ch61-living-as-a-developer.md

**the-essence-of-object-orientation-객체지향의-사실과-오해** (2개)
- the-essence-of-object-orientation-객체지향의-사실과-오해/notes/ch02-objects-in-wonderland.md
- the-essence-of-object-orientation-객체지향의-사실과-오해/notes/ch06-object-map.md

**the-hexagonal-developer** (8개)
- the-hexagonal-developer/notes/ch01-getting-started.md
- the-hexagonal-developer/notes/ch02-implementation-skills-and-learning.md
- the-hexagonal-developer/notes/ch03-software-value-and-cost.md
- the-hexagonal-developer/notes/ch04-understanding-code.md
- the-hexagonal-developer/notes/ch05-cohesion-and-coupling.md
- the-hexagonal-developer/notes/ch09-task-management.md
- the-hexagonal-developer/notes/ch10-organizing-and-sharing.md
- the-hexagonal-developer/notes/ch11-leaders-and-followers.md

**the-pragmatic-programmer** (10개)
- the-pragmatic-programmer/notes/ch01-a-pragmatic-philosophy.md
- the-pragmatic-programmer/notes/ch02-a-pragmatic-approach.md
- the-pragmatic-programmer/notes/ch03-the-basic-tools.md
- the-pragmatic-programmer/notes/ch04-pragmatic-paranoia.md
- the-pragmatic-programmer/notes/ch05-bend-or-break.md
- the-pragmatic-programmer/notes/ch06-concurrency.md
- the-pragmatic-programmer/notes/ch07-while-you-are-coding.md
- the-pragmatic-programmer/notes/ch08-before-the-project.md
- the-pragmatic-programmer/notes/ch09-pragmatic-projects.md
- the-pragmatic-programmer/notes/tips.md

**the-software-craftsman** (17개)
- the-software-craftsman/notes/appendix-a-misconceptions-about-software-craftsmanship.md
- the-software-craftsman/notes/ch01-software-development-in-the-21st-century.md
- the-software-craftsman/notes/ch02-agile.md
- the-software-craftsman/notes/ch03-software-craftsmanship.md
- the-software-craftsman/notes/ch04-the-attitude-of-a-software-craftsman.md
- the-software-craftsman/notes/ch05-heroes-goodwill-and-professionalism.md
- the-software-craftsman/notes/ch06-working-software.md
- the-software-craftsman/notes/ch07-technical-practices.md
- the-software-craftsman/notes/ch08-the-long-road.md
- the-software-craftsman/notes/ch09-recruitment.md
- the-software-craftsman/notes/ch10-interviewing-software-craftsmen.md
- the-software-craftsman/notes/ch11-wrong-interview-approaches.md
- the-software-craftsman/notes/ch12-the-cost-of-low-morale.md
- the-software-craftsman/notes/ch13-the-culture-of-learning.md
- the-software-craftsman/notes/ch14-driving-technical-changes.md
- the-software-craftsman/notes/ch15-pragmatic-craftsmanship.md
- the-software-craftsman/notes/ch16-a-career-as-a-software-craftsman.md

**this-is-coding-test** (19개)
- this-is-coding-test/notes/ch00-javascript-basics-for-coding-test.md
- this-is-coding-test/notes/ch03-greedy.md
- this-is-coding-test/notes/ch04-implementation.md
- this-is-coding-test/notes/ch05-dfs-bfs.md
- this-is-coding-test/notes/ch06-sorting.md
- this-is-coding-test/notes/ch07-binary-search.md
- this-is-coding-test/notes/ch08-dynamic-programming.md
- this-is-coding-test/notes/ch09-shortest-path.md
- this-is-coding-test/notes/ch10-graph-theory.md
- this-is-coding-test/notes/ch11-greedy-problems.md
- this-is-coding-test/notes/ch12-implementation-problems.md
- this-is-coding-test/notes/ch13-dfs-bfs-problems.md
- this-is-coding-test/notes/ch14-sorting-problems.md
- this-is-coding-test/notes/ch15-binary-search-problems.md
- this-is-coding-test/notes/ch16-dynamic-programming-problems.md
- this-is-coding-test/notes/ch17-shortest-path-problems.md
- this-is-coding-test/notes/ch18-graph-theory-problems.md
- this-is-coding-test/notes/ch19-samsung-2020.md
- this-is-coding-test/notes/db-design.md

**unit-testing** (10개)
- unit-testing/notes/ch01-the-goal-of-unit-testing.md
- unit-testing/notes/ch02-what-is-a-unit-test.md
- unit-testing/notes/ch03-the-anatomy-of-a-unit-test.md
- unit-testing/notes/ch04-the-four-pillars-of-a-good-unit-test.md
- unit-testing/notes/ch05-mocks-and-test-fragility.md
- unit-testing/notes/ch06-styles-of-unit-testing.md
- unit-testing/notes/ch07-refactoring-toward-valuable-tests.md
- unit-testing/notes/ch08-why-integration-testing.md
- unit-testing/notes/ch10-testing-the-database.md
- unit-testing/notes/ch11-unit-testing-anti-patterns.md

</details>
