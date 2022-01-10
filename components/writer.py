from abc import ABC, abstractmethod
from typing import Any
import cv2 as cv
import components.Exceptions

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
    cap: Any
    frame_width: int
    frame_height: int

    def init_writer(self) -> None:
        self.frame_width = int(self.cap.get(cv.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv.CAP_PROP_FRAME_HEIGHT))
        if not self.cap.isOpened():
            print("Error opening video stream or file")
            raise components.Exceptions.CapNotOpenedException

    def close(self) -> None:
        self.cap.release()

    def read(self) -> tuple[bool, array]:
        return self.cap.read()

    def is_open(self) -> bool:
        return self.cap.isOpened()

    def get_frame_props(self) -> tuple[int, int]:
        return self.frame_width, self.frame_height

    @abstractmethod
    def write(self, frame) -> None:
        pass


class MonitorWriter(Writer):
    window_name: str

    def __init__(self, window_name: str = "Output Image") -> None:
        self.window_name = window_name
        super().__init__()

    def write(self, frame) -> None:
        cv.imshow(self.window_name, frame)

    def close(self) -> None:
        super().close()
        cv.destroyAllWindows()

    def wait_key_image(self):
        return cv.waitKey(0) & 0xFF == ord("q")

    def wait_key_video(self):
        return cv.waitKey(1) & 0xFF == ord("q")


class WebCamMonitorWriter(MonitorWriter):
    def init_writer(self) -> None:
        self.cap = cv.VideoCapture(0)
        super().init_writer()


class FileMonitorWriter(MonitorWriter):
    file_in: str

    def __init__(self, file_in: str, window_name: str = "Output Image") -> None:
        self.file_in = file_in
        super().__init__(window_name)

    def init_writer(self) -> None:
        self.cap = cv.VideoCapture(self.file_in)
        super().init_writer()


class FileWriter(Writer):
    file_in: str
    file_out: str

    def __init__(self, file_in: str, file_out: str = "") -> None:
        self.file_in = file_in
        self.file_out = file_out
        super().__init__()

    def change_file(self, file_in: str, file_out: str) -> None:
        self.file_in = file_in
        if not file_out:
            self.file_out = f"OUT_{file_in}"
        else:
            self.file_out = file_out


class ImageWriter(FileWriter):
    def init_writer(self) -> None:
        self.cap = cv.VideoCapture(self.file_in)
        super().init_writer()

    def write(self, frame) -> None:
        cv.imwrite(self.file_out, frame)


class VideoWriter(FileWriter):
    out: Any
    fps: int

    def init_writer(self) -> None:
        self.cap = cv.VideoCapture(self.file_in)
        super().init_writer()
        self.fps = self.cap.get(cv.CAP_PROP_FPS)
        four_cc = cv.VideoWriter_fourcc(*"DIVX")
        self.out = cv.VideoWriter(
            self.file_out, four_cc, self.fps, (self.frame_width, self.frame_height)
        )

    def write(self, frame) -> None:
        self.out.write(frame)

    def close(self) -> None:
        self.out.release()
        super().close()
