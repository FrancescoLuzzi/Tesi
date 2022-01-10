from abc import ABC, abstractmethod
from typing import Any, List
import numpy as np
from numpy.typing import NDArray
import cv2 as cv
from time import time
from components.BaseData import pose_pairs, paf_idx, n_points, threshold

__all__ = ["Model", "SingleDetectionModel", "MultipleDetectionsModel", "model_factory"]


def get_framerate(func):
    def wrapper(*args, **kwargs) -> None:
        start_time = time()
        frame = func(*args, **kwargs)
        print("{:.2f} fps".format(1 / float(time() - start_time)))
        return frame

    return wrapper


""" This code snippet shows the heatmaps of the paf"""


def show_heatmap(paf, frame) -> None:
    heatmapshow = None
    heatmapshow = cv.normalize(
        paf, heatmapshow, alpha=0, beta=255, norm_type=cv.NORM_MINMAX, dtype=cv.CV_8U
    )
    heatmapshow = cv.applyColorMap(heatmapshow, cv.COLORMAP_HOT)
    cv.imshow("Heatmap", cv.addWeighted(heatmapshow, 0.3, frame, 0.7, 0))
    cv.waitKey(0)


"""this code snippet estrapolates the prob_maps to a file"""


def extrapolate_prob_map(prob_map) -> None:
    with open("probMaps.txt", "a") as f:
        f.write("#########")
        np.savetxt(f, prob_map, fmt="%.2f")


class Model(ABC):

    model_path: str
    proto_path: str
    n_points: int
    threshold: float
    n_points: int
    pose_pairs: list[list[int]]
    net: Any

    def __init__(self, model_path: str, proto_path: str) -> None:
        self.model_path = model_path
        self.proto_path = proto_path

        self.threshold = threshold
        self.n_points = n_points
        self.pose_pairs = pose_pairs

    @abstractmethod
    def find_detections(self, frame, frame_width: int, frame_height: int) -> Any:
        pass

    def init_net(self) -> None:
        self.net = cv.dnn.readNetFromCaffe(self.proto_path, self.model_path)

    def enable_gpu(self) -> None:
        print("gpu Accelerated")
        self.net.setPreferableBackend(cv.dnn.DNN_BACKEND_CUDA)
        self.net.setPreferableTarget(cv.dnn.DNN_TARGET_CUDA)


"""Model for single detection"""


class SingleDetectionModel(Model):
    @get_framerate
    def find_detections(self, frame, frame_width: int, frame_height: int) -> list[dict]:
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


"""Model for multiple detections"""


