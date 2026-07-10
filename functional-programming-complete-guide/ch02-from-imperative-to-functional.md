# Chapter 2: From Imperative to Functional (절차지향 코드를 함수형으로)

## 핵심 질문

중복된 for·if 코드에서 함수형 추상화는 어떻게 탄생하는가? "보조 함수에 완전히 위임한다"는 것은 무슨 뜻이며, 함수가 먼저 나오는 프로그래밍은 어떻게 다형성을 높이는가?

---

1장에서 함수형 프로그래밍의 개념을 정리했다면, 이 장에서는 그 개념이 실제 코드에서 어떻게 탄생하는지를 손으로 확인한다. 절차지향적으로 작성된 코드의 중복을 함수로 추상화해 가며 `_filter`, `_map`, `_each`, `_get`을 직접 만든다. 이 장의 코드는 ES5 시절 스타일(`function`, `var`, 유사배열 대응)을 일부 유지한다 — 이후 장에서 이터러블 프로토콜(7장)과 타입 시스템(9장) 위에서 같은 함수들이 어떻게 진화하는지 비교하기 위한 역사적 출발점이다.

> **참고**: 함수 이름 앞의 `_` 접두어는 원 노트에서 직접 구현한 함수를 내장 함수·라이브러리와 구분하기 위한 표기다. underscore/lodash의 관례를 따른 것이다.

---

## 1. 명령형 코드의 중복 — 회원 목록 문제

다음 요구사항을 명령형으로 구현해 보자.

```javascript
let users = [
  { id: 1, name: 'ID', age: 36 },
  { id: 2, name: 'BJ', age: 32 },
  { id: 3, name: 'JM', age: 32 },
  { id: 4, name: 'PJ', age: 27 },
  { id: 5, name: 'HA', age: 25 },
  { id: 6, name: 'JE', age: 26 },
  { id: 7, name: 'JI', age: 31 },
  { id: 8, name: 'MP', age: 23 }
];

// 명령형 코드
// 1. 30세 이상인 users를 거른다.
let temp_users1 = [];
for (let i = 0; i < users.length; i++) {
  if (users[i].age >= 30) {
    temp_users1.push(users[i]);
  }
}
console.log(temp_users1);

// 2. 30세 이상인 users의 names를 수집한다.
let names = [];
for (let i = 0; i < temp_users1.length; i++) {
  names.push(temp_users1[i].name);
}
console.log(names.length)
console.log(names);

// 3. 30세 미만인 users를 거른다.
let temp_users2 = [];
for (let i = 0; i < users.length; i++) {
  if (users[i].age < 30) { // ! 1, 3 코드에서 중복을 줄이려고 해도 이 부분을 없애는 게 난해하다
    temp_users2.push(users[i]);
  }
}
console.log(temp_users2);

// 4. 30세 미만인 users의 ages를 수집한다.
let ages = [];
for (let i = 0; i < temp_users2.length; i++) {
  ages.push(temp_users2[i].age);
}
console.log(ages.length);
console.log(ages);
```

1번과 3번의 `for` 문은 `users`를 돌며 특정 조건을 만족하는 값을 모아 새 배열에 담는데, `if` 문의 조건절을 제외하면 완전히 동일한 코드다. 중복을 제거하려 할 때 `30`이라는 값은 변수로 바꿀 수 있지만, 비교 연산자 `>=`와 `<`의 중복은 값으로 추출하기 난해하다. **이럴 때 함수를 사용하면 쉽게 추상화할 수 있다** — 값으로 추출할 수 없는 "로직"을 함수라는 값에 담는 것이다.

## 2. for는 filter로, if는 predicate로

```javascript
const _filter = (list, predicate) => {
  let new_list = [];

  for(let i = 0; i<list.length; i++) {
    if(predicate(list[i])) { 
      new_list.push(list[i]);
    }
  }

  return new_list;
}
```

1. `_filter` 함수는 인자로 `list`와 `predicate` 함수를 받는다.
2. 루프를 돌며 `list`의 i번째 값을 `predicate`에 넘겨준다.
3. `predicate` 함수는 `list.length`만큼 실행되며, 결과가 참일 때만 `new_list.push`를 실행한다.
	- `new_list.push`가 실행될지 여부를 `predicate` 함수에 **완전히 위임**했다.
	- `_filter` 함수는 `predicate` 함수 내부에서 어떤 일을 하는지 모른다. 오직 `predicate`의 결과에만 의존한다.
4. 마지막에 `new_list`를 리턴한다.
	- 이름에 `new_`라는 접두사를 붙였는데, 이는 함수형 프로그래밍 관점에서 상징적이다. **이전 값의 상태를 변경하지 않고 새로운 값을 만드는** 식으로 값을 다루는 것은 함수형 프로그래밍의 중요한 컨셉이다(1장의 불변성).

