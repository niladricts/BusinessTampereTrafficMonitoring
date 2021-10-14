import threading

import respx
from httpx import Response

from BusinessTampereTrafficMonitoring.traffic_lights.api_client import SignalGroup
from BusinessTampereTrafficMonitoring.traffic_lights.api_client import TrafficLightAPIClient
from BusinessTampereTrafficMonitoring.traffic_lights.status import Status


TRE401_MOCK_DATA = {'responseTs': '2021-10-08T02:56:59+03:00', 'device': 'TRE401', 'timestamp': '2021-10-08T02:56:55+03:00', 'signalGroup': [{'idx': 0, 'name': 'A', 'status': 'B'}, {'idx': 1, 'name': 'B', 'status': 'B'}, {'idx': 2, 'name': 'RV1A', 'status': 'B'}, {'idx': 3, 'name': 'RV1B', 'status': 'B'}, {'idx': 4, 'name': 'RV2', 'status': 'B'}, {'idx': 5, 'name': 'C', 'status': 'B'}, {'idx': 6, 'name': 'D', 'status': 'A'}, {'idx': 7, 'name': 'E', 'status': 'B'}, {'idx': 8, 'name': 'F', 'status': 'B'}, {'idx': 9, 'name': 'G', 'status': 'B'}, {'idx': 10, 'name': 'H', 'status': '1'}, {'idx': 11, 'name': '_I', 'status': '1'}, {'idx': 12, 'name': '_J', 'status': '1'}, {'idx': 13, 'name': '_K', 'status': 'C'}, {'idx': 14, 'name': '_M', 'status': 'C'}, {'idx': 15, 'name': 'N_', 'status': '1'}, {'idx': 16, 'name': 'O', 'status': 'B'}, {'idx': 17, 'name': 'RV3', 'status': 'B'}, {'idx': 18, 'name': 'RV4', 'status': 'B'}, {'idx': 19, 'name': 'RV5', 'status': 'B'}, {'idx': 20, 'name': 'RV6', 'status': 'B'}, {'idx': 21, 'name': 'P_', 'status': 'B'}, {'idx': 22, 'name': '_R', 'status': 'B'}, {'idx': 23, 'name': '_S', 'status': 'B'}, {'idx': 24, 'name': '_T', 'status': 'B'}, {'idx': 25, 'name': '_U', 'status': 'C'}, {'idx': 26, 'name': '_V', 'status': 'C'}, {'idx': 27, 'name': '_W', 'status': 'B'}, {'idx': 28, 'name': 'X', 'status': '3'}, {'idx': 29, 'name': 'PRIO_RV1A', 'status': 'C'}, {'idx': 30, 'name': 'PRIO_RV1B', 'status': 'C'}, {'idx': 31, 'name': 'PRIO_RV2', 'status': 'C'}, {'idx': 32, 'name': 'PRIO_RV3', 'status': 'C'}, {'idx': 33, 'name': 'PRIO_RV4', 'status': 'C'}, {'idx': 34, 'name': 'PRIO_RV5', 'status': 'C'}, {'idx': 35, 'name': 'PRIO_RV6', 'status': 'C'}]}  # noqa: E501
TRE428_MOCK_DATA = {'responseTs': '2021-10-08T02:56:59+03:00', 'device': 'TRE428', 'timestamp': '2021-10-08T02:56:48+03:00', 'signalGroup': [{'idx': 0, 'name': 'A', 'status': '3'}, {'idx': 1, 'name': 'B', 'status': '3'}, {'idx': 2, 'name': 'RV1', 'status': 'B'}, {'idx': 3, 'name': 'RV2', 'status': 'B'}, {'idx': 4, 'name': '_C', 'status': 'B'}, {'idx': 5, 'name': 'D', 'status': '3'}, {'idx': 6, 'name': 'RV3', 'status': 'B'}, {'idx': 7, 'name': '_E', 'status': 'B'}, {'idx': 8, 'name': 'F', 'status': '3'}, {'idx': 9, 'name': 'RV4', 'status': 'B'}, {'idx': 10, 'name': '_G', 'status': 'B'}, {'idx': 11, 'name': 'PRIO_RV1', 'status': 'B'}, {'idx': 12, 'name': 'PRIO_RV2', 'status': 'B'}, {'idx': 13, 'name': 'PRIO_RV3', 'status': 'B'}, {'idx': 14, 'name': 'PRIO_RV4', 'status': 'C'}]}  # noqa: E501

RED_STATUS = "A"
GREEN_STATUS = "1"
OTHER_STATUS = "="
TS = [f"2020-01-01T12:00:{x:02d}+03:00" for x in range(0, 59, 3)]


