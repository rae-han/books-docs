# Docker 실전 입문 — 핸즈온 Q&A & vs 비교 노트 (자립형)

## 이 노트는 무엇인가

Docker를 **직접 터미널에 명령어를 치고 Docker Desktop GUI로 확인하며** 한 챕터씩 배우는 실습 과정에서, 실제로 **막혔던 지점과 던졌던 질문**을 정리한 복습 노트다.

- **자립형 노트**다. 교재의 핵심 개념을 압축 요약해 함께 담았으므로, **이 노트 하나만 봐도 학습·복습이 완결**된다.
- 더 깊은 디테일(모든 예제, 세부 설명)은 교재 [ch01](ch01-what-is-docker.md), [ch02](ch02-images.md)를 참고한다.
- 구성: **Part A**(세션별 흐름 + 교재 핵심) → **Part B**(vs 비교 모음) → **Part C**(Q&A 모음) → **Part D**(명령어 치트시트).

> **핵심 통찰**: 입문할 때 가장 헷갈리는 건 "비슷해 보이지만 다른 것들"이다(이미지 vs 컨테이너, run vs start, --rm 즉시 vs 종료 시). 그래서 이 노트는 **vs 비교**를 중심에 둔다. 헷갈리면 Part B부터 펴라.

---

# Part A. 세션별 흐름 + 교재 핵심 요약

## 세션 0 — 환경 셋업: daemon / Docker Desktop / CLI 3자 관계

### 교재 핵심 (이것만 알면 됨)

Docker는 **3층 구조**로 동작한다.

```
[당신이 치는 명령]          [실제 일을 하는 엔진]
 docker CLI  ──명령 전송──→  dockerd (daemon)  ──→  컨테이너/이미지 생성
 (터미널, 리모컨)            (실제 엔진)
      ↑                           ↑
   손으로 조작              같은 daemon을 GUI로 보는 창 = Docker Desktop 대시보드
```

- **CLI(`docker`)**: 명령을 보내는 리모컨일 뿐이다. 직접 일하지 않는다.
- **daemon(`dockerd`)**: 실제로 컨테이너를 만들고 이미지를 관리하는 엔진이다. daemon은 **리눅스 프로그램**이다.
- **Docker Desktop**: 맥에는 리눅스 커널이 없으므로, 맥 안에 **경량 Linux VM**을 띄우고 그 안에서 daemon을 돌린다. 이 VM을 띄우고 관리하는 게 Docker Desktop이고, GUI 대시보드도 제공한다.

`docker version` 출력을 보면 이 구조가 드러난다.

```
Client:  OS/Arch: darwin/arm64   ← 내 맥(Apple Silicon)에서 도는 "리모컨"
Server:  OS/Arch: linux/arm64    ← 엔진은 Linux! (맥 안의 VM에서 돈다)
  containerd: 1.6.x              ← daemon이 컨테이너 생성을 위임하는 하위 컴포넌트
  runc:       1.1.x
```

> **핵심 통찰**: **daemon의 수명 = Docker Desktop 앱의 수명**이다. Docker Desktop을 켜야 Linux VM이 뜨고 daemon이 산다. 앱을 끄면(Quit) daemon도 죽고, 그러면 CLI는 "Cannot connect to the Docker daemon" 에러를 뱉는다. 맥/윈도우의 Docker Desktop은 "앱을 켜야 daemon이 산다"는 점이 핵심이다. (Linux 서버에서는 `systemd`로 daemon을 부팅 시 항상 자동 실행하는 경우가 많아 이 문제가 없다)

### 이 세션에서 한 일

```bash
open -a Docker          # Docker Desktop 실행 (daemon 기동)
docker version          # Client(darwin) + Server(linux) 둘 다 연결 확인
docker info             # Docker 시스템 상세 정보
```

### 그때 깨달은 것

