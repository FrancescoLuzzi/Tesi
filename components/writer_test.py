from os import write
from models import MultipleDetectionsModel, SingleDetectionModel
from painter import SimplePainter, PrivatePainter
from writer import FileMonitorWriter, WebCamMonitorWriter, VideoWriter, FileWriter
from Exceptions import CapNotOpenedException

if __name__ == "__main__":
    modello = [
        ".\\mpi\\pose_iter_160000.caffemodel",
        ".\\mpi\\pose_deploy_linevec_faster_4_stages.prototxt",
    ]
    file_name = "./TEST_IMAGES/group.jpg"
    model = MultipleDetectionsModel(modello[0], modello[1])
    model.init_net()
    painter = PrivatePainter()
    try:
        writer = FileMonitorWriter(file_name)
    except CapNotOpenedException:
        print("error opening CAP")
        exit(-1)
    writer.init_writer()
    frame_width, frame_height = writer.get_frame_props()
    while writer.is_open():
        ret, frame = writer.read()
        if ret:
            out = model.find_detections(frame, frame_width, frame_height)
            painter.paint_frame(frame, out)
            writer.write(frame)
            if writer.wait_key_image():
                break
        else:
            break
    writer.close()
