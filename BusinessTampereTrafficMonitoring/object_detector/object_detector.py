import time
from collections import deque
from datetime import datetime

import cv2
import numpy as np
from tf2_yolov4.anchors import YOLOV4_ANCHORS
from tf2_yolov4.model import YOLOv4

from BusinessTampereTrafficMonitoring.tools.geometry import point_inside
from BusinessTampereTrafficMonitoring.traffic_lights.status import Status
import BusinessTampereTrafficMonitoring.iot_ticket.client as iot

ALLOWED_CLASSES = [1, 2, 3, 5, 7]


def lower_center_from_bbox(bbox):
    return ((bbox[0]+bbox[2]) / 2, bbox[1])


def find_nearest(array, value):
    """
    Utility function for finding array element with closest value to value-parameter
    """
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]


class ObjectDetector:
    def __init__(self, video_location, config):
        self.config = config

        # Initializing cache-dict and timestamp-deque for frame storage
        self.cache = dict()
        self.timestamps = deque([])

        self.cap = cv2.VideoCapture(video_location)


        if not self.cap.isOpened():
            print('Cannot open stream')
            exit(-1)

        # Initializing required constants
        self.WIDTH = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.HEIGHT = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Initializing model parameters
        self.model = YOLOv4(
            input_shape=(self.HEIGHT, self.WIDTH, 3),
            anchors=YOLOV4_ANCHORS,
            num_classes=80,
            training=False,
            yolo_max_boxes=50,
            yolo_iou_threshold=0.5,
            yolo_score_threshold=0.5,
        )

        # Loading the pretrained weights to the model
        self.model.load_weights('yolov4.h5')

    def store_frame(self, timestamp, frame):
        """
        Function for storing a time-stamp associated frame to cache
        Inputs:
            time: UNIX time stamp
            frame: frame read using CV2, no operations done prior
        """
        if len(self.timestamps) == 200:
            self.cache.pop(self.timestamps[0])
            self.timestamps.popleft()
        self.cache[timestamp] = frame
        self.timestamps.append(timestamp)

    def get_frame(self, timestamp=None):
        if timestamp is None:
            timestamp = time.time()
        return self.cache[find_nearest(self.timestamps, timestamp)]

    def detect_by_signal_group_and_time(self, intersection, sgroup, epoch_time, light_status):
        """
        The bread and butter of the program:
            Function which can be called from the traffic lights API.
            Matches the given parameters to specific frames.
            Calls necessary utility functions to transform given parameters to usable formats.
            Does operations on the frames to extract vehicle counts per lane and stores the count, timestamp and lane.
        """
        print(f"[{datetime.fromtimestamp(epoch_time):%H:%M:%S}] light for {sgroup} changed to {light_status}")
        # light changes from red to green are not handled (yet)
        if light_status == Status.GREEN:
            return

        lanes = self.config["lanes"]
        lanes = [lane for lane in lanes if sgroup in lane["signal_groups"]]

        if not lanes:
            # No lanes for this signal group are monitored
            return

        frame_at_the_time = self.get_frame(epoch_time)
        prediction_frame = np.expand_dims(frame_at_the_time, axis=0) / 255.0
        boxes, scores, classes, detections = self.model.predict(prediction_frame)

        boxes = boxes[0] * [self.WIDTH, self.HEIGHT, self.WIDTH, self.HEIGHT]
        scores = scores[0]
        classes = classes[0].astype(int)

        points = []
        for box, score, cls in zip(boxes, scores, classes):
            if cls in ALLOWED_CLASSES:
                points.append(lower_center_from_bbox(box))

        for lane in lanes:
            lane["cars"] = 0
        # Count detected cars by lane
        # TODO: this can be optimized
        for point in points:
            for lane in lanes:
                # point_inside() expects list of tuples, but vertices
                # that are read from json are lists
                vertices = [tuple(xy) for xy in lane["vertices"]]
                if point_inside(point, vertices):
                    lane["cars"] += 1
                    break

        for lane in lanes:
            lane_id = lane["lane"]
            cars = lane["cars"]
            print(f"[{datetime.fromtimestamp(epoch_time):%H:%M:%S}] {cars} cars detected on lane {lane_id}")
            iot.client.post_car_count('92311e32ea3f4619ac69df3c95c3ef0a', lane_id, cars, epoch_time)

        # vehicle_count = #needs implementing

        # TODO: Lane matching and updating database or cache with timestamp, lane and vehicle count
        # data = '{"lane_id" : lane, "traffic_time" : epoch_time, "car_amount" : vehicle_count }

    def read_stream(self):
        """
        Function for reading frames from the stream, runs all the time. Does no operations on the frames.
        """
        while True:
            success = False;
            while success != True:
                success, frame = self.cap.read()
                time.sleep(0.1)
            self.store_frame(time.time(), frame)
            time.sleep(1)