- "Cannot connect to the Docker daemon" 에러는 **daemon이 꺼져 있다**는 신호다 → Docker Desktop을 켜면 해결.
- Client는 맥(`darwin`), Server(엔진)는 Linux다. 맥 안에서 격리된 Linux가 돌고 있다.

> 더 깊이: [ch01 §5 — Docker Engine 아키텍처](ch01-what-is-docker.md)

---

## 세션 1 — ch01: 첫 컨테이너 띄우기

### 교재 핵심 (이것만 알면 됨)

**`docker run`은 세 가지 일을 한 번에** 한다.

```
docker run <이미지>  =  pull(없으면 다운로드)  +  create(컨테이너 생성)  +  start(실행)
```

그래서 첫 실행은 다운로드 때문에 느리고, 두 번째부터는 이미지가 이미 있어 빠르다. (단, **컨테이너는 매번 새로 만든다.** 빨라진 건 pull을 건너뛰어서다 → Part B-2 참고)

**이미지 vs 컨테이너**는 도커에서 가장 중요한 구분이다.

```
이미지(image)     = 붕어빵 틀 / 클래스 / 설계도   → 불변, 디스크에 보관, 재사용
컨테이너(container) = 붕어빵 / 인스턴스 / 실행체   → 틀로 찍어내고, 다 쓰면 버림
```

**이미지에는 두 방향**이 있다.

```
┌─ 받아 쓰는 이미지 (베이스) ──────┐   ┌─ 내가 만드는 이미지 (내 앱) ──────┐
│ node:22-alpine, nginx ...        │   │ my-next-app ...                    │
│ = 남이 만들어 Docker Hub에 올림   │   │ = 내 코드를 담아 내가 build       │
│        docker pull (받기)        │   │        docker build (만들기)      │
│            ↓                     │   │            ↓                      │
│       내 로컬에 저장 ────────FROM───→ 이걸 바탕(base)으로 그 위에 코드를 쌓음 │
└──────────────────────────────────┘   └────────────────────────────────────┘
```

내 앱 이미지도 맨바닥부터 만들지 않고, `FROM node:22-alpine`처럼 **남이 만든 베이스 위에** 쌓는다.

**`node:22-alpine`의 정체**: "노드 서버"가 아니라 **Alpine Linux(초경량 리눅스) + Node.js 런타임**이다. 내 앱 코드는 아직 한 줄도 없는 빈 환경이다.

**명령어 구조** — 이미지 이름이 경계다.

```
docker run  --rm  -it   node:22-alpine   node  -e  "console.log('hi')"
└────────────────────┘  └────────────┘  └──────────────────────────────┘
   ① docker에게 주는 말      이미지 이름      ② 컨테이너 안에서 실행할 명령
   (docker run의 옵션)       ⭐경계⭐         (node 프로그램 + node의 옵션)
```

### 이 세션에서 한 일

```bash
# 첫 컨테이너 — 한 줄 코드 실행
docker run --rm node:22-alpine node -e "console.log('Hello from Docker!')"

# 컨테이너 안 셸로 진입해서 내부 탐험
docker run --rm -it node:22-alpine sh
  # 안에서:
  node --version        # Node 런타임 확인
  cat /etc/os-release   # Alpine Linux 확인
  ls /                  # 리눅스 파일시스템 (내 앱 폴더는 없음)
  exit                  # 셸 종료 → 컨테이너 종료 → --rm으로 삭제
```

### 그때 깨달은 것

- `docker run`은 매번 **새 컨테이너**를 만든다 (기존 것 재사용 아님).
- `--rm`은 "즉시 삭제"가 아니라 **"컨테이너가 종료될 때 삭제"**다.
- `-it`와 `-e`는 **서로 다른 프로그램의 옵션**이다(docker vs node).
- "컨테이너에 들어간다" = 안 끝나는 셸(`sh`)을 실행하고 `-it`로 키보드를 연결한 것.

> 더 깊이: [ch01 §6 — 컨테이너 실행하기](ch01-what-is-docker.md)

