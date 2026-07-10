# Chapter 4: Collection-Centric Programming (컬렉션 중심 프로그래밍)

## 핵심 질문

컬렉션을 다루는 함수들은 왜 수집·거르기·찾기·축약의 4가지 유형으로 정리되는가? 가장 추상화된 함수(map·filter·find·reduce)로부터 특화 함수들은 어떻게 파생되며, `_identity`처럼 사소해 보이는 함수는 왜 강력한가?

---

컬렉션이란 목록성 데이터를 처리하는 자료구조를 통칭한다. 컬렉션을 잘 다루는 함수 세트를 구성하고 그 함수들을 이용해 문제를 풀어 나가는 것을 **컬렉션 중심 프로그래밍**이라 하며, 이는 함수형 프로그래밍에서 더 빛을 발한다. 이 장에서는 2~3장에서 만든 `_map`·`_filter`·`_each`·`_reduce`·`_curryr`를 재료로 실무에서 자주 쓰는 특화 함수들을 파생시킨다.

이 장의 예제에 사용할 데이터는 다음과 같다.

```javascript
const users = [
  { id: 10, name: 'ID', age: 36 },
  { id: 20, name: 'BJ', age: 32 },
  { id: 30, name: 'JM', age: 32 },
  { id: 40, name: 'PJ', age: 27 },
  { id: 50, name: 'HA', age: 25 },
  { id: 60, name: 'JE', age: 26 },
  { id: 70, name: 'JI', age: 31 },
  { id: 80, name: 'MP', age: 23 },
  { id: 90, name: 'FP', age: 13 }
];
```

---

## 1. 컬렉션 중심 프로그래밍의 4유형

컬렉션 중심 프로그래밍은 크게 4가지 유형으로 나뉜다.

1. **수집하기(map)**: map, values, pluck ...
2. **거르기(filter)**: filter, reject, compact, without ...
3. **찾기(find)**: find, some, every ...
4. **접기·축약(reduce)**: reduce, min, max, group_by, count_by ...

각 유형의 맨 앞 함수 4개(map·filter·find·reduce)가 가장 추상화된 함수이고, 이를 이용해 뒤의 특화 함수들을 만들 수 있다. 이 중 수집하기(map)와 거르기(filter)는 reduce에 뿌리를 두고 있다.

> **핵심 통찰**: 특화 함수는 "추상 함수 + 보조 함수"의 조합으로 파생된다. 큰 클래스 하나를 만드는 것보다, 다양하고 작은 함수를 만들어 합성·조합하는 것이 함수형 프로그래밍답다.

## 2. 수집하기 — map 계열

### 2.1 _values와 _identity

`_values`는 컬렉션에 들어 있는 값을 꺼내는 함수다. 키가 0, 1, ...로 시작하는 배열에 쓰면 큰 의미가 없고, 객체에서 사용할 때 빛을 발한다.

```javascript
function _values(data) {
  return _map(data, function(val) { 
    return val; 
  });
}
```

`_values`는 `_identity`와의 합성으로 리팩터링할 수 있다. `_identity`는 받은 값을 그대로 리턴하는 함수인데, 위 `_map`의 보조 함수와 하는 일이 동일하므로 대체할 수 있다.

```javascript
function _identity(val) {
  return val;
}
```

```javascript
let value = 10;
console.log(_identity(value)); // 10
```

그대로 리턴만 하는 함수를 왜 만드는지는 뒤(3.2절, 4.4절)에서 드러난다. 적용하면 다음과 같다.

```javascript
function _values(data) {
  return _map(data, _identity);
}
```

`_map`을 `_curryr`한 형태로 바꿔 뒀다면, 보조 함수만 받았을 때 데이터를 기다리는 함수가 리턴된다. 평가 순서를 뒤집어 다시 만든 `_values`는 한 줄이다.

```javascript
let _values = _map(_identity);
```

함수와 함수의 상호작용만으로 구현이 완성된다.

