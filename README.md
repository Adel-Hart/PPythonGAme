
<img
  src="https://s3.ap-northeast-2.amazonaws.com/media.linkareer.com/activity_manager/thumbnail/238729?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAR4ES2NOJI2A55LPI%2F20230926%2Fap-northeast-2%2Fs3%2Faws4_request&X-Amz-Date=20230926T140123Z&X-Amz-Expires=900&X-Amz-Signature=9accc08620662145288245523e1e37b9b68b03ea10153cc2fb52ea43e83373d6&X-Amz-SignedHeaders=host&response-content-disposition=inline%3B%20filename%3D%22%255B%25ED%258F%25AC%25EC%258A%25A4%25ED%2584%25B0%255D%28%25EC%2583%2581%25EB%258B%25A8%25EC%2595%2595%25EC%25B6%2595%292023%25EA%25B2%258C%25EC%259E%2584%25EC%25BD%2594%25EB%2594%25A9%25EB%258C%2580%25ED%259A%258C.jpg%22"
  height="450px"
/>
 

</br>
</br>
</br>






# Light In Abyss

#### pj-6, Team. Veni Vedi Veci


## [**ENG (click me)**](#ENGLISH)
#### Click to go english ver page

## [**KOR (클릭)**](#KOREAN)
#### 클릭해서 한국어 버전 보기


# KOREAN
### 목차  
  
