import cv2 as cv
from models import SingleDetectionModel, MultipleDetectionsModel

if __name__ == "__main__":
    cap = cv.VideoCapture("./TEST_IMAGES/group.jpg")
    modello = [
        ".\\mpi\\pose_iter_160000.caffemodel",
        ".\\mpi\\pose_deploy_linevec_faster_4_stages.prototxt",
    ]
    frame_width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    model = MultipleDetectionsModel(modello[0], modello[1])
    model.init_net()
    _, frame = cap.read()
    out = model.find_detections(frame, frame_width, frame_height)
    print(out)