```javascript
console.log(_values(users));
// [
//   { id: 10, name: 'ID', age: 36 },
//   { id: 20, name: 'BJ', age: 32 },
//   { id: 30, name: 'JM', age: 32 },
//   { id: 40, name: 'PJ', age: 27 },
//   { id: 50, name: 'HA', age: 25 },
//   { id: 60, name: 'JE', age: 26 },
//   { id: 70, name: 'JI', age: 31 },
//   { id: 80, name: 'MP', age: 23 },
//   { id: 90, name: 'FP', age: 13 }
// ]
```

### 2.2 _pluck

`_pluck`은 컬렉션 내부 개체의 특정 키에 해당하는 값을 수집하는 함수다.

```javascript
function _pluck(data, key) {
  return _map(data, function(obj) {
    return obj[key];
  })
};
```

```javascript
console.log(_pluck(users, 'age')); // [36, 32, 32, 27, 25, 26, 31, 23, 13]
```

2장에서 만든 `_get`을 사용하면 더 간결해진다.

```javascript
function _pluck(data, key) {
  return _map(data, _get(key))
};
```

## 3. 거르기 — filter 계열

### 3.1 _reject와 _negate

`_reject`는 `_filter`를 반대로 동작시킨 것이다. 논리 회로의 NOT 게이트를 적용한 것과 같다.

```javascript
function _reject(data, predi) {
  return _filter(data, function(val) {
    return !predi(val);
  })
}
```

`_filter`의 보조 함수 조건을 직접 뒤집어도 같은 동작을 하지만, `_reject`를 사용하면 보조 함수(`predi`)는 그대로 둔 채 앞의 고차 함수 이름만 바꿔(`_filter` → `_reject`) 의도를 드러낼 수 있어 **더 선언적**이다.

`_filter`를 `_identity`로 간결하게 만들었던 것처럼, `_reject`는 `_negate`로 간결하게 만들 수 있다.

```javascript
function _negate(func) {
  return function(val) {
    return !func(val);
  }
}
```

`_reject`가 `_filter`에 넘기던 보조 함수(1)와 `_negate`가 반환하는 함수(2)의 모양이 같다.

```javascript
// 1
function(val) {
  return !predi(val);
}

// 2
function(val) {
  return !func(val);
}
```

최종적으로 `_reject`는 함수 조합만 남는다.

```javascript
function _reject(data, predi) {
  return _filter(data, _negate(predi));
}
```

```javascript
var _reject = _curryr(_reject); // 파이프라인에서 쓰기 위한 커링
```

### 3.2 _compact

`_compact`는 값 중 `true`로 평가되는 값만 남기는 함수다.

```javascript
var _compact = _filter(_identity);
```

매우 간단하다. `_identity` 자체가 값을 그대로 반환하므로, 그 값의 truthy/falsy가 그대로 필터 조건이 된다.

```javascript
console.log(_compact([0, 1, 2, null, false, {}])) // [ 1, 2, {} ]
```

값을 리턴하기만 하는 `_identity`는 별볼일 없어 보이지만 이렇게 간결하고 강력하게 쓰인다.

## 4. 찾기 — find 계열

### 4.1 _find

`_find`는 컬렉션에서 처음으로 조건에 일치하는 값을 리턴하는 함수다. `_filter`가 모든 값을 검사하며 걸러낸다면, `_find`는 값을 하나 찾으면 바로 리턴한다. **원하는 값을 얻으면 더 이상 로직을 실행하지 않는 최적화의 키워드**가 될 수 있다.

```javascript
function _find(list, predi) {
  var keys = _keys(list);

  for(var i = 0, len = keys.length; i < len; i++) {
    if(predi(list[keys[i]])) return list[keys[i]];
    // 일치하는 조건을 만나면 리턴, 아니라면 undefined
  }
}
```

중복되는 접근을 변수로 정리하면 다음과 같다.

```javascript
function _find(list, predi) {
  var keys = _keys(list);

  for(var i = 0, len = keys.length; i < len; i++) {
    var val = list[keys[i]];
    if(predi(val)) return val;
  }
}
```

```javascript
var _find = _curryr(_find);
```

```javascript
console.log(_find(users, function(user) {
  return user.age < 30;
})); // { id: 40, name: 'PJ', age: 27 }

console.log(_find(users, function(user) {
  return user.id === 30;
})); // { id: 30, name: 'JM', age: 32 }
```