>[1.이 게임에 대하여](#1이-게임에-대하여)  
[2.스토리](#2스토리)  
[3.참여 인원](#3참여-인원)  
[4.핵심 기술](#4핵심-기술)  
[5.이 게임의 독창성](#5이-게임의-독창성)  
[6.이 게임에서 주목해야 할 점?](#6이-게임에서-주목해야-할-점)    

# 1.이 게임에 대하여

> Light In Abyss는, **셀로판지가 특정 빛 성분만 투과시켜 이를 통해 보면</br>
> 해당 빛 성분을 가진 물체들은 배경에 동화되여 안보이는 현상**에서</br>
> 영감을 받아, 만들어진 퍼즐 게임입니다. </br>
> Light In Abyss는, RGB라는 **빛의 삼원색**을 이용한 퍼즐 게임입니다.<br/>
> 간단히 설명하자면, 빨간색 셀로판지를 통해 보면,</br>빨간색인 사물이 없는 것 처럼 보이는 현상을 이용한 게임입니다.<br/>
> 이 게임은, **화면의 색**을 셀로판지를 통해 보는 듯이 **변화시키며**, </br>이를통해 **같은 색의 타일을 없는 것 처럼** 지나가는 게임입니다.</br>
> RGB와 이를 조합한 기본색의 **색 스위치**가 있으며, </br>상황에 맞게 이를 키며 도착지점까지 가면 되는 게임입니다.<br/>
  

# 2.스토리
  
> 20XX년, 한 어둠의 세력이 빛의 색을 모두 가두고, 독점해 사람들의 감정까지 메말라가는 피폐한 삶을 살고 있엇다.<br/>
> 이를 둘러싸고, 빛의 전쟁까지 벌어지게 되며 세상은 더욱 더 황폐화된다.<br/>
> 어둠의 세력은, 도시를 점거하고 세상을 지배하며 도시주변과 도시 중앙에 </br>색을 이용하여 방해물을 놓는다.<br/>
> 당연히 일반인은 색을 잃어 접촉조차 불가능 하였다.<br/>
> 이런 상황속 대학원생 주인공 '라이트'는 드디어 반경 50m의 색을 복원하는 장치를 만들게 된다.<br/>
> 이를 통해 라이트는 점거당한 도시와 색을 되찾는 여정을 시작한다...<br/>
  

# 3.참여 인원
  
|이름|닉네임|역할|활동|
|:---:|:---:|:---:|:---|
|김동훈|Adel-Hart|조장|**아이디어 제공, 전반적인 시스템 구상, </br>서버 프로토콜 및 로직 설계.**|
|기록현|luckhyoen|팀원|**캐릭터 디자인, 타일 디자인**|
|김정원|silverkjw|팀원|**플레이 시스템 개발, 플레이 시스템 아이디어 제공, 서버 개발 참여, 버그 해결, 맵디자인**|
|이재용|Plana095|팀원|**맵 디자인, 에디터 개발**|


# 4.핵심 기술
#### 4-1 클라이언트 - 물리, UI엔진
> UI 엔진에선, **각 버튼과 요소들을 클래스**화 시켜</br> 버튼 등의 요소를 **인스턴스로 생성**하고 </br>인스턴스 변수에 화면에서의 **위치와 크기, </br>클릭시 동작 함수 등을 저장**합니다.</br></br>
> 만약 **마우스의 위치가 해당 위치**일 때 **클릭**이 되면, </br> 설정된 **함수를 실행**시킵니다.</br></br>
> 물리엔진 에서는</br>
> 플레이어의 상하좌우 충돌 감지, 끼임 감지(감지시 사망 처리),</br> 플레이어 이동을 처리합니다.</br>
> 상하좌우 충돌 감지는 좌표에 플레이어 크기이상을 더한 만큼에 해당하는 곳에 타일이 있는지 없는지를 체크하는 함수를 통해 작동되고, </br>
> 끼임 감지도 위와 같은 방식으로 함께 처리됩니다.</br>
> 플레이어 이동에서는 지정된 속도와 방향을 곱한만큼의 위치로 이동시키는 방법을 사용합니다.
#### 4-2 클라이언트 - 인터페이스
#### 4-3 클라이언트 - 에디터
#### 4-4 서버
> 서버는 **게임 서버에서 많이 쓰이는 TCP - UDP 병렬 사용**을 활용한다</br>
> TCP통신 프로토콜은, **안정성이 높지만 속도가 느리고**, </br>UDP 프로토콜은 **이 반대인 점**을 이용하여
> 인게임을 제외한, </br>**서버와의 각종 통신은 TCP로 처리하고 (게임 중, 중요한 트리거 조차도!)** </br>
> **인게임에선**, 패킷이 손실이 되어도 롤백등의 방법을 처리하면 되기 때문에, </br>**UDP를 사용하였다**
>
> 서버 파일이 **실행**되면, **UDP소켓이 스레드로** 계속 돌아가며,</br> **코드에선 **TCP소켓이 열려진다**.</br>
> 만약, TCP로 접속이 되면(서버가 accept하면),</br> **<u>접속한 연결을 인자값으로 전달</u>하는 핸들러 스레드를 하나 열고**</br>
> <u>핸들러 스레드 **하나당**, 플레이어 **한명에 지정**한다</u>,.</br>
> **핸들러 스레드는, 각종 플레이어와 통신을 하며 요청을 받아 처리한다**.
> 이 중, **방은 클래스로 정의**를 하는데, 방을 만들면 </br>**전역 변수에 <u>방이름을 포함한 코드의 이름으로</u> 전역변수가 저장**된다.</br>
> 따라서, **방 목록**을 불러올 때는 **전역변수의 목록**을 불러와 필터링 한다.</br>  
> **방 클래스**에서는 **방 제거, 방 입장, 게임 시작 등 여러가지</br> <u>핸들러 시스템이 따로 존재</u>하며**</br>
> 방 클래스에서 **딕셔너리로 <u>"플레이어 이름" : "그 플레이어의 핸들러"</u> 를</br> 저장**하여, </br>각각 **메세지를 보낼땐**, for문으로
> 방에 참가한 플레이어의 핸들러에 있는 메세지 전송 함수를 실행**시키는 구조이다.
>
> 게임이 **시작하기 전**에, 통상적인 파이썬 udp서버에서는 **서버가 클라이언트의 포트와 주소를 모르기에**</br>
> UDP소켓 통신은 메세지를 받을 때 같이오는 클라이언트의 주소로 echo 하는 시스템이지만,
> 우리는 **지속적인 연결이 필요**하기에, **게임 시작전 모든 플레이어가 udp통신을 보내고 <u>그 주소값을 딕셔너리로 저장</u>해**</br>
> 나중에, 각 플레이어에게 <u>서버가 능동적으로 메세지를 보낼 수 있는 시스템</u>을 구축하였다.
>
> 초반에  켜진 **UDP스레드**에서는 **서버로 부터 오는 <u>모든 udp통신</u>을 </br>방별로 <u>분별하여 저장</u>하고, 방클래스와 게임 클래스는 <u>이를 읽어서</u> 
> 게임을 다룬다.**
>
> **게임 클래스**는
> 스레드로 열린 함수 안에서 **초반에 켜진 UDP스레드를 이용해**</br> 각 **클라이언트에게 <u>클라이언트의 RGB정보와 위치 정보**</u>를 받고</br>
> **이를 게임클래스의 <u>메서드에 저장</u>한다.**</br>
> 동시에 **초반에 저장한 클라이언트 <u>주소값 딕셔너리에서 주소를 가져와**</u> </br>클라이언트에게 **메서드로 저장된 플레이어들의 정보를 보내는** </br>함수를 **스레드**로 실행한다.
>
> **게임 종료**는, **서버**가 tcp통신에서 클라이언트가 보낸 **트리거를 감지**하면</br> 서버는 **방 목록에서 해당 클라이언트를 제거** 한 후,</br> 다른 플레이어들에게 **나간 사람을 알려주는 식**으로 진행된다.</br>
> 서버에서 위 과정을 거칠 때마다, **인원수를 검사**하는데 </br>인원수가 **0명이라면(방에 사람이 다 나가면) <u>게임 클래스를 삭제하고</u></br> 플레이어들에게 <u>게임 끝 신호</u>를 보낸다.**</br> </br>
> 클라이언트는 **오브젝트를 화면에 띄우는 display 함수를 사용**하는데,</br> 만약 서버로 부터 받은 **나간사람이름이 자신 이름**이라면</br> **자기의 화면을 바꾸고(초록색 화면으로)** 자신이 아니라면,</br> 그 사람의 **이름의 오브젝트를 띄우지 않는다.**

# 5.이 게임의 독창성
> 이게임은 </br>
> 타 게임과는 다르게 **빛의 기본색을 조합하는 것을 이용**한 게임이며</br>
> 퍼즐게임 임에도 **멀티플레이가 가능**합니다.</br>
> 또한, **맵을 직접 만들고** 그것을 **공유** 할 수도 있습니다.</br>
> (슈퍼마리오 메이커 처럼...)</br>
> 또한, 여러 테마가 존재합니다.
> 

# 6.이 게임에서 주목해야 할 점?
1. ***획기적인 아이디어***
2. ***독자적인 물리엔진과 UI 시스템***
3. ***개개인의 스크린 사이즈에 따라 바뀌는 게임의 모든 해상도***
4. ***멀티 플레이 구현***(***UDP와  TCP를 동시*** 사용)
5. ***맵 제작 및 구현 시스템*** 제작

## [**ENG (click me)**](#ENGLISH)
#### Click to go english ver page

## [**KOR (클릭)**](#KOREAN)
#### 클릭해서 한국어 버전 보기



# ENGLISH
### Table of Contents

1. [About This Game](#1.About-This-Game)<br/>
2. [Story](#2.Story)<br/>
3. [Participant](#3.Participant)<br/>
4. [Key Technologies](#4.Key-Technologies)<br/>
5. [Uniqueness of This Game](#5.Uniqueness-of-This-Game)<br/>
6. [What to Look Out for in This Game](#6.What-to-Look-Out-for-in-This-Game)<br/>

### 1.About This Game<br/>
  
> Light In Abyss is a puzzle game that utilizes the three primary colors of light, known as RGB.<br/>
> In a nutshell, it employs the phenomenon where, when viewed through a red filter, objects that are red appear to be absent.<br/>
> In this game, you manipulate the screen's colors through filters, making tiles of the same color appear to be nonexistent as you navigate through them.<br/>
> There are RGB color switches and primary color combinations that you can activate strategically to reach your destination.<br/>
  


### 2.Story
  
> In the year 20XX, a dark force had monopolized and controlled all colors of light, leading to a bleak existence where even people's emotions withered away.<br/>
> This led to a war of light, further plunging the world into desolation.<br/>
> The forces of darkness occupied cities and used colors to create obstacles in both urban and suburban areas.<br/>
> Naturally, the average person lost all contact due to the loss of colors.<br/>
> In this situation, the protagonist, a graduate student named 'Light,' finally developed a device capable of restoring colors within a 50-meter radius.<br/>
> With this device, Light embarks on a journey to reclaim the occupied city and restore colors to the world...<br/>
  


### 3.Participant<br/>
  
|Name|nickName|Role|Activity|
|:---:|:---:|:---:|:---|
|Dong Hoon Kim|Adel-Hart|Team Leader|Idea Contribution, Server Protocol and Logic Design, Bugs Development|
|Luck Hyeon KiKiKiKiKi|luckhyoen|Team Member|Character Design, Tile Design|
|Jung Won Kim|silverkjw|Team Member|Gameplay System Development, Gameplay System Idea Contribution, Participation in Server Development, Bug Fixer, Map Design|
|Jae Yong Lee|Plana095|Team Member|Map Design, Editor Development|



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



### 5.Uniqueness of This Game



### 6.What to Look Out for in This Game
