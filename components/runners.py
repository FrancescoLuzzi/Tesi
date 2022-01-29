from types import FunctionType
from . import models, writers, painters, colored_output, file_check
from os import path, mkdir, listdir

__all__ = ["dir_run", "file_run_monitor", "file_run", "webcam_run_monitor"]


def run_simulation_to_file(
    model: models.Model, writer: writers.FileToFileWriter, painter: painters.Painter
) -> None:
    """Given a painter and initialized model and writer this runs the detection and saves the result on the output file"""
    frame_width, frame_height = writer.get_frame_props()
    while writer.is_open():
        ret, frame = writer.read()
        if ret:
            out = model.find_detections(frame, frame_width, frame_height)
            painter.paint_frame(frame, out)
            writer.write(frame)
        else:
            break


def run_simulation_to_monitor(
    model: models.Model,
    writer: writers.MonitorWriter,
    painter: painters.Painter,
    wait: FunctionType,
) -> None:
    """
    Given a painter and initialized model and writer this runs the detection and displays it on a monitor.\n
    The requested wait, is a function that calls a condition (MonitorWriter.wait_key_video or MonitorWriter.wait_key_image)"""
    frame_width, frame_height = writer.get_frame_props()
    while writer.is_open():
        ret, frame = writer.read()
        if ret:
            out = model.find_detections(frame, frame_width, frame_height)
            painter.paint_frame(frame, out)
            writer.write(frame)
            if wait():
                break
        else:
            break


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
        colored_output.print_error(f"{dir_in} is not a directory!")
        exit(-1)
    if not dir_out:
        colored_output.print_error("Argument -o/--videoOut is MISSING")
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
            file_type = file_check.check_file_type(f)
            if not file_type:
                colored_output.print_error(
                    f"{f} doesen't have the correct video or image format"
                )
                continue
            colored_output.print_info(f"Currently working on {f}")
            writer = img_writer if file_type == "image" else video_writer
            writer.change_file(f, fout)
            writer.init_writer()
            run_simulation_to_file(model, writer, painter)
            writer.close()
            colored_output.print_ok(f"Detection on {f} successfully completed!")


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
        colored_output.print_error("The file doesen't exists. Check file_input name!")
        exit(-1)
    input_type = file_check.check_file_type(file_input)
    if not input_type:
        colored_output.print_error(
            "File_input's file extension is not for videos or images!"
        )
        exit(-1)

    output_type = file_check.check_file_type(file_output)
    if output_type != input_type:
        colored_output.print_info(
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
    colored_output.print_ok(f"{file_input} as been elaborated, {file_output=}")


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
        colored_output.print_error("The file doesen't exists. Check file_input name!")
        exit()
    input_type = file_check.check_file_type(file_input)
    if not input_type:
        colored_output.print_error(
            "File_input's file extension is not for videos or images!"
        )
        exit()
    writer = writers.FileMonitorWriter(file_input)
    writer.init_writer()
    waiter = writer.wait_key_image if input_type == "image" else writer.wait_key_video
    run_simulation_to_monitor(model, writer, painter, waiter)
    writer.close()


def webcam_run_monitor(model: models.Model, painter: painters.Painter) -> None:
    """
    Given a model and a painter get video input from webcam and displays the output to a window.
    """
    writer = writers.WebCamMonitorWriter()
    writer.init_writer()
    run_simulation_to_monitor(model, writer, painter, writer.wait_key_video)
    writer.close()