### 4.2 _find_index

`_find`와 비슷하지만, 일치하는 조건을 만나면 값이 아닌 인덱스를, 만나지 못하면 `-1`을 반환한다.

```javascript
function _find_index(list, predi) {
  var keys = _keys(list);

  for(var i = 0, len = keys.length; i < len; i++) {
    if(predi(list[keys[i]])) return i;
  }
  return -1;
}
```

```javascript
var _find_index = _curryr(_find_index)
```

```javascript
console.log(_find_index(users, function(user) {
  return user.age < 30;
})); // 3
console.log(_find_index(users, function(user) {
  return user.id === 30;
})); // 2
console.log(_find_index(users, function(user) {
  return user.id === 35;
})); // -1
```

### 4.3 계속 curryr 형태로 바꾸는 이유

아래 두 코드는 완전히 같게 동작하지만, curryr 형태로 파이프라인에 태운 쪽이 훨씬 읽기 쉽다.

```javascript
console.log(
  _get(_find(users, function(user) {
    return user.id === 50;  
  }), 'name')
)

// functional
_go(
  users,
  _find(function(user) { // 사용 전에 반드시 curryr 형태로 만들어줘야 한다.
    return user.id === 50
  }),
  _get('name'),
  console.log,
)
```

### 4.4 _some과 _every

`_some`은 조건을 만족하는 값이 하나라도 있는지, `_every`는 모든 값이 조건을 만족하는지 확인해 `boolean`을 리턴한다. `_find_index`와 `_negate`의 조합만으로 만들 수 있다.

```javascript
function _some(data, predi) {
  return _find_index(data, predi) !== -1;
} 

function _every(data, predi) {
  return _find_index(data, _negate(predi)) === -1; 
}
```

`_every`가 흥미롭다 — "조건에 어긋나는 값(negate)이 하나도 발견되지 않으면(`=== -1`) 전부 만족"이라는 논리다.

```javascript
var testcase = [1, 2, 4, 6, 8, 9, 11, 17, 19];

console.log(_some(testcase, function(val) {
  return val === 11;
})) // true

console.log(_every(testcase, function(val) {
  return val < 20;
})) // true
```

보조 함수가 없을 때도 대비할 수 있다. 평가할 값 자체가 truthy/falsy를 갖고 있기 때문이다. 여기서도 `_identity`가 실용적으로 쓰인다.

```javascript
function _some(data, predi) {
  return _find_index(data, predi || _identity) !== -1;
} 
function _every(data, predi) {
  return _find_index(data, _negate(predi || _identity)) === -1; 
}
```

```javascript
var testcase = [1, 0, false, null, undefined];

console.log(_some(testcase, _identity)) // true (1이 truthy)

console.log(_some([0, false, null, undefined], _identity)) // false

console.log(_every([1, true, {}, []])) // true (모두 truthy)
```

### 4.5 응용

```javascript
console.log(
  _some(users, function(user) {
    return user.age < 20;
  })
) // true
console.log(
  _every(users, function(user) {
    return user.age > 10;
  })
) // true
```

`_some`·`_every`·`_find`는 모두 고차 함수로서 보조 함수를 받기 때문에, 단순히 "모두 참인가? 참이 있는가?"를 반환하는 함수보다 많은 일을 할 수 있다. 일반적인 `indexOf`가 완전히 같은 값인지 레퍼런스 비교로만 인덱스를 찾는다면, `_find_index`는 보조 함수를 받아 **그 조건을 만족하는** 값이 있는지, 있다면 몇 번째인지 찾는다.

즉, 앞에 있는 고차 함수를 고른 후 보조 함수를 래핑하면서 로직을 고르거나 조합해 나가는 것이다. "모두 그런지, 하나라도 그런지"를 **고차 함수로 선택**하고, "그러하다는 것이 무엇인지"를 **보조 함수로 선택**하는 것이 함수형 프로그래밍이다.

## 5. 접기·축약하기 — reduce 계열

`_reduce`는 함수형 프로그래밍에서 굉장히 상징적인 함수로, Array나 순회 가능한 객체의 값들로 다른 "접혀진 값"을 만들 때 사용한다. 집계, 병합(merge) 등 전혀 다른 값을 만들기 위해 쓰기도 한다.

