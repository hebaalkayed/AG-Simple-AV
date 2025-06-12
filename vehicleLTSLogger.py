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
        print("Vehicle LTS:")
        for s1, action, s2 in self.transitions:
            print(f"{s1} --{action}--> {s2}")
