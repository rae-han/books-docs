# Item 67: 공개 API에 등장하는 모든 타입 export하기 (Export All Types That Appear in Public APIs)

## 핵심 질문

공개 함수의 시그니처에 쓰인 타입을 export하지 않으면 정말 감춰지는가?

타입스크립트를 오래 쓰다 보면 서드파티 라이브러리의 타입이나 인터페이스를 쓰고 싶은데 export되어 있지 않은 경우를 만나게 된다. 사용자에게 성가신 일일 뿐이다 - **공개 API의 일부인 타입은 명시적으로 export하지 않아도 사실상 export된 것**이기 때문이다.

비공개, 비export 타입을 만들려 했다고 하자.

```typescript
interface SecretName {
  first: string;
  last: string;
}
interface SecretSanta {
  name: SecretName;
  gift: string;
}

export function getGift(name: SecretName, gift: string): SecretSanta {
  // ...
}
```

이 모듈의 사용자는 `SecretName`이나 `SecretSanta`를 직접 import할 수 없고 `getGift`만 쓸 수 있다. 하지만 이것은 단단한 장벽이 아니라 성가심일 뿐이다 - 그 타입들이 export된 함수 시그니처에 등장하므로 **추출할 수 있다.** 한 방법은 `Parameters`와 `ReturnType` 제네릭이다.

```typescript
type MySanta = ReturnType<typeof getGift>;
//   ^? type MySanta = SecretSanta
type MyName = Parameters<typeof getGift>[0];
//   ^? type MyName = SecretName
```

export하지 않은 목적이 유연성 유지였다면, 게임은 이미 끝났다 - **공개 API에 넣는 순간 그 타입에 커밋한 것이다.** 사용자를 위해 그냥 export하라.

## 기억해야 할 것들

- 공개 메서드에 어떤 형태로든 등장하는 타입은 export하라. 사용자가 어차피 추출할 수 있으니, 쉽게 쓰도록 해 주는 편이 낫다.
