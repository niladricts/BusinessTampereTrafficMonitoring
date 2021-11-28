import numpy as np
import time
import cv2

from tf2_yolov4.anchors import YOLOV4_ANCHORS
from tf2_yolov4.model import YOLOv4
from collections import deque

def store_frame(time, frame):
    if len(timestamps) == 200:
        cache.pop(timestamps[0])
        timestamps.popleft()
    cache[time] = frame
    timestamps.append(time)

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]

def get_frame(time = time.time()):
    return cache[find_nearest(timestamps, time)]

def detect(frame):
    frame = np.expand_dims(frame, axis=0)
    boxes, scores, classes, detections = model.predict(frame)
    boxes = boxes[0] * [WIDTH, HEIGHT, WIDTH, HEIGHT]
    print(boxes, scores, classes, detections)


def stream_reader(cap):
    while True:
        _, frame = cap.read()
        frame = cv2.resize(frame, (WIDTH, HEIGHT))
        timestamp = time.time()
        store_frame(timestamp, frame)
        detect(frame)
        if cv2.waitKey(500) == 27:
            break

cache = dict()
timestamps = deque([])

cap = cv2.VideoCapture('rtsp://rtsp.kvt.tampere.fi:55489/proxyStream')
#cap = cv2.VideoCapture('http://195.196.36.242/mjpg/video.mjpg')

if not cap.isOpened():
    print('Cannot open stream')
    exit(-1)

WIDTH = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) // 32 * 32
HEIGHT = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) // 32 * 32

model = YOLOv4(
    input_shape=(HEIGHT, WIDTH, 3),
    anchors=YOLOV4_ANCHORS,
    num_classes=80,
    training=False,
    yolo_max_boxes=50,
    yolo_iou_threshold=0.5,
    yolo_score_threshold=0.5,
)

model.load_weights('yolov4.h5')

stream_reader(cap)
