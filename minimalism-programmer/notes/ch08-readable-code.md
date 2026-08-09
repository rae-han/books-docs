# Chapter 8: Readable Code (가독성 높은 코드)

## 핵심 질문

들여쓰기 폭과 중괄호 위치 같은 *스타일 논쟁*은 잠시 접어 두자. 진짜 질문은 따로 있다 — **어떻게 하면 코드를 *읽기*에 단순하고, *수정하기*에 단순하게 만들 것인가?** 정렬·쉼표·파일 구조처럼 사소해 보이는 것들이 어떻게 단순함을 만드는가?

> 들여쓰기 폭이나 중괄호 위치 같은 자잘한 규칙들은 중요하게 생각하지 않습니다. 저는 두 가지 핵심 가치에 집중합니다.

| 핵심 가치 | 점검 질문 |
|-----------|------------|
| **읽기 쉬움** | 필요한 정보를 빠르게 찾을 수 있는가? 구조를 한눈에 파악할 수 있는가? |
| **수정 쉬움** | 최소한의 부수적 수정만으로 항목을 추가·제거할 수 있는가? |

이 챕터의 7개 프랙티스는 코드 *설계*가 아니라 *에디터 버퍼에 보이는 텍스트*에 관한 것이다.

## 1. PRACTICE 23 — 주석 달지 않기

### 주석이 많으면 왜 나쁜가

> **아이디어 50**: 코드를 읽기 쉽게 작성하고, 주석은 최소한으로 유지합니다.

| 주석의 부작용 | 설명 |
|----------------|------|
| 작업량 두 배 | 코드 변경 시 주석도 업데이트해야 함 |
| 테스트 안 됨 | 주석은 검증되지 않으므로 잘못될 수 있음 |
| 시간이 흐르면 독이 됨 | 코드와 어긋나 신뢰를 잃음 |

### 주석이 정당한 3가지 이유

```
1. 도구로 문서를 자동 생성할 때
   (API와 커맨드라인 도구 문서화)

2. 미래의 독자에게 "왜"를 설명해야 할 때
   예: "API의 환불 필드는 음수값이기 때문에 환불 금액을 총합에 더합니다"

3. #TODO 같은 플래그
   (다음 프랙티스에서 다룸)
```

> **핵심 통찰**: *Note* — 일부 언어는 주석에 테스트 코드를 직접 삽입할 수 있다. 엘릭서의 doctest, 자바스크립트의 doctest-js, 파이썬의 doctest 등. 이 경우 주석이 *테스트되는* 살아 있는 문서가 된다.

### 저자의 한 가지 더 — 구조 구분

저자는 코드의 주요 구분마다 별표(`*`) 줄을 삽입해 *시각적 표지*로 사용한다.

```yaml
- part: ##############################
  title: Simplify Your Environment
  ##############################
  intro-wide: |
    <imagedata fileref='images/parts/octa.png' width='30%'/>
  include:
    - Automate
    - Research

- part: ##############################
  title: Simplify Your Interactions
  ##############################
```

### 적정선 찾기

> 코드에 특별한 이유 없이 주석이 필요하다면, 그 원인은 코드 자체에 있을 가능성이 높습니다.

| 단계 | 행동 |
|------|------|
| 한 달 실험 | 최소 주석 방식으로 코드 작성 |
| 점검 | 코드 동작을 *설명*하는 주석이 있는가? → 삭제 |
| 매개변수 설명 주석 | 삭제 후 *매개변수 이름*을 더 명확하게 |
| 남기는 주석 | 자신의 존재 이유를 *명확히* 설명할 수 있을 때만 |

## 2. PRACTICE 24 — TODO를 쓰느냐 마느냐

### 작업 흐름의 보호

코드 작성 중 다른 부분에서 버그를 발견하거나, 인접한 코드의 변경이 필요하다는 사실을 알아챘을 때 — 이전엔 그 작업을 먼저 처리하고 돌아왔지만, 그러면 *맥락을 잃었다*.

저자의 새 패턴:

| 변경의 크기 | 행동 |
|-------------|------|
| 오타 수정, 매개변수 값 변경 | 즉시 처리하고 돌아옴 |
| 더 복잡한 작업 | `TODO` 주석을 남기고 계속 진행 |

```ruby
shape = ellipse(r, r) # TODO: could this just be a circle?

# ... code I'm actually changing
```

### TODO 도구의 활용

| 에디터 | 도구 |
|--------|------|
| Neovim | todo-comments.nvim — 프로젝트 전체 TODO 요약 |
| VS Code | TODO Highlighter (500만+ 설치) |

부수 이점: 회의 시작 전 5분을 활용할 *소규모 작업 목록*이 자동으로 만들어진다.

