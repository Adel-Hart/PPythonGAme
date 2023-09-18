# Light In Abyss

#### pj-6, Veni Vedi Veci
----------

## [**ENG**](#ENGLISH)
#### Click to go english ver page

## [**KOR**](#KOREAN)
#### 클릭해서 한국어 버전 보기

---
#KOREAN

### 목차  
[1.이 게임에 대하여](#about)<br/>
[2.스토리](#story)<br/>
[3.참여 인원](#player)<br/>
[4.핵심 기술](#tech)<br/>
[5.이 게임의 독창성](#creativity)<br/>
[6.이 게임에서 주목해야 할 점?](#remark)<br/>  
---
# about
### 1.이 게임에 대하여<br/>
  
> Light In Abyss는, RGB라는 빛의 삼원색을 이용한 퍼즐 게임입니다.<br/>
> 간단히 설명하자면, 빨간색 셀로판지를 통해 보면, 빨간색 사물이 없는 것 처럼 보이는 현상을 이용한 게임입니다.<br/>
> 이 게임은, 화면의 색을 셀로판지를 통해 보는 듯이 변화시키며, 이를통해 같은 색의 타일을 없는 것 처럼 지나가는 게임입니다.<br/>
> RGB와 이를 조합한 기본색의 색 스위치가 있으며, 상황에 맞게 이를 키며 도착지점까지 가면 되는 게임입니다.<br/>
  
---
# story
### 2.스토리
  
> 20XX년, 한 어둠의 세력이 빛읭 색을 모두 가두고, 독점해 사람들의 감정까지 메말라가는 피폐한 삶을 살고 있엇다.<br/>
> 이를 둘러싸고, 빛의 전쟁까지 벌어지게 되며 세상은 더욱 더 황폐화된다.<br/>
> 어둠의 세력은, 도시를 점거하고 세상을 지배하며 도시주변과 도시 중앙에 색을 이용하여 방해물을 놓는다.<br/>
> 당연히 일반인은 색을 잃어 접촉조차 불가능 하였다.<br/>
> 이런 상황속 대학원생 주인공 '라이트'는 드디어 반경 50m의 색을 복원하는 장치를 만들게 된다.<br/>
> 이를 통해 라이트는 점거당한 도시와 색을 되찾는 여정을 시작한다...<br/>
  
---
# player
### 3.참여인원<br/>
  
|이름|닉네임|역할|활동|
|:---:|:---:|:---:|:---|
|김동훈|Adel-Hart|조장|아이디어 제공, 서버 프로토콜 및 로직 설계, 버그 담당.|
|기록현|luckhyoen|팀원|캐릭터 디자인, 타일 디자인|
|김정원|silverkjw|팀원|게임의 플레이 시스템 개발, 플레이 시스템 아이디어 제공, 서버 개발 참여, 버그 해결사, 맵디자인|
|이재용|Plana095|팀원|맵 디자인, 에디터 개발|

---
# tech
### 4.핵심 기술
#### 4-1 클라이언트 - 물리엔진
#### 4-2 클라이언트 - 인터페이스
#### 4-3 클라이언트 - 에디터
#### 4-4 서버
> 서버는 게임 서버에서 많이 쓰이는 TCP - UDP 병렬 사용을 활용한다
> TCP통신 프로토콜은, 안정성이 높지만 속도가 느리고, UDP 프로토콜은 이 반대인 점을 이용하여
> 인게임을 제외한, 서버와의 각종 통신은 TCP로 처리하고 (게임 중, 중요한 트리거 조차도!)
> 인게임에선, 패킷이 손실이 되어도 롤백등의 방법을 처리하면 되기 때문에, UDP를 사용하였다
>
> 서버 파일이 실행되면, UDP소켓이 스레드로 계속 돌아가며, TCP소켓이 메인 스레드에서 열려진다.
> 만약, TCP로 접속이 되면(서버가 accept하면), 접속한 연결을 인자값으로 전달하는 핸들러 스레드를 하나 열고
> 핸들러 스레드 하나당, 플레이어 한명에 지정한다,.
> 핸들러 스레드는, 각종 플레이어와 응답을 하며 요청을 처리한다.
> 이 중, 방은 클래스로 정의를 하는데, 방을 만들면 전역 변수에 방이름을 포함한 코드의 이름으로 전역변수가 저장된다.
> 따라서, 방 목록을 불러올 때는 전역변수의 목록을 불러와 필터링 하는 것이다.
> 방 클래스에서는 방 제거, 방 입장, 게임 시작 등 여러가지 핸들러 시스템이 따로 존재하며
> 방 클래스에서 딕셔너리로 "플레이어 이름" : "그 플레이어의 핸들러" 를 저장하여, 각각 메세지를 보낼땐, for문으로
> 방에 참가한 플레이어의 핸들러에 있는 메세지 전송 함수를 실행시키는 구조이다.
>
> 게임이 시작하기 전에, 통상적인 파이썬 udp서버에서는 서버가 클라이언트의 포트와 주소를 모르기에
> 메세지를 받을 때 같이오는 클라이언트의 주소로 echo 하는 시스템이지만,
> 우리는 지속적인 연결이 필요하기에, 게임 시작전 모든 플레이어가 udp통신을 보내고 그 주소값을 딕셔너리로 저장해
> 나중에, 각 플레이어에게 서버가 능동적으로 메세지를 보낼 수 있는 시스템을 구축하였다.
>
> 초반에  켜진 UDP스레드에서는 서버로 부터 오는 모든 udp통신을 방별로 분별하여 저장하고, 방클래스와 게임 클래스는 이를 읽어서
> 게임을 다룬다.
>
> 게임 클래스에선
> 스레드로 열린 함수 안에서 udp스레드를 이용하여 각 클라이언트에게 자신의 RGB정보와 위치 정보를 받고
> 서버에선 이를 게임클래스의 메서드에 저장한다.
> 동시에 초반에 저장한 클라이언트 주소값에게 저장된 메서드 들을 보내는 함수를 스레드로 실행한다.
>
> 게임 종료는, 서버가 tcp통신에서 클라이언트가 보낸 트리거를 감지하고 서버는 방 목록에서 제거 한 후, 다른 플레이어들에게 나간 사람을 알려준다,
> 서버에서 위 과정을 거칠 때, 인원수를 검사하는데 인원수가 0명이라면 게임 클래스를 삭제하고 플레이어들에게 게임 끝 신호를 보낸다.
> 플레이어는 나간사람을 받을 때 화면에 display하지 않는 함수를 사용하는데, 만약 나간사람이름이 자신 이름이라면 자기의 화면을 바꾼다.

---
# creativity
### 5.이 게임의 독창성

---
# remark
### 6.이 게임에서 주목해야 할 점?

---

## [**ENG**](#English)
#### Click to go english ver page

## [**KOR**](#Korean)
#### 클릭해서 한국어 버전 보기

---


#ENGLISH
### Table of Contents

1. [About This Game](#1.About-This-Game)<br/>
2. [Story](#2.Story)<br/>
3. [Participant](#3.Participant)<br/>
4. [Key Technologies](#4.Key-Technologies)<br/>
5. [Uniqueness of This Game](#5.Uniqueness-of-This-Game)<br/>
6. [What to Look Out for in This Game](#6.What-to-Look-Out-for-in-This-Game)<br/>
---

### 1.About This Game<br/>
  
> Light In Abyss is a puzzle game that utilizes the three primary colors of light, known as RGB.<br/>
> In a nutshell, it employs the phenomenon where, when viewed through a red filter, objects that are red appear to be absent.<br/>
> In this game, you manipulate the screen's colors through filters, making tiles of the same color appear to be nonexistent as you navigate through them.<br/>
> There are RGB color switches and primary color combinations that you can activate strategically to reach your destination.<br/>
  
---

### 2.Story
  
> In the year 20XX, a dark force had monopolized and controlled all colors of light, leading to a bleak existence where even people's emotions withered away.<br/>
> This led to a war of light, further plunging the world into desolation.<br/>
> The forces of darkness occupied cities and used colors to create obstacles in both urban and suburban areas.<br/>
> Naturally, the average person lost all contact due to the loss of colors.<br/>
> In this situation, the protagonist, a graduate student named 'Light,' finally developed a device capable of restoring colors within a 50-meter radius.<br/>
> With this device, Light embarks on a journey to reclaim the occupied city and restore colors to the world...<br/>
  
---

### 3.Participant<br/>
  
|Name|nickName|Role|Activity|
|:---:|:---:|:---:|:---|
|Dong Hoon Kim|Adel-Hart|Team Leader|Idea Contribution, Server Protocol and Logic Design, Bugs Development|
|Luck Hyeon KiKiKiKiKi|luckhyoen|Team Member|Character Design, Tile Design|
|Jung Won Kim|silverkjw|Team Member|Gameplay System Development, Gameplay System Idea Contribution, Participation in Server Development, Bug Fixer, Map Design|
|Jae Yong Lee|Plana095|Team Member|Map Design, Editor Development|

---

### 4.Key Technologies
#### 4-1 Client - Physics Engine
#### 4-2 Client - Interface
#### 4-3 Client - Editor
#### 4-4 Server
> The server utilizes the parallel use of TCP and UDP, commonly used in game servers.
> TCP communication protocol is used for communication with the server, except during gameplay, where UDP is employed due to its speed, even if packets are lost.
> 
> When the server file is executed, a UDP socket continuously runs in a separate thread, and TCP sockets are opened in the main thread. If a TCP connection is established (when the server accepts a connection), > a handler thread is created for each connection, assigned to one player. Each handler thread interacts with various players and handles requests. Room classes are defined, and when a room is created, the room > name, including the code, is stored in global variables. Therefore, when loading the room list, it involves retrieving the list of global variables and filtering them.
> 
> In the game, before it starts, all players send UDP communications and store their address values in a dictionary, allowing the server to actively send messages to each player later. Initially, the UDP thread > that is turned on discerns all UDP communications from the server and stores them separately by room. The room and game classes read this information and handle the game.
>
> In the game class, within a thread-opened function, information about RGB and player positions is received from each client using the UDP thread. The server stores this information in methods of the game
> class. Simultaneously, a function that sends stored methods to client addresses received earlier is executed in a thread.
>
> Game termination is detected by the server when a trigger sent by the client is received via TCP communication. The server removes the room from the list and informs the remaining players. During this process,
> if the number of players is zero, the game class is deleted, and the end-of-game signal is sent to the players. Players use a function that doesn't display the departed player when they receive the departed
>  player's name. If the departed player's name is their own, they change their screen.

---

### 5.Uniqueness of This Game

---

### 6.What to Look Out for in This Game