순차적인 for 문의 관점보다 함수형 측면에서 바라보는 것이 좋다. 순수 함수로서 **평가 순서와 상관없이** 접거나 축약해 나가는 도구로 이해해야 한다.

### 5.1 _min과 _max

```javascript
var testcase = [-10, -1, 0, 2, 3, 4, 5];

function _min(data) {
  return _reduce(data, function(a, b) {
    return a > b ? b : a;
  });
}
console.log(_min(testcase)); // -10

function _max(data) {
  return _reduce(data, function(a, b) {
    return a > b ? a : b;
  });
}
console.log(_max(testcase)); // 5
```

함수형 프로그래밍에서는 평가 순서와 관계없이 결과를 만드는 식으로 사고하는 것이 좋다. 테스트 케이스가 순서대로 들어오지 않는다고 생각하고, "a, b가 들어왔을 때 무슨 일을 할까?"에 중점을 둔다. 이는 `_reduce` 자체를 for로 생각하며 프로그래밍하는 것을 지양해야 한다는 말과 같다.

### 5.2 _min_by와 _max_by

`_min_by`·`_max_by`는 **어떤 조건으로 비교할 것인가**에 해당하는 보조 함수를 추가로 받는다. `_min`·`_max`는 값을 직접 비교해 다형성이 낮지만, `_by` 함수들은 보조 함수 덕분에 가능성이 열려 있어 더 많은 일을 할 수 있다.

```javascript
function _min_by(data, iter) {
  return _reduce(data, function(a, b) {
    return iter(a) > iter(b) ? b : a;
  })
};

function _max_by(data, iter) {
  return _reduce(data, function(a, b) {
    return iter(a) > iter(b) ? a : b;
  })
};
```

절대값 비교도 보조 함수로 쉽게 해결된다.

```javascript
var testcase = [-10, -1, 0, 2, 3, 4, 5];

console.log(_min_by(testcase, Math.abs)); // 0
console.log(_max_by(testcase, Math.abs)); // -10
```

여기서 생각해 볼 점: 만약 `_map`으로 데이터를 먼저 변환한 뒤 비교하면 `_max_by`의 결과가 `-10`이 아닌 `10`이 된다 — 원본 값을 잃기 때문이다. `_by` 계열처럼 **비교 시점에만 변환을 적용**하는 특화 함수 조각을 만들면 더 정교하게 프로그래밍할 수 있고 다형성과 확장성이 높아진다.

```javascript
var _min_by = _curryr(_min_by);
var _max_by = _curryr(_max_by);
```

실무적인 조합 예시를 보자.

```javascript
// 아래 3개는 모두 같은 코드다. 화살표 함수와 _get으로 각각 리팩터링했다.
_go (
  users,
  _filter(user => user.age >= 30),
  _min_by(function(user) {
    return user.age
  }),
  console.log,
) // { id: 70, name: 'JI', age: 31 }

_go (
  users,
  _filter(user => user.age >= 30),
  _min_by(user => user.age),
  console.log,
) // { id: 70, name: 'JI', age: 31 }

_go (
  users,
  _filter(user => user.age >= 30),
  _min_by(_get('age')),
  console.log,
) // { id: 70, name: 'JI', age: 31 }

_go (
  users,
  _reject(user => user.age >= 30),
  _max_by(_get('age')),
  _get('name'),
  console.log,
) // PJ
```

### 5.3 _group_by와 _push

`_group_by`는 특정 값을 기준으로 그룹화하는, 접기에 특화된 함수다.

```javascript
function _group_by(data, iter) {
  return _reduce(data, function(grouped, val) {
    var key = iter(val);
    (grouped[key] = grouped[key] || []).push(val);
    return grouped;
  }, {});
};
```

```javascript
var _group_by = _curryr(_group_by);
```