---

## 세션 2 — ch02: 이미지

### 교재 핵심 (이것만 알면 됨)

**이미지는 통짜가 아니라 레이어(층)가 쌓인 구조**다. `docker history`로 그 층들을 볼 수 있다.

```
docker history node:22-alpine 결과 (아래 → 위 = 과거 → 최신, git log처럼 최신이 맨 위)

CMD ["node"]                        0B      ┐ 메모 레이어(설정만, 0B)
ENTRYPOINT ["docker-entrypoint.sh"] 0B      │
COPY docker-entrypoint.sh ...       388B    ┘
RUN apk add ... (yarn 설치)         5.37MB  ─ 실제 파일 레이어
RUN addgroup ... (Node 설치)        147MB   ─ ⭐ 제일 큰 층 (Node 본체)
─────────── FROM 경계 ───────────
CMD ["/bin/sh"]                     0B      ┐ Alpine Linux 베이스
ADD alpine-minirootfs...tar.gz      8.7MB   ┘ (리눅스 전체가 8.7MB!)
```

- **용량 있는 레이어**(`RUN`/`COPY`/`ADD`): 진짜 파일을 넣은 층.
- **0B 레이어**(`CMD`/`ENV`/`ENTRYPOINT`): 빌드 때 아무 파일도 안 만들고 **"설정만 기록한 메모"**.
- `CMD ["node"]`는 "이미지로 컨테이너를 띄우면 기본으로 `node`를 실행하라"는 메모다. 이미지 이름 뒤에 명령(`sh` 등)을 직접 쓰면 이 메모를 **덮어쓴다**.
- 합산 크기: `8.7 + 147 + 5.37 + 0.0004 ≈ 161MB` = `docker images`의 SIZE와 일치.

**`CREATED`는 빌드 시각**이다. 내가 받은 시각이 아니다(통조림 제조일 vs 구매일).

**태그는 움직이는 포스트잇**이다. 이미지 본체(불변)와 달리, 태그는 다른 이미지로 옮겨 붙을 수 있다. 절대 안 변하는 식별자는 **다이제스트**(`sha256:...`)다.

**레지스트리 = 이미지의 GitHub**다. 기본 레지스트리는 **Docker Hub**이고, `node`처럼 접두어 없는 이름은 **공식 이미지**(`library/node`)다.

### 이 세션에서 한 일

```bash
docker history node:22-alpine          # 레이어 해부
docker history --no-trunc node:22-alpine  # 잘린 명령 전체 보기

docker pull node:22                    # full 버전 받기 (다운로드만)
docker images node                     # alpine(161MB) vs full(1.13GB) 비교

docker image prune                     # <none>(dangling) 이미지 정리
docker tag node:22 my-node:test        # 별명(라벨) 추가 — 같은 IMAGE ID
docker rmi my-node:test                # 라벨만 제거 (본체는 node:22가 가리켜 유지)
```

### 그때 깨달은 것

- `Pull complete`가 4줄이었던 건 **용량 있는 레이어가 4개**였기 때문.
- 같은 Node 22라도 alpine(161MB)과 full(1.13GB)은 **7배** 차이 → 도커는 보통 alpine 선호.
- `<none>` 이미지는 **태그를 잃은 본체**(dangling)다. pull로 태그가 옮겨가며 생긴다.
- 한 이미지 본체에 **여러 라벨**을 붙일 수 있고, `rmi`는 라벨을 떼는(untag) 명령이다.
- 공식 `node` 이미지엔 **yarn이 기본 포함**돼 있고, **pnpm은 없다**(corepack으로 켠다).

> 더 깊이: [ch02 — 이미지](ch02-images.md)

---

# Part B. vs 비교 모음 (헷갈린 개념 쌍)

> 입문에서 헷갈리는 건 대부분 "비슷해 보이는 짝"이다. 막히면 여기부터 본다.

