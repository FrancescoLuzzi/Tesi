import components.models as models
import components.painters as painters
import components.writers as writers
from components.utils import check_file_type
from .basic_runners import run_simulation_to_monitor
from os import path
import logging


def file_run_monitor(
    model: models.Model,
    painter: painters.Painter,
    file_input: str,
) -> None:
    """
    Given a model, a painter and a file_input path, depending on this last one extension, gets image/video input\n
    and displays the output to a window as an image/video.\n
    """
    if not path.isfile(file_input):
        logging.error("The file doesen't exists. Check file_input name!")
        exit()
    input_type = check_file_type(file_input)
    if not input_type:
        logging.error("File_input's file extension is not for videos or images!")
        exit()
    writer = writers.FileMonitorWriter(file_input)
    writer.init_writer()
    waiter = writer.wait_key_image if input_type == "image" else writer.wait_key_video
    run_simulation_to_monitor(model, writer, painter, waiter)
    writer.close()