이 함수를 적용하면 코드가 이렇게 바뀐다.

```javascript
// 1. 30세 이상인 users를 거른다.
const over_30 = _filter(users, user => user.age >= 30);
console.log(over_30);

// 2. 30세 이상인 users의 names를 수집한다.
let names = [];
for (let i = 0; i < over_30.length; i++) {
  names.push(over_30[i].name);
}
console.log(names.length);
console.log(names);

// 3. 30세 미만인 users를 거른다.
const under_30 = _filter(users, user => user.age < 30);
console.log(under_30);

// 4. 30세 미만인 users의 ages를 수집한다.
let ages = [];
for (let i = 0; i < under_30.length; i++) {
  ages.push(under_30[i].age);
}
console.log(ages.length);
console.log(ages);
```

`_filter`를 통해 1, 3의 반복 코드가 사라졌다. 함수형 프로그래밍은 **함수를 사용하여 중복을 제거하고 추상화한다**. 추상화의 단위가 클래스·객체·메서드가 아니라 함수다.

어떤 조건일 때 걸러낼지를 익명 함수로 정의해 `_filter`의 `predicate` 자리에 넘겨 위임했는데, 이렇게 함수를 인자로 받아 원하는 시점에 적용하는 함수를 응용형 함수라 하고, 이런 방식을 응용형 프로그래밍(*Applicative Programming - 고차 함수에 보조 함수를 적용해 가며 로직을 완성하는 방식*)이라 한다. 그리고 함수를 인자로 받거나, 받은 함수를 실행하거나, 함수를 리턴하는 것이 1장에서 본 고차 함수다.

## 3. 함수형 관점으로 _filter 읽기

함수형 프로그래밍 관점에서 `_filter`를 다시 읽어 보자. `_filter` 안에는 `for`도 있고 `if`도 있지만, `_filter`는 항상 동일한 인자에 동일한 동작을 하는 한 가지 로직을 가진 함수다.

- `_filter`의 로직은 외부나 내부의 어떤 상태 변화에도 의존하지 않는다. 함수 내부에서 `new_list`의 값을 바꾸고 있지만, 그 변화에 의존하는 다른 로직이 없다.
- `for`는 `list.length`만큼 무조건 루프를 돈다. `i`의 변화에 의존해 루프를 돌지만 그 외에 `i`의 변화에 의존하는 다른 로직은 없다. `i++`는 루프를 거들 뿐이다. `list[i]`의 값을 변경하거나 `list`의 개수를 변경하는 코드도 없다.
- `new_list`는 이 함수에서 최초로 만들어졌고 외부의 어떠한 상황이나 상태와도 무관하다. `new_list`가 완성될 때까지 외부에서 어떠한 접근도 할 수 없기 때문에 `_filter`의 결과는 달라질 수 없다. 완성되고 나면 리턴해 버리고 `_filter`는 완전히 종료된다. 반환된 후에는 `new_list`와 `_filter`의 연관성도 없어진다.
- `_filter`의 `if`는 `predicate`의 결과에만 의존한다. `predicate` 역시 값을 변경하지 않고 참/거짓을 `_filter`의 `if`에게 전달하는 일만 한다.

`_filter`를 사용하는 쪽 코드에는 `for`도 `if`도 없다. 별도의 로직 없이 매우 단순하다.

> **핵심 통찰**: 내부에 명령형 코드(for·if)가 있어도, 외부 상태에 의존하지 않고 동일 입력에 동일 출력을 보장하면 그 함수는 함수형의 부품이 된다. 모든 선언형 코드는 명령형 코드 위에 쓰인다.

## 4. 수집의 추상화 — _map

앞의 2, 4번 코드는 특정 값을 추출하여 같은 크기의 새 배열을 만들고, 원 데이터와 1:1로 매핑되는 다른 값을 담고 있다. 이 코드를 그대로 활용해 `_map`을 만들면 다음과 같다.

```javascript
const _map = (list, mapper) => {
  let new_list = [];

  for(let i = 0; i < list.length; i++) {
    new_list.push(mapper(list[i]));
  }

  return new_list;
}
```

기존의 중복 코드와 거의 동일하고, 새 리스트에 **무엇을 넣을지**를 `mapper`(또는 `iteratee`) 함수에 위임했다. `_map` 함수 내부에서는 데이터형이 어떻게 생겼는지 보이지 않는다. 이것은 함수형 프로그래밍의 중요한 특징 중 하나로, **관심사가 완전히 분리**된다.

