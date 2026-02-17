# Working Effectively with Legacy Code

**저자**: Michael C. Feathers
**출판**: 2004, Prentice Hall (Robert C. Martin Series)

---

## 책 소개

"Working Effectively with Legacy Code"는 기존 코드베이스를 안전하고 효과적으로 변경하기 위한 전략과 기법을 체계적으로 정리한 실무 지침서이다. 소프트웨어 개발 현장에서 대부분의 시간은 새로운 코드를 작성하는 것이 아니라 기존 코드를 이해하고 수정하는 데 소비된다. 이 책은 그 과정에서 마주치는 현실적인 문제들에 대한 구체적인 해결책을 제시한다.

### 레거시 코드의 정의

Michael Feathers는 레거시 코드를 다음과 같이 정의한다:

> Legacy code is simply code without tests.

이 정의에 따르면 레거시 코드란 단순히 오래된 코드가 아니라, **테스트가 없는 코드**이다. 테스트가 없으면 코드를 변경할 때 기존 동작이 보존되는지 확인할 방법이 없고, 따라서 모든 변경이 위험을 수반한다. 어제 작성한 코드라도 테스트가 없다면 레거시 코드이며, 10년 전에 작성된 코드라도 충분한 테스트가 있다면 레거시 코드가 아니다.

---

## 이 저장소의 목적

이 저장소는 "Working Effectively with Legacy Code"의 내용을 챕터별로 상세하게 정리한 학습 자료이다. 각 챕터의 핵심 개념, 기법, 예제를 책을 대체할 수 있을 정도로 충실하게 담고 있으며, 다음과 같은 용도로 활용할 수 있다:

- 책의 내용을 빠르게 복습하고 참조하는 레퍼런스
- 레거시 코드 작업 시 특정 상황에 맞는 기법을 찾는 가이드
- 팀 내 학습 및 스터디 자료

---

## 목차

### 1부: 코드 변경의 메커니즘 (The Mechanics of Change)
- [Chapter 1: 소프트웨어 변경 (Changing Software)](ch01-changing-software.md)
- [Chapter 2: 피드백 활용 (Working with Feedback)](ch02-working-with-feedback.md)
- [Chapter 3: 감지와 분리 (Sensing and Separation)](ch03-sensing-and-separation.md)
- [Chapter 4: 봉합 모델 (The Seam Model)](ch04-the-seam-model.md)
- [Chapter 5: 도구 (Tools)](ch05-tools.md)

