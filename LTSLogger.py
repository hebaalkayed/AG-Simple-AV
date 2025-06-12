class LTSLogger:
    def __init__(self):
        self.transitions = []
        self.current_state = 'drive'  # initial assumption

    def log(self, obs, dist, next_state):
        label = f"observe({obs},{dist:.1f})"
        self.transitions.append((self.current_state, label, next_state))
        self.current_state = next_state

    def print_lts(self):
        for (s1, a, s2) in self.transitions:
            print(f"{s1} --{a}--> {s2}")
