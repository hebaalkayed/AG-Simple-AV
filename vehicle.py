import math

class Vehicle:
    def __init__(self):
        # Position (x, y) in meters
        self.x = 0.0
        self.y = 0.0
        # Heading angle in radians (0 means facing east)
        self.theta = 0.0
        # Velocity in meters per second
        self.v = 6  # Small initial velocity
        # Wheelbase length in meters
        self.L = 2.5
        # Time step (fixed)
        self.dt = 0.1
        # Store the last applied acceleration after clamping
        self.actual_acceleration = 0.0
        # Stopped flag to freeze state when vehicle stops
        self.stopped = False

    def step(self, delta, a, dt=None):
        """
        Update the vehicle's state using steering angle and acceleration.

        Parameters:
            delta: steering angle in radians
            a: acceleration in m/s^2
            dt: time step in seconds (optional)
        """
        if self.stopped:
            # Freeze all updates once stopped
            self.actual_acceleration = 0.0
            return

        if dt is None:
            dt = self.dt

        # Clamp acceleration: no negative acceleration if velocity near zero
        if self.v <= 1e-5 and a < 0:
            a = 0

        self.actual_acceleration = a  # Store the clamped acceleration

        # Update velocity
        self.v += a * dt

        # If velocity drops below threshold, stop the vehicle and freeze state
        if self.v <= 1e-5:
            self.v = 0.0
            self.stopped = True
            self.actual_acceleration = 0.0
            return

        # Update position (longitudinal motion along heading)
        self.x += self.v * math.cos(self.theta) * dt
        self.y += self.v * math.sin(self.theta) * dt

        # Heading update (optional, keep for future)
        # self.theta += (self.v / self.L) * math.tan(delta) * dt