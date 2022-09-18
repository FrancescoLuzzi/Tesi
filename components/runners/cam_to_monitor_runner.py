import components.models as models
import components.painters as painters
import components.writers as writers
from components.utils import file_check
from .basic_runners import run_simulation_to_monitor
import logging


def webcam_run_monitor(model: models.Model, painter: painters.Painter) -> None:
    """
    Given a model and a painter get video input from webcam and displays the output to a window.
    """
    writer = writers.WebCamMonitorWriter()
    writer.init_writer()
    run_simulation_to_monitor(model, writer, painter, writer.wait_key_video)
    writer.close()