```javascript
// 1. 30세 이상인 users를 거른다.
const over_30 = _filter(users, user => user.age >= 30);
console.log(over_30);

// 2. 30세 이상인 users의 names를 수집한다.
let over_30_names = _map(over_30, user => user.name);
console.log(over_30_names.length);
console.log(over_30_names);

// 3. 30세 미만인 users를 거른다.
const under_30 = _filter(users, user => user.age < 30);
console.log(under_30);

// 4. 30세 미만인 users의 ages를 수집한다.
let under_30_ages = _map(under_30, user => user.age);
console.log(under_30_ages.length);
console.log(under_30_ages);
```

사용하는 쪽 코드에서 `for`도 `if`도 완전히 사라졌다.

## 5. 함수 결과를 바로 인자로 — 변수 할당 줄이기

함수의 리턴 값을 바로 다른 함수의 인자로 사용하면 변수 할당을 줄일 수 있다.

```javascript
// 1. 2. 30세 이상인 users의 names를 수집한다.
let over_30_names = _map(
	_filter(users, user => user.age >= 30),
	user => user.name
);
console.log(over_30_names.length);
console.log(over_30_names);

// 3. 4. 30세 미만인 users의 ages를 수집한다.
let under_30_ages = _map(
	_filter(users, user => user.age < 30),
	user => user.age
);
console.log(under_30_ages.length);
console.log(under_30_ages);
```

작은 함수(`log_length`)를 하나 더 만들면 변수 할당을 모두 없앨 수 있다. 여기까지의 전체 코드는 다음과 같다.

```javascript
const _filter = (list, predicate) => {
	let new_list = [];
	
	for(let i = 0; i<list.length; i++) {
	  if(predicate(list[i])) { 
	    new_list.push(list[i]);
	  }
	}

	return new_list;
}

const _map = (list, mapper) => {
  let new_list = [];

  for(let i = 0; i < list.length; i++) {
    new_list.push(mapper(list[i]));
  }

  return new_list;
}

const log_length = value => {
	console.log(value.length)
	return value;
}

// 1. 2. 30세 이상인 users의 names를 수집한다.
console.log(log_length(
	_map(
		_filter(users, user => user.age >= 30), 
		user => user.name
	),
));

// 3. 4. 30세 미만인 users의 ages를 수집한다.
console.log(log_length(
	_map(
		_filter(users, user => user.age < 30), 
		user => user.age
	),
));
```

## 6. 함수를 리턴하는 함수의 실용성 — _get

1장의 `addMaker`와 비슷한 패턴(함수를 만들어 리턴하는 함수)이 실제로도 많이 쓰인다. 해당 키의 값을 꺼내주는 `_get` 함수를 만들면 위 코드를 더 줄일 수 있다.

```javascript
const _get = key => {
	return obj => {
		return obj[key]
	}
}
```

```javascript
// 1. 2. 30세 이상인 users의 names를 수집한다.
console.log(log_length(
	_map(
		_filter(users, user => user.age >= 30), 
		_get('name')
	),
));

// 3. 4. 30세 미만인 users의 ages를 수집한다.
console.log(log_length(
	_map(
		_filter(users, user => user.age < 30), 
		_get('age')
	),
));
```

`_map`이 사용할 `mapper` 함수를 `_get`이 리턴한 함수로 대체함으로써 익명 함수 선언이 사라졌다.

## 7. _each로 더 깊게 모듈화

`_filter`와 `_map`의 내부를 보면 `for` 루프가 또 중복된다. 반복문을 돌면서 안에서 하는 일을 위임하는 `_each`를 만들어 한 단계 더 모듈화할 수 있다.

**모듈화 전:**

```javascript
const _filter = (list, predicate) => {
	let new_list = [];
	
	for(let i = 0; i<list.length; i++) {
	  if(predicate(list[i])) { 
	    new_list.push(list[i]);
	  }
	}

	return new_list;
}

const _map = (list, mapper) => {
  let new_list = [];

  for(let i = 0; i < list.length; i++) {
    new_list.push(mapper(list[i]));
  }

  return new_list;
}
```

**모듈화 후:**

```javascript
const _each = (list, iteratee) => {
	for(let i = 0; i < list.length; i++) {
		iteratee(list[i]);
	}
	return list;
}

const _filter = (list, predicate) => {
	let new_list = [];

	_each(list, value => {
		if(predicate(value)) {
			new_list.push(value)
		}
	});

	return new_list;
}

const _map = (list, mapper) => {
  let new_list = [];

  _each(list, value => {
		new_list.push(mapper(value));
	})

  return new_list;
}
```

## 8. 다형성 높이기

