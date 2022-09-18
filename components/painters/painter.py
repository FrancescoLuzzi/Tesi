from typing import List, Dict
from abc import ABC, abstractmethod


class Painter(ABC):
    n_points: int
    colors: List[List[int]]
    pose_pairs: List[List[int]]

    @abstractmethod
    def paint_frame(self, frame, detections: List[Dict]) -> None:
        """Paints the limbs found in the frame it can also cover detected faces."""
        pass






