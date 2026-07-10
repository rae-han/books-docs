# 1. 수집하기 - map

## 1.1. values 함수
컬렉션에 들어있는 값을 꺼내는 함수이다. 키가 0, 1, ... 로 시작하는 배열을 이용해 `_values`를 사용하면 사실 큰 의미가 없고 객체에서 사용할 때 빛을 발한다.
```javascript
function _values(data) {
  return _map(data, function(val) { 
    return val; 
  });
}
```
`_values` 는 `_identity` 함수와 합성하여 리펙토링 가능한데, `_identity` 함수는 값을 그대로 리턴해주는 함수이다. `_values`를 만들기 위해 사용한, 익명한수인 `_map` 함수의  `mapper` 보조함수와 하는 일이 동일하기 때문에 대체 가능하다.
```javascript
function _identity(val) {
  return val;
}
```
```javascript
let value = 10;
console.log(_identity(value)); // 10
```
그냥 리턴하기만 함수를 왜 만들었는지는 나중에 설명하고, 위 함수를 적용 시키면 아래와 같이 코드를 변경 가능하다.
```javascript
function _values(data) {
  return _map(data, _identity);
}
```
추가적으로 `_map` 함수를 `curryr` 한 형태로 변경해 놨다면, `_map` 함수의 첫번째 인자로 함수만 받는다면 함수를 리턴하게 되는데 그 함수는 앞으로 들어올 데이터를 받을 준비를 하는 함수가 된다.
즉 아래 코드는 평가 순서를 뒤집어 다시 만든 `_value` 함수이다.
```javascript
let _values = _map(_identity);
```
`_identity` 함수를 사용하면 위와 같이 함수와 함수의 상호 작용으로만 구현 가능하다.
```javascript
console.log(_values(users);
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

## 1.2. pluck 함수
`_pluck` 함수는 컬렉션 내부에 있는 개체의 특정 키에 해당하는 값을 수집하는 함수이다.
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
`_pluck` 함수를 사용하면 간결하게 값들을 수집할 수 있다.
앞서 구현한 `_get` 함수를 사용하면 더 간결하게 만들 수 있다.
```javascript
function _pluck(data, key) {
  return _map(data, _get(key))
};
```
