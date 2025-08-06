from enum import Enum, auto

class UIState(Enum):
    IDLE = auto()
    MONITORING = auto()
    SHUTDOWN_COUNTDOWN = auto()
