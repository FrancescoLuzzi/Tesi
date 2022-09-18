import cv2 as cv
from .writer import Writer


class MonitorWriter(Writer):
    """This class is used to display frames"""

    window_name: str = ""

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

    file_in: str = ""

    def __init__(self, file_in: str, window_name: str = "Output Image") -> None:
        self.file_in = file_in
        super().__init__(window_name)

    def init_writer(self) -> None:
        """init the input_cap getting frames from file_in"""
        self.input_cap = cv.VideoCapture(self.file_in)
        super().init_writer()
