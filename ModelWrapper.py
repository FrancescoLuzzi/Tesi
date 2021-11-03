import numpy as np
import cv2 as cv
import os
import time


class Wrapper:
    r"""
    Questa classe sara il wrapper e l'utilizzatore del modello MPI di OpenPose
    """

    def __init__(self, file_path, model_path, proto_path, output_path, multiple):
        if file_path != "0" and os.path.isfile(file_path):
            self.file_path = file_path
        else:
            self.file_path = 0
        self.multiple = multiple
        self.output_path = output_path
        self.model_path = model_path
        self.proto_path = proto_path
        self.oldpars = []
        # threshold to detect the keypoint

        # if threshold==0.33 in image_left/000586 bin keypoints are not detected
        self.threshold = 0.10
        # self.threshold = 0.33
        # number of points on PAF
        self.n_interp_samples = 10
        # threshold for paf score
        self.paf_score_th = 0.12
        # threshold for pair to get accepted
        self.conf_th = 0.8
        self.colors = [
            [255, 200, 100],
            [0, 100, 255],
            [0, 255, 255],
            [0, 255, 0],
            [0, 100, 255],
            [0, 255, 255],
            [0, 255, 0],
            [0, 100, 255],
            [255, 0, 255],
            [0, 0, 255],
            [255, 0, 0],
            [255, 0, 255],
            [0, 0, 255],
            [255, 0, 0],
            [0, 0, 128],
        ]
        self.keypoints_mapping = [
            "Head",
            "Neck",
            "R-Sho",
            "R-Elb",
            "R-Wr",
            "L-Sho",
            "L-Elb",
            "L-Wr",
            "R-Hip",
            "R-Knee",
            "R-Ank",
            "L-Hip",
            "L-Knee",
            "L-Ank",
            "Chest",
        ]
        # number of points detected 15 for MPI
        self.n_points = 15
        self.map_idx = [
            [16, 17],
            [18, 19],
            [20, 21],
            [22, 23],
            [24, 25],
            [26, 27],
            [28, 29],
            [30, 31],
            [32, 33],
            [34, 35],
            [36, 37],
            [38, 39],
            [40, 41],
            [42, 43],
        ]
        self.POSE_PAIRS = [
            [0, 1],
            [1, 2],
            [2, 3],
            [3, 4],
            [1, 5],
            [5, 6],
            [6, 7],
            [1, 14],
            [14, 8],
            [8, 9],
            [9, 10],
            [14, 11],
            [11, 12],
            [12, 13],
        ]
        """
        #this is for computing resizes with gpu
        self.gpu_frame_paf_a=cv.cuda_GpuMat()
        self.gpu_frame_paf_b=cv.cuda_GpuMat()
        self.gpu_frame_prob_map=cv.cuda_GpuMat()
        """

    """
    get all keypoints present in the image from the probability map
    """

    def init_net(self, gpu):
        self.net = cv.dnn.readNetFromCaffe(self.proto_path, self.model_path)
        if gpu:
            print("gpu Accelerated")
            self.net.setPreferableBackend(cv.dnn.DNN_BACKEND_CUDA)
            self.net.setPreferableTarget(cv.dnn.DNN_TARGET_CUDA)

    def get_keypoints(self, prob_map):
        # f = open("probMaps.txt", "a")
        # f.write("#########")
        # np.savetxt(f, prob_map, fmt="%.2f")
        # f.close()

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
            # to containt a valid keypoint
            keypoints.append(max_loc + (prob_map[max_loc[1], max_loc[0]],))
        return keypoints

    """
    Check every pair of keypoints from 2 candidates, calculate the distance between them and their PAF value,
    the pair that has the highest PAF value is from the same person
    """

    def get_valid_pairs(self, output):
        valid_pairs = []
        invalid_pairs = []
        # loop for every POSE_PAIR
        for k in range(self.n_points - 1):
            # A->B constitute a limb
            paf_a = output[0, self.map_idx[k][0], :, :]
            paf_b = output[0, self.map_idx[k][1], :, :]
            """
            #this is for computing resizes with gpu
            self.gpu_frame_paf_a.upload(paf_a)
            self.gpu_frame_paf_b.upload(paf_b)
            self.gpu_frame_paf_a = cv.cuda.resize(self.gpu_frame_paf_a, (self.frame_width, self.frame_height))
            self.gpu_frame_paf_b = cv.cuda.resize(self.gpu_frame_paf_b, (self.frame_width, self.frame_height))
            paf_b = self.gpu_frame_paf_b.download()
            paf_a=self.gpu_frame_paf_a.download()"""
            paf_a = cv.resize(paf_a, (self.frame_width, self.frame_height))
            paf_b = cv.resize(paf_b, (self.frame_width, self.frame_height))
            # Find the keypoints for the first and second limb
            # all keypoints for the POSE_PAIR[k][0] keypoint (0=Head,...)
            cand_a = self.detected_keypoints[self.POSE_PAIRS[k][0]]
            # all keypoints for the POSE_PAIR[k][1] keypoint (1=Neck,...)
            cand_b = self.detected_keypoints[self.POSE_PAIRS[k][1]]
            n_a = len(cand_a)
            n_b = len(cand_b)

            # If keypoints for the joint-pair is detected
            # check every joint in cand_a with every joint in cand_b
            # Calculate the distance vector between the two joints
            # Find the PAF values at a set of interpolated points between the joints
            # Use the above formula to compute a score to mark the connection valid

            if n_a != 0 and n_b != 0:
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
                        if norm:
                            d_ij = d_ij / norm
                        else:
                            continue
                        # Create an array of 10 interpolated points on the line joining the two keypoints.
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
                        # Find avg_PAF_score as the midpoint of all the PAF_scores
                        paf_scores = np.dot(paf_interp, d_ij)
                        avg_paf_score = sum(paf_scores) / len(paf_scores)

                        # Check if the connection is valid
                        # If the fraction of interpolated vectors aligned with PAF is higher then threshold -> Valid Pair
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

                # Append the detected connections to the global list
                valid_pairs.append(valid_pair)
            else:  # If no keypoints are detected
                # print("No Connection : k = {}".format(k))
                invalid_pairs.append(k)
                valid_pairs.append([])
        return valid_pairs, invalid_pairs

    """
    This function creates a list of keypoints belonging to each person
    for each detected valid pair, it assigns the joint(s) to a person
    """

    def get_personwise_keypoints(self, valid_pairs, invalid_pairs):
        # the last number in each row is the overall score
        # 0 rows, self.n_points+1 cols
        personwise_keypoints = -1 * np.ones((0, (self.n_points + 1)))

        for k in range(self.n_points - 1):
            if k not in invalid_pairs:
                part_As = valid_pairs[k][:, 0]
                part_Bs = valid_pairs[k][:, 1]
                index_a, index_b = np.array(self.POSE_PAIRS[k])

                for i in range(len(valid_pairs[k])):
                    found = 0
                    person_idx = -1
                    for j in range(len(personwise_keypoints)):
                        if personwise_keypoints[j][index_a] == part_As[i]:
                            person_idx = j
                            found = 1
                            break
                    # if the part_A is found (Start of the connection) then add part_B to the person
                    if found == 1:
                        personwise_keypoints[person_idx][index_b] = part_Bs[i]
                        personwise_keypoints[person_idx][-1] += (
                            self.keypoints_list[part_Bs[i].astype(int), 2]
                            + valid_pairs[k][i][2]
                        )
                    # if find no partA in the person keypoints, add one person
                    elif not found and k < (self.n_points - 1):
                        row = -1 * np.ones((self.n_points + 1))
                        row[index_a] = part_As[i]
                        row[index_b] = part_Bs[i]
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

    """
    Definizione run dell'analisi con differenzazione tra presenza di file di output
    (an_alisi video e creazione di un file di outout) o meno (live feed dalla fotocamera).
    """

    def multiple_detections(self, frame):
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
            """
            #this is for computing resizes with gpu
            self.gpu_frame_prob_map.upload(prob_map)
            self.gpu_frame_prob_map = cv.cuda.resize(self.gpu_frame_prob_map, (frame.shape[1], frame.shape[0]))
            prob_map=self.gpu_frame_prob_map.download()"""
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

        # get vaild_paris from the get_valid_pairs function
        valid_pairs, invalid_pairs = self.get_valid_pairs(output)
        # detect which pair is from the same person
        personwise_keypoints = self.get_personwise_keypoints(valid_pairs, invalid_pairs)

        # display all connections between the keypoints from the same person
        for i in range(self.n_points - 1):
            for n in range(len(personwise_keypoints)):
                index = personwise_keypoints[n][np.array(self.POSE_PAIRS[i])]
                if -1 in index:
                    continue
                B = np.int32(self.keypoints_list[index.astype(int), 0])
                A = np.int32(self.keypoints_list[index.astype(int), 1])
                cv.circle(frame, (B[0], A[0]), 4, self.colors[i], -1, cv.FILLED)
                cv.circle(frame, (B[1], A[1]), 4, self.colors[i], -1, cv.FILLED)
                cv.line(
                    frame, (B[0], A[0]), (B[1], A[1]), self.colors[i], 3, cv.LINE_AA
                )

        # For each person i get the neck,head pair then find the distance between them and
        # the midpoint which will be the center of the circle that covers the face
        """for n in range(len(personwise_keypoints)): 
            index = personwise_keypoints[n][np.array(self.POSE_PAIRS[0])]
            if -1 in index:
                continue
            B = np.int32(self.keypoints_list[index.astype(int), 0])
            A = np.int32(self.keypoints_list[index.astype(int), 1])
            median_x=int(np.absolute(B[0]-B[1])/2+min([B[0],B[1]]))
            median_y=int(np.absolute(A[0]-A[1])/2+min([A[0],A[1]]))
            radius=int(np.sqrt(np.power(B[0]-B[1],2)+np.power(A[0]-A[1],2))*0.6)
            cv.circle(frame, (median_x, median_y), radius, (0, 0, 0), thickness=-1, lineType=cv.FILLED)"""
        return frame

    """
    Get the maxima of the keypoints in the image, hopefully from the same person
    """

    def single_detection(self, frame):
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
        points = []

        for i in range(
            15
        ):  # I want only right shoulder(2), neck(1) and head(0) keypoints

            # confidence map of corresponding body's part.
            prob_map = output[0, i, :, :]

            # Find global maxima of the prob_map.
            _, prob, _, point = cv.minMaxLoc(prob_map)

            # Scale the point to fit on the origin_al image
            x = int((self.frame_width * point[0]) / W)
            y = int((self.frame_height * point[1]) / H)

            if prob > self.threshold:
                points.append((x, y))
                # print(f"{self.keypoints_mapping[i]} detected point: [{x},{y}]")
                cv.circle(
                    frame, (x, y), 3, self.colors[i], thickness=-1, lineType=cv.FILLED
                )
            else:
                # print(f"{self.keypoints_mapping[i]} detected point: None")
                points.append(None)
        # Find median point between neck and head then use the distance between neck and shoulder to
        # estimate the radius of the circle to cover the face in interest
        for x in range(self.n_points - 1):
            par1, par2 = self.POSE_PAIRS[x]
            cv.line(frame, points[par1], points[par2], self.colors[x], 3, cv.LINE_AA)
        """if points[0]!=None and points[1]!=None:
            head_x,head_y=points[0]
            neck_x,neck_y=points[1]
            median_x=int((head_x+neck_x)/2)
            median_y=int((head_y+neck_y)/2)
            radius=int(abs(head_y-neck_y)*0.6)
            self.oldpars=[median_x,median_y,radius]
            cv.circle(frame, (median_x, median_y), radius, (0, 0, 0), thickness=-1, lineType=cv.FILLED)
        elif len(self.oldpars)!=0:
            cv.circle(frame, (self.oldpars[0], self.oldpars[1]), self.oldpars[2], (0, 0, 0), thickness=-1, lineType=cv.FILLED)
        """
        return frame

    """
    Definizione run dell'analisi con differenzazione tra presenza di file di output
    (an_alisi video e creazione di un file di outout) o meno (live feed dalla fotocamera).
    """

    def run_simulation(self):
        cap = ""
        if self.file_path == "0":
            cap = cv.VideoCapture(0)
        else:
            cap = cv.VideoCapture(self.file_path)

        if cap.isOpened() == False:
            print("Error opening video stream or file")
        self.frame_width = int(cap.get(3))
        self.frame_height = int(cap.get(4))
        self.in_height = 368
        self.in_width = int((self.in_height / self.frame_height) * self.frame_width)
        if self.output_path == None:
            self.run_live_feed(cap)
        else:
            self.run_file(cap, self.output_path)

    """
    Se non viene dato in input il path/nome_file_out si avrà la creazione di un_a finestra in cui si vedrà l'output 
    """

    def run_live_feed(self, cap):
        get_frame = None
        if self.multiple == True:
            get_frame = self.multiple_detections
        else:
            get_frame = self.single_detection
        while cap.isOpened():
            # Capture frame-by-frame
            ret, frame = cap.read()
            if ret == True:
                start_time = time.time()
                frame = get_frame(frame)
                print("{:.2f} fps".format(1 / float(time.time() - start_time)))
                cv.imshow("Output-Keypoints", frame)
                # cv.waitKey(1) if you want to reproduce a video smoothly else cv.waitKey(0) for a still image
                if cv.waitKey(0) & 0xFF == ord("q"):
                    break
            else:
                break
        cap.release()
        cv.destroyAllWindows()

    """
    Se viene dato in input path/nome_file_out l'output dell'elaborazione verrà scritto su file definito
    """

    def run_file(self, cap, output_path):
        get_frame = None
        if self.multiple == True:
            get_frame = self.multiple_detections
        else:
            get_frame = self.single_detection
        # out = cv.VideoWriter(output_path, cv.VideoWriter_fourcc(*'DIVX'), 30, (self.frame_width,self.frame_height))
        while cap.isOpened():
            # Capture frame-by-frame
            ret, frame = cap.read()
            if ret == True:
                start_time = time.time()
                frame = get_frame(frame)
                cv.imwrite(output_path, frame)
                print("{:.2f} fps".format(1 / float(time.time() - start_time)))
                # out.write(frame)
            else:
                break
        cap.release()
        # out.release()
