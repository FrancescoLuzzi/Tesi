import cv2 as cv
from .writer import Writer, Any


class FileToFileWriter(Writer):
    """This class is used if your desired input is a file and you want to write the output to a file"""

    file_in: str = ""
    file_out: str = ""

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

    out: Any = None
    fps: int = 0

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
        self.out = None
        super().close()
