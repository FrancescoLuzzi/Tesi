import cv2 as cv
from .writer import Writer, Any


class CapToFileWriter(Writer):
    """This class is used if your desired input cv2.Cap instance and you want to write the output to a file"""

    file_out: str = ""

    def __init__(self, input_cap: Any = None, file_out: str = "") -> None:
        self.input_cap = input_cap
        self.file_out = file_out
        super().__init__()

    def set_input_cap(self, input_cap: Any):
        self.input_cap = input_cap

    def set_file_out_name(self, file_out: str):
        self.file_out = file_out


class CapToImageWriter(CapToFileWriter):
    """This class is used if your desired input is a file and you want to write the output to a file as an image"""

    def write(self, frame) -> None:
        """Writes the frame to a file as an image"""
        cv.imwrite(self.file_out, frame)


class CapToVideoWriter(CapToFileWriter):
    """This class is used if your desired input is a file and you want to write the output to a file as a video"""

    out: Any = None
    fps: int = 0

    def init_writer(self) -> None:
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
        self.out = None
        super().close()