## B-1. 이미지 vs 컨테이너 ⭐ 가장 중요

| 구분 | 이미지(image) | 컨테이너(container) |
|---|---|---|
| 비유 | 붕어빵 틀, 클래스, 설계도 | 붕어빵, 인스턴스, 실행체 |
| 성질 | 불변(읽기 전용) | 실행 중 변경 가능(R/W 레이어 추가) |
| 개수 관계 | 1개로 여러 컨테이너를 찍어냄 | `run`마다 새로 생김 |
| 보관 | 디스크에 남아 재사용 | 만들고 다 쓰면 버림 |
| 확인 명령 | `docker images` | `docker ps` (실행중) / `docker ps -a` (전체) |

## B-2. docker run vs docker start

| 구분 | `docker run <이미지>` | `docker start <컨테이너>` |
|---|---|---|
| 대상 | **이미지** | 기존에 **멈춰있던 컨테이너** |
| 동작 | 새 컨테이너 **생성 + 실행** | 기존 컨테이너 **재실행**(재사용) |
| 반복 시 | 매번 **새것**이 생김 | **같은 것**을 다시 켬 |

```
docker run을 10번 → 컨테이너 10개 생성 (--rm이면 10번 생겼다 사라짐). 이미지는 1개 그대로.
빨라지는 이유 = pull(다운로드) 생략. 컨테이너 재사용이 아니다!
```

## B-3. -it vs -e (이미지 이름이 경계)

| 구분 | `-it` | `-e` (우리가 쓴 `node -e`) |
|---|---|---|
| 소속 | **docker run**의 옵션 | 컨테이너 안 **node**의 옵션 |
| 위치 | 이미지 이름 **앞** | 이미지 이름 **뒤**(실행 명령 쪽) |
| 의미 | 키보드 연결(대화형). `-i`(입력)+`-t`(터미널) | (`--eval`) 뒤 문자열을 JS 코드로 실행 |
| 언제 | 셸·REPL 등 입력이 필요한 프로그램 | 한 줄 코드를 즉시 실행 |

> **핵심 통찰**: **이미지 이름이 경계선**이다. 앞쪽 옵션은 `docker`에게, 뒤쪽은 "컨테이너 안에서 실행할 프로그램"에게 간다. (주의: `docker run`에도 `-e`가 있는데 그건 환경변수 `--env`다. 같은 글자라도 **위치에 따라 주인이 다르다**.)

## B-4. --rm: 즉시 삭제 ❌ vs 종료 시 삭제 ✅

```
docker run --rm -it node:22-alpine sh
│
├─ [0초] 컨테이너 생성 + sh 시작 ──→ 🟢 Running (살아있음, 이때 들어가 있음!)
├─ [그동안] node --version, ls / ... 명령 침 → 셸이 안 끝나니 컨테이너 계속 살아있음
├─ [exit 입력] sh 종료 ──→ 🔴 컨테이너 종료
└─ [종료 직후] --rm 발동 ──→ 🗑️ 그제서야 삭제
```

| 오해 | 사실 |
|---|---|
| `--rm`은 "즉시" 삭제 | "컨테이너가 **종료될 때**" 삭제 |
| 그래서 못 들어감 | 살아있는 동안엔 안 지워지므로 얼마든지 들어감 |

> `node -e "..."`는 1초 만에 끝나서 컨테이너도 1초 만에 종료 → "즉시 삭제처럼" 보였을 뿐. `sh`는 `exit` 전까지 안 끝나서 계속 살아있다.

## B-5. pull vs build vs tag (이미지 얻기 / 이름 붙이기)

| 경로 | 명령 | 하는 일 |
|---|---|---|
| **pull** (받기) | `docker pull node:22` | 레지스트리에서 받으며 이름 자동 부여 |
| **build** (만들기) | `docker build -t my-app:1.0 .` | Dockerfile로 새 이미지 빌드하며 `-t`로 이름 부여 |
| **tag** (별명) | `docker tag node:22 my-node:test` | 기존 이미지에 새 라벨 수동 추가 |

