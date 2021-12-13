import time
from datetime import datetime
from typing import Callable
from typing import List

import httpx
import sqlalchemy
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.sqltypes import VARCHAR

from .signal_group import SignalGroup

Base = declarative_base()


class TrafficLightCycle(Base):
    __tablename__ = "traffic_light_cycles"
    id = Column("id", Integer, primary_key=True)
    device = Column("device", VARCHAR(20), nullable=False)
    signal_group = Column("signal_group", VARCHAR(20), nullable=False)
    t_start = Column("t_start", TIMESTAMP, nullable=False)
    t_green = Column("t_green", TIMESTAMP, nullable=False)
    t_end = Column("t_end", TIMESTAMP, nullable=False)


class TrafficLightAPIClient:
    def __init__(self, url: str, monitored_devices: List[str], db: str):
        """
        Initializes TrafficLightAPIClient.

        # Parameters:
          url: URL of the traffic light API (str), for example  "http://trafficlights.tampere.fi/api/v1/deviceState/"
          monitored_devices: list of intersections, for example ["TRE401", "TRE428"] (List[str])
          db: database connection URL in SQL Alchemy format (str)
        """
        self.url = url
        self.monitored_devices = monitored_devices
        self.active = False

        # future=True flag enables sqlalchemy 2.0 style usage
        self.database = sqlalchemy.create_engine(db, future=True)
        self.db_table = TrafficLightCycle.__table__
        Base.metadata.create_all(bind=self.database)

        # self.__signal_groups is Dict[(str, str), SignalGroup]
        self.__signal_groups = {}

    def update_device_state(self, device: str):
        """
        GETs the state of a device from the API and returns a list of completed events.

        # Parameters:
          device: device name (str)
        # Returns:
          List of traffic light cycle events that were completed as a result of
          updating the device state. (List[Tuple[str,str,str,str,str]])
        """
        resp = httpx.get(f"{self.url}{device}")
        if resp.status_code != httpx.codes.OK:
            print(f"[traffic_lights] Error fetching data: HTTP {resp.status_code}", flush=True)
            return
        obj = resp.json()
        timestamp = obj["timestamp"]
        device = obj["device"]
        events = []

        for sgroup in obj["signalGroup"]:
            sg = (device, sgroup["name"])
            status = sgroup["status"]
            if sg not in self.__signal_groups:
                self.__signal_groups[sg] = SignalGroup(*sg, timestamp, status)
            else:
                event = self.__signal_groups[sg].update_state(timestamp, status)
                if event is not None:
                    events.append(event)
        return events

    def store(self, events: List):
        """
        Stores traffic light cycle events into the database.

        # Parameters:
          events: list of events to be stored (List[Tuple[str,str,str,str,str]])
        """
        if len(events) < 1:
            return
        with self.database.connect() as db_conn:
            for device, signal_group, t_start, t_green, t_end in events:
                stmt = self.db_table.insert().values(
                    device=device,
                    signal_group=signal_group,
                    t_start=_parse_date(t_start),
                    t_green=_parse_date(t_green),
                    t_end=_parse_date(t_end))
                db_conn.execute(stmt)
            db_conn.commit()

    def start_polling(self, interval: float):
        """
        Periodically updates device states and stores events to database.

        This method never returns unless another thread calls stop_polling().
        It is intended to be called in a new thread.

        # Parameters:
          interval: The time to wait between polling the API (float)
        """
        if interval <= 0:
            raise ValueError("Polling interval has to be greater than zero")
        self.active = True
        while self.active:
            # keep track of completed cycles in all signal groups
            events = []
            for device in self.monitored_devices:
                events.extend(self.update_device_state(device))
            # store all completed cycles in database
            self.store(events)
            time.sleep(interval)

    def listen_for_light_change_events(self, interval: float, callback: Callable):
        """
        Calls the callback function every time a light changes state from green to
        red or red to green.

        This method never returns unless another thread calls stop_polling().
        It is intended to be called in a new thread.

        # Parameters:
          interval: The time to wait between polling the API (float)
          callback: callback function (Callable)
        """
        if interval <= 0:
            raise ValueError("Polling interval has to be greater than zero")
        self.active = True
        while self.active:
            for device in self.monitored_devices:
                try:
                    resp = httpx.get(f"{self.url}{device}")
                except httpx.ReadError as e:
                    print(f"[traffic_lights] Error fetching data from {self.url}{device}: {e}", flush=True)
                    return
                if resp.status_code != httpx.codes.OK:
                    print(f"[traffic_lights] Error fetching data: HTTP {resp.status_code}", flush=True)
                    return
                obj = resp.json()
                timestamp = _parse_date(obj["timestamp"]).timestamp()
                device = obj["device"]

                for sgroup in obj["signalGroup"]:
                    sg = (device, sgroup["name"])
                    status = sgroup["status"]
                    if sg not in self.__signal_groups:
                        self.__signal_groups[sg] = SignalGroup(*sg, timestamp, status)
                    else:
                        old_status = self.__signal_groups[sg].status
                        self.__signal_groups[sg].update_state(timestamp, status)
                        new_status = self.__signal_groups[sg].status
                        if old_status != new_status:
                            callback(device, sgroup["name"], timestamp, new_status)

    def stop_polling(self):
        """
        Stops polling the API after the current polling cycle is completed.
        It may take up to interval seconds for the polling thread to finish.
        """
        if self.active:
            self.active = False


def _parse_date(dstr):
    return datetime.strptime(dstr, "%Y-%m-%dT%H:%M:%S%z")
