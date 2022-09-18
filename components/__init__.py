from .models import model_factory
from .painters import painter_factory
from .runners import dir_run, file_run, file_run_monitor, webcam_run_monitor
from .writers import CapToVideoWriter, CapToImageWriter
from colorama import init

from .utils.logger import init_logger

init_logger(enable_stream=True)

__version__ = "3.0"
