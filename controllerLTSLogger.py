# ANSI color codes
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'

class ControllerLTSLogger:
    def __init__(self):
        self.transitions = []
        self.current_state = 'drive'  # initial assumption

    def log(self, obs, dist, next_state):
        label = f"observe({obs},{dist:.1f})"
        self.transitions.append((self.current_state, label, next_state))
        self.current_state = next_state

    def print_lts(self):
        print("=========== Controller LTS ===========")
        for (s1, a, s2) in self.transitions:
            # Extract obs from label "observe(obs,dist)"
            try:
                obs = int(a.split('observe(')[1].split(',')[0])
            except Exception:
                obs = 0
            
            if 'stopped' in s2:
                color = RED
            elif obs == 1:
                color = YELLOW
            else:
                color = GREEN
            print(f"{color}{s1} --{a}--> {s2}{RESET}")
        print("======================================")

