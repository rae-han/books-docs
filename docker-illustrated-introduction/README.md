# 그림으로 배우는 도커 (開発系エンジニアのためのDocker絵とき入門)

> 원서: 『開発系エンジニアのためのDocker絵とき入門』 (스즈키 료/鈴木亮, 슈와시스템/秀和システム, 2022)
> 한국어판: 『그림으로 배우는 도커』 (서수환 옮김, 한빛미디어, 2025) · 404쪽

개발자를 위한 **도커 그림 입문서**. 도커의 기본 개념부터 명령어·Dockerfile·볼륨/네트워크, 그리고 여러 컨테이너로 웹 서비스 개발 환경을 구축하기까지를 **그림과 단계별 실습**으로 익힌다. 명령어를 실행했을 때 시스템 내부에서 무슨 일이 일어나는지를 그림으로 풀어내는 것이 특징인 초·중급 입문서다.

> ⚠️ 현재 이 폴더에는 원문(`origin.md`)만 있고 챕터 노트는 미작성 상태다. 아래 목차는 뼈대이며, 챕터 링크는 노트 작성 후 연결된다.

---

## 전체 목차 (7부 32장)

### 1부 — 가상화와 도커 기본 지식

| 장 | 제목 | 파일 |
|---|---|---|
| 1 | 가상화 | [ch01-virtualization.md](ch01-virtualization.md) |
| 2 | 도커와 주변 요소 살펴보기 | [ch02-docker-components.md](ch02-docker-components.md) |
| 3 | 도커 설치 | [ch03-installing-docker.md](ch03-installing-docker.md) |
| 4 | 도커 기본과 대원칙 | [ch04-docker-basics-and-principles.md](ch04-docker-basics-and-principles.md) |

### 2부 — 도커 컨테이너 활용법

| 장 | 제목 | 파일 |
|---|---|---|
| 5 | 컨테이너 기초 지식 | [ch05-container-basics.md](ch05-container-basics.md) |
| 6 | 컨테이너 기본 조작 | [ch06-basic-container-operations.md](ch06-basic-container-operations.md) |
| 7 | 루비 컨테이너로 인라인 실행하기 | [ch07-ruby-container-inline-execution.md](ch07-ruby-container-inline-execution.md) |
| 8 | 파이썬 대화형 셸로 컨테이너와 소통하기 | [ch08-python-interactive-shell.md](ch08-python-interactive-shell.md) |
| 9 | Nginx 서버를 가동해 브라우저에서 접속하기 | [ch09-nginx-server-browser-access.md](ch09-nginx-server-browser-access.md) |
| 10 | MySQL 서버를 백그라운드로 가동하기 | [ch10-mysql-server-background.md](ch10-mysql-server-background.md) |
| 11 | PostgreSQL 서버 가동해 확인하기 | [ch11-postgresql-server.md](ch11-postgresql-server.md) |

### 3부 — 도커 이미지 활용법

| 장 | 제목 | 파일 |
|---|---|---|
| 12 | 이미지의 기본 내용 | [ch12-image-basics.md](ch12-image-basics.md) |
| 13 | 이미지 기본 조작 | [ch13-basic-image-operations.md](ch13-basic-image-operations.md) |
| 14 | 다른 버전의 MySQL 서버 가동하기 | [ch14-different-mysql-versions.md](ch14-different-mysql-versions.md) |
| 15 | vi 설치 우분투 이미지 작성·공유하기 | [ch15-ubuntu-image-with-vi.md](ch15-ubuntu-image-with-vi.md) |

### 4부 — 도커파일 활용법

| 장 | 제목 | 파일 |
|---|---|---|
| 16 | 도커파일 기초 | [ch16-dockerfile-basics.md](ch16-dockerfile-basics.md) |
| 17 | vi를 쓸 수 있는 우분투 이미지 만들기 | [ch17-building-ubuntu-image-with-vi.md](ch17-building-ubuntu-image-with-vi.md) |
| 18 | 시간대·로그 설정된 MySQL 이미지 만들기 | [ch18-mysql-image-with-timezone-logs.md](ch18-mysql-image-with-timezone-logs.md) |
| 19 | 가동 시 웹서버를 실행하는 파이썬 이미지 만들기 | [ch19-python-image-running-webserver.md](ch19-python-image-running-webserver.md) |

### 5부 — 고급 도커 컨테이너 활용법

| 장 | 제목 | 파일 |
|---|---|---|
| 20 | 볼륨과 네트워크 기초 | [ch20-volumes-and-networks.md](ch20-volumes-and-networks.md) |
| 21 | MySQL 컨테이너 데이터가 사라지지 않게 만들기 | [ch21-persisting-mysql-data-with-volumes.md](ch21-persisting-mysql-data-with-volumes.md) |
| 22 | 호스트에서 편집한 파일을 루비 컨테이너에서 실행하기 | [ch22-bind-mount-ruby-container.md](ch22-bind-mount-ruby-container.md) |
| 23 | PHP 컨테이너에서 MySQL 컨테이너와 통신하기 | [ch23-php-mysql-container-networking.md](ch23-php-mysql-container-networking.md) |

### 6부 — 웹 서비스 개발 환경 구축

| 장 | 제목 | 파일 |
|---|---|---|
| 24 | 구성 정리하기 | [ch24-planning-the-architecture.md](ch24-planning-the-architecture.md) |
| 25 | 필요한 이미지 준비하기 | [ch25-preparing-images.md](ch25-preparing-images.md) |
| 26 | 컨테이너 이외의 리소스 준비하기 | [ch26-preparing-non-container-resources.md](ch26-preparing-non-container-resources.md) |
| 27 | 컨테이너 가동 | [ch27-launching-containers.md](ch27-launching-containers.md) |
| 28 | 도커 컴포즈 이용 | [ch28-using-docker-compose.md](ch28-using-docker-compose.md) |

### 7부 — 운영 시 주의할 점과 트러블슈팅

| 장 | 제목 | 파일 |
|---|---|---|
| 29 | 도커 데스크톱 유료 플랜과 도커 계정 | [ch29-docker-desktop-paid-plans-and-accounts.md](ch29-docker-desktop-paid-plans-and-accounts.md) |
| 30 | 프로젝트에서 도커 사용하기 | [ch30-using-docker-in-projects.md](ch30-using-docker-in-projects.md) |
| 31 | 애플 실리콘 맥에서 도커 사용하기 | [ch31-docker-on-apple-silicon.md](ch31-docker-on-apple-silicon.md) |
| 32 | 디버깅 방법 | [ch32-debugging.md](ch32-debugging.md) |

---

## 관련 책

- [docker-complete-guide/](../docker-complete-guide/) — 자체 구성 Docker 완전 가이드 (Deep Dive 범위, Node.js/Next.js 예제). 본서가 그림 기반 **입문서**라면, 이쪽은 운영·심화까지 다루는 종합 가이드다.
