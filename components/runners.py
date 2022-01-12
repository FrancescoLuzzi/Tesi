from types import FunctionType
from components.models import Model
from components.writers import FileWriter, MonitorWriter
from components.painters import Painter


def run_simulation_to_file(model: Model, writer: FileWriter, painter: Painter) -> None:
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
    model: Model, writer: MonitorWriter, painter: Painter, wait: FunctionType
) -> None:
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