```javascript
_go(
  users,
  _group_by(function(user) { return user.age }),
  console.log,
)
// {
//   '13': [ { id: 90, name: 'FP', age: 13 } ],
//   '23': [ { id: 80, name: 'MP', age: 23 } ],
//   '25': [ { id: 50, name: 'HA', age: 25 } ],
//   '26': [ { id: 60, name: 'JE', age: 26 } ],
//   '27': [ { id: 40, name: 'PJ', age: 27 } ],
//   '31': [ { id: 70, name: 'JI', age: 31 } ],
//   '32': [ { id: 20, name: 'BJ', age: 32 }, { id: 30, name: 'JM', age: 32 } ],
//   '36': [ { id: 10, name: 'ID', age: 36 } ]
// }
```

`_group_by` 안의 reduce 보조 함수 내부 로직은 그 자체로 의미가 있으므로 모듈화하면 좋다. 객체와 키, 값을 넣으면 키로 찾아진 배열이 있으면 거기에 값을 넣고, 없으면 빈 배열을 만들어 넣는다 — 공간이 없으면 공간을 만들어 넣어 주는, 안정성을 높이는 함수다. 참고로 `_push`는 값을 직접 변경하는 함수다.

```javascript
function _push(obj, key, val) { 
  (obj[key] = obj[key] || []).push(val);
  return obj;
}
```

`_push`를 쓰면 `_group_by`가 더 간결해진다. 함수를 쪼개면 값을 두 번 쓰기 위한 변수 선언(`var key`)이 줄어드는 경향이 있다.

```javascript
function _group_by(data, iter) {
  return _reduce(data, function(grouped, val) {
    return _push(grouped, iter(val), val)
  }, {});
};
```

보조 함수에 "어떤 값을 기준으로 그룹핑할 것인가"가 위임되므로, 변형된 키를 만들어 연령대별 그룹핑도 가능하다.

```javascript
_go(
  users,
  _group_by(function(user) { return user.age - user.age % 10 }), // 몇 대인지 변형된 키를 만들어서
  console.log,
)
// {
//   '10': [ { id: 90, name: 'FP', age: 13 } ],
//   '20': [
//     { id: 40, name: 'PJ', age: 27 },
//     { id: 50, name: 'HA', age: 25 },
//     { id: 60, name: 'JE', age: 26 },
//     { id: 80, name: 'MP', age: 23 }
//   ],
//   '30': [
//     { id: 10, name: 'ID', age: 36 },
//     { id: 20, name: 'BJ', age: 32 },
//     { id: 30, name: 'JM', age: 32 },
//     { id: 70, name: 'JI', age: 31 }
//   ]
// }
```

작은 로직도 함수의 연속 실행으로 만들어 갈 수 있다. `_head` 같은 함수를 더해 이름 첫 글자 그룹핑도 함수 조합으로 표현된다(필수는 아니다).

```javascript
var _head = function(list) {
  return list[0]
};
```

```javascript
// 변형 전
_go(
  users,
  _group_by(function(user) { return user.name[0] }),
  console.log,
)

// 변형 후
_go(
  users,
  _group_by(_pipe(_get('name'), _head)),
  console.log,
)
```

### 5.4 _count_by와 _inc

`_count_by`는 `_group_by`와 비슷하지만, 보조 함수로 만들어낸 키가 몇 개인지 세는 함수다. 값을 병합할 필요가 없으므로 더 간결하다.

```javascript
function _count_by(data, iter) {
  return _reduce(data, function(count, val) {
    var key = iter(val);
    count[key] ? count[key]++ : count[key] = 1;
    return count;
  }, {})
}
```

```javascript
var _count_by = _curryr(_count_by);
```

`_group_by`의 `_push`처럼 `_inc`를 만들어 간결화한다.

```javascript
function _inc(count, key) {
  count[key] ? count[key]++ : count[key] = 1;
  return count;
}
```

```javascript
function _count_by(data, iter) {
  return _reduce(data, function(count, val) {
    return _inc(count, iter(val))
  }, {})
}
```

### 5.5 _each·_map 확장과 _pairs

`_each`와 `_map`이 value와 함께 key(또는 index)도 보조 함수에 넘기도록 확장한다.

```javascript
let _each = (list, iteratee) => {
	let keys = _keys(list)
	for(let i = 0, len = keys.length; i < len; i++) {
		iteratee(list[keys[i]], keys[i]); // 수정한 부분: key 혹은 index 값도 넘겨준다.
	}
}
```

