import os
from datetime import datetime

import cv2
import numpy as np
from tf2_yolov4.anchors import YOLOV4_ANCHORS
from tf2_yolov4.model import YOLOv4

from BusinessTampereTrafficMonitoring.iot_ticket.client import client as iot_client
from BusinessTampereTrafficMonitoring.stream_reader.stream_reader import StreamReader
from BusinessTampereTrafficMonitoring.tools.geometry import point_inside
from BusinessTampereTrafficMonitoring.traffic_lights.status import Status

ALLOWED_CLASSES = [1, 2, 3, 5, 7]


def lower_center_from_bbox(bbox):
    return (bbox[0] + bbox[2]) / 2, bbox[3]


class ObjectDetector:
    def __init__(self, video_location, config):
        self.config = config

        self.stream_reader = StreamReader(video_location)

        # Initializing required constants
        self.WIDTH, self.HEIGHT = self.stream_reader.get_constants()

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

    def detect_by_signal_group_and_time(self, intersection, sgroup, epoch_time, light_status):
        """
        The bread and butter of the program:
            Function which can be called from the traffic lights API.
            Matches the given parameters to specific frames.
            Calls necessary utility functions to transform given parameters to usable formats.
            Does operations on the frames to extract vehicle counts per lane and stores the count, timestamp and lane.
        # Parameters:
          intersection: Intersection id, for example "TRE401" (str)
          sgroup: Signal group id, for example "A" or "RV1" (str)
          epoch_time: Epoch time in seconds (float)
          light_status: Current status of the traffic light (Status)
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

        frame_at_the_time = self.stream_reader.get_frame(epoch_time)
        points, boxes = self.detect(frame_at_the_time)
        lanes = self.process_detections(points, lanes)
        vehicle_count = self.post_detections(lanes, epoch_time)

        # TODO: put this behind a flag or something
        self.save_image_for_debugging(frame_at_the_time, sgroup, vehicle_count, boxes, points, epoch_time)

    def detect(self, frame):
        prediction_frame = np.expand_dims(frame, axis=0) / 255.0
        boxes, scores, classes, detections = self.model.predict(prediction_frame)
        boxes = boxes[0] * [self.WIDTH, self.HEIGHT, self.WIDTH, self.HEIGHT]
        scores = scores[0]
        classes = classes[0].astype(int)
        points = []
        for box, score, cls in zip(boxes, scores, classes):
            if cls in ALLOWED_CLASSES:
                points.append(lower_center_from_bbox(box))
        return points, boxes

    @staticmethod
    def process_detections(points, lanes):
        for lane in lanes:
            lane["cars"] = 0
        # Count detected cars by lane
        # TODO: this can be optimized
        for point in points:
            # point_inside() expects list of tuples, but vertices
            # that are read from json are lists
            for lane in lanes:
                vertices = [tuple(xy) for xy in lane["vertices"]]
                if point_inside(point, vertices):
                    lane["cars"] += 1
                    break
        return lanes

    @staticmethod
    def post_detections(lanes, epoch_time):
        vehicle_count = 0
        for lane in lanes:
            lane_id = lane["lane"]
            cars = lane["cars"]
            device_id = lane["camera_id"]
            print(f"[{datetime.fromtimestamp(epoch_time):%H:%M:%S}] {cars} cars detected on lane {lane_id}")
            iot_client.post_car_count(
                device_id=device_id,
                lane=lane_id,
                count=cars,
                timestamp=epoch_time)
            vehicle_count += cars
        return vehicle_count

    def save_image_for_debugging(self, img, sgroup, vehicle_count, boxes, detections, timestamp):
        """
        Draws detected objects in a frame and saves the image on disk.
        # Parameters:
          img: Numpy array representing the image (numpy.ndarray)
          sgroup: Signal group id, for example "A" or "RV1" (str)
          vehicle_count: Number of vehicles detected (int)
          boxes: List of boxes with four coordinates (x0, y0, x1, y1) (List[float])
          points: List of detections to be drawn in the image. (List[Tuple[float, float]])
          timestamp: Epoch time in seconds (float)
        """
        directory = os.path.abspath("./frames")
        if not os.path.exists(directory):
            os.makedirs(directory)

        lanes = self.config["lanes"]
        for lane in lanes:
            vertices = [tuple(xy) for xy in lane["vertices"]]
            color = (255, 0, 255)  # in BGR (not RGB)
            if sgroup in lane["signal_groups"]:
                thickness = 3
            else:
                thickness = 1
            for start_point, end_point in zip(vertices, vertices[1:] + [vertices[0]]):
                img = cv2.line(img, start_point, end_point, color, thickness)

        color = (0, 255, 255)  # in BGR (not RGB)
        for x0, y0, x1, y1 in boxes:
            start_point = (round(x0), round(y0))
            end_point = (round(x1), round(y1))
            img = cv2.rectangle(img, start_point, end_point, color, 2)

        radius = 6
        color = (0, 0, 255)  # in BGR (not RGB)
        for x, y in detections:
            center = (round(x), round(y))
            img = cv2.circle(img, center, radius, color, 3)

        file_name = f"{datetime.fromtimestamp(timestamp):%H%M%S}-{vehicle_count}_vehicles_on_lanes.jpg"
        file_path = os.path.join(directory, file_name)

        if cv2.imwrite(file_path, img):
            print(f"Saved detections to {file_path}")
        else:
            print(f"Failed to save file {file_path}")
