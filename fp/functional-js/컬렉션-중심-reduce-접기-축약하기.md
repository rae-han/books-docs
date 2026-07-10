# 4. 접기, 축약하기 - reduce

`_reduce` 함수는 함수형 프로그래밍에서 굉장히 상징적인 함수로, `Array` 안에 있는 값이나 `Iterable`한 객체의 값들을 통해서 다른 접혀진 값을 만들기 위해 사용한다.
집계, 병합(merge) 등 전혀 다른 값을 만들기 위해 사용하기도 한다.
순차적인 for문 관점에서 `_reduce` 함수를 사용하기보다 함수형적인 측면에서 바라보는게 좋다.
순수 함수로서, 평가 순서 상관 없이 접어나가거나, 축약해나가는 것으로 함수를 이용하는 것이 중요하다.

## 4.1. _min, _max
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
함수형 프로그래밍에서는 평가 순서와 관계 없이 해당하는 결과를 만드는 식으로 사고하는 것이 좋다. 즉 위 코드에서 테스트케이스가 순서대로 들어오지 않는다고 생각하고 프로그래밍 하는 것이 좋다.
즉, `a`, `b`가 들어왔을때 무슨 일을 할까? 에 중점을 둬야한다.
이 말은 `_reduce` 자체를 `for`로 생각하고 프로그래밍 하는 것을 지양해야 한단 말과 같다.

## 4.2. _min_by, _max_by
`_min_by`, `_max_by` 함수는 어떤 조건을 통해 비교를 할 것인가에 해당하는 보조함수인 이터레이터를 추가적으로 받는다.
`_min`, `_max` 함수는 값을 직접 비교하여 다형성이 낮다.
`_by` 함수들은 보조 함수를 받기 때문에, 어떤 일을 할지 가능성을 열어두고 있고 더 많은 일들을 할수 있다.
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
절대 값 비교도 보조 함수를 통해 쉽게 할수 있다.
```javascript
var testcase = [-10, -1, 0, 2, 3, 4, 5];

console.log(_min_by(testcase, Math.abs)); // 0
console.log(_max_by(testcase, Math.abs)); // -10
```
여기서 생각해봐야 할 것이 만약 `_map` 함수를 통해 데이터를 변경 후 비교를 하게 되면 `_max_by` 를 할 때, `-10`이 아닌 `10`이 나오게 된다.
하지만 함수적 아이디어를 통해 이런 특화된 함수 조각을 만들면 좀 더 정교하게 프로그래밍 할수 있고, 다형성과 확장성을 높일수 있다.
```javascript
var _min_by = _curryr(_min_by);
var _max_by = _curryr(_max_by);
```

