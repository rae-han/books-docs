# 함수형 자바스크립트 (Functional Javascript with ES6+)

Notion **"Functional Javascript with ES6+"** 개인 노트를 마크다운으로 이관한 폴더. 함수형 프로그래밍의 개념부터 ES6+ 이터러블/제너레이터 기반의 실전 구현(map/filter/reduce, 지연 평가, Promise·동시성 제어)까지 다룬다.

> 원본: Notion 개인 노트 3개 묶음(① FP with ES6+ 데이터베이스, ② Functional JS 페이지, ③ 실전 함수형 프로그래밍)을 그대로 옮김. 코드 예제는 원본 표기대로 JavaScript/TypeScript가 혼용되어 있다.

---

## fp-with-es6-plus/ — ES6+ 이터러블·제너레이터 기반

이터러블/이터레이터 프로토콜과 제너레이터를 토대로 map/filter/reduce부터 지연 평가, Promise, 병렬/동시성 제어까지 쌓아 올리는 시리즈.

| # | 제목 | 파일 |
|---|---|---|
| 0 | 개론 (평가·일급·고차 함수) | [0-개론.md](fp-with-es6-plus/0-개론.md) |
| 1 | ES6 리스트와 이터러블/이터레이터 프로토콜 | [1-리스트와-이터러블-이터레이터-프로토콜.md](fp-with-es6-plus/1-리스트와-이터러블-이터레이터-프로토콜.md) |
| 2 | 제너레이터와 이터레이터 | [2-제너레이터와-이터레이터.md](fp-with-es6-plus/2-제너레이터와-이터레이터.md) |
| 3 | map, filter, reduce | [3-map-filter-reduce.md](fp-with-es6-plus/3-map-filter-reduce.md) |
| 4 | 코드를 값으로 다루어 표현력 높이기 (go·pipe·curry) | [4-코드를-값으로-다루어-표현력-높이기.md](fp-with-es6-plus/4-코드를-값으로-다루어-표현력-높이기.md) |
| 5 | 지연성 1 (lazy range·take·L.map·L.filter) | [5-지연성-1.md](fp-with-es6-plus/5-지연성-1.md) |
| 6 | 지연성 2 (join·find·flatten·flatMap) | [6-지연성-2.md](fp-with-es6-plus/6-지연성-2.md) |
| 7 | 비동기/동시성 1 (Promise·모나드·Kleisli) | [7-비동기-동시성-프로그래밍-1.md](fp-with-es6-plus/7-비동기-동시성-프로그래밍-1.md) |
| 8 | 비동기/동시성 2 (nop·C.reduce·C.take·C.map) | [8-비동기-동시성-프로그래밍-2.md](fp-with-es6-plus/8-비동기-동시성-프로그래밍-2.md) |
| 9 | 비동기/동시성 3 (async/await vs 파이프라인·에러 핸들링) | [9-비동기-동시성-프로그래밍-3.md](fp-with-es6-plus/9-비동기-동시성-프로그래밍-3.md) |

---

## functional-js/ — 함수형 기초 + 컬렉션 중심

절차지향 코드를 함수형으로 바꾸는 과정, 커링, 함수 합성, 그리고 컬렉션 중심(map/filter/find/reduce 계열) 프로그래밍.

| 제목 | 파일 |
|---|---|
| 함수형 프로그래밍 개론 | [함수형-프로그래밍-개론.md](functional-js/함수형-프로그래밍-개론.md) |
| 1. 절차지향적 코드를 함수형으로 | [함수형-프로그래밍-1-절차지향적-코드를-함수형으로.md](functional-js/함수형-프로그래밍-1-절차지향적-코드를-함수형으로.md) |
| 2. 커링 | [함수형-프로그래밍-2-커링.md](functional-js/함수형-프로그래밍-2-커링.md) |
| 3. 연속적인 함수 실행 (_pipe·_go) | [함수형-프로그래밍-3-연속적인-함수-실행.md](functional-js/함수형-프로그래밍-3-연속적인-함수-실행.md) |
| 4. 다형성 높이기 | [함수형-프로그래밍-4-다형성-높이기.md](functional-js/함수형-프로그래밍-4-다형성-높이기.md) |
| 컬렉션 중심 함수형 프로그래밍 (개요) | [컬렉션-중심-함수형-프로그래밍.md](functional-js/컬렉션-중심-함수형-프로그래밍.md) |
| 컬렉션 중심 - map(수집하기) | [컬렉션-중심-map-수집하기.md](functional-js/컬렉션-중심-map-수집하기.md) |
| 컬렉션 중심 - filter(거르기) | [컬렉션-중심-filter-거르기.md](functional-js/컬렉션-중심-filter-거르기.md) |
| 컬렉션 중심 - find(찾기) | [컬렉션-중심-find-찾기.md](functional-js/컬렉션-중심-find-찾기.md) |
| 컬렉션 중심 - reduce(접기·축약하기) | [컬렉션-중심-reduce-접기-축약하기.md](functional-js/컬렉션-중심-reduce-접기-축약하기.md) |
| fp-ts vs fxts (라이브러리 비교 Q&A) | [fp-ts-vs-fxts.md](functional-js/fp-ts-vs-fxts.md) |

> 원본 4번째 문서의 제목은 그냥 "함수형 프로그래밍"이었으나 내용(1.4 다형성 높이기)에 맞춰 파일명을 지었다. `fp-ts-vs-fxts`는 원본에서 오타 제목("함ㅜ형") 페이지의 하위 문서였다.

---

## 실전-함수형-프로그래밍.md

함수 합성 vs 함수 조합의 합성, 부수 효과를 값(Result)으로 다루기, 조건을 값으로 다루기(패턴 매칭), Effect-TS 소개.

- [실전-함수형-프로그래밍.md](실전-함수형-프로그래밍.md)