## 3. PRACTICE 25 — 줄을 맞춰 정렬하세요

### 정렬되지 않은 목록의 함정

```ruby
# EU 27개국 목록 (실제로는 26개만 들어 있음)
COUNTRIES = ['Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Republic of Cyprus', 
'Czech Republic', 'Denmark', 'Estonia', 'Finland', 'France', 'Germany', 'Greece',
'Hungary', 'Ireland', 'Italy', 'Latvia', 'Lithuania', 'Luxembourg', 'Malta',
'Netherlands', 'Poland', 'Portugal', 'Romania', 'Slovakia', 'Slovenia', 'Spain',
'Sweden']

puts COUNTRIES.length  #=> 26 (한 개 누락!)
```

빠진 국가를 찾으셨는가?

### 정렬된 목록

```ruby
COUNTRIES = [
  'Austria',    'Belgium',    'Bulgaria',  'Croatia',
  'Cyprus',     'Czechia',    'Denmark',   'Estonia',
  'Finland',    'France',     'Germany',   'Greece',
  'Hungary',    'Ireland',    'Italy',     'Latvia',
  'Lithuania',  'Luxembourg', 'Malta',     'Netherlands',
  'Poland',     'Portugal',   'Romania',   'Slovakia',
  'Slovenia',   'Spain',      'Sweden',
]
```

격자로 정렬되어 누락이 즉시 눈에 띈다.

### 변수 이름 오류 사례

```typescript
// ❌ 정렬되지 않음 — 오타 두 개를 발견하기 어렵다
weight = containerContents.weight
size = containerContent.size           // missing 's'
items = contaierContent.items           // typo: 'contaier'
```

```typescript
// ✅ 정렬됨 — 패턴이 깨진 곳이 즉시 보임
weight = containerContents.weight
size   = containerContent.size           // missing 's'
items  = contaierContent.items           // typo: 'contaier'
```

> **아이디어 51**: 적절한 레이아웃을 사용하면 오류를 더 쉽게 찾아낼 수 있습니다.

> **핵심 통찰**: 사람의 뇌는 패턴 인식에 매우 뛰어나다. 여러 요소를 일렬로 정렬하면 비정상적인 부분이 쉽게 눈에 띈다.

### 정렬의 한계 — 변수 이름 길이가 크게 다를 때

```ruby
# 너무 멀리 떨어져 시선이 흐트러짐
name             = 'Nshuti'
address          = '123 Some Street'
shipping_country = 'Rwanda'
postal_code      = '12345'
date             = '2025/01/01'
```

저자의 해결책: *비슷한 길이끼리 그룹*으로 묶어 정렬.

```ruby
name             = 'Nshuti'
date             = '2025/01/01'

address          = '123 Some Street'
shipping_country = 'Rwanda'
postal_code      = '12345'
```

### 도구

| 에디터 | 플러그인 |
|--------|----------|
| Neovim | EasyAlign (`gaip=` 등) |
| VS Code | 정렬 플러그인 수십 가지 |

키 입력 몇 번으로 정렬되지 않으면 이 일을 하지 않게 된다 — 도구를 익히는 것이 핵심.

## 4. PRACTICE 26 — 마지막에 쉼표 남겨 두기

### Trailing Comma의 가치

C, C#, C++, JavaScript, Python, Ruby 등 대부분 언어가 *마지막 항목 뒤의 쉼표*를 허용한다.

```python
[1, 2, 3,]  # 항목 3개
```

### 쉼표 하나 차이의 효과

```python
# ❌ 쉼표 없이
BIG_LAKES = [
    "Caspian",
    "Superior",
    "Victoria",
    "Huron",
    "Michigan"
]
```

알파벳 순으로 정렬하라는 요청을 받고 정렬하면:

```python
# ❌ 쉼표 누락으로 오류
BIG_LAKES = [
    "Caspian",
    "Huron",
    "Michigan"   # ← 쉼표 누락! (이 줄이 마지막이 아니게 됨)
    "Superior",
    "Victoria",
]
```

```python
# ✅ 모든 줄에 쉼표 — 자유롭게 재정렬 가능
BIG_LAKES = [
    "Caspian",
    "Huron",
    "Michigan",
    "Superior",
    "Victoria",
]
```

> **핵심 통찰**: 마지막 요소도 다른 요소와 동일하게 처리되면 목록을 원하는 방식으로 자유롭게 조작할 수 있다.

## 5. PRACTICE 27 — 순서대로 정렬하기

### 항목 순서가 중요하지 않다면 정렬

```typescript
// ✅ 알파벳 순 enum
enum Purple {
  Eggplant,
  Lavender,
  Lilac,
  Mauve,
  Rebecca,
  Royal,
  Violet,
}
```

