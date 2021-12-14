import json

import pytest

from BusinessTampereTrafficMonitoring.object_detector.object_detector import ObjectDetector

with open("../config.json", "r") as configfile:
    CONFIG = json.load(configfile)

LANES = CONFIG["lanes"]


def test_no_detections():
    points = []
    lanes, vehicle_count = ObjectDetector.process_detections(points, LANES)
    assert lanes == LANES and vehicle_count == 0


def test_some_detections_out_of_lanes():
    points = [
        (228, 847),
        (325, 946),
        (962, 1076),
        (2234, 1087)
    ]
    lanes, vehicle_count = ObjectDetector.process_detections(points, LANES)
    assert lanes == LANES and vehicle_count == 0


def test_some_detections_inside_lanes():
    points = [
        (1312, 243),
        (1485, 278),
        (1705, 325),
        (1830, 250)
    ]
    lanes, vehicle_count = ObjectDetector.process_detections(points, LANES)
    for lane in lanes:
        assert lane["cars"] == 1
    assert vehicle_count == 4


def test_some_detections_inside_and_outside():
    points = [
        (228, 847),
        (325, 946),
        (1705, 325),
        (1830, 250)
    ]
    lanes, vehicle_count = ObjectDetector.process_detections(points, LANES)
    assert vehicle_count == 2


@pytest.mark.parametrize("points", list("abcdefgh:"))
def test_invalid_points(points):
    with pytest.raises(TypeError):
        ObjectDetector.process_detections(points, LANES)


@pytest.mark.parametrize("lanes", list("abcdefgh:"))
def test_invalid_lanes(lanes):
    points = [
        (228, 847),
        (325, 946),
        (962, 1076),
        (2234, 1087)
    ]
    with pytest.raises(TypeError):
        ObjectDetector.process_detections(points, lanes)
