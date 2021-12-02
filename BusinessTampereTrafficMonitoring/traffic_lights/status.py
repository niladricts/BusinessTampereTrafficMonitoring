from enum import Enum


class Status(Enum):
    RED = 1
    GREEN = 2
    OTHER = 3

    @classmethod
    def decode(cls, status_str: str):
        """
        Decode traffic light GRINT state.

        Possible states are:
        0 - Red/Amber
        1 - Green
        2 (not used)
        3 - Green
        4 - Green
        5 - Green
        6 - Green
        7 - Green
        8 - Green
        9 - Red
        : - Green (blinking)
        ; - Amber (flashing)
        < - Amber after green
        = - Amber/dark (malfunction)
        > - Amber after green
        ? - Red
        @ - Red
        A - Red
        B - Red (no demand)
        C - Red
        D - Red
        E - Red (no demand)
        F - Red
        G - Red
        H - Red
        I - Used during start-up
        J - Used during start-up

        Detailed documentation:
        http://wiki.itsfactory.fi/images/f/fe/DINT_GRINT_states.pdf
        
        # Returns:
          Either Status.RED, Status.GREEN, or Status.OTHER
        """
        if len(status_str) != 1 or status_str < '0' or status_str > 'J':
            raise ValueError(f"Invalid traffic light status code: '{status_str}'")
        if status_str in "?@ABCDEFGH90":  # includes amber after red
            return Status.RED
        elif status_str in "1345678:<>":  # includes amber after green
            return Status.GREEN
        else:
            return Status.OTHER
