import os
import time

from iotticket.client import Client
from iotticket.models import datanodesvalue

# Read username and password from environment variables
IOT_TICKET_USER = os.environ["IOT_TICKET_USERNAME"]
IOT_TICKET_PASS = os.environ["IOT_TICKET_PASSWORD"]
IOT_TICKET_URL = os.environ.get("IOT_TICKET_URL",
                                default="https://tampere-test.iot-ticket.com/api/v1/")


# the ids are defined in the IoT Ticket
deviceIds = {
    1: "92311e32ea3f4619ac69df3c95c3ef0a",
    2: "2cb0a25295a34cd698fc009ae4e5b933",
    3: "ed345735237d423da8ca58468a88c58c"
}


# params:
#   name:      string,     "Data tag"
#   value:     int,        number of cars
#   timestamp: unix time,  time of the event,
#   deviceId:  string,     unique camera identifier, defined in iot ticket
def sendDataToUI(name, value, timestamp, deviceId, unit='c'):
    client = Client(IOT_TICKET_URL, IOT_TICKET_USER, IOT_TICKET_PASS)

    nv = datanodesvalue()
    nv.set_name(name)  # needed for writing datanode
    nv.set_dataType("long")
    nv.set_value(value)  # needed for writing datanode
    nv.set_timestamp(timestamp)
    nv.set_unit(unit)

    print(client.writedata(deviceId, nv))


# use case:
t = time.time()
sendDataToUI("1", 44, t, deviceIds[1])
