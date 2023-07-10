import socketserver
import sys
import os
import threading
import socket
import random

HOST = "192.168.1.61"
PORT = 7777



Players = []
Rooms = {}




'''
Room = {'방 코드' : [{'게임 중' : False}, {'맵' : '맵코드'}, {'호스트':'아이피'}, {'인원' : [아이피, 아이피, 아이피]}],  '방코드' : [{}, {}, {}]}

'''










class MyTcpHandler(socketserver.BaseRequestHandler):
    '''
    이 클래스 쓰레드(서버) 당 한번씩 초기화
    접속자가 생기면 자동호출(call back)
    handle함수를 '오버라이딩'하여, 재정의 해서 할 액션을 지정해야함
    '''

    def handle(self):
        global Players  #전역변수의 player을 사용할거라 선언 필요 (모든 스레드는 플레이어 내용이 같아야함)
        global Rooms
        print('{} is connected'.format(self.client_address[0])) #접속 ip출력

        self.flagRoomList = True # 현재 방 목록창인가
        self.flagRoom = 0 #방코드 (0이면, 방에서 나간 상태)
        self.flagGame = False # 게임 중인가
        self.Exit = False

        self.msg = ""

        player = self.client_address[0]
        Players.append(player)
        print("추가완료")
        
        self.request.sendall("connected with server".encode('utf-8')) #접속자에게 연결완료 메세지 보내기
        print("문자 보냄, 반복 시작")

        try: #오류 검사
            while not self.Exit:
             
                self.msg = self.request.recv(1024).decode('utf-8') #메세지 오면 읽기
                print("메세지 받음")

                if self.flagRoomList: #방 목록 있을때
                    R = Room()


                    if self.msg == "quit":
                        print("disconnected by user")
                        return #종료
                    
                    elif self.msg == "showRooms": #방 목록 요청처리
                        print("request show Rooms")
                        self.request.sendall(','.join(Rooms.keys()).encode('utf-8')) #방코드,방코드,방코드 형식으로 보내기

                    elif "createRooms" in self.msg: #방생성 요청 (요청 형식 = createRooms-방코드)
                        print("request create Rooms")
                        roomcode = self.msg.split('-')[1]
                        print("add " + player)
                        R.makeRoom(roomcode, player) #makeRoom 실행
                        self.request.sendall(roomcode.encode('utf-8')) #정보(방 코드)를 보냄
                        self.flagRoomList = False
                        self.flagRoom = roomcode # 방에 들어온 상태 지정
                        
                    elif "joinRooms" in self.msg: #방참여 요청 (요청 형식 = createRooms-방코드)
                        roomcode = self.msg.split('-')[1]

                        if(R.joinRoom(roomcode, player)): #조인 실행 하면서 오류검사
                            self.request.sendall(('Ok-'+roomcode).encode('utf-8')) #참여 완료 코드 (싸인-방코드)
                            self.flagRoomList = False
                            self.flagRoom = roomcode
                        else:
                            self.request.sendall('Error'.encode('utf-8'))


                elif self.flagRoom != 0:
                    print("방 에 들어온 모드")
                    self.request.sendall(str(Rooms[self.flagRoom]).encode('utf-8'))

                    if("setMap" in self.msg): #맵 코드 지정 형식 : setMap-맵코드
                        set_map = Map((self.msg).split('-')[1])


                        if(set_map.checkMap()):
                            Rooms[self.flagRoom][1]['Map'] = (self.msg).split('-')[1]
                            self.request.sendall("Ok".encode('utf-8'))
                            self.msg = ""
                            print("방 지정 완료")
                        else:
                            self.msg = ""
                            self.request.sendall("noRoom".encode('utf-8'))
                            print("해당 방 없음")
                            







        except Exception as e:
            print(e)





class Room():

    def makeRoom(self, roomCode, player):
        global Rooms

        Rooms[roomCode] = [{'isGame' : False}, {'Map' : ''}, {'Host' : player}, {'Player' : [player]}]   #방 딕셔너리에 방 정보 추가
        return Rooms
    
    def joinRoom(self, roomCode, player):
        global Rooms

        try: #방이 없는지 검사
            Rooms[roomCode][3]['Player'].append(player)

            return True
        except:
            return False
        
    def deleteRoom(self, roomCode, player):
        global Rooms
        if Rooms[roomCode][2]['Host'] != player: #방만든 호스트 본인이 아니면
            return 'NotHost'
        del Rooms[roomCode]
        return 'Ok'
    
    def leaveRoom(self, roomCode, player):
        global Rooms
        try:
            Rooms[roomCode][3]['Player'].remove(player)
            return 'Ok'
        except:
            return 'Not'



class Map():

    def __init__(self, roomCode):

        self.roomCode = roomCode





    def checkMap(self):
        try:
            maps = os.listdir('./Maps/{}'.format(self.roomCode)) #roomCode의 맵 폴더를 열기  (없으면 오류가 날 것임)
            return True
        except FileNotFoundError: #파일 못 찾음 에러 감지
            return False
        

    def makeMap(self, file, player):
        return #나중에 만들거임 (에디터 완성되면)
    
    def listMap(self):
        maps = os.listdir('./Maps/')
        return maps #폴더 목록 읽어와서 list형태로 보내기











                
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass



def RunServer():
    print('서버 시작')

    with ThreadedTCPServer((HOST, PORT), MyTcpHandler) as server:
        server.serve_forever()

RunServer()


