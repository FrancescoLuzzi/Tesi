import components.models as models
import components.painters as painters
import components.writers as writers
from components.utils import check_file_type
from .basic_runners import run_simulation_to_file
from os import path
import logging


def file_run(
    model: models.Model,
    painter: painters.Painter,
    file_input: str,
    file_output: str,
) -> None:
    """
    Given a model, a painter and a file_input path, depending on the last one's extension, gets image/video input\n
    and writes the output to a file as an image/video.\n
    """
    if not path.isfile(file_input):
        logging.error("The file doesen't exists. Check file_input name!")
        exit(-1)
    input_type = check_file_type(file_input)
    if not input_type:
        logging.error("File_input's file extension is not for videos or images!")
        exit(-1)

    output_type = check_file_type(file_output)
    if output_type != input_type:
        logging.warning(
            f"Output file type is {output_type=} not consistent with the {input_type=}.\nChanged it to the right extension.\n"
        )
        output_type = ""
    if not output_type:
        _, ext = path.splitext(file_input)
        file_output, _ = path.splitext(file_output)
        file_output = file_output + ext

    writer = (
        writers.FileToImageWriter(file_input, file_output)
        if input_type == "image"
        else writers.FileToVideoWriter(file_input, file_output)
    )

    writer.init_writer()
    run_simulation_to_file(model, writer, painter)
    writer.close()
    logging.info(f"{file_input} as been elaborated, {file_output=}")
