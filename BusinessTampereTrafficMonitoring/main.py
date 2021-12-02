import json
import threading
import time

from BusinessTampereTrafficMonitoring.object_detector.object_detector import ObjectDetector
from BusinessTampereTrafficMonitoring.traffic_lights.api_client import TrafficLightAPIClient


with open("config.json", "r") as configfile:
    CONFIG = json.load(configfile)


traffic_light_client = TrafficLightAPIClient(
    url="http://trafficlights.tampere.fi/api/v1/deviceState/",
    monitored_devices=["TRE401"],
    db="sqlite:///:memory:",
)

object_detector = ObjectDetector(
    # video_location="/home/mikko/koulujuduj/proj620/traffic.mp4",
    video_location="rtsp://rtsp.kvt.tampere.fi:55489/proxyStream",
    config=CONFIG
)

video_reading = threading.Thread(
    target=object_detector.stream_reader.read_stream,
    args=tuple(),
    daemon=True
)
video_reading.start()

LIGHT_CHANGE_POLL_INTERVAL = 2.0
light_watching = threading.Thread(
    target=traffic_light_client.listen_for_light_change_events,
    args=(LIGHT_CHANGE_POLL_INTERVAL, object_detector.detect_by_signal_group_and_time),
    daemon=True
)
light_watching.start()


time.sleep(60)
print("Quitting..")
