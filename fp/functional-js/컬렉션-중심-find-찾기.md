# 3. 찾기 - find

## 3.1. find 함수
`_find` 함수는 컬렉션에서 처음으로 일치하는 값을 리턴하는 함수로 `_filter` 함수와 비슷한데, `_filter` 함수는 모든 값을 검색하며 걸러내는 거라면, `_find` 함수는 값을 하나 찾게되면 바로 리턴하는 함수이다.
원하는 값을 얻게 되면 더 이상 로직을 실행하지 않는 최적화의 키워드가 될 수 있다.
`_find` 함수는 앞서 구현했던 `_each` 함수로 만들면 된다.
```javascript
function _find(list, predi) {
  var keys = _keys(list);

  for(var i = 0, len = keys.length; i < len; i++) {
    if(predi(list[keys[i]])) return list[keys[i]];
    // 만약 일치하는 조건을 만나면 리턴 
    // 아니라면 undefined
  }
}
```
중복되는 부분을 아래와 같이 변경 가능하다.
```javascript
function _find(list, predi) {
  var keys = _keys(list);

  for(var i = 0, len = keys.length; i < len; i++) 
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

## 3.2. find_index 함수
_find  함수와 비슷한데, 컬렉션을 순회하며 일치하는 조건을 만나면 해당 개체의 값이 아닌 `index`를, 만나지 못한다면 `-1` 을 반환한다.
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

### ref. 계속 curryr한 형태의 함수로 바꿔주는 이유
아래 두 코드는 완전히 같게 동작하지만, curryr 형태로 바꿔준 쪽이 좀 더 이해하기 쉽다.
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

## 3.3. some  함수와 every 함수
`_some` 함수는 어떤 값이 하나라도 있는지 확인하고 `boolean` 값을 리턴해주고, `_every` 함수는 모든 값이 조건을 만족하는지 확인하고 `boolean` 값을 리턴해준다.
```javascript
function _some(data, predi) {
  return _find_index(data, predi) !== -1;
} 

function _every(data, predi) {
  return _find_index(data, _negate(predi)) === -1; 
}
```
```javascript
var testcase = [1, 2, 4, 6, 8, 9, 11, 17, 19];

console.log(_some(testcase, function(val) {
  return val === 11;
})) // true

console.log(_every(testcase, function(val) {
  return val < 20;
})) // true
```
```javascript
var testcase = [1, 0, false, null, undefined];

console.log(
  _some(testcase, _identity)
) // true
```
```javascript
var testcase = [0, false, null, undefined];

console.log(
  _some(testcase, _identity)
) // false
```
`_some` 함수와 `_every` 함수는 보조 함수가 없을 때를 대비해야한다. 보조 함수 없이 평가 값 자체적으로 `boolean` 값을 가지고 있기 때문이다. 여기서도 들어온 값을 그대로 리턴하는 `_identity` 함수가 매우 실용적으로 쓰인다.
```javascript
function _some(data, predi) {
  return _find_index(data, predi || _identity) !== -1;
} 
function _every(data, predi) {
  return _find_index(data, _negate(predi || _identity)) === -1; 
}
```
```javascript
var testcase = [1, true, {}, []]

console.log(
  _every(testcase)
) // true
```
```javascript
var testcase = [0, false, null, undefined];

console.log(
  _every(testcase)
) // true
```

## 3.4. 응용
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
함수형 프로그래밍에서 `_some`, `_every`, `_find` 등 모두 고차함수로 사용되고 보조 함수를 받기 때문에, 컬렉션을 받아 *모두 참인가? 참이 있는가?* 를 반환하는 함수보다 더 많은 일을 할수 있다.
일반적인 `indexOf` 함수 같은 경우 완전이 값이 같은지 래퍼런스 비교를 통해서만 해당하는 값이 몇번째 인덱스인지 찾을수 있다면, `_find_index` 함수는 보조함수를 받아서 그 함수 상황을 만족하는 값이 있는지, 없는지, 있다면 몇번째인지 찾을수 있다
즉, 앞에 있는 고차 함수를 고른 후에, 보조함수를 래핑하면서 로직을 고르거나, 조합해나가며 프로그래밍 해나가는 것이다. 모두 그런지, 하나라도 그런지를 고차함수로 선택하고, 그러하느냐가 무엇인지를 보조함수로 선택하는 것이 함수형 프로그래밍이다.
