import time
from collections import deque

import cv2
import dateutil.parser as dp
import numpy as np
from tf2_yolov4.anchors import YOLOV4_ANCHORS
from tf2_yolov4.model import YOLOv4

from BusinessTampereTrafficMonitoring.tools.geometry import point_inside


def store_frame(time, frame):
    """
    Function for storing a time-stamp associated frame to cache
    Inputs:
        time: UNIX time stamp
        frame: frame read using CV2, no operations done prior
    """
    if len(timestamps) == 200:
        cache.pop(timestamps[0])
        timestamps.popleft()
    cache[time] = frame
    timestamps.append(time)


def find_nearest(array, value):
    """
    Utility function for finding array element with closest value to value-parameter
    """
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]


def iso_to_unix(iso_time):
    """
    Utility function for converting ISO-8601-formatted timestamp to UNIX time
    """
    parsed_t = dp.parse(iso_time)
    return parsed_t.strftime('%s')


def get_frame(time = time.time()):
    return cache[find_nearest(timestamps, time)]


def detect_by_lane_and_time(intersection, signal_group, ISO_timestamp, light_status):
    """
    The bread and butter of the program:
        Function which can be called from the traffic lights API.
        Matches the given parameters to specific frames.
        Calls necessary utility functions to transform given parameters to usable formats.
        Does operations on the frames to extract vehicle counts per lane and stores the count, timestamp and lane. 
    """
    epoch_time = iso_to_unix(ISO_timestamp)
    frame_at_the_time = get_frame(epoch_time)
    prediction_frame = np.expand_dims(frame_at_the_time, axis=0) / 255.0
    boxes, scores, classes, detections = model.predict(prediction_frame)
    boxes = boxes[0] * [WIDTH, HEIGHT, WIDTH, HEIGHT]
    scores = scores[0]
    classes = classes[0].astype(int)
    detections = detections[0]
    vehicle_count = 0
    for (xmin, ymin, xmax, ymax), score, class_idx in zip(boxes, scores, classes):

        if (class_idx in ALLOWED_CLASSES) and score > 0:
            object_center = (xmin, ymin)
            # if point_inside(object_center, hull)
            #   vehicle_count += 1

    # TODO: Lane matching and updating database or cache with timestamp, lane and vehicle count


def stream_reader(cap):
    """
    Function for reading frames from the stream, runs all the time. Does no operations on the frames.
    """
    while True:
        _, frame = cap.read()
        timestamp = time.time()
        store_frame(timestamp, frame)
        if cv2.waitKey(1000) == 27:
            break


# Initializing cache-dict and timestamp-deque for frame storage
cache = dict()
timestamps = deque([])

# TODO: Implementing multiple video captures depending on the intersection
cap = cv2.VideoCapture('rtsp://rtsp.kvt.tampere.fi:55489/proxyStream')

if not cap.isOpened():
    print('Cannot open stream')
    exit(-1)

# Initializing required constants
ALLOWED_CLASSES = [1, 2, 3, 5, 7]
WIDTH = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
HEIGHT = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Initializing model parameters
model = YOLOv4(
    input_shape=(HEIGHT, WIDTH, 3),
    anchors=YOLOV4_ANCHORS,
    num_classes=80,
    training=False,
    yolo_max_boxes=50,
    yolo_iou_threshold=0.5,
    yolo_score_threshold=0.5,
)

# Loading the pretrained weights to the model
model.load_weights('yolov4.h5')

stream_reader(cap)