from abc import ABC, abstractmethod

class TerminalColours:
    RESET = "\033[0m"
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    ORANGE = "\033[38;5;208m"
    DEFAULT = ""

STATE_COLOUR_MAP = {
    "drive": TerminalColours.GREEN,
    "coast": TerminalColours.DEFAULT,
    "brake": TerminalColours.ORANGE,
    "emergency_brake": TerminalColours.YELLOW,
    "stopped": TerminalColours.RED,
}

class BaseLTSBuilder(ABC):
    @abstractmethod
    def colour_line(self, line: str, **kwargs) -> str:
        pass

    @abstractmethod
    def log_step(self, i, state, **kwargs):
        pass
