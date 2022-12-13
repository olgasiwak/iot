from enum import Enum


class LampState(int, Enum):
    """
    Enum zawierający reprezentację możliwych stanów lamp ON - 1, OFF - 0
    """
    on = 1
    off = 0


class Lamp:
    """
    Klasa będąca reprezentacją grupy lamp/sensorów
    """
    def __init__(self, name: str, state: LampState) -> None:
        """
        :param name: Nazwa grupy lamp
        :type name: String
        :param state: Stan lamp ON/OFF
        :type state: LampState
        """
        self.name = name
        self.state = state
