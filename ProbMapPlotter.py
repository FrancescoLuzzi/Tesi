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

# it is used to space the graph over the y axis and to pick less values over the x axis
resize = 8


def read_file(filename):
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
filename = f"{basename}{keypoints_mapping[resp-1]}"
if not path.isfile(filename):
    print("You need to run probMapsRetreiver.py")
    exit(-1)
read_file(f"{filename}.txt")
Z.reverse()
Z = np.array(Z)
Z = Z.transpose()
X.reverse()
fig = plt.figure()
ax = plt.axes(projection="3d")

width = int(440 / resize)
height = int(640 / resize)
dim = (width, height)

ax.plot_wireframe(X, Y, np.array([Z, Z]), rstride=100, cstride=100)
plt.show()
