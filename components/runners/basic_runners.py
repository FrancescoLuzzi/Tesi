from types import FunctionType
import components.models as models
import components.painters as painters
import components.writers as writers


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