```javascript
let _map = (list, mapper) => {
  let new_list = [];

  _each(list, (value, key) => {
		new_list.push(mapper(value, key)); // 수정한 부분: key 또는 index 값도 넘겨준다.
	})

  return new_list;
}
```

이를 응용하면 객체의 key-value 쌍을 배열로 만드는 `_pairs`도 구현할 수 있다.

```javascript
var _pairs = _map((val, key) => [key, val]);
```

```javascript
console.log(_pairs(users[0])) // [ [ 'id', 10 ], [ 'name', 'ID' ], [ 'age', 36 ] ]
```

## 6. 조합으로 완성하기 — 화면 만들기

지금까지 만든 함수들을 응용하면, 들어온 데이터 중 원하는 데이터를 필터링해 원하는 DOM으로 만든 후 화면에 보여주는 함수를 조합만으로 구현할 수 있다.

```javascript
var f1 = _pipe(
  _count_by(function(user) { return user.age - user.age % 10; }),
  _map((count, key) => `<li>${key}대는 ${count}명 입니다.</li>`),
  list => '<ul>' + list.join('') + '</ul>',
  document.write.bind(document) // document.write는 this가 필요해 bind로 묶는다
  );
```

이 함수를 이용하기 전에 원하는 데이터를 한 번 더 필터링할 수도 있다(`f1` 내부 첫 줄에 추가해도 같은 결과다).

```javascript
_go(users, _reject(user => user.age < 20), f1); // f1 함수 내부 첫 줄에서 필터링해도 된다.
_go(users, _filter(user => user.age < 20), f1);
```

또는 바로 실행하지 않고 한 번 더 함수로 감싸, 데이터를 기다리는 함수를 만들 수 있다.

```javascript
var f2 = _pipe(_reject(user => user.age < 20), f1);
```

```javascript
console.log(f2(users));
// <ul><li>20대는 4명 입니다.</li><li>30대는 4명 입니다.</li></ul>
```

> **핵심 통찰**: 통계(count_by) → 변환(map) → 조립(join) → 효과(document.write)까지, 전 과정이 함수 조합 하나로 표현됐다. 부수효과(화면 출력)는 파이프라인의 맨 끝에만 존재한다 — 1장에서 말한 "순수하지 못한 작업의 격리"가 파이프라인 구조에서는 자연스럽게 이루어진다.

## 요약

- 컬렉션 중심 프로그래밍은 **수집(map)·거르기(filter)·찾기(find)·축약(reduce)** 4유형으로 정리되며, 각 유형의 추상 함수로부터 특화 함수가 파생된다.
- `_identity`처럼 사소해 보이는 함수가 `_values`(`_map(_identity)`), `_compact`(`_filter(_identity)`), 보조 함수 기본값(`predi || _identity`)까지 폭넓게 재사용된다.
- `_reject = _filter + _negate`, `_some/_every = _find_index + _negate` — **특화 함수는 함수 조합으로 만들어진다.**
- "모두 그런지, 하나라도 그런지"는 고차 함수로 선택하고, "그러하다는 것"은 보조 함수로 선택한다.
- `_group_by`·`_count_by`의 내부 로직도 `_push`·`_inc`로 쪼개면 변수 선언이 줄고 재사용이 늘어난다.
- reduce는 for가 아니라 **평가 순서와 무관하게 접는 도구**로 사고해야 한다.

## 다른 챕터와의 관계

- **2장**: `_map`·`_filter`·`_each`·`_keys`·`_get`이 이 장의 모든 특화 함수의 재료다.
- **3장**: `_curryr`와 `_go`/`_pipe`가 있어야 이 장의 함수들이 파이프라인에서 조합된다.
- **8장**: `_find`·`_some`·`_every`는 전체 순회 기반이다 — 지연 평가판(filter + take(1) 조합, accumulateWith)이 그 한계를 해소한다.
- **16장**: `_group_by`·`_count_by`가 해시-매치 패턴(groupBy·indexBy)으로 재등장해 O(1) 매칭 최적화에 쓰인다.
