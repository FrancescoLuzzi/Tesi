import components.models as models
import components.painters as painters
import components.writers as writers
from components.utils import check_file_type
from .basic_runners import run_simulation_to_file
from os import path, mkdir, listdir
import logging


def dir_run(
    model: models.Model,
    painter: painters.Painter,
    dir_in: str,
    dir_out: str,
) -> None:
    """
    Given a model, a painter and a dir_in path and a dir_out, loops over all files in dir_in and for all images and video,\n
    depending on this last one extension, gets image/video input and writes the output to a file in dir_out as an image/video.\n
    """
    if not path.isdir(dir_in):
        logging.error(f"{dir_in} is not a directory!")
        exit(-1)
    if not dir_out:
        logging.error("Argument -o/--videoOut is MISSING")
        exit(-1)
    if not path.isdir(dir_out):
        mkdir(dir_out)
    writer = None
    img_writer = writers.FileToImageWriter("")
    video_writer = writers.FileToVideoWriter("")
    # loop over all files in directory
    for filename in listdir(dir_in):
        f = path.join(dir_in, filename)
        fout = path.join(dir_out, f"OUT{filename}")
        # checking if f is a file
        if path.isfile(f):
            file_type = check_file_type(f)
            if not file_type:
                logging.error(f"{f} doesen't have the correct video or image format")
                continue
            logging.debug(f"Currently working on {f}")
            writer = img_writer if file_type == "image" else video_writer
            writer.change_file(f, fout)
            writer.init_writer()
            run_simulation_to_file(model, writer, painter)
            writer.close()
            logging.info(f"Detection on {f} successfully completed!")
