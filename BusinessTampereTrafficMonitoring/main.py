import json
import threading

from BusinessTampereTrafficMonitoring.object_detector.object_detector import ObjectDetector
from BusinessTampereTrafficMonitoring.traffic_lights.api_client import TrafficLightAPIClient


with open("config.json", "r") as configfile:
    CONFIG = json.load(configfile)

# Read monitored devices from config, get rid of duplicates
monitored_devices = set(lane["intersection_id"] for lane in CONFIG["lanes"])

traffic_light_client = TrafficLightAPIClient(
    url="http://trafficlights.tampere.fi/api/v1/deviceState/",
    monitored_devices=list(monitored_devices),
    db="sqlite:///:memory:",
)

object_detector = ObjectDetector(
    video_location=CONFIG["camera_url"],
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

# Stop the system when user presses enter
input()
print("Shutting down..")
