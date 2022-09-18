from typing import List, Dict
import cv2 as cv
from .model import Model, get_framerate

class SingleDetectionModel(Model):
    """Model for single person detection"""

    @get_framerate
    def find_detections(self, frame, frame_width: int, frame_height: int) -> List[Dict]:
        """Finds the keypoints o a single person in a frame, it returns a List[Dict]\n
        composed by [{ keypoint_id: (x,y) , keypoint_id: (x,y)}, ...]"""
        self.in_height = 368
        self.in_width = int((self.in_height / frame_height) * frame_width)

        in_blob = cv.dnn.blobFromImage(
            frame,
            1.0 / 255,
            (self.in_width, self.in_height),
            (0, 0, 0),
            swapRB=False,
            crop=False,
        )
        self.net.setInput(in_blob)
        output = self.net.forward()
        H = output.shape[2]
        W = output.shape[3]
        # Empty list to store the detected keypoints
        points = {}

        for i in range(self.n_points):

            # confidence map of corresponding body's part.
            prob_map = output[0, i, :, :]

            # Find global maxima of the prob_map.
            _, prob, _, point = cv.minMaxLoc(prob_map)

            # Scale the point to fit on the origin_al image
            x = int((frame_width * point[0]) / W)
            y = int((frame_height * point[1]) / H)

            if prob > self.threshold:
                points[i] = (x, y)
                # print(f"{self.keypoints_mapping[i]} detected point: [{x},{y}]")
        output = []
        for start, end in self.pose_pairs:
            if points.get(start) and points.get(end):
                output.append({start: points[start], end: points[end]})

        return output