### 8.1 외부 다형성과 내부 다형성

자바스크립트 Array 객체에는 이미 `map`, `filter` 함수가 있다. 하지만 객체 안에 내장된 함수는 **메서드**이고, 순수 함수가 아니라 객체의 상태에 따라 결과가 달라진다. 메서드는 객체지향 프로그래밍의 도구다. 메서드는 해당 클래스(자바스크립트에서는 정확히 말하면 프로토타입)에 정의돼 있기 때문에 해당 클래스의 인스턴스에서만 사용할 수 있다.

자바스크립트에는 Array가 아닌데 Array처럼 여겨지는 유사 배열 객체(*Array-like Object - length와 인덱스를 가졌지만 Array가 아닌 객체. NodeList, arguments 등*)가 많다. 함수형 프로그래밍을 사용하면 함수에 맞게 데이터만 맞추면 데이터 타입에 영향받지 않고 사용할 수 있다.

데이터가 먼저 나오는 프로그래밍보다 함수가 먼저 나오는 프로그래밍이 다형성에 덜 구애받는다. 객체지향은 해당 객체가 생겨야 기능을 수행할 수 있지만, 함수 지향은 함수가 먼저 존재하기 때문에 데이터가 생기기 전에도 평가 시점이 유연하고 높은 조합성을 갖는다.

1. **외부 다형성**: 유사 배열이나 함수 내부의 기본 객체인 `arguments` 같은 Array 형태의 객체가 들어와도 모두 실행 가능하다. 특정 객체에만 적용 가능한 메서드가 아니라 함수이기 때문에, 인자의 형태만 맞으면 모두 실행할 수 있다.
2. **내부 다형성**: 요소가 어떤 값이든 수행할 수 있게 하는 것은 두 번째 인자인 보조 함수(`predicate`, `mapper`, `iteratee`)의 역할이다. 내부 값에 대한 다형성은 보조 함수가 책임진다. 데이터가 숫자면 숫자에 맞는 보조 함수를, NodeList가 들어오면 그에 맞는 보조 함수를 작성하면 된다. 개발자가 넘기는 값을 이해하고 보조 함수를 정하므로 데이터 형으로부터 자유롭다.

객체지향의 일반적인 다형성은 다형성 동작을 갖는 개체가 있고 동작이 상속을 통해 개체 내에서 구현되는 방식인데, 이 경우 다형성을 구현하는 코드 전체가 클래스 내부에 긴밀하게 결합된다. 기본 클래스의 요구사항이 변경되면 모든 종속 클래스를 변경해야 하고, 기본 클래스에 함수가 추가·변경되면 상속받은 모든 클래스를 확인해야 한다. 전략 패턴(*Strategy Pattern - 다형성의 실제 구현을 클래스 외부에 두고 주입하는 객체지향 패턴*)은 이를 개선해 구현을 외부에 배치하고 주입한다. 함수형(선언형)에서는 객체와 함수를 분리해 타입만 맞으면 실행되게 하는 것으로 **외부 다형성**을 맞추고, `predicate`·`mapper` 같은 보조 함수로 **내부 다형성**을 맞춘다.

### 8.2 null에도 무너지지 않기 — _each 보강과 _keys

`_each`의 리스트 인자에 `null`을 넣으면 내부에서 `length`를 참조할 때 에러가 난다.

```javascript
_each(null, console.log) // error
```

앞서 만든 `_get`은 값이 없으면 `undefined`를 반환하므로, 어떻게 보면 `null` 체크를 하고 있는 셈이다. `_each` 내부의 `list.length` 대신 `_get('length')`를 쓰면 `undefined`가 들어가 에러를 피할 수 있다.

```javascript
let _length = _get('length')
let _each = (list, iteratee) => {
	for(let i = 0, len = _length(list); i < len; i++) {
		iteratee(list[i]);
	}
}
```

이렇게 수정하면 `_each`로 만든 `_map`, `_filter`도 에러를 피해 간다.

```javascript
console.log(
  _filter(null, v => v), // []
  _map(null, v => v), // []
)
```

**함수형 프로그래밍에서는 에러가 났을 때 흘려보내는 전략을 취한다.** 함수들을 연속 실행할 때 언제 어디서 잘못된 값이 들어와도 에러 없이 흘려보낼 수 있으며, underscore·lodash 같은 라이브러리도 이 전략을 채택하고 있다. 이런 식으로 로직이 흘러가면 데이터 형을 체크하거나 특정 작업을 try-catch로 묶어주는 코드가 줄어든다.

`Object.keys`도 같은 문제가 있다. 객체를 받아 키 값을 리턴하지만 `null`이 들어오면 에러가 발생한다.

