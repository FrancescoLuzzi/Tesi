import cv2 as cv
from typing import List, Dict
from components.common_data import colors, pose_pairs, n_points
from .painter import Painter

class SimplePainter(Painter):
    def __init__(self):
        self.n_points = n_points
        self.colors = colors
        self.pose_pairs = pose_pairs

    def paint_frame(self, frame, detections: List[Dict]) -> None:
        """Paints the limbs found in the frame."""
        for person in detections:
            keys = list(person.keys())
            cv.circle(frame, person[keys[0]], 4, self.colors[keys[0]], -1, cv.FILLED)
            cv.circle(frame, person[keys[1]], 4, self.colors[keys[1]], -1, cv.FILLED)

            cv.line(
                frame,
                person[keys[0]],
                person[keys[1]],
                self.colors[keys[1]],
                3,
                cv.LINE_AA,
            )
