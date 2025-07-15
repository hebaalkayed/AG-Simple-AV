from lts_loggers.logger_utils import BaseLogger, TerminalColours, STATE_COLOUR_MAP

class ControllerLTSLogger(BaseLogger):
    def __init__(self):
        self.transitions = []
        self.current_state = 'drive'  # initial assumption

    def log_step(self, obs, dist, next_state):
        label = f"observe({obs},{dist:.1f})"
        # Store transitions with current state and next state
        self.transitions.append((self.current_state, label, next_state, next_state))
        self.current_state = next_state

    def print_lts(self):
        print("=========== Controller LTS ===========")
        for s1, action, s2, state_label in self.transitions:
            line = f"{s1} --{action}--> {s2}"
            coloured_line = self.colour_line(line, state_label)
            print(coloured_line)
        print("======================================")

    def get_transitions(self):
        return self.transitions

    def colour_line(self, line: str, state: str) -> str:
        """Colour line based on state label."""
        colour = STATE_COLOUR_MAP.get(state, TerminalColours.DEFAULT)
        if colour:
            return f"{colour}{line}{TerminalColours.RESET}"
        else:
            return line
