# project course 2021
# sending data from object detector to Wapice IoT ticket
# settings to be refactored as environment variables?
import time

from iotticket.client import Client
from iotticket.models import datanodesvalue
settings = {
    "password": "Perkele1",
    "username": "JARI.RAUHALA@TAMPERE-TEST",
    "baseUrl": "https://tampere-test.iot-ticket.com/api/v1/"
}


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
    username = settings["username"]
    password = settings["password"]
    baseurl = settings["baseUrl"]

    c = Client(baseurl, username, password)
    listofvalues = []

    nv = datanodesvalue()
    nv.set_name(name)  # needed for writing datanode
    nv.set_dataType("long")
    nv.set_value(value)  # needed for writing datanode
    nv.set_timestamp(timestamp)
    nv.set_unit(unit)

    listofvalues.append(nv)

    print(c.writedata(deviceId, nv))
    print("END WRITE DEVICE DATANODES FUNCTION")
    print("-------------------------------------------------------\n")


# use case:
time = time.time()
sendDataToUI("1", 44, time, deviceIds[1])