def test_signal_group_cycle():
    sg = SignalGroup("TRE444", "A", TS[0], RED_STATUS)
    assert sg.status == Status.RED
    assert sg.t_red_start == TS[0]
    assert sg.t_green_start is None
    assert sg.update_state(TS[1], RED_STATUS) is None
    assert sg.t_red_start == TS[0]
    assert sg.t_green_start is None
    assert sg.update_state(TS[2], GREEN_STATUS) is None
    assert sg.status is Status.GREEN
    assert sg.t_red_start == TS[0]
    assert sg.t_green_start == TS[2]
    assert sg.update_state(TS[3], GREEN_STATUS) is None
    assert sg.t_red_start == TS[0]
    assert sg.t_green_start == TS[2]
    assert sg.update_state(TS[4], RED_STATUS) == ("TRE444", "A", TS[0], TS[2], TS[4])
    assert sg.status is Status.RED
    assert sg.t_red_start == TS[4]
    assert sg.t_green_start is None
    assert sg.update_state(TS[5], GREEN_STATUS) is None
    assert sg.status is Status.GREEN
    assert sg.t_red_start == TS[4]
    assert sg.t_green_start == TS[5]
    assert sg.update_state(TS[6], RED_STATUS) == ("TRE444", "A", TS[4], TS[5], TS[6])
    assert sg.status is Status.RED
    assert sg.t_red_start == TS[6]
    assert sg.t_green_start is None


def test_signal_group_init_green():
    sg = SignalGroup("TRE444", "A", TS[0], GREEN_STATUS)
    assert sg.status == Status.GREEN
    assert sg.t_red_start is None
    assert sg.t_green_start is None
    assert sg.update_state(TS[1], RED_STATUS) is None
    assert sg.status == Status.RED
    assert sg.t_red_start == TS[1]


def test_signal_group_init_other():
    sg = SignalGroup("TRE444", "A", TS[0], OTHER_STATUS)
    assert sg.status == Status.OTHER
    assert sg.t_red_start is None
    assert sg.t_green_start is None
    assert sg.update_state(TS[1], RED_STATUS) is None
    assert sg.status == Status.RED
    assert sg.t_red_start == TS[1]


def test_signal_group_other_mid_cycle():
    sg = SignalGroup("TRE444", "A", TS[0], RED_STATUS)
    assert sg.update_state(TS[1], RED_STATUS) is None
    assert sg.update_state(TS[2], GREEN_STATUS) is None
    assert sg.update_state(TS[3], OTHER_STATUS) is None
    assert sg.t_red_start is None
    assert sg.t_green_start is None
    assert sg.update_state(TS[4], RED_STATUS) is None


def test_init_client():
    client = TrafficLightAPIClient(
        url="http://trafficlights.tampere.fi/api/v1/deviceState/",
        monitored_devices=["TRE401", "TRE428"],
        db="sqlite:///:memory:",
    )
    assert not client.active
    assert client.monitored_devices == ["TRE401", "TRE428"]


@respx.mock
def test_client_update_device():
    client = TrafficLightAPIClient(
        url="http://api.url/",
        monitored_devices=["TEST"],
        db="sqlite:///:memory:",
    )
    resp_json = {
        'responseTs': TS[1],
        'device': 'TEST',
        'timestamp': TS[0],
        'signalGroup': [
            {'idx': 0, 'name': 'A', 'status': RED_STATUS},
            {'idx': 1, 'name': 'B', 'status': RED_STATUS}
        ]
    }
    respx.get("http://api.url/TEST").mock(Response(200, json=resp_json))
    events = client.update_device_state("TEST")
    assert events == []

    resp_json['responseTs'] = TS[3]
    resp_json['timestamp'] = TS[2]
    resp_json['signalGroup'][0]['status'] = GREEN_STATUS
    resp_json['signalGroup'][1]['status'] = GREEN_STATUS
    respx.get("http://api.url/TEST").mock(Response(200, json=resp_json))
    events = client.update_device_state("TEST")
    assert events == []

    resp_json['responseTs'] = TS[5]
    resp_json['timestamp'] = TS[4]
    resp_json['signalGroup'][0]['status'] = RED_STATUS
    resp_json['signalGroup'][1]['status'] = RED_STATUS
    respx.get("http://api.url/TEST").mock(Response(200, json=resp_json))
    events = client.update_device_state("TEST")
    assert events == [("TEST", "A", TS[0], TS[2], TS[4]), ("TEST", "B", TS[0], TS[2], TS[4])]


def test_database_store():
    client = TrafficLightAPIClient(
        url="http://api.url/",
        monitored_devices=["TEST"],
        db="sqlite:///:memory:",
    )
    events = [("TEST", "A", TS[0], TS[2], TS[4]), ("TEST", "B", TS[0], TS[2], TS[4])]
    client.store(events)
    with client.database.connect() as conn:
        stmt = client.db_table.select()
        results = conn.execute(stmt).fetchall()
        assert len(results) == 2


@respx.mock
def test_polling():
    respx.get("http://trafficlights.tampere.fi/api/v1/deviceState/TRE428").mock(
        Response(200, json=TRE428_MOCK_DATA))
    respx.get("http://trafficlights.tampere.fi/api/v1/deviceState/TRE401").mock(
        Response(200, json=TRE401_MOCK_DATA))

    client = TrafficLightAPIClient(
        url="http://trafficlights.tampere.fi/api/v1/deviceState/",
        monitored_devices=["TRE401", "TRE428"],
        db="sqlite:///:memory:",
    )
    interval = 0.1
    polling = threading.Thread(target=client.start_polling, args=(interval,), daemon=True)
    polling.start()
    assert client.active
    client.stop_polling()
    assert not client.active