```javascript
console.log(Object.keys({ name: 'ID', age: 33 }));
console.log(Object.keys([1, 2, 3, 4]));
console.log(Object.keys(10));
// console.log(Object.keys(null)); // 에러
```

`_keys` 함수를 만들어 해결한다.

```javascript
function _is_object(obj) {
  return typeof obj == 'object' && !!obj;
}
function _keys(obj) {
  return _is_object(obj) ? Object.keys(obj) : [];
}
```

```javascript
console.log(_keys({ name: 'ID', age: 33 }));
console.log(_keys([1, 2, 3, 4]));
console.log(_keys(10));
console.log(_keys(null));
```

이처럼 함수형 프로그래밍에서는 어떤 형태의 값이 들어오든 그럴싸한 값을 리턴하는 식으로 다형성을 높여, 연속적인 함수 실행에 무리가 없도록 한다. `_keys`를 이용하면 `_each`가 키가 있는 일반 객체까지 순회하도록 다형성을 높일 수 있다.

```javascript
let _each = (list, iteratee) => {
	let keys = _keys(list) // keys 자체는 null 값이 와도 빈 배열을 뱉도록 준비돼 있다. 무조건 올바른 배열이 리턴되므로 length를 사용할 수 있다.
	for(let i = 0, len = keys.length; i < len; i++) {
		iteratee(list[keys[i]]);
	}
}
```

```javascript
_each({
  13: 'AB',
  19: 'CD',
  29: 'YD',
}, name => console.log(name))
// 보강 전에는 length가 없어 아무 일도 일어나지 않던 객체도 이제 순회된다.
```

## 9. 명령형 문장 → 리스트 프로세싱 대응표

이 장에서 만든 함수들은 명령형 문장을 선언형 함수로 대체하는 작업의 시작이었다. 원 노트가 정리한 대응 관계는 다음과 같다.

| 명령형 문장 | 리스트 프로세싱 함수 |
|---|---|
| `if` | `filter` |
| 변수 할당 | `map` |
| `break` | `take` |
| 축약·합산 | `reduce` |
| `while` | `range` |
| 효과(effect) | `each` |
| `reduce` + 복잡한 함수 | `map` + `filter` + `reduce` + 간단한 함수 |

이 대응표의 완성형 — `break`를 `take`로 바꾸고 무한 수열(`range`)까지 다루는 이야기 — 은 지연 평가(8장)와 하스켈·다언어 리스트 프로세싱(11장)에서 이어진다.

## 요약

- 값으로 추출할 수 없는 로직의 중복(비교 연산자 등)은 **함수를 값으로 넘겨** 추상화한다. `_filter`는 걸러낼 조건을, `_map`은 수집할 값을 보조 함수에 완전히 위임한다.
- 함수형 프로그래밍의 추상화 단위는 클래스가 아니라 **함수**이며, 고차 함수 + 보조 함수 조합을 응용형 프로그래밍이라 한다.
- 내부에 for·if가 있어도 외부 상태에 의존하지 않으면 함수형의 부품이 된다 — **모든 선언형 코드는 명령형 코드 위에 쓰인다.**
- `_each`로 순회를 모듈화하고, `_get`·`_keys`로 `null`에도 무너지지 않게 만들면 **에러를 흘려보내는** 연속 실행이 가능해진다.
- 함수가 먼저 나오는 프로그래밍은 **외부 다형성**(타입만 맞으면 실행)과 **내부 다형성**(보조 함수가 책임)을 분리해 다형성을 높인다.
- `if→filter, 변수 할당→map, break→take, 합산→reduce` — 명령형 문장은 리스트 프로세싱 함수로 하나씩 대체된다.

## 다른 챕터와의 관계

- **1장**: "함수를 값으로 다룬다"(일급 함수)는 개념이 이 장의 `predicate`/`mapper` 위임으로 구체화됐다.
- **3장**: `_get`처럼 함수를 리턴하는 패턴이 커링으로 일반화되고, 중첩 호출(`_map(_filter(...))`)의 가독성 문제를 `_pipe`/`_go`가 해결한다.
- **4장**: 이 장의 `_map`/`_filter`/`_each`/`_keys`를 재료로 컬렉션 중심 함수 세트를 만든다.
- **7장**: 같은 함수들을 인덱스(`length`) 기반이 아닌 **이터러블 프로토콜** 기반으로 다시 구현한다 — 유사 배열 대응(`_keys`)이 프로토콜 수준에서 해결된다.
- **11장·16장**: 9절의 대응표가 다언어 리스트 프로세싱과 실전 패턴 9종으로 확장된다.
