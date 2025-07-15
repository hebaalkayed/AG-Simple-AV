import math

class Vehicle:
    def __init__(self, lts_builder):
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.v = 6
        self.L = 2.5
        self.dt = 0.1
        self.actual_acceleration = 0.0
        self.stopped = False
        self.lts_builder = lts_builder

    def get_state(self, quantize=2):
        """Return current state as rounded tuple."""
        return (
            round(self.x, quantize),
            round(self.y, quantize),
            round(self.theta, quantize),
            round(self.v, quantize)
        )

    def step(self, delta, acceleration, dt=None):
        """
        Update the vehicle's state using steering angle and acceleration.
        """
        # Get vehicle state before stepping
        current_state = self.get_state()
        if self.stopped:
            self.actual_acceleration = 0.0
            return

        if dt is None:
            dt = self.dt

        if self.v <= 1e-5 and acceleration < 0:
            acceleration = 0

        self.actual_acceleration = acceleration

        self.v += acceleration * dt

        if self.v <= 1e-5:
            self.v = 0.0
            self.stopped = True
            self.actual_acceleration = 0.0
            return

        self.x += self.v * math.cos(self.theta) * dt
        self.y += self.v * math.sin(self.theta) * dt
        
        
        # Get vehicle state after stepping
        next_state = self.get_state()
 
        self.lts_builder.log_step(
            s1=current_state,
            delta=delta,
            acceleration=acceleration,
            s2=next_state,
        )
		