> 셋 다 결국 "이미지 본체에 이름표를 붙이는" 같은 일이다. `pull`은 다운로드하며 자동으로, `tag`는 기존 이미지에 손으로, `build`는 새로 만들며 붙인다.

## B-6. 태그 이동 vs 삭제 (다른 두 사건)

| 구분 | 태그 이동 (pull이 자동으로) | 삭제 (prune / rmi) |
|---|---|---|
| 시점 | `docker pull`할 때 | 내가 명령할 때 |
| 대상 | **라벨만** 새 이미지로 옮김 | 이미지 **본체** 제거 |
| 옛 이미지 | 라벨 잃고 `<none>`으로 **남음**(디스크 점유) | 디스크에서 회수 |

```
[pull]   "22" 라벨이 옛 이미지 → 새 이미지로 옮겨붙음 → 옛것은 <none> (안 지워짐!)
[prune]  라벨 없는 <none>을 실제로 삭제 → 디스크 회수
```

## B-7. 이미지 본체 vs 태그(라벨)

| 구분 | 본체 | 태그(라벨) |
|---|---|---|
| 식별자 | `IMAGE ID` (sha256 기반) | `repository:tag` |
| 개수 | 1개 | 한 본체에 **여러 개** 가능 |
| `docker rmi` | 마지막 라벨이 떨어질 때만 삭제 | `rmi`는 라벨만 떼는 것(untag) |

```
        IMAGE ID c8181... (1.13GB 본체, 디스크에 딱 1개)
           ↑              ↑
       [node:22]    [my-node:test]   ← 라벨 2개, 그래도 용량은 1.13GB 그대로
```

## B-8. CREATED = 빌드 시각 vs 내가 받은 시각

| 항목 | 의미 |
|---|---|
| `docker images`의 `CREATED` 열 | 이미지가 **빌드된 시각** (예: Node팀이 만든 때) |
| 내가 pull(다운로드)한 시각 | `docker images`에 **안 나옴** |

> 마트 통조림과 같다. **제조일(CREATED)**과 **구매일(내가 받은 날)**은 다르다. 오늘 받았어도 CREATED는 몇 주 전일 수 있다. 이미지는 **불변**이라 레지스트리에 미리 빌드돼 있는 걸 복사해 올 뿐이다.

## B-9. 가변 태그 vs 불변 식별자

| 구분 | 가변 태그 (`latest`, `22`, `22-alpine`) | 불변 (다이제스트 `sha256:...`, 커밋 SHA) |
|---|---|---|
| 내용물 | 시간이 지나면 바뀔 수 있음 | 절대 안 바뀜 |
| 비유 | 옮겨 붙는 포스트잇 | 지문 |
| 용도 | 개발 편의 | 프로덕션 고정, **롤백** |

> **실무 팁**: `latest`나 메이저 태그(`22`)는 "어느 날 갑자기 내용물이 바뀔 수 있는" 라벨이다. 프로덕션에선 구체적 버전(`22.13.1-alpine`)이나 다이제스트로 고정한다.

## B-10. alpine vs slim vs full

| 변형 | 크기 | 기반 | 언제 쓰나 |
|---|---|---|---|
| `node:22-alpine` | ~161MB | Alpine Linux (musl) | **기본 선호**, 경량 |
| `node:22-slim` | ~200MB | Debian 최소 | 네이티브 모듈 호환성 필요 시 |
| `node:22` (full) | ~1.13GB | Debian + 빌드도구(gcc 등) | 빌드 단계, 디버깅 |

> 이미지 크기 = 빌드/배포 속도 + 저장 비용 + 보안 공격 표면. 그래서 작을수록 유리하다. (단 alpine은 musl libc라 가끔 네이티브 모듈에서 문제 → slim 대안)

