f = open("./probMaps.txt", "r")
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
x = y = 0
mapping = 0
line = f.readline()
o = None
while True:
    if "#" in line:
        x = 0
        y = 0
        if o:
            o.close()
        o = open(
            f"./probMaps{keypoints_mapping[mapping]}.txt",
            "w",
        )
        mapping += 1
    elif line.strip():
        for el in line.split(" "):
            if el.strip():
                o.write(f"{el} ")
                x += 1
        x = 0
        y += 1
        o.write("\n")

    line = f.readline()
    if not line:
        f.close()
        o.close()
        exit()