옵션 해시도 키를 알파벳 순으로:

```typescript
// ✅ 키 알파벳 순
circle({
  fill: RED,
  stroke: BLACK,
  text: "push me",
  x_pos: 231,
  y_pos: 34,
});
```

### 효과

| 효과 | 설명 |
|------|------|
| 중복 방지 | 정렬돼 있으면 같은 키 추가 시 즉시 발견 |
| 위치 잃지 않음 | 입력 중 위치를 잃는 실수 감소 |
| 다중 줄 정렬 도구 | 에디터의 정렬 기능 활용 |

> 이 기법을 꼭 써야 하는 건 아닙니다. 하지만 실수로 기존 목록에 항목을 중복해서 추가하거나 입력하다가 위치를 잃는 경우도 있을 수 있습니다.

## 6. PRACTICE 28 — 옆으로 긴 코드보다 아래로 긴 코드가 낫다

### 한 줄에 적정 문자 수

> 여러 연구 결과에 따르면 읽기에 가장 적합한 한 줄 문자 수는 **45자에서 75자 사이**입니다. 한 줄이 너무 길면 시선이 어디 있는지 놓치기 쉬워서 처음부터 다시 읽어야 할 수 있습니다.

### 같은 SQL — 두 가지 포맷

```ruby
# ❌ 옆으로 긴 코드 — 한 줄
Product.find_by_sql ["select distinct products.* from products, skus, author_sku_royalties where skus.product_id = products.id order by products.title", self.id]
```

```ruby
# ✅ 아래로 긴 코드 — 여러 줄
Product.find_by_sql [%{
  select distinct products.*
    from products, skus, author_sku_royalties
   where skus.product_id = products.id
   order by products.title
}, self.id]
```

새 테이블·조인 절을 추가할 때 어느 쪽이 더 단순한지 명확하다.

### 펀치카드의 유산

> 우리가 코드를 펀치카드에 입력하던 시절에는 한 줄에 최대한 많은 코드를 작성하면 카드 수를 줄일 수 있었고, 카드 뭉치를 옮길 때 발생하던 허리 통증도 덜 수 있었습니다. 여러분처럼 젊은 개발자들은 이런 문제를 겪지 않습니다. 자유롭게 코드를 작성하며 화면 *아래*로 쌓아 나갈 수 있죠.

### 화면 전체를 쓰고 싶다면

> 여전히 모니터 화면 전체를 사용하고 싶다면, 모니터를 90도로 돌려 보세요.

## 7. PRACTICE 29 — 관련된 코드는 한 곳에 모으기

### 관습의 양면

> **관습**: Rails는 "설정보다 관습". 파일을 올바른 위치에, 적절한 이름으로 배치하면 자동으로 찾아 사용한다.

이는 시간을 절약하지만 *변경을 어렵게* 만들기도 한다.

### 전형적인 Rails 뷰 분산

```
app/
├── assets/
│   ├── stylesheets/
│   │   └── customers.css        ◀ 4개 디렉터리 트리에 흩어진 파일
│   └── javascript/
│       └── customers.js
├── controllers/
│   └── customers_controller.rb
├── helpers/
│   └── customers_helper.rb
└── views/
    └── customers/
        └── show.html.erb
```

다섯 개의 파일이 *서로 다른 디렉터리*에 있다. 작업 속도가 느려진다.

### 저자의 통합 구조

```
app/
├── controllers/
│   └── customers_controller.rb
└── views/
    └── customers/
        └── show.html.erb        ◀ 모든 것이 여기에
```

`show.html.erb` 한 파일에 CSS, JavaScript, 헬퍼, 템플릿이 모두 들어 있다.

```erb
<style>
  /* any view specific css */
</style>

<script>
  // any local JavaScript
</script>

<%
  # any view helper functions (Ruby)
%>

<div>
  <!-- and the template itself -->
</div>
```

### 단일 파일 작업의 흐름

> 한 곳에서 여러 작업을 오가며 전환하지 않고 일할 수 있다는 점은 개발자의 업무를 훨씬 단순하게 만들어 줍니다.

```
[ 시작: 모든 코드를 하나의 파일에 ]
              ▼
[ 자유롭게 리팩터링 — 이동/이름 변경/검색 쉬움 ]
              ▼
[ 시스템이 안정 ]
              ▼
[ 한 걸음 물러서서 분리 여부 결정 ]
              ▼
[ 재사용이 필요할 때만 → 별도 파일로 분리 ]
```

여러 뷰에서 동일한 헬퍼 함수가 반복되면 그때 일반 `xxx_helper.rb`로 분리한다.