## B-11. npm vs yarn vs pnpm (공식 node 이미지 번들)

| 도구 | 포함 여부 | 비고 |
|---|---|---|
| `npm` | ✅ | node에 원래 딸려옴 |
| `yarn` (1.x) | ✅ | yarn 1 전성기부터 번들, 호환성 때문에 유지(레거시) |
| `corepack` | ✅ | Node 내장 패키지매니저 관리자 ⭐ |
| `pnpm` | ❌ | 기본 미포함 → `RUN corepack enable`로 켬 |

> **실무 팁**: pnpm 사용자는 Dockerfile에 `RUN corepack enable` 한 줄이면 된다. 베이스 이미지는 "가장 보편적 기본값"만 주고, 내 입맛은 내가 레이어로 얹는다.

## B-12. 버전 고정: 도구 설정 vs Docker (고정 강도 사다리)

```
약함 ←────────────────────────────────────────────────→ 강함
 .nvmrc / volta        engines              Docker (FROM node:22.13.1)
 "이 버전 써줘"          "안 맞으면 경고/에러"   환경을 통째로 봉인
```

| 방식 | 파일/위치 | 동작 | 한계 |
|---|---|---|---|
| `.nvmrc` | nvm/fnm이 읽음 | 각자 설치한 node 버전 전환 안내 | 도구 없으면 무시, OS 차이 못 막음 |
| `volta` | package.json | 폴더 진입 시 자동 전환 | 〃 |
| `engines` | package.json | 설치 시 버전 검사(경고/에러) | 〃 |
| `FROM` (Docker) | Dockerfile | node 깔린 리눅스 환경째 봉인 | (가장 강력) |

> single source of truth 권장: `.nvmrc`/`package.json`을 진실의 원천으로 두고, Docker가 `--build-arg NODE_VERSION=$(cat .nvmrc)`로 그 값을 따라가게 한다. (생태계 도구는 전부 `.nvmrc`/`package.json`을 읽지만, Dockerfile을 읽어주는 도구는 없으므로 방향은 항상 "도구가 읽는 파일 → Dockerfile")

## B-13. 일반(코드) 롤백 vs 도커 이미지 롤백

| 구분 | 일반(코드) 롤백 | 도커 이미지 롤백 |
|---|---|---|
| 과정 | `git revert` → 재빌드 → 배포 | 예전 **이미지 태그로 교체** |
| 재빌드 | 필요 | **불필요**(이미 구운 빵을 도로 꺼냄) |
| 속도 | 몇 분~수십 분 | 수십 초 |
| 환경 일관성 | 재빌드 환경에 따라 미묘하게 다를 수 있음 | 그때 그 환경 그대로(불변) |

> 배포마다 **커밋 SHA**를 이미지 태그로 push하면(`ghcr.io/org/app:$GIT_SHA`), 과거 버전이 레지스트리에 보존되어 즉시 롤백 가능. (단 **DB 스키마 변경은 이미지 롤백으로 안 돌아감** — 데이터는 컨테이너 바깥의 별개 문제)

## B-14. Docker Desktop vs daemon vs CLI

| 구성요소 | 역할 |
|---|---|
| **CLI** (`docker`) | 명령을 보내는 리모컨 (직접 일 안 함) |
| **daemon** (`dockerd`) | 실제 일하는 엔진. 맥에선 Linux VM 안에서 돎 |
| **Docker Desktop** | 맥에 Linux VM을 띄워 daemon을 살리고, GUI 대시보드 제공 |

> 셋은 한 몸이다. CLI로 띄운 컨테이너가 GUI에 즉시 뜨고, GUI에서 멈추면 `docker ps`에서도 사라진다 — 같은 daemon을 보기 때문.

---

# Part C. Q&A 모음 (실제로 물어본 질문)

