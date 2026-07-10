# 2. 거르기 - filter

## 2.1. reject 함수
`_reject` 함수는 `_filter` 함수를 반대로 동작 시킨 것이다. 논리 회로에서 `NOT GATE`를 적용 시킨 것과 같다.
```javascript
function _reject(data, predicate) {
  return _filter(data, function(val) {
    return !predi(val);
  })
}
```
`_filter` 함수을 사용하여 보조 함수의 조건을 바꿔도 같은 동작을 하지만 `_reject`를 사용하면 보조 합수인 `predicate` 함수는 그대로 둔 상태에서 앞에 있는 고차 함수의 이름(`_filter` → `_reject`)을 바꿔 동작하게 함으로, 좀 더 선언적으로 프로그래밍 할 수 있다.
`_filter` 함수도 `_map` 함수에서 `_identity` 함수를 통해 간결하게 한 것처럼, `_negate` 함수를 통해 간결하게 만들수 있다.
```javascript
function _negate(func) {
  return function(val) {
    return !func(val);
  }
}
```
이때 `_reject` 함수에서 반환하는 `_filter` 함수의 보조 함수(`1`)와 `_negate` 함수에서 반환하는 함수(`2`)의 모양이 같다는걸 볼 수 있다.
```javascript
// 1
function(val) {
  return !predi(val);
})

// 2
function(val) {
  return !func(val);
}
```
최종적으로 `_reject` 함수를 함수 중첩만 남겨 함수형 프로그래밍스럽게 만들 수 있다.
```javascript
function _reject(data, predi) {
  return _filter(data, _negate(predi));
}
```
```javascript
var _reject = _curryr(_reject); // 나중을 위한 코드
```

## 2.2. compact 함수
값 중 `true` 로 평가되는 값만 남기는 함수이다.
```javascript
var _compact = _filter(_identity);
```
`_compact` 함수는 매우 간단하게 구현 가능하다. `_map` 함수류에 속하는 `_values` 함수를 리팩토링 할 때 구현한 `_identity` 함수 자체가 값을 나타내기 때문에 이 자체로도 `true`, `false` 필터가 가능하다.
값을 리턴 하기만 하는 `_identity` 함수는 별볼일 없어 보이지만 굉장히 간결하고 강력하게 사용 가능하다. 이처럼 굉장히 큰 하나의 클래스를 만드는 것보다, 다양하고 서로 다른 함수를 만들어 그 함수들을 합성하고 조합하는 것이 함수형 프로그래밍스럽다.
```javascript
console.log(_compact([0, 1, 2, null, false, {}])) // [ 1, 2, {} ]
```
