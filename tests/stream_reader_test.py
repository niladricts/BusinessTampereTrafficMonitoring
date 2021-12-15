from BusinessTampereTrafficMonitoring.stream_reader.stream_reader import StreamReader
import pytest
import time
import numpy as np

# Sample video from https://sample-videos.com
SOURCE = "samples_for_tests/test_video.mp4"


@pytest.mark.parametrize("source", list("01345678:"))
def test_init_class_with_invalid_source(source):
    with pytest.raises(IOError):
        StreamReader(source)


def test_init_class_with_valid_source():
    sr = StreamReader(SOURCE)
    assert sr.cap.isOpened() is True


def test_get_constants():
    sr = StreamReader(SOURCE)
    assert sr.get_constants() == (320, 240)


def test_find_nearest_valid_input():
    test_array = np.array([1, 4, 7, 8, 12, 14, 17, 19, 25, 26])
    assert StreamReader.find_nearest(test_array, 3) == 4
    assert StreamReader.find_nearest(test_array, 12.5) == 12
    assert StreamReader.find_nearest(test_array, 18) == 17
    assert StreamReader.find_nearest(test_array, 21) == 19
    assert StreamReader.find_nearest(test_array, 10.5) == 12
    assert StreamReader.find_nearest(test_array, 25.5) == 25
    assert StreamReader.find_nearest(test_array, 9999) == 26
    assert StreamReader.find_nearest(test_array, -123453) == 1


def test_find_nearest_char_input():
    with pytest.raises(TypeError):
        StreamReader.find_nearest('a', np.array([1, 2, 3]))


def test_find_nearest_empty_array():
    with pytest.raises(ValueError):
        StreamReader.find_nearest(3, np.array([]))


def test_store_frame_get_frame():
    sr = StreamReader(SOURCE)
    dummy_frame = np.ones([320, 240], int)
    sr.store_frame(time.time(), dummy_frame)
    assert len(sr.cache) == 1
    assert len(sr.timestamps) == 1
    assert (sr.get_frame() == dummy_frame).all()