**Q1. 실제로 일하는 daemon이 왜 꺼져 있었나?**
A. daemon은 Docker Desktop 앱이 띄우는 Linux VM 안에서 산다(앱 수명 = daemon 수명). 내 머신은 설정이 `"autoStart": false`라 로그인해도 Docker Desktop이 자동으로 안 켜진다. 재부팅했거나 이전에 종료했다면, 수동으로 켜기 전까지 daemon은 꺼져 있다. → `open -a Docker`로 해결.

**Q2. Docker Desktop 실행 없이 daemon을 계속 띄워둘 순 없나?**
A. 맥에선 "무언가가 Linux VM을 띄워야만" daemon이 산다(맥엔 리눅스 커널이 없으므로). 그러니 "아무것도 없이 상시"는 불가. 단 "수동 실행 없이 자동으로"는 가능하다: ① autoStart 켜기(로그인 시 자동), ② 백그라운드로 조용히(대시보드 자동 열기 끄기), ③ Colima/OrbStack 같은 CLI 기반 대안. 어느 쪽이든 Linux VM은 떠 있어야 해서 메모리(~2GB)를 먹는다.

**Q3. 두 번째 `run`은 기존 컨테이너를 재사용하나?**
A. 아니다. `docker run`은 매번 **새 컨테이너**를 만든다. 두 번째가 빠른 건 컨테이너 재사용이 아니라 **이미지 pull(다운로드)을 건너뛰기** 때문이다. 멈춘 컨테이너를 재실행하려면 `docker start <컨테이너>`를 쓴다. (→ B-2)

**Q4. 방금 받았는데 왜 `CREATED`가 몇 주 전으로 뜨나?**
A. `CREATED`는 **이미지가 빌드된 시각**이지 내가 받은 시각이 아니다. Node팀이 몇 주 전에 빌드해 올린 걸 오늘 다운로드한 것뿐. 이미지는 불변이라 미리 만들어진 걸 복사해 온다. (→ B-8)

**Q5. `--rm`으로 즉시 삭제되는데 어떻게 컨테이너에 들어가나?**
A. `--rm`은 "즉시"가 아니라 **"컨테이너가 종료될 때"** 삭제다. `sh`로 들어가 있는 동안엔 셸이 안 끝나 컨테이너가 살아있으므로 안 지워진다. `exit` 하는 순간에야 삭제된다. (→ B-4)

**Q6. `-e`와 `-it`는 서로 다른 명령의 옵션인가?**
A. 맞다. `-it`는 `docker run`의 옵션(이미지 이름 앞), `node -e`의 `-e`는 컨테이너 안 `node`의 옵션(이미지 이름 뒤)이다. 이미지 이름이 경계다. (→ B-3)

**Q7. node가 설치됐는데 yarn은 왜 또 얹나? 난 pnpm인데.**
A. 기술적으론 필요 없다(node에 npm이 딸려옴). yarn 1 전성기부터 공식 이미지에 번들됐고, 이제 와 빼면 수많은 Dockerfile이 깨져서 호환성 때문에 유지하는 레거시다. pnpm은 미포함이지만 내장된 **corepack**으로 `corepack enable` 한 줄이면 켤 수 있다. (→ B-11)

**Q8. `docker pull node:22`는 클라우드의 환경 구성된 무언가를 받는 거고, 공식 노드팀이 제공하는 건가?**
A. 정확하다. 그 "클라우드 저장소"의 정식 명칭은 **레지스트리**(기본값 = Docker Hub)다. `node`처럼 접두어 없는 이름은 **공식 이미지**(`library/node`)다. `npm install`이나 `git clone`과 똑같은 구조 — 중앙 저장소에서 남이 만든 걸 받아 쓴다.

**Q9. `pull`할 때 원하는 이름으로 바로 못 받나? (그럼 tag로 라벨이 2개 되잖아)**
A. `pull`은 레지스트리에 적힌 이름 그대로 받는다(개명 옵션 없음). 출처를 보존하기 위해서다. 별명이 필요하면 `docker tag`로 추가하는데, 라벨이 2개여도 **본체는 1개**라 디스크 낭비는 없다. (→ B-5, B-7)

