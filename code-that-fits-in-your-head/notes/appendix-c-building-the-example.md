# Appendix C: Building the Example (예제 빌드해 보기)

## 핵심 질문

이 책의 레스토랑 예약 시스템 예제 코드를 실제로 내 컴퓨터에서 실행해보려면 어떻게 해야 하는가? 그리고 사실 예제를 굳이 빌드해야 할까 — 무엇을 배우는 것이 더 중요한가?

---

## 1. 예제 파일 관련 정보

이 책의 예제 파일은 **깃 저장소 전체를 ZIP으로 압축한 형태**로 제공되며, 본문에서 본 것처럼 C# 언어를 사용한다.

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 이 책은 **C# 개발자를 위한 책이 아니다**. 휴리스틱 기법과 프랙티스를 소개하는 것이 목적이며, C# 코드는 단지 예제일 뿐이다. 따라서 빌드해보는 것 자체가 큰 의미를 갖진 않는다.
:::

본문에서도 특정 시점의 코드를 설명할 때 **깃 해시(*Git hash - 커밋을 식별하는 고유 해시값. 예: af31e63*)** 를 함께 제시한다. 어떤 기법 때문에 코드가 어떻게 바뀌었는지 시간 순으로 추적해볼 수 있게 한 것이다.

따라서 이 부록의 진짜 권장은 이것이다.

> 빌드해서 실행하는 것보다 **깃 로그를 통해 코드가 어떻게 진화했는지 시간 순으로 살펴보는 것**이 훨씬 많은 것을 배우게 해준다.

즉, 빌드 환경보다 **익숙하고 깃 로그를 살펴보기 편한 환경**에 파일을 올려두는 것이 중요하다. 최근 Visual Studio는 깃 지원이 좋고, 필요하면 GitLens 같은 플러그인을 추가로 설치할 수 있다.

예제 파일은 깃 저장소 전체를 압축한 것이므로, ``.git`` 디렉터리가 포함되어 있다. 이 디렉터리를 깃이 실행 가능한 PC의 디렉터리에 두어 로컬 저장소로 인식시키면 된다.

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 한글판의 경우 주석 부분과 문서를 한글로 바꾸는 과정에서 원본 HEAD보다 한 버전 위로 커밋이 올라가 있을 수 있다. 크게 문제 되지는 않는다.
:::

---

## 2. 윈도우 환경에서 빌드하는 방법

Visual Studio Community 2022 기준. 설치 시 다음 워크로드를 포함시켜야 한다.

- C# 언어 지원
- MSSQL Express
- IIS Express
- 테스트 관련 컴포넌트

### 2.1 솔루션 파일 열기

두 개의 솔루션 파일이 제공된다.

| 솔루션 | 내용 | 소요 시간 |
|---|---|---|
| ``Restaurant.sln`` | 일상적인 유닛 테스트 | 매우 빠름 |
| ``Build.sln`` | DB 통합 테스트 포함, 2단계 테스트 | 약간 시간 걸림 |

### 2.2 NuGet 패키지 소스 설정

NuGet이 자동 구성되어 있지 않다면 **프로젝트 → NuGet 패키지 관리자 → 설정 → 패키지 소스**에서 다음을 추가한다.

- 이름: ``nuget.org``
- 소스: ``https://api.nuget.org/v3/index.json``

### 2.3 빌드와 테스트

1. 프로젝트를 빌드한다
2. 이 프로젝트의 결과물은 REST API이므로, 웹 서버에서 API를 제공하며 관련 유닛 테스트를 통해 동작을 검증한다
3. **테스트 → 테스트 탐색기**를 열어 모든 테스트를 실행한다
4. 정상 빌드되었다면 모든 테스트가 통과한다

``Build.sln`` 은 다음과 같은 테스트 그룹을 포함한다.

