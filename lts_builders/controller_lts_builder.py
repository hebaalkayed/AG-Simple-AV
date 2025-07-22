from lts_builders.lts_utils import BaseLTSBuilder, TerminalColours, STATE_COLOUR_MAP

class ControllerLTSBuilder(BaseLTSBuilder):
    def __init__(self):
        self.transitions = []
        self.current_state = 'drive'  # initial assumption

    def log_step(self, obs, dist, next_state, est_vel=None, est_acc=None, req_acc=None):
        # Use key=value format instead of observe(...)
        label = f"obstacle_class={obs}, obstacle_distance={dist:.2f}"
        
        if est_vel is not None and est_acc is not None and req_acc is not None:
            label += (
                f", est_vel={est_vel:.2f}, est_acc={est_acc:.2f}, req_acc={req_acc:.2f}"
            )
        
        self.transitions.append((self.current_state, label, next_state, next_state))
        self.current_state = next_state


    def print_lts(self):
        print("=========== Controller LTS ===========")
        for idx, (s1, action, s2, state_label) in enumerate(self.transitions):
            line = f"{idx + 1}. {s1} -- {action} --> {s2}"
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
