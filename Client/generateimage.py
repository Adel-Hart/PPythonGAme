from PIL import Image

import numpy as np

imgname = "sea"

img = Image.open(f"./images/backgrounds/{imgname}/default.png")

"""
Cimg = img.convert("HSV") #이미지를 HSV 형식으로 변경

npimg = np.array(Cimg) #이미지를 numpy로 변경

#색상 변경
Hlist = [0, 88, 155, 44, 120, 213]

for Hcolor in range(len(Hlist)):
    for i in npimg:
        for j in i:
            j[0] = Hlist[Hcolor]
            pass

    newimg = Image.fromarray(npimg, "HSV")
    newimg = newimg.convert("RGB")
    newimg.save(f"./images/backgrounds/{imgname}/colors/{Hcolor+1}.png") #저장



#BLACK과 WHITE(무채색)

Bimg = img.convert("L") #흑백 이미지

npimg = np.array(Bimg) #이미지를 numpy로 변경

for i in range(len(npimg)):
    for j in range(len(npimg[0])):
        npimg[i][j] = (npimg[i][j]+255) // 2
        pass

newimg = Image.fromarray(npimg, "L")
newimg = newimg.convert("RGB")
newimg.save(f"./images/backgrounds/{imgname}/colors/7.png")

npimg = np.array(Bimg) #이미지를 numpy로 변경

for i in range(len(npimg)):
    for j in range(len(npimg[0])):
        npimg[i][j] = npimg[i][j] // 4
        pass


newimg = Image.fromarray(npimg, "L")
newimg = newimg.convert("RGB")
newimg.save(f"./images/backgrounds/{imgname}/colors/0.png")
"""
Bimg = img.convert("L") #흑백 이미지
npimg = np.array(Bimg) #이미지를 numpy로 변경

for i in range(len(npimg)):
    for j in range(len(npimg[0])):
        npimg[i][j] = npimg[i][j] // 2
        pass

newimg = Image.fromarray(npimg, "L")
newimg = newimg.convert("RGB")
newimg.save(f"./images/backgrounds/{imgname}/colors/8.png")







