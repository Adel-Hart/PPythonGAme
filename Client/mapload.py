COLORON = 150 # 켜질 때의 밝기

#RGB 색상표 사전 지정
WHITE = [COLORON,COLORON,COLORON]
BLACK = [0,0,0]

RED = [COLORON,0,0]
GREEN = [0,COLORON,0]
BLUE = [0,0,COLORON]

YELLOW = [COLORON,COLORON,0]
CYAN = [0,COLORON,COLORON]
MAGENTA = [COLORON,0,COLORON]


WALL = [COLORON//2,COLORON//2,COLORON//2]

ColorDict = {"0":BLACK, "1":RED, "2":GREEN, "3":BLUE, "4": YELLOW, "5":CYAN, "6":MAGENTA, "7":WHITE, "8":WALL} #색상표


def readMap(MapName): #dat 파일을 읽고 맵 array와 플레이어의 좌표를 반환하는 함수
    f = open("./maps/"+str(MapName)+"/map.dat", "r") #파일 읽기

    lines = f.readlines()
    backgroundImage = "None"

    Map = []
    for line in lines:
        line = line.strip("\n")
        if "!" in line: # !가 있는 줄은 플레이어의 좌표를 말한다
            line = line.strip("!") #! 제거
            Pos = line.split(",") #, 기준으로 문자열 나누기
            posX = float(Pos[0])
            posY = float(Pos[1]) 
            pass
        elif "@" in line: # @가 있는 줄은 플레이어의 x,y 크기를 말한다
            line = line.strip("@") # @ 제거
            Pos = line.split(",") #, 기준으로 문자열 나누기
            sizeX = float(Pos[0])
            sizeY = float(Pos[1]) 
            pass
        elif "#" in line: # #가 있는 줄은 점프속도, 중력 가속도를 말한다
            line = line.strip("#") #! 제거
            Pos = line.split(",") #, 기준으로 문자열 나누기
            jumpPower = float(Pos[0])
            gravity = float(Pos[1]) 
            movespeed = float(Pos[2]) 
            pass
        elif "$" in line: # &가 있는 줄은 배경 폴더의 이름:
            line = line.strip("#") #$ 제거
            backgroundImage = line
        else:
            Map.append(map(lambda x : ColorDict[x],list(line))) #새로운 가로줄 추가
    #print(Map)
    Map = list(map(list, zip(*Map))) #2차원 배열 뒤집기(x와 y가 반대로 되어있으므로)

    tileX = len(Map)
    tileY = len(Map[0])

    f.close() #파일 닫기

    if backgroundImage == "None":
        backgroundImage = "test"

    return Map, tileX, tileY, posX, posY, sizeX, sizeY, jumpPower, gravity, movespeed, backgroundImage