import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d
import numpy as np
import cv2
from os import path

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
    X = []
    Y = []
    Z = []
    x = 0
    y = 0
    with open(filename, "r") as f;
        for line in f:
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
    return (X,Y,Z)


resp = None
while resp == None:
    print("q: QUIT")
    for indx, el in enumerate(keypoints_mapping):
        print(f"{indx+1}: {el}")
    i = input("What do you want to plot: ")
    if i == "q":
        exit()
    else:
        try:
            resp = int(i)
            if not (0 < resp <= keypoints_mapping.__len__() + 1):
                raise ValueError("index out of range")
        except:
            resp = None
            print("Inserted value incorrect!")

filename = f"{basename}{keypoints_mapping[resp-1]}"
if not path.isfile(filename):
    print("You need to run probMapsRetreiver.py")
    exit(-1)

X, Y, Z = read_file(f"{filename}.txt")
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
