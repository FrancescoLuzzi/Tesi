@echo off
bitsadmin /transfer wcb /priority HIGH http://posefs1.perception.cs.cmu.edu/OpenPose/models/pose/mpi/pose_iter_160000.caffemodel "%CD%\pose_iter_160000.caffemodel"