class MultipleDetectionsModel(Model):

    pose_pairs: List[List[int]]
    paf_idx: List[List[int]]
    n_interp_samples: int
    paf_score_th: float
    conf_th: float

    def __init__(
        self,
        model_path: str,
        proto_path: str,
    ) -> None:
        # number of points on PAF
        self.n_interp_samples = 10
        # threshold for paf score
        self.paf_score_th = 0.12
        # threshold for pair to get accepted
        self.conf_th = 0.8

        self.keypoints_list = np.zeros((0, 3))
        self.paf_idx = paf_idx
        super().__init__(model_path, proto_path)

    """
    get all keypoints present in the image from the probability map
    """

    def get_keypoints(self, prob_map) -> list[tuple[list[int], float]]:
        map_smooth = cv.GaussianBlur(prob_map, (3, 3), sigmaX=0, sigmaY=0)
        map_mask = np.uint8(map_smooth > self.threshold)
        keypoints = []

        # find the contours where the keypoints migth be
        contours, _ = cv.findContours(map_mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

        # for each contour find the maxima, where there is the keypoint
        for cnt in contours:
            blob_mask = np.zeros(map_mask.shape)
            blob_mask = cv.fillConvexPoly(blob_mask, cnt, 1)
            masked_prob_map = map_smooth * blob_mask
            _, _, _, max_loc = cv.minMaxLoc(masked_prob_map)
            # this is a tuple formed by point_x, point_y, probability of that point
            # to contain a valid keypoint
            keypoints.append(max_loc + (prob_map[max_loc[1], max_loc[0]],))
        return keypoints

    """Check every keypoint in cand_a with every keypoint in cand_b
    Calculate the unitary direction vector between the two keypoint
    Find the PAF values at a set of interpolated points between the keypoint
    Dot product between the direction vector and the PAF values to find the value of certainty of that connection.
    Returns the valid connection if true otherwhise np.zeros((0, 3))"""

    def get_valid_pair(self, n_a, n_b, cand_a, cand_b, paf_a, paf_b) -> NDArray:
        valid_pair = np.zeros((0, 3))
        # iterate all keypoints for both joints cand_a and cand_b
        for i in range(n_a):
            max_j = -1
            max_score = -1
            found = 0
            for j in range(n_b):
                # Find d_ij
                d_ij = np.subtract(cand_b[j][:2], cand_a[i][:2])
                norm = np.linalg.norm(d_ij)
                if not norm:
                    continue
                d_ij = d_ij / norm

                # Create an array of n_interp_samples interpolated points on the line joining the two keypoints.
                interp_coord = list(
                    zip(
                        np.linspace(
                            cand_a[i][0],
                            cand_b[j][0],
                            num=self.n_interp_samples,
                        ),
                        np.linspace(
                            cand_a[i][1],
                            cand_b[j][1],
                            num=self.n_interp_samples,
                        ),
                    )
                )
                # Create an array of n_interp_samples probability values of the PAFs in the position of the points that we got beefore.
                paf_interp = []
                for k in range(self.n_interp_samples):
                    paf_interp.append(
                        [
                            paf_a[
                                int(round(interp_coord[k][1])),
                                int(round(interp_coord[k][0])),
                            ],
                            paf_b[
                                int(round(interp_coord[k][1])),
                                int(round(interp_coord[k][0])),
                            ],
                        ]
                    )
                # Check the PAF score of each pair of points, doing the dot product between the PAF and the unit vector giving the direction of the connection
                paf_scores = np.dot(paf_interp, d_ij)
                # Find avg_PAF_score
                avg_paf_score = sum(paf_scores) / len(paf_scores)

                # Check if the connection is valid
                # If the fraction of interpolated vectors that has at least paf_score_th, is higher then threshold -> Valid Pair
                if (
                    len(np.where(paf_scores > self.paf_score_th)[0])
                    / self.n_interp_samples
                ) > self.conf_th and avg_paf_score > max_score:
                    max_j = j
                    max_score = avg_paf_score
                    found = 1
            # Append the connection to the list [[x,y],score]
            if found:
                valid_pair = np.append(
                    valid_pair,
                    [[cand_a[i][3], cand_b[max_j][3], max_score]],
                    axis=0,
                )
        return valid_pair

    """
    Check every pair of keypoints from 2 candidates, calculate the distance between them and their PAF value,
    the pair that has the highest PAF value is from the same person
    """

    def get_valid_pairs(
        self, model_detections, frame_width: int, frame_height: int
    ) -> tuple[list[NDArray], list[int]]:
        valid_pairs = []
        invalid_pairs = []
        # loop for every POSE_PAIR
        for k in range(self.n_points - 1):
            # A->B constitute a limb this the axis inverted
            # to get a point paf value paf[point_y,point_x]
            paf_a = model_detections[0, self.paf_idx[k][0], :, :]
            paf_b = model_detections[0, self.paf_idx[k][1], :, :]
            paf_a = cv.resize(paf_a, (frame_width, frame_height))
            paf_b = cv.resize(paf_b, (frame_width, frame_height))

            # Find the keypoints for the first and second limb
            # all keypoints for the POSE_PAIR[k][0] keypoint (0=Head,...)
            cand_a = self.detected_keypoints[self.pose_pairs[k][0]]
            # all keypoints for the POSE_PAIR[k][1] keypoint (1=Neck,...)
            cand_b = self.detected_keypoints[self.pose_pairs[k][1]]
            n_a = len(cand_a)
            n_b = len(cand_b)

            if n_a != 0 and n_b != 0:
                valid_pair = self.get_valid_pair(n_a, n_b, cand_a, cand_b, paf_a, paf_b)

                # Append the detected connections to the global list
                valid_pairs.append(valid_pair)
            else:  # If no keypoints are detected
                # print("No Connection : k = {}".format(k))
                invalid_pairs.append(k)
                valid_pairs.append([])
        return valid_pairs, invalid_pairs

    """
    Find if part is in personwise_keypoints for its part_indx.
    Returns (indx,True) if found (-1,False) otherwhise
    """

    def find_part(self, part_indx, personwise_keypoints, part) -> tuple[int, bool]:
        for j in range(len(personwise_keypoints)):
            if personwise_keypoints[j][part_indx] == part:
                return (j, True)
        return (-1, False)

    """
    This function creates a list of keypoints belonging to each person
    for each detected valid pair, it assigns the joint(s) to a person
    """

    def get_personwise_keypoints(self, valid_pairs, invalid_pairs) -> NDArray:
        # the last number in each row is the overall score
        # 0 rows, self.n_points+1 cols
        personwise_keypoints = -1 * np.ones((0, (self.n_points + 1)))
        for k in range(self.n_points - 1):
            if k not in invalid_pairs:
                parts_a = valid_pairs[k][:, 0]
                parts_b = valid_pairs[k][:, 1]
                index_a, index_b = np.array(self.pose_pairs[k])

                for i in range(len(valid_pairs[k])):

                    person_idx, found = self.find_part(
                        index_a, personwise_keypoints, parts_a[i]
                    )

                    # if the part_a is found on a person (Start of the connection) then add part_a to that person
                    if found:
                        personwise_keypoints[person_idx][index_b] = parts_b[i]
                        personwise_keypoints[person_idx][-1] += (
                            self.keypoints_list[parts_b[i].astype(int), 2]
                            + valid_pairs[k][i][2]
                        )
                    # if find no part_a in any person keypoints, add one person
                    elif k < (self.n_points - 1):
                        row = -1 * np.ones((self.n_points + 1))
                        row[index_a] = parts_a[i]
                        row[index_b] = parts_b[i]
                        # add the keypoint_scores for the two keypoints and the paf_score
                        row[-1] = (
                            sum(
                                self.keypoints_list[
                                    valid_pairs[k][i, :2].astype(int), 2
                                ]
                            )
                            + valid_pairs[k][i][2]
                        )
                        personwise_keypoints = np.vstack([personwise_keypoints, row])
        return personwise_keypoints

    @get_framerate
    def find_detections(self, frame, frame_width: int, frame_height: int) -> list[dict]:
        self.in_height = 368
        self.in_width = int((self.in_height / frame_height) * frame_width)
        # blob and forwrd to the network
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

        # set up of result points
        self.detected_keypoints = []
        self.keypoints_list = np.zeros((0, 3))
        keypoint_id = 0

        # for each keypoint get the probability map and feed it to the get_keypoints function
        # then add them to an other list as a tuple with it's Id then added to the detected_keypoints

        for part in range(self.n_points):
            prob_map = output[0, part, :, :]
            prob_map = cv.resize(prob_map, (frame.shape[1], frame.shape[0]))
            keypoints = self.get_keypoints(prob_map)
            # print("Keypoints - {} : {}".format(self.keypoints_mapping[part], keypoints))
            keypoints_with_id = []
            for i in range(len(keypoints)):
                # add to the keypoint tuple point_x, point_y, probability the keypoint_id (0=Head,...)
                keypoints_with_id.append(keypoints[i] + (keypoint_id,))
                self.keypoints_list = np.vstack([self.keypoints_list, keypoints[i]])
                keypoint_id += 1
            self.detected_keypoints.append(keypoints_with_id)

        # get vaild_pairs
        valid_pairs, invalid_pairs = self.get_valid_pairs(
            output, frame_width, frame_height
        )
        # detect which pair is from the same person
        personwise_keypoints = self.get_personwise_keypoints(valid_pairs, invalid_pairs)
        output = []
        # display all connections between the keypoints from the same person
        for i in range(self.n_points - 1):
            for n in range(len(personwise_keypoints)):
                person = {}
                index = personwise_keypoints[n][np.array(self.pose_pairs[i])]
                if -1 in index:
                    continue
                # First part of connection
                B = np.int32(self.keypoints_list[index.astype(int), 0])
                # Second part of connection
                A = np.int32(self.keypoints_list[index.astype(int), 1])
                person[self.pose_pairs[i][0]] = (B[0], A[0])
                person[self.pose_pairs[i][1]] = (B[1], A[1])
                output.append(person)
        return output


def model_factory(
    multiple: bool, gpu_enable: bool, model_path: str, proto_path: str
) -> Model:
    model = None
    if multiple:
        model = MultipleDetectionsModel(model_path, proto_path)
    else:
        model = SingleDetectionModel(model_path, proto_path)

    if gpu_enable:
        model.enable_gpu()
    return model