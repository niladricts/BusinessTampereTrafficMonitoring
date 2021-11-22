import os

import iotticket.client
from iotticket.models import datanodesvalue

# Read username and password from environment variables
IOT_TICKET_USER = os.environ["IOT_TICKET_USERNAME"]
IOT_TICKET_PASS = os.environ["IOT_TICKET_PASSWORD"]
IOT_TICKET_URL = os.environ.get("IOT_TICKET_URL",
                                default="https://tampere-test.iot-ticket.com/api/v1/")


class Client(iotticket.client.Client):
    def __init__(self, *args, **kwargs):
        iotticket.client.Client.__init__(self, *args, **kwargs)

    def post_car_count(self, *, device_id: str, lane: str, count: int, timestamp: float):
        """
        Send a measurement result to IoT Ticket.

        Required keyword arguments:
        ===========================
        device_id:  Device ID for the camera (defined in IoT Ticket)
        lane:       Lane ID ("Data tag" name in IoT Ticket)
        count:      Number of cars on the lane at the given moment
        timestamp:  Unix timestamp in seconds (when the cars were counted)

        Usage example:
        ==============
        client.post_car_count(
            device_id="92311e32ea3f4619ac69df3c95c3ef0a",
            lane="Lane1",
            count=12,
            timestamp=time.time())
        """

        time_ms = int(1000 * timestamp)
        nv = datanodesvalue(name=lane, dataType="long", ts=time_ms, v=count, unit="cars")

        # The writedata function from iotticket.client.Client is a bit weird,
        # it can return either:
        # - string "All datanodes are not valid"
        # - object representing the response
        # or it can raise an exception on network error
        response = client.writedata(device_id, nv)

        print(response)


client = Client(IOT_TICKET_URL, IOT_TICKET_USER, IOT_TICKET_PASS)
