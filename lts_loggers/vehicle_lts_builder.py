import re
from lts_loggers.lts_utils import BaseLTSBuilder, TerminalColours

class VehicleLTSBuilder(BaseLTSBuilder):
    def __init__(self, quantize=2):
        self.transitions = []
        self.q = quantize

    def log_step(self, s1, delta, acceleration, s2):
        """Log the LTS transition: from s1 to s2 by action (delta,a)"""
        action_label = f"(delta={round(delta,2)}, acceleration={round(acceleration,2)})"
        self.transitions.append((s1, action_label, s2))

    def print_lts(self):
        print("=========== Vehicle LTS ===========")
        for s1, action, s2 in self.transitions:
            line = f"{s1} --{action}--> {s2}"
            coloured_line = self.colour_line(line)  # no extra args needed here
            print(coloured_line)
        print("===================================")

    def get_transitions(self):
        return self.transitions

    def colour_line(self, line: str) -> str:
        match = re.search(r'acceleration=([-+]?[0-9]*\.?[0-9]+)', line)
        if match:
            a = float(match.group(1))
        else:
            return line

        if a > 0:
            colour = TerminalColours.GREEN
        elif a == 0:
            colour = TerminalColours.DEFAULT
        elif -0.5 <= a < 0:
            colour = TerminalColours.ORANGE
        else:
            colour = TerminalColours.YELLOW

        coloured_line = f"{colour}{line}{TerminalColours.RESET}"
        return coloured_line

