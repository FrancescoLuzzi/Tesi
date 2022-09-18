from models import MultipleDetectionsModel, SingleDetectionModel
import cv2 as cv
from painters import PrivatePainter

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
    painter = PrivatePainter()

    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            out = model.find_detections(frame, frame_width, frame_height)
            painter.paint_frame(frame, out)
            cv.imshow("Output-Keypoints", frame)
            if cv.waitKey(0) & 0xFF == ord("q"):
                break
        else:
            break
    cap.release()
    cv.destroyAllWindows()
