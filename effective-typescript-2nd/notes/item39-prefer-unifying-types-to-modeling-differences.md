# Item 39: 차이를 모델링하기보다 타입 통합을 선호하기 (Prefer Unifying Types to Modeling Differences)

## 핵심 질문

거의 같은 타입 두 벌(snake_case/camelCase 등)을 유지하는 비용은 무엇인가? 차이를 타입 수준에서 모델링하는 것보다 나은 선택은?

타입스크립트의 타입 시스템은 타입 간 매핑의 강력한 도구를 준다(Item 15, Chapter 6). 타입 시스템으로 변환을 모델링할 수 있다는 것을 깨달으면 그렇게 하고 싶은 압도적 충동을 느낄 수 있다. 생산적인 기분도 든다 — 이 많은 타입! 이 많은 안전!

하지만 가능하다면, **두 타입의 차이를 모델링하는 것보다 나은 선택은 그 차이를 없애는 것**이다. 그러면 타입 수준 장치가 필요 없어지고, 지금 어느 버전의 타입을 다루고 있는지 추적하는 인지 부담이 사라진다.

## 1. snake_case vs camelCase — 두 벌의 Student

데이터베이스 테이블에서 파생된 인터페이스가 있다. DB는 보통 snake_case 컬럼명을 쓴다.

```typescript
interface StudentTable {
  first_name: string;
  last_name: string;
  birth_date: string;
}
```

타입스크립트 코드는 보통 camelCase를 쓰므로, 나머지 코드와 일관되게 대체 버전을 도입할 수 있다.

```typescript
interface Student {
  firstName: string;
  lastName: string;
  birthDate: string;
}
```

두 타입 사이를 변환하는 함수를 쓸 수 있고, 더 흥미롭게는 템플릿 리터럴 타입으로 그 함수를 타이핑해서 한 타입을 다른 타입에서 **생성**할 수도 있다(방법은 Item 54).

```typescript
type Student = ObjectToCamel<StudentTable>;
//   ^? type Student = {
//        firstName: string;
//        lastName: string;
//        birthDate: string;
//      }
```

놀랍다! 하지만 화려한 타입 수준 프로그래밍의 그럴듯한 사용처를 찾았다는 짜릿함이 가시고 나면, 한 버전을 기대하는 함수에 다른 버전을 넘겨서 나는 에러들에 시달리게 된다.

```typescript
async function writeStudentToDb(student: Student) {
  await writeRowToDb(db, 'students', student);
  //                                 ~~~~~~~
  // Type 'Student' is not assignable to parameter of type 'StudentTable'.
}
```

에러 메시지로는 분명치 않지만 변환 코드 호출을 잊은 것이 문제다.

```typescript
async function writeStudentToDb(student: Student) {
  await writeRowToDb(db, 'students', objectToSnake(student));  // OK
}
```

런타임 에러가 되기 전에 타입스크립트가 잡아 준 것은 고맙지만, 애초에 코드에 `Student` 타입이 **한 벌만 있어서 이 실수가 불가능**했다면 더 단순했을 것이다.

## 2. 어느 쪽으로 통합할까

- **camelCase 버전 채택**: DB가 camelCase 컬럼을 반환하도록 어댑터를 설치하고, DB에서 타입스크립트 타입을 생성하는 도구도 이 변환을 알게 해야 한다. 장점은 DB 인터페이스가 다른 모든 타입과 똑같이 보인다는 것.
- **snake_case 버전 채택**: **아무것도 할 필요가 없다.** 네이밍 컨벤션의 표면적 불일치를 받아들이는 대가로 타입의 더 깊은 일관성을 얻는다.

둘 다 가능하지만 후자가 더 단순하다.

## 3. 단서 두 가지

일반 원칙은 **작은 차이를 모델링하기보다 타입을 통합하라**는 것이지만, 단서가 있다.

1. **통합이 항상 가능한 것은 아니다.** DB와 API가 내 통제 밖이라면 두 타입이 필요할 수 있다. 그렇다면 이런 차이를 타입 시스템에서 **체계적으로** 모델링하는 것이 변환 코드의 버그를 찾는 데 도움이 된다 — 임시변통으로 타입을 만들고 동기화되길 비는 것보다 낫다.
2. **실제로 같은 것을 표현하지 않는 타입들을 통합하지 마라!** 태그된 유니온의 서로 다른 타입들을 "통합"하는 것은 역효과다 — 그것들은 분리해 두고 싶은 서로 다른 상태를 표현하는 것이니까.

## 기억해야 할 것들

- 같은 타입의 변종들을 여럿 두면 인지 부담이 생기고 변환 코드가 잔뜩 필요해진다.
- 타입의 사소한 변형을 코드에서 모델링하기보다, 변형 자체를 없애서 단일 타입으로 통합하라.
- 타입 통합에는 런타임 코드의 조정이 필요할 수 있다.
- 타입이 내 통제 밖이라면 변형을 모델링해야 할 수도 있다.
- 같은 것을 표현하지 않는 타입들은 통합하지 마라.
