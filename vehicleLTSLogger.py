# ANSI color codes
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'

class VehicleLTSLogger:
    def __init__(self, vehicle, quantize=2):
        self.vehicle = vehicle
        self.transitions = []
        self.q = quantize  # Decimal places for rounding

    def get_state(self):
        return (
            round(self.vehicle.x, self.q),
            round(self.vehicle.y, self.q),
            round(self.vehicle.theta, self.q),
            round(self.vehicle.v, self.q)
        )

    def step_and_log(self, delta, a, dt=0.1):
        s1 = self.get_state()
        self.vehicle.step(delta, a, dt)
        s2 = self.get_state()
        self.transitions.append((s1, f"(delta={round(delta,2)}, a={round(a,2)})", s2))
        return s2

    def print_lts(self):
        print("=========== Vehicle LTS ===========")
        for s1, action, s2 in self.transitions:
            v = s2[-1]
            # If velocity is zero, color red and label status as stopped
            if v == 0.0:
                color = RED
                s1_disp = s1
                # Display s2 with "stopped" label replacing velocity or as you want
                s2_disp = ("stopped", s2[1], s2[2], s2[3])
            else:
                color = GREEN
                s1_disp = s1
                s2_disp = s2

            print(f"{color}{s1_disp} --{action}--> {s2_disp}{RESET}")
        print("===================================")
