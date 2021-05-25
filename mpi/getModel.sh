#!/bin/sh
link="http://posefs1.perception.cs.cmu.edu/OpenPose/models/pose/mpi/pose_iter_160000.caffemodel"
curl -O $link

if [ "$?" -ne "0" ]; then
    wget $link
fi
