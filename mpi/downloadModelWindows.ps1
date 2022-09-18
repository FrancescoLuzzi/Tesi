$URL = "http://posefs1.perception.cs.cmu.edu/OpenPose/models/pose/mpi/pose_iter_160000.caffemodel"
$Path = "pose_iter_160000.caffemodel"

Invoke-WebRequest -URI $URL -OutFile $Path
