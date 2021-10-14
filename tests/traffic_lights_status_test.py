import pytest

from BusinessTampereTrafficMonitoring.traffic_lights.status import Status


def test_status_enum():
    assert Status.RED is Status.RED
    assert Status.GREEN is Status.GREEN
    assert Status.OTHER is Status.OTHER
    assert Status.RED != Status.GREEN
    assert Status.OTHER != Status.RED
    assert Status.OTHER != Status.GREEN


@pytest.mark.parametrize("status_code", list("A?@BECFGH9D"))
def test_decode_red(status_code):
    assert Status.decode(status_code) == Status.RED


@pytest.mark.parametrize("status_code", list("1345678:"))
def test_decode_green(status_code):
    assert Status.decode(status_code) == Status.GREEN


@pytest.mark.parametrize("status_code", list("IJ=;2"))
def test_decode_other(status_code):
    assert Status.decode(status_code) == Status.OTHER


@pytest.mark.parametrize("status_code", ["", "10", "not a status code", "A ", " A", "/", "K"])
def test_decode_invalid_str(status_code):
    with pytest.raises(ValueError):
        Status.decode(status_code)


@pytest.mark.parametrize("status_code", [1.0, 3, [], ["a"], (a for a in "123")])
def test_decode_invalid_type(status_code):
    with pytest.raises(Exception):
        Status.decode(status_code)