### 관습 따르는 개발자들의 반응

> "우리는 알기로는 그건 분명히 잘못됐습니다. 소프트웨어 개발에서는 반드시 기존의 관습을 따라야 합니다."
> 그 말이 맞을지도 모릅니다. 하지만 지금까지는 별다른 부작용이 없었습니다. 꼭 그렇게 해야 한다고 하면, 파일을 분할하는 작업도 어렵지는 않습니다.

> 아마도 Elm과 React 개발자들은 이렇게 말할지도 모르겠습니다. *"그걸 이제야 알았나요? 저희는 예전부터 그렇게 해 왔습니다."*

### 글쓰기에도 적용

> 이 책을 쓰면서 저는 위 접근 방식을 자연스럽게 적용하고 있다는 사실을 깨달았습니다. 각 챕터마다 별도의 파일을 만들었지만, 그 외의 구조적인 요소는 정하지 않았습니다. 모든 내용을 한 곳에 모아 두면 작업 효율이 크게 높아집니다.

### 관습에 얽매이지 않기

| 단계 | 행동 |
|------|------|
| 1 | 새 기능을 한 파일로 시작 |
| 2 | 리팩터링이 필요할 때마다 같은 파일 안에서 |
| 3 | 시스템이 안정되면 분리 여부 검토 |
| 4 | 재사용이 필요할 때만 별도 파일로 분리 |
| 5 | 팀 푸시 전에는 관습대로 분할해도 됨 |

## 8. 가독성 점검 체크리스트

| 항목 | 자기 점검 |
|------|------------|
| 주석 | 코드 *동작*을 설명하는 주석을 마지막으로 삭제한 게 언제인가? |
| TODO | 작업 중 TODO를 남기는 흐름이 있는가? |
| 정렬 | 변수 할당이 격자로 정렬돼 있는가? |
| Trailing comma | 마지막 줄에도 쉼표가 있는가? |
| 알파벳 순 | enum과 옵션 키가 정렬돼 있는가? |
| 줄 길이 | 한 줄이 75자를 넘어가는가? |
| 파일 통합 | 새 기능을 *여러 파일*에 흩어 시작하는가, *한 파일*에서 시작하는가? |

## 요약

- 가독성의 핵심 가치는 **읽기 쉬움**과 **수정 쉬움** 두 가지뿐이다.
- 주석은 *최소화*하라. 정당한 3가지 — 자동 문서, 의도 설명, TODO 플래그.
- TODO 주석은 작업 흐름을 끊지 않게 해 준다. 부수 이점: 회의 전 5분의 작업 목록.
- *정렬*은 사람의 뇌가 잘하는 일을 도와준다. 27개여야 할 목록이 26개임을 즉시 발견할 수 있다.
- *Trailing comma*는 한 글자가 아니라 자유의 표시다. 줄 재정렬을 두려워하지 않게 해 준다.
- 순서가 중요하지 않다면 *알파벳 순*. 중복과 위치 잃기를 막는다.
- 옆으로 긴 코드보다 *아래로 긴 코드*. 45~75자가 읽기에 최적이다.
- 관련 코드는 *한 곳에 모아* 시작. 안정된 후에만 분리. 관습은 도구이지 족쇄가 아니다.

## 다른 챕터와의 관계

이 챕터는 *Part 4(코드의 단순화)*를 닫는다. 7장이 *데이터 구조*의 단순화였다면, 8장은 *그 데이터 구조를 텍스트로 표현*하는 방법의 단순화다.

7장의 데이터 테이블들이 본 챕터의 정렬·trailing comma·알파벳 순 정렬의 원칙을 따를 때 가장 효과적이다. 두 챕터는 *데이터 → 텍스트*의 단방향 의존이 있다.

4장의 *에디터 완전히 장악하기(Practice 12)*가 본 챕터를 가능하게 한다. 키 몇 번으로 정렬·이동·검색이 안 되면, 이 모든 권고는 그저 좋은 말로 그친다.

5장의 *야누스의 두 얼굴*도 단일 파일 시작 패턴에 응답한다 — 새 기능은 *놀이의 영역*에서 한 파일로, 안정된 후에만 *일의 영역*에서 분할한다.

1장의 *현황파악-실행-학습*이 본 챕터에서는 *코드 페이지를 훑어보다 막히면 → 다음엔 어떻게 하면 더 명확하게?*라는 자기 질문으로 나타난다.

다음 마지막 9장은 책 전체를 *단순함의 정의와 평가 기준*으로 닫는다. 본 챕터의 모든 프랙티스가 그 평가 기준의 구체적 예시 — 단순한 코드는 *이해 빠름, 변경 자신감, 동작 파악 빠름*이다.
