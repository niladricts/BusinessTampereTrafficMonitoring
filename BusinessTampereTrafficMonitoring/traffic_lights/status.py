from enum import Enum


class Status(Enum):
    RED = 1
    GREEN = 2
    OTHER = 3

    @classmethod
    def decode(cls, s: str):
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
        """
        if len(s) != 1 or s < '0' or 'J' < s:
            raise ValueError(f"Invalid traffic light status code: '{s}'")
        elif s in "?@ABCDEFGH90":  # includes amber after red
            return Status.RED
        elif s in "1345678:<>":  # includes amber after green
            return Status.GREEN
        else:
            return Status.OTHER
