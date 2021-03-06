import logging
import queue
import sys
import time
from collections import deque
from threading import Thread

import cv2
import numpy as np


logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')

stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setLevel(logging.ERROR)
stream_handler.setFormatter(formatter)

file_handler = logging.FileHandler('stream_reader-log')
file_handler.setFormatter(formatter)

logger.addHandler(stream_handler)
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
            logger.error('Couldnt open stream')
            raise IOError('Couldnt open stream')
        self.WIDTH = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.HEIGHT = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def get_constants(self):
        return self.WIDTH, self.HEIGHT

    @staticmethod
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

    def get_frame(self, epoch_time=None):
        if epoch_time is None:
            epoch_time = time.time()
        return np.copy(self.cache[self.find_nearest(self.timestamps, epoch_time)])

    def read_stream_to_buffer(self):
        while True:
            success, frame = self.cap.read()
            if success:
                self.buffer.put(frame)

    def read_buffer_to_cache(self):
        while True:
            try:
                t = time.time()
                frame = self.buffer.get(timeout=2, block=True)
                if t - self.t_latest_frame >= 0.5:
                    self.t_latest_frame = t
                    self.store_frame(t, frame)
                self.buffer.task_done()
            except queue.Empty:
                logger.error("Unexpected error happened, reinitializing VideoCapture.")
                self.cap.release()
                self.cap = cv2.VideoCapture(self.video_location, apiPreference=cv2.CAP_FFMPEG)
                while not self.cap.isOpened():
                    logger.error("Reinitialization failed, trying again.")
                    self.cap.release()
                    self.cap = cv2.VideoCapture(self.video_location, apiPreference=cv2.CAP_FFMPEG)
                    time.sleep(0.5)
                    if time.time() - self.t_latest_frame > 5:
                        logger.error("Couldn't recover from lost stream.")
                        return -1

    def read_stream(self):
        generator = Thread(target=self.read_stream_to_buffer)
        consumer = Thread(target=self.read_buffer_to_cache)

        generator.start()
        consumer.start()

        generator.join()
        consumer.join()
