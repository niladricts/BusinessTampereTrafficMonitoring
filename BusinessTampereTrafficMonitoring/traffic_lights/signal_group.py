from .status import Status


class SignalGroup:
    def __init__(self, device: str, name: str, timestamp: str, status_code: str):
        """
        Constructor to initialize the signal group
        # Parameter:
        # argument1: device id (String)
        # argument2: device name (String)
        # argument3: timestamp(String)
        # argument4: status_code(String)

        """

        self.device = device
        self.name = name
        self.t_red_start = None
        self.t_green_start = None
        self.status = Status.decode(status_code)
        if self.status == Status.RED:
            self.t_red_start = timestamp

    def __create_event(self, timestamp):
        """

        To create the traffic light cycle event
        # Parameter:
        # argument1: timestamp (TimeStamp)
        # Returns:
        # Device id (String), device name(string), red_light start time(TIMESTAMP), green_light start_time(TIMESTAMP), timestamp

        """

        return (
            self.device,
            self.name,
            self.t_red_start,
            self.t_green_start,
            timestamp
        )

    def update_state(self, timestamp: str, status_code: str):
        """

        Updates the state of the signal group.
        Returns a tuple representing a traffic light cycle
        event (RED to GREEN to RED) if one was completed
        as a result of the update.
        Otherwise returns None.
        # Parameter:
        # argument1: timestamp(String)
        # argument2: status_code(String)
        # Returns:
        # Event (TrafficLightCycle)

        """
        status = Status.decode(status_code)
        if status == self.status:
            return None

        self.status = status

        if status == Status.OTHER:
            self.t_red_start = None
            self.t_green_start = None
        elif status == Status.GREEN:
            # Transition directly from OTHER to GREEN should not be possible
            # according to the state diagram but it might happen if there
            # were multiple state changes during the polling interval
            if self.t_red_start is not None:
                self.t_green_start = timestamp
                return None
        elif status == Status.RED:
            if self.t_green_start is not None:
                # Transition from GREEN to RED completes the cycle
                event = self.__create_event(timestamp)
                self.t_red_start = timestamp
                self.t_green_start = None
                return event
            self.t_red_start = timestamp
            self.t_green_start = None
            return None