### ref. 좀 더 실무적인 예제들
```javascript
// 아래 3개는 모두 같은 코드이다. 화살표 함수와 기존에 구현한 _get 함수를 통해 각각 리펙토링 하였다.
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

## 4.3. group_by
특정 값을 통해서 그룹화 시키는 것으로 접기에 특화된 함수이다.
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
console.log(
  _group_by(users, function(user) {
    return user.age;
  })
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

## 4.4. push
`_group_by` 함수 안의 `_reduce` 함수 안에 구현된 코드를 모듈화 하면 좋다. 이유는 저 로직 자체로 의미가 있는데, 객체와 키를 넣고, 키로 찾아진 배열이 있으면 그 곳에 바로 값을 넣고, 없다면 빈 배열을 만들어서 값을 넣는 역할을 한다.
즉 공간이 없다면 공간을 만들어서 값을 넣어주는, 안정성을 높여주는 함수라 생각하면 좋다.
참고로 `_push` 함수는 값을 직접 변경하는 함수이다.
```javascript
function _push(obj, key, val) { 
  (obj[key] = obj[key] || []).push(val);
  return obj;
}
```
`_push` 함수를 쓰면 `_group_by` 함수도 더 간결하게 만들수 있다.
`_group_by` 함수 내부에서 값은 값을 두번 사용하기 위해 변수에 담아두는 일을 하는데, 함수를 쪼개서 만들게 되면 변수 선언이 줄어드는 경향을 보인다.
```javascript
function _group_by(data, iter) {
  return _reduce(data, function(grouped, val) {
    return _push(grouped, iter(val), val)
  }, {});
};
```
위 코드를 보면 함수 실행의 연속을 통해 로직을 만들어 나가는 것을 알수 있다.
또한 보조 함수를 통해 어떤 값을 기준으로 그룹핑을 할 것인가를 위임하게 된다.
```javascript
_go(
  users,
  _group_by(function(user) { return user.age - user.age % 10 }), // 몇대인지 변형된 함수를 줘서 
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
추가 적으로 함수형스러운 아이디어로 아래와 같은 `_head` 함수를 만들어 더 변형해나갈수 있다. 필수는 아니다. 이런 식으로 작은 로직도 함수의 연속 실행을 통해 만들어 간다고 생각하면 좋을거 같다.
```javascript
var _head = function(list) {
  return list[0]
};
```
```javascript
// 변형 전
_go(
  users,
  _group_by(function(user) { return user.name[0] }), // 
  console.log,
)

// 변형 후
_go(
  users,
  _group_by(_pipe(_get('name'), _head)),
  console.log,
)
```

## 4.5. count_by
`_group_by` 와 비슷하지만 이터레이티로 만들어낸 키가 몇개가 있는지 만드는 함수로, 값을 병합하는 행위를 할 필요가 없으므로 더 간결하다.
```javascript
function _count_by(data, iter) {
  return _reduce(data, function(count, val) {
    var key = iter(val);
    // count[ket] = count[key] ? count[key]++ : 1;
    count[key] ? count[key]++ : count[key] = 1;
    return count;
  }, {})
}
```
```javascript
var _count_by = _curryr(_count_by);
```
`_group_by` 의 `_push` 함수와 마찬가지로 `_inc` 함수를 만들어서 간결화 할 수 있다.
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

## 4.6. 활용
`_each` 함수와 `_map` 함수를 `value` 값과 함께 `key` 값 또는 `index` 값 도 넘겨주게 수정한다.
```javascript
let _each = (list, iteratee) => {
	let keys = _keys(list)
	for(let i = 0, len = keys.length; i < len; i++) {
		// iteratee(list[keys[i]]);
		iteratee(list[keys[i]], keys[i]); // # 수정한 부분, key 혹은 index 값도 넘겨 준다.
	}
}
```
```javascript
let _map = (list, mapper) => {
  let new_list = [];

  _each(list, (value, key) => {
		new_list.push(mapper(value, key)); // # 수정한 부분, key 또는 index 값도 넘겨 준다.
	})

  return new_list;
}
```
위 함수를 응용하면 객체의 key, value 쌍을 배열로 만들어 모든 값을 다시 배열로 만드는 `_pair` 함수도 구현할 수 있다.
```javascript
var _pairs = _map((val, key) => [key, val]);
```
```javascript
console.log(_pairs(users[0])) // [ [ 'id', 10 ], [ 'name', 'ID' ], [ 'age', 36 ] ]
```
지금까지 배운 함수들을 응용하여 들어온 데이터 중 원하는 데이터를 필터링하여 원하는 `DOM`으로 만든 후 화면에 보여주는 함수를 구현 가능하다.
```javascript
var f1 = _pipe(
  _count_by(function(user) { return user.age - user.age % 10; }),
  _map((count, key) => `<li>${key}대는 ${count}명 입니다.</li>`),
  list => '<ul>' + list.join('') + '</ul>',
  // document.write // this가 있어야 동작한다 이거 동작 안한다
  document.write.bind(document)
  // html => document.wirte(html)
  );
```
위 함수를 이용하는데 그 전에 원하는 데이터를 한번 더 필터링 할수도 있다. `f1` 함수 첫번째 줄에 추가해도 같은 결과를 내보낸다.
```javascript
_go(users, _reject(user => user.age < 20), f1); // f1 함수 내부에서 첫번째 줄에 필터링을 해도 된다.
_go(users, _filter(user => user.age < 20), f1);
```
또는 위 코드처럼 바로 실행시키지 않고 한번 더 함수로 감싸서 데이터를 기다리는 함수를 만들수 있다.
```javascript
var f2 = _pipe(_reject(user => user.age < 20), f1);
```
```javascript
console.log(f2(users));

<ul><li>20대는 4명 입니다.</li><li>30대는 4명 입니다.</li></ul>
```
