from abc import ABC, abstractmethod
from typing import Any
import cv2 as cv
from .Exceptions import CapNotOpenedException
from typing import Tuple
from numpy.core.multiarray import array

__all__ = [
    "Writer",
    "MonitorWriter",
    "WebCamMonitorWriter",
    "FileMonitorWriter",
    "FileWriter",
    "ImageWriter",
    "VideoWriter",
]


class Writer(ABC):
    """This class is used to write to a file or to display frames"""

    input_cap: Any
    frame_width: int
    frame_height: int

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


class MonitorWriter(Writer):
    """This class is used to display frames"""

    window_name: str

    def __init__(self, window_name: str = "Output Image") -> None:
        self.window_name = window_name
        super().__init__()

    def write(self, frame) -> None:
        """Displays the frame in a window"""
        cv.imshow(self.window_name, frame)

    def close(self) -> None:
        """Closes input_cap and destorys alla windows"""
        super().close()
        cv.destroyAllWindows()

    def wait_key_image(self):
        """Returns condition to wait for a key and display an image"""
        return cv.waitKey(0) & 0xFF == ord("q")

    def wait_key_video(self):
        """Returns condition to wait for a key and display a video"""
        return cv.waitKey(1) & 0xFF == ord("q")


class WebCamMonitorWriter(MonitorWriter):
    """This class is used if your desired input is the webcam and you want to display the output in a window"""

    def init_writer(self) -> None:
        """Init the input_cap getting frames from the webcam"""
        self.input_cap = cv.VideoCapture(0)
        super().init_writer()


class FileMonitorWriter(MonitorWriter):
    """This class is used if your desired input is a file and you want to display the output in a window"""

    file_in: str

    def __init__(self, file_in: str, window_name: str = "Output Image") -> None:
        self.file_in = file_in
        super().__init__(window_name)

    def init_writer(self) -> None:
        """init the input_cap getting frames from file_in"""
        self.input_cap = cv.VideoCapture(self.file_in)
        super().init_writer()


class FileToFileWriter(Writer):
    """This class is used if your desired input is a file and you want to write the output to a file"""

    file_in: str
    file_out: str

    def __init__(self, file_in: str, file_out: str = "") -> None:
        self.file_in = file_in
        self.file_out = file_out
        super().__init__()

    def change_file(self, file_in: str, file_out: str) -> None:
        """Chenge file_in and file_out"""
        self.file_in = file_in
        if not file_out:
            self.file_out = f"OUT_{file_in}"
        else:
            self.file_out = file_out


class FileToImageWriter(FileToFileWriter):
    """This class is used if your desired input is a file and you want to write the output to a file as an image"""

    def init_writer(self) -> None:
        self.input_cap = cv.VideoCapture(self.file_in)
        super().init_writer()

    def write(self, frame) -> None:
        """Writes the frame to a file as an image"""
        cv.imwrite(self.file_out, frame)


class FileToVideoWriter(FileToFileWriter):
    """This class is used if your desired input is a file and you want to write the output to a file as a video"""

    out: Any
    fps: int

    def init_writer(self) -> None:
        self.input_cap = cv.VideoCapture(self.file_in)
        super().init_writer()
        self.fps = self.input_cap.get(cv.CAP_PROP_FPS)
        four_cc = cv.VideoWriter_fourcc(*"DIVX")
        self.out = cv.VideoWriter(
            self.file_out, four_cc, self.fps, (self.frame_width, self.frame_height)
        )

    def write(self, frame) -> None:
        """Writes the frame appending it to a file as a video"""
        self.out.write(frame)

    def close(self) -> None:
        """Closes the out and the input_cap"""
        self.out.release()
        super().close()
