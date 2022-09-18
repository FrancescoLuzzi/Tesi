from abc import ABC, abstractmethod
from typing import Any
import cv2 as cv
from components.utils import CapNotOpenedException
from typing import Tuple
from numpy.core.multiarray import array


class Writer(ABC):
    """This class is used to write to a file or to display frames"""

    input_cap: Any = None
    frame_width: int = 0
    frame_height: int = 0

    def init_writer(self) -> None:
        """Init the frame_width and frame_height using the initialized input_cap.\n
        It inizialized possible output"""
        self.frame_width = int(self.input_cap.get(cv.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.input_cap.get(cv.CAP_PROP_FRAME_HEIGHT))
        if not self.input_cap.isOpened():
            print("Error opening video stream or file")
            raise CapNotOpenedException

    def close(self) -> None:
        """Closes input_cap and possible output"""
        self.input_cap.release()
        self.input_cap = None

    def read(self) -> Tuple[bool, array]:
        """Reads a frame from the input_cap"""
        return self.input_cap.read()

    def is_open(self) -> bool:
        """If input_cap is open returns True else False"""
        return self.input_cap.isOpened()

    def get_frame_props(self) -> Tuple[int, int]:
        """Get tuple containing the frame width and height"""
        return self.frame_width, self.frame_height

    @abstractmethod
    def write(self, frame) -> None:
        """Given a frame it writes it to a file or displays it in a window"""
        pass