### 2부: 소프트웨어 변경 (Changing Software)
- [Chapter 6: 고칠 것은 많고 시간은 없고 (I Don't Have Much Time and I Have to Change It)](ch06-i-dont-have-much-time.md)
- [Chapter 7: 코드 하나 바꾸는 데 왜 이리 오래 걸리지? (It Takes Forever to Make a Change)](ch07-it-takes-forever-to-make.md)
- [Chapter 8: 어떻게 기능을 추가할까? (How Do I Add a Feature?)](ch08-how-do-i-add-a-feature.md)
- [Chapter 9: 뚝딱! 테스트 하네스에 클래스 제대로 넣기 (I Can't Get This Class into a Test Harness)](ch09-i-cant-get-this-class-into-a-test-harness.md)
- [Chapter 10: 테스트 하네스에서 이 메소드를 실행할 수 없다 (I Can't Run This Method in a Test Harness)](ch10-i-cant-run-this-method-in-a-test-harness.md)
- [Chapter 11: 코드를 변경해야 한다 (I Need to Make a Change. What Methods Should I Test?)](ch11-what-methods-should-i-test.md)
- [Chapter 12: 클래스 의존 관계, 반드시 없애야 할까? (I Need to Make Many Changes in One Area)](ch12-many-changes-in-one-area.md)
- [Chapter 13: 변경해야 하는데, 어떤 테스트를 작성해야 할지 모르겠다 (I Need to Make a Change, but I Don't Know What Tests to Write)](ch13-i-dont-know-what-tests-to-write.md)
- [Chapter 14: 나를 미치게 하는 라이브러리 의존 관계 (Dependencies on Libraries Are Killing Me)](ch14-dependencies-on-libraries.md)
- [Chapter 15: 애플리케이션에 API 호출이 너무 많다 (My Application Is All API Calls)](ch15-my-application-is-all-api-calls.md)
- [Chapter 16: 변경이 가능할 만큼 코드를 이해하지 못하는 경우 (I Don't Understand the Code Well Enough to Change It)](ch16-i-dont-understand-the-code.md)
- [Chapter 17: 내 애플리케이션은 뼈대가 약하다 (My Application Has No Structure)](ch17-my-application-has-no-structure.md)
- [Chapter 18: 테스트 코드가 방해를 한다 (My Test Code Is in the Way)](ch18-my-test-code-is-in-the-way.md)
- [Chapter 19: 내 프로젝트는 객체 지향이 아니다 (My Project Is Not Object Oriented)](ch19-my-project-is-not-object-oriented.md)
- [Chapter 20: 이 클래스는 너무 비대해서 더 이상 확장하고 싶지 않다 (This Class Is Too Big and I Don't Want It to Get Any Bigger)](ch20-this-class-is-too-big.md)
- [Chapter 21: 반복되는 동일한 수정, 그만할 수는 없을까? (I'm Changing the Same Code All Over the Place)](ch21-changing-the-same-code-all-over.md)
- [Chapter 22: '괴물 메소드'를 변경해야 하는데 테스트 코드를 작성하지 못하겠다 (I Need to Change a Monster Method and I Can't Write Tests for It)](ch22-monster-method.md)
- [Chapter 23: 기존 동작을 건드리지 않았음을 어떻게 확인할 수 있을까? (How Do I Know That I'm Not Breaking Anything?)](ch23-how-do-i-know-im-not-breaking-anything.md)
- [Chapter 24: 어찌해야 할지 모르겠다. 나아질 것 같지 않아 (We Feel Overwhelmed. It Isn't Going to Get Any Better)](ch24-we-feel-overwhelmed.md)

### 3부: 의존 관계 제거 기법 (Dependency-Breaking Techniques)
- [Chapter 25: 의존 관계 제거 기법 (Dependency-Breaking Techniques)](ch25-dependency-breaking-techniques.md)

### 부록
- [Refactoring](appendix-refactoring.md)

---

## 학습 가이드

### 추천 읽기 순서

이 책은 순서대로 읽을 수도 있지만, 필요에 따라 특정 챕터를 선택적으로 참조하는 방식으로도 활용할 수 있다. 아래는 체계적인 학습을 위한 추천 순서이다.

**1단계: 기초 개념 (Part I - Chapter 1~5)**

소프트웨어 변경의 본질, 피드백 루프, 감지와 분리, 이음새(Seam) 모델, 도구 등 레거시 코드 작업의 기본 개념을 다룬다. 이후 모든 챕터의 토대가 되므로 반드시 먼저 읽는다.

- Chapter 1: 소프트웨어를 변경하는 네 가지 이유를 이해한다
- Chapter 2: 편집-컴파일-테스트 주기와 피드백의 중요성을 학습한다
- Chapter 3: 감지(Sensing)와 분리(Separation)의 개념을 익힌다
- Chapter 4: 이음새(Seam)의 개념과 유형을 파악한다
- Chapter 5: 자동화된 리팩토링 도구와 테스트 프레임워크를 알아본다

**2단계: 실전 문제 해결 (Part II - Chapter 6~24)**

실무에서 자주 마주치는 구체적인 상황별 해결 전략을 다룬다. 각 챕터의 제목이 개발자가 실제로 하는 질문이나 불만의 형태로 되어 있으므로, 현재 직면한 문제에 해당하는 챕터부터 읽어도 좋다.

- 시간이 부족할 때: Chapter 6
- 변경이 너무 오래 걸릴 때: Chapter 7
- 기능을 추가해야 할 때: Chapter 8
- 테스트를 작성하기 어려울 때: Chapter 9, 10, 13
- 어떤 메서드를 테스트해야 할지 모를 때: Chapter 11
- 한 영역에 많은 변경이 필요할 때: Chapter 12
- 코드를 이해하기 어려울 때: Chapter 16
- 클래스가 너무 클 때: Chapter 20
- 같은 변경을 여러 곳에서 해야 할 때: Chapter 21
- 거대한 메서드를 다뤄야 할 때: Chapter 22

**3단계: 기법 카탈로그 (Part III - Chapter 25 + 부록)**

Chapter 25의 의존성 깨기 기법들과 부록의 리팩토링 기법들은 레퍼런스로 활용한다. Part II를 읽으면서 참조되는 기법이 나올 때마다 해당 기법을 찾아보는 방식이 효과적이다.

---

## 핵심 개념 요약

레거시 코드를 효과적으로 다루는 핵심은 **변경의 안전망을 확보하는 것**이다. 테스트가 없는 코드에 테스트를 추가하려면 코드를 변경해야 하고, 코드를 안전하게 변경하려면 테스트가 필요하다는 역설(Legacy Code Dilemma)이 존재한다. 이 역설을 해결하기 위해 Feathers는 **이음새(Seam)**를 찾아 최소한의 변경으로 의존성을 깨고, **특성화 테스트(Characterization Test)**로 기존 동작을 포착한 후, 안전망 위에서 점진적으로 설계를 개선해 나가는 체계적인 접근법을 제시한다. 완벽한 설계를 한 번에 달성하려는 것이 아니라, 변경이 필요한 부분을 중심으로 조금씩 개선하는 것이 레거시 코드 작업의 현실적이고 효과적인 전략이다.
