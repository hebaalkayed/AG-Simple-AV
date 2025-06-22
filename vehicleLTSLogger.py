from logger_utils import Terminalcolours, BaseLogger

class VehicleLTSLogger(BaseLogger):
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

    def log_vehicle_step(self, i, state, pos, vel, perception, dist, acc):
        line = (
            f"Step {i} -  State {state}, "
            f"Pos={pos}, Vel={vel:.2f}, Perception={perception}, "
            f"ObstacleDist={dist:.2f}, Acc={acc:.2f}"
        )
        coloured_line = self.colour_line(line, state)
        print(coloured_line)

    def step_and_log(self, delta, a, dt=0.1, state_label="drive"):
        s1 = self.get_state()
        self.vehicle.step(delta, a, dt)
        s2 = self.get_state()
        self.transitions.append((s1, f"(delta={round(delta, 2)}, a={round(a, 2)})", s2, state_label))
        return s2

    def print_lts(self):
        print("=========== Vehicle LTS ===========")
        for s1, action, s2, state_label in self.transitions:
            line = f"{s1} --{action}--> {s2}"
            coloured_line = self.colour_line(line, state_label)
            print(coloured_line)
        print("===================================")
