from lts_loggers.logger_utils import BaseLogger

class ControllerLTSLogger(BaseLogger):
    def __init__(self):
        self.transitions = []
        self.current_state = 'drive'  # initial assumption

    def log(self, obs, dist, next_state):
        label = f"observe({obs},{dist:.1f})"
        # Add state label as next_state for coloring
        self.transitions.append((self.current_state, label, next_state, next_state))
        self.current_state = next_state

    def print_lts(self):
        print("=========== Controller LTS ===========")
        for s1, a, s2, state_label in self.transitions:
            line = f"{s1} --{a}--> {s2}"
            coloured_line = self.colour_line(line, state_label)
            print(coloured_line)
        print("======================================")

    def get_transitions(self):
        return self.transitions
