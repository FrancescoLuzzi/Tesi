# Tesi


* [Base progetto](https://learnopencv.com/multi-person-pose-estimation-in-opencv-using-openpose/)


![Python version](https://img.shields.io/badge/python-python%203.8-brightgreen)

The **tags** to launch this program are:
* **-i** to give a relative or absolute path to an image, if omitted default to the camera;
* **-o** to give the path to output an image, if omitted an image will pop up;
* **-m** to detect multiple people, if omitted default to single detection.
* **-g** to use gpu accelerated flow with OpenCv compiled with CUDA support
* **-d** select a directory to process (mutually exclusive with -i), -o behaviour changes to the output directory's name (requested)
* **-p** cover detected faces


[OpenPose's License](https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/LICENSE).

[OpenPose's README.md](https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/README.md).

## Prerequisites
* opencv-python 4.5.1 compiled with CUDA11 and cudnn 8.5 [Link tutorial to install](https://www.youtube.com/watch?v=YsmhKar8oOc)
* numpy

