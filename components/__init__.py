from .models import model_factory
from .painters import painter_factory
from .runners import dir_run, file_run, file_run_monitor, webcam_run_monitor
from colorama import init

init()
__version__ = "1.0"
