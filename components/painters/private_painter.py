import cv2 as cv
from numpy import sqrt, absolute, power, min
from typing import List, Dict
from .simple_painter import SimplePainter


class PrivatePainter(SimplePainter):
    def paint_frame(self, frame, detections: List[Dict]) -> None:
        """Paints the limbs found in the frame and covers detected faces"""
        super().paint_frame(frame, detections)
        for person in detections:
            keys = list(person.keys())
            if keys != [0, 1]:
                break
            head = person[keys[0]]
            neck = person[keys[1]]
            head_x, head_y = head
            neck_x, neck_y = neck
            median_x = int(absolute(head_x - neck_x) / 2 + min([head_x, neck_x]))
            median_y = int(absolute(head_y - neck_y) / 2 + min([head_y, neck_y]))
            radius = int(
                sqrt(power(head_x - neck_x, 2) + power(head_y - neck_y, 2)) * 0.6
            )
            cv.circle(
                frame,
                (median_x, median_y),
                radius,
                (0, 0, 0),
                thickness=-1,
                lineType=cv.FILLED,
            )