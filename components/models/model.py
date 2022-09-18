from abc import ABC, abstractmethod
from typing import Any, List
import numpy as np
import cv2 as cv
from time import time
from components.common_data import pose_pairs, n_points, threshold
import logging


def get_framerate(func):
    """Decorator to evaluate the time spend in a function"""

    def wrapper(*args, **kwargs) -> None:
        start_time = time()
        frame = func(*args, **kwargs)
        time_elapsed = float(time() - start_time)
        print(
            f"Time elapsed: {time_elapsed:.2f} corrisponding to {1/time_elapsed:.2f} fps"
        )
        return frame

    return wrapper


def show_heatmap(paf, frame) -> None:
    """Shows the heatmaps of the paf on to the original frame displaying it"""
    heatmapshow = None
    heatmapshow = cv.normalize(
        paf, heatmapshow, alpha=0, beta=255, norm_type=cv.NORM_MINMAX, dtype=cv.CV_8U
    )
    heatmapshow = cv.applyColorMap(heatmapshow, cv.COLORMAP_HOT)
    cv.imshow("Heatmap", cv.addWeighted(heatmapshow, 0.3, frame, 0.7, 0))
    cv.waitKey(0)


def extrapolate_prob_map(prob_map) -> None:
    """Estrapolates the prob_maps to a file called probMaps.txt"""
    with open("probMaps.txt", "a") as f:
        f.write("#########")
        np.savetxt(f, prob_map, fmt="%.2f")


class Model(ABC):

    model_path: str
    proto_path: str
    n_points: int
    threshold: float
    n_points: int
    pose_pairs: List[List[int]]
    net: Any

    def __init__(self, model_path: str, proto_path: str) -> None:
        self.model_path = model_path
        self.proto_path = proto_path

        self.threshold = threshold
        self.n_points = n_points
        self.pose_pairs = pose_pairs

    @abstractmethod
    def find_detections(self, frame, frame_width: int, frame_height: int) -> Any:
        """Finds the keypoints relative to one or multiple people in a frame, it returns a List[Dict]\n
        composed by [{ keypoint_id: (x,y) , keypoint_id: (x,y)}, ...]"""
        pass

    def init_net(self) -> None:
        """Initialize the net using proto_path and model_path"""
        self.net = cv.dnn.readNetFromCaffe(self.proto_path, self.model_path)

    def enable_gpu(self) -> None:
        """If opencv is built with CUDA support, enable GPU acceleration"""
        if not "cuda" in cv.getBuildInformation():
            logging.warning(
                "Your opencv installation was not built with cuda support, please refer to README.md for clarifications.\nCouldn't enable GPU accelertion, using CPU.\n"
            )
            return

        self.net.setPreferableBackend(cv.dnn.DNN_BACKEND_CUDA)
        self.net.setPreferableTarget(cv.dnn.DNN_TARGET_CUDA)
        logging.info("gpu Accelerated")
