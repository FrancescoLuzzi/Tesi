# Tesi

**[Basics of the project](https://learnopencv.com/multi-person-pose-estimation-in-opencv-using-openpose/)**

The **tags** to launch this program are:

- **-i** to give a relative or absolute path to an image to ingest, if omitted default to the camera;
- **-o** to give the path to the output image, if omitted an image will pop up;
- **-m** to detect multiple people, if omitted default to single detection.
- **-g** to use gpu accelerated flow with OpenCv compiled with CUDA support (only with custom installation, tutorial below)
- **-d** select a directory to process (mutually exclusive with -i), -o behaviour changes to the output directory's name (requested)
- **-p** cover detected faces

[OpenPose's License](https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/LICENSE).

[OpenPose's README.md](https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/README.md).

## Prerequisites

![Python version](https://img.shields.io/badge/python-python%203.8-brightgreen)

- opencv-python 4.5.1 compiled with CUDA11 and cudnn 8.5 [Tutorial to install it](https://www.youtube.com/watch?v=YsmhKar8oOc)
- numpy

## Support code

models.py

```
...

def get_keypoints(self, prob_map) -> List[Tuple[List[int], float]]:
    ...
    # to retrive the prob_maps for probMapsRetreiver.py extrapolate_prob_map(prob_map)
    ...

...

def get_valid_pairs(
        self, model_detections, frame_width: int, frame_height: int
    ) -> Tuple[List[NDArray], List[int]]:
    ...
    # to show the heatmaps run: show_heatmap(paf_a,frame), show_heatmap(paf_b,frame)
    # YOU NEED TO PASS THE FRAME AS AN ARGUMENT FROM find_detections
    ...

...
```

probMapsRetreiver.py is used to parse the debug output of the probability map you'll need to use:

```
extrapolate_prob_map(prob_map)
```

ProbMapPlotter.py also uses Matplotlib to display the different prob maps (this script needs matplotlib)
