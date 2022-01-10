import cv2 as cv
from abc import ABC, abstractmethod
from numpy import sqrt, absolute, power, min
from components.BaseData import colors, pose_pairs, n_points

__all__ = ["Painter", "PrivatePainter", "SimplePainter", "painter_factory"]


class Painter(ABC):
    n_points: int
    colors: list[list[int]]
    pose_pairs: list[list[int]]

    @abstractmethod
    def paint_frame(self, frame, detections: list[dict]) -> None:
        pass


class SimplePainter(Painter):
    def __init__(self):
        self.n_points = n_points
        self.colors = colors
        self.pose_pairs = pose_pairs

    def paint_frame(self, frame, detections: list[dict]) -> None:
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


class PrivatePainter(SimplePainter):
    def paint_frame(self, frame, detections: list[dict]) -> None:
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


def painter_factory(private: bool):
    painter = None
    if private:
        painter = PrivatePainter()
    else:
        painter = SimplePainter()
    return painter