**Q10. GitHub와 연동하면 롤백이 빠른가?**
A. 맞다. GitHub Actions가 push마다 `docker build` → `docker push`(GHCR에)를 자동 수행하고, 커밋 SHA로 태깅하면 과거 버전이 레지스트리에 보존된다. 롤백은 "예전 이미지로 교체"라 재빌드 없이 수십 초면 끝난다. (→ B-13)

**Q11. `node:22-alpine` 대신 `node:24`로 바꾸면 최신 24가 깔리나?**
A. 맞다. 단 기존 이미지가 업그레이드되는 게 아니라(이미지는 불변), **별개의 이미지를 하나 더 받는** 것이다. 받고 나면 22와 24가 로컬에 공존한다. 태그는 `<버전>-<변형>` 조합이다(`24-alpine` = Node 24 최신 + alpine).

**Q12. "라벨(메모)과 실물이 같다"는 게 무슨 뜻?**
A. `docker history`에 적힌 `ENV NODE_VERSION=22.x`(빌드 시 기록한 메모)와, 컨테이너 안에서 `node -v`로 확인한 실제 버전이 일치한다는 뜻. 이미지가 **불변(봉인된 통조림)**이라 누가 언제 어디서 실행해도 똑같다 — 이게 도커가 "내 컴퓨터에선 되는데" 문제를 해결하는 원리다.

---

# Part D. 누적 명령어 치트시트

> 지금까지(세션 0~2) 실제로 쓴 명령. 새 세션마다 아래에 추가된다.

## 환경 / 정보

```bash
open -a Docker                 # (macOS) Docker Desktop 실행 → daemon 기동
docker version                 # Client/Server 버전·연결 확인
docker info                    # Docker 시스템 상세 정보
docker --help                  # 전체 명령 목록
docker <명령> --help           # 특정 명령 사용법 (예: docker history --help)
```

## 이미지

```bash
docker pull <이미지>           # 이미지 다운로드만 (예: docker pull node:22)
docker images                  # 로컬 이미지 목록
docker images <repo>           # 특정 저장소만 (예: docker images node)
docker history <이미지>        # 레이어별 히스토리
docker history --no-trunc <이미지>  # 잘린 명령 전체 보기
docker tag <원본> <새이름:태그>     # 별명(라벨) 추가
docker rmi <이미지/태그>       # 이미지(또는 라벨) 제거
docker image prune             # <none>(dangling) 이미지 정리
docker image prune -a          # 미사용 이미지 전체 정리
```

## 컨테이너 실행

```bash
# 구조: docker run [docker옵션] <이미지> [컨테이너 안에서 실행할 명령]
docker run --rm <이미지> <명령>            # 끝나면 자동 삭제
docker run --rm -it <이미지> sh            # 셸로 진입 (대화형)
docker run --rm <이미지> node -e "코드"    # 한 줄 코드 실행

# 자주 쓰는 옵션
#   --rm     종료 시 컨테이너 자동 삭제
#   -it      키보드 연결(대화형). -i(입력)+-t(터미널)
#   -e KEY=V 환경변수 주입(--env)  ※ node -e 의 -e(코드 평가)와 다름!
```

## 컨테이너 조회 (세션 3에서 본격적으로)

```bash
docker ps                      # 실행 중인 컨테이너
docker ps -a                   # 종료된 것까지 전체
```

---

> **다음 세션 예고**: 세션 3 = [ch03 컨테이너](ch03-containers.md) — 지금까진 `node -e`로 한 줄만 실행했지만, 이번엔 브라우저로 접속되는 **HTTP 서버를 컨테이너에 띄운다**. (생명주기 `run`/`stop`/`rm`, `exec`/`logs`/`stats`, GUI Containers 탭 매칭)
