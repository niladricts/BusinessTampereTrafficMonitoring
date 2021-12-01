import logging
import queue
from collections import deque
from threading import Thread
import time
import cv2
import numpy as np


logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

formatter = logging.Formatter('%(asctime)s:%(name)s:%message)s')

file_handler = logging.FileHandler('stream_reader-log')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


class StreamReader:
    def __init__(self, video_location):

        self.buffer = queue.Queue()
        self.cache = dict()

        self.timestamps = deque([])
        self.t_latest_frame = 0
        self.video_location = video_location

        self.cap = cv2.VideoCapture(self.video_location, apiPreference=cv2.CAP_FFMPEG)
        if not self.cap.isOpened():
            print('Cannot open stream')
            exit(-1)
        self.WIDTH = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.HEIGHT = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def get_constants(self):
        return self.WIDTH, self.HEIGHT

    def find_nearest(array, value):
        """
        Utility function for finding array element with closest value to value-parameter
        """
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return array[idx]

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

    def read_stream_to_buffer(self):
        while True:
            success, frame = self.cap.read()
            if success:
                self.buffer.put(frame)

    def read_buffer_to_cache(self):
        while True:
            t = time.time()
            try:
                frame = self.buffer.get()
            except queue.Empty():
                print("Unexpected error happened, reinitializing VideoCapture")
                self.cap.release()
                self.cap = cv2.VideoCapture(self.video_location, apiPreference=cv2.CAP_FFMPEG)
                while not self.cap.isOpened():
                    self.cap = cv2.VideoCapture(self.video_location, apiPreference=cv2.CAP_FFMPEG)
                    if time.time() - self.t_latest_frame > 5:
                        return -1
            if t - self.t_latest_frame >= 0.5:
                self.t_latest_frame = t
                self.store_frame(t, frame)
            self.buffer.task_done()

    def read_stream(self):
        generator = Thread(target=self.read_stream_to_buffer)
        consumer = Thread(target=self.read_buffer_to_cache)

        generator.start()
        consumer.start()

        generator.join()
        consumer.join()