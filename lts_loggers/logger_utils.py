class Terminalcolours:
    RESET = "\033[0m"
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    ORANGE = "\033[38;5;208m"  # Approximation
    DEFAULT = ""  # Neutral (coast or unknown)

STATE_colour_MAP = {
    "drive": Terminalcolours.GREEN,
    "coast": Terminalcolours.DEFAULT,
    "brake": Terminalcolours.ORANGE,
    "emergency_brake": Terminalcolours.YELLOW,
    "stopped": Terminalcolours.RED,
}

def colour_state(state: str) -> str:
    colour = STATE_colour_MAP.get(state, Terminalcolours.DEFAULT)
    return f"{colour}{state}{Terminalcolours.RESET}"

def colour_line_by_state(line: str, state: str) -> str:
    """Wrap the whole line in the colour corresponding to the state."""
    colour = STATE_colour_MAP.get(state, Terminalcolours.DEFAULT)
    if colour:
        return f"{colour}{line}{Terminalcolours.RESET}"
    else:
        return line

class BaseLogger:
    def colour_state(self, state):
        return colour_state(state)

    def colour_line(self, line, state):
        return colour_line_by_state(line, state)

    def log_step(self, i, state, **kwargs):
        raise NotImplementedError("Each subclass must implement this.")
