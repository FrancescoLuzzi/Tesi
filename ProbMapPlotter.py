import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d
import numpy as np
import cv2
from os import path

X = []
Y = []
Z = []
basename = "./probMaps"
keypoints_mapping = [
    "Head",
    "Neck",
    "R-Sho",
    "R-Elb",
    "R-Wr",
    "L-Sho",
    "L-Elb",
    "L-Wr",
    "R-Hip",
    "R-Knee",
    "R-Ank",
    "L-Hip",
    "L-Knee",
    "L-Ank",
    "Chest",
]
resize = 8


def read_file(filename):
    if not path.isfile(filename):
        print("You need to run probMapsRetreiver.py")
        exit(-1)
    x = 0
    y = 0
    f = open(filename, "r")
    line = f.readline()
    while line:
        if line.strip():
            values = line.split(" ")
            if y % resize == 0:
                for indx, el in enumerate(values):
                    if indx % resize == 0:
                        Z.append(float(el))
                        X.append(x)
                        Y.append(y / resize)
                        x += 1
            x = 0
            y += 1
        line = f.readline()


resp = None
while resp == None:
    print("q: QUIT")
    for indx, el in enumerate(keypoints_mapping):
        print(f"{indx+1}: {el}")
    i = input("Cosa vuoi plottare: ")
    if i == "q":
        exit()
    elif int(i) > keypoints_mapping.__len__() + 1:
        print("valore non giusto")
    else:
        resp = int(i)
read_file(f"{basename}{keypoints_mapping[resp-1]}.txt")
Z.reverse()
Z = np.array(Z)
Z = Z.transpose()
fig = plt.figure()
ax = plt.axes(projection="3d")

# Read the image with Opencv
img = cv2.imread("./group.jpg")
# Change the color from BGR to RGB
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

width = int(440 / resize)
height = int(640 / resize)
dim = (width, height)

# resize image
img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

# Orgird to store data
x, y = np.ogrid[0 : img.shape[0], 0 : img.shape[1]]
# In Python3 matplotlib assumes rgbdata in range 0.0 to 1.0
img = img.astype("float32") / 255
ax.plot_surface(x, y, np.atleast_2d(0), rstride=3, cstride=3, facecolors=img)
X.reverse()
ax.plot_wireframe(X, Y, np.array([Z, Z]), rstride=100, cstride=100)
plt.show()
