from enum import Enum


class LampState(int, Enum):
    on = 1
    off = 0


class Lamp:
    def __init__(self, name: str, state: LampState) -> None:
        self.name = name
        self.state = state