- ``SqlIntegrationTests`` (동시성 테스트 등)
- ``ConcurrencyTests`` (``NoOverbookingPutRace``, ``NoOverbookingRace``)
- ``SqlReservationsRepositoryTests`` (``CreateAndReadRoundTrip``, ``PutAndReadRoundTrip``)
- ``Restaurant.RestApi.Tests`` (일반 유닛 테스트 145개)

윈도우 + Visual Studio 환경이면 대부분의 C# 개발자에게 익숙한 환경이므로 큰 무리 없이 빌드가 될 것이다.

---

## 3. 리눅스 / WSL 환경에서 컴파일하는 방법

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 이 책의 예제는 **LocalDB 기반 SQL 통합 테스트**를 포함하는데, LocalDB는 윈도우 전용이다. 리눅스에서 C# 빌드 환경을 구축하는 것은 그리 적합하지 않다. 개인적 도전이나 학습이 목적이 아니라면 윈도우 환경을 권장한다.
:::

### 3.1 사전 유의사항

- **Ubuntu 22.04 LTS 이상에서는 빌드 불가.** 이 프로젝트는 ASP.NET Core 3.1을 사용하는데, 해당 버전이 우분투 22.04 이상에는 포팅되어 있지 않다. **우분투 20.04 이하**를 사용해야 한다.
- SQL 통합 테스트가 매우 어렵다. LocalDB가 없으므로 MSSQL Express를 별도 설치해야 한다.
- 옮긴이는 WSL 2 + Ubuntu 20.04 환경에서 예제를 실행했다.

### 3.2 .NET 설치

리눅스의 패키지 매니저가 아닌 수동 스크립트로 설치한다.

```bash
$ wget https://dotnet.microsoft.com/download/dotnet/scripts/v1/dotnet-install.sh
$ chmod +x dotnet-install.sh
$ ./dotnet-install.sh --version 3.1.426
$ ./dotnet-install.sh --version 7.0.306
$ export PATH=$HOME/.dotnet:$PATH   # .bashrc 에 추가 권장
$ dotnet --list-sdks
```

``dotnet --list-sdks`` 에서 두 버전이 모두 보이면 설치 완료.

### 3.3 유닛 테스트만 실행

SQL 통합 테스트 없이 유닛 테스트만 돌린다면 ``Restaurant.sln`` 을 사용한다.

```bash
$ dotnet test Restaurant.sln --configuration Release
```

정상이면 REST API 서버가 뜬 뒤 유닛 테스트가 진행되고, 다음과 같은 결과가 나온다.

```
Passed! - Failed: 0, Passed: 168, Skipped: 0, Total: 168, Duration: 8s
```

### 3.4 SQL 통합 테스트를 리눅스에서 돌리는 방법

리눅스에 MSSQL Express를 설치한다.

```bash
$ wget -qO- https://packages.microsoft.com/keys/microsoft.asc \
    | sudo tee /etc/apt/trusted.gpg.d/microsoft.asc
$ sudo add-apt-repository \
    "$(wget -qO- https://packages.microsoft.com/config/ubuntu/20.04/mssql-server-2022.list)"
$ sudo apt-get update
$ sudo apt-get install -y mssql-server
$ sudo /opt/mssql/bin/mssql-conf setup
```

설치 중 에디션 선택에서 **3번 Express (free)** 를 선택하고, 비밀번호는 소문자/대문자/숫자/특수문자 조합으로 입력한다.

**WSL 2에서 systemd 문제**가 발생할 수 있다. 이때는 PowerShell에서 다음을 실행한다.

```powershell
wsl --shutdown
wsl --update
wsl
```

WSL 안으로 들어와 ``wsl.conf`` 를 편집한다.

```bash
$ sudo vi /etc/wsl.conf
```

```
[boot]
systemd=true
```

다시 PowerShell에서 ``wsl --shutdown`` 후 WSL로 재진입하고 ``sudo systemctl status`` 로 systemd 동작을 확인한다. 그 다음 MSSQL을 띄운다.

```bash
$ systemctl status mssql-server --no-pager
```

MSSQL command-line tools도 함께 설치.

```bash
$ curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
$ sudo add-apt-repository \
    "$(curl https://packages.microsoft.com/config/ubuntu/16.04/prod.list)"
$ sudo apt-get update
$ sudo apt-get install -y mssql-tools unixodbc-dev
$ echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc
$ source ~/.bashrc
```

### 3.5 Connection String 수정

``SqlIntegrationTests`` 에 있는 SQL connection string을 LocalDB → MSSQL로 수정한다.

파일 위치: ``/Restaurant.RestApi.SqlIntegrationTests/ConnectionStrings.cs``

**기존**:

```csharp
public static class ConnectionStrings
{
    public const string Reservations =
        @"Server=(LocalDB)\MSSQLLocalDB;Database=RestaurantIntegrationTest;Integrated Security=true";
}
```

**수정 후** (``<SQL_PASSWORD>`` 자리에 설치할 때 지정한 비밀번호):

```csharp
public const string Reservations =
    @"Server=Localhost;Database=RestaurantIntegrationTest;User Id=SA;Password=<SQL_PASSWORD>;Encrypt=False;Integrated Security=False";
```

### 3.6 통합 테스트 실행

```bash
$ dotnet test Build.sln --configuration Release
```

기본 유닛 테스트 결과.

```
Passed! - Failed: 0, Passed: 168, Skipped: 0, Total: 168, Duration: 8s
```

이어서 SQL 통합 테스트가 실행된다. Deadlock 관련 에러가 발생할 수 있지만 테스트 자체에는 문제가 되지 않는다. 정상 종료 시 다음과 같이 나온다.

```
Passed! - Failed: 0, Passed: 8, Skipped: 0, Total: 8, Duration: 54s
```

---

## 4. 끝내면서

앞에서 반복 강조했지만 이 책의 예제는 **빌드하고 유닛 테스트를 돌리는 것 자체가 중요하지 않다**.

::: callout {icon="💡" color="gray_bg"}
**핵심 통찰**: 본문의 내용이 어떤 방식으로 추가되었는지 **시간 순, 기법 순으로 살펴보는 것**이 훨씬 중요하다. 코드를 읽는다고 생각하고 저장소를 둘러보라. ``git log`` 와 ``git show <hash>`` 만으로도 이 책의 진짜 학습이 이루어진다.
:::

예를 들어 본문에서 특정 코드를 소개할 때 함께 나오는 해시로 checkout 하여 해당 시점의 코드를 살펴볼 수 있다.

```bash
$ git log --oneline
$ git show af31e63
$ git checkout af31e63
```

책 안에서 언급된 커밋 해시별 상태를 오가며 **리팩터링의 흐름**을 눈으로 따라가는 것이 이 예제의 진짜 가치다.

---

## 요약

- 이 책의 예제 코드는 C#/ASP.NET Core 3.1로 작성된 REST API. **깃 저장소 전체가 압축된 형태로 제공**됨
- 목적은 빌드/실행이 아니라 **깃 로그를 통해 코드 진화의 시간축을 학습**하는 것
- **윈도우 + Visual Studio 2022**가 가장 매끄러운 환경 — ``Restaurant.sln`` (빠름), ``Build.sln`` (통합 테스트 포함)
- **리눅스/WSL**은 ASP.NET Core 3.1이 필요하므로 **Ubuntu 20.04 이하**만 가능
- SQL 통합 테스트는 LocalDB에 의존하는데 리눅스 미지원 → MSSQL Express를 별도 설치하고 connection string을 수정
- WSL 2에서 MSSQL이 뜨지 않으면 ``systemd=true`` 설정 후 재시작
- **실행보다 학습**이 중심: ``git log`` , ``git show <hash>`` , ``git checkout <hash>`` 를 활용해 본문 예제의 특정 시점을 오가며 리팩터링 흐름을 따라간다
